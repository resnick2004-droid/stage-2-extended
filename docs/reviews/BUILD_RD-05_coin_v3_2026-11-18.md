# Red team, third read: RD-05's coin side, V-1 to V-6 (Q-138r3), 2026-11-18

**What I read.** The diff `wt/wt-firms` e53e812..b049dfd, which changes six files. I read it under E-207's rule:

- **V-1 was blocking**, so I re-read its fix in full: the code, its test, and `main`'s actual path.
- **V-3, V-4 and V-6 are minor**, so I checked only their diffs.
- **V-2 and V-5 have no code change.** V-2 was accepted as it stood. V-5 is a matter for the lead's decision row.

**How I checked.**

- Synthetic checks only, on seeds outside section 15's block.
- No bar was read.
- Nothing was written except this note.
- This note contains no seed literal and no result number.

## Verdict

**Merge the coin side.**

- No blocking finding remains.
- One minor finding is new (W-1). It needs a one-constant fix or a recorded reading before step 2. It does not block the merge.

## Findings

**V-1 — blocking — closed.**

- **The fix.** `scripts/modes_coin.py` adds `assemble`, which extends every section `run` and `joins` share instead of replacing it. `main` now calls `assemble(acc)` (line 512) where it used to call `acc.update(joins(summ))`. No other `update` of `acc` remains.
- **The test.** `test_v1_main_assembles_every_paired_measure` runs `run` and then `assemble` on toy cells. It asserts two things: that the ten paired measures are present before assembly, and that they are all still present afterwards beside the joined nets. It would fail on the old replace semantics.
- **My check of `main`'s actual path.** I reproduced `main`'s whole sequence: `run`, `assemble`, then the frame concatenation that `main` writes. The written `flip_pairs` section keeps all ten of `run`'s measures. It also carries `net_per_attempt` and `net_per_journey` for both `flip_E` and `flip_F`.
- **One small gap in the test.** It checks the two net measures by name, not by flip. My check covers both flips. Asserting both `(flip_E, ...)` and `(flip_F, ...)` pairs in the test would make that explicit. This is optional.

**V-3 — minor — closed.** Each flip-net row now carries a note naming its standard error as approximate, with the reason (`SE_NOTES`). The V-1 test asserts the notes are present.

**V-4 — minor — closed.** `test_v4_part_b_costs_agree_with_size_table` checks two independent pieces of code against each other: part B's cost code (`modes_rules.size`) and the costed coin's `size_table`.

- It covers every start-state size of every mode-corner, costed stop and risk.
- It checks the same contracts, the same realised risk and the same stop-out costs.
- It asserts that every cell was either compared or explicitly skipped as a zero size.

**V-6 — minor — closed, but see W-1.** `M_NULL` is removed. `TOL` is now read from `DECLARED["exact.tol"]`, with a citation. The rest of the diff touches nothing else.

**W-1 — minor — new.** The citation for the exact-check tolerance names 9.6, but its value is looser than 9.6 states.

- **What the text says.** 9.6 states both its exact identities and its "other exact checks" as holding "to 1e-9".
- **What the build does.** `accounting_problems` uses 1e-9, scaled to the run's money. The counters (`EXACT`) use a relative tolerance 100 times looser, and that looser value is the one `DECLARED["exact.tol"]` now cites to 9.6.
- **Why it matters little.** No money difference that matters fits under either tolerance.
- **Evidence the declared value works.** With `TOL` set to 1e-9, one cell of every kind at all 45 mode-corners ran through the oracles clean. The counters compare values computed by identical arithmetic, so they are exact up to float rounding.
- **Remedy.** Set `exact.tol` to 9.6's 1e-9. Otherwise, the lead records the looser value as a reading.

**V-2 — minor — accepted, no change.** The stream guard is a convention, not a lock.

**V-5 — minor — open, the lead's.** E-205's R-c should name the read set the code applies: `(w + 1) r' + stop-out costs <= D`.

## Tests run

Each changed test file was run alone, with a time limit: `test_rd05_runners`, `test_rd05_engine`, `test_rd05_oracles` and `test_rd05_terms`. All pass.

## What I could not check

Nothing new beyond the second read's list:

- the builder's own text describing the smoke run;
- step 2's real time and memory at full size;
- part F's use of the registered cap.
