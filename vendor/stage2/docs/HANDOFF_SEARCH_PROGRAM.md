# Handoff: the rolling model search (program S, D-578)

**Owner:** the Stage 2 owning session (see memory `project-stage2-reset-owner`). Read `CLAUDE.md` first.

## What the operator asked (2026-11-05)

"Autonomously run these tests again the way we did the first time with all integrity checks and safety protocols in
place for an authentic backtest." That means: keep searching for models that beat P-16 (`rc_s150_all_nr`, the 37.5-point
news-safe coin on 5 Topstep seats, the best development row), using the same discipline as family A4 (D-550..D-558).

## The rules (fixed in D-578 and `config/search_program.yaml`; never loosened)

1. A batch's menu is fixed under its own decision row **before** its code is built. Nothing declared is edited; a change is
   a new batch.
2. Batch k spends 0.05 / (k (k + 1)) of one program-wide 5 % budget (S1 2.5 %, S2 0.83 %, S3 0.42 %, ...).
3. NQ development data only (to 2026-07-16). Nothing later is read.
4. Every run comes from a clean checkout (`scripts/run_clean.py --name X -- python scripts/...`, then `--collect`), with
   `scripts/watch_job.py` beside it.
5. Campaign guards (all four): +0.05 over P-16 at the bound (paired), resolves every offered R, ≥ 40/50 coin sequences,
   not below P-16 on either span alone.
6. A candidate: a registered dev test (`/prereg`, prereg-gatekeeper; N counts everything) → auditor → one confirmation on
   unread data. That data needs a purchase: state the cost and wait (`docs/OPERATOR_SETUP.md` items 1 and 6).
7. Every batch's reading gets its own D-row, built from the result file (never typed numbers). Run
   `scripts/build_report.py` before committing variants. Push after every commit.

## The queue

| batch | what | status |
|---|---|---|
| S1 | sided coin: P-16 unchanged, side from 15 declared bar rules; stage 1 lift max-stat at 2.5 %, stage 2 campaign | read: no candidate (D-580) |
| S2 | state-gated coin: P-16 with offers kept only in a declared ex-ante state (5 cells); campaign guards | read: no candidate (D-582) |
| S3 | sided coin, new event kinds: 13 rules (1-3 min breakouts, n-bar, two gaps, outside and range-expansion bars); stage 1 lift max-stat at 0.42 %, stage 2 campaign | read: one candidate at L = 0 (D-588, audited D-589); FAILS at L = 5, closed (D-592) |
| S4 | sided coin, Point & Figure direction (the operator's catapult spec, D-607/D-609): 10 rules (most recent catapult / plain triple top side, boxes 2.5-10 points incl. the contract-sized 6.25), read at t - 5; stage 1 at 0.25 % | read: no candidate (D-616) |
| PFA (own family, not S) | the catapult's natural bracket at L = 5, rest entry: cheap screen with three contract-fit kill lines (D-611, D-612) | read (D-617): only the 2.5-point box survives, net R below zero; its campaign vs P-16 (each trade's own stop and count target) is the next declaration, not started |

**Latency (D-589):** from S4 on every rule reads bars closed at or before the mark minus L = 5 minutes (D-266).

Templates: `scripts/a4_coin_atlas.py` + `propedge/research/a4_coin_atlas.py` (stage 1 lift and the studentised
bootstrap), `scripts/rc150_routing.py` (paired run, 50-coin guard, spans, the coin-swap identity).

## Each batch, step by step

1. Build in a worktree (a subagent), tests first. The identity check comes first: with the rule replaced by P-16's coin,
   the cell's content hash equals P-16's.
2. Record the build's readings in a D-row before running. Merge, commit, push.
3. Run from a clean checkout and watch it. Collect, then commit the result with its manifest.
4. Read it in a D-row. Send any candidate to the auditor. Report to the operator in plain language, results only.
5. Next batch. When the queue is empty, propose new batches (`proposed_not_declared` in the yaml) under a new D-row.
