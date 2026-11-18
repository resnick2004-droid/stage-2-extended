"""Q-145: the statistics every new family's deciding lines share, built once -- **B2's conditional critical values**
(the larger-of rule and its null), **the conjoint MDL**, **the screen rule** and **the pre-pin power gate** reading
Q-126's power file. Engine-free: numpy, pandas, scipy and `extended.lift_bound` only (the gate's file check imports
`extended.results` when it runs, so call `power_gate` in a process of its own, as every reader of a result file is).

**Where the pieces come from.** F-03's build (`extended/opening_stats.py`) and family B's draft
(`prereg/DRAFT_F-B_multifeature.md` sections 8 item 8 and 12, with its references in `tests/test_family_b_b2.py`) each
wrote them for one family. `opening_stats.py` is covered by F-03's A0 identity and the shared identities' covers
(`extended.opening_run.cover`, `extended.identity_cover`), so it is **not edited**: the general pieces are copied here
and `tests/test_family_stats.py` holds each copy bit for bit to the original on the same inputs and generators (the
larger-of rule, the members, the stationary bootstrap, the slow sign, B2's replicate on the grid, B2's t's and
quantiles, the 63-block amplitude, the screen comparison of `scripts/fo_opening.py`), and the one-sample wrapper to
family B's reference `cons_bound_with_critical`. F-03 keeps calling its own module; nothing it computes changes.

**The larger-of rule (B2; E-035, E-051, family B 12, F-03 11 item 1).** A deciding line is read by `cons`
(`lift_bound.SHIPPED`): the trade-weighted session-cluster t on 21-, 42- and 63-session blocks (`MEMBERS`), all three
required; **each member's critical value is the larger of its nominal t and B2's (1 - level) quantile of the same
member's t**, always, with no tolerance and no pretest; the line's bound is the members' smallest lower bound and it
passes when that bound is above zero. `critical`, `larger_of_one_sample`, `larger_of_two_sample`,
`cons_bound_with_critical` (family B's named wrapper), `lower_bounds`, `rejects_t`.

**B2's null (conditional on the judged sides; the family declares its form, block, switching rate and amplitude).**
Each replicate's pair values come from the choice block's own session vectors, resampled to the judged calendar by a
stationary bootstrap (`stationary_indices`: circular, the new-block flags drawn first, then the jump positions, the
first position a jump), plus a declared slow drift `a* x rho_t` (`slow_sign`: a two-state sign, its start drawn first,
then its switches), then the line's values formed with the **real judged sides and weights**. Two forms:
* `b2_null_pooled` (family B's 12): one bootstrap over every choice session; the replicate's mean over its judged offers
  removed; the drift added after;
* `b2_null_strata` (F-03's 11 item 2): one bootstrap per declared day kind (a judged session of another kind left
  empty); the drift added; then re-centred within the judged strata.
**A caution on record** (`tests/test_family_stats.py`, a strict `xfail` and its diagnosis): B2 holds the level when its
null spans the truth; but a choice block carrying its own slow drift, resampled in 63-session blocks, dilutes that drift
into block-scale variance, so on a one-sided side series B2 at the true amplitude can under-cover, and an amplitude
estimated below the true one (family B's yearly-mean rule, on a draw) does too. A family using the pooled form declares
its amplitude, and its sides' balance (Q-126's balance limit), with this in view.
`b2_member_t` draws replicate i from `key(i)` (the family's declared generator, e.g. `default_rng([seed, line, i])`),
so the chunking changes no draw; `b2_quantiles` and `b2_critical` give {member: quantile}. `slow_two_state` and
`centre_within` are family B's C1-f pieces (a process between 0 and 2 g*, centred within the judged block).
`block_mean_amplitude` (F-03's a*) and `year_mean_amplitude` (family B's a*) are the two amplitude rules on record.

**The conjoint MDL (E-051's M5-2; family B 8 item 8; F-03's A9).** The minimum detectable lift of every deciding line
together: per draw the planted lift L each line needs, (-lower bound) / slope -- a line whose per-offer values move by
slope x L under a lift L (C1: 1; a paired line: its disagreement share) -- the draw's need their largest; the MDL the
`power` quantile of the needs (`mdl_from_need`, numpy's default rule, an infinite neighbour giving infinity) or, on a
declared grid, the smallest L at which at least `power` of the same draws pass every line ("above the grid" is
infinity; `conjoint_mdl_grid` takes any rule, `conjoint_mdl_linear` the linear one). With one line and slope 1 the
need is `lift_bound.mdl_draws`'s crit x se - estimate exactly.

**The screen rule (R-16; family B 8 item 8; F-03's A9).** A family is declared a screen when its MDL exceeds
`MDL_FACTOR` (3) times its value bar at **every** surviving cell; no surviving cell is no screen (`scripts/fo_opening.py`'s
comparison, held bit for bit). An MDL above the grid is infinite and counts as above.

**The pre-pin power gate (Q-142 section 3; E-051; E-086's precedent).** Before a family whose C1 is one-sample spends
a k, its power is read from Q-126's power file (`results/q126_cal_power.csv`, written by `scripts/q126_calibrate.py`
under its plan's 6.2; columns as its `power_rows`): the toys' 80 % MDL for the family's adopted statistic and scope, its
value (`win1`: win probability at 1R; `net3`: net R at 3R) and **the smallest calibrated k at or above the family's**
and **the largest calibrated toy size (judged-block trades) at or below its declared supply**, the larger over the two
side models (the coin's side and sides flipped by session). Each choice can only overstate the MDL, so the gate never
passes a family whose true MDL is above the factor times its bar; at a calibrated point it is exact. The family
**closes before its pin, taking no k, when that MDL exceeds the factor (3) times its bar** (in the value's unit).
Beside, deciding nothing: the MDL scaled by sqrt(size / supply). **Until the file exists the gate refuses**, naming it;
it also refuses a file whose manifest does not verify, is not the calibration script's, is exploratory, is not from a
clean run or is marked dirty, and a family outside the calibrated range (k 13 to 20, plan 7 item 5) or below the
smallest toy size.

Every function that draws takes its generator (or a key giving one) explicitly; none has a default seed.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import numpy as np
import pandas as pd
from scipy import stats

from extended import lift_bound as LB

#: `cons`'s members: the session-cluster t on 21-, 42- and 63-session blocks
MEMBERS = (21, 42, 63)
FORMS = ("one_sample", "two_sample")
#: the conjoint MDL's power and the screen rule's factor (R-16; F-03 section 8's table: fixed, 3)
MDL_POWER = 0.8
MDL_FACTOR = 3.0

#: the power gate's file (Q-126's plan 6.2) and what it may hold
POWER_FILE = "q126_cal_power.csv"
POWER_SCRIPT = "scripts/q126_calibrate.py"
GATE_K_RANGE = tuple(range(13, 21))                 # the calibrated range, Q-126's plan 7 item 5
TOY_OF_VALUE = {"win1": "P", "net3": "net3"}        # the toys' `toy` label per value (`q126_calibrate`'s nulls)
TOY_MODELS = ("coin", "flip1")                      # the toys' side models: the coin's side, sides flipped by session
SCOPES = ("D", "Q")


class NotFinite(RuntimeError):
    """A t, a quantile, a standard error or a value a rule needs is not finite: refused, never a fall-back."""


class PowerGateRefused(RuntimeError):
    """The power gate cannot read a family's power: the file is missing or not trusted, or the family is outside it."""


def rng_of(*key: int) -> np.random.Generator:
    """`default_rng` of an integer key (a family's declared seed and its stream indices)."""
    return np.random.default_rng([int(k) for k in key])


def _level(level: float) -> float:
    lv = float(level)
    if not (0.0 < lv < 0.5):
        raise ValueError(f"a one-sided level lies in (0, 0.5), not {level!r}")
    return lv


# ================================================================================================ the larger-of rule


@dataclass(frozen=True)
class Member:
    block: int
    estimate: float
    se: float
    df: float
    t_crit: float
    b2_crit: float
    crit: float
    lower: float


@dataclass(frozen=True)
class Line:
    """A deciding line by the larger-of rule: its members, the bound (their smallest lower bound), and whether it
    passes (the bound above zero)."""
    members: tuple[Member, ...]
    bound: float
    passes: bool
    level: float

    def as_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"bound": self.bound, "passes": self.passes, "level": self.level}
        for m in self.members:
            for k in ("estimate", "se", "df", "t_crit", "b2_crit", "crit", "lower"):
                d[f"t{m.block}w_{k}"] = getattr(m, k)
        return d


def _line(rows: Sequence[tuple[int, float, float, float]], level: float,
          critical: Mapping[int, float] | None) -> Line:
    """F-03's `larger_of` on given (block, estimate, se, df) rows."""
    mem = []
    for b, est, se, df in rows:
        tc = float(stats.t.ppf(1.0 - level, df)) if df >= 1 else float("nan")
        q = float(critical[b]) if critical is not None else float("-inf")
        if critical is not None and not math.isfinite(q):
            raise NotFinite(f"B2's quantile of t{b}w is not finite: the rule is never quietly nominal")
        c = max(tc, q) if math.isfinite(tc) else float("nan")
        lo = est - c * se if (math.isfinite(se) and se > 0 and math.isfinite(c)) else float("nan")
        mem.append(Member(b, est, se, df, tc, q, c, lo))
    lows = [m.lower for m in mem]
    ok = all(math.isfinite(x) for x in lows)
    bound = min(lows) if ok else float("nan")
    return Line(tuple(mem), bound, bool(ok and bound > 0), float(level))


def larger_of_one_sample(S, N, level: float, critical: Mapping[int, float] | None = None) -> Line:
    """One sample's session sums (S, N) by the larger-of rule; `critical` {block: B2's quantile} (None: `cons` at its
    nominal values, `lift_bound.bound("cons")` exactly)."""
    lv = _level(level)
    rows = []
    for b in MEMBERS:
        est, se, df = (float(v) for v in LB.t_stats(S, N, block=b, weight="trades"))
        rows.append((b, est, se, df))
    return _line(rows, lv, critical)


def larger_of_two_sample(S1, N1, S2, N2, level: float, critical: Mapping[int, float] | None = None) -> Line:
    """Two samples' session sums by the larger-of rule, the members `lift_bound.diff_stats` with the treated df (F-03's
    `opening_stats.larger_of`, bit for bit)."""
    lv = _level(level)
    rows = []
    for b in MEMBERS:
        est, se, df = (float(v) for v in LB.diff_stats(S1, N1, S2, N2, block=b))
        rows.append((b, est, se, df))
    return _line(rows, lv, critical)


def cons_bound_with_critical(x, session, n_sessions: int, level: float,
                             critical: Mapping[int, float] | None = None) -> tuple[float, bool]:
    """Family B's named wrapper (its draft's 12 and 20): (lower bound, passes) of one sample of trades `x` at their
    session ordinals by the larger-of rule; with `critical=None`, `lift_bound.bound("cons", ...)` exactly."""
    line = larger_of_one_sample(*LB.session_sums(x, session, n_sessions), level, critical)
    return line.bound, line.passes


def members_one_sample(S, N) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(estimate, se, df), each stacked over `MEMBERS` (axis 0), of one sample's session sums of shape (n,) or (n, R)."""
    out = [LB.t_stats(S, N, block=b, weight="trades") for b in MEMBERS]
    return tuple(np.stack([np.asarray(o[i], dtype=float) for o in out]) for i in range(3))   # type: ignore[return-value]


def members_two_sample(S1, N1, S2, N2) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """As `members_one_sample` for the difference of two samples (`lift_bound.diff_stats`, the treated df)."""
    out = [LB.diff_stats(S1, N1, S2, N2, block=b) for b in MEMBERS]
    return tuple(np.stack([np.asarray(o[i], dtype=float) for o in out]) for i in range(3))   # type: ignore[return-value]


def _t(est, se) -> np.ndarray:
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(np.isfinite(se) & (se > 0), est / se, np.nan)


def member_t_one_sample(S, N) -> np.ndarray:
    """Each member's t (members x replicates) from one sample's session sums of shape (n, replicates)."""
    out = []
    for b in MEMBERS:
        est, se, _ = LB.t_stats(S, N, block=b, weight="trades")
        out.append(_t(est, se))
    return np.vstack(out)


def member_t_two_sample(S1, N1, S2, N2) -> np.ndarray:
    """Each member's t (members x replicates) of the two-sample difference (F-03's `member_t`, bit for bit)."""
    out = []
    for b in MEMBERS:
        est, se, _ = LB.diff_stats(S1, N1, S2, N2, block=b)
        out.append(_t(est, se))
    return np.vstack(out)


def critical(level: float, df, b2: Mapping[int, float] | None = None) -> np.ndarray:
    """Each member's critical value (by `MEMBERS`): its nominal t at `df`, or the larger of it and B2's quantile.
    `df` is one value a member, or (members x replicates); a df below 1 has no critical value (NaN)."""
    lv = _level(level)
    d = np.asarray(df, dtype=float)
    if d.shape[0] != len(MEMBERS):
        raise ValueError(f"df has one row a member ({len(MEMBERS)}), not {d.shape[0]}")
    with np.errstate(invalid="ignore"):
        tc = np.where(d >= 1, stats.t.ppf(1.0 - lv, np.where(d >= 1, d, 1.0)), np.nan)
    if b2 is None:
        return tc
    q = np.array([float(b2[b]) for b in MEMBERS])
    if not np.isfinite(q).all():
        raise NotFinite("a B2 quantile is not finite: the rule is never quietly nominal")
    q = q.reshape((-1,) + (1,) * (tc.ndim - 1))
    return np.where(np.isfinite(tc), np.maximum(tc, q), np.nan)


def lower_bounds(est, se, crit) -> np.ndarray:
    """The line's bound per replicate: the members' smallest est - crit x se, NaN when any member's is not finite (a
    standard error not above zero, a critical value missing)."""
    est, se = np.asarray(est, dtype=float), np.asarray(se, dtype=float)
    c = np.asarray(crit, dtype=float)
    if c.ndim < est.ndim:
        c = c.reshape(c.shape + (1,) * (est.ndim - c.ndim))
    with np.errstate(invalid="ignore"):
        lows = np.where(np.isfinite(se) & (se > 0) & np.isfinite(c), est - c * se, np.nan)
    return np.where(np.all(np.isfinite(lows), axis=0), lows.min(axis=0), np.nan)


def rejects_t(T, crit) -> np.ndarray:
    """Per replicate: every member's t above its critical value (the larger-of rule's pass, where every se > 0)."""
    T = np.asarray(T, dtype=float)
    c = np.asarray(crit, dtype=float)
    if c.ndim < T.ndim:
        c = c.reshape(c.shape + (1,) * (T.ndim - c.ndim))
    with np.errstate(invalid="ignore"):
        return np.all(T > c, axis=0)


# ================================================================================================ B2's null


def stationary_indices(rng: np.random.Generator, n_src: int, n_out: int, mean_block: float) -> np.ndarray:
    """A stationary bootstrap's source positions (circular, mean block `mean_block`): the new-block flags drawn first,
    then the jump positions; the first position is a jump (F-03's, bit for bit)."""
    if n_src <= 0:
        raise ValueError("a bootstrap needs at least one source session")
    starts = rng.random(n_out) < 1.0 / float(mean_block)
    if n_out:
        starts[0] = True
    jumps = rng.integers(0, n_src, n_out)
    t = np.arange(n_out)
    last = np.maximum.accumulate(np.where(starts, t, 0))
    return (jumps[last] + (t - last)) % n_src


def slow_sign(rng: np.random.Generator, n: int, switch: float) -> np.ndarray:
    """rho_t: a two-state Markov sign switching with probability `switch` a session, its start drawn first (F-03's)."""
    s0 = 1.0 if rng.random() < 0.5 else -1.0
    flips = rng.random(n) < switch
    if n:
        flips[0] = False
    return s0 * np.where(np.cumsum(flips) % 2 == 0, 1.0, -1.0)


def slow_two_state(rng: np.random.Generator, n: int, amplitude: float, switch: float) -> np.ndarray:
    """Family B's slow follow regime: a process between 0 and 2 x `amplitude` (mean `amplitude`), switching with
    probability `switch` a session from a random start -- `amplitude x (1 + rho_t)`."""
    return float(amplitude) * (1.0 + slow_sign(rng, n, switch))


def centre_within(values, weights) -> np.ndarray:
    """Values less their weighted mean over the block (the weights' finite, positive entries): family B's centring of
    C1-f's slow part within the judged block, so it shapes the dependence and adds nothing to the estimate."""
    v = np.asarray(values, dtype=float)
    w = np.asarray(weights, dtype=float)
    ok = np.isfinite(v) & (w > 0)
    tot = float(np.where(ok, w, 0.0).sum())
    if not tot > 0:
        raise ValueError("centre_within: no positive weight")
    return v - float(np.where(ok, v * w, 0.0).sum()) / tot


def grid_session_sums(V: np.ndarray, W: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(S, N) per session of a (session x mark) grid: the weighted sum of the values and the weights' sum (a NaN value
    carries no weight; F-03's `session_sums`)."""
    ok = np.isfinite(V) & (W > 0)
    w = np.where(ok, W, 0.0).astype(float)
    return (np.where(ok, V, 0.0) * w).sum(axis=1), w.sum(axis=1)


def b2_null_pooled(rng: np.random.Generator, choice_values: np.ndarray, judged_exists: np.ndarray, a_star: float, *,
                   mean_block: float, switch: float) -> np.ndarray:
    """One replicate's pair values on the judged grid (n_judged x marks), family B's form: the choice block's session
    vectors (n_choice x marks, NaN missing) resampled by one stationary bootstrap to the judged sessions, each judged
    offer taking the drawn session's value at its mark (a missing one dropped); the replicate's mean over its judged
    offers removed; plus `a_star x rho_t` (`slow_sign` at `switch`). Draws: the bootstrap's, then the drift's."""
    cv = np.asarray(choice_values, dtype=float)
    ex = np.asarray(judged_exists, dtype=bool)
    if cv.ndim != 2 or ex.ndim != 2 or cv.shape[1] != ex.shape[1]:
        raise ValueError("choice_values and judged_exists are (sessions x marks) grids on the same marks")
    nj = ex.shape[0]
    V = cv[stationary_indices(rng, cv.shape[0], nj, mean_block)]
    ok = ex & np.isfinite(V)
    if not ok.any():
        raise ValueError("B2: the replicate holds no judged offer")
    V = V - V[ok].mean()
    V = V + float(a_star) * slow_sign(rng, nj, switch)[:, None]
    return np.where(ok, V, np.nan)


def b2_null_strata(rng: np.random.Generator, choice_values: np.ndarray, choice_kind, judged_kind, judged_group,
                   judged_exists: np.ndarray, a_star: float, *, kinds: Sequence[str], mean_block: float,
                   switch: float) -> np.ndarray:
    """One replicate's pair values on the judged grid, F-03's form (`opening_stats.b2_replicate_sums` before its sums,
    bit for bit): each judged session of a declared kind (in `kinds`' order) filled from a choice session of its own
    kind by that kind's stationary bootstrap, a session of any other kind left empty; plus `a_star x rho_t`; then
    re-centred within the judged strata (`judged_group`), every offer's stratum mean over its mark removed."""
    ex = np.asarray(judged_exists, dtype=bool)
    nj = ex.shape[0]
    pi = np.zeros(nj, dtype=np.int64)
    filled = np.zeros(nj, dtype=bool)
    jk = np.asarray(judged_kind).astype(str)
    ck = np.asarray(choice_kind).astype(str)
    for kind in kinds:
        jrows = np.flatnonzero(jk == kind)
        if not len(jrows):
            continue
        src = np.flatnonzero(ck == kind)
        if len(src) == 0:
            raise ValueError(f"B2: no choice session of day kind {kind!r}")
        pi[jrows] = src[stationary_indices(rng, len(src), len(jrows), mean_block)]
        filled[jrows] = True
    V = np.asarray(choice_values, dtype=float)[pi] + float(a_star) * slow_sign(rng, nj, switch)[:, None]
    V[~filled] = np.nan
    ok = ex & np.isfinite(V)
    grp = np.asarray(judged_group)
    for g in np.unique(grp):
        rows = grp == g
        sub, mm = V[rows], ok[rows]
        cnt = mm.sum(axis=0)
        mu = np.where(cnt > 0, np.where(mm, sub, 0.0).sum(axis=0) / np.maximum(cnt, 1), 0.0)
        V[rows] = sub - mu[None, :]
    return np.where(ok, V, np.nan)


def b2_member_t(replicate: Callable[[np.random.Generator], tuple], replicates: int,
                key: Callable[[int], np.random.Generator], *, form: str, chunk: int = 500) -> np.ndarray:
    """B2's member t's (members x replicates): replicate i is `replicate(key(i))`, its session sums -- (S, N) for
    `form="one_sample"`, (S1, N1, S2, N2) for `"two_sample"`; computed in chunks (the chunking changes no draw);
    refused (`NotFinite`) when any t is not finite (F-03's `b2_t`, bit for bit, in the two-sample form)."""
    if form not in FORMS:
        raise ValueError(f"form is one of {FORMS}, not {form!r}")
    arity = 2 if form == "one_sample" else 4
    R = int(replicates)
    T = np.empty((len(MEMBERS), R))
    done = 0
    while done < R:
        r = min(int(chunk), R - done)
        cols = [replicate(key(done + q)) for q in range(r)]
        if any(len(c) != arity for c in cols):
            raise ValueError(f"a {form} replicate returns {arity} session-sum arrays")
        parts = [np.column_stack([c[i] for c in cols]) for i in range(arity)]
        T[:, done:done + r] = member_t_one_sample(*parts) if arity == 2 else member_t_two_sample(*parts)
        done += r
    if not np.isfinite(T).all():
        raise NotFinite(f"B2: {int((~np.isfinite(T)).sum())} replicate t's are not finite")
    return T


def b2_quantiles(T: np.ndarray, level: float) -> dict[int, float]:
    """Each member's (1 - level) quantile of its B2 t's (numpy's default rule), {block: quantile}."""
    lv = _level(level)
    q = {b: float(np.quantile(T[i], 1.0 - lv)) for i, b in enumerate(MEMBERS)}
    if not all(math.isfinite(v) for v in q.values()):
        raise NotFinite("B2: a quantile is not finite")
    return q


def b2_critical(replicate: Callable[[np.random.Generator], tuple], *, level: float, replicates: int,
                key: Callable[[int], np.random.Generator], form: str, chunk: int = 500) -> dict[int, float]:
    """B2's {member: (1 - level) quantile} from `replicates` replicates drawn as `b2_member_t` draws them."""
    return b2_quantiles(b2_member_t(replicate, replicates, key, form=form, chunk=chunk), level)


def block_mean_amplitude(per_session, block: int) -> float:
    """F-03's a*: the largest |mean| over the calendar's disjoint `block`-session blocks (`lift_bound`'s blocks, in
    session order) of a per-session series, sessions without a value left out of their block's mean."""
    x = np.asarray(per_session, float)
    bid, G = LB.block_index(len(x), block)
    best = 0.0
    for g in range(G):
        v = x[(bid == g) & np.isfinite(x)]
        if len(v):
            best = max(best, abs(float(v.mean())))
    return best


def year_mean_amplitude(per_session, years) -> float:
    """Family B's a*: the largest |mean| over calendar years of a per-session series (sessions without a value left
    out), `years` each session's calendar year."""
    x = np.asarray(per_session, float)
    y = np.asarray(years)
    if x.shape != y.shape:
        raise ValueError("one year a session")
    best = 0.0
    for yr in np.unique(y):
        v = x[(y == yr) & np.isfinite(x)]
        if len(v):
            best = max(best, abs(float(v.mean())))
    return best


# ================================================================================================ the conjoint MDL


@dataclass(frozen=True)
class ConjointMDL:
    """The conjoint MDL (`mdl`: the grid's, or the continuous one when no grid is given; infinity above the grid), the
    conjunction's power and each line's at every grid point, each line's own MDL, and the continuous MDL beside."""
    mdl: float
    grid: tuple[float, ...]
    conj_power: np.ndarray
    line_power: np.ndarray
    line_mdl: tuple[float, ...]
    mdl_continuous: float | None = None
    line_mdl_continuous: tuple[float, ...] | None = None
    power: float = MDL_POWER

    def as_dict(self) -> dict[str, Any]:
        return {"mdl": self.mdl, "power": self.power, "grid": list(self.grid),
                "conj_power": [float(x) for x in self.conj_power], "line_mdl": list(self.line_mdl),
                "mdl_continuous": self.mdl_continuous,
                "line_mdl_continuous": None if self.line_mdl_continuous is None else list(self.line_mdl_continuous)}


def _power(power: float) -> float:
    p = float(power)
    if not (0.0 < p < 1.0):
        raise ValueError(f"power lies in (0, 1), not {power!r}")
    return p


def _grid(grid) -> tuple[float, ...]:
    g = tuple(float(x) for x in grid)
    if not g or not all(math.isfinite(x) for x in g) or g[0] <= 0 or any(b <= a for a, b in zip(g, g[1:])):
        raise ValueError("the grid is a non-empty, finite, strictly increasing sequence of positive lifts")
    return g


def need_from_lowers(lowers, slopes=None) -> np.ndarray:
    """Per draw, the planted lift every line needs to pass: the largest over lines of -lower / slope (`lowers`
    draws x lines, or one line as a vector; `slopes` one positive value a line, default 1); infinity where a line's
    bound is not finite. One line at slope 1: `lift_bound.mdl_draws`'s crit x se - estimate."""
    L = np.asarray(lowers, dtype=float)
    if L.ndim == 1:
        L = L[:, None]
    s = np.ones(L.shape[1]) if slopes is None else np.asarray(slopes, dtype=float)
    if s.shape != (L.shape[1],) or not (np.isfinite(s).all() and (s > 0).all()):
        raise ValueError("one finite, positive slope a line")
    need = np.where(np.isfinite(L), -L / s[None, :], np.inf)
    return need.max(axis=1)


def mdl_from_need(need, power: float = MDL_POWER) -> float:
    """The `power` quantile of the needs by numpy's default (linear) rule; infinity when an infinite need is a
    neighbour of the quantile's position (Q-108's `_q` reading); refused on a NaN."""
    p = _power(power)
    v = np.asarray(need, dtype=float).ravel()
    if v.size == 0 or np.isnan(v).any():
        raise ValueError("the needs are a non-empty vector with no NaN")
    if np.isinf(v).any():
        if (v == -math.inf).any():
            raise ValueError("a need of minus infinity")
        srt = np.sort(v)
        h = (srt.size - 1) * p
        lo, hi = int(math.floor(h)), int(math.ceil(h))
        if srt[lo] == math.inf or srt[hi] == math.inf:
            return math.inf
        # numpy interpolates with the next order statistic even at weight zero, so an infinity beyond the neighbours
        # would give NaN: each infinity is replaced by the upper neighbour (finite here), which sorts at or above it and
        # leaves both neighbours' values and the weight as they are (first test run: NaN at [1, 2, inf, inf, inf], 0.25)
        v = np.where(np.isinf(v), srt[hi], v)
    return float(np.quantile(v, p))


def conjoint_mdl_grid(passes_at: Callable[[float], np.ndarray], grid, power: float = MDL_POWER) -> ConjointMDL:
    """Family B's grid form: `passes_at(L)` gives, on the same draws at every L, which lines pass (draws x lines, or a
    vector for one line); the conjoint MDL is the smallest grid L at which at least `power` of the draws pass every
    line, infinity above the grid; each line's own MDL beside."""
    p = _power(power)
    g = _grid(grid)
    conj, lines = [], []
    for L in g:
        P = np.asarray(passes_at(L), dtype=bool)
        if P.ndim == 1:
            P = P[:, None]
        conj.append(float(P.all(axis=1).mean()))
        lines.append(P.mean(axis=0))
    lp = np.vstack(lines)
    first = lambda col: next((L for L, x in zip(g, col) if x >= p), math.inf)   # noqa: E731
    return ConjointMDL(first(conj), g, np.array(conj), lp, tuple(first(lp[:, j]) for j in range(lp.shape[1])),
                       power=p)


def conjoint_mdl_linear(lowers0, slopes=None, grid=None, power: float = MDL_POWER) -> ConjointMDL:
    """The conjoint MDL of lines whose bound moves linearly in the planted lift (lower(L) = lower(0) + slope x L): the
    continuous MDL (`mdl_from_need`) and, on a declared grid, the grid's (a line passes at L when lower(0) + slope x L
    is above zero) -- `mdl` is the grid's when a grid is given."""
    L0 = np.asarray(lowers0, dtype=float)
    if L0.ndim == 1:
        L0 = L0[:, None]
    s = np.ones(L0.shape[1]) if slopes is None else np.asarray(slopes, dtype=float)
    need = need_from_lowers(L0, s)
    cont = mdl_from_need(need, power)
    own = tuple(mdl_from_need(need_from_lowers(L0[:, [j]], s[[j]]), power) for j in range(L0.shape[1]))
    if grid is None:
        return ConjointMDL(cont, (), np.array([]), np.zeros((0, L0.shape[1])), own, cont, own, _power(power))
    with np.errstate(invalid="ignore"):
        res = conjoint_mdl_grid(lambda L: L0 + L * s[None, :] > 0, grid, power)
    return ConjointMDL(res.mdl, res.grid, res.conj_power, res.line_power, res.line_mdl, cont, own, res.power)


# ================================================================================================ the screen rule


@dataclass(frozen=True)
class ScreenVerdict:
    screen: bool
    ratios: dict[str, float]
    cells: tuple[str, ...]
    factor: float

    def as_dict(self) -> dict[str, Any]:
        return {"declared_screen": self.screen, "surviving": list(self.cells), "factor": self.factor,
                "ratios": dict(self.ratios)}


def screen_rule(mdl: Mapping[str, float], bar: Mapping[str, float], factor: float = MDL_FACTOR) -> ScreenVerdict:
    """The family is declared a screen when every surviving cell's MDL exceeds `factor` times its bar (both in the
    same unit); no surviving cell is no screen. An MDL above the grid is infinite (above). Refused: a NaN or negative
    MDL, a bar not finite and positive, a factor not finite and positive, cells that differ between the two maps."""
    f = float(factor)
    if not (math.isfinite(f) and f > 0):
        raise ValueError(f"the factor is finite and positive, not {factor!r}")
    cells = tuple(mdl)
    if set(cells) != set(bar):
        raise ValueError(f"the MDLs' cells {sorted(cells)} differ from the bars' {sorted(bar)}")
    for c in cells:
        m, b = float(mdl[c]), float(bar[c])
        if math.isnan(m) or m < 0:
            raise NotFinite(f"cell {c}: the MDL {m!r} is NaN or negative")
        if not (math.isfinite(b) and b > 0):
            raise ValueError(f"cell {c}: the bar {b!r} is not finite and positive")
    ratios = {c: float(mdl[c]) / float(bar[c]) for c in cells}
    return ScreenVerdict(bool(cells) and all(mdl[c] > f * bar[c] for c in cells), ratios, cells, f)


# ================================================================================================ the power gate


@dataclass(frozen=True)
class GateVerdict:
    """The pre-pin power gate's reading: `closes` (the MDL above the factor times the bar: the family closes before its
    pin, taking no k), the MDL read, the rows it came from, and the scaled MDL beside (deciding nothing)."""
    closes: bool
    mdl80: float
    bar: float
    factor: float
    ratio: float
    k: int
    k_used: int
    supply: float
    size_used: int
    candidate: str
    scope: str
    value: str
    rows: tuple[dict, ...] = field(default_factory=tuple)
    beside_scaled: float = math.nan
    source: str = "table"

    def as_dict(self) -> dict[str, Any]:
        d = {k: getattr(self, k) for k in ("closes", "mdl80", "bar", "factor", "ratio", "k", "k_used", "supply",
                                           "size_used", "candidate", "scope", "value", "beside_scaled", "source")}
        d["rows"] = [dict(r) for r in self.rows]
        return d


def _refuse(msg: str) -> PowerGateRefused:
    return PowerGateRefused(f"REFUSED (the power gate): {msg}")


GATE_COLUMNS = ("row", "toy", "size", "value", "model", "candidate", "scope", "k", "mdl80")


def power_gate_from_table(table: pd.DataFrame, *, k: int, candidate: str, scope: str, value: str, supply: float,
                          bar: float, factor: float = MDL_FACTOR, source: str = "table") -> GateVerdict:
    """The gate on a power table in `q126_cal_power.csv`'s form (module docstring). `supply` is the family's declared
    trades on the judged block (counted from its schedule before any outcome), `bar` its value bar in the unit of
    `value`, `candidate` and `scope` the statistic its band takes under Q-126's adoption row."""
    if not (isinstance(k, (int, np.integer)) and int(k) in GATE_K_RANGE):
        raise _refuse(f"k = {k!r} is outside Q-126's calibrated range {GATE_K_RANGE[0]}..{GATE_K_RANGE[-1]} (its plan "
                      "7 item 5); a family numbered beyond it needs the range extended under its own row")
    if scope not in SCOPES:
        raise _refuse(f"scope {scope!r} is not one of {SCOPES}")
    if value not in TOY_OF_VALUE:
        raise _refuse(f"value {value!r} is not one of {tuple(TOY_OF_VALUE)}: the toys are read in those units only")
    sup, b, f = float(supply), float(bar), float(factor)
    if not (math.isfinite(sup) and sup >= 1):
        raise _refuse(f"the declared supply {supply!r} is not a finite count of trades")
    if not (math.isfinite(b) and b > 0):
        raise _refuse(f"the bar {bar!r} is not finite and positive")
    if not (math.isfinite(f) and f > 0):
        raise _refuse(f"the factor {factor!r} is not finite and positive")
    missing = [c for c in GATE_COLUMNS if c not in table.columns]
    if missing:
        raise _refuse(f"{source} lacks the columns {missing}")
    t = table[(table["row"].astype(str) == "toy") & (table["toy"].astype(str) == TOY_OF_VALUE[value])
              & (table["value"].astype(str) == value) & table["model"].astype(str).isin(TOY_MODELS)]
    if candidate not in set(t["candidate"].astype(str)):
        raise _refuse(f"{source} holds no toy row for the statistic {candidate!r}")
    t = t[(t["candidate"].astype(str) == candidate) & (t["scope"].astype(str) == scope)]
    ks = sorted({int(x) for x in pd.to_numeric(t["k"], errors="raise")})
    up = [x for x in ks if x >= int(k)]
    if not up:
        raise _refuse(f"{source} holds no k at or above {k} for {candidate} in scope {scope} (it holds {ks})")
    sizes = sorted({int(x) for x in pd.to_numeric(t["size"], errors="raise")})
    down = [z for z in sizes if z <= sup]
    if not down:
        raise _refuse(f"the declared supply {supply!r} is below the smallest toy size {sizes[:1]}: no power reading "
                      "exists for so few trades")
    k_used, size_used = up[0], down[-1]
    sel = t[(pd.to_numeric(t["k"]) == k_used) & (pd.to_numeric(t["size"]) == size_used)]
    models = list(sel["model"].astype(str))
    if sorted(models) != sorted(TOY_MODELS):
        raise _refuse(f"{source} holds the side models {sorted(models)} at k = {k_used}, size {size_used} for "
                      f"{candidate} in scope {scope}, not exactly {list(TOY_MODELS)}")
    m = pd.to_numeric(sel["mdl80"], errors="coerce").to_numpy(float)
    if np.isnan(m).any():
        raise _refuse(f"{source}: an MDL80 at k = {k_used}, size {size_used} is not a number")
    mdl80 = float(m.max())
    rows = tuple({c: (v.item() if hasattr(v, "item") else v) for c, v in r.items()}
                 for r in sel[list(GATE_COLUMNS)].to_dict("records"))
    return GateVerdict(bool(mdl80 > f * b), mdl80, b, f, mdl80 / b, int(k), int(k_used), sup, int(size_used),
                       str(candidate), str(scope), str(value), rows, mdl80 * math.sqrt(size_used / sup), source)


def power_gate(*, k: int, candidate: str, scope: str, value: str, supply: float, bar: float,
               factor: float = MDL_FACTOR, path: str | Path | None = None) -> GateVerdict:
    """The pre-pin power gate on Q-126's power file (`results/q126_cal_power.csv` unless `path` names another): refused
    until the file exists, and unless its manifest verifies, names `scripts/q126_calibrate.py`, is not exploratory,
    records a clean run and is not dirty; then `power_gate_from_table`. Imports `extended.results` (the vendored
    tree on sys.path): call it in a process of its own."""
    from extended import RESULTS_DIR

    p = Path(path) if path is not None else Path(RESULTS_DIR) / POWER_FILE
    if not p.is_file():
        shards = sorted(p.parent.glob(f"{p.stem}__*.csv")) if p.parent.is_dir() else []
        raise _refuse(f"{p} does not exist -- Q-126's calibration (`python {POWER_SCRIPT}`, its plan's 6.2) has not "
                      "written its power file" + (f" (shards {[s.name for s in shards]} are not the whole file)"
                                                  if shards else "")
                      + "; no family's power can be read before it, so no family whose C1 is one-sample is pinned "
                      "on it (E-094 (3))")
    from extended import results as XR

    ok, msg = XR.verify_result(p)
    if not ok:
        raise _refuse(f"{p}: {msg}")
    man = json.loads(Path(XR.manifest_path_for(p)).read_text(encoding="utf-8"))
    if man.get("script") != POWER_SCRIPT:
        raise _refuse(f"{p} was written by {man.get('script')!r}, not {POWER_SCRIPT}")
    if man.get("exploratory") is not False:
        raise _refuse(f"{p} is marked exploratory")
    if not (man.get("provenance") or {}).get("clean_run"):
        raise _refuse(f"{p} records no clean run (scripts/run_clean.py) in its manifest")
    if man.get("git_dirty") or str(man.get("git_commit", "")).endswith("-dirty"):
        raise _refuse(f"{p} was written from a dirty tree ({man.get('git_commit')})")
    table = pd.read_csv(p, float_precision="round_trip", low_memory=False)
    return power_gate_from_table(table, k=k, candidate=candidate, scope=scope, value=value, supply=supply, bar=bar,
                                 factor=factor, source=str(p))


__all__ = ["MEMBERS", "FORMS", "MDL_POWER", "MDL_FACTOR", "POWER_FILE", "POWER_SCRIPT", "GATE_K_RANGE", "TOY_OF_VALUE",
           "TOY_MODELS", "SCOPES", "GATE_COLUMNS", "NotFinite", "PowerGateRefused", "rng_of", "Member", "Line",
           "larger_of_one_sample", "larger_of_two_sample", "cons_bound_with_critical", "members_one_sample",
           "members_two_sample", "member_t_one_sample", "member_t_two_sample", "critical", "lower_bounds", "rejects_t",
           "stationary_indices", "slow_sign", "slow_two_state", "centre_within", "grid_session_sums",
           "b2_null_pooled", "b2_null_strata", "b2_member_t", "b2_quantiles", "b2_critical", "block_mean_amplitude",
           "year_mean_amplitude", "ConjointMDL", "need_from_lowers", "mdl_from_need", "conjoint_mdl_grid",
           "conjoint_mdl_linear", "ScreenVerdict", "screen_rule", "GateVerdict", "power_gate_from_table",
           "power_gate"]
