# Status -- the live board

Only the lead edits this file (E-005). It holds states, not result numbers: every figure lives in a result file.

**Updated:** 2026-11-18 (E-208; the triage recorded: F-04 and RL3 recast, family B and B-ON parked, Q-126 parked; search years 2020-2023, held-out 2024-2026; the operator confirmed the journey objective (E-008 amended), the review-speed rule and the standing workflow rule; the restart plan's freeze: no k spent under the old pass line; the journey objective drafted, in force on the operator's word; the sequenced merge on master, every identity to be re-held; RL3 pin-ready; the operator's approved proposals queued; F-04 pin-ready, waiting on Q-126; RL3 latency-free, third text; the latency rule amended in the standing texts; F-04 per firm by fixed-sequence testing, second text; RL3 drafted; each firm on its own execution protocol (F-04 drafting); no trading in news hours, executions at all hours, latency 5/3/2 and limit entries counted; the sequenced merge now; three Topstep drafts; Q-126's calibration next; Q-44's user-measure readings recorded and audited, sound with caveats; RD-05, the firm-modes reading, pinned; the firm-modes reading drafted, red-teamed, a second text; heavy markers merged; new firm rules on their branch; four firms read: two by session, two by the operator's hand; multi-firm testing started, four firms at $50K; the second one-sample calibration built and queued; the second breakeven reading and F-03's T-3 queued; the one-sample build's ledger guarded; F-03 closed by Kill B, k = 12 spent, next k = 13; the one-sample build's crash rule tightened; the second one-sample build in its red-team read; Q-45 audited, a second version building; Q-45 collected; F-03's run 1 running; the second one-sample plan pinned; the one-sample plan's sixth text drafting; the licence guard merged; a size hole in the one-sample plan closed before its pin; RD-03's build complete but stage 0; the one-sample floor's basis corrected, a fourth text; F-03's run 1 fixed and re-queued; the licence scan clean, a guard building; a licensed-price derivative held out of git; derived seeds guarded; Q-121's descriptive collected; the one-sample plan's floor back to zero tolerance; F-03's run 1 crashed on a reader defect, fix building; queue part 10; F-03's run 1 running; RD-03's minors cycle; the second one-sample plan's second text drafting; RD-03's stage 0 stopped at its probe; the second one-sample plan drafted, red team reading; the pre-read route fixed within RD-04's 9.3; RD-03's cycle 3 back, stage 0 building; RD-04 pinned; RD-04's third text drafting; Q-121's authorised mode merged, its run re-queued; RD-03's third cycle authorised; RD-04 red-teamed; heavy runs waiting on memory; the volatility descriptive built, its run queued; the failure diagnosed, a second plan queued; the validation's audit clean, the FAILS stands; Q-108's validation FAILS, no one-sample line; RD-03's build back for fixes; Q-121, Q-123 running; volatility-drift note merged, Q-121..Q-123; RD-03 build partial, red team reading; RD-03 pinned E-152; F-03's build merged E-135; F-03 pinned E-095; Q-108's plan pinned E-115; RD-01's and RD-02's runners merged E-121, E-122).

## Phase

**Phase 1** -- families declared and red-teamed (F-02 levels, family B, family O; described readings F-P, RD firms).
The pass line's statistic is `cons` (E-035); no family reads the judged block before its pin, and the first pin
**F-03 (family O, k = 12) pinned (E-095)** -- its build next. F-02 withdrawn before any read: the one-sample
`cons` failed its fresh-seed validation (E-094); F-02 and k = 11 retired unspent. Family B waits for a one-sample
statistic that holds (Q-108).

## The identity (refusing: nothing of this repository is believed until it holds)

| identity | state | row |
|---|---|---|
| P-14's registered gate paths (500, point and bound, every `PATH_COLS` column to 1e-6) | HOLDS, clean clone of ba2d3b5 | E-004 |
| P-16's registered gate paths (500, same) | HOLDS, clean clone of ba2d3b5 | E-004 |
| U1's start rows for P-14 and P-16 (`user_journey.csv` section `start`, all 1,691 starts, both arms, all 68 columns) | **HOLDS**, wt-verify at 8010969 under the lock | E-010 |
| U1's start rows for P-15 (every start) | **HOLDS**, clean checkout of 1d1ab9f under the lock | E-042 |
| the gate rebuilt in `extended/` against P-14's and P-16's gate runs (500 paths, both shifts, no class and pass-through) | **HOLDS**, clean checkout of 6325e09 under the lock | E-044 |
| the walker against P-16's pinned trades (`TRADES_SHA256`, all 239,768 trades) | **HOLDS** (the lead, under the lock, wt-levels at 318d45b) | E-011 |

## NEEDS_OPERATOR

**Answered 2026-11-15 (E-008):** new designs are judged on their trades first (lift over the coin twin, calibrated),
the user scorecard beside against P-14; the verdict keeps 0 % denial with the placement off; hand entry only stays.

**Answered 2026-11-15 (E-013):** Terms of Use s.8 is priced as a risk (tier 3, the denial ladder beside); the breakeven move is allowed as made (its modelling fixed in Q-20).

**Answered 2026-11-16 (E-023):** levers that add no trades are described, never carried; filters that keep the coin's side are tested against a random filter of the same size.

**Open:** none.

**The gate (E-008):** families may be declared (next k = 13 (E-192)) and built; no judged-block read until the U1 identity holds
(Q-05) and the calibrated statistic exists (Q-16). Safe defaults stand (E-007): F-01 withdrawn; `or30` out; the
signal-service purpose dropped; report-day entries after 07:35:00 CT.

## The run lock

`run.lock` at the repository root (git-ignored): **free**. One heavy run at a time on the machine.

## Worktrees (`%LOCALAPPDATA%\stage2-extended-wt\`)

| worktree | branch | task | state |
|---|---|---|---|
| wt-verify | wt/wt-verify | -- (Q-108's build merged, E-127; its calibration queued) | idle |
| wt-levels | wt/wt-levels | -- (F-02 approved, E-065; the pin after Q-55 and Q-83) | idle |
| wt-user | wt/wt-user | -- (Q-103 parked, E-133) | idle |
| wt-features | wt/wt-features | -- (Q-18b merged, E-135) | idle |
| wt-lit | wt/wt-lit | -- (F-03's build complete, E-143; A0 and run 1 queued) | idle |
| wt-firms | wt/wt-firms | -- (Q-115 committed, merge deferred, E-135) | idle |
| wt-payout | wt/wt-payout | Q-119 RD-03's build | running |
| wt-report | wt/wt-report | -- (Q-86 merged, E-062; its run Q-98 queued) | idle |
| wt-scout | wt/wt-scout | Q-120 volatility drift research (read-only) | running |
| wt-infra | wt/wt-infra | -- (Q-118 merged, E-147) | idle |

## Running now

- Heavy, one at a time under `run.lock`, one queue (E-062, E-066): Q-55 done (collected, E-083; audited, its
  condition holds, E-085); Q-83 (the fresh-seed validation F-02's pin needs, at eba1564); then from f7eda0d: Q-44 (the
  readings beside), Q-98 (money spent), Q-22b, Q-80, Q-89, Q-93, Q-35, Q-18, Q-45, Q-101.
- Light: 
  Q-95.

## Machine

Windows 11, 16 GB, the repository on OneDrive. At 2026-11-15 ~21:00 local the machine had about 1.7 GB available and
its commit charge near its limit, held by the operator's other applications. Light work runs; **a heavy run (a
campaign or a full identity, up to about 3 GB) waits for memory** (`docs/OPERATOR_SETUP.md` item 9;
`python scripts/run_lock.py take` refuses a job the machine cannot hold).
