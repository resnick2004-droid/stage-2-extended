# data/ — required formats

`data/raw/`, `data/processed/` and `data/bars/` are **git-ignored**. Market data is large and
usually licensed; it does not belong in the repository. What belongs here is this description of
the shape it must have, so that a future session can check any file it is handed.

> **What has been supplied.** T2 in [`../NEXT_STEPS.md`](../NEXT_STEPS.md) closed on
> QuantConnect's data, whose raw bars stay in QuantConnect's cloud (D-39, D-120). In the
> repository: the BLS release calendars (§4). On this PC only, git-ignored: the operator's
> Databento 1-minute bars in the local bar store (§5, D-458). The **data-integrity** agent
> blocks unvalidated data from entering the harness.

## Why the data is a gate, not a detail

Stage one established the sample size a demonstrated edge needs
(`vendor/propsim/edge/results_sample_size.csv`):

| R | e = 0.05 | e = 0.10 | e = 0.20 |
|---|---|---|---|
| 1.5 | 6,592 trades (26 yrs at 1/day) | 1,667 (6.6 yrs) | 423 (1.7 yrs) |
| 2 | 8,865 (35 yrs) | 2,263 (9 yrs) | 585 (2.3 yrs) |
| 3 | 13,412 (53 yrs) | 3,453 (14 yrs) | 910 (3.6 yrs) |

If the available history is shorter than the relevant row, **no candidate can meet the
criterion** and the stage ends at outcome (B) before any strategy is written. Establish the
span before writing strategies, not after.

---

## 1. Bar data — `data/raw/<symbol>/<resolution>/*.csv` (or Parquet)

(The operator's Databento bars have their own place and shape: the local bar store, §5.)

One row per bar. Resolution fine enough to model a stop honestly: if the stop is 12 ticks
away, daily bars cannot say whether it was hit before the target.

| column | type | notes |
|---|---|---|
| `timestamp` | ISO 8601 | **Bar OPEN time.** Timezone-aware, or documented as US/Central. State which; an hour's ambiguity moves trades across the 15:10 CT flatten |
| `open`, `high`, `low`, `close` | float | prices in the instrument's quote units |
| `volume` | int | |
| `symbol` | string | matches a key in [`../config/instruments.yaml`](../config/instruments.yaml) |

Also required, written into the data report rather than the file:

- **Contract continuation**: how the continuous series is built across expiries — roll date
  rule, back-adjusted or ratio-adjusted or raw. This changes every price level and therefore
  every stop distance in ticks. An unadjusted series has fictitious gaps at every roll.
- **Session definition**: the CME session runs 17:00 CT to 16:00 CT the next day. Which
  calendar day a bar belongs to determines which trading day its P&L lands in, which
  determines the 16:00 CT lock, the ratchet and the winning-day count.
- **Holiday calendar** and early closes.

### Checks the data-integrity agent runs

- Schema and dtypes as above.
- **Gaps**: missing bars inside a session. A gap that swallows a stop makes a losing trade
  look like a winner.
- **Duplicates**: repeated timestamps, usually a roll or a vendor artefact.
- **Timezone**: consistency, and correct handling of daylight-saving transitions.
- **Session boundaries**: bars falling outside the declared session.
- **Look-ahead risks**: any column derived from the future (a settlement price, an adjusted
  close, a signal computed on the whole series).
- **Span**: total trading days and bars, compared against the sample-size table above.

---

## 2. Trade logs — `data/processed/<name>_trades.csv`

The canonical schema, defined and enforced by
[`../propedge/outcomes/tradelog.py`](../propedge/outcomes/tradelog.py):

| column | type | notes |
|---|---|---|
| `timestamp_in` | datetime, US/Central | entry |
| `timestamp_out` | datetime, US/Central | exit |
| `symbol` | string | |
| `side` | `long` \| `short` | |
| `entry_price`, `exit_price` | float | **actual fill prices**, after the fill model |
| `stop`, `target` | float | as *placed*, so risk can be recomputed and checked |
| `contracts` | int | ≥ 1; integer sizing rounds down |
| `pnl_gross` | float | price move only |
| `pnl_net` | float | after commission, exchange fees and slippage |
| `exit_reason` | `target` \| `stop` \| `flatten` \| `other` | |

Optional and preserved: `dollars_risked`, `commission`, `slippage_dollars`, `fold`,
`variant`, `prereg_id`.

**`exit_reason` matters more than it looks.** A trade closed by the 15:10 CT flatten is
`flatten`, never `stop` or `target`, and its P&L is whatever the market gave —
`vendor/propsim/HANDOFF.md` §3: *"trades not resolved by then are closed at market — record
their actual P&L, do not assume binary."* The share of flattened trades is how far the
strategy departs from stage one's binary model, and
`propedge.outcomes.distribution.EmpiricalDraw.flatten_share` reports it.

The loader rejects, among other things, `pnl_net > pnl_gross` — negative cost — because that
means either mis-signed costs or fills better than the market would give, which is the
SIM-fill problem the conduct guardrails forbid.

---

## 3. What a data report must record

Written to `docs/` by the data-integrity agent, and cited by any result built on the data:

- source, vendor, licence, cost, download date;
- symbols, resolution, full span in calendar and trading days, bar count;
- contract continuation and roll rule;
- session and holiday calendar used;
- every check above with its result;
- **known limitations**, stated plainly — especially anything that means the criterion
  cannot be demonstrated on this data.

## 4. Calendars — `data/release_days_0830_2009_2025.csv`

Not market data: the dates of scheduled 08:30 AM Eastern news releases of the Bureau of Labor Statistics (Employment
Situation, CPI, PPI, import/export prices, real earnings, ECI, productivity), one row per date with the releases that
day, from the BLS's own schedule pages (`https://www.bls.gov/schedule/<year>/home.htm`, one per year, 2009-2025). The
full parse (every release, its time and page) is `releases_bls_0830_2009_2025.csv`; the provenance file beside it holds
the fetch time, the URL and the sha256 of every page read. Used by FV3 (T17 item 3): on these dates the AM session's fair
price is the open of the 8:30 ET candle (JJ Simon's pre-news price). `scripts/make_fv3_news.py` writes the dates into
`propedge/outcomes/fv3_core.py` as per-year bitmasks; `tests/test_fv3_kit.py` checks the two agree.

**2026** (D-355, D-358): `release_days_0830_2026.csv`, `releases_bls_0830_2026.csv` and their provenance, from
`scripts/parse_bls_schedule_2026.py` on BLS's 2026 page -- saved by hand from the operator's browser on 2026-10-13 (BLS
refused scripted fetches), retained at `data/raw/bls_schedule_2026/2026.htm` (gitignored, like the 2009-2025 pages; its
sha256 in the provenance), read with the 2009-2025 parser's reader. Used only by FV3-C's confirmation kits (P-06):
`propedge/data/fv3_kit.confirm_preamble` adds `NEWS[2026]` after the embedded cores, so `fv3_core.py` and the
development kits stay byte-identical. Validated: `docs/data_report_bls_release_days_0830_2026_2026-10-13.md`.

### Checks the data-integrity agent runs on a calendar

- **Schema**: `date` ISO, one row per date, sorted, no duplicates; `n_releases` equals the releases listed.
- **Coverage**: every year 2009-2025 present; about sixty release days a year (five monthly series at 08:30 plus the
  quarterly ones), none on a weekend, none on a federal holiday.
- **Provenance**: every year's page named with its hash; the fetch time recorded; the parser named.
- **Look-ahead**: a schedule is known in advance (published the year before), so reading it on the day is not
  look-ahead; a release rescheduled after the fact would be, and the pages read are the archived ones.

---

## 5. The local bar store — `data/bars/<ROOT>/` (D-458)

The operator's licensed Databento 1-minute bars (`GLBX.MDP3`, `ohlcv-1m`, bought as `docs/OPERATOR_SETUP.md`
specifies), one store per root. **Git-ignored**: the vendor's licence is private use, no redistribution, so bars never
reach the remote, a result file or a document (`tests/test_no_raw_bars_in_results.py` refuses a bar series in
`results/`). Written **only** by `scripts/import_bars.py` (`propedge/data/bar_import.py`); read only through
`propedge.data.bars.read_bars`.

`bars.parquet` -- one row per bar of the day's charted contract, sorted by `ts`:

| column | type | notes |
|---|---|---|
| `ts` | int64 | **Bar START**, epoch seconds UTC (a whole minute) |
| `day` | string `YYYY-MM-DD` | trading day, Chicago: a session opens at 17:00 the evening before (the bar's Chicago time plus seven hours, its date) |
| `contract` | string | the charted outright, e.g. `NQU5` |
| `open`, `high`, `low`, `close` | float | **raw** prices on the tick; no back- or ratio-adjustment |
| `volume` | int | the contract's volume in the minute |

- **One contract a day.** Each trading day holds one outright: the one with the most outright volume on the
  **previous** trading day (D-98; the store's first day, its own), chained across purchases. Calendar spreads are
  dropped, and a day's bars are never stitched to another contract's.
- **Raw prices.** Levels jump by the calendar spread across a roll (the manifest's `rolls`). Inside a day the series
  is clean; any cross-day level, indicator or gap statistic must handle the roll days.
- **The windows guard.** Only days inside the market's declared development, spent and confirmation windows
  (`config/windows.yaml`, `propedge/data/windows.py`, D-459) are stored; a day in a reserved window, or outside every
  window, is dropped and counted, **never on disk**. Storing a confirmation window does not open it: `read_bars` calls
  `assert_readable` first, and a read past a window its purpose may read raises before anything is read.
- **Minute bars.** A minute without a trade has no bar; a target and a stop touched in one minute cannot be ordered.

`manifest.json` -- rewritten by every import:

| field | meaning |
|---|---|
| `decision`, `root`, `licence`, `tick` | D-458, the root, the vendor's licence, the tick the prices were checked on |
| `windows`, `stored_statuses` | the windows applied at the import, and the statuses stored |
| `days`, `first_day`, `last_day`, `day_list`, `rows` | the stored trading days and the row count |
| `parquet_sha256` | the parquet's sha256 (the walk caches key on it) |
| `contracts`, `rolls` | the charted contracts, and the days the charted contract changes |
| `leaders` | each **stored** day's outright-volume leader, from which a later import's first day is charted; a dropped day's is never written |
| `short_days` | `{day: bars}` for the days with fewer than `SHORT_DAY_BARS` (1,000) charted bars -- **not** the early-close list |
| `day_bounds` | `{day: [first, last]}`: each day's first and last bar start, Chicago wall-clock `HH:MM` |
| `late_start_days` | the days whose first bar starts after the 17:00 open (a seam between purchases, a vendor outage, an open without trades) |
| `early_end_days` | the days whose last bar starts before 15:00 Chicago, read in session time (exchange early closes, and a day a purchase's edge cut) |
| `imports` | one entry per source file: the zip and its size, the CSV and its sha256 from the zip's own manifest, Databento's query, rows read, spread rows dropped, charted bars and days dropped by window (and the first such day), `condition`, the import time |
| `imports[].condition` | the zip's `condition.json` (Databento's per-date availability): its sha256 and, for the UTC dates inside the stored windows only, the count by condition and `not_available` -- `{date: condition}` for those not `available` (a reserved date is neither counted nor named, D-458 (2)); `null` when the zip has none |

Each import is validated by the **data-integrity** agent before a result uses it; the report is in
`docs/data_reports/` (`data_report_bars_<ROOT>_<date>.md`). A result built on the store cites that report and names
its source (QuantConnect's AlgoSeek bars or these, D-458 (5)).
