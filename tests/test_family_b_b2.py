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

**Added for the fifth draft** (the fourth review), seeds `[20261968, 64..67, 80..85, 90..95]`:

* `cons_bound_with_critical`, the reference for the build's named wrapper (n4-3): `lift_bound.bound("cons")` exactly
  at nominal critical values, a lower bound when B2 raises them;
* **C1-f's amplitude (M4-1):** with a choice-block amplitude near zero and a judged one above it, the fourth draft's
  rule (B2 at three times the choice block's amplitude) over-rejects, and the fifth's -- the larger also of B2 at the
  twin's largest absolute judged calendar-year lift, read after the judgement -- holds the level;
* **the symmetric slow component (m4-4):** a model whose own lift follows an independent slow regime defeats B2
  with the twin's component only, not B2 with both;
* **C2's routing (M4-2):** the model's own routing selects on its same-day outcomes and biases the routed mean under
  the null (the fourth review's check H), the coin-sided routing does not -- why C2's line takes the lesser;
* **the confirmation (m4-3):** `t21w` at 126 sessions and one-sided 0.05, at the larger of 1.3 times nominal and B2
  over the development window, holds the level pooled and within 1.5 times it for every side series.
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


# --------------------------------------------------------------- the fifth draft: M4-1, m4-4, M4-2, m4-3, n4-3

COMPONENTS = (21, 42, 63)


def cons_bound_with_critical(x, session, n_sessions, level, critical=None):
    """The reference for the build's wrapper (the fourth review's n4-3): `cons` (`lift_bound.SHIPPED`) on one sample,
    each component's critical value the larger of its nominal t and `critical[b]` (B2's), the bound their minimum.
    Returns (lower bound, rejects). With `critical=None` it is `lift_bound.bound("cons", ...)` exactly."""
    S, N = LB.session_sums(x, session, n_sessions)
    lows = []
    for b in COMPONENTS:
        est, se, df = (float(v) for v in LB.t_stats(S, N, block=b, weight="trades"))
        crit = float(stats.t.ppf(1 - level, df))
        if critical is not None:
            crit = max(crit, float(critical[b]))
        lows.append(est - crit * se)
    low = min(lows)
    return low, bool(low > 0)


def test_the_critical_value_wrapper():
    rng = np.random.default_rng([SEED, 64])
    n = 300
    session = np.repeat(np.arange(n), 5)
    x = 0.05 + rng.standard_normal(session.size)
    ref = LB.bound("cons", x, session, n, level=0.01)
    low, rej = cons_bound_with_critical(x, session, n, 0.01)
    assert np.isclose(low, ref.lower, rtol=0, atol=1e-12) and rej == ref.rejects
    higher = {b: 10.0 for b in COMPONENTS}
    low2, _ = cons_bound_with_critical(x, session, n, 0.01, higher)
    assert low2 < low                                            # a critical value above nominal lowers the bound


def component_t(x):
    """(t, df) of `cons`'s three components on per-session values x (R, n), one value a session."""
    S = x.T
    N = np.ones_like(S)
    out = {}
    for b in COMPONENTS:
        est, se, df = LB.t_stats(S, N, block=b, weight="trades")
        out[b] = (est / se, int(df[0]))
    return out


def follow_null_quantiles(rng, grid, n_rep, *, symmetric=False):
    """B2's (1 - ALPHA) quantile of each component at each follow amplitude g of `grid`: the null C1-f values with the
    twin's slow component centred at its expectation and, if `symmetric`, the model's own independent one too."""
    q = {}
    for g in grid:
        gt = g * (1.0 + markov(rng, 1 / 250, n_rep, FOLLOW_N))
        slow = -2 * FOLLOW_Q_DIS * (gt - g)
        if symmetric:
            ht = g * (1.0 + markov(rng, 1 / 250, n_rep, FOLLOW_N))
            slow = slow + 2 * FOLLOW_Q_DIS * (ht - g)
        x = slow + FOLLOW_SIG * rng.standard_normal((n_rep, FOLLOW_N))
        q[g] = {b: float(np.quantile(t, 1 - ALPHA)) for b, (t, _) in component_t(x).items()}
    return q


def _rate(t_by_b, crit_rows):
    """`cons`'s rejection rate: each replicate's components against its own critical values (rows of crit_rows)."""
    rej = np.ones(len(crit_rows), dtype=bool)
    for k, b in enumerate(COMPONENTS):
        rej &= t_by_b[b][0] > crit_rows[:, k]
    return float(rej.mean())


def test_c1f_amplitude_rule_with_the_judged_block_term():
    """M4-1: a choice block whose follow amplitude is near zero, a judged block where it is not (the twin's lift a
    slow two-state process, the model's constant, equal on average: C1-f's boundary null). B2 with the symmetric slow
    component throughout. Three rules for C1-f's critical value:

    * the fourth draft's -- B2 at three times the choice block's amplitude -- over-rejects;
    * the review's remedy alone -- also B2 at the twin's largest absolute judged calendar-year lift -- still
      over-rejects, in the replicates where the twin's lift sat low through all the judged years;
    * the fifth draft's -- that term taken over the twin's **and the model's own** judged yearly lifts, both read after
      the judgement, both able only to raise the critical value -- holds the level."""
    rng = np.random.default_rng([SEED, 65])
    g_judged, a_choice = 0.03, 0.002
    g_pre = 3 * a_choice
    grid = np.round(np.arange(0.004, 0.0801, 0.004), 4)
    q = follow_null_quantiles(rng, np.r_[g_pre, grid], R, symmetric=True)
    gt = g_judged * (1.0 + markov(rng, 1 / 250, R, FOLLOW_N))
    truth = -2 * FOLLOW_Q_DIS * (gt - g_judged) + FOLLOW_SIG * rng.standard_normal((R, FOLLOW_N))
    twin_obs = gt + FOLLOW_SIG * rng.standard_normal((R, FOLLOW_N))
    model_obs = g_judged + FOLLOW_SIG * rng.standard_normal((R, FOLLOW_N))
    years = (slice(0, 252), slice(252, 504), slice(504, FOLLOW_N))

    def yearly_max(obs):
        return np.max(np.abs(np.stack([obs[:, y].mean(1) for y in years], 1)), 1)

    t_by_b = component_t(truth)
    nominal = np.array([stats.t.ppf(1 - ALPHA, t_by_b[b][1]) for b in COMPONENTS])
    pre = np.maximum(nominal, [q[g_pre][b] for b in COMPONENTS])

    def rows(d_term):
        idx = np.minimum(np.searchsorted(grid, np.maximum(g_pre, d_term) - 1e-12), len(grid) - 1)   # rounded up
        return np.maximum(pre, np.array([[q[grid[i]][b] for b in COMPONENTS] for i in idx]))

    assert _rate(t_by_b, np.tile(pre, (R, 1))) >= 2 * ALPHA                          # the fourth draft's rule
    assert _rate(t_by_b, rows(yearly_max(twin_obs))) >= 2 * ALPHA                    # the twin's term alone
    assert _rate(t_by_b, rows(np.maximum(yearly_max(twin_obs), yearly_max(model_obs)))) <= 1.25 * ALPHA


def test_c1f_symmetric_slow_component():
    """m4-4: the model's own lift follows an independent slow regime of the twin's amplitude. B2 with both slow
    components holds the level; with the twin's only it rejects more (at this amplitude; at larger ones the difference
    vanishes -- the scratch check m45_sym.py)."""
    rng = np.random.default_rng([SEED, 66])
    g = 0.03
    gt = g * (1.0 + markov(rng, 1 / 250, R, FOLLOW_N))
    ht = g * (1.0 + markov(rng, 1 / 250, R, FOLLOW_N))
    truth = 2 * FOLLOW_Q_DIS * ((ht - g) - (gt - g)) + FOLLOW_SIG * rng.standard_normal((R, FOLLOW_N))
    t_by_b = component_t(truth)
    nominal = np.array([stats.t.ppf(1 - ALPHA, t_by_b[b][1]) for b in COMPONENTS])
    rate = {}
    for symmetric in (False, True):
        qq = follow_null_quantiles(rng, [g], R, symmetric=symmetric)[g]
        rate[symmetric] = _rate(t_by_b, np.tile(np.maximum(nominal, [qq[b] for b in COMPONENTS]), (R, 1)))
    assert rate[True] <= 1.25 * ALPHA, rate
    assert rate[False] > rate[True], rate


def routed_means(rng, n_rep, rho, stop, *, coin=False):
    """M4-2 (the fourth review's check H): 609 sessions of 24 offers, pair values with intra-session correlation rho,
    uninformative sides constant within a session; a router takes offers in order and ends a session's trading once
    the cumulative of the routed side's outcome reaches -stop. The model's design routes on its own s d; the coin's
    design (coin=True) on a fair coin's s' d. Returns per replicate the routed mean of the model's s d and the mean
    over all offers."""
    n, m = FOLLOW_N, 24
    d = 0.3 * (np.sqrt(rho) * rng.standard_normal((n_rep, n, 1)) + np.sqrt(1 - rho) * rng.standard_normal((n_rep, n, m)))
    s = np.where(rng.random((n_rep, n, 1)) < 0.5, 1.0, -1.0)
    sd = s * d
    driver = (np.where(rng.random((n_rep, n, m)) < 0.5, 1.0, -1.0) * d) if coin else sd
    cum = np.cumsum(driver, axis=2)
    hit = cum <= -stop
    first = np.where(hit.any(2), hit.argmax(2), m - 1)
    mask = np.arange(m)[None, None, :] <= first[..., None]
    return (sd * mask).sum((1, 2)) / mask.sum((1, 2)), sd.mean((1, 2))


def test_c2_routing_selection_is_why_the_line_takes_the_lesser():
    rng = np.random.default_rng([SEED, 67])
    own, every = routed_means(rng, 200, 0.2, 0.6)
    coin, _ = routed_means(rng, 200, 0.2, 0.6, coin=True)
    assert own.mean() > 0.03                       # the model's own routing selects on its own same-day outcomes
    assert abs(coin.mean()) < 0.01 and abs(every.mean()) < 0.01


def confirmation_case(j, a, q_d, q_s, *, n_sessions=126, level=0.05, n_rep=2000, dev=1630, floor=1.3):
    """m4-3: the confirmation's form -- `t21w` on a short window at one-sided 0.05, its critical value the larger of
    `floor` x nominal and B2's, B2 resampling the development window (2020-2026, every year read by then) with `a*`
    its largest absolute calendar-year mean. Returns the true conditional rejection rate for one side series."""
    rng = np.random.default_rng([SEED, 80 + j])
    offers = np.where(rng.random((n_sessions, M)) < np.where(markov(rng, q_s, 1, n_sessions)[0] > 0, P_IN, 1 - P_IN)[:, None],
                      1, -1)
    A = offers.mean(1)
    noise = lambda: S_EPS / np.sqrt(M) * rng.standard_normal((n_rep, n_sessions))   # noqa: E731
    truth = A * (a * markov(rng, q_d, n_rep, n_sessions) + S_ETA * rng.standard_normal((n_rep, n_sessions))) + noise()
    devd = (a * markov(rng, q_d, 1, dev) + S_ETA * rng.standard_normal((1, dev)))[0]
    a_star = np.max(np.abs(devd[: (dev // 252) * 252].reshape(-1, 252).mean(1)))
    dd = devd[stationary_idx(rng, n_rep, n_sessions, dev, STRESS_BLOCK)]
    dd = dd - dd.mean(1, keepdims=True) + a_star * markov(rng, STRESS_Q, n_rep, n_sessions)
    t_true, nb = tstat(truth, 21)
    t_b2, _ = tstat(A * dd + noise(), 21)
    crit = max(floor * stats.t.ppf(1 - level, nb - 1), float(np.quantile(t_b2, 1 - level)))
    return float(np.mean(t_true > crit))


def test_the_confirmation_form_at_its_length_and_level():
    rates = [confirmation_case(j, **REVIEW) for j in range(6)] + [confirmation_case(10 + j, **SLOWER) for j in range(6)]
    assert np.mean(rates) <= 1.25 * 0.05
    assert max(rates) <= 1.5 * 0.05
