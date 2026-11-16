"""Q-38, Q-78 (family R's draft, first and second versions): the bracket arithmetic the draft's resolution forecast
leans on, the pass line's input forms, the clock that keeps the opening range out, and the draft's own reads line and
seeds -- on synthetic data and the draft's text only.

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

Added for the second version (Q-78; the draft's sections 0.2, 6.2-6.3, 7.3-7.4, 17 and 20.1):

  * `test_centred_values_through_placebo_selection_bound_give_the_exact_lift` -- E-035 (2)'s
    `extended.lift_bound.placebo_selection_bound` (`cons`, treated-cluster df) on the (mark, year)-centred values
    c - mu_s estimates exactly the exact-form lift L_R; on the raw c it adds the strata-composition term, which the
    clock makes non-zero (later marks admitted less, their values lower) with no selection effect at all;
  * `test_twin_designs_cancel_the_routing_selection` -- C2's form (7.4): on a routing that takes admitted offers more
    often on fast days, an UNINFORMATIVE admission's routed single-sample mean of the centred value is biased upward
    (the first version's single-sample C2 would credit the router), while the difference against a twin design under
    the same routing averages zero; `two_sample_bound`'s estimate is that difference exactly;
  * `test_the_population_reads_no_opening_window_bar` -- the clock (E-030, E-036): the population's 73 marks
    09:05-15:05, the bands `day1` (09:05-10:05, the so-far term frozen at the 08:30 mark's alert) and `day`
    (10:10-15:05, live), no used input of any population offer reading a bar of its day stamped 08:30-08:59, 10:10 the
    first mark whose live 60-minute window clears it, and Part II's `open` freeze reading nothing stamped 08:25 or
    later;
  * `test_the_draft_names_its_judged_reads` -- `extended.reader.declared_purposes` on the draft gives exactly the five
    purposes of its section 20.1, none containing a choice or fitting word;
  * `test_the_draft_seeds_are_its_own_block` -- the draft's seed table lists 20261970-20261979 once each, the reverse
    walk-forward's struck stream stated reserved and unused, 20261979 assigned to K0 and C0, and no other file under
    `prereg/` names any of them except as the taken range ("20261970-79").

Added for E-052 (the lead's addition to Q-78: the pass-line code review's M1; the draft's 6.6, A8, A10 and C0):

  * `test_twin_design_form_has_power_at_the_family_level` -- a tightening shows its power, not only its size: C2's
    twin-design form at one-sided 0.05 / 182 reaches 80 % power on a planted lift above its arithmetic MDL, and costs
    power against the expectation form on the same draws;
  * `test_k0_kills_only_an_interval_wholly_above_the_family_level` -- K0's and C0's rule at 200,000 replications (a kill
    only when the Clopper-Pearson interval lies wholly above 0.05 / 182), and its layout (a circular run of the cell's
    own counts from a seeded offset);
  * `test_the_amplitude_rule_is_stated_in_the_same_words` -- B2's amplitude rule appears once in section 8 and once in
    section 11, in the same words.

Every Monte Carlo comparison is at 4 standard errors (a two-sided 4-sigma band: about 6e-5 false failures each).

A demonstration of the declared arithmetic and of the draft's text, not the family's code: it reads no bar, no walk and
no result file. Lattice walks step +-1 (slow) or +-2 (fast) with the barriers on even sites, so a walk lands on them
exactly. Seeds `numpy.random.default_rng([20261977, j, ...])`, j = 0..9, the draft's section 17 (its build's synthetic
tests): j = 0..5 the first version's, 6 and 7 the second's, 8 and 9 E-052's.
"""
from __future__ import annotations

import math
import re
from pathlib import Path

import numpy as np
import pytest

from extended import features as F
from extended import lift_bound as LB
from extended import reader

ROOT = Path(__file__).resolve().parent.parent
DRAFT = ROOT / "prereg" / "DRAFT_F-R_resolution.md"
SEED = 20261977
SEEDS = tuple(range(20261970, 20261980))
JUDGED_PURPOSES = frozenset({"stage_C_forecast", "stage_C_judgement", "stage_C_campaign", "stage_C_scorecard",
                             "rcap_reading"})
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


# ------------------------------------------------------------------------------------------------ the second version


def _centre(values: np.ndarray, stratum: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(the values less their stratum's mean, the stratum mean at each value): the draft's y = c - mu_s (7.3)."""
    flat_s, flat_v = stratum.ravel(), values.ravel()
    ids, inv = np.unique(flat_s, return_inverse=True)
    sums = np.bincount(inv, weights=flat_v, minlength=len(ids))
    mu = (sums / np.bincount(inv, minlength=len(ids)))[inv].reshape(values.shape)
    return values - mu, mu


def _admit_per_stratum(rng, stratum: np.ndarray, counts: dict[int, int]) -> np.ndarray:
    """A placebo admission: in each stratum exactly counts[s] offers, drawn uniformly without replacement (7.2)."""
    flat = stratum.ravel()
    out = np.zeros(flat.shape, dtype=bool)
    for s, n in counts.items():
        idx = np.flatnonzero(flat == s)
        out[rng.choice(idx, size=n, replace=False)] = True
    return out.reshape(stratum.shape)


def test_centred_values_through_placebo_selection_bound_give_the_exact_lift():
    """C1's call (7.3): `placebo_selection_bound` has no strata, so the family passes the (mark, year)-centred values
    with every population offer as sample 2. Its estimate is then exactly the exact-form lift; on the raw c it is the
    lift plus the strata-composition term, which the clock makes non-zero: later marks are admitted less and their
    values are lower, so a filter with no information about the day still looks positive on the raw values."""
    rng = np.random.default_rng([SEED, 6])
    sessions, marks, years = 300, 8, 3
    year = np.repeat(np.arange(years), sessions // years)
    stratum = year[:, None] * marks + np.arange(marks)[None, :]
    c = (np.array([0.0, -0.04, 0.02])[year][:, None] - 0.03 * np.arange(marks)[None, :]
         + rng.normal(0.0, 1.0, (sessions, marks)))
    share = 0.6 - 0.06 * np.arange(marks)                          # the clock: later marks are admitted less
    admitted = rng.random((sessions, marks)) < share[None, :]
    session = np.repeat(np.arange(sessions)[:, None], marks, axis=1)
    y, mu = _centre(c, stratum)
    L = y[admitted].mean()                                          # (1 / N_F) sum over admitted of (c - mu_s)
    b = LB.placebo_selection_bound(y.ravel(), session.ravel(), admitted.ravel(), sessions, level=0.01)
    assert b.method == LB.SHIPPED == "cons" and LB.DIFF_DF_RULE == "treated"
    assert abs(b.estimate - L) < 1e-12
    raw = LB.placebo_selection_bound(c.ravel(), session.ravel(), admitted.ravel(), sessions, level=0.01)
    composition = mu[admitted].mean() - c.mean()
    assert abs(raw.estimate - (L + composition)) < 1e-12
    assert composition > 0.01                                       # the raw form credits the clock to the filter


def test_twin_designs_cancel_the_routing_selection():
    """C2's form (7.4): an admitted offer is taken only by a seat still free, and fast days free seats sooner and also
    resolve the offer sooner. On a toy where a routed admitted offer is taken with probability 0.8 on a fast day and
    0.3 on a slow one, an UNINFORMATIVE admission (a placebo with the same per-stratum counts) has a routed mean of the
    centred value well above zero -- what the first version's single-sample C2 would have credited -- while the
    difference against a twin design under the same routing averages zero. `two_sample_bound`'s estimate is exactly
    that difference of means."""
    sessions, marks, years, reps, gap = 600, 12, 3, 400, 0.3
    year = np.repeat(np.arange(years), sessions // years)
    stratum = year[:, None] * marks + np.arange(marks)[None, :]
    session = np.repeat(np.arange(sessions)[:, None], marks, axis=1)
    single, diff = np.empty(reps), np.empty(reps)
    for r in range(reps):
        rng = np.random.default_rng([SEED, 7, r])
        fast = np.empty(sessions, dtype=bool)                       # a persistent fast/slow state, stay 0.9
        fast[0] = rng.random() < 0.5
        flips = rng.random(sessions) >= 0.9
        for d in range(1, sessions):
            fast[d] = fast[d - 1] ^ flips[d]
        value = gap * np.where(fast, 1.0, -1.0)[:, None] + rng.normal(0.0, 1.0, (sessions, marks))
        y, _ = _centre(value, stratum)                              # the stratum-centred value: mean zero overall
        counts = {int(s): int(round(0.3 * (stratum == s).sum())) for s in np.unique(stratum)}
        take = np.where(fast, 0.8, 0.3)[:, None]                    # the router: fast days free seats sooner
        design = _admit_per_stratum(rng, stratum, counts) & (rng.random((sessions, marks)) < take)
        twin = _admit_per_stratum(rng, stratum, counts) & (rng.random((sessions, marks)) < take)
        single[r] = y[design].mean()
        diff[r] = y[design].mean() - y[twin].mean()
        if r == 0:
            b = LB.two_sample_bound(y[design], session[design], y[twin], session[twin], sessions, level=0.01)
            assert b.method == "cons"
            assert abs(b.estimate - diff[0]) < 1e-12
    se_single = single.std(ddof=1) / math.sqrt(reps)
    se_diff = diff.std(ddof=1) / math.sqrt(reps)
    assert single.mean() > Z * se_single and single.mean() > 0.05  # the routed single sample is biased
    assert abs(diff.mean()) <= Z * se_diff                          # the twin design removes it


def test_the_population_reads_no_opening_window_bar():
    marks = list(range(F.slot(9, 5), F.slot(15, 5) + 1, 5))
    day1 = [m for m in marks if m <= F.slot(10, 5)]
    day = [m for m in marks if m >= F.slot(10, 10)]
    assert len(marks) == 73 and len(day1) == 13 and len(day) == 60 and day1 + day == marks
    window = set(range(F.RTH_OPEN, F.OR_END))                       # the bars stamped 08:30-08:59
    assert min(window) == F.slot(8, 30) and max(window) == F.slot(8, 59)
    freeze_alert = F.slot(8, 30) - 5                                # the 08:30 mark's alert, 08:25
    frozen = set(range(freeze_alert - 61, freeze_alert))            # rv_60 reads the bars stamped t-61 .. t-1
    assert max(frozen) == F.slot(8, 24) and not frozen & window
    for m in marks:
        assert m >= F.OR_END                                        # entries, labels, IV, M, x1, x2 start at m
        if m in day:
            t = m - 5                                               # the alert: five minutes before the mark
            live = set(range(t - 61, t))
            assert min(live) >= F.OR_END and not live & window      # the live window opens at 09:00 or later
        # in `day1` the so-far term is the frozen value: no bar stamped after 08:24
    t = F.slot(10, 5) - 5                                           # at 10:05 a live window would hold 08:59
    assert F.slot(8, 59) in set(range(t - 61, t))
    for m in range(F.slot(8, 30), F.slot(9, 0) + 1, 5):             # Part II's `open` band: x3 frozen at 08:24
        assert max(frozen) < F.slot(8, 25) <= m - 5


def test_the_draft_names_its_judged_reads():
    text = DRAFT.read_text(encoding="utf-8")
    got = reader.declared_purposes(text)
    assert got == JUDGED_PURPOSES
    for p in got:
        assert not set(p.lower().split("_")) & reader.CHOICE_WORDS, p


def test_the_draft_seeds_are_its_own_block():
    text = DRAFT.read_text(encoding="utf-8")
    rows = re.findall(r"^\| (2026197\d) \|", text, flags=re.MULTILINE)
    assert sorted(int(r) for r in rows) == list(SEEDS)
    assert "**`[20261972, 1]` is reserved and unused**" in text   # the struck reverse walk-forward's stream
    assert re.search(r"^\| 20261979 \| the level at the counts \(E-052\)", text, flags=re.MULTILINE)  # K0 and C0
    assert "reverse walk-forward's beside" not in text and "fitted on the judged block and read" not in text
    pat = re.compile(r"\b2026197\d\b")
    for p in sorted((ROOT / "prereg").glob("*.md")):
        if p.name != DRAFT.name:
            other = re.sub(r"\b20261970-79\b", "", p.read_text(encoding="utf-8"))   # the taken range, named
            assert not pat.search(other), p.name


# ------------------------------------------------------------------------------------------------ E-052's addition


def test_twin_design_form_has_power_at_the_family_level():
    """E-052: a tightening shows its power at the family's level, not only its size. C2's twin-design form (7.4) pays
    for removing the routing selection with the twin's own noise. On the routing toy without a routing selection
    (every admitted offer taken with probability 1/2) and a planted lift -- the design's admitted offers better by
    delta before centring, so the centred lift is (1 - 0.3) delta -- `two_sample_bound` against two pooled twin draws
    is compared with the expectation form (`placebo_selection_bound` on the same routed uses against every offer), both
    at one-sided 0.05 / 182 (k = 13), 200 seeded draws each. By the arithmetic of 7.4 (about 1,080 design uses and 2,160
    twin uses on 600 sessions, nine 63-session blocks) the MDL is near 0.24 in lift: at delta = 0.5 (a lift of 0.35)
    both forms must reach 80 % power; at delta = 0.25 the twin-design form must have less power than the expectation
    form, and its mean lower bound must sit below the expectation form's at both deltas -- the cost on record."""
    sessions, marks, years, reps, share = 600, 12, 3, 200, 0.3
    level = LB.family_level(13)
    year = np.repeat(np.arange(years), sessions // years)
    stratum = year[:, None] * marks + np.arange(marks)[None, :]
    session = np.repeat(np.arange(sessions)[:, None], marks, axis=1)
    counts = {int(s): int(round(share * (stratum == s).sum())) for s in np.unique(stratum)}
    power, mean_lower = {}, {}
    for delta in (0.25, 0.5):
        hits = {"two": 0, "exp": 0}
        lows = {"two": [], "exp": []}
        for r in range(reps):
            rng = np.random.default_rng([SEED, 8, int(delta * 100), r])
            admitted = _admit_per_stratum(rng, stratum, counts)
            y, _ = _centre(rng.normal(0.0, 1.0, (sessions, marks)) + delta * admitted, stratum)
            design = admitted & (rng.random((sessions, marks)) < 0.5)
            twins = [_admit_per_stratum(rng, stratum, counts) & (rng.random((sessions, marks)) < 0.5) for _ in range(2)]
            y2 = np.concatenate([y[t] for t in twins])
            s2 = np.concatenate([session[t] for t in twins])
            two = LB.two_sample_bound(y[design], session[design], y2, s2, sessions, level=level)
            exp = LB.placebo_selection_bound(y.ravel(), session.ravel(), design.ravel(), sessions, level=level)
            for name, b in (("two", two), ("exp", exp)):
                low = b.lower if np.isfinite(b.lower) else -np.inf
                hits[name] += low > 0
                lows[name].append(low)
        power[delta] = {k: v / reps for k, v in hits.items()}
        mean_lower[delta] = {k: float(np.mean(v)) for k, v in lows.items()}
    assert power[0.5]["two"] >= 0.8 and power[0.5]["exp"] >= 0.8
    assert power[0.25]["two"] < power[0.25]["exp"]
    for delta in (0.25, 0.5):
        assert mean_lower[delta]["two"] < mean_lower[delta]["exp"]


def _k0_kills(rejections: int, replications: int, level: float) -> bool:
    """K0's and C0's rule (A10, C0): kill (claim no pass) only when the rejection rate's 95 % Clopper-Pearson interval
    lies wholly above the nominal level."""
    lo, _ = LB.clopper_pearson(rejections, replications)
    return lo > level


def test_k0_kills_only_an_interval_wholly_above_the_family_level():
    n = 200_000                                                     # A10's replications per cell
    level = LB.family_level(13)                                     # 0.05 / 182
    expected = level * n                                            # about 55 rejections at the nominal rate
    assert 54 < expected < 56
    assert not _k0_kills(55, n, level)                              # at nominal: kept
    assert not _k0_kills(65, n, level)                              # above nominal, but the interval reaches it
    assert _k0_kills(80, n, level)                                  # an interval wholly above: killed
    assert _k0_kills(int(2 * expected), n, level)                   # twice nominal: killed
    # the layout (A10): a consecutive run of the cell's own choice-span counts from a seeded offset, read circularly
    rng = np.random.default_rng([SEED, 9])
    choice_counts = rng.poisson(3.0, 755)
    T = 630
    offset = int(rng.integers(0, len(choice_counts)))
    laid = choice_counts[(offset + np.arange(T)) % len(choice_counts)]
    assert np.array_equal(np.diff(laid[: len(choice_counts) - offset]), np.diff(choice_counts[offset:offset + T]))
    assert laid[0] == choice_counts[offset] and len(laid) == T


def _amplitude_rules(text: str) -> list[str]:
    flat = re.sub(r"\s+", " ", text.replace("**", "").replace("\\", ""))
    return re.findall(r"\(a\) = the larger of \(a1\).*?`a\*_post`\(R\) = the larger of `a\*_pre`\(R\) and \(d\)\.", flat)


def test_the_amplitude_rule_is_stated_in_the_same_words():
    """B2's amplitude (E-047 (1)'s form), one rule stated identically in sections 8 and 11 (family B's M4-1 lesson)."""
    text = DRAFT.read_text(encoding="utf-8")
    sec8 = text[text.index("## 8. Parameters"):text.index("## 9. Stage A")]
    sec11 = text[text.index("## 11. Stage B2"):text.index("## 12. Stage C")]
    r8, r11 = _amplitude_rules(sec8), _amplitude_rules(sec11)
    assert len(r8) == 1 and len(r11) == 1
    assert r8[0] == r11[0]
    assert "`a*_pre`(R) = 3 (a)" in r11[0] and "of the pick itself and of its seeded twin draw (draw 0)" in r11[0]
