# DIRECTIVE -- the lead's standing orders

The lead orchestrator's standing orders: **Parts 1, 3, 5 and 6 of the bootstrap, verbatim** (`docs/BOOTSTRAP_NEW_REPO_ORCHESTRATOR.md`,
copied byte-exact from Stage 2 commit a5708aa; sha256 in E-005). They are not edited here; a change is a decision row.

**How the text maps onto this repository** (E-005; the text below is left as written):

| the bootstrap says | here |
|---|---|
| decision rows `D-nnn`, a worker's proposed row `D-NNN` | this repository's rows are **E-nnn** (E-001); Stage 2's are cited as "Stage 2 D-nnn" |
| `main` | `master` |
| `OPERATOR_SETUP.md` | `docs/OPERATOR_SETUP.md` |
| `TASK_QUEUE.md`, `STATUS.md`, `PROGRESS.md` | at the repository root |
| `%LOCALAPPDATA%\<repo>-wt\<name>` | `%LOCALAPPDATA%\stage2-extended-wt\<name>` (branch `wt/<name>`) |
| `%LOCALAPPDATA%\<repo>-runs\` | `%LOCALAPPDATA%\stage2-extended-runs\` |
| the row to beat P-14, the family level 0.05/(k(k+1)) | as `CHARTER.md` section 3 fixes them (E-001: this repository's first family is k = 10) |

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

## Part 3. The objective (from the handoff, section 1)

Improve a **user's journey** on prop-firm accounts: the primary measure **P** is the mean share of start days ahead
(net cash = payouts received less fees paid, above zero) at months 1, 2 and 3; guarded measures are the bankroll
needed (cash before the first payout, p90), the share paid by session 21, sessions to a first payout, payouts per fee
dollar at month 3, the share ahead at months 6 and 12, and the unlucky tenth's month-3 net. **Payouts per fee dollar
is the screening target** (it is what moves P across designs). The row to beat is P-14 (Stage 2). Report a frontier
and a menu under declared limits, never one number. Beside it, always: Stage 2's long-run gate (growth on the
required bankroll at the bound, D-145), so a design that helps users but cannot grow is visible.

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
