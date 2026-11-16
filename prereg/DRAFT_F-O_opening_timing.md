# DRAFT F-O: a side-free timing filter for the funded account's 3R opening (family O) -- not declared

**Status: DRAFT, first version, 2026-11-16 (TASK_QUEUE Q-37), for the red team. Not pinned, not numbered, not
declared.** Nothing of it is built. No bar, walk, trade or result file was read for it, no state was computed, nothing
was fitted and no outcome was computed. The one piece of code is a synthetic test of the arithmetic and the twin the
draft leans on, and of this file's own reads line and seeds (`tests/test_family_o_persistence.py`, section 18.2,
T-1). This file may be edited until the lead pins it. From the pinning row on, nothing in it is edited: a change is a
new family.

**Its rules come from the operator's ruling of 2026-11-16 (E-023; `CHARTER.md` section 3, "Levers that do not choose a
side").** The filter keeps the coin's side and chooses *when* a newly funded account takes its opening, so E-008's lift
over the coin twin is zero by construction (E-021 (1)); it is a filter of E-023 (2): tested at the trade level against
a **placebo-selection twin**, one-sided at the family's level by a calibrated statistic, valued at that bound, with
section 3's floors and the journey scorecard beside. It can be carried.

**It cannot be pinned before** Q-16 is merged (the pass line's statistic, marked **[Q-16]**), and the items of section
20 are closed. Where the funded openings fall (Q-35) is **not** needed before the pin: it is counted in stage A, on the
choice block, direction-free (section 5.5).

| field | value |
|---|---|
| family | O: a side-free timing filter for a newly funded account's 3R opening -- the opening keeps P-16's coin side and waits, at most W sessions, for a state that predicts persistent moves |
| id | F-XX -- the gatekeeper's |
| program family number k | **the next free at the pin.** F-01 spent 10 (E-007 (a)); F-02's and F-B's drafts are ahead of this one; family R's draft is held unpinned (E-028 (2)); described readings take none (E-023 (1)) |
| level | one-sided **0.05 / (k (k + 1))**: 0.05 / 132 at k = 11, 0.05 / 156 at k = 12, 0.05 / 182 at k = 13, 0.05 / 210 at k = 14, 0.05 / 240 at k = 15 |
| development data | NQ 1-minute bars, 2020-01-02 to 2026-07-16 only, read through `extended/reader.py` (E-026 (2)) |
| base | P-16 (`rc_s150_all_nr`, `vendor/stage2/prereg/P-16_rc-s150-all-nr.md`) as registered; R\* = P-14 beside |
| population | P-16's offers at the marks 17:00-08:25 CT of its walked sessions (on a BLS report day, 07:40-08:25: entries strictly after 07:35:00, E-007 (d)), each walked long and short at 3R (section 5.2) |
| choice block | sessions 2020-01-02 to 2023-12-29. Stages A and B read 2021-01-04 to 2023-12-29; 2020 is the states' warm-up and u3's first training fold |
| judged block | sessions 2024-01-02 to 2026-07-16 |
| confirmation | NQ from 2026-07-17 (`config/windows.yaml`, `reserve`); not on disk, a purchase (section 15) |
| cells (`k_cells`) | **4**: s1, s2, s3, u3 -- each at R = 3, the 150-tick stop, place (c), W = 5 sessions: 4 x 1 x 1 x 1 = 4, each counted whether killed or read |
| judged | one cell: stage B's pick |
| pass line | E-023 (2): C1, the lift over the placebo-selection twin, its one-sided lower bound at the family's level above zero by Q-16's calibrated statistic **[Q-16]** at the larger of its and stage B2's critical value; C2, its value **on the openings' own offers** at that bound at least $500 a year; C3, both sides' halves above zero; section 3's floors; the scorecard beside |
| the wait W | 5 sessions, fixed (section 5.4) |
| seeds | proposed 20261980 to 20261989, checked unique (section 16) |
| model card | only if u3 is the pick (its forecast's 11 coefficients, section 6.5); none otherwise |

---

## 0. In plain words (for the operator)

**Where a win is worth most.** A newly funded account's first trade -- its opening -- is where one more win is worth the
most to a user (Stage 2's value map, `vendor/stage2/results/u_value_map.csv`, section `place_values`, place (c)). P-16
takes it at the first offer the router hands the account, with the coin's side and a target three times the stop (3R).

**What this family changes.** Only *when* the opening is taken. A newly funded account waits -- for at most five
sessions -- for a moment when the market's moves tend to keep going rather than turn back. If no such moment comes in
five sessions, it takes its next offer, as P-16 does. The side is still the coin's. Nothing else changes.

**Why waiting could help, and only at 3R.** On a market without memory, a coin-sided trade with a target three times
its stop wins one time in four, however busy the market is. Busier markets only make it finish sooner. But if moves
persist, a trade that starts moving the coin's way tends to reach the far target, and the coin wins more than one time
in four. At a target equal to the stop (1R) persistence cannot help at all: the long and the short of the same path are
mirror images. So persistence can only matter at the opening's 3R.

**The four moments it can wait for** (each a separate, counted test, chosen from published work before any data):

- **(s1)** the night has been busier than its forecast (an unexpected rise in volatility);
- **(s2)** the night has already moved far in one direction against its expected range (a trending night);
- **(s3)** the day is forecast calm (low predictable volatility);
- **(u3)** family R's "fast" moment, a forecast that the trade will finish quickly. **Stated now: this one is expected to
  win less, not more**, because markets that are predictably busy tend to turn back (the "LeBaron effect").

**How it is judged (the operator's rule, E-023).** The waiting account's choice is compared with a *random* choice of
the same number of offers at the same times of day, on the same kinds of day, in the same years. The family passes
only if:

- the chosen offers do better than random ones by more than chance, at the family's strict level;
- that is worth at least $500 a year **on the offers the openings actually take**;
- both the long side and the short side do better (so a market rising for years cannot pass it by itself);
- every floor holds: trades resolve, the long-run gate, verified rules, conduct.

**Expected.** The published evidence is on the S&P 500 and at other time scales; nobody has shown it on NQ at a
bracket held for hours. The honest prior is no effect, and the development data may only be enough for a screen
(section 9, A9). A "no" is a valid close. What a user would feel (the wait, the journey) is shown beside, never as the
pass line.

## 0.1 Where the brief's items are answered

| the brief's item | where |
|---|---|
| the opening keeps P-16's coin side and waits at most W sessions (declared) | 5.4 |
| the states s1-s3 and family R's (u3), its sign stated in advance, each a counted cell | 1 (iv), 6.3, 17 |
| judged against the placebo-selection twin | 7, 11, 12 |
| valued at place (c) on the openings' own offers | 7.4, 10 item 4, 12 (C2) |
| the journey scorecard beside | 13 |
| prior exposure: Stage 2's S2, the effect atlas's O and R families, S1 and S3 | 2 |
| features only from bars closed by the alert; the library where it serves; no 08:30-08:59 bar of the alert's day (E-030) | 6.1, 6.2, 6.5, 18 (T-2) |
| fitted values only inside the choice-block walk-forward (E-031 (1)) | 6.5 (u3's forecast, the only fitted values) |
| no reverse walk-forward (E-031 (2)) | 8 (dropped), 12 (the year-by-year readings beside instead) |
| the `Judged-block reads:` line (E-026), checked with `extended.reader.declared_purposes` | 19.1; T-1 |
| seeds proposed in 20261980-20261989, checked unique | 16 |
| k the next free | header; 17 |
| where the funded openings fall: counted in stage A, direction-free, on the choice block; what changes if they mostly fall in the opening window | 5.5, 9 (A2) |

## 1. Hypothesis: the mechanism, its sources, and each state's sign stated in advance

**(i) Bracket geometry is textbook probability** (Karlin & Taylor 1975, ch. 7; the scout's note
`docs/research/mechanisms_2026-11-15.md` section 3.1):

- for a driftless price, a bracket with stop a and target b = R a reaches its target first with probability
  1 / (1 + R), on either side, at any volatility; volatility sets only the time to resolve (a b / sigma^2);
- **a side-free filter cannot lift a coin-sided bracket's gross on a price without memory or drift**: whatever days it
  picks, the coin wins 1 / (1 + R) there too (what costs can do is (v) (c));
- **persistence lifts the 3R coin and cannot lift the 1R coin.** With moves that persist, the far target is reached
  more often when the side matches the move, so the side-symmetric 3R win rate rises above 1/4; with moves that revert
  it falls below. At R = 1 the long's and the short's outcomes on one path are exact opposites, so the side-symmetric
  value of every resolved path is zero, whatever the path's memory;
- **a fixed drift moves the two sides apart at first order and their mean only at second order** (gambler's ruin with
  drift).

`tests/test_family_o_persistence.py` (T-1) holds all four on exact chains and seeded walks. One more thing the test
shows in passing, an illustration and not a result: persistence at a scale much shorter than the bracket (a step
repeating its predecessor's sign a little more often than not) moves a bracket many steps wide only a little. **The
mechanism needs persistence at the bracket's own scale** -- a 37.5-point stop and a 112.5-point target, held for hours.

**(ii) The literature linking persistence to observable state** (the scout's 5.1; every figure the paper's own, on the
paper's sample, none at our bracket's scale or on NQ):

- **unexpected against predictable volatility.** Intraday serial correlation of S&P 500 futures is related to realised
  volatility only through its unexpected part, and "the impact of predictable volatility is instead found to be
  negative (LeBaron effect)" (Bianco & Renò 2009, *Quantitative Finance* 9(4) [abstract only]); "a similar but more
  pronounced effect" with intraday measures after the daily effect attenuated (Bianco, Corsi & Renò 2009, *PNAS*
  106(28) [abstract only]); the daily effect is LeBaron 1992 (*J. Business* 65(2) [abstract only]);
- **day-scale persistence.** The first half-hour predicts the last, more strongly on volatile and news days (Gao, Han,
  Li & Zhou 2018); the rest of the day predicts the last 30 minutes, much more strongly on negative dealer-gamma days
  (Baltussen, Da, Lammers & Martens 2021); the always-on version fails out of sample while a threshold version does
  better (Rosa 2022) -- a filter, which is this family's form (all as the review cites them,
  `vendor/stage2/docs/research_inbox/EDGE_LITERATURE_2026-11-15.md` lines 165-192);
- **dealer gamma.** Momentum with a negative gamma imbalance and reversal with a positive one (Barbon & Buraschi 2021
  [abstract only]); higher net gamma predicting a stronger intraday reversal in E-mini order flow (Adams et al.,
  SSRN 5641974 [secondary]). Gamma data are S&P-only and a purchase; this family uses only bar-based proxies of the
  states the literature links to it.

**(iii) The hypothesis.** On P-16's overnight offers, the 3R coin's side-symmetric net outcome is higher, in a declared
ex-ante state, than at a random offer of the same mark, day kind and year; and a newly funded account that waits for the
state takes openings worth more where the openings are actually taken.

**(iv) Each state's sign, stated in advance** (section 6.3 defines them):

| cell | state | sign stated now | why |
|---|---|---|---|
| s1 | unexpected volatility: the night's range above its forecast | **positive** | Bianco & Renò: serial correlation rises with the unexpected part of volatility |
| s2 | a night already trending against its forecast range | **positive** | Gao et al., Baltussen et al.: day-scale persistence, stronger on active days |
| s3 | low predictable volatility | **positive** | LeBaron; Bianco & Renò: predictable volatility lowers serial correlation, so its low third should persist more |
| u3 | family R's (u3): the offer forecast fast | **negative** | family R's draft section 0.1: "by the LeBaron effect, a predictably fast market is less persistent, so a 3R coin opening there should win less". Its forecast also carries today's surprise so far (x3), which by Bianco & Renò pulls the other way, so the prior is weakly negative; **the stated sign is negative** |

s3 and u3 read the same predictable volatility from opposite ends: their two signs are one prediction. The cells are
still judged one-sided for a positive lift (a design is used only if it lifts); section 14 says what a u3 pass would
mean against its stated sign.

**(v) What the trade-level lift can contain, stated before anything is read.** The lift (section 7) is a difference
of net R at 3R between in-state offers and random offers of the same strata. It can contain:

- **(a) persistence** -- the gross effect above, the hypothesis;
- **(b) a drift's second order** -- a state that picks days with a larger drift in either direction raises the
  side-symmetric 3R mean (that is persistence at the day's scale, and counts); a state aligned with a **fixed** drift
  direction (for example calm days in a rising market) raises one side and lowers the other at first order -- C3
  refuses a lift carried by one side;
- **(c) the cost composition** -- Stage 2's walk charges an exit by its kind (`extended.walker.STAGE2`; E-010 (3)): a
  target none, a stop and a breakeven exit one tick, a flatten two ticks **and** the worst of the bars ending
  15:08-15:10 less two ticks. A state that picks fast days (s1, u3) avoids flattens and gains a little from that alone
  (family R's mechanism, its draft section 1 (iv)); a state that picks calm days (s3) flattens more and loses a little.
  Overnight 3R entries mostly resolve before 15:10 (P-16's cutoff admits them), so this part is small, but part of it
  is the conservative flatten convention, not the market: **the lift under the `close` flatten convention is read
  beside** (section 12);
- **(d) the breakeven move** -- P-16's walk moves the stop to the entry at the next session open when in favour
  (FV3's move). It is a stopping rule: on a martingale it adds no expected gross (optional stopping), so it cannot make a
  lift by itself beyond its exit tick; Q-20's corrected moves are read beside (`STAGE2_BE_BOTH`, merged b7232ba).

**(vi) Why it could matter for a user.** The value of a won opening over a lost one is the largest of any place
(`u_value_map.csv`, `place_values`, `mean_dv` at `c_funded_opening`, base `p16`). A filter that fires on about a third
of offers delays openings and does not drop them: the openings' yearly supply is set by passes, not by the filter.

**(vii) Whose accounts and how.** One user's own five Topstep seats, each with its own trades, one position at a time
across the firm (Stage 2 D-157, D-429; E-012 (3)). Every trade is placed by hand at least five minutes after its alert
(E-008). The wait is a decision the user makes before each offer, from bars already closed; nothing is automated.

## 2. Prior exposure: what has already read these bars, this population and this mechanism

A judged reading is worth only what the judged block's freshness allows. Every row below is Stage 2's unless marked.

| row | what was read | data | what it recorded | bearing here |
|---|---|---|---|---|
| D-136, D-137 (the effect atlas, **O family**) | O01: Baltussen et al.'s negative-gamma intraday momentum; O02: an opening-continuation variant; O03: gamma's link to rest-of-day volatility | 2012-2014 (QuantConnect), short | O01 survived and passed its check on NQ narrowly; O02 failed on both markets; O03 passed on both; D-137: O01 not pursued (no translation reaches the criterion; its conditioning is S&P-only) | **outside this repository's window**: independent prior evidence that intraday persistence on NQ is state-dependent, from options data this family does not use; no 2020-2026 bar read |
| D-136 (the effect atlas, **R family**) | R01-R03: the VIX, range compression, a volume surge as predictors of the day's or rest of the day's realised variance | 2009-2014 | VIX and compression predict variance; "sizing and survival inputs, never edge" | outside the window: predictable volatility is predictable on these markets -- the premise of s3 and u3 |
| **D-578 (3), D-580 (S1)** | the sided coin on P-16's schedule: momentum over 1-120 minutes, the move since 17:00, the prior session, range positions, breakouts -- followed and faded, per offer, against the coin twin, at every offered R | 2020-2026, **both spans** | 15-minute momentum and the latest 5-minute breakout, followed, survive the family-wise lift test; both fail the span guard (below P-16 on 2020-2023, above on 2024-2026) | **the sided reading of the same persistence, seen on the judged block.** This family is its side-free counterpart. A sided effect that differs by era warns that a side-free one may too: C3 and the year-by-year readings beside |
| **D-586-D-592 (S3)** | the sided coin on new event kinds; `lnbar1x4` followed passed D-578's guards at L = 0 and failed at the operator's 5-minute latency | 2020-2026, both spans | "the follow-the-breakout effect is broad and slow"; recorded as a lead for unread data (D-592) | the follow effect has been read three times on this window, both blocks: **the judged block is not fresh for persistence at the bracket's scale**, only for this side-free, state-conditioned, 3R-only question |
| **D-578 (4), D-581, D-582 (S2)** | P-16's coin gated by an ex-ante state: the last 30 bars' range in thirds against the same mark's 20 prior sessions; the distance from the 17:00 open above or at-or-below its trailing median | 2020-2026, both spans; **campaign growth over every trade** | no candidate; the high-volatility cell closest to P-16, the trend cell just below; low and mid volatility failed resolution at the longest offered R in their worst year | **the nearest prior: those states and their campaign readings are seen.** S2 read the whole trade stream's campaign growth (mostly 1R-1.5R trades, where persistence cannot act, 1 (i)), removed offers from every account rather than timing one place, and had no placebo. s1 and s2 are relatives of S2's volatility and trend cells and s3 of its low-volatility cell, redefined here from the literature (HAR forecasts, a year's thirds, 3R only, side-symmetric, offer level); **S2's resolution failure is why K2 is a kill before any lift** |
| D-525 (4), D-538, D-542, D-618 (3) | P-16's cutoff per mark (unresolved share at most 5 % at every offered R, kind columns); the stop-width screen | the whole development window, both blocks | P-16's offered marks, none after 09:00 CT at 150 ticks | the population's marks were fixed on both blocks: their average resolution at 3R has been seen, mark by mark |
| P-16's registration; D-605 (by calendar year); D-606 (its draft confirmation) | P-16's gate, journeys and robustness | both blocks | P-16 registered; robust to every single year | the base's own readings over both blocks |
| D-652 (U2), D-667-D-669 (U5) | `u_xfa_day_budget.csv` sections `opening_trade`, `after_opening`, `signal_supply`; `u_value_map.csv` sections `place_values`, `bar`, `records_leaf` | P-16's registered campaign, both blocks pooled, the bound arm | the base's funded opening (the share that won it, its realised risk), what follows it, and the value of a win by place | **the drafter has seen the handoff's tables of these** (sections 2.5 and 2.7; values not typed here): the base opening's won share at 3R, pooled over both blocks and not by any state, is the quantity this family tries to raise. It can bias the decision to propose the family, not the selection |
| E-021; the scout's note section 5.1 | the states s1-s3 proposed from the literature | none | -- | the design, adapted to E-023 |
| family R's draft (Q-38, E-028) | the HAR-type forecast u3 restates (section 6.5) | none | -- | u3's definition; nothing read |
| **Q-35** (queued, heavy) | where P-14's and P-16's funded openings fall | both blocks, if it runs | -- | **if it runs before the pin, its counts over both blocks are a disclosed pre-read** (direction-free); this file's rules use stage A's choice-block count only (5.5) |
| this repository | F-02's and family B's drafts (nothing read); Q-17, Q-18, Q-20, Q-22 when run (P-16's journeys and readings on both blocks) | -- | -- | the scorecard's base readings, beside |

**The drafter's own reads (disclosed).** Code, configuration, decision rows and the section and measure names of two
result files -- no result value was opened beyond what the rows above and the handoff's tables state:

- `vendor/stage2/propedge/campaign/shared_days.py` (the router: `TradeRouter.begin_day`, `able`, the strict rule, the
  new account's stamp), `sizing.py` (`TierSizedDraw.can_take`), `lockstep.py` (`FundedAccount`);
- `vendor/stage2/config/fv3_corrected_portfolio.yaml` (`routing: able`), `vendor/stage2/scripts/rc150_dev_test.py`
  (header), `atlas_a3.py` (`gate_kwargs`), `vendor/stage2/propedge/research/u_value_map.py` (header);
- `extended/features.py`, `extended/walker.py` (presets), `extended/gate.py`, `extended/user_beside.py`,
  `extended/reader.py`;
- the section and measure names (never the values) of `u_value_map.csv` and `u_xfa_day_budget.csv`.

**What follows.**

- (a) **The judged block is late development for persistence**: the sided follow effect has been read on it (S1, S3),
  and so has the base opening's won share at 3R, pooled.
- (b) **What is new** is the side-symmetric 3R lift of an ex-ante state over a placebo selection at the offer level, and
  its value at the openings a waiting account actually takes. Neither has been read.
- (c) S2 is the nearest prior; this family names it and differs from it in the outcome read (3R per offer, not
  campaign growth over every trade), the selection (one place timed, not every account's offers removed) and the
  comparison (a placebo of the same strata).

## 3. Contract fit and conduct: the constraints every cell lives inside (CHARTER section 4)

| constraint | how the family meets it |
|---|---|
| latency, at least 5 minutes, hand entry (D-266; E-008) | **a state at mark m is an alert at t = m - 5 and reads only bars stamped at or before m - 6** (closed by t; feature-rules 1). The entry is P-16's: market at the first bar opening at or after the mark, one tick adverse. No automated or API entry |
| one position per firm, five minutes flat (D-429) | the engine's strict router, as P-16's, unchanged |
| one trade an account a session | P-16's (its registration section 3), unchanged |
| resolution (D-212, D-308) | K2 on the choice block (a kill), floor (i) on the judged block, at 3R, overall and every year |
| realised risk (D-212 (1), D-308) | the stop is P-16's 150 ticks and the opening's size the table's; read in its allowance-capped form (E-022 (1), E-032) |
| stop band and cost floor (`stop_band.csv`; D-271 (3)) | 150 ticks, above the 45-tick floor |
| news (D-525, D-533; E-007 (d)) | P-16's cuts unchanged (a report day's marks before 07:30 CT dropped, then every report-day entry before 07:35 CT); FOMC days excluded. **This family chooses no report-day entry before the 07:40 mark**: E-007 (d) puts report-day entries strictly after 07:35:00, and P-16's 07:35 mark enters at 07:35:00, on the stated end of Topstep's Tier 1 window (07:25-07:35 CT; the audit's U7 (a), `docs/audits/phase0/E_rules_currency.md`) -- the safe reading. On a report day the population starts at 07:40, so s1 can pick a mark after the 07:30 release -- **the twin's strata include the day kind, so the selection cannot win by choosing report days** (7.1) |
| ISM (09:00 CT) and GDP (07:30 CT) | not on any calendar on disk. An overnight opening can be held into ISM at the table's size, and on a GDP day P-16 enters at the release bar (E-021 (3)): **inherited from P-16; Q-39's reading decides it for P-16 and this family alike**. No state reads a release (every state reads bars before its alert) |
| the 08:30-09:00 window (Stage 2 D-281 (3); E-030) | **no entry of this family's choosing falls there** (the population ends at the 08:25 mark), and **no state reads a bar of the alert's day stamped 08:30-08:59** (the latest alert is 08:20; 6.1, T-2). A fallback opening (after W) may be a window offer, as P-16's own are |
| no time stops (D-212 (2)) | none. The wait chooses an entry; it never ends a trade |
| conduct tier 1 (D-145) | no hedging (one position across the firm); no simulator-fill exploitation (37.5-point brackets held hours); no maximum size into major news (above); no copying across accounts (D-157); nothing concealed: the rule is a published state on closed bars |
| conduct tier 2 (D-289) | as P-16: the Responsible Trading Program's placement off in the base case, on beside |
| conduct tier 3 (E-013 (1)) | the opening's size is already priced under Terms of Use s.8; 0 % denial in the verdict, 10, 25 and 50 % beside (Q-17's adapter) |
| firm rules | none loaded by the family; the engine runs Stage 2's verified ledger as P-16 does |
| the breakeven move (E-013 (2)) | allowed as made; P-16's walk; Q-20's corrected moves beside |

## 4. Data, blocks, the seal and the disclosed pre-reads

1. **Data:** Stage 2's NQ 1-minute bars (licensed, uncommitted, `vendor/DATA_MANIFEST_stage2.sha256`), 2020-01-02 to
   2026-07-16 only. Labels from this repository's walker (`extended/walker.py`, E-011), not Stage 2's `data/atlas`.
2. **The blocks:** choice 2020-01-02 to 2023-12-29; judged 2024-01-02 to 2026-07-16. Stages A and B read
   2021-01-04 to 2023-12-29: 2020 serves the states' warm-up (22 sessions for the HAR terms, at least 120 for the
   thirds) and u3's first training fold; **no lift is read on 2020**.
3. **The seal (E-026 (2)).** Every bar and walk read goes through `extended/reader.py`. The judged block is read only
   under the purposes on section 19.1's line, from a clean run of a committed tree, once each; each read appends to
   `results/read_ledger.jsonl` first. Choice-block reads need no tag; this file names them anyway: `fit_forecast`
   (u3's fit), `stage_A_supply`, `stage_B_choice`. The reader refuses any choosing or fitting purpose on the judged block
   whatever this file says. T-3 is the second proof: the choice stages' outputs are unchanged when the judged block is
   replaced.
4. **Disclosed pre-reads** -- inputs fixed or read over 2020-2026 that T-3 cannot see:

   | input | what it is | can bias | cannot bias |
   |---|---|---|---|
   | P-16's offered marks (D-525 (4), whole window) | the population's marks | that the population is "marks whose 3R walks resolve on average" -- common to every arm | the state's selection within a stratum |
   | P-16's per-R bounds (the bound arm's shift), estimated over both blocks | a constant per R | the level of every campaign number, design and twin alike | the lift (computed on net R before any shift) |
   | `u_value_map.csv` (D-668) | `mean_dv` at place (c) | C2's dollars and stage B's ranking | the lift or its bound |
   | `u_xfa_day_budget.csv` `opening_trade` (via the handoff) | the base opening's won share, pooled | the decision to propose the family | the state's selection |
   | S2's readings (D-582) | volatility and trend gates on P-16's marks | the choice of states (disclosed in 6.3) | the pick, the lift |
   | Q-35's counts, if run before the pin | where the base's openings fall, both blocks | nothing of the lift (counts only) | -- |

5. **No NQ from 2026-07-17** is on disk or read (section 15).

## 5. The base, the population, the walk and the design

### 5.1 The base

P-16 exactly, as registered and as this repository's identities reproduce it (E-004's gate paths; E-010's U1 start
rows):

- the coin `rc_s150_all_nr`: one fair coin per (date, mark), seeded 20261102 (`resolved_coin.coin_table`);
- the stop 150 ticks, every quarter R to 3R walked, Stage 2's costs (`fee_by_stop`);
- a report day's marks before 07:30 CT dropped, then every report-day entry before 07:35 CT (D-533 (2));
- the day kinds `n` and `b` (FOMC days, early closes and empty days out);
- P-14's money side: the no-closure table, 20 purchases in 21 sessions, the strict router at five minutes, five seats,
  **routing `able`** (D-318: each trade to the longest-waiting account that can take it,
  `vendor/stage2/config/fv3_corrected_portfolio.yaml`), one trade an account a session;
- the registered trades' content hash `rc150_dev_test.TRADES_SHA256`.

### 5.2 The population: P-16's overnight offers

- **Marks:** every five-minute grid mark P-16 offers from **17:00 to 08:25 CT** (on a report day, from 07:40: E-007 (d)
  puts report-day entries strictly after 07:35:00, and P-16's 07:35 mark enters at 07:35:00 itself, so it is never
  chosen here; a fallback opening may still take it, as P-16 does) -- every
  P-16 mark before its opening-window marks. Fixed as a time range and P-16's admitted set (D-525 (4)), not re-read from
  any table; T-4 checks it against the builder.
- **Sessions:** P-16's walked sessions, after the warm-up (4 item 2).
- **The offer:** at mark m of day d, P-16's market entry at the first bar opening at or after m, one tick adverse; its
  side for the design the registered coin's at (d, m); **walked long and short** for the estimand.
- **Not in the population:** the marks 08:30-09:00 (P-16's own, inside D-281 (3)'s window: unchanged, never chosen by
  this family); the marks from 09:05 (refused by P-16's cutoff; family R's population).
- **Per cell**, an offer at a mark where the cell's state is not defined (s1 and s2 before the 17:30 mark; any offer
  without enough history) is not in state.
- **The strata** g = (mark, day kind, calendar year): what the twin matches (7.1).

### 5.3 The walk and the labels

- **The walker:** `extended/walker.py`, preset **`STAGE2`** (E-011): P-16's own walk -- FV3's rung walk, a stop on a
  touch, a target on a trade through, stop first on a two-barrier bar, the breakeven move, the walk's end the bar ending
  15:08 CT and the flatten at the worst of the bars ending 15:08-15:10 less two ticks, Stage 2's costs.
- **Kinds:** stop, target, flatten (unresolved), breakeven. "Unresolved" means the flatten kind.
- **The values at R = 3** for offer i: the long's net R l_i, the short's net R r_i, and the **side-symmetric value**
  **c_i = (l_i + r_i) / 2**: the coin's expected net outcome at offer i without its noise (F-01's convention for a twin's
  expectation; family R's draft 5.3).
- **Only R = 3 is read** for any cell's lift: the opening's ask (the table's fresh funded state, handoff 2.5). C2's
  beside reading of the other places uses each trade's own R (7.4).

### 5.4 The design: the waiting opening

- **Who waits.** A funded account (XFA) from its first live session until its first trade (its opening). Combines and
  funded accounts that have traded are P-16's in every respect.
- **The rule.** During its first **W = 5** live sessions, a waiting account takes **only an offer in the cell's state**.
  Under P-16's `able` routing the router asks each account, in its order, whether it can take a trade
  (`TierSizedDraw.can_take`, `vendor/stage2/propedge/campaign/sizing.py`; the router's check in `shared_days.py`
  `TradeRouter.begin_day`); a waiting account answers "no" to an offer out of state, and the router hands the offer to
  the next account in its order, exactly as it does for any account that cannot take a trade.
- **The fallback.** From its sixth live session, a still-waiting account takes its next routed offer as P-16 does,
  whatever the state.
- **What is unchanged:** the side (the registered coin's), the R and size (the table's), the router's order (the
  longest-waiting account first; a new account is stamped as of its first day, so accounts that last traded before it
  go first), the strict one-position rule, one trade an account a session, every other account's behaviour.
- **Why W = 5.** A trading week. The states fire on about a third of offers at every mark by construction (6.4), so a
  waiting account usually meets one within a session or two; s3 is a daily state and regimes of calm or turbulence last
  weeks, so a week lets a daily state fire in a typical week while capping the delay at a quarter of a month (21
  sessions). The delay's cost -- the sessions to the first payout, S3a and S3b -- is read on the scorecard, beside.
  Other values of W are variants and are dropped (8).
- **The twin design.** The same rule with the cell's drawn placebo selection (7.1) in place of the state.
- **The seam** (18.1): the gating answer wraps the vendored `can_take`; it is reached through Q-47's
  `funded_account_cls` seam (`extended/gate.py`) and the same keyword in Q-17's `extended/user_beside.py`, never by
  editing a vendored file or substituting a vendored attribute (E-002; the lesson of E-011's first run). With the state
  always on, or W = 0, the design is P-16 bit for bit (A1, refusing).

### 5.5 Where the funded openings fall: counted in stage A; what changes if they mostly fall at 08:30-09:00

**Unknown now.** No vendored file holds the marks, hours or day kinds of P-16's funded openings
(`u_xfa_day_budget.csv` section `opening_trade` has no time column; the scout's unknown 1; TASK_QUEUE Q-35, heavy,
queued). This file does not wait for Q-35.

**Counted in stage A (A2), direction-free, on the choice block:**

- From **P-16's own engine call with its day table restricted to the choice block's sessions** (2020-01-02 to
  2023-12-29; seed 20261984, 200 paths, the bound arm as U2 records), the place-recording adapter (18.1) records every
  funded opening: its (date, mark), hour, day kind, whether it is at 08:30-09:00, whether on a report day, the sessions
  from activation, and whether the offer is in each cell's state.
- The same record for each cell's design and twin design at the same seed (paired day tables), plus each opening's wait
  and whether it was a fallback.
- **Counts only:** no net R, gross, won share, growth or any outcome is read or written. The campaigns compute
  outcomes internally to evolve the accounts; nothing of them leaves the run except the routing records.
- Written to the result file's `openings` section before stage B reads any outcome.
- If Q-35 has run before the pin, its counts over both blocks are a disclosed pre-read (4 item 4); **the rules here use
  stage A's count only**.

**What changes if most of P-16's choice-block openings fall at 08:30-09:00** (more than half: the trigger for the
record, not for any rule):

1. **No rule of this file changes.** The cells, the twin, C1 (offer-level, on the overnight population) and C2 (on the
   design's own openings) are fixed now; the count can move nothing.
2. **The design moves most openings out of the window into the overnight.** That is a change of schedule. The twin
   design shares it (its openings are overnight too), so it is not credited to the selection (E-023: "supply and
   schedule cancel"). The twin design against P-16 on the scorecard (13) shows the move's own effect on a user, and the
   stage-A record shows how far the openings moved.
3. **Reach.** Openings in the window would mean the overnight offers mostly go to longer-waiting accounts first (a new
   account is stamped as of its first day). A waiting account would then be offered few overnight offers, its wait
   would lengthen and **K5 (the fallback share, A7) decides** whether the cell is the declared rule at all. Fallback
   openings may themselves fall in the window, as P-16's do.
4. **The value.** C2 prices the design's own openings, so a window-heavy base changes nothing in its rule. But `mean_dv`
   at (c) is the map's average over P-16's openings wherever they fell; it does not know the mark. If those were
   mostly window openings, the design's overnight openings are priced by a value learnt on window openings -- **an
   assumption that carries money, reported beside the verdict**.
5. **Resolution and the slot.** An overnight 3R opening has hours more to resolve than one entered at 08:30-09:00, so K2
   and the floor are not harder; but it holds the firm's single position slot through the night and morning (D-429),
   which the scorecard's supply reading shows (the minutes the slot is held by openings, other accounts' sessions
   without a trade).
6. **The question it would raise, which this family does not ask.** The window would then be where a timing filter has
   most of its uses, and acting there is inside Stage 2 D-281 (3)'s closed branch, reserved to the operator. A family
   timing openings at 08:30-09:00 (its states frozen at the 08:25 alert, so that no window bar is read) is a
   **different family**, needing the operator's D-281 (3) ruling first. The lead records the count and that question
   under a row. This family runs as declared whatever the answer.

**If most fall overnight,** the design times openings within their own hours, the move is small, and the comparison
with the twin is mostly the selection. **On report days**, s1 is expected to fire after the 07:30 release; the count
reports the share of each design's openings on report days.

## 6. The states: the cells

### 6.1 The clock, and what a state may read

- A trading day opens at 17:00 CT the evening before (the store's rule); a slot is minutes after that 17:00
  (`extended.features.slot`); Chicago wall clock throughout, so a DST change moves no slot.
- A bar stamped hh:mm covers hh:mm:00-hh:mm:59 and closes at hh:mm + 1. **At mark m the alert is t = m - 5, and a state
  reads only the day's bars stamped at or before m - 6 and the bars of earlier sessions** (feature-rules 1).
- **The latest alert is 08:20** (the 08:25 mark): no state reads a bar of the alert's day stamped 08:30 or later, so the
  window E-030 keeps out of family B is unreachable here (T-1 shows the clock; T-2 proves it on the code).
- **Earlier sessions' bars, their 08:30-08:59 included, enter only the daily volatility terms** (H in s2 and s3, IV in
  u3), as family B's third draft, which E-030 merged, reads earlier sessions (its `atr14`, `range_prior`; its rule is
  that "no used feature reads a bar stamped 08:30-08:59 **of the alert's day**", its section 0.1). Recorded as an
  interpretation (20).
- **The library where it serves.** `extended/features.py` computes its features at RTH alerts only (08:30-15:00; its
  `compute` refuses others), so none of its columns is used as is. Reused, never copied: its `grid` (the bars as day x
  slot arrays), `slot`, its trailing-median helper (for x3's slot median), and `rv_tod`'s formula, which x3 extends to
  overnight alerts (T-2 asserts the equality at RTH alerts, where the library computes it).

### 6.2 Common quantities

Every quantity is a log ratio of prices **within one trading day**, so it is scale-free (feature-rules 2: no raw level)
and never differences prices across a roll. Every window runs over **P-16's walked sessions** (S2's reading, D-581 (5)).

| quantity | formula | reads |
|---|---|---|
| LR(d) | ln(max high / min low) over day d's bars (17:00-15:59) | day d's bars; used only on later days |
| LRS(d, m) | ln(max high / min low) over day d's bars stamped 17:00 .. m - 6; defined with at least 15 bars | day d's bars up to m - 6 |
| DIS(d, m) | abs(ln(close of the last bar stamped at or before m - 6 / open of day d's first bar)) | day d's bars up to m - 6 |
| har(x)(d) | (x(d-1) + mean of x over d-5..d-1 + mean of x over d-22..d-1) / 3: an **unfitted** HAR-type mean (Corsi 2009's daily, weekly and monthly terms, equal weights -- the scout's "HAR-type mean"); defined with 22 prior values | the 22 prior sessions |
| H(d) | har(LR)(d): the day's forecast range | the 22 prior sessions' whole days |
| HS(d, m) | har(LRS(., m))(d): the forecast of the range so far at mark m | the 22 prior sessions' same window |

### 6.3 The four states

| cell | state | quantity X | in state when X's share (6.4) is | defined from | reads (all closed by the alert) | sign (1 (iv)) |
|---|---|---|---|---|---|---|
| **s1** | unexpected volatility | U(d, m) = ln(LRS(d, m) / HS(d, m)) | **above 2/3** | the 17:30 mark | day d's bars 17:00 .. m - 6; the same window of the 22 prior sessions; U at m over the 250 prior | positive |
| **s2** | a night already trending | T(d, m) = DIS(d, m) / H(d) | **above 2/3** | the 17:30 mark | day d's first open and its close at m - 6; the 22 prior whole days; T at m over the 250 prior | positive |
| **s3** | low predictable volatility | H(d) (a daily state: every mark of the day alike) | **below 1/3** | 17:00 | the 22 prior whole days; H over the 250 prior | positive |
| **u3** | the offer forecast fast (family R's (u3)) | y_hat(d, m), section 6.5 | **above 2/3** | 17:00 | 6.5 | negative |

Notes, each a disclosure or a recorded interpretation:

- **s1 against the scout.** The scout's forecast was the same mark's median over the 20 prior sessions. Here it is the
  HAR mean of the same window (1, 5 and 22 sessions), so a rise over the last few days counts as predictable, not as a
  surprise. That is closer to Bianco & Renò's split of realised volatility into its expected and unexpected parts.
- **s2 against the scout.** "Above a declared multiple" is replaced by the mark's top third: DIS grows with the time
  since 17:00, so any fixed multiple would fire mostly late in the night and make the state a clock. The twin cancels
  the clock anyway; the third keeps the firing share even across marks.
- **s2 and s1 against S2 (D-581).** S2's trend state compared abs(c[t] - session open) with its trailing 20-session
  median at the mark; s2 normalises it by the day's forecast range and ranks it over a year, top third. S2's volatility
  cells ranked the last 30 bars' range; s1 ranks the whole night's range against its forecast. Relatives, redefined;
  S2's readings are seen (2).
- **s3.** Calm days resolve slowly: S2's low-volatility cell failed resolution at the longest offered R in its worst year
  (D-582 (2)). K2 kills s3 on resolution before any lift is read.
- **u3.** The mirror of s3 in its predictable part, with today's surprise so far added (x3). Under the twin's strata,
  in-state and out-of-state deviations sum to zero within a stratum, so s3's and u3's lifts are related; both are
  counted, and the stage-B critical value is computed jointly (10).
- **No state reads a side, an outcome, a calendar beyond P-16's day kinds, or a price level.**

### 6.4 The rolling third

- For a quantity X at mark m (or daily, for s3), its **share** p(d, m) = (the number of the 250 prior walked sessions'
  values of X at m that are below X(d, m), plus half the equal ones) / their count -- S2's mid-rank rule (D-581 (6))
  over a year instead of a month. At least 120 prior values, else undefined (not in state).
- "Above 2/3" and "below 1/3" are strict.
- **Why 250.** A year's reference: "low" in s3 means low for the past year, not for a calm quarter. For the ratios of
  s1, s2 and u3 the window hardly matters.
- **It is a past-only normaliser** (feature-rules 2: "rolling or expanding windows ending at t - 1 min"), computed the
  same way at every session from bars alone. No value of it is chosen from data or read from an outcome. It fires on
  about a third of offers at every mark by construction (T-1 shows it on an iid series). On the judged block its
  reference reaches back into 2023: that is the past, not a fit.

### 6.5 u3's forecast: the only fitted values, inside the choice-block walk-forward (E-031 (1))

Restated from family R's draft (section 6) so that this file stands alone. If family R is pinned first, the two
procedures must be the same code (T-7).

- **The target** (a label, used only for fitting, never as a feature): IV(d, m) = the sum of squared one-minute price
  changes, in points^2, over day d's bars from the entry bar (stamped m) to the bar ending 15:08 CT (the first change
  that bar's close less its open, then each present bar's close less the previous present bar's close); M(d, m) = the
  mean of IV(d', m) over the 22 prior walked sessions with a value; y = ln(IV(d, m) / M(d, m)).
- **The regressors**, each closed by the alert:
  - x1 = ln(IV(d - 1, m) / M(d, m)), yesterday's same window;
  - x2 = ln(mean of IV over the 5 prior sessions / M(d, m)), last week's;
  - x3 = 2 x `rv_tod` at the alert t = m - 5: ln((rv_60 / its median over the 20 prior sessions at the same slot)^2),
    rv_60 the root mean square of one-minute close changes over the bars stamped t - 61 .. t - 1; at least 10 sessions
    for the median, else missing.
- **Bands** (family R's 6.3, the overnight ones): `evening` 17:00-17:55 (x1, x2: under an hour of the day's bars);
  `asia` 18:00-01:55 and `london` 02:00-08:25 (x1, x2, x3). Family R's `open` and `day` bands are not used (no population
  mark lies there).
- **The fit:** ordinary least squares of y on an intercept and the band's terms, one observation per (session, mark),
  weight one: 3 + 4 + 4 = **11 coefficients**. Deterministic; refused if a band's design matrix is rank-deficient (the
  failure protocol).
- **The walk-forward, inside the choice block only:** test years 2021, 2022 and 2023, each fitted on the choice block's
  sessions before it less the last 22 (expanding; the first fold trains on 2020 after its warm-up). A forward walk needs
  no purge: every IV ends at 15:08 of its own day. Out-of-fold forecasts feed stages A and B.
- **The final fit:** every choice-block session with a value. Its coefficients are serialised to canonical JSON and
  hashed; **the hash is pinned in a decision row before the judged block is read**; the judge's entry point cannot fit
  (T-9). Nothing is fitted, chosen or tuned on the judged block.
- **y_hat's share** (6.4): the 250 prior sessions' y_hat at the same mark, each computed with the same fit as day d's (in
  a test year that fold's; on the judged block the final fit). Every input precedes d.
- **No calibration** (family R's 6.4 maps the forecast to a probability; here only its rank matters), so the 10
  calibration values family R fits are not fitted here.

## 7. The twin and the estimands

### 7.1 The twin (E-023 (2))

- **The placebo-selection twin:** a random filter that fires on **the same number of population offers as the cell's
  state in each stratum g = (mark, day kind, calendar year)**, drawn uniformly without replacement, seeded
  `default_rng([20261982, c, b])` (c the cell's index, 0 to 3 in the order s1, s2, s3, u3; b the block: 0 judged, 1
  choice, 2 the confirmation).
- So the time of day, the report days and the year cancel, as supply and schedule do, and **only the state's choice of
  day within a mark is measured**.
- **What it does not match:** the state's clustering over marks and sessions (the placebo fires independently offer by
  offer). The statistic's dependence on that clustering is section 11's business; the twin design's waits (shorter,
  because the placebo does not cluster) are reported in stage A, and section 13 says what that does to the scorecard.

### 7.2 C1's estimand: the lift over the twin at the offer level

    L_c = (1 / N_F) x sum over the cell's in-state offers i of ( c_i - mu_g(i) )

- mu_g is the mean of c over **all** population offers of stratum g -- the placebo's exact expectation; mu_g(i) is that
  of offer i's stratum; N_F the number of in-state offers. (s names a session throughout, g a stratum.)
- L_c is exactly the expected difference between the in-state offers' mean and the twin's, without the twin's draw noise
  (T-1 holds the identity on synthetic offers). F-01 and family R's draft do the same; the seeded draw is reported
  beside (`[20261982, c, 0]` on the judged block).
- **The session series:** z_s = the sum over the cell's in-state offers on session s of (c_i - mu_g(i)), so
  L_c = sum of z_s / N_F. The judging statistic tests this series (11, 12).
- *Interpretation for the lead (as family R's 7.2):* if E-023's word "seeded" is read as requiring the drawn twin in
  the line, C1 runs on the drawn twin and the exact form goes beside. This file fixes which before the pin.

### 7.3 The halves

- L_c^long on l_i with its strata means, L_c^short on r_i likewise; L_c = (L_c^long + L_c^short) / 2.
- Persistence raises both. A drift aligned with the state raises one and lowers the other at first order (1 (i), T-1).
  **C3 requires both above zero.**

### 7.4 V: the value on the openings' own offers (place (c))

The value map prices a won trade by place, and the lift is valued **where the openings actually fall** (family B's
first review M-3; F-02's third review V1: price only the uses the routing reaches):

- The design's gate campaign records every funded opening j (the place-recording adapter, 18.1): the offer i(j) it took
  and whether it was in state or a fallback.
- Per session s:

      z_s^V = sum over the openings j with i(j) on session s of  mean_dv(c) x ( c_i(j) - mu_g(i(j)) ) / (1 + 3)
              / (paths x years per path)

  with mean_dv(c) = `u_value_map.csv`, section `place_values`, base `p16`, place `c_funded_opening`, measure `mean_dv`
  (a win over a loss, in dollars); to first order a lift of lambda R at 3R is lambda / 4 of win probability (the map's
  definitions).
- **V = sum of z_s^V: dollars a year of a five-seat campaign**, the value map's basis. Uses are the design's own routed
  openings, fallbacks included at their own offers' deviations.
- **Beside, an assumption that carries money:** V counts the openings only. The offers a waiting account declines go to
  other accounts, so the wait also reshuffles other places' trades. At those places the table asks mostly 1R and 1.5R,
  where persistence acts little or not at all (1 (i)), so the reshuffle's first-order cost is expected small; it is
  read beside as V_other -- the same sum over the design's trades at places (b), (d) and (e), each at its own R and
  against the mean over P-16's offers of its own stratum at that R, less the twin design's -- deciding nothing.

## 8. Parameters: fixed, fitted, searched, dropped

| parameter | what it is, in a phrase | class | value | source or reason |
|---|---|---|---|---|
| market, bars | what is traded and read | fixed | NQ 1-minute bars; MNQ micros sized by the table | E-002 |
| development window | the only data read | fixed | 2020-01-02 .. 2026-07-16 | CLAUDE.md; `config/windows.yaml` |
| choice / judged blocks | where choices are made / the one judgement | fixed | 2020-01-02 .. 2023-12-29 / 2024-01-02 .. 2026-07-16 | feature-rules 4; CHARTER 3 |
| stages A and B's span | where the choice block's lifts and gates are read | fixed | 2021-01-04 .. 2023-12-29 | warm-up and u3's first fold (4 item 2) |
| base | the design the filter acts on | fixed | P-16 as registered (5.1) | E-004, E-010 |
| stop | the loss distance | fixed | 150 ticks (37.5 points) | P-16 |
| R | the bracket the lift is read at | fixed | 3 | the opening's ask; persistence cannot act at 1R (1 (i)) |
| population | the offers a state may pick | fixed | P-16's marks 17:00 .. 08:25 CT (report days 07:40 ..) | 5.2; D-281 (3); E-007 (d) |
| entry | how a trade starts | fixed | P-16's: market at the first bar at or after the mark, one tick adverse; by hand; the alert at m - 5 | D-266; E-008 |
| walk | how a trade ends | fixed | `extended.walker.STAGE2` | E-011 |
| costs | fees and slippage | fixed | Stage 2's (`fee_by_stop`, `fills.yaml`) | E-010 |
| the states' formulas | what each cell waits for | fixed | 6.2, 6.3 | the literature (1 (ii)); the scout's 5.1 |
| first defined mark | when s1 and s2 exist | fixed | 17:30 (LRS needs at least 15 bars) | 6.2 |
| HAR terms | daily, weekly, monthly | fixed | 1, 5 and 22 prior sessions, equal weights (s1-s3) | Corsi 2009 |
| the rolling third | the state's threshold | fixed | the 250 prior sessions' mid-rank share, at least 120; above 2/3 (s1, s2, u3), below 1/3 (s3) | 6.4; S2's rule over a year |
| u3's forecast | the fast forecast | fixed form, **fitted in-fold** | 11 coefficients by least squares, three folds and the final fit | 6.5; E-031 (1) |
| u3's so-far term | today's surprise | fixed | 2 x `rv_tod` at m - 5 (60 minutes; 20-session slot median, at least 10) | `extended/features.py`; family R |
| W | the longest wait | fixed | 5 live sessions | 5.4 |
| the fallback | after W | fixed | the next routed offer, as P-16 | the scout's rule |
| routing | who gets an offer | fixed | P-16's, unchanged | 5.4 |
| strata | what the twin matches | fixed | (mark, day kind, calendar year) | E-023 (2); 3 (news) |
| the twin's form | the line's comparison | fixed at the pin | the exact expectation in C1, the seeded draw beside (7.2) | the lead's (20) |
| C1's statistic | the pass line's test | fixed at the pin | Q-16's calibrated statistic **[Q-16]**, at the larger of its and B2's critical value | E-023 (2) |
| B2 | the conditional critical value | fixed | section 11 (63-session blocks; slow component switching 1/63; at least 1,000,000 replicates) | family B's form (E-030) |
| C2's bar | the least worth | fixed | $500 a year at C1's level, on V | `u_value_map.csv` section `bar` (`target=500`); F-02, F-B |
| valuation base | where a win is priced | fixed | `p16`, place (c) | `u_value_map.csv` |
| K1 | the least supply | fixed | 21 sessions holding an in-state offer in each of 2021, 2022, 2023 | a month of sessions |
| K2 | resolution | fixed | at most 5 % unresolved at 3R among in-state offers, overall and every year; 4 % in the worst year to be eligible as the pick | D-212; family B's M2-4 margin |
| K5 | the wait binding | fixed | at most one half of a design's openings taken as fallbacks | the scout's K5 |
| MDL factor | when the family is only a screen | fixed | 3 | family B 8 item 8; family R |
| campaign paths | the campaigns' size | fixed | 200 (stage A and B, choice block, seed 20261984); 500 (stage C, seed 20261983) | U2's re-run (100); the gate (500) |
| other W (1, 2, 3, 10 sessions) | a shorter or longer wait | **dropped** | -- | each a variant; W is the rule |
| other thresholds (quarters, fifths) or a combined state (s1 and s2) | finer or joint states | **dropped** | -- | each a variant; S2's lesson (D-582: no post-hoc finer cut) |
| a sided cell (follow, fade) | a direction rule | **dropped** | -- | S1 and S3 read it (2); a direction family, judged by the coin twin |
| the 25-point US cell, 09:00-12:00 at R 2.5 | the scout's optional US-hours cells | **dropped** | -- | P-15's base and US hours; its identity is not reproduced here; a later family |
| the opening-window marks 08:30-09:00 | where P-16's openings may fall | **out of the population** | -- | D-281 (3); 5.5 item 6 |
| window offers passed through during the wait | taking 08:30-09:00 offers unfiltered | **dropped** | -- | dilutes the filter by the window's share; a variant |
| an opening-first routing priority | giving a waiting account the in-state offers first | **dropped** | -- | changes every other account's trades; a different design |
| VIX or VXN states | implied volatility | **dropped** | -- | not on disk; whether Cboe's history is free without sign-up is unverified (the scout's unknown 6); the atlas read it on 2009-2014 |
| dealer gamma | the mechanism's own variable | **dropped** | -- | S&P-only options data, a purchase (D-137) |
| family R's calibration | the forecast to a probability | **dropped** | -- | u3 uses the forecast's rank only |
| ISM and GDP day exclusions | release days not on disk | **dropped here** | -- | no calendar on disk; Q-39's reading decides it for P-16 and this family (3) |
| the reverse walk-forward | choose late, judge early | **dropped** | -- | E-031 (2): it would make the judged block choose or fit; the year-by-year readings go beside (12) |

**Searched: nothing.** The trial count is the four cells.

## 9. Stage A: the gates, before any outcome (2021-01-04 to 2023-12-29)

Stage A reads **bars** (the states, u3's forecast), the walks' **kind columns** (resolution, side-free, as D-525 (4)
does) and the campaigns' **routing records** (where openings fall). It reads no net R, gross, side outcome or growth
of any cell. Every kill is counted and recorded.

**A1. Identities (refusing).** Any failure stops the family; the failure protocol applies.

1. E-011's walker identity holds at the build's commit.
2. The population builder's P-16 cell gives P-16's trades, `TRADES_SHA256` exactly.
3. **The design with the state always on** (every offer in state) through the family's gate call
   (`extended.gate.run_gate(funded_account_cls=...)`): P-16's gate paths, 500 paths at seed 20261206, every `PATH_COLS`
   column to 1e-6 (E-004's comparison); and through Q-17's adapter, P-16's U1 start rows `p16`, both arms, every start
   (E-010's comparison).
4. **The design with W = 0**: the same two comparisons.
5. Q-47's registered-path gate identities at 500 paths (E-028 (3), owed under the lock) and Q-17's adapter identity
   (`identity/user_beside_identity.py`) have held.
6. The place-recording adapter's identity (18.1 item 4).

**A2. Where the openings fall (5.5).** The counts for P-16, each cell's design and its twin design, written to the
`openings` section: by mark, hour, day kind, the 08:30-09:00 share, the report-day share, the sessions from activation,
the in-state share of P-16's own openings, each design's wait distribution and fallback share. Counts only.

**A3. No look-ahead (refusing).** The states' and u3's shift-invariance test (T-2): every bar stamped at or after
m - 5 is replaced by a seeded random walk (`[20261981, j]`), and separately deleted; every state at (d, m) and every
y_hat must be unchanged, at no fewer than 200 (session, mark) cuts including the first marks after 17:00 and 17:30, a
roll day and a DST change; replacing the alert day's 08:30-08:59 bars changes no state (E-030). No state all-undefined
or constant.

**A4. u3's forecast skill (a control, not a kill).** On 2021-2023 out of fold, per band: the per-session mean squared
error of y under the HAR against under y = 0. The improvement's one-sided 95 % lower bound must be above zero, by
circular 21-session blocks, 2,000 draws (`[20261980, 0]`), in every band. A fail means a defect or a market without the
stylised fact: the failure protocol runs, and u3 waits for the lead's ruling under a row.

**A5. Supply (K1, a kill).** For each cell: in-state offers per session, by year, hour and day kind; the in-state share
per stratum (about a third by construction). **A cell with fewer than 21 sessions holding an in-state offer in any of
2021, 2022 and 2023 is killed.**

**A6. Resolution (K2, a kill).** Among each cell's in-state offers, both sides pooled, the unresolved (flatten-kind)
share at R = 3 must be **at most 5 % overall and in each of 2021, 2022 and 2023**. Else the cell is **killed**. Reported
beside: the same for the whole population, and each cell's worst year (stage B's 4 % eligibility margin).

**A7. The wait (K5, a kill).** On the choice-block campaign, **a cell whose design takes more than one half of its
openings as fallbacks is killed**: it is not the declared rule. Reported: the wait distribution, the twin design's wait
and fallback share (expected shorter: the placebo does not cluster, 7.1).

**A8. Realised risk.** The openings' realised risk against intended in P-14's registered allowance-capped form (E-022
(1), E-032). A build check: the table's sizing is unchanged.

**A9. Power on record.**

- For each surviving cell: the minimum detectable lift (MDL) of C1 at the family's level on the judged block, at 80 %
  power, from Q-16's power function **[Q-16]**, or from section 11's machinery at the judged block's session count with
  the cell's choice-block in-state pattern and the population deviations' dispersion on the choice block (never the
  in-state mean, which stage B reads first).
- The bar in net R: lambda_bar = 4 x $500 / (mean_dv(c) x u_c), u_c the cell's design's in-state openings a year on
  the choice-block campaign (A2).
- **If the MDL exceeds 3 x lambda_bar at every surviving cell, the family is declared a screen** (section 14 says what
  its pass means). Written before stage B reads any lift.

## 10. Stage B: choose on the choice block (2021-01-04 to 2023-12-29)

1. **The statistic.** For each cell surviving stage A, L_c (7.2) on the span, the strata (mark, day kind, year) within
   it, u3 with its out-of-fold forecast.
   - Its bootstrap: a stationary bootstrap of sessions, **mean block 63** (the judging lines' dependence), 2,000 draws
     (`[20261980, 1]`), each draw recomputing L_c, the strata means included, on the resampled sessions.
   - SE_c its standard deviation over draws.
   - The family-wise critical value q_B: the 95th percentile over the centred draws of max over cells of
     (L\*_c - L_c) / SE_c (one-sided 0.05). Benjamini-Hochberg at 10 % beside, never selecting.
2. **Kill B:** no eligible cell with L_c / SE_c > q_B. The family **closes** and the judged block is not read.
3. **Eligible as the pick:**
   - K2's margin: at most 4 % unresolved at 3R among its in-state offers in its worst year;
   - **both halves positive on the span** (C3's choice-block form: L_c^long > 0 and L_c^short > 0);
   - K1 and K5 passed.
4. **The pick:** among the eligible cells above q_B, the largest lower limit of **V_B**, the choice-block form of V (7.4)
   on the choice-block campaign's openings (seed 20261984, 200 paths): V_B - q_B x SE(V_B), its SE from the same
   bootstrap with the routing weights held fixed (`[20261980, 2]`). Ties go to the cell listed first (s1, s2, s3, u3).
   This is the value where the openings fall, not a uniform lift over the cell's offers (M-3).
5. **Reported for every cell before the pick:** L_c and its halves, by year; the kind shares of the in-state offers
   against their strata; L_c under the `close` flatten convention; V_B's in-state and fallback parts.
6. **What it spends:** nothing of the program's level. One cell reaches judgement.
7. **The record:** every cell's stage A and B readings are written to the result file's `choice` section before the
   judged block is read.

## 11. Stage B2: the critical value, conditional on the judged selection (family B's form, E-030)

**Why.** The states cluster: s3 is a daily state whose calm regimes last weeks; s1 and s2 persist through a night; u3's
forecast moves slowly. So the in-state offers sit in long runs of sessions. A slow component of the deviations that the
strata do not remove (anything inside a calendar year) aligns with such runs by chance more often than with a selection
that does not cluster. Family B's third draft found that resampling one realisation -- its second review's own
remedies -- cannot certify the family's level against that, and kept the failed check on record (E-030); so the
critical value here is conditional on the actual judged selection and widened by a declared slow component, as family
B's is.

1. **The statistic for every judging line** (C1 and C2): Student-t on **63-session block means** of the line's
   per-session values (about 10 blocks on the judged block). Q-16's statistic is used if it is merged in this form, with
   its own calibration **[Q-16]**.
2. **B2's null at stage C, conditional on the pick's real judged selection** (read under `stage_C_states` and hashed
   before any outcome is read):
   - **The deviations:** each null replicate d\* is built from the choice span's own per-offer deviations
     c_i - mu_g(i) at 3R (every population offer, 2021-2023), at the session level:
     - resampled by a stationary bootstrap with **mean block 63 sessions** to the judged block's session count;
     - each judged session's offers take the drawn session's deviations at the same marks (a missing mark dropped);
   - **plus a declared slow component** a\* x rho_t: rho_t a two-state Markov sign switching with probability 1/63 per
     session (a random start), a\* the largest absolute mean, over the choice span's disjoint 63-session blocks in
     session order, of the per-session mean deviation;
   - **then re-centred within the judged strata**, so the twin's expectation is zero exactly in every replicate;
   - the line's statistic recomputed with the real judged selection (for C2, with the judged campaign's routing weights
     held fixed, read under `stage_C_campaign`);
   - **draws** `default_rng([20261985, line, j])`, line 0 for C1 and 1 for C2, at least **1,000,000 replicates** per
     line (light in memory; CPU minutes to hours).
3. **The critical value: always the larger of the nominal (or Q-16's) and B2's (1 - level) quantile** -- no tolerance,
   no pretest.
4. **What it cannot see:** a slow component slower or larger than the declared one. The confirmation on unread data
   carries the decision against it.
5. Fixed now. T-10 holds its size on a synthetic clustered selection.

## 12. Stage C: judge the pick once, on the judged block (2024-01-02 to 2026-07-16)

**The judge's inputs:** the pick (from stage B's result file, by its sha256, T-9); u3's frozen forecast by its pinned
hash, if u3 is the pick; the strata within the judged block. **In order:** `stage_C_states` (bars: the selection and
the strata counts, hashed) -> B2 for C1 -> `stage_C_judgement` (the walks' net R at 3R, both sides: L, the halves) ->
`stage_C_campaign` (the design's, its twin design's and P-16's paired gate campaigns; the routing records; B2 for C2; V;
the floors) -> `stage_C_scorecard` (13).

**The design passes only if every line holds. A fail of any line closes the family**, its reason in a decision row.
Each line at the family's level 0.05 / (k (k + 1)):

- **C1, the pass line (E-023 (2)):** L over the judged block's in-state offers; **its one-sided lower bound above zero**
  by Q-16's calibrated statistic for the placebo-selection comparison **[Q-16: its name, module and commit; E-023 asks
  Q-16 to calibrate it]**, at the larger of its critical value and B2's. This file is not pinned until Q-16 is merged.
- **C2, worth something where it is used:**
  - the design's gate campaign on the judged block's sessions: 500 paths, the bound arm, seed **20261983**;
  - **the bound arm's shift is P-16's registered shift at each R**, for the design, its twin design and P-16 alike:
    every trade is a P-16 coin trade walked the same way, so a pair differs only by the wait (family R's choice; the
    alternative, each design's own bounds by the era rule, would be re-estimated over both blocks and move with the
    selection);
  - **V's one-sided lower bound** (7.4; the session count times the lower bound of mean(z^V) by C1's statistic at the
    larger of its and B2's critical value, the routing weights held fixed) **at least $500 a year**. This is CHARTER
    section 3's "its value at that bound", priced on the openings the design takes.
- **C3, both sides:** L^long > 0 and L^short > 0 on the judged block (point estimates). A persistence lift raises both; a
  lift carried by one side is drift (1 (v) (b)) and closes the family.
- **The floors (CHARTER section 3; E-022), all on the design's own judged-block run:**
  - (i) **resolution:** the pick's in-state offers unresolved at 3R at most 5 %, overall and in each of 2024, 2025 and
    2026 to 07-16 (a year with fewer than 63 sessions pooled with its neighbour, D-604); the share of the design's taken
    trades flattened at most 5 % overall and in each year;
  - (ii) realised risk in P-14's registered allowance-capped form (E-022 (1), E-032);
  - (iii) **the long-run gate:** growth on the required bankroll at the bound above zero, on this design's own campaign
    (seed 20261983), never taken from P-16's registered pass (E-022 (2));
  - (iv) every firm rule verified (Stage 2's ledger);
  - (v) conduct tier 1 (section 3).
- **Beside, deciding nothing:**
  - L and its halves **by calendar year on each block** (the place the reverse walk-forward held, E-031 (2));
  - the kind shares of the in-state offers against their strata, and the **kind decomposition** of L: the part from the
    target share's change at fixed costs, and the part from the kinds' cost composition (1 (v) (c));
  - **L under the `close` flatten convention** (`DECLARED_F01`'s flatten, the other rules `STAGE2`'s): how much of the lift
    is the flatten convention;
  - L under Q-20's corrected moves (`STAGE2_BE_BOTH`, merged b7232ba);
  - the seeded twin's draw (`[20261982, c, 0]`);
  - V's parts (in state, fallback), **V_other** (7.4), and the uniform-lift valuation (C1's bound x the openings a year x
    mean_dv(c) / 4) beside V;
  - the share of the design's openings on report days and by hour; the in-state share of P-16's own judged openings;
  - u3's judged forecast skill, if u3 is the pick;
  - Stage 2's S-program guard (the design's paired growth at the bound against P-16's, D-568 (2)), never a line.

**Dropped (E-031 (2)):** the reverse walk-forward.

## 13. The journey scorecard -- beside, never the pass line (CHARTER section 2; E-008, E-014, E-015, E-023)

**Which designs.** Read for the pick only, after stage C has read, whatever its verdict. A family closed at stage A or
at Kill B reads none.

- **The design** (P-16 with the waiting opening at the pick's state), **its twin design** (P-16 with the waiting opening
  at the pick's drawn placebo, `[20261982, c, 0]`), and **P-16**, paired (the same starts, coin and seeds), with R\* =
  P-14 beside.
- **What each pair shows.** The design against its twin is the selection's journey effect -- mixed with the difference
  in waits, because the placebo does not cluster as the state does (7.1); the waits of both are reported beside it. The
  twin design against P-16 is the wait's and the move's own effect (5.5 item 2).
- Journeys from the vendored U1 replay through Q-17's adapter (`extended/user_beside.py`), with the family's account class
  passed as its `funded_account_cls`.

**On which starts.** The judged block's starts (`stage_C_scorecard`), labelled as such; beside, 2021-2023's starts (a
choice-block read, u3 out of fold), **purged by horizon per measure** so that no choice-block journey reads a
judged-block session (Stage 2's `u_select.block` purge, the F-P review's F6); 2020 is not read for it.

**What is read.**

- **P** and the guarded measures S1, S3a, S3b, S3c (with its components: a won funded opening, the five winning days
  after it), S4a, S4b, S5a, S5b, S5c; the reported-only S2, S3d, S6, Q (`vendor/stage2/docs/USER_MILESTONES.md`). S3c
  is compared within one trade stream (E-008): the three designs share P-16's offers.
- **The journey variables (E-014):** sessions and cash to the first pass; sessions and cash to the first payout;
  **sessions to break-even** (the first session whose cumulative net cash is at or above zero, daily), the share of
  starts reaching it by months 1, 2, 3, 6 and 12, and the share that later fall back below zero; **the path's
  evenness** -- the share of months with a positive net change, the longest run of months without a payout, the spread
  of monthly net, the deepest fall of cumulative net from its running high after break-even, payouts per month, the
  largest single month's share of the year's payouts.
- **The wait, as a user feels it:** the sessions from activation to the opening; the openings' hours; the minutes the
  firm's slot is held by openings; funded trades per live account-day and the share of account-sessions without a
  trade, against P-16's.
- **Every measure as a distribution over start days** (median, p10, p90), with its uncertainty from the effective number
  of independent starts and the start day's share of the variance (`user_drivers.csv` section `design_vs_luck`).
- **The paired readings:** the per-start difference against P-16 and against the twin design as distributions, and the
  shares of starts better, equal and worse at months 1, 2, 3, 6 and 12. Draws from `[20261987, 0]`.
- **The frontier** on P, S1, S3a and S5a; **the menu** under E-015's limits once the operator approves them, as **flags
  only** (a limit never fails a design, E-015 (3)); **the evenness trade-off curve** (E-015 (4)).
- **E-007 (e)'s readings** (Q-17's adapter): the denial ladder at 10, 25 and 50 % (draws `[20261987, 1]`); the placement
  on; the binding Focused Trader models; all-accounts forfeiture; P by month, mean net, CVaR10, P under a bankroll limit,
  the effective sample size and the minimum detectable difference.
- Stage 2 D-621 (3)'s rule against P-14, beside as E-008 keeps it, deciding nothing.
- **Not modelled, said wherever the scorecard appears:** a user who stops when their own money runs out, the user's
  time, taxes.

## 14. What a pass and a fail mean

**CARRIED** (every line of stage C and every floor holds):

- a development finding on a late-development block;
- the design -- P-16 with the opening waiting at most five sessions for the pick's state -- takes a registration id
  (Stage 2 D-621 (9)'s house form), a model card if the pick is u3 (`vendor/stage2/prereg/MODEL_CARD_TEMPLATE.md`: the
  forecast's coefficients), its registered development test, the auditor and **one confirmation** (section 15), which
  carries the decision (D-189);
- if stage A declared the family a screen, a pass is still CARRIED, and the carrying row says the development read was a
  screen at its MDL ratio;
- **a u3 pass contradicts its stated sign.** It carries like any pass only if every line holds; the carrying row says it
  runs against the LeBaron prior, and the beside readings (the `close` convention, the kind decomposition) say whether
  its lift is the flatten cost avoided (family R's mechanism) or the surprise term's persistence;
- what a user is told is the scorecard as a distribution (13), never one number.

**CLOSED** at stage A (an identity fails, or every cell is killed; A4's control failing holds u3 for the lead's ruling
and closes nothing by itself), at B (Kill B), or at C (a line or a floor):

- the reason goes in a decision row;
- a close at B or C reads **"no selection lift above the MDL at this family's level"**, never "timing does not help";
- **the closure binds** (D-277's boundary): a later family on these states or this population names this closure, says
  what changed and why it is a different hypothesis, and is not judged on this family's judged block.

## 15. The confirmation, declared before any development read

- **The window:** NQ from **2026-07-17** (`config/windows.yaml`, `reserve`). Not on disk, never read until a carried
  design is registered. **A purchase, the operator's**, stated in `docs/OPERATOR_SETUP.md` and waited for; it would be
  NQ's fourth confirmation window, **the operator's decision** (D-107, D-461).
- Stage 2's draft P-16 confirmation (`vendor/stage2/prereg/DRAFT_P16_confirmation.md`) and F-02's, family B's and family
  R's drafts target the same window. If any test reads it first, the lead records that before registration, and the
  operator decides whether it can still confirm this pick.
- **What it tests -- the pick's trades, not P.** With the state (and u3's pinned forecast) fixed:
  - C1 on the window's population, one-sided at the registered 0.05, by Q-16's statistic (B2 re-simulated at the
    window's length, `[20261985, 10 + line, j]`), the bound at 0.05 / N beside (D-189's form);
  - C2 at the 95 % bound, valued with stage C's routing weights per in-state opening (the window is too short for its own
    campaign), at least $500 a year;
  - C3 and floor (i) on the window, overall and in every calendar year with at least 63 sessions (a stub year pooled,
    D-604);
  - Q-16's draws, if any, from `[20261986, 1]`; the seeded twin's from `[20261982, c, 2]`.
- **What it cannot test: P.** Six months is about 126 sessions, about 63 starts with a month-3 horizon; no interval on P
  exists there (the phase-0 red team's M1). The scorecard on the window is descriptive.
- **How much data:** at least six months (D-604), and at least the months at which the pick's expected in-state
  sessions (the lower of its two blocks' rates) reach the count at which Q-16's statistic, one-sided at 0.05, has 80 %
  power for a lift equal to **the pick's judged lower bound at the family's level**. That count is computed when the pick
  is carried and written in the carrying row, before any confirmation data exist. If it is more than the operator will
  buy, no confirmation is registered, and the pick stays a development finding.

## 16. Seeds -- proposed 20261980-20261989, checked unique, for the lead to confirm at pinning

| seed | what it draws |
|---|---|
| 20261980 | stage A and B's bootstraps: `[20261980, 0]` A4's skill, `[20261980, 1]` stage B's max-statistic, `[20261980, 2]` V_B's standard error |
| 20261981 | the build's shift-invariance test's replacement walks (A3, T-2): `[20261981, j]` |
| 20261982 | the placebo-selection twin: `[20261982, c, b]`, c the cell (0 s1, 1 s2, 2 s3, 3 u3), b the block (0 judged, 1 choice, 2 the confirmation) |
| 20261983 | the judged block's paired gate campaigns (the design, its twin design, P-16): 500 paths -- C2's routing, the long-run gate floor, the scorecard |
| 20261984 | the choice block's paired campaigns of stages A and B (P-16, each cell's design and twin design): 200 paths |
| 20261985 | stage B2's replicates `[20261985, line, j]`; the confirmation's re-simulation `[20261985, 10 + line, j]` |
| 20261986 | Q-16's statistic's draws, if any: `[20261986, 0]` stage C, `[20261986, 1]` the confirmation |
| 20261987 | the scorecard's paired draws `[20261987, 0]`; the denial ladder for this file's designs `[20261987, 1]` |
| 20261988 | the build's synthetic tests: `tests/test_family_o_persistence.py` (`[20261988, j, ...]`, j = 0..6); T-3's synthetic judged block `[20261988, 100]`; T-10's synthetic selection `[20261988, 200, j]` |
| 20261989 | reserved; unused, and every result file says so |

**The check (2026-11-16), before this file was written and again after.**

- `grep -rIowh --exclude-dir=.git -E "2026198[0-9]" .` over the whole working tree, the vendored snapshot and its
  results included: **no hit** before this item; after it, only this file and its test.
- Without word bounds: no hit before this item.
- `git grep -I -E "2026198[0-9]"` over every commit of every local and remote branch (`git rev-list --all`, after a
  fetch), the vendored tree included: no hit before this item.
- T-1 asserts that no other file under `prereg/` names any of them.
- **Not searched:** Stage 2's working tree beyond its vendored snapshot (its decision log and scripts are vendored and
  were searched).

**Neighbouring blocks, taken:** 20261910-19 (Q-16), 20261920-29 (Q-17, Q-20), 20261930-39 (F-02), 20261940-49 (F-P),
20261950-59 (Q-18), 20261960-69 (family B), 20261970-79 (family R).

**Inherited, used only as their owners registered them:** 20261102 (P-16's coin); 20261206 (P-16's gate, the
identity); 20261131 (P-14's, beside); 20261600 + i and 20261700 (Stage 2's coin sequences and D-621 (3), beside only).

## 17. Multiplicity and the budget

1. **k.** The next free program family number at the pin, with level 0.05 / (k (k + 1)), written by the gatekeeper in
   the pinning row.
2. **Counted:**
   - **4 cells** (s1, s2, s3, u3), each counted whether killed at A, closed at B or read at C; u3 is counted although
     its stated sign is negative;
   - **0 searched configurations**;
   - **11 fitted values** (u3's coefficients) inside the walk-forward, fitted in each of its three folds and the final
     fit, none searched.

   The identities, the controls (A4), the counts of stage A, B2's replicates, the seeded twin and the readings beside
   are not trials: nothing is chosen from them.
3. **One cell reaches judgement.** C1, C2, C3 and the floors are an intersection at one level. Stage B spends nothing of
   the program's budget.
4. **The program's honesty sentence:** Stage 2 ran programs S and U on this window, each with its own 5 %; the sided
   follow effect (S1, S3), the state gates (S2) and the base opening's won share have been read on both blocks
   (section 2); the development level is a screening threshold, and the decision is carried by one confirmation on
   unread data (D-189), if the operator buys one.

## 18. The build: adapters, identities and tests (after the pin, before any reading)

### 18.1 The code (in `extended/`, never in `vendor/`)

1. **`extended/opening_states.py`.** LR, LRS, DIS, har, H, HS, the four states, the rolling third, and u3's IV, M,
   x1-x3, bands, fit and y_hat. Bars come only through `extended/reader.py`. The library's `grid`, `slot` and trailing
   median are imported, not copied. The states of every population offer are written as boolean columns of the
   population frame and hashed before any campaign reads them.
2. **The population builder.** P-16's cell as `rc_width_screen.build` builds it with this repository's walker; both
   sides of every population offer at 3R, and at every table R for V_other; the strata. No vendored attribute is
   substituted (the lesson of E-011's first run).
3. **The waiting account.** A subclass of the vendored `FundedAccount`, passed as `funded_account_cls` to
   `extended.gate.run_gate` (Q-47) and to Q-17's replay, whose account answers the router's `can_take` with the
   vendored draw's answer **and** "the offer is in state, or the account has traded, or its wait is over" (5.4). If the
   build finds that the class cannot reach the draw the router registered (`TierSizedDraw` registers itself, sizing.py),
   the seam is composed instead at the funded draw factory in Q-47's form (the vendored body, one keyword, a source-hash
   guard), under a row. Either way A1 items 3 and 4 refuse.
4. **The place-recording adapter** (family B's draft section 20 item 8): every simulated trade's offer, R and place, and
   for each opening its wait and whether it was a fallback; held to its identity -- P-16's registered campaign re-run as
   U2 ran it reproduces `u_value_map.csv`'s `trades_per_year_records` for `p16`.
5. **The estimand.** c_i, the strata means, z_s, L and its halves, V and V_other, from the population frame and the
   routing records.

### 18.2 Tests (fast tier unless marked; written before the code they test)

| test | what it asserts |
|---|---|
| T-1 | **written now:** `tests/test_family_o_persistence.py`. The driftless walk's long and short target-first shares are 1/(1+R) exactly; on the persistent random walk the side-symmetric 3R win rate rises with persistence (above 1/4 when moves persist, below when they revert) and the long equals the short; at R = 1 the two sides cancel on every resolved path; a fixed drift splits the halves at first order and moves their mean by less than a tenth of the split; the twin's exact form equals the mean of 2,000 seeded placebo draws, its noise-free part is exactly the in-state excess share of persistent sessions times the regimes' gap, and over fresh noise the lift averages it; an uninformative state's lift averages zero; the rolling third fires on about a third and reads only the past; the population's latest alert reads no 08:30-08:59 bar; this file's `Judged-block reads:` line gives exactly section 19.1's purposes by `extended.reader.declared_purposes`, none a choice or fitting purpose; this file's seed table is 20261980-20261989 once each, and no other `prereg/` file names them (seeds `[20261988, ...]`) |
| T-2 | the states' and y_hat's shift invariance (A3): replacing, and deleting, every bar stamped at or after m - 5 changes no state; replacing the alert day's 08:30-08:59 bars changes none; x3 equals 2 x `rv_tod` at every RTH alert where the library computes it; no state all-undefined or constant |
| T-3 (heavy, under the run lock) | stages A and B, their result sections and u3's final forecast hash are byte-identical when every judged-block bar is replaced by a seeded synthetic walk (`[20261988, 100]`) |
| T-4 | the population: only P-16's marks 17:00-08:25 on its day kinds; on report days from 07:40 only; never an FOMC day, an early close or a mark in 08:30-09:00; the strata as declared |
| T-5 | the waiting account: within W it takes only in-state offers; after W it takes the next routed offer; after its opening it is P-16's; with the state always on, or W = 0, its answers equal the vendored draw's on every (account, offer) of a synthetic campaign |
| T-6 | the estimand on the family's own code: L equals the drawn twins' mean (T-1's identity); an uninformative state's lift averages zero; the halves average to L; V on a synthetic routing record equals its hand sum |
| T-7 | u3's least-squares fit equals a direct normal-equations solve on synthetic data to 1e-8; a planted HAR process is recovered with the right signs; if family R is pinned first, its fit and this one give the same coefficients on a shared synthetic set |
| T-8 | the reader: every bar and walk read goes through `extended/reader.py` with its purpose; an untagged judged read raises (Q-32's own tests, re-run at the build's commit) |
| T-9 | the judge's entry point reads u3's frozen forecast by its hash and cannot fit; stage C reads the pick from stage B's result file by its sha256 |
| T-10 | B2's machinery holds its size on a synthetic clustered selection with a planted slow component (`[20261988, 200, j]`) |
| T-11 | this file's seeds appear nowhere else in the build's commit except the family's own modules and tests |
| T-12 (slow) | A1 items 3 and 4 at 4 paths and 4 starts; the full 500 paths and every start are the run's first stage (heavy) |
| T-13 | the place-recording adapter's identity (18.1 item 4) at 4 paths; the full count in the run |

## 19. Outputs, the reads and the run

### 19.1 The judged block's reads (E-026)

The reader (`extended/reader.py`) authorises a judged-block read only for a purpose named on this line of the pinned
file:

- **Judged-block reads:** `stage_C_states`, `stage_C_judgement`, `stage_C_campaign`, `stage_C_scorecard`

What each is for, in stage C's order (12): `stage_C_states` -- the judged bars, to compute the pick's states and the
strata counts (no walk is read under it); `stage_C_judgement` -- the population's walks at 3R, both sides (C1, C3, the
beside readings of L); `stage_C_campaign` -- the paired gate campaigns of the design, its twin design and P-16 on the
judged sessions (C2, the floors, B2's routing weights); `stage_C_scorecard` -- the U1 replays of the same three designs on
the judged block's starts (13). Each is read once, from a clean run of a committed tree, ledgered before it reads. No
choosing or fitting purpose is named, and the reader would refuse one.

### 19.2 Files and the run

- **Files**, each with its sidecar manifest through `extended.results.write_result`:
  - `results/fo_opening.csv`, sections `identity`, `states`, `supply`, `openings`, `resolution`, `wait`, `power`,
    `choice`, `level`, `judged`, `campaign`, `floor`, `beside`;
  - `results/fo_journey.csv`, the scorecard of section 13.

  Each manifest carries: `prereg_id` this file's F-id; the cell counts (4 cells, 0 searched, 11 fitted values); every
  seed and parameter; u3's frozen forecast hash; the population frame's and the states' hashes; the sha256 of
  `vendor/DATA_MANIFEST_stage2.sha256`. Every file is EXPLORATORY until a carried design is registered.
- **The runs: two, each once**, from a clean checkout of a named commit (`scripts/run_clean.py`), under the run lock,
  watched to its end.
  - **Run 1 (the choice block only):** stage A (identities first), u3's walk-forward and final fit, stage B. It writes
    the `identity` to `choice` sections, u3's frozen forecast and its hash, and the pick. It reads no judged-block bar or
    walk.
  - **Between them, the lead's row:** u3's forecast hash (if u3 is the pick, and in any case the final fit's hash) and
    the pick, by the sha256 of run 1's result file, pinned in a decision row and committed.
  - **Run 2 (from a clean checkout of that commit):** `stage_C_states`, B2, `stage_C_judgement`, `stage_C_campaign`, the
    floors, `stage_C_scorecard`. The judge's entry point reads the pick and the forecast by their pinned hashes and
    cannot fit (T-9).
  - **Weight: heavy.** Run 1 walks every overnight mark of every session at 150 ticks on both sides (E-011's P-16 run
    is the nearest measure of memory) and runs the choice block's paired campaigns (P-16 and up to four designs and four
    twin designs at 200 paths); run 2 the judged block's three paired campaigns at 500 paths and the U1 replays on two
    arms: hours each, at two workers.
  - Within a run, each stage's file is written before the next reads anything. A kill stops the sequence (a family
    killed or closed in run 1 has no run 2).
  - A run aborted or restarted is recorded by the lead with its log, and only the first complete run of each is read.

## 20. Open before the pin

**The lead's:**

1. **Q-16 merged**, with its calibrated statistic for the placebo-selection comparison (E-023's follow-on) and its power
   function. Its name, module and commit go where this file says **[Q-16]**.
2. **The twin's form:** the placebo's exact expectation in C1, the seeded draw beside (7.2); or the drawn twin in the
   line.
3. **u3's fitted values under E-031 (1)** (11 coefficients, inside the choice-block walk-forward, hashed and pinned
   before the judged read): confirmed as admitted.
4. **The seam (18.1 item 3):** a `FundedAccount` subclass through Q-47's keyword, or a funded-draw-factory composition in
   Q-47's form if the class cannot reach the router's draw -- the build's finding, under a row, the identities refusing.
5. **The place-recording adapter** (family B's item 8) built and held to its identity; **Q-47's 500-path identities**
   held (E-028 (3)).
6. **The fixed values a reviewer may question:** W = 5 sessions, K5 at one half, the 250-session third, the 17:30 start of
   s1 and s2 -- confirmed as the file's, or changed before the pin (each a declaration choice, not a search).
7. **The bound arm's shift:** P-16's registered shift at each R for every design here (12, C2).
8. **The value bar** of $500 a year at place (c), and **V_other beside** rather than inside C2 (7.4).
9. **The family number:** F-02 and family B may be pinned first.
10. **The seeds** (section 16) confirmed unique at the pin.
11. **Q-35**, if it runs first: its both-block counts recorded as a pre-read (4 item 4).
12. **The row between the two runs** (19.2): run 1's result file, the pick and u3's forecast hash pinned before run 2.

**The red team's, in particular:**

- whether the strata (mark, day kind, calendar year) are the right "same population" for E-023's twin, and whether a
  twin that does not match the state's clustering is acceptable when only its exact expectation enters the line;
- whether C1 on every in-state offer plus C2 on the openings' own offers is the right split, or C1 should be read on the
  openings alone (more relevant, far less power);
- **whether earlier sessions' 08:30-08:59 bars inside H and IV are inside D-281 (3)'s closed branch.** This draft reads
  E-030 as excluding the alert day's bars only, as family B's merged draft does. If held inside, H and IV are computed
  with each session's 08:30-08:59 bars left out, by a redraft before the pin;
- whether B2's slow component (switching 1/63, a\* from the choice span's quarterly block means) is the right null for
  clustered daily and nightly states;
- whether V_other belongs beside or in C2.

**The operator's (only when they arise):**

- NQ from 2026-07-17 as a fourth confirmation window (D-107, D-461) and its purchase, only once a pick is carried;
- the levels of E-015's limits (flags only);
- D-281 (3), only if stage A's count shows most openings at 08:30-09:00 and the lead proposes a family that times them
  there (5.5 item 6).

## 21. Anything chosen after seeing results

*(Empty. Anything added after a reading is exploratory, reported apart, `exploratory=True` in its manifest, and recorded
in its own decision row -- never added to this file once pinned.)*
