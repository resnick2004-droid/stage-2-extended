# Amendments draft: putting the journey objective in force (Wave 1.1, corrective cycle 2)

Drafted 2026-11-18 for the lead, from:
- `docs/plans/RESTART_PLAN_journey_objective.md` (the plan; LF sha256 as E-206 records it);
- `CHARTER.md`, `CLAUDE.md`, `DIRECTIVE.md`;
- E-007, E-008, E-015, E-202 to E-206 in `DECISIONS.md`;
- E-207 and E-208 as the lead's row scripts hold them (still committing when this was written);
- Stage 2 D-145.

**Revised in corrective cycle 1** to answer the red team's cold read, `docs/reviews/AMENDMENTS_2026-11-18.md`
(12 blocking, 10 minor findings), and **in corrective cycle 2** to answer its second read,
`docs/reviews/AMENDMENTS_v2_2026-11-18.md` (3 blocking, 10 minor), both under the coordinator's rulings. Section 0 maps
each finding to where it is answered.

**Status: a draft. Nothing here is in force.** E-207 records the operator's confirmation. The lead applies these texts
under the row drafted in section 4. No result figures, no seed literals. Every number is a parameter, a rule or a date.

Contents:
- 0. Finding → where it is answered.
- 1. `CHARTER.md` sections 2-5, the replacement text.
- 2. `CLAUDE.md`, "The objective": the replacement paragraph.
- 3. `DIRECTIVE.md`: every trades-first reference (current text and replacement) and the mapping table.
- 4. The draft decision row.
- 5. Every other file that cites E-008's pass line as binding (Wave 2's list).
- 6. Flags: what is resolved, what remains, and what is the operator's.

Each replacement text sits in its own fenced block, so it can be pasted unchanged. Flags stay outside the blocks.

---

## 0. Finding → section answered

| finding | ruling (coordinator) | answered in |
|---|---|---|
| B-1 held-out years read before; not single-use | ledger of past reads, nominal level when it is not empty, one use per market, map free of held-out results | CHARTER 2 (terms), 3.3 (f), 3.6 (a)-(c), 3.10; CLAUDE.md; row; DIRECTIVE D-11 |
| B-2 limits, budgets and composite inputs settable after a look | every input of 3.8 and 3.9 pinned in one row before the survey; H4 on search years only, held-out output sealed | CHARTER 2 ("Limits"), 3.6 (e), 3.9; row |
| B-3 starts straddle into the held-out years | a horizon is read only if it fits; embargo stated | CHARTER 2 (unit), 3.6 (d) |
| B-4 degenerate calibration; unit of replication | antithetic and disjoint-seed nulls; history blocks the unit; whole-rule calibration on the pinned composite; the coin-seed leg carries the level, the time legs are consistency conditions (E-208) | CHARTER 3.6 (f), 3.7 ("Calibration"); flag R-1 |
| B-5 baselines' convention | same convention as the design; registered rows beside; beat each baseline | CHARTER 2 (terms), 3.8 (b) |
| B-6 zero edge not zero for resting orders | post-fill path flipped with probability one half; as-traded reading beside as a stress; RL3's same-bar pair is one realisable case | CHARTER 3.2; 3.5 (side rule); DIRECTIVE D-5; flag R-2 |
| B-7 gate and verdict arm undefined under zero edge | zero-edge long-run gate written in the text; verdict arm retired on record | CHARTER 2 (unit), 3.2, 3.8 (c), 3.10 |
| B-8 one k against several finalists, latency variants, fallback | fixed sequence at the full level, stop at the first failure; L counted, five-minute cell beside; fallback pinned in place of the composite | CHARTER 3.3 (g), 3.7 ("Finalists"), 3.9 |
| B-9 power never secured; E-007 (2) unanswered | power gate for the whole line before any search pin; exit (B) states power; the data decision is an open operator item, asked before the first pin | CHARTER 3.7 ("Power gate", "Open operator item"), 5 (B); DIRECTIVE D-12 |
| B-10 two margins; E-015's condition dropped | one margin, applied once; fail only if shown to cross; a design equal to the best baseline passes every limit at the target power | CHARTER 2 ("Limits"), 3.7 ("Power gate"), 3.8 (a), 3.10 |
| B-11 evaluated object ≠ traded object | one literal coin draw per moment, shared across all accounts and firms; model sides only beside, with a no-harm floor | CHARTER 2 (terms), 3.5 (side rule) |
| B-12 selection on simulator optimism | +1 tick of worse fills and 10 % of signals missed are floors | CHARTER 3.8 (c) |
| m-1 latency as a searched lever | searched, counted in the multiplicity, nothing chosen after a look | CHARTER 3.3 (g), 3.5 |
| m-2 section 4 omits E-202 (2)(a), (d) | added as marked amendments | CHARTER 4 (final paragraph) |
| m-3 k numbering; "confirmation" ambiguous | E-204's rule quoted; "held-out test" vs "confirmation"; the confirmation spends no k | CHARTER 2 (terms), 3.7 ("The budget"), 5 |
| m-4 E-007 (e) readings dropped | each listed beside the verdict; the minimum detectable difference replaced by the power gate | CHARTER 3.8 ("The verdict") |
| m-5 the years leg's years; regime thresholds | the time leg runs on the held-out years; thresholds come from the search years | CHARTER 3.3 (a), 3.6 (f) |
| m-6 section 6's "the reverse beside" | not run before the held-out test; afterwards only as a description | CHARTER 3.6 (g) |
| m-7 measure count; S3c across designs | 37 measures plus the baseline set, under the plan's numbers; S3c kept within-stream and out of the composite | CHARTER 2 ("The measures") |
| m-8 other firms have no baseline | each firm's baseline set declared in its own search | CHARTER 2 (terms), 3.1; DIRECTIVE D-11 |
| m-9 DIRECTIVE consistency | Part 3 edited in place; Part 5's list and 6.3 C edited; retirements cite E-208 | DIRECTIVE D-0, D-6, D-9 to D-11, mapping table |
| m-10 record hygiene | E-207 cited; plateau rule pinned; each limit's direction stated | row; CHARTER 2 ("Limits"), 3.3 (e), 3.9 |

**Cycle 2** (the second read, `docs/reviews/AMENDMENTS_v2_2026-11-18.md`; the first table's B-10 row is now read with
m-2 / O-5 below):

| finding | ruling (coordinator) | answered in |
|---|---|---|
| V-1 the level bounds coin luck on one history; the nulls cannot see history luck | a history null added to H3; its false-pass rate printed beside every verdict; what the level bounds and what it does not, stated plainly; a declared criterion for the confirmation | CHARTER 3.6 (f) (i), 3.7 ("Calibration"), 3.8 (b) and "The verdict", 5 (A); CLAUDE.md; row |
| V-2 the post-fill flip is exactly zero only at a symmetric bracket | "exactly zero" and "zero by construction" corrected; the martingale-outcome reading (each outcome redrawn at its bracket's driftless first-exit odds, stage one's `BinaryDraw` form), the same for design and baselines; the verdict read on it; the as-walked gap reported as the path-structure edge, never credited; how section 4's oracles read it | CHARTER terms, 3.2, 3.8 (lead, (c), verdict), 3.10, 4 (second marked paragraph); CLAUDE.md; row; DIRECTIVE D-4, D-7 |
| V-3 no floor for the as-traded resting side | the model sides' no-harm floor applied to it; with as-traded sides, the finalist still ahead of each baseline at the point estimate on the held-out years | CHARTER 3.5, 3.8 (c), 3.9 |
| R-4 complete held-out starts over the gate's horizon | a stated pass condition of the power gate | CHARTER 3.7 ("Power gate"), 3.8 (c), 3.9 |
| m-1 / O-4 the literal coin decided in the text | marked "pending the operator (O-4)" wherever stated; the zero-edge evaluation convention kept | CHARTER terms, 3.5; CLAUDE.md; row; section 6 |
| m-1 / O-3 "the size that matters" has no author | marked the operator's, Wave 4.2 | CHARTER 3.7, 3.9 |
| m-10 / O-1 "Topstep $50K first" decides the held-out use | marked the operator's, pending: which firm spends NQ's held-out years, or one search over several firms | CHARTER 2 (objective), 3.6 (c); row; section 6 |
| m-2 / O-5 the burden reverses E-207's confirmed words | E-207's wording in force; B-10's form pending the operator (O-5), both written side by side; the single margin, applied once, stays | CHARTER 3.7 ("Power gate"), 3.8 (a), 3.9; row; DIRECTIVE D-2, D-7 |
| m-3 the ledger leaves out program U and RD-02 | both added; the list a floor that each declaration completes | CHARTER 3.6 (b); row |
| m-4 lever ranges and the whole-window RD maps | ranges from contract arithmetic, verified rules or an RD map's search-year rows only; whole-window rows redrawn; the source in the ledger | CHARTER 3.3 (a) |
| m-5 the side rule's wording; opposite sides across time | RL3's pair named as one that has a construction; the open-position rule | CHARTER 3.5 |
| m-6 the baselines' latency | registered latency, checked by the identity; the comparison's latencies stated | CHARTER 3.8 (b) |
| m-7 the calibration's order | the deciding calibration follows Wave 4.2's pinning row; H3's earlier runs are design checks; the power gate's pairs named | CHARTER 3.7 |
| m-8 the five-minute cell "in the held-out test" | reported, not tested | CHARTER 3.3 (g) |
| m-9 measure structure from H4 alone | one sentence: the dimensions come from variation across starts and seeds | CHARTER 3.9 |

---

## 1. CHARTER.md sections 2-5 (replacement text)

Sections 1 and 6 are out of scope and stay as they are (flags R-6 and R-7). Section 4 keeps its current paragraph byte
for byte, and the red team diffed it. Two marked paragraphs are added to it (m-2, and V-2's oracle reading). Section numbers are kept, so citations
of "CHARTER section 4" and "section 5" stay valid. The pass line is now section 3.8.

````markdown
## 2. The objective: the user's journey to making money

**The objective (the operator, E-207; E-NNN).** Find the way of running prop-firm accounts that gives a real user the
best journey to making money: the least bankroll needed, the fastest and cheapest path to a pass and a payout, a steady
income after that, and the lowest chance of going broke first. Topstep $50K first, then other firms, each on its own
verified rules (section 4), its own execution protocol and its own baselines, never Topstep's reused (E-202). Which
firm's search spends NQ's held-out years, or whether one search covers several firms, is **the operator's, pending
(O-1)** (section 3.6 (c)).

**Where the money comes from.** The firm's asymmetry: a funded account's loss costs the user only fees; its win is
paid. Not from predicting market direction. Stage 2's breakout and mean-reversion designs made money this way with no
trade edge (Stage 2's handoff, section 0). That is accepted: the goal is to make money, however it is done inside
section 4.

**What a design is judged on.** The user's journey -- the measures below, under the operator's limits, by the method
and pass line of section 3 -- never the trades' edge. Every trade runs under the zero-edge convention of section 3.2,
and a design must work under it.

**Terms.**

| term | meaning |
|---|---|
| design (execution model) | one complete way of running accounts, in three layers: (1) **triggers** -- the reason and moment to trade, with the side set by the design's side rule (section 3.5; the side rule is pending the operator, O-4); (2) **trade shape** -- stop, target, max hold, contracts, dollar risk; (3) **account policy** -- which account takes the trade, evaluation vs funded behaviour (RD-05's modes), daily stops, evaluation purchases, the component schedule |
| component | one session-specific trigger with its own trade shape (for example an NY AM component, an NY PM component); a design is a schedule of components |
| lever | a setting the user controls: bracket (stop, target, max hold), contracts, reward-to-risk, dollar risk per trade, accounts held, rotation rule, evaluation-purchase rule, model mix, the order latency L, and any state rule (sizing by distance to drawdown or target) |
| signal source | what decides *when* a trade is taken: a model (breakout, mean reversion, ...) or the naive coin |
| zero edge | the evaluation convention of section 3.2: the fill comes from the real order; the path after the fill is reflected about the fill price with probability one half (direction removed); and every deciding reading redraws each trade's outcome at its own bracket's driftless first-exit odds (the martingale-outcome reading) |
| start day | one development session taken as a fresh user (fresh bankroll, fresh accounts) |
| coin seed | one sequence of coin draws; re-running with many seeds gives the spread a user can live |
| search years | NQ 2020-01-02 to 2023-12-29 (E-208): the only years a search, its lever ranges, volatility units, regime thresholds, schedules, limits, budgets and weights may read |
| held-out years | NQ 2024-01-02 to 2026-07-16, on the pinned calendar `results/q82_judged_sessions.csv` (E-208): read only by a search's held-out test, once per market (section 3.6) |
| held-out read ledger | every past read of the held-out years for a search's comparators and trigger families, carried in its declaration (section 3.6 (b)) |
| held-out test | a search's one test of its ordered finalists on the held-out years; it spends one k |
| confirmation | the one read of a carried design on the confirmation window (NQ from 2026-07-17): a purchase and the operator's decision; it spends no k |
| limits | the operator's floors and ceilings on what a user feels (bankroll, chance of running out, trades per day, ...), each with its direction |
| baselines | for Topstep: naive coin harvesting (its levers fixed in the declaration) and Stage 2's P-14, P-15, P-16, each run under the design's convention (section 3.8 (b)); for another firm: the set its own search declares, at least the naive coin on that firm's own protocol |
| P | **not a p-value**: the mean share of start days ahead in cash at months 1, 2 and 3 |
| frontier | the designs not beaten on one measure without losing on another |
| composite score | one number over the measures' dimensions, weighted by the operator's trade-off answers, pinned with every other input of section 3.9 before the survey; the held-out test's hypothesis |

**The unit** is one user: one development trading session taken as a fresh start (fresh bankroll, fresh accounts), the
design's trades replayed in historical order under the zero-edge convention, over coin seeds fixed in the declaration
before the run. A start is read at a horizon only under section 3.6 (d)'s embargo. A month is 21 sessions. **The
outcome** of a start is its **net cash** -- payouts received less every fee paid -- along its path, and whether it is
above zero ("ahead"). Where a measure is Stage 2's, its definition is Stage 2's (`vendor/stage2/docs/USER_MILESTONES.md`,
Stage 2 D-620, D-621), **read on the zero-edge convention in place of Stage 2's `verdict` arm** (section 3.10). Every
measure's exact formula, and the function that computes it, is in **`docs/MEASURES.md`**. The auditor re-derives from
that file.

**The measures (the operator, E-206, E-207).** The plan's 39 items keep the plan's numbers, so `docs/MEASURES.md` and
the plan agree. They are 37 measures plus the baseline set, (35) and (36), which are comparators, not measures. Items
(12) and (13) are each several readings. Every measure is a distribution over start days (median, p10, p90) unless
stated otherwise, and also over coin seeds. Each carries its uncertainty from the effective number of independent starts.

- **Getting funded.** (1) sessions to first evaluation pass; (2) cash to first pass; (3) evaluations bought before the
  first pass; (4) share of starts passed by session 21.
- **First payout.** (5) sessions to first payout (S3b); (6) cash spent before first payout = bankroll needed (S1);
  (7) first payout's size (S3d); (8) share of starts paid by session 21 (S3a).
- **ROI.** (9) sessions to break-even; (10) share falling back below break-even; (11) deepest fall after break-even;
  (12) net cash at months 1, 2, 3, 6, 12; (13) P, and shares ahead at months 6 and 12 (S4a, S4b); (14) payouts per fee
  dollar (S3c: reported; compared across designs only within one trade stream, E-008 (1)'s rule for it, because its
  link to P across designs is partly arithmetic, E-007; never a dimension of the composite); (15) return on money at
  risk (12-month net over peak out-of-pocket).
- **Steady income and payout variance.** (16) monthly net in months 4-12; (17) payouts per month; (18) share of months
  with a positive net change; (19) spread of monthly net; (20) longest run of months without a payout; (21) longest
  gap between payouts within 126 sessions (S5b); (22) best quarter's share of month-6 net (S5c); (23) largest month's
  share of the year's payouts.
- **Bankroll and downside.** (24) chance of running out before the first payout at budgets the operator sets (the
  bankroll stop); (25) peak out-of-pocket in 12 months; (26) month-3 net of the unlucky tenth (S5a); (27) CVaR10.
- **Realism and robustness.** (28) headline measures with 10 % and 20 % of signals missed or late; (29) headline
  measures at +1 and +2 ticks of worse fills; (30) workload: orders a day, accounts at once, screen hours;
  (31) funded-account lifetime: payouts per funded account before it is lost; (32) worst year and highest-volatility
  period; (33) break-even denial rate: the denial rate at which the design stops making money (reported, never a
  limit); (34) luck against design (S6).
- **The baseline set (comparators).** (35) naive coin harvesting; (36) P-14, P-15, P-16.
- **Supply and speed** (the operator: speed is a positive outcome). (37) trades available per day, per account and in
  total; (38) session coverage: the share of sessions (Asia, London, NY AM, NY PM) with at least one trade, by session;
  (39) longest idle stretch inside the firm's trading day.

Dropped by the operator: firm-rule exposure (the flagged-pattern rate); rule-change sensitivity.

**Limits, the frontier and luck.**
- The lead proposes the limits on what a user feels from the re-baseline on the search years only (section 3.6 (e)).
  The operator approves them before use, and they are pinned with every other input of section 3.9.
- Each limit states its direction: a floor (for example supply) or a ceiling (for example bankroll, or trades per day
  as workload).
- A limit is set at the operator's value with no noise margin of its own. Noise is allowed for once, in section
  3.8 (a)'s check.
- The operator's condition carries (E-015): **the limits must not fail profitable models by being too strict.**
  Section 3.8 (a) and the power gate of section 3.7 enforce it.
- Every reading reports the frontier over the measures and a menu under the limits.
- A user's first quarter is mostly the day they start, not the design (`results/user_drivers.csv`, section
  `design_vs_luck`). The honest promise is a distribution, and the coin-seed spread is reported as the user's payout
  variance.
- Not modelled, and said so wherever a scorecard appears: the user's time, taxes.

## 3. The method and the pass line

**3.1 Model each firm exactly.** Verified rules only (`config/rules_extended.yaml` through `extended/firm_terms.py`;
`/verify-rule`; section 4). Each firm has its own execution protocol, never Topstep's reused (the operator, E-202). Each
firm's search declares its own baseline set, at least the naive coin on that firm's own protocol.

**3.2 Zero edge, for every entry type.**
- The fill -- its time, price and supply -- comes from the real order.
- **Direction removed.** After the fill, the price path is reflected about the fill price with probability one half,
  by the coin of the declared seed. For a market entry this is exactly a fair coin choosing the side. For a resting
  entry (a limit or a stop) the fill conditions on the path, so a coin choosing the resting side does not remove
  direction (E-203 B-1, E-204 NB-1). The reflection does, while keeping the timing, resolution speed and clustering
  that the real order produced.
- **What the reflection does not remove.** For a symmetric bracket (the stop equal to the target), the reflected gross
  expectation is zero on every path. For any other bracket, the reflection keeps the path's serial structure (momentum,
  mean reversion), whose sign depends on the bracket's orientation. The reflection alone is therefore not zero edge.
- **The martingale-outcome reading, which decides.**
  - Each trade's outcome is redrawn at the driftless first-exit probability of its own bracket (stage one's
    `adapter.BinaryDraw` form, as Stage 2 D-150 used it), keyed by the declared seed.
  - Fills, timing, costs and resolution stay as run.
  - The redraw's form for a trade that ends at a time limit (the flatten, or a max hold) is declared in the search
    template, with zero gross expectation.
  - It is applied identically to designs and baselines. Every deciding reading of section 3.8 is this one.
- **Beside, never credited:**
  - the as-walked (reflected) result, and its gap from the martingale-outcome result, reported as the design's
    **path-structure edge**;
  - the **as-traded** result (the real resting side, unreflected), as a stress, with E-204's decomposition.
- RL3's same-bar pair is one realisable case of the reflection rule (E-204: a coin chooses the fade limit or the break
  stop at the same level from the same ticket, the mirror filled on the same bar).
- Signal sources still matter: they set *when* trades happen (timing, resolution speed, clustering), and they are
  compared with the naive coin.
- Stage 2's `verdict` arm (each R shifted to its edge's lower bound) is not used (section 3.10). The martingale-outcome
  reading takes its place.

**3.3 Map the lever space, then search it with a model.**
(a) Declare the lever space: every lever, with its range taken from the firm's verified rules, in volatility units
where sensible (a stop as a multiple of recent range, with dollar caps), so that a setting means the same thing across
the development window's volatility drift (RD-04). No lever range, volatility unit, regime threshold or component
schedule may read the held-out years (E-208). A lever range comes from contract arithmetic, the verified rules, or an
RD map's search-year rows only. A range drawn from a whole-window row is redrawn on the search years, and its source is
entered in the held-out read ledger (3.6 (b)).
(b) Survey: a space-filling sample of designs on the search years, of a size declared in advance.
(c) Fit a surrogate model that predicts each measure from the levers: which levers move which measures, where
trade-offs are unavoidable, and where the ruin chance jumps.
(d) Propose the next round inside the limits (constrained, multi-objective Bayesian optimisation); run it; refit;
repeat for a declared number of rounds.
(e) Prefer plateaus to peaks: a finalist's neighbours must also do well. The plateau rule's metric and radius are
pinned with section 3.9's inputs.
(f) Log every design tried in the variants ledger (`results/variants.jsonl`) with its manifest. The map and the ledger
persist, so the next firm, lever or model starts from them. **No held-out result is ever written where a later search
can read it**, neither in the map nor in the ledger.
(g) **The latency L is a searched lever** (E-202 (2)(c)). Its values (five the reference, three and two counted
variants) are declared before any read. Every L tried is counted in the variants ledger and in the multiplicity, and
nothing is chosen after a look. Each finalist is tested at its own L. The five-minute cell is reported beside every
finalist, and read and reported in the held-out test -- reported, not tested. RL3 is latency-free (E-204), so its latency cells collapse to one.

**3.4 Signal sources are a lever.** Two or three models (and the coin) whose trades differ in timing and shape,
rotated across accounts, can keep each account's variance (which the asymmetry rewards) while lowering the correlation
between accounts (which steadies the total). Which models, their shares and their account assignment are levers in the
same search. A model is judged on what it adds to the mix, not on its backtest alone. **Hard rule:** never opposing
positions at once across accounts or firms (conduct tier 1, section 4); one position at a time across a firm (Stage 2
D-429) stays.

**3.5 Design rules (the operator; every design obeys them).**
- **Many trades, fast.** Supply and speed are objectives: more opportunities mean faster passes and payouts. The
  search rewards supply (37) and speed (1, 5, 9) inside the limits; the ruin chance (24) is the counterweight.
- **Multiple sessions.** A design is a schedule of components across every session the firm allows (Asia, London,
  NY AM, NY PM), each with its own trigger and its own trade shape, since each session's volatility differs.
  Components are judged by what they add to the whole design.
- **Triggers are judged on their properties, not their accuracy:** supply, timing, resolution speed for a given shape,
  clustering, how differently they are timed from other components, and whether they can be executed by hand.
- **Hand-executable.** At least L minutes from alert to order, L a declared parameter: five the reference, three and
  two counted variants declared before any read with the five-minute cell beside every pick (the operator,
  E-202 (2)(c)), counted in the cells and the multiplicity, nothing chosen after a look (3.3 (g)). So a trigger must be
  known L minutes ahead (scheduled times, or resting orders at levels known in advance). Components' windows are
  scheduled not to collide (one position at a time across a firm). Every execution rule of section 4 holds.
- **Any hour.** There is no cap on trading hours (the operator, 2026-11-18; E-202 (2)(b)). Every session the firm
  allows is in the search, and any valid component found in any of them can be approved. Workload (30) is reported;
  a workload ceiling applies only if the operator sets one as a limit.
- **The side rule** (part of every design; **pending the operator, O-4**). The zero-edge evaluation convention (3.2)
  is not the operator's choice, and it stands. Which side a user actually trades is the operator's.
  - **The candidate default** is the evaluated object: one literal coin draw per moment, shared by all the user's
    accounts and firms.
  - **Under any side rule** (3.4's hard rule): while any position is open in the user's accounts, a new trade's side is
    that position's side, or the trade is skipped, so no two of the user's positions are ever opposite (conduct
    tier 1). The evaluation uses the same rule.
  - **Until O-4 is ruled,** every playbook states the coin side, with the model-side and as-traded readings beside, and
    no playbook goes to a user.
  - **Model sides** appear only beside. A playbook may give a model's side only if it clears the **no-harm floor**:
    its composite on the search years is not below the coin side's by more than the margin pinned in 3.9. Its held-out
    reading is reported beside, never judged.
  - **A resting trigger traded as its real order** (one with no realisable construction; RL3's pair is one that has
    one) clears **the same no-harm floor**: its as-traded composite on the search years is not below the reflected one
    by more than the margin pinned in 3.9. Its held-out as-traded reading is reported beside, and it meets 3.8 (c)'s
    as-traded floor.
- **The output is a playbook.** Each finalist is written as a one-page set of rules (triggers, side rule, shapes,
  account policy, schedule) plus the exact alert format, so that it can be traded by hand.

**3.6 Held-out years and the three-way test.**
(a) **The split** (E-208): search years 2020-01-02 to 2023-12-29; held-out years 2024-01-02 to 2026-07-16, on
`results/q82_judged_sessions.csv`. "Held out" means two things: unread by the search's code, and unused by any choice
in its declaration (lever ranges, volatility units, regime thresholds, schedules, limits, budgets, weights).
(b) **The held-out read ledger.** Every search declaration carries every past read of the held-out years for its
comparators and its trigger families, in RD-04's leak-clause form ("written after this reading; no figure cited").
Known entries today:
- Stage 2 D-626: P-14 fixed as R\* from the whole window.
- E-203 S-2: P-14's rung map and P-16's mark cutoff resolved on the whole window.
- Stage 2 D-554: P-16's stop chosen on each block.
- RD-04 (c): P-14 and P-16 replayed on the late block.
- RD-05: the late block read as late development.
- Q-17 and E-201: every user measure read beside the baselines.
- Stage 2's signal search over the whole window.
- RD-03's whole-window lever readings.
- Stage 2's program U: every one of its nine families read P on the late block against P-14 (RD-02 records it).
- RD-02's late-block menu of payout policy, whose levers are now in the lever space.
- Any RD-01 late-block reads.

The list is a floor: each declaration completes it.

When the ledger is not empty, the level is printed as **nominal** beside the verdict (E-203 S-2's form). For the
Topstep NQ search it is not empty: Stage 2's baselines were chosen on the whole window, so for them "held out" means
unread by this search only (E-208).
(c) **Single use per market.** The held-out years are read by one held-out test per market. Which firm's search
spends NQ's held-out years, or whether one search covers several firms, is the operator's, pending (O-1). After that, a later
search on the same market's bars cannot carry on them. Either its reading there is a description only, or its held-out
years move to data not yet read (the confirmation window, or more history), which is a purchase or the operator's
setup. A held-out test on such data spends its own k.
(d) **The horizon embargo.**
- A search-year start is read at horizon h only if h sessions remain inside the search years. This purges, at the end
  of the search years, a strip as long as the longest horizon read: twelve months for the 12-month measures, and
  D-145's horizon for the long-run gate.
- A held-out start reads only held-out sessions for its outcomes, and it is read at h only if h sessions remain before
  2026-07-17.
- Causal look-backs from a held-out start into the search years (volatility normalisers) are allowed.
- So the held-out years hold fewer complete long-horizon starts. The power gate (3.7) counts that cost.
(e) **The re-baseline (H4)** reads the search years only, with its runner refusing held-out sessions (RD-04's guard
pattern). If any held-out output is computed, it is written sealed (its hash recorded, the file unopened) until the
held-out test.
(f) **The three-way test.**
- (i) **The coin-seed leg, which carries the level** (E-208). Each finalist and each baseline run on the same seeds
  and the same start days (paired). The replicates are disjoint coin-seed sets on the fixed held-out history. The
  statistic is fixed in the declaration. The hypothesis: on the held-out years, the design beats the baseline in
  expectation over coin draws. **The leg's level bounds coin luck given the held-out history; it does not bound a
  favourable history.** The history null's false-pass rate (3.7) is the reading for that.
- (ii) **The time leg, a declared consistency condition** (E-208), not a test at the level. On the held-out years, the
  difference holds in most years (a count pinned with 3.9's inputs) and in both volatility regimes, with regime
  thresholds from the search years or a rule fixed in advance. History blocks are its unit, at least as long as the
  composite's longest horizon. A regime absent from the held-out years is reported beside, not required.
- (iii) **The held-out leg.** (i) and (ii) are read on the held-out years only.

The coin-seed spread is reported: it is the user's payout variance.
(g) **The reverse reading** (choose on the held-out years, judge on the search years; section 6's "the reverse
beside") is not run before the held-out test. Afterwards it is run only as a described reading.

**3.7 The held-out test: finalists, calibration, power and the budget.**
- **Finalists.** An ordered list of finalists, produced on the search years by a rule declared before the survey and
  pinned before the held-out read. They are tested by fixed-sequence testing, each at the full level of the search's
  k, stopping at the first failure (E-203 S-1's precedent): one k for the sequence. The fallback (3.9) is pinned in
  place of the composite, never tried after it.
- **Calibration.** The exact pinned rule (the composite or the fallback, the limit checks, the time leg's conditions
  and the floors, all on the martingale-outcome reading) is calibrated as a whole (E-007 (f)). **The deciding run
  follows section 3.9's pinning row** (after Wave 4.2) and precedes the search's pin. H3's earlier runs, as queued
  (E-208), are design checks only.
  - **Same-design nulls:** a design against its **antithetic twin** (every coin side reversed), and the same design on
    **two disjoint seed sets**. Each pair has distinct realisations and equal expected composites by construction. They
    check the coin-seed leg's size.
  - **The history null:** distinct designs whose composites are equal in expectation across histories but differ on
    any one history. One construction: two components on synthetic paths carrying NQ's dependence, exchangeable under
    the generator's symmetry (the same law in two sessions, or mirrored schedules). The whole rule's pass rate on them,
    across synthetic and history-block-resampled histories, is **the history-level false-pass rate**, printed beside
    every verdict. Whether exact equality in expectation holds for the composite's quantile-type dimensions is settled
    in H3's declaration.
  - **History blocks are the unit of replication** for the nulls' resampling and for the time leg, with blocks at
    least as long as the composite's longest horizon. Overlapping start-day windows are calibrated per horizon (Q-16,
    E-208). Within the coin-seed leg, seed sets are the replicates.
  - The rule must reject the same-design nulls no more often than its level. This is H3, re-specified on the pinned
    rule, with the history null in the same run.
- **Power gate** (before any search is pinned).
  - The whole pass line's power at the level of its k is measured on synthetic paths carrying NQ's dependence, with
    **design pairs drawn from H4's baselines and from synthetic plants**, and with a planted improvement of **the size
    that matters (the operator's, set in Wave 4.2; O-3)**. It applies the horizon embargo of 3.6 (d), at the declared
    power target.
  - In the same run, a design equal to the best baseline on every limit must pass every limit check, in the form in
    force (3.8 (a)), with at least the power target.
  - **The count of held-out starts complete over D-145's horizon** is stated. It must reach the minimum pinned in 3.9
    for the gate's quantile to be read.
  - If any of these fails, the search does not pin.
  - Exit (B) states the line's power from this gate. It replaces E-007 (e)'s "minimum detectable difference before the
    read".
- **Open operator item (E-007 (2), the data decision; asked before the first search is pinned, not after a
  failure).** Should more history be added (QuantConnect's free NQ/ES from 2009, which needs the operator's setup; or
  a Databento purchase of older bars, stated, not authorised), so that the held-out test has power? The lead puts the
  question with the power gate's result. The operator decides.
- **The budget.** Each held-out test spends one k at 0.05 / (k (k + 1)); the confirmation spends none.
  - E-204's rule is carried in full, with "held-out test" in place of "stage B": a search whose declaration assigns
    its k at its held-out row is not counted by the gatekeeper's k rule until that row exists; if another declaration
    pins between its held-out run and that row, the held-out run is repeated at the new level under a repeat row.
  - **The multiplicity budget continues Stage 2's program U** (E-001): numbers are given in declaration order across
    both repositories. Stage 2 declared and closed nine (`results/u_*.csv`). This repository's F-01 (k = 10) was
    withdrawn with its k spent (E-007), F-02 retired k = 11 unspent (E-094, E-095), and F-03 spent k = 12 (E-192). The
    next is k = 13.
  - A new repository does not refresh the budget: the data, the baselines and the researcher are the same.
  - A design that passes is **carried**, and only a carried design takes a registration id.

**3.8 The pass line.** A finalist passes, in its place in the sequence, when (a), (b) and (c) all hold. **Every
deciding reading below is the martingale-outcome reading of 3.2, for the finalist and for every baseline alike.**

(a) **Limits.** Two forms are written side by side until the operator rules (O-5).
- **In force (the operator's confirmed words, E-207):** the finalist stays inside every operator limit with a margin
  wider than its noise. That is the one margin, applied once; the limits carry none of their own.
- **Pending the operator (O-5; the red team's B-10):** a limit fails the finalist only if a one-sided check, at a level
  pinned with 3.9's inputs, shows that the finalist crosses it. Until O-5 is ruled, this form is computed and reported
  beside, never deciding.
- Under either form, E-015's condition -- the limits must not fail profitable models by being too strict -- is enforced
  by the power gate's limit clause (3.7). A pinning row whose limits would fail a design equal to the best baseline, at
  the target power, does not pin.

(b) **Each baseline beaten.** The finalist's composite (or the pinned fallback) is above **each** baseline's, an
intersection-union test with every comparison at the full level of the search's k. The test is the calibrated
coin-seed leg on the held-out years, with the time leg's conditions met (3.6 (f)).
- **What the level bounds.** The printed level 0.05 / (k (k + 1)) bounds coin luck, given the held-out history. It
  does not bound a favourable history. A design no better than the baselines across histories, but whose shape suited
  the held-out years, can pass. That second risk is read from the history-level false-pass rate (3.7), printed beside
  every verdict, and from the time leg. The confirmation (section 5 (A)) is the only test on a fresh history.
- Every baseline runs under the design's convention: 3.2's reflection and martingale-outcome reading under the same
  seed keying, the same fill and cost mechanics, no arm shift, and the same verdict settings.
- **Latency.** Each baseline runs at its registered latency (P-14 at five minutes; P-16 scheduled, its latency
  variants dropped, E-203 B-2), which its runner identity checks: each baseline's trade times and brackets equal its
  registered ones, path for path. "The same latency model" means the same mechanics. Every comparison states the
  finalist's L and each baseline's L.
- The registered rows are reported beside.

(c) **The floors.**
- Verified rules.
- Conduct tier 1.
- Section 4's constraints, every trade resolving among them.
- Hand entry at least L minutes from alert to order (3.5).
- **The zero-edge long-run gate:** the median log growth (Stage 2 D-14) of the required bankroll over D-145's horizon,
  above zero at a lower quantile over coin seeds and history-block resamples pinned with 3.9's inputs. It is read on
  starts complete under 3.6 (d), whose count must reach the pinned minimum (3.7).
  - On the martingale-outcome reading, with no shift of outcomes.
  - Fees, payout latency, the tier-2 consequences and D-145's tier-3 denial probability of 25 % applied, with the
    0 % reading beside.
  - It replaces D-145's shift of outcomes to the lower bound of e. Under 3.2 that shift has nothing to estimate:
    direction is removed by the reflection and the path's structure by the redraw, so a sample estimate of e would be
    noise.
- **Fill and supply stress:** at +1 tick of worse fills (29) and with 10 % of signals missed (28), the finalist still
  beats each baseline on the composite at the point estimate, both under the same stress, and stays inside every limit
  in the form in force.
- **As-traded floors** (resting triggers traded as their real orders, 3.5):
  - the no-harm floor on the search years;
  - on the held-out years, with as-traded sides, the finalist still beats each baseline on the composite at the point
    estimate, each baseline read the same way.

**The verdict** is read on the martingale-outcome reading, at 0 % payout denial, the Responsible Trading Program's
placement off and the Focused Trader Program off (the operator, E-008 (2); E-007 (3); Stage 2 D-234, D-289). The level
is printed nominal when the ledger is not empty, and **the history-level false-pass rate is printed beside it**.
**Also beside it:**
- the denial ladder; the break-even denial rate (33); the placement on; the binding Focused Trader models;
- P by month; mean net; CVaR10; P under a bankroll limit; the effective sample size (E-007 (e));
- the as-walked result and the path-structure edge (3.2), never credited;
- the as-traded stress of resting triggers;
- the model-side reading, where a playbook uses one (3.5);
- the limit check in the pending form (O-5).

**3.9 The objective is a combination, fixed before the survey.**
- **Search: every measure at once.** The search is multi-objective: the surrogate models every measure and reports the
  frontier.
- **Measure structure.** On the re-baseline (H4, search years only), find which measures carry independent information
  and which move together (the expected dimensions: speed, cost and bankroll, steadiness, downside, supply, workload),
  and the trade-off curves between them. With only the four baselines in H4, the dimensions come from variation
  across start days and seeds, not across designs, so the trade-off curves put to the operator are not curves across
  designs.
- **The operator's weights.** From those curves the operator answers concrete trade-off questions. The answers set the
  weights of a **composite score** over the dimensions. One of the dimensions is P under the bankroll stop (the share of
  users with the operator's budget who are ahead in cash at months 1-3, `p_by_month` with `spent` and `limit`). S3c
  (14) is not a dimension.
- **One row pins every input of 3.8 and 3.9 before the survey runs:**
  - the limits (values, directions, the noise margin of the form in force, the check's level of the pending form);
  - the bankroll budgets of (24);
  - the dimension definitions and their normalisers or loadings;
  - the weights;
  - the composite **or** the fallback (one, never both);
  - the size that matters (the operator's, set in Wave 4.2; O-3) and the power target;
  - the regimes and "most years";
  - the finalist order rule and the plateau rule;
  - the gate's quantile, and the minimum count of held-out starts complete over its horizon;
  - the no-harm margin for model sides and for as-traded resting triggers (one margin for both, unless the row
    names two);
  - the L values in the lever space.

  All are set from the search years only. None is changed after a search-year result except by re-declaring the
  search.
- **Limits stay hard lines** in the form in force (3.8 (a)): no score buys crossing one.
- **The held-out test reads the pinned objective once**, along the finalist sequence of 3.7. The frontier and every
  measure are reported beside. **Fallback:** if the weights cannot be set before the pinning row, that row pins P under
  the bankroll stop alone, with the rest as limits. It is never invoked after a look.

**3.10 On record, no longer deciding.** These are kept as their rows adopted them and decide nothing from E-NNN on:
- the trades' lift over the coin twin on the same brackets, and its value-map bar, as the pass line (E-008 (1); Q-16's
  statistic stays available as a description);
- R\* = P-14 as the one row to beat (Stage 2 D-626; P-14 is now one baseline among four);
- Stage 2 D-621 (3)'s rule as E-001 adopted it (its text is CHARTER section 3 at E-008's sha256);
- E-015 (3)'s "a limit never fails a design", replaced by 3.8 (a)'s limit check (E-207's form in force, the
  one-sided form pending the operator, O-5), with E-015's operator condition carried;
- E-023's two rules (no-trade levers described, never carried; side-keeping filters against a placebo-selection
  twin): such levers and filters are now searched in the lever space;
- Stage 2's `verdict` arm (each R shifted to its edge's lower bound) and D-145's edge-bound form of the gate, both
  retired: the martingale-outcome reading takes their place (3.2, 3.8 (c)).

## 4. The constraints a model lives inside

Stage 2's handoff section 2, unchanged: the firm rules in Stage 2's verified ledger (`vendor/stage2/config/rules.yaml`,
`RULES_LEDGER.md`; an unverified rule is never loaded); the stop band and cost floor (`results/stop_band.csv`); stage
one's zero-edge ceilings as oracles (an output outside them is an engine error); the execution rules -- at least L
minutes from alert to order, L a declared parameter: five the reference, three and two counted variants declared before
any read with the five-minute cell beside every pick (the operator, E-202 (2)(c)) (a resting order may go live L minutes after its
ticket and then fill at its level),
one position at a time per firm with five minutes flat between trades, every trade resolving (at most 5 % reach the
15:10 CT flatten, Stage 2 D-212 as D-308 raised it from 2 %; no time stops), realised risk matching intended (at least
90 % of trades within 10 % of the state's risk in whole micros, Stage 2 D-212 -- read, as P-14's registration read it,
in its allowance-capped form: the intention is the size the engine's sizing gives under the firm's allowance and the
Combine's room, E-022 (1), E-032), no entry before 07:35:00 CT on a BLS
08:30 release day (strictly after it, E-007) and FOMC days out, each account carrying its own trades; and the three
conduct tiers (Stage 2 D-145: no hedging across accounts or firms, no simulator-fill exploitation, no maximum size into
major news, nothing that conceals a pattern). No automated or API order entry -- **the operator's rule** (Topstep's
pages permit automation through its paid API; the operator kept hand entry, E-008): every trade is placed by hand at
least L minutes after its alert (L as above). Designs are for one user's own accounts; a signal service whose users place the
same tickets is out (Topstep's coordinated-trading prohibition, E-007 (c)).

**Amended (E-NNN), from the operator's rulings E-202 (2)(a) and (2)(d):** no entry and no fill inside any verified news
window, and a position open at a window's start is flattened under E-200 R-1 (RL3's 08:30-08:59 fill window stays
closed); limit (resting) entries go live at the latency, fill only on a trade-through by one tick, and are cancelled at
a news window's start.

**Amended (E-NNN), the oracles under the zero-edge convention (section 3.2):** stage one's zero-edge ceilings are read
on the martingale-outcome reading, where an output outside them is an engine error as before. An as-walked (reflected)
result outside them is the path-structure edge of section 3.2: it is reported beside the verdict, never booked as an
engine error, and never "fixed" as one.

## 5. Exit criterion -- either is a valid close

- **(A)** A design CARRIED under section 3.8, meaning: its held-out test passed (its level printed nominal if its
  ledger is not empty, the history-level false-pass rate beside) and audited, and its playbook written. Then its one
  confirmation on the confirmation window is read against **a criterion declared at its registration, before the
  read**, and reported (a purchase, the operator's). At the least, the criterion requires that on the
  martingale-outcome reading the design is ahead of each baseline on the composite at the point estimate and inside
  every limit in the form in force. The frontier, every measure of section 2 and the rules ledger are verified with it.
  The confirmation is the only test on a fresh history; it spends no k.
- **(B)** A documented negative result: no declared search yields a design that passes, with every search's evidence,
  its count and the pass line's power from its power gate (section 3.7).

Either way: every declaration and outcome on record, the decision log complete, every number traced to a result file
with a manifest, Stage 2's vendored tree unedited and its identity holding.
````

**What changed against the current charter** (for the lead's diff):
- Section 2: the objective, the terms (with E-208's split) and the measures (37 plus the baseline set). The S-keyed
  table and the "Why S3c screened" paragraph are dropped, and S3c's within-stream rule is kept on measure (14). The
  `verdict` arm is replaced by the zero-edge convention. Limits have no margin of their own, and E-015's condition is
  carried. The bankroll-stop line is removed from "not modelled".
- Section 3: the plan's 4.1-4.8 and 4b, plus the cycle-1 rulings, renumbered 3.1-3.10.
- Section 4: the current paragraph is unchanged byte for byte, with two marked paragraphs added (m-2; V-2).
- Section 5: (A) uses "held-out test", "confirmation" and "playbook"; (B) states power. "The sizing at the edge's lower
  bound" is dropped (zero edge).
- Cycle 2:
  - 3.2: the martingale-outcome reading, and the path-structure edge beside;
  - 3.7: the history null; R-4's count of complete starts;
  - 3.8: the scope of the level (b); the as-traded floors (c); the limits' two forms (a, O-5);
  - 3.5: the side rule pending O-4, with the open-position rule;
  - section 4: the oracles' reading;
  - 5 (A): the confirmation's declared criterion;
  - the ledger and lever-source fixes.

---

## 2. CLAUDE.md, "The objective (CHARTER section 2)"

Replace the paragraph at `CLAUDE.md:20-26` (from "**Judged on trades first" to "the next is k = 13.") with this block.
The heading at line 18 stays. The block has fewer words than the current paragraph. Nothing else in CLAUDE.md changes
(flag R-8 lists other lines that are now stale).

```markdown
**Judged on the user's journey (the operator, E-207, E-NNN; amending E-008):** a user's best journey to making money --
least bankroll, fastest, cheapest pass and payout, steady income, least ruin -- under zero edge (direction removed,
each outcome redrawn at its bracket's driftless odds; the traded side rule pending the operator). A design passes only
if it stays inside every operator limit with margin wider than its noise; beats each baseline (naive coin, P-14, P-15,
P-16, same convention) on the composite pinned before the survey (fallback: P under the bankroll stop) by the
calibrated coin-seed test at 0.05 / (k (k+1)) on the held-out years, read once -- bounding coin luck on that history,
not a lucky history (the history null's rate beside); and holds the floors. Verdict: 0 % payout denial, placement off.
One k per held-out test: k = 10 spent (F-01, E-007), 11 unspent (F-02, E-094, E-095), 12 spent (F-03, E-192); next 13.
```

---

## 3. DIRECTIVE.md

The grep `grep -n -i "coin twin\|lift\|trades first\|E-008" DIRECTIVE.md` finds five lines: 17, 92, 104, 112 and 118.
Seven more passages are stale in substance, and all are answered below:
- lines 3-4, the preamble;
- line 16, the mapping row for the row to beat;
- lines 38-46, Part 3;
- lines 56-57, Part 5's worktree list;
- lines 83-85, Part 5's progress report;
- lines 120-122, 6.3 C;
- lines 126-128, the power paragraph;
- lines 130-132, "A candidate".

**How to apply them:** in place, under E-NNN, as E-203 edited Parts 1 and 6.2 in place. Each change is listed in the
mapping table, and the preamble says so (D-0). Part 3 is now edited in place too (m-9), because stale text below the
table misleads whoever reads Part 3 directly.

**D-0. The preamble, lines 3-4.**
- Current: `copied byte-exact from Stage 2 commit a5708aa; sha256 in E-005). They are not edited here; a change is a decision row.`
- Replacement: `copied byte-exact from Stage 2 commit a5708aa; sha256 in E-005). They are not edited here except where a decision row amends them in place (E-203: Parts 1 and 6.2's latency; E-NNN: the journey objective in Parts 3, 5 and 6); every such amendment is listed in the table below.`

**D-1. Mapping table, line 16.**
- Current: `| the row to beat P-14, the family level 0.05/(k(k+1)) | as \`CHARTER.md\` section 3 fixes them (E-001: this repository's first family is k = 10) |`
- Replacement: `| the row to beat P-14, the family level 0.05/(k(k+1)) | the baselines -- naive coin harvesting, P-14, P-15, P-16, each under the design's convention -- and the level 0.05 / (k (k + 1)), one k per held-out test, as \`CHARTER.md\` sections 3.7-3.8 fix them (E-001: the program's first family here was k = 10; the next k is 13) |`

**D-2. Mapping table, line 17** (grep hit).
- Current: `| Part 3: P primary, payouts per fee dollar the screening target | **amended by the operator (E-008):** a design is judged on its trades first (lift over the coin twin, calibrated, at the family's level); P, the guarded measures and the frontier are reported beside against P-14; the verdict keeps 0 % denial with the placement off; hand entry only stays |`
- Replacement: `| Part 3: P primary, payouts per fee dollar the screening target | **amended by the operator (E-008; then E-207, E-NNN), and Part 3 rewritten in place:** a design is judged on the user's journey under zero edge (\`CHARTER.md\` sections 2-3), on the martingale-outcome reading: inside every operator limit with margin wider than its noise (E-207; the alternative form pending the operator, O-5), each baseline beaten on the composite pinned before the survey (or the pinned fallback, P under the bankroll stop) by the calibrated coin-seed test on the held-out years (a level bounding coin luck on that history; the history-level false-pass rate beside), the time leg a consistency condition, with the floors of CHARTER section 3.8; the trades' lift over the coin twin is no pass line; the verdict keeps 0 % denial, the placement off and the Focused Trader Program off; hand entry only stays |`

**D-3. Line 92, Part 6.1** (grep hit). **Keep unchanged.** It records a historical finding of Stage 2's handoff, not a
pass line, and it still holds.

**D-4. Line 104, Part 6.2, "The test"** (grep hit).
- Current:
  ```
  - **The test:** lift over the coin twin on the same brackets, then valued with the value map; supply and resolution
    gates before any outcome is read.
  ```
- Replacement:
  ```
  - **The test:** a signal source is judged by what it adds to a design's journey under zero edge (`CHARTER.md`
    sections 3.2-3.8): its fills from the real orders, the path after each fill reflected with probability one half
    and each outcome redrawn at its bracket's driftless odds for the deciding reading, over paired seeds, its properties read -- supply, timing, resolution speed for a given shape, clustering, how
    differently timed it is from other components, hand-executability; supply and resolution gates before any outcome
    is read; nothing read on the held-out years outside a held-out test. The lift over the coin twin is no pass line
    (E-NNN).
  ```

**D-5. Lines 109-113, Part 6.3 A** (grep hit at 112; it also still said "5 minutes", which E-203 missed).
- Current:
  ```
  - **A. Resting-order levels** (`wt-levels`): levels known before they trigger (prior day high/low, overnight
    high/low, opening-range high/low after it closes, frozen session-VWAP bands, round numbers, prior swing points);
    stop-entry for a break and limit for a pullback; the ticket published at least 5 minutes before it can trigger;
    R values and an expiry fixed in the row; fill rate and adverse selection measured; lift over the coin twin valued
    by the value map; family-wise level by its k.
  ```
- Replacement:
  ```
  - **A. Resting-order levels, as triggers** (`wt-levels`): levels known before they trigger (prior day high/low,
    overnight high/low, opening-range high/low after it closes, frozen session-VWAP bands, round numbers, prior swing
    points); stop-entry for a break and limit for a pullback; the ticket published at least L minutes before it can
    trigger (L = 5 the reference; 3 and 2 counted variants, E-202); R values and an expiry as levers in the declared
    lever space; fill rate and adverse selection measured; judged under `CHARTER.md` section 3.2's zero edge (the path
    after the fill reflected with probability one half), the as-traded result beside as a stress; RL3 recast as an
    NY AM component, F-02 parked (E-208); one k per held-out test.
  ```

**D-6. Lines 114-119, Part 6.3 B** (grep hit at 118).
- Current:
  ```
  - **B. Feature library, then one multi-feature model** (`wt-features`): 30-50 normalised OHLCV features; two targets
    -- resolution speed (expected to be predictable) and direction (expected to be hard); one pre-registered model
    (a shallow gradient-boosted tree or a regularised logistic regression) with its hyperparameters fixed or searched
    inside the declared walk-forward only; purged and embargoed splits longer than the longest trade; judged out of
    fold by lift over the coin twin. Rules read off the model afterwards (SHAP and the like) are exploratory and need
    their own family.
  ```
- Replacement:
  ```
  - **B. Feature library, then the lever map's surrogate** (`wt-features`): 30-50 normalised OHLCV features, kept as
    components for triggers' timing and resolution speed (`feature-rules` binds every source that reads bars); family
    B as a direction model is parked (E-208: Q-14, Q-95, Q-149; `features.py` and the B2 machinery kept); the
    machine learning is the surrogate over the lever space (`CHARTER.md` section 3.3) -- fitted on the search years'
    survey, proposing each round inside the limits, its method, rounds and seeds declared and every design it tries
    counted. Rules read off it afterwards (SHAP and the like) are exploratory and need their own declaration.
  ```

**D-7. Lines 130-132, "A candidate".**
- Current:
  ```
  **A candidate** is one that beats the row to beat on its judged block at its family's level, holds the guarded
  tolerances, the coin guard and the long-run gate floor. It is then registered with the gatekeeper, audited, and
  waits for confirmation data (a purchase: the operator's).
  ```
- Replacement:
  ```
  **A candidate** is a finalist of a declared search that passes `CHARTER.md` section 3.8 in its place in the finalist
  sequence on the held-out years, on the martingale-outcome reading: inside every operator limit with margin wider than
  its noise (E-207; O-5 pending), each baseline beaten on the pinned composite by the calibrated coin-seed test at its
  k's level (the history-level false-pass rate beside), the time leg's conditions met, the floors holding (the
  zero-edge gate, the fill and supply stress and the as-traded floors among them). It is then registered with the gatekeeper, audited, and waits for
  confirmation data (a purchase: the operator's).
  ```

**D-8. Lines 83-85, Part 5's progress report.**
- Current: `give the progress report (the scorecard against the row to beat with the variant count; each family closed, carried or running with one line why; what changed the picture; what the data cannot show; three to five next tasks), and wait.`
- Replacement: `give the progress report (the scorecard against each baseline inside the limits, with the variant count; each search's round, its finalists, its held-out read ledger, and each design closed, carried or running with one line why; what changed the picture; what the data cannot show; three to five next tasks), and wait.`

**D-9. Part 3, lines 38-46, in place** (m-9).
- Current: the section from `## Part 3. The objective (from the handoff, section 1)` to `...so a design that helps users but cannot grow is visible.`
- Replacement:
  ```
  ## Part 3. The objective (from the handoff, section 1; amended by the operator, E-008, E-207, E-NNN)

  Find the way of running prop-firm accounts that gives a real user the best journey to making money: the least
  bankroll, the fastest and cheapest path to a pass and a payout, a steady income, the lowest chance of going broke
  first -- under zero edge (`CHARTER.md` section 3.2). Judged on the journey measures (`docs/MEASURES.md`) under the
  operator's limits, against each baseline (naive coin, P-14, P-15, P-16, each under the design's convention), on a
  composite score pinned with every other input before the survey (fallback P under the bankroll stop, pinned instead,
  never after), by the calibrated coin-seed test on the held-out years, read once per market, with the time leg a
  consistency condition (`CHARTER.md` sections 3.6-3.8). Report the frontier and a menu under the limits, never one
  number. A floor, always: the zero-edge long-run gate (`CHARTER.md` section 3.8 (c)), so a design that helps users but
  cannot grow is visible.
  ```

**D-10. Lines 56-57, Part 5's worktree list** (m-9).
- Current:
  ```
  - `wt-levels` -- the resting-order level family (Phase 1, family A).
  - `wt-features` -- the feature library, then the multi-feature model (family B).
  ```
- Replacement:
  ```
  - `wt-levels` -- signal sources and the mix: the trigger library by session, the naive coin, the component
    scheduler, the mix router and its no-opposing-positions guard (E-208).
  - `wt-features` -- the lever map and the search: the lever-space sampler, the surrogate, the round proposer, the
    plateau check (E-208).
  ```

**D-11. Lines 120-122, Part 6.3 C** (m-8, m-9).
- Current:
  ```
  - **C. Other firms' contracts** (`wt-firms`): firms with end-of-day drawdown or no consistency rule, verified on their
    own pages; a solver-only contract-fit read first (payouts per fee dollar against Topstep's $50K), a campaign family
    only if it clears a declared bar.
  ```
- Replacement:
  ```
  - **C. Other firms' contracts** (`wt-firms`): firms with end-of-day drawdown or no consistency rule, verified on their
    own pages; each firm its own execution protocol and its own baseline set, at least the naive coin on its own
    protocol (E-202); a solver-only contract-fit read first, described; a design search for the firm only under
    `CHARTER.md` section 3, its held-out years subject to their single use per market (section 3.6 (c)).
  ```

**D-12. Lines 126-128, the power paragraph** (B-9).
- Current: `... is the operator's call -- put both in \`OPERATOR_SETUP.md\` in your first commit.`
- Replacement: `... is the operator's call -- put both in \`OPERATOR_SETUP.md\` in your first commit, and put the question to the operator with the power gate's result before the first design search is pinned (\`CHARTER.md\` section 3.7), never after a failure.`

**The mapping table after the edits:**

| the bootstrap says | here |
|---|---|
| decision rows `D-nnn`, a worker's proposed row `D-NNN` | (unchanged) |
| `main` | (unchanged) |
| `OPERATOR_SETUP.md` | (unchanged) |
| `TASK_QUEUE.md`, `STATUS.md`, `PROGRESS.md` | (unchanged) |
| `%LOCALAPPDATA%\<repo>-wt\<name>` | (unchanged) |
| `%LOCALAPPDATA%\<repo>-runs\` | (unchanged) |
| the row to beat P-14, the family level 0.05/(k(k+1)) | D-1's text |
| Part 3: P primary, payouts per fee dollar the screening target | D-2's text |
| Part 1 and Part 6.2: "at least 5 minutes" | **amended in place (E-203):** at least L minutes, L = 5 the reference, 3 and 2 counted variants (E-202 (2)(c)) |
| Part 3, Part 5's worktree list and report, Part 6.2's test, 6.3 A, B and C, the power paragraph, "A candidate" | **amended in place (E-NNN):** judged on the journey under zero edge, not on a coin-twin lift; RL3 recast and F-02 and family B parked (E-208); each firm its own baselines; the data question asked before the first search pin |

---

## 4. Draft decision row (for the lead to number)

```
| E-NNN | 2026-11-DD | **The journey objective put in force (the operator's confirmation, E-207), with the red team's two reads answered (`docs/reviews/AMENDMENTS_2026-11-18.md`, 12 blocking and 10 minor; `docs/reviews/AMENDMENTS_v2_2026-11-18.md`, 3 blocking and 10 minor; corrective cycles 1 and 2 under the lead's rulings): E-008 (1) is replaced.** A design is judged on the user's journey, never on its trades' edge, under the zero-edge evaluation convention for every entry type: the fill from the real order; the path after it reflected with probability one half (direction removed; RL3's same-bar pair one realisable case, E-204); and **every deciding reading on the martingale-outcome reading** -- each trade's outcome redrawn at its own bracket's driftless first-exit odds (stage one's `BinaryDraw` form, Stage 2 D-150), identically for designs and baselines -- because the reflection alone is zero only at a symmetric bracket; the as-walked result's gap is reported as the design's path-structure edge, never credited, and section 4's oracles read the redrawn result. **The traded side rule is pending the operator (O-4):** the candidate default is one literal coin draw per moment shared by all the user's accounts and firms; under any rule a new trade takes the side of any open position or is skipped; until O-4, playbooks state the coin side with the model-side and as-traded readings beside and none goes to a user; model sides and as-traded resting triggers each clear a no-harm floor. **The split (E-208):** search years 2020-01-02 to 2023-12-29, held-out years 2024-01-02 to 2026-07-16 on `results/q82_judged_sessions.csv`; held out = unread by the search's code and unused by its declaration's choices; every declaration carries a held-out read ledger, a floor it completes (Stage 2 D-626, D-554, E-203 S-2, RD-02's late-block menu, RD-03, RD-04 (c), RD-05, Q-17/E-201, program U's nine families' late-block reads of P, Stage 2's signal search, any RD-01 late-block reads), the level printed nominal when it is not empty; lever ranges from contract arithmetic, verified rules or RD maps' search-year rows only; one held-out test per market -- **which firm spends NQ's held-out years, or whether one search covers several firms, is the operator's, pending (O-1)**; no held-out result in the map or the variants ledger; a start read at a horizon only if it fits inside its years; H4 on the search years only, any held-out output sealed. **The pass line (CHARTER 3.8):** (a) inside every operator limit with margin wider than its noise, one margin applied once (the operator's confirmed words, E-207, in force); the red team's alternative -- a limit fails a design only if shown crossed -- **pending the operator (O-5)**, computed beside; E-015's condition carried by the power gate's limit clause; (b) each baseline -- naive coin, P-14, P-15, P-16, under the design's convention at their registered latencies, the registered rows beside -- beaten on the composite (or the pinned fallback, P under the bankroll stop, never tried after it), an intersection-union test at the full level of the search's k by the calibrated coin-seed leg on the held-out years, the time leg (most years, both regimes, history blocks as its unit) a consistency condition (E-208); **the level bounds coin luck given the held-out history, not a favourable history: the history null's false-pass rate is printed beside every verdict**; finalists in a fixed sequence at the full level, stopping at the first failure; L a searched, counted lever, the five-minute cell reported, not tested; (c) floors: verified rules, conduct tier 1, section 4, hand entry, the zero-edge long-run gate (median log growth of the required bankroll over D-145's horizon on the martingale-outcome reading, D-145's tier-3 denial applied, above zero at a pinned quantile over seeds and history resamples, on a pinned minimum of complete held-out starts), the finalist still ahead of each baseline at the point estimate at +1 tick of worse fills and with 10 % of signals missed, and the as-traded floors. **Pinned before the survey, in one row:** limits (both forms' parameters), budgets, dimensions and normalisers, weights, composite or fallback, the size that matters (**the operator's, Wave 4.2; O-3**) and the power target, regimes and "most years", finalist order and plateau rules, the gate's quantile and minimum complete starts, the no-harm margin(s), the L values. **Before any search pin, after the pinning row:** the deciding whole-rule calibration (same-design nulls: antithetic twin, disjoint seed sets; the history null; H3 re-specified, its earlier runs design checks only) and a power gate for the whole line (pairs from H4's baselines and synthetic plants; a design equal to the best baseline passing every limit at the target power; the complete-start count); no power, no pin; exit (B) states the power; **the operator's data question (E-007 (2): more history) is put to them with the power gate's result, before the first search pin.** The confirmation (NQ from 2026-07-17) is read against a criterion declared at registration and spends no k; each held-out test spends one k at 0.05/(k(k+1)) under E-204's rule (k counted from its held-out row; a repeat at the new level if another declaration pins between), the next k = 13. **Kept:** E-008 (2) with E-007 (3) (0 % denial, placement off, Focused Trader Program off in the verdict; E-007 (e)'s readings beside, its minimum detectable difference replaced by the power gate) and E-008 (3); E-202 (its (2)(a) news windows and (2)(d) limit-fill rule now also written into CHARTER section 4); E-203. **On record, no longer deciding (CHARTER 3.10):** the coin-twin lift and its value-map bar as a pass line; R\* = P-14 as the one row to beat; Stage 2 D-621 (3); E-015 (3); E-023 (1)-(2); Stage 2's `verdict` arm and D-145's edge-bound gate form. `CHARTER.md` sections 2-5 replaced from `docs/plans/AMENDMENTS_draft_2026-11-18.md` (section 4's paragraph unchanged, two marked paragraphs added; "a user who stops when their own money runs out" removed from "not modelled"), LF sha256 at this row `<fill>`; `CLAUDE.md`'s objective paragraph and DIRECTIVE's preamble, mapping table, Parts 3 and 5 and Part 6.2-6.3 follow. **To the operator (STATUS NEEDS_OPERATOR, none blocking Waves 2-3):** O-1, O-3 (Wave 4.2), O-4, O-5 and the data question. E-206's freeze stays until Wave 2's gate; Wave 2 changes the files the draft's section 5 lists. | The operator (E-207); the red team's two reads; E-007, E-008, E-015, E-023, E-202, E-203, E-204, E-206, E-208; Stage 2 D-14, D-145, D-150, D-554, D-626. |
```

---

## 5. Files that cite E-008's pass line as binding (Wave 2's list)

Found by `grep -rn -i -E "coin twin|coin-twin|trades first|trades' lift|E-008|pass line|0\.05 ?/ ?\(k|placebo"` and a
second pass for `lift|row to beat|R\* = P-14|judged block|value map|selection rule|CARRIED`, over `.claude/`,
`prereg/TEMPLATE_family.md`, `tests/`, `scripts/`, `extended/`, `config/` and `README.md` (`vendor/` excluded). Line
numbers are as of the working tree on 2026-11-18. "Stale before E-008" marks text that was already out of date under
E-008, because it still treats D-621 (3) as deciding.

**Agents (`.claude/agents/`)**
- `prereg-gatekeeper.md`:
  - `:36-44`: judged on trades first, the coin-twin lift, the value-map bar, R\* = P-14.
  - `:74-78`: k per family, with E-204's rule.
  - `:81-86`: metrics on the S-keyed scorecard and the lift.
  - `:88-95`: "The selection rule, unweakened -- E-008's" (holds a seed literal).
  - `:104`: coin twin seeds.
  - `:128`: power on the judged block.
  - `:159-163`: a carried candidate's registration.
  - `:186`: "limits as menu flags -- never as a pass line".
  - **New checks:** the held-out read ledger; the single pinning row of 3.9; the power gate and calibration before
    the pin; the finalist order rule; the side rule; each firm's baselines.
- `auditor.md`:
  - `:66-75`: the selection rule as D-621 (3) (stale before E-008).
  - `:86-89`: frontier on P, S1, S3a, S5a, and money from the `verdict` arm.
  - **Must change** to: re-derive from `docs/MEASURES.md`; check the zero-edge convention, the embargo, the three-way
    test, the sequence and the floors as pinned.
- `red-team.md`:
  - `:26-29`: the family level "applied to the test that decides".
  - `:30-31`: the coin-twin test of direction, and "Five minutes from alert to order" (also stale against E-202).
  - **Add:** the cycle-1 attack surfaces (held-out reuse, unpinned inputs, horizon straddling, degenerate nulls,
    baseline convention, resting-order edge, selection on fill optimism).
- `data-integrity.md:36-44`: power of "a family k ... on the judged block". Re-aim it at the power gate of 3.7.
- `results-tracer.md:51-56`: accompaniments per the old sections 2-3; money from the `verdict` arm. Point it to the new
  section 3.8's verdict and beside list.
- `scout.md`: no pass-line text. Add the challenger brief (plan section 5).

**Skills (`.claude/skills/`)**
- `prereg-discipline/SKILL.md`:
  - `:22-28`: k per family, "one cell per family reaches judgement".
  - `:56`: coin twin seeds.
  - `:59-72`: "The selection rule (the operator, E-008, E-014, E-015) ... judged on its trades first" (seed literal).
  - `:74-75`: "Weakening the rule".
  - `:139`: "A design is carried".
- `feature-rules/SKILL.md`:
  - `:3`: "the coin twin as the test".
  - `:53`: mirror bias. Keep it, as a fill-realism rule.
  - `:67`: the choice and judged blocks become the search and held-out years.
  - `:76-80`: "The test of direction".
- `contract-engine/SKILL.md:126-131`: D-621 (3) against R\* = P-14 (stale before E-008).
- `merge-checklist/SKILL.md`: no E-008 citation. Add:
  - measures traced to `docs/MEASURES.md`;
  - seeds paired;
  - no search code reads a held-out session (the runner's refusal);
  - the horizon embargo asserted;
  - nothing written to the variants ledger from a held-out read.

**Commands (`.claude/commands/`)**
- `prereg.md:12-18`: D-621 (3) against R\* = P-14 (stale before E-008).
- `audit.md:21-22`: the same.
- `close-check.md:32-36`: the exit criterion with "the sizing at the edge's lower bound". It follows the new section 5,
  including (B)'s power.
- `status.md:20,24`: add the search rounds, the baselines and the held-out ledger. A new `/brief` is needed.

**Template**
- `prereg/TEMPLATE_family.md`:
  - `:92-95`: level per family.
  - `:97-110`: C1 "judged on trades first (E-008)", C1', C2, the value map.
  - `:120`: the runner asserts `lift_bound.family_level(k)`.
  - `:128-137`: MDL of a lift.
  - `:147-153`: stages A-C.
  - `:156-163`: "R\* = P-14", "Beside, never the pass line".
  - `:165-180`: judged-block reads.
- It is replaced by `prereg/TEMPLATE_design_search.md` (Wave 2.1), whose fields now include: the held-out read ledger;
  the 3.9 pinning row's inputs; the zero-edge convention per entry type; the side rule and no-harm margin; each
  baseline's convention and runner identity; the horizon embargo; the finalist order rule; the calibration's nulls;
  the power gate; the stress floors; the martingale-outcome redraw (including its form for time-limited trades); the
  history null; the as-traded no-harm margin; the confirmation's criterion, declared at registration.

**Tests and code**
- `tests/test_family_stats.py:862-870`: `REQUIRED` binds the old template's strings ("0.05 / (k (k + 1))",
  "R* = P-14", "never deciding", "the judged block"). Keep it, scoped to the old file, and give the new template its
  own test.
- `extended/family_stats.py`: `power_gate` and the side-conditional B2 nulls retire with the trade-lift line (E-208).
  Their tests follow.
- Docstrings that name "the pass line":
  - tests: `tests/test_lift_bound.py:1`, `tests/test_p_bound.py:1`, `tests/test_q82_validation.py:1`;
  - extended: `extended/lift_bound.py:1-7,46,54,256`, `extended/p_bound.py:2,20,47`, `extended/lift_one_sample.py:1`,
    `extended/lift_one_sample2.py:1`, `extended/opening_journey.py:4`;
  - scripts: `scripts/q16_calibrate.py`, `scripts/q82_validation.py:1,14`, `scripts/q108_calibrate.py:1`,
    `scripts/q126_calibrate.py:1`.

  These are labels only, and they follow E-208's triage (Q-126 parked, Q-108 closed).
- `extended/journey_page.py:1024-1026,1090-1091` prints "A design passes only on its own trades ... (CHARTER section
  3, E-008)". The generated `docs/report/journey_scorecard/README.md:3,38` carries the same text; that page is a result
  and is not edited. The next page build needs the new wording.
- **Still valid, no change:** citations of E-008 (2) (`scripts/user_beside.py:4,75,222`, `extended/user_spend.py:155`,
  `extended/journey_page.py:32,799,1063,1424`, `scripts/rd01_reading.py:102`) and of E-008 (3)
  (`config/rules_extended.yaml:225`); E-023 (1)'s labels on readings already made (`scripts/rd01_reading.py:3,101`,
  `scripts/pp_reading.py:326`, `scripts/cl_reading.py:356`); and `tests/test_hooks.py:224`, which cites E-008 for a
  hook fix.
- **New runner guards (Wave 3):**
  - the re-baseline and survey runners refuse held-out sessions;
  - the measure code applies the horizon embargo;
  - the variants-ledger writer refuses held-out rows.

**Other documents:** the old drafts follow E-208's dispositions. Pinned declarations are never edited. `README.md:7`
("the row to beat") is a one-word fix. `docs/BOOTSTRAP_NEW_REPO_ORCHESTRATOR.md` is never edited.

---

## 6. Flags

**Resolved:**
- Cycle 1 resolved the first draft's F-1 to F-11 and F-13 to F-18 (section 0's first table).
- Cycle 2 resolved the coordinator's R-1 (V-1: the history null and the scope of the level), R-2 (V-3: the as-traded
  floors) and R-4 (the complete-start count as a power-gate condition).
- R-3 is kept as written: the stress applies to both design and baselines.
- R-5 is accepted, with m-9's sentence.

**Remaining points for the lead or the red team** (a scoped re-read of 3.2, 3.5, 3.7, 3.8, 5, the CLAUDE.md block and
the row, under E-207 (2)):
- **R-6. CHARTER section 1** still frames the gain as an edge. Out of this brief.
- **R-7. CHARTER section 6**'s "the reverse beside" is answered by 3.6 (g); section 6's own text is out of this brief.
- **R-8. CLAUDE.md, other lines** (the lane names; "Declare the family before building it") are stale and left for a
  later row.
- **R-9. The confirmation's minimum criterion** (5 (A)) is my wording of the ruling: on the martingale-outcome reading,
  ahead of each baseline at the point estimate and inside every limit in the form in force. The registration may add
  to it but not weaken it.
- **R-10. The redraw for time-limited trades** (the flatten, a max hold) is left to the search template, with zero
  gross expectation required. Its exact form is a red-team point at the template's read (Wave 2.1).
- **R-11. The history null's exactness** for quantile-type dimensions is settled in H3's declaration, as the red team
  noted.
- **R-12. The open-position rule** (3.5: a new trade takes an open position's side, or is skipped) can reduce supply
  across firms. Its cost is reported with measure (37); it is a conduct rule, not a lever.

**The operator's (the lead puts these in STATUS as NEEDS_OPERATOR; none blocks Waves 2-3):**
- **O-1. Which firm spends NQ's held-out years.** Single use per market (3.6 (c)) means the first held-out test on NQ
  2024-2026 consumes those years for every firm traded on NQ bars. The alternatives are which firm goes first, or one
  search covering several firms (cross-firm rotation, plan item 4). Later searches then need data not yet read (a
  purchase or the operator's setup). Pending; asked with the data question, before the first pin.
- **O-2. A pass on the first search carries a nominal level** (the Topstep NQ ledger is not empty), and only coin luck
  is bounded at it (3.8 (b)). The operator hears both when the confirmation's purchase is put to them. This is
  information, not a choice.
- **O-3. "The size that matters"**: the power gate's planted improvement, a judgement of value to a user. It is the
  operator's, set in Wave 4.2.
- **O-4. The traded side rule.** The candidate default is one literal coin draw per moment, shared across every
  account and firm. The alternative is a model's side behind its no-harm floor. Until the operator rules, no playbook
  goes to a user. The zero-edge evaluation convention is not part of this choice.
- **O-5. The burden of the limit check.** In force are the operator's confirmed words (E-207): inside every limit with
  margin wider than its noise. Pending is the red team's B-10 form: a design fails a limit only if shown to cross it,
  which is closer to E-015's condition that limits must not fail profitable models. Both are computed; the in-force
  form decides until the operator rules.
- **The data question (E-007 (2)):** more history (QuantConnect setup, or older bars bought), put to the operator with
  the power gate's result, before the first search pin.
