"""EXPLORATORY (D-656, program U, U3): the user's journey read as ONE portfolio outcome -- pure functions that say which
of the journey's variables goes with a user being ahead, how much of the outcome is the design and how much the start
day, which designs on file are not beaten at once on the four things a user cares about, and three named picks by
limits declared in D-656. No engine, no market data, no file read here: `scripts/user_drivers.py` reads the result
files on record and hands their rows in. It counts no variant -- every row is a re-reading of a file on record -- and
it selects nothing: the menu is a reading aid, never a candidate (D-656 (5)).

What is computed, as D-656 declares it:

* **(2) Within a design, across start days** (`within_rows`): for one of U1's configurations at one arm and month, each
  variable's Spearman rank correlation with the net cash at that month and with the 0/1 "ahead", and a standardised
  ordinary-least-squares regression of each outcome on the six variables, each with a two-sided percentile interval
  from the moving-block bootstrap over start days (`user_journey.block_indices`: blocks of `BOOT_BLOCK` consecutive
  starts, `BOOT_DRAWS` draws, seed `BOOT_SEED`). `start_frame` holds the censoring rule: a variable not reached inside
  the month being read is read AT that month's end. `accounting_rows`: the mean net split into payouts and fees.
* **(3) Design against luck** (`variance_split`): the spread of the net across start days inside a design against the
  spread between the designs' means -- the share of all the variance that is the design.
* **(4) Between designs** (`between_rows`): across the cells on file (the hypothetical cells never among them), each
  scorecard measure's Spearman rank correlation with P and a standardised regression of P on `BETWEEN_REGRESSORS`, with
  an interval from resampling whole families (`CLUSTER_SEED`) -- a description of related designs, never a test.
* **(5) The frontier and the menu** (`frontier`, `menu`): the cells not beaten at once on `FRONTIER_MEASURES`, and
  three picks by `MENU_LIMITS` among cells whose share ahead at month 12 is at least `MENU_FLOOR`.

`DEFINITIONS` holds, for every variable and statistic, a one-line plain meaning and a one-line "how it is modelled";
`describe` and `short_name` put each design in plain words. They are written into the result file, which is what a
viewer shows (the Campaign Studio imports the file; no page is built here).

**The file is long: one row a figure**, read by the same nine columns in every section (`CORE`): `section`, `subject`
(what the figure is of), `measure` (which figure), `value`, `n`, `lo`, `hi` (an interval's ends, blank where there is
none), `unit` and `note`. `KEY` names a row once. The columns after them qualify a figure (arm, month, statistic,
outcome, variable ...) or describe its subject (name, family, description ...): `COLUMNS`, each one explained in
`scripts/user_drivers.py`'s docstring with every section and every measure name (`measure_names`).

Every blank is NaN in a number and the empty text elsewhere.
"""
from __future__ import annotations

import json
import math
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd
from scipy.stats import rankdata

from propedge.research import u_select as Sel
from propedge.research import user_journey as U

DECISION = "D-656"
STUDY = "U3"
RESULT = "user_drivers"
SCRIPT = "scripts/user_drivers.py"
READING = ("EXPLORATORY (D-656, program U, U3): the user's journey as one outcome -- which variable goes with being "
           "ahead, design against luck, the frontier and a menu by declared limits -- re-read from the result files "
           "on record; no engine run, no variant counted, nothing selected; beside the gate, never a verdict of it "
           "(D-234)")

ARM, BESIDE_ARM = Sel.ARM, Sel.BESIDE_ARM
ARMS = (ARM, BESIDE_ARM)
ALL = "all"
MONTH = U.MONTH
#: D-656 (1): the outcome is read at these months; (2): the within-design statistics at the first three
OUTCOME_MONTHS = (1, 2, 3, 6, 12)
WITHIN_MONTHS = (1, 2, 3)
#: D-656 (2): the moving-block bootstrap over start days -- "blocks of 63 starts, seed fixed in the script, as D-621
#: (3)"; the draws are U1's own count
BOOT_BLOCK = Sel.BOOT_BLOCK
BOOT_DRAWS = U.BOOT_DRAWS
BOOT_SEED = 20261900
#: D-656 (4): the interval between designs resamples whole families; its seed
CLUSTER_SEED = 20261901
#: every interval is the two-sided percentile interval at this level
INTERVAL = 0.95
#: the resamples handled at once (memory, not a statistic: the result is the same at any value)
CHUNK = 100

NET, AHEAD = "net", "ahead"
OUTCOMES = (NET, AHEAD)
BANKROLL, TO_PASS, TO_PAYOUT, FIRST_CASH, PER_FEE, BEFORE_PASS = (
    "bankroll", "sessions_to_first_pass", "sessions_to_first_payout", "first_payout_dollars",
    "payouts_per_fee_dollar", "cash_before_first_pass")
#: D-656 (1): the variables the operator named, in the row's order -- the regression's six
VARIABLES = (BANKROLL, TO_PASS, TO_PAYOUT, FIRST_CASH, PER_FEE, BEFORE_PASS)
#: beside the six, never in the regression (it is nearly a function of three of them): paid inside the month or not
PAID = "paid_by_month"
CORRELATED = (*VARIABLES, PAID)
SPEARMAN, BETA, R2 = "spearman", "beta", "r2"
#: the variables whose link with the net is partly arithmetic (`WITHIN_NOTES` says how): marked on their rows
ARITHMETIC_WITHIN = (BANKROLL, PER_FEE)
#: the scorecard measures that read the same nets as P, so their link with P is partly built in (`BETWEEN_NOTES`)
MECHANICAL_BETWEEN = ("S5a", "S4a")

#: D-656 (4): P regressed on these four scorecard measures
BETWEEN_REGRESSORS = ("S1", "S3a", "S3c", "S5a")
#: the sets the between-design statistics are read on: every cell on file but the hypothetical ones (D-656 (4): the
#: Lucid cells shown), and beside it the same without the upper-bound cells
SET_ALL, SET_NO_LUCID = "all_cells", "without_lucid"
#: the sets design-against-luck is read on: U1's nine configurations (D-656 (3)), and beside it the three rows to beat
SET_U1, SET_ROWS = "u1_configurations", "rows_to_beat"
ROWS_FAMILY = "rows_to_beat"

#: D-656 (5): not beaten at once on these four, each in its direction
FRONTIER_MEASURES = (("P", Sel.HIGHER), ("S1", Sel.LOWER), ("S3a", Sel.HIGHER), ("S5a", Sel.HIGHER))
#: D-656 (5): the three picks -- (name, the limit on S1 in dollars or None) -- "the coordinator's defaults, told to the
#: operator, and changed by a new row at the operator's word"; set after families 1 to 7 were read
MENU_LIMITS: tuple[tuple[str, float | None], ...] = (("lowest_cost", 2000.0), ("balanced", 2500.0),
                                                     ("best_result", None))
MENU_LIMIT_MEASURE = "S1"
#: D-656 (5): a pick is among cells whose share ahead at month 12 (S4b) is at least this
MENU_FLOOR_MEASURE = "S4b"
MENU_FLOOR = 0.95
#: D-656 (4): the cells left out of everything, and the cells shown as upper bounds -- the counts the row names
HYPOTHETICAL_LABEL = Sel.HYPOTHETICAL_LABEL
LUCID_LABEL = U.LUCID_LABEL
HYPOTHETICAL_DECLARED = 12
LUCID_DECLARED = 6

ROW_TO_BEAT, FAMILY_CELL, U1_CONFIG = "row_to_beat", "family_cell", "u1_configuration"
#: the name of the measure of a section `frontier` row and of a section `identity` row
ON_FRONTIER, HOLDS = "on_frontier", "holds"
TOL = 1e-9
NAN = float("nan")

SECTIONS = ("identity", "parameters", "definitions", "design_table", "within_design", "accounting", "design_vs_luck",
            "between_designs", "frontier", "menu", "funded_facts")
(IDENTITY, PARAMETERS, DEFINITIONS_SECTION, DESIGN_TABLE, WITHIN, ACCOUNTING, LUCK, BETWEEN, FRONTIER, MENU,
 FUNDED) = SECTIONS

#: the nine columns every figure is read by, the same in every section (one row a figure)
CORE = ("section", "subject", "measure", "value", "n", "lo", "hi", "unit", "note")
COLUMNS = ("section", "reading",
           # the figure (CORE) and the kind of its subject
           "subject", "subject_kind", "measure", "value", "n", "lo", "hi", "unit", "note",
           # what qualifies a figure
           "arm", "block", "month", "statistic", "outcome", "variable", "direction", "draws", "draws_valid",
           "mechanical",
           # what its subject is
           "name", "family", "family_decision", "base", "label", "description", "overrides",
           # frontier and menu
           "pool", "on_frontier", "dominated_by", "pick", "picked", "limit", "floor", "eligible", "tied",
           # definitions
           "meaning", "modelled",
           # identity
           "check", "holds", "compared", "differing", "refuses",
           # where a figure is from
           "source_file", "source_sha256", "source_section")
#: what names one row of every section but `identity` (whose rows are named by `check`)
KEY = ("section", "subject_kind", "subject", "arm", "month", "measure")
#: the kinds of subject beside a design's (`ROW_TO_BEAT`, `FAMILY_CELL`, `U1_CONFIG`)
DESIGN_SET, MENU_PICK, PARAMETER, IDENTITY_KIND = "design_set", "menu_pick", "parameter", "identity"
#: units: a scorecard measure's is `u_select.MEASURES`' (share, dollars, sessions, ratio)
FLAG, COUNT, CORRELATION, WEIGHT = "flag", "count", "correlation", "standardised_weight"
STATISTIC_UNITS = {SPEARMAN: CORRELATION, BETA: WEIGHT, R2: Sel.SHARE}

_BLANKS = ("", "nan", "NaN", "None")


def text(x: Any) -> str:
    return "" if x is None else str(x).strip()


def flag(x: Any) -> bool:
    return x is True or text(x) == "True"


def number(x: Any) -> float:
    s = text(x)
    return NAN if s in _BLANKS else float(s)


def same(a: Any, b: Any, tol: float = TOL) -> bool:
    """Two readings equal: both blank, or both numbers within `tol` (relative above 1)."""
    x, y = number(a), number(b)
    if not math.isfinite(x) or not math.isfinite(y):
        return (x != x and y != y) or x == y
    return abs(x - y) <= tol * max(1.0, abs(x), abs(y))


# ------------------------------------------------------------------------------------------------ the start days


def money_frame(records: Sequence[Mapping[str, Any]], month: int) -> dict[str, np.ndarray]:
    """One design's start days at one month, in start order: every start with the month's sessions left and a net and
    fees on record (`user_journey`'s eligibility) -- its net cash, the fees paid and the payouts received by the month's
    end (the net plus the fees: the cash moves only by fees and payouts)."""
    m = int(month)
    if not 1 <= m <= U.MONTHS:
        raise ValueError(f"a month is 1 to {U.MONTHS}, got {month!r}")
    recs = Sel.eligible(records, MONTH * m)
    net = np.array([float(r["net_month"][m - 1]) for r in recs], float)
    fees = np.array([float(r["fees_month"][m - 1]) for r in recs], float)
    keep = np.isfinite(net) & np.isfinite(fees)
    day = np.array([int(r["start_day"]) for r in recs], int)
    return {"start_day": day[keep], "net": net[keep], "fees": fees[keep], "payouts": net[keep] + fees[keep],
            "keep": keep, "records": [r for r, k in zip(recs, keep) if k]}


def start_frame(records: Sequence[Mapping[str, Any]], month: int) -> dict[str, Any]:
    """One design's start days at one month as the within-design statistics read them: the two outcomes (`net`, and
    `ahead`: 1 where the net is above zero) and the variables D-656 (1) names, each as U1 defines it -- with THE
    CENSORING RULE, so that every start has every variable and nothing after the month's end is used: with h the
    month's last session, **a variable not reached by h is read at h**. Sessions to the first pass and to the first
    payout are h where the event has not happened by h; the cash before the first payout (the bankroll) and before the
    first pass are the fees paid by h where it has not (before a first payout the cash moves only by fees, so that is
    exactly the cash out of pocket so far); the first payout's dollars are zero where none has arrived by h; `PAID` says
    which starts were paid by h. The payouts per fee dollar are the payouts received by h over the fees paid by h.
    A start with a variable still blank (no fee paid; a paid start with no cash on record) is dropped and counted
    (`dropped`). Arrays in start order."""
    f = money_frame(records, month)
    h = float(MONTH * int(month))
    recs = f["records"]

    def col(key: str) -> np.ndarray:
        return np.array([float(r[key]) for r in recs], float)

    first_pay, first_pass = col("first_payout"), col("first_pass")
    paid = np.isfinite(first_pay) & (first_pay <= h)
    passed = np.isfinite(first_pass) & (first_pass <= h)
    fees, net = f["fees"], f["net"]
    with np.errstate(divide="ignore", invalid="ignore"):
        per_fee = np.where(fees > 0, f["payouts"] / np.where(fees > 0, fees, 1.0), NAN)
    out = {NET: net, AHEAD: (net > 0).astype(float),
           BANKROLL: np.where(paid, col("spent_before_first_payout"), fees),
           TO_PASS: np.where(passed, first_pass, h),
           TO_PAYOUT: np.where(paid, first_pay, h),
           FIRST_CASH: np.where(paid, col("first_payout_cash"), 0.0),
           PER_FEE: per_fee,
           BEFORE_PASS: np.where(passed, col("spent_before_first_pass"), fees),
           PAID: paid.astype(float)}
    ok = np.ones(len(net), bool)
    for k in CORRELATED:
        ok &= np.isfinite(out[k])
    return {**{k: v[ok] for k, v in out.items()}, "start_day": f["start_day"][ok], "n": int(ok.sum()),
            "dropped": int((~ok).sum()), "horizon": int(h)}


# ------------------------------------------------------------------------------------------------ the statistics


def _standardise(a: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(each column of a (B, n, k) stack rescaled to mean 0 and spread 1 inside its resample -- a column that does not
    vary is all zero; which columns vary, (B, k))."""
    varies = (a.max(axis=1) - a.min(axis=1)) > 0
    mu = a.mean(axis=1, keepdims=True)
    sd = a.std(axis=1, keepdims=True)
    z = np.where(varies[:, None, :], (a - mu) / np.where(sd > 0, sd, 1.0), 0.0)
    return z, varies


def batch_stats(x: np.ndarray, y: np.ndarray, n_regressors: int) -> dict[str, np.ndarray]:
    """The statistics of a stack of samples. `x`: (B, n, kx) variables, the first `n_regressors` of them the
    regression's; `y`: (B, n, ky) outcomes. `spearman` (B, kx, ky): the Pearson correlation of the average ranks
    (ties share a rank). `beta` (B, n_regressors, ky) and `r2` (B, ky): ordinary least squares of each outcome on the
    regressors after every column is rescaled to mean 0 and spread 1 -- the standardised weights and the share of the
    outcome's variance the regressors explain together; where regressors are exactly collinear the least-norm
    solution. A statistic of a column that does not vary in a sample is blank there."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    n = x.shape[1]
    rx, vx = _standardise(rankdata(x, axis=1))
    ry, vy = _standardise(rankdata(y, axis=1))
    rho = np.einsum("bnk,bnj->bkj", rx, ry) / n
    rho[~(vx[:, :, None] & vy[:, None, :])] = NAN
    zx, vx = _standardise(x[:, :, :n_regressors])
    zy, vy = _standardise(y)
    gram = np.einsum("bnk,bnl->bkl", zx, zx) / n
    cross = np.einsum("bnk,bnj->bkj", zx, zy) / n
    beta = np.matmul(np.linalg.pinv(gram, hermitian=True), cross)
    r2 = (beta * cross).sum(axis=1)
    beta[~(vx[:, :, None] & vy[:, None, :])] = NAN
    r2[~vy] = NAN
    return {SPEARMAN: rho, BETA: beta, R2: r2}


def interval(draws: np.ndarray, level: float = INTERVAL) -> tuple[float, float, int]:
    """(the lower and upper ends of the two-sided percentile interval at `level` over the draws that hold a figure,
    how many do); blank with none."""
    d = np.asarray(draws, float)
    d = d[np.isfinite(d)]
    if not len(d):
        return NAN, NAN, 0
    a = 100.0 * (1.0 - float(level)) / 2.0
    return float(np.percentile(d, a)), float(np.percentile(d, 100.0 - a)), int(len(d))


WITHIN_NOTES = {
    BANKROLL: "a start day with no payout yet has lost exactly what it has spent, so part of this link is "
              "arithmetic; where no payout has arrived by the month's end it is the fees paid by then",
    TO_PASS: "the month's last session where no evaluation has passed by then",
    TO_PAYOUT: "the month's last session where no payout has arrived by then",
    FIRST_CASH: "zero where no payout has arrived by the month's end",
    PER_FEE: "net cash is the fees paid times this ratio less one, so this link is mostly arithmetic",
    BEFORE_PASS: "the fees paid by the month's end where no evaluation has passed by then",
    PAID: "1 where the first payout's cash has arrived by the month's end; shown beside the six variables, not in "
          "the regression",
}


def within_measure(statistic: str, outcome: str, variable: str = "") -> str:
    """The name of a within-design figure: `<statistic>.<outcome>.<variable>` (`spearman.net.bankroll`), and
    `r2.<outcome>` for the regression's R-squared."""
    return ".".join(x for x in (statistic, outcome, variable) if x)


def between_measure(statistic: str, key: str = "") -> str:
    """The name of a between-design figure: `<statistic>.<scorecard key>` (`spearman.S1`, `beta.S3a`), and `r2`."""
    return ".".join(x for x in (statistic, key) if x)


def within_rows(frame: Mapping[str, Any], *, block: int = BOOT_BLOCK, draws: int = BOOT_DRAWS, seed: int = BOOT_SEED,
                level: float = INTERVAL, chunk: int = CHUNK) -> list[dict[str, Any]]:
    """D-656 (2) on one `start_frame`: for each outcome (`net`, `ahead`) each variable's Spearman rank correlation
    (`CORRELATED`: the six and the paid-or-not indicator), the standardised regression's weight on each of the six
    (`VARIABLES`) and its R-squared -- each with its percentile interval from the moving-block bootstrap over the
    frame's start days in start order (`user_journey.block_indices`: blocks of `block` consecutive starts, `draws`
    resamples, `seed`); every statistic is recomputed inside each resample, ranks and rescaling included. The interval
    is blank with fewer starts than one block. For `ahead` (0 or 1) the regression is a linear probability model."""
    n = int(frame["n"])
    rows: list[dict[str, Any]] = []
    if n < 3:
        return rows
    x = np.column_stack([frame[k] for k in CORRELATED])
    y = np.column_stack([frame[k] for k in OUTCOMES])
    point = batch_stats(x[None], y[None], len(VARIABLES))
    idx = U.block_indices(n, block, draws=draws, seed=seed)
    boot: dict[str, np.ndarray] | None = None
    if idx is not None:
        parts = [batch_stats(x[idx[i:i + chunk]], y[idx[i:i + chunk]], len(VARIABLES))
                 for i in range(0, len(idx), int(chunk))]
        boot = {k: np.concatenate([p[k] for p in parts], axis=0) for k in (SPEARMAN, BETA, R2)}

    def row(outcome: str, variable: str, statistic: str, value: float, sample: np.ndarray | None) -> dict[str, Any]:
        lo, hi, valid = interval(sample, level) if sample is not None else (NAN, NAN, 0)
        return {"section": WITHIN, "measure": within_measure(statistic, outcome, variable),
                "unit": STATISTIC_UNITS[statistic], "outcome": outcome, "variable": variable, "statistic": statistic,
                "value": float(value), "lo": lo, "hi": hi, "n": n, "draws": int(draws) if idx is not None else 0,
                "draws_valid": valid, "mechanical": variable in ARITHMETIC_WITHIN,
                "note": WITHIN_NOTES.get(variable, "")}

    for j, outcome in enumerate(OUTCOMES):
        for i, v in enumerate(CORRELATED):
            rows.append(row(outcome, v, SPEARMAN, point[SPEARMAN][0, i, j],
                            None if boot is None else boot[SPEARMAN][:, i, j]))
        for i, v in enumerate(VARIABLES):
            rows.append(row(outcome, v, BETA, point[BETA][0, i, j], None if boot is None else boot[BETA][:, i, j]))
        rows.append(row(outcome, "", R2, point[R2][0, j], None if boot is None else boot[R2][:, j]))
    return rows


ACCOUNTING_STATS = ("mean_net", "mean_payouts", "mean_fees", "share_ahead", "sd_net", "payouts_per_fee_dollar_pooled",
                    "spread_share_payouts", "spread_share_fees")
ACCOUNTING_UNITS = {"mean_net": Sel.DOLLARS, "mean_payouts": Sel.DOLLARS, "mean_fees": Sel.DOLLARS,
                    "share_ahead": Sel.SHARE, "sd_net": Sel.DOLLARS, "payouts_per_fee_dollar_pooled": Sel.RATIO,
                    "spread_share_payouts": Sel.SHARE, "spread_share_fees": Sel.SHARE}


def accounting(frame: Mapping[str, np.ndarray]) -> dict[str, float]:
    """The accounting split of one `money_frame`: the mean net is the mean payouts received less the mean fees paid;
    the share of starts ahead; the net's standard deviation across starts (ddof 1, as U1's); the payouts over the fees
    pooled over the starts; and the split of the net's SPREAD -- the covariance of the net with the payouts, and with
    minus the fees, each over the net's variance: the two sum to one, and say whether start days differ in their net
    because they were paid differently or because they paid different fees."""
    net, pay, fees = (np.asarray(frame[k], float) for k in ("net", "payouts", "fees"))
    n = len(net)
    if not n:
        return {k: NAN for k in ACCOUNTING_STATS} | {"n": 0}
    var = float(np.var(net))
    with np.errstate(divide="ignore", invalid="ignore"):
        from_pay = float(np.mean((net - net.mean()) * (pay - pay.mean())) / var) if var > 0 else NAN
        from_fees = float(np.mean((net - net.mean()) * -(fees - fees.mean())) / var) if var > 0 else NAN
        pooled = float(pay.sum() / fees.sum()) if fees.sum() > 0 else NAN
    return {"mean_net": float(net.mean()), "mean_payouts": float(pay.mean()), "mean_fees": float(fees.mean()),
            "share_ahead": float((net > 0).mean()), "sd_net": float(np.std(net, ddof=1)) if n > 1 else NAN,
            "payouts_per_fee_dollar_pooled": pooled, "spread_share_payouts": from_pay,
            "spread_share_fees": from_fees, "n": int(n)}


LUCK_STATS = ("design_share", "start_day_share", "between_variance", "within_variance", "total_variance",
              "sd_of_design_means", "mean_sd_across_starts", "designs")
LUCK_UNITS = {"design_share": Sel.SHARE, "start_day_share": Sel.SHARE, "between_variance": "dollars_squared",
              "within_variance": "dollars_squared", "total_variance": "dollars_squared",
              "sd_of_design_means": Sel.DOLLARS, "mean_sd_across_starts": Sel.DOLLARS, "designs": COUNT}


def variance_split(nets: Mapping[str, Sequence[float]]) -> dict[str, float]:
    """D-656 (3), design against luck. `nets`: {design: its starts' net at one month}. Every start day of every design
    is pooled; the pooled variance (around the grand mean) is exactly the variance BETWEEN the designs' means (each
    design weighted by its starts) plus the variance WITHIN the designs (across start days, around each design's own
    mean). `design_share` is the between part over the total -- the share of the spread that is the design -- and
    `start_day_share` the rest. Beside, U1's form: the standard deviation (ddof 1) of the designs' means and the mean
    of the designs' standard deviations across starts."""
    arrays = {d: np.asarray(v, float) for d, v in nets.items()}
    arrays = {d: v[np.isfinite(v)] for d, v in arrays.items()}
    arrays = {d: v for d, v in arrays.items() if len(v)}
    out = {k: NAN for k in LUCK_STATS} | {"n": 0}
    if len(arrays) < 2:
        return out
    pooled = np.concatenate(list(arrays.values()))
    grand, total_n = float(pooled.mean()), len(pooled)
    between = float(sum(len(v) * (float(v.mean()) - grand) ** 2 for v in arrays.values()) / total_n)
    within = float(sum(((v - v.mean()) ** 2).sum() for v in arrays.values()) / total_n)
    total = between + within
    means = np.array([float(v.mean()) for v in arrays.values()])
    sds = np.array([float(np.std(v, ddof=1)) if len(v) > 1 else NAN for v in arrays.values()])
    return {"design_share": between / total if total > 0 else NAN,
            "start_day_share": within / total if total > 0 else NAN,
            "between_variance": between, "within_variance": within, "total_variance": float(np.var(pooled)),
            "sd_of_design_means": float(np.std(means, ddof=1)),
            "mean_sd_across_starts": float(np.nanmean(sds)) if np.isfinite(sds).any() else NAN,
            "designs": float(len(arrays)), "n": int(total_n)}


# ------------------------------------------------------------------------------------------------ between designs


def _spearman(a: np.ndarray, b: np.ndarray) -> tuple[float, int]:
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 3:
        return NAN, int(ok.sum())
    s = batch_stats(a[ok][None, :, None], b[ok][None, :, None], 1)
    return float(s[SPEARMAN][0, 0, 0]), int(ok.sum())


def between_stats(measures: Mapping[str, np.ndarray], *, primary: str = Sel.PRIMARY_KEY,
                  regressors: Sequence[str] = BETWEEN_REGRESSORS) -> dict[str, Any]:
    """D-656 (4) on one set of cells (`measures`: {scorecard key: the cells' values, a blank NaN}): `spearman` -- each
    other measure's rank correlation with P over the cells that hold both; `beta` and `r2` -- P regressed on the
    regressors, every column rescaled to mean 0 and spread 1, over the cells that hold all of them; each with the
    cells it was read on."""
    p = np.asarray(measures[primary], float)
    out: dict[str, Any] = {SPEARMAN: {}, BETA: {}, R2: (NAN, 0)}
    for k, v in measures.items():
        if k != primary:
            out[SPEARMAN][k] = _spearman(np.asarray(v, float), p)
    x = np.column_stack([np.asarray(measures[k], float) for k in regressors])
    ok = np.isfinite(p) & np.isfinite(x).all(axis=1)
    n = int(ok.sum())
    if n > len(regressors) + 1:
        s = batch_stats(x[ok][None], p[ok][None, :, None], len(regressors))
        out[BETA] = {k: (float(s[BETA][0, i, 0]), n) for i, k in enumerate(regressors)}
        out[R2] = (float(s[R2][0, 0]), n)
    else:
        out[BETA] = {k: (NAN, n) for k in regressors}
        out[R2] = (NAN, n)
    return out


BETWEEN_NOTES = {
    "S5a": "both are read off the same month-3 net cash (how low the unlucky tenth is, and how many start days are "
           "above zero), so part of this link is mechanical",
    "S4a": "it reads the same net cash three months later, so it is related to the share ahead by construction",
    "S4b": "nearly every design has nearly every start day ahead at month 12, so there is little spread to rank on",
}


def between_rows(cells: Sequence[Mapping[str, Any]], label: str, *, draws: int = BOOT_DRAWS, seed: int = CLUSTER_SEED,
                 level: float = INTERVAL) -> list[dict[str, Any]]:
    """D-656 (4) as section `between_designs` rows on one set of cells (`label`). `cells`: each {`design`, `family`,
    `measures`: {key: value}}. The interval resamples WHOLE FAMILIES with replacement (as many families as there are,
    `draws` times, `seed`; a family drawn twice counts twice) and recomputes every statistic on each resample -- the
    cells of a family share a base and a lever, so they are not independent readings. A resample on which a statistic
    cannot be computed (too few cells, a column that does not vary) is left out and `draws_valid` says how many held.
    A description of related designs, never a test."""
    keys = [m.key for m in Sel.MEASURES]
    table = {k: np.array([number(c["measures"].get(k)) for c in cells], float) for k in keys}
    point = between_stats(table)
    families = sorted({text(c["family"]) for c in cells})
    members = [np.array([i for i, c in enumerate(cells) if text(c["family"]) == f], int) for f in families]
    rng = np.random.default_rng(int(seed))
    picks = rng.integers(0, len(families), size=(int(draws), len(families))) if len(families) > 1 else None
    boot: dict[tuple[str, str], list[float]] = {}
    if picks is not None:
        for pick in picks:
            take = np.concatenate([members[j] for j in pick])
            s = between_stats({k: v[take] for k, v in table.items()})
            for k, (v, _) in s[SPEARMAN].items():
                boot.setdefault((SPEARMAN, k), []).append(v)
            for k, (v, _) in s[BETA].items():
                boot.setdefault((BETA, k), []).append(v)
            boot.setdefault((R2, ""), []).append(s[R2][0])

    def row(statistic: str, key: str, value: float, n: int) -> dict[str, Any]:
        lo, hi, valid = interval(np.array(boot.get((statistic, key), []), float), level)
        return {"section": BETWEEN, "subject": label, "subject_kind": DESIGN_SET,
                "arm": ARM, "block": ALL,
                "measure": between_measure(statistic, key), "unit": STATISTIC_UNITS[statistic],
                "statistic": statistic, "outcome": Sel.PRIMARY_KEY, "variable": key, "value": float(value),
                "lo": lo, "hi": hi, "n": int(n), "draws": int(draws) if picks is not None else 0,
                "draws_valid": valid, "mechanical": key in MECHANICAL_BETWEEN,
                "note": BETWEEN_NOTES.get(key, "") if statistic != R2 else ""}

    rows = [row(SPEARMAN, k, *point[SPEARMAN][k]) for k in keys if k != Sel.PRIMARY_KEY]
    rows += [row(BETA, k, *point[BETA][k]) for k in BETWEEN_REGRESSORS]
    rows.append(row(R2, "", *point[R2]))
    return rows


# ------------------------------------------------------------------------------------------------ frontier and menu


def in_pool(cell: Mapping[str, Any]) -> bool:
    """A cell the frontier and the menu may name: not hypothetical (never among the cells at all), not an upper bound
    (a Lucid cell's figures are bounds on two unpriced fees, D-656 (5)), and holding all four frontier measures."""
    if text(cell.get("label")) in (HYPOTHETICAL_LABEL, LUCID_LABEL):
        return False
    return all(math.isfinite(number(cell["measures"].get(k))) for k, _ in FRONTIER_MEASURES)


def _signed(cell: Mapping[str, Any]) -> tuple[float, ...]:
    return tuple(number(cell["measures"][k]) * (1.0 if d == Sel.HIGHER else -1.0) for k, d in FRONTIER_MEASURES)


def frontier(cells: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    """D-656 (5): {design: {`pool`, `on_frontier`, `dominated_by`}}. Among the cells of the pool (`in_pool`) a cell is
    BEATEN AT ONCE (dominated) when another is at least as good on all four of `FRONTIER_MEASURES` -- the share ahead
    higher, the cash before the first payout lower, the share paid by session 21 higher, the unlucky tenth's month-3
    net higher -- and better on at least one; the frontier is the cells no other beats so. Two cells equal on all four
    do not beat each other. `dominated_by`: the cells that beat it, in the order given."""
    pool = [c for c in cells if in_pool(c)]
    signed = {text(c["design"]): _signed(c) for c in pool}
    out: dict[str, dict[str, Any]] = {}
    for c in cells:
        name = text(c["design"])
        if name not in signed:
            out[name] = {"pool": False, "on_frontier": False, "dominated_by": []}
            continue
        mine = signed[name]
        beaten = [o for o, theirs in signed.items() if o != name
                  and all(t >= m for t, m in zip(theirs, mine)) and any(t > m for t, m in zip(theirs, mine))]
        out[name] = {"pool": True, "on_frontier": not beaten, "dominated_by": beaten}
    return out


def menu(cells: Sequence[Mapping[str, Any]], *, limits: Sequence[tuple[str, float | None]] = MENU_LIMITS,
         floor: float = MENU_FLOOR) -> list[dict[str, Any]]:
    """D-656 (5): the three named picks. For each (name, limit): among the cells of the pool (`in_pool`) whose share
    ahead at month 12 (S4b) is at least `floor` -- so a plan that stops for good is not offered as cheap -- and whose
    cash before the first payout (S1) is at most the limit (no limit: every such cell), the cell with the highest P.
    A tie on P goes to the lower S1, then the higher S3a, then the higher S5a, then the first in the order given;
    `tied` is how many cells share the highest P and `eligible` how many were inside the limit. A pick with no
    eligible cell names none. A reading aid: no pick is a candidate."""
    out = []
    for name, limit in limits:
        ok = []
        for i, c in enumerate(cells):
            if not in_pool(c):
                continue
            m = c["measures"]
            s4b, s1 = number(m.get(MENU_FLOOR_MEASURE)), number(m.get(MENU_LIMIT_MEASURE))
            if not (math.isfinite(s4b) and s4b >= float(floor)):
                continue
            if limit is not None and not s1 <= float(limit):
                continue
            ok.append((-number(m["P"]), s1, -number(m["S3a"]), -number(m["S5a"]), i))
        ok.sort()
        best = cells[ok[0][4]] if ok else None
        out.append({"pick": name, "limit": NAN if limit is None else float(limit), "floor": float(floor),
                    "design": text(best["design"]) if best is not None else "", "eligible": len(ok),
                    "tied": int(sum(1 for o in ok if o[0] == ok[0][0])) if ok else 0})
    return out


# ------------------------------------------------------------------------------------------------ plain descriptions

#: the families on file, in the order declared: (the row that declared it, its name, the plain name, what it varies)
FAMILIES: tuple[tuple[str, str, str, str], ...] = (
    ("D-629", "budget", "Purchase budget", "how many evaluations may be bought in a month"),
    ("D-630", "entry", "Cost of entry", "three ways of buying fewer evaluations before the first payout"),
    ("D-635", "seats", "Number of accounts", "how many accounts are held at once"),
    ("D-639", "hours", "Trading hours", "the coin design traded in one session window only"),
    ("D-644", "firms", "Second firm (Lucid)", "Lucid accounts added beside the five Topstep accounts"),
    ("D-646", "consistency", "Consistency payout path", "the funded accounts paid by the Consistency rule"),
    ("D-653", "plan", "Flat funded plan", "every funded trade the same size at 1R, with no bold opening trade"),
)
FAMILY_NAMES = {f: name for _, f, name, _ in FAMILIES} | {ROWS_FAMILY: "Registered designs"}
FAMILY_WHAT = {f: what for _, f, _, what in FAMILIES} | {
    ROWS_FAMILY: "the three registered designs every family is judged against"}
FAMILY_DECISIONS = {f: d for d, f, _, _ in FAMILIES} | {ROWS_FAMILY: "D-621"}
#: the registered designs in plain words (design names, not results)
ROW_DESCRIPTIONS = {
    "p14": "P-14 as registered: the breakout design, five accounts (the row to beat)",
    "p15": "P-15 as registered: the coin design with the 25-point stop, five accounts",
    "p16": "P-16 as registered: the coin design with the 37.5-point stop, five accounts",
}
ROW_NAMES = {"p14": "P-14", "p15": "P-15", "p16": "P-16"}
WINDOW_NAMES = {"london": "London", "us": "US", "asia": "Asia"}
#: NQ's tick is a quarter of a point (the window bases are named by their stop in ticks)
TICKS_PER_POINT = 4


def _dollars(x: float) -> str:
    return f"${float(x):,.0f}"


def _whole_or_decimal(x: float) -> str:
    return f"{float(x):g}"


def describe(design: str, family: str, base: str, overrides: Any = "") -> str:
    """A cell in plain words, built from its family, its base and the overrides its family file records (so no
    figure is typed: every number in the sentence is the cell's own setting). An unknown shape falls back to the
    cell's name beside its base."""
    design, family, base = text(design), text(family), text(base)
    if family == ROWS_FAMILY:
        return ROW_DESCRIPTIONS.get(design, design)
    try:
        o = overrides if isinstance(overrides, Mapping) else json.loads(text(overrides) or "{}")
    except ValueError:
        o = {}
    on = Sel.BASE_LABEL.get(base, base)
    if family == "budget" and "purchase_budget" in o:
        b = o["purchase_budget"]
        return (f"{on} with no limit on evaluation purchases" if b is None else
                f"{on} with at most {int(b[0])} evaluation purchases per {int(b[1])} sessions")
    if family == "entry":
        if "wallet_stop" in o:
            return f"{on}, buying no more evaluations while more than {_dollars(o['wallet_stop'])} is out of pocket"
        if "pause_after_funded" in o:
            k = int(o["pause_after_funded"])
            return (f"{on}, buying no more evaluations while {k} funded account{'s' if k != 1 else ''} "
                    "is held and no payout has arrived")
        if "seat_ramp" in o:
            return f"{on}, starting with {int(o['seat_ramp'])} accounts and adding one for each payout received"
    if family == "seats" and "accounts" in o:
        k = int(o["accounts"])
        return f"{on} with {k} account{'s' if k != 1 else ''} instead of five"
    if family == "hours" and base in Sel.WINDOW_BASES:
        w = Sel.WINDOW_BASES[base]
        return (f"The coin design with the {_whole_or_decimal(w['stop_ticks'] / TICKS_PER_POINT)}-point stop, "
                f"traded in the {WINDOW_NAMES.get(w['window'], w['window'])} session only")
    if family == "firms" and base in Sel.JOINT_BASES:
        j = Sel.JOINT_BASES[base]
        k = int(j["lucid_seats"])
        when = "from day 0" if j["opens"] is None else "opened once the first payout has arrived"
        return (f"P-16 on five Topstep accounts plus {k} Lucid account{'s' if k != 1 else ''} {when} "
                "(an upper bound: two Lucid fees are unpriced)")
    if family == "consistency" and o.get("protocol", {}).get("payout_path") == "consistency":
        cap = o.get("funded_cap_share")
        tail = "" if cap is None else f", funded size capped at {float(cap):.0%} of the allowance"
        return f"{on} with funded accounts on the Consistency payout path{tail}"
    if family == "plan" and Sel.FUNDED_PLAN in o:
        p = o[Sel.FUNDED_PLAN]
        path = "Consistency" if o.get("protocol", {}).get("payout_path") == "consistency" else "Standard"
        return (f"{on} with a flat funded plan: {_dollars(p['risk'])} risked per trade at "
                f"{_whole_or_decimal(p['rr'])}R, {path} payout path")
    return f"{design} (on {on})" if on else design


def short_name(design: str, family: str, base: str, overrides: Any = "") -> str:
    """A cell's short label for a chart, built as `describe` builds its sentence: the base and the one setting the
    cell changes. An unknown shape falls back to the cell's name."""
    design, family, base = text(design), text(family), text(base)
    on = Sel.BASE_LABEL.get(base, base)
    if family == ROWS_FAMILY:
        return ROW_NAMES.get(design, design)
    try:
        o = overrides if isinstance(overrides, Mapping) else json.loads(text(overrides) or "{}")
    except ValueError:
        o = {}
    if family == "budget" and "purchase_budget" in o:
        b = o["purchase_budget"]
        return f"{on}: no budget" if b is None else f"{on}: budget {int(b[0])}"
    if family == "entry":
        if "wallet_stop" in o:
            return f"{on}: wallet stop {_dollars(o['wallet_stop'])}"
        if "pause_after_funded" in o:
            return f"{on}: pause at {int(o['pause_after_funded'])} funded"
        if "seat_ramp" in o:
            return f"{on}: ramp from {int(o['seat_ramp'])}"
    if family == "seats" and "accounts" in o:
        k = int(o["accounts"])
        return f"{on}: {k} account{'s' if k != 1 else ''}"
    if family == "hours" and base in Sel.WINDOW_BASES:
        w = Sel.WINDOW_BASES[base]
        return (f"Coin {_whole_or_decimal(w['stop_ticks'] / TICKS_PER_POINT)}, "
                f"{WINDOW_NAMES.get(w['window'], w['window'])} hours")
    if family == "firms" and base in Sel.JOINT_BASES:
        j = Sel.JOINT_BASES[base]
        return f"P-16 + {int(j['lucid_seats'])} Lucid ({'day 0' if j['opens'] is None else 'after payout'})"
    if family == "consistency" and o.get("protocol", {}).get("payout_path") == "consistency":
        cap = o.get("funded_cap_share")
        return f"{on}: Consistency" + ("" if cap is None else f", cap {float(cap):.0%}")
    if family == "plan" and Sel.FUNDED_PLAN in o:
        cons = o.get("protocol", {}).get("payout_path") == "consistency"
        return f"{on}: flat {_dollars(o[Sel.FUNDED_PLAN]['risk'])}" + (" Consistency" if cons else "")
    return design


# ------------------------------------------------------------------------------------------------ the definitions

#: what a viewer shows for every variable, measure, statistic and convention: (kind, key, name, what it means, how it
#: is modelled). Written for a reader who is not a statistician; every figure in a sentence is a constant of this
#: module or of the modules it imports.
_PCT = f"{INTERVAL:.0%}"
_P_MONTHS = f"{Sel.P_MONTHS[0]} to {Sel.P_MONTHS[-1]}"
_H = {m.key: m.horizon for m in Sel.MEASURES}
DEFINITIONS: tuple[tuple[str, str, str, str, str], ...] = (
    ("convention", "unit", "A user = a start day",
     "One user is one day on which someone could have started the design from nothing: fresh cash, fresh accounts.",
     "Every trading day of the development data is taken as a start, and the design's own trades are replayed from "
     "it in historical order. Everyone who starts on the same day gets the same trades, so 'across users' means "
     "across start days; neighbouring start days share most of their history."),
    ("convention", "month", "A month",
     f"A month here is {MONTH} trading sessions, counted from the start day.",
     f"Month 1 ends at session {MONTH}, month 3 at session {MONTH * 3}, month 12 at session {MONTH * 12}. A reading "
     "at a month uses only the start days with that many sessions left in the data."),
    ("convention", "arm", "The cautious arm",
     "Every figure is read with the design's trade results marked down to a cautious level, not at their average.",
     "Each trade outcome is shifted down to the one-sided 95 % lower confidence bound the design's own test read "
     "(the 'verdict' arm). The unshifted reading (the 'point' arm) is kept beside in the result file."),
    ("convention", "bad_case", "The bad case (p90, p10)",
     "For costs and waits the figure quoted is the level nine start days in ten stay under; for money made, the "
     "level nine in ten stay above.",
     "The 90th percentile across start days for a cost or a wait, the 10th percentile for a net (linear "
     "interpolation between start days, as the start-day study reads them)."),
    ("variable", NET, "Net cash",
     "What a user has made or lost so far: payouts received minus every fee paid.",
     f"The replay's cash at the end of the month less the cash at the start, at months "
     f"{', '.join(str(m) for m in OUTCOME_MONTHS)}."),
    ("variable", AHEAD, "Ahead",
     "Whether the user has more cash than they started with.",
     "1 where the net cash at the month's end is above zero, else 0; the 'share ahead' is the share of start days "
     "with a 1."),
    ("variable", BANKROLL, "Bankroll needed (cash before the first payout)",
     "The most a user is out of pocket before any money comes back.",
     "The fees paid up to the day the first payout's cash arrives. For a start with no payout by the month being "
     "read: the fees paid by that month's end."),
    ("variable", TO_PASS, "Sessions to the first evaluation pass",
     "How long until the first evaluation account is passed.",
     "The session on which the first evaluation passes, counted from the start day; the month's last session where "
     "none has passed by then."),
    ("variable", TO_PAYOUT, "Sessions to the first payout",
     "How long until the first payout's cash is in hand.",
     "The session on which the first payout's cash arrives (after the firm's payout delay); the month's last "
     "session where none has arrived by then."),
    ("variable", FIRST_CASH, "First payout (dollars)",
     "How large the first payout is.",
     "The cash of the first payout received; zero where none has arrived by the month's end."),
    ("variable", PER_FEE, "Payouts per fee dollar",
     "How many dollars have come back for each dollar paid in fees.",
     "The payouts received by the month's end over the fees paid by then. Above 1 the user is ahead: the net is the "
     "fees times this ratio less one, so its link with the net is mostly arithmetic."),
    ("variable", BEFORE_PASS, "Cash before the first pass",
     "What a user has paid before the first evaluation is passed.",
     "The fees paid up to the day of the first pass; the fees paid by the month's end where none has passed by "
     "then."),
    ("variable", PAID, "Paid inside the month",
     "Whether any payout has arrived by the month's end.",
     "1 where the first payout's cash has arrived by the month's last session, else 0. Shown beside the six "
     "variables; left out of the regression because three of them already carry it."),
    ("measure", "P", f"Share ahead, months {_P_MONTHS}",
     "Of all the days a user could have started, the share on which they were ahead, averaged over the ends of "
     f"months {_P_MONTHS}.",
     f"The mean of the three shares of start days with net cash above zero at months {_P_MONTHS}, on the start days "
     f"with {Sel.P_HORIZON} sessions left. The program's primary measure (D-621)."),
    ("measure", "S1", "Bankroll needed (bad case)",
     "The cash a user should have ready: nine start days in ten needed no more than this before the first payout.",
     f"The 90th percentile, over the start days paid within {_H['S1']} sessions, of the cash spent before the first "
     "payout."),
    ("measure", "S3a", f"Share paid by day {MONTH}",
     "The share of start days on which the first payout arrived within the first month.",
     f"The share of start days whose first payout's cash arrived by session {MONTH}."),
    ("measure", "S3b", "Sessions to the first payout (bad case)",
     "The wait for the first payout that nine start days in ten stayed under.",
     f"The 90th percentile of the sessions to the first payout, over the start days paid within {_H['S3b']} "
     "sessions; blank where too few are paid to read it."),
    ("measure", "S3c", "Payouts per fee dollar at month 3",
     "For every dollar of fees paid in the first three months, the dollars of payouts received.",
     f"The payouts received by session {_H['S3c']} summed over all start days, over the fees paid by then summed "
     "over the same start days."),
    ("measure", "S4a", "Share ahead at month 6", "The share of start days ahead after six months.",
     f"The share of start days with net cash above zero at session {_H['S4a']}."),
    ("measure", "S4b", "Share ahead at month 12", "The share of start days ahead after a year.",
     f"The share of start days with net cash above zero at session {_H['S4b']}."),
    ("measure", "S5a", "Unlucky tenth's net at month 3",
     "What a user on a bad start day has after three months: one start day in ten did worse than this.",
     f"The 10th percentile across start days of the net cash at session {_H['S5a']}."),
    ("measure", "S5b", "Longest gap between payouts (bad case)",
     "The longest stretch without a payout, after the first, that nine start days in ten stayed under.",
     f"The 90th percentile of the longest run of sessions with no payout after the first one, within {_H['S5b']} "
     "sessions."),
    ("measure", "S5c", "Concentration at month 6",
     "How much of all the money made sits with the luckiest quarter of start days.",
     "The net at month 6 summed over the best quarter of start days, over the net summed over all of them."),
    ("statistic", SPEARMAN, "Rank correlation",
     "How closely two things move together, from -1 to +1: +1 means whenever one is higher the other is too, -1 "
     "means the opposite, 0 means no link. It says what goes together, not what causes what.",
     "Spearman's rank correlation: both columns are replaced by their ranks (ties share a rank) and the ordinary "
     "correlation of the ranks is taken, so one extreme start day cannot dominate."),
    ("statistic", BETA, "Standardised weight",
     "How much the outcome moves when one variable moves and the others are held still, with every variable put "
     "on the same scale so the weights can be compared with one another.",
     "Ordinary least squares after every column is rescaled to mean 0 and spread 1; a variable that does not vary "
     "is left out; for the 0-or-1 'ahead' outcome it is a linear probability model. The variables overlap, so the "
     "weights are a description, not a proof of cause."),
    ("statistic", R2, "Explained share (R-squared)",
     "How much of the differences in the outcome the variables account for together, from 0 to 1.",
     "The share of the outcome's variance the fitted regression reproduces."),
    ("statistic", "interval_within", f"The {_PCT} interval (within a design)",
     "The range a figure would plausibly fall in had history dealt the start days differently. An interval that "
     "crosses zero means the sign of the link is not established.",
     f"A moving-block bootstrap: the start days are redrawn in runs of {BOOT_BLOCK} consecutive days (because "
     f"neighbours share history), {BOOT_DRAWS:,} times, seed {BOOT_SEED}; every statistic is recomputed on each "
     f"redraw and the interval is the middle {_PCT} of the results."),
    ("statistic", "interval_between", f"The {_PCT} interval (between designs)",
     "The range a figure would plausibly fall in had a different set of lever families been tried.",
     f"Whole families are redrawn with replacement {BOOT_DRAWS:,} times (seed {CLUSTER_SEED}), because the "
     f"designs of one family share a base and a lever; the interval is the middle {_PCT} of the results. With so few "
     "families it is wide and rough: a description, never a test."),
    ("statistic", "design_share", "Design or luck",
     "Of all the differences in what users end up with, the share explained by WHICH design they ran, against the "
     "share that is WHICH day they happened to start.",
     "All start days of all designs are pooled; the pooled variance of the net splits exactly into the variance "
     "between the designs' averages and the variance across start days inside each design; the design's share is "
     "the first over the total."),
    ("statistic", "spread_share", "Where the spread in the net comes from",
     "Whether start days differ in their net because they were paid different amounts or because they paid "
     "different fees.",
     "The covariance of the net with the payouts, and with minus the fees, each over the net's variance; the two "
     "shares add to one."),
    ("statistic", "frontier", "The frontier",
     "The designs that no other design beats on everything at once. A design off the frontier is one you would "
     "never pick: another gives at least as much on all four counts.",
     "Among the designs on file (hypothetical designs never included, upper-bound designs left out), a design is "
     "off the frontier when another has a share ahead at least as high, a bankroll at most as large, a share paid "
     "by day "
     f"{MONTH} at least as high and an unlucky-tenth net at least as high, and is better on at least one."),
    ("statistic", "menu", "The menu",
     "Three ready answers to 'which design, if my limit is this much cash': the design with the highest share "
     "ahead inside each limit.",
     "Among the designs that can be on the frontier, those with at least "
     f"{MENU_FLOOR:.0%} of start days ahead at month 12 and a bad-case bankroll inside the limit "
     + ", ".join(f"({name.replace('_', ' ')}: {'no limit' if lim is None else _dollars(lim)})"
                 for name, lim in MENU_LIMITS)
     + "; the highest share ahead wins, a tie going to the smaller bankroll. The limits were set after the "
       "families were "
       "read: a reading aid, not a candidate."),
)
PICK_NAMES = {"lowest_cost": "Lowest cost", "balanced": "Balanced", "best_result": "Best result"}


def definition_rows() -> list[dict[str, Any]]:
    """Section `definitions`: one row a variable, measure, statistic and convention, then one a family and one a
    menu pick's name -- `subject_kind` the kind, `subject` the key it explains, `name` its plain name, `meaning` what
    it means and `modelled` how it is measured or modelled. Text only: no figure."""
    rows = [{"section": DEFINITIONS_SECTION, "subject_kind": kind, "subject": key, "name": name, "meaning": meaning,
             "modelled": modelled} for kind, key, name, meaning, modelled in DEFINITIONS]
    rows += [{"section": DEFINITIONS_SECTION, "subject_kind": "family", "subject": f, "name": FAMILY_NAMES[f],
              "meaning": FAMILY_WHAT[f][0].upper() + FAMILY_WHAT[f][1:] + ".",
              "modelled": f"Declared in {FAMILY_DECISIONS[f]}."} for f in (*[x[1] for x in FAMILIES], ROWS_FAMILY)]
    rows += [{"section": DEFINITIONS_SECTION, "subject_kind": "pick", "subject": name, "name": PICK_NAMES[name],
              "meaning": ("The highest share ahead with no limit on the bankroll." if limit is None else
                          f"The highest share ahead with a bad-case bankroll of at most {_dollars(limit)}."),
              "modelled": f"Among designs with at least {MENU_FLOOR:.0%} of start days ahead at month "
                          f"{Sel.BY_KEY[MENU_FLOOR_MEASURE].horizon // MONTH} (D-656 (5))."}
             for name, limit in MENU_LIMITS]
    return rows


def parameter_rows() -> list[dict[str, Any]]:
    """Section `parameters`: every constant a figure of the file rests on, as a row (so a viewer types none) --
    `measure` its key, `value`, `unit` and `note` what it is."""
    rows = [("month_sessions", MONTH, Sel.SESSIONS, "sessions in a month"),
            ("p_first_month", Sel.P_MONTHS[0], "month", "the first month of P"),
            ("p_last_month", Sel.P_MONTHS[-1], "month", "the last month of P"),
            ("boot_block", BOOT_BLOCK, COUNT, "consecutive start days in a bootstrap block"),
            ("boot_draws", BOOT_DRAWS, COUNT, "bootstrap resamples"),
            ("boot_seed", BOOT_SEED, "seed", "the moving-block bootstrap's seed"),
            ("cluster_seed", CLUSTER_SEED, "seed", "the family bootstrap's seed"),
            ("interval_level", INTERVAL, Sel.SHARE, "the level of every interval"),
            ("menu_floor", MENU_FLOOR, Sel.SHARE, f"the least share ahead ({MENU_FLOOR_MEASURE}) of a menu pick"),
            ("menu_floor_month", Sel.BY_KEY[MENU_FLOOR_MEASURE].horizon // MONTH, "month",
             f"the month the menu's floor is read at ({MENU_FLOOR_MEASURE})"),
            ("hypothetical_cells_left_out", HYPOTHETICAL_DECLARED, COUNT,
             "hypothetical_hedge cells left out of everything"),
            ("lucid_cells_shown", LUCID_DECLARED, COUNT, "lucid_upper_bound cells shown and marked")]
    rows += [(f"menu_limit_{name}", NAN if limit is None else limit, Sel.DOLLARS,
              f"the limit on the bad-case bankroll ({MENU_LIMIT_MEASURE}) of the pick; blank: no limit")
             for name, limit in MENU_LIMITS]
    return [{"section": PARAMETERS, "subject": PARAMETER, "subject_kind": PARAMETER, "measure": k, "value": float(v),
             "unit": unit, "note": what} for k, v, unit, what in rows]


# ------------------------------------------------------------------------------------------------ the family files


def family_verdict(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """What a family file says of itself in its one section `verdict` row on the line `verdict`: the family, its
    decision row and the cells it declares; `problems` when there is not exactly one such row."""
    v = [r for r in rows if text(r.get("section")) == "verdict" and text(r.get("line")) == "verdict"]
    if len(v) != 1:
        return {"problems": [f"{len(v)} verdict rows, not one"]}
    cells = number(v[0].get("cells"))
    return {"family": text(v[0].get("family")), "decision": text(v[0].get("decision")),
            "cells": int(cells) if math.isfinite(cells) else None, "problems": []}


def counted_cells(rows: Sequence[Mapping[str, Any]], arm: str = ARM, block: str = ALL) -> list[dict[str, Any]]:
    """A family file's COUNTED cells at `arm` on `block`, in the file's order, each with its base, overrides, label
    and its scorecard rows ({measure: the file's row}). A cell's rows that are not scorecard measures (an option's own
    record) are not counted rows and are not read."""
    out: dict[str, dict[str, Any]] = {}
    for r in rows:
        if (text(r.get("section")) != "cell" or not flag(r.get("counted")) or text(r.get("arm")) != arm
                or text(r.get("block")) != block or text(r.get("measure")) not in Sel.BY_KEY):
            continue
        c = out.setdefault(text(r.get("cell")), {"design": text(r.get("cell")), "base": text(r.get("base")),
                                                 "overrides": text(r.get("overrides")),
                                                 "label": text(r.get("label")), "rows": {}})
        c["rows"].setdefault(text(r.get("measure")), []).append(r)
    return list(out.values())


def cell_problems(cell: Mapping[str, Any]) -> list[str]:
    """Every scorecard measure of a counted cell is held once (an empty list: it is)."""
    return [f"{cell['design']} {m.key}: {len(cell['rows'].get(m.key, []))} rows, not one" for m in Sel.MEASURES
            if len(cell["rows"].get(m.key, [])) != 1]


def design_rows(design: str, kind: str, family: str, measures: Mapping[str, Mapping[str, Any]], *, base: str = "",
                label: str = "", overrides: str = "", source_file: str = "", source_sha256: str = "",
                source_section: str = "") -> list[dict[str, Any]]:
    """One design as section `design_table` rows: its ten scorecard measures (`measures`: {key: {value, n}}) at the
    bound arm on every start, with its family, base, label and plain description."""
    return [{"section": DESIGN_TABLE, "subject": design, "subject_kind": kind, "family": family,
             "name": short_name(design, family, base, overrides),
             "family_decision": FAMILY_DECISIONS.get(family, ""), "base": base, "label": label,
             "description": describe(design, family, base, overrides), "overrides": overrides, "arm": ARM,
             "block": ALL, "measure": m.key, "unit": m.unit, "direction": m.direction,
             "value": number(measures[m.key]["value"]), "n": int(number(measures[m.key]["n"])),
             "source_file": source_file, "source_sha256": source_sha256, "source_section": source_section}
            for m in Sel.MEASURES]


def cells_of(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """The section `design_table` rows back as cells, in the rows' order: {design, design_kind, family, label, name,
    description, measures: {key: value}}."""
    out: dict[str, dict[str, Any]] = {}
    for r in rows:
        if r.get("section") != DESIGN_TABLE:
            continue
        c = out.setdefault(text(r["subject"]), {"design": text(r["subject"]),
                                                "design_kind": text(r["subject_kind"]),
                                                "family": text(r["family"]), "label": text(r.get("label")),
                                                "name": text(r.get("name")),
                                                "description": text(r.get("description")), "measures": {}})
        c["measures"][text(r["measure"])] = number(r["value"])
    return list(out.values())


def table_differences(rows: Sequence[Mapping[str, Any]], design: str, file_rows: Mapping[str, Sequence[Mapping]],
                      *, tol: float = TOL) -> tuple[int, list[str]]:
    """A design's section `design_table` rows against a source's rows of it ({measure: [the source's rows]}, each
    with `value` and `n`): (the measures compared, every measure absent, held twice, or differing in value by more
    than `tol` or in n). No value is written into a problem."""
    mine = {text(r["measure"]): r for r in rows
            if r.get("section") == DESIGN_TABLE and text(r["subject"]) == design}
    problems = []
    for m in Sel.MEASURES:
        held = list(file_rows.get(m.key, []))
        if len(held) != 1 or m.key not in mine:
            problems.append(f"{design} {m.key}: {len(held)} source rows, {int(m.key in mine)} here")
            continue
        if not same(held[0].get("value"), mine[m.key]["value"], tol):
            problems.append(f"{design} {m.key}: the value differs")
        if int(number(held[0].get("n"))) != int(mine[m.key]["n"]):
            problems.append(f"{design} {m.key}: n differs")
    return len(mine), problems


# ------------------------------------------------------------------------------------------------ the funded facts

#: the facts of `results/u_xfa_day_budget.csv` (U2, D-652) carried into the file: (the measure's name here, the
#: source's section, group and measure, what it is)
FUNDED_FACTS: tuple[tuple[str, str, str, str, str], ...] = (
    ("won_opening_share", "opening_trade", "opened", "share_won_it",
     "the share of funded accounts that win their opening trade"),
    ("won_opening_paid_share", "after_opening", "in_profit_after_opening", "share_requested_first_payout",
     "of the accounts that won the opening trade, the share that went on to request a first payout"),
    ("lost_opening_lived_share", "opening_trade", "opened", "share_lost_it_and_lived",
     "the share of funded accounts that lose their opening trade and stay open"),
    ("lost_opening_paid_share", "after_opening", "lost_opening_and_lived", "share_requested_first_payout",
     "of the accounts that lost the opening trade and stayed open, the share that went on to request a first payout"),
    ("lost_opening_share_of_days", "budget_before_first_payout", "lost_opening_and_lived", "share_of_account_days",
     "the share of all funded account-days before a first payout spent in accounts that lost the opening trade"),
    ("won_opening_share_of_days", "budget_before_first_payout", "won_opening", "share_of_account_days",
     "the share of all funded account-days before a first payout spent in accounts that won the opening trade"),
    ("sessions_opening_to_request_p50", "after_opening", "all_opened", "sessions_after_opening_to_first_request_p50",
     "sessions from the opening trade to the first payout request, the middle account"),
    ("sessions_opening_to_request_p90", "after_opening", "all_opened", "sessions_after_opening_to_first_request_p90",
     "sessions from the opening trade to the first payout request, the slow tenth"),
)


def funded_unit(key: str) -> str:
    """A funded fact's unit, by its name: a share, or sessions."""
    return Sel.SHARE if "share" in key else Sel.SESSIONS


def funded_rows(rows: Sequence[Mapping[str, Any]], designs: Sequence[str], *, source_file: str = "",
                source_sha256: str = "") -> tuple[list[dict[str, Any]], list[str]]:
    """`FUNDED_FACTS` copied from U2's file for each design and arm: (the section `funded_facts` rows, every fact
    that is absent or held twice). Each value is COPIED, never recomputed."""
    index: dict[tuple[str, str, str, str, str], list[Mapping[str, Any]]] = {}
    for r in rows:
        index.setdefault((text(r.get("design")), text(r.get("arm")), text(r.get("section")), text(r.get("group")),
                          text(r.get("measure"))), []).append(r)
    out, problems = [], []
    for d in designs:
        for arm in ARMS:
            for key, section, group, measure, what in FUNDED_FACTS:
                held = index.get((d, arm, section, group, measure), [])
                if len(held) != 1:
                    problems.append(f"{d} {arm} {section}/{group}/{measure}: {len(held)} rows, not one")
                    continue
                out.append({"section": FUNDED, "subject": d, "subject_kind": ROW_TO_BEAT, "arm": arm,
                            "measure": key, "unit": funded_unit(key),
                            "value": number(held[0].get("value")), "n": int(number(held[0].get("n"))),
                            "note": what, "source_file": source_file, "source_sha256": source_sha256,
                            "source_section": f"{section}/{group}/{measure}"})
    return out, problems


# ------------------------------------------------------------------------------------------------ the table


def identity_row(check: str, problems: Sequence[str], *, compared: int | None = None, refuses: bool = True
                 ) -> dict[str, Any]:
    """One section `identity` row; `problems` (kept for the caller's printing, never a column) decide `holds`. In the
    stable columns: the measure `holds` with value 1 or 0, n the comparisons made, the check itself as the note."""
    return {"section": IDENTITY, "subject": IDENTITY_KIND, "subject_kind": IDENTITY_KIND, "measure": HOLDS,
            "value": 0.0 if problems else 1.0, "n": compared, "unit": FLAG, "note": check, "check": check,
            "holds": not problems, "compared": compared, "differing": len(problems), "refuses": bool(refuses),
            "problems": list(problems)}


def key_problems(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    """Every row but an identity's is named once by `KEY`, and names a subject (an empty list: it is)."""
    seen: dict[tuple, int] = {}
    problems = []
    for r in rows:
        if r.get("section") == IDENTITY:
            continue
        if not text(r.get("subject")):
            problems.append(f"{r.get('section')}: a row with no subject")
        k = tuple(text(r.get(c)) for c in KEY)
        seen[k] = seen.get(k, 0) + 1
    return problems + [f"{' / '.join(x for x in k if x)}: {n} rows" for k, n in seen.items() if n > 1]


def hypothetical_problems(rows: Sequence[Mapping[str, Any]], names: Iterable[str]) -> list[str]:
    """No row of the table is of a hypothetical cell or carries its label (an empty list: none is)."""
    names = set(names)
    bad = [text(r.get("subject")) for r in rows
           if text(r.get("subject")) in names or text(r.get("picked")) in names
           or text(r.get("label")) == HYPOTHETICAL_LABEL
           or any(d in names for d in text(r.get("dominated_by")).split())]
    return [f"{d}: a hypothetical cell in the table" for d in sorted(set(bad))]


def measure_names() -> dict[str, tuple[str, ...]]:
    """Every measure name a section can hold, by section (`definitions` holds text and no measure)."""
    keys = tuple(m.key for m in Sel.MEASURES)
    within = tuple(within_measure(SPEARMAN, o, v) for o in OUTCOMES for v in CORRELATED) + tuple(
        within_measure(BETA, o, v) for o in OUTCOMES for v in VARIABLES) + tuple(
        within_measure(R2, o) for o in OUTCOMES)
    between = tuple(between_measure(SPEARMAN, k) for k in keys if k != Sel.PRIMARY_KEY) + tuple(
        between_measure(BETA, k) for k in BETWEEN_REGRESSORS) + (between_measure(R2),)
    return {IDENTITY: (HOLDS,), PARAMETERS: tuple(r["measure"] for r in parameter_rows()), DEFINITIONS_SECTION: (),
            DESIGN_TABLE: keys, WITHIN: within, ACCOUNTING: ACCOUNTING_STATS, LUCK: LUCK_STATS, BETWEEN: between,
            FRONTIER: (ON_FRONTIER,), MENU: keys, FUNDED: tuple(k for k, *_ in FUNDED_FACTS)}


def schema_problems(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    """Every row's measure is one its section can hold (`measure_names`), and every figure row carries a unit (an
    empty list: so)."""
    names = measure_names()
    problems = []
    for r in rows:
        sec, m = r.get("section"), text(r.get("measure"))
        if sec == DEFINITIONS_SECTION:
            if m:
                problems.append(f"definitions: a row with the measure {m}")
            continue
        if m not in names.get(sec, ()):
            problems.append(f"{sec}: {m!r} is not a measure of the section")
        if not text(r.get("unit")):
            problems.append(f"{sec} {m}: no unit")
    return sorted(set(problems))


def section_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    return {s: int(sum(1 for r in rows if r.get("section") == s)) for s in SECTIONS}


def table(rows: Sequence[Mapping[str, Any]]) -> pd.DataFrame:
    """The result's table: `COLUMNS` in order, a field a row does not carry (or holds as None) blank. A key that is
    not a column is refused."""
    unknown = sorted({k for r in rows for k in r} - set(COLUMNS))
    if unknown:
        raise ValueError(f"not columns of the drivers file: {unknown}")
    blank = {c: "" for c in COLUMNS}
    df = pd.DataFrame([{**blank, **{k: ("" if v is None else v) for k, v in r.items()}} for r in rows],
                      columns=list(COLUMNS), dtype=object)
    df["reading"] = READING
    return df


__all__ = ["DECISION", "STUDY", "RESULT", "SCRIPT", "READING", "ARM", "BESIDE_ARM", "ARMS", "ALL", "MONTH",
           "OUTCOME_MONTHS", "WITHIN_MONTHS", "BOOT_BLOCK", "BOOT_DRAWS", "BOOT_SEED", "CLUSTER_SEED", "INTERVAL",
           "NET", "AHEAD", "OUTCOMES", "VARIABLES", "PAID", "CORRELATED", "SPEARMAN", "BETA", "R2",
           "ARITHMETIC_WITHIN", "MECHANICAL_BETWEEN",
           "BETWEEN_REGRESSORS", "SET_ALL", "SET_NO_LUCID", "SET_U1", "SET_ROWS", "ROWS_FAMILY", "FRONTIER_MEASURES",
           "MENU_LIMITS", "MENU_FLOOR", "MENU_FLOOR_MEASURE", "MENU_LIMIT_MEASURE", "HYPOTHETICAL_LABEL",
           "LUCID_LABEL", "HYPOTHETICAL_DECLARED", "LUCID_DECLARED", "ROW_TO_BEAT", "FAMILY_CELL", "U1_CONFIG",
           "SECTIONS", "CORE", "COLUMNS", "KEY", "DESIGN_SET", "MENU_PICK", "PARAMETER", "IDENTITY_KIND",
           "ON_FRONTIER", "HOLDS",
           "STATISTIC_UNITS", "ACCOUNTING_UNITS", "LUCK_UNITS", "within_measure", "between_measure", "funded_unit",
           "measure_names", "schema_problems", "FAMILIES", "FAMILY_NAMES", "DEFINITIONS", "FUNDED_FACTS", "PICK_NAMES",
           "ACCOUNTING_STATS", "LUCK_STATS", "text", "flag", "number", "same", "money_frame", "start_frame",
           "batch_stats", "interval", "within_rows", "accounting", "variance_split", "between_stats", "between_rows",
           "in_pool", "frontier", "menu", "describe", "short_name", "definition_rows", "parameter_rows",
           "family_verdict",
           "counted_cells", "cell_problems", "design_rows", "cells_of", "table_differences", "funded_rows",
           "identity_row", "key_problems", "hypothetical_problems", "section_counts", "table"]
