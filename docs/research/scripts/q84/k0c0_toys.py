"""Q-84 (E-051's rule, E-052 (1)): F-02's K0 and C0 on synthetic toys -- their level and their power at the family's
level, shown before the pin. Synthetic only: no bar, no walk, no outcome of any design is read. Seeds fixed before the
run, in F-02's section 15: 20262024 (the count patterns) and 20262025 (every outcome draw).

    python docs/research/scripts/q84/k0c0_toys.py one     # C1's one-sample `cons` (about 12 minutes, under 200 MB)
    python docs/research/scripts/q84/k0c0_toys.py two     # C1''s treated two-sample `cons` (about 7 minutes)

**The null** is Q-16's `cluster` (the pass-line review's `intensity.py`): each fill is 0.5 sign(a_s + e + c), with a_s
the session effect (icc 0.35) and e ~ N(0, 1 - icc). At c = 0 it is an exact null with sides reset daily; a planted
lift is c > 0 (for C1', on the level fills only).

**The counts** (fills a session, mean M) are drawn under four profiles:
- `iid`: negative binomial, size 1 (Q-16's form);
- `ar98_sd10`, `ar98_sd15`: log-intensity AR(1) 0.98 across sessions, stationary sd 1.0 or 1.5, Poisson given it (the
  review's persistent profiles; at sd 1.5 `cons` alone is above its level there);
- `quarter10`: one 63-session quarter at ten times the rest's rate.

For C1' the placebo's counts are five times the level's rate on the same intensity path, sharing a_s.

**K0 and C0 are F-02's checks (sections 7.1 and 9.0).** For one count pattern they take `cons`'s rejection rate at
0.05/132 over 200,000 replications of the null, with its 95 % Clopper-Pearson interval, and flag the pattern when the
interval lies wholly above nominal.
- K0 lays a 1,006-session choice-block pattern onto 657 sessions at a random circular offset each replication.
- C0 uses the 657 judged counts as they are.

**Per pattern the script reports:**
- the K0 and C0 flags;
- the pattern's size, on independent draws -- the combined line's size is that size times "C0 not flagged";
- the power at the planted lift, again times "C0 not flagged" for the combined line. C0 reads counts only, so it is
  independent of the outcome draw given the counts.

**Per profile it reports** the means of these over the patterns, and the flag rates.
"""
from __future__ import annotations

import math
import sys
import time
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from extended import lift_bound as LB  # noqa: E402

SEED_PATTERNS = 20262024
SEED_DRAWS = 20262025
N_JUDGED, N_CHOICE = 657, 1006
ICC = 0.35
LEVEL = LB.family_level(11)                      # 0.05 / 132
REPS_FLAG = 200_000                              # K0's and C0's own replication count (F-02 7.1, 9.0)
REPS_SIZE = 200_000                              # the independent size estimate
REPS_POWER = 20_000
BATCH = 4000
M1 = 0.3                                         # level fills a session: the sparse end, about 200 judged fills
PLACEBO_X = 5                                    # placebo fills five times the level's (F-02 5.8)
SHIFT = {"one": 0.75, "two": 0.85}               # the planted probit shift c for the power runs
PROFILES = {"one": ("iid", "ar98_sd10", "ar98_sd15", "quarter10"), "two": ("iid", "ar98_sd15")}
PATTERNS = {"one": 4, "two": 3}


def intensity(profile: str, n: int, m: float, rng) -> np.ndarray:
    """The per-session rate path (n,) of one count pattern."""
    if profile == "iid":
        return np.full(n, m)
    if profile == "quarter10":
        L = 63
        start = int(rng.integers(0, n - L + 1))
        base = m * n / (n - L + 10 * L)
        lam = np.full(n, base)
        lam[start:start + L] = 10 * base
        return lam
    sd = {"ar98_sd10": 1.0, "ar98_sd15": 1.5}[profile]
    phi = 0.98
    h = np.empty(n)
    h[0] = rng.standard_normal() * sd
    inn = sd * math.sqrt(1 - phi * phi)
    for t in range(1, n):
        h[t] = phi * h[t - 1] + inn * rng.standard_normal()
    return m * np.exp(h - sd * sd / 2)


def counts(profile: str, lam: np.ndarray, rng) -> np.ndarray:
    """Counts given the rate: negative binomial (size 1) for `iid` and `quarter10` (Q-16's and the review's form),
    Poisson for the AR profiles."""
    if profile in ("iid", "quarter10"):
        return rng.negative_binomial(1.0, 1.0 / (1.0 + lam)).astype(float)
    return rng.poisson(lam).astype(float)


def sums(N: np.ndarray, a: np.ndarray, c: float, rng) -> np.ndarray:
    """Session sums of 0.5 sign(a + e + c) over N fills a session, e ~ N(0, 1 - icc)."""
    p = stats.norm.cdf((a + c) / math.sqrt(1 - ICC))
    up = rng.binomial(N.astype(np.int64), p)
    return 0.5 * (2 * up - N)


def rate_one(N_of, reps: int, c: float, rng) -> int:
    """`cons`'s rejections at LEVEL over `reps` replications; N_of(r) gives the (657, r) counts of a batch."""
    k, done = 0, 0
    while done < reps:
        r = min(BATCH, reps - done)
        N = N_of(r)
        a = rng.standard_normal(N.shape) * math.sqrt(ICC)
        rj, _ = LB.many_levels("cons", sums(N, a, c, rng), N, [LEVEL])
        k += int(rj[0].sum())
        done += r
    return k


def rate_two(N1_of, N2_of, reps: int, c: float, rng) -> int:
    """The treated two-sample `cons`'s rejections at LEVEL: level fills (shift c) against placebo fills (no shift),
    both on the session effect a_s (the C1' null at c = 0)."""
    k, done = 0, 0
    while done < reps:
        r = min(BATCH, reps - done)
        N1, N2 = N1_of(r), N2_of(r)
        a = rng.standard_normal(N1.shape) * math.sqrt(ICC)
        rj, _ = LB.diff_many_levels("cons", sums(N1, a, c, rng), N1, sums(N2, a, 0.0, rng), N2, [LEVEL])
        k += int(rj[0].sum())
        done += r
    return k


def flagged(k: int, reps: int) -> tuple[bool, float, float]:
    lo, hi = LB.clopper_pearson(k, reps)
    return lo > LEVEL, lo, hi


def fixed(N: np.ndarray):
    return lambda r: np.repeat(N[:, None], r, axis=1)


def offsets(Nc: np.ndarray, rng):
    """K0's layout: each replication a 657-session window of the choice-block pattern at a random circular offset."""
    def make(r):
        o = rng.integers(0, len(Nc), size=r)
        idx = (o[None, :] + np.arange(N_JUDGED)[:, None]) % len(Nc)
        return Nc[idx]
    return make


def run(part: str) -> None:
    two = part == "two"
    print(f"Q-84 toys, part {part}: level {LEVEL:.6g} (0.05/132); flags at {REPS_FLAG:,} replications; size at "
          f"{REPS_SIZE:,}; power at {REPS_POWER:,}, planted shift c = {SHIFT[part]}; M = {M1} level fills a session"
          + (f", placebo x{PLACEBO_X}" if two else ""), flush=True)
    for pi, prof in enumerate(PROFILES[part]):
        rows = []
        t0 = time.time()
        for j in range(PATTERNS[part]):
            prng = np.random.default_rng([SEED_PATTERNS, int(two), pi, j])
            lam_c = intensity(prof, N_CHOICE, M1, prng)
            lam_j = intensity(prof, N_JUDGED, M1, prng)
            Nc1, Nj1 = counts(prof, lam_c, prng), counts(prof, lam_j, prng)
            if two:
                Nc2, Nj2 = counts(prof, PLACEBO_X * lam_c, prng), counts(prof, PLACEBO_X * lam_j, prng)
            d = [np.random.default_rng([SEED_DRAWS, int(two), pi, j, s]) for s in range(4)]
            if two:
                # K0 lays both choice-block patterns at the same offset (one draw serves both)
                def k0_pair(r, g=d[0]):
                    o = g.integers(0, N_CHOICE, size=r)
                    idx = (o[None, :] + np.arange(N_JUDGED)[:, None]) % N_CHOICE
                    return Nc1[idx], Nc2[idx]
                cache = {}

                def k1(r):
                    cache["pair"] = k0_pair(r)
                    return cache["pair"][0]

                def k2(r):
                    return cache["pair"][1]
                kk0 = rate_two(k1, k2, REPS_FLAG, 0.0, d[0])
                kc0 = rate_two(fixed(Nj1), fixed(Nj2), REPS_FLAG, 0.0, d[1])
                ksz = rate_two(fixed(Nj1), fixed(Nj2), REPS_SIZE, 0.0, d[2])
                kpw = rate_two(fixed(Nj1), fixed(Nj2), REPS_POWER, SHIFT[part], d[3])
            else:
                kk0 = rate_one(offsets(Nc1, d[0]), REPS_FLAG, 0.0, d[0])
                kc0 = rate_one(fixed(Nj1), REPS_FLAG, 0.0, d[1])
                ksz = rate_one(fixed(Nj1), REPS_SIZE, 0.0, d[2])
                kpw = rate_one(fixed(Nj1), REPS_POWER, SHIFT[part], d[3])
            f0, f0lo, f0hi = flagged(kk0, REPS_FLAG)
            fc, fclo, fchi = flagged(kc0, REPS_FLAG)
            size, power = ksz / REPS_SIZE, kpw / REPS_POWER
            top = np.add.reduceat(Nj1, np.flatnonzero(np.r_[True, np.diff(LB.block_index(N_JUDGED, 63)[0]) != 0]))
            rows.append((f0, fc, size, power, top.max() / max(top.sum(), 1.0), int(Nj1.sum())))
            print(f"  {prof:10s} pattern {j}: judged fills {int(Nj1.sum())}, top-quarter share "
                  f"{top.max() / max(top.sum(), 1.0):.2f} | K0 rate {kk0 / REPS_FLAG / LEVEL:.2f}x "
                  f"[{f0lo / LEVEL:.2f}, {f0hi / LEVEL:.2f}] {'FLAG' if f0 else 'pass'} | C0 rate "
                  f"{kc0 / REPS_FLAG / LEVEL:.2f}x [{fclo / LEVEL:.2f}, {fchi / LEVEL:.2f}] {'FLAG' if fc else 'pass'} | "
                  f"size {size / LEVEL:.2f}x | power {power:.3f}", flush=True)
        f0s = np.array([r[0] for r in rows]); fcs = np.array([r[1] for r in rows])
        sz = np.array([r[2] for r in rows]); pw = np.array([r[3] for r in rows])
        print(f"  {prof:10s} SUMMARY over {len(rows)} patterns: K0 flags {int(f0s.sum())}, C0 flags {int(fcs.sum())}; "
              f"size: cons {sz.mean() / LEVEL:.2f}x, with C0 {np.mean(sz * ~fcs) / LEVEL:.2f}x; "
              f"power: cons {pw.mean():.3f}, with C0 {np.mean(pw * ~fcs):.3f}; {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    part = sys.argv[1] if len(sys.argv) > 1 else "one"
    if part not in ("one", "two"):
        raise SystemExit("usage: k0c0_toys.py one|two")
    run(part)
