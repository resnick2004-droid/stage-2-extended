"""Q-79 (from Q-73's research note): the calendar of FOMC minutes release days, `config/calendar_fomc_minutes.csv`.

Four groups:

* **the builder** (`extended.calendar_fomc_minutes`) on synthetic input: the time conversion, the press-release URL
  rule, and every refusal (a date outside 2020-01-02..2026-07-16 or from 2026-07-17, a duplicate, an unsorted input, a
  time other than 14:00 ET, an unknown date page, a meeting after its minutes, a statement day, another research text);
* **the research input** against its own note: the CSV's sha256 is the note's, and the note's table (meeting, release
  date, weekday, the press release's verbatim time line and its URL) agrees with the CSV row for row;
* **the file**: 53 rows, distinct dates inside the window, every time 14:00 ET = 13:00 CT, none on an FOMC statement
  day of Stage 2's vendored calendars (read here by this test's own parser), every meeting a vendored statement day,
  the note's warnings kept (the dates are not the "three weeks" rule; the two early-close overlaps stay);
* **the rebuild**: the builder reproduces the committed file byte for byte (LF), in memory and through the script.

Nothing here reads a bar; nothing draws randomness.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import re
from collections import Counter
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from extended import ROOT, VENDOR_STAGE2
from extended import calendar_fomc_minutes as M

NOTE = ROOT / "docs" / "research" / "fomc_minutes_dates_2026-11-16.md"
RESEARCH = ROOT / "docs" / "research" / "fomc_minutes_dates_2026-11-16.csv"
SCRIPT = ROOT / "scripts" / "build_calendar_fomc_minutes.py"
NEW_YORK = ZoneInfo("America/New_York")

# ---------------------------------------------------------------------------------------------------------------------
# Independent lists, typed from the research note (docs/research/fomc_minutes_dates_2026-11-16.md), not from the code
# ---------------------------------------------------------------------------------------------------------------------

#: section 3: releases a calendar year inside 2020-01-02..2026-07-16
PER_YEAR = {2020: 8, 2021: 8, 2022: 8, 2023: 8, 2024: 8, 2025: 9, 2026: 4}
#: section 5 (1): the releases that are NOT 21 days after the policy decision (days after it)
NOT_THREE_WEEKS = {"2020-01-03": 23, "2020-04-08": 24, "2020-11-25": 20, "2023-11-21": 20, "2025-12-30": 20,
                   "2024-11-26": 19}
#: section 5 (1): the releases not on a Wednesday
NOT_WEDNESDAY = {"2020-01-03", "2023-11-21", "2024-11-26", "2025-12-30"}
#: section 5 (3): the release days config/calendar_early_closes.csv also lists -> (kind, close_ct)
EARLY_CLOSE_OVERLAPS = {"2020-07-01": ("data_defect_candidate", ""), "2024-07-03": ("early_close", "12:15")}
#: section 4: calendar entries with no minutes of their own (their dates are never a meeting here)
NO_MINUTES_OF_THEIR_OWN = {"2020-03-02", "2020-03-03", "2020-03-18", "2020-03-19", "2020-03-23", "2020-03-31",
                           "2020-08-27", "2025-08-22"}
#: section 6: FOMC statement days of the vendored files inside the window, the unscheduled 2020 ones included
STATEMENT_DAYS_IN_WINDOW = 54
DATE_PAGES = {"https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
              "https://www.federalreserve.gov/monetarypolicy/fomchistorical2020.htm",
              "https://www.federalreserve.gov/monetarypolicy/fomchistorical2019.htm"}


def _vendored_statement_days() -> set[str]:
    """This test's own reading of every FOMC statement day Stage 2 vendored: the `date` column of
    vendor/stage2/config/sources/fomc_*.csv ('#' comment lines skipped) and the `FOMC` rows of
    vendor/stage2/config/im2_release_calendar.csv."""
    out: set[str] = set()
    paths = sorted((VENDOR_STAGE2 / "config" / "sources").glob("fomc_*.csv"))
    assert len(paths) == 4, paths
    for p in paths:
        body = [ln for ln in p.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
        rows = list(csv.DictReader(body))
        assert rows, p
        out |= {r["date"] for r in rows}
    with open(VENDOR_STAGE2 / "config" / "im2_release_calendar.csv", newline="", encoding="utf-8") as fh:
        fomc = [r for r in csv.DictReader(fh) if r["code"] == "FOMC"]
    assert fomc and {r["release"] for r in fomc} == {"FOMC statement"}
    out |= {r["date"] for r in fomc}
    for d in out:
        date.fromisoformat(d)
    return out


def _research_row(meeting_end: str, release: str, time_et: str = "14:00",
                  url: str = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
                  accessed: str = "2026-11-16") -> dict[str, str]:
    return dict(zip(M.RESEARCH_COLUMNS, (meeting_end, release, time_et, url, accessed)))


def _file_rows() -> list[dict[str, str]]:
    return M.read_calendar(M.CALENDAR_CSV)


def _lf(path: Path) -> str:
    return path.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")


# ---------------------------------------------------------------------------------------------------------------------
# The builder, on synthetic input
# ---------------------------------------------------------------------------------------------------------------------

def test_et_to_ct_converts_on_the_date():
    for d in ("2020-01-03", "2020-07-01", "2024-03-10", "2024-11-03", "2025-12-30", "2026-07-08"):
        assert M.et_to_ct(d, "14:00") == "13:00", d
    assert M.et_to_ct("2024-06-12", "08:30") == "07:30"
    # the conversion is the zones', not a fixed hour: an instant in the hour when New York has changed clocks and
    # Chicago has not yet (2024-03-10 02:30 CST = 03:30 EDT)
    assert M.et_to_ct("2024-03-10", "03:30") == "01:30"
    with pytest.raises(ValueError):
        M.et_to_ct("2024-01-03", "2:00")


def test_press_release_url_rule():
    assert M.press_release_url("2020-02-19") == \
        "https://www.federalreserve.gov/newsevents/pressreleases/monetary20200219a.htm"


def test_build_rows_converts_and_keeps_the_research_values():
    rows = M.build_rows([_research_row("2019-12-11", "2020-01-03",
                                       url="https://www.federalreserve.gov/monetarypolicy/fomchistorical2019.htm"),
                         _research_row("2024-06-12", "2024-07-03")], statement_days=set())
    assert [(r.release_date, r.meeting_end, r.time_et, r.time_ct, r.accessed) for r in rows] == [
        ("2020-01-03", "2019-12-11", "14:00", "13:00", "2026-11-16"),
        ("2024-07-03", "2024-06-12", "14:00", "13:00", "2026-11-16")]
    assert rows[0].date_source.endswith("fomchistorical2019.htm")


@pytest.mark.parametrize("bad, why", [
    ([("2019-12-11", "2020-01-01")], "before the window"),
    ([("2026-06-17", "2026-07-17")], "the confirmation window"),
    ([("2026-07-29", "2026-08-19")], "the confirmation window"),
    ([("2024-06-12", "2024-07-03"), ("2024-06-12", "2024-07-03")], "twice"),
    ([("2024-07-31", "2024-08-21"), ("2024-06-12", "2024-07-03")], "not sorted"),
    ([("2024-07-03", "2024-07-03")], "meeting not before"),
    ([("2024-07-04", "2024-07-03")], "meeting not before"),
])
def test_build_rows_refuses_bad_dates(bad, why):
    with pytest.raises(ValueError):
        M.build_rows([_research_row(m, r) for m, r in bad], statement_days=set())


def test_build_rows_refuses_other_times_pages_and_values():
    with pytest.raises(ValueError):  # the header's time source covers 2:00 p.m. releases only
        M.build_rows([_research_row("2024-06-12", "2024-07-03", time_et="14:30")], statement_days=set())
    with pytest.raises(ValueError):  # not one of the Federal Reserve's calendar pages
        M.build_rows([_research_row("2024-06-12", "2024-07-03", url="https://example.com/fomc.htm")],
                     statement_days=set())
    with pytest.raises(ValueError):
        M.build_rows([_research_row("2024-06-12", "2024-07-03", accessed="16 Nov 2026")], statement_days=set())
    with pytest.raises(ValueError):
        M.build_rows([_research_row("2024-06-12", "2024-7-3")], statement_days=set())
    with pytest.raises(ValueError):  # a field the CSV could not carry plainly
        M.build_rows([_research_row("2024-06-12", "2024-07-03",
                                    url="https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm,x")],
                     statement_days=set())


def test_build_rows_refuses_a_statement_day():
    rows = [_research_row("2024-06-12", "2024-07-03")]
    assert M.build_rows(rows, statement_days={"2024-06-12"})  # the meeting's own statement day is expected
    with pytest.raises(ValueError):
        M.build_rows(rows, statement_days={"2024-07-03"})


def test_read_research_refuses_another_text(tmp_path):
    good = RESEARCH.read_bytes().replace(b"\r\n", b"\n")
    p = tmp_path / "r.csv"
    p.write_bytes(good.replace(b"2024-07-03", b"2024-07-02"))
    with pytest.raises(ValueError):
        M.read_research(p)
    p.write_bytes(good.replace(b"\n", b"\r\n"))  # a CRLF checkout of the same text is the same text
    assert M.read_research(p) == M.read_research(RESEARCH)
    q = tmp_path / "q.csv"
    q.write_bytes(good.replace(b"meeting_end,", b"meeting,", 1))
    with pytest.raises(ValueError):
        M.read_research(q, sha256=hashlib.sha256(q.read_bytes()).hexdigest())


def test_render_reads_back(tmp_path):
    rows = M.build_rows([_research_row("2024-06-12", "2024-07-03"), _research_row("2024-07-31", "2024-08-21")],
                        statement_days=set())
    text = M.render(rows, research_sha256="0" * 64, overlaps=[("2024-07-03", "early_close", "12:15")])
    assert "\r" not in text and text.endswith("\n")
    assert all(len(ln) <= 120 for ln in text.splitlines())
    p = tmp_path / "c.csv"
    p.write_text(text, encoding="utf-8", newline="\n")
    got = M.read_calendar(p)
    assert [tuple(r.values()) for r in got] == [
        ("2024-07-03", "2024-06-12", "14:00", "13:00", "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
         "2026-11-16"),
        ("2024-08-21", "2024-07-31", "14:00", "13:00", "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
         "2026-11-16")]
    assert M.release_days(p) == [date(2024, 7, 3), date(2024, 8, 21)]


# ---------------------------------------------------------------------------------------------------------------------
# The research input, against its own note
# ---------------------------------------------------------------------------------------------------------------------

def _note_table() -> list[list[str]]:
    """The note's section 2 table: one list of cells a row (`| # | meeting | meeting_end | released | ...`)."""
    out = []
    section = NOTE.read_text(encoding="utf-8").split("\n## 2. The table", 1)[1].split("\n## 3. ", 1)[0]
    for ln in section.splitlines():
        if re.match(r"^\| \d+ \| ", ln):
            out.append([c.strip() for c in ln.strip().strip("|").split("|")])
    return out


def test_the_research_csv_is_the_notes():
    assert hashlib.sha256(RESEARCH.read_bytes().replace(b"\r\n", b"\n")).hexdigest() == M.RESEARCH_CSV_SHA256
    assert f"`{M.RESEARCH_CSV_SHA256}`" in NOTE.read_text(encoding="utf-8")
    assert M.RESEARCH_CSV == RESEARCH and M.RESEARCH_NOTE == NOTE


def test_the_notes_table_agrees_with_the_research_row_for_row():
    table = _note_table()
    research = M.read_research()
    assert len(table) == len(research) == 53
    for i, (cells, r) in enumerate(zip(table, research), start=1):
        num, _label, meeting_end, released, _days, time_line, date_from, time_from, accessed = cells
        assert int(num) == i
        assert meeting_end == r["meeting_end"]
        m = re.fullmatch(r"\*\*(\d{4}-\d{2}-\d{2})\*\* \((\w{3})\)", released)
        assert m and m.group(1) == r["minutes_release_date"], released
        assert date.fromisoformat(m.group(1)).strftime("%a") == m.group(2), released
        assert (date.fromisoformat(m.group(1)) - date.fromisoformat(meeting_end)).days == int(_days)
        # the press release's verbatim time line: 2:00 p.m., labelled by the zone New York was in on that day
        zone = datetime.combine(date.fromisoformat(m.group(1)), time(14, 0), tzinfo=NEW_YORK).tzname()
        assert time_line == f'"For release at 2:00 p.m. {zone}"', (i, time_line)
        assert r["release_time_et"] == "14:00"
        # the date's page and the time's page, as linked
        assert date_from == f"[`{r['source_url'].rsplit('/', 1)[1]}`]({r['source_url']})", date_from
        pr = M.press_release_url(r["minutes_release_date"])
        assert time_from == f"[`{pr.rsplit('/', 1)[1]}`]({pr})", time_from
        assert accessed == r["accessed"] == "2026-11-16"


def test_the_notes_appendix_lists_the_same_releases():
    text = NOTE.read_text(encoding="utf-8").split("## Appendix A", 1)[1]
    got = re.findall(r"^\| (\d{4}-\d{2}-\d{2}) \| `monetary(\d{8})a\.htm` \|", text, flags=re.M)
    assert [d for d, _ in got] == [r["minutes_release_date"] for r in M.read_research()]
    assert all(d.replace("-", "") == ymd for d, ymd in got)


# ---------------------------------------------------------------------------------------------------------------------
# The file
# ---------------------------------------------------------------------------------------------------------------------

def test_the_file_parses_with_its_columns_and_53_rows():
    text = _lf(M.CALENDAR_CSV)
    body = [ln for ln in text.splitlines() if ln and not ln.startswith("#")]
    assert body[0] == ",".join(M.COLUMNS)
    rows = list(csv.DictReader(body))
    assert len(rows) == 53
    assert all(set(r) == set(M.COLUMNS) and None not in r.values() and all(r.values()) for r in rows)
    assert rows == _file_rows()
    assert [r["release_date"] for r in rows] == [d.isoformat() for d in M.release_days()]


def test_the_files_dates_are_distinct_sorted_and_inside_the_development_window():
    rows = _file_rows()
    ds = [r["release_date"] for r in rows]
    assert ds == sorted(ds) and len(ds) == len(set(ds))
    assert len({r["meeting_end"] for r in rows}) == len(rows)
    for r in rows:
        d = date.fromisoformat(r["release_date"])
        assert date(2020, 1, 2) <= d <= date(2026, 7, 16), r
        assert d < date(2026, 7, 17), r
        assert d.weekday() < 5, r
        assert date.fromisoformat(r["meeting_end"]) < d, r
        assert r["date_source"] in DATE_PAGES, r
    assert Counter(date.fromisoformat(d).year for d in ds) == PER_YEAR


def test_every_time_is_14_00_et_and_13_00_ct():
    rows = _file_rows()
    assert {r["time_et"] for r in rows} == {"14:00"}
    assert {r["time_ct"] for r in rows} == {"13:00"}
    for r in rows:  # converted on the day, by this test's own arithmetic
        t = datetime.combine(date.fromisoformat(r["release_date"]), time(14, 0), tzinfo=NEW_YORK)
        assert t.astimezone(ZoneInfo("America/Chicago")).strftime("%H:%M") == r["time_ct"], r


def test_no_release_day_is_an_fomc_statement_day():
    stmt = _vendored_statement_days()
    assert len({d for d in stmt if "2020-01-02" <= d <= "2026-07-16"}) == STATEMENT_DAYS_IN_WINDOW
    for known in ("2020-01-29", "2020-03-03", "2020-03-15", "2024-07-31", "2026-06-17"):
        assert known in stmt, known
    rows = _file_rows()
    assert not {r["release_date"] for r in rows} & stmt
    # and every meeting the minutes belong to is a statement day of the same files (2019-12-11 included)
    assert {r["meeting_end"] for r in rows} <= stmt
    assert M.fomc_statement_days() == stmt


def test_the_dates_are_read_not_the_three_weeks_rule():
    rows = _file_rows()
    gap = {r["release_date"]: (date.fromisoformat(r["release_date"]) - date.fromisoformat(r["meeting_end"])).days
           for r in rows}
    assert {d: g for d, g in gap.items() if g != 21} == NOT_THREE_WEEKS
    assert {d for d in gap if date.fromisoformat(d).weekday() != 2} == NOT_WEDNESDAY
    # the unscheduled March 15, 2020 meeting has its own minutes (with the March 2 call's); no cancelled meeting,
    # notation vote or the March 2 call is a meeting here
    assert {r["meeting_end"]: r["release_date"] for r in rows}["2020-03-15"] == "2020-04-08"
    assert not {r["meeting_end"] for r in rows} & NO_MINUTES_OF_THEIR_OWN


def test_the_early_close_overlaps_are_kept_and_named():
    from extended import calendar_early_closes as C
    early = {r["date"]: (r["kind"], r["close_ct"]) for r in C.read_calendar(C.CALENDAR_CSV)}
    rows = _file_rows()
    got = {r["release_date"]: early[r["release_date"]] for r in rows if r["release_date"] in early}
    assert got == EARLY_CLOSE_OVERLAPS
    assert M.early_close_overlaps(M.build_rows(M.read_research())) == sorted(
        (d, k, c) for d, (k, c) in EARLY_CLOSE_OVERLAPS.items())
    text = _lf(M.CALENDAR_CSV)
    for d in EARLY_CLOSE_OVERLAPS:
        assert d in text.split("\nrelease_date,", 1)[0], d  # named in the header


def test_the_header_names_the_sources():
    head = _lf(M.CALENDAR_CSV).split("\nrelease_date,", 1)[0]
    assert all(ln.startswith("#") and len(ln) <= 120 for ln in head.splitlines())
    for url in DATE_PAGES:
        assert url in head, url
    assert "https://www.federalreserve.gov/newsevents/pressreleases/monetary<YYYYMMDD>a.htm" in head
    assert "For release at 2:00 p.m. EST" in head and "EDT" in head
    assert "docs/research/fomc_minutes_dates_2026-11-16.md" in head
    assert "docs/research/fomc_minutes_dates_2026-11-16.csv" in head
    assert M.RESEARCH_CSV_SHA256 in head
    assert "scripts/build_calendar_fomc_minutes.py" in head


# ---------------------------------------------------------------------------------------------------------------------
# The rebuild
# ---------------------------------------------------------------------------------------------------------------------

def _script():
    spec = importlib.util.spec_from_file_location("build_calendar_fomc_minutes", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_file_rebuilds_byte_for_byte():
    rows = M.build_rows(M.read_research())
    built = M.render(rows, research_sha256=M.RESEARCH_CSV_SHA256, overlaps=M.early_close_overlaps(rows))
    assert built == _lf(M.CALENDAR_CSV)


def test_the_script_checks_and_writes_the_same_bytes_twice(tmp_path, capsys):
    s = _script()
    assert s.main(["--check"]) == 0
    out = tmp_path / "calendar_fomc_minutes.csv"
    assert s.main(["--out", str(out)]) == 0
    first = out.read_bytes()
    assert s.main(["--out", str(out)]) == 0  # the same text again: written, identical
    assert out.read_bytes() == first
    assert b"\r" not in first
    assert first.decode("utf-8") == _lf(M.CALENDAR_CSV)
    lf_sha = hashlib.sha256(first).hexdigest()
    assert f"LF sha256 {lf_sha}" in capsys.readouterr().out
    # a different file on disk is never replaced without --force
    out.write_bytes(first.replace(b"2024-07-03", b"2024-07-02"))
    assert s.main(["--out", str(out)]) == 1
    assert s.main(["--out", str(out), "--check"]) == 1
    assert s.main(["--out", str(out), "--force"]) == 0 and out.read_bytes() == first
