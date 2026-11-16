# `config/calendar_early_closes.csv` -- how it was built (Q-40, E-022 (3))

**What it is.** One row per trading day, 2020-01-02 to 2026-07-16 (NQ's development window; nothing from 2026-07-17),
on which CME Globex equity-index futures had a scheduled early close or a holiday, plus, apart, the days the bar store's
own record shows as incomplete with no schedule to explain them. Families void such days **from this file, fixed in
advance, never from the day's own bars** (DRAFT F-02 section 4.5 (a) and (b); the red team's F6). Columns: `date`,
`kind` (`holiday` / `early_close` / `data_defect_candidate`), `close_ct` (Chicago time trading stops; blank when the
date has no session or no scheduled close), `source`. The file's own header has the rules and the meaning of every
kind. The lead pins it by its LF sha256 under a decision row. After that it is never edited; a change is a new file
under a new row.

**Read it** with `extended.calendar_early_closes.read_calendar(path)` (a list of dicts of strings), or
`pandas.read_csv(path, comment="#", dtype=str, keep_default_na=False)`. Dates are the bar store's trading days: a
session opens at 17:00 CT the evening before. A holiday's abbreviated Globex session (for example Thanksgiving, 17:00 CT
Wednesday to 12:00 CT Thursday) is dated to the holiday. CME books it to the next business day's trade date, but the
store dates it to the holiday, and so does this file.

## 1. The exchange's own pages were not read, and why

The brief said to read CME Group's terms of use first. On 2026-11-16 the first scripted request to cmegroup.com (its
terms-of-use page) got HTTP 403, and so did a request for `robots.txt`. Both returned this body:

> "This IP address is blocked due to suspected web scraping activity associated with it on this CMEgroup.com page. Use
> of scripts, software, spiders, robots, avatars, agents, tools or other scraping mechanisms is strictly prohibited by
> CME Group’s website Data Terms of Use. If you are attempting to access data or content from the website via
> automated means or for commercial purposes, CME has numerous other methods to deliver the content you require. [...]"

That is the site's own statement that its terms forbid automated retrieval. No calendar page was requested and no way
around the block was tried: no other client string, no archived copy, no mirror, no form or login. As the brief
directs, the schedule is built from the **standard U.S. exchange holiday rules** as CME applies them to its
equity-index futures. Each rule is written into the file's header:

| id | day | NQ on Globex |
|---|---|---|
| H1 | New Year's Day (Sunday -> Monday; a Saturday is not observed) | closed |
| H2, H3, H5, H8, H9 | MLK, Presidents', Memorial, Labor, Thanksgiving | abbreviated session, halt 12:00 CT |
| H4 | Good Friday (Easter less two days) | closed |
| H4b | Good Friday with BLS's Employment Situation at 08:30 ET | abbreviated morning session, close 08:15 CT |
| H6 | Juneteenth, from 2022 (observed) | abbreviated session, halt 12:00 CT |
| H7 | Independence Day (observed) | abbreviated session, halt 12:00 CT |
| H10 | Christmas Day (observed) | closed |
| E1, E2, E3 | the day after Thanksgiving; 24 December and 3 July when Monday to Thursday | early close 12:15 CT (NYSE 13:00 ET) |
| S1 | 2025-01-09, the National Day of Mourning for President Carter (announced in advance) | halt 08:30 CT |

Two inputs are calendars published in advance, not rules. One is the BLS Employment Situation dates, from the vendored
`vendor/stage2/data/releases_bls_0830_*.csv` (for H4b). The other is S1's announced closure. Observance follows NYSE
Rule 7.2. The rules are tested against the NYSE's 2020-2026 holiday and early-close lists, typed into
`tests/test_calendar_early_closes.py` independently of the code. Those lists are typed from the NYSE's published
schedules as known; the NYSE's pages were not read in this session either.

**Not verified on the exchange's pages:** the Globex close times (12:00, 12:15, 08:15, 08:30 CT) and which holidays are
full closures and which are abbreviated sessions. These come from CME's standard equity-index schedule as publicly
known. The store's record is the check on them (section 2).

## 2. The cross-check against the bar store's record

`scripts/build_calendar_early_closes.py` reads one file, the store's manifest `vendor/stage2/data/bars/NQ/manifest.json`.
That is metadata only: `bars.parquet` is never opened. Only the manifest's entries for window days are looked at. The
fields used are `day_list`, `day_bounds` (each day's first and last bar, Chicago), `early_end_days` (last bar before
15:00 CT), `late_start_days` (first bar after 17:00 CT), `short_days` (fewer than 1,000 bars), each import's query
start and end (a purchase's edge), and Databento's per-UTC-date `condition`. The file's header names the store's
`parquet_sha256`.

- **A scheduled row** is annotated in `source` with what the store shows. "(as scheduled)" means the store's last bar
  is the minute before `close_ct`, or, for a closed date, that the store holds no day. "not as scheduled" or "not shown
  by the store" means it does not match, and the row says how.
- **A `data_defect_candidate`** is a window day the store lists as ending early, starting late or short that no
  scheduled row covers. Its `source` gives the store's bounds and bar count, and the manifest's reason where it gives
  one: a purchase's edge, or a Databento `degraded` date. Otherwise it says "no reason given in the manifest". These are
  candidates: which of them become data-defect days a family voids is the lead's decision under a row.
- **Not in the file:** days whose session touches a Databento `degraded` UTC date but which the store holds whole (no
  early end, no late start, not short). The script prints them beside the file, for the lead.

## 3. Rebuild and check

    python scripts/build_calendar_early_closes.py --check    # rebuilds in memory and compares; writes nothing

The build is deterministic. It draws no randomness and reads no bar, and it refuses to replace a file that differs
unless given `--force`, which is allowed only before the pin. `tests/test_calendar_early_closes.py` checks that the
file parses, is sorted with one row per date, holds no date outside 2020-01-02..2026-07-16 and none from 2026-07-17,
and that its scheduled rows are exactly the rules' rows. Where the store's manifest is linked, it also checks that a
rebuild reproduces the file byte for byte.

## 4. Limits

- A gap inside a day with normal bounds and at least 1,000 bars is invisible to the manifest's lists, so it is not here.
- NQ only (CME equity-index futures). Another market needs its own calendar.
- The calendar is the exchange schedule. Firm trading-hour rules (for example a firm closing accounts before an early
  close) are separate, and come only from the verified ledger.
