"""EXPLORATORY (D-611, corrected by D-612): family PFA's cheap screen -- the Point & Figure catapult traded on its
natural bracket at the operator's latency (`config/pf_arm_a.yaml`). Pure functions over one trading day's minute bars;
`scripts/pfa_screen.py` reads the development bars, drives D-607's engine and writes the files. Its kill lines are
contract-fit lines; every P&L reading is reported beside them and decides nothing.

**The orders are the ALERTS (D-612 (2))**, not only the setups that triggered: `pnf.scan`'s `alerts` list holds every
pending entry as D-607's engine opened it -- the catapults (bull and bear; the screen keeps the fixed reading `r7_low`)
and the plain triple top buy / bottom sell, at boxes 2.5, 5, 6.25, 7.5 and 10 points -- whatever its later fate in the
engine (triggered, untriggered, lost at a roll, open at the end). Each carries its bracket, fixed when the alert bar
ends: entry T, stop, the horizontal-count target. An alert is an order when its alert bar ENDS inside Topstep's hours
(end slot below 1330, `pf_fit.window_of`), since that is when the order is placed; its window is that bar's too.

**The clock** is the trading day's (`collect_core.c_slot`): a bar is indexed by its END minute after 17:00 CT, one
day's bars in `atlas_local.day_arrays`' arrays (NaN where no bar; P-16's arrays, `atlas_a3.bar_arrays`). An order lives
on its ALERT bar's trading day: it works from the alert bar's end + L (L = 5, D-266), so the first bar it can fill on is
the first bar STARTING at or after that time -- end slot `alert_end_slot + L + 1` (`first_working_slot`) -- and the
last is the one ending before 15:08 CT (`day_end`: the last bar at or before 15:10, capped at `orb_core.FLAT_ENTRY`, the
bar the rung walk last enters on).

**Missed** (`missed_by_bars`, D-612 (2)): price reached T (high >= T for a buy, low <= T for a sell) on a bar ending
from the alert bar's end slot through the alert bar's end + L -- the alert bar's own range included (a trigger printing
on the alert bar is before the order works, D-607 (12)) -- read from the bars, never from the engine's trigger. On the
alerts the engine triggered on the alert's day this equals D-607's `missed_L5` (the script checks it).

**One cancel rule for every policy** (D-612 (2)): before the fill, a working bar whose range reaches the stop level
(low <= stop for a buy) or the target (high >= target), checked stop first, cancels the order; so does 15:08 CT with no
fill. Bars before the first working bar never cancel. On the fill bar itself nothing is cancelled: the bar is filled
and walked whole. **The policies** (`place`): not missed -- all three alike -- the first working bar reaching T fills,
at T when it opens on T's near side (strictly below T for a buy), else at its open (it opened at or beyond T).
Missed -- ``skip``: no trade; ``rest`` (the card's): only a working bar that OPENS on T's near side and reaches T fills,
at T (a bar opening at or beyond T does not fill; the order keeps resting); ``chase``: the open of the first working
bar. Under every policy there is no trade when the fill price is not strictly between the stop and the target on the
trade's side (`beyond`; a count target not beyond T is reached before any fill).

**The walk** (`walk_bracket`) is FV3-C's rung walk's settlement (`fv3_rung_walk.walk`, P-16's walk through
`atlas_a3.walk_minutes`) on the trade's own stop and target, from the fill bar to the bar ending 15:08 CT: excursions
from the walk's entry price in whole ticks, the fill bar counted whole; the stop is REACHED (adverse excursion >= the
stop), the target TRADED THROUGH (favourable excursion > the target); a bar reaching both counts as the stop; a trade
open after the bar ending 15:08 is unresolved and closes as FV3-C's flatten does (the worst of the bars ending 15:08 to
15:10 less two ticks, else the last close by 15:08). FV3's breakeven move is NOT applied: D-611's stop never moves.

**Costs** (P-16's, `resolved_coin.cell_trades` / `atlas_a3.cell_trades` arithmetic, `a4_coin_atlas.net_r`): net R =
gross ticks / S - (a tick at entry x tick value + the fee a micro-equivalent pays at the fresh Combine's size at that
stop (`atlas_a3.fee_by_stop`) + the exit's ticks by kind x tick value) / (S x tick value), S the trade's own stop in
ticks from the walk's entry price (the slip is a cost, as P-16 books it). The fill price written is the walk's entry
plus the slip.

**P-16's news-safe cut** (D-533 (2), `resolved_coin.drop_release_minute`'s rule on the fill bar): on a report day
(`day_kind` 'b', A1's day records) a fill on a bar starting before 07:35 CT (end slot <= `RELEASE_CLEAR`) is dropped.

**The kill lines** (on ``rest``, the catapults, each box; any one kills): K1 fewer than `K1_MIN` filled trades a session
over the development day list (zero days counted); K2 more than `K2_MAX` unresolved overall or in any calendar year with
at least `K2_YEAR_MIN_SESSIONS` sessions; K3 D-212 (1) as D-312 (1) settled it (D-612 (1)): each state's risk declared
at each stop width as exactly what the full micro allowance carries of P-16's fresh risk (`declared_by_stop`), each
filled trade checked against its own stop's declared risk (`model_card.by_stop_shares`' arithmetic), a stop at which no
whole micro fits counting against it; below `model_card.RISK_SHARE` in either state kills. Beside, deciding nothing:
D-611's single-figure reading (`k3_single`, `model_card.risk_consistency` at P-16's $2,000) and each state's realised
dollars per trade.

**Beside** (deciding nothing): e (the mean net R) and its one-sided 95 % lower bound -- the 5th percentile of the
stationary session-block bootstrap's replicate means (`a4_coin_atlas.stationary_counts`, mean block 21, 2,000
replicates, seed 20261811); gross and net R, the target-hit share, the realised risk over D, the reward-to-risk, the
minutes held; per year and window; the drift-matched coin (D-271): the same fills with the side from a fair coin seeded
20261811 and the same stop and target distances from the walk's entry.
"""
from __future__ import annotations

import hashlib
import math
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from propedge.outcomes.collect_core import C_FLAT, c_slot
from propedge.outcomes.fv3_core import FLATTEN_BARS
from propedge.outcomes.orb_core import FLAT_ENTRY
from propedge.research import fast_walk
from propedge.research import pnf
from propedge.research import resolved_coin as rc

DECISION = "D-611"
CORRECTION = "D-612"
FAMILY = "PFA"
FAMILY_ID = f"{DECISION}:pfa_screen"
RESULT = "pfa_screen"
RESULT_TRADES = "pfa_trades"
CONFIG = "config/pf_arm_a.yaml"
#: sha256 of `config/pf_arm_a.yaml`'s LF text at D-611 (a CRLF checkout reads the same)
CONFIG_SHA256_LF = "42c6ec4322ed6a1cc4c2486ed48eea23a83285f4eb21d62b513caccb91ab3c0d"
SETUPS_FILE = "pf_fit_setups.csv"
#: sha256 of `results/pf_fit_setups.csv` (D-609's read file): its manifest's, and of its LF text
SETUPS_SHA256 = "9fcf7d7330e607ad7bb6bd3a9f35cb24efbf2436ccfad71d0ac199da2cc19983"
SETUPS_SHA256_LF = "d50030533d75ef2f5d81ec24f8df626e736cb8cc99ae22c9bd454391303ca8b8"

MARKET = "NQ"
DEV_START, DEV_END = "2020-01-01", "2026-07-16"
BOXES = (2.5, 5.0, 6.25, 7.5, 10.0)       # D-611: D-607's grid and D-610's contract-sized 6.25 (25 ticks)
FIT_BOXES = tuple(pnf.BOXES)               # the boxes `results/pf_fit_setups.csv` holds
TICK = pnf.TICK                            # 0.25 points
TICK_VALUE = 0.5                           # MNQ: a tick at $2 a point (atlas_a3.TICK_VALUE)
ENTRY_SLIP_TICKS = 1                       # P-16's entry slip (config/atlas_a3.yaml slip_ticks; checked by the script)
LATENCY_MIN = 5                            # D-266, config/pf_arm_a.yaml latency_minutes
POLICIES = ("rest", "skip", "chase")
CARD_POLICY = "rest"
FIXED_CHOICE = "r7_low"                    # D-607's fixed catapult reading
CATAPULT, PLAIN = "catapult", "plain"
GROUPS = {CATAPULT: pnf.CATAPULTS, PLAIN: pnf.PLAINS}
FATES = ("triggered", "untriggered", "lost_at_restart", "open_at_end")
#: D-611's 20 cells: every box x every policy for the catapult; every box at rest for the plain triple
CELLS = tuple([(b, CATAPULT, p) for b in BOXES for p in POLICIES] + [(b, PLAIN, CARD_POLICY) for b in BOXES])

SEED = 20261811                            # D-611: the bound's bootstrap and the coin, used nowhere before
BOOT_REPS = 2000
BOOT_BLOCK = 21.0
BOUND_Q = 0.05                             # one-sided 95 %: the replicates' 5th percentile

K1_MIN = 1.0                               # filled catapults a session (D-154 for five seats)
K2_MAX = 0.05                              # D-212 as amended by D-308
K2_YEAR_MIN_SESSIONS = 63                  # D-604's year rule
REPORT_DAY_KIND = rc.REPORT_DAY_KIND       # 'b'
RELEASE_CLEAR = c_slot(*rc.RELEASE_CLEAR_CT)   # 875: 07:35 CT; a fill bar ending at or before it started before 07:35
WINDOWS = dict(rc.WINDOWS)                 # all [0, 1330), asia [60, 540), london [540, 930), us [930, 1330)
SUB_WINDOWS = ("asia", "london", "us")
QUANTILES = (5, 25, 50, 75, 95)

STOP, TARGET, FLATTEN = 0, 1, 2            # fv3_rung_walk's kinds (no breakeven here)
KIND_NAME = {STOP: "stop", TARGET: "target", FLATTEN: "flatten"}
EXIT_TICKS = {STOP: 1, TARGET: 0, FLATTEN: 2}   # fv3_rung_walk.EXIT_TICKS (checked by the tests)
FLATTEN_SLIP_TICKS = 2
FILLED = "filled"
#: every way an order can end without a trade
REASONS = ("missed", "cancel_stop", "cancel_target", "cancel_1510", "beyond", "news_cut")


# ------------------------------------------------------------------------------------------------ pins


def lf_sha256(data: bytes) -> str:
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


# ------------------------------------------------------------------------------------------------ the alerts


def alert_rows(bars: pd.DataFrame, box: float, result: Mapping[str, Any]) -> pd.DataFrame:
    """One row per alert of `pnf.scan`'s `result` on `bars` (ts, day, contract, ...; in ts order): the alert bar's
    trading day, end (CT and clock slot), window and hours, the bracket in points, the readings' flags, the engine's
    fate and the trigger bar (when triggered)."""
    from propedge.research import pf_fit as PF
    from propedge.research.s3_event_kinds import bar_end_slots

    A = list(result["alerts"])
    cols = ["date", "kind", "side", "box_points", "r7_low", "contract", "chart", "column_k", "alert_bar",
            "alert_end_ct", "alert_end_slot", "window", "in_hours", "level_R", "entry_T", "stop", "D_points",
            "D_over_b", "target", "target_R", "pattern_extreme", "column_k_extreme", "pullback_extreme", "max7_from_R",
            "max7_from_breakout_box", "above_pattern_low", "retest", "fate", "end_bar", "trigger_bar"]
    if not A:
        return pd.DataFrame(columns=cols)
    ts = bars["ts"].to_numpy(dtype="int64")
    day = bars["day"].astype(str).to_numpy()
    con = bars["contract"].astype(str).to_numpy() if "contract" in bars.columns else np.array([""] * len(bars))
    ia = np.array([a["alert_bar"] for a in A], dtype=np.int64)
    slot = bar_end_slots(ts[ia]).astype(int)
    end_ct = pd.to_datetime(pd.Series(ts[ia] + 60), unit="s", utc=True).dt.tz_convert("America/Chicago")
    bt = int(result["box_ticks"])
    df = pd.DataFrame({"date": day[ia], "kind": [a["kind"] for a in A], "side": [int(a["side"]) for a in A],
                       "box_points": bt * TICK, "contract": con[ia], "chart": [int(a["chart"]) for a in A],
                       "column_k": [int(a["column"]) for a in A], "alert_bar": ia,
                       "alert_end_ct": end_ct.dt.strftime("%Y-%m-%d %H:%M").to_numpy(), "alert_end_slot": slot})
    for f in pnf.PRICE_FIELDS:
        df[f] = [np.nan if a[f] is None else a[f] * TICK for a in A]
    df = df.rename(columns={"level": "level_R", "entry": "entry_T", "D": "D_points"})
    df["D_over_b"] = np.array([a["D"] for a in A], dtype=float) / bt
    df["target_R"] = [pnf.target_r(a) for a in A]
    for f in ("max7_from_R", "max7_from_breakout_box", "above_pattern_low", "retest"):
        df[f] = pd.array([None if a[f] is None else bool(a[f]) for a in A], dtype="boolean")
    cat = df["kind"].isin(pnf.CATAPULTS).to_numpy()
    df[FIXED_CHOICE] = cat & np.array([a["max7_from_R"] is True and a["above_pattern_low"] is True for a in A])
    df["window"] = [PF.window_of(s) for s in slot]
    df["in_hours"] = df["window"] != "outside"
    df["fate"] = [a["fate"] for a in A]
    df["end_bar"] = pd.array([a["end_bar"] for a in A], dtype="Int64")
    df["trigger_bar"] = pd.array([a["trigger_bar"] for a in A], dtype="Int64")
    return df[cols]


def alert_problems(result: Mapping[str, Any]) -> list[str]:
    """D-612's additive alerts against the engine's own outputs: the triggered alerts are exactly the setups (every
    field, in order), each other fate's count is the engine's count, and D-607 (4) holds on every alert."""
    out = []
    S, A, c = list(result["setups"]), list(result["alerts"]), result["counts"]
    trig = [a for a in A if a["fate"] == "triggered"]
    if len(trig) != len(S):
        out.append(f"{len(trig)} triggered alerts, {len(S)} setups")
    else:
        key = lambda x: (x["trigger_bar"], x["alert_bar"], x["kind"], x["column"])  # noqa: E731
        for a, s in zip(sorted(trig, key=key), sorted(S, key=key)):
            diff = [k for k in s if a.get(k) != s[k]]
            if diff:
                out.append(f"the {s['kind']} alert at bar {s['alert_bar']} differs from its setup in {diff}")
                break
    for fate, what in (("untriggered", "untriggered"), ("lost_at_restart", "lost_at_restart"),
                       ("open_at_end", "open_at_end")):
        for kind in pnf.KINDS:
            n = sum(1 for a in A if a["fate"] == fate and a["kind"] == kind)
            if n != int(c.get(f"{what}_{kind}", 0)):
                out.append(f"{n} {fate} {kind} alerts, the engine counts {c.get(f'{what}_{kind}', 0)}")
    if any(a["fate"] not in FATES for a in A):
        out.append("an alert with no fate")
    bt = int(result["box_ticks"])
    if any(int(a["D"]) < 5 * bt for a in A):
        out.append("an alert with D < 5b")
    return out


# ------------------------------------------------------------------------------------------------ the clock


def day_end(o: np.ndarray) -> int | None:
    """The last bar a trade can enter on, exclusive: min(the day's last bar at or before 15:10 CT, the bar ending
    15:08 CT) -- `fv3_rung_walk.walk`'s `end`; None for a day with no bar."""
    last = fast_walk.last_bar(np.asarray(o, dtype=float), C_FLAT)
    return None if last is None else min(last, FLAT_ENTRY)


def first_working_slot(alert_end_slot: int, latency: int = LATENCY_MIN) -> int:
    """The end slot of the first bar STARTING at or after the alert bar's end + `latency` minutes."""
    return int(alert_end_slot) + int(latency) + 1


def window_of_slot(slot: int) -> str:
    """The narrowest of P-16's windows holding a bar's end slot ('all' for 17:01-18:00 CT; 'outside' from 1330)."""
    s = int(slot)
    if s >= WINDOWS["all"][1]:
        return "outside"
    for w in SUB_WINDOWS:
        lo, hi = WINDOWS[w]
        if lo <= s < hi:
            return w
    return "all"


def missed_by_bars(h, l, side: int, T: float, alert_end_slot: int, latency: int = LATENCY_MIN) -> bool:
    """D-612 (2): price reached T on a bar ending from the alert bar's end slot through the alert's end + `latency`
    minutes (the bars that start before the order works, the alert bar included)."""
    A = int(alert_end_slot)
    hh = np.asarray(h, dtype=float)[A: A + int(latency) + 1]
    ll = np.asarray(l, dtype=float)[A: A + int(latency) + 1]
    with np.errstate(invalid="ignore"):
        x = hh if int(side) > 0 else ll
        return bool(np.any(int(side) * (x - float(T)) >= 0))


# ------------------------------------------------------------------------------------------------ the walk


def walk_bracket(o, h, l, c, je: int, e: float, side: int, S: int, Tt: int, tick: float = TICK) -> dict[str, int]:
    """One trade walked from bar `je` at entry price `e` with a stop `S` ticks away and a target `Tt` ticks away
    (`fv3_rung_walk.walk`'s settlement without its breakeven move). Returns kind (0 stop, 1 target, 2 flatten), exit
    (bar), gross and mae (ticks)."""
    o, h, l, c = (np.asarray(x, dtype=float) for x in (o, h, l, c))
    n = len(o)
    end = day_end(o)
    je, S, Tt, d = int(je), int(S), int(Tt), int(side)
    if end is None or je >= end or np.isnan(o[je]):
        raise ValueError("an entry at or after 15:08 CT, or on a bar with no open")
    if S <= 0 or Tt <= 0 or d not in (1, -1):
        raise ValueError("a bracket needs a positive stop and target distance and a side of +1 / -1")
    seg = slice(je, end + 1)
    pres = ~np.isnan(o[seg])
    hh, ll = h[seg], l[seg]
    with np.errstate(invalid="ignore"):
        fav = (hh - e) if d > 0 else (e - ll)
        adv = (e - ll) if d > 0 else (hh - e)
    fav = np.where(pres, np.round(fav / tick), -np.inf)
    adv = np.where(pres, np.round(adv / tick), -np.inf)
    rmf = np.maximum.accumulate(fav)
    rma = np.maximum.accumulate(adv)
    sm, tm = rma >= S, rmf > Tt
    ja = int(np.argmax(sm)) if sm.any() else None
    js = int(np.argmax(tm)) if tm.any() else None
    if ja is not None and (js is None or ja <= js):
        return {"kind": STOP, "exit": je + ja, "gross": -S, "mae": S}
    if js is not None:
        return {"kind": TARGET, "exit": je + js, "gross": Tt, "mae": int(max(0.0, rma[js]))}
    fb = [j for j in FLATTEN_BARS if j < n]
    with np.errstate(invalid="ignore"):
        wv = np.array([(l[j] - e) if d > 0 else (e - h[j]) for j in fb], dtype=float)
    if wv.size and not np.isnan(wv).all():
        flat = int(np.round(np.nanmin(wv) / tick)) - FLATTEN_SLIP_TICKS
    else:
        jc = next((j for j in range(min(end, n - 1), 0, -1) if not np.isnan(c[j])), None)
        flat = int(np.round(d * (c[jc] - e) / tick)) if jc is not None else 0
    return {"kind": FLATTEN, "exit": int(FLAT_ENTRY), "gross": flat, "mae": int(max(0.0, rma[-1]))}


# ------------------------------------------------------------------------------------------------ the policies


def _no(reason: str) -> dict[str, Any]:
    return {"outcome": reason}


def _filled(j: int, e: float, how: str, side: int, stop: float, target: float, tick: float) -> dict[str, Any]:
    S = int(round(side * (e - stop) / tick))
    Tt = int(round(side * (target - e) / tick))
    if S <= 0 or Tt <= 0:
        return _no("beyond")
    return {"outcome": FILLED, "fill_slot": int(j), "walk_entry": float(e), "how": how, "S": S, "Tt": Tt}


def fill_order(o, h, l, side: int, T: float, stop: float, target: float, j0: int, end: int | None, *,
               near_only: bool, tick: float = TICK) -> dict[str, Any]:
    """An order at T working from bar `j0` (before `end`) under the one cancel rule. With `near_only` (rest after a
    missed trigger) only a bar opening strictly on T's near side and reaching T fills, at T; otherwise the first bar
    reaching T fills, at T when it opens on the near side, else at its open. A working bar before the fill reaching the
    stop (first) or the target cancels; no fill before `end` cancels."""
    d = int(side)
    if d * (target - T) <= 0:                        # the count target is not beyond T: reached before any fill
        return _no("beyond")
    if end is None or j0 >= end:
        return _no("cancel_1510")
    oo, hh, ll = (np.asarray(x, dtype=float)[j0:end] for x in (o, h, l))
    pres = ~np.isnan(oo)
    fx, ax = (hh, ll) if d > 0 else (ll, hh)          # the favourable and adverse extremes
    with np.errstate(invalid="ignore"):
        near = d * (oo - T) < 0
        reach = d * (fx - T) >= 0
        fillm = pres & reach & (near if near_only else True)
        stopm = pres & (d * (ax - stop) <= 0)
        tgtm = pres & (d * (fx - target) >= 0)
    ev = fillm | stopm | tgtm
    if not ev.any():
        return _no("cancel_1510")
    k = int(np.argmax(ev))
    if fillm[k]:
        if near[k]:
            return _filled(j0 + k, T, "rest_at_T" if near_only else "at_T", d, stop, target, tick)
        return _filled(j0 + k, float(oo[k]), "gap_open", d, stop, target, tick)
    return _no("cancel_stop" if stopm[k] else "cancel_target")


def fill_chase_open(o, side: int, stop: float, target: float, j0: int, end: int | None,
                    tick: float = TICK) -> dict[str, Any]:
    """``chase`` after a missed trigger: the open of the first working bar (no trade at or beyond stop or target)."""
    if end is None or j0 >= end:
        return _no("cancel_1510")
    oo = np.asarray(o, dtype=float)[j0:end]
    pres = np.flatnonzero(~np.isnan(oo))
    if not pres.size:
        return _no("cancel_1510")
    return _filled(j0 + int(pres[0]), float(oo[pres[0]]), "chase_open", int(side), stop, target, tick)


def place(policy: str, arrays: tuple, alert: Mapping[str, Any], *, latency: int = LATENCY_MIN,
          tick: float = TICK) -> dict[str, Any]:
    """One alert under one policy on its trading day's arrays (o, h, l, c): {outcome, missed, and when filled:
    fill_slot, walk_entry, how, S, Tt}. `alert` holds side, entry_T, stop, target (points) and alert_end_slot."""
    o, h, l, _ = arrays
    end = day_end(o)
    A = int(alert["alert_end_slot"])
    j0 = first_working_slot(A, latency)
    d, T, st, tg = int(alert["side"]), float(alert["entry_T"]), float(alert["stop"]), float(alert["target"])
    missed = missed_by_bars(h, l, d, T, A, latency)
    if policy not in POLICIES:
        raise ValueError(f"unknown policy {policy!r}; one of {POLICIES}")
    if missed and policy == "skip":
        r = _no("missed")
    elif missed and policy == "chase":
        r = fill_chase_open(o, d, st, tg, j0, end, tick)
    else:
        r = fill_order(o, h, l, d, T, st, tg, j0, end, near_only=missed and policy == "rest", tick=tick)
    r["missed"] = missed
    return r


def news_cut(day_kind: str, fill_slot: int) -> bool:
    """D-533 (2) on the fill bar: a report day's fill on a bar starting before 07:35 CT is dropped."""
    return str(day_kind) == REPORT_DAY_KIND and int(fill_slot) <= RELEASE_CLEAR


# ------------------------------------------------------------------------------------------------ costs


def net_r(gross_ticks, kind, S, fee, *, tick_value: float = TICK_VALUE, entry_ticks: float = ENTRY_SLIP_TICKS):
    """P-16's settlement in R, elementwise over trades with their own stops `S` (ticks) and fees: gross / S less a tick
    at entry, the fee and the exit's ticks by kind, over the stop's dollar risk (`a4_coin_atlas.net_r`'s arithmetic)."""
    return np.asarray(gross_ticks, float) / np.asarray(S, dtype=float) - cost_r(
        kind, S, fee, tick_value=tick_value, entry_ticks=entry_ticks)


def cost_r(kind, S, fee, *, tick_value: float = TICK_VALUE, entry_ticks: float = ENTRY_SLIP_TICKS):
    S = np.asarray(S, dtype=float)
    td = float(tick_value)
    xt = np.array([float(EXIT_TICKS[int(k)]) for k in np.atleast_1d(kind)], dtype=float)
    return (float(entry_ticks) * td + np.asarray(fee, float) + xt * td) / (S * td)


# ------------------------------------------------------------------------------------------------ the coin


def coin_sides(n: int, seed: int = SEED) -> np.ndarray:
    """D-271's drift-matched coin: one fair side per order of the universe in its fixed order (+1 long / -1 short)."""
    u = np.random.default_rng(int(seed)).random(int(n))
    return np.where(u < 0.5, 1, -1).astype(np.int8)


# ------------------------------------------------------------------------------------------------ the kill lines


def k1_supply(dates: Sequence[str], sessions: Sequence[str]) -> float:
    """Filled trades a session over `sessions` (a day with none a zero; dates outside the list not counted)."""
    s = {str(d) for d in sessions}
    n = sum(1 for d in dates if str(d) in s)
    return float(n) / len(s) if s else float("nan")


def k2_resolution(dates: Sequence[str], unresolved: Sequence[bool], sessions: Sequence[str],
                  min_sessions: int = K2_YEAR_MIN_SESSIONS) -> dict[str, Any]:
    """The unresolved share overall and per calendar year; only years with at least `min_sessions` sessions are
    judged (a judged year with no trade has no share and does not fail). {overall, by_year, judged_years, worst,
    worst_year, fails}."""
    df = pd.DataFrame({"y": [str(d)[:4] for d in dates], "u": np.asarray(unresolved, dtype=bool)})
    per_year_sessions = pd.Series([str(d)[:4] for d in sessions]).value_counts()
    judged = sorted(y for y, n in per_year_sessions.items() if int(n) >= int(min_sessions))
    overall = float(df["u"].mean()) if len(df) else float("nan")
    by_year = {y: float(g["u"].mean()) for y, g in df.groupby("y")}
    jv = {y: by_year[y] for y in judged if y in by_year}
    worst_year = max(jv, key=lambda y: jv[y]) if jv else None
    worst = jv[worst_year] if worst_year else float("nan")
    fails = bool((len(df) and overall > K2_MAX + 1e-12) or any(v > K2_MAX + 1e-12 for v in jv.values()))
    return {"overall": overall, "by_year": by_year, "judged_years": judged, "worst": worst,
            "worst_year": worst_year, "fails": fails}


def realised_dollars(stop_ticks, risk: float, cap: int, tick_value: float = TICK_VALUE):
    """The whole micros' dollars a state's risk buys at a stop, capped: min(floor(risk / stop $), cap) x stop $
    (elementwise for an array of stops)."""
    per = np.asarray(stop_ticks, dtype=float) * float(tick_value)
    n = np.minimum(np.floor(float(risk) / per + 1e-9), int(cap))
    out = n * per
    return float(out) if np.ndim(out) == 0 else out


def declared_by_stop(stop_ticks: Sequence[float], risks: Mapping[str, float], allowance: Mapping[str, int],
                     tick_value: float = TICK_VALUE) -> dict[str, dict[float, float]]:
    """D-312 (1): each state's risk declared at every stop width the trades use, as exactly what the full allowance
    carries of the state's single figure -- min(floor(figure / stop $), the allowance) x stop $."""
    stops = sorted({float(s) for s in stop_ticks})
    return {s: {S: realised_dollars(S, risks[s], allowance[s], tick_value) for S in stops} for s in ("combine", "funded")}


def _band(tick_value: float = TICK_VALUE) -> pd.DataFrame:
    """NQ's row of the stop band (`results/stop_band.csv`, read through its manifest): its tick value and cost floor."""
    from propedge.reporting.results import read_result
    from propedge.research.model_card import BAND_FILE

    b = read_result(BAND_FILE)
    b = b[b["market"] == MARKET]
    if not len(b) or float(b["tick_value"].iloc[0]) != float(tick_value):
        raise ValueError(f"the stop band's {MARKET} tick value is not {tick_value}")
    return b


def k3_by_stop(stop_ticks: Sequence[float], risks: Mapping[str, float], allowance: Mapping[str, int],
               band: pd.DataFrame | None = None, tick_value: float = TICK_VALUE) -> dict[str, dict[str, float]]:
    """K3 (D-612 (1)): per state, each trade against its own stop's declared risk (`declared_by_stop`) at the full
    allowance -- `model_card.by_stop_shares` (risk_ok, unsizeable, outside, n) and `share`, the K3 value: the share of
    trades that realise at least 90 % of their declared risk with at least one whole micro (a stop at which no micro
    fits declares $0 and counts against it)."""
    from propedge.research.model_card import RISK_TOLERANCE, by_stop_shares

    st = np.asarray(stop_ticks, dtype=float)
    states = ("combine", "funded")
    if not st.size:
        return {s: {"share": float("nan"), "risk_ok": float("nan"), "unsizeable": float("nan"),
                    "outside": float("nan"), "n": 0} for s in states}
    decl = declared_by_stop(st, risks, allowance, tick_value)
    stops = pd.concat([pd.DataFrame({"market": MARKET, "stop_ticks": st, "state": s}) for s in states],
                      ignore_index=True)
    sh = by_stop_shares(stops, decl, band if band is not None else _band(tick_value), dict(allowance))
    out = {}
    for s in states:
        per = st * float(tick_value)
        risk = np.array([decl[s][float(x)] for x in st])
        n = np.minimum(np.floor(risk / per + 1e-9), int(allowance[s]))
        ok = (n >= 1) & ((n * per) >= (1.0 - RISK_TOLERANCE) * risk)
        out[s] = {**sh[s], "share": float(ok.mean())}
    return out


def k3_single(stop_ticks: Sequence[float], risks: Mapping[str, float], allowance: Mapping[str, int],
              tick_value: float = TICK_VALUE) -> dict[str, float]:
    """Beside (D-612 (1)): D-611's single-figure reading -- `model_card.risk_consistency` with each state's one dollar
    risk and the full allowance's cap: the share of trades whose whole micros realise at least 90 % of it."""
    from propedge.research.model_card import risk_consistency

    stops = pd.DataFrame({"market": MARKET, "stop_ticks": np.asarray(stop_ticks, dtype=float)})
    sizes = {s: (float(risks[s]), s) for s in ("combine", "funded")}
    if not len(stops):
        return {s: float("nan") for s in sizes}
    band = pd.DataFrame([{"market": MARKET, "state": s, "risk": float(risks[s]), "tick_value": float(tick_value),
                          "cap_micros": int(allowance[s])} for s in sizes])
    return risk_consistency(stops, band, sizes)


def k3_passes(shares: Mapping[str, float]) -> bool:
    from propedge.research.model_card import RISK_SHARE

    return all(np.isfinite(v) and v >= RISK_SHARE for v in shares.values())


# ------------------------------------------------------------------------------------------------ the bound


def boot_counts(n_sessions: int, reps: int = BOOT_REPS, block: float = BOOT_BLOCK, seed: int = SEED) -> np.ndarray:
    """(reps, sessions): each session's multiplicity in each stationary-bootstrap replicate
    (`a4_coin_atlas.stationary_counts`)."""
    from propedge.research.a4_coin_atlas import stationary_counts

    return stationary_counts(int(n_sessions), int(reps), float(block), int(seed))


def mean_and_bound(day_idx: Sequence[int], values: Sequence[float], counts: np.ndarray,
                   q: float = BOUND_Q) -> tuple[float, float]:
    """(the mean per trade, its one-sided lower bound: the `q` quantile of the replicates' means per trade), the
    trades grouped by session index `day_idx` and the replicates resampling sessions (`counts`)."""
    v = np.asarray(values, dtype=float)
    if not len(v):
        return float("nan"), float("nan")
    T = counts.shape[1]
    idx = np.asarray(day_idx, dtype=np.int64)
    s = np.bincount(idx, weights=v, minlength=T).astype(float)
    m = np.bincount(idx, minlength=T).astype(float)
    C = counts.astype(float)
    den = C @ m
    with np.errstate(invalid="ignore", divide="ignore"):
        rep = np.where(den > 0, (C @ s) / den, np.nan)
    rep = rep[np.isfinite(rep)]
    return float(v.mean()), (float(np.quantile(rep, q)) if rep.size else float("nan"))


__all__ = ["DECISION", "CORRECTION", "FAMILY", "FAMILY_ID", "RESULT", "RESULT_TRADES", "CONFIG", "CONFIG_SHA256_LF",
           "SETUPS_FILE", "SETUPS_SHA256", "SETUPS_SHA256_LF", "MARKET", "DEV_START", "DEV_END", "BOXES", "FIT_BOXES",
           "TICK", "TICK_VALUE", "ENTRY_SLIP_TICKS", "LATENCY_MIN", "POLICIES", "CARD_POLICY", "FIXED_CHOICE",
           "CATAPULT", "PLAIN", "GROUPS", "FATES", "CELLS", "SEED", "BOOT_REPS", "BOOT_BLOCK", "BOUND_Q", "K1_MIN",
           "K2_MAX", "K2_YEAR_MIN_SESSIONS", "REPORT_DAY_KIND", "RELEASE_CLEAR", "WINDOWS", "SUB_WINDOWS",
           "QUANTILES", "STOP", "TARGET", "FLATTEN", "KIND_NAME", "EXIT_TICKS", "FILLED", "REASONS", "lf_sha256",
           "alert_rows", "alert_problems", "day_end", "first_working_slot", "window_of_slot", "missed_by_bars",
           "walk_bracket", "fill_order", "fill_chase_open", "place", "news_cut", "net_r", "cost_r", "coin_sides",
           "k1_supply", "k2_resolution", "realised_dollars", "declared_by_stop", "k3_by_stop", "k3_single",
           "k3_passes", "boot_counts", "mean_and_bound"]
