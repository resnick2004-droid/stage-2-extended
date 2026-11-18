# DRAFT F-BON: one multi-feature model choosing the side of P-16's own overnight offers (B-ON) -- first text, not a declaration

**Status: DRAFT, first text, 2026-11-18 (TASK_QUEUE Q-144; the scout's slate note Q-142, sections 2.2 and 8). Not
pinned, no F-number, no k.** Nothing of the family is built beyond the overnight extension of the feature library
(`extended/features.py`'s `compute_overnight`, with `tests/test_features_overnight.py`) and this file's draft-time test
T-0 (`tests/test_bon_draft.py`). No bar has been read for it, no label computed, no model fitted, no outcome of anything
seen. This file may be edited until the lead pins it; from the pinning row on nothing in it is edited (a change is a new
family).

**Proposed k = 15** (the next free numbers: k = 13 to the per-firm execution-protocol family, Q-141; k = 14 proposed for
RL3, Q-142 2.1); **the gatekeeper assigns k at the pin.** The level is one-sided **0.05 / (k (k + 1))**; every worked
level below is at k = 15, **0.05 / 240**, and moves with k. **Seeds: the block 20262040-20262049** (section 21), checked
unique on every ref and worktree on 2026-11-18.

**It pins only after three things, in this order, and stays unpinned otherwise:**
1. **Q-126's adoption row** adopts a one-sample statistic for the band this family declares, **below 42 sessions**
   (`docs/calibration/Q-126_one_sample_plan_2.md`, sha256 `117f5eb36dfd8312b24db35d1e6898167397fe374ae47a1feab94b5a2ebfcdc6`,
   E-187; its section 2.5). **If Q-126 adopts nothing for that band, this family stays unpinned** (E-094 (3)(b)-(c)):
   no conditional pin.
2. **The pre-pin power gate** (section 11.10) passes, from Q-126's power file and this family's declared supply only.
3. **The operator's latency ruling of 2026-11-18 is recorded in a decision row** (section 0.1 item 3), since CHARTER
   section 4 states five minutes; without that row the two- and three-minute cells are struck before the pin and the
   count of section 10 falls with them (section 20 says how).

Its machinery is family B's sixth version, `prereg/DRAFT_F-B_multifeature.md` at git blob
`911771595ada8a3a8159c197670d12b7e37f71ff` ("F-B6" below): every reference to an F-B6 section is to that blob, so it
cannot drift while family B's draft is revised. Where this file and F-B6 differ, this file governs.

---

## 0. In plain words (for the operator)

P-16 is the program's registered coin design: every five minutes through the night (17:00 to 08:25 CT) a fair coin
picks long or short, with a 37.5-point stop, on the marks P-16's registration admitted. **This family keeps P-16's
offers, brackets and schedule exactly, and lets one pre-registered model choose the side instead of the coin.** The
model is a regularised logistic regression on 35 measurements of NQ's recent price, range, volume and calendar, each
scaled to the market's own recent volatility or volume. It is trained on 2020-2023 only, frozen, and judged once on
2024-01-02 to 2026-07-16.

**What the operator ruled for this family (2026-11-18, section 0.1):** trading at night, by hand, is accepted; no entry
and no fill inside a verified news window; the order may follow its alert by 5, 3 or 2 minutes, each declared and
counted; and a resting limit order is tried beside the market order, also counted.

It passes only if its side beats, **at the family's strict level, by the calibrated one-sample test Q-126 adopts:**
- the coin, on the same offers;
- being long in a rising market (the drift-matched line);
- each of the three follow-the-move rules Stage 2 already found, read at the same latency on the same offers;
- and, for a limit order, the coin's limit order **in money (net R)**, not only in wins;

and only if its edge is worth at least $500 a year at that bound where P-16's value map prices it.

**Expected in advance:** direction overnight is hard to predict; the family may be declared a screen before any lift is
read (section 11.9), and it may fail the pre-pin power gate and close before it takes a k. A "no" is a valid close.

## 0.1 The operator's rulings of 2026-11-18, as declared here

The lead conveyed four rulings of the operator (2026-11-18) and will record each in a decision row. Each is declared in
this text as follows.

1. **Overnight execution: yes.** The operator wants executions at every hour of the day and accepts that a user
   hand-enters orders at night. **The user's time stays out of the model, as CHARTER section 2 says** ("not modelled:
   ... the user's time"); the scorecard says so wherever it appears (section 15). The section-19 item on night hand
   entry is closed as answered (section 19 item 1). Hand entry only: no automated or API order entry (CHARTER section
   4).
2. **News: no trading during news hours.** No entry and no fill inside any verified news window; **a position open at a
   window's start is flattened at that bar, under RD-05's rule** (E-200 R-1; RD-05's A-18). Section 4.2 declares the
   windows and what the rule does at each.
3. **Order latency.** The alert-to-order latency L is a declared parameter: **L = 5 minutes is the reference cell**
   (CHARTER section 4; Stage 2 D-266), and **L = 3 and L = 2 minutes are counted variants**, declared here before any
   read and counted in the cells (section 10) and in the family-wise maximum of stage B (section 12). **The 5-minute
   cell of the pick is reported beside every pick** (section 14.5). Nothing is chosen after a look. How the bars and the
   walks resolve 2 and 3 minutes: section 6.1.
4. **Limit orders.** A resting limit entry is a counted variant beside the market entry (section 6.3): it goes live at
   the order's latency, fills only on a trade through its price by one tick, and is cancelled at a news window's start.

## 1. Hypothesis

**The mechanism.** Overnight NQ trades thinly through the Asian session and more heavily from the European open (02:00
CT) to the US releases. Short-horizon momentum and reversal, the price's position against the prior regular session's
levels and round numbers, and volume against its usual time-of-night level move the order flow of the traders active
then. One model reading these together might find a small direction signal on P-16's overnight offers that no single
rule shows. **Expected:** volatility and resolution speed are predictable; direction is hard. Stage 2's single OHLC side
rules on P-16's offers found per-offer effects that failed their span or latency guards (section 2). The European-open
drift, the strongest overnight effect in the literature the scout's review carries, is reported dead by its own authors
(the review's rank 5, as Q-142 2.2 cites it); this family does not rely on it.

**Two targets** (F-B6 section 1): **resolution speed**, the pipeline's positive control (it cannot pass: it ignores the
side); **direction**, the only target the pass line reads.

**What would make it worth something:** its lift in win probability over the coin at the same offers, times how often
it is used, times what a win is worth where P-16's value map prices it -- on every trade (place (a)) and, at 3R, on the
funded opening (place (c)). This is DIRECTIVE 6.1 exactly: supply from a schedule (P-16's marks), an edge as a side on
those offers.

## 2. Prior exposure, and why this is not a repeat

| row | what was read | on these offers? | sign and span |
|---|---|---|---|
| D-578, D-580 (Stage 2's S1) | 15 single OHLC side rules on P-16's offers | **yes**, at no delay (L = 0) | 15-minute momentum (`mom15`) and the latest 5-minute breakout (`lbrk5`), followed, survive the per-offer test; both fail the span guard |
| D-586, D-588, D-589 (S3) | new event kinds, followed | yes, L = 0 | the 1-minute 4-bar breakout followed (`lnbar1x4`) passes, its gain concentrated in 2024-2026 |
| D-590, D-592 (S3 at the latency) | `lnbar1x4` read five minutes early | yes, L = 5 | fails its campaign guard; its per-offer lift is nearly as large at L = 5 as at L = 0, recorded as a lead for unread data |
| D-581, D-582 (S2) | P-16's coin gated by volatility and trend states | yes | no state improves the offers enough |
| D-639, D-642 (handoff 3.1, family 4) | the coin's **trading hours** as a lever, judged on P | the coin's windows | US hours about level; other windows worse |
| F-03 (E-192) | a side-free timing filter of P-16's 3R funded opening on these offers | yes | closed at stage B by Kill B; judged block unread |
| family B's drafts (F-B6) | a side model on a 10:10-15:05 schedule | no | nothing read; overnight alerts dropped "US hours (handoff 3.1)" |

**Why this is not a repeat of anything closed, plainly.**
- **Handoff 3.1 closed levers, not direction.** Its family 4 changed *which hours a coin trades* and judged the change
  on P; the coin's side stayed a coin. Nothing in handoff 3.1 read whether a side chosen by a model beats the coin
  overnight. Family B cited it for keeping its own schedule to US hours, a scope choice of that draft, not a closure
  (F-B6 section 17, "dropped": "resting entries; overnight alerts ... US hours (handoff 3.1)"). **B-ON does not choose
  hours: it keeps P-16's overnight hours as registered and chooses only the side.**
- **No Stage 2 or program work fitted a joint model on normalised features** (F-B6 section 2 (b)). S1 and S3 read single
  rules; a pass here must beat the three that survived, on the same offers, at the family's own latency (C1-f).
- **F-03 asked a different question on the same population:** when a funded account takes its coin-sided opening (a
  filter judged against a placebo selection). B-ON chooses the side on every offer and is judged against the coin twin.
  F-03's closure (E-192) binds F-03's states and mechanism; this family names it (F-B6 section 15's rule) and uses no
  persistence state of F-03.
- **The judged block is late development for direction, not out of sample** (F-B6 section 2 (a)): Stage 2 read the
  follow effect on P-16's offers there. Hence C1-d and C1-f (section 14).

## 3. The population: P-16's own overnight offers

- **The offers.** F-03's population (`extended/opening_population.py` at git blob
  `92d2feaeb784b2ddf6b1c26511143b05a01b1091`; `in_population` and `p16_offered`): **P-16's admitted marks at 150 ticks**
  (its registration's screen file, `marks` section, read by `admitted_marks` against P-16's pinned sha256, never
  recomputed) **at 17:00 .. 08:25 CT**, on the walked day kinds `n` and `b` (not FOMC, not an early close, not empty), a
  report day's (`b`) from 07:40 only. F-03's "label" marks (08:30 .. 09:00 and a report day's 07:35) are **not** offers
  of this family: they lie in or next to the opening half-hour (section 4.3).
- **Sessions:** after the store's first `extended.features.HISTORY_DAYS` sessions. The choice block's and the judged
  block's session counts are counted at the build from A1's day table and Q-83's pinned judged session list (E-094's
  count and sha256, asserted by `opening_population.judged_sessions`), and written in stage A's `supply` section with
  the offers per session, per year and per block **before any outcome is read**.
- **The entry mark m** is P-16's: a market order fills at the open of the first bar opening at or after m (P-16's own
  entry, `walk_offers` under `extended.walker.STAGE2`). **The alert is t = m - L** for the cell's latency L (section
  6.1); the side is computed at t from bars stamped at or before t - 1 minute only.
- **The 17:00 mark.** At L = 5 its alert, 16:55 CT, lies in the daily halt (16:00-16:59 CT, no bar), before the trading
  day's first slot. **Its features are those of the trading day's 17:00 alert (slot 0)**, which reads no bar of the day:
  only the day-level features and the calendar, all built from earlier days whose bars closed by 16:00 CT, an hour
  before the entry -- so the latency is met at every L (`tests/test_features_overnight.py`,
  `test_the_17_00_alert_reads_only_bars_closed_by_the_halt`). In general the feature row of mark m at latency L is the
  row at slot max(0, m - L).
- **What it costs, said in advance.** The offers are P-16's, so supply and resolution are P-16's (its admitted marks
  were fixed by Stage 2's cutoff over 2020-2026, a disclosed pre-read, section 5); the population is not re-cut. A
  report day has no overnight offer before 07:40 (P-16's rule); FOMC days have none.

## 4. Contract fit, and the news rule

### 4.1 The constraints (CHARTER section 4)

| constraint | how the family meets it |
|---|---|
| latency, hand entry (CHARTER 4; D-266; the operator 2026-11-18) | the side at t = m - L from bars stamped <= t - 1 min only; L in {5, 3, 2} minutes, 5 the reference; the order placed by hand at m; no automated or API entry |
| a resting ticket published before it can trigger | a limit ticket is written at the alert t and goes live at m = t + L, never earlier (section 6.3) |
| one position per firm, five minutes flat (D-429) | the pass line reads every offer (the coin twin's form); the scorecard routes by Stage 2's strict rule |
| resolution (D-212, D-308) | P-16's admitted marks; K2 for every cell, at most 5 % at every R in {1, 1.5, 3} overall and in every year (section 11.3); a limit cell's on its filled tickets |
| realised risk (D-308) | K3, reported (a market entry's stop exit slips adversely, D-9); a limit fill at its price |
| stop band and cost floor (`stop_band.csv`) | P-16's 150 ticks, above the 45-tick floor |
| news (CHARTER 4; the operator 2026-11-18; E-200 R-1) | section 4.2 |
| the opening half-hour (D-281 (3)) | section 4.3 |
| conduct tier 1 (D-145) | no hedging (one position across the firm); no simulator-fill exploitation (no tight brackets; the 150-tick stop; a limit fills only on a trade-through); no maximum size into major news (section 4.2); no copying across accounts; nothing concealed |
| tier 2 (D-289) | off in the base case, on beside (P-16's table) |
| tier 3 (E-013 (1)) | 0 % denial in the verdict; 10/25/50 % beside |
| firm rules | none loaded by the family beyond section 4.2's; the scorecard runs Stage 2's engine on its verified ledger |

### 4.2 The news windows (the operator's ruling 2, under RD-05's rule)

**The rule, for every window below** (RD-05's A-18 as E-200 R-1 reads it): an entry's time is its order's **live time**
(the alert plus the cell's latency), known at the alert from the clock and the calendar alone; **no entry whose order
would go live inside a window**, and no fill inside one; **a working entry order is cancelled at the window's start**;
**a position open at the window's start is flattened at that bar** -- the 1-minute bar stamped at the window's first
minute, at its open, with the fill rule's flatten slippage (`fills.yaml`'s active profile, `flatten_slippage_ticks`) --
whether it is open being the walk's state at that minute. In the pass line's walk the flatten applies to both sides of
every pair alike (and to both tickets of a limit pair), so it is side-symmetric and cancels against the twin.

**The windows:**

| window | from | what it is | what the rule does on this population |
|---|---|---|---|
| **W-1** | CHARTER section 4; P-16's registration (D-533 (2)); the BLS 08:30 ET schedule (`vendor/stage2/data/release_days_0830_*.csv`, as published in advance) | on a BLS 08:30 ET release day, the trading day's open (17:00 CT the evening before) to 07:35:00 CT: no entry before 07:35 CT, strictly after the release (E-007) | P-16's report-day population starts at 07:40, so no order goes live inside W-1; no position is open at its start (every trade flattens by 15:10 CT the session before). The rule is checked at zero (a nonzero count is an engine error) |
| **W-2** | CHARTER section 4; Stage 2's FOMC statement set | an FOMC statement day, whole | not walked (day kind); nothing open at its start |
| **W-3** | a firm's **verified** news rule in Stage 2's ledger (`vendor/stage2/config/rules.yaml`) reaching the account traded, as RD-05 4.7 items 1 and 3 read it | the window the verified entry states, applied from the ledger, **never typed here** | **none reaches Topstep's $50K today**: its `tier1_news_events_restriction` entry has status `changed` and is not loaded (RD-05 4.7 item 1). If a window is verified for that account before the pin, the pinning row names its ledger key and the rule above applies to it from the ledger; otherwise W-3 is empty for this family |

**Not windows here, reported beside:** the FOMC minutes (`config/calendar_fomc_minutes.csv`, E-050), whose release
falls inside the regular session, when an overnight entry can still be open: no verified rule at this account names
them, and the record's Topstep list holds none (RD-05 4.7 item 1). **Beside, deciding nothing:** the count and share of
the pick's trades open at the minutes' release minute on a minutes day, and their outcomes, as RD-05's G-3 bracket
(strict: the full stop loss; lenient: the target less a tick). Releases at 10:00 ET have no pinned calendar in this
repository, so none is applied or counted. Both are open items for the lead (section 19 items 4 and 5).

### 4.3 The opening half-hour (D-281 (3))

The family's default is family B's (F-B6 section 22 item 1): **no used feature reads, and no entry lies in, 08:30-08:59
CT.** Here it holds by construction: the last entry mark is 08:25; its alerts lie at 08:20-08:23, reading bars stamped
at most 08:22; a limit ticket's life ends at the bar closing by 08:30 at the latest (section 6.3); the features at an
overnight alert read no bar after the alert (the shift test). **What is not excluded, disclosed:** a position entered
overnight can still be open through the half-hour and resolve in it, as P-16's own trades do. That is the trade's
holding, not an entry or a feature; the operator may still rule (section 19 item 6).

## 5. Data, blocks, the seal and the disclosed pre-reads

- **Data:** Stage 2's NQ 1-minute bars (licensed, uncommitted), development window **2020-01-02 to 2026-07-16** only.
  Stage 2's walks are not read for labels; labels come from this repository's walker (E-011's identity).
- **The choice block:** sessions **2020-01-02 to 2023-12-29** (every fit, the search, the pick). **The judged block:**
  sessions **2024-01-02 to 2026-07-16**, read for the frozen pick only.
- **The confirmation window, declared before any development read:** NQ from **2026-07-17**
  (`vendor/stage2/config/windows.yaml`), not on disk, never read until a carried candidate is registered, and a
  purchase (section 17).
- **The seal (E-026).** Every bar and walk is read through `extended/reader.py`, which refuses anything from 2026-07-17,
  refuses a choosing or fitting purpose on the judged block, refuses a judged purpose this pinned file does not name,
  refuses a judged read outside a clean run of a committed tree, and ledgers every judged read before it reads. The
  family's judged-block purposes, each read once, in this order, by one clean run:

  - **Judged-block reads:** `bon_stage_C_sides`, `bon_stage_C_judgement`, `bon_stage_C_campaign`, `bon_stage_C_scorecard`

  What each is:
  - `bon_stage_C_sides` -- the judged block's bars up to each alert, for the pinned model's features, scores and sides
    (with the trailing threshold of section 8, which reads the frozen model's scores of the 21 population sessions
    before each judged session, the first of them choice-block sessions), the filter's selection and the three twins'
    sides, **for the pick and for its 5-minute sibling** (section 14.5) only, and the judged-count and band checks; all
    hashed into the run's manifest before any outcome is read;
  - `bon_stage_C_judgement` -- the bars after each entry, for the pair values and the tickets at the pick's bracket and
    its sibling's: C1, C1-n, C1-d, C1-f, the twins' judged yearly lifts and the readings beside;
  - `bon_stage_C_campaign` -- the engine's gate campaigns of designs (i) and (ii) on the judged block: C2's routings and
    the long-run gate floor;
  - `bon_stage_C_scorecard` -- the U1 journey replay and Q-17's adapter on the judged block's starts.
- **Disclosed pre-reads** (inputs read or fitted over 2020-2026 that T-3 cannot see):

  | input | what it is | can bias | cannot bias |
  |---|---|---|---|
  | P-16's admitted marks (its screen file's `marks` section, pinned sha256) | Stage 2's side-free per-mark resolution cutoff over 2020-2026 (D-525 (4)) | which marks are offered; the resolution floors | any side or lift |
  | `stop_band.csv` | the cost floor and the stop band | which stop is allowed | any side or lift |
  | `u_value_map.csv` at base `p16` (E-181's reader) | D-667's solved tables | C2's dollars per place; the stage-B ranking; the screen rule's bar | the lift or its bound |
  | Stage 2's S1/S3/S2 reads (D-578 to D-592) | per-offer direction readings on these offers | the design of C1-f (why it exists) | the pick (stage B, choice block) |
  | Q-126's power file (`q126_cal_power.csv`) | the calibration's MDL tables on P-16's judged pairs (a calibration, not this family's outcome) | the pre-pin power gate | any side or lift of this family |
  | F-03's stage B (E-192) | F-03's selection statistic on this population's choice block | nothing here: no rule of this family reads it | anything |

## 6. Entries, brackets, the walk and the labels

### 6.1 Latency: how 2 and 3 minutes are resolved

- **The bars are 1-minute**, each stamped with its open minute (feature-rules 1). An alert on a minute boundary reads
  the bars stamped at or before t - 1 minute, so **L = 2 and L = 3 are resolved exactly**: at m - 2 the side reads bars
  stamped to m - 3, at m - 3 to m - 4, at m - 5 to m - 6. Nothing finer than a minute is declared.
- **The entry does not move with L.** Every cell enters at P-16's mark m (a market order at the open of the first bar
  opening at or after m; a limit ticket live from m). **So the market pair values are the same walk for every L; only
  the side, read at t = m - L, differs.** The coin twin, the supply and the resolution of a market cell are identical
  across its three latencies, and the latency's whole effect is the fresher side.
- **The walks resolve L for the limit ticket** through its price (the close as of the alert, section 6.3) and its live
  slot m: the walker's `Order(LIMIT_ENTRY, side, live=m, price, cutoff)` takes any minute slot.
- **The twins at L** (section 14.3): `s3_latency.lagged_day_sides(..., latency=L)` at the marks m, and
  `s1_sided_coin.day_sides` at the alert m - L, both imported unchanged; a mark whose t - L < 0 ties (S3's own rule).
- **What a shorter latency asks of a user:** the order placed two or three minutes after the alert, by hand, at night.
  The operator accepted that (ruling 1 and 3); the scorecard does not model it (section 15).

### 6.2 The market entry (the reference entry) and its pair

- **Entry:** P-16's market entry at m, one tick charged as a cost (Stage 2's `slip_ticks`), both sides at the same
  price, so the mirror is a realisable market order and there is no fill-bar asymmetry.
- **Brackets:** P-16's stop, **150 ticks**; targets at R in **{1, 1.5, 3}** (the table's three asks), floor(R x S)
  ticks (`target_ticks`); pair values at every table R for C2.
- **The walk:** P-16's registered walk, `extended.walker.STAGE2` (`walk_offers`, F-03's), so design (ii) of a market
  `side` cell is P-16 itself and A0 holds the trades to P-16's pinned content hash. Beside: the fixed-barrier walk
  (`Rules("stage2_fixed", FLAT_ENTRY, "worst_less_two", breakeven=False)`) and Q-20's corrected move, deciding nothing.
- **The pair value** at each offer and R: `d = (win_long - win_short) / 2` in win probability (`win` = a target exit);
  net R `n = (r_long - r_short) / 2` beside. A side series `s_i` has lift over the coin twin `mean(s_i d_i)`.
- **The direction target** (fitted at R = 1 only, on the market walk): `y = 1` if the long's net R at R = 1 exceeds the
  short's, `y = 0` if below, out of the fit if equal. **The resolution target:** `T` = minutes from the entry bar's
  open to the first bar touching entry +- S (the walk's end if none); `y_res = 1` if `T` is at most the training fold's
  median.

### 6.3 The limit entry (the operator's ruling 4) and its pair

- **The ticket**, written at the alert t = m - L: a **limit on the cell's side** at `P = c_t - side x O`, where `c_t` is
  the close of the last bar stamped at or before t - 1 minute and **O = floor(S / 10) ticks = 15 ticks** (a buy limit
  below the alert's price, a sell limit above it). O is a declared choice -- a tenth of P-16's stop, contract
  arithmetic, neither fitted nor searched; another offset is another family.
- **Live from m = t + L** (the order's latency; the ticket published L minutes before it can fill); **it fills only on
  a bar trading through P by at least one tick, at P, never better** (`extended.walker.LIMIT_ENTRY`, `fill_order`);
  **void** if at m the price is already at or through P (marketable, the walker's `through`); **cancelled** at its
  cutoff: the earliest of m + 5 minutes (it may fill on the bars stamped m .. m + 4, the five minutes before the next
  P-16 mark), **a news window's start** (section 4.2), the bar closing at 08:30 CT, and the walk's end.
- **The walk** of a filled ticket: `STAGE2` with the resting fill-bar rule for the ticket's own outcome (a stop touch on
  the fill bar is a loss; a target touch there is not counted; feature-rules 3), the same stop, targets and costs (no
  entry tick: a limit has none).
- **The pair.** Each offer has **two tickets**: the buy limit at `c_t - O` and the sell limit at `c_t + O`, each walked
  on its own. The model's ticket is its side's; the coin twin's is the coin's side's. Each fills on a move against
  itself, so the fill-bar rule handicaps both alike; there is no mirror at a shared fill bar and so no pair-rule bias of
  the kind feature-rules 3 names (each ticket is its own trade). The share of filled tickets whose fill bar touched a
  barrier is reported beside per side.
  - `d_lim = (win_buy - win_sell) / 2`, a win the ticket filled **and** reached its target; an unfilled or void ticket
    counts 0;
  - `n_lim = (r_buy - r_sell) / 2` in net R, an unfilled or void ticket 0.
  - **Why both are read** (section 14.2): a side chosen where its ticket fills more often raises its win probability
    and its loss probability together, so a win-probability lift on limit tickets can exceed the money it makes. C1-n
    holds a limit cell to its net-R lift as well.
- **The direction model is not refitted for the limit entry:** a limit cell takes the same latency's market-trained
  model's side (section 9). The limit variant asks whether the same side is worth more resting than at market.

## 7. The features and their preparation

**The library:** `extended/features.py`, pinned by its sha256 at the pinning commit, through `compute_overnight` at the
alert slots max(0, m - L) (the overnight reading in its docstring: windows clipped at the trading day's 17:00 open,
nothing of the day at the 17:00 alert, `OVERNIGHT_UNDEFINED` NaN). `tests/test_features_overnight.py` holds it: the
shift test overnight (replace and delete the future at 17:00, the first minutes, the evening, the night, the 07:30 CT
release minute and 08:22-08:29, on a Monday's Sunday open, a roll day and the first CDT day, plus seeded minute cuts,
at every alert the three latencies use); each formula against the direct timestamp reference; availability as
`OVERNIGHT_FROM` documents; the RTH library bit for bit unchanged.

**B-ON uses 35 features:** the 37 defined overnight, less two dropped for the side's persistence (section 8.2):

<!-- bon-features:start -->
| feature | overnight | first overnight alert | a window before 17:00 |
|---|---|---|---|
| `ret_5` | as documented | 17:06 | NaN: its anchor close lies before the day's first bar |
| `ret_15` | as documented | 17:16 | NaN: its anchor close lies before the day's first bar |
| `ret_30` | as documented | 17:31 | NaN: its anchor close lies before the day's first bar |
| `ret_60` | as documented | 18:01 | NaN: its anchor close lies before the day's first bar |
| `ret_120` | as documented | 19:01 | NaN: its anchor close lies before the day's first bar |
| `ret_day` | as documented | 17:01 | the day's bars from 17:00 only (the halt has none) |
| `rng_15` | as documented | 17:01 | the day's bars from 17:00 only (the halt has none) |
| `rng_60` | as documented | 17:01 | the day's bars from 17:00 only (the halt has none) |
| `range_day` | as documented | 17:01 | the day's bars from 17:00 only (the halt has none) |
| `pos_day` | as documented | 17:01 | the day's bars from 17:00 only (the halt has none) |
| `pos_prior` | as documented | 17:01 | the day's bars from 17:00 only (the halt has none) |
| `d_pdh` | as documented | 17:01 | the day's bars from 17:00 only (the halt has none) |
| `d_pdl` | as documented | 17:01 | the day's bars from 17:00 only (the halt has none) |
| `d_pdc` | as documented | 17:01 | the day's bars from 17:00 only (the halt has none) |
| `d_round` | as documented | 17:01 | the day's bars from 17:00 only (the halt has none) |
| `vol_5` | as documented | 17:01 | the day's bars from 17:00 only (the halt has none) |
| `vol_30` | as documented | 17:01 | the day's bars from 17:00 only (the halt has none) |
| `vol_day` | as documented | 17:01 | the day's bars from 17:00 only (the halt has none) |
| `vol_accel` | as documented | 17:01 | the day's bars from 17:00 only (the halt has none) |
| `rv_ratio` | as documented | 17:03 | the day's bars from 17:00 only (the halt has none) |
| `rv_tod` | as documented | 17:03 | the day's bars from 17:00 only (the halt has none) |
| `rv_atr` | as documented | 17:03 | the day's bars from 17:00 only (the halt has none) |
| `atr_ratio` | as documented | 17:00 | none: built from earlier days or the calendar |
| `range_prior` | as documented | 17:00 | none: built from earlier days or the calendar |
| `ret_prior` | as documented | 17:00 | none: built from earlier days or the calendar |
| `ret_5d` | as documented | 17:00 | none: built from earlier days or the calendar |
| `ext_ma60` | as documented | 17:01 | the day's bars from 17:00 only (the halt has none) |
| `up_share_30` | as documented | 17:02 | the day's bars from 17:00 only (the halt has none) |
| `eff_30` | as documented | 17:31 | NaN: its anchor close lies before the day's first bar |
| `tod` | as documented | 17:00 | none: built from earlier days or the calendar |
| `dow` | as documented | 17:00 | none: built from earlier days or the calendar |
| `bls_day` | as documented | 17:00 | none: built from earlier days or the calendar |
| `bls_major` | as documented | 17:00 | none: built from earlier days or the calendar |
| `days_to_fomc` | as documented | 17:00 | none: built from earlier days or the calendar |
| `days_since_fomc` | as documented | 17:00 | none: built from earlier days or the calendar |
<!-- bon-features:end -->

Each line is `extended.features.describe_overnight()`'s for that feature (T-0 holds the table to it); each feature's
formula, window, normaliser and the bars it reads are `describe()`'s (F-B6 section 7's table). **Out of this family:**
- the ten `OVERNIGHT_UNDEFINED` (`ret_rth`, `range_rth`, `pos_rth`, `d_vwap`, `or_width`, `or_pos`, `d_onh`, `d_onl`,
  `range_on`, `gap`): no value at any overnight alert;
- **`ret_20d`** (a 20-session trend) and **`atr_rel`** (ATR against the price level, which follows volatility regimes
  of months): dropped for the side's persistence (section 8.2).

**`tod` overnight** is the same formula, (t - 08:30 CT) in hours, negative before 08:30. **What `c` and `atr14` are:**
F-B6 section 7's. The prior regular session after an early close is that partial session (F-B6 n3-4).

**Preparation, every statistic fitted inside the training fold only and applied out of fold** (F-B6 section 7, with
one indicator added):
1. each real feature winsorised at the training fold's 0.5 % and 99.5 % quantiles; standardised by its mean and sd;
2. `dow` as four indicators; the binary flags as they are;
3. two missing indicators: `m_cross` (a roll day: the cross-day features missing) and **`m_open`** (the alert lies
   before 19:01, where at least one windowed feature is NaN by `OVERNIGHT_FROM`); every remaining missing value set to
   0 after standardisation;
4. **the design matrix: 40 columns** (35 features, `dow` as four indicators, `m_cross`, `m_open`) and an unpenalised
   intercept. No feature is selected, transformed or dropped by data; a zero-variance column stops the fit (the failure
   protocol).

## 8. The side rule, and the side's persistence by construction

### 8.1 The side

- `z` is the direction model's linear score (its logit) at an offer.
- **The trailing threshold:** for session d, `med_d` = the session-weighted median of the model's scores over every
  population offer of **the 21 population sessions before d** (each session weight 1, shared equally over its offers),
  scored by the same model -- the fold's model at stage B, the frozen model at stage C. It reads features only (no
  outcome), of sessions before d only.
- **The side:** long if `z > med_d`, short if `z < med_d`, a seeded coin if equal (`[20262043, 0]`).
- **The intercept cancels exactly** (F-B6 section 10's proof): the median of a monotone map is the map of the median,
  so `sign(p - median p) = sign(z - med_d)` whatever the intercept and lambda.
- **The filter use:** an offer is offered only if `|z - med_d|` is at least `q_d`, the session-weighted 80th percentile
  of `|z_j - med_d|` over the same 21 sessions' offers j; at the model's side. About a fifth fire.
- **Warm-up.** A fold's first 21 test sessions read the 21 sessions before them, scored by that fold's model (the
  previous year's features). The judged block's first sessions read the last 21 choice-block population sessions,
  scored by the frozen model under `bon_stage_C_sides` (features only).

### 8.2 The persistence, declared before the pin (E-035 (6); Q-126 plan 2.5)

**Declared: the kind is a switching side; the band is "below 42 sessions"** (Q-126 plan 2.5's first row), the traded
share dense (every admitted offer of every traded session, a `side` cell; a `filter` cell's firing share stated beside).

**By construction:**
- **A level shift in the score cannot hold the side.** Any part of `z` that is constant across sessions, or shifts and
  then holds (a regime of a day-level feature, a volatility level, the intercept), is matched by `med_d` within the
  21-session window: after a shift the session's mean side leans for at most about half the window (the median moves
  once half its sessions are in the new level), then balances.
- **A lean can last only while the score keeps trending**, and the family drops the two inputs that trend for longer
  than its window: **`ret_20d`** (a 20-session sum) and **`atr_rel`** (volatility against the price level, whose regimes
  last months). Of what remains, the day-level inputs have memories of 1 session (`range_prior`, `ret_prior`), 5
  (`ret_5d`), 14 (`atr_ratio`, through `atr14`) or a calendar cycle shorter than the window (`dow`; `days_to_fomc` and
  `days_since_fomc`, each capped at 30 calendar days); the intraday ones vary within the session.
- **The filter's firing share** is held the same way: `q_d` follows the window's own spread.

**What the construction does not exclude, disclosed:** a score trending steadily for longer than the window through the
intraday features' slow drift (for example a months-long rise in overnight volatility relative to `atr14`, which
`atr14` itself follows within 14 sessions). The band check binds it:

- **At stage A**, on the out-of-fold sides of 2021-2023 (Q-126 plan 2.5's `band_check("switching", "below 42",
  block="choice", ...)`, `extended/lift_one_sample2.py` at the blob the adoption row pins, the span's own session
  count): **a cell whose sides miss the band is killed at stage A** -- after the pin there is no re-declaration (the
  plan allows one only before a pin, and this family's sides exist only after its fit). Recorded as "the band is not
  met by the out-of-fold sides".
- **At stage C**, on the pick's judged sides inside `bon_stage_C_sides`, before any outcome: a mismatch is **"not
  claimed"**, never a switch of band, kind or statistic (the plan 2.5).
- **Scope D's admission** (the plan 4.4, with its balance limit) applies where the adopted primary is scope D's: a cell
  not admitted at stage C is "not claimed" (no two-sample line is declared for C1).

**What T-0 shows, and does not** (`tests/test_bon_draft.py`, `test_the_trailing_threshold_bounds_a_slow_lean`): on a
synthetic block of 657 sessions with a planted two-state lean in the score (mean dwell 200 sessions), the side against
a fixed median holds the lean (its session mean side follows the state) and the side against the trailing median does
not (its session mean side is uncorrelated with the state outside the 21 sessions after each switch), and the trailing
side passes the band check for "below 42"; a steady trend in the score longer than the window leans the trailing side
and the band check refuses it on balance. **It also records a limit of the band check:** the fixed-median side under
that lean passes the check too -- its lean covers only the sessions of one state, inside the balance limit, and the band
has no upper runs limit -- so the check alone would not bind a one-state lean of that shape; **the construction is what
removes it, which is why this family declares it rather than relying on the check.** These are properties of the rule
on a toy, not a measurement of the market's sides.

## 9. The model, its search and the walk-forward

- **The model:** F-B6 section 9's L2-regularised logistic regression (session-weighted mean log loss, the intercept
  unpenalised, L-BFGS-B from zero with the analytic gradient, `gtol` 1e-10, at most 2,000 iterations, a non-converged
  fit refused; deterministic).
- **One direction model per latency**, fitted on the market walk's direction target at R = 1 with that latency's
  features. The limit cells use their latency's model (section 6.3). **The resolution model** (the control) at L = 5
  only.
- **Searched: lambda**, over **seven values `0.25 x 10^(j/2)`, j = -2..4**, per direction model and for the
  resolution model, inside the choice block only: the inner walk-forward with test years 2021, 2022, 2023, each trained
  on the population sessions before it less its last 22 sessions; the criterion the session-weighted out-of-fold log
  loss summed over the three test years; the smallest wins, a tie (within 1e-9) to the larger lambda; every
  configuration and its criterion written and **counted** (section 10).
- **Purge and embargo** (feature-rules 4): a label resolves by 15:10 CT of its own session and the longest feature
  window is 20 sessions (the time-of-day medians); the 22 sessions dropped before each test year cover both, and a
  forward walk needs no embargo after it.
- **The out-of-fold sides for stage B:** each fold's model on its test year, with the trailing threshold of section 8.
- **The final model:** refitted at each latency's chosen lambda on all the choice block's population sessions;
  serialised to canonical JSON and **hashed**, the hash pinned in a decision row before the judged read: its
  coefficients, the in-fold winsorising, standardising and imputing constants, and the resolution model's training
  median. No early stopping, no seed refits, no feature subset, no class weights.

## 10. The cells and the count

<!-- counted-cells -->
| factor | values | count |
|---|---|---|
| stop | 150 ticks (P-16's) | 1 |
| R | 1, 1.5, 3 | 3 |
| use | `side`, `filter` | 2 |
| latency L | 5 (reference), 3, 2 minutes | 3 |
| entry | market (reference), limit | 2 |
| **cells** | 1 x 3 x 2 x 3 x 2 | **36** |
| searched: direction lambda | 7 values x 3 latencies | 21 |
| searched: resolution lambda | 7 values at L = 5 | 7 |
| **searched configurations** | 21 + 7 | **28** |
| **recorded in the trial count** | 36 + 28 | **64** |
<!-- end counted-cells -->

- **Every cell is counted** whether it is killed or read; one cell reaches judgement. Within a latency and a use, the
  market cells' trades are the same at every R (R decides the bracket C1 reads and the places C2 prices).
- **The variants are in the multiplicity correction** by stage B's family-wise maximum over all surviving cells
  (section 12): the pick is chosen from all 36 cells under one studentised maximum, and judged once at the family's
  level. The program's level for the family is 0.05 / (k (k + 1)) whatever the cell count; the cell count costs Kill
  B's critical value and the conjoint MDL, which are computed over every cell.
- **If the latency row of section 0.1 item 3 is not recorded before the pin,** the 24 cells at L = 3 and L = 2 and the
  14 direction configurations of those two latencies are struck before the pin (12 cells and 14 configurations -- 7
  direction at L = 5 and 7 resolution -- remain), and this table is re-counted in the pinning text -- a change made
  before any read, so not a variant.
- **Not trials, since nothing is chosen from them:** the controls (the canary, the join assertion, K0 and the count
  checks, the band checks, the conjoint MDL's draws, B2's replicates), the twins, the 5-minute sibling beside the pick
  and the readings beside.

## 11. Stage A: the gates, before any lift is read (choice block)

1. **The dependencies hold, refusing** (section 23's run order): the reader; the identities (section 22); the pinned
   blobs; the news windows' inputs.
2. **K1 supply.** A `side` cell: at least 12 offers a year in every calendar year 2020-2023; a `filter` cell and a limit
   cell: the same, counted on their out-of-fold fired offers (a limit cell: offers whose model-side ticket fills) in
   2021, 2022 and 2023. Else killed.
3. **K2 resolution.** The share flattened unresolved, both sides pooled (a limit cell: its filled tickets of both
   sides), at every R in {1, 1.5, 3}, at most 5 % in each choice year. Else killed; nothing is re-cut.
4. **K3 realised risk** (D-308): reported.
5. **The positive control:** the resolution model's out-of-fold AUC on 2021-2023, its one-sided 95 % lower bound by
   stage B's bootstrap (`[20262040, 0]`) above 0.5; else the failure protocol before stage B.
6. **The join assertion, refusing** (F-B6 8 item 6): every label row's (session, entry mark) equals its feature row's
   (session, max(0, alert) + L at the mark), every pair value's and ticket's session and mark equal its side's.
7. **The null canary** (F-B6 8 item 7) at each latency: the whole direction pipeline on the choice block with the long's
   and the short's outcomes swapped in every 63-session block a seeded coin picks (`[20262041, 0]`), its maximum
   studentised lift against the 99.9th percentile of 10,000 centred bootstrap draws of its own data (`[20262041, 1]`);
   above it is a defect signal and the failure protocol runs.
8. **The band check** (section 8.2), on each surviving cell's out-of-fold sides: a miss kills the cell.
9. **The conjoint MDL** (F-B6 8 item 8), per surviving cell, before any lift: every deciding line together -- C1, C1-n
   for a limit cell, C1-d, C1-f against each twin and C2 by its proxy -- at the adopted statistic's critical values (the
   larger of nominal and B2's on the proxy), on the out-of-fold sides laid on the judged calendar by a stationary
   bootstrap of whole sessions (mean block 63; draw i `[20262040, 5, i]`), the planted lift `d -> d + L s`, the sign
   flips per 63-session block (`[20262040, 2, i]`), B2 on the proxy at 200,000 replicates per line in 20 ordered chunks
   (`[20262040, 6, j, c]`), C2's proxy places from **p16**'s `trades_per_year_records` shares (`[20262040, 7, i]`);
   the smallest L on the grid 0.0025 .. 0.25 at which at least 80 % of 2,000 draws pass every line.
   - **The screen rule:** if the conjoint MDL exceeds the value bar (`u_value_map.csv` section `bar`, base `p16`, at the
     cell's uses) by more than a factor of 3 at every surviving cell, the family is **declared a screen** (section 16).
10. **The pre-pin power gate** (before the pin, from the calibration's power file only; section 0's condition 2): for
    each (R, use) at the family's declared supply -- P-16's admitted overnight offers per session times the choice
    block's walked sessions a year, a count from the registration's marks and A1's day kinds, no outcome -- Q-126's MDL
    at k = 15 for the adopted statistic (plan 5's definition, `q126_cal_power.csv`) against the value bar at base
    `p16`. **If it exceeds the bar by more than a factor of 3 at every (R, use), the family is closed before its pin,
    taking no k** (as family R closed, E-086). The gate reads no bar and no outcome of this family. Its code is the
    shared module (Q-142 section 3, wt-verify).
11. **K0, fill intensity (E-052), run after items 2-4 and before items 5-10:** each cell's
    per-session counts on the choice block (a `side` market cell: its admitted marks less missing bars; a `filter` or
    limit cell: its out-of-fold fired or filled offers in 2021-2023), the adopted statistic's size at the family's level
    on Q-16's `cluster` null at those counts laid on the judged calendar at random circular offsets, 200,000 replications
    (`[20262040, 9, c]`, c the cell's index in section 10's order), the 95 % Clopper-Pearson interval; a cell whose
    interval lies wholly above the level is killed.

## 12. Stage B: choose on the choice block (2021-2023, out of fold)

- **The statistic** (F-B6 section 11): for each cell surviving stage A, `L_c` = the mean over the cell's offers of `s_i
  d_i` (a limit cell: `s_i d_lim,i`); a stationary bootstrap of sessions with mean block 63, 2,000 draws
  (`[20262042, 0]`); `SE_c` the draws' sd; **the family-wise critical value `q`** = the 95th percentile over the
  centred draws of **the maximum over all surviving cells** -- every R, use, latency and entry -- of `(L*_c - L_c) /
  SE_c`; Benjamini-Hochberg at 10 % beside, never selecting.
- **Kill B:** no cell with `L_c / SE_c > q` -- the family closes and the judged block is not read.
- **Reported for every cell before the pick:** each fold's long share, the run lengths of the out-of-fold sides, the
  band check's runs and mean side, the variances of the 21-, 63- and 126-session mean side, and for a limit cell the
  fill shares of the model's tickets and of each side's.
- **Eligible as the pick:** a cell whose worst choice year leaves at most 4 % unresolved at every R in {1, 1.5, 3}, and
  for a limit cell whose `n_lim` lift is above zero on the choice block (C1-n's direction).
- **The pick:** among the eligible cells above `q`, the largest first-order valued lift at its lower limit `L_c - q
  SE_c` (F-B6 section 11's formula, base **`p16`**, u the cell's offers a year on the choice block, the places that
  ask the cell's R). **Its 5-minute sibling** -- the same R, use and entry at L = 5 -- is fixed with it (section 14.5),
  and is the pick itself when the pick is at L = 5.

## 13. Stage B2: the critical values, conditional on the judged sides

F-B6 section 12's construction, unchanged but for these points:
- **The statistic is the adopted one-sample statistic** (Q-126's adoption row; its components and its margin as
  adopted), each component's critical value the larger of its nominal and B2's simulated (1 - level) quantile, always;
  the wrapper is the adopted statistic's form of F-B6's `cons_bound_with_critical`.
- **The pair values** are resampled from the choice block's session vectors at the pick's bracket (a limit pick: its
  latency's ticket pairs `d_lim` and `n_lim`), centred, plus the declared slow drift `a*(R) x rho_t` (1/250 a session).
- **C1-f's two slow components, centred within each replicate's judged block, its null (A)** (E-051), its amplitude
  rule (a), `g*_pre`, (d), `g*_post` as F-B6 12 states them.
- **The seeds:** line j's chunk c from `default_rng([20262045, j, c])` (C1-f: `[20262045, j, a, c]`), with j = 0 C1,
  1 C1-d, 2-4 C1-f against `lnbar1x4`, `lbrk5`, `mom15`, 5 C2 at design (i), 6 C2 at design (ii), 7 C1-n (a limit pick
  only); the confirmation 10 + j; **1,000,000 replicates per line and amplitude in 100 ordered chunks of 10,000**, the
  draw order and the quantile as F-B6 12 (m5-2).
- **The count checks (E-052):** the pick's judged counts `[20262045, 20]`, C2's routed counts `[20262045, 21]` and
  `[20262045, 22]`, the confirmation's `[20262045, 30]`.

## 14. Stage C: judge the pick once, on the judged block (2024-01-02 to 2026-07-16)

### 14.1 The order (one clean run; the reader ledgers each purpose before it reads)

1. `bon_stage_C_sides`: every side series hashed (the model's, the filter's selection, the three twins'), for the pick
   and its 5-minute sibling; **the band check** (section 8.2) and, where the primary is scope D's, the plan 4.4's
   admission, on the pick's sides; **the judged-count check** (`[20262045, 20]`) -- all before any outcome;
2. B2 for C1, C1-d (and C1-n for a limit pick);
3. `bon_stage_C_judgement`: the pair values or tickets; C1, C1-n, C1-d;
4. the twins' judged yearly lifts and (d); B2 for C1-f at `g*_pre` and `g*_post`; C1-f;
5. `bon_stage_C_campaign`: the gate campaigns of designs (i) and (ii) (500 paths, seed `[20262046, 0]`, the bound arm,
   recorded by the place-recording adapter with `shifts=("lower_bound",)`, `levels=(0.0,)`);
6. the count checks on C2's routed counts; B2 for C2 at each routing; C2 and the floors;
7. `bon_stage_C_scorecard`.

The judged calendar is Q-83's pinned session list (E-094's count and sha256, asserted); the adopted statistic's blocks
cover every session, none dropped; empty sessions count with `S = N = 0`.

### 14.2 The lines -- the design passes only if every line holds; a fail of any closes the family

Each line is read by the adopted one-sample statistic at the family's level 0.05 / (k (k + 1)), each component at the
larger of its nominal and B2's critical value.

- **C1, the pass line (CHARTER 3, E-008):** `x_i = s_i d_i` (a limit pick: `s_i d_lim,i`); the lower bound above zero.
- **C1-n, a limit pick only:** `x_i = s_i n_lim,i` in net R; the lower bound above zero. (A market pick reports its
  net-R lift beside.)
- **C1-d, drift-matched:** `x_i = (s_i - s_bar) d_i`; **if `abs(s_bar)` is at least 0.9, C1-d fails.**
- **C1-f, beyond each known follow effect, at the pick's latency:** for each twin r, `x_i = (s_i - f_i^r) d_i` on the
  same offers, null (A), the realised paired lift (E-051); three lines in an intersection-union.
- **C2, worth something where it is used:** the gate campaigns of design (i) (the model's sides) and design (ii) (the
  coin's sides on the same offers and entry), each recording for every simulated trade its offer, its R and its place
  (b) evaluation, (c) the funded account's first trade, (d) funded later before the first payout, (e) paid; the per-trade
  value `v_j = mean_dv(p(j)) x s_i(j) x d_i(j)(R_j)` at **base `p16`** (a limit pick: `d_lim`); the bound at either routing
  by the adopted statistic with B2 at that routing, times that routing's trades a year; **the line: the lesser of the
  two dollar bounds, at least $500 a year** (F-B6 13's reason: design (i)'s routing selects on its own outcomes).
- **The floors** (CHARTER 3): every offered R resolving on the judged block, at most 5 % in 2024, 2025 and 2026 to
  07-16 (a year with fewer than 63 sessions pooled with its neighbour, D-604); the long-run gate (growth on the required
  bankroll at the bound above zero, D-145) from design (i)'s campaign; every firm rule verified; conduct tier 1; **the
  news rule checked at zero** (section 4.2: no order live inside a window, no fill inside one; a nonzero count is an
  engine error); the count checks -- an interval wholly above the level withholds the pass.
- **"Not claimed"** if the band check or the admission refuses the pick's judged sides (section 8.2).

### 14.3 The follow twins, at the pick's latency

| twin | Stage 2's rule | read by (imported unchanged) |
|---|---|---|
| `lnbar1x4` | the side of the most recent 1-minute 4-bar `nbar` event, followed | `s3_latency.lagged_day_sides(..., latency=L)` at the entry marks m |
| `lbrk5` | the side of the most recent 5-minute `brk` event, followed | `s1_sided_coin.day_sides` at the alert m - L |
| `mom15` | `sign(c[t] - c[t-15])`, followed | `s1_sided_coin.day_sides` at the alert m - L |

A zero is a tie (`f = 0`); a mark whose alert falls before the day's first bar ties. The build checks that at L = 0
they reproduce S1's and S3's side tables on P-16's marks (`shift_problems`) and that at the alert they read only bars
ending at or before it.

### 14.4 Beside, deciding nothing

- the lifts in net R; by calendar year; on each session's first offer; by hour of the night (17:00-01:59, 02:00-07:29,
  07:30-08:25 CT); C2's place-by-place parts at both routings;
- the filter's judged share and the conjoint MDL recomputed at it;
- the judged sides' persistence measures (F-B6 12's flag, `[20262040, 3]`, and its lean band `[20262040, 4]`);
- the seeded coin twin (`[20262044, 0]`); a model fitted on the three twins' sides alone on the choice block, applied to
  the judged block, and the lift over it;
- the other walks (fixed barriers; Q-20's corrected move);
- for a limit pick: the fill shares by side, the void share, the share of fills whose fill bar touched a barrier;
- the FOMC minutes count and RD-01 G-3's bracket (section 4.2);
- the resolution model's judged AUC; the denial ladder; the placement on.

### 14.5 The 5-minute cell beside every pick (the operator's ruling 3)

The pick's **5-minute sibling** (the same R, use and entry at L = 5; fixed at stage B) is read on the same judged
offers under the same purposes: every line of 14.2 with its own B2 (seeds `[20262047, j, c]`, the same j map), its band
check, its count check and its C2 (the same campaigns' routing of its sides, design (i') recorded beside), and its
scorecard beside. **It decides nothing**: a pass of the pick is the pick's; the sibling's lines show what the shorter
latency added. When the pick is at L = 5, the sibling is the pick and nothing more is read.

## 15. The journey scorecard -- beside every judgement, never the pass line

F-B6 section 14's scorecard, with these designs and comparisons:
- **(i) the pick at the model's sides** (a `filter` pick: its fired offers; a limit pick: its filled tickets), and
  **(ii) the same offers and entry at P-16's registered coin's sides** -- for a market `side` pick, design (ii) is
  **P-16 itself**; (i') the 5-minute sibling beside;
- Stage 2's RC runner (P-16's design: the no-closure state table, the strict router, five seats, the purchase budget,
  the fees, the R of every trade set by the table), the gate campaign at `[20262046, 0]`, 500 paths, the verdict arm,
  payout denial 0 %, the placement off; journeys by the vendored U1 replay and Q-17's adapter;
- **identity first, refusing:** the runner with P-16's own coin reproduces P-16's registered rows and U1 start rows;
- read **against P-16** (the coin twin's own design) **and against R\* = P-14**, on the judged block's starts, with
  2021-2023's out-of-fold starts beside (journeys truncated at 2023-12-29, labelled);
- P and the guarded measures, the journey variables, every measure a distribution over start days with its
  uncertainty, the frontier, the menu (E-015's limits as flags only), the evenness trade-off, E-007 (e)'s readings,
  Stage 2 D-621 (3)'s rule against P-14 beside;
- **not modelled, said wherever the scorecard appears:** a user who stops when their own money runs out, **the user's
  time -- including that this design is traded by hand at night, which the operator accepted on 2026-11-18** -- and
  taxes.

## 16. What a pass and a fail mean

- **CARRIED** (every line of 14.2 and the floors) is a development finding on a late-development block. It takes a
  registration id, a model card, its registered development test, the auditor, and **one confirmation** (section 17).
  A family declared a screen (11.9) that passes is still CARRIED, its row saying it was a screen at its MDL ratio.
- **CLOSED** before the pin (the power gate, 11.10: no k taken), at stage A (no cell survives), B (Kill B) or C (any
  line or floor), the reason in a decision row. A close at B or C reads **"no lift above the conjoint MDL at this
  family's level"**, never "no lift"; a close on C1-f names the twin and its null (A); a band-check kill reads "the band
  is not met"; a K0 kill or a withheld count check reads "the test's level is not established for these counts".
- **"Not claimed"** (14.2) is not a pass and is recorded as such.
- **The closure binds:** a later family on these offers and these features names this closure, says what changed and
  why it is a different hypothesis, and is not judged on this family's judged block.

## 17. The confirmation, declared before any development read

F-B6 section 16, with this family's pick: the window **NQ from 2026-07-17**, not on disk, never read until a carried
candidate is registered, **a purchase, the operator's**, and a confirmation window other drafts also target (the lead
records any earlier read before registration). C1, C1-n (a limit pick), C1-d and the three C1-f on the window's offers,
one-sided at 0.05 as achieved by the adopted statistic's shortest component at the larger of 1.3 times its nominal and
B2 (`[20262045, 10 + j, c]`); the count check `[20262045, 30]`; C2 the lesser routing at the 95 % bound; resolution at
most 5 %; P not tested (six months hold no interval on P). **The months to buy** are section 11.9's conjoint
computation at the confirmation's form (draws `[20262040, 8, n, 0, i]`, B2 `[20262040, 8, n, 1, j, c]`), written in
the carrying row before any confirmation data exist; if more than the operator will buy, no confirmation is registered.

## 18. Parameters: fixed / searched / dropped

| parameter | what it is, in a phrase | class | value | source |
|---|---|---|---|---|
| market, bars | what is traded and read | fixed | NQ 1-minute bars; MNQ micros sized by the table | E-002 |
| development window | the only data read | fixed | 2020-01-02 .. 2026-07-16 | CLAUDE.md |
| choice / judged blocks | where choices are made / the one judgement | fixed | 2020-01-02 .. 2023-12-29 / 2024-01-02 .. 2026-07-16 | CHARTER 3 |
| offers | where the family trades | fixed | P-16's admitted marks at 150 ticks, 17:00 .. 08:25 CT, kinds `n` and `b`, a report day's from 07:40 | F-03's population; P-16's registration |
| entry mark m | when an order fills | fixed | P-16's mark | P-16 |
| **latency L** | minutes from alert to order | **fixed grid, counted** | **5 (reference), 3, 2** | CHARTER 4; the operator 2026-11-18 |
| alert | when the side is computed | fixed | t = m - L; the 17:00 alert's row for m - L < 0 | section 3 |
| **entry** | how the order is placed | **fixed grid, counted** | **market (reference); limit** | the operator 2026-11-18 |
| limit offset O | how far from the alert's close a limit rests | fixed | floor(S / 10) = 15 ticks | section 6.3 (a declared choice) |
| limit life | how long an unfilled limit works | fixed | to the earliest of m + 5, a window's start, 08:30 CT, the walk's end | section 6.3 |
| news windows | when no order may work | fixed rule | W-1, W-2; W-3 from the verified ledger only (none at Topstep's $50K today) | section 4.2; E-200 R-1 |
| flatten at a window | a position open at its start | fixed | the bar stamped at its first minute, at its open, the flatten slippage | RD-05 A-18 |
| stop | the loss distance | fixed | 150 ticks | P-16 |
| R | target over stop | fixed | 1, 1.5, 3 | the table's asks |
| training R | the label's bracket | fixed | 1 | section 6.2 |
| the walk | how a trade ends | fixed | `STAGE2` (P-16's); a limit fill's own resting rule | E-011 |
| costs | fees and slippage | fixed | Stage 2's (`fee_by_stop`, `fills.yaml`) | E-010 |
| features | what the model sees | fixed | 35 of `compute_overnight` (section 7) | section 7 |
| preprocessing | scaling inside the fold | fixed | winsorise 0.5/99.5 %, standardise, `dow` indicators, `m_cross`, `m_open`, impute 0 | section 7 |
| model | the classifier | fixed | L2 logistic, session-weighted, L-BFGS-B | F-B6 9 |
| **lambda** | how hard the coefficients are shrunk | **searched** | 0.25 x 10^(j/2), j = -2..4, per latency's direction model and for the resolution model; inner walk-forward 2021-2023 | section 9 |
| side rule | prediction to side | fixed | `sign(z - med_d)`, `med_d` the trailing 21 sessions' median score | section 8.1 |
| filter | how confident to trade | fixed | `abs(z - med_d)` at or above the trailing 21 sessions' 80th percentile | section 8.1 |
| persistence | the side's declared band | fixed | switching side, below 42 sessions | section 8.2; Q-126 plan 2.5 |
| C1, C1-n, C1-d, C1-f, C2 | the lines | fixed | section 14.2, the adopted statistic at 0.05 / (k (k + 1)) | E-008 |
| stage B | the family-wise screen | fixed | offer-mean lift; stationary bootstrap, mean block 63, 2,000 draws, centred, studentised maximum over all cells | F-B6 11 |
| valuation base | where a win is priced | fixed | `p16` | `u_value_map.csv` |
| the value bar | the least worth | fixed | $500 a year at the bound, the lesser routing | F-B6 13 |
| MDL factor | when the family is a screen; the power gate | fixed | 3 | R-16 |
| `ret_20d`, `atr_rel` | two features | **dropped** | -- | the side's persistence (section 8.2) |
| the ten overnight-undefined features | the frozen 08:30 levels and the session's own | **dropped** | -- | no overnight value |
| other stops; R 0.25, 2, 2.5 as cells | other brackets | **dropped** | -- | P-16's stop; the table's asks |
| a fixed training-median threshold | F-B6's p~ | **dropped** | -- | a level shift in the score would hold the side (section 8.2) |
| a limit model of its own | refitting on the limit label | **dropped** | -- | more searched configurations; the side question is the same |
| latencies other than 5, 3, 2; a stop entry | other variants | **dropped** | -- | not ruled by the operator; each another family |
| the opening half-hour's marks (F-03's labels) | P-16's 08:30-09:00 marks | **dropped** | -- | D-281 (3)'s default (section 4.3) |
| interactions, feature selection, class weights, early stopping, seed refits | other model freedoms | **dropped** | -- | each a hidden search |

## 19. Open before the pin -- the operator's and the lead's (the section-19 items)

**Answered by the operator (2026-11-18), to be recorded in the lead's rows:**
1. **Night hand entry and the user's time.** B-ON trades overnight, so a user hand-enters orders at night.
   **Answered: accepted** -- the operator wants executions at every hour of the day. The user's time stays out of the
   model, as CHARTER section 2 says; the scorecard says so (section 15). Closed.
2. **News** (the operator's ruling 2): declared in section 4.2.
3. **Latency 5, 3 and 2 minutes** (ruling 3): declared in sections 6.1 and 10. **The lead's row owed:** CHARTER
   section 4 states "at least five minutes from alert to order"; the row records the operator's ruling and whether
   CHARTER's line is amended for this family's 2- and 3-minute cells. Without it those cells are struck before the pin
   (section 10).
   - The limit variant (ruling 4): declared in section 6.3.

**The lead's, before the pin:**
4. **The FOMC minutes** are not a window by default (no verified rule at this account names them); the lead may rule
   them a window, which would add them to W-3's rule from E-050's pinned calendar before the pin.
5. **Releases at 10:00 ET** have no pinned calendar here; none is applied. A calendar pinned under a row before the pin
   could be added; none is assumed.
6. **D-281 (3)** -- the operator may rule; the default of section 4.3 stands until then (entries and features out of the
   half-hour; holdings through it disclosed).
7. **Q-126's adoption row** for the band "below 42 sessions", naming the statistic and its blob; **the power gate**
   (11.10); **Q-122's** readings beside, if built before the pin.
8. **The limit offset and life** (section 6.3) are declared choices; the red team may question them; a change is made
   only before the pin.
9. **A red-team read** of this text (look-ahead at the 17:00 alert, the trailing threshold's warm-up reads, the limit
   pair's estimand and C1-n, the latency variants' count), then the gatekeeper and **k**.
10. **The seeds** confirmed unique at the pin (T-0).
11. **NQ from 2026-07-17** as a confirmation window and its purchase -- the operator's, only once a pick is carried.

## 20. The count, the family number and the level

- **Cells: k_cells = 1 x 3 x 2 x 3 x 2 = 36**, each counted whether killed or read (section 10).
- **Searched configurations: 28** (21 direction, 7 resolution). **Recorded: 64.**
- **The family number:** proposed k = 15; the gatekeeper's count at the pin. **The level: 0.05 / (k (k + 1))**, 0.05 /
  240 at k = 15, inside Q-126's calibrated range k = 13 .. 20 (its section 7 item 5).
- **One cell reaches judgement;** its lines are an intersection at one level; stage B spends nothing of the program's
  budget.
- **If the latency row is missing** (section 0.1 item 3): 12 cells, 14 searched configurations, 26 recorded -- the same
  k and level.
- **The program's honesty sentence:** the development level is a screening threshold; the decision is carried by one
  confirmation on unread data (D-189).

## 21. Seeds -- the block 20262040-20262049, checked unique on 2026-11-18

| seed | status | what it draws |
|---|---|---|
| 20262040 | in use | stage A and the months: `[20262040, 0]` the positive control's bootstrap; `[20262040, 2, i]` the MDL's sign flips; `[20262040, 3]` the persistence flag's permutations; `[20262040, 4]` the lean band; `[20262040, 5, i]` the conjoint MDL's proxy calendar; `[20262040, 6, j, c]` its B2; `[20262040, 7, i]` C2's proxy places; `[20262040, 8, n, 0, i]` and `[20262040, 8, n, 1, j, c]` the confirmation's months; `[20262040, 9, c]` K0 |
| 20262041 | in use | the null canary: `[20262041, 0]` its block swaps, `[20262041, 1]` its centred bootstrap |
| 20262042 | in use | stage B's bootstrap `[20262042, 0]` |
| 20262043 | in use | a tie `z = med_d` (the coin) `[20262043, 0]` |
| 20262044 | in use | the seeded coin twin beside `[20262044, 0]` |
| 20262045 | in use | stage B2, mapped to lines (section 13), and the count checks `[20262045, 20..22, 30]` |
| 20262046 | in use | the gate campaigns of designs (i), (ii) and (i'): C2's routings, the long-run gate floor, the scorecard; 500 paths |
| 20262047 | in use | the 5-minute sibling's B2 `[20262047, j, c]` |
| 20262048 | in use | the build's tests: `tests/test_features_overnight.py` (child streams `SeedSequence(20262048, spawn_key=(stream, i))`, streams 0-7) and T-0's synthetic demonstration (`tests/test_bon_draft.py`, streams 20-21, built by arithmetic) |
| 20262049 | in use | the planted-effect test T-14 |

**The check.** On 2026-11-18, a word-bounded search for `2026204[0-9]` found none of these seeds in any tracked file on
any branch or remote ref (`git grep -lowE` over every ref), nor in any working file of the main tree, of every worktree
under `%LOCALAPPDATA%\stage2-extended-wt` or of every clean-run checkout under `%LOCALAPPDATA%\stage2-extended-runs`
(the licensed data excluded) -- before this file and its two test files were written. RD-05's block and the blocks of
every other declaration are distinct; RL3's draft had no file on wt-levels at that time, so the lead checks RL3's block
against this one when both are drafted. **Inherited, used only as their owners registered them:** P-16's coin
(`resolved_coin.COIN_SEED`, design (ii)) and the identities' seeds, named by role. T-0 re-runs the check on every run of
the fast tier.

## 22. The build's identities and tests (after the pin, before any reading)

1. **The walker:** E-011's identity at the build's commit; F-03's `walk_offers` under `STAGE2` reproduces P-16's trades
   on the two spans to P-16's pinned content hash (F-03's A0 item 1).
2. **The features:** `tests/test_features.py`, `tests/test_features_lookahead.py` (its slow 790-cut test included),
   `tests/test_features_perf.py` and **`tests/test_features_overnight.py`** pass at the pinned `extended/features.py`.
3. **The alert map:** every offer's feature row is the row at max(0, m - L), and at L = 2, 3, 5 the side reads no bar
   stamped at or after m - L (a shift test at the alert map's own level, on synthetic bars).
4. **The limit tickets:** on synthetic days, `fill_order` with `LIMIT_ENTRY` at `c_t -+ O`, live m, cutoff the earliest
   of section 6.3's, reproduces hand-built fills, voids and cancellations (a window's start among them); the pair's two
   tickets are walked independently; an unfilled ticket is 0 in `d_lim` and `n_lim`.
5. **The news rule:** RD-05 T-4's or T-7's toy cases each way (E-200 R-1): no order live inside a window, a working
   order cancelled at its start, a position flattened at the bar stamped at its first minute; W-1 and W-2 counted at
   zero on P-16's population.
6. **The twins:** imported unchanged; at L = 0 they reproduce S1's and S3's side tables on P-16's marks; at L = 2, 3, 5
   they read only bars ending at or before the alert.
7. **The logistic and the side rule:** a Newton solve agrees to 1e-8; a planted coefficient is recovered; the
   intercept cancels against the trailing median exactly; the trailing threshold reads no score of session d or later.
8. **A planted effect (T-14, `[20262049, ...]`):** on synthetic bars with a direction effect tied to a feature, the
   pipeline recovers it at every latency with the right sign; C1-f against a twin carrying the same effect does not
   pass; on a driftless walk the lift is zero within its interval; a planted look-ahead feature fails the shift test; a
   misaligned join is refused; a planted fill-rate side (a side chosen where its limit ticket fills, with no direction)
   passes no C1-n.
9. **B2, the conjoint MDL and K0:** F-B6 20 items 8, 15 and 16 at the adopted statistic.
10. **The place recorder:** E-055's identities, at base `p16`.
11. **Choice-stage invariance (T-3, heavy):** stages A and B and the final models are byte-identical when every judged
    bar is replaced by a seeded synthetic walk.
12. **The judge cannot fit (T-7);** the reader refuses its fitting or choosing purposes on the judged block.
13. **The scorecard's identity:** the runner with P-16's coin reproduces P-16's registered rows and U1 start rows.
14. **The judged calendar:** Q-83's count and sha256 asserted; the level against `lift_bound.family_level(k)`.

## 23. The run order, refusals first, and the memory bounds

**Refusals, each before anything heavy starts, in this order** (a refusal stops the run; none is retried to pass):
1. the declaration's LF sha256 equals the pinning row's; `tests/test_declarations_fixed.py` passes;
2. the adoption row of Q-126 exists and names the band "below 42 sessions", the statistic and the blob of
   `extended/lift_one_sample2.py`, and the blob in the tree is that one;
3. the power gate's row exists and records a pass (11.10);
4. the latency row exists (section 0.1 item 3), or the run's cell list holds the L = 5 cells only;
5. the tree is a clean checkout of a committed commit (`scripts/run_clean.py`), `git status` empty;
6. vendor integrity (`tests/test_vendor_integrity.py`); the bars' and atlas' data manifest;
7. the reader's seal: no read from 2026-07-17; no judged read in runs A0 and 1;
8. the pinned blobs: `extended/features.py`, `extended/opening_population.py`, `extended/walker.py`, the reader;
9. P-16's screen file's sha256 (`admitted_marks`); Q-83's judged session list; the BLS, FOMC and early-close calendars'
   pinned hashes; the verified ledger's news keys at the account (W-3: none, or the pinning row's);
10. the run lock is free and the machine has the declared memory (`python scripts/run_lock.py take ... --mem-gb 2.5`).

**Then, one heavy run at a time, each watched to its exit:**
- **A0** (identities): the walker's and P-16's trades hash (22 item 1), the twins' tables (item 6), the scorecard's
  identity (item 13), the place recorder's (item 10).
- **Run 1** (choice block): the features in chunks of one year; the walks (market, and the limit tickets at each L);
  stage A (supply and K0 before anything else; then K2, K3, the positive control, the join, the canary, the band check,
  the conjoint MDL); stage B; the final models hashed. Then the auditor; then the pinning row of the model hashes.
- **Run 2** (judged block), only if Kill B passed: stage C in section 14.1's order, then the scorecard.

**Memory, declared bounds (each process at most 2.5 GB, measured by `extended.procmem` and logged):**
- the overnight features in chunks of one year (`compute_chunked(..., overnight=True)`), as float64, one latency at a
  time: a year's rows are its sessions times the alerts of one latency, the 186 overnight marks;
- the walks in chunks of `opening_population.CHUNK_DAYS` sessions, as F-03's build;
- B2 and the conjoint MDL in 10,000-replicate chunks, never holding more than one chunk's draws per line;
- the campaigns at 500 paths with the recorder's `columns=` subset (E-055);
- `OMP_NUM_THREADS` at most 2; at most 2 worker processes. A step whose measured peak exceeds 2.5 GB stops (a failed
  check, diagnosed, never rerun to pass).

## 24. Outputs

- `results/bon_model.csv` (sections `supply`, `resolution`, `controls`, `band`, `power`, `search`, `choice`, `sides`,
  `persistence`, `b2`, `judged`, `sibling`, `beside`) and `results/bon_scorecard.csv`, each with its sidecar manifest
  (`extended.results.write_result`, `prereg_id` the F-id, the cell count, every seed and parameter); the pinned models'
  hashes and the judged sides' hash in the judged manifest; the reader's ledger lines for each judged purpose.

## 25. Anything chosen after seeing results

*(Empty. Anything added after a reading is exploratory, reported apart, `exploratory=True` in its manifest, and recorded
in its own decision row -- never added to this file once pinned.)*
