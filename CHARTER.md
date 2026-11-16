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

## 2. The objective: the user's journey as one outcome

**The unit** is one user: one development trading day taken as a fresh start (fresh bankroll, fresh accounts), the
design's trades replayed in historical order. A month is 21 sessions. **The outcome** of a start is its **net cash** --
payouts received less every fee paid -- at months 1, 2, 3, 6 and 12, and whether it is above zero ("ahead"). A design
is judged over all its start days, on the `verdict` arm (every R's outcome shifted to the one-sided 95 % lower bound of
its edge, as Stage 2's gate does). The definitions are Stage 2's (`vendor/stage2/docs/USER_MILESTONES.md`, Stage 2
D-620, D-621) and are used unchanged here.

| key | measure | direction | role |
|---|---|---|---|
| **P** | the mean of the shares of starts ahead at months 1, 2 and 3 | higher | **primary** |
| S1 | cash spent before the first payout, p90 (bankroll needed) | lower | guarded |
| S3a | share of starts paid by session 21 | higher | guarded |
| S3b | sessions to the first payout, p90 | lower | guarded |
| S3c | payouts received per fee dollar at month 3, pooled | higher | guarded; reported (the screening target under E-001; see below) |
| S4a, S4b | shares ahead at months 6 and 12 | higher | guarded |
| S5a | month-3 net of the unlucky tenth of starts (p10) | higher | guarded |
| S5b | longest gap between payouts within 126 sessions, p90 | lower | guarded |
| S5c | month-6 concentration (best quarter's net over all) | lower | guarded |
| S2, S3d, S6, Q | first pass; first payout's cash; luck against design; quit-rule values | -- | reported, never selected on |

**Why S3c screened (E-001), and its role from E-008.** Across Stage 2's designs, what a funded account pays back per
fee dollar is the measure that moves P; speed and bankroll barely do (`results/user_drivers.csv`, section
`between_designs`; the regression beside it). The audit (E-007) found that association partly arithmetic (S3c - 1 is
the mean month-3 net over mean fees) and carried by failed families across designs, while within one trade stream S3c
does track P (the red team). From E-008 a design is screened and judged by its trades' lift over the coin twin
(section 3); S3c and its components (a won funded opening; the five winning days after it) are reported with the user
scorecard, compared only within one trade stream.

**The journey scorecard (the operator, E-014, E-015).** The goal is an evenly distributed path for a user, not one
lump sum: the journey is read as a collective of variables -- sessions and cash to the first pass, sessions and cash
to the first payout, sessions to break-even (cumulative net cash at or above zero, daily) and the share that later fall
back below it, and the path's evenness (the share of months with a positive net change, the longest run of months
without a payout, the spread of monthly net, the deepest fall after break-even, payouts per month, the largest single
month's share of the year's payouts) -- beside P and S1-S5c. **Every measure is reported as a distribution over start
days** (median, p10, p90), with its uncertainty from the effective number of independent starts, and the share of a
user's result that is the start day's luck rather than the design. **Designs are compared by limits first, then the
best inside them** (E-015): limits on what a user feels, set from what P-14, P-15 and P-16 achieve, each with a margin
wider than its measurement noise, approved by the operator before use. **A limit never fails a design**: the pass line
is the trades' calibrated lift (section 3); a design that crosses a limit is shown on the menu with which limit and by
how much, and the trade-off curve (how much "ahead" each step of evenness costs) is reported beside. Not modelled, and
said so wherever a scorecard appears: a user who stops when their own money runs out, the user's time, taxes.

**The frontier, not one number.** A user's first quarter is mostly the day they start, not the design
(`results/user_drivers.csv`, section `design_vs_luck`): the honest promise is a distribution. Every campaign reading
reports the frontier of designs not beaten at once on P, S1, S3a and S5a (the form of `user_drivers.csv` section
`frontier`), and a menu read under limits on what a user feels -- bankroll and time to first payout -- fixed before
the read. A middle ground is searched by fixing those limits first and maximising P inside them.

## 3. The row to beat and the selection rule

**R\*** is the row to beat on P, fixed mechanically by Stage 2's U1 (`results/user_journey.csv`; Stage 2 D-626): **P-14**
(A3-BRK30-CB20: a 30-minute-bar breakout followed five bars late, 12.5/25-point NQ stops, five Topstep seats, the
no-closure state table, at most 20 evaluation purchases in 21 sessions). Each guarded measure's own row to beat is the
best of P-14, P-15 and P-16 in that file, reported beside.

**Amended by the operator (E-008, 2026-11-15): new designs are judged on their trades first.** The Phase 0 audit
(E-007) found that the judged block holds only a few dozen independent start days, so once its bound is calibrated a
rule on P can carry nothing but near-P-14 variants or very large contract-shape effects. So, from E-008:

- **The pass line is direction on the design's own trades:** the lift over the coin twin on the same brackets (the
  same entries with a fair coin's side, so supply, cost and schedule cancel), on the judged block, its one-sided lower
  bound above zero at the family's level 0.05 / (k (k + 1)) **by a statistic calibrated to deliver that level**
  (TASK_QUEUE Q-16), and its value -- the lift priced by Stage 2's value map where the family uses it -- at that
  bound at least the bar the family declares.
- **Floors that still bind:** the long-run gate (growth on the required bankroll at the bound above zero, Stage 2
  D-145), every offered R resolving, every firm rule verified, conduct tier 1.
- **The user scorecard is reported beside every judgement, never as the pass line:** P and the guarded measures
  against R\* = P-14, the frontier, and the readings E-007 (e) names (the denial ladder, the placement on, the
  Focused Trader models, P by month, mean net, CVaR10, P under a bankroll limit, the effective sample size and the
  minimum detectable difference). **Payout denial stays at 0 % with the placement off in the verdict** (the operator,
  E-008; Stage 2 D-234, D-289), the rest beside it.

The rule below, Stage 2 D-621 (3), is kept on record as E-001 adopted it; it no longer decides a design. Its line (i)
was found not to deliver its stated level (E-007).

**Levers that do not choose a side (the operator, E-023, 2026-11-16).** Two kinds of component cannot be judged by a
lift over the coin twin, so they have their own rules:

- **Levers that add no trades** -- payout policy (when and how much to withdraw), and any other choice that leaves the
  offered trades unchanged -- are **described, never carried**: each is read on the journey scorecard (who it helps and
  hurts each month, its uncertainty, the evenness trade-off) for the operator to choose from the menu. Such a reading
  takes **no program family number** and spends nothing of the multiplicity budget; it is declared and pinned like a
  family so nothing in it is chosen after a look.
- **Filters that keep the coin's side but choose which offers to take or when** -- a timing filter on the funded
  opening, a resolution forecast admitting marks -- are **tested at the trade level against a placebo-selection twin**:
  a random filter that fires on the same share of the same population, seeded, so supply and schedule cancel and only
  the selection is measured; one-sided at the family's level 0.05 / (k (k + 1)) by a calibrated statistic (TASK_QUEUE
  Q-16), its value at that bound at least the declared bar; the same floors as section 3; the user scorecard beside.
  Such a filter can be carried.

*As adopted by E-001:* a design is **CARRIED** only by Stage 2 D-621 (3)'s rule, used unchanged: on the judged block of start days
(starts from the first session of 2024, chosen on the starts of 2020-2023), (i) its paired difference in P from R\* is
above zero with the moving-block bootstrap interval (63-session blocks, seed 20261700, 2,000 draws) excluding zero at
its family's level; (ii) on no guarded measure is it worse than R\* by more than five percentage points on a share or
ten per cent on dollars, sessions and ratios; (iii) the gate stays a floor -- growth on the required bankroll at the
bound above zero and above P-06's row at a campaign seed never used before, every offered R resolving, every firm rule
verified; (iv) a coin design also beats R\* under at least 40 of 50 coin sequences; and (D-621 (4)(e)) it is not worse than
R\* on P in more than one of the seven start years. A carried design is a new candidate: its registered development test,
the independent audit, then one confirmation on data never read (a purchase: stated, waited for).

**The multiplicity budget continues Stage 2's program U** (E-001): families are numbered in declaration order across
both repositories; Stage 2 declared and closed nine (`results/u_*.csv`), so this repository's first family is k = 10,
judged one-sided at 0.05 / (k (k + 1)). A new repository does not refresh the budget: the data, the row to beat and the
researcher are the same.

## 4. The constraints a model lives inside

Stage 2's handoff section 2, unchanged: the firm rules in Stage 2's verified ledger (`vendor/stage2/config/rules.yaml`,
`RULES_LEDGER.md`; an unverified rule is never loaded); the stop band and cost floor (`results/stop_band.csv`); stage
one's zero-edge ceilings as oracles (an output outside them is an engine error); the execution rules -- at least five
minutes from alert to order (a resting order may go live five minutes after its ticket and then fill at its level),
one position at a time per firm with five minutes flat between trades, every trade resolving (at most 5 % reach the
15:10 CT flatten, Stage 2 D-212 as D-308 raised it from 2 %; no time stops), realised risk matching intended (at least
90 % of trades within 10 % of the state's risk in whole micros, Stage 2 D-212), no entry before 07:35:00 CT on a BLS
08:30 release day (strictly after it, E-007) and FOMC days out, each account carrying its own trades; and the three
conduct tiers (Stage 2 D-145: no hedging across accounts or firms, no simulator-fill exploitation, no maximum size into
major news, nothing that conceals a pattern). No automated or API order entry -- **the operator's rule** (Topstep's
pages permit automation through its paid API; the operator kept hand entry, E-008): every trade is placed by hand at
least five minutes after its alert. Designs are for one user's own accounts; a signal service whose users place the
same tickets is out (Topstep's coordinated-trading prohibition, E-007 (c)).

## 5. Exit criterion -- either is a valid close

- **(A)** a design CARRIED under section 3, its registered development test passed and audited, and its one
  confirmation on unread data read and reported, with the frontier, the sizing at the edge's lower bound and the rules
  ledger verified; or
- **(B)** a documented negative result: no declared family carries a design, with every family's evidence and count.

Either way: every declaration and outcome on record, the decision log complete, every number traced to a result file
with a manifest, Stage 2's vendored tree unedited and its identity holding.

## 6. Working discipline (summary; `CLAUDE.md` is the operating copy)

Pre-register the family, not the model; count every variant; identities first, refusing; the bound, not the point;
walk-forward (choose early, judge late; the reverse beside); exploratory labelled; the failure protocol (a failed check
stays on record, is diagnosed, is never rerun until it passes); provenance (no typed result numbers); clean runs from
a committed commit; no payment without the operator's explicit yes.
