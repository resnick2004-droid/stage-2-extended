# DRAFT — P-16's single confirmation: the 37.5-point news-safe coin on NQ's unread forward data (not registered)

> **Status: DRAFT, not registered.** Written 2026-11-09, before any NQ bar after 2026-07-16 has been bought, imported or
> read, and before the confirmation script exists. It is handed to the **prereg-gatekeeper** only after (i) the
> operator's NQ data exists (`docs/OPERATOR_SETUP.md` item 6) and its zip's sha256 is recorded in a decision row that
> also records the operator's D-107 decision to open NQ's fourth confirmation; (ii) the open items of §9 are closed;
> (iii) the checks of §5a are computed on development data and quoted here from their result file; (iv) the script of
> §3a is built, tested and committed. Until then nothing here runs, nothing reads the reserve, and no count changes.
> Written in P-10's and P-06's form with every field of `prereg/TEMPLATE.md`; the criteria are read from their single
> source, `docs/SUCCESS_CRITERIA.md` (D-457). The candidate is the one D-546 (3)'s rule carried (D-547 (4)): P-16's cell
> `rc_s150_all_nr`, never P-15's, never a variant. **ES is not this test** (§2, last item).

| field | value |
|---|---|
| **id** | P-XX *(assigned by the prereg-gatekeeper at registration -- leave as P-XX)* |
| **date** | 2026-11-09 (draft) |
| **author** | stage-two session, for the operator (Ryan Resnick) |
| **task** | D-546 (3) / D-547 (4) / D-548: the single confirmation of the coin carried from family RC; D-604's design point on the resolution line; T5 (the stage's pre-registered out-of-sample test) |
| **protocol step** | 8 of `docs/RESEARCH_PROTOCOL.md` (D-155): the verdict's one confirmation, after P-16's development PASS (D-547) and its audit (D-548) |
| **status** | draft |

## Machine-checked fields

| key | value |
|---|---|
| `k` | 1 |
| `development_period` | 2020-01-01 .. 2026-07-16 (P-16's; NQ's development and folded held-back windows of `config/windows.yaml`, D-461) |
| `confirmation_period` | 2026-07-17 .. END -- NQ's reserve, opened as a confirmation window by the decision row that registers this file; END is the last full trading day the operator's purchase covers, fixed in that row from the purchase's date range before any bar is imported or read; the window must supply at least 126 walked sessions (131 full sessions on the exchange calendar, FOMC days and published early closes out, a margin of five) or registration waits (§2) |
| `confirmation_tests_on_this_market` | 3 (P-05, P-06, P-10 -- `prereg/REGISTRY.md`); this would be NQ's **fourth**, which D-107 gives to the operator: the decision row recording item 6's purchase records that decision (item 6: "this request is that decision plus the purchase") |
| `bonferroni_alpha` | not required: a held-out confirmation period is used |
| `assumed_sd` | 1.5427 (P-16's planning input at 3R, D-529 (4)'s form; P-16's machine-checked field) |
| `assumed_sd_source` | planning input, not a result, carried from P-16: the sample sd (ddof 1) of `r_3` over the cell's development candidates (`rc_dev_test.planning_sd`); it decides nothing; the window's realised sd by R is reported beside (§4) |
| `risk_denominator` | intended -- the table's dollar risk at the 150-tick stop in whole micros, the allowance and the Combine's room cap applied (P-16's) |
| `primary_metric` | growth on the required bankroll -- `pf_growth_on_base_p50` on `pf_required_p90` (D-312, D-457); never `median_log_growth`, the notional column (D-451 F4) |
| `data_period` | 2026-07-17 .. END (the window's bars, read once under this id). Development files read, none recomputed: P-16's frozen marks (`results/rc_width_screen.csv`, section `marks`, sha256 `7b4b65d1130c524874de874ff242dbe3cb74fe3aa456ccd3d9fef2e9758c855d`), the no-closure table P-16 loaded (`a3_brk30_cb20.noclose_plan`, its pins), FV3-C's reference slices (`results/customer_slices.csv`, sha256 `0009afa7be22a657a065f1939ded0f53088e59e17ca6a338cd74ced0f248bd98`); the development bars 2020-01-01 .. 2026-07-16 only by the identities of §3 (development purpose) |
| `seed` | 20261227 (the campaign's resampling on every arm read on the window -- fresh: a search of every file in the repository and the main checkout, 2026-11-09, found it nowhere; to be fixed by the decision row that registers this file, so it chooses nothing); 20261102 (the coin, part of the protocol, D-521); 20261017 (the bootstraps beside, §6); 20261131 (identities on development data only, §3) |
| `model_card` | docs/candidates/cards/RC150.md |
| `power_rr` | 1.5 (the fresh Combine's R in the table) |
| `power_effect` | 0.00 (the card's `edge_assumed`: a coin carries no information) |
| `boot_len` | 21 (the bound's block: 21 sessions, P-06's rule, D-237 (4)) |
| `required_trades_source` | assumed_sd fallback: the L5 curve gives the trades needed to find a planted positive edge, and a coin has none by construction -- the money, if any, is the contract's shape, and the campaign decides at the bound |
| `required_trades` | not an edge search: the gate reads the campaign at each R's bound over the window's 21-session blocks -- at least six at the 126-session minimum, against about eighty in development (P-16's 1,691 walked sessions) |
| `available_trades` | about 140 offered candidates a session (P-16's 239,768 over its 1,691 day records) times the window's walked sessions -- an estimate before the read that decides nothing; the campaign takes at most one an account a session |
| `ledger_n` | `propedge.research.ledger.count_n` on `prereg/models.yaml` for RC150 at the registering commit, pool `pool-2026-11-03-rc150`, NQ, minute, 2020-01-01 .. 2026-07-16 -- 414 at P-16's registration (D-546 (1)); the gatekeeper recounts, ruling on the exploratory readings since (D-551, D-583, D-593, D-594, D-599, D-602: each "selects nothing", D-499 (2)'s rule); N reaches only the bound at 0.05/N beside the verdict |

**Multiplicity plan.** RC150 was chosen on development data only, from N trials (`ledger_n`), and passed its development
test at 0.05/414 (P-16, D-547); D-546 (3) declared, before P-16 drew anything, which of the two coin cells goes to the
single confirmation, and D-547 (4) applied it. The window is read here once, for one configuration frozen in advance;
the decision is this single test at the registered one-sided 0.05 with no selection on it (the 0.05/N sentence,
`docs/SUCCESS_CRITERIA.md` §2; D-230, D-419). Each R's bound at 0.05/N and the deflated Sharpe at N are reported beside,
never as the verdict. The family-wise control across confirmations is D-107's count: this is NQ's fourth test, opened by
the operator's decision, reported with the verdict. **The window is unread:** `config/windows.yaml` holds NQ from
2026-07-17 as `reserved`, read by nothing (D-461); the bar store never stores a reserved day (`propedge/data/bars.py`);
no step of P-16, its screens or its robustness studies read a session after 2026-07-16 (each through the guard; e.g.
D-600 (7)). P-15's cell is never tested on this window.

**Power, stated before the read.** At the 126-session minimum the bound reads six 21-session blocks against
development's eighty, so it is wide (P-10's lesson: the block count, not the trade count, sets it -- D-451 (2)). D-604
found every development window of three to twelve months growing at the bound (`results/p16_confirm_feasibility.csv`) --
optimistic by construction (the cell was chosen on those days, and each window there re-read its own mark cutoff, which
this registration does not, §3). A FAIL may reflect the bound's width or the frozen marks' resolution rather than a
changed market; the consequence stays as registered.

**Known before the run (disclosed).**

1. **P-16's development record:** PASS at 0.05/414 with all four slice lines (D-547); the audit confirms with caveats
   (D-548): the PASS exists only with the placement off (every path has a day with several accounts at the loss limit;
   the placement on does not grow); a breach-count knife-edge at the fresh Combine from the shift convention; positions
   open across non-listed releases and report-day entries at 07:35 CT, where one-tick fills are optimistic; no edge (the
   zero-edge twin above the traded arm; propsim D-47 not met); about half the gain over P-15 is the larger funded risk.
2. **Robustness, all exploratory, all on development data:** fills (D-585: growth at the bound survives every declared
   slippage level), the stop on years it was not chosen on (D-554), the stop's neighbours (D-598), late entries, single
   years and fifty other coin sequences (D-605: P-16's own coin in their lower fifth), added Lucid seats (D-601: none
   help). None reads the window; none changes the cell.
3. **D-604's feasibility reading** (`results/p16_confirm_feasibility.csv`): every development window of three to twelve
   months grows at the bound; every failure there is the resolution line read on a stub calendar year. It is the reason
   for §2's minimum and §5's year rule -- a design taken from development data, before any window read. It is
   optimistic twice over: the windows are the history the cell was chosen on, and each re-cut its own marks.
4. **§5a's checks** -- to be computed before registration and quoted here; not yet run.
5. **The window:** no bar of NQ after 2026-07-16 has been bought, imported or read by any step of the project (the
   store never holds a reserved day; the Studio's and the terminal's replays stop at 2026-07-16). Public market prices
   after that date exist and the authors may have seen headlines; the coin takes no input from prices, and nothing in
   this file was chosen from any look at them.
6. **NQ's fourth confirmation** (D-107): P-05, P-06 and P-10 read the held-back year, now development (D-461); this test
   reads none of their data.

---

## 1. Question

Does P-16's frozen campaign -- the 37.5-point news-safe coin (`rc_s150_all_nr`) re-entering when flat, sized by the
no-closure table under P-14's design, five Topstep seats, the strict one-at-a-time rule -- grow cash on the bankroll it
requires, at each R's one-sided 95 % bound, on NQ sessions after 2026-07-16 that no step has read, under
`docs/SUCCESS_CRITERIA.md` §3's confirmation lines and D-509's consistency lines against FV3-C? A **PASS** meets the
D-145 gate out of sample for this campaign (exit (A)'s campaign line; the protocol comparison, sizing report and rules
ledger are still owed) and queues behind FV3-C's shadow period with no levers (D-419, D-337). A **FAIL** ends P-16 on NQ,
kept on record and diagnosed, never rerun. Either answer is informative: the coin carries no signal, so a PASS says the
contract's shape alone grows cash out of sample at the bound; a FAIL says P-16's development growth did not survive
unread data.

## 2. Data period

- **Source:** the operator's Databento NQ one-minute bars (GLBX.MDP3 ohlcv-1m, `parent` symbology, `NQ.FUT`), the
  purchase of `docs/OPERATOR_SETUP.md` item 6, its zip's sha256 recorded in a decision row; imported into `data/bars/NQ`
  (git-ignored) by the store's importer only after registration, then read through `propedge/data/windows.py`'s guard
  under purpose `confirmation` and this registration's id (`registered_reads`). The same vendor and schema as
  development (D-458), so no vendor confound.
- **Symbols and resolution:** NQ, MNQ micros and NQ minis for sizing; minute. The charted contract per trading day by the
  store's rule (the outright with the most volume on the previous trading day, D-98).
- **In-sample:** 2020-01-01 .. 2026-07-16, read only by §3's identities, under the development purpose.
- **Out-of-sample:** 2026-07-17 .. END, read once. Trading days are Chicago time (a session opens at 17:00 CT the evening
  before), so the first session opens 17:00 CT on 2026-07-16. **END** is the last full trading day the purchase covers,
  fixed by the registering decision row from the purchase's date range alone (no bar read). **The minimum (D-604):** the
  window must supply at least **126** walked sessions -- six 21-session blocks, six months. Because the walk's own day
  kinds come from the bars (an abbreviated session reads as an early close), END is fixed so that the CME holiday
  calendar, the FOMC calendar and the exchange's published early and abbreviated closes give at least **131** full
  sessions (a margin of five), counted in the decision row, not from the bars. Below that, registration waits for a
  later purchase; it is never registered short. Longer is better ("as long as the data allows",
  `docs/SUCCESS_CRITERIA.md` §3): END is not capped. On the calendar, 126 sessions from 2026-07-17 end around late
  January 2027 (`docs/OPERATOR_SETUP.md` item 6's timing note says mid-January; the decision row computes the date).
- **Counted periods (C2):** the window's **calendar quarters**, the first being 2026-07-17 .. 2026-09-30; a quarter is
  counted when it holds at least 40 walked sessions (`docs/SUCCESS_CRITERIA.md` C2's minimum); an uncounted quarter's
  trades stay in C1's pool and its figures are reported beside. At least two counted periods, else FAIL. **Why
  quarters, not P-06's and P-10's half-years:** at the 126-session minimum the window ends in early 2027, so a second
  half-year could not be counted and the test would fail by construction; the first quarter (from 2026-07-17) and
  2026 Q4 each clear 40 sessions on the calendar, and a quarter is the slice line's 63-session horizon.
- **Walk-forward scheme:** none -- one frozen configuration; nothing is estimated from the window except each R's mean
  and bound, which the gate's definition requires.
- **The usability test (one test, one consequence, fixed now; P-06's and P-10's form):** after registration and before
  the verdict script parses anything, the data-integrity agent validates the imported window structurally (schema,
  gaps, duplicates, timezone, session boundaries -- no price summary) and the walk's day kinds are counted; the window is
  **unusable** if the report is not VALIDATED, if the store holds fewer than 126 walked sessions (`day_kind` `n` or `b`)
  in it, or if any exchange trading day inside the window is missing from the store. The judgement (the report's
  verdict and the count) is committed in a decision row before the verdict runs. Unusable: one corrected import
  (mechanics only, the same purchase or a re-download of the same range, recorded in a decision before it runs) may
  follow; a second unusable import is a FAIL.
- **ES is a separate, later test, not this one:** ES's declared window (2025-07-01 .. 2026-09-30) needs ES bars
  (item 1) and its own registration, with a rule translating the 150-tick NQ stop to ES declared before any ES bar is
  read, and its own headroom and resolution checks. It is neither a substitute for this test nor a rescue after it.

> The test period is fixed at registration and not revisited. Extending it after seeing a result, or sliding it to a
> friendlier regime, converts an out-of-sample test into an in-sample one.

## 3. Rules fixed before the run

**Everything of P-16's §3 is carried unchanged except what a forward window forces, listed below** -- the coin
(seed 20261102 per date and mark, every five-minute mark from 17:00 CT, entered at the first bar opening after the mark
one tick adverse), the 150-tick stop, every quarter R to 3R walked, FV3's breakeven, MAE settlement and the 15:10 CT
flatten, no time stop, the news-safe cut (a report day's marks before 07:30 CT dropped, then every report-day entry before
07:35 CT, D-533 (2)), FOMC days out, the strict one-at-a-time rule at 5 minutes, the no-closure table and its pins, the
purchase budget (20 in any 21 trading days), the campaign (`atlas_a3.gate_kwargs` through `gate.run_gate`: FV3-C's engine
call under `config/fv3_corrected_portfolio.yaml`, five accounts, one trade an account a session, the room cap, the
45-tick stand-aside, need-aware Combine exits, the fee at the contracts held, the Standard path, `aeropay`, the bankroll
an output, 500 paths over 504 sessions resampled from the window's 21-session blocks, the margin one subscription), the
costs and the fill profile (`config/fills.yaml`, `assumed`, D-95), sizing in whole micros with no funded cap, the
table's R by state (the table is fixed -- no cell is chosen from the window's bound). Contracts and costs as P-16's §3.

**What changes, and why:**

1. **The marks are frozen, never re-cut on the window.** The offered marks are P-16's: the 150-tick rows of
   `results/rc_width_screen.csv`'s `marks` section (193 of 266 marks, P-16 §3), the file pinned by sha256 above, the mark
   list pinned by its own hash in the script. D-525 (4)'s cutoff is a choice made from development outcomes' kind
   columns; re-reading it on the window would select marks on the test data and would make the window-wide resolution
   line hold by construction. (D-599's feasibility study re-cut per window; this registration does not -- a stated
   difference, §5a item 2.)
2. **The bound is the window's own, pooled:** each R's one-sided 95 % bound of `e` over the window's 21-session blocks
   (`a3_brk30.check_bounds`, the function D-551, D-599 and D-602 used; the last partial block as `confirm_fv3.block_of`
   forms it). No era test: the window lies in one regime span (D-600's correction), and P-16's `ERAS` end in 2026. The
   bound at 0.05/N by `confirm_fv3.edge_stats` with N, beside.
3. **The day set** is the window's walked sessions (`day_kind` `n` normal, `b` BLS 08:30 ET report day), early closes,
   missing days and FOMC days out by `atlas_walk._kind`'s rule, with the FOMC and BLS calendars extended through END from
   the official pages (§9 item 3).
4. **The day capacity** is the window's busiest day of candidates (`a3_brk30.capacity`, D-469) -- an array size, not a
   choice.
5. **Arms not carried** (product or diagnostic readings that the window can give later as exploratory reads of a spent
   window): the T24-GF15b reading (rests on unverified closure rules), the campaign without the strict rule, the three
   other customer windows, the check period.

**The identities, each refusing before the window is read and before anything is written** (in this order):
(a) the confirmation build run on the development days (purpose `development`) with the frozen marks gives P-16's cell
exactly: its candidate count and content hash `17bcc29bc0c61296c872eaf04c3d49942649dcddca782836916bebdf29c9635f`
(`rc150_dev_test.TRADES_SHA256`) -- so the window's walk, coin, costs and news cut are P-16's code; (b) those trades at
seed 20261131, 500 paths, with the era-rule bound P-16's screen used, reproduce `results/rc_width_screen.csv`'s
`rc_s150_all` growth at the bound and the point and its required bankroll (P-16's identity (c)) -- so the engine call
is P-16's; (c) FV3-C's slices equal `results/customer_slices.csv`'s `fv3c` verdict rows, start for start (P-16's (d));
(d) the pins: `prereg/REGISTRY.md`'s P-16 row is `complete` with a PASS, `results/rc_s150_all_gate.csv`'s sha256 is
the registered file's, the no-closure table's and the configs' hashes are P-16's, and the frozen marks are the cutoff
table's admitted 150-tick marks. Only then is the window read, under this id.

**Conduct check in D-145's three tiers** (P-16's, unchanged):

- Tier 1, hard:
  - [x] no cross-account hedging -- no two accounts ever hold a position at once (the strict rule); one firm
  - [x] no reliance on simulator fills or fills outside the best bid or offer -- market entries at the first bar after
    the mark, a tick adverse; a 37.5-point stop
  - [x] no maximum size into major news; no coordinated trading -- FOMC days out; no report-day entry before 07:35 CT,
    so no position is opened into the firm's listed NQ releases (8284211, 10305426; D-533 (2)); one position on one
    account at a time. **Stated limit (D-546 (2), D-548 (3)):** other scheduled releases (Census, BEA, DOL claims, ISM,
    10:00 ET) are not excluded; a position at the table's full size can be open into one -- read beside (§4)
  - [x] nothing designed to conceal a pattern from the firm or evade its detection
- Tier 2, modelled: the placement off in the base case (D-289), on beside; several accounts at the MLL in one day
  measured (`share_paths_with_same_day_multi_breach`; on development every path had such a day, D-548 (1)).
- Tier 3, priced: the gate at 0 % denial (D-234); 10, 25 and 50 % and the break-even denial beside; Combine purchases
  under the budget; the Focused Trader Program's 16 declared models beside (D-497, D-499).

**Rules:** the firm's rules as P-16 ran them (`config/rules.yaml`, `RULES_LEDGER.md`, each verified with article id and
date). The rules-verifier re-checks every rule the campaign uses within seven days before registration; a rule changed
since P-16 is recorded beside the verdict and does not change the frozen campaign (the test is of the campaign P-16
registered, on unread prices).

### 3a. The script (to be built -- P-16's script cannot run this test as it stands)

`scripts/rc150_dev_test.py` at P-16's registered commit (b7e6077) is the frozen *specification* of the cell and the engine
call, but it is a development test: its walk reads bars only under purpose `development` (`atlas_a3.bar_arrays`), its
day set is A1's development cache (`a3_resolution_map.load_a1`), its cutoff is recomputed from the walk
(`rc_width_screen.build`), its bounds are the era rule on fixed eras, its window and check period are constants, and its
verdict word is the development word (`t23_d20.verdict_of`, `a3_brk30_cb20.verdict_word`). The route is **a confirmation
script, `scripts/rc150_confirm.py`** (pure parts in `propedge/research/rc150_confirm.py`, tests in
`tests/test_rc150_confirm.py`), built, tested and committed before registration and frozen at the registering commit,
that **reuses P-16's code for everything P-16 fixed** (`rc_dev_test.Spec` and its runner's engine call, `trades_hash`,
`multi_breach_share`, `journey_and_slices`, `fv3c_slices`, `resolved_coin.cell_trades` / `drop_release_minute` /
`coin_table`, `rc_screen.walked_minutes`, `atlas_a3.walk_minutes`, the no-closure plan) and adds only what §3's changes
and §5's lines need. §9 lists the pieces. Run once, from a clean detached checkout of the registering commit
(`scripts/run_clean.py`, D-474), `data/bars` linked in, one BLAS thread:
`python scripts/run_clean.py --name rc150-confirm -- python scripts/rc150_confirm.py --prereg P-XX --workers 4`, then
`--collect`. Writes `results/rc150_confirmation.csv`, `_paths.csv` and `_slices.csv`, each with its manifest (not
exploratory, `prereg_id` this id, seed 20261227, `variant_count` 1).

## 4. Metrics

- **Primary:** growth on the required bankroll (`pf_growth_on_base_p50` on `pf_required_p90`) on the gate row -- section
  `gate`, `shift` = `lower_bound`, `enforcement_p` = 0, placement off -- each R's outcomes shifted to the window's
  one-sided 95 % bound over 21-session blocks, fees and payout latency applied, the Standard path.
- **The lines' inputs:** C2 -- each counted quarter's own campaign at the point (its trades and blocks only, resampled
  within it, P-10's construction): growth on its required bankroll, the activity bound (`pf_activity_bound_p50`, the
  one-sided Wilson bound of the share of days with a trade, D-305), the share of paths whose Sharpe changes sign without
  their idle blocks (`pf_share_sharpe_sign_changed_without_idle`), its trades. C4 -- each offered R's unresolved share
  (the 15:10 flatten; a breakeven exit resolved) on the cell's offered candidates (`a3_brk30.resolution_rows`' reading,
  P-16's) over the whole window and in each calendar year by §5's year rule; `realised_to_intended_capped_risk` on the
  gate row. C5 -- D-509 (3)'s four slice measures at 63 sessions against FV3-C (below).
- **Beside, never the verdict** (`docs/SUCCESS_CRITERIA.md` §4, from the same file): the point arm; 10, 25 and 50 %
  denial at the bound and the break-even denial (`pf_break_even_denial_p50`); the placement on; the zero-edge twin; the
  fixed-legs twin in P-06's form; each R's `e`, bound at 0.05 and at 0.05/N, gross, cost and net, its realised sd
  against `assumed_sd`, and propsim D-47's criterion (e ≥ 0.10 net, bound ≥ 0.05); the deflated Sharpe of the block
  means at N (`propedge.research.haircut`) and `haircut.widened`'s bounds; the Focused Trader Program's 16 models with
  the binding summary; the funded-capped cell and its zero-edge twin (P-16's `funded_cap_beside`, `funded_cap_twin`,
  D-544); the multi-breach share on every gate row; the tier-3 pattern measures (Combine purchases per path and the most
  in any 21 days, payouts exposed); D-518's journey measures on the verdict arm; the slices at 21 and 126 sessions; each
  R's unresolved share in every calendar year and every quarter, counted or not; the required bankroll at p50 / p90 / p99
  / worst, drawdown, days to the first payout, payouts a month, red months, days underwater, with §5's FLAG levels from
  P-06 (`results/success_thresholds.csv`; the same horizon, path count and firm, so the levels apply, D-475); the
  scoreboard row against P-06's (§5); the variant count.
- **The release-minute cost reading (beside, never deciding; promised by D-548 (3)):** every offered candidate entering
  at the 07:30 CT mark on a non-report day, at 07:35 CT on a report day or at the 09:00 CT mark (10:00 ET), or open
  across 07:30 CT or 09:00 CT on any day, recosted with 2 and with 5 extra ticks on its entry and on a stop or breakeven
  exit (D-583's family B form, `resolved_coin.add_cost_ticks`'s convention, on those candidates only; targets stay limit
  fills); the campaign rerun at the bound at seed 20261227; two readings, levels fixed now.
- **Bound and block counts:** the window's 21-session block count beside development's (about eighty), as
  `docs/SUCCESS_CRITERIA.md` §3 requires.

## 5. Pass / fail criteria

**PASS requires all four lines** -- `docs/SUCCESS_CRITERIA.md` §3's three confirmation lines (C1, C2, C4; C3 is not a
line, D-457) and D-509 (3)'s consistency lines, which P-16's development verdict carried and D-509 (4) says are re-checked
on the confirmation:

- **C1 -- the gate:** the gate row's growth on the required bankroll above zero, each R at the window's one-sided 0.05
  bound, 0 % denial, the placement off, fees and latency applied, the Standard path.
- **C2 -- every counted period:** each counted quarter's own campaign at the point grows on its required bankroll, its
  activity bound is above one half, and no path's Sharpe changes sign without its idle blocks; at least two counted
  quarters.
- **C4 -- fidelity:** realised risk at least 0.9 of the allowance-capped intention on the gate row; no counted quarter
  without a gate trade; and **D-212's resolution line by the year rule below**.
- **C5 -- consistency (D-509 (3), verbatim as P-16):** over every start of the window in historical order, the cell's
  bound-shifted arm against FV3-C's development configuration as frozen, at 63 trading days -- (a) `share_positive`
  ≥ FV3-C's, (b) `net_p10` ≥, (c) `share_no_payout` ≤, (d) `needed_bankroll_p95` ≤ -- FV3-C's from
  `results/customer_slices.csv`'s `fv3c` rows (identity (c)). **Confound, stated:** FV3-C's reference is its development
  window (QuantConnect, 2021-2025), the coin's is this window; there is no FV3-C record of this window, and building one
  would read it for a second model.

**The resolution line's year rule (D-604's design point, fixed now).** D-212's line ("at most 5 % of each leg's trades
reach the firm's flatten, overall and in every year") is read, at every offered R (0.25, 1, 1.5, 2, 2.5, 3), on the
cell's offered candidates:

1. **over the whole window** -- at most 5 % unresolved; and
2. **in each calendar year that holds at least 63 of the window's walked sessions** -- at most 5 %.
3. A calendar year holding fewer than 63 walked sessions is **not read on its own**: its candidates count in (1), and its
   share is reported beside, never deciding.

*Why this rule:* D-604 found every development failure was this line read on a window's worst calendar year when that
year was a stub of a few weeks at the window's start (windows from 2020-12-22 and 2023-11-23); a window from 2026-07-17
past the new year carries exactly such a stub (early 2027), and its holiday-thinned first weeks would decide the test
on a handful of sessions. Sessions, not candidates, are the independent unit (D-11): a stub's many candidates share a
few days' volatility. 63 sessions is three of the bound's 21-session blocks, the slice line's horizon and a quarter of a
year -- enough that a year's line reads a season rather than a holiday fortnight -- and it is not tuned to D-604's stubs
(any minimum from about a month up excludes them). The whole-window line keeps every candidate in a reading, so no
session escapes the line. With END before about early April 2027, the line reads the whole window and 2026; later, 2027
too. *Alternatives considered:* whole years only (would never read 2026 or 2027 on their own here, too weak); counted
quarters (40 sessions, would add Thanksgiving-and-Christmas Q4 as its own line -- stricter than D-212 asks, reported
beside instead); the whole window only (drops D-212's "in every year" outright). **This rule is a reading of D-212 for
windows with a stub year; the decision row that registers this file records it** (`docs/SUCCESS_CRITERIA.md` §3 says
"overall and in every year" and defines no stub; the gatekeeper rules whether it needs its own D-row first).

**Verdict words.** **PASS:** C1, C2, C4 and C5 all met. **CONFIRMED ON THE GATE ONLY** (not a PASS, D-509 (3)'s
consistency word): C1, C2 and C4 met, C5 failed -- the D-145 gate is met out of sample by `docs/SUCCESS_CRITERIA.md`'s
lines, the consistency claim against FV3-C is not; recorded as such, the window spent. **FAIL:** C1, C2 or C4 not met,
a result that cannot be computed, a second unusable import, or fewer than two counted quarters.

**Beat P-06's row or stop** (`docs/SUCCESS_CRITERIA.md` §6, D-365, D-382, D-452): the gate row's growth on the required
bankroll against `results/scoreboard.csv`'s P-06 row (FV3-C's confirmation, the row of the same kind, D-455 (2)); not
beating it, P-16 is not pursued past its verdict whatever the verdict says. Different windows, stated beside.

**What a PASS means:** the D-145 gate met out of sample for this campaign, with the money the contract's shape (a coin);
it queues behind FV3-C's shadow period with no levers (D-419); before any real money, the pre-deployment protocol (a
shadow period with its own registration, D-337), with D-548's caveats carried: tier 2's placement (the PASS exists only
under D-289's base case), tier 3's exposure, the release-minute fills. No money decision rests on it alone.

**What a FAIL means:** P-16 ends on NQ, kept on record and diagnosed by the failure protocol, never rerun; family RC's
NQ route closes (P-15's cell is not tried on the same window); the window is spent and is folded into development only
by a later decision row. An ES test of the coin after a FAIL would be a new hypothesis on another market, registered on
its own with this FAIL in its record and its count -- not a rescue of this one.

> A failed pre-registered check is **kept on record and diagnosed**, never rerun until it passes: terminal-state audit →
> stage decomposition → component test in isolation → replication with seeds fixed beforehand (the auditor writes its
> replication seeds into its note, committed, before any replication runs -- P-10's audit F7). The failure protocol
> applies to the machinery, never to the verdict: a correct FAIL stands. Whatever the verdict, the auditor re-derives it
> from the result files without the producing code (D-355 (5)'s symmetry).

### 5a. Checks computed before registration, on development data only (D-451 (3); never on the window)

Declared in a decision row before they run (EXPLORATORY, they select nothing), run from a clean checkout (D-474) on
2020-01-01 .. 2026-07-16 at the identity seed 20261131 (never 20261227), their file quoted in an addendum to this draft
with its sha256 before it goes to the gatekeeper:

1. **The Combine's headroom against the window's bound.** (i) *From the table, no outcomes read:* for every Combine state
   the no-closure table reaches, the realised dollar risk in whole micros at 150 ticks (P-16 §3: the fresh Combine's
   $2,000 realises $1,950), the net win at the state's R after the round turn against the account's remaining need to
   the target, and the loss-side margin -- a stop-out's cost against the room above the MLL, the knife-edge D-548 (2)
   found at the fresh Combine, where the bound's shift turns an abandon into a breach. (ii) *The expected shift:* each R's
   point-minus-bound shift of `e` (`check_bounds`) over every non-overlapping development window of the registered
   length (126 sessions, or END's count), with the frozen marks, its median and 90th percentile, in dollars per trade
   at each Combine state's realised risk. (iii) *The effect:* P-16's development campaign with every R's outcomes
   shifted by (ii)'s median and by its 90th percentile, 200 paths: the Combine pass share, the days to a pass, the
   breach share and growth on the required bankroll, against the gate's own development bound arm. **Consequence, fixed
   now:** the cell does not change. If growth at the 90th-percentile shift is not above zero, END is moved later (a
   longer window, the only lever), decided before registration; the numbers go into this file either way.
2. **The frozen marks' resolution under the year rule.** On every non-overlapping development window of the registered
   length, P-16's frozen marks (not each window's own cutoff, as D-599 did) read by §5's year rule: the share of windows
   whose line fails, at which R, and in which year. A reading beside the registration, deciding nothing; it tells the
   reader how often a frozen-mark window fails the line on the history where the marks were chosen.

## 6. Seed

- **Seed:** **20261227** -- the campaign's resampling on every arm read on the window (the gate and its denial ladder,
  the bound at 0.05/N, the placement on, both twins, the counted quarters' campaigns, the Focused Trader Program's
  models, the funded-capped reading, the release-minute readings). Fresh: a text search of every file in this worktree
  and in the main checkout on 2026-11-09 (git history files and the bar store excluded) found it nowhere; the script's
  test checks it is used by no other script or module. *Why fresh rather than P-16's 20261206 (the common-random-numbers
  precedent of P-06 and P-10):* the window's trades are new, so common random numbers with development buy little, and
  a seed nobody has drawn at removes any question of choice. Any `--check` smoke of the build at it prints and writes
  nothing and reads no window day (the window cannot be read before registration); disclosed at registration if run.
- **The coin's seed:** 20261102 (D-521) -- the sides, per date and mark, extended to the window's dates by
  `resolved_coin.coin_table`; part of the protocol.
- **Identity seed:** 20261131 -- identity (b) and §5a only, on development data.
- **Additional seed:** 20261017 -- `haircut.widened`'s day bootstrap and the deflated Sharpe rows beside (P-16's); nothing
  in C1-C5 reads them. The slices and the journey draw nothing (historical order).

## 7. Variants

- Configurations already tried for this question: the ledger's pool, N at registration (414 at P-16's, §`ledger_n`).
- Configurations this pre-registration will try: 1 (`rc_s150_all_nr`, frozen). Beside it, never a verdict: the Focused
  Trader Program's 16 models (recorded as exploratory variants under this registration's own key), the funded-capped
  cell, the release-minute readings, the identities.

## 8. Anything chosen after seeing results

*(Left empty at registration.)*

## 9. Open items -- what this draft cannot fix before the data arrives, and what must be built

**Choices that wait on the data's arrival (each fixed in the registering decision row, before any bar is imported):**

1. **END** -- the last full trading day the purchase covers; at least 131 full sessions on the calendar (126 walked
   plus the margin), else wait.
2. **The counted quarters** -- which quarters exist follows from END; the calendar counts are computed in the row.
3. **The calendars through END** -- FOMC statements after 2026-09-30 (`config/sources/fomc_statements_2026q3.csv` ends
   there; the October and December 2026 meetings and any in 2027) and BLS 08:30 ET release days for 2027
   (`data/release_days_0830_2026.csv` ends with 2026), packaged with provenance from federalreserve.gov and bls.gov; the
   news-safe cut and FOMC exclusion depend on them.
4. **N** -- `count_n` at the registering commit, the gatekeeper ruling on the exploratory rows since P-16.
5. **§5a's numbers** -- the headroom check and the frozen-mark resolution reading, quoted with their file's sha256; the
   headroom check may move END later.
6. **The purchase's first session** -- item 6's range starts 2026-07-17 (UTC), but trading day 2026-07-17 opens at
   17:00 CT on 2026-07-16 (22:00 UTC), so a range starting 2026-07-17 UTC misses that session's first hours, and the
   store's roll rule needs the previous trading day's volume by contract. Either the range starts 2026-07-16 (the
   overlap is development, which the importer must not rewrite -- a test that the development days' bytes and the
   store's manifest for them are unchanged) or the first session is dropped by a rule fixed before import. A fix to
   item 6's text, not made here.
7. **The rules re-verification** within seven days before registration (rules-verifier); any change recorded beside.
8. **Two gatekeeper rulings this draft asks for:** whether the year rule (§5) needs its own decision row first, and
   whether C5 is a verdict line (this draft's default, D-509 (4)) or beside.

**What must be built (nothing in P-16's registered machinery runs a confirmation):**

1. **A confirmation read path for the walk:** `atlas_a3.bar_arrays` calls `read_bars(..., "development")`; a
   purpose/prereg parameter (default unchanged, tested) or a confirmation reader calling `read_bars(..., "confirmation",
   prereg=pid)`.
2. **The window's day set without A1's development cache:** `a3_resolution_map.load_a1` refuses anything but the
   development days; the coin needs only dates and day kinds, so `atlas_walk._kind`'s rule on the window's bars (early
   close, FOMC, BLS) with the extended calendars, under the confirmation purpose.
3. **The frozen marks:** read from `rc_width_screen.csv`'s `marks` rows at 150 ticks, pinned, never recomputed;
   `rc_width_screen.build` and `rc_stop_walkforward.cell` both recompute the cutoff and cannot be used as they are.
4. **The window's bounds:** `check_bounds` at 0.05 and `edge_stats` at 0.05/N on the window; no era test.
5. **The lines and the verdict word:** C1, C2 on calendar quarters (P-10's per-period campaign pattern,
   `scripts/t24_confirm.py`), C4 with the year rule (a new function -- `a3_brk30.resolution_rows` reads the worst year
   with no minimum), C5 with P-16's slice machinery on the window's starts, and the PASS / CONFIRMED ON THE GATE ONLY /
   FAIL words.
6. **The release-minute cost reading** (§4): the selector of candidates entering at or open across 07:30 and 09:00 CT,
   and the recost.
7. **The guards:** the script refuses without a runnable registration naming NQ's window, unless P-16's row is a
   complete PASS and its result file's sha256 is the registered one, and before identities (a)-(d) hold.
8. **`config/windows.yaml`:** NQ's `reserve` split into a `confirmation` window 2026-07-17 .. END and a `reserve` from
   the next day, with `registered_reads: {P-XX: {NQ: <its name>}}` -- by the registering decision row, not before.
9. **The import and the usability test:** the importer run on the purchase after registration (only days inside
   readable windows stored), the data-integrity report, the walked-session count, the judgement committed before the
   verdict script runs.
10. **§5a's study:** its pure parts, script and tests, declared and run on development data before registration.
11. **Tests:** the seed's freshness, the pins, the frozen marks, the year rule (a stub year below 63 sessions not read on
    its own; at 63 read), the quarters' counting, a read past END raising, and an end-to-end `--check` on development
    days only.

---

## Outcome

*(Filled in after the run. Record it whether it passed or failed; then add the row to `REGISTRY.md`.)*

- **Date run**:
- **Result file(s)**: *(with manifest)*
- **Verdict**: PASS / CONFIRMED ON THE GATE ONLY / FAIL
- **Numbers**: *(cite the result file -- do not type numbers here that are not computed from it)*
- **Diagnosis, if failed**: *(the four-step protocol)*
- **Decision taken**: *(and the `DECISIONS.md` entry number)*
