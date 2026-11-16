"""Q-29 (family B's redraft; the red team's C-1): the draft's side rule on synthetic data only.

The draft (`prereg/DRAFT_F-B_multifeature.md`, section 8) fits an L2 logistic regression -- session-weighted mean log
loss + lambda/2 ||beta||^2, the intercept free, L-BFGS-B from zero -- and turns its probability p into a side. The red
team showed that `side = sign(p - 0.5)` collapses into the training block's majority side when the features carry no
direction and lambda is large (the declared search lands there). The redraft centres the side on the training fold's
session-weighted median of its own fitted p (`p~`, pinned with the model): `side = sign(p - p~)`.

This file holds the declared rule to that on synthetic sessions (six offers each, half the columns near-daily, the
offers of a session agreeing on the outcome 85 % of the time -- the review's Appendix A design, smaller):
  * under a null signal the centred sides are balanced at every lambda of the grid, while the uncentred rule's long
    share at the grid's top edge is the majority side's (the defect, kept on record as a test);
  * under a weak planted signal the centred side recovers it with the right sign at every lambda.

**The proof is an identity, not these numbers** (the second red team's n2-2): p is a monotone function of the linear
score z = b0 + x . beta, and a weighted median that picks an element commutes with a monotone map, so
`sign(p - p~) = sign(z - z~) = sign(x . beta - median(x_train . beta))` -- the intercept, and with it the training
block's base rate, cancels exactly, whatever lambda is. `test_the_intercept_cancels_exactly` asserts the identity.
**What this file cannot show** (n2-3): it standardises each sample by its own statistics and draws its test block
like its training block, so it has no covariate shift; a judged-block imbalance from a level-dependent (`d_round`,
`atr_rel`) or trending (`ret_20d`) feature is not shown here -- C1-d's 0.9 rule and stage B's long-share report are
the guards.

It is a demonstration of a declared rule, not the family's code: it reads no bar and no file, and imports nothing of
this repository. Seeds `numpy.random.default_rng([20261968, j])`, proposed for family B's build tests (the draft's
section 19).
"""
from __future__ import annotations

import numpy as np
import pytest
from scipy.optimize import minimize

SEED = 20261968
LAMBDAS = tuple(0.25 * 10 ** (j / 2) for j in range(-2, 5))     # the draft's grid: 0.025 .. 25, seven values
D_TRAIN, D_TEST, M, P = 400, 300, 6, 20


def _sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def make(rng, n_sessions, base, beta=None):
    """Standardised features (n*M, P), labels and session ids. Without `beta`: no signal -- each session's outcome a
    coin with P(long wins) = `base`, each offer agreeing with it 85 % of the time. With `beta`: P(long wins) =
    sigmoid(logit(base) + x . beta) per offer."""
    X = rng.standard_normal((n_sessions, M, P))
    X[:, :, : P // 2] = X[:, :1, : P // 2] + 0.3 * X[:, :, : P // 2]          # half the columns near-daily
    X = (X - X.mean((0, 1))) / X.std((0, 1))
    if beta is None:
        u = rng.random(n_sessions) < base
        flip = rng.random((n_sessions, M)) < 0.15
        y = np.where(flip, ~u[:, None], u[:, None])
    else:
        z = np.log(base / (1 - base)) + X @ beta
        y = rng.random((n_sessions, M)) < _sigmoid(z)
    return X.reshape(-1, P), y.ravel().astype(float), np.repeat(np.arange(n_sessions), M)


def session_weights(sess):
    counts = np.bincount(sess)
    return 1.0 / (len(counts) * counts[sess])


def fit(X, y, sess, lam):
    """The declared objective and solver (draft section 8)."""
    w = session_weights(sess)

    def f(b):
        z = b[0] + X @ b[1:]
        g = _sigmoid(z) - y
        val = w @ (np.logaddexp(0.0, z) - y * z) + 0.5 * lam * b[1:] @ b[1:]
        return val, np.concatenate([[w @ g], X.T @ (w * g) + lam * b[1:]])

    r = minimize(f, np.zeros(X.shape[1] + 1), jac=True, method="L-BFGS-B",
                 options={"gtol": 1e-10, "maxiter": 2000})
    assert r.success, r.message
    return r.x


def weighted_median(v, w):
    o = np.argsort(v, kind="stable")
    c = np.cumsum(w[o]) / w.sum()
    return float(v[o][np.searchsorted(c, 0.5)])


def sides(b, X_train, sess_train, X_test, centred):
    p_test = _sigmoid(b[0] + X_test @ b[1:])
    if not centred:
        return np.sign(p_test - 0.5)
    p_train = _sigmoid(b[0] + X_train @ b[1:])
    return np.sign(p_test - weighted_median(p_train, session_weights(sess_train)))


@pytest.mark.parametrize("j, base", [(0, 0.53), (1, 0.51)])
def test_null_signal_gives_balanced_centred_sides(j, base):
    rng = np.random.default_rng([SEED, j])
    Xtr, ytr, str_ = make(rng, D_TRAIN, base)
    Xte, _, _ = make(rng, D_TEST, base)
    shares_centred, shares_raw = [], []
    for lam in LAMBDAS:
        b = fit(Xtr, ytr, str_, lam)
        shares_centred.append(float(np.mean(sides(b, Xtr, str_, Xte, True) > 0)))
        shares_raw.append(float(np.mean(sides(b, Xtr, str_, Xte, False) > 0)))
    assert all(0.42 <= s <= 0.58 for s in shares_centred), shares_centred
    if base == 0.53:
        # the defect the redraft removes: at the grid's top edge the uncentred side is the majority side
        assert shares_raw[-1] >= 0.85, shares_raw


def test_the_intercept_cancels_exactly():
    """sign(p - p~) equals sign(x . beta - median(x_train . beta)) on every offer, and moving the intercept by any
    amount changes no side -- the identity that makes the rule unable to collapse into the majority side."""
    rng = np.random.default_rng([SEED, 3])
    Xtr, ytr, str_ = make(rng, D_TRAIN, 0.53)
    Xte, _, _ = make(rng, D_TEST, 0.53)
    w = session_weights(str_)
    for lam in (LAMBDAS[0], LAMBDAS[-1]):
        b = fit(Xtr, ytr, str_, lam)
        by_score = np.sign(Xte @ b[1:] - weighted_median(Xtr @ b[1:], w))
        assert np.array_equal(sides(b, Xtr, str_, Xte, True), by_score)
        for shift in (-3.0, -0.5, 0.5, 3.0):
            moved = b.copy()
            moved[0] += shift
            assert np.array_equal(sides(moved, Xtr, str_, Xte, True), by_score), (lam, shift)


def test_weak_planted_signal_is_recovered_by_the_centred_side():
    rng = np.random.default_rng([SEED, 2])
    beta = np.zeros(P)
    beta[P // 2] = beta[P // 2 + 1] = 0.25                          # two offer-level columns carry direction
    Xtr, ytr, str_ = make(rng, D_TRAIN, 0.53, beta)
    Xte, yte, _ = make(rng, D_TEST, 0.53, beta)
    for lam in LAMBDAS:
        b = fit(Xtr, ytr, str_, lam)
        s = sides(b, Xtr, str_, Xte, True)
        lift = float(np.mean(s * (2 * yte - 1))) / 2                   # the coin-twin lift's form, mean(s d)
        assert lift > 0.02, (lam, lift)
        assert 0.40 <= float(np.mean(s > 0)) <= 0.60, lam
