# Charter: Stage 2 Extended -- execution models for a user's prop-firm journey

Written 2026-11-15 from Stage 2's handoff (`vendor/stage2/docs/HANDOFF_NEW_REPO_2026-11-15.md`, sections 0 and 1; the
handoff's section 7 step 1). Decision row E-001. This file states the question, the objective and the rules of
judgement. It holds no result value: every figure lives in a result file with a sidecar manifest, and Stage 2's are
vendored read-only under `vendor/stage2/results/`.

## 1. The question

Build an execution model for prop-firm accounts -- Topstep's $50K Trading Combine and Express Funded Account first --
that improves a **user's journey**: a person who starts on any day, buys evaluations, passes, trades funded accounts and
collects payouts. In every design that works so far the money comes from the firm's **contract shape** (a funded loss
costs the user only fees; a funded win is paid), not from a trading edge. The next gain needs either

- a **real edge spent where the contract pays most** (Stage 2's value map, `results/u_value_map.csv`: a won trade is
  worth most on the funded account's opening trade), or
- a **contract shape not yet tested** (another firm's drawdown and payout rules, verified on its own pages).

A signal's job is supply, resolution and cost; direction is a bonus spent where it is worth most. A negative result,
documented, is a valid close.

## 2. The objective: the user's journey to making money

**The objective (the operator, E-207; E-210).** Find the way of running prop-firm accounts that gives a real user the
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
| zero edge | the evaluation convention of section 3.2: the fill comes from the real order; the path after the fill is reflected about the fill price with probability one half (direction removed); and every deciding reading redraws each trade's outcome at its own bracket's driftless first-exit odds (the martingale-outcome reading), except the no-harm floors (3.5) and the as-traded floor (3.8 (c)), which are read on the real path with no redraw (3.8) |
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
  - It is applied identically to designs and baselines. Every deciding reading of section 3.8 is this one (3.8's one exception: the no-harm and as-traded floors, read on the real path).
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
  - **Same-design nulls:** a design against its **antithetic twin** (every coin draw replaced by its complement, u to
    1 - u, for the reflection and the redraw alike), and the same design on **two disjoint seed sets**. Each pair has
    distinct realisations and equal expected composites by construction. They check the coin-seed leg's size.
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

**The one exception:** the no-harm floors (3.5) and the as-traded floor (3.8 (c)) are read on the real path, with
no redraw, because they exist to measure what the redraw removes. A no-harm floor compares the side as traded (the
model's side, or the resting order's real side, unreflected) with the coin side on the as-walked, reflected path,
same fills, same seeds. The held-out as-traded floor compares the finalist's as-traded composite with each
baseline's as-walked composite. For a market-entry baseline, its as-traded and as-walked readings coincide.

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

**3.10 On record, no longer deciding.** These are kept as their rows adopted them and decide nothing from E-210 on:
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

**Amended (E-210), from the operator's rulings E-202 (2)(a) and (2)(d):** no entry and no fill inside any verified news
window, and a position open at a window's start is flattened under E-200 R-1 (RL3's 08:30-08:59 fill window stays
closed); limit (resting) entries go live at the latency, fill only on a trade-through by one tick, and are cancelled at
a news window's start.

**Amended (E-210), the oracles under the zero-edge convention (section 3.2):** stage one's zero-edge ceilings are read
on the martingale-outcome reading, where an output outside them is an engine error as before. An as-walked (reflected)
result outside them is the path-structure edge of section 3.2: it is reported beside the verdict, never booked as an
engine error, and never "fixed" as one.

## 5. Exit criterion -- either is a valid close

- **(A)** A design CARRIED under section 3.8, meaning: its held-out test passed (its level printed nominal if its
  ledger is not empty, the history-level false-pass rate beside) and audited, and its playbook written. Then its one
  confirmation on the confirmation window is read against **a criterion declared at its registration, before the
  read**, and reported (a purchase, the operator's). At the least, the criterion requires that on the
  martingale-outcome reading the design is ahead of each baseline on the composite at the point estimate and inside
  every limit in the form in force; and, both at the point estimate, that it meets the as-traded floor of section
  3.8 (c), read on the real path, and stays ahead of each baseline at +1 tick of worse fills. The frontier, every
  measure of section 2 and the rules ledger are verified with it. The confirmation is the only test on a fresh history;
  it spends no k.
- **(B)** A documented negative result: no declared search yields a design that passes, with every search's evidence,
  its count and the pass line's power from its power gate (section 3.7).

Either way: every declaration and outcome on record, the decision log complete, every number traced to a result file
with a manifest, Stage 2's vendored tree unedited and its identity holding.

## 6. Working discipline (summary; `CLAUDE.md` is the operating copy)

Pre-register the family, not the model; count every variant; identities first, refusing; the bound, not the point;
walk-forward (choose early, judge late; the reverse beside); exploratory labelled; the failure protocol (a failed check
stays on record, is diagnosed, is never rerun until it passes); provenance (no typed result numbers); clean runs from
a committed commit; no payment without the operator's explicit yes.
