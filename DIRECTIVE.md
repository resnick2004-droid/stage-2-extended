# DIRECTIVE -- the lead's standing orders

The lead orchestrator's standing orders: **Parts 1, 3, 5 and 6 of the bootstrap**, first taken verbatim (`docs/BOOTSTRAP_NEW_REPO_ORCHESTRATOR.md`,
copied byte-exact from Stage 2 commit a5708aa; sha256 in E-005). They are not edited here except where a decision row amends them in place (E-203: Parts 1 and 6.2's latency; E-NNN: the journey objective in Parts 3, 5 and 6); every such amendment is listed in the table below.

**How the text maps onto this repository** (E-005; the text below is left as written, except the amendments in place that the table's last two rows list):

| the bootstrap says | here |
|---|---|
| decision rows `D-nnn`, a worker's proposed row `D-NNN` | this repository's rows are **E-nnn** (E-001); Stage 2's are cited as "Stage 2 D-nnn" |
| `main` | `master` |
| `OPERATOR_SETUP.md` | `docs/OPERATOR_SETUP.md` |
| `TASK_QUEUE.md`, `STATUS.md`, `PROGRESS.md` | at the repository root |
| `%LOCALAPPDATA%\<repo>-wt\<name>` | `%LOCALAPPDATA%\stage2-extended-wt\<name>` (branch `wt/<name>`) |
| `%LOCALAPPDATA%\<repo>-runs\` | `%LOCALAPPDATA%\stage2-extended-runs\` |
| the row to beat P-14, the family level 0.05/(k(k+1)) | the baselines -- naive coin harvesting, P-14, P-15, P-16, each under the design's convention -- and the level 0.05 / (k (k + 1)), one k per held-out test, as `CHARTER.md` sections 3.7-3.8 fix them (E-001: the program's first family here was k = 10; the next k is 13) |
| Part 3: P primary, payouts per fee dollar the screening target | **amended by the operator (E-008; then E-207, E-NNN), and Part 3 rewritten in place:** a design is judged on the user's journey under zero edge (`CHARTER.md` sections 2-3), on the martingale-outcome reading: inside every operator limit with margin wider than its noise (E-207; the alternative form pending the operator, O-5), each baseline beaten on the composite pinned before the survey (or the pinned fallback, P under the bankroll stop) by the calibrated coin-seed test on the held-out years (a level bounding coin luck on that history; the history-level false-pass rate beside), the time leg a consistency condition, with the floors of CHARTER section 3.8; the trades' lift over the coin twin is no pass line; the verdict keeps 0 % denial, the placement off and the Focused Trader Program off; hand entry only stays |
| Part 1 and Part 6.2: "at least 5 minutes" | **amended in place (E-203):** at least L minutes, L = 5 the reference, 3 and 2 counted variants (E-202 (2)(c)) |
| Part 3, Part 5's worktree list and report, Part 6.2's test, 6.3 A, B and C, the power paragraph, "A candidate" | **amended in place (E-NNN):** judged on the journey under zero edge, not on a coin-twin lift; RL3 recast and F-02 and family B parked (E-208); each firm its own baselines; the data question asked before the first search pin |

---

## Part 1. Hard limits (never crossed, whatever a result suggests)

- **No payment, purchase, subscription, billing change or credit draw.** State the cost in `OPERATOR_SETUP.md` and
  move on.
- **No live orders, and no automated or API order entry design** -- the operator: it gets prop accounts banned.
  Every model is executed by hand with at least L minutes from alert to order (L = 5 the reference; 3 and 2 counted
  variants, E-202); resting orders may be published ahead.
- **No read of a confirmation window.** NQ from 2026-07-17 is reserved; it is not on disk, keep it that way. Declare a
  confirmation window per market before any development read.
- **No edit of anything vendored** (Stage 2's engine, stage one's propsim). Adapt in your own code.
- **No conduct-tier-1 design:** no hedging across accounts or firms, no simulator-fill exploitation or tight-bracket
  scalping, no maximum size into major news, no copying one trade across accounts, nothing that conceals a pattern.
- **No firm rule is used unless verified** on that firm's official help pages, with article id and date.
- **No result number typed into a document.** Numbers come from result files with manifests.
- **No result file deleted or overwritten.** A new reading is a new file under its own decision row.
- **The objective (Part 3) changes only with the operator.** Propose; do not adopt.

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

## Part 5. The loop (how the lead runs the work)

**Roles.** The lead works on `main` and writes no model code. It alone appends to `DECISIONS.md`, edits
`STATUS.md`, `TASK_QUEUE.md`, `PROGRESS.md`, merges branches and pushes. Workers propose decision rows as one finished
line with `D-NNN`; the lead numbers and commits them.

**Worktrees always in use** (the operator wants several working at all times):
- `wt-verify` -- the research-structure track: the identities, the audit's fixes, stress checks, the engine.
- `wt-levels` -- signal sources and the mix: the trigger library by session, the naive coin, the component
  scheduler, the mix router and its no-opposing-positions guard (E-208).
- `wt-features` -- the lever map and the search: the lever-space sampler, the surrogate, the round proposer, the
  plateau check (E-208).
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
scorecard against each baseline inside the limits, with the variant count; each search's round, its finalists, its held-out read ledger, and each design closed, carried or running with one line why;
what changed the picture; what the data cannot show; three to five next tasks), and wait.

## Part 6. Phase 1 -- the research tracks

### 6.1 What the handoff established (do not repeat)

Nine lever families and an account-size fit read are closed (handoff 3.1); rare calendar effects are dropped (too few
signals); OHLC rule searches against the coin twin found nothing that survives costs and latency (handoff 3.2).
Supply comes from a schedule (P-16's 5-minute marks); an edge is a side or a filter on those offers; a rare edge
belongs on the funded openings and a frequent one on every trade (the value map, handoff 2.7).

### 6.2 Labels and features (shared by every model family)

- **Label:** for each candidate alert time t, entry no earlier than t + L minutes (L = 5, or a counted 3 or 2, E-202; a market entry) or a resting order
  live from t + L that fills when the bar trades through its level (a limit needs a trade-through by one tick); the
  stop from the stop band; targets at each R; resolved by 15:10 CT as win, loss or flatten; a bar that could hit
  entry, stop and target is read stop-first. Stage 2's walks hold this for every 5-minute mark at market entry.
- **Features:** only from bars closed at or before t; normalised (rolling ATR, session spread, time-of-day medians),
  never raw price levels; a test that shifting the bars after t changes no feature (shift invariance).
- **The test:** a signal source is judged by what it adds to a design's journey under zero edge (`CHARTER.md`
  sections 3.2-3.8): its fills from the real orders, the path after each fill reflected with probability one half
  and each outcome redrawn at its bracket's driftless odds for the deciding reading, over paired seeds, its properties read -- supply, timing, resolution speed for a given shape, clustering, how
  differently timed it is from other components, hand-executability; supply and resolution gates before any outcome
  is read; nothing read on the held-out years outside a held-out test. The lift over the coin twin is no pass line
  (E-NNN).

### 6.3 The first families (each declared in its own row before it is built)

- **A. Resting-order levels, as triggers** (`wt-levels`): levels known before they trigger (prior day high/low,
  overnight high/low, opening-range high/low after it closes, frozen session-VWAP bands, round numbers, prior swing
  points); stop-entry for a break and limit for a pullback; the ticket published at least L minutes before it can
  trigger (L = 5 the reference; 3 and 2 counted variants, E-202); R values and an expiry as levers in the declared
  lever space; fill rate and adverse selection measured; judged under `CHARTER.md` section 3.2's zero edge (the path
  after the fill reflected with probability one half, and each outcome redrawn at its bracket's driftless odds for the
  deciding reading), the as-traded result beside as a stress; RL3 recast as an NY AM component, F-02 parked (E-208);
  one k per held-out test.
- **B. Feature library, then the lever map's surrogate** (`wt-features`): 30-50 normalised OHLCV features, kept as
  components for triggers' timing and resolution speed (`feature-rules` binds every source that reads bars); family
  B as a direction model is parked (E-208: Q-14, Q-95, Q-149; `features.py` and the B2 machinery kept); the
  machine learning is the surrogate over the lever space (`CHARTER.md` section 3.3) -- fitted on the search years'
  survey, proposing each round inside the limits, its method, rounds and seeds declared and every design it tries
  counted. Rules read off it afterwards (SHAP and the like) are exploratory and need their own declaration.
- **C. Other firms' contracts** (`wt-firms`): firms with end-of-day drawdown or no consistency rule, verified on their
  own pages; each firm its own execution protocol and its own baseline set, at least the naive coin on its own
  protocol (E-202); a solver-only contract-fit read first, described; a design search for the firm only under
  `CHARTER.md` section 3, its held-out years subject to their single use per market (section 3.6 (c)).
- **D. Structure** (`wt-verify`, continuous): the identities, the audit's fixes, the stress checks of D-663 on any
  candidate.

**Power:** six and a half years of NQ give low power for rare effects. More history (QuantConnect's free NQ/ES from
2009, which needs the operator's QuantConnect user ID and API token configured; or a Databento purchase of older bars,
stated not authorised) is the operator's call -- put both in `OPERATOR_SETUP.md` in your first commit, and put the question to the operator with the power gate's result before the first design search is pinned (`CHARTER.md` section 3.7), never after a failure.

**A candidate** is a finalist of a declared search that passes `CHARTER.md` section 3.8 in its place in the finalist
sequence on the held-out years, on the martingale-outcome reading: inside every operator limit with margin wider than
its noise (E-207; O-5 pending), each baseline beaten on the pinned composite by the calibrated coin-seed test at its
k's level (the history-level false-pass rate beside), the time leg's conditions met, the floors holding (the
zero-edge gate, the fill and supply stress and the as-traded floors among them). It is then registered with the gatekeeper, audited, and waits for
confirmation data (a purchase: the operator's).
