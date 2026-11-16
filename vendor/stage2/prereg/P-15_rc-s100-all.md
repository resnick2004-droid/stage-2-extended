# P-15 — RC (rc_s100_all): the resolved coin re-entering when flat on P-14's design -- the development test, with D-509's consistency lines

> Registered 2026-11-02 as P-15 on the prereg-gatekeeper's second review (the first refused it, D-530). Drafted
> 2026-11-02, for the operator's approval and the prereg-gatekeeper; **revised after the gatekeeper's first
> refusal** (recorded by D-530: the card made the selected model's, the seed fixed by D-529 (2), the variant counts read
> from `results/variants.jsonl`, T23's exclusion stated, the planning sd's source, the unverified rules named, the run
> command). Written after D-527 carried family RC's
> `rc_s100_all` cell from its re-entry screen (D-525), after the card (`docs/candidates/cards/RC.md`) passed
> `validate_card`, and before any registered campaign of it ran. Everything it fixes is `scripts/rc_dev_test.py` at the
> commit that registers it: **P-14's registered test (`scripts/a3_brk30_cb20.py`, `prereg/P-14_a3-brk30-cb20.md`) with
> RC's trades in place of A3-BRK30's** -- the same money side, arms, lines and verdict rule. It refuses to run without
> this id, and refuses before any verdict unless each identity of §3 holds. No confirmation is registered with it: the
> confirmation needs unread data not yet bought (§2, §5).

| field | value |
|---|---|
| **id** | P-15 *(assigned by the prereg-gatekeeper, 2026-11-02)* |
| **date** | 2026-11-02 |
| **author** | stage-two session (stage-2-9c), for the operator (Ryan Resnick) |
| **task** | D-521 / D-525 / D-527: family RC, the operator's "randomness with set risk and reward and contract settings that always resolve" |
| **protocol step** | 4 of `docs/RESEARCH_PROTOCOL.md` (D-155): written after the card and its screen (D-525's re-entry screen), before the prop-environment run |
| **status** | registered |

## Machine-checked fields

| key | value |
|---|---|
| `k` | 1 |
| `development_period` | 2020-01-01 .. 2026-07-16 (NQ's development and spent held-back windows of `config/windows.yaml`, both development since D-461; every study of the pool read all of it) |
| `confirmation_period` | none |
| `confirmation_tests_on_this_market` | 3 (P-05, P-06, P-10: NQ's held-back window spent, D-107; the reserve from 2026-07-17 would be NQ's fourth test, the operator's decision, D-461) |
| `bonferroni_alpha` | 0.05 (one-sided 0.05 / k 1); the verdict's bound is at one-sided 0.05/N = 0.05/403 (D-189): see the multiplicity plan |
| `assumed_sd` | 1.631 (planning input, not a result, D-529 (4)) |
| `assumed_sd_source` | planning input, not a result (D-529 (4)); it decides nothing: the sample standard deviation (ddof 1) of `r_3` (net R per micro at 3:1, the fresh funded account's R and the widest R the table offers) over the cell's 295,296 offered candidates -- `rc_dev_test.planning_sd`, reproduced by `python scripts/rc_dev_test.py --planning-sd` at the commit that registers this file (it prints every R's, nothing written) and recorded in the registered result's manifest (`planning_sd`); every narrower R's smaller; the registered run reports every R's sd in its `edge` rows |
| `risk_denominator` | intended -- the table's dollar risk at the 25-point stop in whole micros, the allowance and the Combine's room cap applied |
| `primary_metric` | growth on the required bankroll -- `pf_growth_on_base_p50` on `pf_required_p90` (D-312, D-457); never `median_log_growth`, the notional column; with D-509 (3)'s four slice lines beside it in the verdict |
| `data_period` | 2020-01-01 .. 2026-07-16 (the local bars' development days through the walk at every five-minute mark; FV3-C's development campaign for the slice reference, 2019-11-12 warm-ups to 2025-06-30; nothing past 2026-07-16 is read) |
| `seed` | 20261204 (the campaign, every resampled arm -- fixed by D-529 (2) before anything was read at it; the build's 4-path smoke ran every arm at it before D-529, printing and writing nothing, nothing read); 20261131 (the screen's and P-14's, used only by the identities (a) and (c), §6); 20261102 (the coin, fixed by D-521); 20261017 (the bootstraps beside it, §6) |
| `model_card` | docs/candidates/cards/RC.md |
| `power_rr` | 1.5 (the fresh Combine's R in the table) |
| `power_effect` | 0.00 (the card's `edge_assumed`: a coin carries no information) |
| `boot_len` | 21 (the bound's block: 21 sessions, P-06's rule) |
| `required_trades_source` | assumed_sd fallback: the L5 curve gives the trades needed to find a planted positive edge, and a coin has none by construction -- the money, if any, is the contract's shape through FV3-C's design, and the campaign decides at the bound |
| `required_trades` | not an edge search: the gate reads the campaign at each R's bound over 21-session blocks, which about one hundred seventy offered candidates a day fill in every block |
| `available_trades` | 295296 (the cell's offered candidates over the development period: `results/rc_reentry_screen.csv`'s `rc_s100_all` row, `candidates`; the campaign takes far fewer -- one an account a session at most -- read as `trades_taken_per_session` on that row) |
| `ledger_n` | 403 -- `propedge.research.ledger.count_n` on `prereg/models.yaml` for RC, pool `pool-2026-11-02-rc`, NQ, minute, 2020-01-01 .. 2026-07-16: k 1; every row `pool-2026-10-31-cb20` counts (369: everything P-14's k-less count held); P-14 (1); D-518's customer journey (`customer_journey` 22); D-523's fixed-slot screen (`rc_screen` 2); D-525's re-entry screen (`rc_reentry_screen` 8). The program's per-configuration model readings are not trials (the multiplicity plan) |

**Multiplicity plan.** RC's `rc_s100_all` is one cell of D-525's re-entry screen, carried by D-525 (6)'s selection rule
(the surviving all-window cell with the higher growth at the bound) after that exploratory read (D-527) -- **a choice made
after seeing results**, so a new candidate whose pool counts what was read. k = 1. It was chosen from **N = 403** trials on
this market and window (`ledger_n`), counted by the gatekeeper's rule for P-13 and P-14 (D-499 (2), D-512): **every ledger
row whose run chose a component the candidate keeps.** RC keeps P-14's whole money side -- FV3-C's protocol and rungs, the
no-closure table, the budget, the strict rule, the bounds and eras -- so **every row P-14's pool counted counts here
(369)**, and **P-14 itself (1)**, whose PASS (D-513) chose that money side. Then the family's own reads: **D-518's customer
journey (22)** -- read on P-14's family and FV3-C's just before D-521 declared RC, counted conservatively: 16 readings
under `D-518:customer_journey` and its 6 `hypothetical_hedge` readings under `D-518:hypothetical_hedge`
(`results/variants.jsonl`, counted by `VariantCounter`), all included; **D-523's fixed-slot screen (2)** -- its scheduling fault (D-525 (1)) re-declared
the family, so its cells were read before the carried cell was chosen; **D-525's re-entry screen (8)** -- the carried cell
was selected among its eight cells (the customer windows are product readings, but each counts). **Alternatives, stated
for the gatekeeper:** counting only D-518's 16 non-hypothetical readings gives N = 397; leaving D-518 out, 381; leaving P-14
out as a trial, 402. **Not counted:** T23's fixed-time search (`pool-2026-10-20-t23`: P-07 and its screens) -- RC keeps none
of its choices (T23's slots, its d20 stop, A3's direction), D-499 (2)'s rule, as `pool-2026-10-24-t24` and the a-pools
exclude it (D-521 (4)'s parenthetical counting T23 is corrected by D-530); the scoreboard's coin columns (D-528, a reading of result files), the stop
distributions (readings of trades), the hypothetical hedge studies D-514/D-515 (in no pool), and the Focused Trader
Program's models run beside each configuration (readings under the firm's enforcement scenarios, as the denial arms are;
D-234, D-499). The carried cell counts twice (in k and in `rc_reentry_screen`), the conservative side by one. This test
has no held-back period, so the one-sided 0.05/N sentence binds its verdict (D-189, D-230, D-419): **PASS** only if the
D-145 gate's campaign grows with each R's outcomes shifted to the bound at 0.05/N, every line of §5 holds, **and all four
slice lines hold**; the same campaign at the one-sided 95 % bound is a **continuation gate**, never a pass. **A fresh
seed changes no count** (D-512).

**Known before the run (disclosed).**

1. **The gate's 0.05 arm was effectively read by the screen.** D-525's re-entry screen ran this cell's gate campaign --
   the same trades, the 0.05 bounds by the era rule, the no-closure table, the budget, the strict rule, the capacity --
   at seed 20261131 and 500 paths, and D-527 read its growth on the required bankroll at the bound and the point (above
   zero, above FV3-C's development row, just below P-14's) and its zero-edge twin (`results/rc_reentry_screen.csv`,
   sha256 `dfd93c46deca5651e125ba63a8616b3b6f627beea87097593dbac27df4c37df1`, from a clean checkout of cc7deb1).
   **Answered as D-512 answered P-14:** every resampled arm of the registered run draws at a fresh campaign seed,
   **20261204**, fixed by D-529 (2) before anything was read at it; the screen's run stays as a
   **refusing identity** (§3 (c)): the cell at the screen's seed 20261131 must reproduce the screen's growth at the
   bound and the point and its required bankroll before any registered arm runs. The registered 0.05 arm at 20261204 is
   not independent of the screen's read (500 paths resampled from the same days), but it is a new draw no one has seen.
   **Disclosed:** before D-529, the build's `--check --paths 4 --starts 6` smoke ran every arm at 20261204 at 4 paths
   (and the slices and journey on six starts) to test the code; it printed and wrote nothing, and nothing was read from
   it.
2. **The customer windows** (`rc_s100_asia`, `rc_s100_london`, `rc_s100_us`) were read by the same screen; they are
   beside here, never deciding.
3. **The slice lines are NOT known.** D-508's slices hold no RC row; D-518's journey holds none either. The cell's slices
   at 21, 63 and 126 sessions and its D-518 journey readings are computed for the first time by the registered run.
   FV3-C's reference slices are D-508's `fv3c` rows (`results/customer_slices.csv`, sha256
   `0009afa7be22a657a065f1939ded0f53088e59e17ca6a338cd74ced0f248bd98`), reproduced by the run and refused otherwise.
4. **The coin has no fitted signal parameter.** Its sides are a fair coin seeded 20261102 per date and mark (D-521, before
   any read); its marks every five minutes from 17:00 CT (D-525); its cutoff a resolution rule on kind columns only
   (D-212's 5 %, a test shows it blind to P&L); its rung one of FV3-C's two (the choice between 12.5 and 25 points is the
   only search, inside the 10 screen cells N counts); everything else is P-14's.

**What is not yet read:** every resampled arm at 20261204 -- the gate at 0.05 and at 0.05/403; the denial ladder, the
placement on, the zero-edge twin, the fixed-legs twin, the gf15b reading, the check period, the Focused Trader Program's
16 models, the campaign without the strict rule and the customer windows under that seed; the fidelity line; the slice
lines and the like-for-like slice reading; D-518's journey readings for this cell; the FLAGs and the scoreboard row.

---

## 1. Question

Does a coin -- an entry offered every five minutes all session on NQ, its side a seeded fair coin, on FV3-C's 25-point
rung, taken when every account is flat -- grow cash on Topstep's contract at the bound under P-14's design (FV3-C's
protocol and table re-solved without closure at request, at most 20 Combine purchases and resets in any 21 trading days,
the operator's strict one-at-a-time rule), **and** stay at least as consistent as FV3-C for a customer who starts on any
day? A **yes** at the binding bound (0.05/403) with every line and every slice line holding is a pass; the gate's yes
with a slice line failing is **CONTINUE (consistency)** (D-509's rule); a yes only at the 95 % bound a continue; any of
these waits for a confirmation on unread data registered on its own. A **no** at 95 %, or one of §5's lines failing, ends
the family. **What a PASS shows, plainly:** on development data already read by the screen that chose this cell, a
campaign with no signal at all grows the bankroll the run itself requires at the 0.05/403 bound on a fresh draw of
paths, **with the firm paying every payout requested** (0 % denial, D-234) and the placement off (D-289). It shows the
money is the contract's shape (D-145, D-452): the coin carries no edge by construction (every R's gross e is zero in
expectation; its net e is its costs below zero). It does not show an edge, performance out of sample, that the firm
would pay (tier 3's pattern; the Focused Trader Program beside, never the gate), or anything a money decision rests on.
**Confounds of the slice comparison, stated:** (i) different windows -- the coin's 2020-01-02 to 2026-07-16, FV3-C's
2021-01-04 to 2025-06-30 (the like-for-like reading over common start days beside); (ii) different vendors -- Databento
for the coin, QuantConnect for FV3-C; (iii) the strict rule on the coin, not on FV3-C (against the coin); (iv) the
one-tick entry against FV3-C's max(1 tick, the recorded spread) (for the coin).

## 2. Data period

- **Source** (D-458 (5)): P-14's -- the operator's Databento NQ one-minute bars (GLBX.MDP3 ohlcv-1m) in the local store
  `data/bars/NQ` (git-ignored), read through `config/windows.yaml`'s guard (D-459), walked at every five-minute mark from
  17:00 CT by `atlas_a3.walk_minutes` on FV3-C's rungs (`propedge/research/fv3_rung_walk.py`), A1's 1,691 day records
  2020-01-02 to 2026-07-16 (`a3_brk30.inputs`); nothing is cached for the coin's walk (it runs in memory each time). **The
  source's validation** (D-473): `docs/data_reports/data_report_bars_NQ_2026-10-30.md`, VALIDATED with P-13's caveats
  (C1-C8 as P-14's §2), C8 (minute bars cannot order a target and a stop touched in one minute, settled as the stop)
  applying to every offered mark.
- **The slice reference's source**: FV3-C's development campaign as D-508 built it (`customer_slices.fv3c_campaign`).
- **Symbols and resolution**: NQ, MNQ micros and NQ minis for sizing; minute.
- **In-sample**: 2020-01-01 .. 2026-07-16.
- **Out-of-sample**: none here. **Its confirmation needs unread data not yet bought**: ES's declared unread window
  (2025-07-01 .. 2026-09-30, `config/windows.yaml`) needs ES bars (`docs/OPERATOR_SETUP.md` item 1, a payment), or NQ's
  reserve from 2026-07-17 needs the operator's decision (D-107, D-461) and a bar top-up -- **the operator's call**; a
  confirmation is registered on its own when that data exists.
- **Walk-forward scheme**: none -- one frozen configuration, chosen once.

## 3. Rules fixed before the run

**Everything of P-14's §3 is carried unchanged except the trades** -- the no-closure table and its pinned hashes (read by
`a3_brk30_cb20.noclose_plan`), the purchase budget (20, 21), the strict rule at 5 minutes, the campaign (`atlas_a3.gate_kwargs`
through `gate.run_gate`: FV3-C's engine call under `config/fv3_corrected_portfolio.yaml`, five accounts, one trade an
account a session, MAE settlement, the room cap, the 45-tick stand-aside, need-aware Combine exits, the fee at the
contracts held, the Standard path, `aeropay`, the bankroll an output, 500 paths over 504 sessions, the margin one
subscription, the day capacity at the cell's busiest day), the eras, the check period, the deciding bound, the costs and
the fill profile (`assumed`), the fixed-legs twin in P-06's form, the gf15b reading, the Focused Trader Program beside
with its binding summary, the campaign without the strict rule beside, and D-509 (3)'s slice lines verbatim.

- **Entry** (D-521, D-525): an offer at every five-minute mark from 17:00 CT (`resolved_coin.marks`) that the cutoff
  admits at the 25-point rung; a report day's marks before the 07:30 CT cut dropped (A3's and P-14's rule); entered at
  the first bar opening after the mark, one tick adverse (an alert at the mark; the operator's five minutes counted from
  it, D-522 (2)); its side a fair coin seeded 20261102 per date and mark (`resolved_coin.coin_table`).
- **The cutoff** (D-525 (4), D-212): a mark is offered only if its unresolved share (flattened at 15:08 without a level,
  both sides pooled) is at most 5 % over the window at every R the table offers (0.25, 1, 1.5, 2, 2.5, 3) --
  `resolved_coin.mark_resolution`, kind columns only.
- **Re-entry when flat**: every offered mark is a candidate in its day's block; the strict router takes the first
  candidate at least five minutes after the last position's exit and refuses the rest.
- **Stop, exit, bracket**: FV3-C's 25-point rung; the state's R from the table (every quarter R to 3R walked); FV3's
  breakeven, MAE and the 15:10 CT flatten; no time stop.
- **The identities, each refusing before a verdict and before anything is written** (in this order):
  (a) P-14's own trades through this engine call reproduce `results/a3_brk30_cb20_gate_paths.csv`'s `gate` run, all 500
  paths, point and bound at 0 %, at seed 20261131 (`rc_screen.identity_problems`);
  (b) the cell's trades are `results/rc_reentry_screen.csv`'s `rc_s100_all` (sha256 above): the candidate count, the
  busiest day, the day capacity, the long share, the candidates a day and every R's unresolved share equal its row, and
  the trades' content hash equals `2ffcc96be321d038e039acdec1ca1f517b7797b7acdc97a07f86747e4f0a7926`
  (`rc_dev_test.trades_hash`; the same in two independent builds);
  (c) the cell at the screen's seed 20261131, 500 paths, reproduces the screen's growth on the required bankroll at the
  bound and the point and its required bankroll (section `screen_identity`, never a gate row), before any registered arm;
  (d) FV3-C's slices equal `results/customer_slices.csv`'s `fv3c` verdict rows (sha256 above), start for start.
- **The slice lines** (D-509 (3), verbatim as P-14's §3): over every start of the window in historical order, the cell's
  bound-shifted arm against FV3-C's development configuration as frozen, at 63 trading days -- (a) `share_positive`
  ≥ FV3-C's, (b) `net_p10` ≥, (c) `share_no_payout` ≤, (d) `needed_bankroll_p95` ≤; 21 and 126 beside. **How the coin's
  slices are computed:** D-518's journey replay (`customer_journey._single_replay_task`: runs of exactly 21, 63 and 126
  sessions, D-508's convention -- D-518's identity tied this path to `customer_slices.csv` start for start), the cell's
  `customer_slices.Campaign` built from its point blocks and P-14's engine arguments; FV3-C's by `customer_slices`' own
  job list; `customer_slices.summarise`; `a3_brk30_cb20.slice_lines`; the like-for-like reading over common start days
  beside (`a3_brk30_cb20.common_slices`). Every slice in `results/rc_s100_all_gate_slices.csv`.
- **The gf15b reading rests on unverified rules** (as P-14 stated, D-512 (5)): T24-GF15b's fixed plan closes accounts at
  request (`t24_screen._closing`), so its beside rows rest on the unverified `xfa_closure_at_request` and
  `xfa_seat_frees_at`; the no-closure table that sizes every deciding arm closes no funded account, so the verdict rests on
  neither. The inherited payout credit for a payout requested before an account ends by a breach applies as at every
  registration since P-09.
- **Beside, never deciding:** the three other customer windows -- each window's own trades and bounds through the same
  engine call at seed 20261204, point and bound at 0 % (section `window_beside`); D-518's journey measures on the cell's
  verdict-arm replay (section `journey`).
- **Parameters, with their exact values**: the card's §4; `scripts/rc_dev_test.py`'s, `scripts/rc_reentry_screen.py`'s,
  `propedge/research/resolved_coin.py`'s, `scripts/a3_brk30_cb20.py`'s and `scripts/atlas_a3.py`'s constants;
  `config/atlas_a3.yaml`; `config/fv3_corrected_portfolio.yaml`; `config/fv3_portfolio.yaml`; k = 1.

**Conduct check in D-145's three tiers:**

- Tier 1, hard:
  - [x] no cross-account hedging -- no two accounts ever hold a position at once (the strict rule); one firm
  - [x] no reliance on simulator fills or fills outside the best bid or offer -- market entries at the first bar after the
    mark, a tick adverse; a 25-point stop
  - [x] no maximum size into major news; no coordinated trading -- no entry before a BLS report's cut; one position on one
    account at a time. **Stated limit:** FOMC days and other scheduled releases are not excluded by the coin's marks
    beyond the report-day cut (A3 dropped FOMC days through A1's day set; the coin uses the same day set)
  - [x] nothing designed to conceal a pattern from the firm or evade its detection -- the coin hides nothing; the budget
    restrains a pattern the firm names, chosen on growth and the program's readings, not on a detection level
- Tier 2, modelled: P-14's -- the fresh XFA's $2,000 at half the drawdown on the 25-point stop; the Combine's menu reaching
  R 0.25; several accounts at the MLL in one day measured; the placement off in the base case, on beside.
- Tier 3, priced: P-14's -- the gate at 0 % denial; 10, 25 and 50 % and the break-even denial beside; payouts exposed,
  Combine purchases (at most 20 in any 21 days under the budget); the Focused Trader Program's 16 models beside.

**The run** (D-474, as P-14): once, from a clean detached checkout of the commit that registers this file --
`python scripts/run_clean.py --name rc-dev -- python scripts/rc_dev_test.py --prereg P-15 --workers 4`, then
`python scripts/run_clean.py --name rc-dev --collect`; the ignored stores `data/bars` and `data/atlas` linked in as
junctions; one BLAS thread; `--workers` the memory guard's grant (bit for bit the rows of one process, R11). Written:
`results/rc_s100_all_gate.csv`, `results/rc_s100_all_gate_paths.csv`, `results/rc_s100_all_gate_slices.csv`, each with its
manifest (not exploratory, `prereg_id` this id).

## 4. Metrics

P-14's §4 exactly, with the coin's trades: growth on the required bankroll at 0 % denial with the placement off at each
R's bound at 0.05/N (the verdict's) and at 0.05 (the continuation gate's); the four slice lines at 63 days with 21 and 126
beside; the lines of `docs/SUCCESS_CRITERIA.md` §3 (each offered R's unresolved share overall and in its worst year at
most 5 %, `a3_brk30.resolution_rows`; realised over intended capped risk at least 0.9); beside, never the verdict: the
denial ladder, the break-even denial, the program's summaries, the strict rule's cost, the placement on, the zero-edge
twin, the fixed-legs twin and the gf15b reading, the point arm, the customer windows, each R's e and bounds at 0.05,
0.05/k and 0.05/N with its sd against `assumed_sd` and propsim D-47's criterion, the deflated Sharpe at N, the tier-3 and
budget counts, the drift decomposition (`a3_brk30.drift_rows`: how much of each R's e is the market's drift against a
fair coin's balanced sides), the period rows, D-518's journey measures, and the trades' content hash. FLAG levels as P-14
(the scoreboard after the run).

## 5. Pass / fail criteria

All at 0 % denial with the placement off, each R's bound as the era rule reads it (`t23_d20.verdict_of`, with the lines),
then D-509 (3)'s rule (`a3_brk30_cb20.verdict_word`). **The 0.05/N sentence** (`docs/SUCCESS_CRITERIA.md` §2, D-189, D-230,
D-419): a development verdict is read at `e`'s one-sided bound at 0.05/N, N = 403. Neither PASS nor CONTINUE meets the
D-145 gate, satisfies exit (A) or supports a money decision.

- **Refused before a verdict** (the failure protocol's diagnosis, never a rerun until it passes): any of §3's four
  identities failing, or a pinned file not the one fixed here.
- **Pass**: growth above zero on the arm at e's bound at 0.05/N (and so at 0.05); every line holding; **and all four slice
  lines holding**.
- **Continue (consistency)** -- not a pass: the gate's PASS with one or more slice lines failed, recorded as such (D-509 (3)).
- **Continue (not a pass)**: above zero at the 0.05 bound only, every line holding -- one confirmation on unread data
  decides it. The slice lines are read beside it, never changing it.
- **What PASS adds over CONTINUE** (D-419): both wait for one confirmation on unread data, and a PASS gets no levers; a
  PASS clears the multiplicity bar of everything this pool tried (0.05/403) and so carries the stronger development
  record into the queue behind FV3-C's shadow period, where a CONTINUE carries only the unadjusted 95 % reading.
- **Fail**: not above zero at the 0.05 bound, or one of the lines failing.
- **Beat FV3-C's row or stop** (D-365, D-382, D-452): the gate row's growth at the 0.05 bound against
  `results/scoreboard.csv`'s `FV3-C-dev`; not beating it, RC is not pursued past its verdict. Beside: P-14's row (the same
  money side with the breakout's trades) -- whether the breakout adds anything over a coin at this protocol, read, never a
  line.
- **The confirmation window** (named, not registered here): ES's declared window or NQ's reserve, once bought and opened
  by the operator; the Combine's headroom over its target is checked against that window's bound before registering it
  (D-451).
- **What a fail means**: family RC ends, kept on record and diagnosed by the failure protocol, never rerun until it passes;
  the coin's screen row stays the scoreboard's baseline (D-528).

## 6. Seed

- **Seed**: **20261204** -- the campaign's resampling on every registered arm, twin, section and customer window; fixed by
  D-529 (2) before anything was read at it, so it chooses nothing; used by no other script (a test checks it). The
  build's 4-path smoke ran every arm at it before D-529, printing and writing nothing; nothing was read from it.
- **Identity seed**: 20261131 (the screen's and P-14's) -- used only by identities (a) and (c), run before every
  registered arm.
- **The coin's seed**: 20261102 (D-521) -- the sides; drawn once over the whole grid of dates and marks.
- **Additional seed**: 20261017 -- the eras' whole-year bootstrap and `haircut.widened`'s day bootstrap. The slices and
  the journey draw nothing (historical order).

## 7. Variants

- Configurations already tried for this question: the ledger's pool, N = 403 with this registration (above): P-14's pool
  (369), P-14 (1), D-518's 22 readings (`D-518:customer_journey` 16, `D-518:hypothetical_hedge` 6), D-523's 2
  (`D-521:rc_screen`), D-525's 8 (`D-525:rc_screen`).
- Configurations this pre-registration will try: 1 (`rc_s100_all`). Beside it, never a verdict: the Focused Trader
  Program's 16 declared models on its campaign, recorded as exploratory variants under `D-527:rc_s100_all_ftp`; the
  campaign without the strict rule and the customer windows (readings, no variant); the identities.

## 8. Anything chosen after seeing results

*(Left empty at registration.)*

---

## Outcome

- **Date run**: 2026-11-02, once, by `python scripts/run_clean.py --name rc-dev -- python scripts/rc_dev_test.py --prereg
  P-15 --workers 4` from a clean detached checkout of 8f9644f (D-531's commit, D-474).
- **Result file(s)**: `results/rc_s100_all_gate.csv` (sha256 `7e9a599a7cc9`), its per-path file and its slices file, each
  with its manifest (`exploratory: false`, `prereg_id` P-15, campaign seed 20261204); the four identities held first
  (P-14's per-path record, the screen's trades and their hash, the screen's growth at 20261131, FV3-C's slices).
- **Verdict**: **PASS** on development data -- the gate grows on the required bankroll at the bound at 0.05/403
  (1.2338092519037749) and at 0.05 (1.3147622470794125), every offered R resolving, realised risk at the line; all four
  of D-509's slice lines hold against FV3-C (section `slice_lines`). The audit follows (D-532).
- **Beside, never deciding** (the file's rows): the zero-edge twin grows above the traded arm (the money is the
  contract's shape; the coin has no fitted signal); 10 % denial still grows, 25 % less, 50 % does not; the placement on
  does not grow; nearly every payout is exposed to tier 3; the check years and the three other customer windows grow.

