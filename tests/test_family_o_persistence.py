"""Q-37, Q-63 (family O's draft, first and second versions): the bracket arithmetic, the twin's estimand, the pass
line's input form, the wait's calendar and the clock the draft leans on, on synthetic walks only.

The draft (`prereg/DRAFT_F-O_opening_timing.md`, sections 1, 6 and 7) times the funded account's 3R opening by a
side-free state and keeps the coin's side. Its case rests on four facts it states before anything is read:

  * **no memory, no lift** -- on a driftless walk a coin-sided bracket wins 1 / (1 + R) on either side, so a filter
    that keeps the coin's side can earn nothing on a martingale (scout's note 3.1 (i));
  * **persistence acts at 3R and cannot act at 1R** -- with moves that persist the side-symmetric 3R win rate rises
    above 1/4 and with moves that revert it falls below; at R = 1 the long and the short of one path are mirror images,
    so the side-symmetric value of every resolved path is exactly zero whatever the path's memory (3.1 (iii));
  * **a fixed drift splits the halves** -- a drift moves the long and the short 3R win rates apart at first order and
    their mean only at second order, so a lift carried by one half is drift, not persistence (the draft's C3);
  * **the twin's exact form** -- the lift over the placebo-selection twin (E-023 (2)) computed as the in-state offers'
    mean less their strata's means is exactly the expectation of the drawn twin's difference; it is zero for a state
    that carries no information and positive for one that picks persistent sessions (the draft's section 7).

And two facts about the draft's own text: its population's latest alert reads no bar of the 08:30-08:59 window (E-030),
and its `Judged-block reads:` line names the purposes the reader will be asked for (E-026), none of them a choice or
fitting purpose, with its seeds the block 20261980-20261989 proposed for it.

What each test holds:

  * `test_driftless_walk_wins_one_over_one_plus_r` -- exact (a linear solve): a simple random walk's long and short
    target-first probabilities are 1 / (1 + R) at R = 1, 1.5 and 3, to 1e-12;
  * `test_persistence_lifts_3r_and_reversion_lowers_it` -- exact, on the persistent random walk (each step repeats the
    previous step's sign with probability p): above 1/4 and rising for p > 1/2, below and falling for p < 1/2, the
    long and short equal (the walk is symmetric), the expected gross 4P - 1 of the sign of p - 1/2;
  * `test_one_r_sides_are_mirror_images_on_every_path` -- Monte Carlo paths of a persistent walk: at R = 1 the long's
    and the short's gross outcomes cancel on every resolved path, and the exact chain gives 1/2 at every p;
  * `test_a_fixed_drift_splits_the_halves` -- exact gambler's ruin with a small drift: the halves split at first order,
    their mean moves by less than a tenth of the split;
  * `test_placebo_twin_exact_form_is_the_drawn_twins_mean` -- synthetic sessions with persistent and calm regimes: the
    exact lift equals the mean of 2,000 seeded placebo draws within 4 standard errors; its noise-free part is exactly
    the in-state offers' excess share of persistent sessions, stratum by stratum, times the regimes' gap (positive for
    a state that sees the regime); and over 400 fresh noise draws the realised lift averages that part;
  * `test_an_uninformative_state_has_no_lift` -- 400 seeded states independent of the regimes: their exact lifts
    average zero within 4 standard errors;
  * `test_centred_values_through_placebo_selection_bound_give_the_exact_lift` (second version, review F1) -- Q-16's
    `extended.lift_bound.placebo_selection_bound` (`cons`, treated-cluster df) on the stratum-centred values c - mu_g
    estimates exactly the exact-form lift; on the raw c it adds the strata-composition term, non-zero when the firing
    share differs by year;
  * `test_an_ordered_calendar_keeps_the_wait_an_independent_one_destroys` (second version, review F2) -- a persistent
    daily state: the fallback share at W = 5 in history's order is more than twice that on independently drawn days,
    which is about (2/3)^5;
  * `test_rolling_third_fires_on_a_third_and_reads_only_the_past` -- the draft's mid-rank share over the 250 prior
    sessions (at least 120): on an iid series its top third fires on about a third of days (4 standard errors), and a
    day's state is unchanged when every later value is replaced;
  * `test_the_population_reads_no_opening_window_bar` -- the clock: the population's marks 17:00-08:25 CT, their alerts
    five minutes earlier, the last bar read stamped before 08:30 at every mark;
  * `test_the_draft_names_its_judged_reads` -- `extended.reader.declared_purposes` on the draft gives exactly the four
    purposes of its section 19.1, none containing a choice or fitting word;
  * `test_the_draft_seeds_are_its_own_block` -- the draft's seed table lists 20261980-20261989 once each, and no other
    file under `prereg/` names any of them.

A demonstration of the declared arithmetic and of the draft's text, not the family's code: it reads no bar, no walk and
no result file. Seeds `numpy.random.default_rng([20261988, j, ...])`, the draft's section 16 (its build's synthetic
tests).
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pytest

from extended import features as F
from extended import reader

ROOT = Path(__file__).resolve().parent.parent
DRAFT = ROOT / "prereg" / "DRAFT_F-O_opening_timing.md"
SEED = 20261988
Z = 4.0                                    # Monte Carlo band, in standard errors
A = 10                                     # the stop, in lattice steps (the bracket's -1R)
JUDGED_PURPOSES = frozenset({"stage_C_states", "stage_C_judgement", "stage_C_campaign", "stage_C_scorecard"})
SEEDS = frozenset(range(20261980, 20261990))


# ------------------------------------------------------------------------------------------------ the exact chains


def target_first(a: int, b: int, p: float) -> float:
    """EXACT P(the walk from 0 reaches +b before -a) for the persistent random walk: the first step is a fair coin,
    each later step repeats the previous step's sign with probability p (p = 1/2 is the simple random walk). A linear
    solve over the states (position, last step's sign), absorbing at -a and +b."""
    inner = list(range(-a + 1, b))
    idx = {(x, s): i for i, (x, s) in enumerate((x, s) for x in inner for s in (1, -1))}
    n = len(idx)
    M = np.eye(n)
    rhs = np.zeros(n)
    for (x, s), i in idx.items():
        for step, w in ((s, p), (-s, 1.0 - p)):
            y = x + step
            if y >= b:
                rhs[i] += w
            elif y > -a:
                M[i, idx[(y, step)]] -= w
    h = np.linalg.solve(M, rhs)

    def H(y: int, s: int) -> float:
        return 1.0 if y >= b else 0.0 if y <= -a else float(h[idx[(y, s)]])

    return 0.5 * H(1, 1) + 0.5 * H(-1, -1)


def long_short(a: int, b: int, p: float) -> tuple[float, float]:
    """(the long's, the short's) target-first probability: the long's target is +b and its stop -a; the short's target
    is -b and its stop +a, so the short wins when the walk reaches -b before +a = 1 - P(+a before -b) -- computed on
    the chain, not taken from the reflection."""
    return target_first(a, b, p), 1.0 - target_first(b, a, p)


def ruin(a: int, b: int, q: float) -> float:
    """EXACT P(a simple walk with up-probability q, from 0, reaches +b before -a) -- the gambler's ruin."""
    if abs(q - 0.5) < 1e-15:
        return a / (a + b)
    r = (1.0 - q) / q
    return (1.0 - r ** a) / (1.0 - r ** (a + b))


# ------------------------------------------------------------------------------------------------ the geometry


@pytest.mark.parametrize("R", [1.0, 1.5, 3.0])
def test_driftless_walk_wins_one_over_one_plus_r(R):
    b = int(round(A * R))
    pl, ps = long_short(A, b, 0.5)
    assert abs(pl - 1.0 / (1.0 + R)) < 1e-12
    assert abs(ps - 1.0 / (1.0 + R)) < 1e-12
    assert abs(ruin(A, b, 0.5) - 1.0 / (1.0 + R)) < 1e-12


def test_persistence_lifts_3r_and_reversion_lowers_it():
    b = 3 * A
    ps_ = (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8)
    win = [target_first(A, b, p) for p in ps_]
    assert abs(win[3] - 0.25) < 1e-12                               # the martingale: exactly 1/4
    assert all(x < y for x, y in zip(win, win[1:]))                 # rising in the persistence
    for p, w in zip(ps_, win):
        gross = 4.0 * w - 1.0                                       # 3 x P(target) - 1 x P(stop), every path resolves
        if p > 0.5:
            assert w > 0.25 and gross > 0
        elif p < 0.5:
            assert w < 0.25 and gross < 0
    # the long and the short are the same question on a symmetric walk (checked on the chain, not assumed)
    for p in ps_:
        up = target_first(A, b, p)
        # the short's target first = the long walk reaching -b before +a = 1 - P(+a before -b)
        down = 1.0 - target_first(b, A, p)
        assert abs(up - down) < 1e-12


def _persistent_paths(rng, n: int, p: float, a: int, b: int, max_steps: int):
    """n persistent walks from 0; returns the long bracket's kind per path (1 target +b, 0 stop -a, 2 open) and the
    short bracket's (1 target -b, 0 stop +a, 2 open)."""
    x = np.zeros(n, dtype=np.int64)
    last = np.where(rng.random(n) < 0.5, 1, -1)
    x += last
    lk = np.full(n, 2)
    sk = np.full(n, 2)
    for _ in range(max_steps):
        lk = np.where((lk == 2) & (x >= b), 1, np.where((lk == 2) & (x <= -a), 0, lk))
        sk = np.where((sk == 2) & (x <= -b), 1, np.where((sk == 2) & (x >= a), 0, sk))
        if not ((lk == 2) | (sk == 2)).any():
            break
        last = np.where(rng.random(n) < p, last, -last)
        x = x + last
    return lk, sk


@pytest.mark.parametrize("j,p", [(0, 0.3), (1, 0.5), (2, 0.75)])
def test_one_r_sides_are_mirror_images_on_every_path(j, p):
    rng = np.random.default_rng([SEED, 0, j])
    lk, sk = _persistent_paths(rng, 4000, p, A, A, 20000)
    done = (lk != 2) & (sk != 2)
    assert done.mean() > 0.999
    gross_long = np.where(lk == 1, 1.0, -1.0)[done]
    gross_short = np.where(sk == 1, 1.0, -1.0)[done]
    assert np.array_equal(gross_long + gross_short, np.zeros(done.sum()))       # every path: exactly one side wins
    assert abs(target_first(A, A, p) - 0.5) < 1e-12


def test_a_fixed_drift_splits_the_halves():
    b = 3 * A
    for q in (0.505, 0.51):
        pl = ruin(A, b, q)                         # the long: +b before -a under an upward drift
        ps = 1.0 - ruin(b, A, q)                   # the short: -b before +a = 1 - P(+a before -b)
        split = pl - ps
        mean_dev = 0.5 * (pl + ps) - 0.25
        assert pl > 0.25 > ps                      # first order: the drift helps one half and hurts the other
        assert 0.0 < mean_dev < 0.1 * split        # second order: the side-symmetric mean barely moves (and up)


# ------------------------------------------------------------------------------------------------ the twin


#: the two regimes' expected side-symmetric 3R gross (stop A steps, target 3A): calm the martingale's 0, persistent the
#: persistent walk's at a repeat probability of 0.65 -- small: persistence at the step's scale moves a bracket ten steps
#: wide only a little, which is why the draft's mechanism needs persistence at the bracket's own scale (hours)
REGIME_MEANS = np.array([4.0 * target_first(A, 3 * A, 0.5) - 1.0, 4.0 * target_first(A, 3 * A, 0.65) - 1.0])


def _population(rng, sessions: int = 300, marks: int = 6, years: int = 3):
    """Synthetic offers: sessions in `years` equal years, `marks` marks a session, a session regime (persistent with
    probability of staying 0.9 a session); each offer's side-symmetric 3R value is its regime's expectation (`m`, the
    noise-free part) plus unit noise (`c`)."""
    reg = np.zeros(sessions, dtype=int)
    reg[0] = int(rng.random() < 0.5)
    for s in range(1, sessions):
        reg[s] = reg[s - 1] if rng.random() < 0.9 else 1 - reg[s - 1]
    m = np.repeat(REGIME_MEANS[reg][:, None], marks, axis=1)
    c = m + rng.normal(0.0, 1.0, (sessions, marks))
    year = np.repeat(np.arange(years), sessions // years)
    stratum = year[:, None] * marks + np.arange(marks)[None, :]
    return reg, m, c, stratum


def exact_lift(c: np.ndarray, stratum: np.ndarray, state: np.ndarray) -> float:
    """The draft's L: the mean over in-state offers of (c - the mean of c over the offer's whole stratum)."""
    mu = {s: c[stratum == s].mean() for s in np.unique(stratum)}
    dev = c - np.vectorize(mu.get)(stratum)
    return float(dev[state].mean())


def test_placebo_twin_exact_form_is_the_drawn_twins_mean():
    rng = np.random.default_rng([SEED, 1])
    reg, m, c, stratum = _population(rng)
    sees = np.where(rng.random(reg.size) < 0.8, reg, 1 - reg).astype(bool)     # the state sees the regime 4 in 5
    state = np.repeat(sees[:, None], c.shape[1], axis=1)
    L = exact_lift(c, stratum, state)
    # (1) the exact form is the drawn twin's expectation: 2,000 seeded placebo draws, the same count in every stratum
    draws = np.empty(2000)
    flat_c, flat_s, flat_in = c.ravel(), stratum.ravel(), state.ravel()
    groups = [np.flatnonzero(flat_s == s) for s in np.unique(flat_s)]
    in_mean = flat_c[flat_in].mean()
    rng_t = np.random.default_rng([SEED, 2])
    for j in range(draws.size):
        picked = np.concatenate([rng_t.choice(g, size=int(flat_in[g].sum()), replace=False) for g in groups])
        draws[j] = in_mean - flat_c[picked].mean()
    assert abs(draws.mean() - L) < Z * draws.std(ddof=1) / np.sqrt(draws.size)
    # (2) the signal, exactly: on the noise-free values the lift is, stratum by stratum, the in-state offers' excess
    # share of persistent sessions times the regimes' gap -- positive for a state that sees the regime
    signal = exact_lift(m, stratum, state)
    gap = REGIME_MEANS[1] - REGIME_MEANS[0]
    pers = np.repeat(reg[:, None], c.shape[1], axis=1).astype(float)
    expected = sum(state[stratum == s].sum() * (pers[(stratum == s) & state].mean() - pers[stratum == s].mean())
                   for s in np.unique(stratum)) * gap / state.sum()
    assert abs(signal - expected) < 1e-12
    assert signal > 0.0
    # (3) over fresh noise the realised lift averages the signal, judged against the lift's OWN noise (a first version
    # compared one noisy lift with the placebo draws' standard error, a different and much smaller uncertainty; the
    # planted lift sat inside the lift's noise and the check failed -- kept on record in the hand-back)
    lifts = np.array([exact_lift(m + np.random.default_rng([SEED, 6, j]).normal(0.0, 1.0, m.shape), stratum, state)
                      for j in range(400)])
    assert abs(lifts.mean() - signal) < Z * lifts.std(ddof=1) / np.sqrt(lifts.size)


def test_an_uninformative_state_has_no_lift():
    rng = np.random.default_rng([SEED, 3])
    reg, _, c, stratum = _population(rng)
    lifts = []
    for j in range(400):
        r = np.random.default_rng([SEED, 4, j])
        sees = r.random(reg.size) < 1.0 / 3.0                 # fires on a third of sessions, blind to the regime
        state = np.repeat(sees[:, None], c.shape[1], axis=1)
        lifts.append(exact_lift(c, stratum, state))
    lifts = np.asarray(lifts)
    assert abs(lifts.mean()) < Z * lifts.std(ddof=1) / np.sqrt(lifts.size)


def test_centred_values_through_placebo_selection_bound_give_the_exact_lift():
    """The second version's C1 call (review F1): Q-16's `placebo_selection_bound` has no strata, so the family passes
    the stratum-centred values c - mu_g with every population offer as sample 2. Its estimate is then exactly the
    exact-form lift L; on the raw c it is L plus the strata-composition term (the in-state offers' mean stratum mean
    less the population mean), which a year-varying firing share makes non-zero with no selection effect at all."""
    from extended import lift_bound as LB

    rng = np.random.default_rng([SEED, 7])
    sessions, marks, years = 300, 6, 3
    year = np.repeat(np.arange(years), sessions // years)
    stratum = year[:, None] * marks + np.arange(marks)[None, :]
    c = (np.array([0.0, -0.10, 0.05])[year][:, None] + 0.02 * np.arange(marks)[None, :]
         + rng.normal(0.0, 1.0, (sessions, marks)))
    share = np.array([0.15, 0.55, 0.30])[year]                     # a firing share that differs by year
    sees = rng.random(sessions) < share
    state = np.repeat(sees[:, None], marks, axis=1)
    session = np.repeat(np.arange(sessions)[:, None], marks, axis=1)
    mu = {s: c[stratum == s].mean() for s in np.unique(stratum)}
    mu_g = np.vectorize(mu.get)(stratum)
    L = exact_lift(c, stratum, state)
    b = LB.placebo_selection_bound((c - mu_g).ravel(), session.ravel(), state.ravel(), sessions, level=0.01)
    assert b.method == LB.SHIPPED == "cons" and LB.DIFF_DF_RULE == "treated"
    assert abs(b.estimate - L) < 1e-12
    raw = LB.placebo_selection_bound(c.ravel(), session.ravel(), state.ravel(), sessions, level=0.01)
    composition = mu_g[state].mean() - c.mean()
    assert abs(raw.estimate - (L + composition)) < 1e-12
    assert abs(composition) > 0.01                                 # the raw form credits the strata to the state


def test_an_ordered_calendar_keeps_the_wait_an_independent_one_destroys():
    """Review F2: a daily state firing on a third of days with in-state runs of about 20 sessions. A waiting account
    starting on a uniform day falls back when none of its next W = 5 sessions is in state. In history's order (the U1
    replay) that is far more frequent than on independently drawn days (the gate's `SharedDayTable`), where it is
    about (2/3)^5 whatever the persistence -- so K5 must be read on an ordered calendar."""
    rng = np.random.default_rng([SEED, 8])
    n, W = 20000, 5
    stay_in = 1.0 - 1.0 / 20.0                                     # mean in-state run 20 sessions
    leave_out = (1.0 - stay_in) * (1.0 / 3.0) / (2.0 / 3.0)        # so the long-run share is a third
    state = np.zeros(n, dtype=bool)
    state[0] = rng.random() < 1.0 / 3.0
    u = rng.random(n)
    for t in range(1, n):
        state[t] = (u[t] < stay_in) if state[t - 1] else (u[t] < leave_out)
    starts = np.arange(n - W)
    ordered = np.array([not state[s:s + W].any() for s in starts]).mean()
    independent = np.array([not state[rng.integers(0, n, W)].any() for _ in starts]).mean()
    assert abs(state.mean() - 1.0 / 3.0) < 0.05
    assert abs(independent - (2.0 / 3.0) ** W) < 0.02
    assert ordered > 2.0 * independent


# ------------------------------------------------------------------------------------------------ the rolling third


def mid_rank_share(x: np.ndarray, window: int = 250, min_count: int = 120) -> np.ndarray:
    """The draft's 6.4: for each day d, (the prior values below x[d] + half the equal ones) / their count, over the
    `window` prior days with a value; NaN with fewer than `min_count`."""
    out = np.full(x.size, np.nan)
    for d in range(x.size):
        past = x[max(0, d - window):d]
        past = past[~np.isnan(past)]
        if past.size >= min_count and not np.isnan(x[d]):
            out[d] = ((past < x[d]).sum() + 0.5 * (past == x[d]).sum()) / past.size
    return out


def test_rolling_third_fires_on_a_third_and_reads_only_the_past():
    rng = np.random.default_rng([SEED, 5])
    x = rng.normal(size=3000)
    share = mid_rank_share(x)
    top = share[~np.isnan(share)] > 2.0 / 3.0
    # the band doubled: the thresholds of neighbouring days share 249 of their 250 values, so the indicators are not
    # independent (the sample tercile wanders slowly)
    assert abs(top.mean() - 1.0 / 3.0) < 2.0 * Z * np.sqrt((1 / 3) * (2 / 3) / top.size)
    for d in (130, 700, 2999):
        y = x.copy()
        y[d + 1:] = rng.normal(size=y.size - d - 1) * 50.0          # every later value replaced
        assert mid_rank_share(y)[d] == share[d]
    assert np.isnan(share[:120]).all()


# ------------------------------------------------------------------------------------------------ the draft's text


def test_the_population_reads_no_opening_window_bar():
    marks = list(range(F.slot(17, 0), F.slot(8, 25) + 1, 5))
    assert len(marks) == 186 and marks[0] == 0
    window = set(range(F.slot(8, 30), F.slot(9, 0) + 1))
    assert not window & set(marks)                                   # no entry in 08:30-09:00 CT
    for m in marks:
        alert = m - 5                                                # the alert: five minutes before the mark
        last_bar_read = alert - 1                                    # bars stamped at or before t - 1 minute
        assert last_bar_read < F.RTH_OPEN                            # never a bar of 08:30-08:59 of the day


def test_the_draft_names_its_judged_reads():
    text = DRAFT.read_text(encoding="utf-8")
    got = reader.declared_purposes(text)
    assert got == JUDGED_PURPOSES
    for p in got:
        assert not set(p.lower().split("_")) & reader.CHOICE_WORDS, p


def test_the_draft_seeds_are_its_own_block():
    text = DRAFT.read_text(encoding="utf-8")
    rows = re.findall(r"^\| (2026198\d) \|", text, flags=re.MULTILINE)
    assert sorted(int(r) for r in rows) == sorted(SEEDS)
    pat = re.compile(r"\b2026198\d\b")
    for p in sorted((ROOT / "prereg").glob("*.md")):
        if p.name != DRAFT.name:
            assert not pat.search(p.read_text(encoding="utf-8")), p.name
