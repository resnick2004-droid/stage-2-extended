"""H3-A's report and laxity-stop code (`prereg/H3_three_way.md` sections 8, 10, 11, 14, 17; E-279).

Built after H3's pin (E-279), without touching any file of H3's build commit `4c07026`.

What it decides (and what it never decides):
- **The laxity stop** reads **only the 54 pooled size counts** of H3-A:
  - A1: 2 null classes (`antithetic`, `disjoint`) x 2 composites (`p_b`, `toy_composite`) x 3 bounds
    (`bound_22a`, `eb`, `betting`) x 3 feasible levels (`0.05`, `0.01`, `0.001`) = **36 pooled counts**;
  - A2: 1 null class (`exact_centred`) x 2 composites (`p_b`, `toy_composite`) x 3 bounds x 3 feasible levels =
    **18 pooled counts**;
  - Total = **54 pooled counts**.
  (`bound_22a` denotes section 2.2 (a)'s bound: Hoeffding on `p_b`, McDiarmid on `toy_composite`.)
- Each pooled count `(rejections, n, level)` is tested one-sided at **alpha_each = 0.05 / 54** (Bonferroni across the
  54 pooled counts, family-wise false-stop rate at most 0.05 when every size is correct): its exact one-sided
  Clopper-Pearson lower bound at confidence `1 - 0.05 / 54` is `beta.ppf(0.05 / 54, rejections, n - rejections + 1)`
  for `rejections >= 1` (and `0.0` for `rejections == 0`). It is a **laxity** when `cp_one_sided_lo > level`
  (`stop_on_pooled`).
- **The stop's inputs are tied to the declaration** (the red team's B-4, `evaluate_laxity_stop`): it refuses unless
  every pooled n is the declared n -- R x floor(seeds a side / J'), R from Appendix A (`DECLARED_R`), the seeds a side
  `SEEDS` for the antithetic and exact-centred classes and one `DISJOINT` half for the disjoint class, J' =
  `J_PRIME` (`declared_pooled_n`) -- unless the 1080 per-history counts are all present, one per (cell, history) over
  histories 0 .. R - 1, each at its declared per-history n, and unless each pooled count is the sum of its R
  per-history counts (`pool_counts`, the one pooling the runner also uses).
- **`three_way_stats.size_label`** (E-052's two-sided 95 % Clopper-Pearson interval) is reported beside every pooled
  and per-history count, **never deciding**; so is the empirical-Bernstein bound's range term at J' (`eb_range_term`,
  the red team's m-7: at J' it is large, so the EB counts can fail only on a gross error -- printed beside them).
- **The 1080 per-history counts** (720 for A1, 360 for A2) are reported beside, **never stopping anything**.
- **Premise kills** (section 11: "a pool not centred -- |its mean| above 4 standard errors, two-sided, ... --, an
  asymmetric twin, a term out of range, a key guard refusal"): `check_null_pool` runs
  `three_way_stats.null_pool_guards` (refusing all-zero pools and disjoint pools outside variance tolerance) AND
  centring (`|mean| <= CENTRING_Z * se`, two-sided); `check_symmetry` is the asymmetric twin's kill (a sign test in the
  centring test's own form, at the same `CENTRING_Z`: see its docstring, a form the declaration does not spell out).
  The note's "no serial dependence in seed order" (its 2.6) is not in section 11's kill list and is not implemented.
- **A2's exact centre of the clipped composite** (the red team's B-2): `exact_composite_centre` -- the expectation of
  the clipped composite of a seed set, computed exactly from each start's exact per-unit law: a dimension whose
  arithmetic range lies inside its caps is linear on its whole support (the clip never binds); an indicator dimension
  whose cap can bind takes the exact Poisson-binomial law of its count (`clipped_indicator_expectation`); any other
  dimension refuses (`H3ReportRefused`) -- never an approximation.
- **A4's 426 pass rates and 60 MDLs** (`a4_cells`, `a4_mdl_lines`, `summarise_a4`) and **A3's 6 history-null rates**
  (`summarise_a3`) are pooled here from the per-history files, reported, never stopping anything.
- **Pre-run gate** (E-279, section 16): refuses unless `prereg/H3_three_way.md` matches its pinned LF sha256 under the
  pin grammar in `DECISIONS.md`, template v3's hash row (`prereg/TEMPLATE_design_search.md` sha256) is pinned in
  `DECISIONS.md` and carries R-10's declared clauses, and (when `check_build_commit=True`) `4c07026`'s build files
  are unchanged. **The report's inputs** (`verify_inputs`, the red team's m-5): every manifest verifies, every input is
  clean (`git_dirty: false`), all come from one commit, and that commit's build and report files equal this tree's.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

import numpy as np
from scipy.stats import beta as _beta
from scipy.stats import binom as _binom

from extended import family_stats as FS
from extended import three_way_h3a as H
from extended import three_way_stats as ST

FAMILY_STOP_ALPHA: float = 0.05
A1_NULL_CLASSES: tuple[str, ...] = ("antithetic", "disjoint")
A2_NULL_CLASSES: tuple[str, ...] = ("exact_centred",)
COMPOSITES: tuple[str, ...] = ("p_b", "toy_composite")
#: section 8's three bounds: 2.2 (a)'s (Hoeffding on p_b, McDiarmid on toy_composite), empirical-Bernstein, betting
BOUNDS: tuple[str, ...] = ("bound_22a", "eb", "betting")
LEVELS: tuple[float, ...] = tuple(float(a) for a in H.LEVELS)

A1_POOLED_TOTAL: int = len(A1_NULL_CLASSES) * len(COMPOSITES) * len(BOUNDS) * len(LEVELS)  # 36
A2_POOLED_TOTAL: int = len(A2_NULL_CLASSES) * len(COMPOSITES) * len(BOUNDS) * len(LEVELS)  # 18
POOLED_TOTAL: int = A1_POOLED_TOTAL + A2_POOLED_TOTAL                                       # 54
STOP_ALPHA_PER_COUNT: float = FAMILY_STOP_ALPHA / POOLED_TOTAL                              # 0.05 / 54

#: Appendix A's R per part (`A1 same-design nulls ... R=20`, `A2 exact-centred toy null ... R=20`, `A3 history null
#: ... R=200`, `A4 plants ... R=10`; `docs/plans/scripts/three_way/three_way_arith.py` `parts()`, held equal by
#: `tests/test_h3a_report.py`)
DECLARED_R: dict[str, int] = {"A1": 20, "A2": 20, "A3": H.A3_HISTORIES, "A4": 10}
#: the dimension of the toy composite whose per-unit value is an indicator by its definition (a first payout by the
#: horizon: `scripts/h3a_run.py` `unit_values`), so its seed-set count has an exact Poisson-binomial law
INDICATOR_DIMS: frozenset[str] = frozenset({"paid_by_63"})

H3_DECL_PATH = "prereg/H3_three_way.md"
H3_PIN_SHA256 = "98c5bb94a4f3d0a921c47e683999db0577c65c78c360003ef25072238f5bc2fc"
H3_BUILD_COMMIT = "4c07026"
H3_BUILD_FILES: tuple[str, ...] = (
    "extended/three_way_keys.py",
    "extended/three_way_fastkeys.py",
    "extended/three_way_seeds.py",
    "extended/three_way_redraw.py",
    "extended/three_way_journey.py",
    "extended/three_way_runner.py",
    "extended/three_way_s1.py",
    "extended/three_way_stats.py",
    "extended/three_way_h3a.py",
)
#: the report's own code: an input's commit must hold these as this tree does (m-5)
REPORT_FILES: tuple[str, ...] = ("extended/h3a_report.py", "scripts/h3a_run.py")
H3_PIN_RE = re.compile(r"`(prereg/H3_three_way\.md)` sha256 `([0-9a-f]{64})`")
TEMPLATE_PIN_RE = re.compile(r"`(prereg/TEMPLATE_design_search\.md)` sha256 `([0-9a-f]{64})`")
R10_CLAUSES = (
    "s = max(1, ceil(sigma sqrt(T) / sqrt(`WALK_MAX`)))",
    "**One T for both s and n (s-b):** T is the limit known at the fill for every row",
    "| the 15:10 CT flatten | the stopped walk, T to the flatten |",
    "| its max hold | the stopped walk, T to the max hold's end |",
    "n = round(sigma^2 T / s^2)",
)


class H3ReportRefused(RuntimeError):
    """Refused before reporting or running: invalid cell set, missing pin, or failed premise."""


def _require_exact_int(v: Any, label: str) -> int:
    if isinstance(v, np.integer):
        v = int(v)
    if not isinstance(v, int) or isinstance(v, bool):
        raise H3ReportRefused(f"{label} must be an exact int, got {v!r}")
    return v


def _require_prob(v: Any, label: str) -> float:
    if isinstance(v, bool) or not isinstance(v, (int, float, np.floating)):
        raise H3ReportRefused(f"{label} must be a real number in (0, 1), got {v!r}")
    x = float(v)
    if not math.isfinite(x) or not (0.0 < x < 1.0):
        raise H3ReportRefused(f"{label} must be finite and in (0, 1), got {v!r}")
    return x


@dataclass(frozen=True)
class SizeCount:
    """One size-check cell (pooled over R histories, or one history beside)."""
    part: str            # "A1" or "A2"
    null_class: str      # "antithetic", "disjoint", or "exact_centred"
    composite: str       # "p_b" or "toy_composite"
    bound: str           # "bound_22a", "eb", or "betting"
    level: float         # one of H.LEVELS
    rejections: int
    n: int
    history: int | None = None   # None for pooled counts; exact int history index for beside per-history counts

    def key(self) -> tuple[str, str, str, str, float]:
        return (self.part, self.null_class, self.composite, self.bound, float(self.level))


def expected_pooled_keys() -> set[tuple[str, str, str, str, float]]:
    """The exact 54 (part, null_class, composite, bound, level) keys that the H3-A laxity stop reads."""
    keys: set[tuple[str, str, str, str, float]] = set()
    for nc in A1_NULL_CLASSES:
        for comp in COMPOSITES:
            for b in BOUNDS:
                for lvl in LEVELS:
                    keys.add(("A1", nc, comp, b, lvl))
    for nc in A2_NULL_CLASSES:
        for comp in COMPOSITES:
            for b in BOUNDS:
                for lvl in LEVELS:
                    keys.add(("A2", nc, comp, b, lvl))
    assert len(keys) == POOLED_TOTAL == 54
    return keys


def seeds_a_side(null_class: str) -> int:
    """The seed columns a side of a null class's pairs holds at the declared size: `SEEDS` for the antithetic and the
    exact-centred classes (each seed's base against its own twin, or f against beta on one coin field), one `DISJOINT`
    half for the disjoint class (each seed of the first set against one of the second); the halves must be equal."""
    if null_class in ("antithetic", "exact_centred"):
        return int(H.SEEDS)
    if null_class == "disjoint":
        (a0, a1), (b0, b1) = H.DISJOINT
        if a1 - a0 != b1 - b0 or a1 > b0:
            raise H3ReportRefused(f"the declared DISJOINT sets {H.DISJOINT} are not two equal, disjoint halves")
        return int(a1 - a0)
    raise H3ReportRefused(f"no declared null class {null_class!r}")


def declared_per_history_n() -> dict[tuple[str, str], int]:
    """(part, null class) -> the size count's n on one history: floor(seeds a side / J')."""
    out = {}
    for part, classes in (("A1", A1_NULL_CLASSES), ("A2", A2_NULL_CLASSES)):
        for nc in classes:
            out[(part, nc)] = seeds_a_side(nc) // int(H.J_PRIME)
    return out


def declared_pooled_n() -> dict[tuple[str, str], int]:
    """(part, null class) -> the pooled n: R x floor(seeds a side / J') (B-4's arithmetic)."""
    return {k: DECLARED_R[k[0]] * v for k, v in declared_per_history_n().items()}


def declared_histories() -> dict[str, tuple[int, ...]]:
    """The histories each size part pools: 0 .. R - 1 (Appendix A's R)."""
    return {part: tuple(range(DECLARED_R[part])) for part in ("A1", "A2")}


def one_sided_cp_lower(rejections: int, n: int, alpha: float = STOP_ALPHA_PER_COUNT) -> float:
    """Exact one-sided Clopper-Pearson lower confidence bound at confidence 1 - alpha.

    For k >= 1, returns p_lo such that P(Binomial(n, p_lo) >= k) = alpha, i.e. Beta(k, n - k + 1).ppf(alpha).
    For k == 0, returns 0.0.
    """
    k = _require_exact_int(rejections, "rejections")
    n_i = _require_exact_int(n, "n")
    a = _require_prob(alpha, "alpha")
    if n_i <= 0 or k < 0 or k > n_i:
        raise H3ReportRefused(f"invalid count: rejections={k}, n={n_i}")
    if k == 0:
        return 0.0
    return float(_beta.ppf(a, k, n_i - k + 1))


def eb_range_term(j: int, alpha: float) -> float:
    """The empirical-Bernstein bound's range term at J replicates in [-1, 1]: (7 ln(2/alpha) / 3) x 2 / (J - 1)
    (`three_way_stats.eb_lower`'s last term), printed beside the EB counts (m-7)."""
    j = _require_exact_int(j, "J")
    if j < 2:
        raise H3ReportRefused("the range term needs at least two replicates")
    return (7.0 * math.log(2.0 / _require_prob(alpha, "alpha")) / 3.0) * 2.0 / (j - 1)


def score_pooled_cell(c: SizeCount, *, alpha_each: float = STOP_ALPHA_PER_COUNT) -> dict:
    """Evaluate one pooled size count under section 11's one-sided stop (and E-052's two-sided label beside)."""
    if c.history is not None:
        raise H3ReportRefused("a pooled cell cannot carry a history index")
    lvl = _require_prob(c.level, "level")
    lo_stop = one_sided_cp_lower(c.rejections, c.n, alpha_each)
    lax_stop = bool(lo_stop > lvl)
    beside = ST.size_label(c.rejections, c.n, lvl)
    return {
        "part": c.part,
        "null_class": c.null_class,
        "composite": c.composite,
        "bound": c.bound,
        "level": lvl,
        "rejections": c.rejections,
        "n": c.n,
        "rate": c.rejections / c.n,
        "stop_alpha": float(alpha_each),
        "stop_cp_one_sided_lo": lo_stop,
        "stop_lax": lax_stop,
        "beside_e052_cp_lo": beside["cp_lo"],
        "beside_e052_cp_hi": beside["cp_hi"],
        "beside_e052_label": beside["label"],
        "beside_eb_range_term_at_j_prime": eb_range_term(int(H.J_PRIME), lvl) if c.bound == "eb" else float("nan"),
    }


def score_per_history_beside(c: SizeCount) -> dict:
    """Annotate one per-history size count beside (never decides or stops anything)."""
    if c.history is None:
        raise H3ReportRefused("a per-history beside cell must carry a history index")
    h_idx = _require_exact_int(c.history, "history")
    k = _require_exact_int(c.rejections, "rejections")
    n_i = _require_exact_int(c.n, "n")
    lvl = _require_prob(c.level, "level")
    if n_i <= 0 or k < 0 or k > n_i:
        raise H3ReportRefused(f"invalid per-history count: rejections={k}, n={n_i}")
    beside = ST.size_label(k, n_i, lvl)
    return {
        "part": c.part,
        "history": h_idx,
        "null_class": c.null_class,
        "composite": c.composite,
        "bound": c.bound,
        "level": lvl,
        "rejections": k,
        "n": n_i,
        "rate": beside["rate"],
        "beside_e052_cp_lo": beside["cp_lo"],
        "beside_e052_cp_hi": beside["cp_hi"],
        "beside_e052_label": beside["label"],
        "decides": False,
    }


def pool_counts(per_history: Iterable[SizeCount]) -> list[SizeCount]:
    """The pooled counts: for each cell, the sum of its per-history rejections and of its per-history n (the one
    pooling of H3-A: the runner writes what this returns, and the stop checks its inputs against it). Refused: a row
    without a history, a (cell, history) given twice."""
    acc: dict[tuple, list[int]] = {}
    seen: set[tuple] = set()
    for c in per_history:
        if c.history is None:
            raise H3ReportRefused("pool_counts reads per-history rows only")
        hk = (*c.key(), _require_exact_int(c.history, "history"))
        if hk in seen:
            raise H3ReportRefused(f"duplicate per-history cell: {hk}")
        seen.add(hk)
        a = acc.setdefault(c.key(), [0, 0])
        a[0] += _require_exact_int(c.rejections, "rejections")
        a[1] += _require_exact_int(c.n, "n")
    return [SizeCount(p, nc, comp, b, lvl, k, n) for (p, nc, comp, b, lvl), (k, n) in sorted(acc.items())]


def stop_on_pooled(pooled: Iterable[SizeCount]) -> dict:
    """Section 11's one-sided stop on exactly the 54 declared pooled cells (no input-consistency checks: those are
    `evaluate_laxity_stop`'s). Refuses a missing, extra or duplicate cell and a per-history row."""
    pooled_list = list(pooled)
    want = expected_pooled_keys()
    seen: set[tuple[str, str, str, str, float]] = set()
    for c in pooled_list:
        if c.history is not None:
            raise H3ReportRefused("per-history row passed in pooled counts")
        lvl = _require_prob(c.level, "level")
        k = (c.part, c.null_class, c.composite, c.bound, lvl)
        if k in seen:
            raise H3ReportRefused(f"duplicate pooled cell: {k}")
        seen.add(k)
    if seen != want:
        missing = sorted(want - seen)
        extra = sorted(seen - want)
        raise H3ReportRefused(
            f"pooled cells must be the exact 54 declared cells (missing={len(missing)}, extra={len(extra)})"
        )
    scored_pooled = [score_pooled_cell(c, alpha_each=STOP_ALPHA_PER_COUNT) for c in pooled_list]
    if len(scored_pooled) != POOLED_TOTAL:
        raise H3ReportRefused(f"internal error: scored {len(scored_pooled)} pooled rows != {POOLED_TOTAL}")
    lax_cells = [r for r in scored_pooled if r["stop_lax"]]
    return {
        "pooled_total": POOLED_TOTAL,
        "a1_pooled": A1_POOLED_TOTAL,
        "a2_pooled": A2_POOLED_TOTAL,
        "family_stop_alpha": FAMILY_STOP_ALPHA,
        "stop_alpha_per_count": STOP_ALPHA_PER_COUNT,
        "lax_count": len(lax_cells),
        "stop_h3d": bool(lax_cells),
        "verdict": "FAIL_LAXITY_STOP_H3D" if lax_cells else "PASS_NO_LAXITY",
        "lax_cells": lax_cells,
        "pooled_rows": scored_pooled,
    }


def evaluate_laxity_stop(pooled: Iterable[SizeCount], per_history: Iterable[SizeCount], *,
                         pooled_n: Mapping[tuple[str, str], int] | None = None,
                         histories: Mapping[str, Sequence[int]] | None = None) -> dict:
    """Apply H3-A's declared laxity stop (section 11, E-279) to the 54 pooled counts ONLY, after tying its inputs to
    the declaration (B-4). Refuses unless:
    - `pooled` holds the exact 54 declared keys, once each;
    - each pooled n is its declared n (`declared_pooled_n`; `pooled_n` overrides it for a test's own sizes only);
    - `per_history` holds every declared cell once for each history of its part (`declared_histories`, 0 .. R - 1),
      so 1080 rows at the declared sizes, each at its per-history n (the pooled n over R);
    - each pooled count is the sum of its per-history counts (`pool_counts`).
    The per-history counts are reported beside and NEVER affect `stop_h3d`."""
    pooled_list = list(pooled)
    per_hist_list = list(per_history)
    want = expected_pooled_keys()
    n_want = dict(declared_pooled_n() if pooled_n is None else pooled_n)
    h_want = {p: tuple(int(h) for h in v) for p, v in (declared_histories() if histories is None else histories).items()}

    # the keys first (stop_on_pooled refuses a missing, extra or duplicate cell)
    stop_on_pooled(pooled_list)
    for c in pooled_list:
        nk = (c.part, c.null_class)
        if nk not in n_want:
            raise H3ReportRefused(f"no declared n for {nk}")
        if _require_exact_int(c.n, "n") != int(n_want[nk]):
            raise H3ReportRefused(f"pooled cell {c.key()} has n={c.n}, not the declared n={n_want[nk]} "
                                  "(R x floor(seeds a side / J'))")

    seen_hist: set[tuple] = set()
    scored_hist = []
    for c in per_hist_list:
        row = score_per_history_beside(c)
        base_k = (row["part"], row["null_class"], row["composite"], row["bound"], row["level"])
        if base_k not in want:
            raise H3ReportRefused(f"undeclared per-history cell key: {base_k}")
        hk = (*base_k, row["history"])
        if hk in seen_hist:
            raise H3ReportRefused(f"duplicate per-history cell: {hk}")
        seen_hist.add(hk)
        if row["history"] not in h_want.get(row["part"], ()):
            raise H3ReportRefused(f"per-history cell {hk}: history {row['history']} is not one of {row['part']}'s "
                                  f"declared histories")
        per_n = int(n_want[(row["part"], row["null_class"])]) // len(h_want[row["part"]])
        if row["n"] != per_n:
            raise H3ReportRefused(f"per-history cell {hk} has n={row['n']}, not the declared per-history n={per_n}")
        scored_hist.append(row)
    need = {(*k, h) for k in want for h in h_want.get(k[0], ())}
    if seen_hist != need:
        raise H3ReportRefused(f"per-history cells must be every declared cell under every declared history "
                              f"({len(need)} rows): missing={len(need - seen_hist)}, extra={len(seen_hist - need)}")

    sums = {c.key(): (c.rejections, c.n) for c in pool_counts(per_hist_list)}
    for c in pooled_list:
        got = sums.get(c.key())
        if got != (c.rejections, c.n):
            raise H3ReportRefused(f"pooled cell {c.key()} = ({c.rejections}, {c.n}) is not the sum of its "
                                  f"per-history counts {got}")

    out = stop_on_pooled(pooled_list)
    out["per_history_count"] = len(scored_hist)
    out["per_history_beside"] = scored_hist
    return out


# ------------------------------------------------------------------------------------------------ the premises


def check_centring(D, *, z_max: float = H.CENTRING_Z) -> dict:
    """Section 11 premise check: finite non-degenerate pool with |mean(D)| <= CENTRING_Z * se(D) (two-sided)."""
    if isinstance(z_max, bool) or not isinstance(z_max, (int, float)) or not math.isfinite(float(z_max)) or float(z_max) <= 0:
        raise H3ReportRefused(f"z_max must be positive and finite, got {z_max!r}")
    x = np.asarray(D, dtype=float).ravel()
    if x.size < 2 or not np.isfinite(x).all():
        raise H3ReportRefused("centring check requires at least 2 finite values")
    if not (x != 0.0).any():
        raise H3ReportRefused("all-zero null pool refused (2.3)")
    mean = float(x.mean())
    sd = float(x.std(ddof=1))
    if sd == 0.0:
        raise H3ReportRefused("zero-variance null pool refused")
    se = sd / math.sqrt(x.size)
    z = abs(mean) / se
    ok = bool(z <= float(z_max))
    return {"n": int(x.size), "mean": mean, "sd": sd, "se": se, "abs_z": z, "z_max": float(z_max), "ok": ok}


def check_null_pool(D, *, single_arm_var: float | None = None, var_tol: float = 0.5,
                    z_max: float = H.CENTRING_Z) -> dict:
    """Combined section 11 premise check: `three_way_stats.null_pool_guards` + two-sided centring."""
    if isinstance(var_tol, bool) or not isinstance(var_tol, (int, float)) or not math.isfinite(float(var_tol)) or float(var_tol) < 0:
        raise H3ReportRefused(f"var_tol must be finite and >= 0, got {var_tol!r}")
    try:
        ST.null_pool_guards(D, single_arm_var=single_arm_var, var_tol=float(var_tol))
    except ValueError as exc:
        raise H3ReportRefused(str(exc)) from exc
    return check_centring(D, z_max=z_max)


def check_symmetry(D, *, z_max: float = H.CENTRING_Z) -> dict:
    """The asymmetric twin's kill (section 11), in the centring test's own form: under the twin's exactness (the note's
    2.3 (a): Delta is symmetric about zero given H), each nonzero replicate is positive with probability exactly one
    half, so the count of positive replicates among the n nonzero is Binomial(n, 1/2); the twin is **asymmetric** when
    |positives - n/2| exceeds `CENTRING_Z` standard errors sqrt(n/4), two-sided. It catches a skew the centring test
    misses -- a pool centred in mean whose median is off zero (the m-8 defect: a twin that reverses an outcome instead
    of complementing every uniform). The form is this build's reading (the declaration names the kill, not its
    statistic): the lead's row records it."""
    x = np.asarray(D, dtype=float).ravel()
    if x.size == 0 or not np.isfinite(x).all():
        raise H3ReportRefused("the symmetry check reads a finite, non-empty pool")
    nz = x[x != 0.0]
    if nz.size == 0:
        raise H3ReportRefused("all-zero null pool refused (2.3)")
    pos = int((nz > 0).sum())
    n = int(nz.size)
    z = abs(pos - n / 2.0) / math.sqrt(n / 4.0)
    return {"n_nonzero": n, "positives": pos, "abs_z": z, "z_max": float(z_max), "ok": bool(z <= float(z_max))}


def lag1_autocorrelation(D) -> float:
    """A pool's lag-1 autocorrelation in seed order (the note's 2.6 "no serial dependence in seed order"), printed
    beside the premises and deciding nothing (c2 m-10): sum (x_i - m)(x_{i+1} - m) / sum (x_i - m)^2; NaN for fewer
    than three values or a constant pool."""
    x = np.asarray(D, dtype=float).ravel()
    if x.size < 3 or not np.isfinite(x).all():
        return float("nan")
    d = x - x.mean()
    den = float((d * d).sum())
    return float((d[:-1] * d[1:]).sum() / den) if den > 0 else float("nan")


# ------------------------------------------------------------------------------------------------ A2's exact centre


def clipped_indicator_expectation(dim: ST.Dimension, p_by_start: Sequence[float], seeds_in_set: int) -> float:
    """E[clip((K / n - lo) / (hi - lo), 0, 1)] exactly, for an indicator dimension: K the count of ones among the
    n = seeds_in_set x |starts| units of a seed set, K = sum over starts t of Binomial(seeds_in_set, p_t) independent
    (choice 3: units of different starts and seeds draw independently given H), its law convolved start by start."""
    if dim.name not in INDICATOR_DIMS or dim.a != 0.0 or dim.r != 1.0:
        raise H3ReportRefused(f"{dim.name}: not an indicator dimension (values 0 or 1 by definition)")
    p = np.asarray(p_by_start, float).ravel()
    if p.size == 0 or not np.isfinite(p).all() or (p < -1e-12).any() or (p > 1 + 1e-12).any():
        raise H3ReportRefused(f"{dim.name}: exact probabilities must lie in [0, 1]")
    p = np.clip(p, 0.0, 1.0)
    m = _require_exact_int(int(seeds_in_set), "seeds_in_set")
    if m < 1:
        raise H3ReportRefused("a seed set holds at least one seed")
    k = np.arange(m + 1)
    pmf = np.array([1.0])
    for pt in p:
        pmf = np.convolve(pmf, _binom.pmf(k, m, pt))
    n = m * p.size
    g = np.clip((np.arange(n + 1) / n - dim.lo) / (dim.hi - dim.lo), 0.0, 1.0)
    tot = float(pmf.sum())
    if abs(tot - 1.0) > 1e-9:
        raise H3ReportRefused(f"{dim.name}: the count's law sums to {tot}, not 1")
    return float((pmf * g).sum())


def clipped_dimension_expectation(dim: ST.Dimension, mean_by_start: Sequence[float], seeds_in_set: int) -> float:
    """E[clip((Phi - lo) / (hi - lo), 0, 1)] exactly, Phi the dimension's mean over a seed set's units: linear where the
    dimension's arithmetic range [a, a + r] lies inside its caps [lo, hi] (the clip never binds on any seed set); the
    exact Poisson-binomial law for an indicator (`clipped_indicator_expectation`); refused otherwise (no
    approximation: the lead's ruling on B-2)."""
    if dim.source is None or dim.a is None or dim.r is None:
        raise H3ReportRefused(f"{dim.name}: no a priori range, so no exact centre")
    mu = np.asarray(mean_by_start, float).ravel()
    if dim.lo <= float(dim.a) and float(dim.a) + float(dim.r) <= dim.hi:
        return float((mu.mean() - dim.lo) / (dim.hi - dim.lo))
    if dim.name in INDICATOR_DIMS:
        return clipped_indicator_expectation(dim, mu, seeds_in_set)
    raise H3ReportRefused(f"REFUSED (B-2): {dim.name}'s cap can bind and its law is not an indicator's: no exact centre "
                          "of the clipped composite (A2 would need re-declaring)")


def exact_composite_centre(dims: Sequence[ST.Dimension], exact_f: Mapping[str, Sequence[float]],
                           exact_b: Mapping[str, Sequence[float]], seeds_in_set: int) -> float:
    """theta = E[C(f; S) - C(beta; S) | H] exactly, S a seed set of `seeds_in_set` seeds over every start: the sum over
    dimensions of w_d (E[clipped scaled mean under f] - E[... under beta]), each from the arm's exact per-start
    expectations (`exact_f[d][t]`; an indicator's are its probabilities). Linearity of expectation needs no
    independence between the arms (they share one coin field)."""
    tot = 0.0
    for d in dims:
        tot += d.weight * (clipped_dimension_expectation(d, exact_f[d.name], seeds_in_set)
                           - clipped_dimension_expectation(d, exact_b[d.name], seeds_in_set))
    return float(tot)


# ------------------------------------------------------------------------------------------------ the size counts


def composite_per_seed(X: Mapping[str, np.ndarray], dims: Sequence[ST.Dimension]) -> np.ndarray:
    """C(x; {s}) for each seed column s: the clipped, weighted composite of one seed's mean over the starts (m = 1)."""
    n_seeds = next(iter(X.values())).shape[1]
    out = np.zeros(n_seeds, float)
    for d in dims:
        v = d.values(X[d.name]).mean(axis=0)
        out += d.weight * np.clip((v - d.lo) / (d.hi - d.lo), 0.0, 1.0)
    return out


def composite_per_seed_diffs(Xf: Mapping[str, np.ndarray], Xb: Mapping[str, np.ndarray],
                             dims: Sequence[ST.Dimension]) -> np.ndarray:
    """One composite difference Delta_s in [-1, 1] per seed column (m = 1: each seed's mean over starts, clipped and
    weighted)."""
    return composite_per_seed(Xf, dims) - composite_per_seed(Xb, dims)


def composite_dims(comp: str) -> tuple[ST.Dimension, ...]:
    """The placeholder composites (section 8): `P_B` alone at `BUDGET` (the fallback), and the clipped toy composite."""
    if comp == "p_b":
        return (ST.fallback(),)
    if comp == "toy_composite":
        return tuple(H.TOY_COMPOSITE)
    raise H3ReportRefused(f"no declared composite {comp!r}")


def size_counts(Xf: Mapping[str, np.ndarray], Xb: Mapping[str, np.ndarray], starts: Sequence[int], *, j_prime: int,
                centres: Mapping[str, Mapping[str, float]] | None = None,
                levels: Sequence[float] = LEVELS) -> tuple[dict[tuple[str, str, float], tuple[int, int]], dict]:
    """The size counts of one history: on floor(columns / J') disjoint sets of J' paired seed columns, for both
    composites, all three bounds and every level, a rejection is **the bound's lower limit above the null's centre**
    -- `lower > theta`, the one-sided size event P(LB > E[Delta]) <= alpha (B-2's remedy: every bound is a lower
    confidence limit for the mean whatever it is, so this is centring without any clip). `centres[comp]` gives
    `set` (theta of the set-level estimate the 2.2 (a) bound reads) and `seed` (theta of a per-seed replicate, the
    2.2 (b) bounds' term); None means the exact zero of a symmetric null (A1).

    Returns the counts {(composite, bound, level): (rejections, n_sets)} and the counted pools, centred:
    {composite: {"seed": the per-seed replicates less theta_seed over every column, "set": each set's 2.2 (a)
    estimate less theta_set, "at_cap": the share of sets whose set-level composite has a dimension at a cap}} -- the
    pools the premises read (B-2 (d))."""
    n_cols = Xf["P_B"].shape[1]
    j = _require_exact_int(int(j_prime), "J'")
    if j < 2 or n_cols < j:
        raise H3ReportRefused(f"no seed sets of size {j} from {n_cols} seed columns")
    sets = [np.arange(i * j, (i + 1) * j) for i in range(n_cols // j)]
    counts: dict[tuple[str, str, float], int] = {(c, b, float(lv)): 0 for c in COMPOSITES for b in BOUNDS
                                                   for lv in levels}
    pools: dict[str, dict] = {}
    for comp in COMPOSITES:
        dims = composite_dims(comp)
        th_set = 0.0 if centres is None else float(centres[comp]["set"])
        th_rep = 0.0 if centres is None else float(centres[comp]["seed"])
        smap = {d.name: tuple(starts) for d in dims}
        d_all = composite_per_seed_diffs(Xf, Xb, dims)
        set_est, at_cap = [], 0
        for cols in sets:
            xf = {d.name: Xf[d.name][:, cols] for d in dims}
            xb = {d.name: Xb[d.name][:, cols] for d in dims}
            d_s = d_all[cols]
            cap = False                                     # N-11, beside: a set where a clip binds
            for d in dims:
                for x in (xf, xb):
                    phi = float(d.values(x[d.name]).mean())
                    cap |= phi < d.lo or phi > d.hi
            at_cap += int(cap)
            est = None
            for lv in levels:
                lv = float(lv)
                bnd = ST.mcdiarmid(dims, xf, xb, smap, lv)
                est = bnd.estimate
                if bnd.lower > th_set:
                    counts[(comp, "bound_22a", lv)] += 1
                if ST.eb_lower(d_s, lv) > th_rep:
                    counts[(comp, "eb", lv)] += 1
                if ST.betting_lower(d_s, lv) > th_rep:
                    counts[(comp, "betting", lv)] += 1
            set_est.append(est)
        pools[comp] = {"seed": d_all - th_rep, "set": np.asarray(set_est, float) - th_set,
                       "at_cap": at_cap / len(sets)}
    return {k: (v, len(sets)) for k, v in counts.items()}, pools


def counts_to_rows(part: str, null_class: str, history: int,
                   counts: Mapping[tuple[str, str, float], tuple[int, int]]) -> list[SizeCount]:
    """One history's counts as `SizeCount` rows (sorted, so the file's order is fixed)."""
    return [SizeCount(part, null_class, comp, b, float(lv), int(k), int(n), history=int(history))
            for (comp, b, lv), (k, n) in sorted(counts.items())]


# ------------------------------------------------------------------------------------------------ A4: the plants


def a4_cells() -> list[tuple[str, str, str, str, float]]:
    """Section 8's 426 pass rates as (plant, param, composite, bound, level): P1 1 x 2 x 5 x 3 = 30; P2 3 x 2 x 3 x 3 =
    54; P3 4 x 2 x 3 x 3 = 72; P4 3 x 5 x 2 x 3 x 3 = 270."""
    out = []
    for d in H.SIZE_GRID:
        for b in ("bound_22a", "eb"):
            for lv in LEVELS:
                out.append(("P1", f"delta={d:g}", "p_b", b, lv))
    for name in H.P2_LEVERS:
        for c in COMPOSITES:
            for b in BOUNDS:
                for lv in LEVELS:
                    out.append(("P2", name, c, b, lv))
    for e in H.P3_EPS:
        for c in COMPOSITES:
            for b in BOUNDS:
                for lv in LEVELS:
                    out.append(("P3", f"eps={e:g}", c, b, lv))
    for a in H.P4_A:
        for d in H.SIZE_GRID:
            for c in COMPOSITES:
                for b in BOUNDS:
                    for lv in LEVELS:
                        out.append(("P4", f"a={a:g},d={d:g}", c, b, lv))
    want = (len(H.SIZE_GRID) * 2 * len(LEVELS) + len(H.P2_LEVERS) * 2 * 3 * len(LEVELS)
            + len(H.P3_EPS) * 2 * 3 * len(LEVELS) + len(H.P4_A) * len(H.SIZE_GRID) * 2 * 3 * len(LEVELS))
    assert len(out) == len(set(out)) == want == 426
    return out


def a4_mdl_lines() -> list[tuple[str, str, str, str, float]]:
    """Section 8's 60 MDLs, one a line over the size grid: P1's 1 x 2 x 3 = 6 (param ''), P4's 3 x 2 x 3 x 3 = 54
    (param 'a=...')."""
    out = [("P1", "", "p_b", b, lv) for b in ("bound_22a", "eb") for lv in LEVELS]
    out += [("P4", f"a={a:g}", c, b, lv) for a in H.P4_A for c in COMPOSITES for b in BOUNDS for lv in LEVELS]
    assert len(out) == len(set(out)) == 6 + 54 == 60
    return out


#: beside A4's rates and MDLs (E-295 (a); the red team's c2 m-9)
A4_J_NOTE = (f"A4's pass rates and MDLs hold at J = J_PRIME = {H.J_PRIME} seeds a draw only (E-295 (a)); "
             "H3-D's J is H3-D's")
A4_NULL_NOTE = ("P1's and P4's null: the disjoint same-design null of A4's base arm (2.3 (b), DISJOINT); in H3-A, "
                "with no time condition, P4 is P1 at the size d mean(1 + a rho_t)")

#: P1's bounds by name in `three_way_stats.LINEAR_PLANT_BOUNDS` (2.2 (a) on the unclipped `P_B` is Hoeffding's)
P1_LINEAR_NAME = {"bound_22a": "hoeffding", "eb": "eb"}


def summarise_a4(rows: Sequence[Mapping[str, Any]], p1_lowers: Sequence[Mapping[str, Any]],
                 histories: Sequence[int] | None = None) -> tuple[list[dict], list[dict]]:
    """A4 pooled over its histories (Appendix A's R = 10 by default): the 426 pass rates (each cell's passes over its
    draws, summed over histories; every cell under every history once, refused otherwise) and the 60 MDLs at pi* =
    `family_stats.MDL_POWER` over `SIZE_GRID` -- P1's by `three_way_stats.planted_mdl` on the pooled per-draw lower
    limits at no plant (the linear form, its bounds `LINEAR_PLANT_BOUNDS`), its rates held equal to the linear form's;
    P4's by `family_stats.conjoint_mdl_grid` (one line, one leg: its power at each size is the line's pooled pass rate,
    so the pooled counts give it exactly)."""
    hs = tuple(range(DECLARED_R["A4"])) if histories is None else tuple(int(h) for h in histories)
    cells = a4_cells()
    acc: dict[tuple, list[int]] = {c: [0, 0] for c in cells}
    beside: dict[tuple, list[float]] = {c: [] for c in cells}
    seen: set[tuple] = set()
    for r in rows:
        c = (str(r["plant"]), str(r["param"]), str(r["composite"]), str(r["bound"]), float(r["level"]))
        h = _require_exact_int(int(r["history"]), "history")
        if c not in acc:
            raise H3ReportRefused(f"undeclared A4 cell {c}")
        if (c, h) in seen:
            raise H3ReportRefused(f"duplicate A4 cell {c} at history {h}")
        if h not in hs:
            raise H3ReportRefused(f"A4 history {h} is not one of the declared {hs}")
        seen.add((c, h))
        k, n = int(r["passes"]), int(r["draws"])
        if n < 1 or not 0 <= k <= n:
            raise H3ReportRefused(f"invalid A4 count {k}/{n} at {c}, history {h}")
        acc[c][0] += k
        acc[c][1] += n
        beside[c].append(float(r.get("true_delta", float("nan"))))
    if len(seen) != len(cells) * len(hs):
        raise H3ReportRefused(f"A4 needs every cell under every history ({len(cells) * len(hs)} rows), got {len(seen)}")
    rates = [{"plant": c[0], "param": c[1], "composite": c[2], "bound": c[3], "level": c[4], "passes": k, "draws": n,
              "pass_rate": k / n, "true_delta_mean_beside": float(np.nanmean(beside[c])) if np.isfinite(beside[c]).any()
              else float("nan"), "j_beside": A4_J_NOTE,
              "reading_beside": A4_NULL_NOTE if c[0] in ("P1", "P4") else ""} for c, (k, n) in acc.items()]
    rate_of = {c: k / n for c, (k, n) in acc.items()}

    # P1: the pooled lowers at no plant, by line
    low: dict[tuple[str, float], list[float]] = {}
    seen_d: set[tuple] = set()
    for r in p1_lowers:
        b, lv, h, dr = str(r["bound"]), float(r["level"]), int(r["history"]), int(r["draw"])
        if (b, lv, h, dr) in seen_d:
            raise H3ReportRefused(f"duplicate P1 draw {(b, lv, h, dr)}")
        if h not in hs:
            raise H3ReportRefused(f"P1 history {h} is not one of the declared {hs}")
        seen_d.add((b, lv, h, dr))
        low.setdefault((b, lv), []).append(float(r["lower0"]))
    mdls = []
    for line in a4_mdl_lines():
        plant, param, comp, b, lv = line
        if plant == "P1":
            l0 = np.asarray(low.get((b, lv), []), float)
            n_draws = acc[("P1", f"delta={H.SIZE_GRID[0]:g}", "p_b", b, lv)][1]
            if l0.size != n_draws:
                raise H3ReportRefused(f"P1 {b} at {lv}: {l0.size} pooled lowers for {n_draws} draws")
            res = ST.planted_mdl(l0, P1_LINEAR_NAME[b], grid=H.SIZE_GRID)
            for i, d in enumerate(H.SIZE_GRID):
                lin = float(np.mean(l0 + float(d) > 0))
                if not math.isclose(lin, rate_of[("P1", f"delta={d:g}", "p_b", b, lv)], abs_tol=1e-12):
                    raise H3ReportRefused(f"P1 {b} at {lv}, delta {d}: the pooled rate is not the linear form's")
            mdls.append({"plant": plant, "param": param, "composite": comp, "bound": b, "level": lv,
                         "mdl_grid": float(res.mdl), "mdl_continuous_beside": float(res.mdl_continuous),
                         "form": "planted_mdl (linear)", "j_beside": A4_J_NOTE, "reading_beside": A4_NULL_NOTE})
        else:
            def passes_at(d, _a=param, _c=comp, _b=b, _l=lv):
                k, n = acc[("P4", f"{_a},d={d:g}", _c, _b, _l)]
                return np.array([True] * k + [False] * (n - k))
            res = FS.conjoint_mdl_grid(passes_at, H.SIZE_GRID)
            mdls.append({"plant": plant, "param": param, "composite": comp, "bound": b, "level": lv,
                         "mdl_grid": float(res.mdl), "mdl_continuous_beside": float("nan"),
                         "form": "conjoint_mdl_grid (planted through the bound)", "j_beside": A4_J_NOTE,
                         "reading_beside": A4_NULL_NOTE})
    assert len(rates) == 426 and len(mdls) == 60
    return rates, mdls


# ------------------------------------------------------------------------------------------------ A3: the history null


#: the history null's pair label (2.7: "stylised" where the pair is not a finalist)
A3_PAIR_LABEL = "stylised"


def summarise_a3(rows: Sequence[Mapping[str, Any]], histories: Sequence[int] | None = None,
                 shortcut: Sequence[int] | None = None) -> list[dict]:
    """A3's 6 rates (section 8: 1 stylised pair x 2 composites x 3 levels, each over A3's histories, the whole rule at
    its bound by the composite's form -- 2.2 (a) for both placeholder composites): FPR_hist the mean over histories of
    each history's pass probability at the test's J (2.5's formula times the time conditions' indicator; the note's
    2.7), with its pair's label; beside it, the shortcut's error on `SHORTCUT_HISTORIES` (the formula against the full
    run at the test's J) and `three_way_stats.fpr_hist` of the full run's passes there."""
    hs = tuple(range(H.A3_HISTORIES)) if histories is None else tuple(int(h) for h in histories)
    sc = tuple(H.SHORTCUT_HISTORIES) if shortcut is None else tuple(int(h) for h in shortcut)
    by: dict[tuple[str, float], dict[int, Mapping]] = {}
    for r in rows:
        k = (str(r["composite"]), float(r["level"]))
        h = int(r["history"])
        if k[0] not in COMPOSITES or k[1] not in LEVELS:
            raise H3ReportRefused(f"undeclared A3 cell {k}")
        if h not in hs:
            raise H3ReportRefused(f"A3 history {h} is not declared")
        if h in by.setdefault(k, {}):
            raise H3ReportRefused(f"duplicate A3 row {k} at history {h}")
        by[k][h] = r
    out = []
    for comp in COMPOSITES:
        for lv in LEVELS:
            got = by.get((comp, lv), {})
            if set(got) != set(hs):
                raise H3ReportRefused(f"A3 {comp} at {lv}: {len(got)} histories, not the declared {len(hs)}")
            p = np.array([float(got[h]["pass_prob"]) for h in hs])
            errs, full_passes = [], []
            for h in sc:
                fk, fn = int(got[h]["full_passes"]), int(got[h]["full_draws"])
                if fn < 1:
                    raise H3ReportRefused(f"A3 shortcut history {h} has no full run")
                errs.append(float(got[h]["pass_prob"]) - fk / fn)
                full_passes += [True] * fk + [False] * (fn - fk)
            full = ST.fpr_hist(full_passes, A3_PAIR_LABEL)
            out.append({"pair": A3_PAIR_LABEL, "composite": comp, "bound": "bound_22a", "level": lv,
                        "fpr_hist": float(p.mean()), "histories": len(hs),
                        "shortcut_error_mean_beside": float(np.mean(errs)),
                        "shortcut_error_max_abs_beside": float(np.max(np.abs(errs))),
                        "full_run_fpr_beside": full["rate"], "full_run_n_beside": full["n"],
                        "full_run_cp_lo_beside": full["cp_lo"], "full_run_cp_hi_beside": full["cp_hi"]})
    assert len(out) == len(COMPOSITES) * len(LEVELS) == 6
    return out


# ------------------------------------------------------------------------------------------------ the inputs (m-5)


def _lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def manifest_of(csv_path: Path) -> dict:
    """The sidecar manifest's JSON (read only)."""
    p = Path(str(csv_path) + ".manifest.json")
    if not p.is_file():
        raise H3ReportRefused(f"missing manifest for {csv_path}")
    return json.loads(p.read_text(encoding="utf-8"))


def verify_inputs(paths: Sequence[Path], *, verify: Callable[[Path], tuple[bool, str]], root: Path,
                  read_manifest: Callable[[Path], Mapping] = manifest_of) -> str:
    """m-5: every input's manifest verifies (`verify`, the vendored sha256 check), every input is clean (`git_dirty`
    false), every input names one and the same commit, and that commit's build files (`H3_BUILD_FILES`) and report
    files (`REPORT_FILES`) equal this tree's HEAD. Returns the commit."""
    commits = set()
    for p in paths:
        if not Path(p).is_file():
            raise H3ReportRefused(f"missing input {p}")
        ok, msg = verify(Path(p))
        if not ok:
            raise H3ReportRefused(f"input {p} does not verify: {msg}")
        m = read_manifest(Path(p))
        if m.get("git_dirty") is not False:
            raise H3ReportRefused(f"input {p} was not written from a clean tree (git_dirty={m.get('git_dirty')!r})")
        commits.add(str(m.get("git_commit", "")))
    if len(commits) != 1:
        raise H3ReportRefused(f"the inputs come from {len(commits)} commits, not one: {sorted(commits)}")
    c = commits.pop()
    if not re.fullmatch(r"[0-9a-f]{7,40}", c):
        raise H3ReportRefused(f"the inputs' commit {c!r} is not a commit")
    d = subprocess.run(["git", "-C", str(root), "diff", "--quiet", c, "HEAD", "--", *H3_BUILD_FILES, *REPORT_FILES])
    if d.returncode != 0:
        raise H3ReportRefused(f"the inputs' commit {c[:7]}'s build or report files differ from this tree's HEAD")
    return c


def _flat(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def assert_h3_preconditions(root: Path, *, check_build_commit: bool = False) -> dict[str, str]:
    """E-279 & section 16 pre-run gate: H3 pinned and unedited; template v3 hash row pinned with R-10 clauses;
    optionally verifies that `4c07026` is an ancestor of HEAD and all 9 H3 build files are unchanged since `4c07026`."""
    root = Path(root)
    h3 = root / H3_DECL_PATH
    if not h3.is_file():
        raise H3ReportRefused(f"missing H3 declaration: {H3_DECL_PATH}")
    h3_sha = _lf_sha256(h3)
    if h3_sha != H3_PIN_SHA256:
        raise H3ReportRefused(f"H3 declaration LF sha256 {h3_sha} != pinned {H3_PIN_SHA256}")

    dec = root / "DECISIONS.md"
    if not dec.is_file():
        raise H3ReportRefused("missing DECISIONS.md")
    dec_text = dec.read_text(encoding="utf-8")
    h3_pins = H3_PIN_RE.findall(dec_text)
    if not any(sha == H3_PIN_SHA256 for _p, sha in h3_pins):
        raise H3ReportRefused("H3 pin grammar entry with pinned sha256 not recorded in DECISIONS.md")

    pins = TEMPLATE_PIN_RE.findall(dec_text)
    if not pins:
        raise H3ReportRefused("template v3 hash row is not pinned in DECISIONS.md yet (E-279)")
    rel, want_tpl_sha = pins[-1]
    tpl = root / rel
    if not tpl.is_file():
        raise H3ReportRefused(f"missing pinned template file: {rel}")
    got_tpl_sha = _lf_sha256(tpl)
    if got_tpl_sha != want_tpl_sha:
        raise H3ReportRefused(f"{rel} LF sha256 {got_tpl_sha} != pinned {want_tpl_sha}")

    body = tpl.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")
    s5_mark = "\n## 5. The zero-edge convention"
    s6_mark = "\n## 6. "
    if s5_mark not in body:
        raise H3ReportRefused(f"{rel} missing section 5 heading")
    s5_start = body.index(s5_mark)
    s6_start = body.find(s6_mark, s5_start)
    if s6_start < 0:
        raise H3ReportRefused(f"{rel} missing section 6 heading after section 5")
    sec5 = _flat(body[s5_start:s6_start])
    if "**R-10: the redraw for a trade that ends at a time limit**" not in sec5:
        raise H3ReportRefused(f"{rel} section 5 missing R-10 heading")
    missing = [c for c in R10_CLAUSES if _flat(c) not in sec5]
    if missing:
        raise H3ReportRefused(f"pinned R-10 disagrees with H3 walk clauses: {missing}")

    if check_build_commit:
        anc = subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", H3_BUILD_COMMIT, "HEAD"],
                             capture_output=True)
        if anc.returncode != 0:
            raise H3ReportRefused(f"H3 build commit {H3_BUILD_COMMIT} is not an ancestor of HEAD")
        diff_head = subprocess.run(["git", "-C", str(root), "diff", "--name-only", H3_BUILD_COMMIT, "HEAD", "--",
                                    *H3_BUILD_FILES], capture_output=True, text=True, check=True)
        diff_wt = subprocess.run(["git", "-C", str(root), "diff", "--name-only", H3_BUILD_COMMIT, "--",
                                  *H3_BUILD_FILES], capture_output=True, text=True, check=True)
        changed = sorted({x for x in diff_head.stdout.splitlines() + diff_wt.stdout.splitlines() if x.strip()})
        if changed:
            raise H3ReportRefused(f"H3 build files moved since {H3_BUILD_COMMIT}: {changed}")

    return {"h3_sha256": h3_sha, "template_path": rel, "template_sha256": got_tpl_sha}
