"""H4's naive-coin unchained offer builder, cross-session alert volatility, and P-16 / I-5 identity mode
(`prereg/H4_rebaseline.md` sections 5, 6, 7, 15, 16 I-5, Appendix C; E-287).

Two modes on one shared walk (`extended.walker.STAGE2`, FV3's breakeven move ON):
1. **As-run naive coin (`build_naive_coin_trades`)**:
   - Every 5-minute mark of `resolved_coin.marks()` in P-16's window `all` (`0..1325` step 5), **unchained**, admission
     T7 OFF, latency `L = 5` (order live at `mark + 5`, filled on the first present bar opening at or after `live` and
     strictly before `walk_end`; overlong offers dropped).
   - Filtered by Q-166's void calendar (`extended.day_calendar.day_context(..., reads_overnight=True, rules=W.STAGE2)`)
     and E-223's news convention (`extended.triggers.DayContext`: closed 08:30-08:59 CT, BLS 17:00-07:35 CT, FOMC days
     out, void days out, verified news windows if any; open positions at a window start flattened by
     `triggers.window_flatten_trade`).
   - Walked at P-16's stop (`STOP_TICKS = 150`) and all 12 Rs of `fv3_rung_walk.RR_GRID` (`0.25..3.00` step 0.25), in
     `resolved_coin.cell_trades`'s exact column schema.
   - As-run side drawn **once per `(session, moment)`** from `S.issue("h4s_schedule_side")` in part `H4-S` at
     `history=0, seed_index=0, start=0, draw_kind=SIDE` (matching `three_way_seeds.FIELD_RULES`).
   - Also emits per-trade `be_vendored` (first recorded bar within 5 min of next FV3 session open), clock/calendar
     `time_limit`, and mirror-walk gross ticks at every R (bounded in `[-S, +G]` for rc-11).
2. **P-16 / I-5 verification mode (`build_p16_i5_trades`)**:
   - On A1's walked days (`day_kind in ("n", "b")`), Q-166 void calendar OFF, A3's 07:30 CT report-day cut + D-533's
     07:35 CT release-minute cut, P-16's registered offered marks, latency `L = 0`, P-16's `coin_table` sides,
     walked by `extended.walker.STAGE2` at all 12 Rs and formatted identically to `resolved_coin.cell_trades` ->
     reproduces P-16's search-year `rc_dev_test.trades_hash` bit for bit!

Also provides `alert_sigma_cross_session` (F4-1): the standard deviation of one-minute close-to-close changes, in ticks
per root minute, over the last 60 bars closed at or before the alert, crossing session breaks into previous sessions
with the gap return across any session break excluded; returns `None` when fewer than two changes exist behind an
alert (counted beside and dropped from supply) **and also when two or more changes exist but every one is zero**
(sigma = 0, which the firm path's walk refuses and the declaration does not treat). `alert_sigma_detail` says which
(F-3, Q-188b); the builders count the two apart (`dropped_sigma_lt_2`, `dropped_sigma_zero`) and list each dropped
alert's date and time (`dropped_sigma_rows`), never a price.

Zero raw H4 seed literals appear here; every H4 seed is issued by role through `extended.three_way_seeds.issue`.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from typing import Any, Callable, Mapping, Sequence

import numpy as np
import pandas as pd

from extended import three_way_baseline as TB
from extended import three_way_keys as K
from extended import three_way_seeds as S
from extended import triggers as T
from extended import walker as W

#: P-16's registered stop width in MNQ ticks (37.5 points; `rc150_dev_test.STOP`)
P16_STOP_TICKS: int = 150
#: Naive coin latency in minutes (H4 section 7: lever table T4 reference L = 5)
COIN_LATENCY: int = 5
#: Naive coin offer mark grid step in minutes (`resolved_coin.MARK_STEP`)
MARK_STEP: int = 5
#: Trading-day session end in minutes after 17:00 CT (`resolved_coin.SESSION_END`, 15:10 CT)
SESSION_END: int = 22 * 60 + 10
#: P-16 / FV3 12-point R grid (`fv3_rung_walk.RR_GRID`)
RR_GRID: tuple[float, ...] = tuple(0.25 * k for k in range(1, 13))
#: F4-1 volatility lookback in closed 1-minute bars
SIGMA_LOOKBACK_BARS: int = 60
#: D-533 release-bar clear slot (07:35 CT = 875 min after 17:00 CT)
RELEASE_CLEAR_SLOT: int = W.slot(7, 35)
#: A3 BLS report-day cut slot (07:30 CT = 870 min after 17:00 CT)
BLS_CUT_SLOT: int = W.slot(7, 30)


def all_marks(step: int = MARK_STEP, end: int = SESSION_END) -> list[int]:
    """Every offer mark of P-16's window `all`: 17:00 CT (slot 0) every `step` minutes before `end` (15:10 CT)."""
    return list(range(0, int(end), int(step)))


def slot_ct(slot: int) -> str:
    """Trading-day-clock slot (minutes after 17:00 CT) formatted as HH:MM CT."""
    m = (int(slot) + 17 * 60) % (24 * 60)
    return f"{m // 60:02d}:{m % 60:02d}"


# --------------------------------------------------------------------------------------------- F4-1: alert volatility


#: F-3 (Q-188b): why an alert's volatility is missing -- the declared case and the undeclared one, kept apart
SIGMA_OK = "ok"
SIGMA_LT_2 = "lt_2_changes"          # the declared drop (section 7): fewer than two changes behind the alert
SIGMA_ZERO = "zero_dispersion"       # two or more changes behind the alert, every one zero: sigma = 0, not declared
SIGMA_REASONS = (SIGMA_OK, SIGMA_LT_2, SIGMA_ZERO)


@dataclass(frozen=True)
class SigmaReading:
    """F4-1's reading at one alert, with the counts behind it (F-3, Q-188b): `sigma` is None unless `reason` is
    `SIGMA_OK`; `n_bars` the closes read, `n_changes` the within-session changes formed from them, `n_nonzero` the
    changes that are not zero, `sessions_read` the sessions the window reached (1: the alert's own), `rms_fallback`
    True where the sample standard deviation was zero and the root mean square was returned instead (the builder's
    form since `31c507e`; never reached unless every change is the same non-zero value)."""

    sigma: float | None
    reason: str
    n_bars: int
    n_changes: int
    n_nonzero: int
    sessions_read: int
    rms_fallback: bool = False


def alert_sigma_detail(
    day_closes: Sequence[np.ndarray],
    day_idx: int,
    decision: int,
    *,
    lookback: int = SIGMA_LOOKBACK_BARS,
    tick: float = W.TICK,
) -> SigmaReading:
    """F4-1 with its reason (F-3, Q-188b): the standard deviation of 1-minute close-to-close changes (ticks per root
    minute) over the last `lookback` bars closed at or before `decision` on `day_idx`, crossing session breaks into
    prior sessions (`day_idx - 1`, ...) with every break's gap return excluded.

    `day_closes[d]` is a 1-D array indexed by Stage 2's bar-end minute (0 unused, 1..1440 valid, NaN where no bar).
    Strictly causal: reads ONLY `day_closes[day_idx][:decision + 1]` and earlier days `d < day_idx`.

    Two different refusals, never merged (the audit's F-3): **`SIGMA_LT_2`** -- fewer than two within-session changes
    behind the alert, the one case section 7 declares a drop for (the store's first minutes); **`SIGMA_ZERO`** -- two or
    more changes, every one of them zero (a market that printed one price for the whole window, e.g. a locked limit),
    where the declared estimator gives sigma = 0, which the firm path's walk refuses (`three_way_redraw.walk_step`
    needs sigma > 0) and the declaration does not treat. The builders count the two apart."""
    n_need = int(lookback)
    if n_need < 2:
        raise ValueError(f"lookback must be >= 2, got {lookback}")
    d = int(day_idx)
    if d < 0 or d >= len(day_closes):
        raise ValueError(f"day_idx {d} out of range for {len(day_closes)} days")
    dec = int(decision)
    if dec < 0:
        raise ValueError(f"decision slot must be >= 0, got {dec}")

    collected = 0
    sessions = 0
    # Store per-session chunks of (bar_ends, closes) in chronological order within each session;
    # gap returns across different session chunks are never formed.
    changes: list[np.ndarray] = []
    cur_d = d
    while cur_d >= 0 and collected < n_need:
        arr = np.asarray(day_closes[cur_d], dtype=float)
        hi = min(dec, len(arr) - 1) if cur_d == d else (len(arr) - 1)
        if hi >= 1:
            sub = arr[1 : hi + 1]
            idx = np.flatnonzero(~np.isnan(sub))
            if idx.size:
                need = n_need - collected
                if idx.size > need:
                    idx = idx[-need:]
                bars = idx + 1
                cs = arr[bars]
                collected += int(bars.size)
                sessions = d - cur_d + 1
                if bars.size >= 2:
                    dt = np.diff(bars).astype(float)
                    dx = np.diff(cs) / float(tick)
                    changes.append(dx / np.sqrt(dt))
        cur_d -= 1

    all_ch = np.concatenate(changes) if changes else np.zeros(0)
    n_ch = int(all_ch.size)
    n_nz = int(np.count_nonzero(all_ch))
    if n_ch < 2:
        return SigmaReading(None, SIGMA_LT_2, collected, n_ch, n_nz, sessions)
    sd = float(np.std(all_ch, ddof=1))
    if not (math.isfinite(sd) and sd > 0.0):
        # Fallback to RMS if all changes are the same non-zero value, else zero dispersion (F-3)
        rms = float(math.sqrt(float(np.mean(all_ch * all_ch))))
        if math.isfinite(rms) and rms > 0.0:
            return SigmaReading(rms, SIGMA_OK, collected, n_ch, n_nz, sessions, rms_fallback=True)
        return SigmaReading(None, SIGMA_ZERO, collected, n_ch, n_nz, sessions)
    return SigmaReading(sd, SIGMA_OK, collected, n_ch, n_nz, sessions)


def alert_sigma_cross_session(
    day_closes: Sequence[np.ndarray],
    day_idx: int,
    decision: int,
    *,
    lookback: int = SIGMA_LOOKBACK_BARS,
    tick: float = W.TICK,
) -> float | None:
    """F4-1: `alert_sigma_detail(...).sigma` -- the volatility at the alert, or None where the alert has fewer than
    two changes behind it **or** a zero dispersion (the reason is `alert_sigma_detail`'s; F-3). Unchanged in value
    from `31c507e`: every alert it returned a sigma for, it still does, bit for bit."""
    return alert_sigma_detail(day_closes, day_idx, decision, lookback=lookback, tick=tick).sigma


def sigma_drop_row(date_str: str, decision: int, reading: SigmaReading) -> dict[str, Any]:
    """One dropped alert for the record (F-3): its trading day, its alert minute (as minutes after 17:00 CT and as CT
    time), the reason and the counts behind it -- dates, times and counts only, never a price."""
    return {
        "date": str(date_str),
        "decision_slot_minutes": int(decision),
        "decision_ct": slot_ct(int(decision)),
        "reason": str(reading.reason),
        "n_bars": int(reading.n_bars),
        "n_changes": int(reading.n_changes),
        "n_nonzero_changes": int(reading.n_nonzero),
        "sessions_read": int(reading.sessions_read),
    }


def vendored_move_bar(o: np.ndarray, entry_bar: int, walk_end_bar: int) -> int | None:
    """Stage 2's vendored breakeven move bar (`walker.walk` / `fv3_rung_walk`): first present bar within 5 minutes
    of the first FV3 session open strictly after `entry_bar`, at or before `walk_end_bar`; None if none."""
    s = next((op for op in W.SESSION_OPENS if op > int(entry_bar)), None)
    if s is None:
        return None
    hi = min(s + 1 + W.BREAKEVEN_WINDOW, int(walk_end_bar) + 1, len(o))
    for x in range(s + 1, hi):
        if not math.isnan(float(o[x])):
            return int(x)
    return None


# --------------------------------------------------------------------------------------------- schedule side (H4-S)


def schedule_side_for(session: int, mark: int, *, seed: Any = None, part: int | None = None) -> int:
    """H4 section 15: naive coin's as-run schedule side drawn once per `(session, moment)` from `h4s_schedule_side`
    at `part=H4-S, history=0, seed_index=0, start=0, underlying=NQ, draw_kind=SIDE`. Returns +1 (long) or -1 (short).
    Tests may pass `seed=S.issue('h4_tests'), part=S.PARTS['H4-T']`."""
    sd = S.issue("h4s_schedule_side") if seed is None else seed
    pt = S.PARTS["H4-S"] if part is None else int(part)
    m = K.moment(int(session), int(mark), 0)
    key = K.seed_key(
        sd,
        "coin",
        part=pt,
        history=0,
        seed_index=0,
        start=0,
        underlying=K.UNDERLYING["NQ"],
        moment=m,
        draw_kind=K.SIDE,
    )
    u = float(K.uniforms(key, 1)[0])
    return 1 if u < 0.5 else -1


# --------------------------------------------------------------------------------------------- shared walk helper


def _walk_day_both_sides(
    o: np.ndarray,
    h: np.ndarray,
    l: np.ndarray,
    c: np.ndarray,
    entries: Sequence[tuple[int, int, int]],
    stop_ticks: int,
    rr_grid: Sequence[float],
    *,
    tick: float,
    rules: W.Rules,
    base_rules: W.Rules | None = None,
    costs: W.Costs | None = None,
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
    """Walk `(slot, fill_bar, side)` entries on one day for BOTH `side` (rule) and `-side` (mirror) at every R of
    `rr_grid` under `rules` (`walker.STAGE2` or window-shortened `STAGE2`). When `base_rules` is given and
    `rules.walk_end < base_rules.walk_end`, applies E-223's `window_flatten_trade` booking to any trade still open at
    the window's start."""
    n = len(entries)
    bl = W.brackets((int(stop_ticks),), rr_grid)
    if n == 0:
        empty = {k: np.zeros((0, len(bl)), dtype=np.int32) for k in ("kind", "exit", "mae", "gross")}
        return empty, empty

    fill_bars = np.array([int(fb) for _, fb, _ in entries], dtype=int)
    fill_prices = np.array([float(o[int(fb)]) for _, fb, _ in entries], dtype=float)
    sides = np.array([int(sd) for _, _, sd in entries], dtype=float)
    resting = np.zeros(n, dtype=bool)

    rule_res = W.walk(o, h, l, c, fill_bars, fill_prices, sides, resting, bl, tick=tick, rules=rules)
    mirr_res = W.walk(o, h, l, c, fill_bars, fill_prices, -sides, resting, bl, tick=tick, rules=rules)

    if base_rules is not None and int(rules.walk_end) < int(base_rules.walk_end):
        if W.walk_end(o, rules) == int(rules.walk_end):
            fb_win = T.flatten_bar(o, rules, base_rules)
            if fb_win is not None:
                S_int = int(stop_ticks)
                for idx in range(n):
                    fp = float(fill_prices[idx])
                    for res, sd_val in ((rule_res, int(sides[idx])), (mirr_res, -int(sides[idx]))):
                        fl = res["kind"][idx] == W.FLATTEN
                        if not fl.any():
                            continue
                        adverse = float(l[fb_win]) if sd_val > 0 else float(h[fb_win])
                        a = int(round(sd_val * (fp - adverse) / tick))
                        if a >= S_int:
                            res["kind"][idx, fl] = W.STOP
                            res["gross"][idx, fl] = -S_int
                            res["mae"][idx, fl] = S_int
                        else:
                            res["gross"][idx, fl] = -a - W.FLATTEN_SLIP_TICKS
                            res["mae"][idx, fl] = np.maximum(res["mae"][idx, fl], max(a, 0))
                        res["exit"][idx, fl] = fb_win

    return rule_res, mirr_res


def _format_cell_trades(
    rows: list[dict[str, Any]],
    stop_ticks: int,
    rr_grid: Sequence[float],
    fresh_rr: float,
    fee_micro_eq: float,
    tick_value: float,
    entry_ticks: float,
) -> pd.DataFrame:
    """Format walked offers into `resolved_coin.cell_trades`'s exact column order, types, and arithmetic."""
    if not rows:
        return pd.DataFrame()
    S_int = int(stop_ticks)
    td = float(tick_value)
    fee = float(fee_micro_eq)
    df = pd.DataFrame(rows)
    df = df.sort_values(["date", "entry_t", "decision_slot_minutes"], kind="stable").reset_index(drop=True)

    out = pd.DataFrame(
        {
            "date": df["date"].astype(str),
            "year": df["date"].astype(str).str[:4].astype(int),
            "decision_ct": df["decision_slot_minutes"].astype(int).map(slot_ct),
            "day_kind": df["day_kind"].astype(str),
            "decision_slot_minutes": df["decision_slot_minutes"].astype(int),
            "S": S_int,
            "stop_ticks": float(S_int),
            "entry_t": df["entry_t"].astype(float),
            "side": np.where(df["side_int"].astype(int) > 0, "long", "short"),
            "fee_micro_eq": fee,
        }
    )
    for R in rr_grid:
        kind = df[f"_k_{R:g}"].astype(int).to_numpy()
        ex = df[f"_x_{R:g}"].astype(float).to_numpy()
        mae = df[f"_a_{R:g}"].astype(float).to_numpy()
        gt = df[f"_g_{R:g}"].astype(float).to_numpy()
        gross = gt / S_int
        cost = (float(entry_ticks) * td + fee + np.array([float(W.EXIT_TICKS[int(k)]) for k in kind]) * td) / (
            S_int * td
        )
        out[f"r_{R:g}"] = gross - cost
        out[f"g_{R:g}"] = gross
        out[f"c_{R:g}"] = cost
        out[f"mae_{R:g}"] = mae / S_int
        out[f"exit_t_{R:g}"] = ex
        out[f"o_{R:g}"] = [W.KIND_CODE[int(k)] for k in kind]

    base = f"exit_t_{float(fresh_rr):g}"
    out["exit_t"] = out[base] if base in out else out[[f"exit_t_{R:g}" for R in rr_grid]].max(axis=1)
    ob = f"o_{float(fresh_rr):g}"
    out["flat"] = (out[ob] == "f") if ob in out else False
    return out.sort_values(["date", "entry_t"], kind="stable").reset_index(drop=True)


# --------------------------------------------------------------------------------------------- mode 1: naive coin (as-run)


@dataclass
class CoinBuildResult:
    """Outputs of `build_naive_coin_trades`: trades DataFrame in `resolved_coin.cell_trades` schema plus metadata."""

    trades: pd.DataFrame
    aux: pd.DataFrame            # aligned row-for-row with `trades`: time_limit, be_vendored, sigma, mirror gross per R
    counts: dict[str, Any]       # void counts, data-defect look-ahead count (rn-3), dropped sigma<2 count, etc.


def build_naive_coin_trades(
    dates: Sequence[str],
    day_kinds: Mapping[str, str],
    arrays_fn: Callable[[str], tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]],
    day_context_fn: Callable[[date, int], T.DayContext],
    *,
    fee_micro_eq: float,
    tick: float = W.TICK,
    tick_value: float = 0.5,
    entry_ticks: float = 1.0,
    stop_ticks: int = P16_STOP_TICKS,
    rr_grid: Sequence[float] = RR_GRID,
    fresh_rr: float = 1.5,
    latency: int = COIN_LATENCY,
    marks: Sequence[int] | None = None,
    seed: Any = None,
    part: int | None = None,
    data_void_fn: Callable[[date], tuple[str, ...]] | None = None,
    require_overnight_guard: bool = True,
) -> CoinBuildResult:
    """Build H4's unchained naive-coin offers across `dates` (search years only).

    Every mark in `marks` (default: `all_marks()` = 0..1325 step 5, admission T7 off) at latency `L = 5` goes through
    `triggers.admit` with Q-166's void calendar & E-223's news convention, is walked by `walker.STAGE2` (FV3 breakeven
    move ON) at all 12 Rs of `rr_grid`, and takes its as-run side once per `(session, moment)` from `h4s_schedule_side`.
    """
    if require_overnight_guard:
        T.require_overnight("H4 naive coin")
    mark_list = list(all_marks() if marks is None else marks)
    sorted_dates = [str(d) for d in dates]
    base_rules = W.STAGE2
    costs = W.Costs(fee_micro_eq=float(fee_micro_eq), tick_value=float(tick_value), market_entry_ticks=float(entry_ticks))

    # Load all day arrays once (also needed for causal cross-session alert_sigma_cross_session)
    day_arrs = [arrays_fn(d) for d in sorted_dates]
    day_closes = [arr[3] for arr in day_arrs]

    rows: list[dict[str, Any]] = []
    aux_rows: list[dict[str, Any]] = []
    refused_counts: dict[str, int] = {}
    days_voided = 0
    days_data_defect_lookahead = 0
    offers_clock_grid = 0
    offers_admitted = 0
    offers_unfilled = 0
    offers_dropped_sigma = 0
    offers_dropped_sigma_zero = 0
    sigma_rms_fallback = 0
    dropped_sigma_rows: list[dict[str, Any]] = []
    data_defect_dates: list[str] = []
    limit_differs_dates: list[str] = []
    limit_differs_from_last_bar = 0

    for sess_idx, d_str in enumerate(sorted_dates):
        d_obj = date.fromisoformat(d_str)
        ctx = day_context_fn(d_obj, sess_idx)
        if data_void_fn is not None:
            dv = data_void_fn(d_obj)
            if any(r.startswith("no_bar_at_") or r in ("early_end", "data_defect") for r in dv):
                days_data_defect_lookahead += 1
                data_defect_dates.append(d_str)
        if ctx.void or ctx.fomc:
            days_voided += 1

        raw_offers = [
            T.Offer(
                source="naive_coin",
                session=sess_idx,
                decision=int(m),
                sub=0,
                alert=int(m),
                live=int(m) + int(latency),
                entry=T.MARKET,
            )
            for m in mark_list
        ]
        offers_clock_grid += len(raw_offers)
        kept, refused = T.admit(raw_offers, ctx)
        for _, why in refused:
            refused_counts[why] = refused_counts.get(why, 0) + 1
        if not kept:
            continue
        offers_admitted += len(kept)

        o, h, l, c = day_arrs[sess_idx]
        last_b = W.last_bar(o)
        if last_b is None:
            offers_unfilled += len(kept)
            continue

        # Group admitted offers by effective walk rules (`triggers.rules_for` -> window-shortened STAGE2 or STAGE2)
        by_rules: dict[int, tuple[W.Rules, list[tuple[int, int, int, int, float]]]] = {}
        for off in kept:
            er = T.rules_for(int(off.live), ctx, base_rules)
            # Clock/calendar time limit (never from day's last bar; section 7 breakeven row)
            clock_limit = int(er.walk_end)
            if last_b < clock_limit:
                limit_differs_from_last_bar += 1
                limit_differs_dates.append(d_str)
            eff_end = W.walk_end(o, er)
            if eff_end is None:
                offers_unfilled += 1
                continue
            # Fill at first present bar opening at or after off.live (index >= live + 1) and < eff_end
            lo = int(off.live) + 1
            if lo >= eff_end:
                offers_unfilled += 1
                continue
            js = np.arange(lo, eff_end)
            pres = js[~np.isnan(o[js])]
            if not pres.size:
                offers_unfilled += 1
                continue
            fb = int(pres[0])
            sr = alert_sigma_detail(day_closes, sess_idx, int(off.decision), tick=tick)
            sig = sr.sigma
            if sig is None:
                if sr.reason == SIGMA_ZERO:
                    offers_dropped_sigma_zero += 1
                else:
                    offers_dropped_sigma += 1
                dropped_sigma_rows.append(sigma_drop_row(d_str, int(off.decision), sr))
                continue
            sigma_rms_fallback += int(sr.rms_fallback)
            sd = schedule_side_for(sess_idx, int(off.decision), seed=seed, part=part)
            grp = by_rules.setdefault(clock_limit, (er, []))
            grp[1].append((int(off.decision), fb, sd, clock_limit, sig))

        dk = str(day_kinds.get(d_str, "b" if ctx.bls else "n"))
        for clock_limit, (er, items) in sorted(by_rules.items()):
            entries = [(dec, fb, sd) for dec, fb, sd, _, _ in items]
            rule_res, mirr_res = _walk_day_both_sides(
                o, h, l, c, entries, stop_ticks, rr_grid, tick=tick, rules=er, base_rules=base_rules, costs=costs
            )
            eff_end = int(W.walk_end(o, er) or clock_limit)
            for idx_in, (dec, fb, sd, clim, sig) in enumerate(items):
                rec: dict[str, Any] = {
                    "date": d_str,
                    "day_kind": dk,
                    "decision_slot_minutes": dec,
                    "entry_t": fb,
                    "side_int": sd,
                }
                aux: dict[str, Any] = {
                    "date": d_str,
                    "entry_t": float(fb),
                    "decision_slot_minutes": dec,
                    "session": sess_idx,
                    "time_limit": clim,
                    "be_open": TB.move_bar(fb),
                    "be_vendored": vendored_move_bar(o, fb, eff_end),
                    "sigma": float(sig),
                }
                for b_idx, R in enumerate(rr_grid):
                    rec[f"_k_{R:g}"] = int(rule_res["kind"][idx_in, b_idx])
                    rec[f"_x_{R:g}"] = int(rule_res["exit"][idx_in, b_idx])
                    rec[f"_a_{R:g}"] = int(rule_res["mae"][idx_in, b_idx])
                    rec[f"_g_{R:g}"] = int(rule_res["gross"][idx_in, b_idx])
                    aux[f"mirr_g_{R:g}"] = float(mirr_res["gross"][idx_in, b_idx])
                    aux[f"rule_g_{R:g}"] = float(rule_res["gross"][idx_in, b_idx])
                rows.append(rec)
                aux_rows.append(aux)

    trades = _format_cell_trades(rows, stop_ticks, rr_grid, fresh_rr, fee_micro_eq, tick_value, entry_ticks)
    if aux_rows:
        aux_df = pd.DataFrame(aux_rows).sort_values(["date", "entry_t", "decision_slot_minutes"], kind="stable")
        aux_df = aux_df.sort_values(["date", "entry_t"], kind="stable").reset_index(drop=True)
    else:
        aux_df = pd.DataFrame()

    multi_moment_alerts = (
        int((trades.groupby(["date", "decision_slot_minutes"]).size() >= 2).sum()) if len(trades) else 0
    )
    counts = {
        "days_total": len(sorted_dates),
        "days_voided": days_voided,
        "days_data_defect_lookahead": days_data_defect_lookahead,
        "offers_clock_grid": offers_clock_grid,
        "offers_admitted": offers_admitted,
        "offers_filled": int(len(trades)),
        "offers_unfilled": offers_unfilled,
        "offers_dropped_sigma_lt_2": offers_dropped_sigma,
        # F-3 (Q-188b): zero dispersion kept apart from the declared "fewer than two changes" drop
        "offers_dropped_sigma_zero": offers_dropped_sigma_zero,
        "sigma_rms_fallback": sigma_rms_fallback,
        "dropped_sigma_rows": dropped_sigma_rows,
        "limit_differs_from_last_bar": limit_differs_from_last_bar,
        # F-6 (Q-188b): the dates behind the beside counts, so a year's count is computed, never printed as 0
        "limit_differs_dates": limit_differs_dates,
        "data_defect_lookahead_dates": data_defect_dates,
        "multi_moment_alerts": multi_moment_alerts,
        "refused_by_reason": dict(sorted(refused_counts.items())),
    }
    return CoinBuildResult(trades=trades, aux=aux_df, counts=counts)


# --------------------------------------------------------------------------------------------- mode 2: P-16 / I-5 check


def build_p16_i5_trades(
    days_df: pd.DataFrame,
    arrays_fn: Callable[[str], tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]],
    offered_marks: Sequence[int],
    coins: Mapping[tuple[str, int], int],
    *,
    fee_micro_eq: float,
    tick: float = W.TICK,
    tick_value: float = 0.5,
    entry_ticks: float = 1.0,
    stop_ticks: int = P16_STOP_TICKS,
    rr_grid: Sequence[float] = RR_GRID,
    fresh_rr: float = 1.5,
    bls_cut: int = BLS_CUT_SLOT,
    release_clear: int = RELEASE_CLEAR_SLOT,
    walk_day_kinds: Sequence[str] = ("n", "b"),
) -> pd.DataFrame:
    """H4 section 16 (I-5): run the coin source's unchained offer list in P-16's exact mode:
    - A1's walked days (`day_kind in ('n', 'b')`), Q-166 void calendar OFF;
    - A3's 07:30 CT report-day cut + D-533's 07:35 CT release-minute cut;
    - P-16's registered offered marks (from `h4_registered_constants.csv`), latency `L = 0`;
    - P-16's `coin_table` sides (`coins[(date, mark)]`);
    - walked by `extended.walker.STAGE2` (FV3 breakeven move ON) at all 12 Rs of `rr_grid`;
    - formatted in `resolved_coin.cell_trades`' exact columns (so `rc_dev_test.trades_hash` matches P-16 bit for bit!).
    """
    d_sub = days_df[days_df["day_kind"].astype(str).isin(set(walk_day_kinds))].copy()
    d_sub["date"] = d_sub["date"].astype(str)
    d_sub = d_sub.sort_values("date", kind="stable").reset_index(drop=True)
    marks_sorted = sorted(int(m) for m in offered_marks)
    bl = W.brackets((int(stop_ticks),), rr_grid)
    rules = W.STAGE2

    rows: list[dict[str, Any]] = []
    for _, dr in d_sub.iterrows():
        d_str = str(dr["date"])
        dk = str(dr["day_kind"])
        o, h, l, c = arrays_fn(d_str)
        eff_end = W.walk_end(o, rules)
        if eff_end is None:
            continue
        day_marks = [m for m in marks_sorted if not (dk == "b" and m < int(bls_cut))]
        if not day_marks:
            continue
        # Latency 0 market fill: first present bar opening at or after mark (`index >= mark + 1`) and `< eff_end`
        fbs = W.market_fill_bars(o, day_marks, rules=rules)
        entries: list[tuple[int, int, int]] = []
        for m, fb in zip(day_marks, fbs):
            if int(fb) == W.NONE:
                continue
            entries.append((int(m), int(fb), int(coins[(d_str, int(m))])))
        if not entries:
            continue

        fill_bars = np.array([fb for _, fb, _ in entries], dtype=int)
        fill_prices = np.array([float(o[fb]) for _, fb, _ in entries], dtype=float)
        sides = np.array([sd for _, _, sd in entries], dtype=float)
        res = W.walk(o, h, l, c, fill_bars, fill_prices, sides, np.zeros(len(entries), dtype=bool), bl, tick=tick, rules=rules)
        for idx_in, (m, fb, sd) in enumerate(entries):
            rec: dict[str, Any] = {
                "date": d_str,
                "day_kind": dk,
                "decision_slot_minutes": m,
                "entry_t": fb,
                "side_int": sd,
            }
            for b_idx, R in enumerate(rr_grid):
                rec[f"_k_{R:g}"] = int(res["kind"][idx_in, b_idx])
                rec[f"_x_{R:g}"] = int(res["exit"][idx_in, b_idx])
                rec[f"_a_{R:g}"] = int(res["mae"][idx_in, b_idx])
                rec[f"_g_{R:g}"] = int(res["gross"][idx_in, b_idx])
            rows.append(rec)

    raw = _format_cell_trades(rows, stop_ticks, rr_grid, fresh_rr, fee_micro_eq, tick_value, entry_ticks)
    if raw.empty:
        return raw
    # D-533 release-minute cut (`resolved_coin.drop_release_minute`)
    drop = (raw["day_kind"].astype(str) == "b") & (raw["decision_slot_minutes"].astype(int) < int(release_clear))
    return raw[~drop].reset_index(drop=True)


__all__ = [
    "P16_STOP_TICKS",
    "COIN_LATENCY",
    "MARK_STEP",
    "SESSION_END",
    "RR_GRID",
    "SIGMA_LOOKBACK_BARS",
    "RELEASE_CLEAR_SLOT",
    "BLS_CUT_SLOT",
    "all_marks",
    "slot_ct",
    "alert_sigma_cross_session",
    "alert_sigma_detail",
    "SigmaReading",
    "SIGMA_OK",
    "SIGMA_LT_2",
    "SIGMA_ZERO",
    "SIGMA_REASONS",
    "sigma_drop_row",
    "vendored_move_bar",
    "schedule_side_for",
    "CoinBuildResult",
    "build_naive_coin_trades",
    "build_p16_i5_trades",
]
