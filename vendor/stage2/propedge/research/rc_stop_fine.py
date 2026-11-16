"""EXPLORATORY (D-594): a finer stop-width screen of P-16's coin -- the pure parts. `scripts/rc_stop_fine.py` walks the
bars, builds the cells and writes `results/rc_stop_fine.csv`.

**What it is** (DECISIONS.md's D-594 row, fixed before this code was built): P-16's cell (`rc_s150_all`, the news-safe
all-day coin at 37.5 points) with only the stop changed -- 40, 43.75 and 47.5 points (160, 175 and 190 MNQ ticks), the
coin's one structural choice, between D-542's 37.5-point pick and the 50-point stop that grew more but failed
resolution. Each cell is P-16's in everything else: every five-minute mark, the coin seeded 20261102 per (date, mark),
re-entry when flat, the walk at the cell's stop (`atlas_a3.walk_minutes` through `rc_stop_walkforward.walk_stop`, as
`rc_width_screen.build` walks), the mark-resolution cutoff (D-525 (4)) at the cell's stop, D-533's news-safe cut, v12's
no-closure table sized by the engine in whole micros at the stop (`resolved_coin.width_sizing` reads it, D-538 (2)),
P-14's protocol and five Topstep seats (`rc_screen.Runner`).

**The guards, in D-594's order** (`GUARDS`; the first failure ends the cell and the rest are `not_run`):
(a) every offered R resolves -- at most 5 % unresolved overall and in the worst year (`atlas_a3.resolution` on the
table's offered R, D-212); (b) the paired growth on the required bankroll at the bound beats the 150-tick cell's by more
than 0.05 (campaign seed 20261131, 500 paths); (c) on 2020-2023 and on 2024-01-01 .. 2026-07-16 alone, each span's own
cutoff and bound (D-551's design, `rc_stop_walkforward`), not below the 150-tick cell; (d) at least 40 of 50 coin
sequences (seeds 20261600 + i, 200 paths) beat the 150-tick cell under the same sequence. Each check is
`s1_sided_coin.verdict`'s own (D-578 (2)'s four, independent of each other), so the guard just run is read from it
alone; with all four run, the staged verdict equals that verdict.

**Beside, deciding nothing** (D-594 (3)): the funded leg capped to the 150-tick cell's dollars (D-542's diagnostic:
`resolved_coin.funded_cap_rule` at 150 / stop, `funded_cap_problems`), e and its bound at the fresh Combine's and the
fresh funded R (`edge_row`), the cost in R by exit kind (`exit_cost_r`, `cost_by_kind`), the trades taken a session,
D-518's journey and D-509's four slice lines against FV3-C.
"""
from __future__ import annotations

import hashlib
import math
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from propedge.research import resolved_coin as rc
from propedge.research import s1_sided_coin as S1

DECISION = "D-594"
FAMILY_ID = f"{DECISION}:rc_stop_fine"
RESULT = "rc_stop_fine"
STOPS = (160, 175, 190)                    # D-594: 40, 43.75 and 47.5 points
REFERENCE_STOP = 150                       # P-16's 37.5 points
N_VARIANTS = len(STOPS)                    # D-594: 3 variants (the reference is P-16, not a variant)
WINDOW = "all"
COIN_SEED = rc.COIN_SEED                   # 20261102
CAMPAIGN_SEED = 20261131                   # the screens' (D-522 (3)) and D-578's paired run
N_PATHS = 500
COIN_SEEDS = tuple(20261600 + i for i in range(50))   # D-578 (c)
G2_PATHS = 200
G2_WINS = 40
MARGIN = 0.05
SPANS = {"early": ("2020-01-01", "2023-12-31"), "late": ("2024-01-01", "2026-07-16")}
UNRESOLVED_MAX = 0.05                      # D-212
NOT_RUN = "not_run"

#: D-594's order; each guard read from `s1_sided_coin.verdict`'s check of the same meaning
GUARDS = ("a_resolution", "b_paired", "c_spans", "d_coins")
GUARD_CHECK = {"a_resolution": "b_every_offered_r_resolves", "b_paired": "a_paired_beats_by_margin",
               "c_spans": "d_not_below_on_either_span", "d_coins": "c_wins_coin_sequences"}

#: the reference's identities: `rc_width_screen.csv`'s row (D-594 (4)) and its span rows (D-551's file; rc150_routing's
#: R0 rows carry the same values), compared on these columns to this tolerance
IDENT_COLS = ("growth_on_required", "growth_on_required_point", "required_p90")
IDENT_ATOL = 1e-9
SCREEN_FILE = "rc_width_screen.csv"
WALKFORWARD_FILE = "rc_stop_walkforward.csv"
ROUTING_FILE = "rc150_routing.csv"
ROUTING_REF = "R0_longest_waiting"


def cell_name(stop: int) -> str:
    """The cell's name in the screens' form (`rc_s{stop}_all`)."""
    return rc.reentry_cell_name(int(stop), WINDOW)


REF_CELL = cell_name(REFERENCE_STOP)       # rc_s150_all


def grid() -> list[tuple[str, int]]:
    """The screen's cells (name, stop ticks), the reference excluded."""
    return [(cell_name(s), int(s)) for s in STOPS]


# ------------------------------------------------------------------------------------------------ the declaration

#: DECISIONS.md's D-594 row (LF, the line itself): its sha256 and the phrases each constant rests on
DECLARATION_SHA256 = "770449a75f39609f91f0b1513ac07ff6fa64f4beba11a055fcce163c27578316"
D594_WORDS = (
    "Declared before anything of it is read (EXPLORATORY)",
    "40, 43.75 and 47.5 points (160, 175 and 190 MNQ ticks)",
    f"the news-safe all-day coin, every five-minute mark, coin seed {COIN_SEED}, re-entry when flat",
    "the walk at the cell's stop (`atlas_a3.walk_minutes` as `rc_width_screen.build`)",
    "the mark-resolution cutoff (D-525 (4)) at the cell's stop",
    "v12's no-closure table sized at the stop in whole micros (`resolved_coin.width_sizing`, as D-538)",
    "P-14's protocol, five Topstep seats",
    "Guards, in order, the first failure ending the cell",
    "(a) every offered R resolves (D-212, at most 5 % unresolved overall and in the worst year)",
    f"(b) the paired growth on the required bankroll at the bound beats P-16's (the {REFERENCE_STOP}-tick cell, same "
    f"seeds: campaign {CAMPAIGN_SEED}, {N_PATHS} paths) by more than {MARGIN:g}",
    "(c) within history: on 2020-2023 and on 2024-2026-07-16 alone (each span's own bound, the same seeds) the cell is "
    f"not below the {REFERENCE_STOP}-tick cell",
    f"(d) at least {G2_WINS} of {len(COIN_SEEDS)} coin sequences (seeds {COIN_SEEDS[0]} + i, {G2_PATHS} paths) beat "
    f"the {REFERENCE_STOP}-tick cell under the same sequence",
    f"each cell with its funded leg capped to the {REFERENCE_STOP}-tick cell's dollars (D-542's diagnostic, "
    "`resolved_coin.funded_cap_rule`)",
    "e and its bound at the fresh Combine's and funded R, cost in R by exit kind, trades a session, D-518's journey, "
    "the four slice lines against FV3-C",
    f"the {REFERENCE_STOP}-tick cell equals P-16's trades by content hash and its paired row `{SCREEN_FILE}`'s "
    f"{REF_CELL}",
    f"Writes `results/{RESULT}.csv` (EXPLORATORY; `{FAMILY_ID}`, {N_VARIANTS} variants)",
    "workers 1",
)


def declaration(path: Path | str | None = None) -> dict[str, Any]:
    """DECISIONS.md's D-594 row (LF line ends, the line itself) and its sha256 (`s3_latency.declaration`'s way)."""
    p = Path(path) if path is not None else Path(__file__).resolve().parents[2] / "DECISIONS.md"
    text = p.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")
    rows = [line for line in text.split("\n") if line.startswith(f"| {DECISION} |")]
    row = rows[0] if len(rows) == 1 else ""
    return {"path": str(p), "rows": len(rows), "row": row, "sha256": hashlib.sha256(row.encode("utf-8")).hexdigest()}


def declaration_problems(decl: Mapping[str, Any]) -> list[str]:
    """Every way this module's constants differ from D-594's row (an empty list: they agree)."""
    out = []
    if int(decl["rows"]) != 1:
        out.append(f"DECISIONS.md holds {decl['rows']} {DECISION} rows, not one")
    if str(decl["sha256"]) != DECLARATION_SHA256:
        out.append(f"the {DECISION} row's sha256 is {str(decl['sha256'])[:16]}, not the pinned "
                   f"{DECLARATION_SHA256[:16]}")
    row = re.sub(r"\s+", " ", str(decl["row"]))
    out += [f"{DECISION} does not say {w!r}" for w in D594_WORDS if w not in row]
    # the shared guard constants are D-578's as S1 carries them
    shared = {"campaign seed": (CAMPAIGN_SEED, S1.CAMPAIGN_SEED), "paths": (N_PATHS, S1.N_PATHS),
              "coin seeds": (COIN_SEEDS, tuple(S1.COIN_SEEDS)), "g2 paths": (G2_PATHS, S1.G2_PATHS),
              "g2 wins": (G2_WINS, S1.G2_WINS), "margin": (MARGIN, S1.MARGIN),
              "spans": ({k: tuple(v) for k, v in SPANS.items()}, {k: tuple(v) for k, v in S1.SPANS.items()}),
              "reference stop": (REFERENCE_STOP, S1.STOP_TICKS)}
    out += [f"{k}: this build's {v[0]!r} against D-578's {v[1]!r}" for k, v in shared.items() if v[0] != v[1]]
    if REFERENCE_STOP not in rc.WIDTH_STOPS:
        out.append(f"the reference stop {REFERENCE_STOP} is not one of D-538's {rc.WIDTH_STOPS}")
    if any(not REFERENCE_STOP < s < max(rc.WIDTH_STOPS) for s in STOPS):
        out.append(f"the cells {STOPS} are not between 37.5 and 50 points")
    return out


# ------------------------------------------------------------------------------------------------ the cost in R


def exit_cost_r(stop_ticks: int, fee: float, entry_ticks: float, tick_value: float) -> dict[str, float]:
    """The round-trip cost in R of one trade at `stop_ticks` by exit kind (`resolved_coin.KIND_CODE`: s stop, t target,
    f flatten, b breakeven) -- `resolved_coin.cell_trades`' own arithmetic: (a tick at entry + the fee a micro-equivalent
    pays + the exit's ticks by kind) over the stop's dollars per micro. The fee is `atlas_a3.fee_by_stop` at the stop."""
    from propedge.research.fv3_rung_walk import EXIT_TICKS

    S, td = float(stop_ticks), float(tick_value)
    return {rc.KIND_CODE[int(k)]: (float(entry_ticks) * td + float(fee) + float(EXIT_TICKS[int(k)]) * td) / (S * td)
            for k in sorted(rc.KIND_CODE)}


def cost_by_kind(t: pd.DataFrame, R: float) -> list[dict[str, Any]]:
    """The cell's trades at one offered R by exit kind: count, share, the mean cost in R, gross and net."""
    o = t[f"o_{float(R):g}"].astype(str)
    m = o != ""
    out = []
    n = int(m.sum())
    for k in sorted(set(o[m])):
        s = m & (o == k)
        out.append({"R": float(R), "exit_kind": k, "trades": int(s.sum()), "share": float(s.sum()) / n if n else np.nan,
                    "mean_cost_r": float(t.loc[s, f"c_{float(R):g}"].mean()),
                    "mean_gross_r": float(t.loc[s, f"g_{float(R):g}"].mean()),
                    "mean_net_r": float(t.loc[s, f"r_{float(R):g}"].mean())})
    out.append({"R": float(R), "exit_kind": "all", "trades": n, "share": 1.0 if n else np.nan,
                "mean_cost_r": float(t.loc[m, f"c_{float(R):g}"].mean()),
                "mean_gross_r": float(t.loc[m, f"g_{float(R):g}"].mean()),
                "mean_net_r": float(t.loc[m, f"r_{float(R):g}"].mean())})
    return out


# ------------------------------------------------------------------------------------------------ e and its bound

#: the research criterion (propsim D-47), reported beside, never the gate (D-145)
OLD_GATE_E = 0.10
OLD_GATE_LB = 0.05


def edge_row(e_by: Mapping[float, float], lb_by: Mapping[float, float], combine_rr: float,
             funded_rr: float) -> dict[str, Any]:
    """e and its bound at the fresh Combine's R and the fresh funded R (the era rule's reading the engine shifts by),
    with whether the old research criterion would be met at each."""
    out: dict[str, Any] = {"combine_rr": float(combine_rr), "funded_rr": float(funded_rr)}
    for tag, R in (("combine", combine_rr), ("funded", funded_rr)):
        e, lb = float(e_by.get(float(R), np.nan)), float(lb_by.get(float(R), np.nan))
        out[f"e_at_fresh_{tag}_r"] = e
        out[f"lb_at_fresh_{tag}_r"] = lb
        out[f"old_gate_met_at_fresh_{tag}_r"] = bool(np.isfinite(e) and np.isfinite(lb) and e >= OLD_GATE_E
                                                     and lb >= OLD_GATE_LB)
    return out


# ------------------------------------------------------------------------------------------------ the funded cap


def funded_cap_problems(fs: pd.DataFrame) -> list[str]:
    """D-542's diagnostic at a finer stop (`resolved_coin.funded_cap_sizing(rule, leaves, 150, stop, ...)`): every
    funded state whose micros the cap binds at the reference stop -- the confound D-539 (2) named -- realises at most its
    reference dollars under the scaled cap, and no state is left unsized. States the cap does not bind at the reference
    are sized as the engine sizes them (D-542: "every other state as the engine sizes it"); their whole-micro rounding
    may realise a few dollars more or less than at 37.5 points, which `funded_cap_rounding` reports."""
    out = []
    bind = fs["micros_ref"].astype(int) >= fs["cap_ref"].astype(int)
    above = fs[bind & (fs["realised_capped"] > fs["realised_ref"] + 1e-9)]
    for _, r in above.iterrows():
        out.append(f"{r['leaf']} at tier {r['tier_balance']:g}: ${r['realised_capped']:g} under the cap against "
                   f"${r['realised_ref']:g} at {int(r['ref_stop_ticks'])} ticks")
    if bool(fs["cannot_size_capped"].astype(bool).any()):
        out.append(f"{int(fs['cannot_size_capped'].astype(bool).sum())} funded state(s) cannot be sized under the cap")
    if not bool(bind.any()):
        out.append("no funded state's cap binds at the reference stop: nothing for D-542's diagnostic to hold")
    return out


def funded_cap_rounding(fs: pd.DataFrame) -> dict[str, Any]:
    """Beside the cap: the funded states the cap does not bind at the reference that realise more (or less) dollars at
    the stop than at the reference, from whole micros alone."""
    bind = fs["micros_ref"].astype(int) >= fs["cap_ref"].astype(int)
    free = fs[~bind]
    d = free["realised_capped"].astype(float) - free["realised_ref"].astype(float)
    return {"states": int(len(fs)), "states_cap_binds_at_reference": int(bind.sum()),
            "states_changed_by_cap": int(fs["cap_changes"].astype(bool).sum()),
            "free_states_above_reference": int((d > 1e-9).sum()), "free_states_below_reference": int((d < -1e-9).sum()),
            "free_max_excess_dollars": float(d.max()) if len(d) else 0.0,
            "free_max_shortfall_dollars": float(-d.min()) if len(d) else 0.0}


# ------------------------------------------------------------------------------------------------ the guards


def verdict(cell: str, g1_growth: float, ref_growth: float, resolves: bool, g2_row: Mapping[str, Any] | None,
            span_growth: Mapping[str, float], span_ref: Mapping[str, float]) -> dict[str, Any]:
    """D-578 (2)'s four checks for one cell against the 150-tick cell (`s1_sided_coin.verdict`)."""
    return S1.verdict(cell, g1_growth, ref_growth, resolves, g2_row, span_growth, span_ref)


def g2_summary(rows: Sequence[Mapping[str, Any]], cell: str) -> dict[str, Any]:
    """Guard (d): on how many coin sequences the cell grows more at the bound than the 150-tick cell under the same
    sequence (`s1_sided_coin.g2_summary`; rows hold coin_seed, arm, growth_on_required)."""
    return S1.g2_summary(rows, [cell], REF_CELL)[0]


def next_guard(done: Sequence[Mapping[str, Any]]) -> str | None:
    """The guard to run next given those run (in D-594's order), or None: every guard ran, or one failed."""
    for i, g in enumerate(done):
        if i >= len(GUARDS) or g["guard"] != GUARDS[i]:
            raise ValueError(f"guard {i + 1} is {GUARDS[i] if i < len(GUARDS) else None!r}, not {g['guard']!r}")
        if not bool(g["passes"]):
            return None
    return GUARDS[len(done)] if len(done) < len(GUARDS) else None


def staged(done: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    """The guards that count: up to and including the first failure (a --check runs every guard's machinery)."""
    upto = next((i + 1 for i, g in enumerate(done) if not bool(g["passes"])), len(done))
    return list(done[:upto])


def guard_check(guard: str, v: Mapping[str, Any]) -> bool:
    """One guard read from `verdict`'s output."""
    return bool(v[GUARD_CHECK[guard]])


def guard_rows(cell: str, done: Sequence[Mapping[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """(one row per guard in D-594's order -- pass, fail or not_run -- and the cell's verdict row). The first failure
    ends the cell; a guard after it is not_run; the cell is a candidate only with all four passing."""
    if next_guard(done) is not None:
        raise ValueError(f"guard {next_guard(done)!r} is still to run")
    status = {}
    rows = []
    for i, g in enumerate(GUARDS):
        r = done[i] if i < len(done) else None
        status[g] = NOT_RUN if r is None else ("pass" if bool(r["passes"]) else "fail")
        rows.append({"section": "guard", "cell": cell, "order": i + 1, "guard": g, "check": GUARD_CHECK[g],
                     "status": status[g], **({k: v for k, v in r.items() if k not in ("guard", "passes")} if r else {})})
    first_fail = next((g for g in GUARDS if status[g] == "fail"), "")
    v = {"section": "verdict", "cell": cell, **{g: status[g] for g in GUARDS}, "first_failing_guard": first_fail,
         "candidate": bool(all(status[g] == "pass" for g in GUARDS))}
    return rows, v


def verdict_agrees(staged_verdict: Mapping[str, Any], v: Mapping[str, Any]) -> bool:
    """With all four guards run, the staged verdict is `verdict`'s (every check and the candidate flag)."""
    return all((staged_verdict[g] == "pass") == bool(v[GUARD_CHECK[g]]) for g in GUARDS) and \
        bool(staged_verdict["candidate"]) == bool(v["candidate"])


# ------------------------------------------------------------------------------------------------ identities


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


__all__ = ["DECISION", "FAMILY_ID", "RESULT", "STOPS", "REFERENCE_STOP", "N_VARIANTS", "WINDOW", "COIN_SEED",
           "CAMPAIGN_SEED", "N_PATHS", "COIN_SEEDS", "G2_PATHS", "G2_WINS", "MARGIN", "SPANS", "UNRESOLVED_MAX",
           "NOT_RUN", "GUARDS", "GUARD_CHECK", "IDENT_COLS", "IDENT_ATOL", "SCREEN_FILE", "WALKFORWARD_FILE",
           "ROUTING_FILE", "ROUTING_REF", "REF_CELL", "cell_name", "grid", "DECLARATION_SHA256", "D594_WORDS",
           "declaration", "declaration_problems", "exit_cost_r", "cost_by_kind", "OLD_GATE_E", "OLD_GATE_LB",
           "edge_row", "funded_cap_problems", "funded_cap_rounding", "verdict", "g2_summary", "next_guard", "staged",
           "guard_check", "guard_rows", "verdict_agrees", "row_problems"]
