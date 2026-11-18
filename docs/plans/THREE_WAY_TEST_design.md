# The three-way test: design note (Q-153; the restart plan's Wave 3.2, first part)

Drafted 2026-11-18 on `wt/wt-verify` for the lead and the red team. **Status: a design note, not a declaration.**
Nothing here is pinned, built or run. H3's declaration takes its rules from this note, after the red team's read. No
result number: every figure below is printed by `docs/plans/scripts/three_way/three_way_arith.py` from declared
constants and the calendar (Appendix A, held to the script line for line by `tests/test_three_way_design.py`). No bar
and no outcome was read to write it. The only result file opened was `results/calibration_p.csv`, for its header row.

**Sources.**
- The restart plan, sections 4.5 to 4.8 (`docs/plans/RESTART_PLAN_journey_objective.md`).
- The amendments draft, CHARTER 3.6 to 3.9 (`docs/plans/AMENDMENTS_draft_2026-11-18.md`, corrective cycle 2): the
  martingale-outcome reading, the history null, the antithetic and disjoint-seed nulls, the power gate, the fixed
  sequence, and the scope of the level (coin luck only).
- E-208's design brief for the test (time legs as consistency conditions; the minimum-units arithmetic).
- The triage's section 3.2 (`docs/plans/TRIAGE_2026-11-18.md`): the reusable pieces.
- `extended/p_bound.py`, `extended/family_stats.py`, `results/calibration_p.csv`'s header (columns only), and Q-16's
  and Q-55's rows (E-035, E-083, E-085).

**The note in brief.**
- **Leg (i), the coin-seed leg, carries the level.** Given the held-out history, disjoint seed sets give exactly i.i.d.
  replicates. So a finite-sample bound for bounded i.i.d. means is valid **on every history by theorem**. The full
  level cannot be certified by simulation (Appendix A: the rule of three). H3 checks the theorem's premises on many
  histories and checks the size at the levels a simulation can certify.
- **The two same-design nulls are symmetric by construction**, so neither can show a skew-driven laxity. A third null
  is added: two different designs on toys whose exact expectation comes from dynamic programming, centred by it.
- **The history null is exact for any functional, quantiles included**, when it is built from a symmetry of the history
  generator (D against D composed with the symmetry). This settles flag R-11 for the null's construction. What remains
  open is only how realistic the generator is.
- **The years and held-out legs cannot reach the level.** On the weekday bound, the held-out years hold at most ten
  disjoint 63-session units, and twelve are needed (Appendix A). The legs are written below as exact consistency
  conditions, each with its stated size.

---

## 1. The statistic

### 1.1 The reading and the notation

Every quantity below is read on **the martingale-outcome reading** (CHARTER 3.2):
- each trade's outcome is redrawn at its own bracket's driftless first-exit odds (a target of g ticks and a stop of l
  ticks give a win probability of l / (l + g)), stage one's `adapter.BinaryDraw` form;
- the redraw for a time-limited trade is the search template's (flag R-10), with zero gross expectation;
- fills, timing, costs and resolution are as run;
- the design and every baseline are read the same way, with the same seed keying.

The as-walked and as-traded results are computed on the same seeds and reported beside. They are never tested.

| symbol | meaning |
|---|---|
| H | the held-out history (NQ 2024-01-02 to 2026-07-16 on `results/q82_judged_sessions.csv`), fixed |
| N_H | its session count. It is at most W_H, the weekday count of its dates (Appendix A) |
| h_d | dimension d's horizon in sessions (21 a month); h\* = the largest h_d in the composite (63 for the fallback) |
| T_h | the held-out starts complete at h (3.6 (d)'s embargo): N_H - h + 1 of them |
| U | the coin field: i.i.d. uniforms U_kappa on (0, 1), one per key kappa (section 1.5) |
| s, S | one coin seed; a set of seeds |
| f, beta | a finalist (design); a baseline (naive coin, P-14, P-15, P-16) |
| a(x, t, s) | the fallback's per-journey value of design x started on t under seed s (1.2) |
| C(x; S) | the composite of x over the starts and the seeds in S (1.3) |
| alpha | the family level 0.05 / (k (k + 1)); k = 13 next |

### 1.2 The fallback (P under the bankroll stop): per start, per seed

The per-journey value is the ahead average under the bankroll stop. `extended.user_measures.p_by_month` computes it
with `spent` and `limit`, one start at a time:

    a(x, t, s) = (1/3) * sum over m = 1, 2, 3 of 1[ net_m(x, t, s) > 0  and  spent_m(x, t, s) <= limit ]

Here net_m is the net cash at month m (21 m sessions), and spent_m is the cash spent before the first payout as
month m's reading reads it. Wave 3.1's bankroll stop may stop a user's purchases at the budget. If it does, net_m and
spent_m are read from that journey, and the formula is the same.

- **Per seed:** Delta_s = (1 / |T_63|) * sum over t in T_63 of [a(f, t, s) - a(beta, t, s)].
- **Per start day:** delta_t = (1 / |S|) * sum over s in S of [a(f, t, s) - a(beta, t, s)].
- **The estimate:** Delta-bar = the mean of Delta_s over S, which equals the mean of delta_t over T_63.

P is a mean. A seed set of m seeds therefore gives the mean of its m values of Delta_s, so for the fallback the
replicate can be the single seed (m = 1) with no loss.

### 1.3 The composite: per seed set, and per start beside

The composite is pinned in Wave 4.2:

    C(x; S) = sum over d of w_d * g_d( Phi_d( F_{x, d, S} ) )

- F_{x, d, S} is the empirical distribution of dimension d's per-journey value over the pairs (t, s) in T_{h_d} x S.
- Phi_d is the dimension's functional (a mean, a share, a median, a p10, ...).
- g_d is its pinned normaliser, and w_d its weight.

- **Per seed set:** Delta_j = C(f; S_j) - C(beta; S_j), for disjoint seed sets S_1, ..., S_J of m seeds each.
- **The estimand:** theta_m(H) = E[ Delta_j | H ], the expectation over the coin field. Where some Phi_d is not a mean,
  theta_m depends on m, by order 1 / (m |T|). **m is pinned with the composite.** The plug-in over all J x m of the
  test's seeds is reported beside.
- **Per start day (beside only):** delta_t^C = sum over d of w_d * g_d' * [psi_d(f; t) - psi_d(beta; t)], averaged
  over the seeds. psi_d is the dimension's influence function: x - mu for a mean; the indicator less the share for a
  share; (q - 1[x <= xi_q]) / f-hat(xi_q) for a q-quantile. It shows which start days drive a difference, and it feeds
  `user_measures.n_eff_bartlett` at lag h\*. It decides nothing.

### 1.4 The hypothesis, per pair

For each finalist f and each baseline beta, on the held-out history:

    H0(f, beta):  theta_m(H) <= 0        against        H1(f, beta):  theta_m(H) > 0

f beats the baseline set when every H0(f, beta) is rejected at the full level alpha (an intersection-union test,
CHARTER 3.8 (b)). **The level bounds coin luck given H. It does not bound a favourable H** (section 2.7).

### 1.5 The seed keying (what "paired" means)

- **Every random element of a journey is a fixed function of the coin field U.** That covers the reflection coin, the
  outcome redraw, missed-signal draws (measure 28's stress), any tie-break and any account rotation that draws.
- Each draw takes U_kappa at a key kappa = (seed, start day, decision moment, draw kind), through a counter-based
  keyed generator. Distinct keys give independent uniforms. The build declares the generator exactly.
- **The design and every baseline use the same keying.** Two arms deciding at the same moment on the same start under
  the same seed read the same uniform. That is the pairing, and it is where the paired variance reduction comes from.
- **Uniforms lie on the symmetric grid** (2i + 1) 2^-53, for i = 0 .. 2^52 - 1: odd multiples of 2^-53, each exact in
  float64. 1 - U is then (2 (2^52 - 1 - i) + 1) 2^-53, again on the grid and computed exactly, so the antithetic twin
  of 2.3 is exact in floating point too. (A grid of (i + 1/2) 2^-53 over i < 2^53 would need 54 bits, and is not
  representable.) Every threshold is written `U < p`.
- **Each user (start) has its own coin draws** (the key carries the start day). The other reading -- one draw per
  calendar moment shared by every start -- is admissible. It does not change the validity of 2.2, only the variance
  per seed. **It is a choice for the red team.**

---

## 2. The coin-seed leg

### 2.1 The replicates are seed sets

- **Given H, the replicates Delta_1, ..., Delta_J are exactly i.i.d.** The sets S_j are disjoint, so their keys are
  distinct and their coin fields independent. The same map from field to journey applies to each set.
- No approximation enters. Whatever dependence the journeys carry across start days (overlapping windows, shared
  calendar moments) stays **inside** a replicate.
- **This is why the overlap problem of Q-16 (section 3.1) does not reach leg (i).** Its unit is the seed set, not the
  start day.
- The test's seed sets are declared by the search's declaration. They must be disjoint from every seed drawn on the
  search years. (The keys differ anyway, because the start days differ; disjoint seeds make the independence plain.)

### 2.2 The deciding bound: valid on every history by theorem

**The pinning row is asked to make the composite bounded:**
- each g_d maps into [0, 1], with fixed caps set from the search years;
- the weights sum to one.

Then C lies in [0, 1] and Delta_j in [-R, R] with R = 1. The fallback is bounded as it stands (a lies in [0, 1]).

**The deciding statistic (proposed): the one-sided empirical-Bernstein lower bound** (Maurer and Pontil 2009, theorem
4), applied to (Delta_j + R) / (2R) and mapped back:

    LB = Delta-bar - sqrt( 2 V ln(2/alpha) / J ) - (7 ln(2/alpha) / 3) * 2R / (J - 1)

V is the unbiased sample variance of the Delta_j. H0(f, beta) is rejected when LB > 0. Given H,
P(LB > theta_m(H)) <= alpha **for every J, every history and every shape of the replicates' distribution.** The size
therefore holds conditionally on every H, and so across histories too. The constants at k = 13 are in Appendix A.

**Beside, deciding nothing:**
- the studentised mean with E-035's larger-of critical value (the larger of t(J - 1) and the calibrated quantile from
  the H3 nulls, `family_stats.critical`'s rule);
- the hedged betting bound (Waudby-Smith and Ramdas, JRSS-B 2024), which is tighter than the empirical-Bernstein bound
  and equally valid, but harder to audit.

**Why not the t.** Its size at alpha depends on the replicates' skewness, which varies by history. Certifying alpha
empirically needs more independent full replications per history class than the machine can run (Appendix A: the
rule-of-three line at alpha). The price of exactness is a larger J for the same power (Appendix A: the
replicates-per-(sigma/delta)^2 line and their ratio). Seeds are unlimited, so that price is paid in compute, not in
validity.

**If the pinning row cannot bound the composite,** the empirical-Bernstein bound does not apply. The t with the
larger-of rule then decides, and its size at alpha rests on the size check of 2.6 at feasible levels only. **This must
be printed beside the verdict.**

### 2.3 The same-design nulls (exact)

**(a) The antithetic twin: the complement of every random draw, the redraw included.**

The twin of design x is the same code run on U\* = 1 - U, every key's uniform complemented. That includes:
- the reflection coin: side = 1[U < 1/2], so the side is reversed;
- the outcome redraw: a win is 1[U < p], so the twin's win is 1[U > 1 - p];
- every other draw.

*Exactness.* U\* has the same law as U, and the pair (U, U\*) has the same law as (U\*, U). So the pair
(C(x; U), C(x; U\*)) is exchangeable given H, and Delta = C(x; U) - C(x; U\*) is **symmetric about zero, with mean
exactly zero**. This holds for any functional (C is bounded), for every entry type and for every history. On the grid
of 1.5 it holds bit for bit.

*Note on the charter's words.* CHARTER 3.7 says "every coin side reversed". For the side coin that is exactly the
complement. **For the redraw it is not:** reversing the outcome (a win made a loss) turns the win probability p into
1 - p. Unless p = 1/2, that changes the law and breaks equal expectation. The complement acts on the uniforms, never
on the outcomes. A build that reverses outcomes is a defect, and this null catches it: its mean would not be zero.

*Resting entries.* The deciding reading removes direction by the reflection coin after the real fill, so the twin is
exact for every entry type. The triage's caveat (the twin exact only at RL3's same-bar mirror) applies only to the
as-traded reading, which draws no side coin. That reading is beside, never tested.

**(b) Disjoint seed sets.** The same design on S_j and on S'_j, with every seed of the S sets distinct from every
seed of the S' sets: Delta_j = C(x; S_j) - C(x; S'_j). The two terms are i.i.d. given H, so Delta_j is symmetric with
mean exactly zero.

**What each null catches, and the guards against degeneracy.**
- (a) catches a draw mapped asymmetrically: an outcome reversed instead of its uniform complemented; a `<=` against a
  `<`; a non-uniform primitive the twin does not complement.
- (b) catches reused streams and key collisions. Two arms that share draws give Delta_j identically zero, which never
  rejects: a meaningless "pass".
- **Guards, refused before any rate is read:**
  - a null pool whose Delta_j are all zero;
  - a disjoint pool whose variance is outside a declared tolerance of twice the single arm's variance;
  - any key shared between the S sets and the S' sets (checked on the key lists, not on outcomes).

### 2.4 A third coin-seed null: exact centring on toys (asymmetric)

Both same-design nulls are symmetric. So they cannot show the one failure that matters for any non-exact statistic:
laxity driven by skewness. A null with the asymmetry of two genuinely different designs is needed:
- **Toys whose expectation is exact.** The histories are schedule-level (2.6): each session's trades with their
  times, brackets in tick units, resolution and costs. One to three accounts have balances on a lattice of ticks.
- On the martingale-outcome reading, each start's E[a(x, t, s) | H] is computed exactly by forward dynamic programming
  over the state along the schedule: account state, balance, cash spent, payouts, and the month-end readings.
- Two different designs x1 and x2 (different brackets, sizes or purchase rules) then give theta(H) exactly. The
  centred replicates Delta_j - theta(H) are an exact mean-zero null with x1 and x2's real skew.
- The toys use only trades that resolve at a barrier until the template fixes the time-limit redraw (R-10). After
  that, they use its form.
- For composites with quantile-type dimensions, the DP does not give theta_m exactly. Those are centred instead by a
  pool of independent seeds, at least a hundred times J. The pool's own error is reported, and **that null is labelled
  approximate**.

### 2.5 How many replicates (arithmetic)

The empirical-Bernstein bound rejects at true difference delta with probability about

    Phi( sqrt(J) delta / sigma  -  c1  -  c2 * 2R * sqrt(J) / (sigma (J - 1)) )

where sigma is the replicates' standard deviation, c1 = sqrt(2 ln(2/alpha)) and c2 = 7 ln(2/alpha) / 3.

- **The variance term:** for power pi, J is about (c1 + z_pi)^2 (sigma / delta)^2.
- **The range term:** it stays below a share of delta only when J >= 1 + 2 c2 / (share x delta / R).
- Appendix A gives c1, c2, the factor (c1 + z_pi)^2, the normal t's factor and their ratio, and the range term's J for
  three illustrative values of delta / R.
- delta is the operator's (O-3), so those values only show the formula.
- sigma comes from the same-design pools on the toys (H3-A) and from H4's per-seed outputs (H3-D).

### 2.6 The size check across histories, not on one history

The size of leg (i) is a statement for each history. The check therefore runs over many histories and reports them
one by one as well as pooled.

**History classes.**
- **S1, synthetic schedule histories.** On the deciding reading, a history acts on a journey only through its schedule
  of trades: when, which bracket, how long to resolve, and at what cost. Outcomes are redrawn. So a synthetic history
  can be a schedule, with NQ's dependence carried by the schedule's dependence:
  - volatility persistence and regime switches (`family_stats.slow_sign` and `slow_two_state`, or a log-AR(1));
  - signal arrivals whose rate follows volatility (clustering);
  - brackets in volatility units with dollar caps (RD-04's units);
  - resolution times that lengthen with the bracket over volatility.

  Parameters are stylised in H3-A and fitted on **the search years only** in H3-D.
- **S2, symmetrised block resamples of the search years (H3-D only).** Search-year days are resampled by the
  stationary bootstrap (`family_stats.stationary_indices`), with a mean block at least h\*. For the history null (2.7)
  only, each resampled block also takes a symmetry with probability one half, by a declared coin. **Never the held-out
  years:** the runner refuses them.

**What is checked on each history r = 1 .. R, for each null class (antithetic, disjoint, exact-centred):**
1. *The premises of 2.2*:
   - the pool's mean is consistent with zero (a z-test at a feasible level, with the pool's own sd);
   - symmetry, for (a) and (b) (a sign test);
   - no serial dependence of the replicates in seed order (lag-one autocorrelation);
   - every Delta_j inside [-R, R].
2. *The procedure's size at the feasible levels* alpha' in {0.05, 0.01, 0.001}:
   - the history's pool of M replicates is cut into floor(M / J') disjoint groups of J' (declared), one null test per
     group;
   - the rejections are counted.
3. *The rate at alpha itself*: counted and printed. It cannot be certified (below).

**The criterion is E-052's** (`lift_bound.clopper_pearson`; `scripts/q108_validate.py`'s `criterion`): no null's 95 %
Clopper-Pearson interval lies wholly above nominal.
- It is applied pooled over the histories of a class, and per history at confidence 1 - 0.05/R (Bonferroni over the
  histories).
- **A level counts as certified** only where the pooled count of null tests, R x floor(M / J'), reaches the rule of
  three's n at that level (Appendix A). Below that n it is reported, never claimed.
- At alpha itself, n is beyond reach. **The full level is carried by the theorem of 2.2, and this check confirms the
  build meets the theorem's premises.**

**The whole rule** is leg (i) and the time conditions and the limits and the floors (CHARTER 3.7, "calibrated as a
whole"). It rejects a same-design null no more often than leg (i) alone does, because a conjunction only removes
rejections. Its rate is printed beside leg (i)'s.

### 2.7 The history null

**What it measures.** The level is conditional on H. A design no better than the baselines across histories, whose
shape happens to suit H, passes leg (i) correctly given H and falsely across histories. The history null puts a
number beside every verdict for that risk (CHARTER 3.7, 3.8 (b)).

**Construction from a symmetry of the generator.**
- Let G be a history generator, and sigma a bijection of histories with sigma(H) distributed as H under G.
- For any design D, define D' as "D acting on sigma(H)": D'(H) = D(sigma(H)) as whole journeys, with the coin keys
  mapped by the same bijection, which leaves the coin field's law unchanged.
- Then for **any** functional C, quantiles included:

      C(D'; H) = C(D; sigma H),   so   E_H[ C(D'; H) ] = E_H[ C(D; sigma H) ] = E_H[ C(D; H) ]

- The two designs are equal on average over histories, **exactly**. On any one history they differ. Write
  theta_pair(H) = E[ C(D'; H) - C(D; H) | H ]. For an involution sigma, theta_pair(sigma H) = -theta_pair(H). Exactness
  needs only two things:
  - sigma preserves G's law;
  - sigma leaves the start-day set and the embargo unchanged. Every symmetry below acts within a day, so it does.

  **This settles R-11 for the null's construction.** What stays open is the generator's realism, not exactness.

**Three symmetries, with known truth.**
1. **The session swap.** G gives two declared sessions the same law, and is invariant to swapping them: each day's
   two schedules are i.i.d. given a common daily volatility factor. D puts component A in session one; D' puts it in
   session two.
   - Every rule the journey reads must treat the two sessions alike: one position at a time, flat between them, the
     same distance to the daily close in the toy.
   - Otherwise the swap is not a symmetry. The build asserts it on the toy's rules.
2. **The mirror.** G's price innovations are symmetric: no drift, symmetric shocks, volatility independent of the
   sign. sigma reflects each session's path about its open. D' mirrors every price-level trigger (a break up for a
   break down, a fade of the high for a fade of the low).
   - Under zero edge the sides are coins, so D and D' differ only in timing: which levels fire.
   - These are the charter's "mirrored schedules".
3. **Symmetrised resamples (S2, H3-D only).** Resampled search-year blocks, each mirrored with probability one half by
   a declared coin. The resample law is then mirror-invariant by construction, so D against D' is exact over it,
   though the real data are not mirror-symmetric.

**The known truth.** On the DP toys of 2.4, theta(H) for the pair (D, D') is computed exactly on every history. Each
false pass then splits into two kinds:
- **coin luck:** theta(H) <= 0, and the rule passed;
- **history luck:** theta(H) > 0, and the rule passed. Correct given H, false across histories.

The level bounds the first kind; the printed rate is mostly the second.

**The history-level false-pass rate.** It is FPR_hist = P over H drawn from G that the whole pinned rule passes D' over
D, averaged over both orientations. It is estimated over R histories with its Clopper-Pearson interval. It is printed
beside every verdict, with the pair's spread sd_H(theta(H)) over delta\*, because the rate depends on that spread.
- The pairs are built from **each finalist's own components** wherever the generator can carry them, and from stylised
  pairs otherwise. So the rate is printed per finalist.
- *The computation.* On each history, a pool of M seeds estimates theta-hat(H), sigma-hat(H) and the per-year and
  per-regime differences (the time conditions of 3.4). The coin leg's pass probability at the test's J is computed
  from them by 2.5's formula, and multiplied by the time conditions' indicator.
- A declared subset of histories is run in full at the test's J, to check that shortcut.
- On a symmetric pair, FPR_hist tends to the share of histories on which the time conditions hold with theta(H) > 0.
  **That is why the time conditions (section 3) are the defence against history luck, and why their stated size is
  reported.**

---

## 3. The years leg and the held-out leg

### 3.1 The unit: history blocks, calibrated per horizon

- The time legs' unit is a **history block** at least as long as the composite's longest horizon h\*. Only adjacent
  blocks then share sessions, and they share h\* - 1 of them.
- A start's window covers h_d sessions, so neighbouring starts' windows overlap in h_d - 1 sessions.
- **Q-16's finding** (`docs/research/calibration_2026-11-15.md` 7.2 and 7.4; the rows of `results/calibration_p.csv`,
  whose columns -- `null, kind, pair, form, L, method, level, k, reps, rejections, rate, ci_lo, ci_hi, ratio, model,
  stage` -- are the template for H3's size tables): every batch-type variance on P's start-day series is biased low,
  because of that overlap. `pcons` held its level but detected almost nothing. `bm63c` was not adopted (E-085).
  Month-6 and month-12 measures overlap over 126 and 252 starts, which is worse.
- **Calibration per horizon** therefore means:
  - every statement about a time leg (its stated size, any interval reported beside) is computed at each dimension's
    own h_d, never at a pooled 63;
  - the stationary bootstrap's mean block is at least h\*. The recorded caution applies: a slow drift resampled in
    short blocks under-covers (`tests/test_family_stats.py`'s strict `xfail`);
  - an interval beside uses a variance whose window is at least h_d: `p_bound.flat_top` with FLAT = h_d and
    TAPER = 2 h_d, batches of at least h_d starts, `user_measures.n_eff_bartlett` at lag h_d. Its fixed-b critical
    values are simulated for each (n, h_d), as `p_bound._ft_null` is for 63. **`p_bound.HORIZON` (63) becomes each
    measure's horizon** (the triage's note);
  - `results/calibration_p.csv`'s null classes (real paired start-day nulls; synthetic moving-average and structural
    nulls) are the starting null class for those intervals. They are read as a calibration, never as outcomes.

### 3.2 The minimum-units arithmetic

- **An exact sign-flip test over B independent units** (`lift_one_sample.exact_flip`, `flip_blocks`, `pattern_signs`)
  has 2^B equally likely sign patterns under its null. Its smallest attainable p-value is 2^-B. It can reject at alpha
  only if 2^-B <= alpha, that is B >= B_min = ceil(log2(1/alpha)).
- **At k = 13**, alpha lies between 2^-12 and 2^-11, so B_min = 12. At k = 14 to 17, B_min = 13 (Appendix A).
- **What the held-out years hold.** The weekday count W_H is an upper bound on N_H (no session list is read). Units
  whose windows share no session number at most floor(W_H / h): see Appendix A for h = 21, 63, 126, 252.
  - **At every horizon from 63 sessions they are fewer than twelve.** The fallback's own horizon is 63 (months 1-3),
    so no composite that contains P can give the time legs twelve units.
  - Blocks of h consecutive complete starts are fewer still (Appendix A, `blocks_H`).
  - Twelve disjoint 63-session units need 12 x 63 = 756 sessions: three years of 252, more than the two and a half
    years the held-out dates span.
- **The search years** hold more units (Appendix A, `units_S`), but they are the search's own. A test there is not a
  held-out test.
- **For the lead (a correction to the record's wording, not to its conclusion):** E-208 says the held-out block holds
  "about a dozen 63-session units". On the weekday bound it holds at most ten complete disjoint ones, or eleven
  counting a partial one. The conclusion -- the time legs cannot carry the level -- holds a fortiori.

### 3.3 Why the time legs are consistency conditions

1. **No exact test can reach alpha** on them (3.2).
2. **No asymptotic test can be calibrated there.**
   - With ten units at most, a HAC or batch t's reference distribution is the fixed-b one, at a bandwidth near the
     sample's length. Its tail at alpha is extremely sensitive to the dependence model.
   - Q-16 found batch t's lax on these series at 63 even with nine batches.
   - Certifying such a test at alpha would also need the rule of three's n of independent histories (Appendix A).
3. **They cannot raise the size.** The rule is the conjunction of leg (i) and these conditions, and a conjunction
   rejects no more often than leg (i). So the level stays leg (i)'s. Their job is to lower the history-level false-pass
   rate (2.7), and they are judged by their stated size.
4. **Their stated size** is P(conditions hold | no difference) under a declared model of the history.
   - With B independent, symmetric blocks: P(all B positive) = 2^-B, and P(at least n of B positive) is a binomial
     tail (Appendix A's table, B = 1 to 10).
   - Adjacent blocks share h\* - 1 sessions, so the real stated size is larger. It is computed per horizon on the
     history null's generator (2.7) and printed beside the verdict.

### 3.4 The conditions, written exactly

Each condition is read for every pair (f, beta), on the martingale-outcome reading, at the point estimate pooled over
**all** the test's seeds. Coin noise inside a block is then small: its standard error over sqrt(J m) is printed beside.

**(Y) Most years.**
- The blocks are the calendar years of the start dates, y in {2024, 2025, 2026}. A full year is twelve months of 21
  sessions in the charter's convention, so it is at least h\* for every horizon up to 252 and meets 3.1's length.
  2026 is a part-year, held to n_min like any other.
- T_y = the starts of year y complete at h\*. Y_ok = the years with |T_y| >= n_min, where n_min is pinned.
- Delta-hat_y = C(f; T_y, S_test) - C(beta; T_y, S_test): the composite on year y's starts only, every dimension on
  its own complete starts within T_y.
- **(Y) holds when #{ y in Y_ok : Delta-hat_y > 0 } >= n_Y**, where n_Y is "most years", pinned in 3.9.
- With 252-session dimensions in the composite, 2026 holds no complete start, so Y_ok has at most two years and
  "most" means both. The pinning row states n_Y for the composite's actual h\*.

**(R) Both regimes.**
- Each held-out start t takes the regime rho(t) = volatile if v(t) > v\*, else calm.
  - v(t) is its causal volatility measure in RD-04's unit. Its look-back may enter the search years (3.6 (d)).
  - v\* is a threshold fixed from the search years only, by a rule pinned in 3.9 (for example the search years' median
    of v).
- T_r = the complete starts of regime r; R_ok = the regimes with |T_r| >= n_min.
- **(R) holds when Delta-hat_r > 0 for every r in R_ok.** A regime outside R_ok is reported beside, not required
  (CHARTER 3.6 (f) (ii)).

**(H) The held-out leg.** Leg (i), (Y) and (R) read only:
- held-out starts complete at their horizon;
- outcomes from held-out sessions (from 2024-01-02, before 2026-07-17);
- search-year sessions only for causal normalisers.

The runner refuses any other start or session (RD-04's guard pattern). (H) is a scope condition, enforced
mechanically. It carries no statistic of its own.

**The rule for one pair:** LB > 0 (leg (i)) and (Y) and (R) and (H). Then, for the finalist, all four baselines, with
the limits and the floors of CHARTER 3.8 (a) and (c).

### 3.5 Reported beside, deciding nothing

- Per year and per regime: Delta-hat with its coin-noise standard error.
- The exact sign-flip p-value over the B complete blocks of length h\*, with its floor 2^-B printed next to it.
- For the fallback: the P comparison's interval with the per-horizon variance of 3.1.
- The stated size of (Y) and (R) from the history null, per horizon.

---

## 4. The power check

### 4.1 The parameters

| parameter | class | value or source |
|---|---|---|
| delta\*, "the size that matters", on the composite's scale | fixed, the operator's (O-3, Wave 4.2) | **a parameter here** |
| pi\*, the power target | fixed in 3.9's pinning row | proposed: the repository's convention (`family_stats.MDL_POWER`, Appendix A's `z_0.8`) |
| alpha | fixed | 0.05 / (k (k + 1)) at the search's k |
| J, m (replicates, seeds per set) | searched in H3-A, fixed in H3's declaration | set from 2.5's formula, so that power at delta\* reaches pi\* |

### 4.2 The plants

Each plant is an improvement whose true size on the composite is known. Its power is the whole rule's rejection rate
at the plant whose true size is delta\*.
- **P1, linear** (the statistic alone): Delta_j + delta added to the null replicates. The power is exact in the shift.
  `family_stats.conjoint_mdl_linear` gives each line's MDL and the conjoint one.
- **P2, structural** (zero edge kept): a design better by construction in what the composite rewards -- an evaluation
  fee lowered, a payout delay shortened, a cheaper purchase rule -- with no trade outcome touched. The true delta comes
  from the DP toys or from a pool of at least a hundred times J.
- **P3, edge plants** (zero edge broken on purpose):
  - the redraw's win probability raised by epsilon at every trade;
  - F-04's value arm, every executed trade's dollar P&L shifted by a declared amount (E-208's disposition).

  Each is mapped to the composite's scale by the pool.
- **P4, a plant that varies by regime:** delta_t = delta\* (1 + a rho_t), with rho_t a slow sign
  (`family_stats.slow_sign`, or `lift_one_sample2.drift_draw`'s 63-session switching). It shows what (Y) and (R) cost
  when an improvement is not uniform across years and regimes. a runs over a declared grid, and a > 1 lets the sign
  switch.

**The MDL of the whole line.** `family_stats.conjoint_mdl_grid` gives the smallest delta on a declared grid at which
at least pi\* of the draws pass every leg together: LB > 0 and (Y) and (R) and the limits and the floors. **The line
has power at delta\* when that MDL is at most delta\*.**

### 4.3 On synthetic plants and on H4's baselines

- **H3-A (design checks, toys).** P1 to P4 on S1 histories with stylised parameters. They test the statistic, the
  replicate structure (m, J) and 2.5's formula against simulation.
- **H3-D (the deciding power gate, after H4 and the pinning row).**
  - H4's per-seed outputs of the four baselines on the search years supply the real sigma of each baseline pair's
    replicates, their cross-correlations and their shapes.
  - The planted finalist is the best baseline plus a plant of size delta\*, compared with all four baselines (the
    intersection-union test).
  - Its power is computed from 2.5's formula with H4's sigma. It is checked end to end by P2 and P3 plants on S1
    histories fitted to the search years, and on S2 resamples.
  - The held-out years are read by none of this.

### 4.4 The gate's other clauses (CHARTER 3.7)

- **The limit clause** (E-015's condition). In the form in force, a ceiling L passes when M-hat + w <= L, with w the
  coin-noise half-width at the margin's pinned level. A floor is the mirror image.
  - A design equal to the best baseline (M = M_best) passes with probability at least pi\* only if the headroom
    L - M_best is at least about (c_L + z_pi) sigma_M / sqrt(J).
  - The gate prints that headroom per limit, and fails if any pinned limit lacks it.
  - **Whether "its noise" is coin noise only, or also history variation, is a choice for the red team.** With history
    variation the margin is far wider.
- **The complete-start count.** The held-out starts complete over D-145's horizon H_g number N_H - H_g + 1, and none
  when H_g >= N_H. They must reach the minimum pinned in 3.9.
- **The rule.** The gate passes when:
  - the whole line's MDL is at most delta\* at alpha;
  - every limit has its headroom;
  - the count reaches its minimum.

  Otherwise the search does not pin, and the data question (E-007 (2)) goes to the operator with the gate's result.

---

## 5. The fixed sequence over finalists

**The procedure.**
- The finalists f_1, ..., f_F are ordered on the search years by the rule pinned before the survey. The order is fixed
  before the held-out read.
- Each finalist is tested at its own latency L, in its place, by the whole rule at the **full** level alpha (CHARTER
  3.7, E-203 S-1's precedent).
- Starting at i = 1: if f_i passes, it is carried, and f_(i+1) is tested next. If f_i fails, the sequence stops, and
  no later finalist is read as a test.
- The pinned fallback stands in place of the composite. It is never tried after it.

**Why the family-wise error is at most alpha.**
- Let i_0 be the first finalist in the order whose null is true (it does not beat every baseline, given H).
- A false carry needs f_(i_0) to pass: if it fails, the sequence stops before any later finalist.
- P(f_(i_0) passes | its null) <= alpha. The intersection-union test is at most its weakest comparison's level, and
  each comparison is at most alpha by 2.2. The conjunction with (Y), (R), the limits and the floors only lowers it.
- So P(any false carry) <= alpha, strongly, whatever the other finalists' truths.

**What it costs and what is printed.**
- The gate's power (4.4) is the first finalist's. A later finalist is reached only after every earlier one passed, so
  its power is conditional on theirs.
- FPR_hist (2.7) is printed per finalist.
- The level is printed nominal when the held-out read ledger is not empty (CHARTER 3.6 (b)).

---

## 6. What H3 runs

### 6.1 The order, and what reads what

| part | when | reads | seeds (section 7) | weight |
|---|---|---|---|---|
| **H3-0** the probe | after the build's merge | synthetic toys, a few hundred lanes | the probe's | light |
| **H3-A** design checks: A1 same-design nulls (2.3) across S1 histories; A2 the exact-centred toy null (2.4); A3 the history null on symmetric generators (2.7); A4 end-to-end plants P2 to P4 (4.2) | before Wave 4.2 | **no bar**: S1 histories with stylised parameters; placeholder composites (the fallback with a placeholder limit, and a bounded toy composite) | the design-check block | heavy, one part a slot |
| **H3-D** the deciding calibration: D1 same-design nulls on the **pinned** rule; D2 the history null on S1 fitted to the search years and on S2 resamples; D3 the power gate (4.3, 4.4) | **after 3.9's pinning row (Wave 4.2) and H4's collection; before any search pin** | the search years' bars (the generator's fit and the resamples), H4's search-year outputs; **never a held-out session** | the deciding block | heavy, one part a slot |

- H3-A's results are **design checks only** (CHARTER 3.7, m-7). They choose the build's statistic among 2.2's
  candidates, m, J', and the generator's form. Nothing in them is read as the deciding calibration.
- The deciding seeds (section 7) are drawn by nothing before H3-D.

### 6.2 Memory (the machine's limits)

- **The cap.** One heavy job at a time, at most two workers, under 2.5 GB in all, so 1.25 GB a worker.
- **Per worker:** M_0 + L_w x b_lane, where:
  - M_0 is the process base (interpreter, numpy, pandas, scipy, the engine, one history);
  - L_w is the lockstep width (lanes simulated together);
  - b_lane is one lane's state: up to eight accounts of sixteen float64 fields, plus forty float64 of per-start
    reductions.
- Appendix A prints L_w's ceiling at an assumed M_0. **H3-0 measures M_0 and replaces the assumption.**
- At these sizes memory does not bind. The width is chosen for speed, and the parts are written so that nothing per
  journey is kept beyond its reductions:
  - per seed: the composite's dimension values, the per-year and per-regime partial sums;
  - per start: the fallback's six numbers;
  - a schedule-level history is a few thousand rows.
- A part that walks real bars (S2) holds one copy of the search years' minute bars per worker, read in place through
  the junction.

### 6.3 Time

- **A part's work** is R x arms x M x |T| x h x tau lane-trades: histories, arm-runs per history, seed replicates per
  arm, starts per history, the horizon's sessions, and trades per session (at most four in the toys).
- **Its wall time** is the work x c / 2, where c is the cost of one lane-trade.
- c is **not known**. Appendix A prints each part's work, and its hours at three assumed costs spanning a
  purpose-built lockstep to a slow engine. **H3-0 measures c.**
- **The rule before any heavy part starts:**
  - a part whose estimate at the measured c exceeds the cap (eight hours, `PART_CAP_H`) is cut, M first, and the power
    cost of the cut is stated;
  - or it is split into sub-parts, each its own heavy slot under the lock;
  - the sizes taken are recorded in H3's declaration before the run.
- D2's M is small because its coin-leg pass probability is computed (2.7). The full-J check runs on a declared subset
  of histories only.
- Each part runs from a clean checkout (`scripts/run_clean.py`) under `run.lock`, one at a time, and is watched to its
  exit. Its expected end in the lock is the measured estimate plus a margin.

### 6.4 Outputs

Every output is written with a manifest (`write_result`), from a clean run, carrying its seed map. **The size table**
uses `results/calibration_p.csv`'s columns plus:
- `history`, `history_class`, `horizon`, `J`, `J_prime`;
- the premise checks of 2.6.

**The history-null table:**
- per pair and history: theta(H) where exact, theta-hat(H) and sigma-hat(H) otherwise, the time conditions and the
  pass probability;
- FPR_hist with its interval, per finalist.

**The power table:** per plant and size, the whole line's pass rate, each line's, and the conjoint MDL.

The reused code is cited where it enters:
- `p_bound`'s `paired`, `batch_t`, `obm`, `flat_top` and the fixed-b nulls;
- `user_measures`' `p_by_month` and `n_eff_bartlett`;
- `family_stats`' `rng_of`, `stationary_indices`, `slow_sign`, `slow_two_state`, `block_mean_amplitude`,
  `year_mean_amplitude`, `conjoint_mdl_grid`, `conjoint_mdl_linear`, `need_from_lowers`, `mdl_from_need` and
  `critical`'s larger-of rule;
- `lift_bound.clopper_pearson`;
- `lift_one_sample`'s `exact_flip`, `flip_blocks` and `pattern_signs`;
- `scripts/q108_validate.py`'s `criterion`;
- `scripts/q126_calibrate.py`'s `ProvenanceRefused` and `RetiredSeedMap`, and E-195's part ledger and crash rule.

`family_stats.power_gate` and the B2 nulls conditional on the judged sides retire with the trade-lift line (E-208) and
are not used.

---

## 7. Seeds

**The block, by role.** Every draw is keyed `family_stats.rng_of(seed, part, history r, arm a, replicate j, ...)`,
with each part's key order fixed in H3's declaration. The coin field's uniforms are keyed by section 1.5's kappa under
the role's seed.

| seed | role | status |
|---|---|---|
| 20265870 | the H3 build's unit tests (synthetic toys only) | build tests |
| 20265871 | H3-0, the probe's toys | design check |
| 20265872 | H3-A: the S1 histories of A1 to A4 (the generator's draws; P4's regime signs) | design check |
| 20265873 | H3-A: the coin fields of A1, A2 and A4 (every arm; the disjoint sets by seed index) | design check |
| 20265874 | H3-A3: the history null's symmetric histories, their symmetry coins and their pairs' coin fields | design check |
| 20265875 | H3-D: the S1 histories fitted to the search years, and the S2 resamples' block indices | deciding |
| 20265876 | H3-D: the coin fields of D1 and D3 | deciding |
| 20265877 | H3-D2: the history null's symmetry coins and its pairs' coin fields | deciding |
| 20265878 | H3-D3: the plants' own draws (P3's tilts, P4's regime signs) | deciding |
| 20265879 | spare | spare, drawn by nothing |

**How the block was found (2026-11-18, before this note was committed).**
- **A word-bounded literal search** for every eight-digit number beginning 2026, in three places:
  - `git grep -Iw` on every branch, remote and tag (24 refs);
  - every line added or removed in every reachable commit (`git log --all -p`, 518 commits);
  - `grep -rIw` over the working copy, tracked and untracked, of the main tree and every worktree and clean checkout
    `git worktree list` names (15). The licensed bars and atlas, `.git` and caches were excluded.
- **No literal of the block appears anywhere.** No literal anywhere has a residue modulo 1,000 between 870 and 879.
  The nearest residues held are 838 and 900. So a derived seed (a literal plus a multiple of 1,000 plus c) can land in
  the block only with c from 32 to 41 (from 838), from -30 to -21 (from 900), or further. The nearest literals by value
  lie more than a thousand seeds away on each side. And 58 is no month, so no date written as eight digits can be one
  of these.
- **Derived seeds: Q-108's AST fold guard** (`scripts/q108_calibrate.py`'s `derived_problems`), re-pointed at this
  block with its allow-list emptied, over every `.py` of the working tree and every ref: **no refusal.**
  - It printed three unbounded loop expressions of `tests/test_features_lookahead.py` at older refs
    (`SEED_REPLACE + i`, `+ 200 + i`, `+ 1000 + i`). They would need reaches of thousands of seeds to land, against
    loop ranges hand-checked in Q-126's plan 4.1 at tens, a handful, and under 790.
  - It summarised every other unbounded expression as over a million seeds away.
- **The guard repeats.** `tests/test_three_way_design.py` repeats the literal search on every run (every tracked file
  and every working text file of the checkout it runs in). It builds the block by arithmetic, so it holds no literal
  of it. H3's build adds its own files to `DECLARED_USES` as it writes them.

---

## Appendix A. The arithmetic (printed by `docs/plans/scripts/three_way/three_way_arith.py`)

Every figure the note cites is here and nowhere typed. `units_H` and `units_S` are the most window-disjoint units in
the held-out and search years. `starts_H` and `blocks_H` are the complete held-out starts and their blocks of h. All
are upper bounds from the weekday counts. The run plan's sizes are proposals for H3's declaration, and its costs are
assumptions (6.3).

<!-- three_way_arith: begin -->
```text
levels: k, 0.05/(k(k+1)), B_min, 2^-B_min, 2^-(B_min-1)
  k=13  alpha=2.7473e-04  B_min=12  2^-B_min=2.4414e-04  2^-(B_min-1)=4.8828e-04
  k=14  alpha=2.3810e-04  B_min=13  2^-B_min=1.2207e-04  2^-(B_min-1)=2.4414e-04
  k=15  alpha=2.0833e-04  B_min=13  2^-B_min=1.2207e-04  2^-(B_min-1)=2.4414e-04
  k=16  alpha=1.8382e-04  B_min=13  2^-B_min=1.2207e-04  2^-(B_min-1)=2.4414e-04
  k=17  alpha=1.6340e-04  B_min=13  2^-B_min=1.2207e-04  2^-(B_min-1)=2.4414e-04
weekdays (upper bounds on sessions): held-out W_H=663, search W_S=1042
per horizon h: disjoint units floor(W/h) held-out | search; complete held-out starts W_H-h+1; held-out start-blocks of length h; sessions needed for B_min(13) disjoint units
  h=21   units_H<=31  units_S<=49  starts_H<=643  blocks_H<=30  sessions_for_12_units=252
  h=63   units_H<=10  units_S<=16  starts_H<=601  blocks_H<=9   sessions_for_12_units=756
  h=126  units_H<=5   units_S<=8   starts_H<=538  blocks_H<=4   sessions_for_12_units=1512
  h=252  units_H<=2   units_S<=4   starts_H<=412  blocks_H<=1   sessions_for_12_units=3024
empirical Bernstein at k=13: c1=sqrt(2 ln(2/alpha))=4.2173  c2=7 ln(2/alpha)/3=20.7501  normal z_(1-alpha)=3.4554  z_0.8=0.8416
replicates per (sigma/delta)^2 at power 0.8: exact bound 25.593, normal t 18.465, ratio 1.386
range term at most 0.1 x delta (differences in [-R, R]): replicates J by delta/R
  delta/R=0.01  J>=41502
  delta/R=0.02  J>=20752
  delta/R=0.05  J>=8302
rule of three (zero rejections, 95 % upper limit <= alpha): replications n
  alpha=5.0000e-02  n=59
  alpha=1.0000e-02  n=299
  alpha=1.0000e-03  n=2995
  alpha=2.7473e-04  n=10903
time leg, independent symmetric blocks: B, P(all B positive), P(strict majority positive)
  B=1   all=5.0000e-01  majority=5.0000e-01
  B=2   all=2.5000e-01  majority=2.5000e-01
  B=3   all=1.2500e-01  majority=5.0000e-01
  B=4   all=6.2500e-02  majority=3.1250e-01
  B=5   all=3.1250e-02  majority=5.0000e-01
  B=6   all=1.5625e-02  majority=3.4375e-01
  B=7   all=7.8125e-03  majority=5.0000e-01
  B=8   all=3.9062e-03  majority=3.6328e-01
  B=9   all=1.9531e-03  majority=5.0000e-01
  B=10  all=9.7656e-04  majority=3.7695e-01
memory: cap 2.5 GB over 2 workers, base 0.4 GB assumed, lane 1344 B: at most 632440 lanes a worker
run plan (trades a session <= 4; hours over 2 workers at the assumed costs 0.05 us, 0.5 us, 5.0 us a lane-trade)
  A1 same-design nulls       R=20  arms=3 M=10000  T=120 h=63  lane-trades=1.814e+10  h: 0.1  1.3  12.6
  A2 exact-centred toy null  R=20  arms=2 M=10000  T=120 h=63  lane-trades=1.210e+10  h: 0.1  0.8  8.4
  A3 history null            R=200 arms=2 M=2000   T=120 h=63  lane-trades=2.419e+10  h: 0.2  1.7  16.8
  A4 end-to-end plants       R=10  arms=6 M=10000  T=120 h=63  lane-trades=1.814e+10  h: 0.1  1.3  12.6
  D1 same-design nulls       R=20  arms=3 M=2000   T=601 h=252 lane-trades=7.270e+10  h: 0.5  5.0  50.5
  D2 history null            R=200 arms=2 M=500    T=601 h=252 lane-trades=1.212e+11  h: 0.8  8.4  84.1
  D3 power gate plants       R=10  arms=6 M=2000   T=601 h=252 lane-trades=7.270e+10  h: 0.5  5.0  50.5
```
<!-- three_way_arith: end -->

## Appendix B. The choices the red team should attack

1. **The empirical-Bernstein bound as the deciding statistic** (2.2): exact by theorem on every history, at a price in
   seeds (Appendix A). Its alternatives are the betting bound and the larger-of t. It needs **a bounded composite**,
   which is a demand on 3.9's pinning row.
2. **Seed sets as replicates, and m** (1.3, 2.1): the estimand theta_m depends on m for quantile-type dimensions.
3. **Each start with its own coin draws** (1.5), not one draw per calendar moment across starts.
4. **The complement of the uniforms, not of the outcomes**, for the antithetic twin (2.3). This reads CHARTER 3.7's
   "every coin side reversed" as the uniform complement for the redraw.
5. **The third null by exact DP centring** (2.4), and labelling the quantile composites' pool-centred version as
   approximate.
6. **The full level carried by the theorem, not by simulation** (2.6). Only the feasible levels are certified
   empirically.
7. **The history null by a symmetry of the generator** (2.7). Its rate depends on sd_H(theta), so it is printed per
   finalist with that spread. Its pass probability is computed from a modest pool, with a full-J check on a subset.
8. **Calendar years as the (Y) blocks** (3.4), the sign at the point estimate as "holds", and n_min. At h\* = 252,
   (Y) reduces to two years.
9. **Schedule-level synthetic histories** (2.6): the claim that on the deciding reading a history acts only through
   its schedule.
10. **"Its noise" in the limit clause** (4.4): coin noise only, or history as well.
11. **H3-A reads no bar**, and S2 resamples only in H3-D (6.1).
12. **E-208's "about a dozen" corrected** to at most ten complete disjoint 63-session units (3.2).
