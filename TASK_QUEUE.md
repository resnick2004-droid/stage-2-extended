# Task queue

Ranked: work that can cancel later work comes first. Only the lead edits this file (E-005); a worker's hand-back
proposes changes. Something needed that is not here is added under a decision row before it is done.

**Columns.** `owner` is the worktree (`%LOCALAPPDATA%\stage2-extended-wt\<owner>`, branch `wt/<owner>`) or `lead`
(on `master`) or `scout` (a read-only agent, no worktree). `state`: queued / running / review (hand-back in, the
lead's merge checklist pending) / done / blocked / NEEDS_OPERATOR. `weight`: **light** (reads, code, unit tests on
synthetic data with a time limit, small checks -- run in parallel) or **heavy** (reads the full bars, a solve, a
campaign, the engine beyond a few paths -- one at a time, under `run.lock`). `retries`: corrective cycles used of the
two allowed (DIRECTIVE Part 5 step 3); a third is `NEEDS_OPERATOR`.

## Phase 0 -- set up, then check the research is right (bootstrap Part 4)

| id | task | owner | state | depends on | weight | retries | row |
|---|---|---|---|---|---|---|---|
| Q-01 | Skeleton: DIRECTIVE, STATUS, TASK_QUEUE, PROGRESS; CLAUDE.md machine facts, single writer, run lock; operator asks (remote done, OneDrive, more history) | lead | done | -- | light | 0 | E-005 |
| Q-02 | Agents (5 ported, worker-builder, red-team, scout), skills (3 ported, worker-protocol, run-lock, feature-rules, merge-checklist), commands (8 ported, /dispatch, /collect), Claude hooks (results, decisions, live-trading, fast-tier tests), git hooks (pre-commit fast tier, post-commit push) | lead | running | Q-01 | light | 0 | E-006 |
| Q-03 | Worktrees wt-verify, wt-levels, wt-features, wt-firms, wt-scout under `%LOCALAPPDATA%\stage2-extended-wt\`, the bars and atlas linked as directory junctions (never copied, never written) | lead | done | Q-02 | light | 0 | E-006 |
| Q-04 | House tools: this repository's package (`extended/`: the vendored path, a results writer into this repository's `results/` through the vendored `write_result`, `read_result`), `scripts/run_clean.py` (clean detached checkout under `%LOCALAPPDATA%\stage2-extended-runs\`, junctions, log beside it, `--collect`, `--remove`), `scripts/run_lock.py`, `scripts/status.py`, the trace check (empty registry says NOT CHECKED) | wt-verify | running | Q-03 | light | 0 | -- |
| Q-05 | **The identity, completed (bootstrap 4.1 step 6):** U1's start rows (`results/user_journey.csv` section `start`, every column) reproduced for P-14 and P-16 by the vendored `user_journey` replay -- 4 starts in the suite, every start from a clean checkout under the run lock. E-004 covered the gate rows only. Until it holds, no result of this repository is believed | wt-verify | running (after Q-04) | Q-04 | light; the full run heavy | 0 | -- |
| Q-06 | Phase 0 audit, tracks A-E in parallel, read-only: A re-derive the handoff; B the objective; C the engine's money assumptions; D the protocol and F-01 red-teamed; E rules currency on the official pages | scout | running | -- | light | 0 | -- |
| Q-07 | Red-team pass over A-E's findings (a fresh agent, given the notes and the files, not the conclusions) | scout | queued | Q-06 | light | 0 | -- |
| Q-08 | The audit gate: a decision row; any modelling error that changes a conclusion or an argued objective change goes to STATUS as NEEDS_OPERATOR and is fixed or re-scoped first | lead | queued | Q-07 | light | 0 | -- |
| Q-09 | First report to the operator: setup, identity, the audit's findings, any NEEDS_OPERATOR | lead | queued | Q-05 (4 starts at least), Q-08 | light | 0 | -- |

## Phase 1 -- research tracks (bootstrap Part 6; families start only after Q-08)

| id | task | owner | state | depends on | weight | retries | row |
|---|---|---|---|---|---|---|---|
| Q-10 | **The shared bracket-label walker** (bootstrap 6.2; F-01 section 7 items 1-4): market and resting entries live from t + 5 min, stop-first, fill-bar rule, trade-through limits, 15:10 CT flatten, costs; its identity against P-16's pinned trades hash; no-look-ahead (shift invariance) and synthetic fill tests; the mirror's zero on random bars. No level outcome is computed | wt-levels | running | Q-04 | light; the identity on P-16's entries heavy | 0 | E-003 |
| Q-11 | Feature library (bootstrap 6.2, family B's groundwork): normalised OHLCV features from bars closed at or before t, the shift-invariance test, synthetic data only; no label read. Family B's declaration drafted for the red team, not pinned | wt-features | queued | Q-04 | light | 0 | -- |
| Q-12 | Other firms' contracts (family C's groundwork): firms with end-of-day drawdown or no consistency rule, each rule read on the firm's own pages (rules-verifier's form), into this repository's rules record; no campaign | wt-firms | running | Q-02 | light | 0 | -- |
| Q-13 | F-01 stages A-D (supply and kill lines first; then choose, judge, campaign), each read in its own row from its result file, each run from a clean checkout | wt-levels | blocked | Q-08, Q-10, Q-05 | heavy | 0 | E-003 |
| Q-14 | Family B declared (one pre-registered classifier, purged walk-forward, judged out of fold against the coin) | wt-features | blocked | Q-08, Q-11 | light | 0 | -- |
| Q-15 | Stress checks of Stage 2 D-663 on any candidate; the audit's engine fixes | wt-verify | blocked | a candidate; Q-08 | heavy | 0 | -- |

## Done before the bootstrap (the handoff's section 7)

- [x] Charter -- `CHARTER.md` (E-001).
- [x] Stage 2 vendored read-only with its identity -- `vendor/stage2/`, `identity/stage2_identity.py`, `tests/` (E-002);
  the gate-row identity holding at all 500 registered paths of P-14 and P-16 from a clean clone (E-004).
- [x] First family declared before it is built -- `prereg/F-01_resting_order_level_atlas.md` (E-003).

## Later sides (handoff 3.3), each a family declared in its own row

- Payout policy for a user's first months (tested in Stage 2 for long-run growth only).
- Closing a crippled funded account at request -- only once Topstep answers (`docs/OPERATOR_SETUP.md` item 3).

## Closing checklist (CHARTER section 5)

- [ ] every declaration and outcome on record; the decision log complete
- [ ] every number in a document traced to a result file with a manifest
- [ ] `vendor/stage2/` unedited (`tests/test_vendor_integrity.py`) and its identity holding
- [ ] (A) a carried design, registered, audited and confirmed on unread data -- or (B) the documented negative result
