"""Q-35 (E-021 (2); TASK_QUEUE Q-35): where the registered designs' funded openings fall in U1's replay -- a supply count,
**no outcome**.

    from extended import openings as O
    outs = O.run_starts("p16", "verdict", job, starts, workers=1)            # the replay, the ledger on (engine)
    table = O.TradeTable(trades)                                             # the design's trade table, where/when only
    placed = [O.place(op, job["dates"], table, cal) for x in outs for op in x["openings"]]
    rows = O.count_rows(placed, "p16", "verdict")

**The opening.** A funded account's opening is its first executed trade in the engine's per-trade ledger
(`LockstepPath.trades`, `record_trades=True`), first by (day, slot) -- Stage 2's own definition: U2's `opening_trade`
(`vendor/stage2/scripts/u_xfa_day_budget.py`, the first of the account's ledger rows). A funded account that never
trades has no opening. "Routed" is the engine's: the shared-day router hands the account the trade (D-130, D-216, the
strict rule D-429), and the ledger row exists only when the trade was executed (a slot the sizing stood aside from, or
with no outcome, writes none).

**The replay** is U1's as Q-17 adapted it (`extended.user_beside`): every start of the design's development window, the
long run of min(252, sessions left) sessions, the start's own path seed (`user_beside.start_seed`), every firm response
off -- `ConductModel(rtp=False, enforcement_p=0.0)`, the vendored 0 %, placement-off call (`user_beside.response_args`
with `off`) -- and **the ledger switched on (`record_trades=True`), nothing else changed**. The ledger only records: the
engine appends a row per executed trade and reads nothing back from it (`lockstep.py`; the synthetic test holds a path
equal with it on and off), and the script's identity holds every start's record equal to U1's file on every column.

**Placing an opening.** The ledger row carries the replay's historical day and the trade's index in that day's block
(`SharedDayDraw` / `TierSizedDraw.last_trade`): the session is `dates[start + historical_day]` (calendar day = historical
day + 1, `ReplayTable`; checked), and the block is the design's trade table grouped by date in entry order
(`score_fv3_grid.gate_blocks`: each date's rows sorted by `entry_t`, stable) -- `TradeTable` keeps that order and
`TradeTable.block_problems` holds every block's entry times and sides equal to the table's, day by day. From the table
only `TRADE_COLUMNS` are kept (where and when: the date, the decision mark, the entry bar, the stop, the side for the
check, Stage 2's day kind); every outcome column (`r_*`, `g_*`, `c_*`, `mae_*`, `exit_t*`, `o_*`, `flat`, fees) is
dropped as the table is built.

**The clock.** Stage 2's trading-day clock counts minutes after 17:00 CT (`resolved_coin.ct`, `collect_core.c_slot`). A
mark (`decision_slot_minutes`) is the decision time: the bar ending at it has closed. The entry bar `entry_t` is a bar's
END index on that clock (`fast_walk.entry_bar`: the first bar with an open after the mark, `delay` bars later), so the
entry fills at that bar's open, one minute earlier: entry minute = `entry_t` - 1 (P-16 enters at its mark; P-14 five
bars late, A3's `screen_delay_min`). Hours and marks are Central Time throughout (the clock is built in
America/Chicago, DST-aware).

**Day kinds** (the session's date: a trading day runs 17:00 CT the evening before to 15:10 CT): a **report day** is a
BLS 08:30 ET release day by Stage 2's calendar (`flip_kit.collect_release_days` on A1's `news` files -- the calendar
Stage 2's day kind 'b' is made from; the script holds the trades' `day_kind` to it); an **FOMC day** by the same
function's FOMC list; the **early-close calendar** kind by `config/calendar_early_closes.csv` (E-029: holiday,
early_close, data_defect_candidate, or none); the weekday; the year.

**The blocks** are the opening's own session date's: the choice block 2020-01-02 to 2023-12-29, the judged block
2024-01-02 to 2026-07-16 (`extended.reader`), and both together (`all`). A date outside them is refused.

**What is counted** (`count_rows`, per design, arm and block): every opening (a start's funded account: the same
historical trade opens accounts in many starts' replays), with its share of the block's openings, and the distinct
historical trades among them (date and index), with theirs. Sections: `supply`; `mark` (HH:MM CT); `hour` (the mark's);
`entry_delay` (entry minute less mark); `window` (the shares inside 08:30-09:00 CT, by mark and by entry, the end
exclusive and inclusive, and the marks before 08:30, at 09:00 and after it); `report_day`; `report_day_mark` (the
marks of the report-day openings); `fomc_day`; `calendar`; `weekday`; `year`; `stop`. **No outcome** -- no P&L, win
or loss, exit, pass or payout -- crosses from the engine (`OPENING_KEYS`) or the table (`TRADE_COLUMNS`), or is
written (`COLUMNS`; `output_problems` refuses a frame with any other column or any outcome word in a column's name).

Importing this module touches no `sys.path` and imports no engine: the replay (`run_starts`, `_task`) imports the
vendored tree lazily, in a process that called `extended.use_vendored_stage2()`.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

from extended.reader import CHOICE_END, CHOICE_START, CONFIRMATION_START, JUDGED_END, JUDGED_START

#: the minutes of a day, and 17:00 CT -- the trading-day clock's zero -- in minutes after midnight
DAY_MINUTES = 24 * 60
CLOCK_ZERO = 17 * 60
#: 08:30 and 09:00 CT on the trading-day clock (`collect_core.c_slot(8, 30)`, `c_slot(9, 0)`)
OPEN_0830 = 930
MARK_0900 = 960
#: a micro (MNQ) tick is a quarter point: stop ticks / 4 = stop points
TICKS_PER_POINT = 4.0

#: what crosses from the engine's ledger: where and when an opening was placed, nothing else
OPENING_KEYS = ("start_day", "account", "day", "slot", "historical_day", "trade_index")
#: what is kept of a design's trade table: where and when, the side (only for the block check), Stage 2's day kind
TRADE_COLUMNS = ("date", "decision_slot_minutes", "entry_t", "stop_ticks", "side", "day_kind")
#: what a placed opening carries (`place`)
PLACED_KEYS = ("start_day", "account", "date", "block", "year", "weekday", "mark", "mark_ct", "hour_ct", "entry_minute",
               "entry_ct", "entry_delay", "stop_points", "report_day", "fomc_day", "calendar", "trade_key")

BLOCKS = ("choice", "judged", "all")
SECTIONS = ("identity", "supply", "mark", "hour", "entry_delay", "window", "report_day", "report_day_mark", "fomc_day",
            "calendar", "weekday", "year", "stop")
#: the sections whose groups partition a block's openings (each opening in exactly one group)
PARTITIONS = ("mark", "hour", "entry_delay", "report_day", "fomc_day", "calendar", "weekday", "year", "stop")
COLUMNS = ("section", "reading", "design", "prereg", "arm", "block", "group", "openings", "share", "distinct_trades",
           "distinct_share", "block_openings", "block_distinct", "holds", "compared", "note")
#: words that mark an outcome; no written column's name may contain one (case-insensitive)
OUTCOME_WORDS = ("pnl", "p&l", "profit", "loss", "lost", "win", "won", "exit", "pass", "payout", "paid", "balance",
                 "cash", "net", "fee", "mae", "outcome", "result", "return", "cushion", "floor", "equity", "drawdown",
                 "breach", "r_", "rr", "gross", "cost")
WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

REPORT = "BLS 08:30 ET report day"
NOT_REPORT = "not a report day"
FOMC = "FOMC day"
NOT_FOMC = "not an FOMC day"
NO_CALENDAR = "none"
EVERY = "every opening"
#: the window section's groups, in order: (label, the test on (mark, entry minute)); the first four partition the marks
WINDOWS: tuple[tuple[str, Any], ...] = (
    ("mark before 08:30 CT", lambda m, e: m < OPEN_0830),
    ("mark in [08:30, 09:00) CT", lambda m, e: OPEN_0830 <= m < MARK_0900),
    ("mark at 09:00 CT", lambda m, e: m == MARK_0900),
    ("mark after 09:00 CT", lambda m, e: m > MARK_0900),
    ("mark in [08:30, 09:00] CT", lambda m, e: OPEN_0830 <= m <= MARK_0900),
    ("entry in [08:30, 09:00) CT", lambda m, e: OPEN_0830 <= e < MARK_0900),
    ("entry in [08:30, 09:00] CT", lambda m, e: OPEN_0830 <= e <= MARK_0900),
)
WINDOW_PARTITION = tuple(w for w, _ in WINDOWS[:4])


class OpeningsRefused(RuntimeError):
    """An input or an output this reading cannot stand behind (an outcome column, a placement that does not map)."""


# ------------------------------------------------------------------------------------------------------- the clock


def clock_ct(minutes: int) -> str:
    """A trading-day-clock minute (minutes after 17:00 CT) as HH:MM CT (`resolved_coin.ct`'s arithmetic)."""
    m = (int(minutes) + CLOCK_ZERO) % DAY_MINUTES
    return f"{m // 60:02d}:{m % 60:02d}"


def entry_minute(entry_t: float) -> int:
    """The minute an entry fills on the trading-day clock: the open of its entry bar, whose END index is `entry_t`."""
    return int(round(float(entry_t))) - 1


def block_of(day: str | date) -> str:
    """'choice' or 'judged' for a session date; anything else (the holiday gap, before 2020-01-02, from 2026-07-17) is
    refused."""
    d = day if isinstance(day, date) else date.fromisoformat(str(day))
    if d >= CONFIRMATION_START:
        raise OpeningsRefused(f"REFUSED: an opening dated {d}: NQ from {CONFIRMATION_START} is the confirmation window")
    if CHOICE_START <= d <= CHOICE_END:
        return "choice"
    if JUDGED_START <= d <= JUDGED_END:
        return "judged"
    raise OpeningsRefused(f"REFUSED: an opening dated {d} is in neither the choice nor the judged block")


# ------------------------------------------------------------------------------------------------------ the ledger


def openings_from_ledger(trades: Iterable[Mapping[str, Any]], start_day: int) -> list[dict[str, int]]:
    """Each funded account's first executed trade (first by day, then slot) from the engine's ledger rows, as
    `OPENING_KEYS` only -- the P&L, balances and every other field of the row are dropped here. Sorted by account.
    Refuses a funded row without the draw's historical day or trade index, and a flip session's row (a design with a
    flip stream is refused by `user_beside.base_problems` already)."""
    first: dict[int, tuple[int, int, Mapping[str, Any]]] = {}
    for r in trades:
        if r.get("kind") != "funded":
            continue
        if r.get("source", "strategy") != "strategy":
            raise OpeningsRefused(f"REFUSED: a funded ledger row from source {r.get('source')!r}; only routed strategy "
                                  "trades are openings")
        if r.get("historical_day") is None or r.get("trade_index") is None:
            raise OpeningsRefused("REFUSED: a funded ledger row without the draw's historical day and trade index "
                                  "(the draw is not a shared-day draw): the opening cannot be placed")
        k = int(r["index"])
        key = (int(r["day"]), int(r["slot"]))
        if k not in first or key < first[k][:2]:
            first[k] = (*key, r)
    out = []
    for k in sorted(first):
        d, s, r = first[k]
        out.append({"start_day": int(start_day), "account": int(k), "day": d, "slot": s,
                    "historical_day": int(r["historical_day"]), "trade_index": int(r["trade_index"])})
    return out


def ledger_problems(trades: Sequence[Mapping[str, Any]], funded: Sequence[Any], ops: Sequence[Mapping[str, int]],
                    what: str = "") -> list[str]:
    """The ledger against the engine's own counts: every funded account's ledger rows number its trades
    (`FundedAccount.trades`), each account that traded has exactly one opening and no other has one, the opening is no
    earlier than the account's first session (activation day + 1), and its calendar day is its historical day + 1 (the
    replay's calendar, `ReplayTable`)."""
    rows = Counter(int(r["index"]) for r in trades if r.get("kind") == "funded")
    by = {int(o["account"]): o for o in ops}
    out = []
    for f in funded:
        k, n = int(f.index), int(f.trades)
        if rows.get(k, 0) != n:
            out.append(f"{what}funded account {k}: {rows.get(k, 0)} ledger rows against its {n} trades")
        if (n > 0) != (k in by):
            out.append(f"{what}funded account {k}: {n} trades but {'an' if k in by else 'no'} opening")
        if k in by and int(by[k]["day"]) < int(f.activation_day) + 1:
            out.append(f"{what}funded account {k}: opened on day {by[k]['day']}, before its first session "
                       f"{int(f.activation_day) + 1}")
    extra = sorted(set(by) - {int(f.index) for f in funded})
    if extra:
        out.append(f"{what}openings for accounts the path does not hold: {extra[:5]}")
    for o in ops:
        if int(o["day"]) != int(o["historical_day"]) + 1:
            out.append(f"{what}account {o['account']}: calendar day {o['day']} is not its historical day "
                       f"{o['historical_day']} + 1")
    return out


# ---------------------------------------------------------------------------------------------- the trade table


def _sides(side: pd.Series) -> np.ndarray:
    """`score_fv3_grid.gate_blocks`' sides from a `side` column: +1 long, -1 otherwise."""
    return np.where(side.astype(str).str.lower() == "long", 1, -1).astype(int)


class TradeTable:
    """A design's trade table as its blocks see it: per date, the rows sorted by `entry_t` (stable), as
    `score_fv3_grid.gate_blocks` sorts them -- holding `TRADE_COLUMNS` only."""

    def __init__(self, trades: pd.DataFrame):
        missing = [c for c in TRADE_COLUMNS if c not in trades.columns]
        if missing:
            raise OpeningsRefused(f"REFUSED: the trade table has no column(s) {missing}")
        t = trades.loc[:, list(TRADE_COLUMNS)].copy()             # every outcome column dropped here
        t["date"] = t["date"].astype(str)
        self.columns = tuple(t.columns)
        self.n = int(len(t))
        self._by: dict[str, dict[str, np.ndarray]] = {}
        for d, g in t.groupby("date", sort=True):
            g = g.sort_values("entry_t", kind="stable")
            self._by[str(d)] = {"mark": g["decision_slot_minutes"].astype(int).to_numpy(),
                                "entry_t": g["entry_t"].astype(float).to_numpy(),
                                "stop_ticks": g["stop_ticks"].astype(float).to_numpy(),
                                "side": _sides(g["side"]),
                                "day_kind": g["day_kind"].astype(str).to_numpy()}

    @property
    def dates(self) -> list[str]:
        return sorted(self._by)

    def day(self, d: str) -> dict[str, np.ndarray] | None:
        return self._by.get(str(d))

    def block_problems(self, blocks: Sequence[Any], dates: Sequence[str], what: str = "") -> list[str]:
        """Every block against the table's day: the same trades in the same order -- count, entry bars exactly, sides
        where the block carries them -- and no table date outside `dates`."""
        out = []
        if len(blocks) != len(dates):
            return [f"{what}{len(blocks)} blocks against {len(dates)} dates"]
        bad: list[str] = []
        for b, d in zip(blocks, dates):
            g = self._by.get(str(d))
            n = 0 if g is None else len(g["entry_t"])
            if len(b) != n:
                bad.append(f"{d}: {len(b)} trades in the block, {n} in the table")
                continue
            if n == 0:
                continue
            et = getattr(b, "entry_t", None)
            if et is None or not np.array_equal(np.asarray(et, float), g["entry_t"]):
                bad.append(f"{d}: the block's entry bars are not the table's")
            sd = getattr(b, "sides", None)
            if sd is not None and not np.array_equal(np.asarray(sd, int), g["side"]):
                bad.append(f"{d}: the block's sides are not the table's")
        if bad:
            out.append(f"{what}{len(bad)} of {len(dates)} days differ (first: {bad[0]})")
        stray = sorted(set(self._by) - {str(d) for d in dates})
        if stray:
            out.append(f"{what}{len(stray)} table dates are not session dates (first: {stray[0]})")
        return out

    def day_kind_problems(self, report_days: frozenset[str], what: str = "") -> list[str]:
        """Stage 2's day kind of every row against the report-day calendar: 'b' exactly on a report day, else 'n'."""
        bad = []
        for d, g in self._by.items():
            kinds = set(g["day_kind"].tolist())
            want = "b" if d in report_days else "n"
            if kinds != {want}:
                bad.append(f"{d}: day kind(s) {sorted(kinds)}, the calendar says {want!r}")
        return [f"{what}{len(bad)} of {len(self._by)} trading days' day kinds disagree with the report-day calendar "
                f"(first: {bad[0]})"] if bad else []


# ------------------------------------------------------------------------------------------------- the calendars


@dataclass(frozen=True)
class Calendars:
    """The day kinds of the sessions: Stage 2's BLS 08:30 report days and FOMC days (ISO dates) and the early-close
    calendar's kind by date."""
    report_days: frozenset[str]
    fomc_days: frozenset[str]
    calendar_kind: Mapping[str, str]


def iso_of_yymmdd(x: int) -> str:
    """`flip_kit`'s yymmdd integer (2000s) as an ISO date."""
    x = int(x)
    return f"20{x // 10000:02d}-{(x // 100) % 100:02d}-{x % 100:02d}"


def calendar_kinds(rows: Iterable[Mapping[str, str]]) -> dict[str, str]:
    """`config/calendar_early_closes.csv`'s rows as {date: kind} (two rows on one date joined with '+')."""
    out: dict[str, str] = {}
    for r in rows:
        d, k = str(r["date"]), str(r["kind"])
        out[d] = k if d not in out else f"{out[d]}+{k}"
    return out


# ------------------------------------------------------------------------------------------------- one opening


def place(op: Mapping[str, int], dates: Sequence[str], table: TradeTable, cal: Calendars) -> dict[str, Any]:
    """An opening (`OPENING_KEYS`) placed: its session date (`dates[start + historical day]`), block, year, weekday,
    mark, hour, entry minute, stop and day kinds (`PLACED_KEYS`)."""
    i = int(op["start_day"]) + int(op["historical_day"])
    if not 0 <= i < len(dates):
        raise OpeningsRefused(f"REFUSED: start {op['start_day']} historical day {op['historical_day']} is outside the "
                              f"{len(dates)} sessions")
    d = str(dates[i])
    g = table.day(d)
    j = int(op["trade_index"])
    if g is None or not 0 <= j < len(g["mark"]):
        raise OpeningsRefused(f"REFUSED: {d} trade {j} is not in the trade table")
    m, e = int(g["mark"][j]), entry_minute(g["entry_t"][j])
    dd = date.fromisoformat(d)
    hour = ((m + CLOCK_ZERO) % DAY_MINUTES) // 60
    return {"start_day": int(op["start_day"]), "account": int(op["account"]), "date": d, "block": block_of(dd),
            "year": dd.year, "weekday": WEEKDAYS[dd.weekday()], "mark": m, "mark_ct": clock_ct(m),
            "hour_ct": f"{hour:02d}", "entry_minute": e, "entry_ct": clock_ct(e), "entry_delay": e - m,
            "stop_points": float(g["stop_ticks"][j]) / TICKS_PER_POINT, "report_day": d in cal.report_days,
            "fomc_day": d in cal.fomc_days, "calendar": str(cal.calendar_kind.get(d, NO_CALENDAR)),
            "trade_key": f"{d}#{j}"}


# ------------------------------------------------------------------------------------------------- the counts


def _groups(p: Mapping[str, Any]) -> dict[str, list[tuple[Any, str]]]:
    """Each section's (sort key, group label) pairs for one placed opening."""
    m, e = int(p["mark"]), int(p["entry_minute"])
    return {
        "supply": [(0, EVERY)],
        "mark": [(m, p["mark_ct"])],
        "hour": [(m // 60, p["hour_ct"])],                    # the clock's hours in session order, 17 first
        "entry_delay": [(int(p["entry_delay"]), f"{int(p['entry_delay']):+d} min")],
        "window": [(i, w) for i, (w, f) in enumerate(WINDOWS) if f(m, e)],
        "report_day": [(0, REPORT)] if p["report_day"] else [(1, NOT_REPORT)],
        "report_day_mark": [(m, p["mark_ct"])] if p["report_day"] else [],
        "fomc_day": [(0, FOMC)] if p["fomc_day"] else [(1, NOT_FOMC)],
        "calendar": [(0 if p["calendar"] == NO_CALENDAR else 1, str(p["calendar"]))],
        "weekday": [(WEEKDAYS.index(p["weekday"]), p["weekday"])],
        "year": [(int(p["year"]), str(int(p["year"])))],
        "stop": [(float(p["stop_points"]), f"{float(p['stop_points']):g} points")],
    }


def _row(section: str, design: str, prereg: str, arm: str, block: str, group: str, **kw: Any) -> dict[str, Any]:
    r = {c: np.nan for c in COLUMNS}
    r.update({"section": section, "reading": "", "design": design, "prereg": prereg, "arm": arm, "block": block,
              "group": group, "note": ""})
    r.update(kw)
    return r


def count_rows(placed: Sequence[Mapping[str, Any]], design: str, arm: str, prereg: str = "") -> list[dict[str, Any]]:
    """Per block (choice, judged, all) and section, every group's openings and distinct historical trades, each with
    its share of the block's (NaN when the block holds none)."""
    for p in placed:
        bad = set(p) - set(PLACED_KEYS)
        if bad:
            raise OpeningsRefused(f"REFUSED: a placed opening carries {sorted(bad)}: only where and when is counted")
    rows: list[dict[str, Any]] = []
    for block in BLOCKS:
        sub = [p for p in placed if block == "all" or p["block"] == block]
        n, nd = len(sub), len({p["trade_key"] for p in sub})
        counts: dict[str, Counter] = defaultdict(Counter)
        keys: dict[str, dict[str, set]] = defaultdict(lambda: defaultdict(set))
        order: dict[str, dict[str, Any]] = defaultdict(dict)
        for p in sub:
            for section, gs in _groups(p).items():
                for k, g in gs:
                    counts[section][g] += 1
                    keys[section][g].add(p["trade_key"])
                    order[section][g] = k
        for section in SECTIONS[1:]:
            if section == "supply" and not n:
                rows.append(_row(section, design, prereg, arm, block, EVERY, openings=0, share=np.nan,
                                 distinct_trades=0, distinct_share=np.nan, block_openings=0, block_distinct=0))
                continue
            for g in sorted(counts[section], key=lambda x: (order[section][x], x)):
                c, dc = counts[section][g], len(keys[section][g])
                rows.append(_row(section, design, prereg, arm, block, g, openings=int(c),
                                 share=c / n if n else np.nan, distinct_trades=int(dc),
                                 distinct_share=dc / nd if nd else np.nan, block_openings=int(n),
                                 block_distinct=int(nd)))
    return rows


# ------------------------------------------------------------------------------------------------- the output


def outcome_columns(columns: Iterable[str]) -> list[str]:
    """The column names that carry an outcome word (`OUTCOME_WORDS`, case-insensitive substrings)."""
    return [c for c in columns if any(w in str(c).lower() for w in OUTCOME_WORDS)]


def output_problems(df: pd.DataFrame) -> list[str]:
    """Why a frame is not this reading's: its columns are not `COLUMNS` exactly or carry an outcome word; a section is
    unknown; a count is negative or a share outside [0, 1]; a partition section's groups do not add to the block's
    openings; the choice and judged blocks do not add to `all`; the report-day marks do not add to the report-day
    openings; the window's partition does not add up, or its inclusive window is not its two parts."""
    out = []
    if tuple(df.columns) != COLUMNS:
        out.append(f"the columns are {list(df.columns)}, not {list(COLUMNS)}")
    bad = outcome_columns(df.columns)
    if bad:
        out.append(f"outcome column(s) {bad}: no outcome is written")
    if out:
        return out
    unknown = sorted(set(df["section"].astype(str)) - set(SECTIONS))
    if unknown:
        out.append(f"unknown section(s) {unknown}")
    c = df[df["section"] != "identity"]
    for col in ("openings", "distinct_trades", "block_openings", "block_distinct"):
        v = pd.to_numeric(c[col], errors="coerce")
        if v.isna().any() or (v < 0).any():
            out.append(f"{col}: a blank or negative count")
    for col in ("share", "distinct_share"):
        v = pd.to_numeric(c[col], errors="coerce").dropna()
        if ((v < -1e-12) | (v > 1 + 1e-12)).any():
            out.append(f"{col}: a share outside [0, 1]")
    for (design, arm), g in c.groupby(["design", "arm"], sort=False):
        for block in BLOCKS:
            b = g[g["block"] == block]
            sup = b[b["section"] == "supply"]
            if len(sup) != 1:
                out.append(f"{design} {arm} {block}: {len(sup)} supply rows")
                continue
            n = int(sup["openings"].iloc[0])
            for section in PARTITIONS:
                s = int(b.loc[b["section"] == section, "openings"].sum())
                if s != n:
                    out.append(f"{design} {arm} {block} {section}: the groups add to {s}, not {n}")
            w = b[b["section"] == "window"].set_index("group")["openings"]
            if int(sum(int(w.get(x, 0)) for x in WINDOW_PARTITION)) != n:
                out.append(f"{design} {arm} {block} window: the marks' partition does not add to {n}")
            if int(w.get(WINDOWS[4][0], 0)) != int(w.get(WINDOWS[1][0], 0)) + int(w.get(WINDOWS[2][0], 0)):
                out.append(f"{design} {arm} {block} window: the inclusive window is not its two parts")
            rep = int(b.loc[(b["section"] == "report_day") & (b["group"] == REPORT), "openings"].sum())
            rm = int(b.loc[b["section"] == "report_day_mark", "openings"].sum())
            if rep != rm:
                out.append(f"{design} {arm} {block} report_day_mark: {rm}, not the report day's {rep}")
        for section in SECTIONS[1:]:
            s = g[g["section"] == section]
            parts = s[s["block"].isin(("choice", "judged"))].groupby("group")["openings"].sum()
            whole = s[s["block"] == "all"].set_index("group")["openings"]
            for grp in set(parts.index) | set(whole.index):
                if int(parts.get(grp, 0)) != int(whole.get(grp, 0)):
                    out.append(f"{design} {arm} {section} {grp!r}: choice + judged {int(parts.get(grp, 0))} is not "
                               f"all's {int(whole.get(grp, 0))}")
                    break
    return out


def frame(rows: Sequence[Mapping[str, Any]], reading: str) -> pd.DataFrame:
    """The rows as the reading's frame, columns `COLUMNS` in order, `reading` on every row."""
    df = pd.DataFrame(list(rows), columns=list(COLUMNS))
    df["reading"] = reading
    return df


def identity_row(design: str, prereg: str, arm: str, check: str, compared: int, note: str = "") -> dict[str, Any]:
    """A held identity's row (a failed one ends the run before anything is written)."""
    return _row("identity", design, prereg, arm, "all", check, holds=True, compared=int(compared), note=note)


# ------------------------------------------------------------------------------------------------- the replay


def ledger_args(args: dict[str, Any]) -> dict[str, Any]:
    """The replay's arguments with every response off (`user_beside.response_args(args, off)`: refuses anything but
    the vendored 0 %, placement-off call) and the engine's per-trade ledger on -- nothing else changed."""
    from extended import user_beside as B

    if "record_trades" in args["path"]:
        raise OpeningsRefused("REFUSED: the replay's path arguments already carry record_trades")
    a = B.response_args(args, B.BY_NAME["off"])
    return {**a, "path": {**a["path"], "record_trades": True}}


def _task(task: tuple) -> list[dict[str, Any]]:
    """(design, arm, blocks, dates, args, starts) -> per start: its U1 record from the long replay (the identity's;
    `user_beside.long_record`, with its three checks against the engine's totals), its openings (`OPENING_KEYS`) and
    the ledger's problems against the engine's counts. The path itself is dropped before the next start."""
    import warnings

    from extended import user_beside as B
    from propedge.research import user_journey as U

    warnings.filterwarnings("ignore")
    design, arm, blocks, dates, args, starts = task
    a = ledger_args(args)
    lag = int(args["path"]["payout_lag_days"])
    n = len(blocks)

    def pay(lp, obs):
        return U.payout_arrivals([(f.activation_day, lag, f.payout_days, f.payout_cash) for f in lp.funded], obs)

    def totals(lp):
        return lp.path.total_fees, lp.path.total_payouts

    out = []
    for s in starts:
        L = min(U.HORIZON, n - s)
        lp = B.replay(blocks[s:s + L], a, B.start_seed(s))
        if len(lp.path.cash_series) != L + 1:
            raise RuntimeError(f"{design} {arm} start {s}: {len(lp.path.cash_series)} closes, not {L + 1}")
        rec = B.long_record(s, dates[s], lp, pay, totals)
        ops = openings_from_ledger(lp.trades, s)
        probs = ledger_problems(lp.trades, lp.funded, ops, f"{design} {arm} start {s}: ")
        out.append({"rec": rec["rec"], "differs": [], "checked": [], "pay_bad": rec["pay_bad"],
                    "cash_bad": rec["cash_bad"], "fee_bad": rec["fee_bad"], "openings": ops, "problems": probs})
        del lp
    return out


def run_starts(design: str, arm: str, job: dict[str, Any], starts: Sequence[int], workers: int,
               chunk: int = 20) -> list[dict[str, Any]]:
    """Every chosen start of one design and arm, in start order, across `customer_journey._pool_run`'s guarded pool
    (`workers`; 1 runs in this process)."""
    import customer_journey as CJ

    if job.get("engine") != "single":
        raise OpeningsRefused("REFUSED: Q-35 replays single-firm designs only")
    chunks = [list(starts[j:j + chunk]) for j in range(0, len(starts), chunk)]
    tasks = [(design, arm, job["blocks"], job["dates"], job["args"], c) for c in chunks]
    res = CJ._pool_run(tasks, _task, int(workers), f"Q-35 {design} {arm}")
    return [x for part in res for x in part]


def stage2_calendars(start: date = CHOICE_START, end: date = JUDGED_END) -> tuple[frozenset[str], frozenset[str],
                                                                                    dict[str, Any]]:
    """(report days, FOMC days, provenance) by Stage 2's own reading (`flip_kit.collect_release_days`) of A1's `news`
    files (`vendor/stage2/config/atlas_a1.yaml`) over `start`..`end`. Needs the vendored tree on `sys.path`."""
    import yaml

    from propedge import CONFIG_DIR
    from propedge.data import flip_kit as fk

    if end >= CONFIRMATION_START:
        raise OpeningsRefused(f"REFUSED: the calendars are read to {JUDGED_END} at most")
    cfg = yaml.safe_load((CONFIG_DIR / "atlas_a1.yaml").read_text(encoding="utf-8"))
    win = {"news": cfg["news"], "window": {"warm": start.isoformat(), "start": start.isoformat(),
                                           "end": end.isoformat()}}
    fomc, bls = fk.collect_release_days(win)
    return (frozenset(iso_of_yymmdd(x) for x in bls), frozenset(iso_of_yymmdd(x) for x in fomc),
            {"config": "vendor/stage2/config/atlas_a1.yaml", "news": cfg["news"],
             "function": "propedge.data.flip_kit.collect_release_days", "window": [start.isoformat(), end.isoformat()]})


__all__ = ["OPENING_KEYS", "TRADE_COLUMNS", "PLACED_KEYS", "BLOCKS", "SECTIONS", "PARTITIONS", "COLUMNS", "OUTCOME_WORDS",
           "WINDOWS", "WINDOW_PARTITION", "REPORT", "NOT_REPORT", "FOMC", "NOT_FOMC", "NO_CALENDAR", "EVERY",
           "OpeningsRefused", "clock_ct", "entry_minute", "block_of", "openings_from_ledger", "ledger_problems",
           "TradeTable", "Calendars", "iso_of_yymmdd", "calendar_kinds", "place", "count_rows", "outcome_columns",
           "output_problems", "frame", "identity_row", "ledger_args", "run_starts", "stage2_calendars"]
