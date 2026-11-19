# Restart plan: the journey objective (draft for the operator's approval, then the lead)

Drafted 2026-11-18 by session stage-2-extended-11 from the operator's conversation of that day. **Status: a proposal.
Nothing in it is in force until the lead records it under decision rows (E-xxx) and the operator approves the items
marked OPERATOR.** It contains no result figures; every number in it is a parameter or a rule.

---

## 1. The objective

**Find the way of running prop-firm accounts that gives a real user the best journey to making money**: the least
bankroll needed, the fastest and cheapest path to a pass and a payout, a steady income after that, and the lowest
chance of going broke first. Topstep $50K first, then other firms, each on its own verified rules.

**Where the money comes from.** The firm's asymmetry: a funded account's loss costs the user only fees; its win is
paid. Not from predicting market direction. Stage 2's breakout and mean-reversion designs made money this way with no
trade edge (the handoff, section 0), and that is accepted: the goal is to make money, however it is done.

**What a design is judged on.** The user's journey (section 3's measures), never the trades' edge.

## 2. Definitions

| term | meaning |
|---|---|
| design (execution model) | one complete way of running accounts, in three layers: (1) **triggers** -- the reason and moment to trade, and the entry direction; (2) **trade shape** -- stop, target, max hold, contracts, dollar risk; (3) **account policy** -- which account takes it, evaluation vs funded behaviour (RD-05's modes), daily stops, evaluation purchases, the component schedule |
| component | one session-specific trigger with its own trade shape (e.g. an NY AM component, an NY PM component); a design is a schedule of components |
| lever | a setting the user controls: bracket (stop, target, max hold), contracts, reward-to-risk, dollar risk per trade, accounts held, rotation rule, evaluation-purchase rule, model mix, and any state rule (sizing by distance to drawdown or target) |
| signal source | what decides *when* a trade is taken: a model (breakout, mean reversion, ...) or the naive coin |
| zero-edge assumption | every trade's direction is treated as a fair coin; a design must work under it |
| start day | one development session taken as a fresh user (fresh bankroll, fresh accounts) |
| coin seed | one sequence of coin flips; re-running with many seeds gives the spread a user can live |
| search years / held-out years | the years the lever search may read / the years only the finalists' confirmation reads |
| limits | the ceilings and floors on what a user feels (bankroll, time to first payout, ...); the lead's, set in Wave 4.2 from H4's search-year results (E-221) |
| baselines | naive coin harvesting, and Stage 2's P-14, P-15, P-16 |
| P | **not a p-value**: the mean share of start days ahead in cash at months 1, 2 and 3 |
| frontier | the designs not beaten on one measure without losing on another |
| composite score | one number over the measures' dimensions, its weights the lead's, set in Wave 4.2 from H4's search-year results (E-221), pinned before the held-out years are read; the confirmation's single hypothesis |

## 3. The measures (39)

Every measure is a distribution over start days (median, p10, p90) unless stated, and over coin seeds where the
trades are coin-driven. "Exists" = defined in Stage 2 / the charter's journey scorecard (E-014, E-015) or in
`extended/user_measures.py`; "new" = to be built.

**Getting funded.** (1) sessions to first evaluation pass; (2) cash to first pass; (3) evaluations bought before the
first pass; (4) share of starts passed by session 21 (new).
**First payout.** (5) sessions to first payout (S3b); (6) cash spent before first payout = bankroll needed (S1);
(7) first payout's size (S3d); (8) share of starts paid by session 21 (S3a).
**ROI.** (9) sessions to break-even; (10) share falling back below break-even; (11) deepest fall after break-even;
(12) net cash at months 1, 2, 3, 6, 12; (13) P, and shares ahead at months 6 and 12 (S4a, S4b); (14) payouts per fee
dollar (S3c); (15) return on money at risk = 12-month net / peak out-of-pocket (new).
**Steady income and payout variance.** (16) monthly net in months 4-12 (new); (17) payouts per month; (18) share of
months with a positive net change; (19) spread of monthly net; (20) longest run of months without a payout;
(21) longest gap between payouts within 126 sessions (S5b); (22) best quarter's share of month-6 net (S5c);
(23) largest month's share of the year's payouts.
**Bankroll and downside.** (24) chance of running out before the first payout at the bankroll budgets the lead sets in
Wave 4.2 (E-221; new: the bankroll stop); (25) peak out-of-pocket in 12 months (new); (26) month-3 net of the
unlucky tenth (S5a); (27) CVaR10.
**Realism and robustness.** (28) headline measures with 10 % and 20 % of signals missed or late (new); (29) headline
measures at +1 and +2 ticks of worse fills (approved item 2); (30) workload: orders a day, accounts at once, screen
hours (new); (31) funded-account lifetime: payouts per funded account before it is lost (new); (32) worst year and
highest-volatility period (new); (33) break-even denial rate: the denial rate at which the design stops making money
(new; reported, never a limit); (34) luck against design (S6).
**Baselines.** (35) naive coin harvesting; (36) P-14, P-15, P-16.
**Supply and speed (the operator: speed is a positive outcome).** (37) trades available per day, per account and in
total (new); (38) session coverage: the share of sessions (Asia, London, NY AM, NY PM) with at least one trade, by
session (new); (39) longest idle stretch inside the firm's trading day (new).

Dropped by the operator: firm-rule exposure (flagged-pattern rate); rule-change sensitivity.

## 4. How the objective is achieved (the method)

1. **Model each firm exactly.** Verified rules only (`config/rules_extended.yaml` through `extended/firm_terms.py`;
   `/verify-rule`); each firm's own execution protocol, never Topstep's reused (the operator, 2026-11-18).
2. **Assume zero edge.** Every design is run with coin-driven directions over many coin seeds. Signal sources still
   matter -- they set *when* trades happen (timing, resolution speed, clustering) -- and are compared to the naive coin.
3. **Map the lever space, then search it with a model (the machine-learning part).**
   a. Declare the lever space: every lever, its range from the firm's verified rules, in volatility units where
      sensible (a stop as a multiple of recent range, with dollar caps) so a setting means the same thing across
      2020-2026's volatility drift (RD-04).
   b. Survey: a space-filling sample of a few hundred designs on the search years.
   c. Fit a surrogate model predicting each measure from the levers: which levers move which measures, where
      trade-offs are unavoidable, where the ruin chance jumps.
   d. Propose the next round inside the limits (constrained Bayesian optimisation, multi-objective); run; refit;
      repeat for a declared number of rounds.
   e. Prefer plateaus to peaks: a finalist's neighbours must also do well.
   f. Every design tried is logged in the variants ledger (`results/variants.jsonl`) with its manifest; the map and
      ledger persist, so the next firm, lever or model starts from them.
4. **Mix signal sources as a lever.** Two or three models (and the coin) whose trades differ in timing and shape,
   rotated across accounts, can keep each account's variance (which the asymmetry rewards) while lowering the
   correlation between accounts (which steadies the total). Which models, their shares and their account assignment
   are levers in the same search. A model is judged on what it adds to the mix, not on its backtest alone.
   **Hard rule:** never opposing positions at once across accounts or firms (conduct tier 1); one position at a time
   across a firm (Stage 2 D-429) stays.
4b. **Design rules from the operator (every design obeys them).**
   - **Many trades, fast.** Supply and speed are objectives: more opportunities mean faster passes and payouts. The
     search rewards supply (37) and speed (1, 5, 9) inside the limits; the ruin chance (24) is its counterweight.
   - **Multiple sessions.** A design is a schedule of components across every session the firm allows (Asia,
     London, NY AM, NY PM), each with its own trigger and its own trade shape, since
     each session's volatility differs. Components are judged by what they add to the whole design.
   - **Triggers judged on properties, not accuracy:** supply, timing, resolution speed for a given shape, clustering,
     how differently timed they are from other components, and hand-executability.
   - **Hand-executable.** At least five minutes from alert to order, so a trigger must be known five minutes ahead
     (scheduled times, or resting orders at levels known in advance); one position at a time across a firm, so
     components' windows are scheduled not to collide; flat by the firm's daily close (Topstep: 15:10 CT); no entry
     before 07:35:00 CT on BLS release days; never opposing positions across accounts or firms.
   - **Any hour.** No cap on trading hours (the operator, 2026-11-18): every session the firm allows (Asia, London,
     NY AM, NY PM) is in the search, and any valid component found in any of them can be approved. Workload (30) is
     reported, never a limit on hours.
   - **The output is a playbook.** Each finalist is written as a one-page set of rules (triggers, shapes, account
     policy, schedule) plus the exact alert format, so it can be traded by hand.
5. **Separate design from luck (the three-way test).** A difference between designs counts only if it holds
   (i) across coin seeds, with both designs given the same seeds on the same days (paired); (ii) across time -- most
   years and both volatility regimes, with block resampling of history; and (iii) on the held-out years, which the
   search never read. The coin-seed spread itself is reported: it is the user's payout variance.
6. **Confirm and spend the budget.** A declared search's finalists are confirmed on the held-out years by a paired
   test calibrated on nulls (two identical designs must "differ" no more often than the level) and shown to have power
   (a planted improvement of the size that matters must be found). Each confirmation spends one k at
   0.05 / (k (k + 1)), the next k = 13. A design that passes is carried; the confirmation window (NQ from
   2026-07-17) is a purchase and the operator's decision.
7. **Pass line.** A design passes when (a) it sits inside every limit at its point estimate, which governs, the
   one-sided check beside it (E-221, the lead's O-5 ruling),
   (b) it beats the best baseline on the declared composite score (section 4.8) by the calibrated test at its level, and (c) the
   floors hold: verified rules, conduct tier 1, the long-run gate, hand entry with at least five minutes alert to
   order. The verdict is read at 0 % payout denial with the denial ladder and break-even denial rate reported beside.

8. **The objective is a combination, fixed before the final test.**
   - **Search: every measure at once.** The search is multi-objective: the surrogate models all 39 measures and
     reports the frontier (designs not beaten on one measure without losing on another).
   - **Measure structure (Wave 4).** On the re-baseline and survey results (search years only), find which measures
     carry independent information and which move together -- expected to reduce the 39 to about five or six
     dimensions (speed, cost and bankroll, steadiness, downside, supply, workload) -- and the trade-off curves between
     them (what each step of one costs in another).
   - **The lead's weights (E-221, by the operator's delegation).** From those curves, by a rule declared before H4 is
     read, the lead sets the weights of a **composite score** over the
     dimensions, one of which is P under the bankroll stop (the share of users with the pinned budget who are
     ahead in cash at months 1-3, `p_by_month` with `spent` and `limit`). The weights are recorded and pinned in the
     search declaration, before any held-out year is read, and never changed after a result is seen.
   - **Limits stay hard lines** (bankroll, chance of running out, trades per day, ...): no score buys crossing one.
   - **Confirmation tests the composite once** (one hypothesis, one k); the frontier and every measure are reported
     beside it. Fallback if the weights cannot be set: P under the bankroll stop alone, with the rest as limits.

## 5. What changes, where, and why

| where | change | why |
|---|---|---|
| `DECISIONS.md` | new E-rows: amend E-008 (pass line = journey under limits, zero edge, three-way test); record the operator's measures, baselines, dropped items; hold/withdraw the trade-edge work (section 7) | E-008 made the trades' lift the pass line, which fails the very designs the operator wants |
| `CHARTER.md` sections 2-5 | rewrite: the objective (section 1 here), the measures (section 3), the method and pass line (section 4); remove "a user who stops when their own money runs out" from "not modelled" | the charter is the objective's source of truth |
| `CLAUDE.md` "The objective" | replace the trades-first paragraph with a short statement of section 1 and section 4.7 | every session reads it first |
| `DIRECTIVE.md` | update the trades-first references (5) and the mapping table | standing orders must match the charter |
| `docs/MEASURES.md` (new) | the 36 definitions, exact formulas, which `extended/` function computes each | one place for definitions; the auditor re-derives from it |
| `prereg/TEMPLATE_family.md` | a "design search" template: lever space, survey size, surrogate method, rounds, seeds (fixed beforehand), search vs held-out years, primary measure, limits, the three-way test, power target | the current template asks for a trade-lift family |
| `prereg/DRAFT_F-B_multifeature.md`, F-04's draft, `DRAFT_F-R_resolution.md`, `DRAFT_F-02_*` | triage: retire to `PARKING_LOT.md` or recast as a signal source for the mix | written for the trade-edge pass line |
| `.claude/agents/prereg-gatekeeper.md` | check the new template's fields; k counted per confirmation | it checks for the coin-twin lift today (3 references) |
| `.claude/agents/red-team.md` | add attack surfaces: search leakage into held-out years, peak-picking, seed reuse, unpaired comparisons, limits set after seeing results; findings labelled blocking / minor | aims at the new failure modes |
| `.claude/agents/auditor.md` | re-derive the journey measures from `docs/MEASURES.md`, check the three-way test was run as declared | audits what now decides |
| `.claude/agents/scout.md` | the standing challenger brief before any confirmation (approved item 5, re-aimed at journey measures) | "tell me I'm wrong" before k is spent |
| `.claude/skills/prereg-discipline`, `feature-rules` | trades-first text (3 + 3 references) rewritten; feature rules kept for any signal source that reads bars | skills steer every worker |
| `.claude/skills/merge-checklist` | add: measures traced to `docs/MEASURES.md`; seeds paired; held-out years unread by any search code | merge gate for the new work |
| `.claude/commands/` | `/status` shows the lever map's rounds and the baselines; a new `/brief` for the operator (plain-English: winners inside limits, the trade-offs, the next round) built on traced results only | the operator's on-demand briefing, done natively |
| `extended/user_measures.py`, `user_beside.py`, `user_spend.py` | the new measures (4, 15, 16, 24, 25, 28, 30, 31, 32, 33); the bankroll stop | the scorecard must compute what decides |
| new `extended/` modules | naive coin source; signal-mix router with the no-opposing-positions guard; seed-paired runner; the three-way test with its null calibration and power check; the lever-space sampler and surrogate | the method's parts |
| `scripts/run_clean.py` | per-arm child processes (approved item 2); seeds fixed from the declaration | memory on a 16 GB machine; reproducibility |
| `scripts/hooks/run_tests.py` | master edits run only the edited file's tests plus vendor integrity and declarations fixed (approved item 1) | edit speed; the pre-commit fast tier stays |
| `TASK_QUEUE.md`, `STATUS.md` | rebuilt around the phases in section 8; finished rows archived once `scripts/status.py` copes | the queue drives the work |

## 6. Workflows: who does what, in parallel

**The lead** (`master`, one session per cycle -- commit, close the window, open a fresh one, `/status`): decisions,
queue, status, merges, dispatch. Writes no model code. Only it writes `DECISIONS.md`, `TASK_QUEUE.md`, `STATUS.md`,
`PROGRESS.md`, `CLAUDE.md`, `CHARTER.md`.

**Lanes (light work runs in parallel; each lane is a standing worktree, `worker-builder` unless stated):**

| lane (worktree) | owns | agents and tools |
|---|---|---|
| journey measures (`wt-user`) | `docs/MEASURES.md`, the 39 measures, bankroll stop, missed signals, workload, supply and coverage | worker-builder; auditor on its first result |
| statistics (`wt-verify`) | the three-way test, null calibration, power checks, paired-seed runner, identities, the test hook, per-arm isolation, worse-fill stress | worker-builder; red-team on the calibration |
| lever map and search, the ML (`wt-features`) | lever-space sampler, surrogate model, round proposals, plateau check | worker-builder; red-team on the search declaration |
| signal sources and mix (`wt-levels`) | the trigger library by session (Asia, London, NY AM, NY PM), naive coin, breakout and mean-reversion sources, the component scheduler, the mix router and its guard; data-integrity agent checks the overnight bars before any overnight trigger is used | worker-builder; `feature-rules` for any bar-reading source |
| firms (`wt-firms`) | each firm's verified rules and execution protocol; RD-01/03/05 readings; cross-firm rotation (item 4) once rules are verified | rules-verifier (`/verify-rule`), worker-builder |
| payout policy (`wt-payout`) | RD-02 and the request rule as levers | worker-builder |
| challenger and research (`wt-scout`) | the pre-confirmation challenger brief; the review checklist from past reviews; literature | scout (read-only) |
| reports (`wt-report`) | the operator's `/brief`, the journey page, the menu under limits, each finalist's playbook and alert format | worker-builder; results-tracer (`/trace`) |
| infrastructure (`wt-infra`) | run tooling; a KOA runner only if the operator approves it | worker-builder |

**Heavy work** (full bars, the engine beyond a few paths, a survey or search round, a confirmation): one at a time
under `run.lock`, from a clean checkout (`scripts/run_clean.py`), watched to exit, collected with `/collect`
(manifests verified, variants ledger, trace check, `auditor`). Memory is freed before heavy runs.

**Automations.** Pre-commit: vendor integrity and the fast tier. Post-commit: push to the private remote. Post-edit:
the scoped test hook. A declared search runs its rounds without a review per round: the declaration (lever space,
budget, method, seeds, years) is red-teamed and pinned once; rounds run as clean runs and are collected; the red team
and auditor read the finalists and the confirmation.

**Review.** Findings labelled blocking (could make a result wrong: leakage, peeking, miscounting, unpaired luck) or
minor. Only blocking findings trigger a full re-read; minors are fixed and the diff is checked. Workers run the
review checklist before hand-back. (Proposed; OPERATOR approval pending.)

## 7. Current work: disposition

| item | disposition |
|---|---|
| F-04 (pin-ready, k = 13) | hold; then retire or recast as a signal source -- do not spend k under the old pass line |
| Family B (Q-14), approved item 3 | retire as a trade-picking classifier; the ML becomes the lever-map surrogate (section 4.3) |
| DRAFT_F-RL3, DRAFT_F-R, DRAFT_F-02 | lead triage: park, or recast as signal sources or levers |
| Q-126, Q-108 calibration | check what serves the three-way test's null calibration; keep what does |
| Q-15 + item 2 | keep: worse-fill stress (measure 29) |
| RD-03, RD-04, RD-05, RD-02 | continue: they are the lever and firm maps |
| item 4 (cross-firm rotation) | unpark into the lever space once each firm's rules are verified |
| items 1, 5 | keep (5 re-aimed at journey measures) |
| QuantConnect / older data | downgraded: the journey depends on today's prices and dollar rules |

## 8. The to-do list for the lead: waves, lanes and gates

Light work in a wave runs in parallel (as many lanes as memory allows; roughly three or four at once on this machine
with other applications closed). Heavy work joins the single heavy queue (H1, H2, ...) and runs one at a time under
`run.lock`. A wave's gate must hold before the next wave's dependent items start; independent lanes run on.

### Part A -- structural changes (Waves 0-2)

**Wave 0 -- freeze (lead only).**
- 0.1 Finish and commit the current cycle.
- 0.2 E-row: hold F-04's pin, Family B (Q-14) and approved item 3; no k is spent until the new pass line is recorded.
- 0.3 Commit this plan as `docs/plans/RESTART_PLAN_journey_objective.md` and cite it in the E-row.
- Gate: master clean, the hold recorded.

**Wave 1 -- the constitution (parallel).**
- 1.1 Lead: draft the amendments -- `CHARTER.md` sections 2-5, `CLAUDE.md`'s objective, `DIRECTIVE.md` (sections 1, 2,
  4 and 4b here).
- 1.2 `wt-user` (worker-builder): `docs/MEASURES.md` -- the 39 definitions, formulas, the function computing each
  (existing in `extended/user_measures.py`, `user_beside.py`, `user_spend.py`, or "to build").
- 1.3 `wt-scout` (scout): triage memo -- F-04, `DRAFT_F-B`, `DRAFT_F-RL3`, `DRAFT_F-R`, `DRAFT_F-02`, Q-126, Q-108:
  park, recast as a trigger or lever, or keep (and which calibration parts serve the three-way test).
- 1.4 `wt-scout` (scout, after 1.3): the review checklist from the past review notes (if the operator approves the
  review changes).
- 1.5 red-team (cold): the amended charter text and `docs/MEASURES.md`.
- 1.6 Lead: E-rows recording the amended objective, pass line, measures, design rules and dispositions; `/park` the
  parked items.
- Gate: E-rows recorded; red-team's blocking findings answered.

**Wave 2 -- the agents, skills, templates, commands and automations (parallel).**
- 2.1 `wt-infra` (worker-builder): `prereg/TEMPLATE_design_search.md` (lever space, survey size, surrogate method,
  rounds, seeds, search vs held-out years, primary measure, limits, the three-way test, the power target, the
  component schedule across sessions).
- 2.2 `wt-infra`: `.claude/agents/` prereg-gatekeeper, red-team (new attack surfaces; blocking/minor labels), auditor
  (re-derive from `docs/MEASURES.md`), scout (challenger brief); `.claude/skills/` prereg-discipline, feature-rules,
  merge-checklist; `.claude/commands/` `/status` (search rounds, baselines) and a new `/brief`.
- 2.3 `wt-verify`: the scoped post-edit test hook (approved item 1).
- 2.4 `wt-verify`: per-arm child processes in `scripts/run_clean.py`; seeds read from the declaration (approved
  item 2, part one).
- 2.5 red-team on 2.1 and 2.2; lead merges by `merge-checklist`.
- H1 (heavy): every identity re-held at the merged master.
- Gate: template pinned-ready; agents and skills merged; identities hold.

### Part B -- the work (Waves 3-6)

**Wave 3 -- the parts (parallel lanes, synthetic-data tests).**
- 3.1 `wt-user`: the new measures (4, 15, 16, 24, 25, 28, 30-33, 37-39) and the bankroll stop.
- 3.2 `wt-verify`: the three-way test -- paired-seed runner, block resampling, per-regime split -- with its null
  calibration design and power check; worse-fill stress (measure 29).
- 3.3 `wt-levels`: the trigger library by session (Asia, London, NY AM, NY PM; overnight triggers used only after
  H2 passes), the naive coin source, the component scheduler, the mix router with the no-opposing-positions
  guard; `feature-rules` for every bar-reading trigger.
- 3.4 `wt-features`: the lever-space sampler, the surrogate model, the round proposer, the plateau check.
- 3.5 `wt-report`: the playbook format, the alert format and `/brief`.
- 3.6 `wt-firms` (continuing): RD-03, RD-05 readings; `/verify-rule` for the next firms.
- H2 (heavy): data-integrity on the overnight bars (17:00 CT to 08:30 CT): gaps, session boundaries, daylight-saving
  transitions, thin-liquidity bars -- required before any overnight trigger enters a search.
- H3 (heavy): the three-way test's null calibration and power runs.
- Gate: each part merged by `merge-checklist`, red-team on 3.2 and 3.4; identities re-held.

**Wave 4 -- re-baseline.**
- H4 (heavy): naive coin harvesting and P-14, P-15, P-16 under the full new scorecard, every measure, many seeds.
- `/collect`, auditor, trace.
- 4.1 `wt-user` with `wt-verify`: the measure-structure analysis on H4's results (search years only) -- the
  dimensions, the redundant measures, the trade-off curves.
- 4.2 Lead: sets the limits, the bankroll budgets, the composite's weights and the size that matters from H4's
  search-year results, by a rule declared before H4 is read, pinned in one row before the survey, never after a
  held-out read -- **the lead's, by the operator's delegation (E-221)**; recorded under an E-row.

**Wave 5 -- the first design search (Topstep $50K).**
- 5.1 `wt-features` drafts the declaration on the new template (the lever space from RD-03/RD-05 and the firm record;
  the component schedule across every session the firm allows; limits; the composite's weights from 4.2; seeds; years).
- 5.2 scout: challenger brief on the draft. 5.3 red-team (cold). 5.4 prereg-gatekeeper: k assigned only at the
  confirmation row (E-204); pin; lead `/decide`.
- H5 (heavy): the survey round. H6... (heavy): the surrogate rounds, as declared; each `/collect`ed.
- 5.5 auditor and red-team on the finalists; `wt-report` writes their playbooks.

**Wave 6 -- confirm.**
- 6.1 scout: challenger brief on the finalists.
- H7 (heavy): the calibrated paired test on the held-out years (k = 13); auditor; trace.
- 6.2 Lead: the verdict row; the operator hears the result and the confirmation-window purchase decision.

**Alongside Waves 3-6:** `wt-firms` verifies other firms' rules and execution protocols, then each firm's own search
starts from the Topstep map; cross-firm rotation (item 4) enters the lever space once those rules are verified;
`wt-payout` keeps RD-02's request rule as a lever.

## 9. Decisions for the operator

1. Approve this plan (or amend it) before the lead starts Phase 1.
2. **Decided (the operator delegated it, 2026-11-18):** the objective is a composite score over the measures'
   dimensions with weights fixed before the held-out years are read (section 4.8); fallback P under
   the bankroll stop.
3. **Delegated to the lead (E-221):** the limits, the bankroll budgets for (24) and the weights -- in Wave 4.2, from
   H4's search-year results by a rule declared before H4 is read.
4. The review changes (blocking/minor rule; the checklist).
5. KOA, if wanted: its licence, usage policy and cost checks first.
6. **Decided (the operator, 2026-11-18):** no cap on trading hours; every session the firm allows is in the search.

## 10. What does not change

`vendor/` read-only; the identities first; declarations pinned by sha256; results only with manifests from clean runs;
no typed figures; the failure protocol; development NQ 2020-01-02 to 2026-07-16 and the confirmation window unread
until a carried design; verified firm rules only; conduct tier 1; hand entry only, no automated order entry; nothing
bought without the operator's yes; the single-writer lead; one heavy run at a time.
