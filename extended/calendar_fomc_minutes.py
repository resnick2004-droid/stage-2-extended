"""Q-79 (from Q-73's research note): the calendar of the release days of the FOMC's minutes inside NQ's development
window, 2020-01-02 to 2026-07-16, with each release's time -- so that a reading names TradeDay's FOMC-minutes windows
(`tradeday.tier1_release_list`, 1:00 PM CT) from a calendar fixed in advance, as E-029 fixed the early closes.

    from extended import calendar_fomc_minutes as M
    rows = M.read_calendar(M.CALENDAR_CSV)          # [{"release_date", "meeting_end", "time_et", "time_ct", ...}, ...]
    days = M.release_days()                         # [date, ...], sorted
    python scripts/build_calendar_fomc_minutes.py   # (re)builds config/calendar_fomc_minutes.csv; --check compares

**Where the values come from.** The research CSV `docs/research/fomc_minutes_dates_2026-11-16.csv` and its note (the
scout's Q-73 read of federalreserve.gov, 2026-11-16): each release date as the Federal Reserve's FOMC calendar pages
state it, confirmed on the minutes' own press release; each time as that press release prints it ("For release at
2:00 p.m." ET). The builder takes the CSV only at the sha256 its note states (`RESEARCH_CSV_SHA256`), copies its rows
unchanged, adds the Chicago time (converted on the date) and refuses: a date outside the window or from 2026-07-17, a
duplicate or unsorted date, a meeting not before its minutes, a time other than 14:00 ET, a page other than the three
calendar pages, and a release day that is an FOMC statement day of Stage 2's vendored calendars.

The dates are read, never computed from the calendar page's "three weeks after the policy decision": that rule does
not give every date here (the note's section 5).

Nothing here draws randomness; nothing reads a bar.
"""
from __future__ import annotations

import csv
import hashlib
import io
import re
from dataclasses import astuple, dataclass
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from extended import ROOT, VENDOR_STAGE2
from extended import calendar_early_closes as _early
from extended.calendar_early_closes import CONFIRMATION_START, WINDOW_END, WINDOW_START

#: the date the calendar was compiled (fixed, so a rebuild is byte-identical)
COMPILED_ON = "2026-11-16"

CALENDAR_CSV = ROOT / "config" / "calendar_fomc_minutes.csv"
RESEARCH_CSV = ROOT / "docs" / "research" / "fomc_minutes_dates_2026-11-16.csv"
RESEARCH_NOTE = ROOT / "docs" / "research" / "fomc_minutes_dates_2026-11-16.md"
#: the research CSV's sha256 (of its LF text) as its note states it (section 7): the builder reads no other text
RESEARCH_CSV_SHA256 = "3a50340f0b9a1d6248cd2c93cc1b5956f798727aae9f950c55a38901f7b7d81a"
#: the pinned early-close calendar (E-029), for the overlaps the header names
EARLY_CLOSES_CSV = _early.CALENDAR_CSV
#: Stage 2's vendored FOMC statement days: the `date` column of every file matching this, and the FOMC rows of IM2's
STATEMENT_SOURCES_DIR = VENDOR_STAGE2 / "config" / "sources"
STATEMENT_SOURCES_GLOB = "fomc_*.csv"
IM2_CALENDAR = VENDOR_STAGE2 / "config" / "im2_release_calendar.csv"

RESEARCH_COLUMNS = ("meeting_end", "minutes_release_date", "release_time_et", "source_url", "accessed")
COLUMNS = ("release_date", "meeting_end", "time_et", "time_ct", "date_source", "accessed")

#: the Federal Reserve's FOMC calendar pages a release date may come from -> what each carries here
DATE_PAGES: dict[str, str] = {
    "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm": "meetings of 2021 on",
    "https://www.federalreserve.gov/monetarypolicy/fomchistorical2020.htm": "meetings of 2020",
    "https://www.federalreserve.gov/monetarypolicy/fomchistorical2019.htm": "the December 10-11, 2019 meeting",
}
#: the minutes' press release, the source of the time: the release date without hyphens in place of {ymd}
PRESS_RELEASE_URL = "https://www.federalreserve.gov/newsevents/pressreleases/monetary{ymd}a.htm"
#: "For release at 2:00 p.m." on every press release read: the only time this calendar's header vouches for
RELEASE_TIME_ET = "14:00"

NEW_YORK = ZoneInfo("America/New_York")
CHICAGO = ZoneInfo("America/Chicago")

_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_HHMM = re.compile(r"^\d{2}:\d{2}$")
_BAD_CHARS = ',"#\n\r'


@dataclass(frozen=True)
class Row:
    """One release: the day, the meeting (its policy-decision day), the time in ET and CT, the page, the access day."""

    release_date: str
    meeting_end: str
    time_et: str
    time_ct: str
    date_source: str
    accessed: str


def _iso(s: str, what: str) -> date:
    if not _ISO.match(s):
        raise ValueError(f"{what} is not a YYYY-MM-DD date: {s!r}")
    return date.fromisoformat(s)


def press_release_url(release_date: str) -> str:
    """The URL of the minutes' press release for a release day (the source of its time)."""
    return PRESS_RELEASE_URL.format(ymd=_iso(release_date, "release date").strftime("%Y%m%d"))


def et_to_ct(day: str, hhmm: str) -> str:
    """The Chicago clock time of `hhmm` New York time on `day` (converted by the zones on that date)."""
    if not _HHMM.match(hhmm):
        raise ValueError(f"not an HH:MM time: {hhmm!r}")
    h, m = (int(x) for x in hhmm.split(":"))
    t = datetime(*_iso(day, "day").timetuple()[:3], h, m, tzinfo=NEW_YORK).astimezone(CHICAGO)
    if t.date().isoformat() != day:
        raise ValueError(f"{day} {hhmm} ET is another day in Chicago")
    return t.strftime("%H:%M")


# ---------------------------------------------------------------------------------------------------------------------
# The inputs
# ---------------------------------------------------------------------------------------------------------------------

def read_research(path: Path = RESEARCH_CSV, sha256: str = RESEARCH_CSV_SHA256) -> list[dict[str, str]]:
    """The research CSV's rows (dicts of strings), refused unless its LF text hashes to `sha256` and its header is
    `RESEARCH_COLUMNS` with no comment line."""
    data = Path(path).read_bytes().replace(b"\r\n", b"\n")
    got = hashlib.sha256(data).hexdigest()
    if got != sha256:
        raise ValueError(f"{path}: sha256 {got} of its LF text, not {sha256} (another research text is never read)")
    lines = data.decode("utf-8").splitlines()
    if not lines or lines[0] != ",".join(RESEARCH_COLUMNS):
        raise ValueError(f"{path}: header {lines[:1]} is not {','.join(RESEARCH_COLUMNS)}")
    if any(ln.startswith("#") or not ln for ln in lines):
        raise ValueError(f"{path}: a comment or blank line")
    rows = list(csv.DictReader(lines))
    for r in rows:
        if None in r or None in r.values():
            raise ValueError(f"{path}: a row of the wrong width: {r}")
    return rows


def fomc_statement_days(sources_dir: Path = STATEMENT_SOURCES_DIR, im2: Path = IM2_CALENDAR) -> set[str]:
    """Every FOMC statement day Stage 2 vendored: the `date` column of `sources_dir/fomc_*.csv` ('#' lines skipped) and
    the `FOMC` rows of IM2's release calendar. Federal Reserve calendar dates, not market data."""
    out: set[str] = set()
    for p in sorted(Path(sources_dir).glob(STATEMENT_SOURCES_GLOB)):
        body = [ln for ln in p.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
        out |= {r["date"] for r in csv.DictReader(body)}
    with open(im2, newline="", encoding="utf-8") as fh:
        out |= {r["date"] for r in csv.DictReader(fh) if r["code"] == "FOMC"}
    return out


# ---------------------------------------------------------------------------------------------------------------------
# The build
# ---------------------------------------------------------------------------------------------------------------------

def build_rows(research: list[dict[str, str]], statement_days: set[str] | None = None) -> list[Row]:
    """The calendar's rows from the research rows, in their order, values unchanged, `time_ct` added. Refuses what the
    module docstring lists. `statement_days`: the FOMC statement days no release may fall on (default: the vendored
    ones, `fomc_statement_days()`)."""
    if statement_days is None:
        statement_days = fomc_statement_days()
    out: list[Row] = []
    for r in research:
        meeting_end, release, time_et, url, accessed = (r[c] for c in RESEARCH_COLUMNS)
        for x in (meeting_end, release, time_et, url, accessed):
            if any(c in x for c in _BAD_CHARS):
                raise ValueError(f"a field holds a comma, quote, '#' or line break: {r}")
        d = _iso(release, "minutes_release_date")
        m = _iso(meeting_end, "meeting_end")
        _iso(accessed, "accessed")
        if d >= CONFIRMATION_START:
            raise ValueError(f"{release} lies in NQ's reserve (from {CONFIRMATION_START}): never in this calendar")
        if not WINDOW_START <= d <= WINDOW_END:
            raise ValueError(f"{release} lies outside {WINDOW_START}..{WINDOW_END}")
        if d.weekday() > 4:
            raise ValueError(f"{release} is a weekend day")
        if not m < d:
            raise ValueError(f"meeting {meeting_end} is not before its minutes' release {release}")
        if time_et != RELEASE_TIME_ET:
            raise ValueError(f"{release}: release time {time_et!r} ET; the press releases read print 2:00 p.m. only")
        if url not in DATE_PAGES:
            raise ValueError(f"{release}: {url} is not one of the Federal Reserve's FOMC calendar pages")
        if release in statement_days:
            raise ValueError(f"{release} is an FOMC statement day of the vendored calendars")
        out.append(Row(release, meeting_end, time_et, et_to_ct(release, time_et), url, accessed))
    ds = [r.release_date for r in out]
    if ds != sorted(ds) or len(ds) != len(set(ds)):
        raise ValueError("release dates not sorted, or a date twice")
    ms = [r.meeting_end for r in out]
    if len(ms) != len(set(ms)):
        raise ValueError("a meeting twice")
    return out


def early_close_overlaps(rows: list[Row], path: Path = EARLY_CLOSES_CSV) -> list[tuple[str, str, str]]:
    """The release days the pinned early-close calendar also lists: [(date, kind, close_ct)], sorted."""
    early = {r["date"]: (r["kind"], r["close_ct"]) for r in _early.read_calendar(path)}
    return sorted((r.release_date, *early[r.release_date]) for r in rows if r.release_date in early)


def _overlap_line(day: str, kind: str, close_ct: str, time_ct: str) -> str:
    if close_ct:
        when = "after" if time_ct > close_ct else ("at" if time_ct == close_ct else "before")
        what = f"{kind}; trading stops {close_ct} CT: the release at {time_ct} CT comes {when} it"
    elif kind == "holiday":
        what = f"{kind}; no Globex session for the date"
    else:
        what = f"{kind} (E-029 decides which such days families void)"
    return f"  {day}  {what}"


_HEADER = """\
config/calendar_fomc_minutes.csv -- Q-79: the release days of the minutes of the Federal Open Market Committee
(FOMC) inside NQ's development window, {start} to {end} (nothing from {conf}), with each release's time:
{n} releases, {first} to {last}. Compiled {compiled} by scripts/build_calendar_fomc_minutes.py
(extended/calendar_fomc_minutes.py) from docs/research/fomc_minutes_dates_2026-11-16.csv, rows copied unchanged
(sha256 of its LF text {sha}); its note,
docs/research/fomc_minutes_dates_2026-11-16.md, records how every value was read. Pinned by sha256 (LF) under a
decision row and never edited: a change is a new file under a new row.

DATES come from the Federal Reserve's own FOMC calendar pages, read {accessed}; each row's date_source names the
page its date was read from:
{pages}
A meeting's minutes cell reads "(Released <date>)". Every date was confirmed on the minutes' own press release,
which prints the same date. The dates are read, never inferred: the calendar page's "three weeks after the date of
the policy decision" does not give every date here (the note's section 5).

TIME comes from the minutes' press release, at the URL (the release date without hyphens for <YYYYMMDD>):
  {press_rule}
Each prints one of
  "For release at 2:00 p.m. EST"  or  "For release at 2:00 p.m. EDT"
as daylight saving stood on its date: {time_et} ET. The calendar pages print no time. time_ct is the same instant in
Chicago, converted on the date (America/New_York to America/Chicago). The sha256 of every page and press release as
fetched is in the note (section 1 and Appendix A).

COLUMNS.
  release_date  the day the minutes were released (the calendar page's "Released" date)
  meeting_end   the meeting the minutes belong to, named by its policy-decision day (its last day; the date in its
                minutes file's name, monetarypolicy/fomcminutes<YYYYMMDD>.htm)
  time_et       the release time, Eastern (HH:MM, 24-hour clock)
  time_ct       the same instant, Central (Chicago)
  date_source   the calendar page the release date was read from
  accessed      the day the pages were read

NO MINUTES OF THEIR OWN (the note's section 4): the March 2, 2020 unscheduled meeting (its minutes follow the March
15, 2020 meeting's, released 2020-04-08); the cancelled March 17-18, 2020 meeting; the notation votes of 2020-03-19,
2020-03-23, 2020-03-31, 2020-08-27 and 2025-08-22.
STATEMENT DAYS. No release day here is an FOMC statement day of Stage 2's vendored calendars
(vendor/stage2/config/sources/fomc_*.csv; the FOMC rows of vendor/stage2/config/im2_release_calendar.csv): the
builder refuses one, and tests/test_calendar_fomc_minutes.py checks it.
EARLY CLOSES. The release days config/calendar_early_closes.csv (E-029) also lists. Their rows stay here; the
reading that uses this file resolves them:
{overlaps}
Read with extended.calendar_fomc_minutes.read_calendar (or release_days), or pandas.read_csv(path, comment="#",
dtype=str, keep_default_na=False)."""


def render(rows: list[Row], research_sha256: str, overlaps: list[tuple[str, str, str]]) -> str:
    """The file's text, LF line ends: the header (provenance, sources, columns, the overlaps) and the rows."""
    if not rows:
        raise ValueError("no rows")
    by = {r.release_date: r for r in rows}
    for d, *_ in overlaps:
        if d not in by:
            raise ValueError(f"an overlap {d} that is no release day here")
    for r in rows:
        for x in astuple(r):
            if any(c in x for c in _BAD_CHARS):
                raise ValueError(f"a field holds a comma, quote, '#' or line break: {r}")
    head = _HEADER.format(
        start=WINDOW_START, end=WINDOW_END, conf=CONFIRMATION_START, n=len(rows), first=rows[0].release_date,
        last=rows[-1].release_date, compiled=COMPILED_ON, sha=research_sha256,
        accessed=" and ".join(sorted({r.accessed for r in rows})),
        pages="\n".join(f"  {u:<70}{w}" for u, w in DATE_PAGES.items()),
        press_rule=PRESS_RELEASE_URL.format(ymd="<YYYYMMDD>"), time_et=RELEASE_TIME_ET,
        overlaps="\n".join(_overlap_line(d, k, c, by[d].time_ct) for d, k, c in overlaps) or "  (none)",
    ).splitlines()
    buf = io.StringIO()
    for ln in head:
        buf.write(("# " + ln).rstrip() + "\n")
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(COLUMNS)
    for r in rows:
        w.writerow(astuple(r))
    return buf.getvalue()


# ---------------------------------------------------------------------------------------------------------------------
# The loader
# ---------------------------------------------------------------------------------------------------------------------

def read_calendar(path: Path = CALENDAR_CSV) -> list[dict[str, str]]:
    """The calendar's rows as dicts of strings, in file order (the '#' header skipped)."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return list(csv.DictReader([ln for ln in lines if ln and not ln.startswith("#")]))


def release_days(path: Path = CALENDAR_CSV) -> list[date]:
    """The release days, sorted."""
    return sorted(date.fromisoformat(r["release_date"]) for r in read_calendar(path))


__all__ = ["WINDOW_START", "WINDOW_END", "CONFIRMATION_START", "COMPILED_ON", "CALENDAR_CSV", "RESEARCH_CSV",
           "RESEARCH_NOTE", "RESEARCH_CSV_SHA256", "RESEARCH_COLUMNS", "COLUMNS", "DATE_PAGES", "PRESS_RELEASE_URL",
           "RELEASE_TIME_ET", "Row", "press_release_url", "et_to_ct", "read_research", "fomc_statement_days",
           "build_rows", "early_close_overlaps", "render", "read_calendar", "release_days"]
