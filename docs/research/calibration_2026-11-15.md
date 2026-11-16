# A test that delivers its stated level (TASK_QUEUE Q-16, 2026-11-15/16)

**Status: EXPLORATORY calibration of statistics.** No design's outcome is read here, and no figure is a result of this
repository.
- **Where the figures come from.** Every table below is printed, verbatim, by `scripts/q16_tables.py` from the CSVs
  `scripts/q16_calibrate.py` writes (section 8). The prose quotes no figure that is not in a table.
- **Before any figure is cited in a decision**, the lead reruns both scripts from a clean checkout of the commit
  named in section 8.

**What was asked.** Brief `docs/briefs/Q-16_2026-11-15.md`, plus the lead's additions from E-022 and E-023:
1. The one-sided statistic for the trades-first pass line (E-008): a design's lift over its coin twin on the same
   brackets, on the judged block (2024-01-02 to 2026-07-16), at 0.05 / (k (k + 1)) for k = 11 to 15, under the trades'
   dependence.
2. A calibrated replacement for Stage 2 D-621 (3)(i)'s P comparison, read on the scorecard beside the pass line.
3. The test of a filter that keeps the coin's side, against its **placebo-selection twin** (E-023), with its power
   curve by firing share.
4. F-02's **two-sample** line C1': the level lift minus a placebo lift (E-022).

**The answers.**

| form | statistic (module) | holds its level? | power |
|---|---|---|---|
| C1, the lift over the coin twin | **`cons`** (`extended.lift_bound.SHIPPED`): the trade-weighted session-cluster t on 21-, 42- and 63-session blocks, all three required | the only candidate at or below nominal on every real and every realistic synthetic null at k = 11-15 (Table 1); every single statistic, F-01's declared form included, exceeds its level on some real null | its 80 % minimum detectable lift is about a third above the 21-session t's (Table 4) |
| the P comparison (beside) | **`pcons`** stand-alone (`extended.p_bound.SHIPPED`); **`bm63c`** recommended (`p_bound.RECOMMENDED`), once its critical-value table is pinned | `pcons` everywhere; `bm63c` on every real and realistic null, on fresh replications (Table 5) | `pcons` can detect nothing on this block; `bm63c` can detect only differences near P-14's own trades (Table 6) |
| E-023's placebo-selection twin | **`cons`** on the two-sample difference (`lift_bound.placebo_selection_bound`), treated-cluster df | on all 55 selection nulls, from single offers to quarter-long blocks (Table 8b); the first form (df from every block) failed for persistent selections (Table F8b) | Table 9 |
| E-022's C1' (two-sample) | **`cons`** on the two-sample difference (`lift_bound.two_sample_bound`), treated-cluster df | on all 56 nulls (Table 10b); every single member fails on some | Table 11 |

---

## 1. What was compared

### 1.1 The lift (`extended/lift_bound.py`)

Per trade `i`, the pair difference is `x_i = (outcome(rule side) - outcome(mirror)) / 2` at the same bracket. Trades
are summed per session of the judged block's calendar: A1's 657 trading days from 2024-01-02, every session counted,
an empty one as zero. Sessions are then cut into G = n // b consecutive blocks of b or b + 1 sessions.

| name | the statistic | its critical value |
|---|---|---|
| `t21e` | Student-t on 21-session block means, the non-empty blocks weighted equally (F-01's declared stage-C form) | t, df = blocks - 1 |
| `t21w`, `t42w`, `t63w` | the per-trade mean with a cluster-robust (CR1) variance on 21-, 42- or 63-session blocks | t, df = G - 1 |
| `hac21` | the per-trade mean; a Bartlett-weighted variance over 21-session blocks and their neighbours up to 2 blocks away | fixed-b, simulated for iid normal blocks |
| `cbb21` | the studentised circular block bootstrap: 21-session blocks, each resample's own CR1 variance, centred | the resamples' t* quantile; 96,000 draws (at least 20 / level for every k up to 15) |
| `cons` | **the conservative fallback**: passes only where `t21w`, `t42w` and `t63w` all pass; its bound is their minimum | -- |

### 1.2 The P comparison (`extended/p_bound.py`)

A start's ahead average is `A = (1[net month 1 > 0] + 1[net month 2 > 0] + 1[net month 3 > 0]) / 3`, over starts with
63 sessions observed. The paired series is `d_t = A_design - A_P14` on the judged block's 595 starts (2024-01-02 to
2026-04-21).

| name | the statistic | its critical value |
|---|---|---|
| `d621` | Stage 2 D-621 (3)(i) as coded: the `level` percentile of a 2,000-draw non-circular moving-block bootstrap (63-start blocks, seed 20261700) | -- (the reference) |
| `bm63`, `bm126` | Student-t on 9 or 4 non-overlapping batch means | t, df = batches - 1 |
| `obm63`, `obm126` | the overlapping-batch-means variance (63 or 126 starts) | fixed-b, simulated for iid normal series |
| `ft63` | a flat-top HAC: lags to 63 (a month-3 window) weighted 1, tapering to 0 at 126 | fixed-b, simulated for iid normal series (400,000 draws, seed 20261919) |
| `pcons` | passes only where `bm63`, `obm126` and `ft63` all pass | -- |
| `bm63c` | `bm63`'s statistic | **calibrated** (two stages, below): the largest (1 - level) quantile of its t over the declared real and realistic nulls; rates reported from fresh replications |

**No conjunction of D-621 (3)'s lines is kept** (red team M3). The scorecard reads one statistic beside the pass line.
The guards, the gate, the coin line and the year rule are each reported on their own beside it, never combined with it
into a carry. A conjunction with a calibrated line could only reject less often, so its level would be at most the
line's.

### 1.3 The two-sample forms (`extended/lift_bound.py`, `diff_*`)

Both new forms compare two per-trade means on the same sessions:

    est = sum(S1) / sum(N1) - sum(S2) / sum(N2)

**The variance.** It is cluster-robust on the same session blocks, from the linearised residual block sums

    u_g = (BS1_g - th1 BN1_g) / n1 - (BS2_g - th2 BN2_g) / n2

This holds whether the two samples are disjoint (level and placebo fills) or nested (the selected offers and every
offer). The same four statistics apply (`t21w`, `t42w`, `t63w`, and their intersection `cons`).

**The block count (`DIFF_DF_RULE = "treated"`).** CR1's factor and the df use Gt = min(G1', G2'): the number of blocks
occupied by the sample that occupies fewer. A filter that fires on a few sessions or blocks has only that many
independent units.
- The first form counted every block holding a trade of either sample. The calibration found it lax by orders of
  magnitude for persistent selections: the few-treated-clusters failure of cluster-robust inference (sections 6.1 and
  7.4).
- `--diff-df all` reproduces that first run.

**E-023's placebo-selection twin.** Sample 1 is the filter's selected offers (their own outcome, the coin's side
kept); sample 2 is every offer (`placebo_selection_bound`). A seeded random filter firing on the same share of the same
offers selects, in expectation, the offers' own mean. Using that expectation adds no placebo noise. One seeded draw
instead of the expectation is itself a comparison of two random subsets, which the C1' form covers.

**F-02's C1' (E-022).** Sample 1 is the level fills' pair differences, sample 2 the placebo fills' (five replicates)
(`two_sample_bound`). **One correction to the draft's section 9.2:** its `z_s = (sum w_level on s) / n_level -
(sum w_placebo on s) / n_placebo` gives the right estimate D, but the variance must come from the residual,
count-centred sums `u_g` above. The raw `z_s` carry each session's fill count, and a variance of them is not D's.

## 2. The nulls

Every null is mean-zero by construction. The real nulls keep the data's own dependence.

### 2.1 The lift's real nulls: P-16's own trades, sign-flipped

- **The source.** P-16's trades are `rc_s150_all`, Stage 2's 37.5-point news-safe coin, already read by Stage 2
  (D-547). `scripts/q16_p16_pairs.py` rebuilt them with the vendored walk, one chunk of days at a time, under
  `run.lock`. It refuses unless three identities hold, and all three held:
  - the cutoff's 266 marks equal `rc_width_screen.csv` section `marks`;
  - the cell's counts, long share and every R's unresolved share equal its `rc_s150_all` row;
  - the trades' content hash equals Stage 2's pinned `TRADES_SHA256` (`17bcc29b...`).
- **The direction outcome.** For each judged trade, `v = (outcome(long) - outcome(short)) / 2` at the same bracket,
  in win probability at 1R (`win1`) and in net R at 3R (`net3`).
- **Making the null.** The sign of `v` is flipped by blocks of L sessions (L = 1, 5, 21, 63; a random phase each
  replication), so the dependence within a flip block stays. The null is a rule whose side holds for L sessions.
  `coin` flips the coin's own side by session.
- **The trade streams.**
  - `offered`: every offered candidate, about 141 a session.
  - `taken`: re-entry when flat at the fresh Combine's 1.5R. This approximates P-16's schedule; it takes more trades
    a session than P-16's engine, which has account limits.
  - `thinN`: seeded uniform thinnings to N = 200 to 5,000 trades.
- **The count:** 70 real nulls.

What the pairs show (scratch readings, used only to set the synthetic nulls' parameters):
- strong clustering within a session, with an intra-session correlation of about 0.2 to 0.35 across R;
- nearly uncorrelated session means across sessions;
- a drift by year of about a percentage point of win probability.

### 2.2 The lift's synthetic nulls (`SYNTHETIC` in the script)

Session counts are Poisson or overdispersed negative binomial, for 200 to 5,000 trades.

**The realistic nulls** (`iid`, `cluster`, `cluster_ar1`, `regime01`, `volclust`):
- a probit session effect, at the data's intra-session correlation;
- lag-1 autocorrelation 0.1 across sessions;
- a 63-session regime holding 1 % of the session effect;
- continuous outcomes with clustered volatility.

**The stress nulls** go well past the data:
- `cluster_ar5`, autocorrelation 0.5;
- `regime03` and `regime10`, regimes of 3 % and 10 % (the data's by-year drift is near 0.5 %);
- `skew`, a mean-zero pair difference of +1/2 with probability 0.8 and -2 with probability 0.2. Under a coin-type
  null a pair difference is symmetric, so this is outside the data.

### 2.3 The P comparison's nulls

**The real nulls.** The judged block's paired series from `user_journey.csv` section `start` (already read):
- P-16 against P-14 on both arms;
- P-14 point against P-14 verdict, and P-16 point against P-16 verdict (same trades).

Each series is used centred and raw, and flipped by blocks of 21, 63 and 126 starts: 24 nulls. The raw form keeps
the real mean difference inside each flip block, so it is an advantage over P-14 that switches sign by regime.

**Two identities first, both held:**
- P-14's judged P equals every family file's `judged` reference value (`u_budget.csv`);
- the re-implemented Stage 2 bootstrap reproduces `user_journey.csv`'s paired row (P-14 against P-16, the share ahead
  at 63 sessions, all starts: lo and hi).

**The synthetic nulls:**
- Gaussian moving averages over 21 and 63 starts;
- the red team's structural null (`rt_cal.py`'s `path`), and `path_slow`;
- the stress `path_edge`: a mean-zero edge difference that is AR(1) 0.995 across sessions.

**`bm63c` in two stages.**
1. Its critical value at each level is the largest (1 - level) quantile of `bm63`'s t over the 28 real and realistic
   nulls (200,000 replications each).
2. Its rejection rates are then read on **fresh** replications of every null (`default_rng([seed, 1000 + null])`).
   Only stage 2's rates are reported.

### 2.4 The two-sample forms' nulls (real: P-16's judged offers)

**Placebo-selection.** Each null is a random filter independent of the outcomes, firing on a share of 2 %, 5 %, 10 %,
25 % or 50 % of the 93,037 judged offers. The outcomes are the coin side's own win at 1R, and net R at 3R. The filter
models:
- `offer`: each offer on its own, drawn exactly through the hypergeometric (win only);
- `window`: a contiguous run of offers every session at a random start, as a timing filter would choose;
- `session`: whole sessions;
- `block5`, `block21`, `block63`: whole blocks of 5, 21 or 63 sessions (persistent selections).

**Power by firing share.** The selected offers' outcomes are shifted by d, and the detectable difference is reported as
selected minus twin, d (1 - the selected share of offers).

**C1'.** The level fills and the placebo fills (five times as many) are two disjoint seeded subsets of the offers. The
pair difference's sign is flipped by blocks of L = 1, 21 or 63 sessions:
- `shared`: one side for both samples;
- `indep`: independent sides;
- `coin`: the coin's own side.

There are 200 to 2,000 level fills. Under the null both samples have the same mean, and a common lift cancels exactly.

## 3. Replications and their intervals

- **Why 200,000.** Every t-type and HAC statistic ran 200,000 replications per null. At the smallest level,
  0.05/240 = 2.08e-4, telling the nominal rate from twice it (a binomial test, two-sided 5 %, power 90 %) needs about
  (1.96 + 1.28 √2)² / level, roughly 68,000 replications; at 0.05/132, about 37,600. At 200,000 the expected count at
  0.05/240 is about 42, and its 95 % interval excludes twice the nominal rate.
- **The bootstrap** costs 96,000 draws a replication. It ran 20,000 replications on 12 nulls, so its family-level
  rates carry wide intervals (Table 3); the `t21w` rejections on the same replications sit beside them.
- **D-621's line** ran 20,000 replications per null.
- **The placebo-selection power curves** used 5,000 replications per share.
- **Intervals** are Clopper-Pearson, 95 %.

## 4. Results: the lift

### Table 1. The lift: the worst realised level (rate / nominal) by candidate, family level and null group

Rates x 1e4 with the 95 % Clopper-Pearson interval; the null that attains the maximum.

| method | nulls | k = 11 (nominal 3.79) | k = 12 (nominal 3.21) | k = 13 (nominal 2.75) | k = 14 (nominal 2.38) | k = 15 (nominal 2.08) |
|---|---|---|---|---|---|---|
| `t21e` | real (70) | **3.64x** (13.80 [12.22, 15.53]; real:offered:win1:persist63) | **3.62x** (11.60 [10.16, 13.19]; real:offered:win1:persist63) | **3.79x** (10.40 [9.04, 11.91]; real:offered:win1:persist63) | **3.65x** (8.70 [7.46, 10.09]; real:offered:win1:persist63) | **3.72x** (7.75 [6.58, 9.07]; real:offered:win1:persist63) |
| `t21e` | synthetic (25) | **2.35x** (8.90 [7.64, 10.31]; syn:regime01:5000) | **2.28x** (7.30 [6.16, 8.58]; syn:regime01:5000) | **2.24x** (6.15 [5.11, 7.34]; syn:regime01:5000) | **2.29x** (5.45 [4.48, 6.57]; syn:regime01:5000) | **2.18x** (4.55 [3.66, 5.59]; syn:regime01:5000) |
| `t21e` | stress (20) | **21.49x** (81.40 [77.51, 85.44]; syn:regime10:5000) | **22.79x** (73.05 [69.36, 76.88]; syn:regime10:5000) | **24.41x** (67.05 [63.52, 70.72]; syn:regime10:5000) | **25.75x** (61.30 [57.93, 64.82]; syn:regime10:5000) | **27.36x** (57.00 [53.75, 60.40]; syn:regime10:5000) |
| `t21w` | real (70) | **3.74x** (14.15 [12.55, 15.90]; real:offered:win1:persist63) | **3.85x** (12.35 [10.86, 13.99]; real:offered:win1:persist63) | **4.09x** (11.25 [9.83, 12.82]; real:offered:win1:persist63) | **4.03x** (9.60 [8.29, 11.06]; real:offered:win1:persist63) | **4.15x** (8.65 [7.41, 10.04]; real:offered:win1:persist63) |
| `t21w` | synthetic (25) | **2.56x** (9.70 [8.38, 11.16]; syn:regime01:2000) | **2.64x** (8.45 [7.22, 9.82]; syn:regime01:2000) | **2.60x** (7.15 [6.03, 8.42]; syn:regime01:2000) | **2.67x** (6.35 [5.29, 7.55]; syn:regime01:2000) | **2.76x** (5.75 [4.75, 6.90]; syn:regime01:2000) |
| `t21w` | stress (20) | **21.58x** (81.75 [77.85, 85.79]; syn:regime10:5000) | **23.12x** (74.10 [70.39, 77.96]; syn:regime10:5000) | **24.97x** (68.60 [65.03, 72.31]; syn:regime10:5000) | **26.63x** (63.40 [59.97, 66.98]; syn:regime10:5000) | **28.25x** (58.85 [55.54, 62.30]; syn:regime10:5000) |
| `t42w` | real (70) | **2.36x** (8.95 [7.69, 10.36]; real:taken:net3:persist21) | **2.31x** (7.40 [6.26, 8.69]; real:taken:net3:persist21) | **2.42x** (6.65 [5.57, 7.88]; real:taken:net3:persist21) | **2.52x** (6.00 [4.97, 7.17]; real:taken:net3:persist21) | **2.62x** (5.45 [4.48, 6.57]; real:taken:net3:persist21) |
| `t42w` | synthetic (25) | **1.85x** (7.00 [5.89, 8.26]; syn:regime01:2000) | **1.75x** (5.60 [4.61, 6.74]; syn:regime01:2000) | **1.69x** (4.65 [3.75, 5.70]; syn:regime01:2000) | **1.70x** (4.05 [3.22, 5.03]; syn:regime01:2000) | **1.87x** (3.90 [3.08, 4.87]; syn:regime01:2000) |
| `t42w` | stress (20) | **6.44x** (24.40 [22.29, 26.66]; syn:regime10:5000) | **6.65x** (21.30 [19.33, 23.42]; syn:regime10:5000) | **6.83x** (18.75 [16.90, 20.75]; syn:regime10:5000) | **7.10x** (16.90 [15.15, 18.80]; syn:regime10:5000) | **7.22x** (15.05 [13.40, 16.85]; syn:regime10:5000) |
| `t63w` | real (70) | **3.60x** (13.65 [12.08, 15.37]; real:thin200:win1:persist63) | **3.81x** (12.20 [10.72, 13.83]; real:thin200:win1:persist63) | **3.97x** (10.90 [9.50, 12.45]; real:thin200:win1:persist63) | **4.31x** (10.25 [8.90, 11.75]; real:thin200:win1:persist63) | **4.13x** (8.60 [7.36, 9.98]; real:thin200:win1:persist63) |
| `t63w` | synthetic (25) | **1.39x** (5.25 [4.29, 6.36]; syn:regime01:5000) | **1.47x** (4.70 [3.80, 5.75]; syn:regime01:2000) | **1.47x** (4.05 [3.22, 5.03]; syn:regime01:2000) | **1.43x** (3.40 [2.64, 4.31]; syn:regime01:2000) | **1.44x** (3.00 [2.29, 3.86]; syn:regime01:2000) |
| `t63w` | stress (20) | **2.64x** (10.00 [8.66, 11.49]; syn:regime10:2000) | **2.84x** (9.10 [7.83, 10.52]; syn:regime10:2000) | **2.78x** (7.65 [6.49, 8.96]; syn:regime10:2000) | **2.81x** (6.70 [5.61, 7.93]; syn:regime10:2000) | **2.93x** (6.10 [5.07, 7.28]; syn:regime10:2000) |
| `hac21` | real (70) | **4.21x** (15.95 [14.25, 17.80]; real:offered:win1:persist63) | **4.74x** (15.20 [13.54, 17.01]; real:offered:win1:persist63) | **4.86x** (13.35 [11.80, 15.05]; real:offered:win1:persist63) | **5.36x** (12.75 [11.23, 14.41]; real:offered:win1:persist63) | **5.71x** (11.90 [10.44, 13.51]; real:offered:win1:persist63) |
| `hac21` | synthetic (25) | **1.97x** (7.45 [6.30, 8.75]; syn:regime01:2000) | **2.15x** (6.90 [5.80, 8.15]; syn:regime01:2000) | **2.13x** (5.85 [4.84, 7.01]; syn:regime01:2000) | **2.16x** (5.15 [4.20, 6.25]; syn:regime01:2000) | **2.28x** (4.75 [3.84, 5.81]; syn:regime01:2000) |
| `hac21` | stress (20) | **6.20x** (23.50 [21.43, 25.72]; syn:regime10:5000) | **6.94x** (22.25 [20.23, 24.41]; syn:regime10:5000) | **6.90x** (18.95 [17.09, 20.96]; syn:regime10:5000) | **7.33x** (17.45 [15.67, 19.38]; syn:regime10:5000) | **7.92x** (16.50 [14.77, 18.38]; syn:regime10:5000) |
| `cons` | real (70) | **0.58x** (2.20 [1.60, 2.95]; real:taken:net3:persist21) | **0.62x** (2.00 [1.43, 2.72]; real:taken:net3:persist21) | **0.60x** (1.65 [1.14, 2.32]; real:taken:net3:persist21) | **0.59x** (1.40 [0.93, 2.02]; real:taken:net3:persist21) | **0.60x** (1.25 [0.81, 1.85]; real:taken:net3:persist21) |
| `cons` | synthetic (25) | **0.34x** (1.30 [0.85, 1.90]; syn:regime01:2000) | **0.34x** (1.10 [0.69, 1.67]; syn:regime01:2000) | **0.36x** (1.00 [0.61, 1.54]; syn:regime01:2000) | **0.36x** (0.85 [0.50, 1.36]; syn:regime01:2000) | **0.34x** (0.70 [0.38, 1.17]; syn:regime01:2000) |
| `cons` | stress (20) | **1.69x** (6.40 [5.34, 7.61]; syn:regime10:5000) | **1.65x** (5.30 [4.34, 6.41]; syn:regime10:5000) | **1.67x** (4.60 [3.71, 5.64]; syn:regime10:5000) | **1.60x** (3.80 [2.99, 4.76]; syn:regime10:2000) | **1.63x** (3.40 [2.64, 4.31]; syn:regime10:2000) |

#### Table 1b. Nulls whose 95 % interval lies wholly above the nominal rate (k = 11)

| method | real (nulls) | synthetic (nulls) | stress (nulls) |
|---|---|---|---|
| `t21e` | 5 of 70 | 4 of 25 | 18 of 20 |
| `t21w` | 14 of 70 | 9 of 25 | 19 of 20 |
| `t42w` | 9 of 70 | 7 of 25 | 16 of 20 |
| `t63w` | 16 of 70 | 5 of 25 | 15 of 20 |
| `hac21` | 22 of 70 | 15 of 25 | 20 of 20 |
| `cons` | 0 of 70 | 0 of 25 | 2 of 20 |

### Table 2. The lift: rates x 1e4 at 0.05/132 (ratio to nominal) on the main real nulls

| null | `t21e` | `t21w` | `t42w` | `t63w` | `hac21` | `cons` |
|---|---|---|---|---|---|---|
| real:taken:win1:persist1 | 3.65 (0.96x) | 5.30 (1.40x) | 5.60 (1.48x) | 5.65 (1.49x) | 5.65 (1.49x) | 0.60 (0.16x) |
| real:taken:win1:persist21 | 4.05 (1.07x) | 3.55 (0.94x) | 7.60 (2.01x) | 7.00 (1.85x) | 9.40 (2.48x) | 1.30 (0.34x) |
| real:taken:win1:persist63 | 5.20 (1.37x) | 4.50 (1.19x) | 2.45 (0.65x) | 1.40 (0.37x) | 7.00 (1.85x) | 0.00 (0.00x) |
| real:taken:win1:coin | 2.65 (0.70x) | 4.60 (1.21x) | 5.65 (1.49x) | 4.70 (1.24x) | 4.80 (1.27x) | 0.70 (0.18x) |
| real:taken:net3:persist1 | 3.55 (0.94x) | 5.75 (1.52x) | 6.55 (1.73x) | 6.40 (1.69x) | 6.55 (1.73x) | 1.00 (0.26x) |
| real:taken:net3:persist21 | 6.35 (1.68x) | 5.80 (1.53x) | 8.95 (2.36x) | 10.20 (2.69x) | 8.85 (2.34x) | 2.20 (0.58x) |
| real:taken:net3:persist63 | 0.35 (0.09x) | 0.00 (0.00x) | 0.60 (0.16x) | 3.40 (0.90x) | 3.80 (1.00x) | 0.00 (0.00x) |
| real:taken:net3:coin | 3.90 (1.03x) | 6.45 (1.70x) | 4.50 (1.19x) | 4.90 (1.29x) | 5.15 (1.36x) | 1.00 (0.26x) |
| real:thin200:win1:persist1 | 3.60 (0.95x) | 4.65 (1.23x) | 4.90 (1.29x) | 3.85 (1.02x) | 4.75 (1.25x) | 0.70 (0.18x) |
| real:thin200:win1:persist21 | 4.05 (1.07x) | 4.80 (1.27x) | 3.05 (0.81x) | 5.90 (1.56x) | 3.40 (0.90x) | 0.30 (0.08x) |
| real:thin200:win1:persist63 | 0.25 (0.07x) | 0.10 (0.03x) | 1.50 (0.40x) | 13.65 (3.60x) | 0.10 (0.03x) | 0.10 (0.03x) |
| real:thin200:win1:coin | 3.15 (0.83x) | 4.40 (1.16x) | 3.75 (0.99x) | 4.05 (1.07x) | 4.25 (1.12x) | 0.65 (0.17x) |
| real:thin200:net3:persist1 | 1.70 (0.45x) | 4.85 (1.28x) | 3.85 (1.02x) | 4.30 (1.14x) | 4.80 (1.27x) | 0.60 (0.16x) |
| real:thin200:net3:persist21 | 0.75 (0.20x) | 2.10 (0.55x) | 1.10 (0.29x) | 2.50 (0.66x) | 3.25 (0.86x) | 0.25 (0.07x) |
| real:thin200:net3:persist63 | 0.00 (0.00x) | 0.65 (0.17x) | 0.45 (0.12x) | 0.40 (0.11x) | 5.85 (1.54x) | 0.00 (0.00x) |
| real:thin200:net3:coin | 1.10 (0.29x) | 4.55 (1.20x) | 3.10 (0.82x) | 4.10 (1.08x) | 4.25 (1.12x) | 0.50 (0.13x) |
| real:thin1000:win1:persist1 | 2.65 (0.70x) | 4.20 (1.11x) | 3.95 (1.04x) | 4.05 (1.07x) | 4.45 (1.17x) | 0.65 (0.17x) |
| real:thin1000:win1:persist21 | 3.20 (0.84x) | 3.55 (0.94x) | 4.10 (1.08x) | 2.65 (0.70x) | 3.10 (0.82x) | 0.20 (0.05x) |
| real:thin1000:win1:persist63 | 0.00 (0.00x) | 0.00 (0.00x) | 0.00 (0.00x) | 0.00 (0.00x) | 0.15 (0.04x) | 0.00 (0.00x) |
| real:thin1000:win1:coin | 4.00 (1.06x) | 4.95 (1.31x) | 4.25 (1.12x) | 3.75 (0.99x) | 5.35 (1.41x) | 0.50 (0.13x) |
| real:thin1000:net3:persist1 | 4.20 (1.11x) | 4.80 (1.27x) | 5.85 (1.54x) | 4.30 (1.14x) | 4.65 (1.23x) | 0.70 (0.18x) |
| real:thin1000:net3:persist21 | 2.40 (0.63x) | 1.85 (0.49x) | 3.55 (0.94x) | 5.05 (1.33x) | 2.85 (0.75x) | 0.30 (0.08x) |
| real:thin1000:net3:persist63 | 0.00 (0.00x) | 0.00 (0.00x) | 0.10 (0.03x) | 0.00 (0.00x) | 0.00 (0.00x) | 0.00 (0.00x) |
| real:thin1000:net3:coin | 4.20 (1.11x) | 4.05 (1.07x) | 3.75 (0.99x) | 3.60 (0.95x) | 3.90 (1.03x) | 0.35 (0.09x) |
| real:thin5000:win1:persist1 | 3.85 (1.02x) | 3.75 (0.99x) | 3.65 (0.96x) | 3.80 (1.00x) | 3.40 (0.90x) | 0.50 (0.13x) |
| real:thin5000:win1:persist21 | 4.40 (1.16x) | 4.15 (1.10x) | 4.35 (1.15x) | 2.15 (0.57x) | 4.95 (1.31x) | 0.40 (0.11x) |
| real:thin5000:win1:persist63 | 0.20 (0.05x) | 0.20 (0.05x) | 1.45 (0.38x) | 1.30 (0.34x) | 2.50 (0.66x) | 0.05 (0.01x) |
| real:thin5000:win1:coin | 3.95 (1.04x) | 3.95 (1.04x) | 3.50 (0.92x) | 4.00 (1.06x) | 4.50 (1.19x) | 0.40 (0.11x) |
| real:thin5000:net3:persist1 | 4.40 (1.16x) | 4.25 (1.12x) | 4.20 (1.11x) | 3.25 (0.86x) | 4.40 (1.16x) | 0.25 (0.07x) |
| real:thin5000:net3:persist21 | 4.00 (1.06x) | 3.55 (0.94x) | 3.45 (0.91x) | 2.95 (0.78x) | 3.55 (0.94x) | 0.60 (0.16x) |
| real:thin5000:net3:persist63 | 0.00 (0.00x) | 0.00 (0.00x) | 1.35 (0.36x) | 0.00 (0.00x) | 0.40 (0.11x) | 0.00 (0.00x) |
| real:thin5000:net3:coin | 3.40 (0.90x) | 3.15 (0.83x) | 3.55 (0.94x) | 3.60 (0.95x) | 3.90 (1.03x) | 0.40 (0.11x) |
| real:offered:win1:persist1 | 4.30 (1.14x) | 4.30 (1.14x) | 3.60 (0.95x) | 3.35 (0.88x) | 3.60 (0.95x) | 0.35 (0.09x) |
| real:offered:win1:persist21 | 10.35 (2.73x) | 9.90 (2.61x) | 3.40 (0.90x) | 3.15 (0.83x) | 7.45 (1.97x) | 1.05 (0.28x) |
| real:offered:win1:persist63 | 13.80 (3.64x) | 14.15 (3.74x) | 3.50 (0.92x) | 1.15 (0.30x) | 15.95 (4.21x) | 0.35 (0.09x) |
| real:offered:win1:coin | 3.55 (0.94x) | 3.55 (0.94x) | 4.40 (1.16x) | 4.50 (1.19x) | 5.05 (1.33x) | 0.65 (0.17x) |
| real:offered:net3:persist1 | 3.60 (0.95x) | 3.35 (0.88x) | 4.00 (1.06x) | 3.35 (0.88x) | 4.25 (1.12x) | 0.45 (0.12x) |
| real:offered:net3:persist21 | 3.10 (0.82x) | 3.05 (0.81x) | 3.00 (0.79x) | 5.10 (1.35x) | 4.30 (1.14x) | 0.50 (0.13x) |
| real:offered:net3:persist63 | 0.00 (0.00x) | 0.00 (0.00x) | 0.00 (0.00x) | 1.10 (0.29x) | 0.00 (0.00x) | 0.00 (0.00x) |
| real:offered:net3:coin | 3.95 (1.04x) | 4.20 (1.11x) | 4.15 (1.10x) | 3.15 (0.83x) | 4.00 (1.06x) | 0.55 (0.15x) |

### Table 3. The studentised circular block bootstrap (`cbb21`)

| null | reps | draws | k = 11: rejections (rate x 1e4, ratio) | `t21w` on the same replications | k = 15 | crit / t crit at k = 11 (p10, p50, p90) |
|---|---|---|---|---|---|---|
| real:taken:win1:persist1 | 20000 | 96000 | 12 (6.00, 1.58x) | 14 | 9 (2.16x) | 0.940, 1.034, 1.148 |
| real:taken:net3:persist1 | 20000 | 96000 | 10 (5.00, 1.32x) | 14 | 5 (1.20x) | 0.953, 1.044, 1.158 |
| real:taken:win1:persist21 | 20000 | 96000 | 13 (6.50, 1.72x) | 7 | 8 (1.92x) | 0.936, 1.043, 1.175 |
| real:offered:win1:persist21 | 20000 | 96000 | 35 (17.50, 4.62x) | 24 | 27 (6.48x) | 0.923, 0.989, 1.074 |
| real:thin200:win1:coin | 20000 | 96000 | 11 (5.50, 1.45x) | 11 | 7 (1.68x) | 0.936, 1.016, 1.113 |
| real:thin200:net3:persist1 | 20000 | 96000 | 11 (5.50, 1.45x) | 6 | 5 (1.20x) | 0.930, 1.023, 1.139 |
| real:thin1000:win1:persist5 | 20000 | 96000 | 7 (3.50, 0.92x) | 9 | 5 (1.20x) | 0.934, 1.012, 1.103 |
| real:thin5000:net3:persist21 | 20000 | 96000 | 6 (3.00, 0.79x) | 7 | 2 (0.48x) | 0.944, 1.008, 1.082 |
| syn:cluster:1000 | 20000 | 96000 | 6 (3.00, 0.79x) | 7 | 3 (0.72x) | 0.939, 1.020, 1.119 |
| syn:skew:500 | 20000 | 96000 | 16 (8.00, 2.11x) | 28 | 8 (1.92x) | 1.004, 1.092, 1.208 |
| syn:regime03:2000 | 20000 | 96000 | 28 (14.00, 3.70x) | 34 | 19 (4.56x) | 0.936, 1.019, 1.122 |
| syn:cluster_ar5:5000 | 20000 | 96000 | 7 (3.50, 0.92x) | 12 | 4 (0.96x) | 0.936, 1.021, 1.122 |

### Table 4a. The lift's minimum detectable lift at 80 % power, real coin nulls thinned to N trades

(80 % power; win probability, points (x 100))

| trades | `t21w` k=11 | `t21w` k=15 | `t63w` k=11 | `t63w` k=15 | `cons` k=11 | `cons` k=15 |
|---|---|---|---|---|---|---|
| 200 | 15.4 | 16.2 | 20.3 | 22.0 | 20.5 | 22.2 |
| 500 | 10.3 | 10.8 | 13.5 | 14.6 | 13.7 | 14.8 |
| 1000 | 7.2 | 7.6 | 9.5 | 10.3 | 9.6 | 10.4 |
| 2000 | 4.9 | 5.2 | 6.5 | 7.0 | 6.6 | 7.1 |
| 5000 | 3.3 | 3.5 | 4.4 | 4.7 | 4.4 | 4.7 |

(80 % power; net R at 3R)

| trades | `t21w` k=11 | `t21w` k=15 | `t63w` k=11 | `t63w` k=15 | `cons` k=11 | `cons` k=15 |
|---|---|---|---|---|---|---|
| 200 | 0.385 | 0.403 | 0.507 | 0.548 | 0.512 | 0.552 |
| 500 | 0.277 | 0.290 | 0.364 | 0.394 | 0.368 | 0.397 |
| 1000 | 0.192 | 0.202 | 0.253 | 0.274 | 0.256 | 0.276 |
| 2000 | 0.134 | 0.140 | 0.176 | 0.190 | 0.178 | 0.192 |
| 5000 | 0.089 | 0.093 | 0.117 | 0.126 | 0.118 | 0.127 |

### Table 4b. The lift's minimum detectable lift at 80 % power, real persist1 nulls thinned to N trades

(80 % power; win probability, points (x 100))

| trades | `t21w` k=11 | `t21w` k=15 | `t63w` k=11 | `t63w` k=15 | `cons` k=11 | `cons` k=15 |
|---|---|---|---|---|---|---|
| 200 | 16.2 | 17.0 | 21.4 | 23.1 | 21.6 | 23.3 |
| 500 | 10.7 | 11.3 | 14.1 | 15.3 | 14.3 | 15.4 |
| 1000 | 8.6 | 9.1 | 11.4 | 12.3 | 11.5 | 12.4 |
| 2000 | 7.0 | 7.3 | 9.1 | 9.9 | 9.2 | 10.0 |
| 5000 | 5.6 | 5.9 | 7.4 | 8.0 | 7.5 | 8.1 |

(80 % power; net R at 3R)

| trades | `t21w` k=11 | `t21w` k=15 | `t63w` k=11 | `t63w` k=15 | `cons` k=11 | `cons` k=15 |
|---|---|---|---|---|---|---|
| 200 | 0.426 | 0.447 | 0.560 | 0.606 | 0.565 | 0.610 |
| 500 | 0.310 | 0.325 | 0.408 | 0.441 | 0.412 | 0.445 |
| 1000 | 0.265 | 0.278 | 0.350 | 0.378 | 0.354 | 0.382 |
| 2000 | 0.223 | 0.234 | 0.294 | 0.317 | 0.297 | 0.320 |
| 5000 | 0.187 | 0.196 | 0.246 | 0.267 | 0.249 | 0.268 |


## 5. Results: the P comparison

### Table 5. The P comparison: the worst realised level by candidate, family level and null group

| method | nulls | k = 11 (nominal 3.79) | k = 12 (nominal 3.21) | k = 13 (nominal 2.75) | k = 14 (nominal 2.38) | k = 15 (nominal 2.08) |
|---|---|---|---|---|---|---|
| `d621` | real (24) | **127.25x** (482.00 [452.72, 512.60]; real:p16v-p14v:raw:flip126) | **146.95x** (471.00 [442.05, 501.28]; real:p16v-p14v:raw:flip126) | **167.99x** (461.50 [432.83, 491.49]; real:p16v-p14v:raw:flip126) | **192.36x** (458.00 [429.44, 487.89]; real:p16v-p14v:raw:flip126) | **219.36x** (457.00 [428.47, 486.86]; real:p16v-p14v:raw:flip126) |
| `d621` | synthetic (4) | **73.26x** (277.50 [255.17, 301.21]; syn:ma63) | **82.52x** (264.50 [242.70, 287.69]; syn:ma63) | **94.46x** (259.50 [237.91, 282.49]; syn:ma63) | **107.10x** (255.00 [233.59, 277.80]; syn:ma63) | **120.96x** (252.00 [230.72, 274.67]; syn:ma63) |
| `d621` | stress (1) | **172.66x** (654.00 [620.12, 689.15]; syn:path_edge) | **199.37x** (639.00 [605.49, 673.78]; syn:path_edge) | **228.77x** (628.50 [595.25, 663.03]; syn:path_edge) | **259.98x** (619.00 [585.99, 653.29]; syn:path_edge) | **294.96x** (614.50 [581.61, 648.68]; syn:path_edge) |
| `bm63` | real (24) | **4.01x** (15.20 [13.54, 17.01]; real:p16p-p14p:centred:flip63) | **4.06x** (13.00 [11.47, 14.68]; real:p16p-p14p:centred:flip63) | **4.15x** (11.40 [9.97, 12.98]; real:p16p-p14p:centred:flip63) | **3.97x** (9.45 [8.15, 10.90]; real:p16p-p14p:centred:flip63) | **4.15x** (8.65 [7.41, 10.04]; real:p16p-p14p:centred:flip63) |
| `bm63` | synthetic (4) | **3.46x** (13.10 [11.56, 14.78]; syn:ma63) | **3.51x** (11.25 [9.83, 12.82]; syn:ma63) | **3.44x** (9.45 [8.15, 10.90]; syn:ma63) | **3.57x** (8.50 [7.27, 9.88]; syn:ma63) | **3.41x** (7.10 [5.98, 8.37]; syn:ma63) |
| `bm63` | stress (1) | **12.69x** (48.05 [45.07, 51.18]; syn:path_edge) | **13.23x** (42.40 [39.60, 45.35]; syn:path_edge) | **13.27x** (36.45 [33.86, 39.19]; syn:path_edge) | **13.36x** (31.80 [29.38, 34.37]; syn:path_edge) | **13.92x** (29.00 [26.69, 31.46]; syn:path_edge) |
| `bm126` | real (24) | **41.28x** (156.35 [150.96, 161.88]; real:p16p-p16v:raw:flip126) | **48.78x** (156.35 [150.96, 161.88]; real:p16p-p16v:raw:flip126) | **49.63x** (136.35 [131.31, 141.53]; real:p16p-p16v:raw:flip126) | **22.22x** (52.90 [49.77, 56.18]; real:p16p-p16v:centred:flip126) | **24.17x** (50.35 [47.29, 53.55]; real:p16p-p16v:centred:flip126) |
| `bm126` | synthetic (4) | **1.31x** (4.95 [4.02, 6.03]; syn:ma63) | **1.14x** (3.65 [2.86, 4.59]; syn:ma63) | **1.11x** (3.05 [2.33, 3.92]; syn:ma63) | **1.09x** (2.60 [1.94, 3.41]; syn:ma63) | **1.10x** (2.30 [1.68, 3.07]; syn:ma63) |
| `bm126` | stress (1) | **2.26x** (8.55 [7.32, 9.93]; syn:path_edge) | **2.17x** (6.95 [5.84, 8.21]; syn:path_edge) | **2.09x** (5.75 [4.75, 6.90]; syn:path_edge) | **2.10x** (5.00 [4.07, 6.08]; syn:path_edge) | **2.16x** (4.50 [3.62, 5.53]; syn:path_edge) |
| `obm63` | real (24) | **12.28x** (46.50 [43.57, 49.58]; real:p16v-p14v:centred:flip63) | **13.45x** (43.10 [40.28, 46.07]; real:p16v-p14v:centred:flip63) | **14.60x** (40.10 [37.38, 42.97]; real:p16v-p14v:centred:flip63) | **14.66x** (34.90 [32.36, 37.58]; real:p16v-p14v:centred:flip63) | **15.34x** (31.95 [29.52, 34.52]; real:p16v-p14v:centred:flip63) |
| `obm63` | synthetic (4) | **11.76x** (44.55 [41.68, 47.57]; syn:ma63) | **13.06x** (41.85 [39.07, 44.78]; syn:ma63) | **13.72x** (37.70 [35.06, 40.48]; syn:ma63) | **14.18x** (33.75 [31.26, 36.39]; syn:ma63) | **14.83x** (30.90 [28.51, 33.43]; syn:ma63) |
| `obm63` | stress (1) | **38.98x** (147.65 [142.41, 153.03]; syn:path_edge) | **43.15x** (138.30 [133.23, 143.51]; syn:path_edge) | **46.26x** (127.10 [122.24, 132.11]; syn:path_edge) | **47.33x** (112.70 [108.12, 117.42]; syn:path_edge) | **50.83x** (105.90 [101.46, 110.48]; syn:path_edge) |
| `obm126` | real (24) | **11.84x** (44.85 [41.97, 47.88]; real:p16v-p14v:centred:flip63) | **12.26x** (39.30 [36.61, 42.14]; real:p16v-p14v:centred:flip63) | **12.90x** (35.45 [32.89, 38.15]; real:p16v-p14v:centred:flip63) | **13.61x** (32.40 [29.96, 34.99]; real:p16v-p14v:centred:flip63) | **13.32x** (27.75 [25.49, 30.15]; real:p16v-p14v:centred:flip63) |
| `obm126` | synthetic (4) | **7.08x** (26.80 [24.58, 29.16]; syn:ma63) | **7.36x** (23.60 [21.52, 25.83]; syn:ma63) | **7.99x** (21.95 [19.95, 24.10]; syn:ma63) | **8.65x** (20.60 [18.66, 22.69]; syn:ma63) | **9.00x** (18.75 [16.90, 20.75]; syn:ma63) |
| `obm126` | stress (1) | **19.07x** (72.25 [68.58, 76.06]; syn:path_edge) | **20.55x** (65.85 [62.35, 69.49]; syn:path_edge) | **21.44x** (58.90 [55.59, 62.35]; syn:path_edge) | **23.25x** (55.35 [52.15, 58.70]; syn:path_edge) | **24.50x** (51.05 [47.97, 54.27]; syn:path_edge) |
| `ft63` | real (24) | **8.12x** (30.75 [28.37, 33.28]; real:p16p-p16v:raw:flip126) | **7.35x** (23.55 [21.47, 25.77]; real:p16p-p16v:raw:flip126) | **8.57x** (23.55 [21.47, 25.77]; real:p16p-p16v:raw:flip126) | **8.36x** (19.90 [17.99, 21.95]; real:p16p-p16v:raw:flip126) | **9.55x** (19.90 [17.99, 21.95]; real:p16p-p16v:raw:flip126) |
| `ft63` | synthetic (4) | **0.98x** (3.70 [2.91, 4.64]; syn:ma21) | **0.89x** (2.85 [2.16, 3.69]; syn:ma21) | **0.95x** (2.60 [1.94, 3.41]; syn:ma21) | **0.97x** (2.30 [1.68, 3.07]; syn:ma21) | **0.82x** (1.70 [1.18, 2.38]; syn:ma21) |
| `ft63` | stress (1) | **1.08x** (4.10 [3.26, 5.09]; syn:path_edge) | **0.98x** (3.15 [2.42, 4.03]; syn:path_edge) | **1.02x** (2.80 [2.12, 3.64]; syn:path_edge) | **0.94x** (2.25 [1.64, 3.01]; syn:path_edge) | **0.91x** (1.90 [1.34, 2.61]; syn:path_edge) |
| `pcons` | real (24) | **0.22x** (0.85 [0.50, 1.36]; real:p16v-p14v:centred:flip63) | **0.17x** (0.55 [0.27, 0.98]; real:p16v-p14v:centred:flip63) | **0.20x** (0.55 [0.27, 0.98]; real:p16v-p14v:centred:flip63) | **0.13x** (0.30 [0.11, 0.65]; real:p16v-p14v:centred:flip63) | **0.14x** (0.30 [0.11, 0.65]; real:p16v-p14v:centred:flip63) |
| `pcons` | synthetic (4) | **0.05x** (0.20 [0.05, 0.51]; syn:ma63) | **0.06x** (0.20 [0.05, 0.51]; syn:ma63) | **0.07x** (0.20 [0.05, 0.51]; syn:ma63) | **0.08x** (0.20 [0.05, 0.51]; syn:ma63) | **0.10x** (0.20 [0.05, 0.51]; syn:ma63) |
| `pcons` | stress (1) | **0.29x** (1.10 [0.69, 1.67]; syn:path_edge) | **0.27x** (0.85 [0.50, 1.36]; syn:path_edge) | **0.25x** (0.70 [0.38, 1.17]; syn:path_edge) | **0.23x** (0.55 [0.27, 0.98]; syn:path_edge) | **0.24x** (0.50 [0.24, 0.92]; syn:path_edge) |
| `bm63c` | real (24) | **0.92x** (3.50 [2.73, 4.42]; real:p16p-p14p:centred:flip63) | **0.90x** (2.90 [2.20, 3.75]; real:p16p-p14p:centred:flip63) | **0.95x** (2.60 [1.94, 3.41]; real:p16p-p14p:centred:flip63) | **1.05x** (2.50 [1.86, 3.30]; real:p16p-p14p:centred:flip63) | **0.96x** (2.00 [1.43, 2.72]; real:p16p-p14p:centred:flip63) |
| `bm63c` | synthetic (4) | **0.95x** (3.60 [2.82, 4.53]; syn:ma63) | **0.89x** (2.85 [2.16, 3.69]; syn:ma63) | **0.93x** (2.55 [1.90, 3.35]; syn:ma63) | **0.86x** (2.05 [1.47, 2.78]; syn:ma63) | **0.89x** (1.85 [1.30, 2.55]; syn:ma63) |
| `bm63c` | stress (1) | **4.01x** (15.20 [13.54, 17.01]; syn:path_edge) | **3.87x** (12.40 [10.91, 14.04]; syn:path_edge) | **3.93x** (10.80 [9.41, 12.34]; syn:path_edge) | **3.49x** (8.30 [7.09, 9.66]; syn:path_edge) | **3.31x** (6.90 [5.80, 8.15]; syn:path_edge) |

#### Table 5b. Nulls whose 95 % interval lies wholly above the nominal rate (k = 11)

| method | real (nulls) | synthetic (nulls) | stress (nulls) |
|---|---|---|---|
| `d621` | 18 of 24 | 4 of 4 | 1 of 1 |
| `bm63` | 5 of 24 | 2 of 4 | 1 of 1 |
| `bm126` | 9 of 24 | 1 of 4 | 1 of 1 |
| `obm63` | 11 of 24 | 4 of 4 | 1 of 1 |
| `obm126` | 7 of 24 | 4 of 4 | 1 of 1 |
| `ft63` | 9 of 24 | 0 of 4 | 0 of 1 |
| `pcons` | 0 of 24 | 0 of 4 | 0 of 1 |
| `bm63c` | 0 of 24 | 0 of 4 | 1 of 1 |

### Table 6. The P comparison's minimum detectable difference in P at 80 % power, judged block

| null | `bm63` k=11 | `bm63` k=15 | `bm126` k=11 | `bm126` k=15 | `ft63` k=11 | `ft63` k=15 | `pcons` k=11 | `pcons` k=15 | `bm63c` k=11 | `bm63c` k=15 |
|---|---|---|---|---|---|---|---|---|---|---|
| real:p16v-p14v:centred:flip63 | 0.308 | 0.334 | 0.936 | 1.143 | 1.341 | 1.752 | 1.341 | 1.752 | 0.368 | 0.415 |
| real:p16v-p14v:centred:flip21 | 0.262 | 0.285 | 0.732 | 0.894 | 1.092 | 1.427 | 1.092 | 1.427 | 0.315 | 0.356 |
| real:p14p-p14v:centred:flip63 | 0.103 | 0.112 | 0.288 | 0.352 | 0.413 | 0.539 | 0.413 | 0.539 | 0.124 | 0.140 |
| real:p16p-p16v:centred:flip63 | 0.044 | 0.048 | 0.099 | 0.121 | 0.161 | 0.211 | 0.161 | 0.211 | 0.054 | 0.061 |

### Table 7. `bm63c`: the batch-means t's critical values calibrated on the declared nulls (stage 1)

| level | k | `bm63c` critical value | t(8)'s | ratio | attained on | calibration nulls x replications |
|---|---|---|---|---|---|---|
| 0.000379 | 11 | 6.437 | 5.268 | 1.222 | syn:ma63 | 28 x 200000 |
| 0.000321 | 12 | 6.659 | 5.407 | 1.232 | syn:ma63 | 28 x 200000 |
| 0.000275 | 13 | 6.823 | 5.537 | 1.232 | syn:ma63 | 28 x 200000 |
| 0.000238 | 14 | 7.089 | 5.659 | 1.253 | real:p16p-p14p:centred:flip63 | 28 x 200000 |
| 0.000208 | 15 | 7.319 | 5.775 | 1.267 | real:p16p-p14p:centred:flip63 | 28 x 200000 |
| 0.001 |  | 5.614 | 4.501 | 1.247 | real:p16p-p14p:centred:flip63 | 28 x 200000 |
| 0.005 |  | 4.369 | 3.355 | 1.302 | real:p16p-p14p:centred:flip63 | 28 x 200000 |
| 0.025 |  | 2.884 | 2.306 | 1.250 | real:p16v-p14v:centred:flip63 | 28 x 200000 |


## 6. Results: the two-sample forms

### 6.1 The first form (the df from every block): failed, kept on record

#### Table F8. The placebo-selection twin (E-023): the worst realised level by selection model

Random filters independent of the outcomes, firing on 2 % to 50 % of P-16's judged offers; the selected offers' own outcome against every offer's (the twin's expectation).

| method | nulls | k = 11 (nominal 3.79) | k = 12 (nominal 3.21) | k = 13 (nominal 2.75) | k = 14 (nominal 2.38) | k = 15 (nominal 2.08) |
|---|---|---|---|---|---|---|
| `t21w` | selection: offer (5) | **1.28x** (4.85 [3.93, 5.92]; select:offer:0.02:win1) | **1.25x** (4.00 [3.17, 4.98]; select:offer:0.02:win1) | **1.27x** (3.50 [2.73, 4.42]; select:offer:0.02:win1) | **1.26x** (3.00 [2.29, 3.86]; select:offer:0.02:win1) | **1.30x** (2.70 [2.03, 3.52]; select:offer:0.5:win1) |
| `t21w` | selection: window (10) | **1.31x** (4.95 [4.02, 6.03]; select:window:0.25:win1) | **1.20x** (3.85 [3.04, 4.81]; select:window:0.25:win1) | **1.16x** (3.20 [2.46, 4.09]; select:window:0.25:win1) | **1.13x** (2.70 [2.03, 3.52]; select:window:0.25:win1) | **1.20x** (2.50 [1.86, 3.30]; select:window:0.25:win1) |
| `t21w` | selection: session (10) | **20.54x** (77.80 [74.00, 81.75]; select:session:0.02:win1) | **22.53x** (72.20 [68.54, 76.01]; select:session:0.02:win1) | **24.57x** (67.50 [63.96, 71.19]; select:session:0.02:win1) | **26.42x** (62.90 [59.48, 66.46]; select:session:0.02:win1) | **28.51x** (59.40 [56.08, 62.87]; select:session:0.02:win1) |
| `t21w` | selection: block5 (10) | **248.70x** (942.05 [929.28, 954.94]; select:block5:0.02:net3) | **290.13x** (929.90 [917.21, 942.71]; select:block5:0.02:net3) | **335.63x** (922.05 [909.40, 934.81]; select:block5:0.02:net3) | **376.87x** (897.30 [884.81, 909.91]; select:block5:0.02:net3) | **427.25x** (890.10 [877.65, 902.66]; select:block5:0.02:net3) |
| `t21w` | selection: block21 (10) | **172.11x** (651.95 [641.17, 662.86]; select:block21:0.05:win1) | **200.80x** (643.60 [632.88, 654.44]; select:block21:0.05:win1) | **227.06x** (623.80 [613.24, 634.49]; select:block21:0.05:win1) | **254.31x** (605.50 [595.09, 616.04]; select:block21:0.05:win1) | **286.90x** (597.70 [587.35, 608.18]; select:block21:0.05:win1) |
| `t21w` | selection: block63 (10) | **172.27x** (652.55 [641.76, 663.46]; select:block63:0.1:win1) | **202.10x** (647.75 [637.00, 658.63]; select:block63:0.1:win1) | **233.18x** (640.60 [629.91, 651.42]; select:block63:0.1:win1) | **265.21x** (631.45 [620.83, 642.20]; select:block63:0.1:win1) | **291.74x** (607.80 [597.37, 618.36]; select:block63:0.1:win1) |
| `t42w` | selection: offer (5) | **1.33x** (5.05 [4.11, 6.14]; select:offer:0.02:win1) | **1.26x** (4.05 [3.22, 5.03]; select:offer:0.02:win1) | **1.31x** (3.60 [2.82, 4.53]; select:offer:0.02:win1) | **1.30x** (3.10 [2.38, 3.97]; select:offer:0.02:win1) | **1.25x** (2.60 [1.94, 3.41]; select:offer:0.02:win1) |
| `t42w` | selection: window (10) | **1.17x** (4.45 [3.57, 5.48]; select:window:0.25:win1) | **1.20x** (3.85 [3.04, 4.81]; select:window:0.25:win1) | **1.18x** (3.25 [2.51, 4.14]; select:window:0.5:net3) | **1.26x** (3.00 [2.29, 3.86]; select:window:0.25:win1) | **1.30x** (2.70 [2.03, 3.52]; select:window:0.25:win1) |
| `t42w` | selection: session (10) | **13.93x** (52.75 [49.62, 56.02]; select:session:0.02:net3) | **15.35x** (49.20 [46.18, 52.36]; select:session:0.02:net3) | **16.96x** (46.60 [43.66, 49.68]; select:session:0.02:net3) | **18.61x** (44.30 [41.44, 47.31]; select:session:0.02:net3) | **20.11x** (41.90 [39.12, 44.83]; select:session:0.02:net3) |
| `t42w` | selection: block5 (10) | **254.36x** (963.50 [950.60, 976.52]; select:block5:0.02:net3) | **295.74x** (947.90 [935.10, 960.82]; select:block5:0.02:net3) | **340.41x** (935.20 [922.47, 948.04]; select:block5:0.02:net3) | **386.65x** (920.60 [907.96, 933.35]; select:block5:0.02:net3) | **430.51x** (896.90 [884.41, 909.51]; select:block5:0.02:net3) |
| `t42w` | selection: block21 (10) | **190.83x** (722.85 [711.54, 734.29]; select:block21:0.05:net3) | **217.95x** (698.55 [687.42, 709.81]; select:block21:0.05:net3) | **246.37x** (676.85 [665.88, 687.95]; select:block21:0.05:net3) | **272.22x** (648.15 [637.40, 659.03]; select:block21:0.05:net3) | **299.98x** (624.95 [614.38, 635.65]; select:block21:0.05:net3) |
| `t42w` | selection: block63 (10) | **141.19x** (534.80 [524.98, 544.75]; select:block63:0.1:win1) | **161.79x** (518.55 [508.87, 528.36]; select:block63:0.1:win1) | **178.74x** (491.05 [481.62, 500.61]; select:block63:0.1:win1) | **201.41x** (479.55 [470.23, 489.01]; select:block63:0.1:win1) | **226.66x** (472.20 [462.94, 481.59]; select:block63:0.1:win1) |
| `t63w` | selection: offer (5) | **1.15x** (4.35 [3.48, 5.37]; select:offer:0.02:win1) | **1.20x** (3.85 [3.04, 4.81]; select:offer:0.25:win1) | **1.20x** (3.30 [2.55, 4.20]; select:offer:0.25:win1) | **1.22x** (2.90 [2.20, 3.75]; select:offer:0.5:win1) | **1.22x** (2.55 [1.90, 3.35]; select:offer:0.5:win1) |
| `t63w` | selection: window (10) | **1.12x** (4.25 [3.39, 5.25]; select:window:0.25:win1) | **1.14x** (3.65 [2.86, 4.59]; select:window:0.25:win1) | **1.11x** (3.05 [2.33, 3.92]; select:window:0.25:win1) | **1.09x** (2.60 [1.94, 3.41]; select:window:0.02:net3) | **1.13x** (2.35 [1.73, 3.12]; select:window:0.5:net3) |
| `t63w` | selection: session (10) | **10.67x** (40.40 [37.67, 43.28]; select:session:0.02:net3) | **11.47x** (36.75 [34.15, 39.50]; select:session:0.02:net3) | **12.45x** (34.20 [31.69, 36.86]; select:session:0.02:net3) | **13.69x** (32.60 [30.15, 35.20]; select:session:0.02:net3) | **14.86x** (30.95 [28.56, 33.48]; select:session:0.02:net3) |
| `t63w` | selection: block5 (10) | **208.24x** (788.80 [777.02, 800.70]; select:block5:0.02:net3) | **238.80x** (765.40 [753.78, 777.14]; select:block5:0.02:net3) | **274.22x** (753.35 [741.82, 765.00]; select:block5:0.02:net3) | **309.75x** (737.50 [726.08, 749.04]; select:block5:0.02:net3) | **349.42x** (727.95 [716.60, 739.42]; select:block5:0.02:net3) |
| `t63w` | selection: block21 (10) | **151.91x** (575.40 [565.23, 585.70]; select:block21:0.05:net3) | **171.74x** (550.45 [540.49, 560.54]; select:block21:0.05:net3) | **189.99x** (521.95 [512.24, 531.79]; select:block21:0.05:net3) | **209.03x** (497.70 [488.21, 507.32]; select:block21:0.05:net3) | **230.09x** (479.35 [470.03, 488.80]; select:block21:0.05:net3) |
| `t63w` | selection: block63 (10) | **65.59x** (248.45 [241.67, 255.37]; select:block63:0.1:net3) | **75.80x** (242.95 [236.25, 249.79]; select:block63:0.1:net3) | **80.06x** (219.95 [213.57, 226.47]; select:block63:0.1:net3) | **88.07x** (209.70 [203.46, 216.07]; select:block63:0.1:net3) | **98.35x** (204.90 [198.74, 211.20]; select:block63:0.1:net3) |
| `cons` | selection: offer (5) | **0.16x** (0.60 [0.31, 1.05]; select:offer:0.5:win1) | **0.17x** (0.55 [0.27, 0.98]; select:offer:0.5:win1) | **0.20x** (0.55 [0.27, 0.98]; select:offer:0.5:win1) | **0.15x** (0.35 [0.14, 0.72]; select:offer:0.5:win1) | **0.17x** (0.35 [0.14, 0.72]; select:offer:0.5:win1) |
| `cons` | selection: window (10) | **0.16x** (0.60 [0.31, 1.05]; select:window:0.25:win1) | **0.14x** (0.45 [0.21, 0.85]; select:window:0.25:win1) | **0.13x** (0.35 [0.14, 0.72]; select:window:0.25:win1) | **0.13x** (0.30 [0.11, 0.65]; select:window:0.02:net3) | **0.12x** (0.25 [0.08, 0.58]; select:window:0.02:net3) |
| `cons` | selection: session (10) | **6.28x** (23.80 [21.71, 26.03]; select:session:0.02:net3) | **6.80x** (21.80 [19.80, 23.94]; select:session:0.02:net3) | **7.37x** (20.25 [18.33, 22.32]; select:session:0.02:net3) | **8.02x** (19.10 [17.23, 21.11]; select:session:0.02:net3) | **8.59x** (17.90 [16.10, 19.85]; select:session:0.02:net3) |
| `cons` | selection: block5 (10) | **165.12x** (625.45 [614.88, 636.15]; select:block5:0.02:net3) | **188.39x** (603.80 [593.40, 614.33]; select:block5:0.02:net3) | **216.14x** (593.80 [583.48, 604.25]; select:block5:0.02:net3) | **244.88x** (583.05 [572.82, 593.41]; select:block5:0.02:net3) | **273.72x** (570.25 [560.13, 580.50]; select:block5:0.02:net3) |
| `cons` | selection: block21 (10) | **65.56x** (248.35 [241.57, 255.26]; select:block21:0.02:win1) | **73.65x** (236.05 [229.44, 242.80]; select:block21:0.02:win1) | **81.50x** (223.90 [217.46, 230.48]; select:block21:0.02:win1) | **89.88x** (214.00 [207.70, 220.44]; select:block21:0.02:win1) | **102.41x** (213.35 [207.06, 219.78]; select:block21:0.02:win1) |
| `cons` | selection: block63 (10) | **19.89x** (75.35 [71.61, 79.24]; select:block63:0.1:win1) | **22.51x** (72.15 [68.49, 75.96]; select:block63:0.1:net3) | **24.08x** (66.15 [62.64, 69.80]; select:block63:0.1:net3) | **27.47x** (65.40 [61.91, 69.03]; select:block63:0.1:net3) | **31.39x** (65.40 [61.91, 69.03]; select:block63:0.1:net3) |

##### Table F8b. Nulls whose 95 % interval lies wholly above the nominal rate (k = 11)

| method | selection: offer (nulls) | selection: window (nulls) | selection: session (nulls) | selection: block5 (nulls) | selection: block21 (nulls) | selection: block63 (nulls) |
|---|---|---|---|---|---|---|
| `t21w` | 1 of 5 | 1 of 10 | 6 of 10 | 6 of 10 | 8 of 10 | 10 of 10 |
| `t42w` | 1 of 5 | 0 of 10 | 5 of 10 | 6 of 10 | 8 of 10 | 9 of 10 |
| `t63w` | 0 of 5 | 0 of 10 | 4 of 10 | 6 of 10 | 7 of 10 | 8 of 10 |
| `cons` | 0 of 5 | 0 of 10 | 2 of 10 | 4 of 10 | 6 of 10 | 8 of 10 |

#### Table F9. The placebo-selection twin: the selected-minus-twin difference detectable at 80 % power, by firing share

(win1 in points of win probability; net3 in R; -- where 80 % is not reached inside the grid)

| model | value | share | `t21w` k=11 | `cons` k=11 | `cons` k=15 |
|---|---|---|---|---|---|
| offer | win1 | 0.02 | 5.3 | 7.1 | 7.7 |
| offer | win1 | 0.05 | 3.4 | 4.4 | 4.8 |
| offer | win1 | 0.1 | 2.3 | 3.1 | 3.3 |
| offer | win1 | 0.25 | 1.3 | 1.8 | 1.9 |
| offer | win1 | 0.5 | 0.8 | 1.0 | 1.1 |
| window | win1 | 0.02 | 5.4 | 7.2 | 7.8 |
| window | net3 | 0.02 | 0.196 | 0.261 | 0.282 |
| window | win1 | 0.05 | 3.5 | 4.7 | 5.1 |
| window | net3 | 0.05 | 0.155 | 0.205 | 0.223 |
| window | win1 | 0.1 | 2.6 | 3.5 | 3.8 |
| window | net3 | 0.1 | 0.132 | 0.175 | 0.188 |
| window | win1 | 0.25 | 1.6 | 2.2 | 2.3 |
| window | net3 | 0.25 | 0.093 | 0.124 | 0.133 |
| window | win1 | 0.5 | 1.0 | 1.3 | 1.4 |
| window | net3 | 0.5 | 0.059 | 0.079 | 0.086 |
| session | win1 | 0.02 | 7.3 | 9.5 | 10.2 |
| session | net3 | 0.02 | 0.547 | 0.721 | 0.780 |
| session | win1 | 0.05 | 4.5 | 5.9 | 6.4 |
| session | net3 | 0.05 | 0.348 | 0.456 | 0.495 |
| session | win1 | 0.1 | 3.0 | 4.0 | 4.3 |
| session | net3 | 0.1 | 0.236 | 0.317 | 0.340 |
| session | win1 | 0.25 | 1.7 | 2.3 | 2.5 |
| session | net3 | 0.25 | 0.138 | 0.185 | 0.197 |
| session | win1 | 0.5 | 1.0 | 1.3 | 1.5 |
| session | net3 | 0.5 | 0.079 | 0.107 | 0.118 |
| block5 | win1 | 0.02 | 7.1 | 9.3 | 10.1 |
| block5 | net3 | 0.02 | 0.451 | 0.604 | 0.644 |
| block5 | win1 | 0.05 | 5.0 | 6.4 | 7.0 |
| block5 | net3 | 0.05 | 0.326 | 0.435 | 0.471 |
| block5 | win1 | 0.1 | 3.5 | 4.6 | 5.0 |
| block5 | net3 | 0.1 | 0.227 | 0.305 | 0.329 |
| block5 | win1 | 0.25 | 2.0 | 2.7 | 2.9 |
| block5 | net3 | 0.25 | 0.133 | 0.182 | 0.198 |
| block5 | win1 | 0.5 | 1.2 | 1.7 | 2.0 |
| block5 | net3 | 0.5 | 0.079 | 0.115 | 0.130 |
| block21 | win1 | 0.02 | -- | -- | -- |
| block21 | net3 | 0.02 | -- | -- | -- |
| block21 | win1 | 0.05 | 9.4 | 11.7 | 12.6 |
| block21 | net3 | 0.05 | 0.409 | 0.522 | 0.562 |
| block21 | win1 | 0.1 | 4.1 | 5.6 | 6.0 |
| block21 | net3 | 0.1 | 0.219 | 0.289 | 0.311 |
| block21 | win1 | 0.25 | 2.6 | 3.9 | 4.5 |
| block21 | net3 | 0.25 | 0.137 | 0.202 | 0.228 |
| block21 | win1 | 0.5 | 1.8 | -- | -- |
| block21 | net3 | 0.5 | 0.091 | -- | -- |
| block63 | win1 | 0.02 | -- | -- | -- |
| block63 | net3 | 0.02 | -- | -- | -- |
| block63 | win1 | 0.05 | -- | -- | -- |
| block63 | net3 | 0.05 | -- | -- | -- |
| block63 | win1 | 0.1 | -- | -- | -- |
| block63 | net3 | 0.1 | -- | -- | -- |
| block63 | win1 | 0.25 | 3.0 | -- | -- |
| block63 | net3 | 0.25 | 0.149 | -- | -- |
| block63 | win1 | 0.5 | 2.4 | -- | -- |
| block63 | net3 | 0.5 | 0.118 | -- | -- |

#### Table F10. F-02's C1' (E-022), the level lift minus the placebo lift: the worst realised level

| method | nulls | k = 11 (nominal 3.79) | k = 12 (nominal 3.21) | k = 13 (nominal 2.75) | k = 14 (nominal 2.38) | k = 15 (nominal 2.08) |
|---|---|---|---|---|---|---|
| `t21w` | C1': shared (24) | **3.76x** (14.25 [12.64, 16.00]; c1p:500:net3:shared63) | **3.32x** (10.65 [9.27, 12.18]; c1p:500:net3:shared63) | **3.24x** (8.90 [7.64, 10.31]; c1p:500:net3:shared63) | **3.07x** (7.30 [6.16, 8.58]; c1p:500:net3:shared63) | **2.93x** (6.10 [5.07, 7.28]; c1p:500:net3:shared63) |
| `t21w` | C1': indep (24) | **2.97x** (11.25 [9.83, 12.82]; c1p:500:net3:indep63) | **2.87x** (9.20 [7.92, 10.63]; c1p:500:net3:indep63) | **2.93x** (8.05 [6.85, 9.39]; c1p:500:net3:indep63) | **2.88x** (6.85 [5.75, 8.10]; c1p:500:net3:indep63) | **2.95x** (6.15 [5.11, 7.34]; c1p:500:net3:indep63) |
| `t21w` | C1': coin (8) | **1.41x** (5.35 [4.38, 6.46]; c1p:200:net3:coin) | **1.59x** (5.10 [4.16, 6.19]; c1p:200:net3:coin) | **1.69x** (4.65 [3.75, 5.70]; c1p:200:net3:coin) | **1.72x** (4.10 [3.26, 5.09]; c1p:200:net3:coin) | **1.56x** (3.25 [2.51, 4.14]; c1p:200:net3:coin) |
| `t42w` | C1': shared (24) | **1.89x** (7.15 [6.03, 8.42]; c1p:500:net3:shared63) | **2.00x** (6.40 [5.34, 7.61]; c1p:500:net3:shared63) | **2.02x** (5.55 [4.57, 6.68]; c1p:500:net3:shared63) | **1.93x** (4.60 [3.71, 5.64]; c1p:500:net3:shared63) | **1.87x** (3.90 [3.08, 4.87]; c1p:500:net3:shared63) |
| `t42w` | C1': indep (24) | **1.32x** (5.00 [4.07, 6.08]; c1p:500:win1:indep21) | **1.29x** (4.15 [3.31, 5.14]; c1p:500:win1:indep21) | **1.27x** (3.50 [2.73, 4.42]; c1p:500:win1:indep21) | **1.34x** (3.20 [2.46, 4.09]; c1p:500:net3:indep21) | **1.42x** (2.95 [2.25, 3.81]; c1p:500:net3:indep21) |
| `t42w` | C1': coin (8) | **1.23x** (4.65 [3.75, 5.70]; c1p:500:win1:coin) | **1.25x** (4.00 [3.17, 4.98]; c1p:500:win1:coin) | **1.26x** (3.45 [2.68, 4.37]; c1p:500:win1:coin) | **1.22x** (2.90 [2.20, 3.75]; c1p:1000:net3:coin) | **1.27x** (2.65 [1.99, 3.47]; c1p:500:win1:coin) |
| `t63w` | C1': shared (24) | **4.20x** (15.90 [14.20, 17.75]; c1p:500:win1:shared63) | **4.15x** (13.30 [11.75, 15.00]; c1p:500:win1:shared63) | **4.19x** (11.50 [10.06, 13.09]; c1p:500:win1:shared63) | **3.99x** (9.50 [8.20, 10.95]; c1p:500:win1:shared63) | **3.91x** (8.15 [6.95, 9.50]; c1p:500:win1:shared63) |
| `t63w` | C1': indep (24) | **1.41x** (5.35 [4.38, 6.46]; c1p:500:win1:indep63) | **1.45x** (4.65 [3.75, 5.70]; c1p:500:win1:indep63) | **1.46x** (4.00 [3.17, 4.98]; c1p:500:win1:indep63) | **1.41x** (3.35 [2.60, 4.25]; c1p:500:win1:indep63) | **1.32x** (2.75 [2.07, 3.58]; c1p:200:net3:indep1) |
| `t63w` | C1': coin (8) | **1.25x** (4.75 [3.84, 5.81]; c1p:1000:net3:coin) | **1.34x** (4.30 [3.44, 5.31]; c1p:1000:net3:coin) | **1.35x** (3.70 [2.91, 4.64]; c1p:1000:net3:coin) | **1.39x** (3.30 [2.55, 4.20]; c1p:1000:net3:coin) | **1.25x** (2.60 [1.94, 3.41]; c1p:500:win1:coin) |
| `cons` | C1': shared (24) | **0.49x** (1.85 [1.30, 2.55]; c1p:500:net3:shared63) | **0.42x** (1.35 [0.89, 1.96]; c1p:500:net3:shared63) | **0.49x** (1.35 [0.89, 1.96]; c1p:500:net3:shared63) | **0.36x** (0.85 [0.50, 1.36]; c1p:500:net3:shared63) | **0.24x** (0.50 [0.24, 0.92]; c1p:2000:net3:shared63) |
| `cons` | C1': indep (24) | **0.24x** (0.90 [0.53, 1.42]; c1p:500:net3:indep21) | **0.17x** (0.55 [0.27, 0.98]; c1p:1000:win1:indep21) | **0.16x** (0.45 [0.21, 0.85]; c1p:500:win1:indep21) | **0.17x** (0.40 [0.17, 0.79]; c1p:2000:net3:indep21) | **0.19x** (0.40 [0.17, 0.79]; c1p:2000:net3:indep21) |
| `cons` | C1': coin (8) | **0.22x** (0.85 [0.50, 1.36]; c1p:1000:net3:coin) | **0.23x** (0.75 [0.42, 1.24]; c1p:1000:net3:coin) | **0.20x** (0.55 [0.27, 0.98]; c1p:1000:net3:coin) | **0.19x** (0.45 [0.21, 0.85]; c1p:1000:net3:coin) | **0.14x** (0.30 [0.11, 0.65]; c1p:500:win1:coin) |

##### Table F10b. Nulls whose 95 % interval lies wholly above the nominal rate (k = 11)

| method | C1': shared (nulls) | C1': indep (nulls) | C1': coin (nulls) |
|---|---|---|---|
| `t21w` | 5 of 24 | 8 of 24 | 1 of 8 |
| `t42w` | 3 of 24 | 2 of 24 | 0 of 8 |
| `t63w` | 7 of 24 | 3 of 24 | 1 of 8 |
| `cons` | 0 of 24 | 0 of 24 | 0 of 8 |

#### Table F11. C1': the difference D detectable at 80 % power (placebo fills five times the level's; sides flipped by session)

| level fills | value | sides | `t21w` k=11 | `cons` k=11 | `cons` k=15 |
|---|---|---|---|---|---|
| 200 | win1 | shared | 17.4 | 23.2 | 25.0 |
| 200 | win1 | indep | 18.2 | 24.2 | 26.1 |
| 200 | net3 | shared | 0.475 | 0.633 | 0.683 |
| 200 | net3 | indep | 0.526 | 0.703 | 0.758 |
| 500 | win1 | shared | 10.4 | 13.8 | 14.9 |
| 500 | win1 | indep | 12.1 | 16.0 | 17.3 |
| 500 | net3 | shared | 0.287 | 0.382 | 0.412 |
| 500 | net3 | indep | 0.365 | 0.486 | 0.524 |
| 1000 | win1 | shared | 7.7 | 10.3 | 11.1 |
| 1000 | win1 | indep | 10.1 | 13.5 | 14.5 |
| 1000 | net3 | shared | 0.214 | 0.285 | 0.307 |
| 1000 | net3 | indep | 0.321 | 0.427 | 0.461 |
| 2000 | win1 | shared | 5.4 | 7.1 | 7.7 |
| 2000 | win1 | indep | 8.4 | 11.1 | 12.0 |
| 2000 | net3 | shared | 0.148 | 0.197 | 0.213 |
| 2000 | net3 | indep | 0.281 | 0.373 | 0.403 |


### 6.2 The treated-cluster form (the module's default)

### Table 8. The placebo-selection twin (E-023): the worst realised level by selection model

Random filters independent of the outcomes, firing on 2 % to 50 % of P-16's judged offers; the selected offers' own outcome against every offer's (the twin's expectation).

| method | nulls | k = 11 (nominal 3.79) | k = 12 (nominal 3.21) | k = 13 (nominal 2.75) | k = 14 (nominal 2.38) | k = 15 (nominal 2.08) |
|---|---|---|---|---|---|---|
| `t21w` | selection: offer (5) | **1.28x** (4.85 [3.93, 5.92]; select:offer:0.02:win1) | **1.25x** (4.00 [3.17, 4.98]; select:offer:0.02:win1) | **1.27x** (3.50 [2.73, 4.42]; select:offer:0.02:win1) | **1.26x** (3.00 [2.29, 3.86]; select:offer:0.02:win1) | **1.30x** (2.70 [2.03, 3.52]; select:offer:0.5:win1) |
| `t21w` | selection: window (10) | **1.31x** (4.95 [4.02, 6.03]; select:window:0.25:win1) | **1.20x** (3.85 [3.04, 4.81]; select:window:0.25:win1) | **1.16x** (3.20 [2.46, 4.09]; select:window:0.25:win1) | **1.13x** (2.70 [2.03, 3.52]; select:window:0.25:win1) | **1.20x** (2.50 [1.86, 3.30]; select:window:0.25:win1) |
| `t21w` | selection: session (10) | **2.57x** (9.75 [8.43, 11.22]; select:session:0.05:win1) | **2.68x** (8.60 [7.36, 9.98]; select:session:0.05:win1) | **2.68x** (7.35 [6.21, 8.64]; select:session:0.02:net3) | **2.88x** (6.85 [5.75, 8.10]; select:session:0.02:net3) | **2.76x** (5.75 [4.75, 6.90]; select:session:0.02:net3) |
| `t21w` | selection: block5 (10) | **0.74x** (2.80 [2.12, 3.64]; select:block5:0.5:win1) | **0.69x** (2.20 [1.60, 2.95]; select:block5:0.25:net3) | **0.69x** (1.90 [1.34, 2.61]; select:block5:0.5:win1) | **0.63x** (1.50 [1.01, 2.14]; select:block5:0.25:net3) | **0.65x** (1.35 [0.89, 1.96]; select:block5:0.25:win1) |
| `t21w` | selection: block21 (10) | **0.37x** (1.40 [0.93, 2.02]; select:block21:0.5:net3) | **0.33x** (1.05 [0.65, 1.60]; select:block21:0.5:net3) | **0.31x** (0.85 [0.50, 1.36]; select:block21:0.5:net3) | **0.27x** (0.65 [0.35, 1.11]; select:block21:0.5:net3) | **0.31x** (0.65 [0.35, 1.11]; select:block21:0.5:net3) |
| `t21w` | selection: block63 (10) | **1.53x** (5.80 [4.79, 6.96]; select:block63:0.25:win1) | **1.28x** (4.10 [3.26, 5.09]; select:block63:0.25:win1) | **0.78x** (2.15 [1.56, 2.90]; select:block63:0.25:win1) | **0.42x** (1.00 [0.61, 1.54]; select:block63:0.25:win1) | **0.36x** (0.75 [0.42, 1.24]; select:block63:0.25:win1) |
| `t42w` | selection: offer (5) | **1.33x** (5.05 [4.11, 6.14]; select:offer:0.02:win1) | **1.26x** (4.05 [3.22, 5.03]; select:offer:0.02:win1) | **1.31x** (3.60 [2.82, 4.53]; select:offer:0.02:win1) | **1.30x** (3.10 [2.38, 3.97]; select:offer:0.02:win1) | **1.25x** (2.60 [1.94, 3.41]; select:offer:0.02:win1) |
| `t42w` | selection: window (10) | **1.17x** (4.45 [3.57, 5.48]; select:window:0.25:win1) | **1.20x** (3.85 [3.04, 4.81]; select:window:0.25:win1) | **1.18x** (3.25 [2.51, 4.14]; select:window:0.5:net3) | **1.26x** (3.00 [2.29, 3.86]; select:window:0.25:win1) | **1.30x** (2.70 [2.03, 3.52]; select:window:0.25:win1) |
| `t42w` | selection: session (10) | **2.64x** (10.00 [8.66, 11.49]; select:session:0.02:net3) | **2.59x** (8.30 [7.09, 9.66]; select:session:0.02:net3) | **2.77x** (7.60 [6.44, 8.91]; select:session:0.02:net3) | **3.02x** (7.20 [6.07, 8.48]; select:session:0.02:net3) | **2.98x** (6.20 [5.16, 7.39]; select:session:0.02:net3) |
| `t42w` | selection: block5 (10) | **0.79x** (3.00 [2.29, 3.86]; select:block5:0.5:win1) | **0.76x** (2.45 [1.81, 3.24]; select:block5:0.5:win1) | **0.73x** (2.00 [1.43, 2.72]; select:block5:0.5:win1) | **0.73x** (1.75 [1.22, 2.43]; select:block5:0.25:net3) | **0.72x** (1.50 [1.01, 2.14]; select:block5:0.5:win1) |
| `t42w` | selection: block21 (10) | **0.28x** (1.05 [0.65, 1.60]; select:block21:0.5:win1) | **0.23x** (0.75 [0.42, 1.24]; select:block21:0.5:win1) | **0.16x** (0.45 [0.21, 0.85]; select:block21:0.25:net3) | **0.19x** (0.45 [0.21, 0.85]; select:block21:0.25:net3) | **0.17x** (0.35 [0.14, 0.72]; select:block21:0.25:net3) |
| `t42w` | selection: block63 (10) | **0.00x** (0.00 [0.00, 0.18]; select:block63:0.02:win1) | **0.00x** (0.00 [0.00, 0.18]; select:block63:0.02:win1) | **0.00x** (0.00 [0.00, 0.18]; select:block63:0.02:win1) | **0.00x** (0.00 [0.00, 0.18]; select:block63:0.02:win1) | **0.00x** (0.00 [0.00, 0.18]; select:block63:0.02:win1) |
| `t63w` | selection: offer (5) | **1.15x** (4.35 [3.48, 5.37]; select:offer:0.02:win1) | **1.20x** (3.85 [3.04, 4.81]; select:offer:0.25:win1) | **1.20x** (3.30 [2.55, 4.20]; select:offer:0.25:win1) | **1.22x** (2.90 [2.20, 3.75]; select:offer:0.5:win1) | **1.22x** (2.55 [1.90, 3.35]; select:offer:0.5:win1) |
| `t63w` | selection: window (10) | **1.12x** (4.25 [3.39, 5.25]; select:window:0.25:win1) | **1.14x** (3.65 [2.86, 4.59]; select:window:0.25:win1) | **1.11x** (3.05 [2.33, 3.92]; select:window:0.25:win1) | **1.09x** (2.60 [1.94, 3.41]; select:window:0.02:net3) | **1.13x** (2.35 [1.73, 3.12]; select:window:0.5:net3) |
| `t63w` | selection: session (10) | **1.91x** (7.25 [6.12, 8.53]; select:session:0.02:net3) | **2.04x** (6.55 [5.48, 7.77]; select:session:0.05:win1) | **2.06x** (5.65 [4.66, 6.79]; select:session:0.05:win1) | **2.14x** (5.10 [4.16, 6.19]; select:session:0.02:net3) | **2.14x** (4.45 [3.57, 5.48]; select:session:0.05:win1) |
| `t63w` | selection: block5 (10) | **0.83x** (3.15 [2.42, 4.03]; select:block5:0.25:win1) | **0.83x** (2.65 [1.99, 3.47]; select:block5:0.25:win1) | **0.89x** (2.45 [1.81, 3.24]; select:block5:0.1:net3) | **0.94x** (2.25 [1.64, 3.01]; select:block5:0.1:net3) | **0.94x** (1.95 [1.39, 2.67]; select:block5:0.1:net3) |
| `t63w` | selection: block21 (10) | **0.66x** (2.50 [1.86, 3.30]; select:block21:0.5:win1) | **0.75x** (2.40 [1.77, 3.18]; select:block21:0.5:win1) | **0.69x** (1.90 [1.34, 2.61]; select:block21:0.5:win1) | **0.76x** (1.80 [1.26, 2.49]; select:block21:0.5:win1) | **0.77x** (1.60 [1.09, 2.26]; select:block21:0.5:win1) |
| `t63w` | selection: block63 (10) | **0.01x** (0.05 [0.00, 0.28]; select:block63:0.5:win1) | **0.02x** (0.05 [0.00, 0.28]; select:block63:0.5:win1) | **0.02x** (0.05 [0.00, 0.28]; select:block63:0.5:win1) | **0.00x** (0.00 [0.00, 0.18]; select:block63:0.02:win1) | **0.00x** (0.00 [0.00, 0.18]; select:block63:0.02:win1) |
| `cons` | selection: offer (5) | **0.16x** (0.60 [0.31, 1.05]; select:offer:0.5:win1) | **0.17x** (0.55 [0.27, 0.98]; select:offer:0.5:win1) | **0.20x** (0.55 [0.27, 0.98]; select:offer:0.5:win1) | **0.15x** (0.35 [0.14, 0.72]; select:offer:0.5:win1) | **0.17x** (0.35 [0.14, 0.72]; select:offer:0.5:win1) |
| `cons` | selection: window (10) | **0.16x** (0.60 [0.31, 1.05]; select:window:0.25:win1) | **0.14x** (0.45 [0.21, 0.85]; select:window:0.25:win1) | **0.13x** (0.35 [0.14, 0.72]; select:window:0.25:win1) | **0.13x** (0.30 [0.11, 0.65]; select:window:0.02:net3) | **0.12x** (0.25 [0.08, 0.58]; select:window:0.02:net3) |
| `cons` | selection: session (10) | **0.78x** (2.95 [2.25, 3.81]; select:session:0.02:net3) | **0.69x** (2.20 [1.60, 2.95]; select:session:0.02:net3) | **0.78x** (2.15 [1.56, 2.90]; select:session:0.02:net3) | **0.78x** (1.85 [1.30, 2.55]; select:session:0.02:net3) | **0.72x** (1.50 [1.01, 2.14]; select:session:0.02:net3) |
| `cons` | selection: block5 (10) | **0.13x** (0.50 [0.24, 0.92]; select:block5:0.1:net3) | **0.09x** (0.30 [0.11, 0.65]; select:block5:0.1:net3) | **0.09x** (0.25 [0.08, 0.58]; select:block5:0.25:net3) | **0.10x** (0.25 [0.08, 0.58]; select:block5:0.25:net3) | **0.10x** (0.20 [0.05, 0.51]; select:block5:0.25:net3) |
| `cons` | selection: block21 (10) | **0.01x** (0.05 [0.00, 0.28]; select:block21:0.5:win1) | **0.02x** (0.05 [0.00, 0.28]; select:block21:0.5:win1) | **0.00x** (0.00 [0.00, 0.18]; select:block21:0.02:win1) | **0.00x** (0.00 [0.00, 0.18]; select:block21:0.02:win1) | **0.00x** (0.00 [0.00, 0.18]; select:block21:0.02:win1) |
| `cons` | selection: block63 (10) | **0.00x** (0.00 [0.00, 0.18]; select:block63:0.02:win1) | **0.00x** (0.00 [0.00, 0.18]; select:block63:0.02:win1) | **0.00x** (0.00 [0.00, 0.18]; select:block63:0.02:win1) | **0.00x** (0.00 [0.00, 0.18]; select:block63:0.02:win1) | **0.00x** (0.00 [0.00, 0.18]; select:block63:0.02:win1) |

#### Table 8b. Nulls whose 95 % interval lies wholly above the nominal rate (k = 11)

| method | selection: offer (nulls) | selection: window (nulls) | selection: session (nulls) | selection: block5 (nulls) | selection: block21 (nulls) | selection: block63 (nulls) |
|---|---|---|---|---|---|---|
| `t21w` | 1 of 5 | 1 of 10 | 6 of 10 | 0 of 10 | 0 of 10 | 2 of 10 |
| `t42w` | 1 of 5 | 0 of 10 | 5 of 10 | 0 of 10 | 0 of 10 | 0 of 10 |
| `t63w` | 0 of 5 | 0 of 10 | 4 of 10 | 0 of 10 | 0 of 10 | 0 of 10 |
| `cons` | 0 of 5 | 0 of 10 | 0 of 10 | 0 of 10 | 0 of 10 | 0 of 10 |

### Table 9. The placebo-selection twin: the selected-minus-twin difference detectable at 80 % power, by firing share

(win1 in points of win probability; net3 in R; -- where 80 % is not reached inside the grid)

| model | value | share | `t21w` k=11 | `cons` k=11 | `cons` k=15 |
|---|---|---|---|---|---|
| offer | win1 | 0.02 | 5.3 | 7.1 | 7.7 |
| offer | win1 | 0.05 | 3.4 | 4.4 | 4.8 |
| offer | win1 | 0.1 | 2.3 | 3.1 | 3.3 |
| offer | win1 | 0.25 | 1.3 | 1.8 | 1.9 |
| offer | win1 | 0.5 | 0.8 | 1.0 | 1.1 |
| window | win1 | 0.02 | 5.4 | 7.2 | 7.8 |
| window | net3 | 0.02 | 0.196 | 0.261 | 0.282 |
| window | win1 | 0.05 | 3.5 | 4.7 | 5.1 |
| window | net3 | 0.05 | 0.155 | 0.205 | 0.223 |
| window | win1 | 0.1 | 2.6 | 3.5 | 3.8 |
| window | net3 | 0.1 | 0.132 | 0.175 | 0.188 |
| window | win1 | 0.25 | 1.6 | 2.2 | 2.3 |
| window | net3 | 0.25 | 0.093 | 0.124 | 0.133 |
| window | win1 | 0.5 | 1.0 | 1.3 | 1.4 |
| window | net3 | 0.5 | 0.059 | 0.079 | 0.086 |
| session | win1 | 0.02 | 10.5 | 13.4 | 14.9 |
| session | net3 | 0.02 | 0.790 | 1.019 | 1.147 |
| session | win1 | 0.05 | 4.9 | 6.1 | 6.6 |
| session | net3 | 0.05 | 0.374 | 0.473 | 0.514 |
| session | win1 | 0.1 | 3.1 | 4.0 | 4.3 |
| session | net3 | 0.1 | 0.240 | 0.317 | 0.340 |
| session | win1 | 0.25 | 1.7 | 2.3 | 2.5 |
| session | net3 | 0.25 | 0.138 | 0.185 | 0.197 |
| session | win1 | 0.5 | 1.0 | 1.3 | 1.5 |
| session | net3 | 0.5 | 0.079 | 0.107 | 0.118 |
| block5 | win1 | 0.02 | -- | -- | -- |
| block5 | net3 | 0.02 | -- | -- | -- |
| block5 | win1 | 0.05 | 12.0 | 23.9 | 30.6 |
| block5 | net3 | 0.05 | 0.858 | 1.708 | 2.279 |
| block5 | win1 | 0.1 | 4.5 | 6.0 | 6.7 |
| block5 | net3 | 0.1 | 0.291 | 0.386 | 0.436 |
| block5 | win1 | 0.25 | 2.1 | 2.7 | 3.0 |
| block5 | net3 | 0.25 | 0.138 | 0.185 | 0.202 |
| block5 | win1 | 0.5 | 1.2 | 1.7 | 2.0 |
| block5 | net3 | 0.5 | 0.079 | 0.115 | 0.130 |
| block21 | win1 | 0.02 | -- | -- | -- |
| block21 | net3 | 0.02 | -- | -- | -- |
| block21 | win1 | 0.05 | -- | -- | -- |
| block21 | net3 | 0.05 | -- | -- | -- |
| block21 | win1 | 0.1 | -- | -- | -- |
| block21 | net3 | 0.1 | -- | -- | -- |
| block21 | win1 | 0.25 | 3.4 | 11.8 | -- |
| block21 | net3 | 0.25 | 0.177 | 0.532 | -- |
| block21 | win1 | 0.5 | 1.9 | -- | -- |
| block21 | net3 | 0.5 | 0.097 | -- | -- |
| block63 | win1 | 0.02 | -- | -- | -- |
| block63 | net3 | 0.02 | -- | -- | -- |
| block63 | win1 | 0.05 | -- | -- | -- |
| block63 | net3 | 0.05 | -- | -- | -- |
| block63 | win1 | 0.1 | -- | -- | -- |
| block63 | net3 | 0.1 | -- | -- | -- |
| block63 | win1 | 0.25 | 8.0 | -- | -- |
| block63 | net3 | 0.25 | 0.400 | -- | -- |
| block63 | win1 | 0.5 | 3.2 | -- | -- |
| block63 | net3 | 0.5 | 0.154 | -- | -- |

### Table 10. F-02's C1' (E-022), the level lift minus the placebo lift: the worst realised level

| method | nulls | k = 11 (nominal 3.79) | k = 12 (nominal 3.21) | k = 13 (nominal 2.75) | k = 14 (nominal 2.38) | k = 15 (nominal 2.08) |
|---|---|---|---|---|---|---|
| `t21w` | C1': shared (24) | **3.76x** (14.25 [12.64, 16.00]; c1p:500:net3:shared63) | **3.32x** (10.65 [9.27, 12.18]; c1p:500:net3:shared63) | **3.24x** (8.90 [7.64, 10.31]; c1p:500:net3:shared63) | **3.07x** (7.30 [6.16, 8.58]; c1p:500:net3:shared63) | **2.93x** (6.10 [5.07, 7.28]; c1p:500:net3:shared63) |
| `t21w` | C1': indep (24) | **2.97x** (11.25 [9.83, 12.82]; c1p:500:net3:indep63) | **2.87x** (9.20 [7.92, 10.63]; c1p:500:net3:indep63) | **2.93x** (8.05 [6.85, 9.39]; c1p:500:net3:indep63) | **2.88x** (6.85 [5.75, 8.10]; c1p:500:net3:indep63) | **2.95x** (6.15 [5.11, 7.34]; c1p:500:net3:indep63) |
| `t21w` | C1': coin (8) | **1.41x** (5.35 [4.38, 6.46]; c1p:200:net3:coin) | **1.59x** (5.10 [4.16, 6.19]; c1p:200:net3:coin) | **1.69x** (4.65 [3.75, 5.70]; c1p:200:net3:coin) | **1.72x** (4.10 [3.26, 5.09]; c1p:200:net3:coin) | **1.56x** (3.25 [2.51, 4.14]; c1p:200:net3:coin) |
| `t42w` | C1': shared (24) | **1.89x** (7.15 [6.03, 8.42]; c1p:500:net3:shared63) | **2.00x** (6.40 [5.34, 7.61]; c1p:500:net3:shared63) | **2.02x** (5.55 [4.57, 6.68]; c1p:500:net3:shared63) | **1.93x** (4.60 [3.71, 5.64]; c1p:500:net3:shared63) | **1.87x** (3.90 [3.08, 4.87]; c1p:500:net3:shared63) |
| `t42w` | C1': indep (24) | **1.32x** (5.00 [4.07, 6.08]; c1p:500:win1:indep21) | **1.29x** (4.15 [3.31, 5.14]; c1p:500:win1:indep21) | **1.27x** (3.50 [2.73, 4.42]; c1p:500:win1:indep21) | **1.34x** (3.20 [2.46, 4.09]; c1p:500:net3:indep21) | **1.42x** (2.95 [2.25, 3.81]; c1p:500:net3:indep21) |
| `t42w` | C1': coin (8) | **1.23x** (4.65 [3.75, 5.70]; c1p:500:win1:coin) | **1.25x** (4.00 [3.17, 4.98]; c1p:500:win1:coin) | **1.26x** (3.45 [2.68, 4.37]; c1p:500:win1:coin) | **1.22x** (2.90 [2.20, 3.75]; c1p:1000:net3:coin) | **1.27x** (2.65 [1.99, 3.47]; c1p:500:win1:coin) |
| `t63w` | C1': shared (24) | **4.20x** (15.90 [14.20, 17.75]; c1p:500:win1:shared63) | **4.15x** (13.30 [11.75, 15.00]; c1p:500:win1:shared63) | **4.19x** (11.50 [10.06, 13.09]; c1p:500:win1:shared63) | **3.99x** (9.50 [8.20, 10.95]; c1p:500:win1:shared63) | **3.91x** (8.15 [6.95, 9.50]; c1p:500:win1:shared63) |
| `t63w` | C1': indep (24) | **1.41x** (5.35 [4.38, 6.46]; c1p:500:win1:indep63) | **1.45x** (4.65 [3.75, 5.70]; c1p:500:win1:indep63) | **1.46x** (4.00 [3.17, 4.98]; c1p:500:win1:indep63) | **1.41x** (3.35 [2.60, 4.25]; c1p:500:win1:indep63) | **1.32x** (2.75 [2.07, 3.58]; c1p:200:net3:indep1) |
| `t63w` | C1': coin (8) | **1.25x** (4.75 [3.84, 5.81]; c1p:1000:net3:coin) | **1.34x** (4.30 [3.44, 5.31]; c1p:1000:net3:coin) | **1.35x** (3.70 [2.91, 4.64]; c1p:1000:net3:coin) | **1.39x** (3.30 [2.55, 4.20]; c1p:1000:net3:coin) | **1.25x** (2.60 [1.94, 3.41]; c1p:500:win1:coin) |
| `cons` | C1': shared (24) | **0.49x** (1.85 [1.30, 2.55]; c1p:500:net3:shared63) | **0.42x** (1.35 [0.89, 1.96]; c1p:500:net3:shared63) | **0.49x** (1.35 [0.89, 1.96]; c1p:500:net3:shared63) | **0.36x** (0.85 [0.50, 1.36]; c1p:500:net3:shared63) | **0.24x** (0.50 [0.24, 0.92]; c1p:2000:net3:shared63) |
| `cons` | C1': indep (24) | **0.24x** (0.90 [0.53, 1.42]; c1p:500:net3:indep21) | **0.17x** (0.55 [0.27, 0.98]; c1p:1000:win1:indep21) | **0.16x** (0.45 [0.21, 0.85]; c1p:500:win1:indep21) | **0.17x** (0.40 [0.17, 0.79]; c1p:2000:net3:indep21) | **0.19x** (0.40 [0.17, 0.79]; c1p:2000:net3:indep21) |
| `cons` | C1': coin (8) | **0.22x** (0.85 [0.50, 1.36]; c1p:1000:net3:coin) | **0.23x** (0.75 [0.42, 1.24]; c1p:1000:net3:coin) | **0.20x** (0.55 [0.27, 0.98]; c1p:1000:net3:coin) | **0.19x** (0.45 [0.21, 0.85]; c1p:1000:net3:coin) | **0.14x** (0.30 [0.11, 0.65]; c1p:500:win1:coin) |

#### Table 10b. Nulls whose 95 % interval lies wholly above the nominal rate (k = 11)

| method | C1': shared (nulls) | C1': indep (nulls) | C1': coin (nulls) |
|---|---|---|---|
| `t21w` | 5 of 24 | 8 of 24 | 1 of 8 |
| `t42w` | 3 of 24 | 2 of 24 | 0 of 8 |
| `t63w` | 7 of 24 | 3 of 24 | 1 of 8 |
| `cons` | 0 of 24 | 0 of 24 | 0 of 8 |

### Table 11. C1': the difference D detectable at 80 % power (placebo fills five times the level's; sides flipped by session)

| level fills | value | sides | `t21w` k=11 | `cons` k=11 | `cons` k=15 |
|---|---|---|---|---|---|
| 200 | win1 | shared | 17.4 | 23.2 | 25.0 |
| 200 | win1 | indep | 18.2 | 24.2 | 26.1 |
| 200 | net3 | shared | 0.475 | 0.633 | 0.683 |
| 200 | net3 | indep | 0.526 | 0.703 | 0.758 |
| 500 | win1 | shared | 10.4 | 13.8 | 14.9 |
| 500 | win1 | indep | 12.1 | 16.0 | 17.3 |
| 500 | net3 | shared | 0.287 | 0.382 | 0.412 |
| 500 | net3 | indep | 0.365 | 0.486 | 0.524 |
| 1000 | win1 | shared | 7.7 | 10.3 | 11.1 |
| 1000 | win1 | indep | 10.1 | 13.5 | 14.5 |
| 1000 | net3 | shared | 0.214 | 0.285 | 0.307 |
| 1000 | net3 | indep | 0.321 | 0.427 | 0.461 |
| 2000 | win1 | shared | 5.4 | 7.1 | 7.7 |
| 2000 | win1 | indep | 8.4 | 11.1 | 12.0 |
| 2000 | net3 | shared | 0.148 | 0.197 | 0.213 |
| 2000 | net3 | indep | 0.281 | 0.373 | 0.403 |


## 7. The choices, and what they cannot do

### 7.1 The pass line: `cons`

The brief's rule was to pick the candidate that holds its level with the most power. Only `cons` holds (Tables 1, 1b,
2).

**Where each single statistic fails:**
- The 21-session statistics (`t21e`, `t21w`, `hac21`) are lax when a side persists past the block on dense streams.
  Blocks that straddle a persistent side are correlated, and the family level's tail turns the variance this hides
  into a multiple of the level.
- `t42w` and `t63w` hold there, but fail on the `taken` stream at persistence 5-21 sessions. `t63w` also fails on
  sparse streams, with 10 blocks and df 9 deep in the tail.
- The bootstrap (Table 3) uses the same 21-session blocks and does not repair this. It is as lax as `t21w`, or more,
  on the dense persistent null.

**Why `cons` holds.** Its members fail on different nulls, so their intersection holds on every real and realistic
null. It is lax only on the strongest stress regime, `regime10` at 2,000 and 5,000 trades (Table 1b: 2 of 20 stress nulls), well past the data; on `skew` at 200 trades it is at its level.

**What it costs.** Its power is about that of `t63w` (Table 4). On a calendar much shorter than the judged block's 657
sessions, `t63w` has too few blocks, and `cons` loses power quickly (section 7.4, item 2).

### 7.2 The P comparison: `pcons` now, `bm63c` once its table is pinned

**Where the others fail** (Tables 5, 5b):
- Stage 2's line is lax by two orders of magnitude at the family levels.
- The batch-means t (`bm63`) is lax several times over on real and realistic nulls (red team M3 confirmed).
- The overlapping-batch t's, `bm126` and the flat-top `ft63` are lax on real nulls.

**The cause** (section 7.4's failed check found it): every batch-type variance is biased low on this series. Each
start's month-3 window overlaps its neighbours' for 63 starts.

**Why `pcons` is shipped.** It holds everywhere and needs no table. But its minimum detectable difference equals the
flat-top's, which can detect nothing a design could achieve here (Table 6).

**Why `bm63c` is recommended.** It holds on every real and realistic null on fresh replications, with a critical value
about a fifth to a quarter above t(8)'s (Table 7), at a fraction of `pcons`'s minimum detectable difference. It is lax
on the stress null, a design edge difference persisting for many months. Its table must come from a clean-checkout run
and be pinned under a decision row; until then `p_bound` refuses to read it without the table.

**What P can detect.** Even with `bm63c`, the judged block's P comparison can detect only a variant close to P-14's own
trades, as E-007 (2) and the red team's M2 found.

### 7.3 The two-sample forms

**Both forms use `cons`**, the same intersection as the pass line, on the two-sample difference with the
treated-cluster block count (`placebo_selection_bound`, `two_sample_bound`; section 1.3).

**E-023's placebo-selection twin** (Tables 8, 8b, 9).
- **The level.** `cons` holds on all 55 selection nulls: filters on single offers, on time windows within sessions, on
  whole sessions and on persistent blocks of 5, 21 and 63 sessions, at shares from 2 % to 50 %. Every single member
  stays lax on whole-session filters.
- **The power** (Table 9) depends far more on how persistent the filter is than on its share.
  - A filter that picks offers or time windows inside sessions can be tested at every share.
  - A filter persistent across sessions has few independent units. A regime filter firing on a few quarters is
    untestable on this block: Table 9's "--" means 80 % power is not reached even at a shift of 40 standard errors.
  - So a family declaring a side-keeping filter should state its persistence and read its minimum detectable
    difference from Table 9 before it is pinned.
- **The expectation twin**, the population mean, carries no placebo noise. A family that uses one seeded random draw
  as the twin is doing a two-sample comparison of two random subsets, and loses power for it.

**E-022's C1'** (Tables 10, 10b, 11).
- **The level.** `cons` holds on all 56 nulls: level fills of 200 to 2,000 against five times as many placebo fills;
  sides shared, independent or the coin's; persistence 1, 21 and 63 sessions. Every single member exceeds its level on
  some of them.
- **The form can be calibrated, so the draft need not drop it.** It needs one correction to the draft's section 9.2:
  the variance must come from the residual, count-centred session sums (section 1.3), not from the raw `z_s`.
- **Its minimum detectable difference** is in Table 11. It is larger than C1's at the same fill count, because the
  placebo's own noise adds. A shared side, where the level's and the placebo's sides move together, cancels part of it.

### 7.4 What it cannot do, and what stays on record

1. **A level is only as good as the null class.** The statistics hold against sides that persist up to a quarter and
   against the clustering in P-16's trades, and they fail against the stress regimes. A family file should state its
   side's (or its filter's) persistence before it is pinned.
2. **`cons` on a short calendar.** A fixed-null power test written before the choice, on 300 sessions, expected a
   5-standard-error lift found 90 % of the time. `cons` found it 62.6 %, because its 63-session member had 4 blocks
   there.
   - The test is kept, unchanged, as a strict expected failure. The diagnosis is `docs/research/scripts/q16/diag_power.py`.
   - On the judged block's 657 sessions `cons` finds the same lift about 96 % of the time
     (`test_power_on_the_judged_calendar`).
   - A reverse walk-forward or a per-year reading on a shorter calendar has much less power.
3. **A failed check on the P module, kept on record.** Its first placeholder statistic (`obm126`) failed its
   fixed-null size test: 279 of 20,000 rejections at 1 % on a Gaussian moving average over 21 starts. The diagnosis:
   - fresh replications gave the same rate;
   - the statistic is exact on iid series;
   - its variance's expectation is below the true variance (`docs/research/scripts/q16/diag_obm.py`): the batch bias of 7.2.
   
   The test was not loosened. The calibration chose `pcons`, and the same test passes for it.
4. **A defect found and fixed.** `lift_bound.bound()` gave a positive lower limit when the standard error was exactly
   zero (every trade in one block). The vectorised functions the calibration used already refused that case, so no
   calibration figure is affected. `test_degenerate_samples_never_pass` now covers it.
5. **The sign-flip null with few flip blocks** is a conditional, discrete null. Some statistics reject less often than
   nominal there (L = 63). That is a property of the null.
6. **`taken`** approximates P-16's schedule (section 2.1).
7. **The two-sample form's first version failed its calibration.** With the df and CR1's factor from every block,
   every statistic, `cons` included, held for filters that pick offers or windows within sessions. But it was lax by
   several to hundreds of times for filters firing on whole sessions or blocks (Tables F8, F8b).
   - The diagnosis: few treated clusters. Only the blocks holding selected offers carry sample 1's variance, while the
     df counted all 31 blocks. A fixed-null test (`test_persistent_selection_first_form_fails_and_treated_form_holds`)
     asserts the failure.
   - Counting the selected sample's blocks is the correction (section 1.3). Even then, a single member (`t21w`) stays
     a little lax on a short whole-session null: a strict expected failure, with its diagnosis in
     `docs/research/scripts/q16/diag_treated.py`. Only the intersection holds.
8. **Drift.** The lift credits a long-leaning rule with the drift (Phase 0 D-12). Whether the drift-matched lift is the
   estimand is the family's to declare.
9. **The bootstrap's** family-level rates have wide intervals. It was not chosen.
10. **Not calibrated:** the value-map price at the bound (E-008's second condition), and the placebo's construction in
   F-02 (its source days, its scaling). C1' is calibrated here as a two-sample statistic on real fills; whether F-02's
   placebo tickets match the level's fills is F-02's T-14 (c).

## 8. Reproduction

```
python scripts/q16_p16_pairs.py --out <dir>/pairs                     # reads the development bars: under run.lock
python scripts/q16_calibrate.py --out <dir>/lift   --pairs <dir>/pairs/p16_pairs.parquet --part lift
python scripts/q16_calibrate.py --out <dir>/p      --part p
python scripts/q16_calibrate.py --out <dir>/select --pairs <dir>/pairs/p16_pairs.parquet --part select
python scripts/q16_calibrate.py --out <dir>/select_all --pairs <dir>/pairs/p16_pairs.parquet --part select --diff-df all   # the first form
python scripts/q16_tables.py --dir <dir>/lift ; python scripts/q16_tables.py --dir <dir>/p ; python scripts/q16_tables.py --dir <dir>/select
```

The runs behind the tables (this worktree, 2026-11-16; scratch outputs, not result files; replications at the
script's defaults: 200,000, the bootstrap 20,000, D-621's line 20,000, the power curves 5,000). How each run's code
relates to this note's commit:
- `cal_lift` ran clean at 568c2a4. The lift's calibration path is unchanged since.
- `cal_p` ran on 568c2a4 plus the then-uncommitted P code, which equals 2f5ffd0's except `SHIPPED`, `RECOMMENDED` and
  `bm63c`'s table reader. The calibration does not call those.
- `cal_sel_all` ran on 568c2a4 plus the uncommitted two-sample code, which equals 2f5ffd0's. 3a7a3f5 reproduces it
  with `--diff-df all`.
- `cal_sel` ran at 3a7a3f5; it reads "dirty" only because this note was untracked.

| run | part | commit | tree | arguments | seconds | peak working set (MB) | under run.lock |
|---|---|---|---|---|---|---|---|
| `cal_lift` | lift | `568c2a4` | clean | --out --pairs --part lift | 5738 | 895 | yes |
| `cal_p` | p | `568c2a4` | dirty | --out --part p | 1432 | 486 | yes |
| `cal_sel_all` | select | `568c2a4` | dirty | --out --pairs --part select | 1094 | 763 | yes |
| `cal_sel` | select | `3a7a3f5` | dirty | --out --pairs --part select | 976 | 838 | yes |

Seeds (the brief's 20261910-20261919, fixed before any run):

| seed | use |
|---|---|
| 20261910, 20261911, 20261912 | the tests' fixed nulls |
| 20261913 | `lift_bound`'s fixed-b table (derived by offset: seed + 1000 G + lags) |
| 20261914 | the bootstrap's resample matrix |
| 20261915 | the lift's real nulls, and the two-sample forms' (sub-streams `[20261915, 5000 + i]`, `[.., 7000 + i]`, `[.., 9000]`) |
| 20261916 | the lift's synthetic nulls |
| 20261917, 20261918 | the P comparison's real and synthetic nulls (`bm63c`'s validation at `[seed, 1000 + i]`) |
| 20261919 | `p_bound`'s fixed-b tables |
