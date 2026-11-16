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
| Q-02 | Agents (5 ported, worker-builder, red-team, scout), skills (3 ported, worker-protocol, run-lock, feature-rules, merge-checklist), commands (8 ported, /dispatch, /collect), Claude hooks (results, decisions, live-trading, fast-tier tests), git hooks (pre-commit fast tier, post-commit push) | lead | done (E-006) | Q-01 | light | 0 | E-006 |
| Q-03 | Worktrees wt-verify, wt-levels, wt-features, wt-firms, wt-scout under `%LOCALAPPDATA%\stage2-extended-wt\`, the bars and atlas linked as directory junctions (never copied, never written) | lead | done | Q-02 | light | 0 | E-006 |
| Q-04 | House tools: this repository's package (`extended/`: the vendored path, a results writer into this repository's `results/` through the vendored `write_result`, `read_result`), `scripts/run_clean.py` (clean detached checkout under `%LOCALAPPDATA%\stage2-extended-runs\`, junctions, log beside it, `--collect`, `--remove`), `scripts/run_lock.py`, `scripts/status.py`, the trace check (empty registry says NOT CHECKED) | wt-verify | done (E-010) | Q-03 | light | 0 | -- |
| Q-05 | **The identity, completed (bootstrap 4.1 step 6):** U1's start rows (`results/user_journey.csv` section `start`, every column) reproduced for P-14 and P-16 by the vendored `user_journey` replay -- 4 starts in the suite, every start from a clean checkout under the run lock. E-004 covered the gate rows only. Until it holds, no result of this repository is believed | wt-verify | done: HOLDS at every start (E-010) | Q-04 | light; the full run heavy | 0 | -- |
| Q-06 | Phase 0 audit, tracks A-E in parallel, read-only: A re-derive the handoff; B the objective; C the engine's money assumptions; D the protocol and F-01 red-teamed; E rules currency on the official pages | scout | done (notes in `docs/audits/phase0/`) | -- | light | 0 | -- |
| Q-07 | Red-team pass over A-E's findings (a fresh agent, given the notes and the files, not the conclusions) | scout | done (`docs/reviews/phase0_red_team_2026-11-15.md`) | Q-06 | light | 0 | -- |
| Q-08 | The audit gate: a decision row; any modelling error that changes a conclusion or an argued objective change goes to STATUS as NEEDS_OPERATOR and is fixed or re-scoped first | lead | done: NOT passed for families (E-007); NEEDS_OPERATOR open | Q-07 | light | 0 | -- |
| Q-09 | First report to the operator: setup, identity, the audit's findings, any NEEDS_OPERATOR | lead | done (the report of 2026-11-15; NEEDS_OPERATOR answered, E-008) | Q-05 (4 starts at least), Q-08 | light | 0 | -- |

## Phase 1 -- research tracks (bootstrap Part 6; families start only after Q-08)

| id | task | owner | state | depends on | weight | retries | row |
|---|---|---|---|---|---|---|---|
| Q-10 | **The shared bracket-label walker** (bootstrap 6.2; F-01 section 7 items 1-4): market and resting entries live from t + 5 min, stop-first, fill-bar rule, trade-through limits, 15:10 CT flatten, costs; its identity against P-16's pinned trades hash; no-look-ahead (shift invariance) and synthetic fill tests; the mirror's zero on random bars. No level outcome is computed. **Redirected 2026-11-15 by audit D-1/D-13/T-13:** the fill-bar settlement and the mirror's booking are parameters (F-01's declared rule and the pair rule with symmetric booking); the mirror test per side and per R on wide-range synthetic walks, expected to fail under the declared rule | wt-levels | done: the full identity HOLDS (E-011) | Q-04 | light; the identity on P-16's entries heavy | 1 | E-003 |
| Q-11 | Feature library (bootstrap 6.2, family B's groundwork): normalised OHLCV features from bars closed at or before t, the shift-invariance test, synthetic data only; no label read. Family B's declaration drafted for the red team, not pinned | wt-features | done (E-016) | Q-04 | light | 0 | -- |
| Q-12 | Other firms' contracts (family C's groundwork): firms with end-of-day drawdown or no consistency rule, each rule read on the firm's own pages (rules-verifier's form), into this repository's rules record; no campaign | wt-firms | done (E-009; recording the short-ranked plans' terms is the rules-verifier's, after Q-19) | Q-02 | light | 0 | -- |
| Q-13 | ~~F-01 stages A-D~~ **withdrawn (E-007; k = 10 spent)**; a corrected level family waits for the operator's answer on judging | wt-levels | withdrawn | -- | -- | 0 | E-007 |
| Q-16 | **The calibrated statistic** (E-008): the trades-first pass line's one-sided test of the lift over the coin twin, delivering 0.05/(k(k+1)) under the trades' dependence (sign-flip nulls on P-16's own pairs, synthetic nulls), with power curves; and the P comparison recalibrated for the scorecard beside (red team M3: the whole rule) | wt-verify | running (`docs/briefs/Q-16_2026-11-15.md`) | Q-05 | light; the calibration may be heavy | 0 | E-007 |
| Q-17 | **The readings beside every user measure** (E-007 (e)): an adapter in this repository replaying a design's starts under the denial ladder, the placement on, the binding Focused Trader models and all-accounts forfeiture (the vendored replay hard-codes 0 %: `customer_slices.py:232`), plus P by month, mean net, CVaR10, P under a bankroll limit, n_eff and the MDD | wt-user | running (`docs/briefs/Q-17_2026-11-15.md`) | Q-05 | heavy | 0 | E-007 |
| Q-18 | Stage 2 D-663's stress checks on P-14, the row to beat (block-resampled days, the bound's coverage, break-even e, missed trades and sessions, slippage) | wt-features | queued (after Q-22, same brief) | Q-22 | heavy | 0 | E-007 |
| Q-19 | Rules readings (rules-verifier): Terms of Use s.8 (outsized positions) against the state table; the breakeven stop move against 10305426's "auto-breakeven"; coordinated trading (10296582, s.27) against one user's five accounts | wt-firms | done (E-012) | Q-12 | light | 0 | E-007 |
| Q-20 | **The breakeven move's fidelity** (E-012 (2)): re-walk P-14's and P-16's trades with (a) the stop-first tie after the move (the walk books the target today, `fv3_rung_walk.py:184-185`) and (b) the move made five minutes after the session open (D-266), each alone and both; read P, the guarded measures and the gate beside the registered rows (exploratory, from a clean checkout) -- R\* itself rests on it | wt-user | queued (after Q-17, same brief) | Q-17 | heavy | 0 | E-012 |
| Q-21 | **The corrected level family drafted** (replaces F-01): every audit and red-team defect corrected, judged on trades first by Q-16's statistic; `prereg/DRAFT_F-02_resting_levels.md`, then red team, gatekeeper, pinning row | wt-levels | done: drafted (E-017); review Q-24 | E-007, E-008 | light | 0 | -- |
| Q-22 | P-15's U1 start rows reproduced (the identity's 25-point coin, for the 25-point scorecard; as E-010's for P-14 and P-16) | wt-features | running (`docs/briefs/Q-22_Q-18_2026-11-15.md`) | E-010 | heavy | 0 | E-016 |
| Q-23 | The red team on family B's draft (`prereg/DRAFT_F-B_multifeature.md`), then the gatekeeper once Q-16 is merged | wt-scout | done: **must be redrafted** (`docs/reviews/DRAFT_F-B_multifeature_2026-11-15.md`); redraft Q-29 | Q-11 | light | 0 | E-016 |
| Q-24 | The red team on F-02's draft (`prereg/DRAFT_F-02_resting_levels.md`), then the gatekeeper once Q-16 is merged | wt-levels | done: **must be redrafted** (`docs/reviews/DRAFT_F-02_resting_levels_2026-11-15.md`); redraft Q-30 | Q-21 | light | 0 | E-017 |
| Q-25 | **A payout-policy family drafted** (how much to withdraw and when in a user's first months; same trades as P-14, so a paired comparison): `prereg/DRAFT_F-P_payout_policy.md`; its pass line for a same-trades lever proposed and marked the operator's | wt-payout | running (`docs/briefs/Q-25_2026-11-15.md`) | E-015 | light | 0 | -- |
| Q-26 | The short-ranked firms' terms recorded on their own pages (rules-verifier), for a solver-only contract-fit read (family C) | wt-firms | running (`docs/briefs/Q-26_2026-11-15.md`) | Q-12 | light | 0 | E-009 |
| Q-27 | **The dispersion report**: `scripts/build_report.py` -- the journey table, a fan chart of cumulative net, the break-even curve, payout sizes and gaps, the evenness trade-off, the denial ladder; every number traced | wt-report | running (`docs/briefs/Q-27_2026-11-15.md`) | E-015 | light | 0 | -- |
| Q-28 | A literature scout: mechanisms that could give a rare edge on the funded opening or predictable resolution speed (the value map's places), ranked, after Stage 2's review | wt-lit | running (`docs/briefs/Q-28_2026-11-15.md`) | -- | light | 0 | -- |
| Q-29 | Family B redrafted per the red team (side and filter centred on the training fold; a population and schedule outside Stage 2's closed opening window if one exists, else the operator's ruling; the right follow twin; calibration on its own persistent sides; the confirmation declared) | wt-scout | running (the Q-11 worker, in wt-scout) | Q-23 | light | 0 | -- |
| Q-30 | F-02 redrafted per its red team (F1: `on`/`pd` breaks vs the breakout-follow effect -- a window-matched placebo, or those cells read as leads, or dropped; F2 past-only placebo days; F3-F10 as readings or rules), with Q-16's statistic once merged | wt-levels | running (the Q-21 worker) | Q-24 | light | 0 | -- |
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
