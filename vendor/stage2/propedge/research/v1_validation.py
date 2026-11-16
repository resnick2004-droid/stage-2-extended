"""D-663 (V1): three validation checks the protocol lacked, on the two best results -- the pure parts. EXPLORATORY, read
beside the registered verdicts; changes no verdict, selects nothing, creates no candidate.

**Subjects.** S1 = P-16's registered development gate (`rc_s150_all_nr`; `results/rc_s150_all_gate.csv`: the verdict arm
`gate_at_ledger_n` at one-sided 0.05/414 and the point arm of `gate`). S2 = FV3-C's confirmation P-06
(`results/fv3_confirmation.csv`: the gate's bound arm and point arm, the placement off, 0 % denial).

**What the gates do, and what was never checked** (the inventory behind D-663): both gates give each calendar day of a
path one historical day drawn independently with replacement (`shared_days.SharedDayTable`), so a path keeps nothing of
the order of history's days; the bound of e is a one-sided Student-t bound on 21-session block means, never calibrated
on these data at 0.05/N; neither result carries a missed-trade stress and FV3-C none for slippage.

**Part A, day dependence.** A0 measures it (`acf`, `ljung_box`, `runs_test`, `politis_white`) on each subject's day
series: (i) the day's summed net R over all offered trades at the fresh Combine's R, (ii) its absolute value, (iii) its
sign. A1 reruns each gate with the path's calendar from the stationary bootstrap of days (Politis and Romano, 1994:
`shared_days.StationaryDayTable`, the engine's one optional keyword `mean_block`) at mean blocks `MEAN_BLOCKS`; mean block
1 is the control (the independent draw's law on another random stream: it agrees with the registered row within
Monte-Carlo error and is not an identity). A2 asks which mean block history supports: the real-order replay from every
`A2_STEP`-th session over `A2_HORIZON` sessions against each scheme's resampled paths through the same replay-form
engine call (`exceed_shares`); overlapping starts are dependent, so those shares carry no interval.

**Part B, calibration.** B1 (`coverage`): histories of the subject's own length resampled by the stationary bootstrap at
`B1_BLOCKS` and at A0's automatic length, the registered bound recomputed on each (`block_bounds`, `era_rule_bounds`: the
registered functions' arithmetic on per-day sums, checked against the registered functions themselves on the sample and
on `B1_VERIFY` materialised replicates per run), the share of replicates whose bound exceeds the truth -- the resampling
population's pooled mean, which is the sample's -- with an exact binomial interval. B2 (`break_even`): the verdict arm's
outcomes shifted below the registered bound in steps of `B2_STEP` R, the table frozen, to where growth on the required
bankroll turns. B3 (`familywise`): a family's cells centred to mean zero, days resampled jointly, the family's own
selection rule and bound applied.

**Part C, execution stress.** C1 (`drop_trades`, `miss_sessions`): offered trades dropped independently, and whole
sessions missed, in `C1_REALISATIONS` seeded realisations over the history an arm (`c1_seed`), each reported and their
mean and range beside (`realisation_summary`). C2 (`stress_by_kind`): D-583's slippage families on FV3-C's
trades by each R's exit kind, in ticks over the trade's own stop.

**Readings of one engine run** (`path_readings`, beside the gate row's own columns): the share of paths ending below the
start, the longest payout drought's 90th percentile, the payouts per path (median) and the 10th percentile of net cash.
"""
from __future__ import annotations

import hashlib
import math
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

DECISION = "D-663"
RESULT = "v1_validation"
#: the declaration: DECISIONS.md's D-663 row (LF, the line itself) -- its sha256, and the phrases each constant rests on
DECLARATION_SHA256 = "133ce5031afae834c3469b6d55fcfaebe501e801587ff0811f497fba4d54d2ea"
SUBJECTS = ("S1", "S2")
PARTS = ("A1", "B2", "A0", "B1", "A2", "C1", "C2", "B3")       # the declared run's order: the decisive rows first
N_PATHS = 500
LEDGER_N = {"S1": 414, "S2": 183}
ALPHA = 0.05
# Part A
ACF_LAGS = 21
LB_LAGS = (5, 10, 21)
MEAN_BLOCKS = (1, 5, 21, 63)
A2_HORIZON = 252
A2_STEP = 21
A2_PATHS = 500
# Part B
B1_BLOCKS = (1, 5, 21)
B1_REPS = 200_000
B1_VERIFY = 5
B2_STEP = 0.02
B2_MAX_STEPS = 8
B2_MEAN_BLOCK = 21
B3_REPS = 20_000
B3_MEAN_BLOCK = 21
# Part C
C1_ARMS = (("drop10", "trade", 0.10), ("drop25", "trade", 0.25), ("session10", "session", 0.10))
C1_REALISATIONS = 3                        # seeded realisations a C1 arm (`c1_seed`), each reported, with mean and range
KINDS = ("s", "t", "f", "b")               # stop, target, flatten, breakeven (D-583's codes)
#: fresh seeds, each used by this study alone (a test checks no other file holds them): A2's resampled paths, B1's and
#: B3's bootstraps, C1's realisations. A1, B2, C1 and C2 run at each subject's registered campaign seed (imported).
SEED_A2 = 20262101
SEED_B1 = 20262102
SEED_B3 = 20262103
SEED_C1 = 20262104
READING = ("EXPLORATORY (D-663): block-resampled days, the bound's calibration and execution stress on P-16's and "
           "FV3-C's registered gates; beside the registered verdicts, changes none, selects nothing")
#: the phrases of the declaration row each constant rests on
WORDS = ("mean block 1, 5, 21 and 63 sessions",
         "500 paths, the registered horizon and the registered campaign seed",
         "lags 1 to 21", "Ljung-Box at lags 5, 10 and 21",
         "a 252-session horizon from every 21st session",
         "200,000 replicates", "0.05 and 0.05/N (N 414 for S1, 183 for S2)",
         "steps of 0.02 R, at most 8",
         "20,000 replicates",
         "p = 0.10 and p = 0.25", "whole sessions missed with p = 0.10", "3 seeded realisations each",
         "`lockstep.child_seed(20262104, 3 x subject + arm, realisation)`",
         "measured under the empirical law with the days' dependence kept",
         "the exact interval is reported", "the margin is read for the table as frozen",
         "stop slip 2, 3, 5, 8, 12 ticks", "entry = stop slip 2, 3, 5",
         "`propedge/campaign/shared_days.py`", "`propedge/campaign/gate.py`", "off by default",
         "seeds 20262101 (A2), 20262102 (B1), 20262103 (B3), 20262104 (C1, its 3 realisations",
         "nothing is searched")


# ------------------------------------------------------------------------------------------------ the declaration


def declaration(root: Path | None = None) -> dict[str, Any]:
    """DECISIONS.md's D-663 row (LF line ends, the line itself) and its sha256 (`root`: the repository, by default
    this file's)."""
    base = Path(root) if root is not None else Path(__file__).resolve().parents[2]
    p = base / "DECISIONS.md"
    text = p.read_bytes().replace(b"\r\n", b"\n").decode("utf-8") if p.is_file() else ""
    rows = [line for line in text.split("\n") if line.startswith(f"| {DECISION} |")]
    row = rows[0] if len(rows) == 1 else ""
    return {"path": str(p), "rows": len(rows), "row": row, "sha256": hashlib.sha256(row.encode("utf-8")).hexdigest()}


def declaration_problems(decl: Mapping[str, Any], *, declared: bool) -> list[str]:
    """Every way this module's constants differ from the D-663 row: one row, its sha256 the pinned one (for every run,
    `--check` included: `declared` is kept for the callers and changes nothing now that the row is committed), every
    phrase of `WORDS` in it."""
    out = []
    if int(decl["rows"]) != 1:
        out.append(f"{Path(str(decl['path'])).name} holds {decl['rows']} {DECISION} rows, not one")
    if str(decl["sha256"]) != DECLARATION_SHA256:
        out.append(f"the {DECISION} row's sha256 is {str(decl['sha256'])[:16]}, not the pinned {DECLARATION_SHA256[:16]}")
    row = re.sub(r"\s+", " ", str(decl["row"]))
    out += [f"the declaration does not say {w!r}" for w in WORDS if w not in row]
    return out


# ------------------------------------------------------------------------------------------------ A0: dependence


def acf(x: Sequence[float], nlags: int) -> np.ndarray:
    """The sample autocorrelations at lags 1..nlags (the biased estimator: every lag over n and the lag-0 variance)."""
    v = np.asarray(x, dtype=float)
    v = v - v.mean()
    c0 = float(v @ v)
    if not c0 > 0:
        return np.full(int(nlags), np.nan)
    return np.array([float(v[k:] @ v[:-k]) / c0 for k in range(1, int(nlags) + 1)])


def ljung_box(x: Sequence[float], lags: Sequence[int]) -> dict[int, tuple[float, float]]:
    """{h: (Q, p)}: Ljung and Box's Q = n (n + 2) sum_{k <= h} rho_k^2 / (n - k), p from chi-square with h degrees."""
    from scipy import stats

    n = len(x)
    rho = acf(x, max(int(h) for h in lags))
    out = {}
    for h in lags:
        k = np.arange(1, int(h) + 1)
        q = float(n * (n + 2) * np.sum(rho[: int(h)] ** 2 / (n - k)))
        out[int(h)] = (q, float(stats.chi2.sf(q, int(h))) if np.isfinite(q) else float("nan"))
    return out


def runs_test(x: Sequence[float]) -> dict[str, float]:
    """Wald and Wolfowitz's runs test on the sign of `x` (zeros dropped, counted in `zeros`): the runs, their expected
    count and the two-sided normal p. Fewer runs than expected (z < 0) is clustering."""
    from scipy import stats

    s = np.sign(np.asarray(x, dtype=float))
    zeros = int((s == 0).sum())
    s = s[s != 0]
    n1, n2 = int((s > 0).sum()), int((s < 0).sum())
    n = n1 + n2
    if n1 == 0 or n2 == 0 or n < 3:
        return {"n": n, "zeros": zeros, "positive": n1, "negative": n2, "runs": float("nan"),
                "expected": float("nan"), "z": float("nan"), "p": float("nan")}
    runs = 1 + int((s[1:] != s[:-1]).sum())
    mu = 2.0 * n1 * n2 / n + 1.0
    var = 2.0 * n1 * n2 * (2.0 * n1 * n2 - n) / (n * n * (n - 1.0))
    z = (runs - mu) / math.sqrt(var) if var > 0 else float("nan")
    return {"n": n, "zeros": zeros, "positive": n1, "negative": n2, "runs": float(runs), "expected": float(mu),
            "z": float(z), "p": float(2.0 * stats.norm.sf(abs(z))) if np.isfinite(z) else float("nan")}


def _pw(acv: np.ndarray, n: int) -> dict[str, float]:
    """Politis and White's (2004) automatic block length with Patton, Politis and White's (2009) correction, from the
    autocovariances at lags 0..m_max of a series of length `n`: m-hat the smallest m with the K_N autocorrelations after
    it all inside 2 sqrt(log10 n / n) (K_N = max(5, ceil(sqrt(log10 n)))), M = 2 max(m-hat, 1) capped at m_max, the
    flat-top kernel (1 to M / 2, then linear to 0 at M), G = sum |k| lambda R(k), g = sum lambda R(k),
    b_SB = (2 G^2 / (2 g^2))^(1/3) n^(1/3) for the stationary bootstrap and b_CB = (2 G^2 / (4 g^2 / 3))^(1/3) n^(1/3)
    for the circular one, each at most ceil(min(3 sqrt n, n / 3))."""
    m_max = len(acv) - 1
    kn = max(5, int(math.ceil(math.sqrt(math.log10(n)))))
    cv = 2.0 * math.sqrt(math.log10(n) / n)
    rho = np.abs(acv[1:] / acv[0])                         # rho[k - 1] is lag k
    m_hat = None
    for m in range(0, m_max - kn + 1):
        if np.all(rho[m: m + kn] < cv):                    # lags m + 1 .. m + K_N
            m_hat = m
            break
    big = max(2 * max(m_hat, 1), 2) if m_hat is not None else m_max
    big = min(big, m_max)
    k = np.arange(1, big + 1)
    lam = np.where(k / big <= 0.5, 1.0, 2.0 * (1.0 - k / big))
    g_hat = float(2.0 * np.sum(lam * k * acv[1: big + 1]))
    lr = float(acv[0] + 2.0 * np.sum(lam * acv[1: big + 1]))
    b_max = math.ceil(min(3.0 * math.sqrt(n), n / 3.0))
    if not lr > 0:
        return {"b_sb": float("nan"), "b_cb": float("nan"), "m_hat": float(m_hat if m_hat is not None else m_max),
                "M": float(big), "b_max": float(b_max)}
    b_sb = (2.0 * g_hat ** 2 / (2.0 * lr ** 2)) ** (1.0 / 3.0) * n ** (1.0 / 3.0)
    b_cb = (2.0 * g_hat ** 2 / (4.0 / 3.0 * lr ** 2)) ** (1.0 / 3.0) * n ** (1.0 / 3.0)
    return {"b_sb": float(min(b_sb, b_max)), "b_cb": float(min(b_cb, b_max)),
            "m_hat": float(m_hat if m_hat is not None else m_max), "M": float(big), "b_max": float(b_max)}


def politis_white(x: Sequence[float]) -> dict[str, float]:
    """`_pw` on the sample autocovariances of `x` at lags 0..ceil(sqrt n) + K_N."""
    v = np.asarray(x, dtype=float)
    n = len(v)
    if n < 20 or not np.var(v) > 0:
        return {"b_sb": float("nan"), "b_cb": float("nan"), "m_hat": float("nan"), "M": float("nan"),
                "b_max": float("nan")}
    v = v - v.mean()
    kn = max(5, int(math.ceil(math.sqrt(math.log10(n)))))
    m_max = min(int(math.ceil(math.sqrt(n))) + kn, n - 1)
    acv = np.array([float(v[k:] @ v[: n - k]) / n for k in range(m_max + 1)])
    return _pw(acv, n)


def auto_block(b_sb: float) -> int:
    """A0's automatic mean block as B1 uses it: `b_sb` rounded up, at least one session."""
    return max(1, int(math.ceil(float(b_sb)))) if np.isfinite(b_sb) else 1


def dependence_rows(series: Mapping[str, Sequence[float]]) -> list[dict[str, Any]]:
    """A0's rows for one subject: per series its autocorrelations at lags 1..ACF_LAGS, Ljung and Box at LB_LAGS, and (for
    every series but the sign) the automatic block lengths; the runs test on the series named `sign`."""
    out: list[dict[str, Any]] = []
    for name, x in series.items():
        v = np.asarray(x, dtype=float)
        rho = acf(v, ACF_LAGS)
        lb = ljung_box(v, LB_LAGS)
        row: dict[str, Any] = {"section": "a0", "series": name, "n": int(len(v)),
                               "white_noise_band": 1.96 / math.sqrt(len(v)),
                               **{f"acf_{k}": float(rho[k - 1]) for k in range(1, ACF_LAGS + 1)},
                               **{f"ljung_box_q_{h}": lb[h][0] for h in LB_LAGS},
                               **{f"ljung_box_p_{h}": lb[h][1] for h in LB_LAGS}}
        if name == "sign":
            row.update({f"runs_{k}": v2 for k, v2 in runs_test(v).items()})
        else:
            pw = politis_white(v)
            row.update({"pw_b_sb": pw["b_sb"], "pw_b_cb": pw["b_cb"], "pw_m_hat": pw["m_hat"], "pw_M": pw["M"],
                        "pw_b_max": pw["b_max"], "auto_block": auto_block(pw["b_sb"])})
        out.append(row)
    return out


def day_sums(t: pd.DataFrame, days: Sequence[str], keys: Sequence[float]) -> tuple[np.ndarray, np.ndarray]:
    """(sums, counts), each days x R: every day's summed net outcome at each R over its offered trades (a NaN outcome is
    not offered) and how many there were; a day without trades is a row of zeros."""
    pos = {str(d): i for i, d in enumerate(days)}
    ix = t["date"].astype(str).map(pos)
    if ix.isna().any():
        raise ValueError("a trade on a day outside the day set")
    ix = ix.to_numpy(int)
    sums = np.zeros((len(days), len(keys)))
    cnts = np.zeros((len(days), len(keys)))
    for j, R in enumerate(keys):
        r = t[f"r_{float(R):g}"].to_numpy(float)
        ok = np.isfinite(r)
        sums[:, j] = np.bincount(ix[ok], weights=r[ok], minlength=len(days))
        cnts[:, j] = np.bincount(ix[ok], minlength=len(days))
    return sums, cnts


# ------------------------------------------------------------------------------------------------ resampling


def stationary_indices(n: int, mean_block: float, reps: int, rng: np.random.Generator) -> np.ndarray:
    """`reps` stationary-bootstrap resamples of 0..n-1, each of length n (reps x n): position 0 starts a block at a
    uniform index; each later position restarts with probability 1 / mean_block, else takes the next index, n - 1
    followed by 0. The law of `shared_days.StationaryDayTable`'s calendar (not its random stream)."""
    mb = float(mean_block)
    if not mb >= 1.0:
        raise ValueError(f"the mean block is at least one, got {mean_block!r}")
    p = 0.0 if math.isinf(mb) else 1.0 / mb
    restart = rng.random((int(reps), int(n))) < p
    restart[:, 0] = True
    start = rng.integers(0, int(n), size=(int(reps), int(n)))
    pos = np.arange(int(n))
    last = np.maximum.accumulate(np.where(restart, pos, 0), axis=1)
    return (np.take_along_axis(start, last, axis=1) + pos - last) % int(n)


def _t_quantiles(alpha: float, max_n: int) -> np.ndarray:
    """q[k] = the one-sided (1 - alpha) Student-t quantile at k - 1 degrees of freedom, k = 2..max_n (NaN below)."""
    from scipy import stats

    q = np.full(max_n + 1, np.nan)
    k = np.arange(2, max_n + 1)
    q[2:] = stats.t.ppf(1.0 - float(alpha), k - 1)
    return q


def block_bounds(sums: np.ndarray, cnts: np.ndarray, idx: np.ndarray, block_days: int, alphas: Sequence[float]
                 ) -> dict[str, np.ndarray]:
    """`confirm_fv3.edge_stats`' arithmetic on per-day sums, for many histories at once. `idx` (reps x n) names the day
    at each position of each history; position i belongs to block i // block_days; a block's mean is its offered trades'
    mean; the bound is the one-sided Student-t bound of the mean of the blocks that hold a trade (`bound_at`: NaN with
    fewer than two). Returns `e` (reps x R: the pooled mean over trades), `lb` (alphas x reps x R), `blocks`,
    `sum`, `count` (reps x R)."""
    edges = np.arange(0, idx.shape[1], int(block_days))
    s = np.add.reduceat(sums[idx], edges, axis=1)          # reps x blocks x R
    c = np.add.reduceat(cnts[idx], edges, axis=1)
    has = c > 0
    m = np.where(has, s / np.where(has, c, 1.0), 0.0)
    nb = has.sum(axis=1)
    mu = m.sum(axis=1) / np.maximum(nb, 1)
    var = np.where(has, (m - mu[:, None, :]) ** 2, 0.0).sum(axis=1) / np.maximum(nb - 1, 1)
    se = np.sqrt(var / np.maximum(nb, 1))
    tot_s, tot_c = s.sum(axis=1), c.sum(axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        e = np.where(tot_c > 0, tot_s / np.where(tot_c > 0, tot_c, 1.0), np.nan)
    lb = np.empty((len(alphas),) + mu.shape)
    for a, alpha in enumerate(alphas):
        q = _t_quantiles(alpha, int(max(nb.max(), 2)))
        lb[a] = np.where(nb >= 2, mu - q[np.maximum(nb, 2)] * se, np.nan)
    return {"e": e, "lb": lb, "blocks": nb, "sum": tot_s, "count": tot_c}


def era_rule_bounds(sums: np.ndarray, cnts: np.ndarray, idx_by_era: Sequence[np.ndarray], block_days: int,
                    alphas: Sequence[float]) -> dict[str, np.ndarray]:
    """The era rule's bound as `t24_gf15.eras` reads it when the eras are flagged: each era's own bound over its own
    21-session blocks (`block_bounds` on that era's positions), the lower one read. `idx_by_era`: each era's (reps x its
    length) day indices. Returns `e` (the pooled mean over both eras' trades), `lb` (alphas x reps x R: the lower
    era's), `e_low` (the lower of the eras' own pooled means)."""
    parts = [block_bounds(sums, cnts, ix, block_days, alphas) for ix in idx_by_era]
    tot_s = sum(p["sum"] for p in parts)
    tot_c = sum(p["count"] for p in parts)
    with np.errstate(invalid="ignore", divide="ignore"):
        e = np.where(tot_c > 0, tot_s / np.where(tot_c > 0, tot_c, 1.0), np.nan)
    lb = parts[0]["lb"]
    e_low = parts[0]["e"]
    for p in parts[1:]:
        lb = np.minimum(lb, p["lb"])
        e_low = np.minimum(e_low, p["e"])
    return {"e": e, "lb": lb, "e_low": e_low}


def binomial_interval(k: int, n: int, level: float = 0.95) -> tuple[float, float]:
    """Clopper and Pearson's exact two-sided interval of a proportion k / n."""
    from scipy import stats

    a = (1.0 - float(level)) / 2.0
    lo = 0.0 if k == 0 else float(stats.beta.ppf(a, k, n - k + 1))
    hi = 1.0 if k == n else float(stats.beta.ppf(1.0 - a, k + 1, n - k))
    return lo, hi


def coverage_counts(exceed: int, defined: int, undefined: int, alpha: float) -> dict[str, Any]:
    """B1's reading from its counts: of `defined` replicates whose bound is a number, `exceed` had the bound above the
    truth (the bound failed); the share, its exact binomial interval, and whether the nominal level lies inside it."""
    n, k = int(defined), int(exceed)
    lo, hi = binomial_interval(k, n) if n else (float("nan"), float("nan"))
    return {"replicates": n, "undefined": int(undefined), "exceed": k, "nominal": float(alpha),
            "share_exceed": (k / n if n else float("nan")), "share_lo": lo, "share_hi": hi,
            "ratio_to_nominal": (k / n / float(alpha) if n else float("nan")),
            "nominal_inside_interval": bool(n and lo <= float(alpha) <= hi)}


def coverage(lb: np.ndarray, truth: float, alpha: float) -> dict[str, Any]:
    """`coverage_counts` of one bound's replicates against the truth."""
    v = np.asarray(lb, dtype=float)
    ok = np.isfinite(v)
    return coverage_counts(int((v[ok] > float(truth)).sum()), int(ok.sum()), int((~ok).sum()), alpha)


# ------------------------------------------------------------------------------------------------ B2: break-even


def break_even(curve: Sequence[tuple[float, float]]) -> dict[str, Any]:
    """B2's reading from the curve [(shift below the registered bound in R, at most 0; growth on the required bankroll)]
    in the order run (0, -step, ...): the first step whose growth is at or below zero (a growth that is not a number
    counts as below), the break-even shift by linear interpolation between it and the step before, and the margin (the
    registered bound less the break-even e = minus that shift). `bracketed` False: growth never turned inside the
    declared steps (the margin is then more than the last step, `margin_at_least`), or was already at or below zero at
    the registered bound (margin 0); no extrapolation."""
    pts = [(float(s), float(g)) for s, g in curve]
    if not pts or pts[0][0] != 0.0:
        raise ValueError("the curve starts at the registered bound (shift 0)")
    turned = next((i for i, (_, g) in enumerate(pts) if not (np.isfinite(g) and g > 0)), None)
    if turned is None:
        return {"bracketed": False, "break_even_shift": float("nan"), "margin": float("nan"),
                "margin_at_least": -pts[-1][0], "steps_run": len(pts), "first_step_at_or_below_zero": float("nan")}
    if turned == 0:
        return {"bracketed": False, "break_even_shift": 0.0, "margin": 0.0, "margin_at_least": 0.0,
                "steps_run": len(pts), "first_step_at_or_below_zero": 0.0}
    (s0, g0), (s1, g1) = pts[turned - 1], pts[turned]
    star = s0 + (s1 - s0) * (g0 / (g0 - g1)) if np.isfinite(g1) else s1
    return {"bracketed": True, "break_even_shift": float(star), "margin": float(-star),
            "margin_at_least": float(-s0), "steps_run": len(pts), "first_step_at_or_below_zero": float(s1),
            "interpolated": bool(np.isfinite(g1))}


# ------------------------------------------------------------------------------------------------ C1, C2


def drop_trades(t: pd.DataFrame, p: float, rng: np.random.Generator) -> pd.DataFrame:
    """C1: every offered trade dropped independently with probability `p` (one seeded realisation); the rest unchanged,
    in their order."""
    keep = rng.random(len(t)) >= float(p)
    return t[keep].reset_index(drop=True)


def miss_sessions(t: pd.DataFrame, days: Sequence[str], p: float, rng: np.random.Generator
                  ) -> tuple[pd.DataFrame, list[str]]:
    """C1: every session missed with probability `p` (one seeded realisation over the day set): its trades dropped, the
    day itself kept in the calendar by the caller (an empty block). (the trades left, the missed days)."""
    miss = rng.random(len(days)) < float(p)
    gone = {str(d) for d, m in zip(days, miss) if m}
    return t[~t["date"].astype(str).isin(gone)].reset_index(drop=True), sorted(gone)


def c1_seed(subject_index: int, arm_index: int, realisation: int) -> int:
    """C1's seed for one realisation: `lockstep.child_seed(SEED_C1, len(C1_ARMS) x subject + arm, realisation)` --
    subjects S1, S2 are 0, 1; arms in `C1_ARMS`' order; realisations 0 .. C1_REALISATIONS - 1. All fixed now."""
    from propedge.campaign.lockstep import child_seed

    return int(child_seed(SEED_C1, len(C1_ARMS) * int(subject_index) + int(arm_index), int(realisation)))


def realisation_summary(values: Sequence[float]) -> dict[str, float]:
    """C1's summary of one reading over an arm's realisations: their mean, smallest, largest and range (NaN left out;
    a minus infinity kept, the range then infinite)."""
    v = np.asarray([float(x) for x in values if x is not None and not np.isnan(float(x))], dtype=float)
    if not len(v):
        return {"mean": float("nan"), "min": float("nan"), "max": float("nan"), "range": float("nan"), "n": 0}
    return {"mean": float(v.mean()), "min": float(v.min()), "max": float(v.max()),
            "range": float(v.max() - v.min()) if np.isfinite(v).all() else float("inf"), "n": int(len(v))}


def stress_by_kind(t: pd.DataFrame, kinds: pd.DataFrame, added: Mapping[str, float], keys: Sequence[float],
                   stop_col: str = "stop_ticks") -> pd.DataFrame:
    """C2: each offered R's net outcome lowered by the arm's extra ticks for that R's exit kind over the trade's own stop
    in ticks: r'_R = r_R - added[kind_R] / stop. `kinds` holds a column `o_<R>` per R, row for row with `t`; an offered
    outcome with a kind outside `KINDS` is refused. Every other column is unchanged."""
    if len(kinds) != len(t):
        raise ValueError("the kinds are not row for row with the trades")
    out = t.copy()
    stop = out[stop_col].to_numpy(float)
    if not np.all(np.isfinite(stop) & (stop > 0)):
        raise ValueError("a stop that is not a positive number of ticks")
    for R in keys:
        col = f"r_{float(R):g}"
        r = out[col].to_numpy(float)
        on = np.isfinite(r)
        if not on.any():
            continue
        k = kinds[f"o_{float(R):g}"].astype(str).to_numpy()
        bad = on & ~np.isin(k, KINDS)
        if bad.any():
            raise ValueError(f"{int(bad.sum())} offered {col} outcomes with an exit kind outside {KINDS}")
        ticks = np.zeros(len(out))
        for code in KINDS:
            ticks[k == code] = float(added[code])
        out[col] = np.where(on, r - ticks / stop, r)
    return out


# ------------------------------------------------------------------------------------------------ readings


def longest_gap(events: Sequence[int], horizon: int) -> int:
    """The longest stretch of sessions without an event: from day 0 to the first, between events, from the last to the
    horizon's end (the whole horizon when there is none) -- `customer_slices._longest_gap`."""
    marks = [0] + sorted(int(d) for d in events) + [int(horizon)]
    return int(max(b - a for a, b in zip(marks, marks[1:])))


def payout_days(path: Any) -> list[int]:
    """The days a campaign path's payouts arrived on, from its first-payout day and the gaps after it."""
    if getattr(path, "days_to_first_payout", None) is None:
        return []
    out = [int(path.days_to_first_payout)]
    for g in getattr(path, "payout_gaps", ()) or ():
        out.append(out[-1] + int(g))
    return out


def path_values(paths: Sequence[Any], margin: float) -> dict[str, np.ndarray]:
    """Per path (`LockstepPath`s): net cash at the end, the bankroll it required (its deepest loss from the start plus
    `margin`, `portfolio.required_bankroll`'s), its payouts and its longest payout drought in sessions."""
    net, need, pays, drought = [], [], [], []
    for x in paths:
        p = x.path
        cash = np.asarray(p.cash_series, dtype=float)
        init = float(p.initial_bankroll)
        net.append(float(cash[-1] - init) if len(cash) else 0.0)
        need.append(float(max(0.0, init - cash.min())) + float(margin) if len(cash) else float(margin))
        d = payout_days(p)
        pays.append(len(d))
        drought.append(longest_gap(d, len(cash)))
    return {"net": np.array(net, float), "required": np.array(need, float), "payouts": np.array(pays, float),
            "drought": np.array(drought, float)}


def path_readings(paths: Sequence[Any], margin: float) -> dict[str, float]:
    """One run's columns beside the gate row's own: `v1_share_below_start`, `v1_payout_drought_p90`,
    `v1_payouts_per_path_p50`, `v1_net_p10`, `v1_net_p50`."""
    if not len(paths):
        return {}
    v = path_values(paths, margin)
    return {"v1_share_below_start": float(np.mean(v["net"] < 0)),
            "v1_payout_drought_p90": float(np.percentile(v["drought"], 90)),
            "v1_payouts_per_path_p50": float(np.median(v["payouts"])),
            "v1_net_p10": float(np.percentile(v["net"], 10)), "v1_net_p50": float(np.median(v["net"]))}


def growth_on_required(net: Sequence[float], required: Sequence[float], days: int) -> tuple[float, float]:
    """(growth on the required bankroll, the required bankroll's 90th percentile) from a run's per-path net cash and
    required bankroll, as `portfolio.measures` reads them: the base is the 90th percentile of the required bankroll,
    a path's growth log((base + net) / base) x 252 / days (minus infinity when it lost the base), the median path's."""
    net, req = np.asarray(net, float), np.asarray(required, float)
    base = float(np.percentile(req, 90))
    with np.errstate(divide="ignore", invalid="ignore"):
        g = np.where(base + net > 0, np.log(np.where(base + net > 0, (base + net) / base, 1.0)), -np.inf)
    return float(np.median(g) * 252.0 / int(days)), base


def mc_error(net: Sequence[float], required: Sequence[float], days: int, rng: np.random.Generator,
             reps: int = 1000) -> dict[str, float]:
    """The Monte-Carlo standard error of a run's two gate figures from its own paths: the standard deviation over
    `reps` resamples of the paths (with replacement) of `growth_on_required`'s two values. A reading of how far two
    runs of one law may differ, used for A1's control; never a test."""
    net, req = np.asarray(net, float), np.asarray(required, float)
    n = len(net)
    g, b = np.empty(int(reps)), np.empty(int(reps))
    for i in range(int(reps)):
        ix = rng.integers(0, n, size=n)
        g[i], b[i] = growth_on_required(net[ix], req[ix], days)
    fin = np.isfinite(g)
    return {"growth_se": float(g[fin].std(ddof=1)) if fin.sum() > 1 else float("nan"),
            "required_p90_se": float(b.std(ddof=1)), "mc_resamples": int(reps)}


def exceed_shares(real_required: Sequence[float], real_net: Sequence[float], scheme_required: Sequence[float],
                  scheme_net: Sequence[float]) -> dict[str, float]:
    """A2's reading for one scheme: the share of real-order starts whose required bankroll exceeds the scheme's resampled
    90th percentile (0.10 if the scheme's days are history's) and its median (0.50), and whose net cash is below the
    scheme's 10th percentile (0.10). The starts overlap, so the shares carry no interval."""
    rr, rn = np.asarray(real_required, float), np.asarray(real_net, float)
    sr, sn = np.asarray(scheme_required, float), np.asarray(scheme_net, float)
    if not len(rr) or not len(sr):
        return {"starts": int(len(rr)), "paths": int(len(sr))}
    p90, p50, n10 = float(np.percentile(sr, 90)), float(np.percentile(sr, 50)), float(np.percentile(sn, 10))
    return {"starts": int(len(rr)), "paths": int(len(sr)), "scheme_required_p90": p90, "scheme_required_p50": p50,
            "scheme_net_p10": n10, "share_required_above_p90": float(np.mean(rr > p90)), "expected_above_p90": 0.10,
            "share_required_above_p50": float(np.mean(rr > p50)), "expected_above_p50": 0.50,
            "share_net_below_p10": float(np.mean(rn < n10)), "expected_below_p10": 0.10}


def a2_starts(n_days: int, horizon: int = A2_HORIZON, step: int = A2_STEP) -> list[int]:
    """A2's real-order starts: every `step`-th session whose `horizon` sessions lie inside the history."""
    return [s for s in range(0, int(n_days), int(step)) if s + int(horizon) <= int(n_days)]


def b2_shifts() -> list[float]:
    """B2's declared shifts below the registered bound: 0, -B2_STEP, ... (B2_MAX_STEPS steps after 0)."""
    return [-(B2_STEP * k) if k else 0.0 for k in range(B2_MAX_STEPS + 1)]


def centre_cells(metric: np.ndarray, n: np.ndarray) -> np.ndarray:
    """B3's null: each cell's per-day summed metric (cells x days) less its trades (`n`) times the cell's own mean per
    trade, so every cell's mean per trade is zero and its day-to-day spread and its dependence on the other cells are
    kept."""
    tot_n = n.sum(axis=1, keepdims=True)
    mean = np.where(tot_n > 0, metric.sum(axis=1, keepdims=True) / np.where(tot_n > 0, tot_n, 1.0), 0.0)
    return metric - n * mean


__all__ = ["DECISION", "RESULT", "DECLARATION_SHA256", "SUBJECTS", "PARTS", "N_PATHS", "LEDGER_N", "ALPHA",
           "ACF_LAGS", "LB_LAGS", "MEAN_BLOCKS", "A2_HORIZON", "A2_STEP", "A2_PATHS", "B1_BLOCKS", "B1_REPS",
           "B1_VERIFY", "B2_STEP", "B2_MAX_STEPS", "B2_MEAN_BLOCK", "B3_REPS", "B3_MEAN_BLOCK", "C1_ARMS", "C1_REALISATIONS", "KINDS",
           "SEED_A2", "SEED_B1", "SEED_B3", "SEED_C1", "READING", "WORDS", "declaration", "declaration_problems", "acf",
           "ljung_box", "runs_test", "politis_white", "auto_block", "dependence_rows", "day_sums", "stationary_indices",
           "block_bounds", "era_rule_bounds", "binomial_interval", "coverage_counts", "coverage", "break_even", "drop_trades",
           "miss_sessions", "c1_seed", "realisation_summary", "stress_by_kind", "longest_gap", "payout_days", "path_values", "path_readings",
           "growth_on_required", "mc_error", "exceed_shares", "a2_starts", "b2_shifts", "centre_cells"]
