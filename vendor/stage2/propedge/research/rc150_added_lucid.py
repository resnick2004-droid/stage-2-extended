"""EXPLORATORY (D-593): Lucid seats ADDED to P-16's five Topstep seats -- the pure parts. `scripts/rc150_added_lucid.py`
builds P-16's cell, runs the cells through `hypo_hedge.run_joint` (D-575's machinery, `scripts/rc150_firm_split.py`)
and writes `results/rc150_added_lucid.csv`.

**What it is** (DECISIONS.md's D-593 row, fixed before this code was built): Topstep allows five funded accounts, so
more seats need a second firm; an added Lucid seat replaces nothing and brings a second simultaneous position (one per
firm, D-429). The grid (`CELLS`): 5 + 0 (P-16's own call, the reference), 5 + 1, 5 + 2, 5 + 3 and 5 + 5 -- firm 0
Topstep's five seats, firm 1 Lucid's k -- unhedged only. Everything else is D-575's Lucid screen: P-16's trades
`rc_s150_all`, v12's no-closure table on both firms, P-14's protocol per firm, one position at a time per firm with
D-429's gap, one pooled wallet (D-206), each firm's purchase budget floor(20 x seats / 5) in 21 trading days
(`budget_for`), the unhedged deal of `hypo_hedge.run_joint`, Lucid's verified rules and prices with its two unpriced fees
at zero (`lucid_upper_bound`), the household rule's conservative reading, campaign seed 20261131, coin seed 20261102,
500 paths, each cell's zero-edge twin.

**Lucid's household caps** (`check_caps`): 5 funded, 10 evaluations, 10 accounts in total (`lucid_terms`); a firm's k
seats hold at most k accounts of any kind at once (`hypo_hedge.with_seats`: concurrent accounts, concurrent evaluations
and total accounts all k), so a cell is inside the caps iff k <= min(5, 10, 10); a cell above them is refused.

**The rule** (`verdict`, D-593 (4)): a cell other than 5 + 0 is a candidate only if (a) its growth on the required
bankroll at the bound exceeds 5 + 0's by more than `MARGIN` (0.05); (b) the cell's trades resolve every offered R (D-212;
one property of P-16's trades, the same for every cell, read as `rc150_routing` reads it); (c) on each span alone
(`SPANS`, D-578 (2)'s) its growth at the bound is not below 5 + 0's on that span (>=). Every reading is an upper bound
on Lucid's two unpriced fees (`LUCID_LABEL`).
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

DECISION = "D-593"
RESULT = "rc150_added_lucid"
FAMILY_ID = f"{DECISION}:rc150_added_lucid"
SCRIPT = "scripts/rc150_added_lucid.py"
UNHEDGED = "unhedged"                      # hypo_hedge.UNHEDGED (checked in the tests)
#: (cell, seats per firm in firm order: Topstep's, then Lucid's) -- D-593 (1)
CELLS: tuple[tuple[str, tuple[int, ...]], ...] = (
    ("5+0", (5,)),
    ("5+1", (5, 1)),
    ("5+2", (5, 2)),
    ("5+3", (5, 3)),
    ("5+5", (5, 5)),
)
REFERENCE = "5+0"
N_VARIANTS = 4                             # the four added-seat cells; the reference is P-16's own call
CAMPAIGN_SEED = 20261131
COIN_SEED = 20261102
N_PATHS = 500
MARGIN = 0.05
FULL_SEATS, FULL_BUDGET, BUDGET_WINDOW = 5, 20, 21
TOPSTEP_SEATS = 5
#: D-578 (2)'s spans (`rc_stop_walkforward.SPANS`, `s3_event_kinds.SPANS`; checked in the tests)
SPANS = {"early": ("2020-01-01", "2023-12-31"), "late": ("2024-01-01", "2026-07-16")}
SHIFTS = ("point", "lower_bound")
LUCID_LABEL = "lucid_upper_bound"
#: Lucid's household caps as D-575 verified them (`propedge.contract.lucid.lucid_terms`; checked against it)
LUCID_CAPS = {"max_funded": 5, "eval_count_limit": 10, "max_total_accounts": 10}
READING = ("EXPLORATORY (D-593): Lucid seats added to P-16's five Topstep seats (5+1, 5+2, 5+3, 5+5) against P-16's own "
           "call (5+0); Lucid's verified contract with its funded_monthly_fee and payout_fee uncharged: every Lucid "
           "figure is an upper bound on them; beside the verdicts, never a gate")


def budget_for(seats: int) -> tuple[int, int]:
    """P-14's budget (20 purchases and resets in 21 trading days at five seats) scaled to a firm's seats, floored --
    `rc150_firm_split.budget_for`'s rule (checked equal in the tests)."""
    s = int(seats)
    if s < 1:
        raise ValueError(f"a firm has at least one seat, got {seats!r}")
    return (FULL_BUDGET * s // FULL_SEATS, BUDGET_WINDOW)


def lucid_seat_limit(caps: Mapping[str, int] = LUCID_CAPS) -> int:
    """The most Lucid seats a cell may hold: a firm's k seats hold at most k funded accounts, k evaluations and k
    accounts in all at once, so k is bounded by the smallest of the three caps."""
    return int(min(int(caps["max_funded"]), int(caps["eval_count_limit"]), int(caps["max_total_accounts"])))


def check_caps(cells: Sequence[tuple[str, tuple[int, ...]]] = CELLS, caps: Mapping[str, int] = LUCID_CAPS) -> None:
    """Refuse (ValueError) a cell outside the grid's shape or above Lucid's household caps: firm 0 is Topstep's five
    seats, at most one further firm (Lucid), its seats at least 1 and at most `lucid_seat_limit`."""
    lim = lucid_seat_limit(caps)
    for name, seats in cells:
        seats = tuple(int(s) for s in seats)
        if not seats or seats[0] != TOPSTEP_SEATS:
            raise ValueError(f"{name}: firm 0 is Topstep's {TOPSTEP_SEATS} seats, got {seats!r}")
        if len(seats) > 2:
            raise ValueError(f"{name}: at most one added firm (Lucid), got {len(seats) - 1}")
        if len(seats) == 2 and not 1 <= seats[1] <= lim:
            raise ValueError(f"{name}: {seats[1]} Lucid seats; Lucid's household caps ({caps['max_funded']} funded, "
                             f"{caps['eval_count_limit']} evaluations, {caps['max_total_accounts']} in total) allow "
                             f"1 to {lim}")


def label_of(seats: Sequence[int]) -> str:
    """`lucid_upper_bound` on a cell with Lucid seats; the reference (Topstep alone) unlabelled."""
    return LUCID_LABEL if len(tuple(seats)) > 1 else ""


def seats_text(seats: Sequence[int]) -> str:
    return "+".join(str(int(s)) for s in seats)


# ------------------------------------------------------------------------------------------------ the declaration

#: DECISIONS.md's D-593 row (LF, the line itself): its sha256 and the phrases each constant rests on
DECLARATION_SHA256 = "82496f12f6a792ff7e2e4dcb7614225ee8deaf05eacaa0f7074cfd385b67bf31"
D593_WORDS = (
    "Declared before anything of it is read (EXPLORATORY)",
    "Lucid seats ADDED to P-16's five Topstep seats",
    "5 + 0 (P-16's own call, the reference), 5 + 1, 5 + 2, 5 + 3 and 5 + 5 (Topstep's five, then Lucid's k, inside "
    "Lucid's household caps)",
    "unhedged only (no hedge cell: nothing here is a hedge question)",
    "P-16's trades `rc_s150_all`, v12's no-closure table on both firms, P-14's protocol per firm",
    "one position at a time per firm with D-429's gap, one pooled wallet (D-206)",
    f"each firm's purchase budget floor({FULL_BUDGET} x seats / {FULL_SEATS}) in {BUDGET_WINDOW} trading days",
    "the unhedged deal of `hypo_hedge.run_joint` (each signal to one account at one firm)",
    f"Lucid's verified rules and prices with its two unpriced fees at zero (`{LUCID_LABEL}`)",
    "the household rule's conservative reading",
    f"campaign seed {CAMPAIGN_SEED}, coin seed {COIN_SEED}, {N_PATHS} paths, each cell's zero-edge twin",
    "growth on the required bankroll at the bound and the point, the required bankroll, trades taken a session per "
    "firm, payouts a month, the share of paths where the household rule closed every Lucid seat, D-518's journey on "
    "each cell",
    "the same cells on 2020-2023 and 2024-2026-07-16 alone (D-578 (2)'s spans) at the same seeds",
    f"a cell is a candidate only if it grows more at the bound than 5 + 0 by more than {MARGIN:g}, resolves every "
    "offered R, and is not below 5 + 0 on either span alone",
    "the result is an upper bound on Lucid's unpriced fees and says so",
    "5 + 0 equals P-16's engine call and `rc_width_screen.csv`'s rc_s150_all row",
    f"Writes `results/{RESULT}.csv` (EXPLORATORY; `{FAMILY_ID}`, {N_VARIANTS} variants)",
    "a clean checkout (D-474), workers 1",
)


def declaration(path: Path | str | None = None) -> dict[str, Any]:
    """DECISIONS.md's D-593 row (LF line ends, the line itself) and its sha256 (`s3_latency.declaration`'s way)."""
    p = Path(path) if path is not None else Path(__file__).resolve().parents[2] / "DECISIONS.md"
    text = p.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")
    rows = [line for line in text.split("\n") if line.startswith(f"| {DECISION} |")]
    row = rows[0] if len(rows) == 1 else ""
    return {"path": str(p), "rows": len(rows), "row": row, "sha256": hashlib.sha256(row.encode("utf-8")).hexdigest()}


def declaration_problems(decl: Mapping[str, Any]) -> list[str]:
    """Every way this module's constants differ from D-593's row (an empty list: they agree)."""
    out = []
    if int(decl["rows"]) != 1:
        out.append(f"DECISIONS.md holds {decl['rows']} {DECISION} rows, not one")
    if str(decl["sha256"]) != DECLARATION_SHA256:
        out.append(f"the {DECISION} row's sha256 is {str(decl['sha256'])[:16]}, not the pinned "
                   f"{DECLARATION_SHA256[:16]}")
    row = re.sub(r"\s+", " ", str(decl["row"]))
    out += [f"{DECISION} does not say {w!r}" for w in D593_WORDS if w not in row]
    grid = ", ".join(f"{s[0]} + {s[1] if len(s) > 1 else 0}" for _, s in CELLS)
    if grid != "5 + 0, 5 + 1, 5 + 2, 5 + 3, 5 + 5":
        out.append(f"the grid is {grid}, not D-593 (1)'s")
    if N_VARIANTS != len([c for c, _ in CELLS if c != REFERENCE]):
        out.append(f"{N_VARIANTS} variants declared, {len(CELLS) - 1} added-seat cells built")
    return out


# ------------------------------------------------------------------------------------------------ the rule


def verdict(growth: Mapping[str, float], span_growth: Mapping[str, Mapping[str, float]], resolves: bool,
            *, reference: str = REFERENCE, margin: float = MARGIN) -> list[dict[str, Any]]:
    """D-593 (4) per cell other than the reference: `growth` {cell: growth on the required bankroll at the bound, full
    history}; `span_growth` {span: {cell: growth at the bound on that span alone}}; `resolves` whether P-16's trades
    resolve every offered R. A missing or non-finite value fails its check."""
    ref = float(growth.get(reference, np.nan))
    out = []
    for name, seats in CELLS:
        if name == reference or name not in growth:
            continue
        diff = float(growth[name]) - ref
        span_diff = {s: float(span_growth.get(s, {}).get(name, np.nan)) - float(span_growth.get(s, {}).get(reference,
                                                                                                         np.nan))
                     for s in SPANS}
        checks = {"a_beats_reference_by_margin": bool(np.isfinite(diff) and diff > float(margin)),
                  "b_every_offered_r_resolves": bool(resolves),
                  "c_not_below_reference_on_either_span": bool(all(np.isfinite(v) and v >= 0.0
                                                                   for v in span_diff.values()))}
        out.append({"section": "verdict", "cell": name, "label": label_of(seats), "seats": seats_text(seats),
                    "growth_on_required": float(growth[name]), "reference_growth_on_required": ref,
                    "growth_minus_reference": diff, "margin": float(margin),
                    **{f"{s}_growth_minus_reference": v for s, v in span_diff.items()}, **checks,
                    "candidate": bool(all(checks.values())),
                    "note": "an upper bound on Lucid's two unpriced fees (funded_monthly_fee, payout_fee at zero)"})
    return out


__all__ = ["DECISION", "RESULT", "FAMILY_ID", "SCRIPT", "CELLS", "REFERENCE", "N_VARIANTS", "CAMPAIGN_SEED",
           "COIN_SEED", "N_PATHS", "MARGIN", "SPANS", "SHIFTS", "LUCID_LABEL", "LUCID_CAPS", "READING", "budget_for",
           "lucid_seat_limit", "check_caps", "label_of", "seats_text", "DECLARATION_SHA256", "D593_WORDS",
           "declaration", "declaration_problems", "verdict"]
