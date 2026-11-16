"""EXPLORATORY (D-621, program U): how a lever family is judged on the user's milestones -- pure functions on U1-format
start records (`propedge/research/user_journey.py`). No engine; the only draw is the seeded bootstrap (`U.BOOT_SEED`).

A *family* is a list of cells declared in its own decision row; a *cell* is a design replayed over every start day
(`scripts/u_family.py`). D-621 fixes what is read from the cells' records:

* **The scorecard** (`MEASURES`, `scorecard`; D-621 (1), `docs/USER_MILESTONES.md`): the primary **P** -- the mean of
  the shares of units ahead at months 1, 2 and 3 -- and nine guarded measures, each one of U1's own readings
  (`user_journey.metric_rows`, read by its key; nothing is recomputed here), each on the starts with its own horizon
  left, each with its direction. P is read on the starts with 63 sessions: per start the months 1 to 3 that end above
  zero (`months_ahead`, U1's own indicator `periodic:share_positive`), over three -- so P is an exact ratio of counts
  and a tie between two cells is an exact tie.
* **The blocks** (`block`; D-621 (4)(b)): `early` -- the starts to the last start of 2023 less the reading's horizon
  (the last `horizon` sessions of starts dropped, so no early reading touches a 2024 session) -- and `late` -- the
  starts from the first session of 2024 with the reading's horizon left. The family's cell is chosen on `early`
  (`choose`: the best P, a tie to the first declared) and judged on `late`; the reverse pair is read beside.
* **The lines of D-621 (3) and (4)(e)**, in the row's order (`LINES`):
  `(3)(i)` `p_difference` -- the paired difference in P from R* on the judged block's common start dates, U1's
  moving-block bootstrap (`user_journey.paired_interval`: blocks of 63 starts, seed 20261700, 2,000 draws) read
  ONE-SIDED at the family's level `family_level(k)` = 0.05 / (k (k + 1)); it holds when the difference and the lower
  limit are both above zero;
  `(3)(ii)` `guard_lines` -- no guarded measure worse than R*'s on the judged block by more than the tolerance
  (`tolerance_line`: 0.05 absolute on a share, 10 % of R*'s value on dollars, sessions and ratios; a blank on either
  side fails the line and is reported blank; a zero reference leaves no relative tolerance);
  `(3)(iii)` `gate_floor` -- growth at the bound above zero and above P-06's row, every offered R resolving, every
  firm rule used verified (numbers handed in; no engine call here);
  `(3)(iv)` `coin_line` -- a coin design wins on P against R* under at least 40 of D-568's 50 coin sequences;
  `(4)(e)` `year_rule` -- not worse than R* on P in more than one of the seven start years.
* **The verdict** (`verdict`): `CARRIED` only if every line holds, else `CLOSED` with the first line that does not,
  in D-621's order; a line that was not evaluated never counts as held.
* **The row to beat** (`row_to_beat`; D-621 (2)): on each measure the best of P-14, P-15 and P-16 in U1's file; R* is
  the best on P.
* **The bases** (`BASES`; D-626 (8)): a cell is plain-data overrides on one base's replay setup -- `p16` (the default:
  P-16's, the 37.5-point coin) or `p14` (P-14's: A3-BRK30's breakout on the no-closure table with the 20-in-21 budget).
  A family may mix bases; the choice is still the best P on the choice block, whatever the base. A base's cell with no
  override is its reference (`REFERENCE_CELLS`), the identity's side and never counted. Line (3)(iv) is a coin
  design's only: for a cell on `p14` it is `not applicable` (`BASE_COIN_DESIGN`, `verdict(coin_design=False)`), never
  held. `funded_cap_share` is refused on `p14` (`BASE_REFUSED_KINDS`): there it would scale the funded micro cap of
  both of P-14's rungs alike, which is not D-544's reading (a reference stop over the coin's one wider stop).

* **The window bases** (`WINDOW_BASES`; D-639, the user's hours): a coin cell restricted to one session window --
  London, US or Asia at the 25- or the 37.5-point stop -- on its own trades, its own 0.05 bounds and its own day
  capacity, on P-14's protocol as P-15 and P-16. A window base is a family cell ITSELF: it takes no override, and its
  cell with no override is COUNTED (`counted`), where `p16` and `p14` keep their uncounted references. `BASES` stays
  the two override bases; `ALL_BASES` adds the window bases. **The R cap** (`r_cap`, D-639 (2)): from each offered R's
  pass or fail on D-212's line (at most 5 % unresolved overall and in the worst calendar year -- read by the caller
  from the cell's resolution columns, never from a profit figure) the largest R that passes, or no cap when every R
  passes; a cell with no passing R above the collect leaf's, or with too few marks to offer a trade a session
  (`supply_problem`), is NOT RUNNABLE and is not a cell. `capped_policy_dict` is the table as plain data with every
  leaf's R above the cap set to the cap, its dollar risk unchanged; the table is not re-solved.

* **The joint bases** (`JOINT_BASES`; D-643 as D-644 widens it, the multi-firm portfolio by sequence): P-16's trades
  through the joint two-firm engine -- Topstep's five seats plus 1, 2 or 5 Lucid seats; the Lucid firm run from day 0
  or opened only when the campaign's first payout has arrived (`opens`, the joint run's sequencing option); under one
  of three deals (`deal`: `hypo_hedge`'s `unhedged`, `hedged`, `hedged_combines`). 3 x 2 x 3 = 18. A joint base is a
  family cell ITSELF, as a window base is: no override, counted. Every figure of a joint cell is an UPPER BOUND while
  Lucid's funded monthly fee and payout fee are unpriced (`upper_bound`), so a joint cell that holds every line is not
  `CARRIED`: the verdict is `HOLDS_AS_UPPER_BOUND` (`verdict(upper_bound=True)`), recorded with what it waits for.
  **The six `unhedged` cells are eligible** (`selectable`; labelled `lucid_upper_bound`, counted under the family's
  id). **The twelve hedged cells are HYPOTHETICAL** (`hypothetical`; cross-firm hedging is prohibited at both firms,
  tier 1): labelled `hypothetical_hedge` on every row, counted under `<row id>:hypothetical_hedge`, written with their
  scorecard beside the eligible cells -- and REFUSED in the choice, the judgement, every guard and as a row to beat
  (`refuse_labelled`; `choose`, `judge` and `row_to_beat` raise when handed one).

* **The funded plan** (`funded_plan`; D-653, program U's family 7): an override kind on `p16` and `p14` -- the base's
  table with its funded phase (activation to the first payout) replaced by ONE leaf, `{"risk": X, "rr": 1.0}`: every
  funded trade before the first payout at X dollars and 1R, one trade a session. `funded_plan_policy_dict` is the
  table as plain data with that phase replaced -- the evaluation's leaves and the paid phase's leaves (after a first
  payout) the base's, untouched; the table is not re-solved. R is fixed at 1 (`FUNDED_PLAN_RR`: D-653 drops any
  other); with `funded_cap_share` it is refused (the plan's dollars are read under the full allowance). A window base
  and a joint base take no override, so none there. **`"paid": true`** (optional; D-653 as amended before its run):
  the same leaf replaces the PAID phase too -- X dollars at 1R, one trade a session, in every state after a first
  payout, the request day and the base's no-trade states included -- for the Consistency cells, where a paid phase
  solved for the Standard path can hold an account for good; absent or false, the paid phase is the base's.

* **The crippled funded account resolved at once** (`funded_resolve`; D-659, program U's family 9): an override kind on
  `p16` and `p14`, `{"rr": r}` -- in the base's table's funded phase (activation to the first payout), in every state
  whose balance is BELOW the account's starting balance (`FUNDED_RESOLVE_START`: a balance of zero in the table's
  variables), the base's leaves are replaced by one bold leaf a cushion band: risk = the band's LOWER edge on the
  table's own cushion grid (never more than the room), never less than one micro's dollars at the base's stop
  (`min_risk`, which the runner reads from the base's trades), R = r, one trade a session. States at or above the
  starting balance, the paid phase and the evaluation are the base's own subtrees. `funded_resolve_policy_dict` is the
  table as plain data; it is not re-solved. Refused with `funded_plan` (that plan leaves no base leaf to replace) and
  with `funded_cap_share` (the room's dollars are read under the full allowance); a window base and a joint base take
  no override, so none there.

Every blank is NaN; a blank never passes a line.
"""
from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

from propedge.research import user_journey as U

DECISION = "D-621"
PROGRAM = "U"
SCRIPT = "scripts/u_family.py"
READING = ("EXPLORATORY (D-621, program U): a lever family judged on the user's milestones by the declared selection "
           "rule; beside the gate, never a verdict of the gate (D-234); a carried cell is a new candidate, not a change "
           "to any verdict")

#: the arm the scorecard is read on (D-621 (1)); the chosen cell is also read at `BESIDE_ARM`, beside
ARM = "verdict"
BESIDE_ARM = "point"
if (ARM, BESIDE_ARM) != tuple(U.ARMS):
    raise RuntimeError("U1's arms are not (verdict, point)")

#: the rows to beat (D-621 (2)), in the row's order (a tie goes to the first); never a row to beat: P-13 and FV3-C
ROWS_TO_BEAT = ("p14", "p15", "p16")
BESIDE_ONLY = ("p13", "fv3c")
#: the rows to beat that are coin designs (P-15, P-16: family RC); P-14 is A3-BRK30's breakout -- no coin, so its P is
#: the same under every coin sequence
COIN_DESIGNS = ("p15", "p16")

#: P: months 1, 2 and 3; its horizon, and the bootstrap's block (D-621 (3)(i): "blocks of 63 sessions")
P_MONTHS = (1, 2, 3)
P_HORIZON = U.MONTH * max(P_MONTHS)
BOOT_BLOCK = 63
#: the program's budget (D-621 (5)): family k is judged one-sided at ALPHA / (k (k + 1))
ALPHA = 0.05
#: the tolerances (D-621 (3)(ii))
SHARE_TOLERANCE = 0.05
RELATIVE_TOLERANCE = 0.10
#: floating-point slack on a tolerance's boundary only (a shortfall of exactly the tolerance holds: "by more than")
SLACK = 1e-12
#: the walk-forward's boundary (D-621 (4)(b)) and the seven start years (D-621 (4)(e), D-620 G5)
CHOICE_LAST_YEAR = 2023
JUDGED_FIRST_YEAR = 2024
EARLY, LATE = "early", "late"
BLOCKS = (EARLY, LATE)
START_YEARS = (2020, 2021, 2022, 2023, 2024, 2025, 2026)
YEARS_WORSE_ALLOWED = 1
#: development start days only (D-621 (4)(a))
WINDOW_END = "2026-07-16"
#: the coin sequences (D-621 (3)(iv), D-568) and the thinning
COIN_SEQUENCES = tuple(20261600 + i for i in range(50))
COIN_WINS_NEEDED = 40
COIN_EVERY = 21
REGISTERED_COIN = U.COIN_SEED
#: the gate floor (D-621 (3)(iii)): a campaign seed never used before, and the scoreboard's row to beat
GATE_SEED = 20261801
GATE_PATHS = 500
GATE_ROW_TO_BEAT = "P-06"
#: the lines of the selection rule, in D-621's order
LINES = ("(3)(i)", "(3)(ii)", "(3)(iii)", "(3)(iv)", "(4)(e)")
CARRIED, CLOSED = "CARRIED", "CLOSED"
SECTIONS = ("identity", "cell", "choice", "judged", "reverse", "guards", "verdict")

HIGHER, LOWER = "higher", "lower"
SHARE, DOLLARS, SESSIONS, RATIO = "share", "dollars", "sessions", "ratio"
PRIMARY, GUARDED = "primary", "guarded"


@dataclass(frozen=True)
class Measure:
    """One line of the scorecard: its key, the sessions a start needs for it (`horizon`), U1's reading(s) it is
    (`u1_keys`: `user_journey.metric_rows`' keys), its direction, the unit its tolerance is in, its role."""

    key: str
    what: str
    horizon: int
    u1_keys: tuple[str, ...]
    direction: str
    unit: str
    role: str


#: the scorecard (D-621 (1)); reported-only lines (S2, S3d, S6, Q) are U1's own rows and are not selected on
MEASURES: tuple[Measure, ...] = (
    Measure("P", "the mean of the shares of units ahead at months 1, 2 and 3", P_HORIZON,
            tuple(f"periodic:share_positive@{U.MONTH * m}" for m in P_MONTHS), HIGHER, SHARE, PRIMARY),
    Measure("S1", "cash spent before the first payout, p90", 126, ("first_payout:spent_before_p90@126",), LOWER,
            DOLLARS, GUARDED),
    Measure("S3a", "the share paid by session 21", 21, ("first_payout:share_by@21",), HIGHER, SHARE, GUARDED),
    Measure("S3b", "sessions to the first payout, p90", 126, ("first_payout:days_p90@126",), LOWER, SESSIONS, GUARDED),
    Measure("S3c", "payouts per dollar of fees at month 3, pooled", 63,
            ("money_back:payouts_per_fee_dollar_pooled@63",), HIGHER, RATIO, GUARDED),
    Measure("S4a", "the share ahead at month 6", 126, ("periodic:share_positive@126",), HIGHER, SHARE, GUARDED),
    Measure("S4b", "the share ahead at month 12", 252, ("periodic:share_positive@252",), HIGHER, SHARE, GUARDED),
    Measure("S5a", "the month-3 net's p10", 63, ("periodic:net_p10@63",), HIGHER, DOLLARS, GUARDED),
    Measure("S5b", "the longest gap after the first payout within 126 sessions, p90", 126,
            ("consistency:longest_gap_p90@126",), LOWER, SESSIONS, GUARDED),
    Measure("S5c", "the concentration at month 6", 126, ("consistency:concentration@126",), LOWER, RATIO, GUARDED),
)
BY_KEY = {m.key: m for m in MEASURES}
PRIMARY_KEY = "P"
GUARDED_KEYS = tuple(m.key for m in MEASURES if m.role == GUARDED)
HORIZONS = tuple(sorted({m.horizon for m in MEASURES}))
#: the exact-length runs a scorecard reading may read a start from (`user_journey.Views.at`): a start row of U1's file
#: names them (`exact_runs_differing`) and does not carry them
ALT_HORIZONS = tuple(h for h in U.EXACT if h in {U.MONTH * m for m in P_MONTHS} | set(HORIZONS))

NAN = float("nan")


def _blank(x: Any) -> bool:
    try:
        return not math.isfinite(float(x))
    except (TypeError, ValueError):
        return True


# ------------------------------------------------------------------------------------------------ U1's start rows


def _num(x: Any) -> float:
    s = "" if x is None else str(x).strip()
    return NAN if s in ("", "nan", "NaN", "None") else float(s)


def _days(x: Any) -> list[int]:
    s = "" if x is None else str(x).strip()
    return [] if s in ("", "nan", "NaN", "None") else [int(float(v)) for v in s.split()]


def records_from_start_rows(rows: Iterable[Mapping[str, Any]]) -> tuple[list[dict[str, Any]], list[tuple[int, int]]]:
    """U1's section `start` rows (`scripts/user_journey.py`'s `start_rows`, as text or numbers) back as start records
    in start order, and the (start, h) whose exact h-session run differed from the long replay at a horizon the
    scorecard reads (`ALT_HORIZONS`): the file names such a start and does not hold its exact run's record, so the
    scorecard cannot read it as U1 did. Each payout's cash is in the payouts file and is not needed here (blank)."""
    out, missing = [], []
    for r in rows:
        pays = _days(r.get("pay_days"))
        rec = {"start_day": int(float(r["start_day"])), "start_date": str(r["start_date"]),
               "observed": int(float(r["observed"])), "pass_days": _days(r.get("pass_days")),
               "funded_days": _days(r.get("funded_days")), "pay_days": pays, "pay_cash": [NAN] * len(pays),
               **{k: _num(r.get(k)) for k in ("first_pass", "first_funded", "first_payout", "first_payout_cash",
                                              "spent_before_first_pass", "spent_before_first_payout", "net_30")},
               "net_month": [_num(r.get(f"net_month_{k}")) for k in range(1, U.MONTHS + 1)],
               "fees_month": [_num(r.get(f"fees_month_{k}")) for k in range(1, U.MONTHS + 1)]}
        missing += [(rec["start_day"], h) for h in _days(r.get("exact_runs_differing")) if h in ALT_HORIZONS]
        out.append(rec)
    out.sort(key=lambda x: x["start_day"])
    return out, missing


def window_problems(records: Sequence[Mapping[str, Any]]) -> list[str]:
    """D-621 (4)(a): development start days only -- every start on or before `WINDOW_END`."""
    late = sorted(str(r["start_date"]) for r in records if str(r["start_date"])[:10] > WINDOW_END)
    return [f"{len(late)} start days after {WINDOW_END} (first: {late[0]})"] if late else []


# ------------------------------------------------------------------------------------------------ the blocks


def _year(r: Mapping[str, Any]) -> int:
    return int(str(r["start_date"])[:4])


def _ordered(records: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    return sorted(records, key=lambda r: int(r["start_day"]))


def eligible(records: Sequence[Mapping[str, Any]], horizon: int) -> list[Mapping[str, Any]]:
    """The starts with at least `horizon` sessions left (D-620 (3)(a)), in start order."""
    return [r for r in _ordered(records) if int(r["observed"]) >= int(horizon)]


def block(records: Sequence[Mapping[str, Any]], which: str | None, horizon: int) -> list[Mapping[str, Any]]:
    """D-621 (4)(b)'s blocks for a reading at `horizon` sessions, in start order. `early`: the starts of
    `CHOICE_LAST_YEAR` and before, less the reading's horizon -- every start within `horizon` sessions of the block's
    last start dropped (on consecutive start days: the block's last `horizon` starts), so no early reading touches a
    later session. `late`: the starts from `JUDGED_FIRST_YEAR` on with `horizon` sessions left. None: every start with
    `horizon` sessions left."""
    h = int(horizon)
    if which is None:
        return eligible(records, h)
    if which == EARLY:
        e = [r for r in _ordered(records) if _year(r) <= CHOICE_LAST_YEAR]
        if not e:
            return []
        last = max(int(r["start_day"]) for r in e)
        return [r for r in e if int(r["start_day"]) <= last - h and int(r["observed"]) >= h]
    if which == LATE:
        return [r for r in _ordered(records) if _year(r) >= JUDGED_FIRST_YEAR and int(r["observed"]) >= h]
    raise ValueError(f"a block is one of {BLOCKS} or None, got {which!r}")


def thinned(records: Sequence[Mapping[str, Any]], every: int = COIN_EVERY) -> list[Mapping[str, Any]]:
    """Every `every`-th start of `records` in start order, from the first (D-621 (3)(iv)'s thinning)."""
    return _ordered(records)[::int(every)]


# ------------------------------------------------------------------------------------------------ the scorecard


def _p_stats() -> list[U.Stat]:
    by = {s.key: s for s in U.stats()}
    return [by[k] for k in BY_KEY[PRIMARY_KEY].u1_keys]


def months_ahead(records: Sequence[Mapping[str, Any]]) -> dict[str, float]:
    """{start date: the months 1 to 3 that end with net cash above zero (0 .. 3)} over the starts with `P_HORIZON`
    sessions -- U1's own indicator (`user_journey.stats`' `periodic:share_positive`, so a start whose exact run differed
    is read from it). A start without all three nets is left out."""
    sub = eligible(records, P_HORIZON)
    if not sub:
        return {}
    V = U.Views(sub)
    count = np.zeros(len(sub))
    ok = np.ones(len(sub), bool)
    for s in _p_stats():
        v, _, e = s.fn(V)
        count += v
        ok &= e
    return {str(d): float(c) for d, c, k in zip(V.base["start_date"], count, ok) if k}


def p_of(counts: Iterable[float]) -> tuple[float, int]:
    """(P, the starts): the months ahead summed over the starts, over three a start -- the mean of the three shares on
    the same starts, as one exact ratio."""
    c = [float(x) for x in counts]
    return (float(sum(c) / (len(P_MONTHS) * len(c))) if c else NAN), len(c)


def u1_reading(records: Sequence[Mapping[str, Any]]) -> dict[str, tuple[float, int]]:
    """{U1's key: (value, n)} for every reading the scorecard is made of, exactly as U1 reads them on `records`
    (`user_journey.metric_rows`: each on its own eligible starts)."""
    want = {k for m in MEASURES for k in m.u1_keys}
    if not records:
        return {k: (NAN, 0) for k in want}
    rows = U.metric_rows(U.Views(_ordered(records)))
    return {r["key"]: (float(r["value"]), int(r["n"])) for r in rows if r["key"] in want}


def p_from_u1(reading: Mapping[str, tuple[float, int]]) -> float:
    """The mean of U1's three shares ahead at months 1, 2 and 3 as its file holds them (each on its own eligible
    starts) -- beside `scorecard`'s P, which reads the three on the starts with 63 sessions."""
    v = [float(reading[k][0]) for k in BY_KEY[PRIMARY_KEY].u1_keys]
    return float(sum(v) / len(v)) if all(math.isfinite(x) for x in v) else NAN


def scorecard(records: Sequence[Mapping[str, Any]], which: str | None = None, *,
              paired_with: Sequence[Mapping[str, Any]] | None = None) -> dict[str, dict[str, Any]]:
    """{measure key: {value, n}} on a set of starts: every start (`which` None), or D-621 (4)(b)'s `early` or `late`
    block -- each measure on the starts of the set with its own horizon left (`block`). `paired_with`: the other side's
    records; each measure is then read on the start dates both sides hold in the set at that measure's horizon. A
    measure with no eligible start is blank."""
    out: dict[str, dict[str, Any]] = {}
    for h in HORIZONS:
        mine = block(records, which, h)
        if paired_with is not None:
            dates = {str(r["start_date"]) for r in block(paired_with, which, h)}
            mine = [r for r in mine if str(r["start_date"]) in dates]
        read = u1_reading(mine)
        for m in MEASURES:
            if m.horizon != h:
                continue
            if m.key == PRIMARY_KEY:
                v, n = p_of(months_ahead(mine).values())
            else:
                v, n = read[m.u1_keys[0]] if mine else (NAN, 0)
            out[m.key] = {"value": float(v), "n": int(n)}
    return {m.key: out[m.key] for m in MEASURES}


def row_to_beat(cards: Mapping[str, Mapping[str, Mapping[str, Any]]], *, refused: Iterable[str] = ()
                ) -> dict[str, Any]:
    """D-621 (2): on each measure the best of the rows to beat (`ROWS_TO_BEAT`; `cards`: {configuration: its scorecard
    on every start}), in the measure's direction -- a blank is never the best, a tie goes to the first in D-621's
    order -- and R*, the row to beat on P (None when no row holds a P). `refused` (D-644 (4)): the cells labelled
    `hypothetical_hedge` -- a card of one handed in is refused (`refuse_labelled`): never a row to beat."""
    refuse_labelled(cards, refused, "the rows to beat")
    missing = [c for c in ROWS_TO_BEAT if c not in cards]
    if missing:
        raise ValueError(f"no scorecard for {missing}")
    by: dict[str, dict[str, Any]] = {}
    for m in MEASURES:
        best, val = None, NAN
        for c in ROWS_TO_BEAT:
            v = float(cards[c][m.key]["value"])
            if not math.isfinite(v):
                continue
            if best is None or (v > val if m.direction == HIGHER else v < val):
                best, val = c, v
        by[m.key] = {"config": best, "value": val}
    return {"r_star": by[PRIMARY_KEY]["config"], "by_measure": by}


# ------------------------------------------------------------------------------------------------ the choice


def choose(cells: Sequence[tuple[str, Sequence[Mapping[str, Any]]]], which: str = EARLY, *,
           refused: Iterable[str] = ()) -> dict[str, Any]:
    """D-621 (4)(b): the family's one cell for judgement -- the cell with the best P on the choice block (`which`;
    `early` for the judgement, `late` for the reverse read beside); a tie goes to the first declared; a cell with no
    start in the block is never chosen. `cells`: (name, records) in the declared order. `refused` (D-644 (4)): the
    cells labelled `hypothetical_hedge` -- one handed in is refused (`refuse_labelled`): never in the choice."""
    names = [n for n, _ in cells]
    refuse_labelled(names, refused, "the choice")
    if len(set(names)) != len(names):
        raise ValueError("a family's cells carry distinct names")
    rows, chosen, best = [], None, NAN
    for name, recs in cells:
        p, n = p_of(months_ahead(block(recs, which, P_HORIZON)).values())
        rows.append({"cell": name, "block": which, "p": p, "n": n})
        if math.isfinite(p) and (chosen is None or p > best):
            chosen, best = name, p
    for r in rows:
        r["chosen"] = bool(r["cell"] == chosen)
    return {"chosen": chosen, "block": which, "rows": rows}


# ------------------------------------------------------------------------------------------------ line (3)(i)


def family_level(k: int) -> float:
    """D-621 (5): family k (numbered from 1 in the order declared, both tracks together) is judged one-sided at
    0.05 / (k (k + 1)); the levels sum to at most 0.05 however long the program runs."""
    if isinstance(k, bool) or not isinstance(k, (int, np.integer)) or int(k) < 1:
        raise ValueError(f"a family's number is a whole number from 1, got {k!r}")
    return ALPHA / (int(k) * (int(k) + 1))


def p_difference(cell: Sequence[Mapping[str, Any]], reference: Sequence[Mapping[str, Any]], which: str, level: float,
                 *, draws: int = U.BOOT_DRAWS, seed: int = U.BOOT_SEED) -> dict[str, Any]:
    """D-621 (3)(i): the paired difference in P between a cell and R* on the block's common start dates (date order),
    and the lower limit of its ONE-SIDED interval at `level` from U1's moving-block bootstrap
    (`user_journey.paired_interval` at alpha = 2 x level: its lower percentile is then the `level` quantile; blocks of
    `BOOT_BLOCK` starts). It holds when the difference and the lower limit are both above zero; a blank limit (fewer
    common starts than one block) does not hold."""
    if not 0.0 < float(level) < 0.5:
        raise ValueError(f"a one-sided level is in (0, 0.5), got {level!r}")
    a = months_ahead(block(cell, which, P_HORIZON))
    b = months_ahead(block(reference, which, P_HORIZON))
    dates = sorted(set(a) & set(b))
    den = np.full(len(dates), float(len(P_MONTHS)))
    r = U.paired_interval([a[d] for d in dates], den, [b[d] for d in dates], den, BOOT_BLOCK,
                          alpha=2.0 * float(level), draws=draws, seed=seed)
    diff, lo = float(r["difference"]), float(r["lo"])
    return {"line": LINES[0], "block": which, "value": float(r["value"]), "reference": float(r["reference"]),
            "difference": diff, "lower": lo, "level": float(level), "n": int(r["n"]), "boot_block": BOOT_BLOCK,
            "draws": int(draws), "seed": int(seed), "first_date": dates[0] if dates else "",
            "last_date": dates[-1] if dates else "",
            "holds": bool(math.isfinite(diff) and math.isfinite(lo) and diff > 0 and lo > 0)}


# ------------------------------------------------------------------------------------------------ line (3)(ii)


def tolerance_line(m: Measure, value: float, reference: float) -> dict[str, Any]:
    """D-621 (3)(ii) for one guarded measure: the cell is worse than R* by `worse_by` in the measure's own direction
    (negative: better) and may be worse by `allowed` -- `SHARE_TOLERANCE` (absolute) on a share, `RELATIVE_TOLERANCE`
    of R*'s absolute value on dollars, sessions and ratios (so a zero reference leaves no tolerance: the cell must not
    be worse at all). A shortfall of exactly the tolerance holds ("by more than"). A blank on either side fails the
    line and is reported blank."""
    v, r = float(value), float(reference)
    out = {"measure": m.key, "direction": m.direction, "unit": m.unit, "value": v, "reference": r, "worse_by": NAN,
           "allowed": NAN, "blank": False, "holds": False}
    if not (math.isfinite(v) and math.isfinite(r)):
        out["blank"] = True
        return out
    worse = (r - v) if m.direction == HIGHER else (v - r)
    allowed = SHARE_TOLERANCE if m.unit == SHARE else RELATIVE_TOLERANCE * abs(r)
    out.update(worse_by=float(worse), allowed=float(allowed),
               holds=bool(worse <= allowed + SLACK * max(1.0, abs(r))))
    return out


def guard_lines(cell_card: Mapping[str, Mapping[str, Any]], reference_card: Mapping[str, Mapping[str, Any]]
                ) -> list[dict[str, Any]]:
    """D-621 (3)(ii): `tolerance_line` for every guarded measure, in the scorecard's order."""
    return [{**tolerance_line(BY_KEY[k], cell_card[k]["value"], reference_card[k]["value"]),
             "n": int(cell_card[k]["n"]), "n_reference": int(reference_card[k]["n"])} for k in GUARDED_KEYS]


def guards_hold(lines: Sequence[Mapping[str, Any]]) -> bool:
    return bool(len(lines) == len(GUARDED_KEYS) and all(bool(x["holds"]) for x in lines))


# ------------------------------------------------------------------------------------------------ line (4)(e)


def year_rule(cell: Sequence[Mapping[str, Any]], reference: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """D-621 (4)(e): P of the cell and of R* in each of the seven start years, on the common start dates of every
    start with `P_HORIZON` sessions; the cell is worse in a year when its P is below R*'s there. A year with no common
    start is blank and counts as worse (a blank never passes). It holds when at most `YEARS_WORSE_ALLOWED` years are
    worse."""
    a, b = months_ahead(cell), months_ahead(reference)
    common = sorted(set(a) & set(b))
    rows = []
    for y in START_YEARS:
        ds = [d for d in common if int(d[:4]) == y]
        pa, n = p_of(a[d] for d in ds)
        pb, _ = p_of(b[d] for d in ds)
        blank = n == 0
        rows.append({"year": int(y), "value": pa, "reference": pb, "n": int(n), "blank": bool(blank),
                     "worse": bool(blank or pa < pb)})
    worse = int(sum(r["worse"] for r in rows))
    return {"line": LINES[4], "rows": rows, "years_worse": worse, "allowed": YEARS_WORSE_ALLOWED,
            "holds": bool(worse <= YEARS_WORSE_ALLOWED)}


# ------------------------------------------------------------------------------------------------ line (3)(iv)


def coin_line(cell_p: Sequence[float], reference_p: Sequence[float], *, needed: int = COIN_WINS_NEEDED,
              sequences: int = len(COIN_SEQUENCES)) -> dict[str, Any]:
    """D-621 (3)(iv): the coin sequences on which the cell's P is above R*'s (a tie or a blank is not a win); it holds
    with at least `needed` wins and only when all `sequences` were read."""
    a, b = [float(x) for x in cell_p], [float(x) for x in reference_p]
    if len(a) != len(b):
        raise ValueError(f"{len(a)} sequences of the cell against {len(b)} of the reference")
    wins = int(sum(1 for x, y in zip(a, b) if math.isfinite(x) and math.isfinite(y) and x > y))
    return {"line": LINES[3], "sequences": len(a), "sequences_declared": int(sequences), "wins": wins,
            "wins_needed": int(needed), "holds": bool(len(a) == int(sequences) and wins >= int(needed))}


# ------------------------------------------------------------------------------------------------ line (3)(iii)


def gate_floor(growth_at_bound: float, row_to_beat_growth: float, every_r_resolves: bool, rules_verified: bool
               ) -> dict[str, Any]:
    """D-621 (3)(iii): the gate stays a floor -- the cell's growth on the required bankroll at the bound (the fresh
    campaign seed, 500 paths) above zero and above the scoreboard's row to beat (P-06's), every offered R resolving
    (D-212) and every firm rule the cell uses verified. Numbers handed in; a blank growth does not hold."""
    g, p = float(growth_at_bound), float(row_to_beat_growth)
    problems = []
    if not math.isfinite(g):
        problems.append("the growth at the bound is blank")
    elif not g > 0:
        problems.append("the growth at the bound is not above zero")
    if not math.isfinite(p):
        problems.append(f"{GATE_ROW_TO_BEAT}'s growth at the bound is blank")
    elif math.isfinite(g) and not g > p:
        problems.append(f"the growth at the bound is not above {GATE_ROW_TO_BEAT}'s row")
    if not bool(every_r_resolves):
        problems.append("an offered R does not resolve (D-212)")
    if not bool(rules_verified):
        problems.append("a firm rule the cell uses is not verified")
    return {"line": LINES[2], "growth_at_bound": g, "row_to_beat_growth": p, "every_r_resolves": bool(every_r_resolves),
            "rules_verified": bool(rules_verified), "problems": problems, "holds": not problems}


# ------------------------------------------------------------------------------------------------ the verdict


def verdict(lines: Mapping[str, bool | None], *, coin_design: bool = True, upper_bound: bool = False
            ) -> dict[str, Any]:
    """`CARRIED` only if every line of D-621 (3) and (4)(e) holds; else `CLOSED` with the first line, in D-621's order
    (`LINES`), that does not hold. A line that was not evaluated (None, or absent) never counts as held; (3)(iv) is
    for a coin design only and is left out otherwise. `status`: each line's `holds`, `fails`, `not evaluated` or `not
    applicable`. `upper_bound` (D-643 (3); a cell whose every figure is an upper bound, `upper_bound(base)`): such a
    cell is never `CARRIED` -- with every line held the verdict is `HOLDS_AS_UPPER_BOUND`; a line that does not hold
    closes the family exactly as before."""
    unknown = sorted(set(lines) - set(LINES))
    if unknown:
        raise ValueError(f"not lines of the selection rule: {unknown}")
    status, first = {}, ""
    for line in LINES:
        if line == LINES[3] and not coin_design:
            status[line] = "not applicable"
            continue
        v = lines.get(line)
        status[line] = "not evaluated" if v is None else ("holds" if bool(v) else "fails")
        if status[line] != "holds" and not first:
            first = line
    held = HOLDS_AS_UPPER_BOUND if upper_bound else CARRIED
    return {"verdict": CLOSED if first else held, "first_failing": first,
            "first_failing_status": status.get(first, ""), "status": status}


def judge(cells: Sequence[tuple[str, Sequence[Mapping[str, Any]]]], reference: Sequence[Mapping[str, Any]], k: int,
          *, draws: int = U.BOOT_DRAWS, seed: int = U.BOOT_SEED, refused: Iterable[str] = ()) -> dict[str, Any]:
    """A family's lines that need the start records only. `forward` (the judgement): the cell chosen on `early`, judged
    on `late` -- line (3)(i) at the family's level and line (3)(ii) on the two sides' paired scorecards; `reverse`
    (beside, never the verdict): chosen on `late`, judged on `early`; `years`: line (4)(e) for the forward cell on every
    start. `lines`: {(3)(i), (3)(ii), (4)(e): held or not} -- None where no cell could be chosen; (3)(iii) and (3)(iv)
    are the caller's (they need replays and a campaign). `cells`: (name, records) in the declared order; `reference`:
    R*'s records. `refused` (D-644 (4)): the cells labelled `hypothetical_hedge` -- one handed in is refused
    (`refuse_labelled`): never chosen, never judged."""
    refuse_labelled([n for n, _ in cells], refused, "the judgement")
    level = family_level(k)
    by = dict(cells)
    out: dict[str, Any] = {"k": int(k), "level": level, "cells": len(cells)}
    for direction, choice_block, judged_block in (("forward", EARLY, LATE), ("reverse", LATE, EARLY)):
        ch = choose(cells, choice_block, refused=refused)
        d: dict[str, Any] = {"choice": ch, "chosen": ch["chosen"], "choice_block": choice_block,
                             "judged_block": judged_block, "i": None, "ii": None, "cell_card": None,
                             "reference_card": None}
        if ch["chosen"] is not None:
            recs = by[ch["chosen"]]
            d["i"] = p_difference(recs, reference, judged_block, level, draws=draws, seed=seed)
            d["cell_card"] = scorecard(recs, judged_block, paired_with=reference)
            d["reference_card"] = scorecard(reference, judged_block, paired_with=recs)
            d["ii"] = guard_lines(d["cell_card"], d["reference_card"])
        out[direction] = d
    f = out["forward"]
    out["chosen"] = f["chosen"]
    out["years"] = year_rule(by[f["chosen"]], reference) if f["chosen"] is not None else None
    out["lines"] = {LINES[0]: None if f["i"] is None else bool(f["i"]["holds"]),
                    LINES[1]: None if f["ii"] is None else guards_hold(f["ii"]),
                    LINES[4]: None if out["years"] is None else bool(out["years"]["holds"])}
    return out


# ------------------------------------------------------------------------------------------------ families and counts

FAMILY_NAME = re.compile(r"^[a-z][a-z0-9_]*$")
CELL_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_+.\-]*$")
DECISION_ID = re.compile(r"^D-\d+$")
PROGRAM_ID = re.compile(r"^D-\d+:u_[a-z][a-z0-9_]*$")
HYPOTHETICAL_ID = re.compile(r"^D-\d+:hypothetical_hedge$")
#: the overrides a cell may put on P-16's replay setup with no engine change (`scripts/u_family.py` applies them)
SEAT_KEYS = ("accounts", "combines", "total_accounts")
PROTOCOL_FIELDS = ("keep_balance", "payout_frac", "payout_path")
PAYOUT_PATHS = ("standard", "consistency")
#: D-630's three entry options (`propedge.campaign.lockstep`; the pause as D-632 words it), each the campaign's own
#: restraint on buying evaluations: valid on either base, and none leans on a firm rule (D-630 (4): each only
#: withholds a purchase the trader is free not to make)
ENTRY_KINDS = ("wallet_stop", "pause_after_funded", "seat_ramp")
#: D-653 (program U's family 7): the funded plan with no bold opening -- the base's table with its funded phase
#: (activation to the first payout) replaced by one leaf, `{"risk": X, "rr": 1.0}`; R is fixed at 1 (D-653 (2): an R
#: above 1 is dropped), so any other R is refused, and so is any other key. One optional key, `"paid": true` (D-653 as
#: amended before its run): the same leaf replaces the paid phase too; absent or false, the paid phase is the base's
FUNDED_PLAN = "funded_plan"
FUNDED_PLAN_DECISION = "D-653"
FUNDED_PLAN_KEYS = ("risk", "rr")
FUNDED_PLAN_OPTIONAL = ("paid",)
FUNDED_PLAN_RR = 1.0
#: with the funded micro cap scaled the plan's dollars would not be the dollars D-653 declares (the full allowance)
FUNDED_PLAN_REFUSED_WITH = {"funded_cap_share": "D-653 reads the plan's dollars under the full verified allowance; a "
                                                "scaled funded cap would make them other dollars"}
#: D-659 (program U's family 9): the crippled funded account resolved at once -- the base's table with, in its funded
#: phase, every state whose balance is below the account's starting balance decided by one bold leaf a cushion band:
#: risk = the band's lower edge (never more than the room; never less than one micro at the base's stop), R = `rr`,
#: one trade a session. `{"rr": r}` and no other key; r is searched over D-659's two values by the family's cells, and
#: the runner refuses an r the base's blocks carry no edge and bound for
FUNDED_RESOLVE = "funded_resolve"
FUNDED_RESOLVE_DECISION = "D-659"
FUNDED_RESOLVE_KEYS = ("rr",)
#: one optional key, `"lowest"`: what decides a state below the starting balance whose cushion band's lower edge is
#: under one micro's dollars (on the tables on file the one band from a room of zero). `"micro"` -- the default, and
#: D-659 (1)'s own words ("never less than one micro at the base's stop"): the bold leaf at one micro's dollars.
#: `"base"` -- NOT D-659's text, built beside it because the default trades such a room one micro a session where the
#: base's own leaves there ask for at least the room: the base's subtree is left in that band. A cell may carry
#: `"base"` only under a decision row that amends D-659 before its run
FUNDED_RESOLVE_OPTIONAL = ("lowest",)
FUNDED_RESOLVE_LOWEST = ("micro", "base")
#: a funded account's starting balance in the table's state variables (`risk_policy.account_state`: a fresh funded
#: account is balance 0, cushion 2,000): "below its starting balance" is `balance` < 0
FUNDED_RESOLVE_START = 0.0
#: D-659 (1): "one trade an account a session"
FUNDED_RESOLVE_TRADES = 1
#: the kinds a `funded_resolve` cell cannot also carry, each with the reason
FUNDED_RESOLVE_REFUSED_WITH = {
    FUNDED_PLAN: "D-653's plan replaces the whole funded phase by one leaf, so no leaf of the base is left below the "
                 "starting balance for D-659 to replace: the two are different tables, not one cell",
    "funded_cap_share": "D-659 reads the room's dollars under the full verified allowance; a scaled funded cap would "
                        "make them other dollars"}
OVERRIDE_KINDS = (*SEAT_KEYS, "purchase_budget", "funded_cap_share", "protocol", "payout_timing", FUNDED_PLAN,
                  FUNDED_RESOLVE, *ENTRY_KINDS)
#: the name of the cell with no override (P-16 itself: the identity's side, replayed once and never counted)
REFERENCE_CELL = "reference"
#: the bases a cell's overrides are put on (D-626 (8)): U1's `p16` configuration (the default: every cell declared
#: without a base) or its `p14` configuration -- R*, A3-BRK30's breakout on the no-closure table, budget (20, 21)
BASES = ("p16", "p14")
DEFAULT_BASE = "p16"
BASE_LABEL = {"p16": "P-16", "p14": "P-14"}
#: each base's cell with no override: the identity's side (it must equal U1's start rows of that configuration start
#: for start), replayed once and never counted
REFERENCE_CELLS = {"p16": REFERENCE_CELL, "p14": "reference_p14"}
#: each base's seats -- its concurrent accounts, concurrent Combines and total accounts, the same five (D-34) on
#: both: what `seat_ramp` ramps up to, so a ramp's first seats are below it (`scripts/u_family.py`'s `apply_overrides`
#: refuses a base whose own total differs from this)
BASE_SEATS = {"p16": 5, "p14": 5}
#: line (3)(iv) is a coin design's only: a cell on P-14's trades draws no coin, so the line is not applicable to it
BASE_COIN_DESIGN = {b: b in COIN_DESIGNS for b in BASES}
#: the override kinds refused on a base, each with the reason. On `p14` every other kind reads the same engine
#: argument as on `p16` (both setups are `atlas_a3.gate_kwargs`' arguments): the three seat keys, `purchase_budget`
#: (P-14's own is (20, 21), as P-16's), the `protocol` fields and `payout_timing`. `funded_cap_share` would run -- it
#: scales the funded leg's micro cap by the share on every trade -- but P-14 trades two rungs (12.5 and 25 points),
#: neither wider than D-542's reference stop, so a share there caps both rungs alike and is not D-544's reading (the
#: 25-point stop over the coin's one 37.5-point stop: no funded state realising more dollars than at the reference
#: stop); it is refused rather than left to mean something different
BASE_REFUSED_KINDS: dict[str, dict[str, str]] = {
    "p16": {},
    "p14": {"funded_cap_share": "P-14 trades the 12.5- and 25-point rungs, neither wider than the reference stop: a "
                                "share there scales both rungs' funded micro cap alike, which is not D-544's reading "
                                "(a reference stop over the coin's one wider stop)"},
}
if (set(BASE_LABEL) != set(BASES) or set(REFERENCE_CELLS) != set(BASES) or set(BASE_REFUSED_KINDS) != set(BASES)
        or set(BASE_SEATS) != set(BASES)):
    raise RuntimeError("the bases' tables do not cover the bases")


#: D-639 (program U's family 4, the user's hours): the WINDOW BASES -- each a coin cell restricted to one session
#: window (`resolved_coin.WINDOWS`), built as its screen built it (`scripts/u_family.py`), on its own trades (a pinned
#: content hash), its own 0.05 bounds and its own day capacity, on P-14's protocol as P-15 and P-16 (the no-closure
#: table, the budget (20, 21), the strict rule, five seats). A window base is a family cell ITSELF: it takes no
#: override (`WINDOW_NO_OVERRIDE`), a family names it at most once, and its cell is COUNTED (`counted`). `BASES` above
#: stays the two override bases, whose cell with no override is an uncounted reference
WINDOW_DECISION = "D-639"
WINDOW_BASES: dict[str, dict[str, Any]] = {
    "s100_london": {"stop_ticks": 100, "window": "london"},
    "s100_us": {"stop_ticks": 100, "window": "us"},
    "s100_asia": {"stop_ticks": 100, "window": "asia"},
    "s150_london": {"stop_ticks": 150, "window": "london"},
    "s150_us": {"stop_ticks": 150, "window": "us"},
    "s150_asia": {"stop_ticks": 150, "window": "asia"},
}
ALL_BASES = (*BASES, *WINDOW_BASES)
#: the window base that is one of U1's configurations (D-639 (1): "must equal it start for start")
WINDOW_EQUALS_U1 = {"s150_london": "rc_s150_london"}
WINDOW_NO_OVERRIDE = "a window base is a family cell itself (D-639): it takes no override"
#: D-639 (2)'s two ways a window cell is not runnable (recorded, and then not a cell)
NOT_RUNNABLE_NO_R = "no offered R above the collect leaf's passes D-212"
NOT_RUNNABLE_SUPPLY = "too few marks to offer a trade a session"
if set(WINDOW_BASES) & set(BASES) or set(WINDOW_BASES) & set(REFERENCE_CELLS.values()) or (
        set(WINDOW_EQUALS_U1) - set(WINDOW_BASES)):
    raise RuntimeError("the window bases' names collide with the bases' or their references'")


#: D-643 as D-644 widens it (program U's family 5, the multi-firm portfolio by sequence): the JOINT BASES -- P-16's
#: trades (by their registered content hash, the opposite side aligned) through the joint two-firm engine with D-593's
#: conventions, as U1 builds its `p16_5+1` configuration (`scripts/u_firms.py`): Topstep's five seats and
#: `lucid_seats` Lucid seats (1, 2 or 5: inside Lucid's household caps), each firm's budget floor(20 x its seats / 5)
#: in 21 sessions, one pooled wallet, one position at a time per firm. `opens`: None -- the Lucid firm from day 0 --
#: or the joint run's sequencing option (`propedge.research.second_firm.FIRST_PAYOUT_ARRIVAL`, D-643 (2): the second
#: firm buys nothing and holds nothing until the campaign's first payout has arrived at the first firm). `deal`: one
#: of `propedge.research.hypo_hedge.MODES` by name (D-644 (2); checked equal in `scripts/u_firms.py`) -- `unhedged`,
#: the only deal a user could trade, or one of the two HYPOTHETICAL hedge deals. In D-644 (5)'s order: for each K, for
#: each opening, for each deal. A joint base is a family cell ITSELF: it takes no override (`JOINT_NO_OVERRIDE`), a
#: family names it at most once and its cell is COUNTED (`counted`). `BASES` and `ALL_BASES` stay as they were;
#: `EVERY_BASE` adds these. D-643's four cells keep their names (`l1_day0`, `l2_day0`, `l1_seq`, `l2_seq`)
JOINT_DECISION = "D-644"
SEQUENCING_DECISION = "D-643"
JOINT_OPENS_AT_FIRST_PAYOUT = "first_payout_arrival"
JOINT_TOPSTEP_SEATS = 5
JOINT_LUCID_SEATS = (1, 2, 5)
#: (the opening's name in a base's name, its `opens`)
JOINT_OPENINGS = (("day0", None), ("seq", JOINT_OPENS_AT_FIRST_PAYOUT))
JOINT_UNHEDGED = "unhedged"
JOINT_DEALS = (JOINT_UNHEDGED, "hedged", "hedged_combines")


def joint_base_name(lucid_seats: int, opening: str, deal: str) -> str:
    """A joint base's name: `l<K>_<day0|seq>` for the unhedged deal, with `_<deal>` after it for a hedge deal."""
    if int(lucid_seats) not in JOINT_LUCID_SEATS or opening not in dict(JOINT_OPENINGS) or deal not in JOINT_DEALS:
        raise ValueError(f"not a joint base: {lucid_seats!r} Lucid seats, opening {opening!r}, deal {deal!r}")
    return f"l{int(lucid_seats)}_{opening}" + ("" if deal == JOINT_UNHEDGED else f"_{deal}")


JOINT_BASES: dict[str, dict[str, Any]] = {
    joint_base_name(k, opening, deal): {"lucid_seats": k, "opens": opens, "deal": deal}
    for k in JOINT_LUCID_SEATS for opening, opens in JOINT_OPENINGS for deal in JOINT_DEALS}
EVERY_BASE = (*ALL_BASES, *JOINT_BASES)
#: the joint base that is one of U1's configurations (D-643 (1), D-644 (5): "equals U1's `p16_5+1` start for start")
JOINT_EQUALS_U1 = {"l1_day0": "p16_5+1"}
JOINT_NO_OVERRIDE = "a joint base is a family cell itself (D-643): it takes no override"
#: every row of an ELIGIBLE joint cell carries this label: Lucid's verified contract with its two unpriced fees at zero
UPPER_BOUND_LABEL = U.LUCID_LABEL
#: every row of a HYPOTHETICAL joint cell carries this label (`propedge.research.hypo_hedge.TAG`, checked equal in
#: `scripts/u_firms.py`) and `HYPOTHETICAL_NOTE`; its cell is counted under `hypothetical_id(<row id>)`
HYPOTHETICAL_LABEL = "hypothetical_hedge"
HYPOTHETICAL_NOTE = ("HYPOTHETICAL (D-644 (4), D-514): hypothetical_hedge -- a cross-firm hedge pair, prohibited at "
                     "Topstep (13747047, 10296582) and Lucid (11404734), tier 1; modelled as if the rule did not "
                     "exist; never chosen, judged, ranked, a row to beat or a candidate. Also lucid_upper_bound: "
                     "Lucid's funded monthly fee and payout fee are unpriced, so every figure is an upper bound on "
                     "them. The bound arm flatters a hedged cell (the bound's shift partly cancels inside a mirrored "
                     "pair, D-516): read the point arm beside it.")
#: D-643 (3): the most a family of upper-bound cells can return -- every line held, and still not carried
HOLDS_AS_UPPER_BOUND = "HOLDS AS AN UPPER BOUND"
UPPER_BOUND_WAITS_FOR = ("Lucid's funded monthly fee and payout fee are unpriced (D-561, D-575): every figure of the "
                         "cell is an upper bound on them, and the cell waits for the two prices")
if set(JOINT_BASES) & set(ALL_BASES) or set(JOINT_BASES) & set(REFERENCE_CELLS.values()) or (
        set(JOINT_EQUALS_U1) - set(JOINT_BASES)) or UPPER_BOUND_LABEL != "lucid_upper_bound" or len(JOINT_BASES) != 18:
    raise RuntimeError("the joint bases' names collide with the bases' or their references', or the label is not U1's")


def base_of(cell: Mapping[str, Any]) -> str:
    """A cell's base: its `base`, or the default (`p16`) when it declares none."""
    return str(cell.get("base", DEFAULT_BASE))


def is_joint_base(base: Any) -> bool:
    """Whether `base` is one of the joint bases (`JOINT_BASES`; D-643, D-644)."""
    return isinstance(base, str) and base in JOINT_BASES


def joint_deal(base: str) -> str:
    """A joint base's deal (`JOINT_DEALS`)."""
    if not is_joint_base(base):
        raise ValueError(f"a joint base is one of {tuple(JOINT_BASES)}, got {base!r}")
    return str(JOINT_BASES[base]["deal"])


def hypothetical(base: Any) -> bool:
    """Whether a cell on `base` is HYPOTHETICAL (D-644 (4)): a joint base under a hedge deal. Such a cell is labelled
    `HYPOTHETICAL_LABEL` on every row and never enters the choice, the judgement, a guard or the rows to beat."""
    return is_joint_base(base) and JOINT_BASES[base]["deal"] != JOINT_UNHEDGED


def selectable(cell: Mapping[str, Any]) -> bool:
    """Whether a declared cell may enter the choice and the judgement: every counted cell but a hypothetical one."""
    return counted(cell) and not hypothetical(base_of(cell))


def base_row_label(base: Any) -> str:
    """The label every row of a cell on `base` carries: `HYPOTHETICAL_LABEL` under a hedge deal, `UPPER_BOUND_LABEL`
    on any other joint base, none ('') elsewhere."""
    if hypothetical(base):
        return HYPOTHETICAL_LABEL
    return UPPER_BOUND_LABEL if is_joint_base(base) else ""


def hypothetical_id(decision: str) -> str:
    """The id a family's hypothetical cells are counted under: `<row id>:hypothetical_hedge` (D-514's form)."""
    if not DECISION_ID.match(str(decision)):
        raise ValueError(f"a decision row id is D-nnn, got {decision!r}")
    return f"{decision}:{HYPOTHETICAL_LABEL}"


def refuse_labelled(names: Iterable[Any], labelled: Iterable[str], where: str) -> None:
    """D-644 (4): refuse (ValueError) any of `names` that is one of the `labelled` cells -- a cell labelled
    `hypothetical_hedge` never enters `where` (the choice, the judgement, a guard, the rows to beat)."""
    marked = set(labelled)
    bad = [str(n) for n in names if n in marked]
    if bad:
        raise ValueError(f"REFUSED ({JOINT_DECISION} (4)): {', '.join(bad)} -- labelled {HYPOTHETICAL_LABEL} -- never "
                         f"enters {where}")


def joint_seats(base: str) -> tuple[int, int]:
    """A joint base's seats in firm order: Topstep's five, then Lucid's."""
    if not is_joint_base(base):
        raise ValueError(f"a joint base is one of {tuple(JOINT_BASES)}, got {base!r}")
    return (JOINT_TOPSTEP_SEATS, int(JOINT_BASES[base]["lucid_seats"]))


def joint_label(base: str) -> str:
    """A joint base in words: its seats, when the Lucid firm opens and -- under a hedge deal -- the deal."""
    t, k = joint_seats(base)
    when = ("from day 0" if JOINT_BASES[base]["opens"] is None
            else "opened when the campaign's first payout has arrived")
    deal = JOINT_BASES[base]["deal"]
    return (f"P-16's trades through the joint engine, {t} Topstep seats plus {k} Lucid seat{'' if k == 1 else 's'} "
            f"{when}" + ("" if deal == JOINT_UNHEDGED else f", the {deal} deal ({HYPOTHETICAL_LABEL})"))


def upper_bound(base: Any) -> bool:
    """Whether every figure of a cell on `base` is an upper bound (D-643 (3)): a joint base's cell runs Lucid's
    verified contract with its two unpriced fees at zero. Such a cell is never `CARRIED`."""
    return is_joint_base(base)


def is_window_base(base: Any) -> bool:
    """Whether `base` is one of D-639's window bases (`WINDOW_BASES`)."""
    return isinstance(base, str) and base in WINDOW_BASES


def window_label(base: str) -> str:
    """A window base in words: its stop in points and its window."""
    if not is_window_base(base):
        raise ValueError(f"a window base is one of {tuple(WINDOW_BASES)}, got {base!r}")
    w = WINDOW_BASES[base]
    return f"the {int(w['stop_ticks']) / 4:g}-point coin in the {w['window']} window"


def counted(cell: Mapping[str, Any]) -> bool:
    """Whether a declared cell is a counted family cell: a cell with an override, or a cell on a window base or a
    joint base (each a cell itself, D-639, D-643). A `p16` / `p14` cell with no override is that base's reference and
    is never counted."""
    return bool(cell.get("overrides")) or is_window_base(base_of(cell)) or is_joint_base(base_of(cell))


def coin_design(base: str) -> bool:
    """Whether line (3)(iv) applies to a cell on `base` (a coin design's only; every window base is one, and every
    joint base -- P-16's coin, D-643 (3))."""
    if is_window_base(base) or is_joint_base(base):
        return True
    if base not in BASES:
        raise ValueError(f"a base is one of {BASES}, got {base!r}")
    return bool(BASE_COIN_DESIGN[base])


def override_kinds(base: str = DEFAULT_BASE) -> tuple[str, ...]:
    """The override kinds a cell on `base` may carry (`OVERRIDE_KINDS` less the base's refused kinds; none on a window
    base or a joint base)."""
    if is_window_base(base) or is_joint_base(base):
        return ()
    if base not in BASES:
        raise ValueError(f"a base is one of {BASES}, got {base!r}")
    return tuple(k for k in OVERRIDE_KINDS if k not in BASE_REFUSED_KINDS[base])


# ------------------------------------------------------------------------------------------------ D-639 (2): the R cap


def r_cap(passes: Mapping[float, bool], collect_r: float) -> dict[str, Any]:
    """D-639 (2): the cap a window cell takes. `passes`: {offered R: whether it passes D-212's line -- its unresolved
    share at most 5 % overall and in the worst calendar year} as the caller read it from the cell's resolution columns
    (`scripts/u_family.py`: `atlas_a3.resolution` on that R alone; nothing here reads a profit figure or restates the
    line). `collect_r`: the collect leaf's R.

    `cap`: None when every offered R passes (the cell is run as it is), else the largest R that passes (None too when
    none does). `offered`: the offered R the cell is run with -- every R without a cap, the R at or below the cap with
    one. `failing_below_cap`: the R below the cap that fail (the capped list then does not resolve, and line (3)(iii)
    says so; the walk's unresolved share rises with R, so none is expected). `runnable`: a passing R above the collect
    leaf's exists; `reason` says why not (`NOT_RUNNABLE_NO_R`)."""
    grid = sorted(float(R) for R in passes)
    if not grid:
        raise ValueError("no offered R: the cap needs each offered R's pass or fail")
    ok = [R for R in grid if bool(passes[R])]
    failing = [R for R in grid if not bool(passes[R])]
    top = max(ok) if ok else None
    cap = top if failing else None
    offered = tuple(grid) if not failing else tuple(R for R in grid if top is not None and R <= top)
    runnable = bool(top is not None and top > float(collect_r) + 1e-12)
    return {"cap": cap, "capped": bool(failing), "offered": offered, "passing": tuple(ok), "failing": tuple(failing),
            "failing_below_cap": tuple(R for R in failing if top is not None and R < top),
            "collect_r": float(collect_r), "runnable": runnable, "reason": "" if runnable else NOT_RUNNABLE_NO_R}


def supply_problem(marks: int, candidates: int, days: int) -> str:
    """D-639 (2): "too few marks to offer a trade a session" -- no mark the cutoff admits in the window, or fewer
    offered trades than sessions (under one offered trade a session on average). '' when the supply is enough. Supply
    columns only: the marks offered, the offered trades and the window's sessions."""
    if int(days) < 1:
        raise ValueError("the window holds no session")
    return NOT_RUNNABLE_SUPPLY if (int(marks) < 1 or int(candidates) < int(days)) else ""


def capped_policy_id(policy_id: str, cap: float) -> str:
    """The id of a table whose leaves' R are capped at `cap`: another table than the one it was made from."""
    return f"{policy_id}_rcap{float(cap):g}"


def _capped_node(node: Mapping[str, Any], cap: float, count: list[int]) -> dict[str, Any]:
    t = node.get("type")
    if t == "fixed":
        out = dict(node)
        count[0] += 1
        rr = out.get("rr")
        if rr not in (None, "") and float(rr) > float(cap) + 1e-12:
            out["rr"] = float(cap)
            out["name"] = f"{out.get('name') or 'fixed'} [R {float(rr):g} capped at {float(cap):g}]"
            count[1] += 1
        return out
    if t == "tiers":
        return {**node, "tiers": [{**x, "policy": _capped_node(x["policy"], cap, count)} for x in node["tiers"]]}
    if t == "phase":
        return {**node, **{k: _capped_node(node[k], cap, count) for k in ("combine", "funded", "paid") if node.get(k)}}
    raise ValueError(f"unknown policy node type {t!r}; expected fixed, tiers or phase")


def capped_policy_dict(policy: Mapping[str, Any], cap: float) -> tuple[dict[str, Any], dict[str, int]]:
    """D-639 (2): a risk policy's plain dict (`RiskPolicy.as_dict`) with every leaf asking for an R above `cap` set to
    `cap` -- its dollar risk, its trade limit, its source and the tree around it unchanged; the table is NOT re-solved
    -- and ({leaves, leaves_capped}). Plain data in, plain data out: the caller rebuilds the policy from it
    (`RiskPolicy.from_dict`). A capped leaf's name says so (the name is the regime the engine records); the policy's
    id is `capped_policy_id`'s and its description leads with the cap. A leaf with no R keeps none. A policy wrapped
    in D-390's after-win layer is refused (its brackets are not the table's leaves)."""
    if isinstance(cap, bool) or not isinstance(cap, (int, float)) or not math.isfinite(cap) or not cap > 0:
        raise ValueError(f"a cap is an R above zero, got {cap!r}")
    if "after_win" in policy:
        raise ValueError("the R cap is a transformation of a state table's leaves; an after-win layer is refused")
    count = [0, 0]
    root = _capped_node(policy["root"], float(cap), count)
    out = {**policy, "id": capped_policy_id(str(policy["id"]), cap), "root": root,
           "description": f"D-639 (2): every leaf's R above {float(cap):g} set to {float(cap):g}, its dollar risk "
                          f"unchanged; the table not re-solved -- {policy.get('description', '')}"}
    return out, {"leaves": int(count[0]), "leaves_capped": int(count[1])}


# ------------------------------------------------------------------------------------------------ D-653: the funded plan


def funded_plan_problems(spec: Any) -> list[str]:
    """Every way a `funded_plan` override is not D-653's plain data (an empty list: it is): a dict of `risk` -- the
    dollars a funded trade risks before the first payout, a finite number above zero -- and `rr` -- exactly
    `FUNDED_PLAN_RR` (D-653 (2) fixes R = 1 and drops any other) -- and, optionally, `paid` -- true (the leaf
    replaces the paid phase too) or false (as absent: the paid phase is the base's). No other key."""
    if not isinstance(spec, dict):
        return [f"{FUNDED_PLAN} is a dict of {', '.join(FUNDED_PLAN_KEYS)} (and optionally "
                f"{', '.join(FUNDED_PLAN_OPTIONAL)})"]
    known = (*FUNDED_PLAN_KEYS, *FUNDED_PLAN_OPTIONAL)
    out = [f"{FUNDED_PLAN} key {k!r} is not one of {', '.join(known)}" for k in spec if k not in known]
    out += [f"{FUNDED_PLAN} needs {k}" for k in FUNDED_PLAN_KEYS if k not in spec]
    if "paid" in spec and not isinstance(spec["paid"], bool):
        out.append(f"{FUNDED_PLAN} paid is true (the leaf replaces the paid phase too) or false, nothing else")
    risk, rr = spec.get("risk"), spec.get("rr")
    if "risk" in spec and (isinstance(risk, bool) or not isinstance(risk, (int, float)) or not math.isfinite(risk)
                           or not risk > 0):
        out.append(f"{FUNDED_PLAN} risk is dollars a trade, a finite number above zero")
    if "rr" in spec and (isinstance(rr, bool) or not isinstance(rr, (int, float)) or float(rr) != FUNDED_PLAN_RR):
        out.append(f"{FUNDED_PLAN} rr is exactly {FUNDED_PLAN_RR:g} ({FUNDED_PLAN_DECISION} fixes R = 1 and drops any "
                   "other)")
    return out


def funded_plan_paid(spec: Mapping[str, Any] | None) -> bool:
    """Whether a `funded_plan` override replaces the paid phase too (`"paid": true`)."""
    return bool((spec or {}).get("paid", False))


def funded_plan_policy_id(policy_id: str, risk: float, paid: bool = False) -> str:
    """The id of a table whose funded phase is the plan's one leaf -- `<id>_flat<X>` -- and, with `paid`, whose paid
    phase is too -- `<id>_flat<X>_paid`: each another table than the one it was made from."""
    return f"{policy_id}_flat{float(risk):g}" + ("_paid" if paid else "")


def funded_plan_leaf_name(risk: float, rr: float = FUNDED_PLAN_RR, phase: str = "funded") -> str:
    """The plan's leaf's name in a phase (`funded`, or `paid` where the plan replaces that phase too) -- the regime
    the engine records on every trade the leaf decides."""
    if phase not in ("funded", "paid"):
        raise ValueError(f"the plan's leaf is the funded phase's or the paid phase's, got {phase!r}")
    return f"{phase} flat {_dollars(risk)} {float(rr):g}R"


def _dollars(x: float) -> str:
    return f"${float(x):,.2f}".removesuffix(".00")


def _policy_leaves(node: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
    t = node.get("type")
    if t == "fixed":
        yield node
    elif t == "tiers":
        for x in node["tiers"]:
            yield from _policy_leaves(x["policy"])
    elif t == "phase":
        for k in ("combine", "funded", "paid"):
            if node.get(k):
                yield from _policy_leaves(node[k])
    else:
        raise ValueError(f"unknown policy node type {t!r}; expected fixed, tiers or phase")


def _phase_limit(leaves: Sequence[Mapping[str, Any]], phase: str) -> Any:
    """The trade limit a phase's TRADING leaves carry in common, after refusing what the plan's one leaf could not
    stand for: a phase that trades in no state, abandons accounts, holds flip or collect leaves, or sets no common
    limit."""
    trading = [x for x in leaves if x.get("max_trades") != 0]
    if not trading:
        raise ValueError(f"the base's {phase} phase trades in no state")
    if any(x.get("abandon") for x in leaves):
        raise ValueError(f"the base's {phase} phase abandons accounts: the plan's one leaf would not")
    if any(str(x.get("source") or "strategy") != "strategy" for x in trading):
        raise ValueError(f"the base's {phase} phase holds flip or collect leaves: the plan is routed strategy trades "
                         "only")
    limits = {x.get("max_trades") for x in trading}
    if len(limits) != 1:
        raise ValueError(f"the base's {phase} trading leaves carry different trade limits "
                         f"({sorted(map(str, limits))})")
    return limits.pop()


def funded_plan_policy_dict(policy: Mapping[str, Any], risk: float, rr: float = FUNDED_PLAN_RR, paid: bool = False
                            ) -> tuple[dict[str, Any], dict[str, Any]]:
    """D-653 (1): a risk policy's plain dict (`RiskPolicy.as_dict`) with its FUNDED phase -- a funded account from
    activation to its first payout -- replaced by ONE leaf: `risk` dollars at `rr`, a routed strategy trade, with the
    trade limit the base's funded TRADING leaves carry (they must agree: "one trade an account a session as now"). The
    evaluation's subtree and the paid phase's subtree are the base's own, untouched; a base whose paid phase defaults
    to its funded one (no `paid` subtree) gets that funded subtree as its explicit `paid`, so the phase after a first
    payout is still the base's. The table is NOT re-solved. Plain data in, plain data out: the caller rebuilds the
    policy from it (`RiskPolicy.from_dict`).

    The base's funded phase may hold no-trade leaves (`max_trades` 0: the states its solver sits out); the plan's one
    leaf trades in every funded state -- (`funded_leaves`, `funded_no_trade_leaves`) say how many leaves it replaces.
    A payout request is not a leaf's: the engine requests at the close an account is eligible (the protocol's payout
    fields), so replacing the phase removes none. The policy's id is `funded_plan_policy_id`'s, the leaf's name
    `funded_plan_leaf_name`'s (the name is the regime the engine records) and the description leads with the plan.

    `paid` (D-653 as amended before its run; the override's `"paid": true`): the PAID phase -- a funded account after
    its first payout -- is replaced too, by the same leaf under the paid phase's name (the same dollars, R and trade
    limit): one trade a session in every paid state, the request day and the base's no-trade states included
    (`paid_leaves`, `paid_no_trade_leaves`: what it replaces). The evaluation's subtree is still the base's own. The
    base's paid trading leaves must carry the funded ones' trade limit.

    REFUSED (ValueError): a spec that is not D-653's (`funded_plan_problems`); a root that is not a phase node; D-390's
    after-win layer; a funded phase (with `paid`, a paid phase) whose trading leaves are not all routed strategy
    trades, set no common trade limit, or abandon -- each would make "the base's funded phase with one size and one
    R" mean something else."""
    bad = funded_plan_problems({"risk": risk, "rr": rr, "paid": paid})
    if bad:
        raise ValueError("; ".join(bad))
    if "after_win" in policy:
        raise ValueError("the funded plan replaces a state table's funded phase; an after-win layer is refused")
    root = policy["root"]
    if root.get("type") != "phase" or not root.get("funded") or not root.get("combine"):
        raise ValueError("the funded plan replaces the funded phase of a phase node: the table's root is not one")
    was = list(_policy_leaves(root["funded"]))
    limit = _phase_limit(was, "funded")
    base_paid = root.get("paid") or root["funded"]
    was_paid = list(_policy_leaves(base_paid))
    if paid and _phase_limit(was_paid, "paid") != limit:
        raise ValueError("the base's paid trading leaves carry another trade limit than its funded ones")

    def leaf(phase: str) -> dict[str, Any]:
        d: dict[str, Any] = {"type": "fixed", "name": funded_plan_leaf_name(risk, rr, phase), "risk": float(risk),
                             "rr": float(rr)}
        if limit is not None:
            d["max_trades"] = int(limit)
        return d

    out = {**policy, "id": funded_plan_policy_id(str(policy["id"]), risk, paid),
           "root": {**root, "funded": leaf("funded"), "paid": leaf("paid") if paid else base_paid},
           "description": f"{FUNDED_PLAN_DECISION} (1): the funded phase (activation to the first payout) "
                          + ("and the paid phase (after a first payout) each " if paid else "")
                          + f"replaced by one leaf -- {_dollars(risk)} at {float(rr):g}R, "
                          + ("the protocol's trade limit" if limit is None else f"{int(limit)} trade(s) a session")
                          + ("; the evaluation's leaves the base's" if paid else
                             "; the evaluation's and the paid phase's leaves the base's")
                          + "; the table not re-solved -- " + str(policy.get("description", ""))}
    return out, {"funded_leaves": len(was), "funded_no_trade_leaves": sum(x.get("max_trades") == 0 for x in was),
                 "max_trades": None if limit is None else int(limit), "paid_was_explicit": bool(root.get("paid")),
                 "paid_replaced": bool(paid), "paid_leaves": len(was_paid) if paid else 0,
                 "paid_no_trade_leaves": sum(x.get("max_trades") == 0 for x in was_paid) if paid else 0}


def funded_plan_dict_problems(base: Mapping[str, Any], plan: Mapping[str, Any], risk: float,
                              rr: float = FUNDED_PLAN_RR, paid: bool = False) -> list[str]:
    """Every way `plan` (a policy's plain dict) is not `base` with its funded phase replaced by D-653's one leaf and
    nothing else changed: the evaluation's subtree equal to the base's; the paid subtree equal to the base's paid
    phase (its funded subtree where the base names no `paid`) -- or, with `paid`, exactly the plan's one leaf under
    the paid phase's name; the funded phase exactly one trading leaf at `risk` and `rr` -- a routed strategy trade,
    never abandon, never a no-trade state; the version the base's and the id `funded_plan_policy_id`'s."""
    out = []
    a, b = base["root"], plan["root"]
    if b.get("type") != "phase" or a.get("type") != "phase":
        return ["the table's root is not a phase node"]
    if b.get("combine") != a.get("combine"):
        out.append("the evaluation's leaves are not the base's")

    def one_leaf(f: Mapping[str, Any], phase: str) -> bool:
        return bool(f.get("type") == "fixed" and float(f.get("risk", float("nan"))) == float(risk)
                    and f.get("rr") is not None and float(f["rr"]) == float(rr) and f.get("max_trades") != 0
                    and not f.get("abandon") and str(f.get("source") or "strategy") == "strategy"
                    and f.get("name") == funded_plan_leaf_name(risk, rr, phase))

    if paid:
        if not one_leaf(b.get("paid") or {}, "paid"):
            out.append(f"the paid phase is not one trading leaf at {_dollars(risk)} and {float(rr):g}R")
        elif b["paid"].get("max_trades") != (b.get("funded") or {}).get("max_trades"):
            out.append("the paid leaf's trade limit is not the funded leaf's")
    elif b.get("paid") != (a.get("paid") or a.get("funded")):
        out.append("the paid phase's leaves are not the base's")
    if not one_leaf(b.get("funded") or {}, "funded"):
        out.append(f"the funded phase is not one trading leaf at {_dollars(risk)} and {float(rr):g}R")
    if set(b) - {"type", "name", "combine", "funded", "paid"} or b.get("name") != a.get("name"):
        out.append("the root carries another name or another key")
    if str(plan.get("id")) != funded_plan_policy_id(str(base.get("id")), risk, paid):
        out.append("the table's id is not u_select.funded_plan_policy_id's")
    if int(plan.get("version", 1)) != int(base.get("version", 1)):
        out.append("the table's version is not the base's")
    return out


# ---------------------------------------------------------------------------------------------- D-659: resolved at once


def funded_resolve_problems(spec: Any) -> list[str]:
    """Every way a `funded_resolve` override is not D-659's plain data (an empty list: it is): a dict of `rr` alone --
    the bold leaf's R, a finite number above zero (D-659 (2) searches 1.5 and 3; whether the base's blocks carry an
    edge and a bound at it is the runner's check, `scripts/u_family.py`'s `apply_overrides`) -- and, optionally,
    `lowest` (`FUNDED_RESOLVE_LOWEST`; absent: `micro`, D-659's own text). No other key: the risk is the room, fixed by
    D-659 (1), never a parameter."""
    if not isinstance(spec, dict):
        return [f"{FUNDED_RESOLVE} is a dict of {', '.join(FUNDED_RESOLVE_KEYS)} (and optionally "
                f"{', '.join(FUNDED_RESOLVE_OPTIONAL)})"]
    known = (*FUNDED_RESOLVE_KEYS, *FUNDED_RESOLVE_OPTIONAL)
    out = [f"{FUNDED_RESOLVE} key {k!r} is not one of {', '.join(known)}" for k in spec if k not in known]
    out += [f"{FUNDED_RESOLVE} needs {k}" for k in FUNDED_RESOLVE_KEYS if k not in spec]
    if "lowest" in spec and (not isinstance(spec["lowest"], str) or spec["lowest"] not in FUNDED_RESOLVE_LOWEST):
        out.append(f"{FUNDED_RESOLVE} lowest is one of {', '.join(FUNDED_RESOLVE_LOWEST)} (micro: "
                   f"{FUNDED_RESOLVE_DECISION}'s own text, the default)")
    rr = spec.get("rr")
    if "rr" in spec and (isinstance(rr, bool) or not isinstance(rr, (int, float)) or not math.isfinite(rr)
                         or not rr > 0):
        out.append(f"{FUNDED_RESOLVE} rr is the bold leaf's R, a finite number above zero")
    return out


def funded_resolve_lowest(spec: Mapping[str, Any] | None) -> str:
    """A `funded_resolve` override's `lowest` (`micro`, D-659's own text, when absent)."""
    return str((spec or {}).get("lowest", FUNDED_RESOLVE_LOWEST[0]))


def funded_resolve_policy_id(policy_id: str, rr: float, min_risk: float, lowest: str = "micro") -> str:
    """The id of a table whose funded states below the starting balance are D-659's bold leaves at `rr`, the least
    risk `min_risk` dollars -- `<id>_resolve<r>R_min<dollars>`: another table than the one it was made from, and
    another for each R and each base's one-micro dollars; `_lowbase` where the band under one micro is left to the
    base (`lowest` `base`)."""
    return f"{policy_id}_resolve{float(rr):g}R_min{float(min_risk):g}" + ("_lowbase" if lowest == "base" else "")


def funded_resolve_risk(band_from: float, min_risk: float) -> float:
    """D-659 (1): the bold leaf's dollars in the cushion band that starts at `band_from` -- the band's LOWER edge, so
    never more than the room of any state in the band, and never less than `min_risk` (one micro at the base's stop).
    Only where the edge is under `min_risk` (the lowest band, whose edge is zero) can the leaf ask for more than the
    room: with a room under one micro's dollars the trade is still one micro."""
    return float(max(float(band_from), float(min_risk)))


def funded_resolve_leaf_name(risk: float, rr: float) -> str:
    """A bold leaf's name -- the regime the engine records on every trade it decides."""
    return f"funded resolve {_dollars(risk)} {float(rr):g}R"


def _min_risk_problem(min_risk: Any) -> str:
    if isinstance(min_risk, bool) or not isinstance(min_risk, (int, float)) or not math.isfinite(min_risk) or (
            not min_risk > 0):
        return "min_risk is one micro's dollars at the base's stop, a finite number above zero"
    return ""


def funded_resolve_policy_dict(policy: Mapping[str, Any], rr: float, min_risk: float, lowest: str = "micro"
                               ) -> tuple[dict[str, Any], dict[str, Any]]:
    """D-659 (1): a risk policy's plain dict (`RiskPolicy.as_dict`) with, in its FUNDED phase -- a funded account from
    activation to its first payout -- every state whose balance is BELOW the account's starting balance decided by a
    bold leaf, and (what it replaced).

    **How it is built.** The funded phase of the table is a tier node on `balance` (`Tiers`: a state takes the LAST
    tier whose `from` is at or below its value -- a band is [from, the next from) -- and the first tier below them
    all), and under each balance band a tier node on `cushion` (the dollars above the trailing loss limit: the room).
    The node on `balance` keeps its name and every threshold. **Each band whose `from` is at or above
    `FUNDED_RESOLVE_START` (zero) keeps the base's own subtree -- the same object, untouched**: an account at exactly
    its starting balance, the fresh account among them, is decided by the base (its opening). **Each band whose `from`
    is below zero** keeps its node on `cushion` -- its name and thresholds, the table's own cushion grid -- and under
    each cushion band the base's subtree (its leaves by the request day and the winning days) is replaced by ONE leaf:
    `funded_resolve_risk(from, min_risk)` dollars -- the band's lower edge, never less than `min_risk` -- at `rr`,
    `FUNDED_RESOLVE_TRADES` routed strategy trade a session, named `funded_resolve_leaf_name`. The evaluation's
    subtree and the paid phase's are the base's own; a base whose paid phase defaults to its funded one (no `paid`)
    gets its own funded subtree as the explicit `paid`, so the phase after a first payout is still the base's. The
    table is NOT re-solved. Plain data in, plain data out (`RiskPolicy.from_dict` rebuilds it).

    `lowest` (`FUNDED_RESOLVE_LOWEST`): `micro` -- D-659's own text and the default -- writes the bold leaf at
    `min_risk` in a cushion band whose lower edge is under it; `base` (not D-659's text: an amendment's) leaves the
    base's own subtree in such a band, the same object.

    The record: `balance_bands` (the bands replaced, their `from`), `cushion_bands` ({the band's lower edge: the leaf's
    dollars}, over every replaced balance band), `floored_bands` (the cushion bands whose leaf is `min_risk`, above the
    band's lower edge: there a room under `min_risk` is risked beyond), `base_bands` (the cushion bands left to the
    base, `lowest` `base`), `replaced_leaves` and `replaced_no_trade_leaves` (the base's leaves the bold leaves stand
    in for), `leaves` (the bold leaves written).

    REFUSED (ValueError): a spec that is not D-659's; a `min_risk` that is not dollars above zero; D-390's after-win
    layer; a root that is not a phase node; a funded phase that is not a tier node on `balance` with a band starting
    exactly at the starting balance and at least one below it (the boundary would not be exact); a band below it that
    is not a tier node on `cushion` whose first band starts at zero (a room under the first edge would be risked
    beyond); a replaced state that abandons, or holds a flip or collect leaf; trading leaves there that do not carry
    the one-trade limit D-659 declares."""
    bad = funded_resolve_problems({"rr": rr, "lowest": lowest}) + [x for x in (_min_risk_problem(min_risk),) if x]
    if bad:
        raise ValueError("; ".join(bad))
    if "after_win" in policy:
        raise ValueError("the resolve plan replaces a state table's funded leaves; an after-win layer is refused")
    root = policy["root"]
    if root.get("type") != "phase" or not root.get("funded") or not root.get("combine"):
        raise ValueError("the resolve plan replaces funded leaves of a phase node: the table's root is not one")
    funded = root["funded"]
    if funded.get("type") != "tiers" or funded.get("on") != "balance":
        raise ValueError("the base's funded phase is not a tier node on balance: the states below the starting "
                         "balance cannot be told apart exactly")
    froms = [float(x["from"]) for x in funded["tiers"]]
    if FUNDED_RESOLVE_START not in froms or not any(f < FUNDED_RESOLVE_START for f in froms):
        raise ValueError("the base's funded balance bands do not start one exactly at the starting balance (0) with "
                         "a band below it: the boundary would not be exact")
    tiers, bands, cushions, leaves = [], [], {}, 0
    kept: set[float] = set()
    was: list[Mapping[str, Any]] = []
    for x in funded["tiers"]:
        if float(x["from"]) >= FUNDED_RESOLVE_START:
            tiers.append(x)                                 # the base's own tier: the same object
            continue
        node = x["policy"]
        if node.get("type") != "tiers" or node.get("on") != "cushion" or float(node["tiers"][0]["from"]) != 0.0:
            raise ValueError(f"the base's funded balance band from {float(x['from']):g} is not a tier node on cushion "
                             "whose first band starts at zero: a bold leaf could ask for more than the room")
        inner = []
        for y in node["tiers"]:
            if lowest == "base" and float(y["from"]) < float(min_risk):
                inner.append(y)                             # the base's own subtree in the band under one micro
                kept.add(float(y["from"]))
                continue
            was += list(_policy_leaves(y["policy"]))
            risk = funded_resolve_risk(float(y["from"]), min_risk)
            cushions[float(y["from"])] = risk
            inner.append({**y, "policy": {"type": "fixed", "name": funded_resolve_leaf_name(risk, rr), "risk": risk,
                                          "rr": float(rr), "max_trades": FUNDED_RESOLVE_TRADES}})
            leaves += 1
        tiers.append({**x, "policy": {**node, "tiers": inner}})
        bands.append(float(x["from"]))
    if any(x.get("abandon") for x in was):
        raise ValueError("the base's funded states below the starting balance abandon accounts: a bold leaf would not")
    trading = [x for x in was if x.get("max_trades") != 0]
    if any(str(x.get("source") or "strategy") != "strategy" for x in trading):
        raise ValueError("the base's funded states below the starting balance hold flip or collect leaves: the bold "
                         "leaf is a routed strategy trade")
    if any(x.get("max_trades") != FUNDED_RESOLVE_TRADES for x in trading):
        raise ValueError("the base's funded trading leaves below the starting balance do not carry the limit of "
                         f"{FUNDED_RESOLVE_TRADES} trade a session {FUNDED_RESOLVE_DECISION} (1) declares")
    if not leaves:
        raise ValueError("no state below the starting balance is left to a bold leaf")
    out = {**policy, "id": funded_resolve_policy_id(str(policy["id"]), rr, min_risk, lowest),
           "root": {**root, "funded": {**funded, "tiers": tiers}, "paid": root.get("paid") or root["funded"]},
           "description": f"{FUNDED_RESOLVE_DECISION} (1): in the funded phase (activation to the first payout) every "
                          "state whose balance is below the starting balance risks its room -- the cushion band's "
                          "lower edge, "
                          + (f"never less than {_dollars(min_risk)} (one micro at the base's stop)" if lowest != "base"
                             else f"a band whose edge is under {_dollars(min_risk)} (one micro at the base's stop) "
                                  "left to the base's own leaves")
                          + f" -- at {float(rr):g}R, {FUNDED_RESOLVE_TRADES} trade a session; the states at or above "
                          "the starting balance, the paid phase's leaves and the evaluation's the base's; the table not "
                          "re-solved -- " + str(policy.get("description", ""))}
    return out, {"balance_bands": bands, "cushion_bands": dict(sorted(cushions.items())),
                 "floored_bands": sorted(c for c, r in cushions.items() if r > c), "base_bands": sorted(kept),
                 "lowest": str(lowest), "min_risk": float(min_risk),
                 "replaced_leaves": len(was), "replaced_no_trade_leaves": sum(x.get("max_trades") == 0 for x in was),
                 "leaves": int(leaves), "max_trades": FUNDED_RESOLVE_TRADES, "paid_was_explicit": bool(root.get("paid"))}


def funded_resolve_dict_problems(base: Mapping[str, Any], table: Mapping[str, Any], rr: float, min_risk: float,
                                 lowest: str = "micro") -> list[str]:
    """Every way `table` (a policy's plain dict) is not `base` with D-659's bold leaves below the starting balance and
    nothing else changed: the evaluation's subtree equal to the base's; the paid subtree equal to the base's paid
    phase (its funded subtree where the base names no `paid`); the funded phase a tier node on `balance` with the
    base's name and thresholds, **every band at or above the starting balance equal to the base's**, every band below
    it a tier node on `cushion` with the base's name and thresholds whose every band is one leaf -- the band's lower
    edge and never less than `min_risk`, at `rr`, one routed strategy trade, never abandon, never a no-trade state
    (with `lowest` `base`, a band whose lower edge is under `min_risk` equal to the base's instead) -- the version the
    base's and the id `funded_resolve_policy_id`'s."""
    a, b = base["root"], table["root"]
    if b.get("type") != "phase" or a.get("type") != "phase":
        return ["the table's root is not a phase node"]
    out = []
    if b.get("combine") != a.get("combine"):
        out.append("the evaluation's leaves are not the base's")
    if b.get("paid") != (a.get("paid") or a.get("funded")):
        out.append("the paid phase's leaves are not the base's")
    fa, fb = a.get("funded") or {}, b.get("funded") or {}
    same_grid = (fa.get("type") == fb.get("type") == "tiers" and fa.get("on") == fb.get("on") == "balance"
                 and fa.get("name") == fb.get("name") and set(fb) == {"type", "on", "name", "tiers"}
                 and [float(x["from"]) for x in fa["tiers"]] == [float(x["from"]) for x in fb["tiers"]])
    if not same_grid:
        out.append("the funded phase is not a tier node on the base's balance bands")
    else:
        if FUNDED_RESOLVE_START not in [float(x["from"]) for x in fb["tiers"]]:
            out.append("no funded balance band starts at the starting balance")
        for x, y in zip(fa["tiers"], fb["tiers"]):
            if float(x["from"]) >= FUNDED_RESOLVE_START:
                if y != x:
                    out.append("a funded band at or above the starting balance is not the base's")
                    break
                continue
            na, nb = x["policy"], y["policy"]
            grid = (na.get("type") == nb.get("type") == "tiers" and na.get("on") == nb.get("on") == "cushion"
                    and na.get("name") == nb.get("name") and set(y) == {"from", "policy"}
                    and [float(t["from"]) for t in na["tiers"]] == [float(t["from"]) for t in nb["tiers"]])
            if not grid:
                out.append("a funded band below the starting balance is not on the base's cushion bands")
                break
            wrong = False
            for t0, t in zip(na["tiers"], nb["tiers"]):
                if lowest == "base" and float(t["from"]) < float(min_risk):
                    wrong = wrong or t != t0
                    continue
                f, risk = t["policy"], funded_resolve_risk(float(t["from"]), min_risk)
                if not (f.get("type") == "fixed" and float(f.get("risk", float("nan"))) == risk
                        and f.get("rr") is not None and float(f["rr"]) == float(rr)
                        and f.get("max_trades") == FUNDED_RESOLVE_TRADES and not f.get("abandon")
                        and str(f.get("source") or "strategy") == "strategy"
                        and f.get("name") == funded_resolve_leaf_name(risk, rr)):
                    wrong = True
            if wrong:
                out.append("a funded state below the starting balance is not the bold leaf: its cushion band's lower "
                           f"edge, never less than {_dollars(min_risk)}, at {float(rr):g}R, one trade a session")
                break
    if set(b) - {"type", "name", "combine", "funded", "paid"} or b.get("name") != a.get("name"):
        out.append("the root carries another name or another key")
    if str(table.get("id")) != funded_resolve_policy_id(str(base.get("id")), rr, min_risk, lowest):
        out.append("the table's id is not u_select.funded_resolve_policy_id's")
    if int(table.get("version", 1)) != int(base.get("version", 1)):
        out.append("the table's version is not the base's")
    return out


def family_id(decision: str, family: str) -> str:
    """The id every cell of a family is counted under: `<row id>:u_<family>`."""
    if not DECISION_ID.match(str(decision)) or not FAMILY_NAME.match(str(family)):
        raise ValueError(f"a family is a decision row id (D-nnn) and a lower-case name, got {decision!r}, {family!r}")
    return f"{decision}:u_{family}"


def result_name(family: str) -> str:
    if not FAMILY_NAME.match(str(family)):
        raise ValueError(f"a family's name is lower-case letters, digits and underscores, got {family!r}")
    return f"u_{family}"


def _plain(x: Any) -> bool:
    if x is None or isinstance(x, (bool, int, float, str)):
        return True
    if isinstance(x, (tuple, list)):
        return all(_plain(v) for v in x)
    if isinstance(x, dict):
        return all(isinstance(k, str) and _plain(v) for k, v in x.items())
    return False


def _whole(x: Any) -> bool:
    return isinstance(x, int) and not isinstance(x, bool) and x >= 1


def override_problems(overrides: Any, base: str = DEFAULT_BASE) -> list[str]:
    """Every way a cell's overrides are not the plain data `scripts/u_family.py` applies (an empty list: they are):
    the three seat keys together, each a whole number; `purchase_budget` None (no budget) or (K, window); `
    funded_cap_share` in (0, 1]; `protocol` a dict of `PROTOCOL_FIELDS`; `payout_timing` a name; D-630's entry options
    (`ENTRY_KINDS`) -- `wallet_stop` dollars above zero, `pause_after_funded` a whole number from 1, `seat_ramp` a
    whole number from 1 and below the cell's seats (its `total_accounts` when it overrides the seat keys, else the
    base's, `BASE_SEATS`: a ramp that starts at the seats is the base itself); D-653's `funded_plan`
    (`funded_plan_problems`: `risk` dollars above zero, `rr` exactly 1, optionally `paid` true or false; never with
    `funded_cap_share`); D-659's `funded_resolve` (`funded_resolve_problems`: `rr` above zero, optionally `lowest`,
    no other key; never with `funded_plan` or `funded_cap_share`, `FUNDED_RESOLVE_REFUSED_WITH`). Nothing
    callable, no object. `base`: the
    base the overrides are put on -- a kind refused there (`BASE_REFUSED_KINDS`) is a problem; the default base
    refuses none; a window base (`WINDOW_BASES`, D-639) takes no override at all, nor does a joint base (`JOINT_BASES`,
    D-643)."""
    if not isinstance(base, str) or base not in EVERY_BASE:
        return [f"the base {base!r} is not one of {', '.join(BASES)}"]      # the override bases; the words are pinned
    if not isinstance(overrides, dict):
        return ["the overrides are not a dict"]
    if is_window_base(base):                                # D-639: a window base is a cell itself
        return ([f"base {base}: {WINDOW_NO_OVERRIDE} (given: {', '.join(sorted(map(str, overrides)))})"]
                if overrides else [])
    if is_joint_base(base):                                 # D-643: so is a joint base
        return ([f"base {base}: {JOINT_NO_OVERRIDE} (given: {', '.join(sorted(map(str, overrides)))})"]
                if overrides else [])
    out = [f"{k!r} is not an override kind ({', '.join(OVERRIDE_KINDS)})" for k in overrides if k not in OVERRIDE_KINDS]
    out += [f"{k} is not an override on base {base}: {why}" for k, why in BASE_REFUSED_KINDS[base].items()
            if k in overrides]
    if not _plain(overrides):
        out.append("the overrides are not plain data (numbers, text, tuples, dicts)")
    seats = [k for k in SEAT_KEYS if k in overrides]
    if seats and len(seats) != len(SEAT_KEYS):
        out.append(f"the seat keys change together: {', '.join(SEAT_KEYS)} (given: {', '.join(seats)})")
    out += [f"{k} is not a whole number from 1" for k in seats if not _whole(overrides[k])]
    if "purchase_budget" in overrides and overrides["purchase_budget"] is not None:
        b = overrides["purchase_budget"]
        if not (isinstance(b, (tuple, list)) and len(b) == 2 and all(_whole(v) for v in b)):
            out.append("purchase_budget is None or (K, window), two whole numbers from 1")
    if "funded_cap_share" in overrides:
        s = overrides["funded_cap_share"]
        if isinstance(s, bool) or not isinstance(s, (int, float)) or not 0.0 < float(s) <= 1.0:
            out.append("funded_cap_share is a share in (0, 1]")
    if "protocol" in overrides:
        p = overrides["protocol"]
        if not isinstance(p, dict) or not p:
            out.append("protocol is a non-empty dict of " + ", ".join(PROTOCOL_FIELDS))
        else:
            out += [f"protocol field {k!r} is not one of {', '.join(PROTOCOL_FIELDS)}" for k in p
                    if k not in PROTOCOL_FIELDS]
            kb, pf, pp = p.get("keep_balance"), p.get("payout_frac"), p.get("payout_path")
            if kb is not None and (isinstance(kb, bool) or not isinstance(kb, (int, float)) or kb < 0):
                out.append("protocol keep_balance is dollars, zero or more")
            if pf is not None and (isinstance(pf, bool) or not isinstance(pf, (int, float)) or not 0.0 < pf <= 1.0):
                out.append("protocol payout_frac is a share in (0, 1]")
            if pp is not None and pp not in PAYOUT_PATHS:
                out.append(f"protocol payout_path is one of {PAYOUT_PATHS}")
    if "payout_timing" in overrides and not isinstance(overrides["payout_timing"], str):
        out.append("payout_timing is a name")
    if FUNDED_PLAN in overrides:                            # D-653: one leaf, X dollars at 1R
        out += funded_plan_problems(overrides[FUNDED_PLAN])
        out += [f"{FUNDED_PLAN} with {k} is not a cell: {why}" for k, why in FUNDED_PLAN_REFUSED_WITH.items()
                if k in overrides]
    if FUNDED_RESOLVE in overrides:                         # D-659: the bold leaf below the starting balance
        out += funded_resolve_problems(overrides[FUNDED_RESOLVE])
        out += [f"{FUNDED_RESOLVE} with {k} is not a cell: {why}" for k, why in FUNDED_RESOLVE_REFUSED_WITH.items()
                if k in overrides]
    if "wallet_stop" in overrides:
        w = overrides["wallet_stop"]
        if isinstance(w, bool) or not isinstance(w, (int, float)) or not math.isfinite(w) or not w > 0:
            out.append("wallet_stop is dollars, a finite number above zero")
    if "pause_after_funded" in overrides and not _whole(overrides["pause_after_funded"]):
        out.append("pause_after_funded is a whole number from 1")
    if "seat_ramp" in overrides:
        total = overrides.get("total_accounts")
        seats = int(total) if _whole(total) else int(BASE_SEATS[base])
        if not _whole(overrides["seat_ramp"]) or int(overrides["seat_ramp"]) >= seats:
            out.append(f"seat_ramp is a whole number from 1 and below the cell's seats ({seats})")
    return out


def family_problems(entry: Any) -> list[str]:
    """Every way a registry entry is not a family (an empty list: it is): `family` (its name), `decision` (the row
    that declared it), `k` (its number in the order declared), `cells` -- each a `name`, its `overrides`
    (`override_problems`, on its base), and optionally `base` (one of `BASES`; `p16` when absent -- a family may mix
    bases), `rules` (the ledger's names of the firm rules its overrides lean on beyond its base's own) and `equals_u1`
    (a configuration of U1's file the cell must equal start for start). A cell's name is never one of U1's
    configurations (the rows to beat are reported under theirs), and a base's cell with no override -- the base itself
    -- is named that base's reference (`REFERENCE_CELLS`: `REFERENCE_CELL` for P-16) and no other cell carries a
    reference's name. **A cell on a window base** (`WINDOW_BASES`, D-639) is the base itself: no override, any name
    that is not a reference's, counted (`counted`), and a family names a window base at most once. **A cell on a joint
    base** (`JOINT_BASES`, D-643) likewise: the base itself, no override, counted, named at most once."""
    if not isinstance(entry, dict):
        return ["a family is a dict"]
    out = []
    if not FAMILY_NAME.match(str(entry.get("family", ""))):
        out.append("family: a lower-case name (letters, digits, underscores)")
    if not DECISION_ID.match(str(entry.get("decision", ""))):
        out.append("decision: the id of the row that declared the family (D-nnn)")
    if not _whole(entry.get("k")):
        out.append("k: the family's number in the order declared, a whole number from 1")
    cells = entry.get("cells")
    if not isinstance(cells, (tuple, list)) or not cells:
        return out + ["cells: at least one"]
    names = []
    windows: set[str] = set()
    for i, c in enumerate(cells):
        if not isinstance(c, dict) or not CELL_NAME.match(str(c.get("name", ""))):
            out.append(f"cell {i}: no name")
            continue
        names.append(c["name"])
        base = c.get("base", DEFAULT_BASE)
        if not isinstance(base, str) or base not in EVERY_BASE:
            out.append(f"cell {c['name']}: base is one of {', '.join(EVERY_BASE)}")
            base = DEFAULT_BASE
        out += [f"cell {c['name']}: {p}" for p in override_problems(c.get("overrides"), base)]
        if c["name"] in U.CONFIGS:
            out.append(f"cell {c['name']}: the name is one of U1's configurations")
        if is_window_base(base):                            # D-639: the base itself, counted; named at most once
            if c["name"] in REFERENCE_CELLS.values():
                out.append(f"cell {c['name']}: a cell on a window base is a counted cell, never a reference")
            if base in windows:
                out.append(f"cell {c['name']}: the window base {base} is named twice (it takes no override: one cell)")
            windows.add(base)
        elif is_joint_base(base):                           # D-643: the base itself, counted; named at most once
            if c["name"] in REFERENCE_CELLS.values():
                out.append(f"cell {c['name']}: a cell on a joint base is a counted cell, never a reference")
            if base in windows:
                out.append(f"cell {c['name']}: the joint base {base} is named twice (it takes no override: one cell)")
            windows.add(base)
        elif isinstance(c.get("overrides"), dict) and (
                (c["name"] == REFERENCE_CELLS[base]) != (not c["overrides"])
                or (bool(c["overrides"]) and c["name"] in REFERENCE_CELLS.values())):
            out.append(f"cell {c['name']}: the cell with no override, and only it, is named "
                       f"{REFERENCE_CELLS[base]!r}")
        extra = sorted(set(c) - {"name", "base", "overrides", "rules", "equals_u1"})
        if extra:
            out.append(f"cell {c['name']}: unknown keys {extra}")
        rules = c.get("rules", ())
        if not isinstance(rules, (tuple, list)) or not all(isinstance(r, str) and r for r in rules):
            out.append(f"cell {c['name']}: rules is a tuple of the ledger's rule names")
        if c.get("equals_u1") is not None and c["equals_u1"] not in U.CONFIGS:
            out.append(f"cell {c['name']}: equals_u1 is one of U1's configurations")
    if len(set(names)) != len(names):
        out.append("the cells' names are not distinct")
    return out


def program_count(variants: Iterable[Mapping[str, Any]], family: str | None = None) -> dict[str, Any]:
    """The program's running count of cells (D-621 (5)) from the variant ledger's rows (`VariantCounter.all()`): the
    distinct cells recorded under any lever family's id (`<row id>:u_<family>`), in all and by family; `family`: one
    id's count. A family's hypothetical cells (D-644 (4): recorded under `<row id>:hypothetical_hedge`) count with the
    lever family the same row declared; a `hypothetical_hedge` id of a row with no lever family is not the program's."""
    by: dict[str, set[str]] = {}
    hypo: dict[str, set[str]] = {}
    for r in variants:
        pid = str(r.get("prereg_id", ""))
        if PROGRAM_ID.match(pid):
            by.setdefault(pid, set()).add(str(r.get("variant_id", "")))
        elif HYPOTHETICAL_ID.match(pid):
            hypo.setdefault(pid.split(":")[0], set()).add(str(r.get("variant_id", "")))
    # D-644 (4): a lever family's hypothetical cells (`<row id>:hypothetical_hedge`) are counted with the family the
    # same row declared -- one family, not two; an id of a row that declared no lever family is another study's
    for decision, ids in hypo.items():
        own = [pid for pid in by if pid.split(":")[0] == decision]
        if len(own) == 1:
            by[own[0]] |= ids
    return {"program": int(sum(len(v) for v in by.values())), "families": len(by),
            "by_family": {k: len(v) for k, v in sorted(by.items())},
            "family": int(len(by.get(str(family), ()))) if family is not None else 0}


# ------------------------------------------------------------------------------------------------ the declaration

#: DECISIONS.md's D-621 row (LF, the line itself): its sha256 and the phrases this module's constants rest on
DECLARATION_SHA256 = "0c7a89b6c4e42c5623e1a0e4f69d1af5b4d91fbfcf1ec9913ea35d4c7a50f4df"
D621_WORDS = (
    f"every measure one of D-620 (3)(e)'s readings, the `{ARM}` arm, the replay over every start day",
    "the primary **P** -- the mean of the shares of units ahead at months 1, 2 and 3",
    "guarded -- S1 cash spent before the first payout p90, S3a the share paid by session 21, S3b sessions to the first "
    "payout p90, S3c payouts per dollar of fees at month 3 pooled, S4a and S4b the shares ahead at months 6 and 12, "
    "S5a the month-3 net's p10, S5b the longest gap after the first payout within 126 sessions p90, S5c the "
    "concentration at month 6",
    "Eligible: the registered development PASSes that lean on no unverified rule -- P-14, P-15, P-16",
    "On each measure the row to beat is the best of the three in U1's file; **R*** is the row to beat on P",
    f"A cell is {CARRIED} only if, on the judged block of start days",
    "(i) its paired difference in P from R* on the same start days is above zero with the moving-block bootstrap "
    f"interval (D-620 G2: blocks of {BOOT_BLOCK} sessions, seed {U.BOOT_SEED}, 2,000 draws) excluding zero at the "
    "family's level of (5)",
    "(ii) on no guarded measure is it worse than R* by more than the tolerance -- five percentage points on a share, "
    "ten per cent on dollars, sessions and ratios",
    f"(iii) the gate stays a floor: at a campaign seed never used before ({GATE_SEED}, {GATE_PATHS} paths) its growth "
    f"on the required bankroll at the bound is above zero and above {GATE_ROW_TO_BEAT}'s row",
    "every offered R resolves (D-212) and every firm rule it uses is verified",
    f"(iv) a coin design also beats R* on P under at least {COIN_WINS_NEEDED} of D-568's {len(COIN_SEQUENCES)} coin "
    f"sequences ({COIN_SEQUENCES[0]} + i), each read on every {COIN_EVERY}st start day",
    f"Otherwise the family is {CLOSED}",
    "Each measure's own row to beat is reported beside",
    f"(a) Development start days only (NQ to {WINDOW_END})",
    "a family's one cell for judgement is chosen on the choice block alone -- starts 2020-01-02 to the last start of "
    f"{CHOICE_LAST_YEAR} less the reading's horizon -- as its cell with the best P there; the judged block -- starts "
    f"from the first session of {JUDGED_FIRST_YEAR} with the reading's horizon left -- decides; the reverse (chosen "
    "late, judged early) is reported beside",
    f"a coin design is chosen on the registered coin ({REGISTERED_COIN}) and judged on the fifty other sequences; the "
    "gate floor is read at the fresh campaign seed",
    "(e) Not worse than R* on P in more than one of the seven start years (D-620 G5)",
    "family k is judged one-sided at 0.05 / (k (k + 1))",
    "one cell per family reaches judgement, so there is no further division inside a family",
    "Every cell run is counted under its family's row and the program's running count is reported with every reading",
)


def declaration(path: Path | str | None = None) -> dict[str, Any]:
    """DECISIONS.md's D-621 row (LF line ends, the line itself) and its sha256 (`user_journey.declaration`'s way)."""
    p = Path(path) if path is not None else Path(__file__).resolve().parents[2] / "DECISIONS.md"
    text = p.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")
    rows = [line for line in text.split("\n") if line.startswith(f"| {DECISION} |")]
    row = rows[0] if len(rows) == 1 else ""
    return {"path": str(p), "rows": len(rows), "row": row, "sha256": hashlib.sha256(row.encode("utf-8")).hexdigest()}


def declaration_problems(decl: Mapping[str, Any]) -> list[str]:
    """Every way this module's constants differ from D-621's row (an empty list: they agree)."""
    out = []
    if int(decl["rows"]) != 1:
        out.append(f"DECISIONS.md holds {decl['rows']} {DECISION} rows, not one")
    if str(decl["sha256"]) != DECLARATION_SHA256:
        out.append(f"the {DECISION} row's sha256 is {str(decl['sha256'])[:16]}, not the pinned "
                   f"{DECLARATION_SHA256[:16]}")
    row = re.sub(r"\s+", " ", str(decl["row"]))
    out += [f"{DECISION} does not say {w!r}" for w in D621_WORDS if w not in row]
    if (U.BOOT_DRAWS != 2000 or P_HORIZON != 63 or BOOT_BLOCK != P_HORIZON or len(START_YEARS) != 7
            or len(MEASURES) != 10 or len(GUARDED_KEYS) != 9):
        out.append("the module's draws, block, start years or scorecard are not D-621's")
    return out


__all__ = ["DECISION", "PROGRAM", "SCRIPT", "READING", "ARM", "BESIDE_ARM", "ROWS_TO_BEAT", "BESIDE_ONLY",
           "COIN_DESIGNS", "P_MONTHS", "P_HORIZON", "BOOT_BLOCK", "ALPHA", "SHARE_TOLERANCE", "RELATIVE_TOLERANCE",
           "SLACK", "CHOICE_LAST_YEAR", "JUDGED_FIRST_YEAR", "EARLY", "LATE", "BLOCKS", "START_YEARS",
           "YEARS_WORSE_ALLOWED", "WINDOW_END", "COIN_SEQUENCES", "COIN_WINS_NEEDED", "COIN_EVERY", "REGISTERED_COIN",
           "GATE_SEED", "GATE_PATHS", "GATE_ROW_TO_BEAT", "LINES", "CARRIED", "CLOSED", "SECTIONS", "HIGHER", "LOWER",
           "SHARE", "DOLLARS", "SESSIONS", "RATIO", "PRIMARY", "GUARDED", "Measure", "MEASURES", "BY_KEY",
           "PRIMARY_KEY", "GUARDED_KEYS", "HORIZONS", "ALT_HORIZONS", "records_from_start_rows", "window_problems",
           "eligible", "block", "thinned", "months_ahead", "p_of", "u1_reading", "p_from_u1", "scorecard",
           "row_to_beat", "choose", "family_level", "p_difference", "tolerance_line", "guard_lines", "guards_hold",
           "year_rule", "coin_line", "gate_floor", "verdict", "judge", "FAMILY_NAME", "CELL_NAME", "DECISION_ID", "PROGRAM_ID",
           "SEAT_KEYS", "PROTOCOL_FIELDS", "PAYOUT_PATHS", "OVERRIDE_KINDS", "ENTRY_KINDS", "BASE_SEATS",
           "REFERENCE_CELL", "BASES",
           "DEFAULT_BASE", "BASE_LABEL", "REFERENCE_CELLS", "BASE_COIN_DESIGN", "BASE_REFUSED_KINDS", "base_of",
           "coin_design", "override_kinds", "family_id",
           "result_name",
           "override_problems", "family_problems", "program_count", "DECLARATION_SHA256", "D621_WORDS", "declaration",
           "declaration_problems",
           "WINDOW_DECISION", "WINDOW_BASES", "ALL_BASES", "WINDOW_EQUALS_U1", "WINDOW_NO_OVERRIDE",
           "NOT_RUNNABLE_NO_R", "NOT_RUNNABLE_SUPPLY", "is_window_base", "window_label", "counted", "r_cap",
           "supply_problem", "capped_policy_id", "capped_policy_dict",
           "JOINT_DECISION", "JOINT_OPENS_AT_FIRST_PAYOUT", "JOINT_TOPSTEP_SEATS", "JOINT_BASES", "EVERY_BASE",
           "JOINT_EQUALS_U1", "JOINT_NO_OVERRIDE", "UPPER_BOUND_LABEL", "HOLDS_AS_UPPER_BOUND",
           "UPPER_BOUND_WAITS_FOR", "is_joint_base", "joint_seats", "joint_label", "upper_bound",
           "SEQUENCING_DECISION", "JOINT_LUCID_SEATS", "JOINT_OPENINGS", "JOINT_UNHEDGED", "JOINT_DEALS",
           "joint_base_name", "HYPOTHETICAL_LABEL", "HYPOTHETICAL_NOTE", "HYPOTHETICAL_ID", "joint_deal",
           "hypothetical", "selectable", "base_row_label", "hypothetical_id", "refuse_labelled",
           "FUNDED_PLAN", "FUNDED_PLAN_DECISION", "FUNDED_PLAN_KEYS", "FUNDED_PLAN_OPTIONAL", "FUNDED_PLAN_RR",
           "FUNDED_PLAN_REFUSED_WITH", "funded_plan_problems", "funded_plan_paid", "funded_plan_policy_id",
           "funded_plan_leaf_name", "funded_plan_policy_dict", "funded_plan_dict_problems",
           "FUNDED_RESOLVE", "FUNDED_RESOLVE_DECISION", "FUNDED_RESOLVE_KEYS", "FUNDED_RESOLVE_START",
           "FUNDED_RESOLVE_TRADES", "FUNDED_RESOLVE_REFUSED_WITH", "FUNDED_RESOLVE_OPTIONAL",
           "FUNDED_RESOLVE_LOWEST", "funded_resolve_lowest", "funded_resolve_problems",
           "funded_resolve_policy_id", "funded_resolve_risk", "funded_resolve_leaf_name",
           "funded_resolve_policy_dict", "funded_resolve_dict_problems"]
