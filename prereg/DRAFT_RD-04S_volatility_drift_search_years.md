# RD-10: volatility drift on the search years only -- (a0) the gate files' search-year rows, (a2) Q-121's choice-block descriptive, and a calm-regime replay of P-14 and P-16 (reading VD-S) -- a delta declaration of RD-04, a described reading, unnumbered (E-023 (1))

**Status: declared before anything of it is built or read (O-7, as the lead extended it to RD-04 on the red team's M-3); the second text.** It is pinned by
the sha256 of its LF text in its decision row; nothing declared is edited, a change is a new declaration under a new
row. Written
on wt/wt-firms, 2026-11-19. It re-declares `prereg/RD-04_volatility_drift.md` on the search years alone, so that no
part of the reading touches NQ's held-out years (E-208), which E-221 (O-1) keeps for one joint fixed-sequence
confirmation across firms. The red team's read of the four sibling deltas (`docs/reviews/O7_SEARCH_YEARS_2026-11-19.md`,
M-3) found RD-04's (c) a route to the held-out years that the reader's rule 4 does not close (its `registered_design`
purpose falls under rule 3); this text removes it by reading no held-out day at all. The parent is not edited: it stays
on record, pinned, and is never run (section 0.3). Its id is RD-10 (section 0.2). It follows its
siblings' rules (RD-06 to RD-09), as the lead ruled on the red team's findings; it is complete on its own.

| field | value |
|---|---|
| id | **`RD-10`** (`prereg/RD-10_volatility_drift_search_years.md`); every result's `prereg_id` is `RD-10` (S-10) |
| parent | `prereg/RD-04_volatility_drift.md` sha256 `a8965e1602c5987a0f7fe4fe13f0bf3ce7448c96b38c193e8674782a25c2593b` (of its LF text), pinned by E-168 |
| reading | VD-S: (a0) the two registered gate files' `period` and `drift` rows of the search years (S-17); (a2) Q-121's choice-block descriptive, read as it stands (S-18); (c) the parent's calm-regime replay of P-14 and P-16, every cell, on the search years (S-19) |
| kind | a **described reading** (E-023 (1), as E-157 (c) classes the parent): never carried; no program family number, no level, no pass line, no pick, no menu |
| development data | NQ 1-minute bars, 2020-01-02 to 2023-12-29 (the search years, E-208), read only inside Stage 2's engine by P-14's and P-16's registered builders for (c), cut at the read (S-2); (a2) reads no bar (S-18) |
| held-out years | 2024-01-02 to 2026-07-16: never read by this reading, under any purpose, the parent's registered reproduction identities excepted (S-1, S-8, S-11) |
| blocks | (a2): Q-121's, by calendar year and quarter, 2020 to 2023; (c): all search-year starts the headline, the search years' first half and second half beside, each per measure at its h (S-7) |
| judged-block purposes | none (S-11); (c) reads the search years under the purpose `registered_design` (S-19) |
| confirmation | none; NQ from 2026-07-17 never read |
| the build | not built by this item: section 6 is the build list for a later item |

## 0. What this file is, and how it reads its parent

### 0.1 The incorporation

This declaration **is the parent's text, with the replacements below**. Every section, table, rule, cell, count,
seed, oracle, test and wait of `prereg/RD-04_volatility_drift.md` at the sha256 above is part of this declaration, read
with:

1. the general replacements S-1 to S-20 (section 2), which apply wherever the parent's words reach them;
2. the line-by-line replacements of section 3, each citing the parent's line and a short quote from it; a row citing a
   whole section (its lines as one range) replaces that section by the rule it names.

Where a replacement and the parent's words differ, the replacement is the declaration. Where section 3 is silent on a
parent line, section 2 governs it; where both are silent, the parent's words stand (section 5 lists what stands, and
section 4 lists every line the search of section 7 found that needs no change, with the reason). Section numbers,
item numbers, cell names (`k1`, `yr_act`, `yr_sc`, `tr_act`, `tr_sc`), test names and the parent's own labels (its
pitfalls, its adapters A-1 to A-4, its findings M1 to M5, m1 to m7 and n1 to n12) are the parent's; **the labels S-1 to
S-20 are this file's**.

### 0.2 The id and the name

RD-06 for RD-01's delta, RD-07 for RD-02's, RD-08 for RD-03's, RD-09 for RD-05's part F, **RD-10 for this file**. The
pinned name is `prereg/RD-10_volatility_drift_search_years.md`; it matches no other reading's T-0 glob (the parent's
T-0 takes `*volatility_drift.md` with its two exact names). **New numbers, not a suffix**: the reader takes a
declaration's id from its path as `RD-` and digits (`extended/reader.py`'s `DECLARATION_ID`), so a manifest, ledger or
token naming `prereg/RD-04S_...` would be attributed to RD-04.

### 0.3 The parent, superseded before any run

No result of the parent exists: the read ledger holds no line of RD-04 and no file `results/rd04_*.csv` exists at this
text's pin; nothing of it is built. At this file's pin the parent is **superseded, never run**: no run takes its purpose
`volatility_descriptive`, no `heldout-read` row is written for `scripts/rd04_replay.py` (the red team's M-3), its
result files are never written, and its id is never a manifest's `prereg_id`. The reader cannot see a withdrawal (the
audit's R-8 registry is not built); its rule 4 refuses the parent's `volatility_descriptive` only until a market's
verdict row exists, and the rule-3 hole for `registered_design` is being closed separately (the lead's ruling on
M-3). So the supersession is enforced by the build (section 6, B-1), held now by T-0's code check (N-1: no new code
takes up the parent's purpose or declaration constant; Q-121's frozen module keeps its constants, never called in its
authorised mode), and recorded in the pinning row.

### 0.5 The drafter's reads (disclosed)

The drafter opened: the parent (whole) and its pinning row; CHARTER 3.3 and 3.6; E-208, E-210 and E-221;
`extended/reader.py` (at 6ce8e6a and as merged); the runners' code that names the parent; the vendored code the cut
touches (`user_journey`, `customer_journey`, `rc150_dev_test`, `rc_dev_test`, `rc_width_screen`, `resolved_coin`,
`atlas_a3`, `a3_brk30`, `a3_resolution_map`, `customer_slices`, `u_select`); and the red team's two reads with its
scratch `extra_terms.py`. **Of result files the drafter opened only names and keys, no value**: the column names and
the distinct design, arm and response keys of Q-44's per-start file `results/user_beside_starts.csv`; the column
names and the distinct section, cell and stop keys of `vendor/stage2/results/rc_width_screen.csv` and its
manifest's field names; the read ledger's declaration and purpose fields. No row of the gate files
(`vendor/stage2/results/a3_brk30_cb20_gate.csv`, `vendor/stage2/results/rc_s150_all_gate.csv`) was opened, and of
Q-121's `results/q121_vol_descriptive_a1.csv` only its presence in the main tree and E-177's sha256 are known to
the drafter, which (a2) and (c) read through S-18's check. No bar was opened.

## 1. Why, and what it does to what the reading can show (E-051)

**Why.** Under E-208 every choice and every map the journey search draws on is made on the search years, and the
held-out years are read once, by the joint confirmation (E-221, O-1). CHARTER 3.3 (a) names RD-04 as the source of the
volatility drift lever units must respect and forbids any volatility unit or regime threshold that reads the held-out
years; the parent's (a2) reads them by design, and its (c)'s factors for 2024 to 2026 are functions of them. The lead
ruled that RD-04 is re-declared on the search years by O-7's rule.

**What it does to what the reading can show.** The descriptive is the choice block's alone, which Q-121 already wrote
(E-177): the drift between 2020-2021 and 2022-2023 is described, the rise into 2024-2026 is not (that is the held-out
years' to show, after the verdict, as a description under CHARTER 3.6 (c)). The parent's question "whether the rise is
price level or percent volatility" is answered over four years, not six and a half. (c) replays the search years only:
each year factor k_y is 2020's to 2023's, so the replay compresses at most the years of the search span above the
calm reference, and its scorecard shows how much of P-14's and P-16's search-year journey is points volatility. Each
measure's starts are fewer (S-6), so more readings print "too few separated windows for an interval", and each half
(S-7) holds about two years. The verdict arm's frozen shift is the search years' own, with the halves as eras (S-5).
**There is no leak clause** (S-20): every figure of this reading is of the search years, which CHARTER 3.3 (a) admits as
a source.

## 2. The general replacements

- **S-1. The window.** The development data are NQ 1-minute bars from 2020-01-02 to 2023-12-29, the search years
  (E-208). The held-out years 2024-01-02 to 2026-07-16 are never read by this reading, under any purpose, by (a0),
  (a2), (c), its gates, checks or beside readings; NQ from 2026-07-17 is never read. Wherever the parent says "the
  development window", "the whole window", "2020-2026" or "2020 to 2026" of what this reading reads, read the search
  years.
  **The one exception (the re-read's rm-4):** the parent's registered reproduction identities (S-8) take the whole
  window under the purpose `identity`; they reproduce Stage 2's registered files, write no outcome of any cell and
  are ledgered in a clean run. No other part of this reading, and no check it introduces, takes a held-out day.
- **S-2. The cut at the read** (for (c); RD-06's S-2 in effect). No bar or atlas row dated after 2023-12-29 reaches any
  function of the registered builders, the re-composed builders of the parent's A-2, the replay, the gate or the
  reading. **The guard is the wrapper and the refusal below**, not the reader's authorisation (the reader cannot see
  reads inside vendored calls). The wrapper acts, for the builders' calls only, on exactly these inputs, and restores
  each after the call (nothing vendored is edited): (1) **the bars**, `propedge.data.bars.read_bars` as
  `atlas_a3.bar_arrays` calls it, its last date clamped to 2023-12-29 -- the parent's map (A-1) then wraps the cut
  callable; (2) **A1's events and days**, the two `pd.read_parquet` reads of `a3_resolution_map.load_a1`, the rows
  after 2023-12-29 dropped, **its manifest's `day_list` left whole**; (3) **A3's walks**, the `pd.read_parquet` of
  `atlas_a3.cached_walk`, the rows after 2023-12-29 dropped; (4) **the day list** each builder passes to the walk and
  the bounds, cut. **The vendored checks switched off on the cut, and no others:** (a) `rc_dev_test.trade_problems` as
  the registered P-16 build calls it (its screen row and content hash, whole-window facts); (b) where called,
  `a3_brk30`'s check that the configured eras are P-11's. Each is named in the run's manifest. The runner refuses,
  before any replay, any block or date after 2023-12-29. **If a builder cannot be cut at these reads, or another
  vendored check fails on the cut, the build stops and reports; no fallback.**
- **S-3. P-16's offered marks, fixed to its registered set** (the lead's ruling on B-2), as RD-06's S-3: the parent's
  frozen "five-minute marks the cutoff admits at the 150-tick stop on the actual bars" are the registered set,
  `vendor/stage2/results/rc_width_screen.csv` section `marks` at P-16's stop, the columns `stop_ticks`, `slot` and
  `offered` only, returned for the call by a wrapper on `resolved_coin.mark_resolution`, its admitted count equal to
  the `rc_s150_all` cell row's `marks_offered` (refusing); never re-resolved on the cut. P-14's rung map is a pinned
  file already. Both are whole-window choices of Stage 2's, inherited and labelled (S-12).
- **S-4. The nested cut, refusing** (the lead's ruling on B-2). Before any cell of (c), each design's k = 1 stream is
  built twice on the cut, with S-3's marks: on 2020-01-02 to 2022-12-30 and on 2020-01-02 to 2023-12-29. Their
  point-arm day blocks must be equal up to 2022-12-30, block for block, every field. It reads the search years only,
  writes its pass or fail lines to the run's log and manifest, and a failure stops (c). **No identity these deltas introduce reads 2024 or later** (the lead's ruling rn-5); the parent's declared identities keep
  their declared whole-window form, labelled so (S-8 says which of the parent's identity items they are).
- **S-5. The frozen shift, re-estimated on the search years with the halves as eras** (the lead's ruling on M-1). The
  parent freezes "each R's `lb - e` from the k = 1 build (`atlas_a3.bounds`, the era rule at its registered seed)"; on
  the cut that build is the search years', and its eras are **declared now as the two calendar halves, 2020-2021 and
  2022-2023**, passed in the bounds' configuration for the call, at the registered trial count and era seed (P-11's
  spans would leave 2023 alone). The gate's `e`, `lb`, `e_by_rr` and `lb_by_rr` are these. The `bounds_beside` section
  uses the same eras. **Printed in every manifest, per design and R:** the flag, the bound read, the pooled bound and
  each era's.
- **S-6. The starts and the horizon embargo** (CHARTER 3.6 (d)). (c)'s starts are every start day U1 reads inside the
  search years; each measure (RD-03's section 5 table, carried) is read at h only on starts with h sessions inside the
  search years, which `u_select.block(records, None, h)` gives on the cut replay. U1's long replay and exact-length runs
  stop at the cut. By start year: 2020 to 2023, means only, labelled. Wherever the parent says "every start" or "all
  starts" of (c), read the search-year starts with the horizon left.
- **S-7. The blocks, for (c): the late block replaced by the search years' second half.** **all** (the headline);
  **first**, the starts of 2020 and 2021, read at h only if h sessions remain before 2022's first session; **second**,
  the starts of 2022 and 2023, h inside the search years. On the point arm the halves share no session; on the verdict
  arm they share S-5's frozen shift, labelled. The parent's "the factor of a start's later sessions is their own
  year's" holds within the search years. Nothing is chosen on any block. The reason is RD-06's S-7.
- **S-8. The identities, the comparisons and the citations** (the lead's ruling on B-1). The shared reproduction
  identities (Q-05, Q-80, Q-93 with Q-100, Q-101) are untouched. Of the parent's own `rd04_identity` (8.1): **items 2
  to 5, which reproduce Stage 2's registered files** (the A3 cache, the registered trades and their hash, the registered
  gate paths, U1's start rows), **run as the parent states them**, in their declared whole-window form, labelled so (the lead's ruling rn-5), the purpose `identity`, their own row,
  writing pass or fail only; **items 1 and 6, which reproduce no registered file** (the wrapper's arrays equal the
  vendored callable's; `sc` at k = 1 equals `act`), **run on the search years only**. Inside (c)'s own run, every
  comparison with U1's or Q-44's per-start rows is **on the point arm only**, on the starts whose 252-session replay ends
  inside the search years; so `k1`'s repeat of item 5 compares its point-arm start rows, and step 4's reference checks
  run `k1` under its fourteen responses on the point arm for the checks alone (twenty-eight replays, read for nothing
  else). Q-44's verdict rows and its pooled file are never cited.
- **S-9. The gate on the search years.** Every gate of (c) draws its resampled days from the search-year day blocks.
  Each new cell's gate pairs with its design's `k1` search-year gate at the same seed (the same pool of days, so the
  same day indices, the parent's 5 item 4 argument unchanged), not with the registered gate paths. `k1`'s two
  search-year gates are run and read beside as the pairs' references; the registered gate paths stay S-8's
  reproduction identities. `k1`'s guard-row gate entry is its search-year gate's, not "its design's registered gate
  row".
- **S-10. The outputs.** New files, never the parent's: `results/rd04s_descriptive.csv` (sections `identity`, `a0` and
  `factor`), `results/rd04s_replay.csv`, `results/rd04s_replay_gate.csv`, `results/rd04s_replay_beside.csv`, each
  through `extended.results.write_result` with its sidecar manifest, `prereg_id` this file's id at the pin, the window
  2020-01-02 to 2023-12-29, S-4's result, S-5's constants and flags, S-2's switched-off checks, Q-121's file with its
  sha256 and row, S-12's list, and every other field the parent's 13.1 lists. Q-121's own sections are cited by path
  and sha256, not copied.
- **S-11. No judged-block purpose.** This declaration reads no day of the held-out years, so it carries no line of the
  reader's judged-block form and names no purpose for it; the reader refuses any judged read citing it. The parent's
  line (`volatility_descriptive`) is the parent's and is never taken (0.3).
- **S-12. The held-out read ledger, inherited and labelled** (CHARTER 3.6 (b); no figure cited). This reading rests on
  designs and records that read the held-out years before it: P-14 fixed as R* from the whole window (Stage 2 D-626);
  P-14's rung map and P-16's mark cutoff resolved on the whole window (E-203 S-2), the latter fixed here as P-16's
  registered mark set (S-3); P-16's stop chosen on each block (Stage 2 D-554, "the 50-point stop fails resolution
  early and resolves late"); the era rule on mean gross R over 2020-2022 against 2023 to the window's end (D-271,
  D-420, D-437); the regime map on other bars to June 2025 (D-238, D-239, not vendored, never read here); the span
  guard and the money by year in words (D-578, D-580 to D-582, D-604, D-605); this repository's pooled and worst-year
  resolution shares (E-024, E-030, F-B's M2-4); the registered state tables and protocols; **the two gate files'
  `period` and `drift` rows of the later periods**, whole-window Stage 2 rows, never loaded here (S-17); program U's
  nine families' late-block reads of P; U1's whole-window start rows and Q-44's per-start rows, compared and cited here
  on the point arm and search-year starts only; the parent's registered reproduction identities (`rd04_identity`'s items 2 to 5: the A3 cache, the registered trades and their hash, the registered gate paths, U1's start rows) and the shared ones it waits for (Q-05, Q-80, Q-93 with Q-100, Q-101), which read the whole window under the purpose `identity`, write pass or fail only and are ledgered in a clean run (S-1's one exception, S-8); and the parent's own pinned text, declared over the whole window and
  never run. Nothing here re-estimates them but S-5's constants; every result file names them.
- **S-13. Prior exposure, re-read.** The parent's prior-exposure rows stand as records. Where a row's bearing reads "the
  late block has been read for P many times: late development, not out of sample", read: those reads were of the
  held-out years; they are S-12's entries; this reading reads none of those years.
- **S-14. The binding.** The parent's "the judged block's bars are recorded as read for volatility description ... and
  P-14's and P-16's whole window as read for a calm-regime replay" reads: the search years are recorded as read for
  volatility description (by Q-121's file, cited) and P-14's and P-16's search years for a calm-regime replay; the
  held-out years are not read by this reading and are recorded as unread by it.
- **S-15. In sample.** Every statement made from this reading is a description of the search years, with no
  confirmation (E-023 (1)); the held-out years stay unread by it.
- **S-16. Reruns.** (c)'s `registered_design` reads are ledgered inside a clean run, and its script's own once rule per
  part (the parent's 5 item 6, its third refusal) stands; the lead's rule applies beside it: only the first complete
  clean run of each step is read, a restart or rerun recorded under a row naming this file, and no result file is ever
  overwritten (S-10).
- **S-17. (a0) on the search years.** From each of the two registered gate files, checked first against
  `vendor/MANIFEST_stage2.sha256`: the section `drift`'s rows of the years 2020 to 2023 and the section `period`'s row
  `2020-2022`, every column, as text. **The rows `2023-2026`, `all` and `check` of `period` and the years 2024 to 2026
  of `drift` are never loaded**: the file is parsed line by line and a line is kept only after its `section` and its
  period or year are read and admitted; no other field of a refused line is kept, printed or written. Copied into
  `results/rd04s_descriptive.csv` section `a0` with the source file and its sha256.
- **S-18. (a2) is Q-121's file, read as it stands.** The parent's (a2) runs Q-121's module over the whole window under
  `volatility_descriptive`; on the search years that descriptive already exists: `results/q121_vol_descriptive_a1.csv`,
  sha256 `f1cbb7b88f412fa98c5c8e5fb983e6d70242a9a65b90a9cf6d296064d7a34e26`, collected from a clean run under E-177, its
  manifest verifying and both of Q-121's refusing identities held in that run. So **(a2) reads no bar and runs no
  module**: the check hashes the file's **raw bytes** (as written, CRLF line ends, not its LF text) against that sha256
  and checks its sidecar manifest and E-177, refusing; the file is git-ignored, so a clean run reads it in place from
  the main tree's `results/`, never copying it, as Q-171 does; and its `session` and
  `range` rows (2020-01-02 to 2023-12-29) are what (c)'s factors read. Q-121's module is never called in its authorised
  mode; the parent's (a2)'s identity (8.2) is replaced by this check.
- **S-19. (c) on the search years.** The parent's calm-regime replay, its map, factors, cost readings, frozen inputs,
  pitfalls, adapters, cells and readings, on the search years: L_ref unchanged (2020-01-02 to 2021-12-31, the lead's
  choice, inside the search years); **k_y for the years 2020 to 2023 only**, each L_y Q-121's median and equal to its
  `range` row (the parent's free cross-check, now every year's); k_d from Q-121's `session` rows; the replay cut at the
  read (S-2); the frozen inputs from the k = 1 cut build (S-3 to S-5). Its engine reads are authorised by
  `extended.reader.authorise_engine_read` under the purpose **`registered_design`**, `design=["P-14", "P-16"]`, the
  declaration this file's pinning row (naming both designs), on **2020-01-02 to 2023-12-29** only, from
  `scripts/rd04_replay.py`, inside a clean run, ledgered; no held-out day is ever authorised, so the reader's rule 3
  never applies. The script's three refusals stand, the second reading **this file's** pin (`prereg/RD-10_volatility_drift_search_years.md`
  hashing to its pinning row's sha256), never the parent's.
- **S-20. No leak clause.** The parent's 9.3 exists because (a2) and (c) describe the held-out years' volatility. This
  reading describes the search years only, which CHARTER 3.3 (a) admits as a source of lever ranges, units and
  thresholds, so **9.3 is not this file's**: the pinning row adopts no program rule from it, no `RD-04 read: step 2`
  token is written for this file, and later declarations need no "written after" line on its account. The parent's
  clause and its test (`tests/test_rd04_leak_clause.py`, T-15) stay on master; the test binds nothing while the parent's
  `volatility_descriptive` line is unledgered, which 0.3 keeps so.

## 3. Every dependency in the parent, line by line

The parent's lines as numbered in its LF text at the pinned sha256. A row's lines are one line, a range whose joined
text holds the quote, or a list of lines each holding the quote. The replacement is this declaration's.

| # | parent lines | where | quote | replacement |
|---|---|---|---|---|
| D-01 | L47 | header table, reading | "(a2) the bars-only descriptive on the whole development window" | (a0) the gate files' search-year rows (S-17); (a2) Q-121's choice-block file, read as it stands (S-18); (c) on the search years (S-19) |
| D-02 | L48 | header table, id | "every result's `prereg_id` is `RD-04` (section 13)" | this file's id at the pin (0.2); every result's `prereg_id` is it (S-10) |
| D-03 | L52 | header table, development data | "NQ 1-minute bars, 2020-01-02 to 2026-07-16" | NQ 1-minute bars, 2020-01-02 to 2023-12-29, for (c) only, cut at the read (S-1, S-2); (a2) reads none (S-18) |
| D-04 | L53 | header table, the unit | "(c) one start day as U1 replays it, and one gate path" | (c) one search-year start day as U1 replays it, stopping at the cut (S-6), and one gate path on the search-year pool (S-9) |
| D-05 | L54 | header table, blocks | "the late block from 2024-01-02 beside" | (a2): Q-121's years and quarters, 2020 to 2023; (c): all search-year starts the headline, the first and second halves beside, start years 2020 to 2023 beside (S-6, S-7) |
| D-06 | L55 | header table, cells | "(a2): one pass over the window" | (a2): no pass of its own, Q-121's file (S-18); (c)'s cells unchanged |
| D-07 | L57 | header table, the parent's purposes | "(a2): one purpose, `volatility_descriptive`" | none of the judged-block form (S-11); (c) under `registered_design` on the search years only (S-19) |
| D-08 | L83-L84 | 0.2, what stays fixed | "the frozen choices: P-14's rung by hour, P-16's admitted marks, the state table, the verdict arm's per-R shift" | frozen from the k = 1 cut build: P-16's admitted marks its registered set (S-3), the shift S-5's |
| D-09 | L140-L142 | 1, its job, (a2) | "in percent by year and quarter over 2020-2026" | in percent by year and quarter over 2020-2023, from Q-121's file (S-18); the rise into the held-out years is not described here (section 1) |
| D-10 | L143-L144 | 1, its job, (a0) | "what Stage 2's registered gate files already hold" | the gate files' search-year rows only (S-17) |
| D-11 | L154-L158 | 1, the leak | "**The leak, stated first (section 9.3).**" | no leak clause (S-20) |
| D-12 | L175 | 2, U1, Q-05 and program U | "late development, not out of sample" | those reads were of the held-out years; S-12's entries; none read here (S-13) |
| D-13 | L176 | 2, Q-121 | "its run queued, at this text" | its run collected (E-177); its file is (a2) here (S-18) |
| D-14 | L178-L181 | 2, the gate files' rows | "and none is read before step 2 of this reading's run" | only their search-year rows are ever read, at step 2 (S-17); the later periods' rows never loaded |
| D-15 | L218-L227 | 3.1, (a0), whole | "(a0): the gate files' existing rows, read as they stand" | replaced in whole by S-17: the `drift` rows of 2020 to 2023 and the `period` row `2020-2022` only |
| D-16 | L229-L316 | 3.2, (a2), whole | "(a2): the bars-only descriptive on the whole window" | replaced in whole by S-18: (a2) is Q-121's file, read as it stands, no bar read, no module run, no `volatility_descriptive` purpose; the factors read its `session` rows |
| D-17 | L357-L361 | 4.2, L_ref | "(a2)'s choice-block rows must equal that file's (8.2)" | (a2)'s rows are that file's (S-18): L_ref computed once, from it |
| D-18 | L362-L363 | 4.2, the year factor | "L_y is the same median over year y's rows (2026's to 2026-07-16)" | L_y over year y's rows, y from 2020 to 2023 only (S-1, S-19) |
| D-19 | L416 | 4.4, the frozen inputs | "Each from the registered build on the actual bars (the k = 1 build of section 8.1, which must equal the registered)" | each from the k = 1 build on the cut (S-2), held to the registered design by S-4's nested cut and S-8's point-arm equality |
| D-20 | L422 | 4.4, P-16's offers | "at most 5 % unresolved over the window at every offered R" | P-16's registered mark set (S-3), never re-resolved; the other cuts and sides as the parent says |
| D-21 | L424 | 4.4, the verdict arm's shift | "the era rule at its registered seed" | the era rule with the halves as eras (S-5) on the k = 1 cut build, at the registered seed |
| D-22 | L425 | 4.4, the day capacity | "each design's busiest day's offers (D-469)" | each design's busiest search-year day's offers on the k = 1 cut build |
| D-23 | L432 | 4.4, `k1`'s twin | "`k1`'s twin is the registered one, as 8.1 item 4 reproduces it" | `k1`'s twin is its cut build's; 8.1 item 4's reproduction of the registered gate paths stays a reproduction identity (S-8) |
| D-24 | L436 | 4.4, the bounds beside | "the registered era seed" | the registered era seed and S-5's eras |
| D-25 | L448 | 4.5, pitfall 3 | "P-16's marks are taken from the registered build on the actual bars (4.4)" | P-16's marks are its registered set (S-3) |
| D-26 | L484 | 4.6, the builders | "P-16's recomputes its cutoff from its own walk" | P-16's cutoff returns the registered set for the call (S-3) |
| D-27 | L508 | 5 item 1 | "**(a2)'s unit** is the session; its summaries by calendar year and quarter, whole window" | (a2)'s unit is Q-121's session, its summaries 2020 to 2023 (S-18) |
| D-28 | L509-L514 | 5 item 2, (c)'s unit, starts and gate | "one development start day" | one search-year start day; the starts every start U1 reads inside the search years, h inside them (S-6); the gate's paths drawn from the search-year pool (S-9) |
| D-29 | L515 | 5 item 3, the arms | "every R shifted by 4.4's frozen `lb - e`" | every R shifted by S-5's search-year `lb - e` |
| D-30 | L527-L533 | 5 item 5, the blocks | "late block** (`u_select.block(records, "late", h)`, from 2024-01-02)" | all, first and second (S-7), each at its measure's h; by start year 2020 to 2023 |
| D-31 | L534-L567 | 5 item 6, the seal and the parent's purposes | "The judged block's seal (E-026, E-041, E-037)." | replaced by S-11 and S-19: no judged-block purpose; (c) under `registered_design` on 2020-01-02 to 2023-12-29, its three refusals reading this file's pin; (a2) no read (S-18); (a0) as S-17 |
| D-32 | L568 | 5 item 7 | "No NQ from 2026-07-17" | this reading takes no NQ after 2023-12-29 (S-1); NQ from 2026-07-17 is not on disk and never read |
| D-33 | L572-L575 | 6.1, (a2) | "One pass over every development session" | no pass: (a2) is Q-121's file (S-18) |
| D-34 | L581 | 6.2, `k1` | "reference (identity)" | reference; its point-arm rows checked as S-8 says; its registered reproduction identity unchanged |
| D-35 | L602-L603 | 6.4 item 3 | "the references' gates are 8.1's identities" | `k1`'s two search-year gates run beside as the pairs' references (S-9); the registered gate paths stay 8.1's reproduction identities |
| D-36 | L604-L608 | 6.4 item 4 | "**28 reference checks**" | twenty-eight point-arm replays of `k1`, for the checks alone, against Q-44's point-arm rows on the starts whose 252-session replay ends inside the search years (S-8) |
| D-37 | L609 | 6.4 item 5 | "**Every block read** is recorded as read for volatility description" | S-14 |
| D-38 | L612-L614 | 6.4, in all | "one descriptive pass; two files' rows" | no descriptive pass (S-18); two files' search-year rows (S-17); (c) as counted, `k1`'s two search-year gates added (S-9) |
| D-39 | L634 | 7, arms | "`verdict` the headline, `point` beside" | `verdict` at S-5's frozen search-year shift the headline, `point` beside |
| D-40 | L637 | 7, horizons and blocks | "all, early, late" | all, first, second (S-7) |
| D-41 | L674-L675 | 8.1 item 1 | "on every development session the wrapped callable's four arrays equal" | on every search-year session (S-8: it reproduces no registered file) |
| D-42 | L693-L694 | 8.1 item 6 | "P-14's and P-16's trades built with `sc` at k = 1 equal those built with `act`" | on the cut build, the search years only (S-8) |
| D-43 | L703-L704 | 8.1, inside (c)'s run | "`k1`'s start rows equal U1's again" | on the **point arm only**, on the starts whose 252-session replay ends inside the search years (S-8) |
| D-44 | L711-L726 | 8.2, (a2)'s identity, whole | "(a2)'s identity, refusing, before the judged block is read" | replaced in whole by S-18's check: Q-121's file against E-177's sha256, its manifest and its row, refusing |
| D-45 | L738-L740 | 8.3, the factors | "recomputed in step 3 from (a2)'s session rows equals the file's" | recomputed in step 3 from Q-121's session rows equals step 2's `factor` section; every L_y equals Q-121's `range` row (S-19) |
| D-46 | L782-L783 | 9.1, (a0) and (a2) | "the rows of sections 3.1 and 3.2, by year and quarter" | (a0)'s search-year rows (S-17) and Q-121's rows by year and quarter, 2020 to 2023 (S-18) |
| D-47 | L785 | 9.1, (c) | "every block of section 5" | every block of S-7 |
| D-48 | L793 | 9.1 item 2, the guard row's gate entry | "`k1`'s entry from its design's registered gate row" | `k1`'s entry from its search-year gate (S-9) |
| D-49 | L812-L815 | 9.1 item 7, the gate | "paired with the registered paths" | paired with `k1`'s search-year gate at the same seed (S-9) |
| D-50 | L855-L937 | 9.3, the leak clause, whole | "The leak clause (E-157; the note's 4 (a), "The leak, stated")" | not this file's (S-20); the parent's clause and its test stay the parent's, binding nothing while it is unrun |
| D-51 | L941-L942 | 10, it delivers | "(a2)'s description by year and quarter" | Q-121's description by year and quarter, 2020 to 2023 (S-18), (a0)'s search-year rows, (c) on the search years |
| D-52 | L946-L947 | 10, (a2)'s identity fails | "(a2)'s identity fails (8.2)" | Q-121's file fails S-18's check: (c) does not run (its factors come from that file); the failure protocol applies |
| D-53 | L982-L986 | 11, step 3's draws | "so their paths pair with the registered ones" | so each cell's paths pair with `k1`'s search-year gate's (S-9); the beside bounds' era bootstrap at the registered era seed with S-5's eras |
| D-54 | L987-L989 | 11, step 4's draws | "so `k1`'s ladder rows reproduce Q-44's" | so `k1`'s point-arm check replays reproduce Q-44's point-arm rows on the starts whose 252-session replay ends inside the search years (S-8) |
| D-55 | L1024 | 12.1, A-4 | "(a2) through Q-121's module with the reader's `Authorisation` (3.2)" | (a2) Q-121's file checked and read (S-18); no module call, no `Authorisation` |
| D-56 | L1030 | 12.2, T-0 | "`tests/test_rd04_draft.py`, in RD-03's form" | the parent's T-0 stays for the parent's text; this file's T-0 is `tests/test_rd_search_years_drafts.py` (with this text), extended at the pin, the checks RD-06's section 7 lists |
| D-57 | L1040 | 12.2, T-10 | "(a2)'s order and its reads" | replaced by T-10S (B-8): (a2) reads no bar and refuses a Q-121 file not at E-177's sha256 |
| D-58 | L1042 | 12.2, T-12 | "refused when `prereg/RD-04_volatility_drift.md` does not hash to the pinning row's pin" | refused when this file does not hash to its pinning row's pin (S-19) |
| D-59 | L1045 | 12.2, T-15 | "`tests/test_rd04_leak_clause.py`, the leak-clause test of 9.3" | the parent's, not this file's (S-20) |
| D-60 | L1049-L1090 | 13.1, files and manifests | "**`results/rd04_descriptive.csv`** (step 2), sections:" | replaced by S-10's files: `results/rd04s_descriptive.csv` (`identity`, `a0`, `factor`), `results/rd04s_replay.csv`, `results/rd04s_replay_gate.csv`, `results/rd04s_replay_beside.csv`; Q-121's sections cited by path and sha256, not copied; `prereg_id` this file's id |
| D-61 | L1100-L1106 | 13.2 step 2 | "**(a0) and (a2)** (`scripts/rd04_descriptive.py`)" | step 2 is (a0)'s search-year rows (S-17), Q-121's file checked (S-18), the factors, `results/rd04s_descriptive.csv`; no bar read, no purpose, no `RD-04 read: step 2` token (S-20) |
| D-62 | L1107-L1112 | 13.2 step 3 | "purpose `registered_design`, the pinning row, P-14 and P-16" | on 2020-01-02 to 2023-12-29 only, the pinning row this file's (S-19); S-4 first; `k1`'s rows against U1's on the point arm (S-8) |
| D-63 | L1113-L1117 | 13.2 step 4 | "responses against Q-44's per-start file first, refusing" | `k1`'s twenty-eight point-arm check replays against Q-44's point-arm rows first, refusing (S-8) |
| D-64 | L1123-L1125 | 13.2, weight | "(a2)'s one pass over" | no (a2) pass (S-18); the walks over the search years |
| D-65 | L1136-L1138 | 13.3, Q-121's file | "**Q-121's file on master**" | met: collected under E-177; the wait is S-18's check |
| D-66 | L1139 | 13.3, the leak-clause test | "**the leak-clause test**" | not this file's wait (S-20) |
| D-67 | L1150-L1151 | 14 item 1 | "**T-0** (`tests/test_rd04_draft.py`) and" | this file's T-0 (section 7); T-15 the parent's (S-20) |
| D-68 | L1159-L1161 | 14 item 4 | "**The leak clause as the lead's program rule** (9.3)" | not adopted (S-20) |
| D-69 | L1165-L1166 | 14 item 6, (a0)'s home | "their rows span the judged block, so they are read under this reading" | only their search-year rows are read, under this reading (S-17) |

## 4. Unaffected, because

Every other line the search of section 7 finds in the parent, with the reason it needs no change, grouped by the
parent's sections.

- **L1, L7, L8, L9, L10, L12, L16, L18, L25, L36, L37, L38, L39, L40, L41, L56, L58, L60**: the parent's status, history and header (before section 0): records and the frame; the window rows are D-01 to D-07
- **L77, L82, L89, L91, L92, L99, L100, L101, L102, L103, L104, L105, L107, L108, L109, L110, L112, L115, L116, L122, L123, L124, L125, L126, L127, L128, L131, L132**: what each part changes (section 0): the map's terms and the frozen choices' kinds, unchanged (their values D-08); the tables of changes between the parent's texts are records
- **L145, L148, L152**: what the reading is (section 1): its questions and labels; its windows are D-09 to D-11
- **L164, L166, L167, L168, L169, L170, L171, L172, L173, L174, L183, L186, L187, L188, L189, L191, L192, L193, L198, L199, L200, L203, L207, L208, L211, L212, L213**: prior exposure and the drafter's disclosed reads (section 2): records; the whole-window reads among them are S-12's entries (D-12 to D-14)
- **L318, L335, L339, L350, L351, L352, L355, L367, L368, L371, L372, L373, L375, L376, L381, L383, L384, L386, L393, L395, L407, L421, L427, L428, L430, L434, L435, L437, L444, L445, L446, L447, L451, L452, L455, L457, L458, L463, L464, L468, L469, L470, L471, L483, L488, L491, L494, L497, L500, L502, L503**: (c)'s map, factors' definitions, cost readings, frozen inputs' kinds, pitfalls and adapters (section 4): rules, unchanged; their windows and values are D-17 to D-26 and S-2 to S-5
- **L506, L516, L518, L519, L520, L521, L522, L523, L524, L525, L526**: data, blocks, the unit and the horizons (section 5): the pairing, the horizons and the definitions, unchanged; the windows are D-27 to D-32
- **L582, L583, L588, L589, L590, L594, L616, L618, L622, L625, L626, L627, L628, L629, L631, L632, L633, L635, L636, L638, L642, L643, L644, L648**: the cells, the runs and the parameters (sections 6 and 7): names, kinds and counts, unchanged; the windows and counts that change are D-33 to D-40
- **L653, L655, L658, L659, L660, L662, L663, L665, L666, L668, L669, L677, L679, L681, L682, L683, L684, L685, L686, L687, L688, L689, L690, L692, L698, L700, L701, L706, L735, L736, L737, L744, L746, L747, L748, L749, L751, L752, L761, L762, L764, L765, L766, L767, L768, L771, L772, L773, L776**: the identities, oracles and mechanics (section 8): the shared identities and `rd04_identity`'s items 2 to 5 unchanged (S-8); the oracles' bounds and the mechanics' counts are rules, read on the search years
- **L787, L791, L792, L794, L797, L800, L802, L803, L804, L805, L806, L807, L810, L816, L817, L820, L821, L823, L833, L836, L837, L839, L840, L841, L842, L843, L844, L845, L846, L847, L848, L849, L850, L853**: the reading and its uncertainty (section 9): measures, windows of h starts and the honesty seed, read on S-6's starts and S-7's blocks
- **L948, L950, L952, L955, L956, L960**: what the reading delivers (section 10): unchanged, on the search years (S-15)
- **L966, L967, L968, L969, L970, L971, L972, L973, L974, L975, L979, L980, L991, L994, L996, L1000, L1002, L1004, L1007, L1008, L1010, L1011, L1012**: the seeds and their check (section 11): inherited unchanged and by reference (section 8); the digits of a seed are not a date
- **L1021, L1022, L1023, L1031, L1032, L1033, L1034, L1036, L1037, L1038, L1041, L1043, L1044**: the adapters and tests (section 12): unchanged but as D-55 to D-59 say
- **L1098, L1121, L1134, L1135, L1140, L1142, L1144**: the outputs, the run and its waits (section 13): bounds and waits as the parent states them, the replay's inputs cut by S-2
- **L1152, L1153, L1157, L1162, L1163, L1169**: open before the pin and chosen after (sections 14 and 15): the parent's pin record and items; unchanged but as D-67 to D-69 say
- **L1187, L1188, L1190, L1192, L1195, L1196, L1197, L1198, L1199, L1200, L1201, L1202, L1203, L1204, L1205, L1206, L1207, L1208, L1209, L1211, L1212, L1213, L1214, L1215, L1216, L1217, L1218, L1219, L1220, L1221, L1223, L1224, L1225**: Appendix C, the drafter's choices: records of the parent's choices; each operative rule is cited at its own line or governed by section 2

## 5. What does not change

The parent's question and what it is not (section 1, on the search years); (c)'s map, its anchor and its oracles (4.1);
the population, the statistic, L_ref's span and the year and trailing factors' definitions (4.2), on the years 2020 to
2023; the two cost readings (4.3); what is frozen and why (4.4), its values the cut k = 1 build's (S-3 to S-5); the
pitfalls and their answers (4.5); how it is built without touching `vendor/` (4.6), the cut wrapper added (S-2); (c)'s
unit, arms, pairing and horizons (5), on the search years; the grid and the comparisons (6.2, 6.3); the counts of (c)
(6.4): 10 replays on two arms, 8 gates, 72 replays beside, with `k1`'s two search-year gates added beside (S-9) and
the 28 reference checks now point-arm replays (S-8); the parameters' classes (7); the shared identities and
`rd04_identity`'s items 2 to 5 (S-8); the oracles (8.3) and mechanics (8.4) on the search years; (c)'s reading and
uncertainty (9.1, 9.2) on S-6's starts and S-7's blocks; what the reading delivers (10), on the search years; the
seeds (section 11), inherited unchanged and by reference (section 8); the adapters A-1 to A-4 and the tests T-1 to T-9
and T-11 to T-14 (12), T-0, T-10, T-12's pin and T-15 as section 3 says; the run's steps 1, 3 and 4 and their bounds
(13), step 2 as S-17 and S-18 say; the operator's items (14).

## 6. The build list (for a later item; nothing here is built by this one)

- **B-1. The declaration.** RD-10's files (`extended/rd04_reading.py`, `extended/rd04_replay.py`,
  `scripts/rd04_descriptive.py`, `scripts/rd04_replay.py`, `identity/rd04_identity.py`, none built yet) name this file
  at its pinned name; `scripts/rd04_replay.py`'s second refusal reads this file's pin; no file calls Q-121's module in
  its authorised mode or authorises `volatility_descriptive`; `extended/vol_descriptive.py` (Q-121's frozen module,
  its sha256 tying Q-121's file) is not edited. T-0's code check (N-1) then passes in its after-pin form.
- **B-2. The cut** (S-2): RD-06's B-2 shared module, its bar wrapper composed under the parent's A-1 map.
- **B-3. The blocks** (S-7): the shared repository block function (`all`, `first`, `second`).
- **B-4. P-16's marks and the frozen shift** (S-3, S-5): the shared marks wrapper; the halves as the eras for
  `atlas_a3.bounds` in the k = 1 cut build and in `bounds_beside`.
- **B-5. (a0) and (a2)** (S-17, S-18): the line-by-line gate-file reader admitting only the search-year rows; Q-121's
  file checked against E-177's sha256 and its manifest, refusing; the factors from its rows; `results/rd04s_descriptive.csv`.
- **B-6. The checks** (S-4, S-8): the nested cut before any cell; `rd04_identity`'s items 1 and 6 on the search years,
  items 2 to 5 as the parent states them; `k1`'s point-arm comparison with U1's rows; step 4's twenty-eight point-arm
  replays of `k1` against Q-44's point-arm rows.
- **B-7. The gate** (S-9): each new cell's gate paired with its design's `k1` search-year gate, the two `k1` gates run
  first.
- **B-8. Tests:** T-0 (`tests/test_rd_search_years_drafts.py`, in pin-time form; the parent's `tests/test_rd04_draft.py`
  stays for the parent's text); a T-10S replacing the parent's T-10 -- (a2) reads no bar, refuses a Q-121 file whose
  sha256 is not E-177's, and no RD-10 file constructs an `Authorisation` or names `volatility_descriptive`; T-12 against
  this file's pin; B-5's reader on a toy gate file (a held-out row never kept, a mistyped period refused); RD-06's
  shared wrapper, marks and nested-cut tests.

## 7. The search that found section 3 (re-runnable)

Every line of the parent's LF text that matches any of these patterns (Python regular expressions, case-insensitive),
one per line between the markers, is cited in section 3 or listed in section 4 -- `tests/test_rd_search_years_drafts.py`
checks it, and checks that the patterns below are the test's own (the siblings' first nineteen terms and the red
team's extra terms). T-0's other checks are listed in RD-06's section 7; each is a function that
`test_the_checks_can_fail` calls on a planted fault.

<!-- search-terms -->
```
\b202\d\b
\blate\b
\bearly\b
judged
held.out
\bseal
whole.{0,12}window
development (?:window|data|start|reading)
\bu_select\b
program U
\bblocks?\b
choice block
search.years
out.of.sample|in-sample
sessions left|sessions remain
every start|all starts|all the block
\byears?\b
\bhistor
calendar
\b20\d\d-\d\d-\d\d\b
\bU1\b
\bgate
\bbound|lower.bound|\blb\b|e_by_rr|lb_by_rr
\bshift
Q-44
Q-17
Q-121
RD-0[1-5]
results/|\.csv|\.parquet
\beras?\b
capacity|busiest
cutoff|\bmarks?\b|rung
registered
\b\d{3,4} sessions|\bsessions\b
start days?|\bstarts\b
\bwindow
q82|judged_sessions
volatil|regime|drift|\bATR\b|normalis
estimat|fitted|\bfit\b
identit
count of|counted on|releases?\b
reader|authoris|purpose
D-6\d\d|D-5\d\d
\blast\b|\bfinal\b|\brecent\b|to date|2026
\bbeside\b
```
<!-- end search-terms -->

To re-run: `python -m pytest -q -o addopts= tests/test_rd_search_years_drafts.py`; its `parent_hits` lists the lines.

## 8. Counting, seeds and confirmation

- **Counting.** No program family number and no level (E-023 (1)); the next numbered family's k is unchanged. (a2) is
  no pass of its own (S-18); (a0) is two files' search-year rows; (c)'s counts hold (section 5), with `k1`'s two
  search-year gates added beside (S-9) and the 28 reference checks now point-arm replays (S-8). The parent is never
  run (0.3), so nothing is counted twice.
- **Seeds.** The parent's section 11, inherited unchanged and by reference (its block, statuses and inherited seeds,
  the era seed among them); no seed is restated here, so the parent's T-0 still finds its block in no other
  declaration. The parent was never run, so none of its seeds has been drawn on the bars. Step 2 draws nothing.
- **Confirmation.** None: nothing is carried; NQ from 2026-07-17 is never read.

## 9. At the pin

1. **The reads.** The red team's read of its siblings (M-3, which brought this text) and its re-read (`docs/reviews/O7_SEARCH_YEARS_2026-11-19.md` and its re-read `docs/reviews/REREADS_W32_W34_O7_2026-11-20.md`),
   every finding answered as the lead ruled on it (rm-4, rn-5), and the gatekeeper's form findings answered in this
   text.
2. **The pin** is a byte-identical rename of this text to `prereg/RD-10_volatility_drift_search_years.md`. The pinning
   row names P-14 and P-16 (it is (c)'s `registered_design` declaration, S-19), records the parent as superseded,
   never run, and records that no `heldout-read` row is written for `scripts/rd04_replay.py` before NQ's verdict (the
   red team's M-3); CHARTER 3.6 (b)'s entry "RD-04 (c): P-14 and P-16 replayed on the late block" then reads "declared,
   not run".
3. **`rd04_identity`'s items 2 to 5** (S-8) keep their declared whole-window form, labelled so (the lead's ruling rn-5).
4. **S-2's feasibility** is a build question (RD-06's); its stop-and-report clause is declared.
