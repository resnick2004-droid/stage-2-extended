"""Account-state risk policies by dynamic programming over the contract (D-290).

The question the operator put (2026-10-05) and JJ Simon describes as "state zero: the probability of winning times the
value of the next state": what dollar risk and R should a trade carry, given the account's state, rather than one fixed
pair? Here it is solved exactly on stage one's binary outcome process, by backward induction over a day-indexed state
space that carries what the firm's rules read:

* **Combine**: the balance, the trailing floor (the running end-of-day peak until the floor locks at the starting
  balance, 8284204), and the best day (the consistency target raises the profit target to best / frac, 8284208). A
  pass at a close is worth the funded account's value over the days remaining less the activation fee; the subscription
  is accrued per trading day (subscription / billing_days); a failed account is worth nothing.
* **Funded (XFA)**: the balance, the floor until a payout hardens it at zero (8284204, 8284233), the Standard path's
  winning days (five of at least the minimum), the Payout-request day (the day after a request, left out of the cycle),
  and, once paid, the balance after the last payout (a second request needs profit since it). At an eligible close the
  policy may request any grid amount from the minimum to the cap (half the balance, the Standard cap) or none -- or,
  for a fixed-leg baseline, the largest allowed, as the engine's protocol does; the trader keeps the split less the
  method's fee.

**Outcomes** are the engine's own: p(win at R) = (1 + e) / (1 + R), and a trade risking more than the room above the
floor is raced against the floor with `p_race` and `theta_from_edge` from the vendored engine (floor_mode truncate,
edge_mode drift) -- so a winning trade can still end the account mid-trade, exactly as the lockstep engine settles it.
**Actions** are a risk and R from a declared menu, or no trade; every outcome lands on the balance grid.
**Objective**: expected cash within the horizon less a slot rent per account-day (the declared price of one of the five
slots; zero is pure expected value). No credit for survival.

`CombineDP.solve` and `FundedDP.solve` return the value and the policy per day; `forward` propagates the fresh account
through the policy and reports P(pass), days, fees, payouts and the visitation of every state, from which
`export_policy` projects the decision onto the engine's policy tree (`propedge.campaign.risk_policy`, balance and
cushion bands) for the campaign check. Oracles: at zero edge with no fees and no rent, P(pass) is at most 0.327131 for
any policy and 16/49 for 1:1 at $1,500, and expected gross payouts at most $2,000 (stage one; CLAUDE.md).

**The allowance (D-306, export version 3).** A `Menu` may carry `Rungs`: the stops the regime's trades come at, with
their shares, and the contract allowance per leg. An action's dollar risk is then realised at each rung as the whole
micros that stop and the allowance permit -- `min(floor(risk / risk per micro), cap) x risk per micro`, the engine's
own arithmetic (`propedge.campaign.sizing.size_trade` at headroom 1) -- and every transition is the mixture over the
rungs, so the table's decisions are the ones the allowance can carry (the operator's requirement that intended risk
equal realised). A realised win is rounded to the balance grid and its probability read at the R the grid makes of
it, so each action stays exactly fair at zero edge -- read against the stake the grid carries: a realised risk off the
grid (whole micros at $40, $80 or $120 a micro, or a room-cut size) lands its loss rounded to the grid too, so the
probability is the grid's win over the grid's stake (`_DP._stake`; D-432's fault: read against the unrounded stake, the
T24 maps' tables passed their zero-edge Combine above stage one's supremum). On the grid nothing changes, to the bit.
With an `exit_grid` the Combine takes a **need-aware exit**: in a
state where the pass is nearer than the action's target and today's gain would not raise the consistency target out
of reach, the trade closes at what the account needs, its probability read at the smallest grid R at or above it,
exactly as the lockstep loop settles it (`CombineAccount.need_to_pass`, `TierSizedDraw`).

**The funded table's two rules (D-325, export version 8).** The operator's Studio review found funded accounts whose
risk switched between $250 and $2,000 from one day to the next and a paid account that bet its profit into the floor
(D-324). A check of the exact table found a flat optimum -- in most funded states the values of very different trades
lie within a few dollars of each other, so the argmax flips on noise -- and, below the payout line with winning days
in hand, a real preference for the big bet (bold play under a negative edge). Both rules are solved INSIDE the table,
so the backward induction, the visitation and the export agree: `tie_break_tol` -- among the actions within that many
dollars of the state's best value, the smallest dollar risk is chosen (no trade counts as the smallest), and the
state's value is that action's; `profit_risk_cap` -- once the balance is above its start (every paid state is), no
action risks more than the cap. Neither touches the Combine. Without them (every version to 7) the solver is unchanged
to the bit.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np

from propedge.contract.adapter import Rules, p_race, theta_from_edge

STEP = 50.0
SKIP = (0.0, 0.0)
#: D-329: end the account at the session's start and free its slot -- a Combine cancelled (8284121), an XFA closed at
#: the trader's request (10657969; nothing of its balance credited: the help centre states no terms). Worth exactly 0:
#: no rent that day, no trade; the slot's next attempt is the fresh state, worth 0 net of rent at the rate lambda*.
ABANDON = (-1.0, 0.0)
#: D-379: the collect action's R -- a routed signal taken at the action's risk with a take-profit at the winning-day
#: minimum (`Rules.std_winning_day_min`, read, never typed): a win adds exactly that and is a winning day; its chance is
#: read at the smallest exit-grid R its realised size needs, as the engine's stretch walk settles it
#: (`TierSizedDraw._stretch`). Funded only.
COLLECT_R = -1.0
EPS = 1e-9
ALIVE_CHECKPOINTS = (21, 63, 126, 252, 504)


def on_grid(x: float, step: float = STEP) -> bool:
    return abs(x / step - round(x / step)) < 1e-9


def _groups(keys: np.ndarray):
    """Each distinct key ascending, with the positions holding it ascending (a stable sort): `np.unique(keys)` and
    `np.flatnonzero(keys == key)` per key, in one sort."""
    order = np.argsort(keys, kind="stable")
    ks = keys[order]
    cut = np.flatnonzero(ks[1:] != ks[:-1]) + 1
    for st, en in zip(np.concatenate([[0], cut]), np.concatenate([cut, [ks.shape[0]]])):
        if en > st:
            yield ks[st], order[st:en]


def _scatter_add(new: np.ndarray, acc: np.ndarray, to: np.ndarray, w: np.ndarray) -> None:
    """`new += np.bincount(to, weights=w, minlength=len(new))` to the bit, in the time of `to` rather than of `new`:
    the per-bin partial sums are made in `acc` (zero on entry, zero again on exit) in the input's order, as bincount
    makes them, and added at the bins they land on (a bin landed on twice is written twice with the same sum); every
    other bin would have had +0.0 added, which changes no sum `new` holds (it never holds -0.0: zeros plus non-negative
    mass)."""
    np.add.at(acc, to, w)
    new[to] += acc[to]
    acc[to] = 0.0


@dataclass(frozen=True)
class Rungs:
    """D-306: the stops the regime's trades come at and the allowance that caps the contracts (see the module)."""
    risk_per_contract: tuple[float, ...]          # dollars a micro at each rung's stop (half, full, double)
    shares: tuple[float, ...]                     # each rung's share of the regime's trades; they sum to one
    combine_cap: int                              # the Combine's allowance in micros (8284197)
    funded_caps: tuple[tuple[float, int], ...]    # (balance from, micros), ascending from 0: the ladder (8284223)
    exit_grid: tuple[float, ...] = ()             # the R grid a need-aware Combine exit closes on; () = none
    # D-318: per rung, (R, share of the regime's trades at that rung whose room permits a target at R); () = every R
    # at every rung, as before
    availability: tuple[tuple[tuple[float, float], ...], ...] = ()

    def __post_init__(self) -> None:
        if not self.risk_per_contract or len(self.risk_per_contract) != len(self.shares):
            raise ValueError("rungs need one share per risk per contract")
        if any(x <= 0 for x in self.risk_per_contract) or any(s < 0 for s in self.shares):
            raise ValueError("risk per contract must be positive and shares non-negative")
        if abs(sum(self.shares) - 1.0) > 1e-9:
            raise ValueError(f"the rungs' shares must sum to one, got {sum(self.shares)}")
        if self.combine_cap <= 0 or not self.funded_caps or self.funded_caps[0][0] != 0.0:
            raise ValueError("the Combine cap must be positive and the funded ladder start at a $0 balance")
        if list(self.funded_caps) != sorted(self.funded_caps) or any(c <= 0 for _, c in self.funded_caps):
            raise ValueError("the funded ladder must ascend with positive allowances")
        if list(self.exit_grid) != sorted(self.exit_grid) or any(x <= 0 for x in self.exit_grid):
            raise ValueError("the exit grid must be positive and ascending")
        if self.availability:
            if len(self.availability) != len(self.risk_per_contract):
                raise ValueError("availability needs one table per rung")
            if any(not 0.0 <= s <= 1.0 for tab in self.availability for _, s in tab):
                raise ValueError("an availability share lies in [0, 1]")

    def __len__(self) -> int:
        return len(self.risk_per_contract)

    def avail(self, k: int, rr: float) -> float:
        """D-318: the share of rung `k`'s trades whose room permits a target at `rr` (1 without a table)."""
        if not self.availability:
            return 1.0
        for R, s in self.availability[k]:
            if abs(float(R) - float(rr)) < 1e-9:
                return float(s)
        raise ValueError(f"no availability at R = {rr:g} for rung {k}")

    def funded_cap(self, balance: np.ndarray) -> np.ndarray:
        """The funded allowance in micros at each balance (the tier read at the session's start, D-53)."""
        cap = np.full(np.shape(balance), int(self.funded_caps[0][1]), dtype=float)
        for lo, c in self.funded_caps[1:]:
            cap = np.where(np.asarray(balance, float) >= lo - EPS, float(c), cap)
        return cap

    def realised(self, risk: float, k: int, cap) -> np.ndarray | float:
        """The dollars a `risk` realises at rung `k` under `cap` micros: whole micros, rounded down, capped."""
        rpc = float(self.risk_per_contract[k])
        n = np.minimum(np.floor(float(risk) / rpc + 1e-9), cap)
        return n * rpc


@dataclass(frozen=True)
class Menu:
    """The actions: (risk, R) pairs whose outcomes land on the grid, and optionally no trade (risk 0). With `rungs`
    (D-306) an action's outcomes are realised per rung and rounded to the grid, so only the risk must lie on it.
    `min_rr`: the least R the menu offers -- 1 by default (the table's own floor since D-290); D-316 (the operator,
    2026-10-07: "you can openly test higher risk options and negative RR trades") lowers it on the Combine's menu. R at
    or below 1 is a tier-2 flag (D-151), priced by the conduct model, never a ban."""
    risks: tuple[float, ...]
    rrs: tuple[float, ...]
    skip: bool = True
    step: float = STEP
    rungs: Rungs | None = None
    min_rr: float = 1.0
    abandon: bool = False             # D-329: the ABANDON action offered in every state
    flip: tuple | None = None         # D-339: the flip stream's action (risk, R, its own net edge[, D-343: the scratch
                                      # share of a time-boxed bracket]) -- a scheduled bracket at measured statistics,
                                      # offered every day; funded menu only
    collect: tuple[float, ...] = ()   # D-379: the risks offered the collect action (COLLECT_R); funded menu only
    flips: tuple = ()                 # D-384: a menu of scheduled brackets, each (risk, R, its own net edge, its scratch
                                      # share) -- the collect brackets; after the single flip, before abandon; funded only

    def _flip_ok(self, f: tuple) -> tuple[float, float]:
        fr, fR = float(f[0]), float(f[1])
        if not (fr > 0 and fR > 0 and on_grid(fr, self.step) and on_grid(fr * fR, self.step)):
            raise ValueError("the flip action's risk and win must lie on the grid")
        if len(f) > 3 and not 0.0 <= float(f[3]) < 1.0:
            raise ValueError("the flip action's scratch share lies in [0, 1) (D-343)")
        return fr, fR

    def actions(self) -> list[tuple[float, float]]:
        acts = [SKIP] if self.skip else []
        for r in self.risks:
            for R in self.rrs:
                if (r > 0 and R > 0 and R >= self.min_rr - 1e-12 and on_grid(r, self.step)
                        and (self.rungs is not None or on_grid(r * R, self.step))):
                    acts.append((float(r), float(R)))
        if not any(a != SKIP for a in acts):
            raise ValueError("the menu has no trade whose outcomes land on the grid")
        for r in self.collect:                                    # D-379: after the strategy's trades, before the flip
            if not (float(r) > 0 and on_grid(float(r), self.step)):
                raise ValueError("a collect action's risk must be positive and on the grid (D-379)")
            acts.append((float(r), COLLECT_R))
        if self.flip is not None:                                 # D-339: after the strategy's trades, before abandon
            acts.append(self._flip_ok(self.flip))
        seen = {a for a in acts if a != SKIP}
        for f in self.flips:                                      # D-384: the menu's brackets, after the single flip
            a = self._flip_ok(f)
            if a in seen:
                raise ValueError("each bracket of the flip menu is its own (risk, R), apart from every other action (D-384)")
            seen.add(a)
            acts.append(a)
        if self.abandon:
            acts.append(ABANDON)
        return acts

    def flip_action_index(self) -> int | None:
        """The flip action's index in `actions()`, or None (D-339)."""
        if self.flip is None:
            return None
        return len(self.actions()) - (2 if self.abandon else 1) - len(self.flips)

    def flip_menu_indices(self) -> dict[int, tuple]:
        """D-384: each menu bracket's index in `actions()` and its declaration."""
        if not self.flips:
            return {}
        first = len(self.actions()) - (1 if self.abandon else 0) - len(self.flips)
        return {first + k: tuple(f) for k, f in enumerate(self.flips)}

    @classmethod
    def fixed(cls, risk: float, rr: float, step: float = STEP, rungs: Rungs | None = None) -> "Menu":
        """One declared action, no trade excluded: its own R whatever the menus' floor (D-316's fresh Combine at 0.75R
        is a declared baseline from D-318; at R >= 1 nothing changes)."""
        return cls(risks=(float(risk),), rrs=(float(rr),), skip=False, step=step, rungs=rungs, min_rr=min(1.0, float(rr)))


#: theta_from_edge's results by its exact arguments (stop, target, edge), shared by every table of the process: a pure
#: function of its floats (a fixed bisection), so a table built again -- each rent round, the oracles -- reads the same
#: bits it would compute; keyed by the function too (a test that replaces it is not answered from the memo); bounded
#: so a long screen worker cannot grow it without end
_THETA: dict[tuple, float] = {}
_THETA_MAX = 1 << 16


def _theta_from_edge(risk, W, edge) -> float:
    key = (theta_from_edge, float(risk), float(W), float(edge))
    th = _THETA.get(key)
    if th is None:
        th = theta_from_edge(risk, W, edge)
        if len(_THETA) >= _THETA_MAX:
            _THETA.clear()
        _THETA[key] = th
    return th


class Outcomes:
    """Stage one's binary process at edge `e`, with the engine's race against the floor when the risk exceeds the room."""

    def __init__(self, edge: float, rules: Rules):
        if rules.floor_mode != "truncate":
            raise ValueError("the DP models the engine's truncate floor mode (a trade liquidated at the floor)")
        self.edge, self.rules = float(edge), rules
        self._theta: dict[tuple[float, float], float | None] = {}

    def p_target(self, rr: float) -> float:
        return (1.0 + self.edge) / (1.0 + rr)

    def theta(self, risk: float, rr: float) -> float | None:
        key = (float(risk), float(rr))
        if key not in self._theta:
            self._theta[key] = (_theta_from_edge(risk, risk * rr, self.edge) if self.rules.edge_mode == "drift"
                                else None)
        return self._theta[key]

    def p_win(self, room: np.ndarray, risk: float, rr: float) -> np.ndarray:
        """P(win) with `room` dollars above the floor: the full-size trade races the nearer of its stop and the floor."""
        c = np.minimum(risk, np.maximum(np.asarray(room, float), 0.0))
        W = risk * rr
        th = self.theta(risk, rr)
        if th is None:
            return np.clip((1.0 + self.edge) * c / (c + W), 0.0, 1.0)
        return np.asarray(p_race(c, W, th), float)


@dataclass
class Solution:
    value: float                    # at the fresh state on day 0
    policy: np.ndarray              # uint8 [T, nS]: the action index per day and state
    fresh_value: np.ndarray         # [T + 1]: the fresh state's value at the start of each day (0 at T)
    payout: np.ndarray | None = None   # uint8 [T, nS]: the payout option at a close (funded only; 0 = none)


class _DP:
    """Shared: the day loop over precomputed transitions. Sentinels index past the live states: DEAD, then PASS. Each
    action's transition is per rung -- `iw`, `il` [nR, nS] (the state after a win, after a loss) and `p` [nR, nS] --
    mixed by the rungs' shares `w`; without rungs there is one rung with share one."""

    rules: Rules
    actions: list[tuple[float, float]]
    nS: int
    alive: np.ndarray
    trans: list[tuple[np.ndarray, np.ndarray, np.ndarray]]
    fresh: int
    T: int
    lam: float
    w: np.ndarray
    rungs: Rungs | None

    @property
    def DEAD(self) -> int:
        return self.nS

    @property
    def PASS(self) -> int:
        return self.nS + 1

    @property
    def ABANDONED(self) -> int:
        """D-329: the sentinel an abandoned account lands on (worth 0, like DEAD; counted apart)."""
        return self.nS + 2

    @property
    def nR(self) -> int:
        return len(self.w)

    def _set_rungs(self, menu: Menu) -> None:
        self.rungs = menu.rungs
        self.w = np.array(menu.rungs.shares, float) if menu.rungs is not None else np.array([1.0])
        self.avail: list[np.ndarray] | None = None
        self.stay: np.ndarray | None = None
        self.tie_break_tol: float | None = None                  # D-325: the funded table's two rules; None = off
        self.tie_prefer: str = "small_risk"                      # D-329: 'small_risk' (funded) or 'high_rr' (Combine)
        self.allowed: np.ndarray | None = None                   # bool [nA, nS]: the actions a state may take
        self.abandon_action: int | None = next((i for i, a in enumerate(self.actions) if a == ABANDON), None)
        # D-339: the flip action -- its outcomes from its own measured edge, never the cell's; offered every day.
        # D-343: a time-boxed flip is scratched on a share of its attempts (a day without a trade, its few dollars
        # rounding to nothing on the grid); the attempts that resolve carry the edge that keeps the attempt's expected
        # value the file's: edge / (1 - the scratch share)
        self.flip_action: int | None = menu.flip_action_index()
        self.flip_scratch: float = float(menu.flip[3]) if (menu.flip is not None and len(menu.flip) > 3) else 0.0
        self.flip_out: Outcomes | None = (Outcomes(float(menu.flip[2]) / (1.0 - self.flip_scratch), self.rules)
                                          if menu.flip is not None else None)
        # D-384: every scheduled bracket -- the single flip and the menu's -- with its own outcomes and scratch share
        self.flip_specs: dict[int, tuple[Outcomes, float]] = {}
        if self.flip_action is not None:
            self.flip_specs[self.flip_action] = (self.flip_out, self.flip_scratch)
        for i, f in menu.flip_menu_indices().items():
            sc = float(f[3]) if len(f) > 3 else 0.0
            self.flip_specs[i] = (Outcomes(float(f[2]) / (1.0 - sc), self.rules), sc)
        self.flip_actions: frozenset[int] = frozenset(self.flip_specs)

    def _abandon_stack(self):
        """D-329: the ABANDON action's transition -- every state to the ABANDONED sentinel, with certainty."""
        ab = np.full(self.nS, self.ABANDONED, np.int32)
        return self._stack([ab] * self.nR, [ab] * self.nR, [np.ones(self.nS)] * self.nR)

    def _tie_key(self) -> np.ndarray:
        """D-325 / D-329: the preference among near-tied trades, smaller first -- the smaller risk (`small_risk`: no
        trade the smallest) or the higher R (`high_rr`: a trade before sitting; among trades the one that resolves in
        fewer trades). D-341: `small_risk_flip_first` -- the smaller risk, and at equal risk the flip before the
        strategy's trade (a scheduled bracket needs no signal and leaves the queue to the growth stream; under
        `small_risk` the better value decides between them, a few dollars either way band by band). Abandon is not in
        the tie: it is taken exactly when holding the account is worth no more than starting over
        (`_day_values_ruled`), never within a tolerance -- a tolerance there drops accounts worth holding, and the more
        so the higher the rent, which breaks the rent's fixed point."""
        if self.tie_prefer not in ("small_risk", "high_rr", "small_risk_flip_first"):
            raise ValueError("tie_prefer is 'small_risk', 'high_rr' or 'small_risk_flip_first'")
        key = np.array([-R if self.tie_prefer == "high_rr" else r for r, R in self.actions], float)
        if self.tie_prefer == "small_risk_flip_first":
            # the menu's risks lie on a grid of whole dollars, so half a dollar orders the flip before the strategy's
            # trade of the same risk and changes nothing between different risks; no trade (risk 0) stays first
            key = np.array([k + (0.5 if (r > 0 and i not in self.flip_actions) else 0.0)
                            for i, (k, (r, R)) in enumerate(zip(key, self.actions))], float)
        if self.abandon_action is not None:
            key[self.abandon_action] = np.inf                     # last among ties: never chosen by the tolerance
        return key

    def _set_availability(self) -> None:
        """D-318: with the rungs' availability, each action's share per rung of days its R is offered at all (`avail`)
        and where a day without it leads (`stay`: the no-trade transition). The rest of the mass trades as before; with
        every share one nothing changes, to the bit. D-343: a time-boxed flip's scratch share is a day without a trade
        in the same form -- the flip's availability is one less the scratch share -- while an un-boxed flip is always
        offered (D-339)."""
        has_av = self.rungs is not None and bool(self.rungs.availability)
        if not has_av and all(sc <= 0.0 for _, sc in self.flip_specs.values()):
            return

        def av(i: int, r: float, R: float) -> np.ndarray:
            if i in self.flip_specs:                              # D-384: each bracket its own scratch share
                return np.full(self.nR, 1.0 - self.flip_specs[i][1])
            if r <= 0 or not has_av:                              # no trade, or abandon (D-329): always offered
                return np.ones(self.nR)
            if R == COLLECT_R:                                    # D-379: offered as often as the smallest exit target
                return np.array([self.rungs.avail(k, min(self.rungs.exit_grid)) for k in range(self.nR)])
            return np.array([self.rungs.avail(k, R) for k in range(self.nR)])

        self.avail = [av(i, r, R) for i, (r, R) in enumerate(self.actions)]
        if all((a >= 1.0).all() for a in self.avail):
            self.avail = None
            return
        self.stay = np.asarray(self._transition(0.0, 1.0)[0][0], np.int32)

    def _grid(self, x):
        """`x` rounded to the balance grid (a realised win lands on it; D-306)."""
        return np.rint(np.asarray(x, float) / self.step) * self.step

    def _stake(self, real):
        """The loss a realised risk `real` lands on the balance grid -- the stake the grid carries (D-432's fault). A
        stake off the grid (whole micros at $40, $80 or $120 a micro against the $50 grid, or a room-cut size) is rounded
        by the state index exactly as the win is, so the win's probability is read against it: p = L / (L + W) at zero
        edge. Read against the unrounded stake instead, a bet the engine settles fair is favourable on the grid -- one
        micro at $120 a micro, 1:1, was +$100 against -$100 at 120 / 220, +$9.09 a trade -- and the table's zero-edge
        pass probability rose above stage one's supremum (the T24 maps' refusals, D-431, D-432, D-433). On the grid the
        stake is the realised risk itself, to the bit, so no table whose sizes lie on the grid moves (FV3-C's)."""
        return self._grid(real)

    def _stack(self, iw: list[np.ndarray], il: list[np.ndarray], p: list[np.ndarray]):
        return (np.stack(iw).astype(np.int32), np.stack(il).astype(np.int32), np.stack(p).astype(np.float64))

    def _action_value(self, a: int, ext: np.ndarray, ext_stay: np.ndarray | None, daily: float) -> np.ndarray:
        """Action `a`'s value in every state, given the values `ext` the day closes on."""
        if a == self.abandon_action:                              # D-329: the slot freed at the session's start
            return np.zeros(self.nS)
        iw, il, p = self.trans[a]
        A = None if self.avail is None else self.avail[a]
        val = np.full(self.nS, -daily)
        for k in range(self.nR):
            x = p[k] * np.take(ext, iw[k]) + (1.0 - p[k]) * np.take(ext, il[k])
            if A is not None and A[k] < 1.0:                     # D-318: the R not offered today -- no trade
                x = A[k] * x + (1.0 - A[k]) * ext_stay
            val += self.w[k] * x
        return val

    # ------------------------------------------------------------------------------ the day step, done once a solve
    # The day loop below reads the same numbers in the same order as `_action_value` and `_day_values_ruled`, every
    # IEEE operation of theirs repeated exactly -- so every value, policy and table is the same to the bit -- while
    # what does not change from day to day is built once a solve (`_plan`): each action's allowed states (an action a
    # state may not take is -inf there whatever its value, so it is evaluated only where allowed), the index arrays of
    # its transitions as intp (np.take converted the int32 ones on every call), each distinct index array gathered once
    # a day however many actions share it (an action's loss transition is shared by its every R), the win
    # probability's complement, and work buffers reused instead of allocated. FV3-S's certainty equivalent overrides
    # `_action_value` and keeps the original loop, as does any class (or test) that replaces it or `_day_values_ruled`.

    def _fast(self) -> bool:
        cls = type(self)
        return cls._action_value is _ORIGINAL_STEP[0] and cls._day_values_ruled is _ORIGINAL_STEP[1]

    def _plan(self) -> dict:
        key = (self.trans, self.avail, self.stay, self.allowed, self.w, self.alive)
        cached = getattr(self, "_plan_cache", None)
        if cached is not None and all(x is y for x, y in zip(cached[0], key)):
            return cached[1]
        nS, nR, n_ext = self.nS, self.nR, self.nS + 3
        gathers: list[np.ndarray] = []
        seen: dict[tuple, list[int]] = {}

        def gid(arr) -> int:
            a = np.ascontiguousarray(arr, dtype=np.intp)
            if a.size and (int(a.min()) < 0 or int(a.max()) >= n_ext):
                raise IndexError("a transition leads outside the table's states")   # np.take's own refusal, earlier
            k = (a.size, hashlib.blake2b(a.view(np.uint8), digest_size=16).digest())
            for j in seen.get(k, ()):
                if np.array_equal(gathers[j], a):
                    return j
            seen.setdefault(k, []).append(len(gathers))
            gathers.append(a)
            return len(gathers) - 1

        acts = []
        for a in range(len(self.actions)):
            sub = None
            if self.allowed is not None and not bool(np.all(self.allowed[a])):
                sub = np.flatnonzero(self.allowed[a])
            if a == self.abandon_action:                          # D-329: worth exactly 0
                acts.append((sub, None))
                continue
            iw, il, p = self.trans[a]
            A = None if self.avail is None else self.avail[a]
            rungs = []
            for k in range(nR):
                pick = (lambda x: x) if sub is None else (lambda x: x[sub])
                pk = pick(p[k])
                mix = None
                if A is not None and A[k] < 1.0:                  # D-318: the R not offered today -- no trade
                    mix = (A[k], 1.0 - A[k], gid(pick(self.stay)))
                rungs.append((gid(pick(iw[k])), gid(pick(il[k])), pk, 1.0 - pk, mix, self.w[k]))
            acts.append((sub, rungs))
        last: dict[int, int] = {}
        for a, (_, rungs) in enumerate(acts):
            for k, (jw, jl, _, _, mix, _) in enumerate(rungs or ()):
                for j in (jw, jl) + ((mix[2],) if mix is not None else ()):
                    last[j] = a * nR + k
        release: dict[int, list[int]] = {}
        for j, s in last.items():
            release.setdefault(s, []).append(j)
        plan = {"acts": acts, "gathers": gathers, "release": release, "pool": {}, "vals": None,
                "dead": ~self.alive}
        self._plan_cache = (key, plan)
        return plan

    def _drop_plan(self) -> None:
        self._plan_cache = None

    def _day_values_fast(self, ext: np.ndarray, daily: float) -> tuple[np.ndarray, np.ndarray]:
        """`_day_values` / `_day_values_ruled` to the bit, from the plan (see above)."""
        plan = self._plan()
        nS, nR = self.nS, self.nR
        pool, gathers, release = plan["pool"], plan["gathers"], plan["release"]
        cache: dict[int, np.ndarray] = {}

        def get(size: int) -> np.ndarray:
            free = pool.get(size)
            return free.pop() if free else np.empty(size)

        def put(arr: np.ndarray) -> None:
            pool.setdefault(arr.shape[0], []).append(arr)

        def gather(j: int) -> np.ndarray:
            arr = cache.get(j)
            if arr is None:
                idx = gathers[j]
                arr = get(idx.shape[0])
                np.take(ext, idx, out=arr, mode="clip")           # indices checked in range when the plan was built
                cache[j] = arr
            return arr

        tie = self.tie_break_tol is not None
        if tie:
            if plan["vals"] is None:
                plan["vals"] = np.empty((len(self.actions), nS))
            vals = plan["vals"]
        else:                     # the first action of the best value, as argmax and the unruled loop both take it
            best = np.full(nS, -np.inf)
            arg = np.zeros(nS, np.intp)
        for a, (sub, rungs) in enumerate(plan["acts"]):
            size = nS if sub is None else sub.shape[0]
            val = vals[a] if (tie and sub is None) else get(size)
            if rungs is None:                                     # D-329: abandon, worth 0
                val.fill(0.0)
            else:
                val.fill(-daily)
                x, y = get(size), get(size)
                for k, (jw, jl, pk, qk, mix, wk) in enumerate(rungs):
                    np.multiply(pk, gather(jw), out=x)            # p * V(win) + (1 - p) * V(loss)
                    np.multiply(qk, gather(jl), out=y)
                    np.add(x, y, out=x)
                    if mix is not None:                           # A * x + (1 - A) * V(no trade)
                        np.multiply(mix[0], x, out=x)
                        np.multiply(mix[1], gather(mix[2]), out=y)
                        np.add(x, y, out=x)
                    np.multiply(wk, x, out=x)                     # val += w * x
                    np.add(val, x, out=val)
                    for j in release.get(a * nR + k, ()):
                        put(cache.pop(j))
                put(x)
                put(y)
            if tie:
                if sub is not None:                               # D-325: not allowed -- -inf
                    row = vals[a]
                    row.fill(-np.inf)
                    row[sub] = val
                    put(val)
            else:
                if sub is None:
                    better = val > best
                    np.copyto(best, val, where=better)
                    arg[better] = a
                else:
                    better = val > best[sub]
                    s = sub[better]
                    best[s] = val[better]
                    arg[s] = a
                put(val)
        if not tie:
            best[plan["dead"]] = 0.0
            return best, arg.astype(np.uint8)
        best = vals.max(axis=0)
        pref = self._tie_key()
        thr = best - float(self.tie_break_tol) - EPS
        tied = vals >= thr[None, :]
        least = np.full(nS, np.inf)
        for a in range(len(self.actions)):                        # the least preference among the tied
            np.copyto(least, pref[a], where=tied[a] & (pref[a] < least))
        top = np.full(nS, -np.inf)
        arg = np.zeros(nS, np.intp)
        for a in range(len(self.actions)):                        # the best value among them, the first on a tie
            upd = tied[a] & (least == pref[a]) & (vals[a] > top)
            np.copyto(top, vals[a], where=upd)
            arg[upd] = a
        if self.abandon_action is not None:                       # D-329: abandon exactly where nothing beats it
            arg = np.where(vals[self.abandon_action] >= best - EPS, self.abandon_action, arg)
        chosen = np.take_along_axis(vals, arg[None, :], axis=0)[0]
        chosen[plan["dead"]] = 0.0
        return chosen, arg.astype(np.uint8)

    def _day_values(self, ext: np.ndarray, daily: float) -> tuple[np.ndarray, np.ndarray]:
        if self._fast():
            return self._day_values_fast(ext, daily)
        ext_stay = None if self.stay is None else np.take(ext, self.stay)
        if self.tie_break_tol is None and self.allowed is None:
            best = np.full(self.nS, -np.inf)
            arg = np.zeros(self.nS, np.uint8)
            for a in range(len(self.actions)):
                val = self._action_value(a, ext, ext_stay, daily)
                better = val > best
                best[better] = val[better]
                arg[better] = a
            best[~self.alive] = 0.0
            return best, arg
        return self._day_values_ruled(ext, ext_stay, daily)

    def _day_values_ruled(self, ext: np.ndarray, ext_stay: np.ndarray | None, daily: float) -> tuple[np.ndarray, np.ndarray]:
        """D-325: the day's choice under the two rules -- the actions a state may not take are out (`allowed`), and
        among those within `tie_break_tol` of the best value the smallest dollar risk is taken (no trade the smallest;
        among equal risks the better value). The state's value is the chosen action's, so the table is the value of
        the policy it exports."""
        vals = np.stack([self._action_value(a, ext, ext_stay, daily) for a in range(len(self.actions))])
        if self.allowed is not None:
            vals = np.where(self.allowed, vals, -np.inf)
        best = vals.max(axis=0)
        if self.tie_break_tol is None:
            arg = vals.argmax(axis=0)
        else:
            pref = self._tie_key()[:, None]
            tied = vals >= best[None, :] - float(self.tie_break_tol) - EPS
            least = np.where(tied, pref, np.inf).min(axis=0)
            arg = np.where(tied & (pref == least[None, :]), vals, -np.inf).argmax(axis=0)
            if self.abandon_action is not None:                  # D-329: abandon exactly where nothing beats it
                arg = np.where(vals[self.abandon_action] >= best - EPS, self.abandon_action, arg)
        chosen = np.take_along_axis(vals, arg[None, :], axis=0)[0]
        chosen[~self.alive] = 0.0
        return chosen, arg.astype(np.uint8)

    def _push(self, dist: np.ndarray, pol: np.ndarray, vis: np.ndarray) -> np.ndarray:
        """One day's trades: the mass at each state moved by its action's outcomes; returns [nS + 3] (DEAD, PASS and
        ABANDONED past the live states)."""
        # Only the states holding mass are read, action by action in ascending order and each action's states in
        # ascending order, as before: a state without mass adds +0.0 to every bin and to its visitation, which
        # changes no sum (the mass is never negative), so this is the all-states computation to the bit; each
        # bincount's partial sums are added where they land (`_scatter_add`).
        n = self.nS + 3
        new = np.zeros(n)
        acc = self._scatter_acc(n)
        held = np.flatnonzero(dist > 0)
        for a, pos in _groups(pol[held]):
            iw, il, p = self.trans[a]
            A = None if self.avail is None else self.avail[a]
            s = held[pos]
            m = dist[s]
            vis[s, a] += m
            for k in range(self.nR):
                mk = m * self.w[k]
                if A is not None and A[k] < 1.0:                 # D-318: the R not offered today -- no trade
                    _scatter_add(new, acc, self.stay[s], mk * (1.0 - A[k]))
                    mk = mk * A[k]
                pk = p[k][s]
                _scatter_add(new, acc, iw[k][s], mk * pk)
                _scatter_add(new, acc, il[k][s], mk * (1.0 - pk))
        return new

    def _scatter_acc(self, n: int) -> np.ndarray:
        """A zeroed accumulator of `n` bins for `_scatter_add`, kept between calls (it is zero again after each)."""
        acc = getattr(self, "_acc", None)
        if acc is None or acc.shape[0] < n:
            acc = self._acc = np.zeros(n)
        return acc[:n]


#: the day step the fast path reproduces (`_DP._fast`): a class whose step is another's keeps its own
_ORIGINAL_STEP = (_DP._action_value, _DP._day_values_ruled)


# --------------------------------------------------------------------------------------------------- the Combine

class CombineDP(_DP):
    """The Combine's table. D-313 (the operator, 2026-10-07) adds two rules as options: `room_cap` -- a trade never
    risks more than the room above the floor, cut to the whole micros the room carries at the rung's stop; and
    `consistency_cap` -- when the pass cannot be taken today, a winning trade closes at the day's consistency allowance
    (the allowed fraction of the effective target), so no day lifts the target: the table then needs no lifted-target
    states. Both need the rungs' exit grid (the cap's exit reads its probability at the smallest grid R at or above it,
    as the need-aware exit does); the room cap is modelled only with the consistency cap (without it a room-cut win
    could lift the target to a class the table does not carry)."""

    def __init__(self, rules: Rules, menu: Menu, edge: float, horizon: int, lam: float = 0.0, *,
                 room_cap: bool = False, consistency_cap: bool = False,
                 tie_break_tol: float | None = None, tie_prefer: str = "high_rr"):
        if rules.combine_mll_lock_at is None:
            raise ValueError("the DP needs the Combine floor's lock (combine_mll_lock_at)")
        self.room_cap, self.consistency_cap = bool(room_cap), bool(consistency_cap)
        if (self.room_cap or self.consistency_cap) and (menu.rungs is None or not menu.rungs.exit_grid):
            raise ValueError("the room and consistency caps need the rungs' exit grid (D-313)")
        if self.room_cap and not self.consistency_cap:
            raise ValueError("the room cap is modelled with the consistency cap only (D-313)")
        if menu.flip is not None or menu.flips:
            raise ValueError("the Combine's menu has no flip action: no winning-day rule applies to it (D-338)")
        if menu.collect:
            raise ValueError("the Combine's menu has no collect action: no winning-day rule applies to it (D-379)")
        self.rules, self.menu, self.T, self.lam = rules, menu, int(horizon), float(lam)
        self.step = menu.step
        self.out = Outcomes(edge, rules)
        self.actions = menu.actions()
        self._set_rungs(menu)
        if tie_break_tol is not None:                             # D-329: the Combine's tie-break
            if float(tie_break_tol) < 0.0:
                raise ValueError("the tie-break tolerance is a non-negative number of dollars (D-329)")
            self.tie_break_tol = float(tie_break_tol)
        if str(tie_prefer) == "small_risk_flip_first":
            raise ValueError("the Combine's menu has no flip action, so no preference for it (D-341)")
        self.tie_prefer = str(tie_prefer)
        self._tie_key()                                           # validates the preference
        mll, tgt, frac, lock = rules.mll, rules.profit_target, rules.consistency_max_day_frac, rules.combine_mll_lock_at
        self.frac = float(frac)
        wins = set()
        for r, R in self.actions:
            if r > 0:
                for k in range(self.nR):
                    real = self._combine_realised(r, k)
                    if real > 0:
                        wins.add(float(self._grid(real * R)))
        wins = sorted(wins)
        # D-313: under the consistency cap no day lifts the target, so the only class is the profit target's
        self.best_vals = [0.0] + ([] if self.consistency_cap else [w for w in wins if w > frac * tgt + EPS])
        self.target_eff = np.array([tgt] + [w / frac for w in self.best_vals[1:]])
        self.b_min = -mll
        # a live state's balance is below its class's target (a balance at or above it passed at the lock), so the
        # grid ends at the highest target; before D-306 it ran a largest win further, over states no path reaches
        self.b_max = float(self.target_eff.max())
        self.nB = int(np.ceil((self.b_max - self.b_min) / self.step - EPS)) + 1
        self.p_max = lock + mll                                  # a peak beyond it changes nothing
        self.nM = int(round(self.p_max / self.step)) + 1
        self.nK = len(self.best_vals)
        self.nS = self.nB * self.nM * self.nK
        b, m, k = np.unravel_index(np.arange(self.nS), (self.nB, self.nM, self.nK))
        self.B = self.b_min + self.step * b
        self.P = self.step * m
        self.F = np.maximum(-mll, np.minimum(lock, self.P - mll))
        self.K = k
        self.alive = self.B > self.F + EPS
        self.cushion = self.B - self.F
        self.fresh = int(self.index(0.0, 0.0, 0))
        self.trans = [self._transition(r, R) for r, R in self.actions]
        self._set_availability()                                  # D-318

    def class_of(self, W: float) -> int:
        """The best-day class a win of `W` belongs to (0 when it cannot raise the target)."""
        for j, v in enumerate(self.best_vals):
            if j and abs(v - W) < 1e-6:
                return j
        return 0

    def index(self, B, P, K) -> np.ndarray:
        b = np.clip(np.rint((np.asarray(B, float) - self.b_min) / self.step), 0, self.nB - 1).astype(np.int64)
        m = np.rint(np.minimum(np.asarray(P, float), self.p_max) / self.step).astype(np.int64)
        return (b * self.nM + m) * self.nK + np.asarray(K, np.int64)

    def _combine_realised(self, r: float, k: int) -> float:
        """The dollars action risk `r` realises at rung `k` in the Combine (its allowance is fixed)."""
        if self.rungs is None:
            return float(r)
        return float(self.rungs.realised(r, k, self.rungs.combine_cap))

    def _p_groups(self, mask: np.ndarray, real: np.ndarray, rr: np.ndarray) -> np.ndarray:
        """P(win) per state, 1 outside `mask`, with per-state risk and R: grouped by their distinct values (the engine's
        race needs a scalar risk and R)."""
        p = np.ones(self.nS)
        idx = np.nonzero(mask)[0]
        if not len(idx):
            return p
        keys = np.round(np.stack([real[idx], rr[idx]], axis=1), 9)
        uniq, inv = np.unique(keys, axis=0, return_inverse=True)
        inv = np.asarray(inv).ravel()
        for j, (rv, rrv) in enumerate(uniq):
            sel = idx[inv == j]
            p[sel] = self.out.p_win(self.cushion[sel], float(rv), float(rrv))
        return p

    def _transition_d313(self, r: float, R: float):
        """D-313's transitions: the room cap (per-state risk) and the consistency cap beside the need-aware exit."""
        if r < 0:                                                      # D-329: abandon
            return self._abandon_stack()
        same = np.where(self.alive, np.arange(self.nS), self.DEAD).astype(np.int32)
        if r == 0:
            return self._stack([same] * self.nR, [same] * self.nR, [np.ones(self.nS)] * self.nR)
        grid = np.asarray(self.rungs.exit_grid, float)
        allow = self.frac * self.target_eff[self.K]                    # the day's consistency allowance (one trade a day)
        need = self.target_eff[self.K] - self.B
        pass_ok = (need > EPS) & ((need <= self.frac * self.B / (1.0 - self.frac) + EPS) if self.frac < 1.0
                                  else np.ones(self.nS, bool))
        iws, ils, ps = [], [], []
        for k in range(self.nR):
            real = np.full(self.nS, self._combine_realised(r, k))
            if self.room_cap:                                          # the whole micros the room carries at this stop
                rpc = float(self.rungs.risk_per_contract[k])
                real = np.minimum(real, np.floor(np.maximum(self.cushion, 0.0) / rpc + 1e-9) * rpc)
            W = np.asarray(self._grid(real * R), float)
            L = np.asarray(self._stake(real), float)                  # the loss the grid lands (D-432's fault)
            # D-316: below 1R a room-cut risk's win can round to nothing on the grid -- no trade (it cannot move a state);
            # likewise a stake the grid rounds to nothing
            traded = self.alive & (real > 0) & (W > 0) & (L > 0)
            safe = np.where(real > 0, real, 1.0)
            Wf = np.where(traded, W, 0.0)
            # the need-aware exit: the pass when the trade's target is past it and the pass keeps the consistency rule
            gi = np.searchsorted(grid, need / safe - 1e-9)
            gi_c = np.minimum(gi, len(grid) - 1)
            at_need = traded & pass_ok & (need < Wf - EPS) & (gi < len(grid)) & (grid[gi_c] <= R + 1e-9)
            # the consistency cap: otherwise a win past the day's allowance closes at the allowance
            gc = np.searchsorted(grid, allow / safe - 1e-9)
            gc_c = np.minimum(gc, len(grid) - 1)
            at_cap = (traded & ~at_need & (Wf > allow + EPS) & (gc < len(grid)) & (grid[gc_c] <= R + 1e-9)
                      if self.consistency_cap else np.zeros(self.nS, bool))
            rr = np.where(at_need, grid[gi_c], np.where(at_cap, grid[gc_c], W / safe))
            Wwin = np.where(at_cap, allow, W)
            # the probability against the stake the grid carries: the target's dollars (the grid's win, or the exit's
            # target at the realised size) over the grid's loss; where the stake is on the grid, the R as before
            on = L == real
            if not on[traded].all():
                tgt = np.where(at_need, safe * grid[gi_c], np.where(at_cap, safe * grid[gc_c], W))
                rr = np.where(on, rr, tgt / np.where(L > 0, L, 1.0))
            p = self._p_groups(traded, L, rr)
            Bw = self.B + Wwin
            Pw = np.maximum(self.P, Bw)
            kw = self.K if self.consistency_cap else np.maximum(self.K, np.array([self.class_of(w) for w in Wwin]))
            passed = at_need | (Bw >= self.target_eff[kw] - EPS)
            iw = np.where(~traded, same, np.where(passed, self.PASS, self.index(Bw, Pw, kw))).astype(np.int32)
            c = np.minimum(L, self.cushion)                           # the stake the grid carries (D-432's fault)
            Bl = self.B - c
            dead = Bl <= self.F + EPS
            il = np.where(~traded, same, np.where(dead, self.DEAD, self.index(np.where(dead, self.B, Bl), self.P, self.K))
                          ).astype(np.int32)
            iws.append(iw), ils.append(il), ps.append(np.where(traded, p, 1.0))
        return self._stack(iws, ils, ps)

    def _transition(self, r: float, R: float):
        if self.room_cap or self.consistency_cap:
            return self._transition_d313(r, R)
        if r < 0:                                                      # D-329: abandon
            return self._abandon_stack()
        same = np.where(self.alive, np.arange(self.nS), self.DEAD).astype(np.int32)
        if r == 0:
            return self._stack([same] * self.nR, [same] * self.nR, [np.ones(self.nS)] * self.nR)
        iws, ils, ps = [], [], []
        for k in range(self.nR):
            real = self._combine_realised(r, k)
            W = float(self._grid(real * R)) if real > 0 else 0.0
            L = float(self._stake(real)) if real > 0 else 0.0        # the loss the grid lands (D-432's fault)
            if W <= 0 or L <= 0:             # no contract at this stop, or (D-316, below 1R) a win the grid rounds away,
                iws.append(same), ils.append(same), ps.append(np.ones(self.nS))   # or a stake it rounds away
                continue
            p = self.out.p_win(self.cushion, L, W / L)               # fair on the grid: its win against its stake
            Bw = self.B + W
            Pw = np.maximum(self.P, Bw)
            kw = np.maximum(self.K, self.class_of(W))
            passed = Bw >= self.target_eff[kw] - EPS
            iw = np.where(~self.alive, self.DEAD, np.where(passed, self.PASS, self.index(Bw, Pw, kw))).astype(np.int32)
            if self.rungs is not None and self.rungs.exit_grid:     # D-306: the need-aware exit
                need = self.target_eff[self.K] - self.B
                room_ok = (need <= self.frac * self.B / (1.0 - self.frac) + EPS) if self.frac < 1.0 else np.ones(self.nS, bool)
                feasible = self.alive & (need > EPS) & (need < W - EPS) & room_ok
                if feasible.any():
                    grid = np.asarray(self.rungs.exit_grid, float)
                    gi = np.searchsorted(grid, need / real - 1e-9)   # the smallest grid R at or above the need
                    ok = feasible & (gi < len(grid))
                    gi_c = np.minimum(gi, len(grid) - 1)
                    ok &= grid[gi_c] <= R + 1e-9
                    p = p.copy()
                    for g in np.unique(gi_c[ok]):
                        m = ok & (gi_c == g)
                        # the exit's target at the realised size against the grid's stake (its R where on the grid)
                        p[m] = self.out.p_win(self.cushion[m], L,
                                              float(grid[g]) if L == real else real * float(grid[g]) / L)
                        iw[m] = self.PASS
            c = np.minimum(L, self.cushion)
            Bl = self.B - c
            dead = Bl <= self.F + EPS
            il = np.where(dead | ~self.alive, self.DEAD, self.index(np.where(dead, self.B, Bl), self.P, self.K)).astype(np.int32)
            iws.append(iw), ils.append(il), ps.append(p)
        return self._stack(iws, ils, ps)

    def solve(self, pass_value: Sequence[float]) -> Solution:
        """`pass_value[t]`: what a pass at the close of day t is worth (the funded value over the days left, less the
        activation)."""
        pv = np.asarray(pass_value, float)
        if len(pv) != self.T:
            raise ValueError("pass_value needs one entry per day of the horizon")
        daily = self.rules.subscription / self.rules.billing_days + self.lam
        V = np.zeros(self.nS)
        policy = np.zeros((self.T, self.nS), np.uint8)
        fresh = np.zeros(self.T + 1)
        self._drop_plan()                                         # built afresh for this solve, freed after it
        try:
            for t in range(self.T - 1, -1, -1):
                ext = np.concatenate([V, [0.0, pv[t], 0.0]])      # DEAD, PASS, ABANDONED (D-329)
                V, policy[t] = self._day_values(ext, daily)
                fresh[t] = V[self.fresh]
        finally:
            self._drop_plan()
        return Solution(value=float(fresh[0]), policy=policy, fresh_value=fresh)

    def forward(self, sol: Solution, t0: int = 0) -> dict[str, Any]:
        """The fresh account propagated through `sol.policy` from day `t0`."""
        dist = np.zeros(self.nS)
        dist[self.fresh] = 1.0
        days = 0.0
        pass_by_day = np.zeros(self.T)
        fail_by_day = np.zeros(self.T)
        abandon_by_day = np.zeros(self.T)
        vis = np.zeros((self.nS, len(self.actions)))
        for t in range(t0, self.T):
            alive = dist.sum()
            if alive < 1e-15:
                break
            new = self._push(dist, sol.policy[t], vis)
            days += alive - new[self.ABANDONED]                  # an abandoned account holds no slot that day
            dist = new[:self.nS]
            fail_by_day[t] = new[self.DEAD]
            pass_by_day[t] = new[self.PASS]
            abandon_by_day[t] = new[self.ABANDONED]
        passed, failed, abandoned = float(pass_by_day.sum()), float(fail_by_day.sum()), float(abandon_by_day.sum())
        sub, bd = self.rules.subscription, self.rules.billing_days
        d = np.arange(self.T) + 1 - t0
        cycles = np.ceil(d / bd)                                  # the engine bills at purchase and every cycle
        subs_engine = float(sub * ((pass_by_day + fail_by_day + abandon_by_day) * cycles).sum()
                            + dist.sum() * sub * np.ceil((self.T - t0) / bd))
        return {"p_pass": passed, "p_fail": failed, "p_abandon": abandoned, "p_unresolved": float(dist.sum()),
                "mean_days": float(days), "mean_subscriptions_accrued": float(days * sub / bd),
                "mean_subscriptions_engine": subs_engine, "pass_by_day": pass_by_day, "fail_by_day": fail_by_day,
                "abandon_by_day": abandon_by_day,
                "mean_days_to_pass": float((pass_by_day * d).sum() / passed) if passed > 0 else float("nan"),
                "visitation": vis}


# ------------------------------------------------------------------------------------------------------ the XFA

class FundedDP(_DP):
    """The XFA's table. D-325 adds the two rules of the module docstring: `tie_break_tol` (dollars of value within
    which the smallest risk is taken) and `profit_risk_cap` (the most any action risks once the balance is above its
    start); both None by default, under which the solve is unchanged to the bit."""

    def __init__(self, rules: Rules, menu: Menu, edge: float, horizon: int, lam: float = 0.0, *,
                 balance_cap: float = 6000.0, payout_grid_step: float | None = None, payout_choice: str = "optimal",
                 tie_break_tol: float | None = None, profit_risk_cap: float | None = None,
                 tie_prefer: str = "small_risk"):
        if payout_choice not in ("optimal", "max"):
            raise ValueError("payout_choice is 'optimal' (the DP decides) or 'max' (the engine's fixed protocol)")
        self.rules, self.menu, self.T, self.lam = rules, menu, int(horizon), float(lam)
        self.step = menu.step
        self.payout_choice = payout_choice
        self.out = Outcomes(edge, rules)
        self.actions = menu.actions()
        self._set_rungs(menu)
        if tie_break_tol is not None:
            if float(tie_break_tol) < 0.0:
                raise ValueError("the tie-break tolerance is a non-negative number of dollars (D-325)")
            self.tie_break_tol = float(tie_break_tol)
        self.tie_prefer = str(tie_prefer)
        self._tie_key()                                           # validates the preference (D-329)
        self.profit_risk_cap = None if profit_risk_cap is None else float(profit_risk_cap)
        if self.profit_risk_cap is not None:
            least = min(r for r, _ in self.actions if r > 0)
            if self.profit_risk_cap < least - EPS:
                raise ValueError(f"the profit risk cap ({self.profit_risk_cap:g}) is below the menu's smallest risk "
                                 f"({least:g}): an account in profit could take no trade at all (D-325)")
        mll, lock = rules.mll, rules.xfa_lock_at
        if rules.xfa_mll_start != -mll or lock != 0.0:
            raise ValueError("the DP models the XFA floor starting at -MLL and locking at zero (8284204)")
        self.cap = float(balance_cap)
        self.nW = int(rules.std_winning_days) + 1                 # winning days 0..5 (5 = eligible)
        # unpaid states: B in [-mll, cap], the peak P in [0, mll], the winning days, the request-day flag
        self.nBu = int(round((self.cap + mll) / self.step)) + 1
        self.nM = int(round(mll / self.step)) + 1
        self.nU = self.nBu * self.nM * self.nW * 2
        # paid states: B in (0, cap], the balance after the last payout in [0, cap], the winning days, the flag
        self.nBp = int(round(self.cap / self.step))
        self.nRef = self.nBp + 1
        self.nP = self.nBp * self.nRef * self.nW * 2
        self.nS = self.nU + self.nP
        bu, mu, wu, qu = np.unravel_index(np.arange(self.nU), (self.nBu, self.nM, self.nW, 2))
        bp, rp, wp, qp = np.unravel_index(np.arange(self.nP), (self.nBp, self.nRef, self.nW, 2))
        self.B = np.concatenate([-mll + self.step * bu, self.step * (bp + 1)])
        self.P = np.concatenate([self.step * mu, np.full(self.nP, mll)])
        self.F = np.maximum(-mll, np.minimum(lock, self.P - mll))
        self.wd = np.concatenate([wu, wp])
        self.Q = np.concatenate([qu, qp])
        self.paid = np.concatenate([np.zeros(self.nU, bool), np.ones(self.nP, bool)])
        self.ref = np.concatenate([np.full(self.nU, -np.inf), self.step * rp])
        self.alive = self.B > self.F + EPS
        self.cushion = self.B - self.F
        self.fresh = int(self.index_unpaid(0.0, 0.0, 0, 0))
        self.trans = [self._transition(r, R, flip=(i in self.flip_actions),
                                       flip_out=self.flip_specs[i][0] if i in self.flip_specs else None)
                      for i, (r, R) in enumerate(self.actions)]
        self._set_availability()                                  # D-318
        self._payout_options(payout_grid_step or self.step)
        if self.profit_risk_cap is not None:                      # D-325: in profit (the balance above its start), the cap
            in_profit = self.B > EPS
            self.allowed = np.stack([~in_profit | (r <= self.profit_risk_cap + EPS) if r > 0 else np.ones(self.nS, bool)
                                     for r, _ in self.actions])

    def index_unpaid(self, B, P, w, q) -> np.ndarray:
        b = np.clip(np.rint((np.asarray(B, float) + self.rules.mll) / self.step), 0, self.nBu - 1).astype(np.int64)
        m = np.rint(np.minimum(np.asarray(P, float), self.rules.mll) / self.step).astype(np.int64)
        return ((b * self.nM + m) * self.nW + np.asarray(w, np.int64)) * 2 + np.asarray(q, np.int64)

    def index_paid(self, B, ref, w, q) -> np.ndarray:
        b = np.clip(np.rint(np.asarray(B, float) / self.step) - 1, 0, self.nBp - 1).astype(np.int64)
        r = np.clip(np.rint(np.asarray(ref, float) / self.step), 0, self.nRef - 1).astype(np.int64)
        return self.nU + ((b * self.nRef + r) * self.nW + np.asarray(w, np.int64)) * 2 + np.asarray(q, np.int64)

    def _close(self, Bn: np.ndarray, winning_day: np.ndarray) -> np.ndarray:
        """The close state after a day's trade to balance `Bn`: the floor, the winning days (`winning_day` per state:
        a win of at least the minimum), the flag cleared."""
        wd = np.where(winning_day, np.minimum(self.nW - 1, self.wd + 1), self.wd)
        wd = np.where(self.Q == 1, self.wd, wd)                   # the request day is left out of the cycle
        Bn = np.broadcast_to(np.asarray(Bn, float), (self.nS,))
        Pn = np.maximum(self.P, Bn)
        # each state's own index only -- the unpaid states (the first nU) by the unpaid layout, the paid by the paid:
        # elementwise, so the same integers as computing both everywhere and picking by `paid`
        u, p = slice(0, self.nU), slice(self.nU, self.nS)
        out = np.empty(self.nS, np.int64)
        out[u] = self.index_unpaid(Bn[u], Pn[u], wd[u], 0)
        out[p] = self.index_paid(np.maximum(Bn[p], self.step), self.ref[p], wd[p], 0)
        return out

    def _transition(self, r: float, R: float, flip: bool = False, flip_out: "Outcomes | None" = None):
        """One action's transition per rung. `flip` (D-339): the flip stream's bracket -- its risk exactly as declared
        (the bracket's own contracts, no rung), its win probability from its own measured edge (`flip_out`; D-384: a
        menu bracket's own), the race against the floor as for any trade; the same on every rung, since a scheduled
        bracket has no rung."""
        if r < 0:                                                      # D-329: abandon (the XFA closed, nothing credited)
            return self._abandon_stack()
        no_win = np.zeros(self.nS, bool)
        same = np.where(self.alive, self._close(self.B, no_win), self.DEAD).astype(np.int32)
        if r == 0:
            return self._stack([same] * self.nR, [same] * self.nR, [np.ones(self.nS)] * self.nR)
        out = (flip_out if flip_out is not None else self.flip_out) if flip else self.out
        if flip and out is None:
            raise ValueError("a flip transition needs the menu's flip action (D-339)")
        collect = R == COLLECT_R
        need = float(self.rules.std_winning_day_min)
        iws, ils, ps = [], [], []
        for k in range(self.nR):
            if self.rungs is None or flip:
                real = np.full(self.nS, float(r))
            else:                                                    # the tier read from the balance at the session's start
                real = np.asarray(self.rungs.realised(r, k, self.rungs.funded_cap(self.B)), float)
            if collect:
                # D-379: a win adds the minimum, read at the smallest exit-grid R covering it at the realised size (the
                # exact need without a grid); a size whose need lies beyond the grid takes no trade (the stretch walk's)
                grid = sorted(self.rungs.exit_grid) if (self.rungs is not None and self.rungs.exit_grid) else None
                R_of = np.full(self.nS, np.nan)
                for real_v in np.unique(real[real > 0]):
                    nr = need / float(real_v)
                    g = nr if grid is None else next((x for x in grid if x >= nr - EPS), None)
                    if g is not None:
                        R_of[real == real_v] = float(g)
                real = np.where(np.isfinite(R_of), real, 0.0)
                W = np.where(real > 0, need, 0.0)
            else:
                W = self._grid(real * R)
            L = np.asarray(self._stake(real), float)                  # the loss the grid lands (D-432's fault)
            p = np.ones(self.nS)
            for real_v in np.unique(real[(real > 0) & (L > 0)]):     # a few distinct sizes: the ladder's tiers
                m = real == real_v
                Rv = float(np.unique(R_of[m])[0]) if collect else float(np.unique(W[m])[0]) / float(real_v)
                Lv = float(self._stake(real_v))
                if Lv != float(real_v):                              # off the grid: the target's dollars over its stake
                    Rv = (float(real_v) * Rv if collect else float(np.unique(W[m])[0])) / Lv
                p[m] = out.p_win(self.cushion[m], Lv, Rv)
            traded = (real > 0) & (L > 0)                            # a stake the grid rounds to nothing: no trade
            Bw = np.minimum(self.B + W, self.cap)
            iw = np.where(self.alive & traded, self._close(Bw, W >= self.rules.std_winning_day_min - EPS), np.where(self.alive, same, self.DEAD)).astype(np.int32)
            c = np.minimum(L, self.cushion)                           # the stake the grid carries
            Bl = self.B - c
            dead = traded & (Bl <= self.F + EPS)
            il = np.where(dead | ~self.alive, self.DEAD,
                          np.where(traded, self._close(np.where(dead, self.B, Bl), no_win), same)).astype(np.int32)
            iws.append(iw), ils.append(il), ps.append(np.where(traded, p, 1.0))
        return self._stack(iws, ils, ps)

    def _payout_options(self, qstep: float) -> None:
        ru = self.rules
        self.q_values = np.arange(np.ceil(ru.payout_min / qstep - EPS) * qstep, ru.std_cap + EPS, qstep)
        eligible = self.alive & (self.wd >= ru.std_winning_days)
        if ru.require_profit_since_payout:
            eligible &= (~self.paid) | (self.B > self.ref + EPS)
        allowed = np.minimum(ru.payout_max_frac_of_balance * self.B, ru.std_cap)
        self.pay_idx, self.pay_mask, self.pay_net = [], [], []
        for q in self.q_values:
            mask = eligible & (q <= allowed + EPS) & (self.B - q > EPS)
            after = self.index_paid(np.where(mask, self.B - q, self.step), np.where(mask, self.B - q, 0.0), 0, 1)
            self.pay_idx.append(after.astype(np.int32))
            self.pay_mask.append(mask)
            self.pay_net.append(float(ru.profit_split * q - ru.payout_fee))
        self.eligible = eligible

    def _pay_sub(self) -> list[tuple[np.ndarray, np.ndarray, float]]:
        """Each payout option's eligible states and where a request takes them (intp), built once: the close step and
        the forward pass read the option only where it applies (elsewhere it moves nothing)."""
        key = (self.pay_idx, self.pay_mask, self.pay_net)
        cached = getattr(self, "_pay_sub_cache", None)
        if cached is not None and all(x is y for x, y in zip(cached[0], key)):
            return cached[1]
        out = []
        for idx, mask, net in zip(self.pay_idx, self.pay_mask, self.pay_net):
            mi = np.flatnonzero(mask)
            out.append((mi, np.asarray(idx, np.intp)[mi], net))
        self._pay_sub_cache = (key, out)
        return out

    def _close_values(self, V: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """V at a close: hold, or a payout request -- the best one, or the largest allowed for a fixed baseline. Each
        option is read only at its eligible states (`_pay_sub`), in the same order, to the bit."""
        Vc = V.copy()
        choice = np.zeros(self.nS, np.uint8)
        for j, (mi, to, net) in enumerate(self._pay_sub()):
            cand = net + np.take(V, to)
            if self.payout_choice == "max":
                Vc[mi] = cand
                choice[mi] = j + 1
            else:
                take = cand > Vc[mi]
                s = mi[take]
                Vc[s] = cand[take]
                choice[s] = j + 1
        return Vc, choice

    def solve(self) -> Solution:
        V = np.zeros(self.nS)
        policy = np.zeros((self.T, self.nS), np.uint8)
        payout = np.zeros((self.T, self.nS), np.uint8)
        fresh = np.zeros(self.T + 1)
        self._drop_plan()                                         # built afresh for this solve, freed after it
        try:
            for t in range(self.T - 1, -1, -1):
                Vc, payout[t] = self._close_values(V)
                ext = np.concatenate([Vc, [0.0, 0.0, 0.0]])       # DEAD, PASS (unused), ABANDONED (D-329)
                V, policy[t] = self._day_values(ext, self.lam)
                fresh[t] = V[self.fresh]
        finally:
            self._drop_plan()
        return Solution(value=float(fresh[0]), policy=policy, fresh_value=fresh, payout=payout)

    def forward(self, sol: Solution, t0: int = 0) -> dict[str, Any]:
        dist = np.zeros(self.nS)
        dist[self.fresh] = 1.0
        dead = days = cash = gross = n_pay = first = abandoned = 0.0
        alive_at: dict[int, float] = {}
        vis = np.zeros((self.nS, len(self.actions)))
        # The payout step reads each option only at the states it moves: `m` -- the mass at the states choosing the
        # option where it is allowed, 0.0 elsewhere -- is laid in a zeroed buffer, so its sums run over the same array
        # as before (numpy's pairwise sum, to the bit); the paid states follow the unpaid ones (__init__), so m[~paid]
        # is m[:nU]; a state the option does not move adds +0.0 to `moved` and subtracts 0.0 from `dist` (no change).
        mbuf = np.zeros(self.nS)
        acc = self._scatter_acc(self.nS + 3)[:self.nS]
        for t in range(t0, self.T):
            alive = dist.sum()
            if alive < 1e-15:
                break
            if t - t0 + 1 in ALIVE_CHECKPOINTS:
                alive_at[t - t0 + 1] = float(alive)
            new = self._push(dist, sol.policy[t], vis)
            days += alive - new[self.ABANDONED]                  # an abandoned account holds no slot that day
            abandoned += new[self.ABANDONED]
            dist = new[:self.nS].copy()
            dead += new[self.DEAD]
            ch = sol.payout[t]
            moved = np.zeros(self.nS)
            held = np.flatnonzero(dist > 0)
            for j, pos in _groups(ch[held]):
                if j == 0:
                    continue
                idx, mask, net = self.pay_idx[j - 1], self.pay_mask[j - 1], self.pay_net[j - 1]
                s = held[pos]
                s = s[mask[s]]
                mbuf[s] = dist[s]
                tot = mbuf.sum()
                if tot <= 0:
                    mbuf[s] = 0.0
                    continue
                cash += tot * net
                gross += tot * float(self.q_values[j - 1])
                n_pay += tot
                first += mbuf[:self.nU].sum()
                _scatter_add(moved, acc, idx[s], mbuf[s])
                dist[s] = dist[s] - mbuf[s]
                mbuf[s] = 0.0
            dist = dist + moved
        return {"mean_cash": float(cash), "mean_gross_paid": float(gross), "mean_payouts": float(n_pay),
                "p_paid": float(first), "p_closed": float(dead), "p_abandoned": float(abandoned),
                "p_alive_at_end": float(dist.sum()), "mean_days": float(days), "alive_at": alive_at, "visitation": vis}


# ----------------------------------------------------------------------------------------------------- export

#: D-321: the payout-line bands a paid account's decision is keyed by -- its profit since the last payout below
#: -$1,000, -$1,000 to -$500, -$500 to -$250, -$250 to the line, and over the line (8284233: at least $0.01)
LINE_GAP_FROMS = (-1e13, -1000.0, -500.0, -250.0, 0.01)


def line_gap_band(gap: np.ndarray) -> np.ndarray:
    """Each value's band in LINE_GAP_FROMS (its lower edge)."""
    edges = np.asarray(LINE_GAP_FROMS, float)
    return edges[np.clip(np.searchsorted(edges, np.asarray(gap, float), side="right") - 1, 0, len(edges) - 1)]


#: D-326: the lower edge of the split band just above the start (as the payout-line band's: at least a cent)
START_SPLIT = 0.01


def project(dp: _DP, vis: np.ndarray, balance_band: float, cushion_band: float, *, phases_mask: np.ndarray | None = None,
            extra: Sequence[tuple[str, np.ndarray]] = (), split_start: bool = False, pol0: np.ndarray | None = None):
    """The most-visited action per (balance band, cushion band): {(b, c): (risk, rr, share)} with `share` the action's
    share of the band's trading visitation; the mass that chose no trade; and (D-302) the bands where no trade was
    visited at least as much as the most-visited trade -- exported as no-trade states, where before D-302 the trade
    stood in for them (the DP audit's finding 4). A band visited only by no-trade carries the menu's smallest action as
    its placeholder. `extra` (D-321): further keys, each (name, per-state band values), appended to every cell's key --
    the funded table's winning days and payout-line band, which (balance, cushion) alone marginalised away.
    `split_start` (D-326): the band holding the start (balance 0) is split so the start is a band of its own and the
    states just above it (to the band's end) are keyed by START_SPLIT -- under D-325's cap the start is unconstrained
    and every in-profit state is capped, and one band for both exported the start's bet into them.
    `pol0` (D-332): the table's day-0 policy (`Solution.policy[0]`); with it EVERY band the state space contains gets
    a cell -- the most-visited action where the chain visited the band, and otherwise the table's own decision there
    by state count -- so the engine, whose tier lookup takes the nearest band below, never inherits a neighbouring
    band's choice for a state the chain happened not to reach (the v9 run's funded accounts closed near-fresh: the
    band just above the start had been visited only within $250 of the floor, where the table abandons). Without it,
    the export is the visited bands only, as before."""
    mask = dp.alive if phases_mask is None else (dp.alive & phases_mask)
    bb = np.floor(dp.B / balance_band) * balance_band
    if split_start:
        bb = np.where((dp.B > EPS) & (bb == 0.0), START_SPLIT, bb)
    cb = np.minimum(np.floor(dp.cushion / cushion_band) * cushion_band, dp.rules.mll)
    ex = [np.asarray(v, float) for _, v in extra]
    flip_action = getattr(dp, "flip_action", None)               # D-339: a cell's fourth element names its source
    flip_set = getattr(dp, "flip_actions", None) or (frozenset({flip_action}) if flip_action is not None else frozenset())

    def _src(a: int) -> str:
        if a in flip_set:                                         # D-384: any scheduled bracket, the menu's included
            return "flip"
        return "collect" if dp.actions[a][1] == COLLECT_R else "strategy"     # D-379

    out: dict[tuple[float, ...], tuple[float, float, float, str]] = {}
    idle: set[tuple[float, ...]] = set()
    skip_mass = 0.0
    has_skip = dp.actions[0] == SKIP
    seen = mask & (vis.sum(axis=1) > 0)
    domain = mask if pol0 is not None else seen
    nA = len(dp.actions)
    for key in sorted({tuple(float(z) for z in t) for t in zip(bb[domain], cb[domain], *[e[domain] for e in ex])}):
        cell = mask & (bb == key[0]) & (cb == key[1])
        for e, v in zip(ex, key[2:]):
            cell &= e == v
        sel = cell & seen
        if sel.any():
            w = vis[sel].sum(axis=0)
        else:                                     # D-332: unvisited -- the table's own day-0 decision, by state count
            w = np.bincount(np.asarray(pol0, np.int64)[cell], minlength=nA).astype(float)
        w_skip = 0.0
        if has_skip:
            w_skip = float(w[0])
            if sel.any():
                skip_mass += w_skip
            w = w.copy()
            w[0] = 0.0
        if w.sum() <= 0:
            if w_skip > 0:
                a = 1 if has_skip else 0
                out[key] = (dp.actions[a][0], dp.actions[a][1], 0.0, _src(a))
                idle.add(key)
            continue
        a = int(np.argmax(w))
        out[key] = (dp.actions[a][0], dp.actions[a][1], float(w[a] / w.sum()), _src(a))
        if has_skip and w_skip >= float(w[a]):
            idle.add(key)
            if dp.actions[a][0] < 0:              # D-329: a no-trade band's placeholder must be a trade (the engine sizes it)
                out[key] = (dp.actions[1][0], dp.actions[1][1], out[key][2], _src(1))
    return out, float(skip_mass), idle


def tiers_from(table: dict[tuple[float, ...], tuple[float, float, float]], label: str,
               idle: set[tuple[float, ...]] | None = None, names: Sequence[str] = ("balance", "cushion")):
    """A balance-then-cushion tier tree from `project`'s table, for `propedge.campaign.risk_policy`; a band in `idle`
    is a no-trade state (D-302: `max_trades` 0, the action a placeholder the engine never uses). `names` (D-321): the
    variable of each key position, deeper keys nested under the cushion's (the funded table's winning days, its
    payout-line band)."""
    from propedge.campaign.risk_policy import Leaf, Tiers

    idle = idle or set()
    leaves: dict[tuple[float, ...], Any] = {}
    for key, cell in table.items():
        risk, rr, share = cell[0], cell[1], cell[2]
        source = cell[3] if len(cell) > 3 else "strategy"         # D-339: the cell's source; older tables carry none
        if key in idle:                                           # D-379: a collect placeholder carries no R
            leaves[key] = Leaf(f"{label} no trade", risk=risk, rr=(None if rr == COLLECT_R else rr), max_trades=0)
        elif risk < 0:                                            # D-329: the table's abandon
            leaves[key] = Leaf(f"{label} abandon", risk=0.0, rr=None, max_trades=0, abandon=True)
        elif source == "flip":                                    # D-339: the flip stream's bracket, every session
            leaves[key] = Leaf(f"{label} flip ${risk:,.0f} {rr:g}R", risk=risk, rr=rr, max_trades=1, source="flip")
        elif source == "collect":                                 # D-379: a routed signal, take-profit at the shortfall
            leaves[key] = Leaf(f"{label} collect ${risk:,.0f}", risk=risk, rr=None, max_trades=1, source="collect")
        else:
            leaves[key] = Leaf(f"{label} ${risk:,.0f} {rr:g}R", risk=risk, rr=rr, max_trades=1)

    def build(items: list[tuple[tuple[float, ...], Any]], depth: int):
        if depth == len(names):
            return items[0][1]
        groups: dict[float, list] = {}
        for key, leaf in items:
            groups.setdefault(key[depth], []).append((key, leaf))
        return Tiers(on=names[depth], name=label if depth == 0 else "",
                     tiers=tuple((v, build(g, depth + 1)) for v, g in sorted(groups.items())))

    return build(sorted(leaves.items()), 0)


def export_policy(policy_id: str, combine: CombineDP, c_vis: np.ndarray, funded: FundedDP, f_vis: np.ndarray,
                  balance_band: float, cushion_band: float, description: str = "", version: int = 1,
                  c_pol0: np.ndarray | None = None, f_pol0: np.ndarray | None = None):
    """The DP's decisions as an engine `RiskPolicy`: Combine, funded (unpaid) and paid phases; and the projection's
    bookkeeping. `version` 2 and later (D-302) export the bands where the DP chose no trade as no-trade states
    (`idle_bands`, as (phase, balance band, cushion band)); version 1 is D-290's export, a trade standing in for them;
    version 3 (D-306) is the same export of a table solved with the allowance built in (`Menu.rungs`); version 7
    (D-321) keys the funded decisions by the payout conditions; version 8 (D-325) is version 7's export of a funded
    table solved under the two rules (`FundedDP(tie_break_tol=..., profit_risk_cap=...)`); version 9 (D-326) splits
    the unpaid funded balance band at the start (`project(split_start=True)`), so the cap's exemption of the start
    does not reach the first in-profit states; version 11 (D-332) exports every band the state space contains, the
    table's own day-0 decision standing where the chain never visited (`c_pol0`, `f_pol0`: the day-0 policies,
    required from version 11); version 12 (D-333) leaves the funded balance cap's band out, a modelling boundary the
    engine does not have; version 13 (D-339) carries each cell's source -- 'strategy' or 'flip' -- on its leaf and in
    `cells` (the same export otherwise)."""
    from propedge.campaign.risk_policy import Phase, RiskPolicy

    # D-321 (version 7): a funded decision keyed by the payout-request day and its winning days too, and a paid one by
    # its payout-line band -- the Standard path's conditions, which (balance, cushion) alone marginalised away. The
    # request day has its own cell: the table sits it out (it is left out of the cycle), and pooled with the days after
    # it that no-trade would become every such day's decision -- an account that never trades again
    f_extra: list = []
    p_extra: list = []
    if int(version) >= 7:
        wd = np.minimum(funded.wd, funded.nW - 1).astype(float)
        q = funded.Q.astype(float)
        f_extra = [("request_day", q), ("win_days", wd)]
        p_extra = [("request_day", q), ("win_days", wd),
                   ("line_gap", line_gap_band(np.where(funded.paid, funded.B - funded.ref, 0.0)))]
    full = int(version) >= 11                                                       # D-332: every band, no gaps
    if full and (c_pol0 is None or f_pol0 is None):
        raise ValueError("export version 11 needs the day-0 policies (c_pol0, f_pol0) to fill the bands the chain never visited (D-332)")
    cp, fp = (c_pol0, f_pol0) if full else (None, None)
    # D-333 (version 12): the funded state space's balance cap is a modelling boundary -- at the cap a win can add
    # nothing, so the exact table's decision there is abandon -- and the full export (v11) carried that boundary
    # decision into the engine, which has no cap; the cap band is left out, so the engine reads the band below it
    at_cap = (funded.B >= funded.cap - EPS) if int(version) >= 12 else np.zeros(funded.nS, bool)
    ct, c_skip, c_idle = project(combine, c_vis, balance_band, cushion_band, pol0=cp)
    ft, f_skip, f_idle = project(funded, f_vis, balance_band, cushion_band, phases_mask=~funded.paid & ~at_cap,
                                 extra=f_extra, split_start=int(version) >= 9, pol0=fp)   # D-326, D-332, D-333
    pt, p_skip, p_idle = project(funded, f_vis, balance_band, cushion_band, phases_mask=funded.paid & ~at_cap,
                                 extra=p_extra, pol0=fp)
    if int(version) < 2:
        c_idle, f_idle, p_idle = set(), set(), set()
    f_names = ("balance", "cushion", *[n for n, _ in f_extra])
    p_names = ("balance", "cushion", *[n for n, _ in p_extra])
    pol = RiskPolicy(id=policy_id, description=description, version=int(version),
                     root=Phase(combine=tiers_from(ct, "combine", c_idle),
                                funded=tiers_from(ft, "funded", f_idle, f_names),
                                paid=tiers_from(pt, "paid", p_idle, p_names) if pt else None))
    pol.validate()

    def _cells(phase, table, names):
        return [(phase, k[0], k[1], c[0], c[1], c[2], dict(zip(names[2:], k[2:])), c[3] if len(c) > 3 else "strategy")
                for k, c in table.items()]

    cells = _cells("combine", ct, ("balance", "cushion")) + _cells("funded", ft, f_names) + _cells("paid", pt, p_names)
    idle = ({("combine", *k) for k in c_idle} | {("funded", *k) for k in f_idle} | {("paid", *k) for k in p_idle})
    return pol, {"combine_skip_mass": c_skip, "funded_skip_mass": f_skip, "paid_skip_mass": p_skip, "cells": cells,
                 "idle_bands": idle}


__all__ = ["STEP", "SKIP", "COLLECT_R", "Rungs", "Menu", "Outcomes", "Solution", "CombineDP", "FundedDP", "project",
           "tiers_from", "export_policy"]
