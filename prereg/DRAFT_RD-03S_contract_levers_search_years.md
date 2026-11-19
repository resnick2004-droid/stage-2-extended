# DRAFT RD-03S: contract-use levers on the registered trades, on the search years only (reading CL-S) -- a delta declaration of RD-03, a described reading, unnumbered (E-023 (1))

**Status: a draft, not pinned (O-7, the lead's ruling in E-221); the second text.** The first text (wt/wt-firms, the
O-7 commit) was read by the red team (`docs/reviews/O7_SEARCH_YEARS_2026-11-19.md`, two blocking findings, B-1 and
B-2); this text answers every finding as the lead ruled on it (section 0.4). It re-declares
`prereg/RD-03_contract_levers.md` on the search years alone, so that no part of the reading touches NQ's held-out years
(E-208), which E-221 (O-1) keeps for one joint fixed-sequence confirmation across firms. The parent is not edited: it
stays on record, pinned, and is never run (section 0.3). The lead assigns its id at the pin (section 0.2). Its
siblings state the same general replacements for RD-01, RD-02, RD-04 and RD-05's part F; each draft is complete on its
own.

| field | value |
|---|---|
| id | proposed **`RD-08`** at the pin (section 0.2); until then `RD-03S` |
| parent | `prereg/RD-03_contract_levers.md` sha256 `9a22532d3a32eebf412afccd5b0e0f47a0479cb3699e9e0d76a6629d9d8fb803` (of its LF text), pinned by E-152 |
| reading | CL-S: the parent's reading CL, stage 0 and every cell, run and reading as the parent declares them, on the search years |
| kind | a **described reading** (E-023 (1), E-134 (1)): never carried; no program family number, no level, no pass line, no pick |
| development data | NQ 1-minute bars, 2020-01-02 to 2023-12-29 (the search years, E-208), read only inside Stage 2's engine by P-14's and P-16's registered builders, cut at the read (S-2) |
| held-out years | 2024-01-02 to 2026-07-16: never read by this reading, under any purpose (S-1, S-11) |
| blocks | all search-year starts (the headline); the search years' first half and second half beside, each per measure at its h (S-7) |
| judged-block purposes | none (S-11) |
| stage 0 | on the search years' bound edges and rungs (S-17); the zero edge set unchanged |
| confirmation | none; NQ from 2026-07-17 never read |
| the build | not built by this item: section 6 is the build list for a later item |

## 0. What this file is, and how it reads its parent

### 0.1 The incorporation

This declaration **is the parent's text, with the replacements below**. Every section, table, rule, cell, count,
seed, oracle, test and wait of `prereg/RD-03_contract_levers.md` at the sha256 above is part of this declaration, read
with:

1. the general replacements S-1 to S-17 (section 2), which apply wherever the parent's words reach them;
2. the line-by-line replacements of section 3, each citing the parent's line and a short quote from it.

Where a replacement and the parent's words differ, the replacement is the declaration. Where section 3 is silent on a
parent line, section 2 governs it; where both are silent, the parent's words stand (section 5 lists what stands, and
section 4 lists every line the search of section 7 found that needs no change, with the reason). Section numbers,
item numbers, cell names, run names and test names are the parent's. **The labels S-1 to S-17 are this file's; the
parent's own labels (its gaps G-1 to G-9, its unstated terms U-1 to U-8, its adapters A-1 to A-6, its rules G-B and
G-N) keep the parent's meaning** (the red team's m-1). Where the parent cites RD-02's section 9.2 for its method
(10.2), that method is window-free and stands as RD-02 pins it.

### 0.2 The id scheme (proposed; the lead assigns at the pin)

RD-06 for RD-01's delta, RD-07 for RD-02's, **RD-08 for this file**, RD-09 for RD-05's part F, RD-10 for RD-04's, in
the order of the parents. The pinned name is `prereg/RD-08_contract_levers_search_years.md`; it matches no other
reading's T-0 glob (the parent's T-0 takes `*contract_levers.md` with its two exact names). **New numbers, not a
suffix**: the reader takes a declaration's id from its path as `RD-` and digits (`extended/reader.py`'s
`DECLARATION_ID`), so a manifest, ledger or token naming `prereg/RD-03S_...` would be attributed to RD-03 (the red
team's m-9).

### 0.3 The parent, superseded before any run

No result of the parent exists: the read ledger holds no line of RD-03 and no file `results/cl_*.csv` exists at this
draft. At this file's pin the parent is **superseded, never run**: no run takes its four purposes, neither stage 0 nor
any step runs under it, its result files are never written, and its id is never a manifest's `prereg_id`. The reader
cannot see a withdrawal (the audit's R-8 registry is not built), and its held-out rule 4 refuses the parent's judged
reads only until a market's verdict row exists; so the supersession is enforced by the build (section 6, B-1), held
now by T-0's code check (N-1), and recorded in the pinning row. RD-09 (RD-05's part F) reads its `TS-N` rows from this
file's `naf` cells; the cross-reference is made in RD-09's text at its pin and in the pinning row (the red team's m-2).

### 0.4 What changed from the first text (the red team's read, as the lead ruled on it)

| finding | the first text | this text | where |
|---|---|---|---|
| B-1 | `ref`'s rows compared with U1's and Q-44's verdict-arm rows; the `naf` cells' Focused Trader rows read from Q-44 | every comparison with U1's or Q-44's rows, and every citation of them, on the **point arm only**: `ref`'s fourteen response checks run on the point arm (twenty-eight replays for the check alone); `naf`'s reading re-derived from Q-44's point-arm per-start rows | S-8; D-33, D-34, D-39, D-57, D-62, D-63 |
| B-2 | P-16's marks re-resolved on the cut; a cut identity reading the whole window, and an item (d) reproducing the gate files' rung rows from the whole window | P-16's offered marks fixed to its registered set (S-3); a nested cut inside the search years (S-4) and B-1's point-arm equality; no new identity reads 2024 or later, so item (d) is gone and stage 0's search-year rungs are held by a synthetic test | S-3, S-4, S-8, S-17 |
| M-1 | P-11's eras on the cut, 2023 alone | the halves, 2020-21 and 2022-23, as the eras, declared; stage 0's bound edges the same constants | S-5, S-17 |
| M-2 | missed lines; D-652 and E-125 absent from the ledger | the red team's extra terms added (section 7); L166, L328, L532 and L772 cited (D-58 to D-61); D-652 (U2) and E-125 (Q-18) added to S-12 | sections 3, 4, 7; S-12 |
| m-8 | "the table files ... design constants, no data" | "registered, inherited, S-12": the v12 table offers each R on its availability share of days, an empirical share | S-17 |
| m-1 to m-9, N-1 | as in RD-06's 0.4 | the labels; the wrapper's reads and switched-off checks; the no-op guard; the verdict-arm halves labelled; T-0 rebuilt; the id reason; the code check | throughout |

## 1. Why, and what it does to what the reading can show (E-051)

**Why.** Under E-208 every choice and every map the journey search draws on is made on the search years, and the
held-out years are read once, by the joint confirmation (E-221, O-1). The parent reads the whole development window,
its late block by name and its judged-block purposes, and its stage 0 rests on whole-window edges; CHARTER 3.6 (b) lists
"RD-03's whole-window lever readings" among the reads a search must carry. O-7 rules that the reading is re-declared on
the search years, so its rows can bound a lever range (CHARTER 3.3 (a)).

**What it does to what the reading can show.** The menu describes the search years only. Each measure's starts at its
horizon h are fewer (S-6), so the headline holds fewer kept windows and more readings print "too few separated windows
for an interval"; each half (S-7) holds about two years, so most half readings at months 6 to 12 print the sign count
alone -- and the levers that bind only after a lost funded account (Back2Funded) are the rare, lumpy differences that
fewer windows resolve least. The stability flag compares two halves of four years. The verdict arm's shift and stage
0's bound edges are the search years' own, with the halves as eras (S-5, S-17), and the verdict arm's halves share them
(S-7). Nothing else changes: the levers, the grid, the counts, the uncertainty method and the oracles are the parent's.

## 2. The general replacements

- **S-1. The window.** The development data are NQ 1-minute bars from 2020-01-02 to 2023-12-29, the search years
  (E-208). The held-out years 2024-01-02 to 2026-07-16 are never read by this reading, under any purpose, by stage 0,
  any of its runs, gates, checks, or beside readings; NQ from 2026-07-17 is never read. Wherever the parent says "the
  development window", "2020-2026" or "the whole window" of what this reading reads, read the search years. A pinned
  calendar (E-029, E-050) is used only on days inside the search years.
- **S-2. The cut at the read.** No bar or atlas row dated after 2023-12-29 reaches any function of the registered
  builders, stage 0, the replay, the gate or the reading. **The guard is the wrapper and the refusal below**: the
  reader's `authorise_engine_read` on 2020-01-02 to 2023-12-29 with no purpose checks the dates only and writes
  nothing, and the reader cannot see reads made inside vendored calls (the red team's m-4). The wrapper acts, for the
  builders' calls only, on exactly these inputs, and restores each after the call (nothing vendored is edited):
  1. **the bars**, `propedge.data.bars.read_bars` as `atlas_a3.bar_arrays` calls it: its last date clamped to
     2023-12-29;
  2. **A1's events and days**, the two `pd.read_parquet` reads of `a3_resolution_map.load_a1`: the rows dated after
     2023-12-29 dropped from the frames it returns. **The manifest it checks is not cut**: `load_a1` compares the bars
     manifest's day count and last day with the A1 cache's manifest (its `day_list`), and both stay whole;
  3. **A3's walks**, the `pd.read_parquet` of `atlas_a3.cached_walk`: the rows dated after 2023-12-29 dropped;
  4. **the day list** each builder passes to the walk and the bounds: cut at 2023-12-29.

  **The vendored checks switched off on the cut, and no others:** (a) `rc_dev_test.trade_problems` as
  `user_journey.build_p16` calls it -- P-16's trades against `rc_width_screen.csv`'s cell row and the registered content
  hash, whole-window facts that cannot hold on four years; (b) where the build calls it, `a3_brk30`'s check that the
  configured eras are P-11's ("the bounds are ..., not P-11's"), since S-5 passes the halves as the eras. Each switched-
  off check is named in the run's manifest. The day blocks and dates handed to the replay and to the gate end at the
  search years' last session, and **the runner refuses, before any replay, any block or date after 2023-12-29**. **If a
  registered builder cannot be cut at these reads, or another vendored check fails on the cut, the build stops and
  reports; this declaration does not fall back** to a whole-window build cut afterwards, and switches off no other
  check.
- **S-3. P-16's offered marks, fixed to its registered set** (the lead's ruling on B-2). P-16's builder admits a mark by
  its unresolved share pooled over every day it is given (`resolved_coin.mark_resolution`), so on the cut the shares
  would be the search years' and the marks could differ from the registered design's. Here the marks are **never
  re-resolved**: `resolved_coin.mark_resolution`, as `rc_width_screen.build` calls it at P-16's stop, returns for the
  call the registered table -- `vendor/stage2/results/rc_width_screen.csv` section `marks`, the rows at that stop, the
  columns `stop_ticks`, `slot` and `offered` only, the file checked first against `vendor/MANIFEST_stage2.sha256` --
  so `offered_marks` gives the registered set, whose count must equal the `rc_s150_all` cell row's `marks_offered`
  (refusing). The set is part of the registered design, a whole-window choice of Stage 2's, inherited and labelled in
  S-12's existing entry. P-14's rung map is already a pinned file (`atlas_a3.rung_rule`).
- **S-4. The nested cut, refusing** (the lead's ruling on B-2). Before any replay (and in stage 0's own process before
  its readings), each design's stream is built twice on the cut, with S-3's marks: on 2020-01-02 to 2022-12-30 and on
  2020-01-02 to 2023-12-29. Their **point-arm** day blocks must be equal up to 2022-12-30, block for block, every field,
  the per-R outcomes included. It reads the search years only, needs no purpose, writes its pass or fail lines to the
  run's log and manifest, and a failure stops the step. With S-8's point-arm equality it is the whole check that the cut
  stream is the registered design's. **No new identity reads 2024 or later**; the registered reproduction identities
  are untouched (S-8).
- **S-5. The verdict arm's constants, re-estimated on the search years, with the halves as eras** (the lead's ruling on
  M-1). The parent's "estimated on the whole development window ... a function of 2024-2026 through that one constant"
  (its section 3): here `e`, `lb`, `e_by_rr` and `lb_by_rr` are `atlas_a3.bounds`'s, as the registered builder calls
  it, on the search-year trades and days, at the registered trial count and era seed, **with its eras declared now as
  the two calendar halves, 2020-2021 and 2022-2023**, passed in the bounds' configuration for the call (P-11's spans
  would leave 2023 alone as an era). Each R's bound is the pooled one, or the lower era's when the whole-year bootstrap
  flags the eras. **Printed in every manifest, per design and R:** the flag, the bound read, the pooled bound and each
  era's. **Reason:** inherited, the constant would carry a held-out read into every verdict row and into stage 0's
  bound edges, and so into the lever space (CHARTER 3.3 (a)). The `point` arm is unchanged. The verdict blocks are
  `shifted_blocks` of the point blocks by these constants, which the runner's per-stream shift check holds.
- **S-6. The starts and the horizon embargo** (CHARTER 3.6 (d)). The starts are every start day U1 reads for `p14` and
  `p16` inside the search years. Each measure is read at its horizon h (the parent's section 5 table, unchanged) only on
  starts with h sessions inside the search years: on the cut replay a start observes no session after 2023-12-29, so
  `u_select.block(records, None, h)` gives exactly these. U1's long replay of up to 252 sessions and its exact-length
  runs stop at the cut. Wherever the parent says "every start" or "all starts" of what is replayed or read, read the
  search-year starts with the horizon left. By start year: 2020 to 2023, means only, not purged within the search years,
  2023's starts reading only 2023's sessions; labelled so.
- **S-7. The blocks: the late block replaced by the search years' second half.** On the cut replay the parent's early
  block equals the headline and its late block is empty, so both are replaced, per measure at its h:
  - **all**: every search-year start with h sessions inside the search years (the headline);
  - **first**: the starts of 2020 and 2021, each read at h only if h sessions remain before the first session of 2022
    (D-621 (4)(b)'s purge, moved to the half's end);
  - **second**: the starts of 2022 and 2023, read at h only with h sessions inside the search years.

  **On the point arm no first-half reading touches a second-half session. On the verdict arm the halves share S-5's
  constants, estimated on both halves** -- the kind of shared constant the parent's section 3 disclosed -- and every
  verdict-arm half row is labelled so. The flag "not stable across blocks" is printed on both arms; the point arm's is
  labelled "the halves share no constant". **Reason for the halves:** the flag needs two disjoint stretches read apart;
  two calendar halves of equal length, fixed by the calendar before any read and cut at a year's end as the parent's
  blocks were, keep it without reading a held-out day. At 12 months each half is close to one start year, so the flag
  there is weak; the start-year rows are the fuller description. The vendored `u_select.block` fixes its years, so the
  halves are a function of this repository (B-3). Nothing is chosen on any block. **Considered and not taken:** no
  blocks (it loses the flag); halves by start count (a cut that moves with the data).
- **S-8. The identities, the comparisons and the citations** (the lead's ruling on B-1). The parent's registered
  reproduction identities (`cl_identity`, 9.1; `cl_fit_identity`, 6.4) and the shared ones it waits for (Q-05, Q-80,
  Q-93 with Q-100, Q-101) are untouched: whole window or registered files, the purpose `identity`, their own rows,
  Stage 2's files reproduced, no outcome of any cell written, ledgered in a clean run. Inside the reading's own run:
  - **every comparison with U1's or Q-44's per-start rows is on the point arm only**, on the starts whose 252-session
    replay ends inside the search years, every column the parent names, refusing; no row of another arm or a later
    start is loaded. So 9.1 item 4's repeat compares `ref`'s point-arm start rows with U1's, and 9.1 item 6 runs `ref`
    under `denial_10`, `denial_25`, `denial_50`, `rtp` and the ten `ftp_*` responses **on the point arm, for the check
    alone** (twenty-eight replays, two bases by fourteen responses, read for nothing else) and compares them with
    Q-44's point-arm rows. The verdict arm is never compared with a registered file: its constants are the search
    years' (S-5);
  - **every citation of U1's or Q-44's rows is of their point-arm per-start rows**, on the same starts; a figure the
    parent reads from them (the `naf` cells' readings under the Focused Trader models, 4.5 and 10.1 item 8) is
    re-derived from those rows with the fees re-priced; Q-44's verdict rows and its pooled file `results/user_beside.csv`
    are never cited.
- **S-9. The gate on the search years.** Every gate beside draws its resampled days from the search-year day blocks
  only. Each new cell's gate is paired with its base's own search-year gate at the same seed and the same number of
  paths (the same pool of days, so the same day draws), not with the registered gate paths, which draw from the whole
  window. The two references' search-year gates are run and read beside as the pairs' references; the registered gate
  paths stay S-8's reproduction identities.
- **S-10. The outputs.** New files, never the parent's: `results/cls_fit.csv`, `results/cls_reading.csv`,
  `results/cls_gate.csv`, `results/cls_menu.csv`, each through `extended.results.write_result` with its sidecar
  manifest, `prereg_id` this file's id at the pin, the window 2020-01-02 to 2023-12-29, S-4's result, S-5's constants
  and flags, S-2's switched-off checks, S-12's list, the rows under which the parent's identities held, and every
  manifest field the parent's section 15 lists.
- **S-11. No judged-block purpose.** This declaration reads no day of the held-out years, so it names no purpose of the
  reader's judged-block form and carries no line of that form; the reader refuses any judged read citing it. The
  parent's line is the parent's and is never taken (0.3).
- **S-12. The held-out read ledger, inherited and labelled** (CHARTER 3.6 (b); no figure cited). This reading rests on
  designs and records that read the held-out years before it: P-14 fixed as R* from the whole window (Stage 2 D-626);
  P-14's rung map and P-16's mark cutoff resolved on the whole window (E-203 S-2), the latter fixed here as P-16's
  registered mark set (S-3); P-16's stop chosen on each block (Stage 2 D-554); the registered state table
  (`state_dp_e-0.050_lamstar_noclose`), whose model offers each R on its availability share of the development window's
  days (D-318), and the protocols, as Stage 2 registered them; Stage 2 U4's size fit at the registered bounds (D-666,
  D-667), which 6.4's identity reproduces; **Stage 2 U2's account lives after the opening on whole-window gate paths
  (D-652, `results/u_xfa_day_budget.csv`), the motivation of Back2Funded**; **Q-18's P-14 validation, whole window,
  under `registered_design` (E-125, `results/p14_validation.csv`), which the parent cites for the evaluation trades'
  mean**; program U's families 1, 3 and 5 on both blocks and its nine families' late-block reads of P; U1's whole-window
  start rows (Stage 2 D-620) and Q-44's per-start rows, which S-8 compares and cites on the point arm and search-year
  starts only; Stage 2's signal search over the whole window; and the parent's own pinned text, declared over the whole
  window and never run. Nothing here re-estimates them but S-5's and S-17's constants; every result file names them.
- **S-13. Prior exposure, re-read.** The parent's prior-exposure rows stand as records. Where a row's bearing reads "the
  late block has been read for P nine times: late development, not out of sample", read: those reads were of the
  held-out years; they are S-12's entries; this reading reads none of those years.
- **S-14. The binding.** The parent's "the blocks read here are recorded as read for contract-use levers on P-14 and
  P-16" reads: the search years, and their two halves, are recorded as read for contract-use levers on P-14 and P-16;
  the held-out years are not read by this reading and are recorded as unread by it.
- **S-15. In sample.** Every statement made from this reading, and the operator's choice from its menu, is a
  description of the search years, in sample, with no confirmation (E-023 (1)); the held-out years stay unread by it.
- **S-16. Reruns.** The reader ledgers no choice-block read, so its once-per-purpose refusal does not reach this
  reading. The parent's rule is kept by the lead: only the first complete clean run of each step is read; a restart or
  a rerun is recorded by the lead with its log under a decision row naming this file, which says which run replaces
  which and why; a result file is never overwritten (S-10).
- **S-17. Stage 0 on the search years.** The parent's stage 0 takes its `bound` edge set from "the gate's `lb_by_rr`"
  and each base's rungs from "its gate's `rung` and `resolution` rows" -- whole-window statistics in registered files.
  Here the `bound` edge set is S-5's search-year `lb_by_rr`, and each base's rungs (stops, shares and per-R
  availability) are computed by the vendored computation that writes those rows, on the search-year stream; the `zero`
  edge set and the registered policy are unchanged, and the state-policy configuration and the table files are
  **registered, inherited, S-12** (the table's model offers each R on an empirical availability share; the red team's
  m-8). Stage 0 therefore builds the streams on the cut (S-2), with S-4's nested cut first, in its own process, reading
  bars on the search years only, and runs no replay. 6.4's identity is unchanged (it holds the solver machinery to
  registered files at the registered edges, a reproduction identity, no outcome); the search-year rung computation is
  held by a synthetic test (B-5), since no new identity reads 2024 or later. **Reason:** the solver's view is printed
  beside the replay's rows; on whole-window edges it would be a function of the held-out years beside rows that are
  not. **If the rung computation cannot be composed without editing the vendored code, stage 0's `bound` edge set is
  not run** and its `zero` edge set alone is printed, labelled; stage 0 decides nothing either way (E-146).

## 3. Every dependency in the parent, line by line

The parent's lines as numbered in its LF text at the pinned sha256. A row's lines are one line, a range whose joined
text holds the quote, or a list of lines each holding the quote. The replacement is this declaration's.

| # | parent lines | where | quote | replacement |
|---|---|---|---|---|
| D-01 | L48 | header table, development data | "NQ 1-minute bars, 2020-01-02 to 2026-07-16" | NQ 1-minute bars, 2020-01-02 to 2023-12-29, cut at the read (S-1, S-2) |
| D-02 | L50 | header table, blocks | "the late block from 2024-01-02 (section 5)" | all search-year starts the headline; the first and second halves beside, each purged per measure (S-7) |
| D-03 | L53 | header table, the parent's purposes | "four purposes, on the line of section 5 item 6" | none (S-11); the identities from `identity/*.py` under their own row, unchanged (S-8); stage 0 reads the cut stream (S-17) |
| D-04 | L139 | 1, why described | "The judged block's few independent three-month stretches" | the same reason holds a fortiori on the search years: fewer independent stretches still (section 1) |
| D-05 | L144 | 1, the operator's choice | "a described development reading" | a described reading of the search years (S-15) |
| D-06 | L146 | 1, the operator's choice | "a description of the development window, in sample" | a description of the search years, in sample (S-15) |
| D-07 | L325, L326 | 3, program U families 1, 3 and 5 | "both blocks" | a record; held-out reads by Stage 2, entered in S-12 |
| D-08 | L334 | 3, Q-44 | "the bases' replays under the ladder, the placement and the ten Focused Trader models" | a record; Q-44's rows are whole-window, and S-8 compares and cites them on the point arm and search-year starts only |
| D-09 | L335 | 3, RD-01 and RD-02 | "other firms' contracts; payout policy" | a record; both parents are re-declared on the search years (`prereg/DRAFT_RD-01S_firm_contracts_search_years.md`, `prereg/DRAFT_RD-02S_payout_policy_search_years.md`); this reading reads none of their cells |
| D-10 | L336 | 3, U1 and Q-05 | "P-14's and P-16's own journeys, every start" | a record; the references' rows are whole-window, and S-8 compares them on the point arm and search-year starts only |
| D-11 | L337 | 3, program U's nine families | "late development, not out of sample" | those reads were of the held-out years; S-12's entries; none read here (S-13) |
| D-12 | L339-L342 | 3, the verdict arm's bound | "so an early-block reading on the verdict arm is a function of 2024-2026 through that one constant" | the verdict arm's constants re-estimated on the search years with the halves as eras (S-5); no reading is a function of the held-out years |
| D-13 | L342 | 3, the verdict arm's bound | "Stage 0's bound edges are the same constants." | stage 0's bound edges are S-5's search-year constants (S-17) |
| D-14 | L485 | 4.4, G-8 | "rule changes over 2020-2026" | rule changes over 2020-2023 (S-1); today's terms on every search-year start |
| D-15 | L524 | 5, its title | "Data, blocks, the unit and the horizons" | section 5 as items 1 to 6 are replaced in D-16 to D-23 |
| D-16 | L526 | 5 item 1 | "one development start day" | one search-year start day (S-6) |
| D-17 | L527 | 5 item 1 | "replayed in historical order, a long replay of up to 252 sessions" | replayed in historical order, a long replay of up to 252 sessions and U1's exact-length runs, stopping at the cut (S-6) |
| D-18 | L530-L531 | 5 item 1, the starts | "every start U1 reads for `p14` and `p16`" | every start U1 reads for `p14` and `p16` inside the search years, each reading on the starts with its h inside them (S-6) |
| D-19 | L533 | 5 item 3 | "the same start days, blocks and seeds" | the same search-year start days, S-7's blocks and the parent's seeds |
| D-20 | L535-L540 | 5 item 4 | "**the late block** (`u_select.block(records, "late", h)`: from 2024-01-02, h left)" | item 4 is S-7: all, first and second, each at its measure's h; by start year 2020 to 2023 (S-6); the flag on first and second |
| D-21 | L536-L538 | 5 item 4, the early block | "no early reading touches a 2024 session except through the verdict arm's bound" | no reading touches a session after 2023-12-29, and none through the bound (S-2, S-5); on the point arm no first-half reading touches a second-half session; on the verdict arm the halves share S-5's constants, labelled (S-7) |
| D-22 | L555 | 5 item 5 | "No NQ from 2026-07-17" | this reading takes no NQ after 2023-12-29 (S-1); NQ from 2026-07-17 is not on disk and never read |
| D-23 | L556-L560 | 5 item 6, the seal and the parent's purposes | "`levers_scorecard`, `levers_gate_beside`, `levers_ladder_beside`, `levers_ftp_beside`" | none (S-11): every step authorises 2020-01-02 to 2023-12-29 only (S-2); this file carries no line of the reader's judged-block form |
| D-24 | L569-L571 | 5 item 6, stage 0 | "**Stage 0 reads no bar and no atlas**" | stage 0 builds the streams on the cut and reads the search years' bars and atlas only, through the engine, with no purpose (S-2, S-17); this file is the new declaration the parent's sentence calls for |
| D-25 | L588-L589 | 6.1, the edge sets | "the gate's `lb_by_rr`" | S-5's search-year `lb_by_rr` (S-17) |
| D-26 | L595 | 6.1 (a), the rungs | "from its gate's `rung` and `resolution` rows" | from the same rows computed on the search-year stream (S-17) |
| D-27 | L614-L616 | 6.1, the inputs | "registered gate files' `edge`, `rung` and `resolution` rows" | those rows computed on the search-year stream (S-17); the other registered inputs unchanged |
| D-28 | L730 | 7.2 | "Each cell runs both arms, every start" | each cell runs both arms, every search-year start, the long replay and the exact-length runs stopping at the cut (S-6) |
| D-29 | L775 | 8, horizons and blocks | "all, early, late" | all, first, second (S-7) |
| D-30 | L787 | 9.1, its title | "whole-window identities only from `identity/*.py`" | unchanged: the registered reproduction identities stay under `identity/` (S-8); S-4's nested cut is added in the reading's own process |
| D-31 | L802 | 9.1, this reading's own | "`Judged-block reads:` line" | under the purpose `identity` and their own row; this file has no such line (S-11) |
| D-32 | L811 | 9.1 item 2 | "both arms, every start, every" | unchanged as `identity/cl_identity.py`'s identity (S-8) |
| D-33 | L833 | 9.1 item 4 | "`ref`'s start rows equal U1's again" | on the **point arm only**, on the starts whose 252-session replay ends inside the search years (S-8) |
| D-34 | L837-L838 | 9.1 item 6 | "responses, verdict arm, equals Q-44's `results/user_beside_starts.csv`" | `ref` under the fourteen responses is run on the **point arm** for this check alone (twenty-eight replays, read for nothing else) and compared with Q-44's point-arm rows, on the starts whose 252-session replay ends inside the search year(S-8); the readings beside stay on the verdict arm at S-5's constants |
| D-35 | L849-L850 | 9.1, the order | "a further judged read under `repeat=` (15)" | a rerun recorded by the lead under a row naming this file (S-16) |
| D-36 | L872 | 9.3 | "For each new cell and block" | for each new cell and each of S-7's blocks |
| D-37 | L255, L841, L843, L864, L900, L1004, L1189 | 2.3; 9.1 item 7; 9.2; 9.3; 10.2; 15 | "every start" | every search-year start (S-6) |
| D-38 | L907 | 10.1 | "every block of section 5" | every block of S-7 |
| D-39 | L951-L952 | 10.1 item 8, `naf` | "its reading the base's from Q-44's per-start rows" | re-derived from Q-44's **point-arm** per-start rows on the starts whose 252-session replay ends inside the search years (S-8), fees re-priced; never its verdict rows |
| D-40 | L959 | 10.1 item 9 | "paired with the base's registered gate paths" | paired with the base's search-year gate at the same seed and paths (S-9); the two references' gates run as the pairs' references |
| D-41 | L965 | 10.1 item 10 | "at each base's bound edge" | at each base's search-year bound edge (S-17) |
| D-42 | L970-L971 | 10.1 item 12, the menu | "the early and late blocks and the start years beside" | the first and second halves and the start years 2020 to 2023 beside (S-6, S-7) |
| D-43 | L972-L973 | 10.1 item 12, the flags | "of opposite signs on the early and late blocks" | of opposite signs on the first and second halves (S-7) |
| D-44 | L1033 | 11, the operator's choice | "over the development window" | over the search years, the held-out years unread by it (S-15) |
| D-45 | L1036-L1037 | 11, the binding | "The blocks read here are recorded as read for contract-use levers" | S-14 |
| D-46 | L1044 | 12, the build's toys seed | "T-3's synthetic late block" | T-3S's synthetic sessions after the cut (D-50), drawn from the same seed (section 8) |
| D-47 | L1089-L1092 | 13 item 4, the gates | "the references' gates are 9.1's identities" | the two references' search-year gates are run beside as the pairs' references (S-9); the registered paths stay 9.1's reproduction identities |
| D-48 | L1094 | 13 item 6 | "**Every block read** is recorded as read for contract-use levers" | the search years and their halves recorded as read for contract-use levers (S-14) |
| D-49 | L1129 | 14.3, T-0 | "one `Judged-block reads:` line" | T-0 is `tests/test_rd_search_years_drafts.py` (with this text), extended at the pin: the checks RD-06's section 7 lists, each able to fail |
| D-50 | L1132 | 14.3, T-3 | "every early-block reading at horizon h is byte-identical when every session from 2024-01-02 on is replaced" | T-3S: every reading at h is byte-identical when every session after 2023-12-29 is replaced, the runner refuses a stream holding one, and every first-half point-arm reading at h is byte-identical when every second-half session is replaced; the verdict arm at its search-year constants (S-5) |
| D-51 | L1147-L1153 | 15, files | "`results/cl_fit.csv`" | `results/cls_fit.csv`, `results/cls_reading.csv`, `results/cls_gate.csv`, `results/cls_menu.csv` (S-10) |
| D-52 | L1156 | 15, manifests | "`prereg_id` `RD-03`" | `prereg_id` this file's id at the pin (S-10) |
| D-53 | L1170 | 15 step 2 | "**stage 0** (`scripts/cl_fit.py`, one worker): its identity first (6.4)" | stage 0 after 6.4's identity, its own S-4 nested cut first, on the cut stream (S-17) |
| D-54 | L1172-L1181 | 15 steps 3 to 5 | "purposes `levers_scorecard` then `levers_gate_beside`" | steps 3 to 5 authorise 2020-01-02 to 2023-12-29 with no purpose (S-2, S-11), in the parent's order |
| D-55 | L1193-L1196 | 15, a restart or a rerun | "a further judged read" | S-16 |
| D-56 | L43 | header table, id | "every result's `prereg_id` is `RD-03` (section 15)" | this file's id at the pin (0.2); every result's `prereg_id` is it (S-10) |
| D-57 | L510-L511 | 4.5, `naf` under the Focused Trader models | "its reading is the base's (Q-44's per-start rows" | re-derived from Q-44's **point-arm** per-start rows on the starts whose 252-session replay ends inside the search years (S-8) |
| D-58 | L166 | 2.1, why Back2Funded | "E-125, `results/p14_validation.csv` section `b1`" | a record of a whole-window read (Q-18 under `registered_design`), entered in S-12; the lever is read on the search years |
| D-59 | L328 | 3, Stage 2 U2 | "`results/u_xfa_day_budget.csv`" | a record of whole-window gate paths, entered in S-12 |
| D-60 | L532 | 5 item 2, the arms | "every R at its registered bound" | every R at S-5's search-year bound |
| D-61 | L772 | 8, arms | "`verdict` the headline, `point` beside" | `verdict` at S-5's search-year constants the headline, `point` beside |
| D-62 | L1086, L1088 | 13 item 4 | "checks against Q-44" | point-arm replays of `ref` for the check alone, compared with Q-44's point-arm rows (S-8) |
| D-63 | L1179, L1181 | 15 steps 4 and 5 | "`ref`'s checks against Q-44" | `ref`'s point-arm check replays against Q-44's point-arm rows (S-8) |

## 4. Unaffected, because

Every other line the search of section 7 finds in the parent, with the reason it needs no change. The first bullets
are the first text's; the rest, grouped by the parent's sections, are the lines the red team's extra terms add.

- **L7, L10**: the parent's text history and the record's commit and date; records.
- **L56**: NQ's confirmation tests and the reserve from 2026-07-17, which this reading never reads; unchanged.
- **L63**: "a matched pair with its base on every start day": the pairing holds on every start read; S-6 sets the
  starts.
- **L116, L324, L399, L521, L876, L924, L935, L961, L962**: a user's first year, a year's purchases or payouts, a
  credit's expiry, or the gate's two-year growth on resampled days that carry no date (S-9); unchanged.
- **L154, L157, L184, L185, L210, L228, L389, L403, L428, L430, L431, L765, L844, L862, L865, L892, L1131, L1133,
  L1134, L1272, L1304, L1328**: a firm's clock in calendar days or its translation to sessions, or an account's history
  reset by a rule; a rule's term, unchanged.
- **L360, L1326**: "bought early", another sense of the word (the disclosed direction; the inventory's cap's reason).
- **L371, L383, L384, L385, L386, L387, L388, L390, L391, L392, L393, L394, L395, L396, L397, L398, L400, L401, L402,
  L404, L405, L406, L407, L408, L409, L410, L411, L412, L413, L414, L415, L416, L417, L624**: section 4's record, each
  key's date read, or a search's date; terms of the record, not read windows.
- **L542**: the horizon table's sources; each measure's h is unchanged.
- **L835**: "the start's blocks", a start's day blocks.
- **L880, L881, L883, L1161**: the pinned calendars and their hashes; the files are fixed as declared, and S-1 uses
  their days only inside the search years.
- **L995, L996, L1008**: 10.2's window rule and honesty settings, stated per block; they apply unchanged to S-7's
  blocks.
- **L1035**: no confirmation; NQ from 2026-07-17 is never read; unchanged.
- **L1056, L1065**: section 12's seed check, its date and "block" meaning the seed block; the seeds are inherited
  unchanged (section 8).
- **L1311**: Appendix C's note that the red team judged the drafter's list; a record.
- **L1, L8, L11, L13, L17, L19, L22, L25, L42, L47, L49, L51, L52, L54, L62, L70, L83, L84, L86, L90, L91, L94, L106, L107**: the parent's status, history and record of changes between its texts (before section 1): records; each operative rule they summarise is cited at its own line or governed by section 2
- **L121, L122, L127, L129, L131, L135, L159, L162, L163, L170, L171, L172, L186, L187, L194, L195, L196, L198, L203, L212, L213, L214, L218, L222, L224, L229, L232, L233, L238, L245, L264, L269, L270, L271, L279, L281, L282, L287, L292, L294, L296, L297, L298, L303, L304, L307, L308, L318**: what the reading is, the levers and the user held fixed (sections 1 and 2): the levers' rules, prices and windows, the registered trades and table described, unchanged; the trades are the cut stream's (S-2, S-3), the starts S-6's
- **L327, L329, L330, L332, L333, L347, L348, L352, L353, L355, L356, L357, L361**: prior exposure and the drafter's disclosed reads (section 3): records; the whole-window reads among them are S-12's entries (D-07 to D-13, D-58, D-59)
- **L372, L373, L374, L427, L436, L454, L457, L459, L462, L466, L467, L472, L478, L482, L483, L486, L492, L497, L498, L499, L501, L502, L508, L518**: the rules, the unstated terms, the gaps and conduct (section 4): a rule's term, its record's date, a window of days or a count, not a read window
- **L528, L549, L551, L553, L564, L568**: section 5's horizon table and identity lines: each measure's h unchanged; the registered reproduction identities stay under `identity/` (S-8)
- **L573, L578, L581, L591, L594, L596, L598, L601, L603, L607, L608, L609, L612, L617, L618, L622, L623, L625, L626, L627, L628, L635, L645, L646, L647, L650, L655, L661, L665, L667, L669, L671, L672, L673, L674, L677, L678, L681, L683, L684, L685, L686, L687, L690, L694, L695, L698, L699**: stage 0's computation, readings and checks (section 6): the solver's rules, the registered files of 6.1 and 6.4's reproduction identity, unchanged but the bound edges and rungs (S-17)
- **L705, L706, L712, L731, L733, L742, L751, L752, L753, L754, L758, L761, L770, L773, L774, L776, L777, L780, L781, L783**: the cells, the grid and the parameters (sections 7 and 8): names, settings and counts, unchanged; the arms are D-61
- **L785, L790, L791, L792, L794, L795, L797, L798, L800, L801, L806, L807, L808, L810, L812, L818, L820, L823, L824, L825, L827, L828, L855, L866, L875, L878, L882, L888, L890, L891, L894, L896**: the identities, oracles and mechanics (section 9): the registered reproduction identities, their covers and the shared waits unchanged (S-8); the oracles' bounds and the mechanics' counts are rules, read on S-6's starts and S-7's blocks
- **L911, L916, L917, L919, L925, L928, L930, L936, L939, L940, L942, L943, L950, L954, L956, L957, L958, L960, L963, L964, L966, L991, L997, L998, L999, L1000, L1001, L1002, L1003, L1006, L1009, L1010, L1011**: the reading and its uncertainty (section 10): measures, windows of h starts, the ladder's, the placement's, the models' and the gate's rules, read on S-6's starts, S-7's blocks and S-9's pool
- **L1017, L1018, L1022, L1024, L1026, L1034**: what the reading delivers (section 11): unchanged, on the search years (S-15)
- **L1043, L1045, L1046, L1047, L1048, L1049, L1050, L1051, L1052, L1059, L1061, L1066, L1069, L1070, L1071, L1072**: the seeds (section 12): inherited unchanged and by reference (section 8); the digits of a seed are not a date
- **L1080, L1081, L1083, L1085, L1098, L1110, L1111, L1112, L1113, L1118, L1119, L1130, L1135, L1137, L1139, L1140, L1141, L1142, L1144, L1154, L1157, L1167, L1168, L1169, L1183, L1187, L1190, L1191, L1192, L1198, L1201, L1203**: counting, the build, the tests and the run (sections 13 to 15): counts, adapters, tests and waits as the parent states them, the replay's inputs cut by S-2, the identities S-8's, the gates S-9's
- **L1211, L1212, L1217**: open before the pin and the operator's items (section 16): the parent's pin record and the operator's reads; unchanged
- **L1253, L1270, L1299, L1300, L1301, L1316, L1317, L1318, L1319, L1320, L1324, L1331, L1332, L1335, L1337, L1338, L1340**: Appendices R and C: the rule keys and the drafter's choices; records and terms, unchanged

## 5. What does not change

The levers L-B, L-I, L-H and L-N and what is not here (section 2); the user held fixed (2.6), P-16's marks its
registered set (S-3); the rules, their unstated terms and readings, the gaps and conduct (4); stage 0's rules,
readings, checks and identity (6.1 to 6.5) but its `bound` edges and rungs (S-17); the references, the grid and each
lever's own comparisons (7); the parameters' classes (8); the registered reproduction identities (9.1, 6.4); the
oracles (9.2); the mechanics (9.3) on S-7's blocks; the scorecard, the guard row, the journey variables, the paired
readings, D-34's caveat, the readings beside, stage 0's view beside, the evenness trade-off and the menu's flags (10.1)
on the search years; the uncertainty method (10.2, RD-02's 9.2), its window counts and honesty settings the search
years'; what the reading delivers and what each outcome means (11) on the search years; the seeds (section 12),
inherited unchanged and by reference (section 8); the counting (13): stage 0's policy evaluations and solves, 32
replays, 360 replays beside and 30 gates, with the twenty-eight point-arm check replays of `ref` in place of the 28
reference checks on the verdict arm (S-8) and the two references' search-year gates added beside (S-9); the adapters,
their rules in code and the tests T-1, T-2 and T-4 to T-15 (14), T-0 and T-3 replaced (D-49, D-50); the run's five
steps and waits (15), S-4 added to steps 2 and 3; the open items (16) and Appendices R and C.

## 6. The build list (for a later item; nothing here is built by this one)

- **B-1. The declaration.** `extended/cl_reading.py`'s and `extended/levers_terms.py`'s `DECLARATION` name this file at
  its pinned name and `PURPOSES` and `STAGE_PURPOSE` are empty; `scripts/cl_reading.py`'s `authorise`, its pre-check
  and its `STEP_PURPOSES` authorise `reader.CHOICE_START` to `reader.CHOICE_END` with no purpose; the runners refuse to
  run if any argument or constant names the parent's path or purposes. T-0's code check (N-1) then passes in its
  after-pin form.
- **B-2. The cut** (S-2): the shared module of RD-06's B-2 (for example `extended/search_years.py`), used by stage 0's
  driver and by `scripts/cl_reading.py`: the four reads, the manifests whole, the two switched-off checks and no other;
  the refusal of any day block or date after `reader.CHOICE_END` before any replay or gate.
- **B-3. The blocks** (S-7): `extended/cl_reading.py`'s `BLOCKS` (now `PR.BLOCKS`) follow RD-07's B-3 (`all`, `first`,
  `second`) through the shared repository block function; `u_select.block` is not edited and is called only for `all`;
  the flags on both arms, labelled.
- **B-4. P-16's marks and the verdict constants** (S-3, S-5): the shared marks wrapper and its count check; the halves
  as the eras for `atlas_a3.bounds`; the manifest carries S-5's printed constants.
- **B-5. Stage 0** (S-17): `scripts/cl_fit.py`'s driver (A-5) builds the cut stream with S-4 first, takes the `bound`
  edges from B-4's constants and each base's rungs from the vendored rung computation on the cut stream; the `zero` set
  and the registered files unchanged; a synthetic test that the rungs and edges it hands the solver are the cut
  stream's (a toy stream whose rung shares and edges are known by hand); its stop-and-report clause kept.
- **B-6. The checks:** `identity/cl_identity.py`, `identity/cl_fit_identity.py` and the shared identities unchanged
  (S-8); 9.1 item 4's repeat on the point arm; 9.1 item 6's twenty-eight point-arm replays of `ref` and their
  comparison with Q-44's point-arm rows; 4.5's and 10.1 item 8's `naf` readings re-derived from Q-44's point-arm
  per-start rows; every comparison on the starts whose 252-session replay ends inside the search years.
- **B-7. The gate** (S-9): each new cell's gate paired with its base's search-year gate, the two references' gates run
  first.
- **B-8. The outputs** (S-10): `results/cls_*.csv` with this file's id and every field S-10 names.
- **B-9. Tests:** T-0 (`tests/test_rd_search_years_drafts.py`, extended at the pin); T-3S (D-50) on synthetic
  campaigns under the parent's build-toys seed; the shared wrapper, marks and nested-cut tests of RD-06's B-8; B-5's
  stage-0 test.

## 7. The search that found section 3 (re-runnable)

Every line of the parent's LF text that matches any of these patterns (Python regular expressions, case-insensitive),
one per line between the markers, is cited in section 3 or listed in section 4 -- `tests/test_rd_search_years_drafts.py`
checks it, and checks that the patterns below are the test's own. The first nineteen are the first text's; the rest
are the red team's extra terms, added by the lead's ruling on M-2. T-0's other checks are listed in RD-06's section 7;
each is a function that `test_the_checks_can_fail` calls on a planted fault.

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

- **Counting.** No program family number and no level (E-023 (1)); the next numbered family's k is unchanged. The
  parent's counts hold (section 5), the twenty-eight reference checks now point-arm replays (S-8) and the two
  references' search-year gates added beside (S-9). The parent is never run (0.3), so nothing is counted twice.
- **Seeds.** The parent's section 12, inherited unchanged and by reference (its block, statuses, the honesty series'
  keys and the inherited seeds); no seed is restated here, so the parent's T-0 still finds its block in no other
  declaration. The parent was never run, so none of its seeds has been drawn on the bars. The point-arm check replays
  draw the ladder's per-start seeds as the parent's 9.1 item 6 does.
- **Confirmation.** None: nothing is carried; NQ from 2026-07-17 is never read.

## 9. Open before the pin

1. **The red team's re-read** of B-1 and B-2 in full, and of this text's other answers.
2. **The pin's edits, and only these:** the file renamed to 0.2's name; its title and status in pin-time form; its id
   written where this draft says "RD-03S". T-0's pinned-name test passes only before the pin and is replaced by its
   pin-time form in the pinning commit.
3. **The siblings** (the red team's m-2): RD-09 cites this file by its id and pinned path and sha256, written into
   RD-09's text at the pin, after this file's sha256 is fixed; this file names RD-09 by id only. The lead pins them
   together.
4. **S-2's and S-17's feasibility** are build questions; their stop-and-report clauses are declared now.
5. **The pinning row** records the parent as superseded, never run (0.3).
