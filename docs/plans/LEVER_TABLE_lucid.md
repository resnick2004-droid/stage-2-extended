# The lever table: Lucid Trading $50K design search (Q-151b; beside Topstep's, Q-151)

Drafted 2026-11-20 on `wt/wt-payout` for the lead. **Status: groundwork for the search declaration (Wave 5.1), not a
declaration.** Nothing here is pinned or chosen, and no search or run is built. The table holds no result number and
types no rule value: a rule-derived bound is written as its key, and `extended/lever_space_firms.py` reads it.

**Where Lucid's rules come from.** Lucid's Terms of Use (modified 2026-11-13) forbid copying or monitoring its content
"by automated or unauthorized means" (E-197), so no session reads Lucid's sites. The loader reads two records only:

- this repository's record (`config/rules_extended.yaml`), which wins where it holds the key (`lucid.flex50k.payout_fee`,
  `lucid.flex50k.funded_monthly_fee`);
- Stage 2's verified Lucid ledger (`vendor/stage2/vendor/propfirms/firms/lucid-trading/rules.yaml`; Stage 2 D-30, D-31),
  read before the clause, on which E-197 keeps LucidFlex. A key `lucid.flex50k.<k>` is that ledger's `<k>`.

A rule in neither record is verified only from the operator's own transcription (`docs/OPERATOR_SETUP.md` item 11; no
Lucid screenshots are in the repository at this commit). Read with: Topstep's table
(`docs/plans/LEVER_TABLE_topstep50k.md`), whose 39 rows this one mirrors id for id; the operator's direction that each
firm is traded on its own execution protocol; RD-05's `LU40`, `LU50` and `LU` (`prereg/RD-05_firm_modes.md`); Stage 2's
Lucid adapter (`propedge.contract.lucid`, the identity of `tests/test_lever_space_firms.py`); CHARTER 3.3 to 3.5 and 4.

---

## 1. The plan, and why

**LucidFlex 50K, daily loss limit off**, in its two consistency configurations: the standard and the paid add-on (RD-05's
`LU40` and `LU50`). It is $50K, Topstep's size. It is the only Lucid plan on a verified record: E-197 found new terms on
LucidPro, LucidDaily and LucidDirect, read after the clause, so they verify nothing. Its mechanics are the nearest to
Topstep's Trading Combine. The drawdown is end-of-day trailing in both phases (`eval_drawdown_type`,
`funded_drawdown_type`). The funded account scales its contracts with profit (`funded_position_limit`), as Topstep's
does. The payout gate counts winning days above a floor (`payout_frequency_gate`), and the request is a share of profit
up to a cap (`payout_cap`), as on Topstep's standard path. The daily-loss-limit version is a different account chosen
at checkout, as Topstep's election is (A14, dropped). The consistency setting is the checkout's other switch, and it
changes the price and the evaluation's rule together. It is searched as the price path is on Topstep (A4).

What differs from Topstep and matters to the design: the evaluation's consistency share and fewest days are Lucid's
(and the add-on's); the evaluation allows a larger contract limit from the start, with no scaling (`eval_position_limit`);
the funded account's scaling ladder is Lucid's own; a payout request itself locks the floor
(`payout_balance_consequence`); an account ends after a fixed number of payouts (`payout_frequency_gate`); and the
account caps are per household, with a shared total across evaluations and funded accounts (`max_accounts`).

## 2. Sources and refusals

As Topstep's section 1, and as the MFFU table's section 2. A key absent from both records, or present with any status
but `verified`, refuses its lever with **`NotVerified`**. It is never guessed. No Lucid lever has a search-year reading
(S1 needs its own). The last column is the mechanical comparison with Topstep (`lever_space_firms.vs_topstep`, under no
S1 reading), defined as in the MFFU table.

## 3. The levers

In the prose, `P.` stands for `lucid.flex50k.`. Every key in the rows is written in full.

### 3.1 Trigger layer

| id | layer | lever | range and step | source | unit; what its estimate reads | depends on | class | vs Topstep |
|---|---|---|---|---|---|---|---|---|
| T1 | trigger | signal source of a component | Topstep's T1 (`coin`, `p14`, `p16`, `rl3`) | declared: E-208's dispositions | categorical; reads nothing | T2, T3, T4, T5, A16 | searched | identical |
| T2 | trigger | session of a component | every session of Lucid's day, as Topstep's T2, once the day is on a record | arithmetic: `lucid.flex50k.trading_hours` (absent) | a session | T1, T2b, T3 | searched | refused -- `lucid.flex50k.trading_hours` is on neither record: Lucid's reopen, any flat-by time and its last entry |
| T2b | trigger | the NY AM / NY PM boundary | to declare (Wave 3.3) | to declare | a wall-clock time | T2 | declared | identical |
| T3 | trigger | entry window: a component's offer marks | from Lucid's reopen to its last new entry, in Topstep's mark step | arithmetic: `lucid.flex50k.trading_hours` (absent) | minutes after the reopen | T2, T4, A3 | searched | refused -- `lucid.flex50k.trading_hours` |
| T4 | trigger | latency L, alert to order | Topstep's T4 | declared: E-202 (2)(c); CHARTER 3.3 (g) | clock minutes | T1, T3, T5 | searched | identical |
| T5 | trigger | entry type | `market`, `limit`, held against Lucid's prohibition of exploiting platform or simulator mechanics (`lucid.flex50k.prohibited_conduct`) | declared: E-202 (2)(d); F-04 6.1 R-4 | order type | T1, T4, T6 | searched | differs -- the same choices, held against Lucid's conduct rule |
| T6 | trigger | how long a limit works | Topstep's T6 | declared: F-04 6.1 | minutes | T5 | declared | identical |
| T7 | trigger | admission by forecast resolution | refused until fitted, as Topstep's | **a search-year reading, to compute** | a probability | T1, T3, S1, S2 | searched | identical |
| T8 | trigger | side rule | the coin side; never opposite positions. Lucid prohibits hedging across accounts, users and firms (`lucid.flex50k.prohibited_conduct`) | declared: CHARTER 3.2, 3.5 | side rule | T1, T5, A15 | declared | differs -- the same rule, held against Lucid's hedging prohibition |

### 3.2 Trade-shape layer

| id | layer | lever | range and step | source | unit; what its estimate reads | depends on | class | vs Topstep |
|---|---|---|---|---|---|---|---|---|
| S1 | trade shape | stop width | a multiple k of the trailing range; k's range is Lucid's own search-year translation of its caps (`lever_space_firms.stop_caps('lucid')`: the registered floor, and the widest stop at which one micro fills the larger room of `lucid.flex50k.eval_drawdown_amount` and `lucid.flex50k.funded_drawdown_amount`) | **a search-year reading, to compute** (Lucid's own) | multiple of the session's trailing range | T2, S2, S3, S4, S5 | searched | differs -- Lucid's caps and sessions; no reading yet |
| S2 | trade shape | reward-to-risk w | Topstep's S2 | declared: RD-05 2.6 | ratio | S1, A1, A2 | searched | identical |
| S3 | trade shape | dollar risk per trade, evaluation | from one micro at the floor stop to the evaluation's room (`lucid.flex50k.eval_drawdown_amount`, end-of-day trailing by `lucid.flex50k.eval_drawdown_type`), whole micros, within `lucid.flex50k.eval_position_limit` (no scaling in the evaluation) | arithmetic: the keys and the stop's floor | dollars at the stop | S1, S5, A1 | searched | differs -- Lucid's room and its larger evaluation limit |
| S4 | trade shape | dollar risk per trade, funded | from one micro at the floor stop to the funded room (`lucid.flex50k.funded_drawdown_amount`, `lucid.flex50k.funded_drawdown_type`), within the profit-scaled ladder of `lucid.flex50k.funded_position_limit` | arithmetic: the keys | dollars at the stop | S1, S5, A2, A5 | searched | differs -- Lucid's ladder, not `funded_scaling_plan` |
| S5 | trade shape | instrument mix | `MNQ`, `mixed`, counted against `lucid.flex50k.eval_position_limit` and the ladder of `lucid.flex50k.funded_position_limit` | declared: F-04 6.1; the counting from the keys | categorical | S3, S4 | searched | differs -- Lucid's limits |
| S6 | trade shape | maximum hold (a time stop) | **dropped**: CHARTER 4 | declared: CHARTER 4 | -- | -- | dropped | identical |
| S7 | trade shape | breakeven stop move | **dropped**: off; exploiting simulator mechanics is prohibited (`lucid.flex50k.prohibited_conduct`) and is tier 1 | declared: RL3 6.1; F-04 6.1 | -- | T1 | dropped | identical |
| S8 | trade shape | partial exits, scaling in | **dropped** | declared: F-04 6.1 | -- | -- | dropped | identical |
| S9 | trade shape | contracts | **dropped as a lever**: derived | arithmetic: RD-05 part B's sizing | -- | S1, S3, S4, S5 | dropped | identical |

### 3.3 Account-policy layer

| id | layer | lever | range and step | source | unit; what its estimate reads | depends on | class | vs Topstep |
|---|---|---|---|---|---|---|---|---|
| A1 | account policy | steady or flip, evaluation | `steady`; or `flip` at r_flip = target / (k_E x w), cut to the room, per configuration (A4). Target `lucid.flex50k.eval_profit_target`; k_E from `lucid.flex50k.eval_consistency_rule` and `lucid.flex50k.eval_min_days` (the add-on's share and days from their verified notes); the room `lucid.flex50k.eval_drawdown_amount`; a broken share delays the upgrade rather than failing it | arithmetic: RD-05 part A | policy | S2, S3, A4 | searched | differs -- Lucid's share and days, two configurations |
| A2 | account policy | steady or flip, funded | `steady`, `flip` at b\* / (k_F x w): k_F the winning days of `lucid.flex50k.payout_frequency_gate`, b\* the balance at which the share-of-profit request of `lucid.flex50k.payout_cap` reaches its cap, cut to the room `lucid.flex50k.funded_drawdown_amount`; no funded consistency rule (`lucid.flex50k.funded_consistency_rule`) | arithmetic: RD-05 part A | policy | S2, S4, A5 | searched | differs -- Lucid's gate and cap |
| A3 | account policy | session rule q ("when to stop") | `one`, `all`, `cap`: in the evaluation until the session's net reaches the configuration's share (`lucid.flex50k.eval_consistency_rule`) x `lucid.flex50k.eval_profit_target`; no funded cap (`lucid.flex50k.funded_consistency_rule`) | declared: F-04 6.1; the allowance by rule | categorical | T3, A4, A5 | searched | differs -- Lucid's share; no funded cap |
| A4 | account policy | checkout configuration (the price path) | `LU40` (the standard share) or `LU50` (the add-on), each at its one-time price: `lucid.flex50k.eval_fee` and its verified note's configuration lines; the share and days by `lucid.flex50k.eval_consistency_rule` and `lucid.flex50k.eval_min_days`; no activation fee (`lucid.flex50k.funded_type`) | rule: the operator's card read (Stage 2 D-31) | categorical | A1, A3 | searched | differs -- Lucid's two configurations change the price and the rule together; Topstep's two paths change the price alone |
| A5 | account policy | payout path | one path, `lucid_cycle`: `lucid.flex50k.payout_frequency_gate` (winning days above a floor and a positive net per cycle; a fixed number of payouts per account, then the live review), the share-of-profit cap `lucid.flex50k.payout_cap`, `lucid.flex50k.payout_min`, `lucid.flex50k.payout_split` | rule | -- | A2, A3, A18, A19 | declared | differs -- one path, where Topstep chooses between two |
| A6 | account policy | funded seats held at once | 1 to `lucid.flex50k.max_accounts` (per household), step 1; with the evaluations at once inside the household's total across evaluations and funded accounts (the note of `lucid.flex50k.max_accounts`; `lucid.flex50k.eval_count_limit`) | rule | accounts | A7, A8, A15 | searched | differs -- Lucid's household cap and shared total |
| A7 | account policy | evaluations running at once (C) | 1 to the lesser of Topstep's declared upper end and `lucid.flex50k.eval_count_limit`, step 1; refused with A6 beyond the shared total (`lucid.flex50k.max_accounts`) | declared: RD-03 2.2, cut by the keys | accounts | A6, A8, A11 | searched | differs -- Lucid states caps, Topstep none |
| A8 | account policy | banking: buy evaluations while a pass waits | `on`, `off`: evaluations may be kept in reserve, and traded, while the funded seats are full (the notes of `lucid.flex50k.max_accounts` and `lucid.flex50k.eval_count_limit`) | declared: RD-03 2.2 | categorical | A6, A7, A9 | searched | differs -- Lucid's reserve rule, not `hold_queue_behaviour` |
| A9 | account policy | the hold's expiry | refused: no record states how long an evaluation in reserve may wait (`lucid.flex50k.hold_expiry_days`) | declared (readings of a rule not on the record) | reading | A8, A10 | declared | refused -- `lucid.flex50k.hold_expiry_days` is on neither record |
| A10 | account policy | evaluation-purchase rule | Topstep's A10; one-time purchases, no time limit and no rebilling (`lucid.flex50k.eval_time_limit`) | declared: RD-03 2.3 | categorical | A9, A11 | searched | differs -- the same choices on Lucid's one-time billing |
| A11 | account policy | evaluation-purchase budget | Topstep's A11, once a record says that no rule limits starts | declared: Stage 2 D-501; `lucid.flex50k.account_start_rate_limit` | purchases a month | A7, A10 | searched | refused -- `lucid.flex50k.account_start_rate_limit` is on neither record |
| A12 | account policy | Back2Funded reactivations | **dropped**: Topstep's product (Stage 2's Lucid adapter sets it off) | declared | -- | A4, A6, A18 | dropped | differs -- Topstep's lever loads; Lucid has none |
| A13 | account policy | resets | **dropped**: Stage 2's Lucid engine repurchases a failed evaluation; a reset (`lucid.flex50k.eval_reset_fee`) needs an adapter | declared: RD-03 2.5 | -- | A4 | dropped | identical |
| A14 | account policy | daily-loss-limit election at checkout | **dropped**: a different account (`lucid.flex50k.eval_daily_loss_limit`) | declared: RD-05 2.3 | -- | S3, S4 | dropped | identical |
| A15 | account policy | routing | to declare (Wave 3.3), with the no-opposing-positions guard | to declare | rule | A6, A7, A16, T8 | searched | identical |
| A16 | account policy | signal mix | to declare | to declare | shares | T1, A15 | searched | identical |
| A17 | account policy | state rule | to declare | to declare | rule | S3, S4, A1, A2 | searched | identical |
| A18 | account policy | the first payout request (RD-02 L1) | `elig` (the first close at which `lucid.flex50k.payout_frequency_gate` opens and the request reaches `lucid.flex50k.payout_min`), `lock` (once the floor has locked by reach, `lucid.flex50k.eval_drawdown_lock`). A request itself locks the floor (`lucid.flex50k.payout_balance_consequence`) | declared: RD-02 6.1 | rule | A5, A19 | searched | differs -- Lucid's gate, and the request that locks the floor |
| A19 | account policy | the request amount (RD-02 L2) | `max`, `half`, once a record says a request may be below the cap's maximum (`lucid.flex50k.payout_request_amount_choice`; `lucid.flex50k.payout_cap`, `lucid.flex50k.payout_min`) | declared: RD-02 6.1 | share of the maximum | A5, A18 | searched | refused -- `lucid.flex50k.payout_request_amount_choice` is on neither record |
| A20 | account policy | request cadence after the first payout | every eligible close: a new cycle's winning days after each payout (`lucid.flex50k.payout_frequency_gate`) | declared: RD-02 6.1 | -- | A18 | declared | differs -- Lucid's cycle |
| A21 | account policy | payout method | to choose once the methods' fees are on a record (`lucid.flex50k.payout_fee`; the lag `lucid.flex50k.payout_processing_days`) | declared | -- | -- | declared | refused -- `lucid.flex50k.payout_fee` is unstated in this repository's record, which wins |

## 4. The comparison with Topstep

**identical** (15): T1, T2b, T4, T6, T7, S2, S6, S7, S8, S9, A13, A14, A15, A16, A17.

**differs** (18): T5, T8, S1, S3, S4, S5, A1, A2, A3, A4, A5, A6, A7, A8, A10, A12, A18, A20.

**refused** (6): T2, T3, A9, A11, A19, A21.

Why the differing levers differ, in short:

- **Contracts (S3, S4, S5).** The evaluation has a larger flat limit from the start. The funded account scales on
  Lucid's own ladder, not Topstep's `funded_scaling_plan`.
- **The evaluation's pass and its price together (A1, A3, A4).** The checkout's consistency setting changes the share,
  the fewest passing days and the price at once. So the flip size and the session cap differ per configuration.
- **The payout (A2, A5, A18, A20).** One path, with a winning-day cycle, a share-of-profit cap, a request that locks the
  floor, and a fixed number of payouts per account before the live review. Topstep has two paths and no payout count.
- **Accounts (A6, A7, A8, A10, A12).** The caps are per household, with a shared total (A6 with A7 is refused beyond it).
  Evaluations may wait in reserve. Purchases are one-time. There is no Back2Funded.
- **Conduct floors read from Lucid's record (T5, T8)**, and S1 needs Lucid's own reading.

## 5. Combinations refused and floors fixed

Every Topstep floor (its section 5) holds. `lever_space_firms.check_design`, which `sample` runs on every draw, refuses
**conduct tier 1 for every firm**. **Lucid permits trade copiers and the same strategy on several accounts**
(`copy_trading_terms`, `multi_account_same_strategy`); **this repository does not**: one trade copied across accounts
is tier 1 (CHARTER 3.5, E-221), and accounts alternate. It also refuses automated or API order entry, a setting of a
refused lever, a setting outside its range, and funded seats with evaluations beyond the household's total. The floors
Lucid's own record adds are listed below. Each is read in the engine.

- **Microscalping** (`prohibited_conduct`): profits from trades held a few seconds are forfeited. The designs here hold
  for minutes, but the engine counts it.
- **The household** (`max_accounts`): the caps are per household, and the move to live closes every simulated account
  (Stage 2's household-closure reading, conservative by default).
- **The payout count** (`payout_frequency_gate`): each account ends after its last allowed payout.
- **News**: LucidFlex allows news trading (`news_trading_terms`). CHARTER 4's windows still bind every design.

## 6. The work list: rules to verify (by the operator's transcription, OPERATOR_SETUP item 11)

No session reads Lucid's sites (E-197). Each key below is verified only from the operator's screenshots, recorded by the
rules-verifier under a decision row. It refuses the levers named, or (`engine`) must be verified before the engine can
run any Lucid design (`lever_space_firms.ready('lucid')`). This worker verified none of them.

| key | status | refuses |
|---|---|---|
| `lucid.flex50k.trading_hours` | absent | T2, T3, engine |
| `lucid.flex50k.hold_expiry_days` | absent | A9 |
| `lucid.flex50k.account_start_rate_limit` | absent | A11 |
| `lucid.flex50k.payout_request_amount_choice` | absent | A19 |
| `lucid.flex50k.payout_fee` | unstated (this repository's record; Stage 2's ledger: unverified) | A21 |
| `lucid.flex50k.funded_monthly_fee` | unverified (this repository's record) | engine (Stage 2 charges none and labels every Lucid result an upper bound) |

## 7. Interpretations made in this table (Q-151b)

1. **Stage 2's Lucid ledger counts as a verified record.** The brief names Stage 2's `config/rules.yaml`, this
   repository's record and `docs/RULES_CURRENCY.md`. Lucid's terms in Stage 2 live in its vendored Lucid ledger, which
   E-197 keeps LucidFlex on and which `firm_terms` and RD-05 already read (`firm_terms.LUCID_LEDGER`). Its entries were
   read on or before 2026-11-05, before Lucid's clause of 2026-11-13. A newer Lucid rule comes only by the operator's
   hand.
2. **The plan** is LucidFlex 50K with the daily loss limit off, in both consistency configurations (section 1). The two
   configurations are one lever (A4), as Topstep's two price paths are.
3. **The add-on configuration's figures** (its share, fewest days and price) are parsed from the verified entries'
   notes, as Stage 2's adapter does. `tests/test_lever_space_firms.py` holds them equal to the adapter's.
4. **A key absent from both records refuses its lever** (`NotVerified`). The absent keys are named `lucid.flex50k.<term>`
   (this table's proposal for the verifier).
5. **A5 is declared, not searched**: LucidFlex has one payout path.
6. **A7's upper end** is the lesser of Topstep's declared upper end and Lucid's evaluation cap. The shared household
   total is a combination rule in `check_design`, not a bound.
7. **The funded monthly fee** does not refuse A4: the configurations do not differ by it on the record. It is an engine
   prerequisite, because it costs every Lucid journey.
8. **The declared parameters of Topstep's table** are carried as ranges of the user's behaviour, as in the MFFU table's
   interpretation 6. The search declaration must extend RD-02's and RD-03's to Lucid by name.
