"""The sizeable stop band (D-201 (2)): per market with a micro and per lifecycle state of stage one's family, the stop
distances, in the micro's own ticks, at which a trade both sizes and is worth its costs.

* **The wide edge**: the widest stop that buys one whole micro at the state's dollar risk, floor(risk / tick value)
  ticks. Beyond it the trade is unsizeable (D-190's edge).
* **The narrow edge**: the larger of two stops. One is the stop below which the state's size cap binds,
  ceil(risk / (cap x tick value)), with the cap as the engine sets it (`propedge/campaign/sizing.py`, the current
  tier's allowance x 0.75, at the state's lowest balance, where it binds most); below it the trade no longer risks
  the state's dollars. The other is the stop at which the cost drag -- the round turn plus the fill model's slippage
  for a trade that ends at its stop, over the stop in dollars, per contract -- falls to 0.10: a stop narrow enough
  that costs eat a tenth of it is out of the band whether or not it sizes.

A model card cites the band and fails contract fit when more than 25 % of its screen's stops fall outside it, on
either side, in any state (`share_outside`; D-190 extended). The band is regenerated whenever an input changes: its
manifest records the inputs' sha256 (`INPUTS`), and `tests/test_stop_band.py` fails on a stale band.
"""
from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Any

import pandas as pd

from propedge import REPO_ROOT

#: Stage one's lifecycle family (P-04 §3, from vendor/propsim/results_state_policy_combine.csv, "static 1:1 $1500
#: 1/day", and results_state_policy_xfa.csv, "build 2:1 $1000 -> harvest 1:1 $300 @B>=2000"): state, the state's
#: dollar risk, the sizing kind, and the balance the state's cap is read at (its lowest).
FAMILY: tuple[tuple[str, float, str, float], ...] = (
    ("combine", 1500.0, "combine", 0.0),
    ("funded_below_2000", 1000.0, "funded", 0.0),
    ("funded_at_or_above_2000", 300.0, "funded", 2000.0),
)
COST_DRAG_FLOOR = 0.10
MAX_OUTSIDE = 0.25                     # D-190's share, on either side of the band (D-201)
FILL_PROFILE = "assumed"               # D-95: one tick of the micro on entry, stop and close
#: What the band is computed from; a change to any of them makes the committed band stale.
INPUTS = ("config/instruments.yaml", "config/rules.yaml", "config/fills.yaml", "propedge/research/stop_band.py")
RESULT = "stop_band.csv"


def input_hashes(root: Path | None = None) -> dict[str, str]:
    """{input: sha256 with line endings normalised}."""
    base = Path(root) if root is not None else REPO_ROOT
    return {p: hashlib.sha256((base / p).read_bytes().replace(b"\r\n", b"\n")).hexdigest() for p in INPUTS}


def micro_markets(instruments: dict) -> dict[str, str]:
    """{market: its micro} for every micro the loader lists from `config/instruments.yaml` (MES, MNQ, MCL, M6E, MNG):
    a micro's symbol is 'M' + its market's."""
    return {s[1:]: s for s in sorted(instruments) if s.startswith("M") and len(s) >= 3}


def cost_drag_floor_ticks(fill_model, instrument, *, floor: float = COST_DRAG_FLOOR, max_ticks: int = 100_000) -> int:
    """The narrowest stop, in the instrument's ticks, whose cost drag for one contract ending at its stop is at most
    `floor`."""
    from propedge.execution.costs import ExitReason, trade_cost

    lo, hi = 1, max_ticks
    while lo < hi:                      # the drag falls as the stop widens
        mid = (lo + hi) // 2
        drag = trade_cost(fill_model, instrument, contracts=1, dollars_risked=mid * instrument.tick_value,
                          exit_reason=ExitReason.STOP).drag_fraction
        lo, hi = (lo, mid) if drag <= floor else (mid + 1, hi)
    return lo


def band_rows(*, instruments: dict | None = None, fill_model=None, sizing=None) -> list[dict[str, Any]]:
    """One row per market with a micro and per state of `FAMILY` (see the module docstring)."""
    from propedge.campaign.sizing import CURRENT_TIER, DEFAULT_HEADROOM_FRAC, SizingRule
    from propedge.execution.fills import FillModel
    from propedge.execution.instruments import load_instruments

    instruments = instruments if instruments is not None else load_instruments()
    fill_model = fill_model if fill_model is not None else FillModel.load(FILL_PROFILE)
    sizing = sizing if sizing is not None else SizingRule.from_ledger(CURRENT_TIER, headroom_frac=DEFAULT_HEADROOM_FRAC)
    rows = []
    for market, micro in micro_markets(instruments).items():
        inst = instruments[micro]
        tv = float(inst.tick_value)
        drag_ticks = cost_drag_floor_ticks(fill_model, inst)
        for state, risk, kind, balance in FAMILY:
            cap = int(sizing.cap_micros(kind, balance))
            cap_ticks = math.ceil(risk / (cap * tv))
            rows.append({"market": market, "micro": micro, "state": state, "risk": risk, "tick_size": inst.tick_size,
                         "tick_value": tv, "cap_micros": cap, "cap_stop_ticks": cap_ticks,
                         "cost_drag_floor_ticks": drag_ticks, "narrow_ticks": max(cap_ticks, drag_ticks),
                         "wide_ticks": math.floor(risk / tv)})
    return rows


def share_outside(stops: pd.DataFrame, band: pd.DataFrame) -> dict[str, float]:
    """{state: the share of `stops` (columns `market`, `stop_ticks` in the micro's ticks) outside its market's band,
    either side}. A stop in a market the band does not cover counts as outside."""
    out = {}
    for state, b in band.groupby("state", sort=False):
        lim = b.set_index("market")[["narrow_ticks", "wide_ticks"]]
        lo = stops["market"].map(lim["narrow_ticks"])
        hi = stops["market"].map(lim["wide_ticks"])
        inside = (stops["stop_ticks"] >= lo) & (stops["stop_ticks"] <= hi)
        out[state] = float((~inside).mean()) if len(stops) else float("nan")
    return out


__all__ = ["FAMILY", "COST_DRAG_FLOOR", "MAX_OUTSIDE", "INPUTS", "RESULT", "input_hashes", "micro_markets",
           "cost_drag_floor_ticks", "band_rows", "share_outside"]
