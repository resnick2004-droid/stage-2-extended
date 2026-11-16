# DRAFT F-XX: resting orders at pre-session levels, corrected (family RL2) -- not declared

**Status: DRAFT, second version, of 2026-11-16 (TASK_QUEUE Q-30), redrafted on its red team's review
(`docs/reviews/DRAFT_F-02_resting_levels_2026-11-15.md`). Not pinned, not numbered, not declared.** It replaces F-01
(`prereg/F-01_resting_order_level_atlas.md`, withdrawn, its k = 10 spent, E-007 (a)). No bar has been read for it, no
level computed, no outcome of any order computed. It becomes a declaration only after the red team reads this version,
the prereg-gatekeeper approves it (assigning F-XX and k), and the lead pins its sha256 in a decision row.

**It cannot be pinned before Q-16 is merged:** its pass line is Q-16's calibrated statistic, whose choice is pending.
The marks **[Q-16]** are filled in a revised draft, with the merged statistic's name, module and commit, before the
gatekeeper reads it. The other items left open are listed in section 19, each to be closed before the pin. Anything
chosen after a reading is exploratory and reported apart.

| field | value |
|---|---|
| family | RL2: resting stop and limit orders at four pre-session price levels, judged on their trades first (E-008) |
| id | F-XX -- the gatekeeper's (F-02 if this is the next family pinned) |
| program family number k | the next free at the pin: **11 if pinned next** (F-01 spent 10, E-007 (a)) |
| level | one-sided **0.05 / (k (k + 1))**: 0.05 / 132 at k = 11 |
| development data | NQ 1-minute bars, 2020-01-02 to 2026-07-16 |
| choice block | fills from 2020-01-02 to 2023-12-29 |
| judged block | fills from 2024-01-02 to 2026-07-16 |
| confirmation | NQ from 2026-07-17 (`reserve`, reserved): NQ's fourth (Stage 2 D-107, the operator's decision), a purchase |
| confirmation tests already on NQ | three (P-05, P-06, P-10; `vendor/stage2/config/windows.yaml`) |
| cells (`k_cells`) | `fade` at 4 kinds + `break` at 2 kinds (`pdc`, `rn100`), x 3 stops = (4 + 2) x 3 = **18**, each counted whether killed or read |
| hypotheses | 18 cells x 3 R = **54** signed hypotheses over 36 (kind, stop, R) questions (section 5.9) |
| the pass statistic | the lift over the coin twin on the same fills, by Q-16's calibrated test **[Q-16]** |
| the value bar | $500 a year at that bound (`vendor/stage2/results/u_value_map.csv`, section `bar`, `target=500`) |
| seeds | 20261930 to 20261939, each assigned in section 15 |
| model card | none: no fitted model; the grid is the family |

---

## 0. What this corrects

### 0.1 The Phase 0 findings on F-01 (`docs/audits/phase0/D_protocol.md`, `docs/reviews/phase0_red_team_2026-11-15.md`)

| finding | F-01's defect | the correction | section |
|---|---|---|---|
| D-1 | the fill-bar rule biases break down and fade up | the pair rule (`fill_bar="pair"`); the ambiguous share read and capped (K5) | 5.5, 7.4, 9.5 |
| D-13 | the mirror booked at the rule's fill; fast-market overshoot | symmetric booking decides C1; the conservative `rule_fill` booking decides C2; a spread-and-jumps T-13 on the null | 5.5, 9, 17 |
| D-2 | `or30` in Stage 2's closed branch; line 23 false; break cells load on D-592's lead | `or30` out; line 23 corrected; prior exposure; `break` at range extremes dropped; C1' for the rest | 1, 2, 6.2, 9.2 |
| D-3 | stage D cannot identify the tickets' value | stage D keeps only E-008's floors and the scorecards beside; base by stop; tickets routed to the valued places; cancel and re-place | 10, 11, 12 |
| D-4 | the MDL is far above the value bar | the MDL from counts and Q-16's power curve before stage B; a close reads "no lift above the MDL" | 7.9, 13 |
| D-5 | a minute of look-ahead at 08:25; the side set at `t_live` | levels and sides from bars stamped at or before 08:24; the void rule at `t_live` | 4 |
| D-6, M1 | the confirmation is NQ's fourth and P-16's window; it cannot confirm P | declared so; it tests the pick's trades | 14 |
| D-7 | cells counted, hypotheses not | both counted | 5.9, 16 |
| D-8, D-9, D-10 | K2 at 10 %; K3 cannot fail; stage A read an outcome | 5 % every year; K3 recorded; K4's outcome part moved | 7 |
| D-11 | roll days, the seam, early closes; `rn100` | calendar voids from pinned calendars; `rn100` in the futures' own price | 4.5, 5.1 |
| D-12, D-14, D-15 | drift and placebo; the bootstrap and estimand; no parameter table | beside or decisive; stated; the table | 6, 8, 9.6 |
| A, MINOR 1 and 2 | D-212 / D-308 swapped; "the 12.5-point stop loses to costs (D-527)" | cited correctly; the stop admitted after re-reading D-527 | 3, 6.3 |
| M5, M7, N-2, N-3, M4 | the tickets' bound; k; seeds; the flatten; the signal service | declared; F-01 spent 10; new seeds; Stage 2's flatten; one user | 11.4, 15, 16, 5.4, 1 |

### 0.2 The red team on the first draft (`docs/reviews/DRAFT_F-02_resting_levels_2026-11-15.md`)

| finding | the defect | the correction | section |
|---|---|---|---|
| F1 (MAT) | C1' cannot separate `on` / `pd` breaks from Stage 2's breakout-follow effect | **option (c): `break` at `on` and `pd` dropped** (24 cells to 18); C1' kept where it identifies (`pdc`, `rn100`); T-14 (c), a planted follow effect that grows with the window broken, with a declared kill if it fails | 6.2, 9.2, 17.6 |
| F2 | the placebo read days after its own; outside the shift test; `n_level`, `n_placebo` undefined | past-only source days (at least 21 sessions back); placebo tickets inside the shift test; the n's are block fill totals | 5.8, 9.2, 17.3 |
| F3 | the stop band misquoted; floor (ii)'s form undeclared; `p14`'s rung-averaged `dv` | the band's per-state edges, from the file; floor (ii) in P-14's registered form, and what it does to a 50-tick pick; no per-rung `dv` is vendored, so a 50-tick pick's `dv` is scaled down, conservatively | 3, 6.3, 10, 11.1 |
| F4 | the deciding booking is symmetric about a bar-visible trigger | C2 read at `rule_fill` with 1 tick for every pick; a T-13 variant with a spread and jumps, declared now, which can switch C1 to `rule_fill` | 5.5, 9.3, 17.5 |
| F5 | the rule side's own resolution on 2020-2023 never a line | a pick-eligibility line in stage B, overall and every year | 8.5 |
| F6 | early closes found from the day's own bars | a pinned calendar of scheduled early closes and of data-defect days; no other day voided by its own bars | 4.5, 19 |
| F7 | stage D's bound level unstated; the streams mix levels | one level, the one-sided 0.05 bound, for both streams | 11.4, 11.5 |
| F8 | valued at the best place, spent at the first account | the valuation and the routing use one priority order of places | 10, 11.2 |
| F9 | prior exposure: S3's gap rules, A4's long windows, `pdhl` absent from A4's survivors | the three rows added | 2 |
| F10 | what a fade pass means | stated: a reversal after these crossings, carried on its trades; the level-specific part is the placebo-differenced lift, beside | 9.7, 13 |
| N1, N2 | K5 does not depend on R; K5 / C4 buy measurability, not an error rate | K5 read per (cell, R) after its own cutoff, the share per fill R-free; the 5 % labelled the drafter's choice; the estimand stated | 5.6, 7.4 |
| N3, N4 | a wrong cross-reference; the placebo's draw order and `A_D` on short days | fixed; the draw order specified | 0.1, 5.8 |
| N5 | T-13 at a quarter of the smallest bar is heavy | marked heavy, under the run lock | 17.5 |
| N6, N7, N9 | stage D after a close; K4's micro-rejection rate; the cutoff bound by R = 3 | listed as prior exposure for later families; "reported, decides nothing"; the cutoff per (cell, R) | 7.2, 7.7, 11, 13 |
| N8 | the feature-rules skill's column name | the lead's (corrected on master, 4cddf79); this file cites `ts` | 4.1 |

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
- **The cascade side (`break`)** is tested at the prior close and at round numbers only. At the two range-extreme kinds
  (the prior session's high and low; the overnight high and low) a break is also a breakout of a long window. Stage 2
  read the breakout-follow effect three times on this window and closed the window to it (D-592), and no placebo built
  here separates the two (the red team's F1). So `break` at `on` and `pd` is left to a test on unread data (section
  6.2).

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
fires, times what a win is worth where it is used (section 10). It is judged first on its trades (E-008), with the
user's journey reported beside (section 12).

## 2. Prior exposure: what has already read these bars, these levels and this mechanism

| read | what it read | span | what it recorded | bearing here |
|---|---|---|---|---|
| ORB1 to ORB6 (Stage 2 D-275, D-277, D-278, D-281) | the 08:30 opening-range breakout: a stop at the range's edge (skip, rest, chase), a limit retest | NQ development | the branch closed for good; whether a later hypothesis is "genuinely different is the operator's call" (D-281 (3)) | `or30`, and every opening range, is out (E-007 (b)) |
| atlas families A1 to A3 (D-460; `config/atlas_a1.yaml` to `a3.yaml`) | `pdhl` (the prior day's 08:30-15:10 CT high and low, the first close beyond) followed and faded, five bars late; `orb_rth5/15/30`, `orb_globex30`; P-13/P-14's `brk30` | 2020-01-01 to 2026-07-16 | P-14 (A3-BRK30-CB20) chosen from A3 | `pd`'s break and fade were read at the market; `pdhl` is defined on 08:30-15:10, this family's `pd` on the bars stamped 08:30-14:59 -- close, not identical |
| A4, the coin-benchmarked atlas (D-550, D-555, D-557, D-558) | 34 patterns at 25 and 37.5 points, delays 0 and 5, lift over the coin twin, follow and fade one test: `brk` at k = 5, 10, 15, 30, 60 and 90 minutes; `orb` at the 08:30, 17:00 and 02:00 opens (17:00 and 02:00 at m = 15, 30, 60); `pdhl` | 2020-01-01 to 2026-07-16 | survivors "short breakouts and n-bar runs on 5- and 10-minute bars, a few at 15 and 60 minutes", all on the follow side (D-555); **`pdhl` is not among the survivors' classes**; "a genuine but tiny direction effect", no campaign value (D-558) | the follow effect reaches 60-minute breakouts -- the evidence behind F1; `brk` at 60-90 minutes and the 17:00-open ranges are the nearest reads to `on`; `pdhl`'s own lift is in `results/a4_coin_atlas.csv`, not vendored |
| program S, S1 (D-578, D-580) | the side of recent breakouts and momentum followed and faded, on P-16's schedule | 2020-01-02 to 2026-07-16 | two follow rules (15-minute momentum, the latest 5-minute breakout) survive the lift test; both grow less than P-16 on 2020-2023 and more on 2024-2026, so the span guard rejects them | the follow effect's sign by era |
| program S, S3 (D-586, D-587, D-588, D-589) | 13 rules, among them `gap_glbx` (the session's first open against the previous trading day's last close at or before 16:00 CT) and `gap_rth` (the open after 08:30 against the same close), followed and faded against the coin twin | 2020-01-02 to 2026-07-16 | one survivor, `lnbar1x4_follow`; the Benjamini-Hochberg rejections "every one on the follow side and all but one on the breakout and n-bar rules" (D-588) | the prior close used as a reference: it bears on `pdc` |
| D-592 | S3's candidate at the five-minute latency | -- | fails; the follow effect "broad and slow rather than tied to the last bar"; "re-testing it on that window would reuse hypotheses already seen, so it is recorded as a lead for unread data" | `break` at range extremes dropped (6.2); C1' for the other breaks (9.2) |
| Stage 2's effect atlas (`config/effect_atlas.yaml`, H01 to H04, F01 to F02) | the overnight return's, and the previous close's location's, relation to the day's move | Stage 2's development | returns, not levels | named for completeness |
| program U, nine families (`results/u_budget.csv`, `u_resolve.csv`) | P on start days from 2024 | judged block of starts | all closed below P-14 | the judged block has been read for P nine times |
| P-05, P-06, P-10 (`config/windows.yaml`) | confirmation reads of 2025-07-01 to 2026-07-16 | that window | development since D-461: "a new NQ model may be built on it, never confirmed on it" | inside this family's judged block |
| this repository | F-01 (withdrawn before any read); its walker (E-010, E-011), which computed no level and no outcome but P-16's identity; this draft's red team (two synthetic scripts, no bar) | -- | -- | no read of these levels exists here |

**Not found as price levels.** No Stage 2 decision row or configuration reads the overnight high and low, the prior
close or round numbers as price levels. Searched: `vendor/stage2/DECISIONS.md` and `vendor/stage2/config/`, for
"prior close", "overnight", "round number", "prior day" and `pdhl`, 2026-11-15. The prior close was read as a
reference for a gap's side (S3).

**The drafter's own reads,** all vendored Stage 2 inputs, no bar: `results/u_value_map.csv`, sections `records_leaf`
and `identity` (the leaves' R, risk and balance band; the $50K sizing), to class R = 2 and 2.5 (6.2) and to check
what each sizing form does (6.3); and `results/stop_band.csv` (6.3).

**What follows.**
1. The judged block is late development, not out of sample (D_protocol P-3): a pass is a development finding whose
   evidence is its confirmation (section 14).
2. `or30` is out, and `break` at `on` and `pd` is dropped (6.2).
3. A `break` cell at `pdc` or `rn100` passes only if its lift also exceeds that of matched non-level crossings (9.2).
4. The reverse walk-forward and the lift by year are reported with every judgement (9.6).

## 3. Contract fit: the constraints each cell lives inside

| constraint | how the family meets it |
|---|---|
| latency at least 5 minutes (Stage 2 D-266) | every level and side from bars stamped at or before `t_pub - 1 min`; the order works from `t_live = t_pub + 5 min` (section 4) |
| one position per firm, 5 minutes flat (D-429) | stages A to C read every fill independently; stage D routes by the strict rule, with cancel-on-entry (11.2) |
| every trade resolving: at most 5 % to the flatten, overall, per market and per year, no time stops (D-212 (2) as D-308 (3) raised it) | the cutoff rule and K2 (7.2); the pick's rule side on 2020-2023 (8.5); C3 on the judged block (9.4) |
| realised risk matching intended (D-212 (1)) | cannot fail in the walk (K3, 7.5); in stage D, the form the bases are registered under: realised risk at least 0.9 of the allowance-capped intention (P-14's registration; 11.1, 6.3) |
| the sizeable stop band (`vendor/stage2/results/stop_band.csv`, D-201 (2)) | the narrow edge per state of stage one's family: 82 ticks in the Combine, 134 ticks funded below +$2,000, and 45 ticks funded at or above +$2,000, where the cost-drag floor binds (`cost_drag_floor_ticks`, the stop at which costs reach a tenth of it; D-271 (3)'s 45 MNQ ticks). 50 ticks is inside the band in the last state only, 100 ticks in the Combine and the last, 150 ticks in all three (6.3). The bases' $50K table sizes by its own allowance, which floor (ii) and section 10 use |
| news | tickets go live at 08:30 CT: on a BLS 08:30 ET release day strictly after 07:35:00 CT (E-007 (d)), and outside Topstep's Tier 1 windows (07:25-07:35 CT on CPI, NFP and PPI days; around both FOMC events; E-007 (6), `docs/audits/phase0/E_rules_currency.md` C1). FOMC days carry no tickets. Tickets rest through other 09:00 CT releases, as Stage 2's rule allows (D_protocol N-6) |
| conduct, tier 1 (D-145) | no hedge (cancel-on-entry: never two positions in the firm); no simulator-fill exploitation (stops of at least 50 ticks, no stop move); no maximum size into news (above); no copying (each ticket on one account, D-157); nothing concealed (a resting order at a public level) |
| conduct, tiers 2 and 3 | tier 2: the R = 1 cells meet "R at or below 1"; modelled off in the base case (D-289), on beside in stage D. Tier 3: priced at 0 % denial in the verdict, 10, 25 and 50 % beside; Terms of Use s.8 (outsized positions) priced among them (E-013 (1)) |
| hours | US regular hours: tickets live from 08:30 CT to their cutoff (at latest 14:30); the walk ends at the bar ending 15:08 CT |
| entry by hand | the user places the ticket between `t_pub` and `t_live`, or at 08:30:00 itself if the platform does not take an order that works only from 08:30; the fill window opens with the bar stamped 08:30 either way (E-008; the red team's section 5) |
| firm rules | only rules verified in `vendor/stage2/config/rules.yaml` or `config/rules_extended.yaml` |

## 4. Time, data and calendar (D-5, D-11, F6)

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
5. **Calendar voids, from calendars fixed before the run -- never from the day's own bars (F6).** Each is counted.
   - **(a) Scheduled early closes.** The dates on which CME Group's published holiday schedule closes NQ before
     15:00 CT, within the development window. They are compiled from the exchange's published calendars into a dated
     file pinned by sha256 under a decision row before this family's pin (section 19). Such a day voids every kind;
     the next trading day voids `pd` and `pdc`.
   - **(b) Data-defect days.** The purchase seam -- trading day 2025-06-30 (no trades) and 2025-07-01 (its first two
     hours missing; P-14 caveat C2) -- and any other day Stage 2's NQ data report lists as defective, in the same
     pinned file. Such a day voids every kind; the next trading day voids `pd` and `pdc`.
   - **(c) Roll days**, from the bar store's manifest `rolls`. The charted contract is chosen on the previous day's
     volume (README section 5), so a roll is known in advance. A roll day voids `pd` and `pdc`, whose prices would be
     the old contract's.
   - **(d) Edges.** The first trading day in the store voids `pd` and `pdc`. FOMC days carry no tickets.
   - **(e) Any other day whose bars end early** -- an unscheduled halt, or a gap not in (b) -- is **kept**. Its
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
| `break` | `pdc`, `rn100` | buy **stop** one tick above the level | sell **stop** one tick below | the first bar stamped at or after `t_live` trading at the stop's price; at that price plus one tick (`slip_ticks`, `vendor/stage2/config/atlas_a3.yaml`; D-95), or at the bar's open plus one tick when it opens beyond the stop |
| `fade` | `pd`, `on`, `pdc`, `rn100` | sell **limit** at the level | buy **limit** at the level | only when a bar stamped at or after `t_live` trades **through** the level by at least one tick; at the limit price, never better |

### 5.3 Per ticket

One ticket a level a day. It fills at most once and is never re-armed. Unfilled, it is cancelled at its (cell, R)'s
**cutoff** (7.2): it fills only on bars closing at or before the cutoff. When both levels of a kind fill on one day,
both fills count in stages A to C; stage D takes them by the strict rule.

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

### 5.5 The pair, the fill bar and the two bookings (D-1, D-13, F4)

For every fill, the **mirror** is the opposite side at the same fill bar, with the same stop, targets and walk. The
**trigger** is the first price the bars show at the fill condition: a stop's price on a touch, or the open on a gap; a
tick through a limit's price, or the open when a bar opens through it. **The fill bar is settled by the pair rule**
(`fill_bar="pair"`): if it touches either trade's stop or target, the pair is **ambiguous** -- both booked as stopped
losses (costed as stops), zero lift, counted (K5). Otherwise both are walked from the next bar, and the fill bar is not
read. Two bookings are computed, each settling its own pairs by the pair rule:

- **Symmetric** (`mirror_booking="symmetric"`): the mirror at 2 x trigger less the rule's fill, paying the rule's
  offset in its own direction.
  - It is side-neutral on a tick-continuous driftless walk (the four barriers lie symmetric about the trigger;
    `tests/test_walker_t13.py`).
  - It is not neutral against what one-minute bars cannot show: an overshoot past a stop's price in a fast market
    favours `break`; booking about a print at the offer rather than the mid favours `fade` (the red team's F4).
  - **It decides C1 and C1'**, unless the spread-and-jumps T-13 (17.5) switches a side rule to `rule_fill`.
- **`rule_fill` with 1 tick** (`mirror_booking="rule_fill"`, `slip_ticks=1`): the mirror at the rule's own fill price.
  It hands each mirror its rule's offset, so it is conservative for both side rules. For a break it also absorbs an
  overshoot of up to about a tick. **It decides C2**, for every pick.

### 5.6 The lift, and the estimand of every stage

- **The pair term:** w = 1/2 [win(rule) - win(mirror)], in win probability. A win is the target reached; a flatten or
  an ambiguous pair is not a win.
- **The lift:** lift(c, R) = **the mean of w over all the (cell, R)'s fills in a block** (D-14), ambiguous pairs
  included as zero. The net R lift, 1/2 [net R(rule) - net R(mirror)], is reported beside.
- **The estimand, plainly (N2).** The pair rule zeroes every fill whose fill bar reached a barrier -- under symmetric
  booking, a bar that ran S - 1 ticks or more from the trigger on either side, where a within-minute cascade would
  show. So the lift measures direction on fills whose fill minute stayed inside that band, diluted toward zero by the
  rest. K5 bounds the zeroed share at 5 %.
- **R-independence (N1).** For R of 1 or more, whether a fill is ambiguous does not depend on R (a target touch implies
  the other trade's stop touch).
- **Break and fade at `pdc` and `rn100` are near-exact negatives.** A buy stop a tick above a resistance and a sell
  limit at it fill on the same trigger. Under symmetric booking they form the same pair with the labels swapped, so
  their lifts differ only on gap fills and on a day the price at `t_live` stands exactly at the level (verified on
  synthetic days, the red team's `negation.py`). Under `rule_fill` both are handicapped and are no longer negatives.

### 5.7 The coin twin beside

A seeded coin twin -- one fair side per fill, in date order of the fills, cell by cell in table order, seed
**20261931** -- is computed beside. It decides nothing.

### 5.8 The placebo (decisive for `break` at `pdc` and `rn100`; beside for every `fade`)

The placebo measures the statistic at prices with no visible meaning. Its purpose is to separate the level's effect
from what any crossing carries (D_protocol 1.3 item 4). Every input comes from the past (F2).

- **`A_D`:** the mean, over the 20 most recent trading days before day D with a full regular session (not a scheduled
  early close, not a data-defect day, 4.5), of the regular session's range -- the high of its bars stamped 08:30-14:59
  less their low. It is roll-free: a range inside one day.
- **The source day, from the past only.** A placebo ticket on target day E copies the tickets of a **source day D drawn
  from the kind's eligible days at least 21 and at most 252 trading days before E**. Eligible means the kind is not
  calendar-void that day and `A_D` is defined. Every input -- D's level distances, `A_D`, `A_E`, and `P_ref` of E --
  then predates E's `t_pub`.
- **The placebo ticket.** Each of D's published tickets (distance d ticks from D's `P_ref`, side +1 for a resistance,
  -1 for a support) becomes a placebo ticket on E. It is placed at `P_ref` of E plus side x max(1, round(d x `A_E` /
  `A_D`)) ticks, with the same side rule, stop, R, `t_pub`, `t_live`, cutoff, void rule, walk and bookings.
- **Replicates and the draw order (N4).** There are five replicates, j = 0..4. Replicate j uses
  `numpy.random.default_rng([20261932, j])` and draws in this order:
  - kinds in table order (`pd`, `on`, `pdc`, `rn100`);
  - for each kind, every target day of the development window in date order (choice and judged blocks together, so a
    choice-block draw never depends on a judged-block day);
  - one draw per (kind, target day): `integers(len(pool))` over the source pool in date order.

  A target day with an empty pool (in the store's first weeks) carries no placebo, and is counted.
- **Coincidences.** A placebo price that happens to lie near a real level on E is kept. That moves the placebo toward
  the level's own lift, which is conservative for a pass.
- **Placebo cells.** There are 18 (one per cell). They are controls, not hypotheses. Their counts and K5 shares are read
  in stage A. At `on` and `pd` the placebo is not matched on the window broken (F1), so there it is a reading only.

### 5.9 Cells and hypotheses

- **Cells:** (4 `fade` kinds + 2 `break` kinds) x 3 stops = **18 cells**.
- **Hypotheses:** each cell is read at R = 1, 1.5 and 3, so **54 signed hypotheses**, over 36 (kind, stop, R)
  questions. At `pdc` and `rn100` both signs are asked; at `on` and `pd` only the fade sign.
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
| side rules | break or fade | searched | `fade` at all four kinds; `break` at `pdc` and `rn100` | F-01, less `break` at range extremes (F1; 6.2) |
| stops | the stop's distance from the fill | searched | 50, 100, 150 ticks (12.5, 25, 37.5 points) | P-14's two rungs and P-16's stop; 6.3 |
| R | target over stop | searched | 1, 1.5, 3 | the table's main asks (handoff 2.5; `u_value_map.csv` `records_leaf`); 6.2 |
| `t_pub`, `t_live` | publish and live times | fixed | 08:25 and 08:30 CT | D-266; the US open |
| `P_ref` | the price that sets each side | fixed | close of the last bar stamped at or before 08:24 | D-5 |
| void rule | an order already through at `t_live` is skipped | fixed | price at `t_live` = close of the bar stamped 08:29 | F-01; the walker's `price_at` |
| stop slippage | ticks paid on a stop entry | fixed | 1 tick; 2 and 4 beside | `atlas_a3.yaml` `slip_ticks`; D-95; D-13 |
| limit fill | when a limit fills | fixed | a trade through by at least 1 tick, at the limit's price | feature-rules 3 |
| target rounding; two-barrier bar | -- | fixed | floor(R x S); the stop first | Stage 2's `target_ticks`; feature-rules 3 |
| fill-bar settlement | the fill bar of a pair | fixed | the pair rule | E-010; D-1 |
| booking for C1 and C1' | the mirror's price in the pass line | fixed rule | symmetric, switched to `rule_fill` 1 tick for a side rule the spread-and-jumps T-13 finds biased toward it (17.5) | E-010; D-13; F4 |
| booking for C2 | the mirror's price in the value line | fixed | `rule_fill`, 1 tick, every pick | F4 |
| walk end and flatten | where an open trade is closed | fixed | the bar ending 15:08 CT; the worst of bars ending 15:08-15:10, less 2 ticks | Stage 2's convention (N-3) |
| costs | fees and ticks | fixed | Stage 2's at the stop; exit ticks 1 / 0 / 2 | E-010, E-011 |
| cutoff | when an unfilled ticket is cancelled | fixed rule, value read on the choice block | per (cell, R): the latest of 14:30, 14:00, ..., 10:00 CT passing 7.2 | F-01's rule; D-8; N9 |
| resolution ceiling | the most that may reach the flatten | fixed | 5 % overall and in every calendar year | D-212 (2) as D-308 (3) raised it |
| K1 supply | the fewest fills | fixed | 100 on the choice block and 12 in every calendar year of it | F-01; the value map's smallest use count |
| K5 ambiguity cap | the most fills the walk cannot settle | fixed | 5 % of fills | **the drafter's choice** (N2): it buys measurability, not an error rate; set at D-212's flatten ceiling by analogy only |
| calendar voids | days with no ticket | fixed | 4.5's lists | D-11; F6; P-14 caveats C2, C4 |
| `rn100` spacing | the round number | fixed | 100 points, in the futures' own price | F-01; D-11 |
| placebo | the control for `break` | fixed | 5 replicates; past-only sources, 21 to 252 trading days back; distance scaled by `A` (20 full sessions) | D_protocol 1.3 item 4; F2; the drafter's 21, 252, 20 and 5 |
| stage B bootstrap | the family-wise gate on the choice block | fixed | stationary, mean block 21 sessions, circular, 2,000 replicates, centred, studentised, seed 20261930 | D-14; D-550's form |
| stage C level and statistic | the pass line | fixed | one-sided 0.05 / (k (k + 1)), Q-16's statistic [Q-16] | E-008 |
| value bar | the least a pass must be worth | fixed | $500 a year at C2's bound | `u_value_map.csv` `bar`; E-008 |
| valuation | where a lift is priced | fixed rule | section 10: `p14` for 50 and 100 ticks, `p16` for 150; the places in one priority order shared with stage D's routing; a 50-tick `dv` scaled by the size it carries | `u_value_map.csv`; F3; F8 |
| realised risk in stage D | floor (ii)'s form | fixed | at least 0.9 of the allowance-capped intention, at the base's own sizing | P-14's registration (`prereg/P-14_a3-brk30-cb20.md`, line 427); 6.3 |
| stage D bound level | the shift of both streams | fixed | the one-sided 0.05 bound, both streams | U1's verdict arm (`scripts/user_journey.py`); CHARTER section 2; F7 |
| stage D base, routing, seed | the floors and the scorecards | fixed | section 11; campaign seed 20261935, 500 paths | E-008; D-3 |
| hours | when tickets rest | fixed | 08:30 CT to the cutoff | E-003 (b) |

### 6.2 Dropped, and why

- **`break` at `on` and `pd` (F1: option (c) of the three the red team offered; 6 cells, 2 kinds x 3 stops).**
  - *Why it cannot be judged here.* A break at either kind is a breakout of a long window, by construction: a new high
    since 17:00 the evening before, or beyond the whole prior regular session. Stage 2 found the follow effect up to
    60-minute breakouts on this window (D-555) and closed the window to re-tests of it (D-592), and its sign on the
    judged block is known (D-580, D-588). A pass is therefore what the known effect predicts. `pd`'s break was itself
    read at the market on this window, by A1 to A4, and `pdhl` was not an A4 survivor.
  - *Why not (b), a placebo at the same day's extreme moved outward.* That price sits just beyond a visible extreme,
    where stop orders cluster on Osler's own evidence, so it is itself level-adjacent. It fills only once a breakout has
    already run on, so it measures a later point of the same move. And its offset would be a new parameter with no
    source.
  - *Why not (a), keeping the cells but reading a pass as a lead.* That would spend this family's one judgement, and
    perhaps a confirmation purchase, on D-592's lead under this family's name. D-592's lead belongs in its own
    declaration, on unread data.
  - *What stays.* `fade` at `on` and `pd` stays: no read on this window predicts a fade pass there (the known effect
    works against it).
  - *A note on the count.* The red team wrote "24 cells to 20"; with three stops it is 18.
- **`or30` and every other opening range (5, 15, 60 minutes):** inside Stage 2's closed branch, whose reopening D-281
  (3) reserves to the operator; the safe default (E-007 (b)).
- **Frozen session-VWAP bands, prior swing points:** each needs its own window and multiplier or swing definition -- a
  search of its own, so a later family.
- **R = 2 and 2.5:** a small minority of the table's recorded trading leaf-days in every phase of both bases
  (`records_leaf`), with barriers nested between R = 1.5 and R = 3 on the same fills. **R = 0.25** (in Stage 2's
  offered menu, D-526) is not a leaf R of either $50K table.
- **Round-number spacings other than 100; other publish times; re-published tickets:** one of each, fixed.
- **The breakeven stop move:** it would add a third outcome, and its two modelling defects are open (E-012 (2), Q-20).
  It stays in the bases' own trades in stage D, as registered (E-013 (2)).
- **Time stops** (D-212); **other sessions** (E-003 (b)); **F-01's 15:10 walk end** (`DECLARED_F01`); **the
  signal-service distribution** (E-007 (c)).

### 6.3 The 12.5-point stop, the stop band and the size a ticket carries (A, MINOR 2; F3)

**D-527, read for what it says.** F-01 left the 12.5-point stop out because "it loses to costs (D-527)". D-527 (3) says
that at the 12.5-point rung "costs are a larger share of the risk: the all-day, Asia and London cells clear the line
far below P-14, and the US-hours cell is killed". That is about a coin re-entering when flat through a window, judged by
its campaign. This family's pass line is a lift in win probability over the coin twin, and that lift carries no cost:
both trades of a pair pay the same one. So **the 12.5-point stop is admitted as a cell.** Its known weakness is
resolution on one-minute bars, which K5 catches.

**The stop band, by its source.** `vendor/stage2/results/stop_band.csv` (D-201 (2)) gives the band for the three states
of stage one's family. Its narrow edge is the larger of two stops: the size-cap stop, ceil(risk / (cap x $0.50)); and
the cost-drag stop, `cost_drag_floor_ticks` -- 45 MNQ ticks, the stop at which costs reach a tenth of it, D-271 (3)'s
stand-aside floor, which D-272 replaced with this per-state band.

| state (stage one's family) | risk | cap | narrow edge | 50 ticks | 100 ticks | 150 ticks |
|---|---|---|---|---|---|---|
| Combine | $1,500 | 37 micros | 82 ticks | outside | inside | inside |
| funded below +$2,000 | $1,000 | 15 micros | 134 ticks | outside | outside | inside |
| funded at or above +$2,000 | $300 | 37 micros | 45 ticks | inside | inside | inside |

D-201 (2)'s card rule (a card fails contract fit with more than 25 % of its stops outside the band) is a Stage 2 card
rule. This family has no card, so it is reported beside, not applied: the share of stage D's tickets in states where
their stop is outside the band.

**What decides the size: the bases' own $50K table.** The table sizes by its allowance (D-667's $50K sizing,
`u_value_map.csv` identity `d667_sizing_50k`: "the $50K sizing's Combine limit (50 micros) and funded ladder (0: 20,
1,500: 30, 2,000: 50 micros)"; the funded opening is on the ladder's first step). A ticket at stop S in a state whose
leaf risks r is sized
min(floor(r / (S x $0.50)), allowance) micros -- **the size the base's own trade at that stop gets in that state.**

**Floor (ii)'s form: P-14's registered form** -- realised risk at least 0.9 of the allowance-capped intention
(`prereg/P-14_a3-brk30-cb20.md`, line 427). Three reasons:
1. It is the line R\* = P-14 and the bases are registered under. A ticket at a base's stop in a base state realises
   exactly what the base's own trade there realises, and should not be held to a stricter line than it.
2. Under D-212 (1)'s letter (at least 0.9 of the leaf's own risk) with D-272's stand-aside, the funded opening
   disappears. Its leaves are $1,500 and $2,000 at 3R on the 20-micro step, carrying at most $500, $1,000 and $1,500 at
   50, 100 and 150 ticks. So almost no 3R leaf-day is sizeable at any of the three stops, and the Combine's $2,000 1.5R
   leaf is not sizeable at 50 ticks (50 micros carry $1,250). (This is contract arithmetic on `records_leaf` and D-667's
   ladder, done by the drafter; no figure enters this file.) Every R = 3 hypothesis would then be uncarriable, and the
   charter's highest-value place unreachable -- a change of the program's premise that a family declaration should not
   make on its own.
3. D-212's purpose -- consistent risk, in the operator's words -- holds: with one stop per design, a ticket's realised
   risk in a given state is fixed.

The letter form's share is reported beside (section 19 names the choice for the lead).

**What that does to a 50-tick pick.** It carries less than the leaf wherever the allowance binds:
- a quarter of a $2,000 funded-opening leaf (20 micros x $25);
- five eighths of the Combine's $2,000 leaf (50 micros x $25).

It is a smaller bet than the table's leaf, and section 10 prices it at that smaller size.

## 7. Stage A: the gates, before any outcome

Read on the **choice block only**, per (cell, R), from fill, void and touch counts and the barrier kinds (target, stop,
flatten, ambiguous), **pooled over each rule trade and its mirror** under symmetric booking. The pooled reading is
symmetric under a reflection of the price path, so it shows how far prices travelled, never which way. No lift is
computed.

1. **K0, the build's synthetic kills, before anything is read** (17.6, 17.5):
   - if T-14 (c) fails at a kind, `break` at that kind is killed;
   - the spread-and-jumps T-13 sets each side rule's C1 booking.

   Both are recorded in the result file's `build` section.
2. **The cutoff rule and K2, resolution (D-8; N9).** A (cell, R)'s cutoff is the latest of 14:30, 14:00, 13:30, ...,
   10:00 CT such that, over its fills before it, the pooled unresolved share at **its own R** is at most 5 %, **overall
   and in each calendar year 2020 to 2023**. With no such time the (cell, R) is killed (K2). Fills after the cutoff are
   dropped (the ticket is cancelled at the cutoff).
3. **K1, supply:** at least 100 fills on the choice block after its cutoff, and at least 12 in each calendar year.
4. **K5, ambiguity (D-1; N1, N2).** A (cell, R) whose share of ambiguous pairs among its choice-block fills (after its
   cutoff, under symmetric booking) exceeds 5 % cannot be measured on one-minute bars, and is killed. The share by year
   is reported.
5. **K3, realised risk (D-9).** D-212 (1) cannot fail in this walk (a stop exit books S ticks plus a tick of cost; gaps
   add nothing), so it is recorded as not applicable in stages A to C. Its stage-D form is 6.3's.
6. **A cell** with every R killed is killed.
7. **K4, fill realism: reported, decides nothing (N7).**
   - For `fade`: fills over touches (a touch is a bar reaching the level without trading through it). This is a
     micro-rejection rate -- mechanism-relevant, though it reads no lift.
   - For `break`: the share of fills that gapped.
   - For both: the share of fills in the first five minutes after 08:30, and on fill bars spanning a quarter of the stop
     (D-13).

   K4's outcome part -- the outcome of touched-but-unfilled fades -- is computed with stages B and C, beside (D-10).
8. **The placebo cells and the valuation's inputs.** The placebo cells' counts and K5 shares are read here. So are the
   contract-arithmetic inputs of section 10: σ, cap and ρ per (base, place, stop, R), from `records_leaf`,
   `place_values` and D-667's sizing, with no outcome.
9. **Planning (D-4), from counts only, written before stage B reads anything.** For every surviving (cell, R):
   - its choice-block fills;
   - its judged-block fills, **estimated** as the choice-block rate per session times the judged block's sessions;
   - the minimum detectable lift at the family's level with 80 % power, from Q-16's power curve [Q-16], with the
     worst-case-sd Student-t formula beside (D_protocol Appendix C);
   - for `break`, the same for the placebo-differenced lift;
   - the value bar in points at the cell's uses (section 10), and the ratio of the two.

   Every figure goes to the `planning` section; none is typed anywhere. R-16 (a screen, or pooling, when the ratio is
   large) is a proposed row, not adopted, and is not applied.

Every cell killed: the family closes at stage A.

## 8. Stage B: choose on the choice block

For every surviving (cell, R), on the choice block:

1. **The statistics.**
   - The lift L under the C1 booking (5.5, 5.6).
   - For `break`, also **D = L - L_placebo**: L_placebo is the mean of w over all fills of the five placebo replicates.
   - The lift under `rule_fill` (C2's booking).
2. **The bootstrap.** A stationary bootstrap (Politis and Romano) of the choice block's sessions in date order,
   circular, mean block 21 sessions, **2,000 replicates, seed 20261930**.
   - Each replicate is one draw of session indices, shared by every statistic and by the placebo fills.
   - A replicate's lift is the resampled sessions' summed w over their summed fills (D likewise).
   - The standard error is the replicates' sd. t = L / se, and a centred replicate is t\*_b = (L\*_b - L) / se.
3. **The decisive statistic** T(c, R): for `fade`, t_L; for `break`, the smaller of t_L and t_D (and the same for each
   replicate). The red team's check -- synthetic, its `iut.py` -- found this inside 0.05 for a break cell with D at
   zero, provided break and fade at a kind survive stage A together; they share their pairs and their pooled gates.
4. **The family-wise critical value** q: the 95th percentile over replicates of the maximum of T\* over every surviving
   (cell, R) -- one-sided, family-wise 0.05. Benjamini-Hochberg at 10 % is reported beside and never selects.
5. **Eligibility (F5).** A (cell, R) above q is eligible only if its **rule-side** trades at its R on the choice block
   leave at most 5 % unresolved, overall and in each calendar year 2020 to 2023 (D-212 (2) binds the traded side).
6. **Kill B.** No eligible (cell, R) above q: the family closes, and the judged block is not read.
7. **The pick.** The eligible (cell, R) with the largest **valued lift** (section 10) at the lower limit of its
   `rule_fill` lift, L_rf - q x se_rf, with uses = the choice-block fills a year.
   - A tie (equal to the dollar) goes to the one with more choice-block fills, then to the first in table order (5.1,
     5.2, stops ascending, R ascending).
   - There is one pick.

Stage B is a gate, not a claim (D_protocol N-1): it spends nothing of the program's budget.

## 9. Stage C: judge the pick on the judged block (the pass line, E-008)

The pick alone, with its cutoff and every rule as fixed in stages A and B, on fills from 2024-01-02 to 2026-07-16.
**C1 to C4 must all hold; any failure closes the family.**

1. **C1, direction.** The pick's lift under its C1 booking (5.5) on the judged block has a one-sided lower bound at
   **0.05 / (k (k + 1))** (0.05 / 132 at k = 11) **above zero**, by Q-16's calibrated statistic **[Q-16: its name,
   module and commit]**. It is applied to the mean over all the pick's judged fills, with sessions clustered as Q-16
   calibrated it.
2. **C1', the level beyond a crossing (`break` picks at `pdc` and `rn100`; D-2, D-592).**
   - **The line.** The placebo-differenced lift D on the judged block has its lower bound at the same level above zero,
     by the same statistic.
   - **How it is computed.** The statistic is applied to the per-session sums z_s = (sum of w over level fills on s) /
     n_level - (sum of w over placebo fills on s) / n_placebo, where **n_level and n_placebo are the judged block's fill
     totals** (the pick's fills; the placebo's over its five replicates). So the z_s sum to D, the difference of the two
     means over fills (F2).
   - **Why it costs nothing.** It is an intersection with C1 at the same level, so there is no extra spend.
   - **What it identifies.** At these two kinds the placebo is a fair match: neither level is a range extreme (the red
     team's F1), and T-14 (c) must show that a follow effect growing with the window broken leaves D at zero (17.6).
   - **What a C1-only pass means.** A break pick passing C1 but not C1' is recorded as D-592's follow effect seen
     again: a lead for unread data, not a finding.
   - **If Q-16 does not cover this form.** If Q-16's calibration does not cover this two-sample form, the pin waits for
     one that does, or a revised draft drops `break` before the pin -- never decided after a read.
3. **C2, value (F4).** The valued lift (section 10) at the lower bound -- at the same level, by the same statistic -- of
   the pick's lift **booked at `rule_fill` with 1 tick** is at least **$500 a year**. Its uses are the smaller of the
   choice-block and judged-block fills a year. A side rule's booking bias, of either sign, is at the bar's scale (the
   red team's F4); `rule_fill` turns it against the rule for both side rules.
4. **C3, resolution (a floor, E-008).** On the judged block, the pick's rule-side trades at its R leave at most 5 %
   unresolved, overall and in every calendar year (2024, 2025, and 2026 to 07-16). A calendar year with fewer than 63
   sessions in a window is pooled with the adjacent year (D-604's stub-year point; it does not bind on these blocks).
5. **C4, measurability.** K5 on the judged block: the ambiguous share is at most 5 %. It guards measurability, not an
   error rate, and can close a true effect for a direction-free reason -- for instance, one-minute ranges in points
   larger at NQ's higher 2024-2026 price level (N2).
6. **Beside, deciding nothing:**
   - the lift by calendar year on each block;
   - the reverse walk-forward: stages A to C with the blocks swapped and their own cutoffs, its bootstrap
     `default_rng([20261934, 0])` and its statistic's draws `[20261934, 1]`;
   - the seeded coin twin (20261931);
   - the net R lift;
   - **drift (D-12, D-271 (5)):** the lifts on long-rule and short-rule fills, and their mean, the side-balanced lift;
   - C1's lift under the other booking;
   - the booking ladder: symmetric at 2 and 4 ticks; `rule_fill` at 2 and 4 ticks (the lift if the market at the fill
     stood that many ticks past the trigger);
   - Benjamini-Hochberg;
   - K4's adverse selection;
   - the share of fills in the first five minutes after 08:30;
   - the placebo-differenced lift for a `fade` pick.
7. **What a `fade` pass means (F10).** A fade pick passing C1 to C4 is **a reversal after these crossings**, carried on
   its trades as E-008 judges designs: no read on this window predicts it. Whether the reversal is specific to the
   level is the placebo-differenced lift beside it, and the level claim is made only if that also clears C1's level.
   At `on` and `pd` the placebo is not matched on the window broken. There, the known follow effect pushes a fade's
   lift down at a long-window extreme, so it works against a pass; only a long-window reversal effect, which no read on
   this window has found, could produce one.

## 10. The valued lift (F3, F8)

The value map's own first-order formula (`vendor/stage2/results/u_value_map.csv`, definitions `extra_win_prob_points`
and `mean_dv`), extended to places taken in one priority order, which stage D's routing uses too.

- **The base.** `p14` for 50- and 100-tick stops (P-14's rungs), `p16` for 150 ticks.
- **The places that ask R.**

  | place | phase | R it can price | σ(p, R) | cap(p, R) |
  |---|---|---|---|---|
  | (b) the evaluation | `combine` | any R | the share of the phase's recorded trading leaf-days whose leaf R is the cell's R (`records_leaf`) | `trades_per_year_forward(p)` x σ |
  | (c) the funded opening | `funded` | R = 3 only | 1 (the table's opening ask, handoff 2.5) | `trades_per_year_forward(c)` |
  | (d) funded later | `funded` | R = 1 and 1.5 | over the whole funded phase, the opening's days in the denominator (conservative) | `trades_per_year_forward(p)` x σ |
  | (e) paid | `paid` | any R | as for (b) | `trades_per_year_forward(p)` x σ |

- **The value of a use at the pick's stop:** v(p) = `mean_dv(p)` x ρ(p).
  - **Why ρ.** The vendored map gives no per-rung `dv`: `dv` is "averaged over the rungs" (definitions).
  - **`p16` at 150 ticks** has one rung, so its `dv` is exact and ρ = 1.
  - **`p14` at 100 ticks:** ρ = 1. A 100-tick ticket realises at least what the rung average does, so this errs low
    (conservative).
  - **`p14` at 50 ticks:** ρ(p) = the sum over the place's R-asking leaf-days of the 50-tick realised risk, over the
    same sum at 100 ticks, each realised risk being min(floor(r / (S x $0.50)), allowance) x S x $0.50 (6.3). Under the
    map's first-order model a `dv` is proportional to the dollar risk realised. The rung average is at most the 100-tick
    `dv`, so `mean_dv` x ρ is at most the 50-tick `dv` (conservative).
- **The priority order (F8).** The places are ordered by v(p), highest first. The pick's uses u (its fills a year) are
  allocated in that order, u_p = min(u - the uses already allocated, cap(p, R)).
- **The value:** $ a year = λ x the sum over p of u_p x v(p) / 100, with λ the lift in points at the bound in question.
  Stage D routes each ticket in the same order (11.2), so the value is priced where the campaign spends it.
- **How it is read.** First-order, with the table held fixed. It is a ranking and a bar, never a forecast -- "unreliable
  far from zero" (handoff 2.7; D_protocol N-4).

## 11. Stage D: the campaign -- E-008's floors, and the scorecards beside

Stage D runs whenever stage C has been read:
- **When C1 to C4 hold,** its floors decide.
- **When the family closed at C,** the floors decide nothing, and stage D gives only the scorecards beside the close
  (E-008: the scorecard beside every judgement). Such a run reads the judged block's start days for a closed design, so
  a later family lists it as prior exposure (N6).
- **A close at A or B** reads no judged block and has no stage D.

### 11.1 Its role, and the floors

Kept, not dropped, because E-008 binds the long-run gate, verified rules and conduct tier 1, and requires the user
scorecard beside every judgement -- and a gate is read only on a campaign. **The floors can close the family; nothing
here can carry it.**

- **(i) The gate:** growth on the required bankroll at the bound **above zero** (Stage 2 D-145), at the fresh seed,
  with **both streams at the one-sided 0.05 bound** (11.4; F7).
- **(ii) Realised risk on the tickets' trades, in P-14's registered form** (6.3). It holds by construction at these
  stops and is checked in the build (T-15).
- **(iii)** Every rule is verified.
- **(iv)** Conduct tier 1 is true of the routing (11.3).

F-01's verdict by D-621 (3) against R\* is gone (E-008).

### 11.2 The design

**The base, by the pick's stop** (the table its valuation used, D-3 item 3):
- **50- and 100-tick picks: P-14** (A3-BRK30-CB20, with its schedule, table and five Topstep $50K seats; the
  no-closure table; at most 20 purchases in 21 sessions);
- **150-tick picks: P-16** (`rc_s150_all_nr`).

The base's own trades, walk, coin, cuts and table are unchanged. The pick's tickets are added as follows.

- **Published and placed.**
  - A ticket is published at 08:25 on every day its kind has one (5.1; voids as 4.5).
  - It is placed at 08:30 on one account, taking the places of section 10 in their priority order: the first account,
    in the router's order, whose state is in the highest-priority place asking the pick's R; failing that, the next
    place.
  - That account is **reserved** while the ticket rests: the base routes no offer to it.
  - With no account in any place asking R, there is no ticket that day (counted).
- **A busy firm at 08:30.** If the firm holds a position at 08:30, or closed one in the last five minutes, the ticket is
  placed once the firm has been flat five minutes (void if already through).
- **Cancel on entry.** Before any base entry on another account, the resting ticket is cancelled. It is re-placed five
  minutes after that trade's exit, void if already through, and never after the cutoff.
- **A fill.** A ticket's fill takes the firm's one position; the base's offers are refused until five minutes after its
  exit (D-429).
- **Two tickets of a kind on one day.** Both rest on the reserved account. The first fill cancels the other, which is
  re-placed five minutes after the exit.
- **Size.** min(floor(leaf risk / (S x $0.50)), allowance) micros, in the reserved account's state, at the pick's stop
  and R -- the base's own sizing (6.3).

### 11.3 Conduct

Every step is realisable by hand. The firm never holds two positions, so never opposite positions across accounts
(tier 1). Each ticket rests on one account (D-157).

### 11.4 The bound level, and the tickets' verdict arm (M5, F7)

**One level for both streams: the one-sided 0.05 bound** -- the charter's verdict arm, and the level U1's verdict arm
reads ("every R at the 0.05 bound the design's gate read", `scripts/user_journey.py`).

- **The tickets.**
  - Which trades: the pick's own rule-side trades at its R, walked as in 5.4-5.5 under the C1 booking, with ambiguous
    fills as stopped losses.
  - Which block: each block separately, by Student-t on 21-session block means.
  - Which era rule: **the lower of the two blocks' bounds** (D-271 (1)'s rule, without its test).
- **The base.** Its trades are shifted at the 0.05 bound exactly as U1's verdict arm shifts them -- not at its
  registered 0.05/N development line, which only the identity reproduces (11.5).
- **How.** Each stream is shifted by lb - e (`propedge.campaign.gate.shifted_blocks`), and the two are merged into one
  day log.

### 11.5 The runs

1. **The identity first, refusing (T-15).** With no tickets the runner must reproduce:
   - the base's registered gate paths (P-14: `vendor/stage2/results/a3_brk30_cb20_gate_paths.csv`; P-16:
     `rc_s150_all_gate_paths.csv`), at their registered level, on E-002's columns and tolerance;
   - U1's start rows (`results/user_journey.csv` section `start`, at its 0.05 verdict arm, E-010 (2)'s comparison).

   A failed identity stops the family.
2. **The gate.** Stage 2's `gate` call as the base registered it -- rotation, its horizon, 500 paths, **campaign seed
   20261935**, 0 % denial, the placement off -- with both streams at the 0.05 bound. Floor (i) is read here.
3. **Beside:**
   - the base alone at the same seed and level (the paired difference: the tickets' own effect);
   - P-06's row;
   - denial at 10, 25 and 50 %;
   - the placement on;
   - D-212 (1)'s letter form (the share of tickets carrying at least 90 % of the leaf's risk);
   - the share of tickets outside the stop band (6.3);
   - D-663's stress readings where Q-18's tooling exists.

### 11.6 What stays unidentified (D-3)

1. **The base occupies the firm** at most of its offers, so the tickets' take-up is limited. It is reported: placed,
   filled, cancelled on entry, voided at re-place, and refused for no account at the R.
2. **The reservation changes the base's routing** even when no ticket fills.
3. **For a 150-tick pick,** the comparison with R\* = P-14 mixes the base's own distance from P-14 with the tickets.
   The paired difference against its own base is read beside it.
4. **The judged block has few independent starts** (E-007 (2), red team M2). Every P comparison is calibrated and
   beside.
5. **The value map is first-order with the table fixed.** The routing's priority order follows it; the campaign's
   realised mix can differ, and is reported.

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
   calibrated P comparison **[Q-16]**, one-sided at 0.05; reported, never a line. Its draws, if any, use seed
   **20261936**. D-621 (3)'s percentile bound is not computed (E-007 (1)).
6. **Limits:** E-015's limits, **once approved by the operator**, as **menu flags only**. A design crossing one is shown
   with which limit and by how much; a limit never fails a design. Until approved, the menu is read without flags, and
   says so.
7. **The evenness trade-off curve** -- how much "ahead" each step of evenness costs -- beside, with this design's point
   and its base's, in the form E-015's menu reading fixes.
8. **Not modelled, and said so wherever this scorecard appears:** a user who stops when their own money runs out, the
   user's time, taxes.

The replay draws nothing.

## 13. What a pass and a fail mean

- **CARRIED** (C1 to C4, C1' for a break pick, and stage D's floors all hold). The pick is a development finding on a
  late-development block. It takes a registration id (D-621 (9)'s house form), a model card, its registered development
  test, the auditor, and then **one confirmation** (section 14), which carries the decision (D-189).
  - **A break pass** is a direction at the prior close or at round numbers, beyond what a matched crossing carries.
  - **A fade pass** is a reversal after these crossings (9.7).
- **CLOSED** at stage A, B, C (C1, C1', C2, C3 or C4) or D (a floor). The reason goes in a decision row.
  - A close at B or C is recorded as **"no lift above the MDL (planning section) at this family's level"**, never as
    "no lift at levels" (D-4).
  - A close at C carries stage D's scorecards beside it, and makes the judged block's start days prior exposure for
    later families (N6).
  - The failure protocol applies where a check failed rather than a kill line.
  - The closure binds this specification (D-277's boundary): a later family on these levels names this closure, states
    what changed and why it is a different hypothesis (D_protocol 1.5 (c)), and is judged on data this family did not
    read.
- **`break` at `on` and `pd`** was not tested here (6.2). It belongs in its own declaration, on unread data.

## 14. The confirmation (M1, D-6), declared before any development read

- **The window.** NQ from 2026-07-17 (`config/windows.yaml`, `reserve`, `reserved`): not on disk, never read until a
  carried candidate is registered.
  - It becomes NQ's **fourth** confirmation window only by the operator's decision (D-107; P-05, P-06 and P-10 spent
    the three).
  - It is a purchase (the operator's; `docs/OPERATOR_SETUP.md`, waited for).
  - Stage 2's draft P-16 confirmation targets the same window (`vendor/stage2/prereg/DRAFT_P16_confirmation.md`). If
    any test reads it first, the lead records that before registration, and the operator decides whether it can still
    confirm this pick.
- **What it tests: the pick's trades, not P.**
  - **The line.** The pick's lift over its coin twin on the window's fills (every rule, booking and cutoff as fixed in
    stages A and B), one-sided at the registered **0.05**, by Q-16's statistic [Q-16], with the bound at 0.05/N beside
    (D-189's form). Its draws, if any, use seed **20261937**.
  - **A break pick** is also confirmed by its placebo-differenced lift. Its placebo uses the same past-only pairing
    (sources from development days included), replicates `default_rng([20261932, 5 + j])`, j = 0..4, drawing in 5.8's
    order over the window's days.
  - **C2 at the 95 % bound,** under `rule_fill`: at least $500 a year.
  - **Resolution:** at most 5 % overall, and in every calendar year with at least 63 of the window's sessions (a stub
    year pooled with its neighbour, D-604).
  - **K5:** at most 5 % on the window.
- **What it cannot test: P.** A six-month window is about 126 sessions: about 63 start days with a month-3 horizon left,
  one 63-start block, on which no interval on P exists (red team M1). The scorecard on the window is descriptive,
  without an interval, and never a line.
- **How much data.** At least six months (D-604), and at least the number of months at which the pick's expected fills
  reach the count at which Q-16's statistic, one-sided at 0.05, has 80 % power for a lift equal to the pick's judged
  lower bound at the family level. The expected fills are the lower of its two blocks' rates per session x 21 sessions
  a month. The count is computed when the pick is carried and written in the carrying row, before any confirmation data
  exists. If it is more than the operator will buy, no confirmation is registered, and the pick stays a development
  finding.

## 15. Seeds, fixed now and checked

| seed | what it draws |
|---|---|
| 20261930 | stage B's stationary bootstrap (choice block) |
| 20261931 | the seeded coin twin beside (5.7) |
| 20261932 | the placebo's source draws: `numpy.random.default_rng([20261932, j])`; j = 0..4 on development, 5..9 on the confirmation window; the draw order of 5.8 |
| 20261933 | stage C: the draws of Q-16's statistic, if it draws any (else unused, and the result file says so) |
| 20261934 | the reverse walk-forward beside: `default_rng([20261934, 0])` its bootstrap, `[20261934, 1]` its statistic's draws |
| 20261935 | stage D's campaign seed: the gate floor and every beside arm, 500 paths |
| 20261936 | the scorecard's calibrated P comparison (Q-16), if it draws |
| 20261937 | the confirmation's statistic, if it draws |
| 20261938 | the build's walker tests: `default_rng([20261938, j])` -- j = 0 the shift test's replacement walks, 1 T-3's synthetic judged block, 2 the spread-and-jumps T-13, 3 the heavy T-13 |
| 20261939 | the build's planted-effect test, T-14: `default_rng([20261939, j])` -- j = 0 parts (a) and (b), 1 part (c) |

**The check (T-12).** On 2026-11-15, a word-bounded search of the whole working tree -- the vendored snapshot and its
results included, binary files skipped (`grep -rIowh --exclude-dir=.git -E "2026193[0-9]" .`) -- found 20261930 to
20261939 only in the Q-21 brief, as the proposal. The red team's search on 2026-11-15 found them only in this draft,
that brief and E-017. The one match without word bounds is digits inside a floating-point value in
`vendor/stage2/results/a3_brk30_cb20_gate_paths.csv` -- not a seed.

**Inherited, and used only as their owners registered them:**
- the bases' seeds -- P-16's coin by date and minute 20261102, P-14's identity seed 20261131 and P-16's gate seed
  20261206 (E-002);
- Q-16's 20261910 to 20261919 and Q-17's 20261920 to 20261929, which are theirs.

**Not reused:** F-01's 20261901 to 20261903 (withdrawn, never run). 20261901 is also Stage 2's
`user_drivers.CLUSTER_SEED` (D_protocol N-2).

## 16. Multiplicity and the budget

1. **F-01 spent k = 10** (E-007 (a); committed code of it existed on `wt/wt-levels`, red team M7, so R-6's condition
   (i) failed). **This family takes the next free program family number at its pin -- 11 if pinned next, level
   0.05 / (11 x 12) = 0.05 / 132.** If another family is pinned first, k and the level are the gatekeeper's count, and
   the pinning row writes them.
2. **One cell reaches judgement**, with no further division in the family.
   - C1' is an intersection with C1 at the same level.
   - C2 is a conjunctive gate, not a claim.
   - Stage B's family-wise test, on the choice block, spends nothing (D_protocol N-1).
3. **The program's honesty sentence (P-2).** Stage 2 ran programs S and U on this same window, each with its own 5 %.
   The development-stage level is a screening threshold; **the decision is carried by one confirmation on unread
   data** (D-189: "the confirmation window carries the decision, never a smaller N"). A program ledger across both
   repositories (R-1) is not built; when it is, this family is listed in it.
4. **Counted (R-17's words):**
   - 18 cells, each counted whether killed or read;
   - 54 signed hypotheses, over 36 (kind, stop, R) questions;
   - 18 placebo cells, as controls;
   - one campaign cell if stage D runs;
   - the reverse walk-forward re-reads the same cells;
   - `break` at `on` and `pd` (6 cells) is dropped before any read, and is not counted.

   A later D-189 N counts these, plus section 2's Stage 2 reads of the mechanism.
5. **D_protocol 1.5's holes:**
   - (a) There is no fitted model and no hyperparameter.
   - (b) No normaliser spans the sample: `A` trails 20 full sessions, placebo sources are past-only, and T-3 shows the
     choice stages ignore the judged block.
   - (c) This family re-declares F-01 after reviews, not after a read (F-01 read no bar). The closed branch, and the
     cells D-592 closed the window to, are left out; the follow effect elsewhere is met by C1'.
   - (d) No exploratory read of these levels exists here. No read ledger exists yet (R-5), so the family's bars are
     read only by its runner, from a clean checkout, after the pin.
   - (e) k, as above.
   - (f) The tests, section 17.

## 17. The build's identities and tests, before any reading

All of the family's code is committed after its pin (T-9). It is fast-tier unless marked.

1. **The walker** (E-011: P-16's `TRADES_SHA256` under `STAGE2`) holds at the build's commit. The family's preset
   differs from `STAGE2` only in the breakeven move, and a test shows the preset with the move on is `STAGE2` exactly.
2. **E-002's and Q-05's identities** hold at the build's commit, and the run **refuses, never skips**, when their data
   are absent (T-11).
3. **No look-ahead** (feature-rules 2; D-5; F2).
   - **What is replaced:** every bar stamped at or after 08:25 on day E, and every bar of every later day.
   - **What must not move:** every level, side and `P_ref` on E, every `A_E`, and **every placebo ticket on E** (its
     source, distance, price and side).
   - **How:** a seeded walk (`[20261938, 0]`) and a constant as the replacements, over days including roll days, DST
     changes, the seam, early closes and the days after them. Also asserted: no level is all-NaN or constant.
4. **Fill rules on synthetic bars**, under the family's preset:
   - the void at `t_live`;
   - the gap through;
   - the trade-through;
   - one fill;
   - the cutoff;
   - every calendar void, read from the pinned calendar file and never from the day's bars;
   - FOMC days, and report days;
   - the pair rule under both bookings;
   - two levels a day;
   - break and fade exact negatives under symmetric booking, except on gaps and at the void boundary.
5. **T-13, the mirror's zero, per side rule, per stop (50, 100, 150 ticks) and per R, never pooled:**
   - **(a) Today's form, extended (fast).** A tick-continuous walk whose one-minute ranges reach the stop on a declared
     share of bars (at least Appendix B's middle row): `pair` with symmetric booking covers zero, and `declared` with
     `rule_fill` stays the strict expected failure (E-010 (3)).
   - **(b) Spread and jumps (F4; declared now, runs in the build before stage A; synthetic, seed `[20261938, 2]`).**
     - *The walk:* a mid-price on a tick-continuous walk, with a one-tick bid-ask spread; prints at the ask on an
       up-move and at the bid on a down-move; jumps of 2 to 8 ticks (uniform) with probability 0.002 a step; as many
       synthetic days as today's T-13.
     - *What it reads:* each booking's mean lift under this null, per (side rule, stop, R), with its 95 % interval,
       written to the `build` section.
     - *What it decides:* where symmetric booking's interval lies wholly on the side favouring the rule, C1 and C1' for
       that (side rule, stop, R) are read under `rule_fill` with 1 tick instead (K0, 7.1). `rule_fill`'s own reading is
       reported, expected conservative.
   - **(c) The precise form (N5; heavy).** It is held to a quarter of the smallest `extra_win_prob_points` in
     `u_value_map.csv`, section `bar`, at `target=500`. That needs about 3.5 million fills per (side rule, stop): it
     runs under the run lock, synthetic, CPU-bound, with modest memory, seed `[20261938, 3]`.
6. **T-14, a planted effect** (seed 20261939):
   - **(a)** A continuation of known size, planted at level touches only, is recovered with its sign and size by L and
     by D; stage C's bound covers it at its level.
   - **(b)** The same continuation planted at every crossing alike leaves D at zero within its interval.
   - **(c) The window-length null (F1).** On synthetic multi-day paths with an overnight segment and a prior session,
     plant a follow drift for a few minutes after every crossing, proportional to the log of the minutes since the price
     last stood there, and no level effect. At `pdc` and `rn100` break cells:
     - L's lower bound must be above zero (the effect is visible in L);
     - D's two-sided 95 % interval must cover zero, with enough synthetic days that its half-width is under a quarter of
       the planted lift's size on L.

     **If (c) fails at a kind, `break` at that kind is killed before stage A** (K0; recorded, not rerun).
   - **(d)** A level read from the 08:25 bar is caught by test 3.
7. **T-3, choice-stage invariance.** Stage A's and B's outputs are byte-identical when every bar from 2024-01-02 on is
   replaced by a seeded synthetic walk (`[20261938, 1]`). The outputs compared: cutoffs, kills, planning, the
   valuation's inputs, the critical value and the pick.
8. **T-15, stage D's routing.**
   - With no tickets, the base's registered paths and U1's start rows (11.5).
   - Toy days for: the priority order, the reservation, cancel-on-entry, re-place at exit plus five minutes, void at
     re-place, two tickets, the cutoff, the base's sizing at the pick's stop, and floor (ii).
9. **Q-16's own size test** passes at the build's commit.
10. **T-12:** section 15's seeds appear nowhere else in the build's commit.
11. **T-7's analogue:** stage C reads the pick from stage B's result file by its sha256, and its entry point cannot run
    stage B.

**Protocol items, not this family's to build (named so they are not lost):**
- T-1 (the program ledger);
- T-2 (the family-file lint -- this file carries its sections);
- T-4 (the read ledger);
- T-5 (withdrawals);
- T-6 (Q-16's calibration);
- T-8 (append-only decisions);
- T-10 (results provenance; this family's manifests carry the data manifest's hash, section 18).

## 18. Outputs, counts and the run

- **Files.**
  - `results/rl2_levels.csv`, with sections `build`, `supply`, `cutoff`, `kill`, `planning`, `valuation`, `choice`,
    `judged`, `placebo` and `beside`;
  - `results/rl2_campaign.csv` (stage D: `identity`, `gate`, `beside`);
  - `results/rl2_journey.csv` (section 12).

  Each is written with its sidecar manifest through `extended.results.write_result`, carrying:
  - `prereg_id` the family's F-id;
  - the cell and hypothesis counts;
  - every seed and parameter;
  - the sha256 of `vendor/DATA_MANIFEST_stage2.sha256` and of the pinned calendar file (P-4 item 6).

  They are EXPLORATORY until a carried candidate is registered.
- **The run.** Once, from a clean checkout of a named commit (`scripts/run_clean.py`), under the run lock, watched to
  its end.
  - The order is fixed: the build's synthetic K0 tests, then stages A, B, C and D. Each stage's file is written before
    the next stage reads anything.
  - A kill stops the sequence.
  - A run aborted or restarted is recorded by the lead with its log, and only the first complete run is read.
- **Waits.** No judged-block read until Q-05 holds (done, E-010) and Q-16 is merged (E-008).

## 19. Open before the pin

**The lead's:**

1. **Q-16.** Its choice fills the [Q-16] marks (7.9, 9.1-9.3, 12 item 5, 14), and settles whether its calibration
   covers the two-sample form of C1'.
2. **The calendar file (F6)** must be compiled and pinned under a decision row before this family's pin: the scheduled
   early closes of NQ in 2020-01-02 to 2026-07-16 from CME Group's published holiday calendars, and the data-defect
   days from Stage 2's NQ data report (`docs/data_reports/data_report_bars_NQ_2026-10-30.md`, not vendored). Dates
   only, read as a calendar. Until it exists, 4.5 (a) and (b) cannot be applied.
3. **Floor (ii)'s form (F3).** This draft takes P-14's registered allowance-capped form, which keeps the funded opening
   reachable. D-212 (1)'s letter, with D-272's stand-aside, would make every R = 3 hypothesis uncarriable at these
   stops (6.3). The lead confirms the form, or puts the letter to the operator, whose rule D-212 is.
4. **The readings beside.** Q-17's adapter is needed for 12 item 4, and E-015's approved limits for 12 item 6.
5. **The long-run-gate floor.** Whether it is read on stage D's design, as here, or taken as met by the base's
   registered PASS (which would make stage D wholly beside). Either way, decided before the pin.

**The operator's**, each with its safe default applied, none blocking:

1. `or30` and the opening ranges (D-281 (3)): out by default (E-007 (b)).
2. The confirmation: NQ's fourth (D-107), shared with P-16's draft; its length and its purchase.
3. The levels of E-015's limits (approval pending).
4. D-212 (1)'s form for tickets at the table's capped leaves, if the lead puts it to them (item 3 above).

## 20. Anything chosen after seeing results

*(Empty at declaration. Anything added after a reading is exploratory, reported apart, `exploratory=True` in its
manifest, and recorded in its own decision row -- never in this file.)*
