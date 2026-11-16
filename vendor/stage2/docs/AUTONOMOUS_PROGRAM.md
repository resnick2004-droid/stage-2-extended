# Autonomous program: user-milestone optimisation (run until the operator asks for a report)

*The operator's instruction of 2026-11-14, kept verbatim below. Coordinator: the session that holds program U
(stage-2-0c on 2026-11-14; D-620, D-621). Its companion files: `docs/USER_MILESTONES.md` (definitions),
`docs/AUTONOMOUS_QUEUE.md` (the ranked queue), `docs/AUTONOMOUS_PROGRESS.md` (the log),
`docs/HANDOFF_USER_JOURNEY_PROGRAM.md` (program U's rules).*

---

**Use a workflow:** you are authorised to run multi-agent workflows, background agents, worktrees and
/loop self-pacing for this program. Work continuously and independently. Do NOT ask the operator for next
steps, approvals or choices; keep a safe default, record it under a decision row, and continue (CLAUDE.md:
"A research question never goes to the operator"). Stop only when the operator writes in this session; then
give the progress report (below) and wait.

## Hard limits (never cross, whatever a result suggests)
- No payment, purchase, subscription, billing change or credit draw: state the cost in
  `docs/OPERATOR_SETUP.md` and move on.
- No live orders.
- No reading of a confirmation window (`config/windows.yaml`; NQ from 2026-07-17 is reserved).
- No edits under `vendor/`.
- No change to the D-145 gate or `docs/SUCCESS_CRITERIA.md`.
- No deleting or overwriting result files.
- No conduct-tier-1 designs: no hedging across accounts or firms, nothing that conceals a pattern.
  `hypothetical_hedge` work is context only.
- Every firm rule you rely on is verified on the official help centre first (rules-verifier); an
  unverified rule is never loaded.
- CLAUDE.md applies in full: pre-register before running, numbers only from result files with manifests,
  exploratory labels, every variant counted, the failure protocol (diagnose, never rerun until it passes).

## The objective (separate from the gate)
Optimise the product for the USER's milestones, for a user starting on any day:
1. the smallest starting bankroll to reach the first payout (p90);
2. the fastest, cheapest first evaluation pass;
3. the fastest first payout at the best payout per dollar spent (does spending more for bigger payouts pay
   for the time?);
4. the share of users in profit at 1, 2, 3, 6 and 12 months;
5. consistency across users: the spread of start-day outcomes, droughts, and the concentration of profit
   in the luckiest starts;
6. the share of that spread due to execution luck rather than design.

The D-145 gate verdicts stay as they are; this program keeps its own exploratory scoreboard beside them.

## Phase 0: baseline and frozen rules (do first; everything later depends on it)
1. **Coordinate.** stage-2-0c holds D-620 (a 252-session start-day journey re-read of FV3-C and P-13 to
   P-16), and D-619 is the hypothetical hedge-cycle study. Use and extend their outputs, never duplicate
   them. Check ListAgents and the latest decision row before every row you write.
2. **Audit.** Run Parts A and B of the user-journey audit (the inventory of everything modelled, with each
   milestone defined exactly from engine fields). Write `docs/USER_MILESTONES.md` with the definitions.
3. **Declare one decision row, before reading any new result.** It holds:
   - the user scorecard: each milestone's measure, and the row to beat (the best existing design on that
     scorecard, from files already on record);
   - the selection rule: a candidate must beat the row to beat on the scorecard's primary milestone
     without losing more than a declared tolerance on any other;
   - the overfitting guards:
     - selection on development start days only;
     - every choice made on one block of start days and judged on a held-out block (walk-forward over
       start days);
     - variant counts and a multiplicity budget across the whole program (0.05/N bounds where a bound
       applies);
     - fresh seeds;
     - no lever chosen on the same draws it is judged on;
   - the compute rules: at most about 8 concurrent agents and heavy jobs (memory pressure on this
     machine), clean-checkout runs (`scripts/run_clean.py`, D-474), a watch on every long job.

## Track 1: rule and risk-management levers on existing models (run in parallel)
Re-read previous tests (P-13 to P-16, FV3-C and the screens on file) for intra-firm and risk-management
settings that could move the user milestones without changing the signal. One pre-registered family per
lever group. Each is judged on the held-out start-day blocks.

| Lever group | Settings |
|---|---|
| Seats | seat count, and ramping seats up over the first weeks |
| Purchase budget | K and window |
| Sizing table | early-account caution against boldness; bankroll-aware sizing |
| Funded leg | funded cap; payout policy (when and how much); Standard against Consistency path |
| Evaluation settings | daily loss limit option; account size ($50K against larger), only once verified |
| Pausing | pause or stop rules after drawdowns; a "first payout first" mode |
| Hours | P-16 trades 17:00 to 09:00 CT; a user who can only trade US hours, or only London |

Close a family if it doesn't beat the row to beat on its held-out block. Carry a winner as a NEW candidate,
never as a tweak to an existing verdict.

## Track 2: new execution models built for the milestones (run in parallel with Track 1)
Following `docs/RESEARCH_PROTOCOL.md` and the search program (`docs/HANDOFF_SEARCH_PROGRAM.md`):
1. a model card, passing `validate_card`;
2. a cheap local screen on development bars;
3. a family pre-registration;
4. the campaign run;
5. the audit.

The target is the user scorecard, using Track 1's best settings as each family's protocol.

Signals are judged on supply, resolution and cost, not win rate (D-452). Manual-execution latency counts
(L declared on the card), and so does the user's hours.

Anything that needs the operator (QuantConnect runs, data purchases) goes to `docs/OPERATOR_SETUP.md`, and
the program continues on local data.

## Orchestration
- **Parallelism:** one coordinator (this session) owns `DECISIONS.md`, `NEXT_STEPS.md`, numbering and
  merges. Agents work in worktrees or clean checkouts on one family each. They propose decision-row text,
  and the coordinator writes it.
- **Worktree caveat:** worktrees under `.claude/worktrees` refused on 2026-11-14 because git resolves them
  to the OneDrive path. Fix or avoid that first; `scripts/run_clean.py` clean checkouts work.
- **The queue:** keep a ranked queue in `docs/AUTONOMOUS_QUEUE.md`, ordered by expected information value
  against compute cost, with work that can cancel later work first. When a slot frees, start the next item.
  When a result lands, re-rank.
- **The loop:** self-pace with /loop. On each wake:
  1. collect finished work;
  2. run the auditor on anything that matters;
  3. diagnose any failure;
  4. update the scoreboard and the queue;
  5. launch the next items.

  Commit in the background (hooks take 10 to 15 minutes) and push after every commit.
- **Silence:** no chat messages to the operator for routine progress (memory: no idle chat). Log progress
  to `docs/AUTONOMOUS_PROGRESS.md`.

## When the operator writes: the progress report
Then stop launching new work and wait. The report contains:
- the user scorecard: the row to beat against the best candidate on every milestone, from result files,
  with the variant count;
- each family tried: closed, carried or running, with one line on why;
- what changed the picture, and what didn't;
- what the data can't show yet (fills, real churn, firm discretion, out-of-sample);
- the 3 to 5 next tasks you'd recommend, for us to decide together.
