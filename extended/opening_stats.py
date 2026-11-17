"""F-03 (family O): the estimands, the twins, the controls and the critical values (sections 7, 9, 10, 11, 12; build
item 18.1 item 5). Engine-free: numpy, pandas, scipy and `extended.lift_bound` (at its pinned blob) only.

**The offers as matrices.** A block's offers are laid out as a (session x mark) grid (`Layout`): the block's calendar of
sessions (every trading session counted; `session` its ordinal) by P-16's marks (the population's 17:00 .. 08:25 and the
labels' marks), with each cell's value and flags; a missing offer is NaN / False. Strata g = (mark, day kind, calendar
year) are the grid's columns within each session's (day kind, year) group.

**C1** (7.2): `extended.lift_bound.placebo_selection_bound` on y = c - mu_g over every population offer, the in-state
flag selecting -- `cons` with the treated df (`SHIPPED`, `DIFF_DF_RULE`). **The larger-of rule** (11 item 1): each member
(`t21w`, `t42w`, `t63w`, `extended.lift_bound.diff_stats`) at the larger of its t critical value and B2's (1 - level)
quantile of the same member's t; `cons` passes only if all three lower bounds are above zero; its bound is their minimum.

**B2** (11 item 2): the null is the realised judged population; each replicate fills every judged session with a choice
span session **of its own day kind** (two stationary bootstraps of mean block 63, normal days and report days), its
offers that session's centred values at the same marks (a mark the drawn session lacks is dropped), plus a* x rho_t (a
sign switching with probability 1/63 a judged session, a random start), **re-centred within the judged strata**, the
members recomputed with the real judged weights (C1: the in-state flag against every population offer; C2: the
design's uses against the twin designs' uses). Replicate j draws from `default_rng([SEED_B2, line, j])`.

**a*** (11 item 3): the largest of (a) the choice span's largest |mean| over its disjoint 63-session blocks (in session
order; `lift_bound.block_index`'s blocks) of the per-session mean of y, (b) Stage 2's recorded follow lifts at 3R
(`mom15`, `lbrk5` in `s1_sided_coin.csv`; `lnbar1x4` in `s3_event_kinds.csv` and at latency 5 in `s3_latency.csv`; each
file's section `lift`, `mean_lift`), and (d) the judged block's largest |mean| over its disjoint 63-session blocks of
the per-session mean of the **out-of-state** offers' values, each centred by its own stratum's out-of-state mean.

**K0** (A11): `cons`'s size at the family's level on Q-16's `cluster` sign null (each offer or use 1/2 sign(a_s + e), the
session effect shared, icc 0.35), each replication the judged block's length of the count series from a uniform
circular offset; replication j from `default_rng([SEED_K0, cell, form, j])`; a cell killed when the 95 %
Clopper-Pearson interval lies wholly above the nominal. Counts only: no value is read.

**The clustered twin** (7.1): the state's own indicator shifted circularly, within each (calendar year, day kind)
sequence of sessions, by a uniform offset over the sequence's positions (`default_rng([SEED_TWIN, c, b, d])`, one
offset a sequence in (year, kind) order), all marks of a session together.

Every function that draws takes its generator's key explicitly (section 16's seeds); none has a default seed.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

import numpy as np
import pandas as pd
from scipy import stats

from extended import lift_bound as LB

#: section 16's seeds
SEED_STAGE_B = 20261980          # [.., 0] A4's skill; [.., 1] stage B's max-statistic; [.., 2] V_B's standard error
SEED_SHIFT = 20261981            # T-2's replacement walks [.., j]
SEED_TWIN = 20261982             # [.., c, b, d]
SEED_GATE = 20261983             # floor (iii)'s campaign
SEED_A10 = 20261984              # [.., class, share, j]
SEED_B2 = 20261985               # [.., line, j]
SEED_Q16 = 20261986
SEED_SCORECARD = 20261987        # [.., 0] paired draws; [.., 1] the denial ladder
SEED_TESTS = 20261988
SEED_K0 = 20261989               # [.., cell, form, j]
SEEDS = tuple(range(20261980, 20261990))
#: the blocks in the twin's seed (7.1): 0 judged, 1 choice, 2 the confirmation
BLOCK_JUDGED, BLOCK_CHOICE, BLOCK_CONFIRMATION = 0, 1, 2
TWIN_DRAWS = (0, 1)
#: B2's lines (11 item 2)
LINE_C1, LINE_C1_CLOSE, LINE_C2 = 0, 1, 2
B2_REPLICATES = 1_000_000
B2_MEAN_BLOCK = 63
#: 11 item 2's two stationary bootstraps: normal days and report days (sorted, the order the draws are made in); a
#: session of any other kind (FOMC, early close, no bar) is left empty -- it carries no offer of the population
B2_KINDS = ("b", "n")
SLOW_SWITCH = 1.0 / 63.0
MEMBERS = (21, 42, 63)
#: K0 (A11)
K0_REPLICATIONS = 200_000
K0_ICC = 0.35
K0_FORMS = {"c1_choice": 0, "c2_choice": 1, "c1_judged": 2, "c2_judged": 3, "confirmation": 4}
#: A10 (9): Table 9's classes, its two shares, 2,000 selections, two levels
A10_CLASSES = ("offer", "window", "session", "block5", "block21", "block63")
A10_SHARES = (0.25, 0.5)
A10_SELECTIONS = 2000
A10_LEVELS = (0.01, 0.05)
A10_INNER = 20_000
#: stage B (10)
STAGE_B_DRAWS = 2000
STAGE_B_MEAN_BLOCK = 63
STAGE_B_QUANTILE = 0.95
#: A4 (9): circular 21-session blocks, 2,000 draws, one-sided 95 %
A4_BLOCK, A4_DRAWS = 21, 2000
#: the kills (9)
K1_SESSIONS = 21
K1_YEARS = (2021, 2022, 2023)
K2_MAX, K2_PICK_MAX = 0.05, 0.04
K5_MAX_FALLBACK = 0.5
MDL_FACTOR = 3.0
BAR_DOLLARS = 500.0
FLATTEN_KIND = 2
SESSIONS_A_YEAR = 252.0


def rng_of(*key: int) -> np.random.Generator:
    return np.random.default_rng([int(k) for k in key])


# ------------------------------------------------------------------------------------------------ the layout


@dataclass
class Layout:
    """A block's offers on its (session x mark) grid. `sessions`: the block's calendar (sorted ISO dates); `marks`: the
    grid's marks; `kind` and `year` a session's; `group` its (kind, year) index; `values` {name: (n, M) float, NaN
    missing}; `flags` {name: (n, M) bool}; `exists` the offer exists (population or label); `population` its
    population offers."""
    sessions: list[str]
    marks: list[int]
    kind: np.ndarray
    year: np.ndarray
    group: np.ndarray
    groups: list[tuple[str, int]]
    exists: np.ndarray
    population: np.ndarray
    values: dict[str, np.ndarray] = field(default_factory=dict)
    flags: dict[str, np.ndarray] = field(default_factory=dict)

    @property
    def n(self) -> int:
        return len(self.sessions)


def layout(pop: pd.DataFrame, sessions: Sequence[str], *, kinds: Mapping[str, str] | None = None,
           values: Sequence[str] = ("c", "c_close", "rl", "rs"), flags: Sequence[str] = ()) -> Layout:
    """The frame's offers (one row an offer: `date`, `slot`, `day_kind`, `year`, `population`, the value and flag
    columns) on the calendar `sessions` (every session of the block, with or without an offer)."""
    cal = sorted(str(s) for s in sessions)
    pos = {d: i for i, d in enumerate(cal)}
    marks = sorted(int(m) for m in pd.unique(pop["slot"]))
    mpos = {m: k for k, m in enumerate(marks)}
    n, M = len(cal), len(marks)
    i = np.array([pos[str(d)] for d in pop["date"]], dtype=np.int64)
    k = np.array([mpos[int(m)] for m in pop["slot"]], dtype=np.int64)
    kd = dict(kinds) if kinds is not None else {}
    for d, kk in zip(pop["date"].astype(str), pop["day_kind"].astype(str)):
        kd.setdefault(d, kk)
    kind = np.array([kd.get(d, "") for d in cal], dtype=object)
    year = np.array([int(d[:4]) for d in cal], dtype=np.int64)
    groups = sorted({(str(a), int(b)) for a, b in zip(kind, year)})
    gpos = {g: j for j, g in enumerate(groups)}
    group = np.array([gpos[(str(a), int(b))] for a, b in zip(kind, year)], dtype=np.int64)
    exists = np.zeros((n, M), dtype=bool)
    exists[i, k] = True
    popm = np.zeros((n, M), dtype=bool)
    popm[i, k] = pop["population"].to_numpy(bool)
    L = Layout(cal, marks, kind, year, group, groups, exists, popm)
    for v in values:
        if v in pop.columns:
            a = np.full((n, M), np.nan)
            a[i, k] = pop[v].to_numpy(float)
            L.values[v] = a
    for f in flags:
        a = np.zeros((n, M), dtype=bool)
        a[i, k] = pop[f].to_numpy(bool)
        L.flags[f] = a
    return L


def centred(L: Layout, value: str, mask: np.ndarray | None = None) -> np.ndarray:
    """value - mu_g over the grid: mu_g the mean of the value over every existing offer of its stratum (mark, kind,
    year) -- `mask` restricts the offers the mean is taken over (and the result's support)."""
    V = L.values[value]
    m = L.exists & np.isfinite(V) if mask is None else (mask & np.isfinite(V))
    out = np.full(V.shape, np.nan)
    for g in range(len(L.groups)):
        rows = L.group == g
        sub, mm = V[rows], m[rows]
        cnt = mm.sum(axis=0)
        mu = np.where(cnt > 0, np.where(mm, sub, 0.0).sum(axis=0) / np.maximum(cnt, 1), np.nan)
        out[rows] = np.where(mm, sub - mu[None, :], np.nan)
    return out


def session_sums(V: np.ndarray, W: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(S, N) per session: the weighted sum of the values and the weights' sum (a NaN value carries no weight)."""
    ok = np.isfinite(V) & (W > 0)
    w = np.where(ok, W, 0.0).astype(float)
    return (np.where(ok, V, 0.0) * w).sum(axis=1), w.sum(axis=1)


# ------------------------------------------------------------------------------------------------ the clustered twin


def clustered_twin(L: Layout, state: np.ndarray, cell: int, block: int, draw: int) -> tuple[np.ndarray, dict]:
    """7.1's clustered placebo: (the twin's flags on the grid, the offsets by (kind, year)). Within each (year, kind)
    sequence of sessions, the state's indicator shifted circularly by a uniform offset over the sequence's positions,
    all marks of a session together; only where the twin's offer exists (a shift permutes the sequence's sessions, so
    each stratum keeps its count wherever every session of the sequence has the mark)."""
    rng = rng_of(SEED_TWIN, cell, block, draw)
    out = np.zeros_like(state, dtype=bool)
    offsets = {}
    for (kind, year) in sorted(L.groups, key=lambda g: (g[1], g[0])):
        rows = np.flatnonzero((L.kind == kind) & (L.year == year))
        n = len(rows)
        if n == 0:
            continue
        off = int(rng.integers(0, n))
        offsets[(kind, year)] = off
        src = rows[(np.arange(n) + off) % n]
        out[rows] = state[src] & L.population[rows]
    return out, offsets


# ------------------------------------------------------------------------------------------------ C1 and the rule


@dataclass
class Member:
    block: int
    estimate: float
    se: float
    df: float
    t_crit: float
    b2_crit: float
    crit: float
    lower: float


@dataclass
class Line:
    """A deciding line by the larger-of rule: its members, the bound (their minimum lower bound), pass, and the
    module's own nominal `cons` bound beside."""
    members: list[Member]
    bound: float
    passes: bool
    nominal: Any
    level: float

    def as_dict(self) -> dict[str, Any]:
        d = {"bound": self.bound, "passes": self.passes, "level": self.level,
             "nominal_bound": float(self.nominal.lower) if self.nominal is not None else float("nan"),
             "estimate": self.members[0].estimate if self.members else float("nan")}
        for m in self.members:
            for k in ("estimate", "se", "df", "t_crit", "b2_crit", "crit", "lower"):
                d[f"t{m.block}w_{k}"] = getattr(m, k)
        return d


def members_of(S1, N1, S2, N2) -> list[tuple[int, float, float, float]]:
    """(block, estimate, se, df) of each member, by `lift_bound.diff_stats` with the treated df."""
    out = []
    for b in MEMBERS:
        est, se, df = (float(v) for v in LB.diff_stats(S1, N1, S2, N2, block=b))
        out.append((b, est, se, df))
    return out


def larger_of(S1, N1, S2, N2, level: float, b2: Mapping[int, float] | None = None, nominal: Any = None) -> Line:
    """11 item 1's rule on one sample of session sums: each member at max(t, B2's quantile); `b2` {block: quantile}
    (None: the t's alone -- `cons` at its nominal values)."""
    mem = []
    for b, est, se, df in members_of(S1, N1, S2, N2):
        tc = float(stats.t.ppf(1.0 - level, df)) if df >= 1 else float("nan")
        q = float(b2[b]) if b2 is not None else float("-inf")
        if b2 is not None and not math.isfinite(q):
            raise NotFinite(f"B2's quantile of t{b}w is not finite: the rule is never quietly nominal (m6)")
        c = max(tc, q) if math.isfinite(tc) else float("nan")
        lo = est - c * se if (math.isfinite(se) and se > 0 and math.isfinite(c)) else float("nan")
        mem.append(Member(b, est, se, df, tc, q, c, lo))
    lows = [m.lower for m in mem]
    ok = all(math.isfinite(x) for x in lows)
    bound = min(lows) if ok else float("nan")
    return Line(mem, bound, bool(ok and bound > 0), nominal, float(level))


def c1_sums(y: np.ndarray, selected: np.ndarray, population: np.ndarray) -> tuple[np.ndarray, ...]:
    """(S1, N1, S2, N2): the in-state population offers against every population offer (the nested form)."""
    S1, N1 = session_sums(y, (selected & population).astype(float))
    S2, N2 = session_sums(y, population.astype(float))
    return S1, N1, S2, N2


def c1_line(L: Layout, y: np.ndarray, selected: np.ndarray, level: float, b2: Mapping[int, float] | None = None
            ) -> Line:
    """C1 (or C1-close on the close convention's y): the larger-of rule; the module's own `placebo_selection_bound` on
    the offers beside (its estimate is the line's)."""
    S1, N1, S2, N2 = c1_sums(y, selected, L.population)
    sess = np.repeat(np.arange(L.n)[:, None], len(L.marks), axis=1)
    m = L.population & np.isfinite(y)
    nom = LB.placebo_selection_bound(y[m], sess[m], selected[m], L.n, level=level)
    return larger_of(S1, N1, S2, N2, level, b2, nom)


def lift(L: Layout, y: np.ndarray, selected: np.ndarray) -> float:
    """L_c (7.2): the in-state offers' mean of the centred value (the twin's exact expectation is zero)."""
    m = selected & L.population & np.isfinite(y)
    return float(y[m].mean()) if m.any() else float("nan")


def halves(L: Layout, selected: np.ndarray) -> dict[str, float]:
    """7.3: L^long on l, L^short on r, each centred by its own strata means; their mean is L."""
    lo = lift(L, centred(L, "rl", L.population), selected)
    sh = lift(L, centred(L, "rs", L.population), selected)
    return {"long": lo, "short": sh, "mean": (lo + sh) / 2.0}


def two_sample_line(y1, s1, y2, s2, n_sessions: int, level: float, b2: Mapping[int, float] | None = None) -> Line:
    """C2's line (7.4): the design's uses against the twin designs' uses (values at their offers, sessions their
    ordinals), by the larger-of rule; `lift_bound.two_sample_bound` beside."""
    S1, N1 = LB.session_sums(y1, np.asarray(s1, np.int64), n_sessions)
    S2, N2 = LB.session_sums(y2, np.asarray(s2, np.int64), n_sessions)
    nom = LB.two_sample_bound(y1, np.asarray(s1, np.int64), y2, np.asarray(s2, np.int64), n_sessions, level=level)
    return larger_of(S1, N1, S2, N2, level, b2, nom)


def v_line(u_d: float, mean_dv: float, D: float) -> float:
    """7.4: V = u_d x mean_dv(c) x D / (1 + 3) dollars a year."""
    return float(u_d) * float(mean_dv) * float(D) / 4.0


def lambda_bar(mean_dv: float, u_c: float, bar: float = BAR_DOLLARS) -> float:
    """A9: the bar in net R, 4 x $500 / (mean_dv(c) x u_c)."""
    return 4.0 * float(bar) / (float(mean_dv) * float(u_c))


def openings_a_start_year(n_openings: int, start_sessions: Sequence[int]) -> float:
    """u_d (7.4): the design's openings per start-year of its replays -- the openings over the starts' years (each
    start's replay length in sessions / 252)."""
    years = float(np.sum(np.asarray(start_sessions, float))) / SESSIONS_A_YEAR
    return float(n_openings) / years if years > 0 else float("nan")


# ------------------------------------------------------------------------------------------------ B2


def stationary_indices(rng: np.random.Generator, n_src: int, n_out: int, mean_block: float) -> np.ndarray:
    """A stationary bootstrap's source positions (circular, mean block `mean_block`)."""
    if n_src <= 0:
        raise ValueError("a bootstrap needs at least one source session")
    starts = rng.random(n_out) < 1.0 / float(mean_block)
    if n_out:
        starts[0] = True
    jumps = rng.integers(0, n_src, n_out)
    t = np.arange(n_out)
    last = np.maximum.accumulate(np.where(starts, t, 0))
    return (jumps[last] + (t - last)) % n_src


def slow_sign(rng: np.random.Generator, n: int, switch: float = SLOW_SWITCH) -> np.ndarray:
    """rho_t: a two-state Markov sign switching with probability `switch` a session, a random start."""
    s0 = 1.0 if rng.random() < 0.5 else -1.0
    flips = rng.random(n) < switch
    if n:
        flips[0] = False
    return s0 * np.where(np.cumsum(flips) % 2 == 0, 1.0, -1.0)


@dataclass
class B2Inputs:
    """B2's fixed parts: the choice span's centred values (n_c x M on the judged grid's marks) and day kinds, the judged
    layout's kinds, (kind, year) groups and existing offers, and the two samples' weights."""
    choice_values: np.ndarray
    choice_kind: np.ndarray
    judged_kind: np.ndarray
    judged_group: np.ndarray
    judged_exists: np.ndarray
    W1: np.ndarray
    W2: np.ndarray


def b2_replicate_sums(inp: B2Inputs, a_star: float, rng: np.random.Generator) -> tuple[np.ndarray, ...]:
    """One replicate's (S1, N1, S2, N2): the realised judged population as the null (11 item 2) -- each judged normal
    or report day filled from a choice session of its own kind by a stationary bootstrap (mean block 63; the declared two
    bootstraps, `B2_KINDS`; a session of any other kind left empty), plus a* x rho_t,
    re-centred within the judged strata, weighted by the real judged samples."""
    nj, M = inp.judged_exists.shape
    pi = np.zeros(nj, dtype=np.int64)
    filled = np.zeros(nj, dtype=bool)
    jk = np.asarray(inp.judged_kind).astype(str)
    ck = np.asarray(inp.choice_kind).astype(str)
    for kind in B2_KINDS:                                    # the declared two, in sorted order (V3)
        jrows = np.flatnonzero(jk == kind)
        if not len(jrows):
            continue
        src = np.flatnonzero(ck == kind)
        if len(src) == 0:
            raise ValueError(f"B2: no choice session of day kind {kind!r}")
        pi[jrows] = src[stationary_indices(rng, len(src), len(jrows), B2_MEAN_BLOCK)]
        filled[jrows] = True
    V = inp.choice_values[pi] + float(a_star) * slow_sign(rng, nj)[:, None]
    V[~filled] = np.nan                                      # a session of another kind is left empty
    ok = inp.judged_exists & np.isfinite(V)
    for g in np.unique(inp.judged_group):
        rows = inp.judged_group == g
        sub, mm = V[rows], ok[rows]
        cnt = mm.sum(axis=0)
        mu = np.where(cnt > 0, np.where(mm, sub, 0.0).sum(axis=0) / np.maximum(cnt, 1), 0.0)
        V[rows] = sub - mu[None, :]
    V = np.where(ok, V, np.nan)
    S1, N1 = session_sums(V, inp.W1)
    S2, N2 = session_sums(V, inp.W2)
    return S1, N1, S2, N2


def member_t(S1, N1, S2, N2) -> np.ndarray:
    """Each member's t (members x replicates) from session sums of shape (n, replicates)."""
    out = []
    for b in MEMBERS:
        est, se, _ = LB.diff_stats(S1, N1, S2, N2, block=b)
        with np.errstate(invalid="ignore", divide="ignore"):
            out.append(np.where(np.isfinite(se) & (se > 0), est / se, np.nan))
    return np.vstack(out)


def b2_quantiles(inp: B2Inputs, a_star: float, level: float, line: int, replicates: int = B2_REPLICATES,
                 seed: int = SEED_B2, keep: bool = False, chunk: int = 500, prefix: tuple[int, ...] | None = None
                 ) -> tuple[dict[int, float], np.ndarray | None]:
    """Each member's (1 - level) quantile of its t under B2's null ({block: quantile}); replicate j from
    `default_rng([seed, line, j])` (or `[*prefix, j]` when a test gives its own key), computed in chunks of `chunk`
    replicates (the chunking changes no draw). `keep` returns the replicates' t's too (members x replicates)."""
    T = b2_t(inp, a_star, replicates, (lambda i: rng_of(*prefix, i)) if prefix is not None
             else (lambda i: rng_of(seed, line, i)), chunk=chunk)
    return quantiles_of(T, level), (T if keep else None)


def block_mean_amplitude(per_session: np.ndarray, block: int = 63) -> float:
    """The largest |mean| over the calendar's disjoint `block`-session blocks (in session order, `lift_bound`'s
    blocks) of a per-session series (sessions without a value left out of their block's mean)."""
    x = np.asarray(per_session, float)
    bid, G = LB.block_index(len(x), block)
    best = 0.0
    for g in range(G):
        v = x[(bid == g) & np.isfinite(x)]
        if len(v):
            best = max(best, abs(float(v.mean())))
    return best


def per_session_mean(V: np.ndarray, mask: np.ndarray) -> np.ndarray:
    ok = mask & np.isfinite(V)
    cnt = ok.sum(axis=1)
    return np.where(cnt > 0, np.where(ok, V, 0.0).sum(axis=1) / np.maximum(cnt, 1), np.nan)


def amplitude_a(L_choice: Layout, y_choice: np.ndarray, mask: np.ndarray) -> float:
    """a*'s (a): the choice span's largest |63-block mean| of the per-session mean of y over `mask`'s offers."""
    return block_mean_amplitude(per_session_mean(y_choice, mask))


def amplitude_d(L_judged: Layout, value: str, out_of_state: np.ndarray) -> float:
    """a*'s (d): the judged block's largest |63-block mean| of the per-session mean of the out-of-state offers' values,
    each centred by its own stratum's out-of-state mean -- no in-state offer enters."""
    y = centred(L_judged, value, out_of_state)
    return block_mean_amplitude(per_session_mean(y, out_of_state))


#: a*'s (b): Stage 2's recorded follow lifts at 3R (E-040; Q-61): (file, rule, latency or None)
FOLLOW_LIFTS = (("s1_sided_coin.csv", "mom15", None), ("s1_sided_coin.csv", "lbrk5", None),
                ("s3_event_kinds.csv", "lnbar1x4", None), ("s3_latency.csv", "lnbar1x4", 5.0))


def amplitude_b(results_dir) -> tuple[float, list[dict[str, Any]]]:
    """a*'s (b), read at run time: the largest |mean_lift| at R 3.0 over `FOLLOW_LIFTS` (each file's section `lift`,
    its manifest verified first). Upward only: it can raise a critical value and choose nothing."""
    from pathlib import Path

    from extended.results import verify_result

    rows, best = [], 0.0
    for name, rule, lat in FOLLOW_LIFTS:
        p = Path(results_dir) / name
        ok, msg = verify_result(p)
        if not ok:
            raise ValueError(f"REFUSED (F-03): {name}: {msg}")
        d = pd.read_csv(p, float_precision="round_trip", low_memory=False)
        d = d[(d["section"].astype(str) == "lift") & (d["rule"].astype(str) == rule)
              & (pd.to_numeric(d["R"], errors="coerce") == 3.0)]
        if lat is not None:
            d = d[pd.to_numeric(d["latency"], errors="coerce") == float(lat)]
        if len(d) != 1:
            raise ValueError(f"REFUSED (F-03): {name} holds {len(d)} lift rows for {rule} at 3R"
                             + (f", latency {lat:g}" if lat is not None else ""))
        v = abs(float(d["mean_lift"].iloc[0]))
        rows.append({"file": name, "rule": rule, "latency": lat, "abs_mean_lift": v})
        best = max(best, v)
    return best, rows


# ------------------------------------------------------------------------------------------------ K0


def k0_counts_null(rng: np.random.Generator, N1s: np.ndarray, N2s: np.ndarray, form: str, n_judged: int
                   ) -> tuple[np.ndarray, ...]:
    """One replication's (S1, N1, S2, N2) on the cluster sign null: the counts from a uniform circular offset; each offer
    or use 1/2 sign(a_s + e), a_s shared by the session's offers and both samples (icc 0.35). `form` 'nested' (C1: the
    in-state offers inside every offer) or 'pair' (C2: two designs' uses)."""
    nc = len(N1s)
    idx = (int(rng.integers(0, nc)) + np.arange(int(n_judged))) % nc
    N1, N2 = np.asarray(N1s)[idx].astype(np.int64), np.asarray(N2s)[idx].astype(np.int64)
    p = stats.norm.cdf(rng.standard_normal(int(n_judged)) * math.sqrt(K0_ICC) / math.sqrt(1 - K0_ICC))
    if form == "nested":
        u1 = rng.binomial(N1, p)
        ur = rng.binomial(N2 - N1, p)
        S1 = 0.5 * (2 * u1 - N1)
        S2 = S1 + 0.5 * (2 * ur - (N2 - N1))
    elif form == "pair":
        S1 = 0.5 * (2 * rng.binomial(N1, p) - N1)
        S2 = 0.5 * (2 * rng.binomial(N2, p) - N2)
    else:
        raise ValueError(f"K0's form is 'nested' or 'pair', not {form!r}")
    return S1.astype(float), N1.astype(float), S2.astype(float), N2.astype(float)


@dataclass
class K0Verdict:
    rejections: int
    replications: int
    level: float
    ci_lo: float
    ci_hi: float
    lax: bool

    def as_dict(self) -> dict[str, Any]:
        return {"rejections": self.rejections, "replications": self.replications, "level": self.level,
                "rate": self.rejections / self.replications, "ci_lo": self.ci_lo, "ci_hi": self.ci_hi,
                "ratio": self.rejections / self.replications / self.level, "lax": self.lax}


def k0_rejections_from_sums(S1, N1, S2, N2, level: float) -> int:
    """`cons`'s rejections at `level` over replications given as session-sum columns (n, replications)."""
    rj, _ = LB.diff_many_levels("cons", S1, N1, S2, N2, [level])
    return int(rj[0].sum())


def k0(N1s, N2s, form: str, n_judged: int, level: float, rng_for: Callable[[int], np.random.Generator],
       replications: int = K0_REPLICATIONS, chunk: int = 2000) -> K0Verdict:
    """A11: `cons`'s rejections at `level` on the sign null over `replications`; replication j's draws from
    `rng_for(j)` (the family's: `default_rng([SEED_K0, cell, form, j])`); the verdict the Clopper-Pearson interval's
    and nothing else (lax when its lower end is above the nominal). Reads counts only."""
    rej, done = 0, 0
    while done < replications:
        r = min(chunk, replications - done)
        cols = [k0_counts_null(rng_for(done + q), N1s, N2s, form, n_judged) for q in range(r)]
        S1, N1, S2, N2 = (np.column_stack([c[i] for c in cols]) for i in range(4))
        rej += k0_rejections_from_sums(S1, N1, S2, N2, level)
        done += r
    lo, hi = LB.clopper_pearson(rej, done)
    return K0Verdict(rej, done, float(level), lo, hi, bool(lo > level))


def k0_family(N1s, N2s, form: str, n_judged: int, level: float, cell: int, form_index: int,
              replications: int = K0_REPLICATIONS) -> K0Verdict:
    """K0 with the declared generators `[SEED_K0, cell, form, j]`."""
    return k0(N1s, N2s, form, n_judged, level, lambda j: rng_of(SEED_K0, cell, form_index, j), replications)


# ------------------------------------------------------------------------------------------------ A10


def a10_selection(rng: np.random.Generator, model: str, share: float, population: np.ndarray) -> np.ndarray:
    """One random selection independent of the outcomes in a Table 9 class (Q-16's `_sel_batch`'s models on the grid):
    `offer` each offer independently; `window` a contiguous run of round(share x the session's offers) offers each
    session from a uniform start (circular within the session); `session` whole sessions independently; `blockL` whole
    sessions in L-session blocks from a random phase."""
    n, M = population.shape
    if model == "offer":
        return population & (rng.random((n, M)) < share)
    if model == "window":
        out = np.zeros_like(population)
        for s in range(n):
            cols = np.flatnonzero(population[s])
            m = len(cols)
            if not m:
                continue
            L = max(1, int(np.rint(share * m)))
            a = int(math.floor(rng.random() * m))
            out[s, cols[(a + np.arange(L)) % m]] = True
        return out
    if model == "session":
        f = rng.random(n) < share
    elif model.startswith("block"):
        Lb = int(model[5:])
        phase = int(rng.integers(0, Lb))
        nb = (n + Lb) // Lb + 1
        fb = rng.random(nb) < share
        f = fb[(np.arange(n) + phase) // Lb]
    else:
        raise ValueError(f"unknown class {model!r}; Table 9's are {A10_CLASSES}")
    return population & f[:, None]


def a10(L: Layout, y: np.ndarray, classes: Sequence[str] = A10_CLASSES, shares: Sequence[float] = A10_SHARES,
        selections: int = A10_SELECTIONS, levels: Sequence[float] = A10_LEVELS) -> pd.DataFrame:
    """A10 (9): `cons` (treated) through `placebo_selection_bound` on y = c - mu_g over the choice span's population, at
    one-sided 1 % and 5 %, on random selections; selection j of (class, share) from `default_rng([SEED_A10, class,
    share, j])` (class its index in Table 9's order, share its index); a class lax when the rejection rate's 95 %
    Clopper-Pearson interval lies wholly above the nominal."""
    rows = []
    for ci, model in enumerate(classes):
        for si, share in enumerate(shares):
            cols = []
            for j in range(int(selections)):
                sel = a10_selection(rng_of(SEED_A10, ci, si, j), model, float(share), L.population)
                cols.append(c1_sums(y, sel, L.population))
            S1, N1, S2, N2 = (np.column_stack([c[i] for c in cols]) for i in range(4))
            rj, _ = LB.diff_many_levels("cons", S1, N1, S2, N2, list(levels))
            for a, r in zip(levels, rj):
                k = int(r.sum())
                lo, hi = LB.clopper_pearson(k, int(selections))
                rows.append({"class": model, "share": float(share), "level": float(a), "selections": int(selections),
                             "rejections": k, "ci_lo": lo, "ci_hi": hi, "lax": bool(lo > a)})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------------------------ the kills


def k1_sessions_by_year(L: Layout, selected: np.ndarray) -> dict[int, int]:
    """A5: the sessions holding an in-state offer, by year."""
    has = (selected & L.population).any(axis=1)
    return {int(y): int(has[L.year == y].sum()) for y in sorted(set(int(v) for v in L.year))}


def k1_killed(by_year: Mapping[int, int], years: Sequence[int] = K1_YEARS) -> bool:
    return any(int(by_year.get(int(y), 0)) < K1_SESSIONS for y in years)


def k2_shares(kl: np.ndarray, ks: np.ndarray, selected: np.ndarray, year: np.ndarray) -> dict[str, float]:
    """A6: among the in-state offers, both sides pooled, the unresolved (flatten-kind) share at 3R overall and by year."""
    f = np.concatenate([np.asarray(kl)[selected] == FLATTEN_KIND, np.asarray(ks)[selected] == FLATTEN_KIND])
    yy = np.concatenate([np.asarray(year)[selected], np.asarray(year)[selected]])
    out = {"overall": float(f.mean()) if len(f) else float("nan")}
    for y in sorted(set(int(v) for v in yy)):
        out[str(y)] = float(f[yy == y].mean())
    return out


def k2_killed(shares: Mapping[str, float], years: Sequence[int] = K1_YEARS, limit: float = K2_MAX) -> bool:
    vals = [shares.get("overall", float("nan"))] + [shares.get(str(y), float("nan")) for y in years]
    return any(not (v <= limit + 1e-12) for v in vals)


def k2_worst_year(shares: Mapping[str, float], years: Sequence[int] = K1_YEARS) -> float:
    return max(float(shares.get(str(y), float("nan"))) for y in years)


def k5_killed(fallback_share: float) -> bool:
    """A7: more than one half of a design's openings taken as fallbacks kills the cell."""
    return not (float(fallback_share) <= K5_MAX_FALLBACK + 1e-12)


# ------------------------------------------------------------------------------------------------ A4


def a4_skill(y: np.ndarray, y_hat: np.ndarray, band_cols: Mapping[str, Sequence[int]], rows: np.ndarray
             ) -> dict[str, dict[str, float]]:
    """A4 (9): per band, the per-session MSE of y under the HAR against under y = 0 on the out-of-fold sessions `rows`;
    the improvement's one-sided 95 % lower bound by circular 21-session blocks, 2,000 draws (`[SEED_STAGE_B, 0]`, one
    generator for every band in `band_cols`' order)."""
    rng = rng_of(SEED_STAGE_B, 0)
    out = {}
    for band, cols in band_cols.items():
        Y, F_ = y[rows][:, list(cols)], y_hat[rows][:, list(cols)]
        ok = np.isfinite(Y) & np.isfinite(F_)
        cnt = ok.sum(axis=1)
        keep = cnt > 0
        mse0 = np.where(ok, Y ** 2, 0.0).sum(axis=1)[keep] / cnt[keep]
        mse1 = np.where(ok, (Y - F_) ** 2, 0.0).sum(axis=1)[keep] / cnt[keep]
        d = mse0 - mse1
        n = len(d)
        nb = max(1, int(math.ceil(n / A4_BLOCK)))
        starts = rng.integers(0, n, size=(A4_DRAWS, nb))
        idx = (starts[:, :, None] + np.arange(A4_BLOCK)[None, None, :]).reshape(A4_DRAWS, -1)[:, :n] % n
        boot = d[idx].mean(axis=1)
        lb = float(d.mean() - np.quantile(boot - d.mean(), 0.95))
        out[band] = {"sessions": int(n), "improvement": float(d.mean()), "lower95": lb, "skill": bool(lb > 0)}
    return out


# ------------------------------------------------------------------------------------------------ stage B


def _strata_lift(C: np.ndarray, pop: np.ndarray, sel: np.ndarray, group: np.ndarray, n_groups: int) -> float:
    ok = pop & np.isfinite(C)
    Cz = np.where(ok, C, 0.0)
    num = np.zeros((n_groups, C.shape[1]))
    den = np.zeros((n_groups, C.shape[1]))
    np.add.at(num, group, Cz)
    np.add.at(den, group, ok.astype(float))
    mu = np.where(den > 0, num / np.maximum(den, 1), 0.0)
    s = sel & ok
    k = s.sum()
    return float(((Cz - mu[group]) * s).sum() / k) if k else float("nan")


def stage_b_bootstrap(L: Layout, value: str, selections: Mapping[str, np.ndarray], draws: int = STAGE_B_DRAWS,
                      seed_key: tuple[int, int] = (SEED_STAGE_B, 1)) -> dict[str, Any]:
    """10 item 1: L_c for each eligible cell on the span, and its stationary bootstrap of sessions (mean block 63,
    2,000 draws from one generator `[SEED_STAGE_B, 1]`), each draw recomputing L_c, the strata means included, on the
    resampled sessions; SE_c the draws' sd; q_B the 95th percentile over the centred draws of max_c (L*_c - L_c) / SE_c."""
    C = L.values[value]
    names = list(selections)
    est = {c: _strata_lift(C, L.population, selections[c], L.group, len(L.groups)) for c in names}
    rng = rng_of(*seed_key)
    B = np.empty((int(draws), len(names)))
    for b in range(int(draws)):
        pi = stationary_indices(rng, L.n, L.n, STAGE_B_MEAN_BLOCK)
        for i, c in enumerate(names):
            B[b, i] = _strata_lift(C[pi], L.population[pi], selections[c][pi], L.group[pi], len(L.groups))
    se = {c: float(np.std(B[:, i], ddof=1)) for i, c in enumerate(names)}
    Z = np.column_stack([(B[:, i] - est[c]) / se[c] for i, c in enumerate(names)]) if names else np.zeros((draws, 0))
    q = float(np.quantile(Z.max(axis=1), STAGE_B_QUANTILE)) if names else float("nan")
    return {"estimate": est, "se": se, "q_B": q, "draws": int(draws)}


def d_bootstrap_se(y1, s1, y2, s2, n_sessions: int, draws: int = STAGE_B_DRAWS,
                   seed_key: tuple[int, int] = (SEED_STAGE_B, 2)) -> tuple[float, float]:
    """V_B's per-opening difference D_B and its standard error: a stationary bootstrap of the span's sessions (mean
    block 63, 2,000 draws, `[SEED_STAGE_B, 2]`), each resampled session bringing its uses of both samples (the uses held
    fixed; the values centred once on the span)."""
    S1, N1 = LB.session_sums(y1, np.asarray(s1, np.int64), n_sessions)
    S2, N2 = LB.session_sums(y2, np.asarray(s2, np.int64), n_sessions)
    D = float(S1.sum() / N1.sum() - S2.sum() / N2.sum())
    if not math.isfinite(D):
        raise NotFinite("D_B is not finite")
    rng = rng_of(*seed_key)
    out = np.empty(int(draws))
    for b in range(int(draws)):
        pi = stationary_indices(rng, n_sessions, n_sessions, STAGE_B_MEAN_BLOCK)
        with np.errstate(invalid="ignore", divide="ignore"):
            out[b] = S1[pi].sum() / N1[pi].sum() - S2[pi].sum() / N2[pi].sum()
    if not np.isfinite(out).all():
        raise NotFinite("a bootstrap draw of D_B is not finite")
    return D, float(np.std(out, ddof=1))


def stage_b_pick(cells: Sequence[str], est: Mapping[str, float], se: Mapping[str, float], q_B: float,
                 eligible: Mapping[str, bool], v_lower: Mapping[str, float]) -> dict[str, Any]:
    """10 items 2-4: Kill B when no eligible cell has L_c / SE_c above q_B; else the pick is the eligible cell above q_B
    with the largest lower limit of V_B, ties to the cell listed first."""
    for c in cells:
        if eligible.get(c, False) and not (math.isfinite(est[c]) and math.isfinite(se[c]) and se[c] > 0
                                           and math.isfinite(q_B) and math.isfinite(v_lower[c])):
            raise NotFinite(f"stage B: {c}'s L, SE, q_B or V_B's lower limit is not finite")
    above = [c for c in cells if eligible.get(c, False) and est[c] / se[c] > q_B]
    if not above:
        return {"killed": True, "pick": None, "above": []}
    best = max(v_lower[c] for c in above)
    pick = next(c for c in cells if c in above and v_lower[c] == best)
    return {"killed": False, "pick": pick, "above": above}


# ------------------------------------------------------------------------------------------------ A9


A9_MIN_OFFSET = 63


def within_kind_index(L: Layout, base: np.ndarray, offset: int) -> np.ndarray:
    """Each session of `base` moved `offset` places along its own day kind's sequence of sessions (circular)."""
    out = np.empty(len(base), dtype=np.int64)
    for kind in np.unique(L.kind):
        seq = np.flatnonzero(L.kind == kind)
        pos = {int(x): i for i, x in enumerate(seq)}
        for t, s_ in enumerate(base):
            if L.kind[s_] == kind:
                out[t] = seq[(pos[int(s_)] + int(offset)) % len(seq)]
    return out


def a9_mdl(L: Layout, y: np.ndarray, selected: np.ndarray, n_judged: int, level: float, power: float = 0.8
           ) -> dict[str, float]:
    """A9: the minimum detectable lift of C1 at the family's level and 80 % power on a judged-length calendar, from the
    cell's choice-span in-state pattern (its first `n_judged` sessions, circularly) and the population's centred values
    moved along each day kind's own sequence by every offset from 63 to n - 63 (the build read's m2: no value sits
    within a quarter of its own session's selection, so the in-state mean is not read), each window re-centred within
    its own strata; each member at the larger of its t and the windows' (1 - level) quantile of its t under this null;
    the MDL the `power` quantile over the windows of max over members of (crit x se - estimate). Deterministic."""
    n = L.n
    base = np.arange(int(n_judged)) % n
    sel = selected[base] & L.population[base]
    offs = list(range(A9_MIN_OFFSET, max(A9_MIN_OFFSET + 1, n - A9_MIN_OFFSET)))
    est, se, df = (np.full((len(offs), len(MEMBERS)), np.nan) for _ in range(3))
    for w, o in enumerate(offs):
        idx = within_kind_index(L, base, o)
        V = y[idx].copy()
        pop = L.population[idx] & L.population[base]
        grp = L.group[base]
        for g in np.unique(grp):
            rows = grp == g
            sub, mm = V[rows], pop[rows] & np.isfinite(V[rows])
            cnt = mm.sum(axis=0)
            mu = np.where(cnt > 0, np.where(mm, sub, 0.0).sum(axis=0) / np.maximum(cnt, 1), 0.0)
            V[rows] = sub - mu[None, :]
        S1, N1, S2, N2 = c1_sums(V, sel & pop, pop)
        for i, (b, e, s_, d) in enumerate(members_of(S1, N1, S2, N2)):
            est[w, i], se[w, i], df[w, i] = e, s_, d
    with np.errstate(invalid="ignore", divide="ignore"):
        T = est / se
    if not np.isfinite(T).all():
        raise NotFinite("A9: a window's member t is not finite")
    q = np.quantile(T, 1.0 - level, axis=0)
    tc = stats.t.ppf(1.0 - level, np.maximum(df, 1))
    crit = np.maximum(tc, q[None, :])
    need = np.max(crit * se - est, axis=1)
    return {"mdl": float(np.quantile(need, power)), "windows": int(len(offs)),
            "null_quantiles": [float(x) for x in q], "offsets": [offs[0], offs[-1]]}


# ------------------------------------------------------------------------------------------------ A10's consequence


class NotFinite(RuntimeError):
    """A replicate's t, a quantile, a standard error or a value the rule needs is not finite: refused, never a fall-back
    (the build read's m6)."""


def b2_t(inp: B2Inputs, a_star: float, replicates: int, key: Callable[[int], np.random.Generator], chunk: int = 500
         ) -> np.ndarray:
    """B2's member t's (members x replicates), replicate i from `key(i)`; refused (`NotFinite`) when any is not finite."""
    T = np.empty((len(MEMBERS), int(replicates)))
    done = 0
    while done < int(replicates):
        r = min(int(chunk), int(replicates) - done)
        cols = [b2_replicate_sums(inp, a_star, key(done + q)) for q in range(r)]
        S1, N1, S2, N2 = (np.column_stack([c[i] for c in cols]) for i in range(4))
        T[:, done:done + r] = member_t(S1, N1, S2, N2)
        done += r
    if not np.isfinite(T).all():
        raise NotFinite(f"B2: {int((~np.isfinite(T)).sum())} replicate t's are not finite")
    return T


def quantiles_of(T: np.ndarray, level: float) -> dict[int, float]:
    q = {b: float(np.quantile(T[i], 1.0 - float(level))) for i, b in enumerate(MEMBERS)}
    if not all(math.isfinite(v) for v in q.values()):
        raise NotFinite("B2: a quantile is not finite")
    return q


def sub_layout(L: Layout, rows: np.ndarray) -> Layout:
    """The layout of the sessions `rows` (a boolean mask): its own (kind, year) groups, the same marks."""
    rows = np.asarray(rows, bool)
    sessions = [s for s, k in zip(L.sessions, rows) if k]
    kind, year = L.kind[rows], L.year[rows]
    groups = sorted({(str(a), int(b)) for a, b in zip(kind, year)})
    gpos = {g: j for j, g in enumerate(groups)}
    group = np.array([gpos[(str(a), int(b))] for a, b in zip(kind, year)], dtype=np.int64)
    out = Layout(sessions, list(L.marks), kind, year, group, groups, L.exists[rows], L.population[rows])
    out.values = {k: v[rows] for k, v in L.values.items()}
    out.flags = {k: v[rows] for k, v in L.flags.items()}
    return out


@dataclass
class ConsequenceResult:
    rows: list[dict[str, Any]]
    closed: bool
    b2_runs: int
    decisions: dict[tuple[float, float], list[bool]] = field(default_factory=dict)


def a10_consequence(L: Layout, value: str, model: str, a_b: float, *, shares: Sequence[float] = A10_SHARES,
                    levels: Sequence[float] = A10_LEVELS, selections: int = A10_SELECTIONS, inner: int = A10_INNER,
                    shortcut: bool = True, test_year: int = 2023) -> ConsequenceResult:
    """A10's consequence (9; the lead's reading, E-112): the deciding rule itself -- each member at the larger of its t
    and B2's (1 - level) quantile -- on the same A10 replications as a pseudo-judged split. Selection j of (class,
    share) is A10's own (`[A10 seed, class, share, j]`) restricted to `test_year`; the statistic on that year's values
    centred within its strata; B2 from the earlier years' centred values, within day kind, a* the largest of (a) on
    the earlier years, (b) `a_b`, and (d) on the test year's out-of-state offers of that selection; the inner draws
    `[A10 seed, class, share, j, i]` (A10's replication key extended by the inner index), `inner` of them, shared by
    both levels. **The exact shortcut** (`shortcut`): the larger-of rule rejects only where nominal `cons` rejects (each
    member's critical value is at least its t), and nominal at 1 % only where it rejects at 5 %, so B2 runs only for the
    selections nominal `cons` rejects at the largest level; per-selection keys mean a skipped selection changes no
    other's draws. The cell is closed when any (share, level)'s rejection rate has its 95 % Clopper-Pearson interval
    wholly above the nominal."""
    ci = A10_CLASSES.index(model)
    te = L.year == int(test_year)
    tr = (L.year < int(test_year))
    Lte, Ltr = sub_layout(L, te), sub_layout(L, tr)
    yte = centred(Lte, value, Lte.population)
    ytr = centred(Ltr, value, Ltr.population)
    a_a = amplitude_a(Ltr, ytr, Ltr.population)
    rows, closed, runs = [], False, 0
    decisions: dict[tuple[float, float], list[bool]] = {}
    lv = sorted(float(a) for a in levels)
    for share in shares:
        si = list(A10_SHARES).index(float(share))
        rej = {a: 0 for a in lv}
        for a in lv:
            decisions[(float(share), a)] = []
        for j in range(int(selections)):
            sel_all = a10_selection(rng_of(SEED_A10, ci, si, j), model, float(share), L.population)
            sel = sel_all[te] & Lte.population
            S1, N1, S2, N2 = c1_sums(yte, sel, Lte.population)
            nominal = {a: larger_of(S1, N1, S2, N2, a).passes for a in lv}
            if shortcut and not nominal[lv[-1]]:
                for a in lv:
                    decisions[(float(share), a)].append(False)
                continue
            a_d = amplitude_d(Lte, value, Lte.population & ~sel)
            inp = B2Inputs(ytr, Ltr.kind, Lte.kind, Lte.group, Lte.exists & Lte.population, sel.astype(float),
                           Lte.population.astype(float))
            T = b2_t(inp, max(a_a, float(a_b), a_d), inner, lambda i, j=j: rng_of(SEED_A10, ci, si, j, i))
            runs += 1
            for a in lv:
                d_ = bool(larger_of(S1, N1, S2, N2, a, quantiles_of(T, a)).passes)
                decisions[(float(share), a)].append(d_)
                rej[a] += int(d_)
        for a in lv:
            lo, hi = LB.clopper_pearson(rej[a], int(selections))
            lax = bool(lo > a)
            closed = closed or lax
            rows.append({"check": "A10_consequence", "class": model, "share": float(share), "level": a,
                         "selections": int(selections), "rejections": rej[a], "ci_lo": lo, "ci_hi": hi, "lax": lax,
                         "a": a_a, "b": float(a_b), "inner": int(inner), "shortcut": bool(shortcut)})
    return ConsequenceResult(rows, closed, runs, decisions)


def implied_class(mean_run: float, share_sessions: float) -> str:
    """The persistence class a cell's run lengths imply (6.6, beside): `offer` when its state fills a part of most
    sessions, else the session-level class nearest its mean in-state run (1 session, 5, 21, 63)."""
    if share_sessions > 0.9:
        return "window"
    marks = {"session": 1.0, "block5": 5.0, "block21": 21.0, "block63": 63.0}
    return min(marks, key=lambda k: abs(math.log(max(mean_run, 1e-9)) - math.log(marks[k])))


__all__ = [n for n, v in list(globals().items()) if not n.startswith("_") and type(v).__name__ != "module"
           and n not in ("annotations", "field", "dataclass", "Any", "Callable", "Mapping", "Sequence")]
