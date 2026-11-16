# Red team, fifth read: `prereg/DRAFT_F-B_multifeature.md` version 5 (family B), 2026-11-16

**Target.** `prereg/DRAFT_F-B_multifeature.md` at a50ad94 (branch `wt/wt-scout`; the fifth version is 14b140c plus
a50ad94), with `tests/test_family_b_b2.py`, `tests/test_family_b_opening_range.py`, `tests/test_family_b_side_rule.py`
and the drafter's scratch checks `docs/reviews/scripts/family_b_drafter/*.py` (the four new ones: `m41_d_diag.py`,
`m42_flag.py`, `m43_conf.py`, `m45_sym.py`).

**Read against.**
- `CHARTER.md` sections 2 and 3 as amended (E-008's "a statistic calibrated to deliver that level").
- `DECISIONS.md` E-007, E-008, E-023, E-026, E-030, E-031, E-035, E-036, E-040, E-043, E-044, and the newest rows
  E-045 and E-046 (master's working copy).
- `extended/lift_bound.py` (`t_stats`, `block_index`, `session_sums`, `bound`, `mdl_draws`), `extended/reader.py`
  (`DECLARED_LINE`, `PURPOSE_TOKEN`, `CHOICE_WORDS`), `extended/features.py` (unchanged since the fourth read:
  `git diff e76ad23 a50ad94` does not touch it).
- The four earlier reviews of this family.

**What the brief held.** It named the parts the drafter changed against the fourth review's remedies -- C1-f's (d) with
the model's own judged yearly lift, C2 as the lesser of two routings, the confirmation's 1.3 x nominal floor, the
persistence flag's permutation null, the multiple 3 in g*_pre -- and asked that each be tested like anything else. It did
not say what answer it expected. The draft's section 0.1 says every finding is corrected; I treated that as the draft's
claim, not as a prior.

**What I ran.**
- Nothing read a bar, the atlas, the store's manifest, a Stage 2 result file or NQ from 2026-07-17. Nothing ran the
  engine or a slow test.
- The three family-B test files: 20 passed.
- Two synthetic scratch checks, seeds fixed before running (`[7701, ...]`, `[7702, ...]`, `[7703, ...]`), one process
  each, a few minutes on one thread, about 200 MB at most. They use `tests/test_family_b_b2.py`'s own helpers and
  constants (609 sessions, disagreement share q = 0.4, session sd 0.13, switching 1/250, random start). They are
  exploratory and select nothing. The Appendix gives them and their printed output.

## Verdict: **must be redrafted**

The fourth read's corrections mostly hold: (a) is absolute, the impossible part (b) is gone, sections 12 and 17 state
one rule, C2 takes the lesser of the two routings, the partialled reading is per alert with the range position and is
sealed, the persistence flag is defined and has power, the seeds are mapped, the bound arm's edges are defined.
Neither post-judgement rule (the (d) term, the lesser of the routings) can lower any bar.

But the amplitude rule now leaves C1-f no power, and C1-f is a kill line that must hold three times. Two MATERIAL
findings change declared rules:

- **M5-1.** (d) takes the **model's own** judged yearly lift. So C1-f's critical value grows with the model's own edge.
  - At the family's level, B2's two slow processes sit frozen in opposite states through the whole judged block with
    probability 0.0019, five times the level 0.05/132. B2's critical value is then about the frozen shift itself.
  - With g* at least the model's own lift, no steady edge can pass against a twin whose lift is not negative.
  - In the draft's own toy, at 0.05/132, C1-f rejects at most 1 in 10,000 replications at every edge up to a median
    t63 of 19. At the confirmation, its rejection rate stays at its size (0.05-0.07) whatever the edge.
- **M5-2.** Even without that term, g*_pre = 3 (a) costs most of the power, through the same frozen state and the
  symmetric component, and nothing that decides sees the cost.
  - For an uninformative twin, C1-f's 80 % MDL is about 2.7 times nominal `cons`'s. For a twin with a real
    choice-block lift T, the excess must be about six times T.
  - The stage-A screen rule uses the nominal MDL. The confirmation's months use C1's B2 ratio, not C1-f's.
  - So the family can fail to be declared a screen when it is one. A close would then read "no lift above the MDL at
    this family's level" against an MDL the line could not reach, and the operator would be asked to buy a confirmation
    sized for a test it cannot pass.

| id | severity | finding (one line) |
|---|---|---|
| M5-1 | **MATERIAL** | §12 l. 579-594, §17 l. 921, §16 l. 865-866: (d) includes the model's own judged yearly lift. B2's frozen-opposite state (P 0.0019 > 0.05/132) puts C1-f's critical value at about 4 q g*/SE, and g* ≥ the model's own lift, so for q ≥ 1/4 and a twin lift ≥ 0 the expected statistic never reaches it. Toy: power ≤ 0.0001 at every edge at 0.05/132; flat at its size at the confirmation |
| M5-2 | **MATERIAL** | §12 l. 583, §8 l. 453-458, §16 l. 883-884: g*_pre = 3 (a) with the symmetric component sets C1-f's bar at about 2.7 x the nominal MDL (uninformative twin), or an excess of about 6 T (a twin of choice-block lift T). The screen rule and the confirmation's months ignore it. The "3" has no source |
| m5-1 | MINOR | §16 l. 860-870: the confirmation's `t21w` at max(1.3 x nominal, B2) holds 0.05 pooled but is tested only to 1.5 x 0.05 per side series (the drafter's own runs reach 0.061). The 1.3 was chosen by comparing 1.0 and 1.3 on the test's two designs |
| m5-2 | MINOR | §12 l. 609, §17 l. 921: "at least 1,000,000 replicates" leaves B2's count open, and B2 for C1-f at g*_post and for C2 at both routings runs after the judged outcomes |
| m5-3 | MINOR | `tests/test_family_b_b2.py` l. 61, 290-324; §20 item 8 l. 1021-1024: every B2 test, and the build's declared-construction test, runs at 0.01 and checks level only. At the family level the frozen state binds, and no test checks power |
| n5-1 | NOTE | E-045 (4) names F-02 as k = 11, so this family is k ≥ 12 (0.05/156: t 3.84 / 4.46 / 5.41 at df 28 / 13 / 8; z 3.41). The draft's worked figures at 0.05/132 will change |
| n5-2 | NOTE | §9's hashed list (l. 482-487) omits the partialled reading's 60 x 5 coefficients and `z~_res`, which §13 (l. 756-758) and §20 item 11 put in the hash and T-3 |
| n5-3 | NOTE | `m41_d_diag.py` draws `[20261968, 65]` and `[20261968, 66]` through `T.SEED`. §19 attributes those seeds to the test only. A grep for the literal cannot find them. Harmless |
| n5-4 | NOTE | The long-run gate floor reads design (i)'s routing (§13 l. 742-743), which M4-2 showed selects on same-day outcomes. It is Stage 2's floor as Stage 2 used it, and C1 and C2 guard the pass. Say so beside |

---

## The fourth review's findings: whether each correction works

| finding | corrected? | why |
|---|---|---|
| M4-1 (a) absolute | yes | "largest absolute deviation of a choice year's lift from the block mean, plus the absolute mean" (l. 580-582) |
| M4-1 (b) dropped | yes | §5's pre-read row (l. 280) and §22 say no rule reads the S1/S3 files. E-046 (3) confirms they hold no per-year lift |
| M4-1 one rule | yes | §12 l. 579 and §17 l. 921 are identical except for a final period (checked by script) |
| M4-1 (d) | **added, plus a term the ruling did not name** | E-044 (2) ruled "the twin's largest absolute yearly lift on the judged block". The draft adds the model's own (l. 584-585, 591-594). That term makes the line unpassable: M5-1 |
| M4-1 test | extended, level only | l. 290-324 checks the size at 0.01, never the power and never the family's level: m5-3 |
| M4-2 | **yes** | C2 = the lesser of the two routings' dollar bounds (l. 715-734), B2 at each routing (l. 597-598), the "second order" text withdrawn, the confirmation likewise (l. 871-872). An intersection of a valid bound (design (ii)) and a questionable one (design (i)) holds the level of the valid one. The test reproduces check H (l. 346-369) |
| m4-1 | yes | per alert (l. 750-751), the range position (l. 755), B2 on the partialled sides at both levels (l. 761-763), the carrying sentence at the family's level (l. 764-766), the sides hashed under `stage_C_sides` (l. 253-256, 670-671; a50ad94), a session-weighted median. §9's hash list lags (n5-2). T-14 plants a breakout-follow effect (l. 1016-1018). The regressors read bars stamped ≤ 09:29, closed before every alert |
| m4-2 | yes | defined (l. 645-651), a permutation null, a filter's firing share (l. 657-658), a filter cell's MDL on its out-of-fold pattern (l. 450-452). It decides nothing |
| m4-3 | partly | B2's inputs declared (l. 861-867), a test at 126 sessions and 0.05. The level is held only to 1.5 x per side series (m5-1). The months' critical value ignores C1-f (M5-2) |
| m4-4 | yes, at a power cost | `(h_t - g*) s_i` added (l. 574-578). At the family level it doubles the frozen shift (M5-1, M5-2) |
| m4-5 | yes | mapped (l. 599-607, 969). The replicate count is still open (m5-2) |
| m4-6 | yes | `cons` at one-sided 0.05 on each design's per-offer mean net R (l. 735-738) |
| n4-1..n4-7 | yes | each in place (§0.1 l. 66-72). n4-3's "a lower bound" is true but far too small a word: M5-2 |

---

## MATERIAL

### M5-1. C1-f's critical value grows with the model's own edge, so the line cannot pass

**Where.**
- Section 12, l. 579 (the rule in one sentence), l. 584-585 ("(d) = the largest absolute calendar-year lift over the
  coin, over the judged block's years ... **of the twin and of the model itself**").
- l. 591-594: "Why the model's own term ... Its cost is power: a model with a large, steady lift raises its own C1-f
  bar."
- Section 17, l. 921; section 0, l. 40-41; section 0.1, l. 58.
- Section 16, l. 865-866: the confirmation's g* uses the same rule, with (d) over the window's own year.

**Evidence.**

1. **The algebra of B2's slow part for C1-f.**
   - B2's pair value is `d*_i ⊃ (g_t - g*) f_i + (h_t - g*) s_i` (l. 574).
   - C1-f's value is `x_i = (s_i - f_i) d*_i`.
   - Because `(s_i - f_i) f_i = s_i f_i - 1` and `(s_i - f_i) s_i = 1 - s_i f_i`, the slow part is
     `(h_t - g_t)(1 - s_i f_i)`. That is 0 where the model and the twin agree, and `2 (h_t - g_t)` where they disagree.
   - Per session it is `2 q_t (h_t - g_t)`, with `q_t` the session's share of disagreeing offers. `h_t - g_t` takes
     the values `-2g*`, 0 and `+2g*`. This is exactly the test's `follow_null_quantiles(..., symmetric=True)`
     (l. 272-276).
2. **The frozen state outweighs the level.**
   - Each process switches with probability 1/250 per session from a random start. It never switches over 609
     sessions with probability (1 - 1/250)^608 = 0.087.
   - Both frozen, with h high and g low through the whole block, has probability 0.25 x 0.087^2 = **0.0019**. The
     family's level is 0.00038 at k = 11 (0.00032 at k = 12).
   - So B2's (1 - level) quantile lies inside that event: it is at least the conditional 0.8 quantile of
     `(4 q g* + noise) / SE-hat`, about `4 q g* / SE`, inflated further by the block SE's few degrees of freedom.
   - The draft's own B2 tests all run at 0.01 (test l. 61), where the frozen state has less mass than the level and the
     quantile saturates. At the family level it does not saturate: my check prints t63w quantiles of 7.3, 15.1 and
     51.9 at g* = 0.01, 0.03 and 0.12, roughly linear in g*. At 0.01 the t63w quantiles are 4.2, 7.1 and 9.7 at g* = 0.012,
     0.032 and 0.12 (Appendix).
3. **g* is at least the model's own lift.**
   - If the model has a steady lift L, its judged yearly lifts are about L plus noise, so (d), and with it g*, is at
     least about L.
   - C1-f's statistic has mean `L - T` (the model's lift less the twin's). Its critical value is about `4 q g* / SE ≥
     4 q L / SE`.
   - For any twin with `T ≥ 0` that disagrees with the model on at least a quarter of the offers (q ≥ 1/4), `L - T ≤ L
     ≤ 4 q L`. The expected statistic never reaches the critical value, and a larger edge raises both together.
   - An uninformative twin agrees about half the time (q ≈ 1/2). `lnbar1x4` and `lbrk5`, against a model of 37
     features, are likely near that. C1-f must pass against all three twins.
4. **The draft's toy, under an alternative** (Appendix, check 1). The model's lift L is steady, the twin's is 0, and
   each line uses 20,000 replications. g*_pre is the test's own 0.006, the case most favourable to the draft. The grid
   lookup rounds down, also in the draft's favour.

   | at 0.05/132 | L 0.030 | 0.045 | 0.060 | 0.090 | 0.120 |
   |---|---|---|---|---|---|
   | median t63 | 4.75 | 7.13 | 9.50 | 14.27 | 19.01 |
   | nominal `cons` | 0.338 | 0.850 | 0.990 | 1.000 | 1.000 |
   | (d) of the twin only | 0.194 | 0.617 | 0.882 | 0.991 | 0.999 |
   | **(d) of the twin and the model (v5)** | **0.0001** | **0.0000** | **0.0000** | **0.0000** | **0.0000** |

   - At the test's level 0.01, v5's rate is 0.008-0.07 at L = 0.03-0.06, where nominal `cons` has 0.91-1.00. It rises
     only at t63 above 14, where the 0.01 quantile saturates. The family's level has no such saturation.
   - With a twin of real lift (L 0.06, T 0.03), v5 gives 0.0001 or less.
5. **At the confirmation** (Appendix, check 2): 126 sessions, `t21w`, one-sided 0.05. Over 126 sessions a process stays
   frozen with probability 0.61, and the frozen-opposite state has probability 0.092, more than 0.05.
   - Under v5, C1-f rejects **0.064, 0.073, 0.058, 0.056 and 0.053** at L = 0.04 to 0.18 (median t21 2.9 to 13.3). Its
     power never exceeds its size.
   - At 1.3 x nominal alone the power runs from 0.59 to 1.00.
6. **The draft's own scratch shows the symptom.**
   - `m41_d_diag.py` prints B2's symmetric quantiles at g = 0.03 as 7.9 / 7.5 / 7.7 against nominal 2.5 / 2.7 / 2.9
     (its l. 49 and 57).
   - `m45_sym.py` prints rates of 0.0008 and 0.0001 at 0.01 for v5's rule under its boundary null (its l. 45-46), a
     tenth to a hundredth of the level.
   - No test asks how often the rule passes a real edge.

**The failure it allows.**
- Any pick fails C1-f, whatever its edge. The family closes at stage C on C1-f.
- The closing row then reads "no lift above the MDL at this family's level" (l. 838). That is false: the stage-A MDL is
  nominal (l. 453), and a lift several times that MDL would still have been refused.
- k (11 or 12) is spent on a family that could not pass, and every later family's level tightens with it.
- If a pick did reach a confirmation, its C1-f there could not pass either. The months of data the operator is asked to
  buy (l. 879-890) are sized on C1's ratio.

**Remedy (changes a declared rule).**
1. **Drop the model's own term from (d).** E-044 (2) did not rule it. It cannot coexist with a power claim, however it
   is tuned, because its amplitude is the effect being tested.
2. **The lead names C1-f's null**, because the case that the model's term was meant to cover (the twin's lift sitting
   low through the whole judged block, `m41_d_diag.py`) cannot be identified from the judged block itself:
   - **(A) the realised paired lift on the judged block.** "The model's lift exceeds the twin's on the same offers in
     2024-2026", as C1 is the realised lift over the coin.
     - The slow components model only variation within the block: each replicate's slow process is centred on its own
       block mean.
     - The "twin sat low throughout" case is then not a false rejection. It is named in "What it cannot see", and the
       confirmation carries it.
   - **(B) the expected lift across regimes.** The amplitude comes from the twin only: its judged yearly lifts, and a
     source outside the judged block that does not move with the model's edge.
     - An example of the outside source: Stage 2's whole-window lift for the twin, disclosed as another population and
       stop and converted to win probability by a declared rule. E-043 vendored it.
     - The power cost is stated: an excess of about the twin's amplitude, or twice it with the symmetric component.
3. **Whichever is chosen, a test at the family level, of level and of power.**
   - The size at C1-f's boundary null.
   - Power non-decreasing in L against an uninformative twin (q = 1/2) and against a twin with a real lift, at least a
     stated share at twice the nominal MDL.
   - The same for the confirmation's form at 126 sessions. My check costs a few minutes on one thread (Appendix).

### M5-2. The pre-judgement amplitude g*_pre = 3 (a) costs most of C1-f's power, and nothing that decides sees it

**Where.**
- Section 12, l. 580-583 ((a) and `g*_pre = 3 (a)`, "fixed now"); section 17, l. 921.
- Section 8 item 8, l. 442-460: the MDL at nominal critical values, the screen rule at a factor of 3, and "a lower bound
  (n4-3) ... the screen rule leans against declaring a screen".
- Section 16, l. 879-890: the confirmation's months at "the larger of 1.3 times nominal and **C1's** stage-C ratio".
- Section 15, l. 838: the close's wording.

**Evidence.**
- The frozen-state argument of M5-1 holds for any g*. At the family level, C1-f's critical value is about
  `4 q g* / SE`, inflated by the block SE.
- (a) is the largest absolute deviation of four noisy yearly lifts from their mean, plus the absolute mean.
  - For a twin with no lift on the pick's offers, (a) is an envelope of sampling noise: about 1.6 yearly standard
    errors.
  - For a twin with lift T, (a) ≥ |T|.
  - Tripled, and then doubled again by the frozen-opposite state, it sets the bar.
- **Toy** (Appendix, check 1, (a) computed as declared on a 4 x 250-session choice block of the twin, at the observation
  sd consistent with the offer level, 0.13 / sqrt(4q)). Uninformative twin, at 0.05/132:

  | L | 0.030 | 0.045 | 0.060 | 0.090 | 0.120 |
  |---|---|---|---|---|---|
  | nominal `cons` | 0.336 | 0.847 | 0.991 | 1.000 | 1.000 |
  | B2 at g*_pre only (or with the twin's (d)) | 0.013 | 0.084 | 0.215 | 0.541 | 0.793 |

  - C1-f's 80 % MDL moves from about 0.045 to about 0.12: about 2.7 times. The screen rule's factor of 3 is spent by
    C1-f alone.
  - With a twin of real choice-block lift T = 0.03 (L 0.06), g*_pre is about 0.11, and the rate is 0.000 even at 0.01.
  - In general the excess must be about `4 q x 3 (a) ≥ 6 |T|` at q = 1/2.
- **The "3" has no derivation and no outside source** (§17 l. 921 cites M4-1, whose remedy said "absolute", not "x 3").
  It was fixed before any family-B read, so it is not a choice made after an outcome. But it is the most consequential
  unlabelled constant in the file.
- **The symmetric component (m4-4)** doubles the frozen shift (`4q` against `2q`). The fourth review called it
  "conservative if the regimes coincide". At the family level it is also a power cost, because its null holds "the
  model's lift sits at 2g* through the whole block", which is a steady edge.
- **Nothing that decides sees any of this.**
  - The stage-A MDL is `mdl_draws("cons")` at nominal values (l. 443-453).
  - The MDL "at stage C's B2 critical values is reported beside once they exist" (l. 454-455): after the judged read,
    too late for the screen rule.
  - The confirmation's months use C1's ratio, whose B2 shift `a* x s_bar` is small for a balanced side. C1-f's ratio is
    several times larger.

**The failure it allows.**
- The family is not declared a screen when C1-f makes it one. A close is then worded against the nominal MDL, a figure
  the line could not reach (l. 838).
- A carried pick's confirmation is bought at a length where C1-f has a fraction of the power the carrying row states.

**Remedy (changes a declared rule).**
1. **Compute the conjunction's MDL before any judged read**, per surviving cell, and set the screen rule and the
   confirmation's months on it.
   - The conjunction is C1, C1-d and each C1-f at B2(g*_pre).
   - The inputs are the choice-block proxies the MDL already uses: the out-of-fold sides and the twins' sides, laid on
     the judged calendar, and (a) on the choice block.
2. **Argue the 3 or drop it.**
   - If (a) is to stand for a regime amplitude, subtract its sampling noise, or state why three envelopes are needed.
   - State the symmetric component's cost at the family level.
3. Report in section 8 the factor by which C1-f's critical value exceeds nominal on the proxies.

---

## MINOR

- **m5-1. The confirmation's level** (§16 l. 860-870; test l. 372-395; `m43_conf.py`).
  - `t21w` at the larger of 1.3 x nominal and B2 holds 0.05 pooled. Per side series the test asserts only
    `max(rates) <= 1.5 x 0.05`, and the drafter's own runs reach 0.0517 and 0.0607.
  - "Each one-sided at the registered 0.05" (l. 856) is therefore the pooled level, not a guaranteed one.
  - The 1.3 was picked by comparing floors of 1.0 and 1.3 on the test's two designs. It is synthetic, so this is not
    selection on an outcome, but it is tuned to the test.
  - E-044's ruling asked for the statistic "calibrated at the window's length or replaced by `cons`".
  - **Remedy.** Either state the achieved bound ("at most 1.5 x 0.05 on the test's designs") in the carrying row and
    the confirmation's registration, or calibrate the floor on a wider declared set of designs (slower drift; `a*`
    short of the drift) to hold 0.05 per series.
- **m5-2. B2's replicate count is open after the judgement** (l. 609, l. 921: "at least 10^6").
  - B2 for C1-f at `g*_post` and for C2 at both routings runs after the judged outcomes (§13 steps 4 and 6).
  - With the seeds fixed, a different count gives a different quantile. At the 0.00038 quantile, 10^6 replications
    leave about 380 exceedances, so a marginal line can flip.
  - **Remedy.** Fix the count exactly (10^6) and the order of the draws.
- **m5-3. B2's tests run at 0.01 and check level only** (test l. 61; §12 l. 611-625; §20 item 8 l. 1021-1024).
  - At 0.01 the frozen state has less mass than the level, so the quantile saturates and the tests cannot show M5-1 or
    M5-2.
  - The build's declared-construction test is also "at 0.01".
  - **Remedy.** Run the declared-construction test at the family's level. Add power assertions (M5-1 remedy 3).

## NOTE

- **n5-1.** E-045 (4) fixes F-02 as k = 11, so this family is k ≥ 12. The level is 0.05/156, and the one-sided t is
  3.842, 4.461 and 5.407 at df 28, 13 and 8, against z 3.414 (my arithmetic). §0 l. 9-10, §8 l. 447-448 and §18 state
  the k = 11 figures. The rule ("the next free") is right; the worked figures will change.
- **n5-2.** §9 l. 482-487 lists what the model's hash holds. Add the partialled reading's 60 x 5 coefficients and
  `z~_res`, which §13 l. 756-758 and §20 item 11 already put there.
- **n5-3.** `m41_d_diag.py` uses `default_rng([T.SEED, 65])` and `[T.SEED, 66]`, the test's own seeds. §19 l. 972
  lists them as the test's only, and the literal grep of l. 975 cannot find them. This is harmless (a scratch
  replicating the test), but the table should say so.
- **n5-4.** The long-run gate floor (§13 l. 742-743) is read from design (i)'s campaign, whose routing M4-2 showed
  selects on same-day outcomes. Under the null this can only flatter the floor. It is Stage 2's floor in Stage 2's
  form, and C1 and C2 at the lesser routing guard the pass. Say it beside the floor.

---

## What I tried that found nothing

- **Post-judgement rules moving a bar the wrong way.**
  - (d) enters only through `g*_post = max(g*_pre, (d))`, and C1-f's critical value is the largest of three. It cannot
    fall.
  - C2 is the lesser of two dollar bounds, so it cannot rise above either.
  - B2's critical value is the larger of nominal and simulated, always.
  - No rule read after the judgement has a branch that lowers a critical value or raises a value. The defects are the
    other way (M5-1, M5-2).
  - The 2026 stub year (about 134 sessions) enters (d) as one year, with no discretion.
- **C2's lesser routing.**
  - Design (ii)'s routing selects on `s' d`, where `s'` is a seeded coin independent of the model's side. Under the
    null the model's `s` is independent of `(s', d)`, so the routed mean of `s d` is unbiased. This is the fourth
    review's check H, now `test_c2_routing_selection_is_why_the_line_takes_the_lesser`.
  - An intersection with design (i)'s bound keeps design (ii)'s level.
  - The trades-a-year multiplier is per routing, and the lesser takes the smaller product.
- **Frozen drift in C1, C1-d and C2.** The same frozen-state mechanism sets C1's B2 shift at `a* x s_bar` (P 0.044 for
  one sign). That is the intended drift guard. C1-d's slow part is `a* rho_t (m_s - s_bar)`, whose frozen mean is
  exactly 0. C2 carries `a*` times its weighted mean side. None of these scales with the edge.
- **The persistence flag.**
  - A permutation of `m` across sessions is an exact null for no serial dependence. The ratio of rolling variances has
    expectation 1/6 under independence (21/126).
  - `m42_flag.py`'s 5.3 % false flags and 0.51-0.77 sensitivity are consistent with the code (it used 400
    permutations, the declaration 2,000).
  - It decides nothing.
- **Look-ahead.**
  - `extended/features.py` is unchanged since the fourth read.
  - The partialled regressors read bars stamped ≤ 09:29, closed by 09:30, before the first alert at 10:05.
  - The twins' timing is per n4-7: `lagged_day_sides` at `t + 5` with L = 5 is the L = 0 side at `t`, and `day_sides`
    at `t` reads bars ending at or before `t`.
  - (d) is read under `stage_C_judgement`, after the sides are hashed (§13 steps 1-4).
- **Leakage across blocks.**
  - (a), `a*`, the partialling OLS, `z~_res`, the MDL's dispersion and the out-of-fold patterns all come from
    2020-2023.
  - The confirmation's B2 resamples 2020-2026, every year of which has been read by then; it chooses nothing.
- **The reads line.** l. 250 matches `reader.py`'s `DECLARED_LINE` and yields `stage_C_sides`, `stage_C_judgement`,
  `stage_C_campaign` and `stage_C_scorecard`. No other line of the file matches, and no purpose contains a
  `CHOICE_WORDS` token.
- **Counts.** 12 cells, 28 searched configurations, 40 in the trial count, 41 columns and 60 alerts, unchanged. At 609
  sessions `block_index` gives 29, 14 and 9 blocks.
- **Seeds.** The test's sub-seeds match §19, 30..32, 40..41, 60..67, 80..85 and 90..95. The new scratch seeds (8101,
  8201, 9101, 9201) lie outside every block.
- **The wrapper.** `cons_bound_with_critical` (test l. 227-240) equals `lift_bound.bound("cons")` at nominal values,
  because `bound` takes the minimum of the three components' lower bounds. A higher critical value lowers the bound.
- **One rule.** §12 l. 579 and §17 l. 921 differ only in a final period.

## What I could not check

1. **The real disagreement shares q between the pick and each twin, and the real ratio of (a) to C1-f's standard
   error.** They set M5-1's and M5-2's sizes on real data.
   - The experiment: on 2021-2023's out-of-fold sides at each surviving cell (a choice read), compute q against
     `lnbar1x4`, `lbrk5` and `mom15`, the twins' four yearly lifts at the cell's offers and bracket, and C1-f's
     per-session sd.
   - Cost: light once the build exists, minutes, no judged read.
   - M5-1's conclusion does not depend on the answer for any q ≥ 1/4 and twin lift ≥ 0.
2. **The declared B2 construction at the family level** (choice-block resampling with the real joint weights, 10^6
   replications). It is heavy and under the lock (§20 item 8).
   - My toy is the draft's own session-level form.
   - The frozen-state lower bound on the critical value comes from the declared Markov processes alone, so it holds
     for any resampled noise.
3. **The real size of C2's routing bias at design (i).** It is moot for the level now that the line takes the lesser.
4. **Q-55's clean rerun of the calibration** (the draft cites none of its figures).

---

## Appendix: the scratch checks (exploratory, synthetic, seeds fixed before running)

Both scripts import `tests/test_family_b_b2.py` (for `markov` and its constants) and `extended.lift_bound` (for
`t_stats` and `block_index`). They read no file and select nothing.

```python
# check 1 (c1f_power.py) -- the draft's toy, C1-f under an alternative
N, Q, SIG = 609, 0.4, 0.13                  # T.FOLLOW_N, T.FOLLOW_Q_DIS, T.FOLLOW_SIG
# B2 null (declared, symmetric): x = 2 Q g (markov - markov) + SIG eps; per-component t by LB.t_stats(block 21/42/63,
#   weight "trades"); quantiles on a grid of g: at 0.01, 4,000 reps per g, seeds [7701, 0, gi]; at 0.05/132, 120,000
#   reps per g, seeds [7702, 0, gi]
# alternative: x = 2 Q (L - Tw) + SIG eps; the model's and the twin's yearly lifts observed with per-session sd SIG_OBS
#   (0.13 = the test's; 0.13 / sqrt(4 Q) = consistent with the offer level); judged years 252 / 252 / 105 sessions
# g_pre: the test's 0.006, or 3 (a) with (a) = max |year - mean| + |mean| over 4 x 250 choice sessions of the twin
# rules: nominal; pre = max(nominal, B2(g_pre)); twin = max(pre, B2(max(g_pre, d_twin)));
#        v5 = max(pre, B2(max(g_pre, max(d_twin, d_model)))); B2 looked up on the grid ROUNDED DOWN
# power: share of replicates where all three components exceed their critical values; 8,000 reps at 0.01 (seeds
#   [7701, 1, i, ...]), 20,000 at 0.05/132 (seeds [7702, 1, i, ...])

# check 2 (c1f_conf_power.py) -- the confirmation: 126 sessions, t21w (df 5), one-sided 0.05; B2 symmetric, 20,000 reps
#   per g (seeds [7703, 0, gi]); floor 1.3 x nominal; g_pre = 3 (a) over 7 x 252 development sessions (noise-only twin);
#   (d) over the window's one year; 20,000 reps per L (seeds [7703, 1, i])
```

Printed (check 1, abridged to the lines cited; L the model's lift, Tw the twin's; "t63 median" the alternative's):

```
C1-f per-session sd 0.130, SE over 609 sessions 0.00527; q 0.40
B2 (symmetric) quantiles at 0.01, t21w/t42w/t63w:
   g 0.000: [2.45 2.72 3.04]      g 0.012: [4.11 4.11 4.22]     g 0.032: [7.81 7.61 7.14]
   g 0.060: [11.08 8.96 8.66]     g 0.120: [13.48 10.63 9.67]
nominal at 0.01: [2.467 2.65  2.896]
-- alpha 0.01, obs sd 0.103 (offer-consistent), g_pre test
   L 0.020 Tw 0.000 (t63 median  3.16): nom 0.525 | pre 0.440 | twin-only d 0.253 | v5 0.0088
   L 0.030 Tw 0.000 (t63 median  4.73): nom 0.907 | pre 0.866 | twin-only d 0.636 | v5 0.0084
   L 0.045 Tw 0.000 (t63 median  7.14): nom 1.000 | pre 0.999 | twin-only d 0.954 | v5 0.0135
   L 0.060 Tw 0.000 (t63 median  9.51): nom 1.000 | pre 1.000 | twin-only d 0.996 | v5 0.0684
   L 0.090 Tw 0.000 (t63 median 14.30): nom 1.000 | pre 1.000 | twin-only d 1.000 | v5 0.5071
   L 0.060 Tw 0.030 (t63 median  4.70): nom 0.911 | pre 0.870 | twin-only d 0.008 | v5 0.0001
-- alpha 0.01, obs sd 0.103 (offer-consistent), g_pre 3a
   L 0.060 Tw 0.030 (t63 median  4.73): nom 0.916 | pre 0.000 | twin-only d 0.000 | v5 0.0000   [g_pre 0.1126]
B2 (symmetric) quantiles at 0.05/132 (120,000 replicates each):
   g 0.000: [3.84 4.29 5.24]      g 0.010: [5.66 6.35 7.33]     g 0.020: [ 8.66  9.39 11.18]
   g 0.030: [11.72 13.8  15.12]   g 0.060: [21.79 24.78 27.87]  g 0.120: [43.45 47.29 51.87]
nominal at 0.05/132: [3.779 4.371 5.268]
-- alpha 0.05/132, obs sd 0.103, g_pre test
   L 0.030 Tw 0.000 (t63 median  4.75): nom 0.338 | pre 0.336 | twin-only d 0.194 | v5 0.0001
   L 0.045 Tw 0.000 (t63 median  7.13): nom 0.850 | pre 0.849 | twin-only d 0.617 | v5 0.0000
   L 0.060 Tw 0.000 (t63 median  9.50): nom 0.990 | pre 0.990 | twin-only d 0.882 | v5 0.0000
   L 0.090 Tw 0.000 (t63 median 14.27): nom 1.000 | pre 1.000 | twin-only d 0.991 | v5 0.0000
   L 0.120 Tw 0.000 (t63 median 19.01): nom 1.000 | pre 1.000 | twin-only d 0.999 | v5 0.0000
-- alpha 0.05/132, obs sd 0.103, g_pre 3a
   L 0.030 Tw 0.000 (t63 median  4.73): nom 0.336 | pre 0.013 | twin-only d 0.010 | v5 0.0000   [g_pre 0.0299]
   L 0.045 Tw 0.000 (t63 median  7.08): nom 0.847 | pre 0.084 | twin-only d 0.078 | v5 0.0000   [g_pre 0.0302]
   L 0.060 Tw 0.000 (t63 median  9.47): nom 0.991 | pre 0.215 | twin-only d 0.208 | v5 0.0000   [g_pre 0.0302]
   L 0.090 Tw 0.000 (t63 median 14.22): nom 1.000 | pre 0.541 | twin-only d 0.539 | v5 0.0000   [g_pre 0.0300]
   L 0.120 Tw 0.000 (t63 median 18.99): nom 1.000 | pre 0.793 | twin-only d 0.793 | v5 0.0000   [g_pre 0.0302]
```

Printed (check 2):

```
t21w df 5, nominal 2.015, 1.3 x nominal 2.620
L 0.000 (t21 median 0.02): 1.3 x nominal 0.025 | pre 0.003 | twin-only d 0.003 | v5 0.0031  [g_pre 0.0355]
L 0.040 (t21 median 2.92): 1.3 x nominal 0.587 | pre 0.132 | twin-only d 0.132 | v5 0.0643  [g_pre 0.0354]
L 0.060 (t21 median 4.44): 1.3 x nominal 0.899 | pre 0.350 | twin-only d 0.350 | v5 0.0728  [g_pre 0.0354]
L 0.090 (t21 median 6.68): 1.3 x nominal 0.998 | pre 0.687 | twin-only d 0.687 | v5 0.0580  [g_pre 0.0354]
L 0.120 (t21 median 8.80): 1.3 x nominal 1.000 | pre 0.879 | twin-only d 0.879 | v5 0.0562  [g_pre 0.0354]
L 0.180 (t21 median 13.34): 1.3 x nominal 1.000 | pre 0.992 | twin-only d 0.992 | v5 0.0531  [g_pre 0.0354]
frozen over 609 sessions: 0.0874 (one process); 0.00191 (both, in opposite states, the upper one); level 0.000379
frozen over 126 sessions: 0.6059 (one process); 0.0918 (both, opposite, upper); level 0.05
```
