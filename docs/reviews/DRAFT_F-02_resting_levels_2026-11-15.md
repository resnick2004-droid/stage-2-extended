# Red team: `prereg/DRAFT_F-02_resting_levels.md` (family RL2, the corrected resting-order level family), 2026-11-15

The red team (`.claude/agents/red-team.md`), read-only, in worktree `wt-levels` at master e450912. **Target:** the
draft as committed (818 lines; not pinned, not numbered). **Read against:** `CHARTER.md` (sections 2-4 as amended by
E-008, E-014, E-015); `DECISIONS.md` E-001..E-017; `CLAUDE.md`; `extended/walker.py` with `tests/test_walker.py`,
`test_walker_mirror.py`, `test_walker_stage2.py`, `test_walker_t13.py` (identity E-010, E-011);
`.claude/skills/feature-rules` and `prereg-discipline`; `docs/audits/phase0/D_protocol.md` (all of it, Part 2 and 1.5
in particular) and `E_rules_currency.md` (C1); `docs/reviews/phase0_red_team_2026-11-15.md`; the briefs Q-16 and Q-21;
the withdrawn `prereg/F-01_resting_order_level_atlas.md` and `prereg/DRAFT_F-B_multifeature.md` (for its follow-effect
control only). In the vendored tree: decision rows D-212, D-266, D-271, D-272, D-308, D-429, D-527, D-550, D-555,
D-557, D-558, D-578, D-580, D-586, D-587, D-588, D-589, D-592, D-604; `data/README.md` section 5; `config/atlas_a1..a3.yaml`
(`pdhl`), `search_program_s3.yaml`, `gap_reversal.yaml`, `open_reversion_nq.yaml`; `prereg/P-14_*.md` (sizing, caveats,
pass line), `P-16_*.md` (its bound); `results/stop_band.csv` and its manifest; `results/u_value_map.csv` (sections
`definitions`, `place_values`, `records_leaf`, `bar`); `propedge/campaign/gate.py` (`shifted_blocks`, the bound arm);
`propedge/research/user_journey.py` and `scripts/user_journey.py` (the verdict arm's level).

**What I ran:** two small synthetic scripts, one process each, `OMP_NUM_THREADS=1`, in the session scratchpad
(not durable; their code is in Appendix A so they can be re-run): `negation.py` (the walker as committed, on synthetic
tick-walk days) and `iut.py` (Gaussian stand-ins, no data). A seed search by `grep` over the worktree. **Not done:** no
read of `data/bars` or `data/atlas`, no engine run, no web, nothing written but this note.

**On the brief.** It names C1', stage D and K5 as places to look and asks whether each correction removes its defect;
it states no wanted conclusion. I treated it as scope. The draft's own section 0 maps every audit finding to a
correction; I did not take that map as evidence and judged each correction from the text and the code.

**Severity** as the audit's: CHANGES-A-CONCLUSION (CAC), MATERIAL (MAT), MINOR, NOTE. Figures marked *synthetic* are
red-team arithmetic on simulated data, not results of this repository, and decide nothing.

---

## Verdict

**Must be redrafted** -- a revised draft is due anyway for Q-16's marks, and these changes belong in it. None is a
reason to abandon the family.

- **Corrections that remove their defects** (checked, section 3 below): D-1 (the pair rule and symmetric booking are
  side-neutral on a tick-continuous walk; the ambiguous mark is reflection-invariant and does not depend on R), D-5
  (levels, sides and `P_ref` from bars stamped at or before 08:24; void read from the bar stamped 08:29; fills from the
  bar stamped 08:30 -- the walker's indices agree), D-6, D-7, D-8 (in stage A), D-9, D-10, D-14, M1, M7, N-2 (the seeds
  are unique), N-3, M4, A's MINOR 1, and the re-declaration boundary of section 13.
- **One correction does not do what it says (MATERIAL, F1).** C1' is meant to separate a level's effect from the
  follow-the-breakout effect Stage 2 already read on this window (D-592). For the two range-extreme kinds, `on` and `pd`,
  it cannot. A break fill there is also a breakout of a long window. Stage 2's A4 found the follow effect at breakouts up
  to 60 minutes (D-555). The placebo is a since-08:30 crossing at a matched distance, not a breakout of that window.
  So a C1 + C1' pass at `on` or `pd` would be recorded as a level finding when it is what the known effect predicts.
- **Corrections that bring in defects of their own (MINOR, F2-F10):**
  - the placebo can read days after its own (F2);
  - stage D's realised-risk floor, its sizing and the stop-band claim (F3);
  - a microstructure bias left on the deciding booking (F4);
  - the rule side's own resolution on the choice block, never checked (F5);
  - early closes found from the day's own bars (F6);
  - the stage-D floor's bound level, not stated (F7);
  - valuation at the best place, while tickets go to the first account (F8);
  - gaps in the prior-exposure section (F9);
  - the meaning of a fade pass (F10).

## 1. Findings

| id | sev | finding (short) | remedy |
|---|---|---|---|
| F1 | **MAT** | C1' does not separate `on` / `pd` breaks from Stage 2's breakout-follow effect: the placebo is not a breakout of the same window | redraft 9.2 / 5.8 (one of three options) and add T-14 (c) |
| F2 | MINOR | The placebo ticket on day π(D) is built from day D's level distance and `A_D`, and π(D) may come before D; the draft's shift test (17.3) does not cover placebo tickets; `n_level` / `n_placebo` in C1' undefined | past-only source days; placebo tickets in the shift test; define the n's |
| F3 | MINOR | "Stop band" cited as the 45-tick cost floor only; NQ's band edge is 82 ticks (Combine, $1,500) and 134 (funded below $2,000); floor (ii)'s form (D-212 (1) as written, or P-14's allowance-capped intention) undeclared; C2 prices 50- and 100-tick picks at `p14`'s rung-averaged `mean_dv` | declare the form; stand aside (D-272) where the cap cannot carry the leaf; value at the places where the stop is sizeable |
| F4 | MINOR | The deciding booking is symmetric about a bar-visible trigger; fast-market overshoot (pro-break) and bid-ask bounce (pro-fade) are invisible to T-13's tick-continuous, spreadless walk; break and fade being exact negatives, either is a pure sign bias; the overshoot reading is beside only | C2 for a break pick at the `rule_fill` 1-tick rung; a T-13 variant with a spread and jumps on record before the pin |
| F5 | MINOR | Stage A reads resolution pooled over rule and mirror; the rule side's own unresolved share on 2020-2023 is never a line (C3 reads it on the judged block only), while D-212 (2) binds every year | the pick's rule side at its R at most 5 % overall and every year 2020-2023, read in stage B |
| F6 | MINOR | "A trading day ending before 15:00 CT voids every kind" -- found from the day's own bars at 08:25 | a pinned list of scheduled early closes (CME calendar) and of data-defect days, fixed before the run |
| F7 | MINOR | Stage D floor (i)'s bound level is not stated: the bases' registered PASS lines are at 0.05/N; the tickets are shifted at 0.05 (11.4); one campaign then mixes levels | one level for both streams, stated |
| F8 | MINOR | C2 values a pick at the best place that asks its R (10); stage D routes the ticket to the first account that asks it (11.2): D-3's "what the screen valued is not what the campaign spends" survives in C2 | value at the routing's own expected mix, or route to the valued place |
| F9 | MINOR | Prior exposure misses S3's `gap_rth` / `gap_glbx` (side of the previous close, NQ 2020-2026), A4's `brk` at 60-90 minutes and Globex-open ranges, and that `pdhl` is absent from A4's survivors | add them, with what each found |
| F10 | MINOR | A fade pass is judged on its plain lift only, so it is not separated from a generic reversal at any crossing (the audit's 1.3 item 4) | say so in 9 and 13, or apply C1' to both side rules (costs power, spends nothing) |
| N1 | NOTE | K5's share does not depend on R (for R >= 1) under symmetric booking; a "(cell, R)" kill is a cell kill | -- |
| N2 | NOTE | K5 / C4 guard no error rate under the pair rule (zeros only dilute); the 5 % is borrowed from D-212's flatten ceiling by analogy; the pair rule excises in-bar moves of S - 1 ticks or more, where a cascade would be | label 5 % a design choice; state the estimand |
| N3 | NOTE | Section 0's D-1 row cites 7.6 for K5; K5 is 7.3 | -- |
| N4 | NOTE | The derangements' draw order (kinds, years, the reshuffle loop) is unspecified, so seed 20261932 does not yet fix the placebo; `A_D` on early-close and seam days undefined | specify |
| N5 | NOTE | T-13 at a quarter of the smallest bar (0.283 points) needs about 3.5 million fills per (side rule, stop): about 20 times today's T-13 | mark it heavy; budget it |
| N6 | NOTE | Stage D after a close at C reads the judged block's start days for a closed design | later families list it as prior exposure |
| N7 | NOTE | K4's fills-over-touches is a micro-rejection rate read in stage A; it decides nothing, but it is mechanism-relevant | call it "reported, decides nothing", not "direction-free" |
| N8 | NOTE | The feature-rules skill calls the bar column `timestamp`, "Bar OPEN time"; the README's is `ts`, "Bar START, epoch seconds UTC". The draft is right | the skill's slip, for the lead |
| N9 | NOTE | Stage A's cutoff requires all three R to resolve, though only the pick's R is traded | conservative; costs power |

---

## 2. The findings in detail

### F1 (MATERIAL) -- C1' cannot separate a range-extreme level from the known breakout-follow effect

**Where.** `prereg/DRAFT_F-02_resting_levels.md`:
- lines 121-124: "a break cell passes only if its lift also exceeds that of matched non-level crossings";
- lines 233-250: the placebo, 5.8;
- lines 406-415: C1', and what a C1-only pass means;
- line 41: section 0, D-2's row;
- line 108: A4's row of the prior-exposure table.

**Evidence.**

*What the placebo is.* It is placed on day π(D) at `P_ref(π(D)) + side x d'`, where d' is the real level's distance
scaled by `A_π(D) / A_D` (line 244). A buy-stop placebo fills at the first trade at that price after 08:30 (the void
rule removes earlier crossings). At its fill the price is at a new high **since 08:30**, and above the 08:24 close by d'.
Whether it is also a new high of a longer window (the overnight session, the prior day) is left to chance. With d' near
`P_ref` -- typical for `on` -- it usually is not.

*What the real fill is.* A real `on`-high fill is, by construction, a new high since 17:00 the evening before. A real
`pd`-high fill is a new high above the whole prior regular session.

*What Stage 2 found on this window.*
- A4 found the follow effect at breakouts of 5- to 90-minute windows. Its menu was `brk` at k = 5..90 minutes, `nbar` up
  to 30-minute bars x 8 (D-550). Its survivors were "short breakouts and n-bar runs on 5- and 10-minute bars, **a few at
  15 and 60 minutes**", all on the follow side (D-555).
- S1 and S3 found the follow side again (D-580, D-588).
- D-592 calls the effect "broad and slow rather than tied to the last bar".

*What D therefore measures.* D = L(level) - L(placebo) estimates the follow lift at a long-window breakout less the
follow lift at a short-window one. If the follow effect is the same at every horizon, D is about zero and C1' works. If
it is larger at longer horizons -- signals at several horizons adding up, which "broad and slow" allows and A4's
60-minute survivors suggest -- then D > 0 with no level effect at all.

*Where it does not apply.* For `pdc` and `rn100` the real level is not a range extreme, so the placebo is a fair
match there. This finding concerns `on` and `pd` only.

**The failure it allows.** Take an NQ judged block on which (i) no order clusters at any visible price, and (ii) D-592's
follow lift is somewhat larger after breaking the overnight high than after a 20-tick rise from 08:24. Then:
- stage B picks an `on` break cell at its choice-block lift;
- C1 passes (the follow effect is strong in 2024-2026, D-588);
- C1' passes (D > 0);
- 9.2 records a level finding beyond D-592, the pick is CARRIED and takes a registration id and a confirmation purchase.

Under the same mechanism the confirmation passes too, because the follow effect is "a lead for unread data" (D-592). So
the confirmation would confirm the known effect under the level's name. The draft's statement of what a pass means
(lines 412-413 and 121-124) is then wrong. This is exactly the D-2 / D_protocol 1.2 (4) case the correction was meant to
close.

**Remedy (one of these, before the pin; each changes declared text):**
- (a) **A reading that changes the meaning, the cheapest.** In 9.2 and 13: a break pick at `on` or `pd` that passes C1
  and C1' is recorded as "a range-extreme breakout effect beyond a matched since-08:30 crossing, not separated from the
  long-horizon end of Stage 2's follow-the-breakout effect (D-555, D-592): a lead for unread data, carried only by its
  confirmation". Say the same in section 2.
- (b) **A placebo matched on the horizon for `on` and `pd`.** On π(D), put the placebo at that day's own same-kind
  extreme moved outward by the scaled offset (seeded as now). Every placebo fill is then a breakout of the same window,
  at a price with no visible meaning. Its contamination by the level's own continuation is conservative, as the draft
  says of coincidences.
- (c) **Drop `break` at `on` and `pd`** (24 cells to 20), leaving C1' where it identifies.

With any of these, **add T-14 (c)** (synthetic, cheap):
- plant a continuation that grows with the look-back of the range broken -- for example a drift for a few minutes
  after a crossing, proportional to the log of the minutes since the price last stood there -- and no level effect,
  on days with an overnight segment;
- the C1' statistic must then cover zero.

The draft's T-14 (line 751), "planted at every crossing alike", plants the effect the placebo already matches, so it
cannot show this.

### F2 (MINOR) -- the placebo reads days after its own; its shift test does not cover it

**Where.** Lines 238-246 (the range, the pairing, the placebo ticket); lines 725-728 (test 3); line 409 (`z_s`).

**Evidence.** The pairing is a random derangement within a calendar year (line 240), so π(D) is before D about half the
time. The placebo ticket on π(D) is placed using day D's level distance d and `A_D` (line 244):
- **`A_D` overlap.** When π(D) is within the 20 sessions before D (about 20/250, 8 % of placebo tickets), `A_D` includes
  π(D)'s own regular-session range -- an outcome of π(D).
- **`pd` / `pdc` with D = π(D) + 1** (about 0.4 %). d is π(D)'s own regular-session high or low (or close) less the next
  morning's price. The placebo resistance then sits about (high - close) of π(D) above that day's 08:24 price, so it
  fills about exactly when π(D) closed above its 08:24 price.

Test 3 (line 726) holds levels, sides, `P_ref` and `A_D` on day D fixed when day D's bars from 08:25 are replaced. It
never asks whether a placebo ticket on π(D) moves when π(D)'s own later bars are replaced. The house rule
(feature-rules 2: "every normaliser is computed from the past only") is broken for a control that decides break cells.

**Direction and size.** On these mechanisms the leak raises the placebo's follow lift: placebos sit nearer on wide-range
(trend) days, and fill on the days that then continue. So it lowers D, which is conservative for a break pass. That
makes it MINOR. But:
- it is a look-ahead the build's own test would pass;
- the fade placebo beside is biased the other way;
- C1' is computed from per-session sums `z_s` whose `n_level` and `n_placebo` (line 409) are not defined. With block
  totals, the sum of z_s is D (the mean over fills, D-14's estimand); with per-session counts it is a mean of session
  means.

**Remedy.**
- Draw each placebo day's source from sessions at least 21 sessions **before** it (a past-only pairing). Or draw the
  normalised distance d / `A_D` from the kind's own distances on earlier days.
- Put the placebo tickets into test 3: replace every bar of π(D) from 08:25, and every bar of every later day, and the
  placebo price must not move.
- Define `n_level` and `n_placebo` as the block's fill totals.

### F3 (MINOR) -- the stop band, floor (ii)'s form and the 50-tick ticket's size

**Where.** Line 135 (contract fit: "stop band and cost floor (`stop_band.csv`, 45 ticks) | ... all above the floor");
line 134; lines 324-325 (6.3); lines 446-458 (valuation); lines 479, 507-508 (floor (ii); size).

**Evidence.**
- *The band.* `results/stop_band.csv`'s manifest defines the band's narrow edge as "the larger of the size-cap stop and
  the 0.10 cost-drag stop" (D-201 (2)). For NQ its narrow edge is 82 ticks in the Combine (at $1,500, 37-micro cap), 134
  ticks funded below +$2,000 (at $1,000, 15-micro cap), and 45 ticks only above +$2,000. The 45 is `cost_drag_floor_ticks`.
  D-272 replaced "T16 2(c)'s single 45-tick floor, which ignored the cap" with exactly this, so the draft's line 135
  repeats the error D-272 corrected.
- *The leaves.* P-14's recorded Combine leaves are almost all "$2,000 1.5R" (`u_value_map.csv`, `records_leaf`, `p14`,
  `combine`). D-212 (1) as written sizes min(floor(risk / (stop ticks x tick value)), the state's cap).
- *The 50-tick ticket.* At 50 ticks ($25 a micro) a $2,000 leaf needs 80 micros. Capped at 37 it realises about 46 % of
  the state's risk (about 62 % even at 50 micros).
- *The 100-tick ticket.* At 100 ticks, a funded $1,000 leaf needs 20 micros. Capped at 15 it realises 75 %.
- *P-14's form.* P-14 itself is held to "realised risk at least 0.9 of its **allowance-capped** intention"
  (`prereg/P-14_a3-brk30-cb20.md` lines 36, 388, 427) -- a relaxed form under which the cap cannot fail the line.

**The failure it allows.** The draft's floor (ii) says "D-212 (1)" and its size rule says "whole micros under the
allowance". It does not say which form decides.
- *Under D-212 (1) as written,* a 50-tick pick at R = 1.5 that passes C1-C4 is routed to Combine accounts (the
  evaluation asks 1.5R). Floor (ii) then fails by arithmetic knowable today: a close at D after the judged block is spent.
- *Under P-14's form,* the floor cannot fail, but the ticket carries a third to a half less dollar risk than the leaf.
- *Either way,* C2 prices it at `p14`'s `mean_dv`, which is "averaged over the rungs" (`definitions`, `dv`). So 50-tick
  picks are over-priced and 100-tick picks under-priced where the cap binds.

**Remedy.**
- Correct line 135: the band per state, from the file.
- Declare floor (ii)'s form.
- Apply D-272's stand-aside -- a ticket is routed only to a state whose cap carries at least 90 % of the leaf's risk at
  the pick's stop (contract arithmetic, not a parameter).
- Compute C2 over the places where the stop is sizeable. A (stop, R) with no sizeable place is valued at zero.
- If a per-rung `dv` is not in the vendored map, say C2 uses the rung average and in which direction it errs.

### F4 (MINOR) -- the booking that decides is symmetric about a bar-visible trigger

**Where.** Lines 201-212 (5.5); line 268 (slippage row); lines 434-437 (the ladder, beside); lines 741-747 (T-13).

**Evidence.**
- *What symmetric booking fixes.* It removes F-01's one-tick handicap of the rule (the audit's D-13, part one).
- *Part two, left beside.* The rule's fill is "the stop's price plus one tick" on any bar that touches it. If the market
  skips past the stop -- the cascade the hypothesis describes -- the user's stop fills worse. Meanwhile the symmetric
  mirror is booked a tick below the stop's price, below where a coin's market sell would have filled. Both errors favour
  `break`. With an overshoot of k ticks the pair is mis-booked by about 2k - 1 ticks. That is about (2k - 1) / (4S) of
  lift: 1.25 points at S = 100 and k = 3; 2.5 points at S = 50 (Appendix C's 1/(2S) per tick and trade).
- *A bias of the other sign.* A trigger print on a rising bar is likely a buy at the offer, so the mid sits about half a
  tick below it. Booking about the print, not the mid, then tilts the pair against `break` and toward `fade` by about a
  tick.
- *Why sign matters.* Break and fade at one level are the same pair with the labels swapped (lines 221-226, verified in
  Appendix A). So either bias is a pure sign bias: stage B's choice of side and C1 / C2 inherit it.
- *What else catches it.* C1' cancels only the part that is the same at placebo prices, and a level-specific cascade
  predicts more overshoot exactly at levels. K5 zeroes the fill bars that span S - 1 ticks, which bounds the worst
  cases.
- *What T-13 can see.* T-13 (`tests/test_walker_t13.py`) is tick-continuous (one tick a step) with no spread, so it
  cannot see either bias. The draft's T-13 extension (line 744) keeps that walk.

**Size.** Against an MDL of several points the bias can hardly make C1 pass alone. But C2's bar is 0.28 to 2.5 points
(`u_value_map.csv`, section `bar`, `target=500`; the audit's D-4), the same scale as the bias.

**Remedy.**
- For a `break` pick, read C2 (and optionally C1) at the overshoot reading's 1-tick rung (`rule_fill`, the mirror at the
  rule's fill: conservative for the rule), with symmetric booking beside.
- Add a T-13 variant on record before the pin: a one-tick spread and occasional multi-tick jumps, per side rule. It
  reads the size of both biases under the null, and needs no bar.

### F5 (MINOR) -- the pick's own resolution on the choice block is never a line

**Where.** Lines 336-339 (7.1: "the pooled unresolved share ... at every R ... overall and in each calendar year 2020 to
2023"); lines 418-421 (C3: rule side, judged block only).

**Evidence.** Pooling rule and mirror is right for stage A, which must not read direction. But D-212 (2), as D-308
raised it, binds the traded side at 5 % "overall, per market and per year". With the pooled share at 5 %, the rule side
alone can sit near 10 % in a year if its mirror resolves. Nothing after stage A reads the rule side on 2020-2023.

**The failure it allows.** A pick whose follow side leaves 7 % unresolved in 2022 (and 3 % on the mirror) passes A,
is picked at B and passes C3 on 2024-2026. It is carried while breaking D-212 (2) in a development year.

**Remedy.** Make it a pick-eligibility line in stage B (B already reads direction): the pick's rule-side trades at its
R at most 5 % unresolved overall and in each year 2020-2023.

### F6 (MINOR) -- early closes found from the day's own bars

**Where.** Lines 160-161: "A trading day ending before 15:00 CT (P-14 caveat C5) voids every kind".

**Evidence.**
- *What is wrong.* The void is taken at 08:25 from where the day's bars end. A scheduled early close is known in
  advance; a vendor gap or an unscheduled halt that ends a day's data early is not. Voiding such a day uses bars after
  `t_pub`.
- *How Stage 2 did it.* Stage 2's own house form lists early-close sessions by date from the exchange calendar
  (`config/gap_reversal.yaml`, `early_close_sessions`, D-111). The data report's caveat C5 records what was observed, not
  how to detect it.

**Remedy.** A pinned list of scheduled early closes (the exchange's published calendar), and a list of data-defect days
from the data report -- both fixed before the run and read as calendars.

### F7 (MINOR) -- stage D mixes bound levels

**Where.** Lines 478, 517-527 (11.4), 537-538 (11.5 (2)).

**Evidence.** The bases' registered pass lines shift each R "to the bound at 0.05/N" (`prereg/P-14_*.md` line 425,
N = 370; `P-16_*.md` lines 31, 66-67, N = 414). U1's `verdict` arm is the 0.05 bound (`scripts/user_journey.py` line
834). The tickets are shifted to the one-sided 95 % bound (line 517). Floor (i) is "Stage 2's `gate` call as the base
registered it ... Floor (i) is read here", with no level.

**The failure it allows.** If the base keeps its registered 0.05/N shift, one campaign carries base trades cut harder
than ticket trades. Floor (i) and the paired "base plus tickets less the base" then lean toward the tickets.

**Remedy.** State one level for both streams in floor (i) and in the scorecard's campaign. The 0.05 bound matches U1's
verdict arm and the charter's words.

### F8 (MINOR) -- valued at the best place, spent at the first account

**Where.** Line 447 ("the maximum over the places that ask the cell's R"); lines 495-498 (routing to "the first, in the
router's order, whose state's table leaf that session asks the pick's R").

**Evidence.**
- *The valuation.* For R = 1.5 the places asking it are (b), (d) and (e). Their `mean_dv` for `p14` are about $225,
  $629 and $665 (`place_values`), so the maximum is the funded or paid place.
- *The spend.* The router gives the ticket to whichever account comes first, and most account-days are Combine days.
- *Why it matters.* C2 is a pass line, so it can be met by a value the campaign does not spend. That is a milder form of
  D-3 (2).

**Remedy.** Value C2 at the routing rule's expected mix of places (from `records_leaf` shares, as σ already is). Or
route the ticket to the valued place first.

### F9 (MINOR) -- prior exposure: three omissions

**Where.** Lines 104-117.

**What is missing.**
1. **S3 (D-586, D-587)** read `gap_glbx` and `gap_rth` -- the side of the price against the previous trading day's last
   close, followed and faded against the coin twin -- on NQ 2020-2026 on P-16's schedule. That is the prior close as a
   reference, and it bears on `pdc`.
   - The "Not found" sentence (line 115) is true only for "as price levels".
   - D-588 records that Benjamini-Hochberg's rejections were nearly all breakout and n-bar rules.
2. **A4's menu (D-550)** held `brk` at 60 and 90 minutes and `orb` at the Globex (17:00) open for m = 15-60. These are
   the nearest Stage 2 reads to `on`, and A4's survivors include the 60-minute class (D-555).
3. **`pdhl` is not among A4's survivors.** D-555 names their classes, and `pdhl` is not one. Its sign is unknown here
   (line 108), but its survival status on 2020-2026 at 25 and 37.5 points, at delays 0 and 5, is known. Stage 2's
   `pdhl` is also defined on 08:30-15:10 (`config/atlas_a1.yaml` line 58) where `pd` here is 08:30-14:59 -- close, not
   identical.

**Why it matters.** Item 2 is the evidence behind F1. Items 1 and 3 belong in the D-189 N a later registration counts.

**Remedy.** Add the three rows, with what each found.

### F10 (MINOR) -- what a fade pass means

**Where.** Lines 233-236 ("decisive for `break` ...; beside for `fade`"), line 431, lines 611-614.

**Evidence.** The audit's 1.3 item 4 asks for lift(level) - lift(placebo) as the judged statistic because "any crossing
after a move carries short-term follow or reversal". The draft keeps it only for `break`, because D-592's known effect
is follow. A fade pass is then a reversal at a level crossing that is not separated from a reversal at any crossing.
Yet section 13's CARRIED and section 1's mechanism read it as the level's.

**Remedy.**
- Either say in 9 and 13 that a fade pass is "a reversal at these crossings; the level-specific part is the
  placebo-differenced lift beside";
- or apply C1' to both side rules. It is an intersection with C1 at the same level, so it spends nothing; it costs
  power only.

### Notes

- **N1.** Under symmetric booking with R >= 1 the four ambiguity conditions reduce to two: the fill bar's low at or below
  trigger + 1 - S, or its high at or above trigger - 1 + S (a target touch implies the other trade's stop touch). So the
  K5 share is the same at every R (Appendix A: 0 of 538 synthetic tickets differ). Line 342's "(cell, R) ... a cell with
  every R killed" is a cell-level kill. Harmless.
- **N2.** Ambiguous pairs count as zero lift, so they only dilute L. K5 and C4 therefore protect no error rate; they buy
  measurability.
  - The 5 % is "the share D-212 lets fall to the flatten" (line 279): an analogy, not a source. Label it the drafter's
    fixed choice.
  - C4 can close a true effect on the judged block for a direction-free reason. The 2024-2026 one-minute ranges in
    points are larger at NQ's higher price level, though not necessarily in volatility.
  - The pair rule also removes fills whose bar ran S - 1 ticks or more past the trigger -- where a within-minute cascade
    would be. K5 bounds that at 5 % of fills. Say so where the estimand is defined (5.6).
- **N3.** Line 39 cites 7.6 for K5; K5 is 7.3.
- **N4.** `default_rng([20261932, j])` must draw for several kinds (each has its own valid days) and several years, with
  a reshuffle loop. The order is not stated, so the declared seed does not yet determine the placebo; fix the order in
  the redraft. `A_D` on early-close days (a truncated range) and on 2025-06-30 (kept with no trades, P-14 C2) is
  undefined; say which 20 sessions count.
- **N5.** The smallest `extra_win_prob_points` at `target=500` is 0.283 (`p16`, best place, N = 104 and 250). A quarter
  of it, at T-13's Z = 2.64 and a per-fill sd near 0.5, needs about (2.64 x 0.5 / 0.00071)^2, about 3.5 million fills
  per (side rule, stop). Today's T-13 has about 470,000 a side rule from 9,000 days, so this is about 20 times as many
  synthetic days over three stops. Mark it heavy under the run lock, not fast tier (line 718).
- **N6.** Stage D after a close at C (lines 468-470) is consistent with E-008, but it reads P on the judged block for a
  closed design. Later families list it as prior exposure.
- **N7.** K4's "fills over touches" (line 348) measures how often the price stopped within a tick of the level -- the
  fade mechanism at its smallest. It is read in stage A, before stage B. It decides nothing, and stage B is mechanical,
  so no defect. But it is mechanism-relevant, not direction-free.
- **N8.** `.claude/skills/feature-rules/SKILL.md` line 13 calls the bar column `timestamp`, "Bar OPEN time".
  `vendor/stage2/data/README.md` (section 5) has `ts`, "**Bar START**, epoch seconds UTC". The draft (line 145) has it
  right; the skill needs the lead's correction.
- **N9.** The cutoff must pass K2 at R = 1, 1.5 and 3 (line 337), so an R = 1 cell loses late fills to R = 3's
  resolution. That is conservative, inherited from F-01, and costs power. E-008's "every offered R" is, for a ticket, the
  pick's R.

## 3. Does each correction remove its defect?

| audit / red-team finding | the correction | removed? | why |
|---|---|---|---|
| D-1 fill-bar asymmetry | pair rule, symmetric booking, K5 | **yes** | barriers symmetric about the trigger; ambiguity reflection-invariant (N1); T-13 holds on a tick walk at S = 100 (the extension to 50 / 150 owed, N5) |
| D-13 booking | symmetric; ladder beside | **partly** | the one-tick handicap is gone; overshoot (pro-break) and bounce (pro-fade) stay on the deciding booking (F4) |
| D-2 closed branch, line 23, follow effect | `or30` out; line 23 corrected; prior exposure; C1' | **partly** | `or30` and line 23 yes; prior exposure incomplete (F9); C1' does not identify at `on` / `pd` (F1) |
| D-3 stage D | base by stop; R-routing; cancel and re-place; floors only | **mostly** | the identification limits are stated (11.6); floor (ii)'s form and the stop band (F3) and the floor's level (F7) are new gaps |
| D-4 power | MDL from counts before B; close wording | yes (as a reading) | R-16 is honestly not applied |
| D-5 look-ahead, side at `t_live` | bars at or before 08:24; side at `t_pub`; void at 08:29 close | **yes** | checked against `walker.price_at` and `_window`: P_ref index <= 925, void index 930, first fill index 931 |
| D-6, M1 confirmation | NQ's fourth by D-107; tests trades not P | yes | -- |
| D-7 count | 24 cells, 72 hypotheses | yes | -- |
| D-8 K2 per year | 5 % overall and per year | yes in A; **not for the rule side** (F5) | -- |
| D-9, D-10, D-14, D-15 | recorded; moved; stated; table | yes (D-15: the placebo's 20 days and 5 replicates, and K5's 5 %, are the drafter's choices, N2) | -- |
| D-11 calendar | voids counted; `rn100` in futures price | **mostly** | the early-close rule reads the day's own bars (F6) |
| D-12 drift, placebo | beside; placebo decisive for break | yes for drift (it favours break, and C1' matches sides; it works against fade) | -- |
| A MINOR 1 and 2 | citations; 12.5-point stop admitted | yes, but the stop-band claim beside it is wrong (F3) | -- |
| M5 tickets' bound | which trades, block, era rule | yes in substance; its level against the base's is unstated (F7) | -- |
| M7, N-2, N-3, M4 | k next free; new seeds; Stage 2's flatten; one user | yes | the seed search reproduced: 20261930-39 appear only in the draft, the brief Q-21 and E-017 |

## 4. What I tried that found nothing

- **Stage B's min(t_L, t_D) inside the family-wise max** (lines 384-388).
  - *The suspicion.* With both components centred, the critical value is the least-favourable one for an
    intersection-union test only when both components are null. When the follow effect makes L large and D = 0, the
    break statistic is about t_D alone.
  - *The check.* `iut.py`, synthetic: 12 break cells and their 12 fade negatives, 4,000 bootstrap and 4,000 outcome
    replications, correlation of t_L and t_D at 0.5, 0.8 and 0.95.
  - *What it found.* The chance that some break cell with D = 0 clears stage B is 0.028-0.043 under the draft's
    construction, against 0.018-0.024 with the components entered separately. That is within 0.05.
  - *Why.* The fade cells sit in the same maximum as full-normal entries and carry q.
  - *Conclusion.* No defect, provided break and fade survive stage A together. They do: the same fills and
    direction-free gates, differing only at gaps and the void boundary.
- **Break and fade as exact negatives** (lines 221-226). `negation.py`, synthetic, the walker as committed (`pair`,
  `symmetric`, `STAGE2` rules): 538 pairs; every pair the same fill bar, and every non-gap pair exactly opposite at R = 1,
  1.5 and 3. The synthetic opens equal the previous close, so no gap fill arose; gap pairs differ, as the draft says.
- **C1' spends nothing.** It is an intersection with C1 at the same level: the IUT's size is at most the level.
- **Seeds (T-12).** `grep -rIow -E "2026193[0-9]"` over the worktree: only the draft, `docs/briefs/Q-21_2026-11-15.md`
  and E-017. Without word bounds, also one digit run in `vendor/stage2/results/a3_brk30_cb20_gate_paths.csv`, as the
  draft says. 20261910-29 appear only in the Q-16 and Q-17 briefs and the draft.
- **Leakage across blocks.**
  - Trades open and close the same session (no straddle).
  - `pd`, `pdc` and `A_D` at 2024-01-02 read 2023 bars, outcome-free.
  - Derangements stay inside a calendar year; stage B's bootstrap is on choice sessions only.
  - The value map spans 2020-2026 but carries no level direction (the audit's N-4).
  - T-3 is declared.
- **Roll and contract.** The store charts one contract a day, chosen on the **previous** day's volume (README section
  5), so the roll is known in advance. `on`, `rn100` and `A_D` are same-day; `pd` and `pdc` are voided on rolls and
  after early closes.
- **News.** Tickets go live at 08:30 CT, an hour after the 07:30 CT releases; FOMC days carry none. Topstep's rule that
  "pending orders ... will not fill during the 10-minute window" (E's C1) is never reached.
- **Walk end and flatten.** The family's preset is `STAGE2` without the breakeven move. The flatten reads the bars
  ending 15:08-15:10 less two ticks, which is conservative and does not enter w (a flatten is not a win).
- **Selection after the fact.**
  - Stops are P-14's and P-16's registered rungs; R values are the table's asks.
  - R = 2 and 2.5 were dropped on `records_leaf` shares, a Stage 2 input, not a level outcome.
  - The cutoff is searched by a declared rule on pooled, direction-free counts.
  - The placebo's 20 days and 5 replicates and K5's 5 % are fixed before any read (unsourced, N2).
- **Re-declaration escape.** Section 13 binds a later family on these levels to "data this family did not read".
- **Drift.** It favours break: break fills lean long in a rising market. C1' (side-matched placebo, same calendar year)
  cancels it. It works against fade.

## 5. What I could not check, and the experiments that would settle it

- **Whether the follow effect grows with the breakout's look-back** (F1's premise). That needs A4's lift by pattern
  (`results/a4_coin_atlas.csv`: `brk` k = 5..90, `pdhl`), which is not vendored.
  - It is a Stage 2 result already read by Stage 2. Vendoring and reading it is a prior-exposure read the redraft would
    cite.
  - The synthetic T-14 (c) of F1 needs no data and settles whether the statistic separates under that premise: minutes
    of CPU, well under 500 MB.
- **The size on NQ** of the ambiguous share, the overshoot and the bounce (F4, N2). These are direction-free and belong
  to stage A after the pin. The T-13 variant of F4 costs about what today's T-13 does.
- **Q-16's statistic**, and whether it covers C1''s per-session two-sample form. It is pending (the draft blocks the pin
  on it, line 414).
- **A per-rung `dv`** for F3. `u_value_map.csv` gives `mean_dv` averaged over P-14's two rungs.
- **Whether TopstepX lets a resting order be placed between 08:25 and 08:30 that works only from 08:30.** If it does
  not, the user places the ticket at 08:30:00. That matches the model: the fill window opens with the bar stamped 08:30.

---

## Appendix A. The two synthetic scripts (re-runnable; scratchpad copies are not durable)

```python
# negation.py -- the walker as committed, synthetic tick-walk days (no bar read)
import sys, numpy as np
sys.path.insert(0, r"C:\Users\resni\AppData\Local\stage2-extended-wt\wt-levels")
from extended import walker as W
rng = np.random.default_rng(424242); first = W.slot(8, 30) + 1; n = W.C_FLAT + 1
def day(steps=1600, jump_p=0.0):
    m = W.C_FLAT - first + 1
    st = rng.choice([-1, 1], size=(m, steps)).astype(np.int32)
    if jump_p:
        j = rng.random((m, steps)) < jump_p; st = st * np.where(j, rng.integers(2, 9, size=(m, steps)), 1)
    p = 80000 + np.cumsum(st.reshape(-1)).reshape(m, steps)
    o = np.full(n, 80000.0); h = o.copy(); l = o.copy(); c = o.copy()
    close = p[:, -1].astype(float); opens = np.concatenate([[80000.0], close[:-1]])
    o[first:], c[first:] = opens, close
    h[first:] = np.maximum(p.max(axis=1), opens); l[first:] = np.minimum(p.min(axis=1), opens)
    for x in (o, h, l, c): x[0] = np.nan
    return o * W.TICK, h * W.TICK, l * W.TICK, c * W.TICK
RRS = (1.0, 1.5, 3.0); S = 100
same = neg = gaps = nongap = ambR = npairs = 0
for d in range(150):
    o, h, l, c = day(jump_p=0.002 if d % 2 else 0.0); live = W.slot(8, 30)
    for k in rng.integers(20, 200, size=4):
        lvl = c[live] + int(k) * W.TICK
        tb = W.trade(W.Order(W.STOP_ENTRY, +1, live, lvl + W.TICK, W.slot(14, 0)), o, h, l, c, S, RRS,
                     rules=W.STAGE2, fill_bar="pair", mirror_booking="symmetric")
        tf = W.trade(W.Order(W.LIMIT_ENTRY, -1, live, lvl, W.slot(14, 0)), o, h, l, c, S, RRS,
                     rules=W.STAGE2, fill_bar="pair", mirror_booking="symmetric")
        if tb.fill.status != "filled" or tf.fill.status != "filled": continue
        npairs += 1; same += tb.fill.bar == tf.fill.bar
        lb = 0.5 * (tb.rule.win.astype(float) - tb.mirror.win.astype(float))
        lf = 0.5 * (tf.rule.win.astype(float) - tf.mirror.win.astype(float))
        if tb.fill.gap: gaps += 1
        else: nongap += 1; neg += bool(np.all(lb == -lf))
        ambR += int(len(set(tb.ambiguous.tolist())) > 1)
print(npairs, same, nongap, neg, gaps, ambR)
```

Output (2026-11-15): `pairs 538; same fill bar 538; non-gap 538, of which exact negatives 538; gap fills 0`; `tickets
whose ambiguous mark differs across R in (1, 1.5, 3): 0`.

```python
# iut.py -- stage B's q with break's statistic min(t_L, t_D), both centred; Gaussian stand-ins, no data
import numpy as np
rng = np.random.default_rng(7); K, B, REPS = 12, 4000, 4000
for rho in (0.5, 0.8, 0.95):
    Lc = np.linalg.cholesky(np.array([[1, rho], [rho, 1]]))
    z = rng.standard_normal((B, K, 2)) @ Lc.T; tL, tD = z[..., 0], z[..., 1]
    q_min = np.quantile(np.maximum(np.minimum(tL, tD).max(1), (-tL).max(1)), 0.95)   # the draft: fade = -break
    q_sep = np.quantile(np.maximum(np.maximum(tL, tD).max(1), (-tL).max(1)), 0.95)   # components entered apart
    for n_follow in (12, 1):
        x = rng.standard_normal((REPS, K, 2)) @ Lc.T; muL = np.zeros(K); muL[:n_follow] = 6.0
        T = np.minimum(x[..., 0] + muL, x[..., 1])                                     # L far above zero, D = 0
        print(rho, n_follow, (T.max(1) > q_min).mean(), (T.max(1) > q_sep).mean())
```

Output (2026-11-15), the share of replications in which some break cell with D = 0 clears q, the draft's against the
components entered separately:

| rho | 12 follow cells | 1 follow cell |
|---|---|---|
| 0.5 | 0.041 against 0.018 | 0.006 against 0.003 |
| 0.8 | 0.043 against 0.024 | 0.013 against 0.007 |
| 0.95 | 0.028 against 0.019 | 0.019 against 0.013 |

Every rate is at or below 0.05, so no finding.
