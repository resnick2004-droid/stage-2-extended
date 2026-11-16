"""Q-87 (family O's third draft): the level and power **at the family's level** of the rules the third version adds or
tightens -- E-051's program rule ("a tightening is accepted only with its level and power at the family's level shown
before the pin"). Synthetic data only: no bar, walk or result file is read. Slow tier (minutes; light in memory,
chunked); the figures are printed and quoted in the draft's section 18.3 and the hand-back.

1. **K0, E-052 (1)'s outcome-free check** (the draft's A11). `cons` (the treated two-sample form E-035 (2) adopts) at
   the family's level on the sign null of Q-16's `cluster` form -- each offer 1/2 sign(a_s + e), the session effect
   a_s shared by every offer of the session (icc 0.35), so the null is exact -- with the counts of a cell taken from a
   count series at a random circular offset. Toy count patterns stand for the declared persistence classes: offers
   (Q-16's iid reference), a window clustered across nights (s1, s2), whole sessions in runs of 5 (u3), 21 and 63 (s3);
   and C2's openings, the design's uses clustered on in-state sessions against two twin draws' uses clustered at shifted
   sessions (the clustered placebo, m2-1). Printed: the rejection rate over the nominal with its 95 % Clopper-Pearson
   interval at k = 12 and 15, and K0's verdict (killed when the interval lies wholly above the nominal). K0 changes no
   statistic: a surviving cell keeps `cons`'s level and power; a killed cell has none.

2. **B2 with the judged-block amplitude floor (d)** (the draft's 11 item 2, m2-3 under E-051's ruling). Each session
   has a common value -- A x rho (a sign switching 1/63) plus an AR(1) (phi 0.5, sd 0.25), as the second read's check
   B -- and 186 offers, the in-state group's and the rest's mean noise per-offer sd 0.8 over about 1 to 6 effective
   offers (neighbouring marks' walks overlap); a choice span of 750 sessions and a judged span of 630, values centred
   within years at the offer level. Two fixed selections, independent of the values: **whole sessions** in runs of
   mean 21 (s3, u3's class) and a **window** whose nightly share clusters across nights (s1, s2). B2 as declared: the
   choice values resampled by a stationary bootstrap (mean block 63), fresh offer noise, plus a* x a slow sign, centred
   within the judged years; each member's critical value the larger of its t and B2's (1 - level) quantile, the
   quantile taken non-decreasing in a*. a* is (a), the choice span's largest |63-block mean| ((b), Stage 2's recorded
   lift, is 0 in the toy), or max((a), (d)) with (d) the judged block's largest |63-block mean| over the
   **out-of-state offers only, centred by their own year means** -- so it takes no term from the selection's own lift.
   Printed: the level at the family's level over 200,000 null judged blocks, and the power over 4,000 judged blocks
   at each planted lift, for `cons` at its nominal values, the larger-of rule with (a), and with (a) and (d).

Seeds `numpy.random.default_rng([20261988, 300, ...])` (K0's toys) and `[20261988, 400, ...]` (B2's), the draft's
section 16. The toy B2 uses 400,000 replicates per grid point (the declared B2 uses at least 1,000,000); its quantile
at the family's level then rests on about 128 exceedances, stated as the toy's own Monte Carlo error.
"""
from __future__ import annotations

import math
import time

import numpy as np
import pytest
from scipy import stats

from extended import lift_bound as LB

pytestmark = pytest.mark.slow

SEED = 20261988
N_C, N_J = 750, 630                      # the choice span's and the judged block's sessions (about)
KS = (12, 15)
LEVELS = tuple(LB.family_level(k) for k in KS)
ICC = 0.35
OFFERS = 186                              # P-16's overnight population marks a normal session
MEMBERS = (21, 42, 63)


def cp_ratio(k: int, n: int, a: float) -> tuple[float, float, float]:
    lo, hi = LB.clopper_pearson(int(k), int(n))
    return k / n / a, lo / a, hi / a


def daily_chain(rng, n: int, share: float, mean_run: float) -> np.ndarray:
    """A two-state daily state: in-state runs of mean `mean_run`, long-run share `share`."""
    stay = 1.0 - 1.0 / mean_run
    enter = (1.0 / mean_run) * share / (1.0 - share)
    s = np.zeros(n, dtype=bool)
    s[0] = rng.random() < share
    u = rng.random(n)
    for t in range(1, n):
        s[t] = (u[t] < stay) if s[t - 1] else (u[t] < enter)
    return s


# ------------------------------------------------------------------------------------------------ 1. K0


def count_patterns(rng) -> dict[str, tuple[np.ndarray, np.ndarray, str]]:
    """{name: (N1 series, N2 series, form)} over the choice span; form 'nested' (C1: in-state offers within every
    offer) or 'pair' (C2: the design's openings against the twin designs')."""
    out: dict[str, tuple[np.ndarray, np.ndarray, str]] = {}
    n2 = np.full(N_C, OFFERS, dtype=np.int64)
    out["offer (iid, Q-16's reference)"] = (rng.binomial(OFFERS, 1 / 3, N_C), n2, "nested")
    w = np.zeros(N_C)
    for t in range(1, N_C):
        w[t] = 0.7 * w[t - 1] + math.sqrt(1 - 0.49) * rng.standard_normal()
    share = np.clip(1 / 3 + 0.25 * w, 0.0, 1.0)
    out["window, clustered across nights (s1, s2)"] = (np.rint(OFFERS * share).astype(np.int64), n2, "nested")
    for run, tag in ((5, "u3"), (21, "s3"), (63, "s3, slower")):
        s = daily_chain(rng, N_C, 1 / 3, run)
        out[f"whole sessions, runs {run} ({tag})"] = (np.where(s, OFFERS, 0).astype(np.int64), n2, "nested")
    s = daily_chain(rng, N_C, 1 / 3, 21)
    noise = np.zeros(N_C)
    for t in range(1, N_C):
        noise[t] = 0.98 * noise[t - 1] + 0.5 * math.sqrt(1 - 0.98 ** 2) * rng.standard_normal()
    lam = np.exp(noise - 0.125)
    design = rng.poisson(4.0 * np.where(s, 3.0, 0.3) * lam)
    twin = sum(rng.poisson(4.0 * np.where(np.roll(s, int(rng.integers(63, N_C - 63))), 3.0, 0.3) * lam)
               for _ in range(2))                                 # two clustered twin draws, pooled
    out["C2 openings: design vs two clustered twin draws"] = (design.astype(np.int64), twin.astype(np.int64), "pair")
    return out


def k0_rejections(N1s, N2s, form: str, reps: int, seed, chunk: int = 2000) -> np.ndarray:
    """`cons`'s rejections at LEVELS on the cluster sign null, the counts at a random circular offset each replication."""
    rng = np.random.default_rng(seed)
    rej = np.zeros(len(LEVELS), dtype=np.int64)
    done = 0
    t = np.arange(N_J)
    while done < reps:
        r = min(chunk, reps - done)
        idx = (rng.integers(0, N_C, r)[None, :] + t[:, None]) % N_C
        N1, N2 = N1s[idx], N2s[idx]
        p = stats.norm.cdf(rng.standard_normal((N_J, r)) * math.sqrt(ICC) / math.sqrt(1 - ICC))
        if form == "nested":
            u1 = rng.binomial(N1, p)
            ur = rng.binomial(N2 - N1, p)
            S1 = 0.5 * (2 * u1 - N1)
            S2 = S1 + 0.5 * (2 * ur - (N2 - N1))
        else:
            S1 = 0.5 * (2 * rng.binomial(N1, p) - N1)
            S2 = 0.5 * (2 * rng.binomial(N2, p) - N2)
        rj, _ = LB.diff_many_levels("cons", S1, N1.astype(float), S2, N2.astype(float), LEVELS)
        rej += rj.sum(axis=1)
        done += r
    return rej


def test_k0_count_persistence_size_at_the_family_level():
    reps = 200_000
    pats = count_patterns(np.random.default_rng([SEED, 300, 0]))
    print(f"\nK0 toys: cons (treated two-sample) on the cluster sign null, {reps} replications each, {N_J} sessions")
    for i, (name, (N1s, N2s, form)) in enumerate(pats.items()):
        t0 = time.time()
        rej = k0_rejections(N1s, N2s, form, reps, [SEED, 300, 1, i])
        cells = []
        for k, a, n_rej in zip(KS, LEVELS, rej):
            ratio, lo, hi = cp_ratio(n_rej, reps, a)
            killed = lo > 1.0
            cells.append(f"k={k}: {n_rej} rej, {ratio:.2f}x [{lo:.2f}, {hi:.2f}] {'KILLED' if killed else 'kept'}")
            lo_raw, _ = LB.clopper_pearson(int(n_rej), reps)
            assert killed == (lo_raw > a)                            # K0's verdict is the interval's, nothing else
        print(f"  {name} ({form}; mean N1 {N1s.mean():.1f}, mean N2 {N2s.mean():.1f}): " + "; ".join(cells)
              + f"  [{time.time() - t0:.0f} s]", flush=True)
        assert np.all(rej >= 0)


# ------------------------------------------------------------------------------------------------ 2. B2 and (d)


def slow_values(rng, n: int, A: float) -> np.ndarray:
    """A session's common value: A x rho (a sign switching with probability 1/63) plus an AR(1) (phi 0.5, sd 0.25)."""
    rho = np.empty(n)
    rho[0] = 1.0 if rng.random() < 0.5 else -1.0
    flips = rng.random(n) < 1 / 63
    for t in range(1, n):
        rho[t] = -rho[t - 1] if flips[t] else rho[t - 1]
    e = np.zeros(n)
    e[0] = 0.25 * rng.standard_normal()
    for t in range(1, n):
        e[t] = 0.5 * e[t - 1] + 0.25 * math.sqrt(1 - 0.25) * rng.standard_normal()
    return A * rho + e


def years_of(n: int) -> np.ndarray:
    return np.minimum(np.arange(n) // 252, 2)


def group_noise_sd(n: np.ndarray) -> np.ndarray:
    """The sd of a group of n offers' mean noise in one session: per-offer sd 0.8 (a side-symmetric 3R value), and
    neighbouring marks' walks overlap, so a whole night holds about 6 effective offers (1 + 5 n / 186)."""
    return 0.8 / np.sqrt(1.0 + 5.0 * n / OFFERS)


def sums(mu: np.ndarray, n1: np.ndarray, delta: float, rng) -> tuple[np.ndarray, np.ndarray]:
    """(S1, S2) per session (columns replications): the in-state offers' sum and every offer's, the in-state group
    carrying a planted lift `delta`."""
    n0 = OFFERS - n1
    z1 = rng.standard_normal(mu.shape) * group_noise_sd(n1)[:, None]
    z0 = rng.standard_normal(mu.shape) * group_noise_sd(n0)[:, None]
    S1 = n1[:, None] * (mu + delta + z1)
    S2 = S1 + n0[:, None] * (mu + z0)
    return S1, S2


def centre_sums(S1, S2, n1, years):
    """Centred within years at the offer level (the twin's exact expectation): every offer less its year's mean."""
    S1, S2 = S1.copy(), S2.copy()
    for g in np.unique(years):
        m = years == g
        mean = S2[m].sum(axis=0, keepdims=True) / (OFFERS * m.sum())
        S1[m] -= n1[m][:, None] * mean
        S2[m] -= OFFERS * mean
    return S1, S2


def member_t(S1, S2, n1):
    """Each member's (t, df): the nested two-sample difference, the module's own `diff_stats` (treated df)."""
    N1 = np.broadcast_to(n1[:, None].astype(float), S1.shape)
    N2 = np.full(S1.shape, float(OFFERS))
    out = []
    for b in MEMBERS:
        est, se, df = LB.diff_stats(S1, N1, S2, N2, block=b)
        with np.errstate(invalid="ignore", divide="ignore"):
            out.append((est / se, df))
    return out


def out_of_state_floor(S1, S2, n1, years) -> np.ndarray:
    """(d): the largest |mean| over disjoint 63-session blocks of the out-of-state offers' per-session means, each
    centred by the out-of-state offers' own year mean -- no in-state offer enters, so no term of the selection's lift."""
    n0 = (OFFERS - n1).astype(float)
    So = S2 - S1
    has = n0 > 0
    m = np.where(has[:, None], So / np.where(has, n0, 1.0)[:, None], np.nan)
    for g in np.unique(years):
        k = (years == g) & has
        if k.any():
            m[k] -= np.nanmean(m[k], axis=0, keepdims=True)
    out = np.zeros(S1.shape[1])
    for b0 in range(0, S1.shape[0] - 62, 63):
        blk = m[b0:b0 + 63]
        if np.isfinite(blk).any():
            out = np.maximum(out, np.abs(np.nanmean(blk, axis=0)))
    return out


def choice_amplitude(muC: np.ndarray) -> float:
    """(a): the choice span's largest |mean| over its disjoint 63-session blocks (population values)."""
    return max(abs(float(muC[b0:b0 + 63].mean())) for b0 in range(0, muC.size - 62, 63))


def b2_quantiles(muC, n1, grid, M, seed, chunk: int = 2500) -> np.ndarray:
    """B2's (1 - level) quantile of each member's t per a* on `grid`: (len(LEVELS), len(grid), 3). A replicate: the
    choice values resampled by a stationary bootstrap (mean block 63) to the judged length, fresh offer noise, plus
    a* x a slow sign, centred within the judged years -- the real (fixed) selection."""
    rng = np.random.default_rng(seed)
    yrs = years_of(N_J)
    top = max(int(math.ceil(a * M)) for a in LEVELS) + 5
    keep = [[np.full(0, -np.inf) for _ in MEMBERS] for _ in grid]
    t_idx = np.arange(N_J)[:, None]
    done = 0
    while done < M:
        r = min(chunk, M - done)
        flags = rng.random((N_J, r)) < 1 / 63
        flags[0] = True
        starts = rng.integers(0, N_C, (N_J, r))
        begin = np.maximum.accumulate(np.where(flags, t_idx, 0), axis=0)
        idx = (np.take_along_axis(starts, begin, axis=0) + t_idx - begin) % N_C
        base = muC[idx]
        rho = np.where(rng.random(r) < 0.5, 1.0, -1.0)[None, :] * np.where(
            np.cumsum(rng.random((N_J, r)) < 1 / 63, axis=0) % 2 == 0, 1.0, -1.0)
        noise_seed = int(rng.integers(0, 2 ** 62))
        for gi, a_star in enumerate(grid):
            S1, S2 = sums(base + a_star * rho, n1, 0.0, np.random.default_rng([noise_seed, gi]))
            S1, S2 = centre_sums(S1, S2, n1, yrs)
            for mi, (tt, _df) in enumerate(member_t(S1, S2, n1)):
                v = np.concatenate([keep[gi][mi], np.where(np.isfinite(tt), tt, -np.inf)])
                keep[gi][mi] = np.partition(v, v.size - top)[-top:] if v.size > top else v
        done += r
    q = np.empty((len(LEVELS), len(grid), len(MEMBERS)))
    for li, a in enumerate(LEVELS):
        rank = int(math.ceil(a * M))
        for gi in range(len(grid)):
            for mi in range(len(MEMBERS)):
                q[li, gi, mi] = np.sort(keep[gi][mi])[::-1][rank - 1]
    # a larger slow amplitude can only widen the null: the quantile is taken non-decreasing in a* (its running maximum
    # over the grid), so Monte Carlo noise between grid points never makes a larger floor a weaker rule
    return np.maximum.accumulate(q, axis=1)


def decide(S1, S2, n1, crit_extra, level: float) -> np.ndarray:
    """`cons`, each member at the larger of its t and `crit_extra[member]` (per member, scalar or per column)."""
    ok = np.ones(S1.shape[1], dtype=bool)
    for mi, (tt, df) in enumerate(member_t(S1, S2, n1)):
        c = stats.t.ppf(1.0 - level, np.maximum(df, 1))
        if crit_extra is not None:
            c = np.maximum(c, crit_extra[mi])
        ok &= np.isfinite(tt) & (tt > c) & (df >= 1)
    return ok


SETTINGS = {
    "whole sessions, runs 21 (s3/u3), slow 0.05 / 0.05": ("daily", 0.05, 0.05, (0.25, 0.5, 1.0, 2.0)),
    "whole sessions, runs 21 (s3/u3), slow 0.05 / 0.15": ("daily", 0.05, 0.15, (0.25, 0.5, 1.0, 2.0)),
    "window, clustered across nights (s1/s2), slow 0.05 / 0.05": ("window", 0.05, 0.05, (0.05, 0.1, 0.15, 0.25)),
    "window, clustered across nights (s1/s2), slow 0.05 / 0.15": ("window", 0.05, 0.15, (0.05, 0.1, 0.15, 0.25)),
}


def setting_inputs(name: str):
    kind, A_C, A_J, deltas = SETTINGS[name]
    si = list(SETTINGS).index(name)
    rng = np.random.default_rng([SEED, 400, si, 0])
    yc = np.minimum(np.arange(N_C) // 250, 2)
    muC = slow_values(rng, N_C, A_C)
    muC = muC - np.array([muC[yc == g].mean() for g in range(3)])[yc]
    if kind == "daily":
        n1 = np.where(daily_chain(rng, N_J, 1 / 3, 21), OFFERS, 0).astype(np.int64)
    else:
        w = np.zeros(N_J)
        for t in range(1, N_J):
            w[t] = 0.7 * w[t - 1] + math.sqrt(1 - 0.49) * rng.standard_normal()
        n1 = np.rint(OFFERS * np.clip(1 / 3 + 0.25 * w, 0.0, 1.0)).astype(np.int64)
    return si, A_J, deltas, muC, n1


@pytest.mark.parametrize("name", list(SETTINGS))
def test_b2_judged_floor_level_and_power_at_the_family_level(name, M: int = 400_000, n_null: int = 200_000,
                                                             n_power: int = 4000):
    si, A_J, deltas, muC, n1 = setting_inputs(name)
    a_hat = choice_amplitude(muC)
    grid = a_hat * np.array([1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 9.0])
    t0 = time.time()
    q = b2_quantiles(muC, n1, grid, M, [SEED, 400, si, 1])
    yrs = years_of(N_J)
    lines = [f"\nB2 toy [{name}]: a_hat {a_hat:.4f}, in-state offers {int(n1.sum())} of {OFFERS * N_J}, "
             f"B2 {M} replicates per a* [{time.time() - t0:.0f} s]"]

    def judged(n_rep, delta, seed):
        r = np.random.default_rng(seed)
        mu = np.stack([slow_values(r, N_J, A_J) for _ in range(n_rep)], axis=1)
        S1, S2 = sums(mu, n1, delta, r)
        return centre_sums(S1, S2, n1, yrs)

    for li, (k, level) in enumerate(zip(KS, LEVELS)):
        chunk = 4000
        counts = np.zeros(3, dtype=np.int64)
        clipped = 0
        for c0 in range(0, n_null, chunk):
            S1, S2 = judged(min(chunk, n_null - c0), 0.0, [SEED, 400, si, 2, li, c0])
            a_d = np.maximum(a_hat, out_of_state_floor(S1, S2, n1, yrs))
            clipped += int((a_d > grid[-1]).sum())
            q_d = np.stack([np.interp(a_d, grid, q[li, :, mi]) for mi in range(3)])
            counts[0] += int(decide(S1, S2, n1, None, level).sum())
            counts[1] += int(decide(S1, S2, n1, q[li, 0, :], level).sum())
            counts[2] += int(decide(S1, S2, n1, q_d, level).sum())
        assert counts[2] <= counts[1] <= counts[0]                    # each tightening only removes rejections
        lev = [cp_ratio(int(cn), n_null, level) for cn in counts]
        lines.append(f"  k={k} level, {n_null} null judged blocks: cons {counts[0]} ({lev[0][0]:.2f}x "
                     f"[{lev[0][1]:.2f}, {lev[0][2]:.2f}]); larger-of (a) {counts[1]} ({lev[1][0]:.2f}x "
                     f"[{lev[1][1]:.2f}, {lev[1][2]:.2f}]); larger-of (a),(d) {counts[2]} ({lev[2][0]:.2f}x "
                     f"[{lev[2][1]:.2f}, {lev[2][2]:.2f}]); a* beyond the grid {clipped}")
        pw = []
        for delta in deltas:
            S1, S2 = judged(n_power, delta, [SEED, 400, si, 3, li, int(round(delta * 1000))])
            a_d = np.maximum(a_hat, out_of_state_floor(S1, S2, n1, yrs))
            q_d = np.stack([np.interp(a_d, grid, q[li, :, mi]) for mi in range(3)])
            p = [decide(S1, S2, n1, None, level).mean(), decide(S1, S2, n1, q[li, 0, :], level).mean(),
                 decide(S1, S2, n1, q_d, level).mean()]
            pw.append(f"lift {delta}: {p[0]:.3f} / {p[1]:.3f} / {p[2]:.3f}")
        lines.append(f"  k={k} power (cons / larger-of (a) / larger-of (a),(d)), {n_power} blocks each: "
                     + "; ".join(pw))
    print("\n".join(lines), flush=True)


