"""H3-A's report and laxity-stop code (`prereg/H3_three_way.md` sections 8, 11, 14, 17; E-279).

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
  for `rejections >= 1` (and `0.0` for `rejections == 0`). It is a **laxity** when `cp_one_sided_lo > level`.
- **`three_way_stats.size_label`** (E-052's two-sided 95 % Clopper-Pearson interval) is reported beside every pooled
  and per-history count, **never deciding**.
- **The 1080 per-history counts** (720 for A1, 360 for A2) are reported beside, **never stopping anything**.
- **Premise kills** (section 11): `check_null_pool` runs `three_way_stats.null_pool_guards` (refusing all-zero pools
  and disjoint pools outside variance tolerance) AND centring (`|mean| <= CENTRING_Z * se`, two-sided).
- **Pre-run gate** (E-279, section 16): refuses unless `prereg/H3_three_way.md` matches its pinned LF sha256 under the
  pin grammar in `DECISIONS.md`, template v3's hash row (`prereg/TEMPLATE_design_search.md` sha256) is pinned in
  `DECISIONS.md` and carries R-10's declared clauses, and (when `check_build_commit=True`) `4c07026`'s build files
  are unchanged.
"""
from __future__ import annotations

import hashlib
import math
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
from scipy.stats import beta as _beta

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
    if not isinstance(v, int) or isinstance(v, bool):
        raise H3ReportRefused(f"{label} must be an exact int, got {v!r}")
    return v


def _require_prob(v: Any, label: str) -> float:
    if isinstance(v, bool) or not isinstance(v, (int, float)):
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


def evaluate_laxity_stop(pooled: Iterable[SizeCount], per_history: Iterable[SizeCount] = ()) -> dict:
    """Apply H3-A's declared laxity stop (section 11, E-279) to the 54 pooled counts ONLY.

    Refuses if `pooled` does not contain the exact 54 declared keys (36 A1 + 18 A2), once each.
    Per-history counts (1080 = 720 A1 + 360 A2 when supplied) are validated for key/uniqueness, reported beside, and
    NEVER affect `stop_h3d`.
    """
    pooled_list = list(pooled)
    per_hist_list = list(per_history)

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

    seen_hist: set[tuple[str, str, str, str, float, int]] = set()
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
        scored_hist.append(row)

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
        "per_history_count": len(scored_hist),
        "per_history_beside": scored_hist,
    }


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


def _lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


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
