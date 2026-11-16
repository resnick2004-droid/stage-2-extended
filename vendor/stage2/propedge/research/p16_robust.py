"""EXPLORATORY (D-602): D-536's slower-hands and calendar-year sections on P-16's own cell -- the pure parts.
`scripts/p16_robust.py` walks the bars, builds the cells, runs the engine and writes `results/p16_robust.csv`.

**What it is** (DECISIONS.md's D-602 row, fixed before this code was built): P-16's cell (`rc_s150_all`, the news-safe
all-day coin at 37.5 points, coin seed 20261102, re-entry when flat, v12's no-closure table, P-14's protocol, five
Topstep seats) read (1) under late entries -- every entry at the `delay`-th bar with an open after the mark
(`fast_walk.entry_bar`), delays 1, 3 and 5 bars, the walk rerun at the delay and D-525 (4)'s cutoff re-read on that
walk's kind columns -- and (2) on each calendar year's sessions alone (2020 .. 2026, the last to 2026-07-16), D-536
(4)'s construction (`rc_robust.run_years`): the year's own pooled 0.05 bound (`a3_brk30.check_bounds`), the full cell's
day capacity, the campaign's 504-session horizon resampling that year's days. (3) Beside: the fifty
`R0_longest_waiting` coin-sequence rows of `results/rc150_routing.csv` (D-568's G2: seeds 20261600 + i, 200 paths, the
same campaign seed) -- the share growing at the bound, the quantiles and where P-16's own coin, run the same way, falls.

Reading only (D-602 (5)): no delay, year or seed is chosen; a weak year or a delay that stops the growth is P-16's
limit, reported beside its registered verdict.
"""
from __future__ import annotations

import hashlib
import math
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from propedge.research import resolved_coin as rc

DECISION = "D-602"
RESULT = "p16_robust"
FAMILY_ID = f"{DECISION}:p16_robust"
FAMILIES = ("latency", "years")            # D-602: one variant record per reading family
STOP = 150                                 # P-16's 37.5 points (MNQ ticks)
WINDOW = "all"
CELL = rc.reentry_cell_name(STOP, WINDOW)  # rc_s150_all
COIN_SEED = rc.COIN_SEED                   # 20261102
CAMPAIGN_SEED = 20261131                   # D-602 (1): the screens' seed (rc_screen.SEED), rc_width_screen's row
N_PATHS = 500
HORIZON = 504                              # the campaign's sessions (config: gate.campaign.horizon_days)
DELAYS = (1, 3, 5)                         # D-602 (1), as D-536 (3)
BASE_DELAY = 0                             # P-16's entry (resolved_coin.DELAY): the identity row
YEARS = (2020, 2021, 2022, 2023, 2024, 2025, 2026)
LAST_DAY = "2026-07-16"
BESIDE_PATHS = 200                         # rc150_routing.G2_PATHS: the fifty coin sequences' path count
QUANTILES = (5, 10, 25, 50, 75, 90, 95)
SCREEN_FILE = "rc_width_screen.csv"
ROUTING_FILE = "rc150_routing.csv"
ROUTING_REF = "R0_longest_waiting"
#: the routing screen's file as D-568's run wrote it (D-569); the beside reads it, never reruns it
ROUTING_SHA256 = "d4d2568e09ba273a4fb7e4498f458b9a07bc9f1e1c4d192b6293be95680c014e"
ROUTING_COIN_SEEDS = tuple(20261600 + i for i in range(50))
COMPARABLE_SEED = ROUTING_COIN_SEEDS[0]    # the routing row rebuilt here: P-16's own coin is run the same way
IDENT_COLS = ("growth_on_required", "growth_on_required_point", "required_p90")
IDENT_ATOL = 1e-9
READING = ("EXPLORATORY (D-602): P-16's cell under late entries (1, 3, 5 bars) and on each calendar year alone, beside "
           "rc150_routing's fifty coin sequences; selects nothing")


# ------------------------------------------------------------------------------------------------ the declaration

#: DECISIONS.md's D-602 row (LF, the line itself): its sha256 and the phrases each constant rests on
DECLARATION_SHA256 = "ad48104079122a03a767d8d28e9bd12f48bd0b16302199a75502fb9c3aa98516"
D602_WORDS = (
    "Declared before anything of it is read (EXPLORATORY, selects nothing)",
    "D-536's slower-hands and calendar-year sections run on P-16's own cell -- the 37.5-point coin",
    "P-16's coin draw is covered by `results/rc150_routing.csv`'s fifty coin sequences, read beside here (no new coins)",
    "every entry at the `delay`-th bar with an open after the mark (`fast_walk.entry_bar`), delays "
    f"{DELAYS[0]}, {DELAYS[1]} and {DELAYS[2]} bars",
    "the walk rerun at the delay, D-525 (4)'s cutoff re-read on that walk's kind columns (its admitted marks reported)",
    f"the strict rule, the coin ({COIN_SEED}), the news-safe cut and everything else P-16's",
    f"campaign seed {CAMPAIGN_SEED}, {N_PATHS} paths",
    "growth on the required bankroll at the bound and the point, the required bankroll, every offered R resolving",
    f"P-16's cell on each calendar year's sessions alone ({YEARS[0]} .. {YEARS[-1]}, the last to {LAST_DAY})",
    "its own pooled 0.05 bound (`a3_brk30.check_bounds`)",
    "the cell's day capacity",
    f"the campaign's {HORIZON}-session horizon resampling that year's days, {N_PATHS} paths -- D-536 (4)'s construction",
    f"the share of `{ROUTING_FILE}`'s fifty `{ROUTING_REF}` coin-sequence rows growing at the bound and where P-16's "
    "own coin falls among them",
    f"the cell's content hash is P-16's; delay 0 through the latency path reproduces `{SCREEN_FILE}`'s {CELL} at "
    f"{N_PATHS} paths",
    "no delay, year or seed is chosen",
    f"Writes `results/{RESULT}.csv` (EXPLORATORY; `{FAMILY_ID}`, one record per reading family: "
    f"{', '.join(FAMILIES)})",
    "workers 1",
)


def declaration(path: Path | str | None = None) -> dict[str, Any]:
    """DECISIONS.md's D-602 row (LF line ends, the line itself) and its sha256 (`rc_stop_fine.declaration`'s way)."""
    p = Path(path) if path is not None else Path(__file__).resolve().parents[2] / "DECISIONS.md"
    text = p.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")
    rows = [line for line in text.split("\n") if line.startswith(f"| {DECISION} |")]
    row = rows[0] if len(rows) == 1 else ""
    return {"path": str(p), "rows": len(rows), "row": row, "sha256": hashlib.sha256(row.encode("utf-8")).hexdigest()}


def declaration_problems(decl: Mapping[str, Any]) -> list[str]:
    """Every way this module's constants differ from D-602's row (an empty list: they agree)."""
    out = []
    if int(decl["rows"]) != 1:
        out.append(f"DECISIONS.md holds {decl['rows']} {DECISION} rows, not one")
    if str(decl["sha256"]) != DECLARATION_SHA256:
        out.append(f"the {DECISION} row's sha256 is {str(decl['sha256'])[:16]}, not the pinned "
                   f"{DECLARATION_SHA256[:16]}")
    row = re.sub(r"\s+", " ", str(decl["row"]))
    out += [f"{DECISION} does not say {w!r}" for w in D602_WORDS if w not in row]
    if STOP not in rc.WIDTH_STOPS:
        out.append(f"P-16's stop {STOP} is not one of D-538's {rc.WIDTH_STOPS}")
    if BASE_DELAY != rc.DELAY:
        out.append(f"the identity delay {BASE_DELAY} is not P-16's entry delay {rc.DELAY}")
    return out


# ------------------------------------------------------------------------------------------------ the years


def year_span(year: int) -> tuple[str, str]:
    """One calendar year's sessions [lo, hi] as `rc_robust.run_years` takes them (2026 to the window's last day)."""
    y = int(year)
    return f"{y}-01-01", (LAST_DAY if y == YEARS[-1] else f"{y}-12-31")


# ------------------------------------------------------------------------------------------------ the marks


def marks_change(base: Sequence[int], marks: Sequence[int]) -> dict[str, Any]:
    """The marks a delayed walk's cutoff admits against delay 0's (`rc_robust.run_latency`'s `latency_marks` row)."""
    b, m = set(int(x) for x in base), set(int(x) for x in marks)
    return {"marks_admitted": len(m), "marks_admitted_delay0": len(b),
            "marks_dropped_vs_delay0": " ".join(rc.ct(x) for x in sorted(b - m)),
            "marks_added_vs_delay0": " ".join(rc.ct(x) for x in sorted(m - b))}


# ------------------------------------------------------------------------------------------------ the readings


def reading(df, taken: float | None = None) -> dict[str, Any]:
    """A gate run's reading at 0 % denial: growth on the required bankroll at the bound and the point, the required
    bankroll at each, whether it grows at the bound (`rc150_routing.run_rule`'s columns, plus the point's bankroll)."""
    def at(shift: str, col: str) -> float:
        r = df[(df["shift"] == shift) & np.isclose(df["enforcement_p"].astype(float), 0.0)]
        if len(r) != 1:
            raise ValueError(f"{len(r)} gate rows at {shift}, 0 %")
        return float(r.iloc[0][col])

    gb = at("lower_bound", "pf_growth_on_base_p50")
    out = {"growth_on_required": gb, "growth_on_required_point": at("point", "pf_growth_on_base_p50"),
           "required_p90": at("lower_bound", "pf_required_p90"),
           "required_p90_point": at("point", "pf_required_p90"), "grows_at_bound": bool(gb > 0)}
    if taken is not None:
        out["trades_taken_per_session"] = float(taken)
    return out


def beside_summary(growths: Sequence[float], own: float) -> dict[str, Any]:
    """The coin sequences' growth at the bound (D-602 (3)): the share above zero, the quantiles, and P-16's own coin's
    place among them (`rc_robust.coins_summary`'s arithmetic: rank 1 = below every sequence)."""
    g = np.asarray([float(x) for x in growths], float)
    if not len(g) or not np.all(np.isfinite(g)):
        raise ValueError("the coin sequences' growths must be finite and non-empty")
    q = {f"growth_on_required_p{p}": float(np.percentile(g, p)) for p in QUANTILES}
    o = float(own)
    return {"sequences": int(len(g)), "share_growing_at_bound": float(np.mean(g > 0)),
            "growth_on_required_min": float(g.min()), "growth_on_required_max": float(g.max()), **q,
            "own_coin_growth_on_required": o, "own_coin_share_of_sequences_below": float(np.mean(g < o)),
            "own_coin_rank": int(np.sum(g < o)) + 1}


def row_problems(mine: Mapping[str, Any], want: Mapping[str, Any], cols: Sequence[str] = IDENT_COLS,
                 atol: float = IDENT_ATOL, what: str = "the file") -> list[str]:
    """A reading against a written row (each of `cols` within `atol`; a missing or non-finite value is a problem)."""
    out = []
    for c in cols:
        try:
            a, b = float(mine[c]), float(want[c])
        except (KeyError, TypeError, ValueError):
            out.append(f"{c}: missing")
            continue
        if not (math.isfinite(a) and math.isfinite(b) and abs(a - b) <= atol):
            out.append(f"{c}: {a!r} against {what}'s {b!r}")
    return out


__all__ = ["DECISION", "RESULT", "FAMILY_ID", "FAMILIES", "STOP", "WINDOW", "CELL", "COIN_SEED", "CAMPAIGN_SEED",
           "N_PATHS", "HORIZON", "DELAYS", "BASE_DELAY", "YEARS", "LAST_DAY", "BESIDE_PATHS", "QUANTILES",
           "SCREEN_FILE", "ROUTING_FILE", "ROUTING_REF", "ROUTING_SHA256", "ROUTING_COIN_SEEDS", "COMPARABLE_SEED",
           "IDENT_COLS", "IDENT_ATOL", "READING", "DECLARATION_SHA256", "D602_WORDS", "declaration",
           "declaration_problems", "year_span", "marks_change", "reading", "beside_summary", "row_problems"]
