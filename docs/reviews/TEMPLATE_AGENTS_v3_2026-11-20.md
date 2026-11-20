# Red-team re-read: Wave 2 after its second corrective cycle (2026-11-20)

**Target.** `wt/wt-lit` at 1a9be8c, read as `git diff 1a9be8c~1 1a9be8c` (nine files) and, for the full re-reads, the
files at 1a9be8c. "T l.N" cites `prereg/TEMPLATE_design_search.md` at 1a9be8c; "GK l.N" cites
`.claude/agents/prereg-gatekeeper.md` at 1a9be8c. The Wave 3.2 runner is read at `wt/wt-three` adedf7f.

**Scope (the coordinator's).**
- A full re-read of R-10 (T section 5): N-1 (the take decided at the fill by L_fill), N-2 (a rule's exit at a profit
  level takes the race at min(g, level)), attacked for drift, look-ahead and an outcome-dependent take; and its
  consistency with the corrected runner (`wt/wt-three` adedf7f, E-237's rulings).
- A full re-read of the gatekeeper's item 5.
- Diff checks: n-1 to n-6; the E-221 alignment (O-1, O-3 / Wave 4.2, O-4, O-5, O-6 (a)); E-223 M-4's news flatten; the
  edits to the auditor, red team, `prereg-discipline`, `feature-rules`, `/brief` and `/status`.

**The brief's framing.** The brief describes the runner's race and walk and E-237's ruling. I checked the runner
against E-237's text and against the template; I did not take the brief's description as the answer.

**Labels (E-207 (2)).** Blocking: it could make a result wrong. Minor: wording, a clarification, or a defect that
cannot bind yet.

---

## Verdict: **blocked** -- must be re-declared in R-10, section 2's held-out line, and section 4's side rule.

- **N-1 and N-2 are answered in the template's text**, and both are free of look-ahead: the take reads only the fill's
  state, and the as-placed level is known at placement.
- **But R-10 still rounds inward, against E-237's ruling** (B-1). That is the stranded-account defect the Wave 3.2 read
  found in the runner. The template, seven copies and two tests keep it.
- **The take rule leaves a second stranded state** that E-237's fractional race does not remove (B-2). It affects both
  the template and the runner.
- **Two alignment gaps:**
  - O-1: the search template still carries, and its test requires, the `Judged-block reads:` line that O-1 moves to the
    held-out test's declaration. That declaration's own Q-158 token is not written anywhere (B-3).
  - O-4: the playbook side's no-harm floor, and its "not carried" consequence, are missing from the floors the template
    points to (B-4).
- **Where the template and the runner differ:**
  - E-237 governs the race and the walk: fractional L, and the walk's last sub-step a two-point race. The template must
    change.
  - The template governs the take (N-1) and the profit-level row (N-2). The runner must change: both defects are latent
    at adedf7f (m-1, m-2).

| id | label | one line |
|---|---|---|
| B-1 | **blocking** | T l.193-195, l.239, l.262 and the gatekeeper's item 5 (GK l.100-104) round L and L_fill inward. E-237 rules the race fractional and the walk's last sub-step a two-point race. Inward rounding leaves every cushion-bound loss under a tick above the floor: never breached, never replaced, still billed. Seven copies and `tests/test_design_search_template.py` l.313, l.328 and l.505-512 require it. |
| B-2 | **blocking** | The take rule ("L_fill <= 0: not taken") makes an absorbing state. An account whose floor room is at most the entry cost plus max(x_stop, x_flat) never trades and never fails. It is reached by stop-bound race losses, walk time exits near the barrier, and walk barrier losses when x_flat > x_stop. The vendored engine has no such state. Both the template and the runner (adedf7f `_barrier`, l.234-241) carry it. |
| B-3 | **blocking** | O-1 is not carried through section 14. T l.556-569 keeps the `Judged-block reads:` line with "Keep the house names", and the test at l.181-195 asserts the line is there. Under Q-158, that line plus the search's own finalists' token (step 7) authorises a lone search's held-out read. Step 8 never gives the held-out test's declaration the `heldout-finalists:` token for its own hash that rule 1 needs. |
| B-4 | **blocking** | O-4's floor is dropped. T l.144-147 says the trigger's side is "held by the no-harm floor ... (section 10 (c))". Section 10 (c) (l.434-437) holds only the resting-trigger floors, and section 11 (l.460) puts "the playbook's trigger-side reading" beside, never deciding. CHARTER 3.5's "a trigger whose side fails the no-harm floor offers no playbook side; that design is not carried" is nowhere in the template or GK item 4. |
| m-1 | minor (runner) | adedf7f `_barrier` l.239 nets x_stop for a race and max(x_stop, x_flat) for a walk, then takes on `Lt > 0` (l.336, l.382). So the take still reads the exit's law (N-1). It is latent: every vendored profile has equal stop and flatten slippage. It must change before a profile or stress with unequal slippage runs. |
| m-2 | minor (runner) | adedf7f `EXIT_LAW` (`three_way_redraw.py` l.55-64) has no profit-level row, and maps `"other"` ("a rule's exit") to the walk: this is N-2's defect. It is latent because the toy rules have no rule exits. It must change before any runner reads A3 `cap` or a need-aware exit. |
| m-3 | minor | N-2's level has no unit. The engine's need is a net-dollar amount, so g' = min(g, (level + x_target) / tick value) to net it exactly, or as declared. A fractional g' is refused by the runner's walk (`walk_barriers` l.169). Say whether it is rounded down to the lattice. |
| m-4 | minor | E-223 M-4 is carried. The deciding reading books a news exit at `flatten_slippage_ticks` on the walk's value at the window's start, less than M-4's as-walked convention by the first bar's adverse excursion and a tick. State it as a declared reading and print the cost gap and the news-flatten share beside. |
| m-5 | minor | `test_n1_...` (l.515-536) is a tautology: `_l_fill` takes no exit, so its dict of decisions cannot differ. Hold N-1 in the runner instead. That test fails at adedf7f (probe 1 below). |
| m-6 | minor | "No design search pins before Q-158 merges" (T l.516; GK l.81-82) and "built, E-220" (T l.548): Q-158 merged at E-222. Cite E-222 and drop the condition, or say it is met. |
| m-7 | minor | "one declaration of its own (E-230)" (T l.68, l.449, l.493, l.535; GK l.62) cites a row that does not say it. E-230 says "the joint held-out read is 'the held-out test', its order across firms declared before it". The ruling's words are in E-238 (Wave 2's staged cycle, "with the lead's rulings"). Cite E-238, or have the lead record it. |
| m-8 | minor | The red team's item 8 (`red-team.md` l.59-68) gained neither N-1 nor N-2, and still says "the walk's barriers on its lattice inward". |
| m-9 | minor | T l.522-525's "<that row>": the lead's CHARTER 3.7 reading row (n-1) does not exist in `DECISIONS.md`. A drafter cannot fill it. GK should refuse a pin before the row exists. |
| m-10 | minor | `/brief` (l.48-50) and `/status` (l.32-33): "O-1 and O-3 to O-7 ruled at E-221". O-5's governing form is E-230's; cite both. |

n-1 to n-6: each is answered (section 4 below). O-3 / Wave 4.2, O-5 (as E-230) and O-6 (a): aligned.

---

## 1. R-10, re-read in full (T l.235-281, with l.186-204)

### N-1 as written: no look-ahead, no drift, no exit in the take

- **Inputs.** L_fill = min(l, c - max(x_stop, x_flat)) (T l.239). It reads:
  - the bracket as placed;
  - c, the room after the entry cost (l.188-191): the floor's room and the day's loss-limit room, both known from the
    account's state before the order;
  - the profile's two exit costs.
- **What it does not read.** The exit reason, the walked path and the redraw's uniforms. A worse-fill stress adds the
  same ticks to both costs before the take. A missed-signal draw comes before it.
- **The race, the walk and the floor:**
  - the race keeps L = min(l, c - x_stop) >= L_fill (l.242);
  - the walk uses L_fill (l.262);
  - with costs netted, no exit passes the floor (re-derived below).
- **Drift.** None.
  - The race: p = L/(L + g) has gross p g - (1 - p) L = 0.
  - The walk, in its runner form: each step is a martingale move. The plain step is ±s at one half. The bottom step
    goes to -L with probability s/(s + rho), else up by s, and its mean is (-rho s + s rho)/(s + rho) = 0.
  - The walk stops at the first barrier or at n steps, a bounded martingale stopped at a bounded time.
  - `walk_law` gives exactly 0 at L = 37/3, n = 9 (probe 5). When L is a multiple of s, the bottom step is a plain step
    (q_bar = 1/2).
- **Clock.** n = round(sigma^2 T / s^2) uses sigma from bars closed at or before the alert and T from fill to a limit
  known at the fill (l.266-271). Bars are stamped at their open, so the last bar it may read at alert t is the one
  stamped t - 1 minute. The exception, an unscheduled release (the table's last row), is declared and its share
  reported.
- **Lattice step.** s is one tick, or a fixed declared value (l.244-245); not left to the build. **N-1 is answered as a
  rule.** The defects are in its rounding (B-1) and in what happens to an account it never lets trade (B-2).

### N-2 as written: the level is known at placement

- **The vendored engine** computes `need_to_pass(rules, day_pnl)` or `day_allowance` before it calls the draw
  (`vendor/stage2/propedge/campaign/lockstep.py` l.459-466). So min(g, level) is a fill-time quantity.
- **The template** makes it "the target as placed" for every terminal state (l.187-188). A trade carrying a level that
  ends at its stop, or at a time limit, uses the same g', so the law does not depend on which barrier was hit.
- **The table** maps the row to the race (l.254), and "any other exit" no longer names a rule's exit (l.258).
- **Answered**, subject to the units in m-3.

### B-1. Inward rounding stays in R-10 after E-237 ruled it out. **Blocking.**

- **Where.**
  - T l.193-195: "rounded inward to the tick lattice when the cushion binds".
  - T l.239: L_fill "rounded inward to the lattice".
  - T l.244-245: "L_fill is then computed on that lattice".
  - T l.261-262: the walk's loss barrier "**rounded inward**".
  - GK l.100-101 and l.104.
  - `red-team.md` l.60 and l.64; `merge-checklist` l.80 and l.83; `feature-rules` l.96; `contract-engine` l.133;
    `prereg-discipline` l.73; `auditor.md` l.3 and l.75.
  - The tests require it: `tests/test_design_search_template.py` l.313 (`assert "inward" in text` for every copy),
    l.328 (`"rounded inward"` in section 5), and the `_l_fill` helper (l.505-512).
- **The governing text.** E-237 (2026-11-19, the lead's rulings on the Wave 3.2 read):
  - "the race at fractional L, no rounding; R-10's walk resolving its last sub-step before the floor-side barrier by a
    driftless two-point race".
  - The finding it rules on (`docs/reviews/BUILD_W32_H3_2026-11-19.md` l.75-110): with any fractional cost,
    c - x_stop is almost never a whole number of ticks, so inward rounding turns almost every account failure into a
    stranded account.
  - CHARTER 3.2 names `adapter.BinaryDraw`'s form, which is fractional (CHARTER l.139).
  - Inward rounding was the design note's N-4 rule for the shared path of overlapping positions (note 1.6). It was not a
    rule for the single-trade race. The runner says so (`three_way_redraw.py` l.18-21).
- **Failing input.** Toy rules, s = 1. A cushion after entry of c = x_stop + 7.752 ticks:
  - The template: L = 7. A loss leaves 0.752 ticks above the floor.
  - The next trade: L_fill = floor(0.752 - max(x)) <= 0, so it is not taken. The account is never breached and never
    replaced, and keeps paying its fee.
  - The runner (fractional): L = 7.752, and the loss ends on the floor (`_settle` breaches at `bal <= floor + EPS`,
    adedf7f l.253). The account is replaced, as the vendored lockstep does.
  - E-237's own probe measured the effect on P_B and on replacements. Its figures are in that note, not retyped here.
- **What governs.** E-237: the lead's later ruling on a diagnosed defect, matching CHARTER 3.2. The runner stays as it
  is.
- **Remedy (the template and every copy):**
  - The race: L = min(l, c - x_stop), fractional, never rounded.
  - L_fill = min(l, c - max(x_stop, x_flat)), fractional, with the take at L_fill > 0. Name the tolerance: the runner
    uses `EPS` dollars.
  - The walk: on the lattice of step s from the fill, its floor-side barrier the fractional L_fill. At the last
    lattice point above it (rho = L_fill - d s below), a step goes to -L_fill with probability s/(s + rho), else up one
    step.
  - Delete "L_fill is then computed on that lattice". Keep "rounded inward" only for m-2's shared path, where the
    design note puts it.
  - In the tests: replace l.313's `"inward"` with a check for "fractional"/"never rounded", and l.328 likewise. Make
    `_l_fill` fractional. Add the runner's forced-loss toy (E-237) as the template's exact-fraction case.

### B-2. "Not taken" makes an account that can never trade and never fail. **Blocking.**

- **Where.** T l.199-201 and l.240-243 ("L_fill <= 0 means the trade is not taken"). GK l.103-105. The runner: adedf7f
  `_barrier` l.234-241 returns 0 where `room - e - x <= EPS`; `taken = act & (Lt > 0)` (l.336); nothing else changes
  the account.
- **Evidence.**
  - An account whose floor room R satisfies 0 < R <= e + max(x_stop, x_flat) cannot take any trade, whatever the
    bracket.
  - Nothing it does changes R, so the state is absorbing: alive until the horizon, billed, never counted as a failure.
  - The vendored engine has no such band. It races min(risk, cushion) at any positive cushion, so an account a cost
    above its floor trades on and, almost surely, fails at the floor (the race's limit as L goes to 0+).
  - B-1's fix closes the cushion-bound route only, where a race loss ends exactly on the floor. Three routes remain:
    1. **A stop-bound race loss.** R lands in the band when R before the trade is in (e + l·tv + x_stop,
       2e + l·tv + x_stop + max x]. Probe 2: tick $5, e = x_stop = $2, l = 20. R = $107 is a loss to $3, never taken
       again, not breached.
    2. **A walk's time exit near its barrier.** The lowest lattice point leaves R' = rho·tv + (max x - x_flat), at most
       one step plus the cost gap. For NQ, e + x is more than a tick, so every cushion-bound walk that ends at its
       lowest point strands its account.
    3. **A walk's barrier loss when x_flat > x_stop.** This leaves x_flat - x_stop (probe 3: $4).
- **How large (scratch, not a result).** A seeded toy: static floor at $2000, tick $5, every cost $2.12, 400 trades,
  20 000 accounts, a 5 % walk share. It ends between about 1 % and 4 % of accounts this way, rather than failing,
  across four brackets. The share moves with the bracket, so a search lever moves it.
- **The failure it allows.**
  - Ruin is understated and fees overstated, by an amount that depends on brackets and sizing.
  - A sizing lever that cuts risk to the room (S3's "cut ... by the room cap", `LEVER_TABLE_topstep50k.md` l.70)
    lands stop-bound losses near the floor. It can buy "accounts that never fail" on a ruin dimension or a ruin limit.
  - The designs and the baselines carry the same rule, but their exposure differs, so the comparison is affected too.
- **Remedy.**
  - Where the floor's room binds and L_fill <= 0, book the account as failed at that fill: the balance taken to the
    floor, a breach, replaced at the close as the engine does. This is the race's own limit as L goes to 0+, and needs
    no new law.
  - Where the daily loss limit's room binds, the day stops (`stopped`), as now.
  - Count these failures apart and report their share beside the verdict.
  - Add an exact test, for the template and the runner: an account at R = e + max x - epsilon fails; one at
    R = e + max x + epsilon takes the race.
  - Whether S3's whole-micro cut creates its own untradeable state (zero micros at a positive room) is the lever's
    builder's to show. I did not read Stage 2's handling of it.
- **The experiment to settle the size** (light, synthetic):
  - the runner's `_trade_mc` on the H3-A toy and on a Topstep-shaped toy (MLL, DLL, fractional costs from
    `fills.yaml` `assumed`, brackets over S1/S3's ranges);
  - count the lanes alive with room in (EPS, e + max x] at the horizon, with and without the remedy;
  - read P_B and replacements;
  - minutes on one worker.

### Consistency with the corrected runner (adedf7f): which governs

| point | template (1a9be8c) | runner (adedf7f) | governs | change |
|---|---|---|---|---|
| race barrier | min(l, c - x_stop), inward | fractional, never rounded | E-237 | template (B-1) |
| walk barrier | L_fill, inward to the lattice | fractional L_fill, last sub-step a two-point race | E-237 | template (B-1) |
| take | L_fill (max of both costs) for every trade | x by law: x_stop for a race, max for a walk (l.239) | the template's N-1 (the v2 read's ruling) | runner (m-1) |
| a rule's profit level | race at min(g, level) | no row; `"other"` ("a rule's exit") goes to the walk | the template's N-2 | runner (m-2) |
| untradeable account | not taken, alive | not taken, alive | neither as written | both (B-2) |
| lattice step | one tick unless fixed | `Trade.walk_step`, default 1, divides l and g | consistent | -- |
| n | round(sigma^2 T / s^2), halves up, at least 1 | `walk_steps` the same | consistent | -- |

**m-1, in detail.**
- Probe 1: tick $5, e = x_stop = $2, x_flat = $6, room = e + x_stop + half a tick.
- An exit reason `stop` gets a barrier of 0.5 ticks and is taken. The same trade with exit reason `flatten` gets 0 and
  is not.
- The take therefore reads the run's exit.
- **Remedy:** take on `min(l, (room - e - max(xs, xf)) / tvn) > EPS` for every law. Keep the race's barrier at x_stop.
  Add the v2 read's test (two trades identical at the fill, one barrier exit, one time-limited, taken alike) to the
  runner's suite.

**m-2, in detail.** Add an exit reason for a rule's profit level, mapped to the race, with the Trade's g the as-placed
target. Strike "a rule's exit" from `"other"`'s comment. Both are required before a firm's runner reads A3 `cap` or a
need-aware exit.

---

## 2. The gatekeeper's item 5, re-read in full (GK l.99-113)

- **Carried correctly:**
  - the costed race;
  - g as placed;
  - `BinaryDraw` as the cost-free case, keyed by the coin field;
  - the take at the fill, refusing a take that reads the exit;
  - s one tick or fixed, refusing an s left to the build;
  - m-2, m-3;
  - R-10's table, with the profit-level row and the walk only for real time limits;
  - the causal step count;
  - the pair rule's settlement;
  - the exact-fraction test for a replaced form.
- **To change:**
  - "rounded inward to the tick lattice for a fractional cushion" (l.100-101) and "rounded inward" (l.104): B-1.
  - Add a refusal for a draft that leaves an untradeable account alive (B-2).
  - Add the walk's two-point last sub-step as the house form.
  - Item 5 does not say the level is converted to ticks gross of x_target (m-3).
- **Item 4** (l.93-98) carries O-4's side rule without "not carried" (B-4).
- **Item 1** (l.60-65) refuses a search naming a `heldout_*` purpose of its own. That is right, and it is the only
  guard against T l.561's instruction (B-3).

---

## 3. The alignment and diff checks

### B-3. O-1 is not carried into section 14's held-out line, nor into Q-158's tokens. **Blocking.**

- **Where.**
  - T l.556-569 keeps the line, with the italic "*Keep the house names*" and "Nothing else of this search reads the
    held-out years". The line is "**Judged-block reads:** `heldout_test`, `heldout_stress`".
  - `test_the_template_names_its_held_out_reads_as_the_reader_parses_them` (l.181-195) asserts exactly one such line,
    because "a search drafted on the template must carry that line, or its one held-out test cannot run".
  - Step 7 (T l.529-533) writes each search's finalists' row as `heldout-finalists: F-NN @ <this file's sha> ...`.
  - Step 8 (l.534-539) does not say what token the held-out test's declaration needs.
- **Evidence.**
  - Q-158's rule 1 (`extended/reader.py` on master, `_finalists`, l.691-715) honours a `heldout_*` purpose for exactly
    the declaration named by a finalists' token with that declaration's sha. Rule 2 gives a market's window to the
    first family whose judged read is ledgered.
  - So a search drafted faithfully (line kept) whose finalists' row is written as step 7 says is authorised by the
    reader to read NQ's held-out years alone. Its read then locks the window against the joint test (rule 2).
  - Meanwhile the held-out test's declaration, which O-1 makes "the one family that reads NQ's held-out window", has
    no finalists' token for its own hash. The reader would refuse it.
  - Section 2 (l.63-73) and GK item 1 say the right thing. Section 14 and the test say the opposite.
- **The failure it allows.**
  - One firm's search spends the market's held-out years before the other firms have finalists, against O-1 (leakage
    across the joint test).
  - Or the joint test cannot run as written.
  - Only the gatekeeper's reading stands between the template's instruction and the first failure.
- **Remedy.**
  - In the search template, replace the line with: "this search carries no `Judged-block reads:` line (E-221, O-1);
    the held-out test's declaration carries it."
  - Move l.565-569 into a description of what the held-out test's declaration reads.
  - Say in step 8 that the held-out test's declaration takes an F-number and its own row
    `heldout-finalists: F-HT @ <its LF sha256> list <the joint list's sha256>`, the joint list file citing each
    search's finalists' list by its sha256.
  - Invert the test: a search draft carries no line, and the template's held-out paragraph names the held-out test's
    declaration as the line's holder.
  - The searches' own finalists' tokens are then harmless: the reader also requires the purpose on the file's own line
    (`reader.py` l.557).

### B-4. O-4's no-harm floor for the playbook's side is cited to a section that does not hold it. **Blocking.**

- **Where.**
  - T l.144-147: "held by **the no-harm floor** against the coin on the real path (section 10 (c); the no-harm margin
    pinned in section 7)".
  - Section 10 (c) (l.434-437): "the as-traded floors for resting triggers ... the no-harm floor on the search years".
    That is resting triggers only.
  - Section 11 (l.460): "The playbook's trigger-side reading (E-221, O-4)", beside, never deciding.
  - GK item 4 (l.95-96).
- **The governing text.** CHARTER 3.5 (master l.202-205):
  - The floor is defined: "its composite on the search years is not below the coin side's by more than the margin
    pinned in 3.9".
  - Only "its held-out reading is reported beside, never judged".
  - "A trigger whose side fails the no-harm floor offers no playbook side; that design is not carried (E-221)."
  - E-230 confirms it: "a design whose trigger's side fails the no-harm floor offers no playbook side and is not
    carried".
- **The failure it allows.**
  - A declaration copied from the template carries a finalist whose trigger side does worse than the coin on the search
    years by more than the margin. The only reading of that side the template keeps is a beside one.
  - The auditor checks "the pass line against CHARTER 3.8 and the declaration". This floor lives in 3.5, so neither
    check catches it.
- **Remedy.**
  - Write the floor and its consequence in section 4, or as a clause of 10 (c), in CHARTER 3.5's words.
  - Fix when it is read: on the search years, before the finalists' row, a failing design removed from the finalists'
    list, so the fixed sequence's order is not set after the held-out read.
  - Make section 11's line "its held-out reading".
  - Add "not carried" to GK item 4 and a needle to `test_e221_rulings_are_in_the_template_each_marked`.

### The rest of E-221 and E-223 M-4

- **O-1 (section 2, l.63-73; section 10, l.447-450; section 13, l.492-495; GK item 1).**
  - One joint fixed-sequence test across Topstep, My Funded Futures and Lucid, held until each firm has finalists.
  - It is its own declaration, which lists every firm's finalists by hash, fixes the order and takes the k.
  - The words are right, apart from B-3's mechanics and m-7's citation.
- **O-3 / Wave 4.2 (section 7, l.325-340; section 9, l.398-410).**
  - The limits, budgets, weights and the size that matters are the lead's, from H4's search-year results, by a rule
    declared before H4 is read, pinned in one row before the survey, never after a held-out read.
  - Aligned with E-221.
- **O-5 (l.335, l.417-421, l.460-462; GK l.42-43, item 10; auditor l.78-80; `prereg-discipline` l.75-76).**
  - The point estimate governs. Inside passes and outside fails, never a second margin. The one-sided check is
    reported beside.
  - This is E-230's form; E-221's "fails only when the evidence shows" is retired from every copy (the test at
    l.629-645).
- **O-6 (a) (l.343, l.427-431, l.442-445; GK item 7; auditor item 9; red-team item 9).** Over coin seeds on the
  held-out years, with the search years' history-block reading beside as a consistency condition. Aligned.
- **E-223 M-4 (l.167).**
  - One convention for every source: the adverse extreme of the window's first bar less two ticks, or the resting stop
    if the extreme reaches it. M-8's closed 08:30-08:59 window is included.
  - E-223 labels this "the as-walked convention". The template gives the deciding reading R-10's walk to the window's
    start at `flatten_slippage_ticks` (table l.256).
  - That is consistent with E-223's label, but it is the least conservative of the costs on record for that exit
    (m-4).

### The edits to the agents, skills and commands

- **Auditor** (l.3, l.75-86, l.123-124): the costed race, the take at the fill, O-5 and O-6 (a), all present. "Rounded
  inward" is B-1.
- **Red team** (l.72-76): O-6 (a) present. Item 8 not updated (m-8).
- **`prereg-discipline`** (l.73-84, l.99-103): the costed race, the take at the fill, O-5, Wave 4.2 as the lead's, and
  Q-158. "Rounded inward" is B-1; "before it merges" is m-6.
- **`feature-rules`** (l.63-69): n-5's settlement, word for word as the template. l.96 carries B-1.
- **`/brief`** (l.48-50) and **`/status`** (l.32-33): the open items replaced by NEEDS_OPERATOR, with the rulings
  cited (m-10).

## 4. n-1 to n-6, diff-checked

| n | answered at | state |
|---|---|---|
| n-1 | T l.522-525 (the go row is CHARTER 3.7's "pin"; the data question goes with the gate's result) | answered in the text; the lead's row it cites does not exist (m-9) |
| n-2 | T l.509-512 | answered: the final text with section 7 filled; a later value is a diff check or a re-read |
| n-3 | T l.529-533, l.546-552; GK l.78-82 | answered (the token form, Q-158 checks the token not the held-out row); stale merge condition (m-6) |
| n-4 | `prereg-discipline` l.73, auditor l.3, both in `RACE_COPIES` | answered |
| n-5 | T l.282-287; `feature-rules` l.63-69 | answered: both legs at the as-walked leg's settled outcome, difference zero by construction, share reported and capped |
| n-6 | T l.385-387; GK l.137-138 | answered: cite the failed record, report it beside, fresh seed block |

---

## What I tried that found nothing

- **Look-ahead in the take.**
  - Every input of L_fill traced: bracket, room after entry (floor and DLL room from the state), the profile's costs.
  - The stress ticks are added before the take.
  - The missed-signal draw comes before the take (adedf7f l.326-329).
  - No exit or path field enters.
- **Look-ahead in N-2's level.** The vendored need and allowance are computed from `day_pnl` and the rules before the
  draw (lockstep l.459-466).
- **Drift in the walk.**
  - The bottom step's mean is zero by hand, and `walk_law` is exactly 0 at a fractional barrier (probe 5).
  - It reduces to the plain walk when L is on the lattice.
  - No time exit passes the floor: -d s - x_flat > -L_fill - max x >= -c.
- **Outcome-dependent g.** None: g' is fixed at placement for every terminal state (T l.187-188).
- **The step count's clock.** sigma reads bars closed at or before the alert. T is known at the fill for every row but
  the declared last one.
- **The tests.** `tests/test_design_search_template.py` at 1a9be8c: 34 passed (`pytest -q -o addopts=`, wt-lit tree,
  clean). They pass because they hold the text, including B-1's and B-3's defects.
- **The copy-trading clause in conduct tier 1** (T l.168), checked against D-145's "coordinated trading" and D-157.
  It has a basis.
- **The probes**, run from scratch scripts against adedf7f's modules, reading no bar and writing nothing in a tree:
  - probe 1: the runner's take by law (m-1);
  - probe 2: a stop-bound loss into the untradeable band (B-2);
  - probe 3: a walk barrier loss leaving x_flat - x_stop;
  - probe 5: the walk's exact zero.

  The toy rates in B-2 come from a separate seeded numpy toy reimplementing the same laws.

## What I could not check

- The real frequency of B-2's state under Topstep's rules (trailing MLL, DLL, S3's room cut, the stop band). That is
  the experiment specified under B-2.
- Whether Stage 2's own engine has a "zero micros" untradeable state under D-313's room cap.
- The held-out test's declaration itself: it does not exist yet, so B-3's token form is a proposal.
- `merge-checklist` and `contract-engine` beyond their B-1 lines. They are outside this cycle's diff.
