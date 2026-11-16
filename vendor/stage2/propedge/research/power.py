"""Required and available trade counts from the planted-effect power curve (D-192; T12 item 3).

From P-05 every registration states how many trades its test needs and how many its data will supply. The required
count is read from L5's power curve (`results/l5_power_curve.csv`, `scripts/l5_planted_effect.py --part curve`): the
power of the registered lower bound to clear zero, per R, planted e and trade count, at the curve's own statistic and
bootstrap length. A registration whose statistic or bootstrap length differs from the curve's cannot read it, and
falls back to `assumed_sd` (`metrics.sample_size_required`), labelled as the fallback.

* **Target power** `POWER_TARGET`: 0.80, the conventional level (D-208). Stage one's own sample-size rule -- the bound
  above half the true edge -- corresponds to about 0.95 at the normal approximation; the registration also states the
  power its available trades give, so neither level hides the other.
* **Between grid points** the count is interpolated linearly in log trades; beyond the largest count the curve has,
  the requirement is reported as above it (`None`), never extrapolated.
* **An effect size between the curve's** is read at the largest tabulated e not above it (the conservative side); an
  effect below the smallest positive e cannot be read.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import pandas as pd

from propedge import RESULTS_DIR

POWER_TARGET = 0.80
CURVE_FILE = RESULTS_DIR / "l5_power_curve.csv"


def load_curve(path: Path | None = None) -> tuple[pd.DataFrame, dict[str, Any]]:
    """The power curve and its manifest's parameters (statistic, boot_len, rate_per_day), through the manifest check."""
    from propedge.reporting.results import read_manifest, read_result

    p = Path(path) if path is not None else CURVE_FILE
    return read_result(p), dict(read_manifest(p).parameters)


def _curve_at(curve: pd.DataFrame, R: float, e: float) -> tuple[pd.DataFrame, float]:
    """The curve's rows at R and at the largest tabulated positive e not above `e`, sorted by trades."""
    at_r = curve[(curve["R"] - float(R)).abs() < 1e-9]
    if at_r.empty:
        raise ValueError(f"the power curve has no rows at R = {R:g} (it has R {sorted(curve['R'].unique())})")
    grid = sorted(x for x in at_r["e"].unique() if 0 < x <= float(e) + 1e-12)
    if not grid:
        raise ValueError(f"effect {e:g} is below the smallest positive e the curve tabulates at R = {R:g}")
    e_read = float(grid[-1])
    return at_r[(at_r["e"] - e_read).abs() < 1e-12].sort_values("trades"), e_read


def required_trades(curve: pd.DataFrame, R: float, e: float, *, target: float = POWER_TARGET) -> dict[str, Any]:
    """{'required': trades at which the bound clears zero with probability `target` (None if the curve never reaches
    it), 'e_read': the effect the curve was read at, 'max_trades': the curve's largest count}."""
    rows, e_read = _curve_at(curve, R, e)
    n, pw = rows["trades"].to_numpy(float), rows["power"].to_numpy(float)
    out = {"R": float(R), "e": float(e), "e_read": e_read, "target": float(target), "max_trades": int(n.max()),
           "required": None}
    if pw[0] >= target:
        out["required"] = int(n[0])
        return out
    for i in range(1, len(n)):
        if pw[i] >= target:
            f = (target - pw[i - 1]) / (pw[i] - pw[i - 1])
            out["required"] = int(math.ceil(math.exp(math.log(n[i - 1]) + f * (math.log(n[i]) - math.log(n[i - 1])))))
            return out
    return out


def power_at(curve: pd.DataFrame, R: float, e: float, trades: float) -> float | None:
    """The curve's power at `trades` (log-linear between grid points; None outside the curve's range of counts)."""
    rows, _ = _curve_at(curve, R, e)
    n, pw = rows["trades"].to_numpy(float), rows["power"].to_numpy(float)
    t = float(trades)
    if t < n[0] or t > n[-1]:
        return None
    for i in range(1, len(n)):
        if t <= n[i]:
            f = (math.log(t) - math.log(n[i - 1])) / (math.log(n[i]) - math.log(n[i - 1]))
            return float(pw[i - 1] + f * (pw[i] - pw[i - 1]))
    return float(pw[-1])


__all__ = ["POWER_TARGET", "CURVE_FILE", "load_curve", "required_trades", "power_at"]
