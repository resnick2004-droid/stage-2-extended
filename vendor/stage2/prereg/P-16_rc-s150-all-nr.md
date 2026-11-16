# P-16 — RC150 (rc_s150_all_nr): the 37.5-point news-safe coin re-entering when flat on P-14's design -- the development test, with D-509's consistency lines

> Registered 2026-11-03 as P-16 on the prereg-gatekeeper's first review (seed 20261206 and N = 414 as fixed by D-545).
> Drafted 2026-11-03, for the operator's approval and the prereg-gatekeeper, after D-544 made `rc_s150_all_nr` a new
> candidate (D-538's stop-width screen, D-542's funded-risk diagnostic), after the card
> (`docs/candidates/cards/RC150.md`) passed `validate_card(for_prereg=True)` on a stand-in stop distribution, and before
> any registered campaign of it ran. Written in P-15's form and answering, in advance, every finding of the
> gatekeeper's first review of P-15 (D-530) and every caveat of P-15's audit (D-533). Everything it fixes is
> `scripts/rc150_dev_test.py` -- **P-15's registered test (`scripts/rc_dev_test.py`, whose runner it reuses through
> `rc_dev_test.Spec`) with the 37.5-point news-safe cell in place of P-15's**, plus two readings beside (the funded-capped
> cell and the multi-breach share). It refuses to run without this id, and refuses before any verdict unless each identity
> of §3 holds. No confirmation is registered with it: the confirmation needs unread data not yet bought (§2, §5).

| field | value |
|---|---|
| **id** | P-16 *(assigned by the prereg-gatekeeper, 2026-11-03)* |
| **date** | 2026-11-03 |
| **author** | stage-two session (stage-2-9c), for the operator (Ryan Resnick) |
| **task** | D-538 / D-542 / D-544: family RC's stop-width choice -- the operator's "randomness with set risk and reward and contract settings that always resolve", at the stop where the coin's costs are a smaller share of its risk |
| **protocol step** | 4 of `docs/RESEARCH_PROTOCOL.md` (D-155): written after the card and its screen (D-538) and diagnostic (D-542), before the prop-environment run |
| **status** | registered |

## Machine-checked fields

| key | value |
|---|---|
| `k` | 1 |
| `development_period` | 2020-01-01 .. 2026-07-16 (NQ's development and spent held-back windows of `config/windows.yaml`, both development since D-461; every study of the pool read all of it) |
| `confirmation_period` | none |
| `confirmation_tests_on_this_market` | 3 (P-05, P-06, P-10: NQ's held-back window spent, D-107; the reserve from 2026-07-17 would be NQ's fourth test, the operator's decision, D-461) |
| `bonferroni_alpha` | 0.05 (one-sided 0.05 / k 1); the verdict's bound is at one-sided 0.05/N = 0.05/414 (D-189): see the multiplicity plan |
| `assumed_sd` | 1.5427 (planning input, not a result, D-529 (4)'s form) |
| `assumed_sd_source` | planning input, not a result (D-529 (4)'s form); it decides nothing: the sample standard deviation (ddof 1) of `r_3` (net R per micro at 3:1, the fresh funded account's R and the widest R the table offers) over the cell's 239,768 offered candidates -- `rc_dev_test.planning_sd` on this cell, reproduced by `python scripts/rc150_dev_test.py --planning-sd` at the commit that registers this file (it prints every R's, nothing written) and recorded in the registered result's manifest (`planning_sd`); every narrower R's smaller; the registered run reports every R's sd in its `edge` rows |
| `risk_denominator` | intended -- the table's dollar risk at the 150-tick stop in whole micros, the allowance and the Combine's room cap applied |
| `primary_metric` | growth on the required bankroll -- `pf_growth_on_base_p50` on `pf_required_p90` (D-312, D-457); never `median_log_growth`, the notional column; with D-509 (3)'s four slice lines beside it in the verdict |
| `data_period` | 2020-01-01 .. 2026-07-16 (the local bars' development days through the walk at every five-minute mark; FV3-C's development campaign for the slice reference, 2019-11-12 warm-ups to 2025-06-30; nothing past 2026-07-16 is read) |
| `seed` | 20261206 (the campaign, every resampled arm -- fresh, used by no other script or module (a test checks), to be fixed by the decision row that sends this draft to the gatekeeper; the build's `--check --paths 4 --starts 6` smoke ran at it before that row, printing and writing nothing, nothing read -- §"Known before the run" (1)); 20261131 (the screen's, the diagnostic's and P-14's, used only by the identities (a) and (c), §6); 20261102 (the coin, fixed by D-521); 20261017 (the bootstraps beside it, §6) |
| `model_card` | docs/candidates/cards/RC150.md |
| `power_rr` | 1.5 (the fresh Combine's R in the table) |
| `power_effect` | 0.00 (the card's `edge_assumed`: a coin carries no information) |
| `boot_len` | 21 (the bound's block: 21 sessions, P-06's rule) |
| `required_trades_source` | assumed_sd fallback: the L5 curve gives the trades needed to find a planted positive edge, and a coin has none by construction -- the money, if any, is the contract's shape through P-14's design, and the campaign decides at the bound |
| `required_trades` | not an edge search: the gate reads the campaign at each R's bound over 21-session blocks, which about one hundred forty offered candidates a day fill in every block |
| `available_trades` | 239768 (the cell's offered candidates over the development period: `results/rc_width_screen.csv`'s `rc_s150_all` row, `candidates`; the campaign takes far fewer -- one an account a session at most -- read as `trades_taken_per_session` on that row) |
| `ledger_n` | 414 -- `propedge.research.ledger.count_n` on `prereg/models.yaml` for RC150, pool `pool-2026-11-03-rc150`, NQ, minute, 2020-01-01 .. 2026-07-16: k 1; every row of `pool-2026-11-02-rc` counts (402: everything P-15's k-less count held); P-15 (1); D-535's news-safe reading (`rc_nr_dev` 1); D-538's stop-width screen (`rc_width_screen` 8); D-542's diagnostic (`rc_width_diag` 1). The program's per-configuration model readings are not trials (the multiplicity plan) |

**Multiplicity plan.** RC150's `rc_s150_all` is one cell of D-538's stop-width screen, carried by D-538 (4)'s rule (an
all-window wider cell that clears the kill line, resolves at every offered R and grows more at the bound than the 25-point
news-safe reference at the same seeds, D-542) and kept after D-542's funded-risk diagnostic (D-544) -- **choices made after
seeing results**, so a new candidate whose pool counts what was read. k = 1. It was chosen from **N = 414** trials on this
market and window (`ledger_n`), counted by the gatekeeper's rule for P-13, P-14 and P-15 (D-499 (2), D-512, D-530):
**every ledger row whose run chose a component the candidate keeps.** RC150 keeps everything RC kept -- P-14's money side,
the coin, its seed, the re-entry, the cutoff, the all-day window -- so **every row of P-15's pool counts here (402)**, and
**P-15 itself (1)**, whose PASS (D-532) is the result the wider stop was read against. Then the family's own reads since
P-15's registration: **D-535's news-safe reading (1)** -- RC150 keeps D-533 (2)'s cut, a conduct fix chosen without a
reading, but its development reading was run before the stop was chosen; **D-538's stop-width screen (8)** -- the carried
cell was selected among its eight cells (the windows are product readings, but each counts); **D-542's diagnostic (1)** --
its reading kept the cell as a candidate. **Alternatives, stated for the gatekeeper:** counting D-536's robustness study's
four reading families as trials gives N = 418; leaving out the diagnostic, 413; leaving out P-15 as a trial, 413. **Not
counted, with reasons:** D-536's robustness study (`rc_robust`: 101 coin seeds, extra costs, delays, years -- readings of
the 25-point cell from which no seed, cost, delay or year is chosen, D-536 (1), D-541; RC150 keeps none of its choices,
D-499 (2)'s rule); T23's fixed-time search (`pool-2026-10-20-t23`) -- RC150 keeps none of its choices (D-530 (3)); the
scoreboard's coin columns (D-528) and the stop distributions (readings); the hypothetical hedge studies D-514/D-515 (in no
pool); the Focused Trader Program's models run beside each configuration (readings under the firm's enforcement scenarios,
D-234, D-499). The carried cell counts twice (in k and in `rc_width_screen`), the conservative side by one. This test has
no held-back period, so the one-sided 0.05/N sentence binds its verdict (D-189, D-230, D-419): **PASS** only if the D-145
gate's campaign grows with each R's outcomes shifted to the bound at 0.05/N, every line of §5 holds, **and all four slice
lines hold**; the same campaign at the one-sided 95 % bound is a **continuation gate**, never a pass. **A fresh seed
changes no count** (D-512). The variant counts are `results/variants.jsonl`'s, by `VariantCounter`: `D-538:rc_width` 8,
`D-538:rc_width_diag` 1, `D-533:rc_nr` 1, `D-536:rc_robust` 4 (not counted, above).

**Known before the run (disclosed).**

1. **The gate's 0.05 arm was effectively read by the screen, and again by the diagnostic.** D-538's screen ran this cell's
   gate campaign -- the same trades, the 0.05 bounds by the era rule, the no-closure table, the budget, the strict rule,
   the capacity -- at seed 20261131 and 500 paths, and D-542 read its growth on the required bankroll at the bound and the
   point (above the 25-point reference's at the same seeds, resolving) and its zero-edge twin
   (`results/rc_width_screen.csv`, sha256 `7b4b65d1130c524874de874ff242dbe3cb74fe3aa456ccd3d9fef2e9758c855d`); D-542's
   diagnostic reproduced that run at the same seed and read the cell with the funded leg capped
   (`results/rc_width_diag.csv`, D-544). **Answered as D-512 answered P-14 and D-529 (2) P-15:** every resampled arm of
   the registered run draws at a fresh campaign seed, **20261206**, used nowhere else; the screen's run stays as a
   **refusing identity** (§3 (c)). The registered 0.05 arm at 20261206 is not independent of the screen's read (500 paths
   resampled from the same days), but it is a new draw no one has seen. **Disclosed:** the build's `--check --paths 4
   --starts 6` smoke ran at 20261206 to test the code -- a first attempt stopped at the ledger lookup after identities (a)
   and (b) (no arm ran), the second ran every arm at 4 paths and the slices and journey on six starts; each printed and
   wrote nothing, and nothing was read from either.
2. **The customer windows** (`rc_s150_asia`, `rc_s150_london`, `rc_s150_us`) were read by the same screen; they are beside
   here, never deciding. `rc_s150_us` failed the every-offered-R-resolves line there.
3. **The funded-risk confound is known and read beside** (D-539 (2), D-544): at the 150-tick stop the fresh XFA's $2,000
   realises $1,500 under the 20-micro allowance against the 25-point cell's $1,000, and about half of the screen's gain
   over the reference was that larger funded risk. The candidate is the table's own sizing (no cap); the cell with the
   funded leg held to the 25-point dollars (`resolved_coin.funded_cap_rule`) is read beside the verdict at the
   registered seed (sections `funded_cap_beside`, `funded_cap_twin`), never deciding.
4. **The slice lines are NOT known.** D-508's slices hold no RC150 row; neither does any journey. The cell's slices at 21,
   63 and 126 sessions and its D-518 journey readings are computed for the first time by the registered run. FV3-C's
   reference slices are D-508's `fv3c` rows (`results/customer_slices.csv`, sha256
   `0009afa7be22a657a065f1939ded0f53088e59e17ca6a338cd74ced0f248bd98`), reproduced by the run and refused otherwise.
5. **The coin has no fitted signal parameter.** Its sides are a fair coin seeded 20261102 per date and mark (D-521, before
   any read; D-541 found this draw among the least favourable of 101 at the 25-point stop -- no other coin seed is ever
   tried); its marks every five minutes from 17:00 CT (D-525); its cutoff a resolution rule on kind columns only; its
   stop chosen from a declared grid of contract arithmetic (12.5 / 25 points in D-525, 37.5 / 50 in D-538), inside the
   cells N counts; everything else is P-14's.
6. **The news-safe cut** (D-533 (2)) removes the 07:30 CT mark on every report day, the release minute P-15's audit found
   the 25-point coin entering (D-533 finding 1); it is part of this cell (the screen applied it) and was read on the
   25-point cell (D-535) before this cell was chosen.

**What is not yet read:** every resampled arm at 20261206 -- the gate at 0.05 and at 0.05/414; the denial ladder, the
placement on, the zero-edge twin, the fixed-legs twin, the gf15b reading, the check period, the Focused Trader Program's
16 models, the campaign without the strict rule, the customer windows, the funded-capped reading and the multi-breach
share under that seed; the fidelity line; the slice lines and the like-for-like slice reading; D-518's journey readings
for this cell; the FLAGs and the scoreboard row.

---

## 1. Question

Does the 37.5-point news-safe coin -- an entry offered every five minutes all session on NQ, its side a seeded fair coin,
at a 150-tick stop, no report-day entry before 07:35 CT, taken when every account is flat, sized as the table sizes it --
grow cash on Topstep's contract at the bound under P-14's design (FV3-C's protocol and table re-solved without closure at
request, at most 20 Combine purchases and resets in any 21 trading days, the operator's strict one-at-a-time rule),
**and** stay at least as consistent as FV3-C for a customer who starts on any day? A **yes** at the binding bound
(0.05/414) with every line and every slice line holding is a pass; the gate's yes with a slice line failing is
**CONTINUE (consistency)** (D-509's rule); a yes only at the 95 % bound a continue; any of these waits for a confirmation
on unread data registered on its own. A **no** at 95 %, or one of §5's lines failing, ends the candidate (P-15's cell
stands). **What a PASS shows, plainly:** on development data already read by the screen that chose this cell, a campaign
with no signal at all grows the bankroll the run itself requires at the 0.05/414 bound on a fresh draw of paths, **with
the firm paying every payout requested** (0 % denial, D-234) and the placement off (D-289). It shows the money is the
contract's shape (D-145, D-452): the coin carries no information; its net edge is minus its costs (its gross is not
exactly zero at every R in this walk -- the settlement convention and the asymmetric bracket in a rising market move it
slightly by R and side, D-533 (3)). It does not show an edge, performance out of sample, that the firm would pay, how much
of any gain over P-15 is the stop's lower cost share rather than the larger funded risk (read beside, §3), or anything a
money decision rests on. **Confounds of the slice comparison, stated:** (i) different windows -- the coin's 2020-01-02 to
2026-07-16, FV3-C's 2021-01-04 to 2025-06-30 (the like-for-like reading over common start days beside); (ii) different
vendors -- Databento for the coin, QuantConnect for FV3-C; (iii) the strict rule on the coin, not on FV3-C -- it counts
**for** the coin (P-15's unstrict arm grew less, D-533 (3)); (iv) the one-tick entry against FV3-C's max(1 tick, the
recorded spread) (for the coin).

## 2. Data period

- **Source** (D-458 (5)): P-15's -- the operator's Databento NQ one-minute bars (GLBX.MDP3 ohlcv-1m) in the local store
  `data/bars/NQ` (git-ignored), read through `config/windows.yaml`'s guard (D-459), walked at every five-minute mark from
  17:00 CT by `atlas_a3.walk_minutes` at the 150-tick stop (`rc_width_screen.build`), A1's 1,691 day records 2020-01-02
  to 2026-07-16; nothing is cached for the coin's walk. **The source's validation** (D-473):
  `docs/data_reports/data_report_bars_NQ_2026-10-30.md`, VALIDATED with P-13's caveats (C1-C8 as P-14's §2), C8 (minute
  bars cannot order a target and a stop touched in one minute, settled as the stop) applying to every offered mark.
- **The slice reference's source**: FV3-C's development campaign as D-508 built it (`customer_slices.fv3c_campaign`).
- **Symbols and resolution**: NQ, MNQ micros and NQ minis for sizing; minute.
- **In-sample**: 2020-01-01 .. 2026-07-16.
- **Out-of-sample**: none here. **Its confirmation needs unread data not yet bought**: ES's declared unread window
  (2025-07-01 .. 2026-09-30, `config/windows.yaml`) needs ES bars (`docs/OPERATOR_SETUP.md` item 1, a payment), or NQ's
  reserve from 2026-07-17 needs the operator's decision (D-107, D-461) and a bar top-up -- **the operator's call**. **Only
  one of P-15's cell (`rc_s100_all_nr`, D-535) and this cell is carried to a single confirmation**, chosen by a rule
  declared in a decision row before that confirmation is registered (D-544); the confirmation is registered on its own
  when that data exists.
- **Walk-forward scheme**: none -- one frozen configuration, chosen once.

## 3. Rules fixed before the run

**Everything of P-15's §3 is carried unchanged except the cell's stop, the news-safe cut and two readings beside** -- the
no-closure table and its pinned hashes, the purchase budget (20, 21), the strict rule at 5 minutes, the campaign
(`atlas_a3.gate_kwargs` through `gate.run_gate`: FV3-C's engine call under `config/fv3_corrected_portfolio.yaml`, five
accounts, one trade an account a session, MAE settlement, the room cap, the 45-tick stand-aside, need-aware Combine exits,
the fee at the contracts held, the Standard path, `aeropay`, the bankroll an output, 500 paths over 504 sessions, the
margin one subscription, the day capacity at the cell's busiest day), the eras, the check period, the deciding bound, the
costs and the fill profile (`assumed`), the fixed-legs twin in P-06's form, the gf15b reading, the Focused Trader Program
beside with its binding summary, the campaign without the strict rule beside, and D-509 (3)'s slice lines verbatim.

- **Entry** (D-521, D-525, D-533): an offer at every five-minute mark from 17:00 CT (`resolved_coin.marks`) that the cutoff
  admits at the 150-tick stop; a report day's marks before the 07:30 CT cut dropped and then every report-day entry
  before 07:35 CT (`resolved_coin.drop_release_minute`); entered at the first bar opening after the mark, one tick adverse
  (an alert sent before the mark -- the mark and the side are known in advance -- the operator's five minutes counted
  from it, D-522 (2), D-533 (3)); its side a fair coin seeded 20261102 per date and mark.
- **The cutoff** (D-525 (4), D-212): a mark is offered only if its unresolved share (flattened at 15:08 without a level,
  both sides pooled) is at most 5 % over the window at every R the table offers (0.25, 1, 1.5, 2, 2.5, 3) --
  `resolved_coin.mark_resolution`, kind columns only; at 150 ticks it admits 193 of 266 marks (`results/rc_width_screen.csv`,
  section `marks`).
- **Re-entry when flat**: every offered mark is a candidate in its day's block; the strict router takes the first
  candidate at least five minutes after the last position's exit (bar end to bar end -- four to five minutes on the wall
  clock, D-533 (3)) and refuses the rest.
- **Stop, exit, bracket, sizing**: the 150-tick stop; the state's R from the table (every quarter R to 3R walked); FV3's
  breakeven, MAE and the 15:10 CT flatten; no time stop; contracts the engine's whole micros at the 150-tick stop (no
  funded cap: the fresh Combine's $2,000 realises $1,950, the fresh XFA's $2,000 realises $1,500, D-539 (2)).
- **The identities, each refusing before a verdict and before anything is written** (in this order):
  (a) P-14's own trades through this engine call reproduce `results/a3_brk30_cb20_gate_paths.csv`'s `gate` run, all 500
  paths, point and bound at 0 %, at seed 20261131 (`rc_screen.identity_problems`);
  (b) the cell's trades are `results/rc_width_screen.csv`'s `rc_s150_all` (sha256 above): the candidate count, the busiest
  day, the day capacity, the long share, the candidates a day and every R's unresolved share equal its row, and the
  trades' content hash equals `17bcc29bc0c61296c872eaf04c3d49942649dcddca782836916bebdf29c9635f`
  (`rc_dev_test.trades_hash`; pinned by D-543's diagnostic, recomputed by this build's smoke);
  (c) the cell at the screen's seed 20261131, 500 paths, reproduces the screen's growth on the required bankroll at the
  bound and the point and its required bankroll (section `screen_identity`, never a gate row), before any registered arm;
  (d) FV3-C's slices equal `results/customer_slices.csv`'s `fv3c` verdict rows (sha256 above), start for start.
- **The slice lines** (D-509 (3), verbatim as P-15's §3): over every start of the window in historical order, the cell's
  bound-shifted arm against FV3-C's development configuration as frozen, at 63 trading days -- (a) `share_positive`
  ≥ FV3-C's, (b) `net_p10` ≥, (c) `share_no_payout` ≤, (d) `needed_bankroll_p95` ≤; 21 and 126 beside; computed as P-15's
  (D-518's journey replay of runs of exactly 21, 63 and 126 sessions; FV3-C's by `customer_slices`' job list). Every slice
  in `results/rc_s150_all_gate_slices.csv`.
- **The gf15b reading rests on unverified rules** (as P-14 and P-15 stated): T24-GF15b's fixed plan closes accounts at
  request, so its beside rows rest on the unverified `xfa_closure_at_request` and `xfa_seat_frees_at`; the no-closure table
  that sizes every deciding arm closes no funded account, so the verdict rests on neither. The inherited payout credit for
  a payout requested before an account ends by a breach applies as at every registration since P-09.
- **Beside, never deciding:** the three other customer windows (section `window_beside`, each window's own trades and
  bounds at seed 20261206); D-518's journey measures on the cell's verdict-arm replay (section `journey`); **the
  funded-capped cell** (sections `funded_cap_beside` -- point and bound at 0 % -- and `funded_cap_twin`, its zero-edge
  twin under the same cap; `resolved_coin.funded_cap_rule`: the funded leg's micro cap scaled by 100/150, floored, the
  Combine's sizing and the table unchanged); **the multi-breach share** (`share_paths_with_same_day_multi_breach` on every
  gate row: the share of paths with a day on which two or more accounts hit the loss limit, from the engine's
  `CampaignPath.same_day_multi_breach_days` -- promised by P-13's and P-14's files and missing from their rows, the
  audits' repeated finding).
- **Parameters, with their exact values**: the card's §4; `scripts/rc150_dev_test.py`'s, `scripts/rc_dev_test.py`'s,
  `scripts/rc_width_screen.py`'s, `scripts/rc_reentry_screen.py`'s, `propedge/research/resolved_coin.py`'s,
  `scripts/a3_brk30_cb20.py`'s and `scripts/atlas_a3.py`'s constants; `config/atlas_a3.yaml`;
  `config/fv3_corrected_portfolio.yaml`; `config/fv3_portfolio.yaml`; k = 1.

**Conduct check in D-145's three tiers:**

- Tier 1, hard:
  - [x] no cross-account hedging -- no two accounts ever hold a position at once (the strict rule); one firm
  - [x] no reliance on simulator fills or fills outside the best bid or offer -- market entries at the first bar after the
    mark, a tick adverse; a 37.5-point stop
  - [x] no maximum size into major news; no coordinated trading -- Topstep's wording (10305426) is "purposefully trading
    your full Maximum Position Size directly into a scheduled major news event"; the firm's release list for NQ (8284211,
    D-170) names the Unemployment Rate at 07:30 CT and the FOMC Statement at 13:00 CT: FOMC days are out of A1's day set
    and no report-day entry is offered before 07:35 CT, so no position is opened into either (D-533 (2)); one position on
    one account at a time. **Stated limit:** other scheduled releases (Census, BEA, DOL claims, ISM) are not excluded --
    a position at the table's full size can be open into one of them (D-530 (1))
  - [x] nothing designed to conceal a pattern from the firm or evade its detection -- the coin hides nothing; the budget
    restrains a pattern the firm names, chosen on growth and the program's readings, not on a detection level
- Tier 2, modelled: P-14's -- the fresh XFA's $2,000 realised at $1,500 on the 150-tick stop; the Combine's menu reaching
  R 0.25; several accounts at the MLL in one day measured (the multi-breach share); the placement off in the base case, on
  beside.
- Tier 3, priced: P-14's -- the gate at 0 % denial; 10, 25 and 50 % and the break-even denial beside; payouts exposed,
  Combine purchases (at most 20 in any 21 days under the budget); the Focused Trader Program's 16 models beside.

**The run** (D-474, as P-15): once, from a clean detached checkout of the commit that registers this file -- first
`python scripts/run_clean.py --name rc150-stops -- python scripts/rc150_dev_test.py --stop-distribution` and `--collect`
(the card's stop distribution, a reading of the trades, committed before registration), then
`python scripts/run_clean.py --name rc150-dev -- python scripts/rc150_dev_test.py --prereg P-16 --workers 4`, then
`python scripts/run_clean.py --name rc150-dev --collect`; the ignored stores `data/bars` and `data/atlas` linked in as
junctions; one BLAS thread; `--workers` the memory guard's grant (bit for bit the rows of one process, R11). Written:
`results/rc_s150_all_gate.csv`, `results/rc_s150_all_gate_paths.csv`, `results/rc_s150_all_gate_slices.csv`, each with
its manifest (not exploratory, `prereg_id` this id).

## 4. Metrics

P-15's §4 exactly, with this cell's trades: growth on the required bankroll at 0 % denial with the placement off at each
R's bound at 0.05/N (the verdict's) and at 0.05 (the continuation gate's); the four slice lines at 63 days with 21 and 126
beside; the lines of `docs/SUCCESS_CRITERIA.md` §3 (each offered R's unresolved share overall and in its worst year at
most 5 %, `a3_brk30.resolution_rows`; realised over intended capped risk at least 0.9); beside, never the verdict: the
denial ladder, the break-even denial, the program's summaries, the strict rule's cost, the placement on, the zero-edge
twin, the fixed-legs twin and the gf15b reading, the point arm, the customer windows, **the funded-capped cell and its
twin**, **the multi-breach share**, each R's e and bounds at 0.05, 0.05/k and 0.05/N with its sd against `assumed_sd` and
propsim D-47's criterion, the deflated Sharpe at N, the tier-3 and budget counts, the drift decomposition, the period rows,
D-518's journey measures, and the trades' content hash. FLAG levels as P-14 (the scoreboard after the run).

## 5. Pass / fail criteria

All at 0 % denial with the placement off, each R's bound as the era rule reads it (`t23_d20.verdict_of`, with the lines),
then D-509 (3)'s rule (`a3_brk30_cb20.verdict_word`). **The 0.05/N sentence** (`docs/SUCCESS_CRITERIA.md` §2, D-189, D-230,
D-419): a development verdict is read at `e`'s one-sided bound at 0.05/N, N = 414. Neither PASS nor CONTINUE meets the
D-145 gate, satisfies exit (A) or supports a money decision.

- **Refused before a verdict** (the failure protocol's diagnosis, never a rerun until it passes): any of §3's four
  identities failing, or a pinned file not the one fixed here.
- **Pass**: growth above zero on the arm at e's bound at 0.05/N (and so at 0.05); every line holding; **and all four slice
  lines holding**.
- **Continue (consistency)** -- not a pass: the gate's PASS with one or more slice lines failed, recorded as such (D-509 (3)).
- **Continue (not a pass)**: above zero at the 0.05 bound only, every line holding -- one confirmation on unread data
  decides it. The slice lines are read beside it, never changing it.
- **What PASS adds over CONTINUE** (D-419): both wait for one confirmation on unread data, and a PASS gets no levers; a
  PASS clears the multiplicity bar of everything this pool tried (0.05/414) and so carries the stronger development
  record into the queue behind FV3-C's shadow period, where a CONTINUE carries only the unadjusted 95 % reading.
- **Fail**: not above zero at the 0.05 bound, or one of the lines failing.
- **Beat FV3-C's row or stop** (D-365, D-382, D-452): the gate row's growth at the 0.05 bound against
  `results/scoreboard.csv`'s `FV3-C-dev`; not beating it, RC150 is not pursued past its verdict. Beside: P-15's row (the
  25-point coin) and the scoreboard's coin baseline -- whether the wider stop adds anything, read, never a line.
- **The confirmation window** (named, not registered here): ES's declared window or NQ's reserve, once bought and opened by
  the operator; the Combine's headroom over its target is checked against that window's bound before registering it
  (D-451); only one of P-15's cell and this cell goes to it, by a rule declared before it is registered.
- **What a fail means**: RC150 ends, kept on record and diagnosed by the failure protocol, never rerun until it passes;
  P-15's cell stands as family RC's confirmation candidate (D-535).

## 6. Seed

- **Seed**: **20261206** -- the campaign's resampling on every registered arm, twin, section and customer window, and on the
  funded-capped reading; fresh, used by no other script or module (a test checks it), to be fixed by the decision row that
  sends this draft to the gatekeeper, so it chooses nothing. The build's smoke runs at it (§"Known before the run" (1))
  printed and wrote nothing; nothing was read from them.
- **Identity seed**: 20261131 (the screen's, the diagnostic's and P-14's) -- used only by identities (a) and (c), run
  before every registered arm.
- **The coin's seed**: 20261102 (D-521) -- the sides; drawn once over the whole grid of dates and marks.
- **Additional seed**: 20261017 -- the eras' whole-year bootstrap and `haircut.widened`'s day bootstrap. The slices and
  the journey draw nothing (historical order).

## 7. Variants

- Configurations already tried for this question: the ledger's pool, N = 414 with this registration (above): P-15's pool
  (402), P-15 (1), D-535's news-safe reading (`D-533:rc_nr` 1), D-538's 8 width cells (`D-538:rc_width`), D-542's
  diagnostic (`D-538:rc_width_diag` 1).
- Configurations this pre-registration will try: 1 (`rc_s150_all`, news-safe). Beside it, never a verdict: the Focused
  Trader Program's 16 declared models on its campaign, recorded as exploratory variants under `D-544:rc_s150_all_ftp`;
  the campaign without the strict rule, the customer windows and the funded-capped cell (readings, no variant); the
  identities.

## 8. Anything chosen after seeing results

*(Left empty at registration.)*

---

## Outcome

- **Date run**: 2026-11-03, once, by `python scripts/run_clean.py --name rc150-dev -- python scripts/rc150_dev_test.py
  --prereg P-16 --workers 4` from a clean detached checkout of b7e6077 (D-546's commit, D-474).
- **Result file(s)**: `results/rc_s150_all_gate.csv` (sha256 `dfd29188f364`), its per-path file and its slices file, each
  with its manifest (`exploratory: false`, `prereg_id` P-16, campaign seed 20261206); the four identities held first
  (P-14's per-path record, the screen's trades and their hash, the screen's growth at 20261131, FV3-C's slices).
- **Verdict**: **PASS** on development data -- the gate grows on the required bankroll at the bound at 0.05/414
  (1.439748604835227) and at 0.05 (1.50042325831915), every offered R resolving, realised risk at the line; all four
  of D-509's slice lines hold against FV3-C (section `slice_lines`). The audit follows (D-547).
- **Beside, never deciding** (the file's rows): the funded-capped reading (`funded_cap_beside`) also grows, less, at a
  lower required bankroll -- the funded-risk confound named in §1; the zero-edge twin grows above the traded arm; 10 %
  denial still grows, 25 % less, 50 % barely; the placement on does not grow; every path has a day with several
  accounts at the loss limit (`share_paths_with_same_day_multi_breach`), the pattern tier 2 names -- the reason the
  placement on fails; nearly every payout exposed to tier 3; the check years and the three other windows grow.
