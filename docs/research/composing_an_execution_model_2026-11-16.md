# Composing an execution model from the program's components (TASK_QUEUE Q-99, 2026-11-16)

A read-only structure note by the scout (wt-scout, branch `wt/wt-scout`, on master 40a56a7). It changes nothing,
declares nothing and recommends no component: nothing in the program has been judged yet. It reads the program's rules
and its declaration drafts, and says how the pieces would fit together and what fitting them would require.

**What was read** (2026-11-16): `CHARTER.md` sections 1-6 as amended (its sha256 at E-032); `DECISIONS.md` E-001 to
E-060 at 40a56a7, and E-061 to E-063 in the lead's staged copy (`Desktop\Stage 2 - Extended\DECISIONS.md`, staged, not
yet committed at 40a56a7); `TASK_QUEUE.md` and `STATUS.md` in the lead's copy; every draft under `prereg/` --
`DRAFT_F-02_resting_levels.md` (seventh text), `DRAFT_F-B_multifeature.md` (sixth version), `DRAFT_F-O_opening_timing.md`
(second version; its third, Q-87, is being drafted), `DRAFT_F-R_resolution.md` (second version),
`DRAFT_F-P_payout_policy.md` (second version; its third, Q-92, is being drafted), `DRAFT_RD_firms.md` (second version;
its third, Q-91, is being drafted); the scout's note `docs/research/mechanisms_2026-11-15.md` sections 3.1-3.2; the
audit's `docs/audits/phase0/D_protocol.md` section 1.5; the
docstrings and signatures of `extended/gate.py`, `extended/user_beside.py`, `extended/place_records.py`,
`extended/openings.py`, `extended/user_spend.py`, `extended/journey_page.py`; the title blocks of Stage 2's registrations
`vendor/stage2/prereg/P-15_rc-s100-all.md` and `P-16_rc-s150-all-nr.md`.

**What was not read:** no result value (no `results/*.csv` of either repository was opened; the value map
`vendor/stage2/results/u_value_map.csv` is cited only through the drafts' descriptions of its sections), no bar, no
walk, no trade table, no NQ from 2026-07-17. No statistic of any outcome is computed or quoted here. The figures in this
note are declared constants (k, levels, cell counts, seeds, the wait W, the $500 bar), taken from the rows and drafts
cited beside them.

---

## The question

The operator's aim, in their words: measure "components and levers of an actual execution" so they show "what
components we need to piece together into an actual execution model", judged by the user's path -- time and money to
the first passed account, to the first payout, to being ahead, and how evenly that is spread across start days -- not
one lump sum. The brief asks four things: (1) the component map; (2) how components compose; (3) what declaring a
composite would require; (4) the order of operations the program implies, and where the user's path is reported.

## The answer in a few sentences

An execution model has about ten slots: when offers appear, how an order is entered, which side, the bracket and its
R, the size, how trades are routed across accounts, how many evaluations are bought, when a funded account first
trades, when and how much is withdrawn, and at which firm. Stage 2's registered designs P-14, P-15 and P-16 fill every
slot and share one money side (P-14's state table, router, seats and purchase budget); they differ only in their trade
stream. Each piece of this program proposes to replace **one** slot: F-02 the entry and side (resting orders at
pre-session price levels), family B the side (a model, on its own afternoon schedule), family O the time of the funded
account's first trade, family R which late offers to admit (and, described only, the opening's R), reading PP the payout
policy, reading FC the firm. Only pieces that change trades can pass (E-008, E-023 (2)); the money-side levers are
described for the operator to choose from a menu (E-023 (1)). The pieces are **not** independent: every one shares the
firm's single position slot, the five seats, the router and the state table, so their offer-level tests (C1) can be
read separately but their value at the places a win is worth most (C2), the floors and the user's journey cannot. Two
pairs conflict outright on the funded opening (F-02 with family O; family O with R's cap). A composite is a new family:
its own k, pin, count and lines; components that each passed do not make it pass; and if it is chosen after the
components' judged reads, its cleanest evidence is the confirmation window, a purchase and the operator's decision.
The user's path is never the pass line: it is reported beside every verdict on the journey page (Q-69) and the money
page (Q-86), and it is how the operator chooses among described levers.

---

## 1. The component map

### 1.1 In plain words

Think of an execution model as a form with ten boxes. Stage 2 filled every box once and registered the result three
times (P-14, P-15, P-16). Each family or reading in this program offers a different answer for one box and keeps every
other box as Stage 2 filled it. The table says, box by box, what the registered designs do today and which piece of
this program would change it.

| box (slot) | what P-14 / P-15 / P-16 do today | which piece would change it | the piece's class under E-023 |
|---|---|---|---|
| 1. **schedule** -- when offers exist | P-14: 30-minute-bar breakouts, the 100-tick rung from 17:00 to the 12:00 hour, the 50-tick rung at 13:00 and 14:00 (F-02 draft lines 867-868, citing P-14's registration); P-15: a 25-point coin, marks to 12:00 CT (`rc_s100_all_nr`; family B draft lines 166, 284); P-16: a 37.5-point coin every five minutes 17:00-09:00 CT (family R draft lines 55-56; family O draft 5.1) | F-02 adds tickets at 08:30 at four pre-session levels; family B its own marks 10:10-15:05; family R Part I admits P-16's refused marks 09:05-15:05 on forecast-fast days | F-02, B: E-008; R Part I: E-023 (2) |
| 2. **entry mechanics** | a market order at the mark plus five minutes, by hand (CHARTER section 4) | F-02: a resting stop or limit at the level, live five minutes after it is published (F-02 section 3, lines 247, 257) | E-008 (with box 3) |
| 3. **side** | P-14 follows the breakout; P-15 and P-16 a seeded fair coin (P-16: `rc_s150_all_nr`, seed 20261102 per date and mark, family O draft line 328) | F-02: the level's geometry (`break` / `fade`); family B: a model's side | E-008 |
| 4. **bracket and R** | the stop is the design's (12.5/25, 25, 37.5 points); R is set per account state by the no-closure table `state_dp_e-0.050_lamstar_noclose` (F-P draft lines 157-158), 3R at the fresh funded account's opening (handoff 2.5, E-012 (1)) | family R Part II `R-cap`: the opening's R where it is forecast to resolve | E-023 (1), described |
| 5. **size** | the engine's sizing under the firm's allowance and the Combine's room, allowance-capped (E-022 (1), E-032 (3)) | none (every piece keeps it) | -- |
| 6. **routing across accounts** | the longest-waiting account that can take the trade (`able`), one position at a time across the firm with five minutes flat (D-429), one trade an account a session, five seats (family O draft 5.1, lines 333-335) | family O: a waiting account declines out-of-state offers; F-02: a reserved account and cancel-on-entry (F-02 11.2) | as its family |
| 7. **purchases** | at most 20 evaluations in 21 sessions (CHARTER section 3) | none | -- |
| 8. **the funded opening's timing** | the first offer the router hands the new funded account (family O draft lines 51-53) | family O: wait at most W = 5 live sessions for one of four declared states | E-023 (2) |
| 9. **payout policy** | the maximum request at the first eligible close (F-P draft 6.1) | reading PP: `lock` (hold the first request until the loss limit locks) and `half` | E-023 (1), described |
| 10. **firm and contract** | Topstep $50K, Standard path, Aeropay (RD firms draft 2.1) | reading FC: Lucid LucidFlex 50K, DayTraders EOD 50K, TradeDay Fast Pass and Quick Pay | E-023 (1), described |

Fixed for every piece, never a component: hand entry at least five minutes after the alert, the news and FOMC cuts, the
resolution rule (at most 5 % to the 15:10 flatten), the conduct tiers (CHARTER section 4; E-008 (3)).
F-01 (`prereg/F-01_resting_order_level_atlas.md`) is withdrawn and spent k = 10 (E-007 (a)); F-02 replaces it, so it is
no component here.

**One fact carries most of what follows:** P-15 and P-16 are registered as "the resolved coin re-entering when flat on
P-14's design" (`vendor/stage2/prereg/P-15_rc-s100-all.md` and `P-16_rc-s150-all-nr.md`, title lines). All three
registered designs run on **one money side** -- boxes 4 to 10 -- and differ in boxes 1 to 3. Every piece of this program
is built on one of them as its **base** and changes one box.

### 1.2 Each component, precisely

**F-02, resting orders at pre-session levels** (`prereg/DRAFT_F-02_resting_levels.md`; E-017, E-022, E-032, E-042,
E-044, E-045, E-047, E-048, E-052, E-063).
- *Decision:* where to enter (a resting order at the prior session's high and low, the overnight high and low, the prior
  close, or the nearest 100-point round numbers) and which side (`fade` at all four kinds, `break` at round numbers
  only), at stops of 50, 100 or 150 ticks, R 1, 1.5 or 3 (header lines 36-52; 5.1-5.2).
- *Holds fixed:* the base's own trades, walk, coin, cuts and table, "unchanged" (11.2, line 937); the base is P-14 for
  50- and 100-tick picks and P-16 for 150-tick picks (11.2, lines 932-935).
- *Reads:* bars stamped at or before 08:24 CT for levels and sides; fills from the bar stamped 08:30; the pinned
  calendars (section 4); the value map's place values and records for C2 (section 10).
- *Count and level:* 15 cells, 45 signed hypotheses; k = 11 at 0.05/132 (header; 16), "pinned next or not at all"
  (E-048 (1)); the pin waits for Q-55 and Q-83 and the gatekeeper's re-read (E-063).
- *Pass line:* E-008 -- the tickets' lift over the coin twin on the same fills by `cons` (C1), a placebo line for the
  `break` cell (C1'), the value at the bound at least $500 a year on the uses the routing can reach (C2), resolution
  (C3), measurability (C4) and C0's count check, all required (section 9, line 729). Stage D's floors "can close the
  family; nothing here can carry it" (11.1, lines 919-920).
- *Places it can act at:* (b) the evaluation, (c) the funded opening (R = 3 only), (d) funded before the first payout,
  (e) paid -- allocated in order of a place's value, capped by what the routing reaches (section 10, lines 855-902).

**Family B, one model choosing the side** (`prereg/DRAFT_F-B_multifeature.md`, sixth version; E-016, E-019, E-024,
E-030, E-036, E-040, E-044, E-047, E-051, E-060, E-062).
- *Decision:* which side, on its own schedule -- alerts 10:05-15:00, entries 10:10-15:05 CT, stops 12.5 and 25 points
  (section 3, lines 171-174); `side` takes every offer, `filter` takes only offers where the model is confident (10,
  lines 561-567).
- *Holds fixed:* P-14's money side through Stage 2's RC runner (14, lines 914-918); not a registered coin's schedule
  (3, lines 216-218).
- *Reads:* 37 features from bars stamped at or before t - 1 minute, none from 08:30-08:59 of the day (2 (c), lines
  125-128); a regularised logistic fitted in the 2020-2023 walk-forward (E-031 (1)); Stage 2's three follow rules as
  twins (13, lines 813-817).
- *Count and level:* 12 cells, 28 searched configurations; k at least 12 (18, lines 1113-1121).
- *Pass line:* E-008 -- C1 over the coin, C1-d drift-matched, C1-f over each follow rule, C2 at the lesser of the
  model's own routing and the coin's (13, lines 823-864). Its own text expects a screen (0, lines 53-56).

**Family O, a side-free timing filter for the funded opening** (`prereg/DRAFT_F-O_opening_timing.md`, second version;
E-021, E-023, E-039, E-042, E-046, E-054).
- *Decision:* **when** a newly funded account takes its first trade -- it waits at most five live sessions for one of
  four declared states (s1, s2, s3, u3) in P-16's overnight offers, then falls back to P-16's next routed offer (header
  lines 27-44; 5.4).
- *Holds fixed:* P-16 exactly -- the coin side, the table's R and size, the router's order, the one-position rule;
  "Combines and funded accounts that have traded are P-16's in every respect" (5.4, lines 374-387).
- *Reads:* P-16's offers at the marks 17:00-08:25 CT (report days from 07:40), walked long and short at 3R (5.2); states
  from closed overnight bars; u3's forecast fitted in the walk-forward (6.5); the U1 replay in history's order for C2
  (7.4).
- *Count and level:* 4 cells; k the next free at its pin (17).
- *Pass line:* E-023 (2) -- C1 and C1-close against a placebo-selection twin by `placebo_selection_bound`, C2 the
  design's openings against the twin design's by `two_sample_bound`, at least $500 a year at place (c), C3 both halves
  (header line 41; 7, 12).
- *Place:* (c) only; R = 3 only (5.3, line 369).

**Family R, resolution forecasts** (`prereg/DRAFT_F-R_resolution.md`, second version; E-021, E-028, E-057).
- *Decision, Part I:* which of P-16's refused marks (09:05-15:05 CT) to admit, on days the forecast says they resolve
  (header lines 40, 44; 0.1 line 124). *Part II, `R-cap`:* the funded opening's R where it is forecast to resolve
  (14). Its third use -- routing the opening to a fast offer -- is family O's cell u3 (0.1, lines 126-131).
- *Holds fixed:* P-16 as registered, its report-day 07:35 entry kept (header line 39).
- *Reads:* a HAR-type variance forecast from closed bars, 35 fitted values inside the walk-forward (header line 47;
  6).
- *Count and level:* Part I 3 cells, k the next free; Part II unnumbered (header line 44). Its pin is deferred until
  F-02 and family B go first (E-028 (2)), and it may close before its pin as "not judgeable on this block" (E-057 (1)).
- *Pass line:* Part I E-023 (2) as family O's form; Part II none, described (E-023 (1)). Its own text expects the
  selection's lift to be only the cost avoided at the flatten (E-028 (2); draft 0, lines 64-68).

**Reading PP, payout policy** (`prereg/DRAFT_F-P_payout_policy.md`, second version; E-018, E-023, E-025, E-059).
- *Decision:* when the first payout is asked (`elig` / `lock`) and how much each request takes (`max` / `half`)
  (6.1, lines 256-259).
- *Holds fixed:* P-14's registered trades (P-16's beside); the offered trades unchanged (0.1, lines 62-64).
- *Reads:* no bar; the registered trades; Stage 2's verified payout rules (section 4).
- *Count:* 11 runs; no k, no level, no pick (header lines 22-34; 12).

**Reading FC, other firms' contracts** (`prereg/DRAFT_RD_firms.md`, second version; E-038, E-045, E-058).
- *Decision:* which firm and plan (2.1).
- *Holds fixed:* P-16's registered trades (P-14's beside), their tables, protocol, routing and purchase budget; only the
  plan's allowances and per-trade costs replace Topstep's (2.3, lines 128-133); the payout request carried from the
  reference (2.3, lines 139-144).
- *Reads:* no bar; each plan's verified terms; declared readings of the unverified ones (section 5).
- *Count:* 27 replays (or 29); no k, no level, no pick (header lines 42-54).

### 1.3 What each piece can move on the user's path, and what the program can credit it with

**In plain words.** "Can move" means the piece can change that measure on some start day, by its mechanics. "Credited"
means what its pass line measures. A piece can change a user's path in ways its pass line deliberately ignores: extra
trades, for instance, are felt by a user but cancelled by the twin, so a design cannot pass on supply alone.

The measures are the operator's (E-014; CHARTER section 2): sessions and cash to the first pass; sessions and cash to
the first payout; sessions to break-even and P (the share ahead at months 1-3); the path's evenness; and money spent and
the return on spend (Q-86, `extended/user_spend.py` lines 10-14).

| piece | first pass (sessions, cash) | first payout (sessions, cash) | break-even, P | evenness | money spent | what its pass line credits |
|---|---|---|---|---|---|---|
| F-02 | **can** (a ticket used at place (b)) | can (places (c), (d)) | can | can | can | the tickets' direction at the same fills; their value only at uses the routing reaches |
| family B | can (its design is a whole stream) | can | can | can | can | direction on its own offers, beyond drift and Stage 2's follow rules; value at the lesser routing |
| family O | **cannot** -- before the first funded account exists its rule never acts, so the first pass is P-16's on every start (5.4, lines 374-376) | can (the opening waits up to five live sessions; its outcome) | can | can | can (accounts end or survive differently, so purchases differ) | the state's choice of offer against a random choice of the same share; not the schedule move |
| family R, Part I | can (more offers reach Combines) | can | can | can | can | the forecast's choice of late offers against a random admission; **not the added supply**, which the twin adds too (draft 0, lines 94-96) |
| R-cap (described) | can (it caps any leaf asking more than the cap, mostly the opening's 3R; 14.1, lines 1102-1107) | can | can | can | can | nothing: described, never carried |
| reading PP | **cannot** -- identical to its base until the first payout request (0.1, lines 66-74) | can (`lock` its timing, `half` its cash) | can | can (the lever aimed at evenness) | can (later purchases and fees diverge, 0.1 line 71) | nothing: described, never carried |
| reading FC | can (price, target, drawdown from the first session; RD 0, lines 64-74) | can | can | can | can | nothing: described, never carried |

Two further limits on what any piece can move, from the rules rather than its mechanics:

- **The value map is first-order and Topstep's.** Every C2 prices a win by `mean_dv` at a place, "first-order, with the
  table held fixed. It is a ranking and a bar, never a forecast" (F-02 10, lines 905-906). The tables were solved for
  Topstep's contract and are not re-solved for any other plan (RD firms G-6, line 349). So a piece's dollar value at
  another firm is not defined by anything in the program.
- **The first quarter is mostly the start day** (CHARTER section 2, lines 66-70): every measure is reported as a
  distribution over start days with the start day's share of the variance, because a single number would overstate what
  any component controls.

---

## 2. How components compose

### 2.1 In plain words

Two pieces can meet at three levels. **At the level of single offers** (each piece's C1 test), pieces that look at
different offers do not touch each other at all, and nothing on the money side changes any C1. **At the level of the
campaign** -- one firm, one open position at a time, five seats, one router, one state table -- every pair touches: an
extra trade in the afternoon blocks the slot for the next offer, a waiting account hands its offer to another account, a
payout changes which bracket the table asks next. **At the level of the user's journey**, everything that happens in
the campaign shows up. So "stacking without re-testing" is true only of the C1 lines; the value lines, the floors and
the scorecard of a stack must be read on the stack itself. Two pairs do not merely interact but collide over the same
decision -- the funded account's first trade -- and need a declared rule of precedence before they can coexist.

### 2.2 The three levels, precisely

1. **Offer level (C1).** Each family's pass line reads every offer independently: F-02 "stages A to C read every fill
   independently" (section 3, line 248); family B "the pass line reads every offer (the coin twin's form)" (section 4,
   line 229); family O's and family R's C1 compare in-state (admitted) offers with their strata's means over the whole
   population (O 7.2; R 7.3). None of these reads routing. So a C1 result is unchanged by any other piece's routing and by
   any money-side lever (PP, FC, R-cap), provided the offer population and its labels are unchanged.
2. **Campaign level (C2, the floors, the counts).** C2 is valued at the places the routing reaches (F-02 10 (ii); B 13,
   lines 834-864; O 7.4; R 7.4); the long-run gate is read on the family's own design, never taken from the base's
   registered pass (E-022 (2); F-02 11.1); the routed counts are checked under E-052 (B 13, line 790; R header line
   46). All of these depend on the slot, the seats, the router and the table, which every piece shares.
3. **Journey level (the scorecard).** The U1 replay in history's order (CHARTER section 2; F-02 12; B 14; O 13; R 13),
   which is downstream of the campaign.

Every family's judged design is already a **base plus one component**: F-02's stage D adds the tickets to P-14 or P-16
(11.2); family O's design is "P-16 with the waiting opening" (14, line 1024); family R's "P-16's schedule plus the
pick's forecast admission" (15, line 1153); family B's design (i) is P-14's money side with its offers (14, lines
914-917). A composite is a base plus **two or more** components.

### 2.3 Pair by pair

"Independent at C1" means disjoint offers or a lever that changes no offer. "Interacts" means the campaign level must be
re-read. "Conflicts" means both pieces decide the same thing and a precedence rule must be declared before both can run.

| pair | C1 | campaign | verdict |
|---|---|---|---|
| F-02 x family B | independent (F-02's tickets from 08:30 to a cutoff at latest 14:30, F-02 line 256; B's market entries 10:10-15:05) | both hold the slot between 10:10 and 14:30; F-02 cancels a resting ticket "before any base entry on another account" (11.2, line 947), so B's entries would cancel tickets; base-compatible only at F-02's 50- and 100-tick picks (P-14's money side) | interacts |
| F-02 x family O | independent (O's population is P-16's overnight marks; F-02's tickets live from 08:30) | **conflicts at place (c).** F-02 places a ticket on "an account that asks the pick's R, has not traded that session" (11.2, lines 940-942) -- a fresh funded account asking 3R qualifies; under O that account is waiting and "answers 'no' to an offer out of state" (5.4, lines 376-380), and a ticket is never in O's state. Also O changes F-02's reachable count (ii): "most of them go to the base's own overnight trades first" (10, line 896), and O makes waiting accounts decline those trades. Neither draft names the other's presence | **conflicts**: a precedence rule is a design choice |
| F-02 x family R (Part I) | independent (levels against P-16's late marks) | share the slot 09:05-14:30; R's admissions are base entries for F-02's cancel-on-entry; base-compatible only at F-02's 150-tick pick (P-16) | interacts |
| F-02 x R-cap | -- | R-cap lowers the opening's R where forecast slow; F-02 prices a 3R ticket only at (c), whose share of leaf-days asking 3R it takes from the base's records (10, lines 859-862) -- capped days ask less | conflicts on the opening's R |
| F-02 x reading PP | unchanged | PP changes balances from the first payout on, so which accounts ask which R at (d) and (e) and how far the tickets reach there | interacts after the first payout |
| F-02 x reading FC | unchanged | another plan's allowance changes a ticket's size, and F-02's release-window cancellation keys on "full allowance" (section 3, line 252); TradeDay liquidates positions 12:58-13:02 CT on FOMC statement and minutes days (RD firms G-3, line 346), inside the tickets' resting window; C2 has no value map at another firm (G-6) | interacts; C2 not transferable |
| family B x family O | O's population is P-16's overnight coin offers; B trades none of them | in B's own design the opening moves to the first offer after 10:10 (B 3, line 199); a waiting rule on B's schedule is not family O as declared | not stackable as declared: a new hypothesis |
| family B x family R | different stops (12.5/25 against 37.5 points), sides and bases | slot contention after 10:10; no common base | not stackable as declared |
| family B x reading PP / FC | unchanged | as F-02 x PP / FC | interacts |
| family O x family R (Part I) | independent populations (overnight against 09:05-15:05); u3 *is* family R's forecast, "if both are pinned, the two are one module (T-7)" (R 0.1, lines 128-131) | an account still waiting at its sixth live session takes its next routed offer (O 5.4, lines 383-384), which with R could be an admitted late mark | interacts; shares a module |
| family O x R-cap | -- | **conflicts**: both change the funded opening -- O its time at R = 3, R-cap its R; O's C1 reads R = 3 only (5.3, line 369) | **conflicts** |
| family O x reading PP | unchanged | sequential in an account's life (the opening comes before the first payout), but both need their own `FundedAccount` subclass through the one seam (O 5.4, lines 395-401; PP 13.1, lines 593-600) | interacts; needs one composed class |
| family O x reading FC | unchanged | O's wrapper subclasses Topstep's `FundedAccount`; DayTraders' and TradeDay's funded accounts are their own subclasses (RD firms A-3, A-5, A-7, lines 328-331) | interacts; needs a composed class per plan |
| family R x reading PP | unchanged | R adds offers through the trade stream, no class of its own; PP changes accounts after the first payout | interacts |
| reading PP x reading FC | -- | FC carries the reference's request rule to every plan, "the payout lever itself is reading PP's subject" (RD 2.3, lines 139-144); `lock` is defined on Topstep's loss-limit lock (8284204; PP 6.1) | not stackable as declared: PP at another firm is a new reading |
| R-cap x reading PP | -- | R-cap changes table leaves; PP's held-state rule reads the table at four winning days (PP 6.3) | interacts |

**Summary.** No pair is independent at the campaign level. At the offer level, every pair whose offer populations are
disjoint is independent, and the three money-side levers change no C1 at all. Two conflicts are on the funded opening,
the place the value map prices highest (CHARTER section 1, lines 15-16): F-02 with family O, and family O with R-cap.
The one-position rule is why every pair meets at the campaign level: "a slow 3R opening hold[s] the firm's slot"
(`docs/research/mechanisms_2026-11-15.md` section 3.2, lines 141-142), and so does every added trade.

### 2.4 The bases, and what they allow

| piece | base | stop |
|---|---|---|
| F-02 | P-14 (50-, 100-tick picks); P-16 (150-tick pick) | 50, 100, 150 ticks |
| family B | its own schedule on P-14's money side (identity through P-15's cell, 14 line 924) | 12.5, 25 points |
| family O | P-16 | 150 ticks |
| family R | P-16 | 150 ticks |
| reading PP | P-14 (P-16 beside) | -- |
| reading FC | P-16 (P-14 beside) | -- |

So a composite on **P-16** could hold F-02 only at its 150-tick pick, with family O and family R; a composite on
**P-14** could hold F-02's 50- or 100-tick pick and family B's money side, but neither family O nor family R as declared.
Which base F-02 lands on is decided by its own stage B pick on the choice block, so it is not known before F-02 runs. A
composite on a base none of its components was judged on is a new design throughout. One more inherited rule: the
registered designs keep their 07:35 report-day entries, while every new family's entries are strictly after 07:35:00 CT
(E-039 (1)); a composite carries both, counted.

### 2.5 What the engine's seams allow today

| seam | what it takes | its state |
|---|---|---|
| `extended/gate.py` `run_gate` (lines 271-315) | **one** trade stream (`blocks`), shifted by `e`/`lb` or per-R `e_by_rr`/`lb_by_rr`; **one** `funded_account_cls` (Q-47; a subclass of the vendored `FundedAccount`, lines 126-139); `payout_lag_days`, `household_closure`, **one** `combine_account_cls` (Q-71, docstring lines 32-47); `recorder` (Q-70) | Q-47's arms HOLD at 500 paths (Q-51, E-044 (3)); every arm now runs through the re-composed campaign, so "nothing carries through `extended/gate.py` until Q-80 holds" (E-049); the recorder's identities are Q-89 (E-055) |
| `extended/user_beside.py` `run_starts(..., funded_account_cls=C)` (docstring lines 52-68) | **one** funded class on every replay path | built (Q-76, E-059); its identity Q-93 owed; **the Focused Trader models are refused for any class but the vendored one** (lines 263-265; E-059 (2)), and forfeiture is refused over a class with its own household rule (lines 266-267) |
| `extended/place_records.py` `PlaceRecorder` (docstring lines 1-56) | every simulated trade's offer -- with the caller's own offer ids (line 8, lines 138-142) -- its R, its place (b)-(e), account and state; each funded account's opening | on the gate only; "the U1 replay ... is not wired" and "offers a waiting account declines are not trades and are not recorded" (line 48 on); Q-94 is wiring the replay |
| `extended/openings.py` (Q-35) | where each funded opening falls: mark, hour, day kind, the 08:30-09:00 window, report day; counts only | built (E-051 (2)); the run is in the heavy queue (E-062 (4)) |
| `extended/user_spend.py` (Q-86) | per start: fees and payouts at the first pass, the first payout, break-even and each month end; the cash out of pocket before break-even; the return on spend | built (E-062 (2)); the run is Q-98 |
| `extended/journey_page.py` (Q-69) | the scorecard page from Q-44's files, the money section from Q-86's; E-015's limits as a pending hook with no level | built (E-054 (1)); waits for Q-44 |
| `extended/lift_bound.py` | `cons` by `bound`, `two_sample_bound`, `placebo_selection_bound` (E-035) | merged; Q-55 and Q-83 before any pin (E-052 (2), E-063 (2)) |

So today a single design can carry **one** trade stream, **one** funded class and **one** evaluation class through the
gate, and one funded class through the replay (an evaluation class there is the firms reading's A-9, not built), with
every trade's place recorded on the gate. F-02's stage D is the program's only declared
two-stream design: each stream is shifted by its own bound "and the two are merged into one day log" (11.4, lines
984-987), with F-02's own placement, reservation and cancel rules (11.2). That runner is F-02's to build after its pin;
it is not a general seam.

### 2.6 What a composite would need built (each in `extended/`, never in `vendor/`, each with its own identity)

1. **A composed funded-account class**, where two pieces each bring one -- family O's waiting wrapper (registered with
   the router through a `FundedAccount` subclass, O 5.4 lines 395-401) with reading PP's `lock` (an override of
   `_standard_eligible`, PP 13.1 lines 593-600) and its held-state table wrapper (13.1 item 2), or either with an FC
   plan's adapter class (A-3, A-5, A-7). Identity: each part off reproduces the other alone bit for bit; both off is the
   vendored class. A composite with its own class reports E-007 (e)'s readings without the ten Focused Trader models,
   labelled, unless the separate build E-059 (2) names is made.
2. **An n-stream day log**: F-02 11.4's per-stream shift generalised -- each stream at its own bound -- with **declared
   precedence rules** where streams meet: who takes the slot; whether a waiting account may take a resting ticket;
   cancel-on-entry across streams; reservation. Identity: with every added stream empty, the base's registered gate paths
   and U1 start rows.
3. **Component tags on every trade**: the recorder's caller-supplied offer ids carrying the component, so each place's
   uses are attributed to a component -- on the gate today, on the U1 replay once Q-94 holds -- and family O's declined
   offers from its own wrapper.
4. **The composite's twin**: for a side-choosing piece the coin side on the same entries (E-008), for a filter the
   placebo selection of the same share (E-023 (2)); a composite holding both needs a twin that cancels both at once
   (coin side and placebo selection together, seeded). `cons`'s level for that joint form is not calibrated: Q-16 and
   Q-82 calibrate the coin-side and placebo-selection forms (E-035 (1)-(2), E-062 (1)), not a joint one.
5. **One priority order of places with shared caps**: F-02's section 10 allocates its uses place by place under caps
   taken from the base's records; in a composite the caps at each place are shared by every component that reaches it,
   so one allocation must cover all of them.

---

## 3. What declaring a composite would require

### 3.1 In plain words

A composite is not a sum of passes. It is a new design with new trades, so it is a new family with its own number, its
own pinned file and its own test. Its number makes every later test stricter, and its test has more conditions than any
one component's, so it needs more evidence to pass. If it is assembled **after** its components have been judged, the
choice of what to assemble was made by looking at their results; the development data can then add little that the
components' own reads did not already show, and the cleanest test is fresh data -- the confirmation window, which the
operator would have to buy, and which several other tests already have their eye on.

### 3.2 The house form

- **A family file** `prereg/F-xx_<slug>.md`, pinned by the sha256 of its LF text in its decision row and enforced by
  `tests/test_declarations_fixed.py` (CLAUDE.md; E-001 (b)); nothing in it edited after the pin (a change is a new
  family).
- **Its k, the next free at its pin**, at the one-sided level 0.05 / (k (k + 1)) (CHARTER section 3, lines 124-127).
  F-02 is k = 11 (0.05/132); family B is at least 12 (0.05/156); then 0.05/182 at k = 13, 0.05/210 at k = 14,
  0.05/240 at k = 15, 0.05/272 at k = 16 (the arithmetic of the charter's formula; family O draft header line 32).
  The lead deferred family R because "a family number spends the program's budget and tightens every later family's
  level" (E-028 (2)); a composite spends the same way.
- **Its `Judged-block reads:` line** (E-026 (2)), its seeds in a block verified unused (as every draft's section on
  seeds), the red team and the prereg-gatekeeper before the pin (CLAUDE.md, "Merging").
- **Its count:** every cell counted whether killed or read -- the base choice, the components' picks, each declared
  precedence rule, each stop and R -- plus any searched value (CHARTER section 6).
- **Its prior exposure:** every component's reads of the same bars and blocks, listed (the drafts' section 2 form).
- **The journey scorecard section** (E-015: the gatekeeper refuses a declaration without it).

### 3.3 Its pass line, trades first (E-008, E-023 (2))

- **The lines on the composite's own trades:** for each side-choosing component, its lift over the coin twin; for each
  filter, its lift over the placebo-selection twin; together an intersection at the composite's level, each by `cons`
  (E-035).
- **Its value line:** the composite's value at the bound, at least the bar it declares, on the uses its own routing
  reaches with shared caps (2.6 item 5) -- at the lesser of its own routing and an outcome-free one where its routing
  selects on its own outcomes (E-047 (2), family B's M4-2 form, B 13 lines 851-860).
- **The floors on its own design:** the long-run gate read on the composite, never taken from a component's or the
  base's registered pass (E-022 (2)); every offered R resolving on the merged stream -- added late trades raise the
  flatten share; verified rules; conduct tier 1 for the composite (one position across the firm across every stream;
  each account its own trades).
- **The scorecard beside, never the line** (CHARTER section 3, lines 90-94).

One consequence to state plainly: the composite's **offer-level** lines would read the same offers as its components'
C1s, so on the judged block they would re-read what the components already read. What is new in a composite is at the
campaign level (C2, the floors, the counts) -- exactly the lines that depend on routing.

### 3.4 Why components that each passed do not make a composite that passes

1. **Different trades.** The shared slot, seats and router change which offers are taken, by which account, at which
   place. F-02's own text says its tickets change the base's routing even when no ticket fills (11.6 item 2), and that
   the base "still occupies the firm" (11.6 item 1).
2. **Values do not add.** Each C2 is first-order with the table fixed (F-02 10, lines 905-906), its `mean_dv` averaged
   over the base's own routing, its caps from the base's records (10 (i)). Two components drawing on place (c) share one
   cap of openings.
3. **Its own level.** Each component passed at its own 0.05 / (k (k + 1)); those statements do not combine into one at
   any level for a different hypothesis, which takes the next free k (CHARTER section 3).
4. **Chosen after a look.** A composite assembled from components because they passed is chosen knowing the judged
   block's reads -- the audit's "between families" hole: "the budget bounds the multiplicity, not the adaptivity"
   (`docs/audits/phase0/D_protocol.md` 1.5 (b)-(c), lines 275-289). Within a family, anything added after a reading is
   "exploratory, reported apart" (F-02 section 20; family B section 23; family O section 21); a later family on a
   *closed* specification "is not judged on this family's judged block" (B 15, lines 982-986; F-02 13, lines
   1134-1136; O 14, lines 1042-1043; the audit's R-8, which sends it to a placebo-differenced statistic or to
   confirmation). **No row yet rules on a family assembled from *carried* components**: the nearest rules point to
   disclosure in its prior exposure and to the confirmation as its evidence, as every draft already says of its own
   pass ("a pass is a development finding whose evidence is its confirmation", F-02 2, line 235-236).
5. **More lines, less power (E-051).** An intersection of lines is a tightening; "a tightening is accepted only with its
   level and power at the family's level shown before the pin", because "a powerless line fails profitable models"
   (E-051). The deciding lines' conjoint minimum detectable lift is computed on choice-block proxies before any judged
   read (E-051 M5-2; family B 0, lines 49-51, which declares itself a screen if that is far above the bar).
6. **Its own counts (E-052).** A composite's trades per session are the sum of its components'. F-02's fill intensity
   is "persistent, regime-like" (E-063 (1)); family R's admissions follow the volatility regime (R 0, lines 88-92); family
   O's openings cluster with their state (E-054 (2)). The sum persists at least as much, and its routed counts depend on
   the interaction. So K0 on the composite's own choice-block counts, C0 on its judged counts and the check on its
   routed counts are its own; no component's K0 transfers.
7. **Its floors are its own** (E-022 (2)), as above.

### 3.5 When a composite could be declared: the options and what each costs

No option is recommended here; each is listed with what it needs.

| option | what it is | what it needs | what it costs |
|---|---|---|---|
| **A. Before any component's judged read** | a family declared now whose cells are the stack of its components' stage-B picks (each chosen on the choice block only), judged once on the judged block | everything in 3.2-3.3; the precedence rules (2.3) fixed now, without knowing which stop F-02 will pick and so which base it lands on; the builds of 2.6 before its stage A | it spends a k now and tightens the level of every family pinned after it (E-028 (2)); F-02 is pinned next or not at all (E-048 (1)), so the composite would come after F-02 in k and before family B or O; it reads the judged block whatever its components' fates; a component killed at stage A or B leaves its part with no pick, and that cell dies, counted; its offer-level lines duplicate the components' |
| **B. After components carry, on the development data** | a family declared after its components carried, judged on the judged block | 3.2-3.3, with every component's judged read in its prior exposure; **a row ruling what such a family may claim there** (none exists, 3.4 item 4) | its choice followed the components' results (D_protocol 1.5 (b)-(c)); its offer-level lines re-read the components' offers; its claim is at most a development finding whose evidence is a confirmation |
| **C. After components carry, on unread data only** | a family declared before the confirmation window is read, whose only test is that window | 3.2-3.3; its confirmation's months computed from its conjoint power (3.7) and written before any confirmation data exist | the window is one, a purchase and the operator's; it competes with its own components' confirmations and with Stage 2's draft P-16 confirmation (3.7); if a component's confirmation reads it first, the operator decides whether it can still serve |
| **D. No trade-level composite** | the execution model is one carried design (a base plus one component) with the operator's menu choices among described levers (PP, FC, R-cap) | each described lever re-read on the carried design under its own pinned reading (`prereg/RD-nn_<slug>.md`, E-025 (1)), since PP and FC are read on P-14 and P-16, not on any carried design | its trade-level claim is the one component's; the menu choices carry no claim (E-023 (1)); a payout policy could be *tested* only if the operator changed E-023 first (PP 1, lines 99-100) |

### 3.6 E-051 and E-052 on a composite, precisely

- **E-051.** Before the pin: the level and power, at the composite's level, of every line that is a tightening (each
  added component line, the lesser-of-routings value line, any amplitude rule in a stage-B2 critical value), and the
  conjoint MDL of all deciding lines on choice-block proxies, used by a declared screen rule. B2-type slow components
  centred within the judged block, shaping dependence and not the mean (E-051's ruling; E-060 (1)).
- **E-052.** Before the pin: the fill intensity's persistence stated per component and for the union. At stage A, K0:
  `cons`'s size at the composite's level on a sign-flip null laid on the composite's own choice-block counts, a cell
  whose 95 % interval lies wholly above nominal killed. At stage C, C0 on the composite's judged counts before any
  outcome, and the same on its routed counts after the campaign; a pass not claimed above nominal (E-052 (1); F-02 9.0;
  family B 13 step 1 and step 6). The marginal-excess limit F-02 states for its K0 applies equally (E-063 (1)).

### 3.7 What the confirmation window would test

- **The window:** NQ from 2026-07-17, not on disk, refused by the reader, a purchase and NQ's fourth confirmation window
  only by the operator's decision (F-02 14, lines 1141-1146; family B 16, lines 990-993).
- **Who else targets it:** Stage 2's draft P-16 confirmation (`vendor/stage2/prereg/DRAFT_P16_confirmation.md`), F-02,
  family B, family O and family R (O 15, lines 1050-1052). "If any test reads it first, the lead records that before
  registration, and the operator decides" (F-02 14, lines 1147-1149).
- **What it tests:** the composite's trades -- each line on the window's offers at the registered one-sided 0.05, with
  the bound at 0.05/N beside (D-189's form), its value at the 95 % bound with stage C's per-place shares, resolution,
  the count check (family B 16, lines 997-1032 as the most complete form).
- **What it cannot test: P.** Six months is about one 63-start block; no interval on P exists there; the scorecard on
  the window is descriptive (F-02 14, lines 1164-1165).
- **How long:** at least six months, and at least the months at which **every deciding line together** has 80 % power
  for a lift equal to the judged lower bound at the family's level (family B 16, lines 1038-1046; F-02 14). An
  intersection of more lines needs at least as long as its most demanding component, so a composite's purchase is at
  least as large as any component's. "If that is more than the operator will buy, no confirmation is registered" (B 16,
  lines 1049-1050).

---

## 4. The order of operations

### 4.1 In plain words

First the program finishes checking its own tools (the calibration rerun, the fresh-seed check, the identities of the
gate, the recorder and the replay), and runs the readings that draw the user's path for the registered designs. Then the
trade-changing pieces are judged one at a time, in the order of their numbers: F-02 first, then family B, then family O,
with family R held back and possibly closed before it is numbered. The money-side readings (payout policy, other firms)
can run alongside, because they spend nothing. Only after at least one piece is judged does a composite become a
question with an answer, and the answer depends on which pieces passed, on which base, and whether the operator will buy
fresh data. At every step the user's path -- time and money to the first pass, the first payout and break-even, and
how evenly that falls across start days -- is shown beside the verdict, never as the verdict.

### 4.2 The sequence, as the queue stands (TASK_QUEUE in the lead's copy; E-062 (4), E-063)

1. **Tools and identities (heavy, one at a time; Q-55 running):** Q-55 (the calibration's clean rerun), then Q-83 (the
   fresh-seed validation; F-02's pin needs both, E-052 (2), E-063 (2)); then from the Q-97 commit Q-44 (the readings
   beside, the journey page's input), Q-22b, Q-80 (the gate's re-composed campaign), Q-89 (the recorder), Q-93 (the
   replay's class), Q-35 (where openings fall), Q-98 (money spent), Q-18 (P-14's stress checks), Q-45 (the breakeven
   move's fidelity). Light: Q-94 (recording on the replay), Q-97 (clean manifests), Q-66c (F-02's gatekeeper re-read).
2. **F-02 (k = 11):** pin, build, stages A-D (its sections 7-12). Stage D is already a two-component design (base plus
   tickets) whose floors can close it but not carry it (11.1).
3. **Family B (k at least 12):** after its sixth red-team read (Q-95), pin, run.
4. **Family O (next free k):** after its third draft (Q-87) and Q-55's power table (its 6.6), pin, run.
5. **Family R:** its third draft after F-02 and family B (Q-90; E-057 (2)); its drop rule may close it before any k
   (E-057 (1)), its supply question then going to a described reading (E-028 (2)).
6. **Alongside, spending nothing:** reading PP (Q-92) and reading FC (Q-91), each pinned as `RD-nn` and run once from a
   clean checkout; their menus to the operator; E-015's limits proposed by the lead from Q-44's file and approved by the
   operator before use (E-015 (2)).
7. **A carried piece:** registration, model card, registered development test, auditor, one confirmation (the
   operator's purchase) -- each draft's "What a pass and a fail mean".
8. **A composite**, if ever: by one of 3.5's options.

### 4.3 Each outcome, and what it opens or closes for a composite

| outcome | what it closes | what it opens |
|---|---|---|
| F-02 closes at stage A or B | no judged read; F-02's specification closed (13, line 1134) | -- |
| F-02 closes at stage C | the judged block's start days become prior exposure for later families (13, lines 1131-1132); any composite with F-02's levels goes to unread data only | -- |
| F-02 carries, 50- or 100-tick pick (base P-14) | -- | a composite on P-14 with family B's money side (if B carries) or with described levers (option D); not with family O or R as declared (2.4) |
| F-02 carries, 150-tick pick (base P-16) | -- | a composite on P-16 with family O or family R, once 2.3's conflict at place (c) has a declared rule; described levers (option D) |
| family B closes (its own text expects a screen) | B's features and population closed (15, lines 982-986) | -- |
| family B carries | -- | a composite on its own schedule and P-14's money side; with F-02's P-14 picks (slot shared); not with family O or R as declared |
| family O closes | the opening-timing slot stays P-16's; u3, family R's forecast at the opening, closes with it | -- |
| family O carries | -- | P-16 plus the waiting opening; composites with F-02's 150-tick pick (precedence at (c)), with reading PP (a composed class), not with R-cap (conflict) |
| family R closes before its pin | no k spent (E-057 (1)); the late-mark supply question goes to a described reading | -- |
| family R carries | -- | P-16 plus admissions; with family O (one module) |
| reading PP / FC read | nothing (nothing can close or carry) | menu choices for the operator, in their own decision row; each laid on a carried design only through a reading of its own on that design (3.5 D) |

### 4.4 Where the user's path is reported beside a composite's verdict

- **The measures** (E-014; CHARTER section 2): sessions and cash to the first pass and to the first payout; sessions to
  break-even, the share there by months 1, 2, 3, 6 and 12 and the share that fall back; the path's evenness (months with
  a positive net change, the longest run without a payout, the spread of monthly net, the deepest fall after break-even,
  payouts per month, the largest month's share of the year's payouts); P and S1-S5c. **Each as a distribution over start
  days** (median, p10, p90) with its uncertainty from the effective number of independent starts and the start day's
  share of the variance (E-015 (1)).
- **The money** (Q-86, `extended/user_spend.py` lines 10-14 and 22-35): fees paid and payouts received at the first
  pass, the first payout, break-even and each month end; the cash out of pocket before break-even; the return on spend;
  evaluations bought before the first pass.
- **The page:** `extended/journey_page.py`, registered as `journey_scorecard` (E-054 (1)), with its money section from
  Q-86's file; the verdict view first (0 % denial, the placement off, E-008 (2)), every firm response beside. Today it is
  built for the registered designs from Q-44's files; a composite's page needs the readings run on the composite's own
  design (its own result files through the same writers).
- **The designs read side by side for a composite:** the composite; each leave-one-out design (the composite less one
  component); the base; R\* = P-14 -- paired by start day, as every draft reads its design against its twin design and
  its base (O 13, lines 976-980; R 13, lines 1039-1043; F-02 12, lines 1063-1066). The leave-one-out differences say
  what each component did to the path, as a description: on the judged block's few independent starts (E-007 (2)) none
  is a test.
- **The menu:** E-015's limits, once the operator approves them before the run, as flags only -- "a limit never fails a
  design" (E-015 (3)); the evenness trade-off curve beside (E-015 (4)).
- **Not modelled, wherever it appears:** a user who stops when their own money runs out, the user's time, taxes (E-015
  (5)); Topstep's unstated news rules (E-034); and, for a composite with its own funded class, the Focused Trader models
  (E-059 (2)).

So the operator's measure -- the path, not a lump sum -- is on every page, beside every verdict. Under E-008 and E-015
it decides the menu, not the pass.

---

## 5. What is unknown, and how it could be found

| unknown | why it matters to a composite | how it could be found |
|---|---|---|
| where P-14's and P-16's funded openings fall (marks, hours, report days) | how much F-02's 08:30 tickets and family O's overnight wait compete for place (c) (O 5.5; F-02 10, line 896) | Q-35's run (heavy queue, E-062 (4)) |
| how often two components would want the firm's slot or the same account on the same session | the size of each interaction in 2.3, before any precedence rule is declared | a direction-free count on choice-block replays (proposed below); no such count exists |
| whether first-order value-map prices hold when two components share a place | C2 of any composite | a per-rung or re-solved value function (D-667's solver; F-02 19) |
| whether `cons` holds its level for a twin that cancels a side and a selection at once | a composite's offer-level line | a Q-16 / Q-82-type calibration of the joint form |
| whether the confirmation window can serve more than one test | options C and D's confirmations | the operator (D-107; F-02 14) |
| the Focused Trader models with a family's own funded class | E-007 (e)'s readings for a composite holding family O or reading PP | a separate build under its own row (E-059 (2)) |
| what `lock` means at another firm | reading PP with reading FC | each plan's verified payout rules (`config/rules_extended.yaml`), then a new described reading |
| whether D-281 (3)'s window would be where a timing filter has most of its uses | a composite timing openings at 08:30-09:00 is a different family needing the operator's ruling (O 5.5 item 6) | Q-35's count, then the operator |

---

## 6. If a composite became a family: what it would have to declare

- **Mechanism:** each component's own mechanism with its sources (the drafts' section 1), and the composition's own
  claim -- why the components' gains would add at the places they share -- with the expected sign of each interaction
  stated in advance (as family O states u3's, its 0 and 1).
- **Supply:** each component's supply at its own gates; the union's trades per session and their persistence (E-052);
  the slot's occupancy and how often streams meet; each place's reach with shared caps; the fallbacks; the
  composite's own resolution share on the merged stream.
- **Contract fit (CHARTER section 4):** at least five minutes from alert to order on every stream, hand entry; one
  position at a time across the firm with five minutes flat **across every stream** (cancel-on-entry, reservation);
  every trade resolving, at most 5 % to the flatten overall and each year, no time stops; realised risk in its
  allowance-capped form (E-022 (1), E-032 (3)); report-day entries strictly after 07:35:00 for new components, the
  registered trades' 07:35 kept and counted (E-039 (1)); FOMC days out; full-allowance resting tickets cancelled around
  in-window releases (F-02 11.2); conduct tier 1 (no hedging across accounts or firms, no simulator-fill exploitation, no
  maximum size into major news, nothing concealed, each account its own trades), tier 2 off and beside, tier 3 priced
  with the denial ladder; only verified rules.
- **Cells and their count:** the base (P-14 or P-16) x the components' picks (fixed from their stage B or their
  registrations) x each precedence rule declared for a conflict (for example, at place (c): a waiting account refuses a
  ticket / takes a ticket) x the stops and R it offers -- every one counted whether killed or read, plus any searched
  value; its k the next free; its seeds; its reads line; the confirmation declared before any development read.

---

## 7. For the lead

**Proposed TASK_QUEUE line** (only if the lead wants composites scoped before any component is judged):

| Q-NNN | **Where components would meet (a supply count, no outcome):** on P-16's and P-14's choice-block U1 replays (Q-17's adapter, the ledger on, as Q-35), count per session how often a newly funded account's opening, an 08:30 resting ticket's reachable account (F-02 section 10's rule) and a 09:05-15:05 mark (family R's population) would contend for the firm's one position or for the same account; counts only, read as `registered_design` on choice-block days only | wt-user | queued (after Q-35's run) | Q-35, Q-94 | heavy | 0 | E-NNN |

**Proposed decision row:**

| E-NNN | 2026-11-16 | **Q-99 read: how the program's components would compose into one execution model (`docs/research/composing_an_execution_model_2026-11-16.md`, wt/wt-scout) -- a structure note; no result value, bar or walk read; nothing declared or recommended.** Readings recorded: (1) an execution model has ten slots (schedule, entry, side, bracket and R, size, routing, purchases, the funded opening's timing, payout policy, firm); P-14, P-15 and P-16 share one money side and differ in their trade stream; each family or reading replaces one slot, and every family's judged design is already its base plus one component (F-02's stage D, family O's and family R's designs, family B's design (i)); (2) a component's offer-level line (C1) reads every offer independently, so it is unchanged by another component's routing or by a money-side lever, while its value line, the floors and the scorecard depend on the shared slot, seats, router and table and must be read on any composite's own design (E-022 (2)); (3) two conflicts on the funded opening are named for any future composite -- F-02 with family O (a waiting account and a resting ticket; neither draft names the other) and family O with R-cap -- and family B is not stackable with family O or R as declared (different populations and bases); (4) a composite is a new family under its own row: its own k at its pin, count, seeds, reads line and pin; components that each passed do not make it pass (different trades and places; first-order values that do not add; its own level; its choice informed by the components' judged reads -- the audit's between-family hole, D_protocol 1.5 (b)-(c), on which no row yet rules for carried components; E-051's power rule on its intersection of lines; E-052's checks on its own and its routed counts); (5) levers that add no trades (reading PP, reading FC, R-cap) enter an execution model only as the operator's menu choice, re-read on a carried design under a pinned reading of their own (E-023 (1)); (6) the options for when a composite could be declared, and their costs, are the note's section 3.5; until the lead chooses one, nothing changes. | Brief Q-99; the note; CHARTER sections 2-4; E-008, E-014, E-015, E-022, E-023, E-028, E-039, E-048, E-051, E-052, E-059, E-063. |

---

## Sources (files and rows, all read 2026-11-16)

- `CHARTER.md` (sections 1-6; lines cited inline).
- `DECISIONS.md` E-001 to E-060 (master 40a56a7); E-061 to E-063 (the lead's staged copy).
- `TASK_QUEUE.md`, `STATUS.md` (the lead's copy).
- `prereg/DRAFT_F-02_resting_levels.md`, `prereg/DRAFT_F-B_multifeature.md`, `prereg/DRAFT_F-O_opening_timing.md`,
  `prereg/DRAFT_F-R_resolution.md`, `prereg/DRAFT_F-P_payout_policy.md`, `prereg/DRAFT_RD_firms.md` (sections and lines
  cited inline).
- `docs/research/mechanisms_2026-11-15.md` sections 3.1-3.2; `docs/audits/phase0/D_protocol.md` section 1.5.
- `extended/gate.py` (docstring lines 1-66; `run_gate` lines 271-315; checks lines 121-139); `extended/user_beside.py`
  (lines 52-68, 254-270); `extended/place_records.py` (lines 1-56, 138-142); `extended/openings.py` (lines 1-30);
  `extended/user_spend.py` (lines 1-60); `extended/journey_page.py` (lines 1-60).
- `vendor/stage2/prereg/P-15_rc-s100-all.md`, `vendor/stage2/prereg/P-16_rc-s150-all-nr.md` (title blocks only).
