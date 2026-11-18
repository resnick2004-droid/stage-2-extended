# Red team, second read: RD-05's coin side after corrective cycle 1 (Q-138r2), 2026-11-18

**What I read**

- **The change itself:** `wt/wt-firms`, the diff 9bda841..e53e812 (14 files).
- **In full:**
  - the new `extended/modes_engine.py`;
  - the diffs to `modes_oracles.py`, `modes_rules.py`, `modes_steps.py`, `modes_terms.py` and `modes_reading.py`;
  - the diffs to `scripts/modes_coin.py`, `scripts/modes_rules.py` and `identity/modes_coin_identity.py`;
  - the test diffs.
- **The readings:** E-205's R-a to R-d.
- **Not seen:** the builder's own smoke-run disclosure. I had only E-205's summary of it.

**How I checked**

- Synthetic checks only, on seeds outside section 15's block.
- At most 20,000 accounts.
- No bar read.
- Nothing written but this note.
- No seed literal and no result number appear below.

## Verdict

**Merge the coin side once V-1 is fixed.** V-1 is one line plus a test.

- If the lead merges first, V-1 must land before step 2.
- Every first-read blocker and should-fix item is closed in the code.
- Nothing else found here blocks.
- Nothing in the smoke-run disclosure, as E-205 records it, is a reason not to run step 2 on the declared streams.

## 1. The first read's items, checked closed

| item | closed? | how I checked |
|---|---|---|
| **B-1** | **yes** | Details below the table. |
| **B-2** | **yes** | Details below the table. |
| **S-1 / R-a** | yes | `is_boundary` is the declared conditions plus lattice exactness. The six w = 2 cells now carry the pass ceiling. The cycle also fixed a second defect from the first build: flip cells at a boundary `(index, w, r)` had been exempted from the ceiling. They are off the lattice, so they now carry it, both in `cell_rows` (`policy == "steady"`) and in `oracle_count`. |
| **S-2** | yes | `item_a_specs` compares `EvalSpec(TS-S)`, `FundedSpec(TS/con)` and `FundedSpec(TS/std)` (A-16 off) against the vendored functions at `rules_from_ledger()`: all 24 cells, every array, on the `coin_identity` streams. Item (b) compares every raw array. |
| **S-3** | yes | Eight exact counters (`EXACT`), each asserted zero in `accounting_problems`. `attempt_ev_problems` raises in `joins` at `TS-S`. See V-4 for one shared dependency. |
| **S-4** | yes | The gates now record their last false-to-true change (`_rise`), on both modes. The new T-10 case is my first-read sequence. |
| **S-5** | yes | Null batteries run at `M_POWER` as exact binomial sums, plus a random-V battery. `K_NULL`, `K_POWER` and the three shifts are byte-identical at 9bda841 and e53e812. |
| **S-6 / R-d** | yes | Both `_request` and `modes_rules.request_amount` apply the quoted share only while `B` is below the buffer. `b_star` at the lenient end is now the buffer plus the cap, unless the share alone reaches the cap inside the buffer. Row 39 is labelled. |
| **S-7** | yes, as a convention | The declared coin roles refuse until `allow_declared_streams` is called with step 2's string. `main` calls it only after `step_problems(2)` is empty and step 0's file matches. The timing path and the identity never touch those roles. See V-2. |
| **S-8** | yes | On the costed coin, an untraded session is taken back out of `w_days` in a marked hook. The gross coin is unchanged (tested). |
| **S-9 / R-b** | yes (labels) | Both caps print, with R-b's note. Part F is not built yet, so the substance waits for it. |
| **S-10** | yes in the functions, **no in the file** | See V-1. |
| **S-11** | yes | Details below the table. |

**B-1 in detail.** `_Spec._trade_facts` now takes every fact from the engine side, never from the draw:

- the room the `room` hook handed;
- the cell's `w` and its risk schedule;
- the trade's change in the balance;
- the costed size and costs, recomputed from the room and the tier.

`loss_peak_cdf` is written out on the spec's side.

I re-ran my first-read checks against e53e812:

- **Funded side (`TS/std`, `RE`).** A biased `p_race`, at the first read's gross bias and at a bias of a few percent of the win probability, breaches the fairness check at both corners.
- **Evaluation side.** The biased run breaches fairness as well as the ceiling and the supremum.
- **Correct engine.** The unbiased run does not breach.
- **Tests.** The new T-9 tests break the engine from inside (`p_race`, costed payoff, slippage sign, peak inverse) and pass.

**B-2 in detail.**

- `CostedCoinDraw` draws peaks at `a = r'`, `b = w r'`, `n` per slot.
- `ri_read_set_costed` admits a costed `RI` cell only where `(w + 1) r' + stop-out costs <= D`. Here `r'` is part B's start-state mixed size. `RI`'s allowance has no ladder and the start room is not binding, so that is the largest size the draw can take. My derivation in the first read gives exactly this condition.
- Every runnable cell at rows 36 and 37 ran through `cell_rows` and the oracles clean, alongside rows 1, 3, 15, 17, 22, 39 and 41.
- One cell of every kind at all 45 mode-corners also ran clean.

**S-11 in detail.**

- The third cell must begin `rd05-step-recorded: <step> @ <hex sha> -- <text naming the file>`.
- The sha must be HEAD or an ancestor of it.
- A bare placeholder never matches.
- The new stem cannot trip `identity_tokens`' breach scan: its `TOKEN_LIKE` needs an `identity…holds/held` stem.

**N = 7,333.** The recount matches its parts:

- **Fairness:** one per running coin run, gross and costed.
- **Pass ceiling:** every evaluation run less the two close-only corners' runs and the six steady w = 1 boundary cells.
- **Supremum:** one per `TS` evaluation run.
- **Reference:** one.

It is under the declared maximum. It moved from the first build's count because:

- the w = 2 cells and the flips at boundary cells regained the ceiling;
- the costed `RI` read set moved from `r` to the realised `r'` plus costs, which admits a few more cells where the allowance binds below `r`.

## 2. New findings

**V-1 (blocker for step 2; one line). `main` drops part D's paired readings from the file it writes.**

*Where:* `scripts/modes_coin.py`.

1. `run` fills `acc["flip_pairs"]` with pass, sessions to a pass, any payout, first payout within 21 and 63, and net.
2. `joins` now also returns a `flip_pairs` key, with the per-attempt and per-journey net differences (331).
3. `main` does `acc.update(joins(summ))`, which replaces the first set with the second.

*Evidence.* On a toy run, assembled exactly as `main` assembles it, the section holds ten measures before the update and two after. `test_step2_pipeline_on_toys` checks the two dictionaries separately, never the assembled one.

*The failure it allows.* A twelve-hour step 2 writes a file without 10.2's paired pass, timing and first-payout rows. It would have to be run again.

*Remedy.*

- Extend rather than overwrite: either give `joins` a distinct internal key and concatenate, or `acc["flip_pairs"].extend(...)`.
- Add a test of `main`'s assembled sections on toy cells.

**V-2 (note). The stream guard is a convention, not a lock.**

- Any caller can pass the magic string to `allow_declared_streams`. Accepted: it stops accidents, which is what S-7 asked.
- The test restores the flag through `monkeypatch`, so it leaves nothing cleared.

**V-3 (note). The flip pairs' standard errors are approximations.** That is fine for a description, but the rows should say so.

- **`flip_E` per attempt.** `flip_net_pairs` gives the variance of a per-account `A + B Y` with an independent `Y` per account, divided by `n`. The estimator actually uses one funded mean from `nf` accounts. At `n = nf` the two agree to first order.
- **`flip_F`.** It divides by `min(n, nf)`.
- **The journeys.** These use the delta method, and their rows already say so.

**V-4 (note). The in-run fee check shares its fee code with the draw.** The spec and the draw both build their sizes and costs from `size_table` and `tier_cap_index`, so a defect inside `size_table` would pass both. Part B's `size()` computes the cost by independent code. Against the costed table it agrees on every start-state size of every mode-corner, stop and risk, with no mismatch (my check). Make that a T-8 test.

**V-5 (should-fix, the record). E-205's R-c does not say the read set includes costs.**

- E-205's text: "the gross coin's peak law on the costed outcome inside the read set".
- The build uses `(w + 1) r' + stop-out costs <= D`. That is the exact condition (first read, B-2), and stronger than `(w + 1) r <= D`.
- The lead's row should name the condition the code applies, so the readings and the code agree on paper.

**V-6 (note). Small leftovers.**

- `M_NULL` is now unused in T-9.
- `TOL` (the exact checks' relative tolerance) is a new build constant. It sits far above float error and far below any money difference, so it cannot be tuned to a stream. Cite it in 17.2's table.

## 3. Is `_trade_facts`' chance the right null at every corner?

Yes. The table walks the cases; my mechanical checks follow it.

| case | the chance used | why it is the zero-edge chance |
|---|---|---|
| Gross coin | `c / (c + w x risk)`, with `c = min(risk, room)` | `room` is what the hook handed the draw: the floor distance, cut by the daily limit (A-1) at the soft-limit plans, infinite at a close-only corner (and still cut by a limit there, N-3). It is the barrier race at zero drift with the closer exit, so the mean P&L is zero. |
| The flip | the same formula | `risk_at(d)` is the spec's own schedule. |
| `RI` | the same formula | `c` is cut by the intraday-trailed floor; inside the read set the floor cannot cut the trade's own path. |
| Costed coin | `1 / (1 + w)` at the recomputed size | The chosen size's whole stop-out (stop, entry and stop slippage, fees) lies inside the room. The floor and the daily limit are therefore never closer than the stop, and the bracket is driftless at `s` against `w s` ticks. That is the costed race 9.6 names. Costs come in at the exit, outside the race. A close-only corner gives the uncut size, which is right. |
| Outcome | read from the balance change | It must equal the win or the loss exactly, or a counter fires. |

**Mechanical checks.**

- The `trade_taken_unpredicted` and `loss_beyond_room` counters stayed at zero across the smokes.
- No false alarm appeared in about a thousand runs at the edge corners.

## 4. The builder's N-16 statement

- **What git shows.** `K_NULL`, `K_POWER`, `M_POWER` and the three shifts are identical at both commits. Cycle 1 changed only the null batteries' construction (S-5), on new `build_toys` keys.
- **What git cannot show.** "Fixed before T-9 first ran" is unverifiable from git: the first build is a single commit, and the pre-commit hook runs the fast tier.
- **Conclusion.** I accept it as the builder's statement, recorded in E-205's sense. A failure would be under the failure protocol.

## 5. The smoke-run disclosure

Nothing in it, as E-205 records it, is a reason to keep step 2 off the declared streams:

- **Outputs discarded; nothing chosen.** The run's outputs were discarded, and nothing in part C is chosen.
- **The coin's truth is analytic.**
- **The fairness check could not fire then.** Under the first build's oracle it was a martingale by construction.
- **The code changes since are this review's.** Every change came from B-1 to S-11's findings, not from anything the streams showed.

**Keep the declared seeds.** Moving to the reserved ones now would be the choice-after-a-look to avoid.

**One condition.** If the builder's own text says an exception or an oracle breach was seen on the declared streams:

- it stays on record under the failure protocol;
- the step-2 row names it;
- even then, it is not a reason to change the seeds.

## What I tried that found nothing

- **The copies.** The copies' new marked hooks: `after_window` takes `w_days`; `after_payouts` takes `cash` and `gross_paid`. All are guarded by `spec`. `recomposition_problems` passes in T-1.
- **B-1, B-2 and the identity specs.** The biased-engine checks, the costed-`RI` runs and the specs-at-Topstep identity, re-run as described in section 1.
- **Every RD-05 test file, alone with a time limit:** engine, oracles, runners, rules, terms, reading, draft. All pass.
- **Not run:** T-11, the heavy-marked identity test. Q-132 held `run.lock` during the first read.

## What I could not check

- The builder's smoke-run text itself.
- The step-2 run's real memory and time at full size.
- Part F's use of the registered cap (R-b), which waits for Q-138b.
