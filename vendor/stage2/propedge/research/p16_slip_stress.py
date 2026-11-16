"""D-583: a fill-slippage stress test of P-16 (`rc_s150_all_nr`) -- the pure parts. EXPLORATORY, beside P-16's registered
verdict; decides nothing, selects nothing.

**The base costs** (`config/fills.yaml`'s ASSUMED, D-95; `fv3_rung_walk.EXIT_TICKS` and the config's `slip_ticks`): one
tick on entry, one on a stop (and on a breakeven exit, which `EXIT_TICKS` costs as a stop), none on a target (a limit
fill needing a trade-through), two on the 15:08 flatten.

**The arms** (D-583, fixed before the build):

    base        entry 1, stop 1, flatten 2                       P-16 as it is
    A_stop<k>   entry 1, stop k, flatten k + 1, k in 2 3 5 8 12  exits only
    B_slip<k>   entry k, stop k, flatten k + 1, k in 2 3 5       entry too

Targets stay at zero slip in every arm; a breakeven exit ('b') takes the stop's slip, as `EXIT_TICKS` does. An arm's
*level* is its stop slip (A) or its entry = stop slip (B); the base is level 1 of both families.

**The stress** (`stress`): P-16's built trades with each offered R's net outcome lowered by the arm's extra ticks over
the base, by the exit's kind, in R:  r'_R = r_R - (d_entry + d_exit(o_R)) / S  and  c'_R = c_R + the same, S the row's
stop in ticks (150). The tick value cancels as it does in `resolved_coin.cell_trades`' own cost
((entry x tv + fee + exit(kind) x tv) / (S x tv)), so this is that cost recomputed at the arm's ticks (a test checks it
against `cell_trades` rebuilt at the arm's ticks). Gross (`g_R`), MAE, exits, kinds and every other column are
unchanged; an R the trades do not offer (a NaN outcome, or a column `zero_edge_decomposition.pad` added with no kind) is
left as it is. At the base every delta is zero and the trades come back unchanged (a copy), so their content hash is
P-16's.

**The reading** (`reading`, fixed by D-583): per family (A with the base, B with the base) the lowest declared level at
which growth on the required bankroll at the bound is at or below zero ("none" if every level grows) and the highest
declared level at which all four D-509 slice lines hold ("none" if no level holds them) -- read literally, level by
level; no interpolation.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

DECISION = "D-583"
RESULT = "p16_slip_stress"
COIN_SEED = 20261102                       # P-16's own coin (resolved_coin.COIN_SEED)
CAMPAIGN_SEED = 20261131                   # the screen's campaign seed (rc_screen.SEED)
N_PATHS = 500
STOP = 150                                 # P-16's stop in MNQ ticks (37.5 points)
KINDS = ("s", "t", "f", "b")               # resolved_coin.KIND_CODE's codes: stop, target, flatten, breakeven
#: the base ticks, D-95's ASSUMED: entry 1; by exit kind stop 1, target 0, flatten 2, breakeven 1 (as a stop)
BASE = {"entry": 1, "stop": 1, "flatten": 2}
LEVELS_A = (1, 2, 3, 5, 8, 12)             # (A) the stop slip; 1 is the base
LEVELS_B = (1, 2, 3, 5)                    # (B) the entry = stop slip; 1 is the base
N_VARIANTS = 8                             # nine runs, eight beyond the base
FAMILIES = ("A", "B")
NONE = "none"
#: the declaration: DECISIONS.md's D-583 row (LF, the line itself) -- its sha256 and the phrases each constant rests on
DECLARATION_SHA256 = "779e0e50e7bdf201dfd977f7cde4764c409ad19cfd2ead39448c8917f327d45d"
D583_WORDS = ("one tick on entry, one on a stop, two on the flatten",
              "its coin seed 20261102", "the sizing table stays the one solved at the base costs",
              "each trade's net R recomputed from its gross R and kind with more slippage",
              "(A) exits only -- stop slip 1 (the base), 2, 3, 5, 8, 12 ticks, the flatten one tick more than the stop, "
              "entry 1", "(B) entry too -- entry = stop slip at 2, 3, 5, the flatten one more",
              "nine runs, eight beyond the base (counted as variants under `D-583`)",
              "Targets stay limit fills (trade-through, zero slip)",
              "`rc150_routing.run_rule` with the zero-edge twin at the screen's campaign seed 20261131, 500 paths, the 0.05 "
              "bound by the era rule",
              "the base arm's trades equal P-16's hash",
              "the base arm's run equals `rc_width_screen.csv`'s `rc_s150_all` row and `rc150_routing.csv`'s R0 row",
              "each arm's added cost per trade equals the declared extra ticks over the stop in R, by kind",
              "the lowest declared level in each arm at which growth at the bound is at or below zero (none if every "
              "level grows), and the highest level at which all four slice lines hold; no interpolation",
              "Writes `results/p16_slip_stress.csv` with its manifest", "workers 1")
#: identity (ii)'s tolerance: r - r' and c' - c against the declared ticks / S, in R (floating subtraction only)
COST_ATOL = 1e-12


# ------------------------------------------------------------------------------------------------ the arms


def arm(name: str, family: str, level: int, entry: int, stop: int, flatten: int) -> dict[str, Any]:
    return {"arm": name, "family": family, "level": int(level), "entry_slip_ticks": int(entry),
            "stop_slip_ticks": int(stop), "flatten_slip_ticks": int(flatten), "target_slip_ticks": 0,
            "breakeven_slip_ticks": int(stop)}


def arms() -> list[dict[str, Any]]:
    """The nine runs in D-583's order: the base, then (A) exits only, then (B) entry too."""
    out = [arm("base", "base", 1, BASE["entry"], BASE["stop"], BASE["flatten"])]
    out += [arm(f"A_stop{k}", "A", k, BASE["entry"], k, k + 1) for k in LEVELS_A if k != 1]
    out += [arm(f"B_slip{k}", "B", k, k, k, k + 1) for k in LEVELS_B if k != 1]
    return out


def exit_ticks(a: Mapping[str, Any]) -> dict[str, int]:
    """An arm's exit ticks by kind code."""
    return {"s": int(a["stop_slip_ticks"]), "t": int(a["target_slip_ticks"]), "f": int(a["flatten_slip_ticks"]),
            "b": int(a["breakeven_slip_ticks"])}


def base_exit_ticks() -> dict[str, int]:
    return exit_ticks(arms()[0])


def added_ticks(a: Mapping[str, Any]) -> dict[str, int]:
    """The arm's extra ticks over the base, by exit kind: the entry's extra plus the exit's."""
    b, x = base_exit_ticks(), exit_ticks(a)
    d_entry = int(a["entry_slip_ticks"]) - BASE["entry"]
    return {k: d_entry + x[k] - b[k] for k in KINDS}


def base_problems(engine_exit_ticks: Mapping[int, float], kind_code: Mapping[int, str], entry_ticks: float) -> list[str]:
    """The base arm against the engine's own costs (`fv3_rung_walk.EXIT_TICKS` by `resolved_coin.KIND_CODE`, the walk's
    entry slip): they must be D-95's ticks, or the arms' deltas are not over the cost P-16 was built with."""
    out = []
    b = base_exit_ticks()
    got = {str(kind_code[int(k)]): float(v) for k, v in engine_exit_ticks.items()}
    if set(got) != set(KINDS):
        out.append(f"the engine's exit kinds {sorted(got)} are not {sorted(KINDS)}")
    for k in KINDS:
        if k in got and got[k] != float(b[k]):
            out.append(f"the engine costs a {k!r} exit {got[k]:g} ticks, the base {b[k]}")
    if float(entry_ticks) != float(BASE["entry"]):
        out.append(f"the walk's entry slip is {float(entry_ticks):g} ticks, the base {BASE['entry']}")
    return out


# ------------------------------------------------------------------------------------------------ the stress


def _r_columns(t: pd.DataFrame) -> list[str]:
    return [c for c in t.columns if c.startswith("r_") and c[2:].replace(".", "", 1).isdigit()]


def stress(trades: pd.DataFrame, a: Mapping[str, Any]) -> pd.DataFrame:
    """P-16's built trades at the arm's slippage: every offered R's `r_R` lowered and `c_R` raised by the arm's extra
    ticks over the base for that R's exit kind (`o_R`), over the row's stop in ticks (`S`). Fail-loud: an offered outcome
    with no kind, an unknown kind, or an R column with outcomes and no cost column is refused. At the base the trades come
    back unchanged (a copy)."""
    if trades is None or len(trades) == 0:
        raise ValueError("stress: no trades")
    out = trades.copy()
    add = added_ticks(a)
    if all(v == 0 for v in add.values()):
        return out
    if "S" not in out.columns:
        raise ValueError("stress needs the trades' 'S' (stop ticks) column")
    S = out["S"].astype(float).to_numpy()
    if not np.all(np.isfinite(S)) or np.any(S <= 0):
        raise ValueError("stress: a stop that is not a positive number of ticks")
    for col in _r_columns(out):
        R = col[2:]
        r = out[col].astype(float).to_numpy()
        on = np.isfinite(r)
        if not on.any():
            continue                                         # an R offered on none of the trades (padded)
        if f"o_{R}" not in out.columns or f"c_{R}" not in out.columns:
            raise ValueError(f"stress: {col} carries outcomes but the trades have no o_{R} / c_{R} column")
        kind = out[f"o_{R}"].astype(str).to_numpy()
        bad = on & ~np.isin(kind, KINDS)
        if bad.any():
            raise ValueError(f"stress: {int(bad.sum())} offered {col} outcomes with an exit kind outside {KINDS} "
                             f"(first {kind[bad][0]!r})")
        ticks = np.zeros(len(out))
        for k in KINDS:
            ticks[kind == k] = float(add[k])
        delta = np.where(on, ticks / S, 0.0)
        out[col] = np.where(on, r - delta, r)
        c = out[f"c_{R}"].astype(float).to_numpy()
        out[f"c_{R}"] = np.where(on, c + delta, c)
    return out


def cost_problems(base: pd.DataFrame, stressed: pd.DataFrame, a: Mapping[str, Any], atol: float = COST_ATOL
                  ) -> list[str]:
    """Identity (ii): the arm's added cost per trade equals the declared extra ticks over the stop in R, by kind, at every
    R (both `r - r'` and `c' - c`, within `atol`); the offered set (NaN pattern) unchanged; every other column, row and
    the order unchanged."""
    out = []
    if list(base.columns) != list(stressed.columns) or len(base) != len(stressed):
        return [f"{a['arm']}: the columns or the row count changed"]
    add = added_ticks(a)
    S = base["S"].astype(float).to_numpy()
    rc_cols = set()
    for col in _r_columns(base):
        R = col[2:]
        r0, r1 = base[col].astype(float).to_numpy(), stressed[col].astype(float).to_numpy()
        on = np.isfinite(r0)
        if not np.array_equal(on, np.isfinite(r1)):
            out.append(f"{a['arm']}: {col}'s offered set changed")
            continue
        rc_cols.add(col)
        if not on.any():
            continue
        rc_cols.add(f"c_{R}")
        kind = base[f"o_{R}"].astype(str).to_numpy()
        want = np.array([float(add.get(k, np.nan)) for k in kind]) / S
        got_r = r0 - r1
        got_c = stressed[f"c_{R}"].astype(float).to_numpy() - base[f"c_{R}"].astype(float).to_numpy()
        for what, got in (("r - r'", got_r), ("c' - c", got_c)):
            miss = on & ~(np.abs(got - want) <= float(atol))
            if miss.any():
                out.append(f"{a['arm']}: {col} {what} differs from the declared ticks / S on {int(miss.sum())} trades")
    others = [c for c in base.columns if c not in rc_cols]
    for c in others:
        if not base[c].reset_index(drop=True).equals(stressed[c].reset_index(drop=True)):
            out.append(f"{a['arm']}: column {c} changed")
    return out


# ------------------------------------------------------------------------------------------------ the reading


def family_rows(rows: Sequence[Mapping[str, Any]], family: str) -> list[Mapping[str, Any]]:
    """A family's arms with the base, by level ascending; every declared level present exactly once."""
    levels = LEVELS_A if family == "A" else LEVELS_B if family == "B" else None
    if levels is None:
        raise ValueError(f"unknown family {family!r}")
    by = {}
    for r in rows:
        if str(r["family"]) in ("base", family):
            lv = int(r["level"])
            if lv in by:
                raise ValueError(f"family {family}: level {lv} twice")
            by[lv] = r
    if sorted(by) != sorted(levels):
        raise ValueError(f"family {family}: levels {sorted(by)}, not the declared {list(levels)}")
    return [by[lv] for lv in sorted(levels)]


def reading(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """D-583's reading per family: the lowest declared level with growth on the required bankroll at the bound at or
    below zero, and the highest declared level at which all four slice lines hold ("none" for either when no level
    qualifies). A growth that is not a number, or a slice-line reading that is not a boolean, is refused."""
    out = []
    for fam in FAMILIES:
        fr = family_rows(rows, fam)
        lowest, highest = NONE, NONE
        for r in fr:
            g = float(r["growth_on_required"])
            if not np.isfinite(g):
                raise ValueError(f"family {fam}: level {r['level']}'s growth at the bound is not a number")
            if g <= 0.0 and lowest == NONE:
                lowest = int(r["level"])
            h = r["slice_lines_hold"]
            if not isinstance(h, (bool, np.bool_)):
                raise ValueError(f"family {fam}: level {r['level']}'s slice lines are not read ({h!r})")
            if bool(h):
                highest = int(r["level"])
        out.append({"section": "reading", "family": fam, "levels": " ".join(str(int(r["level"])) for r in fr),
                    "arms": " ".join(str(r["arm"]) for r in fr),
                    "lowest_level_growth_at_bound_at_or_below_zero": lowest,
                    "highest_level_all_slice_lines_hold": highest})
    return out


# ------------------------------------------------------------------------------------------------ the declaration


def declaration(path: Path | None = None) -> dict[str, Any]:
    """DECISIONS.md's D-583 row (LF line ends, the line itself) and its sha256."""
    p = Path(path) if path is not None else Path(__file__).resolve().parents[2] / "DECISIONS.md"
    text = p.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")
    rows = [line for line in text.split("\n") if line.startswith(f"| {DECISION} |")]
    row = rows[0] if len(rows) == 1 else ""
    return {"path": str(p), "rows": len(rows), "row": row, "sha256": hashlib.sha256(row.encode("utf-8")).hexdigest()}


def declaration_problems(decl: Mapping[str, Any]) -> list[str]:
    """Every way this module's constants differ from D-583's row (an empty list: they agree)."""
    out = []
    if int(decl["rows"]) != 1:
        out.append(f"DECISIONS.md holds {decl['rows']} {DECISION} rows, not one")
    if str(decl["sha256"]) != DECLARATION_SHA256:
        out.append(f"the D-583 row's sha256 is {str(decl['sha256'])[:16]}, not the pinned {DECLARATION_SHA256[:16]}")
    row = re.sub(r"\s+", " ", str(decl["row"]))
    out += [f"D-583 does not say {w!r}" for w in D583_WORDS if w not in row]
    a = arms()
    if len(a) != N_VARIANTS + 1 or len({x["arm"] for x in a}) != len(a):
        out.append(f"{len(a)} arms, not nine distinct")
    return out


__all__ = ["DECISION", "RESULT", "COIN_SEED", "CAMPAIGN_SEED", "N_PATHS", "STOP", "KINDS", "BASE", "LEVELS_A",
           "LEVELS_B", "N_VARIANTS", "FAMILIES", "NONE", "DECLARATION_SHA256", "D583_WORDS", "COST_ATOL", "arm", "arms",
           "exit_ticks", "base_exit_ticks", "added_ticks", "base_problems", "stress", "cost_problems", "family_rows",
           "reading", "declaration", "declaration_problems"]
