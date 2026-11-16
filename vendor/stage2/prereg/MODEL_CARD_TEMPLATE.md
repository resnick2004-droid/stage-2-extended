# Model card — <model id>: <name>

> Steps 1-4 of the research protocol (`docs/RESEARCH_PROTOCOL.md`, D-155) on one page. Copy to
> `docs/candidates/cards/<model id>.md` and fill it **before any QuantConnect kit is built**. The check is
> `propedge.research.model_card.validate_card`; a model's pre-registration names this card in its `model_card` row
> and is refused unless the card passes. Numbers from result files are cited by file, never typed.

## Machine-checked fields

| key | value |
|---|---|
| `model` | *(an id the kits, results and pre-registration will carry, e.g. IM1)* |
| `markets` | *(e.g. ES, NQ)* |
| `money_source` | *(edge, the contract's shape, or both — and which is expected to carry the result)* |
| `combine_rr` | *(the Combine's R: stage one's choice for the edge assumed — T5 2a, propsim D-08/D-36/D-45)* |
| `combine_risk` | *(dollars per trade in the Combine, same source)* |
| `funded_rr` | *(the funded account's R, same source)* |
| `funded_risk` | *(dollars per trade in the funded account, same source)* |
| `edge_assumed` | *(the low end of the edge the model is expected to have, e.g. 0.00; D-154's check reads it)* |
| `setups_per_day` | *(setups a day per market the mechanism produces, known before any kit: from its rules or the screen)* |
| `accounts` | *(how many accounts the model feeds)* |
| `layout` | *(rotation or partitioned by market across the accounts; copier only for a single account — D-157)* |
| `k` | *(variants: the product of the searched parameters' grids, across markets)* |
| `screen` | *(the cheap screen's result file, or `none: <why no data on hand bears on it>`)* |
| `screen_verdict` | *(continue or kill, against the kill line in §3 declared before the screen ran)* |
| `prereg` | *(the registered P-id, or `pending`)* |
| `entry_type` | *(`market`: at the decision bar; `wait`: a retrace or level touch — D-201)* |
| `max_wait_bars` | *(wait only: the fixed maximum wait, an execution parameter; searched, it counts in k)* |
| `fill_rate` | *(wait only: the screen's share of signals filled within the wait; D-154 reads setups x fill rate)* |
| `stop_distribution` | *(the screen's stops: a result file with `market` and `stop_ticks` in the micro's ticks, or `none: <why>`. From D-191 a file: the prop-fit score reads the zero-micro share from it. From D-212 it also carries each entry's `exit` (target, stop or flatten) and `date`)* |
| `trading_window` | *(D-212: the hours the model trades, HH:MM-HH:MM CT, inside Topstep's: trading resumes at 17:00, flat by 15:10 (8284206). Say in Entry why this window, and count overnight costs if it trades outside the regular session)* |
| `time_stop` | *(D-212: `none` -- every trade is held to its stop or its target. At most 5 % of the screen's trades may reach the 15:10 flatten, overall, in each market and in each year (D-308; 2 % before 2026-10-06); and in every lifecycle state at least 90 % of them must realise at least 90 % of the state's dollar risk in whole micros)* |
| `candidate_record` | *(D-191, step 0: the result file, with its manifest, holding the replicated atlas row the model comes from)* |
| `atlas_row` | *(D-191: the row in it, as `market:test`, e.g. `ES:H01_overnight_reversal`)* |
| `mechanism_grade` | *(D-191: A forced flow, named counterparty, structural or regulatory reason it cannot avoid it; B behavioural, two independent published results and persistence after publication; C a regime or filter, not standalone; D mined, unconfirmed out of sample)* |
| `screen_k` | *(D-191: the screen's own k — every filter and threshold it tried)* |
| `setups_by_market` | *(D-191: setups a day each market produces, e.g. `ES 3, CL 2.5`; the prop-fit score needs at least three of every four markets to reach D-154's minimum on their own)* |
| `conduct_tier1` | *(D-191: `none` — no hedging, simulator fills, off-book fills, size into news, coordination or concealment)* |
| `conduct_tier2` | *(D-191: the Responsible Trading Program flags the sizes raise — R at or below 1, a funded risk above half the drawdown — or `none`)* |
| `conduct_tier3` | *(D-191: `priced` — stacking and purchase patterns carry the gate's denial probability)* |
| `execution` | *(D-266: `manual` — the operator trades every signal by hand. `automated` is a recognised value but refused: D-266 declares every card manual, and an automated model needs its own decision first)* |
| `latency_minutes` | *(D-266: L, minutes from the signal to a working order — a positive number, at least the operator's 5. An order is modelled working only from the signal + L; with rotation one account takes each signal, so L is per signal. Results are reported at L = 0 and at L; the verdict is the one at L)* |
| `missed_trigger_policy` | *(D-266: what happens to a trigger before the order works — `skip`, `rest` (left resting at its level until it next trades through) or `chase` (at the market — in ORB5's capture the next bar's open plus a tick — whose spread is its cost). Required for a resting stop or limit entry (`entry_type` wait) traded by hand; declared before any run. ORB5's capture scores all three at L = 5 and only `skip` at other latencies)* |
| `trading_hours` | *(D-266: the hours the operator can trade — `unconstrained` (the operator's: "Any hours that perform the best I can be available"), or a window HH:MM-HH:MM CT that holds `trading_window`)* |
| `coordination` | *(D-269, where the model has several entries a day (`setups_per_day` above 1): `one_at_a_time` (D-160, the rule for every model but ORB5), or ORB5's option `own_account` declared beside it (`one_at_a_time, own_account`) — each entry to its own free account, direction-locked, which needs more than one account in rotation)* |

## 1. Hypothesis

*(What should make money and why it should exist: the mechanism, a prior from outside our data (paper, market
structure), and who pays. Said before any data is read. A pattern found in our own data is not a hypothesis.)*

## Entry

*(D-201: the feature, the signal rule, the session and time-of-day conditions; market entry at the decision bar or a
wait for a retrace or level touch, with its maximum wait. D-266: the order is placed by hand and works only from the
signal + L (`latency_minutes`); say what a trigger before then does (`missed_trigger_policy`) and how the entry is
scored at L = 0 and at L.)*

## Stop

*(D-201: the structural location rule and the stops' size distribution in the micro's ticks, against the sizeable stop
band `results/stop_band.csv` in each lifecycle state: where the stops fall in it. More than 25 % outside it, on either
side, in any state fails contract fit.)*

## Exit

*(D-201: the target as R x the stop, the session-flat rule. D-212: no time stop -- the trade is held to its stop or
target, and the bracket is sized to the movement left in the trading window, so the 15:10 flatten is a rare outlier.)*

## 2. Contract fit

*(Before any data. The size per lifecycle state from stage one's results, cited — the Combine and the funded account
separately. Setups per day against D-154's minimum for that size (`results/setups_per_day.csv`; the check is
automatic). Copier or rotation, and why. The conduct tiers (D-145): tier 1 refused outright; which tier-2 triggers the
model will fire and that the simulator applies their consequence. The Studio's Configure shows D-150's break-even
edge for the profile as a quick read. D-271: the sizes are met by stop widths drawn from today's regime, not one
stop — see "Eras and today's economics".)*

## 3. Cheap screen

*(The check on data already on hand — the bracket map, the atlas, earlier runs — that could kill the model before a
kit is built. The kill line is written here **before** the screen runs; the result file goes in the `screen` row. If
no data on hand bears on it, say why.)*

## Eras and today's economics

*(D-271, for every model from ORB5 on, fixed before any of its data is read: behaviour is estimated in R on every
year, money only under today's tick economics. Say each of these; `validate_card` checks each is stated, never its
numbers, which come from result files.*

- *Per-era report: beside the pooled figures, e, its one-sided 95 % lower bound, the skew of R per trade, the median
  time to the stop and the share still open at 15:08 for 2009-2017 and 2018 on separately.*
- *The rule: the eras are flagged as different when the 95 % interval of the difference in their mean gross R, from a
  bootstrap that resamples whole years (its seed fixed in the pre-registration), excludes zero; when flagged, the money
  steps use the lower of the two eras' bounds, never the pooled one.*
- *Gross and net: gross R and net R at today's cost in R side by side; no era's costs in the behaviour step —
  era-specific costs enter only the money steps, which are today's.*
- *Today's regime, by the stop: a day is today's when its stop in ticks is at least the stand-aside floor (45 MNQ
  ticks unless T16 item 2(c) fixes another); that old days clearing the floor are the old era's volatile days, a
  selected sample, is reported with them.*
- *Sizing: in the contract fit and the campaign each R outcome is paired with a stop width drawn (seeded) from today's
  regime's own stops — the 2020 to June 2025 days at or above the floor — so the spread of realised risk, and the cap
  it meets, reaches the money numbers.*
- *The baseline: the no-skill baseline (D-246's random entries) rebuilt with the model's own long/short share and entry
  times, year by year; the part of e that NQ's drift alone explains is reported.*
- *D-269, where the model has several entries a day: the `coordination` row — one position at a time (D-160), or
  ORB5's option beside it, each entry to its own free account, direction-locked (never opposite another account,
  D-145 tier 1; never a copy, D-157). For each option the trades it adds over one position at a time are reported
  apart — their own e, its lower bound and their costs — and the options are ranked by time-aware return at the bound
  of e; the tier-2 consequence of several accounts at the MLL in one day applies.)*

## 4. Parameters

| parameter | value or grid | class | source |
|---|---|---|---|
| *(name)* | *(the value, or the grid if searched)* | *(fixed / searched / dropped)* | *(paper, stage one, D-xx)* |

## 5. Kill criteria

*(What ends the model at each later step: a verification failure (D-148: any rule violation is a defect, diagnosed);
the D-145 gate failing on development data; the confirmation run failing. A fail is kept on record and diagnosed,
never rerun until it passes.)*

## 6. Trail

*(Filled in as the steps happen, never before: the pre-registration id, the kit ids, the verification files, the
campaign result files, the verdict and its `DECISIONS.md` entry.)*
