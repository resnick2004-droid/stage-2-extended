# Red-team full read: the design-search template, text v2 (wt/wt-lit 68436c9), with its agents, skills and commands

**Reviewer:** red team, 2026-11-20. **Target:** `wt/wt-lit` at 68436c9, eleven files, read with `git show 68436c9:<path>`
(nothing written in that tree). "T l.N" is `prereg/TEMPLATE_design_search.md` at 68436c9; "GK l.N" is
`.claude/agents/prereg-gatekeeper.md`; "TT l.N" is `tests/test_design_search_template.py`. The first text is 1a9be8c.

**What I checked against.** CHARTER sections 2-3 (master); E-207, E-221, E-222, E-230, E-237, E-238, E-247, E-251;
`extended/reader.py` on master (Q-158, rules 1 and 2); the runner that stood (Wave 3.2 cycle 2, the staged index of
`wt-three` on 427a21f, read with `git show :<path>`, and its read `BUILD_W32_v3_2026-11-20.md`); the vendored engine's
sizing and lockstep (`vendor/stage2/propedge/campaign/sizing.py`, `lockstep.py`), read only.

**The brief's framing.** The brief summarised B-1 to B-4 and described the two proposals. I read the findings and the
proposals in their source texts and judged them against the files. I did not take the summaries as the answer.

**Scratch.** A data-free copy of the target (`scratchpad\tv2`, made with `git archive`; two empty placeholder files
stand in for `results/q82_judged_sessions.csv` and `vendor/stage2/config/rules.yaml`, which one test only checks for
existence). The probes are `scratchpad\probes_v2\mutate.py` and `zero_micro.py`. Everything ran with `OMP_NUM_THREADS=1`
and well under 500 MB. I read no bar, atlas or result file, and nothing from 2026-07-17 on. The one ledger I opened,
`results/read_ledger.jsonl`, I read for its declaration fields only.

---

## Verdict: **must be re-declared**

**B-1 to B-4 are answered in the text:**
- R-10 is fractional with a two-point last sub-step.
- No "not taken" state is left at a fill.
- A search carries no `Judged-block reads:` line, and F-HT's token is written.
- CHARTER 3.5's no-harm floor is in sections 4 and 10 (c), with "not carried".

**Two defects change a declared rule:**
- **C-1.** B-2's guarantee ("no account is ever left alive, billed and unable to trade", T l.264) holds only at a fill.
  A trade that the lever space's own room cut sizes to **zero contracts** never reaches a fill. On a synthetic toy that
  account is left alive, billed and never failed in about a fifth of all account lives. Stage 2's engine ends such an
  account (D-318, D-335); the template has no rule for it.
- **M-1.** The held-out test's declaration, the one file that reads NQ's held-out years and spends k = 13, has no form.
  It is written after every search-year result, and the order across the firms is free until the read.

**Two further defects would make a template-drafted declaration fail or diverge at run time.** These are a declared
lattice step that the runner refuses on NQ (M-3), and the walk's floor-side law, which differs from the runner's
(m-1, latent). The tests hold the words, not the rules: 24 of 30 one-phrase mutants survive, including a swap of the
B-2 clause that brings the stranded account back (M-4).

**The two proposals:**
- **The CHARTER 3.7 reading row** is a tightening and is sound. It needs three additions, chiefly that a successor
  after a failed gate cannot re-set the lead's limits by a rule written after H4 was read (M-5).
- **The sizing experiment** cannot see C-1's route as specified, and its count is not zero under the rule by
  construction (m-8). A corrected specification is under m-8.

| id | label | one line |
|---|---|---|
| C-1 | **CHANGES-A-CONCLUSION** | T l.210-213, l.259-266: B-2 acts only "at a fill". S3's room cut to whole micros (the lever table l.70, Stage 2 D-313) gives zero contracts at a positive room, so there is no fill. The account is alive, billed and never failed. Toy (`zero_micro.py`): 21.5 % of accounts end that way against 59.3 % breached. Stage 2 ends it as out of room (D-318, D-335). |
| M-1 | **MATERIAL** | The held-out test's declaration (T l.68-78, l.482-485, l.571-578) has no template, no gatekeeper item list and no rule restricting it to the searches' pinned inputs. The order across firms is set "before the held-out read" (T l.484), after every search-year result, by a researcher who has read 2024-2026. Nothing says what happens if a firm's search closes without finalists. |
| M-2 | **MATERIAL** | B-3's guard is textual. Reader rule 1 binds only `heldout_test` and `heldout_stress` (`reader.py` l.850). A search whose line names any other non-choice purpose reads NQ's held-out years with no finalists' token, and by rule 2 it then locks out the joint test. No test checks drafts or pinned files. The gatekeeper's refusal is untested (mutants J2, J3 survive). |
| M-3 | **MATERIAL** | T l.272: "s is one tick" unless a fixed value. At s = 1 tick, n = sigma² T / s² exceeds the runner's `WALK_MAX` = 1024 for any sigma above 32/√T ticks per root-minute (1.85 at T = 300 min), and the runner refuses such a trade (staged `three_way_journey.py` l.106-107). A fixed s must divide every l and g (l.99-101), which imposes a bracket grid nobody declares. The runner's own fix, a per-trade s from v and T (`three_way_s1.walk_step_for`), is what T l.272 and GK l.110-111 forbid. |
| M-4 | **MATERIAL** | 24 of 30 one-phrase mutants survive TT. Among them: the B-2 clause with floor and daily-limit swapped (the stranded state returns), the gatekeeper keeping a floor-bound account alive, the no-harm floor read on the held-out years, a failed power gate proceeding, rounds extended, the embargo dropped, `<S4>` reusing `<S1>`, the joint order set after the held-out read, and typed figures (0.42, 37 %, 1250 USD). |
| M-5 | **MATERIAL (the proposal)** | The CHARTER 3.7 reading row is sound and stricter than the literal order. It must also: (a) cover 3.8 (a)'s "a pinning row ... does not pin" and 3.7's "before any search is pinned"; (b) name the reader's "pin" (the hash row) apart from CHARTER's "search's pin" (the go row); (c) bar a successor after a failed gate from re-setting the limits, budgets, weights or size that matters by a rule written after H4 was read (CHARTER 3.9). |
| m-1 | MINOR (latent) | The walk's floor-side law differs from the runner's. The template uses L_fill, with its barrier loss at x_stop, so the account is left x_flat - x_stop above the floor, and T l.295's "a floor-side loss ends exactly on the floor" is false (TT l.626 asserts it with the wrong cost). The runner uses L_race, with the flatten cost clipped at -room, so the clip binds (staged l.258-263, l.421-423). Both are identical while x_flat = x_stop, which holds in every vendored profile. |
| m-2 | MINOR | The walk's case where one lattice point is the last above the floor-side barrier and the last below the target is unstated. T l.291-293 gives each side its own rule, and the two conflict there. The runner uses rho_d / (rho_u + rho_d). It is reachable with a profit-level g' under one step. |
| m-3 | MINOR | A daily loss limit at or below e + max x (at the stress) ends every day at the first offer, so the account never trades and never fails, against T l.264. The runner refuses this at construction (n-2, staged l.600-608); the template has no such refusal. |
| m-4 | MINOR | T l.430, "The power gate, before the pin", contradicts T l.407-408 and step 3 (after the pin, before the go row). |
| m-5 | MINOR | The no-harm floor's comparison form is open (T l.376's "its direction or form" is left to the draft). A drafter may write "not significantly below" (mutant N3 survives). Under O-5's principle, state the point estimate over `<S1>`'s seeds on the same fills. |
| m-6 | MINOR | Copies: `contract-engine` l.135 and `feature-rules` use L_fill without defining it and omit the daily-limit clause. The auditor's item 6 (l.105-107) and item 4 (l.92) keep the single-search wording ("the search's finalists' row and its held-out row", "the pinned order"), not F-HT and the joint order. The auditor's (c) does not name the playbook floor's "not carried" check on the finalists' list. |
| m-7 | MINOR | A finalist's power at its place in the joint sequence is conditional on every earlier finalist passing. Exit (B)'s power (T l.437-438, l.614) is the per-search gate's, so it should be re-stated at the joint order in F-HT. |
| m-8 | MINOR (the proposal) | The sizing experiment (T l.267-271) runs `_trade_mc`, whose `Trade` has fixed contracts, so it cannot show C-1. Its horizon count of rooms in (EPS, e + max x] is non-zero under the rule (accounts after their last trade). It has no stated use and no stated output form. A corrected specification is below. |
| n-1 | NOTE | The runner's open m-3 (the level's unit): the template's g' (T l.198) converts net dollars to gross ticks. The runner's `level` must receive g' in gross ticks; close it in the template's words. |
| n-2 | NOTE | Rule 2 and the once-rule read `results/read_ledger.jsonl` of the tree that authorises the read. A clean checkout's ledger lines must reach master before any later judged read. This is out of the template's scope and stated for the lead. |
| n-3 | NOTE | The scratch run: 38 passed once the two placeholder files existed. The first run's one failure was my scratch copy's missing `rules.yaml`, not a defect. |

Counts: 1 CHANGES-A-CONCLUSION, 5 MATERIAL, 8 MINOR, 3 NOTE.

---

## C-1 (CHANGES-A-CONCLUSION). An account sized to zero contracts is left alive and never fails

**Where.**
- **T l.210-213.** "What happens at the fill is decided at the fill ... There is no 'not taken' state: an account with
  L_fill <= 0 at a fill is failed there or stops its day."
- **T l.259-266.** The B-2 clauses, ending: "So no account is ever left alive, billed and unable to trade."
- **GK l.108-110.** The gatekeeper's refusal, "a draft that leaves an account alive, billed and unable to trade".
- **The lever space the template imports (T l.99-101).** `docs/plans/LEVER_TABLE_topstep50k.md`:
  - l.70, S3: "the step is one micro at the trade's own stop (whole micros) ... cut each trade by the room cap (D-313)";
  - l.71, S4: whole micros, likewise;
  - l.82, A1: the flip "cut to the room of `combine_mll`";
  - l.98, A17: sizing by distance to the floor, a searched state rule.

**Evidence.**
- **What Stage 2's room cap does.**
  - `vendor/stage2/propedge/campaign/sizing.py` l.783-790: n_room = floor(room / risk per contract).
  - Below one contract's risk, n_room = 0. Then `sized.unsized` returns "no trade" (l.820-822), so no fill happens.
- **Nothing changes the room afterwards, so the state is absorbing** whenever the room is below one contract at the
  stop's floor.
- **Stage 2 met this in production and added an end for it.** D-318 (Stage 2 DECISIONS l.337): "Combines that could
  never trade again and never fail ... residues of a few dollars above the floor". `lockstep.py` l.1685-1691 and
  l.1900-1909 (D-318, D-335) end a room-capped account whose room buys no trade as out of room, "a failed attempt, not
  a breach".
- **The template's rule cannot reach this account.** L_fill = min(l, c - max x), with c in ticks per contract, is
  undefined at zero contracts. No fill is offered, so the B-2 clause never fires.
- **How large (`probes_v2/zero_micro.py`; toy values typed in the script, seed 20261120, 200 000 accounts).**
  - The setup: a static floor, the template's costed race and B-2 rule, and a room cut to whole micros (stop 40 ticks,
    target 40, at most 20 micros).
  - The outcome:
    - 59.3 % breached;
    - 19.2 % passed;
    - 0 % failed at the fill;
    - **21.5 % alive with zero micros at a positive room** (median room 4.86, at most 19.92 toy dollars, under one
      micro's risk).
  - After a run of room-capped losses, the residue is almost always under one contract's risk. So most accounts that
    would have failed become stranded instead.
- **The probe I could not run.** The runner that stood cannot show this: its `Trade` carries fixed contracts (`tvn`),
  so `_trade_mc` never sizes to zero.

**The failure it allows.**
- **The inputs:** a declaration searching S3 (or S4, A1's flip or A17) under this template, with a runner built to the
  template.
- **The wrong outputs:**
  - (24)'s ruin chance and the share failing are understated by about a fifth of all account lives on the toy;
  - fees are overstated by the subscriptions of accounts that never end;
  - P_B is moved.
- **Why it binds the verdict:** the share moves with the sizing lever, so the search will find it, and a design and a
  baseline differ in exposure.

**Remedy (a new terminal state, so a declared rule changes).**
- **In section 5, beside B-2:** "A trade the sizing rule cuts to zero contracts because the floor's room carries no
  contract at its stop ends the account **out of room** at that slot. It is failed (Stage 2 D-318, D-335), counted
  apart with the failures at the fill, its share printed beside the verdict, and replaced as a failure."
- **Zero contracts from another cut** (D-272's stand-aside, the allowance): a no-trade slot. The declaration shows
  such a state is not absorbing, or the design is refused.
- **In section 3:** cite the rule at S3, S4, A1 and A17.
- **In GK item 5:** refuse a draft with a room cut and no out-of-room rule.
- **Tests:**
  - a boundary case: room = one contract's risk at the stop, minus epsilon, ends out of room; plus epsilon, it trades;
  - a needle for the clause.
- **Runner:** before any search reads S3, the runner implements it.

---

## M-1 (MATERIAL). The held-out test's declaration has no form, and its order across firms is free

**Where.**
- **T l.68-78, l.482-485, l.528-530, l.571-578, l.600-604.** The declaration "lists every firm's finalists ..., fixes
  the joint order, takes the k, and is the one family that reads NQ's held-out window". It is "written when every
  firm's search has finalists".
- **The gatekeeper.** Its description (GK l.3) and item list cover design searches, RD readings and registrations. It
  has no list for this declaration.

**Evidence.**
- **When it is written.** It is the only declaration that reads 2024-2026 and spends k = 13. It is written after every
  firm's search-year results exist.
- **What it may contain is unconstrained.** Nothing in the template, the gatekeeper or the tests restricts it to the
  searches' pinned inputs: statistic, J, m, seeds `<S4>`, limits, composite, baselines, floors. It could add a
  reading, change a baseline or re-order the readings, and no house form refuses it.
- **The order across firms.** CHARTER 3.7 asks only that it be "declared before the held-out read". Each firm's own
  order comes from a rule declared before its survey (T l.348-349). The interleaving across firms is a free choice,
  made after every search-year result, by a researcher whose ledger is not empty: Stage 2's whole-window reads of the
  baselines, RD-02's and RD-05's late-block reads.
- **Why the order matters.** A fixed sequence stops at the first failure, so the order decides which finalists are
  tested at all. An order informed by knowledge of 2024-2026 is not independent of the held-out data. That goes beyond
  "the level is nominal": it is a selection channel at the one test.
- **A deadlock.** Nothing says what happens if one firm's search closes with no finalists (a failed power gate, every
  design failing a gate, every finalist failing its no-harm floor). Then "held until each firm's search has finalists"
  either waits forever, or someone decides afterwards whether to wait or drop the firm.
- **The rows' order.** It is implied but not stated. Rule 1 (`reader.py` l.66-68, `_finalists`) needs F-HT's
  finalists' token in a row newer than F-HT's pin row, so pin and token in one row are refused.

**The failure it allows.**
- After seeing three firms' search-year frontiers, the lead puts first the firm whose finalist most resembles what
  Stage 2 saw work late in the window.
- Or F-HT's text adds a reading or relaxes a floor no search pinned.
- Either way, the one k is spent on a test whose design was set after a look.

**Remedy.**
- **A section, or a short companion template, for the held-out test's declaration.**
  - It contains only:
    - the joint list, by each search's hash and finalists' list sha256;
    - the order, **by a rule fixed now** (for example: firms in a fixed order written in the template, each firm's
      list in its own pinned order; or a rule on the searches' pinned search-year readings written before any survey);
    - the k;
    - the `Judged-block reads:` line;
    - the token.
  - Every other input is cited from the searches' pinned files. Anything new is refused.
  - A firm whose search closes without finalists enters with none, recorded by a row, and the test proceeds when
    every firm is either a finalists' row or a closing row.
- **The rows, in order:** F-HT's pin row, then its finalists' and held-out row, newer.
- **The gate:** a gatekeeper item list and a red-team read for it.
- **The test:** a needle for the order rule. Mutant O1 survives today.

---

## M-2 (MATERIAL). Only the gatekeeper's reading stops a lone search's held-out read

**Where.**
- **The template.** T l.585-590: "With no line in any search, no single search can read NQ's held-out years, even with
  its own finalists' token from step 7".
- **The reader.** `extended/reader.py` l.66-71 (rules 1 and 2) and l.850 (`if purpose in HELDOUT_PURPOSES:` -- rule 1
  only there).
- **The test.** TT l.181-199 checks the template's text only.

**Evidence.**
- **Rule 1 is narrow.** It applies only to `heldout_test` and `heldout_stress`.
- **Any other purpose gets through.** A pinned F- declaration whose own line names another non-choice purpose (for
  example `stage_C_judgement`, the reader's own example) passes `_family`, `_clean_run` and `_once`, and reads the
  judged block with no finalists' token.
- **That one read takes the market.** Rule 2 then refuses every other family's judged read of NQ's base window, F-HT
  included.
- **The reader cannot tell the two kinds of file apart.** A search declaration and the held-out test's declaration are
  both `F-NN` files.
- **So the claim rests on one thing:** no search file ever carries a line. Only GK item 1 refuses a search draft's line
  (GK l.64, l.68-69), and no test holds that refusal:
  - **J2**, "a search declaration may carry a `Judged-block reads:` line", survives;
  - **J3**, deleting the refusal bullet, survives.
- **An accidental line is enough.** A drafter's rewrap that puts "Judged-block reads:" at a line's start, followed by a
  backticked purpose, makes a line the reader honours (`DECLARED_LINE`).

**The failure it allows.**
- **A gatekeeper's miss**, or one rewrapped sentence in one firm's search.
- **That search reads NQ's held-out years alone**, against O-1.
- **Rule 2 then blocks the joint test**, unless a new window row is opened.

**Remedy (either one):**
- a test over every `prereg/F-*.md`: any file with a non-empty `declared_purposes` must be the held-out test's
  declaration, identified by a declared marker or by its token row;
- or extend the reader's rule 1 to every family judged purpose.

Hold GK item 1's refusal with a needle.

---

## M-3 (MATERIAL). The declared lattice step does not run on NQ

**Where.**
- **The template.** T l.272-273: "The lattice step s is one tick, unless the declaration states another fixed value
  here, classed fixed (<...>), dividing l and g". T l.300: n = round(sigma² T / s²).
- **The gatekeeper.** GK l.110-111: "refuse an s left to the build".
- **The runner (staged).**
  - `three_way_journey.py` l.61 (`WALK_MAX = 1024`);
  - l.99-101 (s must divide l and g);
  - l.106-107 (REFUSED rn-2 above 1024 steps);
  - `three_way_s1.walk_step_for` (l.180-190): a per-trade s from v and T.

**Evidence (arithmetic; I read no bar).**
- **The bound.** n <= 1024 at s = 1 tick needs sigma <= 32 / √T ticks per root-minute: 1.85 at T = 300 minutes, 4.1
  at T = 60.
- **NQ is far above it.** NQ's one-minute moves on the search years are well above half a point per root-minute. That
  is general knowledge, not a reading here, and it is checkable on the search years.
- **So the template's default fails.** A template-default declaration has its walk trades refused at run time.
- **The way out the runner took is forbidden.** The H3 toy escapes by choosing s per trade (`walk_step_for`), which T
  l.272 and GK forbid.
- **A single fixed s has a cost.** It must keep n <= 1024 at the search years' highest causal sigma and longest T, and
  divide every l and g. That forces S1's and S2's brackets onto multiples of s, a lever-space restriction no row
  declares.

**The failure it allows.**
- **The default declaration's run is refused.** Under the failure protocol, that run is never rerun until it passes.
- **Or the drafter picks s after seeing which values the runner accepts.** That choice is unlabelled, and it moves the
  bracket grid.

**Remedy.**
- **Declare s as a rule fixed before the pin, either:**
  - one value with its n bound shown on the search years' causal sigma (a search-year reading, entered in the ledger),
    and the bracket grid it imposes, in section 3;
  - or a per-trade rule from the causal sigma and T known at the fill (the S1 form), classed fixed.
- **Divisibility.** Since both ends are resolved by two-point sub-steps (the runner's `_p_up` already handles a
  fractional top), "dividing l and g" can be dropped, with a runner change. Cite `WALK_MAX`.

---

## M-4 (MATERIAL). The tests hold the words, not the rules: mutants

`probes_v2/mutate.py` applies one text edit to a fresh copy of the scratch tree and runs TT (38 tests); a failure
counts as a kill. **6 killed, 24 survive.**

| mutant | result |
|---|---|
| J1 a `stage_C_judgement` line in the template | killed |
| J2 GK: "a search declaration may carry" the line | **survives** |
| J3 GK: the refusal of a search's line deleted | **survives** |
| J4 step 8 no longer gives F-HT the line | **survives** |
| B2a/B2b the B-2 clause's floor and daily-limit labels swapped (a floor-bound account's day stops: the stranded state) | **survives** (each) |
| B2c GK: a floor-bound account "kept, the trade skipped" | **survives** |
| B2d the boundary sentence inverted | **survives** |
| W1 the walk on L (the runner's form) | **survives** |
| W2 the two-point probability rho/(s + rho) (drift) | **survives** |
| W3 s "chosen by the build per trade" | **survives** |
| N1 10 (c)'s playbook no-harm floor read on the held-out years | **survives** |
| N2 section 4's floor read on the held-out years, the design removed "after the held-out test" | **survives** |
| N3 "not significantly below" | **survives** |
| P1 a failed power gate "proceeds" | **survives** |
| P2 a failed calibration "may be re-run once with another seed" | **survives** |
| R1 rounds "may be extended after a look" | **survives** |
| K1 the level 0.05 / k | killed |
| K2 "taken by this search" | killed |
| S1 `<S4>` "may reuse `<S1>`" | **survives** |
| F1 "P_B ... is 0.42 and its pass rate 37 %" | **survives** |
| F2 "1250 USD" | **survives** |
| E1 the horizon embargo dropped | **survives** |
| O1 the joint order fixed "after the held-out read" | **survives** |
| C1 GK's race at min(l, c) | killed |
| C2 the merge checklist's walk "rounded inward" | killed |
| A1 the auditor's single use per market dropped | killed |
| T1 "the clip binds" (once) | survives (the phrase appears twice) |
| H1 "This search reads the five-minute cell on the held-out years" | **survives** |
| G1 the gates read "after the outcomes" | **survives** |

**The failure it allows.**
- The gatekeeper's step 0 runs TT as "the template itself still carries every field" (GK l.29-30).
- A later edit to the template or a copy that reintroduces B-2, B-3 or B-4, or reads the no-harm floor on the held-out
  years, passes it.
- The typed-figure scan (TT l.57-63) catches only fractions of three or more decimals, dollar signs and long integers.

**Remedy.**
- **A needle for each rule-carrying phrase above:** the floor/limit assignment of the B-2 clauses (as an ordered pair),
  "on the search years" inside the playbook clause itself, "goes no further", "never extended after a look", the
  embargo sentence, `<S4>`'s disjointness, "before the held-out read" for the order, "Nothing of this search reads the
  held-out years", "before any outcome", and GK's refusal bullets.
- **A figure scan** for any decimal and any "N %" outside an allowlist of the rule values the template cites (5 %,
  10 %, 0 %, 20 %, 25 %).

---

## M-5 (MATERIAL, the drafter's proposal 1). The CHARTER 3.7 reading row

**The proposal.** The whole declaration is frozen by one sha256 at its pin, before the calibration and the power
gate. "The search's pin" is the go row after them. "Does not pin" means no go row: the file is closed by a row and k
stays unspent.

**What holds.**
- **It is stricter than CHARTER's literal order.** That order lets the rest of the declaration be written after the
  calibration has run on the pinning row's inputs; under the reading, everything is frozen first.
- **It matches E-204.** k is assigned at the held-out row.
- **It matches the template.** T l.407-408, l.436-438, l.549-563; GK l.80-81.
- **It weakens no safeguard.**

**What it must add.**
1. **Every CHARTER phrase that uses "pin" for this step**, not only 3.7's "precedes the search's pin" and "does not
   pin". That is 3.7's "Power gate (before any search is pinned)" and 3.8 (a)'s "A pinning row whose limits would fail
   a design equal to the best baseline ... does not pin". Otherwise 3.8 (a) still reads as if the limits could be
   altered before a pin.
2. **The two senses of "pin", named.** The reader's `pins()`, `tests/test_declarations_fixed.py` and rule 1's "newer
   than the pin" mean the hash row. CHARTER's "the search's pin" means the go row. An auditor applying rule 1 for F-HT
   must use the hash row.
3. **What a successor may change after a closing row.** The limits, budgets, weights and the size that matters are set
   "from H4's search-year results by a rule declared before H4 is read" (CHARTER 3.9). A successor after a failed
   limit clause or power gate cannot re-set them by a new rule, because that rule would be written after H4 was read
   (red-team item 7, "limits set after a result").
   - So either the H4 rule declares its own next option before H4 is read, or the line closes with exit (B) and the
     gate's power.
   - The row must say which. Otherwise "closed, k unspent, re-declare" is a free retry on the gate.
   - Also say: the successor changes only what the failure's diagnosis names, cites the record, takes a fresh seed
     block (T l.417-419), and the number of closed attempts is printed beside the verdict.

---

## m-1 (MINOR, latent). The walk's floor-side law: the template against the runner

- **The template.**
  - T l.257-258: "its walk uses L_fill".
  - T l.289-296: the walk's barrier is the fractional L_fill; each outcome pays its exit's cost (m-3: a stop's cost for
    the barrier loss); "a floor-side loss ends exactly on the floor ... so the clip never binds".
  - GK l.115-116 and the merge checklist say the same.
- **What happens when x_flat > x_stop:** the barrier loss leaves c - L_fill - x_stop = x_flat - x_stop above the
  floor. It does not breach the floor, and the B-2 rule fails the account at its next fill. So T l.295's claim fails.
  TT l.624-626 asserts `-lf - max(xs, xf) == -c`, a booking the template does not make.
- **The runner (staged).**
  - The walk's floor-side barrier is L_race = min(l, c - x_stop) (l.258-263: "since corrective cycle 2, R-10's
    walk's too").
  - A time exit's flatten cost is clipped at -room (l.421-423, l.468): the clip binds and credits up to x_flat - x_stop
    of cost. That is the defect T l.214-216 rules out, in miniature.
- **Today:** identical while x_flat = x_stop. `vendor/stage2/config/fills.yaml` `assumed` has stop and flatten at 1 tick
  each, and +1/+2 tick stresses add to both.
- **Remedy:** before any profile or stress with unequal stop and flatten costs loads, the lead rules one law. One
  choice is L_fill with the residue failed at the next fill, the claim worded "at most x_flat - x_stop above"; the
  other is L_race with the clip, its credit counted and printed. The template, its copies, TT l.626 and the runner then
  agree.

## m-2 (MINOR). Both barriers within one step

- T l.291-293 resolves the floor side by "down to -L_fill with probability s/(s + rho), else up one step", and "a
  fractional g' ... the same way on its side".
- At a lattice point that is the last above the floor and the last below g', the two rules conflict.
- The runner uses rho_d / (rho_u + rho_d) (BUILD_W32_v3 probe 3).
- A need-aware g' under one step reaches it.
- Remedy: state the runner's case.

## m-3 (MINOR). A daily limit below the costs

- T l.263: where the daily limit binds, "the day stops". If dll <= e + max x (at the arm's stress), every day stops at
  its first offer, so the account never trades and never fails, against T l.264.
- The runner refuses this at construction (n-2; staged l.600-608). A design's own daily stop (an account-policy lever)
  can be set there.
- Remedy: the refusal, in the template's words.

## m-4 (MINOR). "Before the pin" in section 9

T l.430 says "The power gate, before the pin", against T l.407-408 and step 3. Read it as "before the go row" and
change the words.

## m-5 (MINOR). The no-harm floor's form

- T l.152-153 and l.466-468 say "not below the coin side's by more than the margin". T l.376 leaves "its direction or
  form" to the draft.
- Remedy: state that it is decided at the point estimate over `<S1>`'s seeds, paired on the same fills, as O-5 rules
  for limits, never by a test that fails only on evidence of harm.

## m-6 (MINOR). The copies

- **`contract-engine` l.135-137 and `feature-rules` (section 5's paragraph):**
  - "an account with L_fill <= 0 failed at the fill where the floor binds", with L_fill never defined there;
  - neither names the daily-limit case.
- **The auditor:**
  - item 6 (l.105-107) checks "the search's finalists' row and its held-out row" and "no `heldout_*` line ... by
    another declaration", where it should be F-HT's rows, every firm's finalists' rows before F-HT's held-out row, and
    F-HT as the one declaration;
  - item 4 (l.92) reads "the finalists in the pinned order", where it should be the joint order F-HT fixed;
  - (c) (l.84) does not name the check that no finalist failed its playbook no-harm floor before the finalists' row.
- **The other copies** (red team item 8, the merge checklist, `prereg-discipline`, GK items 1, 4 and 5) say what the
  template says, except as m-1 to m-3 note.

## m-7 (MINOR). Power at the joint place

- The per-search gate states power for a finalist tested first.
- In the joint sequence, a later finalist is tested only if every earlier one passes.
- Exit (B)'s "line's power" (T l.437-438, l.614) should be re-stated in F-HT at the joint order.

## m-8 (MINOR, the drafter's proposal 2). The sizing experiment

**As specified** (T l.267-271):
- It cannot reach C-1, because `_trade_mc`'s `Trade` has fixed contracts.
- Its count of rooms in (EPS, e + max x] at the horizon is not zero under the rule, because accounts that end there
  after their last trade are counted.
- It states no use and no output form.

**A specification that settles B-2's and C-1's size.**
- **Setup:**
  - synthetic only;
  - one worker, `OMP_NUM_THREADS=1`, under 500 MB, minutes;
  - toy rules shaped like Topstep's, cited by their keys (`combine_mll` with its trailing lock, the DLL where the
    account has one);
  - costs from `fills.yaml` `assumed` with `round_turn_by_instrument`;
  - brackets over S1's search-year range (Q-171's file) and S3's whole-micro room cut.
- **Arms:**
  - (i) the template's B-2 rule only;
  - (ii) (i) plus C-1's out-of-room rule;
  - (iii) the vendored engine's handling (the race at the clip, with its win chance, and D-318).
- **Read per offer:** the share of lanes that take, fail at the fill, end their day, end out of room, or do none of
  these (the invariant, expected 0 in (ii)).
- **Read at the end:**
  - P_B, replacements and the failure share by route;
  - the n-1 band's share at a stop-only stress.
- **Output:** a result file with its manifest (it sizes a declared rule's beside reading), or labelled exploratory. It
  chooses no lever.

## Notes

- **n-1.** T l.198's g' = min(g, level / (tick value x contracts) + x_target) is gross ticks from a net-dollar level.
  The runner's `Trade.level` must receive it in that unit (BUILD_W32_v3 m-3).
- **n-2.** The reader's ledger is per tree: the clean run's lines must be on master before the next judged read.
- **n-3.** The scratch run, as above.

---

## What I tried that found nothing

- **Look-ahead.**
  - R-10's sigma reads bars closed at or before the alert (T l.297-302); T is known at the fill except for the declared
    last row.
  - The profit level is known at placement (T l.196-199).
  - The take reads only the fill's state: the bracket, the room after the entry cost, both exit costs and `EPS` (T
    l.253-256). The runner's `_l_fill` matches (staged l.266-271).
  - Calendars are published in advance; regime thresholds come from the search years; the embargo is stated (T
    l.62-65).
- **Leakage.**
  - Every input in section 7 is from the search years only.
  - H4 is sealed; the reverse reading is not run.
  - No held-out row reaches the variants ledger (a build requirement with its test, T l.89-91).
  - The ledger I could read holds no family judged read of NQ (identity and registered-design lines only). E-192
    confirms that F-03 read nothing past 2023, so rule 2 does not yet block F-HT.
- **B-1.** Fractional everywhere, with inward rounding only on m-2's shared path; mutant C2 is killed.
  - The race: L = min(l, c - x_stop); a loss plus its cost ends at or above the floor; p = L/(L + g) gives zero gross.
  - The two-point bottom step has mean zero by hand: -rho s/(s + rho) + s rho/(s + rho) = 0.
  - TT's exact walk (l.588-626) gives zero mean at fractional barriers.
- **B-2 at a fill.**
  - With the template's c, the failure at the fill books -room, the race's limit as L goes to 0+, consistent with
    E-247's ruling and the runner's `_classes` (staged l.274-289).
  - The take uses L_fill for every law, and the n-1 band is empty while x_flat = x_stop.
- **B-3's token mechanics.**
  - F-HT's `heldout-finalists: F-HT @ <sha> list <sha>` matches `HELDOUT_TOKENS["finalists"]`, and rule 1 requires it
    newer than F-HT's pin.
  - Rule 2 excludes only other families, and the once-rule is per purpose, so one run per purpose reads every firm.
- **B-4.** The playbook floor is in section 4 (T l.149-156), 10 (c) (T l.466-469) and GK item 4. It is read on the
  search years before the finalists' row, and section 11 keeps only its held-out reading.
- **Multiple testing.**
  - One k, at 0.05 / (k (k + 1)) with k = 13 (T l.528-531).
  - Intersection-union over baselines at the full level, and a fixed sequence at the full level.
  - Every added condition (time leg, stresses, floors) only removes passes, so the family-wise level holds.
  - A search takes no k; mutant K2 is killed.
- **The point-estimate form of the limits** (E-230) is in every O-5 copy (TT l.719-734).
- **The test file.** 38 tests pass in the scratch copy.

## What I could not check

- **C-1's frequency** under Topstep's trailing MLL, the real S1 range and S3's step: m-8's experiment.
- **Whether Wave 5's search runner will call the vendored lockstep** (which has D-318 for room-capped Combines) or this
  repository's race (which has no sizing). C-1 binds in the second case.
- **NQ's causal sigma in the runner's unit on the search years** (M-3's bound is arithmetic). One light reading would
  settle the s that keeps n <= 1024.
- **The held-out test's declaration itself:** it does not exist yet.
