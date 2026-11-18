# F-XX: resting orders at pre-session levels, re-declared (family RL3) -- draft

**Status: a draft, first text (Q-143). Nothing of it is built, run or read.** No bar has been read for it, no level
computed, no fill counted and no outcome of any order computed. It is pinned, if ever, by the sha256 of its LF text in
a decision row; nothing declared is edited after that, and a change is a new family under a new row.

**What it is.** The successor of F-02's resting-levels text (`prereg/DRAFT_F-02_resting_levels.md`, the seventh text,
approved by the gatekeeper under E-065 and withdrawn before any read under E-094). F-02's F-number and its k = 11 retired
with that text and are never reused (E-094 (3)(b)). F-02 failed on one thing only: its C1 decided by the one-sample
`cons`, which failed its fresh-seed validation (E-094 (1)). This text keeps F-02's grid, walk, placebo, stages and
floors. It changes what section 0 lists:
- C1 moves to the one-sample line Q-126 adopts;
- the operator's three rulings of 2026-11-18 are applied: no fill in 08:30-08:59, latency as a counted parameter, and
  limit entries as the repository's fill rule;
- the seeds are new.

At the pin the file is renamed `prereg/F-NN_resting_levels.md` and `F-XX` becomes `F-NN` on line 1 and in the table's
`id` row only; nothing else changes. The pinning row names the commit and the sha256 it pins.

**The pin's conditions -- every one must hold, or this text is not pinned and takes no k (section 19 item 1):**
1. **Q-126's adoption row exists** (`docs/calibration/Q-126_one_sample_plan_2.md`, pinned by E-187, LF sha256
   `117f5eb36dfd8312b24db35d1e6898167397fe374ae47a1feab94b5a2ebfcdc6`). It must adopt, as a one-sample line HOLDING its
   validation, a statistic for the band this family declares: **side persistence below 42 sessions**, as a **switching
   side** (5.10). That row pins `extended/lift_one_sample2.py`'s blob and names the statistic and its scope (D or Q,
   plan 2.5's first row).
   - **If Q-126 adopts nothing for that band** (plan 7 items 1-2), the family stays unpinned and takes no k. This text
     stays on record.
2. **The pre-pin power gate (7.1) passes.** It is light and reads no bar, from `results/q126_cal_power.csv` and the
   vendored value map. If no (cell, R) passes, the family closes before its pin and takes no k, as family R did
   (E-086).
3. **K0's and C0's level and power on the adopted statistic** are shown on synthetic toys at the family's level, before
   the pin (E-051's rule; Q-108's 7 item 5). The script is under `docs/research/scripts/` and uses seed
   `[20263409, 20..21]` (15).
4. **The family number k** is assigned by the gatekeeper at the pin. **Proposed: k = 14**: k = 13 goes to the
   per-firm protocol family (Q-141), and Q-126 calibrated k = 13 to 20 only (plan 7 item 5). The runner asserts that k
   lies in `lift_one_sample.K_RANGE_1S`.
5. **The lead's rulings of section 19 items 2 to 6** are recorded, each under its row.

If any of these fails, nothing of this text runs. **The judged-block reads this family may make are named on the one
line the reader requires (18.1, E-026).** Anything chosen after a reading is exploratory and reported apart.

| field | value |
|---|---|
| family | RL3: resting stop and limit orders at four pre-session price levels, judged on their trades first (E-008) |
| id | F-XX (`prereg/F-NN_resting_levels.md` at the pin) |
| program family number k | **proposed 14**, assigned by the gatekeeper at the pin (F-01 spent 10, E-007 (a); F-02 retired 11 unspent, E-094; F-03 spent 12, E-192; 13 to Q-141) |
| level | one-sided **0.05 / (k (k + 1))**; at k = 14, **0.05 / 210** |
| development data | NQ 1-minute bars, 2020-01-02 to 2026-07-16 |
| choice block | fills from 2020-01-02 to 2023-12-29 |
| judged block | fills from 2024-01-02 to 2026-07-16 |
| confirmation | NQ from 2026-07-17 (`reserve`, reserved): NQ's fourth only by the operator's decision (Stage 2 D-107), a purchase |
| cells (`k_cells`) | (`fade` at 4 kinds + `break` at 1 kind) x 3 stops x 3 latencies = 5 x 3 x 3 = **45**, each counted whether dropped, killed or read |
| hypotheses | 45 cells x 3 R = **135** signed hypotheses over 108 (kind, stop, latency, R) questions (5.9) |
| the pass statistic | the lift over the coin twin on the same fills, by **the one-sample line Q-126's adoption row adopts for side persistence below 42 sessions**, in that row's scope (5.10, 9.2) |
| the two-sample lines | C1' by `two_sample_bound` against the window-matched placebo levels (it holds, E-094 (1)) |
| the value bar | $500 a year at C1's bound (`vendor/stage2/results/u_value_map.csv`, section `bar`, `target=500`) |
| seeds | 20263400 to 20263409, each assigned in section 15 |
| model card | none: no fitted model; the grid is the family |

---

## 0. What this re-declares, and what changed from F-02's seventh text

F-02's own corrections (its sections 0.1 to 0.6) are carried: Phase 0's findings on F-01, four red-team reads, the
gatekeeper's refusal of its fifth text and the pass-line review. They stay on record in
`prereg/DRAFT_F-02_resting_levels.md` and its reviews (`docs/reviews/DRAFT_F-02_resting_levels_2026-11-15.md`, `_v3_`,
`_v4_`). Every rule they settled is restated here as it stands in F-02, unless the table below changes it.

| # | F-02's seventh text | this text | basis | section |
|---|---|---|---|---|
| 1 | C1 and C2 decided by `cons` (`lift_bound.bound`) | **C1 and C2 by the one-sample line Q-126's adoption row adopts for "below 42 sessions"**, in its scope; C1' unchanged (`two_sample_bound`, treated df) | E-094 (1), (3)(b); E-161; E-187; plan 2.5, 7 item 4 | header, 9 |
| 2 | the pin waited on Q-55 and Q-83 | the pin waits on Q-126's adoption row, the pre-pin power gate (7.1), K0/C0's toys on the adopted statistic, and k | E-094 (3); plan 7; E-051; E-086 | header, 19 |
| 3 | the sides' persistence stated as "at most one session", for `cons`'s class | **declared as plan 2.5 asks before the pin: a switching side, band below 42 sessions, with the balance limit; the band check and (in scope D) 4.4's admission run on the choice block at stage A and on the judged block inside stage C, before any outcome** | plan 2.5, 4.4; E-184; E-187 (regime-filter kind barred) | 5.10, 7.2, 9.1 |
| 4 | K0 and C0 by `cons` | K0 and C0 by **the adopted statistic** | Q-108's 7 item 5 (m4) | 7.2, 9.1 |
| 5 | tickets worked from 08:30 CT; levels and sides from bars at or before 08:24 | **no fill and no entry in 08:30-08:59 CT, nor inside any verified news window** -- the operator's ruling of 2026-11-18 (item 1), which answers what Q-142 left as a lead's ruling. **Every ticket works from 09:00 CT**, and a resting ticket is cancelled at a verified news window's start | the operator (2026-11-18, item 1); Stage 2 D-281 (3); Q-142 section 2.1 | 3, 4 |
| 6 | the alert-to-order latency fixed at 5 minutes (`t_pub` 08:25, `t_live` 08:30) | **latency L a declared, counted parameter: 5 minutes (the reference, CHARTER section 4), 3 and 2 minutes**; `t_live` = 09:00 CT for every L and `t_pub` = 09:00 - L; every variant counted in the cells, in stage B's family-wise maximum and in the hypotheses; the 5-minute sibling reported beside every pick | the operator (2026-11-18, item 2) | 4, 5.9, 8, 9.7, 16 |
| 7 | the limit fill as the walker's | **checked against the operator's statement:** a limit fills only on a trade through its price by at least one tick, at the limit price, never better; it is live from its latency after the ticket; it is cancelled at a verified news window's start. Written as a build test (T-4) | the operator (2026-11-18, item 3); `extended/walker.py`; feature-rules 3 | 5.2, 17 item 4 |
| 8 | `on` = bars 17:00 CT to 08:24 | **`on` = bars 17:00 CT to 08:29**: the whole overnight session, closed before any `t_pub` | consequence of item 5 | 5.1 |
| 9 | k = 11, level 0.05/132 | proposed k = 14, level 0.05/210; the gatekeeper's number | Q-142; the brief | header, 16 |
| 10 | seeds in F-02's two blocks | **one new block, 20263400 to 20263409**, found nowhere on any ref, worktree or the main tree by a word-bounded search (15) | E-094 (3)(b) (F-02's seeds retire with it) | 15 |
| 11 | -- | **Q-122's readings beside** (regime-bucketed, equal-weight block); **E-161's drift nulls named beside** from the adoption row | E-157 (b); E-161; plan 3.3 | 9.6 |
| 12 | -- | **a memory bound:** every heavy step at most 2.5 GB, its figure measured on the build | the machine (CLAUDE.md); the brief | 18.2 |
| 13 | a stage-D ticket placed at 08:30 | placed at its `t_pub`, live from 09:00; the reachable count read at 09:00 | consequence of items 5 and 6 | 10, 11.2 |
| 14 | rule values typed in sections 3 and 6.3 (news windows, the allowance, the stop band's edges) | cited by key or by file; the build reads them | "no typed rule value" (E-199 (S5); the brief) | 3, 6.3 |

**What is not changed** (as F-02, restated below): the four kinds, the two side rules and where each is offered; the
three stops and three R; the pair rule; symmetric booking for C1 and C1', and rung 1 for C2, with T-13 (b)'s switches;
the placebo (5.8); K1, K2, K5, K3 and K4; stage B's bootstrap and max-T; the valuation (10); stage D (11); the
scorecard beside (12); the confirmation (14); T-3, T-12, T-13, T-14 and T-15; the run order, with the refusals first.

## 1. Hypothesis

**The mechanism.** Orders cluster at prices everyone can see before the session: just beyond the prior session's high
and low, the overnight range, the prior close, and round numbers. Stop-loss and breakout stop orders beyond such a
level turn a touch into a burst of market orders in the direction of the break (a cascade). Resting limit orders at the
level absorb a touch and push it back (a rejection). Which dominates is the question.

The evidence that clustered orders at visible levels move prices comes from currency markets:
- Osler 2003, *Journal of Finance*, "Currency orders and exchange rate dynamics";
- Osler 2005, *Journal of International Money and Finance*, "Stop-loss orders and price cascades in currency markets".

For NQ the mechanism is untested here. No later test was searched for this text (Q-142 section 2.1).

**What this family can test on this window** (as F-02):
- **The rejection side (`fade`)** at all four kinds.
- **The cascade side (`break`)** at round numbers only.
  - At the two range-extreme kinds a break is also a long-window breakout. Stage 2 read that follow effect on this
    window and closed the window to it (D-592).
  - At the prior close the level's distance is the overnight move's size, which no placebo can match (F-02's final
    read, G1).
- **At the prior close** the fade always trades with the overnight move. It is judged on its trades, with no level
  claim (9.8).

**What Stage 2 did and did not do** (F-02 section 1, unchanged).
- ORB5's stop at the opening range's edge and ORB6's limit at the broken edge lie inside the 08:30 opening-range branch
  Stage 2 closed (D-275, D-277, D-278, D-281).
- Its atlases read `pdhl` as a market entry after the first close beyond it: five bars late (A1 to A3) and against the
  coin twin (A4, D-550).
- This family adds something narrower: resting orders at four pre-session levels other than the opening range, filled
  at the level itself.

**Why a resting order.** A ticket written L minutes before it can trigger moves the operator's latency from the fill to
the writing of the order (D-266). So the order fills at its level, not L minutes after a touch. **Whether a shorter L
helps** is the operator's question (2026-11-18, item 2). Here a shorter L means a ticket written from a more recent
price. It is asked by three counted latencies, every one declared now (4, 5.9).

**Whose accounts.** One user's own accounts, each with its own trades, one position at a time across the firm (Stage 2
D-157, D-429; E-012 (3)). There is no signal service: users placing the same tickets would be trading in coordination
(E-007 (c)). Every order is placed by hand; there is no automated or API entry (E-008).

**What would make it worth something.** Its lift in win probability over the coin at the same fills, times how often it
can be used, times what a win is worth where it is used (10). It is judged first on its trades (E-008), with the user's
journey reported beside (12).

## 2. Prior exposure: what has already read these bars, these levels and this mechanism

F-02's section 2 is carried whole: ORB1 to ORB6; the atlas families A1 to A4 and `pdhl`; program S (S1, S3) and its
gap rules; D-592; Stage 2's effect atlas; program U's nine families; P-05, P-06 and P-10's confirmation reads inside the
judged block. Its finding stands: **no Stage 2 decision row or configuration reads the overnight high and low, the
prior close or round numbers as price levels** (searched 2026-11-15, F-02 section 2). Added since F-02's text:

| read | what it read | bearing here |
|---|---|---|
| F-02 (E-094) | nothing: withdrawn before anything was built or read | no read of these levels exists in this repository |
| F-03 (E-095, E-192) | P-16's overnight offers and their funded 3R opening, through stage B on the choice span; the judged block unread | the choice block's P-16 openings were read for a side-free timing filter; no level of this family |
| Q-83, Q-108, Q-126 (E-094, E-159, E-187) | P-16's judged pairs, as a source of null dependence | P-16's judged outcomes have been read for calibration; no level of this family |
| the described readings RD-01 to RD-05, Q-44 and the user readings | the registered designs' trades over all start days | P-14's and P-16's judged start days have been replayed; stage D's bases are those designs (11) |
| Q-121 (E-157) | a side-free descriptive of session range and fixed-band exit times on 2023 and before | the choice block's volatility drift, described; no level |

**What follows** (as F-02):
1. The judged block is late development, not out of sample. A pass is a development finding whose evidence is its
   confirmation (14).
2. `or30` is out, and `break` at `on`, `pd` and `pdc` is dropped (6.2).
3. A `break` cell passes only if its lift also exceeds that of matched non-level crossings (C1', 9.3).
4. The pick's year-by-year readings are reported with every judgement (9.7). No reverse walk-forward (E-031 (2)).

## 3. Contract fit: the constraints each cell lives inside

| constraint | how the family meets it |
|---|---|
| latency (Stage 2 D-266; CHARTER section 4: at least five minutes from alert to order, by hand) | **L in {5, 3, 2} minutes, a counted parameter by the operator's ruling (2026-11-18, item 2).** 5 is the charter's reference; 3 and 2 are variants. Every level and side comes from bars stamped at or before `t_pub - 1 min`, and the order works from `t_live = t_pub + L` = 09:00 CT (4). The charter's text is the lead's to amend for the variants (19 item 4) |
| news (the operator's ruling of 2026-11-18, item 1; E-007 (d); E-034) | **No fill and no entry in 08:30-08:59 CT, nor inside any verified news window.** The verified windows are those the record holds under `tier1_news_events_restriction` (`config/rules_extended.yaml`, article 13613539), and any further window verified there before the pin. A resting ticket is cancelled at a window's start. It is re-written at the window's end and live L minutes later, void if already through, never after its cutoff; a ticket that filled before a window walks on (the record's rule for positions held from before a window). On a BLS 08:30 ET day no entry comes before 07:35:00 CT (E-007 (d)), which 09:00 meets by construction. FOMC days are void (4.5 (d)). The EIA releases inside the resting window are handled for full-allowance tickets in stage D (11.2) as F-02's final read's M5 ruled. USDA crop production is not modelled (12 item 8) |
| one position per firm, 5 minutes flat (D-429); one trade an account a session | stages A to C read every fill independently. Stage D routes by the strict rule: a ticket goes only to an account that has not traded that session, with cancel-on-entry (11.2) |
| every trade resolving: at most 5 % to the flatten, overall and per year (D-212 (2) as D-308 (3) raised it) | the cutoff rule and K2 (7.2); the pick's rule side on 2020-2023 (8.5); C3 on the judged block (9.5); each read with every trade's own fill-bar rule |
| realised risk matching intended (D-212 (1)) | it cannot fail in the walk (K3). In stage D the ticket is sized by the engine's own form (6.3), so it can miss only by whole-micro rounding: a build check (11.1). The charter records this allowance-capped reading (E-032 (3)) |
| the stop band (`vendor/stage2/results/stop_band.csv`, D-201 (2)) | the band's narrow edge per state is read from that file by the build. Which of 50, 100 and 150 ticks lie inside it in each state is written to the `build` section and reported beside (6.3). No edge is typed here |
| conduct, tier 1 (D-145) | no hedge (cancel-on-entry: never two positions in the firm); no simulator-fill exploitation (stops of at least 50 ticks, no stop move, limits need a trade-through); no maximum size into news (the closed window, the news windows above, and 11.2's EIA rule); no copying (each ticket on one account, D-157); nothing concealed (a resting order at a public level) |
| conduct, tier 2 (D-145; `vendor/stage2/propedge/campaign/conduct.py`) | each pattern modelled off in the base case (D-289) and on beside in stage D's placement-on arm (11.5): (1) R at or below 1 (`conduct.MIN_RR`); (2) an account-deciding funded position (`MAX_FUNDED_RISK_FRACTION_OF_DRAWDOWN`); (3) maximum position on most trades, with the share of the pick's tickets at full allowance reported; (4) several accounts at the MLL in a day, a campaign pattern, with its share of days reported. Each is stated for the tickets and for the bases as F-02's section 3 states it |
| conduct, tier 3 | priced at 0 % denial in the verdict, with 10, 25 and 50 % and the break-even denial beside (11.5) |
| hours | US regular hours: tickets live from 09:00 CT to their cutoff (14:30 at the latest); the walk ends at the bar ending 15:08 CT |
| entry by hand | **the ticket is written at `t_pub` and submitted at 09:00:00 CT.** It is never submitted inside the closed window, where a platform order would work at once. The latency L is the time the user has to write it. The levels of `pd`, `on` and `pdc` are known before 08:30, so at `t_pub` only the sides and `rn100`'s multiples are new (4.3) |
| firm rules | only rules verified in `vendor/stage2/config/rules.yaml` or `config/rules_extended.yaml` |

## 4. Time, data and calendar

1. **The clock.** The bar store's `ts` is the bar's **start**, in epoch seconds UTC (`vendor/stage2/data/README.md`
   section 5). Bars are read on Stage 2's trading-day clock in US/Central, DST handled there (the walker's clock). The
   bar stamped 08:54 CT covers 08:54:00-08:54:59 and closes at 08:55.
2. **The latency and the three clocks** (the operator's ruling, item 2):

   | L (minutes) | `t_pub` (CT) | the last bar read (`P_ref`'s bar) | `t_live` (CT) |
   |---|---|---|---|
   | 5 (the reference) | 08:55 | stamped 08:54 | 09:00 |
   | 3 | 08:57 | stamped 08:56 | 09:00 |
   | 2 | 08:58 | stamped 08:57 | 09:00 |

   - `t_live` is the first minute outside the closed window, the same for every L. So the variants differ only in what
     the ticket was written from: a later `P_ref`, and so possibly a different side or `rn100` multiple. The void at
     `t_live` (item 4) is read the same way for each.
   - **The bars resolve these latencies exactly.** Every L is a whole number of minutes on minute boundaries, so the
     last closed bar at `t_pub` is the bar stamped `t_pub - 1 min`, and the first bar a ticket can fill on is the bar
     stamped 09:00. Neither needs a sub-minute price. What one-minute bars cannot show is the order of prints inside a
     fill bar; that is the pair rule's case (5.5), the same at every L. A latency of 1 minute or less would leave no
     closed bar between `P_ref` and the void check, and is not declared.
3. **Publish.** At `t_pub` every level and every side reads only bars stamped at or before `t_pub - 1 min`. The
   **reference price** `P_ref` is the close of the last bar stamped at or before `t_pub - 1 min` that trading day; with
   none from 08:30 on, every kind is void that day (counted). **What `P_ref` reads (a disclosure).** At these `t_pub`
   it reads closes inside 08:30-08:5x, so a ticket's side carries the net move across part of the opening half-hour.
   That is the information E-036 ruled outside Stage 2's closed opening-range branch for family B: a net move
   computable from closes on either side, not a rule defined on or triggered by the opening range. No fill and no entry
   lies in the half-hour (the operator's ruling). As E-036 required for family B, the pick's lift split by whether its
   side and multiple agree with those `P_ref` would set at 08:24 is reported beside (9.7). Whether this reading stands
   for RL3 is the lead's ruling before the pin (19 item 3).
4. **The side, fixed at `t_pub` and never re-read.** A level above `P_ref` is a resistance, below it a support. A level
   exactly at `P_ref` is void (counted), except `on`, whose high is a resistance and whose low a support by
   construction.
5. **Live and void.** `t_live` = 09:00 CT: the order works from the bar stamped 09:00.
   - "A bar after `t_live`" is a bar stamped at or after 09:00.
   - At `t_live` the price is the close of the bar stamped 08:59, the last closed by then (the walker's `price_at`).
   - A stop already at or through its price, or a limit already at or beyond its price (marketable), is **void** for
     the day (skipped, counted).
   - A bar stamped 09:00 or later that opens beyond a stop fills at its open plus the slippage (a gap through). One
     that opens through a limit fills at the limit's price, never better.
   - **A touch or a trade through inside 08:30-08:59 does nothing.** The order is not working then (the closed window).
6. **News windows inside the resting period** (3): the ticket is cancelled at the window's start, re-written at its end
   and live L minutes later, void if already through, never after its cutoff. At this text's date the record's windows
   on a non-void day all fall before 09:00, so in stages A to C the rule binds only if the record gains a window before
   the pin. The count of cancellations is reported.
7. **Calendar voids, from calendars fixed before the run, never from the day's own bars** (F-02's 4.5, unchanged). Each
   is counted.
   - **(a) Scheduled early closes** -- every `early_close` row, and every `holiday` row with a `close_ct`, of the pinned
     calendar `config/calendar_early_closes.csv` (E-029; LF sha256
     `72db4941f95320900aac29c6c047742da176cd9b55c925cc9275a18fb3e67fb2`). Such a day voids every kind; the next trading
     day voids `pd` and `pdc`.
   - **(b) Data-defect days** -- every `data_defect_candidate` row of the same file, and the purchase seam (trading day
     2025-06-30, no trades; 2025-07-01, its first two hours missing). Such a day voids every kind; the next trading day
     voids `pd` and `pdc`.
   - **(c) Roll days**, from the bar store's manifest `rolls`. A roll day voids `pd` and `pdc`.
   - **(d) FOMC**, from the list Stage 2's A3 reads (`vendor/stage2/config/atlas_a3.yaml` `news.fomc`). A scheduled
     meeting's statement day carries no tickets. An unscheduled statement released before `t_pub` changes nothing. One
     released after `t_pub` cancels every resting ticket five minutes before its release; a ticket that filled earlier
     walks on.
   - **(e) Edges.** The first trading day in the store voids `pd` and `pdc`.
   - **(f) Any other day whose bars end early** is kept. Its walk ends at the day's last present bar, and an open trade
     is flattened there and counted unresolved (the walker's `walk_end`).
8. **The test** (17 item 3): for each L, every level, side, `P_ref`, `A_E` and placebo ticket is unchanged when every
   bar stamped at or after `t_pub` that day, and every bar of every later day, is replaced.

## 5. The grid and the walk

### 5.1 Levels (each frozen at `t_pub`)

| kind | the level(s) | tickets a day |
|---|---|---|
| `pd` | the prior regular session's high and low: the bars stamped 08:30-14:59 CT of the previous trading day | 2 |
| `on` | the overnight session's high and low: the bars stamped 17:00 CT the evening before to **08:29** CT | 2 |
| `pdc` | the prior regular session's close: the close of its bar stamped 14:59 CT (void when that bar is missing) | 1 |
| `rn100` | the nearest multiples of 100 points of the futures' own price above and below `P_ref`; when `P_ref` is exactly a multiple, the multiples 100 points above and below it | 2 |

`pd`, `on` and `pdc` do not depend on L. Their sides do, through `P_ref`, except `on`'s (4.4). `rn100`'s multiples
depend on L through `P_ref`.

### 5.2 Side rules (order types), and where each is offered

| rule | offered at | at a resistance | at a support | fill |
|---|---|---|---|---|
| `break` | `rn100` | buy **stop** one tick above the level | sell **stop** one tick below | the first bar stamped at or after `t_live` trading at the stop's price; at that price plus one tick (`slip_ticks`, `vendor/stage2/config/atlas_a3.yaml`; D-95), or at the bar's open plus one tick when it opens beyond the stop |
| `fade` | `pd`, `on`, `pdc`, `rn100` | sell **limit** at the level | buy **limit** at the level | **only when a bar stamped at or after `t_live` trades through the level by at least one tick** (a buy limit: the bar's low at or below the price less a tick; a sell limit: the high at or above the price plus a tick); at the limit price, never better, also when the bar opens through it. A bar that reaches the price without trading through does not fill it |

**The limit rule, checked against the operator's ruling (item 3).** The operator asks that limit entries be modelled as
the repository's fill rule: a trade-through by one tick, live from the order's latency, cancelled at a news window's
start.
- **The trade-through and the price:** the walker's `LIMIT_ENTRY` (`extended/walker.py`'s module text and
  `fill_order`) states exactly that rule, and feature-rules 3 states it too.
- **"Live from the order's latency":** the walker's `live` slot -- the order fills only on bars stamped at or after it
  -- is set to 09:00, which is `t_pub + L` (4.2).
- **The void:** a limit already marketable at `live` is void (the walker's `price_at` rule).
- **The cancellation at a news window's start:** a cutoff at the window's start and a re-written order live L minutes
  after its end (4.6), in the family's adapter.

T-4 holds each of these on synthetic bars at every L (17 item 4).

### 5.3 Per ticket

One ticket a level a day. It fills at most once and is never re-armed, except by 4.6's re-writing after a news window
or stage D's re-placing (11.2), each void if already through. Unfilled, it is cancelled at its (cell, R)'s **cutoff**
(7.2): it fills only on bars closing at or before the cutoff. When both levels of a kind fill on one day, both fills
count in stages A to C. In stage D, and in the valuation, the two tickets of a kind are one-cancels-other (11.2).

### 5.4 The walk

This repository's walker (`extended/walker.py`; its identity with Stage 2's walk holds, E-011), with this family's
preset, built after the pin:
- **The walk's end and the flatten.** The walk's last bar is the bar ending 15:08 CT. A trade still open there is
  flattened at the worst of the bars ending 15:08-15:10 CT, less two ticks (Stage 2's `fv3_rung_walk` convention).
- **No stop move** (`breakeven` off).
- **The barriers.** From the fill, the stop at S ticks is reached by a touch, and the target at floor(R x S) ticks by a
  trade through it by a tick. On a bar reaching both, the stop.
- **Costs.** Stage 2's per-contract cost at the stop (`atlas_a3.fee_by_stop`; `vendor/stage2/config/fills.yaml`). No
  entry tick on a resting fill, since a stop's slippage is in its price. A tick on a stop exit, none on a target, two
  on a flatten.

### 5.5 The pair, the fill bar, and the bookings

As F-02's 5.5, unchanged.
- **The mirror.** Every fill has a mirror: the opposite side at the same fill bar, with the same stop, targets and walk.
- **The pair rule** (`fill_bar="pair"`). If a pair's fill bar touches either trade's stop or target, the pair is
  ambiguous: both are booked as stopped losses, zero lift, and counted (K5). Otherwise both are walked from the next
  bar.
- **Symmetric booking** (`mirror_booking="symmetric"`) decides C1 and C1'. **Rung 1** (`mirror_booking="rule_fill"`)
  decides C2. Rungs 2 and 4 are read beside.
- **T-13 (b)'s switches** run per (side rule, stop, R) and apply to every latency alike, since the latency does not
  change the null T-13 reads:
  - symmetric booking moves to rung 1 where its null interval lies wholly on the rule's side;
  - C2's rung 1 moves to rung 2 where rung 1's interval does;
  - the (cell, R) is killed where rung 2's interval does too (KB).
- **What T-13 (b) can move.** Only `fade` cells. A level-specific overshoot stays in `break`'s C1, bounded by K5,
  cancelled in part by C1', and absorbed by a tick in C2's rung 1. The rest is stated, not removed.

### 5.6 The lift, and the estimand of every stage

As F-02's 5.6.
- **The pair term:** w = 1/2 [win(rule) - win(mirror)], in win probability.
- **The lift:** the mean of w over all the (cell, R)'s fills in a block, ambiguous pairs included as zero. The net R
  lift is beside.
- **The estimand:** direction on fills whose fill minute stayed inside the pair rule's band, diluted toward zero by
  the rest. K5 caps the zeroed share at 5 %.
- **Resolution** is read with each trade's own fill-bar rule (`fill_bar="declared"` for that trade alone).
- **Break and fade at `rn100`** are near-exact negatives under symmetric booking.

### 5.7 The coin twin beside

A seeded coin twin is computed beside: one fair side per fill, in date order of the fills, cell by cell in table order
(5.9), seed **20263401**. It decides nothing.

### 5.8 The placebo (decisive for `break` at `rn100`; beside for every `fade`)

As F-02's 5.8, with the latency added.
- **`A_D`:** the mean, over the 20 most recent full regular sessions before day D, of the regular session's range.
- **The source day:** drawn past-only, from the kind's eligible days at least 21 and at most 252 trading days before
  the target day E.
- **The placebo ticket:**
  - its side is E's own real ticket's side (the target day's own side);
  - its distance from E's `P_ref` is the counterpart's distance on D, both at the cell's latency L: scaled by
    `A_E / A_D` at `pd`, `on` and `pdc`, unscaled at `rn100`;
  - everything else is the real ticket's: rule, stop, R, L, `t_pub`, `t_live`, cutoff, void rule, walk, bookings and
    4.6's news rule.
- **The draws are shared across latencies.** Five replicates, j = 0..4. Each (replicate j, kind k, block b) has its own
  generator, `numpy.random.default_rng([20263402, j, k, b])`, with k: 0 `pd`, 1 `on`, 2 `pdc`, 3 `rn100`, and b: 0
  the choice block, 1 the judged block, 2 the confirmation window. It makes one `integers(len(pool))` draw per target
  day, in date order, over the source pool in date order.
  - So the source day of (j, k, E) is the same at every L. Only the distances, which are measured at each L's
    `P_ref`, differ.
  - A target day with an empty pool carries no placebo, and is counted.
- **Coincidences** with a real level are kept (conservative for a pass).
- **Placebo cells:** 45, one per cell. They are controls, not hypotheses. Only `rn100`'s decides anything (C1').
- **What it identifies:**
  - at `rn100` the placebo's distances are exchangeable with the level's;
  - at `pdc` it matches the overnight move's sign but not its size;
  - at `pd` and `on` it matches neither.

  Outside `rn100` the placebo-differenced lift is a reading only, with no level claim (9.8).

### 5.9 Cells and hypotheses

- **Cells:** (4 `fade` kinds + 1 `break` kind) x 3 stops x 3 latencies = **45 cells**.
- **Table order** (the cell index c = 0..44, used by every seed and every tie):
  - c = (g x 3 + s) x 3 + l;
  - g is the rule-kind, 0 to 4: `fade` `pd`, `fade` `on`, `fade` `pdc`, `fade` `rn100`, `break` `rn100`;
  - s is the stop, 0 to 2: 50, 100 and 150 ticks;
  - l is the latency, 0 to 2: 5, 3 and 2 minutes, the reference first.
  - R's index r is 0 to 2 for R = 1, 1.5 and 3.
- **Hypotheses:** each cell at R = 1, 1.5 and 3, so **135 signed hypotheses**: 108 `fade`-signed and 27
  `break`-signed, over **108 (kind, stop, latency, R) questions**. At `rn100` both signs are asked; elsewhere only the
  fade sign.
- **How they are counted.** Every cell is counted whether dropped at the pin (7.1), killed or read. **Every latency
  variant is counted in `k_cells`, in the hypotheses and in stage B's family-wise maximum (8 item 4)**, which covers
  the dependence between latencies, as it covers that between break and fade (E-003 (d)).
- **Why the latencies cost little power at stage B.** The three latencies share every level but `rn100`'s multiples,
  every source draw and almost every fill. Their statistics are close to perfectly correlated, so the max-T's critical
  value rises far less than three separate families would. That is stated, not assumed: stage B's bootstrap computes
  it.
- **Nothing is chosen after a look.** The three latencies are declared now. The pick among them is stage B's declared
  rule (8 item 7). The 5-minute sibling of the pick is reported beside it (9.7).

<!-- counted-cells -->
| what | count | how |
|---|---|---|
| rule-kinds | 5 | 4 `fade` kinds + 1 `break` kind |
| stops | 3 | 50, 100, 150 ticks |
| latencies | 3 | 5, 3, 2 minutes |
| cells | 45 | 5 x 3 x 3 |
| R per cell | 3 | 1, 1.5, 3 |
| signed hypotheses | 135 | 45 x 3 |
| fade-signed hypotheses | 108 | 4 x 3 x 3 x 3 |
| break-signed hypotheses | 27 | 1 x 3 x 3 x 3 |
| questions | 108 | (kind, stop, latency, R): 4 x 3 x 3 x 3 |
| placebo cells | 45 | one per cell, controls |
| campaign cells | 1 | stage D, if it runs |
<!-- end counted-cells -->

### 5.10 The side's persistence, its band and its balance (Q-126's plan 2.5 and 4.4, declared before the pin)

Q-126's plan fixes a family's one-sample statistic by the side persistence the family declares before its pin, and
holds it to that statement from its sides alone (plan 2.5, E-184, E-187). This family declares:

- **The kind: a switching side.** The regime-filter kind is barred (E-187), and this family's side has no regimes.
- **The band: below 42 sessions** -- plan 2.5's first row. Under it:
  - **when scope D chose the primary,** C1 uses the primary, in scope D, for cells 4.4's admission admits;
  - **when the scope-Q branch is the primary** (scope D chose none), C1 uses the primary, in scope Q, with the band
    check at 2.5's loosest band (its second-column clause).

  The second statistic (2.5's 42-to-50 row) is never this family's.
- **Why the band, from the rule.** Each ticket's side is set at its day's `t_pub` from that day's levels and `P_ref`,
  and never carried to another day. There is no multi-session filter. A cell's session side is the net of its fills'
  sides (+1 long, -1 short). So the side's dwell is set by which levels trade from day to day, not by any state the
  rule holds.
- **What could make it persist (a risk stated now; Q-142 section 2.1).**
  - A fade sells resistances and buys supports. In a rising stretch upper levels trade more, so a fade cell leans
    short; in a falling one, long. A break cell leans with the stretch.
  - So the side inherits the persistence of the market's drift over weeks to months. That presses the balance limit
    and E-161's drift question.
  - This text does not estimate it: the band check reads it, outcome-free, from the sides.
- **The traded share** (plan 2.5's V-2 reading). Not every session trades. `rn100` and `on` are expected to trade on
  most sessions; `pd` and `pdc` on fewer, since their levels can lie far from the price. This is an expectation, not a
  figure. Each cell's share of sessions with a non-tie side is reported at stage A. A thinly traded cell is refused more
  often, which costs power, never size (plan 2.5).
- **The series, as Q-108's 4.4 defines it.** For each cell, each traded session's net side is the sum of its fills'
  sides. Sessions with no fill, and ties (both levels of a kind filled, a net of zero), are dropped. What is left is the
  non-tie series m_j in calendar order. R is its runs, E its effective count, and the mean side |sum m_j| over its
  length. Fills are counted from the fill rule alone; no walk past the fill and no pair term is computed.
- **The checks**, every one on sides only, by the built functions (`extended/lift_one_sample2.py` at the adopted blob,
  and the `lift_one_sample` functions it imports). No threshold is typed here: each is computed for the span's n from
  `docs/calibration/scripts/q126/q126_arith.py`'s functions, as the plan defines them.
  - **The band check for a switching side:** R within `band_interval` for the band below 42 on n sessions, and the
    mean side at most `band_b` for that band (plan 2.5).
  - **In scope D, 4.4's admission:** R at least floor((n - 1)/63) + 3 on the span stage A reads, or 13 on the judged
    block; E at least 4; a single side never admitted; the mean side at most `admission_b` (plan 4.4).
- **Where they run.**
  - **On the choice block at stage A** (7.2 item 9), after the pin, on the span stage A reads, whose n the runner
    asserts. A cell that misses either check is **killed at stage A**, and counted. It is not re-declared, since the
    text is pinned (19 item 6 offers the lead the plan's pre-pin alternative).
  - **On the judged block inside stage C, before any outcome** (9.1), under the purpose `stage_C_sides`. A pick that
    misses is **"not claimed"** and the family closes. There is never a switch of band, kind or statistic (plan 2.5).
  - **No two-sample line is declared for a cell not admitted.** `break`'s C1' is a conjunctive line, never a fallback.
    A not-admitted pick is not claimed.

## 6. Parameters: fixed, searched, dropped

### 6.1 The table

| parameter | what it is | class | value | source or reason |
|---|---|---|---|---|
| market, bars | the data | fixed | NQ 1-minute bars, Databento GLBX.MDP3 `ohlcv-1m`, raw prices, one contract a day | E-002; `vendor/stage2/data/README.md` |
| development window | the days read | fixed | 2020-01-02 to 2026-07-16 | CHARTER; `config/windows.yaml` |
| choice and judged blocks | where the pick is chosen, where it is judged | fixed | 2020-01-02 to 2023-12-29; 2024-01-02 to 2026-07-16 | CHARTER section 3 |
| level kinds | which prices | searched | `pd`, `on`, `pdc`, `rn100` | F-02's |
| side rules | break or fade | searched | `fade` at all four kinds; `break` at `rn100` | F-02's (6.2) |
| stops | the stop's distance from the fill | searched | 50, 100, 150 ticks (12.5, 25, 37.5 points) | P-14's two rungs and P-16's stop; 6.3 |
| R | target over stop | searched | 1, 1.5, 3 | the table's main asks (`u_value_map.csv` `records_leaf`) |
| **latency L** | the minutes from the ticket's writing to its working | **searched, counted** | **5 (the reference), 3, 2** | the operator (2026-11-18, item 2); CHARTER section 4 for 5 |
| `t_live` | when a ticket starts working | fixed | 09:00 CT, every L | the operator (2026-11-18, item 1): no fill in 08:30-08:59 |
| `t_pub` | when a ticket is written | fixed per L | 09:00 - L: 08:55, 08:57, 08:58 CT | 4.2 |
| `P_ref` | the price that sets each side | fixed per L | the close of the last bar stamped at or before `t_pub - 1 min` | 4.3 |
| void rule | an order already through at `t_live` is skipped | fixed | the price at `t_live` = the close of the bar stamped 08:59 | the walker's `price_at` |
| news windows | when no fill or entry may happen | fixed rule | 08:30-08:59 CT; every window under `tier1_news_events_restriction` in the record at the pin; cancel at the start, re-written at the end, live L later | the operator (2026-11-18, items 1 and 3); E-034 |
| stop slippage | ticks paid on a stop entry | fixed | 1 tick; symmetric booking at 2 and 4 beside (break) | `atlas_a3.yaml` `slip_ticks`; D-95 |
| limit fill | when a limit fills | fixed | a trade through by at least 1 tick, at the limit's price, never better | feature-rules 3; the walker; the operator (item 3) |
| target rounding; two-barrier bar | -- | fixed | floor(R x S); the stop first | Stage 2's `target_ticks`; feature-rules 3 |
| fill-bar settlement | the fill bar | fixed | the pair rule for the lift; each trade's own rule for resolution | E-010; F-02's N5 |
| booking for C1 and C1' | the mirror's price in the pass line | fixed rule | symmetric; rung 1 where T-13 (b) finds symmetric booking favours the rule; per (side rule, stop, R), every L alike | E-010; 5.5 |
| booking for C2 | the mirror's price in the value line | fixed rule | rung 1; rung 2 where T-13 (b) finds rung 1 favours the rule; killed where rung 2 does too | 5.5 |
| walk end and flatten | where an open trade is closed | fixed | the bar ending 15:08 CT; the worst of bars ending 15:08-15:10, less 2 ticks | Stage 2's convention |
| costs | fees and ticks | fixed | Stage 2's at the stop; exit ticks 1 / 0 / 2 | E-010, E-011 |
| cutoff | when an unfilled ticket is cancelled | fixed rule, value read on the choice block | per (cell, R): the latest of 14:30, 14:00, ..., 10:00 CT passing 7.2 item 2 | F-02's rule |
| resolution ceiling | the most that may reach the flatten | fixed | 5 % overall and in every calendar year | D-212 (2) as D-308 (3) raised it |
| K1 supply | the fewest fills | fixed | 100 on the choice block and 12 in every calendar year of it | F-02 |
| K5 ambiguity cap | the most fills the walk cannot settle | fixed | 5 % of fills | the drafter's choice (F-02's): it buys measurability, not an error rate |
| calendar voids | days with no ticket | fixed | 4.7's lists | E-029 |
| `rn100` spacing | the round number | fixed | 100 points, in the futures' own price | F-02 |
| placebo | the control for `break` | fixed | 5 replicates; past-only sources 21 to 252 trading days back; the target day's own sides; distances scaled by `A` (20 full sessions) at `pd`, `on`, `pdc`, unscaled at `rn100`; draws shared across L | F-02's 5.8; 5.8 |
| the side's persistence | the band C1's statistic is fixed by | fixed, declared | a switching side, below 42 sessions (5.10) | plan 2.5; E-187 |
| power gate | what a (cell, R) must show before the pin | fixed rule | 7.1: finite MDL80 at most R-16's factor 3 times its value-bar lift, at ceiling supply | E-086; R-16; F-B's screen factor |
| stage B bootstrap | the family-wise gate on the choice block | fixed | stationary, mean block 21 sessions, circular, 2,000 replicates, centred, normalised by the sample's se, seed 20263400 | F-02's 8 |
| stage B's gate | the choice block's selection device | fixed, not calibrated | the stationary bootstrap's max-T over every surviving (cell, R), every latency included, at family-wise 0.05 | 8 |
| stage C level and statistic | the pass line | fixed | one-sided 0.05 / (k (k + 1)); the adopted one-sample line for C1 and C2; `two_sample_bound` (treated-cluster df) for C1' | E-008; E-187; 9 |
| value bar | the least a pass must be worth | fixed | $500 a year at C2's bound | `u_value_map.csv` `bar`; E-008 |
| valuation | where a lift is priced | fixed rule | section 10 | F-02's 10 |
| the 50-tick scaling rho | the value of a smaller bet | fixed rule | rho (10), an approximation of unknown sign; rho squared and 1 beside | F-02's V2 |
| ticket size in stage D | the micros a ticket carries | fixed | the engine's `_plain_size` at the pick's stop: the allowance, the Combine's room cap, the 45-tick floor (D-271 (3)) | P-14's configuration; 6.3 |
| realised risk in stage D | floor (ii) | a build check | at least 0.9 of the allowance- and room-capped intention | E-022 (1) |
| stage D bound level | the shift of both streams | fixed | the one-sided 0.05 bound, both streams | U1's verdict arm; CHARTER section 2 |
| stage D base, routing, seed | the floors and the scorecards | fixed | section 11; campaign seed 20263405, 500 paths | E-008; E-022 (2) |
| hours | when tickets rest | fixed | 09:00 CT to the cutoff | 4 |
| memory | each heavy step's ceiling | fixed | at most 2.5 GB, measured on the build | 18.2 |

### 6.2 Dropped, and why

F-02's 6.2 is carried:
- `break` at `on` and `pd` (the long-window breakout's follow effect, read and closed on this window, D-555, D-592);
- `break` at `pdc` (G1: no placebo can match the level's distance);
- `or30` and every opening range (D-281 (3); E-007 (b));
- frozen session-VWAP bands and prior swing points (each a search of its own);
- R = 2, 2.5 and 0.25;
- round-number spacings other than 100, and re-published tickets other than 4.6's and 11.2's;
- the breakeven stop move;
- time stops, other sessions and the signal-service distribution.

Added:
- **Latencies of 1 minute or less, and any between those declared** -- not asked by the operator. A latency of 1 minute
  or less leaves no closed bar between `P_ref` and the void check (4.2).
- **A `t_live` before 09:00** -- the operator's closed window.
- **A `t_live` that moves with L** (for example `t_pub` fixed at 08:25 and the ticket working from 08:25 + L) -- every
  such ticket would work inside the closed window.
- **A `t_pub` before 08:30 for every L** -- then all three variants would be the same tickets, which would count three
  identical cells. 19 item 3 records this as the alternative to 4.3's reading.

### 6.3 The 12.5-point stop, the stop band and the size a ticket carries

As F-02's 6.3.
- **The 12.5-point stop is admitted as a cell.** D-527 (3)'s cost finding concerns a coin re-entering through a window,
  judged by its campaign. This family's pass line is a lift over the coin twin, which carries no cost.
- **The stop band** comes from `vendor/stage2/results/stop_band.csv` (D-201 (2)). The build reads each state's narrow
  edge -- the larger of the size-cap stop and the cost-drag floor `cost_drag_floor_ticks` -- and writes, for each stop,
  whether it lies inside the band in each state. The share of stage D's tickets outside the band is reported beside
  (D-201 (2)'s card rule is Stage 2's, and this family has no card).
- **The size a ticket carries is the engine's own** (`propedge/campaign/sizing.py` `_plain_size`, under P-14's
  configuration `vendor/stage2/config/fv3_corrected_portfolio.yaml`). That is:
  - the state's dollar risk in whole micros at the pick's stop, under the allowance by balance
    (`u_value_map.csv` identity `d667_sizing_50k`);
  - never more than the room above the floor on a Combine (`room_cap`, D-313);
  - standing aside below the 45-tick cost floor;
  - the fee re-priced at the contracts (D-324).
- The intention it is measured against is the engine's `capped_intention`. The engine's need-aware and consistency-cap
  exits act on tickets as on the base's trades.
- **Why that form:** it is the form R\* = P-14 was registered under (E-022 (1)). D-212's purpose -- consistent risk
  -- holds, since a ticket's size in a given state is fixed.
- **Floor (ii) becomes a build check** (T-15), reported beside.

## 7. Before the pin, and stage A: the gates, before any outcome

### 7.1 Before the pin: the power gate (G; light, no bar)

**Why.** By the program's rule a strict line must show power, not only size (E-051; the operator's standing concern).
A family whose minimum detectable lift is far above the lift worth its value bar should not spend one of the seven
calibrated k (Q-142 section 4 step 5). The gate runs after Q-126's adoption row and before the pin. It reads no bar and
no outcome, only `results/q126_cal_power.csv` from the calibration's clean run and the vendored value map. It is
computed by a script committed before it runs, and its rows are written to the pinning row.

**For each (cell, R)** -- in practice per (kind, stop, R), since the latency changes none of the inputs:
1. **The supply, at its ceiling.** The most fills the cell could have on the judged block, with every ticket filling on
   every one of its 657 sessions (E-094 (2)'s count): two tickets a session at `pd`, `on` and `rn100`, one at `pdc`.
   The power file's row is the largest toy size at or below that ceiling. If the ceiling lies below the smallest toy
   size, the (cell, R) has no figure and fails the gate.
2. **The MDL.** In the power file, under the statistic and scope the adoption row adopts for "below 42 sessions":
   - the 80 % minimum detectable lift (`MDL80`) in win probability, on the `win1` toys;
   - the larger of the coin-side and session-flipped toys' entries at that row;
   - at the family's k if tabulated, otherwise at the next tabulated k above it (the power file holds k = 13, 15 and
     20: k = 14 reads the k = 15 column, which is conservative).

   An empty or infinite entry means no power.
3. **The value-bar lift, at its ceiling.** lambda_bar = the lift in points at which section 10's value reaches $500 a
   year, with u = the judged block's sessions a year (every session a filled ticket-day) and caps at the records count
   (10's cap (i)) alone. This is the most uses a ticket-day count can reach, and needs no bar.
4. **The rule.** The (cell, R) passes when its MDL80 is finite and at most **3 x lambda_bar**. The 3 is R-16's factor:
   the factor at which family B's draft declares itself a screen (`prereg/DRAFT_F-B_multifeature.md`, section 8 item
   8). A (cell, R) that fails is **dropped at the pin and counted** (F-03 dropped a cell at its pin by its own rule,
   E-095). **If every (cell, R) fails, the family closes before its pin and takes no k.**

**What it can and cannot do.** It is lenient by construction: supply and uses at their ceilings, the records cap
erring high. It closes only a family that could not reach its bar even with every ticket filled every day. The
realistic figures come at stage A (7.2 item 8), where a family over the factor at every surviving (cell, R) is declared
a screen, but still runs. The toys are P-16's 150-tick pairs at the 1R win value. Each figure is labelled with that
null's stop and R, not the cell's.

### 7.2 Stage A, on the choice block

Read on the **choice block only**, per (cell, R), from fill, void and touch counts and the barrier kinds, pooled over
each rule trade and its mirror (reflection-symmetric: how far prices travelled, never which way). No lift is computed.

1. **KB, the build's synthetic tests, before anything is read** (17 items 5 and 6): T-14 (c) and (e) kill `break` at
   an `rn100` stop, or withdraw the fade's level claim there; T-13 (b) sets each (side rule, stop, R)'s bookings, and
   kills a (cell, R) at the ladder's end.
2. **The cutoff rule and K2, resolution.** A (cell, R)'s cutoff is the latest of 14:30, 14:00, 13:30, ..., 10:00 CT
   such that, over its fills before it, the pooled unresolved share at its own R is at most 5 %, overall and in each
   calendar year 2020 to 2023. Each trade is walked by its own fill-bar rule. With no such time the (cell, R) is killed.
3. **K1, supply:** at least 100 fills on the choice block after its cutoff, and at least 12 in each calendar year.
4. **K5, ambiguity:** a (cell, R) whose ambiguous share among its choice-block fills (after its cutoff, under symmetric
   booking) exceeds 5 % is killed. The share by year is reported.
5. **K3, realised risk:** not applicable in stages A to C. Its stage-D form is 6.3's check.
6. **A cell** with every R killed or dropped is killed.
7. **K4, fill realism: reported, decides nothing.**
   - For `fade`: fills over touches.
   - For `break`: the share of gap fills.
   - For both: the share of fills in the first five minutes after 09:00, and the share on fill bars spanning a quarter
     of the stop.
   - For each L: the share of tickets void at `t_live`, and the share whose side or multiple differs from the 5-minute
     sibling's.
8. **Planning (D-4), from counts only, written before stage B reads anything.** For every surviving (cell, R):
   - its choice-block fills;
   - its judged-block fills, estimated as the choice-block rate per session times 657;
   - **the MDL80 from `results/q126_cal_power.csv`**, by 7.1 item 2's rules at the estimated judged fills in place of
     the ceiling ("above the smallest toy entry" when below it, with no figure);
   - for `break`, the same figure stated for C1' (the two-sample line), from the power tables Q-55's rerun wrote for
     `two_sample_bound`;
   - the value-bar lift at the cell's capped uses (10), and the ratio.

   **Declared a screen:** if the MDL80 exceeds 3 x the value-bar lift at every surviving (cell, R), the family is
   declared a screen in the `planning` section. It still runs, and a pass is still carried, with the label. Every
   figure goes to the `planning` section; none is typed anywhere.
9. **The side checks (5.10), on sides only**, for every surviving cell, on the span stage A reads: the band check for a
   switching side below 42 sessions, and, in scope D, 4.4's admission. A cell that misses either is killed, and
   counted. Each cell's R, E, mean side, traded share and verdict are written to the `sides` section.
10. **K0, the adopted statistic's size on the cell's own fill counts** (E-052 (1); Q-108's 7 item 5). It is
    outcome-free, and runs after items 2 to 4 and 9, for every surviving (cell, R).
    - **Its counts:** the (cell, R)'s fills per session on the choice block's calendar after its cutoff, in date order.
    - **Its null:** Q-16's `cluster` null: each fill 0.5 sign(a_s + e), with a_s ~ N(0, 0.35) the session effect and
      e ~ N(0, 0.65). An exact null with sides reset daily.
    - **Its replications:** 200,000. Each lays a window of 657 consecutive sessions of those counts at a random circular
      offset, draws the outcomes, and applies the adopted statistic at one-sided 0.05 / (k (k + 1)). It applies the
      statistic alone, without scope D's admission: the admission can only remove rejections, so leaving it out makes
      K0 stricter.
    - **The rule:** if the rate's 95 % Clopper-Pearson interval lies wholly above the level, the (cell, R) is killed
      before stage B, and counted.
    - **For a `break` cell** the same check runs on the treated two-sample form (C1'), with level and placebo fills at
      the same offset sharing a_s. A wholly-above interval kills the whole cell (E-065's build note).
    - **Seeds:** `default_rng([20263408, 0, c, r])` for C1's form and `[20263408, 1, c, r]` for C1''s, with c and r as
      in 5.9.
    - **What it is:** a check conditional on the cell's realised choice-block counts. A kept cell says its own counts
      are safe, never that its profile is.
11. **The valuation's inputs, from contract arithmetic and direction-free counts** (10): sigma, rho and the records
    caps; the reachable uses (one heavy, direction-free count from the base's campaign on the choice block's days
    only, or not used, E-032 (2)); phi.

Every cell killed or dropped: the family closes at stage A.

## 8. Stage B: choose on the choice block

As F-02's section 8, over every surviving (cell, R) at every latency:

1. **The statistics:** the lift L under its C1 booking; for `break`, also D = L - L_placebo; the lift under its C2
   booking.
2. **The bootstrap.** A stationary bootstrap (Politis and Romano) of the choice block's sessions in date order:
   circular, mean block 21 sessions, **2,000 replicates, seed 20263400**.
   - Each replicate is one draw of session indices, shared by every statistic, every latency and the placebo fills.
   - The standard error is the replicates' sd. t = L / se, and a centred replicate is t\*_b = (L\*_b - L) / se,
     normalised by the sample's se.
3. **The decisive statistic** T(c, R): t_L for `fade`; for `break`, the smaller of t_L and t_D.
4. **The family-wise critical value** q: the 95th percentile over replicates of the maximum of T\* over **every
   surviving (cell, R), all three latencies included** -- one-sided, family-wise 0.05. Benjamini-Hochberg at 10 % is
   reported beside and never selects.
5. **Eligibility.** A (cell, R) above q is eligible only if its rule-side trades at its R on the choice block, each
   walked by its own fill-bar rule, leave at most 5 % unresolved, overall and in each calendar year 2020 to 2023.
6. **Kill B.** No eligible (cell, R) above q: the family closes, and the judged block is not read.
7. **The pick.** The eligible (cell, R) with the largest valued lift (10) at the lower limit of its C2-booked lift,
   L_C2 - q x se_C2.
   - A tie (equal to the dollar) goes to more choice-block fills, then to the first in table order (5.9: rule-kind,
     stop, latency with 5 minutes first, R ascending).
   - There is one pick. Its latency is part of it, and every stage after B uses it.

Stage B is a gate, not a claim. Its bootstrap is not calibrated and is kept as the choice block's selection device only
(F-02's section 8, the paragraph on calibration, unchanged). The program's error rate rests on C1 at the family's
level, by the adopted statistic, on a judged block that played no part in the choice.

## 9. Stage C: judge the pick on the judged block (the pass line, E-008)

The pick alone, with its latency, its cutoff and every rule as fixed in stages A and B, on fills from 2024-01-02 to
2026-07-16. **The side checks, C0 and C1 to C4 must all hold; any failure closes the family.**

1. **The side checks and C0, before any x is computed.**
   - **The sides (5.10)**, under the purpose `stage_C_sides`. The pick's judged fills are counted per session of the
     judged calendar from the fill rule alone, and their sides form the non-tie series. The band check (below 42
     sessions, on the judged block's n) and, in scope D, 4.4's judged admission are applied. **A miss: "not claimed",
     and the family closes.** The pick's lift is still computed and reported beside, labelled "not a claim".
   - **C0:** K0's check (7.2 item 10) on the pick's judged counts as they are (no offset), with 200,000 replications.
     Seeds: `default_rng([20263408, 2, 0])`, and for a `break` pick also the two-sample form, `[20263408, 3, 0]`. If
     the 95 % Clopper-Pearson interval lies wholly above the level, no pass is claimed and the family closes at C0.
   - **The order:** the sides' and C0's rows are written to the result file before any x is computed, and the runner
     computes x only after them (17 item 11).
2. **C1, direction.** The pick's lift under its C1 booking on the judged block has its one-sided lower bound at
   **0.05 / (k (k + 1))** above zero, by **the adopted one-sample line** in its adopted scope (5.10).
   - **The call:** the function and statistic the adoption row names in `extended/lift_one_sample2.py`. The run
     asserts `git rev-parse HEAD:extended/lift_one_sample2.py` equals the blob that row pins before stage C, and
     refuses otherwise.
   - **The estimate:** the per-fill mean of the pair terms x = w over every fill of the pick in the judged block,
     ambiguous pairs as zero.
   - **The calendar:** every trading day the bar store holds from 2024-01-02 to 2026-07-16, void for this family or
     not, in date order: **657 sessions, sha256 (LF-joined ISO dates)
     `d1e4524b15dc6a69c2f66865462a5fe30527c6a56b4c7cc7aaccc1436a30f3bd`** (E-094 (2)). The runner asserts both and
     writes them to the result file. Fills are summed per session of that calendar (`session_sums`); blocks are cut by
     `lift_bound.block_index`.
   - **The level:** `lift_bound.family_level(k)`, asserted equal to 0.05 / (k (k + 1)), strictly inside (0, 0.5), with
     k in `lift_one_sample.K_RANGE_1S`. That one value is passed to C1, C1', C2, K0 and C0.
   - **The null class.** The class Q-126 calibrated for its band, held to it by 5.10's checks. **The fill intensity**
     is persistent by expectation: resting orders fill when the price travels to them, so fills rise in volatile
     stretches. That is outside the calibrated class, so K0 and C0 check it on the cell's own counts. **The residual**
     (F-02's R1): a momentum or reversal regime gives w a mean that persists as long as the regime. It is stated beside
     the verdict, with the readings of 9.7.
3. **C1', the level beyond a matched crossing (`break` picks, at `rn100` only).** The placebo-differenced lift D on the
   judged block has its lower bound at the same level above zero, by
   `extended.lift_bound.two_sample_bound(x_level, s_level, x_placebo, s_placebo, n_sessions, level=...)`:
   - sample 1 is the pick's level fills, and sample 2 the placebo fills of the five replicates, each summed per session
     of the same calendar;
   - D is the difference of the two per-fill means, over the judged block's fill totals;
   - the variance comes from the count-centred residual block sums, with the treated-cluster count and df = Gt - 1
     (`DIFF_DF_RULE = "treated"`);
   - all three block lengths are required.

   It holds its level (E-094 (1)). The run asserts `git rev-parse HEAD:extended/lift_bound.py` equals
   **`984f3467a4a05aa790d3ea43e94ac7761f0725b2`** before stage C.
   - It is an intersection with C1 at the same level, so there is no extra spend.
   - **What a C1-only pass means:** a break pick passing C1 but not C1' is recorded as a lead for unread data, not a
     finding.
4. **C2, value.** The valued lift (10, on its capped uses) at the lower bound -- at the same level, by the same adopted
   one-sample line -- of the pick's lift **under its C2 booking** (rung 1, or rung 2 where 5.5 moves it) is at least
   **$500 a year**. It is a conjunctive gate on a calibrated bound, not a claim. C2 prices the bound of the lift over
   the coin twin, as E-008 reads "its value-map price at that bound". For a `break` pick it is read beside at D's bound
   too, deciding nothing.
5. **C3, resolution (a floor):** on the judged block, the pick's rule-side trades at its R, each walked by its own
   fill-bar rule, leave at most 5 % unresolved, overall and in every calendar year (2024, 2025, and 2026 to 07-16). A
   calendar year with fewer than 63 sessions in a window is pooled with the adjacent year (D-604).
6. **C4, measurability:** K5 on the judged block -- the ambiguous share is at most 5 %.
7. **Beside, deciding nothing:**
   - **the pick's latency siblings:** the same (rule-kind, stop, R) at the other two latencies, **the 5-minute cell
     always among them** -- each with its judged lift, its net R lift, its fills, its unresolved and K5 shares and, for
     `break`, D, each lift with its one-sided 0.05 bound by the adopted statistic on the judged calendar. When the pick
     is the 5-minute cell, its 3- and 2-minute siblings are reported;
   - **the opening half-hour's part** (4.3): the pick's lift on tickets whose side and multiple agree with those `P_ref`
     at 08:24 would set, and on those that differ, with the shares;
   - **the pick's year-by-year readings:** for each calendar year of each block, its lift, net R lift, fills,
     unresolved share, K5 share and, for `break`, D, each with its one-sided 0.05 bound on that year's calendar;
   - **Q-122's readings** (E-157 (b)): the pick's lift by tercile of a causal trailing session range, absolute and
     relative, and the equal-weight-block reading beside the adopted statistic, in the form Q-122's merged module
     fixes;
   - **E-161's drift nulls:** the adopted statistic's sizes on the drift nulls, cited from the adoption row (plan 3.3);
   - drift: the lifts on long-rule and short-rule fills, and their mean, the side-balanced lift;
   - the seeded coin twin (20263401); the net R lift; C1's lift under the other bookings; the booking ladder (for
     `break`, symmetric booking at 2 and 4 ticks of slippage; rungs 2 and 4 for both); Benjamini-Hochberg; K4's
     adverse selection; the share of fills in the first five minutes after 09:00; the placebo-differenced lift for a
     `fade` pick; C2 at rho squared and at rho = 1 for a 50-tick pick; lambda on first fills; the regime readings
     (stage B's lift by quarter of the choice block, the lag-1 correlation of its 21- and 63-session block lifts);
   - `cons` on the same x, labelled "the failed statistic, beside only" (E-094).
8. **What a `fade` pass means.** A fade pick passing every line is a reversal after these crossings, carried on its
   trades as E-008 judges designs.
   - A level claim is made only at `rn100`, and only if the placebo-differenced lift beside it also clears C1's level
     and 17 item 6 has not withdrawn the claim.
   - At `pdc`, `on` and `pd` no level claim is made (G1; the placebo matches neither the window nor the overnight
     path).

## 10. The valued lift

As F-02's section 10, with the reach read at 09:00. It uses the value map's own first-order formula
(`vendor/stage2/results/u_value_map.csv`, definitions `extra_win_prob_points` and `mean_dv`), with each place's uses
capped by what the routing can reach.

- **The base:** `p14` for 50- and 100-tick stops, `p16` for 150 ticks.
- **The places that ask R, and sigma:**
  - (b) the evaluation, any R, by the share of `records_leaf`'s recorded trading leaf-days at the cell's R;
  - (c) the funded opening, R = 3 only, sigma = 1;
  - (d) funded later, R = 1 and 1.5;
  - (e) paid, any R.
- **The value of a use:** v(p) = `mean_dv(p)` x rho(p), with rho = 1 at `p16` 150 ticks and at `p14` 100 ticks. At
  `p14` 50 ticks, rho is the 50-tick ticket's realised risk over the 100-tick ticket's, summed over the place's R-asking
  leaf-days, each sized as 6.3 sizes it. That is an approximation of unknown sign, so rho squared and 1 are read
  beside.
- **What a place can take:** cap(p, R) is the smaller of:
  - (i) the records count, `trades_per_year_records(p)` x sigma(p, R);
  - (ii) the reachable count: phi x the yearly count, per path-year, of the base's campaign path-days on which, **at
    09:00 CT**, place p is the highest-priority place with an account that asks R, has not traded that session, and
    sits in a firm that holds no position and closed none in the last five minutes.

  (ii) is counted once in stage A from the base's registered engine call, with its day table restricted to the choice
  block's days and read through `extended/reader.py` on those days only (E-032 (2)). If that cannot be done without
  opening the judged part of the files, (ii) is not used and the `valuation` section says so. phi is the cell's
  choice-block filled ticket-days over its placed ticket-days.
- **Uses:** u is the cell's filled ticket-days a year. A day with both levels filled counts once.
- **The priority order:** places by v(p), highest first; u_p = min(u - the uses already allocated, cap(p, R)).
- **The value:** $ a year = lambda x the sum over p of u_p x v(p) / 100, with lambda the lift in points at the bound
  in question. Stage D routes by the same order and reach rule. It is first-order: a ranking and a bar, never a
  forecast.

## 11. Stage D: the campaign -- E-008's floors, and the scorecards beside

As F-02's section 11. It runs whenever stage C has been read. When C's lines hold, its floors decide. When the family
closed at C, it gives only the scorecards beside the close. A close at A or B has no stage D.

### 11.1 Its role, and the floors

The long-run gate is read on stage D's own design (E-022 (2)). The floors can close the family; nothing here can carry
it.
- **(i)** Growth on the required bankroll at the bound above zero, at the fresh seed 20263405, with both streams at the
  one-sided 0.05 bound (11.4).
- **(ii)** Realised risk: a build check (6.3).
- **(iii)** Every rule verified.
- **(iv)** Conduct tier 1 true of the routing (11.3).

### 11.2 The design

**The base, by the pick's stop:** P-14 (A3-BRK30-CB20) for 50- and 100-tick picks, P-16 (`rc_s150_all_nr`) for
150-tick picks. The base's own trades, walk, coin, cuts and table are unchanged (19 item 5 on its trades inside
08:30-08:59).

- **Published and placed.** A ticket is written at the pick's `t_pub` on every day its kind has one. It goes to one
  account: the first, in the router's order, in the highest-priority place of section 10 with an account that asks the
  pick's R, has not traded that session, and sits in a firm flat and not within five minutes of a close. It is
  submitted at 09:00:00 and works from the bar stamped 09:00. With no such account there is no ticket that day
  (counted).
- **A busy firm at 09:00:** the ticket is re-written once the firm has been flat five minutes, on an account meeting
  the same conditions. It is live L minutes later, void if already through, never after the cutoff. This is a use the
  valuation does not count, so the valuation errs low.
- **Reserved:** the account is reserved while the ticket rests; the base routes no offer to it.
- **Cancel on entry.** Before any base entry on another account, the resting ticket is cancelled. It is re-written five
  minutes after that trade's exit, on the reserved account if it still has not traded that session. It is live L
  minutes later, void if already through, never after the cutoff.
- **A fill** takes the firm's one position; the base's offers are refused until five minutes after its exit (D-429).
  That is the account's one trade of the session.
- **No second trade.** A ticket is never an account's second trade of a session. The two tickets of a kind are
  one-cancels-other.
- **Size:** the engine's own sizing at the pick's stop (6.3).
- **News windows:** 4.6's rule, for every ticket.
- **The EIA releases inside the resting window** (F-02's final read, M5). A resting ticket sized at its account's full
  allowance is cancelled five minutes before each EIA crude oil or natural gas inventories release on its day
  (`vendor/stage2/config/im2_release_calendar.csv`, rows `EIAC` and `EIAG`, their `time_ct`). It is re-written five
  minutes after, live L minutes later, void if already through, never after the cutoff. A ticket that filled before
  walks on. Tickets below the full allowance rest through. The screen counts every fill; the share of the pick's fills
  inside these windows is reported beside.

### 11.3 Conduct

Every step can be done by hand. The firm never holds two positions, so never opposite positions across accounts. Each
ticket rests on one account.

### 11.4 The bound level, and the tickets' verdict arm

One level for both streams: **the one-sided 0.05 bound** (U1's verdict arm, `scripts/user_journey.py`).
- The tickets: the pick's own rule-side trades at every R of the base's carried menu, by Student-t on 21-session block
  means in each block separately. The lower of the two blocks' bounds is taken, R by R.
- The base: shifted at the 0.05 bound exactly as U1's verdict arm shifts it.
- Each stream is shifted by lb - e (`propedge.campaign.gate.shifted_blocks`), and the two are merged into one day log.

### 11.5 The runs

1. **The identity first, refusing (T-15).** With no tickets the runner reproduces the base's registered gate paths
   (P-14: `vendor/stage2/results/a3_brk30_cb20_gate_paths.csv`; P-16: `rc_s150_all_gate_paths.csv`) on E-002's columns
   and tolerance, and U1's start rows (`results/user_journey.csv`, section `start`). A failed identity stops the
   family.
2. **The gate.** Stage 2's `gate` call as the base registered it -- 500 paths, **campaign seed 20263405**, 0 % denial,
   the placement off -- with both streams at the 0.05 bound. Floor (i) is read here.
3. **Beside, each reported and never a line:**
   - the base alone at the same seed and level; P-06's row;
   - the denial ladder (10, 25, 50 %) and the break-even denial;
   - the placement on, with the tier-2 shares of section 3;
   - the zero-edge twin;
   - the tickets' e and its bound for each R, and stage one's D-47 criterion at the pick's R;
   - D-212 (1)'s letter share; floor (ii)'s check; the share of tickets outside the stop band.
   - **The pick's 5-minute sibling's campaign** (when the pick is not the 5-minute cell): the same gate call with the
     sibling's tickets, at the same seed and level.
4. **D-663's validation readings** (EXPLORATORY, deciding nothing), through `extended/v1_adapter.py`, heavy, under the
   run lock, after the gate:
   - A0 (no draws);
   - A1 at mean blocks 1, 5, 21 and 63 sessions, `mc_seed = 20263403`;
   - B1 by `part_b1(seed = 20263404)`, 200,000 replicates, at one-sided 0.05 and at the family's level;
   - B2 at campaign seed 20263405 with Monte Carlo error drawn by `mc_seed = 20263403`;
   - C1's missed trades by `part_c1(seed = 20263406)`;
   - the slippage families (A) and (B) at campaign seed 20263405.

   A2 and B3 are not run: their seeds are fixed in the vendored code. All as F-02's 11.5 item 4.

### 11.6 What stays unidentified

As F-02's 11.6:
- the base occupies the firm after 09:00, and the take-up is reported;
- the reservation changes the base's routing;
- a 150-tick pick's comparison with R\* mixes its base's distance from P-14;
- the judged block has few independent starts;
- the value map is first-order.

Added: **the bases' own entries inside 08:30-08:59** stay as registered (19 item 5). Their count is reported beside.

## 12. The journey scorecard -- beside every judgement, never the pass line (CHARTER section 2; E-008, E-014, E-015)

As F-02's section 12. Stage D's real-order replay over start days (U1's form, `vendor/stage2/docs/USER_MILESTONES.md`)
runs on the verdict arm at the 0.05 bound for three designs: base plus tickets, the base alone, and **R\* = P-14**.
Each is read on all starts and on the judged block's starts. It is computed whenever stage C has been read. After a
close at A or B there is no scorecard, and the closing row says so.

1. P and the guarded measures as USER_MILESTONES defines them, with the frontier.
2. The journey's variables (E-014): sessions and cash to the first pass and the first payout, sessions to break-even,
   and the path's evenness.
3. Each measure as a distribution over start days, with its uncertainty from the effective number of independent
   starts.
4. E-007 (e)'s readings (Q-17's adapter, and its second version if merged by stage D).
5. The paired differences by `extended/p_bound`'s `pcons`, one-sided at 0.05, reported, never a line. Its module's
   blob, **`f5b29710e243f97a2795e57f6458512fea99199b`**, is asserted before stage D. `pcons` uses that module's own
   seed.
6. E-015's limits, once approved by the operator before stage D's run, as menu flags only.
7. The evenness trade-off curve.
8. **Not modelled, said wherever this scorecard appears:**
   - a user who stops when their own money runs out;
   - the user's time (a 2-minute ticket's demands on it included);
   - taxes;
   - E-034's unstated news rules;
   - USDA crop production inside the resting window;
   - the base's full-size trades held through an unnamed release;
   - the bases' own entries inside 08:30-08:59.

The replay draws nothing.

## 13. What a pass and a fail mean

- **CARRIED** -- the side checks, C0 to C4, C1' for a break pick, and stage D's floors all hold. The pick, with its
  latency, is a development finding on a late-development block. It takes a registration id, a model card, its
  registered development test, the auditor, and **one confirmation** (14).
  - **A break pass** is a direction at round numbers, beyond what a crossing matched on its side and an exchangeable
    distance carries.
  - **A fade pass** is a reversal after these crossings (9.8).
  - **A pick at 3 or 2 minutes** is carried at that latency. Its 5-minute sibling is stated beside in the carrying row.
    A user who cannot write the ticket in that time cannot use it.
- **CLOSED** -- before the pin (7.1: no k), at A, B, C (the side checks, C0, C1, C1', C2, C3 or C4) or D (a floor). The
  reason goes in a decision row.
  - A close at B or C is worded "no lift detectable at this power", with the planning section's MDL at this family's
    level.
  - A close at C carries stage D's scorecards beside it, and makes the judged block's start days prior exposure.
  - **"Not claimed"** (the side checks at stage C) closes the family. It says the pick's sides left the calibrated
    class, not that the lift is zero.
  - The closure binds this specification (D-277's boundary). A later family on these levels names this closure, says
    what changed, and is judged on data this family did not read.
- **NOT PINNED** -- Q-126 adopts no line for the band, or the power gate fails. The text stays on record, no k is
  spent, and nothing is read.

## 14. The confirmation, declared before any development read

As F-02's section 14.
- **The window:** NQ from 2026-07-17 (`config/windows.yaml`, `reserve`, reserved). It is not on disk and is never read
  until a carried candidate is registered; the reader refuses it outright. It becomes NQ's fourth confirmation window
  only by the operator's decision (D-107). It is a purchase. Stage 2's draft P-16 confirmation targets the same
  window; if any test reads it first, the lead records that and the operator decides.
- **What it tests: the pick's trades, at the pick's latency, not P.**
  - The pick's lift over its coin twin on the window's fills, one-sided at the registered 0.05, by the adopted
    statistic on the window's calendar of sessions, with the bound at 0.05/N beside (D-189).
  - **The statistic's size at 0.05 and at the window's length is shown at the registration**, before the window is
    bought. Q-126 tabulates levels to 0.025 only (plan 2.1). If it is not shown, no confirmation is registered and the
    pick stays a development finding.
  - For a break pick, D by `two_sample_bound`, with the placebo built as 5.8 builds it under generators
    `default_rng([20263402, j, k, 2])`.
  - C2 at the 95 % bound; resolution at most 5 %; K5 at most 5 %.
- **What it cannot test: P.** The scorecard on the window is descriptive.
- **How much data:** at least six months (D-604), and at least the months at which the adopted statistic, one-sided at
  0.05 on a calendar of that length, has 80 % power for a lift equal to the pick's judged lower bound at the family
  level.
  - The power is computed from the pick's judged session sums by F-02's construction: 2,000 replications per length,
    each drawing 21 m sessions with replacement, thinning to the lower block rate, flipping each session's sign,
    adding the lift.
  - Seed `default_rng([20263407, m])`. The same at zero lift is beside, as a size reading.
  - It moves only the length, and so the purchase, never the level. It is written in the carrying row.

## 15. Seeds, fixed now and checked

| seed | status | what it draws |
|---|---|---|
| 20263400 | in use | stage B's stationary bootstrap on the choice block (8) |
| 20263401 | in use | the seeded coin twin beside (5.7) |
| 20263402 | in use | the placebo's source draws: `default_rng([20263402, j, k, b])` -- j the replicate (0..4), k the kind (0..3), b the block (0 choice, 1 judged, 2 confirmation); shared across latencies (5.8) |
| 20263403 | in use | D-663's A1 and B2 readings: `v1_adapter.Engine(mc_seed = 20263403)`, each run's Monte-Carlo error (11.5 item 4) |
| 20263404 | in use | D-663's B1: `v1_adapter.part_b1(seed = 20263404)` (11.5 item 4) |
| 20263405 | in use | stage D's campaign seed: the gate floor and every beside arm, 500 paths (11) |
| 20263406 | in use | D-663's C1: `v1_adapter.part_c1(seed = 20263406)`, each realisation's seed `v1_adapter.c1_seed(20263406, subject, arm, realisation)` (11.5 item 4) |
| 20263407 | in use | the confirmation's length rule: `default_rng([20263407, m])` (14) |
| 20263408 | in use | K0 and C0 (7.2 item 10, 9.1): `[20263408, 0, c, r]` K0 by the adopted statistic, `[20263408, 1, c, r]` K0's two-sample form for `break` cells, `[20263408, 2, 0]` C0, `[20263408, 3, 0]` C0's two-sample form |
| 20263409 | in use | the build's synthetic tests: `[20263409, j]` -- j = 0 the shift test, 1 T-3's synthetic judged block, 2 T-13 (b), 3 T-13 (c), 4 T-13 (a)'s extension; 10 to 14 T-14 (a), (b), (c), (e) gap follow, (e) gap reversal; 20 and 21 the K0/C0 toys' count patterns and outcome draws (header, condition 3) |

**The search (2026-11-18, before this text).**
- Every 8-digit token beginning 2026 was collected, word-bounded, from every tracked text file on every local branch
  and remote-tracking ref (`git grep -Iow` over 22 refs, the vendored snapshot included).
- The same was done on every uncommitted or untracked text file of the main tree and every worktree under
  `%LOCALAPPDATA%\stage2-extended-wt`, with the licensed data excluded.
- No token lay in 20263400 to 20263409. Without word bounds, the digits occur only inside floating-point values of
  result files.
- No other declaration's block is named here. The blocks other texts hold are taken by role -- F-02's two (retired with
  its text), F-03's, the described readings' and Q-108's and Q-126's calibration and validation blocks -- and none is
  used.

**Inherited, used only as their owners registered them:**
- the bases' own seeds: P-16's coin by date and minute, P-14's identity seed and P-16's gate seed (E-002);
- `pcons`'s module seed (Q-16's);
- Q-17's adapter's block.

They are named by role, not by number.

**The check (T-12 at the build; T-0 now).** A use is a seed passed to a generator in code, or declared as a family's
own in a `prereg/` file. A reference, or an exclusive range bound, is not a use. T-0 (`tests/test_rl3_draft.py`) holds
the block to this table, finds it nowhere else, and finds no other 2026 seed token in this text.

## 16. Multiplicity and the budget

1. **This family is program family number k, proposed 14, at 0.05 / (k (k + 1)) = 0.05 / 210 at k = 14.** The
   gatekeeper assigns k at the pin, within Q-126's calibrated k = 13 to 20.
2. **One cell reaches judgement**, with no further division in the family. C1' is an intersection with C1 at the same
   level; C2 is a conjunctive gate; stage B's family-wise test, on the choice block, spends nothing.
3. **The latency variants spend nothing of the program's budget.** They are cells of this one family, counted in
   `k_cells` and in stage B's family-wise maximum, which fixes the one pick before the judged block is read.
4. **The program's honesty sentence.** Stage 2 ran programs S and U on this same window, each with its own 5 %. The
   development-stage level is a screening threshold. **The decision is carried by one confirmation on unread data**
   (D-189).
5. **Counted** (5.9's table): 45 cells, each counted whether dropped at the pin, killed or read; 135 signed hypotheses
   over 108 questions; 45 placebo cells as controls; one campaign cell if stage D runs. The pick's latency siblings and
   year-by-year readings re-read the grid and add no cell. The 27 `break` cells at `on`, `pd` and `pdc` (3 kinds x 3
   stops x 3 latencies) were dropped before any read and are not counted.
6. **D_protocol 1.5's holes:**
   - (a) no fitted model;
   - (b) no normaliser spans the sample;
   - (c) this family re-declares F-02 after reviews and a failed statistic, not after a read;
   - (d) every judged-block read goes through `extended/reader.py` and its ledger under a purpose named in 18.1;
   - (e) k, as above;
   - (f) the tests, section 17.

## 17. The build's identities and tests, before any reading

All of the family's code is committed after its pin. A failure of any test other than T-13 (b) and T-14 (c) and (e)
**stops the build**: the failure protocol applies, and no stage runs until a decision row records the diagnosis.

1. **The walker** (E-011: P-16's `TRADES_SHA256` under `STAGE2`) holds at the build's commit. The family's preset
   differs from `STAGE2` only in the breakeven move. (fast)
2. **E-002's and Q-05's identities** hold, and the run refuses, never skips, when their data are absent. (slow)
3. **No look-ahead**, for each L. (fast)
   - Replaced: every bar stamped at or after `t_pub` on day E, and every bar of every later day.
   - Not moved: every level, side and `P_ref` on E, every `A_E`, and every placebo ticket on E.
   - The replacements are a seeded walk (`[20263409, 0]`) and a constant, over days including roll days, DST changes,
     the seam, early closes and the days after them.
   - Also asserted: no level is all-NaN or constant, and the 2- and 3-minute `P_ref` differ from the 5-minute one on
     synthetic days that move after 08:54.
4. **Fill rules on synthetic bars**, under the family's preset, at every L (fast):
   - the void at `t_live`; the gap through;
   - **the limit's trade-through by one tick at the limit's price, never better, including a bar opening through it,
     and no fill on a bar that only reaches the price** (the operator's item 3);
   - **no fill on any bar stamped 08:30-08:59, whatever it trades**; the first fill no earlier than the bar stamped
     09:00;
   - **a ticket cancelled at a news window's start, re-written at its end and live L minutes later, void if through,
     never after the cutoff**, on a synthetic window inside the resting period;
   - one fill; the cutoff; every calendar void from the pinned files; FOMC days and an unscheduled statement after
     `t_pub`;
   - the pair rule under every booking, and each trade's own rule for resolution; the rungs for both side rules;
   - two levels a day; break and fade near-exact negatives under symmetric booking.
5. **T-13, the mirror's zero**, per side rule, per stop and per R (latency-free; its tickets live from 09:00): (a)
   today's form extended, seed `[20263409, 4]`, slow; (b) spread and jumps, seed `[20263409, 2]`, slow, deciding 5.5's
   switches; (c) the precise form, seed `[20263409, 3]`, heavy, under the run lock. All as F-02's 17 item 5, with its
   tickets live every five minutes from 09:00 to 13:25 CT and cancelled at 14:00.
6. **T-14, planted effects** (seeds `[20263409, 10..14]`; (c) and (e) heavy, under the run lock). The generator is
   F-02's 17 item 6 (the regular session 08:30-15:09, the overnight session 17:00-08:29, one tick a step), with tickets
   live from 09:00 and plant (a) at the first touch after 09:00. Its checks are at `rn100`'s `break` cells, per stop, at
   R = 1 and L = 5:
   - (a) L and D bounded above zero at the family's level;
   - (b) D's interval covering zero at Z = 2.394;
   - (c) and (e), 9 kill checks at Z = 2.773, with F-02's precision and visibility rules;
   - (d) a level read from a bar at or after `t_pub` caught by test 3.

   A (kind, stop) killed or withdrawn by (c) or (e) is so at every latency.
7. **T-3, choice-stage invariance** (slow). Stage A's and B's outputs are byte-identical when every judged row of every
   file stages A and B open is replaced, on temporary copies: the bars from 2024-01-02 on by a seeded walk
   (`[20263409, 1]`), and the judged rows of the reachable count's walk and event files. The outputs compared: cutoffs,
   kills, sides, planning, the valuation's inputs, the critical value and the pick.
8. **T-15, stage D's routing** (slow): the identity with no tickets, and toy days for the priority order and the reach
   rule, the reservation, cancel-on-entry and re-writing with live at L, the void at re-place, one-cancels-other, the
   cutoff, the news window, `_plain_size` with the room cap binding, floor (ii)'s check, and the need-aware exit.
9. **The adopted statistic's own tests** (Q-126's build) pass at the build's commit, at the adopted blob.
10. **T-12:** section 15's seeds are used nowhere else, telling references from uses.
11. **T-7's analogue:** stage C reads the pick from stage B's result file by its sha256, and its entry point cannot run
    stage B. It writes the sides' and C0's rows before computing any x.
12. **The stage-C runner's assertions**, each refusing, a test showing each refusing:
    - the level and k (9.2);
    - the calendar's count and sha256 (9.2);
    - `lift_one_sample2.py`'s and `lift_bound.py`'s blobs (9.2, 9.3);
    - the span n the side checks read (5.10).
13. **T-0** (`tests/test_rl3_draft.py`, now, fast): this text's form.

## 18. Outputs, the reads and the run

### 18.1 The judged block's reads (E-026)

Every read of Stage 2's bars or walks goes through `extended/reader.py`. A read after 2023-12-29 needs a purpose named on
the one line below, inside a clean run of a committed tree, once per purpose (a repeat needs a row). No purpose here
contains a choosing or fitting word.

- **Judged-block reads:** `stage_C_sides`, `stage_C_judgement`, `stage_D_gate_floor`, `stage_D_scorecard`

| purpose | what it reads, and why |
|---|---|
| `stage_C_sides` | the pick's judged fills and their sides only, from the fill rule (no walk past a fill, no pair term): the band check and, in scope D, 4.4's judged admission, before any outcome (9.1) |
| `stage_C_judgement` | the pick's judged fills, its placebo and its walks, and those of its two latency siblings: C0 to C4 and every reading beside (9.7) |
| `stage_D_gate_floor` | the stage-D campaign over the development window: the engine's reads and the tickets' walks at every R of the base's menu, for the pick and, beside, its 5-minute sibling (11.5) |
| `stage_D_scorecard` | the real-order replay over start days of the three designs (12) |

**Not on this line:** the identity reads (purpose `identity`); stages A and B and the reachable count (the choice block
only); T-13 and T-14 (synthetic); the pre-pin power gate (no bar); the confirmation window, which the reader refuses.

### 18.2 Files and the run

- **Files:**
  - `results/rl3_levels.csv`, with sections `build`, `supply`, `cutoff`, `kill`, `sides`, `planning`, `valuation`,
    `choice`, `judged`, `placebo` and `beside`;
  - `results/rl3_campaign.csv`;
  - `results/rl3_journey.csv`;
  - the power gate's rows, `results/rl3_power_gate.csv`, from a clean run before the pin.

  Each is written with its sidecar manifest through `extended.results.write_result`. The manifest carries `prereg_id`,
  the cell and hypothesis counts, every seed and parameter, the latencies, the sha256 of
  `vendor/DATA_MANIFEST_stage2.sha256` and of `config/calendar_early_closes.csv`, and the adopted statistic's blob.
  They are EXPLORATORY until a carried candidate is registered.
- **The run.** Once, from a clean checkout of a named commit (`scripts/run_clean.py`), under the run lock, watched to
  its end.
  - **The order is fixed, the refusals first:** the identities (T-15 item 1, E-002, Q-05), refusing; the blob and
    calendar assertions; the build's synthetic KB tests; stage A (the side checks, K0 and the reachable count
    included); B; C (the sides, then C0, then the lines); then D.
  - Each stage's file is written before the next reads anything. A kill stops the sequence. A run aborted or restarted
    is recorded by the lead with its log, and only the first complete run is read.
- **Memory.** Each heavy step -- stage A with the reachable count, stage B, stage C, stage D's gate and each D-663
  reading, and T-13 (c), T-14 (c) and (e) -- declares its peak at most **2.5 GB**. The figure is measured on the build
  at its final commit and recorded, and `run_lock.py take` is given it. The 45 cells' fills are walked one stop at a
  time, all latencies together, so the working set does not grow with the latency count.
- **Pre-run conditions, each refusing:** this file pinned; Q-122's module merged (for 9.7); Q-133's fix not needed
  (this family reuses no opening path).

## 19. What the pin requires, and what stays open

**1. The pin's conditions** (the header, restated). The pin requires all of:
- Q-126's adoption row for side persistence below 42 sessions, with its statistic, scope and blob;
- the power gate (7.1) passing at least one (cell, R), its rows in the pinning row, every dropped (cell, R) named;
- K0's and C0's level and power on the adopted statistic shown on toys;
- the gatekeeper's k within 13 to 20;
- items 2 to 6 below recorded.

If Q-126 adopts nothing for the band, or the gate drops every (cell, R), this text is not pinned, takes no k, and stays
on record. **The pinning row** names: the adopted statistic's blob, `extended/lift_bound.py`'s
`984f3467a4a05aa790d3ea43e94ac7761f0725b2`, `extended/p_bound.py`'s `f5b29710e243f97a2795e57f6458512fea99199b`, the
pinned file and its diff from this reviewed text (the rename and `F-XX` only), and the judged session list's count and
sha256 (E-094 (2)).

**The operator's rulings of 2026-11-18, applied here as declared, each to be recorded by the lead's row:**
- **(a) News -- ANSWERED.** No fill and no entry in 08:30-08:59 CT, nor inside any verified news window (3, 4). The
  question Q-142 left open for this family -- whether F-02's fills from 08:30 or family B's D-281 (3) default governs
  -- is answered by the operator's ruling. This text declares the closed window, so this item is closed.
- **(b) Latency.** 5 minutes (the reference), 3 and 2, every one counted (4.2, 5.9).
- **(c) Limit entries.** The repository's fill rule, checked in 5.2 and held by T-4.

**The lead's, before the pin:**

2. **Q-126's adoption row**, the band and scope it names, and its blob (item 1).
3. **What `P_ref` reads (4.3).** At `t_pub` = 09:00 - L, `P_ref` reads closes inside the opening half-hour. That is the
   net move E-036 ruled outside Stage 2's closed branch for family B, here with no fill and no entry in the half-hour.
   **Declared default: as written,** with the agree/differ split beside (9.7). **The alternative:** `P_ref` from the
   bar stamped 08:24 for every L, as F-02 did. Then all three latencies are the same tickets, so the latency parameter
   collapses to one value and the cells to 15. That would be a new text, not this one.
4. **CHARTER section 4** states five minutes from alert to order. The operator's ruling admits 3 and 2 as counted
   variants. The charter's wording is the lead's to amend, or to record as read beside the ruling, before the pin.
5. **The bases' own entries inside 08:30-08:59.** P-14's and P-16's registered trades include entries there, and
   stage D keeps them as registered: the identity needs them, and E-034 decided the bases' trades. Under the
   operator's "no trading during news hours", the lead may rule that stage D also drops the bases' entries inside the
   window. That would need its own identity form, since the registered paths would no longer be reproduced.
   **Declared default: as registered,** their count reported beside (11.6, 12 item 8).
6. **Where the choice-block side checks run** (5.10). Q-126's plan 2.5 places them "on the choice block, at stage A,
   before the family's pin", and lets a family that misses re-declare its band or kind from sides only before the pin
   (E-184's minor). **Declared default: after the pin, at stage A, where a miss kills the cell** (stricter: there is no
   re-declaration, and nothing is read before the pin). **The alternative:** a sides-only, choice-block-only read before
   the pin, as a declared heavy step of its own, with any re-declaration in the pinning row.
7. **C2's statistic (a note).** The brief for this text named C2 among the two-sample lines. F-02's C2 was the
   pass statistic's one-sample bound, and E-008 prices "that bound": the bound of the lift over the coin twin. So this
   text keeps C2 on the adopted one-sample line (9.4) and reads it at D's two-sample bound beside for a break pick. A
   ruling that C2 decides at the two-sample bound would be a further text.

**Readings beside, needed before stage D:** Q-17's adapter for 12 item 4, and E-015's approved limits for 12 item 6.
**Optional:** a per-rung `dv` from D-667's solver would replace rho.

**The operator's**, each with its safe default applied, none blocking:
1. `or30` and the opening ranges (D-281 (3)): out (E-007 (b)).
2. The confirmation: NQ's fourth (D-107), shared with P-16's draft; its length and its purchase.
3. The levels of E-015's limits (approval pending).

## 20. Anything chosen after seeing results

*(Empty at declaration. Anything added after a reading is exploratory, reported apart, `exploratory=True` in its
manifest, and recorded in its own decision row -- never in this file.)*
