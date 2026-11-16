# FOMC minutes release dates, 2020-01-02 to 2026-07-16 (TASK_QUEUE Q-73, 2026-11-16)

**Status: read-only research note (wt-scout pattern, worktree wt-firms).** It reads only the Federal Reserve's own
pages on federalreserve.gov. It reads no bar, no result and no outcome. It computes no statistic of any design. The
table is the input the other-firms reading owes before its run (`prereg/DRAFT_RD_firms.md:501-503` and `:905-907`).
It is not pinned here: pinning a `config/` calendar is a builder's item under a decision row, as E-029 pinned
`config/calendar_early_closes.csv`.

## The question

TradeDay's tier-1 list names "FOMC minutes - All products" / "1:00 PM CT" (`config/rules_extended.yaml:2773-2785`,
`tradeday.tier1_release_list`, verified 2026-11-16). Under `tradeday.tier1_news_auto_liquidation` that gives a
12:58 to 13:02 CT window on every FOMC minutes day. Section 5.5 of the firms reading counts the trades open in that
window and brackets them. To do that it needs **every FOMC minutes release date from 2020-01-02 to 2026-07-16**, taken
from the Federal Reserve's own FOMC calendar pages, with the release time in ET where the pages state it.

## The answer

- **53 minutes release dates fall in the range.** By calendar year: 2020: 8, 2021: 8, 2022: 8, 2023: 8, 2024: 8,
  2025: 9, 2026 (to 2026-07-16): 4.
- **Every date is stated on the Federal Reserve's calendar pages.** For 2021 on that is `fomccalendars.htm`; for 2020
  it is `fomchistorical2020.htm`. The first release in the range, 2020-01-03, is the minutes of the December 10-11,
  2019 meeting, so it is on `fomchistorical2019.htm`.
- **Every date was confirmed on the minutes' own press release** on federalreserve.gov. Each press release prints the
  same date and links the same meeting's minutes file. No date is missing, none conflicts, and none was inferred.
- **The calendar pages state no release time.** Every one of the 53 press releases prints "For release at 2:00 p.m.
  EST" or "For release at 2:00 p.m. EDT". Each EST/EDT label matches the U.S. daylight-saving rule for its date. So
  every release is at **14:00 ET, which is 13:00 CT**. That agrees with TradeDay's "1:00 PM CT", so the window is
  12:58 to 13:02 CT on all 53 days.
- **Seven calendar entries in the range have no minutes date of their own** (section 4):
  - The **March 2, 2020** unscheduled meeting. The 2020 page says "Minutes: See end of minutes of March 15 meeting",
    and those minutes were released 2020-04-08 (row 3).
  - The cancelled March 17-18, 2020 meeting and five **notation votes** (2020-03-19, 2020-03-23, 2020-03-31,
    2020-08-27, 2025-08-22). The calendar gives them no minutes entry at all.
- **Stage 2's vendored FOMC files hold policy-statement dates only.** None of them holds a minutes date (section 6).

## 1. What was read

Everything was fetched on **2026-11-16 at about 13:50 UTC**, by a plain HTTPS GET with a generic client string. No
form, login or personal detail was sent. `robots.txt` on the site answers HTTP 404, and Stage 2 read the same calendar
pages (`vendor/stage2/config/sources/fomc_statements_2020_2024q1.csv:1-8`). The downloaded copies live in the
session's scratch space and are not committed. Their hashes are given so that a re-read can be compared.

| page | URL | HTTP | bytes | sha256 | "Last Update" printed on the page | what it carries here |
|---|---|---|---|---|---|---|
| FOMC calendars | https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm | 200 | 166,065 | `183292de88ae13007b36cd6b4857f7fbc9aabd36b15c8906182859fee1791756` | November 12, 2026 | meetings 2021-2027; minutes dates for rows 10-53 |
| 2020 historical | https://www.federalreserve.gov/monetarypolicy/fomchistorical2020.htm | 200 | 98,731 | `7307f6da9e6be559a302eab8b683c0b864e8956d42ed451250e27bb524ec2125` | January 16, 2026 | rows 2-9; March 2 unscheduled; notation votes |
| 2019 historical | https://www.federalreserve.gov/monetarypolicy/fomchistorical2019.htm | 200 | 97,520 | `919b14cadf5d1b10b1bfdc6d223782bc75db3082048d7e2a151d63cc5688b2f3` | July 18, 2025 | row 1 (the December 2019 meeting's minutes, released 2020-01-03) |
| 2021 historical | https://www.federalreserve.gov/monetarypolicy/fomchistorical2021.htm | **404** ("Federal Reserve Board - Page not Found") | 82,310 | -- | -- | nothing; 2021 is on `fomccalendars.htm` |
| 2022 historical | .../fomchistorical2022.htm | **404** | 82,310 | -- | -- | nothing; 2022 is on `fomccalendars.htm` |
| 2023 historical | .../fomchistorical2023.htm | **404** | 82,310 | -- | -- | nothing; 2023 is on `fomccalendars.htm` |
| 53 minutes press releases | https://www.federalreserve.gov/newsevents/pressreleases/monetaryYYYYMMDDa.htm (YYYYMMDD = the release date) | 200 each | Appendix A | Appendix A | -- | the time line; a second reading of each date |

The 2021-2023 historical pages answered 404 to Stage 2 on 2026-10-03 as well
(`vendor/stage2/config/sources/fomc_statements_2020_2024q1.csv:3`). The brief named "the historical-year pages for
2020 onward"; **2019's page was read in addition**, because the December 2019 meeting's minutes fall inside the range.

**How a date appears on the pages (verbatim).**

- On `fomccalendars.htm`, each meeting row has a minutes cell reading, for example, "Minutes: PDF | HTML (Released
  February 18, 2026)", linking `/monetarypolicy/fomcminutes20260128.htm`.
- On the historical pages, each meeting panel reads, for example, "Minutes (Released February 19, 2020):", linking
  `/monetarypolicy/fomcminutes20200129.htm`.
- The minutes file is named for the meeting's policy-decision day, the last day of the meeting. That date is the
  `meeting_end` column below.

**What the calendar says about timing (verbatim, `fomccalendars.htm`).** "The FOMC holds eight regularly scheduled
meetings during the year and other meetings as needed. Links to policy statements and minutes are in the calendars
below. The minutes of regularly scheduled meetings are released three weeks after the date of the policy decision."
The page states no clock time for the minutes.

**How a press release states the time (verbatim, `monetary20200219a.htm`).** "February 19, 2020" / "Minutes of the
Federal Open Market Committee, January 28-29, 2020" / "For release at 2:00 p.m. EST".

**Checks run on the pages' text** (a script in the session's scratch space; no bar or outcome read):

- For each of the 53 rows, the press release's printed date equals the calendar page's "Released" date.
- Each press release links exactly one minutes file, and it is the file of the row's meeting.
- Each press release's time line is exactly "For release at 2:00 p.m. EST" or "For release at 2:00 p.m. EDT".
- Each EST/EDT label agrees with the U.S. rule: EDT from the second Sunday of March to the first Sunday of November.
- All 53 rows passed. The press release for each date was the `a` release of that day; no other suffix was needed.

## 2. The table

`meeting_end` is the meeting's policy-decision day. "Days after the decision" is the release date minus
`meeting_end`, both read from the pages. An asterisk in a label is the page's own: "* Meeting associated with a
Summary of Economic Projections." For every row, ET = 14:00 and CT = 13:00, so TradeDay's window is 12:58 to
13:02 CT.

| # | meeting (the page's label) | meeting_end | minutes released | days after the decision | time line on the minutes' press release (verbatim) | date read from | time read from | accessed |
|---|---|---|---|---|---|---|---|---|
| 1 | December 10-11, 2019 | 2019-12-11 | **2020-01-03** (Fri) | 23 | "For release at 2:00 p.m. EST" | [`fomchistorical2019.htm`](https://www.federalreserve.gov/monetarypolicy/fomchistorical2019.htm) | [`monetary20200103a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20200103a.htm) | 2026-11-16 |
| 2 | January 28-29, 2020 | 2020-01-29 | **2020-02-19** (Wed) | 21 | "For release at 2:00 p.m. EST" | [`fomchistorical2020.htm`](https://www.federalreserve.gov/monetarypolicy/fomchistorical2020.htm) | [`monetary20200219a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20200219a.htm) | 2026-11-16 |
| 3 | March 15 (unscheduled), 2020 | 2020-03-15 | **2020-04-08** (Wed) | 24 | "For release at 2:00 p.m. EDT" | [`fomchistorical2020.htm`](https://www.federalreserve.gov/monetarypolicy/fomchistorical2020.htm) | [`monetary20200408a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20200408a.htm) | 2026-11-16 |
| 4 | April 28-29, 2020 | 2020-04-29 | **2020-05-20** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomchistorical2020.htm`](https://www.federalreserve.gov/monetarypolicy/fomchistorical2020.htm) | [`monetary20200520a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20200520a.htm) | 2026-11-16 |
| 5 | June 9-10, 2020 | 2020-06-10 | **2020-07-01** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomchistorical2020.htm`](https://www.federalreserve.gov/monetarypolicy/fomchistorical2020.htm) | [`monetary20200701a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20200701a.htm) | 2026-11-16 |
| 6 | July 28-29, 2020 | 2020-07-29 | **2020-08-19** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomchistorical2020.htm`](https://www.federalreserve.gov/monetarypolicy/fomchistorical2020.htm) | [`monetary20200819a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20200819a.htm) | 2026-11-16 |
| 7 | September 15-16, 2020 | 2020-09-16 | **2020-10-07** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomchistorical2020.htm`](https://www.federalreserve.gov/monetarypolicy/fomchistorical2020.htm) | [`monetary20201007a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20201007a.htm) | 2026-11-16 |
| 8 | November 4-5, 2020 | 2020-11-05 | **2020-11-25** (Wed) | 20 | "For release at 2:00 p.m. EST" | [`fomchistorical2020.htm`](https://www.federalreserve.gov/monetarypolicy/fomchistorical2020.htm) | [`monetary20201125a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20201125a.htm) | 2026-11-16 |
| 9 | December 15-16, 2020 | 2020-12-16 | **2021-01-06** (Wed) | 21 | "For release at 2:00 p.m. EST" | [`fomchistorical2020.htm`](https://www.federalreserve.gov/monetarypolicy/fomchistorical2020.htm) | [`monetary20210106a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20210106a.htm) | 2026-11-16 |
| 10 | January 26-27, 2021 | 2021-01-27 | **2021-02-17** (Wed) | 21 | "For release at 2:00 p.m. EST" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20210217a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20210217a.htm) | 2026-11-16 |
| 11 | March 16-17*, 2021 | 2021-03-17 | **2021-04-07** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20210407a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20210407a.htm) | 2026-11-16 |
| 12 | April 27-28, 2021 | 2021-04-28 | **2021-05-19** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20210519a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20210519a.htm) | 2026-11-16 |
| 13 | June 15-16*, 2021 | 2021-06-16 | **2021-07-07** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20210707a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20210707a.htm) | 2026-11-16 |
| 14 | July 27-28, 2021 | 2021-07-28 | **2021-08-18** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20210818a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20210818a.htm) | 2026-11-16 |
| 15 | September 21-22*, 2021 | 2021-09-22 | **2021-10-13** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20211013a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20211013a.htm) | 2026-11-16 |
| 16 | November 2-3, 2021 | 2021-11-03 | **2021-11-24** (Wed) | 21 | "For release at 2:00 p.m. EST" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20211124a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20211124a.htm) | 2026-11-16 |
| 17 | December 14-15*, 2021 | 2021-12-15 | **2022-01-05** (Wed) | 21 | "For release at 2:00 p.m. EST" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20220105a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20220105a.htm) | 2026-11-16 |
| 18 | January 25-26, 2022 | 2022-01-26 | **2022-02-16** (Wed) | 21 | "For release at 2:00 p.m. EST" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20220216a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20220216a.htm) | 2026-11-16 |
| 19 | March 15-16*, 2022 | 2022-03-16 | **2022-04-06** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20220406a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20220406a.htm) | 2026-11-16 |
| 20 | May 3-4, 2022 | 2022-05-04 | **2022-05-25** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20220525a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20220525a.htm) | 2026-11-16 |
| 21 | June 14-15*, 2022 | 2022-06-15 | **2022-07-06** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20220706a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20220706a.htm) | 2026-11-16 |
| 22 | July 26-27, 2022 | 2022-07-27 | **2022-08-17** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20220817a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20220817a.htm) | 2026-11-16 |
| 23 | September 20-21*, 2022 | 2022-09-21 | **2022-10-12** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20221012a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20221012a.htm) | 2026-11-16 |
| 24 | November 1-2, 2022 | 2022-11-02 | **2022-11-23** (Wed) | 21 | "For release at 2:00 p.m. EST" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20221123a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20221123a.htm) | 2026-11-16 |
| 25 | December 13-14*, 2022 | 2022-12-14 | **2023-01-04** (Wed) | 21 | "For release at 2:00 p.m. EST" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20230104a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20230104a.htm) | 2026-11-16 |
| 26 | Jan/Feb 31-1, 2023 | 2023-02-01 | **2023-02-22** (Wed) | 21 | "For release at 2:00 p.m. EST" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20230222a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20230222a.htm) | 2026-11-16 |
| 27 | March 21-22*, 2023 | 2023-03-22 | **2023-04-12** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20230412a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20230412a.htm) | 2026-11-16 |
| 28 | May 2-3, 2023 | 2023-05-03 | **2023-05-24** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20230524a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20230524a.htm) | 2026-11-16 |
| 29 | June 13-14*, 2023 | 2023-06-14 | **2023-07-05** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20230705a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20230705a.htm) | 2026-11-16 |
| 30 | July 25-26, 2023 | 2023-07-26 | **2023-08-16** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20230816a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20230816a.htm) | 2026-11-16 |
| 31 | September 19-20*, 2023 | 2023-09-20 | **2023-10-11** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20231011a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20231011a.htm) | 2026-11-16 |
| 32 | Oct/Nov 31-1, 2023 | 2023-11-01 | **2023-11-21** (Tue) | 20 | "For release at 2:00 p.m. EST" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20231121a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20231121a.htm) | 2026-11-16 |
| 33 | December 12-13*, 2023 | 2023-12-13 | **2024-01-03** (Wed) | 21 | "For release at 2:00 p.m. EST" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20240103a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20240103a.htm) | 2026-11-16 |
| 34 | January 30-31, 2024 | 2024-01-31 | **2024-02-21** (Wed) | 21 | "For release at 2:00 p.m. EST" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20240221a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20240221a.htm) | 2026-11-16 |
| 35 | March 19-20*, 2024 | 2024-03-20 | **2024-04-10** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20240410a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20240410a.htm) | 2026-11-16 |
| 36 | Apr/May 30-1, 2024 | 2024-05-01 | **2024-05-22** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20240522a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20240522a.htm) | 2026-11-16 |
| 37 | June 11-12*, 2024 | 2024-06-12 | **2024-07-03** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20240703a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20240703a.htm) | 2026-11-16 |
| 38 | July 30-31, 2024 | 2024-07-31 | **2024-08-21** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20240821a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20240821a.htm) | 2026-11-16 |
| 39 | September 17-18*, 2024 | 2024-09-18 | **2024-10-09** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20241009a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20241009a.htm) | 2026-11-16 |
| 40 | November 6-7, 2024 | 2024-11-07 | **2024-11-26** (Tue) | 19 | "For release at 2:00 p.m. EST" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20241126a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20241126a.htm) | 2026-11-16 |
| 41 | December 17-18*, 2024 | 2024-12-18 | **2025-01-08** (Wed) | 21 | "For release at 2:00 p.m. EST" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20250108a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20250108a.htm) | 2026-11-16 |
| 42 | January 28-29, 2025 | 2025-01-29 | **2025-02-19** (Wed) | 21 | "For release at 2:00 p.m. EST" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20250219a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20250219a.htm) | 2026-11-16 |
| 43 | March 18-19*, 2025 | 2025-03-19 | **2025-04-09** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20250409a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20250409a.htm) | 2026-11-16 |
| 44 | May 6-7, 2025 | 2025-05-07 | **2025-05-28** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20250528a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20250528a.htm) | 2026-11-16 |
| 45 | June 17-18*, 2025 | 2025-06-18 | **2025-07-09** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20250709a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20250709a.htm) | 2026-11-16 |
| 46 | July 29-30, 2025 | 2025-07-30 | **2025-08-20** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20250820a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20250820a.htm) | 2026-11-16 |
| 47 | September 16-17*, 2025 | 2025-09-17 | **2025-10-08** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20251008a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20251008a.htm) | 2026-11-16 |
| 48 | October 28-29, 2025 | 2025-10-29 | **2025-11-19** (Wed) | 21 | "For release at 2:00 p.m. EST" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20251119a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20251119a.htm) | 2026-11-16 |
| 49 | December 9-10*, 2025 | 2025-12-10 | **2025-12-30** (Tue) | 20 | "For release at 2:00 p.m. EST" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20251230a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20251230a.htm) | 2026-11-16 |
| 50 | January 27-28, 2026 | 2026-01-28 | **2026-02-18** (Wed) | 21 | "For release at 2:00 p.m. EST" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20260218a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20260218a.htm) | 2026-11-16 |
| 51 | March 17-18*, 2026 | 2026-03-18 | **2026-04-08** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20260408a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20260408a.htm) | 2026-11-16 |
| 52 | April 28-29, 2026 | 2026-04-29 | **2026-05-20** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20260520a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20260520a.htm) | 2026-11-16 |
| 53 | June 16-17*, 2026 | 2026-06-17 | **2026-07-08** (Wed) | 21 | "For release at 2:00 p.m. EDT" | [`fomccalendars.htm`](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) | [`monetary20260708a.htm`](https://www.federalreserve.gov/newsevents/pressreleases/monetary20260708a.htm) | 2026-11-16 |

## 3. Count per year (release dates in 2020-01-02 to 2026-07-16)

| year | releases | rows | note |
|---|---|---|---|
| 2020 | 8 | 1-8 | row 1 is the December 2019 meeting's minutes; row 3 covers the March 15 meeting and the March 2 call |
| 2021 | 8 | 9-16 | row 9 is the December 2020 meeting's minutes |
| 2022 | 8 | 17-24 | |
| 2023 | 8 | 25-32 | |
| 2024 | 8 | 33-40 | |
| 2025 | 9 | 41-49 | the December 2024 meeting's minutes (2025-01-08) and the December 2025 meeting's (2025-12-30) both fall in 2025 |
| 2026 | 4 | 50-53 | to 2026-07-16 only |
| **total** | **53** | | 53 distinct days; no two releases share a day |

## 4. Meetings with no minutes date of their own, and the edges of the range

| meeting (the page's label) | what the page says | consequence for the calendar |
|---|---|---|
| March 2 (unscheduled) Meeting - 2020 | "Minutes: *See end of minutes of March 15 meeting*" (`fomchistorical2020.htm`). The 2020-04-08 press release says the Board and the FOMC "released the attached minutes of the Committee meeting held on March 15, 2020, and of the conference call held on March 2, 2020." | no separate date; covered by row 3 (2020-04-08) |
| March 17-18 (cancelled) Meeting - 2020 | the panel is empty | no minutes |
| March 19, March 23, March 31 and August 27 (notation vote) - 2020 | links to a "Press Release", a "Statement" or the "Statement on Longer-Run Goals and Monetary Policy Strategy"; no minutes entry | no minutes date. Whether these votes are recorded inside a later meeting's minutes was not read; that would add no release day either way |
| August 22 (notation vote), 2025 | links the "Statement on Longer-Run Goals and Monetary Policy Strategy"; the minutes cell is empty | no minutes date |
| October 29-30 Meeting - 2019 | "Minutes (Released November 20, 2019)" | before the range; not in the table |
| July 28-29, 2026 | "(Released August 19, 2026)" | after 2026-07-16, inside the confirmation window; not in the table |

**No date in the range was unstated, and none was stated inconsistently.**

## 5. Facts a builder needs

1. **Do not use the "three weeks" rule in place of the table.** 47 of the 53 releases are exactly 21 days after the
   decision. Six are not:
   - 2020-01-03: 23 days;
   - 2020-04-08: 24 days (the unscheduled March 15 meeting, which the rule does not cover);
   - 2020-11-25, 2023-11-21 and 2025-12-30: 20 days each;
   - 2024-11-26: 19 days.

   Four of the 53 releases are not on a Wednesday: 2020-01-03 is a Friday; 2023-11-21 and 2024-11-26 are the
   Tuesdays of Thanksgiving week; 2025-12-30 is a Tuesday. A calendar built from the rule would put six windows on
   the wrong day.
2. **The time is the same on all 53 days.** 2:00 p.m. ET is 13:00 CT all year, because the two zones change clocks
   together. The pinned file could carry either `14:00` ET (as the CSV does) or `13:00` CT.
3. **Overlap with the pinned early-close calendar** (`config/calendar_early_closes.csv`, E-029). Every one of the 53
   dates was looked up in it, and two appear:
   - **2024-07-03** is an `early_close` at **12:15 CT** (`config/calendar_early_closes.csv:117`). The minutes came out
     at 13:00 CT, after the Globex close, so the 12:58 to 13:02 CT window falls outside the session and no position
     can be open in it.
   - **2020-07-01** is a `data_defect_candidate` (`config/calendar_early_closes.csv:72`), which E-029 voids for
     families. A voided day carries no trade, so its window is moot.

   Neither overlap changes the table. The builder keeps both rows; the count of 5.5 resolves them.
4. **No minutes day is a statement day.** The 53 dates were checked against every statement date in Stage 2's
   vendored source files (`fomc_statements.csv`, `fomc_statements_2020_2024q1.csv`, `fomc_statements_2026q3.csv`;
   54 statement dates in the range, the three unscheduled 2020 statements included) and against the `FOMC` rows of
   `vendor/stage2/config/im2_release_calendar.csv`. None is shared. So "FOMC days out" (E-007 (d)), which names
   statement days, does not reach any of these 53 days. `DRAFT_RD_firms.md:508-510` made that point; this check
   supplies the dates.

## 6. What Stage 2's vendored FOMC files hold

A case-blind search of `vendor/stage2` for "fomc" finds 80 files: configs, scripts, prereg files and documents. A
search for `fomcminutes`, "FOMC minutes", `fomc_minutes` and "Minutes of the Federal Open Market" finds **nothing**.
The four lines where "FOMC" and "minutes" fall within 40 characters of each other use "minutes" for clock minutes
(`prereg/P-04_im2_lifecycle_v3.md:162`, `propedge/data/run_kit.py:1513`, `propedge/data/im2_releases.py:16`,
`propedge/data/flip_kit.py:1740`). The FOMC source files hold **statements only**:

| file | what it holds | minutes? |
|---|---|---|
| `vendor/stage2/config/sources/fomc_statements.csv` | policy statements 2009-05-01 to 2019-12-31 and 2024-04-01 to 2026-08-31; columns `date,meeting,press_conference,statement_url,release_line` (`:5`); read 2026-09-27 | no |
| `vendor/stage2/config/sources/fomc_statements_2020_2024q1.csv` | policy statements 2020-01-01 to 2024-03-31, scheduled and unscheduled, with each statement page's time line (`:9`); read 2026-10-03; its header records the 404s of `fomchistorical2021-2023.htm` (`:3`) | no |
| `vendor/stage2/config/sources/fomc_statements_2026q3.csv` | the September 15-16, 2026 statement (`:7`) | no |
| `vendor/stage2/config/sources/fomc_schedule_2026q4_2027.csv` | statement days scheduled 2026-10-28 to 2027-12-08, for FV3-C's shadow period (`:16`) | no |
| `vendor/stage2/config/im2_release_calendar.csv` | release minutes for IM2; its FOMC rows are all `code = FOMC`, `release = FOMC statement` (110 rows, e.g. `:2389`, 2026-07-29 14:00 ET); no other FOMC code | no |
| `vendor/stage2/propedge/data/im2_releases.py:11-17` | the builder of that calendar; its FOMC source is "the statement dates linked from the Federal Reserve's calendar pages" | no |

Stage 2 built its calendar from Topstep's list, and the FOMC item on that list is the statement, "1:00 PM CT"
(`im2_releases.py:3-5`). The minutes are on TradeDay's list, not Topstep's (`config/rules_extended.yaml:2770-2771`).
That is why Stage 2 never needed a minutes calendar.

**An aside, outside this question.** The 2027 rows on `fomccalendars.htm` as read today differ from Stage 2's
`fomc_schedule_2026q4_2027.csv:25-26`, which was read 2026-10-19:
- the page shows "October 26-27" with "Monetary Policy Strategy Meeting" in its minutes cell;
- the page's last 2027 meeting is "November 16-17", not December 7-8.

Neither this repository's window nor Stage 2's development window reaches 2027. The difference would matter only to
Stage 2's FV3-C shadow schedule, and that file is vendored read-only.

## 7. The CSV beside this note

`docs/research/fomc_minutes_dates_2026-11-16.csv`: 53 data rows and a header row, in release-date order, LF line
endings, plain ASCII, with no comment lines. Its sha256 as written (LF) is
`3a50340f0b9a1d6248cd2c93cc1b5956f798727aae9f950c55a38901f7b7d81a`.

| column | meaning |
|---|---|
| `meeting_end` | the meeting's policy-decision day (the date in its minutes file name) |
| `minutes_release_date` | the "Released" date on the calendar page |
| `release_time_et` | `14:00` on every row. **Source:** the minutes' press release, whose URL is `https://www.federalreserve.gov/newsevents/pressreleases/monetary` + `minutes_release_date` without hyphens + `a.htm`; Appendix A gives each one's hash |
| `source_url` | the calendar page the date was read from |
| `accessed` | `2026-11-16` |

A builder turning this into a pinned `config/` calendar should:
- copy the rows unchanged;
- write a header naming both sources (the calendar pages for dates, the press releases for the time) and this note;
- have the lead pin it by the sha256 of its LF text under a decision row, as E-029 did.

The time source is a URL rule rather than a sixth column because the brief fixed the five columns.

## 8. What is not known, and how it could be found

- **Whether any release reached the market at a time other than its printed embargo line.** The pages state only
  "For release at 2:00 p.m." The bars around 13:00 CT would show it, but reading them is outcome-adjacent and is not
  this note's job. The firms reading treats the window as stated, which is the right default.
- **Whether TradeDay's own platform used these dates.** TradeDay says its tier-1 list is "subject to change without
  notice" (`config/rules_extended.yaml:2775`). Its pages give no historical list of liquidation days. This calendar is
  the Federal Reserve's record of the release days, read as TradeDay's rule names them. A historical record of
  TradeDay's actual liquidations could come only from TradeDay, and that would be an operator question, not a
  research one.
- **The 2021-2023 historical pages** answer 404 today. When the Federal Reserve publishes them, a re-read could
  cross-check rows 10-33 against a second calendar page. Each of those rows is already confirmed on its own press
  release.

## 9. Family declaration

None. This is a fixed input calendar for section 5.5's count and bracket (gap G-3, U-11). It has no mechanism and no
cells, and it uses none of the k budget. What it must satisfy is E-029's pattern:
- fixed before the run;
- built from the stated sources only;
- pinned by sha256 under a row;
- never edited (a change is a new file under a new row).

## 10. Proposed queue line and decision row (for the lead)

- TASK_QUEUE (the lead numbers it): `Q-NN (wt-firms, light): build config/calendar_fomc_minutes.csv from docs/research/fomc_minutes_dates_2026-11-16.csv (53 rows, 2020-01-03..2026-07-08, 14:00 ET), header naming fomccalendars.htm / fomchistorical2019-2020.htm for dates and the monetaryYYYYMMDDa.htm press releases for the time; a unit test that it has 53 rows, distinct dates inside 2020-01-02..2026-07-16 and none on an FOMC statement day of the vendored calendars; the lead pins its LF sha256 -- this closes DRAFT_RD_firms 16 item 2's calendar.`
- Decision row, for the lead to number: `| E-NNN | 2026-11-16 | **Q-73: the FOMC minutes release dates for 2020-01-02 to 2026-07-16 read from the Federal Reserve's own pages** -- 53 releases (2020 8, 2021 8, 2022 8, 2023 8, 2024 8, 2025 9, 2026 4), every date stated on fomccalendars.htm / fomchistorical2019-2020.htm and confirmed on its minutes press release, every one "For release at 2:00 p.m." ET (13:00 CT); none unstated or inconsistent; Stage 2's vendored FOMC files hold statements only. The firms reading's 5.5 reads them once a config/ calendar built from docs/research/fomc_minutes_dates_2026-11-16.csv is pinned. | Brief Q-73; its hand-back. |`

## Appendix A. The 53 press releases as fetched (2026-11-16)

These are the HTML pages as served. They include site chrome, so a later fetch may differ in bytes even when the
release text is unchanged.

| release date | press release | bytes | sha256 |
|---|---|---|---|
| 2020-01-03 | `monetary20200103a.htm` | 81173 | `e49c74eea50b5f07cc9f186a0458f1f03cba5424cf7ee6d1c001241a9cd48a92` |
| 2020-02-19 | `monetary20200219a.htm` | 80958 | `87f363fadd76f08fb0e4f4387a086537254941f315372b168a391c8de88edec5` |
| 2020-04-08 | `monetary20200408a.htm` | 80974 | `4fb489dac14e8f81950650a653259b800a97943a18843b6d0cd164788a54d1a8` |
| 2020-05-20 | `monetary20200520a.htm` | 80926 | `755fa2e4229777f8201c27f54b33ba65599facc68d1e696e1be444b86785303a` |
| 2020-07-01 | `monetary20200701a.htm` | 81146 | `ce147f2804fb5b3acb1652ee1f347f2177b50c308e98b6626cd12f67dd965a9e` |
| 2020-08-19 | `monetary20200819a.htm` | 80978 | `69cc0d37c79b6aee31d121f0d13b70e82a573522a0907d27b0fb361b0516e03b` |
| 2020-10-07 | `monetary20201007a.htm` | 81248 | `91ed168fbaaffc7c7d5ebc5deb85debf314db1e7d803063a6511e9d50ca872b2` |
| 2020-11-25 | `monetary20201125a.htm` | 80949 | `8d9e2f305c6960212c14d9993d2162a15ad289dbcf86fa304dc205dc2ca7972d` |
| 2021-01-06 | `monetary20210106a.htm` | 81029 | `bd3d4b99b794a638e8df162b52f6d807dff2031b034c3beb33963ddd9f66f55c` |
| 2021-02-17 | `monetary20210217a.htm` | 80960 | `5417e844aefe510a26c1bf0c7caf1380440652e9379b4fd0e1a13e580d14e768` |
| 2021-04-07 | `monetary20210407a.htm` | 81007 | `1d1e11b9cf38798ee99f2f7675a6203af1ce2d031959598435a2554b0c3a5266` |
| 2021-05-19 | `monetary20210519a.htm` | 80960 | `b00aec88cfe05d5af0020f3abeb6f30cf42bec8ea31abe4d9c3bdd5585be7163` |
| 2021-07-07 | `monetary20210707a.htm` | 80934 | `24da8302106b53dacc5000b189a3d431c0ce6abda7ee64071ebcb51ae6e7e434` |
| 2021-08-18 | `monetary20210818a.htm` | 80988 | `05aef7c78d15d09b1b44a3aca65f2b601627550d20453fac4e4d3ba13381cb48` |
| 2021-10-13 | `monetary20211013a.htm` | 81045 | `808f355167ec99a750fbbfc160ed5659b140e47e3b4283121bf2f810af0653ba` |
| 2021-11-24 | `monetary20211124a.htm` | 81131 | `d7e72eb330ec025e7d603f2dc9f8ae2ad9587b778e76af14a382482907fb6b26` |
| 2022-01-05 | `monetary20220105a.htm` | 81214 | `73a1ce97f16c5cc85f29847c8a0d4db63c3498d65b91f196772bc3781d0fc8d3` |
| 2022-02-16 | `monetary20220216a.htm` | 81177 | `382647bb238768902b6eb472f10c82856d34b7bd778ab9984aa37a5886e7c596` |
| 2022-04-06 | `monetary20220406a.htm` | 81129 | `e6e750024c8168e44333d174f0d51ee35912b863432296432797d7037942cd02` |
| 2022-05-25 | `monetary20220525a.htm` | 81160 | `ea45db4dde731d26ad8460901daf95992eeae3b99543892198e551b3d0ca2e12` |
| 2022-07-06 | `monetary20220706a.htm` | 81074 | `0baa00cd9aed4e9867a0d97cde85b9797bb440ed10e389e53fce34710ccbd0a0` |
| 2022-08-17 | `monetary20220817a.htm` | 81221 | `db7817079b1e984df4b206ddefcf13441dbf3e2fa147fbb98c5285c1090b65d8` |
| 2022-10-12 | `monetary20221012a.htm` | 81236 | `670834df69eff19b4aeaa088add09d4ed001b61643c5e21375b013debce07065` |
| 2022-11-23 | `monetary20221123a.htm` | 81131 | `f0294833cbf7d70bca1666c63169d309be9476a20838ee929ffbc1b8c7ad2abd` |
| 2023-01-04 | `monetary20230104a.htm` | 81170 | `6b0cc40c862264b32133f81e9fa5e0cb0199c60330f9d8ab75d0199a6f620f75` |
| 2023-02-22 | `monetary20230222a.htm` | 81275 | `0d420b53907527956187b8f817103a628e1ebad2abe38bcba9f4f8adeaebe84a` |
| 2023-04-12 | `monetary20230412a.htm` | 80991 | `bc59a31d383c27b93658df63bfc78fda47366562ea2e8dfd120ea5c9d8a65293` |
| 2023-05-24 | `monetary20230524a.htm` | 80912 | `65767c089a584381a5950e874b47039805ac55fbaa933dab36158c2605d11365` |
| 2023-07-05 | `monetary20230705a.htm` | 81005 | `d4319298eea7b8443bd15e6b9c0bc3412e567d3231d9a7b721632ff91caf6b77` |
| 2023-08-16 | `monetary20230816a.htm` | 80948 | `bd4874dc9ec11c7f3c1842fc07af8afd6507cb4d94694d5c9aa0ebffbfdd73c2` |
| 2023-10-11 | `monetary20231011a.htm` | 81006 | `79e60d0af7b66a05194c0305df1ef36fcf8fffee745a49d17ab924e916bb9812` |
| 2023-11-21 | `monetary20231121a.htm` | 81102 | `cb3aef9b11b7039b1adfc36536e911e4c3ea64a19aa06f6277952839a77a5119` |
| 2024-01-03 | `monetary20240103a.htm` | 81026 | `6c2931090ded37ac736a80ef3e949819fc870870e1fb3906045ff9d84b6ab5c1` |
| 2024-02-21 | `monetary20240221a.htm` | 81041 | `363bb895ecb7ab8b34420ba8783345ed1a2e76d0f21ae8cd9339b5cbdd83adde` |
| 2024-04-10 | `monetary20240410a.htm` | 80960 | `2aa2431df626e3feba986c540ba27f3bd76b7aa7998fee32337b6b995e324ded` |
| 2024-05-22 | `monetary20240522a.htm` | 80981 | `bd51aa798ea85539d8feeaddb072a25f051ff4e4d40361e33f64a940db838c91` |
| 2024-07-03 | `monetary20240703a.htm` | 81018 | `78385e30ccd47c4b9d95ab9b2a90aedacbc9a2860844a826d73add1a8eb1fdf9` |
| 2024-08-21 | `monetary20240821a.htm` | 81020 | `5ef0ded81c9ba9df066652b6c6f61044485404a505918a9e0df812da41617360` |
| 2024-10-09 | `monetary20241009a.htm` | 81039 | `c4ddcaf99ca09aa16bf20edbd4b7a0e343bc7388752c021af9a69999fd42fbf6` |
| 2024-11-26 | `monetary20241126a.htm` | 81004 | `8366dc42dd76c693b27ceba79cdcfd0d270c3337f61ccf78a3a01e28f0a99649` |
| 2025-01-08 | `monetary20250108a.htm` | 81060 | `c80f15be92af23636e8731ffce9c52fcc1056c95a5aea122b91aa8678a665fa8` |
| 2025-02-19 | `monetary20250219a.htm` | 81036 | `761ae18b804bf4d3c899237eb75e80469516b2d115712c672803daf306d9a742` |
| 2025-04-09 | `monetary20250409a.htm` | 81070 | `9538aca1dffa49b321f5e6ee70101c1050d7f5021195135b8461845b0e099926` |
| 2025-05-28 | `monetary20250528a.htm` | 80981 | `6be972392e5901973d60165ed4c1ba73e3440d25de73f602e0861df6a971cf70` |
| 2025-07-09 | `monetary20250709a.htm` | 81052 | `8c64150f375a037aede408e211ac79a13e86379f26f146e53e7f4f4e06caec31` |
| 2025-08-20 | `monetary20250820a.htm` | 81052 | `574f39d329c83fdbecbd95f5de17c1b0093cb1b42770d5414eb21e9575a36238` |
| 2025-10-08 | `monetary20251008a.htm` | 81107 | `d2a1cca6c122ca449477ebd4ac19640c988bda29f4fede69ddb7a344cb40f9d2` |
| 2025-11-19 | `monetary20251119a.htm` | 81049 | `92a82a8eff37e4caa1ec376011fce332172ceccdb90bc2454194056b1a2a5b4d` |
| 2025-12-30 | `monetary20251230a.htm` | 81030 | `0662ed66e8157396ed8bec0431b2a71a0b2291dc548641b217f60d284aa4d2f8` |
| 2026-02-18 | `monetary20260218a.htm` | 81029 | `8f3f654958184c2e4243b59857d54aa5e9952eb975e1d2adffc5ee7f93b1ba0b` |
| 2026-04-08 | `monetary20260408a.htm` | 81105 | `c520ddc62a75d2e669059abac9515873cfd4206c921f146fbd523fa69aec7af2` |
| 2026-05-20 | `monetary20260520a.htm` | 81060 | `9fd21481c230c7c8e68b3cb9861b63e5d3294686b79c003687834faef936be45` |
| 2026-07-08 | `monetary20260708a.htm` | 81050 | `379a12a06ce1d9863991ff1b8b8a18705dd44ddcc5200fdf93718276eaf56d54` |
