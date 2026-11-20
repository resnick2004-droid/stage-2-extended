"""Wave 4.2's setting rule, as a pure function (`docs/plans/WAVE42_SETTING_RULE.md`; E-221, O-3; CHARTER 3.7-3.9).

Given **H4's one output** on the search years only -- the per-baseline readings of the naive coin, P-14, P-15 and P-16
(every per-unit measure the rule reads, as a matrix of start days by coin seeds), bound to H4's result file by that
file's sha256 and its manifest -- `setting_rule` returns, mechanically and once:

1. **the bankroll budgets B** of measure (24), and the primary budget B* that P under the bankroll stop and the
   bankroll limit read (the rule's section 3);
2. **the composite's dimensions, normalisers and weights** (section 4), or the fallback P_B alone (section 4.4);
3. **the size that matters delta*** (O-3) and the power the three-way test then has at it, at the declared seed count
   `TEST_SEEDS` (section 5);
4. **the limits**, each with its direction, and the level of the one-sided check reported beside them (section 6).

Nothing here draws randomness, reads a file, a bar or a result, or knows a held-out outcome: the held-out years enter
only as the declared count of complete starts per horizon on the pinned calendar (the three-way test's arithmetic,
with its named source). An input tagged anything but the search block, or carrying a start day outside the search
years, is refused before any value is computed (`Wave42Refused`); so is an input that is not the whole of H4's one
output (its start days, its seeds and its optional measures exactly the manifest's, its content the manifest's
digest), and a second application. Sessions left are computed here from the pinned search calendar, never taken from
the caller. Every constant is the document's, which `tests/test_wave42_rule.py` machine-reads.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np
from scipy import stats

from extended.family_stats import MDL_POWER

# ---------------------------------------------------------------------------------------------- the constants (doc 2)
RULE_ID = "W42-R1"
SEARCH_FIRST, SEARCH_LAST = "2020-01-02", "2023-12-29"        # E-208's search years
HELD_OUT_FIRST = "2024-01-02"                                  # E-208's held-out years begin; never read
BLOCK = "search"
READING = "martingale_outcome"                                 # CHARTER 3.2's deciding reading
BASELINES = ("naive_coin", "p14", "p15", "p16")                # CHARTER 2: Topstep's baseline set, in this order
W = 126                                                        # the first-payout window (U1, Q-44: a ledger constant)
MONTH = 21
AHEAD_TOL = 1e-6                                               # MEASURES 1.2 (m-11)
H4_MIN_SEEDS = 62                                              # m-2: the fewest seeds at which a gap may resolve
TEST_SEEDS = 1000                                              # B-3: the held-out test's seed count J, declared here
FEE_SOURCE = "vendor/stage2/config/rules.yaml:subscription_fee"  # m-4: the Standard path's monthly subscription
BUDGET_QUANTILES = (0.50, 0.75, 0.90)
PRIMARY_BUDGET_QUANTILE = 0.75
CAP_QUANTILES = (0.05, 0.95)
CAP_MARGIN = 0.25
RESOLVE_Z = 2.0                                                # m-2: a gap resolves above twice its standard error
DELTA_FRACTION = 0.25
DELTA_MIN = 0.01
DELTA_MAX = 0.05                                               # m-2: delta*'s declared cap
POWER_TARGET = MDL_POWER
K_TEST = 13
LIMIT_CHECK_LEVEL = 0.05
J_MAX = 10 ** 7
HELD_OUT_LEDGER = "none"                                       # B-8: this rule's own held-out reads (E-211's form)

CONSTANTS: dict[str, Any] = {
    "RULE_ID": RULE_ID, "SEARCH_FIRST": SEARCH_FIRST, "SEARCH_LAST": SEARCH_LAST, "BLOCK": BLOCK, "READING": READING,
    "BASELINES": list(BASELINES), "W": W, "MONTH": MONTH, "AHEAD_TOL": AHEAD_TOL, "H4_MIN_SEEDS": H4_MIN_SEEDS,
    "TEST_SEEDS": TEST_SEEDS, "FEE_SOURCE": FEE_SOURCE,
    "BUDGET_QUANTILES": list(BUDGET_QUANTILES), "PRIMARY_BUDGET_QUANTILE": PRIMARY_BUDGET_QUANTILE,
    "CAP_QUANTILES": list(CAP_QUANTILES), "CAP_MARGIN": CAP_MARGIN, "RESOLVE_Z": RESOLVE_Z,
    "DELTA_FRACTION": DELTA_FRACTION, "DELTA_MIN": DELTA_MIN, "DELTA_MAX": DELTA_MAX, "POWER_TARGET": POWER_TARGET,
    "K_TEST": K_TEST, "LIMIT_CHECK_LEVEL": LIMIT_CHECK_LEVEL, "J_MAX": J_MAX, "HELD_OUT_LEDGER": HELD_OUT_LEDGER,
}

#: the fields H4's manifest must carry for its output to be this rule's input (B-1, B-2, m-6, m-9)
H4_MANIFEST_KEYS = ("sha256", "block", "reading", "W", "baselines", "starts", "seeds", "optional_measures",
                    "calendar_sha256", "readings_sha256")
#: the fields naming where the held-out start counts come from (m-7)
TEST_STARTS_SOURCE_KEYS = ("function", "commit", "calendar_sha256")
_HEX64 = re.compile(r"[0-9a-f]{64}")
_COMMIT = re.compile(r"[0-9a-f]{7,40}")


@dataclass(frozen=True)
class Dim:
    """One composite dimension: its objective term, MEASURES.md's number, the per-unit key it reads (or the derived
    value at B*), its horizon, its direction (+1 higher is better, -1 lower is better) and its kind (`share`: fixed
    caps [0, 1]; `days`: a priori [0, W + 1]; `dollars`: a priori [0, inf))."""
    name: str
    term: str
    measure: str
    key: str
    horizon: int
    direction: int
    kind: str


DIMENSIONS = (
    Dim("money", "making money: P under the bankroll stop (CHARTER 3.9)", "(13) P_B", "P_B", 63, +1, "share"),
    Dim("bankroll", "least bankroll", "(25)", "peak_oop_12_months", 252, -1, "dollars"),
    Dim("speed", "fastest", "(5)", "first_payout_days", W, -1, "days"),
    Dim("cost", "cheapest pass and payout", "(2)", "cash_to_first_pass", W, -1, "dollars"),
    Dim("steady", "steady income", "(18)", "share_months_positive", 252, +1, "share"),
    Dim("ruin", "least ruin: run out before the first payout at B*", "(24)", "run_out", W, -1, "share"),
)


@dataclass(frozen=True)
class LimitSpec:
    name: str
    measure: str
    key: str
    direction: str          # "ceiling" or "floor"
    horizon: int
    stat: str               # "mean", "p10", "p50", "p90"
    optional: bool
    kind: str


LIMITS = (
    LimitSpec("not_paid_within_B", "(24)", "not_paid_within_B", "ceiling", W, "mean", False, "share"),
    LimitSpec("peak_oop_12_months_p90", "(25)", "peak_oop_12_months", "ceiling", 252, "p90", False, "dollars"),
    LimitSpec("first_payout_days_p50", "(5)", "first_payout_days", "ceiling", W, "p50", False, "days"),
    LimitSpec("orders_max_p90", "(30)", "orders_max", "ceiling", W, "p90", True, "count"),
    LimitSpec("accounts_max_p90", "(30)", "accounts_max", "ceiling", W, "p90", True, "count"),
    LimitSpec("taken_mean_p10", "(37)", "taken_mean", "floor", W, "p10", True, "count"),
)

# the per-unit measures H4 must hand in (each a start-days x seeds matrix), with their horizon and a priori range
REQUIRED = {
    **{f"net_month_{m}": (MONTH * m, -math.inf, math.inf) for m in (1, 2, 3)},
    **{f"peak_month_{m}": (MONTH * m, 0.0, math.inf) for m in (1, 2, 3)},
    "spent_before_first_payout": (W, 0.0, math.inf),
    "first_payout_days": (W, 0.0, W + 1.0),
    "first_pass_days": (W, 0.0, W + 1.0),
    "cash_to_first_pass": (W, 0.0, math.inf),
    "peak_oop_12_months": (252, 0.0, math.inf),
    "share_months_positive": (252, 0.0, 1.0),
}
OPTIONAL = {"orders_max": (W, 0.0, math.inf), "accounts_max": (W, 0.0, math.inf), "taken_mean": (W, 0.0, math.inf)}
STATS = {"mean": None, "p10": 0.10, "p50": 0.50, "p90": 0.90}
HORIZONS = tuple(sorted({d.horizon for d in DIMENSIONS} | {lim.horizon for lim in LIMITS}))


class Wave42Refused(RuntimeError):
    """The rule refuses its input before any value is computed."""


@dataclass(frozen=True)
class BaselineReading:
    """One baseline's H4 reading: its block tag, its reading tag (CHARTER 3.2), its start days (ISO dates on the
    search calendar, increasing), its coin seeds, and per measure key a matrix `values[key][s, c]`. Sessions left are
    not an input: the rule computes them from the pinned search calendar (B-2)."""
    name: str
    block: str
    reading: str
    starts: tuple[str, ...]
    seeds: tuple[int, ...]
    values: Mapping[str, Any]


@dataclass(frozen=True)
class H4Binding:
    """H4's one output: its result file's sha256 and that file's sidecar manifest (the fields `H4_MANIFEST_KEYS`)."""
    result_sha256: str
    manifest: Mapping[str, Any]


# ------------------------------------------------------------------------------------------------------- digests
def calendar_digest(calendar: Sequence[str]) -> str:
    """The sha256 of the calendar's ISO dates, one per line, each line ended by a newline (UTF-8)."""
    return hashlib.sha256("".join(f"{d}\n" for d in calendar).encode("utf-8")).hexdigest()


def readings_digest(readings: Mapping[str, BaselineReading]) -> str:
    """The content digest H4's runner records in its manifest (`readings_sha256`): every baseline in name order, its
    tags, start days and seeds, and every measure's matrix (shape and float64 bytes, blanks as one canonical NaN)."""
    h = hashlib.sha256()
    for name in sorted(readings):
        b = readings[name]
        h.update(json.dumps([b.name, b.block, b.reading, [str(d) for d in b.starts], [int(x) for x in b.seeds],
                             sorted(b.values)]).encode("utf-8"))
        for key in sorted(b.values):
            x = np.asarray(b.values[key], dtype=np.float64)
            x = np.where(np.isnan(x), np.nan, x)
            h.update(key.encode("utf-8"))
            h.update(json.dumps(list(x.shape)).encode("utf-8"))
            h.update(np.ascontiguousarray(x).tobytes())
    return h.hexdigest()


# ------------------------------------------------------------------------------------------------------- validation
def _refuse(msg: str) -> Wave42Refused:
    return Wave42Refused(f"Wave 4.2's rule refuses its input: {msg}")


def _validate(readings: Mapping[str, BaselineReading], h4: H4Binding, calendar: Sequence[str], fee_unit: float,
              fee_source: str, test_starts: Mapping[int, int], test_starts_source: Mapping[str, str],
              prior_applications: Sequence[Mapping[str, Any]]) -> tuple[dict[str, dict[str, np.ndarray]], np.ndarray]:
    for b in readings.values():                                    # the held-out guard first, before anything else
        if b.block != BLOCK:
            raise _refuse(f"{b.name!r} is tagged block {b.block!r}; only the search years ({BLOCK!r}) are read")
        for d in b.starts:
            if not (SEARCH_FIRST <= str(d) <= SEARCH_LAST) or str(d) >= HELD_OUT_FIRST:
                raise _refuse(f"{b.name!r} has start day {d!r} outside the search years {SEARCH_FIRST}..{SEARCH_LAST}"
                              " (a held-out or confirmation day is never read)")
    for b in readings.values():
        if b.reading != READING:
            raise _refuse(f"{b.name!r} is the {b.reading!r} reading; only the {READING!r} reading is read")
    if not isinstance(prior_applications, (list, tuple)):
        raise _refuse("prior_applications lists every Wave 4.2 output already written (empty before the one run)")
    for rec in prior_applications:
        rid = str((rec or {}).get("rule_id", ""))
        if not rid:
            raise _refuse("a prior application's record names no rule id")
        if rid.startswith("W42-"):
            raise _refuse(f"Wave 4.2's rule is applied once: {rid!r} has already been applied to H4's output")
    if set(readings) != set(BASELINES) or any(readings[k].name != k for k in readings):
        raise _refuse(f"the baselines are exactly {BASELINES}, each under its own name; got {sorted(readings)}")

    # ---- the search calendar (B-2): sessions left are computed here
    cal = [str(d) for d in calendar]
    if not cal or cal != sorted(set(cal)) or cal[0] != SEARCH_FIRST or cal[-1] != SEARCH_LAST:
        raise _refuse(f"the search calendar is strictly increasing from {SEARCH_FIRST} to {SEARCH_LAST}")
    cal_sha = calendar_digest(cal)

    # ---- H4's one output (B-1, m-6, m-9)
    if not isinstance(h4, H4Binding) or not (isinstance(h4.result_sha256, str) and _HEX64.fullmatch(h4.result_sha256)):
        raise _refuse("H4's output is named by its result file's sha256 (64 hex digits) and its manifest")
    man = h4.manifest
    missing = [k for k in H4_MANIFEST_KEYS if k not in man]
    if missing:
        raise _refuse(f"H4's manifest lacks {missing}")
    if man["sha256"] != h4.result_sha256:
        raise _refuse("H4's manifest names another result file (its sha256 differs)")
    if man["block"] != BLOCK or man["reading"] != READING:
        raise _refuse(f"H4's manifest is not the {BLOCK!r} block's {READING!r} reading")
    if int(man["W"]) != W:
        raise _refuse(f"H4's declaration pins W = {man['W']}; this rule is declared at W = {W} (m-9)")
    if list(man["baselines"]) != list(BASELINES):
        raise _refuse(f"H4's manifest declares the baselines {man['baselines']}, not {list(BASELINES)}")
    if man["calendar_sha256"] != cal_sha:
        raise _refuse("the search calendar is not the one H4's manifest names (its sha256 differs)")
    ref = readings[BASELINES[0]]
    if [str(d) for d in ref.starts] != [str(d) for d in man["starts"]]:
        raise _refuse("the start days are not every start day H4 declared (a subset or another list)")
    if [int(s) for s in ref.seeds] != [int(s) for s in man["seeds"]]:
        raise _refuse("the coin seeds are not every seed H4 declared (a subset or another list)")
    n, J = len(ref.starts), len(ref.seeds)
    if n < 1 or J < 2 or len(set(ref.seeds)) != J:
        raise _refuse("at least one start day and at least two distinct coin seeds")
    if list(ref.starts) != sorted(set(ref.starts)):
        raise _refuse("start days strictly increasing")
    pos = {d: i for i, d in enumerate(cal)}
    off = [d for d in ref.starts if str(d) not in pos]
    if off:
        raise _refuse(f"start day {off[0]!r} is not a session of the search calendar")
    sl = np.asarray([len(cal) - pos[str(d)] for d in ref.starts])        # the start session is session 1
    for b in readings.values():
        if tuple(b.starts) != tuple(ref.starts) or tuple(b.seeds) != tuple(ref.seeds):
            raise _refuse(f"{b.name!r} is not paired with {ref.name!r}: same start days and seeds")

    if not (isinstance(fee_unit, (int, float)) and math.isfinite(fee_unit) and fee_unit > 0):
        raise _refuse("the fee unit is a positive dollar amount from the verified ledger")
    if fee_source != FEE_SOURCE:
        raise _refuse(f"the fee unit is read from {FEE_SOURCE!r} (the Standard path's subscription); got {fee_source!r}")
    if any(h not in test_starts for h in HORIZONS):
        raise _refuse(f"the test's complete-start count is declared for every horizon {list(HORIZONS)}")
    counts = [int(test_starts[h]) for h in HORIZONS]
    if any(c < 1 for c in counts) or any(b > a for a, b in zip(counts, counts[1:])):
        raise _refuse("the test's complete-start counts are positive and non-increasing in the horizon")
    src = test_starts_source if isinstance(test_starts_source, Mapping) else {}
    if any(not (isinstance(src.get(k), str) and src[k].strip()) for k in TEST_STARTS_SOURCE_KEYS) \
            or not _COMMIT.fullmatch(src["commit"]) or not _HEX64.fullmatch(src["calendar_sha256"]):
        raise _refuse("the test's start counts name their source: the function, its commit and the calendar's sha256")

    out: dict[str, dict[str, np.ndarray]] = {}
    for name in BASELINES:
        b = readings[name]
        vals: dict[str, np.ndarray] = {}
        for key, (h, lo, hi) in {**REQUIRED, **OPTIONAL}.items():
            if key not in b.values:
                if key in REQUIRED:
                    raise _refuse(f"{name!r} lacks the required measure {key!r}")
                continue
            x = np.asarray(b.values[key], dtype=float)
            if x.shape != (n, J):
                raise _refuse(f"{name!r} {key!r} is {x.shape}, not start days x seeds {(n, J)}")
            rows = sl >= h
            if not rows.any():
                raise _refuse(f"no start day has {h} sessions left (E_{h} is empty)")
            xe = x[rows]
            if not np.isfinite(xe).all():
                raise _refuse(f"{name!r} {key!r} is blank or not finite on E_{h} (MEASURES 1.3's blank rule)")
            if (xe < lo).any() or (xe > hi).any():
                raise _refuse(f"{name!r} {key!r} lies outside its a priori range [{lo}, {hi}]")
            vals[key] = x
        rW = sl >= W
        paid = vals["first_payout_days"][rW] <= W
        if (vals["first_pass_days"][rW][paid] > vals["first_payout_days"][rW][paid]).any():
            raise _refuse(f"{name!r} has a unit paid before its first pass")
        out[name] = vals
    for key in OPTIONAL:
        have = [key in out[name] for name in BASELINES]
        if any(have) and not all(have):
            raise _refuse(f"the optional measure {key!r} is given for some baselines and not others")
    present = {k for k in OPTIONAL if k in out[BASELINES[0]]}
    if present != set(man["optional_measures"]):
        raise _refuse(f"the optional measures present {sorted(present)} are not those H4 declared "
                      f"{sorted(man['optional_measures'])}")
    if readings_digest(readings) != man["readings_sha256"]:
        raise _refuse("the readings are not H4's output: their digest is not the manifest's readings_sha256")
    return out, sl


# --------------------------------------------------------------------------------------------------- the pieces
def _rows(sl: np.ndarray, h: int) -> np.ndarray:
    return sl >= h


def _q(x: np.ndarray, p: float) -> float:
    return float(np.quantile(np.asarray(x, dtype=float).ravel(), p))       # numpy's linear rule (MEASURES 1.3)


def fee_lattice(x: float, fee_unit: float) -> float:
    """The smallest whole number of fee units at or above x, and at least one (section 3)."""
    k = max(1, math.ceil(x / fee_unit - 1e-9))
    return float(k * fee_unit)


def equal_weights(names: Sequence[str]) -> dict[str, float]:
    """m-1, the lead's ruling: one equal weight per kept dimension (CHARTER 2 lists the terms without ranking them)."""
    return {k: 1.0 / len(names) for k in names}


def spearman(x: np.ndarray, y: np.ndarray) -> float | None:
    """Spearman's rho with average ranks; None when either side is constant (no rank order to compare)."""
    rx, ry = stats.rankdata(x), stats.rankdata(y)
    if rx.std() == 0 or ry.std() == 0:
        return None
    return float(np.corrcoef(rx, ry)[0, 1])


def bankroll_states(v: Mapping[str, np.ndarray], B: float) -> dict[str, np.ndarray]:
    """The per-unit values at budget B (MEASURES 2 and (24)): `P_B`, the months 1-3 ahead (net above AHEAD_TOL) with
    the peak out-of-pocket through that month's close at or below B, over three; `run_out`, spending before the first
    payout above B; `not_paid_within_B`, run out plus censored (unpaid by W, spending at or below B)."""
    ahead = sum(((v[f"net_month_{m}"] > AHEAD_TOL) & (v[f"peak_month_{m}"] <= B)).astype(float) for m in (1, 2, 3))
    x6, paid = v["spent_before_first_payout"], v["first_payout_days"] <= W
    return {"P_B": ahead / 3.0, "run_out": (x6 > B).astype(float),
            "not_paid_within_B": 1.0 - (paid & (x6 <= B)).astype(float)}


def _caps(dim: Dim, pooled: np.ndarray, fee_unit: float) -> tuple[float, float, str]:
    if dim.kind == "share":
        return 0.0, 1.0, "fixed [0, 1]"
    a, b = (0.0, W + 1.0) if dim.kind == "days" else (0.0, math.inf)
    if pooled.size == 0:
        return 0.0, float(fee_unit), "degenerate: no unit passed; every z is 0"
    ql, qh = _q(pooled, CAP_QUANTILES[0]), _q(pooled, CAP_QUANTILES[1])
    span = qh - ql
    lo, hi = max(a, ql - CAP_MARGIN * span), min(b, qh + CAP_MARGIN * span)
    if hi > lo:
        return lo, hi, "pooled quantiles widened by the cap margin"
    if dim.kind == "days":
        return a, b, "degenerate: the a priori range"
    return max(0.0, ql - fee_unit), qh + fee_unit, "degenerate: one fee unit each side"


def _z(dim: Dim, x: np.ndarray, lo: float, hi: float) -> np.ndarray:
    u = np.clip((x - lo) / (hi - lo), 0.0, 1.0)
    return u if dim.direction > 0 else 1.0 - u


def _stat(x: np.ndarray, stat: str) -> float:
    return float(np.mean(x)) if STATS[stat] is None else _q(x, STATS[stat])


def level(k: int = K_TEST) -> float:
    return 0.05 / (k * (k + 1))


def q_factor(weights: Mapping[str, float], horizons: Mapping[str, int], test_starts: Mapping[int, int],
             J: int) -> float:
    """Q = (1 / J) sum over nested strata of count x (sum_{d reaching the stratum} w_d / |E_{h_d}|)^2 (section 5.3):
    the Hoeffding half-width is c_h sqrt(Q) and the estimate's coin sd about sigma_u sqrt(Q)."""
    hs = sorted(set(horizons.values()))
    total = 0.0
    for i, h in enumerate(hs):
        count = int(test_starts[h]) - (int(test_starts[hs[i + 1]]) if i + 1 < len(hs) else 0)
        a = sum(w / int(test_starts[horizons[d]]) for d, w in weights.items() if horizons[d] <= h)
        total += count * a * a
    return total / J


def pair_power(delta: float, Q: float, sigma: float, alpha: float) -> float:
    """2.5's normal approximation: Phi((delta / sqrt(Q) - c_h) / sigma), c_h = sqrt(2 ln(1 / alpha)); sigma = 0 gives
    the deterministic estimate's 0 or 1."""
    ch = math.sqrt(2.0 * math.log(1.0 / alpha))
    t = delta / math.sqrt(Q) - ch
    if sigma <= 0:
        return 1.0 if t > 0 else 0.0
    return float(stats.norm.cdf(t / sigma))


def conjoint_power(deltas: Mapping[str, float], sigmas: Mapping[str, float], Q: float, alpha: float) -> float:
    """The intersection-union pass's power, bounded below by the union bound: max(0, 1 - sum of each pair's miss)."""
    return max(0.0, 1.0 - sum(1.0 - pair_power(deltas[b], Q, sigmas[b], alpha) for b in deltas))


def limit_z(n_limits: int) -> float:
    """m-3 (c): the normal quantile that gives every one of n limits its headroom jointly at the power target
    (Bonferroni: each at 1 - (1 - pi*) / n)."""
    return float(stats.norm.ppf(1.0 - (1.0 - POWER_TARGET) / max(1, n_limits)))


# ------------------------------------------------------------------------------------------------------ the output
@dataclass(frozen=True)
class Wave42Values:
    values: dict[str, Any]

    def as_json(self) -> str:
        return json.dumps(self.values, sort_keys=True, separators=(",", ":"), allow_nan=False)

    def digest(self) -> str:
        return hashlib.sha256(self.as_json().encode("utf-8")).hexdigest()


def input_digest(readings: Mapping[str, BaselineReading], h4: H4Binding, calendar: Sequence[str], fee_unit: float,
                 fee_source: str, test_starts: Mapping[int, int], test_starts_source: Mapping[str, str]) -> str:
    """Every input in one sha256: the readings' content, H4's binding, the calendar, the fee and the test's counts."""
    h = hashlib.sha256()
    h.update(json.dumps({"fee_unit": float(fee_unit), "fee_source": fee_source,
                         "test_starts": {str(k): int(v) for k, v in sorted(test_starts.items())},
                         "test_starts_source": {k: str(v) for k, v in sorted(test_starts_source.items())},
                         "h4_result_sha256": h4.result_sha256,
                         "h4_manifest": json.loads(json.dumps(dict(h4.manifest), sort_keys=True, default=str)),
                         "calendar_sha256": calendar_digest([str(d) for d in calendar])},
                        sort_keys=True).encode("utf-8"))
    h.update(readings_digest(readings).encode("utf-8"))
    return h.hexdigest()


def _r(x: float) -> float:
    return float(x)


def _year_estimates(x: np.ndarray, starts: Sequence[str], rows: np.ndarray, stat: str) -> dict[str, float | None]:
    """m-3 (b): the statistic on each search year's start days (of E_h), beside the limit, deciding nothing."""
    yrs = np.asarray([str(d)[:4] for d in starts])
    out: dict[str, float | None] = {}
    for y in sorted(set(yrs.tolist())):
        sel = rows & (yrs == y)
        out[y] = _stat(x[sel], stat) if sel.any() else None
    return out


# ------------------------------------------------------------------------------------------------------- the rule
def setting_rule(readings: Mapping[str, BaselineReading] | Sequence[BaselineReading], *, h4: H4Binding,
                 search_calendar: Sequence[str], fee_unit: float, fee_source: str, test_starts: Mapping[int, int],
                 test_starts_source: Mapping[str, str],
                 prior_applications: Sequence[Mapping[str, Any]]) -> Wave42Values:
    """The whole rule (sections 3-6), in its fixed order: budgets, dimensions and weights, delta\\* and power, limits.
    Applied once to H4's one output (B-1); the seed count J is the declared `TEST_SEEDS`, never an input (B-3)."""
    if not isinstance(readings, Mapping):
        readings = {b.name: b for b in readings}
    vals, sl = _validate(readings, h4, search_calendar, fee_unit, fee_source, test_starts, test_starts_source,
                         prior_applications)
    ref = readings[BASELINES[0]]
    nJ = len(ref.seeds)
    J = TEST_SEEDS
    n_search = {h: int(_rows(sl, h).sum()) for h in HORIZONS}
    out: dict[str, Any] = {
        "rule_id": RULE_ID, "constants": CONSTANTS,
        "input_sha256": input_digest(readings, h4, search_calendar, fee_unit, fee_source, test_starts,
                                     test_starts_source),
        "h4": {"result_sha256": h4.result_sha256, "readings_sha256": h4.manifest["readings_sha256"],
               "calendar_sha256": calendar_digest([str(d) for d in search_calendar]),
               "starts": len(ref.starts), "seeds": nJ, "optional_measures": sorted(h4.manifest["optional_measures"])},
        "held_out_read_ledger": {"entry": HELD_OUT_LEDGER, "refuses": f"any reading not tagged {BLOCK!r}",
                                 "level": "nominal (CHARTER 3.6 (b): the baselines' ledger is not empty)"},
        "application": {"prior_applications": 0, "rule": "applied once to H4's one output"},
        "search_starts": {str(h): n_search[h] for h in HORIZONS}, "seeds": nJ,
        "test_starts_source": {k: str(test_starts_source[k]) for k in TEST_STARTS_SOURCE_KEYS},
    }

    # ---- 3. budgets
    rW = _rows(sl, W)
    pooled6 = np.concatenate([vals[b]["spent_before_first_payout"][rW].ravel() for b in BASELINES])
    paid_share = float(np.mean(np.concatenate([(vals[b]["first_payout_days"][rW] <= W).ravel() for b in BASELINES])))
    budgets, bt = [], []
    for p in BUDGET_QUANTILES:
        qv = _q(pooled6, p)
        B = fee_lattice(qv, fee_unit)
        bt.append({"quantile": p, "pooled_value": _r(qv), "budget": B})
        if B not in budgets:
            budgets.append(B)
    Bstar = fee_lattice(_q(pooled6, PRIMARY_BUDGET_QUANTILE), fee_unit)
    out["budgets"] = {"values": budgets, "primary": Bstar, "trace": bt, "measure": "(6)/(24) spent_before_first_payout",
                      "horizon": W, "units_pooled": int(pooled6.size), "share_paid_by_W": paid_share,
                      "fee_unit": float(fee_unit), "fee_source": fee_source}

    # ---- 4. dimensions, caps, weights (fixed: no data-driven drop, B-4)
    per = {b: {**vals[b], **bankroll_states(vals[b], Bstar)} for b in BASELINES}
    z: dict[str, dict[str, np.ndarray]] = {b: {} for b in BASELINES}
    dims_out = []
    for d in DIMENSIONS:
        r = _rows(sl, d.horizon)
        rec: dict[str, Any] = {}
        if d.name == "cost":                      # B-5: caps from the passed units; an unpassed unit scores z = 0
            ok = {b: per[b]["first_pass_days"] <= W for b in BASELINES}
            pooled = np.concatenate([per[b][d.key][r][ok[b][r]] for b in BASELINES])
            lo, hi, how = _caps(d, pooled, fee_unit)
            for b in BASELINES:
                z[b][d.name] = np.where(ok[b], _z(d, per[b][d.key], lo, hi), 0.0)
            rec["share_passed_by_W"] = float(np.mean(np.concatenate([ok[b][r].ravel() for b in BASELINES])))
        else:
            pooled = np.concatenate([per[b][d.key][r].ravel() for b in BASELINES])
            lo, hi, how = _caps(d, pooled, fee_unit)
            for b in BASELINES:
                z[b][d.name] = _z(d, per[b][d.key], lo, hi)
        allz = np.concatenate([z[b][d.name][r].ravel() for b in BASELINES])
        rec.update({"name": d.name, "term": d.term, "measure": d.measure, "key": d.key, "horizon": d.horizon,
                    "direction": "higher" if d.direction > 0 else "lower", "kind": d.kind, "lo": _r(lo),
                    "hi": _r(hi), "caps": how, "constant": bool(np.ptp(allz) == 0),
                    "baseline_means": {b: float(np.mean(z[b][d.name][r])) for b in BASELINES}})
        dims_out.append(rec)
    hz = {d.name: d.horizon for d in DIMENSIONS}
    names = [d.name for d in DIMENSIONS]
    rho = {}
    for i, a in enumerate(names):                 # reported beside, deciding nothing (B-4)
        for bname in names[i + 1:]:
            r = _rows(sl, max(hz[a], hz[bname]))
            rv = spearman(np.concatenate([z[b][a][r].ravel() for b in BASELINES]),
                          np.concatenate([z[b][bname][r].ravel() for b in BASELINES]))
            rho[f"{a}|{bname}"] = None if rv is None else _r(rv)
    form = "fallback" if all(rec["constant"] for rec in dims_out[1:]) else "composite"
    kept = ["money"] if form == "fallback" else names
    w = equal_weights(kept)
    for rec in dims_out:
        rec["weight"] = w.get(rec["name"], 0.0)
        rec["weight_per_unit"] = rec["weight"] if rec["kind"] == "share" else rec["weight"] / (rec["hi"] - rec["lo"])
    out["dimensions"] = dims_out
    out["weights"] = w
    out["form"] = form
    out["rho_beside"] = rho

    # composite per baseline per seed: C_b(c) = sum_d w_d mean_{s in E_d} z_d(b, s, c)
    Cs = {b: sum(w[k] * z[b][k][_rows(sl, hz[k])].mean(axis=0) for k in kept) for b in BASELINES}
    C = {b: float(np.mean(Cs[b])) for b in BASELINES}
    order = sorted(BASELINES, key=lambda b: (-C[b], BASELINES.index(b)))
    out["composite"] = {"value": C, "ranking": order}

    # ---- 5. delta* and the power
    resolvable = nJ >= H4_MIN_SEEDS               # m-2: below the declared seed count no gap may resolve
    gaps = []
    for hi_b, lo_b in zip(order, order[1:]):
        diff = Cs[hi_b] - Cs[lo_b]
        g, se = float(np.mean(diff)), float(np.std(diff, ddof=1) / math.sqrt(nJ))
        gaps.append({"upper": hi_b, "lower": lo_b, "gap": g, "se": se,
                     "resolved": bool(resolvable and g > RESOLVE_Z * se)})
    spread = C[order[0]] - C[order[-1]]
    resolved = [g["gap"] for g in gaps if g["resolved"]]
    if resolved:
        raw, how = min(resolved), "the smallest resolved adjacent gap"
    elif not resolvable:
        raw, how = DELTA_FRACTION * spread, (f"fewer than {H4_MIN_SEEDS} seeds: no gap may resolve; the fraction of "
                                             "the baselines' spread")
    else:
        raw, how = DELTA_FRACTION * spread, "no gap resolved: the fraction of the baselines' spread"
    delta = min(DELTA_MAX, max(DELTA_MIN, raw))
    if raw < DELTA_MIN:
        how += "; raised to the floor"
    if raw > DELTA_MAX:
        how += "; held at the declared cap"
    unit_name = {"share": "share", "days": "sessions", "dollars": "dollars"}
    in_units = {}
    for rec in dims_out:
        if rec["name"] in w:
            scale = 1.0 if rec["kind"] == "share" else rec["hi"] - rec["lo"]
            in_units[rec["name"]] = {"delta_star": delta * scale / w[rec["name"]],
                                     "delta_min": DELTA_MIN * scale / w[rec["name"]], "unit": unit_name[rec["kind"]]}
    best = order[0]
    rc = _rows(sl, max(hz[k] for k in kept))
    unit = {b: sum(w[k] * z[b][k][rc] for k in kept) for b in BASELINES}          # per-unit composite, common set
    sig = {}
    for b in BASELINES:
        if b == best:
            s = math.sqrt(2.0) * math.sqrt(float(np.mean(np.var(unit[best], axis=1, ddof=1))))
        else:
            s = math.sqrt(float(np.mean(np.var(unit[best] - unit[b], axis=1, ddof=1))))
        sig[b] = min(1.0, s)
    deltas = {b: delta + (C[best] - C[b]) for b in BASELINES}
    alpha = level(K_TEST)
    hk = {k: hz[k] for k in kept}
    Q = q_factor(w, hk, test_starts, J)
    pw = conjoint_power(deltas, sig, Q, alpha)
    pw1 = conjoint_power(deltas, {b: 1.0 for b in BASELINES}, Q, alpha)
    Jn = None
    if conjoint_power(deltas, sig, q_factor(w, hk, test_starts, J_MAX), alpha) >= POWER_TARGET:
        lo_j, hi_j = 1, J_MAX
        while lo_j < hi_j:
            mid = (lo_j + hi_j) // 2
            if conjoint_power(deltas, sig, q_factor(w, hk, test_starts, mid), alpha) >= POWER_TARGET:
                hi_j = mid
            else:
                lo_j = mid + 1
        Jn = lo_j
    out["delta_star"] = {"value": delta, "raw": raw, "how": how, "gaps": gaps, "spread": spread,
                         "resolvable": resolvable, "min_seeds": H4_MIN_SEEDS, "resolve_z": RESOLVE_Z,
                         "floor": DELTA_MIN, "cap": DELTA_MAX, "fraction": DELTA_FRACTION, "in_units": in_units}
    out["power"] = {"alpha": alpha, "k": K_TEST, "target": POWER_TARGET, "test_seeds": J,
                    "test_starts": {str(h): int(test_starts[h]) for h in sorted(test_starts)}, "Q": Q,
                    "planted": f"{best} + delta*", "pair_delta": deltas, "pair_sigma": sig,
                    "pair_power": {b: pair_power(deltas[b], Q, sig[b], alpha) for b in BASELINES},
                    "conjoint_lower": pw, "conjoint_lower_sigma1": pw1, "J_needed": Jn,
                    "meets_target": bool(pw >= POWER_TARGET),
                    "J_needed_within_declared": bool(Jn is not None and Jn <= J),
                    "at_level": f"k = {K_TEST}; recomputed at the assigned k if it differs (m-8)"}

    # ---- 6. limits
    present = [L for L in LIMITS if L.key in per[BASELINES[0]]]
    zp = limit_z(len(present))
    lims = []
    for L in LIMITS:
        if L not in present:
            lims.append({"name": L.name, "measure": L.measure, "direction": L.direction, "status": "not set",
                         "reason": "the measure is absent from H4's declared output (its manifest does not list it)"})
            continue
        r = _rows(sl, L.horizon)
        M = {b: _stat(per[b][L.key][r], L.stat) for b in BASELINES}
        sd = {b: float(np.std([_stat(per[b][L.key][r][:, c], L.stat) for c in range(nJ)], ddof=1))
              for b in BASELINES}
        ceil_ = L.direction == "ceiling"
        key_best = (lambda b: (M[b], BASELINES.index(b))) if ceil_ else (lambda b: (-M[b], BASELINES.index(b)))
        key_worst = (lambda b: (-M[b], BASELINES.index(b))) if ceil_ else (lambda b: (M[b], BASELINES.index(b)))
        bb, bw = min(BASELINES, key=key_best), min(BASELINES, key=key_worst)
        se = sd[bb] * math.sqrt(n_search[L.horizon] / (J * int(test_starts[L.horizon])))
        need = M[bb] + zp * se if ceil_ else M[bb] - zp * se
        if (ceil_ and M[bw] >= need) or (not ceil_ and M[bw] <= need):
            val, binds = M[bw], "worst_baseline"
        else:
            val, binds = need, "headroom"
        pooled = np.concatenate([per[b][L.key][r].ravel() for b in BASELINES])
        top = {"share": 1.0, "days": W + 1.0}.get(L.kind, math.inf)
        if (ceil_ and val >= top) or (not ceil_ and val <= 0.0):
            vac = "at or beyond the a priori end of its range"
        elif (ceil_ and val >= float(pooled.max())) or (not ceil_ and val <= float(pooled.min())):
            vac = "beyond every baseline unit (no baseline's unit distribution crosses it)"
        else:
            vac = None
        lims.append({"name": L.name, "measure": L.measure, "key": L.key, "direction": L.direction,
                     "horizon": L.horizon, "stat": L.stat, "status": "set", "value": _r(val), "binds": binds,
                     "best": bb, "worst": bw, "baseline_values": M, "best_se_test": se, "headroom_needed": _r(need),
                     "headroom_z": zp, "vacuous": vac is not None, "vacuous_reason": vac,
                     "by_search_year": {b: _year_estimates(per[b][L.key], ref.starts, r, L.stat) for b in BASELINES},
                     "budget": Bstar if L.key == "not_paid_within_B" else None})
    out["limits"] = {"values": lims, "check_level": LIMIT_CHECK_LEVEL, "headroom_z": zp, "limits_set": len(present),
                     "form": "the point estimate governs; the one-sided check beside, never deciding (E-230)"}
    return Wave42Values(out)


__all__ = ["RULE_ID", "CONSTANTS", "DIMENSIONS", "LIMITS", "BASELINES", "Dim", "LimitSpec", "BaselineReading",
           "H4Binding", "H4_MANIFEST_KEYS", "TEST_STARTS_SOURCE_KEYS", "Wave42Refused", "Wave42Values",
           "setting_rule", "fee_lattice", "equal_weights", "spearman", "bankroll_states", "q_factor", "pair_power",
           "conjoint_power", "limit_z", "level", "input_digest", "readings_digest", "calendar_digest"]
