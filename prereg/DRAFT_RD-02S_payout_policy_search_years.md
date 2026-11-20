# DRAFT RD-02S: payout policy in a user's first months, on the search years only (reading PP-S) -- a delta declaration of RD-02, a described reading, unnumbered (E-023 (1))

**Status: a draft, not pinned (O-7, the lead's ruling in E-221); the second text.** The first text (wt/wt-firms, the
O-7 commit) was read by the red team (`docs/reviews/O7_SEARCH_YEARS_2026-11-19.md`, two blocking findings, B-1 and
B-2); this text answers every finding as the lead ruled on it (section 0.4). It re-declares
`prereg/RD-02_payout_policy.md` on the search years alone, so that no part of the reading touches NQ's held-out years
(E-208), which E-221 (O-1) keeps for one joint fixed-sequence confirmation across firms. The parent is not edited: it
stays on record, pinned, and is never run (section 0.3). The lead assigns its id at the pin (section 0.2). Its
siblings state the same general replacements for RD-01, RD-03, RD-04 and RD-05's part F; each draft is complete on its
own.

| field | value |
|---|---|
| id | proposed **`RD-07`** at the pin (section 0.2); until then `RD-02S` |
| parent | `prereg/RD-02_payout_policy.md` sha256 `0c9dddabbc1cda0cd57787b4e8b5d34d42ee600df2d2c90e8a26178a31cb407c` (of its LF text), pinned by E-082 |
| reading | PP-S: the parent's reading PP, every cell, run and reading as the parent declares them, on the search years |
| kind | a **described reading** (E-023 (1)): never carried; no program family number, no level, no pass line, no pick |
| development data | NQ 1-minute bars, 2020-01-02 to 2023-12-29 (the search years, E-208), read only inside Stage 2's engine by P-14's and P-16's registered builders, cut at the read (S-2) |
| held-out years | 2024-01-02 to 2026-07-16: never read by this reading, under any purpose, the parent's registered reproduction identities excepted (S-1, S-8, S-11) |
| blocks | all search-year starts (the headline); the search years' first half and second half beside, each per measure at its h (S-7) |
| judged-block purposes | none (S-11) |
| Appendix A | not incorporated (D-50): a separate exploratory item, as the parent states; unrun |
| confirmation | none; NQ from 2026-07-17 never read |
| the build | not built by this item: section 6 is the build list for a later item |

## 0. What this file is, and how it reads its parent

### 0.1 The incorporation

This declaration **is the parent's text, with the replacements below**. Every section, table, rule, cell, count,
seed, oracle, test and wait of `prereg/RD-02_payout_policy.md` at the sha256 above -- its Appendix A excepted (D-50)
-- is part of this declaration, read with:

1. the general replacements S-1 to S-16 (section 2), which apply wherever the parent's words reach them;
2. the line-by-line replacements of section 3, each citing the parent's line and a short quote from it.

Where a replacement and the parent's words differ, the replacement is the declaration. Where section 3 is silent on a
parent line, section 2 governs it; where both are silent, the parent's words stand (section 5 lists what stands, and
section 4 lists every line the search of section 7 found that needs no change, with the reason). Section numbers,
item numbers, cell names, run names and test names are the parent's. **The labels S-1 to S-16 are this file's; the
parent's own labels (its findings F1 to F11 and N1 to N5, its tests T-0 to T-11) keep the parent's meaning.**

### 0.2 The id scheme (proposed; the lead assigns at the pin)

RD-06 for RD-01's delta, **RD-07 for this file**, RD-08 for RD-03's, RD-09 for RD-05's part F, RD-10 for RD-04's, in
the order of the parents. The pinned name is `prereg/RD-07_payout_policy_search_years.md`. **New numbers, not a
suffix**: the reader takes a declaration's id from its path as `RD-` and digits (`extended/reader.py`'s
`DECLARATION_ID`), so a manifest, ledger or token naming `prereg/RD-02S_...` would be attributed to RD-02; and the
parents' T-0 globs would find a name beginning with the parent's id (the red team's m-9). **One glob to narrow at the
pin:** the parent's T-0 (`tests/test_pp_draft.py`) finds its declaration by `RD-*payout*.md` and asserts exactly one,
so the pinned name above matches it; the pinning commit narrows that glob to `RD-*_payout_policy.md`, nothing else
changed (E-200 did the same for RD-01's T-0).

### 0.3 The parent, superseded before any run

No result of the parent exists: the read ledger holds no line of RD-02 and no file `results/pp_*.csv` exists at this
draft (RD-02's build and its two-worker check are merged, E-220; its run is not). At this file's pin the parent is
**superseded, never run**: no run takes its three purposes, its result files are never written, and its id is never a
manifest's `prereg_id`. The reader cannot see a withdrawal (the audit's R-8 registry is not built), and its held-out
rule 4 refuses the parent's judged reads only until a market's verdict row exists; so the supersession is enforced by
the build (section 6, B-1), held now by T-0's code check (N-1), and recorded in the pinning row.

### 0.4 What changed from the first text (the red team's read, as the lead ruled on it)

| finding | the first text | this text | where |
|---|---|---|---|
| B-1 | `ref`'s rows compared with U1's and Q-44's verdict-arm rows; the bases' readings and Q-44's pooled `results/user_beside.csv` cited | every comparison with U1's or Q-44's rows, and every citation of them, on the **point arm only**: `ref`'s ladder and placement checks run on the point arm (eight replays for the check alone); the bases' readings re-derived from Q-44's point-arm per-start rows; the pooled file never cited | S-8; D-30, D-31, D-37, D-56 |
| B-2 | P-16's marks re-resolved on the cut; a cut identity reading the whole window | P-16's offered marks fixed to its registered set (S-3); a nested cut inside the search years (S-4) and B-1's point-arm equality; no new identity reads 2024 or later | S-3, S-4, S-8 |
| M-1 | P-11's eras on the cut, 2023 alone | the halves, 2020-21 and 2022-23, as the eras, declared | S-5 |
| M-2 | missed lines; the drafter's terms alone | the red team's extra terms added (section 7); the verdict arm's "registered bound" lines (D-54, D-55) and the pooled file (D-56) cited | sections 3, 4, 7 |
| m-1 to m-9, N-1 | as in RD-06's 0.4 | the labels S-1 to S-16; the wrapper's reads and switched-off checks; the no-op guard; the verdict-arm halves labelled; T-0 rebuilt; the id reason; the code check | throughout |

## 1. Why, and what it does to what the reading can show (E-051)

**Why.** Under E-208 every choice and every map the journey search draws on is made on the search years, and the
held-out years are read once, by the joint confirmation (E-221, O-1). The parent reads the whole development window, its
late block by name, and its judged-block purposes, and its levers are now in the search's lever space (CHARTER 3.6
(b)); any range drawn from its menu would carry a held-out read into the search (CHARTER 3.3 (a)). O-7 rules that the
reading is re-declared on the search years.

**What it does to what the reading can show.** The menu describes the search years only. Each measure's starts at its
horizon h are fewer (S-6): at h = 252 they are the starts with 252 sessions inside the search years, so the headline
holds fewer kept windows and more readings print "too few separated windows for an interval"; each half (S-7) holds
about two years, so most half readings at months 6 to 12 -- where the parent's section 2 says a gain from keeping money
in the account should show -- print the sign count alone. The stability flag compares two halves of four years
instead of the search years against the held-out years. The verdict arm's shift is the search years' own, with the
halves as its eras (S-5), and the verdict arm's halves share it (S-7). The Focused Trader rows of the bases, beside,
are the point arm's (S-8). Nothing else of the reading changes: the levers, the cells, the held-state rule, the counts,
the uncertainty method and the oracles are the parent's.

## 2. The general replacements

- **S-1. The window.** The development data are NQ 1-minute bars from 2020-01-02 to 2023-12-29, the search years
  (E-208). The held-out years 2024-01-02 to 2026-07-16 are never read by this reading, under any purpose, by any of its
  runs, gates, checks, or beside readings; NQ from 2026-07-17 is never read. Wherever the parent says "the development
  window", "2020-2026" or "the whole window" of what this reading reads, read the search years. A pinned calendar
  (E-029, E-050) is used only on days inside the search years.
  **The one exception (the re-read's rm-4):** the parent's registered reproduction identities (S-8) take the whole
  window under the purpose `identity`; they reproduce Stage 2's registered files, write no outcome of any cell and
  are ledgered in a clean run. No other part of this reading, and no check it introduces, takes a held-out day.
- **S-2. The cut at the read.** No bar or atlas row dated after 2023-12-29 reaches any function of the registered
  builders, the replay, the gate or the reading. **The guard is the wrapper and the refusal below**: the reader's
  `authorise_engine_read` on 2020-01-02 to 2023-12-29 with no purpose checks the dates only and writes nothing, and the
  reader cannot see reads made inside vendored calls (the red team's m-4). The wrapper acts, for the builders' calls
  only, on exactly these inputs, and restores each after the call (nothing vendored is edited):
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
- **S-4. The nested cut, refusing** (the lead's ruling on B-2). Before any replay, the reading's own process builds each
  design's stream twice on the cut, with S-3's marks: on 2020-01-02 to 2022-12-30 and on 2020-01-02 to 2023-12-29.
  Their **point-arm** day blocks must be equal up to 2022-12-30, block for block, every field, the per-R outcomes
  included. It reads the search years only, needs no purpose, writes its pass or fail lines to the run's log and
  manifest, and a failure stops the reading. With S-8's point-arm equality it is the whole check that the cut stream is
  the registered design's. **No identity these deltas introduce reads 2024 or later** (the lead's ruling rn-5); the parent's declared identities keep
  their declared whole-window form, labelled so (S-8); the registered reproduction identities are
  untouched (S-8).
- **S-5. The verdict arm's constants, re-estimated on the search years, with the halves as eras** (the lead's ruling on
  M-1). The parent's N2: the bound "was estimated on the whole development window", so every verdict row is a function
  of the held-out years through one constant per R. Here `e`, `lb`, `e_by_rr` and `lb_by_rr` are `atlas_a3.bounds`'s,
  as the registered builder calls it, on the search-year trades and days, at the registered trial count and era seed,
  **with its eras declared now as the two calendar halves, 2020-2021 and 2022-2023**, passed in the bounds'
  configuration for the call (P-11's spans would leave 2023 alone as an era). Each R's bound is the pooled one, or the
  lower era's when the whole-year bootstrap flags the eras. **Printed in every manifest, per design and R:** the flag,
  the bound read, the pooled bound and each era's. **Reason:** inherited, the constant would carry a held-out read into
  every verdict row and so into the lever space (CHARTER 3.3 (a)). The `point` arm is unchanged. The verdict blocks are
  `shifted_blocks` of the point blocks by these constants, which the runner's per-stream shift check holds.
- **S-6. The starts and the horizon embargo** (CHARTER 3.6 (d)). The starts are every start day U1 reads inside the
  search years. Each measure is read at its horizon h (the parent's 5 item 3 table, unchanged) only on starts with h
  sessions inside the search years: on the cut replay a start observes no session after 2023-12-29, so
  `u_select.block(records, None, h)` gives exactly these. U1's long replay of up to 252 sessions and its exact-length
  runs stop at the cut. Wherever the parent says "every start" or "all starts" of what is replayed or read, read the
  search-year starts with the horizon left. By start year: 2020 to 2023, means only, not purged within the search years
  (a start late in a year reads the next year's sessions), and 2023's starts read only 2023's sessions; labelled so.
- **S-7. The blocks: the late block replaced by the search years' second half.** On the cut replay the parent's early
  block equals the headline and its late block is empty, so both are replaced, per measure at its h:
  - **all**: every search-year start with h sessions inside the search years (the headline);
  - **first**: the starts of 2020 and 2021, each read at h only if h sessions remain before the first session of 2022
    (the parent's per-measure purge, F6 and D-621 (4)(b), moved to the half's end);
  - **second**: the starts of 2022 and 2023, read at h only with h sessions inside the search years.

  **On the point arm no first-half reading touches a second-half session. On the verdict arm the halves share S-5's
  constants, estimated on both halves** -- the kind of shared constant the parent's N2 disclosed -- and every
  verdict-arm half row is labelled so. The stability flag is printed on both arms; the point arm's is labelled "the
  halves share no constant". **Reason for the halves:** the flag needs two disjoint stretches read apart; two calendar
  halves of equal length, fixed by the calendar before any read and cut at a year's end as the parent's blocks were,
  keep it without reading a held-out day. At 12 months each half is close to one start year, so the flag there is weak;
  the start-year rows are the fuller description. The vendored `u_select.block` fixes its years, so the halves are a
  function of this repository (B-3). Nothing is chosen on any block. **Considered and not taken:** no blocks (it loses
  the flag); halves by start count (a cut that moves with the data).
- **S-8. The identities, the comparisons and the citations** (the lead's ruling on B-1). The parent's registered
  reproduction identities (8.1 items 1 to 3, from `identity/pp_identity.py`) and the shared ones it waits for (Q-05,
  Q-80, Q-93, Q-101) are untouched: whole window, the purpose `identity`, their own rows, Stage 2's files reproduced,
  no outcome of any cell written, ledgered in a clean run. Inside the reading's own run:
  - **every comparison with U1's or Q-44's per-start rows is on the point arm only**, on the starts whose 252-session
    replay ends inside the search years, every column the parent names, refusing; no row of another arm or a later
    start is loaded. So 8.1 item 4's repeat compares `ref`'s point-arm start rows with U1's, and 8.1 item 6 runs `ref`
    under `denial_10`, `denial_25`, `denial_50` and `rtp` **on the point arm, for the check alone** (eight replays, two
    bases by four responses, read for nothing else) and compares them with Q-44's point-arm rows. The verdict arm is
    never compared with a registered file: its constants are the search years' (S-5);
  - **every citation of U1's or Q-44's rows is of their point-arm per-start rows**, on the same starts; a figure the
    parent cites from them (the bases' readings under the Focused Trader models, 9.1 item 7 and 7.2) is re-derived from
    those rows; Q-44's verdict rows and its pooled file `results/user_beside.csv` are never cited.
- **S-9. The gate on the search years.** Every gate beside draws its resampled days from the search-year day blocks
  only. Each policy cell's gate is paired with its base's own search-year gate at the same seed and the same number of
  paths (the same pool of days, so the same day draws), not with the registered gate paths, which draw from the whole
  window. The two references' search-year gates are run and read beside as the pairs' references, so the 8 gates are 6
  new and 2 references; the registered gate paths stay S-8's reproduction identities.
- **S-10. The outputs.** New files, never the parent's: `results/pps_reading.csv`, `results/pps_gate.csv`,
  `results/pps_menu.csv`, each through `extended.results.write_result` with its sidecar manifest, `prereg_id` this
  file's id at the pin, the window 2020-01-02 to 2023-12-29, S-4's result, S-5's constants and flags, S-2's
  switched-off checks, S-12's list, the rows under which the parent's identities held, and every manifest field the
  parent's section 14 lists.
- **S-11. No judged-block purpose.** This declaration reads no day of the held-out years, so it names no purpose of the
  reader's judged-block form and carries no line of that form; the reader refuses any judged read citing it. The
  parent's line is the parent's and is never taken (0.3).
- **S-12. The held-out read ledger, inherited and labelled** (CHARTER 3.6 (b); no figure cited). This reading rests on
  designs and records that read the held-out years before it: P-14 fixed as R* from the whole window (Stage 2 D-626);
  P-14's rung map and P-16's mark cutoff resolved on the whole window (E-203 S-2), the latter fixed here as P-16's
  registered mark set (S-3); P-16's stop chosen on each block (Stage 2 D-554); the registered state table
  (`state_dp_e-0.050_lamstar_noclose`) and protocols as Stage 2 registered them; Stage 2 D-564 to D-566's payout screen
  on P-16's cell over the whole window; program U's nine families, which read P on the late block, and its families 6,
  7 and 8 on both blocks; U1's whole-window start rows (Stage 2 D-620) and Q-44's per-start rows, which S-8 compares and
  cites on the point arm and search-year starts only; Q-44's pooled file, never cited; Stage 2's signal search over the
  whole window; and the parent's own pinned text, declared over the whole window and never run. Nothing here
  re-estimates them but S-5's constants; every result file of this reading names them.
- **S-13. Prior exposure, re-read.** The parent's prior-exposure rows stand as records. Where a row's bearing reads "the
  late block has been read for P nine times; it is late development, not out of sample", read: those reads were of the
  held-out years; they are S-12's entries; this reading reads none of those years.
- **S-14. The binding.** The parent's "the blocks this reading reads are recorded as read for payout policy on P-14 and
  P-16" reads: the search years, and their two halves, are recorded as read for payout policy on P-14 and P-16; the
  held-out years are not read by this reading and are recorded as unread by it.
- **S-15. In sample.** Every statement made from this reading, and the operator's choice from its menu, is a
  description of the search years, in sample, with no confirmation (E-023 (1)); the held-out years stay unread by it.
- **S-16. Reruns.** The reader ledgers no choice-block read, so its once-per-purpose refusal does not reach this
  reading. The parent's rule is kept by the lead: only the first complete clean run is read; a restart or a rerun is
  recorded by the lead with its log under a decision row naming this file, which says which run replaces which and
  why; a result file is never overwritten (S-10).

## 3. Every dependency in the parent, line by line

The parent's lines as numbered in its LF text at the pinned sha256. A row's lines are one line, a range whose joined
text holds the quote, or a list of lines each holding the quote. The replacement is this declaration's.

| # | parent lines | where | quote | replacement |
|---|---|---|---|---|
| D-01 | L45 | header table, development data | "NQ 1-minute bars, 2020-01-02 to 2026-07-16" | NQ 1-minute bars, 2020-01-02 to 2023-12-29, cut at the read (S-1, S-2) |
| D-02 | L47 | header table, blocks | "the late block from 2024-01-02 (section 5)" | all search-year starts the headline; the first and second halves beside, each purged per measure (S-7) |
| D-03 | L49 | header table, beside | "8 gates (6 new, 2 identities)" | the 6 new gates, and the two references' search-year gates as their pairs' references (S-9); and the eight point-arm check replays of `ref` (S-8) |
| D-04 | L51 | header table, the parent's purposes | "three purposes, on the line of section 5 item 6" | none (S-11); the identities from `identity/*.py` under their own row, unchanged (S-8) |
| D-05 | L147 | 1, why described | "the late block's few independent three-month stretches" | the same reason holds a fortiori on the search years: fewer independent stretches still (section 1) |
| D-06 | L154 | 1, the operator's choice | "a described development reading" | a described reading of the search years (S-15) |
| D-07 | L156 | 1, the operator's choice | "a description of the development window" | a description of the search years (S-15) |
| D-08 | L188-L189 | 2, where to look | "where the late block has the fewest independent windows" | where each half has the fewest independent windows (section 1) |
| D-09 | L201 | 3, Stage 2 D-564 to D-566 | "over the whole development window" | a record; a held-out read by Stage 2, entered in S-12 |
| D-10 | L202, L203 | 3, program U families 6, 7 and 8 | "both blocks" | a record; held-out reads by Stage 2, entered in S-12 |
| D-11 | L204 | 3, U1 and Q-05 | "P-14's and P-16's own journeys, every start" | a record; the references' rows are whole-window, and S-8 compares them on the point arm and search-year starts only |
| D-12 | L205 | 3, program U's nine families | "it is late development, not out of sample" | those reads were of the held-out years; S-12's entries; none read here (S-13) |
| D-13 | L207-L211 | 3, N2 | "So an early-block reading on the verdict arm is a function of 2024-2026 through that one constant" | the verdict arm's constants re-estimated on the search years with the halves as eras (S-5); no reading is a function of the held-out years |
| D-14 | L318 | 5, its title | "Data, blocks and the unit" | section 5 as items 1 to 6 are replaced in D-15 to D-24 |
| D-15 | L320 | 5 item 1 | "one development start day" | one search-year start day (S-6) |
| D-16 | L320-L322 | 5 item 1 | "U1 runs a long replay of up to 252 sessions plus its exact runs" | U1's long replay of up to 252 sessions and its exact runs, stopping at the cut (S-6) |
| D-17 | L325 | 5 item 2 | "the same start days, the same blocks and the same seeds" | the same search-year start days, S-7's blocks and the parent's seeds |
| D-18 | L327-L333 | 5 item 3 | "the starts from 2024-01-02 with h sessions left" | item 3's three sets are S-7's all, first and second, each at its measure's h; the horizon table is unchanged |
| D-19 | L330-L332 | 5 item 3, the early block | "No early reading touches a 2024 session, except through the verdict arm's bound (N2, section 3)" | no reading touches a session after 2023-12-29, and none through the bound (S-2, S-5); on the point arm no first-half reading touches a second-half session; on the verdict arm the halves share S-5's constants, labelled (S-7) |
| D-20 | L335-L337 | 5 item 3 | "The early and late blocks are read separately" | the first and second halves are read separately, so the menu can flag a policy whose effect changes sign between them (S-7) |
| D-21 | L354-L356 | 5 item 3, by start year | "the purged comparison is the early and late blocks'" | by start year 2020 to 2023 (S-6); the purged comparison is the halves' (S-7) |
| D-22 | L357-L360 | 5 item 4 | "The late block holds about nine non-overlapping 63-start windows" | each half holds about two years of starts and the headline the search years'; each reading prints its own count (9.2), none typed here |
| D-23 | L361 | 5 item 5 | "No NQ from 2026-07-17" | this reading takes no NQ after 2023-12-29 (S-1); NQ from 2026-07-17 is not on disk and never read |
| D-24 | L362-L366 | 5 item 6, the seal and the parent's purposes | "`payout_scorecard`, `payout_ladder_beside`, `payout_gate_beside`" | none (S-11): the reading authorises 2020-01-02 to 2023-12-29 only (S-2); this file carries no line of the reader's judged-block form |
| D-25 | L494 | 7.1, blocks | "all; early and late per measure (section 5)" | all; first and second per measure (S-7) |
| D-26 | L544 | 8.1, its title | "whole-window identities only from `identity/*.py`" | unchanged: the registered reproduction identities stay under `identity/` (S-8); S-4's nested cut is added in the reading's own process |
| D-27 | L555, L558 | 8.1, the shared identities | "every start" | unchanged, whole-window, under `identity/` (S-8) |
| D-28 | L564 | 8.1, this reading's own | "never under this file's `Judged-block reads:` line" | under the purpose `identity` and their own row; this file has no such line (S-11) |
| D-29 | L577 | 8.1 item 2 | "both arms, every start, every column" | unchanged as `identity/pp_identity.py`'s identity (S-8) |
| D-30 | L588 | 8.1 item 4 | "And the reading's own `ref` start rows equal U1's again" | on the **point arm only**, on the starts whose 252-session replay ends inside the search years (S-8) |
| D-31 | L595-L596 | 8.1 item 6 | "verdict arm, equals Q-44's `results/user_beside_starts.csv`" | `ref` under the four responses is run on the **point arm** for this check alone (eight replays, read for nothing else) and compared with Q-44's point-arm rows, on the starts whose 252-session replay ends inside the search years (S-8); the readings beside stay on the verdict arm at S-5's constants |
| D-32 | L604 | 8.1, the order | "a rerun is a further judged read under `repeat=`" | a rerun is recorded by the lead under a row naming this file (S-16) |
| D-33 | L618 | 8.3 | "For each new cell and each block" | for each new cell and each of S-7's blocks |
| D-34 | L636-L638 | 8.3, E-029's voided days | "The three days E-029 voids for families" | of E-029's voided days only 2020-07-01 is in the search years; it is listed with the number of starts, per block of S-7 and horizon, whose h sessions hold it; the two later days are outside the search years and never read |
| D-35 | L640, L894, L997 | 8.3; 13.1 item 1; 14 weight | "every start" | every search-year start (S-6) |
| D-36 | L647 | 9.1 | "on every block of section 5" | on every block of S-7 |
| D-37 | L704 | 9.1 item 7 | "The bases' readings are cited from Q-44's file" | re-derived from Q-44's **point-arm** per-start rows on the starts whose 252-session replay ends inside the search years; never its verdict rows or its pooled file (S-8) |
| D-38 | L711-L713 | 9.1 item 8 | "paired with the base's registered gate paths" | paired with the base's search-year gate at the same seed and paths (S-9); the two references' gates run as the pairs' references, the registered paths staying S-8's reproduction identities |
| D-39 | L722-L723 | 9.1 item 10, the menu | "the early and late blocks beside" | the first and second halves beside, and by start year 2020 to 2023 (S-6, S-7) |
| D-40 | L724-L725 | 9.1 item 10, the stability flag | "on the early and late blocks is flagged" | on the first and second halves is flagged (S-7) |
| D-41 | L815-L816 | 10, the binding | "The blocks this reading reads are recorded as read for payout policy" | S-14 |
| D-42 | L829 | 11, the build's toys seed | "T-3's synthetic late block" | T-3S's synthetic sessions after the cut (D-48), drawn from the same seed (section 8) |
| D-43 | L878 | 12 item 2 | "the 2 references' are 8.1's identities" | the two references' search-year gates are run beside as the pairs' references (S-9); the registered paths stay 8.1's identities |
| D-44 | L880 | 12 item 2 | "every block read, recorded as read for payout policy" | the search years and their halves recorded as read for payout policy (S-14) |
| D-45 | L942 | 13.3, T-0 | "one `Judged-block reads:` line" | T-0 is `tests/test_rd_search_years_drafts.py` (with this text), extended at the pin: the checks RD-06's section 7 lists, each able to fail |
| D-46 | L958-L961 | 14, files | "`results/pp_reading.csv`" | `results/pps_reading.csv`, `results/pps_gate.csv`, `results/pps_menu.csv` (S-10) |
| D-47 | L964 | 14, manifests | "`prereg_id`: `RD-02`" | `prereg_id` this file's id at the pin (S-10) |
| D-48 | L945 | 13.3, T-3 | "every early-block reading at horizon h is byte-identical when every session from 2024-01-02 on is replaced" | T-3S: every reading at h is byte-identical when every session after 2023-12-29 is replaced, the runner refuses a stream holding one, and every first-half point-arm reading at h is byte-identical when every second-half session is replaced; the verdict arm at its search-year constants (S-5) |
| D-49 | L985-L986 | 14 step 2 | "The runner authorises its engine reads under the three purposes of section 5 item 6" | the runner authorises 2020-01-02 to 2023-12-29 with no purpose (S-2, S-11); S-4's nested cut holds first |
| D-50 | L1046-L1052 | Appendix A | "A SEPARATE ITEM, EXPLORATORY" | not incorporated: the parent states it is not part of reading PP; it stays on record, unrun; any run of it needs its own row ruling its window (its identity (b) reproduces a whole-window registered gate call) |
| D-51 | L998-L1002 | 14, a restart or a rerun | "Each purpose on the line allows one clean run" | S-16 |
| D-52 | L1000 | 14, a restart or a rerun | "a further judged read" | S-16 |
| D-53 | L41 | header table, id | "every result's `prereg_id` is `RD-02` (section 14)" | this file's id at the pin (0.2); every result's `prereg_id` is it (S-10) |
| D-54 | L323 | 5 item 1, the arms | "every R at its registered bound" | every R at S-5's search-year bound |
| D-55 | L487 | 7.1, arms | "`verdict` the headline, `point` beside" | `verdict` at S-5's search-year constants the headline, `point` beside |
| D-56 | L531-L532 | 7.2, the Focused Trader models | "Q-44's `results/user_beside.csv`, at the vendored class), cited beside by file" | the bases' own readings under the models re-derived from Q-44's point-arm per-start rows (`results/user_beside_starts.csv`) on the starts whose 252-session replay ends inside the search years; the pooled file `results/user_beside.csv` never cited (S-8) |
| D-57 | L877-L878 | 12 item 2 | "the 8 at `ref` are 8.1 item 6's checks" | the 8 at `ref` are verdict-arm base rows; 8.1 item 6's checks are eight further replays of `ref` on the point arm (S-8) |
| D-58 | L966 | 14, the manifests' run counts | "32 replays and 8 gates beside" | 32 replays, the eight point-arm check replays and 8 gates beside (S-8, S-9) |
| D-59 | L988 | 14 step 2 (b) | "`ref` under the ladder and the placement, verdict arm: item 6" | `ref` under the ladder and the placement, verdict arm, and its eight point-arm check replays: item 6 (S-8) |

## 4. Unaffected, because

Every other line the search of section 7 finds in the parent, with the reason it needs no change. The first bullets
are the first text's; the rest, grouped by the parent's sections, are the lines the red team's extra terms add.

- **L7, L15**: the parent's text history, a record of how it was made.
- **L54**: NQ's confirmation tests and the reserve from 2026-07-17, which this reading never reads; unchanged.
- **L67, L69, L72, L79, L80, L85, L92, L103, L105, L112**: the parent's table of changes between its drafts, a record;
  each rule it summarises is cited at its own line (D-01 to D-52) or governed by section 2.
- **L121**: "a matched pair with its base on every start day": the pairing holds on every start read; S-6 sets the
  starts.
- **L139, L236, L237, L660, L716, L809**: a user's first months and year, a year's payouts, or Stage 2's two-year growth
  (a measure's or the gate's horizon on resampled days that carry no date, S-9); unchanged.
- **L175**: "an early payout", another sense of the word.
- **L200**: a record of a search Stage 2's log was given, with its date; unchanged.
- **L218, L224, L227**: the drafter's disclosed reads (code, rules and calendars); records.
- **L252, L253, L254, L255, L256, L257, L258, L259, L260, L261, L262, L263**: section 4's rule table, each key's date
  read; a term of the record, not a read window.
- **L282, L283, L297, L298, L300, L626, L627, L630, L631, L972**: the pinned calendars and their hashes; the files are
  fixed as declared, and S-1 uses their days only inside the search years.
- **L339, L345, L346, L347, L350, L493**: the horizon table and its sources (`u_select.MEASURES`); each measure's h is
  unchanged.
- **L467**: nothing is chosen on any block; holds for S-7's blocks.
- **L495, L743, L744, L752, L754, L759, L760, L765, L770, L794**: 9.2's window rule and its pieces, stated per block;
  they apply unchanged to S-7's blocks.
- **L525**: a record of another identity owed (P-15's); unchanged.
- **L593, L632, L634**: "blocks" in another sense (a start's day blocks, a trade's block).
- **L813**: no confirmation; NQ from 2026-07-17 is never read; unchanged.
- **L837, L845, L848, L853, L858**: section 11's seed check, its date and "block" meaning the seed block; the seeds are
  inherited unchanged (section 8).
- **L950, L1007**: the identity script's full run and the Q-93 wait, whole-window identities under `identity/` (S-8).
- **L1035**: E-015's limits "never block"; unchanged.
- **L1, L9, L11, L12, L13, L16, L17, L19, L20, L21, L35, L40, L46, L48, L52, L60, L68, L70, L71, L73, L74, L75, L76, L78, L82, L83, L84, L86, L90, L101, L102, L104, L111, L113, L115**: the parent's status, history and record of changes between its texts (before section 0.3): records; each operative rule they summarise is cited at its own line or governed by section 2
- **L120, L129, L143, L164, L170, L187**: what a payout policy changes, what the reading is and the mechanism (sections 0.3 to 2): the registered trades, table and rules described, unchanged; the trades are the cut stream's (S-2, S-3), the starts S-6's
- **L215, L216, L221, L228, L232, L241**: prior exposure and the drafter's disclosed reads (section 3): records; the whole-window reads among them are S-12's entries (D-09 to D-13)
- **L245, L267, L272, L279, L286, L287, L289, L290, L291, L292, L293, L299, L302, L313, L314**: contract fit and the verified rules (section 4): a rule's term, its record's date, a payout gate or a count of days, not a read window
- **L324, L340, L348, L349, L352, L371, L373, L374**: section 5's horizon table and identity lines: each measure's h unchanged; the registered reproduction identities stay under `identity/` (S-8)
- **L395, L405, L406, L410, L411, L413, L443, L445, L448, L451, L457, L458, L473, L474, L475, L476, L478, L481, L488, L489, L491, L492, L496, L497, L498, L503, L511, L513, L524, L526, L534, L535, L536, L538, L539**: the cells, the levers, the held-state rule and the parameters (sections 6 and 7): rules and declared choices, unchanged; the arms are D-55, the pooled file D-56
- **L542, L548, L549, L550, L551, L552, L554, L557, L561, L562, L563, L567, L573, L574, L575, L576, L580, L587, L598, L603, L610, L621, L624, L625**: the identities, oracles and mechanics (section 8): the registered reproduction identities and the shared ones unchanged (S-8); the oracles' bounds and the mechanics' counts are rules, read on S-6's starts and S-7's blocks
- **L654, L655, L656, L661, L662, L666, L667, L669, L679, L680, L681, L684, L685, L689, L697, L699, L709, L710, L715, L735, L745, L746, L748, L749, L750, L751, L753, L756, L757, L761, L763, L764, L766, L767, L769, L772, L773, L776, L777, L778, L780, L781, L783, L784, L786, L789, L791, L795, L796, L801, L802, L803**: the reading and its uncertainty (section 9): measures, windows of h starts, the ladder's and the gate's rules, read on S-6's starts, S-7's blocks and S-9's pool
- **L822, L823, L824, L825, L826, L827, L828, L830, L831, L834, L840, L842, L850, L851, L852, L854, L860, L862, L863, L864, L866, L867, L868**: the seeds (section 11): inherited unchanged and by reference (section 8); the digits of a seed are not a date
- **L875, L884, L890, L891, L892, L893, L897, L901, L903, L910, L916, L919, L920, L923, L924, L925, L926, L943, L946, L948, L952, L953, L967, L970, L982, L983, L990, L991, L996, L1006, L1008, L1009, L1010**: counting, the build, the tests and the run (sections 12 to 14): counts, adapters, tests and waits as the parent states them, the replay's inputs cut by S-2, the identities S-8's, the gates S-9's
- **L1017, L1020, L1025, L1026, L1027, L1028, L1030**: what the pin requires and stays open (sections 15 and 16): the parent's pin record and the open items; unchanged
- **L1059, L1061, L1062, L1064, L1065, L1070, L1072, L1073, L1074, L1076, L1077, L1079, L1084, L1087, L1088, L1092, L1093, L1108, L1111, L1116**: Appendix A: not incorporated (D-50)

## 5. What does not change

The mechanism (section 2); the verified rules and every assumption of section 4; the levers L1 and L2, the grid, the
held-state rule and its rule-sensitivity runs (section 6); the parameters' classes and what is dropped (7); the
registered reproduction identities (8.1 items 1 to 3); the oracles (8.2); the mechanics (8.3) on S-7's blocks; the
scorecard, the paired readings, each lever alone and their interaction, what diverges, the readings beside and the
menu's flags (9.1) on the search years; the uncertainty method (9.2), its window counts and honesty settings the
search years'; what the reading delivers (10) on the search years; the seeds (section 11), inherited unchanged and by
reference (section 8); the counting (12): 11 runs, 32 replays beside and 8 gates, with the eight point-arm check
replays of `ref` added (S-8) and the two references' gates run on the search years (S-9); the adapters, their rules in
code and the tests T-1, T-2 and T-4 to T-11 (13), T-0 and T-3 replaced (D-45, D-48); the run's two steps and waits
(14), S-4 added to step 2; the lead's and the operator's items after the pin (15).

## 6. The build list (for a later item; nothing here is built by this one)

- **B-1. The declaration.** `extended/pp_run.py`'s `DECLARATION` names this file at its pinned name and `PURPOSES` is
  empty; `scripts/pp_reading.py`'s `check` and `ledger` calls authorise `reader.CHOICE_START` to `reader.CHOICE_END`
  with no purpose; the runner refuses to run if any argument or constant names the parent's path or purposes. T-0's
  code check (N-1) then passes in its after-pin form.
- **B-2. The cut** (S-2): the shared module of RD-06's B-2 (for example `extended/search_years.py`): the four reads, the
  manifests whole, the two switched-off checks and no other, and the refusal of any day block or date after
  `reader.CHOICE_END` before any replay or gate.
- **B-3. The blocks** (S-7): `extended/pp_run.py`'s `BLOCKS` become `(("all", None), ("first", "first"), ("second",
  "second"))` through the shared repository block function; `extended/pp_reading.py`'s `block` and `by_year` call it
  (`u_select.block` is not edited and is called only for `all`); the stability flag on both arms, labelled.
- **B-4. P-16's marks and the verdict constants** (S-3, S-5): the shared marks wrapper and its count check; the halves
  passed as the eras to `atlas_a3.bounds` for the builders' calls; the shift recorded; the manifest carries S-5's
  printed constants.
- **B-5. The checks:** `identity/pp_identity.py` and the shared identities unchanged (S-8); S-4's nested cut as the
  runner's first stage; 8.1 item 4's repeat on the point arm; 8.1 item 6's eight point-arm replays of `ref` and their
  comparison with Q-44's point-arm rows; 9.1 item 7's bases' readings re-derived from Q-44's point-arm per-start rows;
  every comparison on the starts whose 252-session replay ends inside the search years.
- **B-6. The gate** (S-9): each policy cell's gate paired with its base's search-year gate, the two references' gates
  run first.
- **B-7. The outputs** (S-10): `results/pps_*.csv` with this file's id and every field S-10 names.
- **B-8. Tests:** T-0 (`tests/test_rd_search_years_drafts.py`, extended at the pin); T-3S (D-48) on synthetic campaigns
  under the parent's build-toys seed; the shared wrapper, marks and nested-cut tests of RD-06's B-8; the narrowed glob
  of `tests/test_pp_draft.py` at the pin (0.2).

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
  parent's counts hold (section 5), with the eight point-arm check replays of `ref` added (S-8) and the two references'
  gates run on the search years (S-9). The parent is never run (0.3), so nothing is counted twice.
- **Seeds.** The parent's section 11, inherited unchanged and by reference (its block, statuses, the inherited seeds and
  the honesty series' keys); no seed is restated here, so the parent's T-0 still finds its block in no other
  declaration. The parent was never run, so none of its seeds has been drawn on the bars. The point-arm check replays
  draw the ladder's per-start seeds as the parent's 8.1 item 6 does. The seeds the parent names for Appendix A stay
  Appendix A's (D-50).
- **Confirmation.** None: nothing is carried; NQ from 2026-07-17 is never read.

## 9. Open before the pin

1. **The red team's re-read** of B-1 and B-2 in full, and of this text's other answers.
2. **The pin's edits, and only these:** the file renamed to 0.2's name; its title and status in pin-time form; its id
   written where this draft says "RD-02S"; the narrowed glob of `tests/test_pp_draft.py`. T-0's pinned-name test
   passes only before the pin and is replaced by its pin-time form in the pinning commit.
3. **S-2's feasibility** is a build question; its stop-and-report clause is declared now.
4. **The pinning row** records the parent as superseded, never run (0.3), and Appendix A as unrun and not incorporated
   (D-50).
