"""Wave 3.2: the three-way test's statistics -- the deciding bound by the composite's form, the same-design nulls'
guards, the time legs as consistency conditions with their stated sizes, the long-run gate at H_g = 504 sessions, and
the power check by a planted shift (`docs/plans/THREE_WAY_TEST_design.md` 2.2-2.7, 3.2-3.5, 4; E-213; E-221's O-5 and
O-6).

**2.2 (a): Hoeffding's or McDiarmid's bound over every start-seed term** (`mcdiarmid`), admitted only when **every**
dimension is an unconditional mean over all of E_{h_d} of a per-unit value with **a priori bounds** (`Dimension`): from
contract arithmetic or the verified rules (source (i), `"arithmetic"`) or a per-unit clip in the dimension's own
definition (source (ii), `"clip"`) -- never from data. **Each source-(i) bound is also written as a clip** (the third
read's M-1): the value is clip(y, a, a + r) by definition, so the bound holds on every coin field, and the refusal stays
as the check that the arithmetic was right -- a raw value outside it refuses the whole run before any statistic is
written. A censored session count's range is [0, W + 1] (M-2; `session_count`). A dimension with neither an arithmetic
bound nor a pinned clip is not admitted (M-3), nor is a conditional share or mean, a ratio of means, a tail mean or a
quantile: those go to 2.2 (b). With every dimension admitted,

    c_u = sum over d of 1[u in E_{h_d}] w_d 2 r_d / ((hi_d - lo_d) J |E_{h_d}|),
    LB  = Delta-hat - sqrt( ln(1/alpha) x sum over units of c_u^2 / 2 ),

rejecting H0(f, beta) when LB > 0 (for the fallback P_B: Delta-bar - sqrt(2 ln(1/alpha) / (J |E_63|))). Valid only under
choice 3 (every coin key carries its start: the runner's guard).

**2.2 (b): any other composite** -- a bound over J i.i.d. seed-set replicates Delta_j in [-1, 1]: the one-sided
empirical-Bernstein bound (Maurer and Pontil 2009, theorem 4; `eb_lower`) or the hedged betting bound
(Waudby-Smith and Ramdas 2024, its one-sided capital process with predictable plug-in bets; `betting_lower`).
**The rule** (N-6): the bound needing the smaller J for power pi* at delta* decides (`smaller_j`), applied in H3-D
only; H3-A reports both J and applies nothing. **No t decides, in any branch.**

**The same-design nulls' guards** (2.3): a pool whose replicates are all zero is refused; a disjoint pool whose variance
is outside a declared tolerance of twice the single arm's is refused (`null_pool_guards`); the key guard is the
runner's.

**The time legs** (3.4; E-208): consistency conditions, not tests at the level. (Y): every start-year group of Y_ok
(n_min from the calendar) positive; (R): every regime of R_ok positive. Each carries **its stated size** -- the
white-noise Gaussian orthant probability on the actual groups with their windows' overlap counted (a lower bound;
`white_noise_size`) and the S2 block-resampled size on the search years (`resampled_size`, blocks at least h*, the
held-out years refused) -- and **a size at or above one half is labelled vacuous**.

**The long-run gate** (CHARTER 3.8 (c); O-6): over D-145's horizon `H_GATE` = 504 sessions, on the held-out years its
lower quantile is **over coin seeds only** (`long_run_gate`); the history-block reading of the search years is beside.
**The gate's denial** (CHARTER 3.8 (c)): read at D-145's 25 % (`gate_reading`), the 0 % reading beside. **The limits**
(O-5 as E-230 ruled): the point estimate governs -- inside passes, outside fails -- and the one-sided check is reported
beside, never a second margin (`limit_check`); the power gate's headroom is z_pi sigma_M / sqrt(J)
(`headroom_needed`).

**Power** (4): P1's linear plant through `family_stats.conjoint_mdl_linear`; the rule's pass rate at a plant on a grid
through `family_stats.conjoint_mdl_grid`; 2.5's formulas (`hoeffding_units`, `power_hoeffding`).

numpy, scipy and `extended.family_stats` / `extended.lift_bound`; no engine, no bar.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

import numpy as np
from scipy import stats

from extended import family_stats as FS
from extended import lift_bound as LB

#: D-145's gate horizon (`horizon_days: 504` in Stage 2's gate configs; the note's m-11)
H_GATE = 504
#: a condition whose stated size is at least this is labelled vacuous (N-7)
VACUOUS = 0.5
#: E-208's first held-out session: the time legs' resamples and the gate's beside reading refuse it and every later one
HELD_OUT_FIRST = np.datetime64("2024-01-02")
#: the kinds a dimension's functional can be (MEASURES.md 1.3); only "mean" is admitted to 2.2 (a)
KINDS = ("mean", "conditional", "ratio", "tail", "quantile")
SOURCES = ("arithmetic", "clip")
#: a raw value may differ from its arithmetic bound by float residue only
BOUND_TOL = 1e-9


def level(k: int) -> float:
    """The family level 0.05 / (k (k + 1))."""
    return 0.05 / (k * (k + 1))


# ------------------------------------------------------------------------------------------------ the dimensions


class BoundRefused(ValueError):
    """A per-unit value outside its dimension's declared a priori bounds (2.2 (a) item 6): the whole run is refused."""


@dataclass(frozen=True)
class Dimension:
    """One dimension of the pinned composite: its functional's kind, horizon, a priori bounds a <= x <= a + r and
    their source, the composite's caps lo < hi (from the search years) and its weight. `stat` is the functional on a
    seed set's values (2.2 (b)); a mean unless the kind says otherwise."""

    name: str
    kind: str
    horizon: int
    a: float | None = None
    r: float | None = None
    source: str | None = None
    lo: float = 0.0
    hi: float = 1.0
    weight: float = 1.0
    stat: Callable[[np.ndarray], float] | None = None

    def __post_init__(self) -> None:
        if self.kind not in KINDS:
            raise ValueError(f"a dimension's kind is one of {KINDS}")
        if self.source is not None and self.source not in SOURCES:
            raise ValueError(f"a bound's source is one of {SOURCES} or none")
        if self.source is not None and (self.a is None or self.r is None or not self.r > 0):
            raise ValueError("a bound has a lower end and a positive range")
        if not self.hi > self.lo or self.weight < 0:
            raise ValueError("caps lo < hi and a non-negative weight")

    def admitted(self) -> tuple[bool, str]:
        """Whether 2.2 (a) admits it, and why not."""
        if self.kind != "mean":
            return False, f"{self.name}: a {self.kind} is decided by 2.2 (b), never by Hoeffding/McDiarmid"
        if self.stat is not None:
            return False, (f"{self.name}: a functional given through `stat` is not the plain mean 2.2 (a) admits "
                           "(the red team's m-3): decided by 2.2 (b)")
        if self.source is None:
            return False, f"{self.name}: neither an arithmetic bound nor a pinned clip (M-3): decided by 2.2 (b)"
        return True, ""

    def values(self, y) -> np.ndarray:
        """The per-unit values by the definition: clip(y, a, a + r). Source (i): a raw value outside the bound
        refuses (`BoundRefused`) -- the check that the arithmetic was right (M-1); source (ii): the clip is the
        definition. No bound: the values as given."""
        v = np.asarray(y, float)
        if not np.isfinite(v).all():
            raise BoundRefused(f"{self.name}: a blank or infinite per-unit value")
        if self.source is None:
            return v
        a, b = float(self.a), float(self.a) + float(self.r)
        if self.source == "arithmetic" and ((v < a - BOUND_TOL).any() or (v > b + BOUND_TOL).any()):
            bad = v[(v < a - BOUND_TOL) | (v > b + BOUND_TOL)]
            raise BoundRefused(f"REFUSED (2.2 (a) item 6; M-1): {self.name} has a per-unit value {bad[0]!r} outside "
                               f"its arithmetic bound [{a}, {b}]; on the held-out run this fails the finalist, "
                               "diagnosed, never re-run with new bounds")
        return np.clip(v, a, b)

    def functional(self, x: np.ndarray) -> float:
        return float(self.stat(x)) if self.stat is not None else float(np.mean(x))

    def scaled(self, phi: float) -> float:
        """The clipped normaliser clip((Phi - lo) / (hi - lo), 0, 1)."""
        return float(min(1.0, max(0.0, (phi - self.lo) / (self.hi - self.lo))))


def session_count(name: str, window: int, horizon: int, **kw) -> Dimension:
    """A censored sessions-to-event dimension (its never-blank form): its range [0, W + 1], the censored value W + 1
    included (M-2)."""
    return Dimension(name, "mean", horizon, a=0.0, r=float(window + 1), source="arithmetic", **kw)


def fallback() -> Dimension:
    """The pinned fallback P_B: its per-unit value, the share of months 1 to 3 ahead under B, lies in [0, 1]."""
    return Dimension("P_B", "mean", 63, a=0.0, r=1.0, source="arithmetic", lo=0.0, hi=1.0, weight=1.0)


def admission(dims: Sequence[Dimension]) -> tuple[bool, list[str]]:
    """2.2 (a) admits the composite only if every dimension is admitted; the reasons otherwise."""
    why = [w for ok, w in (d.admitted() for d in dims) if not ok]
    return not why, why


def _check_weights(dims: Sequence[Dimension]) -> None:
    if not dims or abs(sum(d.weight for d in dims) - 1.0) > 1e-12:
        raise ValueError("the composite's weights are non-negative and sum to one")


def composite(dims: Sequence[Dimension], X: Mapping[str, np.ndarray]) -> float:
    """C = sum over d of w_d clip((Phi_d - lo_d) / (hi_d - lo_d), 0, 1), Phi_d the functional of the dimension's
    per-unit values (by its definition) over every unit given."""
    _check_weights(dims)
    return float(sum(d.weight * d.scaled(d.functional(d.values(X[d.name]).ravel())) for d in dims))


# ------------------------------------------------------------------------------------------------ 2.2 (a)


@dataclass(frozen=True)
class Bound:
    estimate: float
    lower: float
    alpha: float
    rejects: bool
    form: str
    detail: dict


def mcdiarmid(dims: Sequence[Dimension], Xf: Mapping[str, np.ndarray], Xb: Mapping[str, np.ndarray],
              starts: Mapping[str, Sequence[int]], alpha: float) -> Bound:
    """2.2 (a)'s bound for f against beta: `Xf[d]`, `Xb[d]` are x[s, c] over E_{h_d}'s starts `starts[d]` (the same
    for both arms) and the test's J seeds; refused unless every dimension is admitted (and on any value outside its
    bounds, before any statistic)."""
    ok, why = admission(dims)
    if not ok:
        raise ValueError("REFUSED (2.2 (a)): not admitted -- " + "; ".join(why))
    _check_weights(dims)
    Js = {np.asarray(Xf[d.name]).shape[1] for d in dims} | {np.asarray(Xb[d.name]).shape[1] for d in dims}
    if len(Js) != 1:
        raise ValueError("every dimension and both arms read the same J seeds")
    J = Js.pop()
    vf, vb = {}, {}
    for d in dims:
        a, b = np.asarray(Xf[d.name], float), np.asarray(Xb[d.name], float)
        if a.shape != b.shape or a.shape[0] != len(starts[d.name]):
            raise ValueError(f"{d.name}: both arms on the same E_{d.horizon} (one row a start, one column a seed)")
        vf[d.name], vb[d.name] = d.values(a), d.values(b)          # the refusal comes before any statistic
    est = composite(dims, vf) - composite(dims, vb)
    c_t: dict[int, float] = {}
    for d in dims:
        n_d = len(starts[d.name])
        c = d.weight * 2.0 * float(d.r) / ((d.hi - d.lo) * J * n_d)
        for t in starts[d.name]:
            c_t[int(t)] = c_t.get(int(t), 0.0) + c
    sum_c2 = J * sum(v * v for v in c_t.values())
    lower = est - math.sqrt(math.log(1.0 / alpha) * sum_c2 / 2.0)
    return Bound(est, lower, alpha, lower > 0, "mcdiarmid", {"J": J, "sum_c2": sum_c2, "units": J * len(c_t)})


def hoeffding_terms(d: np.ndarray, alpha: float) -> float:
    """Hoeffding's lower bound for the mean of independent terms in [-1, 1]: mean - sqrt(2 ln(1/alpha) / n)."""
    d = np.asarray(d, float).ravel()
    if (np.abs(d) > 1 + BOUND_TOL).any():
        raise BoundRefused("a term outside [-1, 1]")
    return float(d.mean() - math.sqrt(2.0 * math.log(1.0 / alpha) / d.size))


# ------------------------------------------------------------------------------------------------ 2.2 (b)


def _replicates(D) -> np.ndarray:
    D = np.asarray(D, float).ravel()
    if D.size < 2 or not np.isfinite(D).all() or (np.abs(D) > 1 + BOUND_TOL).any():
        raise ValueError("at least two finite replicates in [-1, 1]")
    return np.clip(D, -1.0, 1.0)


def eb_lower(D, alpha: float) -> float:
    """Maurer and Pontil's one-sided bound on (D + 1) / 2, mapped back:
    mean - sqrt(2 V ln(2/alpha) / J) - (7 ln(2/alpha) / 3) x 2 / (J - 1), V the replicates' unbiased variance."""
    D = _replicates(D)
    J = D.size
    lg = math.log(2.0 / alpha)
    return float(D.mean() - math.sqrt(2.0 * D.var(ddof=1) * lg / J) - (7.0 * lg / 3.0) * 2.0 / (J - 1))


def _capital(y: np.ndarray, m: np.ndarray, alpha: float, c: float) -> np.ndarray:
    """The one-sided betting capital K_J(m) = prod (1 + lambda_i(m) (y_i - m)) on y in [0, 1], for each m: the
    predictable plug-in bet lambda_i = min( sqrt(2 ln(1/alpha) / (J sigma2_{i-1})), c / m ), sigma2 the running
    variance estimate (1/4 + sum over j < i of (y_j - mu_j)^2) / i (i from one), mu_j the running mean
    (1/2 + y_1 + ... + y_j) / (j + 1); c < 1 keeps every factor positive, and under mean(y) <= m the capital is a
    non-negative supermartingale, so P(K_J(m) >= 1 / alpha) <= alpha."""
    lam = bets(y, alpha)
    logk = np.zeros_like(m)
    for i in range(y.size):
        li = np.minimum(lam[i], c / np.maximum(m, 1e-12))
        logk += np.log1p(li * (y[i] - m))
    return logk


def bets(y: np.ndarray, alpha: float) -> np.ndarray:
    """The plug-in bets before the c / m cap: lambda_i = sqrt(2 ln(1/alpha) / (J sigma2_{i-1})), a function of
    y_1 .. y_{i-1} only (predictable; `tests/test_three_way_stats.py` holds it so by perturbing each later term)."""
    y = np.asarray(y, float)
    J = y.size
    lg = math.log(1.0 / alpha)
    mus = (0.5 + np.cumsum(y)) / np.arange(2, J + 2)
    sq = np.concatenate([[0.0], np.cumsum((y - mus) ** 2)[:-1]])
    s2 = (0.25 + sq) / np.arange(1, J + 1)
    return np.sqrt(2.0 * lg / (J * s2))


def betting_lower(D, alpha: float, grid: int = 2001, c: float = 0.5) -> float:
    """The hedged betting bound's one-sided form on y = (D + 1) / 2, mapped back: the largest grid point m such that
    every grid point at or below it is rejected (the capital at least 1 / alpha), so the bound is valid on the grid;
    -1 when none is."""
    y = (_replicates(D) + 1.0) / 2.0
    m = np.linspace(0.0, 1.0, int(grid))[1:-1]
    logk = _capital(y, m, alpha, c)
    rej = logk >= math.log(1.0 / alpha)
    if not rej[0]:
        return -1.0
    first_kept = int(np.argmin(rej)) if not rej.all() else len(m)
    return float(2.0 * m[first_kept - 1] - 1.0)


BOUNDS_B: dict[str, Callable[..., float]] = {"eb": eb_lower, "betting": betting_lower}


def power_of(bound: str, J: int, delta: float, sigma: float, alpha: float, rng: np.random.Generator, reps: int,
             draw: Callable[[np.random.Generator, int], np.ndarray] | None = None) -> float:
    """The share of `reps` replicate samples of size J (a normal of mean delta and sd sigma clipped to [-1, 1], or
    `draw`) on which `bound` rejects."""
    f = BOUNDS_B[bound]
    hits = 0
    for _ in range(int(reps)):
        x = draw(rng, J) if draw is not None else np.clip(rng.normal(delta, sigma, J), -1.0, 1.0)
        hits += f(x, alpha) > 0
    return hits / int(reps)


#: the smaller-J rule's declared inputs (the red team's m-14): J on powers of two from 16 to 32768, 2000 simulated
#: replicate samples a J, the power model a resample with replacement of the pair's per-seed-set search-year
#: replicates (H4's outputs) shifted to mean delta\* (`bootstrap_draw`); the normal model only for H3-A's toys
SMALLER_J_GRID = tuple(2 ** k for k in range(4, 16))
SMALLER_J_DRAWS = 2000


def bootstrap_draw(replicates, delta: float) -> Callable[[np.random.Generator, int], np.ndarray]:
    """The smaller-J rule's power model in H3-D: J replicates drawn with replacement from the pair's per-seed-set
    replicates, recentred to mean `delta`, clipped to [-1, 1]."""
    r = np.asarray(replicates, float).ravel()
    if r.size < 2:
        raise ValueError("the power model needs the pair's replicates")
    r = r - r.mean() + float(delta)

    def draw(rng: np.random.Generator, J: int) -> np.ndarray:
        return np.clip(r[rng.integers(0, r.size, int(J))], -1.0, 1.0)

    return draw


def smaller_j(delta: float, sigma: float, alpha: float, power: float, J_grid: Sequence[int],
              rng: np.random.Generator, reps: int, draw=None) -> dict:
    """2.2 (b)'s rule (N-6): each bound's smallest J on the grid with power at least `power` at delta, and the one
    needing the smaller J (a tie: the empirical-Bernstein bound, the simpler); None where the grid holds none. H3-D
    calls it with `SMALLER_J_GRID`, `SMALLER_J_DRAWS` and `bootstrap_draw` of H4's replicates."""
    need = {}
    for b in BOUNDS_B:
        need[b] = next((int(J) for J in J_grid if power_of(b, int(J), delta, sigma, alpha, rng, reps, draw) >= power),
                       None)
    cands = [(v, b) for b, v in need.items() if v is not None]
    decides = min(cands, key=lambda t: (t[0], t[1] != "eb"))[1] if cands else None
    return {"J": need, "decides": decides}


def seed_set_replicates(dims: Sequence[Dimension], Xf: Mapping[str, np.ndarray], Xb: Mapping[str, np.ndarray],
                        sets: Sequence[np.ndarray]) -> np.ndarray:
    """Delta_j = C(f; S_j) - C(beta; S_j) on disjoint seed sets (the columns of each set), in [-1, 1]."""
    out = []
    for cols in sets:
        out.append(composite(dims, {k: np.asarray(v)[:, cols] for k, v in Xf.items()})
                   - composite(dims, {k: np.asarray(v)[:, cols] for k, v in Xb.items()}))
    return np.array(out)


# ------------------------------------------------------------------------------------------------ the nulls' guards


def null_pool_guards(D, *, single_arm_var: float | None = None, var_tol: float = 0.5) -> None:
    """2.3's guards: refused when every replicate is zero, and (a disjoint pool) when the pool's variance is outside
    `var_tol` of twice the single arm's."""
    D = np.asarray(D, float).ravel()
    if D.size == 0 or not (D != 0).any():
        raise ValueError("REFUSED (2.3): the null pool's replicates are all zero")
    if single_arm_var is not None:
        if not single_arm_var > 0:
            raise ValueError("the single arm's variance is positive")
        ratio = float(D.var(ddof=1)) / (2.0 * float(single_arm_var))
        if abs(ratio - 1.0) > var_tol:
            raise ValueError(f"REFUSED (2.3): the disjoint pool's variance is {ratio:.3f} x twice the single arm's, "
                             f"outside the declared tolerance {var_tol}")


def size_label(rejections: int, n: int, alpha: float) -> dict:
    """E-052's criterion on a count of rejections: fails when the 95 % Clopper-Pearson interval lies wholly above the
    nominal level; a pass means only "no laxity detected" (2.6)."""
    lo, hi = LB.clopper_pearson(int(rejections), int(n))
    return {"rate": rejections / n, "cp_lo": lo, "cp_hi": hi,
            "label": "lax" if lo > alpha else "no laxity detected"}


# ------------------------------------------------------------------------------------------------ the time legs


def condition(delta_hat: Mapping, counts: Mapping, n_min: int) -> dict:
    """(Y) or (R): the groups with at least n_min complete starts (calendar only), and whether Delta-hat is positive in
    every one of them (n_Y = all of Y_ok, N-7)."""
    ok = [g for g in delta_hat if int(counts[g]) >= int(n_min)]
    if not ok:
        raise ValueError("REFUSED (m-17): no group reaches n_min -- a declaration error, not a failed pair")
    return {"ok": ok, "holds": all(float(delta_hat[g]) > 0 for g in ok)}


def _orthant(rho: np.ndarray) -> float:
    k = rho.shape[0]
    if k == 1:
        return 0.5
    if k == 2:
        return 0.25 + math.asin(float(rho[0, 1])) / (2 * math.pi)
    if k == 3:
        return 0.125 + (math.asin(rho[0, 1]) + math.asin(rho[0, 2]) + math.asin(rho[1, 2])) / (4 * math.pi)
    raise ValueError("one to three groups")


def white_noise_size(groups: Sequence[Sequence[int]], h: int, n_sessions: int) -> float:
    """A condition's stated size under white-noise per-session contributions: P(every group's difference positive),
    each start's value the mean of its window's h sessions, the windows' overlap counted -- a Gaussian orthant
    probability, a lower bound by Slepian's inequality ("size>=")."""
    W = np.zeros((len(groups), int(n_sessions)))
    for j, g in enumerate(groups):
        for i in g:
            if i + h > n_sessions:
                raise ValueError("a start's window passes the sessions given")
            W[j, i:i + h] += 1.0 / h
        W[j] /= len(g)
    G = W @ W.T
    s = np.sqrt(np.diag(G))
    return _orthant(G / np.outer(s, s))


def label(size: float) -> str:
    """'VACUOUS' at a stated size of one half or more (N-7)."""
    return "VACUOUS" if size >= VACUOUS else "not vacuous at this bound"


def regimes(v_start, v_star: float) -> np.ndarray:
    """rho(t): 'volatile' where the start's causal volatility (bars closed before its first decision: the caller's)
    exceeds v* (from the search years), else 'calm'."""
    return np.where(np.asarray(v_start, float) > float(v_star), "volatile", "calm")


SEARCH_FIRST, SEARCH_LAST = np.datetime64("2020-01-02"), np.datetime64("2023-12-29")


def refuse_held_out(dates, n: int | None = None) -> None:
    """The time legs' resamples and the gate's beside reading are the search years' only: the dates one a value of
    the series (`n` its length), strictly increasing, and every one inside 2020-01-02 to 2023-12-29 (m-8); a held-out
    session refused."""
    d = np.asarray(dates, dtype="datetime64[D]")
    if (d >= HELD_OUT_FIRST).any():
        raise ValueError("REFUSED (3.6; E-208): a search-year reading was handed a held-out session")
    if n is not None and d.size != int(n):
        raise ValueError(f"REFUSED (m-8): {d.size} dates for a series of {n} values")
    if d.size > 1 and not (np.diff(d) > np.timedelta64(0, "D")).all():
        raise ValueError("REFUSED (m-8): the dates are not strictly increasing")
    if d.size and (d.min() < SEARCH_FIRST or d.max() > SEARCH_LAST):
        raise ValueError("REFUSED (m-8): a date outside the search years")


def resampled_size(contrib, dates, groups_of: Callable[[int], Sequence[Sequence[int]]], h: int, mean_block: float,
                   rng: np.random.Generator, R: int) -> dict:
    """A condition's stated size on S2: the share of R stationary-bootstrap resamples of the search years' centred
    per-session null contributions (`family_stats.stationary_indices`, mean block at least h) on which every group's
    window mean is positive; with the median count of distinct source blocks (2.6: S2's histories recombine few
    blocks) and the vacuity label."""
    refuse_held_out(dates, np.asarray(contrib).size)
    if mean_block < h:
        raise ValueError("REFUSED (3.1): resampled blocks are at least h* long")
    x = np.asarray(contrib, float)
    x = x - x.mean()
    n = x.size
    groups = groups_of(n)
    holds, blocks = 0, []
    for _ in range(int(R)):
        idx = FS.stationary_indices(rng, n, n, mean_block)
        y = x[idx]
        cs = np.concatenate([[0.0], np.cumsum(y)])
        ok = True
        for g in groups:
            g = np.asarray(g)
            ok &= float(((cs[g + h] - cs[g]) / h).mean()) > 0
        holds += ok
        jumps = np.concatenate([[True], np.diff(idx) != 1])
        blocks.append(len(set(idx[jumps].tolist())))
    size = holds / int(R)
    return {"size": size, "label": label(size), "distinct_blocks_median": float(np.median(blocks))}


# ------------------------------------------------------------------------------------------------ the gate, the limits


def complete_starts(n_sessions: int, h: int = H_GATE) -> int:
    """Starts complete at horizon h in n sessions: n - h + 1."""
    return max(0, int(n_sessions) - int(h) + 1)


#: CHARTER 3.8 (c): the gate is read at D-145's tier-3 denial probability of 25 %, the 0 % reading beside (m-7)
GATE_DENIAL = 0.25


def gate_reading(g_at_denial, g_at_zero, q: float, min_starts: int) -> dict:
    """The long-run gate as CHARTER 3.8 (c) reads it: deciding on `g_at_denial` (the journeys at `GATE_DENIAL`), the
    0 % reading beside, never deciding."""
    out = long_run_gate(g_at_denial, q, min_starts)
    out["denial"] = GATE_DENIAL
    out["beside_at_zero_denial"] = long_run_gate(g_at_zero, q, min_starts)
    return out


def long_run_gate(g, q: float, min_starts: int) -> dict:
    """The zero-edge long-run gate on the held-out years (O-6 (a)): `g[s, c]` the log growth of the required bankroll
    over H_g on each complete start s under seed c; per seed the median over starts; the gate passes when the lower q
    quantile of those over the coin seeds is above zero and the complete-start count reaches its pinned minimum."""
    g = np.asarray(g, float)
    if g.ndim != 2 or not np.isfinite(g).all():
        raise ValueError("g is one row a complete start, one column a coin seed, every value finite")
    med = np.median(g, axis=0)
    lowq = float(np.quantile(med, q))
    enough = g.shape[0] >= int(min_starts)
    return {"lower_quantile": lowq, "starts": int(g.shape[0]), "enough_starts": enough,
            "passes": bool(enough and lowq > 0)}


def limit_check(estimate: float, limit: float, halfwidth: float, ceiling: bool = True) -> dict:
    """O-5 as E-230 ruled: **the point estimate governs** -- a design passes a limit when its point estimate is inside
    it and fails it when outside; the one-sided check (B-10's form: for a ceiling, estimate - w > limit, w the coin-seed
    half-width at the pinned level; a floor mirrored) is reported beside, never a second margin. A negative half-width
    is refused (m-6)."""
    if not halfwidth >= 0:
        raise ValueError("REFUSED (m-6): a half-width is non-negative")
    if ceiling:
        inside = estimate <= limit
        crosses = estimate - halfwidth > limit
    else:
        inside = estimate >= limit
        crosses = estimate + halfwidth < limit
    return {"passes": bool(inside), "inside_at_point": bool(inside), "beside_evidence_crosses": bool(crosses)}


def headroom_needed(sigma: float, J: int, power: float = FS.MDL_POWER) -> float:
    """Under the point-estimate rule a design equal to the best baseline passes a limit with probability
    Phi((L - M_best) sqrt(J) / sigma), so the headroom for `power` is z_power sigma / sqrt(J) (no c_L; m-6)."""
    return float(stats.norm.ppf(power)) * float(sigma) / math.sqrt(int(J))


# ------------------------------------------------------------------------------------------------ power (2.5, 4)


def hoeffding_units(delta: float, alpha: float, power: float = FS.MDL_POWER, sigma: float = 1.0) -> int:
    """2.5: the independent terms n at which Hoeffding's bound has the power at true difference delta (terms in
    [-1, 1], sd sigma <= 1): sqrt(n) >= (c_h + z_power sigma) / delta."""
    ch = math.sqrt(2.0 * math.log(1.0 / alpha))
    return math.ceil(((ch + float(stats.norm.ppf(power)) * sigma) / delta) ** 2)


def power_hoeffding(n: int, delta: float, alpha: float, sigma: float) -> float:
    """2.5's power: Phi((sqrt(n) delta - c_h) / sigma)."""
    ch = math.sqrt(2.0 * math.log(1.0 / alpha))
    return float(stats.norm.cdf((math.sqrt(n) * delta - ch) / sigma))


#: the bounds whose lower limit moves one for one with a constant shift of unclipped terms (P1's linear form)
LINEAR_PLANT_BOUNDS = ("hoeffding", "mcdiarmid_unclipped", "eb")


def planted_mdl(lowers0, bound: str, grid=None, power: float = FS.MDL_POWER):
    """P1, the linear plant: each draw's bound at no plant, lower(delta) = lower(0) + delta; the conjoint MDL
    (`family_stats.conjoint_mdl_linear`). **Valid only for `LINEAR_PLANT_BOUNDS` on unclipped terms** (EB while the
    shifted replicates stay in [-1, 1]); refused for the betting bound, whose bet cap moves with the location, and for
    a clipped composite (m-12) -- those run the plant through the bound itself (`planted_rates`)."""
    if bound not in LINEAR_PLANT_BOUNDS:
        raise ValueError(f"REFUSED (m-12): P1's linear form is not valid for {bound!r}; use planted_rates")
    return FS.conjoint_mdl_linear(lowers0, None, grid, power)


def planted_rates(lower: Callable[[np.ndarray], float], null_samples: Sequence[np.ndarray], deltas: Sequence[float]
                  ) -> np.ndarray:
    """The plant run through the bound itself: for each delta, the share of the null samples, shifted by delta and
    clipped to [-1, 1], on which `lower` is above zero (any bound, the betting bound and clipped composites
    included)."""
    out = []
    for dl in deltas:
        out.append(float(np.mean([lower(np.clip(np.asarray(x, float) + dl, -1.0, 1.0)) > 0 for x in null_samples])))
    return np.array(out)


def fpr_hist(passes: Sequence[bool], pair_label: str) -> dict:
    """The history-level false-pass rate (2.7): the whole rule's pass share over the history null's histories, with its
    pair's label (the finalist itself, or 'stylised') and its Clopper-Pearson interval."""
    p = np.asarray(passes, bool)
    lo, hi = LB.clopper_pearson(int(p.sum()), int(p.size))
    return {"pair": pair_label, "rate": float(p.mean()), "n": int(p.size), "cp_lo": lo, "cp_hi": hi}


__all__ = ["H_GATE", "VACUOUS", "HELD_OUT_FIRST", "KINDS", "SOURCES", "level", "BoundRefused", "Dimension",
           "session_count", "fallback", "admission", "composite", "Bound", "mcdiarmid", "hoeffding_terms", "eb_lower",
           "betting_lower", "BOUNDS_B", "power_of", "smaller_j", "seed_set_replicates", "null_pool_guards",
           "size_label", "condition", "white_noise_size", "label", "regimes", "refuse_held_out", "resampled_size",
           "complete_starts", "GATE_DENIAL", "gate_reading", "long_run_gate", "limit_check", "headroom_needed",
           "hoeffding_units", "power_hoeffding", "LINEAR_PLANT_BOUNDS", "planted_mdl", "planted_rates", "bets",
           "SMALLER_J_GRID", "SMALLER_J_DRAWS", "bootstrap_draw", "SEARCH_FIRST", "SEARCH_LAST", "fpr_hist"]
