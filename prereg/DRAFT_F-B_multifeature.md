# DRAFT F-B: one multi-feature model on P-16's offers (family B) -- a draft for the red team, not a declaration

**Status: DRAFT, written 2026-11-15 by the Q-11 worker (wt-features) for the red team and the lead. Not pinned, no
F-number, no seeds.** Nothing of the family is built beyond the feature library it names (`extended/features.py`,
Q-11, built and tested on synthetic bars only); no bar has been read for it, no label computed, no model fitted, no
outcome of anything seen. This file may be edited until the lead pins it; from the pinning row on, nothing in it is
edited (a change is a new family). Seeds are written `<to be fixed at pinning>`. The family number is **k = the next
free (11 if pinned next)**, so the level is one-sided **0.05 / (k (k + 1))** (0.05 / 132 at k = 11).

It follows `vendor/stage2/prereg/TEMPLATE.md` and `FAMILY_TEMPLATE.md` as this repository adapts them after E-008 (the
pass line is the trades' calibrated lift over the coin twin; the user scorecard is reported beside), with the Phase 0
audit's sections (`docs/audits/phase0/D_protocol.md` Part 3: prior exposure, parameter classes, seeds, count,
confirmation) and CHARTER section 2's journey scorecard (E-014, E-015).

---

## 0. In plain words (for the operator)

P-16 offers a trade every five minutes and lets a fair coin choose long or short. This family asks one question:
**can a model that looks only at the last few hours and days of NQ's price and volume choose the side better than the
coin, on the same trades, by enough to be worth money?** The model is a simple, pre-registered one (a regularised
logistic regression on 47 measurements of the market, each scaled to the market's own recent volatility or volume).
It is trained only on 2020-2023, frozen, and then judged once on 2024-01-02 to 2026-07-16, a period it never saw. It
passes only if its side beats the coin's on those trades with a margin no chance result of this size would show
(one-sided at 0.05 / (k (k + 1))), and also beats two simple explanations already known to Stage 2 (being long in a
rising market, and following the last fifteen minutes' move), and the edge is worth at least $500 a year where the
value map prices it. Expected answer, stated in advance: the model will predict **how fast** a trade resolves (a
check that the machinery works) but probably **not which way**; a "no" is a valid close.

## 1. Hypothesis (research protocol step 1)

**The mechanism.** Intraday direction on an index future is close to unpredictable, but not exactly: short-horizon
momentum and the session's position relative to levels everyone watches (the prior day's range, the overnight range,
the opening range, VWAP, round numbers) move the order flow of discretionary and systematic traders, and volume
against its usual time-of-day level marks when informed flow is present. One model reading all of these together
might find a small, stable direction signal that no single rule shows. **Expected:** volatility and resolution speed
are predictable (volatility clusters; the handoff 3.3), direction hard (Stage 2's OHLC rules against their coin twins
found gains of schedule, not direction, D-558; a short-momentum follow effect that is real per trade but concentrated
in 2024-2026, D-580, D-588, D-592).

**What would make it worth something.** Not its accuracy: its lift in win probability over the coin at the same
entries, times how often it is used, times what a win is worth where it is used (Stage 2's value map,
`vendor/stage2/results/u_value_map.csv`; handoff 2.7: rank a signal by frequency x extra win probability x the value
of a win where it is used).

**Two targets** (the handoff 3.3's form): **resolution speed** (expected predictable) -- declared as the pipeline's
**positive control** and as a filter read beside the scorecard; it cannot pass, because a filter that ignores the
side has no lift over the coin by construction -- and **direction** (expected hard), the only target the pass line
reads.

## 2. Prior exposure (the audit's R-3; P-3, D-2)

What Stage 2 already read of this mechanism on these data (NQ 2020-01-02 to 2026-07-16):

| row | what was read | sign and span |
|---|---|---|
| Stage 2 D-555, D-557, D-558 (A4) | short-bar momentum rules against their coin-sided copies | a genuine but tiny per-trade direction effect; no campaign value beyond the schedule |
| Stage 2 D-578, D-580 (program S, S1) | 15 OHLC side rules on P-16's offers (momentum 1-120 min, session, prior day, range midpoints, latest breakouts) | 15-minute momentum and the latest 5-minute breakout, **followed**, survive the per-offer lift test; both fail the span guard -- below P-16 on 2020-2023, above on 2024-2026 |
| Stage 2 D-581, D-582 (S2) | P-16's coin gated by volatility and trend states | no state improves the offers enough |
| Stage 2 D-586, D-588, D-589 (S3) | new event kinds, followed | the 1-minute 4-bar breakout followed passes all guards, its gain concentrated in 2024-2026 |
| Stage 2 D-592 | S3's candidate at the 5-minute latency | fails; the follow effect is "broad and slow", recorded as **a lead for unread data**; re-testing it on this window "would reuse hypotheses already seen" |
| Stage 2 D-275, D-277, D-281 (ORB1-ORB6) | the 08:30 NQ opening-range breakout | closed for good; whether a later hypothesis is genuinely different is the operator's call (D-281 (3)) |
| Stage 2 program U (nine families), F-01 (E-003, withdrawn E-007) | contract levers; resting orders at levels | no direction read in U; F-01 read nothing |

**What follows for this family.** (a) The judged block is late development for direction, not out of sample (the
audit's P-3): its follow effect is known. So the pass line is joined by two conjunctive kill lines that a known
effect cannot clear (section 9, C1-d and C1-f): the drift-matched lift and the lift over Stage 2's own follow rule.
(b) The family is a new question rather than a re-run because no Stage 2 work fitted a model jointly on normalised
features, and because it must beat the recorded follow rule on the same offers to pass. (c) **The opening range.**
Two of the 47 features (`or_width`, `or_pos`) describe the 08:30-08:59 range. This draft keeps them: the family enters
at the market on a fixed schedule and no entry is triggered by the range, so it is not an opening-range breakout
specification. E-007 (b) put `or30` out of any **level** family until the operator rules; whether that reaches a
feature of a model is the lead's (and, under D-281 (3), the operator's) call -- **if ruled out, the two features are
removed before pinning** and the library's 45 others stand (open question 2).

## 3. Contract fit (step 2) -- the constraints the family lives inside (CHARTER section 4)

| constraint | how the family meets it |
|---|---|
| latency, at least 5 minutes, hand entry (Stage 2 D-266; E-008) | the side at alert t is computed from bars stamped <= t - 1 min only (`extended/features.py`); the order is a market order placed by hand at t + 5, filled at the open of the first bar opening at or after t + 5, one tick adverse (Stage 2's market entry, `extended/walker.py` `MARKET`); no automated or API entry |
| one position per firm, 5 minutes flat (D-429) | the pass line reads every offer independently (the coin twin's form); the scorecard's design routes by P-16's strict rule |
| resolution, at most 5 % to the flatten overall and in every year, no time stop (D-212, D-308; the audit's D-8) | kill line K2 (section 7) |
| realised risk matches intended (D-308) | K3 (reported: a market entry's stop exit slips adversely, so it cannot fail -- the audit's D-9) |
| stop band and cost floor (`vendor/stage2/results/stop_band.csv`) | stops of 25 and 37.5 points only, the registered coin rungs (P-15, P-16), both above the cost floor |
| news (D-525, D-533; E-007 (d)) | RTH alerts only, so every entry is after 08:35 CT, after 07:35:00 CT on a BLS release day; FOMC days excluded (Stage 2's FOMC day set) |
| conduct tier 1 (D-145) | no hedging (one position across the firm); no simulator-fill exploitation (25/37.5-point brackets held minutes to hours, no tight brackets); no maximum size into major news (FOMC days out, entries an hour after the 07:30 CT BLS releases); no copying across accounts (D-157); nothing concealed. The breakeven move of P-16's walk is allowed as made (E-013 (2)) |
| conduct tier 2 (D-289) | as P-16: off in the base case, on beside (R at or below 1 in the table's later leaves) |
| conduct tier 3 (E-013 (1)) | 0 % denial in the verdict; the 10/25/50 % ladder beside |
| firm rules | none loaded by the family: the scorecard runs Stage 2's engine on its verified ledger (`vendor/stage2/config/rules.yaml`) |
| hours | US regular hours (handoff 3.1, program U family 4) |

## 4. Data, blocks, the population and the confirmation

- **Data:** Stage 2's NQ 1-minute bars (Databento GLBX.MDP3 ohlcv-1m, licensed, vendored uncommitted, hashes in
  `vendor/DATA_MANIFEST_stage2.sha256`), development window **2020-01-02 to 2026-07-16** only, read through Stage 2's
  window guard (`propedge.data.bars.read_bars`). Stage 2's walks (`vendor/stage2/data/atlas`) are not read: every label
  comes from this repository's walker, whose identity to P-16's trades holds (E-011).
- **The choice block:** sessions **2020-01-02 to 2023-12-29** (fitting, the search, every choice). **The judged
  block:** sessions **2024-01-02 to 2026-07-16** (one read of the frozen pick). Sealed during choice and fitting (the
  audit's R-4): no stage before C reads a judged-block bar; enforced by the choice-stage invariance check (section 14,
  T-3).
- **The population of offers:** every (session, alert t) with t one of `extended.features.ALERT_MARKS` (08:30 to 15:00
  CT every five minutes) whose entry mark t + 5 is an **offered mark** of the stop's registered coin -- P-16's
  (`vendor/stage2/results/rc_width_screen.csv`, section `marks`, `stop_ticks` 150, `offered` true) for 37.5 points,
  P-15's (`resolved_coin.mark_resolution` at the 100-tick rung, as P-15's cell is built) for 25 points -- on a session
  of Stage 2's day kinds `n` or `b` (`atlas_local.close_day`: not FOMC, not an early close, not empty), after the
  store's first `extended.features.HISTORY_DAYS` (22) sessions (the features' warm-up). *Disclosed:* the offered marks
  were fixed by Stage 2 over the whole window from resolution columns only (no P&L, both sides pooled) -- a
  side-neutral choice that cannot favour a side; and Stage 2's FOMC set includes the unscheduled statements of March
  2020, excluded after the fact as P-16 excludes them (side-neutral; open question 8).
- **Confirmation, declared now:** NQ from **2026-07-17**, at least six months (Stage 2 D-604), never read until a
  carried candidate is registered; not owned -- **a purchase, the operator's** (`docs/OPERATOR_SETUP.md`). NQ's
  held-back window was spent by Stage 2's P-05, P-06 and P-10 (Stage 2 D-107: at most three a market), so the reserve
  would be NQ's fourth confirmation, **the operator's decision** (Stage 2 D-461); Stage 2's own P-16 draft targets the
  same window (the audit's D-6): if it is read first for P-16, a P-16-based design of this family cannot be confirmed
  on it cleanly, and the lead decides which goes first under a row before either is registered.

## 5. The offers, the brackets and the labels

- **Entry:** at the open of the first bar opening at or after t + 5, one tick adverse (Stage 2's; `extended.walker`
  `MARKET`). Both sides of every offer enter at the same price (a market order), so the resting order's fill-bar
  problem (the audit's D-1, D-13) does not arise: market fills are walked whole in every mode.
- **Brackets:** stop S in {25, 37.5} points (100, 150 ticks); targets at R in {1, 1.5, 3} (the table's three asks,
  handoff 2.5) -- **six brackets**.
- **The walk:** `extended.walker` preset `STAGE2` -- Stage 2's FV3 rung walk as P-16 walks it (stop on a touch, target
  on a trade through, stop first on a two-barrier bar, FV3's breakeven move, the flatten at 15:08-15:10 at the worst of
  those bars less two ticks), with Stage 2's costs (`atlas_a3.fee_by_stop`, `config/fills.yaml`); its identity to P-16's
  pinned trades holds (E-011). The breakeven move is allowed as made (E-013 (2)). Beside, deciding nothing: the same
  readings under Q-20's corrected move (its five-minute latency and stop-first tie, when merged) and with no move.
  *Note:* the two known defects of the move (E-012 (2)) favour whichever side is ahead at the next session open; under
  the null the model's side is ahead as often as the coin's, so they cannot create a lift, only enlarge a real one.
- **The pair at each offer** (for each bracket): the long's and the short's outcome -- kind, gross and net R -- and the
  pair value `d = (win_long - win_short) / 2` in win probability (`win` = a target exit), with the same in net R beside.
  A side rule with sides `s_i` in {+1, -1} has **lift over the coin twin** `mean(s_i d_i)`: the coin's expectation at
  the same entries without the coin's noise (F-01's estimand; the audit 1.3: unbiased here because both sides enter at
  the same price and walk under the same rules).
- **The direction target** (per stop, fitted at R = 1 only, where the two sides' barriers are symmetric): `y = 1` if
  the long's net R at R = 1 exceeds the short's, `y = 0` if below, the offer left out of the fit if equal (both
  stopped, e.g. on a two-barrier bar).
- **The resolution target** (per stop): `T` = minutes from the entry bar's open to the first bar touching entry +- S
  (the 1R band either way, side-free), the walk's end when none; `y_res = 1` if `T` is at most the training fold's
  median of `T`, else 0 (the median fitted in-fold).
- **Gates first:** the labels' kinds are read for K2 (resolution) before any direction outcome (section 7).

## 6. The features (Q-11's library) and their preparation

**The library:** `extended/features.py` (47 features, 13 of them one value a day), pinned at pinning by the sha256 of
the file at the pinning commit. Every feature at t reads only bars stamped <= t - 1 minute and bars of earlier
sessions; every normaliser is from the past only (ATR of the 14 prior sessions, roll-safe; time-of-day medians over the
20 prior sessions); cross-day features are NaN on a roll day; calendars only as known in advance. The proof is the
library's tests (`tests/test_features.py`, `tests/test_features_lookahead.py`: shift invariance at every alert of ten
synthetic sessions across a roll and a DST change, the whole future replaced, a one-minute leak and a full-sample
z-score caught). The registry, as `extended.features.describe()` prints it:

| feature | group | formula | window | normaliser | reads | from | cross-day | warm-up | per |
|---|---|---|---|---|---|---|---|---|---|
| `ret_5` | return | (c - close of the last bar stamped <= t-1-5min) / atr14 | 5 min | atr14 | the day's bars stamped <= t-1min; atr14's 14 prior days | 08:30 | no | 14 | alert |
| `ret_15` | return | (c - close of the last bar stamped <= t-1-15min) / atr14 | 15 min | atr14 | the day's bars stamped <= t-1min; atr14's 14 prior days | 08:30 | no | 14 | alert |
| `ret_30` | return | (c - close of the last bar stamped <= t-1-30min) / atr14 | 30 min | atr14 | the day's bars stamped <= t-1min; atr14's 14 prior days | 08:30 | no | 14 | alert |
| `ret_60` | return | (c - close of the last bar stamped <= t-1-60min) / atr14 | 60 min | atr14 | the day's bars stamped <= t-1min; atr14's 14 prior days | 08:30 | no | 14 | alert |
| `ret_120` | return | (c - close of the last bar stamped <= t-1-120min) / atr14 | 120 min | atr14 | the day's bars stamped <= t-1min; atr14's 14 prior days | 08:30 | no | 14 | alert |
| `ret_rth` | return | (c - open of the first bar stamped >= 08:30) / atr14 | 08:30 to t | atr14 | the day's bars stamped 08:30..t-1min | 08:35 | no | 14 | alert |
| `ret_day` | return | (c - open of the trading day's first bar) / atr14 | 17:00 to t | atr14 | the day's bars stamped <= t-1min | 08:30 | no | 14 | alert |
| `rng_15` | range | (max high - min low of the bars stamped t-15..t-1) / atr14 | 15 min | atr14 | the day's bars stamped t-15..t-1min | 08:30 | no | 14 | alert |
| `rng_60` | range | (max high - min low of the bars stamped t-60..t-1) / atr14 | 60 min | atr14 | the day's bars stamped t-60..t-1min | 08:30 | no | 14 | alert |
| `range_day` | range | (day high - day low so far) / atr14 | 17:00 to t | atr14 | the day's bars stamped <= t-1min | 08:30 | no | 14 | alert |
| `range_rth` | range | (regular-session high - low so far) / atr14 | 08:30 to t | atr14 | the day's bars stamped 08:30..t-1min | 08:35 | no | 14 | alert |
| `pos_day` | position | (c - day low) / (day high - day low), so far | 17:00 to t | the day's own range | the day's bars stamped <= t-1min | 08:30 | no | 0 | alert |
| `pos_rth` | position | (c - RTH low) / (RTH high - RTH low), so far | 08:30 to t | the session's own range | the day's bars stamped 08:30..t-1min | 08:35 | no | 0 | alert |
| `pos_prior` | position | (c - prior RTH low) / (prior RTH high - prior RTH low) | the prior regular session | the prior session's range | the prior day's bars stamped 08:30..14:59; c | 08:30 | yes | 1 | alert |
| `d_pdh` | level | (c - prior RTH high) / atr14 | the prior regular session | atr14 | the prior day's bars stamped 08:30..14:59; c | 08:30 | yes | 14 | alert |
| `d_pdl` | level | (c - prior RTH low) / atr14 | the prior regular session | atr14 | the prior day's bars stamped 08:30..14:59; c | 08:30 | yes | 14 | alert |
| `d_pdc` | level | (c - prior RTH close: the last close stamped <= 14:59) / atr14 | the prior regular session | atr14 | the prior day's bars stamped <= 14:59; c | 08:30 | yes | 14 | alert |
| `d_onh` | level | (c - overnight high) / atr14; overnight = bars stamped 17:00..08:29, frozen at 08:30 | 17:00 to 08:30 | atr14 | the day's bars stamped 17:00..08:29; c | 08:30 | no | 14 | alert |
| `d_onl` | level | (c - overnight low) / atr14 | 17:00 to 08:30 | atr14 | the day's bars stamped 17:00..08:29; c | 08:30 | no | 14 | alert |
| `range_on` | level | (overnight high - overnight low) / atr14 | 17:00 to 08:30 | atr14 | the day's bars stamped 17:00..08:29 | 08:30 | no | 14 | day |
| `gap` | level | (the last close stamped <= 08:29 - prior RTH close) / atr14 | prior 14:59 to 08:30 | atr14 | the prior day's bars stamped <= 14:59; the day's bars stamped <= 08:29 | 08:30 | yes | 14 | day |
| `d_vwap` | level | (c - RTH VWAP so far: sum((h+l+c)/3 x volume) / sum(volume)) / atr14 | 08:30 to t | atr14 | the day's bars stamped 08:30..t-1min | 08:35 | no | 14 | alert |
| `d_round` | level | (c - the nearest multiple of 100 index points) / atr14 | the last bar | atr14 | the last bar stamped <= t-1min | 08:30 | no | 14 | alert |
| `or_width` | opening range | (OR high - OR low) / atr14, OR = the bars stamped 08:30..08:59 | 08:30 to 09:00 | atr14 | the day's bars stamped 08:30..08:59 | 09:00 | no | 14 | day |
| `or_pos` | opening range | (c - OR low) / (OR high - OR low) | 08:30 to 09:00 | the OR's own range | the day's bars stamped 08:30..08:59; c | 09:00 | no | 0 | alert |
| `vol_5` | volume | log((V5 + 1) / (median V5 + 1)), V5 = volume of the bars stamped t-5..t-1 | 5 min | its median at the same CT slot over the 20 prior trading days | the day's bars stamped t-5..t-1min; the same slots of the 20 prior days | 08:30 | no | 10 | alert |
| `vol_30` | volume | log((V30 + 1) / (median V30 + 1)) | 30 min | its median at the same CT slot over the 20 prior trading days | the day's bars stamped t-30..t-1min; the same slots of the 20 prior days | 08:30 | no | 10 | alert |
| `vol_day` | volume | log((Vday + 1) / (median Vday + 1)), Vday = the day's volume stamped <= t-1 | 17:00 to t | its median at the same CT slot over the 20 prior trading days | the day's bars stamped <= t-1min; the same slots of the 20 prior days | 08:30 | no | 10 | alert |
| `vol_accel` | volume | log((V5 / 5 + 1) / (V60 / 60 + 1)) | 5 vs 60 min | the trailing hour's own rate | the day's bars stamped t-60..t-1min | 08:30 | no | 0 | alert |
| `rv_ratio` | volatility | rv_15 / rv_60 | 15 vs 60 min | the trailing hour's own rv | the day's bars stamped t-61..t-1min | 08:30 | no | 0 | alert |
| `rv_tod` | volatility | log(rv_60 / median rv_60) | 60 min | its median at the same CT slot over the 20 prior trading days | the day's bars stamped t-61..t-1min; the same slots of the 20 prior days | 08:30 | no | 10 | alert |
| `rv_atr` | volatility | rv_60 / atr14 | 60 min | atr14 | the day's bars stamped t-61..t-1min | 08:30 | no | 14 | alert |
| `atr_ratio` | volatility | atr5 / atr14 | 5 vs 14 days | atr14 | the 14 prior trading days | 08:30 | no | 14 | day |
| `range_prior` | volatility | (prior RTH high - prior RTH low) / atr14 | the prior regular session | atr14 | the prior day's bars stamped 08:30..14:59 | 08:30 | no | 14 | day |
| `atr_rel` | volatility | atr14 / c x 10,000 (basis points of the price) | 14 days | the price level | the 14 prior trading days; c | 08:30 | no | 14 | alert |
| `ret_prior` | trend | (prior RTH close - prior RTH open) / atr14 | the prior regular session | atr14 | the prior day's bars stamped 08:30..14:59 | 08:30 | no | 14 | day |
| `ret_5d` | trend | sum of the 5 prior days' changes (C_d - C_{d-1}; C_d - O_d on a roll day) / atr14 | 5 days | atr14 | the 6 prior trading days' first and last bars | 08:30 | no | 14 | day |
| `ret_20d` | trend | sum of the 20 prior days' changes, chained within the contract / atr14 | 20 days | atr14 | the 21 prior trading days' first and last bars | 08:30 | no | 20 | day |
| `ext_ma60` | trend | (c - mean close of the bars stamped t-60..t-1) / atr14 | 60 min | atr14 | the day's bars stamped t-60..t-1min | 08:30 | no | 14 | alert |
| `up_share_30` | trend | share of rising 1-minute close changes among those of the bars stamped t-30..t-1 | 30 min | a share | the day's bars stamped t-31..t-1min | 08:30 | no | 0 | alert |
| `eff_30` | trend | \|c - close as of t-31\| / sum \|1-minute close changes\| over t-30..t-1 | 30 min | the path's own length | the day's bars stamped t-31..t-1min | 08:30 | no | 0 | alert |
| `tod` | calendar | (t - 08:30 CT) in hours | -- | -- | none (the alert's CT time) | 08:30 | no | 0 | alert |
| `dow` | calendar | the trading day's weekday, 0 Monday .. 4 Friday | -- | -- | none (the date) | 08:30 | no | 0 | day |
| `bls_day` | calendar | 1 if the trading day has a BLS 08:30 ET release, else 0 | -- | -- | the BLS schedule (published the year before) | 08:30 | no | 0 | day |
| `bls_major` | calendar | 1 if it releases the Employment Situation or the CPI, else 0 | -- | -- | the BLS schedule | 08:30 | no | 0 | day |
| `days_to_fomc` | calendar | calendar days to the next scheduled FOMC statement day (0 on one), capped 30 | -- | -- | the FOMC schedule as known on the day | 08:30 | no | 0 | day |
| `days_since_fomc` | calendar | calendar days since the last FOMC statement before the day, capped 30 | -- | -- | the FOMC statements already made | 08:30 | no | 0 | day |

(`c` = the close of the last bar stamped <= t - 1 min; `atr14` = the mean daily true range of the 14 prior sessions,
the prior close used only within one contract. Two are level-dependent by design: `d_round`, `atr_rel`.)

**Preparation, every statistic fitted inside the training fold only and applied out of fold** (feature-rules
section 4): (1) each real feature winsorised at the training fold's 0.5 % and 99.5 % quantiles; (2) standardised by the
training fold's mean and standard deviation; (3) `dow` as four indicators (Tuesday-Friday; Monday the reference); the
binary flags as they are; (4) three missing indicators -- `m_rth` (the 08:30 alert, before any regular-session bar has
closed), `m_or` (before 09:00), `m_cross` (a roll day) -- and every remaining missing value set to 0 after
standardisation (the training mean). The design matrix: 53 columns and an unpenalised intercept. No feature is
selected, transformed or dropped by data.

## 7. Gates before any outcome (stage A, on the choice block; counts and side-free columns only)

- **K1 supply:** offers per session and per year of each cell (a `filter` cell's counted after its out-of-fold filter,
  which reads no outcome); at least 12 a year (the value map's smallest use count) in every choice year, else the cell
  is killed.
- **K2 resolution:** the share of offers flattened unresolved, both sides pooled, at every R in {1, 1.5, 3}, at most
  5 % over the choice block **and in every year of it** (Stage 2 D-212 per year; the audit's D-8); else the cell is
  killed (no cutoff is re-tuned).
- **K3 realised risk** (D-308): reported.
- **The identities** (section 14) hold, refusing.
- **The positive control:** the resolution model's out-of-fold AUC on the choice block's inner test years (2021-2023)
  at each stop, its 95 % lower bound by the same session-block bootstrap as stage B (seed `<to be fixed at pinning>`)
  above 0.5. **If not, the pipeline is suspected and the failure protocol runs before stage B** (terminal states, stage
  decomposition, the component in isolation, replication); the family does not proceed until the lead rules under a row.
- **The null canary:** the whole direction pipeline (folds, search, fit, out-of-fold sides, stage B's statistic) run
  once on the choice block with the long's and the short's outcomes swapped in every 21-session block a seeded coin
  picks (seed `<to be fixed at pinning>`) -- so the label and `d` both flip there and the features keep no relation to
  the side, the dependence kept: its maximum studentised lift is reported; above the one-sided 0.001 critical value it
  is a defect signal and the failure protocol runs.
- **Power on record (R-16), before stage B, from counts only:** each cell's minimum detectable lift (MDL) at the
  family's level on the judged block from its offer count and Q-16's power curve, set against the value map's bar
  (`u_value_map.csv`, section `bar`: the extra win probability for $500 a year at the cell's uses). If the MDL exceeds
  the bar by more than a factor of 3 at every surviving cell, the family is **declared a screen**: it still runs to the
  end, but a CLOSED reads "no lift above the MDL", and a pass is a lead for confirmation only.

## 8. The model, its search and the walk-forward (R-7)

- **The model:** an **L2-regularised logistic regression**, one per stop and target (four models): minimise the
  session-weighted mean log loss `(1/D) sum_d (1/m_d) sum_{i in d} logloss_i + (lambda/2) ||beta||^2` (D sessions in the
  training set, m_d labelled offers in session d, so every session weighs the same however many marks it offers; the
  intercept not penalised), by `scipy.optimize.minimize(method="L-BFGS-B")` with the analytic gradient, from zero,
  `gtol` 1e-10, at most 2,000 iterations, refusing a fit that does not converge. Deterministic: no seed. Implemented in
  this repository's package (neither scikit-learn nor LightGBM is installed on the machine, Q-11; the logistic needs
  neither), held by its own tests before any fit (section 14).
- **Searched, one hyperparameter: lambda**, over **five values `0.25 x 10^(j/2)`, j = -2..2** (from little shrinkage to
  heavy: with standardised features near p = 0.5 the coefficients shrink by about `0.25 / (0.25 + lambda)`), per stop
  and target, **inside the choice block only**:
  - **inner walk-forward:** test years 2021, 2022, 2023; each trained on the choice block's population sessions before
    the test year **less an embargo of the last 22 sessions before it** -- longer than the longest trade (a label
    resolves by 15:10 the same session) and equal to the features' longest history (`HISTORY_DAYS`), so no training
    label or feature window touches a test session;
  - **criterion:** the session-weighted out-of-fold log loss summed over the three test years; the smallest wins, a tie
    (within 1e-9) to the larger lambda;
  - every configuration evaluated (lambda x stop x target, its folds and its criterion) written to the family's result
    file and **counted** (section 11).
- **The out-of-fold predictions for stage B:** at each stop's chosen lambda, the three inner folds' predictions on
  2021-2023 (2020 is training only).
- **The final model:** refitted at the chosen lambda on all the choice block's population sessions; its coefficients,
  the in-fold winsorising, standardising and imputing constants, the filter threshold (below) and the training medians
  serialised to canonical JSON and **hashed; the hash pinned in a decision row before the judged read** (R-7, T-7: the
  judge's manifest names it and the judge entry point refuses to fit). No early stopping, no refits with other seeds,
  no feature subset, no class weights.
- **The resolution model** (the positive control): the same pipeline on `y_res`, its own lambda by the same search.

## 9. How a prediction becomes a trade, the cells, and the judgement

**A prediction becomes a side** (handoff 3.4: supply comes from the schedule; an edge is a side or a filter on its
offers): `p` is the direction model's probability that the long beats the short; the side is **long if p > 0.5, short
if p < 0.5**, a seeded coin if exactly 0.5 (seed `<to be fixed at pinning>`). Two uses:

- `side` -- every offer of the population takes the model's side (the coin replaced);
- `filter` -- only offers with `|p - 0.5|` at or above the **80th percentile of `|p - 0.5|` over the training fold's own
  fitted predictions** are offered (about the most confident fifth; the threshold fitted in-fold and pinned with the
  model), at the model's side; the rest are not offered.

**The cells (k_cells = 2 stops x 3 R x 2 uses = 12).** Within a stop and a use the trades and sides are the same at
every R; R decides the bracket the lift is read at and the place the value map prices it at.

**Stage B -- choose on the choice block (2021-2023, out of fold).** For every cell surviving stage A: the lift over the
coin twin `L_c = mean(s_i d_i)` over its offers; a session moving-block bootstrap (circular, 21-session blocks, 2,000
draws, seed `<to be fixed at pinning>`) of the session-weighted lift, centred at `L_c` and studentised by each cell's
bootstrap standard error `SE_c`; the family-wise critical value `q` = the 95th percentile over draws of
`max_c (L*_c - L_c) / SE_c` (one-sided 0.05). Benjamini-Hochberg at 10 % beside, never selecting.

- **Kill B:** no cell with `L_c / SE_c > q` -- the family closes; the judged block is not read.
- **The pick:** among those above it, the cell with the largest **valued lift** at its lower limit `L_c - q SE_c`.
  **The valued lift** (the value map's own first-order formula, `u_value_map.csv` definitions
  `extra_win_prob_points`, `mean_dv`): `$ a year = (lift in points) x uses x mean_dv / 100`, uses = the cell's offers a
  year on the choice block, capped by the place's `trades_per_year_forward`; the place by R -- R = 3: (c) the funded
  opening; R = 1.5: (b) the evaluation; R = 1: the larger of (d) later funded and (e) paid -- on base `p16` for 37.5
  points and `p14` for 25 points (section `place_values`; the value map holds no P-15 base -- the mismatch named, the
  audit's D-3, open question 12). First-order, the table held fixed; read as a ranking, not a forecast.

**Stage C -- judge the pick once, on the judged block (2024-01-02 to 2026-07-16), with the frozen pinned model.** Per
offer `i` of the pick's population, `d_i` at the pick's bracket, the model's side `s_i`, and the **follow twin's** side
`f_i = sign(ret_15 at t)` (Stage 2's S1 survivor `mom15`, followed, at the 5-minute latency -- `config/search_program.yaml`
`mom15: c[t] - c[t-15]` read at t = mark - 5 as D-589 reads every rule; a zero is a tie, `f_i = 0`). **The design
passes only if every line holds:**

- **C1 -- the pass line (CHARTER section 3, E-008):** the lift over the coin twin `mean(s_i d_i)`, its one-sided lower
  bound at **0.05 / (k (k + 1))** by **Q-16's calibrated lift test** (TASK_QUEUE Q-16, the test that delivers its stated
  level under the trades' within-session clustering and across-session dependence; used as merged, unchanged; this
  file is not pinned until it is merged with its calibration holding at that level), above zero;
- **C1-d -- drift-matched:** the same test on `(s_i - s_bar) d_i` (`s_bar` the pick's mean side on the judged block):
  above zero at the same level -- a model that is mostly long in a rising market earns nothing here (the audit's D-12);
- **C1-f -- beyond the known follow effect:** the same test on `(s_i - f_i) d_i` (the lift over the follow twin):
  above zero at the same level -- the model must add direction beyond the effect Stage 2 recorded as a lead for unread
  data (D-592; the audit's 1.2 (4));
- **C2 -- worth something:** the valued lift at C1's one-sided 95 % lower bound at least **$500 a year** (the value
  map's `bar` target);
- **the floors** (CHARTER section 3): every offered R resolving on the judged block (K2's lines, per year); the
  long-run gate -- growth on the required bankroll at the bound above zero (Stage 2 D-145) for the pick's scorecard
  design (section 10) through `gate.run_gate` at a campaign seed never used before (`<to be fixed at pinning>`), 500
  paths; every firm rule verified (Stage 2's ledger); conduct tier 1.

The three statistics are read at the same level in conjunction (a conjunction of tests each at the level holds the
level), never as alternatives. **A fail of any line closes the family**, its reason in a decision row.

**Beside, deciding nothing:** the lift and C1-d, C1-f in net R; the lift by year (P-3 (5)); the reverse walk-forward
(the same pipeline and lambda fitted on the judged block, read on 2021-2023); the seeded coin twin (one coin side per
offer, seed `<to be fixed at pinning>`); the follow twins of S1's `lbrk5` and S3's `lnbar1x4` (Stage 2's event code,
imported); a momentum-only model (the same pipeline on the `return` and `trend` features); the lifts under Q-20's
corrected walk and with no breakeven move; the resolution model's judged AUC; the 10/25/50 % denial ladder and the
placement on in the scorecard.

## 10. The journey scorecard -- beside every judgement, never the pass line (CHARTER section 2; E-008, E-014, E-015)

**The scorecard design** (the pick's only; a family closed at Kill B runs none): Stage 2's engine call for the stop's
registered coin -- P-16's for 37.5 points, P-15's for 25 points (the table, the strict router, five seats, the
no-closure state table, the purchase budget, the fees) -- on **the family's offers only**, with **(i) the model's
sides** (a `filter` pick: only the filtered offers) and **(ii) the same offers with the registered coin's sides**
(P-15's and P-16's coin, seed 20261102, Stage 2 D-521), the R of every trade set by the table as the coin's is (the
side does not depend on R). Its journey replayed by the vendored U1 replay (`user_journey`) and Q-17's adapter (wt-user) on the
`verdict` arm (every R's outcome at the one-sided 95 % bound of its edge), payout denial 0 % and the placement off in
the verdict. **Identity first, refusing:** design (ii) on the registered coin's full offer set reproduces P-16's U1
start rows (E-010) and P-15's (to be established: open question 11).

**Read against R\* = P-14** and against design (ii) -- the comparison within one trade stream that isolates the side:

- **P** and the guarded measures S1, S3a, S3b, S3c (with its components: a won funded opening, the five winning days
  after it), S4a, S4b, S5a, S5b, S5c; the reported-only S2, S3d, S6, Q (`vendor/stage2/docs/USER_MILESTONES.md`);
- **the journey variables (E-014):** sessions and cash to the first pass; sessions and cash to the first payout;
  **sessions to break-even** (the first session whose cumulative net cash is at or above zero, daily), the share of
  starts reaching it by months 1, 2, 3, 6 and 12, and the share that later fall back below zero; **the path's
  evenness** -- the share of months with a positive net change, the longest run of months without a payout, the spread
  of monthly net, the deepest fall of cumulative net from its running high after break-even, payouts per month, and
  the largest single month's share of the year's payouts (the lump-sum detector);
- **every measure as a distribution over start days** (median, p10, p90), on all starts and on the judged block's
  starts, **with its uncertainty from the effective number of independent starts**, and the start day's share of the
  variance (Stage 2's design-against-luck reading, `user_drivers.csv` section `design_vs_luck`);
- **the frontier** of designs not beaten at once on P, S1, S3a and S5a (`user_drivers.csv` section `frontier`'s form);
- **the menu under limits:** **E-015's limits, once approved by the operator**, applied as **menu flags only** -- a
  design crossing one is shown with which limit and by how much, and **a limit never fails a design** (E-015 (3));
- **the evenness trade-off curve** beside: how much of the share ahead each step of evenness costs (E-015 (4); Stage 2's
  families 7 and 8 found flatter funded plans paid sooner but less than their fees);
- **E-007 (e)'s readings:** the denial ladder (10/25/50 %; E-013 (1) prices Terms of Use s.8 here), the placement on,
  the binding Focused Trader models, P by month, mean net, CVaR10, P under a bankroll limit, the effective sample size
  and the minimum detectable difference before the read;
- Stage 2 D-621 (3)'s rule against P-14, recorded beside as E-008 keeps it, deciding nothing;
- **not modelled, and said so wherever the scorecard appears:** a user who stops when their own money runs out, the
  user's time, taxes.

The resolution model as a filter (offers predicted fast only, at the coin's side) is a second scorecard design read
beside -- a supply and speed reading for the journey, never a pass.

## 11. The count, the family number and the level (R-17's words)

- **Cells (the trials the pick is chosen among):** k_cells = 2 x 3 x 2 = **12**, each counted whether killed or read.
- **Searched configurations:** lambda's 5 values x 2 stops x 2 targets = **20** model configurations, each evaluated on
  the inner folds and counted.
- **Recorded in the family's result file and the trial count:** 12 + 20 = **32**. Readings beside (section 9's list,
  the scorecard) are not trials: nothing is chosen from them.
- **The family number:** k = the next free in the program (**11 if pinned next**; F-01 spent k = 10, E-007 (a)), the
  level **0.05 / (k (k + 1))**. One cell reaches judgement; the family-wise test of stage B spends nothing of the
  program's budget (the judged block decides).
- *Reading of the brief's "every searched value counted in k":* counted in the family's **trial count**, not as extra
  family numbers (the audit's R-17); open question 3.

## 12. Parameters: fixed / searched / dropped

| parameter | what it is, in a phrase | class | value | source |
|---|---|---|---|---|
| market | what is traded | fixed | NQ (MNQ micros sized by the table) | CHARTER 1; handoff 2.2 |
| development window | the only data read | fixed | 2020-01-02 .. 2026-07-16 | CLAUDE.md; `config/windows.yaml` |
| choice / judged blocks | where choices are made / the one judgement | fixed | 2020-01-02 .. 2023-12-29 / 2024-01-02 .. 2026-07-16 | feature-rules 4; CHARTER 3 |
| alert marks | when a side is computed | fixed | 08:30 .. 15:00 CT every 5 min (`ALERT_MARKS`) | the brief; US hours (handoff 3.1) |
| offers | which marks can trade | fixed | entry mark t + 5 an offered mark of P-16 (37.5) / P-15 (25) | handoff 3.4; P-15, P-16 |
| excluded days | not traded | fixed | FOMC, early closes, empty days (Stage 2's day kinds); the first 22 sessions | D-525, D-533; the library's warm-up |
| entry | how a trade starts | fixed | market at the open of the first bar at or after t + 5, one tick adverse, by hand | D-266; P-16; E-008 |
| stop | the loss distance | fixed | 25 and 37.5 points | the stop band; P-15, P-16's rungs |
| R | target over stop, where read | fixed | 1, 1.5, 3 | handoff 2.5 (the table's asks) |
| training R | the label's bracket | fixed | 1 (the symmetric bracket) | this file |
| the walk | how a trade ends | fixed | `extended.walker` `STAGE2` (P-16's) | E-011; E-013 (2) |
| costs | fees and slippage | fixed | Stage 2's (`fee_by_stop`, `fills.yaml`) | E-010 |
| features | what the model sees | fixed | the 47 of `extended/features.py` (sha256 at pinning) | Q-11 |
| preprocessing | scaling inside the fold | fixed | winsorise 0.5/99.5 %, standardise, `dow` indicators, 3 missing indicators, impute 0 | feature-rules 4 |
| model | the classifier | fixed | L2 logistic, session-weighted, L-BFGS-B, gtol 1e-10, 2,000 iterations | the brief (one of its two) |
| **lambda** | how hard the coefficients are shrunk | **searched** | 0.25 x 10^(j/2), j = -2..2; inner walk-forward on 2021-2023, embargo 22 sessions, out-of-fold log loss | R-7; this file |
| side rule | prediction to side | fixed | long if p > 0.5, short if p < 0.5 | this file |
| filter fraction | how confident to trade | fixed | the top fifth (80th percentile of the training fold's \|p - 0.5\|) | this file (not searched) |
| resolution target | speed of resolution | fixed | first touch of entry +- S within the training median | handoff 3.3 |
| stage B bootstrap | the family-wise test on the choice block | fixed | circular session blocks of 21, 2,000 draws, studentised, one-sided 0.05 | handoff 4.3 |
| C1 statistic | the pass line's test | fixed | Q-16's calibrated lift test at 0.05 / (k (k + 1)) | E-008; Q-16 |
| C1-d, C1-f | kill lines against drift and the known follow effect | fixed | the same test on `(s - s_bar) d` and `(s - f) d` | the audit D-12, 1.2 (4); D-592 |
| value bar | the least worth | fixed | $500 a year at C1's 95 % bound | `u_value_map.csv` `bar` |
| MDL factor | when the family is only a screen | fixed | 3 | R-16; this file |
| gradient-boosted tree | the brief's other model | **dropped** | -- | not installed; more hyperparameters to fix or search; a tree is another family |
| 12.5 / 50-point stops | other stops | **dropped** | -- | not registered coin rungs (12.5: P-14's breakout, not a coin schedule); 40-50 worse or unresolved (handoff 2.2) |
| R 0.25, 2, 2.5 | the table's other offers | **dropped** | -- | the value map prices the three asks; fewer cells |
| resting entries | stop or limit orders | **dropped** | -- | family A's mechanism; market entries avoid the fill-bar problem (D-1) |
| non-RTH alerts | overnight sides | **dropped** | -- | US hours (handoff 3.1, U family 4) |
| interactions, feature selection, class weights, early stopping, seed refits | other model freedoms | **dropped** | -- | each a hidden search (the audit's P-5 (a)) |
| a filter fraction search | other confidence cuts | **dropped** | -- | a hidden search |
| rules read off the model (SHAP and the like) | explanations | **dropped** | -- | exploratory, their own family (bootstrap 6.3 B) |

## 13. Seeds -- every one `<to be fixed at pinning>`, each used nowhere else (T-12)

| purpose | seed |
|---|---|
| stage A's positive-control bootstrap | `<to be fixed at pinning>` |
| stage A's null canary (block sign flips) | `<to be fixed at pinning>` |
| stage B's session-block bootstrap | `<to be fixed at pinning>` |
| a tie at p = 0.5 (the coin) | `<to be fixed at pinning>` |
| the seeded coin twin beside | `<to be fixed at pinning>` |
| the long-run gate's campaign (a seed never used before) | `<to be fixed at pinning>` |
| T-3's synthetic replacement of the judged block | `<to be fixed at pinning>` |
| Q-16's test, if it draws | as Q-16 ships it |
| inherited, unchanged | 20261102 (P-16's coin, design (ii)); 20261700 and 20261600 + i (D-621 (3), beside) |

## 14. The build's identities and tests (Q-14, before any reading)

1. **The walker:** E-011's identity (P-16's cell rebuilt with `extended.walker`, `TRADES_SHA256`) holds at the build's
   commit.
2. **The features:** Q-11's tests pass at the pinned `extended/features.py`, including the slow tier's 790-cut shift
   test.
3. **The labels:** the family's pair outcomes at P-16's offers equal P-16's trades (side for side where the coin chose
   it) for the 37.5-point stop; P-15's for 25 points.
4. **The logistic:** agrees with a Newton solve of the same objective on synthetic data to 1e-8; recovers a planted
   coefficient; a planted look-ahead feature (L3's form) fails the shift test.
5. **A planted effect (T-14's form):** on synthetic bars with a direction effect of known size tied to a feature, the
   whole pipeline recovers it with the right sign, and C1's bound covers it at its level; on a driftless walk the lift
   is zero within its interval.
6. **Choice-stage invariance (T-3, heavy, under the run lock):** stages A and B and the final model are byte-identical
   when every judged-block bar is replaced by a seeded synthetic walk.
7. **The judge cannot fit (T-7):** the judge entry point refuses to fit and its manifest names the pinned model hash.
8. **The scorecard's identity:** design (ii) reproduces the registered coin's U1 start rows.

## 15. Outputs and what a result leads to

- `results/fb_model.csv` (sections `supply`, `resolution`, `controls`, `power`, `search`, `choice`, `judged`,
  `beside`) and `results/fb_scorecard.csv`, each with its sidecar manifest (`extended.results.write_result`), the pinned
  model's hash in the judged manifest; run once from a clean checkout of a named commit (`scripts/run_clean.py`), the
  heavy steps under the run lock.
- **CARRIED** (every line of stage C): a model card (`vendor/stage2/prereg/MODEL_CARD_TEMPLATE.md`), its registered
  development test through the gatekeeper, the auditor, one confirmation on NQ from 2026-07-17 (a purchase, the
  operator's).
- **CLOSED** at any kill line: the reason in a decision row; where a check (not a kill line) failed, the failure
  protocol. The next family is declared on its own.

## 16. Open questions for the red team and the lead (the draft's safe defaults, each overrulable before pinning)

1. **C1-d and C1-f** make the family stricter than CHARTER section 3's pass line (C1 and C2). Kept because a pass on
   drift or on the recorded follow effect would say nothing new (P-3, D-12, D-592); the cost is power.
2. **The opening-range features** (`or_width`, `or_pos`) under E-007 (b) and D-281 (3): kept; removed before pinning if
   ruled out.
3. **"Every searched value counted in k"** read as the trial count (R-17), not extra family numbers.
4. **The gatekeeper's text on master** (`.claude/agents/prereg-gatekeeper.md`) still makes Stage 2 D-621 (3) the
   mandatory judgement (its item 6), which E-008 replaced with the trades-first pass line, and asks for integer seeds
   and an `F-XX_` file name; this draft follows E-008 and the brief (`<to be fixed at pinning>`, `DRAFT_F-B_`). The
   lead amends one or the other before the gatekeeper reads it.
5. **The model:** the L2 logistic (deterministic, auditable, needs no package); a gradient-boosted tree would be a new
   family, and LightGBM and scikit-learn are not installed.
6. **The walk:** `STAGE2` with the breakeven move (E-013 (2)); Q-20's corrected move beside. If the lead prefers the
   corrected walk as primary, it must be merged with its own identity first.
7. **The offered marks** were fixed by Stage 2 over 2020-2026 from resolution only (side-neutral); a choice-block-only
   cutoff would be cleaner but would leave P-16's design.
8. **FOMC days:** the population excludes Stage 2's FOMC set, which includes the unscheduled statements of March 2020
   (excluded after the fact, as P-16 does; side-neutral); the calendar features use the scheduled meetings only, the
   cancelled 2020-03-18 meeting counted until 2020-03-13.
9. **BLS 2025:** Stage 2's archived 2025 schedule shows the post-shutdown dates of October-November 2025; each was
   announced before its day, so `bls_day` uses it as known on the day.
10. **Q-16:** not yet merged; this file is not pinned until it is, with its calibration at 0.05/(k(k+1)) holding.
11. **P-15's U1 identity** (for the 25-point scorecard) is not yet run (E-010 established P-14's and P-16's).
12. **The value map** has no P-15 base: 25-point cells valued on P-14's table (as F-01 did; the audit's D-3).
13. **Power:** likely low for direction (Stage 2's effects are "genuine but tiny"); section 7's R-16 line says what a
    "no" then means.

## 17. Anything chosen after seeing results

*(Empty. Anything added after a reading is exploratory, reported apart, `exploratory=True` in its manifest, and
recorded in its own decision row -- never added to this file once pinned.)*
