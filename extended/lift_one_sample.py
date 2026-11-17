"""Q-108 (E-115): the one-sample pass line's re-calibration -- the candidate statistics, their admission check (scope D)
and the exact enumeration of the long sign-flip nulls, built from the pinned plan
`docs/calibration/Q-108_one_sample_plan.md` (sha256 c8e7424b..., E-115). Nothing here is chosen: the calibration
(`scripts/q108_calibrate.py`) measures every candidate and applies the plan's choice rule; the validation
(`scripts/q108_validate.py`) checks the chosen one on other seeds.

**The quantity** is `extended.lift_bound`'s: per trade the pair difference `x = (outcome(rule side) - outcome(mirror))
/ 2`, summed per session of the judged calendar into `S_j`, `N_j` (every session counted). `lift_bound.py` is imported,
never edited (its blob `984f3467...` is pinned by F-03).

**The candidates** (the plan's 2.2; ids and order as its table -- ties in the choice go to fewer members, then to the
earlier row):

| id | name | members (all must reject; the bound is their minimum) |
|---|---|---|
| C0 | `cons` | `t21w`, `t42w`, `t63w`: the per-trade mean, CR1 variance on b-session blocks, t with df G' - 1 |
| C1-C4 | `cons_m1.25` ... `cons_m2` | the same three, each critical value times m = 1.25, 1.5, 1.75, 2 |
| C5 | `cons_bm` | the same three blocks with the CR2 variance and Bell-McCaffrey df (`cr2_parts`) |
| C6 | `cons_bm_m1.25` | C5 with the margin 1.25 |
| C7 | `cons_im` | C0's three and `t63e` (`lift_bound.t_stats(..., block=63, weight="equal")`) |
| C8 | `sn` | the self-normalised T against its calendar-time reference (`sn_reference`) |
| C9 | `cons_sn` | C0's three and C8 |

A member's lower bound is `est - (m crit) se` (t-type; `crit = t(1 - a; df)`) or `(sum S - c_a D) / sum N` (C8, D the
self-normaliser); it rejects when its bound is above zero and it is defined (se > 0 and finite, df >= 1; C8's
self-normaliser > 0). Its minimum detectable lift (MDL) is minus the bound, infinite where the bound is blank. An
intersection's bound is its members' minimum, its MDL their maximum.

**Two forms of each.** `evaluate` (vectorised over replications, the calibration's) and `bound_1s` (scalar, the form a
family calls). The scalar form is written apart from the vectorised one -- the CR1 members through the shipped
`lift_bound.bound`, the rest from their formulas on one sample -- so the calibration's re-decision of its rejections by
the scalar form (the plan's 2.1, E-115 (R1)) checks one against the other.

**Scope D's admission** (the plan's 4.4): a cell's non-tie side series -- each traded session's net side (the sum of
its trades' sides, +1 long, -1 short), sessions with no trade or a zero net side dropped, the signs in calendar order --
has R runs and the effective count E = (sum of run lengths)^2 / (sum of squared run lengths); it is admitted when R >=
floor((n - 1)/63) + 3 (13 on the judged block's 657 sessions, `runs_threshold`), E >= 4, and the series has both sides.
`admission` is the scalar form; `runs_and_effective` the vectorised one; `exact_flip` applies it per cell.

**Exact enumeration** (the plan's 3.1): on a sign-flip null at L sessions every candidate is a function of the test
blocks' sums, linear in the pattern of flip signs, so `exact_flip` sums the rejecting cells over every phase and every
pattern -- phase p ascending, then pattern q ascending, flip block f being +1 when bit f of q is set -- exactly (an
integer numerator over L 2^Bmax). The alternating models' 2L configurations are evaluated directly (`alternating_sides`).

Every random draw takes its generator or seed from the caller (`sn_reference`'s entropy is the calibration's).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache

import numpy as np
from scipy import stats

from extended import lift_bound as LB

#: the calibrated family numbers (the plan's 2.1, E-105 (d)): k = 11 retired with F-02, k = 12 is F-03's
K_RANGE_1S = tuple(range(13, 21))
#: the family levels 0.05 / (k (k + 1)) at k = 13..20, in k order (so, decreasing)
FAMILY_LEVELS_1S = tuple(LB.family_level(k) for k in K_RANGE_1S)
#: the levels reported beside (the plan's 2.1)
EXTRA_LEVELS_1S = (0.001, 0.005, 0.01, 0.025)
LEVELS_1S = FAMILY_LEVELS_1S + EXTRA_LEVELS_1S
#: the CR members' blocks, in sessions (`lift_bound.block_index`)
BLOCKS = (21, 42, 63)
#: the margins of C1-C4 (E-105 (2) extended the grid to 1.75)
MARGINS = (1.25, 1.5, 1.75, 2.0)
#: the judged block's sessions (E-094 (2))
N_SESSIONS = 657
#: a quarter, in sessions: the admission's thresholds come from the most 63-session blocks a side can touch
QUARTER = 63
#: the admission's floor on the effective count (no run holds more than half the non-tie sessions: E <= 1 / s^2)
E_MIN = 4.0
#: C8's reference: 2,000,000 draws of 657 iid standard-normal session sums with N_j = 1, in 200 batches of 10,000
#: drawn in turn from one generator (the plan's 2.2 and 4.1); each batch drawn as one (sessions, batch) array
SN_DRAWS = 2_000_000
SN_BATCH = 10_000
#: (a builder's reading, E-115 hand-back) C8's bound is blank -- it never rejects, its MDL is infinite -- when its
#: self-normaliser sqrt((1/n) sum U_t^2) is zero (every session's mean equal to the overall mean): the t members'
#: "se > 0" carried to C8
SN_NEEDS_POSITIVE_SCALE = True
#: (a builder's reading, E-115 hand-back) "df >= 1" is read with a tolerance: Bell-McCaffrey's df is at least 1
#: whenever it is defined -- exactly 1 when two blocks hold every trade (a rank-one residual) -- and floating point can
#: put it a few ulps below; such a df is taken as 1. The integer dfs (CR1, the block means) are unaffected.
DF_TOL = 1e-9


def level_k(k: int) -> float:
    return LB.family_level(int(k))


def level_fraction(level: float) -> Fraction:
    """A level as an exact fraction: 1 / (20 k (k + 1)) for a family level, the decimal for the levels beside."""
    for k in K_RANGE_1S:
        if abs(LB.family_level(k) - float(level)) < 1e-15:
            return Fraction(1, 20 * k * (k + 1))
    return Fraction(str(float(level)))


def k_of(level: float) -> int | None:
    return next((k for k in K_RANGE_1S if abs(LB.family_level(k) - float(level)) < 1e-15), None)


def runs_threshold(n_sessions: int) -> int:
    """R's threshold on a span of `n_sessions` sessions: floor((n - 1)/63) + 3 -- one more than the most 63-session
    blocks a side constant on them can touch (13 on the judged block, 18 on a 1,006-session choice block)."""
    n = int(n_sessions)
    if n < 1:
        raise ValueError("a span has at least one session")
    return (n - 1) // QUARTER + 3


# ================================================================================================ the candidates


@dataclass(frozen=True)
class Member:
    """One member test: `kind` cr1 (CR1, df G' - 1), cr2 (CR2, Bell-McCaffrey df), eq (equal-weight block means), sn."""
    kind: str
    block: int | None = None
    margin: float = 1.0

    @property
    def name(self) -> str:
        base = {"cr1": f"t{self.block}w", "cr2": f"t{self.block}bm", "eq": f"t{self.block}e", "sn": "sn"}[self.kind]
        return base if self.margin == 1.0 else f"{base}*{self.margin:g}"


@dataclass(frozen=True)
class Candidate:
    cid: str
    name: str
    members: tuple[Member, ...]
    row: int                                    # the plan's table order (ties go to the earlier row)
    scope_q: bool                               # eligible in scope Q (C0 is not: it failed E-052 on Q-16's class)

    @property
    def n_members(self) -> int:
        return len(self.members)


def _cr1(m: float = 1.0) -> tuple[Member, ...]:
    return tuple(Member("cr1", b, m) for b in BLOCKS)


def _cr2(m: float = 1.0) -> tuple[Member, ...]:
    return tuple(Member("cr2", b, m) for b in BLOCKS)


CANDIDATES: tuple[Candidate, ...] = (
    Candidate("C0", "cons", _cr1(), 0, False),
    *(Candidate(f"C{i + 1}", f"cons_m{m:g}", _cr1(m), i + 1, True) for i, m in enumerate(MARGINS)),
    Candidate("C5", "cons_bm", _cr2(), 5, True),
    Candidate("C6", "cons_bm_m1.25", _cr2(1.25), 6, True),
    Candidate("C7", "cons_im", _cr1() + (Member("eq", 63),), 7, True),
    Candidate("C8", "sn", (Member("sn"),), 8, True),
    Candidate("C9", "cons_sn", _cr1() + (Member("sn"),), 9, True),
)
BY_NAME = {c.name: c for c in CANDIDATES}
BY_ID = {c.cid: c for c in CANDIDATES}
NAMES = tuple(c.name for c in CANDIDATES)


def candidate(name_or_id: str) -> Candidate:
    if name_or_id in BY_NAME:
        return BY_NAME[name_or_id]
    if name_or_id in BY_ID:
        return BY_ID[name_or_id]
    raise ValueError(f"unknown candidate {name_or_id!r}; one of {NAMES}")


def needs_sn(cands) -> bool:
    return any(m.kind == "sn" for c in cands for m in c.members)


# ================================================================================================ critical values


@lru_cache(maxsize=None)
def _t_crit_scalar(level: float, df: float) -> float:
    return float(stats.t.ppf(1.0 - float(level), float(df)))


def t_crit(level: float, df) -> np.ndarray:
    """t(1 - level; df), NaN where df < 1 or is not finite; integer df looked up once each."""
    df = np.asarray(df, dtype=float)
    good = np.isfinite(df) & (df >= 1 - DF_TOL)
    out = np.full(df.shape, np.nan)
    if not good.any():
        return out
    d = np.maximum(df[good], 1.0)
    if np.all(d == np.round(d)) and d.size > 8:
        u, inv = np.unique(d, return_inverse=True)
        out[good] = np.array([_t_crit_scalar(float(level), float(x)) for x in u])[inv]
    elif d.size <= 8:
        out[good] = [_t_crit_scalar(float(level), float(x)) for x in d]
    else:
        out[good] = stats.t.ppf(1.0 - float(level), d)
    return out


# ================================================================================================ the parts (vectorised)


def block_sums(S, N, block: int):
    """(BS, BN), each (G, ...) -- the b-session blocks' sums of S and N (`lift_bound.block_index`)."""
    S = np.asarray(S, dtype=float)
    N = np.asarray(N, dtype=float)
    bid, _ = LB.block_index(S.shape[0], block)
    starts = np.flatnonzero(np.r_[True, np.diff(bid) != 0])
    return np.add.reduceat(S, starts, axis=0), np.add.reduceat(N, starts, axis=0)


def cr_parts(BS, BN):
    """(est, se_CR1, df_CR1, se_CR2, df_BM) from block sums (G, r) and block counts (G, r) or (G, 1).

    CR1 is `lift_bound.t_stats`'s, term for term. CR2 for a mean: u_g = BS_g - est BN_g, p_g = BN_g / N, w_g = 1 / (1 -
    p_g), se^2 = sum w_g u_g^2 / N^2; df_BM = N^2 / [sum BN_g^2 + (sum w_g BN_g^2 / N)^2 - sum w_g^2 BN_g^4 / N^2]
    (Bell and McCaffrey's (tr K)^2 / tr K^2 for the mean under independent trades; G' - 1 on equal blocks). A block
    holding every trade (p_g = 1) leaves CR2 blank (NaN)."""
    BS = np.asarray(BS, dtype=float)
    BN = np.asarray(BN, dtype=float)
    with np.errstate(invalid="ignore", divide="ignore", over="ignore"):
        tot = BN.sum(axis=0)
        est = BS.sum(axis=0) / tot
        u = BS - est * BN
        Gp = (BN > 0).sum(axis=0)
        u2 = u ** 2
        se1 = np.sqrt(Gp / (Gp - 1) * u2.sum(axis=0)) / tot
        p = BN / tot
        w = 1.0 / (1.0 - p)
        se2 = np.sqrt((w * u2).sum(axis=0)) / tot
        BN2 = BN ** 2
        den = BN2.sum(axis=0) + ((w * BN2).sum(axis=0) / tot) ** 2 - ((w * BN2) ** 2).sum(axis=0) / tot ** 2
        df2 = tot ** 2 / den
    return est, se1, Gp - 1, se2, df2


def eq_parts(BS, BN):
    """(est, se, df) of the equal-weight block means (`lift_bound.t_stats(..., weight="equal")`, term for term)."""
    BS = np.asarray(BS, dtype=float)
    BN = np.asarray(BN, dtype=float)
    with np.errstate(invalid="ignore", divide="ignore"):
        import warnings

        ok = BN > 0
        m = np.where(ok, BS / np.where(ok, BN, 1.0), np.nan)
        Gp = ok.sum(axis=0)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            est = np.nanmean(m, axis=0)
        sd = np.sqrt(np.nansum((m - est) ** 2, axis=0) / (Gp - 1))
        se = sd / np.sqrt(Gp)
    return est, se, Gp - 1


def sn_parts(S, N):
    """(sum S, sum N, the self-normaliser sqrt((1/n) sum_t U_t^2)) with U_t = sum_{j <= t} (S_j - est N_j), est = sum S
    / sum N, over all n sessions in calendar time."""
    S = np.asarray(S, dtype=float)
    N = np.asarray(N, dtype=float)
    n = S.shape[0]
    with np.errstate(invalid="ignore", divide="ignore"):
        sumS = S.sum(axis=0)
        tot = N.sum(axis=0) * np.ones_like(sumS)
        est = sumS / tot
        U = np.cumsum(S - est * N, axis=0)
        scale = np.sqrt((U * U).sum(axis=0) / n)
    return sumS, tot, scale


def sn_statistic(S, N) -> np.ndarray:
    """C8's T = sum S / sqrt((1/n) sum U_t^2)."""
    sumS, _, scale = sn_parts(S, N)
    with np.errstate(invalid="ignore", divide="ignore"):
        return sumS / scale


def sn_rank(level: float, draws: int = SN_DRAWS) -> int:
    """ceil(level x draws): which largest T sets the reference (a D rounded to 6 decimals first, so a float product
    that should be an integer is not pushed past it)."""
    return int(math.ceil(round(float(level) * int(draws), 6)))


def sn_reference(entropy, levels=LEVELS_1S, *, draws: int = SN_DRAWS, batch: int = SN_BATCH,
                 n: int = N_SESSIONS) -> dict[float, float]:
    """C8's reference c_a at each level: the ceil(a D)-th largest T over D draws of n iid standard-normal session sums
    with N_j = 1, drawn in batches of `batch` in turn from `default_rng(entropy)`, each batch one (n, batch) array."""
    if draws % batch:
        raise ValueError("draws is a whole number of batches")
    rng = np.random.default_rng(entropy)
    T = np.empty(int(draws))
    ones = np.ones((int(n), 1))
    for i in range(int(draws) // int(batch)):
        Z = rng.standard_normal((int(n), int(batch)))
        T[i * batch:(i + 1) * batch] = sn_statistic(Z, ones)
    out = {}
    for a in levels:
        r = sn_rank(a, draws)
        if not (1 <= r <= draws):
            raise ValueError(f"level {a} needs a rank inside the draws")
        out[float(a)] = float(-np.partition(-T, r - 1)[r - 1])
    return out


# ================================================================================================ the decisions (vectorised)


def _member_lower(mem: Member, P: dict, levels, sn_crit) -> np.ndarray:
    """(len(levels), r): the member's lower bound at each level, -inf where it is blank."""
    if mem.kind == "sn":
        if sn_crit is None:
            raise ValueError("C8 needs its reference table (sn_crit)")
        sumS, tot, scale = P["sn"]
        ok = np.isfinite(scale) & np.isfinite(sumS) & (tot > 0)
        if SN_NEEDS_POSITIVE_SCALE:
            ok &= scale > 0
        c = np.array([float(sn_crit[float(a)]) for a in levels])[:, None]
        with np.errstate(invalid="ignore", divide="ignore", over="ignore"):
            low = (sumS[None, :] - c * scale[None, :]) / tot[None, :]
        return np.where(ok[None, :], low, -np.inf)
    if mem.kind in ("cr1", "cr2"):
        est, se1, df1, se2, df2 = P[("cr", mem.block)]
        se, df = (se1, df1) if mem.kind == "cr1" else (se2, df2)
    elif mem.kind == "eq":
        est, se, df = P[("eq", mem.block)]
    else:
        raise ValueError(mem.kind)
    est, se = np.atleast_1d(est), np.atleast_1d(se)
    df0 = np.atleast_1d(np.asarray(df, dtype=float))
    one = df0.size == 1                                           # fixed counts: one df for every replication
    df = np.broadcast_to(df0, est.shape)
    ok = np.isfinite(se) & (se > 0) & np.isfinite(df) & (df >= 1 - DF_TOL) & np.isfinite(est)
    low = np.empty((len(levels), est.shape[0]))
    with np.errstate(invalid="ignore", over="ignore"):
        for i, a in enumerate(levels):
            c = t_crit(a, df0)[0] if one else t_crit(a, df)
            low[i] = est - (mem.margin * c) * se
    return np.where(ok[None, :], low, -np.inf)


def parts(S, N, cands=CANDIDATES) -> dict:
    """Every part the candidates need, from session sums (n, r) and counts (n, r) or (n, 1)."""
    P: dict = {}
    mems = {m for c in cands for m in c.members}
    for b in sorted({m.block for m in mems if m.kind in ("cr1", "cr2", "eq")}):
        BS, BN = block_sums(S, N, b)
        if any(m.kind in ("cr1", "cr2") and m.block == b for m in mems):
            P[("cr", b)] = cr_parts(BS, BN)
        if any(m.kind == "eq" and m.block == b for m in mems):
            P[("eq", b)] = eq_parts(BS, BN)
    if any(m.kind == "sn" for m in mems):
        P["sn"] = sn_parts(S, N)
    return P


def lowers(P: dict, levels, sn_crit=None, cands=CANDIDATES) -> dict[str, np.ndarray]:
    """{candidate: (len(levels), r) lower bound}: its members' minimum, -inf where any member is blank."""
    cache: dict = {}
    out = {}
    for c in cands:
        low = None
        for m in c.members:
            if m not in cache:
                cache[m] = _member_lower(m, P, levels, sn_crit)
            low = cache[m] if low is None else np.minimum(low, cache[m])
        out[c.name] = low
    return out


def evaluate(S, N, levels=LEVELS_1S, *, sn_crit=None, cands=CANDIDATES) -> dict[str, np.ndarray]:
    """The vectorised form: {candidate: (len(levels), r) lower bound}. It rejects where the bound is above zero; its
    MDL is minus the bound (infinite where blank)."""
    return lowers(parts(S, N, cands), levels, sn_crit, cands)


def rejections(low: np.ndarray) -> np.ndarray:
    return low > 0.0


def mdl(low: np.ndarray) -> np.ndarray:
    return -low


# ================================================================================================ the scalar form


@dataclass(frozen=True)
class MemberBound:
    member: str
    estimate: float
    se: float
    critical: float
    df: float
    lower: float                                # NaN when blank


@dataclass(frozen=True)
class Bound1S:
    """One candidate's reading on one sample at one level (the form a family calls)."""
    candidate: str
    level: float
    lower: float                                # the members' minimum; NaN when any is blank
    members: tuple[MemberBound, ...]
    trades: int

    @property
    def rejects(self) -> bool:
        return bool(math.isfinite(self.lower) and self.lower > 0.0)

    @property
    def mdl(self) -> float:
        return -self.lower if math.isfinite(self.lower) else math.inf


def _blank(x: float) -> bool:
    return not (isinstance(x, float) and math.isfinite(x))


def _scalar_member(mem: Member, n: int, S, N, levels, sn_crit) -> list[MemberBound]:
    """One member on one sample's session sums, at each level (its parts computed once)."""
    nan = float("nan")
    if mem.kind in ("cr1", "eq"):
        est, se, df = (float(v) for v in LB.t_stats(S, N, block=mem.block,
                                                    weight="trades" if mem.kind == "cr1" else "equal"))
        ok = math.isfinite(se) and se > 0 and math.isfinite(est) and math.isfinite(df) and df >= 1 - DF_TOL
        out = []
        for a in levels:
            crit = _t_crit_scalar(a, max(df, 1.0)) if ok else nan
            out.append(MemberBound(mem.name, est, se, crit, df, est - (mem.margin * crit) * se if ok else nan))
        return out
    if mem.kind == "cr2":
        bid, G = LB.block_index(n, mem.block)
        BS = np.bincount(bid, weights=S, minlength=G)
        BN = np.bincount(bid, weights=N, minlength=G)
        tot = float(BN.sum())
        if not tot > 0:
            return [MemberBound(mem.name, nan, nan, nan, nan, nan) for _ in levels]
        est = float(BS.sum()) / tot
        ss = d1 = d2 = d3 = 0.0
        for g in range(G):
            if BN[g] <= 0:
                continue
            p = BN[g] / tot
            if p >= 1.0:                                   # one block holds every trade: blank
                return [MemberBound(mem.name, est, nan, nan, nan, nan) for _ in levels]
            w = 1.0 / (1.0 - p)
            u = BS[g] - est * BN[g]
            ss += w * u * u
            d1 += BN[g] ** 2
            d2 += w * BN[g] ** 2
            d3 += (w * BN[g] ** 2) ** 2
        se = math.sqrt(ss) / tot
        den = d1 + (d2 / tot) ** 2 - d3 / tot ** 2
        df = tot ** 2 / den if den > 0 else nan
        ok = math.isfinite(se) and se > 0 and math.isfinite(df) and df >= 1 - DF_TOL
        out = []
        for a in levels:
            crit = _t_crit_scalar(a, max(df, 1.0)) if ok else nan
            out.append(MemberBound(mem.name, est, se, crit, df, est - (mem.margin * crit) * se if ok else nan))
        return out
    if mem.kind == "sn":
        if sn_crit is None:
            raise ValueError("C8 needs its reference table (sn_crit)")
        tot = float(N.sum())
        sumS = float(S.sum())
        if not tot > 0:
            return [MemberBound(mem.name, nan, nan, float(sn_crit[float(a)]), nan, nan) for a in levels]
        est = sumS / tot
        U = q = 0.0
        for j in range(n):
            U += S[j] - est * N[j]
            q += U * U
        scale = math.sqrt(q / n)
        ok = math.isfinite(scale) and (scale > 0 or not SN_NEEDS_POSITIVE_SCALE)
        out = []
        for a in levels:
            c = float(sn_crit[float(a)])
            out.append(MemberBound(mem.name, est, scale, c, nan, (sumS - c * scale) / tot if ok else nan))
        return out
    raise ValueError(mem.kind)


def bound_1s_levels(name: str, x, session, n_sessions: int, *, levels, sn_crit=None) -> list[Bound1S]:
    """`bound_1s` at several levels from one computation of the sample's parts (the re-decision's form)."""
    c = candidate(name)
    levels = [float(a) for a in levels]
    if not all(0.0 < a < 0.5 for a in levels):
        raise ValueError("a one-sided level is in (0, 0.5)")
    S, N = LB.session_sums(x, session, n_sessions)
    per = [_scalar_member(m, int(n_sessions), S, N, levels, sn_crit) for m in c.members]
    out = []
    for i, a in enumerate(levels):
        mb = tuple(p[i] for p in per)
        lows = [m.lower for m in mb]
        low = float("nan") if any(_blank(v) for v in lows) else min(lows)
        out.append(Bound1S(c.name, a, low, mb, int(N.sum())))
    return out


def bound_1s(name: str, x, session, n_sessions: int, *, level: float, sn_crit=None) -> Bound1S:
    """The scalar form a family calls: candidate `name`'s bound on one sample's trades (pair differences `x` and their
    sessions' ordinals on the calendar 0 .. n_sessions - 1) at one-sided `level`. The CR1 and equal-weight members are
    `lift_bound.t_stats` on the sample's session sums (as `lift_bound.bound` computes them); CR2/BM and C8 from their
    formulas, term by term."""
    return bound_1s_levels(name, x, session, n_sessions, levels=[level], sn_crit=sn_crit)[0]


# ================================================================================================ scope D's admission


@dataclass(frozen=True)
class Admission:
    admitted: bool
    runs: int                                   # R
    effective: float                            # E (NaN when the non-tie series is empty)
    nontie: int                                 # the non-tie traded sessions
    threshold: int                              # R's threshold on this span


def nontie_series(sides, session, n_sessions: int) -> np.ndarray:
    """The non-tie series: each traded session's net side (the sum of its trades' sides), sessions with no trade or a
    zero net side dropped, as signs in calendar order."""
    s = np.asarray(sides, dtype=float)
    ses = np.asarray(session)
    if s.shape != ses.shape or s.ndim != 1:
        raise ValueError("one side and one session a trade")
    if len(s) and not np.all(np.isin(s, (-1.0, 1.0))):
        raise ValueError("a side is +1 (long) or -1 (short)")
    net = np.bincount(ses, weights=s, minlength=int(n_sessions))
    return np.sign(net[net != 0]).astype(np.int8)


def runs_of(series) -> tuple[int, float]:
    """(R, E) of a sign series: its maximal runs, and (sum of run lengths)^2 / (sum of squared run lengths)."""
    m = np.asarray(series)
    if m.size == 0:
        return 0, float("nan")
    cut = np.flatnonzero(np.r_[True, m[1:] != m[:-1], True])
    lens = np.diff(cut).astype(float)
    return int(len(lens)), float(lens.sum() ** 2 / (lens ** 2).sum())


def admits(R, E, n_sessions: int):
    """R >= its threshold, E >= 4, and both sides present (R >= 2) -- elementwise."""
    R = np.asarray(R)
    E = np.asarray(E, dtype=float)
    with np.errstate(invalid="ignore"):
        return (R >= runs_threshold(n_sessions)) & (R >= 2) & (E >= E_MIN)


def admission(sides, session, n_sessions: int) -> Admission:
    """The scalar admission check (the plan's 4.4) of a cell's own sides on a span of `n_sessions` sessions."""
    m = nontie_series(sides, session, n_sessions)
    R, E = runs_of(m)
    return Admission(bool(admits(R, E, n_sessions)), R, E, int(m.size), runs_threshold(n_sessions))


def runs_and_effective(m) -> tuple[np.ndarray, np.ndarray]:
    """Vectorised (R, E) per column of a session-side matrix `m` (n, r) in {-1, 0, +1} (0: no trade or a tie)."""
    m = np.asarray(m, dtype=np.int8)
    n, r = m.shape
    nz = m != 0
    idx = np.where(nz, np.arange(n, dtype=np.int32)[:, None], -1)
    np.maximum.accumulate(idx, axis=0, out=idx)              # the last non-zero row at or before each row
    prev = np.full((n, r), -1, dtype=np.int32)
    prev[1:] = idx[:-1]
    has_prev = prev >= 0
    prev_sign = np.where(has_prev, np.take_along_axis(m, np.maximum(prev, 0), axis=0), 0)
    start = nz & ((~has_prev) | (prev_sign != m))            # a run starts here
    R = start.sum(axis=0)
    cnt = np.cumsum(nz, axis=0, dtype=np.int32)              # non-zero entries so far
    base = np.where(start, cnt - 1, 0)
    np.maximum.accumulate(base, axis=0, out=base)            # entries before the current run
    pos = cnt - base                                         # 1-based position in its run
    sumsq = np.where(nz, 2 * pos.astype(np.int64) - 1, 0).sum(axis=0)    # sum of l^2 = sum of (2i - 1)
    M = nz.sum(axis=0).astype(float)
    with np.errstate(invalid="ignore", divide="ignore"):
        E = np.where(sumsq > 0, M * M / np.where(sumsq > 0, sumsq, 1), np.nan)
    return R, E


def session_side_matrix(g, traded, coin_net=None) -> np.ndarray:
    """The net-side signs (n, r) of a null's replications: every trade of session j on the side g_j (`coin_net`
    None), or the coin's own sides times g_j (`coin_net` the per-session sum of the trades' coin sides)."""
    g = np.asarray(g)
    if coin_net is None:
        return np.where(np.asarray(traded)[:, None], np.sign(g), 0).astype(np.int8)
    return (np.sign(np.asarray(coin_net, dtype=float))[:, None] * np.sign(g)).astype(np.int8)


# ================================================================================================ the side models


def markov_sides(rng: np.random.Generator, n: int, dwell: float, reps: int) -> np.ndarray:
    """(n, reps) a two-state side on sessions: a fair first side, then a reversal at each session boundary with
    probability 1 / dwell; drawn in that order (the first sides, then the (n - 1, reps) switches)."""
    first = rng.choice(np.array([-1.0, 1.0]), size=int(reps))
    sw = rng.random((int(n) - 1, int(reps))) < 1.0 / float(dwell)
    par = np.concatenate([np.zeros((1, int(reps)), dtype=np.int64), np.cumsum(sw, axis=0)], axis=0)
    return first[None, :] * np.where(par % 2 == 0, 1.0, -1.0)


def alternating_sides(n: int, L: int) -> np.ndarray:
    """(n, 2L) the alternating model's configurations, in the plan's cell order: phase p ascending, starting long
    before starting short; session j is in block (j + p) // L and the side starting long is (-1)^b on block b."""
    j = np.arange(int(n))
    cols = []
    for p in range(int(L)):
        b = (j + p) // int(L)
        s = np.where(b % 2 == 0, 1.0, -1.0)
        cols += [s, -s]
    return np.stack(cols, axis=1)


def flip_blocks(n: int, L: int, p: int) -> tuple[np.ndarray, int]:
    """(each session's flip block (j + p) // L, the number of blocks B) at phase p (`q16_calibrate._flip_signs`)."""
    fid = (np.arange(int(n)) + int(p)) // int(L)
    return fid, int(fid[-1]) + 1


def pattern_signs(q, B: int) -> np.ndarray:
    """(len(q), B): flip block f's sign under pattern q -- +1 when bit f of q is set, -1 when clear."""
    q = np.asarray(q, dtype=np.int64)
    return (((q[:, None] >> np.arange(int(B))[None, :]) & 1) * 2 - 1).astype(float)


def flip_cells(n: int, L: int) -> tuple[list[int], list[int]]:
    """([B(p)], [the global index of phase p's first cell]) in the plan's cell order."""
    Bs = [flip_blocks(n, L, p)[1] for p in range(int(L))]
    offs = list(np.cumsum([0] + [2 ** b for b in Bs[:-1]]).astype(int))
    return Bs, offs


# ================================================================================================ exact enumeration


@dataclass
class ExactResult:
    """An exact null's sizes: per candidate and scope, the rejecting cells' weight at each level as an integer
    numerator over `den` (L 2^Bmax, or 2L for the alternating models), the admitted weight, and the sampled cells'
    decisions (for the scalar re-decision)."""
    den: int
    num: dict                                   # (candidate, scope) -> list of ints, one a level
    admitted: int
    cells: int
    samples: dict                               # (candidate, scope) -> list of (cell, phase, pattern, decisions)
    uniform: list                               # [(cell, phase, pattern, {(cand, scope): decisions})]

    def size(self, cand: str, scope: str, i: int) -> Fraction:
        return Fraction(int(self.num[(cand, scope)][i]), int(self.den))


def _admit_patterns(Pk: np.ndarray, nf: np.ndarray, n_sessions: int) -> np.ndarray:
    """Admission of each pattern (rows of Pk, signs per flip block): runs over the blocks holding a traded session
    (their traded-session counts nf), equal neighbours merged, empty blocks skipped."""
    keep = nf > 0
    sg = Pk[:, keep]
    w = nf[keep].astype(float)
    if sg.shape[1] == 0:
        return np.zeros(Pk.shape[0], dtype=bool)
    R = 1 + (sg[:, 1:] != sg[:, :-1]).sum(axis=1)
    acc = np.full(Pk.shape[0], w[0])
    sumsq = np.zeros(Pk.shape[0])
    for k in range(1, sg.shape[1]):
        same = sg[:, k] == sg[:, k - 1]
        sumsq += np.where(same, 0.0, acc * acc)
        acc = np.where(same, acc + w[k], w[k])
    sumsq += acc * acc
    E = w.sum() ** 2 / sumsq
    return admits(R, E, n_sessions)


def exact_flip(V, N, L: int, levels=LEVELS_1S, *, sn_crit=None, cands=CANDIDATES, n_first: int = 100,
               uniform_cells=(), first_level: int = 0, family: int = len(FAMILY_LEVELS_1S),
               chunk: int = 1 << 15) -> ExactResult:
    """Every phase x every pattern of the L-session sign-flip null on fixed session sums `V` (n,) and counts `N` (n,),
    in both scopes (Q: the statistic; D: the statistic where the cell's own non-tie side series is admitted).

    Recorded for the scalar re-decision (the plan's 4.1): per candidate and scope, the first `n_first` cells in cell
    order rejecting at `levels[first_level]` (k = 13; in scope D, rejecting and admitted), and the cells
    `uniform_cells` (global indices) for every candidate -- each with its decisions at the first `family` levels."""
    V = np.asarray(V, dtype=float)
    N = np.asarray(N, dtype=float)
    n = V.shape[0]
    traded = (N > 0).astype(float)
    Bs, offs = flip_cells(n, L)
    Bmax = max(Bs)
    den = int(L) * 2 ** Bmax
    names = [c.name for c in cands]
    num = {(c, s): [0] * len(levels) for c in names for s in ("Q", "D")}
    samples = {(c, s): [] for c in names for s in ("Q", "D")}
    uni = sorted(int(u) for u in uniform_cells)
    uniform = []
    admitted_w = 0
    tot = float(N.sum())
    mats = {}
    for b in BLOCKS:
        bid, G = LB.block_index(n, b)
        mats[b] = (bid, G, np.bincount(bid, weights=N, minlength=G))
    need_sn = needs_sn(cands)
    for p in range(int(L)):
        fid, B = flip_blocks(n, L, p)
        wgt = 2 ** (Bmax - B)
        nf = np.bincount(fid, weights=traded, minlength=B)
        VS = np.bincount(fid, weights=V, minlength=B)
        M = {}
        for b, (bid, G, _) in mats.items():
            Mb = np.zeros((B, G))
            np.add.at(Mb, (fid, bid), V)
            M[b] = Mb
        if need_sn:
            cumN = np.cumsum(N)
            D = np.empty((B, n))
            for f in range(B):
                vf = np.where(fid == f, V, 0.0)
                D[f] = np.cumsum(vf) - (VS[f] / tot) * cumN
            Qm = D @ D.T
        uni_here = [u - offs[p] for u in uni if offs[p] <= u < offs[p] + 2 ** B]
        for q0 in range(0, 2 ** B, chunk):
            q = np.arange(q0, min(2 ** B, q0 + chunk))
            Pk = pattern_signs(q, B)
            adm = _admit_patterns(Pk, nf, n)
            admitted_w += wgt * int(adm.sum())
            sumS = Pk @ VS
            keep = sumS > 0                                       # only a positive sum can reject (one-sided)
            sel = np.flatnonzero(keep)
            loc_uni = [x - q0 for x in uni_here if q0 <= x < q0 + len(q)]
            if sel.size:
                Pp = Pk[sel]
                P = {}
                for b, (bid, G, BN) in mats.items():
                    BS = (Pp @ M[b]).T                            # (G, patterns)
                    if any(m.kind in ("cr1", "cr2") and m.block == b for c in cands for m in c.members):
                        P[("cr", b)] = cr_parts(BS, BN[:, None])
                    if any(m.kind == "eq" and m.block == b for c in cands for m in c.members):
                        P[("eq", b)] = eq_parts(BS, BN[:, None])
                if need_sn:
                    qf = np.maximum(np.einsum("ij,jk,ik->i", Pp, Qm, Pp), 0.0)
                    P["sn"] = (sumS[sel], np.full(sel.size, tot), np.sqrt(qf / n))
                low = lowers(P, levels, sn_crit, cands)
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
    return ExactResult(den, num, admitted_w, sum(2 ** b for b in Bs), samples, uniform)


def flip_cell_sides(n: int, L: int, p: int, q: int) -> np.ndarray:
    """(n,) the session sides of one exact flip cell."""
    fid, B = flip_blocks(n, L, p)
    return pattern_signs([q], B)[0][fid]


__all__ = ["K_RANGE_1S", "FAMILY_LEVELS_1S", "EXTRA_LEVELS_1S", "LEVELS_1S", "BLOCKS", "MARGINS", "N_SESSIONS",
           "QUARTER", "E_MIN", "SN_DRAWS", "SN_BATCH", "SN_NEEDS_POSITIVE_SCALE", "DF_TOL", "Member", "Candidate", "CANDIDATES",
           "BY_NAME", "BY_ID", "NAMES", "candidate", "level_k", "level_fraction", "k_of", "runs_threshold", "t_crit",
           "block_sums", "cr_parts", "eq_parts", "sn_parts", "sn_statistic", "sn_rank", "sn_reference", "parts",
           "lowers", "evaluate", "rejections", "mdl", "MemberBound", "Bound1S", "bound_1s", "bound_1s_levels",
           "Admission",
           "nontie_series", "runs_of", "admits", "admission", "runs_and_effective", "session_side_matrix",
           "markov_sides", "alternating_sides", "flip_blocks", "pattern_signs", "flip_cells", "ExactResult",
           "exact_flip", "flip_cell_sides"]
