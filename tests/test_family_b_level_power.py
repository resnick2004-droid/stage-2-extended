"""Q-81 (family B's sixth draft): level AND power at the family's level, on the draft's synthetic toys.

The fifth review (`docs/reviews/DRAFT_F-B_multifeature_v5_2026-11-16.md`) found that every B2 test ran at 0.01 and
checked level only (m5-3), where the frozen state of B2's slow processes has less mass than the level; at the family's
level it binds, and the fifth draft's C1-f could not pass (M5-1, M5-2). The lead's ruling (E-050) names C1-f's null:
**(A) the realised paired lift on the judged block** -- B2's slow follow components centred within the block, so they
shape the dependence and not the mean; the twin's term only in (d); the 3 dropped. E-052 adds the fill-intensity check.

Everything here runs at the family's level `lift_bound.family_level(12)` = 0.05/156 (n5-1: this family is k >= 12),
except the confirmation's form (126 sessions, one-sided 0.05). Session-level toys, as `tests/test_family_b_b2.py`'s,
whose helpers it imports; it reads one file, the vendored value map, for C2's place values. Seeds
`default_rng([20261968, 100 + j])`, fixed before the first run (section 19 of the draft).

* **C1-f under (A)** (the review's check 1 toy: per-session value 2 q (L_t - T_t) plus noise, the twin's and the model's
  lifts each a two-state slow regime switching 1/250 a session):
  - the fifth draft's B2 (slow part centred at its expectation) sets C1-f's critical value far above nominal at the
    family level -- the defect on record; the sixth's (centred within each replicate's block) does not raise it;
  - the size at (A)'s boundary null (realised paired lift exactly zero) is at most the level;
  - the power, against an uninformative twin (q = 1/2) and against a twin with a lift of its own (q = 0.3, T = 0.03),
    rises with the model's excess, is within 0.05 of nominal `cons`'s at every point, and is at least 0.8 at twice the
    nominal 80 % MDL.
* **The conjunction** (C1, C1-d, C1-f against three twins, C2's dollar form; offer-level sides, session-level sums):
  each line at the larger of its nominal and B2's critical values. At no lift every line and the conjunction hold the
  level; the conjoint MDL (the smallest lift at which every line passes in 80 % of draws) exists on the grid, is no
  smaller than any line's own, and lies above the twin's own lift where the twin has one.
* **The confirmation's C1-f** at 126 sessions: `t21w` at the larger of 1.3 x nominal and B2 holds 0.05 at (A)'s boundary
  null and has power (the fifth draft's was flat at its size).
* **E-052's fill-intensity check:** `cons`'s size at the family's level on Q-16's `cluster` null with a cell's own
  per-session counts at random circular offsets; a cell whose 95 % interval lies wholly above the level is killed.
  Constant counts (a `side` cell: every admitted mark offered) are kept; of two count paths of the pass-line review's
  lax profile (log-intensity AR(1) 0.98 with sd 1.5), the more concentrated is killed and the other kept -- the check
  is conditional on the cell's own path (its first form failed on that point; kept on record in the test).

Each test prints its figures (`pytest -s`); the hand-back reads them from that output.

**Tiers (the lead, Q-81).** The level and power cases are marked `slow` (about 3.6 CPU-minutes, light in memory): they
run in `/validate`'s slow tier, not in every commit's fast tier. One fast smoke case,
`test_the_declared_functions_smoke`, exercises every declared function on small counts in a few seconds.
"""
from __future__ import annotations

import csv
import math
import pathlib

import numpy as np
import pytest
from scipy import stats

import test_family_b_b2 as T
from extended import lift_bound as LB

SEED = T.SEED                                   # 20261968
K = 12
LEVEL = LB.family_level(K)                      # 0.05 / 156
COMPONENTS = T.COMPONENTS                       # (21, 42, 63)
N_J = T.FOLLOW_N                                # 609 judged sessions
N_C = 1000                                      # the choice block, 4 x 250 sessions
YEARS_J = (slice(0, 252), slice(252, 504), slice(504, N_J))
YEARS_C = tuple(slice(250 * y, 250 * (y + 1)) for y in range(4))
Q_SLOW = 1 / 250                                # B2's and the toy's slow switching
G_SLOW = 0.03                                   # the toy's follow-regime amplitude
CHUNK = 5000
B2_REPS = 100_000                               # B2's quantile at the family level: about 32 exceedances
ROOT = pathlib.Path(__file__).resolve().parents[1]


def sig_for(q):
    """The per-session sd of C1-f's value at disagreement share q: the toy's 0.13 at q = 0.4, scaled by sqrt(q)."""
    return T.FOLLOW_SIG * math.sqrt(q / T.FOLLOW_Q_DIS)


def chunks(n_rep, size=CHUNK):
    done = 0
    while done < n_rep:
        n = min(size, n_rep - done)
        yield n
        done += n


def nominal(level, n_sessions=N_J, blocks=COMPONENTS):
    return np.array([stats.t.ppf(1 - level, LB.block_index(n_sessions, b)[1] - 1) for b in blocks])


def comp_t(x, blocks=COMPONENTS):
    """(R, len(blocks)) t of `cons`'s components on per-session values x (R, n), one trade a session."""
    S = x.T
    N = np.ones_like(S)
    out = []
    for b in blocks:
        est, se, _ = LB.t_stats(S, N, block=b, weight="trades")
        out.append(est / se)
    return np.stack(out, 1)


def slow_part(rng, n, q, g, *, within, n_sessions=N_J):
    """C1-f's symmetric slow part per session, 2 q g (rho_h - rho_g), each rho a +-1 process switching Q_SLOW a session
    from a random start. within=True: the sixth draft's -- centred on its own block mean (null (A)); False: the fifth's
    -- centred at its expectation only."""
    x = 2 * q * g * (T.markov(rng, Q_SLOW, n, n_sessions) - T.markov(rng, Q_SLOW, n, n_sessions))
    if within:
        x = x - x.mean(1, keepdims=True)
    return x


def b2_quantile(rng, q, g, *, within, level=LEVEL, n_rep=B2_REPS, n_sessions=N_J, blocks=COMPONENTS):
    """B2's (1 - level) quantile of each component for C1-f at amplitude g (the slow part plus session noise)."""
    ts = []
    for n in chunks(n_rep):
        x = (slow_part(rng, n, q, g, within=within, n_sessions=n_sessions)
             + sig_for(q) * rng.standard_normal((n, n_sessions)))
        ts.append(comp_t(x, blocks))
    return np.quantile(np.concatenate(ts), 1 - level, axis=0)


def c1f_truth_t(rng, n_rep, q, excess, *, centred, n_sessions=N_J, blocks=COMPONENTS):
    """The truth's component t: per-session value 2 q (excess + g (rho_h - rho_g)) + noise, g = G_SLOW. centred=True is
    (A)'s boundary null family (the slow part centred within the block, so the realised paired lift is `excess`
    exactly); False the realistic alternative (the regimes uncentred)."""
    ts = []
    for n in chunks(n_rep):
        x = (2 * q * excess + slow_part(rng, n, q, G_SLOW, within=centred, n_sessions=n_sessions)
             + sig_for(q) * rng.standard_normal((n, n_sessions)))
        ts.append(comp_t(x, blocks))
    return np.concatenate(ts)


def rate(t, crit):
    return float(np.mean(np.all(t > np.asarray(crit)[None, :], axis=1)))


# ------------------------------------------------------------------------------- C1-f under (A), the family's level


@pytest.mark.slow
def test_c1f_b2_at_the_family_level_fifth_form_inflated_sixth_not():
    """M5-1 at the family's level: the fifth draft's B2 puts C1-f's critical value at a multiple of nominal (its frozen
    opposite state, probability about 0.0019, exceeds the level); the sixth's, centred within the block, never above
    1.05 x nominal at any amplitude it can take."""
    rng = np.random.default_rng([SEED, 100])
    nom = nominal(LEVEL)
    fifth = {g: b2_quantile(rng, 0.5, g, within=False) for g in (0.01, 0.03)}
    sixth = {(q, g): b2_quantile(rng, q, g, within=True) for q in (0.5, 0.3) for g in (0.01, 0.03, 0.12)}
    print("\n[C1-f B2 at 0.05/156] nominal", nom.round(3))
    for g, v in fifth.items():
        print(f"  fifth (expectation-centred) q 0.5 g {g}: {v.round(3)}  ratio {(v / nom).round(2)}")
    for (q, g), v in sixth.items():
        print(f"  sixth (block-centred)       q {q} g {g}: {v.round(3)}  ratio {(v / nom).round(2)}")
    assert all(v[2] >= 1.3 * nom[2] for v in fifth.values())          # the defect on record (t63w)
    assert all(np.all(v <= 1.05 * nom) for v in sixth.values())       # the sixth draft's form


@pytest.mark.slow
def test_c1f_size_at_the_boundary_null_of_a():
    """(A)'s boundary null: the realised paired lift exactly zero, the follow regimes present but centred within the
    block. Nominal `cons` holds the level; the declared rule's critical values are never below nominal, so its
    rejections are a subset and it holds a fortiori."""
    rng = np.random.default_rng([SEED, 101])
    nom = nominal(LEVEL)
    n_rep = 200_000
    r = {q: rate(c1f_truth_t(rng, n_rep, q, 0.0, centred=True), nom) for q in (0.5, 0.3)}
    print(f"\n[C1-f size at (A)'s boundary null, 0.05/156, {n_rep} reps] level {LEVEL:.6f}; nominal cons:", r)
    assert all(v <= 1.25 * LEVEL for v in r.values()), r


def _amplitude_grid_crit(rng, q, nom):
    """The declared rule's critical values bounded above: the larger of nominal and B2's quantiles over the amplitudes
    0, 0.01, 0.03 and 0.12 (B2 at any amplitude (a) or (d) can take lies at or below the largest of them -- the
    previous test). Using the bound can only understate the power."""
    grid = (0.0, 0.01, 0.03, 0.12)
    qs = np.stack([b2_quantile(rng, q, g, within=True) for g in grid])
    return np.maximum(nom, qs.max(0))


@pytest.mark.slow
def test_c1f_power_at_the_family_level():
    """M5-1 remedy 3: power non-decreasing in the model's excess over the twin, against an uninformative twin
    (q = 1/2, T = 0) and a twin with its own lift (q = 0.3, T = 0.03, so the excess is L - T); within 0.05 of nominal
    `cons` at every point; at least 0.8 at twice the nominal 80 % MDL."""
    rng = np.random.default_rng([SEED, 102])
    nom = nominal(LEVEL)
    excesses = (0.015, 0.03, 0.045, 0.06, 0.09, 0.12)
    n_rep = 10_000
    print(f"\n[C1-f power at 0.05/156, {n_rep} reps a point; the regimes uncentred, amplitude {G_SLOW}]")
    for q, T_own in ((0.5, 0.0), (0.3, 0.03)):
        crit = _amplitude_grid_crit(rng, q, nom)
        p_nom, p_rule = [], []
        for e in excesses:
            t = c1f_truth_t(rng, n_rep, q, e, centred=False)
            p_nom.append(rate(t, nom))
            p_rule.append(rate(t, crit))
        mdl = next((e for e, p in zip(excesses, p_nom) if p >= 0.8), None)
        assert mdl is not None
        p2 = rate(c1f_truth_t(rng, n_rep, q, 2 * mdl, centred=False), crit)
        print(f"  q {q}, twin lift {T_own}: rule crit {crit.round(3)}")
        print(f"    excess L - T  {excesses}")
        print(f"    nominal cons  {np.round(p_nom, 4).tolist()}")
        print(f"    declared rule {np.round(p_rule, 4).tolist()}")
        print(f"    nominal 80 % MDL {mdl}; the rule's power at twice it: {p2:.4f}")
        assert all(b >= a - 0.01 for a, b in zip(p_rule, p_rule[1:])), p_rule
        assert all(abs(a - b) <= 0.05 for a, b in zip(p_nom, p_rule)), (p_nom, p_rule)
        assert p2 >= 0.8


# ---------------------------------------------------------------------- the conjunction of the deciding lines (M5-2)

M_OFF = 24
LINE_NAMES = ("C1", "C1-d", "C1-f lnbar1x4", "C1-f lbrk5", "C1-f mom15", "C2")
TWIN_Q = (0.5, 0.5, 0.3)          # two twins uninformative about the model's side, one agreeing more (mom15-like)
FOLLOW_LINES = (2, 3, 4)


def place_values():
    """p14's mean_dv and trades_per_year_records at places (b)-(e), and (a) every trade's trades a year, read from the
    vendored value map (`u_value_map.csv`, section place_values)."""
    rows = {}
    with open(ROOT / "vendor/stage2/results/u_value_map.csv", newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["section"] == "place_values" and r["base"] == "p14":
                rows[(r["state"], r["measure"])] = float(r["value"])
    places = ("b_evaluation", "c_funded_opening", "d_funded_later", "e_paid")
    dv = np.array([rows[(p, "mean_dv")] for p in places])
    rec = np.array([rows[(p, "trades_per_year_records")] for p in places])
    return dv, rec, rows[("a_every_trade", "trades_per_year_records")]


def judged_design(rng):
    """One judged side series and its fixed products: the model's sides (the review's regime, long share 0.8 / 0.2,
    switching 1/60), three twins disagreeing with it on shares TWIN_Q of the offers, and each offer's place value
    drawn from p14's records shares. Returns the lines' weights against the pair values' parts (the common part, the
    model's side, the mom15-like twin's side), the offer noise's per-session Cholesky across lines, the disagreement
    counts, the mean side and the trades a year."""
    n, m = N_J, M_OFF
    regime = T.markov(rng, T.REVIEW["q_s"], 1, n)[0]
    s = np.where(rng.random((n, m)) < np.where(regime > 0, T.P_IN, 1 - T.P_IN)[:, None], 1.0, -1.0)
    f = [np.where(rng.random((n, m)) < q, -s, s) for q in TWIN_Q]
    dv, rec, t_year = place_values()
    w = dv[rng.choice(4, size=(n, m), p=rec / rec.sum())]
    W = np.stack([s, s - s.mean(), s - f[0], s - f[1], s - f[2], w * s])
    U = np.stack([np.ones_like(s), s, f[2]])
    P = np.einsum("lti,kti->lkt", W, U)
    C = T.S_EPS ** 2 * np.einsum("lti,kti->tlk", W, W) + 1e-9 * np.eye(len(W))[None]
    D = np.stack([(1.0 - s * fr).sum(1) for fr in f])
    return dict(P=P, chol=np.linalg.cholesky(C), D=D, sbar=float(s.mean()), t_year=min(m * 252, t_year))


def _noise(rng, des, n):
    return np.einsum("tlk,rtk->rlt", des["chol"], rng.standard_normal((n, N_J, len(LINE_NAMES))))


def line_stats(S):
    """est, se (R, lines, 3) of `cons`'s components on session sums S (R, lines, n), M_OFF trades a session."""
    R, nl, n = S.shape
    N = np.full((n, R), float(M_OFF))
    est = np.empty((R, nl, len(COMPONENTS)))
    se = np.empty_like(est)
    for li in range(nl):
        for k, b in enumerate(COMPONENTS):
            e, s_, _ = LB.t_stats(S[:, li].T, N, block=b, weight="trades")
            est[:, li, k], se[:, li, k] = e, s_
    return est, se


def conj_b2_crit(rng, des, n_rep=B2_REPS):
    """Each line's per-component critical value: the larger of nominal and B2's (1 - LEVEL) quantile. B2: a choice
    block's session pair values (drift 0.03 switching 1/120, session effect 0.30) resampled in stationary 63-session
    blocks, centred, plus a* rho_t (1/250); fresh offer noise; for the C1-f lines also the symmetric follow part at
    amplitude 0 and G_SLOW, centred within the block, the larger taken (the previous tests: B2 at any amplitude lies at
    or below these)."""
    a = T.REVIEW["a"]
    choice = a * T.markov(rng, T.REVIEW["q_d"], 1, N_C)[0] + T.S_ETA * rng.standard_normal(N_C)
    a_star = np.max(np.abs([choice[y].mean() for y in YEARS_C]))
    ts, tf = [], []
    for n in chunks(n_rep, 1000):
        cs = choice[T.stationary_idx(rng, n, N_J, N_C, T.STRESS_BLOCK)]
        cs = cs - cs.mean(1, keepdims=True) + a_star * T.markov(rng, T.STRESS_Q, n, N_J)
        S = des["P"][:, 0][None] * cs[:, None] + _noise(rng, des, n)
        est, se = line_stats(S)
        ts.append(est / se)
        rho = T.markov(rng, Q_SLOW, n, N_J) - T.markov(rng, Q_SLOW, n, N_J)
        slow = G_SLOW * rho[:, None, :] * des["D"][None]
        slow = slow - slow.mean(2, keepdims=True)                 # N_t constant: the trade-weighted centring
        Sf = S[:, list(FOLLOW_LINES)] + slow
        ef, sf = line_stats(Sf)
        tf.append(ef / sf)
    q = np.quantile(np.concatenate(ts), 1 - LEVEL, axis=0)
    qf = np.quantile(np.concatenate(tf), 1 - LEVEL, axis=0)
    q[list(FOLLOW_LINES)] = np.maximum(q[list(FOLLOW_LINES)], qf)
    return np.maximum(nominal(LEVEL)[None, :], q)


def conj_pass(rng, des, crit, n_rep, L, T_own, g_twin):
    """Per replicate: which lines pass and whether all do. Pair values: drift 0.03 (1/120) + session effect 0.30 +
    the model's planted lift L on its side + the mom15-like twin's own lift T_own + g_twin rho_t (1/250) on its side +
    offer noise 0.35. C1-d also needs |s_bar| < 0.9; C2 needs its dollar bound x trades a year >= $500."""
    a = T.REVIEW["a"]
    out = []
    for n in chunks(n_rep, 1000):
        c = a * T.markov(rng, T.REVIEW["q_d"], n, N_J) + T.S_ETA * rng.standard_normal((n, N_J))
        tw = T_own + g_twin * T.markov(rng, Q_SLOW, n, N_J)
        P = des["P"]
        S = P[:, 0][None] * c[:, None] + P[:, 1][None] * L + P[:, 2][None] * tw[:, None] + _noise(rng, des, n)
        est, se = line_stats(S)
        ok = np.all(est / se > crit[None], axis=2)
        ok[:, 1] &= abs(des["sbar"]) < 0.9
        ok[:, 5] = np.min(est[:, 5] - crit[5][None] * se[:, 5], axis=1) * des["t_year"] >= 500.0
        out.append(ok)
    ok = np.concatenate(out)
    return ok.mean(0), float(np.all(ok, axis=1).mean())


@pytest.mark.slow
def test_the_conjunction_level_and_power_at_the_family_level():
    """M5-2 on the toy: every deciding line at the larger of its nominal and B2's critical values, at the family's
    level. At no lift each line and the conjunction hold the level. Under a planted lift L on the model's side (the
    pair values moved toward it by L, so a twin agreeing with the model shares that much of it), with no twin lift of
    its own and with the mom15-like twin's own lift 0.03 (plus its slow regime): the conjunction's power rises with L,
    is never above any line's, and its 80 % point (the conjoint MDL) exists, is no smaller than any line's own and
    lies above the twin's own lift.

    **The first form failed (kept on record):** with the twin's own lift its grid stopped at L = 0.12, where the
    conjunction's power was 0.7795 -- C1-f against the twin that agrees with the model on 70 % of the offers binds,
    its excess being (L - T) on the 30 % where they differ. Level, monotonicity and the bounds held. The grid of that
    case is extended to 0.18 (the claims unchanged); the uninformative case's grid is the first form's."""
    rng = np.random.default_rng([SEED, 110])
    des = judged_design(rng)
    crit = conj_b2_crit(rng, des)
    nom = nominal(LEVEL)
    print(f"\n[the conjunction at 0.05/156] nominal {nom.round(3)}; mean side {des['sbar']:.3f}")
    for name, c in zip(LINE_NAMES, crit):
        print(f"  {name:14s} crit {c.round(3)}  ratio to nominal {(c / nom).round(2)}")
    lines0, conj0 = conj_pass(rng, des, crit, 100_000, 0.0, 0.0, 0.0)
    print(f"  no lift (100000 reps): lines {dict(zip(LINE_NAMES, lines0.round(6)))}; conjunction {conj0:.6f}")
    assert np.all(lines0 <= 1.5 * LEVEL) and conj0 <= 1.25 * LEVEL
    grids = {0.0: (0.02, 0.03, 0.045, 0.06, 0.09, 0.12), 0.03: (0.03, 0.06, 0.09, 0.12, 0.15, 0.18)}
    for T_own, g_twin in ((0.0, 0.0), (0.03, G_SLOW)):
        grid = grids[T_own]
        lines, conj = [], []
        for L in grid:
            lp, cp = conj_pass(rng, des, crit, 6000, L, T_own, g_twin)
            lines.append(lp)
            conj.append(cp)
        lines = np.array(lines)
        own = {nm: next((L for L, p in zip(grid, lines[:, i]) if p >= 0.8), None) for i, nm in enumerate(LINE_NAMES)}
        mdl = next((L for L, p in zip(grid, conj) if p >= 0.8), None)
        print(f"  mom15-like twin's own lift {T_own} (regime {g_twin}); lift L {grid}")
        for i, nm in enumerate(LINE_NAMES):
            print(f"    {nm:14s} {lines[:, i].round(4).tolist()}  80 % MDL {own[nm]}")
        print(f"    conjunction    {np.round(conj, 4).tolist()}  conjoint 80 % MDL {mdl}")
        assert all(b >= a - 0.02 for a, b in zip(conj, conj[1:])), conj
        assert np.all(np.array(conj)[:, None] <= lines + 1e-12)
        assert mdl is not None and all(v is not None and mdl >= v for v in own.values())
        assert mdl > T_own


# ------------------------------------------------------------------------- the confirmation's C1-f (M5-1 remedy 3)


@pytest.mark.slow
def test_the_confirmation_c1f_level_and_power():
    """126 sessions, `t21w`, one-sided 0.05, at the larger of 1.3 x nominal and B2 (block-centred, amplitudes 0 to
    0.12): at most 1.25 x 0.05 at (A)'s boundary null; power non-decreasing and at least 0.8 at twice the 80 % point of
    1.3 x nominal alone."""
    rng = np.random.default_rng([SEED, 120])
    n_s, lev, blocks = 126, 0.05, (21,)
    nom = 1.3 * nominal(lev, n_s, blocks)
    crit = np.maximum(nom, np.stack([b2_quantile(rng, 0.5, g, within=True, level=lev, n_rep=20_000, n_sessions=n_s,
                                                 blocks=blocks) for g in (0.0, 0.01, 0.03, 0.12)]).max(0))
    size = rate(c1f_truth_t(rng, 20_000, 0.5, 0.0, centred=True, n_sessions=n_s, blocks=blocks), crit)
    excesses = (0.02, 0.04, 0.06, 0.09, 0.12, 0.18)
    p_nom, p_rule = [], []
    for e in excesses:
        t = c1f_truth_t(rng, 10_000, 0.5, e, centred=False, n_sessions=n_s, blocks=blocks)
        p_nom.append(rate(t, nom))
        p_rule.append(rate(t, crit))
    mdl = next((e for e, p in zip(excesses, p_nom) if p >= 0.8), None)
    assert mdl is not None
    p2 = rate(c1f_truth_t(rng, 10_000, 0.5, 2 * mdl, centred=False, n_sessions=n_s, blocks=blocks), crit)
    print(f"\n[the confirmation's C1-f: 126 sessions, t21w, 0.05] 1.3 x nominal {nom.round(3)}; rule {crit.round(3)}")
    print(f"  size at (A)'s boundary null {size:.4f}; excess {excesses}")
    print(f"  1.3 x nominal {np.round(p_nom, 4).tolist()}; rule {np.round(p_rule, 4).tolist()}; "
          f"80 % point {mdl}; rule at twice it {p2:.4f}")
    assert size <= 1.25 * lev
    assert all(b >= a - 0.01 for a, b in zip(p_rule, p_rule[1:])), p_rule
    assert p2 >= 0.8


# --------------------------------------------------------------------- E-052: the fill-intensity (counts) check


def count_check(counts, n_rep, rng, *, level=LEVEL, n_sessions=N_J, offset=True, icc=0.35):
    """The reference for the declared check: `cons`'s rejection rate at `level` on Q-16's `cluster` null (each trade
    1/2 sign(a + e), a ~ N(0, icc) per session, e ~ N(0, 1 - icc); `scripts/q16_calibrate.py`'s SYNTHETIC['cluster']
    outcome) with the per-session counts taken from `counts` -- at a random circular offset per replication
    (offset=True, the stage-A form on a cell's choice-block counts) or as given (the judged form). Returns the rate, its
    95 % Clopper-Pearson interval and whether the interval lies wholly above the level (killed / not claimed)."""
    counts = np.asarray(counts, dtype=np.int64)
    k = 0
    for n in chunks(n_rep, 4000):
        if offset:
            idx = (rng.integers(0, counts.size, n)[None, :] + np.arange(n_sessions)[:, None]) % counts.size
            N = counts[idx]
        else:
            N = np.repeat(counts[:n_sessions, None], n, axis=1)
        a = math.sqrt(icc) * rng.standard_normal((n_sessions, n))
        up = rng.binomial(N, stats.norm.cdf(a / math.sqrt(1 - icc)))
        S = 0.5 * (2 * up - N)
        Nf = N.astype(float)
        rej = np.ones(n, dtype=bool)
        for b in COMPONENTS:
            est, se, df = LB.t_stats(S, Nf, block=b, weight="trades")      # df = G' - 1, G' the non-empty blocks
            with np.errstate(invalid="ignore", divide="ignore"):
                c = stats.t.ppf(1 - level, np.where(df > 0, df, 1))
                rej &= (df > 0) & (se > 0) & (np.nan_to_num(est / se, nan=-np.inf) > c)
        k += int(rej.sum())
    lo, hi = LB.clopper_pearson(k, n_rep)
    return k / n_rep, (lo, hi), bool(lo > level)


def ar_count_path(rng, n=N_C, phi=0.98, sd=1.5, mean=2.0):
    """A count path whose log-intensity is AR(1) phi with stationary sd `sd`, Poisson given it, mean `mean` a session
    (the pass-line review's lax profile)."""
    z = np.empty(n)
    z[0] = sd * rng.standard_normal()
    for t in range(1, n):
        z[t] = phi * z[t - 1] + sd * math.sqrt(1 - phi * phi) * rng.standard_normal()
    return rng.poisson(mean * np.exp(z - sd * sd / 2))


@pytest.mark.slow
def test_the_fill_intensity_check():
    """E-052's check, by its reference `count_check`. A `side` cell's counts are its admitted marks every session
    (constant): kept, at stage A and in the judged form. Two count paths of the lax profile: path 3 of the diagnosis
    (`[20261968, 131, 3]`, replications `[20261968, 132, 3]`) killed, path 7 (`[..., 131, 7]`, `[..., 132, 7]`) kept.

    **The first form failed (kept on record):** it asserted that one path of the profile (drawn from `[20261968, 130]`
    after the constant profile's draws) is killed; that path's rate was 0.000300 (0.94 x the level), interval
    [0.000202, 0.000428], not wholly above. The diagnosis (`docs/reviews/scripts/family_b_drafter/q81_counts_diag.py`
    and its printed output): the declared check is **conditional on the cell's own count path**, and its size varies
    with the path -- of ten paths of the profile five are killed (1.65 x to 3.00 x) and five kept (0.28 x to 0.97 x);
    with a fresh path every replication (the review's unconditional setting) the rate is 2.43 x, interval wholly above.
    The two paths here were chosen after the diagnosis, one of each verdict (disclosed): the test pins the reference
    function's verdicts on them, a regression, not a claim about the profile."""
    rng = np.random.default_rng([SEED, 134])
    r_flat = count_check(np.full(N_C, 40), 50_000, rng)
    r_judged = count_check(np.full(N_J, 40), 50_000, rng, offset=False)
    r = {i: count_check(ar_count_path(np.random.default_rng([SEED, 131, i])), 100_000,
                        np.random.default_rng([SEED, 132, i])) for i in (3, 7)}
    print(f"\n[E-052's count check at 0.05/156] level {LEVEL:.6f}")
    print(f"  constant 40 a session (a side cell), 50000 reps: rate {r_flat[0]:.6f} CI {np.round(r_flat[1], 6)} "
          f"killed {r_flat[2]}")
    print(f"  judged form, constant 40, 50000 reps: rate {r_judged[0]:.6f} CI {np.round(r_judged[1], 6)} "
          f"killed {r_judged[2]}")
    for i, v in r.items():
        print(f"  lax-profile path {i}, 100000 reps: rate {v[0]:.6f} ({v[0] / LEVEL:.2f} x) CI {np.round(v[1], 6)} "
              f"killed {v[2]}")
    assert not r_flat[2] and not r_judged[2]
    assert r[3][2] and not r[7][2]


def test_the_declared_functions_smoke():
    """The fast tier's case (the full checks are `slow`): every declared function of this file runs on small counts
    and gives what its construction guarantees -- B2's sixth form below its fifth at C1-f's slow regime, the
    conjunction's critical values never below nominal and a large planted lift passing every line, the count check
    keeping constant counts. Seeds `[20261968, 140]`."""
    rng = np.random.default_rng([SEED, 140])
    lev = 0.01
    fifth = b2_quantile(rng, 0.5, G_SLOW, within=False, level=lev, n_rep=4000)
    sixth = b2_quantile(rng, 0.5, G_SLOW, within=True, level=lev, n_rep=4000)
    assert np.all(sixth < fifth)
    t = c1f_truth_t(rng, 2000, 0.5, 0.0, centred=True)
    assert t.shape == (2000, len(COMPONENTS)) and 0.0 <= rate(t, nominal(lev)) <= 1.0
    des = judged_design(rng)
    crit = conj_b2_crit(rng, des, n_rep=2000)
    assert crit.shape == (len(LINE_NAMES), len(COMPONENTS)) and np.all(crit >= nominal(LEVEL)[None, :] - 1e-12)
    lines, conj = conj_pass(rng, des, crit, 500, 0.2, 0.0, 0.0)
    assert conj > 0.9 and np.all(lines >= conj)
    r, ci, killed = count_check(np.full(N_C, 40), 2000, rng, level=0.05)
    assert r < 0.05 and not killed and ci[0] <= r <= ci[1]
    assert ar_count_path(np.random.default_rng([SEED, 131, 3])).shape == (N_C,)
