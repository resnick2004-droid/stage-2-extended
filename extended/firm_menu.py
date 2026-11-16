"""RD-01's menu (`prereg/RD-01_firm_contracts.md` 10.1 items 3, 4, 5, 10 and 11; 9.3's last line): a **declared light
step on the run's own written files** (`results/fc_reading.csv`, `results/fc_gate.csv`), never on the bars -- every
input it reads is in them: the paired card (P and the guarded measures, by block), the mechanics' counts and the
per-start rows (the journey variables and 10.1 item 6's fields). `scripts/rd01_reading.py` runs it once its first two
files are written, and writes `results/fc_menu.csv`. It draws nothing.

**Sections of the menu file:**

* `menu` -- each run's row (TS's references, every plan's corners and one-at-a-time runs), verdict arm the headline and
  point beside: P under the plan and under TS on the same starts (`paired` / `card`), their difference and side, on all
  starts (the headline), the early and late blocks and each start year (P from the long replays' month-end nets, a
  start-year reading beside); every row carries its labels (`LABELS`: U-3's upper bounds, the gaps of 4.7 that touch
  it, 4.8's open question, 16's open written questions, at QP its request rule) and the moot checks and conduct counts
  of 9.3 from the run's own counts.
* `flags` -- 10.1 items 5 and 11, mechanical: "depends on its unread terms" (a plan whose two corners lie on opposite
  sides of TS on P), "depends on its request rule" (Quick Pay's two request readings on P-16 on opposite sides of TS),
  "not stable across blocks" (P or a guarded measure whose paired difference has opposite signs on the early and late
  blocks), "no effect on these trades" (a plan whose daily cash equals TS's on every start within 252 sessions). E-015's
  limits flag nothing: none was approved before the run's commit (the menu says so).
* `distribution` -- item 3: each per-start measure's p10, p50, p90 and mean over start days, with 10.2's reading on the
  plan's own series (unpaired), by block at the measure's horizon.
* `variance_share` -- item 3's S6 form: across the plans' runs on one stream and arm, the start day's share of the
  variance of each measure (the within-run variance over starts against the variance of the runs' means).
* `paired_more` -- item 4 for every per-start measure of items 1 and 2 the month-end nets do not already pair: plan less
  TS on the same starts, by block at the measure's horizon -- the difference's p10, p50, p90; the shares better, equal
  and worse (each measure's own direction); the mean with 10.2's reading, its window count and minimum detectable
  difference; the coverage label where the run computed that setting.
* `evenness` -- item 10: each run's P against each evenness measure's mean (E-015's menu form, as points).
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from extended import firm_uncertainty as FU
from extended import user_measures as M

STATUS = "described, not carried"
BLOCKS = ("all", "early", "late")
ARMS = ("verdict", "point")
E015 = ("E-015's limits: none approved before the run's commit -- the menu is read without their flags (10.1 item 11); "
        "a limit approved later is an exploratory reading, reported apart")
GUARDED = ("S1", "S3a", "S3b", "S3c", "S4a", "S4b", "S5a", "S5b", "S5c")

#: the labels each plan's rows carry (10.1 item 11): U-3's upper bounds, the gaps of 4.7, 4.8's open question, the
#: firm's written questions while open (16); the request rule is added at QP per row
LABELS: dict[str, tuple[str, ...]] = {
    "TS": ("the reference: P-14's and P-16's registered rows (4.1)", "G-6: the tables solved for this contract",
           "G-13: payouts in holiday hours and Topstep's live move as in every registered row",
           "G-11: today's terms on every start"),
    "LU": ("U-3: Lucid's funded monthly fee and payout fee read at $0 -- its money figures an upper bound in them",
           "G-4: the live move ends the accounts, nothing credited beyond the reach read (5.2)",
           "G-5: Lucid's per-trade costs at TS's schedule, conservative in this term (4.8)",
           "G-6: the tables solved for Topstep's contract", "G-11: today's terms on every start"),
    "DT": ("U-3: DayTraders' payout fee read at $0 -- its money figures an upper bound in it",
           "4.8's open question: whether DayTraders' listed commissions include exchange and NFA fees (both ends read)",
           "U-2: DayTraders' evaluation price read on a declared grid ($25 to $250)",
           "U-5: DayTraders' processing days read at the bracket of the other plans' verified lags",
           "G-5: any DayTraders fee beyond Topstep's decomposition left open",
           "G-6: the tables solved for Topstep's contract", "G-7: Lifetime billing not read",
           "G-8: the outsized-position clause priced by the denial ladder only; its tier the operator's (16)",
           "G-9: the consistency tolerance read strictly: a lower bound in that term",
           "G-11: today's terms on every start", "G-12: a paused account's later signals not re-dealt (counted)",
           "16: the written question to DayTraders.com (s.26 3.c, its commissions, its payout days) open"),
    "FP": ("U-3: Fast Pass's payout fee read at $0 -- its money figures an upper bound in it",
           "U-1: Fast Pass's price read at both ends of its listed prices", "G-2: the price-limit rule not modelled; its "
           "effect not bounded", "G-3: the tier-1 liquidation bracketed (5.5)", "G-4: the fifth request's live move "
           "(5.2)", "G-6: the tables solved for Topstep's contract", "G-10: dormancy offboarding not modelled "
           "(counted)", "G-11: today's terms on every start", "G-14: bracketing data releases not modelled",
           "16: the written question to TradeDay (multiple users making the same trades) open"),
    "QP": ("U-1: Quick Pay's price read at both ends of its listed prices",
           "G-1: the intraday peak bracketed from the trades' own outcomes (5.4)", "G-2: the price-limit rule not "
           "modelled; its effect not bounded", "G-3: the tier-1 liquidation bracketed (5.5)", "G-4: the $10,000 "
           "ceiling's live review (5.2)", "G-6: the tables solved for Topstep's contract", "G-10: dormancy "
           "offboarding not modelled (counted)", "G-11: today's terms on every start",
           "G-14: bracketing data releases not modelled",
           "16: the written question to TradeDay (multiple users making the same trades) open"),
}
REQUEST_RULE = {"every": "QP's request rule: every eligible close", "cadence": "QP's request rule: the reference's "
                "cadence (5.6)"}
#: 9.3's conduct counts each plan's rows carry (DT: the martingale rule; FP, QP: the 200-trades line)
CONDUCT = {"DT": ("martingale_per_account", "martingale_firm_wide", "martingale_accounts_per_account",
                  "martingale_accounts_firm_wide"),
           "FP": ("max_trades_session_account", "max_trades_session_across", "sessions_above_trade_line"),
           "QP": ("max_trades_session_account", "max_trades_session_across", "sessions_above_trade_line")}

#: the per-start measures items 3 and 4 read: (column, horizon in sessions, the better direction, days window or None)
MEASURES: tuple[tuple[str, int, str, int | None], ...] = (
    ("months_ahead", 63, "higher", None),
    ("first_pass", 126, "lower", 126), ("spent_before_first_pass", 126, "lower", None),
    ("first_payout", 126, "lower", 126), ("spent_before_first_payout", 126, "lower", None),
    ("break_even_day", 252, "lower", 252), ("fell_back", 252, "lower", None),
    ("deepest_fall_after_break_even", 252, "lower", None),
    ("share_months_positive", 252, "higher", None), ("longest_months_without_payout", 252, "lower", None),
    ("sd_monthly_net", 252, "lower", None), ("payouts_per_month", 252, "higher", None),
    ("payout_cash_per_month", 252, "higher", None), ("largest_month_share", 252, "lower", None),
    ("funded_activated", 252, "higher", None), ("funded_lost", 252, "lower", None),
    ("evaluations_bought", 252, "lower", None), ("fees_evaluations", 252, "lower", None),
    ("fees_activation", 252, "lower", None), ("fees_payout", 252, "lower", None), ("fees_pro", 252, "lower", None),
    ("payouts_count", 252, "higher", None), ("payouts_gross", 252, "higher", None),
    ("payouts_net", 252, "higher", None), ("trades_taken", 252, "higher", None),
    ("realised_risk", 252, "higher", None),
)
#: item 2's break-even shares by month, as per-start indicators (paired by month, 10.1 item 4)
BREAK_EVEN_BY = (1, 2, 3, 6, 9, 12)
HORIZON_OF_MONTH = {1: 63, 2: 63, 3: 63, 6: 126, 9: 252, 12: 252}
EVENNESS = ("share_months_positive", "longest_months_without_payout", "sd_monthly_net", "deepest_fall_after_break_even",
            "payouts_per_month", "largest_month_share")


def _num(x: Any) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return float("nan")
    return v


def _starts(reading: pd.DataFrame, section: str) -> pd.DataFrame:
    s = reading[(reading["section"] == section) & (reading["subsection"] == "start")].copy()
    for c in ("start_day", "observed"):
        s[c] = pd.to_numeric(s[c], errors="coerce").astype("Int64")
    return s


def _block_days(t: pd.DataFrame, block: str, h: int) -> set[int]:
    """The starts of `t` (one run and arm) in `block` at horizon `h`, as `u_select.block` chooses them (its years)."""
    from propedge.research import u_select as S

    obs = t["observed"].astype(int).to_numpy() >= int(h)
    day = t["start_day"].astype(int).to_numpy()
    year = t["start_date"].astype(str).str[:4].astype(int).to_numpy()
    if block == "all":
        m = obs
    elif block == "late":
        m = obs & (year >= int(S.JUDGED_FIRST_YEAR))
    else:
        e = year <= int(S.CHOICE_LAST_YEAR)
        last = int(day[e].max()) if e.any() else 0
        m = obs & e & (day <= last - int(h))
    return set(int(x) for x in day[m])


def _value(t: pd.DataFrame, col: str, window: int | None) -> pd.Series:
    v = pd.to_numeric(t[col], errors="coerce").astype(float)
    if window is not None:                                  # an unreached start beyond the window (UR's reading)
        v = v.where(np.isfinite(v) & (v <= window), float(window) + 1.0)
    return v


def _card(reading: pd.DataFrame) -> pd.DataFrame:
    c = reading[(reading["section"] == "paired") & (reading["subsection"] == "card")].copy()
    c["value"] = pd.to_numeric(c["value"], errors="coerce")
    return c


def _counts(reading: pd.DataFrame) -> pd.DataFrame:
    c = reading[(reading["section"] == "mechanics") & (reading["subsection"] == "count")].copy()
    c["value"] = pd.to_numeric(c["value"], errors="coerce")
    return c


def _side(d: float) -> str:
    if not np.isfinite(d):
        return "blank"
    return "above" if d > 1e-12 else "below" if d < -1e-12 else "equal"


def labels_of(plan: str, request_rule: str | None, counts: pd.DataFrame, run: str, arm: str) -> str:
    """A row's labels (10.1 item 11): the plan's declared ones, at QP its request rule, every moot check nonzero and the
    conduct counts of 9.3, from the run's own counts (all starts)."""
    out = list(LABELS.get(plan, ()))
    if plan == "QP" and request_rule in REQUEST_RULE:
        out.append(REQUEST_RULE[request_rule])
    c = counts[(counts["run"] == run) & (counts["arm"] == arm) & (counts["block"] == "all")]
    for _, r in c.iterrows():
        m = str(r["measure"])
        if m.startswith("zero_") and np.isfinite(r["value"]) and r["value"] != 0:
            out.append(f"moot check nonzero (U-7): {m} = {r['value']:g}")
        if m in CONDUCT.get(plan, ()) and np.isfinite(r["value"]):
            out.append(f"conduct count (9.3): {m} = {r['value']:g}")
    return "; ".join(out)


def menu_rows(reading: pd.DataFrame) -> list[dict[str, Any]]:
    """The `menu` section: P plan against TS by run, arm and block (and start year), with the labels."""
    card, counts = _card(reading), _counts(reading)
    head = reading.drop_duplicates("run").set_index("run")
    rows = []
    own = reading[(reading["section"] == "scorecard") & (reading["subsection"] == "card") & (reading["plan"] == "TS")
                  & (reading["measure"] == "P")]
    for (run, arm), c in own.groupby(["run", "arm"]):                # TS's references: its own card
        h = head.loc[run]
        for b in BLOCKS:
            v = pd.to_numeric(c[c["block"] == b]["value"], errors="coerce")
            p = float(v.iloc[0]) if len(v) else float("nan")
            rows.append({"section": "menu", "run": run, "plan": "TS", "stream": h["stream"], "arm": arm,
                         "corner": h["corner"], "kind": h["kind"], "block": b, "measure": "P", "plan_value": p,
                         "ts_value": p, "difference": 0.0, "side": "the reference",
                         "labels": labels_of("TS", None, counts, run, arm)})
    for run in sorted(set(card["run"].dropna())):
        h = head.loc[run]
        plan = str(h["plan"])
        for arm in ARMS:
            c = card[(card["run"] == run) & (card["arm"] == arm) & (card["measure"] == "P")]
            if c.empty:
                continue
            lab = labels_of(plan, h.get("request_rule"), counts, run, arm)
            for b in BLOCKS:
                cb = c[c["block"] == b]
                p = _num(cb[cb["stat"] == "plan"]["value"].iloc[0]) if (cb["stat"] == "plan").any() else float("nan")
                q = _num(cb[cb["stat"] == "ts"]["value"].iloc[0]) if (cb["stat"] == "ts").any() else float("nan")
                rows.append({"section": "menu", "run": run, "plan": plan, "stream": h["stream"], "arm": arm,
                             "corner": h["corner"], "flip": h["flip"], "kind": h["kind"],
                             "request_rule": h.get("request_rule"), "block": b, "measure": "P", "plan_value": p,
                             "ts_value": q, "difference": p - q, "side": _side(p - q), "labels": lab})
    # the start years beside: P from the long replays' month-end nets (months ahead over three), plan and TS
    st = _starts(reading, "scorecard")
    for (run, arm), t in st.groupby(["run", "arm"]):
        plan = str(t["plan"].iloc[0])
        if plan == "TS":
            continue
        ts = st[(st["plan"] == "TS") & (st["stream"] == t["stream"].iloc[0]) & (st["arm"] == arm)]
        tsv = dict(zip(ts["start_day"].astype(int), pd.to_numeric(ts["months_ahead"], errors="coerce")))
        t = t[t["observed"].astype(int) >= 63]
        for y, ty in t.groupby(t["start_date"].astype(str).str[:4]):
            x = pd.to_numeric(ty["months_ahead"], errors="coerce").to_numpy(float) / 3.0
            z = np.array([tsv.get(int(s0), np.nan) for s0 in ty["start_day"].astype(int)], float) / 3.0
            ok = np.isfinite(x) & np.isfinite(z)
            rows.append({"section": "menu", "run": run, "plan": plan, "stream": t["stream"].iloc[0], "arm": arm,
                         "block": f"year_{y}", "measure": "P_long_replay", "plan_value": float(x[ok].mean()) if ok.any()
                         else float("nan"), "ts_value": float(z[ok].mean()) if ok.any() else float("nan"),
                         "difference": float((x[ok] - z[ok]).mean()) if ok.any() else float("nan"),
                         "n": int(ok.sum()), "note": "a start-year reading beside: P from the long replays' month-end "
                                                     "nets (the exact-length runs not substituted)"})
    return rows


def flag_rows(reading: pd.DataFrame) -> list[dict[str, Any]]:
    """10.1 items 5 and 11 and 9.3's last line, mechanical."""
    card, counts = _card(reading), _counts(reading)
    head = reading.drop_duplicates("run").set_index("run")

    def diff(run: str, arm: str, block: str, measure: str) -> float:
        c = card[(card["run"] == run) & (card["arm"] == arm) & (card["block"] == block) & (card["measure"] == measure)]
        p, q = c[c["stat"] == "plan"]["value"], c[c["stat"] == "ts"]["value"]
        return float(p.iloc[0]) - float(q.iloc[0]) if len(p) and len(q) else float("nan")

    rows = []
    runs = [r for r in sorted(set(card["run"].dropna())) if str(head.loc[r]["plan"]) != "TS"]
    for arm in ARMS:
        for plan in ("LU", "DT", "FP", "QP"):
            for stream in ("16", "14"):
                s_, l_ = f"{plan}-{stream}-s", f"{plan}-{stream}-l"
                a, b = diff(s_, arm, "all", "P"), diff(l_, arm, "all", "P")
                if np.isfinite(a) and np.isfinite(b):
                    flag = a * b < 0
                    rows.append({"section": "flags", "plan": plan, "stream": f"P-{stream}", "arm": arm,
                                 "flag": "depends on its unread terms", "raised": bool(flag),
                                 "note": f"P less TS: strict {a:+.6f}, lenient {b:+.6f} (10.1 item 5)"})
        a, b = diff("QP-16-s", arm, "all", "P"), diff("QP-16-req", arm, "all", "P")
        if np.isfinite(a) and np.isfinite(b):
            rows.append({"section": "flags", "plan": "QP", "stream": "P-16", "arm": arm,
                         "flag": "depends on its request rule", "raised": bool(a * b < 0),
                         "note": f"P less TS: every eligible close {a:+.6f}, the reference's cadence {b:+.6f} (5.6)"})
        for run in runs:
            bad = [m for m in ("P",) + GUARDED
                   if np.isfinite(diff(run, arm, "early", m)) and np.isfinite(diff(run, arm, "late", m))
                   and diff(run, arm, "early", m) * diff(run, arm, "late", m) < 0]
            rows.append({"section": "flags", "run": run, "plan": str(head.loc[run]["plan"]),
                         "stream": head.loc[run]["stream"], "arm": arm, "flag": "not stable across blocks",
                         "raised": bool(bad), "note": ("opposite signs on the early and late blocks: " + ", ".join(bad))
                         if bad else "no measure of P and the guarded ones changes sign between the blocks"})
            c = counts[(counts["run"] == run) & (counts["arm"] == arm) & (counts["block"] == "all")]
            shares = {str(m): float(v) for m, v in zip(c["measure"], c["value"]) if str(m).startswith("share_starts_")}
            if shares:
                same = all(np.isfinite(v) and v == 0.0 for v in shares.values())
                rows.append({"section": "flags", "run": run, "plan": str(head.loc[run]["plan"]),
                             "stream": head.loc[run]["stream"], "arm": arm, "flag": "no effect on these trades",
                             "raised": bool(same), "note": "the plan's daily cash equals TS's on every start within 252 "
                                                           "sessions (9.3)" if same else "the plan differs from TS"})
    rows.append({"section": "flags", "flag": "E-015's limits", "raised": False, "note": E015})
    return rows


def _reading(x: np.ndarray, h: int, coverage: dict[tuple[int, int], float]) -> dict[str, Any]:
    r = FU.paired_reading(x, h)
    out = {"mean": r["mean"], "n_w": float(r["n_w"]), "n_eff": float(r["n_eff"]), "note": r["note"],
           "windows_above": float(r["signs"]["above"]), "windows_equal": float(r["signs"]["equal"]),
           "windows_below": float(r["signs"]["below"])}
    if r["interval"] is not None:
        out.update(interval_lo=float(r["interval"][0]), interval_hi=float(r["interval"][1]), mdd=float(r["mdd"]))
        cov = coverage.get((int(h), int(r["n_w"])))
        out["coverage"] = float("nan") if cov is None else float(cov)
        if cov is None:
            out["note"] = "coverage not computed by the run at this setting"
        elif FU.coverage_label(cov):
            out["note"] = FU.coverage_label(cov)
    return out


def _coverage(reading: pd.DataFrame) -> dict[tuple[int, int], float]:
    c = reading[(reading["section"] == "coverage") & (reading["subsection"] == "worst")]
    if c.empty or not {"horizon", "n_w", "value"} <= set(c.columns):
        return {}
    return {(int(_num(h)), int(_num(n))): float(_num(v)) for h, n, v in zip(c["horizon"], c["n_w"], c["value"])}


def _indicators(t: pd.DataFrame) -> dict[str, tuple[pd.Series, int, str]]:
    """item 2's break-even by month m as a per-start 0/1 (a start with m months observed)."""
    be = pd.to_numeric(t["break_even_day"], errors="coerce").astype(float)
    return {f"break_even_by_month_{m}": (((be <= M.MONTH * m) & np.isfinite(be)).astype(float), HORIZON_OF_MONTH[m],
                                         "higher") for m in BREAK_EVEN_BY}


def distribution_rows(reading: pd.DataFrame) -> list[dict[str, Any]]:
    """Item 3: each per-start measure's distribution over starts, with 10.2's reading on the plan's own series."""
    st = _starts(reading, "scorecard")
    cov = _coverage(reading)
    rows = []
    for (run, arm), t in st.groupby(["run", "arm"]):
        t = t.sort_values("start_day")
        series = {c: (_value(t, c, w), h, d) for c, h, d, w in MEASURES if c in t}
        series.update(_indicators(t))
        for c, (v, h, _d) in series.items():
            for b in BLOCKS:
                keep = t["start_day"].astype(int).isin(_block_days(t, b, h)).to_numpy()
                x = v.to_numpy(float)[keep]
                x = x[np.isfinite(x)]
                q = M.quantiles(x)
                base = {"section": "distribution", "run": run, "plan": t["plan"].iloc[0], "stream": t["stream"].iloc[0],
                        "arm": arm, "block": b, "measure": c, "horizon": h, "n": int(len(x))}
                rows += [{**base, "stat": f"p{p}", "value": q[f"p{p}"]} for p in M.PERCENTILES]
                rows.append({**base, "stat": "mean_over_starts", "value": float(x.mean()) if len(x) else float("nan")})
                r = _reading(x, h, cov)
                rows += [{**base, "stat": k, "value": v_, "note": "10.2 on the plan's own series (unpaired)"}
                         for k, v_ in r.items() if k != "note"]
                rows.append({**base, "stat": "reading_note", "value": float("nan"), "note": r["note"]})
    return rows


def variance_rows(reading: pd.DataFrame) -> list[dict[str, Any]]:
    """Item 3's S6 form: on one stream and arm, across TS's reference and the plans' runs, on the starts all of them
    hold at the measure's horizon: the start day's share of the variance."""
    st = _starts(reading, "scorecard")
    rows = []
    for (stream, arm), t in st.groupby(["stream", "arm"]):
        for c, h, _d, w in MEASURES:
            if c not in t:
                continue
            by = {}
            for run, tr in t.groupby("run"):
                keep = tr["start_day"].astype(int).isin(_block_days(tr, "all", h))
                by[run] = dict(zip(tr["start_day"].astype(int)[keep], _value(tr, c, w)[keep]))
            common = sorted(set.intersection(*(set(k for k, v in d.items() if np.isfinite(v)) for d in by.values())))
            if len(by) < 2 or len(common) < 2:
                continue
            x = np.array([[by[r_][s0] for s0 in common] for r_ in sorted(by)], float)
            within = float(np.mean(np.var(x, axis=1, ddof=1)))
            between = float(np.var(x.mean(axis=1), ddof=1))
            tot = within + between
            rows.append({"section": "variance_share", "stream": stream, "arm": arm, "measure": c, "horizon": h,
                         "n": len(common), "runs": len(by), "stat": "start_day_share",
                         "value": within / tot if tot > 0 else float("nan"),
                         "note": "within-run variance over starts / (within + the variance of the runs' means)"})
    return rows


def paired_more_rows(reading: pd.DataFrame) -> list[dict[str, Any]]:
    """Item 4 for the per-start measures: plan less TS on the same starts, by block at the measure's horizon."""
    st = _starts(reading, "scorecard")
    cov = _coverage(reading)
    rows = []
    ts_by = {(s_, a): t for (s_, a, p), t in st.groupby(["stream", "arm", "plan"]) if p == "TS"}
    for (run, arm), t in st.groupby(["run", "arm"]):
        plan, stream = str(t["plan"].iloc[0]), t["stream"].iloc[0]
        ts = ts_by.get((stream, arm))
        if plan == "TS" or ts is None:
            continue
        t, ts = t.sort_values("start_day"), ts.sort_values("start_day")
        mine = {c: (_value(t, c, w), h, d) for c, h, d, w in MEASURES if c in t}
        mine.update(_indicators(t))
        theirs = {c: _value(ts, c, w) for c, h, d, w in MEASURES if c in ts}
        theirs.update({k: v[0] for k, v in _indicators(ts).items()})
        for c, (v, h, direction) in mine.items():
            tv = dict(zip(ts["start_day"].astype(int), theirs[c]))
            pv = dict(zip(t["start_day"].astype(int), v))
            for b in BLOCKS:
                days = [s0 for s0 in sorted(_block_days(t, b, h)) if s0 in tv]
                x = np.array([pv[s0] for s0 in days], float)
                y = np.array([tv[s0] for s0 in days], float)
                ok = np.isfinite(x) & np.isfinite(y)
                dlt = (x - y)[ok]
                good = dlt if direction == "higher" else -dlt
                base = {"section": "paired_more", "run": run, "plan": plan, "stream": stream, "arm": arm, "block": b,
                        "measure": c, "horizon": h, "direction": direction, "n": int(ok.sum())}
                q = M.quantiles(dlt)
                rows += [{**base, "stat": f"difference_p{p}", "value": q[f"p{p}"]} for p in M.PERCENTILES]
                for k, m_ in (("better", good > 1e-9), ("equal", np.abs(dlt) <= 1e-9), ("worse", good < -1e-9)):
                    rows.append({**base, "stat": f"share_{k}", "value": float(m_.mean()) if len(dlt) else float("nan")})
                r = _reading(dlt, h, cov)
                rows += [{**base, "stat": k, "value": v_} for k, v_ in r.items() if k != "note"]
                rows.append({**base, "stat": "reading_note", "value": float("nan"), "note": r["note"]})
    return rows


def evenness_rows(reading: pd.DataFrame) -> list[dict[str, Any]]:
    """Item 10: each run's P (the paired card, all starts) against each evenness measure's mean (starts with 252)."""
    card = _card(reading)
    own = reading[(reading["section"] == "scorecard") & (reading["subsection"] == "card") & (reading["measure"] == "P")
                  & (reading["block"] == "all")]
    st = _starts(reading, "scorecard")
    rows = []
    for (run, arm), t in st.groupby(["run", "arm"]):
        c = card[(card["run"] == run) & (card["arm"] == arm) & (card["block"] == "all") & (card["measure"] == "P")
                 & (card["stat"] == "plan")]
        if t["plan"].iloc[0] == "TS":                                # the reference: its own card's P
            c = own[(own["run"] == run) & (own["arm"] == arm)]
        p = _num(c["value"].iloc[0]) if len(c) else float("nan")
        keep = t["start_day"].astype(int).isin(_block_days(t, "all", 252)).to_numpy()
        for m in EVENNESS:
            x = pd.to_numeric(t[m], errors="coerce").to_numpy(float)[keep]
            x = x[np.isfinite(x)]
            rows.append({"section": "evenness", "run": run, "plan": t["plan"].iloc[0], "stream": t["stream"].iloc[0],
                         "arm": arm, "measure": m, "ahead_P": p, "value": float(x.mean()) if len(x) else float("nan"),
                         "n": int(len(x)), "note": "E-015's menu form: the run as a point of P against this evenness "
                                                   "measure's mean over starts with twelve months"})
    return rows


def menu(reading: pd.DataFrame, gate: pd.DataFrame | None = None) -> pd.DataFrame:
    """The menu file from the run's written reading (and gate) files: every section above, every row labelled."""
    rows = (menu_rows(reading) + flag_rows(reading) + distribution_rows(reading) + variance_rows(reading)
            + paired_more_rows(reading) + evenness_rows(reading))
    if gate is not None and len(gate):
        g = gate[gate["section"].astype(str) == "gate"]
        for _, r in g.iterrows():
            rows.append({"section": "menu_gate", "run": r.get("run"), "plan": r.get("plan"), "stream": r.get("stream"),
                         "corner": r.get("corner"), "reading": r.get("reading"), "shift": r.get("shift"),
                         "measure": "median_log_growth", "value": _num(r.get("median_log_growth")),
                         "labels": r.get("labels")})
    out = pd.DataFrame(rows)
    out["status"] = STATUS
    return out


__all__ = ["STATUS", "LABELS", "REQUEST_RULE", "CONDUCT", "MEASURES", "EVENNESS", "E015", "labels_of", "menu_rows",
           "flag_rows", "distribution_rows", "variance_rows", "paired_more_rows", "evenness_rows", "menu"]
