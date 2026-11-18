"""RD-05's oracles (`prereg/RD-05_firm_modes.md` 9.6; E-200 N-1, N-2, R-2): exact interval tests under a family-wise
correction, and the exact accounting identities. An output outside an oracle is an engine error, never a finding.

* **The level.** Family-wise 0.01, Bonferroni over N (step 0's count, `modes_rules.oracle_count`): a one-sided check at
  `0.01 / N`; a two-sided one puts `0.01 / (2 N)` in each tail.
* **The fairness check** (one per coin run, two-sided): `S`, the sum over the run's trades of (1{target} - p) times
  the trade's span, is a martingale with increments bounded by `b` and predictable variance `V`; a breach when `|S|`
  exceeds Freedman's bound at the level -- `2 exp(-a^2 / (2 (V + b a / 3))) = 0.01 / N` solved for `a`, at the
  realised `V` (N-1: the plug-in form, not peeled). `RI`'s losing-trade peaks enter the same sums by their
  probability-integral increment (N-2).
* **The pass ceiling** (one-sided): a breach when the pass probability's Clopper-Pearson lower limit exceeds
  `D / (D + T)`; dropped at the close-only corners; replaced at a boundary cell by the boundary quantity.
* **The supremum** (one-sided, `TS-S`): against `results_combine_supremum.csv`, read (the largest `sup_p_pass` of its
  no-DLL rows, the finest grid's).
* **The reference** (13.1 (b), two-sided): stage one's 16/49, parsed from the vendored README.
* **The exact identities** (to 1e-9 on every account): final balance + gross payouts + forfeitures + costs = the sum
  of the trades' gross P&L; on the funded coin the final balance at least the starting floor; every request within
  its bounds; every forfeiture at a verified ceiling.
"""
from __future__ import annotations

import math
import re
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

from extended import modes_terms as M

ROOT = Path(__file__).resolve().parent.parent
SUPREMUM_CSV = ROOT / "vendor" / "stage2" / "vendor" / "propsim" / "optimality" / "results_combine_supremum.csv"
PROPSIM_README = ROOT / "vendor" / "stage2" / "vendor" / "propsim" / "README.md"
HALF = 0.5


class OracleBreach(RuntimeError):
    """9.6: an engine error -- the step stops."""


def level(N: int) -> float:
    """The per-check level, `0.01 / N` (9.6)."""
    if int(N) < 1:
        raise ValueError("N is at least 1")
    return float(M.declared("oracle.level")) / int(N)


def freedman_bound(V: float, b: float, alpha: float) -> float:
    """`a` with `2 exp(-a^2 / (2 (V + b a / 3))) = alpha`: `a = L b / 3 + sqrt((L b / 3)^2 + 2 L V)`, `L = ln(2 / alpha)`."""
    L = math.log(2.0 / float(alpha))
    x = L * float(b) / 3.0
    return x + math.sqrt(x * x + 2.0 * L * float(V))


def fairness_breach(fair: dict[str, float], alpha: float) -> bool:
    if fair["trades"] == 0:
        return False
    return abs(float(fair["S"])) > freedman_bound(fair["V"], fair["b"], alpha)


def cp_lower(x: int, n: int, alpha: float) -> float:
    """The exact (Clopper-Pearson) one-sided lower limit at level `alpha`."""
    x, n = int(x), int(n)
    return 0.0 if x == 0 else float(stats.beta.ppf(float(alpha), x, n - x + 1))


def cp_upper(x: int, n: int, alpha: float) -> float:
    x, n = int(x), int(n)
    return 1.0 if x == n else float(stats.beta.ppf(1.0 - float(alpha), x + 1, n - x))


def pass_ceiling(t: M.EvalTerms) -> float:
    return float(t.mll) / (float(t.mll) + float(t.target))


def pass_ceiling_breach(x: int, n: int, t: M.EvalTerms, alpha: float) -> bool:
    return cp_lower(x, n, alpha) > pass_ceiling(t)


@lru_cache(maxsize=1)
def supremum() -> float:
    """The supremum over fair strategies of the Combine's pass probability, read from the vendored file: its no-DLL
    rows' largest `sup_p_pass` (the finest grid)."""
    import pandas as pd

    df = pd.read_csv(SUPREMUM_CSV)
    rows = df[df["dll"].astype(float) == 0.0]
    if rows.empty:
        raise ValueError("no no-DLL row in results_combine_supremum.csv")
    return float(rows["sup_p_pass"].astype(float).max())


def supremum_breach(x: int, n: int, alpha: float) -> bool:
    return cp_lower(x, n, alpha) > supremum()


@lru_cache(maxsize=1)
def stage_one_reference() -> Fraction:
    """Stage one's reference profile's exact pass probability, parsed from the vendored README (`P(pass) = a/b`)."""
    text = PROPSIM_README.read_text(encoding="utf-8")
    m = re.search(r"P\(pass\) = (\d+)/(\d+)", text)
    if m is None:
        raise ValueError("stage one's README no longer states P(pass) = a/b")
    return Fraction(int(m.group(1)), int(m.group(2)))


def reference_breach(x: int, n: int, alpha: float) -> bool:
    """13.1 (b): two-sided at the corrected width, `alpha / 2` in each tail."""
    ref = float(stage_one_reference())
    return not (cp_lower(x, n, alpha / 2.0) <= ref <= cp_upper(x, n, alpha / 2.0))


def boundary_quantity(out: dict[str, Any], t: M.EvalTerms) -> np.ndarray:
    """9.6: `T 1{pass} - D 1{fail} + B 1{neither}` per account."""
    T, D = float(t.target), float(t.mll)
    neither = ~out["passed"] & ~out["failed"]
    return np.where(out["passed"], T, 0.0) - np.where(out["failed"], D, 0.0) + np.where(neither, out["B"], 0.0)


def boundary_problems(out: dict[str, Any], t: M.EvalTerms) -> list[str]:
    """9.6 at a boundary cell: every pass at exactly `T`, every failure at exactly `-D` (exact identities); the
    boundary quantity is then each account's summed trade P&L."""
    out_p = []
    T, D = float(t.target), float(t.mll)
    if np.any(np.abs(out["B"][out["passed"]] - T) > 1e-9):
        out_p.append("a pass not at exactly T")
    if np.any(np.abs(out["B"][out["failed"]] + D) > 1e-9):
        out_p.append("a failure not at exactly -D")
    if np.any(np.abs(boundary_quantity(out, t) - out["gross_sum"]) > 1e-9 * max(1.0, T)):
        out_p.append("the boundary quantity differs from the summed trade P&L")
    return out_p


def accounting_problems(out: dict[str, Any], kind: str, floor_start: float | None = None) -> list[str]:
    """9.6's exact identities on every account."""
    gross = np.asarray(out["gross_sum"], float)
    B = np.asarray(out["B"], float)
    paid = np.asarray(out.get("gross_paid", np.zeros_like(B)), float)
    forfeit = np.asarray(out.get("forfeit", np.zeros_like(B)), float)
    costs = np.asarray(out["costs"], float)
    scale = max(1.0, float(np.max(np.abs(gross))) if gross.size else 1.0, float(np.max(np.abs(B))) if B.size else 1.0)
    probs = []
    if np.any(np.abs(B + paid + forfeit + costs - gross) > 1e-9 * scale):          # relative to the run's scale
        probs.append("balance + payouts + forfeitures + costs != the trades' gross P&L")
    if kind == M.FUNDED and floor_start is not None and np.any(B < float(floor_start) - 1e-9):
        probs.append("a funded balance below its starting floor")
    if kind == M.FUNDED and int(np.sum(out.get("request_check", 0))) != 0:
        probs.append("a request outside its plan's bounds")
    return probs


def ceiling_problems(out: dict[str, Any], f: M.FundedTerms) -> list[str]:
    """Every forfeiture and every "moved to Live" ending at a verified ceiling (A-11)."""
    if f.ceiling is None and (np.any(out["forfeit"] > 0) or np.any(out["moved_live"])):
        return ["a forfeiture or a Live move at a plan with no verified ceiling"]
    return []


def oracle_rows(kind: str, out: dict[str, Any], t: Any, *, N: int, mode: str, boundary: bool, close_only: bool
                ) -> list[dict[str, Any]]:
    """Every check of one coin run, each a row (`check`, `value`, `bound`, `breach`); raises `OracleBreach` on any."""
    a = level(N)
    rows = []
    fair = out["fair"]
    fb = freedman_bound(fair["V"], fair["b"], a) if fair["trades"] else 0.0
    rows.append({"check": "fairness", "value": fair["S"], "bound": fb, "breach": fairness_breach(fair, a)})
    if kind == M.EVAL:
        n, x = len(out["passed"]), int(np.sum(out["passed"]))
        if boundary:
            bp = boundary_problems(out, t)
            rows.append({"check": "boundary_identity", "value": len(bp), "bound": 0, "breach": bool(bp)})
        elif not close_only:
            rows.append({"check": "pass_ceiling", "value": cp_lower(x, n, a), "bound": pass_ceiling(t),
                         "breach": pass_ceiling_breach(x, n, t, a)})
        if mode == "TS":
            rows.append({"check": "supremum", "value": cp_lower(x, n, a), "bound": supremum(),
                         "breach": supremum_breach(x, n, a)})
        ap = accounting_problems(out, kind)
    else:
        ap = accounting_problems(out, kind, t.floor_start) + ceiling_problems(out, t)
    rows.append({"check": "accounting", "value": len(ap), "bound": 0, "breach": bool(ap), "note": "; ".join(ap)})
    bad = [r for r in rows if r["breach"]]
    if bad:
        raise OracleBreach(f"9.6: {[r['check'] for r in bad]} breached -- an engine error, the step stops")
    return rows


__all__ = ["OracleBreach", "level", "freedman_bound", "fairness_breach", "cp_lower", "cp_upper", "pass_ceiling",
           "pass_ceiling_breach", "supremum", "supremum_breach", "stage_one_reference", "reference_breach",
           "boundary_quantity", "boundary_problems", "accounting_problems", "ceiling_problems", "oracle_rows", "HALF"]
