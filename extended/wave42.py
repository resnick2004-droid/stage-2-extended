"""Wave 4.2's setting rule, as a pure function (`docs/plans/WAVE42_SETTING_RULE.md`; E-221, O-3; CHARTER 3.7-3.9).

Given H4's per-baseline readings on the **search years only** (the naive coin, P-14, P-15 and P-16; every per-unit
measure the rule reads, as a matrix of start days by coin seeds), `setting_rule` returns, mechanically:

1. **the bankroll budgets B** of measure (24), and the primary budget B* that P under the bankroll stop and the
   bankroll limit read (the rule's section 3);
2. **the composite's dimensions, normalisers and weights** (section 4), or the fallback P_B alone (section 4.4);
3. **the size that matters delta*** (O-3) and the power the three-way test then has at it (section 5);
4. **the limits**, each with its direction, and the level of the one-sided check reported beside them (section 6).

Nothing here draws randomness, reads a file, a bar or a result, or knows a held-out outcome: the held-out years enter
only as the declared count of complete starts per horizon on the pinned calendar and the declared number of test
seeds, both the three-way test's (its declaration, from `three_way_arith`'s calendar arithmetic). An input tagged
anything but the search block, or carrying a start day outside the search years, is refused before any value is
computed (`Wave42Refused`). Every constant is the document's, which `tests/test_wave42_rule.py` machine-reads.
"""
from __future__ import annotations

import hashlib
import json
import math
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
BASELINES = ("naive_coin", "p14", "p15", "p16")                # CHARTER 2: Topstep's baseline set, in this order
W = 126                                                        # the first-payout window (U1, Q-44: a ledger constant)
MONTH = 21
AHEAD_TOL = 1e-6                                               # MEASURES 1.2 (m-11)
BUDGET_QUANTILES = (0.50, 0.75, 0.90)
PRIMARY_BUDGET_QUANTILE = 0.75
CAP_QUANTILES = (0.05, 0.95)
CAP_MARGIN = 0.25
REDUNDANT_RHO = 0.90
RESOLVE_Z = 2.0
DELTA_FRACTION = 0.25
DELTA_MIN = 0.01
POWER_TARGET = MDL_POWER
K_TEST = 13
LIMIT_CHECK_LEVEL = 0.05
J_MAX = 10 ** 7

CONSTANTS: dict[str, Any] = {
    "RULE_ID": RULE_ID, "SEARCH_FIRST": SEARCH_FIRST, "SEARCH_LAST": SEARCH_LAST, "BLOCK": BLOCK,
    "BASELINES": list(BASELINES), "W": W, "MONTH": MONTH, "AHEAD_TOL": AHEAD_TOL,
    "BUDGET_QUANTILES": list(BUDGET_QUANTILES), "PRIMARY_BUDGET_QUANTILE": PRIMARY_BUDGET_QUANTILE,
    "CAP_QUANTILES": list(CAP_QUANTILES), "CAP_MARGIN": CAP_MARGIN, "REDUNDANT_RHO": REDUNDANT_RHO,
    "RESOLVE_Z": RESOLVE_Z, "DELTA_FRACTION": DELTA_FRACTION, "DELTA_MIN": DELTA_MIN, "POWER_TARGET": POWER_TARGET,
    "K_TEST": K_TEST, "LIMIT_CHECK_LEVEL": LIMIT_CHECK_LEVEL, "J_MAX": J_MAX,
}


@dataclass(frozen=True)
class Dim:
    """One composite dimension: its objective term (CHARTER 2's order), MEASURES.md's number, the per-unit key it
    reads (or the derived value at B*), its horizon, its direction (+1 higher is better, -1 lower is better) and its
    kind (`share`: fixed caps [0, 1]; `days`: a priori [0, W + 1]; `dollars`: a priori [0, inf))."""
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
    "cash_to_first_pass": (W, 0.0, math.inf),
    "peak_oop_12_months": (252, 0.0, math.inf),
    "share_months_positive": (252, 0.0, 1.0),
}
OPTIONAL = {"orders_max": (W, 0.0, math.inf), "accounts_max": (W, 0.0, math.inf), "taken_mean": (W, 0.0, math.inf)}
STATS = {"mean": None, "p10": 0.10, "p50": 0.50, "p90": 0.90}


class Wave42Refused(RuntimeError):
    """The rule refuses its input before any value is computed."""


@dataclass(frozen=True)
class BaselineReading:
    """One baseline's H4 reading: its block tag, its start days (ISO dates, increasing) with the sessions each has left
    in its block (MEASURES 1.1's obs), the coin seeds, and per measure key a matrix `values[key][s, c]`."""
    name: str
    block: str
    starts: tuple[str, ...]
    sessions_left: tuple[int, ...]
    seeds: tuple[int, ...]
    values: Mapping[str, Any]


# ------------------------------------------------------------------------------------------------------- validation
def _refuse(msg: str) -> Wave42Refused:
    return Wave42Refused(f"Wave 4.2's rule refuses its input: {msg}")


def _validate(readings: Mapping[str, BaselineReading], fee_unit: float, fee_source: str,
              test_starts: Mapping[int, int], test_seeds: int) -> dict[str, dict[str, np.ndarray]]:
    for b in readings.values():                                    # the held-out guard first, before anything else
        if b.block != BLOCK:
            raise _refuse(f"{b.name!r} is tagged block {b.block!r}; only the search years ({BLOCK!r}) are read")
        for d in b.starts:
            if not (SEARCH_FIRST <= str(d) <= SEARCH_LAST) or str(d) >= HELD_OUT_FIRST:
                raise _refuse(f"{b.name!r} has start day {d!r} outside the search years {SEARCH_FIRST}..{SEARCH_LAST}"
                              " (a held-out or confirmation day is never read)")
    if set(readings) != set(BASELINES) or any(readings[k].name != k for k in readings):
        raise _refuse(f"the baselines are exactly {BASELINES}, each under its own name; got {sorted(readings)}")
    ref = readings[BASELINES[0]]
    n, J = len(ref.starts), len(ref.seeds)
    if n < 1 or J < 2 or len(set(ref.seeds)) != J:
        raise _refuse("at least one start day and at least two distinct coin seeds")
    if list(ref.starts) != sorted(set(ref.starts)) or len(ref.sessions_left) != n:
        raise _refuse("start days strictly increasing, one sessions-left count each")
    sl = np.asarray(ref.sessions_left)
    if (sl < 1).any() or (np.diff(sl) >= 0).any():
        raise _refuse("sessions left are positive and strictly decreasing in start order")
    for b in readings.values():
        if tuple(b.starts) != tuple(ref.starts) or tuple(b.sessions_left) != tuple(ref.sessions_left) \
                or tuple(b.seeds) != tuple(ref.seeds):
            raise _refuse(f"{b.name!r} is not paired with {ref.name!r}: same start days, sessions left and seeds")
    if not (isinstance(fee_unit, (int, float)) and math.isfinite(fee_unit) and fee_unit > 0):
        raise _refuse("the fee unit is a positive dollar amount from the verified ledger")
    if not (isinstance(fee_source, str) and fee_source.strip()):
        raise _refuse("the fee unit names its source in the verified ledger")
    if not (isinstance(test_seeds, int) and test_seeds >= 1):
        raise _refuse("the test's seed count J is a positive integer (H3's declaration)")
    hs = sorted({d.horizon for d in DIMENSIONS} | {lim.horizon for lim in LIMITS})
    if any(h not in test_starts for h in hs):
        raise _refuse(f"the test's complete-start count is declared for every horizon {hs}")
    counts = [int(test_starts[h]) for h in hs]
    if any(c < 1 for c in counts) or any(b > a for a, b in zip(counts, counts[1:])):
        raise _refuse("the test's complete-start counts are positive and non-increasing in the horizon")
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
        out[name] = vals
    for key in OPTIONAL:
        have = [key in out[name] for name in BASELINES]
        if any(have) and not all(have):
            raise _refuse(f"the optional measure {key!r} is given for some baselines and not others")
    return out


# --------------------------------------------------------------------------------------------------- the pieces
def _rows(sl: np.ndarray, h: int) -> np.ndarray:
    return sl >= h


def _q(x: np.ndarray, p: float) -> float:
    return float(np.quantile(np.asarray(x, dtype=float).ravel(), p))       # numpy's linear rule (MEASURES 1.3)


def fee_lattice(x: float, fee_unit: float) -> float:
    """The smallest whole number of fee units at or above x, and at least one (section 3)."""
    k = max(1, math.ceil(x / fee_unit - 1e-9))
    return float(k * fee_unit)


def roc_weights(D: int) -> list[float]:
    """Rank-order-centroid weights for D ranked dimensions: w_i = (1/D) sum_{j=i..D} 1/j (Barron and Barrett 1996)."""
    return [sum(1.0 / j for j in range(i, D + 1)) / D for i in range(1, D + 1)]


def spearman(x: np.ndarray, y: np.ndarray) -> float | None:
    """Spearman's rho with average ranks; None when either side is constant (no rank order to compare)."""
    rx, ry = stats.rankdata(x), stats.rankdata(y)
    if rx.std() == 0 or ry.std() == 0:
        return None
    return float(np.corrcoef(rx, ry)[0, 1])


def _derived(v: dict[str, np.ndarray], B: float) -> dict[str, np.ndarray]:
    """The per-unit values at budget B: months ahead under B (MEASURES 2), run out and not paid within B ((24))."""
    ahead = sum(((v[f"net_month_{m}"] > AHEAD_TOL) & (v[f"peak_month_{m}"] <= B)).astype(float) for m in (1, 2, 3))
    x6, paid = v["spent_before_first_payout"], v["first_payout_days"] <= W
    return {"P_B": ahead / 3.0, "run_out": (x6 > B).astype(float),
            "not_paid_within_B": 1.0 - (paid & (x6 <= B)).astype(float)}


def _caps(dim: Dim, pooled: np.ndarray, fee_unit: float) -> tuple[float, float, str]:
    if dim.kind == "share":
        return 0.0, 1.0, "fixed [0, 1]"
    a, b = (0.0, W + 1.0) if dim.kind == "days" else (0.0, math.inf)
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


# ------------------------------------------------------------------------------------------------------ the output
@dataclass(frozen=True)
class Wave42Values:
    values: dict[str, Any]

    def as_json(self) -> str:
        return json.dumps(self.values, sort_keys=True, separators=(",", ":"), allow_nan=False)

    def digest(self) -> str:
        return hashlib.sha256(self.as_json().encode("utf-8")).hexdigest()


def input_digest(readings: Mapping[str, BaselineReading], fee_unit: float, fee_source: str,
                 test_starts: Mapping[int, int], test_seeds: int) -> str:
    h = hashlib.sha256()
    h.update(json.dumps({"fee_unit": float(fee_unit), "fee_source": fee_source,
                         "test_starts": {str(k): int(v) for k, v in sorted(test_starts.items())},
                         "test_seeds": int(test_seeds)}, sort_keys=True).encode())
    for name in sorted(readings):
        b = readings[name]
        h.update(json.dumps([b.name, b.block, list(b.starts), [int(x) for x in b.sessions_left],
                             [int(x) for x in b.seeds]]).encode())
        for key in sorted(b.values):
            h.update(key.encode())
            h.update(np.ascontiguousarray(np.asarray(b.values[key], dtype=np.float64)).tobytes())
    return h.hexdigest()


def _r(x: float) -> float:
    return float(x)


# ------------------------------------------------------------------------------------------------------- the rule
def setting_rule(readings: Mapping[str, BaselineReading] | Sequence[BaselineReading], *, fee_unit: float,
                 fee_source: str, test_starts: Mapping[int, int], test_seeds: int) -> Wave42Values:
    """The whole rule (sections 3-6), in its fixed order: budgets, dimensions and weights, delta\\* and power, limits."""
    if not isinstance(readings, Mapping):
        readings = {b.name: b for b in readings}
    vals = _validate(readings, fee_unit, fee_source, test_starts, test_seeds)
    ref = readings[BASELINES[0]]
    sl = np.asarray(ref.sessions_left)
    nJ = len(ref.seeds)
    J = int(test_seeds)
    n_search = {h: int(_rows(sl, h).sum()) for h in {d.horizon for d in DIMENSIONS} | {lim.horizon for lim in LIMITS}}
    out: dict[str, Any] = {"rule_id": RULE_ID, "constants": CONSTANTS,
                           "input_sha256": input_digest(readings, fee_unit, fee_source, test_starts, test_seeds),
                           "search_starts": {str(h): n_search[h] for h in sorted(n_search)}, "seeds": nJ}

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

    # ---- 4. dimensions, caps, redundancy, weights
    per = {b: {**vals[b], **_derived(vals[b], Bstar)} for b in BASELINES}
    z: dict[str, dict[str, np.ndarray]] = {b: {} for b in BASELINES}
    dims_out = []
    for d in DIMENSIONS:
        r = _rows(sl, d.horizon)
        pooled = np.concatenate([per[b][d.key][r].ravel() for b in BASELINES])
        lo, hi, how = _caps(d, pooled, fee_unit)
        for b in BASELINES:
            z[b][d.name] = _z(d, per[b][d.key], lo, hi)
        dims_out.append({"name": d.name, "term": d.term, "measure": d.measure, "key": d.key, "horizon": d.horizon,
                         "direction": "higher" if d.direction > 0 else "lower", "lo": _r(lo), "hi": _r(hi),
                         "caps": how, "baseline_means": {b: float(np.mean(z[b][d.name][r])) for b in BASELINES}})
    kept: list[str] = []
    hz = {d.name: d.horizon for d in DIMENSIONS}
    for d, rec in zip(DIMENSIONS, dims_out):
        if not kept:
            kept.append(d.name)
            rec.update(kept=True, reason="first in the objective order; never dropped")
            continue
        hit = None
        for k in kept:
            r = _rows(sl, max(hz[k], d.horizon))
            rho = spearman(np.concatenate([z[b][d.name][r].ravel() for b in BASELINES]),
                           np.concatenate([z[b][k][r].ravel() for b in BASELINES]))
            if rho is not None and rho >= REDUNDANT_RHO:
                hit = (k, rho)
                break
        if hit:
            rec.update(kept=False, reason=f"redundant with {hit[0]}", rho=_r(hit[1]))
        else:
            kept.append(d.name)
            rec.update(kept=True, reason="not redundant with an earlier kept dimension")
    w = dict(zip(kept, roc_weights(len(kept))))
    for rec in dims_out:
        rec["weight"] = w.get(rec["name"], 0.0)
    form = "composite" if len(kept) >= 2 else "fallback"
    out["dimensions"] = dims_out
    out["weights"] = w
    out["form"] = form

    # composite per baseline per seed: C_b(c) = sum_d w_d mean_{s in E_d} z_d(b, s, c)
    Cs = {b: sum(w[k] * z[b][k][_rows(sl, hz[k])].mean(axis=0) for k in kept) for b in BASELINES}
    C = {b: float(np.mean(Cs[b])) for b in BASELINES}
    order = sorted(BASELINES, key=lambda b: (-C[b], BASELINES.index(b)))
    out["composite"] = {"value": C, "ranking": order}

    # ---- 5. delta* and the power
    gaps = []
    for hi_b, lo_b in zip(order, order[1:]):
        diff = Cs[hi_b] - Cs[lo_b]
        g, se = float(np.mean(diff)), float(np.std(diff, ddof=1) / math.sqrt(nJ))
        gaps.append({"upper": hi_b, "lower": lo_b, "gap": g, "se": se, "resolved": bool(g > RESOLVE_Z * se)})
    spread = C[order[0]] - C[order[-1]]
    resolved = [g["gap"] for g in gaps if g["resolved"]]
    if resolved:
        raw, how = min(resolved), "the smallest resolved adjacent gap"
    else:
        raw, how = DELTA_FRACTION * spread, "no gap resolved: the fraction of the baselines' spread"
    delta = max(DELTA_MIN, raw)
    if delta == DELTA_MIN and raw < DELTA_MIN:
        how += "; raised to the floor"
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
    Q = q_factor(w, {k: hz[k] for k in kept}, test_starts, J)
    pw = conjoint_power(deltas, sig, Q, alpha)
    pw1 = conjoint_power(deltas, {b: 1.0 for b in BASELINES}, Q, alpha)
    Jn = None
    if conjoint_power(deltas, sig, q_factor(w, {k: hz[k] for k in kept}, test_starts, J_MAX), alpha) >= POWER_TARGET:
        lo_j, hi_j = 1, J_MAX
        while lo_j < hi_j:
            mid = (lo_j + hi_j) // 2
            if conjoint_power(deltas, sig, q_factor(w, {k: hz[k] for k in kept}, test_starts, mid),
                              alpha) >= POWER_TARGET:
                hi_j = mid
            else:
                lo_j = mid + 1
        Jn = lo_j
    out["delta_star"] = {"value": delta, "raw": raw, "how": how, "gaps": gaps, "spread": spread,
                         "floor": DELTA_MIN, "fraction": DELTA_FRACTION}
    out["power"] = {"alpha": alpha, "k": K_TEST, "target": POWER_TARGET, "test_seeds": J,
                    "test_starts": {str(h): int(test_starts[h]) for h in sorted(test_starts)}, "Q": Q,
                    "planted": f"{best} + delta*", "pair_delta": deltas, "pair_sigma": sig,
                    "pair_power": {b: pair_power(deltas[b], Q, sig[b], alpha) for b in BASELINES},
                    "conjoint_lower": pw, "conjoint_lower_sigma1": pw1, "J_needed": Jn,
                    "meets_target": bool(pw >= POWER_TARGET)}

    # ---- 6. limits
    zp = float(stats.norm.ppf(POWER_TARGET))
    lims = []
    for L in LIMITS:
        if L.key not in per[BASELINES[0]]:
            lims.append({"name": L.name, "measure": L.measure, "direction": L.direction, "status": "not set",
                         "reason": "the measure is absent from every baseline's H4 reading"})
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
        vac = (L.kind == "share") and ((ceil_ and val >= 1.0) or (not ceil_ and val <= 0.0))
        lims.append({"name": L.name, "measure": L.measure, "key": L.key, "direction": L.direction,
                     "horizon": L.horizon, "stat": L.stat, "status": "set", "value": _r(val), "binds": binds,
                     "best": bb, "worst": bw, "baseline_values": M, "best_se_test": se, "headroom_needed": _r(need),
                     "vacuous": bool(vac), "budget": Bstar if L.key == "not_paid_within_B" else None})
    out["limits"] = {"values": lims, "check_level": LIMIT_CHECK_LEVEL, "form": "the point estimate governs (E-230)"}
    return Wave42Values(out)


__all__ = ["RULE_ID", "CONSTANTS", "DIMENSIONS", "LIMITS", "BASELINES", "Dim", "LimitSpec", "BaselineReading",
           "Wave42Refused", "Wave42Values", "setting_rule", "fee_lattice", "roc_weights", "spearman", "q_factor",
           "pair_power", "conjoint_power", "level", "input_digest"]
