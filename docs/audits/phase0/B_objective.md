# Phase 0 audit, track B: is the objective right?

**Status: EXPLORATORY audit reading, 2026-11-15. Read-only.** Nothing of Stage 2's engine was run and no bar was read.
No campaign ran. Every figure below either comes straight from a vendored result file (file, section and filter
named), or was computed from one by a scratch script (named in section 7) with the filter stated beside it. **None of
these figures is a result of this repository.** A decision row quotes one only after it has been recomputed into a
result file with a manifest (the convention of Stage 2 D-628). All of them are in-sample, on development data, and
on the `verdict` arm unless a row says otherwise.

Objects audited: `CHARTER.md` sections 2 and 3 (P, the guarded measures, S3c as the screening target, R\* = P-14,
Stage 2 D-621 (3) and (4)(e) used unchanged); `vendor/stage2/results/user_journey.csv` (section `start`);
`user_drivers.csv` (`between_designs`, `design_table`, `design_vs_luck`); the nine family files `u_*.csv` (sections
`cell`, `judged`, `choice`; **none of them holds per-start rows**: only U1's nine configurations have start rows);
`propedge/research/u_select.py` and `user_journey.py` (the code of the rule).

Definitions used below. One start's **ahead average** is `A = (1[net_month_1 > 0] + 1[net_month_2 > 0] +
1[net_month_3 > 0]) / 3`, over starts with `observed >= 63`. P is the mean of A, as in Stage 2 D-627 (1). It
reproduces the file: P-14 0.671168 on all 1,629 starts. The **judged block** is the starts from 2024-01-02 with at
least 63 sessions left: 595 starts, 2024-01-02 to 2026-04-21. That matches every family file's `judged` rows.

---

## 1. Summary: findings by severity

### CHANGES-A-CONCLUSION

1. **S3c is not a sound screening target where screening matters. Its 0.76 rank correlation with P comes from failed
   designs and from arithmetic.** (Q2)
   - Among the 22 designs with P >= 0.60 (the region where anything could beat R\*), Spearman(P, S3c) is **-0.20**.
     The whole-family bootstrap interval is -0.60 to +0.02.
   - Inside the purchase-budget family it is -0.67. The three rows to beat are in reverse order: P-16 has the highest
     S3c and the lowest P.
   - P-14, the row to beat, ranks 18th of those 22 by S3c. The design with the highest S3c of all 61 (`seats1`) is
     37th by P.
   - Leaving out the Consistency and flat-plan families (16 cells whose P is 0.00 to 0.59) brings the 0.76 down to
     0.50.
   - Near the top, P goes with **speed** instead: S3a +0.48.
   - S3c is an exact function of the same month-3 cash as P: S3c - 1 = mean month-3 net / mean month-3 fees. It works
     as a **kill line** (no design on file with S3c at or below P-14's beats P-14 on P). It does not work as a
     **ranking**: only 4 of the 27 designs above P-14's S3c beat it on P.
   - What this changes: the charter's "Why S3c screens" and E-001 (2).
2. **Line (3)(i) of the selection rule does not hold its stated level.** (Q3)
   - The test: a Gaussian null with this data's own dependence, which is the bootstrap's best case.
   - The 63-block percentile line, at one-sided 0.05/110 from 2,000 draws, rejects a true zero difference **1.4 to
     1.6 % of the time against a nominal 0.045 %, about 30 to 36 times too often.**
   - The causes:
     - About 9 independent blocks fit in the judged block, so the bootstrap's spread is itself badly estimated.
     - The 0.045 % percentile of 2,000 draws sits between the smallest and the second-smallest draw.
     - The block bootstrap is not centred: on P-14 minus P-16 its centre is 0.029 above the sample difference.
   - What this changes: the charter's statement that the program "spends at most 5 %" is not delivered by this
     implementation. A Student-t on non-overlapping 63-start batch means is close to nominal (0.08 %).
3. **The judged block cannot detect any improvement of the size seen so far, so exit (A) is out of reach and a (B)
   close would say little.** (Q3)
   - There are about 60 to 75 independent starts in the judged block, not 595.
   - For a design whose trades differ from P-14's as much as P-16's do (F-01's stage D is P-16's schedule plus
     tickets), the nominal rule needs a true gain of about **0.21 to 0.23** in P for 80 % power. A calibrated test
     needs about 0.30.
   - For a variant on R\*'s own trades it needs about 0.05 to 0.08.
   - The largest gain over P-14 among 66 cells on file is +0.021 on all starts, and it is -0.002 on the judged block.
   - P-14's own +0.103 lead over P-16 on the judged block would not carry: its lower limit at seed 20261700 is -0.011.
   - So F-01's stage D can carry only a candidate whose judged P reaches about 0.89 to 0.95.

### MATERIAL

4. **Which design is best depends on the objective, and the data cannot settle it.** (Q4)
   - Among the three rows to beat, P, P under a $2,000 or $2,500 bankroll, and CVaR10 all rank P-14 first.
   - Mean month-3 net, a loss-averse mean, a log-utility certainty equivalent and S3c all rank **P-16** first.
   - Every P-14 vs P-16 difference in mean dollars is inside noise (+$790, SE about $590, on all starts).
   - R\* = P-14 is the output of one value judgement: count starts above zero over months 1 to 3, ignore how far
     above or below.
5. **The guards (line (ii)) compare point estimates against tolerances smaller than their own noise.** (Q1, Q5)
   - On the judged block S5a's tolerance is **$10.57**: ten per cent of P-14's p10 of $105.70, a quantity that
     crosses zero. Its paired standard error is $325 to $673.
   - S3b's tolerance is 2.4 sessions against an SE of 3.8 to 5.4 sessions. S1's is $246 against $188 to $374.
   - A design exactly as good as R\* on every guarded measure would pass line (ii) only about one time in five to one
     in three.
6. **P's blind spots go unguarded.** (Q1)
   - P ignores how far a start is above or below zero, the cash a user actually has, the tail below p10, and every
     dollar after month 3.
   - S4a and S4b are 0.97 to 1.00 for every design, so the months 6 to 12 dollars are unguarded. Mean month-12 net
     differs by 39 % between P-15 and P-16.
   - S3c's 10 % tolerance allows about **22 % less month-3 profit** for P-14 at equal fees.
   - P sits on the horizon where the design explains least of a user's outcome: 3 to 7.5 % of the variance at months
     1 to 3, against 19.5 % at month 12.
   - On all starts, P-14's lead over P-16 is entirely month 1 (+0.131, +0.022, 0.000 at months 1, 2, 3).
7. **The bootstrap's weights favour advantages in the middle of the judged block.** (Q3, Q5) The first and last start
   are drawn at 0.02 times the uniform weight, the middle at 1.12 times. A candidate whose edge falls in mid-2024 to
   early 2025 gains up to about half a standard error for free. Stage 2 D-627 (3) records the limit but not its size.
8. **Ways a new family could game the measures** (Q5):
   - **Month-boundary fee timing.** One evaluation costs $49 in these rows. 5.1 % of P-14's starts and 12.2 % of
     P-16's are within $250 below zero at session 21. Deferring purchases past sessions 21, 42 and 63 could add up to
     about +0.03 (P-14) or +0.05 (P-16) to P with no gain to the user, which is more than any real gain on file.
   - **S3c's denominator.** Buying fewer evaluations raises S3c while lowering P.
   - **A judged block already read by nine families.**

### MINOR

9. The 63-session block is long enough for the **standard error**: the autocorrelation reaches zero by lag 28 to 56,
   and the SE grows only 8 to 16 % at blocks of 126 to 189. The problem is the **number** of blocks (9.4), not their
   length. (Q3)
10. `user_drivers.csv` marks S5a and S4a as partly mechanical against P, but not S3c, which is equally a function of
    the month-3 net. (Q2)
11. The year rule (4)(e) passes a true +0.02 improvement only about 27 to 52 % of the time, and +0.05 about 71 to
    95 %: it is a further power drain. (Q3)
12. The operator's "dollars per payout" is measured as S3c, payouts per *fee* dollar. The literal reading, the size of
    a payout, is S3d, which is reported only. (Q1)

### NOTE

13. Reports of "595 starts" overstate the evidence about 9 times. (Q3)
14. R\* was fixed on all starts, judged block included (Stage 2 D-626). Its judged-block P (0.719) carries some winner's
    curse, which makes R\* harder to beat, not easier. (Q5)
15. The verdict prices conduct tier 3 at 0 % denial. A design that leans more on payouts a firm might deny gets full
    credit in P; this cannot be measured from these files. (Q5)
16. The rank-stability frequencies in Q4 come from the same few-block bootstrap as finding 2, and overstate certainty.

---

## 2. Q1: is P the right primary for the journey?

**What P is.** For each start day it counts how many of months 1, 2 and 3 end with net cash above zero, over three,
averaged over start days. Everyone who starts on one day gets the same trades, so P is a frequency over start dates,
not over people.

**What it rewards, measured** (`user_journey.csv` `start`, verdict, `observed >= 63`, 1,629 starts; script
`q4_rankstab.py`, `q1_q5.py`):

| share ahead | month 1 | month 2 | month 3 |
|---|---|---|---|
| P-14 | 0.451 | 0.715 | 0.848 |
| P-16 | 0.319 | 0.693 | 0.848 |
| difference | +0.131 | +0.022 | 0.000 |
| difference, judged block only | +0.121 | +0.108 | +0.081 |

Across the whole window, P-14's lead on P is all month 1. Month 1 asks one question: did a first payout arrive
within 21 sessions, and was it larger than month-1 fees? Not paid by session 21: P-14 21.1 % of starts, P-16 40.9 %.
P therefore loads heavily on **speed**. That sits badly with the handoff's "speed and bankroll barely move P",
which is a statement about 61 designs, most of them far below the top (Q2).

**What it ignores, measured:**

- **Magnitude.**
  - At month 3, P-14's starts that are not ahead average -$1,654 and those ahead +$5,550. P-16's average -$2,122 and
    +$6,566.
  - P scores a start at +$1 the same as one at +$20,000, and one at -$1 the same as one at -$7,000.
  - The mass right at the threshold: 5.1 % of P-14's starts are within $250 below zero at month 1, and 3.1 % are
    within $250 above. For P-16 the shares are 12.2 % and 8.7 %.
- **The bankroll a user actually has.**
  - The replay assumes "the bankroll never binds" (manifest `conventions.net`).
  - P-14's starts ahead at month 3 needed up to $4,097 before their first payout; 8.5 % of them needed more than
    $2,500. One P-14 start needed $7,198 (the maximum of `spent_before_first_payout`).
  - S1 guards only the p90 over starts paid by session 126, with 10 % tolerance.
  - Counting a start only if it is ahead *and* never needed more than B (the "P at B" rows in Q4) drops P-14 from
    0.671 to **0.511 at $2,000** and **0.637 at $2,500**.
- **Months 4 to 12.**
  - S4a and S4b are 0.985 / 1.000 (P-14), 0.966 / 0.999 (P-15) and 0.977 / 0.999 (P-16) (`user_drivers.csv`
    `design_table`). With a 5-point tolerance they cannot bind on dollars.
  - Mean month-12 net is $29,188 (P-14), $24,068 (P-15) and $33,505 (P-16), on starts with 252 sessions. Nothing in
    the scorecard reads it.
  - The design's share of the variance of a user's net is 0.075 / 0.032 / 0.041 at months 1 / 2 / 3, against 0.195
    at month 12 (`user_drivers.csv` `design_vs_luck`, `u1_configurations`, verdict). Among the three rows to beat it
    is 0.016 / 0.002 / 0.016 against 0.141.
  - So P is read where the design matters least. The month-12 figures do rest on only about six windows that do not
    overlap (Stage 2 D-628 (c)).
- **A start that never gets paid** counts the same in P whether it lost $1,000 or $7,000. S5a reads the p10 only. The
  tail below it (CVaR10 -$2,328 for P-14, -$2,922 for P-16) is unguarded.

**Could a design raise P and leave users worse off without a guard catching it? Yes.** Each of these passes line
(ii) as written:

1. **Tip the near-zero starts.** Shift fees or payout timing so that starts just below zero at sessions 21, 42 and 63
   land just above. Upper bound from the masses above: +0.030 in P for P-14, +0.054 for P-16. That is larger than
   every real gain on file.
2. **Give up magnitude.**
   - S3c may fall 10 %. For P-14 (S3c 1.851, mean month-3 fees $5,231) that is mean month-3 net falling from $4,453
     to about $3,485, a 22 % cut, at equal fees.
   - Month-6 and month-12 dollars may fall without limit while the shares ahead stay within 5 points of about 1.0.
3. **Fatten the tail below p10.** No guard reads it.
4. **Need more cash per start.** P has no per-start bankroll, and S1's p90 may rise 10 %.

The tolerances also stack: nine guarded measures may all be worse at once by their full tolerance.

**Verdict on Q1.** P is a defensible reading of the operator's first stated wish: be ahead early. But it is a value
judgement, not a neutral summary, and its blind spots are exactly the ones a design family can move.

---

## 3. Q2: is S3c a sound screening target or partly mechanical?

**The arithmetic.** Pooled S3c at month 3 is `sum(payouts) / sum(fees)` = `1 + mean(net_month_3) /
mean(fees_month_3)` (`user_journey.py` `metric_rows`, money back; checked: P-14 1.851329 both ways, P-16 2.079778).
P's month-3 term is the share of the same `net_month_3` above zero. Suppose two designs differ mainly in where their
month-3 distribution sits ("a lever that changes what the trades pay"). Then S3c and P move together by
construction. Suppose they differ in shape or in fees (a bold funded opening, fewer purchases). Then they need not.

**The data.** 61 designs = `user_drivers.csv`'s set: the three rows to beat plus the 58 non-hypothetical cells of
families 1 to 7. Each value is the family file's `cell` section, block `all`, role `family cell`, verdict arm. Six
held-out cells from families 8 and 9 (`u_limit.csv`, `u_resolve.csv`) are added where stated. Scripts:
`q2_cells.py`, `q2_analysis.py`, `q2_top.py`, `q2_screen.py`. Spearman throughout. The whole-family bootstrap uses
2,000 draws, seed 20261115.

| set | n | Spearman(P, S3c) |
|---|---|---|
| all 61 (reproduces `between_designs` `all_cells` `spearman.S3c` 0.7646) | 61 | 0.765 |
| leave out `plan` (P 0.06-0.59) | 49 | 0.613 |
| leave out `consistency` (P 0.000-0.001) | 57 | 0.711 |
| leave out `consistency` and `plan` | 45 | 0.500 |
| ... and `firms` | 39 | 0.392 |
| other single families left out | -- | 0.75 to 0.84 |
| families 8, 9 held out, with the three rows to beat | 9 | 0.450 |
| P >= 0.55 | 33 | 0.254 |
| **P >= 0.60 (the region R\* is in)** | **22** | **-0.198** (family bootstrap -0.60 to +0.02) |
| fee levers: `budget`, `entry`, `seats` | 30 | 0.299 |
| trading or contract levers: `hours`, `plan`, `consistency` | 22 | 0.922 |
| pooled within family (ranks centred in each family) | 61 | 0.487 |
| between family means | 8 | 0.905 |

Within each family: `budget` -0.67 (8 cells), `entry` +0.39 (14), `seats` +0.26 (8), `hours` +0.77 (6), `firms`
+0.94 (6), `plan` +0.96 (12), `consistency` +0.78 (4, all with P <= 0.001). The three rows to beat: P orders them
P-14 > P-15 > P-16, while S3c orders them P-16 (2.080) > P-14 (1.851) > P-15 (1.743).

**What goes with P near the top** (the 22 cells with P >= 0.60): S3a +0.48, S5a +0.33, S1 -0.28, S3b -0.27, S3c -0.20.
The top five by S3c of all 61 are `seats1` (P 0.538, 37th by P), `wallet1500` (0.585), `budget10` (0.627),
`wallet1000` (0.548) and `budget15` (0.674). All five are fee levers on P-16's trades.

**Kill line or ranking?** Of the 66 cells other than P-14 (all nine families), 39 have S3c at or below P-14's and
none of them beats P-14 on P. 27 have S3c above, and only 4 of those beat P-14 on P: `budget15`, `budget15_p14`,
`budget30_p14` and `nobudget_p14`, all in the purchase-budget family and all within 0.021.

**Verdict on Q2.** Three things produce the 0.76:

1. The two families that pay back less than their fees (Consistency and the flat plans): both P and S3c collapse
   there.
2. A shared numerator: both are read off the same month-3 net.
3. Between-family composition: eight points give 0.90.

S3c rewards a smaller fee denominator, so a screen ranked by S3c would rank fee-cutting cells first and P-14 near
the bottom of the competitive set. It is a reasonable **kill line** ("not below R\*'s S3c") and a poor **ranking
target**. The charter's sentence "what a funded account pays back per fee dollar is the measure that moves P; speed
and bankroll barely do" holds across failed and working designs. **Among working designs it does not hold, and speed
is what tracks P.**

---

## 4. Q3: the start-day unit and the honesty of the intervals

**The series.** Per start, `d = A(P-14) - A(P-16)` on common start dates, verdict arm (`q3_dependence.py`). All
starts: n = 1,629, mean +0.051. Judged block: n = 595, mean +0.103. The judged-block P is 0.7193 for P-14 (equal to
every family file's `judged` `reference_value` 0.719328) and 0.6162 for P-16. The standard deviation per start is
0.438.

**Autocorrelation of d:**

| lag (starts) | 1 | 2 | 5 | 10 | 21 | 42 | 63 | first lag <= 0 |
|---|---|---|---|---|---|---|---|---|
| judged block | 0.47 | 0.35 | 0.20 | 0.14 | 0.16 | 0.01 | -0.08 | 28 |
| all starts | 0.49 | 0.38 | 0.23 | 0.16 | 0.13 | 0.05 | -0.02 | 56 |

**Standard error of the judged-block mean difference, and the effective number of starts:**

| estimator | SE | n_eff |
|---|---|---|
| iid (wrong) | 0.018 | 595 |
| moving block, b = 21 / 63 / 126 / 189 / 252 (2,000 draws, seed 20261700) | 0.041 / 0.051 / 0.055 / 0.060 / 0.056 | 114 / 74 / 63 / 54 / 61 |
| Bartlett long-run variance, L = 63 / 126 / 189 | 0.054 / 0.054 / 0.055 | 66 / 65 / 63 |
| non-overlapping batch means, b = 63 (9 batches) | 0.056 | 61 |

On all starts: moving block b = 63 / 126 / 189 gives SE 0.034 / 0.035 / 0.037 (n_eff 175 / 163 / 153), and batch
means b = 126 / 189 give 0.042 / 0.046 (n_eff 116 / 98).

**Is a 63-session block long enough?** For the *standard error*, nearly. The autocorrelation is gone by lag 28 to 56,
and longer blocks raise the SE only 8 to 16 %. But three things make the *interval* dishonest at the family's level
(`q3_calib.py`, `q3_calib2.py`, `q3_more.py`):

1. **Too few blocks.** 595 starts hold 9.4 blocks of 63, so the bootstrap's spread is itself estimated from about 9
   degrees of freedom.
   - The test: a Gaussian null with this data's own autocorrelation (the all-start autocorrelation of d to lag 62,
     Bartlett-tapered; n_eff 62; seeds 20261116 to 20261118).
   - The rule's lower limit then sits a median **2.51** true standard errors below the mean (10th to 90th percentile
     3.43 to 1.76), against the 3.32 a calibrated one-sided 0.05/110 limit needs.
   - **Rejection rate at a true zero:** D-621's line (percentile, 2,000 draws, "difference and limit both above zero")
     gives 56/4,000 = 1.4 % in one run and 1.6 % in another. A normal line with the bootstrap's SE gives 0.85 %. A
     Student-t on the 9 non-overlapping 63-start batch means (df 8, critical value 5.12) gives 0.08 %. The nominal
     rate is 0.045 %.
2. **Monte Carlo noise at the far tail.**
   - `np.percentile` at 100 x 0.05/110 of 2,000 draws interpolates at index 0.91, between the smallest and
     second-smallest draw.
   - On the real P-14 minus P-16 judged data the limit is -0.0107 at seed 20261700. Across 20 seeds it averages
     -0.021 (SD 0.010, range -0.045 to -0.002). At 200,000 draws it is -0.029.
   - So the registered 2,000-draw limit is noisy and biased towards zero.
3. **An uncentred bootstrap.**
   - `block_indices` draws block starts uniformly from 0 to n - 63. The first and last start get 0.019 and 0.017
     times the uniform weight, the middle 1.116 times.
   - On P-14 minus P-16 the bootstrap's centre is 0.132, against a sample difference of 0.103: +0.029, about 0.57 SE.
   - The cause: P-14 led in 2024 Q2 to 2025 Q1 and trailed in 2024 Q1 (-0.153) and 2026 Q2 (-0.089), the two edges.
   - The percentile interval is not recentred, so where in the block a candidate's advantage falls changes its
     verdict.

**Is the judged block large enough at one-sided 0.05/110? No.** Minimum detectable difference (MDD) at 80 % power,
judged block, `(z_0.05/110 + z_0.2) x SE` = 4.16 x SE (normal theory, nominal level):

| pair (how far apart the trades are) | judged diff | SE b=63 (b=126) | MDD, nominal | MDD, calibrated t (about 5.5-6 x SE) |
|---|---|---|---|---|
| P-14 vs P-16 (different signal and stop) | +0.103 | 0.051 (0.055) | 0.21 (0.23) | about 0.30-0.33 |
| P-14 vs P-15 | +0.059 | 0.044 (0.034) | 0.18 (0.14) | about 0.19-0.28 |
| P-14 vs P-13 (P-14's trades, other purchase rule) | +0.068 | 0.027 (0.024) | 0.11 (0.10) | about 0.13-0.16 |
| P-16 vs its 4-seat cell | -0.028 | 0.019 (0.013) | 0.08 (0.05) | about 0.07-0.11 |
| P-16 vs its 5 + 1 cell | -0.005 | 0.017 (0.015) | 0.07 (0.06) | about 0.08-0.10 |
| P-16 vs its funded-cap cell | +0.017 | 0.015 (0.012) | 0.06 (0.05) | about 0.07-0.09 |
| P-14 verdict vs P-14 point | -0.002 | 0.015 (0.012) | 0.06 (0.05) | about 0.07-0.09 |

The SEs implied by Stage 2's own judged rows agree: `(difference - lower) / z` gives 0.065 for `budget15` (P-16
trades) and 0.018 for `resolve3_p14` (P-14 trades) (`u_budget.csv`, `u_resolve.csv` section `judged`, measure P;
`fam3.py`).

Two more readings:

- **Power of the D-621 line under the Gaussian null** (as implemented, so anti-conservative): at a true shift of 1 /
  2 / 3 / 4 standard errors it carries 10 / 34 / 65 / 87 %. The calibrated t carries 1 / 5 / 16 / 37 %.
- **Against what is plausible.** The largest P gain over P-14 among 66 cells is `nobudget_p14`, +0.021 on all starts
  (`u_budget.csv` `cell`). On the judged block that cell is at 0.7176 against 0.7193 (`u_budget.csv` `choice`, late).
  Nine families' picks reached 0.48 to 0.68 on the judged block against P-14's 0.719.

**F-01's stage D** puts tickets on P-16's schedule and judges the result against P-14, so its paired noise is
P-16-like. Even under the nominal rule it needs a judged P of about 0.89 (50 % power) to 0.93 (80 %). That is a gain
of 0.27 to 0.31 over P-16's 0.616, close to the ceiling (P-14 is at 0.719 and P cannot pass 1).

**The year rule (4)(e).**
- Method: per-year SEs come from a moving block within each year (b = 63, 2,000 draws, seed 20261115), years are
  treated as independent, and the pass chance is P(at most one of the seven years worse).
- P-14-vs-P-16-like noise: the rule passes 6 % / 27 % / 71 % / 96 % of designs whose true gain is 0 / +0.02 / +0.05 /
  +0.10.
- Same-trade-variant noise: 6 % / 52 % / 95 % / 100 %. This is rough: within-year blocks are few, and 2026 holds 78
  starts.

---

## 5. Q4: would a utility over the distribution rank the designs differently?

**The measures** (`q4_utility.py`; `user_journey.csv` `start`, starts with `observed >= 63`):

- **P at B:** the mean over months m = 1..3 of `1[net_m > 0 and dip_m <= B]`. Here `dip_m` is the larger of
  `spent_before_first_payout` (when the first payout came by session 21m) and `-min(net_1..net_m)`. Dips inside a
  month after the first payout are not visible, so this is an *upper* bound on what a user with bankroll B gets.
- **Loss-averse mean:** `mean(net3 + min(net3, 0))`, losses counted twice.
- **CVaR10:** the mean of the worst 10 % of month-3 nets.
- **CE (log, $10k):** `10,000 x (exp(mean(log(1 + net3 / 10,000))) - 1)`. Every month-3 net is above -$10,000; the
  lowest is -$7,419.50.

**Verdict arm, all starts** (n = 1,629; FV3-C 1,021). Rank in brackets, 1 = best of nine:

| config | P | P at $2,000 | P at $2,500 | mean net m3 | loss-averse | CVaR10 m3 | CE log $10k | S3c |
|---|---|---|---|---|---|---|---|---|
| **p14** (R\*) | **0.671 (1)** | 0.511 (2) | **0.637 (1)** | $4,453 (4) | $4,201 (4) | -$2,328 (2) | $3,810 (4) | 1.851 (4) |
| p15 | 0.642 (4) | 0.494 (3) | 0.610 (2) | $3,854 (6) | $3,563 (6) | -$2,462 (4) | $3,217 (6) | 1.743 (8) |
| p16 | 0.620 (5) | 0.428 (5) | 0.558 (5) | $5,243 (2) | $4,920 (2) | -$2,922 (5) | $4,357 (3) | 2.080 (2) |
| p13 (beside only) | 0.645 (3) | 0.247 (7) | 0.454 (7) | $5,038 (3) | $4,833 (3) | -$2,040 (1) | $4,403 (2) | 1.768 (7) |
| p16_4+0 | 0.646 (2) | 0.555 (1) | 0.598 (3) | $4,273 (5) | $3,877 (5) | -$3,173 (7) | $3,496 (5) | 2.084 (1) |
| p16_5+1 (Lucid upper bound) | 0.610 (6) | 0.148 (9) | 0.473 (6) | $5,909 (1) | $5,559 (1) | -$3,265 (8) | $4,809 (1) | 1.984 (3) |
| p16_funded_cap | 0.600 (7) | 0.471 (4) | 0.569 (4) | $3,754 (7) | $3,479 (7) | -$2,401 (3) | $3,207 (7) | 1.793 (5) |
| rc_s150_london | 0.469 (8) | 0.302 (6) | 0.414 (8) | $3,119 (8) | $2,675 (8) | -$3,128 (6) | $2,442 (8) | 1.773 (6) |
| fv3c (beside only) | 0.468 (9) | 0.193 (8) | 0.331 (9) | $2,686 (9) | $2,101 (9) | -$3,990 (9) | $1,945 (9) | 1.449 (9) |

**Among the three eligible rows to beat:**

| arm and block | P-14 first on | P-16 first on |
|---|---|---|
| verdict, all starts | P, P at $2,000, P at $2,500, CVaR10 | mean net, loss-averse mean, CE, S3c |
| point arm, all starts | the same | the same |
| verdict, judged block | P, P at $2,000 / $2,500, CVaR10, CE ($4,262 vs $4,203) | mean net ($5,130 vs $4,756), loss-averse mean, S3c |

Judged-block values: P 0.719 / 0.661 / 0.616 for P-14 / P-15 / P-16; CVaR10 -$1,436 / -$2,388 / -$3,103.

**P-14 stays first on P among all nine** configurations. On the money-weighted measures it is 4th, behind the Lucid
upper-bound cell, P-16 and P-13. P-13 and FV3-C are never rows to beat because they use an unverified closure rule.

**Paired differences against P-14** (verdict). SE is the larger of the moving-block SE at b = 63 and b = 126 (2,000
draws, seed 20261115). "Inside" means |difference| < 2 SE.

| vs P-14 | P | P at $2,500 | mean net m3 | loss-averse | CVaR10 |
|---|---|---|---|---|---|
| P-16, all starts | -0.051 (0.034) inside | -0.079 (0.035) outside | +$790 ($591) inside | +$718 ($663) inside | -$594 ($551) inside |
| P-15, all starts | -0.029 (0.034) inside | -0.027 (0.035) inside | -$599 ($563) inside | -$639 ($609) inside | -$134 ($319) inside |
| P-16, judged | -0.103 (0.055) inside (z about 1.9) | -0.137 (0.057) outside | +$374 ($1,000) inside | +$156 ($1,075) inside | -$1,667 ($760) outside |
| P-15, judged | -0.059 (0.043) inside | -0.063 (0.047) inside | -$1,084 ($708) inside | -$1,212 ($770) inside | -$952 ($669) inside |

Only the bankroll-limited share (P-16 needs more cash) and, on the judged block, CVaR10 separate P-14 from P-16 by
more than 2 SE.

**Rank stability** (`q4_rankstab.py`; moving block b = 126, 1,000 draws, seed 20261119). The share of resamples in
which each row to beat ranks first:

| measure | all starts | judged block |
|---|---|---|
| P | P-14 0.92 | P-14 0.995 |
| P at $2,500 | P-14 0.90 | -- |
| mean net m3 | P-16 0.84 | P-14 0.52 / P-16 0.48 |
| loss-averse mean | P-16 0.76 | -- |
| CVaR10 | P-14 0.85 | P-14 1.00 |

These resamples have only 13 (all starts) or 5 (judged) blocks, so read them as optimistic (finding 2).

**Verdict on Q4.** A utility over the distribution changes R\*: money-weighted readings put P-16 first, while
downside and bankroll readings keep P-14 first. Apart from bankroll and, on the judged block, CVaR10, the differences
between the rows to beat are inside noise. **R\* = P-14 is a consequence of choosing P, not a separated fact** (in
line with Stage 2 D-628 (a)). A bankroll-limited P agrees with P and is closer to what the operator named, the
"bankroll needed".

---

## 6. Q5: Goodhart risks a new family could exploit

| target | how it can be gamed | size on file | caught by |
|---|---|---|---|
| P | Time fees and payout requests around sessions 21, 42 and 63 (defer purchases past the reading; request payouts to land before it). The user's welfare barely changes. | Starts within $250 below zero at months 1 / 2 / 3: P-14 5.1 / 2.4 / 1.5 %; P-16 12.2 / 3.1 / 1.0 %. Upper bound on the P gain: +0.030 / +0.054 | nothing: no guard reads cash between month ends |
| P | Turn a few large wins into many small early ones (smaller funded risk, earlier minimum payouts) | S3c may fall 10 %, about 22 % of P-14's month-3 profit; months 6 to 12 dollars free | S3c only beyond 10 %; no guard on month-6/12 dollars |
| P | Push losses into the tail below p10 (more purchases in bad starts) | CVaR10 unguarded; S5a reads one percentile | S5a, partly |
| S3c | Cut the fee denominator (fewer seats, wallet stops, purchase caps) | The top 4 S3c cells cut fees on P-16's trades, P 0.54 to 0.63 | P at the campaign stage, if the screen lets it through |
| S3c (pooled) | A ratio of sums is driven by the big-payout starts: concentrate payouts | S5c 0.37 to 0.50 across the top cells | S5c's 10 % tolerance |
| line (3)(i) | An advantage concentrated in mid-2024 to early 2025 is weighted about 1.1 times, one at the block's ends about 0.02 times | Centre shift +0.029 (0.57 SE) on P-14 minus P-16 | nothing |
| line (3)(i) | A seed-sensitive limit: at 2,000 draws a candidate near the line passes or fails by bootstrap noise (SD about 0.01) | -- | nothing |
| line (ii) | Guards with tolerances below their noise (S5a $10.57 against SE $325 to $673): the designs that pass are the ones lucky on the guards, so selection rewards noise | Pass chance for a truly equal design: about 0.18 (P-16-like) to 0.34 (same-trade variant); S4b and S5b not included | -- |
| the judged block | Already read by nine Stage 2 families. The handoff's lessons ("bold funded opening", "US hours level") come partly from judged readings, so a new family's ideas are not independent of 2024 to 2026 | -- | the confirmation window only |
| 0 % denial | Designs that lean harder on payouts a firm may deny (more accounts, bolder openings) get full credit | not measurable here | tier-1 conduct rules only |

**What protects the program.** R\*'s winner's curse (finding 14), the walk-forward choice, and the confirmation
window. That window is unread data and a purchase, and it is the only fully fresh test. Given finding 3, it is also
the only test able to tell a modest improvement from luck, and only if it is long.

---

## 7. Proposed changes

Each change is labelled **objective change -- the operator's decision** or **a reporting addition the lead can
adopt**.

1. **Demote S3c from screening target to kill line.** Rank a cheap screen on S3a (share paid by session 21) beside
   S3c, or on P from a thinned replay of the choice block (every 21st start). Never rank on S3c alone. Before any
   screen is used, record its rank correlation with P among designs within 0.10 of R\*, not across all designs. --
   *objective change -- the operator's decision* (it rewrites E-001 (2) and the charter's section 2).
2. **Recalibrate line (3)(i).**
   - Replace the 2,000-draw percentile with a Student-t on non-overlapping 63-start batch means, df = batches - 1.
     F-01's stage C already uses this form on 21-session blocks. Or use a studentised circular (centred) block
     bootstrap at 200,000 draws or more.
   - Carry a null-simulation calibration test in this repository's suite.
   - State plainly that power falls further.
   - *objective change -- the operator's decision* (the charter adopts D-621 (3) unchanged).
3. **Get power where it exists.** Pick one or more:
   - (a) Judge a family on both folds: choose on 2020-2023 and judge on 2024-2026, then the reverse, with both judged
     results required. This doubles the judged starts without reusing a choice.
   - (b) Where possible, judge a candidate against a same-trades twin of R\*, since paired noise falls about 3 to 4
     times.
   - (c) More history (the handoff's 3.4: NQ from 2009).
   - (d) Accept that only contract-shape changes with large effects can carry, and say so in each family file before
     its build.
   - *objective change -- the operator's decision* for (a) to (c); (d) is a reporting addition.
4. **Make guards non-inferiority tests, not point comparisons.** "Worse than R\* by more than the tolerance at a
   one-sided interval" fails a design, "not shown worse" passes it. Replace S5a's relative tolerance, which breaks
   down near zero, with a dollar tolerance in contract units (for example five evaluation fees). Add a guard on mean
   net at months 6 and 12. -- *objective change -- the operator's decision*.
5. **Put the per-start bankroll into the objective.** Read P at B (ahead and never needed more than B) at the
   operator's limits ($2,000 and $2,500, already the menu's), as co-primary or as a hard constraint on the menu, in
   place of S1's p90. -- *objective change -- the operator's decision*.
6. **Report beside P in every reading**, each with its paired SE: P by month (m1, m2, m3), mean month-3 net, the
   loss-averse mean, CVaR10, P at $2,000 and $2,500, mean net at months 6 and 12. -- *a reporting addition the lead
   can adopt*.
7. **Report the honesty of every interval.** Give n_eff (the long-run-variance estimate), the moving-block SE at
   blocks 63, 126 and 189, the bootstrap's centre beside the sample difference, the lower limit under 20 bootstrap
   seeds and at 200,000 draws, and the **minimum detectable difference at the family's level before the judged block
   is read**. F-01 records this for stage C; extend it to stage D, where the table above already says about 0.21 to
   0.30. -- *a reporting addition the lead can adopt*.
8. **Label S3c "partly mechanical"** in any reading of drivers against P, as S5a and S4a already are. Report its
   correlation with P inside families and in the top region. -- *a reporting addition the lead can adopt*.
9. **Add a month-boundary diagnostic for every candidate.** Report the share of starts within $49 and within $250 of
   zero at sessions 21, 42 and 63, and P re-read at sessions 20/22, 41/43 and 62/64. The runner must record those
   closes, since U1's start rows hold month ends only. A gain that disappears when the reading shifts a day is
   timing, not value. -- *a reporting addition the lead can adopt*.
10. **Record in F-01's next decision row, before its build, that stage D is very unlikely to carry** under the
    current rule (finding 3), so a stage-D close is read as "not detectable here", not as "does not help". --
    *a reporting addition the lead can adopt* (F-01's file itself stays as declared).

---

## 8. Provenance

The scratch scripts live in the session scratchpad
`C:\Users\resni\AppData\Local\Temp\claude\197752aa8b2362c7\9862c1b3-c57d-4498-a2d7-44492c7a25e6\scratchpad\phase0_B\`.
That folder is not durable: it may be cleared, so move them into the repository before any figure is promoted to a
result.

| script | what it does |
|---|---|
| `load_starts.py` | `user_journey.csv` section `start`, selected columns, to `starts.csv` (29,222 rows; no start read from an exact run) |
| `q2_cells.py` | the `cell` section of each `u_*.csv` (block `all`, role `family cell`, plus the rows to beat) to `cells_all.csv` |
| `q2_analysis.py`, `q2_top.py`, `q2_screen.py` | Q2 |
| `q3_dependence.py`, `q3_calib.py`, `q3_calib2.py`, `q3_more.py` | Q3; seeds 20261115 to 20261118 and 20261700 + i |
| `fam3.py` | the families' judged P rows |
| `q4_utility.py`, `q4_rankstab.py` | Q4; seeds 20261115, 20261119 |
| `q1_q5.py` | Q1 and Q5 |
| `dvl.py` | `user_drivers.csv` `design_vs_luck` |

Source hashes are the vendored manifests': `user_journey.csv` sha256 `5c8e7413...`, `user_drivers.csv` `0ea08cb8...`.
The bootstrap reimplements `user_journey.block_indices` line for line, in a separate process; nothing under
`vendor/` was imported or edited. OMP_NUM_THREADS=1, one process at a time.
