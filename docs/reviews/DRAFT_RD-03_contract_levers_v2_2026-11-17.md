# Red team: RD-03's second text -- an addendum to the first read (Q-116r2, 2026-11-17)

**Target.** `prereg/DRAFT_RD-03_contract_levers.md` at 4f5c0aa on `wt/wt-payout`. Its LF sha256 was re-hashed from the
blob and matches E-147's `1dc9365e1b3b2a008a0af851aa6c932e580a55bad77d33b79f4d7ce05a84d603`. I diffed it against
153f453 (`git diff 153f453 4f5c0aa -- prereg/`, 785 lines; only that declaration changes under `prereg/`).

**Read.**
- E-146 (master): the lead's ruling on M1 and the adoption of the rest.
- The whole diff, and the second text's 0.1, 6, 9.1, 10.1, 13 to 15 and Appendix C in full.
- My first read (`docs/reviews/DRAFT_RD-03_contract_levers_2026-11-17.md`).
- Vendored code only: `scripts/state_policy_dp.py`'s `find_rent`, `solve_rent`, `solve_rent_ce` and `cycle_rate`;
  `cell`'s link between the funded and Combine solves; `state_policy.py`'s method list (for a fixed-policy
  evaluator); `extended/identity_cover.py` (`BASE`, `cover`, `imports`).

No bar, no result file, no judged-block read. Seeds: none of the draft's literals appear here; they are named by role.
My one small check is an exact chain with no randomness.

---

## Verdict: pin after the listed changes (text only; the lead's diff check, then the gatekeeper)

Every finding of the first read is answered, as asked or as E-146 adopted it.

The changes add two defects. Both change a declared rule and are fixed in a line or a paragraph:
- **V1.** M2's two new input checks, as worded, are either vacuous or fail by construction. My first read's wording of
  them was imprecise, and the draft carried that over.
- **V2.** Step 1 of the run still lets stage 0's identity stop every cell, against E-146's ruling.

Five minors follow. Once V1, V2 and the minors are answered, the lead can check the diff against 4f5c0aa. If it stays
inside the named hunks, the text goes to the gatekeeper, T-0 and the pin; no further red-team read is needed.

---

## 1. The first read's findings against the second text

| finding | asked / adopted (E-146) | the second text | judgement |
|---|---|---|---|
| M1 | stage 0 decides nothing; every cell runs | header, 2.1, 2.4, 6, 7.2, 11, 13, 15 step 2, T-12 ("no code path from them to any cell, flag or order") | **answered**, except 15 step 1 (V2) |
| M2 | label, or the registered policy's forward pass at its own rate, with two checks | the registered policy evaluated at each base's per-R edges, `lambda_pi = (p W - F_acc) / (D + p T)`; D-666's re-solve kept beside, labelled; two refusing checks at 1e-6 | **the route is right** (it is Stage 2's own `cycle_rate`); **the checks are not** (V1); the rungs are unspecified (V1, item 4) |
| M3 | house money at both expiry readings | 8 house cells; U-1, 9.1 item 7, 9.2, 9.3, T-5, flags | **answered** |
| M4 | delete 9.1 item 3 or admit its constants | deleted, with the toy and in-run equalities named | **answered**, but T-8 still cites "items 1 to 3" (v1) |
| m1 | run the Focused Trader models, or name the gap | gap named on every house-money and `naf` row and on the menu (100 replays not run) | **enough under E-146** (section 2 below), with a sharper reason owed |
| m2 | a counted reading, or the optimistic label | a second Focused Trader reading on the Back2Funded cells with each reactivation counted (A-1 (e), T-2), both labelled | **answered**; the purchase budget stays optimistic only, labelled (acceptable: a self-imposed restraint) |
| m3 | the verified timing, or the pessimism named | bought on the evening of the breach close, trading the next session, labelled "bought before the 17:00 CT reopening" | **answered**, with two consequences to state (v3) |
| m4 | correct the account-stacking sentence | corrected against D-495 (2)-(3), with 10305426's words | **answered** |
| m5 | the guard row on beside rows | full guard row; gate entry "the gate at 0 %" | **answered** |
| m6 | the frontier without house money | printed without, and with them labelled | **answered in 10.1**; T-14 not updated though 0.1 says it is (v2) |
| m7 | four assertions | resets off (T-4, T-15), activation on activation (T-4), the sentinel never loaded (14.2, T-4), T-9 reworded | **answered** |
| m8 | declare the covers | `BASE` plus the script's import closure under Q-111's rule; T-0 holds it | **answered**; `BASE` and `imports()` exist as cited (`extended/identity_cover.py` 81-82, 326) |
| n1, n2, n4, n6 | notes | 6.5; 2.1 and A-1; U-7 and section 8; 4.2 | **answered** |
| n5 | note | G-9 | answered; one citation to sharpen (v5) |

**Counts, re-added.**
- New cells: 4 + 16 + 8 + 2 = 30; replays: 32 with the two references.
- Ladder and placement: 4 x 30 = 120.
- Focused Trader: 10 x 20 = 200, plus 40 for the counted reading.
- Beside in all: 360, plus 28 reference checks. Gates: 30.
- Not run: 10 x 10 = 100.
- The header, 7.2, 13 and 15 agree.

---

## 2. Is naming the Focused Trader gap enough under E-007 (e)?

**Procedurally, yes.** E-007 (e) asks for the binding Focused Trader models beside every user reading. E-146, a later
row, adopted "the Focused Trader models beside every lever cell **or the gap named**". RD-02 set the same precedent: it
named its gap where the class made the models unreadable.

**Substantively, the two omissions differ, and the text should say how.**

- **`naf`: the omission loses no information, and the text can say exactly why.**
  - With U1's unbound bankroll, a `naf` cell's path equals its base's: same trades, same purchases, same funded
    losses. Only the fee amounts differ.
  - The Focused Trader models count purchases and funded losses, not dollars. So under every model the `naf` cell is
    placed exactly when its base is, and closes exactly what its base closes.
  - Its reading is therefore the base's (Q-44's per-start rows) with the fees re-priced.
  - The row should say so ("identical to the base's under every model, fees aside"), not just "not read".
- **House money: the omission loses a reading, but not one that could flatter the lever.**
  - Before its trigger the cell equals its base, placements included.
  - After it, the cell buys no more (`house_stop`) or fewer (`house_zero`) evaluations, while its funded accounts trade
    and are lost exactly as the base's. So its purchase measure is at most the base's and its loss measure equal.
  - The cell can therefore be placed no sooner than its base. Under the models, the paired reading would, if anything,
    move in house money's favour.
  - Leaving it unread cannot make house money look better than it is. It is already labelled gaming P and never
    ordered.
  - The reason in 4.5 ("withholds purchases after it") is the right one. State the conclusion: "placed no sooner than
    its base; the gap cannot flatter this lever".

---

## 3. Findings on the second text

### V1 (MATERIAL; text). M2's two input checks, as worded, are vacuous or fail by construction

**Where.** 6.2, "The read's two checks on the inputs" (lines 627-631 of the second text); T-12; 6.1 (a).

**Evidence.**

- **The rate is Stage 2's own definition.** The new route computes `lambda_pi = (p W - F_acc) / (D + p T)` from the
  registered policy's forward summaries at a base's edges. That is exactly Stage 2's `cycle_rate`
  (`scripts/state_policy_dp.py` 244-250: cash `p (W - activation) - subscription - accrued`; days `D + p T`).
- **Check (i)** asks that `W - lambda_pi x T` equal "the funded table's fresh value under the registered policy at the
  rent `lambda_pi`, to 1e-6". The vendored solver has no fixed-policy backward evaluator: `FundedDP` and `CombineDP`
  offer only `solve`, which optimises, and `forward`. So:
  - if the right side is computed with `solve` at `lambda_pi`, it is the optimal value at the base's edges. That
    differs from the registered policy's value wherever the registered policy is not optimal there, which is the
    reason M2 exists. The check fails by construction;
  - if it is computed from the same forward summaries, it is `W - lambda_pi T` against itself, and checks nothing;
  - it is a real check only if the build writes a fixed-policy backward evaluation in `extended/`. That is new code
    the text does not name.
- **Check (ii)** asks that "the evaluation's fresh value under that policy at `lambda_pi` is zero, to 1e-6". Three
  problems:
  - **The wrong quantity.** Stage 2's fixed point sets the attempt's worth **net of its first subscription** to zero
    (`csol.value - rules.subscription`; `find_rent`, `solve_rent` 276).
  - **The horizon.** The Combine's backward pass prices a pass at day t with the funded value over the days left
    (`cell`: `fsol.fresh_value[1:T + 1] - activation`), while `lambda_pi` uses the full-horizon `W` and `T`. So even a
    correct fixed-policy evaluation misses zero by the horizon's truncation, not by 1e-6.
  - **The optimum.** With the vendored optimising `solve` it misses by the optimum's margin.
  - My exact toy chain shows both (Appendix A3):
    - at `lambda_pi`, the fixed policy's backward attempt value, net of the first subscription, is -0.025;
    - the optimal one is +27.87;
    - check (i) with a hand-written fixed-policy evaluator holds exactly.
- **For (c),** the text applies "the same two at its lambda\*, to the fixed point's tolerance". (c)'s exported table is
  the **tie-broken** solve at the **exact** tables' lambda\*. Its attempt value at lambda\* is below zero by the
  tie-breaks' price, "a few dollars an attempt" (`solve_rent`'s docstring; D-325, D-329). So (ii) on (c) fails unless
  it is read on the exact solve, or allows that price.
- **I own part of this.** My first read proposed these two checks for the re-solve route, where (i) is a real
  forward-against-backward comparison of one solution. I worded (ii) loosely ("the fixed point's tolerance"). The
  second text carried both into a route where they do not apply.

**The failure it allows.**
- A refusing check that fails by construction blanks stage 0's whole view ("stage 0 writes nothing but the failure's
  lines").
- Or the builder quietly reinterprets a declared check.
- Or a vacuous check certifies inputs it never tested.
- No cell is affected, since stage 0 decides nothing.

**Remedy (6.2, 6.1 (a), A-5, T-12).**

1. Take `lambda_pi` from the vendored `cycle_rate`, imported, never restated. Say that it is the registered policy's
   long-run cash per slot-day at the base's edges (a renewal rate on the forward summaries), not a fixed point of a
   backward solve.
2. Replace (a)'s two checks with checks on the evaluator, which is what can go wrong:
   - **(a-1)** At FV3-C's single edge, the evaluator applied to the registered solve's own `Solution` (6.4 item 1)
     reproduces that solve's own forward summaries, and its `cycle_rate` the tie-broken rate Stage 2 recorded beside
     lambda\*. Use `state_policy_v12_noclose.csv`'s rent rounds where that file holds them, else the identity solve's
     own forward, to 1e-9.
   - **(a-2)** At each base's per-R edges, the evaluator applied to (c)'s Standard `Solution` reproduces (c)'s own
     forward summaries (`u_size_fit.csv`'s `reading` rows, already 6.4 item 2's identity), to 1e-9. This proves the
     evaluator is the vendored `forward` on the per-R classes, policy aside.
3. Keep, for (c) only:
   - **(c-i)** `W - lambda* T` from the forward equals the funded solve's `fresh_value` at day 0, to 1e-6: one
     solution, forward against backward;
   - **(c-ii)** on the **exact** (not tie-broken) solve at lambda\*, the attempt's value net of its first subscription
     lies inside the rent search's recorded bracket. The tie-broken table's value is printed beside with its
     tie-break price.
4. Say which rungs the evaluator's per-R classes carry: **each base's own** (its stops, shares and per-R availability,
   as D-666 builds them), since the cells trade the base's offers. The registered policy's arrays index the shared
   balance grid and v12's menu. Also say that (a) is the registered **DP policy whose banded export** the cells trade,
   not the export itself. The existing stop-and-report clause covers a menu that does not align.
5. T-12: each new check fires on a hand-broken toy, and on a toy where the fixed policy is not optimal, check (i)'s
   optimising form would fail. That shows why the evaluator, not `solve`, is used.

### V2 (MATERIAL; one line). Step 1 lets stage 0's identity stop every cell, against E-146 and 6.4

**Where.** 15, step 1 (lines 1107-1108): "the identities: `identity/cl_fit_identity.py` and `identity/cl_identity.py`
... Any failure stops the reading". Also 15's waits, "steps 1 and 2 recorded" (1140), and 11, "the reading (or stage 0)
stops" (964).

**Evidence.** 6.4's new sentence (635) says that a failure of stage 0's identity "stops stage 0's view; it does not
stop the reading's cells, which wait only on their own identities (9.1)". E-146 rules that stage 0 decides nothing.
Step 1 runs both identities and stops the reading on either. So a failure in the solver machinery, which no cell uses,
would halt all 30 cells.

**The failure it allows.** A solver identity failure, say a nudged `u_size_fit.csv` row or the absent D-559 files
handled differently, vetoes the whole reading. That is stage 0 deciding after all.

**Remedy.**
- Step 1: "a failure of `cl_identity` stops the reading; a failure of `cl_fit_identity` stops stage 0 alone (6.4)".
- The waits: "step 1's `cl_identity` held; step 2 recorded, whatever its outcome".
- 11's bullet split the same way.

### MINOR

**v1. T-8 still runs "9.1 items 1 to 3"** (line 1077); item 3 is deleted. Make it "items 1 and 2".

**v2. T-14 was not updated for m6.** 0.1 lists T-14 among m6's places, but T-14 (1083) still asserts only the guard
row, the label and the flags. Add: "the frontier printed without the house-money cells, and the version with them
labelled 'gaming P'".

**v3. m3's timing has two consequences the text should state** (2.1, U-3, T-2). Both follow from my own m3 remedy.

- (a) **The lost account must leave the funded list at the reactivation.** Under the engine's `next_session`
  convention, a breached account stays in `funded` until the next evening (`lockstep.py` 2061-2064). If A-1 adds the
  reactivated account that same evening without removing the lost one, then until the next evening:
  - `len(funded)` counts both, and the joint-cap test (`len(running) + len(funded) + len(queue)`, 2116) counts both;
  - that idles one seat for a session, or shows six funded entries.
  2.1 says the reactivated account "takes the lost account's seat". It should also say that the lost account moves to
  the finished list at that moment. T-2 should assert that `len(funded)` never exceeds five and that the joint-cap
  count is unchanged by the swap.
- (b) **The pair now mixes the lever with a convention.** The base refills the freed seat a session later under the
  engine's pessimistic `next_session` convention (`xfa_seat_frees_at` unverified). The cell refills it at the verified
  Back2Funded timing. So up to one session of each paired Back2Funded difference is the convention, not the lever.
  Label it on every Back2Funded row: "the base refills a session later by the engine's convention".

**v4. m1's reason, sharpened as section 2 says.**
- `naf`: "identical to its base's under every model, fees aside", with its derivation from Q-44's rows named.
- House money: "placed no sooner than its base; the gap cannot flatter this lever".

**v5. G-9's citation.** The sentence that a failed (MLL) Combine "does not cancel -- it keeps rebilling" is 8284121 as
quoted in the record's `reset_rebill_push` note (deb45ad 3390-3392). It is not in `combine_cancellation`, whose quote
covers active Combines. Cite both.

### NOTE

- **n1. The purchase budget stays optimistic for reactivations.** Only the Focused Trader measure gets the counted
  reading; the budget does not. That is acceptable: the budget is the bases' self-imposed restraint, not a firm rule,
  and the row is labelled. Appendix C item 9 states it.
- **n2. The convention's validity window.** U-3 places a breached account's closure "at the end of the day"
  (`lockstep.py` 2059-2061, D-339's re-read), so "bought before the 17:00 CT reopening" leaves a short window after the
  closure. The label carries it; no change is needed.

---

## 4. Appendix C: the drafter's 25 choices

| # | choice | judgement |
|---|---|---|
| 1 | G-B weighs `W - lambda x T` against $599 | right as the solver's view (the exact policy-improvement test for the long-run rent); beside only |
| 2 | stage 0 decides nothing | right (E-146); 15 step 1 must follow (V2) |
| 3 | inputs from the registered policy's forward pass at its own rate | right; its checks (V1) and its rungs (V1 item 4) to fix |
| 4 | G-N on payouts per fee dollar, the table fixed | right as a view; it is a mean-fee measure, not P, and the text says so |
| 5 | `naf` replayed | right: an exact re-pricing, nearly free |
| 6 | reactivation on the breach evening, trading next session | right by the two verified keys; the swap and the convention mix to state (v3) |
| 7 | a requested, unpaid payout counts as taken | a conservative single reading, labelled; fine |
| 8 | the closures that are not eligible | fine: none is the designs' "rule violation"; the Focused Trader Plan bars it in words |
| 9 | reactivations not purchases, with a counted Focused Trader reading | fine; the budget optimistic and labelled (n1) |
| 10 | the entry tier | follows from verified rules |
| 11 | C in {5, 7} | contract arithmetic; D-651's influence disclosed |
| 12 | banking on and off | fine |
| 13 | `exp_30` from the pass, at or below the cap, neither the base | fine: the strict reading, both run |
| 14 | house money at both expiry readings | right (M3) |
| 15 | the trigger at the first close above zero | fixed by CHARTER's "ahead" |
| 16 | cancel only at the last close before a rebill | right under either cancellation reading |
| 17 | budget held; "budget off" dropped | fine: D-634 read it; crossing levers is a later declaration |
| 18 | levers not crossed; Back2Funded not under No Activation Fee | fine (`back2funded_fee_by_pricing_path` unstated) |
| 19 | resets and the DLL excluded | right (`reset_rebill_push` against the engine; D-320 (2)) |
| 20 | no Focused Trader models on house money and `naf`, the gap named | enough under E-146; sharpen the reasons (v4) |
| 21 | Back2Funded in a copy of the vendored path, not a subclass | right: keeps the class the models require (E-059 (2)) |
| 22 | compose the size-fit pieces, not its runner | right: D-559's two files are absent; the stop-and-report clause covers failure |
| 23 | RD-02's uncertainty method with a fresh honesty seed | right |
| 24 | the frontier without house money, and with it labelled | right; T-14 to follow (v2) |
| 25 | the beside rows' guard carries the 0 % gate, labelled | right: no gate runs under a beside response |

No choice is made after an outcome. No choice reads a block, and none chooses among cells.

---

## 5. What I tried that found nothing

- The hash. The diff is confined to the declaration under `prereg/`; the other four files in the commit are master's
  merge.
- **Stale stop language.** I searched the second text for "go on", "goes on", "closed at the fit", "which levers" and
  "stops a lever" in stage 0's sense. Nothing is left outside the history in 0.1 and 6.5, apart from V2.
- Every cell count and beside total (section 1), re-added.
- **M3's absorbing claim with `exp_30`:** a lapsed pass pays no fee, so "ahead" stays absorbing. The 9.2 oracle and
  9.1 item 7 extend to house money.
- **m8:** `BASE` is as cited, and `imports(script)` exists for the closure.
- **No new judged-block purpose,** no new seed, no new rule key. Appendix R is unchanged.
- **m2's counted reading:** the Focused Trader measures are computed inside the copied path, so A-1 (e) is a marked
  addition there, not a vendored edit.

## 6. What I could not check

- Whether the registered policy's arrays fit the per-R classes built with each base's own rungs. That is the build's
  test; the text's stop-and-report clause covers it.
- Whether `state_policy_v12_noclose.csv` records the tie-broken round's rate, cycle cash and cycle days, which (a-1)
  would use. I did not open it; the remedy names the fallback.
- The run's cost at 30 cells and 360 beside replays (measured before step 3 under E-117's form).

---

## Appendix A3. The check behind V1 (scratchpad; exact chain, no seed)

- **Script:**
  `C:\Users\resni\AppData\Local\Temp\claude\197752aa8b2362c7\9862c1b3-c57d-4498-a2d7-44492c7a25e6\scratchpad\rt\m2_checks.py`.
  It ran under a one-minute limit.
- **The toy chain:**
  - a horizon of 300 days;
  - a funded account alive each day with probability 0.97, paying $12 a day, with no choice;
  - a Combine with two actions, per day: "safe" passes w.p. 0.02 and fails w.p. 0.03; "bold" passes w.p. 0.06 and
    fails w.p. 0.10;
  - the fixed policy is "safe";
  - fees: $49 at purchase, $49/21 a day accrued, $149 at the pass.
- **The rate.** `lambda_pi` comes from the fixed policy's forward summaries by Stage 2's `cycle_rate` formula: 0.1415.
- **Check (i).** Forward `W - lambda_pi T` = 395.241174, and the fixed-policy backward funded value = 395.241174.
  They are equal, but only with a fixed-policy evaluator, which the vendored solver lacks.
- **Check (ii).** The attempt's backward value net of its first subscription, at `lambda_pi`:
  - fixed policy, horizon-truncated pass values: **-0.025420**;
  - optimal (what the vendored `solve` returns): **+27.869119**.
  - Neither is zero to 1e-6.

---

## The proposed decision row (the lead numbers and commits it)

| E-NNN | 2026-11-17 | **Q-116r2 read (`docs/reviews/DRAFT_RD-03_contract_levers_v2_2026-11-17.md`; RD-03's second text at wt/wt-payout 4f5c0aa, LF sha256 `1dc9365e1b3b2a008a0af851aa6c932e580a55bad77d33b79f4d7ce05a84d603`, re-hashed, diffed against 153f453): pin after the listed changes -- every first-read finding answered as asked or as E-146 adopted it; two new defects, both text; five minors; no look-ahead, leakage, new seed, new rule key or after-the-look choice.** (V1) M2's two input checks, as worded, are vacuous or fail by construction: the vendored solver has no fixed-policy evaluator, and the fixed point is the attempt's worth net of its first subscription with horizon-truncated pass values (an exact toy chain: -0.025 under the fixed policy, +27.87 optimal, at the policy's own rate) -- `lambda_pi` taken from the vendored `cycle_rate`; the checks replaced by the evaluator's identities (the registered solution at FV3-C's edge, and D-666's solution at each base's edges, reproduced to 1e-9), with (c)'s forward-against-backward check kept and its zero check read on the exact solve within the rent search's bracket; each base's own rungs named; (V2) 15 step 1 lets stage 0's identity stop every cell, against E-146 and 6.4 -- a `cl_fit_identity` failure stops stage 0 alone; the waits and section 11 to match. Minors: T-8's stale item 3; T-14 to assert m6's frontier; the lost account leaves the funded list at the reactivation (T-2) and the one-session convention mix labelled on Back2Funded rows; the Focused Trader gap's reasons sharpened (`naf` identical to its base under every model, fees aside; house money placed no sooner than its base); G-9's citation. **Naming the Focused Trader gap is enough under E-146** (E-007 (e)'s "or the gap named" as adopted). Then the lead's diff check against 4f5c0aa, the gatekeeper, T-0 and the pin. | Q-116r2's brief; the addendum; E-007, E-134, E-135, E-146, E-147; Stage 2 D-325, D-329, D-495, D-666. |
