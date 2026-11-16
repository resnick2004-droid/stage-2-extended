# F-01: the resting-order level atlas (family RL) -- declared before it is built

**Status: DECLARED 2026-11-15 (E-003). Nothing of it is built; no bar has been read for it; no outcome of any level
order has been computed.** This file is fixed by its sha256 in E-003. Nothing declared here is edited: a change is a
new family under a new decision row. Anything chosen after a reading is exploratory and reported apart.

Family number **k = 10** of the program (E-001: Stage 2's program U closed families 1-9), so the family's level is
one-sided **0.05 / (10 x 11) = 0.05 / 110**. One cell reaches judgement; no further division inside the family.

---

## 1. Hypothesis (research protocol step 1)

**The mechanism.** Orders cluster at prices everyone can see before the session: just beyond the prior session's high
and low, the overnight range, the opening range, the prior close, and round numbers. Stop-loss and breakout stop
orders beyond such a level turn a touch into a burst of market orders in the direction of the break (a cascade);
resting limit orders at the level absorb a touch and push it back (a rejection). Which dominates is the question: the
break side is paid by liquidity providers caught by the cascade, the fade side by momentum traders who bought the
touch. The evidence that order clustering at visible levels moves prices is in currency markets (Osler 2003, *Journal
of Finance*, "Currency orders and exchange rate dynamics"; Osler 2005, *Journal of International Money and Finance*,
"Stop-loss orders and price cascades in currency markets"); for NQ it is untested here. Stage 2's own breakout work
entered at the market after a delay (ORB5, Stage 2 D-275; P-14's 30-minute-bar breakout followed five bars late);
nothing in Stage 2 entered **at the level itself**.

**Why a resting order (the structural side, handoff section 3.3).** A ticket published at least five minutes before it
can trigger moves the operator's latency (Stage 2 D-266) from the fill to the placing of the order: the order then
fills at its level, not five minutes after. Level ideas that died on the delay are re-opened, and the form suits a
signal service whose users enter by hand. Automated entry stays out.

**What would make it worth something.** Not its win rate: its lift in win probability over the coin at the same fills,
times how often it fires, times what a win is worth where it is used (Stage 2's value map, `results/u_value_map.csv`).

## 2. Contract fit (step 2) -- the constraints each cell lives inside

| constraint | how the family meets it |
|---|---|
| latency, at least 5 minutes (D-266) | every level is computed from bars closed at or before the ticket's publish time `t_pub`; the order is live from `t_live = t_pub + 5 min`; nothing fills before `t_live` |
| one position per firm, 5 minutes flat (D-429) | the screen reads every fill of a cell independently; the campaign (stage D) routes by the strict rule |
| resolution, at most 5 % to the 15:10 CT flatten, no time stops (D-212) | kill line K2 and the cutoff rule (section 4) |
| realised risk matches intended (D-308) | kill line K3 |
| stop band and cost floor (`results/stop_band.csv`) | stops of 25 and 37.5 points only -- the two coin rungs registered as P-15 and P-16; both above the cost floor; the 12.5-point stop loses to costs (D-527) and is not offered |
| news (D-525, D-533) | no order live before 07:35 CT on a BLS 08:30 release day (`vendor/stage2/data/releases_bls_0830_*.csv`); FOMC days excluded |
| conduct (D-145) | each account its own ticket (no copying, D-157); no hedge; no maximum size into news; a resting order at a public level conceals nothing |
| hours | US regular hours (handoff 3.1, family 4: US hours level, other windows worse); a user publishes and places the ticket by hand |

## 3. The grid (every cell is one trial; k_cells = 20)

**Levels** (kinds; each computed from 1-minute bars closed at or before `t_pub`; CT throughout):

| kind | the level(s) | `t_pub` | `t_live` |
|---|---|---|---|
| `pd` | the prior regular session's (08:30-15:00) high and low | 08:25 | 08:30 |
| `on` | the overnight session's high and low (17:00 the prior evening to the 08:25 bar's close) | 08:25 | 08:30 |
| `or30` | the opening range's high and low (08:30-09:00) | 09:00 | 09:05 |
| `pdc` | the prior regular session's close (the 14:59 bar's close), on whichever side of price it lies at `t_live` | 08:25 | 08:30 |
| `rn100` | the nearest multiples of 100 index points above and below the 08:25 bar's close | 08:25 | 08:30 |

A level above the price at `t_live` is a **resistance**, below a **support**. On a BLS 08:30 release day no ticket
is live before 07:35 CT (every `t_live` above is already later; the rule binds any later kind); FOMC days carry no
tickets.

**Side rules** (order types):

| rule | at a resistance | at a support | fill |
|---|---|---|---|
| `break` | buy **stop** one tick above the level | sell **stop** one tick below | first bar after `t_live` trading at the stop price; fill at the stop price plus one tick of slippage (`slip_ticks`, Stage 2 `config/atlas_a3.yaml`), or at the bar's open plus slippage if it opens beyond the stop (gap through) |
| `fade` | sell **limit** at the level | buy **limit** at the level | only when a bar after `t_live` trades **through** the level by at least one tick (a touch is not a fill); fill at the limit price, never better |

**Stops:** 25 and 37.5 points (100 and 150 ticks) from the fill price. **Targets:** R in {1, 1.5, 3} -- the table's three
asks (handoff 2.5: about 1R on later funded and paid trades, 1.5R on the evaluation, 3R on the funded opening).

Cells: 5 level kinds x 2 side rules x 2 stops = **20 cells**, each read at 3 R values.

**Per ticket and day:** each level is one ticket a day; it fills at most once; once filled it is not re-armed. A ticket
whose level is on the wrong side of the price at `t_live` (a stop already through, a limit already marketable) is
**void** for the day and counted. A ticket is cancelled at its cell's **cutoff** (section 4) if unfilled. When both
levels of a kind fill on one day, both fills count in the screen (the campaign takes the first, by the strict rule).

**The walk (bars, conservative).** From the fill bar on, on Stage 2's 1-minute NQ bars: a bar that reaches the stop is a
loss; **on the fill bar itself a stop touch is a loss and a target touch is not counted**; on a later bar touching both
stop and target, **the stop comes first**; a trade still open at 15:10 CT is flattened at that bar's close and counted
unresolved. Costs: Stage 2's cost at the cell's stop (`atlas_a3.fee_by_stop`, FV3-C's model; the published round-turn
costs of `config/fills.yaml`), the stop exit slipping one tick, a target exit (a limit) none.

**The mirror and the coin twin.** For every fill the **mirror** trade is the opposite side at the same fill bar and price
with the same stop, target and walk rules. A fair coin's expected outcome at that fill is the mean of the rule's trade
and its mirror, so the **lift over the coin twin** is

    lift(c, R) = mean over the cell's fills of  1/2 [ win(rule side) - win(mirror side) ]

in win probability (and the same in net R, beside). This is the coin twin's expectation, without the coin's noise. A
seeded coin twin (seed 20261902, one side per fill) is computed beside, as Stage 2 does, and decides nothing.

## 4. Supply and resolution gates -- read before any outcome (the kill lines K1-K4)

Read on the **choice block** (fills from 2020-01-02 to 2023-12-29) from fill counts and barrier columns only, the rule
side and its mirror pooled so no direction is read:

- **The cutoff rule.** A cell's cutoff is the latest of 14:30, 14:00, 13:30, ..., 10:00 CT such that, over fills before
  it, the pooled unresolved share is at most 5 % at every R in {1, 1.5, 3}. Fills after the cutoff are dropped (the
  ticket is cancelled at the cutoff). No such time: the cell is killed (K2).
- **K1 supply:** at least 100 fills on the choice block and at least 12 a year (the value map's smallest use count).
- **K2 resolution:** the cutoff exists, and in no single year of the choice block does the pooled unresolved share
  exceed 10 % at any R.
- **K3 realised risk (D-308):** at least 90 % of the cell's stopped trades realise at least 90 % of the intended risk.
- **K4 fill realism (reported, never a kill):** for `fade`, the share of touches that traded through (fills over
  touches); for `break`, the share of fills that gapped through the stop; the outcome of touched-but-unfilled `fade`
  tickets beside the filled ones (the **adverse selection** of the limit fill: what the fills missed).

**Planning (before the screen, from counts only):** each surviving cell's minimum detectable lift at the family level on
the judged block, from its fill count and the worst-case sd of the paired difference (0.5), so the family's power is
on record before any lift is read.

## 5. The selection rule and the kill lines on outcomes

**Stage B -- choose on the choice block.** For every surviving cell and R: the lift, studentised by a session-block
bootstrap (21-session blocks, seed 20261901, 2,000 draws), and the family-wise critical value of the **maximum**
studentised lift over all (cell, R) pairs at one-sided 0.05. Benjamini-Hochberg at 10 % beside, never selecting.
- **Kill B:** no (cell, R) above the critical value -- the family closes; the judged block is not read.
- **The pick:** among those above it, the (cell, R) with the largest **valued lift** (below) at its lower confidence
  limit at the critical value. One pick only.

**The valued lift** (the value map's own first-order formula, `results/u_value_map.csv` definitions
`extra_win_prob_points` and `mean_dv`): `$ a year = (lift in points) x uses x mean_dv / 100`, uses = the cell's fills a
year on the choice block, capped by the place's `trades_per_year_forward`; the place is the one whose table ask is the
cell's R -- R = 3: (c) the funded opening; R = 1.5: (b) the evaluation; R = 1: the larger of (d) later funded and (e)
paid -- on base `p16` for the 37.5-point stop and `p14` for the 25-point stop (section `place_values`, phase as the
file records it). First-order; the table held fixed; read as a ranking, not a forecast.

**Stage C -- judge on the judged block** (fills from 2024-01-02 to 2026-07-16), the pick alone:
- **Kill C1:** the lift's one-sided lower bound at **0.05 / 110** (Student-t on 21-session block means of the paired
  differences, the handoff's bound convention) is not above zero.
- **Kill C2:** the valued lift at the lift's one-sided 95 % lower bound is below **$500 a year** (the value map's `bar`
  target) -- a real but worthless lift closes the family too.
- Beside, deciding nothing: the reverse walk-forward (chosen on 2024-2026, judged on 2020-2023); the pick's lift by
  year; the seeded coin twin; net R lift; K4's adverse selection on the judged block.

**Stage D -- the campaign** (only if C holds), through Stage 2's vendored engine:
- **The design:** P-16's schedule (the 37.5-point news-safe coin re-entering when flat, P-14's engine call) with the
  pick's tickets added: a ticket is published to the firm; whichever of a level fill and a P-16 offer comes first while
  the firm is flat takes the firm's one position (the strict rule, 5 minutes), the other is skipped and counted; the
  table sizes every trade as it sizes P-16's.
- **Identity first, refusing:** with no tickets the design reproduces P-16's registered paths (E-002's identity).
- **Judged by Stage 2 D-621 (3)'s selection rule** against R\* = P-14 (CHARTER section 3) at the family's level
  0.05 / 110: CARRIED or CLOSED. The gate floor at a fresh campaign seed, **20261903**, 500 paths; the coin guard under
  D-568's 50 sequences (20261600 + i) for the P-16 part.

## 6. Data, windows and seeds

- **Development data:** Stage 2's NQ 1-minute bars, 2020-01-02 to 2026-07-16 (Databento GLBX.MDP3 ohlcv-1m, licensed
  for private use; vendored uncommitted, hashes in `vendor/DATA_MANIFEST_stage2.sha256`). Nothing later is read.
- **Confirmation (declared now, before any development read):** NQ from 2026-07-17, at least six months (Stage 2
  D-604), never read until a carried candidate is registered. It is not owned: buying it is the operator's decision
  (stated in `docs/OPERATOR_SETUP.md`, waited for).
- **Seeds, fixed now and used nowhere else:** 20261901 the stage-B bootstrap; 20261902 the coin twin beside; 20261903 the
  stage-D campaign. Stage 2's 20261700 (D-621's paired bootstrap) and 20261600 + i (the coin sequences) as D-621 fixed.

## 7. The build's identities and tests (before any reading)

1. **The walker against Stage 2:** given P-16's own entries (time, price, side, stop -- market entries at a bar's
   open, where the whole bar follows the fill and the fill-bar rule does not apply) the family's bracket walker and
   costs reproduce P-16's trade outcomes exactly -- the content hash Stage 2 pinned
   (`rc150_dev_test.TRADES_SHA256`) -- before it walks a level.
2. **No look-ahead:** every level at `t_pub` is unchanged when every bar after `t_pub` is replaced (a test).
3. **Fill rules on synthetic bars:** stop touch and gap-through; limit touch without fill and trade-through; void
   tickets; the fill-bar rule; stop first on a two-barrier bar; cutoff cancellation; the BLS and FOMC rules; one fill
   a ticket a day.
4. **The mirror:** on synthetic random-walk bars the mean lift is zero within its interval.
5. E-002's identity holds in the build's commit.

## 8. Count, outputs and what a result leads to

- **Variants counted:** 20 cells (each counted whether killed or read), plus one campaign cell if stage D runs.
- **Outputs:** `results/rl_atlas.csv` (sections `supply`, `cutoff`, `kill`, `planning`, `choice`, `judged`, `beside`)
  and, if stage D runs, `results/rl_campaign.csv`; each with a sidecar manifest, EXPLORATORY until a carried candidate
  is registered; run once from a clean checkout of a named commit.
- **Leads to:** CARRIED -> a model card, its registered development test, the auditor, one confirmation on NQ from
  2026-07-17 (a purchase). CLOSED at any kill line -> the reason recorded in a decision row, the failure protocol where
  a check failed rather than a kill line; the family closes and the next family (the handoff's multi-feature model)
  is declared.
