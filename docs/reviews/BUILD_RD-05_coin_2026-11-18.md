# Red team: RD-05's coin side as built (Q-138r), 2026-11-18

**Target.** `wt/wt-firms` at 9bda841 (worktree `%LOCALAPPDATA%\stage2-extended-wt\wt-firms`), against
`prereg/RD-05_firm_modes.md` (pinned in E-200) with E-200's readings R-1, R-2 and N-1 to N-5. Files read in full:
`extended/modes_engine.py`, `modes_oracles.py`, `modes_rules.py`, `modes_join.py`, `modes_terms.py`, `modes_steps.py`,
`scripts/modes_coin.py`, `scripts/modes_rules.py`, `scripts/modes_part_f.py`, `identity/modes_coin_identity.py`,
`identity/modes_identity.py`, `tests/test_rd05_{engine,oracles,runners,terms,identity}.py`; skimmed the rest of the
map. The brief offered a draft reading for the w = 2 boundary cells. I tested that reading. I did not adopt it.

**Seeds and figures.** This note holds no seed literal and no result number. Every synthetic check below ran on
seeds outside section 15's block, at 20,000 accounts or fewer. No bar was read and nothing was written outside this
note.

## Verdict

**The declaration stands with readings.** Four readings are needed (R-a to R-d below). Each applies the text's own
definitions, and none changes a declared rule.

**The build does not merge yet.** Two blockers:

- **B-1.** As built, the fairness oracle cannot fail on an engine with an edge.
- **B-2.** Every costed run at `RI`'s funded corners crashes.

Both are fixable on the branch. B-1 needs code only. B-2 needs one reading (R-c) and then code. The should-fix items
can land after the merge, but they must land before step 2 runs.

## Findings, by severity

### Blockers

**B-1 (CHANGES-A-CONCLUSION). The fairness check is computed from the draw's own `p` and `hit`, so it is a
martingale whatever the engine does.**

*Where:*

- `extended/modes_engine.py` 474-491 (`_fair_add` reads `last["p"]`, `last["hit"]`, `last["span"]`);
- 332-350 (`CoinDraw`: `hit = u < p`, with `p` the draw's own);
- 443-448 (`CostedCoinDraw`: `p` hard-set, `hit` from the same `u`);
- 348 (`peak_F` from the same `s` that drew the peak).

*Evidence.* S = sum of `(1{u < p} - p) x span` has mean zero for any `p`. A draw whose `p` is wrong therefore still
passes. I patched the engine's `p_race` to a biased win probability and ran the patched engine through `run_eval` and
`run_funded`.

- **Funded.** At `TS/std` and `RE` the biased draw made a mean gross gain per account of many standard errors, and
  `oracle_rows` raised nothing (fairness and accounting both held).
- **Evaluation.** At `TS` the fairness ratio |S| / bound stayed near zero. Only the pass ceiling and the supremum fired,
  and only because the bias was gross.

The in-run peak check is vacuous in the same way: `peak_F` equals `1 - s` exactly on every losing trade (checked).

T-9's "each oracle fires on a hand-broken engine" (`tests/test_rd05_oracles.py` 66-85) never runs a broken engine. It
builds a `fair` dict by hand.

*The failure it allows.* Any defect inside a draw passes every oracle on the funded side and at the boundary cells. On
the evaluation side it passes unless it is big enough to breach the ceiling or the supremum. Examples:

- a costed payoff booked with the wrong sign of slippage;
- a wrong `r_flip` race;
- a peak law that `peak_inverse` and `peak_survival` get wrong together.

That covers 25 of the 45 mode-corners, where no other statistical oracle exists. The funded map would then be printed
as zero-edge when it is not.

*Remedy (code only; the text already says it).* 9.6 defines "that chance" as `c / (c + w r)` at the trade's room, and
"1 if the target was reached" as the trade's outcome. So:

1. Compute `p`, the span and the outcome on the spec side, from engine facts: the room the `room` hook handed, the
   cell's `w` and its risk schedule, the trade's change in `B` plus its costs, and the contracts recomputed against the
   fee schedule. Never from `draw.last`.
2. For `RI`, compute `F(m)` from the peak the engine applied (the step in `peak_eq`), at the spec's own `a` and `b`.
3. Add T-9 tests that monkeypatch `p_race`, the costed payoff and the peak inverse, run the result through
   `run_eval` / `run_funded` and `oracle_rows`, and assert a breach.

The experiment is light: the two scratch checks above took seconds. A correct engine's S is unchanged by this fix, so
the false-alarm rate is unchanged.

**B-2 (MATERIAL). Costed runs at `RI`'s funded corners (Appendix M rows 36 and 37) crash with `KeyError: 'peak'`.**

*Where:* `modes_engine.py` 742-745 reads `last["peak"]`, which `CostedCoinDraw.last` (448-452) never sets. Meanwhile
`modes_rules.coin_cells` (436-437) marks these cells as runs.

*Evidence.* Step 0 lists dozens of such cells as runs. A one-cell run raises the error. A smoke of one cell of every
kind at every mode-corner (100 accounts, a seed outside the block) found this as the only crash.

*The failure it allows.* Step 2 would stop hours in, after the earlier mode-corners had run, with nothing written. A
naive fix (drop the trail on the costed coin) would silently change `RI`'s floor rule.

*What the text leaves open.* 9.2 gives the peak law for a path racing `-a` against `+b`, and the read set `(w+1) x
size <= D`. It does not say what these are on the costed coin. With costs charged at the exit (9.2's own convention),
a losing trade at `r' = r` can close below the floor its own peak raised whenever its stop-out costs are positive. The
gross guarantee therefore does not carry over.

*Remedy.* The lead's reading R-c, then code, then a T-8 and T-3 case on a costed `RI` cell.

### Should-fix (before step 2)

**S-1. The w = 2 boundary cells: the defect is real; the lead's draft reading is exact for the first identity but
incomplete.**

*Where:* declaration 7 item 8 and 9.6; `modes_rules.boundary_exact` 245-252; `scripts/modes_rules.py` 47-53, which
refuses.

*The defect.* The declared conditions admit six cells at `w = 2` (`L6` and `L11`, three `r` each). From 0 the balance
moves on the lattice `rZ`, so a pass lands at `T` (from `T - 2r`) or at `T + r` (from `T - r`). "Every pass at
exactly `T`" is therefore false on a correct engine. Failures stay exact: the floor is static, `r` divides `D`, and the
daily limit is at least `r`. No `w = 1.5` or `w = 3` cell meets the conditions.

*The draft reading.* "The pass balance lies in {T, T + r}" is exact for these six cells. But it leaves the third exact
identity, the boundary quantity `T 1{pass} - D 1{fail} + B 1{neither}` equal to the summed trade P&L
(`modes_oracles.py` 132), off by `r` on every pass at `T + r`. Taken literally, its two-sided test with zero would then
be biased below zero.

*Remedy.* R-a below.

**S-2. Identity 13.1 (a) proves nothing that the recomposition proof does not; (b) compares one array.**

*Where:* `identity/modes_coin_identity.py` 41-56 (`spec` None, `draw` None: the vendored `RandomDraw` on both sides,
textually the same code) and 59-71 (`pass_day` only).

*The failure it allows.* A hook that changes Topstep's behaviour, or a `CoinDraw` that drifts from `RandomDraw`,
passes (a). (a) can fail only if the unmarked text differs, and the recomposition proof already catches that.

*What I checked.* There is no such difference now. With the specs at Topstep's terms, these all equal the vendored
functions at `rules_from_ledger()`, every output array, at all 24 `(w, r)` (400 accounts):

- `EvalSpec(TS-S)`;
- `FundedSpec(TS/con)`;
- `FundedSpec(TS/std)` with A-16 off.

T-3 holds this at only two cells, and holds `TS/con` at none.

*Remedy.*

- Add to (a), on the `coin_identity` streams, the three spec-on comparisons above (A-16 off for `TS/std`) at all 24
  cells, every array. This is what 4.3's "with every switch at its Topstep setting ... bit for bit" asks.
- In (b), compare every array, not only `pass_day`.

**S-3. 9.6's "other exact checks" are mostly not built.**

*Where:* `modes_oracles.py` 137-188.

*What is there:* the request-bounds counter, and "no forfeiture without a ceiling".

*What is missing:*

- no trade larger than its room, its daily limit or (costed) its allowance;
- every costed fee equal to its schedule at its contracts;
- every net equal to its split;
- every forfeiture at the ceiling's threshold exactly;
- 9.5's per-attempt net equal to `propsim.attempt_ev` at `TS-S` in the run (T-9 checks it only on typed toy inputs).

*Remedy.* Add counters in the hooks (O(accounts)) and assert each one in `oracle_rows`.

**S-4. Part E's "last gate to open" uses the session each gate *first* held, which misattributes non-monotone gates.**

*Where:* `modes_engine.py` 600-618 and 800-802; `modes_reading.last_funded_gate` 93-100.

*Evidence.* At `TS`, a scripted account has four small winning days, so consistency holds at session 1. Then a day
large enough to raise the target, then a further day to the raised target. It passes with `raised` true, and
`last_gate` reads `base_target`. The consistency-raised target held last.

*Where it bites.* The same holds funded-side for the buffer and minimum, and for Builder's cycle share, which can hold,
lapse and hold again before a first payout. Gross steady cells cannot show it (equal wins). Flip and costed cells can.

*Remedy.* Keep, per gate, the session of its last false-to-true change (still O(accounts)). Add a T-10 case like the
one above.

**S-5. T-9's null batteries cannot fail at the declared tail.**

*Where:* `tests/test_rd05_oracles.py` 38 and 119-132.

*Evidence.* At `M_NULL` = 50 trades the Freedman bound sits close to the largest possible |S|. A breach is then
astronomically rare, so the test fails only if the bound is off by about a factor of two. The batteries also hold `p`
fixed, so `V` is never random. That is the one place the plug-in form of N-1 could leak.

*Remedy.*

- Run the null batteries at `M_POWER` trades, drawing S exactly as a binomial sum (cheap).
- Add a battery whose per-trade `p` varies with a simulated room, so `V` is random.

The declared K and shifts stay as committed (R-2).

**S-6. U-17's lenient end extends past "inside the buffer". This is a free choice that moves `b*` and `r_flip` at
`PRO`'s lenient corner (row 39).**

*Where:* `modes_engine.py` 857-859 and `modes_rules.py` 143-144 and 168-176, which take
`max(B - buffer, share x B)` at every balance.

*Text against code.* 5.1 says "a request inside the buffer at the share the record's note quotes". For balances from
the buffer up to `buffer / (1 - share)`, the code lets the request exceed `B - buffer`. So the lenient `b*` is
`cap / share`, not `buffer + cap`. The literal reading makes the request jump down as the buffer clears. The
code's envelope avoids that jump, but no text supports it.

*Remedy.* The lead rules (R-d) and labels row 39.

**S-7. The declared streams are reachable from any caller, and the disclosed smoke run used them.**

*Where:* `modes_engine.stream` 913-915; `scripts/modes_coin.run_cell` 67-70 and `run`'s default `seeds=None` (230).

*Judgement on the smoke run.* It breaks section 15's sentence "No run on the declared streams happens before step 2".
It does not, by itself, bias anything that matters here:

- the coin's truth is analytic;
- nothing in part C is picked, passed or carried;
- under B-1 the fairness check could not have breached, so the run could reveal little.

The one channel that matters is tuning: an oracle or engine change made because of what that run printed. Remedy for
the smoke run:

1. The builder states which keys, cells and account counts, and whether any oracle result or exception was seen.
2. The builder attests that no code change was conditioned on it.
3. The lead records both in the row that takes the build.
4. If anything breached, it stays on record under the failure protocol.
5. Do **not** move to the reserved seeds: a seed change after a look is the worse act.

*Remedy for the code.* Make `stream()` refuse the `coin_eval`, `coin_funded` and `coin_peak` roles unless step 2's
`main` has cleared `step_problems(2)`. A module flag set only there is enough.

**S-8. On the costed coin, a stood-aside (no-trade) session counts as a cycle day.**

*Where:* the vendored `lk = alive & alive_at_start` (`modes_engine.py` 237-243) adds to `w_days` whether or not the
account traded. Builder's `days_ok` (846) and `TS/con`'s minimum days read `w_days`.

*The failure it allows.* A costed account near its floor accrues "trading days in the cycle" without trading. The
error is lenient and probably small, since such an account is far from its buffer.

*Remedy.* Count days traded in the hook and feed that count to the Builder and `TS/con` day gates on the costed coin.
Do not edit the copied lines; correct the count in a marked hook.

**S-9. The headroom defect is real, but it is part F's, not the coin's.**

*Where:* `modes_terms.registered_stand_aside` 1062-1078 reads `gate.campaign.headroom` from
`vendor/stage2/config/fv3_corrected_portfolio.yaml` (line 192), which is the full allowance. Separately,
`sizing.DEFAULT_HEADROOM_FRAC` (D-117) is a fraction below it.

*Text against code.* 8 labels D-117's fraction "the registered designs' operating rule". 2.6 and 4.7 item 3 promise a
flip trade "never at the full allowance". Both are false if the registered cap is the full allowance.

*Coin side.* Untouched. The gross coin has no contracts, the costed coin is steady and capped at the allowance by 9.2,
and part B prints both caps.

*Remedy (before part F).*

1. Confirm the cap U1's P-14 and P-16 replays actually use (`user_journey.py`'s sizing rule, not only the gate config).
2. If it is the full allowance, record the reading R-b.

**S-10. Part D's and part E's coin readings fall short of 10.2 and 4.7 item 5.**

*Where:* `scripts/modes_coin.py` 217-227 and 113-118.

*What is short:*

- The flip pairs give pass, "sessions occupied", any payout and cash. They do not give sessions to a pass (mean and
  p50), first payout, or the per-attempt and per-journey nets with paired standard errors.
- "Evaluations bought per 21 sessions" is not computed.
- `size_spread` is the mean of each account's largest size, not a spread.

*Remedy.* Build these before step 2. They are cheap from the existing counters and the renewal.

**S-11. Each step's gate on its predecessor is matched by text.**

*Where:* `modes_steps.recorded` 157-162 accepts any row that names the result file and "RD-05". A row merely
mentioning `results/modes_rules.csv` would unlock step 1.

*Remedy.* Require a positional token in the third cell (E-104's form), as the identity waits already do.

### Notes

**On the copy and its hooks.**

- **N-1. The copy is verbatim at the statement level.** The marked lines removed, the vendored functions and the copies
  differ only in the signature's line wrap and in trailing blank lines (`diff` checked). The recomposition proof is
  AST-level, so it is right to pass.
- **N-2. The hooks are inert with `spec` None.** Every hook is behind `if spec is not None`. The unguarded marked lines
  (`check_vendored_sources()` and the unused `out` dict) change no state.
- **N-3. `room` returns infinity at a close-only corner and ignores the daily limit.** This is inert at the declared
  corners, since U-27's and U-28's lenient ends coincide. It would be wrong at a future corner that had both.

**The builder's interpretations, item by item.**

- **N-4. `k_F` counting follows the text and the engine.** Elapsed sessions with the first trade at session 0 give a
  wait plus one, and match `first_ok`'s `d >= first_trade + wait`. Nothing here is free.
- **N-5. A-16 on `L6/std` comes through U-13, not 4.3's list.** 4.3 lists "TS/std and the Labs 5 Winning Days maps".
  `L6/std` is Topstep's Standard path by U-13, so carrying the exclusion follows the text. Label it.
- **N-6. Builder's buffer is left after every request, not only the first.** This is A-8's general My Funded Futures
  form, so it is not a free choice in effect. Label it.
- **N-7. The "fails" convention ("a day above `c T` fails it") is a free choice.** It moves only the labelled
  counterfactual rows, since every plan here records `extends`. Label it as the builder's reading. Separately, the
  `extends` semantics for `TS` and the Labs plans are hard-set, not read from a key.
- **N-8. Part B states each funded tier at its band's lower edge.** That is the smallest room in the band, the
  conservative choice. Label it.
- **N-9. The zero-contract rule and the stand-aside share.** A zero-contract trade is no trade, counted toward
  inactivity. That is the only coherent reading of 9.2. The registered `min_risk_share` is nil in the config, so
  D-212's share test is vacuous: only n of at least 1 and the cost-floor ticks bind. Every costed stop clears the
  cost floor. Say so in step 0's rows.

**Other checks.**

- **N-10. Q-05 has no `identity-holds:` token, but that is not a defect.** 13.1 requires every shared identity to be
  re-held after the record's merge anyway, and Q-104 (RD-01's `firms_identity`) is in the same state. The lead's
  re-holding rows will carry the tokens. Q-80, Q-93 and Q-101 will also go stale at the merge (`config/` is in every
  cover).
- **N-11. The stated-fewest check is tautological at `PRO1` and `B20`.** `stated_fewest` is set to the same record
  field as `min_days`. Parse the firm's own fewest-days sentence instead, where the record has one.
- **N-12. 17.2's literal scan covers the adapters only.** `modes_oracles.HALF` equals a rule value and would trip it.
  Widen the scan to every build file, for hygiene.
- **N-13. Step 2 compares step 0's file by count only.** `modes_coin.main` checks the number of runs and N, not the
  cell list. Compare the `coin_cells` rows themselves.
- **N-14. `--measure` runs before the refusals and without a lock check.** The timing seed is allowed (15, 18), but at
  50,000 accounts it is compute-heavy. Take `run.lock` for it.
- **N-15. The power assertion's false-failure risk.** At K = 200 and power 0.999, R-2's assertion needs at least 199
  hits. A correct build fails it about 2 % of the time per type. The seeds are fixed, so this is a one-shot property,
  not a rerun risk.
- **N-16. R-2's "committed before T-9 first runs" cannot be verified.** The branch has a single build commit, and the
  pre-commit hook runs the fast tier. Ask the builder whether any K or shift changed after a T-9 run.
- **N-17. Two labels are applied by the menu, not carried on step 2's rows.** "Allowance and scaling not applied" and
  "no calendar: no news rule" sit in `modes_reading` (137-138). 2.6 asks for every gross row to carry them.
- **N-18. The supremum oracle reads the largest no-DLL `sup_p_pass`, the finest grid's.** That is a grid lower
  bound on the true supremum. Harmless at the corrected width, but say so.

## The readings proposed (each applies the text; none changes a declared rule)

- **R-a (S-1).** 7 item 8 defines the boundary cells as those "at which every pass ends at exactly `T` and every
  failure at exactly `-D`". The listed conditions are a derivation that falls short. Apply the definition: a cell is a
  boundary cell only if the conditions hold and the lattice lands every pass at `T` (`boundary_exact`, which the build
  already has).
  - The six `w = 2` cells are not boundary cells. They carry the ordinary pass-ceiling check, which is valid there
    because the ceiling is not attained.
  - N rises by six and stays under the declared maximum.
  - *Preferred:* this keeps the pass ceiling's power on six cells and adds no new identity.
  - *If the lead keeps the draft ({T, T + r})*, it must also replace `T 1{pass}` in the boundary quantity by the
    realised pass balance, so the third identity again equals the summed P&L.
- **R-b (S-9).** The flip's contract cap is the registered rule's own, read from the rule (2.6's mechanism, kept). The
  sentences "never at the full allowance" (2.6) and "No trade is ever sized at the full allowance" (4.7 item 3) are
  read as withdrawn where that rule's headroom is the full allowance. Tier 1's "maximum size into news" remains
  enforced by the news rule (no entry inside a verified window; flat at its start). The full-allowance share stays an
  exposure. Part F only.
- **R-c (B-2).** On the costed coin at `RI`:
  - the losing-trade peak law is 9.2's, at `a = r'` and `b = w r'`;
  - equity at the peak excludes the exit's costs (9.2: costs at the exit);
  - the read set is `(w + 1) r' + stop-out costs <= D`, at the cell's largest `r'`, which is part B's size for `r` at
    `s`;
  - cells outside it are printed "not read: a trade can be stopped by the floor its own peak raised".
- **R-d (S-6).** U-17's lenient end has two readings: literal (the quoted share only while `B` is below the buffer) or
  envelope (the code's `max`). The lead names one and labels row 39. I lean literal, since 5.1's words are "inside the
  buffer".

## What I tried that found nothing

- **The copy.** Diffed against `vendor/stage2/vendor/propsim/propsim.py` with the marked lines stripped; it differs in
  signature wrapping only. Every hook statement is guarded by `if spec is not None`.
- **The base coin at `TS`.** Specs on against the vendored functions at `rules_from_ledger()`, all 24 cells, every
  array, for the evaluation, `TS/con`, and `TS/std` with A-16 off: equal (S-2's check).
- **Crashes.** One run of every (mode-corner, policy, coin) kind through `cell_rows` and the oracles: clean except
  B-2's two.
- **Seeds.** Grep of the build and the tests: the declared coin streams are drawn only in `scripts/modes_coin.py`
  under `seeds=None`. No test draws them. Item (a) uses `coin_identity`; the tests use `build_toys`; the timing uses
  0. T-13 holds the literals to `modes_terms.py`.
- **The law and the formulas, re-derived:**
  - Freedman's bound and its inversion;
  - the Clopper-Pearson limits;
  - the pass ceiling with expired and censored accounts (it holds, since every "neither" balance is at least `-D`);
  - the losing-trade peak law and its inverse, including gambler's-ruin exactness on the integer lattice, so T-8's
    random-walk test can fail on a swapped law;
  - `b*` at both U-25 ends, against the request function.
- **The arithmetic in `modes_join`, re-derived:**
  - the renewal `R * f_pass * f_pay`;
  - the stacking decomposition (prefix ending in the second-to-last breach; suffix of at most 20 sessions after it);
  - Wald's means;
  - the purchase-limit sum;
  - `TS-N`'s re-pricing on `TS-S`'s runs;
  - the join's corner pairing.
- **Refusals.** Steps 3 to 5 refuse with NOT BUILT before any read. Step 0 refuses on the boundary defect. No module on
  the coin side imports the bar reader (`modes_steps` imports `reader` for the pin hash only).
- **Tests.** Each `test_rd05_*` file was run alone with a time limit (engine, oracles, terms, rules, runners, reading,
  draft): all pass. T-11 (`test_rd05_identity.py`, marked heavy) was not run, while `run.lock` was held by Q-132.

## What I could not check

- The content of the builder's smoke run on the declared streams (S-7).
- Whether U1's replays size at the gate config's headroom (S-9).
- The record at the merged commit. The keys were checked at this branch's record only.
- The order of R-2's commit against T-9's first run (N-16).
- Whether stage one's supremum file was solved at the Combine terms the ledger now holds.

## Experiments specified, not run

1. **B-1's regression tests.** Light, seconds each: a biased `p_race`, a biased costed payoff and a wrong peak inverse,
   each run through `run_eval` / `run_funded` and `oracle_rows` on `build_toys` keys, each asserting a breach.
2. **A whole-grid smoke before step 2's measurement.** Every runnable cell of step 0's list, at 100 accounts, on a seed
   outside the block, through `cell_rows` and the joins.
   - Data: none; no bar.
   - Memory: well under 0.5 GB.
   - Compute: about the cost of step 2 divided by 500, roughly under an hour.
   - Run it under `run.lock`, since it is CPU-bound.
   - It would have found B-2, and it would catch any similar crash before the 12-hour run.
