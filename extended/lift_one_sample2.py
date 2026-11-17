"""Q-126 (E-187): the one-sample pass line's second calibration -- the margin grid, scope D's admission with the
balance limit, the band check and the second statistic, built from the pinned plan
`docs/calibration/Q-126_one_sample_plan_2.md` (sha256 117f5eb3..., E-187). Nothing here is chosen: the calibration
(`scripts/q126_calibrate.py`) measures every candidate and applies the plan's choice rule (its 4.2); the validation
(`scripts/q126_validate.py`) judges each chosen statistic on other seeds (its 4.3).

**This module imports `extended/lift_one_sample.py` and changes none of its definitions** (the plan's 2.4, B-13): Q-108's
result files keep their code. Its own blob is pinned only by an adoption row.

**The candidates** (the plan's 2.2; rows in its table order -- ties in the choice go to fewer members, then to the
earlier row):

| row | name | members (all must reject; the bound is their minimum) | scope D | scope-Q branch |
|---|---|---|---|---|
| 1-7 | `cons`, `cons_m1.125`, `cons_m1.25`, `cons_m1.375`, `cons_m1.5`, `cons_m1.75`, `cons_m2` | `t21w`, `t42w`, `t63w`, each critical value times m | yes | rows 5-7 (m >= 1.5) |
| 8 | `cons_bm_m1.25` | `t21bm`, `t42bm`, `t63bm` (CR2, Bell-McCaffrey df) times 1.25 | yes | no |

Every candidate is computed in both scopes on the same draws; a (candidate, scope) pair outside the "yes" cells is
beside (`IN_RULE`). Rows 1-7 are nested in m (`NESTED`): the margin multiplies the critical value only, and IEEE
multiplication is monotone, so a larger margin's rejections are a subset of a smaller's on every sample.

**Scope D's admission** (the plan's 4.4) is Q-108's -- R >= floor((n - 1)/63) + 3, E >= 4, both sides
(`lift_one_sample.admits`) -- **and the balance limit** (B-32): the mean side of the non-tie series, |sum of the signs|
over the number of non-tie sessions, at most b_D, the largest 97.5 % quantile of |mean side| over every flip and every
Markov side of length 1 to 63 on the span's n sessions, every session non-tie (`admission_b`). The comparison is exact
in integers: b is a fraction v/n.

**The band check** (the plan's 2.5): a family's declared side persistence picks the statistic it may use
(`statistic_for`); its sides are checked against its band from its sides only (`band_check`). **The regime-filter kind
is barred by E-187** (W-1, W-2): `band_check` refuses it; its four declared conditions are kept as
`regime_filter_conditions` for the build's tests only. Neither calibration run reads the band check.

**The drift nulls' generator** (the plan's 3.3 and Appendix A) is `drift_draw`, Q-125's `draw` verbatim with n an
argument. Every random draw takes its generator from the caller.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from fractions import Fraction
from functools import lru_cache

import numpy as np
from scipy import stats

from extended import lift_bound as LB
from extended import lift_one_sample as O

K_RANGE_1S = O.K_RANGE_1S
FAMILY_LEVELS_1S = O.FAMILY_LEVELS_1S
LEVELS_1S = O.LEVELS_1S
NF = len(FAMILY_LEVELS_1S)
N_SESSIONS = O.N_SESSIONS

# ================================================================================================ the candidates

#: the margins of rows 1-7 (the plan's 2.2, B-2, B-3), ascending
GRID = (1.0, 1.125, 1.25, 1.375, 1.5, 1.75, 2.0)
#: the scope-Q branch holds only these margins (B-4)
Q_BRANCH_MIN = 1.5
#: C6's margin (row 8, scope D only; B-5)
C6_MARGIN = 1.25


def name_of(m: float) -> str:
    return "cons" if m == 1.0 else f"cons_m{m:g}"


CANDIDATES: tuple[O.Candidate, ...] = (
    *(O.Candidate(f"R{i + 1}", name_of(m), O._cr1(m), i + 1, m >= Q_BRANCH_MIN) for i, m in enumerate(GRID)),
    O.Candidate("R8", "cons_bm_m1.25", O._cr2(C6_MARGIN), 8, False),
)
BY_NAME = {c.name: c for c in CANDIDATES}
NAMES = tuple(c.name for c in CANDIDATES)
#: rows 1-7, nested in m (ascending)
NESTED = tuple(name_of(m) for m in GRID)
#: the scope-Q branch (rows 5-7)
Q_BRANCH = tuple(c.name for c in CANDIDATES if c.scope_q)
#: the (candidate, scope) pairs in the rule: every row in scope D, rows 5-7 in scope Q (2.2's "yes" cells)
IN_RULE = frozenset({(c.name, "D") for c in CANDIDATES} | {(c, "Q") for c in Q_BRANCH})
SCOPES = ("Q", "D")


def candidate(name: str) -> O.Candidate:
    if name not in BY_NAME:
        raise ValueError(f"unknown candidate {name!r}; one of {NAMES}")
    return BY_NAME[name]


def margin_of(name: str) -> float | None:
    c = candidate(name)
    ms = {m.margin for m in c.members}
    return ms.pop() if len(ms) == 1 else None


def in_rule(name: str, scope: str) -> bool:
    return (name, scope) in IN_RULE


# ================================================================================================ the two forms


def evaluate(S, N, levels=LEVELS_1S, *, cands=CANDIDATES) -> dict[str, np.ndarray]:
    """The vectorised form: {candidate: (len(levels), r) lower bound}, `lift_one_sample`'s parts and members."""
    cands = [candidate(c) if isinstance(c, str) else c for c in cands]
    return O.lowers(O.parts(S, N, cands), levels, None, cands)


def bound_1s_levels(name: str, x, session, n_sessions: int, *, levels) -> list[O.Bound1S]:
    """The scalar form a family calls, at several levels: `lift_one_sample`'s scalar members (CR1 through the shipped
    `lift_bound.t_stats`, CR2 term by term) for one of this module's candidates."""
    c = candidate(name)
    levels = [float(a) for a in levels]
    if not all(0.0 < a < 0.5 for a in levels):
        raise ValueError("a one-sided level is in (0, 0.5)")
    S, N = LB.session_sums(x, session, n_sessions)
    per = [O._scalar_member(m, int(n_sessions), S, N, levels, None) for m in c.members]
    out = []
    for i, a in enumerate(levels):
        mb = tuple(p[i] for p in per)
        lows = [m.lower for m in mb]
        low = float("nan") if any(O._blank(v) for v in lows) else min(lows)
        out.append(O.Bound1S(c.name, a, low, mb, int(N.sum())))
    return out


def bound_1s(name: str, x, session, n_sessions: int, *, level: float) -> O.Bound1S:
    return bound_1s_levels(name, x, session, n_sessions, levels=[level])[0]


# ================================================================================================ the balance limit

#: the bands of the plan's 2.5, as (lowest, highest) declared persistence in sessions
BANDS = {"below 42": (1, 41), "42 to 50": (42, 50), "51 to 62": (51, 62)}
#: scope D's domain (4.4): persistence below a quarter, so its balance limit is taken over lengths 1..63
ADMISSION_RANGE = (1, 63)
#: the balance limit's quantile (B-32)
BALANCE_Q = 0.975
#: a switching side's runs interval: this tail at each end (B-33)
RUNS_TAIL = 0.0125
#: no model of the band's own is refused with more than this (E-184)
MAX_IN_BAND_REFUSAL = 0.05
#: the two-quarters regime the switching side's runs floor may exclude, where it costs no in-band refusal
EXCLUDED_REGIME = 126
#: the regime filter's one-sided runs floor's tail (E-186)
REGIME_TAIL = 0.0125


def _flip_counts(n: int, L: int) -> list[list[int]]:
    return [np.bincount((np.arange(n) + p) // L).tolist() for p in range(L)]


@lru_cache(maxsize=None)
def flip_balance(n: int, L: int) -> tuple[np.ndarray, np.ndarray]:
    """The exact distribution of |sum of the side| (an integer 0..n) for the L-session flip on n sessions, every session
    non-tie, phase uniform: (values, cdf) -- independent fair block signs times the block sizes, by convolution."""
    acc: dict[int, float] = {}
    for w in _flip_counts(int(n), int(L)):
        W = int(sum(w))
        d = np.zeros(2 * W + 1)
        d[W] = 1.0
        for x in w:
            d = 0.5 * (np.roll(d, int(x)) + np.roll(d, -int(x)))
        for k in np.flatnonzero(d > 0):
            v = abs(int(k) - W)
            acc[v] = acc.get(v, 0.0) + float(d[k]) / L
    vals = np.array(sorted(acc), dtype=np.int64)
    return vals, np.cumsum([acc[int(v)] for v in vals])


@lru_cache(maxsize=None)
def markov_balance(n: int, D: float) -> tuple[np.ndarray, np.ndarray]:
    """The exact distribution of |sum of the side| for a Markov side of mean dwell D on n sessions (a fair first side,
    a reversal at each boundary with 1/D), by recursion over the count of long sessions: (values, cdf)."""
    n = int(n)
    q = 1.0 / float(D)
    lo_, sh = np.zeros(n + 1), np.zeros(n + 1)
    lo_[1], sh[0] = 0.5, 0.5
    for _ in range(n - 1):
        nl = np.zeros(n + 1)
        nl[1:] = (1 - q) * lo_[:-1] + q * sh[:-1]
        sh = (1 - q) * sh + q * lo_
        lo_ = nl
    pk = lo_ + sh
    m = np.abs(2 * np.arange(n + 1) - n)
    acc: dict[int, float] = {}
    for k in range(n + 1):
        acc[int(m[k])] = acc.get(int(m[k]), 0.0) + float(pk[k])
    vals = np.array(sorted(acc), dtype=np.int64)
    return vals, np.cumsum([acc[int(v)] for v in vals])


def _quantile(dist, a: float = BALANCE_Q) -> int:
    vals, cdf = dist
    return int(vals[min(int(np.searchsorted(cdf, a - 1e-12)), len(vals) - 1)])


def _exceeds(dist, v: int) -> float:
    """P(|sum| > v)."""
    vals, cdf = dist
    i = int(np.searchsorted(vals, int(v), side="right")) - 1
    return max(0.0, float(1.0 - (cdf[i] if i >= 0 else 0.0)))


@lru_cache(maxsize=None)
def balance_limit(n: int, lo: int, hi: int) -> Fraction:
    """b = v / n: the largest 97.5 % quantile of |mean side| over every flip and every Markov side of length lo..hi on
    n sessions (the plan's 2.5 rule)."""
    v = max(max(_quantile(flip_balance(int(n), L)), _quantile(markov_balance(int(n), float(L))))
            for L in range(int(lo), int(hi) + 1))
    return Fraction(v, int(n))


def band_b(n: int, band: str) -> Fraction:
    return balance_limit(int(n), *BANDS[band])


def admission_b(n: int) -> Fraction:
    """b_D: the admission's balance limit on a span of n sessions (4.4)."""
    return balance_limit(int(n), *ADMISSION_RANGE)


def balance_ok(side_sum, nontie, b: Fraction):
    """|side_sum| / nontie <= b, exactly (elementwise; integers or floats holding integers)."""
    s = np.abs(np.asarray(side_sum, dtype=np.float64))
    m = np.asarray(nontie, dtype=np.float64)
    return s * b.denominator <= b.numerator * m


# ================================================================================================ scope D's admission


@dataclass(frozen=True)
class Admission2:
    admitted: bool
    runs: int                                   # R
    effective: float                            # E (NaN when the non-tie series is empty)
    nontie: int                                 # the non-tie traded sessions
    threshold: int                              # R's threshold on this span
    side_sum: int                               # the sum of the non-tie signs
    balance: Fraction                           # b_D on this span
    balanced: bool                              # |side_sum| / nontie <= b_D

    @property
    def mean_side(self) -> float:
        return abs(self.side_sum) / self.nontie if self.nontie else float("nan")


def admission2(sides, session, n_sessions: int, *, balance: bool = True) -> Admission2:
    """The scalar admission (the plan's 4.4) of a cell's own sides on a span of `n_sessions` sessions: Q-108's
    (`lift_one_sample.admission`'s series, R, E and threshold) and, with `balance`, the balance limit."""
    m = O.nontie_series(sides, session, n_sessions)
    R, E = O.runs_of(m)
    b = admission_b(n_sessions)
    s = int(m.astype(np.int64).sum())
    bal = bool(balance_ok(s, m.size, b)) if m.size else False
    adm = bool(O.admits(R, E, n_sessions)) and (bal or not balance)
    return Admission2(adm, int(R), E, int(m.size), O.runs_threshold(n_sessions), s, b, bal)


def admitted_matrix(m, n_sessions: int, *, balance: bool = True) -> np.ndarray:
    """The vectorised admission per column of a session-side matrix `m` (n, r) in {-1, 0, +1} (0: no trade or a tie):
    `lift_one_sample.runs_and_effective` and `admits`, and with `balance` the balance limit."""
    m = np.asarray(m, dtype=np.int8)
    R, E = O.runs_and_effective(m)
    adm = O.admits(R, E, n_sessions)
    if balance:
        s = m.astype(np.int64).sum(axis=0)
        M = (m != 0).sum(axis=0)
        adm = adm & balance_ok(s, M, admission_b(n_sessions))
    return adm


def flip_cell_balance(N, L: int, p: int, q: int) -> tuple[int, int]:
    """(the sum of the side over the traded sessions, the traded sessions) of one exact flip cell: the sum over flip
    blocks of the block's sign times its traded sessions, over the traded sessions (the plan's 4.4)."""
    N = np.asarray(N, dtype=float)
    fid, B = O.flip_blocks(len(N), L, p)
    nf = np.bincount(fid, weights=(N > 0).astype(float), minlength=B)
    sg = O.pattern_signs([q], B)[0]
    return int(round(float(sg @ nf))), int(nf.sum())


# ================================================================================================ exact enumeration


@dataclass
class ExactResult2:
    """An exact null's sizes: per candidate and scope the rejecting cells' weight at each level as an integer numerator
    over `den`; the admitted weight; the sampled cells for the scalar re-decision; and, for the pairs asked for, every
    cell rejecting at the first level (k = 13) with the largest family k at which it rejects (the plan's 4.5)."""
    den: int
    num: dict                                   # (candidate, scope) -> list of ints, one a level
    admitted: int
    cells: int
    samples: dict                               # (candidate, scope) -> [(cell, phase, pattern, decisions)]
    uniform: list                               # [(cell, phase, pattern, {(cand, scope): decisions}, admitted)]
    records: dict = field(default_factory=dict)  # (candidate, scope) -> dict of arrays (cell, p, q, B, weight,
    #                                              admitted, kmax)

    def size(self, cand: str, scope: str, i: int) -> Fraction:
        return Fraction(int(self.num[(cand, scope)][i]), int(self.den))


def _kmax(r_fam: np.ndarray) -> np.ndarray:
    """(cells,) the largest family k at which each column of `r_fam` (family, cells) rejects."""
    nf = r_fam.shape[0]
    idx = nf - 1 - np.argmax(r_fam[::-1], axis=0)
    return np.asarray(K_RANGE_1S, dtype=np.int64)[idx]


def _empty_records() -> dict:
    return {k: [] for k in ("cell", "p", "q", "B", "weight", "admitted", "kmax")}


def _close_records(rec: dict) -> dict:
    return {k: (np.concatenate(v) if v else np.zeros(0, dtype=np.int64)) for k, v in rec.items()}


def exact_flip2(V, N, L: int, levels=LEVELS_1S, *, cands=CANDIDATES, n_first: int = 100, uniform_cells=(),
                first_level: int = 0, family: int = NF, balance: bool = True, record=(),
                chunk: int = 1 << 15) -> ExactResult2:
    """Every phase x every pattern of the L-session sign-flip null on fixed session sums `V` (n,) and counts `N` (n,),
    in both scopes (Q: the statistic; D: the statistic where the cell's own non-tie side series is admitted -- Q-108's
    runs admission and, with `balance`, the balance limit). `lift_one_sample.exact_flip`'s enumeration, cell order and
    re-decision samples; with `balance=False` it is that function's procedure exactly (a test holds the two equal).

    `record`: the (candidate, scope) pairs whose cells rejecting at `levels[first_level]` are kept (`records`)."""
    cands = [candidate(c) if isinstance(c, str) else c for c in cands]
    V = np.asarray(V, dtype=float)
    N = np.asarray(N, dtype=float)
    n = V.shape[0]
    traded = (N > 0).astype(float)
    Bs, offs = O.flip_cells(n, L)
    Bmax = max(Bs)
    den = int(L) * 2 ** Bmax
    names = [c.name for c in cands]
    num = {(c, s): [0] * len(levels) for c in names for s in SCOPES}
    samples = {(c, s): [] for c in names for s in SCOPES}
    record = {tuple(x) for x in record}
    recs = {k: _empty_records() for k in record}
    uni = sorted(int(u) for u in uniform_cells)
    uniform = []
    admitted_w = 0
    b = admission_b(n) if balance else None
    mats = {}
    for blk in O.BLOCKS:
        bid, G = LB.block_index(n, blk)
        mats[blk] = (bid, G, np.bincount(bid, weights=N, minlength=G))
    need_cr = {blk for c in cands for m in c.members if m.kind in ("cr1", "cr2") for blk in [m.block]}
    for p in range(int(L)):
        fid, B = O.flip_blocks(n, L, p)
        wgt = 2 ** (Bmax - B)
        nf = np.bincount(fid, weights=traded, minlength=B)
        tot_tr = float(nf.sum())
        VS = np.bincount(fid, weights=V, minlength=B)
        M = {}
        for blk, (bid, G, _) in mats.items():
            Mb = np.zeros((B, G))
            np.add.at(Mb, (fid, bid), V)
            M[blk] = Mb
        uni_here = [u - offs[p] for u in uni if offs[p] <= u < offs[p] + 2 ** B]
        for q0 in range(0, 2 ** B, chunk):
            q = np.arange(q0, min(2 ** B, q0 + chunk))
            Pk = O.pattern_signs(q, B)
            adm = O._admit_patterns(Pk, nf, n)
            if balance:
                adm = adm & balance_ok(Pk @ nf, np.full(len(q), tot_tr), b)
            admitted_w += wgt * int(adm.sum())
            sumS = Pk @ VS
            sel = np.flatnonzero(sumS > 0)                          # only a positive sum can reject (one-sided)
            loc_uni = [x - q0 for x in uni_here if q0 <= x < q0 + len(q)]
            if sel.size:
                Pp = Pk[sel]
                P = {}
                for blk, (bid, G, BN) in mats.items():
                    if blk in need_cr:
                        P[("cr", blk)] = O.cr_parts((Pp @ M[blk]).T, BN[:, None])
                low = O.lowers(P, levels, None, cands)
            else:
                low = {c: np.empty((len(levels), 0)) for c in names}
            adm_sel = adm[sel]
            pos_of = {int(s): i for i, s in enumerate(sel)} if loc_uni else {}
            for c in names:
                rej = low[c] > 0.0
                for s_, r_ in (("Q", rej), ("D", rej & adm_sel[None, :])):
                    cnt = r_.sum(axis=1)
                    acc = num[(c, s_)]
                    for i in range(len(levels)):
                        acc[i] += wgt * int(cnt[i])
                    lst = samples[(c, s_)]
                    if len(lst) < n_first:
                        for i in np.flatnonzero(r_[first_level])[: n_first - len(lst)]:
                            qq = int(q[sel[i]])
                            lst.append((offs[p] + qq, p, qq, tuple(bool(v) for v in r_[:family, i])))
                    if (c, s_) in record:
                        hit = np.flatnonzero(r_[first_level])
                        if hit.size:
                            qq = q[sel[hit]].astype(np.int64)
                            rr = recs[(c, s_)]
                            rr["cell"].append(offs[p] + qq)
                            rr["p"].append(np.full(hit.size, p, dtype=np.int64))
                            rr["q"].append(qq)
                            rr["B"].append(np.full(hit.size, B, dtype=np.int64))
                            rr["weight"].append(np.full(hit.size, wgt, dtype=np.int64))
                            rr["admitted"].append(adm_sel[hit].astype(np.int64))
                            rr["kmax"].append(_kmax(r_[:family, hit]))
            for x in loc_uni:
                qq = int(q[x])
                dec = {}
                for c in names:
                    if x in pos_of:
                        r_ = low[c][:family, pos_of[x]] > 0.0
                    else:
                        r_ = np.zeros(family, dtype=bool)
                    dec[(c, "Q")] = tuple(bool(v) for v in r_)
                    dec[(c, "D")] = tuple(bool(v) and bool(adm[x]) for v in r_)
                uniform.append((offs[p] + qq, p, qq, dec, bool(adm[x])))
    return ExactResult2(den, num, admitted_w, sum(2 ** b_ for b_ in Bs), samples, uniform,
                        {k: _close_records(v) for k, v in recs.items()})


@dataclass
class AltResult:
    """An alternating model's 2L configurations: rejections per candidate and scope (levels, 2L), the admission per
    configuration, and the counts."""
    den: int
    num: dict
    admitted: int
    rej: dict                                   # (candidate, scope) -> (levels, 2L) bool
    adm: np.ndarray
    records: dict = field(default_factory=dict)


def exact_alternating(V, N, L: int, levels=LEVELS_1S, *, cands=CANDIDATES, balance: bool = True, record=(),
                      first_level: int = 0, family: int = NF) -> AltResult:
    """The alternating model at L on fixed session sums: every configuration (phase p ascending, starting long before
    starting short: cell 2p + q, q = 0 long first) evaluated directly, scope D admitting by the cell's own sides."""
    cands = [candidate(c) if isinstance(c, str) else c for c in cands]
    V = np.asarray(V, dtype=float)
    N = np.asarray(N, dtype=float)
    n = V.shape[0]
    sides = O.alternating_sides(n, L)
    low = evaluate(sides * V[:, None], N[:, None], levels, cands=cands)
    mm = np.where((N > 0)[:, None], sides, 0).astype(np.int8)
    adm = admitted_matrix(mm, n, balance=balance)
    num, rej = {}, {}
    records = {}
    record = {tuple(x) for x in record}
    for c in cands:
        r = low[c.name] > 0.0
        for s_, rr in (("Q", r), ("D", r & adm[None, :])):
            rej[(c.name, s_)] = rr
            num[(c.name, s_)] = [int(x) for x in rr.sum(axis=1)]
            if (c.name, s_) in record:
                hit = np.flatnonzero(rr[first_level])
                records[(c.name, s_)] = {"cell": hit.astype(np.int64), "p": (hit // 2).astype(np.int64),
                                         "q": (hit % 2).astype(np.int64), "B": np.full(hit.size, -1, dtype=np.int64),
                                         "weight": np.ones(hit.size, dtype=np.int64),
                                         "admitted": adm[hit].astype(np.int64), "kmax": _kmax(rr[:family, hit])
                                         if hit.size else np.zeros(0, dtype=np.int64)}
    return AltResult(2 * int(L), num, int(adm.sum()), rej, adm, records)


# ================================================================================================ the drift nulls

#: the plan's 3.3: (index, label, z, T, delta, varying by quarter), in its order
DRIFT_SCENARIOS = (
    (0, "A", 5000, 560, 0.0, False),
    (1, "B", 5000, 560, 0.01, False),
    (2, "C", 5000, 560, 0.02, False),
    (3, "D", 5000, 560, 0.03, False),
    (4, "E", 500, 300, 0.02, False),
    (5, "F", 5000, 150, 0.0, False),
    (6, "G", 5000, 150, 0.02, False),
    (7, "H", 5000, 560, 0.02, True),
)
DRIFT_POPULATIONS = 150


def drift_draw(rng, z, T, d, varying, n: int = N_SESSIONS):
    """Q-125's Appendix A `draw` (the plan's Appendix A), verbatim, with the module-level `n` an argument: (V, N), the
    population's session sums and counts."""
    N = np.zeros(n)
    w = np.zeros(n); tr = rng.choice(n, T, replace=False); w[tr] = rng.gamma(2.0, 1.0, T)  # noqa: E702
    N = rng.multinomial(z, w / w.sum()).astype(float)
    q = np.arange(n) // 63
    dq = d * (rng.choice([-1.0, 1.0], q.max() + 1)[q] if varying else np.ones(n))
    V = np.zeros(n)
    for j in np.flatnonzero(N):
        k = int(N[j]); u = rng.random(k)  # noqa: E702
        V[j] = 0.5 * ((u < 0.25 + dq[j]).sum() - ((u >= 0.25 + dq[j]) & (u < 0.5)).sum())
    return V, N


# ================================================================================================ the probe


def probe_ranking(scores: dict, *, per_size: int = 23, core: int = 23) -> dict:
    """The plan's 3.2 (B-23): at each size, the `per_size` sizing subsets (j >= `core`) with the largest score, ties to
    the smaller j. `scores` maps (z, j) to a score (a Fraction: the sum over both values and the flips at 42, 55 and 63
    of `cons`'s scope-Q exact size over the level at k = 13). Returns {z: [(j, score), ...]} in rank order."""
    by: dict = {}
    for (z, j), s in scores.items():
        if int(j) >= core:
            by.setdefault(z, []).append((int(j), s))
    out = {}
    for z, lst in by.items():
        lst.sort(key=lambda t: (-t[1], t[0]))
        out[z] = lst[:per_size]
    return out


# ================================================================================================ the band check (2.5)


def _markov_runs_out(n: int, D: float, lo_r: int, hi_r: int | None) -> float:
    below = float(stats.binom.cdf(lo_r - 2, n - 1, 1.0 / D))
    above = 0.0 if hi_r is None else float(stats.binom.sf(hi_r - 1, n - 1, 1.0 / D))
    return below + above


def _max_runs(n: int, L: int) -> int:
    return (int(n) - 1) // int(L) + 2


@lru_cache(maxsize=None)
def runs_interval(n: int, band: str) -> tuple[int, int | None, str]:
    """A declared switching side's runs interval on n sessions and whether the two-quarters floor is kept (the plan's
    2.5): lower 1 + the 1.25 % quantile of Bin(n - 1, 1/hi), raised to one more than the most runs of a side constant
    over 126 sessions only where every Markov model of the band then stays within the refusal rule; upper 1 + the
    98.75 % quantile of Bin(n - 1, 1/lo) (none below 42)."""
    n = int(n)
    lo, hi = BANDS[band]
    lower = 1 + int(stats.binom.ppf(RUNS_TAIL, n - 1, 1.0 / hi))
    upper = None if band == "below 42" else 1 + int(stats.binom.ppf(1.0 - RUNS_TAIL, n - 1, 1.0 / lo))
    floor = _max_runs(n, EXCLUDED_REGIME) + 1
    if floor <= lower:
        return lower, upper, "not binding"
    v = band_b(n, band).numerator * n // band_b(n, band).denominator
    worst = max(_markov_runs_out(n, float(D), floor, upper) + _exceeds(markov_balance(n, float(D)), v)
                for D in range(lo, hi + 1))
    if worst <= MAX_IN_BAND_REFUSAL:
        return floor, upper, "kept"
    return lower, upper, "dropped"


def band_interval(n: int, band: str) -> tuple[int, int | None]:
    lo_r, hi_r, _ = runs_interval(n, band)
    return lo_r, hi_r


def band_of(persistence: int) -> str | None:
    """The band of a declared side persistence (sessions), or None for 63 sessions or more (no one-sample line)."""
    p = int(persistence)
    if p < 1:
        raise ValueError("a declared persistence is at least one session")
    for name, (lo, hi) in BANDS.items():
        if lo <= p <= hi:
            return name
    return None


def statistic_for(persistence: int, primary_scope: str | None, *, primary_holds: bool = True,
                  second_holds: bool = False) -> tuple[str, str] | None:
    """The plan's 2.5 table: which adopted statistic a family may use for its C1, by its declared persistence alone
    -- ("primary", its scope) or ("second", "Q") -- or None (no one-sample line). `primary_scope` is "D" when scope D
    chose the primary, "Q" when the scope-Q branch is the primary (scope D chose none), None at NONE. A statistic that
    FAILS its validation leaves its rows with no line; the other is never extended to them (B-30)."""
    band = band_of(persistence)
    if primary_scope is None or band is None:
        return None
    if primary_scope == "Q":
        return ("primary", "Q") if primary_holds else None
    if primary_scope != "D":
        raise ValueError("the primary's scope is D or Q")
    if band == "42 to 50":
        return ("second", "Q") if second_holds else None
    return ("primary", "D") if primary_holds else None


@dataclass(frozen=True)
class BandCheck:
    passes: bool
    reasons: tuple[str, ...]
    outcome: str                                # "passes" | "not claimed" | "re-declare before the pin" | "barred"
    details: dict


def regime_floor(B: int) -> int:
    return int(stats.binom.ppf(REGIME_TAIL, int(B) - 1, 0.5)) if B > 1 else 0


def regime_filter_conditions(sides, points, band: str, n: int | None = None) -> tuple[bool, list[str]]:
    """The plan's 2.5 regime-filter test on a dense side series (+1 or -1 a session) and the declared decision points:
    (a) spacing, (b) every change on a point, (c) the one-sided runs floor, (d) the balance limit. **Barred by E-187
    from any family's use** (`band_check` refuses the kind); kept for the build's tests only."""
    s = np.asarray(sides, dtype=int)
    n = len(s) if n is None else int(n)
    lo, hi = BANDS[band]
    pts = sorted(int(x) for x in points if 0 < int(x) < n)
    why = []
    gaps = np.diff(pts)
    if len(gaps) and not np.all((gaps >= lo) & (gaps <= hi)):
        why.append("spacing")
    changes = [j for j in range(1, n) if s[j] != s[j - 1]]
    pset = set(pts)
    if any(j not in pset for j in changes):
        why.append("a change off the decision points")
    if len(changes) < regime_floor(len(pts) + 1):
        why.append("runs floor")
    if not bool(balance_ok(int(s.sum()), n, band_b(n, band))):
        why.append("balance")
    return (not why), why


def switching_side_check(sides, session, n_sessions: int, band: str) -> tuple[bool, list[str], dict]:
    """A declared switching side (2.5): R, the runs of 4.4's non-tie series, in the band's runs interval on the span's
    n sessions, and the mean side at most the band's b. Reads sides only."""
    m = O.nontie_series(sides, session, n_sessions)
    R, _ = O.runs_of(m)
    lo_r, hi_r = band_interval(n_sessions, band)
    b = band_b(n_sessions, band)
    why = []
    if R < lo_r or (hi_r is not None and R > hi_r):
        why.append("runs interval")
    s = int(m.astype(np.int64).sum())
    if m.size == 0 or not bool(balance_ok(s, m.size, b)):
        why.append("balance")
    return (not why), why, {"runs": int(R), "interval": (lo_r, hi_r), "side_sum": s, "nontie": int(m.size),
                            "balance": b}


def band_check(kind: str, band: str, *, block: str, n_sessions: int, sides=None, session=None) -> BandCheck:
    """The band check of a family's sides against its declared band (2.5), from sides only, never an outcome.
    `kind` "switching" (a declared mean dwell) or "regime_filter" (barred by E-187: always refused, outcome "barred").
    `block` "judged" (inside stage C: a mismatch is "not claimed", never a switch of band, kind or statistic) or
    "choice" (at stage A, before the pin: a mismatch may be re-declared from sides only, recorded in the pinning row)."""
    if block not in ("judged", "choice"):
        raise ValueError("the band check runs on the judged block or the choice block")
    if band not in BANDS:
        raise ValueError(f"no band {band!r}: persistence of 63 sessions or more has no one-sample line")
    if kind == "regime_filter":
        return BandCheck(False, ("the regime-filter kind is barred by E-187 (W-1, W-2) until a revision under a new "
                                 "row lifts the bar",), "barred", {})
    if kind != "switching":
        raise ValueError("the kinds are 'switching' and 'regime_filter'")
    ok, why, det = switching_side_check(sides, session, n_sessions, band)
    if ok:
        return BandCheck(True, (), "passes", det)
    return BandCheck(False, tuple(why), "not claimed" if block == "judged" else "re-declare before the pin", det)


__all__ = ["GRID", "Q_BRANCH_MIN", "C6_MARGIN", "CANDIDATES", "BY_NAME", "NAMES", "NESTED", "Q_BRANCH", "IN_RULE",
           "SCOPES", "NF", "K_RANGE_1S", "FAMILY_LEVELS_1S", "LEVELS_1S", "candidate", "name_of", "margin_of",
           "in_rule", "evaluate", "bound_1s", "bound_1s_levels", "BANDS", "ADMISSION_RANGE", "BALANCE_Q",
           "flip_balance", "markov_balance", "balance_limit", "band_b", "admission_b", "balance_ok", "Admission2",
           "admission2", "admitted_matrix", "flip_cell_balance", "ExactResult2", "exact_flip2", "AltResult",
           "exact_alternating", "DRIFT_SCENARIOS", "DRIFT_POPULATIONS", "drift_draw", "probe_ranking",
           "runs_interval", "band_interval", "band_of", "statistic_for", "BandCheck", "regime_floor",
           "regime_filter_conditions", "switching_side_check", "band_check"]
