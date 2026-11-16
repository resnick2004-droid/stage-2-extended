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
proposed build-test seed. A demonstration of the declared rule, not the family's code: it reads no file.

**Added for the fourth draft** (the third review's M3-1), under the shipped statistic `cons`
(`extended.lift_bound.SHIPPED`: the trade-weighted session-cluster t on 21-, 42- and 63-session blocks, all three
required, here with each component's critical value the larger of its nominal one and B2's), seeds
`[20261968, 60 + j]`:

* **C1-f's boundary null** (the review's check C2: the twin's lift a two-state process between 0 and twice its mean,
  switching 1/250 a session, the model's lift constant and equal to it on average, the model disagreeing with the
  twin on 40 % of offers, session sd 0.13, 609 judged sessions): `cons` at its nominal values over-rejects; B2 with the
  follow component **centred at its expectation** `(g_t - g*) f` and **an amplitude no smaller than the judged one**
  holds the level; at half the judged amplitude, or with the third draft's recentring of the statistic, it does not;
* **C2's dollar-weighted form**: per-offer values weighted by the value map's four place values (fixed weights, the
  review's persistent sides and drift): B2 holds `cons`'s level where its nominal value over-rejects.
"""
from __future__ import annotations

import numpy as np
from scipy import stats

from extended import lift_bound as LB

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


# ------------------------------------------------------------------- the fourth draft: cons, C1-f and C2 (M3-1)

FOLLOW_N, FOLLOW_Q_DIS, FOLLOW_SIG = 609, 0.4, 0.13
PLACE_DV = np.array([225.0, 1426.0, 629.0, 665.0])        # u_value_map.csv's p14 mean_dv at (b), (c), (d), (e)
PLACE_P = np.array([0.40, 0.05, 0.30, 0.25])              # a routing mix (assumed; fixed weights)


def cons_rate(true_x, null_x=None, *, recentre=False, n_trades=None):
    """`cons`'s rejection rate over the replications of `true_x` (R, n) -- every component (t21w, t42w, t63w by
    `lift_bound.t_stats`) must reject, each at the larger of its nominal t and, if given, B2's (1 - ALPHA) quantile of
    the same component over `null_x`. `n_trades`: offers per session (default one value a session)."""
    S_t = true_x.T
    N_t = np.ones_like(S_t) if n_trades is None else np.full_like(S_t, float(n_trades))
    rej = np.ones(true_x.shape[0], dtype=bool)
    for b in (21, 42, 63):
        est, se, df = LB.t_stats(S_t, N_t, block=b, weight="trades")
        crit = stats.t.ppf(1 - ALPHA, df[0])
        if null_x is not None:
            S_n = null_x.T
            e2, s2, _ = LB.t_stats(S_n, np.ones_like(S_n) if n_trades is None else np.full_like(S_n, float(n_trades)),
                                   block=b, weight="trades")
            tn = e2 / s2
            if recentre:
                tn = tn - tn.mean()
            crit = max(crit, float(np.quantile(tn, 1 - ALPHA)))
        rej &= (est / se) > crit
    return float(rej.mean())


def follow_x(rng, n_rep, g_amp, centred):
    """Per-session C1-f values at the boundary null: the twin's lift g_t in {0, 2 g_amp} (mean g_amp, switching 1/250),
    the model's lift constant at g_amp, so a session's value is -2 q (g_t - g_amp) plus noise; `centred=False` is the
    third draft's uncentred component."""
    g = g_amp * (1.0 + markov(rng, 1 / 250, n_rep, FOLLOW_N))
    return -2 * FOLLOW_Q_DIS * (g - (g_amp if centred else 0.0)) + FOLLOW_SIG * rng.standard_normal((n_rep, FOLLOW_N))


def test_c1f_follow_component_centred_and_no_smaller_than_the_judged_amplitude():
    rng = np.random.default_rng([SEED, 60])
    for g in (0.02, 0.03):
        truth = follow_x(rng, R, g, True)
        assert cons_rate(truth) >= 2 * ALPHA                                         # the nominal over-rejects
        assert cons_rate(truth, follow_x(rng, R, g, True)) <= 1.25 * ALPHA            # B2 as declared
        assert cons_rate(truth, follow_x(rng, R, g / 2, True)) >= 1.5 * ALPHA         # too small an amplitude
    truth = follow_x(rng, R, 0.03, True)
    assert cons_rate(truth, follow_x(rng, R, 0.03, False), recentre=True) >= 1.5 * ALPHA   # v3's recentring


def c2_case(j, a, q_d, q_s):
    """C2's per-session dollar sums under H0 (fresh pair values) and under B2's null, for one judged side series and
    one fixed set of place weights."""
    rng = np.random.default_rng([SEED, 61 + j])
    sides = np.where(rng.random((FOLLOW_N, M)) < np.where(markov(rng, q_s, 1, FOLLOW_N)[0] > 0, P_IN, 1 - P_IN)[:, None],
                     1.0, -1.0)
    w = PLACE_DV[rng.choice(4, size=(FOLLOW_N, M), p=PLACE_P)]
    aw, nw = (w * sides).sum(1), S_EPS * np.sqrt((w ** 2).sum(1))
    truth = aw * (a * markov(rng, q_d, R, FOLLOW_N) + S_ETA * rng.standard_normal((R, FOLLOW_N)))         + nw * rng.standard_normal((R, FOLLOW_N))
    choice = (a * markov(rng, q_d, 1, TC) + S_ETA * rng.standard_normal((1, TC)))[0]
    a_star = np.max(np.abs(choice[:1000].reshape(4, 250).mean(1)))
    d = choice[stationary_idx(rng, R, FOLLOW_N, TC, STRESS_BLOCK)]
    d = d - d.mean(1, keepdims=True) + a_star * markov(rng, STRESS_Q, R, FOLLOW_N)
    null = aw * d + nw * rng.standard_normal((R, FOLLOW_N))
    return cons_rate(truth, n_trades=M), cons_rate(truth, null, n_trades=M)


def test_c2_weighted_form_holds_under_b2():
    rates = [c2_case(0, **REVIEW), c2_case(1, **REVIEW), c2_case(2, **SLOWER)]
    assert rates[2][0] >= 1.3 * ALPHA                       # the slower case: cons's nominal values over-reject
    assert all(b2 <= 1.25 * ALPHA for _, b2 in rates), rates
