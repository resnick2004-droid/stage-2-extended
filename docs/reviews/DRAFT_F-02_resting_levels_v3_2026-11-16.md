# Red team: `prereg/DRAFT_F-02_resting_levels.md`, third version (family RL2), 2026-11-16

The red team (`.claude/agents/red-team.md`), read-only, in worktree `wt-levels` (branch `wt/wt-levels`) at master
ede4843 (TASK_QUEUE Q-41).

**The target.** The draft as committed in 255e13b and merged in 9fbaf6a: 992 lines, not pinned, not numbered. Its status
line says "second version" and E-022 calls it the third (N10).

**What I read it against:**
- `CHARTER.md` as amended (E-008, E-014, E-015); `DECISIONS.md` E-001..E-022; `CLAUDE.md`;
- `extended/walker.py`, `tests/test_walker_t13.py`, `tests/test_walker_mirror.py`;
- `.claude/skills/feature-rules/SKILL.md`, `.claude/skills/prereg-discipline/SKILL.md`;
- the previous review (`docs/reviews/DRAFT_F-02_resting_levels_2026-11-15.md`), and the version it reviewed (fc7747b),
  to see what each correction replaced.

In the vendored tree:
- Stage 2 D-201, D-212, D-266, D-271, D-272, D-308, D-313, D-555, D-558, D-580, D-586, D-587, D-588, D-592, D-604, D-667;
- `data/README.md` section 5; `config/windows.yaml`; `config/search_program_s3.yaml` (the gap rules);
  `config/fv3_corrected_portfolio.yaml` (P-14's sizing and routing block); `config/atlas_a3.yaml` (`news`);
  `config/sources/fomc_statements_2020_2024q1.csv`;
- `prereg/P-14_a3-brk30-cb20.md` (lines 36, 197-198, 229-237, 427) and `prereg/P-16_rc-s150-all-nr.md` (line 168);
- `propedge/campaign/sizing.py` (`_plain_size`);
- `results/stop_band.csv`; `results/u_value_map.csv` (sections `definitions`, `place_values`, `records_leaf`, `bar`).

**What I ran.** Two small synthetic scripts and a parser, one process at a time, one BLAS thread, in the session
scratchpad. The scratchpad is not durable, so their code is in Appendix A:
- `pdc_side.py`: the walker as committed, with a drift tied to the overnight move's sign and no level effect;
- `bounce.py`: the walker as committed, under T-13 (b)'s spread without its jumps;
- `leaf_agg.py`: a parser of `records_leaf`.

I also ran a word-bounded seed search. **Not done:** no read of `data/bars` or `data/atlas`, no engine run, no web, and
nothing written but this note.

**On the brief.** It names the items new in this version and asks whether each correction removes its defect. It states
no wanted conclusion, so I treated it as scope. E-022 records the lead's decisions: floor (ii)'s form, and the long-run
gate read on stage D's own design. I judged both from the text and the code, not from the row.

**Labels.** Severity is CHANGES-A-CONCLUSION (CAC), MATERIAL (MAT), MINOR or NOTE. A figure marked *synthetic* is
red-team arithmetic on simulated data and decides nothing. A figure quoted from `u_value_map.csv` is Stage 2's vendored
result, cited by section and row. An *illustration* is arithmetic on a made-up lift.

---

## Verdict

**Must be redrafted.** Two defects change declared rules (P1, V1). Neither is a reason to abandon the family. The
revised draft that Q-16's marks already require can carry both corrections.

**P1 (MATERIAL): C1' does not identify the prior close either.**
- At `pdc` the real level's side is set by the sign of the overnight move:
  - every real `break` there trades against that move;
  - every real `fade` trades with it.
- The placebo copies its side from the source day, so its side has nothing to do with the target day's overnight move.
- So the placebo-differenced lift D at `pdc` carries any effect of the overnight move's sign. That is the variable
  Stage 2's S3 gap rules read on this window.
- T-14 (c) plants a different effect and cannot catch this.
- *Synthetic:* with no level effect, D for a `pdc` break is about +9.7 points (se about 1.8) under a gap-reversal
  drift. A placebo on the target day's own side gives about 0.

**V1 (MATERIAL): C2 prices uses the design does not reach.**
- The value of each place is capped at the base's *forward* trade count. The value map also gives the *records* count,
  which is lower, and the draft gives no reason for taking the higher one.
- Those slots are the base's own trades, and the base takes them from 17:00 CT. The ticket exists only from 08:30.
- The funded opening is the only place an R = 3 pick can be priced, and the place with the largest value per use. Most
  openings are offered to the base before any ticket is live.
- So "the value is priced where the campaign spends it" (line 601) is not true. This version's waterfall (a sum over
  places) values a pick above the previous version's maximum over places.

**MINOR (each changes declared text):**
- T1: T-14 (c)'s generator is not specified, so the kill it decides is set after the pin.
- T2: T-13 (b)'s switch is stated at two granularities, and no consequence is declared if `rule_fill` itself favours the
  rule.
- V2: the 50-tick valuation's "conservative" is not established.
- S1: floor (ii)'s intention and the ticket's size omit the Combine's room cap that P-14's form includes.

**Corrections that remove their defects:**
- F1 at `on` and `pd` (those cells are gone);
- F2's look-ahead (every placebo input now predates the target day's `t_pub`);
- F3's band (the per-state edges match `stop_band.csv`);
- F4 for C2 (`rule_fill` is conservative for both side rules on a tick walk and under the bid-ask bounce: *synthetic*,
  `bounce.py`);
- F5, F6 (pending Q-40), F7, F9 and F10;
- the notes N1-N9.

F8 is corrected in its order but not in its quantities (V1).

## 1. Findings

| id | sev | finding (short) | remedy |
|---|---|---|---|
| P1 | **MAT** | `pdc`'s placebo copies the source day's side, so D at `pdc` carries any lift tied to the sign of the target day's overnight move -- the variable S3's `gap_glbx` / `gap_rth` read on this window. 9.2's "at these two kinds the placebo is a fair match" is false at `pdc`. The fade's level claim (9.7) inherits it. T-14 (c) does not plant it | `pdc`'s placebo on the target day's own side; T-14 (e), a planted overnight-sign drift of either sign, with (c)'s kill; correct 9.2 and 14 |
| V1 | **MAT** | Section 10's caps are `trades_per_year_forward` (the table's model), not the map's `trades_per_year_records`. Either way they count the base's own slots, which the base takes from 17:00 CT, before the 08:30 ticket exists. Place (c), the only place an R = 3 pick is priced, is mostly the base's. The waterfall (a sum) values a pick above the previous version's maximum. C2 can pass, and stage B can pick, on value the routing does not spend | cap at the records count at least; then either price reachable uses only (a direction-free count from the base's registered campaign), or change 11.2 so the routing reaches what is priced; declare whether a ticket may be an account's second trade of a session |
| T1 | MINOR | T-14 (c)'s generator is not specified: the overnight and regular-session volatility, the drift's size, duration and cap, the crossing, and the day count. A "fail" includes the planted effect being too weak to show in L. Its precision is relative to a planted size nobody fixed. So the kill is set by choices made after the pin | fix every generator parameter, the planted size and the day count (a pilot at a separate seed, as T-13 did) in the file; a refusal, not a kill, when L cannot see the plant |
| T2 | MINOR | The T-13 (b) switch is "for a side rule" in 6.1 and 7.1, but per "(side rule, stop, R)" in 17.5. Nothing follows if `rule_fill`'s own T-13 (b) interval lies on the rule's side, although `rule_fill` is pro-break for any overshoot past a tick | one granularity; if `rule_fill` 1 tick favours the rule, C2 (and a switched C1) is read at the next rung, or the (cell, R) is killed |
| V2 | MINOR | "Under the map's first-order model a `dv` is proportional to the dollar risk realised", so ρ errs low -- but the map's `dv` is the solver's value after a win less after a loss, which is not proportional to risk. The direction of the 50-tick approximation is not known | call it an approximation of unknown sign; report a sensitivity beside; or obtain the per-rung `dv` |
| S1 | MINOR | P-14's registered intention is "the allowance and the Combine's room cap applied" (P-14 line 36; the engine's `_plain_size`). The draft's intention and 11.2's size line omit the room cap. Floor (ii) cannot fail ("intended_capped = realised exactly"), so it is a build check, not a floor | define the size and the intention as the engine's (allowance, room cap, 45-tick floor); call floor (ii) a check |
| N1 | NOTE | Under T-13 (b)'s generator the bid-ask bounce dominates. Symmetric booking leans to `fade` and against `break` (*synthetic*, `bounce.py`), so the switch can only move `fade` cells, and only where T-13 (b) has the power to see the bias. The jump part, which is F4's pro-break overshoot, is generic and cannot switch `break` | -- (say so in 5.5) |
| N2 | NOTE | T-14 (c)'s two-sided criterion also kills for a conservative (negative) bias in D | state whether the intent is "matched" or "not anti-conservative" |
| N3 | NOTE | `rn100`'s distances are fixed in price, not in volatility units; scaling them by `A_E / A_D` mismatches the placebo whenever volatility drifts over the 21-252-session lag | copy `rn100` distances unscaled, or use a phase-shifted 100-point grid |
| N4 | NOTE | The draw order (kinds, then all days) puts `pd`'s judged-block draws before `on`'s choice-block draws. Choice-block invariance holds only because each draw's consumption depends on calendar-fixed pool sizes | one generator per (replicate, kind) |
| N5 | NOTE | Ambiguous pairs are booked kind `a`, not a flatten, so K2, F5's eligibility and C3 count them as resolved | read the rule side's resolution with the one-trade fill-bar rule |
| N6 | NOTE | "FOMC days carry no tickets" names no file. Stage 2's list includes the unscheduled 2020-03-03 statement, released at 10:00 a.m. ET, which was not known at 08:25 CT | name the file; scheduled meetings only, or the unscheduled ones from their release time |
| N7 | NOTE | The booking ladder's 2- and 4-tick rungs (9.6) are undefined for `fade`: `slip_ticks` does not move a limit's fill in the walker | define the fade rungs |
| N8 | NOTE | T-13 (a) is called "fast", but today's T-13 is marked `slow`. The consequences of a failed T-13 (a) or (c) are unstated. T-13 (b)'s walk (steps a minute, offsets, live times, cutoff, preset) is only "as today's" | mark the tier; state the consequences; fix the walk |
| N9 | NOTE | T-12's sentence (lines 818-822) is stale: the F-B and F-P drafts, the log and the previous review now name 20261930-39, as reserved for F-02 (references, not uses) | update; the build's T-12 must tell a reference from a use |
| N10 | NOTE | The version label: the file says "second version", E-022 says "third" | the pinning row names the commit and sha256 |
| N11 | NOTE | CHARTER section 4 still states D-212 (1)'s letter; E-022 (1) reads it in P-14's form for this family with no charter row | record the reading against the charter's words |
| N12 | NOTE | The Tier 1 news windows are cited from the audit note, not from `config/rules_extended.yaml` (no 13613539 entry). Nothing is loaded and the tickets avoid the windows by construction, so this is a reading | -- |
| N13 | NOTE | Section 2's row for this repository lists two red-team scripts; this review adds two more (synthetic, no bar) | add them |

## 2. The findings in detail

### P1 (MATERIAL) -- the prior close's placebo is not matched on the overnight move's sign

**Where.**
- 5.8, lines 293-299: the source day D and the placebo ticket ("side +1 for a resistance, -1 for a support", copied from
  D).
- 9.2, lines 537-538: "At these two kinds the placebo is a fair match: neither level is a range extreme".
- 9.7, line 569: the fade's level claim.
- 17.6 (c), lines 911-918: the planted null.
- Section 2, line 129: S3's row.

**The evidence.**
- *What the real level is.* On target day E let g be the overnight move, `P_ref` less the prior close.
  - The prior close is a resistance exactly when g < 0, and a support when g > 0. Its distance is |g|.
  - So a `break` at `pdc` fills only once the whole overnight move has been retraced, and it always trades against
    the move.
  - A `fade` at `pdc` always trades with the move.
- *What the placebo is.* It copies source day D's distance and **D's side**. D's side is set by D's own overnight move,
  which has nothing to do with E's. So about half of the placebo tickets on E are breakouts in the direction of E's
  overnight move (an extension), and half are partial or overshooting retracements.
- *What D then measures.* With no level effect at all, let the regular session's drift depend on the sign of the
  overnight move: drift μ x sign(g). Then:
  - the level's break lift is proportional to -μ;
  - the placebo's averages about zero;
  - so D is about -μ for `break` and about +μ for `fade`.
- *Why μ is not hypothetical here.* It is the effect S3 read on this window.
  - S3's `gap_glbx` takes "sign(open of the session's first bar - the previous trading day's last close at or before
    16:00 CT)", and `gap_rth` the 08:30 open against the same close (`config/search_program_s3.yaml` lines 25-26).
    Both were followed and faded against the coin twin (D-586, D-587).
  - D-588's Benjamini-Hochberg rejections were "every one on the follow side and all but one on the breakout and n-bar
    rules".
  - The draft's own section 2 says S3 "bears on `pdc`". The placebo does not use that.
- *Why `rn100` is different.* A day's `rn100` tickets are always one above and one below `P_ref`, at prices set by
  arithmetic. D's two sides are therefore E's two sides. The match there is by construction.
- *Why T-14 (c) cannot see it.* Its planted effect is a drift after every crossing that grows with the minutes since the
  price last stood there. It plants nothing tied to the overnight move's sign.

**A synthetic check** (`pdc_side.py`, Appendix A; 2,000 synthetic days per arm; the walker as committed, pair rule,
symmetric booking, the family's preset; S = 100 ticks, R = 1; drift ±0.002 a step on a one-tick walk of 400 steps a
minute, i.e. 0.8 ticks a minute in or against the overnight direction):

| arm | D, `break` at `pdc` (draft's placebo) | D, `break` (placebo on E's own side) | D, `fade` (draft's placebo) |
|---|---|---|---|
| null | +0.01 (se 1.92) | +0.71 (1.92) | -0.01 (1.92) |
| gap follow | -7.69 (2.04) | +1.65 (2.11) | **+7.69 (2.04)** |
| gap reversal | **+9.70 (1.81)** | +0.03 (1.70) | -9.70 (1.81) |

Points of win probability, *synthetic*. The drift is far larger than any NQ effect Stage 2 reports ("a genuine but tiny
direction effect", D-558). The table shows a sign, not a size.

**The failure it allows.**
- *Gap reversal on the judged block.* Suppose NQ's regular session tends to retrace the overnight move on 2024-2026, and
  no orders cluster at the prior close. Then:
  - a `break` pick at `pdc` has L > 0 and D > 0;
  - C1 and C1' pass;
  - section 13 records "a direction at the prior close ... beyond what a matched crossing carries";
  - the confirmation passes too, if the drift persists.
- *Gap follow, the sign S3's follow-side rejections point to.* Break's D is biased down, which is harmless. But a
  `fade` pick at `pdc`:
  - takes the drift as its lift ("a reversal after these crossings", 9.7, which is literally true);
  - also has a placebo-differenced lift that clears C1's level;
  - so 9.7's level claim is made on S3's effect, not on the level.

This is the same class of defect as F1, which removed `break` at `on` and `pd`.

**Remedy (changes 5.8, 9.2, 14 and 17.6).**
- For `pdc`, put the placebo ticket on **E's own pdc side**, with D's scaled distance. That side is known at E's
  `t_pub` from the prior close and `P_ref`, so there is no look-ahead. `rn100` is unchanged. For `pd`'s placebo, which
  is beside only, use E's own sides too.
- Add **T-14 (e)**: plant, with no level effect, a regular-session drift of each sign tied to the overnight move's sign,
  on the same synthetic paths as (c). At `pdc` break cells, D's interval must cover zero, under the same kill as (c).
  The draft's construction would fail it; the side-matched one passes (the table above).
- Correct the sentence in 9.2. Use the same placebo in the confirmation (section 14).

### V1 (MATERIAL) -- C2 prices the base's own slots, at the higher of the map's two counts

**Where.**
- Section 10, lines 582-601: the caps, the waterfall, and "Stage D routes each ticket in the same order (11.2), so the
  value is priced where the campaign spends it".
- 11.2, lines 638-654: the routing, the reservation "while the ticket rests", two tickets on one account.
- 11.6 (1), line 697: "the tickets' take-up is limited".

**The evidence.**

1. **Which count.** `u_value_map.csv` defines two:
   - `trades_per_year_forward`: "in the table's model";
   - `trades_per_year_records`: "U2's re-run of the registered gate campaign ... its router, budget and
     one-position-at-a-time rule limit them".

   Its `bar` section computes the bar on both bases. Section 10 takes `forward` without saying why. From
   `place_values`, forward against records:

   | base | (b) | (c) | (d) | (e) |
   |---|---|---|---|---|
   | p14 | 405.5 / 319.5 | 75.26 / 58.945 | 335.1 / 285.2 | 367.4 / 328.1 |
   | p16 | 427.3 / 299.8 | 77.55 / 52.2 | 267.2 / 209.7 | 480.8 / 355.8 |

   At the funded opening, the map's own bar rows (`best_place`, N = 104, `target=500`) read 0.466 points forward against
   0.595 records for `p14`, and 0.283 against 0.421 for `p16`.

2. **Whose slots.** Every cap counts the base's own trades in the place: the slots of the table's one-trade-a-session
   model (`leaf_max_trades`). The base takes them first:
   - P-14 enters "17:00 to 14:00 CT" (P-14 line 197), and P-16 offers "at every five-minute mark from 17:00 CT" (P-16
     line 168);
   - P-14's campaign allows "at most one trade an account a day" and one open position across all accounts (P-14
     lines 229-235);
   - the ticket exists only from 08:30, and 11.2 reserves an account only "while the ticket rests".

   So an account's slot is the ticket's only if no base entry reached that account first in the session, and the firm
   is flat at 08:30.

3. **The funded opening is the extreme case.** Place (c) is the funded account's first trade.
   - It is the only place priced for an R = 3 pick:
     - `records_leaf` shows the Combine's recorded leaves are all 1.5R (`p16`), or all but 52 leaf-days at 2R (`p14`)
       (`leaf_agg.py`);
     - the paid phase has no 3R leaf;
     - place (d) excludes 3R.
   - It has the largest `mean_dv`: $1,426 for `p14` and $2,277 for `p16` (`place_values`).
   - The account's first session opens with the base's overnight offers. The ticket gets the opening only when none of
     those reach the account before 08:30, and then only if it fills before its cutoff.
   - The valuation instead takes u_c = min(u, 75.26): every opening the table forecasts.

4. **This version's waterfall raises the value.** The previous version took the **maximum** over the places that ask R
   (its section 10). This one **sums** u_p x v(p) over places in priority order, which is at least the maximum. The F8
   correction made the routing follow the valuation's order. It did not make the valuation follow the routing's reach.

5. **Two gaps in 11.2.**
   - It does not say whether a ticket may be an account's second trade of a session.
   - It lets the second ticket of a kind fill on the same account after the first exits, which is a second trade in
     that session.

   The map's `dv` assumes one trade a session.

**The failure it allows** (an *illustration*, not a result). Take an R = 3 pick at 100 ticks (base `p14`) whose
`rule_fill` lift has its lower bound at 0.6 points, with u above 75.
- C2 = 0.6 x 75.26 x $1,426 / 100, about $644 a year: C2 holds.
- If the routing reaches a third of the openings, the value the campaign spends is about $215.
- The pick is CARRIED with "worth at least $500 a year" untrue.
- Stage B's ranking also puts every eligible R = 3 cell first, because (c)'s `dv` is the largest.

The same holds, less sharply, at (b), (d) and (e). This is the audit's D-3 ("what the screen valued is not what the
campaign spends") surviving in the quantities.

**Remedy (changes section 10 or 11.2).** Each of these is contract arithmetic or a direction-free count. None reads an
outcome of the tickets.
- (i) **At the least:** cap at `trades_per_year_records`, the count the map's records basis gives for the registered
  campaign's router and one-position rule.
- (ii) **Price only what the routing can reach.** Let cap'(p, R) be the base's recorded account-days a year on which, at
  08:30:
  - the account is in place p, asking R;
  - it has not yet traded that session;
  - the firm is flat.

  Multiply cap'(p, R) by the cell's choice-block fills per placed ticket-day. This is counted once from the base's
  registered campaign (section 5).
- (iii) **Or route to what is priced.** An account entering place (c) is reserved for the ticket from its activation
  until the ticket fills: the base's offers skip it. The cost to the base is read in the paired difference.

With any of these, declare whether a ticket may be an account's second trade of a session. Then line 601's sentence is
true.

### T1 (MINOR) -- T-14 (c) decides a kill on a generator the file does not fix

**Where.** Lines 911-918.

**The evidence.**
- *What is fixed.* "Synthetic multi-day paths with an overnight segment and a prior session", "a follow drift for a few
  minutes after every crossing, proportional to the log of the minutes since the price last stood there", and "enough
  synthetic days that its half-width is under a quarter of the planted lift's size on L". The seed is fixed.
- *What is not fixed:*
  - the overnight and regular-session volatilities and their ratio;
  - the drift's coefficient and its duration;
  - what "every crossing" is (each tick, each new price);
  - the minutes assigned to a price never visited;
  - how the prior close relates to the path;
  - the planted size;
  - the day count.

  All are chosen by the builder after the pin. At `pdc` the result depends on them, because the real level is where the
  price stood at 14:59 and the placebo is not (P1).
- *Two things the kill counts as a failure that are not failures of the statistic:*
  - "L's lower bound must be above zero". If the plant is too weak to show in L, the break cells are killed for the
    test's own weakness.
  - The precision is "a quarter of the planted lift's size on L". It is relative to a size nobody fixed, so the test's
    absolute resolution is free.

**The failure it allows.** After the pin, a builder can make T-14 (c) pass or fail with generator settings that the
declaration allows. That decides whether 6 of the 18 cells live. The data are synthetic, so no outcome can be fitted to,
but the kill is not determined by the file.

**Remedy.**
- Fix every generator parameter in the file, and the planted drift's size in points of L.
- Fix the day count from a pilot at a separate seed, read only for the interval's width, as T-13 did
  (`tests/test_walker_t13.py` lines 6-7).
- Make "L's bound not above zero" a refusal of the test, not a kill.
- Optionally, tie the precision to an absolute figure, as T-13 (c) does.

### T2 (MINOR) -- the T-13 (b) switch: two granularities, and no line on `rule_fill` itself

**Where.** Line 341 ("for a side rule"); line 453 ("sets each side rule's C1 booking"); lines 901-903 ("for that (side
rule, stop, R)"); line 903 ("`rule_fill`'s own reading is reported, expected conservative").

**The evidence.**
- *Granularity.* The switch decides C1's booking, which is the pass line's booking. Read per side rule, the file does not
  say how 9 (stop, R) intervals combine into one decision. Read per (side rule, stop, R), lines 341 and 453 are wrong.
- *No line on `rule_fill`.* On a walk with jumps, a stop entry fills in the walker at the stop's price plus a tick,
  while the market stands j ticks past the stop.
  - The symmetric booking's bias is about j / (S + T) toward `break`.
  - `rule_fill`'s is about (j - 1) / (S + T), still toward `break` for any j of 2 or more. (The arithmetic is in N1's
    frame; first-passage on a driftless walk.)

  So "conservative for both side rules" (line 260) holds only for overshoots of up to a tick. T-13 (b) reads
  `rule_fill`, and nothing follows if that reading lies on the rule's side.

**Remedy.**
- One granularity, per (side rule, stop, R), in 6.1, 7.1 and 17.5.
- If `rule_fill` 1 tick's T-13 (b) interval lies wholly on the rule's side, read C2 (and a switched C1) for that
  (side rule, stop, R) at the 2-tick rung, or kill it. Declared now.

### V2 (MINOR) -- the 50-tick ρ is not shown to err low

**Where.** Lines 594-597: "Under the map's first-order model a `dv` is proportional to the dollar risk realised ...
`mean_dv` x ρ is at most the 50-tick `dv` (conservative)".

**The evidence.**
- *What the map's `dv` is.* "The next state after the full win and after the full loss of the leaf at each rung (a loss
  to the floor ends the account, worth 0), each at the next session's value" (`definitions`, `dv`). It is the solver's
  value function evaluated twice, which is not linear in risk.
- *What "first-order" means there.* In the map it refers to the lift: "the table held fixed" (`dollars_per_trade`). It
  does not say `dv` is proportional to the risk.
- *Why the sign can go either way.* At the funded opening the 100-tick trade risks $1,000 and the 50-tick trade $500,
  both on 20 micros. Whether V(s + 1,500) - V(s - 500) is at least half of V(s + 3,000) - V(s - 1,000) depends on the
  value function's curvature.
- *What the average mostly is.* `p14`'s average is mostly its 100-tick rung, which trades "from 17:00 to the 12:00
  hour"; the 50-tick rung trades only "at 13:00 and 14:00" (P-14 lines 197-198). So `mean_dv` x ρ is essentially a linear
  rescaling of the 100-tick `dv`.

**The failure it allows.** A 50-tick pick's C2 is off by an unknown amount, of unknown sign.

**Remedy.** Call ρ an approximation of unknown sign. Report beside it the C2 value with ρ squared, or with the 50-tick
leaf-days valued at the funded opening's `dv` x ρ only. Or obtain a per-rung `dv` (section 5).

### S1 (MINOR) -- floor (ii)'s intention and the ticket's size omit the room cap

**Where.** Lines 416-420 and 653-654 (the size, "min(floor(leaf risk / (S x $0.50)), allowance)"); lines 422-436, 356
and 622-623 (floor (ii) "in P-14's registered form").

**The evidence.**
- *P-14's form includes the room cap.* P-14's `risk_denominator` is "the table's dollar risk at each trade's stop in
  whole micros, the allowance and the Combine's room cap applied" (P-14 line 36). Its campaign config says "intended:
  capped ... (D-313: and the room)" (`config/fv3_corrected_portfolio.yaml` line 146).
- *The engine applies it.* `_plain_size` cuts both the contracts and the capped intention to the room above the floor on
  a Combine (`sizing.py` line 596).
- *The draft omits it.* Its size line and its intention do not mention the room cap.
- *The floor cannot fail.* The same config says "intended_capped = realised exactly" (line 141). So under P-14's form,
  floor (ii) is identically met, up to contract rounding.
- *The engine also does more to a Combine trade:* the need-aware exit and the consistency cap (D-313). It will apply
  them to tickets merged into the base's day log.

**The failure it allows.**
- If T-15's toy days (line 926) or the ticket stream are built with the draft's size line, a Combine ticket can risk
  more than the room above the floor. Its stop-out then ends an attempt that the base's own sizing would have kept open.
- Or the engine re-sizes the ticket, and 11.2's line does not describe what is traded.

**Remedy.**
- Define the ticket's size and its intention as the engine's `_plain_size` at the pick's stop: the allowance, the
  Combine's room cap, the 45-tick floor.
- Say that floor (ii) cannot fail under that form, so it is a check of the build, not a floor.
- Say that the engine's need-aware exits and consistency cap act on tickets, and that this is P-14's convention.

### Notes

- **N1 (what T-13 (b) will do).** Take the generator as declared (line 896: a one-tick spread, prints at the ask on
  up-moves and at the bid on down-moves). Then every trigger print sits half a tick from the mid, and each barrier is
  reached by a print at the bid or the ask. The rule buys at a stop and sells at a limit, so the offsets fall
  differently on the two side rules. First-passage arithmetic on the mid gives, under symmetric booking:
  - a bias of about -0.5 / (S + T) for `break`, and +0.5 / (S + T) for `fade`.

  Under `rule_fill`, both biases are against the rule. *Synthetic* (`bounce.py`, S = 20 ticks so the bias shows on 1,500
  days; standard errors are not clustered by day, so they are understated):

  | R | break, symmetric | fade, symmetric | break, `rule_fill` | fade, `rule_fill` |
  |---|---|---|---|---|
  | 1 | -0.86 (0.16) | +0.66 (0.16) | -2.52 (0.17) | -1.03 (0.18) |
  | 3 | -0.38 (0.12) | +0.23 (0.12) | -1.25 (0.12) | -0.60 (0.12) |

  So the switch can move only `fade` cells: those at small S + T, where T-13 (b) has the power. The bias left where it
  does not switch is at most about the interval's half-width, far below any MDL.

  The jump component (2-8 ticks at 0.002 a step) is generic, not level-specific, and the bounce outweighs it. So `break`
  is never switched. F4's level-specific overshoot (a stop cascade jumping through the level within the minute) stays
  in `break`'s C1, and C2 absorbs a tick of it. Line 258's sentence should say so.
- **N2.** T-14 (c) asks D's **two-sided** interval to cover zero. A negative D under the plant is conservative for a
  break pass, but it would also kill. If "matched" is the intent, say so. If "not anti-conservative" is, make the test
  one-sided.
- **N3.** `rn100`'s real distances are fixed in price: uniform up to 400 ticks, whatever the volatility. The placebo
  multiplies D's by `A_E / A_D`. When the regular-session range in points drifts over a 21-252-session lag (it rises
  with NQ's price level), the placebo sits systematically farther or nearer than the real round numbers. Copy `rn100`'s
  distances unscaled, or use the 100-point grid shifted by a seeded phase. The scaling is right for `pd`, `on` and
  `pdc`, whose distances are set by the path.
- **N4.** Each replicate draws "kinds in table order" and, within a kind, every day of the window (lines 302-305). So
  `on`'s, `pdc`'s and `rn100`'s choice-block draws come after `pd`'s judged-block draws. Choice-block invariance holds
  because the number of draws per day, and their consumption, depend only on calendar-fixed pool sizes. A future change
  that let a judged-day draw depend on bar presence would break it. One generator per (replicate, kind) and block
  removes the coupling; T-3 checks only what its replacement perturbs.
- **N5.** The walker books an ambiguous pair as kind `a` (`walker.py` line 530) and counts only kind `f` as unresolved
  (lines 555-556). So K2 (lines 456-459), F5's eligibility (509-510) and C3 (547-549) treat every ambiguous fill as
  resolved.
  - A pair is ambiguous when its fill bar touched any of the four barriers. When the bar touched only the mirror's,
    the rule's own trade is still open and can reach the flatten.
  - The understatement is bounded by K5's 5 % times the share of those that later flatten.
  - Read the rule side's resolution with the one-trade fill-bar rule (`fill_bar="declared"` for the rule's own trade:
    feature-rules 3, "for one trade's own outcome only").
- **N6.** Line 196 ("FOMC days carry no tickets") names no calendar. Stage 2's list (`config/atlas_a3.yaml` `news`
  `fomc`) includes `config/sources/fomc_statements_2020_2024q1.csv`. That file holds the unscheduled 2020-03-03
  statement, "For release at 10:00 a.m. EST" (its line 11), which was not known at 08:25 CT that day. That is one day.
  Name the file, and void scheduled meetings only, or unscheduled ones only from their release time.
- **N7.** 9.6's ladder ("`rule_fill` at 2 and 4 ticks (the lift if the market at the fill stood that many ticks past the
  trigger)") is implementable for stops through `slip_ticks`, but not for limits: `fill_order` fills a limit at its
  price whatever `slip_ticks` is (`walker.py` lines 300-308). Define the fade rungs, for example the mirror moved k - 1
  ticks in its own favour.
- **N8.** Line 892 calls T-13 (a) "fast". Today's T-13 is `@pytest.mark.slow` (`tests/test_walker_t13.py` lines 151, 160,
  167). The file does not say what follows a failed T-13 (a) or (c): a kill, or a stop of the build. T-13 (b)'s walk is
  "as many synthetic days as today's T-13". Its steps a minute, ticket offsets, live times, cutoff and preset should be
  written out. Today's T-13 uses `DECLARED_F01`, not the family's preset.
- **N9.** The T-12 sentence (lines 818-822) says 20261930-39 were found only in the Q-21 brief. A word-bounded search
  today finds them also in `DECISIONS.md`, the previous review, `prereg/DRAFT_F-B_multifeature.md` line 613 and
  `prereg/DRAFT_F-P_payout_policy.md` line 659. The last two are references that reserve the range for F-02, not uses.
  The build's T-12 must tell a reference from a use.
- **N10.** Line 3 says "second version"; E-022 says "third version". The pinning row should name the commit and the
  sha256.
- **N11.** CHARTER section 4 (lines 121-122) states realised risk as D-212 (1)'s letter: "at least 90 % of trades within
  10 % of the state's risk in whole micros". E-022 (1) adopts P-14's form for this family, and R\* itself was registered
  under it, so the reading is consistent with how the row to beat was judged. But no row reads the charter's words that
  way. Record it, so that an audit reading the charter does not find floor (ii) in conflict with it. The letter's share
  is already reported beside (11.5 (3)).
- **N12.** Line 161 cites the Tier 1 windows from `docs/audits/phase0/E_rules_currency.md` C1. `config/rules_extended.yaml`
  has no 13613539 entry. Nothing is loaded and the tickets avoid the windows by construction, so this is a reading. If
  the build asserts the windows, the rules-verifier records them first.
- **N13.** Section 2's row for this repository: add this review's two synthetic scripts (no bar read).

## 3. Does each correction remove its defect?

| previous finding | the correction | removed? | why |
|---|---|---|---|
| F1 (C1' at `on` / `pd`) | `break` at `on`, `pd` dropped; T-14 (c) | **yes at `on` / `pd`** | the cells are gone before any read, and the count says so (16.4). C1' still does not identify at `pdc` (P1); T-14 (c) is underspecified (T1) |
| F2 (placebo look-ahead) | past-only sources 21-252 back; placebo in the shift test; n's are block totals | **yes** | every input (D's distances, `A_D`, `A_E`, E's `P_ref`) predates E's `t_pub`; the test covers it (17.3). New: the side at `pdc` (P1); draw coupling (N4); `rn100` scaling (N3) |
| F3 (band, form, `dv`) | band per state; P-14's form; ρ | **band yes; form declared; ρ partly** | the edges 82 / 134 / 45 match `stop_band.csv` (NQ rows); E-022 (1) declares the form; the room cap is omitted (S1); ρ's sign is not known (V2) |
| F4 (booking bias) | C2 at `rule_fill` for every pick; T-13 (b) | **yes for C2, to a tick** | `rule_fill` is conservative for both rules on a tick walk and under bounce (N1, *synthetic*); break's level-specific overshoot stays in C1 (N1); the switch's rules (T2) |
| F5 (rule-side resolution) | an eligibility line in B | **yes** | ambiguous fills count as resolved (N5) |
| F6 (early closes) | a pinned calendar | **yes, pending Q-40** | the FOMC source is unnamed (N6) |
| F7 (bound levels) | one 0.05 bound for both streams | **yes** | matches U1's verdict arm |
| F8 (valued vs spent) | one priority order | **no, in substance** | the order is shared, the quantities are not; the sum raised the value (V1) |
| F9 (prior exposure) | three rows | **yes** | -- |
| F10 (fade pass) | stated | **yes** | the fade's level claim at `pdc` is exposed (P1) |
| N1-N9 | as section 0.2 says | **yes** | N8: the skill now says `ts` is the bar's start |

## 4. What I tried that found nothing

- **Look-ahead in the levels and sides.**
  - The pieces: `P_ref` from bars stamped at or before 08:24; the void at the close of the bar stamped 08:29
    (`price_at(slot(8, 30))`, index 930); fills from the bar stamped 08:30 (`_window`'s `live + 1`).
  - `pd` and `pdc` from the previous day's bars stamped 08:30-14:59; `on` from 17:00 to 08:24.
  - `A_E` over the 20 full sessions before E.
  - All are closed by `t_pub`. The ticket goes live five minutes after (D-266).
- **The past-only placebo's inputs.** The source window is strictly before E; the source pool is calendar-defined; a
  source with no `P_ref` or no 14:59 bar yields no ticket. No input post-dates E's `t_pub`.
- **Roll and contract.** The charted contract is chosen on the previous day's volume (`data/README.md` section 5), so a
  roll is known in advance. `on`, `rn100` and `A` are same-day or roll-free; `pd` and `pdc` are voided on rolls.
- **The dropped cells as selection.**
  - They were dropped before any read, on Stage 2's recorded reads (D-555, D-592), and the decision is conservative.
  - The remaining `break` and `fade` cells at `pdc` and `rn100` still share their fills and stage-A gates, so the
    previous review's IUT check of stage B's min(t_L, t_D) still applies. A T-13 (b) switch can give a kind's two side
    rules different bookings; centring removes the handicap's mean, and the two rules stay almost perfectly negatively
    correlated.
- **The per-(cell, R) cutoffs.**
  - The cutoff is read from pooled rule-and-mirror counts under symmetric booking. These are reflection-invariant, so
    they read how far prices moved, not which way.
  - The grid is declared, the same cutoff is applied to the placebo and to stage D, and K1, K2 and K5 are read after it.
  - The per-R fill sets are honest: stage B's maximum takes each (cell, R) on its own fills.
  - Nothing beyond N5.
- **Count.** 54 = 2 kinds x 3 stops x 3 R x 2 signs + 2 kinds x 3 x 3 x 1. Cells: 18; killed cells are counted.
  0.05 / 132 at k = 11.
- **Floor (ii)'s arithmetic in 6.3.**
  - D-667's ladder in P-14's config gives 50 micros in the Combine, and 20 / 30 / 50 micros funded at 0 / 1,500 /
    2,000 (`config/fv3_corrected_portfolio.yaml` line 136).
  - `records_leaf` shows the funded 3R leaves are $2,000 (21,973 leaf-days for `p14`) and $1,500 (291), and the Combine
    is $2,000 1.5R on almost every day (`leaf_agg.py`).
  - So the funded opening carries $500, $1,000 and $1,500 at 50, 100 and 150 ticks, and the Combine's $2,000 leaf
    carries $1,250 at 50 ticks. 6.3 is right.
- **`rule_fill` as conservative.** On a tick walk and under the declared bounce, it handicaps both side rules: by
  1 / (S + T) of the pair on a tick walk; under bounce, -1.5 / (S + T) for `break` and -0.5 / (S + T) for `fade` (N1).
- **Seeds.** 20261930-39 are used only in this draft. The other mentions reserve the range (N9). My scratch seeds are
  outside the 2026xxxx space.
- **Leakage across blocks.**
  - Trades open and close in one session.
  - The stationary bootstrap reads choice sessions only.
  - T-3 replaces every bar from 2024-01-02 and compares stage A's and B's outputs, the placebo's statistics included.
  - Placebo sources for early-2024 targets are 2023 distances, which carry no outcome.
  - The value map spans 2020-2026 but carries no level direction (the audit's N-4, accepted before).
- **News.** Tickets go live at 08:30 CT, outside the 07:25-07:35 CT windows. FOMC days, the 12:55-13:05 and 13:25-13:35
  windows, carry none. Pending orders never meet a window.
- **The stage-D bound level.** One 0.05 bound for both streams; the identity at the registered level first (11.5).
- **Re-declaration escape.** Section 13 binds a later family on these levels to data this family did not read.

## 5. What I could not check, and the experiments that would settle it

- **What the routing reaches** (V1). This needs the base's registered campaign with a per-account-day log at 08:30:
  - the place and leaf R;
  - whether the account has traded that session;
  - whether the firm is flat.

  One run of P-14's registered gate at its seed (or U2's 100-path bound-arm re-run), through an adapter in `extended/`,
  reading counts only. It is direction-free for the tickets. Cost: about E-004's P-14 run (minutes, one worker), under
  the run lock. The same for P-16.
- **The sign and size of the overnight-move effect on this window** (P1). This is in Stage 2's
  `results/s3_event_kinds.csv` (the `gap_glbx` and `gap_rth` rows), which is not vendored. Vendoring it is a new
  snapshot under a new row, and reading it is a prior-exposure read for section 2. P1's remedy does not need it.
- **T-14 (c) and the proposed (e) on a fixed generator** (T1, P1). Synthetic, minutes of CPU, well under 500 MB.
- **A per-rung `dv`** (V2). This needs the solver's transition at each rung on the $50K table (D-667's tooling).
- **Q-16's statistic**, and whether it covers C1''s per-session two-sample form. It is pending; the draft blocks the pin
  on it.

---

## Appendix A. The scripts (scratchpad copies are not durable)

`leaf_agg.py` -- `records_leaf` aggregated by (base, phase, leaf R), with the leaf risks' day counts:

```python
import csv, re, sys, collections
path = sys.argv[1]
agg = collections.defaultdict(float); cnt = collections.defaultdict(float)
risk = collections.defaultdict(lambda: collections.defaultdict(float))
with open(path, newline="") as f:
    for r in csv.reader(f):
        if not r or r[0] != "records_leaf":
            continue
        base, phase, state = r[1], r[2], r[3]
        leaf = state.split("/")[-1].strip()
        m = re.search(r"\$([\d,]+) ([\d.]+)R", leaf)
        R = m.group(2) if m else leaf
        key = (base, phase, R)
        agg[key] += float(r[5]); cnt[key] += float(r[6] or 0)
        if m:
            risk[key][m.group(1)] += float(r[6] or 0)
for k in sorted(agg):
    print(k, round(agg[k], 4), int(cnt[k]), dict(risk[k]))
```

Its output on `vendor/stage2/results/u_value_map.csv` (2026-11-16), the rows used above:
- `('p14', 'combine', '1.5') 0.9993 69311` and `('p14', 'combine', '2') 0.0007 52`;
- `('p14', 'funded', '3') 0.2946 22276 {'1,500': 291, '2,000': 21973, '1,000': 12}`;
- `p14` paid: R 1, 1.5, 2 and 2.5 only;
- `('p16', 'combine', '1.5') 1.0 78144`; `('p16', 'funded', '3') 0.2971 18788`;
- `p16` paid: no 3R.

`pdc_side.py` -- P1's check:

```python
import sys
import numpy as np
sys.path.insert(0, r"C:\Users\resni\AppData\Local\stage2-extended-wt\wt-levels")
from extended import walker as W

SEED, DAYS, STEPS = 515151, 2000, 400
S, RRS, SD_ON = 100, (1.0,), 200
LIVE, CUT = W.slot(8, 30), W.slot(14, 0)
PRESET = W.Rules("f02_preset", W.FLAT_ENTRY, "worst_less_two", False)
FIRST = LIVE + 1; M = W.C_FLAT - FIRST + 1; N = W.C_FLAT + 1; BASE = 80000

def day(rng, drift):
    st = np.where(rng.random(M * STEPS) < 0.5 * (1.0 + drift), 1, -1).astype(np.int32)
    path = (BASE + np.cumsum(st)).reshape(M, STEPS)
    o = np.full(N, float(BASE)); h = o.copy(); l = o.copy(); c = o.copy()
    close = path[:, -1].astype(float); opens = np.concatenate([[float(BASE)], close[:-1]])
    o[FIRST:], c[FIRST:] = opens, close
    h[FIRST:] = np.maximum(path.max(axis=1), opens); l[FIRST:] = np.minimum(path.min(axis=1), opens)
    for x in (o, h, l, c): x[0] = np.nan
    return o * W.TICK, h * W.TICK, l * W.TICK, c * W.TICK

def w_of(rule, side_level, dist, bars):          # side_level +1 a resistance at P_ref + dist, -1 a support
    if dist < 1: return None
    lvl = (BASE + side_level * dist) * W.TICK
    od = (W.Order(W.STOP_ENTRY, side_level, LIVE, lvl + side_level * W.TICK, CUT) if rule == "break"
          else W.Order(W.LIMIT_ENTRY, -side_level, LIVE, lvl, CUT))
    t = W.trade(od, *bars, S, RRS, rules=PRESET, fill_bar="pair", mirror_booking="symmetric")
    if t.fill.status != "filled": return None
    return 0.5 * (float(t.rule.win[0]) - float(t.mirror.win[0]))

def run(delta, seed):
    rng = np.random.default_rng(seed)
    acc = {k: [] for k in ("L_break", "P_break", "Pm_break", "L_fade", "P_fade", "Pm_fade")}
    for _ in range(DAYS):
        gE = int(round(rng.normal(0, SD_ON))); gD = int(round(rng.normal(0, SD_ON)))
        sE = 1 if gE > 0 else -1; sD = 1 if gD > 0 else -1
        bars = day(rng, delta * sE)                # drift follows (delta > 0) or reverses the overnight sign
        for rule in ("break", "fade"):
            for key, side, dist in ((f"L_{rule}", -sE, abs(gE)),       # the real pdc: side -sign(g_E)
                                    (f"P_{rule}", -sD, abs(gD)),       # the draft's placebo: D's side
                                    (f"Pm_{rule}", -sE, abs(gD))):     # the side-matched placebo
                w = w_of(rule, side, dist, bars)
                if w is not None: acc[key].append(w)
    return {k: (len(v), 100 * np.mean(v), 100 * np.std(v, ddof=1) / np.sqrt(len(v))) for k, v in acc.items()}

for i, delta in enumerate((0.0, +0.002, -0.002)):
    r = run(delta, SEED + i)
    for rule in ("break", "fade"):
        n1, m1, s1 = r[f"L_{rule}"]
        for p in ("P", "Pm"):
            n2, m2, s2 = r[f"{p}_{rule}"]
            print(delta, rule, p, round(m1 - m2, 2), round(float(np.hypot(s1, s2)), 2))
```

Output (2026-11-16, 46 s). Each line is the level's lift; the draft's placebo; the side-matched placebo:
- null:
  - break: L -0.82 (se 1.35), P -0.83 (1.36), Pm -1.53 (1.36);
  - fade: the negatives.
- gap follow (+0.002):
  - break: L -8.69 (1.51) on 1,047 fills, P -1.00 (1.38) on 1,299, Pm -10.34 (1.48) on 1,078;
  - fade: the negatives.
- gap reversal (-0.002):
  - break: L +9.36 (1.20) on 1,661, P -0.34 (1.36) on 1,333, Pm +9.33 (1.20) on 1,640;
  - fade: the negatives.

The differences are in P1's table. The level and its placebos share each synthetic day's path, so the hypot standard
error is approximate.

`bounce.py` -- N1's check (T-13 (b)'s spread without its jumps):

```python
import sys
import numpy as np
sys.path.insert(0, r"C:\Users\resni\AppData\Local\stage2-extended-wt\wt-levels")
from extended import walker as W

SEED, DAYS, STEPS = 616161, 1500, 100
S, RRS = 20, (1.0, 3.0)
LIVES = tuple(range(W.slot(8, 30), W.slot(13, 30), 5)); CUT = W.slot(14, 0)
PRESET = W.Rules("f02_preset", W.FLAT_ENTRY, "worst_less_two", False)
FIRST = W.slot(8, 30) + 1; M = W.C_FLAT - FIRST + 1; N = W.C_FLAT + 1; BASE = 80000

def day(rng):
    st = np.where(rng.random(M * STEPS) < 0.5, 1, -1).astype(np.int64)
    mid2 = 2 * BASE + 1 + 2 * np.cumsum(st)          # twice the mid (a half-tick mid)
    prints = (mid2 + st) // 2                         # the ask on an up-move, the bid on a down-move
    p = prints.reshape(M, STEPS).astype(float)
    o = np.full(N, float(BASE)); h = o.copy(); l = o.copy(); c = o.copy()
    close = p[:, -1]; opens = np.concatenate([[float(BASE)], close[:-1]])
    o[FIRST:], c[FIRST:] = opens, close
    h[FIRST:] = np.maximum(p.max(axis=1), opens); l[FIRST:] = np.minimum(p.min(axis=1), opens)
    for x in (o, h, l, c): x[0] = np.nan
    return o * W.TICK, h * W.TICK, l * W.TICK, c * W.TICK

rng = np.random.default_rng(SEED); bl = W.brackets((S,), RRS)
acc = {(ru, bk): [] for ru in ("break", "fade") for bk in ("symmetric", "rule_fill")}
for _ in range(DAYS):
    o, h, l, c = day(rng); fills = {"break": [], "fade": []}
    for t in LIVES:
        ref = c[t]
        for ru in ("break", "fade"):
            above = bool(rng.random() < 0.5); k = int(rng.integers(20, 61))
            price = ref + (k if above else -k) * W.TICK
            od = (W.Order(W.STOP_ENTRY, +1 if above else -1, t, price, CUT) if ru == "break"
                  else W.Order(W.LIMIT_ENTRY, -1 if above else +1, t, price, CUT))
            f = W.fill_order(od, o, h, l, c, rules=PRESET)
            if f.status == "filled": fills[ru].append((f, od.side))
    for ru in ("break", "fade"):
        if not fills[ru]: continue
        fb = [f.bar for f, _ in fills[ru]]
        for bk in ("symmetric", "rule_fill"):
            res = W.walk_pair(o, h, l, c, fb, [f.price for f, _ in fills[ru]],
                              [W.mirror_price(f, bk) for f, _ in fills[ru]], [s for _, s in fills[ru]],
                              True, bl, rules=PRESET, fill_bar="pair")
            acc[(ru, bk)].append(0.5 * ((res["rule"]["kind"] == W.TARGET).astype(float)
                                        - (res["mirror"]["kind"] == W.TARGET).astype(float)))
for (ru, bk), parts in acc.items():
    x = np.concatenate(parts, axis=0)
    for b, R in enumerate(RRS):
        print(ru, bk, R, len(x), round(100 * x[:, b].mean(), 2), round(100 * x[:, b].std(ddof=1) / np.sqrt(len(x)), 2))
```

Output (2026-11-16, 38 s): 66,924 `break` fills and 66,397 `fade` fills; the lifts are in N1's table. The standard
errors are not clustered by day; tickets on one day overlap.
