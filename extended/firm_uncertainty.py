"""RD-01 10.2 (`prereg/RD-01_firm_contracts.md`): the uncertainty on each paired reading, fixed at the reading's pin.

Descriptions, not tests: nothing here is compared with a critical value to decide anything, and no one-sided
comparison is computed (a described reading has no level, E-023 (1)).

* **The windows** (item 1): a block's starts in order, cut into consecutive h-start windows from the first (a last
  incomplete window dropped), **every other window kept** -- the first, third, fifth, ... -- so no two kept windows'
  measures share a session.
* **The interval** (item 2): a two-sided 90 % Student-t interval on the kept window means, n_w - 1 degrees of freedom,
  only when n_w >= 4; below that, "too few independent windows for an interval".
* **The sign count** (item 3), **the effective sample size** (item 4, `extended.user_measures.n_eff_bartlett` at lag h
  on all the block's starts), **the minimum detectable difference** (item 5: (t(0.95) + t(0.80)) x SE), **the zero
  rule** (item 6: "identical on these trades").
* **The interval's honesty** (item 7): its coverage on synthetic overlapping series built as the reading's measures
  are (a session series; each start's measure the sum, or the 0/1 sign, of the h sessions from it; the windows of item
  1), seed 20261991, on the declared shapes; a coverage below 0.88 is labelled.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np
from scipy import stats

#: 10.2 item 7's seed (section 12)
SEED = 20261991
#: 10.2 item 2: the interval's level, and the least number of kept windows that prints one
LEVEL = 0.90
MIN_WINDOWS = 4
#: 10.2 item 5: the power of the minimum detectable difference
POWER = 0.80
#: 10.2 item 7: the coverage below which a reading is labelled
COVERAGE_FLOOR = 0.88
#: 10.2 item 7: the series per setting, and the skewed shapes' grid
N_SERIES = 20_000
LUMPY_G = 0.01
LUMPY_P = (0.05, 0.10, 0.20)
LUMPY_S = (0.0025, 0.005, 0.01)
#: 10.2 item 7 (c): the paired series' common factor -- two session series correlated 0.64 (0.8 squared)
PAIRED_LOADING = 0.8
TOO_FEW = "too few independent windows for an interval"
IDENTICAL = "identical on these trades"


def n_windows(n_starts: int, h: int) -> int:
    """The number of kept windows (item 1) on a block of `n_starts` starts at horizon `h`."""
    whole = int(n_starts) // int(h)
    return (whole + 1) // 2


def kept_windows(x: np.ndarray, h: int) -> list[np.ndarray]:
    """Item 1: the kept windows of `x` (the per-start series in start order): every other whole h-start window."""
    v = np.asarray(x, float)
    whole = len(v) // int(h)
    return [v[i * h:(i + 1) * h] for i in range(0, whole, 2)]


def paired_reading(diff: np.ndarray, h: int) -> dict[str, Any]:
    """Items 1-6 on one per-start series (plan less TS, in start order) at horizon `h`."""
    from extended.user_measures import n_eff_bartlett

    d = np.asarray(diff, float)
    wins = kept_windows(d, h)
    means = np.array([float(np.mean(w)) for w in wins])
    n_w = len(means)
    out: dict[str, Any] = {"n_w": n_w, "h": int(h), "mean": float(means.mean()) if n_w else float("nan"),
                           "signs": {"above": int((means > 0).sum()), "equal": int((means == 0).sum()),
                                     "below": int((means < 0).sum())},
                           "n_eff": n_eff_bartlett(d, lag=int(h)), "interval": None, "mdd": None, "note": ""}
    if n_w and all(bool(np.all(w == 0.0)) for w in wins):          # item 6 (m3): the values, not the means
        out["note"] = IDENTICAL
        return out
    if n_w < MIN_WINDOWS:
        out["note"] = TOO_FEW
        return out
    se = float(means.std(ddof=1)) / math.sqrt(n_w)
    tq = float(stats.t.ppf(0.5 + LEVEL / 2.0, n_w - 1))
    out["interval"] = (float(means.mean() - tq * se), float(means.mean() + tq * se))
    out["mdd"] = float((tq + float(stats.t.ppf(POWER, n_w - 1))) * se)
    return out


# ------------------------------------------------------------------------------------------------ item 7


def per_start_sums(sessions: np.ndarray, h: int, n_starts: int) -> np.ndarray:
    """Each start's measure: the sum of the h sessions from it (sessions s .. s + h - 1)."""
    c = np.concatenate([[0.0], np.cumsum(np.asarray(sessions, float))])
    return c[h:h + n_starts] - c[:n_starts]


def coverage_shapes() -> list[str]:
    """Item 7's shapes: (a) gauss, (b) ahead, (c) paired, (d) lumpy (and mirror) on the declared grid, (e) persistent."""
    out = ["gauss", "ahead", "paired"]
    for p in LUMPY_P:
        for s in LUMPY_S:
            for m in ("", "_mirror"):
                out.append(f"lumpy{m}_p{p}_s{s}")
                out.append(f"persistent{m}_p{p}_s{s}")
    return out


def _lumpy_sessions(rng: np.random.Generator, n: int, p: float, s: float, mirror: bool, persistent: bool) -> np.ndarray:
    rare = rng.random(n) < p
    if persistent:                                   # (e): the rare session's sign repeated in the next with prob 1/2
        rep = rng.random(n) < 0.5
        for i in range(1, n):
            if rare[i - 1] and rep[i]:
                rare[i] = True
    g = LUMPY_G
    low = -g * (1.0 - p) / p
    x = np.where(rare, low, g) + rng.normal(0.0, s, n)
    if persistent:
        # the repetition raises the rare share from p to its stationary value 2p / (1 + p) (rare_i = base_i or
        # (rare_{i-1} and a coin)); its known mean is taken off, so the series' mean is zero, as (d)'s is
        pi = 2.0 * p / (1.0 + p)
        x = x - (pi * low + (1.0 - pi) * g)
    return -x if mirror else x


def _series(shape: str, rng: np.random.Generator, h: int, n_starts: int) -> np.ndarray:
    n_sess = n_starts + h - 1
    if shape == "gauss":
        return per_start_sums(rng.standard_normal(n_sess), h, n_starts) / math.sqrt(h)
    if shape == "ahead":
        return (per_start_sums(rng.standard_normal(n_sess), h, n_starts) > 0).astype(float) - 0.5
    if shape == "paired":
        z = rng.standard_normal(n_sess)
        q = math.sqrt(1.0 - PAIRED_LOADING ** 2)
        ea = PAIRED_LOADING * z + q * rng.standard_normal(n_sess)
        eb = PAIRED_LOADING * z + q * rng.standard_normal(n_sess)
        sa, sb = per_start_sums(ea, h, n_starts), per_start_sums(eb, h, n_starts)
        return (sa > 0).astype(float) - (sb > 0).astype(float)
    kind, rest = shape.split("_p", 1)
    p_s, s_s = rest.split("_s")
    mirror = kind.endswith("_mirror")
    persistent = kind.startswith("persistent")
    sess = _lumpy_sessions(rng, n_sess, float(p_s), float(s_s), mirror, persistent)
    return per_start_sums(sess, h, n_starts)


def coverage(shape: str, *, h: int, n_w: int, n_series: int = N_SERIES, seed: int = SEED) -> float:
    """Item 7: the share of `n_series` zero-mean synthetic series (`shape`) whose item-2 interval covers zero, at
    horizon `h` with `n_w` kept windows (so 2 n_w - 1 whole windows of starts)."""
    if n_w < MIN_WINDOWS:
        raise ValueError("the interval is printed only from four kept windows")
    rng = np.random.default_rng(int(seed))
    n_starts = (2 * int(n_w) - 1) * int(h)
    hits = done = 0
    for _ in range(int(n_series)):
        r = paired_reading(_series(shape, rng, int(h), n_starts), int(h))
        if r["interval"] is None:
            continue
        done += 1
        hits += int(r["interval"][0] <= 0.0 <= r["interval"][1])
    return float(hits / done) if done else float("nan")


def coverage_label(cov: float) -> str | None:
    """Item 7's label: below 0.88, "interval below its coverage" with the coverage."""
    return None if not (cov < COVERAGE_FLOOR) else f"interval below its coverage ({cov:.3f})"


__all__ = ["SEED", "LEVEL", "MIN_WINDOWS", "POWER", "COVERAGE_FLOOR", "N_SERIES", "TOO_FEW", "IDENTICAL", "n_windows",
           "kept_windows", "paired_reading", "per_start_sums", "coverage_shapes", "coverage", "coverage_label"]
