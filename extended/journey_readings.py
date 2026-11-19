"""Wave 3.1: the section `journey` of a reading on E-208's blocks -- `docs/MEASURES.md`'s measures read from each
block-bounded journey's closes 0 .. h (`extended.journey_measures`), beside `extended.user_readings`' sections. A module
of its own so that `user_readings`, which RD-01's, RD-02's and the CL reading's identity covers reach, imports nothing
new (`extended/identity_cover.py`'s rule: a file a runner's closure reaches is in its cover).

    from extended import journey_readings as JR, user_beside as B
    outs = B.run_starts(design, arm, B.BY_NAME["off"], job, starts, workers, journey=True)
    rows, table = JR.summary(design, arm, B.BY_NAME["off"], outs, budgets=(...,))     # the search years by default
    JR.consistency_problems(rows, outs, what)                                           # user_readings' own checks

**The rows** (`journey_rows`; each `section` `journey`, `block` `search` or `held_out`, `measure` / `stat`):
* `record` / `exact_runs_differing` -- the record each reading read (m-8): the long run cut at the block's end, and the
  starts whose exact h-session runs' event days differ from it;
* (2) `cash_to_first_pass`, (3) `evaluations_before_first_pass`, (6) `spent_before_first_payout_all` -- over all of
  `E_W`, unreached units at their censored lower bounds through W: `p10` .. `p90`, each with `p10_exact` .. (1 exact,
  0 "at least": MEASURES.md 1.3's strict rule, `journey_measures.strict_quantiles`), `share_passed_by_W` /
  `share_paid_by_W`, `n_censored`;
* (24) `bankroll_stop_{B}` at each budget -- `share_paid_within`, `share_run_out`, `share_censored`, the limit's
  `share_not_paid_within` (run out plus censored), and beside it `share_peak_over` (the peak through close W);
* (21) `longest_wait` -- from day 0 within 126 sessions, unpaid units censored at 127: `p10` .. `p90`,
  `share_paid_by_126`;
* (13) `S4a`, `S4b` -- ahead above 1e-6 at months 6 and 12, on `E_126` and `E_252`;
* (15) `return_on_money_at_risk`, (16) `monthly_net_4_12_median` (the mean beside, `monthly_net_4_12_mean`), (25)
  `peak_oop_12_months` -- `p10` .. `p90` on `E_252`;
* (31) `funded_lifetime_payouts` -- the Kaplan-Meier percentiles of payouts before loss (blank: beyond), each with the
  risk weight of the step it was read at (`p10_risk` ..), every step's risk and event weights (`n_at_risk_k`,
  `lost_at_k`; m-4), the counts,
  the censored share (by accounts and weighted) and every ending by kind; `funded_lifetime_sessions` beside.

`window` (W) is (2), (3), (6) and (24)'s, `lifetime_window` (31)'s, `budgets` (24)'s B: all the declaration's and the
operator's, none chosen here (the defaults are Q-44's ledger constants, MEASURES.md 7). The coin layer's three
readings (MEASURES.md 1.4) need the seed-paired runner (Wave 3.2) and are not rows here.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from extended import journey_measures as J
from extended import user_measures as M
from extended import user_readings as UR

#: (21)'s window: the longest wait within 126 sessions
WAIT_WINDOW = 126


def _dist(block: str, measure: str, x: Sequence[float], note: str) -> list[dict[str, Any]]:
    return UR._dist("journey", block, measure, np.asarray(x, float), note)


def _strict_rows(block: str, measure: str, vals: Sequence[tuple[float, bool]], window: int, reached: str
                 ) -> list[dict[str, Any]]:
    """A censored dollar (or count) quantity over every unit of `E_W`: the percentiles, each with its strict-rule flag
    (MEASURES.md 1.3, N-1), the share reached by W, the censored count."""
    q = J.strict_quantiles([v for v, _ in vals], [k for _, k in vals])
    n = q["n"]
    out = []
    for p in M.PERCENTILES:
        out.append(UR._row("journey", block, measure, f"p{p}", q[f"p{p}"], n,
                           f"every unit of E_{window}; unreached by {window}: a censored lower bound"))
        out.append(UR._row("journey", block, measure, f"p{p}_exact", float(q[f"p{p}_exact"]), n,
                           "1: exact; 0: \"at least\" (MEASURES.md 1.3's strict rule)"))
    out.append(UR._row("journey", block, measure, f"share_{reached}_by_{window}",
                       (1.0 - q["n_censored"] / n) if n else np.nan, n))
    out.append(UR._row("journey", block, measure, "n_censored", float(q["n_censored"]), n))
    return out


def journey_rows(outs: Sequence[Mapping[str, Any]], blocks: Sequence[str] = UR.BLOCKS, *,
                 budgets: Sequence[float] = (), window: int = UR.FIRST_WINDOW,
                 lifetime_window: int = UR.YEAR_WINDOW,
                 explained: Mapping[tuple[int, int], str] | None = None) -> list[dict[str, Any]]:
    """The section `journey` (the module docstring) on E-208's blocks, from each journey's closes 0 .. h. Every output
    must be a block-bounded journey (`user_beside.run_starts(..., journey=True)`), and every block one of E-208's.
    Corrective cycle 1 (M-2): the named blocks' starts must pass `user_readings.journey_check_problems` -- every start
    checked at every exact horizon below its run's length, and no exact-run difference unless `explained` (the
    declaration's reasons, by (start day, h)) explains it -- or the rows are refused."""
    if not UR.is_journey(outs):
        raise ValueError("REFUSED (W3.1): the journey rows read block-bounded journeys")
    UR.check_blocks(blocks, True, "the journey rows")
    bad = UR.journey_check_problems([x for x in outs if x["journey"]["block"] in blocks], explained)
    if bad:
        raise ValueError("REFUSED (W3.1, M-2): " + "; ".join(bad))
    W = int(window)
    out: list[dict[str, Any]] = []

    def obs(x: Mapping[str, Any]) -> int:
        return int(x["rec"]["observed"])

    def rel(x: Mapping[str, Any]) -> np.ndarray:
        return np.asarray(x["journey"]["rel"], float)

    for b in blocks:
        units = [x for x in outs if x["journey"]["block"] == b]
        out.append(UR._row("journey", b, "record", "exact_runs_differing",
                           float(sum(1 for x in units if x["differs"])), len(units),
                           "the long run cut at the block's end; the starts whose exact h-session runs' event days "
                           f"differ from it, of {sum(1 for x in units if x['checked'])} checked; each one explained by "
                           "a declared reason, or the reading is refused (m-8, M-2)"))
        ew = [x for x in units if obs(x) >= W]
        out += _strict_rows(b, "cash_to_first_pass",
                            [J.spent_to_event(rel(x), x["rec"]["first_pass"], W) for x in ew], W, "passed")
        out += _strict_rows(b, "evaluations_before_first_pass",
                            [J.evaluations_to_first_pass(x["journey"]["purchases"], x["rec"]["first_pass"], W)
                             for x in ew], W, "passed")
        out += _strict_rows(b, "spent_before_first_payout_all",
                            [J.spent_to_event(rel(x), x["rec"]["first_payout"], W) for x in ew], W, "paid")
        stop = J.bankroll_stop([rel(x) for x in ew], [x["rec"]["first_payout"] for x in ew], W, budgets)
        for lim in budgets:
            r = stop[float(lim)]
            for k in ("paid_within", "run_out", "censored", "not_paid_within", "peak_over"):
                note = {"not_paid_within": f"the limit's reading: run out plus censored, by {W}",
                        "peak_over": f"beside: the peak out-of-pocket through close {W} above the budget"}.get(
                            k, f"of E_{W}")
                out.append(UR._row("journey", b, f"bankroll_stop_{lim:g}", f"share_{k}", r[f"share_{k}"], r["n"],
                                   note))
        e126 = [x for x in units if obs(x) >= WAIT_WINDOW]
        waits = [J.longest_wait(x["rec"]["pay_days"], WAIT_WINDOW) for x in e126]
        d = J.days_reading([w if not c else np.nan for w, c in waits], WAIT_WINDOW)
        out += [UR._row("journey", b, "longest_wait", f"p{p}", d[f"p{p}"], d["n"],
                        f"from day 0 within {WAIT_WINDOW}; unpaid censored at {WAIT_WINDOW + 1}")
                for p in M.PERCENTILES]
        out.append(UR._row("journey", b, "longest_wait", f"share_paid_by_{WAIT_WINDOW}", d["share_by"], d["n"]))
        s4a = J.share_ahead_at([rel(x) for x in e126], WAIT_WINDOW)
        out.append(UR._row("journey", b, "S4a", "value", s4a["share"], s4a["n"], "ahead (above 1e-6) at month 6"))
        ey = [x for x in units if obs(x) >= UR.YEAR_WINDOW]
        s4b = J.share_ahead_at([rel(x) for x in ey], UR.YEAR_WINDOW)
        out.append(UR._row("journey", b, "S4b", "value", s4b["share"], s4b["n"], "ahead (above 1e-6) at month 12"))
        out += _dist(b, "return_on_money_at_risk", [J.return_on_money_at_risk(rel(x)) for x in ey],
                     "the 12-month net over the peak out-of-pocket")
        m412 = [J.monthly_net_4_12(rel(x)) for x in ey]
        out += _dist(b, "monthly_net_4_12_median", [m["median"] for m in m412], "the median of D_4 .. D_12")
        out += _dist(b, "monthly_net_4_12_mean", [m["mean"] for m in m412], "beside: their mean")
        out += _dist(b, "peak_oop_12_months", [J.peak_oop(rel(x)) for x in ey], "closes 0 .. 252")
        el = [x for x in units if obs(x) >= int(lifetime_window)]
        lt = J.funded_lifetime([x["journey"]["accounts"] for x in el], int(lifetime_window))
        for p in M.PERCENTILES:
            out.append(UR._row("journey", b, "funded_lifetime_payouts", f"p{p}", lt[f"p{p}"], lt["n_accounts"],
                               "Kaplan-Meier, each unit weighted equally; blank: beyond (the curve does not fall "
                               "so far)"))
            out.append(UR._row("journey", b, "funded_lifetime_sessions", f"p{p}", lt[f"sessions_p{p}"],
                               lt["n_accounts"], "beside: in sessions alive"))
        for p in M.PERCENTILES:                                        # m-4: the risk weight a percentile rests on
            out.append(UR._row("journey", b, "funded_lifetime_payouts", f"p{p}_risk", lt[f"p{p}_risk"],
                               lt["n_accounts"], "the risk weight of the step the percentile was read at"))
        for k, n_k, d_k in lt["steps_payouts"]:                       # m-4: every step's risk and event weights
            out.append(UR._row("journey", b, "funded_lifetime_payouts", f"n_at_risk_{k}", n_k, lt["n_accounts"],
                               f"the step {k} -> {k + 1} payouts: at risk (above {k}, or lost at {k})"))
            out.append(UR._row("journey", b, "funded_lifetime_payouts", f"lost_at_{k}", d_k, lt["n_accounts"]))
        for k in ("n_accounts", "n_units", "n_lost", "n_censored", "share_censored", "share_censored_weighted"):
            out.append(UR._row("journey", b, "funded_lifetime_payouts", k, float(lt[k]), lt["n_accounts"]))
        kinds = {**{f"censored_{k}": v for k, v in lt["censored_by_kind"].items()},
                 **{f"lost_{k}": v for k, v in lt["lost_by_kind"].items()}}
        for k, v in kinds.items():
            out.append(UR._row("journey", b, "funded_lifetime_payouts", k, float(v), lt["n_accounts"]))
    return out


def summary(design: str, arm: str, resp: Any, outs: Sequence[Mapping[str, Any]], *,
            blocks: Sequence[str] = UR.BLOCKS, budgets: Sequence[float] = (), window: int = UR.FIRST_WINDOW,
            lifetime_window: int = UR.YEAR_WINDOW,
            explained: Mapping[tuple[int, int], str] | None = None) -> tuple[list[dict], pd.DataFrame]:
    """`user_readings.summary` on block-bounded journeys (E-208's blocks; the search years by default) with the
    section `journey` added: (the rows, the per-start table)."""
    if not UR.is_journey(outs):
        raise ValueError("REFUSED (W3.1): a journey reading reads block-bounded journeys")
    rows, t = UR.summary(design, arm, resp, outs, blocks=blocks, budgets=budgets, explained=explained)
    head = {k: rows[0][k] for k in ("design", "arm", "response", "kind", "enforcement_p", "rtp", "rtp_warnings",
                                    "ftp_label")} if rows else {}
    more = journey_rows(outs, blocks, budgets=budgets, window=window, lifetime_window=lifetime_window,
                        explained=explained)
    return rows + [{**head, **r} for r in more], t


def consistency_problems(rows: Sequence[Mapping[str, Any]], outs: Sequence[Mapping[str, Any]], what: str, *,
                         blocks: Sequence[str] = UR.BLOCKS) -> list[str]:
    """`user_readings.consistency_problems` -- it holds the section `journey` too ((24)'s three states sum to one)."""
    return UR.consistency_problems(rows, outs, what, blocks=blocks)


__all__ = ["WAIT_WINDOW", "journey_rows", "summary", "consistency_problems"]
