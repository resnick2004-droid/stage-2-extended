# Phase 0 audit, track D: the research protocol and F-01, read as a red team

Written 2026-11-15/16 by audit track D (TASK_QUEUE Q-06), read-only. Repository at `master` 1171c7d; F-01 as pinned by
E-003 (sha256 `535033f2...`); Stage 2 vendored at f1b42e2 under `vendor/stage2/`.

**Read:** `CHARTER.md`, `CLAUDE.md`, `DECISIONS.md` (E-001..E-005), `DIRECTIVE.md`, `TASK_QUEUE.md`, `STATUS.md`,
`docs/BOOTSTRAP_NEW_REPO_ORCHESTRATOR.md` (Parts 5-7), `docs/briefs/Q-10_2026-11-15.md`, `.claude/skills/feature-rules`
and `merge-checklist`, `prereg/F-01_resting_order_level_atlas.md`, `identity/stage2_identity.py`, `tests/*`,
`scripts/hooks/protect_vendor.py`, `.claude/settings.json`; in the vendored tree: the handoff, `docs/RESEARCH_PROTOCOL.md`,
`prereg/FAMILY_TEMPLATE.md`, `prereg/README.md`, `prereg/REGISTRY.md`, `prereg/P-14_*.md` and `P-16_*.md` (parts),
`prereg/DRAFT_P16_confirmation.md` (parts), `data/README.md`, `config/windows.yaml`, `config/atlas_a3.yaml`,
`config/orb5_grid.yaml`, `config/search_program*.yaml`, decision rows D-107, D-189, D-266, D-275, D-277, D-278, D-281,
D-308, D-419, D-461, D-558, D-568, D-578, D-580, D-588, D-589, D-592, D-620 (G2), D-621, D-663;
`propedge/research/u_select.py`, `user_journey.py` (`block_indices`, `paired_interval`), `user_drivers.py` (constants),
`fv3_rung_walk.py` (docstring), `scripts/atlas_a3.py` (walk and fee functions), `propedge/reporting/results.py` (fields);
result files `u_value_map.csv` (+ manifest), `u_budget.csv`, `u_resolve.csv`, `u_xfa_day_budget.csv` (rows named below).
**Not read:** the bars and atlas, the other tracks' notes (A, B, C, E), the worktree branches. No engine was run.

**Figures.** Every figure from Stage 2 below names its file, section and row. Figures marked *synthetic* are audit
arithmetic from two small seeded simulations on synthetic random walks (Appendices A and B, code in full, so they can be
re-run); they are not results of this repository and decide nothing until a decision row adopts a remedy.

**Severity.** CHANGES-A-CONCLUSION -- a recorded conclusion, or the meaning of a verdict a declared procedure would
issue, is wrong as written. MATERIAL -- a declared procedure can reach a wrong or uninformative answer with real
probability, or breaks a binding rule. MINOR -- a gap or ambiguity with a small or bounded effect. NOTE -- worth
recording, no defect.
**Remedy classes for F-01:** NEW FAMILY (changes a declared rule: F-01 withdrawn, a corrected family declared under a
new row) or READING (a clarification recorded in the build's row; changes no declared rule). Protocol defects take a
PROTOCOL ROW (a decision row of this repository), a TEST or a HOOK.

---

## 0. Summary

### Verdict on F-01

**Withdraw F-01 and declare a corrected family.** Four defects change declared rules and cannot be readings: the
statistic's fill-bar rule (D-1), the grid against Stage 2's closures (D-2), stage D's design (D-3) and K2's per-year
line (D-8); stage D also rests on the selection rule's bound, which does not deliver its level (P-1). The other F-01
defects are readings and should be written into the corrected family's text. On whether the withdrawal spends k = 10,
see section 1.5 (e): it need not, under conditions that hold today, but the rule must be fixed now, once.

**Urgent:** Q-10 (`wt/wt-levels`) is building F-01's walk rules and its mirror test now (`docs/briefs/Q-10_2026-11-15.md`),
and the house label rule copies the fill-bar rule (`.claude/skills/feature-rules/SKILL.md` section 3). D-1 changes both.
The walker can be kept, with the fill-bar settlement made a parameter, and the mirror test strengthened as T-13 says.

### Findings

| id | sev | finding | remedy |
|---|---|---|---|
| P-1 | **CHANGES-A-CONCLUSION** | Stage 2 D-621 (3)(i)'s bound -- the percentile of a 2,000-draw moving-block bootstrap, 63-session blocks, about nine blocks of judged starts -- does not deliver the family level. On synthetic nulls it rejects at 0.8 % to 3.4 % where the nominal level is 0.05/110, about 0.045 % (18 to 75 times), and its realised level does not fall with k, so "at most 5 % however long it runs" fails. No recorded closure flips; any CARRIED would not mean what it says | PROTOCOL ROW (amends E-001) + TEST |
| P-2 | **CHANGES-A-CONCLUSION** | E-001 continues program U's budget because "the data, the row to beat and the researcher are the same" -- an argument that binds Stage 2's program S equally (D-578: four batches on the same NQ window, 0.04 of its own 5 % spent). Programs S and U alone spent at least 0.085 nominally on this window. The charter's "the program spends at most 5 %" is false of the researcher | PROTOCOL ROW |
| D-1 | MATERIAL | F-01's fill-bar rule (a stop touch counts, a target touch does not) is applied to the rule and to its mirror, but the price approaches the fill from the rule's side, so the rule penalises the trade whose stop lies on the approach side: the **break lift is biased down, the fade lift up**, by at most about half the share of fills whose fill bar touches either trade's stop or target. Synthetic: about -1.8 / +1.6 points when about a quarter of fill bars span the stop | NEW FAMILY |
| D-2 | MATERIAL | Prior exposure and closed branches: the `or30` cells lie in the opening-range branch Stage 2 closed for good (D-275, D-277, D-281: "whether any later hypothesis is genuinely different is the operator's call"). F-01 line 23 ("nothing in Stage 2 entered at the level itself") is false (ORB5's stop at the range's edge with a `rest` policy; ORB6's limit at the broken edge). The break cells pick up the follow-the-breakout effect that Stage 2 read three times on this window, concentrated in the judged block, and ruled a lead for unread data only (D-580, D-588, D-592); F-01 line 27 re-opens exactly that | NEW FAMILY |
| D-3 | MATERIAL | Stage D does not identify the tickets' value: its base (P-16) is below R\* = P-14 on P; tickets compete first-come against an offer at every admitted five-minute mark, and P-16 already routes about 3 % of its own offers, so few tickets would take a position; the table sets R by account state, not the pick's R; 25-point picks are valued on P-14's table and campaigned in P-16's; resting tickets in a firm that holds a P-16 position need a cancel-and-replace cycle the design does not model (otherwise a tier-1 hedge) | NEW FAMILY |
| D-4 | MATERIAL | Power: C1's minimum detectable lift is about 4 to 11 points of win probability for 300 to 900 judged fills; the value map's bar for $500 a year is about 0.3 to 2.5 points. The family can find only effects far larger than anything Stage 2 found (D-558: "genuine but tiny"); a CLOSED says "no lift above the MDL", not "no lift" | READING + PROTOCOL ROW |
| D-5 | MATERIAL | Look-ahead and latency at `t_pub`: `on` and `rn100` read "the 08:25 bar's close", which closes at 08:26 by the store's bar-start stamps and by F-01's own naming (`pdc` = "the 14:59 bar's close"); every ticket's side is set by "the price at `t_live`" (line 58), after `t_pub`, which contradicts the void rule (line 75) and section 2; test 7.2's wording can pass with both | READING |
| D-6 | MATERIAL | The declared confirmation (NQ from 2026-07-17) would be NQ's fourth confirmation under Stage 2 D-107 (the operator's decision, not only a purchase) and is the window Stage 2's own P-16 draft targets; if read first for P-16, a P-16-based design cannot be confirmed there cleanly | READING now; PROTOCOL ROW |
| P-3 | MATERIAL | The judged block is not fresh for direction (nine program-U families, program S's span guard, every atlas, P-05/06/10's window); it still guards within-family choice, not the choice of family; the protocol says nothing about prior exposure | PROTOCOL ROW + lint TEST |
| P-4 | MATERIAL | Identities and tests that can pass while the result is wrong (section 1.4: eight cases) | TESTS |
| P-5 | MATERIAL | Holes (a)-(f) are guarded by prose and the lead's checklist, not by tests or hooks (section 1.5) | RULES, TESTS, HOOKS (Part 3) |
| D-7 | MINOR | Count: 20 cells declared, 60 (cell, R) hypotheses selected over | READING |
| D-8 | MINOR | K2 allows 10 % unresolved in a year; Stage 2 D-212/D-308 binds 5 % per year | NEW FAMILY |
| D-9 | MINOR | K3 cannot fail in this walk (a stop exit slips adversely, so realised risk is never below intended) | READING |
| D-10 | MINOR | Stage A, declared outcome-free, reads an outcome (K4's touched-but-unfilled fades) and the judged block (planning's fill counts) | READING |
| D-11 | MINOR | Cross-day levels (`pd`, `pdc`) on roll days are the old contract's prices; the 2025-06-30/07-01 seam and early closes leave levels undefined | READING |
| D-12 | MINOR | D-271's drift-matched baseline and per-era report, a placebo-level control and D-663's stress readings are not declared | READING (beside) |
| D-13 | MINOR | Booking: the mirror is booked at the rule's fill price (about 0.5 point per tick at 100 ticks, R = 1 -- the value bar's scale); in fast markets "stop plus one tick" books the break better than the market, a bias that favours `break` | READING (stress beside); NEW FAMILY for the rule |
| D-14 | MINOR | Stage B's bootstrap type and centering, and the estimator C1 bounds (fill mean or block mean), are unstated | READING |
| D-15 | MINOR | No fixed / searched / dropped table (CLAUDE.md); silent drops (VWAP bands, swing points, other range lengths, R 2 and 2.5) | READING |
| P-6 | MINOR | `tests/test_stage2_identity.py` skips without data; "k" means both the family number and a trial count | TEST; wording |
| N-1 | NOTE | C1 then D at 0.05/110 is fixed-sequence testing: no double spending (given P-1 fixed); C2 at 95 % is a conjunctive gate, not a claim | -- |
| N-2 | NOTE | Seed 20261901, "used nowhere else", is Stage 2's `user_drivers.CLUSTER_SEED` | READING; TEST T-12 |
| N-3 | NOTE | "Flattened at that bar's close" (15:10 bar) closes 15:11; P-16's walker convention governs the identity | READING |
| N-4 | NOTE | The value map is first-order and "unreliable far from zero"; any pick passing C1 is far from zero | -- |
| N-5 | NOTE | Target limits fill on a touch; entry limits need a trade-through (symmetric for the lift) | -- |
| N-6 | NOTE | Tickets rest through 09:00 CT releases outside the BLS list; consistent with Stage 2's news rule | -- |

---

## Part 1. The protocol

### 1.1 Multiple-testing control

**The schedule is coherent as a union bound.** Family k at 0.05 / (k (k + 1)): the levels telescope to 0.05 (1 - 1/(K+1))
< 0.05. Starting this repository at k = 10 leaves 0.005 in total for every later family (sum over k >= 10 of
0.05/(k(k+1)) = 0.05/10). The bound needs one thing: each family's test really holds its nominal level. Two things break
that, and one framing claim is wrong.

**P-2 (CHANGES-A-CONCLUSION): the budget is not one 5 % for the researcher.** E-001 (a) refuses a fresh budget because
"the data, the row to beat and the researcher are the same". Stage 2 ran two such programs in parallel on the same NQ
development window: program S (D-578, `config/search_program.yaml` `family_wise_budget: 0.05  # across ALL batches,
ever`; batches S1-S4 at 0.025, 0.00833, 0.00417 and 0.0025 -- `search_program.yaml`, `_s3.yaml` line 10, `_s4.yaml`
line 11) and program U (D-621 (5); nine families, the ninth at 0.05/90, `u_resolve.csv` section `judged`, column
`level`). Together that is at least 0.085 nominally on this window, before D-189's registered tests and the earlier atlas
families. E-001's own argument therefore implies the 5 % is already spent; E-001 (a), CHARTER section 3 and D-621 (5)
("so the program spends at most 5 % however long it runs") are not true of the researcher. F-01's stage C is, in method,
a program-S test (a per-fill lift over the coin twin, D-578 (3)). Putting it in program U (0.05/110) is stricter than
program S's next batch would be (0.05/30), so E-001's choice is not lenient: the defect is the claim, not the number.
**Remedy:** a protocol row that (1) keeps program U's numbering for continuity, (2) lists every family and batch ever
declared on the NQ development window with its level (a ledger, R-1), and (3) states plainly that the development-stage
level is a screening threshold and that **the decision is carried by one confirmation on unread data** -- D-189's own
words: "the confirmation window carries the decision, never a smaller N".

**P-1 (CHANGES-A-CONCLUSION): the selection rule's bound is anti-conservative by an order of magnitude at family
levels.** D-621 (3)(i) is computed by `u_select.p_difference` (`vendor/stage2/propedge/research/u_select.py` lines
422-440): `user_journey.paired_interval` at alpha = 2 x level, a non-circular moving-block bootstrap with blocks of 63
starts (line 125), 2,000 draws (`user_journey.py` line 77), the lower limit `np.percentile(boot, 100 x level)`. The
judged block of start days runs 2024-01-02 to 2026-04-21 (`u_budget.csv`, section `judged`, `first_date`/`last_date`):
about 578 starts, about nine 63-start blocks. Two things go wrong at small levels: 2,000 x 0.05/110 is less than one
draw, so the "quantile" is an interpolation between the two smallest draws; and with about nine blocks the bootstrap's
spread behaves like a variance estimate with few degrees of freedom, read in a normal-like tail. **Synthetic nulls**
(Appendix A: mean-zero series of 578 starts, the exact resampling of `block_indices`, the rule "difference > 0 and
lower limit > 0"):

| null series | nominal 0.05/110 (0.045 %) | nominal 0.05/90 | nominal 0.5 % | nominal 2.5 % |
|---|---|---|---|---|
| iid | 0.80 % | 0.85 % | 2.1 % | 5.4 % |
| moving average over 21 starts | 1.0 % | 1.1 % | 2.5 % | 5.9 % |
| over 42 starts | 2.1 % | 2.2 % | 3.9 % | 8.3 % |
| over 63 starts (a month-3 window) | 3.4 % | 3.6 % | 5.9 % | 11.0 % |
| *for comparison:* Student-t on the 9 non-overlapping 63-start block means, df 8 (MA 21 / MA 63) | 0.055 % / 0.13 % | -- | 0.74 % / 1.3 % | 3.3 % / 4.9 % |

*Synthetic; 4,000 replications per row (20,000 for the t rows).* The realised level has a floor near 1 % that does not
shrink with k, so the sum over families diverges instead of staying under 5 %. **Impact:** no recorded closure flips --
the nine program-U families closed with their judged P below P-14's (`u_budget.csv`, `u_resolve.csv`, section `judged`,
column `difference` negative) -- but a CARRIED under this bound would not carry its stated level, and F-01's stage D and
every later family use it. **Remedy (before any stage D is read):** a protocol row that replaces the percentile bound by
one whose level is calibrated -- for example Student-t on non-overlapping horizon-length block means (df = blocks - 1)
-- or a studentised bootstrap with draws of at least 20 / level, plus a calibration test (T-6). CHARTER section 3 uses
D-621 (3) "unchanged", so the row names E-001. D-663 records a similar gap for the gate's own bound ("never calibrated
on these data at 0.05/N").

**Within the family (no defect).** Stage B's studentised maximum over the 60 (cell, R) pairs at one-sided 0.05 on
2020-2023 is a selection gate, not a spend: one pick goes to a judged block not used to choose it. That is valid when
the blocks are close to independent; they are (the first judged day's levels read the last choice session's bars, no
outcome). Because `break` and `fade` at one level fill on the same events (both need a trade at the level plus a tick,
F-01 lines 66-67), the 20 cells are 10 level-stop pairs read with a sign; the bootstrap's joint maximum covers that, as
E-003 (d) says.

**N-1, stages C and D at 0.05/110 (the family's real error rate).** C1 and then D, each at the same level, in a fixed
order, with D read only if C1 passes, is fixed-sequence testing: it controls the family-wise error for both hypotheses
at the level. Under the global null a false carry needs C1's false pass (at most the level; C1 is a Student-t bound on
about thirty 21-session block means, df about 29, close to valid). Under the partial null -- a real lift, no gain over
R\* -- the error is D's realised level, which is P-1's problem, not double spending. C2 is read at the 95 % bound: a
conjunctive decision gate, never a claim, so it does not inflate anything; it should not be cited as a finding at 95 %.
So the family's real error rate is the larger of C1's level and D's realised level; with P-1 unfixed, the second can be
around a percent, two orders above the nominal 0.045 %, though D-621's other guards ((ii)-(iv), (4)(e)) lower it.

### 1.2 The walk-forward and the judged block (P-3)

**What has read 2024-01-02 to 2026-07-16 already:** program U's nine families judged on starts from 2024 (`u_*.csv`
sections `judged`); program S's span guard on 2024-2026 alone (D-578 (2)), where the follow-the-breakout lift sat --
D-580 (5) "the gain is the late years'", D-588 "the gain is concentrated in 2024-2026", D-589 caveat (1); D-592: "a
development-data observation read three times on the same NQ window; re-testing it on that window would reuse hypotheses
already seen, so it is recorded as a lead for unread data, not as a new batch"; every atlas family over 2020-2026 (A3's
`orb_rth5/15/30` followed and faded, `config/atlas_a3.yaml` `development.end: 2026-07-16`); P-05, P-06 and P-10's
confirmation reads of 2025-07-01 to 2026-07-16 (`config/windows.yaml`: "a new NQ model may be built on it, never
confirmed on it").

**Is it still a fair judging block?** For choice *within* a family, yes: the pick is mechanical on 2020-2023 and judged
on 2024-2026. For the choice *of* a family, no: the families are designed after reading what 2024-2026 did. Where a
mechanism's judged-block sign is already known (follow the break: up in 2024-2026), a pass on the judged block is
expected and carries little information; the union bound in 1.1 assumes a hypothesis fixed before the data, and that
assumption fails when hypotheses are chosen after reading the same block (adaptive reuse). It is late development, not
out of sample.

**What the protocol needs to say** (R-3, R-4): (1) the judged block is late development, and a CARRIED design is a
development finding whose evidence is its confirmation; (2) every family file carries a **prior-exposure** section --
the Stage 2 and E rows that read the family's mechanism on either block, with the sign and span each found -- before it
is pinned; (3) a cell inside a branch Stage 2 closed for good (D-277's boundary) is excluded unless a row argues it is
genuinely different, and where Stage 2 reserved that call to the operator (D-281 (3)) it is excluded by default; (4) a
cell whose mechanism Stage 2 recorded as "a lead for unread data" (D-592) is judged only by a statistic that separates
it from the known effect (a placebo control), or goes straight to confirmation; (5) the reverse walk-forward stays
beside, and the lift by year is reported with every judgement.

### 1.3 The coin-twin lift as the test of direction

**The algebra is right.** With the rule's trade and its mirror settled under the same rules, a fair coin's expected win
at that fill is their mean, so lift = 1/2 [win(rule) - win(mirror)] is the rule's excess over the coin without the coin's
noise. It is **unbiased under the null only if the settlement treats the two sides symmetrically given what the bars
show.** F-01's does not:

1. **The fill-bar rule is asymmetric (D-1).** A resting order fills inside a bar, after part of the bar has traded. For
   a resistance broken from below, the bar's high comes after the trigger, but its low usually came before. "On the
   fill bar a stop touch is a loss and a target touch is not counted" then penalises the long -- through a low that
   probably came before the fill, and through a high beyond its target that certainly came after the fill. The long is
   the rule side for `break` and the mirror for `fade`, so `break`'s lift is pushed down and `fade`'s up. The size is
   at most about half the share of fills whose fill bar spans the approach-side stop (or reaches the far target), and in
   Appendix B a fraction of that bound. Synthetic (Appendix
   B; driftless walk; S = 100 ticks, R = 1; the same fills settled by F-01's bar rules and by the exact path):

   | 1-minute sd (ticks) | fill bars spanning the stop | break: bar rules, exact path | fade: bar rules, exact path |
   |---|---|---|---|
   | 25 | 0.07 % | -0.09, -0.09 | -0.88, -0.88 |
   | 50 | 27 % | -0.72, +1.03 | -0.47, -2.07 |
   | 80 | 79 % | -6.96, +1.90 | +5.74, -2.96 |

   *Synthetic, points of win probability, standard error about 0.25.* The bar-rule minus exact-path gap is the rule's
   bias: about -1.8 / +1.6 points at the middle row and about -8.9 / +8.7 at the last. How often NQ's fill bars span 100
   or 150 ticks is direction-free and can be read in stage A (K5 below); it is likely highest at the 08:30 open, where four of the five kinds go live. The sum
   lift(break) + lift(fade) does **not** reveal the bias (it cancels there), so it cannot be a diagnostic.
2. **Booking prices (D-13).** The mirror is booked at the rule's fill price. For `break` that is the stop plus a tick of
   slippage, so the mirror short sells a tick above the trigger; for `fade` the mirror long buys at the limit while the
   market trades a tick through it. At a 100-tick stop and R = 1, one tick moves a Brownian win probability by 1/(2S) =
   0.5 point (0.33 at 150 ticks; a quarter of that at R = 3): conservative for the rule, and at the scale of the value
   bar. In fast markets the trigger price can overshoot by several ticks within the minute: "stop plus one tick" then
   books the break *better* than the market and the fade's limit worse. In Appendix B the exact-path lifts at F-01's
   booking are +1.0 to +1.9 (break) and -2.1 to -3.0 (fade) points on a driftless walk at high volatility -- a bias in
   favour of `break` precisely when the hypothesised cascade happens.
3. **Drift (D-12).** In a rising market a long-leaning rule is credited with the drift. `break` at a resistance is long,
   and prior highs are broken more often than lows in an up-trend, so `break`'s fills lean long. Stage 2 knew this (P-16
   prereg line 129: "its gross is not exactly zero... the asymmetric bracket in a rising market move it") and D-271 makes
   a drift-matched baseline the rule. F-01 does not declare it.
4. **Conditioning on the rule's own fill.** In continuous time, conditioning on a first passage (the trigger) does not
   bias a martingale's future, so the comparison at the same fill is the right estimand for "direction after the
   touch". Its biases come from bar resolution (items 1-2), not from the conditioning. But the estimand is not "the level
   is special": any crossing after a move carries short-term follow or reversal, including the known follow effect
   (D-580, D-592). Separating the level's cascade from that needs a **placebo-level control** -- the same statistic at
   matched levels with no visible meaning (same distance from the price at `t_pub`, a seeded offset off the grid) --
   and the judged statistic should be lift(level) - lift(placebo).
5. **Realisability.** The mirror is no order anyone could place at that price: the opposite of a buy stop at the trigger
   is a market sell (a tick worse) or a resting sell limit at the stop's price (a fade order that fills on a touch); the
   opposite of a sell limit filled on a trade-through is a market buy a tick above the limit. As a counterfactual null it
   is acceptable only if both sides are booked symmetrically relative to the trigger price.

**The repair (for the corrected family):** (a) a **pair rule** on the fill bar -- if the fill bar touches either trade's
stop or target, the pair contributes zero lift (both settled as losses), is counted, and its share is reported and
capped (K5: above a declared share the cell is unmeasurable at one-minute resolution); otherwise both walk from the next
bar under stop-first; (b) the mirror booked at the trigger price with the same slippage the rule pays, in the other
direction; (c) a slippage ladder for stop entries (1, 2 and 4 ticks) with the decision at the conservative rung, or at
least beside; (d) the drift-matched baseline and the placebo control as declared statistics.

### 1.4 Identities, the clean-run rule, the failure protocol, the variant count: satisfied while wrong (P-4)

1. **The vendored identity proves self-consistency, not correctness**: the vendored engine reproduces the vendored
   results. That is the right first gate, but a bug in Stage 2's engine reproduces itself. It covers the gate rows, not
   U1's start rows -- and F-01's stage D verdict is computed by the U1 replay and `u_select` (E-005 (c); Q-05 open).
2. **The suite passes without the identity**: `tests/test_stage2_identity.py` calls `pytest.skip` when the bars or
   atlas are absent, so a worktree or clean checkout with a broken junction is green (P-6; T-11).
3. **F-01 7.1** walks P-16's market entries at a bar's open, where "the fill-bar rule does not apply": none of the new
   code -- intrabar fills, the fill-bar rule, trade-through, gap-through, void, cutoff, the mirror's booking -- is
   touched by it.
4. **F-01 7.2** ("every level at `t_pub` is unchanged when every bar after `t_pub` is replaced") passes with D-5's look-
   ahead if "after" is read by start stamp (> 08:25); it tests levels only, not the side set at `t_live`. The house form
   is right: replace every bar stamped `>= t` (feature-rules section 2).
5. **F-01 7.4 / Q-10's mirror test** passes under D-1 when the synthetic one-minute ranges rarely reach the stop (Appendix
   B's first row: no visible bias), when its interval is wide against the value bar, or if break and fade are pooled.
   Q-10's brief specifies "synthetic random-walk bars" with no range or size.
6. **The clean-run rule pins code, not data**: the vendored `write_result` records the commit, the dirty flag and the
   seed; nothing records the data's hash unless the caller puts it in the parameters. "Run once" is recorded nowhere: a run killed and restarted, or two
   clean runs from two commits, leave no trace beyond the one kept.
7. **The failure protocol** cannot tell a defect fix from a tune from outside: nothing requires the defect to be shown
   first by an outcome-free failing test, or both runs to be kept and the first cited.
8. **The variant count** reports 20 cells where 60 hypotheses are selected over (D-7), and does not carry the Stage 2
   reads of the same mechanism (S1 and S3's breakout rules, A3's `orb_rth30`, ORB5/ORB6) that a later registration's
   D-189 N must include. Stage 2's L3 look-ahead canary and L5 planted-effect tests (RESEARCH_PROTOCOL: "a verdict is
   cited only when... L3 and L5 passed") have no counterpart for this repository's walker (T-14).

### 1.5 Holes a new family could fall through (P-5)

**(a) A hyperparameter search inside a "single hypothesis".** Family B (the classifier) is one "cell" that can hide a
search: inner folds that reach into 2024-2026, configurations tried and not counted, early stopping on a validation slice
of the judged block, refits with new seeds keeping the best, a feature subset chosen from a library built on all years.
D-621 (4)(d) ("no fitted values") forbids it outright, so family B needs its own row; the house rule (feature-rules
section 4: "searched inside the declared walk-forward only, and every searched value is counted in the family's k") uses
"k" for two things (P-6). **Rule R-7:** the family file declares the search space and budget (a grid, or a seeded random
search of fixed size), the inner purged and embargoed folds **inside 2020-2023 only**, the selection criterion and the
count; every configuration evaluated is written to the family's result file and counted in its trial count; the final
model's parameters are hashed and the hash pinned in a row before the judged read. **Enforced by** T-3 (choice-stage
invariance: every output of the fitting stage is byte-identical when the judged block's bars are replaced by synthetic
bars), T-7 (the judge's manifest names the pinned model hash; the judge entry point cannot fit), and H-2 (a purpose-tagged
bar reader that refuses judged dates to a `choose` or `fit` purpose).

**(b) Feature or level selection informed by the judged block.** In-family: full-sample normalisers (a z-score, a
quantile or a time-of-day median over 2020-2026) leak the judged block into the choice block; feature-rules section 2
forbids it and the shift test catches a feature reading after `t`, but not a normaliser fitted on later years.
Between families: the grid itself is chosen knowing 2024-2026 (P-3, D-2). **Rules R-3, R-4:** the prior-exposure section;
normalisers trailing or fitted on 2020-2023 only. **Enforced by** T-3 (which also catches a full-sample normaliser: the
choice stage's output changes when the judged block is replaced) and the family-file lint T-2.

**(c) Re-declaring a killed family with a small change.** "A change is a new family" plus a fresh k is a licence to
iterate on the same judged block: the budget bounds the multiplicity, not the adaptivity. Stage 2 closed this hole in
words (D-277: "a closed specification is never resurrected by a new parameter combination... the boundary between
researching new models and fishing for a surviving parameterization") and F-01 already falls through it for `or30` (D-2).
**Rule R-8:** a family registry (`prereg/FAMILIES.yaml`): id, k, level, status, mechanism tags, cells, the blocks it read,
its closing row; a new family sharing a tag with a closed family or branch must name the closure, state what changed and
why it is a different hypothesis, and may not be judged on a block on which the closed family's mechanism was already
judged -- it goes to a placebo-differenced statistic or to confirmation. **Enforced by** T-2.

**(d) Exploratory readings before a declaration.** "No bar has been read for it" is an assertion: any script can import
the vendored `read_bars` and look. **Rule R-5:** every development read in this repository goes through one adapter that
appends to a committed read ledger (family id or `exploratory`, purpose, date range, commit, dirty flag) and refuses a
family id with no pinned declaration; a family declared after an exploratory read touching its mechanism cites the read
and is labelled. **Enforced by** H-2 (a PreToolUse hook on Bash that refuses Python commands importing
`propedge.data.bars` or opening `vendor/stage2/data/bars` outside the adapter and the clean-run helper -- a deterrent, not
proof) and T-4 (no ledger entry tagged with a family precedes its pin commit).

**(e) A withdrawn declaration: does it spend a k?** The budget controls the chance of a false carry; a declaration
withdrawn before any of its data is read performs no test and cannot produce one, so spending its k buys nothing. Stage 2
treated withdrawals so: D-107 does not count "withdrawn drafts never registered", and P-01 to P-03, withdrawn before any
data was read, stand in the registry as "abandoned: not run". The risk is a withdrawal that was data-informed. **Rule
R-6:** a withdrawn declaration does **not** spend its k, and the corrected family takes it, only if (i) no result file,
run log, read-ledger entry or committed code of the family exists, (ii) the withdrawal row names a review finding (not a
read of data) as the cause, and (iii) the corrected family is declared in the same row; otherwise the k is spent and recorded
as a closed family with no cell judged. **For F-01 today:** the history (five commits) holds no F-01 code, run or result;
the identity's reads were P-14's and P-16's; the cause is this audit. So F-01 may be withdrawn without spending k = 10,
the corrected family taking k = 10 at 0.05/110 -- **provided** Q-10's walker branch has computed no level and no outcome
other than P-16's identity (its brief says so; the lead checks). The conservative alternative -- spend k = 10, the
corrected family at k = 11, 0.05/132 -- costs little: C1's critical value moves from 3.695 to 3.763 (t, df 29), about
2 % on the MDL. Either choice is acceptable; what is not acceptable is choosing it later. **Enforced by** T-5.

**(f) House rules with no test or hook behind them.** Enforced today: `vendor/` (hook plus the integrity test), the pinned
family hash (`test_declarations_fixed.py`), licensed data untracked, the reserved window physically absent. Not enforced:

| rule | gap | fix |
|---|---|---|
| decision log append-only | a row (with its pinned sha) can be edited in the same commit as the file it pins | T-8: every row of every ancestor's `DECISIONS.md` is in HEAD unchanged; H-1 refuses edits that change an existing row |
| a pinned family never edited | the test only checks files that already have a pin; an unpinned `prereg/F-*.md` passes; Bash can edit | T-9: every `prereg/F-*.md` has exactly one pin; H-1 refuses Write/Edit of a pinned file |
| declare before building | checked by the lead's eye (merge checklist 2) | T-9: the pin commit is an ancestor of every commit touching the family's code or results |
| results only with a manifest, from a clean run; no typed figure | no writer, trace check or run ledger yet (Q-04) | T-10: every `results/*.csv` has a manifest, `git_dirty` false, a commit reachable from `master`, the data manifest's sha; the trace check |
| one heavy run at a time | `run.lock` is a convention (E-005) | `run_clean.py` refuses without the lock |
| seeds fixed and "used nowhere else" | nothing checks; F-01's 20261901 is already Stage 2's (N-2) | T-12 |
| identities first, refusing | the identity test skips without data | T-11 |
| count every cell | prose | T-2 against the registry and the result file's distinct cells |
| every new runner has its own identity | prose | T-15 for stage D; a registry field naming each runner's identity test |
| the confirmation window counted (Stage 2 D-107) | not carried into this repository | R-15 |

---

## Part 2. F-01 red-teamed, section by section

Line numbers are those of `prereg/F-01_resting_order_level_atlas.md` as pinned.

**Status and level (lines 3-8).** "No bar has been read for it" is true of this repository's history (1.5 (e)), but the
file has no prior-exposure section, and its declarer had read Stage 2's results on the same mechanisms (D-2). k = 10 and
"no further division" are right (1.1, N-1).

**D-2 (MATERIAL; NEW FAMILY) -- the hypothesis's basis (lines 14-28).** Line 22-23: "Stage 2's own breakout work entered
at the market after a delay (ORB5, Stage 2 D-275...); nothing in Stage 2 entered at the level itself." False: ORB5's
entry was "a stop order at the range's edge" with `missed_trigger: [skip, rest, chase]` (`config/orb5_grid.yaml`; D-266
defines `rest` as "left resting at its level until it next trades through"), and ORB6's hypothesis was "a retest (limit)
entry at the broken edge" (D-277, D-278). D-281 closed "the 08:30 NQ opening-range-breakout research branch (ORB1 to
ORB6)... for good" under the operator's D-277 rule, and its finding (3) reserves "whether any later hypothesis is
genuinely different" to the operator. A3 read `orb_rth30` followed and faded on 2020-2026 (`config/atlas_a3.yaml`). So
the four `or30` cells sit inside a closed branch without the row D-277 requires. Line 27, "level ideas that died on the
delay are re-opened", names exactly the class D-592 closed to this window: S3's follow-the-breakout candidate died at
the five-minute latency, and D-592 recorded the follow effect "as a lead for unread data, not as a new batch". The
`break` cells at `pd`, `on`, `pdc` and `rn100` will load on that effect, whose sign on the judged block is known (D-580,
D-588). E-003's basis cites none of D-277, D-281, D-580, D-588, D-592. **Remedy:** drop `or30` (the safe default under
D-281; recorded as a decision the operator owns, never a question that blocks); judge the other kinds by
lift(level) - lift(placebo) (1.3 item 4), so a pass is about levels and not the known follow effect; add the
prior-exposure section; correct line 23.

**Section 2, the contract fit (lines 33-44).** Line 37's constraint ("every level is computed from bars closed at or
before `t_pub`") is right and is broken by section 3 (D-5). Line 38: "the screen reads every fill of a cell
independently; the campaign routes by the strict rule" -- the screen's uses and the campaign's uses then differ by a
large factor (D-3). Line 39 points to K2, which relaxes D-212 (D-8). Line 40 points to K3, which cannot fail (D-9).
Line 42: the BLS and FOMC rules are as Stage 2's (N-6).

**D-5 (MATERIAL; READING) -- look-ahead and the side of the ticket (lines 48-60, 75, 164).** The bar store stamps a bar
by its start (`vendor/stage2/data/README.md` line 154, `ts`: "Bar START"); the house rule says it in so many words:
"'The 08:25 bar's close' is known at 08:26, not 08:25" (feature-rules section 1). F-01 names bars by their start too
(`pdc` = "the 14:59 bar's close", the last bar of 08:30-15:00). So `on` ("to the 08:25 bar's close", line 53) and
`rn100` ("the 08:25 bar's close", line 56) read a bar that closes after `t_pub` = 08:25: a minute of look-ahead and a
four-minute latency. Line 58 classifies every level by "the price at `t_live`" -- after `t_pub`, undefined (which
price?), and incompatible with line 75: if the side is set by the price at `t_live`, no stop can be "already through" and
no limit "already marketable", so the void rule is empty; and `pdc` (line 55, "on whichever side of price it lies at
`t_live`") makes the side of a published ticket depend on the market five minutes after publication. **Reading** (section
2 governs): `on` and `rn100` end with the bar stamped 08:24; the side is set at `t_pub` from the close of the bar stamped
`t_pub - 1 min`; at `t_live` a ticket already through is void (the declared `skip`); "the price at `t_live`" is the open of
the bar stamped `t_live`; "a bar after `t_live`" is a bar stamped `>= t_live`; test 7.2 replaces every bar stamped
`>= t_pub` and also asserts the side. `or30` (bars 08:30-08:59, `t_pub` 09:00) is consistent.

**D-11 (MINOR; READING) -- cross-day levels and calendar edges (lines 52, 55).** The store holds one contract a day at raw
prices, and "any cross-day level... must handle the roll days" (data README lines 160-164). On a roll day `pd` and `pdc`
are the old contract's prices, off by the calendar spread. P-14's caveats C2 (the seam: 2025-06-30 removed, the first two
hours of 2025-07-01 missing -- inside the judged block) and C5 (days ending before 15:00 not traded) leave `pd`, `pdc` and
`on` undefined on those days. **Reading:** void, and counted, on roll days for `pd` and `pdc`, on the seam days for every
kind, and on early-close days; `rn100` is multiples of 100 in the futures' own price (not "index points"); a close
exactly on a multiple takes the multiples on either side.

**D-15 (MINOR; READING) -- unlabelled choices (section 3).** CLAUDE.md asks for every parameter classed fixed /
searched / dropped; F-01 has no such table. Silent drops: frozen session-VWAP bands and prior swing points (the
bootstrap's family A list, 6.3), opening ranges of 5, 15 and 60 minutes (ORB5 searched them), R = 2 and 2.5 (the table's
offered set, P-16 prereg line 174), round-number spacing other than 100. **Reading:** the table, each with its one-line
reason.

**D-1 (MATERIAL; NEW FAMILY) -- the walk and the mirror (lines 79-92).** See 1.3 items 1-2. The walk's absolute
conservatism (stop first, fill bar) is right for a trade's outcome but, applied to both sides of a comparison whose
approach direction is aligned with one side by construction, it biases the comparison with a predictable sign. The rule
is declared ("the same stop, target and walk rules", line 86), so the repair -- the pair rule, symmetric booking, a K5
ambiguity share read in stage A -- is a new family. The house label rule (feature-rules section 3) copies line 80 and
needs the same change for any coin-twin comparison of resting entries.

**D-13 (MINOR; READING beside, NEW FAMILY for the rule) -- booking and slippage (lines 66-67, 85-86).** See 1.3 item 2.
The hypothesis is a stop cascade beyond the level; that is when a stop fills worst. One tick of slippage (Stage 2's D-95
convention for market entries at a bar's open) is optimistic there. **Reading:** a slippage ladder (1, 2, 4 ticks) for
`break` fills beside, with the share of fills in the first five minutes after 08:30 and on bars spanning a quarter of the
stop.

**N-3 (NOTE; READING).** Line 81, "flattened at that bar's close": the bar stamped 15:10 closes at 15:11, after the
firm's flatten. The identity 7.1 fixes the convention -- adopt P-16's walker's (`fv3_rung_walk`: FV3-C's flatten).
**N-5 (NOTE).** Target exits fill on a touch while limit entries need a trade-through; symmetric for the lift, optimistic
for a trade's own outcome.

**Section 4, the gates (lines 94-112).**
- The cutoff rule is direction-blind (rule and mirror pooled; their barrier sets are reflections) and chosen on
  2020-2023: sound. It is bound by R = 3, so R = 1 cells lose late fills: declared, fine.
- **D-8 (MINOR; NEW FAMILY).** K2 allows 10 % unresolved in a single year; D-212 as amended by D-308 binds "at most 5 %...
  overall, per market and per year" (RESEARCH_PROTOCOL step 2; CHARTER section 4). Stage D's D-621 (3)(iii) would catch it
  later, but the screen should apply the binding line. Also report K2 on the judged block.
- **D-9 (MINOR; READING).** K3: "at least 90 % of the cell's stopped trades realise at least 90 % of the intended risk"
  cannot fail -- a stop exit slips one tick against the trade (line 83) and gaps only add -- so realised risk is never
  below intended. The substantive check (whole micros at the table's risk, D-272) belongs to stage D. Record it so.
- **D-10 (MINOR; READING).** Stage A is declared "from fill counts and barrier columns only... so no direction is read"
  (lines 96-97), but K4 reads "the outcome of touched-but-unfilled `fade` tickets" (line 107-108) -- a directional
  outcome on the choice block, before stage B. Planning (lines 110-112) needs "its fill count" on the judged block -- a
  read of 2024-2026 before choice. **Reading:** K4's outcome part is computed with stage B; the judged-block fill count
  is estimated as the choice-block rate times the judged sessions until stage C.
- **K5 (proposed, NEW FAMILY):** the share of fills whose fill bar touches either trade's stop or target -- direction-free,
  a bound on D-1's bias; above a declared share the cell is unmeasurable at one-minute resolution.

**Section 5, selection and the kill lines (lines 114-146).**
- **D-14 (MINOR; READING).** Stage B's "session-block bootstrap" does not say moving, circular or stationary (program S
  used a stationary bootstrap, `config/search_program.yaml`), nor that the maximum is taken over centred studentised
  replicates. C1's "Student-t on 21-session block means" bounds the mean of block means, while the lift (line 89) is the
  mean over fills; with uneven fills per block they differ. **Reading:** stationary, mean block 21, centred,
  studentised by the bootstrap's own standard error; C1 on the ratio of block sums with a block-weighted t; C2 uses the
  same estimator.
- **The valued lift** copies the value map's own formula (`u_value_map.csv`, `definitions` `extra_win_prob_points`: "target
  / (uses x mean_dv) x 100, uses = N, or the place's trades a year where fewer"): faithful. The file is EXPLORATORY,
  "selects nothing" in its own manifest, and is computed over 2020-2026; using it to rank is acceptable because it is
  pinned and carries no level-direction information (N-4), but it is "first-order... unreliable far from zero" (handoff
  2.7), and any pick that passes C1 is far from zero.
- **D-4 (MATERIAL; READING + PROTOCOL ROW) -- power.** C1's critical value is t(29) at 1 - 0.05/110 = 3.695; the paired
  term 1/2 [win(rule) - win(mirror)] takes the values -1/2, 0, 1/2, sd at most 0.5 (R = 1), about 0.45 (R = 1.5), about 0.35
  (R = 3). The lift that reaches the bound half the time: 10.7 / 7.5 / 6.2 points at R = 1 for 300 / 600 / 900 judged
  fills; 7.5 / 5.3 / 4.4 at R = 3 (Appendix C). Stage B on 2020-2023 needs about as much. The value map's bar for $500 a
  year (`u_value_map.csv`, section `bar`, `target=500`, forward basis) is 0.28 to 0.97 points at the best place for 36 or
  more uses a year (p16 and p14 rows) and 0.33 to 2.5 on every trade for 36 to 250 uses. So the family can detect only
  lifts five to thirty times what would be worth having, and far larger than anything Stage 2 found against coin twins
  (D-558: "a genuine but tiny direction effect"). Planning puts the MDL "on record" (line 112) but nothing acts on it.
  **Reading:** a CLOSED at B or C is recorded as "no lift above the MDL (stated) at this family's level"; never "no lift
  at levels". **Protocol row (R-16):** a family whose MDL exceeds the value bar by more than a declared factor is
  declared as a screen, or pooled to fewer hypotheses, before it is run.
- C2 ($500 a year at the 95 % bound) never binds once C1 passes (C1 needs several points); harmless (N-1).

**D-3 (MATERIAL; NEW FAMILY) -- stage D (lines 138-146).** The design is P-16's schedule plus the pick's tickets,
first-come, judged by D-621 (3) against P-14.
1. **The base is behind R\*.** P-16's P is below P-14's on all starts (`u_budget.csv`, section `cell`, cells `p16` and
   `p14`, block `all`, measure P). The tickets must close that gap before (3)(i) can hold, and (3)(iv) asks a coin-based
   design to beat P-14 in 40 of 50 coin sequences. The verdict confounds the base (P-14 to P-16) with the tickets.
2. **The tickets rarely get the position.** P-16 offers at every five-minute mark its cutoff admits (P-16 prereg lines
   168-177; the strict router takes the first flat moment) and already routes a small share of its own offers -- about
   3 %, the rest arriving while an account is in position or none is flat (`u_xfa_day_budget.csv`, `p16`, `verdict`,
   section `signal_supply`, group `router`, `share_routed` and the three refusal shares). A ticket takes the firm only if
   it fills in the short gap between the end of the five-minute flat and the next admitted mark, or after P-16's last
   mark. What the screen valued (every fill used, up to the place's supply) is not what the campaign would spend.
3. **The wrong R and the wrong table.** "The table sizes every trade as it sizes P-16's": the table also chooses the R by
   account state (1.5R in the evaluation, 3R at the funded opening, about 1R after), so a ticket judged at R = 3 is
   traded at whatever the state asks. The valuation puts 25-point picks on P-14's table (line 127), the campaign on
   P-16's schedule and table.
4. **Conduct.** A resting ticket left at the broker while another account holds a P-16 position can fill the other way:
   opposite positions across accounts is tier 1 (D-145). The design needs a cancel-on-entry and a re-place after flat at
   the operator's five minutes (D-266), and it has neither.
5. **The bound.** (3)(i) is P-1's bound.
**Remedy (corrected family):** add tickets to the base whose table the valuation used (P-14 for 25 points, P-16 for
37.5); route a ticket only to an account in the state whose table ask is the pick's R, with priority there; model
cancel-on-entry and re-place at L = 5; report the paired difference from the same base at the same paths and seeds
(the tickets' own effect) beside the D-621 verdict against R\*; with P-1 fixed first.

**Section 6, data, windows and seeds (lines 148-156).**
- **D-6 (MATERIAL; READING now, PROTOCOL ROW).** NQ from 2026-07-17 is `reserved` (`config/windows.yaml`): "becomes NQ's
  fourth confirmation window only by the operator's decision (D-107)". D-107 caps confirmations at three a market and makes
  a fourth an operator decision recorded in the log -- not just a purchase. Stage 2's `prereg/DRAFT_P16_confirmation.md`
  (lines 6, 28-29, 51-53) targets the same window for P-16. If Stage 2 reads it for P-16 first, a design built on P-16's
  schedule cannot be cleanly confirmed there by the same researcher; E-005 (b) already sees that Stage 2 may import it.
  **Reading:** the confirmation is "NQ's next unread window, by the operator's D-107 decision, not read by any test whose
  design shares this family's base"; **protocol row (R-15):** one ledger of confirmation windows across both repositories.
- **N-2 (NOTE; READING).** Seed 20261901 is `user_drivers.CLUSTER_SEED` in the vendored tree (`propedge/research/
  user_drivers.py` line 71; `results/user_drivers.csv` manifest). Statistically harmless (a different procedure on
  different data), but "used nowhere else" is false; T-12 would have caught it. 20261902 and 20261903 are unused.

**Section 7, the build's tests (lines 158-169).** See 1.4 items 3-5. Missing: the per-side mirror test with realistic
ranges and enough size (T-13), a planted-effect test (T-14), the choice-stage invariance test (T-3), and stage D's routing
identities (T-15). Item 5 (E-002's identity in the build's commit) should be "and U1's start rows" once Q-05 holds.

**Section 8, count and outputs (lines 171-180).**
- **D-7 (MINOR; READING).** "Variants counted: 20 cells" while stage B selects over 60 (cell, R) pairs. Stage 2's house
  form counted the same way (S1: "variants: 15" for 90 hypotheses), so it is consistent, but a later D-189 N should count
  the 60 hypotheses and the prior reads of the mechanism (1.4 item 8). **Reading:** report "20 cells, 60 hypotheses".
- **D-12 (MINOR; READING).** Beside, deciding nothing until a row says otherwise: the drift-matched baseline and the
  per-era figures (D-271), the placebo-level lift, the slippage ladder (D-13), D-663's stress readings for stage D,
  K2 on the judged block.

**What stands in F-01.** The choice-then-judge structure; the max-statistic with BH beside; C1's t-bound; the cutoff
rule; void-as-skip at `t_live` (once D-5's reading fixes the side at `t_pub`); the trade-through rule for limit fills;
seeds fixed in advance; the confirmation declared before any read; the exploratory label until a carried candidate is
registered. The corrected family can keep all of these.

---

## Part 3. Proposed rules, tests and hooks

**Rules (each its own decision row before the next family is pinned):**

- **R-1 One error ledger.** `prereg/PROGRAM.yaml`: every family and batch declared on the NQ development window (Stage 2's
  S1-S4 and U1-U9, then this repository's), its level, status, cells and hypotheses; the cumulative nominal spend printed
  with every reading; the sentence that the development level is a screen and the confirmation decides (P-2).
- **R-2 A calibrated selection bound** replacing D-621 (3)(i)'s percentile bound for this repository (P-1), before any
  stage D is read.
- **R-3 Prior exposure** in every family file, and the closed-branch and "lead for unread data" rules of 1.2 (P-3, D-2).
- **R-4 The judged block sealed** during choice and fitting (purpose-tagged reader; H-2; T-3).
- **R-5 A read ledger** for every development read (1.5 (d)).
- **R-6 Withdrawal** does not spend a k only under 1.5 (e)'s three conditions (decided now, for F-01 and every later
  family).
- **R-7 Fitted models**: declared search, inner folds in 2020-2023, every configuration counted, the model hash pinned
  before judgement (1.5 (a)).
- **R-8 A family registry** with mechanism tags and closure links (1.5 (c)).
- **R-15 A confirmation-window ledger** across both repositories, with D-107's count (D-6).
- **R-16 Power before reading**: the MDL against the value bar on record, and a family whose ratio exceeds a declared
  factor declared as a screen or pooled (D-4).
- **R-17 Words**: "family number k" (the program index) and "cells" / "hypotheses" (the trials), never "k" for both.

**Tests (fast tier unless marked):**

- **T-1** `test_program_ledger`: k unique and consecutive; level = 0.05/(k(k+1)); every `prereg/F-*.md` listed;
  withdrawn entries carry spent / not spent per R-6.
- **T-2** `test_family_files`: every family file has the sections Prior exposure, Parameter classes (fixed / searched /
  dropped), Seeds, Count (cells and hypotheses), Confirmation (window and D-107 count); tags checked against the registry
  (R-8).
- **T-3** `test_choice_stage_invariance`: a family's stage A and B (or its fit) run on bars whose judged block is replaced by
  a seeded synthetic walk produce byte-identical outputs (the cutoffs, the critical value, the pick, the fitted model).
- **T-4** `test_read_ledger`: no read tagged with a family before its pin commit.
- **T-5** `test_withdrawals`: a withdrawn family with any result, run log or ledger read is marked spent.
- **T-6** `test_selection_level` (slow): the selection bound's rejection rate on synthetic nulls (iid, MA 21, MA 63; the
  judged block's length) within 1.5 times nominal at 0.5 % and 2.5 % (20,000 replications), and analytically at the family
  level for a t-based bound.
- **T-7** `test_judge_uses_pinned_model`: the judge's manifest names the pinned model hash; the judge entry point
  refuses to fit.
- **T-8** `test_decisions_append_only`: for every ancestor commit, each of its `DECISIONS.md` rows is in HEAD unchanged.
- **T-9** `test_declarations_fixed` extended: every `prereg/F-*.md` has exactly one pin; the pin's commit is an ancestor
  of every commit touching the family's code or results.
- **T-10** `test_results_provenance`: every `results/*.csv` has a manifest with `git_dirty` false, a commit reachable from
  `master` and the data manifest's sha256; every run (started, aborted or kept) is in the run ledger.
- **T-11** the identity refuses: the clean-run helper fails, not skips, when the identity's data are absent; U1's start
  rows join the identity (Q-05) before any stage D.
- **T-12** `test_seeds_unique`: every seed a family file declares as its own appears nowhere else in `vendor/stage2`
  (code, configs, manifests) or another family file; inherited seeds (20261700, 20261600 + i) listed explicitly.
- **T-13** the mirror's zero, per side rule (`break` and `fade` separately, never pooled) and per R, on synthetic walks
  whose one-minute ranges reach and exceed the stop on a declared share of bars (Appendix B's middle row at least), with
  enough fills that the interval's half-width is under a quarter of the value bar (of the order of 10^6 synthetic fills); under
  F-01's declared rule it should **fail** -- the evidence for D-1's pair rule.
- **T-14** a planted-effect test (Stage 2's L5 form): a planted continuation of known size at level touches is recovered
  by the statistic with the right sign and size, and the stage-C bound covers it at its level; a planted look-ahead
  feature (L3's form) produces no lift.
- **T-15** stage D's routing identities: tickets that never fill reproduce the base's registered paths; tickets that
  duplicate the base's own offers (same time, side, price) reproduce them too.

**Hooks:**

- **H-1** PreToolUse (Write, Edit, MultiEdit): refuse a change to an existing row of `DECISIONS.md` (append only) and any
  write to a `prereg/F-*.md` that has a pin; mirrored in the git pre-commit hook so Bash edits are caught too.
- **H-2** PreToolUse (Bash): refuse a Python command that imports `propedge.data.bars` or opens
  `vendor/stage2/data/bars` outside this repository's reader and `scripts/run_clean.py` (a deterrent; T-4 is the proof).
- **H-3** pre-commit: T-1, T-2, T-8, T-9, T-12 in the fast tier.

---

## Appendix A. The selection bound on synthetic nulls (P-1)

Synthetic only. `block_indices` re-implemented from `vendor/stage2/propedge/research/user_journey.py`; nothing of the
repository's data is read. Run as `python mbb_level.py <ma> <reps>`; the comparison as `python tblock_level.py`.

```python
# mbb_level.py
import sys
import numpy as np

def block_indices(n, b, draws, rng):                 # Stage 2's: non-circular moving blocks, ceil(n/b), cut to n
    k = -(-n // b)
    first = rng.integers(0, n - b + 1, size=(draws, k))
    return (first[:, :, None] + np.arange(b)[None, None, :]).reshape(draws, k * b)[:, :n]

def series(n, rng, ma=63, noise=0.3):                # mean-zero start-day differences, dependent over `ma` starts
    e = rng.standard_normal(n + ma - 1)
    x = np.convolve(e, np.ones(ma) / ma, mode="valid")[:n]
    return x / x.std() + noise * rng.standard_normal(n)

def run(n=578, b=63, draws=2000, reps=3000, levels=(0.05/110, 0.05/132, 0.05/90, 0.005, 0.025), seed=1, ma=63):
    rng = np.random.default_rng(seed)
    rej = {a: 0 for a in levels}
    for _ in range(reps):
        x = series(n, rng, ma=ma)
        boot = x[block_indices(n, b, draws, rng)].mean(axis=1)
        for a in levels:                              # D-621 (3)(i): difference > 0 and the level's percentile > 0
            if x.mean() > 0 and np.percentile(boot, 100.0 * a) > 0:
                rej[a] += 1
    return {a: rej[a] / reps for a in levels}

if __name__ == "__main__":
    ma = int(sys.argv[1]) if len(sys.argv) > 1 else 63
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
    for a, r in run(reps=reps, ma=ma).items():
        print(f"ma={ma} nominal={a:.6f} realised={r:.5f} ratio={r / a:.1f}")
```

```python
# tblock_level.py -- the iid row, and Student-t on non-overlapping 63-start block means (df = blocks - 1)
import numpy as np
from scipy import stats
from mbb_level import run, series
print("iid:", run(reps=4000, ma=1))
rng = np.random.default_rng(7)
for ma in (21, 63):
    rej = {a: 0 for a in (0.05/110, 0.005, 0.025)}
    for _ in range(20000):
        x = series(578, rng, ma=ma); nb = 578 // 63
        bm = x[: nb * 63].reshape(nb, 63).mean(axis=1)
        t = bm.mean() / (bm.std(ddof=1) / np.sqrt(nb))
        for a in rej:
            rej[a] += t > stats.t.ppf(1 - a, nb - 1)
    print("t on block means, ma", ma, {a: v / 20000 for a, v in rej.items()})
```

Output (2026-11-16; reps 4,000 for `mbb_level.py` with `ma` = 63, 21, 42; numpy 2.5.2, scipy 1.18.1):

```
ma=63 nominal=0.000455 realised=0.03425   ma=21 nominal=0.000455 realised=0.01025   ma=42 nominal=0.000455 realised=0.02100
ma=63 nominal=0.000379 realised=0.03325   ma=21 nominal=0.000379 realised=0.00975   ma=42 nominal=0.000379 realised=0.01975
ma=63 nominal=0.000556 realised=0.03575   ma=21 nominal=0.000556 realised=0.01050   ma=42 nominal=0.000556 realised=0.02200
ma=63 nominal=0.005000 realised=0.05900   ma=21 nominal=0.005000 realised=0.02525   ma=42 nominal=0.005000 realised=0.03900
ma=63 nominal=0.025000 realised=0.10975   ma=21 nominal=0.025000 realised=0.05875   ma=42 nominal=0.025000 realised=0.08250
iid: {0.000455: 0.008, 0.000379: 0.00725, 0.000556: 0.0085, 0.005: 0.0205, 0.025: 0.05425}
t on block means, ma 21 {0.000455: 0.00055, 0.005: 0.0074, 0.025: 0.0326}
t on block means, ma 63 {0.000455: 0.0013, 0.005: 0.013, 0.025: 0.04935}
```

The synthetic series stand in for the paired start-day differences in P (a start's month-1 to month-3 outcomes share
21 to 63 sessions with its neighbours'); the real series' dependence is not known here, but even the iid row is about 18
times nominal at the family level.

## Appendix B. F-01's fill-bar rule on synthetic random walks (D-1, D-13)

Synthetic only: a driftless one-second walk in ticks, aggregated to one-minute bars; a resistance L ticks above the start
(L uniform on 1 to 3 x the one-minute sd); `break` = buy stop at L + 1 filled at L + 2 (or the bar's open + 1 on a gap);
`fade` = sell limit at L filled when a bar trades at L + 1; each trade and its mirror (the opposite side at the same price)
settled (a) by F-01's bar rules and (b) by the exact path after the trigger second. S = 100 ticks, R = 1, 180 minutes,
40,000 trials (about 36,000 fills), seed 11. Run as `python fillbar_bias.py 25 50 80`.

```python
# fillbar_bias.py
import sys
import numpy as np

def run(sig_min, S=100, R=1.0, trials=40000, batch=400, minutes=180, seed=11):
    rng = np.random.default_rng(seed)
    T, tgt = minutes * 60, int(round(R * S))
    acc = {k: [] for k in ("brk_bar", "brk_true", "fad_bar", "fad_true", "amb")}
    done = 0
    while done < trials:
        n = batch
        L = rng.integers(1, max(2, int(3 * sig_min)), size=n)
        p = np.cumsum(np.rint(rng.normal(0.0, sig_min / np.sqrt(60.0), size=(n, T))).astype(np.int32), axis=1)
        hit = p >= (L + 1)[:, None]
        ok = hit.any(axis=1)
        ti = np.where(ok, hit.argmax(axis=1), -1)
        bars = p.reshape(n, minutes, 60)
        o, h, l = bars[:, :, 0], bars.max(axis=2), bars.min(axis=2)
        for i in np.arange(n)[ok]:
            t = ti[i]; m = t // 60
            if m >= minutes - 1:
                continue
            Fb = (o[i, m] + 1) if o[i, m] >= L[i] + 1 else (L[i] + 2)
            Ff = L[i]
            def bar_settle(F, side):                     # F-01: fill bar -- stop touch a loss, target not counted
                stop, targ = F - side * S, F + side * tgt
                st = (l[i, m:] <= stop) if side > 0 else (h[i, m:] >= stop)
                tg = ((h[i, m:] >= targ) if side > 0 else (l[i, m:] <= targ)).copy(); tg[0] = False
                js = st.argmax() if st.any() else 10**9; jt = tg.argmax() if tg.any() else 10**9
                return 0.0 if js == jt == 10**9 else float(jt < js)   # stop first on a shared bar
            def true_settle(F, side):                    # the exact path after the trigger second
                path = p[i, t + 1:]
                st = (path <= F - side * S) if side > 0 else (path >= F - side * S)
                tg = (path >= F + side * tgt) if side > 0 else (path <= F + side * tgt)
                js = st.argmax() if st.any() else 10**9; jt = tg.argmax() if tg.any() else 10**9
                return 0.0 if js == jt == 10**9 else float(jt < js)
            acc["brk_bar"].append(0.5 * (bar_settle(Fb, +1) - bar_settle(Fb, -1)))
            acc["brk_true"].append(0.5 * (true_settle(Fb, +1) - true_settle(Fb, -1)))
            acc["fad_bar"].append(0.5 * (bar_settle(Ff, -1) - bar_settle(Ff, +1)))
            acc["fad_true"].append(0.5 * (true_settle(Ff, -1) - true_settle(Ff, +1)))
            acc["amb"].append(float((h[i, m] - l[i, m]) >= S))
        done += n
    return {k: (100 * np.mean(v), 100 * np.std(v, ddof=1) / np.sqrt(len(v)), len(v)) for k, v in acc.items()}

if __name__ == "__main__":
    for sig in [float(x) for x in sys.argv[1:]] or [12.0, 25.0, 50.0]:
        r = run(sig)
        print(f"sigma_per_minute={sig:g}: fills={r['brk_bar'][2]}; fill bars spanning S={r['amb'][0]:.2f}%")
        for k in ("brk_bar", "brk_true", "fad_bar", "fad_true"):
            print(f"   {k:9s} lift {r[k][0]:+.2f} points (se {r[k][1]:.2f})")
```

Output (2026-11-16, condensed to one line per volatility; re-run from the code as printed here, the 50-tick row
matched to the digit):

```
sigma_per_minute=25: fills=36255; fill bars spanning S=0.07%   brk_bar -0.09 brk_true -0.09 fad_bar -0.88 fad_true -0.88 (se 0.26)
sigma_per_minute=50: fills=36274; fill bars spanning S=27.28%  brk_bar -0.72 brk_true +1.03 fad_bar -0.47 fad_true -2.07 (se 0.26)
sigma_per_minute=80: fills=36283; fill bars spanning S=78.74%  brk_bar -6.96 brk_true +1.90 fad_bar +5.74 fad_true -2.96 (se 0.23-0.26)
```

The gap between `bar` and `true` is the fill-bar rule's bias (same fills, same booking). The non-zero `true` lifts on a
driftless walk are the booking effect (D-13): Gaussian one-second steps overshoot the trigger, which "stop plus one tick"
ignores, so the break is booked below the market and the fade above it. Real NQ seconds are mostly 0 to 1 tick with
bursts, so the booking effect on NQ is smaller on average and concentrated in fast moments; the fill-bar share is
readable in stage A without reading direction.

## Appendix C. The minimum detectable lift (D-4)

The lift that reaches C1's bound half the time: MDL = t(df, 1 - level) x sd / sqrt(n), with df = 21-session blocks on
the judged block minus one (about 29), the level 0.05/110 (t = 3.695; 3.763 at 0.05/132), sd the paired term's (at most
0.5 at R = 1; 0.5 sqrt(0.8) at R = 1.5; 0.5 sqrt(0.5) at R = 3, where a rule and its mirror cannot both win), n the
judged fills. For 80 % power add about 0.85 standard errors.

| R | sd | n = 300 | n = 600 | n = 900 |
|---|---|---|---|---|
| 1 | 0.50 | 10.7 | 7.5 | 6.2 |
| 1.5 | 0.45 | 9.5 | 6.8 | 5.5 |
| 3 | 0.35 | 7.5 | 5.3 | 4.4 |

(points of win probability; for comparison, the value map's $500-a-year bar rows quoted in D-4.) One tick of entry price
at stop S and R = 1 is worth 1/(2S) of win probability (0.5 point at 100 ticks, 0.33 at 150), and 1/(4S) at R = 3.
