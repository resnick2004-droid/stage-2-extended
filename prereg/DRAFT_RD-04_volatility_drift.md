# RD-04: volatility drift -- the whole-window descriptive and a calm-regime replay of P-14 and P-16 (reading VD) -- a described reading, unnumbered (E-023 (1))

**Status: declared before anything of it is built or read.** It is pinned by the sha256 of its LF text in its decision
row. Nothing declared is edited: a change is a new declaration under a new row. It takes no program family number
(E-023 (1)).

**Its text's history.** The first text, drafted as `prereg/DRAFT_RD-04_volatility_drift.md` (TASK_QUEUE Q-123, E-157, E-158;
on wt/wt-scout, master merged at df95e3d), from the scout's note `docs/research/volatility_drift_2026-11-17.md` (Q-120,
merged under E-157): its sections 3.2 (the scorecard's exposure), 4 (a) (the descriptive), 4 (c) (the calm-regime
replay) and 7 (what is unknown). At the pin the file is renamed `prereg/RD-04_volatility_drift.md` and nothing else
changes; the pinning row names the commit and the sha256 it pins. It goes to the red team, then the gatekeeper, before
any pin. Appendix C lists every choice the drafter made where the note, the brief or the rules left the text open.

**What E-023 (1) makes of it, as E-134 (1) rules it.** Neither part is a design, a lever or a filter:

- **(a2)** reads the bars only -- session ranges and the side-free first-exit times of fixed bands -- and no trade,
  side, outcome or design;
- **(c)** replays P-14's and P-16's own registered offers, sides, state table and protocol on a market whose movement in
  points is turned down. It adds or removes no offered trade, chooses nothing, and computes no lift over a coin twin.

So this file is a **described reading**:

- it takes **no program family number** and spends **nothing** of the multiplicity budget (the next numbered family's
  k is unchanged by it);
- **nothing in it can carry, pass or fail**: there is no pass line, no level, no pick and no menu;
- it is declared and pinned before its run, by its own decision row with its sha256, so nothing in it is chosen after a
  look.

**When it was declared, nothing of it had been built, no bar had been read for it, no replay or gate had been run for
it, and no figure of the gate files' `period` or `drift` rows, of Q-121's early-block file (not yet built) or of any
outcome had been read.** Anything chosen after a reading is exploratory and reported apart (section 15).

| field | value |
|---|---|
| reading | VD: volatility drift in points against a contract fixed in dollars -- (a0) the two registered gate files' `period` and `drift` rows; (a2) the bars-only descriptive on the whole development window; (c) a calm-regime replay of P-14 and P-16 |
| id | RD-04 (`prereg/RD-04_volatility_drift.md` at the pin); every result's `prereg_id` is `RD-04` (section 13) |
| kind | a **described reading** (E-023 (1), E-134 (1)): never carried; it describes and decides nothing |
| program family number | **none**; the next numbered family's k is unchanged by this file |
| level, pass line, pick, menu | **none** |
| development data | NQ 1-minute bars, 2020-01-02 to 2026-07-16; (a2) reads them through `extended/reader.py`; (c) has Stage 2's engine read them inside P-14's and P-16's registered builders, authorised by `extended.reader.authorise_engine_read` (section 5) |
| the unit | (a2) the session (the walker's day, 17:00 to 15:10 CT, `atlas_local.day_arrays`); (c) one start day as U1 replays it, and one gate path |
| blocks | (a2): the whole window, reported by calendar year and quarter; (c): all starts the headline, the early block (purged per measure) and the late block from 2024-01-02 beside, start years beside (section 5) |
| cells | (a2): one pass over the window. (c): **2 references (identities) and 8 new cells, every one run** -- 2 designs x 2 scale factors (the year factor, the trailing-range factor) x 2 cost readings (actual, scaled by the factor; Stage 2 D-122) (section 6) |
| beside | (c): the denial ladder and the placement on for every new cell; the ten binding Focused Trader models for the two headline cells, the gap named on the other six; the long-run gate for every new cell; each cell's own per-R edge and bound by the registered rule, never used (section 9) |
| judged-block reads | (a2): one purpose, `volatility_descriptive`, on the line of section 5 item 6. (c): the purpose `registered_design` (E-037) under the pinning row, which names P-14 and P-16 -- never under this file's line. The identity under `identity` from `identity/vd_identity.py` and its own row |
| seeds | from 20262310 to 20262319: three in use, seven reserved; P-14's and P-16's gate seeds, P-16's coin seed, the registered era seed, Q-17's ladder start seeds and U1's replay seeds inherited (section 11) |
| confirmation | none: nothing is carried (section 10) |
| `confirmation_tests_on_this_market` | 3: NQ's three of Stage 2 D-107's three are spent (P-05, P-06, P-10; `vendor/stage2/config/windows.yaml`, `held_back_2025`); this reading adds none and reads no NQ from 2026-07-17 |

---

## 0. What each part changes, stated truly

### 0.1 (a2) changes nothing

It is a property of the bars: per session, how far NQ moved in points and in percent, and how long a band of fixed
points (or of a fixed share of the trailing range) took to be left, both sides pooled. No sign, no target-against-stop
split, no win share, no trade of any design.

### 0.2 (c) changes only the market's amplitude in points

Per session d, every bar's open, high, low and close is drawn toward the session's first open O_d by a factor k at most
one and put back on the tick grid (section 4.1). **What stays fixed:**

- the brackets in points (P-14's 12.5- and 25-point rungs, P-16's 150-tick stop) and every R the state table offers;
- the whole micros at each state's fixed dollar risk, so every trade risks the same dollars;
- the contract's dollar limits: the Combine's $3,000 target (`combine_profit_target`, 8284208), its $2,000 trailing loss
  limit (`combine_mll`, 8284204), the funded account's -$2,000 floor (`xfa_mll_start`, 8284204), the $150 winning day
  (`xfa_std_winning_day_min`, 8284233);
- the offers: P-14's event minutes and sides, P-16's admitted marks and coin sides, the day kinds, the report-day cuts;
- the frozen choices: P-14's rung by hour, P-16's admitted marks, the state table, the verdict arm's per-R shift, the
  day capacity (section 4.4);
- the protocol: seats, purchase budget, routing under the strict one-position rule, payout rule, fees, conduct model.

**What changes:** every offer's walked outcome -- its kind (target, stop, breakeven, flatten), exit bar, MAE and gross
ticks. From that, everything downstream changes and is rebuilt: which offers the router takes, when each account
resolves, the gate's paths and every start's journey.

This is the operator's counterfactual (E-155): **today's market moving as little in points as the calm reference years,
with the contract unchanged.** It is not a replay of 2020-2021: volume, spreads, the intraday clock, news and market
structure stay as they were (pitfall 5, section 4.5).

## 1. What this reading is, and what it is not

**Its job.**

- **(a2)** answers the factual question the record leaves open (the note's section 7): NQ's session range in points and
  in percent by year and quarter over 2020-2026, and the resolution time of fixed brackets by year -- whether the rise
  is price level or percent volatility.
- **(a0)** puts beside it what Stage 2's registered gate files already hold: P-14's and P-16's trades per day by era and
  their trade counts by year.
- **(c)** shows how much of P-14's and P-16's journey scorecard, gate and supply is points volatility: the same designs,
  the same contract, a calmer market.

**What it is not.** A test, a claim of an edge, a candidate, a registered design, a correction applied to any other
reading, or a choice of any parameter. It carries nothing; no rule changes because of it.

**Why described rather than tested** (E-023 (1)). There is nothing to judge: (a2) has no outcome, and (c) is a
counterfactual of designs already judged in Stage 2 (E-037's reasoning). Its value is the description.

**The leak, stated first (section 9.3).** (a2) and (c) read the judged block's volatility and the registered designs'
supply in it. A figure from them could steer a later declaration -- for example toward a stop that resolves in
2024-2026. **Every later declaration states that it was written after this reading's run, and none cites a figure of
it as the reason for a parameter.**

## 2. Prior exposure: what has already read this, on which data

| read | what it read | data | what it recorded | bearing here |
|---|---|---|---|---|
| Stage 2 D-106, D-121 (2), D-122 (1) | development prices rescaled to the era; the remedy corrected | ES 2009-2014 | "No era-matching method removes it [the one-tick bounce relative to the stop] ...; it is bounded by reporting actual and rescaled prices side by side" | the cost readings of (c) (pitfall 1) |
| Stage 2 D-225, D-226 | NQ rescaled to today's price level | 2009-2019 | an exploratory proxy, never a result | rescaling's standing: a counterfactual, labelled |
| Stage 2 D-238, D-239 (`results/regime_then_now.csv`, **not vendored**) | the regime map: fixed stops in points and range-scaled stops, per market, decision, stop and R, by era; beside resolution, "per window and year, volume and range" and "the session range" | QuantConnect's AlgoSeek bars, 2009-06-01 to 2025-06-30 | in words only here: range-scaled brackets era-stable, fixed-point ones not; NQ moved "several times further a day in 2020-2025" | **D-238 measured range by window and year over 2020 to June 2025 on other bars; the file is not in the snapshot and its values were never read here.** (a2) is the first such reading on this repository's Databento bars and to 2026-07-16 |
| Stage 2 D-240 | range stops dropped from the no-edge campaign | 2020-2025 | "their dollars per trade move with the trailing range, which D-212 forbids" | why (c) keeps the brackets in points and scales the market instead |
| Stage 2 D-212, D-308 | the resolution floor: at most 5 % flattened overall and in each year | -- | a rule | (c)'s per-year resolution reading; a failure there is a finding (pitfall 4) |
| Stage 2 D-271, D-420, D-437 | the era rule on mean gross R; the per-era report beside | 2020-2022 against 2023 to 2026-07-16 | eras flagged for P-13; the lower era's bounds read | the verdict arm's shift that (c) holds fixed (4.4) |
| Stage 2 D-292 | range per half-hour window | 2020 to June 2025 | time of day, in words | not by year |
| Stage 2 D-300 to D-307 | ATR-scaled stops, then fixed points with exact dollars | 2013-2026 | ATR stops broke the dollar sizing | why (c) scales the market, not the bracket |
| Stage 2 D-554 | P-16's stop chosen on 2020-2023 alone and on 2024-2026 alone | both spans | the 50-point stop fails resolution early and resolves late | **knowledge of resolution drift across the blocks already on record** (9.3) |
| Stage 2 D-578, D-580, D-581, D-582, D-604, D-605 | the span guard; S1's momentum sides; S2's volatility thirds; P-16's money "from supply"; the money by year in words | both blocks | supply depends on the regime; 2020-2021 the weakest years for growth, in words | the direction (c) is expected to show is partly on record |
| This repository: E-024, E-030, the red team's M2-4 on F-B (`docs/reviews/DRAFT_F-B_multifeature_v2_2026-11-16.md`) | pooled and worst-year resolution shares from Stage 2's files | both blocks | far apart; the 37.5-point stop dropped from F-B | prior knowledge of the drift's effect on resolution (9.3) |
| U1 (Stage 2 D-620), Q-05 (E-010), program U's nine families | P-14's and P-16's journeys, every start; P on the late block | both blocks | the reference rows; all nine families closed | the late block has been read for P many times: late development, not out of sample |
| Q-121 (E-157), queued, not built at this text | (a1): the same descriptive on the choice block only | 2020-01-02 to 2023-12-29 | nothing yet | L_ref's source (4.2) and (a2)'s identity (8.2) |

**The gate files' `period` and `drift` rows** (`vendor/stage2/results/a3_brk30_cb20_gate.csv`,
`vendor/stage2/results/rc_s150_all_gate.csv`) are Stage 2's registered designs' own rows, already judged in Stage 2.
Only their section and column names are on record here (the note's section 2, end); **no value of them has been read in
this repository**, and none is read before step 2 of this reading's run (section 13). The pinning row records that.

**The drafter's own reads (disclosed).** The scout's note (whole); the briefs Q-121 and Q-123; `DECISIONS.md` E-007,
E-008, E-021, E-023, E-025, E-026, E-037, E-053, E-104, E-117, E-125, E-134, E-146, E-152, E-155, E-156, E-157 and E-158
(the first draft read E-157 from the lead's working copy before it was committed); Stage 2's rows D-106, D-121, D-122, D-212,
D-238, D-239, D-240, D-308, D-554; `prereg/RD-03_contract_levers.md` (whole, for form); `vendor/stage2/prereg/P-14_a3-brk30-cb20.md`
lines 180-240 and `P-16_rc-s150-all-nr.md` lines 150-200; code only: `extended/reader.py` (whole),
`vendor/stage2/scripts/atlas_a3.py` (header, lines 140-260, `bounds`), `rc_screen.build`, `rc_width_screen.build` and
`cutoff_reading`, `rc150_dev_test.build_cells`, `rc_dev_test.trades_hash` and `build_cells`,
`user_journey._rc_campaign` and `build_p16`'s header, `a3_brk30_cb20.py` lines 280-330 and 423-445,
`customer_slices.arm_blocks`, the gate's column names in `extended/gate.py`, `extended.user_measures.cvar`'s line, `atlas_local`'s header and
`day_arrays`, the headers of `extended/replay_records.py`, `identity/user_beside_identity.py` and
`identity/gate_identity.py`, the function names of `extended/user_beside.py`, `extended/gate.py` and
`extended/pp_reading.py`. **No result file of either repository was opened**; the vendored results folder was not
listed. The seed search of section 11.

**What is already known of the direction (disclosed).** NQ's movement in points rose from 2009-2019 to 2020-2025
(D-239); a wider fixed stop resolved late and not early (D-554); P-16's money is supply (D-582); 2020 and 2021 were the
weakest years for growth (D-605, in words). Nothing is known of (c)'s quantities: no replay at a reduced amplitude has
been run in either repository.

## 3. (a0) and (a2): the descriptive

### 3.1 (a0): the gate files' existing rows, read as they stand

From each of `vendor/stage2/results/a3_brk30_cb20_gate.csv` (P-14) and `vendor/stage2/results/rc_s150_all_gate.csv`
(P-16), each checked first against `vendor/MANIFEST_stage2.sha256` (refusing):

- section `period`: every row (periods `2020-2022`, `2023-2026`, `all`, `check`), every column, as text;
- section `drift`: every row (years `2020` to `2026`), every column, as text.

Copied into `results/vd_descriptive.csv` section `a0` with the source file and its sha256. Nothing is computed from them
and nothing else of either file is read.

### 3.2 (a2): the bars-only descriptive on the whole window

**The code is Q-121's**, imported, never copied: the per-session computation and the summaries of
`extended/vol_descriptive.py` (Q-121's build, E-157), run on every development session from 2020-01-02 to 2026-07-16.
Per session:

- the high-low range **in points** and **in percent of the session's first open**, and the trailing 20-session mean of
  each (prior sessions only; undefined for the window's first 20 sessions, which are left out of every median that uses
  them, and counted);
- at P-16's five-minute marks and at P-14's slots, the side-free first-exit time of a band of 12.5, 25 and 37.5 points
  around the entry, at every R the tables offer, both sides pooled, as Stage 2's `mark_resolution` reads "kind columns
  only" (`vendor/stage2/propedge/research/resolved_coin.py:241`), and the share still open at 15:08;
- the same at bands of 0.10 and 0.25 of the trailing range (D-238's scale-free reading).

**Reported** by calendar year and by quarter: median, p10 and p90 of every quantity, with the session counts. 2026 is a
part year (to 2026-07-16), labelled.

**And the factors for (c)** (section 4.2), computed from (a2)'s own session rows: L_ref, each year's L_y and k_y, and
the trailing factor's distribution by year (its p10, p50, p90 and the count of sessions left unscaled), in section
`factor`.

**If Q-121's per-session functions refuse a judged-block date inside themselves** (its brief asks for a hard refusal of
any bar from 2024-01-02), so that (a2) cannot call them on the whole window without editing them, the build stops and
reports: (a2) does not copy them, and the lead decides (section 14 item 2).

## 4. (c): the calm-regime replay

### 4.1 The map

For each session d (the walker's day, 17:00 to 15:10 CT, as `atlas_local.day_arrays` builds it) and its factor k_d in
(0, 1]:

- O_d is the session's first open: the open of the first bar present in the day's arrays;
- each of a bar's open, high, low and close p (not missing) maps to

  `p' = O_d + 0.25 x round(k_d x (p - O_d) / 0.25)`,

  `round` being numpy's round half to even, 0.25 points the MNQ and NQ tick (`vendor/stage2/config/instruments.yaml`
  lines 73-78); a missing bar stays missing.

Since O_d and p lie on the tick grid and rounding to the nearest is non-decreasing, the map keeps every bar's order: the
high stays the highest, the low the lowest, and no bar's range grows. At k_d = 1 it returns p exactly (an exact
multiple of the tick divided by the tick is an exact integer in binary floating point), so the identity of section 8.1
is bit for bit.

Prices relative to any entry inside the session scale by the same factor: p' - e' = k_d x (p - e), up to rounding of
half a tick at each. **So a bracket of fixed points, entered anywhere in the session, faces moves k_d times as large.**

### 4.2 The factors

- **The trailing range.** For each session, the trailing 20-session mean of the session range in points (prior
  sessions only) -- (a2)'s session column, the same column as Q-121's file.
- **L_ref, the calm reference:** the median of that column over the sessions dated 2020-01-02 to 2021-12-31 (both in
  the choice block; the operator's calm years, E-155), the window's first 20 sessions left out (no trailing mean).
  **Read from Q-121's early-block file**: `results/vol_descriptive.csv`, section `session`, columns `date` and
  `range_pts_trail20`, the file checked against its sidecar manifest and its decision row (section 13, waits). (a2)'s
  session rows to 2023-12-29 must equal that file's (8.2), so the same median from (a2)'s rows is checked equal, refusing.
  *The file name, the section and the column names are Q-121's to fix; this text names them by their roles, and the
  pin-time text writes Q-121's actual names (section 14 item 2).*
- **The year factor (the headline):** for each calendar year y, L_y is the median of the trailing column over y's
  sessions (2026's to 2026-07-16), and

  `k_y = min(1, L_ref / L_y)`,

  one constant for every session of the year. A year whose L_y is at or below L_ref is left unscaled (k_y = 1).
- **The trailing factor (beside):** for each session d, `k_d = min(1, L_ref / L_d)`, L_d being d's own trailing mean
  (prior sessions only: known before d opens). A session with no trailing mean (the window's first 20) is left unscaled
  (k_d = 1), counted.

Only compressions: every factor is at most one, so (c) turns volatility down and never up. **The day's own range is
never used** (pitfall 2).

### 4.3 The two cost readings (Stage 2 D-122 (1))

Compressing the path by k at the actual tick costs is the same as the real path with the brackets and the tick costs
both divided by k: costs per unit of movement rise by 1/k. That is realistic for a calm market but cannot be removed
(D-122 (1)), so it is bounded by two readings side by side:

- **`act` -- actual costs:** every per-trade cost as the registered builders charge it: the entry tick, the tick on a
  stop or breakeven exit, the two ticks on the flatten, the round-turn fee at the contracts held (P-14's and P-16's
  §3, FV3-C's `Signals3.outcome`, `atlas_a3.fee_by_stop`, D-324). **The headline.**
- **`sc` -- costs scaled by the factor:** each of those per-trade costs multiplied by the session's k (fractional ticks
  allowed), so the cost per unit of movement is today's. The account fees (subscriptions, activations) are not trade
  costs and are not scaled. **Beside.**

The tick grid of the prices is kept in both (it is the market's); its bounce relative to the stop is the part neither
reading removes, labelled on every row of (c).

### 4.4 What is frozen, never recomputed on the rescaled bars

Each from the registered build on the actual bars (the k = 1 build of section 8.1, which must equal the registered):

| frozen | value | why |
|---|---|---|
| P-14's offers | A1's event minutes and sides on the 'n' and 'b' days, a 'b' day's events before the 07:30 CT cut dropped (`atlas_a3.pool_minutes`, A1's cache read only) | the entries are the design's; pitfall 3 |
| P-14's rung by hour | the 25-point rung from 17:00 to the 12:00 hour, the 12.5-point rung at 13:00 and 14:00, and the R offered at each, from `results/a3_resolution_map.csv` as pinned in P-14's config (P-14 §3) | pitfall 4 |
| P-16's offers | the five-minute marks the cutoff admits at the 150-tick stop on the actual bars (`resolved_coin.mark_resolution`, kind columns only, at most 5 % unresolved over the window at every offered R), the report-day cuts, D-533's release-minute removal, the coin sides at seed 20261102 | pitfall 4; P-16 §3 |
| the state table | `state_dp_e-0.050_lamstar_noclose`, checked against `a3_brk30_cb20.NOCLOSE_POLICIES_SHA256` | the designs' sizing |
| the verdict arm's shift | each R's `lb - e` from the k = 1 build (`atlas_a3.bounds`, the era rule at its registered seed), applied to the rescaled blocks by `customer_slices.arm_blocks` and the gate's `shifted_blocks` | the registered pessimism held fixed, only the amplitude moved |
| the day capacity | each design's busiest day's offers (D-469) | the offers are unchanged, so it is unchanged (asserted, 8.3) |

**The rescaled walk's own readings are printed beside, never used:** how many of P-16's frozen marks, and of P-14's
frozen hour-rung pairs, would fail the 5 % cutoff on the rescaled walk; and each R's e and bound recomputed on the
cell's own trades by the registered rule (`atlas_a3.bounds`, the registered era seed), section `bounds_beside`.

### 4.5 The pitfalls (the note's 4 (c)), each answered here

1. **The tick grid does not shrink** (D-122 (1)). Answered by the two cost readings side by side (4.3); the grid's
   bounce is named on every row as not removed.
2. **One factor per year, not the day's own range.** Rescaling each day by its own range would erase clustering and
   news days and would use the day's future range. The headline is the year factor; the trailing factor (prior
   sessions only) is the causal alternative beside; the day's own range enters no factor.
3. **Drift is scaled too.** Net moves shrink by k, so drift relative to volatility is kept. The entries do not move:
   P-14's events and P-16's marks are taken from the registered build on the actual bars (4.4), never re-detected on
   the rescaled bars. (An affine map about the open preserves a break of the 30-minute bar up to ties made by the
   rounding, so re-detection would differ only there; it is not done.)
4. **Frozen choices stay frozen.** P-14's rung by hour and P-16's admitted marks are kept (4.4). The replay's
   unresolved shares are reported by year and R against D-212's 5 % (D-308), and **a D-212 failure there is a
   finding, recorded and read, never a trigger to rerun, re-freeze or drop a cell.**
5. **Only amplitude changes.** Volume, spreads, the intraday clock and market structure stay as they were. Every row of
   (c) is labelled **"today's market with its points volatility turned down, not a replay of 2020-2021"**.
6. **Session gaps are not rescaled.** Every session is anchored at its own first open; every position is flat by 15:10
   CT, so none crosses a gap. No input of either design crosses sessions on the rescaled bars: P-14's events and
   P-16's marks are frozen, and the trailing factor is computed on the actual bars.
7. **Nothing is written to the data junction.** The rescaled arrays and walks live in memory in the clean run;
   `atlas_a3.cached_walk` is never called with `write=True` on rescaled arrays, A1's and A3's caches are read only, and a
   test holds that no file under `vendor/stage2/data` is written or touched (T-5).
8. **It changes the trade sequence.** Fewer trades resolve, exits come later, more trades flatten, and the router takes
   a different set of offers. So the gate and U1 are rerun for every cell, from the rescaled trades; nothing of the
   registered runs is reused except the frozen inputs of 4.4.

**Two more, the drafter's.**

9. **The early years may be unchanged.** Under the year factor a year at or below the reference is left as it was, so
   many early-block starts can be identical to the reference. Such starts are printed as "identical", and every paired
   reading prints its share of starts differing at all (9.1 item 5).
10. **The rounding can create ties.** Two distinct prices can round to the same tick, so a minute can reach a target
    and a stop together more or less often than before; the local walk gives every such minute to the stop (the
    cautious side, `atlas_local`'s header). Counted per cell (8.3).

### 4.6 How it is built without touching `vendor/`

- **The seam.** `atlas_a3.walk_minutes` takes the day's arrays through a callable, `arrays: Callable[[str], tuple]`
  (`vendor/stage2/scripts/atlas_a3.py:160-170`). The adapter wraps the callable the vendored `atlas_a3.bar_arrays`
  returns, applying 4.1's map with the session's factor, and nothing else.
- **The builders that call it internally.** P-16's `rc_width_screen.build` and P-14's builder (as
  `identity/gate_identity.py` makes P-14's call: `rc_screen.inputs()`, A3-BRK30's cell trades) call `bar_arrays` or
  read A3's cache themselves, and P-16's recomputes its cutoff from its own walk. So the adapter **re-composes** each
  builder in Q-71's pattern (`extended/campaign.py`): the vendored function's text copied verbatim under a guard that
  refuses unless its LF source hashes to its pin, a proof that the copy with its marked lines removed parses to the
  vendored function statement for statement, and **marked additions only**: (a) the wrapped arrays; (b) the frozen
  offers, rungs and shift of 4.4 passed in from the k = 1 build; (c) the scaled costs of 4.3; (d) no cache write.
- **Never** a substituted vendored attribute during a call (E-011, Q-47), never an edit of `vendor/`, and **no file a
  shared identity covers is edited** (E-104, E-117): the adapter is new modules only (12.1). **If any piece cannot be
  built that way -- a builder that cannot be re-composed, a cost that cannot be scaled through arguments or a
  re-composed copy, a shared file that would need an edit -- the build stops and reports; this declaration does not
  fall back.**
- Downstream, the rescaled trades go through this repository's adapters unchanged: the gate through
  `extended/gate.py` (Q-47, held by Q-80, E-049) and the replay through `extended.user_beside.run_starts` (Q-17), with
  Q-94's recorder (`extended/replay_records.py`).

## 5. Data, blocks, the unit and the horizons

1. **(a2)'s unit** is the session; its summaries by calendar year and quarter, whole window.
2. **(c)'s unit** is U1's: one development start day, a fresh (unbound) bankroll and fresh accounts, the cell's trades
   replayed in historical order, a long replay of up to 252 sessions plus U1's exact-length runs (21, 63, 90, 126)
   (`vendor/stage2/scripts/user_journey.py`, `customer_slices.replay`), through Q-17's adapter. `USER_MILESTONES.md`'s
   definitions unchanged; a month is 21 sessions. **The starts:** every start U1 reads for `p14` and `p16`
   (`vendor/stage2/results/user_journey.csv`, section `start`), each reading on the starts with its horizon h left.
   And the gate's 500 paths over 504 sessions at each design's registered seed.
3. **The arms.** `verdict` (every R shifted by 4.4's frozen `lb - e`) the headline; `point` beside.
4. **Pairing.** Each new cell and its design's `k1` reference on the same start days and the same arm; in the gate, on
   the same seed and so the same resampled day indices (the rescaled day set has the same days).
5. **The blocks, per measure** (RD-03 section 5 item 4, carried): **all starts** with h sessions left
   (`u_select.block(records, None, h)`), the headline; **the early block** (`u_select.block(records, "early", h)`); **the
   late block** (`u_select.block(records, "late", h)`, from 2024-01-02); by start year, means only, not purged,
   labelled. Each measure at its horizon h as RD-03's section 5 table fixes it (`u_select.MEASURES`; P and the shares
   ahead at months 1-3 at 63; S1, S3b and the month-6 net at 126; the month-12 net and S4b at 252). **The factor of a
   start's later sessions is their own year's**, so an early start's journey can run into a scaled year; no purge
   removes that, and it is labelled.
6. **The judged block's seal (E-026, E-041, E-037).**

   - **Judged-block reads:** `volatility_descriptive`

   - `volatility_descriptive`: (a2)'s read of the bars from 2020-01-02 to 2026-07-16 through `extended.reader.read_bars`,
     from a clean checkout of a committed commit, once (a further run only with `repeat=` under a row naming this
     file). It is not a choosing or fitting purpose (the reader's `CHOICE_WORDS`, `extended/reader.py:125`).
   - **(c) is not on that line.** Its engine reads are authorised by `extended.reader.authorise_engine_read` under the
     purpose `registered_design` (E-037), `design=["P-14", "P-16"]`, the declaration **the pinning row**, which names
     both designs (`extended.reader.names_design`), from `scripts/vd_replay.py`, inside a clean run, ledgered. The
     reader does not limit `registered_design` to one run, so **the replay's script enforces its own once rule, per
     part**: it runs one part a run, `--part scorecard` (step 3) or `--part beside` (step 4), the part written into the
     ledger line's description, and refuses to start if `results/read_ledger.jsonl` holds a `registered_design` line
     from `scripts/vd_replay.py` under the same row for the same part by another run id, unless `--repeat E-NNN` names
     a row that names this file (T-12).
   - **The identity** runs from `identity/vd_identity.py` under the purpose `identity` and its own row, never under
     either of the above.
   - (a0) reads two vendored result files, not bars: no purpose; the step and its file hashes are recorded in the
     result's manifest.
7. **No NQ from 2026-07-17** is on disk or read.

## 6. The cells and the runs

### 6.1 (a2)

One pass over every development session (one bar read under `volatility_descriptive`), after its early-block identity
(8.2). No cell, no variant.

### 6.2 (c)'s grid

| cell | factor | costs | on P-14 | on P-16 |
|---|---|---|---|---|
| `k1` | 1 for every session | actual | reference (identity) | reference (identity) |
| `yr_act` | the year factor k_y | actual | new, **the headline** | new, **the headline** |
| `yr_sc` | the year factor k_y | scaled by k_y | new | new |
| `tr_act` | the trailing factor k_d | actual | new | new |
| `tr_sc` | the trailing factor k_d | scaled by k_d | new | new |

Each new cell: its walk (one rescaled walk per design and factor, shared by its two cost readings -- **four rescaled
walks**), its trades, U1's replay on both arms over every start with the exact-length runs, and its gate (500 paths,
point and bound, with its zero-edge twin). **Every cell runs.**

### 6.3 The comparisons read (all paired, none a pick)

- each new cell against its design's `k1`: the headline `yr_act`; beside `yr_sc`, `tr_act`, `tr_sc`;
- `yr_sc` against `yr_act` and `tr_sc` against `tr_act`: the cost reading alone;
- `tr_act` against `yr_act`: the factor alone.

### 6.4 Counting

1. **No program family number and no level** (E-023 (1)).
2. **(a2):** one descriptive pass; **(a0):** two files' rows.
3. **(c) at 0 % with the placement off, both arms, every one run:** 2 references (identities) + 8 new cells = **10
   replays on two arms; 8 new cells**; **8 gates** for the new cells (the references' gates are 8.1's identities).
4. **Beside, verdict arm:** the denial ladder (`denial_10`, `denial_25`, `denial_50`) and the placement on (`rtp`) for
   every new cell: 4 x 8 = **32 replays**; the ten binding Focused Trader models (`extended.user_beside.FTP_BINDING`)
   for the two headline cells: 10 x 2 = **20 replays**, not read for the other six cells (60 replays not run, the gap
   named, Appendix C item 9); `k1`'s fourteen responses on each design checked against Q-44's per-start file: **28
   reference checks**.
5. **Every block read** is recorded as read for volatility description (10, the binding).
6. **Nothing is selected.**

**In all:** one descriptive pass; two files' rows; 10 replays on two arms (2 references, 8 new cells); 8 gates; 52
replays beside (32 ladder and placement, 20 Focused Trader) and 28 reference checks; four rescaled walks; the honesty
series synthetic.

## 7. Parameters: fixed, beside, dropped

"Beside" means every value listed is run and read and none is chosen; there is no menu. **Searched: none.**

| parameter | what it is | class | value | source or reason |
|---|---|---|---|---|
| designs | what is replayed | fixed | P-14 and P-16 as registered | E-037; E-157 (c) |
| the map | how a price is drawn toward the open | fixed | `O_d + 0.25 x round(k x (p - O_d) / 0.25)`, half to even | 4.1; the note's 4 (c) |
| the anchor | the price each session is scaled about | fixed | the session's first open | the note's 4 (c); pitfall 6 |
| the trailing window | sessions in the trailing mean range | fixed | 20, prior sessions only | the note's 4 (a), (c); Stage 2 D-238's 20 sessions |
| the reference years | the calm reference for L_ref | fixed | 2020-01-02 to 2021-12-31 | the operator's (E-155); the note's 4 (c); both in the choice block |
| the reference statistic | how L_ref and L_y summarise | fixed | the median of the trailing mean | the note's 4 (c) |
| **the factor** | one per year, or one per session | **beside** | `yr` (the year's, the headline), `tr` (the session's trailing, beside) | pitfall 2 |
| **the cost reading** | trade costs as charged, or scaled | **beside** | `act` (the headline), `sc` | D-122 (1); pitfall 1 |
| the cap on k | no amplification | fixed | k at most 1 | the question is a calmer market (E-155) |
| unscaled sessions | no trailing mean | fixed | k = 1, counted | 4.2 |
| frozen inputs | offers, rungs, marks, table, shift, capacity | fixed | the k = 1 build's | 4.4 |
| arms | outcome shift | fixed | `verdict` the headline, `point` beside | CHARTER section 2 |
| denial, placement | firm discretion | fixed | 0 % and the placement off in the headline; the ladder and `rtp` beside | E-008; Stage 2 D-234, D-289 |
| Focused Trader models | beside | fixed | Q-17's ten, on the two headline cells | E-007 (e); Appendix C item 9 |
| horizons, blocks | replay length; starts read | fixed | U1's; RD-03's section 5 table; all, early, late | Stage 2 D-620 |
| the interval | uncertainty on paired readings | fixed | 9.2 | RD-02 section 9.2; E-058 (5) |

**Dropped, and why.**

- A second reference (the choice block's median, the note's "possibly"): one reference, the operator's years; a second
  doubles the heavy cells for a variant the operator did not ask for -- a later reading may add it, citing this one.
- Amplification (k above one, a busier market): not the question.
- Rescaling by the day's own range: pitfall 2.
- Re-detecting events or re-admitting marks on the rescaled bars: pitfalls 3 and 4.
- A range-scaled design: it needs a classification row first (E-157; the note's section 5), and it is a design, not a
  replay.
- P-15: not asked (E-157 names P-14 and P-16).

## 8. Before any reading: identities, oracles, mechanics

### 8.1 (c)'s identity, refusing (E-004, E-010; whole-window identities only from `identity/*.py`, E-026, E-041)

**Shared, owed by other items; this reading waits for each.** A wait is met only by a decision row whose third cell
begins with the positional token of E-104's form (`identity-holds: <id> @ <sha>`, parsed by
`extended/identity_tokens.py`), at the run's commit or an ancestor, with the identity's cover unchanged since
(`extended/identity_cover.py`'s `cover(id)`, never less):

- Q-05 (E-010): U1's start rows reproduced (`identity/stage2_identity.py`);
- Q-80 (E-049): `extended/gate.py` through the re-composed campaign, P-14's and P-16's registered gate paths at 500
  paths;
- Q-93 with Q-100 (E-059 (1)): U1's start rows through Q-17's adapter;
- Q-101 (E-068): U1's start rows with the replay recorder on.

**This reading's own, run first from `identity/vd_identity.py` (label `vd_identity`)**, from a clean checkout of the
reading's commit, under the purpose `identity` and the row that registers it (the lead's). **The script runs the
reference only:** the factor is the constant 1 for every session and the cost reading the constant `act`; no argument
selects a factor, a cost reading or a cell; before its first session it asserts both and refuses otherwise (T-11). It
must reproduce, through this reading's path (12.1 A-1 to A-3) at k = 1:

1. **The wrapper is the identity:** on every development session the wrapped callable's four arrays equal the vendored
   `atlas_a3.bar_arrays` callable's, bit for bit, missing positions included.
2. **P-14's walk and trades:** the walk built through A-2 equals the vendored A3 cache's rows
   (`vendor/stage2/data/atlas/A3/walks.parquet`) at every minute it walks, row for row, every column, exactly, and walks
   every minute P-14's trades are drawn from; the trades equal those the
   registered builder makes in the same process, every column, exactly; each R's e and bound equal the registered
   builder's.
3. **P-16's trades and marks:** the trades' content hash (`rc_dev_test.trades_hash`) equals
   `rc150_dev_test.TRADES_SHA256`; P-16's identity (b) holds as P-16 §3 states it (`rc_dev_test.trade_problems` with
   `rc150_dev_test.SPEC`); the admitted marks equal those the vendored `rc_width_screen.build` admits at 150 ticks in
   the same process.
4. **The gates:** P-14's registered gate paths, `vendor/stage2/results/a3_brk30_cb20_gate_paths.csv`, `gate` run, 0 %
   denial, point and bound, through `extended/gate.py`, every `zero_edge_decomposition.PATH_COLS` column to 1e-6, all
   500 paths, at seed 20261131; **and P-16's**, `vendor/stage2/results/rc_s150_all_gate_paths.csv`, at seed 20261206.
5. **U1's start rows for P-14 and P-16**, through `extended.user_beside.run_starts` with the response `off` and the
   recorder on: `vendor/stage2/results/user_journey.csv` section `start`, configs `p14` and `p16`, both arms, every
   start, every column as E-010 compared them (money and the ratio to 1e-6; counts, days, dates and text exactly), with
   U1's own checks of every run's payouts and fees against the engine's totals.
6. **The scaled-cost path at k = 1:** P-14's and P-16's trades built with `sc` at k = 1 equal those built with `act`,
   bit for bit (trades only, no campaign).

**Its cover, declared under Q-111's rule** (`extended/identity_cover.py`, E-119): `BASE` -- `extended/__init__.py`, the
folder `config/` whole (E-117), `vendor/MANIFEST_stage2.sha256` and `vendor/DATA_MANIFEST_stage2.sha256` -- plus
`identity/vd_identity.py` and every repository file it imports, directly or transitively, as
`identity_cover.imports(script)` computes it. A change to any covered file after its token re-requires it.

**Inside (c)'s own run (no further read):** `k1`'s start rows equal U1's again (item 5's comparison, refusing), before
any new cell is read.

**A failure of `vd_identity` stops (c)**: nothing of a new cell is computed, written or printed; the failure protocol
applies; nothing is rerun until it passes, and a rerun is a further read under `--repeat` (13). (a2) does not depend on
it. E-010's negative controls (the verdict rows against the point rows; a 2e-6 nudge) show that the comparisons are not
vacuous.

### 8.2 (a2)'s identity, refusing, before the judged block is read

Inside step 2 (section 13), **before the read under `volatility_descriptive` is authorised**: (a2)'s code run on the
choice block alone (2020-01-02 to 2023-12-29, a read that needs no purpose) reproduces Q-121's file -- every row of
every section whose sessions, years or quarters lie in the choice block, every column, as text at the file's precision.
Then the whole-window run; and its rows to 2023-12-29 equal the choice-block run's again (the trailing means do not look
ahead), refusing. **A failure stops (a2) before any judged-block bar is read, and so stops (c)** (whose factors come
from (a2)'s rows).

### 8.3 Oracles (an output outside them is an engine or adapter error, never a finding; each stops its step)

- **The map:** on every rescaled session and bar, low <= min(open, close) <= max(open, close) <= high; every price on the
  0.25 grid; |p' - O_d| <= |p - O_d|; the session's rescaled range within one tick of k times its range; missing bars
  in the same positions; every factor in (0, 1].
- **The frozen inputs:** every new cell's offers -- (date, slot or mark, side, stop in ticks) -- equal its design's
  `k1` offers, one for one; the day capacity equal; the per-R shift equal to `k1`'s; the state table's hash the
  registered.
- **The factors:** section `factor`'s L_ref equals the median recomputed from Q-121's file, and every k_y and k_d
  recomputed in step 3 from (a2)'s session rows equals the file's.
- **The gate's zero-edge twin:** the mean gross payouts per funded account do not exceed $2,000 beyond its Monte Carlo
  interval; the pass rate per evaluation does not exceed 2/5 beyond its interval (propsim D-02).
- Every payout request at most min(50 % of the balance, $2,000) and at least $125, paid at 90 % less the method's fee
  (`payout_max_frac_of_balance`, `xfa_std_cap`, `payout_min`, `profit_split`, Stage 2's verified ledger).
- **No write under `vendor/stage2/data`** during the run: the data folder's file list, sizes and modification times
  equal before and after each step.

### 8.4 The mechanics, printed first

For each new cell beside its `k1`, before any scorecard measure. They describe where the amplitude binds; each names its
source (the walk's kind columns; Q-94's recorder; the gate's rows):

- **resolution (D-212):** per year and offered R, the share of offers unresolved at 15:08 (both sides pooled, kind
  columns only), against D-212's 5 % (D-308), each failing year and R flagged **"fails D-212 here: a finding"**; for
  P-14 also by hour and rung, as the rung map reads it; the count of frozen marks and hour-rung pairs that would fail
  the cutoff on the rescaled walk (4.4);
- **supply:** per year, the trades the router takes per session (median, p10, p90), the share of sessions at the
  router's five, the median minutes from entry to exit of taken trades, the share of taken trades flattened, the
  minutes reaching a target and a stop together (pitfall 10);
- **the gate's pooled columns:** trades per day, `share_trades_skipped_busy`, `share_trades_at_tier_cap`;
- **the journey's counts:** evaluations bought, passes, funded accounts activated and lost, payouts, by start year;
- **not read, named:** how often the Combine's consistency cap and the 45-tick stand-aside bind by year -- no record
  this reading's path carries holds them (the note's section 7 asks; a later reading with a counters channel can).

A cell identical to its `k1` on every start (every factor 1) is reported as **"no change at this amplitude"**.

## 9. The reading (CHARTER sections 2-3; E-008, E-014, E-023, E-134 (2))

### 9.1 What is read

**(a0) and (a2):** the rows of sections 3.1 and 3.2, by year and quarter, as described quantities. No interval, no
test, no trend fitted.

**(c):** every cell and its `k1`, both arms (the verdict arm the headline), every block of section 5:

1. **The scorecard.** P, S1 to S5c, S2, S3d, S6 and Q, as `USER_MILESTONES.md` defines them; sessions and cash to the
   first pass and to the first payout; payouts per fee dollar (S3c, comparable within a design only, E-008).
2. **The guard row (E-134 (2)), printed with every P.** The mean net at months 1, 2 and 3; the month-6 and month-12 net
   (mean, p10, p50, p90); CVaR10 (`extended.user_measures.cvar`) of the month-3, month-6 and month-12 net; the long-run
   gate's growth on the required bankroll at the bound with its ruin probability (item 7) -- the gate entry Stage 2
   D-312's `pf_growth_on_base_p50` of the bound arm, as E-158 (M1) fixed it for RD-03, never `median_log_growth`;
   `k1`'s entry from its design's registered gate row; no P printed beside a missing guard value (E-158 (M2)).
3. **E-014's journey variables:** sessions to break-even and the share reaching it by months 1, 2, 3, 6 and 12; the
   share that later falls back; the share of months with a positive net change; the longest run of months without a
   payout; payouts per month.
4. **Each measure as a distribution over start days** (median, p10, p90), with 9.2's uncertainty on every paired
   difference.
5. **The paired readings, by month:** for every measure of items 1 to 3, cell less `k1` (and 6.3's other comparisons):
   the per-start difference (p10, p50, p90); the share of starts differing at all; the shares better, equal and worse at
   months 1, 2, 3, 6, 9 and 12 (for the share ahead: ahead under the cell and not the reference, under both, under
   neither, under the reference and not the cell); the mean difference with 9.2's interval, its window count and its
   minimum detectable difference.
6. **E-007 (e)'s readings beside**, through Q-17's adapter, verdict arm, U1's exact-length runs on every 21st start
   index (`EXACT_EVERY`): the denial ladder and the placement on for every new cell, the ten binding Focused Trader
   models for `yr_act` on each design (the gap named on the other six: "Focused Trader models read on the headline
   cells only"); on every beside row the full guard row, its gate entry the cell's 0 % gate, labelled; P by month, P
   under a bankroll limit, the effective sample size and the MDD.
7. **The long-run gate, every new cell:** at its design's registered seed (P-14's 20261131, P-16's 20261206), 500
   paths, point and bound, with its zero-edge twin, paired with the registered paths: growth on the required bankroll,
   the required bankroll, the ruin probability, payouts a month, days to the first payout, purchases a year. **Nothing
   is a floor: nothing is carried.**
8. **The labels, on every row of (c):** "described, not carried"; "today's market with its points volatility turned
   down, not a replay of 2020-2021" (pitfall 5); "first-order: offers, rungs, marks, table and shift fixed" (4.4); "the
   tick grid's bounce not removed" (pitfall 1); and on `sc` rows "costs scaled by the factor (D-122)", on `tr` rows "the
   trailing factor (beside)".
9. **Not modelled, said wherever (c) appears:** a calmer market's other changes (pitfall 5); the consistency cap's and
   the stand-aside's binding by year (8.4); a user who stops when their money runs out; taxes; payouts unavailable in
   holiday hours; the move to a Live Funded Account; Topstep's unstated news rules (E-034).

**How many intervals, and what chance alone gives.** (c)'s output prints the number of 90 % intervals it shows, that
each is marginal and none simultaneous, and the count expected to exclude zero by chance alone were there no effect
anywhere -- a tenth of them. A count, not a level.

### 9.2 The uncertainty on each paired reading (fixed now)

Descriptions, not tests: nothing is compared with a critical value to decide anything, and no reading has a level
(E-023 (1), E-025). **The method is reading PP's section 9.2, items 1 to 7, unchanged** (`prereg/RD-02_payout_policy.md`,
pinned; built in `extended/pp_reading.py`, imported, never copied), with this reading's own seed for its honesty series:

1. **The windows (E-058 (5)):** at horizon h on a block, the starts in order cut into consecutive windows of h starts
   from the block's first (a last incomplete window dropped), every other window kept from the first; n_w printed with
   every reading.
2. **The interval:** two-sided 90 %, Student t on the kept windows' means, n_w - 1 degrees of freedom, printed only
   when n_w is at least 4 and the means are not all equal; else "too few separated windows for an interval".
3. **The window sign count**, always printed.
4. **The effective sample size**, Bartlett, lag window h (`extended.user_measures.n_eff_bartlett`), beside.
5. **The minimum detectable difference:** (t(0.95; n_w - 1) + t(0.80; n_w - 1)) times the kept windows' standard error,
   printed beside each mean and before it.
6. **A series zero on every start** prints "identical"; one whose kept means are all equal prints its sign count alone.
7. **The interval's honesty, beside, on overlapping series:** RD-02 9.2 item 7's 21 shapes and construction, 20,000
   series per setting, at every (h, n_w) at which this reading prints an interval; **seed 20262310**, each setting
   drawing from `numpy.random.default_rng([20262310, 1, shape, h, n_w])` (`extended.pp_reading.honesty_rng`'s keys),
   the build's test from `[20262310, 0, ...]`, never these keys. The label "under-covers at this window count" where the
   lowest coverage of gauss, ahead and paired at its (h, n_w) is below 0.88; beside every interval, without a
   threshold, the lowest lumpy or persistent coverage, its shape and its misses above and below.

**The gate** is read as two sets of 500 paths on the same seed: each row's two values side by side, no interval.

### 9.3 The leak clause (E-157; the note's 4 (a), "The leak, stated")

(a0), (a2) and (c) describe the judged block's volatility and P-14's and P-16's supply in it. From the commit of this
reading's first run:

1. **Every later declaration** -- a family file, a described reading, or any registration's text -- **states in its
   header that it was written after RD-04 was read**, naming the rows that recorded RD-04's steps.
2. **None cites a figure of RD-04's result files** (`results/vd_descriptive.csv`, `results/vd_replay.csv`,
   `results/vd_replay_gate.csv`, `results/vd_replay_beside.csv`) **as the reason for any parameter**: its value, its class, its range or its grid. A
   parameter whose reason is such a figure was chosen after a look at the judged block: exploratory, reported apart, in
   its own row, `exploratory=True`. A later declaration may cite RD-04 as the reason a *question* is asked (for example,
   why a range-scaled family is declared at all), never as the reason for a *value*.
3. **The choice block stays the only source of a family's choices** (feature-rules section 4). Q-121's (a1), which
   reads the choice block only, may be cited as a reason; its rows equal (a2)'s rows there (8.2), and only the
   choice-block rows of (a2) may be cited, by their Q-121 source.
4. **The red team's read of every later declaration checks 1 to 3.** The lead's family template carries the line
   (section 14 item 4).
5. **Knowledge already on record is disclosed, not cleansed:** D-554, D-580, D-582, D-605 and the red team's M2-4
   (section 2) carried part of this before RD-04; a later declaration that leans on them says so as it would anyway.

**The binding.** The judged block's bars are recorded as read for volatility description (`volatility_descriptive`),
and P-14's and P-16's whole window as read for a calm-regime replay. A later reading of these measures names this one,
states what changed, and reads no block of it as fresh.

## 10. What the reading delivers, and what each outcome means

- **It delivers** (a0)'s rows, (a2)'s description by year and quarter, and (c)'s replay of P-14 and P-16 at a calmer
  amplitude, each beside its reference.
- **It does not deliver** a carried design, a registration id, a confirmation, a claim at a level, a correction of any
  other result, or a parameter for any later design (9.3).
- **No outcome passes or fails.** What follows from each, fixed now:
  - (a2)'s identity fails (8.2): (a2) stops before any judged-block bar is read, and (c) does not run (its factors come
    from (a2)); the failure protocol applies;
  - `vd_identity` fails (8.1), or a shared identity's wait is unmet: (c) stops; (a0) and (a2) stand;
  - an oracle of 8.3 is breached: an engine or adapter error; its step stops and the failure protocol applies;
  - **a replay cell fails D-212's resolution line in some year and R: a finding**, flagged on its rows and read; no
    cell is rerun, re-frozen, dropped or re-admitted because of it;
  - a cell identical to its reference: "no change at this amplitude";
  - the headline shows a large fall in P or in supply: a description of how much of the registered scorecard is points
    volatility; it changes no rule, no design and no verdict. **What the lead may do with it** is declare a new
    question (section 9.3 item 2: a question, not a value) -- for example the classification row for range-scaled
    brackets (E-157);
  - the cost readings straddle the reference: printed side by side; neither is chosen.
- **No confirmation.** Nothing is carried; NQ from 2026-07-17 is not touched.

## 11. Seeds, fixed now and checked

| seed | status | what it draws |
|---|---|---|
| 20262310 | in use | 9.2 item 7's honesty series (keys `[20262310, 1, shape, h, n_w]`) and the build's test of it (keys `[20262310, 0, ...]`) |
| 20262311 | in use | the build's synthetic bars and toy campaigns (T-1 to T-7, T-10, T-12, T-13) |
| 20262312 | in use | the synthetic bars and campaigns of the window's length on which the run's time and memory are measured before step 2 and before step 3 (13) |
| 20262313 | reserved, unused | -- |
| 20262314 | reserved, unused | -- |
| 20262315 | reserved, unused | -- |
| 20262316 | reserved, unused | -- |
| 20262317 | reserved, unused | -- |
| 20262318 | reserved, unused | -- |
| 20262319 | reserved, unused | -- |

**What draws randomness, stage by stage:**

- **step 1, the identity:** the gates at P-14's 20261131 and P-16's 20261206 (inherited, as registered); U1's replays at
  0 % draw nothing (the path seed feeds only the enforcement stream, `identity/user_beside_identity.py` (1));
- **step 2, (a0) and (a2):** nothing;
- **step 3, (c):** the rescaling draws nothing; P-16's sides are its registered coin at seed 20261102 and P-14's its
  registered event sides, unchanged by the map; the gates at the same two registered seeds, so their paths pair with
  the registered ones; U1's replays at 0 % draw nothing; the beside bounds' era bootstrap at the registered era seed
  (`config/atlas_a3.yaml`, `bounds.era_seed`, as `atlas_a3.bounds` reads it), never used; the honesty series at
  20262310;
- **step 4, the readings beside:** the denial ladder's start seeds, Q-17's `lockstep.child_seed(20261920, 0,
  start_day)` (`extended.user_beside.start_seed`, E-024), as `run_starts` draws them -- no keyword takes another seed,
  so `k1`'s ladder rows reproduce Q-44's.

**The check, 2026-11-17 (the machine clock), on this text.** Two word-bounded searches for `2026231[0-9]`, every file
type, code and tests included, the licensed data excluded:

- `git grep -IwnoE "2026231[0-9]" <ref>` on every local and remote ref of the repository (22 refs), the vendored
  snapshot and its results included;
- `grep -rIownE --exclude-dir=.git --exclude-dir=data "2026231[0-9]"` on the working files of the main tree, of every
  worktree under `%LOCALAPPDATA%\stage2-extended-wt\` and of everything under `%LOCALAPPDATA%\stage2-extended-runs\`,
  before this file was written.

They found the block nowhere. After this text is committed they find it in this file alone. The block lies outside the
range 20262000 to 20262199 that Q-82's and Q-108's tests scan, and outside RD-03's own block of ten (its section 12,
named here by reference only: RD-03's T-0 refuses its seeds in any other declaration). The build's
T-9 repeats the check on its commit; T-0 repeats it, in its own scope, on every run.

## 12. The build: adapters and tests

### 12.1 The adapters (in `extended/`, never in `vendor/`)

| id | adapter | what it adds |
|---|---|---|
| A-1 | the map and the factors (`extended/vd_rescale.py`) | 4.1's map as a wrapper of an `arrays` callable, with a factor per session; 4.2's L_ref, L_y, k_y and k_d from a session table; no bar read of its own |
| A-2 | the builders re-composed (`extended/vd_replay.py`) | P-14's and P-16's trade builders copied verbatim in Q-71's pattern (a hash guard on each vendored source; the statement-for-statement proof), with marked additions only: the wrapped arrays (A-1); the frozen offers, rungs, marks and shift passed in (4.4); the scaled costs (4.3); no cache write; the vendored walk, cutoff, coin and bounds functions imported, never copied |
| A-3 | the cells, the gates and the replays (`extended/vd_replay.py`) | each cell's campaign from its trades with the frozen shift and capacity, through `extended/gate.py` and `extended.user_beside.run_starts` with Q-94's recorder, unchanged; nothing in a shared covered file edited |
| A-4 | the reading (`extended/vd_reading.py`, `scripts/vd_descriptive.py`, `scripts/vd_replay.py`, `identity/vd_identity.py`) | sections 3, 8 and 9 in section 13's order; 9.2 by RD-02's functions (`extended/pp_reading.py`, imported); the once rule for (c); the waits by `extended/identity_tokens.py` and `extended/identity_cover.py` |

### 12.2 Tests (fast tier unless marked; written before the code they test)

| test | what it asserts |
|---|---|
| T-0 (before the pin) | `tests/test_rd04_draft.py`: the pin-time form (the `id` and `confirmation_tests_on_this_market` rows; no draft-form status); one `Judged-block reads:` line, its one purpose `volatility_descriptive` parsed by `extended.reader.declared_purposes`, not choosing, not `identity` or `registered_design`; section 11 holds 20262310..20262319 once each and they appear in no other file of the repository (vendored snapshot, reviews and audits included); the cell counts of 6.4 equal 6.2's grid; the identity's cover equals `BASE` plus its script's import closure; Appendix C present; the reader end to end on this text pinned in a temporary tree, authorising `volatility_descriptive` and refusing a purpose not on the line |
| T-1 | A-1's map on synthetic bars (seed 20262311): every price on the grid; the bar order kept; the anchor at the first open; |p' - O_d| at most |p - O_d|; the range within one tick of k times the range; missing bars kept; at k = 1 bit for bit; a factor outside (0, 1] refused |
| T-2 | A-1's factors: L_y and L_ref the medians of the trailing column over the right sessions, the first 20 left out; k_y = min(1, L_ref / L_y); k_d causal -- a shift-invariance test: changing any session from d on changes no factor before d (skill feature-rules); a session without a trailing mean unscaled and counted |
| T-3 | the frozen inputs: on a toy where the rescaled walk would admit fewer marks or another rung, the cell's offers are still the reference's; the shift and the capacity the reference's; P-14's rung map read from its pinned file only |
| T-4 | the cost readings: each per-trade cost multiplied by k under `sc`, untouched under `act`; account fees untouched under both; at k = 1 the two equal bit for bit |
| T-5 | no write under the data folder: the replay path on toy bars in a temporary tree whose data folder is listed before and after (names, sizes, times) and must be unchanged; `cached_walk` never called with `write=True` on wrapped arrays |
| T-6 | 9.2 on RD-02's functions with this seed: the kept windows, the interval from four kept windows with a spread, the sign count, the zero-series rule, the MDD's formula, and the honesty series' keys `[20262310, 0, ...]` drawn only by the test |
| T-7 | 8.3's oracles on toys, each shown to fire on a hand-broken case |
| T-8 (`slow`, `heavy`) | 8.1 items 1 to 6 at 4 paths and 4 starts per design and arm, through `identity/vd_identity.py` |
| T-9 | section 11's seeds appear nowhere in the build's commit outside the uses section 11 declares |
| T-10 | (a2)'s order: the whole-window read is not authorised before the early-block identity holds; the identity fires on a nudged cell of a toy Q-121 file; the early rows re-checked after the whole-window run |
| T-11 | `identity/vd_identity.py` runs the reference only: the factor 1 and the cost reading `act` constants; no argument naming a factor, a cost reading or a cell; any flipped refuses before the first session |
| T-12 | (c)'s once rule on a toy ledger: a second run of the same part under the same row refused, the other part allowed; allowed with `--repeat` naming a row that names this file, once; a row not naming this file refused |
| T-13 | the labels of 9.1 item 8 on every (c) row; D-212 failures flagged and never filtered; no P printed without its guard row; the count of intervals and the tenth expected by chance printed |
| T-14 | A-3 with the factor 1 and `act`: every gate row, replay and recorder row equals the path without A-1 and A-2, bit for bit, on toy campaigns |

## 13. Outputs and the run

### 13.1 Files

Each written with its sidecar manifest through `extended.results.write_result`:

- **`results/vd_descriptive.csv`** (step 2), sections:
  - `identity` -- (a2)'s early-block comparison with Q-121's file: `check`, `holds`, `compared`, `differing`,
    `problems`;
  - `a0` -- the gate files' rows as read: `source`, `source_sha256`, `gate_section` (`period` or `drift`), then every
    column of the source row, as text;
  - `session` -- per session: `date`, `year`, `quarter`, the range in points and in percent, their trailing 20-session
    means, the trailing factor `k_trail`, in Q-121's column names;
  - `year`, `quarter` -- per period and quantity: `quantity`, `n`, `median`, `p10`, `p90`;
  - `band` -- per period, band (points or share of the trailing range), R and the design's marks or slots:
    first-exit time `median`, `p10`, `p90`, `open_share_1508`, `n`;
  - `factor` -- `l_ref_pts` with its source file and sha256; per year `l_year_pts`, `k_year`, `sessions`; per year the
    trailing factor's `k_trail_p10`, `k_trail_p50`, `k_trail_p90` and `sessions_unscaled`.
- **`results/vd_replay.csv`** (step 3), sections `identity`, `oracle`, `frozen`, `mechanics`, `resolution`,
  `bounds_beside`, `scorecard`, `guard`, `paired`, `coverage`; every row keyed by `design`
  (`p14`, `p16`), `cell` (`k1`, `yr_act`, `yr_sc`, `tr_act`, `tr_sc`), `arm`, `block` and, where it applies, `measure`,
  `h`, `year`, `rr`, `response`; the scorecard's columns `n_starts`, `mean`, `p10`, `p50`, `p90`; the paired columns
  `diff_mean`, `diff_p10`, `diff_p50`, `diff_p90`, `share_differing`, `better`, `equal`, `worse`, `n_w`, `ci_lo`,
  `ci_hi`, `sign_pos`, `sign_neg`, `n_eff`, `mdd`, `under_covers`; the resolution columns `offers`,
  `unresolved_share`, `d212_line`, `fails_d212`; and the labels of 9.1 item 8 in a `labels` column.
- **`results/vd_replay_gate.csv`** (step 3) -- the gate rows: `design`, `cell`, `shift` (point, bound), `twin`, the
  gate's own columns as `extended/gate.py` writes them.
- **`results/vd_replay_beside.csv`** (step 4), sections `reference_checks` (`k1`'s fourteen responses against Q-44's
  per-start file: `design`, `response`, `holds`, `compared`, `differing`, `problems`), `ladder`, `rtp`, `ftp`, each
  beside row with the scorecard's and the paired columns above, its full guard row and its gate entry labelled "the
  gate at 0 %". Step 4 writes its own file: no result file is written twice or overwritten.

**Each manifest carries:** `prereg_id` `RD-04` and its pinning row; the rows under which `vd_identity`, Q-05, Q-80, Q-93
with Q-100 and Q-101 held, each with its sha and the run's head (none for step 2); Q-121's file, its sha256 and its row;
the cell and run counts (6.4, as run); each cell's trades' content hash (`rc_dev_test.trades_hash`'s form) and its
walk's row count; every seed, the inherited ones named; every parameter of section 7 with its class; the commit and blob ids of every adapter run; the sha256 of `vendor/DATA_MANIFEST_stage2.sha256`, checked
before the first read; `exploratory=False` (nothing is chosen after a look), every row labelled "described, not
carried".

### 13.2 The run, in four steps

Each from a clean checkout of a named commit (`scripts/run_clean.py`), under the run lock (`run.lock`, skill
`run-lock`), one heavy job on the machine, watched to its exit; **each step only after the lead's row records the one
before**:

1. **the identity:** `identity/vd_identity.py`, under the purpose `identity` and its own row. **A failure stops (c)**;
   step 2 does not depend on it and runs once the lead's row has recorded step 1, whatever its outcome.
2. **(a0) and (a2)** (`scripts/vd_descriptive.py`): (a) (a0)'s two files' rows, each file checked against the vendored
   manifest first; (b) (a2)'s early-block identity (8.2), refusing, before any authorisation; (c) the read under
   `volatility_descriptive`, the whole-window computation, its early rows re-checked; (d) the factors; (e)
   `results/vd_descriptive.csv`.
3. **(c)** (`scripts/vd_replay.py --part scorecard`, purpose `registered_design`, the pinning row, P-14 and P-16; its
   once rule first):
   (a) the factors recomputed from step 2's file and checked; (b) `k1` on P-14 then P-16, both arms, the recorder on,
   its start rows against U1's again; (c) each new cell, P-14 then P-16, in the order `yr_act`, `yr_sc`, `tr_act`,
   `tr_sc`, each checked under 8.3 before anything of it is read; (d) the gates in the same order; (e) the mechanics,
   then the reading; (f) `results/vd_replay.csv` and `results/vd_replay_gate.csv`.
4. **The readings beside** (`scripts/vd_replay.py --part beside`, the same purpose and row; its once rule first; the
   cells' trades rebuilt as step 3 built them and their hashes checked equal to step 3's manifest): `k1`'s fourteen
   responses against Q-44's per-start file first, refusing; then the ladder and the placement on every new cell in step
   3's order; then the Focused Trader models on the two `yr_act` cells; then `results/vd_replay_beside.csv`.

**On any failure, nothing more of the failed step's own run is computed, written or printed**: that step's run stops
at the failed check, and its log and the check's own lines are all it leaves. A failure in step 1 or 3 stops (c); a
failure in step 2 stops (a2) and (c); a failure in step 4 stops the beside readings, and steps 2 and 3's files stand.

- **weight: heavy.** Four rescaled walks over the window (built again in step 4, its trades held to step 3's hashes),
  ten replays on two arms over every start, eight gates of 500 paths, fifty-two replays beside; (a2)'s one pass over
  the bars. Measured on synthetic bars and campaigns of the window's length (seed 20262312) before step 2 and before
  step 3 (E-117's form), and stated in the lead's row with its memory; two workers at most.
- **A restart or a rerun (E-053).** Each step allows one clean run; a restart, a rerun after a fix, or the failure
  protocol's replication is a further read: `repeat='E-NNN'` for (a2) and `--repeat E-NNN` for (c), a row naming this
  file. Only the first complete run of each step is read.

### 13.3 Waits, all before step 1 unless stated

- the pinning row, naming P-14 and P-16 (it admits (c)'s `registered_design` reads);
- **Q-121's file on master** from its own clean run, with its row (before step 2), and this text's names for it
  matching (section 14 item 2);
- every shared identity of 8.1 held at a commit whose covers are unchanged at the run's commit (the build edits no
  shared covered file, 4.6);
- **Q-44's per-start file on master** (`results/user_beside_starts.csv`), for step 4's reference checks (before step 4);
- the adapters built with T-0 to T-14, and the red team's read of the build;
- step 1's `vd_identity` held (before step 3); step 2 recorded (before step 3).

## 14. Open before the pin

**The lead's:**

1. **The red team's read of this text, then the gatekeeper's**; and **T-0** (`tests/test_rd04_draft.py`, owed by the
   build or written before the pin), which must pass on the text pinned.
2. **Q-121's names.** This text names Q-121's file `results/vol_descriptive.csv`, its section `session` and its columns
   `date` and `range_pts_trail20` by their roles; Q-121's build fixes the real names, and the pin-time text writes
   them. And **where Q-121's judged-date refusal sits**: if inside its per-session functions, (a2) cannot import them
   unchanged (3.2); placing the refusal at its script's entry, or behind a keyword its script sets, keeps one code path
   for (a1) and (a2).
3. **The pinning row names P-14 and P-16**, so it can serve as (c)'s `registered_design` declaration (5 item 6); or the
   lead names another row here before the pin.
4. **The leak clause's line in the family template** (9.3 item 4): the lead's, with Q-122's template work (E-157 (b)).
5. **(a0)'s home, settled.** E-157 (a1) listed the gate files' `period` and `drift` rows under Q-121; E-158 corrected
   it (their rows span the judged block, so they are read under this reading), as Q-121's and Q-123's briefs say. Nothing
   open; recorded for the red team.

**The operator's:** none before the run. After it: nothing to choose -- (c) is a description. Pre-2020 bars stay the
operator's purchase decision (E-008), not proposed here.

## 15. Anything chosen after seeing results

*(Empty at declaration. Anything added after a reading is exploratory, reported apart, `exploratory=True` in its
manifest, and recorded in its own decision row -- never in this file.)*

---

## Appendix C -- the drafter's choices, each with its reason

Every choice made where the note, the brief or the rules left the text open.

| # | choice | where | reason |
|---|---|---|---|
| 1 | (c)'s judged reads under `registered_design` by the pinning row, not on the `Judged-block reads:` line | 5 item 6 | the brief and E-157; the reader admits `registered_design` only under a decision row naming the designs, never under a declaration's file, whatever its line says (`extended/reader.py:36-41`, `_registered`) |
| 2 | a once rule for (c) enforced by its own script | 5 item 6; T-12 | the reader never limits `registered_design` to one run; a declared reading is read once (E-053) |
| 3 | the map rounds half to even, about the session's first open | 4.1 | the note's map made exact; half to even is numpy's default and non-decreasing, so bar order is kept; exact at k = 1 |
| 4 | L_ref and L_y as medians of the trailing 20-session mean, the window's first 20 sessions left out | 4.2 | the note's definitions; the trailing mean is undefined there |
| 5 | the trailing factor uses the actual bars' trailing range, a session without one unscaled | 4.2 | causal, and independent of the map; scaling by a factor computed on rescaled bars would feed the map into itself |
| 6 | the verdict arm's shift frozen at the reference's; the cell's own bounds printed beside, unused | 4.4 | the edge assumption held fixed so only the amplitude moves; recomputing the bound would mix the bound's noise into the replay |
| 7 | the 2 x 2 grid of factor and cost reading, every cell run | 6.2 | the brief names both factors and both cost readings; a full grid lets each be read alone (6.3) |
| 8 | the cost reading scales every per-trade cost, not the account fees | 4.3 | D-122's bounce is per trade; the subscription and activation are the contract's, fixed in dollars, the thing held constant |
| 9 | the ten Focused Trader models on the two headline cells only, the gap named | 6.4; 9.1 item 6 | E-007 (e) asks for them beside every user reading; the six other cells are sensitivity readings of the headline's two assumptions, and 60 more heavy replays for them is a cost the lead may still choose to pay (the red team may say otherwise) |
| 10 | the ladder and the placement on every new cell | 6.4 | E-007 (e); cheap beside the walks |
| 11 | (a2) reuses Q-121's code, its early rows its identity | 3.2; 8.2 | one code path for (a1) and (a2); the identity is free and comes before the judged read |
| 12 | (c)'s factors computed from (a2)'s file, so (a2) runs first | 13.2 | one source for L_y; (a2)'s identity then covers (c)'s inputs |
| 13 | L_ref read from Q-121's file and also recomputed from (a2)'s rows, both required equal | 4.2; 8.3 | the brief: L_ref from Q-121's file, named by path |
| 14 | the frozen marks' and rungs' would-fail counts printed beside | 4.4; 8.4 | the note's pitfall 4 says the unresolved shares are reported; the counts say how far the frozen admission is from what the rescaled walk would admit, without acting on it |
| 15 | the consistency cap's and the stand-aside's binding by year named as not read | 8.4 | no record this reading's path carries holds them (the gate files carry pooled columns only); a counters channel would edit a shared covered file (RD-03's A-1 (d) is on an unmerged branch) |
| 16 | a second reference (the choice block's median) dropped | 7 | the note's "possibly"; doubles the heavy cells for an unasked variant |
| 17 | the leak clause extended from (a2) to (a0) and (c) | 9.3 | all three describe the judged block; a question may cite them, a value may not |
| 18 | the uncertainty method RD-02's 9.2 unchanged, with this reading's own honesty seed | 9.2 | the program's corrected method (E-058 (5)), built and tested; a new seed so no seed changes meaning |
| 19 | (a0) recorded in the result's manifest, not the read ledger | 5 item 6 | the reader ledgers bar, walk and engine reads only; the gate files are vendored results |
| 20 | no shared covered file edited; new modules only | 4.6; 12.1 | keeps every shared identity's token valid (E-104, E-117), unlike RD-03's build (E-156) |
| 21 | Q-121's file, section and column names written by their roles, to be replaced by Q-121's real names at the pin | 4.2; 14 item 2 | Q-121 is not built at this text; the brief asks the file named by path and its columns stated |
| 22 | Q-44's per-start file a wait before step 4, `k1`'s fourteen responses checked against it | 8.1; 13.3 | RD-03's form (its 9.1 item 6): the beside readings' reference is the program's own, not recomputed unchecked |
| 23 | `k1` replayed inside step 3 and held to U1's rows, the pairs read against that replay | 8.1; 9.1 | the paired readings need U1's records in this repository's form; the comparison keeps them U1's |
| 24 | step 4 rebuilds the cells' trades and holds them to step 3's hashes, writing no intermediate file | 13.2 | a result is written only through `write_result` from a clean run; an untracked cache of rescaled trades would be neither |
