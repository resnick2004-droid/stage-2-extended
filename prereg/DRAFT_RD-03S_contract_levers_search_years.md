# DRAFT RD-03S: contract-use levers on the registered trades, on the search years only (reading CL-S) -- a delta declaration of RD-03, a described reading, unnumbered (E-023 (1))

**Status: a draft, not pinned (O-7, the lead's ruling in E-221).** Drafted on wt/wt-firms, 2026-11-18. It re-declares
`prereg/RD-03_contract_levers.md` on the search years alone, so that no part of the reading touches NQ's held-out years
(E-208), which E-221 (O-1) keeps for one joint fixed-sequence confirmation across firms. The parent is not edited: it
stays on record, pinned, and is never run (section 0.3). The red team reads this draft before it is pinned; the lead
assigns its id at the pin (section 0.2). Its siblings state the same general replacements for RD-01 and RD-02; each
draft is complete on its own.

| field | value |
|---|---|
| id | proposed **`RD-08`** at the pin (section 0.2); until then `RD-03S` |
| parent | `prereg/RD-03_contract_levers.md` sha256 `9a22532d3a32eebf412afccd5b0e0f47a0479cb3699e9e0d76a6629d9d8fb803` (of its LF text), pinned by E-152 |
| reading | CL-S: the parent's reading CL, stage 0 and every cell, run and reading as the parent declares them, on the search years |
| kind | a **described reading** (E-023 (1), E-134 (1)): never carried; no program family number, no level, no pass line, no pick |
| development data | NQ 1-minute bars, 2020-01-02 to 2023-12-29 (the search years, E-208), read only inside Stage 2's engine by P-14's and P-16's registered builders, cut at the read (G-2) |
| held-out years | 2024-01-02 to 2026-07-16: never read by this reading, under any purpose (G-1, G-10) |
| blocks | all search-year starts (the headline); the search years' first half and second half beside, each per measure at its h (G-6) |
| judged-block purposes | none (G-10) |
| stage 0 | on the search years' bound edges and rungs (G-16); the zero edge set unchanged |
| confirmation | none; NQ from 2026-07-17 never read |
| the build | not built by this item: section 6 is the build list for a later item |

## 0. What this file is, and how it reads its parent

### 0.1 The incorporation

This declaration **is the parent's text, with the replacements below**. Every section, table, rule, cell, count,
seed, oracle, test and wait of `prereg/RD-03_contract_levers.md` at the sha256 above is part of this declaration, read
with:

1. the general replacements G-1 to G-16 (section 2), which apply wherever the parent's words reach them;
2. the line-by-line replacements of section 3, each citing the parent's line and a short quote from it.

Where a replacement and the parent's words differ, the replacement is the declaration. Where section 3 is silent on a
parent line, section 2 governs it; where both are silent, the parent's words stand (section 5 lists what stands, and
section 4 lists every line the search of section 7 found that needs no change, with the reason). Section numbers,
item numbers, cell names, run names and test names are the parent's. Where the parent cites RD-02's section 9.2 for
its method (10.2), that method is window-free and stands as RD-02 pins it.

### 0.2 The id scheme (proposed; the lead assigns at the pin)

RD-06 for RD-01's delta, RD-07 for RD-02's, **RD-08 for this file**, RD-09 for RD-05's part F, in the order of the
parents. The pinned name is `prereg/RD-08_contract_levers_search_years.md`; it matches no other reading's T-0 glob (the
parent's T-0 takes `*contract_levers.md` with its two exact names). New numbers, not a suffix: the reader reads an id
as `RD-` and digits (`extended/reader.py`'s `F_ID`, `DECLARATION_ID`), so `prereg/RD-03S_...` would be read as RD-03,
and a `repeat=` row naming the parent would authorise a rerun of this file.

### 0.3 The parent, superseded before any run

No result of the parent exists: the read ledger holds no line of RD-03 and no file `results/cl_*.csv` exists at this
draft. At this file's pin the parent is **superseded, never run**: no run takes its four purposes, neither stage 0 nor
any step runs under it, its result files are never written, and its id is never a manifest's `prereg_id`. The reader
cannot yet see a withdrawal (the audit's R-8 registry is not built), and its held-out rule 4 refuses the parent's judged
reads only until a market's verdict row exists; so the supersession is enforced by the build (section 6, B-1) and
recorded in the pinning row. RD-05's part F reads its `TS-N` rows from this file's `naf` cells in place of the parent's
(`prereg/DRAFT_RD-05FS_firm_modes_part_f_search_years.md`).

## 1. Why, and what it does to what the reading can show (E-051)

**Why.** Under E-208 every choice and every map the journey search draws on is made on the search years, and the
held-out years are read once, by the joint confirmation (E-221, O-1). The parent reads the whole development window,
its late block by name and its judged-block purposes, and its stage 0 rests on whole-window edges; CHARTER 3.6 (b) lists
"RD-03's whole-window lever readings" among the reads a search must carry. O-7 rules that the reading is re-declared on
the search years, so its rows can bound a lever range (CHARTER 3.3 (a)).

**What it does to what the reading can show.** The menu describes the search years only. Each measure's starts at its
horizon h are fewer (G-5), so the headline holds fewer kept windows and more readings print "too few separated windows
for an interval"; each half (G-6) holds about two years, so most half readings at months 6 to 12 print the sign count
alone -- and the levers that bind only after a lost funded account (Back2Funded) are the rare, lumpy differences that
fewer windows resolve least. The stability flag compares two halves of four years. The verdict arm's shift and stage
0's bound edges are the search years' own (G-4, G-16). Nothing else changes: the levers, the grid, the counts, the
uncertainty method and the oracles are the parent's.

## 2. The general replacements

- **G-1. The window.** The development data are NQ 1-minute bars from 2020-01-02 to 2023-12-29, the search years
  (E-208). The held-out years 2024-01-02 to 2026-07-16 are never read by this reading, under any purpose, by stage 0,
  any of its runs, gates, identities in its own run, or beside readings; NQ from 2026-07-17 is never read. Wherever the
  parent says "the development window", "2020-2026" or "the whole window" of what this reading reads, read the search
  years. A pinned calendar (E-029, E-050) is used only on days inside the search years.
- **G-2. The cut at the read.** The reading's processes authorise the engine's reads with
  `extended.reader.authorise_engine_read` on 2020-01-02 to 2023-12-29 -- the choice block, which needs no purpose and is
  not ledgered -- and no bar or atlas row dated after 2023-12-29 reaches any function of the registered builders, stage
  0, the replay, the gate or the reading: the vendored readers the builders call are wrapped for the call so that every
  row after 2023-12-29 is dropped at the read, and restored after it (nothing vendored is edited). The day blocks and
  dates handed to the replay and the gate end at the search years' last session, and the runner refuses, before any
  replay, a block or a date after 2023-12-29. **If a registered builder cannot be cut at its reads, the build stops and
  reports; this declaration does not fall back** to a whole-window build cut afterwards. The builders' own whole-window
  checks (the registered trades' content hash, the registered edge rows) cannot hold on the cut and are replaced by
  G-3 (b).
- **G-3. The cut identity, refusing** (its own script under `identity/`, the purpose `identity`, its own decision row,
  before stage 0 and the reading; one script may serve all four deltas). (a) The parent's whole-window identities hold
  as the parent states them (G-7). (b) For P-14 and P-16, the stream built on the cut equals the whole-window stream's
  day blocks up to 2023-12-29, block for block, every field, the per-R outcomes included. (c) The vendored estimator of
  the verdict arm's constants (G-4), applied to the whole-window stream, reproduces the registered constants exactly.
  (d) The vendored computation of each base's gate-file `edge`, `rung` and `resolution` rows, applied to the
  whole-window stream, reproduces the registered gate files' rows (G-16). The script reads the whole window under the
  purpose `identity`, writes pass or fail lines and nothing of any cell, and is not this reading. A failure of (b) stops
  the reading; of (c) alone, the verdict arm (G-4); of (d) alone, stage 0's `bound` edge set (G-16).
- **G-4. The verdict arm's constants, re-estimated on the search years.** The parent's "estimated on the whole
  development window ... a function of 2024-2026 through that one constant" (its section 3): here `e`, `lb`, `e_by_rr`
  and `lb_by_rr` are the vendored estimator's (the one the registered builder calls, at the registered trial count) on
  the search-year trades and days; under G-2 the builder's own call computes them on the cut. **Reason:** inherited, the
  constant would carry a held-out read into every verdict row and into stage 0's bound edges, and so into the lever
  space (CHARTER 3.3 (a)); re-estimated, both are functions of the search years alone, at the cost of one identity
  (G-3 (c)). The `point` arm is unchanged. If G-3 (c) fails, the verdict arm is not run: `point` is the headline, every
  row labelled so.
- **G-5. The starts and the horizon embargo** (CHARTER 3.6 (d)). The starts are every start day U1 reads for `p14` and
  `p16` inside the search years. Each measure is read at its horizon h (the parent's section 5 table, unchanged) only on
  starts with h sessions inside the search years: on the cut replay a start observes no session after 2023-12-29, so
  `u_select.block(records, None, h)` gives exactly these. U1's long replay of up to 252 sessions and its exact-length
  runs stop at the cut. Wherever the parent says "every start" or "all starts" of what is replayed or read, read the
  search-year starts with the horizon left. By start year: 2020 to 2023, means only, not purged within the search years,
  2023's starts reading only 2023's sessions; labelled so.
- **G-6. The blocks: the late block replaced by the search years' second half.** On the cut replay the parent's early
  block equals the headline and its late block is empty, so both are replaced, per measure at its h:
  - **all**: every search-year start with h sessions inside the search years (the headline);
  - **first**: the starts of 2020 and 2021, each read at h only if h sessions remain before the first session of 2022
    (D-621 (4)(b)'s purge, moved to the half's end);
  - **second**: the starts of 2022 and 2023, read at h only with h sessions inside the search years.

  **Reason:** the flag "not stable across blocks" needs two disjoint stretches read apart; two calendar halves of equal
  length, fixed by the calendar before any read and cut at a year's end as the parent's blocks were, keep it without
  reading a held-out day. The vendored `u_select.block` fixes its years, so the halves are a function of this
  repository (B-3). Nothing is chosen on any block. **Considered and not taken:** no blocks (it loses the flag); halves
  by start count (a cut that moves with the data).
- **G-7. The identities.** The parent's `cl_identity` and `cl_fit_identity` (9.1, 6.4) run as the parent states them,
  on the whole window or on registered files, from `identity/*.py` under the purpose `identity` and their own rows, and
  the shared identities it waits for (Q-05, Q-80, Q-93 with Q-100, Q-101) are unchanged: they compare Stage 2's engine
  and solver with Stage 2's registered files and write no outcome of any cell, so they are not this reading's reads.
  Inside the reading's own run (9.1 items 4 and 6), every comparison with a registered whole-window file (U1's start
  rows; Q-44's per-start rows) is made **only on the starts whose 252-session replay ends inside the search years**,
  every column the parent names, refusing; no row of a later start is loaded. Where the parent reads a base's rows from
  Q-44's file (the `naf` cells under the Focused Trader models, 10.1 item 8), it reads them on the same starts only.
  G-3 holds before stage 0 and the run.
- **G-8. The gate on the search years.** Every gate beside draws its resampled days from the search-year day blocks
  only. Each new cell's gate is paired with its base's own search-year gate at the same seed and the same number of
  paths (the same pool of days, so the same day draws), not with the registered gate paths, which draw from the whole
  window. The two references' search-year gates are run and read beside as the pairs' references; the registered gate
  paths stay G-7's identities.
- **G-9. The outputs.** New files, never the parent's: `results/cls_fit.csv`, `results/cls_reading.csv`,
  `results/cls_gate.csv`, `results/cls_menu.csv`, each through `extended.results.write_result` with its sidecar
  manifest, `prereg_id` this file's id at the pin, the window 2020-01-02 to 2023-12-29, the rows under which G-3 and the
  parent's identities held, and every manifest field the parent's section 15 lists.
- **G-10. No judged-block purpose.** This declaration reads no day of the held-out years, so it names no purpose of the
  reader's judged-block form and carries no line of that form; the reader refuses any judged read citing it. The
  parent's line is the parent's and is never taken (0.3).
- **G-11. The held-out read ledger, inherited and labelled** (CHARTER 3.6 (b); no figure cited). This reading rests on
  designs and records that read the held-out years before it: P-14 fixed as R* from the whole window (Stage 2 D-626);
  P-14's rung map and P-16's mark cutoff resolved on the whole window (E-203 S-2); P-16's stop chosen on each block
  (Stage 2 D-554); the registered state table (`state_dp_e-0.050_lamstar_noclose`) and protocols as Stage 2 registered
  them; Stage 2 U4's size fit at the registered bounds (D-666, D-667), which 6.4's identity reproduces; program U's
  families 1, 3 and 5 on both blocks and its nine families' late-block reads of P; U1's whole-window start rows (Stage 2
  D-620) and Q-44's per-start rows, which G-7's comparisons cite on search-year starts only; Stage 2's signal search
  over the whole window; and the parent's own pinned text, declared over the whole window and never run. Nothing here
  re-estimates them but G-4's and G-16's constants; every result file of this reading names them.
- **G-12. Prior exposure, re-read.** The parent's prior-exposure rows stand as records. Where a row's bearing reads "the
  late block has been read for P nine times: late development, not out of sample", read: those reads were of the
  held-out years; they are G-11's entries; this reading reads none of those years.
- **G-13. The binding.** The parent's "the blocks read here are recorded as read for contract-use levers on P-14 and
  P-16" reads: the search years, and their two halves, are recorded as read for contract-use levers on P-14 and P-16;
  the held-out years are not read by this reading and are recorded as unread by it.
- **G-14. In sample.** Every statement made from this reading, and the operator's choice from its menu, is a
  description of the search years, in sample, with no confirmation (E-023 (1)); the held-out years stay unread by it.
- **G-15. Reruns.** The reader ledgers no choice-block read, so its once-per-purpose refusal does not reach this
  reading. The parent's rule is kept by the lead: only the first complete clean run of each step is read; a restart or
  a rerun is recorded by the lead with its log under a decision row naming this file, which says which run replaces
  which and why; a result file is never overwritten (G-9).
- **G-16. Stage 0 on the search years.** The parent's stage 0 takes its `bound` edge set from "the gate's `lb_by_rr`"
  and each base's rungs from "its gate's `rung` and `resolution` rows" -- whole-window statistics in registered files.
  Here the `bound` edge set is G-4's search-year `lb_by_rr`, and each base's rungs (stops, shares and per-R
  availability) are computed by the same vendored computation on the search-year stream; the `zero` edge set, the
  registered policy, the state-policy configuration and the table files are unchanged (design constants, no data).
  Stage 0 therefore builds the streams on the cut (G-2) in its own process, reading bars on the search years only,
  and runs no replay. 6.4's identity is unchanged (it holds the solver machinery to registered files at the registered
  edges, an identity, no outcome), and G-3 (d) holds the rung computation. **Reason:** the solver's view is printed
  beside the replay's rows; on whole-window edges it would be a function of the held-out years beside rows that are
  not. If G-3 (d) fails or the computation cannot be composed without editing the vendored code, stage 0's `bound` edge
  set is not run and its `zero` edge set alone is printed, labelled; stage 0 decides nothing either way (E-146).

## 3. Every dependency in the parent, line by line

The parent's lines as numbered in its LF text at the pinned sha256. A row's lines are one line, a range whose joined
text holds the quote, or a list of lines each holding the quote. The replacement is this declaration's.

| # | parent lines | where | quote | replacement |
|---|---|---|---|---|
| D-01 | L48 | header table, development data | "NQ 1-minute bars, 2020-01-02 to 2026-07-16" | NQ 1-minute bars, 2020-01-02 to 2023-12-29, cut at the read (G-1, G-2) |
| D-02 | L50 | header table, blocks | "the late block from 2024-01-02 (section 5)" | all search-year starts the headline; the first and second halves beside, each purged per measure (G-6) |
| D-03 | L53 | header table, the parent's purposes | "four purposes, on the line of section 5 item 6" | none (G-10); the identities from `identity/*.py` under their own row, unchanged (G-7); stage 0 reads the cut stream (G-16) |
| D-04 | L139 | 1, why described | "The judged block's few independent three-month stretches" | the same reason holds a fortiori on the search years: fewer independent stretches still (section 1) |
| D-05 | L144 | 1, the operator's choice | "a described development reading" | a described reading of the search years (G-14) |
| D-06 | L146 | 1, the operator's choice | "a description of the development window, in sample" | a description of the search years, in sample (G-14) |
| D-07 | L325, L326 | 3, program U families 1, 3 and 5 | "both blocks" | a record; held-out reads by Stage 2, entered in G-11 |
| D-08 | L334 | 3, Q-44 | "the bases' replays under the ladder, the placement and the ten Focused Trader models" | a record; Q-44's rows are whole-window, and G-7 compares them on search-year starts only |
| D-09 | L335 | 3, RD-01 and RD-02 | "other firms' contracts; payout policy" | a record; both parents are re-declared on the search years (`prereg/DRAFT_RD-01S_firm_contracts_search_years.md`, `prereg/DRAFT_RD-02S_payout_policy_search_years.md`); this reading reads none of their cells |
| D-10 | L336 | 3, U1 and Q-05 | "P-14's and P-16's own journeys, every start" | a record; the references' rows are whole-window, and G-7 compares them on search-year starts only |
| D-11 | L337 | 3, program U's nine families | "late development, not out of sample" | those reads were of the held-out years; G-11's entries; none read here (G-12) |
| D-12 | L339-L342 | 3, the verdict arm's bound | "so an early-block reading on the verdict arm is a function of 2024-2026 through that one constant" | the verdict arm's constants re-estimated on the search years (G-4); no reading is a function of the held-out years |
| D-13 | L342 | 3, the verdict arm's bound | "Stage 0's bound edges are the same constants." | stage 0's bound edges are G-4's search-year constants (G-16) |
| D-14 | L485 | 4.4, G-8 | "rule changes over 2020-2026" | rule changes over 2020-2023 (G-1); today's terms on every search-year start |
| D-15 | L524 | 5, its title | "Data, blocks, the unit and the horizons" | section 5 as items 1 to 6 are replaced in D-16 to D-23 |
| D-16 | L526 | 5 item 1 | "one development start day" | one search-year start day (G-5) |
| D-17 | L527 | 5 item 1 | "replayed in historical order, a long replay of up to 252 sessions" | replayed in historical order, a long replay of up to 252 sessions and U1's exact-length runs, stopping at the cut (G-5) |
| D-18 | L530-L531 | 5 item 1, the starts | "every start U1 reads for `p14` and `p16`" | every start U1 reads for `p14` and `p16` inside the search years, each reading on the starts with its h inside them (G-5) |
| D-19 | L533 | 5 item 3 | "the same start days, blocks and seeds" | the same search-year start days, G-6's blocks and the parent's seeds |
| D-20 | L535-L540 | 5 item 4 | "**the late block** (`u_select.block(records, "late", h)`: from 2024-01-02, h left)" | item 4 is G-6: all, first and second, each at its measure's h; by start year 2020 to 2023 (G-5); the flag on first and second |
| D-21 | L536-L538 | 5 item 4, the early block | "no early reading touches a 2024 session except through the verdict arm's bound" | no reading touches a session after 2023-12-29, and none through the bound (G-2, G-4); no first-half reading touches a second-half session (G-6) |
| D-22 | L555 | 5 item 5 | "No NQ from 2026-07-17" | no NQ after 2023-12-29 is read by this reading (G-1); NQ from 2026-07-17 is not on disk and never read |
| D-23 | L556-L560 | 5 item 6, the seal and the parent's purposes | "`levers_scorecard`, `levers_gate_beside`, `levers_ladder_beside`, `levers_ftp_beside`" | none (G-10): every step authorises 2020-01-02 to 2023-12-29 only (G-2); this file carries no line of the reader's judged-block form |
| D-24 | L569-L571 | 5 item 6, stage 0 | "**Stage 0 reads no bar and no atlas**" | stage 0 builds the streams on the cut and reads the search years' bars and atlas only, through the engine, with no purpose (G-2, G-16); this file is the new declaration the parent's sentence calls for |
| D-25 | L588-L589 | 6.1, the edge sets | "the gate's `lb_by_rr`" | G-4's search-year `lb_by_rr` (G-16) |
| D-26 | L595 | 6.1 (a), the rungs | "from its gate's `rung` and `resolution` rows" | from the same rows computed on the search-year stream (G-16) |
| D-27 | L614-L616 | 6.1, the inputs | "registered gate files' `edge`, `rung` and `resolution` rows" | those rows computed on the search-year stream (G-16); the other registered inputs unchanged |
| D-28 | L730 | 7.2 | "Each cell runs both arms, every start" | each cell runs both arms, every search-year start, the long replay and the exact-length runs stopping at the cut (G-5) |
| D-29 | L775 | 8, horizons and blocks | "all, early, late" | all, first, second (G-6) |
| D-30 | L787 | 9.1, its title | "whole-window identities only from `identity/*.py`" | unchanged: the whole-window identities stay under `identity/` (G-7); G-3 added |
| D-31 | L802 | 9.1, this reading's own | "`Judged-block reads:` line" | under the purpose `identity` and their own row; this file has no such line (G-10) |
| D-32 | L811 | 9.1 item 2 | "both arms, every start, every" | unchanged as `identity/cl_identity.py`'s identity (G-7) |
| D-33 | L833 | 9.1 item 4 | "`ref`'s start rows equal U1's again" | on the starts whose 252-session replay ends inside the search years (G-7) |
| D-34 | L837-L838 | 9.1 item 6 | "equals Q-44's `results/user_beside_starts.csv`" | on the starts whose 252-session replay ends inside the search years (G-7) |
| D-35 | L849-L850 | 9.1, the order | "a further judged read under `repeat=` (15)" | a rerun recorded by the lead under a row naming this file (G-15) |
| D-36 | L872 | 9.3 | "For each new cell and block" | for each new cell and each of G-6's blocks |
| D-37 | L255, L841, L843, L864, L900, L1004, L1189 | 2.3; 9.1 item 7; 9.2; 9.3; 10.2; 15 | "every start" | every search-year start (G-5) |
| D-38 | L907 | 10.1 | "every block of section 5" | every block of G-6 |
| D-39 | L951-L952 | 10.1 item 8, `naf` | "its reading the base's from Q-44's per-start rows" | Q-44's per-start rows on the starts whose 252-session replay ends inside the search years (G-7) |
| D-40 | L959 | 10.1 item 9 | "paired with the base's registered gate paths" | paired with the base's search-year gate at the same seed and paths (G-8); the two references' gates run as the pairs' references |
| D-41 | L965 | 10.1 item 10 | "at each base's bound edge" | at each base's search-year bound edge (G-16) |
| D-42 | L970-L971 | 10.1 item 12, the menu | "the early and late blocks and the start years beside" | the first and second halves and the start years 2020 to 2023 beside (G-5, G-6) |
| D-43 | L972-L973 | 10.1 item 12, the flags | "of opposite signs on the early and late blocks" | of opposite signs on the first and second halves (G-6) |
| D-44 | L1033 | 11, the operator's choice | "over the development window" | over the search years, the held-out years unread by it (G-14) |
| D-45 | L1036-L1037 | 11, the binding | "The blocks read here are recorded as read for contract-use levers" | G-13 |
| D-46 | L1044 | 12, the build's toys seed | "T-3's synthetic late block" | T-3S's synthetic sessions after the cut (D-50), drawn from the same seed (section 8) |
| D-47 | L1089-L1092 | 13 item 4, the gates | "the references' gates are 9.1's identities" | the two references' search-year gates are run beside as the pairs' references (G-8); the registered paths stay 9.1's identities |
| D-48 | L1094 | 13 item 6 | "**Every block read** is recorded as read for contract-use levers" | the search years and their halves recorded as read for contract-use levers (G-13) |
| D-49 | L1129 | 14.3, T-0 | "one `Judged-block reads:` line" | T-0 is `tests/test_rd_search_years_drafts.py` (with this text), extended at the pin: no line of the reader's judged-block form; the parent's pin; every searched line accounted for (section 7) |
| D-50 | L1132 | 14.3, T-3 | "every early-block reading at horizon h is byte-identical when every session from 2024-01-02 on is replaced" | T-3S: every reading at h is byte-identical when every session after 2023-12-29 is replaced, the runner refuses a stream holding one, and every first-half reading at h is byte-identical when every second-half session is replaced; the verdict arm at its search-year constant (G-4) |
| D-51 | L1147-L1153 | 15, files | "`results/cl_fit.csv`" | `results/cls_fit.csv`, `results/cls_reading.csv`, `results/cls_gate.csv`, `results/cls_menu.csv` (G-9) |
| D-52 | L1156 | 15, manifests | "`prereg_id` `RD-03`" | `prereg_id` this file's id at the pin (G-9) |
| D-53 | L1170 | 15 step 2 | "**stage 0** (`scripts/cl_fit.py`, one worker): its identity first (6.4)" | stage 0 after G-3 and 6.4's identity, on the cut stream (G-16) |
| D-54 | L1172-L1181 | 15 steps 3 to 5 | "purposes `levers_scorecard` then `levers_gate_beside`" | steps 3 to 5 authorise 2020-01-02 to 2023-12-29 with no purpose (G-2, G-10), in the parent's order |
| D-55 | L1193-L1196 | 15, a restart or a rerun | "a further judged read" | G-15 |
| D-56 | L43 | header table, id | "every result's `prereg_id` is `RD-03` (section 15)" | this file's id at the pin (0.2); every result's `prereg_id` is it (G-9) |
| D-57 | L510-L511 | 4.5, `naf` under the Focused Trader models | "its reading is the base's (Q-44's per-start rows" | Q-44's per-start rows on the starts whose 252-session replay ends inside the search years (G-7) |

## 4. Unaffected, because

Every other line the search of section 7 finds in the parent, with the reason it needs no change.

- **L7, L10**: the parent's text history and the record's commit and date; records.
- **L56**: NQ's confirmation tests and the reserve from 2026-07-17, which this reading never reads; unchanged.
- **L63**: "a matched pair with its base on every start day": the pairing holds on every start read; G-5 sets the
  starts.
- **L116, L324, L399, L521, L876, L924, L935, L961, L962**: a user's first year, a year's purchases or payouts, a
  credit's expiry, or the gate's two-year growth on resampled days that carry no date (G-8); unchanged.
- **L154, L157, L184, L185, L210, L228, L389, L403, L428, L430, L431, L765, L844, L862, L865, L892, L1131, L1133,
  L1134, L1272, L1304, L1328**: a firm's clock in calendar days or its translation to sessions, or an account's history
  reset by a rule; a rule's term, unchanged.
- **L360, L1326**: "bought early", another sense of the word (the disclosed direction; the inventory's cap's reason).
- **L371, L383, L384, L385, L386, L387, L388, L390, L391, L392, L393, L394, L395, L396, L397, L398, L400, L401, L402,
  L404, L405, L406, L407, L408, L409, L410, L411, L412, L413, L414, L415, L416, L417, L624**: section 4's record, each
  key's date read, or a search's date; terms of the record, not read windows.
- **L542**: the horizon table's sources; each measure's h is unchanged.
- **L835**: "the start's blocks", a start's day blocks.
- **L880, L881, L883, L1161**: the pinned calendars and their hashes; the files are fixed as declared, and G-1 uses
  their days only inside the search years.
- **L995, L996, L1008**: 10.2's window rule and honesty settings, stated per block; they apply unchanged to G-6's
  blocks.
- **L1035**: no confirmation; NQ from 2026-07-17 is never read; unchanged.
- **L1056, L1065**: section 12's seed check, its date and "block" meaning the seed block; the seeds are inherited
  unchanged (section 8).
- **L1311**: Appendix C's note that the red team judged the drafter's list; a record.

## 5. What does not change

The levers L-B, L-I, L-H and L-N and what is not here (section 2); the user held fixed (2.6); the rules, their unstated
terms and readings, the gaps and conduct (4); stage 0's rules, readings, checks and identity (6.1 to 6.5) but its
`bound` edges and rungs (G-16); the references, the grid and each lever's own comparisons (7); the parameters' classes
(8); the oracles (9.2); the mechanics (9.3) on G-6's blocks; the scorecard, the guard row, the journey variables, the
paired readings, D-34's caveat, the readings beside, stage 0's view beside, the evenness trade-off and the menu's flags
(10.1) on the search years; the uncertainty method (10.2, RD-02's 9.2), its window counts and honesty settings the
search years'; what the reading delivers and what each outcome means (11) on the search years; the seeds (section 12),
inherited unchanged and by reference (section 8); the counting (13): stage 0's policy evaluations and solves, 32
replays, 360 replays beside with 28 reference checks and 30 gates, with the two references' search-year gates added
beside (G-8); the adapters, their rules in code and the tests T-1, T-2 and T-4 to T-15 (14), T-0 and T-3 replaced
(D-49, D-50); the run's five steps and waits (15), G-3 added to step 1; the open items (16) and Appendices R and C.

## 6. The build list (for a later item; nothing here is built by this one)

- **B-1. The declaration.** `extended/cl_reading.py`'s and `extended/levers_terms.py`'s `DECLARATION` name this file at
  its pinned name and `PURPOSES` is empty; `scripts/cl_reading.py`'s `authorise` and its pre-check call
  `reader.CHOICE_START` to `reader.CHOICE_END` with no purpose; the runners refuse to run if any argument or constant
  names the parent's path or purposes.
- **B-2. The cut** (G-2): the shared module of RD-06's B-2 (for example `extended/search_years.py`), used by stage 0's
  driver and by `scripts/cl_reading.py`; the refusal of any day block or date after `reader.CHOICE_END` before any
  replay or gate.
- **B-3. The blocks** (G-6): `extended/cl_reading.py`'s `BLOCKS` (now `PR.BLOCKS`) follow RD-07's B-3 (`all`, `first`,
  `second`) through the shared repository block function; `u_select.block` is not edited and is called only for `all`.
- **B-4. The verdict constants** (G-4): recorded from the builder's call on the cut; the manifest carries them.
- **B-5. Stage 0** (G-16): `scripts/cl_fit.py`'s driver (A-5) takes the `bound` edges from B-4's constants and each
  base's rungs from the vendored rung computation on the cut stream; the `zero` set and the registered files unchanged;
  its stop-and-report clause kept.
- **B-6. The identities:** `identity/cl_identity.py`, `identity/cl_fit_identity.py` and the shared identities unchanged
  (G-7); the shared G-3 script with its item (d); inside the run, 9.1 items 4 and 6 and 10.1 item 8's Q-44 rows
  restricted to the starts whose 252-session replay ends inside the search years.
- **B-7. The gate** (G-8): each new cell's gate paired with its base's search-year gate, the two references' gates run
  first.
- **B-8. The outputs** (G-9): `results/cls_*.csv` with this file's id, the window, G-3's row and G-11's list.
- **B-9. Tests:** T-0 (`tests/test_rd_search_years_drafts.py`, extended at the pin); T-3S (D-50) on synthetic
  campaigns under the parent's build-toys seed; a stage-0 test that the `bound` edges and rungs are the cut stream's.

## 7. The search that found section 3 (re-runnable)

Every line of the parent's LF text that matches any of these patterns (Python regular expressions, case-insensitive),
one per line between the markers, is cited in section 3 or listed in section 4 -- `tests/test_rd_search_years_drafts.py`
checks it, and checks that the patterns below are the test's own:

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
```
<!-- end search-terms -->

To re-run: `python -m pytest -q -o addopts= tests/test_rd_search_years_drafts.py` (its `parent_hits` lists the lines).

## 8. Counting, seeds and confirmation

- **Counting.** No program family number and no level (E-023 (1)); the next numbered family's k is unchanged. The
  parent's counts hold (section 5), with the two references' search-year gates added beside (G-8). The parent is never
  run (0.3), so nothing is counted twice.
- **Seeds.** The parent's section 12, inherited unchanged and by reference (its block, statuses, the honesty series'
  keys and the inherited seeds); no seed is restated here, so the parent's T-0 still finds its block in no other
  declaration. The parent was never run, so none of its seeds has been drawn on the bars.
- **Confirmation.** None: nothing is carried; NQ from 2026-07-17 is never read.

## 9. Open before the pin

1. **The red team's read** of this draft and its three siblings.
2. **The id and the name** (0.2): the lead's.
3. **G-2's and G-16's feasibility** are build questions; their stop-and-report clauses are declared now.
4. **The pinning row** records the parent as superseded, never run (0.3).
