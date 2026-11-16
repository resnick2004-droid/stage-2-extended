"""EXPLORATORY and descriptive (D-607): the P&F catapult's contract-fit count -- one row per setup and the summary
readings of D-607 (8). Pure functions; `scripts/pf_fit.py` reads NQ's development bars and writes the files.

**No outcome is read.** Every field of a setup row is fixed by the end of its trigger bar (the engine's setup, the
alert and trigger bars' times on the trading-day clock and the latency measures, which compare the trigger bar with
the alert bar). There is no P&L, no seed and no money.

**The clock** (`collect_core.c_slot`, `s3_event_kinds.bar_end_slots`): a bar's END in minutes after 17:00 CT (1 ..
1440; Databento stamps a bar at its start, it ends 60 s later). A setup's window is the one of
`resolved_coin.WINDOWS` ([start, end) on that clock: all [0, 1330), asia [60, 540), london [540, 930), us [930, 1330))
holding its trigger bar's end slot; a trigger ending in [1330, 1440] (15:10 to 17:00 CT) is outside Topstep's hours:
excluded from supply, counted beside as the window `outside`. A setup's `window` field names its narrowest window
(`asia`, `london`, `us`; `all` for a trigger ending 17:01 to 18:00 CT, inside `all` but none of the three; `outside`).

**Latency (D-607 (5), D-266, D-589)**: minutes from alert to trigger = (trigger bar's end - alert bar's end) / 60, 0
when the trigger prints on the alert bar; `missed_L5`: the trigger bar ends at or before the alert bar's end + 5
minutes (bars are minute-aligned, so the trigger printed before an order placed 5 minutes after the alert);
`on_alert_bar`: the trigger is on the alert bar itself (missed even at L = 0).

**The definitions** (D-607 (9): 4 boxes x (2 x 2 catapult readings + 1 plain) = 20): for the catapult, `r7_low` (the
fixed reading: 7 max counted from R, the pullback above the pattern low), `r8_low` (7 max from the breakout box),
`r7_retest` and `r8_retest` (the pullback above R); `plain` for the triple top / bottom. Each row of the summary is one
(box, kind, choice, window): kinds `bull_catapult`, `bear_catapult`, their sum `catapult`, `triple_top_buy`,
`triple_bottom_sell` and their sum `plain`.

**Setups per session**: per trading day of the development day list (the store's days, 2020-01-01 to 2026-07-16), a
setup counted on its trigger bar's trading day, a day with none a zero; per calendar year of the trading day.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from propedge.research import pnf
from propedge.research import resolved_coin as rc

DECISION = "D-607"
RESULT = "pf_fit"
RESULT_SETUPS = "pf_fit_setups"
FAMILY_ID = f"{DECISION}:pf_fit"
MARKET = "NQ"
DEV_START = "2020-01-01"
DEV_END = "2026-07-16"
LATENCY_MIN = 5                            # D-607 (5): L = 5 minutes
STOP_LINES = (37.5, 40.0)                  # P-16's 37.5 points (D-547) and 40
QUANTILES = (5, 25, 50, 75, 95)
WINDOWS = dict(rc.WINDOWS)                 # all [0, 1330), asia [60, 540), london [540, 930), us [930, 1330)
HOURS_END = WINDOWS["all"][1]              # 1330: 15:10 CT
SUB_WINDOWS = ("asia", "london", "us")
SUMMARY_WINDOWS = ("all", "asia", "london", "us", "outside")
#: the catapult's 2 x 2 readings: (7-max flag, pullback flag); `r7_low` is D-607's fixed reading
CATAPULT_CHOICES = {"r7_low": ("max7_from_R", "above_pattern_low"),
                    "r8_low": ("max7_from_breakout_box", "above_pattern_low"),
                    "r7_retest": ("max7_from_R", "retest"),
                    "r8_retest": ("max7_from_breakout_box", "retest")}
FIXED_CHOICE = "r7_low"
PLAIN_CHOICE = "plain"
CHOICES = tuple(CATAPULT_CHOICES) + (PLAIN_CHOICE,)
GROUPS = {pnf.BULL_CATAPULT: (pnf.BULL_CATAPULT,), pnf.BEAR_CATAPULT: (pnf.BEAR_CATAPULT,),
          "catapult": pnf.CATAPULTS, pnf.TRIPLE_TOP: (pnf.TRIPLE_TOP,), pnf.TRIPLE_BOTTOM: (pnf.TRIPLE_BOTTOM,),
          "plain": pnf.PLAINS}
CHOICE_TEXT = {
    "r7_low": "the catapult, D-607's fixed reading: H(k) <= R + 7b (7 max from the old resistance), L(k+1) > L(k-1) "
              "(above the pattern low); bears mirrored",
    "r8_low": "the catapult: H(k) <= R + 8b (7 max from the breakout box, beside), L(k+1) > L(k-1)",
    "r7_retest": "the catapult: H(k) <= R + 7b, L(k+1) > R (the retest reading, beside)",
    "r8_retest": "the catapult: H(k) <= R + 8b, L(k+1) > R (both alternates)",
    "plain": "the plain triple top buy / triple bottom sell (the PDF's benchmark): entry R + b, stop L(k-1) - b, the "
             "4-column count"}


def definitions() -> list[dict[str, Any]]:
    """D-607 (9)'s 20 definitions: every box with each catapult reading (both sides) and the plain triple (both)."""
    return [{"box_points": float(b), "choice": c, "definition": CHOICE_TEXT[c], "fixed": c in (FIXED_CHOICE,)}
            for b in pnf.BOXES for c in CHOICES]


def _ct(ts_end: np.ndarray) -> pd.Series:
    return pd.to_datetime(pd.Series(np.asarray(ts_end, dtype="int64")), unit="s", utc=True).dt.tz_convert(
        "America/Chicago")


def window_of(slot: int) -> str:
    """The narrowest window holding a trigger bar's end slot (`outside` from 1330 on)."""
    s = int(slot)
    if s >= HOURS_END:
        return "outside"
    for w in SUB_WINDOWS:
        lo, hi = WINDOWS[w]
        if lo <= s < hi:
            return w
    return "all"


def in_window(window: Sequence[str], w: str) -> np.ndarray:
    """Which rows (by their narrowest `window`) lie in summary window `w`."""
    a = np.asarray(window, dtype=object)
    if w == "all":
        return a != "outside"
    return a == w


def setup_rows(bars: pd.DataFrame, box: float, *, result: Mapping[str, Any] | None = None) -> pd.DataFrame:
    """One row per setup of `pnf.scan` on `bars` (columns ts, day, contract, high, low, close; in ts order): prices in
    points, the alert and trigger bars' ends (CT and clock slot), the window, the latency measures and the flags."""
    from propedge.research.s3_event_kinds import bar_end_slots

    if result is None:
        result = pnf.scan(bars["high"].to_numpy(), bars["low"].to_numpy(), bars["close"].to_numpy(),
                          bars["contract"].astype(str).to_numpy() if "contract" in bars.columns else None, box=box)
    S = list(result["setups"])
    cols = ["date", "alert_date", "kind", "side", "box_points", "choice_fixed", "r7_low", "r8_low", "r7_retest",
            "r8_retest", "contract", "chart", "column_k", "alert_end_ct", "trigger_end_ct", "alert_end_slot",
            "trigger_end_slot", "window", "in_hours", "level_R", "entry_T", "stop", "D_points", "D_over_b", "target",
            "target_R", "pattern_extreme", "column_k_extreme", "pullback_extreme", "max7_from_R",
            "max7_from_breakout_box", "above_pattern_low", "retest", "minutes_alert_to_trigger", "on_alert_bar",
            "missed_L5", "alert_bar", "trigger_bar"]
    if not S:
        return pd.DataFrame(columns=cols)
    ts = bars["ts"].to_numpy(dtype="int64")
    day = bars["day"].astype(str).to_numpy()
    con = bars["contract"].astype(str).to_numpy() if "contract" in bars.columns else np.array([""] * len(bars))
    ia = np.array([s["alert_bar"] for s in S], dtype=np.int64)
    it = np.array([s["trigger_bar"] for s in S], dtype=np.int64)
    a_end, t_end = ts[ia] + 60, ts[it] + 60
    t_slot = bar_end_slots(ts[it])
    a_slot = bar_end_slots(ts[ia])
    tick = pnf.TICK
    bt = int(result["box_ticks"])
    df = pd.DataFrame({
        "date": day[it], "alert_date": day[ia], "kind": [s["kind"] for s in S], "side": [int(s["side"]) for s in S],
        "box_points": bt * tick, "contract": con[it], "chart": [int(s["chart"]) for s in S],
        "column_k": [int(s["column"]) for s in S],
        "alert_end_ct": _ct(a_end).dt.strftime("%Y-%m-%d %H:%M").to_numpy(),
        "trigger_end_ct": _ct(t_end).dt.strftime("%Y-%m-%d %H:%M").to_numpy(),
        "alert_end_slot": a_slot.astype(int), "trigger_end_slot": t_slot.astype(int)})
    for f in pnf.PRICE_FIELDS:
        v = [s[f] for s in S]
        df[f] = [np.nan if x is None else x * tick for x in v]
    df = df.rename(columns={"level": "level_R", "entry": "entry_T", "D": "D_points"})
    df["D_over_b"] = np.array([s["D"] for s in S], dtype=float) / bt
    df["target_R"] = [pnf.target_r(s) for s in S]
    flags = {}
    for f in ("max7_from_R", "max7_from_breakout_box", "above_pattern_low", "retest"):
        flags[f] = np.array([s[f] is True for s in S])
        df[f] = pd.array([None if s[f] is None else bool(s[f]) for s in S], dtype="boolean")
    df["window"] = [window_of(x) for x in t_slot]
    df["in_hours"] = df["window"] != "outside"
    df["minutes_alert_to_trigger"] = (t_end - a_end) / 60.0
    df["on_alert_bar"] = it == ia
    df["missed_L5"] = t_end <= a_end + 60 * LATENCY_MIN
    cat = df["kind"].isin(pnf.CATAPULTS).to_numpy()
    for c, (f7, fp) in CATAPULT_CHOICES.items():
        df[c] = cat & flags[f7] & flags[fp]
    df["choice_fixed"] = np.where(cat, df["r7_low"], True)
    df["alert_bar"], df["trigger_bar"] = ia, it
    return df[cols]


def choice_mask(rows: pd.DataFrame, group: str, choice: str) -> np.ndarray:
    kinds = GROUPS[group]
    m = rows["kind"].isin(kinds).to_numpy()
    if choice == PLAIN_CHOICE:
        return m & rows["kind"].isin(pnf.PLAINS).to_numpy()
    return m & rows["kind"].isin(pnf.CATAPULTS).to_numpy() & rows[choice].astype(bool).to_numpy()


def _supply(dates: Sequence[str], sessions: Sequence[str]) -> dict[str, Any]:
    s = pd.Index([str(d) for d in sessions])
    per = pd.Series(0, index=s, dtype=np.int64)
    vc = pd.Series([str(d) for d in dates], dtype=object).value_counts()
    vc = vc[vc.index.isin(s)]
    per.loc[vc.index] = vc.to_numpy()
    x = per.to_numpy()
    n = len(x)
    return {"sessions": n, "setups": int(x.sum()), "per_session_mean": float(x.mean()) if n else np.nan,
            "per_session_median": float(np.median(x)) if n else np.nan,
            "share_sessions_ge1": float((x >= 1).mean()) if n else np.nan,
            "share_sessions_ge5": float((x >= 5).mean()) if n else np.nan}


def _q(x: np.ndarray, name: str) -> dict[str, float]:
    if not len(x):
        return {f"{name}_q{q:02d}": np.nan for q in QUANTILES}
    v = np.percentile(x, QUANTILES)
    return {f"{name}_q{q:02d}": float(a) for q, a in zip(QUANTILES, v)}


def _spread(sub: pd.DataFrame, box: float) -> dict[str, Any]:
    D = sub["D_points"].to_numpy(float)
    R = sub["target_R"].to_numpy(float)
    m = sub["minutes_alert_to_trigger"].to_numpy(float)
    n = len(sub)
    out: dict[str, Any] = {"n": n}
    out.update(_q(D, "D"))
    out.update({"D_min": float(D.min()) if n else np.nan, "D_max": float(D.max()) if n else np.nan,
                "D_over_b_median": float(np.median(D / box)) if n else np.nan})
    for line in STOP_LINES:
        out[f"share_D_le_{line:g}"] = float((D <= line + 1e-9).mean()) if n else np.nan
    out.update(_q(R, "target_R"))
    out["share_target_R_le_0"] = float((R <= 0).mean()) if n else np.nan
    out.update(_q(m, "minutes_alert_to_trigger"))
    out["minutes_alert_to_trigger_mean"] = float(m.mean()) if n else np.nan
    out["share_on_alert_bar"] = float(sub["on_alert_bar"].astype(bool).mean()) if n else np.nan
    out["share_missed_L5"] = float(sub["missed_L5"].astype(bool).mean()) if n else np.nan
    return out


def summary(rows: pd.DataFrame, sessions: Sequence[str]) -> pd.DataFrame:
    """D-607 (8)'s readings: one `reading` row per (box, kind, choice, window) -- supply per session, D, target R and
    latency -- and one `year` row per (box, kind, choice, window, year) with the supply per session that year."""
    sessions = [str(d) for d in sessions]
    years = sorted({d[:4] for d in sessions})
    by_year = {y: [d for d in sessions if d[:4] == y] for y in years}
    out: list[dict[str, Any]] = []
    for box in pnf.BOXES:
        rb = rows[np.isclose(rows["box_points"].astype(float), box)]
        for group in GROUPS:
            choices = (PLAIN_CHOICE,) if group in (pnf.TRIPLE_TOP, pnf.TRIPLE_BOTTOM, "plain") else tuple(
                CATAPULT_CHOICES)
            for choice in choices:
                sub0 = rb[choice_mask(rb, group, choice)]
                for w in SUMMARY_WINDOWS:
                    sub = sub0[in_window(sub0["window"], w)]
                    head = {"section": "reading", "box_points": box, "kind": group, "choice": choice,
                            "fixed": choice in (FIXED_CHOICE, PLAIN_CHOICE), "window": w,
                            "supply": w != "outside"}
                    out.append({**head, **_supply(sub["date"], sessions), **_spread(sub, box)})
                    for y in years:
                        sy = sub[sub["date"].astype(str).str[:4] == y]
                        out.append({**head, "section": "year", "year": int(y), **_supply(sy["date"], by_year[y])})
    return pd.DataFrame(out)


def beside_rows(scans: Mapping[float, Mapping[str, Any]], restart_days: Mapping[float, Sequence[str]]
                ) -> list[dict[str, Any]]:
    """Per box: the chart's restarts (the rolls) and the engine's counts beside (alerts untriggered, lost at a restart
    or open at the series' end; catapult candidates and their rejections)."""
    out = []
    for box, s in scans.items():
        c = s["counts"]
        row = {"section": "beside", "box_points": float(box), "restarts": len(s["restarts"]),
               "restart_days": ";".join(restart_days.get(box, [])), "columns": len(s["columns"]),
               "signals": len(s["signals"])}
        for k in pnf.SIGNALS:
            row[f"signals_{k}"] = int(sum(1 for x in s["signals"] if x["kind"] == k))
        for kind in pnf.KINDS:
            for what in ("untriggered", "lost_at_restart", "open_at_end"):
                row[f"{what}_{kind}"] = int(c.get(f"{what}_{kind}", 0))
        for kind in pnf.CATAPULTS:
            for what in ("candidates", "rejected_7max", "rejected_new_extreme"):
                row[f"{what}_{kind}"] = int(c.get(f"{what}_{kind}", 0))
        row["first_column_waits_both"] = int(c.get("first_column_waits_both", 0))
        out.append(row)
    return out


def identity_problems(rows: pd.DataFrame) -> list[str]:
    """D-607 (4)'s derivation and the bracket's construction, re-read on the rows (the engine already raised on any
    violation; this is the file's own check)."""
    out = []
    if not len(rows):
        return out
    b = rows["box_points"].astype(float)
    D = rows["D_points"].astype(float)
    tol = 1e-9
    if (D < 5 * b - tol).any():
        out.append(f"{int((D < 5 * b - tol).sum())} setups with D < 5b")
    side = rows["side"].astype(float)
    if not np.allclose(side * (rows["entry_T"] - rows["stop"]), D):
        out.append("D is not side x (T - stop)")
    cat = rows["kind"].isin(pnf.CATAPULTS)
    rc_ = cat & (rows["retest"] == True)  # noqa: E712 (a nullable flag: NA on plain setups)
    r7 = rc_ & (rows["max7_from_R"] == True)  # noqa: E712
    if (D[r7] > 8 * b[r7] + tol).any():
        out.append("a retest setup with the fixed 7-max has D > 8b")
    if (D[rc_] > 9 * b[rc_] + tol).any():
        out.append("a retest setup has D > 9b")
    cc = rows[cat]
    if len(cc) and not np.allclose(cc["entry_T"], cc["column_k_extreme"] + cc["side"] * cc["box_points"]):
        out.append("a catapult's T is not H(k) + b (L(k) - b)")
    if len(cc) and not np.allclose(cc["D_points"], cc["side"] * (cc["column_k_extreme"] - cc["pullback_extreme"])
                                   + 2 * cc["box_points"]):
        out.append("a catapult's D is not (H(k) - L(k+1)) + 2b")
    pp = rows[~cat]
    if len(pp) and not np.allclose(pp["D_points"], pp["side"] * (pp["level_R"] - pp["pullback_extreme"])
                                   + 2 * pp["box_points"]):
        out.append("a plain triple's D is not (R - L(k-1)) + 2b")
    if len(pp) and not np.allclose(pp["entry_T"], pp["level_R"] + pp["side"] * pp["box_points"]):
        out.append("a plain triple's entry is not R + b")
    if (rows["minutes_alert_to_trigger"] < 0).any():
        out.append("a trigger before its alert")
    for c in CATAPULT_CHOICES:
        if (rows[c] & ~cat).any():
            out.append(f"{c} holds a plain setup")
    if (rows["r7_retest"] & ~rows["r7_low"]).any() or (rows["r7_low"] & ~rows["r8_low"]).any():
        out.append("the readings do not nest (retest within above-the-low; R + 7b within R + 8b)")
    return out


__all__ = ["DECISION", "RESULT", "RESULT_SETUPS", "FAMILY_ID", "MARKET", "DEV_START", "DEV_END", "LATENCY_MIN",
           "STOP_LINES", "QUANTILES", "WINDOWS", "HOURS_END", "SUB_WINDOWS", "SUMMARY_WINDOWS", "CATAPULT_CHOICES",
           "FIXED_CHOICE", "PLAIN_CHOICE", "CHOICES", "GROUPS", "CHOICE_TEXT", "definitions", "window_of", "in_window",
           "setup_rows", "choice_mask", "summary", "beside_rows", "identity_problems"]
