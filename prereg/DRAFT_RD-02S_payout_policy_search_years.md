# DRAFT RD-02S: payout policy in a user's first months, on the search years only (reading PP-S) -- a delta declaration of RD-02, a described reading, unnumbered (E-023 (1))

**Status: a draft, not pinned (O-7, the lead's ruling in E-221).** Drafted on wt/wt-firms, 2026-11-18. It re-declares
`prereg/RD-02_payout_policy.md` on the search years alone, so that no part of the reading touches NQ's held-out years
(E-208), which E-221 (O-1) keeps for one joint fixed-sequence confirmation across firms. The parent is not edited: it
stays on record, pinned, and is never run (section 0.3). The red team reads this draft before it is pinned; the lead
assigns its id at the pin (section 0.2). Its sibling `prereg/DRAFT_RD-01S_firm_contracts_search_years.md` states the
same general replacements for RD-01; each draft is complete on its own.

| field | value |
|---|---|
| id | proposed **`RD-07`** at the pin (section 0.2); until then `RD-02S` |
| parent | `prereg/RD-02_payout_policy.md` sha256 `0c9dddabbc1cda0cd57787b4e8b5d34d42ee600df2d2c90e8a26178a31cb407c` (of its LF text), pinned by E-082 |
| reading | PP-S: the parent's reading PP, every cell, run and reading as the parent declares them, on the search years |
| kind | a **described reading** (E-023 (1)): never carried; no program family number, no level, no pass line, no pick |
| development data | NQ 1-minute bars, 2020-01-02 to 2023-12-29 (the search years, E-208), read only inside Stage 2's engine by P-14's and P-16's registered builders, cut at the read (G-2) |
| held-out years | 2024-01-02 to 2026-07-16: never read by this reading, under any purpose (G-1, G-10) |
| blocks | all search-year starts (the headline); the search years' first half and second half beside, each per measure at its h (G-6) |
| judged-block purposes | none (G-10) |
| Appendix A | not incorporated (D-50): a separate exploratory item, as the parent states; unrun |
| confirmation | none; NQ from 2026-07-17 never read |
| the build | not built by this item: section 6 is the build list for a later item |

## 0. What this file is, and how it reads its parent

### 0.1 The incorporation

This declaration **is the parent's text, with the replacements below**. Every section, table, rule, cell, count,
seed, oracle, test and wait of `prereg/RD-02_payout_policy.md` at the sha256 above -- its Appendix A excepted (D-50)
-- is part of this declaration, read with:

1. the general replacements G-1 to G-15 (section 2), which apply wherever the parent's words reach them;
2. the line-by-line replacements of section 3, each citing the parent's line and a short quote from it.

Where a replacement and the parent's words differ, the replacement is the declaration. Where section 3 is silent on a
parent line, section 2 governs it; where both are silent, the parent's words stand (section 5 lists what stands, and
section 4 lists every line the search of section 7 found that needs no change, with the reason). Section numbers,
item numbers, cell names, run names and test names are the parent's.

### 0.2 The id scheme (proposed; the lead assigns at the pin)

RD-06 for RD-01's delta, **RD-07 for this file**, RD-08 for RD-03's, RD-09 for RD-05's part F, in the order of the
parents. The pinned name is `prereg/RD-07_payout_policy_search_years.md`. New numbers, not a suffix: the reader reads
an id as `RD-` and digits (`extended/reader.py`'s `F_ID`, `DECLARATION_ID`), so `prereg/RD-02S_...` would be read as
RD-02, and a `repeat=` row naming the parent would authorise a rerun of this file. **One glob to narrow at the pin:**
the parent's T-0 (`tests/test_pp_draft.py`) finds its declaration by `RD-*payout*.md` and asserts exactly one, so the
pinned name above matches it; the pin narrows that glob to `RD-*_payout_policy.md`, nothing else changed (E-200 did
the same for RD-01's T-0).

### 0.3 The parent, superseded before any run

No result of the parent exists: the read ledger holds no line of RD-02 and no file `results/pp_*.csv` exists at this
draft (RD-02's build and its two-worker check are merged, E-220; its run is not). At this file's pin the parent is
**superseded, never run**: no run takes its three purposes, its result files are never written, and its id is never a
manifest's `prereg_id`. The reader cannot yet see a withdrawal (the audit's R-8 registry is not built), and its
held-out rule 4 refuses the parent's judged reads only until a market's verdict row exists; so the supersession is
enforced by the build (section 6, B-1) and recorded in the pinning row.

## 1. Why, and what it does to what the reading can show (E-051)

**Why.** Under E-208 every choice and every map the journey search draws on is made on the search years, and the
held-out years are read once, by the joint confirmation (E-221, O-1). The parent reads the whole development window, its
late block by name, and its judged-block purposes, and its levers are now in the search's lever space (CHARTER 3.6
(b)); any range drawn from its menu would carry a held-out read into the search (CHARTER 3.3 (a)). O-7 rules that the
reading is re-declared on the search years.

**What it does to what the reading can show.** The menu describes the search years only. Each measure's starts at its
horizon h are fewer (G-5): at h = 252 they are the starts with 252 sessions inside the search years, so the headline
holds fewer kept windows and more readings print "too few separated windows for an interval"; each half (G-6) holds
about two years, so most half readings at months 6 to 12 -- where the parent's section 2 says a gain from keeping money
in the account should show -- print the sign count alone. The stability flag compares two halves of four years instead
of the search years against the held-out years. The verdict arm's shift is the search years' own (G-4). Nothing else of
the reading changes: the levers, the cells, the held-state rule, the counts, the uncertainty method and the oracles are
the parent's.

## 2. The general replacements

- **G-1. The window.** The development data are NQ 1-minute bars from 2020-01-02 to 2023-12-29, the search years
  (E-208). The held-out years 2024-01-02 to 2026-07-16 are never read by this reading, under any purpose, by any of its
  runs, gates, identities in its own run, or beside readings; NQ from 2026-07-17 is never read. Wherever the parent says
  "the development window", "2020-2026" or "the whole window" of what this reading reads, read the search years. A
  pinned calendar (E-029, E-050) is used only on days inside the search years.
- **G-2. The cut at the read.** The reading's process authorises the engine's reads with
  `extended.reader.authorise_engine_read` on 2020-01-02 to 2023-12-29 -- the choice block, which needs no purpose and is
  not ledgered -- and no bar or atlas row dated after 2023-12-29 reaches any function of the registered builders, the
  replay, the gate or the reading: the vendored readers the builders call are wrapped for the call so that every row
  after 2023-12-29 is dropped at the read, and restored after it (nothing vendored is edited). The day blocks and dates
  handed to the replay and to the gate end at the search years' last session, and the runner refuses, before any
  replay, a block or a date after 2023-12-29. **If a registered builder cannot be cut at its reads, the build stops and
  reports; this declaration does not fall back** to a whole-window build cut afterwards. The builders' own whole-window
  checks (the registered trades' content hash, the registered edge rows) cannot hold on the cut and are replaced by
  G-3 (b).
- **G-3. The cut identity, refusing** (its own script under `identity/`, the purpose `identity`, its own decision row,
  before the reading; one script may serve all four deltas). (a) The parent's whole-window identities hold as the parent
  states them (G-7). (b) For P-14 and P-16, the stream built on the cut equals the whole-window stream's day blocks up to
  2023-12-29, block for block, every field, the per-R outcomes included. (c) The vendored estimator of the verdict arm's
  constants (G-4), applied to the whole-window stream, reproduces the registered constants exactly. The script reads the
  whole window under the purpose `identity` (an identity of Stage 2's engine against Stage 2's files), writes pass or
  fail lines and nothing of any cell, and is not this reading. A failure of (b) stops the reading; a failure of (c) alone
  stops the verdict arm (G-4).
- **G-4. The verdict arm's constants, re-estimated on the search years.** The parent's N2: the bound "was estimated on
  the whole development window", so every verdict row is a function of the held-out years through one constant per R.
  Here `e`, `lb`, `e_by_rr` and `lb_by_rr` are the vendored estimator's (the one the registered builder calls, at the
  registered trial count) on the search-year trades and days; under G-2 the builder's own call computes them on the cut.
  **Reason:** inherited, the constant would carry a held-out read into every verdict row and so into the lever space
  (CHARTER 3.3 (a)); re-estimated, the arm is a function of the search years alone, at the cost of one identity
  (G-3 (c)). The `point` arm is unchanged. If G-3 (c) fails, the verdict arm is not run: `point` is the headline, every
  row labelled so.
- **G-5. The starts and the horizon embargo** (CHARTER 3.6 (d)). The starts are every start day U1 reads inside the
  search years. Each measure is read at its horizon h (the parent's 5 item 3 table, unchanged) only on starts with h
  sessions inside the search years: on the cut replay a start observes no session after 2023-12-29, so
  `u_select.block(records, None, h)` gives exactly these. U1's long replay of up to 252 sessions and its exact-length
  runs stop at the cut. Wherever the parent says "every start" or "all starts" of what is replayed or read, read the
  search-year starts with the horizon left. By start year: 2020 to 2023, means only, not purged within the search years
  (a start late in a year reads the next year's sessions), and 2023's starts read only 2023's sessions; labelled so.
- **G-6. The blocks: the late block replaced by the search years' second half.** On the cut replay the parent's early
  block equals the headline and its late block is empty, so both are replaced, per measure at its h:
  - **all**: every search-year start with h sessions inside the search years (the headline);
  - **first**: the starts of 2020 and 2021, each read at h only if h sessions remain before the first session of 2022
    (the parent's per-measure purge, F6 and D-621 (4)(b), moved to the half's end);
  - **second**: the starts of 2022 and 2023, read at h only with h sessions inside the search years.

  **Reason:** the stability flag ("not stable across blocks") needs two disjoint stretches read apart; two calendar
  halves of equal length, fixed by the calendar before any read and cut at a year's end as the parent's blocks were,
  keep it without reading a held-out day. The vendored `u_select.block` fixes its years, so the halves are a function of
  this repository (B-3). Nothing is chosen on any block. **Considered and not taken:** no blocks (it loses the flag);
  halves by start count (a cut that moves with the data).
- **G-7. The identities.** The parent's 8.1 items 1 to 3 run as the parent states them, on the whole window, from
  `identity/pp_identity.py` under the purpose `identity` and their own row, and the shared identities it waits for (Q-05,
  Q-80, Q-93, Q-101) are unchanged: they compare Stage 2's engine with Stage 2's registered files and write no outcome of
  any cell, so they are not this reading's reads. Inside the reading's own run (8.1 items 2's repeat, 4 and 6), every
  comparison with a registered whole-window file (U1's start rows; Q-44's per-start rows) is made **only on the starts
  whose 252-session replay ends inside the search years**, every column the parent names, refusing; no row of a later
  start is loaded. Where the parent cites the bases' readings from Q-44's file (9.1 item 7), they are cited on the same
  starts only. G-3 holds before the run.
- **G-8. The gate on the search years.** Every gate beside draws its resampled days from the search-year day blocks
  only. Each policy cell's gate is paired with its base's own search-year gate at the same seed and the same number of
  paths (the same pool of days, so the same day draws), not with the registered gate paths, which draw from the whole
  window. The two references' search-year gates are run and read beside as the pairs' references; the registered gate
  paths stay G-7's identities.
- **G-9. The outputs.** New files, never the parent's: `results/pps_reading.csv`, `results/pps_gate.csv`,
  `results/pps_menu.csv`, each through `extended.results.write_result` with its sidecar manifest, `prereg_id` this
  file's id at the pin, the window 2020-01-02 to 2023-12-29, the rows under which G-3 and the parent's identities held,
  and every manifest field the parent's section 14 lists.
- **G-10. No judged-block purpose.** This declaration reads no day of the held-out years, so it names no purpose of the
  reader's judged-block form and carries no line of that form; the reader refuses any judged read citing it. The
  parent's line is the parent's and is never taken (0.3).
- **G-11. The held-out read ledger, inherited and labelled** (CHARTER 3.6 (b); no figure cited). This reading rests on
  designs and records that read the held-out years before it: P-14 fixed as R* from the whole window (Stage 2 D-626);
  P-14's rung map and P-16's mark cutoff resolved on the whole window (E-203 S-2); P-16's stop chosen on each block
  (Stage 2 D-554); the registered state table (`state_dp_e-0.050_lamstar_noclose`) and protocols as Stage 2 registered
  them; Stage 2 D-564 to D-566's payout screen on P-16's cell over the whole window; program U's nine families, which
  read P on the late block, and its families 6, 7 and 8 on both blocks; U1's whole-window start rows (Stage 2 D-620) and
  Q-44's per-start rows, which G-7's comparisons cite on search-year starts only; Stage 2's signal search over the whole
  window; and the parent's own pinned text, declared over the whole window and never run. Nothing here re-estimates
  them; every result file of this reading names them.
- **G-12. Prior exposure, re-read.** The parent's prior-exposure rows stand as records. Where a row's bearing reads "the
  late block has been read for P nine times; it is late development, not out of sample", read: those reads were of the
  held-out years; they are G-11's entries; this reading reads none of those years.
- **G-13. The binding.** The parent's "the blocks this reading reads are recorded as read for payout policy on P-14 and
  P-16" reads: the search years, and their two halves, are recorded as read for payout policy on P-14 and P-16; the
  held-out years are not read by this reading and are recorded as unread by it.
- **G-14. In sample.** Every statement made from this reading, and the operator's choice from its menu, is a
  description of the search years, in sample, with no confirmation (E-023 (1)); the held-out years stay unread by it.
- **G-15. Reruns.** The reader ledgers no choice-block read, so its once-per-purpose refusal does not reach this
  reading. The parent's rule is kept by the lead: only the first complete clean run is read; a restart or a rerun is
  recorded by the lead with its log under a decision row naming this file, which says which run replaces which and
  why; a result file is never overwritten (G-9).

## 3. Every dependency in the parent, line by line

The parent's lines as numbered in its LF text at the pinned sha256. A row's lines are one line, a range whose joined
text holds the quote, or a list of lines each holding the quote. The replacement is this declaration's.

| # | parent lines | where | quote | replacement |
|---|---|---|---|---|
| D-01 | L45 | header table, development data | "NQ 1-minute bars, 2020-01-02 to 2026-07-16" | NQ 1-minute bars, 2020-01-02 to 2023-12-29, cut at the read (G-1, G-2) |
| D-02 | L47 | header table, blocks | "the late block from 2024-01-02 (section 5)" | all search-year starts the headline; the first and second halves beside, each purged per measure (G-6) |
| D-03 | L49 | header table, beside | "8 gates (6 new, 2 identities)" | the 6 new gates, and the two references' search-year gates as their pairs' references (G-8) |
| D-04 | L51 | header table, the parent's purposes | "three purposes, on the line of section 5 item 6" | none (G-10); the identities from `identity/*.py` under their own row, unchanged (G-7) |
| D-05 | L147 | 1, why described | "the late block's few independent three-month stretches" | the same reason holds a fortiori on the search years: fewer independent stretches still (section 1) |
| D-06 | L154 | 1, the operator's choice | "a described development reading" | a described reading of the search years (G-14) |
| D-07 | L156 | 1, the operator's choice | "a description of the development window" | a description of the search years (G-14) |
| D-08 | L188-L189 | 2, where to look | "where the late block has the fewest independent windows" | where each half has the fewest independent windows (section 1) |
| D-09 | L201 | 3, Stage 2 D-564 to D-566 | "over the whole development window" | a record; a held-out read by Stage 2, entered in G-11 |
| D-10 | L202, L203 | 3, program U families 6, 7 and 8 | "both blocks" | a record; held-out reads by Stage 2, entered in G-11 |
| D-11 | L204 | 3, U1 and Q-05 | "P-14's and P-16's own journeys, every start" | a record; the references' rows are whole-window, and G-7 compares them on search-year starts only |
| D-12 | L205 | 3, program U's nine families | "it is late development, not out of sample" | those reads were of the held-out years; G-11's entries; none read here (G-12) |
| D-13 | L207-L211 | 3, N2 | "So an early-block reading on the verdict arm is a function of 2024-2026 through that one constant" | the verdict arm's constants re-estimated on the search years (G-4); no reading is a function of the held-out years |
| D-14 | L318 | 5, its title | "Data, blocks and the unit" | section 5 as items 1 to 6 are replaced in D-15 to D-24 |
| D-15 | L320 | 5 item 1 | "one development start day" | one search-year start day (G-5) |
| D-16 | L320-L322 | 5 item 1 | "U1 runs a long replay of up to 252 sessions plus its exact runs" | U1's long replay of up to 252 sessions and its exact runs, stopping at the cut (G-5) |
| D-17 | L325 | 5 item 2 | "the same start days, the same blocks and the same seeds" | the same search-year start days, G-6's blocks and the parent's seeds |
| D-18 | L327-L333 | 5 item 3 | "the starts from 2024-01-02 with h sessions left" | item 3's three sets are G-6's all, first and second, each at its measure's h; the horizon table is unchanged |
| D-19 | L330-L332 | 5 item 3, the early block | "No early reading touches a 2024 session, except through the verdict arm's bound (N2, section 3)" | no reading touches a session after 2023-12-29, and none through the bound (G-2, G-4); no first-half reading touches a second-half session (G-6) |
| D-20 | L335-L337 | 5 item 3 | "The early and late blocks are read separately" | the first and second halves are read separately, so the menu can flag a policy whose effect changes sign between them (G-6) |
| D-21 | L354-L356 | 5 item 3, by start year | "the purged comparison is the early and late blocks'" | by start year 2020 to 2023 (G-5); the purged comparison is the halves' (G-6) |
| D-22 | L357-L360 | 5 item 4 | "The late block holds about nine non-overlapping 63-start windows" | each half holds about two years of starts and the headline the search years'; each reading prints its own count (9.2), none typed here |
| D-23 | L361 | 5 item 5 | "No NQ from 2026-07-17" | no NQ after 2023-12-29 is read by this reading (G-1); NQ from 2026-07-17 is not on disk and never read |
| D-24 | L362-L366 | 5 item 6, the seal and the parent's purposes | "`payout_scorecard`, `payout_ladder_beside`, `payout_gate_beside`" | none (G-10): the reading authorises 2020-01-02 to 2023-12-29 only (G-2); this file carries no line of the reader's judged-block form |
| D-25 | L494 | 7.1, blocks | "all; early and late per measure (section 5)" | all; first and second per measure (G-6) |
| D-26 | L544 | 8.1, its title | "whole-window identities only from `identity/*.py`" | unchanged: the whole-window identities stay under `identity/` (G-7); G-3 added |
| D-27 | L555, L558 | 8.1, the shared identities | "every start" | unchanged, whole-window, under `identity/` (G-7) |
| D-28 | L564 | 8.1, this reading's own | "never under this file's `Judged-block reads:` line" | under the purpose `identity` and their own row; this file has no such line (G-10) |
| D-29 | L577 | 8.1 item 2 | "both arms, every start, every column" | unchanged as `identity/pp_identity.py`'s identity (G-7) |
| D-30 | L588 | 8.1 item 4 | "And the reading's own `ref` start rows equal U1's again" | on the starts whose 252-session replay ends inside the search years (G-7) |
| D-31 | L595-L596 | 8.1 item 6 | "equals Q-44's `results/user_beside_starts.csv`" | on the starts whose 252-session replay ends inside the search years (G-7) |
| D-32 | L604 | 8.1, the order | "a rerun is a further judged read under `repeat=`" | a rerun is recorded by the lead under a row naming this file (G-15) |
| D-33 | L618 | 8.3 | "For each new cell and each block" | for each new cell and each of G-6's blocks |
| D-34 | L636-L638 | 8.3, E-029's voided days | "The three days E-029 voids for families" | of E-029's voided days only 2020-07-01 is in the search years; it is listed with the number of starts, per block of G-6 and horizon, whose h sessions hold it; the two later days are outside the search years and never read |
| D-35 | L640, L894, L997 | 8.3; 13.1 item 1; 14 weight | "every start" | every search-year start (G-5) |
| D-36 | L647 | 9.1 | "on every block of section 5" | on every block of G-6 |
| D-37 | L704 | 9.1 item 7 | "The bases' readings are cited from Q-44's file" | cited from Q-44's file on the starts whose 252-session replay ends inside the search years (G-7) |
| D-38 | L711-L713 | 9.1 item 8 | "paired with the base's registered gate paths" | paired with the base's search-year gate at the same seed and paths (G-8); the two references' gates run as the pairs' references, the registered paths staying G-7's identities |
| D-39 | L722-L723 | 9.1 item 10, the menu | "the early and late blocks beside" | the first and second halves beside, and by start year 2020 to 2023 (G-5, G-6) |
| D-40 | L724-L725 | 9.1 item 10, the stability flag | "on the early and late blocks is flagged" | on the first and second halves is flagged (G-6) |
| D-41 | L815-L816 | 10, the binding | "The blocks this reading reads are recorded as read for payout policy" | G-13 |
| D-42 | L829 | 11, the build's toys seed | "T-3's synthetic late block" | T-3S's synthetic sessions after the cut (D-48), drawn from the same seed (section 8) |
| D-43 | L878 | 12 item 2 | "the 2 references' are 8.1's identities" | the two references' search-year gates are run beside as the pairs' references (G-8); the registered paths stay 8.1's identities |
| D-44 | L880 | 12 item 2 | "every block read, recorded as read for payout policy" | the search years and their halves recorded as read for payout policy (G-13) |
| D-45 | L942 | 13.3, T-0 | "one `Judged-block reads:` line" | T-0 is `tests/test_rd_search_years_drafts.py` (with this text), extended at the pin: no line of the reader's judged-block form; the parent's pin; every searched line accounted for (section 7) |
| D-46 | L958-L961 | 14, files | "`results/pp_reading.csv`" | `results/pps_reading.csv`, `results/pps_gate.csv`, `results/pps_menu.csv` (G-9) |
| D-47 | L964 | 14, manifests | "`prereg_id`: `RD-02`" | `prereg_id` this file's id at the pin (G-9) |
| D-48 | L945 | 13.3, T-3 | "every early-block reading at horizon h is byte-identical when every session from 2024-01-02 on is replaced" | T-3S: every reading at h is byte-identical when every session after 2023-12-29 is replaced, the runner refuses a stream holding one, and every first-half reading at h is byte-identical when every second-half session is replaced; the verdict arm at its search-year constant (G-4) |
| D-49 | L985-L986 | 14 step 2 | "The runner authorises its engine reads under the three purposes of section 5 item 6" | the runner authorises 2020-01-02 to 2023-12-29 with no purpose (G-2, G-10); G-3 holds first |
| D-50 | L1046-L1052 | Appendix A | "A SEPARATE ITEM, EXPLORATORY" | not incorporated: the parent states it is not part of reading PP; it stays on record, unrun; any run of it needs its own row ruling its window (its identity (b) reproduces a whole-window registered gate call) |
| D-51 | L998-L1002 | 14, a restart or a rerun | "Each purpose on the line allows one clean run" | G-15 |
| D-52 | L1000 | 14, a restart or a rerun | "a further judged read" | G-15 |
| D-53 | L41 | header table, id | "every result's `prereg_id` is `RD-02` (section 14)" | this file's id at the pin (0.2); every result's `prereg_id` is it (G-9) |

## 4. Unaffected, because

Every other line the search of section 7 finds in the parent, with the reason it needs no change.

- **L7, L15**: the parent's text history, a record of how it was made.
- **L54**: NQ's confirmation tests and the reserve from 2026-07-17, which this reading never reads; unchanged.
- **L67, L69, L72, L79, L80, L85, L92, L103, L105, L112**: the parent's table of changes between its drafts, a record;
  each rule it summarises is cited at its own line (D-01 to D-52) or governed by section 2.
- **L121**: "a matched pair with its base on every start day": the pairing holds on every start read; G-5 sets the
  starts.
- **L139, L236, L237, L660, L716, L809**: a user's first months and year, a year's payouts, or Stage 2's two-year growth
  (a measure's or the gate's horizon on resampled days that carry no date, G-8); unchanged.
- **L175**: "an early payout", another sense of the word.
- **L200**: a record of a search Stage 2's log was given, with its date; unchanged.
- **L218, L224, L227**: the drafter's disclosed reads (code, rules and calendars); records.
- **L252, L253, L254, L255, L256, L257, L258, L259, L260, L261, L262, L263**: section 4's rule table, each key's date
  read; a term of the record, not a read window.
- **L282, L283, L297, L298, L300, L626, L627, L630, L631, L972**: the pinned calendars and their hashes; the files are
  fixed as declared, and G-1 uses their days only inside the search years.
- **L339, L345, L346, L347, L350, L493**: the horizon table and its sources (`u_select.MEASURES`); each measure's h is
  unchanged.
- **L467**: nothing is chosen on any block; holds for G-6's blocks.
- **L495, L743, L744, L752, L754, L759, L760, L765, L770, L794**: 9.2's window rule and its pieces, stated per block;
  they apply unchanged to G-6's blocks.
- **L525**: a record of another identity owed (P-15's); unchanged.
- **L593, L632, L634**: "blocks" in another sense (a start's day blocks, a trade's block).
- **L813**: no confirmation; NQ from 2026-07-17 is never read; unchanged.
- **L837, L845, L848, L853, L858**: section 11's seed check, its date and "block" meaning the seed block; the seeds are
  inherited unchanged (section 8).
- **L950, L1007**: the identity script's full run and the Q-93 wait, whole-window identities under `identity/` (G-7).
- **L1035**: E-015's limits "never block"; unchanged.

## 5. What does not change

The mechanism (section 2); the verified rules and every assumption of section 4; the levers L1 and L2, the grid, the
held-state rule and its rule-sensitivity runs (section 6); the parameters' classes and what is dropped (7); the oracles
(8.2); the mechanics (8.3) on G-6's blocks; the scorecard, the paired readings, each lever alone and their
interaction, what diverges, the readings beside and the menu's flags (9.1) on the search years; the uncertainty method
(9.2), its window counts and honesty settings the search years'; what the reading delivers (10) on the search years;
the seeds (section 11), inherited unchanged and by reference (section 8); the counting (12): 11 runs, 32 replays beside
and the 6 new gates, with the two references' search-year gates added beside (G-8); the adapters, their rules in code
and the tests T-1, T-2 and T-4 to T-11 (13), T-0 and T-3 replaced (D-45, D-48); the run's two steps and waits (14),
G-3 added to step 1; the lead's and the operator's items after the pin (15).

## 6. The build list (for a later item; nothing here is built by this one)

- **B-1. The declaration.** `extended/pp_run.py`'s `DECLARATION` names this file at its pinned name and `PURPOSES` is
  empty; `scripts/pp_reading.py`'s `check` and `ledger` calls authorise `reader.CHOICE_START` to `reader.CHOICE_END`
  with no purpose; the runner refuses to run if any argument or constant names the parent's path or purposes.
- **B-2. The cut** (G-2): the shared module of RD-06's B-2 (for example `extended/search_years.py`) wrapping the vendored
  bar and atlas readers for the builders' calls, and the refusal of any day block or date after `reader.CHOICE_END`
  before any replay or gate.
- **B-3. The blocks** (G-6): `extended/pp_run.py`'s `BLOCKS` become `(("all", None), ("first", "first"), ("second",
  "second"))` through the shared repository block function; `extended/pp_reading.py`'s `block` and `by_year` call it
  (`u_select.block` is not edited and is called only for `all`); every place that iterates `BLOCKS` is unchanged.
- **B-4. The verdict constants** (G-4): recorded from the builder's call on the cut; the manifest carries them.
- **B-5. The identities:** `identity/pp_identity.py` and the shared identities unchanged (G-7); the shared G-3 script;
  inside the run, 8.1 items 2's repeat, 4 and 6 and 9.1 item 7's citations of Q-44 restricted to the starts whose
  252-session replay ends inside the search years.
- **B-6. The gate** (G-8): each policy cell's gate paired with its base's search-year gate, the two references' gates
  run first.
- **B-7. The outputs** (G-9): `results/pps_*.csv` with this file's id, the window, G-3's row and G-11's list.
- **B-8. Tests:** T-0 (`tests/test_rd_search_years_drafts.py`, extended at the pin); T-3S (D-48) on synthetic campaigns
  under the parent's build-toys seed; the narrowed glob of `tests/test_pp_draft.py` at the pin (0.2).

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
- **Seeds.** The parent's section 11, inherited unchanged and by reference (its block, statuses, the inherited seeds and
  the honesty series' keys); no seed is restated here, so the parent's T-0 still finds its block in no other
  declaration. The parent was never run, so none of its seeds has been drawn on the bars. The seeds the parent names for
  Appendix A stay Appendix A's (D-50).
- **Confirmation.** None: nothing is carried; NQ from 2026-07-17 is never read.

## 9. Open before the pin

1. **The red team's read** of this draft and its three siblings.
2. **The id and the name** (0.2), and the narrowed glob of `tests/test_pp_draft.py` in the pinning commit.
3. **G-2's feasibility** is a build question; its stop-and-report clause is declared now.
4. **The pinning row** records the parent as superseded, never run (0.3), and Appendix A as unrun and not incorporated
   (D-50).
