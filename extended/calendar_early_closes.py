"""Q-40 (E-022 (3)): the calendar of scheduled early closes and holidays of CME Globex equity-index futures (NQ) for the
trading days 2020-01-02 to 2026-07-16, and, apart, the bar store's data-defect candidates -- so that a family voids
such days from a calendar fixed in advance, never from the day's own bars (DRAFT F-02 section 4.5, the red team's F6).

    from extended import calendar_early_closes as C
    rows = C.read_calendar(C.CALENDAR_CSV)          # [{"date", "kind", "close_ct", "source"}, ...]
    python scripts/build_calendar_early_closes.py   # (re)builds config/calendar_early_closes.csv; --check compares

**Where the schedule comes from.** CME Group's own holiday-calendar pages were not read: cmegroup.com answered the
session's first scripted request (2026-11-16) with HTTP 403 and the statement that scripts, robots and other scraping
mechanisms are prohibited by its website Data Terms of Use (config/calendar_early_closes.md). So the schedule is built
from the standard U.S. exchange holiday rules (`RULES`, written into the file's header), as CME applies them to its
equity-index futures, with the two inputs that are calendars published in advance: the BLS Employment Situation dates
(the vendored `vendor/stage2/data/releases_bls_0830_*.csv`, for the Good Friday rule) and one announced closure (S1).

**The cross-check** (`build_rows`) reads the bar store's manifest only -- `vendor/stage2/data/bars/NQ/manifest.json`,
metadata, never a bar file -- and only its entries for trading days inside the window: every list is filtered by date
first, and every lookup is keyed by a window day, so nothing about a day from 2026-07-17 reaches a row, a note or the
printout (the store holds none: its windows guard drops the reserve, Stage 2 D-458 (2)). A scheduled day is annotated
with what the store shows (its last bar against the scheduled close); a day the store records as ending early,
starting late or short that no rule explains is a `data_defect_candidate`, with the manifest's reason where it gives
one (a purchase's edge, a Databento `degraded` date).

Nothing here draws randomness; nothing reads a bar.
"""
from __future__ import annotations

import csv
import io
import json
import textwrap
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from extended import ROOT, VENDOR_STAGE2

#: the development window of NQ (vendor/stage2/config/windows.yaml): the calendar's span
WINDOW_START = date(2020, 1, 2)
WINDOW_END = date(2026, 7, 16)
#: NQ's reserve from here: never read, never written into the calendar
CONFIRMATION_START = date(2026, 7, 17)
#: the date the calendar was compiled (fixed, so a rebuild is byte-identical)
COMPILED_ON = "2026-11-16"

CALENDAR_CSV = ROOT / "config" / "calendar_early_closes.csv"
MANIFEST = VENDOR_STAGE2 / "data" / "bars" / "NQ" / "manifest.json"
BLS_CALENDARS = (VENDOR_STAGE2 / "data" / "releases_bls_0830_2009_2025.csv",
                 VENDOR_STAGE2 / "data" / "releases_bls_0830_2026.csv")

COLUMNS = ("date", "kind", "close_ct", "source")
KINDS = ("holiday", "early_close", "data_defect_candidate")

#: a holiday on which Globex trades an abbreviated equity-index session: the halt, Chicago time
HOLIDAY_HALT_CT = "12:00"
#: a business day with the NYSE's 13:00 ET early close: Globex equity-index futures close fifteen minutes after it
EARLY_CLOSE_CT = "12:15"
#: Good Friday with the BLS Employment Situation at 08:30 ET: the abbreviated morning session's close
GOOD_FRIDAY_JOBS_CLOSE_CT = "08:15"
#: S1, the National Day of Mourning for President Carter: the equity-index halt at the NYSE's (unheld) open
MOURNING_CLOSE_CT = "08:30"

#: the bar store's thresholds (vendor/stage2/propedge/data/bar_import.py, read here as numbers, never imported)
STORE_EARLY_END_CT = "15:00"
STORE_SHORT_DAY_BARS = 1000

CHICAGO = ZoneInfo("America/Chicago")

#: rule id -> (name, the rule as written into the file's header). Names hold no comma and no '#'.
RULES: dict[str, tuple[str, str]] = {
    "H1": ("New Year's Day",
           "1 January; on a Sunday observed Monday 2 January; on a Saturday not observed (the Friday before closes a "
           "yearly accounting period). Globex equity-index futures closed: no session for the date."),
    "H2": ("Martin Luther King Jr. Day",
           f"the third Monday of January. NYSE closed; Globex equity abbreviated session, halt {HOLIDAY_HALT_CT} CT."),
    "H3": ("Washington's Birthday (Presidents' Day)",
           f"the third Monday of February. NYSE closed; Globex equity abbreviated session, halt {HOLIDAY_HALT_CT} CT."),
    "H4": ("Good Friday",
           "Easter Sunday less two days (the anonymous Gregorian computus), when no Employment Situation release is "
           "scheduled that day. Globex equity-index futures closed: no session for the date."),
    "H4b": ("Good Friday with the Employment Situation release",
            "a Good Friday on which BLS scheduled the Employment Situation at 08:30 ET (the vendored BLS calendars "
            "vendor/stage2/data/releases_bls_0830_*.csv, published in advance). NYSE closed; Globex equity trades an "
            f"abbreviated morning session closing {GOOD_FRIDAY_JOBS_CLOSE_CT} CT (CME's practice on such Good Fridays, "
            "from the public record; not read on CME's pages)."),
    "H5": ("Memorial Day",
           f"the last Monday of May. NYSE closed; Globex equity abbreviated session, halt {HOLIDAY_HALT_CT} CT."),
    "H6": ("Juneteenth National Independence Day",
           "19 June (observed), an exchange holiday from 2022 (2021-06-18 was a business day). NYSE closed; Globex "
           f"equity abbreviated session, halt {HOLIDAY_HALT_CT} CT."),
    "H7": ("Independence Day",
           f"4 July (observed). NYSE closed; Globex equity abbreviated session, halt {HOLIDAY_HALT_CT} CT."),
    "H8": ("Labor Day",
           f"the first Monday of September. NYSE closed; Globex equity abbreviated session, halt {HOLIDAY_HALT_CT} CT."),
    "H9": ("Thanksgiving Day",
           "the fourth Thursday of November. NYSE closed; Globex equity abbreviated session, halt "
           f"{HOLIDAY_HALT_CT} CT."),
    "H10": ("Christmas Day",
            "25 December (observed). Globex equity-index futures closed: no session for the date."),
    "E1": ("Day after Thanksgiving",
           f"the Friday after the fourth Thursday of November. NYSE closes 13:00 ET; Globex equity {EARLY_CLOSE_CT} CT."),
    "E2": ("Christmas Eve",
           "24 December when it falls Monday to Thursday (on a Friday it is the observed Christmas Day, H10). NYSE "
           f"closes 13:00 ET; Globex equity {EARLY_CLOSE_CT} CT."),
    "E3": ("Day before Independence Day",
           "3 July when it falls Monday to Thursday (on a Friday it is the observed Independence Day, H7). NYSE closes "
           f"13:00 ET; Globex equity {EARLY_CLOSE_CT} CT."),
    "S1": ("National Day of Mourning for President Jimmy Carter",
           "2025-01-09 only: an announced closure (NYSE and CME notices of late December 2024), not a recurring rule. "
           f"NYSE closed; Globex equity-index futures halt {MOURNING_CLOSE_CT} CT."),
}

#: announced one-off closures: date -> (kind, close_ct, rule)
SPECIAL: dict[date, tuple[str, str, str]] = {date(2025, 1, 9): ("holiday", MOURNING_CLOSE_CT, "S1")}


@dataclass(frozen=True)
class Row:
    """One calendar row. `rule` is the rule id for a scheduled row, "" for a data-defect candidate."""

    date: str
    kind: str
    close_ct: str
    rule: str
    source: str


# ---------------------------------------------------------------------------------------------------------------------
# The rules
# ---------------------------------------------------------------------------------------------------------------------

def easter_sunday(year: int) -> date:
    """Easter Sunday in the Gregorian calendar (the anonymous Gregorian algorithm: Meeus, Jones, Butcher)."""
    a, b, c = year % 19, year // 100, year % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    el = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * el) // 451
    n = h + el - 7 * m + 114
    return date(year, n // 31, n % 31 + 1)


def nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    """The n-th `weekday` (Monday 0) of the month."""
    first = date(year, month, 1)
    return first + timedelta(days=(weekday - first.weekday()) % 7 + 7 * (n - 1))


def last_weekday(year: int, month: int, weekday: int) -> date:
    """The last `weekday` (Monday 0) of the month."""
    last = (date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)) - timedelta(days=1)
    return last - timedelta(days=(last.weekday() - weekday) % 7)


def observed(d: date) -> date:
    """NYSE Rule 7.2's observance: a holiday on a Saturday is observed the Friday before, on a Sunday the Monday after."""
    if d.weekday() == 5:
        return d - timedelta(days=1)
    if d.weekday() == 6:
        return d + timedelta(days=1)
    return d


def observed_new_year(year: int) -> date | None:
    """New Year's Day as observed in `year`: on a Saturday not observed at all (the Friday before, 31 December, closes
    a yearly accounting period), on a Sunday the Monday after."""
    d = date(year, 1, 1)
    if d.weekday() == 5:
        return None
    return observed(d)


def employment_situation_dates(paths: tuple[Path, ...] = BLS_CALENDARS) -> set[date]:
    """The dates BLS scheduled its Employment Situation release at 08:30 ET, from the vendored BLS calendars (a
    schedule published the year before; vendor/stage2/data/README.md section 4)."""
    out: set[date] = set()
    for p in paths:
        with open(p, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r["release"].startswith("Employment Situation") and r["time_et"].startswith("08:30"):
                    out.add(date.fromisoformat(r["date"]))
    return out


def _year_rows(year: int, es: set[date]) -> list[tuple[date, str, str, str]]:
    out: list[tuple[date, str, str, str]] = []

    def add(d: date | None, kind: str, close: str, rule: str) -> None:
        if d is not None:
            out.append((d, kind, close, rule))

    add(observed_new_year(year), "holiday", "", "H1")
    add(nth_weekday(year, 1, 0, 3), "holiday", HOLIDAY_HALT_CT, "H2")
    add(nth_weekday(year, 2, 0, 3), "holiday", HOLIDAY_HALT_CT, "H3")
    gf = easter_sunday(year) - timedelta(days=2)
    if gf in es:
        add(gf, "holiday", GOOD_FRIDAY_JOBS_CLOSE_CT, "H4b")
    else:
        add(gf, "holiday", "", "H4")
    add(last_weekday(year, 5, 0), "holiday", HOLIDAY_HALT_CT, "H5")
    if year >= 2022:
        add(observed(date(year, 6, 19)), "holiday", HOLIDAY_HALT_CT, "H6")
    add(observed(date(year, 7, 4)), "holiday", HOLIDAY_HALT_CT, "H7")
    add(nth_weekday(year, 9, 0, 1), "holiday", HOLIDAY_HALT_CT, "H8")
    thanksgiving = nth_weekday(year, 11, 3, 4)
    add(thanksgiving, "holiday", HOLIDAY_HALT_CT, "H9")
    add(observed(date(year, 12, 25)), "holiday", "", "H10")
    add(thanksgiving + timedelta(days=1), "early_close", EARLY_CLOSE_CT, "E1")
    if date(year, 12, 24).weekday() <= 3:
        add(date(year, 12, 24), "early_close", EARLY_CLOSE_CT, "E2")
    if date(year, 7, 3).weekday() <= 3:
        add(date(year, 7, 3), "early_close", EARLY_CLOSE_CT, "E3")
    for d, (kind, close, rule) in SPECIAL.items():
        if d.year == year:
            add(d, kind, close, rule)
    return out


def scheduled_rows(start: date = WINDOW_START, end: date = WINDOW_END, es_dates: set[date] | None = None,
                   clip: bool = True) -> list[Row]:
    """The scheduled holidays and early closes from `start` to `end`, sorted, from the rules alone (no bar, no
    manifest). `clip` (the default) clips the span to the development window; `clip=False` refuses a span reaching
    NQ's reserve (2026-07-17 on). `es_dates`: the Employment Situation dates (default: the vendored BLS calendars)."""
    if clip:
        start, end = max(start, WINDOW_START), min(end, WINDOW_END)
    elif end >= CONFIRMATION_START:
        raise ValueError(f"the calendar stops at {WINDOW_END}: {end} lies in NQ's reserve (from {CONFIRMATION_START})")
    if es_dates is None:
        es_dates = employment_situation_dates()
    found: list[tuple[date, str, str, str]] = []
    for y in range(start.year, end.year + 1):
        found += [t for t in _year_rows(y, es_dates) if start <= t[0] <= end]
    found.sort()
    ds = [t[0] for t in found]
    if len(ds) != len(set(ds)):
        raise ValueError(f"two rules fall on one date: {sorted(d for d in ds if ds.count(d) > 1)}")
    for d, *_ in found:
        if d.weekday() > 4:
            raise ValueError(f"a scheduled day on a weekend: {d}")
    return [Row(d.isoformat(), kind, close, rule, f"{rule} {RULES[rule][0]}") for d, kind, close, rule in found]


# ---------------------------------------------------------------------------------------------------------------------
# The cross-check against the bar store's manifest
# ---------------------------------------------------------------------------------------------------------------------

def session_minute(hhmm: str) -> int:
    """Minutes since the session's 17:00 CT open (the bar importer's session time): 17:00 -> 0, 16:59 -> 1439."""
    h, m = (int(x) for x in hhmm.split(":"))
    return (h * 60 + m - 17 * 60) % 1440


def _minus_one_minute(hhmm: str) -> str:
    h, m = (int(x) for x in hhmm.split(":"))
    t = (h * 60 + m - 1) % 1440
    return f"{t // 60:02d}:{t % 60:02d}"


def trading_day_of(instant: datetime) -> date:
    """The trading day an instant belongs to, as the store dates bars: its Chicago time plus seven hours, its date."""
    return (instant.astimezone(CHICAGO) + timedelta(hours=7)).date()


def load_manifest(path: Path = MANIFEST) -> dict:
    """The bar store's manifest (JSON metadata; the parquet beside it is never opened)."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _in_window(day: str) -> bool:
    return WINDOW_START.isoformat() <= day <= WINDOW_END.isoformat()


@dataclass(frozen=True)
class _StoreView:
    """The manifest's entries for window days only."""

    bounds: dict[str, list[str]]
    early: frozenset[str]
    late: frozenset[str]
    short: dict[str, int]
    degraded: dict[str, str]
    edges: dict[str, list[str]]


def _window_view(m: dict) -> _StoreView:
    days = [d for d in m.get("day_list", m.get("day_bounds", {})) if _in_window(d)]
    bounds_all = m.get("day_bounds", {})
    bounds = {d: list(bounds_all[d]) for d in days if d in bounds_all}
    early = frozenset(d for d in m.get("early_end_days", []) if _in_window(d))
    late = frozenset(d for d in m.get("late_start_days", []) if _in_window(d))
    short_all = m.get("short_days", {})
    short = {d: int(short_all[d]) for d in short_all if _in_window(d)}
    # Databento's per-UTC-date condition, looked up only for the two UTC dates a window day's session spans
    cond: dict[str, str] = {}
    for imp in m.get("imports", []):
        cond.update((imp.get("condition") or {}).get("not_available") or {})
    degraded: dict[str, str] = {}
    for d in set(bounds) | early | late | set(short):
        day = date.fromisoformat(d)
        for u in (day - timedelta(days=1), day):
            if u.isoformat() in cond:
                degraded.setdefault(d, "")
                degraded[d] = "; ".join(x for x in (degraded[d], f"Databento condition {cond[u.isoformat()]} on UTC "
                                                    f"{u.isoformat()}") if x)
    # a purchase's edge: the trading day holding an import's query start, or its last instant before the query end
    edges: dict[str, list[str]] = {}
    imports = m.get("imports", [])
    for i, imp in enumerate(imports):
        q = imp.get("query") or {}
        for key, verb, shift in (("start", "starts", timedelta(0)), ("end", "ends", timedelta(minutes=1))):
            ns = q.get(key)
            if ns is None:
                continue
            t = datetime.fromtimestamp(ns // 1_000_000_000, tz=timezone.utc)
            td = trading_day_of(t - shift).isoformat()
            if _in_window(td):
                edges.setdefault(td, []).append(
                    f"purchase edge (import {i + 1} of {len(imports)}: its query {verb} {t:%Y-%m-%dT%H:%M}Z "
                    "inside this session)")
    return _StoreView(bounds, early, late, short, degraded, edges)


def _extras(d: str, v: _StoreView) -> list[str]:
    out = []
    if d in v.late:
        out.append(f"late start (first bar {v.bounds[d][0]} CT)" if d in v.bounds else "late start")
    if d in v.short:
        out.append(f"short day {v.short[d]} bars")
    if d in v.degraded:
        out.append(v.degraded[d])
    return out


def _scheduled_note(r: Row, v: _StoreView) -> str:
    if r.date not in v.bounds:
        note = "store: no day; not shown by the store" if r.close_ct else "store: no day (as scheduled)"
    else:
        first, last = v.bounds[r.date]
        if not r.close_ct:
            note = f"store: day held (bars {first}-{last} CT); not as scheduled"
        else:
            want = _minus_one_minute(r.close_ct)
            note = (f"store: last bar {last} CT (as scheduled)" if last == want
                    else f"store: last bar {last} CT; not as scheduled (expected {want})")
    return "; ".join([note] + _extras(r.date, v))


def _defect_source(d: str, v: _StoreView) -> str:
    parts = [x for x, on in (("early_end_days", d in v.early), ("late_start_days", d in v.late)) if on]
    if d in v.bounds:
        parts.append(f"bars {v.bounds[d][0]}-{v.bounds[d][1]} CT")
    if d in v.short:
        parts.append(f"short day {v.short[d]} bars")
    reasons = v.edges.get(d, []) + ([v.degraded[d]] if d in v.degraded else [])
    reason = " and ".join(reasons) if reasons else "no reason given in the manifest"
    return "store: " + "; ".join(parts) + f"; reason: {reason}"


def build_rows(scheduled: list[Row], manifest: dict) -> list[Row]:
    """The calendar: every scheduled row annotated with what the store shows, and a `data_defect_candidate` for every
    window day the store records as ending before 15:00 CT, starting after 17:00 CT or short that no scheduled row
    covers. Sorted by date, one row a date. Only the manifest's window days are looked at."""
    v = _window_view(manifest)
    out = [Row(r.date, r.kind, r.close_ct, r.rule, f"{r.source}; {_scheduled_note(r, v)}")
           for r in scheduled if _in_window(r.date)]
    covered = {r.date for r in out}
    for d in sorted((v.early | v.late | set(v.short)) - covered):
        out.append(Row(d, "data_defect_candidate", "", "", _defect_source(d, v)))
    out.sort(key=lambda r: r.date)
    return out


def degraded_days_not_listed(manifest: dict, rows: list[Row]) -> list[tuple[str, str]]:
    """Window days the store holds whose session touches a Databento `degraded` UTC date, that the calendar does not
    list: the store shows them whole (no early end, late start or short day), so they are not candidates under the
    brief -- reported beside, for the lead. [(day, the condition note)], sorted."""
    v = _window_view(manifest)
    listed = {r.date for r in rows}
    return sorted((d, v.degraded[d]) for d in v.bounds if d in v.degraded and d not in listed)


# ---------------------------------------------------------------------------------------------------------------------
# The file
# ---------------------------------------------------------------------------------------------------------------------

_HEADER = """\
config/calendar_early_closes.csv -- Q-40 (E-022 (3)): the scheduled early closes and holidays of CME Globex
equity-index futures (NQ), trading days {start} to {end}, and the bar store's data-defect candidates.
Compiled {compiled} by scripts/build_calendar_early_closes.py (extended/calendar_early_closes.py); how it was
built: config/calendar_early_closes.md. Pinned by sha256 (LF) under a decision row and never edited: a change is a
new file under a new row.

SOURCE. CME Group's own holiday-calendar pages were NOT read: cmegroup.com answered the first scripted request
(2026-11-16) with HTTP 403 and the statement that scripts, robots and other scraping mechanisms are prohibited by
CME Group's website Data Terms of Use. The schedule is built from the standard U.S. exchange holiday rules below, as
CME applies them to its equity-index futures, and then cross-checked against the bar store's own record.

CROSS-CHECK. The bar store's manifest, vendor/stage2/data/bars/NQ/manifest.json (metadata only, no bar file read;
its entries for trading days {start} to {end} only), of the store whose parquet_sha256 is
{parquet}.

DATES are trading days as the bar store dates them: a session opens at 17:00 CT the evening before, and its bars
carry the next calendar date. CME books a holiday's abbreviated session to the next business day's trade date; the
store dates it to the holiday itself, the date given here.

KINDS.
  holiday                the NYSE is closed. close_ct blank: Globex equity-index futures are closed and hold no
                         session for the date. close_ct HH:MM: Globex trades an abbreviated session from 17:00 CT
                         the evening before and halts at close_ct; it reopens at 17:00 CT for the next trading day.
  early_close            a business day on which the NYSE closes at 13:00 ET and Globex equity-index futures at
                         close_ct.
  data_defect_candidate  a day the store's manifest lists as ending before {early_end} CT (early_end_days), starting
                         after the 17:00 CT open (late_start_days) or holding fewer than {short} bars (short_days),
                         that no rule below explains. close_ct blank (no scheduled close). For the lead's decision.
close_ct: when trading stops, Chicago time (the last one-minute bar starts a minute earlier).
source: the rule id and name, then what the store shows ("store: ..."): "(as scheduled)" when its last bar is the
minute before close_ct (or it holds no day for a closed date), "not as scheduled" / "not shown by the store"
otherwise. Read with extended.calendar_early_closes.read_calendar, or pandas.read_csv(path, comment="#",
dtype=str, keep_default_na=False).

OBSERVANCE (NYSE Rule 7.2): a holiday on a Saturday is observed the Friday before, on a Sunday the Monday after.

RULES."""


def render(rows: list[Row], manifest: dict) -> str:
    """The file's text, LF line ends: the header (provenance, kinds, every rule) and the rows."""
    for r in rows:
        if r.kind not in KINDS:
            raise ValueError(f"unknown kind: {r}")
        if not _in_window(r.date):
            raise ValueError(f"a date outside {WINDOW_START}..{WINDOW_END}: {r}")
        for x in (r.date, r.kind, r.close_ct, r.source):
            if any(c in x for c in ',"#\n\r'):
                raise ValueError(f"a field holds a comma, quote, '#' or line break: {r}")
    ds = [r.date for r in rows]
    if ds != sorted(ds) or len(ds) != len(set(ds)):
        raise ValueError("rows not sorted by date, or a date twice")
    head = _HEADER.format(start=WINDOW_START, end=WINDOW_END, compiled=COMPILED_ON,
                          parquet=manifest.get("parquet_sha256", "unknown"), early_end=STORE_EARLY_END_CT,
                          short=f"{STORE_SHORT_DAY_BARS:,}").splitlines()
    for k, (name, text) in RULES.items():
        head += textwrap.wrap(f"{k} {name}: {text}", width=116, subsequent_indent="    ",
                              break_long_words=False, break_on_hyphens=False)
    buf = io.StringIO()
    for ln in head:
        buf.write(("# " + ln).rstrip() + "\n")
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(COLUMNS)
    for r in rows:
        w.writerow([r.date, r.kind, r.close_ct, r.source])
    return buf.getvalue()


def read_calendar(path: Path = CALENDAR_CSV) -> list[dict[str, str]]:
    """The calendar's rows as dicts of strings (the '#' header skipped; a blank close_ct stays "")."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return list(csv.DictReader([ln for ln in lines if ln and not ln.startswith("#")]))


__all__ = ["WINDOW_START", "WINDOW_END", "CONFIRMATION_START", "CALENDAR_CSV", "MANIFEST", "COLUMNS", "KINDS",
           "RULES", "Row", "easter_sunday", "observed", "observed_new_year", "employment_situation_dates",
           "scheduled_rows", "session_minute", "trading_day_of", "load_manifest", "build_rows", "render",
           "read_calendar"]
