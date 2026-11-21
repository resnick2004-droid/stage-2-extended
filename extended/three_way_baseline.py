"""Q-185c: the firm path's **baseline mode** -- a registered baseline (P-14, P-15, P-16) replayed over start days under
the martingale-outcome reading, with everything but each trade's outcome the vendored engine's (the lead's rulings,
2026-11-21, on H4's RC-1 and rc-4). Explicit and separate: the design mode (`extended.three_way_firm.simulate`) is
unchanged.

    from extended import three_way_baseline as TB
    rec = TB.simulate(job_blocks, job_args, facts, start, seed_indices, horizon, seed=..., part=..., history=...,
                      block_sessions=..., dates=..., outcome="race")       # outcome="vendored": the identity arm

**Ruling 1, where the outcome is replaced.** The unit's replay is U1's (`customer_slices.replay`, ruling 2): the
vendored `SharedDayDraws` over the job's blocks from the start, in replay, with the job's own draw arguments -- its
sizing (`TierSizedDraw`), its risk policy (on the path), its routing (`TradeRouter`, the strict rule at each account's
own R with `can_take`), its settlement -- and the vendored `simulate_lockstep_path`. Each account's draw is the
vendored one wrapped (`RaceOver`): every attribute and call is the vendored draw's (routing, `can_take`, `set_risk`,
the session hook, the ledger fields), and **only the P&L it returns is replaced**: from what the vendored draw reports
of the trade it handed out (`last_trade`: the block day `h`, the trade `j`, its realised risk, the R it used -- the
risk policy's `rr_used`, else the log's own R, the job's declared `log_rr`), the
trade's facts (`TradeFacts`) and the room the engine handed it, by the runner's law at that R, keyed on the unit's
coin field. `outcome="vendored"` passes the vendored P&L through: the identity, bit for bit with
`customer_slices.replay`.

**The law at the account's R**, in dollars, the position's dollars a tick `d = realised risk / stop ticks`:
- G = FV3's target at R, floor(R x stop + 1e-9) ticks (`fv3_rung_walk.target_ticks`); the costs the facts' per-tick
  ones times d: e (entry), x_t, x_s, x_f (target, stop or breakeven, flatten);
- the take at the fill (E-247): L_fill = min(stop d, room - e - max(x_s, x_f)) above `EPS`, else a floor-bound account
  fails at the fill (the room booked) and a limit-bound day ends;
- the kind at R from the facts: `t` or `s` -- the race at L = min(stop d, room - e - x_s) against G d; `f` -- R-10's walk
  to the time limit known at the fill (step `walk_step(sigma, T)`, steps `walk_steps`); `b` -- the move-aware
  sequential race (`extended.three_way_move`), its walk to the move bar's open `be_open`, then the race from there;
- P3's plant on a race, the antithetic twin, a worse fill (measure 29) as in the design mode.
Same-bar exits are admitted (`entry <= exit` on Stage 2's bar-end clock). The admission boundary is the vendored
router's (`shared_days`: refused while `open_until + gap > t`), untouched.

**Ruling 3, the facts** (`TradeFacts`, per block day and trade, from the schedule builder): the alert minute (the coin
key's moment), the fill bar's end, the stop in ticks, the tick value, the per-tick costs, the kind at every R of the
job's table, the time limit known at the fill, the volatility at the alert (bars closed at or before the alert only) and
the move bar's open `be_open` (FV3's next session open after the fill bar -- 17:00, 19:00, 08:30, 13:00 CT -- the first
recorded bar within five minutes of it: the fill time and the declared opens, no price). A trade whose kind at the R
used is `b` needs `be_open`; one without facts is refused.

**What the runner (wt/wt-three) must add** for the design mode to carry the same state: `EXIT_LAW["breakeven"] =
"move"`; on `three_way_journey.Trade` the move's steps (`move_n`) and the fields above; `Trade.__post_init__` admitting
`entry <= exit` for a same-bar exit; and its `_trade_mc` / `_trade_dp` dispatching the `move` law to
`three_way_move.move_outcomes` / `move_law`.

**Not here.** The cut data (Q-172's `search_cut`, a stub on this tree); the denial ladder (refused).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

import numpy as np

from extended import three_way_firm as TF
from extended import three_way_journey as J
from extended import three_way_keys as K
from extended import three_way_move as MV
from extended import three_way_redraw as RD

TASK = "Q-185c"
EPS = J.EPS
OUTCOMES = ("race", "vendored")
KINDS = ("t", "s", "f", "b")


@dataclass(frozen=True)
class TradeFacts:
    """One baseline trade's facts known at the fill (the schedule builder's, ruling 3). Minutes on Stage 2's bar-end
    clock (after 17:00 CT); costs in dollars a tick of the position (a contract's tick value times the cost ticks, the
    fee per contract over its ticks' dollars included)."""

    decision: int                         # the alert minute: the coin key's moment, with the block's session
    entry: int                            # the fill bar's end
    stop_ticks: int
    tick_value: float
    kinds: Mapping[float, str]            # the kind at every R of the job's table: t, s, f or b
    limit: int                            # the time limit known at the fill (the flatten bar, a news window, a max hold)
    sigma: float                          # ticks per sqrt minute, from bars closed at or before the alert
    be_open: int | None = None            # the move bar's open (FV3's next session open), None where none comes
    e_ticks: float = 0.0                  # the entry's cost, in ticks of the position
    xt_ticks: float = 0.0                 # the target exit's
    xs_ticks: float = 0.0                 # the stop's (and the breakeven's)
    xf_ticks: float = 0.0                 # the flatten's
    sub: int = 0
    underlying: str = "NQ"

    def __post_init__(self) -> None:
        if not (0 <= self.entry <= self.limit):
            raise ValueError(f"a trade fills at or before its time limit (a same-bar exit admitted): {self}")
        if self.stop_ticks <= 0 or self.tick_value <= 0 or not self.sigma > 0:
            raise ValueError("the stop, the tick value and the volatility are positive")
        bad = [k for k in self.kinds.values() if k not in KINDS]
        if bad:
            raise ValueError(f"REFUSED: exit kinds {bad} are not in {KINDS}")
        if any(k == "b" for k in self.kinds.values()) and (self.be_open is None or not self.entry < self.be_open):
            raise ValueError("a trade with a breakeven exit names its move bar's open after its fill (be_open)")
        if min(self.e_ticks, self.xt_ticks, self.xs_ticks, self.xf_ticks) < 0:
            raise ValueError("costs are non-negative")


@dataclass(frozen=True)
class _Key:
    """The coin key's stand-in for one trade (what `CoinLanes.coin` reads)."""

    moment: int
    underlying: str


def target_ticks(R: float, stop: int) -> int:
    """FV3's target in ticks at R: floor(R x stop + 1e-9) (`fv3_rung_walk.target_ticks`)."""
    return int(math.floor(float(R) * int(stop) + 1e-9))


class _Unit:
    """One start's coin field (`three_way_journey.CoinLanes`) and the trades' facts, for its lanes."""

    def __init__(self, facts: Mapping[tuple[int, int], TradeFacts], start: int, coins: Any, arm: J.ArmSpec,
                 log_rr: float | None):
        self.facts, self.start, self.coins, self.arm = facts, int(start), coins, arm
        self.log_rr = None if log_rr is None else float(log_rr)
        self.cache: dict[tuple[int, int], np.ndarray] = {}

    def key(self, h: int, j: int) -> tuple[_Key, TradeFacts]:
        f = self.facts.get((self.start + int(h), int(j)))
        if f is None:
            raise ValueError(f"REFUSED: no facts for the block day {self.start + int(h)}'s trade {j}")
        return _Key(K.moment(self.start + int(h), int(f.decision), int(f.sub)), f.underlying), f

    def uniform(self, k: _Key, kind: int, lane: int) -> float:
        u = self.cache.get((k.moment, int(kind)))
        if u is None:
            u = self.coins.coin(k, kind)[:, 0]
            self.cache[(k.moment, int(kind))] = u
        return float(u[lane])


class RaceOver:
    """A vendored per-account draw, every attribute and call its own, its returned P&L replaced (ruling 1)."""

    def __init__(self, inner: Any, unit: _Unit, lane: int, outcome: str, log: list | None):
        object.__setattr__(self, "_inner", inner)
        object.__setattr__(self, "_unit", unit)
        object.__setattr__(self, "_lane", int(lane))
        object.__setattr__(self, "_outcome", outcome)
        object.__setattr__(self, "_log", log)
        object.__setattr__(self, "_state", [0.0, 0.0, False])     # the floor's room at the start, today's net, ended

    def __getattr__(self, name: str) -> Any:
        return getattr(object.__getattribute__(self, "_inner"), name)

    def __setattr__(self, name: str, value: Any) -> None:
        setattr(self._inner, name, value)

    def begin_session(self, balance: float, floor: float) -> None:
        st = object.__getattribute__(self, "_state")
        st[0], st[1], st[2] = float(balance) - float(floor), 0.0, False
        begin = getattr(self._inner, "begin_session", None)
        if begin is not None:
            begin(balance=balance, floor=floor)

    def __call__(self, n: int, day: int, slot: int, cushion: np.ndarray, **kw: Any) -> np.ndarray:
        out = self._inner(n, day, slot, cushion, **kw)
        if self._outcome == "vendored":
            return out
        if kw:
            raise ValueError(f"REFUSED: the baseline race takes no {sorted(kw)} (need-aware or stretch exits)")
        pnl = float(np.asarray(out)[0])
        if math.isnan(pnl):
            return out
        lt = getattr(self._inner, "last_trade", None) or {}
        if lt.get("stood_aside") or not lt.get("realised_risk", lt.get("risk")):
            return out
        st = object.__getattribute__(self, "_state")
        room = float(np.asarray(cushion)[0])
        if st[2]:
            return np.array([math.nan])
        new = self._law(int(lt["historical_day"]), int(lt["trade_index"]),
                        float(lt.get("realised_risk", lt.get("risk"))), lt, room, st)
        if not math.isnan(new):
            st[1] += max(new, -room)
        return np.array([new])

    def _rr(self, lt: Mapping[str, Any]) -> float:
        """The R the vendored draw read the trade at: the risk policy's (`rr_used`), else the log's own outcome's R --
        the job's declared `log_rr` (P-16's: its fresh Combine's R, the log's single exit)."""
        r = lt.get("rr_used")
        if r is None:
            r = lt.get("rr")
        if r is None:
            r = self._unit.log_rr
        if r is None:
            raise ValueError("REFUSED: the vendored draw read the log's own outcome and the job declares no log_rr")
        return float(r)

    def _law(self, h: int, j: int, risk: float, lt: Mapping[str, Any], room: float, st: list) -> float:
        u, arm = self._unit, self._unit.arm
        key, f = u.key(h, j)
        R = self._rr(lt)
        kind = f.kinds.get(R)
        if kind is None:
            raise ValueError(f"REFUSED: the trade ({u.start + h}, {j}) carries no kind at R = {R}")
        d = risk / float(f.stop_ticks)                        # the position's dollars a tick
        extra = float(arm.worse_ticks) * d
        e, xt, xs, xf = (f.e_ticks * d + extra, f.xt_ticks * d + extra, f.xs_ticks * d + extra,
                         f.xf_ticks * d + extra)
        G = float(target_ticks(R, f.stop_ticks))
        win = G * d
        floor_room = st[0] + st[1]
        if arm.missed_q > 0 and u.uniform(key, K.MISSED, self._lane) < arm.missed_q:
            self._note(h, j, R, kind, room, "missed", math.nan)
            return math.nan
        L_fill = min(f.stop_ticks * d, room - e - max(xs, xf))
        if not L_fill > EPS:
            if floor_room <= room + EPS:
                self._note(h, j, R, kind, room, "fill_fail", -room)
                return -room
            st[2] = True
            self._note(h, j, R, kind, room, "day_end", math.nan)
            return math.nan
        L = min(f.stop_ticks * d, room - e - xs)
        if kind in ("t", "s"):
            p = L / (L + win)
            w = bool(RD.race_outcome(np.array([u.uniform(key, K.RACE, self._lane)]), np.array([p]), arm.plant_eps)[0])
            out = (-e + win - xt) if w else (-e - L - xs)
            self._note(h, j, R, kind, room, "race", out)
            return out
        T = max(1, int(f.limit) - int(f.entry))
        s = RD.walk_step(float(f.sigma), float(T), J.WALK_MAX)
        lane = self._lane
        coins = u.coins
        coins.record(key, K.WALK, [lane])

        def read(rows, first, count):
            return coins.coin(key, K.WALK, count, np.asarray([lane])[rows], first=first, record=False)

        if kind == "f":
            n = RD.walk_steps(float(f.sigma), float(T), s)
            v, k = RD.walk_run(read, 1, G, np.array([L / d]), s, int(n), J.WALK_CHUNK)
            cost = xt if int(k[0]) == 1 else xs if int(k[0]) == -1 else xf
            out = -e + float(v[0]) * d - cost                   # a flatten past the floor: the engine clips it
            self._note(h, j, R, kind, room, "walk", out)
            return out
        n_move = RD.walk_steps(float(f.sigma), float(max(1, int(f.be_open) - int(f.entry))), s)
        gross, kk = MV.move_outcomes(read, 1, G, np.array([L / d]), s, int(n_move),
                                     np.array([u.uniform(key, K.RACE, lane)]), J.WALK_CHUNK)
        kc = int(kk[0])
        cost = xt if kc == MV.TARGET else xs                  # the moved stop's exit costs the stop side's
        out = -e + float(gross[0]) * d - cost
        self._note(h, j, R, kind, room, "move", out)
        return out

    def _note(self, h, j, R, kind, room, law, out) -> None:
        log = object.__getattribute__(self, "_log")
        if log is not None:
            log.append((self._unit.start + h, j, R, kind, room, law, out))


def replay(blocks: Sequence[Any], args: Mapping[str, Any], horizon: int, *, unit: _Unit | None = None, lane: int = 0,
           outcome: str = "race", log: list | None = None) -> Any:
    """`customer_slices.replay`'s call (the vendored `SharedDayDraws` over the blocks in replay, the job's draw and
    path arguments, the vendored `simulate_lockstep_path`), each account's draw wrapped in `RaceOver`."""
    from extended import use_vendored_stage2

    use_vendored_stage2()
    from propedge.campaign.lockstep import simulate_lockstep_path
    from propedge.campaign.shared_days import SharedDayDraws

    if outcome not in OUTCOMES:
        raise ValueError(f"outcome is one of {OUTCOMES}, got {outcome!r}")
    if outcome == "race" and unit is None:
        raise ValueError("the race needs the unit's coin field and the trades' facts")
    n = int(horizon)
    sd = SharedDayDraws({0: list(blocks[:n])}, seed=args["seed"], replay=True, **args["draws"])
    kw = sd.lockstep_kwargs()
    if "flip" in kw:
        raise ValueError("REFUSED: a flip stream is not read on the baseline mode")
    cf, ff = kw["combine_draw_factory"], kw["funded_draw_factory"]
    kw["combine_draw_factory"] = lambda i, d: RaceOver(cf(i, d), unit, lane, outcome, log)
    kw["funded_draw_factory"] = lambda i, d: RaceOver(ff(i, d), unit, lane, outcome, log)
    return simulate_lockstep_path(args["draws"]["protocol"], seed=args["seed"], horizon_days=n + 1, **args["path"],
                                  **kw)


@dataclass
class BaselineRecords(J.Records):
    """`three_way_journey.Records` on the baseline mode, with the paths and the laws' logs when kept."""

    paths: tuple = ()
    logs: tuple = ()
    outcome: str = "race"


def simulate(blocks: Sequence[Any], args: Mapping[str, Any], facts: Mapping[tuple[int, int], TradeFacts], start: int,
             seed_indices: Sequence[int], horizon: int, *, seed: int, part: int, history: int, block_sessions: int,
             dates: Any = None, arm: J.ArmSpec = J.ArmSpec(), budget: float | None = None,
             guard: K.KeyGuard | None = None, outcome: str = "race", keep_paths: bool = False, log: bool = False,
             calendar: frozenset | None = None, log_rr: float | None = None) -> BaselineRecords:
    """The units (start, c), c in `seed_indices`: each U1's replay of the job's blocks from `start` for `horizon`
    sessions, its trades' outcomes redrawn on the unit's coin field (`outcome="race"`) or passed through
    (`"vendored"`, every lane then the same vendored path)."""
    J.check_window(start, horizon, block_sessions)
    TF.check_dates(dates, start, horizon, block_sessions, seed=seed, calendar=calendar)
    idx = [int(c) for c in seed_indices]
    if len(set(idx)) != len(idx):
        raise ValueError("REFUSED: a seed index repeats (two lanes would read one coin field)")
    if arm.enforcement_q > 0 or arm.reading != "martingale":
        raise ValueError("REFUSED: the baseline mode reads the martingale outcome at 0 % denial (the vendored "
                         "outcome is `outcome='vendored'`)")
    if len(blocks) < start + horizon:
        raise ValueError("the job's blocks end before the window")
    coins = J.CoinLanes(seed, part, history, start, idx, guard, arm.twin)
    unit = _Unit(facts, start, coins, arm, log_rr)
    path_kw = args["path"]
    bankroll, lag = float(path_kw["initial_bankroll"]), int(path_kw["payout_lag_days"])
    out = {k: [] for k in ("rel", "first_pass", "first_pay", "ahead", "accounts", "balance", "arrivals")}
    paths, logs, fills = [], [], []
    for j in range(len(idx)):
        lg: list = []
        p = replay(blocks[start:start + horizon], args, horizon, unit=unit, lane=j, outcome=outcome, log=lg)
        r = TF.records_of(p, bankroll=bankroll, lag=lag, horizon=horizon, budget=budget)
        for k in out:
            out[k].append(r[k])
        fills.append(sum(1 for x in lg if x[5] == "fill_fail"))
        if keep_paths:
            paths.append(p)
        if log:
            logs.append(lg)
    n = len(idx)
    return BaselineRecords(start=int(start), seed_indices=tuple(idx),
                           rel=np.asarray(out["rel"]).reshape(n, horizon + 1),
                           first_pass=np.asarray(out["first_pass"], np.int64),
                           first_pay=np.asarray(out["first_pay"], np.int64), ahead=np.asarray(out["ahead"], np.int64),
                           arrivals=out["arrivals"], accounts=np.asarray(out["accounts"], np.int64), budget=budget,
                           balance=np.asarray(out["balance"], float),
                           fill_failures=np.asarray(fills, np.int64),
                           paths=tuple(paths), logs=tuple(logs), outcome=outcome)


__all__ = ["TASK", "EPS", "OUTCOMES", "KINDS", "TradeFacts", "target_ticks", "RaceOver", "replay", "BaselineRecords",
           "simulate"]
