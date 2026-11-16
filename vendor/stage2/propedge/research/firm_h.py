"""HYPOTHETICAL (D-203): Firm H, where two parties may hedge each other. A contract-structure study, never a candidate.

Cross-account hedging is prohibited at Topstep (Prohibited Conduct 10296582, tier 1 under D-145), and that rule does
not change. Firm H is Topstep's 50K environment -- the Combine, the funded account, fees, payouts by Aeropay, the
scaling plan, all from the verified ledger -- with one change: two parties may hold opposite positions. The question
(the operator's, 2026-09-29): does dealing each trade to both parties, one long and one short, A) raise Combine pass
rates, and B) raise the number and size of payouts from funded accounts?

* **The parties.** Each has its own five-account cap (Combines and funded accounts together), its own bankroll and
  stage one's lifecycle as P-04 registered it (`im2_score.policy`), sized from its own tier and settled from MAE.
* **Paired rotation** (`SlotRouter`). The day's trades are dealt to five slots in turn; trade j goes to the same slot in
  both parties, so slot i's account in one party always holds the opposite of slot i's in the other. A slot whose
  account cannot take a trade (none live, or at its trade limit) skips it; a trade one party took and the other did
  not is unhedged, and the router keeps the day's taken slots so the pair's hedge can be measured.
* **The trades** (`mirrored_trades`). Zero-edge brackets on a driftless walk of `STEP` stop units a step: the long's
  and the short's outcomes at R = 1 and 2 are read off the same walk, with each bracket's MAE, so the two sides are
  exact mirrors at 1:1 and the same path at 2:1. Each trade costs what an MES trade at `STOP_TICKS` costs at its stop.
  Zero edge, so any difference between the arms is the contract and the routing.
* **Pairing by state** (D-204, `pair_accounts`, `_Joint`). Besides seats: `matched` pairs accounts in the same state
  first (a Combine with a Combine, a funded account building to +$2,000 with another, a harvesting one with
  another), then funded with funded; `crossed` pairs a funded account against a Combine first. Both parties then run
  in step, in two threads that meet at each day's routing. Every account still takes at most one trade a day, as
  under seats, so only the pairing differs.
* **What the pairs held** (D-204, `RecordingDraw`, `pair_rows`): every trade is recorded with the account's state,
  its balance (profit since it began) and room above its loss limit at the start of the session, and its P&L, so
  each hedged pair's composition and balances, and the dollars the hedge left open, can be measured. A hedge can
  lose on both sides: two 2:1 brackets both stopped out, or an account near its loss limit knocked out by the trade's
  adverse move before it came good (the intraday trailing drawdown, settled from MAE, D-156).
* **Pairing by balance and the room cap** (D-205). The engine hands a four-argument day hook each account's balance
  and loss-limit floor at the start of the session, so `balance_matched` and `balance_opposed` pair accounts in the
  same state by their room above the loss limit -- similar rooms together, or the most room against the least. The
  room cap (`RecordingDraw(cap_at_room=True)`) sizes each trade at no more than the account's room at that moment,
  and at least one micro, instead of the policy's full risk.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from propedge.campaign.shared_days import ROTATION, SharedDayDraws, TradeRouter
from propedge.outcomes.distribution import DayBlock

LABEL = ("HYPOTHETICAL: Firm H lets two parties hedge each other; at Topstep cross-account hedging is prohibited "
         "(10296582, tier 1). A contract-structure study, never a candidate (D-203).")
SEED = 20261203
SLOTS = 5                       # each party's five accounts (D-203)
STOP_TICKS = 60                 # an MES stop inside the sizeable stop band in every state (results/stop_band.csv)
MICRO = "MES"
STEP = 0.05                     # the walk's step in stop units; 20 steps to the stop
N_HISTORY = 2000                # synthetic days the campaigns resample
BANKROLL, HORIZON = 5_000.0, 504


LEVELS = {("l", 1): (1.0, -1.0), ("l", 2): (2.0, -1.0), ("s", 1): (-1.0, 1.0), ("s", 2): (-2.0, 1.0)}


def up_probability(edge_1to1: float, step: float = STEP) -> float:
    """D-206: the chance of an up step that plants `edge_1to1` -- the long 1:1 bracket's gross mean in R -- on the
    walk: +1 before -1 with chance p = (1 + e) / 2 is 1 / (1 + r^(1/step)) with r = (1 - q) / q, so
    q = 1 / (1 + ((1 - p) / p)^step). Zero edge gives one half. The long side has the edge, the short side the
    same edge against it; at 2:1 the same walk gives its own edge, measured, not set."""
    p = (1.0 + float(edge_1to1)) / 2.0
    if not 0.0 < p < 1.0:
        raise ValueError(f"an edge at 1:1 lies strictly between -1 and 1, got {edge_1to1}")
    return 1.0 / (1.0 + ((1.0 - p) / p) ** float(step))


def mirrored_trades(n: int, rng: np.random.Generator, *, step: float = STEP, p_up: float = 0.5, block: int = 256,
                    max_blocks: int = 100_000) -> dict[str, np.ndarray]:
    """`n` trades, each one walk read by both sides: for side in (long 'l', short 's') and R in (1, 2), the gross
    outcome in R (`r{side}{R}`: +R at the target, -1 at the stop), the exit kind (`k{side}{R}`: t or s) and the MAE
    in R up to the exit (`mae{side}{R}`). Long: target +R, stop -1; short: target -R, stop +1. `p_up` is the chance
    of an up step: one half is zero edge; above it the long side has an edge (`up_probability`, D-206). The walks
    are advanced `block` steps at a time, only those with a bracket still open."""
    x, lo, hi = np.zeros(n), np.zeros(n), np.zeros(n)
    out = {f"{k}{side}{R}": np.full(n, np.nan) for side, R in LEVELS for k in ("r", "mae")}
    kind = {f"k{side}{R}": np.full(n, "", dtype=object) for side, R in LEVELS}
    done = {key: np.zeros(n, bool) for key in LEVELS}
    eps = step / 10.0
    active = np.arange(n)
    for _ in range(max_blocks):
        if not active.size:
            return {**out, **kind}
        path = x[active, None] + np.cumsum(np.where(rng.random((active.size, block)) < p_up, step, -step), axis=1)
        run_lo = np.minimum(lo[active, None], np.minimum.accumulate(path, axis=1))
        run_hi = np.maximum(hi[active, None], np.maximum.accumulate(path, axis=1))
        rows = np.arange(active.size)
        for (side, R), (target, stop) in LEVELS.items():
            up = side == "l"
            open_ = ~done[(side, R)][active]
            at_t = (path >= target - eps) if up else (path <= target + eps)
            at_s = (path <= stop + eps) if up else (path >= stop - eps)
            first_t = np.where(at_t.any(axis=1), at_t.argmax(axis=1), block)
            first_s = np.where(at_s.any(axis=1), at_s.argmax(axis=1), block)
            first = np.minimum(first_t, first_s)
            hit = open_ & (first < block)
            if not hit.any():
                continue
            i, j = rows[hit], first[hit]
            idx = active[hit]
            won = first_t[hit] < first_s[hit]
            out[f"r{side}{R}"][idx] = np.where(won, float(R), -1.0)
            kind[f"k{side}{R}"][idx] = np.where(won, "t", "s")
            out[f"mae{side}{R}"][idx] = -run_lo[i, j] if up else run_hi[i, j]
            done[(side, R)][idx] = True
        x[active], lo[active], hi[active] = path[:, -1], run_lo[:, -1], run_hi[:, -1]
        active = active[~np.logical_and.reduce([done[key][active] for key in LEVELS])]
    raise RuntimeError(f"a walk did not resolve in {max_blocks * block} steps")


def trade_cost_r(stop_ticks: int = STOP_TICKS, micro: str = MICRO) -> tuple[float, float]:
    """(cost per trade in R, risk per contract in dollars): the round turn and the fill model's slippage for one
    contract of `micro` ending at a `stop_ticks` stop, over that stop in dollars (`propedge.execution.costs`)."""
    from propedge.execution.costs import ExitReason, trade_cost
    from propedge.execution.fills import FillModel
    from propedge.execution.instruments import load_instruments

    inst = load_instruments()[micro]
    rpc = float(stop_ticks) * float(inst.tick_value)
    cost = trade_cost(FillModel.load("assumed"), inst, contracts=1, dollars_risked=rpc, exit_reason=ExitReason.STOP)
    return float(cost.drag_fraction), rpc


def day_blocks(trades: Mapping[str, np.ndarray], side: str, per_day: int, *, cost_r: float, rpc: float
               ) -> list[DayBlock]:
    """One side's trades (`side` 'l' or 's') as day blocks of `per_day` trades, net of `cost_r`, at R = 1 and 2, with
    their MAE (a trade went at least as far against it as the loss it closed at, as the IM2 scorer's blocks)."""
    n_days = len(trades[f"r{side}1"]) // per_day
    blocks = []
    for d in range(n_days):
        sl = slice(d * per_day, (d + 1) * per_day)
        r = {float(R): trades[f"r{side}{R}"][sl] - cost_r for R in (1, 2)}
        mae = {float(R): np.maximum(trades[f"mae{side}{R}"][sl], -r[float(R)]) for R in (1, 2)}
        k = np.full(per_day, rpc)
        blocks.append(DayBlock(pnl=r[2.0] * rpc, risked=k.copy(), exit_reasons=("bracket",) * per_day,
                               risk_per_contract=k.copy(), mae=mae[2.0] * rpc, r_by_rr=r, mae_by_rr=mae,
                               markets=("ES",) * per_day))
    return blocks


class SlotRouter(TradeRouter):
    """D-203's paired rotation: trade j of a day goes to slot (trades dealt so far + j) mod `slots`, the same slot in
    both parties because both see the same days. A new account takes the lowest free slot and keeps it; an account at
    its trade limit, or an empty slot, skips the trade. `taken[day]` is the bitmask of slots that took a trade."""

    def __init__(self, table: Any, trades_by_history_day: Sequence[int], slots: int = SLOTS):
        super().__init__(table, trades_by_history_day)
        self.slots = int(slots)
        self.slot_of: dict[tuple, int] = {}
        self.taken: dict[int, int] = {}
        self.dealt: dict[int, int] = {}

    def begin_day(self, day: int, keys: Sequence[tuple], caps: Mapping[tuple, int] | None = None) -> None:
        h = self.table.historical_day(int(day))
        m = self.n_trades[h] if h >= 0 else 0
        self._day = int(day)
        live = [tuple(k) for k in keys]
        self._assigned = {k: [] for k in live}
        for k in [k for k in self.slot_of if k not in self._assigned]:
            del self.slot_of[k]
        used = set(self.slot_of.values())
        for k in live:                                   # the engine's order: earliest start first
            if k not in self.slot_of:
                free = next((s for s in range(self.slots) if s not in used), None)
                if free is not None:
                    self.slot_of[k] = free
                    used.add(free)
        by_slot = {s: k for k, s in self.slot_of.items()}
        mask = 0
        for j in range(m):
            s = (self.counter + j) % self.slots
            k = by_slot.get(s)
            if k is not None and (caps is None or caps.get(k) is None or len(self._assigned[k]) < int(caps[k])):
                self._assigned[k].append(j)
                self.routed += 1
                mask |= 1 << s
            else:
                self.skipped += 1
        self.taken[int(day)] = mask
        self.dealt[int(day)] = m
        self.counter += m


def protocol(trades_per_day: int):
    """Stage one's lifecycle legs for Firm H's parties (the policy sets every trade)."""
    from propedge.campaign.protocols import Protocol

    return Protocol(name="firm_h", combine_rr=1.0, combine_risk=1500.0, funded_rr=2.0, funded_risk=1000.0,
                    trades_per_day=int(trades_per_day), payout_path="standard", keep_balance=0.0, payout_frac=1.0,
                    max_concurrent_accounts=SLOTS, family="hypothetical", source="D-203; P-04 §3's lifecycle",
                    note=LABEL)


#: D-204: an account's state when it takes a trade -- the Combine, the funded account building to +$2,000 (one trade a
#: day) and the funded account harvesting at or above it (up to three) -- as the lifecycle policy sets it.
COMBINE, BUILD, HARVEST = 0, 1, 2
STATE_NAMES = {COMBINE: "Combine", BUILD: "funded (build)", HARVEST: "funded (harvest)"}
#: the pairing rules (D-203, D-204, D-205): seats in turn; the same state first; a funded account against a Combine
#: first; the same state first and, within it, by room above the loss limit -- similar rooms together, or the most
#: room against the least
SEAT, MATCHED, CROSSED = "seat", "matched", "crossed"
BALANCE_MATCHED, BALANCE_OPPOSED = "balance_matched", "balance_opposed"
JOINT_RULES = (MATCHED, CROSSED, BALANCE_MATCHED, BALANCE_OPPOSED)
#: a recorded trade's columns (D-204, D-205)
RECORD = ("day", "trade", "state", "balance", "room", "pnl", "risk", "policy_risk")


class RecordingDraw:
    """An account's draw that passes everything to the engine's own draw and records each trade it hands out
    (D-204): the calendar day, the day's trade index, the account's state, its balance and its room above the loss
    limit at the start of the session, the trade's settled P&L, and the risk it aimed at (before whole-micro
    rounding) beside the risk the policy set (`RECORD`); the two differ only when the room cap bound.

    `cap_at_room` (D-205): each trade risks no more than the account's room above its loss limit at that moment, but
    at least `min_risk` (one micro), so an account near its limit still trades; the policy's risk is kept for the
    rest."""

    def __init__(self, inner: Any, kind: str, sink: list, *, cap_at_room: bool = False, min_risk: float = 0.0):
        self._inner, self._kind, self._sink = inner, kind, sink
        self._cap, self._min_risk = bool(cap_at_room), float(min_risk)
        self._balance = self._room = float("nan")
        self._policy_risk = float(getattr(inner, "target_risk", float("nan")))

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    def set_risk(self, risk: float, rr: float | None = None) -> None:
        self._policy_risk = float(risk)
        self._inner.set_risk(risk, rr)

    def begin_session(self, balance: float, floor: float) -> None:
        self._balance, self._room = float(balance), float(balance) - float(floor)
        self._inner.begin_session(balance=balance, floor=floor)

    def __call__(self, n: int, day: int, slot: int, cushion: np.ndarray) -> np.ndarray:
        if self._cap:
            self._inner.target_risk = max(min(self._policy_risk, float(np.asarray(cushion)[0])), self._min_risk)
        out = self._inner(n, day, slot, cushion)
        last = getattr(self._inner, "last_trade", None)
        if last is not None and np.isfinite(out[0]):
            state = COMBINE if self._kind == "combine" else (BUILD if self._policy_risk >= 1000 else HARVEST)
            self._sink.append((self._inner.start_day + 1 + int(day), int(last["trade_index"]), state, self._balance,
                               self._room, float(out[0]), float(self._inner.target_risk), self._policy_risk))
        return out


def _state(key: tuple, caps: Mapping[tuple, int]) -> int:
    """An account's state from its key and its trade limit today: the build state allows one trade, harvest three."""
    if key[0] == "combine":
        return COMBINE
    return BUILD if int(caps.get(key, 1) or 1) <= 1 else HARVEST


def pair_accounts(a: Sequence[tuple], b: Sequence[tuple], states_a: Mapping[tuple, int],
                  states_b: Mapping[tuple, int], rule: str, rooms_a: Mapping[tuple, float] | None = None,
                  rooms_b: Mapping[tuple, float] | None = None) -> tuple[list[tuple[tuple, tuple]], list, list]:
    """(pairs, party 1's accounts left alone, party 2's) under `rule`, each account at most once. `matched`: the
    same state first, then funded with funded, then anything; `crossed`: a funded account against a Combine first,
    then anything; `balance_matched` and `balance_opposed` (D-205): as `matched`, but within each class party 1's
    accounts go in order of room above the loss limit, most first, against party 2's most first (similar rooms
    together) or least first (the most room against the least). Accounts left over trade alone (unhedged) when
    trades remain."""
    if rule not in JOINT_RULES:
        raise ValueError(f"rule must be one of {JOINT_RULES}, got {rule!r}")
    by_room = rule in (BALANCE_MATCHED, BALANCE_OPPOSED)
    if by_room and (rooms_a is None or rooms_b is None):
        raise ValueError(f"{rule} needs each account's room above its loss limit")
    left_a, left_b, pairs = list(a), list(b), []
    if by_room:
        left_a.sort(key=lambda k: -rooms_a[k])
        left_b.sort(key=lambda k: (rooms_b[k] if rule == BALANCE_OPPOSED else -rooms_b[k]))

    def take(ok) -> None:
        for x in list(left_a):
            y = next((y for y in left_b if ok(states_a[x], states_b[y])), None)
            if y is not None:
                pairs.append((x, y))
                left_a.remove(x)
                left_b.remove(y)

    funded = lambda s: s != COMBINE                                                        # noqa: E731
    if rule == CROSSED:
        take(lambda s, t: funded(s) != funded(t))
    else:
        take(lambda s, t: s == t)
        take(lambda s, t: funded(s) and funded(t))
    take(lambda s, t: True)
    return pairs, left_a, left_b


class _Joint:
    """One path's coupling of two parties (D-204): each party's day hook hands over its live accounts and trade
    limits and waits; when both have, the pairing rule deals the day's trades to both at once -- each account at most
    one trade a day, as under seats -- and each party reads its share."""

    def __init__(self, rule: str, timeout: float = 900.0):
        import threading

        self.rule = rule
        self.barrier = threading.Barrier(2, action=self._deal, timeout=timeout)
        self.sub: list = [None, None]
        self.out: list = [None, None]
        self.turn = 0

    def submit(self, party: int, keys: Sequence[tuple], caps: Mapping[tuple, int] | None, m: int,
               states: Mapping[tuple, tuple[float, float]] | None = None) -> dict:
        self.sub[party] = ([tuple(k) for k in keys], dict(caps or {}), int(m), dict(states or {}))
        self.barrier.wait()
        return self.out[party]

    def _deal(self) -> None:
        self.out = _deal(self.rule, self.sub[0], self.sub[1], self.turn)
        self.turn += 1


class _Wallet:
    """D-206: a cash pot two campaigns share (`lockstep.simulate_lockstep_path`'s `wallet`)."""

    def __init__(self, cash: float):
        self.cash = float(cash)


class _Turns:
    """One path's two parties taking turns between their day hooks (D-206), for a shared wallet: party 0 runs up to
    its hook, then party 1 up to its; when both have handed over the day's accounts, the day's trades are dealt (by a
    pairing rule, or not at all when each party routes its own) and party 0 goes on. Only one party moves at a time,
    so the shared wallet sees every flow in a fixed order and the run is repeatable."""

    def __init__(self, rule: str | None, wallet: _Wallet, timeout: float = 900.0):
        import threading

        self.rule, self.wallet, self.timeout = rule, wallet, float(timeout)
        self.cv = threading.Condition()
        self.turn = 0
        self.sub: list = [None, None]
        self.out: list = [None, None]
        self.out_day: int | None = None
        self.deal_turn = 0
        self.aborted = False

    def _wait(self, cond) -> None:
        if not self.cv.wait_for(lambda: self.aborted or cond(), timeout=self.timeout):
            raise RuntimeError("the two parties' turns timed out")
        if self.aborted:
            raise RuntimeError("the other party's run failed")

    def abort(self) -> None:
        with self.cv:
            self.aborted = True
            self.cv.notify_all()

    def enter(self, party: int) -> None:
        """A party's path starts: wait for its turn (party 1 starts once party 0 reached its first hook)."""
        with self.cv:
            self._wait(lambda: self.turn == party)

    def release(self, party: int) -> None:
        """A party's path is over: the other party goes on."""
        with self.cv:
            self.turn = 1 - party
            self.cv.notify_all()

    def hook(self, party: int, day: int, keys: Sequence[tuple], caps: Mapping[tuple, int] | None, m: int,
             states: Mapping[tuple, tuple[float, float]] | None) -> dict | None:
        with self.cv:
            self.sub[party] = ([tuple(k) for k in keys], dict(caps or {}), int(m), dict(states or {}))
            if party == 0:
                self.turn = 1
                self.cv.notify_all()
                self._wait(lambda: self.out_day == day and self.turn == 0)
            else:
                if self.rule is not None:
                    self.out = _deal(self.rule, self.sub[0], self.sub[1], self.deal_turn)
                    self.deal_turn += 1
                self.out_day = day
                self.turn = 0
                self.cv.notify_all()
                self._wait(lambda: self.turn == 1)
            return self.out[party] if self.rule is not None else None


def _deal(rule: str, sub_a: tuple, sub_b: tuple, turn: int) -> list[dict]:
    """The day's trades dealt to both parties under `rule` (`_Joint._deal`'s rule, shared with `_Turns`)."""
    (ka, ca, m, sa), (kb, cb, _, sb) = sub_a, sub_b
    rot = lambda ks: ks[turn % len(ks):] + ks[:turn % len(ks)] if ks else ks                   # noqa: E731
    la = [k for k in rot(ka) if int(ca.get(k, 1) or 1) >= 1]
    lb = [k for k in rot(kb) if int(cb.get(k, 1) or 1) >= 1]
    room = lambda st, k: (st[k][0] - st[k][1]) if k in st else 0.0                         # noqa: E731
    pairs, alone_a, alone_b = pair_accounts(la, lb, {k: _state(k, ca) for k in la}, {k: _state(k, cb) for k in lb},
                                            rule, {k: room(sa, k) for k in la}, {k: room(sb, k) for k in lb})
    out_a, out_b = {k: [] for k in ka}, {k: [] for k in kb}
    j = 0
    for x, y in pairs:
        if j < m:
            out_a[x].append(j)
            out_b[y].append(j)
            j += 1
    for x in alone_a:
        if j < m:
            out_a[x].append(j)
            j += 1
    for y in alone_b:
        if j < m:
            out_b[y].append(j)
            j += 1
    return [out_a, out_b]


class TurnRouter(TradeRouter):
    """D-206: one party's router while two parties share a wallet. Under a pairing rule the day's trades come from
    the joint deal (`_Turns`); otherwise the party's own router (`inner`: the engine's rotation or seats) deals them
    after the party's turn."""

    def __init__(self, table: Any, trades_by_history_day: Sequence[int], turns: _Turns, party: int,
                 inner: TradeRouter | None = None):
        super().__init__(table, trades_by_history_day)
        self.turns, self.party, self.inner = turns, int(party), inner
        self.taken = getattr(inner, "taken", None)

    def begin_day(self, day: int, keys: Sequence[tuple], caps: Mapping[tuple, int] | None = None,
                  states: Mapping[tuple, tuple[float, float]] | None = None) -> None:
        h = self.table.historical_day(int(day))
        m = self.n_trades[h] if h >= 0 else 0
        self._day = int(day)
        dealt = self.turns.hook(self.party, day, keys, caps, m, states)
        if self.inner is not None:
            self.inner.begin_day(day, keys, caps)
            self._assigned = {tuple(k): list(v) for k, v in self.inner._assigned.items()}
        else:
            self._assigned = {tuple(k): list(v) for k, v in (dealt or {}).items()}
        self.routed += sum(len(v) for v in self._assigned.values())


class PairRouter(TradeRouter):
    """One party's router under a joint pairing rule (`_Joint`)."""

    def __init__(self, table: Any, trades_by_history_day: Sequence[int], joint: _Joint, party: int):
        super().__init__(table, trades_by_history_day)
        self.joint, self.party = joint, int(party)

    def begin_day(self, day: int, keys: Sequence[tuple], caps: Mapping[tuple, int] | None = None,
                  states: Mapping[tuple, tuple[float, float]] | None = None) -> None:
        """The engine passes `states`, each account's balance and floor at the start of the session (D-205)."""
        h = self.table.historical_day(int(day))
        m = self.n_trades[h] if h >= 0 else 0
        self._day = int(day)
        dealt = self.joint.submit(self.party, keys, caps, m, states)
        self._assigned = {tuple(k): list(v) for k, v in dealt.items()}
        self.routed += sum(len(v) for v in self._assigned.values())


@dataclass
class PartyRun:
    """One party's campaign, reduced to what the comparison needs: per path its measures (`party_measures`) and
    daily cash; under seats the slots that took a trade each day; and, when recorded, each path's trades as rows
    (calendar day, trade index, state, balance and room at the session's start, settled P&L)."""

    measures: list[dict[str, Any]]
    cash: list[np.ndarray]
    initial: float
    taken: list[dict[int, int]] | None = None
    trades: list[np.ndarray] | None = None


def run_party(blocks: Sequence[DayBlock], *, seed: int, paired: bool | None = None, router: Any = None,
              record: bool = False, cap_at_room: bool = False, min_risk: float = 0.0, n_paths: int,
              horizon_days: int = HORIZON, bankroll: float = BANKROLL, wallet_for_path: Any = None) -> PartyRun:
    """One party's campaign. The router: the engine's own rotation (None), `SEAT` (`SlotRouter`; `paired=True` is
    the same), or `f(table, trades_by_history_day, path_index) -> router`. `record` keeps every trade
    (`RecordingDraw`); `cap_at_room` sizes each trade at no more than the account's room above its loss limit and
    at least `min_risk` (D-205), which needs `record`. Two parties run with the same `seed` see the same days on
    every path."""
    if cap_at_room and not record:
        raise ValueError("the room cap is applied by the recording draw: pass record=True")
    from propedge.campaign.lockstep import simulate_lockstep_campaign
    from propedge.campaign.payout_method import rules_for_method
    from propedge.campaign.sizing import CURRENT_TIER, DEFAULT_HEADROOM_FRAC, SizingRule
    from propedge.research import im2_score as sc

    if paired:
        router = SEAT
    busiest = max(len(b) for b in blocks)
    proto = protocol(busiest)
    sizing = SizingRule.from_ledger(CURRENT_TIER, headroom_frac=DEFAULT_HEADROOM_FRAC)
    rules = rules_for_method("aeropay")
    routers: list = []
    sinks: list[list] = []

    def draws(s):
        sd = SharedDayDraws({0: list(blocks)}, protocol=proto, seed=s, mode=ROTATION, sizing=sizing,
                            settlement="mae", markets=1)
        n_trades = [len(b) for b in blocks]
        if router == SEAT:
            sd.router = SlotRouter(sd.table, n_trades)
        elif callable(router):
            sd.router = router(sd.table, n_trades, len(routers))
        routers.append(sd.router)
        kw = sd.lockstep_kwargs()
        if record:
            if sinks and isinstance(sinks[-1], list):          # the last path is done: keep its trades compactly
                sinks[-1] = np.asarray(sinks[-1], float).reshape(-1, len(RECORD))
            sink: list = []
            sinks.append(sink)
            opts = dict(cap_at_room=cap_at_room, min_risk=min_risk)
            kw["combine_draw_factory"] = lambda i, d: RecordingDraw(sd.draw_for("combine", i, d), "combine", sink,
                                                                    **opts)
            kw["funded_draw_factory"] = lambda i, d: RecordingDraw(sd.draw_for("funded", i, d), "funded", sink,
                                                                   **opts)
        return kw["combine_draw_factory"], kw["funded_draw_factory"], kw["day_hook"]

    _, paths = simulate_lockstep_campaign(
        proto, edge=0.0, seed=seed, rules=rules, initial_bankroll=bankroll,
        horizon_days=horizon_days, n_paths=n_paths, payout_method="aeropay", max_concurrent_accounts=SLOTS,
        max_concurrent_combines=SLOTS, max_total_accounts=SLOTS, require_verified_cap=False, conduct=None,
        risk_policy=sc.policy(), draw_factories_for_path=draws, wallet_for_path=wallet_for_path)
    return PartyRun(measures=[party_measures(p, float(rules.subscription)) for p in paths],
                    cash=[np.asarray(p.path.cash_series, float) for p in paths], initial=float(bankroll),
                    taken=[dict(r.taken) for r in routers] if router == SEAT else None,
                    trades=[np.asarray(s, float).reshape(-1, len(RECORD)) for s in sinks] if record else None)


def run_pair(blocks_1: Sequence[DayBlock], blocks_2: Sequence[DayBlock], *, seed: int, rule: str | None,
             n_paths: int, cap_at_room: bool = False, min_risk: float = 0.0, horizon_days: int = HORIZON,
             bankroll: float = BANKROLL, pooled: bool = False, seed_2: int | None = None
             ) -> tuple[PartyRun, PartyRun]:
    """Two parties under a pairing rule, both recorded. `SEAT` runs them one after the other (the seats need nothing
    from the other party); the joint rules (`JOINT_RULES`) run them in two threads that meet at every day's routing
    (`_Joint`). `cap_at_room` and `min_risk` as `run_party`. `seed_2`: party 2's days, when not party 1's.

    `pooled` (D-206): the two parties share one wallet of twice `bankroll` for the whole run -- every fee comes out of
    it and every payout goes into it -- and take turns between their day hooks (`_Turns`); `rule` may then also be
    None (each party its own rotation) or `SEAT`. Both parties' paths then report the shared cash; party 2 acts last
    each day, so its cash series is the pair's."""
    import threading

    kw = dict(record=True, cap_at_room=cap_at_room, min_risk=min_risk, n_paths=n_paths, horizon_days=horizon_days)
    seeds = (seed, seed if seed_2 is None else seed_2)
    if not pooled:
        if rule == SEAT:
            return (run_party(blocks_1, seed=seeds[0], router=SEAT, bankroll=bankroll, **kw),
                    run_party(blocks_2, seed=seeds[1], router=SEAT, bankroll=bankroll, **kw))
        if rule not in JOINT_RULES:
            raise ValueError(f"an unpooled pair needs {SEAT!r} or one of {JOINT_RULES}, got {rule!r}")
    joints: dict[int, Any] = {}
    lock = threading.Lock()

    def joint(k: int) -> Any:
        with lock:
            if k not in joints:
                joints[k] = _Turns(None if rule in (None, SEAT) else rule, _Wallet(2 * bankroll)) if pooled \
                    else _Joint(rule)
            return joints[k]

    def router_for(party: int):
        def make(t, n, k):
            if not pooled:
                return PairRouter(t, n, joint(k), party)
            if k > 0:
                joint(k - 1).release(party)              # the last path is over: the other party goes on
            joint(k).enter(party)
            inner = SlotRouter(t, n) if rule == SEAT else (TradeRouter(t, n) if rule is None else None)
            return TurnRouter(t, n, joint(k), party, inner)
        return make

    out: list = [None, None]
    errors: list = []

    def go(party: int, blocks: Sequence[DayBlock]) -> None:
        try:
            out[party] = run_party(blocks, seed=seeds[party], router=router_for(party),
                                   bankroll=2 * bankroll if pooled else bankroll,
                                   wallet_for_path=(lambda k: joint(k).wallet) if pooled else None, **kw)
        except BaseException as exc:                     # noqa: BLE001 -- raised again below, after the other stops
            errors.append(exc)
            with lock:
                for j in joints.values():
                    if isinstance(j, _Joint):
                        j.barrier.abort()
                    else:
                        j.abort()
        finally:
            if pooled:
                with lock:
                    last = max(joints) if joints else None
                if last is not None:
                    joint(last).release(party)

    threads = [threading.Thread(target=go, args=(i, b)) for i, b in enumerate((blocks_1, blocks_2))]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    if errors:
        raise errors[0]
    return out[0], out[1]


def party_measures(p: Any, subscription: float) -> dict[str, float]:
    """One party's path: the Combine side (A) and the funded side (B), and its cash. Days to pass are a passed
    Combine's own trading days (`CombineRecord.days`; its `pass_day` is on the account's clock); the first payout is
    on the campaign's clock (`CampaignPath.days_to_first_payout`)."""
    combines, funded, path = p.combines, p.funded, p.path
    resolved = [c for c in combines if c.resolved_on is not None]
    passed = [c for c in resolved if c.passed]
    pays = [x for f in funded for x in f.payout_cash]
    first = path.days_to_first_payout
    combine_fees = float(sum(c.subscriptions_paid for c in combines) * subscription)
    return {"combines_bought": len(combines), "combines_resolved": len(resolved), "combines_passed": len(passed),
            "combine_fees": combine_fees, "combine_days": float(sum(c.days for c in resolved)),
            "days_to_pass": float(np.median([c.days for c in passed])) if passed else np.nan,
            "funded_accounts": len(funded), "payouts": len(pays), "payout_cash": float(sum(pays)),
            "funded_closed": sum(bool(f.closed) for f in funded),
            "funded_ever_paid": sum(f.n_payouts > 0 for f in funded),
            "first_payout_day": float(first) if first is not None else np.nan,
            "payouts_credited": float(path.total_payouts),         # payouts that reached the cash by the horizon
            "total_fees": float(path.total_fees), "net_cash": float(path.final_cash - path.initial_bankroll),
            "ruined": bool(path.ruined), "max_drawdown": float(path.max_drawdown),
            "growth": _growth(float(path.final_cash), float(path.initial_bankroll), len(path.cash_series))}


def _growth(final: float, initial: float, days: int) -> float:
    from propedge.campaign.irr import TRADING_DAYS_PER_YEAR

    if final <= 0:
        return float("-inf")
    return float(np.log(final / initial) / (days / TRADING_DAYS_PER_YEAR))


def share_hedged(a: PartyRun, b: PartyRun) -> float:
    """Of the trades either party took under paired rotation, the share both took (the slot's two accounts held
    opposite positions); NaN unless both ran paired."""
    if a.taken is None or b.taken is None:
        return float("nan")
    both = either = 0
    for x, y in zip(a.taken, b.taken):
        for day in set(x) | set(y):
            m, n = x.get(day, 0), y.get(day, 0)
            both += bin(m & n).count("1")
            either += bin(m | n).count("1")
    return both / either if either else float("nan")


def hedged_trades(a: PartyRun, b: PartyRun) -> tuple[dict[str, np.ndarray], int]:
    """({column + side: values}, one value per hedged trade -- both parties took the day's trade j on the same path
    -- for each of `RECORD`'s columns after the day and trade index, side "1" and "2"; the number of trades only one
    party took). Needs both parties recorded."""
    rows, alone = [], 0
    for x, y in zip(a.trades or [], b.trades or []):
        kx, ky = x[:, 0] * 64 + x[:, 1], y[:, 0] * 64 + y[:, 1]
        _, ix, iy = np.intersect1d(kx, ky, return_indices=True)
        rows.append(np.column_stack([x[ix, 2:], y[iy, 2:]]))
        alone += len(x) + len(y) - 2 * len(ix)
    cols = RECORD[2:]
    h = np.vstack(rows) if rows else np.zeros((0, 2 * len(cols)))
    out = {f"{c}{side}": h[:, i + k * len(cols)] for k, side in enumerate("12") for i, c in enumerate(cols)}
    return out, alone


def pair_rows(arm: str, a: PartyRun, b: PartyRun) -> list[dict[str, Any]]:
    """D-204: what the hedged pairs held, all together and by composition (Combine vs Combine, Combine vs funded,
    funded vs funded): each side's balance and room above its loss limit at the start of the session (a balance is
    the account's profit since it began), the pair's net P&L per trade and the dollars the hedge left open, how often
    both sides lost and how often one of them had less room than its policy's risk, and in mixed pairs how often the
    funded side won. D-205: the share of trades sized below the policy's risk (the room cap)."""
    h, alone = hedged_trades(a, b)
    sa, ba, ra, pa, ka, qa = (h[f"{c}1"] for c in RECORD[2:])
    sb, bb, rb, pb, kb, qb = (h[f"{c}2"] for c in RECORD[2:])
    fa, fb = sa != COMBINE, sb != COMBINE
    both_lost = (pa < 0) & (pb < 0)
    short_room = (ra < qa - 1e-6) | (rb < qb - 1e-6)            # a side's room below the risk its policy wanted
    comps = {"all": np.ones(len(sa), bool), "Combine vs Combine": ~fa & ~fb, "Combine vs funded": fa != fb,
             "funded vs funded": fa & fb}
    out = []
    for name, sel in comps.items():
        n = int(sel.sum())
        comb_bal = np.concatenate([ba[sel & ~fa], bb[sel & ~fb]])
        comb_room = np.concatenate([ra[sel & ~fa], rb[sel & ~fb]])
        fund_bal = np.concatenate([ba[sel & fa], bb[sel & fb]])
        fund_room = np.concatenate([ra[sel & fa], rb[sel & fb]])
        net = pa[sel] + pb[sel]
        mixed = sel & (fa != fb)
        f_pnl = np.where(fa, pa, pb)[mixed]
        c_pnl = np.where(fa, pb, pa)[mixed]
        mean = lambda v: float(v.mean()) if len(v) else np.nan                             # noqa: E731
        total = len(sa)
        out.append({"arm": arm, "section": "hedged pairs", "scope": name, "hedged_trades": n,
                    "share_of_hedged_trades": n / total if total else np.nan,
                    "share_trades_hedged": total / (total + alone) if name == "all" and total else np.nan,
                    "combine_balance_mean": mean(comb_bal), "combine_room_mean": mean(comb_room),
                    "funded_balance_mean": mean(fund_bal), "funded_room_mean": mean(fund_room),
                    "pair_net_pnl_mean": mean(net), "pair_open_dollars_mean": mean(np.abs(net)),
                    # both sides lost: 2:1 brackets both stopped, or an account near its loss limit knocked out by the
                    # trade's adverse move before the trade came good (D-156's settlement)
                    "share_both_sides_lost": float(both_lost[sel].mean()) if n else np.nan,
                    "share_both_lost_with_a_side_short_of_room": float(short_room[sel & both_lost].mean())
                    if (sel & both_lost).any() else np.nan,
                    "share_sides_sized_below_policy": float(np.concatenate([ka[sel] < qa[sel] - 1e-6,
                                                                           kb[sel] < qb[sel] - 1e-6]).mean())
                    if n else np.nan,
                    "funded_side_win_share": float((f_pnl > 0).mean()) if len(f_pnl) else np.nan,
                    "funded_side_pnl_mean": mean(f_pnl), "combine_side_pnl_mean": mean(c_pnl),
                    "funded_same_state_share": float((sa[sel & fa & fb] == sb[sel & fa & fb]).mean())
                    if (sel & fa & fb).any() else np.nan})
    return out


def arm_rows(arm: str, a: PartyRun, b: PartyRun, *, hedged: bool, pooled: bool = False) -> list[dict[str, Any]]:
    """One row per scope (party 1, party 2, the pair) for one arm; the pair's figures are sums of its parties'.
    `hedged`: the two parties saw the same days on opposite sides, so the share of trades hedged is reported (from
    the recorded trades when both were recorded, else from the seats). `pooled` (D-206): the parties shared one
    wallet, so the pair's cash is party 2's series (it acts last each day) from the shared starting cash, and each
    party's own money columns are left empty -- its cash is the pair's."""
    rows_a, rows_b = a.measures, b.measures
    pair = []
    for k, (x, y) in enumerate(zip(rows_a, rows_b)):
        s = {key: x[key] + y[key] for key in ("combines_bought", "combines_resolved", "combines_passed",
                                               "combine_fees", "combine_days", "funded_accounts", "payouts",
                                               "payout_cash", "funded_closed", "funded_ever_paid", "total_fees",
                                               "net_cash")}
        n = min(len(a.cash[k]), len(b.cash[k]))
        cash = b.cash[k][:n].copy() if pooled else a.cash[k][:n] + b.cash[k][:n]
        start = b.initial if pooled else a.initial + b.initial
        if pooled:
            s["net_cash"] = float(cash[-1] - start)
        peak = np.maximum.accumulate(cash)
        s.update({"days_to_pass": np.nanmedian([x["days_to_pass"], y["days_to_pass"]])
                  if np.isfinite([x["days_to_pass"], y["days_to_pass"]]).any() else np.nan,
                  "first_payout_day": np.nanmin([x["first_payout_day"], y["first_payout_day"]])
                  if np.isfinite([x["first_payout_day"], y["first_payout_day"]]).any() else np.nan,
                  "ruined": bool(x["ruined"] and y["ruined"]),
                  "max_drawdown": float(max((peak - cash).max(), 0.0)) if len(cash) else 0.0,
                  "growth": _growth(float(cash[-1]), start, len(cash))})
        pair.append(s)
    hedge = float("nan")
    if hedged:
        if a.trades is not None and b.trades is not None:
            h, alone = hedged_trades(a, b)                  # of the trades either party took, the share both took
            both = len(h["state1"])
            hedge = both / (both + alone) if both + alone else float("nan")
        else:
            hedge = share_hedged(a, b)

    def sized_down(run: PartyRun) -> float:
        """D-205: the share of the party's trades sized below its policy's risk (the room cap); NaN unrecorded."""
        if run.trades is None:
            return float("nan")
        t = np.vstack(run.trades) if run.trades else np.zeros((0, len(RECORD)))
        return float((t[:, 6] < t[:, 7] - 1e-6).mean()) if len(t) else float("nan")

    down_a, down_b = sized_down(a), sized_down(b)
    down = {"party 1 (long)": down_a, "party 2 (short)": down_b,
            "pair": float(np.nanmean([down_a, down_b])) if np.isfinite([down_a, down_b]).any() else np.nan}
    out = []
    for scope, rows in (("party 1 (long)", rows_a), ("party 2 (short)", rows_b), ("pair", pair)):
        df = pd.DataFrame(rows)
        resolved = df["combines_resolved"].sum()
        funded_n = df["funded_accounts"].sum()
        out.append({
            "arm": arm, "section": "accounts", "scope": scope, "paths": len(df),
            # A) the Combine side
            "combines_bought_mean": float(df["combines_bought"].mean()),
            "combine_days_mean": float(df["combine_days"].sum() / resolved) if resolved else np.nan,
            "combine_pass_rate": float(df["combines_passed"].sum() / resolved) if resolved else np.nan,
            "combine_passes_mean": float(df["combines_passed"].mean()),
            "passes_per_100_usd_combine_fees": float(100 * df["combines_passed"].sum() / df["combine_fees"].sum())
            if df["combine_fees"].sum() else np.nan,
            "median_days_to_pass": float(np.nanmedian(df["days_to_pass"])) if df["days_to_pass"].notna().any()
            else np.nan,
            "share_paths_no_pass": float((df["combines_passed"] == 0).mean()),
            # B) the funded side
            "funded_accounts_mean": float(df["funded_accounts"].mean()),
            "payouts_mean": float(df["payouts"].mean()),
            "payouts_per_funded_account": float(df["payouts"].sum() / df["funded_accounts"].sum())
            if df["funded_accounts"].sum() else np.nan,
            "mean_payout_size": float(df["payout_cash"].sum() / df["payouts"].sum()) if df["payouts"].sum() else np.nan,
            "payout_cash_mean": float(df["payout_cash"].mean()),
            "median_days_to_first_payout": float(np.nanmedian(df["first_payout_day"]))
            if df["first_payout_day"].notna().any() else np.nan,
            "share_paths_no_payout": float((df["payouts"] == 0).mean()),
            "share_funded_ever_paid": float(df["funded_ever_paid"].sum() / funded_n) if funded_n else np.nan,
            "share_funded_closed": float(df["funded_closed"].sum() / funded_n) if funded_n else np.nan,
            # money
            "fees_mean": float(df["total_fees"].mean()),
            "net_cash_mean": float(df["net_cash"].mean()), "net_cash_median": float(df["net_cash"].median()),
            "net_cash_p10": float(df["net_cash"].quantile(0.10)), "net_cash_sd": float(df["net_cash"].std(ddof=1)),
            "share_losing_money": float((df["net_cash"] < 0).mean()),
            "ruin": float(df["ruined"].mean()), "max_drawdown_mean": float(df["max_drawdown"].mean()),
            "median_log_growth": float(np.median(df["growth"])) if "growth" in df else np.nan,
            "net_cash_correlation": float(np.corrcoef([r["net_cash"] for r in rows_a],
                                                      [r["net_cash"] for r in rows_b])[0, 1])
            if scope == "pair" else np.nan,
            "share_trades_hedged": hedge if scope == "pair" else np.nan,
            "share_trades_sized_down": down[scope],
        })
    if pooled:                                           # D-206: one wallet, so money is the pair's alone
        money = ("fees_mean", "net_cash_mean", "net_cash_median", "net_cash_p10", "net_cash_sd", "share_losing_money",
                 "ruin", "max_drawdown_mean", "median_log_growth")
        for row in out:
            if row["scope"] != "pair":
                row.update({key: np.nan for key in money})
            row["net_cash_correlation"] = np.nan
            row["pooled"] = True
    return out


__all__ = ["LABEL", "SEED", "SLOTS", "STOP_TICKS", "N_HISTORY", "COMBINE", "BUILD", "HARVEST", "SEAT", "MATCHED",
           "CROSSED", "BALANCE_MATCHED", "BALANCE_OPPOSED", "JOINT_RULES", "RECORD", "up_probability",
           "mirrored_trades", "trade_cost_r", "day_blocks", "SlotRouter", "RecordingDraw", "pair_accounts",
           "PairRouter", "TurnRouter", "PartyRun", "protocol", "run_party", "run_pair", "party_measures",
           "share_hedged", "hedged_trades", "pair_rows", "arm_rows"]
