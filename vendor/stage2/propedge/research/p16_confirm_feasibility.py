"""EXPLORATORY (D-599): a confirmation-feasibility study of P-16 -- the pure parts. `scripts/p16_confirm_feasibility.py`
walks the bars, builds P-16's cell on each window and writes `results/p16_confirm_feasibility.csv`.

**What it is** (DECISIONS.md's D-599 row, fixed before this code was built): how often a window of a given length, run
as P-16's confirmation would be run, passes the gate -- so the data bought for P-16's single confirmation is long enough
to be informative. P-10 failed its confirmation on the width of a one-year bound, set by the number of 21-session
blocks (D-451).

**The windows** (`windows`, `plan`): consecutive, non-overlapping blocks of 63, 126, 189 and 252 walked development
sessions (three, six, nine and twelve months) of P-16's day list (`rc_stop_walkforward.walk_stop`'s, the list every
P-16 identity runs on), each length started from the first development session; a final partial block is dropped. No
day after 2026-07-16 is admitted (`window_problems` refuses; the bar store's window guard refuses the read first).

**Each window** (`rc_stop_walkforward.cell` / `span_row` on the window's sessions alone): the window's own mark cutoff,
its own one-sided 0.05 bound by `a3_brk30.check_bounds` (pooled over the window's 21-session blocks), v12's no-closure
table, P-14's protocol, five Topstep seats, campaign seed 20261131, 200 paths. A window whose bound is undefined at an R
its trades carry -- fewer than two 21-session blocks holding a trade at that R (`bound_short`) -- is recorded
`too_short` and not run; one whose cutoff admits no mark is recorded `no_mark` and not run. Neither passes.

**The pass rule** (`pass_rule`): growth on the required bankroll at the bound above zero AND every offered R resolves in
the window (`atlas_a3.resolution` on the table's offered R: at most 5 % unresolved overall and in the window's worst
calendar year, D-212).

**Readings per length** (`aggregate`): the count and share passing; the median, smallest and largest growth at the
bound and at the point; the median shift the bound applies (e minus its bound at the fresh Combine's 1.5R and the
fresh funded 3R, `rc_stop_fine.edge_row` on the bounds the window's run shifted by); the median required bankroll.

**What it is not** (D-599 (5)): the windows are P-16's own development history, from which its cell was chosen, so
the shares are optimistic -- a lower bound on the window length needed, never a forecast of the confirmation.
"""
from __future__ import annotations

import hashlib
import math
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from propedge.research import rc_stop_fine as F
from propedge.research import resolved_coin as rc

DECISION = "D-599"
FAMILY_ID = f"{DECISION}:p16_confirm_feasibility"
RESULT = "p16_confirm_feasibility"
N_VARIANTS = 0                             # D-599: readings, 0 variants -- nothing is chosen
LENGTHS = (63, 126, 189, 252)              # three, six, nine and twelve months of sessions
STOP = 150                                 # P-16's 37.5 points
WINDOW = "all"
CELL = rc.reentry_cell_name(STOP, WINDOW)  # rc_s150_all
CAMPAIGN_SEED = 20261131
N_PATHS = 200                              # D-599 (2): fewer than the registered 500, stated
IDENT_PATHS = 500                          # D-599 (4)
DEV_FIRST = "2020-01-02"                   # the first development session
DEV_LAST = "2026-07-16"                    # the development window's end; nothing later is read
SPANS = {"early": ("2020-01-01", "2023-12-31"), "late": ("2024-01-01", "2026-07-16")}
BLOCK_DAYS = 21
MIN_BLOCKS = 2                             # `confirm_fv3.bound_at`: a bound needs two block means
OFFERED_R = (0.25, 1.0, 1.5, 2.0, 2.5, 3.0)
COMBINE_RR = 1.5                           # the fresh Combine's R
FUNDED_RR = 3.0                            # the fresh funded R
UNRESOLVED_MAX = 0.05                      # D-212
#: atlas_a3.yaml's eras (P-11's): reported beside each window (a window crossing them is where the pooled bound and
#: the full-window era rule can differ); never changes the window's bound
ERAS = ((2020, 2022), (2023, 2026))

RAN, TOO_SHORT, NO_MARK = "ran", "too_short", "no_mark"
FAIL_GROWTH = "growth on the required bankroll at the bound not above zero"
FAIL_RESOLUTION = "an offered R unresolved above 5 % overall or in the window's worst year (D-212)"

#: identity columns and tolerance: rc_stop_fine's
IDENT_COLS = F.IDENT_COLS
IDENT_ATOL = F.IDENT_ATOL
SCREEN_FILE = F.SCREEN_FILE                # rc_width_screen.csv
WALKFORWARD_FILE = F.WALKFORWARD_FILE      # rc_stop_walkforward.csv


def window_name(length: int, index: int) -> str:
    return f"{CELL}_w{int(length)}_{int(index):02d}"


# ------------------------------------------------------------------------------------------------ the declaration

#: DECISIONS.md's D-599 row (LF, the line itself): its sha256 and the phrases each constant rests on
DECLARATION_SHA256 = "724e9acc2cfb3e59101f42f8a3f999f3f39a7972acff81e546e9341656e8b6fa"
D599_WORDS = (
    "Declared before anything of it is read (EXPLORATORY, selects nothing)",
    f"consecutive, non-overlapping blocks of the development history ({DEV_FIRST} .. {DEV_LAST}; nothing later is "
    "read)",
    f"of {LENGTHS[0]}, {LENGTHS[1]}, {LENGTHS[2]} and {LENGTHS[3]} sessions (three, six, nine and twelve months), each "
    "started from the first development session; a final partial block is dropped",
    "P-16's frozen cell restricted to the window's sessions (`rc_stop_walkforward.cell` / `span_row`: the window's own "
    "mark cutoff, its own one-sided 0.05 bound from its own trade outcomes by the era rule, `a3_brk30.check_bounds`)",
    f"v12's no-closure table, P-14's protocol, five Topstep seats, campaign seed {CAMPAIGN_SEED}, **{N_PATHS} paths**",
    "the window passes when growth on the required bankroll at the bound is above zero and every offered R resolves "
    "in the window (D-212)",
    "the share of windows passing; the median, smallest and largest growth at the bound and at the point; the median "
    "shift the bound applies (the point minus the bound of `e` at the fresh Combine's and funded R); the median "
    "required bankroll",
    f"the span machinery on the whole development history at {IDENT_PATHS} paths reproduces `{SCREEN_FILE}`'s "
    f"{CELL} row, and on 2020-2023 and 2024-2026-07-16 `{WALKFORWARD_FILE}`'s span rows",
    "the shares are optimistic -- a lower bound on the window length needed, never a forecast of the confirmation",
    f"Writes `results/{RESULT}.csv` (EXPLORATORY; `{FAMILY_ID}`, readings, {N_VARIANTS} variants -- nothing is chosen)",
    "workers 1",
)


def declaration(path: Path | str | None = None) -> dict[str, Any]:
    """DECISIONS.md's D-599 row (LF line ends, the line itself) and its sha256 (`rc_stop_fine.declaration`'s way)."""
    p = Path(path) if path is not None else Path(__file__).resolve().parents[2] / "DECISIONS.md"
    text = p.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")
    rows = [line for line in text.split("\n") if line.startswith(f"| {DECISION} |")]
    row = rows[0] if len(rows) == 1 else ""
    return {"path": str(p), "rows": len(rows), "row": row, "sha256": hashlib.sha256(row.encode("utf-8")).hexdigest()}


def declaration_problems(decl: Mapping[str, Any]) -> list[str]:
    """Every way this module's constants differ from D-599's row and from the screens it reuses (empty: they agree)."""
    out = []
    if int(decl["rows"]) != 1:
        out.append(f"DECISIONS.md holds {decl['rows']} {DECISION} rows, not one")
    if str(decl["sha256"]) != DECLARATION_SHA256:
        out.append(f"the {DECISION} row's sha256 is {str(decl['sha256'])[:16]}, not the pinned "
                   f"{DECLARATION_SHA256[:16]}")
    row = re.sub(r"\s+", " ", str(decl["row"]))
    out += [f"{DECISION} does not say {w!r}" for w in D599_WORDS if w not in row]
    shared = {"campaign seed": (CAMPAIGN_SEED, F.CAMPAIGN_SEED), "identity paths": (IDENT_PATHS, F.N_PATHS),
              "stop": (STOP, F.REFERENCE_STOP), "cell": (CELL, F.REF_CELL), "window": (WINDOW, F.WINDOW),
              "spans": ({k: tuple(v) for k, v in SPANS.items()}, {k: tuple(v) for k, v in F.SPANS.items()}),
              "unresolved line": (UNRESOLVED_MAX, F.UNRESOLVED_MAX)}
    out += [f"{k}: this build's {v[0]!r} against D-594's build's {v[1]!r}" for k, v in shared.items() if v[0] != v[1]]
    if any(int(n) % BLOCK_DAYS for n in LENGTHS):
        out.append(f"a window length in {LENGTHS} is not a whole number of {BLOCK_DAYS}-session blocks")
    return out


# ------------------------------------------------------------------------------------------------ the windows


def window_problems(days: Sequence[str]) -> list[str]:
    """P-16's day list must be sorted, unique and inside the development window (nothing after 2026-07-16)."""
    d = [str(x) for x in days]
    out = []
    if not d:
        return ["no development sessions"]
    if d != sorted(set(d)):
        out.append("the day list is not sorted and unique")
    if max(d) > DEV_LAST:
        out.append(f"a session after {DEV_LAST} ({max(d)}): nothing later may be read (D-599 (1))")
    if min(d) < SPANS["early"][0]:
        out.append(f"a session before the development window ({min(d)})")
    return out


def windows(days: Sequence[str], length: int) -> list[dict[str, Any]]:
    """Consecutive, non-overlapping blocks of `length` sessions from the first session; a final partial block dropped."""
    bad = window_problems(days)
    if bad:
        raise ValueError("; ".join(bad))
    d = [str(x) for x in days]
    n = int(length)
    if n <= 0:
        raise ValueError(f"a window length must be positive, not {length!r}")
    out = []
    for i in range(len(d) // n):
        w = d[i * n:(i + 1) * n]
        out.append({"length": n, "index": i, "window": window_name(n, i), "first": w[0], "last": w[-1],
                    "sessions": len(w), "blocks": len(w) // BLOCK_DAYS, "crosses_eras": crosses_eras(w),
                    "days": w})
    return out


def plan(days: Sequence[str], lengths: Sequence[int] = LENGTHS) -> list[dict[str, Any]]:
    """Every length's windows, in length order."""
    return [w for n in lengths for w in windows(days, n)]


def dropped(days: Sequence[str], length: int) -> int:
    """The sessions in the final partial block."""
    return len(days) % int(length)


def crosses_eras(days: Sequence[str], eras: Sequence[tuple[int, int]] = ERAS) -> bool:
    """Whether a window holds sessions of more than one of P-11's eras (beside; the window's bound is pooled)."""
    ys = {int(str(x)[:4]) for x in days}
    hit = {i for i, (lo, hi) in enumerate(eras) for y in ys if lo <= y <= hi}
    return len(hit) > 1


# ------------------------------------------------------------------------------------------------ the rule


def bound_short(stats: Mapping[float, Mapping[str, Any]]) -> str:
    """Why a window is too short for its bound ("" when it is not): an R its trades carry whose pooled bound is
    undefined -- fewer than `MIN_BLOCKS` 21-session blocks hold a trade at that R (`confirm_fv3.edge_stats`' n and
    blocks; an R carried by no trade is not shifted, `a3_brk30.check_bounds`' rule, and is not a shortness)."""
    short = []
    for R in sorted(stats, key=float):
        s = stats[R]
        n, b = int(s["n"]), int(s["blocks"])
        lb = float(s["lb"]) if s.get("lb") is not None else float("nan")
        if n > 0 and (b < MIN_BLOCKS or not math.isfinite(lb)):
            short.append(f"{float(R):g}R ({b} block(s) with a trade)")
    return ("the bound is undefined at " + ", ".join(short) + f": fewer than {MIN_BLOCKS} {BLOCK_DAYS}-session blocks "
            "hold a trade") if short else ""


def pass_rule(growth_at_bound: float, every_offered_r_resolves: bool) -> tuple[bool, str]:
    """D-599 (2): (passes, why it fails -- "" when it passes)."""
    g = float(growth_at_bound)
    why = []
    if not (math.isfinite(g) and g > 0):
        why.append(FAIL_GROWTH)
    if not bool(every_offered_r_resolves):
        why.append(FAIL_RESOLUTION)
    return (not why), "; ".join(why)


def shift_row(e_by: Mapping[float, float], lb_by: Mapping[float, float]) -> dict[str, Any]:
    """e and its bound at the fresh Combine's and funded R (`rc_stop_fine.edge_row`) and the shift the bound applies:
    e minus its bound at each."""
    out = F.edge_row(e_by, lb_by, COMBINE_RR, FUNDED_RR)
    for tag in ("combine", "funded"):
        out[f"shift_at_fresh_{tag}_r"] = float(out[f"e_at_fresh_{tag}_r"]) - float(out[f"lb_at_fresh_{tag}_r"])
    return out


# ------------------------------------------------------------------------------------------------ the readings


def _vals(rows: Sequence[Mapping[str, Any]], col: str) -> np.ndarray:
    v = np.array([float(r.get(col, np.nan)) for r in rows], dtype=float)
    return v[~np.isnan(v)]


def _med(v: np.ndarray) -> float:
    return float(np.median(v)) if len(v) else float("nan")


def aggregate(rows: Sequence[Mapping[str, Any]], lengths: Sequence[int] = LENGTHS,
              n_sessions: int | None = None) -> list[dict[str, Any]]:
    """One row per length from the window rows (`status`, `passes`, `fail_reason`, the growths, the shifts and the
    required bankroll). The share passing is over every window of the length (a `too_short` or `no_mark` window does
    not pass) and, beside, over the windows run; the medians, smallest and largest are over the windows run."""
    out = []
    for n in lengths:
        w = [r for r in rows if int(r["length"]) == int(n)]
        ran = [r for r in w if r["status"] == RAN]
        passing = [r for r in ran if bool(r["passes"])]
        gb, gp = _vals(ran, "growth_on_required"), _vals(ran, "growth_on_required_point")
        row = {"section": "length", "length": int(n), "windows": len(w), "ran": len(ran),
               "too_short": sum(r["status"] == TOO_SHORT for r in w), "no_mark": sum(r["status"] == NO_MARK for r in w),
               "passing": len(passing), "share_passing": len(passing) / len(w) if w else float("nan"),
               "share_passing_of_ran": len(passing) / len(ran) if ran else float("nan"),
               "failing_growth": sum(FAIL_GROWTH in str(r.get("fail_reason", "")) for r in ran),
               "failing_resolution": sum(FAIL_RESOLUTION in str(r.get("fail_reason", "")) for r in ran),
               "growth_at_bound_median": _med(gb), "growth_at_bound_min": float(gb.min()) if len(gb) else float("nan"),
               "growth_at_bound_max": float(gb.max()) if len(gb) else float("nan"),
               "growth_at_point_median": _med(gp), "growth_at_point_min": float(gp.min()) if len(gp) else float("nan"),
               "growth_at_point_max": float(gp.max()) if len(gp) else float("nan"),
               "shift_at_fresh_combine_r_median": _med(_vals(ran, "shift_at_fresh_combine_r")),
               "shift_at_fresh_funded_r_median": _med(_vals(ran, "shift_at_fresh_funded_r")),
               "required_p90_median": _med(_vals(ran, "required_p90")),
               "sessions_used": sum(int(r["sessions"]) for r in w)}
        if n_sessions is not None:
            row["sessions_dropped"] = int(n_sessions) - row["sessions_used"]
        out.append(row)
    return out


def row_problems(mine: Mapping[str, Any], want: Mapping[str, Any], what: str = "the file") -> list[str]:
    """A reading against a written row on the identity columns (`rc_stop_fine.row_problems`)."""
    return F.row_problems(mine, want, IDENT_COLS, IDENT_ATOL, what)


__all__ = ["DECISION", "FAMILY_ID", "RESULT", "N_VARIANTS", "LENGTHS", "STOP", "WINDOW", "CELL", "CAMPAIGN_SEED",
           "N_PATHS", "IDENT_PATHS", "DEV_FIRST", "DEV_LAST", "SPANS", "BLOCK_DAYS", "MIN_BLOCKS", "OFFERED_R",
           "COMBINE_RR", "FUNDED_RR", "UNRESOLVED_MAX", "ERAS", "RAN", "TOO_SHORT", "NO_MARK", "FAIL_GROWTH",
           "FAIL_RESOLUTION", "IDENT_COLS", "IDENT_ATOL", "SCREEN_FILE", "WALKFORWARD_FILE", "window_name",
           "DECLARATION_SHA256", "D599_WORDS", "declaration", "declaration_problems", "window_problems", "windows",
           "plan", "dropped", "crosses_eras", "bound_short", "pass_rule", "shift_row", "aggregate", "row_problems"]
