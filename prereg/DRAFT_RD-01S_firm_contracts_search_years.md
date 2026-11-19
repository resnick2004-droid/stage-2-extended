# DRAFT RD-01S: other firms' contracts on the registered trades, on the search years only (reading FC-S) -- a delta declaration of RD-01, a described reading, unnumbered (E-023 (1))

**Status: a draft, not pinned (O-7, the lead's ruling in E-221).** Drafted on wt/wt-firms, 2026-11-18. It re-declares
`prereg/RD-01_firm_contracts.md` on the search years alone, so that no part of the reading touches NQ's held-out years
(E-208), which E-221 (O-1) keeps for one joint fixed-sequence confirmation across firms. The parent is not edited
(CLAUDE.md; `tests/test_declarations_fixed.py`): it stays on record, pinned, and is never run (section 0.3). The red
team reads this draft before it is pinned; the lead assigns its id at the pin (section 0.2).

| field | value |
|---|---|
| id | proposed **`RD-06`** at the pin (section 0.2); until then `RD-01S` |
| parent | `prereg/RD-01_firm_contracts.md` sha256 `f6df144da5ea706e88c3e8f84549b4492f78802fe84cdf506d7754c3cf5c9bcb` (of its LF text), pinned by E-080 |
| reading | FC-S: the parent's reading FC, every cell, run and reading as the parent declares them, on the search years |
| kind | a **described reading** (E-023 (1)): never carried; no program family number, no level, no pass line, no pick |
| development data | NQ 1-minute bars, 2020-01-02 to 2023-12-29 (the search years, E-208), read only inside Stage 2's engine by P-16's and P-14's registered builders, cut at the read (G-2) |
| held-out years | 2024-01-02 to 2026-07-16: never read by this reading, under any purpose (G-1, G-10) |
| blocks | all search-year starts (the headline); the search years' first half and second half beside (G-6) |
| judged-block purposes | none (G-10) |
| confirmation | none; NQ from 2026-07-17 never read |
| the build | not built by this item: section 6 is the build list for a later item |

## 0. What this file is, and how it reads its parent

### 0.1 The incorporation

This declaration **is the parent's text, with the replacements below**. Every section, table, rule, cell, count,
seed, oracle, test and wait of `prereg/RD-01_firm_contracts.md` at the sha256 above is part of this declaration, read
with:

1. the general replacements G-1 to G-15 (section 2), which apply wherever the parent's words reach them;
2. the line-by-line replacements of section 3, each citing the parent's line and a short quote from it.

Where a replacement and the parent's words differ, the replacement is the declaration. Where section 3 is silent on a
parent line, section 2 governs it; where both are silent, the parent's words stand (section 5 lists what stands, and
section 4 lists every line the search of section 7 found that needs no change, with the reason). Section numbers,
item numbers, cell names, run names and test names are the parent's.

### 0.2 The id scheme (proposed; the lead assigns at the pin)

Each search-years delta takes the next free described-reading number, in the order of its parent: **RD-06** for this
file (RD-01's), **RD-07** for RD-02's, **RD-08** for RD-03's, **RD-09** for RD-05's part F. The pinned name is
`prereg/RD-06_firm_contracts_search_years.md`. The reason for new numbers rather than a suffix such as `RD-01S`: the
reader reads a declaration's id as `RD-` followed by digits (`extended/reader.py`'s `F_ID` and `DECLARATION_ID`), so
`prereg/RD-01S_...` would be read as RD-01 wherever the id is taken from the path -- a `repeat=` row naming the parent
would then authorise a rerun of this file. The pinned name ends in `_search_years.md`, so it matches no other reading's
T-0 glob (`RD-*_firm_contracts.md` among them).

### 0.3 The parent, superseded before any run

No result of the parent exists: the read ledger holds no line of RD-01 and no file `results/fc_*.csv` exists at this
draft. At this file's pin the parent is **superseded, never run**: no run takes its three purposes, its result files
are never written, and its id is never a manifest's `prereg_id`. The reader cannot yet see a withdrawal (the audit's
R-8 registry is not built), and its held-out rule 4 refuses the parent's judged reads only until a market's verdict row
exists; so the supersession is enforced by the build (section 6, item B-1: the runner names this file, never the
parent) and recorded in the pinning row.

## 1. Why, and what it does to what the reading can show (E-051)

**Why.** Under E-208 every choice and every map the journey search draws on is made on the search years, and the
held-out years are read once, by the joint confirmation (E-221, O-1). The parent reads the whole development window, its
late block by name, and its judged-block purposes; any lever range drawn from its menu would carry a
held-out read into the search (CHARTER 3.3 (a), 3.6 (a)). O-7 rules that the reading is re-declared on the search years.

**What it does to what the reading can show.** The menu describes the search years only. The starts read at each
horizon are fewer (G-5): at month 12 the starts are those with 252 sessions inside the search years, so the headline
holds fewer kept windows and more readings print "too few independent windows"; each half (G-6) holds about two years,
so most month-6 and month-12 half readings print the sign count alone. The stability flag compares two halves of four
years instead of the search years against the held-out years. The verdict arm's shift is the search years' own (G-4),
so verdict rows are not comparable with any whole-window row. Nothing else of the reading changes: the plans, the
cells, the corners, the counts, the uncertainty method and the oracles are the parent's.

## 2. The general replacements

- **G-1. The window.** The development data are NQ 1-minute bars from 2020-01-02 to 2023-12-29, the search years
  (E-208). The held-out years 2024-01-02 to 2026-07-16 are never read by this reading, under any purpose, by any of its
  runs, gates, identities in its own run, or beside readings; NQ from 2026-07-17 is never read. Wherever the parent says
  "the development window", "2020 to 2026", "2020-2026" or "the whole window" of what this reading reads, read the
  search years. A pinned calendar (E-029, E-050) or a release file of section 5.5 is used only on days inside the search
  years.
- **G-2. The cut at the read.** The reading's process authorises the engine's reads with
  `extended.reader.authorise_engine_read` on 2020-01-02 to 2023-12-29 -- the choice block, which needs no purpose and is
  not ledgered -- and no bar or atlas row dated after 2023-12-29 reaches any function of the registered builders, the
  replay, the gate or the reading: the vendored readers the builders call are wrapped for the call so that every row
  after 2023-12-29 is dropped at the read, and restored after it (the pattern of `extended/firm_reading.py`'s
  `build_with_deltas`; nothing vendored is edited). The day blocks and dates handed to the replay and to the gate end at
  the search years' last session, and the runner refuses, before any replay, a block or a date after 2023-12-29. **If a
  registered builder cannot be cut at its reads, the build stops and reports; this declaration does not fall back** to a
  whole-window build cut afterwards (a new declaration would be needed). The builders' own whole-window checks -- the
  registered trades' content hash, the registered edge rows -- cannot hold on the cut and are replaced by G-3 (b).
- **G-3. The cut identity, refusing** (its own script under `identity/`, the purpose `identity`, its own decision row;
  run before the reading, as the parent's identities are). (a) The parent's whole-window identities hold as the parent
  states them (G-7). (b) For P-16 and P-14, the stream built on the cut (G-2) equals the whole-window stream's day blocks
  up to 2023-12-29, block for block, every field of every day block, the per-R outcomes included: the registered
  builders are causal at the cut, so the search-year stream is the registered design's. (c) The vendored estimator the
  builder calls for the verdict arm's constants (G-4), applied to the whole-window stream, reproduces the registered
  constants exactly. The script reads the whole window under the purpose `identity` (an identity of Stage 2's engine
  against Stage 2's files, E-004's kind), writes its comparisons' pass or fail lines and nothing of any cell, and is not
  this reading. A failure of (b) stops the reading; a failure of (c) alone stops the verdict arm (G-4).
- **G-4. The verdict arm's constants, re-estimated on the search years.** The parent's verdict arm shifts every R to the
  registered bound "estimated on the whole development window", so every verdict row is a function of the held-out
  years through one constant per R. Here `e`, `lb`, `e_by_rr` and `lb_by_rr` are the vendored estimator's (the one the
  registered builder calls, at the registered trial count) on the search-year trades and days; under G-2 the builder's
  own call computes them on the cut. **Reason:** inherited, the constants would carry a held-out read into every
  verdict row and so into any lever range read from it (CHARTER 3.3 (a)); re-estimated, the arm is a function of the
  search years alone, at the cost of one identity (G-3 (c)). The `point` arm (as traded) carries no constant and is
  unchanged. If G-3 (c) fails, the verdict arm is not run: the `point` arm is the headline, every row labelled so.
- **G-5. The starts and the horizon embargo** (CHARTER 3.6 (d)). The starts are every start day U1 reads inside the
  search years. A start is read at horizon h only if h sessions remain inside the search years: on the cut replay a
  start observes no session after 2023-12-29, so `u_select.block(records, None, h)` gives exactly these. U1's long
  replay of up to 252 sessions and its exact-length runs stop at the cut. Wherever the parent says "every start",
  "all starts" or "every start day" of what is replayed or read, read the search-year starts with the horizon left.
  By start year: 2020 to 2023 only, means only, not purged within the search years, labelled so.
- **G-6. The blocks: the late block replaced by the search years' second half.** On the cut replay the parent's early
  block (the starts of 2023 and before, purged) equals the headline and its late block is empty, so both are replaced:
  - **all**: every search-year start with h sessions inside the search years (the headline);
  - **first**: the starts of 2020 and 2021, each read at h only if h sessions remain before the first session of 2022
    (D-621 (4)(b)'s purge, moved to the half's end, so no first-half reading touches a second-half session);
  - **second**: the starts of 2022 and 2023, read at h only with h sessions inside the search years.

  **Reason:** the menu's stability flag ("not stable across blocks") needs two disjoint stretches read apart; two
  calendar halves of equal length, fixed by the calendar before any read and cut at a year's end as the parent's blocks
  were, keep it without reading a held-out day. The vendored `u_select.block` fixes its years, so the halves are a
  function of this repository (section 6, B-3). Nothing is chosen on any block. **Considered and not taken:** no blocks
  at all (it loses the flag); halves by start count rather than by calendar year (a cut that moves with the data).
- **G-7. The identities.** The parent's identities (9.1) run as the parent states them, on the whole window, from
  `identity/*.py` under the purpose `identity` and their own rows: they compare Stage 2's engine with Stage 2's
  registered files and write no outcome of any cell, so they are not this reading's reads. Inside the reading's own run,
  every comparison the parent makes with a registered whole-window file (U1's start rows; Q-44's per-start rows) is made
  **only on the starts whose 252-session replay ends inside the search years**, every column as E-010 compared them,
  refusing; no row of a later start is loaded. G-3 holds before the run.
- **G-8. The gate on the search years.** Every gate beside draws its resampled days from the search-year day blocks
  only. Its pairs are formed with the reference's own search-year gate at the same seed and the same number of paths
  (the same pool of days, so the same day draws), not with the registered gate paths, which draw from the whole window.
  The two references' search-year gates are therefore run and read beside as the pairs' references; they are not
  identities (the registered gate paths stay G-7's identities).
- **G-9. The outputs.** The result files are new files, never the parent's: `results/fcs_reading.csv`,
  `results/fcs_gate.csv` and `results/fcs_menu.csv`, each through `extended.results.write_result` with its sidecar
  manifest, `prereg_id` this file's id at the pin, the window 2020-01-02 to 2023-12-29, the rows under which G-3 and the
  parent's identities held, and every manifest field the parent's section 15 lists. A file of the parent's name is
  never written by this reading.
- **G-10. No judged-block purpose.** This declaration reads no day of the held-out years, so it names no purpose of the
  reader's judged-block form: it carries no line of that form at all, and the reader refuses any judged read citing it
  (the purpose must be on the declaration's own line). The parent's line is the parent's and is never taken (0.3).
- **G-11. The held-out read ledger, inherited and labelled** (CHARTER 3.6 (b); no figure cited). This reading rests on
  designs and records that read the held-out years before it: P-14 fixed as R* from the whole window (Stage 2 D-626);
  P-14's rung map and P-16's mark cutoff resolved on the whole window (E-203 S-2); P-16's stop chosen on each block
  (Stage 2 D-554); the registered state tables and protocols as Stage 2 registered them; program U's nine families,
  which read P on the late block, and its family 5 (Lucid seats beside Topstep's, both blocks); U1's whole-window
  start rows (Stage 2 D-620) and Q-44's per-start rows, which G-7's comparisons cite on search-year starts only; Stage
  2's signal search over the whole window; and the parent's own pinned text, declared over the whole window and never
  run. These are the registered designs' and Stage 2's; nothing here re-estimates them, and every result file of this
  reading names them.
- **G-12. Prior exposure, re-read.** The parent's prior-exposure rows stand as records. Where a row's bearing reads "the
  late block is late development, not out of sample", read: those reads were of the held-out years; they are G-11's
  entries; this reading reads none of those years.
- **G-13. The binding.** The parent's "the blocks read here are recorded as read for firm contracts on P-14 and P-16"
  reads: the search years, and their two halves, are recorded as read for firm contracts on P-14 and P-16; the
  held-out years are not read by this reading and are recorded as unread by it.
- **G-14. In sample.** Every statement made from this reading, and the operator's choice from its menu, is a
  description of the search years, in sample, with no confirmation (E-023 (1)); the held-out years stay unread by it.
- **G-15. Reruns.** The reader ledgers no choice-block read, so its once-per-purpose refusal does not reach this
  reading. The parent's rule is kept by the lead instead: only the first complete clean run is read; a restart or a
  rerun (an adapter fix, the failure protocol's replication) is recorded by the lead with its log under a decision row
  naming this file, which says which run replaces which and why; a result file is never overwritten (G-9).

## 3. Every dependency in the parent, line by line

The parent's lines as numbered in its LF text at the pinned sha256. A row's lines are one line, a range whose joined
text holds the quote, or a list of lines each holding the quote. The replacement is this declaration's.

| # | parent lines | where | quote | replacement |
|---|---|---|---|---|
| D-01 | L78 | header table, development data | "NQ 1-minute bars, 2020-01-02 to 2026-07-16" | NQ 1-minute bars, 2020-01-02 to 2023-12-29, cut at the read (G-1, G-2) |
| D-02 | L80 | header table, blocks | "the early and late blocks per measure by `u_select.block`" | all search-year starts the headline; the first and second halves beside (G-6) |
| D-03 | L81 | header table, runs | "16 gates beside (section 7)" | the parent's 16 gates beside, and the two references' search-year gates as their pairs' references (G-8) |
| D-04 | L120-L121 | 1, why described | "three-month stretches of the late block" | the same reason holds a fortiori on the search years: fewer independent stretches still (section 1) |
| D-05 | L125 | 1, the operator's choice | "a described development reading" | a described reading of the search years (G-14) |
| D-06 | L127 | 1, the operator's choice | "a description of the development window" | a description of the search years (G-14) |
| D-07 | L151, L153 | 2.2 | "every start" | every search-year start (G-5) |
| D-08 | L153 | 2.2 | "every start day from 2020 to 2026" | every start day from 2020 to 2023 (G-1, G-5) |
| D-09 | L198 | 3, U1's row | "five Topstep seats and one Lucid seat, every start" | a record; U1's rows are whole-window, and 9.1 item 3 (a) compares them under G-7 (on the identity's own row) |
| D-10 | L199 | 3, program U family 5 | "both blocks" | a record; a held-out read by Stage 2, entered in G-11 |
| D-11 | L201 | 3, program U's nine families | "the late block is late development, not out of sample" | those reads were of the held-out years; G-11's entries; none read here (G-12) |
| D-12 | L217 | 3, what is known of the direction | "program U's family 5" | a record; its read spanned the held-out years (G-11) |
| D-13 | L397 | 4.7, G-11 | "rule changes over 2020-2026" | rule changes over 2020-2023 (G-1); today's terms on every search-year start |
| D-14 | L637-L638 | 5.5, the count | "by release and year" | by release and year, 2020 to 2023: the trades of the search-year stream only (G-1); the condition of 7.3's four news runs ("if P-16's count of 5.5 is not zero") is read on this count |
| D-15 | L701 | 6, its title | "Data, blocks and the unit" | section 6 as items 1, 2, 4, 5 and 6 are replaced in D-16 to D-21 |
| D-16 | L703 | 6 item 1 | "one development start day" | one search-year start day (G-5) |
| D-17 | L704 | 6 item 1 | "for up to 252 sessions plus" | for up to 252 sessions, stopping at the cut, plus U1's exact-length runs inside the search years (G-5) |
| D-18 | L706-L709 | 6 item 2 | "verdict arm is a function of 2024-2026 through that one constant" | the verdict arm's constants re-estimated on the search years (G-4); no reading is a function of the held-out years |
| D-19 | L710 | 6 item 3 | "the same start days, blocks and seeds" | the same search-year start days, G-6's blocks and the parent's seeds |
| D-20 | L712-L717 | 6 item 4 | "and on the late block (`u_select.block(records, "late", h)`" | item 4 is G-6: all, first and second, each at its measure's h; the stability flag on first and second |
| D-21 | L713-L714 | 6 item 4 | "on the early block" | replaced by G-6's first half; the parent's early block equals the headline on the cut replay |
| D-22 | L718 | 6 item 5 | "No NQ from 2026-07-17" | no NQ after 2023-12-29 is read by this reading (G-1); NQ from 2026-07-17 is not on disk and never read |
| D-23 | L719-L721 | 6 item 6 | "The judged block's seal" | the search years need no seal: the reading authorises 2020-01-02 to 2023-12-29 only (G-2) |
| D-24 | L723 | 6 item 6, the parent's purposes | "`firm_scorecard`, `firm_ladder_beside`, `firm_gate_beside`" | none (G-10); this file carries no line of the reader's judged-block form |
| D-25 | L727-L729 | 6 item 6 | "**Once per purpose:**" | G-15: the lead's first-complete-run rule; no purpose to ledger |
| D-26 | L769 | 7.3 | "Each runs both arms, every start" | each runs both arms, every search-year start, the long replay and the exact-length runs stopping at the cut (G-5) |
| D-27 | L775-L776 | 7.4, the gate | "TS's gates are the identities (9.1 item 1)" | the gates draw search-year days (G-8); TS's search-year gates are run as the pairs' references; the registered gate paths stay G-7's identities |
| D-28 | L808 | 8, horizons and blocks | "all, early and late per measure" | all, first and second per measure (G-6) |
| D-29 | L824 | 9.1 item 1 | "every start, every column as E-010 compared them" | unchanged as an identity under `identity/` (G-7); inside the reading's run, the references' comparison with U1's rows is on the starts whose 252-session replay ends inside the search years (G-7) |
| D-30 | L831 | 9.1 item 2 | "at every start and all 500 paths as the run's first stage" | unchanged as the identity script's stage (G-7); G-3 (b) and (c) are added to it |
| D-31 | L832, L836 | 9.1 item 3 | "every start" | unchanged: the Lucid identities, whole-window, under `identity/` (G-7) |
| D-32 | L859 | 9.3 | "stream and block" | stream and G-6's block |
| D-33 | L862-L863 | 9.3, G-3's count | "by release and year" | by release and year, 2020 to 2023 (D-14) |
| D-34 | L376, L902, L948 | 4.6 A-10; 9.3; 10.1 item 9 | "every start" | every search-year start (G-5) |
| D-35 | L908 | 10.1 | "every block of" | every block of G-6 |
| D-36 | L939-L940 | 10.1 item 8 | "paired with TS's registered gate paths" | paired with TS's search-year gate at the same seed and paths (G-8) |
| D-37 | L953-L954 | 10.1 item 11 | "the early and late blocks and the" | the first and second halves and the start years 2020 to 2023 beside (G-5, G-6) |
| D-38 | L957 | 10.1 item 11, the stability flag | "opposite signs on the early and late blocks" | opposite signs on the first and second halves (G-6) |
| D-39 | L1003-L1004 | 10.2, its effect | "much of the late block at months 6 and 12" | much of each half at months 6 and 12 (section 1) |
| D-40 | L1025-L1026 | 11, the operator's choice | "on the development window 2020-2026" | on the search years 2020-2023, the held-out years unread by it (G-14) |
| D-41 | L1029-L1030 | 11, the binding | "The blocks read here are recorded as read for firm contracts" | G-13 |
| D-42 | L1067 | 12, inherited seeds | "paired with the registered paths" | paired with the reference's search-year gate at the same seed (G-8) |
| D-43 | L1076 | 13 item 2 | "every block read, recorded as read" | the search years and their halves recorded as read for firm contracts (G-13); counted beside: the two references' search-year gates (G-8) |
| D-44 | L1100 | 14.3, T-0 | "the `Judged-block reads:` purposes parse and choose nothing" | T-0 is `tests/test_rd_search_years_drafts.py` (with this text), extended at the pin: no line of the reader's judged-block form; the parent's pin; every searched line accounted for (section 7) |
| D-45 | L1120-L1123 | 15, files | "`results/fc_reading.csv`" | `results/fcs_reading.csv`, `results/fcs_gate.csv`, `results/fcs_menu.csv` (G-9) |
| D-46 | L1125 | 15, manifests | "`prereg_id` = `RD-01`" | `prereg_id` this file's id at the pin (G-9) |
| D-47 | L1134 | 15, weight | "Every start on two arms" | every search-year start on two arms; the replays are shorter than the parent's |
| D-48 | L1138-L1141 | 15, a restart or a rerun | "passes `repeat="E-NNN"`" | G-15 |
| D-49 | L1167-L1169 | 16 item 6, the name | "must match the test's glob `RD-*firm*.md`" | the pinned name is 0.2's; this file's T-0 asserts it (D-44) |
| D-50 | L73 | header table, id | "RD-01" | this file's id at the pin (0.2); every result's `prereg_id` is it (G-9) |
| D-51 | L937-L938 | 10.1 item 7, TS's placement and Focused Trader rows | "TS only, from Q-17's own reading, not rerun here" | TS only, from Q-44's per-start rows (Q-17's reading) on the starts whose 252-session replay ends inside the search years, not rerun here (G-7) |

## 4. Unaffected, because

Every other line the search of section 7 finds in the parent, with the reason it needs no change.

- **L3**: the parent's own status line and date; the parent stays pinned as it is (0.3).
- **L22, L27, L35**: the parent's table of changes between its drafts, a record of how it was made; each rule it
  summarises is cited at its own line (D-16 to D-49) or governed by section 2.
- **L85**: NQ's confirmation tests and the reserve from 2026-07-17, which this reading never reads; unchanged.
- **L92**: "a matched pair with Topstep's on every start day": the pairing holds on every start read; G-5 sets the
  starts.
- **L139, L155**: a rule's applicability date (Fast Pass's terms for accounts opened on or after a date) and the G-11
  gap; a term of the record, not a read window. G-11 itself is D-13.
- **L154**: describes Stage 2's practice (today's rules replayed over its history).
- **L210**: the drafter's disclosed reads of the release calendars; a record.
- **L282, L369, L370, L377, L396, L696, L890, L943, L1102, L1232**: a firm's clock in calendar days, or the record key
  that translates it to sessions; a rule's term, unchanged.
- **L25, L631, L634, L635, L646, L895, L896, L899, L1155**: the pinned calendars and release files and their hashes;
  the files are fixed as declared, and G-1 uses their days only inside the search years.
- **L406, L418, L435, L448**: "blocks" in another sense (a trade's day block, `DayBlock`, or a rule that blocks a
  request).
- **L520, L1018**: a property of a term on any start (monotone in one direction); it holds on each search-year start.
- **L679, L918, L941**: a rule's or a measure's year (idle for the rest of the year; a year's payouts; the gate's
  two-year growth on resampled days that carry no date, G-8).
- **L973, L974, L986**: 10.2's window rule, stated per block; it applies unchanged to G-6's blocks.
- **L1028**: no confirmation; NQ from 2026-07-17 is never read; unchanged.
- **L1047, L1049, L1055, L1059**: section 12's seed check, its date and "block" meaning the seed block; the seeds are
  inherited unchanged (section 8).
- **L1181**: the operator's written question to DayTraders ("historical data"); unchanged.
- **L1196**: E-015's limits "never block"; unchanged.

## 5. What does not change

The plans and their terms (section 2.1, 4, 5, Appendix R); the user held fixed (2.3); the adapters A-1 to A-11 and
their switches (4.6); the gaps (4.7); the cost rule (4.8); the table's inputs (4.9); every unread term and its reading
(section 5); the cells, the corners, the one-at-a-time runs and their names (section 7), and their counts: 30 replays,
or 34 with the four news runs, 27 denial-ladder replays and 16 gates beside, with the two references' search-year
gates added beside (G-8); the parameters' classes (section 8); the oracles (9.2); the mechanics (9.3) on the blocks of
G-6; the scorecard, the paired readings, the price grid, the evenness trade-off and the menu's flags (10.1) on the
search years; the uncertainty method (10.2) unchanged, its window counts the search years'; what the reading delivers
and what each outcome means (11) on the search years; the seeds (section 12), inherited unchanged and by reference
(section 8); the counting (13); the adapters' rules in code and tests T-1 to T-15 (14), T-0 replaced (D-44); the run's
order and waits (15), G-3 added before the reading; the operator's items (16).

## 6. The build list (for a later item; nothing here is built by this one)

- **B-1. The declaration.** `extended/firm_reading.py`'s `DECLARATION` names this file at its pinned name and
  `PURPOSES` is empty; `scripts/rd01_reading.py` (or a new runner beside it) drops `precheck`'s purposes and calls
  `reader.authorise_engine_read(reader.CHOICE_START, reader.CHOICE_END, ...)` with no purpose; it refuses to run if any
  argument or constant names the parent's path or purposes.
- **B-2. The cut** (G-2): a new module (for example `extended/search_years.py`) with a context manager that wraps the
  vendored bar and atlas readers the registered builders call, dropping every row after `reader.CHOICE_END` and
  restoring them on exit; `streams_of` builds through it; a check refusing any day block or date after
  `reader.CHOICE_END` in a job before any replay or gate. If a builder reads around the wrapper, the build stops and
  reports (G-2).
- **B-3. The blocks** (G-6): a repository function `block(records, which, h)` for `which` in `all`, `first`, `second`;
  `extended/firm_reading.py`'s and `extended/firm_menu.py`'s `BLOCKS` become `("all", "first", "second")`;
  `extended/user_readings.py`'s `KNOWN_BLOCKS` and `READING_BLOCKS` and `_which` learn the halves; 9.3's counts by
  block (`COUNT_HORIZON`) and the stability flag read first and second. `u_select.block` is not edited and is called
  only for `all`.
- **B-4. The verdict constants** (G-4): `build_with_deltas` records the search-year shift the builder computes on the
  cut; the `r6` check (one shift per stream) unchanged; the manifest carries the shift.
- **B-5. The identities:** `identity/firms_identity.py` and the shared identities unchanged (G-7); a new identity
  script for G-3 (b) and (c), its cover declared under Q-111's rule, its own row; inside the run, `identity_problems`
  and the reference comparisons restricted to the starts whose 252-session replay ends inside the search years (G-7).
- **B-6. The gate** (G-8): `registered_gate` and `paired_paths` pair each corner's gate with the reference's
  search-year gate at the same seed; `gate_reading` runs the two references' search-year gates first.
- **B-7. The outputs** (G-9): `write_all` and `manifest_params` write `results/fcs_*.csv` with this file's id, the
  window, G-3's row and G-11's list.
- **B-8. Tests:** T-0 (`tests/test_rd_search_years_drafts.py`, extended at the pin); a T-3S on synthetic campaigns
  -- every reading is byte-identical when every session after 2023-12-29 is replaced, the runner refuses a stream with
  such a session, and each first-half reading at h is byte-identical when every second-half session is replaced; B-2's
  wrapper on a toy reader (rows after the cut never returned; the reader restored on exit, on error too).

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

To re-run by hand: `python -m pytest -q -o addopts= tests/test_rd_search_years_drafts.py`; or, for the list of lines,
`grep -inE` with the patterns above (POSIX `grep -E` lacks `(?:`; use `python -c` or the test's `parent_hits`).

## 8. Counting, seeds and confirmation

- **Counting.** No program family number and no level (E-023 (1)); the next numbered family's k is unchanged. The
  parent's counts hold (section 5), with the two references' search-year gates added beside (G-8). The parent's counts
  are never also spent: the parent is never run (0.3).
- **Seeds.** The parent's section 12, inherited unchanged and by reference (its block, statuses and inherited seeds);
  no seed is restated here, so the parent's T-0 still finds its block in no other declaration. The parent was never
  run, so none of its seeds has been drawn on the bars.
- **Confirmation.** None: nothing is carried; NQ from 2026-07-17 is never read.

## 9. Open before the pin

1. **The red team's read** of this draft and of its three siblings (`prereg/DRAFT_RD-02S_payout_policy_search_years.md`,
   `prereg/DRAFT_RD-03S_contract_levers_search_years.md`, `prereg/DRAFT_RD-05FS_firm_modes_part_f_search_years.md`).
2. **The id and the name** (0.2): the lead's; at the pin the file is renamed, its title and status put in pin-time
   form, and its id written where this draft says "RD-01S"; nothing else changes.
3. **G-2's feasibility** is a build question; its stop-and-report clause is declared now.
4. **The pinning row** records the parent as superseded, never run (0.3), and RD-05's part F reading this file's
   `LU` rows in place of the parent's (`prereg/DRAFT_RD-05FS_firm_modes_part_f_search_years.md`).
