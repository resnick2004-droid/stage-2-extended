# F-XX: resting orders at pre-session levels (family RL2)

**Status: declared before anything of it is built or read.** It is pinned by the sha256 of its LF text in its decision
row. Nothing declared is edited: a change is a new family under a new row. It replaces F-01
(`prereg/F-01_resting_order_level_atlas.md`, withdrawn, its k = 10 spent, E-007 (a)). No bar has been read for it, no
level computed, no outcome of any order computed.

**Its text's history.** It was drafted and reviewed as `prereg/DRAFT_F-02_resting_levels.md`:
- commits fc7747b, 255e13b, 9ee82e6 and 825f264, 0d40ece, 1d61a31, and Q-72's text;
- four red-team reads and the prereg-gatekeeper's refusal of the fifth text, each answered in section 0.

At the pin the file is renamed `prereg/F-02_resting_levels.md` (the reader's `DECLARATION_PATH`) and `F-XX` becomes
`F-02`; nothing else changes (N9). The pinning row names the commit and the sha256 it pins.

**The pin's conditions (the final read's M3; E-052 (2)).** It is pinned only if both hold:
1. **Q-55's clean rerun** of Q-16's calibration (E-035 (4)) reproduces `cons`, and the treated two-sample `cons`, at or
   below its level on every real and realistic null at k = 11;
2. **Q-83's fresh-seed validation** (seeds 20262010-20262019, E-052 (2)) HOLDS on E-052's criterion: at every k in 11
   to 15, no real or realistic null's 95 % interval lies wholly above nominal. Its count-persistent tables are reported
   beside, met here by K0 and C0 (7.10, 9.0), and never folded in.

If either does not hold, this text is withdrawn before any read, to be re-declared under a new row, and nothing of it
runs. Stage A's planning reads Q-55's power tables, and no figure of Q-16 is cited before that rerun. The pinning row
also cites the count and the sha256 of the judged session list Q-83 writes (9.1, 17 item 12).

Q-16 is merged (E-035), and its statistics stand where the draft's marks stood (Q-57). The pass line is `cons`
(`extended/lift_bound.SHIPPED`); C1' is its two-sample form; the scorecard's P comparison is `extended/p_bound`'s
`pcons`.

The early-close calendar this file reads is pinned (E-029).

What the pin requires, and what stays open, is in section 19. **The judged-block reads this family may make are named
on the one line the reader requires (section 18.1, E-026).** Anything chosen after a reading is exploratory and reported
apart.

| field | value |
|---|---|
| family | RL2: resting stop and limit orders at four pre-session price levels, judged on their trades first (E-008) |
| id | F-XX (`prereg/F-02_resting_levels.md` at the pin) |
| program family number k | **11** (F-01 spent 10, E-007 (a); the gatekeeper's count, E-045) |
| level | one-sided **0.05 / (k (k + 1))** = **0.05 / 132** |
| development data | NQ 1-minute bars, 2020-01-02 to 2026-07-16 |
| choice block | fills from 2020-01-02 to 2023-12-29 |
| judged block | fills from 2024-01-02 to 2026-07-16 |
| confirmation | NQ from 2026-07-17 (`reserve`, reserved): NQ's fourth (Stage 2 D-107, the operator's decision), a purchase |
| confirmation tests already on NQ | three (P-05, P-06, P-10; `vendor/stage2/config/windows.yaml`) |
| cells (`k_cells`) | `fade` at 4 kinds + `break` at 1 kind (`rn100`), x 3 stops = (4 + 1) x 3 = **15**, each counted whether killed or read |
| hypotheses | 15 cells x 3 R = **45** signed hypotheses over 36 (kind, stop, R) questions (section 5.9) |
| the pass statistic | the lift over the coin twin on the same fills, by `cons` (`extended/lift_bound.SHIPPED`, E-035): the trade-weighted session-cluster t on 21-, 42- and 63-session blocks, all three required |
| the value bar | $500 a year at that bound (`vendor/stage2/results/u_value_map.csv`, section `bar`, `target=500`) |
| seeds | 20261930 to 20261939, each assigned in section 15 |
| model card | none: no fitted model; the grid is the family |

---

## 0. What this corrects

### 0.1 The Phase 0 findings on F-01 (`docs/audits/phase0/D_protocol.md`, `docs/reviews/phase0_red_team_2026-11-15.md`)

| finding | F-01's defect | the correction | section |
|---|---|---|---|
| D-1 | the fill-bar rule biases break down and fade up | the pair rule (`fill_bar="pair"`); the ambiguous share read and capped (K5) | 5.5, 7.4, 9.5 |
| D-13 | the mirror booked at the rule's fill; fast-market overshoot | symmetric booking decides C1; the `rule_fill` ladder decides C2; a spread-and-jumps T-13 on the null | 5.5, 9, 17.5 |
| D-2 | `or30` in Stage 2's closed branch; line 23 false; break cells load on D-592's lead | `or30` out; line 23 corrected; prior exposure; `break` at range extremes dropped; C1' for the rest | 1, 2, 6.2, 9.2 |
| D-3 | stage D cannot identify the tickets' value | stage D keeps only E-008's floors and the scorecards beside; base by stop; tickets routed, and valued, only where they can be reached | 10, 11, 12 |
| D-4 | the MDL is far above the value bar | the MDL from counts and Q-16's power curve before stage B; a close reads "no lift above the MDL" | 7.9, 13 |
| D-5 | a minute of look-ahead at 08:25; the side set at `t_live` | levels and sides from bars stamped at or before 08:24; the void rule at `t_live` | 4 |
| D-6, M1 | the confirmation is NQ's fourth and P-16's window; it cannot confirm P | declared so; it tests the pick's trades | 14 |
| D-7 | cells counted, hypotheses not | both counted | 5.9, 16 |
| D-8, D-9, D-10 | K2 at 10 %; K3 cannot fail; stage A read an outcome | 5 % every year; K3 recorded; K4's outcome part moved | 7 |
| D-11 | roll days, the seam, early closes; `rn100` | calendar voids from pinned calendars; `rn100` in the futures' own price | 4.5, 5.1 |
| D-12, D-14, D-15 | drift and placebo; the bootstrap and estimand; no parameter table | beside or decisive; stated; the table | 6, 8, 9.6 |
| A, MINOR 1 and 2 | D-212 / D-308 swapped; "the 12.5-point stop loses to costs (D-527)" | cited correctly; the stop admitted after re-reading D-527 | 3, 6.3 |
| M5, M7, N-2, N-3, M4 | the tickets' bound; k; seeds; the flatten; the signal service | declared; F-01 spent 10; new seeds; Stage 2's flatten; one user | 11.4, 15, 16, 5.4, 1 |

### 0.2 The first red team on the draft (`docs/reviews/DRAFT_F-02_resting_levels_2026-11-15.md`)

| finding | the correction (all confirmed as removing their defects by the third read, except where 0.3 says otherwise) | section |
|---|---|---|
| F1 | `break` at `on` and `pd` dropped (24 cells to 18); C1' kept at `pdc` and `rn100` -- and since the final read's G1 at `rn100` only (18 cells to 15); T-14 (c) | 6.2, 9.2, 17.6 |
| F2 | past-only placebo sources; placebo tickets in the shift test; block-total denominators | 5.8, 9.2, 17.3 |
| F3 | the stop band per state; floor (ii)'s form (E-022 (1)); the 50-tick `dv` | 3, 6.3, 10 |
| F4 | C2 at `rule_fill`; a spread-and-jumps T-13 | 5.5, 9.3, 17.5 |
| F5, F6, F7 | the rule side's 2020-2023 resolution; a pinned calendar (E-029); one 0.05 bound in stage D | 8.5, 4.5, 11.4 |
| F8 | one priority order for value and routing -- the quantities now too (0.3, V1) | 10, 11.2 |
| F9, F10 | prior-exposure rows; what a fade pass means | 2, 9.7 |
| N1-N9 | as rules or readings | 5.6, 7, 13 |

### 0.3 The third read (`docs/reviews/DRAFT_F-02_resting_levels_v3_2026-11-16.md`)

| finding | the defect | the correction | section |
|---|---|---|---|
| P1 (MAT) | `pdc`'s placebo copied the source day's side, so D at `pdc` carried any effect of the target day's overnight-move sign -- the variable S3's gap rules read | `pdc`'s (and `pd`'s) placebo on the **target day's own side**; T-14 (e), a planted overnight-sign drift of either sign, with a declared kill; 9.2 and 14 corrected | 5.8, 9.2, 14, 17.6 |
| V1 (MAT) | C2 capped at the forward count, counting slots the base's own trades take first (most funded openings before 08:30) | caps at the **records count at most**, and at the uses the routing can reach at 08:30 (a direction-free count on the base's choice-block campaign); **a ticket is never an account's second trade of a session**; the two tickets of a kind are one-cancels-other | 10, 11.2, 7.8 |
| T1 | T-14 (c)'s generator, plant size and day count unfixed; a weak plant killed cells | every generator parameter, plant, day count and precision fixed here; a plant L cannot see means a refusal, not a kill | 17.6 |
| T2 | the T-13 (b) switch at two granularities; nothing if `rule_fill` itself favours the rule | one granularity, per (side rule, stop, R); a rung ladder with a kill at its end | 5.5, 7.1, 17.5 |
| V2 | the 50-tick ρ called conservative without proof | an approximation of unknown sign; C2 at ρ, with ρ squared and no scaling beside | 10 |
| S1 | the ticket's size and floor (ii)'s intention omitted the room cap | the size and intention are the engine's `_plain_size` (the allowance, the Combine's room cap, the 45-tick floor); floor (ii) becomes a build check | 6.3, 11.1, 11.2 |
| N1 | what T-13 (b) can move | stated in 5.5: only `fade` cells; `break`'s level-specific overshoot stays in C1 | 5.5 |
| N2 | T-14's two-sided criterion | decided: a positive bias in D kills `break`, a negative one withdraws the fade's level claim | 17.6 |
| N3 | `rn100`'s distances scaled by volatility | copied unscaled | 5.8 |
| N4 | draw coupling across kinds and blocks | one generator per (replicate, kind, block) | 5.8, 15 |
| N5 | ambiguous pairs counted as resolved | resolution read with each trade's own fill-bar rule | 7.2, 8.5, 9.4 |
| N6 | FOMC days from no named file; an unscheduled statement | Stage 2's A3 list, named; scheduled statements void the day; an unscheduled one cancels resting tickets from its release | 4.5 |
| N7 | the ladder's rungs undefined for `fade` | one rung definition for both side rules | 5.5, 9.6 |
| N8 | T-13's tier and walk; consequences of a failure | the tiers marked, the walks written out, a failure stops the build | 17.5 |
| N9 | the T-12 sentence stale | updated: references against uses | 15 |
| N10 | the version label | stated above; the row names the commit | status |
| N11 | CHARTER section 4 states D-212 (1)'s letter | the charter now records the allowance-capped reading (E-032 (3)) | 3 |
| N12 | the Tier 1 windows cited from an audit note | a reading; the rules-verifier records 13613539 before anything asserts them | 3 |
| N13 | the red team's scripts | listed in section 2 | 2 |
| E-026 | the reader requires a judged-block reads line | added, with each purpose | 18.1 |
| E-031 (2), E-032 (1) | the reverse walk-forward would make the judged block a block that chooses | struck from the reads line and the readings; the pick's year-by-year readings beside instead | 9.6, 15, 18.1 |
| E-032 (2) | how the reachable count is read | through `extended/reader.py` on choice-block days only; if that cannot be done, C2 falls back to the records cap, with no new purpose | 10, 7.8 |
| E-029 | the calendar | `config/calendar_early_closes.csv`, pinned | 4.5 |
| E-035 (Q-57) | the `[Q-16]` marks | C1 and C2 by `cons`; C1' by `two_sample_bound` (treated-cluster df, count-centred residual sums); the year-by-year readings and the confirmation by `cons`; the P comparison by `pcons`; planning from Q-16's power tables as Q-55 reruns them; stage B's bootstrap stated as an uncalibrated selection device; the sides' persistence stated | header, 7.9, 8, 9, 12, 14, 15 |

### 0.4 The final read (`docs/reviews/DRAFT_F-02_resting_levels_v4_2026-11-16.md`)

| finding | the defect | the correction | section |
|---|---|---|---|
| G1 (MAT) | at `pdc` the placebo matches the overnight move's sign but not its size, which is the real level's distance; a size-dependent overnight effect gives D > 0 with no level effect | **the lead's ruling, option (a): `break` at `pdc` dropped** (18 cells to 15, 45 signed hypotheses over the same 36 questions); `fade` at `pdc` stays, judged on its trades, with **no level claim at `pdc`**; the same confound named for the `pd` and `on` readings | 1, 2, 5.8, 6.2, 9.2, 9.7, 13, 16, 17.6 |
| M1 | T-14 (b)'s and T-13 (a)'s pass lines had no fixed cells or multiplicity; T-14 (a) had no target | each test's cells fixed, a Bonferroni Z over them, T-13 (a)'s walk per stop and its seed, (a)'s criterion a bound at the family's level | 15, 17.5, 17.6 |
| M2 | T-3 replaced bars only, but the reachable count reads Stage 2's walks | the reachable count reads only through the reader's choice-block window and asserts every row's date; T-3 also poisons the judged rows of every file it opens, on temporary copies; the fallback recorded before stage A | 10, 17.7 |
| M3 | nothing followed if Q-55 did not reproduce `cons` holding | the pin only after Q-55 reproduces it; otherwise withdrawn before any read | status, 19 |
| M4 | the planning lookup was undefined for k = 12-14 and below 200 fills | the k = 15 column when k is not tabulated; "above the 200-trade entry" below; each figure's null stated; a close worded "no lift detectable at this power" | 7.9, 13 |
| M5 | the news row stale; 8284211's EIA releases inside the resting window | E-034's 13613539 entry cited; a full-allowance ticket cancelled around the EIA releases; USDA Crop Production not modelled | 3, 11.2, 12 |
| M6 | the confirmation's length rule not fully fixed | the construction fixed (session sums resampled with replacement, thinned, on 21 m sessions), its zero-lift rate beside | 14 |
| N1 | `lift_bound.py` not hashed | its blob (and `p_bound.py`'s) recorded for the pinning row; the run asserts them | 9.1, 12 |
| N2 | the judged calendar and the df unnamed | the day list named; df = non-empty blocks - 1 | 9.1 |
| N3 | C2's λ the all-fills mean, stage D spending first fills | λ on first fills reported beside | 9.6 |
| N4 | stage B's bootstrap called studentised | relabelled: normalised by the sample's se | 6.1, 8 |
| N5 | T-14's kill multiplicity | Bonferroni over the kill checks; the rate stated | 17.6 |
| N6 | the T-12 record stale | updated: references, and a range bound in code, are not uses | 15 |
| N7 | stage D's ticket shift by `t21e` | stated as U1's form, consistent with R\*, lax at family levels | 11.4 |
| N8 | stage D's ticket walks under `stage_D_gate_floor` | the row widened | 18.1 |
| N9 | the pinned file's name and changed status lines | stated for the pinning row | status |
| R1 | the null class reasoned from the side reset, not the pair terms' dependence | the residual stated; the pick's choice-block lift by quarter and its block lifts' lag-1 correlations beside | 9.1, 9.6 |

### 0.5 The prereg-gatekeeper's refusal of the fifth text (E-045, TASK_QUEUE Q-72)

| gap | the defect | the correction | section |
|---|---|---|---|
| 1 (template section 3) | tier 2 named only "R at or below 1" | all four tier-2 patterns, each stated for the tickets and the bases; off in the base case, on beside | 3 |
| 2 (template section 5) | the readings beside a campaign verdict incomplete | the break-even denial, the zero-edge twin, the tickets' e and its bound for each R, and stage one's D-47 criterion, added beside | 11.5 |
| 3 | D-663's stress readings left to "where Q-18's tooling exists" | each reading named, with its blocks, levels and seeds (20261933, 20261934, 20261936, reassigned before any use); A2 and B3 not run, and why | 11.5, 15 |
| 4 | line 192: `s3_event_kinds.csv` "not vendored" | vendored by E-043 (905eb19); not read for this text | 2 |
| notes | the pin-time form; E-015's limits; the Combine-headroom check | the title and status in pin-time form (k = 11, `prereg/F-02_resting_levels.md`); only limits approved before stage D flag the menu; F3 does not apply to a trades-lift confirmation | status, 12, 14 |

### 0.6 The red team's read of the pass-line code (`docs/reviews/PASS_LINE_CODE_2026-11-16.md`; E-052, TASK_QUEUE Q-84)

| finding | the defect | the correction | section |
|---|---|---|---|
| M1 (MAT) | no Q-16 null lets the fills per session persist, and on nulls where it does `cons` can exceed its level | the fill intensity's persistence stated beside the side's; **K0** at stage A and **C0** at stage C, `cons`'s size on the cell's or the pick's own counts, outcome-free, seeds 20262020-20262023; their level and power shown on synthetic toys before the pin (E-051's rule) | 7.10, 9.0, 9.1, 15 |
| M2 (MAT) | Q-55 replays Q-16's own draws, so it can only reproduce | the pin also requires Q-83's fresh-seed validation to HOLD on E-052's criterion | status, 19 |
| m1 | the level argument unchecked | the stage-C runner asserts the level equals `family_level(11)`, lies in (0, 0.5), and k is in `K_RANGE` -- a build check | 17 item 12 |
| m2 | the calendar only half pinned | the runner asserts `n_sessions` and the judged session list against Q-83's count and sha256, cited in the pinning row -- a build check | 9.1, 17 item 12 |
| -- | "K0" named the build's synthetic kills | renamed **KB**, so that K0 is E-052's | 5.5, 7.1, 17.6, 18.2 |

## 1. Hypothesis

**The mechanism.** Orders cluster at prices everyone can see before the session: just beyond the prior session's high
and low, the overnight range, the prior close, and round numbers. Stop-loss and breakout stop orders beyond such a
level turn a touch into a burst of market orders in the direction of the break (a cascade); resting limit orders at
the level absorb a touch and push it back (a rejection). Which dominates is the question.

The evidence that clustered orders at visible levels move prices is in currency markets:
- Osler 2003, *Journal of Finance*, "Currency orders and exchange rate dynamics";
- Osler 2005, *Journal of International Money and Finance*, "Stop-loss orders and price cascades in currency markets".

For NQ it is untested here.

**What this family can test on this window.**
- **The rejection side (`fade`)** is tested at all four kinds.
- **The cascade side (`break`)** is tested at round numbers only.
  - At the two range-extreme kinds a break is also a breakout of a long window, whose follow effect Stage 2 read three
    times on this window and closed the window to (D-592), so `break` at `on` and `pd` is left to a test on unread data.
  - At the prior close the level's distance from `P_ref` *is* the overnight move's size, so no placebo can match it
    without collapsing onto the level, and a size-dependent overnight effect would pass as a level effect (the final
    read's G1). So `break` at `pdc` is dropped too (6.2).
- **At the prior close,** the level's side is also set by the overnight move: a fade there always trades with it. The
  fade is judged on its trades, and no level claim is made there (9.7).

**What Stage 2 did and did not do (F-01's line 23 corrected).**
- **Stage 2 did enter at levels.**
  - ORB5's entry was a stop order at the opening range's edge, on 5- to 60-minute ranges; a trigger before the order
    worked was skipped, left resting at its level (`rest`, Stage 2 D-266) or chased
    (`vendor/stage2/config/orb5_grid.yaml`).
  - ORB6's hypothesis was a limit at the broken edge (D-277, D-278).
  - Both are inside the 08:30 opening-range branch Stage 2 closed for good (D-275, D-281).
- **Stage 2's atlases read the prior day's high and low** (`pdhl`) as a breakout entered at the market after the first
  close beyond it:
  - five bars late, followed and faded (families A1 to A3; D-460 declared the pattern core and A1);
  - against its coin twin, at delays of zero and five minutes (A4, D-550).
- **What this family adds is narrower:** resting orders at four pre-session levels other than the opening range, live
  from the US open, filled at the level itself.

**Why a resting order.** A ticket written at least five minutes before it can trigger moves the operator's latency
(D-266) from the fill to the placing of the order, so the order fills at its level, not five minutes after.

**Whose accounts.** One user's own accounts, each its own trades, one position at a time across the firm (Stage 2
D-157, D-429; E-012 (3)). F-01's "the form suits a signal service" is dropped: users placing the same tickets would be
coordinated trading (E-007 (c)). Every order is placed by hand; there is no automated or API entry (the operator's
rule, E-008).

**What would make it worth something.** Its lift in win probability over the coin at the same fills, times how often it
can actually be used, times what a win is worth where it is used (section 10). It is judged first on its trades (E-008),
with the user's journey reported beside (section 12).

## 2. Prior exposure: what has already read these bars, these levels and this mechanism

| read | what it read | span | what it recorded | bearing here |
|---|---|---|---|---|
| ORB1 to ORB6 (Stage 2 D-275, D-277, D-278, D-281) | the 08:30 opening-range breakout: a stop at the range's edge (skip, rest, chase), a limit retest | NQ development | the branch closed for good; whether a later hypothesis is "genuinely different is the operator's call" (D-281 (3)) | `or30`, and every opening range, is out (E-007 (b)) |
| atlas families A1 to A3 (D-460; `config/atlas_a1.yaml` to `a3.yaml`) | `pdhl` (the prior day's 08:30-15:10 CT high and low, the first close beyond) followed and faded, five bars late; `orb_rth5/15/30`, `orb_globex30`; P-13/P-14's `brk30` | 2020-01-01 to 2026-07-16 | P-14 (A3-BRK30-CB20) chosen from A3 | `pd`'s break and fade were read at the market; `pdhl` is defined on 08:30-15:10, this family's `pd` on the bars stamped 08:30-14:59 -- close, not identical |
| A4, the coin-benchmarked atlas (D-550, D-555, D-557, D-558) | 34 patterns at 25 and 37.5 points, delays 0 and 5, lift over the coin twin, follow and fade one test: `brk` at k = 5, 10, 15, 30, 60 and 90 minutes; `orb` at the 08:30, 17:00 and 02:00 opens (17:00 and 02:00 at m = 15, 30, 60); `pdhl` | 2020-01-01 to 2026-07-16 | survivors "short breakouts and n-bar runs on 5- and 10-minute bars, a few at 15 and 60 minutes", all on the follow side (D-555); **`pdhl` is not among the survivors' classes**; "a genuine but tiny direction effect", no campaign value (D-558) | the follow effect reaches 60-minute breakouts -- the evidence behind dropping `break` at `on` and `pd`; `pdhl`'s own lift is in `results/a4_coin_atlas.csv`, not vendored |
| program S, S1 (D-578, D-580) | the side of recent breakouts and momentum followed and faded, on P-16's schedule | 2020-01-02 to 2026-07-16 | two follow rules (15-minute momentum, the latest 5-minute breakout) survive the lift test; both grow less than P-16 on 2020-2023 and more on 2024-2026, so the span guard rejects them | the follow effect's sign by era |
| program S, S3 (D-586, D-587, D-588, D-589) | 13 rules, among them `gap_glbx` (the session's first open against the previous trading day's last close at or before 16:00 CT) and `gap_rth` (the open after 08:30 against the same close), followed and faded against the coin twin | 2020-01-02 to 2026-07-16 | one survivor, `lnbar1x4_follow`; the Benjamini-Hochberg rejections "every one on the follow side and all but one on the breakout and n-bar rules" (D-588); the gap rules' own rows are in `results/s3_event_kinds.csv`, vendored by E-043 (905eb19) and not read for this text | **the overnight move, read on this window: the reason `break` at `pdc` is dropped and the fade at `pdc` carries no level claim (6.2, 9.7; the final read's G1), after the side-matched placebo of the third read's P1 proved to match its sign but not its size** |
| D-592 | S3's candidate at the five-minute latency | -- | fails; the follow effect "broad and slow rather than tied to the last bar"; "re-testing it on that window would reuse hypotheses already seen, so it is recorded as a lead for unread data" | `break` at range extremes dropped (6.2); C1' for the other breaks (9.2) |
| Stage 2's effect atlas (`config/effect_atlas.yaml`, H01 to H04, F01 to F02) | the overnight return's, and the previous close's location's, relation to the day's move | Stage 2's development | returns, not levels | the overnight move's sign again; named for completeness |
| program U, nine families (`results/u_budget.csv`, `u_resolve.csv`) | P on start days from 2024 | judged block of starts | all closed below P-14 | the judged block has been read for P nine times |
| P-05, P-06, P-10 (`config/windows.yaml`) | confirmation reads of 2025-07-01 to 2026-07-16 | that window | development since D-461: "a new NQ model may be built on it, never confirmed on it" | inside this family's judged block |
| this repository | F-01 (withdrawn before any read); its walker (E-010, E-011), which computed no level and no outcome but P-16's identity; the red team's synthetic scripts -- `negation.py` and `iut.py` (first read), `pdc_side.py` and `bounce.py` (third read) -- and its parser `leaf_agg.py` of a vendored result; no bar | -- | -- | no read of these levels exists here |

**Not found as price levels.** No Stage 2 decision row or configuration reads the overnight high and low, the prior
close or round numbers as price levels. Searched: `vendor/stage2/DECISIONS.md` and `vendor/stage2/config/`, for "prior
close", "overnight", "round number", "prior day" and `pdhl`, 2026-11-15. The prior close was read as a reference for a
gap's side (S3).

**The drafter's own reads,** all vendored Stage 2 inputs, no bar: `results/u_value_map.csv` (sections `records_leaf`,
`identity`, `place_values`, `definitions`), `results/stop_band.csv`, `config/fv3_corrected_portfolio.yaml`,
`propedge/campaign/sizing.py`, `config/atlas_a3.yaml` and its FOMC sources.

**What follows.**
1. The judged block is late development, not out of sample (D_protocol P-3): a pass is a development finding whose
   evidence is its confirmation (section 14).
2. `or30` is out, and `break` at `on` and `pd` is dropped (6.2).
3. A `break` cell, now only at `rn100`, passes only if its lift also exceeds that of matched non-level crossings, where
   the placebo's distances are exchangeable with the level's (5.8, 9.2).
4. The pick's year-by-year readings are reported with every judgement (9.6). The reverse walk-forward is dropped
   program-wide (E-031 (2)): it would make the judged block a block that chooses.

## 3. Contract fit: the constraints each cell lives inside

| constraint | how the family meets it |
|---|---|
| latency at least 5 minutes (Stage 2 D-266) | every level and side from bars stamped at or before `t_pub - 1 min`; the order works from `t_live = t_pub + 5 min` (section 4) |
| one position per firm, 5 minutes flat (D-429); one trade an account a session (the table's model, P-14's campaign) | stages A to C read every fill independently; stage D routes by the strict rule, a ticket only to an account that has not traded that session, with cancel-on-entry (11.2) |
| every trade resolving: at most 5 % to the flatten, overall, per market and per year, no time stops (D-212 (2) as D-308 (3) raised it) | the cutoff rule and K2 (7.2); the pick's rule side on 2020-2023 (8.5); C3 on the judged block (9.4); each read with every trade's own fill-bar rule (N5) |
| realised risk matching intended (D-212 (1)) | cannot fail in the walk (K3, 7.5). In stage D the ticket is sized by the engine's own form (6.3), under which the line can miss only by whole-micro rounding near a Combine's floor: a build check (11.1). **Against CHARTER section 4's words:** the charter now records this allowance-capped reading of D-212 (1) (E-032 (3)), the form R\* = P-14 was itself judged by (E-022 (1)); the letter's share is reported beside (11.5) |
| the sizeable stop band (`vendor/stage2/results/stop_band.csv`, D-201 (2)) | the narrow edge per state of stage one's family: 82 ticks in the Combine, 134 ticks funded below +$2,000, and 45 ticks funded at or above +$2,000, where the cost-drag floor binds (`cost_drag_floor_ticks`, the stop at which costs reach a tenth of it; D-271 (3)'s 45 MNQ ticks). 50 ticks is inside the band in the last state only, 100 ticks in the Combine and the last, 150 ticks in all three (6.3). The bases' $50K table sizes by its own allowance, which 6.3 and section 10 use |
| news | tickets go live at 08:30 CT: on a BLS 08:30 ET release day strictly after 07:35:00 CT (E-007 (d)), and outside Topstep's Tier 1 windows -- 07:25-07:35 CT on CPI, NFP and PPI days, and around both FOMC events, as Track E read them (E-007 (6), `docs/audits/phase0/E_rules_currency.md` C1). The article is recorded by E-034 (`config/rules_extended.yaml`, key `tier1_news_events_restriction`, article 13613539, read 2026-11-16, with its windows and its rule that positions opened before a window may be kept); the tickets avoid those windows by construction. FOMC days as 4.5 (d). **Releases inside the resting window (the final read's M5).** 8284211 lists seven releases (E-034), three of which fall inside it: EIA crude oil inventories, EIA natural gas inventories, and USDA crop production. 10305426 forbids "trading your full Maximum Position Size directly into a scheduled major news event", and which events count is unstated (E-034). A 50-tick Combine ticket is sized at the 50-micro allowance, which is full size. So **a ticket sized at its account's full allowance is cancelled from five minutes before to five minutes after each EIA release** (11.2), dated by Stage 2's `config/im2_release_calendar.csv` (its `EIAC` and `EIAG` rows). Crop production has no vendored dated calendar, so it is listed as not modelled (12 item 8). Tickets below the full allowance rest through every release, as Stage 2's rule allows for 09:00 CT releases (D_protocol N-6) |
| conduct, tier 1 (D-145) | no hedge (cancel-on-entry: never two positions in the firm); no simulator-fill exploitation (stops of at least 50 ticks, no stop move); no maximum size into news (above, 4.5 (d), and 11.2's release cancellation); no copying (each ticket on one account, D-157); nothing concealed (a resting order at a public level) |
| conduct, tier 2 (Stage 2 D-145; `vendor/stage2/propedge/campaign/conduct.py`; the template's section 3) | each pattern is **modelled off in the base case (D-289) and on beside, in stage D's placement-on arm (11.5)**. **(1) R at or below 1** (`conduct.MIN_RR`): applies to the tickets of an R = 1 pick, to Combine tickets the engine's need-aware exits close below 1R (6.3), and to the bases' own 1R leaves. **(2) A funded position risking more than half the $2,000 drawdown, an account-deciding position** (`MAX_FUNDED_RISK_FRACTION_OF_DRAWDOWN`): applies to the tickets -- a 150-tick ticket at the funded opening on 20 micros carries $1,500 (6.3), and a funded 100- or 150-tick ticket carries more than $1,000 wherever the ladder's 30- or 50-micro step sizes it -- and to the bases' own funded openings (P-16's carries $1,500). **(3) Maximum position on most trades:** can apply to the tickets, since a 50-tick ticket is capped at its allowance in the Combine (50 micros, the full size of a $50K Combine) and at the funded opening (6.3); the share of the pick's tickets at full allowance is reported beside (11.5); it applies to the bases' own trades wherever their tables size at the allowance, as registered. **(4) Several accounts at the MLL in one day:** a campaign pattern, not one ticket's -- a ticket is one account's only trade of its session (11.2), so tickets alone cannot put several accounts at the MLL in a day, but with the bases' trades they can; the campaign's share of such days is reported beside (11.5) |
| conduct, tier 3 | priced at 0 % denial in the verdict, 10, 25 and 50 % beside, with the break-even denial (11.5); Terms of Use s.8 (outsized positions) priced among them (E-013 (1)) |
| hours | US regular hours: tickets live from 08:30 CT to their cutoff (at latest 14:30); the walk ends at the bar ending 15:08 CT |
| entry by hand | the user places the ticket between `t_pub` and `t_live`, or at 08:30:00 itself if the platform does not take an order that works only from 08:30; the fill window opens with the bar stamped 08:30 either way (E-008) |
| firm rules | only rules verified in `vendor/stage2/config/rules.yaml` or `config/rules_extended.yaml` |

## 4. Time, data and calendar (D-5, D-11, F6, N6)

1. **The clock.** The bar store's `ts` is the bar's **start**, in epoch seconds UTC (`vendor/stage2/data/README.md`
   section 5). Bars are read on Stage 2's trading-day clock in US/Central (`atlas_local.day_arrays`, the walker's
   clock; DST handled there). The bar stamped 08:24 CT covers 08:24:00-08:24:59 and closes at 08:25.
2. **Publish.** `t_pub` = 08:25 CT. Every level and every side reads only bars stamped **at or before 08:24** CT (closed
   by 08:25). The **reference price** `P_ref` is the close of the last bar stamped at or before 08:24 of that trading
   day; with none, every kind is void that day.
3. **The side, fixed at `t_pub` and never re-read.** A level above `P_ref` is a resistance, below it a support. A level
   exactly at `P_ref` is void (counted) -- except `on`, whose high is a resistance and low a support by construction.
4. **Live and void.** `t_live` = 08:30 CT: the order works from the bar stamped 08:30.
   - "A bar after `t_live`" is a bar stamped at or after 08:30.
   - At `t_live` the price is the close of the bar stamped 08:29 (the last closed by then; the walker's `price_at`).
   - A stop already at or through its price, or a limit already at or beyond its price, is **void** for the day
     (skipped, counted).
   - A bar stamped 08:30 or later that opens beyond a stop fills at its open plus the slippage (a gap through). One
     that opens through a limit fills at the limit's price, never better.
5. **Calendar voids, from calendars fixed before the run -- never from the day's own bars.** Each is counted.
   - **(a) Scheduled early closes** -- from the pinned calendar `config/calendar_early_closes.csv` (E-029): every
     `early_close` row, and every `holiday` row with a `close_ct` (an abbreviated session). Such a day voids every
     kind; the next trading day voids `pd` and `pdc`. (A `holiday` row with no `close_ct` holds no session.)
   - **(b) Data-defect days** -- every `data_defect_candidate` row of the same file, and the purchase seam (trading day
     2025-06-30, no trades; 2025-07-01, its first two hours missing; P-14 caveat C2). Such a day voids every kind; the
     next trading day voids `pd` and `pdc`.
   - **(c) Roll days**, from the bar store's manifest `rolls`. The charted contract is chosen on the previous day's
     volume (README section 5), so a roll is known in advance. A roll day voids `pd` and `pdc`, whose prices would be
     the old contract's.
   - **(d) FOMC (N6)**, from the list Stage 2's A3 reads (`vendor/stage2/config/atlas_a3.yaml` `news.fomc`:
     `config/im2_release_calendar.csv` with `config/sources/fomc_statements_2020_2024q1.csv` and
     `fomc_statements_2026q3.csv`).
     - A **scheduled** meeting's statement day carries no tickets: the day was known in advance.
     - An **unscheduled** statement (the file's "(unscheduled)" and "(notation vote)" rows) released before 08:25 CT
       changes nothing: it was known at `t_pub`.
     - One released after 08:25 CT -- in the window, 2020-03-03 at 10:00 a.m. ET -- cancels every resting ticket five
       minutes before its release. A ticket that filled earlier walks on.
   - **(e) Edges.** The first trading day in the store voids `pd` and `pdc`.
   - **(f) Any other day whose bars end early** -- an unscheduled halt, or a gap not in (b) -- is **kept**. Its
     tickets work as on any day; the walk ends at the day's last present bar, and an open trade is flattened there and
     counted unresolved (the walker's `walk_end`). This differs from Stage 2's local walk, which marks an early close
     from the day's own bars (`atlas_local.py`, D-215).
6. **The test** (17.3): every level, side, `P_ref`, `A_D` and placebo ticket is unchanged when every bar stamped at or
   after 08:25 that day, and every bar of every later day, is replaced.

## 5. The grid and the walk

### 5.1 Levels (each frozen at `t_pub`)

| kind | the level(s) | tickets a day |
|---|---|---|
| `pd` | the prior regular session's high and low: the bars stamped 08:30-14:59 CT of the previous trading day | 2 |
| `on` | the overnight session's high and low: the bars stamped 17:00 CT the evening before to 08:24 CT | 2 |
| `pdc` | the prior regular session's close: the close of its bar stamped 14:59 CT (void when that bar is missing) | 1 |
| `rn100` | the nearest multiples of 100 points of the futures' own price above and below `P_ref`; when `P_ref` is exactly a multiple, the multiples 100 points above and below it | 2 |

### 5.2 Side rules (order types), and where each is offered

| rule | offered at | at a resistance | at a support | fill |
|---|---|---|---|---|
| `break` | `rn100` | buy **stop** one tick above the level | sell **stop** one tick below | the first bar stamped at or after `t_live` trading at the stop's price; at that price plus one tick (`slip_ticks`, `vendor/stage2/config/atlas_a3.yaml`; D-95), or at the bar's open plus one tick when it opens beyond the stop |
| `fade` | `pd`, `on`, `pdc`, `rn100` | sell **limit** at the level | buy **limit** at the level | only when a bar stamped at or after `t_live` trades **through** the level by at least one tick; at the limit price, never better |

### 5.3 Per ticket

One ticket a level a day. It fills at most once and is never re-armed. Unfilled, it is cancelled at its (cell, R)'s
**cutoff** (7.2): it fills only on bars closing at or before the cutoff. When both levels of a kind fill on one day,
both fills count in stages A to C. In stage D, and in the valuation, the two tickets of a kind are one-cancels-other
(11.2).

### 5.4 The walk

This repository's walker (`extended/walker.py`; its identity with Stage 2's walk holds, E-011), with this family's
preset, built after the pin:
- **The walk's end and the flatten.** The walk's last bar is the bar ending 15:08 CT. A trade still open there is
  flattened at the worst of the bars ending 15:08-15:10 CT, less two ticks (Stage 2's `fv3_rung_walk` convention;
  `STAGE2`'s `walk_end` and `flatten`; D_protocol N-3).
- **No stop move** (`breakeven` off; 6.2).
- **The barriers.** From the fill, the stop at S ticks is reached by a touch. The target at floor(R x S) ticks is
  reached by a trade through it by a tick. On a bar reaching both, the stop.
- **Costs.** Stage 2's per-contract cost at the stop (`atlas_a3.fee_by_stop`; `vendor/stage2/config/fills.yaml`):
  - no entry tick on a resting fill (a stop's slippage is in its price);
  - a tick on a stop exit, none on a target;
  - two on a flatten, with Stage 2's two in the flatten price, as its scorer does (E-010 (3)).

### 5.5 The pair, the fill bar, and the bookings (D-1, D-13, F4, T2, N1, N7)

For every fill, the **mirror** is the opposite side at the same fill bar, with the same stop, targets and walk. The
**trigger** is the first price the bars show at the fill condition: a stop's price on a touch, or the open on a gap; a
tick through a limit's price, or the open when a bar opens through it. **The fill bar of a pair is settled by the pair
rule** (`fill_bar="pair"`): if it touches either trade's stop or target, the pair is **ambiguous** -- both booked as
stopped losses (costed as stops), zero lift, counted (K5). Otherwise both are walked from the next bar, and the fill bar
is not read.

**The bookings:**
- **Symmetric** (`mirror_booking="symmetric"`): the mirror at 2 x trigger less the rule's fill, paying the rule's
  offset in its own direction. It is side-neutral on a tick-continuous driftless walk (`tests/test_walker_t13.py`).
- **The `rule_fill` rungs, k = 1, 2, 4 (one definition for both side rules, N7).** At rung k, the rule's fill is
  unchanged -- the stop's price plus one tick, or the limit's price -- and the mirror is booked at the rule's fill
  moved k - 1 ticks in the mirror's own favour.
  - Rung 1 is the walker's `mirror_booking="rule_fill"`. It hands each mirror its rule's offset, so it is conservative
    for both side rules on a tick walk and under the bid-ask bounce (the third read's N1, *synthetic*).
  - Rungs 2 and 4 stand for a market that, at the fill, stood that many ticks past the trigger. They need a mirror
    offset the build adds to `mirror_price` after the pin.

**Which booking decides what -- one granularity, per (side rule, stop, R):**
- **C1 and C1'** use symmetric booking, unless the spread-and-jumps T-13 (17.5 (b)) finds symmetric booking's null
  interval wholly on the side favouring the rule. Then they move to rung 1.
- **C2** uses rung 1, unless T-13 (b) finds rung 1's interval wholly on the rule's side. Then C2 (and a moved C1) uses
  rung 2. If rung 2's interval is wholly on the rule's side too, that (cell, R) is killed (KB, 7.1).

**What T-13 (b) can move (N1).** Under its declared generator the bid-ask bounce dominates: symmetric booking leans
toward `fade` and against `break`, so the switch can move only `fade` cells, and only where T-13 (b) has the power to
see the bias. A **level-specific** overshoot -- a stop cascade jumping through the level within the minute, which is
the hypothesis itself -- is in no generic null.
- It stays in `break`'s C1, bounded by K5, which removes the fill bars that ran S - 1 ticks or more.
- C1' cancels the part that is the same at placebo crossings.
- C2's rung 1 absorbs a tick of it.

The rest is stated, not removed.

### 5.6 The lift, and the estimand of every stage

- **The pair term:** w = 1/2 [win(rule) - win(mirror)], in win probability. A win is the target reached; a flatten or
  an ambiguous pair is not a win.
- **The lift:** lift(c, R) = **the mean of w over all the (cell, R)'s fills in a block** (D-14), ambiguous pairs
  included as zero. The net R lift, 1/2 [net R(rule) - net R(mirror)], is reported beside.
- **The estimand, plainly.** The pair rule zeroes every fill whose fill bar reached a barrier (under symmetric booking,
  a bar that ran S - 1 ticks or more from the trigger on either side, where a within-minute cascade would show). So the
  lift measures direction on fills whose fill minute stayed inside that band, diluted toward zero by the rest. K5
  bounds the zeroed share at 5 %.
- **R-independence.** For R of 1 or more, whether a fill is ambiguous does not depend on R.
- **Resolution, as distinct from the lift (N5).** Unresolved shares (K2, the eligibility of 8.5, C3) are read with
  **each trade's own fill-bar rule** (`fill_bar="declared"` for that trade alone; feature-rules 3: "for one trade's own
  outcome only"). So a pair zeroed for the lift whose rule trade stays open still counts when it reaches the flatten.
- **Break and fade at `rn100` are near-exact negatives** under symmetric booking: the same trigger, the same
  pair with the labels swapped, differing only on gap fills and when the price at `t_live` stands exactly at the level
  (verified on synthetic days, the red team's `negation.py`). Under the `rule_fill` rungs both are handicapped and are
  no longer negatives.

### 5.7 The coin twin beside

A seeded coin twin -- one fair side per fill, in date order of the fills, cell by cell in table order, seed
**20261931** -- is computed beside. It decides nothing.

### 5.8 The placebo (decisive for `break` at `rn100`; beside for every `fade`)

The placebo measures the statistic at prices with no visible meaning, to separate the level's effect from what a
comparable crossing carries (D_protocol 1.3 item 4). Every input comes from the past (F2).
- **At `rn100`** the placebo's distances are exchangeable with the level's: both are arithmetic modulo 100 points,
  which no feature of the path determines.
- **At `pdc`** the placebo matches the overnight move's sign (P1) but not its size, which is the real level's distance
  (the final read's G1).
- **At `pd` and `on`** it matches neither the window broken (F1) nor the overnight path.

So outside `rn100` the placebo-differenced lift is a reading only, and carries no level claim (9.7).

- **`A_D`:** the mean, over the 20 most recent trading days before day D with a full regular session (not an early
  close, not a data-defect day, 4.5), of the regular session's range -- the high of its bars stamped 08:30-14:59 less
  their low. It is roll-free.
- **The source day, from the past only.** For target day E, a source day D is drawn from the kind's eligible days at
  least 21 and at most 252 trading days before E. Eligible means the kind is not calendar-void that day and `A_D` is
  defined.
- **Correspondence.** Each of E's published real tickets of the kind has a counterpart on D:
  - `pd`'s high and low;
  - `on`'s high and low;
  - `pdc`'s one ticket;
  - `rn100`'s multiple above and below.

  With no counterpart (void on D), that ticket has no placebo.
- **The placebo ticket for one of E's real tickets:**
  - **Its side is the real ticket's side on E** -- the target day's own side (P1). At `pdc` that is the side set by
    E's own overnight move. At `on` and `rn100` it is so by construction. At `pd` it is E's own high or low side.
  - **Its distance from E's `P_ref`** is the counterpart's distance on D:
    - at `pd`, `on` and `pdc`, scaled: max(1, round(d_D x `A_E` / `A_D`)) ticks, because those distances are set by
      the path's volatility;
    - at `rn100`, **unscaled**: d_D ticks (N3), because its distances are set by arithmetic, uniform in price whatever
      the volatility.
  - **Everything else is the real ticket's:** side rule, stop, R, `t_pub`, `t_live`, cutoff, void rule, walk and
    bookings.

  Every input -- D's distances, `A_D`, `A_E`, E's `P_ref` and E's sides -- predates E's `t_pub`.
- **Replicates and the generators (N4).** There are five replicates, j = 0..4. Each (replicate j, kind k, block b) has
  its own generator, `numpy.random.default_rng([20261932, j, k, b])`:
  - k: 0 `pd`, 1 `on`, 2 `pdc`, 3 `rn100`;
  - b: 0 the choice block, 1 the judged block, 2 the confirmation window;
  - it makes one `integers(len(pool))` draw per target day, in date order, over the source pool in date order.

  A target day with an empty pool (in the store's first weeks) carries no placebo, and is counted.
- **Coincidences.** A placebo price that happens to lie near a real level on E is kept. That moves the placebo toward
  the level's own lift, which is conservative for a pass.
- **Placebo cells.** There are 15 (one per cell). They are controls, not hypotheses, and their counts and K5 shares are
  read in stage A. Only the `rn100` placebo decides anything (C1'); elsewhere it is a reading.

### 5.9 Cells and hypotheses

- **Cells:** (4 `fade` kinds + 1 `break` kind) x 3 stops = **15 cells**.
- **Hypotheses:** each cell is read at R = 1, 1.5 and 3, so **45 signed hypotheses** (36 `fade`-signed and 9
  `break`-signed), over 36 (kind, stop, R) questions. At `rn100` both signs are asked; at `pd`, `on` and `pdc` only the
  fade sign.
- **How they are counted:** every cell is counted whether killed or read; stage B's maximum covers the dependence
  between break and fade (E-003 (d)).

## 6. Parameters: fixed, searched, dropped (D-15)

### 6.1 The table

| parameter | what it is | class | value | source or reason |
|---|---|---|---|---|
| market, bars | the data | fixed | NQ 1-minute bars, Databento GLBX.MDP3 `ohlcv-1m`, raw prices, one contract a day | E-002; `vendor/stage2/data/README.md` |
| development window | the days read | fixed | 2020-01-02 to 2026-07-16 | CHARTER; `config/windows.yaml` |
| choice and judged blocks | where the pick is chosen, where it is judged | fixed | 2020-01-02 to 2023-12-29; 2024-01-02 to 2026-07-16 | CHARTER section 3 |
| level kinds | which prices | searched | `pd`, `on`, `pdc`, `rn100` | F-01's, less `or30` (E-007 (b)) |
| side rules | break or fade | searched | `fade` at all four kinds; `break` at `rn100` | F-01, less `break` at the range extremes and the prior close (6.2) |
| stops | the stop's distance from the fill | searched | 50, 100, 150 ticks (12.5, 25, 37.5 points) | P-14's two rungs and P-16's stop; 6.3 |
| R | target over stop | searched | 1, 1.5, 3 | the table's main asks (handoff 2.5; `u_value_map.csv` `records_leaf`); 6.2 |
| `t_pub`, `t_live` | publish and live times | fixed | 08:25 and 08:30 CT | D-266; the US open |
| `P_ref` | the price that sets each side | fixed | close of the last bar stamped at or before 08:24 | D-5 |
| void rule | an order already through at `t_live` is skipped | fixed | price at `t_live` = close of the bar stamped 08:29 | F-01; the walker's `price_at` |
| stop slippage | ticks paid on a stop entry | fixed | 1 tick; symmetric booking at 2 and 4 beside (break) | `atlas_a3.yaml` `slip_ticks`; D-95; D-13 |
| limit fill | when a limit fills | fixed | a trade through by at least 1 tick, at the limit's price | feature-rules 3 |
| target rounding; two-barrier bar | -- | fixed | floor(R x S); the stop first | Stage 2's `target_ticks`; feature-rules 3 |
| fill-bar settlement | the fill bar | fixed | the pair rule for the lift; each trade's own rule for resolution | E-010; D-1; N5 |
| booking for C1 and C1' | the mirror's price in the pass line | fixed rule | symmetric; rung 1 where T-13 (b) finds symmetric booking favours the rule; per (side rule, stop, R) | E-010; D-13; T2 |
| booking for C2 | the mirror's price in the value line | fixed rule | rung 1; rung 2 where T-13 (b) finds rung 1 favours the rule; killed where rung 2 does too | F4; T2 |
| walk end and flatten | where an open trade is closed | fixed | the bar ending 15:08 CT; the worst of bars ending 15:08-15:10, less 2 ticks | Stage 2's convention (N-3) |
| costs | fees and ticks | fixed | Stage 2's at the stop; exit ticks 1 / 0 / 2 | E-010, E-011 |
| cutoff | when an unfilled ticket is cancelled | fixed rule, value read on the choice block | per (cell, R): the latest of 14:30, 14:00, ..., 10:00 CT passing 7.2 | F-01's rule; D-8 |
| resolution ceiling | the most that may reach the flatten | fixed | 5 % overall and in every calendar year | D-212 (2) as D-308 (3) raised it |
| K1 supply | the fewest fills | fixed | 100 on the choice block and 12 in every calendar year of it | F-01; the value map's smallest use count |
| K5 ambiguity cap | the most fills the walk cannot settle | fixed | 5 % of fills | **the drafter's choice**: it buys measurability, not an error rate; set at D-212's flatten ceiling by analogy only |
| calendar voids | days with no ticket | fixed | 4.5's lists, from `config/calendar_early_closes.csv` and Stage 2's FOMC list | D-11; F6; N6; E-029 |
| `rn100` spacing | the round number | fixed | 100 points, in the futures' own price | F-01; D-11 |
| placebo | the control for `break` | fixed | 5 replicates; past-only sources 21 to 252 trading days back; the target day's own sides; distances scaled by `A` (20 full sessions) at `pd`, `on`, `pdc`, unscaled at `rn100` | D_protocol 1.3 item 4; F2; P1; N3; the drafter's 21, 252, 20 and 5 |
| stage B bootstrap | the family-wise gate on the choice block | fixed | stationary, mean block 21 sessions, circular, 2,000 replicates, centred, normalised by the sample's se (not studentised replicate by replicate, N4), seed 20261930 | D-14; D-550's form |
| stage C level and statistic | the pass line | fixed | one-sided 0.05 / (k (k + 1)); `cons` for C1 and C2, `two_sample_bound` (`cons`, treated-cluster df) for C1' | E-008; E-035 |
| stage B's gate | the choice block's selection device | fixed, not calibrated | the stationary bootstrap's max-T at family-wise 0.05 (section 8) | decides no level (8) |
| value bar | the least a pass must be worth | fixed | $500 a year at C2's bound | `u_value_map.csv` `bar`; E-008 |
| valuation | where a lift is priced | fixed rule | section 10: `p14` for 50 and 100 ticks, `p16` for 150; caps at the records count and the reachable uses (or the records cap alone, E-032 (2)); one priority order shared with stage D's routing | `u_value_map.csv`; V1 |
| the 50-tick scaling ρ | the value of a smaller bet | fixed rule | ρ (section 10), an approximation of unknown sign; ρ squared and 1 beside | V2 |
| ticket size in stage D | the micros a ticket carries | fixed | the engine's `_plain_size` at the pick's stop: the allowance, the Combine's room cap, the 45-tick floor | P-14's configuration; S1; 6.3 |
| realised risk in stage D | floor (ii) | a build check | at least 0.9 of the allowance- and room-capped intention, P-14's form | E-022 (1); S1 |
| stage D bound level | the shift of both streams | fixed | the one-sided 0.05 bound, both streams | U1's verdict arm (`scripts/user_journey.py`); CHARTER section 2 |
| stage D base, routing, seed | the floors and the scorecards | fixed | section 11; campaign seed 20261935, 500 paths | E-008; E-022 (2); D-3 |
| hours | when tickets rest | fixed | 08:30 CT to the cutoff | E-003 (b) |

### 6.2 Dropped, and why

- **`break` at `on` and `pd`** (6 cells, 2 kinds x 3 stops; the first read's F1, option (c)).
  - *Why it cannot be judged here.* A break at either kind is, by construction, a breakout of a long window. Stage 2
    found the follow effect up to 60-minute breakouts on this window (D-555), closed the window to re-tests of it
    (D-592), and its judged-block sign is known (D-580, D-588). `pd`'s break was read at the market on this window by
    A1 to A4, and `pdhl` was not an A4 survivor.
  - *Why not a placebo at the day's own extreme moved outward.* It is level-adjacent (where stops cluster), fills only
    once a breakout has run on, and needs an unsourced offset.
  - *Why not keeping the cells but reading a pass as a lead.* That would spend this family's one judgement, and perhaps
    a confirmation purchase, on D-592's lead.
  - *What stays.* `fade` at `on` and `pd` stays.
- **`break` at `pdc`** (3 cells, 1 kind x 3 stops; the final read's G1, option (a), the lead's ruling).
  - *Why it cannot be identified here.* The real ticket's distance from `P_ref` is the overnight move's size |g|, and a
    ticket's fill probability falls with its distance. So the level's fills sit on days of smaller overnight moves than
    any placebo's.
  - *What that does.* An overnight effect whose strength depends on the move's size -- small moves revert, large ones
    continue -- gives L and D both positive with no level effect (the final read's synthetic check). The sign-only
    T-14 (e) cannot see it.
  - *Why no placebo can fix it.* Matching the distance would put the placebo on the level itself.
  - *What stays.* `fade` at `pdc` stays, judged on its trades, with no level claim (9.7).
- **`or30` and every other opening range:** inside Stage 2's closed branch (D-281 (3)); the safe default (E-007 (b)).
- **Frozen session-VWAP bands, prior swing points:** each a search of its own, so a later family.
- **R = 2 and 2.5:** a small minority of the table's recorded trading leaf-days in every phase of both bases
  (`records_leaf`), with barriers nested between R = 1.5 and 3 on the same fills. **R = 0.25** (D-526's menu) is not a
  leaf R of either $50K table.
- **Round-number spacings other than 100; other publish times; re-published tickets:** one of each, fixed.
- **The breakeven stop move:** it would add a third outcome, and its modelling defects are open (E-012 (2), Q-20). It
  stays in the bases' own trades in stage D, as registered (E-013 (2)).
- **Time stops** (D-212); **other sessions** (E-003 (b)); **F-01's 15:10 walk end** (`DECLARED_F01`); **the
  signal-service distribution** (E-007 (c)).

### 6.3 The 12.5-point stop, the stop band and the size a ticket carries (A, MINOR 2; F3; S1)

**D-527, read for what it says.** F-01 left the 12.5-point stop out because "it loses to costs (D-527)". D-527 (3) says
that at the 12.5-point rung "costs are a larger share of the risk: the all-day, Asia and London cells clear the line
far below P-14, and the US-hours cell is killed" -- a coin re-entering through a window, judged by its campaign. This
family's pass line is a lift in win probability over the coin twin, which carries no cost (both trades of a pair pay the
same one). So **the 12.5-point stop is admitted as a cell.** K5 catches its weakness on one-minute bars.

**The stop band, by its source.** `vendor/stage2/results/stop_band.csv` (D-201 (2)) gives the band for the three states
of stage one's family. Its narrow edge is the larger of the size-cap stop (ceil(risk / (cap x $0.50))) and the
cost-drag stop (`cost_drag_floor_ticks`, 45 MNQ ticks: the stop at which costs reach a tenth of it; D-271 (3)'s
stand-aside floor, which D-272 replaced with this per-state band).

| state (stage one's family) | risk | cap | narrow edge | 50 ticks | 100 ticks | 150 ticks |
|---|---|---|---|---|---|---|
| Combine | $1,500 | 37 micros | 82 ticks | outside | inside | inside |
| funded below +$2,000 | $1,000 | 15 micros | 134 ticks | outside | outside | inside |
| funded at or above +$2,000 | $300 | 37 micros | 45 ticks | inside | inside | inside |

D-201 (2)'s card rule (more than 25 % of stops outside the band fails contract fit) is a Stage 2 card rule. This family
has no card, so it is reported beside: the share of stage D's tickets in states where their stop is outside the band.

**The size a ticket carries: the engine's own sizing (S1).** A ticket is sized exactly as the base's own trade at that
stop in that state: by `propedge/campaign/sizing.py` `_plain_size`, under P-14's configuration
(`vendor/stage2/config/fv3_corrected_portfolio.yaml`, the sizing block). That is:
- the state's dollar risk in whole micros at the pick's stop, under the allowance (`allowance`: a Combine limit of 50
  micros, and funded 20, 30 and 50 micros by balance from 0, $1,500 and $2,000; `u_value_map.csv` identity
  `d667_sizing_50k`);
- **never more than the room above the floor on a Combine** (`room_cap: [combine]`, D-313);
- standing aside below the 45-tick cost floor (`stand_aside`, no share rule);
- the fee re-priced at the contracts (D-324).

The intention it is measured against is the engine's `capped_intention` -- the allowance-capped and room-capped
intended risk. The engine's need-aware Combine exits and consistency-cap exits (`fidelity`: D-303 to D-313) act on
tickets merged into the base's day log as they act on the base's trades: P-14's convention. So in stage D a ticket is
walked at every R of the base's carried menu (the quarter-R grid to 3), the pick's R being the one the routing asks.

**Why that form (E-022 (1)).**
1. It is the form R\* = P-14 was registered under (`prereg/P-14_a3-brk30-cb20.md`, line 36 -- "the allowance and the
   Combine's room cap applied" -- and line 427). A ticket at a base's stop in a base state realises exactly what the
   base's own trade there realises.
2. Under D-212 (1)'s letter, with D-272's stand-aside, the funded opening disappears. Its leaves are $1,500 and $2,000
   at 3R on the 20-micro step, carrying at most $500, $1,000 and $1,500 at 50, 100 and 150 ticks. So almost no 3R
   leaf-day is sizeable at any stop. (This is contract arithmetic on `records_leaf`, confirmed by the third read's
   `leaf_agg.py`.)
3. D-212's purpose -- consistent risk -- holds: with one stop per design, a ticket's size in a given state is fixed.

**What that does to a 50-tick pick.** It is a smaller bet than the leaf wherever the allowance or the room binds:
- a quarter of a $2,000 funded-opening leaf (20 micros x $25);
- at most five eighths of the Combine's $2,000 leaf (50 micros x $25, less where the room is smaller).

Section 10 prices it at that size, approximately (V2).

**Floor (ii) becomes a check.** Under this form, `intended_capped = realised exactly` (P-14's configuration, its
`contracts` line). Only whole-micro rounding near a Combine's floor can leave a trade below 0.9 of its intention. So
floor (ii) is a **check of the build** (T-15) and a figure reported beside, not a floor that decides (11.1).

## 7. Stage A: the gates, before any outcome

Read on the **choice block only**, per (cell, R), from fill, void and touch counts and the barrier kinds, pooled over
each rule trade and its mirror. The pooled reading is symmetric under a reflection of the price path, so it shows how
far prices travelled, never which way. No lift is computed.

1. **KB, the build's synthetic tests, before anything is read** (17.5, 17.6), each consequence recorded in the
   `build` section:
   - T-14 (c) and (e) kill `break` at an `rn100` stop, or withdraw the fade's level claim there, as 17.6 declares;
   - T-13 (b) sets each (side rule, stop, R)'s bookings, and kills a (cell, R) at the ladder's end (5.5).
2. **The cutoff rule and K2, resolution (D-8; N5).** A (cell, R)'s cutoff is the latest of 14:30, 14:00, 13:30, ...,
   10:00 CT such that, over its fills before it, the pooled unresolved share at **its own R** is at most 5 %, **overall
   and in each calendar year 2020 to 2023**. The share is counted with each trade walked by its own fill-bar rule
   (5.6); pooled over rule and mirror it stays reflection-symmetric. With no such time the (cell, R) is killed (K2).
3. **K1, supply:** at least 100 fills on the choice block after its cutoff, and at least 12 in each calendar year.
4. **K5, ambiguity (D-1).** A (cell, R) whose share of ambiguous pairs among its choice-block fills (after its cutoff,
   under symmetric booking) exceeds 5 % cannot be measured on one-minute bars, and is killed. The share by year is
   reported.
5. **K3, realised risk (D-9):** not applicable in stages A to C (a stop exit books S ticks plus a tick of cost). Its
   stage-D form is 6.3's check.
6. **A cell** with every R killed is killed.
7. **K4, fill realism: reported, decides nothing.**
   - For `fade`: fills over touches, a micro-rejection rate (mechanism-relevant, though it reads no lift).
   - For `break`: the share of gap fills.
   - For both: the share of fills in the first five minutes after 08:30, and on fill bars spanning a quarter of the
     stop.

   K4's outcome part (touched-but-unfilled fades) is computed with stages B and C, beside (D-10).
8. **The valuation's inputs, from contract arithmetic and direction-free counts** (section 10):
   - σ, ρ and the records caps, from `records_leaf`, `place_values` and D-667's sizing;
   - **the reachable uses** -- one heavy, direction-free count from the base's campaign on the choice block's days,
     read through `extended/reader.py` on those days only, or not used at all (10; V1; E-032 (2));
   - φ, the cell's filled ticket-days over its placed ticket-days.

   The placebo cells' counts and K5 shares are read here too.
9. **Planning (D-4), from counts only, written before stage B reads anything.** For every surviving (cell, R):
   - its choice-block fills;
   - its judged-block fills, **estimated** as the choice-block rate per session times the judged block's sessions;
   - the minimum detectable lift at the family's level with 80 % power, from Q-16's power tables for `cons`
     (`docs/research/calibration_2026-11-15.md`, section 4: Table 4a on the real coin nulls and Table 4b on the real
     persist1 nulls, both thinned to N trades).
     - **The column.** It is read at the family's k where tabulated (11 or 15), and otherwise at the **k = 15 column**,
       which is conservative for k = 12 to 14 (M4).
     - **The row.** It is read at the largest tabulated N at or below the cell's estimated judged fills. Below the
       smallest tabulated N (200) it is written "**above the 200-trade entry**", with no figure.
     - It is the larger of the two tables' entries.
     - It is in win probability; the net R figure is beside where the table gives it.
     - **Its null, stated beside each figure.** The tables' real nulls are P-16's 150-tick pairs, at win1 and net3. The
       cells are at R = 1, 1.5 and 3 and at 50, 100 and 150 ticks, so each figure is labelled with the null's R and
       stop.
   - for `break`, the same for D, from Table 11 (section 6.2: C1' with placebo fills five times the level's), the larger
     of its "shared" and "indep" sides rows, under the same column and row rules;
   - the tables as Q-55's clean rerun of the calibration writes them (E-035 (4)). No figure of Q-16 is cited before that
     rerun, or typed here;
   - the value bar in points at the cell's capped uses (10), and the ratio of the two.

   Every figure goes to the `planning` section; none is typed anywhere. R-16 is not adopted, and is not applied.
10. **K0, `cons`'s size on the cell's own fill counts** (E-052 (1); the pass-line review's M1). Outcome-free, after K1,
    K2 and K5, for every surviving (cell, R).
    - **Its counts:** the (cell, R)'s fills per session on the choice block's calendar after its cutoff, in date order
      -- every trading day the store holds from 2020-01-02 to 2023-12-29. Counts only.
    - **Its null:** Q-16's `cluster` null: each fill 0.5 sign(a_s + e), a_s ~ N(0, 0.35) the session effect, e ~
      N(0, 0.65) -- an exact null with sides reset daily.
    - **Its replications:** 200,000. Each one lays a window of n_judged consecutive sessions of those counts at a random
      circular offset, where n_judged is the judged calendar's session count Q-83 writes (9.1). It then draws the
      outcomes and applies `cons` at one-sided **0.05/132** (`lift_bound.many_levels`).
    - **The rule:** if the rate's 95 % Clopper-Pearson interval (`lift_bound.clopper_pearson`) lies **wholly above
      0.05/132**, the (cell, R) is **killed before stage B**, and counted.
    - **For a `break` cell** the same check runs on the treated two-sample `cons` (C1''s form): the level fills and the
      placebo fills are laid at the same offset and share a_s, and a wholly-above interval kills the cell too.
    - **Seeds:** `numpy.random.default_rng([20262020, c, r])` for C1's form and `[20262021, c, r]` for C1''s, with c
      the cell's index in table order and r its R's (15).
    - **Cost:** light. It reads counts only.
    - **What it is: a check conditional on the cell's realised choice-block counts.** It sizes `cons` on the one count
      path the cell actually has -- not on its profile.
      - For a profile whose unconditional size is well above the level, some realised paths are killed and others
        kept, each correctly by its own conditional size (family B's drafter's diagnosis, E-052).
      - **A kept cell says its own counts are safe, never that its profile is.**
    - **Why it costs no power where the size holds:** a (cell, R) whose size on its counts is at or below nominal is
      killed only when the 95 % interval lies wholly above nominal -- a chance of at most 2.5 % at nominal, and far less
      below it. Its level and power at the family's level were shown on synthetic toys before the pin (E-051's rule):
      `docs/research/scripts/q84/k0c0_toys.py`, seeds 20262024 and 20262025. Its figures are in Q-84's hand-back,
      regenerated by that script, and none is typed here.

Every cell killed: the family closes at stage A.

## 8. Stage B: choose on the choice block

For every surviving (cell, R), on the choice block:

1. **The statistics.**
   - The lift L under its C1 booking (5.5, 5.6).
   - For `break`, also **D = L - L_placebo**: L_placebo is the mean of w over all fills of the five placebo replicates.
   - The lift under its C2 booking.
2. **The bootstrap.** A stationary bootstrap (Politis and Romano) of the choice block's sessions in date order,
   circular, mean block 21 sessions, **2,000 replicates, seed 20261930**.
   - Each replicate is one draw of session indices, shared by every statistic and by the placebo fills.
   - A replicate's lift is the resampled sessions' summed w over their summed fills (D likewise).
   - The standard error is the replicates' sd. t = L / se, and a centred replicate is t\*_b = (L\*_b - L) / se, each
     replicate normalised by the sample's se rather than its own (not a studentised bootstrap, N4).
3. **The decisive statistic** T(c, R): for `fade`, t_L; for `break`, the smaller of t_L and t_D (and the same for each
   replicate). The first read's synthetic check (`iut.py`) found this inside 0.05 for a break cell with D at zero,
   provided break and fade at a kind survive stage A together. They share their pairs and pooled gates. A T-13 (b)
   switch can give them different bookings, but the two stay almost perfectly negatively correlated (the third read,
   section 4).
4. **The family-wise critical value** q: the 95th percentile over replicates of the maximum of T\* over every surviving
   (cell, R) -- one-sided, family-wise 0.05. Benjamini-Hochberg at 10 % is reported beside and never selects.
5. **Eligibility (F5; N5).** A (cell, R) above q is eligible only if its **rule-side** trades at its R on the choice
   block, each walked by its own fill-bar rule, leave at most 5 % unresolved, overall and in each calendar year 2020 to
   2023.
6. **Kill B.** No eligible (cell, R) above q: the family closes, and the judged block is not read.
7. **The pick.** The eligible (cell, R) with the largest **valued lift** (section 10, on its capped uses) at the
   lower limit of its C2-booked lift, L_C2 - q x se_C2.
   - A tie (equal to the dollar) goes to more choice-block fills, then to the first in table order (5.1, 5.2, stops
     ascending, R ascending).
   - There is one pick.

Stage B is a gate, not a claim (D_protocol N-1): it spends nothing of the program's budget.

**Stage B's bootstrap is not calibrated, and is kept as the choice block's selection device only.** Q-16 calibrated
the pass line's statistics, not stage B's stationary bootstrap or its max-T gate. Q-16 found a studentised block
bootstrap on 21-session blocks as lax as `t21w`, or more, on dense persistent nulls (the note's section 7.1, Table 3),
so q may be too small. That decides no level:
- **The program's error rate.** It rests on C1 at the family's level, by `cons`, on a judged block that played no part
  in the choice. A pick chosen through a lax gate is still judged by a calibrated test.
- **What a lax q costs.** At most the one judgement, spent on a pick chosen with less evidence than q implies. A
  conservative q costs closes at B.

Calibrating it would take Q-16's form applied to this family's own choice-block pairs: the pair terms' signs flipped
by blocks of sessions (persistence 1 to 63 sessions), the max-T's family-wise rejection rate read at 0.05 over enough
replications to bound it, and q replaced by a calibrated table if it fails. That reads the choice block's outcomes, so
it could run only inside stage B. It is not done.

## 9. Stage C: judge the pick on the judged block (the pass line, E-008)

The pick alone, with its cutoff and every rule as fixed in stages A and B, on fills from 2024-01-02 to 2026-07-16.
**C0 to C4 must all hold; any failure closes the family.**

0. **C0, `cons`'s size on the pick's own judged counts** (E-052 (1)), **before any x is computed.**
   - **When.** Inside `stage_C_judgement`, the pick's judged fills are first counted per session of the judged
     calendar. The counts come from the fill rule alone; no pair term is computed.
   - **The check:** K0's (7.10), on those counts as they are (no offset), with 200,000 replications. Seeds:
     `default_rng([20262022, 0])`, and for a `break` pick also the two-sample form on the level's and the placebo's
     judged counts, `[20262023, 0]`.
   - **What it is:** like K0, a check conditional on the pick's **realised** judged counts. It is not a statement about
     their profile.
   - **The rule:** if the 95 % Clopper-Pearson interval lies wholly above 0.05/132, **no pass is claimed.** The family
     closes at C0. Its judged lift is still computed and reported beside, labelled "not a claim".
   - **The order:** C0's row is written to the result file before any x is computed, and the runner computes x only
     after it (17 item 11).
   - **Its level and power:** shown with K0's before the pin (7.10).
1. **C1, direction.** The pick's lift under its C1 booking (5.5) on the judged block has a one-sided lower bound at
   **0.05 / (k (k + 1))** (0.05 / 132 at k = 11) **above zero**, by **`cons`** (E-035 (1)).
   - **The call:** `extended.lift_bound.bound(SHIPPED, x, session, n_sessions, level=...)`, with `SHIPPED = "cons"`.
     The module is the one merged in Q-16's commits 2f5ffd0 and 3a7a3f5 (master bb3d913), whose git blob is
     **`984f3467a4a05aa790d3ea43e94ac7761f0725b2`** (N1). The pinning row records it, and the run asserts
     `git rev-parse HEAD:extended/lift_bound.py` equals it before stage C, refusing otherwise.
   - **The estimate:** the per-fill mean of the pair terms x = w (5.6), every fill of the pick in the judged block,
     ambiguous pairs as zero.
   - **The calendar (N2; E-052 (3)):** every trading day the bar store holds from 2024-01-02 to 2026-07-16, void for
     this family or not, in date order. Its count, n_sessions, and the sha256 of its newline-joined dates are the ones
     Q-83 writes and the pinning row cites. The runner asserts both (17 item 12) and writes them to the result file. The
     fills are summed per session of that calendar, every session counted with or without a fill (`session_sums`).
     Blocks are cut by `block_index` (session j in block floor(j G / n), G = n // b), so the block edges follow that
     count.
   - **The bound:** the trade-weighted session-cluster t (CR1) on 21-, 42- and 63-session blocks of that calendar,
     each with df = the non-empty blocks - 1. C1 holds only if **all three** bounds are above zero; `cons`'s bound is
     their minimum.
   - **No draws:** `cons` draws nothing, so no seed. 20261933, once reserved for it, serves D-663's readings (15).
   - **The null class (E-035 (6); the calibration note, section 7.4 item 1).** A ticket's side is set each day at
     `t_pub` from that day's levels, and there is no multi-session regime filter. So the family's sides persist at most
     one session, inside the class Q-16 calibrated against (sides persisting up to a quarter).
   - **The fill intensity (E-052 (1); the pass-line review's M1).** This is stated beside the side's persistence, and
     the expected class is persistent:
     - Resting orders at price levels fill when the price travels to them, so a cell's fills per session rise in
       volatile stretches and fall in quiet ones. Its fill intensity can persist across sessions for weeks to months --
       the regime-like class of the review's count-persistent nulls (a log-intensity AR(1) near 0.98, a busy quarter).
     - That is outside the class Q-16 calibrated, whose counts are iid or uniform thinnings.
     - So `cons`'s size is checked on each cell's own counts and on the pick's, outcome-free (K0, 7.10; C0, 9.0).
   - **The residual (R1, a reading).** What sizes the test is the dependence of the pair terms w, not the rule's daily
     reset. A momentum or reversal regime gives w a mean that persists as long as the regime. Q-16's real nulls (P-16's
     long-minus-short pairs, flipped by blocks of up to 63 sessions) do not model that, and `cons` was lax on the stress
     regimes. This is stated beside the verdict, with the readings of 9.6 that bound it.
2. **C1', the level beyond a matched crossing (`break` picks, at `rn100` only; D-2, D-592, P1, G1).**
   - **The line.** The placebo-differenced lift D on the judged block has its lower bound at the same level above zero,
     by `cons` in its two-sample form (E-035 (2)): `extended.lift_bound.two_sample_bound(x_level, s_level, x_placebo,
     s_placebo, n_sessions, level=...)`.
     - Sample 1 is the pick's level fills; sample 2 is the placebo fills of the five replicates.
     - Each sample is summed per session of the same judged calendar.
     - All three block lengths are required.
   - **The estimate.** D = sum(S1) / n_level - sum(S2) / n_placebo -- the difference of the two per-fill means -- where
     **n_level and n_placebo are the judged block's fill totals** (F2).
   - **The variance (corrected, the calibration note section 1.3).** It is cluster-robust on the same session blocks,
     from the **count-centred residual block sums**,
     u_g = (BS1_g - D1 BN1_g) / n_level - (BS2_g - D2 BN2_g) / n_placebo.
     - BS and BN are a block's sums of w and its fill counts; D1 and D2 are the two per-fill means.
     - The previous version's raw per-session sums z_s gave the right D but the wrong variance, because they carry each
       session's fill count.
   - **The block count.** CR1's factor and the df use the **treated-cluster** count, Gt = the blocks occupied by the
     sample that occupies fewer, with df = Gt - 1 (`DIFF_DF_RULE = "treated"`). Q-16 found the first form, which counted
     every block, lax for persistent selections; it is kept on record (the note's section 6.1).
   - **Why it costs nothing.** It is an intersection with C1 at the same level, so there is no extra spend.
   - **What it identifies** (corrected, G1).
     - At `rn100` the placebo matches the real tickets by construction: the same day, one ticket above and one below,
       with distances exchangeable with the level's (arithmetic modulo 100 points, which no feature of the path sets).
     - `rn100` is not a range extreme.
     - The prior close, where the placebo cannot match the overnight move's size, has no `break` cell (6.2).
     - What D still cannot separate is any effect specific to crossing a price the market traded at earlier. That is
       what T-14 (c) (look-back) bounds, with T-14 (e) (overnight sign) as a check of the construction, each with a kill
       (17.6).
   - **What a C1-only pass means.** A break pick passing C1 but not C1' is recorded as a lead for unread data -- D-592's
     follow effect or S3's overnight-move effect seen again -- not a finding.
   - **What Q-16 calibrated, and what it did not.** It calibrated C1' as a two-sample statistic on real fills, with
     placebo fills five times the level's (the note's Tables 10 and 10b, section 6.2). It did not calibrate the
     placebo's construction -- its source days and its scaling (section 7.4 item 10) -- which is this family's T-14 (b),
     (c) and (e) (17.6).
3. **C2, value (F4, T2, V1).** The valued lift (section 10, on its capped uses) at the lower bound -- at the same
   level, by `cons` -- of the pick's lift **under its C2 booking** (rung 1, or rung 2 where 5.5 moves it) is at least
   **$500 a year**. Q-16 did not calibrate the value-map price at the bound (the note's section 7.4 item 10); it is a
   conjunctive gate on a calibrated bound, not a claim.
4. **C3, resolution (a floor, E-008; N5).** On the judged block, the pick's rule-side trades at its R, each walked by
   its own fill-bar rule, leave at most 5 % unresolved, overall and in every calendar year (2024, 2025, and 2026 to
   07-16). A calendar year with fewer than 63 sessions in a window is pooled with the adjacent year (D-604).
5. **C4, measurability.** K5 on the judged block: the ambiguous share is at most 5 %. It guards measurability, not an
   error rate, and can close a true effect for a direction-free reason.
6. **Beside, deciding nothing:**
   - **the pick's year-by-year readings** (E-031 (2), in place of the dropped reverse walk-forward): for each calendar
     year of each block, the pick's lift, its net R lift, its fills, its unresolved share, its K5 share and, for a break
     pick, D. Each lift has its `cons` bound at one-sided 0.05 on that year's own calendar of sessions (`bound`, or
     `two_sample_bound` for D). On a one-year calendar `cons`'s 63-session member has about four blocks, so these
     readings have much less power than C1 (the note's section 7.4 item 2) and decide nothing. No draws;
   - the seeded coin twin (20261931);
   - the net R lift;
   - drift: the lifts on long-rule and short-rule fills, and their mean, the side-balanced lift;
   - C1's lift under the other bookings;
   - the booking ladder: for `break`, symmetric booking at 2 and 4 ticks of slippage; for both side rules, rungs 2 and
     4 (5.5);
   - Benjamini-Hochberg;
   - K4's adverse selection;
   - the share of fills in the first five minutes after 08:30;
   - the placebo-differenced lift for a `fade` pick;
   - C2 at ρ squared and at ρ = 1 for a 50-tick pick (10);
   - **λ on first fills (N3):** the lift, and C2, on each day's first fill of the kind only -- the fill stage D's
     one-cancels-other spends;
   - **the regime readings (R1),** from stage B's own choice-block read, with nothing new spent: the pick's lift by
     quarter of the choice block, and the lag-1 correlation of its 21-session and of its 63-session block lifts.
7. **What a `fade` pass means (F10).** A fade pick passing C1 to C4 is **a reversal after these crossings**, carried on
   its trades as E-008 judges designs.
   - **A level claim is made only at `rn100`**, and only if the placebo-differenced lift beside it also clears C1's
     level and 17.6 has not withdrawn the claim.
   - **At `pdc` no level claim is made (G1).** The side-matched placebo removes the overnight move's sign but not its
     size, and a size-dependent overnight effect -- small moves continue, large ones revert -- would give the fade a
     level lift where none exists. The placebo-differenced lift is reported beside as a reading.
   - **At `on` and `pd` no level claim is made either.** The placebo matches neither the window broken nor the overnight
     path (the same confound as G1). The known follow effect works against a fade pass there.

## 10. The valued lift (F3, F8, V1, V2)

The value map's own first-order formula (`vendor/stage2/results/u_value_map.csv`, definitions `extra_win_prob_points`
and `mean_dv`), with each place's uses capped by what the routing can actually reach.

- **The base.** `p14` for 50- and 100-tick stops (P-14's rungs), `p16` for 150 ticks.
- **The places that ask R, and σ.**

  | place | phase | R it can price | σ(p, R) |
  |---|---|---|---|
  | (b) the evaluation | `combine` | any R | the share of the phase's recorded trading leaf-days whose leaf R is the cell's R (`records_leaf`) |
  | (c) the funded opening | `funded` | R = 3 only | 1 (the table's opening ask, handoff 2.5) |
  | (d) funded later | `funded` | R = 1 and 1.5 | over the whole funded phase, the opening's days in the denominator |
  | (e) paid | `paid` | any R | as for (b) |

- **The value of a use at the pick's stop:** v(p) = `mean_dv(p)` x ρ(p).
  - **Why ρ.** The vendored map gives no per-rung `dv`: `dv` is "averaged over the rungs" (definitions).
  - **`p16` at 150 ticks:** one rung, so ρ = 1, exact.
  - **`p14` at 100 ticks:** ρ = 1, about exact. The rung average is mostly the 100-tick rung, which trades "from 17:00
    to the 12:00 hour" while the 50-tick rung trades only "at 13:00 and 14:00" (P-14's registration, lines 197-198).
  - **`p14` at 50 ticks:** ρ(p) = the sum over the place's R-asking leaf-days of the 50-tick ticket's realised risk,
    over the same sum at 100 ticks, each sized as 6.3 sizes it.
  - **ρ is an approximation of unknown sign (V2).** The map's `dv` is the solver's value after a win less after a loss
    (definitions `dv`), and is not proportional to risk. Whether ρ errs high or low depends on the value function's
    curvature, so C2 is read at ρ, with **ρ squared and 1** beside (9.6). A per-rung `dv` would settle it; it needs
    D-667's solver (19).
- **What a place can take: the reachable uses (V1).** cap(p, R) is the smaller of:
  - **(i) the records count** -- `trades_per_year_records(p)` x σ(p, R). This is the count "its router, budget and
    one-position-at-a-time rule limit", not the table model's forward count, which the previous version used
    (definitions; the third read's V1);
  - **(ii) the reachable count** -- φ x the yearly count, per path-year, of the base's campaign path-days on which, at
    08:30 CT, **place p is the highest-priority place** (below) with an account that:
    - asks R;
    - **has not traded that session**;
    - sits in a firm that holds no position and closed none in the last five minutes.

    It is counted once in stage A (7.8), from the base's registered engine call with its day table **restricted to the
    choice block's days**, the base's trades read through `extended/reader.py` on those days only (E-032 (2)): counts
    only, no outcome of the tickets, and T-3 covers it.
  - **The fallback (E-032 (2)).** If Stage 2's builders cannot restrict the base's trades to the choice block's days
    without opening the judged part of their files, the reachable count is not used, and cap(p, R) is the records cap
    (i) alone. No purpose is created for it, and the `valuation` section says which cap applied. The fallback prices
    uses the base's own trades may take first, most at the funded opening (the third read's V1), so C2 then errs high
    there; stage D's realised take-up is reported beside it (11.6).
  - **φ** is the cell's choice-block filled ticket-days over its placed ticket-days. A ticket-day is a day the kind
    publishes a ticket not void at `t_live`; it is filled when at least one of the kind's tickets fills by the cutoff.

  At the funded opening, (ii) keeps only the openings no base entry reached before 08:30: most of them go to the base's
  own overnight trades first.
- **Uses.** u is the cell's filled ticket-days a year: a day with both levels filled counts once, since a ticket is
  never an account's second trade of a session (11.2).
- **The priority order.** Places ordered by v(p), highest first; u is allocated in that order, u_p = min(u - the uses
  already allocated, cap(p, R)).
- **The value:** $ a year = λ x the sum over p of u_p x v(p) / 100, with λ the lift in points at the bound in question.
  Stage D routes each ticket by the same order and the same reach rule (11.2), so the value is priced on uses the
  campaign can reach. Its realised take-up is reported beside (11.6).
- **How it is read.** First-order, with the table held fixed. It is a ranking and a bar, never a forecast -- "unreliable
  far from zero" (handoff 2.7; D_protocol N-4).

## 11. Stage D: the campaign -- E-008's floors, and the scorecards beside

Stage D runs whenever stage C has been read.
- **When C1 to C4 hold,** its floors decide.
- **When the family closed at C,** the floors decide nothing, and stage D gives only the scorecards beside the close
  (E-008). Such a run reads the judged block's start days for a closed design, so a later family lists it as prior
  exposure.
- **A close at A or B** reads no judged block and has no stage D.

### 11.1 Its role, and the floors

The long-run gate is read on stage D's own design, never taken as met by the base's registered PASS (E-022 (2)). **The
floors can close the family; nothing here can carry it.**

- **(i) The gate:** growth on the required bankroll at the bound **above zero** (Stage 2 D-145), at the fresh seed, with
  both streams at the one-sided 0.05 bound (11.4).
- **(ii) Realised risk** -- a **build check**, not a deciding floor (6.3, S1): at least 90 % of the tickets' trades
  realise at least 0.9 of the engine's `capped_intention`, which under the engine's sizing fails only by rounding. It is
  checked in T-15 and reported.
- **(iii)** Every rule is verified.
- **(iv)** Conduct tier 1 is true of the routing (11.3).

### 11.2 The design

**The base, by the pick's stop:**
- **50- and 100-tick picks: P-14** (A3-BRK30-CB20, with its schedule, table and five Topstep $50K seats; the
  no-closure table; at most 20 purchases in 21 sessions);
- **150-tick picks: P-16** (`rc_s150_all_nr`).

The base's own trades, walk, coin, cuts and table are unchanged. The pick's tickets are added as follows.

- **Published and placed.** A ticket is published at 08:25 on every day its kind has one (5.1; voids as 4.5). At
  08:30 it is placed on one account: the first, in the router's order, in the highest-priority place of section 10
  with an account that asks the pick's R, **has not traded that session**, and sits in a firm that is flat and not
  within five minutes of a close. With no such account, there is no ticket that day (counted).
- **A busy firm at 08:30.** If the firm is in a position, or within five minutes of a close, the ticket is placed once
  the firm has been flat five minutes, on an account meeting the same conditions, void if already through. This is a
  use the valuation does not count (10), so it errs low.
- **Reserved.** The account is reserved while the ticket rests: the base routes no offer to it.
- **Cancel on entry.** Before any base entry on another account, the resting ticket is cancelled. It is re-placed five
  minutes after that trade's exit, on the reserved account if it still has not traded that session, void if already
  through, and never after the cutoff.
- **A fill.** A ticket's fill takes the firm's one position; the base's offers are refused until five minutes after its
  exit (D-429). **That is the account's one trade of the session.**
- **No second trade (V1).** A ticket is never an account's second trade of a session. The two tickets of a kind are
  one-cancels-other: the first fill cancels the other for the day.
- **Size.** The engine's own sizing at the pick's stop (6.3): `_plain_size`, the allowance, the Combine's room cap, the
  45-tick floor. The engine's need-aware and consistency-cap exits act on Combine tickets as on the base's trades.
- **Releases inside the resting window (the final read's M5).** A resting ticket whose size is its account's **full
  allowance** -- for instance a 50-tick Combine ticket on a $2,000 leaf, capped at 50 micros -- is handled this way:
  - it is **cancelled five minutes before** each EIA crude oil or natural gas inventories release on its day
    (`vendor/stage2/config/im2_release_calendar.csv`, `EIAC` and `EIAG` rows, their `time_ct`);
  - it is **re-placed five minutes after** the release, void if already through, and never after the cutoff;
  - a ticket that filled before the window walks on (13613539's own rule for positions opened before a window, E-034).

  Tickets below the full allowance rest through. The screen (stages A to C) counts every fill; the share of the pick's
  fills inside these windows is reported beside. USDA crop production is not modelled (12 item 8). The base's own
  trades keep E-034's decision.

### 11.3 Conduct

Every step is realisable by hand. The firm never holds two positions, so never opposite positions across accounts
(tier 1). Each ticket rests on one account (D-157).

### 11.4 The bound level, and the tickets' verdict arm (M5)

**One level for both streams: the one-sided 0.05 bound** -- the charter's verdict arm, and the level U1's verdict arm
reads ("every R at the 0.05 bound the design's gate read", `scripts/user_journey.py`).

- **The tickets.**
  - Which trades: the pick's own rule-side trades at every R of the base's carried menu, walked as in 5.4 (each by its
    own fill-bar rule for its outcome).
  - Which block: each block separately, by Student-t on 21-session block means -- U1's form, so the tickets are shifted
    as R\* is read. Q-16 found that form (`t21e`) lax at the family levels, and it is untested at 0.05, so a lax shift
    makes floor (i) easier to pass; stated, not changed (N7).
  - Which era rule: **the lower of the two blocks' bounds**, R by R (D-271 (1)'s rule, without its test).
- **The base.** Its trades are shifted at the 0.05 bound exactly as U1's verdict arm shifts them -- not at its
  registered 0.05/N development line, which only the identity reproduces (11.5).
- **How.** Each stream is shifted by lb - e (`propedge.campaign.gate.shifted_blocks`), and the two are merged into one
  day log.

### 11.5 The runs

1. **The identity first, refusing (T-15).** With no tickets the runner must reproduce:
   - the base's registered gate paths (P-14: `vendor/stage2/results/a3_brk30_cb20_gate_paths.csv`; P-16:
     `rc_s150_all_gate_paths.csv`), at their registered level, on E-002's columns and tolerance;
   - U1's start rows (`results/user_journey.csv` section `start`, at its 0.05 verdict arm, E-010 (2)'s comparison).

   Its reads go through `extended/reader.py` under the purpose `identity` and the build's identity row (E-026; Q-48).
   A failed identity stops the family.
2. **The gate.** Stage 2's `gate` call as the base registered it -- rotation, its horizon, 500 paths, **campaign seed
   20261935**, 0 % denial, the placement off -- with both streams at the 0.05 bound. Floor (i) is read here.
3. **Beside, each reported and never a line** (the template's section 5):
   - the base alone at the same seed and level (the paired difference);
   - P-06's row;
   - **the denial ladder:** the same campaign at 10, 25 and 50 % denial;
   - **the break-even denial:** `propedge.campaign.portfolio.break_even_denial(fees, payouts)` on the design's campaign
     at the bound -- one minus fees over payouts, the share of payouts the firm could deny before the gain is gone;
   - **the placement on:** tier 2's patterns of section 3 modelled (D-289), with the share of the pick's tickets at full
     allowance and the campaign's share of days with several accounts at the MLL;
   - **the zero-edge twin:** the same gate call at the same seed with every R of both streams shifted to a zero mean,
     each stream by its own e (Stage 2's `scripts/portfolio_stage.zero_edge_blocks`). It reports the twin's growth on
     the required bankroll, and the design's point growth less the twin's (`signal_lift_over_zero_edge_twin`, the form
     of `propedge/reporting/scoreboard.py`);
   - **the tickets' e and its bound for each R** of the base's carried menu: e the mean net R of the pick's rule-side
     trades, per block and pooled; its one-sided 95 % bound as 11.4 computes the shift;
   - **stage one's D-47 criterion** (propsim D-47: e at least 0.10 and its bound at least 0.05) at the pick's R: met or
     not;
   - D-212 (1)'s letter share;
   - floor (ii)'s check;
   - the share of tickets outside the stop band.
4. **D-663's validation readings** (EXPLORATORY, deciding nothing; the template's section 4). They run on stage D's
   design -- base plus tickets, both streams at the 0.05 bound -- through `extended/v1_adapter.py`, after the gate,
   heavy, under the run lock:
   - **A0, the days' dependence:** the design's day series of summed net R at the fresh Combine's R, its absolute value
     and its sign -- autocorrelations at lags 1 to 21, Ljung-Box at lags 5, 10 and 21, a runs test on the sign, and the
     automatic block length (`V.ACF_LAGS`, `V.LB_LAGS`). No draws.
   - **A1, block-resampled days:** the gate with each path's calendar from the stationary bootstrap of days at mean
     blocks of **1, 5, 21 and 63 sessions** (`V.MEAN_BLOCKS`; mean block 1 the control). It runs 500 paths, campaign
     seed 20261935, growth on the required bankroll at the 0.05 bound and the point. Each run's Monte-Carlo error is
     drawn with **`mc_seed = 20261933`** (`v1_adapter.Engine`).
   - **B1, the bound's coverage:** the tickets' and the base's bound of e on block-resampled histories. The stationary
     bootstrap runs at mean blocks of **1, 5 and 21 sessions** and the automatic length, with **200,000 replicates** and
     5 verification draws (`V.B1_BLOCKS`, `V.B1_REPS`, `V.B1_VERIFY`). Coverage is read at one-sided **0.05** and at the
     family's **0.05 / 132**, with **`part_b1(seed = 20261934)`**.
   - **B2, the break-even e:** each R's outcomes stepped down by **0.02 R**, up to **8 steps**, under the independent
     draw and at mean block **21** (`V.B2_STEP`, `V.B2_MAX_STEPS`, `V.B2_MEAN_BLOCK`), at campaign seed 20261935. The
     reading is the step at which growth at the bound reaches zero, and its margin below the bound.
   - **C1, missed trades:** the arms drop **10 %** and **25 %** of offered trades and miss **10 %** of sessions
     (`V.C1_ARMS`), with **3 realisations** an arm (`V.C1_REALISATIONS`), each R's e and bound as in 11.4, and
     **`part_c1(seed = 20261936)`** -- each realisation's seed
     `v1_adapter.c1_seed(20261936, subject, arm, realisation)`.
   - **Slippage, D-583's families** (`v1_adapter.part_slip`): **(A)** stop slip 2, 3, 5, 8 and 12 ticks, the flatten one
     more; **(B)** entry and stop slip 2, 3 and 5 ticks, targets at zero. Each arm's e and bound is re-read on the
     stressed trades by each stream's own bound rule, at campaign seed 20261935. The reading per family is the lowest
     level at which growth at the bound is at or below zero.
   - **Not run: A2 and B3.** Their seeds are D-663's own (`V.SEED_A2`, `V.SEED_B3`), fixed in the vendored code and not
     adapted by `v1_adapter`, so they could not be this family's. They are recorded as not computed.

### 11.6 What stays unidentified (D-3)

1. **The base still occupies the firm** after 08:30, so tickets are cancelled on its entries. The take-up is reported:
   placed, filled, cancelled on entry, voided at re-place, refused for no reachable account; and the realised uses
   against section 10's cap -- the reachable count, or under E-032 (2)'s fallback the records cap, which errs high at
   the funded opening.
2. **The reservation changes the base's routing** even when no ticket fills.
3. **For a 150-tick pick,** the comparison with R\* = P-14 mixes the base's own distance from P-14 with the tickets; the
   paired difference against its own base is read beside.
4. **The judged block has few independent starts** (E-007 (2), red team M2). Every P comparison is calibrated and
   beside.
5. **The value map is first-order,** with the table fixed and ρ of unknown sign (V2).

## 12. The journey scorecard -- beside every judgement, never the pass line (CHARTER section 2; E-008, E-014, E-015)

**What it is computed from.** Stage D's real-order replay over start days (the U1 form,
`vendor/stage2/docs/USER_MILESTONES.md`), on the verdict arm at the 0.05 bound (11.4), for three designs:
- **base plus tickets**;
- **the base alone**;
- **R\* = P-14**, as U1 reads it.

Each is read on all starts and on the judged block's starts (from 2024-01-02, with the reading's horizon left). The
scorecard is computed whenever stage C has been read, pass or close. After a close at A or B there is no judgement and
no scorecard, and the closing row says so.

1. **The scorecard:** P, and S1 to S5c, S2, S3d, S6 and Q as USER_MILESTONES defines them; the frontier on P, S1, S3a
   and S5a.
2. **The journey's variables (E-014):**
   - sessions and cash to the first pass;
   - sessions and cash to the first payout;
   - **sessions to break-even** (the first session at which cumulative net cash is at or above zero, daily), the share
     reaching it by months 1, 2, 3, 6 and 12, and the share that later falls back below zero;
   - **the path's evenness:** the share of months with a positive net change, the longest run of months without a
     payout, the spread of monthly net, the deepest fall of cumulative net from its running high after break-even,
     payouts per month, and the largest single month's share of the year's payouts.
3. **Each measure as a distribution over start days** -- median, p10, p90 -- with its uncertainty from the effective
   number of independent starts, and the start day's share of the variance (design against luck, S6's form).
4. **E-007 (e)'s readings** (Q-17's adapter):
   - the denial ladder (10, 25, 50 %);
   - the placement on;
   - the binding Focused Trader models;
   - P by month;
   - mean net;
   - CVaR10;
   - P under a bankroll limit;
   - the effective sample size;
   - the minimum detectable difference, before the read.
5. **The paired differences** -- base plus tickets less the base, and base plus tickets less R\* -- by Q-16's
   calibrated P comparison, `extended/p_bound`'s `pcons` (E-035 (3)), one-sided at 0.05; reported, never a line.
   - `pcons` carries only where `bm63`, `obm126` and `ft63` all carry, its limit their minimum. It holds its level and
     has almost no power on this judged block.
   - `bm63c` is reported beside once its critical-value table comes from a clean run and is pinned (E-035 (3)).
   - `pcons`'s fixed-b critical values are simulated with the module's own seed (Q-16's 20261919). The family's
     20261936, reserved for it, is reassigned to D-663's C1 (11.5 item 4).
   - D-621 (3)'s percentile bound is not computed (E-007 (1)).
6. **Limits:** E-015's limits, **once approved by the operator**, as **menu flags only**. A design crossing one is shown
   with which limit and by how much; a limit never fails a design.
   - Only limits approved **before stage D's run** flag the menu.
   - A limit approved later flags it only in a reading labelled exploratory.
   - With none approved by then, the menu is read without flags, and says so.
7. **The evenness trade-off curve** -- how much "ahead" each step of evenness costs -- beside, with this design's point
   and its base's, in the form E-015's menu reading fixes.
8. **Not modelled, and said so wherever this scorecard appears:**
   - a user who stops when their own money runs out;
   - the user's time;
   - taxes;
   - E-034's unstated rules: which releases count as "scheduled major news", and whether holding through one counts;
   - USDA crop production inside the tickets' resting window (8284211), which no vendored calendar dates (11.2);
   - the base's full-size trades held through an unnamed release (E-034's decision).

The replay draws nothing.

## 13. What a pass and a fail mean

- **CARRIED** (C0 to C4, C1' for a break pick, and stage D's floors all hold). The pick is a development finding on a
  late-development block. It takes a registration id (D-621 (9)'s house form), a model card, its registered development
  test, the auditor, and then **one confirmation** (section 14), which carries the decision (D-189).
  - **A break pass** is a direction at round numbers, beyond what a crossing matched on its side and an exchangeable
    distance carries.
  - **A fade pass** is a reversal after these crossings (9.7).
- **CLOSED** at stage A (K0 among its kills), B, C (C0, C1, C1', C2, C3 or C4) or D (a floor). The reason goes in a
  decision row.
  - A close at B or C is recorded as **"no lift detectable at this power"**, with the planning section's MDL (or
    "above the 200-trade entry") at this family's level -- never as "no lift at levels" (D-4, M4).
  - A close at C carries stage D's scorecards beside it, and makes the judged block's start days prior exposure for
    later families.
  - The failure protocol applies where a check failed rather than a kill line.
  - The closure binds this specification (D-277's boundary): a later family on these levels names this closure, states
    what changed and why it is a different hypothesis (D_protocol 1.5 (c)), and is judged on data this family did not
    read.
- **`break` at `on`, `pd` and `pdc`** was not tested here (6.2). It belongs in its own declaration, on unread data.

## 14. The confirmation (M1, D-6), declared before any development read

- **The window.** NQ from 2026-07-17 (`config/windows.yaml`, `reserve`, `reserved`): not on disk, never read until a
  carried candidate is registered. The reader refuses it outright (`ConfirmationWindowRefused`), so its read belongs to
  the registration, never to this file.
  - It becomes NQ's **fourth** confirmation window only by the operator's decision (D-107; P-05, P-06 and P-10 spent
    the three).
  - It is a purchase (the operator's; `docs/OPERATOR_SETUP.md`, waited for).
  - Stage 2's draft P-16 confirmation targets the same window (`vendor/stage2/prereg/DRAFT_P16_confirmation.md`). If any
    test reads it first, the lead records that before registration, and the operator decides whether it can still
    confirm this pick.
- **What it tests: the pick's trades, not P.**
  - **The line.** The pick's lift over its coin twin on the window's fills (every rule, booking and cutoff as fixed in
    stages A and B), one-sided at the registered **0.05**, by `cons` on the window's own calendar of sessions, with the
    bound at 0.05/N beside (D-189's form). D for a break pick is read by `two_sample_bound`.
  - **A break pick** is also confirmed by its placebo-differenced lift, built exactly as 5.8 builds it -- on the target
    day's own sides, distances scaled or not by kind, sources past-only (development days included) -- with generators
    `default_rng([20261932, j, k, 2])`.
  - **C2 at the 95 % bound,** under its C2 booking, on its capped uses (10): at least $500 a year.
  - **Resolution:** at most 5 % overall, and in every calendar year with at least 63 of the window's sessions (a stub
    year pooled with its neighbour, D-604).
  - **K5:** at most 5 % on the window.
- **The family template's Combine-headroom check (F3) does not apply.** That check weighs the Combine's headroom over
  its target against the window's bound for a campaign confirmed on its growth (D-451 (3)). This confirmation tests the
  pick's lift over its coin twin on the window's fills, so no campaign's growth, and no Combine headroom, is confirmed.
- **What it cannot test: P.** A six-month window holds one 63-start block, on which no interval on P exists (red team
  M1). The scorecard on the window is descriptive, without an interval, and never a line.
- **How much data.** At least six months (D-604), and at least the number of months at which `cons`, one-sided at 0.05
  on a calendar of that many months, has 80 % power for a lift equal to the pick's judged lower bound at the family
  level.
  - **The fills assumed:** the lower of the pick's two blocks' rates per session x 21 sessions a month, by the thinning
    below.
  - **Why the length matters for `cons`.** On a short window its 63-session member has few blocks -- two on six months
    -- and its power falls fast (the note's section 7.4 item 2), so the length is read from `cons`'s own power at that
    length, not from Table 4.
  - **How the power is computed (fixed now, M6).** It uses the pick's judged-block session sums (S_j, N_j) from stage
    C's result file, with no new read of bars. For each candidate length of m months, 2,000 replications, each:
    - draws 21 m sessions with replacement from the judged calendar's sessions;
    - thins each drawn session's fills, every fill kept with probability (the lower of the two blocks' rates per
      session) / (the judged rate);
    - flips each session's sign by a fair coin;
    - adds the lift -- the pick's judged lower bound at the family level -- to every kept fill;
    - asks whether `cons` carries at one-sided 0.05 (`lift_bound.many_levels`).

    The power is the share that carry. Seed **20261937**: `default_rng([20261937, m])` for the session draws, the
    thinning and the signs, in that order. The same simulation at zero lift is reported beside, as a size reading.
  - **What it can move.** It runs after stage C, but it moves only the window's length, and so the purchase -- never the
    confirmation's level, which is fixed at 0.05.
  - **When.** It is computed when the pick is carried and written in the carrying row, before any confirmation data
    exists. If the length is more than the operator will buy, no confirmation is registered, and the pick stays a
    development finding.

## 15. Seeds, fixed now and checked

| seed | what it draws |
|---|---|
| 20261930 | stage B's stationary bootstrap (choice block) |
| 20261931 | the seeded coin twin beside (5.7) |
| 20261932 | the placebo's source draws: `numpy.random.default_rng([20261932, j, k, b])`, j the replicate (0..4), k the kind (0..3), b the block (0 choice, 1 judged, 2 confirmation) |
| 20261933 | D-663's A1, B2 and slippage readings (11.5 item 4): `v1_adapter.Engine(mc_seed = 20261933)`, each run's Monte-Carlo error. Reassigned before any use: it was reserved for stage C, where `cons` draws nothing |
| 20261934 | D-663's B1 (11.5 item 4): `v1_adapter.part_b1(seed = 20261934)`, its block-resampled histories. Reassigned before any use: it was reserved for the year-by-year readings, which draw nothing |
| 20261935 | stage D's campaign seed: the gate floor and every beside arm, 500 paths |
| 20261936 | D-663's C1 (11.5 item 4): `v1_adapter.part_c1(seed = 20261936)`, its missed-trade realisations. Reassigned before any use: it was reserved for the scorecard, where `pcons` uses `extended/p_bound`'s own seed |
| 20261937 | the confirmation's length rule (14): `default_rng([20261937, m])`, the sign flips of its power simulation at m months |
| 20261938 | the build's walker tests: `default_rng([20261938, j])` -- j = 0 the shift test, 1 T-3's synthetic judged block, 2 T-13 (b), 3 T-13 (c), 4 T-13 (a)'s extension (today's T-13 keeps its own 20261118) |
| 20261939 | the build's planted-effect tests, T-14: `default_rng([20261939, j])` -- j = 0 (a), 1 (b), 2 (c), 3 (e) gap follow, 4 (e) gap reversal |

**The second block, 20262020-20262029 (E-052; the block above being fully used):**

| seed | what it draws |
|---|---|
| 20262020 | K0's replications, C1's form (7.10): `default_rng([20262020, c, r])` per (cell, R) |
| 20262021 | K0's replications, C1''s two-sample form for `break` cells: `default_rng([20262021, c, r])` |
| 20262022 | C0's replications, C1's form (9.0): `default_rng([20262022, 0])` |
| 20262023 | C0's replications, C1''s form for a `break` pick: `default_rng([20262023, 0])` |
| 20262024 | the K0/C0 toys' count patterns (`docs/research/scripts/q84/k0c0_toys.py`): `default_rng([20262024, part, profile, pattern])` |
| 20262025 | the K0/C0 toys' outcome draws: `default_rng([20262025, part, profile, pattern, purpose])` |
| 20262026 to 20262029 | reserved for this family, unused; never assigned without a decision row |

On 2026-11-16 a word-bounded search of the working tree (the vendored snapshot included, binary files skipped) and a
`git grep` of every branch and remote found none of 20262020-20262029 before this text.

**The check (T-12; N9).** A word-bounded search of the whole working tree (`grep -rIow --exclude-dir=.git -E
"2026193[0-9]" .`, binary files skipped):
- On 2026-11-15 it found the range only in the Q-21 brief, as the proposal.
- The third read's search on 2026-11-16 found it also in `DECISIONS.md`, the two earlier reviews,
  `prereg/DRAFT_F-B_multifeature.md` and `prereg/DRAFT_F-P_payout_policy.md`. The last two reserve the range for F-02:
  they are references, not uses.
- The final read's search (2026-11-16) found it also in `prereg/DRAFT_F-O_opening_timing.md` and
  `prereg/DRAFT_F-R_resolution.md` (references reserving the range), and 20261930 as the exclusive bound of
  `extended/user_beside.py`'s `SEED_BLOCK = tuple(range(20261920, 20261930))` -- code, but not a use (N6).
- Without word bounds, the one other match is digits inside a floating-point value in
  `vendor/stage2/results/a3_brk30_cb20_gate_paths.csv`.

The build's T-12 must tell a reference from a use: a use is a seed passed to a generator in code, or declared as a
family's own in a `prereg/F-*.md` other than this one. An exclusive `range` bound is not a use.

**Inherited, and used only as their owners registered them:**
- the bases' seeds -- P-16's coin by date and minute 20261102, P-14's identity seed 20261131 and P-16's gate seed
  20261206 (E-002);
- Q-16's 20261910 to 20261919 and Q-17's 20261920 to 20261929.

**Not reused:** F-01's 20261901 to 20261903 (withdrawn, never run). 20261901 is also Stage 2's
`user_drivers.CLUSTER_SEED`.

## 16. Multiplicity and the budget

1. **F-01 spent k = 10** (E-007 (a)). **This family is program family number k = 11, at the level 0.05 / (11 x 12) =
   0.05 / 132** (the gatekeeper's count, E-045).
2. **One cell reaches judgement**, with no further division in the family.
   - C1' is an intersection with C1 at the same level.
   - C2 is a conjunctive gate, not a claim.
   - Stage B's family-wise test, on the choice block, spends nothing (D_protocol N-1).
3. **The program's honesty sentence (P-2).** Stage 2 ran programs S and U on this same window, each with its own 5 %.
   The development-stage level is a screening threshold; **the decision is carried by one confirmation on unread
   data** (D-189). A program ledger across both repositories (R-1) is not built; when it is, this family is listed in
   it.
4. **Counted:**
   - 15 cells, each counted whether killed or read;
   - 45 signed hypotheses, over 36 (kind, stop, R) questions;
   - 15 placebo cells, as controls;
   - one campaign cell if stage D runs;
   - the year-by-year readings re-read the pick, no new cell;
   - the 9 `break` cells at `on`, `pd` and `pdc`, dropped before any read, are not counted.

   A later D-189 N counts these, plus section 2's Stage 2 reads of the mechanism.
5. **D_protocol 1.5's holes:**
   - (a) There is no fitted model.
   - (b) No normaliser spans the sample: `A` trails 20 full sessions, placebo sources are past-only, the reachable count
     reads the choice block's days only, and T-3 checks the choice stages.
   - (c) This family re-declares F-01 after reviews, not after a read.
   - (d) Every judged-block read goes through `extended/reader.py` and its ledger, under a purpose named in 18.1
     (E-026).
   - (e) k, as above.
   - (f) The tests, section 17.

## 17. The build's identities and tests, before any reading

All of the family's code is committed after its pin (T-9). The tier of each test is stated. A failure of any test other
than T-13 (b) and T-14 (c) and (e) **stops the build**: the failure protocol applies, and no stage runs until a decision
row records the diagnosis. That is not a kill.

1. **The walker** (E-011: P-16's `TRADES_SHA256` under `STAGE2`) holds at the build's commit. The family's preset
   differs from `STAGE2` only in the breakeven move, and a test shows the preset with the move on is `STAGE2` exactly.
   (fast)
2. **E-002's and Q-05's identities** hold, and the run **refuses, never skips**, when their data are absent (T-11).
   (slow)
3. **No look-ahead** (D-5; F2). (fast)
   - **What is replaced:** every bar stamped at or after 08:25 on day E, and every bar of every later day.
   - **What must not move:** every level, side and `P_ref` on E, every `A_E`, and **every placebo ticket on E** -- its
     source, distance, price and side.
   - **How:** the replacements are a seeded walk (`[20261938, 0]`) and a constant, over days including roll days, DST
     changes, the seam, early closes and the days after them. Also asserted: no level is all-NaN or constant.
4. **Fill rules on synthetic bars**, under the family's preset (fast):
   - the void at `t_live`;
   - the gap through;
   - the trade-through;
   - one fill;
   - the cutoff;
   - every calendar void, read from the pinned files;
   - FOMC and report days, including an unscheduled statement after `t_pub`;
   - the pair rule under every booking, and each trade's own rule for resolution;
   - the `rule_fill` rungs for both side rules;
   - two levels a day;
   - break and fade exact negatives under symmetric booking, except on gaps and at the void boundary.
5. **T-13, the mirror's zero, per side rule, per stop (50, 100, 150 ticks) and per R, never pooled.**
   - **(a) Today's form, extended** (slow; seed `[20261938, 4]`; today's `tests/test_walker_t13.py` is unchanged).
     - *The walk, per stop S:* one tick a step, (S / 2)^2 steps a minute, so the one-minute sd is S / 2 ticks: 625,
       2,500 and 5,625 steps a minute at 50, 100 and 150 ticks. The 100-tick walk is today's (Appendix B's middle
       row), and the others are its rescaling.
     - *The tickets:* every five minutes from 08:30 to 13:25 CT; offsets uniform on S / 2 to 3 S / 2 ticks; cancelled at
       14:00; the family's preset; 9,000 days per stop (today's count; the walk's rescaling keeps its fill counts).
     - *The cells:* 2 side rules x 3 stops x 3 R = 18.
     - *The pass:* each cell's interval, clustered by day, is the mean +/- Z se with **Z = 2.991** (two-sided,
       Bonferroni over the 18 cells at a family-wise 95 %). `pair` with symmetric booking covers zero in every cell,
       with half-width under 0.0025 and at least 20 % of fill bars spanning the stop, else the test is refused, as
       today's is. `declared` with `rule_fill` stays the strict expected failure (E-010 (3)).
   - **(b) Spread and jumps** (slow; F4, T2; runs in the build before stage A; seed `[20261938, 2]`).
     - *The walk:*
       - bars stamped 08:30-15:09;
       - the mid moves one tick a step, 400 steps a minute;
       - with probability 0.002 a step it moves instead 2 to 8 ticks (uniform);
       - a one-tick bid-ask spread: the print at the ask (the mid plus half a tick) after an up-move, at the bid after a
         down-move.
     - *The tickets:* live every five minutes from 08:30 to 13:25 CT, cutoff 14:00; a level k ticks (uniform on 20 to
       60) above or below (a fair coin) the close of the bar before live; `break` as a stop and `fade` as a limit; the
       family's preset; 9,000 days per (side rule, stop).
     - *What it reads:* each booking's -- symmetric, rungs 1, 2 and 4 -- mean lift under this null per (side rule, stop,
       R), with its two-sided 95 % interval clustered by day, written to the `build` section. No multiplicity
       correction here, by design: a per-cell 95 % interval acts on a bias more readily, which is the conservative
       direction for a switch.
     - *What it decides:* 5.5's switches and kill, per (side rule, stop, R).
   - **(c) The precise form** (heavy, under the run lock; synthetic, CPU-bound, modest memory; seed `[20261938, 3]`):
     (a) held to a quarter of the smallest `extra_win_prob_points` in `u_value_map.csv`, section `bar`, at `target=500`.
     That needs about 3.5 million fills per (side rule, stop).
6. **T-14, planted effects** (seed 20261939; synthetic; (c) and (e) heavy, under the run lock).
   - **The generator (T1, fixed here), shared by (a) to (e):**
     - a continuous synthetic history of trading days;
     - each day's bars: the regular session, bars stamped 08:30-15:09; then 15:10-15:59; none from 16:00 to 16:59; the
       overnight session from 17:00 to 08:29;
     - the price moves one tick a step: 400 steps a minute in the regular session, 100 a minute otherwise;
     - it starts at 80,000 ticks (20,000 points), so `rn100`'s multiples fall every 400 ticks;
     - with no plant each step is up or down with probability one half;
     - `pd`, `on`, `pdc`, `rn100`, `A`, the placebo and every walk rule are exactly the family's, on these bars.
   - **The plants:**
     - **(a) a level effect:** at the first touch after 08:30 of each real level, for ten minutes each step goes up with
       probability 0.5 (1 + 0.004 d), d the touch's direction. 10,000 days.
     - **(b) a crossing effect:** the same, at every 5-minute breakout in the regular session (a minute whose high
       exceeds, or whose low undercuts, every price of the five minutes before it). 10,000 days.
     - **(c) a look-back-dependent follow effect (F1):** at each such breakout, with τ the minutes since the path last
       stood at the breakout's price before that minute (capped at 2,760; a price never visited takes the cap), for
       five minutes each step goes up with probability 0.5 (1 + κ d), κ = min(0.01, 0.002 ln(1 + τ / 5)). A newer
       breakout replaces the drift; a minute with both directions plants none. 40,000 days.
     - **(e) an overnight-sign effect (P1):** in the regular session every step goes up with probability
       0.5 (1 + κ sign(g)), g = `P_ref` less the prior close. κ = +0.002 is the gap-follow arm and -0.002 the
       gap-reversal arm; g = 0 plants nothing. 40,000 days per arm. With `break` at `pdc` dropped (G1), it checks
       `rn100`'s construction only.
   - **What each checks** -- at `rn100`'s `break` cells only, the one kind whose placebo decides; per stop, at R = 1:
     - **(a)** L's one-sided lower bound by `cons`, and D's by `two_sample_bound`, at the family's level on the
       synthetic calendar, are both above zero, in every one of the 3 cells.
     - **(b)** D's two-sided interval, clustered by day, covers zero in every one of the 3 cells, at **Z = 2.394**
       (Bonferroni over 3 cells, family-wise 95 %).
     - **(d)** a level read from the 08:25 bar is caught by test 3.
     - **(c) and (e)** -- 9 kill checks: (c), and (e)'s two arms, x 3 stops:
       - **the interval:** two-sided, clustered by day, at **Z = 2.773** (Bonferroni over the 9 checks). So under a
         correct placebo the chance that some cell is killed by chance is at most 5 % (N5);
       - **precision:** D's interval at that Z has a half-width of at most 1.0 point of win probability;
       - **visibility:** in (c), the break lift L's lower bound at that Z is above zero. (e) needs none at `rn100`: an
         overnight-sign drift moves the ticket above and the ticket below in opposite directions;
       - **if D's interval lies wholly above zero:** `break` at that (kind, stop) is **killed** (KB) -- the placebo
         would let a non-level effect pass C1' (N2);
       - **if it lies wholly below zero:** break is unaffected (conservative), but the placebo-differenced lift is
         **not used for a fade level claim** at that (kind, stop), where it would be anti-conservative;
       - **if the precision or the visibility fails:** the test is **refused** for that (kind, stop), not failed. Its
         break cells are withheld from stage A, recorded as "refused, not killed" and counted, and no fade level claim
         is made there.
   - **Failures of (a), (b) or (d)** stop the build. The seeds: `[20261939, 0]` (a), `[20261939, 1]` (b),
     `[20261939, 2]` (c), `[20261939, 3]` and `[20261939, 4]` (e)'s arms.
7. **T-3, choice-stage invariance** (slow). Stage A's and B's outputs must be byte-identical when **every judged row
   of every file stages A and B open** is replaced on temporary copies, never the store:
   - every bar from 2024-01-02 on, by a seeded synthetic walk (`[20261938, 1]`);
   - and, for the reachable count, the rows dated from 2024-01-02 of each walk and event file its engine call opens
     (for P-14, Stage 2's `data/atlas/A3/walks.parquet` and A1's `events.parquet` and `days.parquet`; for P-16, the
     inputs of its cell builder), poisoned (M2).

   The outputs compared: cutoffs, kills, planning, the valuation's inputs (the reachable count included), the critical
   value and the pick.

   Beside T-3, the reachable count's adapter reads only through the reader's choice-block window
   (`reader.read_walks(..., end="2023-12-29")`) and asserts that every row it consumes is dated at or before
   2023-12-29. Before stage A, the build records whether E-032 (2)'s fallback applies.
8. **T-15, stage D's routing** (slow).
   - With no tickets, the base's registered paths and U1's start rows (11.5).
   - Toy days for:
     - the priority order and the reach rule (an account that has traded that session is never chosen);
     - the reservation;
     - cancel-on-entry, and re-place at exit plus five minutes;
     - void at re-place;
     - one-cancels-other;
     - the cutoff;
     - the engine's `_plain_size` at the pick's stop, with the room cap binding;
     - floor (ii)'s check;
     - the need-aware exit acting on a Combine ticket.
   - The reachable count's adapter, if built (E-032 (2)), reproduces the base's registered paths when its day table
     is not restricted.
9. **Q-16's own size test** passes at the build's commit.
10. **T-12:** section 15's seeds are used nowhere else, telling references from uses.
11. **T-7's analogue:** stage C reads the pick from stage B's result file by its sha256, and its entry point cannot run
    stage B. It writes C0's row before computing any x (9.0).
12. **The stage-C runner's assertions** (E-052 (3); the pass-line review's m1 and m2). These are build checks: each
    refuses the run, and a test shows each refusing.
    - **The level:** `level = lift_bound.family_level(k)` with k = 11, asserted equal to `family_level(11)`, strictly
      inside (0, 0.5), and with k in `lift_bound.K_RANGE`. That one value is the level passed to `bound`,
      `two_sample_bound`, K0 and C0.
    - **The calendar:** `n_sessions` and the judged session list (the session dates in order) are asserted against the
      count and the sha256 Q-83 writes, which the pinning row cites. Each fill is mapped to its session's ordinal by the
      session date the walker assigns, never by its calendar date.

**Protocol items, not this family's to build:**
- T-1 (the program ledger);
- T-2 (the family-file lint);
- T-4 (the read ledger -- now `extended/reader.py`, E-026);
- T-5 (withdrawals);
- T-6 (Q-16's calibration);
- T-8 (append-only decisions);
- T-10 (results provenance).

## 18. Outputs, the reads and the run

### 18.1 The judged block's reads (E-026)

Every read of Stage 2's bars or walks goes through `extended/reader.py`. A read after 2023-12-29 needs a purpose this
file names on its one reads line below, inside a clean run of a committed tree, once per purpose (a repeat needs a row).
No purpose here contains a choosing or fitting word: choosing reads only the choice block.

- **Judged-block reads:** `stage_C_judgement`, `stage_D_gate_floor`, `stage_D_scorecard`

| purpose | what it reads, and why |
|---|---|
| `stage_C_judgement` | the pick's judged-block fills, its placebo and its walks: C1 to C4 and every stage-C reading beside, the pick's year-by-year readings included (9.6) |
| `stage_D_gate_floor` | the stage-D campaign over the development window: the engine's reads (`reader.authorise_engine_read`), and the tickets' walks at every R of the base's menu through `reader.read_bars` (N8); floor (i), the base alone and the arms beside (11.5). Each ledger line's `what` says which |
| `stage_D_scorecard` | the real-order replay over start days of the three designs (section 12) |

**Not on this line:**
- the identity reads (purpose `identity`, under the build's identity row, from `identity/*.py`; Q-48);
- stage A and B (the choice block only), and the reachable count, which is read on the choice block's days only or not
  used at all (10; E-032 (2));
- T-13 and T-14 (synthetic);
- the confirmation window, which the reader refuses outright and which belongs to a registration;
- the reverse walk-forward, dropped program-wide (E-031 (2), E-032 (1)): it would make the judged block a block that
  chooses.

### 18.2 Files and the run

- **Files.**
  - `results/rl2_levels.csv`, with sections `build`, `supply`, `cutoff`, `kill`, `planning`, `valuation`, `choice`,
    `judged`, `placebo` and `beside`;
  - `results/rl2_campaign.csv` (stage D: `identity`, `gate`, `beside`);
  - `results/rl2_journey.csv` (section 12).

  Each is written with its sidecar manifest through `extended.results.write_result`, carrying:
  - `prereg_id` the family's F-id;
  - the cell and hypothesis counts;
  - every seed and parameter;
  - the sha256 of `vendor/DATA_MANIFEST_stage2.sha256` and of `config/calendar_early_closes.csv` (E-029).

  They are EXPLORATORY until a carried candidate is registered. The reader's ledger (`results/read_ledger.jsonl`)
  records every judged read.
- **The run.** Once, from a clean checkout of a named commit (`scripts/run_clean.py`), under the run lock, watched to
  its end.
  - The order is fixed: the build's synthetic KB tests; stage A (K0 and the reachable count included, or its
    fallback); B; C (C0 first); then D. Each stage's file is written before the next reads anything.
  - A kill stops the sequence.
  - A run aborted or restarted is recorded by the lead with its log, and only the first complete run is read.
- **Waits.** The pin itself waits for Q-55's clean rerun reproducing `cons` holding and for Q-83's fresh-seed validation
  holding (status; M3; E-052 (2)); no judged-block read
  until this file is pinned (the reader refuses a draft). Q-05 holds (E-010) and Q-16 is merged (E-035). Before stage
  C, the run asserts `extended/lift_bound.py`'s blob `984f3467a4a05aa790d3ea43e94ac7761f0725b2` and before stage D
  `extended/p_bound.py`'s blob `f5b29710e243f97a2795e57f6458512fea99199b` (N1).

## 19. What the pin requires, and what stays open

**The lead's:**

1. **Q-55's clean rerun** of Q-16's calibration (E-035 (4)) must reproduce `cons` and the treated two-sample `cons`
   holding at the family's k, **and Q-83's fresh-seed validation must HOLD** on E-052's criterion (at every k in 11 to
   15, no real or realistic null's 95 % interval wholly above nominal), before the pin. If either does not, this text is
   withdrawn before any read (status; M3; E-052 (2)).
2. **The pinning row** names `extended/lift_bound.py`'s blob `984f3467a4a05aa790d3ea43e94ac7761f0725b2` and
   `extended/p_bound.py`'s `f5b29710e243f97a2795e57f6458512fea99199b` (N1), the pinned file `prereg/F-NN_<slug>.md` and
   its diff from this reviewed text (N9), and the judged session list's count and sha256 that Q-83 writes (E-052 (3)).
3. **The readings beside.** Q-17's adapter is needed for section 12 item 4, and E-015's approved limits for 12 item 6.
4. **Optional (V2):** a per-rung `dv` from D-667's solver would replace ρ.

**Decided since the fourth version was written, and applied here:**
- the calendar (E-029);
- the reverse walk-forward struck (E-031 (2), E-032 (1));
- the reachable count read on the choice block's days only, or not used and replaced by the records cap, with no new
  purpose (E-032 (2));
- the charter's record of the allowance-capped reading (E-032 (3));
- `break` at `pdc` dropped, with no fade level claim at `pdc` (the final read's G1, option (a), the lead's ruling);
- the final red-team read (Q-53) answered here.

**The operator's**, each with its safe default applied, none blocking:

1. `or30` and the opening ranges (D-281 (3)): out by default (E-007 (b)).
2. The confirmation: NQ's fourth (D-107), shared with P-16's draft; its length and its purchase.
3. The levels of E-015's limits (approval pending).

## 20. Anything chosen after seeing results

*(Empty at declaration. Anything added after a reading is exploratory, reported apart, `exploratory=True` in its
manifest, and recorded in its own decision row -- never in this file.)*
