"""The success criteria's computed levels (R1, D-457; `docs/SUCCESS_CRITERIA.md`).

* **The required-bankroll p95 path** (the deployment protocol's §4.6 and §5; D-400's P2): the 95th percentile, across a
  confirmation run's lower-bound-arm paths (run "gate placement off", 0 % denial), of each path's deepest loss from the
  start. The live drawdown from the start is held inside it; the point arm's p95 is its FLAG level (D-400). The
  required bankroll at p95 is the same percentile plus one subscription (`portfolio.DEFAULT_MARGIN`), as
  `portfolio.required_bankroll` builds p50 / p90 / p99 / worst.
* **The FLAG levels** (§5): for each measure, P-06's lower-bound arm's 90th-percentile path in the measure's bad
  direction (the 10th where higher is better); a candidate's gate-row median path beyond it is flagged. A FLAG never
  changes the gate's verdict.

Percentiles use `portfolio._pct`, the engine's own (D-319, D-334), so a level here is the number the engine would give.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from propedge.campaign.portfolio import DEFAULT_MARGIN, _pct

GATE_RUN = "gate placement off"


def arm(paths: pd.DataFrame, shift: str = "lower_bound", enforcement_p: float = 0.0, run: str = GATE_RUN) -> pd.DataFrame:
    """One arm's rows of a per-path file (`results/<verdict>_paths.csv` or the path-detail file); refuses an empty arm."""
    m = (paths["run"].astype(str) == run) & (paths["shift"].astype(str) == shift) & \
        np.isclose(pd.to_numeric(paths["enforcement_p"], errors="coerce"), float(enforcement_p))
    out = paths[m]
    if out.empty:
        raise ValueError(f"no paths for run {run!r}, shift {shift!r}, denial {enforcement_p}")
    return out


def paths_quantile(paths: pd.DataFrame, column: str, q: float, *, shift: str = "lower_bound",
                   enforcement_p: float = 0.0, run: str = GATE_RUN, offset: float = 0.0) -> float:
    """The q-th percentile of `column` across one arm's paths, plus `offset` (the engine's percentile)."""
    vals = [float(x) for x in pd.to_numeric(arm(paths, shift, enforcement_p, run)[column], errors="coerce")]
    return _pct(vals, q) + float(offset)


def p95_path(paths: pd.DataFrame, *, margin: float = DEFAULT_MARGIN) -> dict[str, float]:
    """The required-bankroll p95 path: the lower-bound arm's p95 of the deepest loss from the start (the FAIL-MODEL
    level of D-400's P2 and the protocol's drawdown line), the point arm's (the FLAG level), and the required bankroll
    at p95 (the lower-bound arm's p95 plus one subscription)."""
    lb = paths_quantile(paths, "deepest_loss_from_start", 95, shift="lower_bound")
    pt = paths_quantile(paths, "deepest_loss_from_start", 95, shift="point")
    return {"deepest_loss_p95_lower_bound": lb, "deepest_loss_p95_point": pt, "required_p95_lower_bound": lb + margin}


@dataclass(frozen=True)
class FlagMeasure:
    name: str
    candidate_column: str       # the candidate's gate-row column (its median path, or the engine's p50)
    path_column: str            # P-06's per-path column the level is read from
    worse: str                  # "higher" or "lower"
    offset: float = 0.0         # added to the per-path value (the required bankroll's one subscription)

    @property
    def q(self) -> float:
        return 90.0 if self.worse == "higher" else 10.0


#: §5's table, one rule for every measure
FLAG_MEASURES: tuple[FlagMeasure, ...] = (
    FlagMeasure("required_bankroll", "pf_required_p50", "deepest_loss_from_start", "higher", DEFAULT_MARGIN),
    FlagMeasure("largest_drawdown", "pf_max_drawdown_p50", "max_drawdown", "higher"),
    FlagMeasure("days_to_first_payout", "median_days_to_first_payout", "days_to_first_payout", "higher"),
    FlagMeasure("payouts_per_month", "st_payouts_per_month_p50", "st_payouts_per_month", "lower"),
    FlagMeasure("red_month_share", "st_red_share_p50", "st_red_share", "higher"),
    FlagMeasure("month_sd", "st_month_sd_p50", "st_month_sd", "higher"),
    FlagMeasure("underwater_days", "st_underwater_days_p50", "st_underwater_days", "higher"),
)


def flag_levels(detail: pd.DataFrame, shift: str = "lower_bound") -> pd.DataFrame:
    """Each FLAG measure's level from P-06's per-path detail: the arm's 90th (or 10th) percentile path, with the
    arm's p50 and p95 beside for reading."""
    rows = []
    for m in FLAG_MEASURES:
        vals = [float(x) for x in pd.to_numeric(arm(detail, shift)[m.path_column], errors="coerce")]
        rows.append({"measure": m.name, "candidate_column": m.candidate_column, "p06_path_column": m.path_column,
                     "worse": m.worse, "q": m.q, "level": _pct(vals, m.q) + m.offset,
                     "p06_p50": _pct(vals, 50) + m.offset, "p06_p95": _pct(vals, 95) + m.offset,
                     "p06_p10": _pct(vals, 10) + m.offset, "p06_arm": shift})
    return pd.DataFrame(rows)


def flags(gate_row: dict[str, Any] | pd.Series, levels: pd.DataFrame) -> dict[str, bool | None]:
    """A candidate's FLAGs: True where its gate-row column is beyond the level in the bad direction, False where not,
    None where the candidate's file has no such column (a measure built after its run)."""
    out: dict[str, bool | None] = {}
    for r in levels.itertuples(index=False):
        v = gate_row.get(r.candidate_column) if hasattr(gate_row, "get") else None
        try:
            v = float(v)
        except (TypeError, ValueError):
            v = float("nan")
        if v != v:
            out[r.measure] = None
        else:
            out[r.measure] = bool(v > r.level) if r.worse == "higher" else bool(v < r.level)
    return out


__all__ = ["GATE_RUN", "arm", "paths_quantile", "p95_path", "FlagMeasure", "FLAG_MEASURES", "flag_levels", "flags"]
