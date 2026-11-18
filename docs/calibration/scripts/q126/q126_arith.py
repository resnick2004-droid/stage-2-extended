"""Q-126's plan (`docs/calibration/DRAFT_Q-126_one_sample_plan_2.md`, sixth text): its arithmetic -- no bar, no market
outcome, no random number. Every figure the plan states is printed here, from three kinds of input only:

- the plan's declared constants: the validation's exposure (23 subsets at each of five sizes, two values, five exact
  side models), the sizing rule's two probabilities, the family levels 0.05/(k(k+1)) at k = 13..20, 200,000
  replications, the 1,123 Monte Carlo nulls of Q-108's class;
- columns of Q-108's result files, read as a calibration (they are not market outcomes): `results/q108_choice.csv`
  (`P`, `p_mc`), `results/q108_cal_size.csv` (`admitted_share`) and `results/q108_val_size.csv` (`count_k*`);
- Q-108's two run logs (`%LOCALAPPDATA%/stage2-extended-runs/q108-calibrate.log` and `q108-validate.log` by default):
  their per-null timing lines (`... of <den>; <t> s, ws <MB> MB`), their `EXIT 0 (<s> s)` lines and the pairs step's
  peak working set, for the cost (section 6.2). Without the logs the cost lines are not printed.

    python docs/calibration/scripts/q126/q126_arith.py [--repo ROOT] [--cal-log PATH] [--val-log PATH]

`main()` prints everything; the functions are imported by `tests/test_q126_draft.py`, which holds the plan's stated
figures to them."""
from __future__ import annotations

import argparse
import math
import os
import re
from functools import lru_cache
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[4]

# ------------------------------------------------------------------------------------------- declared constants

KS = tuple(range(13, 21))
LEV = {k: 0.05 / (k * (k + 1)) for k in KS}
REPS = 200_000
SIZES = (200, 500, 1000, 2000, 5000)
VALUES = ("win1", "net3")
EXACT_MODELS = ("flip42", "flip55", "flip63", "alt45", "alt55")
#: the validation's exposure: Q-108's class, unchanged (23 fresh subsets at each size)
VAL_SUBSETS_PER_SIZE = 23
#: the Monte Carlo nulls of Q-108's class (its plan's 3.5), unchanged in the validation
MC_NULLS = 1123
#: the sizing rule: a pooled bad-subset rate at which the validation passes with probability at most VAL_PASS is seen
#: at least once in the calibration with probability at least DETECT (the rule of three's form)
VAL_PASS = 0.9
DETECT = 0.95
#: the declared calibration subsets at each size (the plan's 3.2): the rule's minimum rounded up to a multiple of 20
CAL_SUBSETS_PER_SIZE = 660
#: the margins of the scope-D grid (the plan's 2.2), ascending; the scope-Q branch takes those of at least 1.5
GRID = (1.0, 1.125, 1.25, 1.375, 1.5, 1.75, 2.0)
Q_BRANCH_MIN = 1.5
#: the reference against which power costs are stated (the brief's item 7)
REFERENCE = ("cons_m1.25", "Q")


def n_val() -> int:
    """The validation's exposed subsets, pooled over sizes (each at both values and every exact model)."""
    return VAL_SUBSETS_PER_SIZE * len(SIZES)


def punished_rate(n: int | None = None, val_pass: float = VAL_PASS) -> float:
    """The pooled bad-subset rate r_V at which the validation's n subsets all hold with probability val_pass."""
    n = n_val() if n is None else n
    return 1.0 - val_pass ** (1.0 / n)


def min_cal_subsets(n: int | None = None, val_pass: float = VAL_PASS, detect: float = DETECT) -> int:
    """The least N with 1 - (1 - r_V)^N >= detect: N = ceil(ln(1 - detect) / ln(1 - r_V))."""
    r = punished_rate(n, val_pass)
    return math.ceil(math.log(1.0 - detect) / math.log(1.0 - r) - 1e-9)


def detection(N: int, r: float) -> float:
    return 1.0 - (1.0 - r) ** N


def minimax_one(a: float) -> float:
    """sup over r of P(the calibration's N subsets hold) x P(the validation's n fail), a = n / N: max over x in (0, 1)
    of x^(1/a) (1 - x), attained at x = 1 / (1 + a)."""
    x = 1.0 / (1.0 + a)
    return x ** (1.0 / a) * (1.0 - x)


def minimax_nested(a: float) -> float:
    """For candidates nested in their margin (a larger margin's rejections are a subset of a smaller's, so its
    eligibility is implied), the choice -- the smallest eligible margin -- fails the validation's exact part with
    probability at most the integral of 1 - p^a over p in (0, 1), which is a / (1 + a), whatever the rates."""
    return a / (1.0 + a)


# ------------------------------------------------------------------------------------------- the floor's allowance (M2)

#: the declared allowance (the plan's 3.2): zero tolerance, no bad subset among the 3,300 (the lead's E-176, which
#: reverses E-173's allowance after its computed cost)
ALLOWANCE = 0
#: beside, a reading: E-173's reversed ruling -- at the bad-subset rate where the validation's exact part passes a
#: candidate with probability GUARD_PASS, the floor (at most c bad subsets) refuses it with at most MAX_REFUSAL; c the
#: least such count. `allowance()` computes it; it must equal E173_ALLOWANCE
GUARD_PASS = 0.95
MAX_REFUSAL = 0.10
E173_ALLOWANCE = 3
#: the allowances compared in the plan's 4.3 reading
COMPARED = (0, 1, 2, 3)
#: the rates at which the floor's power is tabulated (the plan's 4.3), beside r_95 and r_V
FLOOR_RATES = (1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 2e-3)


def guard_rate(n: int | None = None) -> float:
    """r_95: the pooled bad-subset rate at which the validation's n subsets all hold with probability GUARD_PASS."""
    return punished_rate(n, GUARD_PASS)


def floor_admits(r: float, N: int | None = None, c: int | None = None) -> float:
    """P(at most c bad subsets among N | rate r): the floor's chance of admitting a candidate."""
    N = CAL_SUBSETS_PER_SIZE * len(SIZES) if N is None else N
    c = ALLOWANCE if c is None else c
    return float(stats.binom.cdf(c, N, r))


def allowance(N: int | None = None, n: int | None = None) -> int:
    """E-173's c (beside): the least c whose floor refuses a candidate at r_95 with probability at most MAX_REFUSAL."""
    r = guard_rate(n)
    c = 0
    while 1.0 - floor_admits(r, N, c) > MAX_REFUSAL:
        c += 1
    return c


def bound_nested_c(N: int, n: int, c: int) -> float:
    """The nested branch's bound with an allowance c: the choice fails the validation's exact part with probability at
    most the integral over p in (0, 1) of 1 - (1 - G^-1(p))^n, G(r) = P(Bin(N, r) <= c). Substituting p = G(r), it is
    1 - E[(1 - R)^n] with R ~ Beta(c + 1, N - c): 1 - prod_{i < n} (N - c + i) / (N + 1 + i). At c = 0 it is
    n / (N + n) = a / (1 + a)."""
    return 1.0 - math.exp(sum(math.log((N - c + i) / (N + 1 + i)) for i in range(n)))


def bound_one_c(N: int, n: int, c: int) -> float:
    """One candidate's bound with an allowance c: sup over r of P(Bin(N, r) <= c) (1 - (1 - r)^n), on a fine log grid
    of r (the maximum is interior and smooth)."""
    r = np.exp(np.linspace(math.log(1e-7), math.log(0.2), 400_001))
    return float((stats.binom.cdf(c, N, r) * (1.0 - (1.0 - r) ** n)).max())


def cp_upper(x: int, m: int, conf: float = 0.95) -> float:
    """The one-sided Clopper-Pearson upper limit on a rate after x bad among m."""
    return float(stats.beta.ppf(conf, x + 1, m - x))


def rule_bounds(N: int | None = None, n: int | None = None, c: int | None = None) -> dict[str, float]:
    """The bounds on the chance that a statistic the rule chooses holds the calibration and fails the validation's
    exact part: the primary (scope D's nested grid plus C6; or, when scope D has none, the scope-Q branch alone) and
    the second statistic (the scope-Q branch's choice, validated beside when scope D chooses; M3)."""
    N = CAL_SUBSETS_PER_SIZE * len(SIZES) if N is None else N
    n = n_val() if n is None else n
    c = ALLOWANCE if c is None else c
    nest, one = bound_nested_c(N, n, c), bound_one_c(N, n, c)
    return {"nested": nest, "one": one, "primary": nest + one, "second": nest, "all": 2 * nest + one}


def bound_by_subsets(Ns=(3300, 6600, 13200, 26400), n: int | None = None) -> list[tuple[int, int, float]]:
    """Beside, not taken: (N, the ruled allowance at N, the nested bound) for larger calibrations. Under the ruling the
    floor admits a candidate at r_95, which the validation's exact part fails with 1 - GUARD_PASS, so the bound tends
    to 1 - GUARD_PASS from above as N grows and never falls below it."""
    n = n_val() if n is None else n
    return [(N, allowance(N, n), bound_nested_c(N, n, allowance(N, n))) for N in Ns]


# ------------------------------------------------------------------------------------------- the floor's readings (M-C)

#: the red team's illustrative rate profiles over the seven margins 1.0 .. 2.0 (its re-read, M-C): readings, not
#: estimates
PROFILES = {
    "A": (3e-4, 3e-4, 1e-4, 3e-5, 1e-5, 3e-6, 1e-6),
    "B": (1e-3, 3e-4, 1e-4, 3e-5, 1e-5, 3e-6, 1e-6),
    "C": (3e-4,) * 7,
}
#: the flat-in-m rates of the reading (Q-125's H-d: no finite margin removes the mechanism in scope Q)
FLAT_RATES = (1e-5, 3e-5, 1e-4, 3e-4, 1e-3)


def certificates(N: int | None = None, n: int | None = None) -> tuple[float, float]:
    """The 95 % upper limits on the pooled bad-subset rate after zero bad subsets: the calibration's N and the
    validation's n (one-sided Clopper-Pearson)."""
    N = CAL_SUBSETS_PER_SIZE * len(SIZES) if N is None else N
    n = n_val() if n is None else n
    return cp_upper(0, N), cp_upper(0, n)


def profile_reading(rates, c: int = 0, ratios=None, N: int | None = None, n: int | None = None) -> dict[str, float]:
    """On a nested grid with these bad-subset rates (margins ascending), every other condition assumed to pass: the
    chance the validation's exact part fails the choice, the chance the floor empties the branch (NONE), and the mean
    P ratio of a choice that is made and holds. Bad sets nested, so P(choice = i) = G(r_i) - G(r_{i-1})."""
    N = CAL_SUBSETS_PER_SIZE * len(SIZES) if N is None else N
    n = n_val() if n is None else n
    r = np.asarray(rates, dtype=float)
    G = stats.binom.cdf(c, N, r)
    pch = np.diff(np.r_[0.0, G])
    F = 1.0 - (1.0 - r) ** n
    held = pch * (1.0 - F)
    ratios = np.asarray(list(grid_p().values()) if ratios is None else ratios, dtype=float)
    return {"val_fail": float((pch * F).sum()), "none": float(1.0 - G[-1]),
            "mean_p": float((held * ratios).sum() / held.sum())}


def flat_none(r: float, N: int | None = None) -> float:
    """At a rate flat in m, the zero-tolerance floor empties the branch (every margin refused) with 1 - (1 - r)^N."""
    N = CAL_SUBSETS_PER_SIZE * len(SIZES) if N is None else N
    return 1.0 - (1.0 - r) ** N


# ------------------------------------------------------------------------------------------- the band check (M-D, F-1..F-3)

#: the bands of the plan's 2.5, as (lowest, highest) declared persistence in sessions
BANDS = {"below 42": (1, 41), "42 to 50": (42, 50), "51 to 62": (51, 62)}
#: scope D's admission (4.4) covers declared persistence below a quarter: its balance limit is taken over 1..63
ADMISSION_RANGE = (1, 63)
#: the balance limit's quantile: b is the largest, over every flip and Markov model whose length lies in the band, of
#: the BALANCE_Q quantile of |mean side| on the span's n sessions, every session non-tie (the dense case)
BALANCE_Q = 0.975
#: the runs interval's tail at each end, for a declared switching side (Markov models at the band's ends)
RUNS_TAIL = 0.0125
#: the in-band refusal allowed for any of the band's own models, of either kind (the lead's rule, E-184)
MAX_IN_BAND_REFUSAL = 0.05
#: the regime length (two quarters) whose sides the runs floor excludes, kept only where it costs no in-band refusal
EXCLUDED_REGIME = 126
#: Markov dwells beyond the class's longest (80), whose pass rates the residual states
BEYOND_DWELLS = (80, 100, 125, 150, 200)


def max_runs(n: int, L: int) -> int:
    """The most runs a side constant over blocks of at least L sessions can have on n sessions (Q-108's 4.4)."""
    return (int(n) - 1) // int(L) + 2


def dwell_runs(D: float, n: int = 657) -> float:
    """The expected runs of a Markov side of mean dwell D on n sessions: 1 + (n - 1)/D."""
    return 1.0 + (n - 1) / D


def flip_counts(n: int, L: int) -> list[list[int]]:
    """Each phase's block sizes of the L-session flip on n sessions (`lift_one_sample.flip_blocks`)."""
    return [np.bincount((np.arange(n) + p) // L).tolist() for p in range(L)]


def flip_mean_runs(n: int, L: int) -> float:
    """The flip's expected runs, its block signs independent and fair: 1 + (B - 1)/2, averaged over phases."""
    return float(np.mean([1.0 + (len(w) - 1) / 2.0 for w in flip_counts(n, L)]))


@lru_cache(maxsize=None)
def flip_balance(n: int, L: int) -> tuple[np.ndarray, np.ndarray]:
    """The exact distribution of |mean side| for the L-session flip on n sessions, every session non-tie, phase uniform:
    (values, cdf). The sum of independent fair signs times the block sizes, by convolution."""
    acc: dict[int, float] = {}
    for w in flip_counts(n, L):
        W = int(sum(w))
        d = np.zeros(2 * W + 1)
        d[W] = 1.0
        for x in w:
            d = 0.5 * (np.roll(d, int(x)) + np.roll(d, -int(x)))
        for k in np.flatnonzero(d > 0):
            v = abs(int(k) - W)
            acc[v] = acc.get(v, 0.0) + float(d[k]) / L
    vals = np.array(sorted(acc), dtype=float)
    return vals / n, np.cumsum([acc[int(v)] for v in vals])


@lru_cache(maxsize=None)
def markov_balance(n: int, D: float) -> tuple[np.ndarray, np.ndarray]:
    """The exact distribution of |mean side| for a Markov side of mean dwell D on n sessions (a fair first side, a
    reversal at each boundary with 1/D), by recursion over the count of long sessions: (values, cdf)."""
    q = 1.0 / D
    lo_, sh = np.zeros(n + 1), np.zeros(n + 1)
    lo_[1], sh[0] = 0.5, 0.5
    for _ in range(n - 1):
        nl = np.zeros(n + 1)
        nl[1:] = (1 - q) * lo_[:-1] + q * sh[:-1]
        sh = (1 - q) * sh + q * lo_
        lo_ = nl
    pk = lo_ + sh
    m = np.abs(2 * np.arange(n + 1) - n)
    acc: dict[int, float] = {}
    for k in range(n + 1):
        acc[int(m[k])] = acc.get(int(m[k]), 0.0) + float(pk[k])
    vals = np.array(sorted(acc), dtype=float)
    return vals / n, np.cumsum([acc[int(v)] for v in vals])


def quantile(dist, a: float = BALANCE_Q) -> float:
    vals, cdf = dist
    return float(vals[min(int(np.searchsorted(cdf, a - 1e-12)), len(vals) - 1)])


def exceeds(dist, b: float) -> float:
    """P(|mean side| > b)."""
    vals, cdf = dist
    i = int(np.searchsorted(vals, b + 1e-12)) - 1
    return max(0.0, float(1.0 - (cdf[i] if i >= 0 else 0.0)))


def balance_limit(n: int, lo: int, hi: int) -> float:
    """b: the largest BALANCE_Q quantile of |mean side| over every flip and Markov model of length lo..hi on n."""
    return max(max(quantile(flip_balance(n, L)), quantile(markov_balance(n, float(L)))) for L in range(lo, hi + 1))


def band_b(n: int, band: str) -> float:
    return balance_limit(n, *BANDS[band])


def admission_b(n: int) -> float:
    return balance_limit(n, *ADMISSION_RANGE)


def markov_runs_out(n: int, D: float, lo_r: int, hi_r: int | None) -> float:
    """P(R outside [lo_r, hi_r]) for a Markov side of dwell D on n sessions: R - 1 ~ Bin(n - 1, 1/D)."""
    below = float(stats.binom.cdf(lo_r - 2, n - 1, 1.0 / D))
    above = 0.0 if hi_r is None else float(stats.binom.sf(hi_r - 1, n - 1, 1.0 / D))
    return below + above


def runs_interval(n: int, band: str) -> tuple[int, int | None, str]:
    """A declared switching side's runs interval on n sessions, and whether the two-quarters floor is kept: from
    1 + the RUNS_TAIL quantile of Bin(n - 1, 1/hi), raised to one more than the most runs of a side constant over
    EXCLUDED_REGIME sessions only where no Markov model of the band then exceeds MAX_IN_BAND_REFUSAL (with the
    balance limit's share); to 1 + the 1 - RUNS_TAIL quantile of Bin(n - 1, 1/lo) (none for the band below 42)."""
    lo, hi = BANDS[band]
    lower = 1 + int(stats.binom.ppf(RUNS_TAIL, n - 1, 1.0 / hi))
    upper = None if band == "below 42" else 1 + int(stats.binom.ppf(1.0 - RUNS_TAIL, n - 1, 1.0 / lo))
    floor = max_runs(n, EXCLUDED_REGIME) + 1
    if floor <= lower:
        return lower, upper, "not binding"
    b = band_b(n, band)
    worst = max(markov_runs_out(n, float(D), floor, upper) + exceeds(markov_balance(n, float(D)), b)
                for D in range(lo, hi + 1))
    if worst <= MAX_IN_BAND_REFUSAL:
        return floor, upper, "kept"
    return lower, upper, "dropped"


def band_interval(n: int, band: str) -> tuple[int, int | None]:
    lo_r, hi_r, _ = runs_interval(n, band)
    return lo_r, hi_r


#: the regime filter's one-sided runs floor (the red team's V-1, E-186): the changes at declared decision points are at
#: least this quantile of Bin(B - 1, 1/2), B the regimes the span touches
REGIME_TAIL = 0.0125


def regime_floor(B: int) -> int:
    """The least number of sign changes a declared regime filter touching B regimes must show."""
    return int(stats.binom.ppf(REGIME_TAIL, int(B) - 1, 0.5)) if B > 1 else 0


def regime_miss(B: int) -> float:
    """P(fewer changes than the floor) under independent fair regime signs: the floor's refusal of a class regime
    filter."""
    f = regime_floor(B)
    return float(stats.binom.cdf(f - 1, int(B) - 1, 0.5)) if f > 0 else 0.0


def regime_refusal(n: int, L: int, b: float) -> float:
    """A bound on the in-band refusal of the L-session flip read as a declared regime filter: the runs floor's miss,
    averaged over phases, plus the balance limit's refusal (its spacing passes by construction)."""
    miss = float(np.mean([regime_miss(len(w)) for w in flip_counts(n, L)]))
    return miss + exceeds(flip_balance(n, L), b)


def in_band_refusals(n: int, band: str) -> dict[str, float]:
    """The largest in-band refusal over the band's own models, each a bound: regime filters (flips at every length in
    the band: the runs floor's miss plus the balance limit's) and switching sides (Markov at every dwell in the band:
    the runs interval's miss plus the balance limit's)."""
    lo, hi = BANDS[band]
    b = band_b(n, band)
    lo_r, hi_r = band_interval(n, band)
    fl = {L: regime_refusal(n, L, b) for L in range(lo, hi + 1)}
    mk = {D: markov_runs_out(n, float(D), lo_r, hi_r) + exceeds(markov_balance(n, float(D)), b)
          for D in range(lo, hi + 1)}
    out = {"regime": max(fl.values()), "regime_at": max(fl, key=fl.get),
           "switching": max(mk.values()), "switching_at": max(mk, key=mk.get)}
    for L in (lo, hi):
        out[f"flip{L}"] = fl[L]
        out[f"markov{L}"] = mk[L]
    return out


def regime_filter_check(sides, points, band: str, n: int | None = None) -> tuple[bool, list[str]]:
    """2.5's regime-filter test on a dense side series (one side per session, +1 or -1) and the declared decision points
    (the sessions at which a regime begins, inside the span): (passes, reasons for refusal).
    (a) spacing: every interior regime's length lies in the band; (b) every change of side falls on a decision point;
    (c) the changes are at least the runs floor for the B regimes touched; (d) the balance limit."""
    s = np.asarray(sides, dtype=int)
    n = len(s) if n is None else int(n)
    lo, hi = BANDS[band]
    pts = sorted(int(x) for x in points if 0 < int(x) < n)
    why = []
    gaps = np.diff(pts)
    if len(gaps) and not np.all((gaps >= lo) & (gaps <= hi)):
        why.append("spacing")
    changes = [j for j in range(1, n) if s[j] != s[j - 1]]
    if any(j not in set(pts) for j in changes):
        why.append("a change off the decision points")
    B = len(pts) + 1
    if len(changes) < regime_floor(B):
        why.append("runs floor")
    if abs(float(s.mean())) > band_b(n, band) + 1e-12:
        why.append("balance")
    return (not why), why


def gamed_sides(n: int = 657) -> dict[str, tuple[np.ndarray, list[int]]]:
    """The red team's three gamed sides (V-1), each with the decision points it would declare in 42 to 50, and an honest
    regime filter beside: {name: (sides, points)}."""
    one = np.r_[np.ones(328, int), -np.ones(n - 328, int)]
    one_pts = list(range(20, n, 44))                      # 44 apart, one of them at the switch (328)
    three = np.r_[np.ones(219, int), -np.ones(219, int), np.ones(n - 438, int)]
    steps = [44, 44, 44, 44, 43] * 3
    three_pts = list(np.cumsum(steps)[:-1])                # 44 or 43 apart, two of them at 219 and 438
    burst = np.r_[np.ones(320, int), np.array([(-1) ** k for k in range(1, 14)]), -np.ones(n - 333, int)]
    burst_pts = list(range(44, 320, 44)) + list(range(320, 334)) + list(range(377, n, 44))
    honest = np.array([1 if ((j + 20) // 44) % 2 == 0 else -1 for j in range(n)])
    honest_pts = list(range(24, n, 44))
    return {"one switch, unused points": (one, one_pts), "three fixed regimes": (three, three_pts),
            "two halves with a burst": (burst, burst_pts), "an honest 44-session filter": (honest, honest_pts)}


def edge_reversal_filter_check() -> tuple[bool, list[str]]:
    """The edge-reversal side read as a declared 42-to-50 regime filter: its 8 changes declared as decision points, with
    others 44 apart filling the span; its reversals put two changes one session apart."""
    n = 657
    s = []
    for k in range(3):
        sign = 1 if k % 2 == 0 else -1
        block = [sign] * 219
        block[1] = -sign
        s += block
    s = np.array(s)
    changes = [j for j in range(1, n) if s[j] != s[j - 1]]
    pts = sorted(set(changes) | set(range(44, n, 44)))
    return regime_filter_check(s, pts, "42 to 50", n)


def regime_floors(Bs=range(11, 18)) -> dict[int, tuple[int, float]]:
    """{B: (the runs floor, its miss)}."""
    return {B: (regime_floor(B), regime_miss(B)) for B in Bs}


def regime_blocks(n: int, band: str) -> tuple[int, int]:
    """The fewest and most regimes a filter of a length in the band touches on n sessions."""
    lo, hi = BANDS[band]
    Bs = [len(w) for L in range(lo, hi + 1) for w in flip_counts(n, L)]
    return min(Bs), max(Bs)


def class_tail(B: int, k: int) -> float:
    """P(at most k sign changes) for a class regime filter touching B regimes."""
    return float(stats.binom.cdf(k, B - 1, 0.5))


def second_column_floors(n: int) -> tuple[int, float]:
    """When the scope-Q branch is the primary every band uses one statistic, so the check binds at its loosest band: the
    switching side's lowest runs floor and the largest balance limit."""
    return min(band_interval(n, b)[0] for b in BANDS), max(band_b(n, b) for b in BANDS)


def residual_regimes(n: int, band: str) -> tuple[int, int] | None:
    """For a declared switching side: the regime lengths, from 64 sessions, a side constant over regimes of which can
    still reach the band's runs floor -- (64, the longest such) or None."""
    lo_r, _ = band_interval(n, band)
    longest = max((L for L in range(64, 2 * n) if max_runs(n, L) >= lo_r), default=None)
    return None if longest is None else (64, longest)


def beyond_pass(n: int, band: str, D: float) -> float:
    """At most this share of Markov sides of dwell D passes the band's switching-side check: its runs interval alone
    (the balance limit can only refuse more)."""
    lo_r, hi_r = band_interval(n, band)
    return 1.0 - markov_runs_out(n, float(D), lo_r, hi_r)


def dominated_side(n: int = 657, shorts: int = 8) -> tuple[int, float]:
    """The red team's F-1 side: long on every session but `shorts` evenly spaced one-session shorts: (R, |mean side|)."""
    return 2 * shorts + 1, (n - 2 * shorts) / n


def edge_reversal_side(regime: int = 219, regimes: int = 3) -> tuple[int, float]:
    """The red team's F-3 side: regimes of alternating sign, each with one one-session reversal at its second session:
    (R, |mean side|)."""
    s = []
    for k in range(regimes):
        sign = 1 if k % 2 == 0 else -1
        block = [sign] * regime
        block[1] = -sign
        s += block
    m = np.array(s)
    R = 1 + int((m[1:] != m[:-1]).sum())
    return R, abs(float(m.mean()))


def alternating_balance(n: int, L: int) -> np.ndarray:
    """|mean side| of each of the alternating model's 2L configurations on n sessions."""
    j = np.arange(n)
    return np.array([abs(np.where(((j + p) // L) % 2 == 0, 1.0, -1.0).mean()) for p in range(L)] * 2)


def admission_cost(n: int = 657) -> dict[str, float]:
    """The share of each class side model's sides that the added balance limit (b over 1..63) refuses on n sessions,
    every session non-tie: an upper bound on the share it removes from those 4.4 already admits."""
    b = admission_b(n)
    out = {f"flip{L}": exceeds(flip_balance(n, L), b) for L in (1, 5, 21, 42, 55, 63)}
    out.update({f"markov{D}": exceeds(markov_balance(n, float(D)), b) for D in (30, 50, 80)})
    for L in (45, 55):
        out[f"alt{L}"] = float((alternating_balance(n, L) > b + 1e-12).mean())
    return out


# ------------------------------------------------------------------------------------------- the Monte Carlo probe (M1)

#: at each size, the sizing subsets with the largest exact size (the plan's 3.2) carry the four persistent Monte Carlo
#: models at both values
PROBE_PER_SIZE = 23
PROBE_MODELS = ("flip21", "markov30", "markov50", "markov80")


def probe_nulls() -> int:
    return PROBE_PER_SIZE * len(SIZES) * len(PROBE_MODELS) * len(VALUES)


def probe_tail_refusal() -> float:
    """The probe's refusal of a candidate at the Monte Carlo tail rate the validation passes with GUARD_PASS, when the
    ranking finds the whole tail and it fits in the probed subsets: 1 - GUARD_PASS^(sizing subsets / validation
    subsets) (the red team's re-read, M-B)."""
    sizing = (CAL_SUBSETS_PER_SIZE - VAL_SUBSETS_PER_SIZE) * len(SIZES)
    return 1.0 - GUARD_PASS ** (sizing / n_val())


def probe_refusal(rho: float, m: int | None = None) -> float:
    """The probe's chance of refusing a candidate with m probed nulls at rho times nominal at every k: each null is
    refused exactly as the validation fails a null (E-052's failure counts)."""
    m = probe_nulls() if m is None else m
    return 1.0 - (1.0 - null_fail(rho)) ** m


# ------------------------------------------------------------------------------------------- the criterion's power


def failure_count(level: float, reps: int = REPS) -> int:
    """E-052's failure: the least count whose 95 % Clopper-Pearson lower limit lies above the level."""
    c = max(1, int(level * reps))
    while stats.beta.ppf(0.025, c, reps - c + 1) <= level:
        c += 1
    return c


FAIL = {k: failure_count(LEV[k]) for k in KS}


def p_holds(rates, fail=None, reps: int = REPS) -> float:
    """P(X_k < fail_k at every k) for X_13 ~ Bin(reps, rates[0]), X_{k+1} | X_k ~ Bin(X_k, rates[i+1] / rates[i])
    (Q-108's 4.2 computation, by dynamic programming over the counts)."""
    fail = FAIL if fail is None else fail
    f = [int(fail[k]) for k in KS]
    r = [float(x) for x in rates]
    if r[0] <= 0.0:
        return 1.0
    prob = stats.binom.pmf(np.arange(f[0]), reps, r[0])
    for i in range(1, len(f)):
        q = r[i] / r[i - 1] if r[i - 1] > 0 else 0.0
        x = np.arange(prob.size)
        y = np.arange(f[i])
        prob = stats.binom.pmf(y[:, None], x[None, :], q) @ prob
    return float(prob.sum())


def null_fail(rho: float) -> float:
    """One Monte Carlo null at rho times nominal at every k: the chance it breaks E-052's criterion somewhere."""
    return 1.0 - p_holds([rho * LEV[k] for k in KS])


def mc_pass(rho: float, nulls: int = MC_NULLS) -> float:
    return (1.0 - null_fail(rho)) ** nulls


def tolerated(rho: float, target: float = VAL_PASS) -> float:
    """How many Monte Carlo nulls at rho times nominal the criterion passes with probability target."""
    f = null_fail(rho)
    return math.inf if f <= 0 else math.log(target) / math.log(1.0 - f)


# ------------------------------------------------------------------------------------------- Q-108's files


def choice_p(repo: Path = ROOT) -> dict[tuple[str, str], float]:
    import pandas as pd
    d = pd.read_csv(repo / "results" / "q108_choice.csv")
    d = d[d["row"] == "candidate"]
    return {(str(r.candidate), str(r.scope)): float(r.P) for r in d.itertuples()}


def choice_p_mc(repo: Path = ROOT) -> dict[tuple[str, str], float]:
    import pandas as pd
    d = pd.read_csv(repo / "results" / "q108_choice.csv")
    d = d[d["row"] == "candidate"]
    return {(str(r.candidate), str(r.scope)): float(r.p_mc) for r in d.itertuples()}


def name_of(m: float) -> str:
    return "cons" if m == 1.0 else f"cons_m{m:g}"


def power_costs(repo: Path = ROOT) -> dict[str, tuple[str, float, float]]:
    """{candidate: (how, low, high)} -- P / P(cons_m1.25, Q). From the file where Q-108 measured the candidate
    ("file", low = high); bracketed by its grid neighbours' file values where it did not ("bracket": a margin's MDL is
    m crit se - est, increasing in m on every replication, so P is too)."""
    P = choice_p(repo)
    ref = P[REFERENCE]
    measured = {m: P[(name_of(m), "D")] / ref for m in GRID if (name_of(m), "D") in P}
    out = {}
    for m in GRID:
        if m in measured:
            out[name_of(m)] = ("file", measured[m], measured[m])
        else:
            lo = max(x for x in measured if x < m)
            hi = min(x for x in measured if x > m)
            out[name_of(m)] = ("bracket", measured[lo], measured[hi])
    out["cons_bm_m1.25"] = ("file", P[("cons_bm_m1.25", "D")] / ref, P[("cons_bm_m1.25", "D")] / ref)
    return out


def interpolated(repo: Path = ROOT) -> dict[str, float]:
    """The bracketed margins' cost by linear interpolation in m between the neighbours (an estimate, not a file
    value)."""
    P = choice_p(repo)
    ref = P[REFERENCE]
    pts = {m: P[(name_of(m), "D")] for m in GRID if (name_of(m), "D") in P}
    out = {}
    for m in GRID:
        if m not in pts:
            lo = max(x for x in pts if x < m)
            hi = min(x for x in pts if x > m)
            out[name_of(m)] = (pts[lo] + (pts[hi] - pts[lo]) * (m - lo) / (hi - lo)) / ref
    return out


def worst_flip42(cand: str, scope: str, repo: Path = ROOT) -> float:
    """`q108_choice.csv`'s `worst_ratio_flip42` for one candidate and scope (the plan's section 5, M3)."""
    import pandas as pd
    d = pd.read_csv(repo / "results" / "q108_choice.csv")
    d = d[(d["row"] == "candidate") & (d["candidate"] == cand) & (d["scope"] == scope)]
    return float(d["worst_ratio_flip42"].iloc[0])


def grid_p(repo: Path = ROOT) -> dict[str, float]:
    """Each grid margin's P / P(cons_m1.25): the file's value, or the linear interpolation where Q-108 did not run it."""
    pc, ip = power_costs(repo), interpolated(repo)
    return {name_of(m): (pc[name_of(m)][1] if pc[name_of(m)][0] == "file" else ip[name_of(m)]) for m in GRID}


def step_costs(repo: Path = ROOT) -> list[tuple[str, str, float]]:
    """The MDL cost of one grid step: P(next) / P(this) - 1, from `grid_p` (an estimate where a margin is
    interpolated)."""
    g = grid_p(repo)
    names = [name_of(m) for m in GRID]
    return [(a, b, g[b] / g[a] - 1.0) for a, b in zip(names, names[1:])]


def coverage(repo: Path = ROOT):
    """Scope D's admitted share under each side model: the mean of `admitted_share` over the in-rule fixed-data and
    subset nulls of `cons_m1.25` in scope D (the admission reads sides only, so every candidate's is the same), and
    its range over the five sizes."""
    import pandas as pd
    d = pd.read_csv(repo / "results" / "q108_cal_size.csv", low_memory=False)
    d = d[d["row"].isna() & (d["candidate"] == "cons_m1.25") & (d["scope"] == "D")
          & d["group"].isin(["fixed", "subset"])]
    d = d[d["in_rule"].astype(str) == "True"]
    mean = d.groupby("model")["admitted_share"].mean()
    by = d[d["group"] == "subset"].groupby(["model", "size"])["admitted_share"].mean().unstack()
    return mean, by.min(axis=1), by.max(axis=1)


def q108_val_mc_headroom(repo: Path = ROOT) -> tuple[float, str, int]:
    """In Q-108's validation, `cons_m1.25` scope Q: the largest Monte Carlo null's count as a share of E-052's
    failure count, over every k (its null and k)."""
    import pandas as pd
    d = pd.read_csv(repo / "results" / "q108_val_size.csv", low_memory=False)
    d = d[d["row"].isna() & (d["candidate"] == "cons_m1.25") & (d["scope"] == "Q") & (d["kind"] == "mc")
          & (d["in_rule"].astype(str) == "True")]
    best = (0.0, "", 0)
    for k in KS:
        share = d[f"count_k{k}"] / FAIL[k]
        i = share.idxmax()
        if share[i] > best[0]:
            best = (float(share[i]), str(d.loc[i, "null"]), k)
    return best


# ------------------------------------------------------------------------------------------- the cost

#: the plan's 3.3: the drift populations, each enumerated at every exact model
DRIFT_SCENARIOS = 8
DRIFT_POPULATIONS = 150
DRIFT_MODELS = EXACT_MODELS
RUNS = Path(os.environ.get("LOCALAPPDATA", "")) / "stage2-extended-runs"
CAL_LOG = RUNS / "q108-calibrate.log"
VAL_LOG = RUNS / "q108-validate.log"

EXACT_LINE = re.compile(r"\]   (?:fixed|sub):\S*:(flip42|flip55|flip63|alt45|alt55): .*; ([0-9.]+) s, ws ([0-9]+) MB")
MC_LINE = re.compile(r"\]   sub:\S*:(flip21|markov30|markov50|markov80): .*; ([0-9.]+) s, ws ([0-9]+) MB")
EXIT_LINE = re.compile(r"\] EXIT 0 \(([0-9]+) s\)")
PAIRS_PEAK = re.compile(r"peak working set ([0-9]+) MB")


def log_stats(path: Path) -> dict:
    """From a Q-108 run log: per exact model the median and mean seconds of one enumeration; the mean seconds of one
    persistent Monte Carlo subset null; the run's EXIT seconds; the largest per-null working set and the pairs step's
    peak (MB)."""
    ex: dict[str, list[float]] = {}
    mc: list[float] = []
    ws: list[int] = []
    out = {"exit_s": None, "pairs_peak_mb": None}
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        m = EXACT_LINE.search(line)
        if m:
            ex.setdefault(m.group(1), []).append(float(m.group(2)))
            ws.append(int(m.group(3)))
            continue
        m = MC_LINE.search(line)
        if m:
            mc.append(float(m.group(2)))
            ws.append(int(m.group(3)))
            continue
        m = EXIT_LINE.search(line)
        if m:
            out["exit_s"] = int(m.group(1))
        m = PAIRS_PEAK.search(line)
        if m:
            out["pairs_peak_mb"] = int(m.group(1))
    out["median"] = {k: float(np.median(v)) for k, v in ex.items()}
    out["mean"] = {k: float(np.mean(v)) for k, v in ex.items()}
    out["mc_mean"] = float(np.mean(mc)) if mc else None
    out["ws_max_mb"] = max(ws) if ws else None
    return out


def logs_present() -> bool:
    return CAL_LOG.is_file() and VAL_LOG.is_file()


def sizing_hours(per_subset_value_s: float, extra_subsets: int | None = None) -> float:
    extra = (CAL_SUBSETS_PER_SIZE - VAL_SUBSETS_PER_SIZE) * len(SIZES) if extra_subsets is None else extra_subsets
    return extra * len(VALUES) * per_subset_value_s / 3600.0


def per_subset_value(st: dict) -> float:
    """The mean seconds of one subset-value's five exact enumerations."""
    return sum(st["mean"][m] for m in EXACT_MODELS)


#: the candidates this plan computes (2.2), and the Q-108 logs' (the validation two, the calibration ten)
CANDIDATES_HERE = 8
CANDIDATES_LOGS = (2, 10)


def scaled(lo: float, hi: float, k: int = CANDIDATES_HERE) -> float:
    """A cost linear in the candidate count, through the validation log's (2) and the calibration log's (10)."""
    a, b = CANDIDATES_LOGS
    return lo + (hi - lo) * (k - a) / (b - a)


def scaled_cost(cal: dict, val: dict) -> dict[str, float]:
    """The run's hours at this plan's eight candidates, each part's two log figures scaled linearly (an estimate)."""
    c = cost(cal, val)
    out = {k: scaled(*v) for k, v in c.items() if k != "total"}
    out["total"] = sum(out.values())
    return out


def cost(cal: dict, val: dict) -> dict[str, tuple[float, float]]:
    """(low, high) hours of each part of the calibration run: low from the validation log (two candidates), high from
    the calibration log (ten); means throughout; the core from the two runs' EXIT seconds."""
    out = {
        "core": (val["exit_s"] / 3600.0, cal["exit_s"] / 3600.0),
        "sizing": (sizing_hours(per_subset_value(val)), sizing_hours(per_subset_value(cal))),
        "probe": (probe_nulls() * val["mc_mean"] / 3600.0, probe_nulls() * cal["mc_mean"] / 3600.0),
        "drift": (DRIFT_SCENARIOS * DRIFT_POPULATIONS * per_subset_value(val) / 3600.0,
                  DRIFT_SCENARIOS * DRIFT_POPULATIONS * per_subset_value(cal) / 3600.0),
    }
    out["total"] = (sum(v[0] for v in out.values()), sum(v[1] for v in out.values()))
    return out


# ------------------------------------------------------------------------------------------- print


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, default=ROOT)
    ap.add_argument("--cal-log", type=Path, default=None)
    ap.add_argument("--val-log", type=Path, default=None)
    a = ap.parse_args()

    n = n_val()
    N = CAL_SUBSETS_PER_SIZE * len(SIZES)
    rV = punished_rate(n)
    print("== 3.2 the sizing rule")
    print(f"validation exposure: {VAL_SUBSETS_PER_SIZE} x {len(SIZES)} = {n} subsets, each at {len(VALUES)} values x "
          f"{len(EXACT_MODELS)} exact models = {n * len(VALUES) * len(EXACT_MODELS)} exact subset nulls")
    print(f"punished rate r_V = 1 - {VAL_PASS}^(1/{n}) = {rV:.4e}")
    Nmin = min_cal_subsets(n)
    print(f"least calibration subsets: {Nmin} pooled ({math.ceil(Nmin / len(SIZES))} a size); declared "
          f"{CAL_SUBSETS_PER_SIZE} a size = {N}, of which {VAL_SUBSETS_PER_SIZE} a size carry the whole class")
    print(f"at {N}: P(see r_V) = {detection(N, rV):.4f}; rule-of-three bound 3/N = {3 / N:.4e}; validation passes at "
          f"that bound with {(1 - 3 / N) ** n:.4f}")
    aa = n / N
    print(f"a = n/N = {aa:.5f}; worst P(calibration holds, validation fails) one candidate {minimax_one(aa):.4f}; "
          f"a nested branch {minimax_nested(aa):.4f}; the rule (D's nested grid + C6 + Q's nested branch) "
          f"{2 * minimax_nested(aa) + minimax_one(aa):.4f}")
    print(f"exact enumerations: {N} x {len(VALUES)} x {len(EXACT_MODELS)} = {N * len(VALUES) * len(EXACT_MODELS)}; "
          f"at L = 42 alone {N * len(VALUES)}")
    print(f"Q-108's own design (a = 1): one candidate {minimax_one(1.0):.4f}, a nested branch "
          f"{minimax_nested(1.0):.4f}; "
          f"its 115 subsets saw r_V with {detection(n, rV):.4f}")
    for r in (1e-4, rV, 3 / N, 1e-3, 3 / n, 0.01):
        print(f"   bad-subset rate {r:.2e}: the validation's exact part passes with {(1 - r) ** n:.4f}; the "
              f"calibration sees one with {detection(N, r):.4f}")

    print("== 4.3 the criterion's power (E-052's, unchanged)")
    print("failure counts at 200,000:", FAIL)
    for rho in (0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
        print(f"   every MC null at {rho} x nominal: one null fails with {null_fail(rho):.3e}; all {MC_NULLS} pass "
              f"with "
              f"{mc_pass(rho):.4f}; nulls tolerated at {VAL_PASS}: {tolerated(rho):.0f}")
    pm = choice_p_mc(a.repo)
    for c in [("cons_m1.25", "Q"), ("cons_m1.25", "D"), ("cons_m1.5", "Q"), ("cons_bm_m1.25", "D")]:
        print(f"   Q-108's P_MC (q108_choice.csv p_mc) {c}: {pm[c]:.6f}")
    s, nm, k = q108_val_mc_headroom(a.repo)
    print(f"   Q-108's validation, cons_m1.25 Q: the largest MC count is {s:.3f} of its failure count ({nm}, k = {k})")

    print("== 5 the power costs against cons_m1.25 (q108_choice.csv P)")
    P = choice_p(a.repo)
    print(f"   P(cons_m1.25, Q) = {P[REFERENCE]:.5f}; P(cons_m1.25, D) = {P[('cons_m1.25', 'D')]:.5f}")
    ip = interpolated(a.repo)
    for c, (how, lo, hi) in power_costs(a.repo).items():
        extra = f"; linear interpolation {ip[c]:.3f}" if c in ip else ""
        print(f"   {c}: {how} {lo:.3f}" + (f" to {hi:.3f}" if hi != lo else "") + extra)

    print(f"   Q-108's worst flip-42 ratio, cons_m1.5 in scope Q: {worst_flip42('cons_m1.5', 'Q', a.repo):.3f}")

    print("== 7 scope D's coverage (q108_cal_size.csv admitted_share, cons_m1.25 D, in-rule fixed and subset nulls)")
    mean, lo, hi = coverage(a.repo)
    for m in mean.index:
        print(f"   {m}: mean {mean[m]:.3f}; over sizes {lo.get(m, float('nan')):.3f} to {hi.get(m, float('nan')):.3f}")

    print(f"== 3.2 / 4.3 the floor: declared c = {ALLOWANCE} (E-176); E-173's allowance beside")
    N = CAL_SUBSETS_PER_SIZE * len(SIZES)
    r95 = guard_rate(n)
    c = allowance(N, n)
    print(f"r_95 = 1 - {GUARD_PASS}^(1/{n}) = {r95:.4e}; E-173's least allowance c = {c} (recorded {E173_ALLOWANCE}); "
          f"it refuses at r_95 with {1 - floor_admits(r95, N, c):.4f} (at c - 1: {1 - floor_admits(r95, N, c - 1):.4f})")
    print("   c | refuses at r_95 | refuses at r_V | one | nested | primary | second | rule")
    for cc in COMPARED:
        bb = rule_bounds(N, n, cc)
        print(f"   {cc} | {1 - floor_admits(r95, N, cc):.4f} | {1 - floor_admits(rV, N, cc):.4f} | {bb['one']:.4f} | "
              f"{bb['nested']:.4f} | {bb['primary']:.4f} | {bb['second']:.4f} | {bb['all']:.4f}")
    print(f"at c = {c}: r_V refused with {1 - floor_admits(rV, N, c):.4f}; the 95 % upper limit after {c} bad of {N}: "
          f"{cp_upper(c, N):.4e}, at which the validation's exact part passes with {(1 - cp_upper(c, N)) ** n:.4f}")
    print(f"   per size: 0 bad of {CAL_SUBSETS_PER_SIZE} bound that size at {cp_upper(0, CAL_SUBSETS_PER_SIZE):.4e}; "
          f"{c} bad of {CAL_SUBSETS_PER_SIZE} at {cp_upper(c, CAL_SUBSETS_PER_SIZE):.4e}")
    b = rule_bounds(N, n, c)
    print(f"bounds at c = {c}: one candidate {b['one']:.4f}; a nested branch {b['nested']:.4f}; the primary "
          f"{b['primary']:.4f}; the second statistic {b['second']:.4f}; the whole rule {b['all']:.4f}")
    b0 = rule_bounds(N, n, 0)
    print(f"   (at c = 0: {b0['one']:.4f}, {b0['nested']:.4f}, {b0['primary']:.4f}, {b0['second']:.4f}, {b0['all']:.4f})")
    for NN, cc, bb in bound_by_subsets(n=n):
        print(f"   beside, not taken: {NN} subsets, allowance {cc}, nested bound {bb:.4f} (its limit {1 - GUARD_PASS:.2f})")
    for r in (*FLOOR_RATES[:4], r95, rV, *FLOOR_RATES[4:]):
        print(f"   rate {r:.4e}: floor admits (c = {c}) {floor_admits(r, N, c):.4f}; (c = 0) {floor_admits(r, N, 0):.4f}; "
              f"the validation's exact part passes {(1 - r) ** n:.4f}")
    print("   grid steps:", [(x, y, round(z, 3)) for x, y, z in step_costs(a.repo)])
    print(f"   the first text's floor (c = 0) refused at 1e-04 with {1 - floor_admits(1e-4, N, 0):.4f} and at r_95 with "
          f"{1 - floor_admits(r95, N, 0):.4f}; the validation's {n} subsets catch a rate of 1e-03 with "
          f"{1 - (1 - 1e-3) ** n:.4f}")

    print("== 3.2 / 4.3 the floor's readings (the re-read's M-C)")
    cal0, val0 = certificates(N, n)
    print(f"   95 % upper limit after zero bad: calibration's {N} subsets {cal0:.4e}; the validation's {n} {val0:.4e}")
    for k, prof in PROFILES.items():
        for cc in (0, E173_ALLOWANCE):
            pr = profile_reading(prof, cc)
            print(f"   profile {k}, c = {cc}: validation fails {pr['val_fail']:.4f}; NONE {pr['none']:.4f}; mean P of a "
                  f"held choice {pr['mean_p']:.3f}")
    for r in FLAT_RATES:
        print(f"   flat rate {r:.0e}: the floor empties the branch with {flat_none(r):.4f}; the validation passes "
              f"{(1 - r) ** n:.4f}")
    print("== 2.5 the band check (M-D; the last read's F-1 to F-3)")
    for nn in (657, 1006):
        for bd in BANDS:
            lo_r, hi_r, fl = runs_interval(nn, bd)
            ib = in_band_refusals(nn, bd)
            print(f"   n = {nn}, {bd}: b = {band_b(nn, bd):.4f}; switching-side runs [{lo_r}, {hi_r}], two-quarters floor {fl}; "
                  f"worst in-band refusal: regime {ib['regime']:.4f} (L = "
                  f"{ib['regime_at']}), switching {ib['switching']:.4f} (D = {ib['switching_at']}); edges "
                  + ", ".join(f"{k} {v:.4f}" for k, v in ib.items() if k[:4] in ("flip", "mark"))
                  + f"; residual regimes {residual_regimes(nn, bd)}")
        print(f"   n = {nn}: admission b = {admission_b(nn):.4f}")
    print("   Markov beyond the class (at most this share passes):")
    for D in BEYOND_DWELLS:
        print(f"      dwell {D}: 42 to 50 at 657 {beyond_pass(657, '42 to 50', D):.3f}; 51 to 62 at 657 "
              f"{beyond_pass(657, '51 to 62', D):.3f}; 51 to 62 at 1006 {beyond_pass(1006, '51 to 62', D):.3f}")
    R_, M_ = dominated_side()
    print(f"   the dominated side (8 one-session shorts on 657): R = {R_}, |mean side| = {M_:.4f}")
    print("   the regime filter's runs floor by B (floor, miss):", {B: (f, round(m, 4)) for B, (f, m) in regime_floors().items()})
    for nn in (657, 1006):
        print(f"   n = {nn}: regimes touched by band", {b: regime_blocks(nn, b) for b in BANDS})
    for name, (sd, pts) in gamed_sides().items():
        print(f"   {name}: {regime_filter_check(sd, pts, '42 to 50')}")
    print(f"   the edge-reversal side as a regime filter: {edge_reversal_filter_check()}")
    print(f"   the class's tail: P(at most 4 changes | B = 16) = {class_tail(16, 4):.4f}; P(at most 2 | B = 12) = "
          f"{class_tail(12, 2):.4f}")
    for nn in (657, 1006):
        f2, b2 = second_column_floors(nn)
        print(f"   second column at {nn}: switching R >= {f2}; balance at most {b2:.4f}")
    R2, M2 = edge_reversal_side()
    print(f"   the edge-reversal side (three regimes of 219, one reversal each): R = {R2}, |mean side| = {M2:.4f}")
    print(f"   runs: Markov dwell 50 about {dwell_runs(50):.1f}; flip-42 {flip_mean_runs(657, 42):.1f}; flip-55 "
          f"{flip_mean_runs(657, 55):.1f}; blocks at 42 {sorted(set(len(w) for w in flip_counts(657, 42)))}, at 55 "
          f"{sorted(set(len(w) for w in flip_counts(657, 55)))}")
    print("   the admission's balance limit removes, at 657:", {k: round(v, 4) for k, v in admission_cost().items()})
    print("== 4.2 / 4.3 the Monte Carlo probe (M1)")
    m = probe_nulls()
    print(f"probed nulls: {PROBE_PER_SIZE} x {len(SIZES)} x {len(PROBE_MODELS)} x {len(VALUES)} = {m}")
    sz = (CAL_SUBSETS_PER_SIZE - VAL_SUBSETS_PER_SIZE) * len(SIZES)
    print(f"   at the tail rate the validation passes with {GUARD_PASS}, the probe refuses with up to "
          f"1 - {GUARD_PASS}^({sz}/{n_val()}) = {probe_tail_refusal():.3f}")
    for rho in (0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
        print(f"   rho {rho}: one probed null refused {null_fail(rho):.3e}; all {m} at rho {probe_refusal(rho):.4f}; "
              f"the validation's {MC_NULLS} all at rho pass {mc_pass(rho):.4f}")

    print("== 6.2 the cost")
    cal_p = a.cal_log or CAL_LOG
    val_p = a.val_log or VAL_LOG
    if Path(cal_p).is_file() and Path(val_p).is_file():
        cs, vs = log_stats(Path(cal_p)), log_stats(Path(val_p))
        for name, st in (("calibration", cs), ("validation", vs)):
            print(f"   Q-108's {name} log: median s an enumeration {st['median']}; mean {st['mean']}; a subset-value "
                  f"(means) {per_subset_value(st):.2f} s; a persistent MC subset null {st['mc_mean']:.2f} s; EXIT "
                  f"{st['exit_s']} s; per-null working set at most {st['ws_max_mb']} MB; pairs step peak "
                  f"{st['pairs_peak_mb']} MB")
        sc = scaled_cost(cs, vs)
        for part, (lo, hi) in cost(cs, vs).items():
            print(f"   {part}: {lo:.1f} to {hi:.1f} h; at {CANDIDATES_HERE} candidates {sc[part]:.1f} h")
    else:
        print("   the logs are not present: no cost line")


if __name__ == "__main__":
    main()
