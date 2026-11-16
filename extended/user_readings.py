"""Q-17: one design, arm and response's readings from its starts (`extended.user_beside.run_starts`' outputs) -- the
rows of `results/user_beside.csv` and `results/user_beside_starts.csv`. Imports the vendored engine's pure modules
(`propedge.research.user_journey`, `u_select`) at call time: run in a process with `use_vendored_stage2()` done.

**Blocks.** `all`: every start with the reading's horizon left; `judged`: D-621 (4)(b)'s late block -- the starts from
2024 with the horizon left (`u_select.block(..., "late", h)`).

**Sections** (each row: design, arm, response and its descriptors, block, measure, stat, value, n):

* `scorecard` -- D-621's card (`u_select.scorecard`): P, S1, S3a, S3b, S3c, S4a, S4b, S5a, S5b, S5c, each on its own
  eligible starts, exact-length runs read where they differed (`user_journey.Views`), as Stage 2 reads it.
* `extra` -- E-007 (e): the shares ahead at months 1, 2, 3 and P on the starts with 63 sessions (P must equal the
  card's: a refusing check); the mean net at months 1, 2, 3; CVaR10 of the month-3 net; P under a bankroll limit of
  $2,000 and $2,500 of cash spent before the first payout, and the share of starts past each limit; the effective
  number of independent starts (`n_eff_bartlett` at lag 63 on each start's months ahead over three, start order) and
  the non-overlapping count n / 63; the minimum detectable difference in P -- **blank**: TASK_QUEUE Q-16's calibrated
  P comparison is not on master (2026-11-15), and an uncalibrated one is what E-007 (1) found does not deliver its level.
* `path` -- the operator's measures (2026-11-15), each a distribution over starts (p10, p50, p90; shares where named):
  sessions to the first pass and to the first payout (window 126, an unreached start beyond; the share reached), the
  cash spent before each (among those reaching it by 126); sessions to break-even at daily resolution (window 252) and
  the share broken even by months 1, 2, 3, 6, 12 (each on the starts with that horizon left), the share of those broken
  even by 252 that later close below zero, the deepest fall from the running high after break-even; on the starts with
  twelve months: the share of months with a positive net change, the longest run of months without a payout, the
  standard deviation of the monthly net, payouts per month (count and dollars), the largest month's share of the
  twelve months' payout dollars. These read each start's long replay (its daily closes), not an exact-length run.
* `response` -- what the response did: the share of starts it acted on by months 1, 3, 12 (its first denial, placement
  or forfeiture close), that close's distribution (window 252), payouts denied and cash forfeited per start.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from extended import user_measures as M

BLOCKS = ("all", "judged")
MONTH = 21
FIRST_WINDOW = 126
YEAR_WINDOW = 252
BANKROLL_LIMITS = (2000.0, 2500.0)
BREAK_EVEN_MONTHS = (1, 2, 3, 6, 12)
ACTED_MONTHS = (1, 3, 12)
N_EFF_LAG = 63
MDD_NOTE = ("not computed: TASK_QUEUE Q-16's calibrated P comparison is not on master (2026-11-15); an uncalibrated MDD "
            "is what E-007 (1) found does not deliver its level")
#: the per-start file's columns (money as the engine books it, to the cent)
START_COLS = ("design", "arm", "response", "start_day", "start_date", "observed", "exact_runs_differing",
              "months_ahead", "net_month_1", "net_month_2", "net_month_3", "net_month_6", "net_month_12",
              "first_pass", "spent_before_first_pass", "first_payout", "spent_before_first_payout", "payouts",
              "break_even_day", "fell_back", "deepest_fall_after_break_even", "share_months_positive",
              "longest_months_without_payout", "sd_monthly_net", "payouts_per_month", "payout_cash_per_month",
              "largest_month_share", "response_day", "payouts_denied", "cash_forfeited")
MONEY_COLS = ("net_month_1", "net_month_2", "net_month_3", "net_month_6", "net_month_12", "spent_before_first_pass",
              "spent_before_first_payout", "deepest_fall_after_break_even", "sd_monthly_net", "payout_cash_per_month",
              "cash_forfeited")


def _which(block: str) -> str | None:
    if block not in BLOCKS:
        raise ValueError(f"a block is one of {BLOCKS}, got {block!r}")
    return None if block == "all" else "late"


# ------------------------------------------------------------------------------------------------ per start


def start_table(design: str, arm: str, response: str, outs: Sequence[Mapping[str, Any]]) -> pd.DataFrame:
    """One row a start: the record's long-replay values, the daily path measures, the evenness over twelve months (a
    start with 252 sessions), what the response did."""
    rows = []
    for x in outs:
        r, d, z = x["rec"], x["daily"], x["response"]
        nm = [np.nan if v is None else float(v) for v in r["net_month"]]
        ev = (M.evenness(nm, list(zip(r["pay_days"], r["pay_cash"]))) if int(r["observed"]) >= YEAR_WINDOW
              else {k: np.nan for k in ("share_months_positive", "longest_months_without_payout", "sd_monthly_net",
                                        "payouts_per_month", "payout_cash_per_month", "largest_month_share")})
        ahead = M.months_ahead(np.array([nm[:3]]))[0] if int(r["observed"]) >= 63 else np.nan
        rows.append({"design": design, "arm": arm, "response": response, "start_day": int(r["start_day"]),
                     "start_date": str(r["start_date"]), "observed": int(r["observed"]),
                     "exact_runs_differing": " ".join(str(int(h)) for h in x["differs"]),
                     "months_ahead": ahead, **{f"net_month_{k}": nm[k - 1] for k in (1, 2, 3, 6, 12)},
                     **{k: float(r[k]) for k in ("first_pass", "spent_before_first_pass", "first_payout",
                                                 "spent_before_first_payout")},
                     "payouts": len(r["pay_days"]), **{k: float(v) for k, v in d.items()},
                     **{k: float(v) for k, v in ev.items()},
                     **{k: float(z[k]) for k in ("response_day", "payouts_denied", "cash_forfeited")}})
    t = pd.DataFrame(rows, columns=list(START_COLS))
    return t


def rounded(t: pd.DataFrame) -> pd.DataFrame:
    """The per-start file's form: money to the cent (the summary rows are read before rounding)."""
    t = t.copy()
    for c in MONEY_COLS:
        t[c] = t[c].astype(float).round(2)
    return t


# ------------------------------------------------------------------------------------------------ the summary


def _row(section: str, block: str, measure: str, stat: str, value: float, n: int, note: str = "") -> dict[str, Any]:
    return {"section": section, "block": block, "measure": measure, "stat": stat, "value": float(value), "n": int(n),
            "note": note}


def _elig(t: pd.DataFrame, block: str, h: int) -> np.ndarray:
    m = t["observed"].to_numpy(int) >= int(h)
    if block == "judged":
        from propedge.research import u_select as S

        m &= t["start_date"].str[:4].astype(int).to_numpy() >= int(S.JUDGED_FIRST_YEAR)
    return m


def _dist(section: str, block: str, measure: str, x: np.ndarray, note: str = "") -> list[dict[str, Any]]:
    q = M.quantiles(x)
    return [_row(section, block, measure, f"p{p}", q[f"p{p}"], q["n"], note) for p in M.PERCENTILES]


def _days(section: str, block: str, measure: str, first: np.ndarray, window: int) -> list[dict[str, Any]]:
    n = len(first)
    out = [_row(section, block, measure, f"p{p}", M.days_quantile(first, window, p), n,
                f"window {window}; an unreached start beyond") for p in M.PERCENTILES]
    hit = np.isfinite(first) & (first <= window)
    out.append(_row(section, block, measure, f"share_by_{window}", float(hit.mean()) if n else np.nan, n))
    return out


def scorecard_rows(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    from propedge.research import u_select as S

    out = []
    for b in BLOCKS:
        card = S.scorecard(records, _which(b))
        out += [_row("scorecard", b, k, "value", v["value"], v["n"]) for k, v in card.items()]
    return out


def extra_rows(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    from propedge.research import u_select as S
    from propedge.research import user_journey as U

    out = []
    for b in BLOCKS:
        sub = S.block(records, _which(b), S.P_HORIZON)
        if not sub:
            out += [_row("extra", b, "P", "value", np.nan, 0)]
            continue
        V = U.Views(sub)
        nets = np.column_stack([U._net_at(V, MONTH * m) for m in M.P_MONTHS])
        spent = np.column_stack([V.at(MONTH * m)["spent_before_first_payout"].to_numpy(float) for m in M.P_MONTHS])
        p = M.p_by_month(nets)
        n = p["n"]
        out += [_row("extra", b, f"share_ahead_month_{m}", "value", p[f"share_month_{m}"], n) for m in M.P_MONTHS]
        out.append(_row("extra", b, "P", "value", p["P"], n))
        for i, m in enumerate(M.P_MONTHS):
            x = nets[:, i]
            out.append(_row("extra", b, f"mean_net_month_{m}", "value", float(np.nanmean(x)), int(np.isfinite(x).sum())))
        out.append(_row("extra", b, "cvar10_net_month_3", "value", M.cvar(nets[:, 2], 0.10),
                        int(np.isfinite(nets[:, 2]).sum()), "the mean of the worst ceil(0.10 n) month-3 nets"))
        for lim in BANKROLL_LIMITS:
            q = M.p_by_month(nets, spent=spent, limit=lim)
            out.append(_row("extra", b, f"P_bankroll_{int(lim)}", "value", q["P"], q["n"],
                            f"ahead only within ${lim:,.0f} of cash spent before the first payout"))
            out.append(_row("extra", b, f"share_spent_over_{int(lim)}", "value",
                            M.share_over_limit(spent[:, 2], lim), int(np.isfinite(spent[:, 2]).sum()),
                            "among starts with a first payout within the observed sessions (the month-3 reading)"))
        ahead = M.months_ahead(nets) / len(M.P_MONTHS)
        out.append(_row("extra", b, "n_eff_bartlett", "value", M.n_eff_bartlett(ahead, N_EFF_LAG), n,
                        f"each start's months ahead over three, start order; Bartlett lag {N_EFF_LAG}; a description"))
        out.append(_row("extra", b, "n_nonoverlapping", "value", n / float(S.P_HORIZON), n,
                        f"the starts over the reading's {S.P_HORIZON} sessions"))
        out.append(_row("extra", b, "mdd_P", "value", np.nan, n, MDD_NOTE))
    return out


def path_rows(t: pd.DataFrame) -> list[dict[str, Any]]:
    out = []
    for b in BLOCKS:
        e = _elig(t, b, FIRST_WINDOW)
        for ev, spent in (("first_pass", "spent_before_first_pass"), ("first_payout", "spent_before_first_payout")):
            f = t[ev].to_numpy(float)[e]
            out += _days("path", b, f"{ev}_days", f, FIRST_WINDOW)
            hit = np.isfinite(f) & (f <= FIRST_WINDOW)
            out += _dist("path", b, spent, t[spent].to_numpy(float)[e][hit], f"among starts reaching it by {FIRST_WINDOW}")
        e = _elig(t, b, YEAR_WINDOW)
        be = t["break_even_day"].to_numpy(float)
        out += _days("path", b, "break_even_days", be[e], YEAR_WINDOW)
        for m in BREAK_EVEN_MONTHS:
            em = _elig(t, b, MONTH * m)
            x = be[em]
            out.append(_row("path", b, "break_even", f"share_by_month_{m}",
                            float((np.isfinite(x) & (x <= MONTH * m)).mean()) if em.any() else np.nan, int(em.sum())))
        hit = e & np.isfinite(be)
        fb = t["fell_back"].to_numpy(float)[hit]
        out.append(_row("path", b, "break_even", "share_fell_back", float(fb.mean()) if len(fb) else np.nan, len(fb),
                        f"of the starts broken even within {YEAR_WINDOW}: a later close below zero"))
        out += _dist("path", b, "deepest_fall_after_break_even", t["deepest_fall_after_break_even"].to_numpy(float)[hit],
                     f"of the starts broken even within {YEAR_WINDOW}")
        for c in ("share_months_positive", "longest_months_without_payout", "sd_monthly_net", "payouts_per_month",
                  "payout_cash_per_month", "largest_month_share"):
            x = t[c].to_numpy(float)[e]
            out += _dist("path", b, c, x, "starts with twelve months" + ("; paid within them" if c ==
                                                                         "largest_month_share" else ""))
            if c in ("share_months_positive", "payouts_per_month", "payout_cash_per_month"):
                out.append(_row("path", b, c, "mean", float(np.nanmean(x)) if np.isfinite(x).any() else np.nan,
                                int(np.isfinite(x).sum())))
    return out


def response_rows(t: pd.DataFrame) -> list[dict[str, Any]]:
    out = []
    day = t["response_day"].to_numpy(float)
    for b in BLOCKS:
        for m in ACTED_MONTHS:
            em = _elig(t, b, MONTH * m)
            x = day[em]
            out.append(_row("response", b, "acted", f"share_by_month_{m}",
                            float((np.isfinite(x) & (x <= MONTH * m)).mean()) if em.any() else np.nan, int(em.sum())))
        e = _elig(t, b, YEAR_WINDOW)
        out += _days("response", b, "response_day", day[e], YEAR_WINDOW)
        for c in ("payouts_denied", "cash_forfeited"):
            x = t[c].to_numpy(float)[_elig(t, b, 1)]
            out.append(_row("response", b, c, "mean", float(np.nanmean(x)) if np.isfinite(x).any() else np.nan,
                            int(np.isfinite(x).sum()), "per start, its long replay"))
    return out


def summary(design: str, arm: str, resp: Any, outs: Sequence[Mapping[str, Any]]) -> tuple[list[dict], pd.DataFrame]:
    """One design, arm and response: (the summary rows, the per-start table)."""
    records = [x["rec"] for x in outs]
    t = start_table(design, arm, resp.name, outs)
    rows = scorecard_rows(records) + extra_rows(records) + path_rows(t) + response_rows(t)
    head = {"design": design, "arm": arm, "response": resp.name, "kind": resp.kind,
            "enforcement_p": float(resp.enforcement_p), "rtp": bool(resp.rtp), "rtp_warnings": int(resp.rtp_warnings),
            "ftp_label": resp.ftp_label}
    return [{**head, **r} for r in rows], t


def consistency_problems(rows: Sequence[Mapping[str, Any]], outs: Sequence[Mapping[str, Any]], what: str) -> list[str]:
    """The refusing checks on one reading: every run's payouts and fees against the engine's totals; the record from
    the long replay alone equal to `_one_start`'s wherever both are made; the extra P equal
    to the card's; P within each bankroll limit not above P, the $2,000 one not above the $2,500 one; every share in
    [0, 1]."""
    out = []
    for k in ("pay", "cash", "fee"):
        n = int(sum(x[f"{k}_bad"] for x in outs))
        if n:
            out.append(f"{what}: {n} runs' {k} check against the engine's totals fails")
    n = sum(1 for x in outs if x.get("record_same") is False)
    if n:
        out.append(f"{what}: on {n} starts the long replay's record is not user_journey._one_start's")
    by = {(r["section"], r["block"], r["measure"], r["stat"]): float(r["value"]) for r in rows}
    for b in BLOCKS:
        card, mine = by.get(("scorecard", b, "P", "value")), by.get(("extra", b, "P", "value"))
        if card is None or mine is None or not (np.isnan(card) and np.isnan(mine) or abs(card - mine) <= 1e-12):
            out.append(f"{what} {b}: the extra P {mine} is not the card's {card}")
        lo, hi = by.get(("extra", b, "P_bankroll_2000", "value")), by.get(("extra", b, "P_bankroll_2500", "value"))
        if None not in (lo, hi, mine) and np.isfinite(mine) and not (lo <= hi + 1e-12 and hi <= mine + 1e-12):
            out.append(f"{what} {b}: P within the limits ({lo}, {hi}) not ordered below P {mine}")
    for r in rows:
        if (r["stat"].startswith("share") or r["measure"].startswith("share")) and np.isfinite(r["value"]) and \
                not -1e-12 <= r["value"] <= 1 + 1e-12:
            out.append(f"{what}: {r['section']} {r['block']} {r['measure']} {r['stat']} = {r['value']} is not a share")
    return out


__all__ = ["BLOCKS", "START_COLS", "MONEY_COLS", "MDD_NOTE", "start_table", "rounded", "scorecard_rows", "extra_rows",
           "path_rows", "response_rows", "summary", "consistency_problems"]
