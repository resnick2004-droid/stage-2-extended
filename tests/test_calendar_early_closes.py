"""Q-40 (E-022 (3)): the pinned calendar of scheduled early closes, holidays and data-defect candidates.

Three groups:

* **the rules** (`extended.calendar_early_closes`) against lists typed here independently of the code -- the NYSE's
  holidays and 13:00 ET early closes for 2020-2026 as the exchange published them -- so a rule written wrong (an
  observance, an nth weekday, Easter) fails here and not silently in the file;
* **the cross-check** against the bar store's manifest, on synthetic manifests only (no bar, no real manifest);
* **the file** `config/calendar_early_closes.csv`: it parses, is sorted, holds no date outside 2020-01-02..2026-07-16
  and none from 2026-07-17; its scheduled rows are exactly what the rules give; and, where the store's manifest is
  present (a worktree's junction), rebuilding it reproduces it byte for byte (LF).
"""
from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path

import pytest

from extended import calendar_early_closes as C

# ---------------------------------------------------------------------------------------------------------------------
# Independent lists (typed from the NYSE's published holiday and early-close schedules, not from the code)
# ---------------------------------------------------------------------------------------------------------------------

#: NYSE full-day closures inside 2020-01-02..2026-07-16 (2020-01-01 lies before the window's first day;
#: 2022-01-01 fell on a Saturday and was not observed; 2025-01-09 is the National Day of Mourning for President Carter)
NYSE_CLOSED = {
    2020: ["01-20", "02-17", "04-10", "05-25", "07-03", "09-07", "11-26", "12-25"],
    2021: ["01-01", "01-18", "02-15", "04-02", "05-31", "07-05", "09-06", "11-25", "12-24"],
    2022: ["01-17", "02-21", "04-15", "05-30", "06-20", "07-04", "09-05", "11-24", "12-26"],
    2023: ["01-02", "01-16", "02-20", "04-07", "05-29", "06-19", "07-04", "09-04", "11-23", "12-25"],
    2024: ["01-01", "01-15", "02-19", "03-29", "05-27", "06-19", "07-04", "09-02", "11-28", "12-25"],
    2025: ["01-01", "01-09", "01-20", "02-17", "04-18", "05-26", "06-19", "07-04", "09-01", "11-27", "12-25"],
    2026: ["01-01", "01-19", "02-16", "04-03", "05-25", "06-19", "07-03"],
}
#: NYSE 13:00 ET early closes inside the window (none in 2026 to 07-16: 07-03 is the observed holiday)
NYSE_EARLY = {
    2020: ["11-27", "12-24"],
    2021: ["11-26"],
    2022: ["11-25"],
    2023: ["07-03", "11-24"],
    2024: ["07-03", "11-29", "12-24"],
    2025: ["07-03", "11-28", "12-24"],
    2026: [],
}
#: Easter Sunday, 2020-2026
EASTER = ["2020-04-12", "2021-04-04", "2022-04-17", "2023-04-09", "2024-03-31", "2025-04-20", "2026-04-05"]
#: Good Fridays on which BLS's Employment Situation was scheduled at 08:30 ET (the vendored BLS calendars)
GOOD_FRIDAY_JOBS = {"2021-04-02", "2023-04-07", "2026-04-03"}


def _dates(table: dict[int, list[str]]) -> set[str]:
    return {f"{y}-{md}" for y, mds in table.items() for md in mds}


@pytest.fixture(scope="module")
def scheduled():
    return C.scheduled_rows()


# ---------------------------------------------------------------------------------------------------------------------
# The rules
# ---------------------------------------------------------------------------------------------------------------------

def test_easter_sunday_known_dates():
    assert [C.easter_sunday(y).isoformat() for y in range(2020, 2027)] == EASTER
    # a few far years too (the computus is the anonymous Gregorian algorithm)
    assert C.easter_sunday(2000) == date(2000, 4, 23)
    assert C.easter_sunday(2038) == date(2038, 4, 25)
    assert C.easter_sunday(2285) == date(2285, 3, 22)


def test_holidays_are_the_nyse_closures(scheduled):
    got = {r.date for r in scheduled if r.kind == "holiday"}
    assert got == _dates(NYSE_CLOSED)


def test_early_closes_are_the_nyse_early_closes(scheduled):
    got = {r.date for r in scheduled if r.kind == "early_close"}
    assert got == _dates(NYSE_EARLY)
    assert {r.close_ct for r in scheduled if r.kind == "early_close"} == {C.EARLY_CLOSE_CT}
    assert C.EARLY_CLOSE_CT == "12:15"


def test_close_times_by_rule(scheduled):
    by = {r.date: r for r in scheduled}
    # full closures: no session for the date
    for d in ("2020-12-25", "2021-01-01", "2021-12-24", "2022-12-26", "2023-01-02", "2024-03-29", "2025-04-18",
              "2026-01-01", "2020-04-10", "2022-04-15"):
        assert by[d].kind == "holiday" and by[d].close_ct == "", d
    # holidays with Globex's abbreviated equity session, halting at noon CT
    for d in ("2020-01-20", "2020-07-03", "2021-07-05", "2022-06-20", "2023-07-04", "2024-11-28", "2025-09-01",
              "2026-07-03"):
        assert by[d].kind == "holiday" and by[d].close_ct == "12:00", d
    # Good Friday with the jobs report: the abbreviated morning session
    for d in GOOD_FRIDAY_JOBS:
        assert by[d].kind == "holiday" and by[d].close_ct == C.GOOD_FRIDAY_JOBS_CLOSE_CT == "08:15", d
    # the National Day of Mourning
    assert by["2025-01-09"].close_ct == "08:30" and by["2025-01-09"].rule == "S1"


def test_observance_rules():
    # New Year's on a Saturday is not observed (2022), on a Sunday observed Monday (2023)
    assert C.observed_new_year(2022) is None
    assert C.observed_new_year(2023) == date(2023, 1, 2)
    # Saturday -> Friday, Sunday -> Monday for the others
    assert C.observed(date(2021, 12, 25)) == date(2021, 12, 24)
    assert C.observed(date(2022, 12, 25)) == date(2022, 12, 26)
    assert C.observed(date(2020, 7, 4)) == date(2020, 7, 3)
    assert C.observed(date(2021, 7, 4)) == date(2021, 7, 5)
    assert C.observed(date(2022, 6, 19)) == date(2022, 6, 20)
    assert C.observed(date(2024, 6, 19)) == date(2024, 6, 19)
    # Juneteenth only from 2022 (2021-06-18, the first federal observance, was an exchange business day)
    rows = C.scheduled_rows(date(2021, 6, 1), date(2021, 6, 30))
    assert rows == []


def test_good_friday_follows_the_jobs_calendar_given():
    gf = date(2024, 3, 29)
    plain = {r.date: r for r in C.scheduled_rows(date(2024, 3, 1), date(2024, 4, 30), es_dates=set())}
    jobs = {r.date: r for r in C.scheduled_rows(date(2024, 3, 1), date(2024, 4, 30), es_dates={gf})}
    assert plain[gf.isoformat()].close_ct == "" and plain[gf.isoformat()].rule == "H4"
    assert jobs[gf.isoformat()].close_ct == "08:15" and jobs[gf.isoformat()].rule == "H4b"


def test_employment_situation_dates_from_the_vendored_bls_calendars():
    es = C.employment_situation_dates()
    assert date(2021, 4, 2) in es and date(2023, 4, 7) in es and date(2026, 4, 3) in es
    assert date(2024, 3, 29) not in es and date(2025, 4, 18) not in es
    goods = {C.easter_sunday(y) - timedelta(days=2) for y in range(2020, 2027)}
    assert {d.isoformat() for d in goods & es} == GOOD_FRIDAY_JOBS


def test_scheduled_rows_are_weekdays_in_the_window_sorted_and_unique(scheduled):
    ds = [r.date for r in scheduled]
    assert ds == sorted(ds) and len(ds) == len(set(ds))
    for r in scheduled:
        d = date.fromisoformat(r.date)
        assert d.weekday() < 5, r
        assert C.WINDOW_START <= d <= C.WINDOW_END, r
        assert r.rule in C.RULES, r


def test_scheduled_rows_never_reach_the_confirmation_window():
    rows = C.scheduled_rows(date(2026, 7, 1), date(2027, 12, 31))
    assert rows and max(r.date for r in rows) < C.CONFIRMATION_START.isoformat()
    with pytest.raises(ValueError):
        C.scheduled_rows(date(2026, 7, 17), date(2026, 12, 31), clip=False)


# ---------------------------------------------------------------------------------------------------------------------
# The cross-check, on synthetic manifests
# ---------------------------------------------------------------------------------------------------------------------

def _manifest(bounds: dict[str, list[str]], short=None, condition=None, query=None) -> dict:
    """A synthetic store manifest in the bar importer's shape (vendor/stage2/data/README.md section 5)."""
    days = sorted(bounds)
    early = [d for d in days if C.session_minute(bounds[d][1]) < C.session_minute("15:00")]
    late = [d for d in days if C.session_minute(bounds[d][0]) > 0]
    return {
        "root": "NQ", "days": len(days), "first_day": days[0], "last_day": days[-1], "day_list": days,
        "day_bounds": bounds, "early_end_days": early, "late_start_days": late, "short_days": short or {},
        "parquet_sha256": "0" * 64,
        "imports": [{"query": query or {}, "condition": {"not_available": condition or {}}}],
    }


FULL = ["17:00", "15:59"]


def test_cross_check_scheduled_days_the_store_agrees_with():
    m = _manifest({"2024-11-27": FULL, "2024-11-28": ["17:00", "11:59"], "2024-11-29": ["17:00", "12:14"],
                   "2024-12-02": FULL})
    rows = C.build_rows(C.scheduled_rows(date(2024, 11, 1), date(2024, 12, 2)), m)
    by = {r.date: r for r in rows}
    for d, kind in (("2024-11-28", "holiday"), ("2024-11-29", "early_close")):
        assert by[d].kind == kind and "(as scheduled)" in by[d].source and "not as scheduled" not in by[d].source, d
    assert "11:59" in by["2024-11-28"].source and "12:14" in by["2024-11-29"].source
    assert not any(r.kind == "data_defect_candidate" for r in rows)


def test_cross_check_flags_what_the_schedule_does_not_explain():
    # 2024-09-18 ends early with no schedule; 2025-06-30 ends at 18:59 the evening before (a purchase's edge);
    # 2025-07-01 starts late; 2024-10-01 is a short day with full bounds (a gap inside)
    m = _manifest({"2024-09-18": ["17:00", "10:30"], "2024-10-01": FULL, "2025-06-30": ["17:00", "18:59"],
                   "2025-07-01": ["19:00", "15:59"]},
                  short={"2024-10-01": 700, "2025-06-30": 120},
                  condition={"2024-09-18": "degraded"},
                  query={"start": 1577836800000000000, "end": 1751241600000000000})
    rows = C.build_rows([], m)
    by = {r.date: r for r in rows}
    assert set(by) == {"2024-09-18", "2024-10-01", "2025-06-30", "2025-07-01"}
    for r in rows:
        assert r.kind == "data_defect_candidate" and r.close_ct == "" and r.source.startswith("store: ")
    assert "degraded" in by["2024-09-18"].source and "10:30" in by["2024-09-18"].source
    assert "early_end_days" in by["2024-09-18"].source
    assert "short day 700 bars" in by["2024-10-01"].source
    assert "purchase edge" in by["2025-06-30"].source and "early_end_days" in by["2025-06-30"].source
    # 07-01's own start edge belongs to an import this manifest does not hold: no reason given
    assert "late_start_days" in by["2025-07-01"].source and "no reason given" in by["2025-07-01"].source
    m2 = _manifest({"2025-07-01": ["19:00", "15:59"]}, query={"start": 1751328000000000000})
    (r,) = C.build_rows([], m2)
    assert r.date == "2025-07-01" and "late_start_days" in r.source and "purchase edge" in r.source
    (r,) = C.build_rows([], _manifest({"2023-03-01": ["17:00", "09:00"]}))
    assert "no reason given" in r.source


def test_cross_check_lists_scheduled_closes_the_store_does_not_show():
    m = _manifest({"2023-07-03": FULL, "2023-07-05": FULL, "2023-07-04": ["17:00", "11:00"],
                   "2023-12-25": ["17:00", "12:14"]})
    rows = C.build_rows(C.scheduled_rows(date(2023, 7, 1), date(2023, 12, 31)), m)
    by = {r.date: r for r in rows}
    assert "not as scheduled" in by["2023-07-03"].source and "15:59" in by["2023-07-03"].source
    assert "not as scheduled" in by["2023-07-04"].source and "11:00" in by["2023-07-04"].source
    assert "not as scheduled" in by["2023-12-25"].source and "day held" in by["2023-12-25"].source
    assert "no day" in by["2023-11-23"].source and "not shown" in by["2023-11-23"].source
    assert by["2023-11-23"].kind == "holiday"


def test_degraded_days_the_store_holds_whole_are_reported_not_listed():
    m = _manifest({"2021-12-06": FULL, "2024-11-29": ["17:00", "12:14"], "2024-12-02": FULL, "2026-07-20": FULL},
                  condition={"2021-12-05": "degraded", "2024-11-29": "degraded", "2026-07-20": "degraded"})
    rows = C.build_rows(C.scheduled_rows(date(2021, 12, 1), date(2024, 12, 31)), m)
    assert not any(r.kind == "data_defect_candidate" for r in rows)
    got = C.degraded_days_not_listed(m, rows)
    assert got == [("2021-12-06", "Databento condition degraded on UTC 2021-12-05")]
    assert "degraded" in {r.date: r for r in rows}["2024-11-29"].source


def test_cross_check_never_reads_past_the_window():
    m = _manifest({"2026-07-16": ["17:00", "10:00"], "2026-07-20": ["17:00", "10:00"], "2026-08-03": ["21:00", "15:59"]},
                  short={"2026-07-20": 5}, condition={"2026-07-20": "degraded"},
                  query={"start": 1751328000000000000, "end": 1791849600000000000})
    rows = C.build_rows([], m)
    assert [r.date for r in rows] == ["2026-07-16"]
    assert "2026-07-2" not in rows[0].source and "2026-08" not in rows[0].source


# ---------------------------------------------------------------------------------------------------------------------
# The file
# ---------------------------------------------------------------------------------------------------------------------

def _file_rows() -> list[dict[str, str]]:
    return C.read_calendar(C.CALENDAR_CSV)


def test_the_file_parses_with_its_four_columns():
    text = C.CALENDAR_CSV.read_text(encoding="utf-8")
    body = [ln for ln in text.splitlines() if ln and not ln.startswith("#")]
    assert body[0] == ",".join(C.COLUMNS)
    rows = list(csv.DictReader(body))
    assert rows and all(set(r) == set(C.COLUMNS) and None not in r.values() for r in rows)
    assert rows == _file_rows()
    # the header carries every rule the rows cite
    for rule_id in C.RULES:
        assert f"# {rule_id} " in text, rule_id
    for r in rows:
        assert "#" not in "".join(r.values()), r


def test_the_file_is_sorted_and_inside_the_development_window():
    rows = _file_rows()
    ds = [r["date"] for r in rows]
    assert ds == sorted(ds) and len(ds) == len(set(ds))
    for r in rows:
        d = date.fromisoformat(r["date"])
        assert date(2020, 1, 2) <= d <= date(2026, 7, 16), r
        assert d < date(2026, 7, 17), r
        assert r["kind"] in C.KINDS, r
        assert r["close_ct"] == "" or (len(r["close_ct"]) == 5 and r["close_ct"][2] == ":"), r
        if r["kind"] == "early_close":
            assert r["close_ct"], r
        if r["kind"] == "data_defect_candidate":
            assert r["close_ct"] == "" and r["source"].startswith("store"), r


def test_the_files_scheduled_rows_are_the_rules():
    want = [(r.date, r.kind, r.close_ct, r.rule) for r in C.scheduled_rows()]
    got = [(r["date"], r["kind"], r["close_ct"], r["source"].split(" ", 1)[0])
           for r in _file_rows() if r["kind"] != "data_defect_candidate"]
    assert got == want


@pytest.mark.skipif(not C.MANIFEST.exists(), reason="the bar store's manifest is not linked in this tree")
def test_the_file_rebuilds_byte_for_byte_from_the_rules_and_the_manifest():
    built = C.render(C.build_rows(C.scheduled_rows(), C.load_manifest()), C.load_manifest())
    on_disk = C.CALENDAR_CSV.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")
    assert built == on_disk
