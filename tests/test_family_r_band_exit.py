"""Q-38 (family R's draft): the bracket arithmetic the draft's resolution forecast leans on, on synthetic walks only.

The draft (`prereg/DRAFT_F-R_resolution.md`, sections 1 and 6.4) turns a forecast of the variance a trade will see
before the walk's end into the probability that the trade is still open at the end, by the textbook exit law of a
driftless Brownian motion between two barriers (Karlin & Taylor 1975, ch. 7). In units of the stop -- the stop one unit
below the entry, the target R units above, time measured as integrated variance u in stop^2:

  * the target comes first with probability 1 / (1 + R), at any volatility;
  * the expected exit time is stop x target / variance, i.e. E[u] = R;
  * the probability the bracket is still open after u is
        Psi_R(u) = sum over odd n of 4 / (n pi) sin(n pi / (1 + R)) exp(-n^2 pi^2 u / (2 (1 + R)^2)).

And the consequence the draft's pass-line section rests on (section 1 (iv)): selecting brackets by a volatility forecast
moves the time to resolve and the share left open at a deadline -- and the share that reaches the target by it -- but
not the coin's expected gross outcome; with a cost charged on a flatten, the selection's lift over a placebo selection
of the same share is exactly that cost times the change in the open share.

What each test holds:

  * `test_series_equals_images` -- the draft's series equals an independent derivation (the method of images) to 1e-9;
  * `test_survival_limits_and_mean` -- Psi starts at 1, falls with u, rises with R, and integrates to R;
  * `test_lattice_converges_to_the_formula` -- a simple random walk's EXACT survival (its transition matrix) at a
    16-step stop is within 0.005 of Psi (the lattice error falls as 1/a^2; computed at about 0.003 before this test was
    written);
  * `test_target_first_and_mean_time_at_any_volatility` -- Monte Carlo at two volatilities: the target share is
    1/(1+R) at both, the mean exit time scales as 1/variance;
  * `test_monte_carlo_survival_matches_the_exact_lattice` -- the simulated open share at five times matches the exact
    lattice survival;
  * `test_a_volatility_forecast_selects_time_not_the_coins_outcome` -- days with persistent slow/fast regimes, the
    forecast yesterday's regime: the open share and the target share at the deadline differ by forecast exactly as the
    exact survival predicts, the mean outcome is zero in both, and with a flatten cost the selection's lift over the
    population mean (the placebo's expectation) equals the cost times the open-share difference.

Every Monte Carlo comparison is at 4 standard errors (a two-sided 4-sigma band: about 6e-5 false failures each).

A demonstration of the declared arithmetic, not the family's code: it reads no bar and no file and imports nothing of
this repository. Lattice walks step +-1 (slow) or +-2 (fast) with the barriers on even sites, so a walk lands on them
exactly. Seeds `numpy.random.default_rng([20261977, j])`, proposed for family R's build tests (the draft's section 16).
"""
from __future__ import annotations

import math

import numpy as np
import pytest

SEED = 20261977
RS = (1.0, 1.5, 3.0)                       # the table's three asks (the draft's cells)
Z = 4.0                                    # Monte Carlo band, in standard errors


# ------------------------------------------------------------------------------------------------ the formulas


def psi_series(u, R: float, n_max: int = 401, chunk: int = 20000) -> np.ndarray:
    """The draft's Psi_R(u): the probability a driftless bracket (stop 1, target R, unit variance) is still open after
    integrated variance u. The series converges fast for u not tiny; `psi` switches to the images below 0.05. At
    u >= 0.05 and R <= 3 the first omitted term (n = 403) is below exp(-2500): 401 terms are exact to machine
    precision. Evaluated `chunk` points at a time, so memory stays small (a first version built one u x n array and ran
    out of memory on the quadrature -- kept on record in the hand-back)."""
    L = 1.0 + float(R)
    n = np.arange(1, n_max + 1, 2, dtype=float)
    u = np.atleast_1d(np.asarray(u, dtype=float))
    c = 4.0 / (n * math.pi) * np.sin(n * math.pi / L)
    k = n * n * math.pi ** 2 / (2.0 * L * L)
    out = np.empty_like(u)
    for lo in range(0, len(u), chunk):
        uc = u[lo:lo + chunk]
        out[lo:lo + chunk] = (c[None, :] * np.exp(-np.outer(uc, k))).sum(axis=1)
    return out


def _Phi(x) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    return 0.5 * (1.0 + np.vectorize(math.erf)(x / math.sqrt(2.0)))


def psi_images(u, R: float, K: int = 6) -> np.ndarray:
    """The same probability by the method of images: the killed density of a Brownian motion from 0 between -1 and R is
    sum_k [phi(x - 2kL) - phi(x + 2 - 2kL)], L = 1 + R; integrated over (-1, R)."""
    a, b = 1.0, float(R)
    L = a + b
    u = np.atleast_1d(np.asarray(u, dtype=float))
    s = np.sqrt(u)
    out = np.zeros_like(u)
    for k in range(-K, K + 1):
        out += (_Phi((b - 2 * k * L) / s) - _Phi((-a - 2 * k * L) / s)
                - _Phi((b + 2 * a - 2 * k * L) / s) + _Phi((a - 2 * k * L) / s))
    return out


def psi(u, R: float) -> np.ndarray:
    u = np.atleast_1d(np.asarray(u, dtype=float))
    out = np.ones_like(u)
    small = (u > 0) & (u < 0.05)
    big = u >= 0.05
    if small.any():
        out[small] = psi_images(u[small], R)
    if big.any():
        out[big] = psi_series(u[big], R)
    return out


def lattice_survival(a: int, b: int, steps) -> dict[int, float]:
    """EXACT P(still open after t steps) of a simple +-1 random walk from 0 absorbed at -a and +b."""
    L = a + b
    p = np.zeros(L + 1)
    p[a] = 1.0
    want, out = set(int(s) for s in steps), {}
    for t in range(1, max(want) + 1):
        q = np.zeros_like(p)
        q[1:] += 0.5 * p[:-1]
        q[:-1] += 0.5 * p[1:]
        q[0] = q[L] = 0.0
        p = q
        if t in want:
            out[t] = float(p.sum())
    return out


# ------------------------------------------------------------------------------------------------ the simulator


def walk_brackets(rng, n: int, a: int, b: int, step: np.ndarray | int, deadline: int | None = None):
    """n lattice walks from 0, each stepping +-step (an array: one volatility per walk), absorbed at -a or +b (both
    multiples of every step), or stopped at `deadline` steps. Returns (kind: 0 stop, 1 target, 2 open at the deadline;
    exit step; the position at the exit)."""
    step = np.broadcast_to(np.asarray(step, dtype=np.int64), (n,)).copy()
    if ((a % step) != 0).any() or ((b % step) != 0).any():
        raise ValueError("the barriers must be multiples of every step")
    x = np.zeros(n, dtype=np.int64)
    kind = np.full(n, 2, dtype=np.int64)
    when = np.zeros(n, dtype=np.int64)
    live = np.arange(n)
    t, limit = 0, (deadline if deadline is not None else 200 * a * b)
    while live.size and t < limit:
        t += 1
        x[live] += np.where(rng.random(live.size) < 0.5, 1, -1) * step[live]
        hit_s = x[live] <= -a
        hit_t = x[live] >= b
        done = hit_s | hit_t
        kind[live[hit_s]] = 0
        kind[live[hit_t]] = 1
        when[live[done]] = t
        live = live[~done]
    when[live] = t
    if deadline is None and live.size:
        raise AssertionError("some walks never resolved")
    return kind, when, x


# ------------------------------------------------------------------------------------------------ the tests


def test_series_equals_images():
    us = np.linspace(0.06, 4.0, 60)
    for R in RS:
        assert np.max(np.abs(psi_series(us, R) - psi_images(us, R))) < 1e-9


def test_survival_limits_and_mean():
    for R in RS:
        assert psi(np.array([1e-4]), R)[0] > 1.0 - 1e-12                          # open at the start
        us = np.linspace(0.0, 30.0, 3001)
        v = psi(us, R)
        assert np.all(np.diff(v) <= 1e-15)                                         # falls with u
        uu = np.linspace(0.0, 120.0, 120001)       # step 0.001: trapezoid error ~ h^2/12 x int|Psi''| < 1e-6
        assert abs(np.trapezoid(psi(uu, R), uu) - R) < 1e-4                        # E[u] = stop x target / variance
    u = np.linspace(0.1, 10.0, 50)
    assert np.all(psi(u, 3.0) > psi(u, 1.5)) and np.all(psi(u, 1.5) > psi(u, 1.0))   # a wider target is slower


def test_lattice_converges_to_the_formula():
    a = 16
    us = (0.25, 0.5, 1.0, 2.0, 4.0)
    for R in RS:
        b = int(round(a * R))
        exact = lattice_survival(a, b, [int(u * a * a) for u in us])
        for u in us:
            assert abs(exact[int(u * a * a)] - psi(np.array([u]), R)[0]) < 0.005, (R, u)


@pytest.mark.parametrize("j, R", list(enumerate(RS)))
def test_target_first_and_mean_time_at_any_volatility(j, R):
    a, n = 8, 20000
    b = int(round(a * R))
    for k, step in enumerate((1, 2)):                                             # slow and fast: variance 1 and 4
        rng = np.random.default_rng([SEED, j, k])
        kind, when, _ = walk_brackets(rng, n, a, b, step)
        p = (kind == 1).mean()
        assert abs(p - 1.0 / (1.0 + R)) <= Z * math.sqrt(p * (1 - p) / n), (R, step, p)
        want = a * b / step ** 2                                                  # stop x target / variance
        assert abs(when.mean() - want) <= Z * when.std(ddof=1) / math.sqrt(n), (R, step, when.mean(), want)


@pytest.mark.parametrize("R", (1.0, 3.0))
def test_monte_carlo_survival_matches_the_exact_lattice(R):
    a, n = 16, 20000
    b = int(round(a * R))
    us = (0.25, 0.5, 1.0, 2.0, 4.0)
    steps = [int(u * a * a) for u in us]
    exact = lattice_survival(a, b, steps)
    rng = np.random.default_rng([SEED, 3, int(R * 10)])
    kind, when, _ = walk_brackets(rng, n, a, b, 1)
    for s in steps:
        open_ = ((kind == 2) | (when > s)).mean()
        p = exact[s]
        assert abs(open_ - p) <= Z * math.sqrt(p * (1 - p) / n) + 1e-12, (R, s, open_, p)


def test_a_volatility_forecast_selects_time_not_the_coins_outcome():
    a, R = 8, 3.0
    b = int(round(a * R))
    T = int(R * a * a)                         # the deadline: the slow regime's mean exit time
    days, stay = 40000, 0.9                    # a persistent two-state volatility (stationary half and half)
    rng = np.random.default_rng([SEED, 4])
    fast = np.empty(days, dtype=bool)
    fast[0] = rng.random() < 0.5
    flips = rng.random(days) >= stay
    for d in range(1, days):
        fast[d] = fast[d - 1] ^ flips[d]
    kind, _, x = walk_brackets(np.random.default_rng([SEED, 5]), days, a, b, np.where(fast, 2, 1), deadline=T)
    outcome = np.where(kind == 1, R, np.where(kind == 0, -1.0, x / a))         # stop units; a flatten at its position
    forecast_fast = np.r_[False, fast[:-1]]    # the forecast: yesterday's regime (the first day has none)
    sel, rest = forecast_fast[1:], ~forecast_fast[1:]
    out, kd, fs = outcome[1:], kind[1:], fast[1:]

    # what the exact survival predicts: a slow day is open at T with Psi_slow, a fast day (four times the variance)
    # with Psi_fast; a forecast-fast day is fast with probability `stay`
    p_slow = lattice_survival(a, b, [T])[T]
    p_fast = lattice_survival(a // 2, b // 2, [T])[T]
    want_gap = (2 * stay - 1) * (p_slow - p_fast)
    open_sel, open_rest = (kd[sel] == 2).mean(), (kd[rest] == 2).mean()
    se = math.sqrt(open_sel * (1 - open_sel) / sel.sum() + open_rest * (1 - open_rest) / rest.sum())
    assert open_rest - open_sel > 0.15                                            # the forecast sorts the open share
    assert abs((open_rest - open_sel) - want_gap) <= Z * se, (open_rest - open_sel, want_gap)

    # the share reaching the target by the deadline moves too -- it is not the measure of value
    tgt_sel, tgt_rest = (kd[sel] == 1).mean(), (kd[rest] == 1).mean()
    se_t = math.sqrt(tgt_sel * (1 - tgt_sel) / sel.sum() + tgt_rest * (1 - tgt_rest) / rest.sum())
    assert tgt_sel - tgt_rest > Z * se_t

    # ... while the expected outcome is zero on either side of the forecast (no direction; optional stopping)
    for g in (sel, rest):
        assert abs(out[g].mean()) <= Z * out[g].std(ddof=1) / math.sqrt(g.sum())

    # with a cost charged on a flatten, the selection's lift over the population mean -- the placebo selection's
    # expectation at the same share -- is the cost times the open-share difference, and nothing else
    cost = 0.1
    net = out - cost * (kd == 2)
    lift = net[sel].mean() - net.mean()
    want_lift = cost * ((kd == 2).mean() - open_sel) + (out[sel].mean() - out.mean())
    assert abs(lift - want_lift) < 1e-12                                          # an identity of the estimand
    se_l = math.sqrt(net[sel].var(ddof=1) / sel.sum() + net.var(ddof=1) / len(net))
    assert abs(lift - cost * ((kd == 2).mean() - open_sel)) <= Z * se_l           # the outcome part is noise
    assert lift > 0
    assert fs[sel].mean() > 0.85 and fs[rest].mean() < 0.15                       # the forecast is informative
