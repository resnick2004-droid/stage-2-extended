"""IM2's release calendar (P-04 §3; the fill audit of 2026-09-27, finding 1).

Topstep names the scheduled releases that move each product and warns that "Slippage is common during these events"
(help.topstep.com 8284211, read 2026-09-27). For IM2's four markets it names three: the FOMC statement, 1:00 PM CT,
"All products"; Crude Oil Inventories (EIA), "9:30 AM / 10:00 AM*" CT, CL (and MCL); Natural Gas Inventories (EIA),
9:30 AM CT, NG. (Its Unemployment Rate at 7:30 AM CT falls before any IM2 decision: the first is 08:00 CT on 6E.) This
module turns those into dated release minutes, from the sources in `config/sources/` and declared rules where no
dated source was found, and writes `config/im2_release_calendar.csv` (`scripts/build_im2_release_calendar.py`).

Sources and rules, fixed before any IM2 bar is read:

* **FOMC statements** (all four markets): the statement dates linked from the Federal Reserve's calendar pages
  (`config/sources/fomc_statements.csv`). The time: the statement page's own line where it prints one ("For release at
  2:00 p.m. EDT", 2016 on); else from 2013-03-20 on 2:00 p.m. ET (Fed notice 2013-03-13: "will now be released at 2
  p.m. Eastern Time"); else, for the 2011 press-conference meetings, 12:30 p.m. ET (Fed notice 2011-03-24: "expected to
  be released at around 12:30 p.m., one hour and forty-five minutes earlier than for other FOMC meetings"); for the
  2012 press-conference meetings, whose time no page read states, both 12:30 and 2:15 p.m. ET; otherwise 2:15 p.m. ET
  (the same notice's "other FOMC meetings").
* **EIA crude** (CL): the Weekly Petroleum Status Report's release dates from EIA's archive
  (`config/sources/eia_wpsr_release_dates.txt`, 2011-08-03 on): a Wednesday at 10:30 a.m. ET (9:30 CT); any other day,
  both of Topstep's times, 10:30 and 11:00 a.m. ET. Before the archive starts, a rule: each Wednesday at 10:30 ET; in a
  week whose Monday, Tuesday or Wednesday is a federal holiday, also Thursday at 10:30 and 11:00 ET, and Friday too if
  the Thursday is a holiday (the archive shows the report moving to Thursday in such weeks).
* **EIA natural gas** (NG): every Thursday at 10:30 a.m. ET (EIA's standard, https://ir.eia.gov/ngs/schedule.html);
  the alternates EIA lists for 2025 and 2026 at their stated times (`config/sources/eia_wngsr_holiday_schedule.csv`),
  the Thursday they replace kept as well; before 2025, where no schedule was found (EIA's archive page answers 403 and
  is not worked around), a rule: in any week with a federal holiday on a weekday, also Wednesday, Thursday and Friday at
  12:00 p.m. ET, Wednesday and Friday at 10:30, and the next Monday at 10:30 and 12:00 (every alternate day and time
  EIA's 2025-2026 schedule uses). Both rules over-flag: a flagged minute without a release costs the model a worse
  fill, never a better one.

Federal holidays are pandas' `USFederalHolidayCalendar` (observed dates, Juneteenth from 2021). CT is ET less one hour
all year (the two zones change clocks together).
"""
from __future__ import annotations

import csv
import re
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from propedge import CONFIG_DIR

SOURCES = CONFIG_DIR / "sources"
CALENDAR = CONFIG_DIR / "im2_release_calendar.csv"
COLUMNS = ["date", "time_et", "time_ct", "code", "release", "markets", "source", "method"]
#: The periods P-04 reads (development with its warm-up, confirmation with its warm-up); nothing else is listed.
WINDOWS = ((date(2009, 5, 1), date(2019, 12, 31)), (date(2024, 4, 1), date(2026, 8, 31)))
MARKETS = {"FOMC": "ES,CL,6E,NG", "EIAC": "CL", "EIAG": "NG"}
NAMES = {"FOMC": "FOMC statement", "EIAC": "Crude Oil Inventories (EIA Weekly Petroleum Status Report)",
         "EIAG": "Natural Gas Inventories (EIA Weekly Natural Gas Storage Report)"}
PC_2011 = {date(2011, 4, 27), date(2011, 6, 22), date(2011, 11, 2)}
WPSR_ARCHIVE_START = date(2011, 8, 3)
WNGSR_SCHEDULE_YEARS = (2025, 2026)
N2011 = ("Fed notice 2011-03-24 (federalreserve.gov/newsevents/pressreleases/monetary20110324a.htm), read 2026-09-27")
N2013 = ("Fed notice 2013-03-13 (federalreserve.gov/newsevents/pressreleases/monetary20130313a.htm), read 2026-09-27")
TOPSTEP = "Topstep 8284211 (9:30 AM / 10:00 AM* CT), read 2026-09-27"


def _csv_rows(path: Path) -> list[dict]:
    lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l and not l.startswith("#")]
    return list(csv.DictReader(lines))


def in_windows(d: date) -> bool:
    return any(a <= d <= b for a, b in WINDOWS)


def federal_holidays() -> set[date]:
    from pandas.tseries.holiday import USFederalHolidayCalendar

    return {x.date() for x in USFederalHolidayCalendar().holidays("2009-01-01", "2027-01-31")}


def _et(text: str) -> str:
    """'2:00 p.m.' / '10:30 a.m.' -> 'HH:MM' (24 h)."""
    m = re.search(r"(\d{1,2}):(\d\d)\s*([ap])\.m\.", text)
    if not m:
        raise ValueError(f"no time in {text!r}")
    h = int(m.group(1)) % 12 + (12 if m.group(3) == "p" else 0)
    return f"{h:02d}:{m.group(2)}"


def _ct(et: str) -> str:
    h, m = (int(x) for x in et.split(":"))
    return f"{h - 1:02d}:{m:02d}"


def _row(d: date, et: str, code: str, source: str, method: str) -> dict:
    return {"date": d.isoformat(), "time_et": et, "time_ct": _ct(et), "code": code, "release": NAMES[code],
            "markets": MARKETS[code], "source": source, "method": method}


def fomc_rows(src: Path = SOURCES) -> list[dict]:
    out = []
    for r in _csv_rows(src / "fomc_statements.csv"):
        d = date.fromisoformat(r["date"])
        base = f"statement {r['statement_url']}"
        if r["release_line"]:
            out.append(_row(d, _et(r["release_line"]), "FOMC", f"{base}: '{r['release_line']}'", "statement_page"))
        elif d >= date(2013, 3, 20):
            out.append(_row(d, "14:00", "FOMC", f"{base}; time: {N2013}", "fed_notice"))
        elif d in PC_2011:
            out.append(_row(d, "12:30", "FOMC", f"{base}; time: {N2011}", "fed_notice"))
        elif r["press_conference"] == "1" and d.year == 2012:
            for et in ("12:30", "14:15"):
                out.append(_row(d, et, "FOMC", f"{base}; press-conference meeting, time stated on no page read: "
                                               "both 12:30 and 2:15 p.m. ET flagged", "rule_both"))
        else:
            out.append(_row(d, "14:15", "FOMC", f"{base}; time: {N2011} ('other FOMC meetings', 2:15 p.m. ET)",
                            "fed_notice"))
    return out


def _weeks(a: date, b: date):
    """Mondays of every week that overlaps [a, b]."""
    m = a - timedelta(days=a.weekday())
    while m <= b:
        yield m
        m += timedelta(days=7)


def wpsr_rows(src: Path = SOURCES, hol: set[date] | None = None) -> list[dict]:
    hol = federal_holidays() if hol is None else hol
    out = []
    listed = [date.fromisoformat(l.strip()) for l in (src / "eia_wpsr_release_dates.txt").read_text(
        encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
    arch = "EIA WPSR archive date (config/sources/eia_wpsr_release_dates.txt)"
    for d in listed:
        if d.weekday() == 2:
            out.append(_row(d, "10:30", "EIAC", f"{arch}; Wednesday 10:30 ET, {TOPSTEP}", "eia_archive"))
        else:
            for et in ("10:30", "11:00"):
                out.append(_row(d, et, "EIAC", f"{arch}; not a Wednesday: both of {TOPSTEP}", "eia_archive_both"))
    for a, b in WINDOWS:
        for mon in _weeks(a, min(b, WPSR_ARCHIVE_START - timedelta(days=1))):
            wed, thu, fri = (mon + timedelta(days=k) for k in (2, 3, 4))
            early = any(mon + timedelta(days=k) in hol for k in range(3))
            rule = "rule: before the archive (2011-08-03), Wednesday 10:30 ET"
            if wed not in hol:
                out.append(_row(wed, "10:30", "EIAC", rule, "rule"))
            if early:
                days = [thu] + ([fri] if thu in hol else [])
                for x in days:
                    for et in ("10:30", "11:00"):
                        out.append(_row(x, et, "EIAC", "rule: a federal holiday Monday-Wednesday moves the report; "
                                                       f"both of {TOPSTEP}", "rule_holiday_week"))
    return out


def wngsr_rows(src: Path = SOURCES, hol: set[date] | None = None) -> list[dict]:
    hol = federal_holidays() if hol is None else hol
    out = []
    sched = "EIA WNGSR schedule https://ir.eia.gov/ngs/schedule.html, read 2026-09-27"
    for r in _csv_rows(src / "eia_wngsr_holiday_schedule.csv"):
        d = date.fromisoformat(r["alternate_date"])
        out.append(_row(d, _et(r["release_time_et"]), "EIAG", f"{sched}: alternate for {r['holiday']}",
                        "eia_schedule"))
    for a, b in WINDOWS:
        for mon in _weeks(a, b):
            thu = mon + timedelta(days=3)
            covered = thu.year in WNGSR_SCHEDULE_YEARS
            out.append(_row(thu, "10:30", "EIAG", f"{sched}: standard Thursday 10:30 ET",
                            "eia_schedule" if covered else "rule_standard"))
            if covered or not any(mon + timedelta(days=k) in hol for k in range(5)):
                continue
            extra = [(2, "10:30"), (2, "12:00"), (3, "12:00"), (4, "10:30"), (4, "12:00"), (7, "10:30"), (7, "12:00")]
            for k, et in extra:
                out.append(_row(mon + timedelta(days=k), et, "EIAG",
                                "rule: a week with a federal holiday before 2025, every alternate day and time of "
                                "EIA's 2025-2026 schedule flagged", "rule_holiday_week"))
    return out


def build(src: Path = SOURCES) -> pd.DataFrame:
    """The calendar: every row inside `WINDOWS`, one per (date, time, release), sorted."""
    hol = federal_holidays()
    rows = fomc_rows(src) + wpsr_rows(src, hol) + wngsr_rows(src, hol)
    df = pd.DataFrame(rows, columns=COLUMNS)
    df = df[df["date"].map(lambda s: in_windows(date.fromisoformat(s)))]
    df = df[pd.to_datetime(df["date"]).dt.weekday < 5]
    df = df.drop_duplicates(["date", "time_ct", "code"]).sort_values(["date", "time_ct", "code"], kind="stable")
    return df.reset_index(drop=True)


def load(path: Path = CALENDAR) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str)


def releases(market: str, start: date, end: date, path: Path = CALENDAR) -> dict[str, list[int]]:
    """{YYYYMMDD: sorted release minutes after midnight CT} for `market` between `start` and `end` inclusive."""
    df = load(path)
    out: dict[str, set[int]] = {}
    for _, r in df.iterrows():
        d = date.fromisoformat(r["date"])
        if start <= d <= end and market in r["markets"].split(","):
            h, m = (int(x) for x in r["time_ct"].split(":"))
            out.setdefault(d.strftime("%Y%m%d"), set()).add(60 * h + m)
    return {k: sorted(v) for k, v in sorted(out.items())}


def hot_slots(minutes: list[int], open_min: int, n_slots: int, hot_minutes: int) -> set[int]:
    """The session's slots (bar STARTS open_min + slot) inside a release's hot window: the release minute and the
    `hot_minutes - 1` after it."""
    return {m - open_min + k for m in minutes for k in range(hot_minutes) if 0 <= m - open_min + k < n_slots}


__all__ = ["CALENDAR", "COLUMNS", "WINDOWS", "build", "load", "releases", "hot_slots", "fomc_rows", "wpsr_rows",
           "wngsr_rows", "federal_holidays"]
