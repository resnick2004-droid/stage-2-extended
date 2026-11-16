# DRAFT F-XX: resting orders at pre-session levels, corrected (family RL2) -- not declared

**Status: DRAFT of 2026-11-15 (TASK_QUEUE Q-21), for the red team. Not pinned, not numbered, not declared.** It
replaces F-01 (`prereg/F-01_resting_order_level_atlas.md`, withdrawn, its k = 10 spent, E-007 (a)). No bar has been
read for it, no level computed, no outcome of any order computed. It becomes a declaration only after the red team's
review, the prereg-gatekeeper's approval (which assigns F-XX and k) and the lead's pinning row with its sha256.
**It cannot be pinned before Q-16 is merged:** its pass line is Q-16's calibrated statistic, whose choice is pending;
the marks **[Q-16]** below are filled in a revised draft, with the merged statistic's name, module and commit, before
the gatekeeper reads it. Nothing else is left open except the items of section 19, each closed before the pin.
Anything chosen after a reading is exploratory and reported apart.

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
| cells (`k_cells`) | 4 level kinds x 2 side rules x 3 stops = **24**, each counted whether killed or read |
| hypotheses | 24 cells x 3 R = **72** signed (36 up to sign, section 5.6) |
| the pass statistic | the lift over the coin twin on the same fills, by Q-16's calibrated test **[Q-16]** |
| the value bar | $500 a year at that bound (`vendor/stage2/results/u_value_map.csv`, section `bar`, `target=500`) |
| seeds | 20261930 to 20261939, each assigned in section 15 |
| model card | none: no fitted model; the grid is the family |

---

## 0. What this corrects

Every finding of the Phase 0 audit (`docs/audits/phase0/D_protocol.md`) and the red team
(`docs/reviews/phase0_red_team_2026-11-15.md`) that bears on F-01, and where this file answers it.

| finding | F-01's defect | the correction | section |
|---|---|---|---|
| D-1 | the fill-bar rule (a stop touch counts, a target touch not) biases break down and fade up | the pair rule (`fill_bar="pair"`); the ambiguous share read and capped (K5) | 5.5, 7.6, 9.5 |
| D-13 | the mirror booked at the rule's fill; fast-market overshoot | symmetric booking about the trigger (`mirror_booking="symmetric"`); a slippage and overshoot ladder beside | 5.5, 9.6 |
| D-2 | `or30` inside Stage 2's closed opening-range branch; line 23 false; break cells load on D-592's lead | `or30` out (E-007 (b)); line 23 corrected; a prior-exposure section; break cells also judged by a placebo-differenced lift | 1, 2, 9.2 |
| D-3 | stage D cannot identify the tickets' value | stage D keeps only E-008's floors; the scorecards beside; base by stop; tickets routed to the state asking the pick's R; cancel and re-place; what stays unidentified stated | 11, 12 |
| D-4 | the MDL is far above the value bar | the MDL from counts and Q-16's power curve on record before stage B; a close reads "no lift above the MDL" | 7.7, 13 |
| D-5 | a minute of look-ahead at 08:25; the side set at `t_live` | levels and sides from bars stamped at or before `t_pub - 1 min`; the void rule at `t_live` | 4 |
| D-6 | the confirmation is NQ's fourth and P-16's window | declared so; the operator's D-107 decision | 14 |
| D-7 | 20 cells counted, 60 hypotheses selected over | cells and hypotheses both counted | 16 |
| D-8 | K2 allowed 10 % unresolved in a year | 5 % overall and in every calendar year | 7.1 |
| D-9 | K3 cannot fail in this walk | recorded so; realised risk checked in stage D | 7.4, 11.1 |
| D-10 | stage A read an outcome (K4) and the judged block (planning) | K4's outcome part moved to stages B and C; judged fill counts estimated | 7.5, 7.7 |
| D-11 | roll days, the 2025 seam, early closes; `rn100` in "index points" | calendar voids, counted; `rn100` in the futures' own price | 4.5, 5.1 |
| D-12 | no drift control, per-era report, placebo or stress readings | beside; the placebo decisive for break cells | 9.2, 9.6, 11.5 |
| D-14 | the bootstrap's type and the bounded estimator unstated | stationary, mean block 21, centred, studentised; the estimand the mean over fills | 5.6, 8 |
| D-15 | no fixed / searched / dropped table; silent drops | the table, every drop with its reason | 6 |
| A, MINOR 1 | D-212 and D-308 swapped | realised risk is D-212 (1); resolution is D-212 (2) as D-308 (3) raised it | 3 |
| A, MINOR 2 | "the 12.5-point stop loses to costs (D-527)" | D-527 re-read; the 12.5-point stop admitted as a cell | 6.3 |
| M1 | the confirmation cannot confirm P | it tests the pick's trades; P on the window is descriptive | 14 |
| M5 | the tickets' verdict-arm bound undeclared | which trades, which block, which era rule | 11.4 |
| M7, R-6 | F-01's k | F-01 spent k = 10 (E-007 (a)); this family is the next free | 16 |
| N-2 | seed 20261901 is Stage 2's `user_drivers.CLUSTER_SEED` | new seeds, searched | 15 |
| N-3 | "flattened at that bar's close" (15:10's bar closes at 15:11) | Stage 2's flatten convention | 5.4 |
| M4, E-007 (c) | the signal-service purpose | dropped: one user's own accounts | 1, 3 |
| P-1, E-008 | stage D judged by D-621 (3)'s uncalibrated bound | the pass line is the trades' calibrated lift; every P comparison beside and calibrated | 9, 12 |
| P-2, P-3 | the budget's claim; the judged block's freshness | stated plainly | 2, 16 |
| 1.5 (a)-(f), T-1 to T-15 | holes and tests | which this family's build owns, which are protocol items | 16.3, 17 |
| E-014, E-015 | the journey scorecard | beside, every measure a distribution, limits as menu flags | 12 |

## 1. Hypothesis

**The mechanism (F-01's, unchanged).** Orders cluster at prices everyone can see before the session: just beyond the
prior session's high and low, the overnight range, the prior close, and round numbers. Stop-loss and breakout stop
orders beyond such a level turn a touch into a burst of market orders in the direction of the break (a cascade);
resting limit orders at the level absorb a touch and push it back (a rejection). Which dominates is the question. The
evidence that clustered orders at visible levels move prices is in currency markets (Osler 2003, *Journal of
Finance*, "Currency orders and exchange rate dynamics"; Osler 2005, *Journal of International Money and Finance*,
"Stop-loss orders and price cascades in currency markets"); for NQ it is untested here.

**What Stage 2 did and did not do (F-01's line 23 corrected).** Stage 2 did enter at levels. ORB5's entry was a stop
order at the opening range's edge on 5- to 60-minute ranges, a trigger before the order worked being skipped, left
resting at its level (`rest`, Stage 2 D-266) or chased (`vendor/stage2/config/orb5_grid.yaml`); ORB6's hypothesis was
a limit at the broken edge (D-277, D-278); both are inside the 08:30 opening-range branch Stage 2 closed for good
(D-275, D-281). Stage 2's atlases read the prior day's high and low (`pdhl`) as a breakout entered at the market after
the first close beyond it -- five bars late, followed and faded (families A1 to A3; D-460 declared the pattern core and
A1) -- and against its coin twin
at delays of zero and five minutes (A4, D-550). What this family adds is narrower: **resting orders at four
pre-session levels other than the opening range, live from the US open and filled at the level itself.**

**Why a resting order.** A ticket written at least five minutes before it can trigger moves the operator's latency
(D-266) from the fill to the placing of the order, so the order fills at its level, not five minutes after it.

**Whose accounts.** One user's own accounts, each its own trades, one position at a time across the firm (Stage 2
D-157, D-429; E-012 (3)). F-01's "the form suits a signal service" is dropped: users placing the same tickets would be
coordinated trading under Topstep's prohibition (E-007 (c)). Every order is placed by hand; no automated or API entry
(the operator's rule, E-008).

**What would make it worth something.** Its lift in win probability over the coin at the same fills, times how often
it fires, times what a win is worth where it is used (the value map, section 10) -- judged first on its trades
(E-008), with the user's journey reported beside (section 12).

## 2. Prior exposure: what has already read these bars, these levels and this mechanism

A pass on the judged block is worth only what the block's freshness allows. These are the reads that touch this
family's levels or its mechanism on NQ's development window.

| read | what it read | span | what it recorded | bearing here |
|---|---|---|---|---|
| ORB1 to ORB6 (Stage 2 D-275, D-277, D-278, D-281) | the 08:30 opening-range breakout: a stop at the range's edge (skip, rest, chase), a limit retest at the broken edge | NQ development | the branch closed for good; whether a later hypothesis is "genuinely different is the operator's call" (D-281 (3)) | `or30`, and every opening range, is out (E-007 (b)) |
| atlas families A1 to A3 (D-460; `config/atlas_a1.yaml` to `a3.yaml`) | `pdhl` (the prior day's 08:30-15:10 CT high and low, the first close beyond) followed and faded, five bars late; `orb_rth5/15/30`; and P-13/P-14's `brk30` | 2020-01-01 to 2026-07-16 | P-14 (A3-BRK30-CB20) chosen from A3 | `pd`'s break and fade were read at the market; this family enters at the level |
| A4, the coin-benchmarked atlas (D-550, D-555, D-557, D-558) | `pdhl` among 34 patterns at 25 and 37.5 points, delays 0 and 5, lift over the coin twin, follow and fade one test | 2020-01-01 to 2026-07-16 | survivors "short breakouts and n-bar runs", all on the follow side (D-555); "a genuine but tiny direction effect" with no campaign value (D-558) | `pdhl`'s own row is in `results/a4_coin_atlas.csv`, not vendored: its sign is not known here |
| program S (D-578, D-580, D-588, D-589, D-592) | the side of recent breakouts and momentum followed, on P-16's schedule | 2020-01-02 to 2026-07-16, span guard on 2020-2023 and 2024-2026 | weak in 2020-2023, strong in 2024-2026; "re-testing it on that window would reuse hypotheses already seen, so it is recorded as a lead for unread data" (D-592) | a `break` cell loads on this effect: section 9.2 |
| Stage 2's effect atlas (`config/effect_atlas.yaml`, H01 to H04, F01 to F02) | the overnight return's and the previous close's location against the day's move | Stage 2's development | returns, not levels | named for completeness |
| program U, nine families (`results/u_budget.csv`, `u_resolve.csv`) | P on start days from 2024 | judged block of starts | all closed below P-14 | the judged block has been read for P nine times |
| P-05, P-06, P-10 (`config/windows.yaml`) | the confirmation reads of 2025-07-01 to 2026-07-16 | that window | development since D-461: "a new NQ model may be built on it, never confirmed on it" | inside this family's judged block |
| this repository | F-01, withdrawn before any read; its walker (E-010, E-011) computed no level and no outcome but P-16's identity | -- | -- | no read of these levels exists here |

**Not found:** no Stage 2 decision row or configuration reads the overnight high and low, the prior close or round
numbers as price levels (searched `vendor/stage2/DECISIONS.md` and `vendor/stage2/config/` for "prior close",
"overnight", "round number", "prior day" and `pdhl`, 2026-11-15). **The drafter's own reads:** the vendored
`results/u_value_map.csv`, section `records_leaf` (the leaf names' R), to class R = 2 and 2.5 (section 6.2) -- a
Stage 2 input; no bar.

**What follows.** (1) The judged block is late development, not out of sample (D_protocol P-3): a pass is a
development finding whose evidence is its confirmation (section 14). (2) `or30` is out. (3) A `break` cell's plain
lift alone would re-test D-592's lead on the window D-592 closed to it, so a break cell passes only if its lift also
exceeds that of matched non-level crossings (section 9.2). (4) The reverse walk-forward and the lift by year are
reported with every judgement (section 9.6).

## 3. Contract fit: the constraints each cell lives inside

| constraint | how the family meets it |
|---|---|
| latency at least 5 minutes (Stage 2 D-266) | every level and every side from bars stamped at or before `t_pub - 1 min`; the order works from `t_live = t_pub + 5 min`; nothing fills before (section 4) |
| one position per firm, 5 minutes flat (D-429) | stages A to C read every fill independently; stage D routes by the strict rule, with cancel-on-entry (section 11) |
| every trade resolving: at most 5 % to the flatten, overall, per market and per year, no time stops (D-212 (2) as D-308 (3) raised it) | the cutoff rule and K2 (7.1); C3 on the judged block (9.4) |
| realised risk matching intended: at least 90 % of trades realise at least 90 % of the state's risk in whole micros (D-212 (1)) | cannot fail in the walk (K3, 7.4); a floor on the tickets' trades in stage D (11.1) |
| stop band and cost floor (`vendor/stage2/results/stop_band.csv`, 45 ticks) | stops of 50, 100 and 150 ticks, all above the floor (6.3) |
| news | every ticket goes live at 08:30 CT: on a BLS 08:30 ET release day strictly after 07:35:00 CT (E-007 (d)) and outside Topstep's Tier 1 windows (07:25-07:35 CT on CPI, NFP and PPI days; around both FOMC events; E-007 (6), `docs/audits/phase0/E_rules_currency.md` C1); FOMC days carry no tickets; tickets rest through other 09:00 CT releases, as Stage 2's rule allows (D_protocol N-6) |
| conduct, tier 1 (D-145) | no hedge (cancel-on-entry: never two positions in the firm, 11.3); no simulator-fill exploitation (stops of at least 50 ticks, no stop move); no maximum size into news (above); no copying (each ticket on one account, D-157); nothing concealed (a resting order at a public level) |
| conduct, tiers 2 and 3 | tier 2: the R = 1 cells meet "R at or below 1"; modelled off in the base case (D-289), on beside in stage D. Tier 3 priced: 0 % denial in the verdict, 10, 25 and 50 % beside; Terms of Use s.8 (outsized positions) priced among them (E-013 (1)) |
| hours | US regular hours: tickets live from 08:30 CT to the cell's cutoff (at latest 14:30); the walk ends at the bar ending 15:08 CT |
| entry by hand | the user places the ticket between `t_pub` and `t_live` (E-008) |
| firm rules | only rules verified in `vendor/stage2/config/rules.yaml` or `config/rules_extended.yaml` |

## 4. Time, data and calendar (D-5, D-11)

1. **The clock.** Stage 2's bars carry their **open** time (`vendor/stage2/data/README.md`: `ts`, "Bar START"): the
   bar stamped 08:24 covers 08:24:00-08:24:59 and closes at 08:25. Times are US/Central.
2. **Publish.** `t_pub` = 08:25 CT. Every level and every side reads only bars stamped **at or before 08:24** (closed
   by 08:25). The **reference price** `P_ref` is the close of the last bar stamped at or before 08:24 of that trading
   day; with none, every kind is void that day.
3. **The side, fixed at `t_pub` and never re-read.** A level above `P_ref` is a resistance, below it a support; a
   level exactly at `P_ref` is void (counted) -- except `on`, whose high is a resistance and low a support by
   construction (they bracket `P_ref`).
4. **Live and void.** `t_live` = 08:30 CT: the order works from the bar stamped 08:30, and "a bar after `t_live`" is a
   bar stamped at or after 08:30. At `t_live` the price is the close of the bar stamped 08:29 (the last closed by
   then; the walker's `price_at`): a stop already at or through its price, or a limit already at or beyond its price,
   is **void** for the day (skipped, counted). A bar stamped 08:30 or later that opens beyond a stop fills at its open
   plus the slippage (a gap through); one that opens through a limit fills at the limit's price, never better.
5. **Calendar voids, each counted.** Roll days (the bar store's manifest `rolls`; the charted contract changes on the
   Tuesday of expiry week, P-14 caveat C4) void `pd` and `pdc`, whose prices would be the old contract's. The seam days
   2025-06-30 and 2025-07-01 (P-14 caveat C2) void every kind. A trading day ending before 15:00 CT (P-14 caveat C5)
   voids every kind, and the next trading day voids `pd` and `pdc`. The first trading day in the store voids `pd` and
   `pdc`. FOMC days carry no tickets.
6. **The test** (section 17, item 3): every level, side and `P_ref` is unchanged when every bar stamped at or after
   08:25 is replaced.

## 5. The grid and the walk

### 5.1 Levels (each frozen at `t_pub`)

| kind | the level(s) | tickets a day |
|---|---|---|
| `pd` | the prior regular session's high and low: the bars stamped 08:30-14:59 CT of the previous trading day | 2 |
| `on` | the overnight session's high and low: the bars stamped 17:00 CT the evening before to 08:24 CT | 2 |
| `pdc` | the prior regular session's close: the close of its bar stamped 14:59 CT (void when that bar is missing) | 1 |
| `rn100` | the nearest multiples of 100 points of the futures' own price above and below `P_ref`; when `P_ref` is exactly a multiple, the multiples 100 points above and below it | 2 |

### 5.2 Side rules (order types)

| rule | at a resistance | at a support | fill |
|---|---|---|---|
| `break` | buy **stop** one tick above the level | sell **stop** one tick below | the first bar stamped at or after `t_live` trading at the stop's price; at that price plus one tick (`slip_ticks`, `vendor/stage2/config/atlas_a3.yaml`; D-95), or at the bar's open plus one tick when it opens beyond the stop |
| `fade` | sell **limit** at the level | buy **limit** at the level | only when a bar stamped at or after `t_live` trades **through** the level by at least one tick; at the limit price, never better |

### 5.3 Per ticket

One ticket a level a day. It fills at most once and is never re-armed. Unfilled, it is cancelled at its cell's
**cutoff** (7.1): it fills only on bars closing at or before the cutoff. When both levels of a kind fill on one day,
both fills count in stages A to C; stage D takes them by the strict rule.

### 5.4 The walk

This repository's walker (`extended/walker.py`; its identity with Stage 2's walk holds, E-011) with this family's
preset, built after the pin: **the walk's last bar is the bar ending 15:08 CT; a trade still open there is flattened
at the worst of the bars ending 15:08-15:10 CT less two ticks** (Stage 2's `fv3_rung_walk` convention, `STAGE2`'s
`walk_end` and `flatten`; D_protocol N-3); **no stop move** (`breakeven` off: section 6.2). From the fill: the stop at
S ticks is reached by a touch; the target at floor(R x S) ticks is reached by a trade through it by a tick; on a bar
reaching both, the stop. Costs: Stage 2's per-contract cost at the stop (`atlas_a3.fee_by_stop`;
`vendor/stage2/config/fills.yaml`), no entry tick on a resting fill (a stop's slippage is in its price), a tick on a
stop exit, none on a target, two on a flatten (with Stage 2's two in the flatten price, as its scorer does, E-010 (3)).

### 5.5 The pair, the fill bar and the booking (D-1, D-13)

For every fill, the **mirror** is the opposite side at the same fill bar, with the same stop, targets and walk,
**booked symmetrically about the trigger** (`mirror_booking="symmetric"`: the mirror at 2 x trigger less the rule's
fill, paying the rule's offset in its own direction). The **trigger** is the first price the bars show at the fill
condition: a stop's price on a touch, or the open on a gap; a tick through a limit's price, or the open when a bar
opens through it. **The fill bar is settled by the pair rule** (`fill_bar="pair"`): if the fill bar touches either
trade's stop or target, the pair is **ambiguous**. Both trades are then booked as stopped losses (costed as stops), the
pair contributes zero lift, and it is counted (K5). Otherwise both trades are walked from the next bar, and the fill
bar is not read. On a tick-continuous driftless walk this settlement is side-neutral by construction (the four
barriers lie symmetric about the trigger); `tests/test_walker_t13.py` holds it there, and holds F-01's declared rule
failing (E-010 (3)).

### 5.6 The lift (the estimand of every stage)

The pair term is **w = 1/2 [win(rule) - win(mirror)]**, in win probability. A win is the target reached; a flatten or
an ambiguous pair is not a win. **lift(c, R) = the mean of w over all the cell's fills in a block**, ambiguous pairs
included as zero (D-14: the mean over fills, not over block means). The net R lift, 1/2 [net R(rule) - net R(mirror)],
is reported beside.

**Break and fade at one level are near-exact negatives.** A buy stop a tick above a resistance and a sell limit at it
fill on the same trigger (a trade at the level plus a tick); under symmetric booking they form the same pair with the
labels swapped. Their lifts differ only on gap fills (the stop fills at the open plus a tick, the limit at its price)
and on a day the price at `t_live` stands exactly at the level (the limit void, the stop live). So the 24 cells are 12
two-sided (kind, stop) questions, read with a sign. Both are counted, and stage B's maximum covers their dependence
(E-003 (d)).

### 5.7 The coin twin beside

A seeded coin twin -- one fair side per fill, drawn in date order of the fills, cell by cell in table order, seed
**20261931** -- is computed beside, as Stage 2 does. It decides nothing.

### 5.8 The placebo (decisive for `break`, section 9.2; beside for `fade`)

The placebo measures the same statistic at prices that have no visible meaning, so as to separate the level's
effect from what any crossing carries (D_protocol 1.3 item 4).

- **Range.** `A_D` is the mean, over the 20 trading days before day D, of the regular session's range (the high of
  the bars stamped 08:30-14:59 less their low). It reads past days only and is roll-free (a range inside one day).
- **Day pairing.** In each calendar year of a block, the days on which the kind is not calendar-void and `A_D` is
  defined are paired by a random derangement π (a permutation with no fixed point, drawn by reshuffling until none
  is fixed). There are five replicates j = 0..4, replicate j drawn by `numpy.random.default_rng([20261932, j])`.
- **The placebo ticket.** Every ticket of the kind on day D (distance d ticks from `P_ref`, side +1 for a
  resistance, -1 for a support) gives a placebo ticket on day π(D). It is placed at `P_ref` of π(D) plus side x
  max(1, round(d x `A_π(D)` / `A_D`)) ticks, with the same side rule, stop, R, `t_pub`, `t_live`, cutoff, void rule,
  walk and booking.
- **Coincidences.** A placebo price that happens to lie near a real level on π(D) is kept. That moves the placebo
  toward the level's own lift, which is conservative for a pass.
- **Placebo cells.** There are 24 (one per cell). They are controls, not hypotheses. Their fill counts and K5 shares
  are read with stage A.

## 6. Parameters: fixed, searched, dropped (D-15)

### 6.1 The table

| parameter | what it is | class | value | source or reason |
|---|---|---|---|---|
| market, bars | the data | fixed | NQ 1-minute bars, Databento GLBX.MDP3 `ohlcv-1m`, raw prices, one contract a day | E-002; `vendor/stage2/data/README.md` |
| development window | the days read | fixed | 2020-01-02 to 2026-07-16 | CHARTER; `config/windows.yaml` |
| choice and judged blocks | where the pick is chosen, where it is judged | fixed | 2020-01-02 to 2023-12-29; 2024-01-02 to 2026-07-16 | CHARTER section 3; feature-rules 4 |
| level kinds | which prices | searched | `pd`, `on`, `pdc`, `rn100` | F-01's, less `or30` (E-007 (b)) |
| side rules | break or fade | searched | `break`, `fade` | F-01 |
| stops | the stop distance from the fill | searched | 50, 100, 150 ticks (12.5, 25, 37.5 points) | P-14's two rungs and P-16's stop; above the cost floor; 6.3 |
| R | target over stop | searched | 1, 1.5, 3 | the table's main asks (handoff 2.5; `u_value_map.csv` `records_leaf`); 6.2 |
| `t_pub`, `t_live` | publish and live times | fixed | 08:25 and 08:30 CT | D-266 (five minutes); the US open |
| `P_ref` | the price that sets each ticket's side | fixed | close of the last bar stamped at or before 08:24 | D-5 |
| void rule | an order already through at `t_live` is skipped | fixed | price at `t_live` = close of the bar stamped 08:29 | F-01; the walker's `price_at` |
| stop slippage | ticks paid on a stop entry | fixed | 1 tick (a ladder of 2 and 4 beside) | `atlas_a3.yaml` `slip_ticks`; D-95; D-13 |
| limit fill | when a limit fills | fixed | a trade through the level by at least 1 tick, at the limit's price | feature-rules 3 |
| target rounding | target ticks | fixed | floor(R x S) | Stage 2's `target_ticks` |
| two-barrier bar | which barrier first | fixed | the stop | feature-rules 3 |
| fill-bar settlement | the fill bar of a pair | fixed | the pair rule | E-010; D-1 |
| mirror booking | the mirror's price | fixed | symmetric about the trigger | E-010; D-13 |
| walk end and flatten | where an open trade is closed | fixed | bar ending 15:08 CT; the worst of bars ending 15:08-15:10 less 2 ticks | Stage 2's convention (N-3) |
| costs | fees and ticks | fixed | Stage 2's at the stop (`fee_by_stop`, `fills.yaml`); exit ticks 1 / 0 / 2 | E-010; E-011 |
| cutoff | when an unfilled ticket is cancelled | fixed rule, value read on the choice block | the latest of 14:30, 14:00, ..., 10:00 CT passing 7.1 | F-01's rule, D-8's per-year line added |
| resolution ceiling | the most that may reach the flatten | fixed | 5 % overall and in every calendar year | D-212 (2) as D-308 (3) raised it |
| K1 supply | the fewest fills | fixed | 100 on the choice block and 12 in every calendar year of it | F-01; the value map's smallest use count |
| K5 ambiguity cap | the most unsettleable fill bars | fixed | 5 % of fills | the share D-212 lets fall to the flatten; a measured lift then speaks for at least 95 % of a cell's trades |
| calendar voids | days with no ticket | fixed | 4.5's list | D-11; P-14 caveats C2, C4, C5 |
| `rn100` spacing | the round number | fixed | 100 points, in the futures' own price | F-01; D-11 |
| placebo | the control for break | fixed | 5 replicates; derangement within a calendar year; distance scaled by `A_D` (20 days) | D_protocol 1.3 item 4; 5.8 |
| stage B bootstrap | the family-wise gate on the choice block | fixed | stationary, mean block 21 sessions, circular, 2,000 replicates, centred, studentised, seed 20261930 | D-14; D-550's form |
| stage C level and statistic | the pass line | fixed | one-sided 0.05 / (k (k + 1)), Q-16's calibrated statistic [Q-16] | E-008 |
| value bar | the least a pass must be worth | fixed | $500 a year at C1's bound | `u_value_map.csv` `bar`; E-008 |
| valuation bases and places | where a lift is priced | fixed | `p14` for 50 and 100 ticks, `p16` for 150 ticks; section 10's place rule | `u_value_map.csv` |
| tickets' verdict-arm bound | the shift of the tickets' outcomes in stage D | fixed | one-sided 95 %, Student-t on 21-session block means, the lower of the two blocks' bounds | CHARTER section 2; D-271 (1); M5 |
| stage D base, routing, seed | the campaign floor and the scorecards | fixed | section 11; campaign seed 20261935, 500 paths | E-008; D-3 |
| hours | when tickets rest | fixed | 08:30 CT to the cutoff | E-003 (b) |

### 6.2 Dropped, and why

- **`or30` and every other opening range (5, 15, 60 minutes):** inside Stage 2's closed branch, whose reopening
  D-281 (3) reserves to the operator; the safe default (E-007 (b)) keeps it out.
- **Frozen session-VWAP bands and prior swing points** (the bootstrap's family A list): each needs its own window and
  multiplier, or its own swing definition -- a search of its own -- so each is a later family.
- **R = 2 and 2.5:** a small minority of the table's recorded trading leaf-days in every phase of both bases
  (`u_value_map.csv`, `records_leaf`), and on the same fills their barriers nest between R = 1.5 and R = 3, so they
  would add hypotheses with little new information. **R = 0.25** (in Stage 2's offered menu, D-526) is not a leaf R
  of either $50K table.
- **Round-number spacings other than 100:** one spacing fixed. Another would be a searched parameter.
- **Other publish times, or a re-published ticket during the session:** `t_pub` 08:25 is the one time at which all
  four kinds are known before the US open.
- **The breakeven stop move:** this family measures direction after the fill at fixed barriers. Stage 2's move would
  add a third outcome, and its two modelling defects (zero latency at the open; the target-first tie) are open
  (E-012 (2), Q-20). The move is allowed as made (E-013 (2)) and stays in the base's own trades in stage D, as
  registered.
- **Time stops:** none (D-212).
- **Other sessions:** US regular hours only (E-003 (b)).
- **F-01's walk end at 15:10 with the close as the flatten price (`DECLARED_F01`):** replaced by Stage 2's convention
  (5.4).
- **The signal-service distribution:** E-007 (c).

### 6.3 The 12.5-point stop, re-argued from what D-527 says (A, MINOR 2)

F-01 left the 12.5-point stop out because "it loses to costs (D-527)". D-527 (3) says something narrower: at the
12.5-point rung "costs are a larger share of the risk: the all-day, Asia and London cells clear the line far below
P-14, and the US-hours cell is killed". That is about a coin re-entering when flat all through a window, judged by
its campaign's growth at the bound. It is not about a level's direction.

This family's pass line is the lift in win probability over the coin twin at the same fills, and that lift carries no
cost: both trades of a pair pay the same one. Costs enter only where this family prices the lift (section 10) and
where it reads the gate floor (section 11). In both places R\* = P-14's own table already trades the 12.5-point rung:
the value map's base `p14` holds both of P-14's rungs. The stop is above the cost floor
(`vendor/stage2/results/stop_band.csv`, 45 ticks). **So the 12.5-point stop is admitted as a cell.**

Its known weakness is resolution on one-minute bars. At 50 ticks a fill bar touches a barrier more often, most of all
at the 08:30 open. K5 exists to catch exactly that, so it is no reason to leave the stop out unread.

## 7. Stage A: the gates, before any outcome

Read on the **choice block only**. The inputs are fill, void and touch counts and the barrier kinds (target, stop,
flatten, ambiguous), **pooled over each rule trade and its mirror**. The pooled reading is symmetric under a
reflection of the price path: it shows how far prices travelled, never which way. No lift is computed.

1. **The cutoff rule and K2, resolution (D-8 corrected).** A cell's cutoff is the latest of 14:30, 14:00, 13:30, ...,
   10:00 CT such that, over its fills before it, the pooled unresolved share (flattened at the walk's end) is at most
   5 % at every R in {1, 1.5, 3}, **overall and in each calendar year 2020 to 2023**. With no such time the cell is
   killed (K2). Fills after the cutoff are dropped (the ticket is cancelled at the cutoff).
2. **K1, supply:** at least 100 fills on the choice block after its cutoff, and at least 12 in each calendar year.
3. **K5, ambiguity (D-1).** A (cell, R) whose share of ambiguous pairs among its choice-block fills exceeds 5 % cannot
   be measured on one-minute bars, and it is killed. A cell with every R killed is killed. The share by year is
   reported. The share does not depend on direction (the four barriers lie symmetric about the trigger).
4. **K3, realised risk (D-9).** D-212 (1) cannot fail in this walk: a stop exit books exactly S ticks plus a tick of
   cost, and a gap adds nothing (Stage 2's convention). It is recorded as not applicable in stages A to C. Its
   substantive form -- whole micros at the table's risk -- is a floor in stage D (11.1).
5. **K4, fill realism (reported, never a kill; direction-free parts only):**
   - for `fade`, fills over touches (a touch is a bar reaching the level without trading through it);
   - for `break`, the share of fills that gapped;
   - for both, the share of fills in the first five minutes after 08:30 and on fill bars spanning a quarter of the
     stop (D-13).

   K4's outcome part -- the outcome of touched-but-unfilled `fade` tickets, i.e. the limit fill's adverse selection
   -- reads direction. It is computed with stage B (choice block) and stage C (judged block), beside (D-10).
6. **The placebo cells:** their fill counts and K5 shares, read here.
7. **Planning (D-4), from counts only, written before stage B reads anything.** For every surviving (cell, R):
   - its choice-block fills;
   - its judged-block fills, **estimated** as the choice-block rate per session times the judged block's sessions (no
     judged read, D-10);
   - the **minimum detectable lift** at the family's level with 80 % power, from Q-16's power curve for its
     calibrated statistic at that count [Q-16], with the worst-case-sd Student-t formula beside (D_protocol
     Appendix C);
   - for break cells, the same for the placebo-differenced lift;
   - **the value bar in points** at the cell's uses and best place (section 10) -- the lift whose price at the bound
     is $500 a year -- and the ratio of the two.

   Every figure goes to the result file's `planning` section; none is typed anywhere. A close at stage B or C is
   recorded against this MDL (section 13). R-16 (declare a screen, or pool, when the ratio is large) is a proposed
   protocol row, not adopted, and is not applied here.

Every cell killed: the family closes at stage A.

## 8. Stage B: choose on the choice block

For every surviving (cell, R), on the choice block:

1. **The statistics.** The lift L (5.6). For break cells also **D = L - L_placebo**, where L_placebo is the mean of w
   over all fills of the five placebo replicates (5.8).
2. **The bootstrap.** A stationary bootstrap (Politis and Romano) of the choice block's sessions in date order,
   circular, with mean block 21 sessions, **2,000 replicates, seed 20261930**. Each replicate is one draw of session
   indices, shared by every (cell, R) and by the placebo fills, so their joint dependence is kept. A replicate's lift
   is the resampled sessions' summed w over their summed fills (D likewise). A statistic's standard error is the
   replicates' sd. The studentised statistic is t = L / se; a centred replicate is t\*_b = (L\*_b - L) / se.
3. **The decisive statistic** T(c, R): for `fade`, t_L; for `break`, the smaller of t_L and t_D (and the same for
   each replicate).
4. **The family-wise critical value** q: the 95th percentile, over replicates, of the maximum of T\* over every
   surviving (cell, R) -- one-sided, family-wise 0.05. Benjamini-Hochberg at 10 % on the per-hypothesis bootstrap
   p-values is reported beside and never selects.
5. **Kill B.** If no (cell, R) has T above q, the family closes and the judged block is not read.
6. **The pick.** Among the (cell, R) above q: the largest **valued lift** (section 10) at the lower limit L - q x se
   (the plain lift, for both side rules), with uses = the choice-block fills a year. A tie (equal to the dollar) goes
   to the one with more choice-block fills, then to the first in table order (5.1, 5.2, stops ascending, R
   ascending). There is one pick.

Stage B is a gate, not a claim (D_protocol N-1): it spends nothing of the program's budget. Its calibration bears on
which pick is judged, not on stage C's error rate.

## 9. Stage C: judge the pick on the judged block (the pass line, E-008)

The pick alone, with its cutoff and every rule as fixed in stages A and B, on fills from 2024-01-02 to 2026-07-16.
**C1 to C4 must all hold; any failure closes the family.**

1. **C1, direction.** The pick's lift (5.6) on the judged block has a one-sided lower bound at **0.05 / (k (k + 1))**
   (0.05 / 132 at k = 11) **above zero**, by Q-16's calibrated statistic **[Q-16: its name, module and commit]**,
   applied to the mean over all the pick's judged fills, with sessions clustered as Q-16 calibrated it.
2. **C1', the level beyond a crossing (break picks only; D-2, D-592).**
   - **The line.** The placebo-differenced lift D on the judged block has its lower bound at the same level above zero.
   - **How it is computed.** The same statistic is applied to the per-session sums
     z_s = (sum of w over level fills on s) / n_level - (sum of w over placebo fills on s) / n_placebo.
   - **Why it costs nothing.** It is an intersection with C1 at the same level, so there is no extra spend and no
     further division.
   - **What a C1-only pass means.** A break pick passing C1 but not C1' is recorded as D-592's follow effect seen
     again: a lead for unread data, not a finding.
   - **If Q-16 does not cover this form.** If Q-16's calibration does not cover this two-sample form, the pin waits
     for one that does, or a revised draft drops `break` before the pin. That is never decided after a read.
3. **C2, value.** The valued lift (section 10) at C1's lower bound is at least **$500 a year**, with uses = the smaller
   of the choice-block and judged-block fills a year.
4. **C3, resolution (a floor, E-008 "every offered R resolving").** On the judged block, the pick's rule-side trades at
   its R leave at most 5 % unresolved, overall and in every calendar year (2024, 2025, and 2026 to 07-16). A calendar
   year with fewer than 63 sessions in a window is pooled with the adjacent year (D-604's stub-year point; it does not
   bind on these blocks).
5. **C4, measurability.** K5 on the judged block: the ambiguous share is at most 5 %.
6. **Beside, deciding nothing:**
   - the lift by calendar year on each block;
   - the reverse walk-forward: stages A to C with the blocks swapped and their own cutoffs, its bootstrap
     `default_rng([20261934, 0])` and its statistic's draws `[20261934, 1]`;
   - the seeded coin twin (20261931);
   - the net R lift;
   - **drift (D-12, D-271 (5)):** the lift on long-rule fills and on short-rule fills, and the side-balanced lift
     (their mean);
   - the placebo-differenced lift for a fade pick;
   - Benjamini-Hochberg;
   - K4's adverse selection;
   - **the booking ladder (D-13):** (a) symmetric booking at 2 and 4 ticks of stop slippage; (b) the overshoot
     reading -- the mirror booked at the rule's fill (`rule_fill`) at 1, 2 and 4 ticks, i.e. the lift if the market
     at the fill had stood that many ticks past the trigger. Symmetric booking about the visible trigger does not
     remove a fast-market overshoot, which favours `break`; this reading bounds it;
   - the share of fills in the first five minutes after 08:30.

## 10. The valued lift

The value map's own first-order formula (`vendor/stage2/results/u_value_map.csv`, definitions `extra_win_prob_points`
and `mean_dv`): **$ a year = λ x min(u, cap) x mean_dv / 100**. Here λ is the lift in percentage points at the bound
in question, u the cell's fills a year, and mean_dv the place's.

- **The base.** `p14` for 50- and 100-tick stops (P-14's rungs), `p16` for 150 ticks.
- **The value.** The **maximum over the places that ask the cell's R** of λ x min(u, cap(p, R)) x mean_dv(p) / 100.
  - **Where each figure comes from.** `mean_dv(p)` and `trades_per_year_forward(p)` come from section `place_values`.
  - **The cap.** cap(p, R) = `trades_per_year_forward(p)` x σ(p, R), where σ is the share of the place's phase's
    recorded trading leaf-days whose leaf R is the cell's R. It is computed from section `records_leaf`, over the
    leaves whose names end in an R.
- **The places.**

  | place | phase | R it can price | σ |
  |---|---|---|---|
  | (b) the evaluation | `combine` | any R | as defined above |
  | (c) the funded opening | `funded` | R = 3 only | 1 (the table's opening ask, handoff 2.5) |
  | (d) funded later | `funded` | R = 1 and 1.5 | over the whole funded phase, the opening's days in the denominator (conservative) |
  | (e) paid | `paid` | any R | as defined above |

- **What it corrects.** F-01 mapped each R to one place. In fact the table asks 1R and 1.5R on funded and paid accounts
  alike, and 3R at the funded opening (A's NOTE; `records_leaf`).
- **How it is read.** The table is held fixed. The value is read as a ranking and a bar, never as a forecast; it is
  "unreliable far from zero" (handoff 2.7; D_protocol N-4).

## 11. Stage D: the campaign -- E-008's floors, and the scorecards beside

Stage D runs whenever stage C has been read. When C1 to C4 hold, its floors decide. When the family has closed at C,
the floors decide nothing, and stage D gives only the scorecards, beside the close (E-008: the scorecard beside every
judgement). A close at A or B reads no judged block, so it has no judgement and no stage D.

### 11.1 Its role

Kept, not dropped, because E-008 binds the floors -- the long-run gate, verified rules, conduct tier 1 -- and requires
the user scorecard beside every judgement; a gate is read only on a campaign. **The floors here can close the family;
nothing here can carry it.** Floors:

- (i) the gate: growth on the required bankroll at the bound **above zero** (Stage 2 D-145), at the fresh seed;
- (ii) realised risk on the tickets' trades (D-212 (1));
- (iii) every rule verified;
- (iv) conduct tier 1 true of the routing (11.3).

F-01's verdict by D-621 (3) against R\* is gone (E-008).

### 11.2 The design

**The base, by the pick's stop** (the table its valuation used, D-3 item 3):

- **50- and 100-tick picks: P-14.** That is A3-BRK30-CB20 with its schedule and table, five Topstep $50K seats, the
  no-closure table and at most 20 purchases in 21 sessions.
- **150-tick picks: P-16** (`rc_s150_all_nr`).

The base's own trades, walk, coin, cuts and table are unchanged. The pick's tickets are added as follows.

- **Published and placed.** A ticket is published at 08:25 on every day its kind has one (5.1; voids as 4.5). It is
  placed at 08:30 on one account: the first, in the router's order, whose state's table leaf that session asks **the
  pick's R**. That account is **reserved** while the ticket rests: the base routes no offer to it.
  With no such account there is no ticket that day (counted).
- **A busy firm at 08:30.** If the firm holds a position at 08:30, or closed one in the last five minutes, the ticket
  is placed once the firm has been flat for five minutes (void if already through by then).
- **Cancel on entry.** Before any base entry on another account, the resting ticket is cancelled. It is re-placed five
  minutes after that trade's exit (the strict rule's gap), void if already through, and never after the cutoff.
- **A fill.** A ticket's fill takes the firm's one position. The base's offers are refused until five minutes after
  its exit (D-429).
- **Two tickets of a kind on one day.** Both rest on the reserved account. The first fill cancels the other, which is
  re-placed five minutes after the exit, as above.
- **Size.** By the table, in the reserved account's state, at the pick's stop and R: whole micros under the allowance
  (D-212 (1)).

### 11.3 Conduct

Every step is realisable by hand: a resting order placed, cancelled and re-placed. The firm never holds two
positions, so never opposite positions across accounts (tier 1). Each ticket rests on one account (D-157).

### 11.4 The tickets' verdict-arm bound (M5)

The tickets' trades enter the campaign with each R's outcome shifted to the one-sided 95 % lower bound of its mean
net R -- the charter's verdict arm.

- **Which trades:** the pick's own rule-side trades at its R, walked as in 5.4-5.5 (ambiguous fills as stopped
  losses), after its cutoff.
- **Which block:** each block separately (2020-01-02 to 2023-12-29, and 2024-01-02 to 2026-07-16), by Student-t on
  21-session block means (the handoff's convention).
- **Which era rule:** **the lower of the two blocks' bounds** -- D-271 (1)'s rule, applied without its test, so no era
  test and no seed is needed.
- **How it is applied.** The shift is lb - e, as Stage 2's gate applies it (`propedge.campaign.gate.shifted_blocks`).
  The base's trades keep their registered shifts. The two streams are shifted separately, then merged into one day log.

### 11.5 The runs

1. **The identity first, refusing (T-15).** With no tickets the runner must reproduce:
   - the base's registered gate paths (P-14: `vendor/stage2/results/a3_brk30_cb20_gate_paths.csv`; P-16:
     `rc_s150_all_gate_paths.csv`), on E-002's columns to E-002's tolerance;
   - U1's start rows (`results/user_journey.csv` section `start`, by E-010 (2)'s comparison).

   A failed identity stops the family.
2. **The gate.** Stage 2's `gate` call as the base registered it: rotation, its horizon, 500 paths, **campaign seed
   20261935**, 0 % denial, the placement off. Floor (i) is read here.
3. **Beside:**
   - the base alone at the same seed (the paired difference: the tickets' own effect on the gate);
   - P-06's row;
   - denial at 10, 25 and 50 %;
   - the placement on;
   - D-663's stress readings where Q-18's tooling exists.

### 11.6 What stays unidentified (D-3), stated so the scorecards are read for what they are

1. **The base occupies the firm** at most of its offers (for P-16 at most of its marks, red team 2.10), so the
   tickets' take-up is limited. It is reported: placed, filled, cancelled on entry, voided at re-place, and refused for
   no account at the R.
2. **The reservation changes the base's routing** even when no ticket fills, so base-plus-tickets differs from the base
   by more than the tickets' trades.
3. **For a 150-tick pick**, the comparison with R\* = P-14 mixes the base's own distance from P-14 with the tickets'
   effect. The paired difference against its own base is read beside it.
4. **The judged block holds few independent starts** (E-007 (2), red team M2). Every P comparison is calibrated and
   beside.
5. **The value map's price is first-order, with the table held fixed;** the campaign's realised change can differ.

## 12. The journey scorecard -- beside every judgement, never the pass line (CHARTER section 2; E-008, E-014, E-015)

**What it is computed from.** Stage D's real-order replay over start days (the U1 form,
`vendor/stage2/docs/USER_MILESTONES.md`), on the verdict arm, for three designs:

- **base plus tickets**;
- **the base alone**;
- **R\* = P-14**, as registered.

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
4. **E-007 (e)'s readings:**
   - the denial ladder (10, 25, 50 %);
   - the placement on;
   - the binding Focused Trader models;
   - P by month;
   - mean net;
   - CVaR10;
   - P under a bankroll limit;
   - the effective sample size;
   - the minimum detectable difference, before the read.

   These come from Q-17's adapter.
5. **The paired differences** -- base plus tickets less the base (the tickets' own effect), and base plus tickets less
   R\* -- by Q-16's calibrated P comparison **[Q-16]**, one-sided at 0.05; reported, never a line. Its draws, if any,
   use seed **20261936**. D-621 (3)'s percentile bound is not computed: it does not hold its level (E-007 (1)).
6. **Limits:** E-015's limits, **once approved by the operator**, as **menu flags only**. A design crossing one is
   shown with which limit and by how much; a limit never fails a design. Until they are approved, the menu is read
   without flags, and it says so.
7. **The evenness trade-off curve** -- how much "ahead" each step of evenness costs -- reported beside, with this
   design's point and its base's, in the form E-015's menu reading fixes.
8. **Not modelled, and said so wherever this scorecard appears:** a user who stops when their own money runs out, the
   user's time, taxes.

The replay draws nothing.

## 13. What a pass and a fail mean

- **CARRIED** (C1 to C4 and stage D's floors all hold). The pick is a development finding on a late-development
  block, not an out-of-sample one. It takes a registration id (D-621 (9)'s house form), a model card, its registered
  development test, the auditor, and then **one confirmation** (section 14). The confirmation carries the decision
  (D-189).
- **CLOSED** at stage A (no cell survives the gates), B (no (cell, R) above the critical value), C (C1, C1' for a
  break pick, C2, C3 or C4) or D (a floor). The reason goes in a decision row.
  - A close at B or C is recorded as **"no lift above the MDL (planning section) at this family's level"**, never as
    "no lift at levels" (D-4). A close at C carries stage D's scorecards beside it (section 12).
  - Where a check failed, rather than a kill line, the failure protocol applies.
  - The family closes. The closure binds this specification (D-277's boundary): a later family on these levels names
    this closure, states what changed and why it is a different hypothesis (D_protocol 1.5 (c)), and is judged on
    data this family did not read.

## 14. The confirmation (M1, D-6), declared before any development read

- **The window.** NQ from 2026-07-17 (`config/windows.yaml`, `reserve`, `reserved`). It is not on disk and is never
  read until a carried candidate is registered.
  - It becomes NQ's **fourth** confirmation window only by the operator's decision (D-107; NQ's three were spent by
    P-05, P-06 and P-10).
  - It is a purchase (the operator's; stated in `docs/OPERATOR_SETUP.md` and waited for).
  - Stage 2's draft P-16 confirmation targets the same window (`vendor/stage2/prereg/DRAFT_P16_confirmation.md`). If
    any test reads it first, the lead records that before registration, and the operator decides whether it can still
    confirm this pick.
- **What it tests: the pick's trades, not P.**
  - The line: the pick's lift over its coin twin on the window's fills (every rule and its cutoff as fixed in stage
    B), one-sided at the registered **0.05**, by Q-16's statistic [Q-16], with the bound at 0.05/N beside (D-189's
    form). Its draws, if any, use seed **20261937**.
  - A break pick is also confirmed by its placebo-differenced lift. The placebo's derangements are drawn within each
    calendar year of the window, replicates `default_rng([20261932, 5 + j])`, j = 0..4.
  - C2 at the 95 % bound: at least $500 a year.
  - Resolution: at most 5 % on the window, overall and in every calendar year with at least 63 of its sessions (a stub
    year pooled with its neighbour, D-604).
  - K5: at most 5 % on the window.
- **What it cannot test: P.** A six-month window is about 126 sessions, so about 63 start days with a month-3 horizon
  left -- one 63-start block, on which no interval on P exists (the moving-block bootstrap degenerates, red team M1).
  The scorecard on the window is reported descriptively, without an interval, and is never a line.
- **How much data.** At least six months (D-604), and at least the number of months at which the pick's expected fills
  reach the count at which Q-16's statistic, one-sided at 0.05, has 80 % power for a lift equal to the pick's judged
  lower bound at the family level. The expected fills are the lower of its two blocks' rates per session x 21 sessions
  a month. The count is computed when the pick is carried and written in the carrying row, before any confirmation
  data exists. If it is more than the operator will buy, no confirmation is registered and the pick stays a
  development finding.

## 15. Seeds, fixed now and checked

| seed | what it draws |
|---|---|
| 20261930 | stage B's stationary bootstrap (choice block) |
| 20261931 | the seeded coin twin beside (5.7) |
| 20261932 | the placebo derangements: `numpy.random.default_rng([20261932, j])`, j = 0..4 on development, 5..9 on the confirmation window |
| 20261933 | stage C: the draws of Q-16's statistic, if it draws any (else unused, and the result file says so) |
| 20261934 | the reverse walk-forward beside: `default_rng([20261934, 0])` its bootstrap, `[20261934, 1]` its statistic's draws |
| 20261935 | stage D's campaign seed: the gate floor and every beside arm, 500 paths |
| 20261936 | the scorecard's calibrated P comparison (Q-16), if it draws |
| 20261937 | the confirmation's statistic, if it draws |
| 20261938 | the build's tests: the shift test's replacement walks and T-3's synthetic judged block |
| 20261939 | the build's planted-effect test (T-14) |

**The check (T-12).** On 2026-11-15, a word-bounded search of the whole working tree -- the vendored snapshot and its
results included, binary files skipped -- found 20261930 to 20261939 only in this item's brief
(`docs/briefs/Q-21_2026-11-15.md`), as the proposal. The command was `grep -rIowh --exclude-dir=.git -E
"2026193[0-9]" .`. The only other match, found without word bounds, is digits inside a floating-point value in
`vendor/stage2/results/a3_brk30_cb20_gate_paths.csv` -- not a seed.

**Inherited, and used only as their owners registered them:**

- the bases' own seeds -- P-16's coin by date and minute 20261102, P-14's identity seed 20261131 and P-16's gate seed
  20261206 (E-002);
- Q-16's calibration seeds 20261910 to 20261919 and Q-17's 20261920 to 20261929, which are theirs, not this family's.

**Not reused:** F-01's 20261901 to 20261903 (withdrawn, never run). 20261901 is also Stage 2's
`user_drivers.CLUSTER_SEED` (D_protocol N-2).

## 16. Multiplicity and the budget

1. **F-01 spent k = 10** (E-007 (a)): committed code of it existed on `wt/wt-levels` (red team M7), so D_protocol
   R-6's condition (i) failed, and the conservative route was taken. **This family takes the next free program family
   number at its pin -- 11 if pinned next, level 0.05 / (11 x 12) = 0.05 / 132.** If another family is pinned first,
   k and the level are the gatekeeper's count, and the pinning row writes them.
2. **One cell reaches judgement**, with no further division inside the family. C1' is an intersection with C1 at the
   same level. C2 is a conjunctive gate, not a claim. Stage B's family-wise test is on the choice block and spends
   nothing (D_protocol N-1).
3. **The program's honesty sentence (P-2).** Stage 2 ran programs S and U on this same window, each with its own 5 %.
   The development-stage level is a screening threshold; **the decision is carried by one confirmation on unread
   data** (D-189: "the confirmation window carries the decision, never a smaller N"). A program ledger across both
   repositories (R-1) is not built; when it is, this family is listed in it.
4. **Counted (R-17's words: "program family number k", "cells", "hypotheses"):**
   - 24 cells, each counted whether killed or read;
   - 72 hypotheses (36 up to sign);
   - 24 placebo cells, as controls, not hypotheses;
   - one campaign cell if stage D runs;
   - the reverse walk-forward re-reads the same cells.

   A later D-189 N counts these, plus section 2's Stage 2 reads of the mechanism.
5. **D_protocol 1.5's holes:**
   - (a) There is no fitted model and no hyperparameter.
   - (b) No normaliser spans the sample: the placebo's range trails 20 days, and T-3 shows the choice stages ignore
     the judged block.
   - (c) This family re-declares F-01 after a review, not after a read (F-01 read no bar). The closed branch is left
     out, and the known follow effect is met by C1'.
   - (d) No exploratory read of these levels exists in this repository. No read ledger exists yet (R-5), so the
     family's bars are read only by its runner, from a clean checkout, after the pin.
   - (e) k, as above.
   - (f) The tests, section 17.

## 17. The build's identities and tests, before any reading

All of the family's code is committed after its pin (T-9). It is all fast-tier unless marked.

1. **The walker** (E-011: P-16's `TRADES_SHA256` under `STAGE2`) holds at the build's commit. The family's preset
   differs from `STAGE2` only in the breakeven move: a test shows the preset with the move switched on is `STAGE2`
   exactly.
2. **E-002's and Q-05's identities** hold at the build's commit, and the run **refuses, never skips**, when their data
   are absent (T-11).
3. **No look-ahead** (feature-rules 2; D-5).
   - Every level, side and `P_ref` at `t_pub`, and every `A_D`, is unchanged when every bar stamped at or after 08:25
     is replaced. Replacements: a seeded walk (20261938) and a constant.
   - The days tested include roll days, DST changes, the seam and early closes.
   - The test also asserts that no level is all-NaN or constant.
4. **Fill rules on synthetic bars, under the family's preset:**
   - the void at `t_live`;
   - the gap through;
   - the trade-through;
   - one fill;
   - the cutoff;
   - every calendar void;
   - FOMC days, and report days;
   - the pair rule and symmetric booking;
   - two levels a day;
   - break and fade exact negatives, except on gaps and at the void boundary.
5. **T-13, the mirror's zero.**
   - It is read per side rule, per stop (50, 100, 150 ticks) and per R, never pooled.
   - The bars are synthetic walks whose one-minute ranges reach the stop on a declared share of bars (at least
     Appendix B's middle row).
   - The pass: `pair` plus `symmetric` covers zero, with an interval half-width under a quarter of the smallest
     `extra_win_prob_points` in `u_value_map.csv`, section `bar`, at `target=500`.
   - `declared` plus `rule_fill` stays the strict expected failure (E-010 (3)).
6. **T-14, a planted effect** (seed 20261939). The checks:
   - A continuation of known size planted at level touches is recovered, with its sign and size, by L and by D, and
     stage C's bound covers it at its level.
   - Planted at every crossing alike, it leaves D at zero within its interval.
   - A level read from the 08:25 bar is caught by test 3.
7. **T-3, choice-stage invariance.** Stage A's and B's outputs -- cutoffs, kills, planning, critical value, pick -- are
   byte-identical when every bar from 2024-01-02 on is replaced by a seeded synthetic walk (20261938).
8. **T-15, stage D's routing.**
   - With no tickets, the base's registered paths and U1's start rows (11.5).
   - Toy days for: the reservation, cancel-on-entry, re-place at exit plus five minutes, void at re-place, two
     tickets, the cutoff, and sizing in whole micros.
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
  - `results/rl2_levels.csv`, with sections `supply`, `cutoff`, `kill`, `planning`, `choice`, `judged`, `placebo`
    and `beside`;
  - `results/rl2_campaign.csv` (stage D: `identity`, `gate`, `beside`);
  - `results/rl2_journey.csv` (section 12).

  Each is written with its sidecar manifest through `extended.results.write_result`, carrying:
  - `prereg_id` the family's F-id;
  - the cell and hypothesis counts;
  - every seed and parameter;
  - the sha256 of `vendor/DATA_MANIFEST_stage2.sha256` (P-4 item 6).

  They are EXPLORATORY until a carried candidate is registered.
- **The run.** Once, from a clean checkout of a named commit (`scripts/run_clean.py`), under the run lock, watched to
  its end.
  - The stages run in order -- A, B, C, then D -- and each stage's file is written before the next stage reads
    anything.
  - A kill stops the sequence.
  - A run aborted or restarted is recorded by the lead with its log, and only the first complete run is read.
- **Waits.** No judged-block read until Q-05 holds (done, E-010) and Q-16 is merged (E-008).

## 19. Open before the pin

**The lead's:**

1. Q-16's choice fills the [Q-16] marks (7.7, 9.1, 9.2, 12 item 5, 14), and settles whether its calibration covers
   the two-sample form of C1'.
2. The prereg-gatekeeper's item 6 and `.claude/skills/prereg-discipline/SKILL.md`'s selection-rule paragraph still
   name D-621 (3) as the judgement. E-008 replaced it, so as written the gatekeeper would refuse this draft there.
3. Q-17's adapter is needed for 12 item 4, and E-015's approved limits for 12 item 6.
4. Whether E-008's long-run-gate floor is read on stage D's design, as here, or taken as met by the base's registered
   PASS -- which would make stage D wholly beside. Either way it is decided before the pin.

**The operator's**, each with its safe default applied, never blocking:

1. `or30` and the opening ranges (D-281 (3)): out by default (E-007 (b)).
2. The confirmation: NQ's fourth (D-107), shared with P-16's draft; its length and its purchase.
3. The levels of E-015's limits (approval pending).

## 20. Anything chosen after seeing results

*(Empty at declaration. Anything added after a reading is exploratory, reported apart, `exploratory=True` in its
manifest, and recorded in its own decision row -- never in this file.)*
