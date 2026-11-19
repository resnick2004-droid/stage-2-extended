**Verdict: BLOCKED**

# H2 (Q-154): NQ overnight 1-minute bars, 17:00 to 08:30 CT -- data integrity, 2026-11-18

Rendered by `scripts/h2_overnight_bars.py` from its JSON (`extended/overnight_bars_check.py`); every number below is computed from the bars or the store's manifest by that script, none typed. Counts, shares, clock labels and dates only: no price, return or range.

**Why blocked:**
- the held-out years' overnight bars were not read (the reader's seal, Q-158): their gaps, duplicates, clock continuity, bar validity and slot presence are unchecked.
- 6 search-year overnights are void by the rules fixed before the read; no void calendar exists yet outside this report, so a source reading overnight bars cannot drop them by a pinned file.

## Can the family's question be answered on this data?

The held-out block holds 657 sessions, 10 whole 63-session blocks; an exact sign-flip over 10 blocks cannot reach below 0.000977, against the family's level 0.05 / (13 x 14) = 0.000275 (that needs 12 blocks): it cannot reach it -- so, as E-208 records, only the paired coin-seed leg can carry the level and the years leg is a consistency condition. The search block holds 1034 sessions (16 blocks). An overnight source adds offer moments inside sessions, not sessions: it does not change this arithmetic.

Stage one's sample-size table (`vendor/stage2/vendor/propsim/edge/results_sample_size.csv`): the trades a demonstrated edge e needs, beside the sessions here (at one trade a session):

| R | e | trades (lower bound above e/2) | search sessions | held-out sessions |
|---|---|---|---|---|
| 1.5 | 0.05 | 6592 | 1034 | 657 |
| 1.5 | 0.1 | 1667 | 1034 | 657 |
| 1.5 | 0.2 | 423 | 1034 | 657 |
| 2.0 | 0.05 | 8865 | 1034 | 657 |
| 2.0 | 0.1 | 2263 | 1034 | 657 |
| 2.0 | 0.2 | 585 | 1034 | 657 |
| 3.0 | 0.05 | 13412 | 1034 | 657 |
| 3.0 | 0.1 | 3453 | 1034 | 657 |
| 3.0 | 0.2 | 910 | 1034 | 657 |

The journey objective judges P on coin-sided designs, not an edge, so the table bounds only a claim of edge, which no overnight trigger here makes.

## Source, span and the confirmation window

- **Store:** `vendor/stage2/data/bars/NQ/` (Stage 2 D-458), Databento historical data under the operator's licence: private use, no redistribution; tick 0.25; `parquet_sha256` `c391d97ad1c11db3ce0da0c65f0d0ac9df1582617666b37c00ad206c3add2041`. `python scripts/vendor_stage2.py --verify`: exit 0; data: 8 files match DATA_MANIFEST_stage2.sha256.
- **Purchase** `GLBX-20261008-EQHDB8M3K5.zip` (`glbx-mdp3-20200101-20250629.ohlcv-1m.csv`; GLBX.MDP3, ohlcv-1m, NQ.FUT), imported 2026-10-30T11:10:58+00:00; days dropped by the windows guard 0 (first: None). Cost: not recorded in the manifest.
- **Purchase** `GLBX-20261014-WGBSWWD6RT.zip` (`glbx-mdp3-20250701-20261012.ohlcv-1m.csv`; GLBX.MDP3, ohlcv-1m, NQ.FUT), imported 2026-10-30T11:11:06+00:00; days dropped by the windows guard 63 (first: 2026-07-17). Cost: not recorded in the manifest.
- **Span stored:** 2020-01-02 to 2026-07-16, 1691 trading days, 2308343 bars. **Nothing from the confirmation window is present:** the store's last day is 2026-07-16; every frame loaded was asserted to hold no bar starting at or after 16:00 CT on 2026-07-16 (`assert_loaded`); the last search day loaded is 2023-12-29.
- **Contract continuation:** one outright a trading day, the previous day's outright-volume leader (Stage 2 D-98); **raw prices**, no back- or ratio-adjustment, so a cross-day level jumps by the calendar spread on a roll day (26 rolls in the store). `vendor/stage2/data/README.md` section 5.
- **Calendar used:** `config/calendar_early_closes.csv` (Q-40: the U.S. exchange holiday rules, cross-checked against the manifest; CME's pages refuse scripted reads); BLS 08:30 ET release days from the vendored schedule parses (`extended.features.load_calendars`). No CME calendar is vendored under `vendor/stage2/config/sources/` (FOMC and EIA schedules only).

## The clock: what the code assumes and what the data shows

- README section 5: a session opens at 17:00 CT the evening before; `day` = the bar's Chicago time plus seven hours, its date; `ts` the bar's **start**. `extended.lever_space.trading_day()`: reopen 17:00 CT, flat 15:10 CT. The features grid and RL3's `on` level read slots 0..929 (bars stamped 17:00..08:29); RL3's reference is the bar stamped 08:29.
- **The daily maintenance break** is the 16:00-16:59 CT halt: bars stamped there in the search years: 2. No break inside 17:00-08:29 is scheduled; the gap clock below shows none recurring.
- **Reopen** (the first bar of each search-year day, CT, days): {'17:00': 1033, '19:00': 1}.
- **The manifest's `day_bounds` against the bars** (search years): the first bar agrees on 1034 of 1034 days (disagreeing: none) -- the basis for reading the held-out reopen times from the manifest.

## The search years, 2020-01-02 to 2023-12-29 (bars read)

1034 trading days, 2020-01-02 to 2023-12-29; 959452 overnight bars of 961620 day-minutes 17:00-08:29 (99.77 % present).

| check | result |
|---|---|
| schema, dtypes | columns and dtypes as README section 5: `ts` int64, `day` string, `contract` string, `open` float64, `high` float64, `low` float64, `close` float64, `volume` int64 |
| `day` against the clock's rule | 0 bars disagree |
| duplicate timestamps / two bars in one (day, slot) | 0 / 0 |
| out-of-order timestamps | not checkable through the reader (it sorts by `ts`, stably); after the sort, duplicates as above |
| bars stamped 16:00-16:59 CT / trading days dated a weekend | 2 (2020-03-31 16:59 CT, 2020-06-30 16:59 CT) / 0 |
| days holding two contracts | 0 |
| clock breaks (consecutive bars whose UTC gap differs from their CT slot gap) | 0 |
| overnights under two UTC offsets | 0 |
| malformed overnight bars (off tick, price <= 0, high/low not bracketing open and close, volume < 0) | 0 |
| zero-volume overnight bars | 0 |
| minutes missing between the reopen and the scheduled overnight end, of the scheduled overnight minutes (17:00 to 08:29, or to an earlier close) | 2018 of 961590 (0.210 %) |
| longest gap | 80 minutes from 00:28 CT on trading day 2020-03-16 |

**Gaps after the reopen** (runs of minutes with no bar; a minute without a trade has no bar), by length: runs, and days holding at least one:

| run length (minutes) | runs | days |
|---|---|---|
| 1 | 293 | 103 |
| 2-4 | 166 | 9 |
| 5-14 | 82 | 8 |
| 15-29 | 20 | 3 |
| >=30 | 5 | 1 |

**Where the missing minutes concentrate** (calendar month: minutes missing after the reopen): 2020-03 1885, 2021-06 12, 2023-06 12, 2020-01 8; outside 2020-03, the most on any day is 8 minutes (2021-06-14).

**The days with the most minutes missing after the reopen** (trading day, minutes missing, longest run): 2020-03-16 (762, 80), 2020-03-18 (397, 28), 2020-03-17 (300, 26), 2020-03-09 (241, 8), 2020-03-13 (59, 6), 2020-03-23 (51, 9), 2020-03-12 (37, 5), 2020-03-24 (20, 3), 2020-03-20 (18, 7), 2021-06-14 (8, 1), 2020-01-20 (5, 1), 2021-04-02 (5, 1).

**Gaps of 15 minutes or more** (each voids its day; trading day, start CT, minutes): 2020-03-16 20:55 (16), 2020-03-16 21:28 (27), 2020-03-16 22:34 (17), 2020-03-16 22:56 (28), 2020-03-16 23:53 (21), 2020-03-16 00:28 (80), 2020-03-16 02:01 (30), 2020-03-16 04:00 (16), 2020-03-16 04:17 (50), 2020-03-16 06:08 (38), 2020-03-16 06:48 (73), 2020-03-16 08:02 (16), 2020-03-17 22:52 (24), 2020-03-17 23:46 (26), 2020-03-17 01:48 (20), 2020-03-17 02:32 (23), 2020-03-18 01:32 (17), 2020-03-18 02:40 (20), 2020-03-18 04:01 (17), 2020-03-18 04:49 (25), 2020-03-18 05:35 (17), 2020-03-18 05:57 (22), 2020-03-18 06:34 (17), 2020-03-18 07:31 (28), 2020-03-18 08:07 (23).

**Where gaps of 2 minutes or more start, by CT hour** (the thin hours):

| hour | 17:00 | 18:00 | 19:00 | 20:00 | 21:00 | 22:00 | 23:00 | 00:00 | 01:00 | 02:00 | 03:00 | 04:00 | 05:00 | 06:00 | 07:00 | 08:00 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gaps | 11 | 13 | 8 | 11 | 10 | 18 | 10 | 18 | 19 | 28 | 30 | 12 | 25 | 18 | 25 | 17 |

**Bars by CT hour** (share of scheduled day-minutes holding a bar; of the bars, the share flat -- open = high = low = close -- and the share thin, volume <= 5):

| hour | present | flat | thin | zero volume |
|---|---|---|---|---|
| 17:00 | 99.80 % | 0.43 % | 1.63 % | 0 |
| 18:00 | 99.77 % | 0.31 % | 1.25 % | 0 |
| 19:00 | 99.93 % | 0.03 % | 0.11 % | 0 |
| 20:00 | 99.89 % | 0.11 % | 0.25 % | 0 |
| 21:00 | 99.85 % | 0.26 % | 0.66 % | 0 |
| 22:00 | 99.80 % | 0.49 % | 1.82 % | 0 |
| 23:00 | 99.77 % | 0.61 % | 2.29 % | 0 |
| 00:00 | 99.76 % | 0.25 % | 0.77 % | 0 |
| 01:00 | 99.71 % | 0.13 % | 0.25 % | 0 |
| 02:00 | 99.70 % | 0.09 % | 0.10 % | 0 |
| 03:00 | 99.79 % | 0.16 % | 0.16 % | 0 |
| 04:00 | 99.78 % | 0.14 % | 0.16 % | 0 |
| 05:00 | 99.75 % | 0.19 % | 0.20 % | 0 |
| 06:00 | 99.74 % | 0.14 % | 0.11 % | 0 |
| 07:00 | 99.67 % | 0.16 % | 0.14 % | 0 |
| 08:00 | 99.66 % | 0.18 % | 0.16 % | 0 |

**The slots the overnight sources read** (share of the block's days):

- RL3 `on`: the bar stamped 08:29 (its reference; `no_ref_bar` otherwise) 99.32 %; at least one bar 17:00-08:29 100.00 %.
- `compute_overnight`: the bar stamped at alert - 1, over the alerts 17:05..08:25: lowest 99.42 %, mean 99.77 %; the lowest alerts 08:20 (99.42 %), 18:00 (99.52 %), 07:25 (99.52 %), 07:55 (99.52 %), 08:25 (99.52 %), 17:50 (99.61 %). At least one bar in the five minutes before the alert: lowest 99.61 %. The close c defined (any bar of the day before the alert): at 17:05 99.90 %, lowest over the alerts 99.90 %. The bar stamped 17:00: 99.90 %.

**Roll evenings:** 16 roll days in the block; the days the bars change contract agree with the manifest's `rolls` (2020-03-17, 2020-06-16, 2020-09-15, 2020-12-15, 2021-03-16, 2021-06-15, 2021-09-14, 2021-12-13, 2022-03-15, 2022-06-14, 2022-09-13, 2022-12-13, 2023-03-14, 2023-06-13, 2023-09-12, 2023-12-12). On 4 of 16 the reopen jump (first open against the previous day's last close, in ticks) exceeds the 99.5th percentile of the non-roll evenings' -- the calendar spread the raw series carries, fictitious as a move. Minutes missing after the reopen, mean a day: roll days 19.12, other days 1.68. Inside a roll day the series is one contract (two-contract days above).

**The clock check on release days** (the 08:30 ET BLS release is the bar stamped 07:30 CT; the overnight minute 06:00-08:29 CT with the most volume):

| days | n | at 07:30 | within a minute | an hour off |
|---|---|---|---|---|
| all release days | 239 | 48.1 % | 51.9 % | 9 |
| release days within 7 days after a US change | 14 | 21.4 % | 28.6 % | 0 |
| the other release days | 225 | 49.8 % | 53.3 % | 9 |
| non-release weekdays (control) | 795 | 9.6 % | 10.8 % | 123 |
| major releases (Employment Situation, CPI) | 95 | 67.4 % | 70.5 % | 1 |
| major releases within 7 days after a US change | 5 | 40.0 % | 60.0 % | 0 |
| the other major releases | 90 | 68.9 % | 71.1 % | 1 |
| all release days, window 06:00-07:59 | 239 | 51.5 % | 56.9 % | 2 |
| release days within 7 days after a US change, window 06:00-07:59 | 14 | 28.6 % | 35.7 % | 0 |
| major releases, window 06:00-07:59 | 95 | 69.5 % | 75.8 % | 1 |
| non-release weekdays, window 06:00-07:59 | 795 | 12.3 % | 15.0 % | 12 |

The first four rows are the reading fixed before the first run; the rest were added after it, to diagnose its low share (minor releases move little; the 08:00 hour's pre-open volume competes) -- the first reading stays on record. Where the busiest minute falls instead (all release days, window to 08:29): {'08:29': 8, '07:32': 7, '08:28': 5, '08:25': 5, '08:09': 4, '07:00': 4, '08:12': 3, '08:04': 3}; window to 07:59: {'07:32': 8, '07:33': 6, '07:48': 4, '07:39': 4, '07:00': 4, '07:49': 3, '06:47': 3, '07:22': 3}.

Release days whose busiest minute is elsewhere: 2020-01-14, 2020-01-15, 2020-01-16, 2020-01-31, 2020-02-06, 2020-02-13, 2020-02-14, 2020-02-19, 2020-03-05, 2020-03-06, 2020-03-11, 2020-03-12, 2020-03-13, 2020-04-14, 2020-04-30, 2020-05-07, 2020-05-12, 2020-05-13, 2020-05-14, 2020-06-04, 2020-06-05, 2020-06-10, 2020-06-11, 2020-06-12, 2020-07-10, 2020-07-14, 2020-07-15, 2020-07-31, 2020-08-11, 2020-08-12, 2020-08-13, 2020-08-14, 2020-09-03, 2020-09-04, 2020-09-10, 2020-09-11, 2020-09-15, 2020-10-02, 2020-10-13, 2020-10-14, ... (115 in all).

**The daylight-saving transitions** (each change is at 02:00 local on a Sunday, while the market is shut between Friday 16:00 and Sunday 17:00 CT; the last session before it and the first after):

| change | before: day, reopen, UTC offset | after: day, reopen, UTC offset | after: breaks / offsets / dup slots / missing |
|---|---|---|---|
| 2020-03-08 | 2020-03-06, 17:00, -6 h | 2020-03-09, 17:00, -5 h | 0 / 1 / 0 / 241 |
| 2020-11-01 | 2020-10-30, 17:00, -5 h | 2020-11-02, 17:00, -6 h | 0 / 1 / 0 / 0 |
| 2021-03-14 | 2021-03-12, 17:00, -6 h | 2021-03-15, 17:00, -5 h | 0 / 1 / 0 / 0 |
| 2021-11-07 | 2021-11-05, 17:00, -5 h | 2021-11-08, 17:00, -6 h | 0 / 1 / 0 / 1 |
| 2022-03-13 | 2022-03-11, 17:00, -6 h | 2022-03-14, 17:00, -5 h | 0 / 1 / 0 / 0 |
| 2022-11-06 | 2022-11-04, 17:00, -5 h | 2022-11-07, 17:00, -6 h | 0 / 1 / 0 / 0 |
| 2023-03-12 | 2023-03-10, 17:00, -6 h | 2023-03-13, 17:00, -5 h | 0 / 1 / 0 / 0 |
| 2023-11-05 | 2023-11-03, 17:00, -5 h | 2023-11-06, 17:00, -6 h | 0 / 1 / 0 / 0 |

Across the block: 0 clock breaks and 0 overnights under two UTC offsets.

**Session boundaries abroad** (not a data defect -- the declared windows are fixed in CT, `lever_space.declared('windows_ct')`): 08:00 London is not 02:00 CT on 65 days (the US and the UK change on different Sundays): 2020-03-09 to 2020-03-27 (15), 2020-10-26 to 2020-10-30 (5), 2021-03-15 to 2021-03-26 (10), 2021-11-01 to 2021-11-05 (5), 2022-03-14 to 2022-03-25 (10), 2022-10-31 to 2022-11-04 (5), 2023-03-13 to 2023-03-24 (10), 2023-10-30 to 2023-11-03 (5). 09:00 Tokyo falls at CT {'18:00': 356, '19:00': 678} (days), so `asia` from 18:00 CT is Tokyo's open only under US standard time.

**Void and special days** (rules fixed in `extended/overnight_bars_check.py` before the read):

- **VOID: 6 days.** By rule: {'late_reopen': 1, 'long_gap': 3, 'manifest_defect': 3, 'outside_hours': 2}.
  - 2020-03-16: long_gap, manifest_defect
  - 2020-03-17: long_gap
  - 2020-03-18: long_gap, manifest_defect
  - 2020-03-31: outside_hours
  - 2020-06-30: outside_hours
  - 2020-07-01: late_reopen, manifest_defect
- **SPECIAL** (counts by flag): {'abbreviated_day': 34, 'after_abbreviated': 34, 'after_closure': 8, 'bls_0730': 239, 'degraded_utc': 9, 'gap_5_14': 8, 'london_shift': 65, 'no_0829_bar': 5, 'roll': 16, 'scheduled_short_overnight': 2, 'sunday_open': 205, 'us_dst_session': 8}.
  - `abbreviated_day`: 2020-01-20, 2020-02-17, 2020-05-25, 2020-07-03, 2020-09-07, 2020-11-26, 2020-11-27, 2020-12-24, 2021-01-18, 2021-02-15, 2021-04-02, 2021-05-31, 2021-07-05, 2021-09-06, 2021-11-25, 2021-11-26, 2022-01-17, 2022-02-21, 2022-05-30, 2022-06-20, 2022-07-04, 2022-09-05, 2022-11-24, 2022-11-25, 2023-01-16, 2023-02-20, 2023-04-07, 2023-05-29, 2023-06-19, 2023-07-03, 2023-07-04, 2023-09-04, 2023-11-23, 2023-11-24
  - `after_abbreviated`: 2020-01-21, 2020-02-18, 2020-05-26, 2020-07-06, 2020-09-08, 2020-11-27, 2020-11-30, 2020-12-28, 2021-01-19, 2021-02-16, 2021-04-05, 2021-06-01, 2021-07-06, 2021-09-07, 2021-11-26, 2021-11-29, 2022-01-18, 2022-02-22, 2022-05-31, 2022-06-21, 2022-07-05, 2022-09-06, 2022-11-25, 2022-11-28, 2023-01-17, 2023-02-21, 2023-04-10, 2023-05-30, 2023-06-20, 2023-07-04, 2023-07-05, 2023-09-05, 2023-11-24, 2023-11-27
  - `degraded_utc`: 2020-02-27, 2020-02-28, 2020-05-05, 2020-05-06, 2020-06-30, 2020-07-01, 2020-07-02, 2021-12-06, 2022-01-03
  - `us_dst_session`: 2020-03-09, 2020-11-02, 2021-03-15, 2021-11-08, 2022-03-14, 2022-11-07, 2023-03-13, 2023-11-06
  - `gap_5_14`: 2020-03-09, 2020-03-12, 2020-03-13, 2020-03-16, 2020-03-17, 2020-03-18, 2020-03-20, 2020-03-23
  - `no_0829_bar`: 2020-03-09, 2020-03-12, 2020-03-13, 2020-03-16, 2020-03-18
  - `after_closure`: 2020-04-13, 2020-12-28, 2021-01-04, 2021-12-27, 2022-04-18, 2022-12-27, 2023-01-03, 2023-12-26
  - `scheduled_short_overnight`: 2021-04-02, 2023-04-07

## The held-out years, 2024-01-02 to 2026-07-16 (manifest only; bars not read)

The reader seals these years (`extended/reader.py`, CHARTER 3.6-3.7, Q-158): a read touching them needs a pinned declaration naming its purpose on a `Judged-block reads:` line, inside a clean run, once. No declaration names a data check, so the bars were **not read**. What the manifest -- metadata, no bar -- shows:

- 657 trading days, 2024-01-02 to 2026-07-16; reopen (first bar, CT, days): {'17:00': 655, '17:02': 1, '19:00': 1}.
- Reopen after 17:05 CT: 2025-07-01. The manifest's late-start days: 2025-04-03, 2025-07-01; short days (< 1,000 bars): {'2025-01-09': 930, '2025-06-30': 120, '2025-11-28': 508, '2026-04-03': 909}; days ending before 15:00 CT: 28.
- The manifest's short days against their scheduled length (17:00 to the scheduled close; trading day: bars / scheduled minutes, deficit, first-last bar CT, Databento degraded): 2025-01-09: 930 / 930, 0, 17:00-08:29; 2025-06-30: 120 / 1380, 1260, 17:00-18:59; 2025-11-28: 508 / 1155, 647, 17:00-12:14, degraded; 2026-04-03: 909 / 915, 6, 17:00-08:14.
- Q-40's data-defect candidates: 2025-04-03, 2025-06-30, 2025-07-01.
- Overnights spanning a UTC date Databento marks `degraded`: 2024-09-18, 2024-09-19, 2025-09-17, 2025-09-18, 2025-09-24, 2025-09-25, 2025-11-28, 2026-03-16, 2026-03-17, 2026-04-10, 2026-05-25.
- Rolls: 2024-03-12, 2024-06-18, 2024-09-17, 2024-12-18, 2025-03-19, 2025-06-17, 2025-09-17, 2025-12-16, 2026-03-17, 2026-06-16.
- Evenings: Sunday opens 132; after a full closure 2024-01-02, 2024-04-01, 2024-12-26, 2025-01-02, 2025-04-21, 2025-12-26, 2026-01-02; after an abbreviated session 2024-01-16, 2024-02-20, 2024-05-28, 2024-06-20, 2024-07-04, 2024-07-05, 2024-09-03, 2024-11-29, 2024-12-02, 2024-12-26, 2025-01-10, 2025-01-21, 2025-02-18, 2025-05-27, 2025-06-20, 2025-07-04, 2025-07-07, 2025-09-02, 2025-11-28, 2025-12-01, 2025-12-26, 2026-01-20, 2026-02-17, 2026-04-06, 2026-05-26, 2026-06-22, 2026-07-06; abbreviated days 27; a scheduled close before 08:30 CT (the overnight itself cut) 2026-04-03.
- First sessions after a US daylight-saving change (change -> session, its reopen per the manifest): 2024-03-10 -> 2024-03-11 17:00, 2024-11-03 -> 2024-11-04 17:00, 2025-03-09 -> 2025-03-10 17:00, 2025-11-02 -> 2025-11-03 17:00, 2026-03-08 -> 2026-03-09 17:00.
- 08:00 London not at 02:00 CT: 54 days; BLS 07:30 CT release days: 148.
- **Not checked** (they need the bars): gaps and their clock, duplicates, the 16:00-16:59 halt, clock continuity across the DST sessions, malformed or zero-volume bars, flat and thin shares, slot presence for the features and RL3's `on`, the roll-evening jump, the BLS clock check.

## Known limitations

- **The held-out years' overnight bars are unchecked.** Until a row authorises their read, no overnight source may be judged on them.
- **A minute without a trade has no bar.** A 1-4 minute gap in the thin hours is the market, not a defect; an order inside it fills on the next bar's range, and a fill on a bar that gaps past a stop is the stop-fill convention's question (conduct tier 1), not this data's.
- **The gaps sit in one month (2020-03).** The void rule fixed before the read (a run of 15 minutes or more) leaves that month's days with many shorter gaps SPECIAL (`gap_5_14`, `no_0829_bar`), not VOID; the days with the most missing minutes are listed above. Whether an overnight source drops the whole month, or those days, is a decision for its own row, made from this list and not from outcomes.
- **Stray bars stamped 16:59 CT** (the table above) belong to the day they close (Chicago + 7 h) and fall after its overnight; what they move is the next day's cross-day reads of the previous close (`extended.features`' day-level last close), and the fixed rule voids their day as outside the session.
- **Raw prices across rolls.** A cross-day level is the old contract's price on a roll day; the features set such features NaN there and RL3 voids `pd` and `pdc`. A roll day's own overnight levels (RL3 `on`) are within one contract and stand.
- **Out-of-order rows in the file** cannot be seen through the reader, which sorts; the importer writes the file sorted (README section 5), and a double-write would survive the stable sort as a duplicate.
- **The day boundary** is the store's (Chicago + 7 h): 16:59 CT belongs to the day it closes, 17:00 to the next. CME books a holiday's abbreviated session to the next business day; the store dates it to the holiday (Q-40).
- **Session windows abroad** are fixed in CT: London's 08:00 and Tokyo's 09:00 move against them for parts of each year, so a source keyed to `london` or `asia` reads a different market hour on those days.

## What a future session must not assume

- That the held-out overnight bars are clean because the search years' are.
- That every overnight minute has a bar, or that a feature at an overnight alert reads a bar stamped at alert - 1 (it reads the last bar before the alert, forward-filled).
- That the 08:29 bar exists (RL3 voids the day without it), or that the overnight runs to 08:29 on a Good Friday with the jobs report (the session closes 08:15 CT).
- That the series is continuous across a roll or across the purchase seam (2025-06-30 / 2025-07-01).
- That a CT session window is the same market hour abroad all year.

## To unblock

1. A decision row authorising this check's held-out read by a mechanism the reader accepts (a pinned declaration whose `Judged-block reads:` line names a data-integrity purpose, run once in a clean run), then `scripts/h2_overnight_bars.py --held-out` from that clean run, the held-out section rendered from the bars by the same code.
2. The void list as a pinned calendar (this script's re-runnable output, dates and reasons only, outside `vendor/`) under its own row, read by every overnight source before it builds its offers.

## Reproduce

`python scripts/h2_overnight_bars.py` (outputs: this report, its JSON, the flags `results\h2_overnight_flags.csv`), commit `3cf3453c2e23198bcb1b86c2093120977023ecca` (clean); run 2026-11-19T08:33:39Z under the run lock with `OMP_NUM_THREADS=1`. The code run, by sha256: `scripts/h2_overnight_bars.py` `d89ccc6797ecd576d3e497dd7aeacde4a0835b20dfafeb9ac7e4990069bd27d4`, `extended/overnight_bars_check.py` `0f5673d597c97f9452e0ab8ed74ff9b3a6f6391a385c32ee0d9428e467066e4b`.
