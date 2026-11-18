"""RD-05's readings (`prereg/RD-05_firm_modes.md` 10, 11, 12.5, 12.6, 4.7 item 5; A-15): the large-days count `k*`, the
last gate to open, the exposures, the paired coin readings, and the menu with its flags.

* **`k*` (10.1).** For a pass, the fewest of its trading days, largest first, whose profit sums to the base target.
  On a steady coin cell `k*` is arithmetic (`ceil(T / (w r))`, printed as such); on a flip cell it follows exactly from
  A-13's two win counts (`k_star_from_counts`): the flip wins first, then the steady wins. On records, a sort
  (`k_star_from_days`).
* **The last gate (11).** From A-13's sessions at which each gate last turned true (S-4): the condition that held last at the pass (ties named in the
  order base target, consistency-raised target, minimum days); for a failure its cause; on the funded side the gate
  that held last before the first payout (`last_funded_gate`).
* **The menu (12.6).** Every cell stays on it; no P without its guard row; the exposures of 4.7 item 5 the same for
  `flip` and `steady`; the mechanical flags. `menu_problems` is T-12's check.
"""
from __future__ import annotations

import math
from typing import Any, Iterable, Sequence

import numpy as np

from extended import modes_terms as M

EPS = 1e-9


def k_star_steady(T: float, w: float, r: float) -> int:
    """10.1 (N3): on a steady coin cell every win is `w r`, so `k* = ceil(T / (w r))` on every pass."""
    return int(math.ceil(float(T) / (float(w) * float(r)) - 1e-12))


def k_star_from_counts(flip_wins: np.ndarray, steady_wins: np.ndarray, T: float, w: float, r_flip: float,
                       r: float) -> np.ndarray:
    """10.1 on a flip cell: the largest days are the flip wins (`w r_flip` each, the larger), then the steady wins
    (`w r`); `k*` the fewest of them summing to `T` (-1 where they cannot)."""
    a, b = float(w) * float(r_flip), float(w) * float(r)
    hi, lo = (a, b) if a >= b else (b, a)
    n_hi = np.asarray(flip_wins if a >= b else steady_wins, int)
    n_lo = np.asarray(steady_wins if a >= b else flip_wins, int)
    need_hi = int(math.ceil(float(T) / hi - 1e-12))
    out = np.where(n_hi >= need_hi, need_hi, -1)
    rest = float(T) - n_hi * hi
    need_lo = np.ceil(np.maximum(rest, 0.0) / lo - 1e-12).astype(int)
    take = (n_hi < need_hi) & (n_lo >= need_lo)
    out = np.where(take, n_hi + need_lo, out)
    return out


def k_star_from_days(day_pnls: Sequence[float], T: float) -> int:
    """10.1 on records: the fewest of the trading days, largest first, whose profit sums to `T` (-1: none)."""
    s = 0.0
    for i, x in enumerate(sorted((float(v) for v in day_pnls), reverse=True)):
        if x <= 0:
            break
        s += x
        if s >= float(T) - EPS:
            return i + 1
    return -1


def k_star_distribution(k: np.ndarray) -> dict[str, float]:
    """10.1's printed distribution: 1, 2, 3, 4, 5 and more, and the shares `k* = 1` and `k* <= 2`."""
    k = np.asarray(k)
    k = k[k > 0]
    n = len(k)
    bins = M.declared("large_days.bins")
    out = {f"k{b}": (float(np.mean(k == b)) if n else float("nan")) for b in bins[:-1]}
    out[f"k{bins[-1]}+"] = float(np.mean(k >= bins[-1])) if n else float("nan")
    out["share_k1"] = out.get("k1", float("nan"))
    out["share_k_le2"] = float(np.mean(k <= bins[1])) if n else float("nan")
    out["n"] = n
    return out


EVAL_GATES = ("base_target", "consistency_target", "min_days")


def last_gate(first: dict[str, int], raised: bool) -> str:
    """11 item 2 on one pass's last-rise sessions (the session each gate last turned true, S-4): the gate that held last (ties in `EVAL_GATES` order); the
    consistency target is named only when it raised the target."""
    order = [g for g in EVAL_GATES if g in first and first[g] is not None and first[g] >= 0]
    if not order:
        raise ValueError("a pass with no gate held")
    best = max(first[g] for g in order)
    g = next(x for x in order if first[x] == best)
    if g == "consistency_target" and not raised:
        return "base_target"
    return g


FUNDED_GATES = ("winning_days", "cycle_share", "cycle_days", "buffer_min", "clock", "profit_since")


def last_funded_gate(first: dict[str, int]) -> str | None:
    """11 item 2 on a first payout's gates: the one that held last among those the plan has (ties in
    `FUNDED_GATES` order)."""
    have = [(g, first[g]) for g in FUNDED_GATES if g in first and first[g] is not None and first[g] >= 0]
    if not have:
        return None
    best = max(v for _, v in have)
    return next(g for g, v in have if v == best)


def gate_shares(labels: Iterable[str]) -> dict[str, float]:
    """11 item 3: the share of each last gate and each cause; none singled out."""
    labels = [str(x) for x in labels if str(x)]
    n = len(labels)
    out: dict[str, float] = {}
    for x in sorted(set(labels)):
        out[x] = labels.count(x) / n
    return out


def paired_difference(a: np.ndarray, b: np.ndarray) -> dict[str, float]:
    """10.2 / 12.5 on the coin: a paired difference on common streams with its paired standard error."""
    d = np.asarray(a, float) - np.asarray(b, float)
    n = len(d)
    return {"diff": float(np.mean(d)), "se": float(np.std(d, ddof=1) / math.sqrt(n)) if n > 1 else float("nan"),
            "n": n}


# ------------------------------------------------------------------------------------------------ exposures

EXPOSURES = ("stacking_share", "evaluations_per_21", "full_allowance_share", "s8_ratio_max", "size_spread")


def exposures_row(policy: str, values: dict[str, Any]) -> dict[str, Any]:
    """4.7 item 5: the exposures beside every cell, the same columns for `flip` and `steady` (a value absent where it
    does not apply, printed so: the gross coin has no contracts)."""
    if policy not in ("flip", "steady"):
        raise ValueError(policy)
    return {"policy": policy, **{k: values.get(k, "not applicable") for k in EXPOSURES}}


# ------------------------------------------------------------------------------------------------ the menu

FLAGS = {
    "gross": "allowance and scaling not applied",
    "coin": "no calendar: no news rule",
    "fees_upper": "upper bound in fees",
    "general": "from the general article",
    "price_grid": "price unverified: on the grid",
    "table_fixed": "first-order, the table fixed",
    "unstable": "not stable across blocks",
    "straddle": "corners straddle the reference",
}


def flags_for(cell: dict[str, Any]) -> list[str]:
    """12.6's flags, mechanical, from a menu cell's own fields."""
    out = []
    if cell.get("part") == "C":
        out.append(FLAGS["coin"])
        if cell.get("coin") == "gross":
            out.append(FLAGS["gross"])
    if cell.get("part") == "F":
        out.append(FLAGS["table_fixed"])
    labels = str(cell.get("labels", ""))
    if "upper bound in fees" in labels:
        out.append(FLAGS["fees_upper"])
    if "from the general article" in labels:
        out.append(FLAGS["general"])
    if "price unverified" in labels:
        out.append(FLAGS["price_grid"])
    if cell.get("signs_by_block") and len(set(cell["signs_by_block"])) > 1:
        out.append(FLAGS["unstable"])
    if cell.get("corner_values") is not None and cell.get("reference") is not None:
        lo, hi = min(cell["corner_values"]), max(cell["corner_values"])
        if lo < float(cell["reference"]) < hi:
            out.append(FLAGS["straddle"])
    return out


def menu_rows(cells: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    """12.6: every cell on the menu with its flags; nothing withheld for conduct."""
    rows = []
    for c in cells:
        rows.append({**c, "flags": "; ".join(flags_for(c)), "described": "described, not carried"})
    return rows


def menu_problems(rows: Sequence[dict[str, Any]], cells: Sequence[dict[str, Any]]) -> list[str]:
    """T-12: no P without its guard row; every exposure for flip and steady alike; no cell withheld; the flags."""
    out = []
    if len(rows) != len(cells):
        out.append("a cell is withheld from the menu")
    for r in rows:
        if r.get("part") == "F" and "P" in r and not r.get("guard"):
            out.append(f"{r.get('cell')}: a P without its guard row")
        if r.get("policy") in ("flip", "steady") and any(k not in r for k in EXPOSURES):
            out.append(f"{r.get('cell')}: an exposure missing")
        if r.get("part") == "C" and FLAGS["coin"] not in r.get("flags", ""):
            out.append(f"{r.get('cell')}: a coin row without '{FLAGS['coin']}'")
        if r.get("part") == "C" and r.get("coin") == "gross" and FLAGS["gross"] not in r.get("flags", ""):
            out.append(f"{r.get('cell')}: a gross row without '{FLAGS['gross']}'")
    return out


def intervals_note(n_intervals: int) -> str:
    """12.5: the menu prints the number of 90 % intervals it shows and that a tenth would exclude zero by chance."""
    return (f"{int(n_intervals)} 90 % intervals are shown; about a tenth would exclude zero by chance alone -- a count, "
            "not a level")


__all__ = ["k_star_steady", "k_star_from_counts", "k_star_from_days", "k_star_distribution", "EVAL_GATES", "last_gate",
           "FUNDED_GATES", "last_funded_gate", "gate_shares", "paired_difference", "EXPOSURES", "exposures_row",
           "FLAGS", "flags_for", "menu_rows", "menu_problems", "intervals_note"]
