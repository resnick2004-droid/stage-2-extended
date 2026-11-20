# Red team: the four O-7 search-years deltas (RD-01S, RD-02S, RD-03S, RD-05FS) and RD-04

**Reviewer:** wt-scout (red team), 2026-11-19. **Read cold:** the four drafts as staged, uncommitted, in
`%LOCALAPPDATA%\stage2-extended-wt\wt-firms` (`prereg/DRAFT_RD-01S_firm_contracts_search_years.md`,
`prereg/DRAFT_RD-02S_payout_policy_search_years.md`, `prereg/DRAFT_RD-03S_contract_levers_search_years.md`,
`prereg/DRAFT_RD-05FS_firm_modes_part_f_search_years.md`) and their test `tests/test_rd_search_years_drafts.py`.
Also read: their parents (RD-01, RD-02, RD-03, RD-05 at their pinned shas), RD-04, E-208, E-221 (O-1, O-7), E-231,
CHARTER 3.3 (a) and 3.6, `extended/reader.py`, and the vendored builders the drafts cut (`user_journey.build_p16` and
`build_d518`, `rc_width_screen.build`, `resolved_coin`, `atlas_a3`, `a3_brk30`, `a3_resolution_map.load_a1`,
`t24_gf15.eras`, `customer_slices.arm_blocks`). The brief's hints (its attack list and the lead's provisional view on
RD-04) were read and set aside; every point below stands on the files.

## Verdict: **must be re-drafted** (all four; none is pinnable as written)

Two defects change declared rules, and both sit in the general replacements the four drafts share (G-3, G-4, G-7):

- the verdict arm is re-estimated on the search years (G-4), yet the drafts keep **refusing comparisons of verdict-arm
  rows with whole-window files** (U1's and Q-44's per-start rows) and **cite whole-window verdict-arm rows** beside the
  search-year rows. So the run can never pass its own checks, and the cited rows carry exactly the held-out read that G-4
  removes;
- the **cut identity G-3 (b)** reads the held-out years under the purpose `identity`. Its pass or fail depends on the
  held-out bars, through P-16's whole-window mark cutoff, and it decides whether the reading runs. Its premise, that
  "the registered builders are causal at the cut", is false for P-16.

Per draft: **RD-01S must be re-drafted; RD-02S must be re-drafted; RD-03S must be re-drafted; RD-05FS must be
re-drafted** (it shares both defects and adds a pin-order defect). The remedies are shared and small (below). **RD-04
must be re-declared on the search years by the same rule**, and it also has a route to the held-out years that the
reader's rule 4 does not close (finding M-3).

Counts: **2 blocking** (B-1, B-2); **3 material, not blocking** (M-1 to M-3); **9 minor** (m-1 to m-9); **4 notes**.

---

## Blocking

### B-1 (MATERIAL; blocking, all four). Verdict-arm rows are compared with, and cited from, whole-window files after G-4 re-estimates the arm's constants

**Where.** RD-01S:99-106 (G-4) against RD-01S:125-130 (G-7), D-29 (RD-01S:201), D-51 (RD-01S:223) and G-3 (b)
(RD-01S:92-94). RD-02S:101-108 (G-4) against G-7 (RD-02S:128-135), D-30, D-31 and D-37 (RD-02S:206, 207, 213). RD-03S:101-108
against G-7 (RD-03S:128-136) and D-34 (RD-03S:222). RD-05FS:107-114 against G-7 (RD-05FS:134-140), D-30 and D-44
(RD-05FS:214, 228). The parents' lines these rows keep:
- RD-01 L823-L825: 9.1 item 1, U1's start rows, "both arms, every start, every column";
- RD-02 L595-L596: 8.1 item 6, the `ref` cell under the ladder, "verdict arm, equals Q-44's `results/user_beside_starts.csv`";
- RD-03 L837-L838: the same as RD-02's 8.1 item 6;
- RD-05 L988-L990: `TS-16`'s "three checks against Q-44's per-start rows", verdict arm.

**Evidence.** U1 builds each arm's day blocks as `customer_slices.arm_blocks(camp, "verdict")`, which is
`shifted_blocks(blocks, lb - e, {R: lb_by_rr[R] - e_by_rr[R]})` (`vendor/stage2/scripts/customer_slices.py:182-195`).
The constants come from `atlas_a3.bounds(t, days, ...)` over whatever trades and days the builder is given
(`user_journey._rc_campaign`, `user_journey.py:302-316`). U1's file and Q-44's `results/user_beside_starts.csv` hold
`verdict` rows for p14 and p16 on every start from 2020-01-02 to 2026-07-16 (inspected: its columns and its
design/arm/response/date keys). Those rows were computed with constants estimated over the whole window. G-4 replaces
them with constants estimated on the search years. G-7 and the rows above then compare the reading's verdict rows
with the file's on search-year starts, "every column ... refusing". G-3 (b) compares "the stream" (U1's jobs hold both
arms' blocks) "every field of every day block, the per-R outcomes included".

**What fails.**
1. *The run cannot pass its own checks.* On the first search-year start (P-14, 2020-01-02, verdict arm, response
   `off`), every trade at an offered R is shifted by the search-year `lb_by_rr[R] - e_by_rr[R]` instead of the
   whole-window one. So `net_month_1` differs from U1's and Q-44's row, the refusing comparison fails, and the run
   stops. The same holds for G-3 (b) read on both arms. This failure is certain, not a matter of chance.
2. *The cited rows are functions of the held-out years.* RD-01S D-51 cites TS's placement and Focused Trader rows "from
   Q-44's per-start rows ... on the starts whose 252-session replay ends inside the search years". RD-02S D-37 cites
   the bases' readings from Q-44's file. RD-03S G-7 reads the bases' `naf` rows under the Focused Trader models from
   Q-44, and RD-05FS reads `TS-N` from those rows (its D-08). On a search-year start, Q-44's verdict row is a function
   of 2024-2026 through the whole-window constant: the parents' N2 leak. Restricting the starts does not remove it.
   So the drafts' claim "no reading is a function of the held-out years" (RD-01S D-18, RD-02S D-13, RD-03S D-12,
   RD-05FS D-14) is false for every such citation, and those rows sit in the menu that CHARTER 3.3 (a) lets bound a
   lever range.
3. RD-02 L531 is not cited and is governed only by G-7's general words. It cites Q-44's *aggregate* file
   `results/user_beside.csv` "beside by file". Those rows pool every start from 2020 to 2026, so a held-out read
   enters directly, not through the constant. G-7's "cited on the same starts only" can be met only by recomputing from
   the per-start file, and the draft does not say that.

**Remedy (one paragraph in G-7 of each draft, plus G-3 (b)).**
- Every in-run comparison with U1's or Q-44's rows, and G-3 (b), is made on the **point arm only**, and the draft says
  so. The point arm carries no constant.
- The verdict arm's own correctness is held by G-3 (c) together with the point-arm equality (the shift is
  `shifted_blocks` of the point blocks, which r6's `delta_problems` already checks per stream).
- Every row cited from Q-44 (ladder, placement, Focused Trader, the bases' readings) is cited on the point arm, or is
  re-run on the cut at the search-year constants. A whole-window verdict row is never cited.
- Aggregates are recomputed from the per-start rows on the search-year starts; `results/user_beside.csv` is never
  cited.

### B-2 (MATERIAL; blocking, all four). The cut identity G-3 (b) reads the held-out years, its outcome depends on them, it decides whether the reading runs, and its premise is false for P-16

**Where.** RD-01S:90-98 ("the registered builders are causal at the cut, so the search-year stream is the registered
design's", lines 93-94; "A failure of (b) stops the reading", line 98), RD-02S:93-100, RD-03S:92-100, RD-05FS:100-106.

**Evidence.**
- P-16's stream is built by `rc150_dev_test.build_cells`, which calls `rc_width_screen.build`
  (`vendor/stage2/scripts/rc_width_screen.py:103-154`). That walks every mark on every day it is given and admits a
  mark only if its unresolved share, `resolved_coin.mark_resolution`, is at most 5 % **pooled over every day passed
  in**. The docstring says so: "at every R the table offers, over the whole window" (`resolved_coin.py:241-261`). The
  admitted marks then decide which trades exist on every day (`offered_marks`, `window_marks`, `cell_trades`).
- On the cut (G-2), the shares are pooled over 2020-2023 only, so the offered marks are the search years' own. They
  equal the registered set only if no mark's share crosses 5 % between the two pools.
- A synthetic check (scratch `wt-scout_o7\synthetic_cut.py`, no bar read) builds a mark unresolved 4 % before a cut
  and 8 % after it. `mark_resolution` admits it on the cut and refuses it on the whole span. Every trade at that mark,
  on every search-year day, then differs.
- So G-3 (b) for P-16 tests whether the search years and the whole window resolve the same marks. That is a statistic
  of the held-out bars.
- P-14 is different: its rung map is a pinned results file (`atlas_a3.rung_rule`, `atlas_a3.py:126-136`), constant
  under the cut. It most likely passes (b) on the point arm.

**Under what purpose, and is it allowed?**
- **The reader allows it.** G-3's script reads the whole window under `identity`. `reader.authorise` returns for
  `identity` before any held-out rule is consulted (`extended/reader.py:833-838`). It needs only a script under
  `identity/` and a decision row that mentions "identit" (`_identity`, reader.py:479-493). Outside a clean run the read
  is not even ledgered, and nothing limits how often it runs or what it writes.
- **CHARTER 3.6 (a) does not allow it.** "Held out" means unread by the search's code *and unused by any choice in its
  declaration*. G-3 (b) is a precondition the declaration itself sets, and its result chooses between "run" and "stop;
  a new declaration would be needed" (G-2, RD-01S:86-88). The next declaration would then be written knowing that the
  held-out years moved P-16's marks.
- **The lead has already ruled on the nearest case.** E-231 (1) moved even a held-out *data-integrity* check into the
  joint test's `Judged-block reads:` line rather than let it run before. A check whose verdict is a function of the
  held-out bars belongs in the same place.
- **The other parts are of another kind.** G-3 (a) and (c), and RD-03S's (d), reproduce numbers already in Stage 2's
  registered files, whose expected outcome is fixed. They are E-004's kind, and the parents' identities do the same
  today. RD-02S:98 nonetheless calls the whole of G-3 "an identity of Stage 2's engine against Stage 2's files", which
  (b) is not: it compares two fresh builds.

**What fails.**
- *(i)* If any P-16 mark sits near 5 % with a different share after 2023, G-3 (b) fails and the reading stops on a
  held-out fact.
- *(ii)* If none does, the stream passes. But the draft has then made a run/no-run decision from the held-out bars,
  and its declared fallback ("a new declaration") is shaped by that.
- *(iii)* Either way, the T-3S planned in B-8 (synthetic campaigns, RD-01S:293-296) cannot catch this channel, because
  synthetic campaigns bypass the vendored builders.

**Remedy (choose before the pin; both read no held-out day).**
1. **Fix P-16's offered marks** to the registered set as an inherited constant (it is already G-11's entry "P-16's mark
   cutoff resolved on the whole window", the same standing as P-14's pinned rung map). Pass it into the cut build by
   wrapping `resolved_coin.offered_marks` or `mark_resolution` for the call (nothing vendored edited).
   *Or* declare the cutoff re-resolved on the search years (a search-year P-16). The latter is not the registered
   design: the point-arm comparisons of B-1 then fail and must be dropped, and every row must be labelled so.
2. **Replace G-3 (b) with checks that read no held-out day:**
   - a **nested cut inside the search years**: build on 2020-01-02 to 2022-12-30 and on 2020-01-02 to 2023-12-29, and
     require point-arm day blocks equal up to 2022-12-30 (with option 1's marks fixed this must hold if the build is
     causal, and it tests the wrapper);
   - G-7's **point-arm** equality with U1's and Q-44's rows on the starts whose 252-session replay ends inside the
     search years. That already shows the cut stream is the registered one on those starts.

   Keep G-3 (a) and (c) as reproduction identities. Ask the lead to rule, under E-231 (1), whether reproduction
   identities that read the held-out years may still run before the joint test (finding N-3).

---

## Material, not blocking

### M-1 (MATERIAL). The re-estimated verdict constants inherit an era rule that is degenerate on the search years; the drafts do not say so

**Where.** G-4 in each draft (RD-01S:99-106 and its siblings): "the vendored estimator's (the one the registered
builder calls, at the registered trial count)".

**Evidence.**
- That estimator is `atlas_a3.bounds` (`atlas_a3.py:323-349`): each R's bound is the pooled one, or "the lower era's
  when the whole-year bootstrap flags the eras". The eras are P-11's `((2020, 2022), (2023, 2026))` (`a3_brk30.py:81`,
  checked against the config).
- On the cut, era 2 is **2023 alone**. `t24_gf15.eras` resamples whole years within each era (`t24_gf15.py:121-128`),
  so with one year in era 2 its bootstrap mean never varies. The synthetic check shows 2000 draws giving one distinct
  era-2 mean.
- So the flag fires whenever 2023's mean lies outside the bootstrap spread of three years. When it fires, the bound
  read is the lower era's, which may be 2023's one-year bound over about a dozen 21-session blocks.
- The headline (the verdict arm) then turns on one year, by a rule nobody chose for four years.

**What fails.** The menu's headline differs materially from both a pooled-bound and a two-era reading, without a word
in "what it does to what the reading can show". Once seen, the temptation is to "fix" the era rule, which would be a
choice made after the outcome.

**Remedy (a reading, no rule change if the first option is taken).** State in G-4 and in section 1, before the pin:
- the era spans on the cut (P-11's spans as configured, era 2 = 2023 alone, its bootstrap degenerate);
- that the flag and the bound read are printed in every manifest;
- that the pooled bound is printed beside.

If the lead prefers a different rule (pooled only, or spans 2020-2021 / 2022-2023), it is chosen now, in the text,
before any read.

### M-2 (MATERIAL). Missed window-dependent lines and an incomplete held-out read ledger (G-11)

**Evidence.** Re-running the drafter's search with terms the drafter did not use (`bound|lb|e_by_rr`, `shift`, `U1`,
`Q-44`, `Q-17`, `results/|.csv`, `era`, `capacity|busiest`, `cutoff|mark|rung`, `registered`, `window`, `estimat|fit`,
`volatil|regime`, dates `20\d\d-\d\d-\d\d`, and others; scratch `wt-scout_o7\extra_terms.py`) leaves these lines
neither cited nor listed as unaffected:

- **RD-01 L664-L665** (A-11: a liquidated trade "takes the same per-R shift to its R's registered bound"), **L806**
  (arms), **RD-02 L323, L487**, **RD-03 L532, L772**: "registered bound", which under G-4 is no longer the registered
  one. G-4 governs these lines, but they should be cited so that no builder loads `lb_by_rr` from a registered gate
  file for A-11's liquidation.
- **RD-02 L531**: B-1 item 3.
- **RD-03 L166, L328** and **RD-05 L304**: the motivation of Back2Funded and of part F's evaluation rows rests on Stage
  2 D-652 (U2, `u_xfa_day_budget.csv`, whole-window gate paths) and E-125 (Q-18's `results/p14_validation.csv`,
  whole-window, under `registered_design`). Neither is in RD-03S's or RD-05FS's G-11. CHARTER 3.6 (b) says "each
  declaration completes it", and a lever chosen to be studied after a whole-window read is exactly what the ledger
  must carry.

**Remedy.** Cite the lines above in section 3, and add D-652 (U2) and E-125/Q-18 to G-11 in RD-03S and RD-05FS.

### M-3 (MATERIAL; the brief's RD-04 question). RD-04 must be re-declared on the search years by the same rule, and it has a held-out route that rule 4 does not close

**Evidence.**
- RD-04 declares `volatility_descriptive` (its (a2), whole window, RD-04 L536-L544). That is an RD purpose, so the
  reader's rule 4 refuses it until NQ's verdict row exists (reader.py:742-753).
- But RD-04 (c), the calm-regime replay including the late block (RD-04 L527-L533), authorises its engine reads under
  **`registered_design`** (RD-04 L545-L560). For that purpose the reader applies **rule 3, not rule 4**
  (reader.py:839-845): a lead's row carrying `heldout-read: P-14,P-16 by scripts/rd04_replay.py -- ...` admits it at
  any time, **with no verdict needed**.
- (c)'s factors are per-year medians from (a2)'s rows (RD-04 section 4.2; "the factor of a start's later sessions is
  their own year's", L531-L533), so its outputs for 2024-2026 are functions of the held-out years.
- CHARTER 3.3 (a) names RD-04 as the source of the volatility drift that lever units must respect, and forbids any
  volatility unit or regime threshold that reads the held-out years.

**What fails.** A heldout-read row for `scripts/rd04_replay.py`, written in good faith to "run RD-04", admits a
held-out replay of P-14 and P-16 before the joint test. Its year factors or late-block rows could then reach a
volatility unit, a regime threshold or a lever range (CHARTER 3.6 (a)). Nothing in the reader stops it.

**Remedy.** Re-declare RD-04 on the search years by O-7's rule:
- (a2)'s search-year half exists already as Q-121 (E-177);
- (c) on the search years, its reference years (2020-2021) unchanged, its factors from search-year years only, and its
  blocks G-6's halves.

Until then, the pinning row of the O-7 deltas should record that no `heldout-read` row is written for
`scripts/rd04_replay.py` (or any RD runner) before NQ's verdict row. CHARTER 3.6 (b)'s entry "RD-04 (c): P-14 and P-16
replayed on the late block" should read "declared, not run". A held-out (a2) after the verdict remains a description
under 3.6 (c), as rule 4 already allows.

---

## Minor

- **m-1 (all four). The deltas' replacement labels G-1 to G-15 (and G-16) collide with the parents' own gap labels.**
  RD-01 4.7 defines G-1 to G-14 (L387-L400), RD-03 4.4 defines G-1 to G-9, and RD-05 4.4 defines G-1 to G-10. Each
  delta incorporates its parent's text, so one declaration then holds two meanings of each label.
  - Concrete case: RD-01's gap **G-3** is TradeDay's tier-1 auto-liquidation (L389), while RD-01S's **G-3** is the cut
    identity. RD-05 L489 refers to "RD-01 G-3's bracket", which RD-09 now reads through RD-06.
  - RD-01S's D-13 already writes "4.7, G-11" (the gap) beside its own G-11 (the ledger).

  Remedy: rename the replacements (for example S-1 to S-16) before the pin.
- **m-2 (RD-05FS, RD-01S, RD-03S). Pin order and cross-references by draft path.**
  - RD-05FS D-07 and D-08 (RD-05FS:191-192) and G-2 (RD-05FS:94) cite `prereg/DRAFT_RD-01S_...` and
    `prereg/DRAFT_RD-03S_...`.
  - RD-01S:343-349 and RD-03S:57 cite `DRAFT_RD-05FS_...`. RD-01S:345-346 says that at the pin "nothing else changes"
    but the id and name.
  - After renaming, these paths dangle; and a text cannot carry the sha256 of a text that carries its own.

  Remedy:
  - RD-09 cites RD-06 and RD-08 by **pinned path and sha256** (RD-06 and RD-08 pinned first, or earlier in the same
    row, with their shas computed before RD-09's text is fixed).
  - RD-06 and RD-08 cite RD-09 by id only, or not at all; the cross-link goes in the pinning row.
  - Section 9 item 2 is amended to allow these path edits.
- **m-3 (all four). B-2's wrapper is under-specified.** The builders do not read through one "bar and atlas reader":
  - P-16's walk reads bars with `propedge.data.bars.read_bars` (`atlas_a3.bar_arrays`);
  - A1's events and days come from `pd.read_parquet` in `a3_resolution_map.load_a1`, and A3's walks from
    `pd.read_parquet` in `atlas_a3.cached_walk`;
  - `load_a1` refuses unless the bars manifest's day count and last day match the A1 cache's manifest
    (`a3_resolution_map.py:201-212`), so the manifest's `day_list` **must not** be cut while the parquet rows must be;
  - the builders' refusing identity rows (`rc_dev_test.trade_problems`, the content hash) must be suppressed on the
    cut, and the draft does not list which.

  The runner's refusal of any block or date after 2023-12-29 is the real backstop (`gf.gate_blocks` makes a block for
  every day, so an uncut day list is caught). Remedy: B-2 names the four inputs, the cut for each, and the exact list of
  vendored checks suppressed; nothing else may be suppressed.
- **m-4 (all four). G-2's `authorise_engine_read` on the choice block is a no-op guard.** With no purpose it checks only
  the dates and writes nothing (reader.py:821-826, 1101-1121), and the reader cannot see reads inside vendored calls
  (reader.py:111-114). Say plainly that the wrapper and the refusal are the guard.
- **m-5 (RD-02S D-19, RD-02S:195; the siblings' G-6). "No first-half reading touches a second-half session" is false
  on the verdict arm.** The G-4 constants are estimated on both halves. The parents disclosed the same thing as N2.
  Remedy: label it the same way, or read the stability flag on the point arm. T-3S as written holds the constant fixed
  (RD-02S D-48), so it cannot see this.
- **m-6 (RD-05FS:63-70, 0.3). A delta governs its parent's output.** RD-05FS says RD-05's (pinned) menu file prints a
  placeholder line for part F. A pinned declaration's behaviour is changed by another's text. Remedy: move this to the
  pinning row (section 9 item 3 already half-says so), and keep RD-09's text about RD-09.
- **m-7 (the test). Checks that cannot fail, or cannot fail where it matters.**
  1. `NEVER_READ` (test:95) includes `held.out`, so any line saying "held-out" exempts every date on it. "reads the
     held-out years 2024-01-02 to 2026-07-16 as its late block" passes. The planted case in
     `test_the_checks_are_not_vacuous` (test:327) avoids the word, so it does not probe this. Remedy: drop `held.out`
     from `NEVER_READ`, require "never read|not read|unread", and plant a "held-out ... read" line.
  2. `test_the_checks_are_not_vacuous` re-implements the date and quote logic inline instead of calling the tested
     functions, so a change to the real check is not caught.
  3. `test_no_result_number_is_typed` checks decimals, percentages and dollars, not integers.
  4. `test_the_proposed_pinned_name_reads_as_its_own_id` asserts the pinned file does not exist, so it fails at the pin
     by design and must be changed in the pinning commit (say so in section 9).
  5. `test_the_parent_never_ran` cannot see choice-block runs or identity runs outside a clean run (neither is
     ledgered).
  6. The "unaffected, because" list exempts lines on the drafter's word. The test cannot judge a reason, which is why
     M-2's lines passed.
- **m-8 (RD-03S:170-180, G-16).** "the registered policy, the state-policy configuration and the table files are
  unchanged (design constants, no data)". The v12 state table's model offers each R "on its availability share of
  days" (`vendor/stage2/config/state_policy_v10.yaml:31`, D-318), an empirical share from the development window. It
  is G-11's entry, but "no data" is not accurate. Say "registered, inherited, G-11".
- **m-9 (RD-01S:42-46 and siblings' 0.2).** The stated reason for new numbers ("a `repeat=` row naming the parent
  would authorise a rerun of this file") is moot: these files make no judged read, so `repeat=` never applies to them.
  The numbering is right for other reasons (the reader's `DECLARATION_ID` would attribute `RD-01S_...` to RD-01 in any
  ledger or manifest; the parents' T-0 globs). State those.

## Notes

- **N-1. Supersession (the brief's ids question; the drafter's R-8 point).** The new ids work:
  - `DECLARATION_ID` reads RD-06 to RD-09;
  - `_family_ref("RD-01")` globs `prereg/RD-01_*.md`, which finds only the parent;
  - RD-06 does not match RD-01's T-0 glob `RD-*_firm_contracts.md`, and RD-07 matches `RD-*payout*.md`, which RD-02S
    0.2 already flags for narrowing;
  - with the drafts present, the parents' T-0s and `test_declarations_fixed.py` pass (60 passed).

  But the parents' `Judged-block reads:` lines stay live after **any** NQ verdict row (rule 4 lifts). The supersession
  is enforced only by B-1's runner constants, and today's `scripts/rd01_reading.py` still authorises RD-01's purposes.
  Before the verdict, rule 4 closes the parents' RD purposes. The `registered_design` route (M-3) and the `identity`
  door (N-2) are not closed by any id.

  Remedy, cheap:
  - a test now, failing if any file under `extended/`, `scripts/` or `identity/` names a superseded parent's path, its
    purposes, or `prereg_id` RD-01/02/03 (or RD-05 for steps 3 to 5);
  - until R-8, a `SUPERSEDED` tuple in the reader refusing judged reads that cite those parents, unless a later row
    reopens them.
- **N-2. The `identity` door is wide.** Any `identity/*.py`, any decision row mentioning "identit", any number of runs,
  no ledger outside a clean run, and no check on what the script writes. G-3's "writes pass or fail lines and nothing
  of any cell" is a promise only. Remedy: a test that G-3's script calls no `write_result` and writes only its pass or
  fail file. (For scale: at the time of this read, `run.lock` shows RD-03's `cl_identity` running whole-window under
  E-205.)
- **N-3. The ruling owed.** After E-231 (1), the lead should state whether *reproduction* identities that read the
  held-out years (the parents' 9.1 / 8.1 / 13.1 items, G-3 (a), (c) and RD-03S's (d)) may run before the joint test.
  They are E-004's kind and tolerable, but no row says so under E-208.
- **N-4. The halves (G-6) are not chosen after the fact in a way that can change a decision, and they are a fair,
  weak stability check.**
  - The split at 2022 is the natural midpoint at a year's end. It was fixed before any run of these readings, and the
    alternatives considered are named.
  - It confounds time with regime (2022's drawdown in the second half), as the parent's early/late split did; that is
    what such a flag is for.
  - At 12 months each half reduces to roughly one start year (2020 against 2022), so the sign comparison at long
    horizons is close to a comparison of two years. It fires by noise about as easily as by signal.
  - Keep it, labelled. The start-year rows (G-5) beside are the better description.

## What I tried that found nothing

- **Held-out dates in the drafts' own text:** none outside never-read statements (the test, plus my scan with the
  `held.out` exemption removed); every `development data` row reads 2020-01-02 to 2023-12-29.
- **No judged-block line and no purpose** in any draft (reader's `DECLARED_LINE`).
- **Typed figures and seeds:** no stray decimal, percentage, dollar figure or eight-digit seed. The restated counts
  match the parents (RD-01: 30/34 replays, 27 ladder, 16 gates; RD-02: 11 runs, 32 beside; RD-05: 52 steady, 39
  ladder, 13 gates, 4 Q-44 checks). Seed blocks are inherited by reference, and the parents' seed scans pass.
- **The parents never ran:** the read ledger holds only `identity` and `registered_design` lines, and no `fc_*`,
  `pp_*`, `cl_*` or `modes_*` result exists.
- **The coin table under the cut:** `resolved_coin.coin_table` draws `default_rng(seed).random(n)` over sorted dates,
  which is prefix-stable. The synthetic check confirms the coin side of every search-year mark is unchanged by the cut.
- **Capacity** (`a3_brk30.capacity`, the busiest day): it enters the engine's arguments, not the day blocks. On the cut
  it is the search years' busiest day, which no search-year day exceeds, so it binds nowhere. No leak was found.
- **P-14's rung map and the state table:** pinned result files, inherited (G-11). They do not move under the cut.
- **Calendars** (release, FOMC, early closes): fixed in advance, publication schedules, used on search-year days only.
- **Q-121's rows** are search-year only (E-177); RD-04 has not run; no draft reads either.
- **G-5's `u_select.block(records, None, h)`** keeps `observed >= h`, so on the cut replay it gives exactly the
  starts with h sessions inside the search years.
- **G-8's pairing:** gate day draws are a function of seed and pool size (RD-04 L518-L522), so the corners and the
  references' search-year gates pair.
- **RD-02S D-34:** E-029's voided days are 2020-07-01, 2025-06-30 and 2025-07-01, so only 2020-07-01 is in the search
  years. The claim is true.

## What I could not check

- **Whether P-16's offered marks actually move between the search years and the whole window.** Settling it needs the
  cut build of P-16's walk (heavy: a full walk of P-16's marks over 2020-2023 through the engine, one worker, the cut
  wrapper of m-3). Under B-2's first remedy the question becomes moot, so no run is recommended.
- **Whether the era flag fires on the search years** for P-14 or P-16 (the same cut build, plus `atlas_a3.bounds`).
- **The wrapper's feasibility** (a build question; the drafts' stop-and-report clause stands).
- **RD-05's coin side** (parts A to E) was not reviewed. It is outside O-7's re-declaration.
- **Disclosure:** inspecting `results/user_beside_starts.csv`'s columns printed its first data row (P-14, verdict,
  `off`, start 2020-01-02, a search-year start). No other value of that file, and no bar, was read. Nothing from
  2026-07-17 was read.
