"""Wave 3.2: the three-way runner's journey -- **journey = f(schedule, coin field, rules)** (the design note's 1.7) --
replayed over lanes: the coin seeds of one start (Monte Carlo, `simulate`) or the distinct states of one start with
their exact probabilities (the dynamic program of 2.4, `expect`). Both run the same transition code, so the program's
expectation is the simulation's own law, exactly.

**The schedule** (`Trade`, `Schedule`): per trade its session index and decision slot (the coin key's moment), its
entry and exit slots and terminal state **as run**, its bracket (g, l) in ticks, contracts, tick value, its costs in
dollars (entry, and the target, stop and flatten exits), and for a time-limited trade R-10's lattice step and number of
steps (read from the causal volatility at the alert: the schedule's field). **No bar is read here**: a history enters
only through its schedule, so two histories with one schedule give one journey (the exact test of 1.7).

**Overlap is refused** (1.6; the amendments' m-2): a schedule whose positions' holding intervals overlap -- on the
scheduled entries and the run's exit times, defined before any draw -- is refused at construction, and so is one with
two trades at one moment (they would read one uniform). The replay holds one account at a time, so no two positions of
the user are ever open together.

**The rules** (`ToyRules`): a stylised two-phase account -- an evaluation with a fee per billing period, a profit
target, a trailing end-of-day maximum loss and a daily loss limit; on a pass an activation fee and a funded account
with a trailing floor locked at its start, payouts after a count of winning days, a share of the balance capped,
the trader's split, arriving after a lag. **Every value is the caller's; none is a firm's** (a firm's run reads the
vendored engine with its verified rules; this replay exists for synthetic toys, the exact program and H3's design
checks). A failed account is replaced at that close by a new evaluation.

**The cushion** is the room to the nearer of the floor and the daily loss limit, read after the entry cost
(`three_way_redraw`'s race); a breach is a balance at or below the floor (within `EPS`), as the vendored lockstep
reads it. **The barrier is fractional** (the lead's ruling on B-1): a cushion-bound loss ends exactly on the floor, so
the account fails at that close and is replaced, as the engine's; R-10's walk ends its last step by a two-point race
to the fractional barrier (`three_way_redraw.walk_law`).

**The money and the readings** (MEASURES.md 1.2): `rel[k]` is the cash at close k less the start -- payouts arrived
less fees paid; day 0 is the purchase evening. A payout's cash arrives `payout_lag` closes after its request. The
program carries P_B's per-unit count (`MEASURES.md` section 2: ahead at month m when `rel[21 m] > 1e-6` and the peak
out-of-pocket through the closes before it at most B).

**Enforcement** (the denial ladder, beside; 0 % in the verdict): a payout request is denied with probability q by the
`enforce` key of its unit, account and request -- seeded apart from the coin, so the ladder moves no coin draw.

numpy and fractions; imports no engine.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from fractions import Fraction
from typing import Callable, Sequence

import numpy as np

from extended import three_way_fastkeys as F
from extended import three_way_keys as K
from extended import three_way_redraw as RD

MONTH = 21
TOL = 1e-6              # "ahead" above a millionth of a dollar (MEASURES.md 1.2)
EPS = 1e-6              # a breach: the balance at or below the floor within this
#: R-10's walk is read this many steps at a time, only for the lanes still walking (`three_way_redraw.walk_run`): the
#: same outcome as reading every step, at the cost of the steps walked
WALK_CHUNK = 32
#: the longest walk a trade may read: `tests/test_three_way_fastkeys.py` admits the vectorised generator on every output
#: up to it; a longer walk is refused (the red team's rn-2)
WALK_MAX = 1024


# ------------------------------------------------------------------------------------------------ the schedule


@dataclass(frozen=True)
class Trade:
    """One scheduled trade, as run; its outcome is redrawn (the martingale-outcome reading)."""

    session: int
    decision: int
    entry: int
    exit: int
    exit_reason: str
    g: int
    l: int
    tick_value: float
    contracts: int = 1
    sub: int = 0
    entry_cost: float = 0.0
    x_target: float = 0.0
    x_stop: float = 0.0
    x_flat: float = 0.0
    walk_step: int = 1
    walk_n: int = 1
    underlying: str = "NQ"
    walked_ticks: float | None = None       # the run's gross ticks for a long (the as-walked reading beside)
    level: float | None = None              # a rule's profit level: the net dollars the trade must make (m-2, m-3)

    def __post_init__(self) -> None:
        RD.law_of(self.exit_reason)
        if not (0 <= self.entry < self.exit <= K.DAY_SLOTS):
            raise ValueError(f"a trade enters and exits inside its trading day, entry before exit: {self}")
        if self.g <= 0 or self.l <= 0 or self.contracts <= 0 or self.tick_value <= 0:
            raise ValueError("bracket, contracts and tick value are positive")
        if min(self.entry_cost, self.x_target, self.x_stop, self.x_flat) < 0:
            raise ValueError("costs are non-negative")
        if self.law == "walk" and (self.walk_n < 1 or self.walk_step < 1):
            raise ValueError("a time-limited trade's lattice step and its steps are at least one (s-c: the step need not "
                             "divide its bracket)")
        if self.level is not None and not self.level > 0:
            raise ValueError("a profit level is positive")
        if self.exit_reason == "profit_level" and self.level is None:
            raise ValueError("a profit-level exit carries its level")
        if self.law == "walk" and self.walk_n > WALK_MAX:
            raise ValueError(f"REFUSED (rn-2): a walk of {self.walk_n} steps reads past the {WALK_MAX} outputs the "
                             "vectorised generator is admitted on")
        K.moment(self.session, self.decision, self.sub)

    @property
    def law(self) -> str:
        return RD.law_of(self.exit_reason)

    @property
    def moment(self) -> int:
        return K.moment(self.session, self.decision, self.sub)

    def target(self, e: float, xt: float) -> float:
        """The as-placed target in gross ticks, for every terminal state of the trade (the level is known at
        placement; m-2). **A profit level is booked as the vendored engine books its need** (m-3): the net dollars
        the trade must make, every cost of the trade included -- `lockstep.CombineAccount.need_to_pass` ("what the
        account must net on its next trade to pass", `vendor/stage2/propedge/campaign/lockstep.py` l.408-419), which
        the need-aware draw "settles ... at exactly the need" (`vendor/stage2/propedge/campaign/sizing.py` l.380-388,
        `self._settle(float(need) if at_need ...)`). So G = min(g, (level + entry + x_target) / tick dollars), at the
        trade's own costs (a worse-fill stress included), and a win at the level books exactly +level."""
        if self.level is None:
            return float(self.g)
        return min(float(self.g), (float(self.level) + float(e) + float(xt)) / self.tvn)

    @property
    def tvn(self) -> float:
        return float(self.tick_value) * int(self.contracts)


@dataclass(frozen=True)
class Schedule:
    """A design's (or a baseline's) trades on one history, in time order; refused when two positions' holding
    intervals overlap or two trades share a moment."""

    name: str
    trades: tuple[Trade, ...]
    by_session: dict = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        ts = tuple(sorted(self.trades, key=lambda t: (t.session, t.entry, t.decision, t.sub)))
        object.__setattr__(self, "trades", ts)
        seen: set[int] = set()
        by: dict[int, list[Trade]] = {}
        for t in ts:
            if t.moment in seen:
                raise ValueError(f"REFUSED: {self.name} has two trades at one moment ({t.session}, {t.decision}, "
                                 f"{t.sub}): they would read one uniform")
            seen.add(t.moment)
            day = by.setdefault(t.session, [])
            if day and t.entry < day[-1].exit:
                raise ValueError(f"REFUSED (1.6, m-2): {self.name} holds two positions at once on session "
                                 f"{t.session} (entry {t.entry} before the open position's exit {day[-1].exit}); "
                                 "overlap stays refused until the template defines one shared driftless path")
            day.append(t)
        object.__setattr__(self, "by_session", {k: tuple(v) for k, v in by.items()})

    def window(self, start: int, horizon: int) -> "Schedule":
        """The trades of sessions start .. start + horizon - 1 only."""
        return Schedule(self.name, tuple(t for t in self.trades if start <= t.session < start + horizon))


# ------------------------------------------------------------------------------------------------ the rules


@dataclass(frozen=True)
class ToyRules:
    """A stylised two-phase account (every value the caller's; none a firm's)."""

    combine_fee: float
    billing: int
    target: float
    mll: float
    dll: float | None
    activation_fee: float
    funded_mll: float
    win_day: float
    payout_days: int
    payout_share: float
    payout_cap: float
    split: float
    payout_lag: int
    combine_lock: float | None = 0.0         # the evaluation's trailing floor stops at the start balance
    label: str = "toy rules, no firm's"

    def __post_init__(self) -> None:
        if self.billing < 1 or self.payout_days < 1 or self.payout_lag < 1:
            raise ValueError("billing, payout days and the payout lag are at least one session")
        if not 0 < self.payout_share < 1 or not 0 < self.split <= 1:
            raise ValueError("a payout takes a share of the balance in (0, 1); the split is in (0, 1]")
        if min(self.combine_fee, self.activation_fee, self.target, self.mll, self.funded_mll, self.payout_cap) <= 0:
            raise ValueError("fees, target, loss limits and cap are positive")


# ------------------------------------------------------------------------------------------------ the lanes


@dataclass
class Lanes:
    """The state of n lanes (one unit per lane, or one exact state with its probability `w`)."""

    phase: np.ndarray      # 0 evaluation, 1 funded
    bal: np.ndarray
    floor: np.ndarray
    peak: np.ndarray
    age: np.ndarray        # sessions since the account's purchase or activation
    wins: np.ndarray
    cash: np.ndarray
    minrel: np.ndarray     # the lowest rel over the closes so far
    ahead: np.ndarray      # P_B's months-ahead count so far
    pend: np.ndarray       # payouts on their way, a ring of payout_lag + 1 closes
    acct: np.ndarray       # the account's ordinal in the journey (the enforce key's)
    req: np.ndarray        # the request's ordinal in the account (the enforce key's)
    first_pass: np.ndarray
    first_pay: np.ndarray
    w: np.ndarray          # the exact program's probability (1 in a simulation)
    ffail: np.ndarray = None  # accounts failed at the fill (the take refused at a floor-bound room), counted apart
    day: np.ndarray = None  # today's net
    dead: np.ndarray = None  # the account failed today (replaced at the close)
    stopped: np.ndarray = None  # no more trades today (the daily loss limit)

    def take(self, idx: np.ndarray) -> "Lanes":
        return Lanes(**{k: (None if v is None else v[idx]) for k, v in self.__dict__.items()})

    @staticmethod
    def concat(parts: Sequence["Lanes"]) -> "Lanes":
        keys = parts[0].__dict__.keys()
        return Lanes(**{k: (None if parts[0].__dict__[k] is None else np.concatenate([p.__dict__[k] for p in parts]))
                        for k in keys})

    def __len__(self) -> int:
        return len(self.bal)


def fresh(n: int, rules: ToyRules) -> Lanes:
    """n lanes on the purchase evening (day 0): an evaluation bought, its fee paid."""
    f = np.zeros(n)
    i = np.zeros(n, np.int64)
    cash = np.full(n, -float(rules.combine_fee))
    return Lanes(phase=i.copy(), bal=f.copy(), floor=np.full(n, -float(rules.mll)), peak=f.copy(), age=i.copy(),
                 wins=i.copy(), cash=cash, minrel=cash.copy(), ahead=i.copy(),
                 pend=np.zeros((n, rules.payout_lag + 1)), acct=i.copy(), req=i.copy(), first_pass=i - 1,
                 first_pay=i - 1, w=np.ones(n), ffail=i.copy())


def _room(L: Lanes, rules: ToyRules) -> np.ndarray:
    room = L.bal - L.floor
    if rules.dll is not None:
        room = np.minimum(room, float(rules.dll) + L.day)
    return room


def _barrier(t: Trade, room: np.ndarray, extra: float) -> np.ndarray:
    """The floor-side barrier in ticks, **fractional** (the lead's ruling on B-1): min(l, (room - entry - x_stop) /
    tick dollars) -- the race's and, since corrective cycle 2, R-10's walk's too (its flatten exit is clipped at the
    floor instead; RB-1). A cushion-bound loss ends exactly on the floor and fails the account."""
    e, xs = t.entry_cost + extra, t.x_stop + extra
    return np.minimum(float(t.l), (room - e - xs) / t.tvn)


def _l_fill(t: Trade, room: np.ndarray, extra: float) -> np.ndarray:
    """The take, decided at the fill (the template's N-1; the red team's m-1): L_fill = min(l, (room - entry -
    max(x_stop, x_flat)) / tick dollars), unrounded, for every exit law -- it reads the bracket, the room and both exit
    costs, never the run's exit."""
    e, xs, xf = t.entry_cost + extra, t.x_stop + extra, t.x_flat + extra
    return np.minimum(float(t.l), (room - e - max(xs, xf)) / t.tvn)


def _classes(t: Trade, act: np.ndarray, room: np.ndarray, floor_room: np.ndarray, extra: float
             ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """(the barrier, the lanes taking the trade, the lanes failed at the fill, the lanes whose day ends).

    **The take** at the fill: L_fill above `EPS` dollars (`_l_fill`). **A lane that cannot take it** (the lead's
    rulings on RB-1 and on the template read's B-2): where the floor's room binds, the account **fails at the fill** --
    its balance taken to the floor, a breach, replaced at the close, counted apart (`Lanes.ffail`) -- the race's own
    limit as its barrier goes to zero, and the vendored engine's end for such an account (it races the room and clips
    at the cushion: `lockstep.py`, `max(pnl, -cushion)`, then `B <= F + EPS`); where the daily loss limit's room binds,
    the day ends. So no account is left alive with room it can never trade."""
    Lt = _barrier(t, room, extra)
    take = act & (_l_fill(t, room, extra) * t.tvn > EPS)
    floor_bound = floor_room <= room + EPS
    fail = act & ~take & floor_bound
    stop_day = act & ~take & ~floor_bound
    return Lt, take, fail, stop_day


def _settle(L: Lanes, act: np.ndarray, change: np.ndarray, rules: ToyRules) -> None:
    """Book each acting lane's change; a breach ends the account (replaced at the close); the daily loss limit stops
    the day. **No booked change passes the floor or the daily limit** (B-1, N-5, M-4, RB-1): the race's barrier nets
    the stop exit's cost, and where a cost would pass a barrier -- a walk's flatten, an account failed at the fill --
    the caller has already clipped it there, as the engine clips; a change that still passes either by more than `EPS`
    is refused."""
    L.bal = np.where(act, L.bal + change, L.bal)
    L.day = np.where(act, L.day + change, L.day)
    if (act & (L.bal < L.floor - EPS)).any() or (rules.dll is not None and (act & (L.day < -float(rules.dll) - EPS)).any()):
        raise RuntimeError("REFUSED (B-1, M-4): a redrawn loss passed the floor or the daily loss limit: the race's "
                           "barrier is not the cushion less the stop exit's own cost")
    breach = act & (L.bal <= L.floor + EPS)
    L.dead |= breach
    if rules.dll is not None:
        L.stopped |= act & (L.day <= -float(rules.dll) + EPS)


@dataclass(frozen=True)
class ArmSpec:
    """How an arm reads its trades: the antithetic twin, P3's edge plant, measure 29's worse fill, measure 28's
    missed share, the denial ladder's probability and the reading (`martingale`, or `as_walked` beside)."""

    twin: bool = False
    plant_eps: float = 0.0
    worse_ticks: int = 0
    missed_q: float = 0.0
    enforcement_q: float = 0.0
    reading: str = "martingale"

    def __post_init__(self) -> None:
        if self.reading not in ("martingale", "as_walked"):
            raise ValueError("the reading is 'martingale' (deciding) or 'as_walked' (beside)")
        if not (0 <= self.plant_eps < 1 and 0 <= self.missed_q < 1 and 0 <= self.enforcement_q < 1):
            raise ValueError("a plant, a missed share and a denial probability lie in [0, 1)")
        if self.worse_ticks < 0:
            raise ValueError("a worse fill is non-negative")


class CoinLanes:
    """The coin field of the lanes of one start: lane j is unit (start, seed_indices[j]). The uniforms come from the
    declared law vectorised (`three_way_fastkeys`, admitted by its bit-identity tests against the scalar path, every
    output a walk reads included); every key carries the start by construction (one start a call); the guard checks
    and stores the keys of its declared sample, built one by one through `three_way_keys.Unit` (N-2 at construction)."""

    def __init__(self, seed: int, part: int, history: int, start: int, seed_indices: Sequence[int],
                 guard: K.KeyGuard | None, twin: bool):
        self.seed, self.part, self.history, self.start = seed, int(part), int(history), int(start)
        self.seed_idx = np.asarray([int(c) for c in seed_indices], dtype=np.int64)
        self.units = [K.Unit(seed, self.part, self.history, int(c), self.start) for c in self.seed_idx]
        self.guard, self.twin = guard, bool(twin)

    def _record(self, idx, make) -> None:
        if self.guard is None:
            return
        for j in idx:
            c = int(self.seed_idx[j])
            if self.guard.in_sample(self.start, c):
                self.guard.add(make(int(j)), self.start, c)
            else:
                self.guard.checked += 1

    def coin(self, t: Trade, kind: int, n: int = 1, lanes: np.ndarray | None = None, first: int = 0,
             record: bool = True) -> np.ndarray:
        idx = np.arange(len(self.units)) if lanes is None else np.asarray(lanes, dtype=np.int64)
        if record:
            self.record(t, kind, idx)
        return F.coin_uniforms(self.seed, self.part, self.history, self.seed_idx[idx], self.start, t.moment, kind,
                               n, self.twin, t.underlying, first)

    def record(self, t: Trade, kind: int, idx) -> None:
        self._record(np.asarray(idx, dtype=np.int64), lambda j: self.units[j].coin_key(t.moment, kind, t.underlying))

    def enforce(self, acct: np.ndarray, req: np.ndarray, lanes: np.ndarray) -> np.ndarray:
        idx = np.asarray(lanes, dtype=np.int64)
        self._record(idx, lambda j: self.units[j].enforce_key(int(acct[j]), int(req[j])))
        return F.enforce_uniforms(self.seed, self.part, self.history, self.seed_idx[idx], self.start, acct[idx],
                                  req[idx], self.twin)


# ------------------------------------------------------------------------------------------------ one session


def _trade_mc(L: Lanes, t: Trade, rules: ToyRules, arm: ArmSpec, coins: CoinLanes) -> None:
    act = ~(L.dead | L.stopped)
    if arm.missed_q > 0 and act.any():
        miss = coins.coin(t, K.MISSED)[:, 0] < arm.missed_q
        act &= ~miss
    if not act.any():
        return
    extra = float(arm.worse_ticks) * t.tvn
    e = t.entry_cost + extra
    xt, xs, xf = t.x_target + extra, t.x_stop + extra, t.x_flat + extra
    room = _room(L, rules)
    Lt, normal, fail, stop_day = _classes(t, act, room, L.bal - L.floor, extra)
    L.stopped |= stop_day
    if fail.any():                                          # failed at the fill: to the floor, breached, counted
        L.ffail = L.ffail + fail.astype(np.int64)
        _settle(L, fail, -room, rules)
    taken = normal
    if not taken.any():
        return
    if arm.reading == "as_walked":
        if t.walked_ticks is None:
            raise ValueError("the as-walked reading needs each trade's walked ticks")
        side = np.where(coins.coin(t, K.SIDE)[:, 0] < 0.5, 1.0, -1.0)
        # beside only, never deciding, and labelled so wherever it is printed: the stop side's cost on every exit (n-5)
        pnl = side * float(t.walked_ticks) * t.tvn - xs
        pnl = np.maximum(pnl, -(room - e))                  # liquidated at the floor, as the engine clips
        _settle(L, taken, -e + pnl, rules)
        return
    change = np.zeros(len(L))
    G = t.target(e, xt)
    if t.law == "race":
        u = coins.coin(t, K.RACE)[:, 0]
        p = Lt / (Lt + G)
        win = RD.race_outcome(u, p, arm.plant_eps)
        change = np.where(normal, -e + np.where(win, G * t.tvn - xt, -Lt * t.tvn - xs), change)
    else:
        s = int(t.walk_step)
        rows_all = np.flatnonzero(normal)
        coins.record(t, K.WALK, rows_all)

        def read(rows, first, count):
            return coins.coin(t, K.WALK, count, rows_all[rows], first=first, record=False)

        v_t, k_t = RD.walk_run(read, rows_all.size, G, Lt[rows_all], s, int(t.walk_n), WALK_CHUNK)
        val = np.zeros(len(L))
        kind = np.zeros(len(L), np.int64)
        val[rows_all], kind[rows_all] = v_t, k_t
        cost = np.where(kind == 1, xt, np.where(kind == -1, xs, xf))
        # a flatten whose cost would pass the floor is clipped there (the engine's clip), and the account fails
        change = np.where(normal, np.maximum(-e + val * t.tvn - cost, -room), change)
    _settle(L, normal, change, rules)


def _trade_dp(L: Lanes, t: Trade, rules: ToyRules, arm: ArmSpec) -> Lanes:
    """The exact program's step: every taking state branches into its outcomes with their probabilities."""
    if arm.missed_q > 0 or arm.reading != "martingale":
        raise ValueError("the exact program reads the martingale-outcome reading with no missed signal")
    act = ~(L.dead | L.stopped)
    if not act.any():
        return L
    extra = float(arm.worse_ticks) * t.tvn
    e = t.entry_cost + extra
    xt, xs, xf = t.x_target + extra, t.x_stop + extra, t.x_flat + extra
    room = _room(L, rules)
    Lt, normal, fail, stop_day = _classes(t, act, room, L.bal - L.floor, extra)
    L.stopped = L.stopped | stop_day
    if fail.any():                                          # failed at the fill (RB-1, B-2): one branch, certain
        L.ffail = L.ffail + fail.astype(np.int64)
        _settle(L, fail, -room, rules)
    if not normal.any():
        return L
    keep = L.take(np.flatnonzero(~normal))
    parts = [keep]
    go = L.take(np.flatnonzero(normal))
    Lg = Lt[normal]
    rg = room[normal]
    G = t.target(e, xt)
    if t.law == "race":
        p = np.minimum(Lg / (Lg + G) + arm.plant_eps, 1.0)
        for win in (True, False):
            b = go.take(np.arange(len(go)))
            b.w = b.w * (p if win else 1.0 - p)
            ch = (G * t.tvn - xt) if win else (-Lg * t.tvn - xs)
            _settle(b, np.ones(len(b), bool), -e + ch, rules)
            parts.append(b)
    else:
        s = int(t.walk_step)
        for Lv in np.unique(Lg):
            sel = np.flatnonzero(Lg == Lv)
            law = RD.walk_law(G, float(Lv), s, int(t.walk_n))
            for (k, v), pr in law.items():
                b = go.take(sel)
                b.w = b.w * float(pr)
                cost = {"target": xt, "stop": xs, "time": xf}[k]
                ch = np.maximum(np.full(len(b), -e + float(v) * t.tvn - cost), -rg[sel])   # the engine's clip
                _settle(b, np.ones(len(b), bool), ch, rules)
                parts.append(b)
    return Lanes.concat(parts)


def _close(L: Lanes, k: int, rules: ToyRules, arm: ArmSpec, budget: float | None, coins: CoinLanes | None,
           dp: bool) -> Lanes:
    """Close k: a failed account replaced, the trailing floors, a pass, a payout request (denied by the ladder with
    probability q), the billing, the arrivals, and P_B's month count."""
    n = len(L)
    dead = L.dead
    # a failed account: a new evaluation bought at this close
    L.cash = np.where(dead, L.cash - rules.combine_fee, L.cash)
    live = ~dead
    # the trailing floors
    L.peak = np.where(live, np.maximum(L.peak, L.bal), L.peak)
    mll = np.where(L.phase == 0, rules.mll, rules.funded_mll)
    nf = np.maximum(L.floor, L.peak - mll)
    lock = np.where(L.phase == 0, np.inf if rules.combine_lock is None else rules.combine_lock, 0.0)
    L.floor = np.where(live, np.minimum(nf, lock), L.floor)
    # a pass
    passed = live & (L.phase == 0) & (L.bal >= rules.target - EPS)
    L.first_pass = np.where(passed & (L.first_pass < 0), k, L.first_pass)
    L.cash = np.where(passed, L.cash - rules.activation_fee, L.cash)
    # a funded account's winning day and payout request
    fund = live & (L.phase == 1)
    L.wins = np.where(fund & (L.day >= rules.win_day - EPS), L.wins + 1, L.wins)
    ask = fund & (L.wins >= rules.payout_days) & (L.bal > EPS)
    denied = np.zeros(n, bool)
    parts: list[Lanes] = []
    if ask.any() and arm.enforcement_q > 0:
        if dp:
            q = float(arm.enforcement_q)
            idx = np.flatnonzero(ask)
            d = L.take(idx)
            d.w = d.w * q
            d.dead = np.ones(len(d), bool)
            d.cash = d.cash - rules.combine_fee            # denied: the account ends, a new evaluation bought
            L.w = np.where(ask, L.w * (1.0 - q), L.w)
            parts.append(d)
        else:
            lanes = np.flatnonzero(ask)
            u = coins.enforce(L.acct, L.req, lanes)
            dn = np.zeros(n, bool)
            dn[lanes] = u < arm.enforcement_q
            denied = dn
            L.cash = np.where(denied, L.cash - rules.combine_fee, L.cash)
    ok = ask & ~denied
    amount = np.where(ok, np.minimum(rules.payout_cap, rules.payout_share * L.bal), 0.0)
    L.bal = L.bal - amount
    L.wins = np.where(ok, 0, L.wins)
    L.req = np.where(ok, L.req + 1, L.req)
    slot_req = (k + rules.payout_lag) % (rules.payout_lag + 1)
    L.pend[:, slot_req] += amount * rules.split
    gone = dead | denied
    L = _replace_accounts(L, gone, passed, rules)
    if parts:
        p = _replace_accounts(parts[0], np.ones(len(parts[0]), bool), np.zeros(len(parts[0]), bool), rules)
        L = Lanes.concat([L, p])
    return _close_cash(L, k, rules, budget)


def _replace_accounts(L: Lanes, gone: np.ndarray, passed: np.ndarray, rules: ToyRules) -> Lanes:
    # the billing of a live evaluation (not bought or passed at this close)
    stay0 = ~gone & ~passed & (L.phase == 0)
    L.age = np.where(~gone & ~passed, L.age + 1, L.age)
    bill = stay0 & (L.age % rules.billing == 0)
    L.cash = np.where(bill, L.cash - rules.combine_fee, L.cash)
    # a pass: the funded account starts
    L.phase = np.where(passed, 1, L.phase)
    L.bal = np.where(passed | gone, 0.0, L.bal)
    L.peak = np.where(passed | gone, 0.0, L.peak)
    L.floor = np.where(passed, -float(rules.funded_mll), np.where(gone, -float(rules.mll), L.floor))
    L.age = np.where(passed | gone, 0, L.age)
    L.wins = np.where(passed | gone, 0, L.wins)
    L.phase = np.where(gone, 0, L.phase)
    L.acct = np.where(passed | gone, L.acct + 1, L.acct)
    L.req = np.where(passed | gone, 0, L.req)
    return L


def _close_cash(L: Lanes, k: int, rules: ToyRules, budget: float | None) -> Lanes:
    slot = k % (rules.payout_lag + 1)
    arr = L.pend[:, slot].copy()
    L.pend[:, slot] = 0.0
    L.cash = L.cash + arr
    L.first_pay = np.where((arr > 0) & (L.first_pay < 0), k, L.first_pay)
    if k % MONTH == 0 and 1 <= k // MONTH <= 3:
        spent = np.maximum(0.0, -L.minrel)
        ok = L.cash > TOL
        if budget is not None:
            ok &= spent <= float(budget)
        L.ahead = L.ahead + ok.astype(np.int64)
    L.minrel = np.minimum(L.minrel, L.cash)
    return L


def _session(L: Lanes, trades: Sequence[Trade], k: int, rules: ToyRules, arm: ArmSpec, budget: float | None,
             coins: CoinLanes | None, dp: bool) -> Lanes:
    L.day = np.zeros(len(L))
    L.dead = np.zeros(len(L), bool)
    L.stopped = np.zeros(len(L), bool)
    for t in trades:
        if dp:
            L = _trade_dp(L, t, rules, arm)
        else:
            _trade_mc(L, t, rules, arm, coins)
    return _close(L, k, rules, arm, budget, coins, dp)


# ------------------------------------------------------------------------------------------------ the two replays


@dataclass
class Records:
    """One start's units under its seeds (rows: the seeds' lanes)."""

    start: int
    seed_indices: tuple[int, ...]
    rel: np.ndarray
    first_pass: np.ndarray
    first_pay: np.ndarray
    ahead: np.ndarray
    arrivals: list[list[tuple[int, float]]]
    accounts: np.ndarray
    budget: float | None = None
    balance: np.ndarray | None = None       # each lane's account balance at the last close (relative to its start)
    fill_failures: np.ndarray | None = None  # accounts failed at the fill, counted apart (reported beside)


def check_costs(schedule: Schedule, rules: ToyRules, arm: ArmSpec = ArmSpec()) -> None:
    """n-2: refused when the declared daily loss limit is at or below a trade's costs (its entry and larger exit cost,
    at the arm's worse fill): such a lane could never take a trade and never fail, its day ending at every offer."""
    if rules.dll is None:
        return
    for t in schedule.trades:
        extra = float(arm.worse_ticks) * t.tvn
        if float(rules.dll) <= t.entry_cost + max(t.x_stop, t.x_flat) + 2 * extra + EPS:
            raise ValueError(f"REFUSED (n-2): the daily loss limit ${rules.dll} is at or below a trade's costs "
                             f"(session {t.session}, slot {t.entry})")


def check_window(start: int, horizon: int, block_sessions: int) -> None:
    """The block bound (CHARTER 3.6 (d)): a start is read at h only when its h sessions lie inside its block."""
    if start < 0 or horizon < 1 or start + horizon > block_sessions:
        raise ValueError(f"REFUSED (3.6 (d)): start {start} at horizon {horizon} reads past the block's last session "
                         f"({block_sessions} sessions): it is not in E_{horizon}")


def simulate(schedule: Schedule, rules: ToyRules, start: int, seed_indices: Sequence[int], horizon: int, *,
             seed: int, part: int, history: int, block_sessions: int, arm: ArmSpec = ArmSpec(),
             budget: float | None = None, guard: K.KeyGuard | None = None) -> Records:
    """The units (start, c) for c in `seed_indices`: the design's trades of sessions start .. start + horizon - 1,
    each outcome redrawn from the unit's own coin field; exactly `horizon` sessions run (closes 0 .. horizon)."""
    check_window(start, horizon, block_sessions)
    check_costs(schedule, rules, arm)
    n = len(seed_indices)
    coins = CoinLanes(seed, part, history, start, seed_indices, guard, arm.twin)
    L = fresh(n, rules)
    rel = np.zeros((n, horizon + 1))
    rel[:, 0] = L.cash
    arrivals: list[list[tuple[int, float]]] = [[] for _ in range(n)]
    for k in range(1, horizon + 1):
        before = L.pend[:, k % (rules.payout_lag + 1)].copy()
        L = _session(L, schedule.by_session.get(start + k - 1, ()), k, rules, arm, budget, coins, dp=False)
        rel[:, k] = L.cash
        for j in np.flatnonzero(before > 0):
            arrivals[j].append((k, float(before[j])))
    return Records(int(start), tuple(int(c) for c in seed_indices), rel, L.first_pass.copy(), L.first_pay.copy(),
                   L.ahead.copy(), arrivals, L.acct.copy(), budget, L.bal.copy(), L.ffail.copy())


def _state_key(L: Lanes, rules: ToyRules, budget: float | None) -> np.ndarray:
    """The state as the future reads it: the peak only while the floor still trails, the age only modulo the billing
    and only for an evaluation, the lowest rel only as whether it is still within the budget (min(minrel, x) >= -B
    depends on nothing else), and no lowest rel at all without a budget."""
    lock = np.where(L.phase == 0, np.inf if rules.combine_lock is None else rules.combine_lock, 0.0)
    peak = np.where(L.floor >= lock - 1e-12, 0.0, L.peak)
    age = np.where(L.phase == 0, L.age % rules.billing, 0)
    within = (L.minrel >= -float(budget) - 1e-9) if budget is not None else np.zeros(len(L))
    cols = [L.phase, L.bal, L.floor, peak, age, L.wins, L.cash, within, L.ahead, L.first_pass > 0]
    return np.column_stack([np.round(np.asarray(c, float), 9) for c in cols] + [np.round(L.pend, 9)])


def _merge(L: Lanes, rules: ToyRules, budget: float | None) -> Lanes:
    """Identical states joined, their probabilities added (the enforcement ordinals carry no law at a fixed q); the
    failures at the fill so far carried as the merged states' expected count (the w-weighted mean), so the program's
    expected count is exact without splitting a state by it (n-3)."""
    if len(L) <= 1:
        return L
    M = _state_key(L, rules, budget)
    _, first, inv = np.unique(M, axis=0, return_index=True, return_inverse=True)
    w = np.zeros(len(first))
    np.add.at(w, inv.ravel(), L.w)
    wf = np.zeros(len(first))
    np.add.at(wf, inv.ravel(), L.w * np.asarray(L.ffail, float))
    out = L.take(first)
    out.w = w
    out.ffail = np.where(w > 0, wf / np.where(w > 0, w, 1.0), 0.0)
    return out


def expect(schedule: Schedule, rules: ToyRules, start: int, horizon: int, *, block_sessions: int,
           arm: ArmSpec = ArmSpec(), budget: float | None = None) -> dict[str, float]:
    """The exact expectation over the coin field of one start's journey (the design note's 2.4): a forward dynamic
    program over the states, each trade's outcomes branched with the race's (or R-10's walk's) exact probabilities.
    Returns E[P_B's per-unit value] (months ahead under B over 3), the probability of a first pass by the horizon, the
    expected number of failures at the fill (n-3), and the total probability (1 within rounding) and the largest
    number of states held."""
    check_window(start, horizon, block_sessions)
    check_costs(schedule, rules, arm)
    L = fresh(1, rules)
    biggest = 1
    for k in range(1, horizon + 1):
        L = _session(L, schedule.by_session.get(start + k - 1, ()), k, rules, arm, budget, None, dp=True)
        L.day = L.dead = L.stopped = None
        L = _merge(L, rules, budget)
        biggest = max(biggest, len(L))
    tot = float(L.w.sum())
    return {"p_b": float((L.w * L.ahead).sum() / 3.0), "passed": float((L.w * (L.first_pass > 0)).sum()),
            "fill_failures": float((L.w * np.asarray(L.ffail, float)).sum()), "total": tot, "states": biggest}


# ------------------------------------------------------------------------------------------------ per-unit values


def p_b_values(rec: Records, budget: float | None) -> np.ndarray:
    """P_B's per-unit value, the months 1 to 3 ahead under B over 3 (`journey_measures.months_ahead_under`, the second
    code path; the replay's own count held equal to it), in [0, 1]."""
    from extended import journey_measures as JM

    v = np.array([JM.months_ahead_under(r, budget) for r in rec.rel], float) / 3.0
    if budget == rec.budget and not np.array_equal(v * 3.0, rec.ahead.astype(float)):
        raise RuntimeError("the replay's month count and journey_measures' disagree")
    return v


def share_ahead_values(rec: Records, k: int) -> np.ndarray:
    """1 where the unit is ahead at close k (an indicator: range [0, 1])."""
    return (rec.rel[:, int(k)] > TOL).astype(float)


def days_to_first_payout(rec: Records, window: int) -> np.ndarray:
    """Sessions to the first payout's arrival within `window`, censored at W + 1 (range [0, W + 1], M-2)."""
    f = rec.first_pay.astype(float)
    return np.where((f > 0) & (f <= window), f, float(window + 1))


__all__ = ["MONTH", "TOL", "EPS", "WALK_CHUNK", "WALK_MAX", "check_costs", "Trade", "Schedule", "ToyRules", "Lanes", "fresh", "ArmSpec", "CoinLanes",
           "Records", "check_window", "simulate", "expect", "p_b_values", "share_ahead_values",
           "days_to_first_payout"]
