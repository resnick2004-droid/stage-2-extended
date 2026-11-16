# Red team: the pass-line code -- `extended/lift_bound.py`, `extended/p_bound.py` and Q-16's calibration, 2026-11-16

The red team, read-only, in worktree `wt-verify` (branch `wt/wt-verify`) at master 57d7ed8 (TASK_QUEUE Q-68). This
read comes before the first family, F-02, is pinned on this code.

**The target.**
- `extended/lift_bound.py`: `SHIPPED = "cons"`, `bound`, `two_sample_bound`, `placebo_selection_bound` and the
  functions they call.
- `extended/p_bound.py`: `pcons`, and `bm63c`'s table reader.
- The calibration that chose them: `scripts/q16_p16_pairs.py`, `scripts/q16_calibrate.py`, `scripts/q16_tables.py` and
  `scripts/q55_calibration.py`.
- Their tests: `tests/test_lift_bound.py`, `tests/test_p_bound.py` and `tests/test_q55_calibration.py`.

**What I read it against:**
- `CHARTER.md` sections 2-3;
- `DECISIONS.md` E-008, E-022, E-023, E-035 (line 42), E-042 and E-044;
- the brief `docs/briefs/Q-16_2026-11-15.md`;
- `docs/research/calibration_2026-11-15.md`, all of it;
- `prereg/DRAFT_F-02_resting_levels.md` v5: its status lines 14-18, C1 (9.1, lines 678-700), C1' (9.2, lines
  701-733), 9.6, 14, and 18.2 with the blob ids at lines 1333-1336;
- the v4 red-team read of F-02 (`docs/reviews/DRAFT_F-02_resting_levels_v4_2026-11-16.md`), so as not to repeat its
  N1 and N2;
- `extended/reader.py`, `extended/results.py`, and the one-door scan in `tests/test_reader.py`;
- in the vendored tree: `propedge/research/user_journey.py` (`block_indices`), `propedge/research/atlas_walk.py` and
  `scripts/atlas_screen.py` (what A1's `days.parquet` is).

**What I ran.** Synthetic only, in the session scratchpad, one process at a time, one BLAS thread, each under 200 MB.
The seeds were fixed in each script before it ran: 68680001-68680005 and 68680010-68680041, outside the program's 2026
space. The scratchpad is not durable, so the code is in Appendix A.
- `checks.py` and `edge2.py`: hand and consistency checks, and degenerate inputs.
- `intensity.py` and `intensity2.py`: `cons`'s size when the fills' rate persists across sessions, at 200,000
  replications a row.

Every figure marked *synthetic* is red-team arithmetic on simulated data. It decides nothing.

**Not done.**
- No read of `data/bars` or `data/atlas`. I took metadata only: the data folders' sizes, and the bytes of the two
  modules in Q-55's clean checkout, through `git hash-object`.
- No engine, and no slow or heavy test.
- No result file read.
- No judged-block outcome read.
- **Disclosure.** To see whether the heavy run was still going, I read the last five lines of Q-55's log. They were
  rejection counts on synthetic nulls. I cite none of them, and nothing below rests on them.

**On the brief.** It lists places to look, and I took them as scope. It says the read comes "before the first family is
pinned on it", which leans towards a pin soon; I set that lean aside. It names c7e01bd as Q-55's commit, and I
checked that rather than assume it.

**Labels.** Severity is CHANGES-A-CONCLUSION, MATERIAL, MINOR or NOTE.

---

## Verdict

**Stands with readings.** The code computes what E-008, E-022, E-023, E-035, CHARTER sections 2-3 and F-02's C1, C1'
and 9.1 say:
- the per-trade mean;
- the CR1 residual block sums, with G' / (G' - 1) and df = G' - 1 (G' the non-empty blocks);
- the one-sided upper t quantile;
- `cons` as the minimum of the three members' lower bounds;
- C1''s count-centred u_g with the treated-cluster count Gt = min(G1', G2');
- the placebo-selection twin as the population mean.

The modules' blobs are the ones F-02 pins. They are identical at 57d7ed8, at c7e01bd, and in Q-55's running checkout.
**No defect found changes a declared rule.**

Two readings are MATERIAL and should be acted on **before F-02's pin**. Neither changes the code. Both bear on whether
the pass line delivers its level *for F-02*, and on whether Q-55 could show that it does not.

| id | severity | finding | where |
|---|---|---|---|
| M1 | MATERIAL | **No Q-16 null lets the fills' rate persist across sessions.** On synthetic nulls where it does, `cons` reaches its level when one quarter carries ten times the rest's rate, and exceeds it when log-intensity is AR(1) 0.98 with sd 1.5: 1.60x [1.33, 1.91] at 200 fills and 2.51x [2.16, 2.89] at 1,300 fills, at 0.05/132 (*synthetic*). It holds for trends up to 3x and sd up to 1.0. F-02's claim to sit "inside the class Q-16 calibrated against" rests on side persistence only | `scripts/q16_calibrate.py` 165-168, 207-214, 689-696; the note's 2.1-2.2 and 7.4 item 1; F-02 694-696 |
| M2 | MATERIAL | **Q-55 replays Q-16's own replications**, with the same seeds, the same pairs and the same code. It checks provenance (that the committed code reproduces figures first made partly from uncommitted trees). It is not a test of the choices made on those replications: the treated block count was devised after the first form failed and was judged on the same draws, and `cons` was picked from the seven candidates by the brief's rule. As written, F-02's gate (status, M3) "withdrawn if Q-55 does not reproduce `cons` holding" can fail only through a code or environment change, and its criterion for "holding" is not fixed | `scripts/q55_calibration.py` 123-130; `scripts/q16_calibrate.py` 64-67, 267, 640, 689, 699; F-02 14-18 |
| m1 | MINOR | The level is not checked. Passing `level = 1 - 0.05/132` (a confidence passed as a level), or 0.9, makes a **negative** lift pass (*synthetic*: estimate -0.0100, lower +0.0381) | `lift_bound.py` 266, 429, 435-454 |
| m2 | MINOR | The verdict depends on the calendar the caller passes, and the module checks only that the ordinals fit. Padding 657 to 700 sessions, or compressing to the days with a fill, changed 43 of 600 verdicts at 0.01 (*synthetic*). F-02 names the day list in words and writes its count after the run | `lift_bound.py` 69-93; F-02 686-689 |
| m3 | MINOR | The one-door exemption certifies itself (any `E-ddd` passes). The exempted read of A1's `days.parquet` is labelled "this repository's own derived file ... not Stage 2's bars or walks", but it is an atlas walk table by the reader's own list, read in full, and unledgered inside Q-55. Its content is dates and day kinds, so nothing of an outcome is read | `tests/test_reader.py` 867; `scripts/q16_calibrate.py` 126; `extended/reader.py` 764-765; E-035 (5) |
| m4 | MINOR | `t_block` at a block other than 21, 42 or 63 keeps the zero-se defect the note says was fixed in `bound()`: a constant +0.5 sample "passes" at 0.05/132 on 5-, 10- or 126-session blocks (*synthetic*). F-02 does not call it | `lift_bound.py` 459-465 |
| n1-n10 | NOTE | Docstrings ("b or b + 1"; G for G'); `_diff_bound` takes any method label; `Bound.blocks` in the two-sample forms; the exact `se > 0` guard; `p_bound`'s floor of 1.25e-4; `q55`'s stale reader text, manifest seed and partial writes; `p_bound`'s direct CSV reads; the statistic chosen on judged-block data of other designs; library versions not recorded | below |

---

## Findings

### M1 (MATERIAL) -- fill intensity that persists across sessions is outside the calibrated null class

**Evidence: what the calibration's nulls hold.**
- The real streams are `offered`, every five-minute mark, about 141 a session; `taken`; and `thinN`, seeded uniform
  thinnings (`q16_calibrate.py` 150-168).
- **Each `thinN` stream is one fixed subset.** It is drawn once, with `default_rng([20261915, 999])` (165-168), and only
  the signs vary across replications. So each size's rate is conditional on one count pattern, close to uniform in
  expectation.
- The C1' nulls' level/placebo split is likewise one fixed uniform split per fill count (689-696).
- The synthetic counts are Poisson or negative binomial, **iid across sessions** (207-214).
- No null lets the number of fills a session persist: no busy quarter, no volatility regime in the counts.
  `volclust` clusters the outcome's volatility, not the counts.
- The note's 7.4 item 1 and E-035 (6) ask a family to state its **side's** persistence. F-02 9.1 (694-696) does that,
  and concludes it is "inside the class Q-16 calibrated against".

**Why counts matter.** CR1 with G' - 1 df treats the blocks as comparable units. When a few blocks carry most of the
trades, the trade-weighted mean is mostly those blocks, and the effective number of clusters falls well below G'. The
variance estimate is then too small for the t reference (Carter, Schnepel and Steigerwald 2017, *REStat*; MacKinnon and
Webb 2017, *JAE*).

F-02's fills are orders resting at price levels. How many fill on a day depends on how far and how often the price
travels, which moves with volatility regimes lasting weeks to months. Its fills are as likely to bunch as anything this
program will test.

**Evidence: *synthetic*** (`intensity.py`, `intensity2.py`; Appendix A).
- **The outcome model** is Q-16's own `cluster`: each fill is 1/2 sign(a_s + e), with the session effect icc 0.35 and
  symmetric. So the null is exact, and sides reset daily, as in F-02.
- **The counts** have mean m a session on 657 sessions, under these profiles:
  - iid negative binomial, Q-16's form;
  - a linear trend in the rate, last session's rate 2x or 3x the first's;
  - log-intensity AR(1) at 0.98 or 0.995 across sessions, stationary sd 0.7, 1.0 or 1.5, Poisson given it;
  - one random 63-session quarter at 10x the rest's rate.
- 200,000 replications a row; rate / nominal, with its 95 % Clopper-Pearson interval.
- "Top share" is the busiest 63-session block's share of the fills (median, p90). Under uniform counts it is about a
  tenth.

| counts | fills a session | top share | `t21w` at 0.05/132 | `t63w` at 0.05/132 | **`cons` at 0.05/132** | `cons` at 0.001 | `cons` at 0.01 |
|---|---|---|---|---|---|---|---|
| iid (Q-16's form) | 0.3 | 0.14, 0.16 | 1.28x [1.04, 1.56] | 1.28x [1.04, 1.56] | 0.24x [0.14, 0.38] | 0.29x [0.22, 0.38] | 0.49x [0.46, 0.53] |
| iid | 2.0 | 0.12, 0.14 | 1.19x [0.96, 1.46] | 1.07x [0.85, 1.33] | 0.20x [0.11, 0.33] | 0.24x [0.18, 0.32] | 0.45x [0.42, 0.48] |
| trend 2x | 0.3 | -- | -- | -- | 0.22x [0.13, 0.36] | 0.25x [0.19, 0.33] | 0.46x [0.44, 0.50] |
| trend 2x | 2.0 | -- | -- | -- | 0.11x [0.05, 0.21] | 0.21x [0.16, 0.29] | 0.44x [0.41, 0.47] |
| trend 3x | 0.3 | -- | -- | -- | 0.22x [0.13, 0.36] | 0.31x [0.24, 0.40] | 0.48x [0.45, 0.52] |
| trend 3x | 2.0 | -- | -- | -- | 0.21x [0.12, 0.34] | 0.25x [0.19, 0.33] | 0.46x [0.43, 0.49] |
| AR 0.98, sd 0.7 | 0.3 | -- | -- | -- | 0.22x [0.13, 0.36] | 0.34x [0.27, 0.44] | 0.56x [0.52, 0.59] |
| AR 0.98, sd 0.7 | 2.0 | -- | -- | -- | 0.25x [0.15, 0.39] | 0.32x [0.24, 0.40] | 0.57x [0.53, 0.60] |
| AR 0.98, sd 1.0 | 0.3 | 0.25, 0.37 | 2.75x [2.39, 3.14] | 2.73x [2.37, 3.13] | 0.42x [0.29, 0.60] | 0.44x [0.35, 0.54] | 0.70x [0.67, 0.74] |
| AR 0.995, sd 1.0 | 0.3 | 0.23, 0.33 | 2.14x [1.82, 2.49] | 2.63x [2.27, 3.02] | 0.53x [0.38, 0.72] | 0.55x [0.45, 0.66] | 0.63x [0.59, 0.66] |
| one quarter at 10x | 0.3 | 0.41, 0.52 | 4.92x [4.44, 5.45] | 5.54x [5.03, 6.10] | 0.86x [0.66, 1.09] | 1.06x [0.92, 1.21] | 1.02x [0.97, 1.06] |
| one quarter at 10x | 2.0 | 0.41, 0.51 | 8.09x [7.46, 8.76] | 7.64x [7.03, 8.29] | 1.16x [0.93, 1.43] | 1.09x [0.95, 1.24] | **1.12x [1.07, 1.17]** |
| AR 0.98, sd 1.5 | 0.3 | 0.33, 0.53 | 5.91x [5.38, 6.49] | 8.50x [7.86, 9.18] | **1.60x [1.33, 1.91]** | **1.35x [1.20, 1.53]** | 1.03x [0.99, 1.08] |
| AR 0.98, sd 1.5 | 2.0 | 0.32, 0.52 | 9.20x [8.53, 9.91] | 14.53x [13.69, 15.42] | **2.51x [2.16, 2.89]** | **2.04x [1.85, 2.25]** | **1.23x [1.18, 1.28]** |

C1''s treated two-sample `cons` on the same counts. Level fills at m1 a session and placebo fills at 5 m1 share the
profile and the day's session effect, so their means are equal (the C1' null).

| counts | m1 0.3 at 0.05/132 | m1 1.0 at 0.05/132 |
|---|---|---|
| AR 0.98, sd 0.7 | 0.24x [0.14, 0.38] | 0.25x [0.15, 0.39] |
| AR 0.98, sd 1.0 | 0.50x [0.35, 0.69] | 0.41x [0.28, 0.58] |
| AR 0.98, sd 1.5 | 0.81x [0.62, 1.03] | 0.90x [0.70, 1.14] |

**What this shows.**
- `cons` holds with room where the counts are uniform, trend, or vary moderately.
- Its margin shrinks as the fills concentrate. It is at nominal when about four tenths of the fills sit in one quarter,
  and above it, with intervals wholly above, when the log-intensity sd is 1.5.
- Every single member is lax, by 2x to 15x, on every heterogeneous profile where I ran the members. `cons` holds only
  where they disagree.
- The C1' form holds on these profiles, because the shared day effect cancels, but its margin shrinks the same way.

**The failure it allows.** Suppose a pick whose judged fills bunch in volatile stretches as strongly as the sd 1.5 row,
with no direction at all. It passes C1 at about 1.6 to 2.5 times the declared 0.05/132. Nothing in stage A or C would
show it, because the size was never computed for the pick's own count pattern.

Whether F-02's cells bunch that much is not known. It can be known **without reading an outcome**: counts are
direction-free. So I cannot say the pass line fails for F-02, only that its level for F-02 is not established. If a
pick's profile sits in the lax region, this becomes CHANGES-A-CONCLUSION for that pick.

**Remedy** (F-02 is a draft, so this is a redraft before the pin, not a re-declaration):
1. **A stage-A kill, outcome-free, declared now.** For each of the 15 cells, take its fills per session on the choice
   block (counts only). On Q-16's `cluster` outcome null, run `cons`'s size at the family's level, with each
   replication's 657 session counts taken from that cell's choice-block counts at a random offset. Seeds fixed in
   section 15; 200,000 replications.
   - A cell whose 95 % interval lies wholly above nominal is killed (K0).
   - Cost: about half a minute and under 200 MB a cell (*synthetic* timing above). Light.
2. **At stage C, the same check on the pick's own judged counts.** Counts only, read inside `stage_C_judgement`
   before any x. If its interval lies wholly above nominal, the pass is not claimed.
   - This is legitimate: the counts carry no direction under the null.
   - A check that can only remove passes cannot raise the size.
   - Declared now, not after the read.
3. **For the program (E-035 (6)).** A family states its fill-intensity persistence beside its side persistence. Q-16's
   null class gains a count-persistent member, P-16's pairs thinned at an outcome-independent persistent rate (M2's
   run).
4. An optional screen: Carter, Schnepel and Steigerwald's effective number of clusters, which needs counts only.

### M2 (MATERIAL) -- Q-55 can only reproduce; it cannot test the choice

**Evidence.**
- Q-55 reruns Q-16's commands with Q-16's seeds (`q55_calibration.py` 123-130). `q16_calibrate.py` fixes every seed in
  code: 64-67, and per null `default_rng([seed, null index])` at 267, 640, 689 and 699.
- Q-55 rebuilds the same pairs, which must hash to `TRADES_SHA256`, and runs the same statistics code: the blobs are
  identical, and the lift path has been unchanged since 568c2a4, the clean lift run.
- **It therefore draws the same replications.** Only a change of code, library or pairs can move a figure.
- That is worth having for provenance. The P part and both two-sample parts were first run from dirty trees (the note's
  section 8), so Q-55 shows that committed code gives those tables.
- **But it is not a validation of the choices made on those draws:**
  - **(a)** `cons` was the declared fallback (f34bc9c defined it before the calibration). It was picked by the brief's
    rule, "the one that holds its level with the most power", from the seven candidates on these replications.
  - **(b)** The treated block count (3a7a3f5) was devised after the first two-sample form failed (Table F8b). Its
    holding (Tables 8b and 10b) was read on the same seeds, `[20261915, 5000 + i]` and `[20261915, 7000 + i]`.
  - **(c)** "Holds" was judged on the point estimates, Table 1's "at or below nominal", and on intervals wholly above
    nominal, Tables 1b, 8b and 10b. The treated `cons`'s worst row in Table 8 has an interval that reaches past
    nominal. F-02's gate says "at or below its level on every real and realistic null" and does not say which.
    (E-035 (4): no Q-16 figure is quoted here.)

**The failure it allows.**
- F-02's status (lines 14-18) and E-044 make the pin wait on Q-55 "reproducing `cons` holding" and withdraw the draft if
  it does not. That gate cannot fail on the selection's account.
- A choice that held on these draws partly by luck would pass the gate unexamined. The note's margins (Tables 1, 8 and
  10) are wide, so the expected outcome of a real test is a hold. The point is that the gate as written does not test
  it.

**Remedy.** One run after Q-55, under the lock, with **new seeds fixed in the decision row** (no file names them yet).
- **What:**
  - `cons` and its three members on Q-16's 70 real and 25 realistic synthetic lift nulls;
  - the treated two-sample `cons` on the 55 selection and 56 C1' nulls;
  - M1's count-persistent nulls on P-16's offered pairs: thinned to 200-5,000 trades at an outcome-independent
    log-AR(0.98) rate, sd 0.7, 1.0 and 1.5, a fresh thinning each replication.
- **Replications:** 200,000 a null, at k = 11-15.
- **The criterion, fixed in the row:** no real or realistic null's 95 % interval lies wholly above nominal, with the
  ratios reported.
- **Cost:** about the calibration's own lift and select runs, without `t21e`, `hac21` or the bootstrap (the note's
  section 8 gives their times). It reads the identity-checked pairs file only, with no bars, under 1 GB. Heavy by the
  20-minute rule.

### m1 (MINOR) -- the level argument is not validated

**Evidence.** `bound`, `two_sample_bound` and `placebo_selection_bound` accept any `level` (`lift_bound.py` 266, 429,
452). The critical value is `t.ppf(1 - level, df)`, so a level above 0.5 makes it negative.

*Synthetic* (`checks.py` [4]): on 800 trades with a lift of exactly -0.0100:

| level | lower bound | result |
|---|---|---|
| 0.05/132 | -0.0733 | no pass |
| 1 - 0.05/132 | **+0.0381** | **passes** |
| 0.9 | +0.0051 | passes |
| 0.5 | -0.0100 | no pass |
| 0, negative, 1.5 or NaN | NaN | no pass |

The two-sample form behaves the same.

**The failure it allows.** A runner that passes the confidence `1 - alpha`, or a typo, turns any sample into a pass.

**Remedy, keeping the blob.** F-02 9.1 states that the runner computes `family_level(k)`, asserts 0 < level < 0.5,
asserts that it equals 0.05/132 at k = 11, and asserts `k in K_RANGE` (the calibrated range). The alternative is a
module guard, which changes the blob and needs a re-pin.

### m2 (MINOR) -- the calendar is load-bearing and only half pinned

**Evidence.**
- `session_sums` refuses only an ordinal outside `0..n-1` (`lift_bound.py` 79-80). `block_index` cuts at n // b, so the
  block edges move with n.
- *Synthetic* (`checks.py` [5]): the same fills on 657 sessions, on 700 (trailing empty sessions), or on only the days
  with a fill. 43 of 600 verdicts at 0.01 changed.
- F-02 9.1 (686-689) defines the calendar as "every trading day the bar store holds from 2024-01-02 to 2026-07-16" and
  writes its count after the run. The v4 read's N2 asked for the day list to be named; its count and bytes are still not
  pinned.
- That list is A1's: `days.parquet` lists every stored day (`vendor/stage2/scripts/atlas_screen.py` 58-63, "every
  stored day"). The calibration ran on it and refused any count but 657 (`q16_calibrate.py` 346-353).

**The failure it allows.** Each of these silently moves the block edges away from those the calibration used:
- a runner that dates a fill by its calendar date rather than its session;
- a runner that builds the ordinals from the fills' own dates;
- a store that changes.

**Remedy, keeping the blob.**
- The pinning row records the day list (first and last date, the count 657, the sha256 of the newline-joined dates).
  These are dates, not outcomes, already read by the calibration.
- The runner asserts `n_sessions` and the list's hash, and maps each fill to its session's ordinal by the session date
  the walker assigns.

### m3 (MINOR) -- the one-door exemption certifies itself and mislabels one read

**Evidence.**
- The scan accepts any line carrying `one-door-exempt: E-\d{3}` (`tests/test_reader.py` 867). It does not check that
  the row exists, names the file, or that the file is not Stage 2's.
- `q16_calibrate.py` 126 reads `vendor/stage2/data/atlas/A1/days.parquet` whole: every column and both blocks. The
  label on that line says "this repository's own derived file (P-16's registered pairs or its day calendar), not Stage
  2's bars or walks", and E-035 (5) says the same.
- But `reader.read_walks` lists A1's `days` among Stage 2's walk tables (`extended/reader.py` 764-765). Its `day_kind`
  column is computed from each day's bars (`vendor/stage2/propedge/research/atlas_walk.py` 139-141).
- In Q-55's clean run the pairs step ledgers the engine's read of that file. Each calibrate step reads it again with no
  ledger line.
- The content is dates and day kinds. Nothing of an outcome is read, and nothing leaks.

**The failure it allows.** The next exemption copied from these lines can carry a real walk or bar read past the scan,
with a row number that names nothing.

**Remedy.**
- Read the calendar through `reader.read_walks("A1", "days", ..., columns=["date"], purpose="registered_design",
  declaration="E-035", design="P-16")`, which `_registered` admits for `scripts/*.py`. Or correct the label and E-035
  (5)'s wording.
- Make the scan require the named row to exist in `DECISIONS.md` and to name the file.

### m4 (MINOR) -- `t_block`'s non-standard branch keeps the zero-se defect

**Evidence.** For a block other than 21, 42 or 63, `t_block` (`lift_bound.py` 459-465) computes `est - crit * se` with
no `se > 0` guard.

*Synthetic* (`edge2.py`): a constant +0.5 on every third session gives se 0.0 and lower 0.5, and "passes" at 0.05/132
on 5-, 10- and 126-session blocks. At 21 sessions it is blank, as it should be.

The note's 7.4 item 4 says this defect was fixed. It was fixed in `bound()` only. `test_degenerate_samples_never_pass`
covers `bound` and `rejects`, not `t_block`.

**The failure it allows.** Any later family that calls `t_block` at its own block length passes a degenerate sample.
F-02 does not call it.

**Remedy.** Route the branch through `bound`'s guard, or drop it, with a test, in the next version of the module (a new
blob, under its own row).

### Notes

1. **n1 -- docstrings.** `lift_bound.py` 10-12 and 88-90, and the note's line 36, say the blocks hold "b or b + 1"
   sessions.
   - At n = 657 the 42- and 63-session members cut blocks of 43-44 and 65-66 sessions (G = 15 and 10; `checks.py`
     [1]). E-035's "21-, 42- and 63-session blocks" are labels.
   - The table at line 20 says "CR1: G / (G - 1)" and "df = G - 1". The code uses G', the non-empty blocks, which is
     what F-02 9.1 says.
   - These are text only: the calibration used the same function.
2. **n2 -- `_diff_bound` takes any method label** (422-432). `two_sample_bound(..., method="t21e")` computes the
   trade-weighted form and labels it `t21e` (df 30); `"hac21"` raises from `int("ac")`. Not on F-02's path, which uses
   the default `SHIPPED`. A check against `DIFF_METHODS` would close it.
3. **n3 -- `Bound.blocks` in the two-sample forms** is sample 1's non-empty blocks (431-432). The `df` is Gt - 1, and
   Gt can be sample 2's. Report Gt beside it.
4. **n4 -- the zero-se guard is exact (`se > 0`).** A constant 0.1 gives se of about 4e-18 for `t21w` and `t42w`, and
   "passes" them. `cons` is saved only by `t63w`'s exact zero (`edge2.py`). This cannot happen with F-02's x in {-1/2,
   0, 1/2}, whose sums are exact. A relative tolerance would be safer.
5. **n5 -- `p_bound`'s fixed-b tables refuse levels below 1.25e-4** (210, 253), so `pcons` cannot be read at k >= 20.
   F-02 reads `pcons` at 0.05 only.
6. **n6 -- `q55_calibration.py`.**
   - Lines 8-11 still say the reader refuses `registered_design` "until ... Q-58". Q-58 is merged (5b2ac27), and
     `_registered` admits `scripts/*.py` under a row naming P-16 (`reader.py` 413-431).
   - Line 178 writes seed 20261915 into every manifest's `seed` field, including `calibration_p` and `bm63c_table`,
     whose seeds are 20261917-19. All the seeds are in `parameters`.
   - The five writes (177-180) are sequential, so a failure on the third leaves two files. The docstring says "nothing
     is written" of failed steps only.
7. **n7 -- `p_bound` reads Stage 2's result CSVs directly** (`user_journey.csv`, `u_budget.csv`; 61-67, 89-128). This is
   outside `extended.results.read_result`'s manifest check and outside the reader, which covers bars and walks; the scan
   looks at parquet calls only.
   - Integrity rests on the vendor manifest test.
   - The rows are Stage 2's registered designs' judged-block outcomes, already read, so nothing new is read.
8. **n8 -- the pass line was chosen on judged-block data of other designs.** It used P-16's judged pairs and
   P-14's and P-16's judged start series, as the brief asked.
   - That is a choice made with judged-block data.
   - It is a size-control choice on designs already read, and uses no F-02 outcome, so it cannot carry F-02's
     direction. Recorded, not a defect.
9. **n9 -- what the blob pin does not cover.** The bound also depends on scipy's t quantile, on numpy, and on the
   runner that builds x and the ordinals. The vendored writer records no library versions. Put numpy's and scipy's
   versions in stage C's `parameters`.
10. **n10 -- P's judged block of starts.** `p_bound.judged` keeps starts from 2024-01-02 with 63 sessions observed:
    595 starts, the last 2026-04-21. That is correct for P-14's file. A design's own start rows must meet the same
    eligibility, which `ahead_average` applies (`observed >= 63`).

---

## What I tried that found nothing

- **The statistic against its texts.** I compared these, by reading and by the tests' hand computations
  (`test_lift_bound.py` 59-75, 277-285): the per-trade mean sum S / sum N; residual block sums u_g = BS_g - est BN_g;
  CR1 with G' / (G' - 1); df = G' - 1; the upper t quantile; lower = est - crit se; `cons` = all three members, its
  bound their minimum.
- **The modules' forms against each other** (*synthetic*, `checks.py` [2]-[3]):
  - `bound("cons")` against `rejects("cons")`: 0 mismatches in 400 near-threshold samples (160 passes), and the lower
    bound equals the members' minimum in every one;
  - `two_sample_bound` against `diff_rejects("cons")`: 0 of 300 (107 passes);
  - `placebo_selection_bound` against `diff_rejects("cons")`: 0 of 300 (133 passes).

  The vectorised forms the calibration used and the scalar forms F-02 calls are the same test.
- **C1' against F-02 9.2 (708-718) and E-035 (2).** D is the difference of the per-fill means over the judged-block
  totals; u_g is count-centred; Gt = min(G1', G2'); df = Gt - 1; `cons` over the three. They match.
- **E-023's twin.** It is the population mean, as E-035 (2) adopted, unseeded where CHARTER section 3 says "seeded".
  The calibration note explains why (one draw is the C1' form). No defect.
- **The critical value at 0.05/132.** `t.ppf(1 - a)` equals `t.isf(a)` to 1e-13 at k = 11, 15 and 40, df 9-30: no
  precision lost.
- **The end of the sample.** `block_index` spreads the remainder, so no final block is short and every session is
  counted.
- **Degenerate inputs.** None passes; each gives a blank lower bound:
  - no trade;
  - one trade;
  - one session holding everything;
  - two 63-blocks only;
  - no spread;
  - an empty placebo;
  - nothing selected.

  NaN x, float ordinals and ordinals outside the calendar are refused with ValueError. An empty Python list is refused
  too: its dtype is float.
- **Determinism.** `cons` draws nothing. `p_bound`'s tables are seeded by `[seed, n, m]` and `[seed, n, flat, taper]`.
  The calibration seeds each null by its index. No seed comes from data.
- **The blobs.**
  - `lift_bound.py` 984f3467a4a05aa790d3ea43e94ac7761f0725b2 and `p_bound.py` f5b29710e243f97a2795e57f6458512fea99199b
    at 57d7ed8, c7e01bd, bb3d913, 3a7a3f5 and 3837256, and in this working copy;
  - the same bytes in Q-55's clean checkout of c7e01bd (`git hash-object`);
  - 2f5ffd0's `lift_bound.py` differs (98a52ff8...), and F-02 pins 3a7a3f5's.
- **The calibration path against the pinned code.**
  - `lift_bound.py` from 568c2a4 to 3a7a3f5 changes only `SHIPPED`, an errstate move in `cbb_tstar`, and adds the
    two-sample code.
  - `q16_calibrate.py` from 3a7a3f5 to c7e01bd changes only comments and the `--days` seam.
  - `q16_p16_pairs.py` adds only the reader's authorisation, before any read.
  - `q16_tables.py` is the same blob at c7e01bd and 57d7ed8.
- **What Q-55 runs and writes.** The same parts as the note's section 8, at the same defaults: 200,000 replications,
  20,000 bootstrap draws, D-621's line at 20,000, power at 5,000, and both block-count rules.
  - It refuses a protected `results/` outside a clean run before any step (96-102), and refuses existing files
    (103-106).
  - Its work folder is outside the tree (111-114), and it writes the five files only through
    `extended.results.write_result` (177-180).
  - `q16_calibrate.py` refuses an `--out` under `results/` (765-767), pairs whose identity did not hold (135-136), and a
    calendar other than 657 sessions (346-353).
- **Stage 2's line.** `p_bound.stage2_block_indices` equals the vendored `user_journey.block_indices` line for line.
- **`p_bound`'s statistics.** OBM is Meketon-Schmeiser's; the flat-top uses linear autocovariances through a zero-padded
  FFT; `pcons` is the AND of three with the minimum lower bound and est > 0. These were checked by reading against
  `test_p_bound.py`.
- **Look-ahead.** The statistic fits nothing on the sample. Its block edges depend only on the calendar's count, and
  nothing reads 2026-07-17 or later.

## What I could not check

- **F-02's fill-intensity profile.** It needs a choice-block count read, so whether M1 bites for F-02 is open. That is
  the remedy's first step.
- **Q-55's figures.** The run is going and its results were not read.
- **The bar store's judged day count.** That it is 657 rests on the calibration's own assertion and A1's definition; I
  read no data.
- **numpy's Generator streams.** Whether they are identical between the numpy that made the note's tables and Q-55's
  environment. Both runs are on this machine.
- **Larger M1 grids.** M1's size figures are one synthetic outcome model (the probit cluster). Real P-16 pairs under a
  persistent thinning are M2's proposed run, not done here.

## Proposed decision row (for the lead to number)

| E-NNN | 2026-11-16 | **Q-68: the red team's read of the pass-line code (`docs/reviews/PASS_LINE_CODE_2026-11-16.md`) -- stands with readings.** `extended/lift_bound.py` (blob `984f3467a4a05aa790d3ea43e94ac7761f0725b2`) and `extended/p_bound.py` (`f5b29710e243f97a2795e57f6458512fea99199b`) compute what E-008, E-022, E-023, E-035 and F-02 v5's C1, C1' and 9.1 say, and are the same bytes at 57d7ed8 and in Q-55's checkout of c7e01bd; no defect changes a declared rule. **Before F-02's pin:** (1) **fill intensity** (M1, MATERIAL) -- no Q-16 null lets the fills' rate persist across sessions, and on synthetic nulls where it does `cons` reaches or exceeds its level (the note's table); F-02 adds an outcome-free stage-A kill -- `cons`'s size at the family's level on Q-16's `cluster` null with each cell's own choice-block counts, 200,000 replications, seeds in its section 15, a cell whose interval lies wholly above nominal killed (K0) -- and the same check on the pick's judged counts before any x in stage C, a pass not claimed above nominal; every family states its fill-intensity persistence beside its side persistence (E-035 (6) extended); (2) **a fresh-seed validation** (M2, MATERIAL) -- Q-55 replays Q-16's replications and so checks provenance, not the choice of `cons` and the treated block count made on them; after Q-55, one run under the lock on seeds fixed in this row: `cons` and the treated two-sample `cons` on Q-16's real and realistic nulls plus P-16's pairs thinned at a persistent outcome-independent rate, criterion fixed here (at k = 11-15 no real or realistic null's 95 % interval wholly above nominal); (3) **the MINOR items in the stage-C runner, the module unchanged:** the level from `family_level(k)` asserted in (0, 0.5) and k in `K_RANGE`; `n_sessions` and the day list (A1's stored days 2024-01-02..2026-07-16, count and sha256 in the pinning row) asserted; E-035 (5)'s label for A1's `days.parquet` corrected and the exemption scan made to check the row it names; `t_block`'s zero-se branch fixed in the next module version under its own row. | Brief Q-68; the review and its hand-back; E-008, E-022, E-023, E-035, E-042, E-044; F-02 v5. |

---

## Appendix A: the scripts (scratchpad, not durable)

Run with `OMP_NUM_THREADS=1`, from the scratchpad, importing this worktree's `extended` package.
- `checks.py` and `edge2.py` take seconds.
- `intensity.py 200000` and `intensity2.py 200000` take about 25 s a row. The "(0 s)" in `intensity2.py`'s lines is a
  print-order slip (the timer is read before the run) and touches no figure.

### `checks.py`

```python
"""Q-68 red-team checks on extended/lift_bound.py and extended/p_bound.py: synthetic only, small, seeds fixed here
before any run (seed 68680001 .. 68680020; outside the program's 2026xxxx space)."""
import math
import sys

import numpy as np
from scipy import stats

sys.path.insert(0, r"C:\Users\resni\AppData\Local\stage2-extended-wt\wt-verify")
from extended import lift_bound as LB  # noqa: E402

def say(*a):
    print(" ".join(str(x) for x in a), flush=True)

# 1. block sizes on the judged calendar
for b in (21, 42, 63):
    bid, G = LB.block_index(657, b)
    sz = np.bincount(bid)
    say(f"[1] n=657 b={b}: G={G}, block sizes {sorted(set(sz.tolist()))}")

# 2. bound('cons') == rejects('cons') and lower == min of members on random near-threshold samples
rng = np.random.default_rng(68680001)
mism, mism_low, n_pass = 0, 0, 0
for r in range(400):
    n = 657
    m = int(rng.integers(30, 3000))
    s = np.sort(rng.integers(0, n, m))
    x = rng.choice([-0.5, 0.0, 0.5], size=m, p=[0.47, 0.06, 0.47]) + rng.normal(0, 0.02) * 0
    shift = rng.uniform(0, 0.25)
    x = np.where(rng.random(m) < shift, 0.5, x)
    lev = LB.family_level(int(rng.integers(11, 16)))
    b = LB.bound("cons", x, s, n, level=lev)
    S, N = LB.session_sums(x, s, n)
    rj = bool(LB.rejects("cons", S, N, level=lev))
    mem = [LB.bound(mm, x, s, n, level=lev).lower for mm in ("t21w", "t42w", "t63w")]
    if b.rejects != rj:
        mism += 1
    if not (np.isnan(b.lower) and any(np.isnan(mem))) and not math.isclose(b.lower, min(mem), rel_tol=1e-12, abs_tol=1e-15):
        mism_low += 1
    n_pass += int(b.rejects)
say(f"[2] bound('cons') vs rejects('cons'): {mism} mismatches, lower != min(members) {mism_low}, passes {n_pass}/400")

# 3. two_sample_bound / placebo_selection_bound vs diff_rejects
rng = np.random.default_rng(68680002)
mism2, mism3, p2, p3 = 0, 0, 0, 0
for r in range(300):
    n = 657
    m1, m2 = int(rng.integers(50, 1500)), int(rng.integers(100, 5000))
    s1, s2 = np.sort(rng.integers(0, n, m1)), np.sort(rng.integers(0, n, m2))
    x1 = rng.choice([-0.5, 0.0, 0.5], size=m1) + 0.0
    x1 = np.where(rng.random(m1) < rng.uniform(0, 0.3), 0.5, x1)
    x2 = rng.choice([-0.5, 0.0, 0.5], size=m2) + 0.0
    lev = LB.family_level(11)
    b = LB.two_sample_bound(x1, s1, x2, s2, n, level=lev)
    S1, N1 = LB.session_sums(x1, s1, n); S2, N2 = LB.session_sums(x2, s2, n)
    if b.rejects != bool(LB.diff_rejects("cons", S1, N1, S2, N2, level=lev)):
        mism2 += 1
    p2 += int(b.rejects)
    y = rng.random(m2).round() + 0.0
    sel = rng.random(m2) < rng.uniform(0.02, 0.5)
    y = y + 0.3 * sel * (rng.random() < 0.5)
    b3 = LB.placebo_selection_bound(y, s2, sel, n, level=lev)
    A, B = LB.session_sums(y[sel], s2[sel], n); C, M = LB.session_sums(y, s2, n)
    if b3.rejects != bool(LB.diff_rejects("cons", A, B, C, M, level=lev)):
        mism3 += 1
    p3 += int(b3.rejects)
say(f"[3] two_sample_bound vs diff_rejects: {mism2} mismatches ({p2} pass); placebo_selection_bound: {mism3} ({p3} pass)")

# 4. the level argument is not checked: 1 - level (a confidence) or 0.5 passes a zero/negative lift
rng = np.random.default_rng(68680003)
n = 657
s = np.sort(rng.integers(0, n, 800))
x = rng.choice([-0.5, 0.5], size=800)
x = x - (x.mean() + 0.01)                     # a NEGATIVE lift of 0.01 exactly
lev = LB.family_level(11)
for L in (lev, 1 - lev, 0.5, 0.9, 0.0, -0.1, 1.5, float("nan")):
    try:
        b = LB.bound("cons", x, s, n, level=L)
        b2 = LB.two_sample_bound(x, s, x[:400] + 0.0, s[:400], n, level=L)
        say(f"[4] level={L!r}: est {b.estimate:+.4f} lower {b.lower:+.4f} rejects {b.rejects}; two-sample rejects {b2.rejects}")
    except Exception as e:                    # noqa: BLE001
        say(f"[4] level={L!r}: raised {type(e).__name__}: {e}")

# 5. the calendar the caller passes moves the verdict: the same trades on 657 sessions vs trailing empty sessions added,
#    vs only the sessions with a fill (a compressed calendar)
rng = np.random.default_rng(68680004)
flips = 0
tot = 0
for r in range(300):
    m = 300
    s = np.sort(rng.integers(0, 657, m))
    a = rng.normal(0, 0.15, 657)               # a session effect
    p = 0.5 + 0.5 * np.tanh(a[s]) * 0.8 + 0.045
    x = np.where(rng.random(m) < p, 0.5, -0.5)
    lev = 0.01
    full = LB.bound("cons", x, s, 657, level=lev).rejects
    longer = LB.bound("cons", x, s, 700, level=lev).rejects
    u, inv = np.unique(s, return_inverse=True)
    comp = LB.bound("cons", x, inv.astype(np.int64), len(u), level=lev).rejects
    tot += 1
    flips += int(full != longer) + int(full != comp)
say(f"[5] verdict changes when the calendar is padded (657->700) or compressed to fill days: {flips} of {2 * tot} comparisons")

# 6. the critical value at the family levels: ppf(1 - a) vs isf(a)
for k in (11, 15, 40):
    a = LB.family_level(k)
    for df in (9, 14, 30):
        c1, c2 = stats.t.ppf(1 - a, df), stats.t.isf(a, df)
        say(f"[6] k={k} df={df}: ppf(1-a)={c1:.10f} isf(a)={c2:.10f} diff {abs(c1 - c2):.2e}")

# 7. degenerate inputs
cases = {
    "empty": (np.array([]), np.array([], dtype=int)),
    "one trade": (np.array([0.5]), np.array([5])),
    "one session, many": (np.full(50, 0.5), np.full(50, 7)),
    "all +0.5 spread": (np.full(400, 0.5), np.arange(0, 657, 657 / 400).astype(int)),
    "2 blocks of 63": (np.r_[np.full(30, 0.5), np.full(30, 0.4)], np.r_[np.full(30, 3), np.full(30, 600)]),
}
for nm, (x, s) in cases.items():
    b = LB.bound("cons", x, s, 657, level=LB.family_level(11))
    say(f"[7] {nm}: lower {b.lower} rejects {b.rejects}")
try:
    LB.bound("cons", [], [], 657, level=0.01)
    say("[7] python empty lists: accepted")
except Exception as e:                       # noqa: BLE001
    say(f"[7] python empty lists: raised {type(e).__name__}: {e}")
try:
    LB.bound("cons", np.array([0.5, np.nan]), np.array([1, 2]), 657, level=0.01)
except Exception as e:                       # noqa: BLE001
    say(f"[7] NaN x: raised {type(e).__name__}")
try:
    LB.bound("cons", np.array([0.5, 0.5]), np.array([1.0, 2.0]), 657, level=0.01)
except Exception as e:                       # noqa: BLE001
    say(f"[7] float ordinals: raised {type(e).__name__}")
b = LB.two_sample_bound(np.full(300, 0.5), np.arange(300), np.array([]), np.array([], dtype=int), 657, level=0.01)
say(f"[7] two-sample, empty placebo: est {b.estimate} lower {b.lower} rejects {b.rejects}")
b = LB.placebo_selection_bound(np.ones(300), np.arange(300), np.zeros(300, bool), 657, level=0.01)
say(f"[7] selection, nothing selected: est {b.estimate} lower {b.lower} rejects {b.rejects}")

# 8. Bound fields of cons: df/blocks/trades are the binding member's
b = LB.bound("cons", np.r_[np.full(200, 0.5), np.full(180, -0.5)], np.sort(np.random.default_rng(68680005).integers(0, 657, 380)), 657, level=0.01)
say(f"[8] cons Bound: method {b.method} df {b.df} blocks {b.blocks} trades {b.trades} crit {b.critical:.3f}")
```

### `checks.py`'s output

```
[1] n=657 b=21: G=31, block sizes [21, 22]
[1] n=657 b=42: G=15, block sizes [43, 44]
[1] n=657 b=63: G=10, block sizes [65, 66]
[2] bound('cons') vs rejects('cons'): 0 mismatches, lower != min(members) 0, passes 160/400
[3] two_sample_bound vs diff_rejects: 0 mismatches (107 pass); placebo_selection_bound: 0 (133 pass)
[4] level=0.0003787878787878788: est -0.0100 lower -0.0733 rejects False; two-sample rejects False
[4] level=0.9996212121212121: est -0.0100 lower +0.0381 rejects True; two-sample rejects True
[4] level=0.5: est -0.0100 lower -0.0100 rejects False; two-sample rejects False
[4] level=0.9: est -0.0100 lower +0.0051 rejects True; two-sample rejects True
[4] level=0.0: est -0.0100 lower +nan rejects False; two-sample rejects False
[4] level=-0.1: est -0.0100 lower +nan rejects False; two-sample rejects False
[4] level=1.5: est -0.0100 lower +nan rejects False; two-sample rejects False
[4] level=nan: est -0.0100 lower +nan rejects False; two-sample rejects False
[5] verdict changes when the calendar is padded (657->700) or compressed to fill days: 43 of 600 comparisons
[6] k=11 df=9: ppf(1-a)=4.9817967820 isf(a)=4.9817967820 diff 2.22e-14
[6] k=15 df=9: ppf(1-a)=5.4294568202 isf(a)=5.4294568202 diff 1.20e-13
[6] k=40 df=30: ppf(1-a)=4.6586689157 isf(a)=4.6586689157 diff 3.25e-13
[7] empty: lower nan rejects False
[7] one trade: lower nan rejects False
[7] one session, many: lower nan rejects False
[7] all +0.5 spread: lower nan rejects False
[7] 2 blocks of 63: lower -41.56688514297273 rejects False
[7] python empty lists: raised ValueError: session must be integer ordinals
[7] NaN x: raised ValueError
[7] float ordinals: raised ValueError
[7] two-sample, empty placebo: est nan lower nan rejects False
[7] selection, nothing selected: est nan lower nan rejects False
[8] cons Bound: method cons df 9.0 blocks 10 trades 380 crit 2.821
```

(Lines [6] for df 14 and 30 at k = 11 and 15 and df 9 and 14 at k = 40 are omitted; each difference is below 1e-12.)

### `edge2.py`

```python
import sys
import numpy as np
sys.path.insert(0, r"C:\Users\resni\AppData\Local\stage2-extended-wt\wt-verify")
from extended import lift_bound as LB
s = np.arange(0, 657, 3)                      # one trade every third session
x = np.full(len(s), 0.5)                      # no spread at all
for blk in (21, 5, 10, 126):
    b = LB.t_block(x, s, 657, level=LB.family_level(11), block=blk)
    print(f"t_block block={blk}: se {b.se!r} lower {b.lower!r} rejects {b.rejects}")
x2 = np.full(len(s), 0.1)                     # constant, not a binary fraction
for m in ("t21w", "t42w", "t63w", "cons"):
    b = LB.bound(m, x2, s, 657, level=LB.family_level(11))
    print(f"bound {m} constant 0.1: se {b.se!r} lower {b.lower!r} rejects {b.rejects}")
b = LB.two_sample_bound(np.full(200, 0.3), s[:200], np.full(219, 0.1), s, 657, level=LB.family_level(11))
print(f"two-sample constants 0.3 vs 0.1: est {b.estimate!r} se {b.se!r} rejects {b.rejects}")
try:
    b = LB.two_sample_bound(x, s, x, s, 657, level=0.01, method="t21e")
    print(f"two_sample_bound method='t21e' accepted, labelled {b.method}, df {b.df}")
except Exception as e:
    print("t21e refused", type(e).__name__, e)
```

Output:

```
t_block block=21: se 0.0 lower nan rejects False
t_block block=5: se 0.0 lower 0.5 rejects True
t_block block=10: se 0.0 lower 0.5 rejects True
t_block block=126: se 0.0 lower 0.5 rejects True
bound t21w constant 0.1: se 4.024864388067647e-18 lower 0.09999999999999996 rejects True
bound t42w constant 0.1: se 3.148465777326242e-18 lower 0.1 rejects True
bound t63w constant 0.1: se 0.0 lower nan rejects False
bound cons constant 0.1: se 0.0 lower nan rejects False
two-sample constants 0.3 vs 0.1: est 0.19999999999999998 se 0.0 rejects False
two_sample_bound method='t21e' accepted, labelled t21e, df 30.0
```

### `intensity.py`

```python
"""Q-68: is `cons` still at its level when the fills' INTENSITY is persistent across sessions (fills bunch in a volatile
quarter), a dependence Q-16's nulls do not hold (their counts are iid per session, or a uniform thinning of a stream
with near-constant density)? Synthetic only. Seeds fixed before the run: 68680010 + scenario index.

Outcome model (Q-16's `cluster`): each fill 0.5 sign(a_s + e), a_s the session effect (icc 0.35), symmetric, so the
null is exact (mean zero) and every fill of a session shares its sign tendency (a side reset daily, persist1).
Count models (mean m fills a session, so about 657 m fills):
  iid      negative binomial (size 1), iid across sessions -- Q-16's form (the reference)
  burst    one quarter (63 sessions, random phase) at 10x the rest's intensity, negative binomial within
  ar98s1   log-intensity AR(1) 0.98 across sessions, stationary sd 1.0; Poisson given it
  ar98s15  the same, sd 1.5
  ar995s1  AR(1) 0.995, sd 1.0
"""
import math
import sys
import time

import numpy as np
from scipy import stats

sys.path.insert(0, r"C:\Users\resni\AppData\Local\stage2-extended-wt\wt-verify")
from extended import lift_bound as LB  # noqa: E402

N_SESS = 657
LEVELS = (LB.family_level(11), 0.001, 0.01)
ICC = 0.35


def counts(model, m, rng, reps):
    n = N_SESS
    if model == "iid":
        return rng.negative_binomial(1.0, 1.0 / (1.0 + m), size=(n, reps)).astype(float)
    if model == "burst":
        L = 63
        phase = rng.integers(0, n - L + 1, size=reps)
        j = np.arange(n)[:, None]
        inb = (j >= phase[None, :]) & (j < phase[None, :] + L)
        base = m * n / (n - L + 10 * L)
        lam = np.where(inb, 10 * base, base)
        return rng.negative_binomial(1.0, 1.0 / (1.0 + lam)).astype(float)
    phi, sd = {"ar98s1": (0.98, 1.0), "ar98s15": (0.98, 1.5), "ar995s1": (0.995, 1.0)}[model]
    h = np.empty((n, reps))
    h[0] = rng.standard_normal(reps) * sd
    inn = sd * math.sqrt(1 - phi * phi)
    for t in range(1, n):
        h[t] = phi * h[t - 1] + inn * rng.standard_normal(reps)
    lam = m * np.exp(h - sd * sd / 2)
    return rng.poisson(lam).astype(float)


def batch(model, m, rng, reps):
    N = counts(model, m, rng, reps)
    a = rng.standard_normal(N.shape) * math.sqrt(ICC)
    p = stats.norm.cdf(a / math.sqrt(1 - ICC))
    up = rng.binomial(N.astype(np.int64), p)
    return 0.5 * (2 * up - N), N


def run(model, m, reps, seed, bsz=4000):
    rng = np.random.default_rng(seed)
    rej = {(meth, a): 0 for meth in ("t21w", "t42w", "t63w", "cons") for a in LEVELS}
    share_top = []
    done = 0
    while done < reps:
        r = min(bsz, reps - done)
        S, N = batch(model, m, rng, r)
        for meth in ("t21w", "t42w", "t63w", "cons"):
            rj, _ = LB.many_levels(meth, S, N, LEVELS)
            for i, a in enumerate(LEVELS):
                rej[(meth, a)] += int(rj[i].sum())
        BN = np.add.reduceat(N, np.flatnonzero(np.r_[True, np.diff(LB.block_index(N_SESS, 63)[0]) != 0]), axis=0)
        share_top.append(BN.max(axis=0) / np.maximum(BN.sum(axis=0), 1))
        done += r
    st = np.concatenate(share_top)
    return rej, float(np.median(st)), float(np.quantile(st, 0.9))


if __name__ == "__main__":
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 100_000
    scen = [("iid", 0.3), ("burst", 0.3), ("ar98s1", 0.3), ("ar98s15", 0.3), ("ar995s1", 0.3),
            ("iid", 2.0), ("burst", 2.0), ("ar98s15", 2.0)]
    for i, (model, m) in enumerate(scen):
        t0 = time.time()
        rej, med, p90 = run(model, m, reps, 68680010 + i)
        cells = []
        for a in LEVELS:
            for meth in ("t21w", "t63w", "cons"):
                k = rej[(meth, a)]
                lo, hi = LB.clopper_pearson(k, reps)
                cells.append(f"{meth}@{a:.2e}: {k} ({k / reps / a:.2f}x [{lo / a:.2f}, {hi / a:.2f}])")
        print(f"{model:8s} m={m}: top-quarter share of fills median {med:.2f} p90 {p90:.2f}; {time.time() - t0:.0f} s",
              flush=True)
        for c in cells:
            print("    " + c, flush=True)
```

### `intensity2.py`

```python
"""Q-68, second batch (seeds 68680030 + i, fixed before the run): milder intensity profiles (a trend across the block,
log-intensity sd 0.7), and C1''s two-sample form when the level fills and the placebo fills share a persistent
intensity and the day's session effect (the C1' null: equal means, a common day effect)."""
import math
import sys
import time

import numpy as np
from scipy import stats

sys.path.insert(0, r"<scratchpad>\q68")      # <scratchpad>: the session scratchpad (its long path shortened here)
sys.path.insert(0, r"C:\Users\resni\AppData\Local\stage2-extended-wt\wt-verify")
from extended import lift_bound as LB  # noqa: E402
import intensity as I  # noqa: E402

N_SESS, ICC = 657, 0.35
LEVELS = (LB.family_level(11), 0.001, 0.01)


def lam_profile(model, m, rng, reps):
    n = N_SESS
    if model.startswith("trend"):
        r = float(model[5:-1])                       # last / first intensity
        w = 1 + (r - 1) * np.arange(n) / (n - 1)
        return np.repeat((m * w / w.mean())[:, None], reps, axis=1)
    phi, sd = {"ar98s07": (0.98, 0.7), "ar98s1": (0.98, 1.0), "ar98s15": (0.98, 1.5)}[model]
    h = np.empty((n, reps))
    h[0] = rng.standard_normal(reps) * sd
    inn = sd * math.sqrt(1 - phi * phi)
    for t in range(1, n):
        h[t] = phi * h[t - 1] + inn * rng.standard_normal(reps)
    return m * np.exp(h - sd * sd / 2)


def one_sample(model, m, reps, seed, bsz=4000):
    rng = np.random.default_rng(seed)
    rej = {a: 0 for a in LEVELS}
    done = 0
    while done < reps:
        r = min(bsz, reps - done)
        N = rng.poisson(lam_profile(model, m, rng, r)).astype(float)
        a = rng.standard_normal(N.shape) * math.sqrt(ICC)
        up = rng.binomial(N.astype(np.int64), stats.norm.cdf(a / math.sqrt(1 - ICC)))
        S = 0.5 * (2 * up - N)
        rj, _ = LB.many_levels("cons", S, N, LEVELS)
        for i, al in enumerate(LEVELS):
            rej[al] += int(rj[i].sum())
        done += r
    return rej


def two_sample(model, m1, m2, reps, seed, bsz=4000):
    """Level fills (rate m1) and placebo fills (m2) on the same days, the same intensity profile, the same session
    effect a_s (shared market day); each fill 0.5 sign(a_s + e). Both samples have mean zero: the C1' null."""
    rng = np.random.default_rng(seed)
    rej = {a: 0 for a in LEVELS}
    done = 0
    while done < reps:
        r = min(bsz, reps - done)
        lam = lam_profile(model, 1.0, rng, r)
        N1 = rng.poisson(lam * m1).astype(float)
        N2 = rng.poisson(lam * m2).astype(float)
        a = rng.standard_normal(N1.shape) * math.sqrt(ICC)
        p = stats.norm.cdf(a / math.sqrt(1 - ICC))
        u1 = rng.binomial(N1.astype(np.int64), p)
        u2 = rng.binomial(N2.astype(np.int64), p)
        S1, S2 = 0.5 * (2 * u1 - N1), 0.5 * (2 * u2 - N2)
        rj, _ = LB.diff_many_levels("cons", S1, N1, S2, N2, LEVELS)
        for i, al in enumerate(LEVELS):
            rej[al] += int(rj[i].sum())
        done += r
    return rej


def show(tag, rej, reps):
    cells = []
    for al in LEVELS:
        k = rej[al]
        lo, hi = LB.clopper_pearson(k, reps)
        cells.append(f"@{al:.2e}: {k} ({k / reps / al:.2f}x [{lo / al:.2f}, {hi / al:.2f}])")
    print(f"{tag}: " + "; ".join(cells), flush=True)


if __name__ == "__main__":
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 200_000
    i = 0
    for model in ("trend2x", "trend3x", "ar98s07"):
        for m in (0.3, 2.0):
            t0 = time.time()
            show(f"cons one-sample {model} m={m} ({time.time() - t0:.0f} s)", one_sample(model, m, reps, 68680030 + i), reps)
            i += 1
    for model in ("ar98s07", "ar98s1", "ar98s15"):
        for m1 in (0.3, 1.0):
            show(f"cons C1' {model} level {m1}/session placebo {5 * m1}/session", two_sample(model, m1, 5 * m1, reps,
                                                                                              68680030 + i), reps)
            i += 1
```

The rejection counts behind M1's tables, at 200,000 replications a row, as printed (`intensity.py`; for each
model, t21w / t63w / cons at 0.05/132, then 0.001, then 0.01):

```
iid      m=0.3: 97 / 97 / 18;      267 / 232 / 59;     2262 / 2158 / 988
burst    m=0.3: 373 / 420 / 65;    777 / 880 / 212;    4156 / 5051 / 2031
ar98s1   m=0.3: 208 / 207 / 32;    440 / 477 / 88;     2877 / 3331 / 1406
ar98s15  m=0.3: 448 / 644 / 121;   814 / 1160 / 271;   3952 / 5280 / 2061
ar995s1  m=0.3: 162 / 199 / 40;    380 / 459 / 110;    2604 / 3052 / 1251
iid      m=2.0: 90 / 81 / 15;      216 / 219 / 48;     2050 / 2061 / 890
burst    m=2.0: 613 / 579 / 88;    1154 / 1212 / 218;  5395 / 6602 / 2241
ar98s15  m=2.0: 697 / 1101 / 190;  1224 / 1860 / 409;  4869 / 6668 / 2464
```

`intensity2.py` (cons only; at 0.05/132, 0.001, 0.01):

```
one-sample trend2x m=0.3: 17, 50, 930        trend2x m=2.0: 8, 43, 878
one-sample trend3x m=0.3: 17, 62, 968        trend3x m=2.0: 16, 50, 918
one-sample ar98s07 m=0.3: 17, 69, 1114       ar98s07 m=2.0: 19, 63, 1133
C1' ar98s07 0.3/1.5: 18, 60, 1047            C1' ar98s07 1.0/5.0: 19, 61, 1015
C1' ar98s1  0.3/1.5: 38, 93, 1215            C1' ar98s1  1.0/5.0: 31, 85, 1228
C1' ar98s15 0.3/1.5: 61, 167, 1669           C1' ar98s15 1.0/5.0: 68, 179, 1698
```
