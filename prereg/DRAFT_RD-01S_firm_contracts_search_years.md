# DRAFT RD-01S: other firms' contracts on the registered trades, on the search years only (reading FC-S) -- a delta declaration of RD-01, a described reading, unnumbered (E-023 (1))

**Status: a draft, not pinned (O-7, the lead's ruling in E-221); the second text.** The first text (wt/wt-firms, the
O-7 commit) was read by the red team (`docs/reviews/O7_SEARCH_YEARS_2026-11-19.md`, two blocking findings, B-1 and
B-2); this text answers every finding as the lead ruled on it (section 0.4). It re-declares
`prereg/RD-01_firm_contracts.md` on the search years alone, so that no part of the reading touches NQ's held-out years
(E-208), which E-221 (O-1) keeps for one joint fixed-sequence confirmation across firms. The parent is not edited
(CLAUDE.md; `tests/test_declarations_fixed.py`): it stays on record, pinned, and is never run (section 0.3). The lead
assigns its id at the pin (section 0.2).

| field | value |
|---|---|
| id | proposed **`RD-06`** at the pin (section 0.2); until then `RD-01S` |
| parent | `prereg/RD-01_firm_contracts.md` sha256 `f6df144da5ea706e88c3e8f84549b4492f78802fe84cdf506d7754c3cf5c9bcb` (of its LF text), pinned by E-080 |
| reading | FC-S: the parent's reading FC, every cell, run and reading as the parent declares them, on the search years |
| kind | a **described reading** (E-023 (1)): never carried; no program family number, no level, no pass line, no pick |
| development data | NQ 1-minute bars, 2020-01-02 to 2023-12-29 (the search years, E-208), read only inside Stage 2's engine by P-16's and P-14's registered builders, cut at the read (S-2) |
| held-out years | 2024-01-02 to 2026-07-16: never read by this reading, under any purpose, the parent's registered reproduction identities excepted (S-1, S-8, S-11) |
| blocks | all search-year starts (the headline); the search years' first half and second half beside (S-7) |
| judged-block purposes | none (S-11) |
| confirmation | none; NQ from 2026-07-17 never read |
| the build | not built by this item: section 6 is the build list for a later item |

## 0. What this file is, and how it reads its parent

### 0.1 The incorporation

This declaration **is the parent's text, with the replacements below**. Every section, table, rule, cell, count,
seed, oracle, test and wait of `prereg/RD-01_firm_contracts.md` at the sha256 above is part of this declaration, read
with:

1. the general replacements S-1 to S-16 (section 2), which apply wherever the parent's words reach them;
2. the line-by-line replacements of section 3, each citing the parent's line and a short quote from it.

Where a replacement and the parent's words differ, the replacement is the declaration. Where section 3 is silent on a
parent line, section 2 governs it; where both are silent, the parent's words stand (section 5 lists what stands, and
section 4 lists every line the search of section 7 found that needs no change, with the reason). Section numbers,
item numbers, cell names, run names and test names are the parent's. **The labels S-1 to S-16 are this file's; the
parent's own labels (its gaps G-1 to G-14, its unread terms U-1 to U-12, its adapters A-1 to A-11) keep the parent's
meaning** (the red team's m-1).

### 0.2 The id scheme (proposed; the lead assigns at the pin)

Each search-years delta takes the next free described-reading number, in the order of its parent: **RD-06** for this
file (RD-01's), RD-07 for RD-02's, RD-08 for RD-03's, RD-09 for RD-05's part F, RD-10 for RD-04's. The pinned name is
`prereg/RD-06_firm_contracts_search_years.md`. **New numbers, not a suffix such as `RD-01S`**, for two reasons (the red
team's m-9): the reader takes a declaration's id from its path as `RD-` and digits (`extended/reader.py`'s
`DECLARATION_ID`), so a manifest, ledger or token naming `prereg/RD-01S_...` would be attributed to RD-01; and a name
beginning `RD-01_` would be found by the parent's own T-0 glob. The pinned name ends in `_search_years.md`, so it
matches no other reading's T-0 glob (`RD-*_firm_contracts.md` among them).

### 0.3 The parent, superseded before any run

No result of the parent exists: the read ledger holds no line of RD-01 and no file `results/fc_*.csv` exists at this
draft. At this file's pin the parent is **superseded, never run**: no run takes its three purposes, its result files
are never written, and its id is never a manifest's `prereg_id`. The reader cannot see a withdrawal (the audit's R-8
registry is not built), and its held-out rule 4 refuses the parent's judged reads only until a market's verdict row
exists; so the supersession is enforced by the build (section 6, B-1), held now by T-0's code check (N-1: no new code
takes up the parent's declaration constant or its purposes, and after the pin none may), and recorded in the pinning
row.

### 0.4 What changed from the first text (the red team's read, as the lead ruled on it)

| finding | the first text | this text | where |
|---|---|---|---|
| B-1 | the references' rows compared with U1's and Q-44's files on both arms; Q-44's verdict rows cited beside | every comparison with U1's or Q-44's rows, and every citation of them, on the **point arm only**; a needed figure re-derived from per-start rows of search-year starts; Q-44's pooled file never cited | S-8; D-29, D-51, D-55, D-58, D-63 |
| B-2 | P-16 re-built on the cut, its marks re-resolved on the search years; a cut identity reading the whole window | P-16's offered marks **fixed to its registered set** (S-3); the cut identity replaced by **a nested cut inside the search years** (S-4) and B-1's point-arm equality; **no new identity reads 2024 or later**; the registered reproduction identities untouched | S-3, S-4, S-8 |
| M-1 | the verdict constants re-estimated with P-11's eras, the second era 2023 alone | **two eras equal to the calendar halves, 2020-21 and 2022-23**, a declared rule | S-5 |
| M-2 | lines of the parent missed; the search terms the drafter's alone | the red team's extra terms added to the recorded set (section 7); every line they find cited or listed; A-11's per-R shift cited (D-56) | sections 3, 4, 7 |
| m-1 | the replacements labelled G-1 to G-16 | labelled S-1 to S-16 | throughout |
| m-2 | the siblings cited by their draft paths | RD-09 cites this file by id and pinned path at its pin; this file names RD-09 by id only | 9 |
| m-3 | the wrapper unspecified | its four inputs, the manifest left uncut, and every vendored check switched off, listed | S-2 |
| m-4 | the choice-block authorisation called a guard | stated as a no-op for this purpose; the wrapper and the refusal are the guard | S-2 |
| m-5 | "no first-half reading touches a second-half session" | true on the point arm; on the verdict arm the halves share S-5's constants, labelled | S-7 |
| m-7 | T-0's checks could not all fail | T-0 rebuilt (section 7) | `tests/test_rd_search_years_drafts.py` |
| m-9 | the reason for new ids | corrected | 0.2 |
| N-1 | supersession enforced by the build alone | T-0's code check added | 0.3 |

## 1. Why, and what it does to what the reading can show (E-051)

**Why.** Under E-208 every choice and every map the journey search draws on is made on the search years, and the
held-out years are read once, by the joint confirmation (E-221, O-1). The parent reads the whole development window, its
late block by name, and its judged-block purposes; any lever range drawn from its menu would carry a held-out read into
the search (CHARTER 3.3 (a), 3.6 (a)). O-7 rules that the reading is re-declared on the search years.

**What it does to what the reading can show.** The menu describes the search years only. The starts read at each
horizon are fewer (S-6): at month 12 the starts are those with 252 sessions inside the search years, so the headline
holds fewer kept windows and more readings print "too few independent windows"; each half (S-7) holds about two years,
so most month-6 and month-12 half readings print the sign count alone. The stability flag compares two halves of four
years instead of the search years against the held-out years. The verdict arm's shift is the search years' own,
estimated with the two halves as its eras (S-5), so verdict rows are not comparable with any whole-window row, and the
verdict arm's halves share that constant (S-7). P-16 is its registered design: its offered marks are the registered
set (S-3), a whole-window choice of Stage 2's, inherited and labelled (S-12). Nothing else of the reading changes: the
plans, the cells, the corners, the counts, the uncertainty method and the oracles are the parent's.

## 2. The general replacements

- **S-1. The window.** The development data are NQ 1-minute bars from 2020-01-02 to 2023-12-29, the search years
  (E-208). The held-out years 2024-01-02 to 2026-07-16 are never read by this reading, under any purpose, by any of its
  runs, gates, checks, or beside readings; NQ from 2026-07-17 is never read. Wherever the parent says "the development
  window", "2020 to 2026", "2020-2026" or "the whole window" of what this reading reads, read the search years. A pinned
  calendar (E-029, E-050) or a release file of section 5.5 is used only on days inside the search years.
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
     manifest's day count and last day with the A1 cache's manifest (its `day_list`), and both stay whole, since they
     are files' descriptions, not rows read;
  3. **A3's walks**, the `pd.read_parquet` of `atlas_a3.cached_walk`: the rows dated after 2023-12-29 dropped;
  4. **the day list** each builder passes to the walk and the bounds: cut at 2023-12-29.

  **The vendored checks switched off on the cut, and no others:** (a) `rc_dev_test.trade_problems` as
  `user_journey.build_p16` calls it -- P-16's trades against `rc_width_screen.csv`'s cell row and the registered content
  hash, whole-window facts that cannot hold on four years; (b) where the build calls it, `a3_brk30`'s check that the
  configured eras are P-11's ("the bounds are ..., not P-11's"), since S-5 passes the halves as the eras. Each switched-
  off check is named in the run's manifest. The day blocks and dates handed to the replay and to the gate end at the
  search years' last session, and **the runner refuses, before any replay, any block or date after 2023-12-29** (every
  day of an uncut day list makes a block, so an uncut input is caught here). **If a registered builder cannot be cut at
  these reads, or another vendored check fails on the cut, the build stops and reports; this declaration does not fall
  back** to a whole-window build cut afterwards, and switches off no other check.
- **S-3. P-16's offered marks, fixed to its registered set** (the lead's ruling on B-2). P-16's builder admits a mark by
  its unresolved share pooled over every day it is given (`resolved_coin.mark_resolution`), so on the cut the shares
  would be the search years' and the marks could differ from the registered design's. Here the marks are **never
  re-resolved**: `resolved_coin.mark_resolution`, as `rc_width_screen.build` calls it at P-16's stop (`stop_ticks` `150`), returns for
  the call the registered table -- `vendor/stage2/results/rc_width_screen.csv` section `marks`, the rows at that stop, the
  columns `stop_ticks`, `slot` and `offered` only, the file checked first against `vendor/MANIFEST_stage2.sha256` --
  so `offered_marks` gives the registered set, whose count must equal the `rc_s150_all` cell row's `marks_offered`
  (refusing). The set is part of the registered design, a whole-window choice of Stage 2's, inherited and labelled in
  S-12's existing entry ("P-16's mark cutoff resolved on the whole window"). P-14's rung map is already a pinned file
  (`atlas_a3.rung_rule`) and needs nothing.
- **S-4. The nested cut, refusing** (replacing the first text's cut identity; the lead's ruling on B-2). Before any
  replay, the reading's own process builds each design's stream twice on the cut, with S-3's marks: on 2020-01-02 to
  2022-12-30 and on 2020-01-02 to 2023-12-29. Their **point-arm** day blocks must be equal up to 2022-12-30, block for
  block, every field, the per-R outcomes included: a causal build with fixed marks gives exactly this, so it tests the
  wrapper and the build's causality without a held-out day. It reads the search years only, needs no purpose, and
  writes its pass or fail lines to the run's log and manifest. A failure stops the reading. With S-8's point-arm
  equality it is the whole check that the cut stream is the registered design's. **No identity these deltas introduce reads 2024 or later** (the lead's ruling rn-5); the parent's declared identities keep
  their declared whole-window form, labelled so (S-8); the registered reproduction identities are untouched (S-8).
- **S-5. The verdict arm's constants, re-estimated on the search years, with the halves as eras** (the lead's ruling on
  M-1). The parent's verdict arm shifts every R to the bound "estimated on the whole development window". Here `e`,
  `lb`, `e_by_rr` and `lb_by_rr` are `atlas_a3.bounds`'s, as the registered builder calls it, on the search-year trades
  and days, at the registered trial count and era seed, **with its eras declared now as the two calendar halves,
  2020-2021 and 2022-2023** (S-7's halves), passed in the bounds' configuration for the call. P-11's spans would leave
  2023 alone as an era, whose whole-year bootstrap cannot vary, so they are not used. Each R's bound is the pooled one,
  or the lower era's when the whole-year bootstrap flags the eras, as the registered rule says. **Printed in every
  result file's manifest, per design and R:** the flag, the bound read, the pooled bound and each era's. **Reason:**
  inherited, the constants would carry a held-out read into every verdict row and so into any lever range read from it
  (CHARTER 3.3 (a)); re-estimated, the arm is a function of the search years alone. The `point` arm (as traded) carries
  no constant and is unchanged. The verdict blocks are `shifted_blocks` of the point blocks by these constants, which
  the runner's per-stream shift check (`build_with_deltas`, r6) holds.
- **S-6. The starts and the horizon embargo** (CHARTER 3.6 (d)). The starts are every start day U1 reads inside the
  search years. A start is read at horizon h only if h sessions remain inside the search years: on the cut replay a
  start observes no session after 2023-12-29, so `u_select.block(records, None, h)` gives exactly these. U1's long
  replay of up to 252 sessions and its exact-length runs stop at the cut. Wherever the parent says "every start",
  "all starts" or "every start day" of what is replayed or read, read the search-year starts with the horizon left.
  By start year: 2020 to 2023 only, means only, not purged within the search years, labelled so.
- **S-7. The blocks: the late block replaced by the search years' second half.** On the cut replay the parent's early
  block (the starts of 2023 and before, purged) equals the headline and its late block is empty, so both are replaced:
  - **all**: every search-year start with h sessions inside the search years (the headline);
  - **first**: the starts of 2020 and 2021, each read at h only if h sessions remain before the first session of 2022
    (D-621 (4)(b)'s purge, moved to the half's end);
  - **second**: the starts of 2022 and 2023, read at h only with h sessions inside the search years.

  **On the point arm no first-half reading touches a second-half session. On the verdict arm the halves share S-5's
  constants, estimated on both halves** -- the same kind of shared constant the parent's N2 disclosed -- and every
  verdict-arm half row is labelled so (the red team's m-5). The stability flag is printed on both arms; the point arm's
  is labelled "the halves share no constant". **Reason for the halves:** the menu's flag ("not stable across blocks")
  needs two disjoint stretches read apart; two calendar halves of equal length, fixed by the calendar before any read
  and cut at a year's end as the parent's blocks were, keep it without reading a held-out day. At 12 months each half
  is close to one start year, so the flag there is weak; the start-year rows beside are the fuller description. The
  vendored `u_select.block` fixes its years, so the halves are a function of this repository (B-3). Nothing is chosen
  on any block. **Considered and not taken:** no blocks (it loses the flag); halves by start count (a cut that moves
  with the data).
- **S-8. The identities, the comparisons and the citations** (the lead's ruling on B-1). The parent's registered
  reproduction identities (9.1) are untouched: they run as the parent states them, on the whole window, from
  `identity/*.py` under the purpose `identity` and their own rows, reproduce Stage 2's registered files, write no
  outcome of any cell and are ledgered in a clean run. Inside the reading's own run:
  - **every comparison with U1's or Q-44's per-start rows is on the point arm only**, on the starts whose 252-session
    replay ends inside the search years, every column the parent names, refusing; no row of another arm or of a later
    start is loaded. The verdict arm is never compared with a registered file: its constants are the search years'
    (S-5);
  - **every citation of U1's or Q-44's rows is of their point-arm per-start rows**, on the same starts; a figure the
    parent cites from them is re-derived from those rows; Q-44's verdict rows and its pooled file
    `results/user_beside.csv` are never cited.
- **S-9. The gate on the search years.** Every gate beside draws its resampled days from the search-year day blocks
  only. Its pairs are formed with the reference's own search-year gate at the same seed and the same number of paths
  (the same pool of days, so the same day draws, `SharedDayTable`'s indices being a function of the seed and the
  number of blocks), not with the registered gate paths, which draw from the whole window. The two references'
  search-year gates are therefore run and read beside as the pairs' references; the registered gate paths stay S-8's
  reproduction identities.
- **S-10. The outputs.** The result files are new files, never the parent's: `results/fcs_reading.csv`,
  `results/fcs_gate.csv` and `results/fcs_menu.csv`, each through `extended.results.write_result` with its sidecar
  manifest, `prereg_id` this file's id at the pin, the window 2020-01-02 to 2023-12-29, S-4's result, S-5's constants
  and flags, S-2's switched-off checks, S-12's list, the rows under which the parent's identities held, and every
  manifest field the parent's section 15 lists. A file of the parent's name is never written by this reading.
- **S-11. No judged-block purpose.** This declaration reads no day of the held-out years, so it names no purpose of the
  reader's judged-block form: it carries no line of that form at all, and the reader refuses any judged read citing it
  (the purpose must be on the declaration's own line). The parent's line is the parent's and is never taken (0.3).
- **S-12. The held-out read ledger, inherited and labelled** (CHARTER 3.6 (b); no figure cited). This reading rests on
  designs and records that read the held-out years before it: P-14 fixed as R* from the whole window (Stage 2 D-626);
  P-14's rung map and P-16's mark cutoff resolved on the whole window (E-203 S-2), the latter fixed here as P-16's
  registered mark set (S-3); P-16's stop chosen on each block (Stage 2 D-554); the registered state tables and
  protocols as Stage 2 registered them; Stage 2's Lucid reads beside Topstep's seats on whole-window gate paths (D-575,
  D-577, D-593, D-601) and U1's `p16_5+1` rows; program U's nine families, which read P on the late block, and its
  family 5 (Lucid seats beside Topstep's, both blocks); U1's whole-window start rows (Stage 2 D-620) and Q-44's
  per-start rows, which S-8 compares and cites on the point arm and search-year starts only; Stage 2's signal search
  over the whole window; and the parent's own pinned text, declared over the whole window and never run. These are the
  registered designs' and Stage 2's; nothing here re-estimates them but S-5's constants, and every result file of this
  reading names them.
- **S-13. Prior exposure, re-read.** The parent's prior-exposure rows stand as records. Where a row's bearing reads "the
  late block is late development, not out of sample", read: those reads were of the held-out years; they are S-12's
  entries; this reading reads none of those years.
- **S-14. The binding.** The parent's "the blocks read here are recorded as read for firm contracts on P-14 and P-16"
  reads: the search years, and their two halves, are recorded as read for firm contracts on P-14 and P-16; the
  held-out years are not read by this reading and are recorded as unread by it.
- **S-15. In sample.** Every statement made from this reading, and the operator's choice from its menu, is a
  description of the search years, in sample, with no confirmation (E-023 (1)); the held-out years stay unread by it.
- **S-16. Reruns.** The reader ledgers no choice-block read, so its once-per-purpose refusal does not reach this
  reading. The parent's rule is kept by the lead instead: only the first complete clean run is read; a restart or a
  rerun (an adapter fix, the failure protocol's replication) is recorded by the lead with its log under a decision row
  naming this file, which says which run replaces which and why; a result file is never overwritten (S-10).

## 3. Every dependency in the parent, line by line

The parent's lines as numbered in its LF text at the pinned sha256. A row's lines are one line, a range whose joined
text holds the quote, or a list of lines each holding the quote. The replacement is this declaration's.

| # | parent lines | where | quote | replacement |
|---|---|---|---|---|
| D-01 | L78 | header table, development data | "NQ 1-minute bars, 2020-01-02 to 2026-07-16" | NQ 1-minute bars, 2020-01-02 to 2023-12-29, cut at the read (S-1, S-2) |
| D-02 | L80 | header table, blocks | "the early and late blocks per measure by `u_select.block`" | all search-year starts the headline; the first and second halves beside (S-7) |
| D-03 | L81 | header table, runs | "16 gates beside (section 7)" | the parent's 16 gates beside, and the two references' search-year gates as their pairs' references (S-9) |
| D-04 | L120-L121 | 1, why described | "three-month stretches of the late block" | the same reason holds a fortiori on the search years: fewer independent stretches still (section 1) |
| D-05 | L125 | 1, the operator's choice | "a described development reading" | a described reading of the search years (S-15) |
| D-06 | L127 | 1, the operator's choice | "a description of the development window" | a description of the search years (S-15) |
| D-07 | L151, L153 | 2.2 | "every start" | every search-year start (S-6) |
| D-08 | L153 | 2.2 | "every start day from 2020 to 2026" | every start day from 2020 to 2023 (S-1, S-6) |
| D-09 | L198 | 3, U1's row | "five Topstep seats and one Lucid seat, every start" | a record; U1's rows are whole-window, and 9.1 item 3 (a) compares them under S-8 (on the identity's own row) |
| D-10 | L199 | 3, program U family 5 | "both blocks" | a record; a held-out read by Stage 2, entered in S-12 |
| D-11 | L201 | 3, program U's nine families | "the late block is late development, not out of sample" | those reads were of the held-out years; S-12's entries; none read here (S-13) |
| D-12 | L217 | 3, what is known of the direction | "program U's family 5" | a record; its read spanned the held-out years (S-12) |
| D-13 | L397 | 4.7, G-11 | "rule changes over 2020-2026" | rule changes over 2020-2023 (S-1); today's terms on every search-year start |
| D-14 | L637-L638 | 5.5, the count | "by release and year" | by release and year, 2020 to 2023: the trades of the search-year stream only (S-1); the condition of 7.3's four news runs ("if P-16's count of 5.5 is not zero") is read on this count |
| D-15 | L701 | 6, its title | "Data, blocks and the unit" | section 6 as items 1, 2, 4, 5 and 6 are replaced in D-16 to D-21 |
| D-16 | L703 | 6 item 1 | "one development start day" | one search-year start day (S-6) |
| D-17 | L704 | 6 item 1 | "for up to 252 sessions plus" | for up to 252 sessions, stopping at the cut, plus U1's exact-length runs inside the search years (S-6) |
| D-18 | L706-L709 | 6 item 2 | "verdict arm is a function of 2024-2026 through that one constant" | the verdict arm's constants re-estimated on the search years with the halves as eras (S-5); no reading is a function of the held-out years |
| D-19 | L710 | 6 item 3 | "the same start days, blocks and seeds" | the same search-year start days, S-7's blocks and the parent's seeds |
| D-20 | L712-L717 | 6 item 4 | "and on the late block (`u_select.block(records, "late", h)`" | item 4 is S-7: all, first and second, each at its measure's h; the stability flag on first and second |
| D-21 | L713-L714 | 6 item 4 | "on the early block" | replaced by S-7's first half; the parent's early block equals the headline on the cut replay |
| D-22 | L718 | 6 item 5 | "No NQ from 2026-07-17" | this reading takes no NQ after 2023-12-29 (S-1); NQ from 2026-07-17 is not on disk and never read |
| D-23 | L719-L721 | 6 item 6 | "The judged block's seal" | the search years need no seal: the reading authorises 2020-01-02 to 2023-12-29 only (S-2) |
| D-24 | L723 | 6 item 6, the parent's purposes | "`firm_scorecard`, `firm_ladder_beside`, `firm_gate_beside`" | none (S-11); this file carries no line of the reader's judged-block form |
| D-25 | L727-L729 | 6 item 6 | "**Once per purpose:**" | S-16: the lead's first-complete-run rule; no purpose to ledger |
| D-26 | L769 | 7.3 | "Each runs both arms, every start" | each runs both arms, every search-year start, the long replay and the exact-length runs stopping at the cut (S-6) |
| D-27 | L775-L776 | 7.4, the gate | "TS's gates are the identities (9.1 item 1)" | the gates draw search-year days (S-9); TS's search-year gates are run as the pairs' references; the registered gate paths stay S-8's reproduction identities |
| D-28 | L808 | 8, horizons and blocks | "all, early and late per measure" | all, first and second per measure (S-7) |
| D-29 | L823-L825 | 9.1 item 1 | "both arms, every start, every column as E-010 compared them" | unchanged as the registered reproduction identity under `identity/` (S-8); inside the reading's run, the references' comparison with U1's rows is on the **point arm only**, on the starts whose 252-session replay ends inside the search years (S-8) |
| D-30 | L831 | 9.1 item 2 | "at every start and all 500 paths as the run's first stage" | unchanged as the identity script's stage (S-8); S-4's nested cut runs first in the reading's own process |
| D-31 | L832, L836 | 9.1 item 3 | "every start" | unchanged: the Lucid identities, whole-window, under `identity/` (S-8) |
| D-32 | L859 | 9.3 | "stream and block" | stream and S-7's block |
| D-33 | L862-L863 | 9.3, G-3's count | "by release and year" | by release and year, 2020 to 2023 (D-14) |
| D-34 | L376, L902, L948 | 4.6 A-10; 9.3; 10.1 item 9 | "every start" | every search-year start (S-6) |
| D-35 | L908 | 10.1 | "every block of" | every block of S-7 |
| D-36 | L939-L940 | 10.1 item 8 | "paired with TS's registered gate paths" | paired with TS's search-year gate at the same seed and paths (S-9) |
| D-37 | L953-L954 | 10.1 item 11 | "the early and late blocks and the" | the first and second halves and the start years 2020 to 2023 beside (S-6, S-7) |
| D-38 | L957 | 10.1 item 11, the stability flag | "opposite signs on the early and late blocks" | opposite signs on the first and second halves (S-7) |
| D-39 | L1003-L1004 | 10.2, its effect | "much of the late block at months 6 and 12" | much of each half at months 6 and 12 (section 1) |
| D-40 | L1025-L1026 | 11, the operator's choice | "on the development window 2020-2026" | on the search years 2020-2023, the held-out years unread by it (S-15) |
| D-41 | L1029-L1030 | 11, the binding | "The blocks read here are recorded as read for firm contracts" | S-14 |
| D-42 | L1067 | 12, inherited seeds | "paired with the registered paths" | paired with the reference's search-year gate at the same seed (S-9) |
| D-43 | L1076 | 13 item 2 | "every block read, recorded as read" | the search years and their halves recorded as read for firm contracts (S-14); counted beside: the two references' search-year gates (S-9) |
| D-44 | L1100 | 14.3, T-0 | "the `Judged-block reads:` purposes parse and choose nothing" | T-0 is `tests/test_rd_search_years_drafts.py` (with this text), extended at the pin: the checks section 7 lists, each able to fail |
| D-45 | L1120-L1123 | 15, files | "`results/fc_reading.csv`" | `results/fcs_reading.csv`, `results/fcs_gate.csv`, `results/fcs_menu.csv` (S-10) |
| D-46 | L1125 | 15, manifests | "`prereg_id` = `RD-01`" | `prereg_id` this file's id at the pin (S-10) |
| D-47 | L1134 | 15, weight | "Every start on two arms" | every search-year start on two arms; the replays are shorter than the parent's |
| D-48 | L1138-L1141 | 15, a restart or a rerun | "passes `repeat="E-NNN"`" | S-16 |
| D-49 | L1167-L1169 | 16 item 6, the name | "must match the test's glob `RD-*firm*.md`" | the pinned name is 0.2's; this file's T-0 asserts it (D-44) |
| D-50 | L73 | header table, id | "RD-01" | this file's id at the pin (0.2); every result's `prereg_id` is it (S-10) |
| D-51 | L937-L938 | 10.1 item 7, TS's placement and Focused Trader rows | "TS only, from Q-17's own reading, not rerun here" | TS only, from Q-44's **point-arm** per-start rows (Q-17's reading) on the starts whose 252-session replay ends inside the search years, each figure re-derived from them, not rerun here (S-8) |
| D-52 | L79 | header table, the unit | "one start day, replayed as U1 replays it" | one search-year start day, replayed as U1 replays it, stopping at the cut (S-6) |
| D-53 | L159 | 2.3, the trades | "`rc150_dev_test.TRADES_SHA256`" | P-16's registered trades on the cut stream, its offered marks the registered set (S-3); the content hash, a whole-window check, is switched off on the cut (S-2) and replaced by S-4 and S-8's point-arm equality |
| D-54 | L196-L197 | 3, Stage 2's Lucid reads | "500 gate paths" | records; whole-window gate reads by Stage 2, entered in S-12 |
| D-55 | L249 | 4.1, TS | "TS is the identity (9.1 item 1)" | TS is the reference: its registered reproduction identity unchanged (S-8); in the run its rows are checked on the point arm only (S-8) |
| D-56 | L663-L665 | 5.5, the bracket on the verdict arm | "takes the same per-R shift to its R's registered bound" | takes the same per-R shift to its R's search-year bound (S-5); no builder loads `lb_by_rr` from a registered gate file for A-11's liquidation |
| D-57 | L705 | 6 item 1 | "U1's exact-length runs" | U1's exact-length runs inside the search years (S-6) |
| D-58 | L735 | 7.1, the references | "they must reproduce the registered rows (9.1 item 1)" | on the point arm only, on the starts whose 252-session replay ends inside the search years (S-8); the registered reproduction identity unchanged |
| D-59 | L751, L752 | 7.3, the references | "reference (identity)" | reference; its point-arm rows checked as S-8 says |
| D-60 | L806 | 8, arms | "`verdict` the headline, `point` beside" | `verdict` at S-5's search-year constants the headline, `point` beside |
| D-61 | L838 | 9.1 item 4 | "one of its design's registered offered trades" | one of its design's offered trades on the cut stream (S-3, S-4) |
| D-62 | L1127 | 15, the manifests' run counts | "16 gates)" | the parent's 16 gates and the two references' search-year gates (S-9) |
| D-63 | L1243 | Appendix R, `focused_trader_program` | "TS only, beside from Q-17" | TS only, beside from Q-44's point-arm per-start rows on the search-year starts of S-8 |

## 4. Unaffected, because

Every other line the search of section 7 finds in the parent, with the reason it needs no change. The first bullets
are the first text's; the rest, grouped by the parent's sections, are the lines the red team's extra terms add.

- **L3**: the parent's own status line and date; the parent stays pinned as it is (0.3).
- **L22, L27, L35**: the parent's table of changes between its drafts, a record of how it was made; each rule it
  summarises is cited at its own line (D-16 to D-49) or governed by section 2.
- **L85**: NQ's confirmation tests and the reserve from 2026-07-17, which this reading never reads; unchanged.
- **L92**: "a matched pair with Topstep's on every start day": the pairing holds on every start read; S-6 sets the
  starts.
- **L139, L155**: a rule's applicability date (Fast Pass's terms for accounts opened on or after a date) and the parent's
  gap G-11; a term of the record, not a read window. That gap itself is D-13.
- **L154**: describes Stage 2's practice (today's rules replayed over its history).
- **L210**: the drafter's disclosed reads of the release calendars; a record.
- **L282, L369, L370, L377, L396, L696, L890, L943, L1102, L1232**: a firm's clock in calendar days, or the record key
  that translates it to sessions; a rule's term, unchanged.
- **L25, L631, L634, L635, L646, L895, L896, L899, L1155**: the pinned calendars and release files and their hashes;
  the files are fixed as declared, and S-1 uses their days only inside the search years.
- **L406, L418, L435, L448**: "blocks" in another sense (a trade's day block, `DayBlock`, or a rule that blocks a
  request).
- **L520, L1018**: a property of a term on any start (monotone in one direction); it holds on each search-year start.
- **L679, L918, L941**: a rule's or a measure's year (idle for the rest of the year; a year's payouts; the gate's
  two-year growth on resampled days that carry no date, S-9).
- **L973, L974, L986**: 10.2's window rule, stated per block; it applies unchanged to S-7's blocks.
- **L1028**: no confirmation; NQ from 2026-07-17 is never read; unchanged.
- **L1047, L1049, L1055, L1059**: section 12's seed check, its date and "block" meaning the seed block; the seeds are
  inherited unchanged (section 8).
- **L1181**: the operator's written question to DayTraders ("historical data"); unchanged.
- **L1196**: E-015's limits "never block"; unchanged.
- **L1, L9, L10, L11, L20, L21, L23, L24, L29, L30, L31, L38, L44, L45, L47, L49, L50, L51**: the parent's status, history and table of changes between its drafts (before section 0): records; each operative rule they summarise is cited at its own line or governed by section 2
- **L54, L60, L67, L68, L74, L83, L91, L101, L111, L112, L113, L136, L137, L149, L160, L162, L164, L179, L184, L186**: what the reading is, its frame and the user held fixed (sections 0 to 2): the registered trades, tables, plans and conduct settings, described and unchanged; the trades are the cut stream's (S-2, S-3), the starts S-6's
- **L200, L207, L208, L213, L216**: prior exposure and the drafter's disclosed reads (section 3): records; the whole-window reads among them are S-12's entries
- **L231, L234, L235, L243, L258, L261, L276, L278, L284, L285, L287, L289, L291, L295, L298, L302, L325, L333, L334, L350, L362, L363, L368, L371, L372, L374, L375, L387, L388, L391, L392, L395, L399, L400, L404, L412, L413, L434, L437, L438, L445, L446, L450, L460, L470, L486, L487, L495, L505, L509, L510, L525, L528, L535, L536, L539, L540, L544, L554, L561, L563, L564, L594, L602, L604, L605, L610, L615, L618, L619, L620, L623, L628, L629, L632, L633, L639, L642, L644, L645, L650, L653, L655, L657, L661, L671, L683, L689**: the contracts on the engine, their adapters, gaps, costs, table inputs, unread terms, brackets and release dates (sections 4 and 5): a rule's term, a payout gate, a tier-1 window, an upper-bound label or a count of days, not a read window; their days are the search years' (S-1)
- **L725, L726**: section 6's identity-stage lines: the registered reproduction identities, unchanged (S-8)
- **L743, L744, L764, L765, L766, L771, L774, L786, L787, L788, L791, L793, L795, L797, L801, L803, L804, L807, L813**: the cells, the runs and the parameters (sections 7 and 8): names, kinds, both-ends terms and counts, unchanged
- **L815, L817, L819, L820, L826, L827, L828, L833, L847, L848, L852, L871, L876, L881, L884, L886, L887, L889**: the identities, oracles and mechanics (section 9): the registered reproduction identities and their gate paths unchanged (S-8); the oracles' bounds and the mechanics' counts are rules, read on S-6's starts and S-7's blocks
- **L914, L919, L920, L923, L925, L934, L935, L942, L944, L945, L950, L970, L975, L976, L977, L978, L979, L980, L981, L983, L985, L988, L989, L990, L992, L1001**: the scorecard and the uncertainty (section 10): measures, windows of h starts, the ladder's and the gate's rules, read on S-6's starts, S-7's blocks and S-9's pool
- **L1009, L1014, L1027**: what the reading delivers (section 11): unchanged, on the search years (S-15)
- **L1036, L1037, L1038, L1039, L1040, L1041, L1042, L1043, L1044, L1045, L1048, L1051, L1053, L1054, L1056, L1058, L1065, L1068**: the seeds (section 12): inherited unchanged and by reference (section 8); the digits of a seed are not a date
- **L1075, L1081, L1085, L1086, L1101, L1104, L1105, L1108, L1109, L1110, L1112, L1113, L1115, L1135, L1136, L1143, L1144, L1145, L1146**: counting, the build, the tests and the run (sections 13 to 15): counts, adapters, tests and waits as the parent states them, the replay's inputs cut by S-2, the identities S-8's, the gates S-9's
- **L1153, L1163, L1165, L1185, L1195**: open before the pin, and the operator's items (section 16): the parent's pin record and the operator's reads and questions; unchanged
- **L1223, L1224, L1229, L1231, L1261, L1289, L1326, L1367, L1368**: Appendix R, the rule keys: a rule's term (a payout gate, a window, a count of sessions), unchanged

## 5. What does not change

The plans and their terms (section 2.1, 4, 5, Appendix R); the user held fixed (2.3), P-16's marks its registered set
(S-3); the adapters A-1 to A-11 and their switches (4.6); the gaps (4.7); the cost rule (4.8); the table's inputs
(4.9); every unread term and its reading (section 5); the cells, the corners, the one-at-a-time runs and their names
(section 7), and their counts: 30 replays, or 34 with the four news runs, 27 denial-ladder replays and 16 gates beside,
with the two references' search-year gates added beside (S-9); the parameters' classes (section 8); the registered
reproduction identities (9.1); the oracles (9.2); the mechanics (9.3) on the blocks of S-7; the scorecard, the paired
readings, the price grid, the evenness trade-off and the menu's flags (10.1) on the search years; the uncertainty
method (10.2) unchanged, its window counts the search years'; what the reading delivers and what each outcome means
(11) on the search years; the seeds (section 12), inherited unchanged and by reference (section 8); the counting (13);
the adapters' rules in code and tests T-1 to T-15 (14), T-0 replaced (D-44); the run's order and waits (15), S-4 added
before the reading; the operator's items (16).

## 6. The build list (for a later item; nothing here is built by this one)

- **B-1. The declaration.** `extended/firm_reading.py`'s `DECLARATION` names this file at its pinned name and
  `PURPOSES` is empty; `extended/firm_terms.py`'s `DECLARATION` likewise; `scripts/rd01_reading.py` (or a new runner
  beside it) drops `precheck`'s purposes and calls `reader.authorise_engine_read(reader.CHOICE_START,
  reader.CHOICE_END, ...)` with no purpose; it refuses to run if any argument or constant names the parent's path or
  purposes. T-0's code check (N-1) then passes in its after-pin form.
- **B-2. The cut** (S-2): a new module (for example `extended/search_years.py`) with a context manager wrapping, for
  the builders' calls, `propedge.data.bars.read_bars` as `atlas_a3.bar_arrays` calls it, `a3_resolution_map.load_a1`'s
  two frames, `atlas_a3.cached_walk`'s walks and the builders' day lists, cutting each at `reader.CHOICE_END` and
  leaving the manifests whole; the two switched-off checks of S-2 and no other; a refusal of any day block or date
  after `reader.CHOICE_END` in a job before any replay or gate.
- **B-3. The blocks** (S-7): a repository function `block(records, which, h)` for `which` in `all`, `first`, `second`;
  `extended/firm_reading.py`'s and `extended/firm_menu.py`'s `BLOCKS` become `("all", "first", "second")`;
  `extended/user_readings.py`'s `KNOWN_BLOCKS` and `READING_BLOCKS` and `_which` learn the halves; 9.3's counts by
  block (`COUNT_HORIZON`) and the stability flag read first and second, on both arms, labelled as S-7 says.
  `u_select.block` is not edited and is called only for `all`.
- **B-4. P-16's marks and the verdict constants** (S-3, S-5): the wrapper of `resolved_coin.mark_resolution` returning
  the registered table, with its count check; the halves passed as the eras to `atlas_a3.bounds` for the builder's
  call; `build_with_deltas` records the search-year shift; the `r6` check (one shift per stream) unchanged; the
  manifest carries S-5's printed constants.
- **B-5. The checks:** `identity/firms_identity.py` and the shared identities unchanged (S-8); S-4's nested cut as the
  runner's first stage; inside the run, `identity_problems` and the reference comparisons on the point arm only, on
  the starts whose 252-session replay ends inside the search years (S-8); TS's placement and Focused Trader rows read
  from Q-44's point-arm per-start rows on those starts (D-51, D-63).
- **B-6. The gate** (S-9): `registered_gate` and `paired_paths` pair each corner's gate with the reference's
  search-year gate at the same seed; `gate_reading` runs the two references' search-year gates first.
- **B-7. The outputs** (S-10): `write_all` and `manifest_params` write `results/fcs_*.csv` with this file's id and
  every field S-10 names.
- **B-8. Tests:** T-0 (`tests/test_rd_search_years_drafts.py`, extended at the pin); a T-3S on synthetic campaigns
  -- every reading is byte-identical when every session after 2023-12-29 is replaced, the runner refuses a stream with
  such a session, each first-half point-arm reading at h is byte-identical when every second-half session is replaced;
  B-2's wrapper on toy readers (rows after the cut never returned, the manifests whole, each reader restored on exit,
  on error too); B-4's marks wrapper on a toy table; S-4's nested cut on a synthetic causal build (passes) and on a
  planted non-causal one (fails).

## 7. The search that found section 3 (re-runnable)

Every line of the parent's LF text that matches any of these patterns (Python regular expressions, case-insensitive),
one per line between the markers, is cited in section 3 or listed in section 4 -- `tests/test_rd_search_years_drafts.py`
checks it, and checks that the patterns below are the test's own. The first nineteen are the first text's; the rest
are the red team's extra terms (`extra_terms.py` in the scratchpad's `wt-scout_o7`), added by the lead's ruling on
M-2. T-0 also checks: the parent's pin; every quote; no held-out date outside a never-read statement and no "read" or
"replay" beside one; no judged-block line; no typed decimal, percentage, dollar figure, integer or seed; the proposed
ids; the parents unrun; and (N-1) that no new code takes up a superseded parent. Each check is a function that
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

- **Counting.** No program family number and no level (E-023 (1)); the next numbered family's k is unchanged. The
  parent's counts hold (section 5), with the two references' search-year gates added beside (S-9). The parent's counts
  are never also spent: the parent is never run (0.3).
- **Seeds.** The parent's section 12, inherited unchanged and by reference (its block, statuses and inherited seeds);
  no seed is restated here, so the parent's T-0 still finds its block in no other declaration. The parent was never
  run, so none of its seeds has been drawn on the bars.
- **Confirmation.** None: nothing is carried; NQ from 2026-07-17 is never read.

## 9. Open before the pin

1. **The red team's re-read** of B-1 and B-2 in full, and of this text's other answers.
2. **The pin's edits, and only these:** the file renamed to 0.2's name; its title and status put in pin-time form; its
   id written where this draft says "RD-01S". T-0's pinned-name test passes only before the pin and is replaced by its
   pin-time form in the pinning commit.
3. **The siblings** (the red team's m-2): RD-09 cites this file by its id and pinned path and sha256, written into
   RD-09's text at the pin, after this file's sha256 is fixed; this file names RD-09 by id only. The lead pins them
   together.
4. **S-2's feasibility** is a build question; its stop-and-report clause is declared now.
5. **The pinning row** records the parent as superseded, never run (0.3).
