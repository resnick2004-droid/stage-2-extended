# DRAFT — FV3-C's paper shadow period (not registered)

> **Status: DRAFT, not registered** (D-398). Written 2026-10-19 so the shadow period can be registered the day its
> start is known; kept current under R8 (`docs/HANDOFF_RESET_2026-10-29.md`). It is handed to the
> **prereg-gatekeeper** only when every item of §8a is closed, the firm's rules have been re-verified within seven days
> of the start, and the file is committed and hashed. Until then nothing here runs and no session counts.
>
> **Brought current 2026-10-29 (R8).** R1-R4's levels are sourced (§6a): the ones data can give from the operator's
> Databento NQ minute bars (`results/shadow_system_levels.csv`, exploratory, written by
> `scripts/shadow_system_levels.py`), the ones no record can give by a burn-in whose rule is fixed here. The criteria
> are read from their single source, `docs/SUCCESS_CRITERIA.md` (D-457): C3 beside the verdict, the gate's metric
> growth on the required bankroll, the required-bankroll p95 path computed by `propedge.campaign.criteria.p95_path`.
> §8's items 6 and 7 are recorded as built. What is still open is listed with who closes it (§8a).

| field | value |
|---|---|
| **id** | P-XX *(assigned by the gatekeeper at registration)* |
| **date** | 2026-10-19 (draft); brought current 2026-10-29 |
| **author** | Stage 2, for the operator (Ryan Resnick) |
| **task** | T19 item 5 (`NEXT_STEPS.md`), carried as R8; the deployment protocol's sections 2–5 (`docs/DEPLOYMENT_PROTOCOL.md`, D-337) |
| **kind** | an execution test of a frozen, confirmed campaign — not a model test; no selection, one configuration |
| **status** | draft |

## 1. Question

Does live execution by hand reproduce the simulation of FV3-C? The engine's decisions, costs, latency and fills
recorded for every signal of a forward period, against the engine's own replay of the same days. "Yes" lets the
first Combine go live under section 6 of the protocol. "No" stops the deployment and sends the failure, kept on record,
back to the research.

## 2. The protocol, named exactly (protocol §2.4)

- **Candidate:** FV3-C, frozen at `c561ec9` (D-354), confirmed by P-06 (D-361, audited; PASS on C1–C4 as registered;
  contract shape, not edge). The verdict's metric is **growth on the required bankroll**: `pf_growth_on_base_p50`
  read on `pf_required_p90`, the gate row of `results/fv3_confirmation.csv` (D-312; `docs/SUCCESS_CRITERIA.md` §1).
  `median_log_growth` is the engine's notional column (D-451 F4) and is never read here. Under D-457, C3 (the
  break-even denial and the bound arm at 10 % denial) is no longer a confirmation line: P-06's denial readings are read
  beside its verdict with the rest of `docs/SUCCESS_CRITERIA.md` §4, and its PASS stands as registered.
- **Config:** `config/fv3_corrected_portfolio.yaml`, sha256 `a6dccfcc58ff519d0bd2db9ba8af5e7c62dd4bac2d3cf9a48b6c11236ea13c0c`.
- **State table (version 12):** `results/state_policy_v12.csv`, sha256
  `b134100a8c6d224c235d281f44d68d21e2b7bdf8f3c8d12a8810b29cb8684a10`; `results/state_policy_v12_policies.json`, sha256
  `c96930b051dc7ef3659d7013a7368741bd4b29870fe276bd9a5140c4180fc207`. Rung shares `results/fv3_rung_shares_2020.csv`,
  sha256 `1083b9da328e74562715f80703d2ad60f62550d96920a3b3171a426f8df4e840`.
- **Unchanged since the freeze:** `git diff c561ec9` on these four files is empty (checked 2026-10-19, and again
  2026-10-29). Each sha256 in this section is of the committed content (`git show <commit>:<path>`, line endings as
  committed). A checkout that converts line endings to CRLF hashes the config and the policies file differently while
  the diff stays empty (found 2026-10-29 in a worktree), so the registration's check reads the committed content.
- **Engine:** the Stage 2 commit at registration. It must reproduce `fv3_corrected_v1`, as the lever harness's identity
  check showed at `528b83f` (D-396). The commit is written here at registration.
- **The confirmation it is read against:** `results/fv3_confirmation.csv` (P-06), sha256
  `e9f146081d6373c0e730024b5d3c14db6d814a8dd214353d9140f1cfe62bb503`, and its per-path file
  `results/fv3_confirmation_paths.csv`, sha256 `0321e51448953844b5ee1c479d81ae4f3a7f67b7724eef2d65d9d7fdfc01824f`
  (both committed at `d189464`). The required bankroll (`pf_required_p90`) and the lower-bound mean are read from the
  first. The **required-bankroll p95 path** is read from the second by `propedge.campaign.criteria.p95_path` (D-457;
  `docs/SUCCESS_CRITERIA.md` §7): over the run "gate placement off" at 0 % denial, the 95th percentile of each path's
  `deepest_loss_from_start`. The lower-bound arm's value (`deepest_loss_p95_lower_bound`) is the line of §5.6, §6
  and P2's FAIL-MODEL; the point arm's (`deepest_loss_p95_point`) is P2's FLAG. `scripts/success_thresholds.py` writes
  both into `results/success_thresholds.csv` (section `p95_path`). **That file does not exist yet:** the script also
  reads P-06's per-path detail (`results/fv3c_confirmation_path_detail.csv`, from
  `scripts/fv3c_confirmation_path_detail.py`, not yet run), so the p95 path is pending (§8a). No figure is typed here.
- **The Studio's mirror:** the P-06 mirror the Studio reproduces path for path (SD-29).

## 3. The period

- **Start:** the first trading session after registration. Registration happens only after the live signal source is
  connected and the rules have been re-verified within seven days (protocol §2.5).
- **Length:** the greater of **60 trading sessions or 100 logged signals** (protocol §3). It is fixed and is not
  extended after a reading.
- **Mode:** paper — the execution terminal's simulation mode (Stage 3, its `TERMINAL_SPEC.md` §13 #7, approved SD-55),
  or the smallest size the firm allows. No real-money order.
- **Nothing in the protocol changes during the period.** A change ends it and starts a new one (protocol §3).

## 3a. Two tracks (D-399)

- **Track A — automated, the record.** The terminal's live FV3-C model on every session.
  - Every alert is taken automatically on the simulated accounts, at L = 2 minutes and the ASSUMED fill profile.
  - It carries criteria 5.4–5.8 and the kill rules that read the model.
  - Each night the engine replays the day from the same states and signals and must match it decision for decision.
  - A session without its record by the next session's open is flagged that day and never filled in from memory.
  - Each day's raw bars are kept as a data capture with its sha256.
- **Track B — manual, alongside.** The operator takes what they choose by hand from the same alerts.
  - Measured against track A: decision match, latency, slippage, coverage.
  - It carries criteria 5.1–5.3. These must hold over at least 100 signals executed by hand before any real capital
    is traded by hand, in this period or a following one registered the same way.
- **The data:** sessions from the registered start are this period's own (D-399). Trading days from 2026-07-17 to the
  day before the start stay reserved and unread.

## 4. What is logged and checked

- **Each morning:** the morning card, one line per account from the engine's table and queue (Stage 3, SD3-13).
- **Each signal:** one row in the Studio's execution log format (`docs/EXPORT_FORMAT.md` in the Studio, approved by the
  operator 2026-10-17, SD-55). It records the signal time, the account the queue assigned, taken or not, alert to
  order, intended and actual fill, fees, the outcome at the R traded, and the account's state as the policy read it.
- **Each night:** the day replayed through the engine from the recorded states and signals, and diffed against the
  log. Three numbers: the decision-match rate, the slippage distribution, the latency distribution (its tail).

## 5. Acceptance — all must hold (protocol §4, numbers fixed by D-398)

1. Decision match **≥ 95 %** over the period.
2. Realised cost per trade **≤ 1.5 ×** the modelled cost; fills within the kit's assumed slippage.
3. Latency p90 within **L = 2 minutes** (D-282, the card's `latency_minutes`); the missed-setup share within the
   stress-priced share.
4. Realised risk equals the intended (capped) risk on **≥ 90 %** of trades (P4's share).
5. **No unexplained trade.**
6. Drawdown inside the confirmation run's required-bankroll **p95 path**: the live drawdown from the start held inside
   `deepest_loss_p95_lower_bound` (§2).
7. **Edge:** the mean net R of taken trades not below the confirmation's lower-bound mean by more than **0.25 R**, on
   the day-block band (D-398: about two standard errors over 100 trades at FV3's per-trade spread, so normal noise does
   not trip it).
8. **Conduct:** no tier-1 rule touched; in particular no opposite positions held at the same time on any two accounts
   (D-336 (iv)). Tier-2 flags acknowledged in writing.

## 6. Kill rules during the period (protocol §5, numbers fixed by D-398)

- decision match below 90 % at any point;
- realised cost above 1.5 × the modelled for more than **5 sessions**;
- live drawdown beyond the required-bankroll p95 path (`deepest_loss_p95_lower_bound`, §2);
- any single unexplained trade;
- a firm rule change the ledger does not cover.

A failed criterion or a kill is a result. It goes on record and the failure protocol applies (`CLAUDE.md`).

## 6a. The automatic pilot's fail criteria (D-400)

There are three tiers:

- **FLAG:** logged and reported that night; the pilot continues.
- **FAIL-SYSTEM:** the pilot is not reflecting the market. It pauses, the fault is fixed, and a new registered
  period starts.
- **FAIL-MODEL:** the period ends FAILED.

Each level below names its source. R1-R4's levels that data can give are in `results/shadow_system_levels.csv`
(exploratory; `scripts/shadow_system_levels.py`, over the operator's Databento NQ minute bars for the development span
2020-01-01 to 2026-07-16, normal days only). They are named here by window, measure and stat and read from the file,
never typed. The levels no record can give are set by the burn-in below, by a rule fixed here. The rest (R5's band,
P1-P6) are computed into the registration's result file with a manifest at registration. Sessions count from the
pilot's day 0, with fresh accounts.

**The windows** (Chicago time; the file's `window` column):

- FV3-C's three signal windows (its card's Entry): `eve` 17:00-18:30 and `asia` 19:00-20:30 on the evening before,
  and `ny` 08:30-10:00.
- `rth`, 08:30-15:10: the window the terminal's R2 reads now.
- Reported only: the three signal windows together (`signal`) and the whole session to the flatten (`session`,
  17:00-15:10).

**System checks: is it reflecting the market live?**

| id | check | FLAG | FAIL-SYSTEM |
|---|---|---|---|
| R1 | the feed's heartbeat: **(a)** the age of the last heartbeat the server heard from the feed (the terminal's reading); **(b)** the market's silence, the longest run of minutes without a trade on the live-built bars, per window (`longest_run`) | (a) above the burn-in's largest age, anywhere in the session; (b) above the development's p99 day (`level` rows, measure `longest_run`, stat `flag_above`; windows `eve`, `asia`, `ny`, `rth`) | (a) silent through a whole alert window, L = 2 minutes (D-282), inside a signal window: an alert may have lapsed unseen, so the session is INCOMPLETE; (b) above the development's largest normal day (stat `fail_system_above`) |
| R2 | minute bars complete: the minutes without a bar, per window (`missing`; in `rth` the terminal's own interior count, `missing_interior`, which equals it on every development day) | above the development's p99 day (measure `missing`, stat `flag_above`) | above the development's largest normal day (stat `fail_system_above`); and, at the weekly re-pull (R7), any minute inside a signal window or `rth` that the vendor's file has and the live-built bars lack: the session INCOMPLETE |
| R3 | alert latency: the alert's emission less its signal bar's close (the terminal's reading) | above the burn-in's largest, for any alert | an alert emitted at or after its window's end, the signal bar's close plus L (D-282; the terminal's `alertclock.window_end`): track A cannot take it at the modelled latency |
| R4 | the clock: each bar on its exchange minute; the server against NTP | the NTP offset: an absolute offset above the burn-in's largest | any bar off its exchange minute (the development's bars: none, section `bars_off_minute`); an absolute NTP offset of at least L less R3's FLAG level, the smallest that can carry an alert R3 passes across its window's end (set with R3's at the burn-in's end) |
| R5 | the signal rate (`results/fv3_studio_corrected_v1_days.csv`) | a session with no signal; the rolling 10-session count outside the development's p01-p99 | two sessions in a row with no signal |
| R6 | the nightly replay against track A | -- | any difference |
| R7 | the vendor's historical bars, re-pulled weekly | a trade that differs | -- (a bar's absence is R2's) |
| R8 | the session's record by the next open | MISSING | three in the period |
| R9 | the calendar | a scheduled FOMC row unconfirmed after its meeting | -- |

The US daylight-saving changes inside the period (2026-11-01; 2027-03-14) are checked by hand on their first session.

**Why these levels (R1 (b), R2, R4's bars).**

- *FLAG at the p99 day, FAIL-SYSTEM above the largest normal day.* The p99 day is taken by nearest rank, an observed
  day, the terminal's own percentile rule. Beside it the file gives the share of development days above it and the
  chance of at least one FLAG in 60 development-like sessions (`flag_share_dev_days_above`,
  `flag_p_any_in_period`). The largest normal day is the most the market itself produced in the span. A new day passes
  it with probability at most 1/(n + 1), so a false FAIL-SYSTEM in a 60-session period has at most the chance in
  `fail_p_any_in_period_bound`. No lower FAIL-SYSTEM is supported without choosing, after seeing them, which days to
  set aside.
- *What set the tail* (the `tail` rows, by date). In `rth` and `ny`, every development day above the FLAG is one of
  March 2020's market-wide circuit-breaker halts (2020-03-09, -12, -16, -18; the last fell after 10:00, so it is not
  in `ny`). In `eve` and `asia` the largest days are March 2020's limit-down nights (trading days 2020-03-16 and
  2020-03-23). Outside March 2020, the days above the FLAG show a minute or two of quiet. So the FAIL-SYSTEM
  levels were set by exchange events: on the night they catch only a gross outage, and the exact test of a feed
  fault is R2's comparison with the vendor's file. Minutes inside a declared exchange halt are the market, never a
  fault.
- *R1 (b) in seconds.* A run of k minutes without a bar means the longest silence between two trades was at least k
  minutes and under k + 2. So a silence of k + 2 minutes, with k the p99 day's run, is certainly beyond the p99 day.
  The draft's earlier 60 s and 300 s cannot be read from minute bars; that would need the vendor's trades, another
  purchase. The levels stay in whole minutes on the live-built bars, where the reading and the level are made the
  same way.
- *Left out, and counted* (the `excluded` and `days` rows). Holidays and early closes (a last bar before 15:00 CT).
  One late open: trading day 2020-07-01's session starts at 19:00 CT in the file. That rule mirrors the early-close
  rule; it was added after reading the first run's tail, and it removes that day alone. And the gap between the two
  Databento files: trading day 2025-06-30, and 2025-07-01's evening.

**What the live feed changes (R1 (b), R2).** The file's levels are the market's own quiet in Databento's historical
file: a bar only for a minute with a trade in the charted outright (the previous day's volume leader, D-98; spreads
dropped), stamped by the exchange. The live feed is another product: trades and best bid/offer (the terminal's spec
§13 #8), from a vendor not yet chosen. The terminal builds its bars, and any of these can differ from the historical
file: the trade filter, the timestamp used (the exchange's or the receipt's), the contract on a roll day, whether an
empty minute gets a bar, and the feed's own drops. So:

1. A session beyond a level is first read against the vendor's historical bars for the same session (R7). Only a
   minute the vendor has and the live bars lack is a fault.
2. Over the burn-in, the live-built bars are compared minute for minute with the vendor's file. If the live bars
   carry minutes the file lacks (an empty minute filled in), R1 (b) and R2 cannot see a fault by counting, and they
   read only that comparison. This is said in the registration's file at the burn-in's end.
3. The levels are counts of the market's structure (NQ, 2020 to 2026), not of a vendor. A different vendor changes how
   they are read, not the levels.

**The burn-in (R1 (a), R3, R4's NTP offset).** No record exists of a live feed's heartbeat, alert latency or clock.
The terminal's figures come from replays:

- its outage drill of 2026-10-16 (Stage 3's `docs/RUNBOOK.md`) measured its own stale notice against its design
  cadence: an engine heartbeat every 5 s, stale after 15 s (`FEED_STALE_SECONDS`);
- its alert latency is read on a replay's clock;
- its NTP refresher (SD3-115, SD3-121) is off by default, with nothing recorded.

So these FLAG levels are not typed. The period's first 10 sessions are their burn-in:

- **Recorded:** every reading — the heartbeat's age at the terminal's cadence and each silent spell's length, each
  alert's latency, and the NTP offset every five minutes (the refresher on for the whole period).
- **Judged during the burn-in:** the FAIL-SYSTEM levels only. They come from the protocol's L, not from data, and apply
  from day 0. The FLAGs are not judged.
- **At the close of session 10:** each FLAG level is set to the burn-in's largest reading. It is computed into the
  registration's result file with a manifest before session 11. This is a rule fixed here, not a change of the
  protocol (§3).
- **Why inside the period:** trading days before the registered start are the reserve, unread (D-399 (5)), and the
  terminal's guard refuses them (its SD3-27, SD3-28).
- **Why 10 sessions:** it is the board's own span (R5's rolling count, D-400).
- **An option for R3:** if the terminal records how long each bar in the signal windows takes to evaluate (proposed to
  it, as its own row), R3's FLAG reads that sample's p99 instead. That sample does not wait on the signal rate.

**Model checks: is it performing as confirmed? (track A)**

Read from `results/fv3_confirmation_paths.csv`, run "gate placement off", 0 % denial, unless named otherwise: P1 and P3
by `propedge.campaign.criteria.paths_quantile`, P2 by `propedge.campaign.criteria.p95_path` (§2).

| id | check | FLAG | FAIL-MODEL |
|---|---|---|---|
| P1 | no payout yet (`days_to_first_payout`) | beyond the point arm's p95 | beyond the lower-bound arm's p99 |
| P2 | drawdown from the start before the first payout (`deepest_loss_from_start`) | beyond the point arm's p95 (`deepest_loss_p95_point`) | beyond the lower-bound arm's p95, the p95 path (`deepest_loss_p95_lower_bound`) |
| P3 | peak-to-trough drawdown after payouts (`max_drawdown`) | beyond the point arm's p95 | beyond the lower-bound arm's p95 |
| P4 | an XFA alive and unpaid since activation (`results/fv3c_xfa_time_budget.csv`, `xfa_timing`) | beyond the development's p90, for that account | -- |
| P5 | the edge over the last 100 trades | -- | below the confirmation's lower-bound mean less 0.25 R |
| P6 | a rule change the ledger does not cover; an unexplained trade | -- | either |

Reported beside, never criteria: the Combine pass share, the share of XFAs paid, the mean payout and the bracket's
shares, each against its development figure.

## 7. Beside the verdict, never part of it (D-398)

- **The 08:30 collect bracket, measured, not traded.** Every session the terminal records, from its live data, the
  collect brackets D-383 chose:
  - setup: 08:30 CT, 5 MNQ, a 20-point target ($200), the 1x and 2x stops, both sides, a 60-bar box from each entry;
  - entries: the opens of the first, second and third bars after the bar ending 08:30 CT (delays 0, 1 and 2), one
    tick adverse — R145's conventions exactly (D-399 (6)); 12 rows a session;
  - the record: target, stop or scratch, and the minutes to resolve;
  - exclusions: none on FOMC days, as R145.
- Reported: each bracket's target share with its Wilson interval, against R145's 2021–2025 share. This is unread
  evidence on the bracket's real hit rate, the quantity D-393 and D-396 turned on.
- No account takes it, and FV3-C is unchanged.
- **The live kill rule's window** for later real capital (protocol §7.1) is **the last 100 trades** (D-398).

## 8. Open before registration

1. **The live signal source.** Stage 3's terminal on a licensed live NQ feed, or a QuantConnect live algorithm
   emitting alerts. This waits on the operator's data and account purchase (Stage 3 `NEXT_STEPS.md` step 5).
2. **The start date,** and the firm's rules re-verified within seven days before it (rules-verifier, each rule with its
   article id and date).
3. **The bankroll for the paper period:** the confirmation run's required p90 plus one subscription is written down
   (protocol §2.6). It is paper, so no money moves; the figure is the one real capital must meet later.
   `pf_required_p90` already holds one subscription: each path's deepest loss from the start plus
   `portfolio.DEFAULT_MARGIN` (`portfolio.required_bankroll`). The decision row says whether the protocol's "plus one
   subscription" is that one or a second (§8a).
4. **The execution assumptions re-read with the operator:** L = 2 minutes, the hours traded, the expected missed share
   (protocol §2.7).
5. **R1-R4's levels sourced** (raised by the terminal session, 2026-10-26). §6a's levels for the feed's heartbeat,
   missing minute bars, alert latency and the clock named no source, R3 had no FAIL-SYSTEM level and R4 no FLAG, and
   the terminal measures alert latency as emitted minus signal. **Sourced 2026-10-29 (R8), §6a:**
   - R1 (b), R2 and R4's bars from `results/shadow_system_levels.csv`;
   - R1 (a), R3 and R4's NTP offset: their FAIL-SYSTEM levels from the protocol's L, their FLAGs by the burn-in.

   Until the registration's file carries them, the terminal's board shows R1-R4 as "not judged" (its SD3-115). What
   remains is in §8a.
6. **Need exits in the mechanics check** (the terminal's SD3-103, 2026-10-26). The terminal's executed brackets took
   profit at the state's R target, never at D-306's pass exit or D-313's consistency exit. The nightly replay (§4,
   R6) diffs each trade's take-profit against the engine's, at the need wherever one binds (the export's `exit_need`
   and `exit_need_kind`), and only a terminal build carrying SD3-103 can be the period's record. **Built** in the
   terminal (SD3-103, 2026-10-27): the take-profit at the engine's need, read by the engine's own `need_to_pass` and
   `day_allowance`, with the guidance's `exit_need` and its kind kept as the engine's. The registration names the
   build.
7. **The edge checks with need-capped trades** (§5.7 and the live window, protocol §4.7 and §7.1; agreed with the
   Studio session 2026-10-26, built there as SD-86). A trade whose take-profit was a need stays in, read against the
   model's lower-bound expectation for the trade as the draw books it, fixed at the entry: the engine's walk
   (`sizing._need_exit`) over the development log at the trade's need/risk and the state's R, each R's column at its
   own lower bound, a trade the walk reaches booked at exactly the need (the draw settles the need, `sizing.py`'s
   fixed-risk and tier-sized branches), the rest at the state's own outcome, a blank outcome at the state's R no trade
   (D-315). Never the rung the walk settled on, which the outcome chooses. The capped and uncapped subsets are reported
   beside the whole, each with its count; leaving a trade out is only the labelled fallback where the log cannot
   support the walk. **Built** in the Studio (SD-86, 2026-10-26, `be0cf84`: `studio/execution.py` and its
   `docs/EXPORT_FORMAT.md`), and the wording above matches it. One name is settled at registration (§8a): §5.7 and P5
   read "the confirmation's lower-bound mean", and the walk reads the log the export is read against. Reading it
   against the P-06 mirror (§2) keeps the lower bounds the confirmation's.

## 8a. Everything still open before registration, and who closes it (2026-10-29)

| # | open | who closes it | when |
|---|---|---|---|
| 1 | The live feed and account (item 1; Stage 3 step 5; `docs/OPERATOR_SETUP.md` item 2), with the vendor's terms for keeping each day's bars and for sending the nightly figures (Stage 3 step 5 item 10) | the operator (a payment); Stage 3 states the request | first: everything on live data waits on it |
| 2 | The start date (item 2) | Stage 2, once item 1 is connected | after 1 |
| 3 | The firm's rules re-verified within seven days before the start, each with article id and date, and D-336's declared assumptions re-read (protocol §2.5). Among them are the two rows FV3-C leans on that the help centre does not state: `xfa_seat_frees_at` (D-446; D-353's same-evening seat) and `xfa_closure_at_request` (D-444; the table's abandon) | Stage 2 (the rules-verifier); a changed rule reopens the research | in the seven days before the start |
| 4 | The p95 path and the FLAG levels: `scripts/fv3c_confirmation_path_detail.py` (refused unless it reproduces P-06's saved paths exactly), then `scripts/success_thresholds.py`, which writes `results/success_thresholds.csv` | Stage 2 (R1's file, D-457 (5)); no purchase | before registration |
| 5 | The registration's result file. It holds: P1-P6 (`criteria.paths_quantile`, `criteria.p95_path`, `results/fv3c_xfa_time_budget.csv`, the lower-bound mean); R5's band (`results/fv3_studio_corrected_v1_days.csv`); R1 (b) and R2 from `results/shadow_system_levels.csv`, re-run from a clean tree so its manifest names a commit, not `-dirty` | Stage 2 | at registration |
| 6 | The bankroll figure (item 3), and whether "plus one subscription" is the one inside `pf_required_p90` or a second | the decision row (Stage 2) | at registration |
| 7 | The execution assumptions (item 4) | the operator; meanwhile a safe default is recorded: L = 2 minutes (D-282), the card's three windows, the stress-priced missed share | before registration |
| 8 | §6a's burn-in and the derived levels accepted: 10 sessions; each FLAG at the burn-in's largest reading; R1 (a) and R3's FAIL-SYSTEM at L; R4's at L less R3's FLAG | the decision row (Stage 2) | before registration |
| 9 | The terminal's §6a changes: R2 per window (`eve`, `asia`, `ny`, `rth`) with the longest run beside it (R1 (b)); R3's and R4's FAIL-SYSTEM levels; the burn-in's "not judged" state for R1 (a), R3 and R4's offset, and its computation at the burn-in's end; the NTP refresher on for the period; R7's comparison extended to a bar's presence; the board's level sources no longer "not yet sourced"; optionally each bar's evaluation time (R3) | Stage 3, each as its own row | after 8, before registration |
| 10 | The vendor's historical bars for the period's sessions, re-pulled weekly (R7, and R2's fault test) | the operator (each pull a Databento purchase, stated with its cost first) | weekly from the start |
| 11 | The NQ top-up from 2026-07-17, once the start fixes the reserve's end (`docs/OPERATOR_SETUP.md`); the period itself does not need it | the operator (a payment) | after the start is fixed |
| 12 | The FOMC rows (R9): 2026-12-09 confirmed on its statement page after its meeting, then each 2027 row as it falls. The terminal's calendar is re-vendored: its copy still lists 2026-10-28 as scheduled, confirmed here under D-449, which R9 would flag | Stage 2 (each row, under a decision row); Stage 3 (the re-vendor, its step 5 item 10) | each meeting as it passes; the re-vendor before the start |
| 13 | The terminal re-vendors Stage 2 at the registration's engine commit (its NEXT_STEPS step 4 item 7, the rules ledger's new rows with it), with the parity test, the port check and the export test green; that commit is written into §2 | Stage 3, then Stage 2 | before registration |
| 14 | The log the edge check's walk reads (item 7 against §5.7 and P5) | Stage 2 with the Studio | at registration |
| 15 | The Studio's export format, its questions 1 and 6 (open until the paid account, D-398 (4)) | the Studio | after 1 |
| 16 | The file committed and hashed (the committed content, §2), and handed to the prereg-gatekeeper | Stage 2 | last |
| 18 | The operating rule of D-549: a replacement Combine is bought (or reset) only after the 16:00 CT close, for the next session -- never intraday after a breach -- so no Combine is bought and blown in one trading day; the period's log checks it every day | Stage 2 (written into §2), Stage 3 (the terminal enforces it) | before registration |
| 17 | FV3-C holds a few report-day positions, entered before 07:30 CT, across the BLS release (`results/news_minute_exposure.csv`, D-534): whether holding into a scheduled major release counts under Topstep's wording ("purposefully trading your full Maximum Position Size directly into a scheduled major news event", 10305426) is read on the official page, and if it might, the protocol flattens or does not enter before the release -- declared before registration | Stage 2 (the rules-verifier, then a decision row) | before registration |

## Outcome

*(Filled in after the period. Record it whether it passed or failed; then add the row to `REGISTRY.md`.)*
