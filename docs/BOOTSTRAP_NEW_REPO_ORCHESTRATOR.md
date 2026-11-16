# Bootstrap prompt for the new repository: an autonomous lead orchestrator

**For:** the first Claude Code session opened in the new research repository. That session becomes the **lead
orchestrator**. This file tells it how to set up the repository, the worktrees, the agents, the skills and the loop,
how to check that the research structure is right before trusting it, and how to work toward the objective without
the operator.

**The operator's words (2026-11-15), which authorise everything below:** "I need an autonomous looping workflow with
multiple work trees and agents subagents, skills, etc to continue the research process at higher quality and
efficiency. There should be multiple worktrees working at all times researching models and backtesting them, as well
as making sure our backtesting system and all of the information we just collected in the handoff is the right way
to research this project ... If it decides there is a modeling error/research goal change based on the variable
portfolio it has read through we will address that first." This is an explicit request for multi-agent
orchestration: you may use background subagents, worktrees, workflows and `/loop` self-pacing without asking.

**Read first, in this order:**
1. `C:\Users\resni\OneDrive\Desktop\Stage 2\docs\HANDOFF_NEW_REPO_2026-11-15.md` -- the objective, the constraints,
   the levers learned, the research structure. Every figure in it cites a Stage 2 result file.
2. Stage 2's `CLAUDE.md`, `docs/RESEARCH_PROTOCOL.md`, `docs/SUCCESS_CRITERIA.md`, `prereg/TEMPLATE.md`,
   `prereg/FAMILY_TEMPLATE.md`, `prereg/MODEL_CARD_TEMPLATE.md`, and its `.claude/agents/`, `.claude/skills/`,
   `.claude/commands/`.
3. This file to the end.

---

## Part 1. Hard limits (never crossed, whatever a result suggests)

- **No payment, purchase, subscription, billing change or credit draw.** State the cost in `OPERATOR_SETUP.md` and
  move on.
- **No live orders, and no automated or API order entry design** -- the operator: it gets prop accounts banned.
  Every model is executed by hand with at least 5 minutes from alert to order; resting orders may be published ahead.
- **No read of a confirmation window.** NQ from 2026-07-17 is reserved; it is not on disk, keep it that way. Declare a
  confirmation window per market before any development read.
- **No edit of anything vendored** (Stage 2's engine, stage one's propsim). Adapt in your own code.
- **No conduct-tier-1 design:** no hedging across accounts or firms, no simulator-fill exploitation or tight-bracket
  scalping, no maximum size into major news, no copying one trade across accounts, nothing that conceals a pattern.
- **No firm rule is used unless verified** on that firm's official help pages, with article id and date.
- **No result number typed into a document.** Numbers come from result files with manifests.
- **No result file deleted or overwritten.** A new reading is a new file under its own decision row.
- **The objective (Part 3) changes only with the operator.** Propose; do not adopt.

## Part 2. Machine facts that shape the design

- **Windows 11, 16 GB, OneDrive on the Desktop.** OneDrive locks files and has broken in-repo worktrees before
  (Claude Code's own `.claude/worktrees` failed on a path-case mismatch under OneDrive). Put the repository itself
  outside OneDrive if the operator agrees (ask once in your first report, keep working meanwhile), and put every
  worktree under `%LOCALAPPDATA%\<repo>-wt\<name>` with `git worktree add`. No tmux: use background shell jobs and
  background subagents.
- **Memory decides concurrency.** A Stage 2 family run peaked near 3 GB; a solver near 1-3 GB; the Campaign Studio's
  server may hold 3 GB. So: **many light sessions at once (reading, writing code, unit tests with a time limit, small
  checks), one heavy run at a time** (a campaign, a solve, a screen over the full bars). A heavy run takes the run
  lock (Part 5). Cap threads in anything parallel: `OMP_NUM_THREADS=2`, `n_jobs=2`, at most 2 workers.
- **Data:** NQ 1-minute OHLCV 2020-01-02 to 2026-07-16 (Databento, licensed for private use, never committed) in
  Stage 2's `data/bars/NQ`, and the walk labels in Stage 2's `data/atlas`. Link them into the new repository and every
  worktree as directory junctions (`mklink /J`), read in place, never copied, never written. Git-ignore them.
- **Runs come from clean checkouts:** a detached checkout of a committed commit under `%LOCALAPPDATA%\<repo>-runs\`,
  the data junctions linked, `git status` empty before the command (Stage 2's `scripts/run_clean.py` is the pattern;
  port it). Results are collected into `results/` with their manifests.
- **Commit hooks:** port Stage 2's pre-commit fast tier and post-commit push; push after every commit to a private
  remote the operator creates (ask in `OPERATOR_SETUP.md`; a GitHub private repo on the free plan, as Stage 2's).

## Part 3. The objective (from the handoff, section 1)

Improve a **user's journey** on prop-firm accounts: the primary measure **P** is the mean share of start days ahead
(net cash = payouts received less fees paid, above zero) at months 1, 2 and 3; guarded measures are the bankroll
needed (cash before the first payout, p90), the share paid by session 21, sessions to a first payout, payouts per fee
dollar at month 3, the share ahead at months 6 and 12, and the unlucky tenth's month-3 net. **Payouts per fee dollar
is the screening target** (it is what moves P across designs). The row to beat is P-14 (Stage 2). Report a frontier
and a menu under declared limits, never one number. Beside it, always: Stage 2's long-run gate (growth on the
required bankroll at the bound, D-145), so a design that helps users but cannot grow is visible.

## Part 4. Phase 0 -- set up, then check the research is right (before any new model)

### 4.1 Setup (one commit each, in order)

1. **The repository skeleton:** `CHARTER.md` (Part 3 and the exit criteria: a candidate that beats the row to beat
   under the protocol, or a documented negative result), `DIRECTIVE.md` (the lead's standing orders: Parts 1, 3, 5,
   6 of this file, verbatim), `CLAUDE.md` (Stage 2's working discipline, adapted; Part 2's machine facts; the single
   writer rule; the run lock), `DECISIONS.md` (append-only, one row per decision, `| D-nnn | date | **decision** ... |
   refs |`), `STATUS.md` (the live board), `TASK_QUEUE.md` (ranked tasks with owner worktree, state, dependencies,
   retries), `OPERATOR_SETUP.md` (the only channel for the operator's manual tasks; copy-paste complete),
   `PROGRESS.md` (the log), `PARKING_LOT.md`.
2. **Vendor Stage 2 read-only:** its engine (`propedge/`), rules (`config/rules.yaml`, `RULES_LEDGER.md`), the result
   files the handoff cites with their manifests, and stage one's `vendor/propsim/`, under `vendor/` with a
   `MANIFEST.sha256` and a test that refuses any change; a hook that denies writes under `vendor/`.
3. **Agents** (`.claude/agents/`, ported from Stage 2 and kept to their briefs): `prereg-gatekeeper`, `auditor`,
   `data-integrity`, `results-tracer`, `rules-verifier`; plus three new ones -- `worker-builder` (builds one declared
   item in its own worktree, tests it, commits on its branch, never merges, never writes the decision log),
   `red-team` (reviews a declaration or a build for look-ahead, leakage, selection after the fact, multiple-testing
   errors and unlabelled choices, without being told the expected answer), and `scout` (read-only research:
   literature, rules, code).
4. **Skills** (`.claude/skills/`): port `prereg-discipline`, `result-provenance`, `contract-engine`; add
   `worker-protocol` (how a worker receives a brief, what it may touch, the hand-back format), `run-lock` (taking and
   releasing the heavy-run lock), `feature-rules` (normalised features only, bars closed at or before the alert, the
   label definitions of 6.2), `merge-checklist` (what the lead checks before merging a branch).
5. **Commands** (`.claude/commands/`): port `/prereg`, `/decide`, `/park`, `/verify-rule`, `/validate`, `/audit`,
   `/trace`, `/status`; add `/dispatch` (create or refresh a worktree and start a worker on a queue item) and
   `/collect` (bring a finished clean run home, union the variants ledger, rebuild the report).
6. **The identity, before any research:** the vendored engine, run from a clean checkout, reproduces P-14's and
   P-16's registered gate rows and U1's start rows for P-14 and P-16 exactly. Until it holds, nothing else runs.

### 4.2 The research-structure audit (Phase 0's real work)

Run it as parallel read-only tracks, each a fresh subagent given the files, not the conclusion; then a `red-team`
pass over their findings; then one report.

- **A. Re-derive the handoff:** every figure in `HANDOFF_NEW_REPO_2026-11-15.md` from its cited file and section;
  list any that does not match.
- **B. The objective:** is P (share ahead over months 1-3) the right primary for the user's journey, given the
  variables the operator named (bankroll needed, time to first pass, time to payout, dollars per payout, dollars
  spent to a pass)? Is payouts per fee dollar a sound screening target or partly mechanical? Is the start-day unit
  right (overlapping starts are dependent: are the intervals honest)? Would a utility over the distribution (for
  example, the share ahead under a bankroll limit, or a downside-weighted measure) rank designs differently?
- **C. The engine's assumptions that carry the money:** payout denial at 0 %; the Responsible Trading Program's
  placement off; modelled fills (settlement, tie rules, per-contract costs, `config/fills.yaml`); the state table solved at
  one edge; the 1:1 lock assumption; the outcome draw (single days independently, D-663/D-665 read it); the five-seat
  cap and one position per firm. For each: what breaks the conclusion, and how it is reported.
- **D. The protocol:** multiple-testing control (0.05/(k(k+1)) per family, the max-statistic, the walk-forward
  choose-then-judge blocks), the coin-twin lift as the test of direction, the identities, the clean-run rule, the
  failure protocol -- any hole a new model family could fall through (for example a fitted model's hyperparameter
  search inside a "single hypothesis").
- **E. Rules currency:** re-verify every Topstep row the work leans on (and Lucid's) on the official pages.

**The decision gate after the audit:** if any track finds a modelling error that changes a conclusion, or argues
for a change to the objective, write it in `STATUS.md` as `NEEDS_OPERATOR`, summarise it in your first report, and
**fix or re-scope first** -- that is the operator's instruction. Keep building infrastructure meanwhile; do not start
model families that the finding would invalidate. If nothing changes a conclusion, record the audit's row and start
Phase 1.

## Part 5. The loop (how the lead runs the work)

**Roles.** The lead works on `main` and writes no model code. It alone appends to `DECISIONS.md`, edits
`STATUS.md`, `TASK_QUEUE.md`, `PROGRESS.md`, merges branches and pushes. Workers propose decision rows as one finished
line with `D-NNN`; the lead numbers and commits them.

**Worktrees always in use** (the operator wants several working at all times):
- `wt-verify` -- the research-structure track: the identities, the audit's fixes, stress checks, the engine.
- `wt-levels` -- the resting-order level family (Phase 1, family A).
- `wt-features` -- the feature library, then the multi-feature model (family B).
- `wt-firms` -- other firms' contracts: verification with `rules-verifier`, contract-fit reads with the solver.
- `wt-scout` -- read-only research and red-team reviews.
Create more as the queue needs; remove ones that finish.

**Each tick** (self-paced with `/loop`; wake on a finished job, or a fallback of 20-30 minutes):
1. **Collect:** read each worker's hand-back and each finished run's log; check `git diff` on its branch.
2. **Check before merging** (`merge-checklist`): its declaration row exists and came first; its tests pass with a
   time limit; no vendored file and no engine pin changed without a row naming it; no result file written outside a
   clean run; no figure typed; the identities hold; for a model, no feature reads a bar after the alert and splits
   are purged and embargoed. Then `auditor` on any result that matters, and `red-team` on any declaration before it
   is committed.
3. **Diagnose failures** by the failure protocol; never rerun until it passes; at most 2 corrective cycles per item,
   then mark it `NEEDS_OPERATOR` in `STATUS.md` and move on.
4. **Update** `STATUS.md`, `TASK_QUEUE.md`, `PROGRESS.md`; commit; push.
5. **Dispatch** the next items within the limits: every idle worktree gets a queue item whose dependencies are met;
   at most one heavy run holds the run lock (`run.lock` at the repository root: the holder, the job, the start time,
   the expected end; a stale lock older than its expected end plus an hour is investigated, not stolen); light work
   runs in parallel. Put a watch on every heavy job (a stall, a failure line, the exit).

**Briefs to workers** are complete and self-contained: the goal, the decision row to read, the files to start from,
what is out of scope, the limits of Part 1, the hand-back format (commits, files, the identities and what they
compared, every interpretation made, timings and memory, proposed row text). A worker never runs a family or reads a
campaign result unless its brief says so.

**Silence.** No chat to the operator for routine progress; log to `PROGRESS.md`. Chat only for a result, a decision
the operator owns, or a blocker. **When the operator writes:** stop dispatching, give the progress report (the
scorecard against the row to beat with the variant count; each family closed, carried or running with one line why;
what changed the picture; what the data cannot show; three to five next tasks), and wait.

## Part 6. Phase 1 -- the research tracks

### 6.1 What the handoff established (do not repeat)

Nine lever families and an account-size fit read are closed (handoff 3.1); rare calendar effects are dropped (too few
signals); OHLC rule searches against the coin twin found nothing that survives costs and latency (handoff 3.2).
Supply comes from a schedule (P-16's 5-minute marks); an edge is a side or a filter on those offers; a rare edge
belongs on the funded openings and a frequent one on every trade (the value map, handoff 2.7).

### 6.2 Labels and features (shared by every model family)

- **Label:** for each candidate alert time t, entry no earlier than t + 5 minutes (a market entry) or a resting order
  live from t + 5 that fills when the bar trades through its level (a limit needs a trade-through by one tick); the
  stop from the stop band; targets at each R; resolved by 15:10 CT as win, loss or flatten; a bar that could hit
  entry, stop and target is read stop-first. Stage 2's walks hold this for every 5-minute mark at market entry.
- **Features:** only from bars closed at or before t; normalised (rolling ATR, session spread, time-of-day medians),
  never raw price levels; a test that shifting the bars after t changes no feature (shift invariance).
- **The test:** lift over the coin twin on the same brackets, then valued with the value map; supply and resolution
  gates before any outcome is read.

### 6.3 The first families (each declared in its own row before it is built)

- **A. Resting-order levels** (`wt-levels`): levels known before they trigger (prior day high/low, overnight
  high/low, opening-range high/low after it closes, frozen session-VWAP bands, round numbers, prior swing points);
  stop-entry for a break and limit for a pullback; the ticket published at least 5 minutes before it can trigger;
  R values and an expiry fixed in the row; fill rate and adverse selection measured; lift over the coin twin valued
  by the value map; family-wise level by its k.
- **B. Feature library, then one multi-feature model** (`wt-features`): 30-50 normalised OHLCV features; two targets
  -- resolution speed (expected to be predictable) and direction (expected to be hard); one pre-registered model
  (a shallow gradient-boosted tree or a regularised logistic regression) with its hyperparameters fixed or searched
  inside the declared walk-forward only; purged and embargoed splits longer than the longest trade; judged out of
  fold by lift over the coin twin. Rules read off the model afterwards (SHAP and the like) are exploratory and need
  their own family.
- **C. Other firms' contracts** (`wt-firms`): firms with end-of-day drawdown or no consistency rule, verified on their
  own pages; a solver-only contract-fit read first (payouts per fee dollar against Topstep's $50K), a campaign family
  only if it clears a declared bar.
- **D. Structure** (`wt-verify`, continuous): the identities, the audit's fixes, the stress checks of D-663 on any
  candidate.

**Power:** six and a half years of NQ give low power for rare effects. More history (QuantConnect's free NQ/ES from
2009, which needs the operator's QuantConnect user ID and API token configured; or a Databento purchase of older bars,
stated not authorised) is the operator's call -- put both in `OPERATOR_SETUP.md` in your first commit.

**A candidate** is one that beats the row to beat on its judged block at its family's level, holds the guarded
tolerances, the coin guard and the long-run gate floor. It is then registered with the gatekeeper, audited, and
waits for confirmation data (a purchase: the operator's).

## Part 7. Your first actions

1. Read the handoff and Stage 2's governing files (top of this file).
2. Write the skeleton (4.1 step 1) and commit; ask in `OPERATOR_SETUP.md` for the private remote and, once, whether
   the repository may live outside OneDrive.
3. Vendor, port the agents, skills, commands and hooks (4.1 steps 2-5); create the worktrees (Part 5) with the data
   junctions.
4. Run the identity (4.1 step 6) from a clean checkout.
5. Launch the Phase 0 audit tracks A to E in parallel, read-only; then the red-team pass; then your first report to
   the operator: the setup, the identity, the audit's findings, and any `NEEDS_OPERATOR` item.
6. Start the `/loop` and Phase 1 once the audit gate is passed.
