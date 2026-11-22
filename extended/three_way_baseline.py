"""Q-185c: the firm path's **baseline mode** -- a registered baseline (P-14, P-15, P-16) replayed over start days under
the martingale-outcome reading, everything but each trade's outcome the vendored engine's (the lead's rulings of
2026-11-21 on H4's RC-1 and rc-4, and on BUILD_FIRMPATH_c2). Explicit and separate: the design mode
(`extended.three_way_firm.simulate`) is unchanged.

    from extended import three_way_baseline as TB
    rec = TB.simulate(job_blocks, job_args, facts, start, seed_indices, horizon, seed=..., part=..., history=...,
                      block_sessions=..., dates=..., outcome="race")   # "vendored": the identity; "as_walked": beside

**Where the outcome is replaced (ruling 1).** A unit is U1's start replay (`customer_slices.replay`'s call, ruling 2):
the vendored `SharedDayDraws` over the job's blocks in replay with the job's draw arguments -- its sizing
(`TierSizedDraw`), its risk policy, its routing (`TradeRouter`: the strict rule at each account's own R, `can_take`),
its settlement -- and the vendored `simulate_lockstep_path`. Each account's draw is the vendored one wrapped
(`RaceOver`): every attribute and call is the vendored draw's, called with the engine's own keywords (a need-aware or
consistency-cap exit's `need`, so its state is the engine's), and **only the P&L it returns is replaced**.

**The trade the engine hands out**, from the vendored draw's report (`last_trade`): its block day and index, its
realised risk, its contracts, **its fee at those contracts** (`fee`, D-324: as many minis as fit, the rest in micros;
C2-2) and **the R it was read at, `rr`: the state's R** (C2-1, C2-6). Never `rr_used`: on a need-aware exit
`sizing._need_exit` picks it from the trade's historical net outcomes (look-ahead). A trade without an R is refused (no
fallback; the registered tables' leaves without an R are abandon leaves, which take no trade). Its facts
(`TradeFacts`, the schedule builder's) are checked against it: the stop's dollars a micro against the draw's
`risk_per_contract`, the fill against the block's `entry_t`, the alert at or before the fill (C2-8); a mismatch is
refused. Two facts at one coin moment are refused (C2-9).

**The law at R**, in dollars, `d` = realised risk / stop ticks the position's dollars a tick:
- the costs: the entry e = its spread ticks x d + the fee; the exits' ticks x d by kind (`xt`, `xs` for a stop or a
  breakeven, `xf` for a flatten); a worse fill's ticks on each (measure 29);
- the target: FV3's at R, floor(R x stop + 1e-9) ticks -- **with a need** (a need-aware exit, or the consistency cap at
  its cap level: the engine's `need`) the `profit_level` race's as-placed target, min(G, (need + e + x_t) / d), the
  need booked as the engine books it (a win nets exactly the need; m-3);
- the take at the fill (E-247): L_fill = min(stop d, room - e - max(x_s, x_f)) above `EPS`, else a floor-bound
  account fails at the fill (the room booked) and a limit-bound day ends -- no later slot that session;
- **every trade whose move bar comes before its limit** (whatever its historical kind; C2-4): the time-limited move
  law (`extended.three_way_move`), phase 1's step from the time to the move bar (C2-5), phase 2 to the limit (N-3);
- otherwise by the historical kind at R: `t` or `s` the race at L = min(stop d, room - e - x_s) against G; `f` R-10's
  walk to the limit known at the fill (`walk_step`, `walk_steps`); P3's plant on the race only (N-7).
Every walk's steps are at most `WALK_MAX` by the step rule, and refused otherwise (C2-10). Same-bar exits are admitted;
the admission boundary is the vendored router's, untouched.

**The ledger and the draw's statistics (C2-7).** On a replaced trade the report's historical `u` and `mae` are set to
None (not applicable) and the race's own fields added: `race_law`, `race_kind`, `race_R`, `race_u` (the booked P&L
over the risk), `race_need` (whether it closed at the need). A trade the race leaves untaken (a missed signal, a day
ended) is taken back out of the draw's statistics; its need exits count the race's. `extended.firm_reading`'s trade
check refuses a historical outcome on a race-arm row.

**The facts (ruling 3)** per block day and trade: the alert minute (the coin key's moment), the fill bar's end, the
stop, the tick value, the costs' ticks and the fee a contract (used only where the draw reports no fee), the kind at
every R (the dispatch of trades without a move, and FV3's historical `b` share beside), the time limit known at the
fill, **the volatility at the alert -- from bars closed at or before it: bar end index <= the alert, open stamp <= the
alert - 1** (N-6; `alert_sigma`), and **`be_open`, the move bar's END index on Stage 2's bar-end clock: s + 1, s FV3's
next session open (17:00, 19:00, 08:30, 13:00 CT) after the fill bar** (N-1). A missing bar is voided only by Q-197's
pinned calendar (`extended/search_calendar.py`), never by data; the vendored move bar (`be_vendored`, the first
recorded bar within five minutes) is counted beside where it differs from s + 1. `be_open` at or after the limit: no
move (C2-10).

**Beside every reading** (`BaselineRecords`): per lane the trades given the move law, the `b` exits it redrew, FV3's
historical `b` exits among the same trades, and the trades whose vendored move bar differs from s + 1.

**What the runner (wt/wt-three) must add** for the design mode: `EXIT_LAW["breakeven"] = "move"` read for every trade
with a move bar before its limit; on `three_way_journey.Trade` `be_open` (the end index), the volatility at the alert
and the time limit; `Trade.__post_init__` admitting `entry <= exit`; `_trade_mc` / `_trade_dp` dispatching to
`three_way_move.move_outcomes` / `move_law`; a need-aware exit as the `profit_level` race at min(G, need).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np

from extended import three_way_firm as TF
from extended import three_way_journey as J
from extended import three_way_keys as K
from extended import three_way_move as MV
from extended import three_way_redraw as RD

TASK = "Q-185c"
EPS = J.EPS
OUTCOMES = ("race", "vendored", "as_walked")
KINDS = ("t", "s", "f", "b")


@dataclass(frozen=True)
class TradeFacts:
    """One baseline trade's facts known at the fill (the schedule builder's, ruling 3). Minutes on Stage 2's bar-end
    clock (after 17:00 CT)."""

    decision: int                         # the alert minute: the coin key's moment, with the block's session
    entry: int                            # the fill bar's end
    stop_ticks: int
    tick_value: float                     # a contract's (a micro's: the sizing's unit)
    kinds: Mapping[float, str]            # the historical kind at every R of the job's table: t, s, f or b
    limit: int                            # the time limit known at the fill (the flatten bar, a news window, a max hold)
    sigma: float                          # ticks per sqrt minute, from bars closed at or before the alert (N-6)
    be_open: int | None = None            # the move bar's END index: s + 1 (N-1); None, or >= limit: no move
    be_vendored: int | None = None        # the vendored walk's move bar (first recorded within five minutes), beside
    e_ticks: float = 0.0                  # the entry's spread, in ticks
    xt_ticks: float = 0.0                 # the target exit's ticks
    xs_ticks: float = 0.0                 # a stop's and a breakeven's
    xf_ticks: float = 0.0                 # a flatten's
    fee_per_contract: float | None = None  # the round turn a contract, only where the draw reports no fee
    walked: Mapping[float, float] | None = None   # the historical gross ticks at every R (the as-walked arm, beside)
    sub: int = 0
    underlying: str = "NQ"

    def __post_init__(self) -> None:
        if not (0 <= self.decision <= self.entry <= self.limit):
            raise ValueError(f"the alert, the fill and the limit are in order (a same-bar fill admitted): {self}")
        if self.stop_ticks <= 0 or self.tick_value <= 0 or not self.sigma > 0:
            raise ValueError("the stop, the tick value and the volatility are positive")
        bad = [k for k in self.kinds.values() if k not in KINDS]
        if bad:
            raise ValueError(f"REFUSED: exit kinds {bad} are not in {KINDS}")
        if self.be_open is not None and not self.entry < self.be_open:
            raise ValueError("the move bar comes after the fill bar")
        if any(k == "b" for k in self.kinds.values()) and not self.has_move:
            raise ValueError("a historical breakeven exit has a move bar before its limit")
        if min(self.e_ticks, self.xt_ticks, self.xs_ticks, self.xf_ticks) < 0 or (
                self.fee_per_contract is not None and self.fee_per_contract < 0):
            raise ValueError("costs are non-negative")

    @property
    def has_move(self) -> bool:
        """A move bar before the limit (C2-10: one at or after the limit is no move)."""
        return self.be_open is not None and self.entry < self.be_open < self.limit


@dataclass(frozen=True)
class _Key:
    """The coin key's stand-in for one trade (what `CoinLanes.coin` reads)."""

    moment: int
    underlying: str


def target_ticks(R: float, stop: int) -> int:
    """FV3's target in ticks at R: floor(R x stop + 1e-9) (`fv3_rung_walk.target_ticks`)."""
    return int(math.floor(float(R) * int(stop) + 1e-9))


def alert_sigma(bar_end: Sequence[int], closes: Sequence[float], decision: int, lookback: int, tick: float) -> float:
    """N-6: the volatility at the alert, ticks per sqrt minute -- the root mean square of the one-minute close changes
    over the bars whose END index lies in (decision - lookback, decision]: bars closed at or before the alert, nothing
    after it read. Refused with fewer than two such bars."""
    e = np.asarray(bar_end, int)
    c = np.asarray(closes, float)
    keep = (e <= int(decision)) & (e > int(decision) - int(lookback))
    ee, cc = e[keep], c[keep]
    if ee.size < 2:
        raise ValueError("the volatility at the alert needs two bars closed at or before it")
    order = np.argsort(ee)
    ee, cc = ee[order], cc[order]
    dt = np.diff(ee).astype(float)
    dx = np.diff(cc) / float(tick)
    return float(math.sqrt(float(np.sum(dx * dx)) / float(np.sum(dt))))


class _Unit:
    """One start's coin field (`three_way_journey.CoinLanes`), the trades' facts and the job's blocks, for its lanes."""

    def __init__(self, facts: Mapping[tuple[int, int], TradeFacts], blocks: Sequence[Any], start: int, coins: Any,
                 arm: J.ArmSpec):
        self.facts, self.blocks, self.start, self.coins, self.arm = facts, blocks, int(start), coins, arm
        self.cache: dict[tuple[int, int], np.ndarray] = {}
        seen: dict[int, tuple[int, int]] = {}
        for (i, j), f in facts.items():                  # C2-9: two trades at one moment would read one uniform
            m = K.moment(int(i), int(f.decision), int(f.sub))
            if m in seen:
                raise ValueError(f"REFUSED (C2-9): the trades {seen[m]} and {(i, j)} share the coin moment {m}")
            seen[m] = (int(i), int(j))

    def key(self, h: int, j: int, lt: Mapping[str, Any]) -> tuple[_Key, TradeFacts]:
        i = self.start + int(h)
        f = self.facts.get((i, int(j)))
        if f is None:
            raise ValueError(f"REFUSED: no facts for the block day {i}'s trade {j}")
        rpc = lt.get("risk_per_contract")                # C2-8: the facts against the trade the engine handed out
        if rpc is not None and abs(float(rpc) - f.stop_ticks * f.tick_value) > 1e-9:
            raise ValueError(f"REFUSED (C2-8): the trade ({i}, {j})'s stop is {rpc} a contract, its facts "
                             f"{f.stop_ticks * f.tick_value}")
        et = getattr(self.blocks[i], "entry_t", None)
        if et is not None and abs(float(et[int(j)]) - float(f.entry)) > 1e-9:
            raise ValueError(f"REFUSED (C2-8): the trade ({i}, {j}) fills at {float(et[int(j)])}, its facts at "
                             f"{f.entry}")
        return _Key(K.moment(i, int(f.decision), int(f.sub)), f.underlying), f

    def uniform(self, k: _Key, kind: int, lane: int) -> float:
        u = self.cache.get((k.moment, int(kind)))
        if u is None:
            u = self.coins.coin(k, kind)[:, 0]
            self.cache[(k.moment, int(kind))] = u
        return float(u[lane])


_STATS = (("trades", None), ("intended_risk", "intended_risk"), ("intended_capped_risk", "intended_capped_risk"),
          ("realised_risk", "realised_risk"))


class RaceOver:
    """A vendored per-account draw, every attribute and call its own, its returned P&L replaced (ruling 1)."""

    def __init__(self, inner: Any, unit: _Unit | None, lane: int, outcome: str, log: list | None,
                 counts: dict | None):
        object.__setattr__(self, "_inner", inner)
        object.__setattr__(self, "_unit", unit)
        object.__setattr__(self, "_lane", int(lane))
        object.__setattr__(self, "_outcome", outcome)
        object.__setattr__(self, "_log", log)
        object.__setattr__(self, "_counts", counts)
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
        out = self._inner(n, day, slot, cushion, **kw)       # the engine's own keywords: its state is the engine's
        if self._outcome == "vendored":
            return out
        if kw.get("stretch"):
            raise ValueError("REFUSED: the baseline race takes no stretch exit (D-368; no registered baseline uses it)")
        pnl = float(np.asarray(out)[0])
        if math.isnan(pnl):
            return out
        lt = getattr(self._inner, "last_trade", None)
        if not lt or lt.get("stood_aside") or not lt.get("realised_risk", lt.get("risk")):
            return out
        st = object.__getattribute__(self, "_state")
        room = float(np.asarray(cushion)[0])
        if st[2]:
            self._uncount(lt)
            return np.array([math.nan])
        risk = float(lt.get("realised_risk", lt.get("risk")))
        new, info = self._law(int(lt["historical_day"]), int(lt["trade_index"]), risk, lt, room, st, pnl)
        if math.isnan(new):
            self._uncount(lt)
        else:
            st[1] += max(new, -room)
            stats = getattr(self._inner, "stats", None)
            if stats is not None and hasattr(stats, "need_exits"):
                stats.need_exits += int(info.get("need_hit", False)) - int(bool(lt.get("at_need")))
        lt.update({"u": None, "mae": None, "race_law": info["law"], "race_kind": info["kind"], "race_R": info["R"],
                   "race_u": (new / risk) if not math.isnan(new) else None,
                   "race_need": bool(info.get("need_hit", False))})
        return np.array([new])

    def _uncount(self, lt: Mapping[str, Any]) -> None:
        """A trade the race leaves untaken, taken back out of the vendored draw's statistics."""
        stats = getattr(self._inner, "stats", None)
        if stats is None or not hasattr(stats, "trades"):
            return
        stats.trades -= 1
        for name, key in _STATS[1:]:
            if lt.get(key) is not None:
                setattr(stats, name, getattr(stats, name) - float(lt[key]))
        stats.need_exits -= int(bool(lt.get("at_need")))
        stats.room_capped -= int(bool(lt.get("room_capped")))
        stats.at_cap -= int(bool(lt.get("at_cap")))

    def _law(self, h: int, j: int, risk: float, lt: Mapping[str, Any], room: float, st: list, vend: float
             ) -> tuple[float, dict]:
        u, arm = self._unit, self._unit.arm
        key, f = u.key(h, j, lt)
        R = lt.get("rr")
        if R is None:
            raise ValueError("REFUSED (C2-6): the vendored draw read the trade at no R (no fallback; an abandon leaf "
                             "takes no trade)")
        R = float(R)
        kind = f.kinds.get(R)
        if kind is None:
            raise ValueError(f"REFUSED: the trade ({u.start + h}, {j}) carries no kind at R = {R}")
        d = risk / float(f.stop_ticks)                        # the position's dollars a tick
        fee = lt.get("fee")                                   # D-324: the engine's fee at the contracts held
        if fee is None:                                       # no fee schedule: the facts' a contract, at the contracts
            n_c = lt.get("contracts")
            if f.fee_per_contract is None or n_c is None:
                raise ValueError("REFUSED (C2-2): the draw reports no fee, and the facts no fee a contract or the draw "
                                 "no contracts")
            fee = float(f.fee_per_contract) * int(n_c)
        fee = float(fee)
        extra = float(arm.worse_ticks) * d
        e = f.e_ticks * d + fee + extra
        xt, xs, xf = f.xt_ticks * d + extra, f.xs_ticks * d + extra, f.xf_ticks * d + extra
        need = lt.get("need")
        G = float(target_ticks(R, f.stop_ticks))
        capped = need is not None and np.isfinite(float(need)) and (float(need) + e + xt) / d < G
        if capped:
            G = (float(need) + e + xt) / d                    # the profit_level race: a win nets exactly the need
        info: dict[str, Any] = {"R": R, "kind": kind, "G": G, "fee": fee, "d": d, "need": need, "vendored": vend}
        if self._outcome == "as_walked":
            out = self._as_walked(f, R, kind, d, fee, lt)
            info["law"] = "as_walked"
            self._note(h, j, room, info, out)
            return out, info
        floor_room = st[0] + st[1]
        if arm.missed_q > 0 and u.uniform(key, K.MISSED, self._lane) < arm.missed_q:
            info["law"] = "missed"
            self._note(h, j, room, info, math.nan)
            return math.nan, info
        L_fill = min(f.stop_ticks * d, room - e - max(xs, xf))
        if not L_fill > EPS:
            if floor_room <= room + EPS:
                info["law"] = "fill_fail"
                self._note(h, j, room, info, -room)
                return -room, info
            st[2] = True
            info["law"] = "day_end"
            self._note(h, j, room, info, math.nan)
            return math.nan, info
        L = min(f.stop_ticks * d, room - e - xs)
        info["L"] = L
        if f.has_move:
            d1 = float(int(f.be_open) - int(f.entry))
            d2 = float(int(f.limit) - int(f.be_open))
            s1 = RD.walk_step(float(f.sigma), d1, J.WALK_MAX)
            n1 = RD.walk_steps(float(f.sigma), d1, s1)
            s2 = RD.walk_step(float(f.sigma), d2, J.WALK_MAX)
            n2 = RD.walk_steps(float(f.sigma), d2, s2)
            if max(n1, n2) > J.WALK_MAX:
                raise ValueError("REFUSED (C2-10): a phase of the move reads past WALK_MAX")
            read = self._reader(key)
            g, k = MV.move_outcomes(read, 1, G, L / d, s1, n1, s2, n2, J.WALK_CHUNK)
            kc = int(k[0])
            cost = xt if kc == MV.TARGET else xs if kc in (MV.STOP, MV.BREAKEVEN) else xf
            out = -e + float(g[0]) * d - cost
            info.update(law="move", exit=kc, s1=s1, n1=n1, s2=s2, n2=n2, need_hit=bool(capped and kc == MV.TARGET))
            self._count(f, R, kc == MV.BREAKEVEN)
            self._note(h, j, room, info, out)
            return out, info
        if kind in ("t", "s"):
            p = L / (L + G * d)
            w = bool(RD.race_outcome(np.array([u.uniform(key, K.RACE, self._lane)]), np.array([p]), arm.plant_eps)[0])
            out = (-e + G * d - xt) if w else (-e - L - xs)
            info.update(law="race", p=p, exit=1 if w else -1, need_hit=bool(capped and w))
            self._note(h, j, room, info, out)
            return out, info
        T = float(max(1, int(f.limit) - int(f.entry)))
        s = RD.walk_step(float(f.sigma), T, J.WALK_MAX)
        n = RD.walk_steps(float(f.sigma), T, s)
        if n > J.WALK_MAX:
            raise ValueError("REFUSED (C2-10): the walk reads past WALK_MAX")
        v, k = RD.walk_run(self._reader(key), 1, G, np.array([L / d]), s, int(n), J.WALK_CHUNK)
        kc = int(k[0])
        cost = xt if kc == 1 else xs if kc == -1 else xf
        out = -e + float(v[0]) * d - cost                     # a flatten past the floor: the engine clips it
        info.update(law="walk", exit=kc, s=s, n=n, need_hit=bool(capped and kc == 1))
        self._note(h, j, room, info, out)
        return out, info

    def _reader(self, key: _Key):
        coins, lane = self._unit.coins, self._lane
        coins.record(key, K.WALK, [lane])

        def read(rows, first, count):
            return coins.coin(key, K.WALK, count, np.asarray([lane])[rows], first=first, record=False)

        return read

    def _as_walked(self, f: TradeFacts, R: float, kind: str, d: float, fee: float, lt: Mapping[str, Any]) -> float:
        """Beside only: the trade's historical gross at R re-booked with the race arm's costs (C2-2's test)."""
        if lt.get("at_need"):
            return float(lt["need"])
        if f.walked is None or R not in f.walked:
            raise ValueError("the as-walked arm needs each trade's historical gross at its R")
        ex = {"t": f.xt_ticks, "s": f.xs_ticks, "b": f.xs_ticks, "f": f.xf_ticks}[kind]
        return float(f.walked[R]) * d - f.e_ticks * d - fee - ex * d

    def _count(self, f: TradeFacts, R: float, redrawn_b: bool) -> None:
        c = object.__getattribute__(self, "_counts")
        if c is None:
            return
        c["move_trades"] += 1
        c["b_redrawn"] += int(redrawn_b)
        c["b_historical"] += int(f.kinds.get(R) == "b")
        c["be_differs"] += int(f.be_vendored is not None and int(f.be_vendored) != int(f.be_open))

    def _note(self, h, j, room, info, out) -> None:
        log = object.__getattribute__(self, "_log")
        if log is not None:
            log.append({"i": self._unit.start + h, "j": j, "lane": self._lane, "acct": getattr(self._inner, "key", None),
                        "room": room, "out": out, **info})


def replay(blocks: Sequence[Any], args: Mapping[str, Any], horizon: int, *, unit: _Unit | None = None, lane: int = 0,
           outcome: str = "race", log: list | None = None, counts: dict | None = None) -> Any:
    """`customer_slices.replay`'s call (the vendored `SharedDayDraws` over the blocks in replay, the job's draw and
    path arguments, the vendored `simulate_lockstep_path`), each account's draw wrapped in `RaceOver`."""
    from extended import use_vendored_stage2

    use_vendored_stage2()
    from propedge.campaign.lockstep import simulate_lockstep_path
    from propedge.campaign.shared_days import SharedDayDraws

    if outcome not in OUTCOMES:
        raise ValueError(f"outcome is one of {OUTCOMES}, got {outcome!r}")
    if outcome != "vendored" and unit is None:
        raise ValueError("the race needs the unit's coin field and the trades' facts")
    n = int(horizon)
    sd = SharedDayDraws({0: list(blocks[:n])}, seed=args["seed"], replay=True, **args["draws"])
    kw = sd.lockstep_kwargs()
    if "flip" in kw:
        raise ValueError("REFUSED: a flip stream is not read on the baseline mode")
    cf, ff = kw["combine_draw_factory"], kw["funded_draw_factory"]
    kw["combine_draw_factory"] = lambda i, d: RaceOver(cf(i, d), unit, lane, outcome, log, counts)
    kw["funded_draw_factory"] = lambda i, d: RaceOver(ff(i, d), unit, lane, outcome, log, counts)
    return simulate_lockstep_path(args["draws"]["protocol"], seed=args["seed"], horizon_days=n + 1, **args["path"],
                                  **kw)


@dataclass
class BaselineRecords(J.Records):
    """`three_way_journey.Records` on the baseline mode, with the counts printed beside (C2-4, N-1) and the paths and
    laws' logs when kept."""

    move_trades: np.ndarray | None = None     # trades given the move law
    b_redrawn: np.ndarray | None = None       # the `b` exits the move law redrew among them
    b_historical: np.ndarray | None = None    # FV3's historical `b` exits among the same trades
    be_differs: np.ndarray | None = None      # those whose vendored move bar differs from s + 1
    paths: tuple = ()
    logs: tuple = ()
    outcome: str = "race"


def simulate(blocks: Sequence[Any], args: Mapping[str, Any], facts: Mapping[tuple[int, int], TradeFacts], start: int,
             seed_indices: Sequence[int], horizon: int, *, seed: int, part: int, history: int, block_sessions: int,
             dates: Any = None, arm: J.ArmSpec = J.ArmSpec(), budget: float | None = None,
             guard: K.KeyGuard | None = None, outcome: str = "race", keep_paths: bool = False, log: bool = False,
             calendar: frozenset | None = None) -> BaselineRecords:
    """The units (start, c), c in `seed_indices`: each U1's replay of the job's blocks from `start` for `horizon`
    sessions, its trades' outcomes redrawn on the unit's coin field (`outcome="race"`), passed through (`"vendored"`,
    the identity) or re-booked as walked (`"as_walked"`, beside)."""
    J.check_window(start, horizon, block_sessions)
    TF.check_dates(dates, start, horizon, block_sessions, seed=seed, calendar=calendar)
    idx = [int(c) for c in seed_indices]
    if len(set(idx)) != len(idx):
        raise ValueError("REFUSED: a seed index repeats (two lanes would read one coin field)")
    if arm.enforcement_q > 0 or arm.reading != "martingale":
        raise ValueError("REFUSED: the baseline mode reads the martingale outcome at 0 % denial (the vendored outcome "
                         "is `outcome='vendored'`, the historical one `outcome='as_walked'`)")
    if len(blocks) < start + horizon:
        raise ValueError("the job's blocks end before the window")
    coins = J.CoinLanes(seed, part, history, start, idx, guard, arm.twin)
    unit = _Unit(facts, blocks, start, coins, arm)
    path_kw = args["path"]
    bankroll, lag = float(path_kw["initial_bankroll"]), int(path_kw["payout_lag_days"])
    out = {k: [] for k in ("rel", "first_pass", "first_pay", "ahead", "accounts", "balance", "arrivals")}
    names = ("move_trades", "b_redrawn", "b_historical", "be_differs")
    side = {k: [] for k in names}
    paths, logs, fills = [], [], []
    for j in range(len(idx)):
        lg: list = []
        cnt = {k: 0 for k in names}
        p = replay(blocks[start:start + horizon], args, horizon, unit=unit, lane=j, outcome=outcome, log=lg,
                   counts=cnt)
        r = TF.records_of(p, bankroll=bankroll, lag=lag, horizon=horizon, budget=budget)
        for k in out:
            out[k].append(r[k])
        for k in names:
            side[k].append(cnt[k])
        fills.append(sum(1 for x in lg if x["law"] == "fill_fail"))
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
                           balance=np.asarray(out["balance"], float), fill_failures=np.asarray(fills, np.int64),
                           **{k: np.asarray(v, np.int64) for k, v in side.items()},
                           paths=tuple(paths), logs=tuple(logs), outcome=outcome)


__all__ = ["TASK", "EPS", "OUTCOMES", "KINDS", "TradeFacts", "target_ticks", "alert_sigma", "RaceOver", "replay",
           "BaselineRecords", "simulate"]
