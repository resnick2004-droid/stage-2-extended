"""Q-43 (family B's third draft; the red team's M2-2): stage B2's critical value on the red team's own synthetic design.

The draft (`prereg/DRAFT_F-B_multifeature.md`, version 3, section 12) reads every judging line by Student-t on
63-session block means of per-session values, with its critical value the larger of the nominal one and a value
simulated **conditional on the pinned model's real judged side series**. The null pair values are the choice block's own
session pair values, resampled in stationary blocks of mean 63 sessions, centred, plus a declared slow drift. That
drift is a two-state Markov sign switching with probability 1/250 per session, its amplitude the largest absolute
calendar-year mean of the choice block's pair values.

This file holds that rule to the design the review simulated (its Appendix B: 630 judged sessions, 24 offers a session,
a side regime switching about every 60 sessions with long share 0.8 / 0.2 inside it, a pair-value drift +-0.03
switching about every 120 sessions, session noise 0.30, offer noise 0.35), and to a slower stress case (regimes about
120 and 250 sessions). It works on session means; the offer-level noise is drawn at its session-mean variance. Each case:

* the defects on record: 21-session block means at their nominal value over-reject the true conditional null, and the
  second draft's run-length surrogate sets its critical value below the true conditional quantile;
* the rule: rejecting at B2's critical value holds the level, on 63-session blocks and on 21-session blocks (the
  confirmation's form).

Light (session means, 4,000 replications a case); seeds `numpy.random.default_rng([20261968, 30 + j])`, the draft's
proposed build-test seed. A demonstration of the declared rule, not the family's code: it imports nothing of this
repository and reads no file.
"""
from __future__ import annotations

import numpy as np
from scipy import stats

SEED = 20261968
TJ, TC, M = 630, 1000, 24
S_ETA, S_EPS, P_IN = 0.30, 0.35, 0.80
R = 4000
ALPHA = 0.01
STRESS_Q, STRESS_BLOCK = 1 / 250, 63
REVIEW = dict(a=0.03, q_d=1 / 120, q_s=1 / 60)
SLOWER = dict(a=0.03, q_d=1 / 250, q_s=1 / 120)


def markov(rng, q, n_rep, n):
    sw = rng.random((n_rep, n)) < q
    sw[:, 0] = rng.random(n_rep) < 0.5
    return np.where(np.cumsum(sw, axis=1) % 2 == 0, 1.0, -1.0)


def tstat(x, block):
    nb = x.shape[1] // block
    bm = x[:, : nb * block].reshape(len(x), nb, block).mean(2)
    return bm.mean(1) / (bm.std(1, ddof=1) / np.sqrt(nb)), nb


def stationary_idx(rng, n_rep, n_out, n_src, mean_block):
    idx = np.empty((n_rep, n_out), dtype=np.int64)
    idx[:, 0] = rng.integers(0, n_src, n_rep)
    new = rng.random((n_rep, n_out)) < 1.0 / mean_block
    fresh = rng.integers(0, n_src, (n_rep, n_out))
    for t in range(1, n_out):
        idx[:, t] = np.where(new[:, t], fresh[:, t], (idx[:, t - 1] + 1) % n_src)
    return idx


def one_case(j, a, q_d, q_s):
    """For one judged side series: the true conditional null's t (fresh pair values), and B2's null t (the choice
    block's pair values resampled, plus the declared drift), at 21- and 63-session blocks; and the second draft's
    run-length surrogate's t."""
    rng = np.random.default_rng([SEED, 30 + j])
    offers = np.where(rng.random((TJ, M)) < np.where(markov(rng, q_s, 1, TJ)[0] > 0, P_IN, 1 - P_IN)[:, None], 1, -1)
    A = offers.mean(1)                                                    # the judged per-session mean side
    noise = lambda: S_EPS / np.sqrt(M) * rng.standard_normal((R, TJ))     # noqa: E731
    true_x = A * (a * markov(rng, q_d, R, TJ) + S_ETA * rng.standard_normal((R, TJ))) + noise()
    choice = (a * markov(rng, q_d, 1, TC) + S_ETA * rng.standard_normal((1, TC)))[0]
    a_star = np.max(np.abs(choice[:1000].reshape(4, 250).mean(1)))      # the largest calendar-year mean
    d_star = choice[stationary_idx(rng, R, TJ, TC, STRESS_BLOCK)]
    d_star = d_star - d_star.mean(1, keepdims=True) + a_star * markov(rng, STRESS_Q, R, TJ)
    b2_x = A * d_star + noise()
    # the second draft's surrogate: signs alternating along the offers, run lengths resampled from the judged sides
    flat = offers.ravel()
    ch = np.flatnonzero(np.diff(flat) != 0)
    runs = np.diff(np.concatenate([[-1], ch, [flat.size - 1]]))
    surr = np.empty((R, TJ))
    for i in range(R):
        L = rng.choice(runs, size=int(2 * flat.size / runs.mean()) + 50)
        ends = np.cumsum(L)
        ends = ends[ends < flat.size]
        mark = np.zeros(flat.size, dtype=np.int64)
        mark[ends] = 1
        s = np.where(np.cumsum(mark) % 2 == 0, 1.0, -1.0) * (1.0 if rng.random() < 0.5 else -1.0)
        surr[i] = s.reshape(TJ, M).mean(1)
    surr_x = surr * choice[:TJ] + noise()
    out = {}
    for block in (21, 63):
        t_true, nb = tstat(true_x, block)
        t_b2, _ = tstat(b2_x, block)
        nominal = stats.t.ppf(1 - ALPHA, nb - 1)
        crit = max(nominal, float(np.quantile(t_b2, 1 - ALPHA)))
        out[block] = {"rej_nominal": float(np.mean(t_true > nominal)), "rej_b2": float(np.mean(t_true > crit)),
                      "q_true": float(np.quantile(t_true, 1 - ALPHA))}
    t_s, _ = tstat(surr_x, 21)
    out["surrogate_q"] = float(np.quantile(t_s, 1 - ALPHA))
    return out


def _pooled(cases, block, key):
    return float(np.mean([c[block][key] for c in cases]))


def test_b2_holds_the_level_where_the_review_found_the_surrogate_failing():
    cases = [one_case(j, **REVIEW) for j in range(3)]
    # the defects on record
    assert _pooled(cases, 21, "rej_nominal") >= 1.3 * ALPHA
    assert np.mean([c["surrogate_q"] for c in cases]) < np.mean([c[21]["q_true"] for c in cases])
    # the declared rule
    assert _pooled(cases, 63, "rej_b2") <= 1.25 * ALPHA
    assert _pooled(cases, 21, "rej_b2") <= 1.25 * ALPHA


def test_b2_holds_the_level_on_a_slower_stress_case():
    cases = [one_case(10 + j, **SLOWER) for j in range(2)]
    assert _pooled(cases, 21, "rej_nominal") >= 1.3 * ALPHA
    assert _pooled(cases, 63, "rej_b2") <= 1.25 * ALPHA
    assert _pooled(cases, 21, "rej_b2") <= 1.25 * ALPHA
