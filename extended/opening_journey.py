"""F-03 (family O): section 13's scorecard parts beside Q-17's U1 readings (`extended.user_readings`) and the paired
readings (`extended.opening_stagec.paired_rows`) -- the choice-block beside, the wait as the user feels it, every
measure's uncertainty and design against luck, the evenness trade-off curve, `bm63c`'s place, the frontier's
directions. Beside the pass line, never it (E-008); nothing here decides anything. The vendored pure modules
(`propedge.research.u_select`, `user_drivers`) are imported at call time: run in a process with
`use_vendored_stage2()` done where a function says so.

**The choice-block beside** (13, "On which starts"): 2021-2023's starts, a choice-block read (u3 out of fold: the
pinned fold fits, `opening_states.compute(frozen_folds=...)`), each start's history ending at 2023-12-29 (the restricted
job, 18.1 item 4), **purged by horizon per measure by Stage 2's `u_select.block` purge** (`early`: a start within the
reading's horizon of the block's last start is dropped -- one start more than the job's own end needs, as Stage 2
reads it). `choice_rows` gives Q-17's four sections on that purge: the card by `u_select.scorecard(records, "early")`,
the E-007 (e) rows on `u_select.block(records, "early", 63)` (their only horizon), and the path and response rows on
the start table with `observed` cut to the purge (`purged_table`: `min(observed, last - start_day)`, the month nets past
it blank), which is what their eligibility reads. Every row is labelled `block` = `choice`.

**The wait, as a user feels it** (13): on the replay's records (the verdict arm, no firm response), for each design --
the sessions from activation to the opening, the openings' hours, **the minutes the firm's slot is held by each
opening** (its trade's exit at its own R less its entry, `exit_t_<R> - entry_t`, both bar-end minutes of the trade
table), **funded trades per live account-day** (the funded trades over the funded accounts' live sessions,
`FundedAccount.days`) and **the share of account-sessions without a trade** (one less the account-sessions holding a
funded trade over the live sessions) -- pooled and as a distribution over starts, and each against P-16's (`against`).

**Every measure's uncertainty and design against luck** (13; E-015 (1); `user_drivers.csv` section `design_vs_luck`):
for each measure of `LUCK_MEASURES`, on each block's eligible starts, each design's distribution (p10, p50, p90),
its effective number of independent starts (Bartlett at the measure's own horizon as its lag, in start order, as RD-01 and
RD-02 read it, `user_measures.n_eff_bartlett`) and the
mean's standard error from it; across the three designs the vendored `user_drivers.variance_split` (the start day's
share of the variance and the design's). Time-to-event measures are read censored at their window (an unreached start
at the window plus one), the money spent among the starts reaching the event, the deepest fall among the starts broken
even.

**The evenness trade-off curve** (E-015 (4)): for each block and arm, each design's P (its card's) against each
evenness measure's median over starts (its path row), the designs ordered from the least even to the most even, and
each step's change in P per unit of evenness gained -- read from the rows already computed, so the curve is the rows'.

**`bm63c`** (`p_bound.RECOMMENDED`) is read beside only once its critical-value table is pinned (13): no decision row pins
it (E-085: not adopted, the table not pinned), so `BM63C_TABLE_SHA256` is None and `bm63c_rows` writes the note in its
place; a pinned table is a code commit naming its sha256, checked against the file before it is read.

**The frontier's directions** are Stage 2's (`user_drivers.FRONTIER_MEASURES`): P, S3a and S5a higher is better, S1 (the
cash spent before the first payout, p90) lower.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from extended import user_measures as M
from extended import user_readings as UR

CHOICE_FIRST = "2021-01-04"
CHOICE_LAST_YEAR = 2023
JUDGED_FIRST_YEAR = 2024
MONTH = 21
OUTCOME_MONTHS = (1, 2, 3, 6, 12)
N_EFF_LAG = 63
W_DECLARED = 5
#: 13's frontier on P, S1, S3a, S5a in Stage 2's directions (`user_drivers.FRONTIER_MEASURES`; a test holds them)
FRONTIER_HIGHER = {"P": True, "S1": False, "S3a": True, "S5a": True}
#: E-014 (4)'s evenness measures and their direction (True: higher is more even)
EVENNESS = (("share_months_positive", True), ("longest_months_without_payout", False), ("sd_monthly_net", False),
            ("deepest_fall_after_break_even", False), ("payouts_per_month", True), ("largest_month_share", False))
#: every journey measure read for its uncertainty and design against luck: (start-table column, horizon, how)
#: how: "value" as it is; "censored" an unreached start at the window plus one; "reached:<col>" among the starts whose
#: <col> fell inside the window; "broken_even" among the starts broken even inside the window
LUCK_MEASURES: tuple[tuple[str, int, str], ...] = (
    *((f"net_month_{m}", MONTH * m, "value") for m in OUTCOME_MONTHS),
    ("months_ahead", 63, "value"),
    ("first_pass", UR.FIRST_WINDOW, "censored"), ("first_payout", UR.FIRST_WINDOW, "censored"),
    ("spent_before_first_pass", UR.FIRST_WINDOW, "reached:first_pass"),
    ("spent_before_first_payout", UR.FIRST_WINDOW, "reached:first_payout"),
    ("break_even_day", UR.YEAR_WINDOW, "censored"),
    ("deepest_fall_after_break_even", UR.YEAR_WINDOW, "broken_even"),
    *((c, UR.YEAR_WINDOW, "value") for c, _ in EVENNESS),
    ("payout_cash_per_month", UR.YEAR_WINDOW, "value"))
#: `bm63c`'s critical-value table: (path, sha256) once a decision row pins it -- None: not pinned (E-085)
BM63C_TABLE: tuple[str, str] | None = None
BM63C_NOTE = ("bm63c (p_bound.RECOMMENDED) not read: its critical-value table is not pinned (E-085: not adopted, the "
              "table not pinned); read beside once a row pins it (section 13)")
NAN = float("nan")


# ------------------------------------------------------------------------------------------------ eligibility


def last_choice_start(t: pd.DataFrame) -> int:
    """The block's last start (`u_select.block`'s `last` for `early`): the largest start day of the starts of
    2023 and before."""
    yr = t["start_date"].astype(str).str[:4].astype(int)
    e = t.loc[yr <= CHOICE_LAST_YEAR, "start_day"]
    if not len(e):
        raise ValueError("no start of the choice block")
    return int(e.max())


def purged_table(t: pd.DataFrame) -> pd.DataFrame:
    """The start table under Stage 2's `early` purge: the choice block's starts (2023 and before) with `observed` cut to
    `min(observed, last - start_day)` -- so `observed >= h` is exactly `u_select.block(..., "early", h)` -- and the month
    nets and months ahead past the cut blank."""
    yr = t["start_date"].astype(str).str[:4].astype(int)
    p = t[yr <= CHOICE_LAST_YEAR].copy()
    last = last_choice_start(t)
    p["observed"] = np.minimum(p["observed"].astype(int).to_numpy(), last - p["start_day"].astype(int).to_numpy())
    obs = p["observed"].to_numpy(int)
    for m in OUTCOME_MONTHS:
        p.loc[obs < MONTH * m, f"net_month_{m}"] = np.nan
    p.loc[obs < 63, "months_ahead"] = np.nan
    return p.reset_index(drop=True)


def eligible(t: pd.DataFrame, block: str, h: int) -> np.ndarray:
    """Each start of the table read at horizon `h` on `block`: `judged` the starts from 2024 with `h` sessions left
    (`u_select`'s `late`), `choice` a purged table's starts with `h` left (`early`)."""
    m = t["observed"].to_numpy(int) >= int(h)
    if block == "judged":
        m &= t["start_date"].astype(str).str[:4].astype(int).to_numpy() >= JUDGED_FIRST_YEAR
    elif block != "choice":
        raise ValueError(f"a block is judged or choice, not {block!r}")
    return m


# ------------------------------------------------------------------------------------------------ the choice block


def _relabel(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [{**r, "block": "choice"} for r in rows if r.get("block") == "all"]


def choice_rows(design: str, arm: str, resp: Any, outs: Sequence[Mapping[str, Any]]) -> tuple[list[dict], pd.DataFrame]:
    """One design, arm and response on the choice block's starts under Stage 2's purge (the module docstring): (the
    rows, `block` = `choice`, in `user_readings.summary`'s form; the purged start table). Needs the vendored path."""
    from propedge.research import u_select as S

    records = [x["rec"] for x in outs]
    t = UR.start_table(design, arm, resp.name, outs)
    tp = purged_table(t)
    card = S.scorecard(records, S.EARLY)
    rows = [UR._row("scorecard", "choice", k, "value", v["value"], v["n"]) for k, v in card.items()]
    rows += _relabel(UR.extra_rows(S.block(records, S.EARLY, S.P_HORIZON), UR.Q44_BLOCKS))   # W3.1: named
    rows += _relabel(UR.path_rows(tp, UR.Q44_BLOCKS) + UR.response_rows(tp, UR.Q44_BLOCKS))
    head = {"design": design, "arm": arm, "response": resp.name, "kind": resp.kind,
            "enforcement_p": float(resp.enforcement_p), "rtp": bool(resp.rtp), "rtp_warnings": int(resp.rtp_warnings),
            "ftp_label": resp.ftp_label}
    return [{**head, **r} for r in rows], tp


def choice_problems(rows: Sequence[Mapping[str, Any]], what: str) -> list[str]:
    """The choice block's refusing check, like with like since Wave 3.1 (`docs/MEASURES.md` section 6, m-11; as
    `user_readings.consistency_problems`): the E-007 (e) P (on `early`'s 63-session starts; ahead above 1e-6) equal to
    the mean of its own three month shares, and never above the card's P (Stage 2's `> 0`, read beside, never held
    equal to it)."""
    by = {(r["section"], r["measure"], r["stat"]): float(r["value"]) for r in rows if r.get("block") == "choice"}
    card, mine = by.get(("scorecard", "P", "value")), by.get(("extra", "P", "value"))
    shares = [by.get(("extra", f"share_ahead_month_{m}", "value")) for m in (1, 2, 3)]
    if card is None or mine is None:
        return [f"{what} choice: the extra P {mine} or the card's {card} is missing"]
    if np.isnan(card) or np.isnan(mine):
        return [] if (np.isnan(card) and np.isnan(mine)) else [f"{what} choice: one of P {mine}, {card} is blank"]
    if None in shares or abs(mine - float(np.mean(shares))) > 1e-12 or mine > card + 1e-12:
        return [f"{what} choice: the extra P {mine} is not the mean of its month shares {shares}, at most the "
                f"card's {card}"]
    return []


def p14_choice(ahead: pd.Series, dates: Sequence[str], h: int = 63) -> pd.Series:
    """P-14's registered ahead series on the choice block's purged starts: start dates from 2021-01-04 whose index in
    the choice job's calendar `dates` is at most the last start's less `h` (the same `early` purge)."""
    ds = [str(d) for d in dates]
    last = max(i for i, d in enumerate(ds) if int(d[:4]) <= CHOICE_LAST_YEAR)
    keep = {d for i, d in enumerate(ds) if d >= CHOICE_FIRST and i <= last - int(h)}
    return ahead[[d in keep for d in ahead.index.astype(str)]]


# ------------------------------------------------------------------------------------------------ the wait as felt


def _row(section: str, block: str, design: str, measure: str, stat: str, value: float, n: int, note: str = ""
         ) -> dict[str, Any]:
    return {"section": section, "block": block, "design": design, "measure": measure, "stat": stat,
            "value": float(value), "n": int(n), "note": note}


def _dist(section: str, block: str, design: str, measure: str, x: np.ndarray, note: str = "") -> list[dict[str, Any]]:
    v = np.asarray(x, float)
    v = v[np.isfinite(v)]
    q = M.quantiles(v)
    out = [_row(section, block, design, measure, f"p{p}", q[f"p{p}"], q["n"], note) for p in M.PERCENTILES]
    out.append(_row(section, block, design, measure, "mean", float(v.mean()) if len(v) else NAN, len(v), note))
    return out


def slot_minutes(opens: pd.DataFrame, trades: pd.DataFrame) -> np.ndarray:
    """Each opening's minutes in position: its offer's exit at the opening's own R less its entry (`exit_t_<R>` and
    `entry_t` of the trade table, bar-end minutes); refused when an opening's offer or its R's exit is missing."""
    from extended import opening_population as OP

    tt = trades.assign(_offer=[OP.offer_id(d, int(s)) for d, s in zip(trades["date"].astype(str),
                                                                       trades["decision_slot_minutes"])])
    tt = tt.drop_duplicates("_offer").set_index("_offer")
    out = np.empty(len(opens))
    for i, (o, r) in enumerate(zip(opens["offer"], pd.to_numeric(opens["rr"], errors="coerce"))):
        R = OP.R_JUDGED if not np.isfinite(r) else float(r)
        col = f"exit_t_{R:g}"
        if o not in tt.index or col not in tt.columns:
            raise ValueError(f"an opening's offer {o} at R {R:g} has no exit in the trade table")
        out[i] = float(tt.at[o, col]) - float(tt.at[o, "entry_t"])
    return out


def wait_rows(design: str, block: str, opens: pd.DataFrame, funded: pd.DataFrame, accounts: pd.DataFrame,
              minutes: np.ndarray, W: int = W_DECLARED) -> tuple[list[dict[str, Any]], dict[str, float]]:
    """13's wait as a user feels it, for one design on one block's starts: `opens` its openings (`start_day`,
    `opening_session`, `offer` "date|slot"), `funded` its funded trades (`start_day`, `account`, `day`), `accounts` its
    funded accounts (`start_day`, `account`, `days` = live sessions), `minutes` each opening's minutes in position.
    (rows, the pooled values `against` differences)."""
    out: list[dict[str, Any]] = []
    sec = "wait"
    out += _dist(sec, block, design, "sessions_to_opening", opens["opening_session"].to_numpy(float),
                 "live sessions from activation to the opening (0: the first)")
    n_o = len(opens)
    out.append(_row(sec, block, design, "opened_inside_wait", "share",
                    float((opens["opening_session"].astype(int) < int(W)).mean()) if n_o else NAN, n_o))
    slot = np.array([int(str(o).split("|")[1]) for o in opens["offer"]], dtype=int) if n_o else np.zeros(0, int)
    hour = (slot + 1020) % 1440 // 60
    for h_ in sorted(set(hour.tolist())):
        out.append(_row(sec, block, design, "opening_hour", f"share_{h_:02d}", float((hour == h_).mean()), n_o,
                        "the opening's mark, CT hour"))
    out += _dist(sec, block, design, "slot_minutes", minutes, "each opening's minutes in position: its exit at its "
                                                              "own R less its entry")
    live = accounts.groupby("start_day")["days"].sum()
    trades_n = funded.groupby("start_day").size().reindex(live.index, fill_value=0)
    sess_n = (funded.drop_duplicates(["start_day", "account", "day"]).groupby("start_day").size()
              .reindex(live.index, fill_value=0))
    ok = live > 0
    per_tr = (trades_n[ok] / live[ok]).to_numpy(float)
    per_none = (1.0 - sess_n[ok] / live[ok]).to_numpy(float)
    L = float(live.sum())
    pooled = {"trades_per_live_account_day": float(len(funded)) / L if L > 0 else NAN,
              "share_account_sessions_without_trade": (1.0 - float(len(funded.drop_duplicates(
                  ["start_day", "account", "day"]))) / L) if L > 0 else NAN,
              "slot_minutes": float(np.nanmean(minutes)) if len(minutes) else NAN,
              "sessions_to_opening": float(opens["opening_session"].astype(float).mean()) if n_o else NAN}
    for k in ("trades_per_live_account_day", "share_account_sessions_without_trade"):
        out.append(_row(sec, block, design, k, "pooled", pooled[k], int(L), "over every funded account's live sessions"))
    out += _dist(sec, block, design, "trades_per_live_account_day", per_tr, "per start")
    out += _dist(sec, block, design, "share_account_sessions_without_trade", per_none, "per start")
    return out, pooled


def against(pooled: Mapping[str, Mapping[str, float]], block: str, base: str = "p16") -> list[dict[str, Any]]:
    """Each design's pooled wait readings less P-16's (13: "against P-16's")."""
    out = []
    for d, v in pooled.items():
        if d == base or base not in pooled:
            continue
        for k, x in v.items():
            out.append({**_row("wait", block, d, k, f"minus_{base}", float(x) - float(pooled[base][k]), 0),
                        "against": base})
    return out


# ------------------------------------------------------------------------------------------------ uncertainty and luck


def measure_values(t: pd.DataFrame, block: str, column: str, h: int, how: str) -> np.ndarray:
    """A measure's per-start values on `block`'s eligible starts at horizon `h`, in start order (`LUCK_MEASURES`)."""
    s = t[eligible(t, block, h)].sort_values("start_day", kind="stable")
    x = pd.to_numeric(s[column], errors="coerce").to_numpy(float)
    if how == "censored":
        return np.where(np.isfinite(x) & (x <= h), x, float(h) + 1.0)
    if how.startswith("reached:"):
        f = pd.to_numeric(s[how.split(":", 1)[1]], errors="coerce").to_numpy(float)
        return x[np.isfinite(f) & (f <= h)]
    if how == "broken_even":
        be = pd.to_numeric(s["break_even_day"], errors="coerce").to_numpy(float)
        return x[np.isfinite(be) & (be <= h)]
    return x


def luck_rows(tables: Mapping[str, pd.DataFrame], block: str, arm: str,
              measures: Sequence[tuple[str, int, str]] = LUCK_MEASURES) -> list[dict[str, Any]]:
    """Every measure's uncertainty (each design: p10, p50, p90, n_eff at lag 63, the mean's standard error) and design
    against luck (`user_drivers.variance_split` over the designs) on one block and arm. Needs the vendored path."""
    from propedge.research import user_drivers as UD

    out: list[dict[str, Any]] = []
    for col, h, how in measures:
        vals = {d: measure_values(t, block, col, h, how) for d, t in tables.items()}
        for d, x in vals.items():
            v = x[np.isfinite(x)]
            ne = M.n_eff_bartlett(v, int(h))                  # x1: the lag at the measure's own horizon
            sd = float(np.std(v, ddof=1)) if len(v) > 1 else NAN
            base = {"section": "uncertainty", "block": block, "arm": arm, "design": d, "measure": col,
                    "horizon": int(h), "read": how}
            q = M.quantiles(v)
            out += [{**base, "stat": f"p{p}", "value": q[f"p{p}"], "n": q["n"]} for p in M.PERCENTILES]
            out += [{**base, "stat": "n_eff_bartlett", "lag": int(h), "value": ne, "n": len(v)},
                    {**base, "stat": "sd", "value": sd, "n": len(v)},
                    {**base, "stat": "se_mean", "value": sd / np.sqrt(ne) if (np.isfinite(ne) and ne > 0) else NAN,
                     "n": len(v)}]
        split = UD.variance_split(vals)
        out += [{"section": "design_vs_luck", "block": block, "arm": arm, "design": "|".join(tables), "measure": col,
                 "horizon": int(h), "read": how, "stat": k, "value": float(v), "n": int(split.get("n", 0))}
                for k, v in split.items() if k != "n"]
    return out


# ------------------------------------------------------------------------------------------------ the evenness curve


def evenness_curve_rows(rows: Sequence[Mapping[str, Any]], designs: Sequence[str]) -> list[dict[str, Any]]:
    """E-015 (4)'s curve from the computed rows (the off response): for each (block, arm) and evenness measure, each
    design's P (`scorecard` P) and the measure's median over starts (`path` p50), ordered least to most even, with each
    step's change in P per unit of evenness gained."""
    card: dict[tuple, float] = {}
    med: dict[tuple, float] = {}
    for r in rows:
        if r.get("response") != "off":
            continue
        k = (r.get("block"), r.get("arm"), r.get("design"))
        if r.get("section") == "scorecard" and r.get("measure") == "P" and r.get("stat") == "value":
            card[k] = float(r["value"])
        elif r.get("section") == "path" and r.get("stat") == "p50":
            med[(*k, r.get("measure"))] = float(r["value"])
    out = []
    for block, arm in sorted({(k[0], k[1]) for k in card if k[0] in ("judged", "choice")}):    # the two blocks read
        for m, higher in EVENNESS:
            pts = [(d, med.get((block, arm, d, m), NAN), card.get((block, arm, d), NAN)) for d in designs]
            pts = [p for p in pts if np.isfinite(p[1]) and np.isfinite(p[2])]
            pts.sort(key=lambda p: (p[1] if higher else -p[1]))                       # least even first
            if not pts:
                out.append({"section": "evenness_curve", "block": block, "arm": arm, "design": "", "measure": m,
                            "more_even": "higher" if higher else "lower", "note": "no point: no design has both P "
                            "and the measure's median (no start with twelve months on this block)"})
            prev = None
            for i, (d, e, P) in enumerate(pts):
                step = {}
                if prev is not None:
                    gain = (e - prev[1]) if higher else (prev[1] - e)
                    step = {"evenness_gained": gain, "P_change": P - prev[2],
                            "P_change_per_unit_evenness": (P - prev[2]) / gain if gain != 0 else NAN,
                            "from_design": prev[0]}
                out.append({"section": "evenness_curve", "block": block, "arm": arm, "design": d, "measure": m,
                            "more_even": "higher" if higher else "lower", "evenness_p50": e, "P": P, "rank": i,
                            **step})
                prev = (d, e, P)
    return out


# ------------------------------------------------------------------------------------------------ bm63c


def bm63c_table(table: tuple[str, str] | None = BM63C_TABLE, root: Path | None = None) -> dict[float, float] | None:
    """`bm63c`'s critical values when a row pins the table ((path, sha256)): the file checked against its pin, then
    `p_bound.load_bm63c_critical`; None when no table is pinned. A pin whose file differs refuses (ValueError)."""
    if table is None:
        return None
    from extended import ROOT as _ROOT
    from extended import p_bound as PB

    p = (Path(root) if root is not None else _ROOT) / table[0]
    got = hashlib.sha256(p.read_bytes()).hexdigest()
    if got != table[1]:
        raise ValueError(f"REFUSED (F-03): bm63c's table {table[0]} hashes to {got[:12]}, not its pin {table[1][:12]}")
    return PB.load_bm63c_critical(p)


def bm63c_rows(name: str, other: str, D: np.ndarray, table: dict[float, float] | None, level: float = 0.05
               ) -> list[dict[str, Any]]:
    """13's `bm63c` beside the paired P difference: its one-sided verdict at `level` on a pinned table, else the note."""
    base = {"design": name, "against": other, "measure": "P_difference", "n": int(len(D))}
    if table is None:
        return [{**base, "stat": "bm63c_0.05", "value": NAN, "note": BM63C_NOTE}]
    from extended import p_bound as PB

    if len(D) < 2 * 63:
        return [{**base, "stat": "bm63c_0.05", "value": NAN, "note": "fewer than two 63-start batches"}]
    rej = bool(np.asarray(PB.bm63c_rejects(np.asarray(D, float)[:, None], level=level, table=table)).ravel()[0])
    return [{**base, "stat": "bm63c_0.05", "value": float(rej), "note": "1: above at one-sided 0.05 (beside)"}]


__all__ = ["CHOICE_FIRST", "FRONTIER_HIGHER", "EVENNESS", "LUCK_MEASURES", "BM63C_TABLE", "BM63C_NOTE",
           "last_choice_start", "purged_table", "eligible", "choice_rows", "choice_problems", "p14_choice",
           "slot_minutes", "wait_rows", "against", "measure_values", "luck_rows", "evenness_curve_rows", "bm63c_table",
           "bm63c_rows"]
