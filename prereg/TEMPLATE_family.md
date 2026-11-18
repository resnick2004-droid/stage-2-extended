# TEMPLATE: a family declaration of this repository -- copy it, never pin it

**What this file is.** The house form for a new family's draft, carrying the program rules every declaration must
meet (the rows cited in each section). It is not a declaration: it names no family, holds no seed, no k, no cell
count and no figure, and its name matches neither the reader's grammar (`F-` or `RD-` and a number) nor any test's
declaration glob, so no pin, seal or seed scan reads it as one (`tests/test_family_stats.py` holds that). **To use it:**
copy it to `prereg/DRAFT_F-XX_<slug>.md`, replace every `<...>` with the family's own text, delete nothing but the
template's instructions in *italics*, and send the draft to the red team, then the gatekeeper. The lead pins the
renamed file by the sha256 of its LF text in the pinning row (E-001 (b), E-003). **Nothing declared is edited: a change
is a new family.** A section left as the template wrote it is a gap the gatekeeper refuses.

*Every rule below is a floor. A draft may tighten one only with the tightening's level and power at the family's level
shown before the pin (E-051); it may loosen none without the operator (DIRECTIVE Part 1).*

## 0. In plain words (for the operator)

<What the design trades, when, on which side and why, in a paragraph a non-quant can follow; what would count as a
pass; and what a fail means -- "the family closes", never "we investigate further".>

## 1. Hypothesis: the mechanism, its sources, and each cell's sign stated in advance

<The mechanism; its sources (author, year, journal, title, and the market they studied); why it should hold on NQ;
each cell's expected sign. A mechanism with no source is said to be untested.>

## 2. Prior exposure: what has already read these bars, this population and this mechanism

<Every Stage 2 and program reading of the same bars, offers, levels or rules (the handoff's 3.1 and 3.2, the closed
families' rows), and what each has seen. The judged block is late development for direction, not out of sample, where
Stage 2 read the effect there.>

## 3. Contract fit and conduct (CHARTER section 4, item by item)

| item | the family's answer |
|---|---|
| stops in the stop band, above the cost floor | <...> |
| at least five minutes from alert to order, by hand; a resting ticket published at least five minutes before it can trigger | <...> |
| one position at a time per firm, five minutes flat between trades | <...> |
| at most 5 % of trades reaching the 15:10 CT flatten, overall and in every year | <...> |
| realised risk within 10 % on at least 90 % of trades | <...> |
| no entry before 07:35:00 CT on a BLS 08:30 day; FOMC days out | <...> |
| **conduct tier 1** (no hedging across accounts or firms, no simulator-fill exploitation, no maximum size into major news, no trade copied across accounts, nothing that conceals a pattern) | <...> |
| conduct tier 2 modelled and off in the base case; tier 3 priced, 0 % denial in the verdict | <...> |
| firm rules only from Stage 2's verified ledger (`vendor/stage2/config/rules.yaml`) or a row verifying them | <...> |
| no automated or API order entry | <...> |

## 4. Data, blocks, the seal and the confirmation window (dates, fixed now)

- **Development:** NQ 1-minute bars 2020-01-02 to 2026-07-16 only, read through `extended/reader.py` (the one door).
- **the choice block:** 2020-01-02 to 2023-12-29 <with 2020 as warm-up, if the family needs one>; everything that is
  chosen, fitted or searched is chosen here.
- **the judged block:** 2024-01-02 to 2026-07-16, read once, after the pin and after run 1's row; the runner asserts its
  session count and list against the count and sha256 E-094 (2) records.
- **The confirmation window:** NQ from 2026-07-17, declared now, never read until a carried candidate is registered,
  and a purchase (section 14).
- **Disclosed pre-reads:** <every file of this or Stage 2's that has read these bars for this question>.

## 5. Supply: the population, the schedule and the walk (counted before any outcome)

<The offers' schedule (marks, hours, days), the bracket and the walk (`extended/walker.py`, its identity E-011), the
offers per session and per block **from the schedule and the admitted marks alone**, and the family's supply on the
judged block in trades -- the count the power gate reads (section 10).>

## 6. The side, its persistence, its band and the fill intensity (E-035 (6), E-052, E-187)

- **The side's persistence, stated before the pin (E-035 (6)):** <the length in sessions over which the side is held:
  a switching side's mean dwell, or a regime filter's regime length -- with the reason from the rule>.
- **The band (E-187; Q-126's plan 2.5):** <below 42 | 42 to 50 | 51 to 62 sessions>. It decides which adopted
  statistic C1 may use; 63 sessions or more has no one-sample line. **The band check** holds the family to it from its
  sides only, never an outcome: the balance limit for every kind, the runs interval for a switching side. **The
  regime-filter kind is barred** until a row lifts the bar (E-187); a regime filter may be checked as a switching side.
  A cell scope D does not admit at stage C is "not claimed" unless a two-sample line was declared for it here.
- **The fill intensity (E-052):** <whether the trades a session can persist, and why>; stated beside the side's.

## 7. Parameters: fixed / searched / dropped (every one, with its value)

| parameter | what it is, in a phrase | fixed / searched / dropped | value or grid | source |
|---|---|---|---|---|
| <...> | <...> | <...> | <...> | <...> |

- **Fitted values (E-031 (1)):** only inside the declared walk-forward on the choice block (2020-01-02 to 2023-12-29),
  each procedure fixed here before any read, every searched value counted in the trials, the fitted model hashed and
  pinned in a row before any judged read; nothing fitted, chosen or tuned on the judged block (the reader refuses such
  a purpose). **The reverse walk-forward is dropped** (E-031 (2)); year-by-year readings of the pick go beside.
- No fitted value in a grid: grids are contract arithmetic and verified rule values (Stage 2 D-621 (4)(d)).

## 8. The cells and the count

- **k_cells** = <the product of the cells' factors, written as a product and a number>; **every cell is counted**,
  whether dropped at the pin, killed at stage A, closed at stage B or read at stage C; every searched configuration and
  every fitted value counted beside it.
- **k:** the next free program family number at the pin, written by the gatekeeper in the pinning row; the family is
  judged one-sided at **0.05 / (k (k + 1))** (E-001 (a); the program spends at most 5 % however long it runs). One
  cell reaches judgement; stage B spends none of the budget.
- The program's honesty sentence: <what Stage 2's programs S and U and this program have read on this window, and
  that the development level is a screening threshold, the decision carried by one confirmation on unread data>.

## 9. The deciding lines and the floors (E-008, E-023, E-035, E-052, E-094 (3))

- **C1, judged on trades first (E-008):** the lift over the coin twin on the same brackets on the judged block,
  one-sided at 0.05 / (k (k + 1)). **A one-sample C1 only via Q-126's adoption row:** the statistic that row adopts
  for the band of section 6, in its scope (`extended/lift_one_sample2.py` at the blob the row pins). Before that row
  exists the family may be drafted, red-teamed and built on synthetic data, **not pinned** (E-094 (3) (b)-(c)); a
  conditional pin needs its own lead's row. E-052's criterion applies per statistic: the family's condition is met
  when the statistics its deciding lines use hold (E-094 (3) (a)).
- **C1', C2 and the two-sample forms:** `extended.lift_bound.two_sample_bound` and `placebo_selection_bound` (they
  hold, E-094 (1)); C2 priced by the value map at the places the routing reaches, its value at the bound at least
  <the family's bar; the program's is $500 a year>.
- **B2 (E-035, E-051):** every deciding line read by `cons` at the larger of each member's nominal t and B2's
  (1 - level) quantile, conditional on the real judged sides, through `extended/family_stats.py`
  (`larger_of_one_sample`, `larger_of_two_sample`, `b2_null_pooled` or `b2_null_strata`, `b2_critical`); the null's
  form, mean block, switching rate, amplitude rule and **replicate count fixed exactly** here, with its seeds by role
  (section 15). *Q-145's caution: a pooled null whose choice block carries its own slow drift can under-cover on a
  one-sided side series when the amplitude is at or below the true one -- declare the amplitude with that in view and
  show B2's level on the family's own toy at the family's level.*
- **K0 (E-052):** `cons`'s size at the family's level on Q-16's `cluster` null with each cell's own choice-block counts
  at random circular offsets; a cell whose 95 % interval lies wholly above nominal is killed before stage B; the same
  check on the pick's judged counts before any outcome, a pass not claimed above nominal.
- **The floors:** the long-run gate (growth on the required bankroll at the bound, Stage 2 D-145) above zero; every
  offered R resolving; verified rules; conduct tier 1.
- **The runner's assertions (E-052 (3)):** the level equal to `lift_bound.family_level(k)`, in (0, 0.5), k in the
  calibrated range; the judged session count and list as E-094 (2) records them.

## 10. Power before the pin: the power gate, the conjoint MDL, the screen rule (E-051, E-086)

- **The power gate, before the pin:** `extended.family_stats.power_gate` reads Q-126's power file
  (`results/q126_cal_power.csv`) at the family's k, its adopted statistic and scope, its value (`win1` or `net3`) and
  its declared supply (section 5), against its bar in the same unit. **At the pin a family or cell is dropped only
  on an empty MDL** (infinite: no lift on the toys' range detects it), taking no k, as family R's cells were (E-086);
  **the factor-3 screen is a label at stage A**, never a drop at the pin (the lead's ruling on RL3's red-team read,
  finding B-1: a pass-line rule shows power as well as size, and the ratio at a ceiling supply understates the bar's
  lift). The MDL's ratio to the bar and the gate's `screen_label` are written in the pinning row beside. Until the file
  exists the gate refuses, and a one-sample family waits.
- **The conjoint MDL (E-051's M5-2):** the minimum detectable lift of every deciding line together at the family's
  level, on choice-block proxies, seeded, written in stage A's result before stage B reads any lift
  (`conjoint_mdl_grid` or `conjoint_mdl_linear`): <the proxy, the planted lift's form, the grid, the draws, 80 %>.
- **The screen rule (a label at stage A):** if the conjoint MDL exceeds 3 times the value bar at every surviving cell,
  the family is declared a screen (`screen_rule`), said with the figure; it drops nothing, and a pass is then carried
  with that said in its row.
- **Every tightening shows its level and power at the family's level before the pin (E-051):** <the tests that show
  it, on toys with known truth, at fixed seeds of section 15>.

## 11. The stages and the Kill rules

*Kill lines on supply, resolution and realised risk come before any outcome. A killed cell is counted; a killed family
closes and its judged block is not read.*

- **Stage A (the choice block, before any lift is read):** the dependencies hold (refusing); **K1** supply (<offers a
  year in every choice year>); **K2** resolution (the share flattened unresolved at most 5 % in each choice year);
  **K3** realised risk; **K0** (section 9); the positive control; the conjoint MDL and the screen rule (section 10).
- **Stage B (choose on the choice block):** <the one estimator, its bootstrap, the family-wise critical value, the
  pick's rule and its eligibility margin>. **Kill B:** no cell above the family-wise critical value -- the family
  closes and the judged block is not read.
- **Stage C (judge the pick once, on the judged block):** in the order of the reads line (section 13); the band check
  on the judged sides before any outcome; the judged-count check; C1, C1', C2 and the floors.

## 12. Beside, never deciding (E-157 (b), E-161; CHARTER section 2)

- **Q-122's readings (E-157 (b)):** the regime-bucketed readings (a causal trailing session range, terciles absolute
  and relative) and the equal-weight-block reading beside `cons`, never deciding.
- **E-161's drift nulls** (Q-126's plan 3.3, constant and sign-varying drift) named beside the one-sample line.
- **The user scorecard (E-008, E-014, E-015):** P and the guarded measures against `R* = P-14`, the frontier, the
  denial ladder, the placement on and E-007 (e)'s readings, each a distribution over start days; the verdict at 0 %
  denial with the placement off; the operator's limits as menu flags only. Beside, never the pass line.

## 13. The judged block's reads (E-026)

The reader authorises a judged-block read only for a purpose named on this line of the pinned file:

- **Judged-block reads:** `stage_C_sides`, `stage_C_judgement`, `stage_C_campaign`, `stage_C_scorecard`

<What each purpose reads, in stage C's order; each read once, from a clean run of a committed tree, ledgered before it
reads. No choosing or fitting purpose is named, and the reader would refuse one.>

## 14. What a pass and what a fail means; the confirmation

- **A pass:** <the design is carried: it takes a registration id, its registered test, the auditor, and one
  confirmation>.
- **A fail -- what a fail means:** <the family closes; the k is spent; nothing of it is rerun; a new question is a new
  family citing this one>.
- **The confirmation:** NQ from 2026-07-17, read once, only for a carried candidate, at <its form and level>; a
  purchase, the operator's.

## 15. Seeds -- by role, found nowhere else

| seed | its role: what it draws, by stream |
|---|---|
| `<S0>` | <...> |
| `<S1>` | <...> |

- Every seed an integer written here before any run, **one role each**, a block never used before in Stage 2 or here,
  **found nowhere else**: checked by the house search with the licensed data excluded (`grep -rIlw --exclude-dir=.git
  --exclude-dir=data` over the tree and the vendored snapshot, and `git grep` over every commit of every branch), the
  check's command and hits written here; a test of the draft refuses its block in any other declaration.
- Streams are children of a named seed, `default_rng([seed, stream, i])`, never the seed plus an offset (E-171,
  `tests/test_seed_derivation_guard.py`). A seed chosen after a result is a variant.
- Inherited seeds are used only as their owners registered them, named here with their owners.

## 16. The run order -- refusals first

1. **Refusals first**, before anything is read, each refusing: the declaration pinned and unedited
   (`tests/test_declarations_fixed.py`); the identities on record as holding (`identity/stage2_identity.py`, the
   shared ones the runner waits on, by their covers); the power gate's verdict recorded in the pinning row; a clean
   checkout of a named commit (`scripts/run_clean.py`); the run lock held (one heavy run on the machine).
2. **A0**, the family's own identity run, under its own identity row, before any outcome of the runner is believed.
3. **Run 1** (the choice block only): stage A, the walk-forward and its final fit, stage B; it reads no judged-block bar
   or walk.
4. **The lead's row**: run 1's result file by its sha256, the pick and every fitted model's hash, pinned and committed.
5. **Run 2** (from a clean checkout of that commit): stage C in the reads line's order, the floors, the scorecard.

Each run once, watched to its exit, its file written with its manifest (`extended.results.write_result`, `prereg_id`
the F-id, the cell count, every seed and parameter). A kill stops the sequence. A failed check stays on record and is
diagnosed by the failure protocol, never rerun until it passes.

## 17. The build and its tests (after the pin, before any reading)

<The code in this repository's package (never in `vendor/`), the shared module `extended/family_stats.py` imported, not
copied; each test written before its code; fast tier unless marked; the level and power at the family's level of every
rule this family adds (E-051).>

## 18. The pin's conditions

- Q-126's adoption row for the band of section 6 (a one-sample C1); the statistics its deciding lines use holding
  (E-094 (3) (a)).
- The power gate read (section 10): every cell kept has a finite MDL (a cell with an empty one is dropped, counted);
  its ratio and screen label written in the pinning row, deciding nothing.
- The red team's read answered; the gatekeeper's approval; the seed search repeated at the pin.

## 19. Anything chosen after seeing results

*(Empty at the pin. Anything added after a reading is exploratory, reported apart, `exploratory=True` in its manifest,
and recorded in its own decision row -- never added to this file once pinned.)*
