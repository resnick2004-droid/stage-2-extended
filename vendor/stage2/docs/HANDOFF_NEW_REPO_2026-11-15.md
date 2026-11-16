# Handoff: starting the execution-model research in a new repository (2026-11-15)

**Read this whole file before doing anything else.** It is the brief for a fresh Claude Code session that starts a
new repository. It carries what Stage 2 (`C:\Users\resni\OneDrive\Desktop\Stage 2`) learned in its last weeks so the
new work starts from evidence, not from zero, and it keeps the research discipline that made those results
trustworthy.

**How to read the numbers.** Every figure below was copied on 2026-11-15 from a committed Stage 2 result file that
has a sidecar manifest (script, commit, seed, sha256). The file and section are named beside each figure. They are
exploratory readings on development data (NQ 2020-01-02 to 2026-07-16), read at the one-sided 95 % lower bound of
each strategy's edge (the "bound" or "verdict" arm) unless stated. Re-derive any figure from its file before relying
on it; never copy a figure into new work without its source.

**The operator.** Not a quant; trades by hand; wants every parameter explained and classified as fixed, searched or
dropped; does no work but setup and purchases (nothing is ever bought without their explicit yes). Automated or API
order entry is out: it gets prop accounts banned. Alert-sellers' users also enter by hand.

---

## 0. The task in one paragraph

Build an execution model for prop-firm accounts (Topstep $50K first) that improves a **user's journey** -- a person
who starts on any day, buys evaluations, passes, trades funded accounts and collects payouts -- measured as the
outcome in section 1. The money in every design that works so far comes from the firm's contract shape (a funded
loss costs the user only fees; a funded win is paid), not from a trading edge. The next gain needs either a real
edge spent where the contract pays most, or a contract shape not yet tested. Section 2 lists the constraints any
model must live inside, section 3 what has been learned about levers, section 4 how to test without fooling
ourselves.

---

## 1. The objective: the user's journey as one portfolio outcome

### 1.1 The outcome and the variables

The **outcome** is a start day's **net cash** = payouts received less fees paid, at months 1, 2, 3, 6 and 12
(a month = 21 trading sessions), and whether it is above zero ("ahead"). Every development trading day is replayed as
a fresh start; a design is judged over all of them.

The variables the operator named, as Stage 2 measures them (`docs/USER_MILESTONES.md`, D-620, D-621):

| variable | measure | name |
|---|---|---|
| bankroll needed | cash spent before the first payout, 90th percentile of start days | S1 |
| time to first evaluation pass | sessions to the first pass | (U1 start rows) |
| time to first payout | share of starts paid by session 21; sessions to first payout, p90 | S3a, S3b |
| dollars per payout | payouts received per fee dollar at month 3 (pooled) | S3c |
| dollars spent to a pass | cash spent before the first pass | (U1 start rows) |
| **the outcome** | mean share of starts ahead at months 1, 2 and 3 | **P (primary)** |
| outcome later | share ahead at months 6 and 12 | S4a, S4b |
| the bad case | month-3 net of the unlucky tenth of starts (p10) | S5a |
| steadiness | longest gap between payouts p90; month-6 concentration | S5b, S5c |

### 1.2 What decides the outcome (measured)

From `results/user_drivers.csv` (U3, D-656/D-657), section `between_designs`, subject `all_cells` (61 designs,
intervals from resampling whole families -- a description of related designs, not a test):

| measure against P (rank correlation) | value | 95 % interval |
|---|---|---|
| payouts per fee dollar (S3c) | 0.76 | 0.37 to 0.93 |
| share paid by session 21 (S3a) | 0.19 | -0.45 to 0.87 |
| bankroll needed (S1) | 0.09 | -0.46 to 0.55 |
| sessions to first payout (S3b) | 0.07 | -0.67 to 0.60 |

A standardised regression of P on S1, S3a, S3c and S5a gives S3c the weight (0.88) and explains most of P
(R squared 0.92). **What moves the share of users ahead is what a funded account pays back per fee dollar. Speed
and bankroll barely do.**

Inside one design across start days (section `within_design`, P-14, bound arm, month 1): the month-1 net moves most
with whether and how soon a first payout came (sessions to first payout -0.74; paid by the month 0.70; first payout
dollars 0.68); cash before the first pass (-0.10) and sessions to the first pass (-0.12) hardly matter. Section
`accounting`: nearly all the spread in a user's net is the payouts (spread share 0.99 at month 1 for P-14), almost
none the fees -- users pay much the same and are paid very differently.

**Design against luck** (section `design_vs_luck`, U1's nine configurations, bound arm): the design is 0.075 of the
variance of a user's net at month 1, 0.032 at month 2, 0.041 at month 3, 0.092 at month 6, 0.195 at month 12; among
the three best designs alone, 0.016 / 0.002 / 0.016 / 0.058 / 0.141. **A user's first quarter is mostly the day
they start, not the design.** The honest promise to a user is a distribution of outcomes, not a design's average.

### 1.3 What is solid ("something that works")

- **The best designs on file for a user** (`results/u_budget.csv` section `cell`, block `all`, bound arm):

  | design | P | S1 | S3a | S3c | S4a | S5a |
  |---|---|---|---|---|---|---|
  | P-14 (row to beat) | 0.671 | $3,003 | 0.795 | 1.85 | 0.985 | -$769 |
  | P-15 | 0.642 | $3,003 | 0.768 | 1.74 | 0.966 | -$1,146 |
  | P-16 | 0.620 | $3,450 | 0.595 | 2.08 | 0.977 | -$1,162 |

  P-14: a 30-minute-bar breakout followed five bars late, on 12.5/25-point NQ stops, five Topstep seats, the
  no-closure state table, at most 20 evaluation purchases in 21 sessions. P-15/P-16: a "coin" (a fair coin chooses
  the side at every 5-minute mark; no signal) on 25 and 37.5-point stops. Registered verdicts: P-14 PASS at
  0.05/370, P-15 PASS at 0.05/403, P-16 PASS at 0.05/414 (Stage 2 `prereg/REGISTRY.md`, D-532, D-547). Their margin
  for a user is inside the noise (D-628).
- **Robust under stress** (`results/v1_validation_*.csv`, D-665): P-16's growth at the bound holds under
  block-resampled days at 5, 21 and 63-session blocks, under missed trades and missed sessions, and through every
  declared shift below its bound -- it does not depend on the order of days. FV3-C (an older design) does.
- **No variable is a free improvement.** Every lever tested moved along a trade-off (section 3).

### 1.4 The middle ground

`results/user_drivers.csv` section `frontier` lists the designs not beaten at once on P, S1, S3a and S5a; section
`menu` picks the highest-P design under a bankroll limit among those still ahead in at least 95 % of starts at
month 12 (limits set after the families were read -- reading aids, not candidates):

| pick | design | P | S1 | S3a |
|---|---|---|---|---|
| lowest cost (S1 at most $2,000) | P-14 on one account | 0.460 | $1,774 | 0.211 |
| balanced (at most $2,500) | P-14, budget of 10 purchases in 21 sessions | 0.645 | $2,355 | 0.615 |
| best result (no limit) | P-14, no purchase budget | 0.692 | $3,405 | 0.819 |

**How to search for a middle ground in the new work:** fix limits on what a user feels (bankroll, time to first
payout) first, then maximise P inside them, and report the frontier, not one number. Use payouts per fee dollar as
the screening target, because it is what moves P.

---

## 2. The constraints a model must live inside

### 2.1 Firm rules (Topstep $50K; every row verified on the official help centre, Stage 2 `config/rules.yaml`)

| rule | evaluation (Trading Combine) | funded account (XFA) | article |
|---|---|---|---|
| profit target | $3,000 | none | 8284208 |
| maximum loss limit | $2,000, trailing, locks at the start balance | starts at -$2,000; floor to $0 after the first payout | 8284204 |
| best day | at most 55 % of the target ($1,650) | Consistency path only: at most 40 % of profit | 8284208 |
| position size | 5 minis (50 micros) | scaling: 2 minis from $0, 3 from $1,500 profit, 5 from $2,000 | 8284197, 8284223 |
| payout eligibility | n/a | Standard: 5 winning days of at least $150; Consistency: 3 trading days | 8284233, 8284208 |
| payout | n/a | at most 50 % of balance; cap $2,000 Standard, $3,000 Consistency; 90 % split; minimum $125 | 8284233 |
| fees | $49 a month, $49 reset | $149 activation | 14289835, 8284217 |
| accounts | n/a | at most 5 funded at once (shared across sizes) | 8284215 |

Larger sizes ($100K, $150K) are verified too (D-623, D-645); the funded lock balance of a larger account is stated
on no page. Lucid (second firm) is verified and priced except its funded monthly and payout fees (D-561, D-575).
Conduct, three tiers (D-145): tier 1 hard -- no hedging across accounts or firms, no simulator-fill exploitation or
tight-bracket scalping, no maximum size into major news, nothing that conceals a pattern; tier 2 modelled -- the
Responsible Trading Program's triggers; tier 3 priced -- account stacking and discretionary payout denial.

### 2.2 Stop, size and cost on NQ micros (`results/stop_band.csv`)

| state | risk the table uses | micro cap | widest stop at full size |
|---|---|---|---|
| evaluation | $1,500 | 37 micros | 82 ticks (20.5 points) |
| funded, below $2,000 profit | $1,000 | 15 micros | 134 ticks (33.5 points) |
| funded, at or above $2,000 | $300 | 37 micros | 17 ticks (4.25 points) |

Cost floor: stops under 45 ticks (11.25 points) are eaten by costs (`stop_band.csv`, `cost_drag_floor_ticks`).
Measured: the 12.5-point stop loses to costs (D-527); fixed 20-point brackets lose (D-423); 37.5 points is best all
day; 40 and 50 points are worse or do not resolve (D-542, D-598).

### 2.3 Contract ceilings at zero edge (stage one, exact; an output outside them is an engine error)

P(pass) at most 2/5 for any fair strategy; the supremum over fair strategies 0.327131; 1:1 at $1,500 passes 16/49;
expected gross payouts of a funded account at most $2,000 (Stage 2 `CLAUDE.md`, propsim D-08, D-47).

### 2.4 Execution rules imposed

- latency: at least 5 minutes from alert to order (D-266); a resting order may go live 5 minutes after the alert
  and then fill at its level;
- one position at a time across a firm's accounts, five minutes flat between trades (D-429);
- every trade resolves: at most 5 % reach the 15:10 CT flatten; no time stops (D-212);
- realised risk matches intended: at least 90 % of trades realise at least 90 % of intended risk (D-308);
- no entry before 07:35 CT on a BLS 08:30 release day; FOMC days excluded (D-525, D-533);
- each account carries its own trades -- never the same trade copied across accounts (D-157).

### 2.5 The sizing plan that works (P-14/P-16's state table; `results/u_xfa_day_budget.csv`, U2, D-652)

- evaluation: asks 1.5R at $2,000 fresh; realised about $1,000 (P-14) and $1,500 (P-16), the size limit binding;
- funded opening: asks 3R at $2,000, realised $1,000 to $1,500 (`opening_trade`, `realised_risk_p50`);
- after the opening: mostly $250 at 1R to collect the five winning days; paid accounts $250 to $500 at 1R to 2.5R
  (`table_leaves`).

What a funded account's life is (bound arm; P-14 / P-15 / P-16):

| reading (`u_xfa_day_budget.csv`) | P-14 | P-15 | P-16 |
|---|---|---|---|
| win the opening trade (`opening_trade`, `share_won_it`) | 0.251 | 0.219 | 0.225 |
| of those, reach the payout (`after_opening`, in profit) | 0.939 | 0.922 | 0.963 |
| lose it and live (`share_lost_it_and_lived`) | 0.749 | 0.781 | 0.775 |
| of those, ever paid (`share_ever_paid`) | 0.199 | 0.193 | 0.110 |
| their share of pre-payout account-days (`budget_before_first_payout`) | 0.610 | 0.649 | 0.574 |
| sessions from opening to fifth winning day, median (`after_opening`) | 8 | 9 | 10 |
| funded trades per live account-day (`signal_supply`) | 0.920 | 0.931 | 0.841 |
| share of offers routed (`signal_supply`, router) | 0.149 | 0.022 | 0.026 |

### 2.6 Supply

About one decisive trade per account per day and five or more signals a session per firm (D-452, D-154). Signals are
not the limit: the router uses only a few percent of what it is offered (above). At zero edge, one $1,500 1:1 setup a
day passes an evaluation as often as any frequency and resolves in a median 2 days; more than one a day lowers the
pass rate (`results/setups_per_day.csv`).

### 2.7 Where a win is worth most (`results/u_value_map.csv`, U5, D-668/D-669)

From the solved tables at the bound edge, the value of one won trade over one lost trade (mean, dollars), and of
+1 percentage point of win probability, by place (section `place_values`):

| place | P-14 value of a win | P-14 $/yr per +1 pt | P-16 value of a win | P-16 $/yr per +1 pt |
|---|---|---|---|---|
| (b) evaluation trades | $225 | $914 | $287 | $1,224 |
| (c) funded opening trade | $1,426 | $1,073 | $2,277 | $1,766 |
| (d) later funded trades | $629 | $2,109 | $571 | $1,526 |
| (e) paid-account trades | $665 | $2,442 | $639 | $3,071 |
| (a) every trade | $553 | $6,538 | $606 | $7,587 |

("$/yr" is a five-seat campaign, the solver's forward basis; the file also holds a records basis.) Section `bar`:
the extra win probability a signal needs to add $500 a year -- on P-16, used on the funded openings: 1.83 points at
12 uses a year, 0.61 at 36, 0.42 at 52, then capped by the openings' supply (about 50 to 78 a year); used on every
trade: 6.88 points at 12, 2.29 at 36, 1.59 at 52, 0.79 at 104, 0.33 at 250. First-order; unreliable far from zero.

**Rank a signal by frequency x extra win probability x the value of a win where it is used, not by win rate or
R:R.**

---

## 3. Levers: what was learned

### 3.1 Lever families tested on the user scorecard (all CLOSED; nothing carried)

Each family was chosen on starts in 2020-2023 and judged on starts from 2024 against P-14 (the row to beat), at a
family-wise level 0.05/(k(k+1)). The judged-block P of each family's pick against P-14's 0.719 (each family's file,
section `judged`, measure P):

| # | family (decision rows) | pick, judged P | why it closed |
|---|---|---|---|
| 1 | purchase budget (D-629, D-634) | 0.654 | less cash needed, fewer users ahead |
| 2 | cost of entry: wallet stop, pause, seat ramp (D-630, D-637) | 0.618 | the same trade-off |
| 3 | seats (D-635, D-638) | 0.668 | fewer accounts are worse on everything but cash |
| 4 | trading hours (D-639, D-642) | 0.670 | US hours about level; other windows worse |
| 5 | a second firm, hedged or not (D-643, D-644, D-651) | 0.621 | Lucid seats cost more up front or spend the first payout; hedge pairs under a fifth of signals (hypothetical) |
| 6 | Consistency path on the tables on file (D-646, D-648) | 0.001 | the bold opening breaks the 40 % rule |
| 7 | flat funded plan (D-653, D-654, D-655) | 0.482 | pays sooner but less than the fees |
| 8 | flat plan at the size limit (D-658, D-661) | 0.514 | the size trend runs out |
| 9 | crippled accounts resolved at once (D-659, D-662, D-664) | 0.683 | ends more accounts than it rescues |
| -- | account size $100K/$150K, solver fit (D-666, D-667) | closed at the fit | 18 to 41 % less back per fee dollar (`u_size_fit.csv`) |

Files: `results/u_budget.csv`, `u_entry.csv`, `u_seats.csv`, `u_hours.csv`, `u_firms.csv`, `u_consistency.csv`,
`u_plan.csv`, `u_limit.csv`, `u_resolve.csv`, `u_size_fit.csv`. 76 cells counted in nine families.

### 3.2 Mechanics inside the execution model

- **The bold funded opening is where the money is.** One won opening funds the account's payouts; every change to
  the funded leg (smaller, flatter, equal-days, resolving crippled accounts) was worse for a user.
- **Lost-opening accounts are not waste:** the table's small trades recover enough of them to be worth the seat.
- **Equal 1R days suit the Consistency path** (it beats Standard at equal size, D-655), but still lose to the bold
  opening on Standard.
- **Time of day changes resolution speed and cost, not the win rate at zero edge.**
- **Signal search on OHLC rules found nothing that survives costs and latency:** 136 strategies against their coin
  twins -- gains are schedule, not direction (D-558); the 2024-2026 follow-momentum lift failed the span guard
  (D-580); the one rule that passed at no delay died at 5 minutes (D-592); ORB5, fixed brackets, P&F all closed
  (D-275, D-423, D-616, D-617).

### 3.3 Structural sides not yet tested

- **Resting orders at pre-announced levels** (stop-entry for breaks, limit for pullbacks; ticket published at least
  5 minutes before it can trigger, so latency counts to placing the order, not to the fill). Re-opens level-based
  ideas that died on the delay; suits a signal service. Model fills conservatively (trade-through by a tick for
  limits; same-bar stop first) and measure adverse selection.
- **A multi-feature model** (one pre-registered classifier on 30-50 normalised OHLCV features, purged walk-forward,
  judged out of fold against the coin on the same brackets and valued by the value map). Expect volatility and
  resolution speed to be predictable, direction hard.
- **Other firms' contracts** (end-of-day drawdown, no consistency rule), each verified on the firm's own pages.
- **Payout policy for a user's first months** (how much to withdraw and when) was tested for long-run growth only.
- **Closing a crippled funded account at request to free its seat** -- the rule is unverified
  (`xfa_closure_at_request`); ask Topstep support (Stage 2 `docs/OPERATOR_SETUP.md` item 5).
- Dropped: rare calendar effects (pre-announcement drift, turn of month, FOMC cycle) -- too few signals to matter
  and about 2 % power on six years of data (the operator, 2026-11-15); automated entry (bans).

### 3.4 How to use it next

1. Supply comes from a schedule (P-16's marks); an edge is a **side or a filter on those offers**, never a
   replacement for supply.
2. Spend a rare edge on the funded openings; a frequent one on every trade; rank by the value map's bar.
3. First families to build: the resting-order level atlas, then the multi-feature model, both on the local NQ bars.
4. More history (QuantConnect's free NQ/ES from 2009, or a Databento purchase) raises power for everything; it is
   the operator's call.

---

## 4. The research structure (A to Z): turning constraints into tested models

### 4.1 The pipeline (Stage 2 `docs/RESEARCH_PROTOCOL.md`, D-155)

1. **Hypothesis** -- the mechanism (why someone is on the other side) and the source.
2. **Contract fit** -- does it fit section 2: supply, stop band, latency, resolution, conduct.
3. **Cheap screen** -- one mechanism plus at most one filter, on development data; lift over the coin twin.
4. **Pre-registration** -- written before the run: data span, fixed rules, every parameter classed fixed /
   searched / dropped, metrics, pass/fail lines, seeds, the family's N; refused if incomplete. A model card must pass
   `validate_card` (setups per day, stop band, latency, resolution, eras).
5. **The run** -- from a clean checkout of a named commit, results written with a manifest.
6. **Verification** -- the identities hold; an independent auditor re-derives the numbers from the CSV without the
   producing code.
7. **Prop environment** -- the campaign through the firm's rules, with the gate and the user scorecard beside.
8. **Verdict and one confirmation** on data never read.

### 4.2 Turning constraints into features and labels

- **Label = the bracket outcome.** For each candidate time t (alert), entry no earlier than t + 5 minutes (or a
  resting order live from t + 5), the stop from the stop band, targets at each R, resolved by 15:10 CT: win, loss or
  flatten (the triple-barrier label). Stage 2 already holds these walks for every 5-minute mark (`data/atlas`).
- **Features** are computed from bars closed at or before t only, and normalised (rolling ATR, session spread,
  time-of-day medians) -- never raw price levels.
- **The test statistic is lift over the coin twin** on the same brackets (the same entries with a fair coin's side),
  so supply, cost and schedule cancel and only direction is measured; then value the lift with the value map.
- **Supply and resolution gates** come before any outcome is read: signals per session, unresolved share at every R
  (at most 5 %), realised-risk match.

### 4.3 Guards against overfitting and poor procedure

- **Pre-register the family, not the model;** count every variant tried; report the count with any result.
- **Multiple testing:** a family's level is 0.05/(k(k+1)) for the k-th family of a program (a fixed 5 % budget);
  within a family a studentised max-statistic over a session block bootstrap (block 21, fixed seed); Benjamini-
  Hochberg beside, never selecting.
- **Walk-forward:** choose on an early block, judge on a late block; one pick per family reaches judgement;
  purged and embargoed splits longer than the longest trade for any fitted model.
- **The bound, not the point:** money decisions use the one-sided 95 % lower bound of the edge (Student-t on
  21-session block means); the point estimate is reported beside.
- **Identities first, refusing:** with the new option off, the code reproduces the registered result exactly; a
  result outside a stage-one ceiling is an engine error.
- **Twins:** a zero-edge twin and a coin twin for every campaign; a 50-sequence coin guard (at least 40 of 50).
- **Stress checks beside every verdict (D-663):** block-resampled days (5, 21, 63), the bound's coverage, the
  break-even edge and its margin, missed trades and sessions, slippage.
- **Data windows:** declare a confirmation window per market before any development read; never read it until a
  candidate is registered (Stage 2 `config/windows.yaml`; NQ from 2026-07-17 is reserved).
- **Exploratory is labelled:** anything chosen after seeing results is exploratory and reported separately.
- **The failure protocol:** a failed check stays on record; diagnose (terminal states, stage decomposition,
  component in isolation, replication with seeds fixed in advance); never rerun until it passes.
- **Provenance:** every result CSV has a manifest (script, commit, seed, parameters, sha256); no number is typed
  into a document; a trace check recomputes the headline numbers.
- **Clean runs:** results come only from a clean, detached checkout of a committed commit; one heavy run at a time
  on the machine.

---

## 5. What to bring from Stage 2

Read-only references (copy or vendor, never edit in place): the rules ledger (`config/rules.yaml`,
`RULES_LEDGER.md`); the result files named above with their manifests; the research protocol, success criteria and
pre-registration templates (`docs/RESEARCH_PROTOCOL.md`, `docs/SUCCESS_CRITERIA.md`, `prereg/TEMPLATE.md`,
`prereg/FAMILY_TEMPLATE.md`, `prereg/MODEL_CARD_TEMPLATE.md`); the engine (`propedge/campaign/` -- `lockstep.py`,
`gate.py`, `risk_policy.py`, `state_policy.py`; `propedge/contract/adapter.py`); the bars (`data/bars/NQ`,
Databento NQ 1-minute OHLCV 2020-01-02 to 2026-07-16, licensed for private use, never committed) and the atlas walks
(`data/atlas`); the release calendars (`data/releases_bls_0830_*.csv` with provenance); the literature review
(`docs/research_inbox/EDGE_LITERATURE_2026-11-15.md`).

The Campaign Studio (`Stage 2C - Campaign Studio`, its analytics workbench, SD-95) visualises program U's files;
it reads Stage 2's `results/` and needs no change while those files stay.

## 6. Open items the operator holds

- Data: ES 1-minute bars (Stage 2 `docs/OPERATOR_SETUP.md` item 1) and NQ from 2026-07-17 (item 6) for any
  confirmation; or QuantConnect's free history (needs the operator's QuantConnect user ID and API token configured).
- Topstep support questions (item 5): closure at request, seat timing.
- Lucid's two unpriced fees.

## 7. First steps in the new repository

1. Write its charter from section 0 and section 1: the objective is P (share of starts ahead over months 1-3) with
   the guarded measures, payouts per fee dollar as the screening target, the frontier reported.
2. Vendor Stage 2's engine and rules read-only, with an identity test that it reproduces P-14's and P-16's
   registered rows.
3. Declare the first family before building it: the resting-order level atlas (levels, order types, R values,
   expiry, fill rules), judged by lift over the coin twin valued with the value map, with its kill lines.
