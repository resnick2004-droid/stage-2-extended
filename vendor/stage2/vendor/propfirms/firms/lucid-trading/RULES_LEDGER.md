# Rules ledger — Lucid Trading (LucidFlex, $50,000 account — tier per D-06)

One row per rule. **Nothing in this repository may depend on a rule whose status is not
`verified`** — `propfirms/spec.py` loads the machine-readable copy (`rules.yaml`, keys
match 1:1) and raises otherwise. Status vocabulary and the official-source rule:
[`firms/README.md`](../README.md). Update a row with `/verify-rule <firm> <rule>`; the
rules-verifier agent writes both files together and appends a `DECISIONS.md` entry.

> Values are written in canonical form (the number the code loads), with the human reading
> in brackets after it — a value column that says only "90/10" cannot be checked against
> `0.9`.

**Official domains:** `lucidtrading.com` (main site; refuses non-browser clients — HTTP 403
on 2026-10-04, not readable by an agent on 2026-10-30), `support.lucidtrading.com` (the
firm's official help centre, its canonical host on 2026-10-30; masthead "Lucid Home" links to
lucidtrading.com) and `intercom.help/lucid-trading` (the same help centre's host on
2026-10-04, same article ids). **Program captured:** LucidFlex at $50,000 — the first plan
listed on the firm's own help centre and the one with the fullest rule set; the same $50K
geometry exists under other plan names (§E). Since the October 2026 customization (article
16226050) the LucidFlex checkout has two settings, four configurations (§E 10); the rows
carry the **standard 40 % consistency**, and the modelled variant is **DLL OFF**.

**Reading history:** first captured **2026-10-04** on intercom.help/lucid-trading (D-07;
operator reads D-22, D-28). **Every row re-read 2026-10-30** on support.lucidtrading.com by
the rules-verifier standard (D-30): a changed row says CHANGED and keeps its earlier value
in brackets; the yaml notes carry the full quotes and history. **Prices read 2026-11-05** from the official
pricing cards on lucidtrading.com (operator's screenshots, D-31): `eval_fee` and
`eval_reset_fee` verified again; the funded rules card cross-checked four rows.

## A. Evaluation account

| key | rule | value | official page id and URL | date read | verified by | status |
|---|---|---|---|---|---|---|
| `eval_profit_target` | profit target | `3000` [$3,000; re-verified, unchanged] | [12945790-lucidflex-evaluation-account](https://support.lucidtrading.com/en/articles/12945790-lucidflex-evaluation-account) — $50K row: "$50,000 \| $3,000 \| $2,000 \| 40% (50% with add-on) \| 4 mini or 40 micros" | 2026-10-30 | rules-verifier agent (D-30) | verified |
| `eval_drawdown_amount` | maximum drawdown | `2000` [$2,000 MLL; re-verified, unchanged] | [12945815-lucidflex-drawdown](https://support.lucidtrading.com/en/articles/12945815-lucidflex-drawdown) — $50K row: MLL $2,000, Initial Trail Balance $52,100, Locked MLL Balance $50,100 | 2026-10-30 | rules-verifier agent (D-30) | verified |
| `eval_drawdown_type` | drawdown type: `eod_trailing` / `intraday_trailing` / `static` | `eod_trailing` [re-verified, unchanged] | [12945815-lucidflex-drawdown](https://support.lucidtrading.com/en/articles/12945815-lucidflex-drawdown) — "LucidFlex evaluation and funded accounts use an End-of-Day Drawdown (EOD Drawdown) system to calculate the Max Loss Limit (MLL)." | 2026-10-30 | rules-verifier agent (D-30) | verified |
| `eval_drawdown_lock` | does/when the trailing floor lock | `locks_at_start_plus_100` [floor stops at $50,100 once highest EOD close exceeds $52,100; re-verified, unchanged] | [12945815-lucidflex-drawdown](https://support.lucidtrading.com/en/articles/12945815-lucidflex-drawdown) — "Once your account exceeds the Initial Trail Balance, the MLL locks and no longer moves."; "Once the account exceeds the trail, the MLL locks at the initial balance plus $100" | 2026-10-30 | rules-verifier agent (D-30) | verified |
| `eval_daily_loss_limit` | daily loss limit, if any | `optional_at_checkout` [re-verified, value unchanged; NEW text: "The DLL is a soft breach, so if you hit it you will simply be locked out until the next trading session."; DLL ON = lower price + On Demand (intraday) payouts in funded; DLL OFF = none in either phase, higher price, "Payouts follow the regular end-of-day schedule"; amount when on still not stated; **2026-11-05 (D-31)**: the pricing card shows the $50K amount when ON, **$1,200** (DLL OFF "+$35"; [evidence/2026-11-05](evidence/2026-11-05/README.md))] | [16226050-lucidflex-customization](https://support.lucidtrading.com/en/articles/16226050-lucidflex-customization); [12945790](https://support.lucidtrading.com/en/articles/12945790-lucidflex-evaluation-account) — "Customize at checkout: Daily Loss Limit On or Off, and 40% or 50% consistency" | 2026-10-30 | rules-verifier agent (D-30) | verified |
| `eval_consistency_rule` | consistency rule | `0.40` [**CHANGED 2026-10-30**: largest day ≤ 40 % of evaluation profit is the standard; 50 % is a paid checkout add-on ("Added at checkout for a small fee"), not modelled; evaluation only — was `0.50` (read 2026-10-04, D-07, then the only option)] | [12945805-lucidflex-consistency-percentage](https://support.lucidtrading.com/en/articles/12945805-lucidflex-consistency-percentage) — "In LucidFlex evaluation accounts your Consistency Percentage must be 40% or less to be eligible to upgrade to a LucidFlex funded account. If you added the 50% consistency add-on at checkout, it must be 50% or less." | 2026-10-30 | rules-verifier agent (D-30) | verified |
| `eval_min_days` | minimum trading days | `3` [**CHANGED 2026-10-30**: no standalone rule; fastest pass under the standard 40 % consistency (2 days with the add-on) — was `2` (read 2026-10-04, D-07: "you can pass in two days" under the then-only 50 % rule)] | [12945790-lucidflex-evaluation-account](https://support.lucidtrading.com/en/articles/12945790-lucidflex-evaluation-account) — "Pass in as few as 3 days with 40% consistency, or 2 days with the 50% consistency add-on" | 2026-10-30 | rules-verifier agent (D-30) | verified |
| `eval_position_limit` | maximum position size | `4 minis / 40 micros` [full size from day one: "There is no scaling plan in the evaluation phase."; re-verified, unchanged] | [12945790-lucidflex-evaluation-account](https://support.lucidtrading.com/en/articles/12945790-lucidflex-evaluation-account); scaling exception in [12945808](https://support.lucidtrading.com/en/articles/12945808-lucidflex-scaling-plan) | 2026-10-30 | rules-verifier agent (D-30) | verified |
| `eval_fee` | evaluation fee and billing basis | `115.50` [$115.50 one-time, **VERIFIED 2026-11-05 (D-31)** from the official 50K Flex Eval pricing card (operator's browser screenshots, [evidence/2026-11-05](evidence/2026-11-05/README.md)): "ONE TIME FEE $165 $115.50 W/ COUPON AT CHECKOUT" with the DLL OFF ("+$35"), On Demand Payouts OFF, consistency 40 % — the modelled configuration (§E 10, Option 3). The coupon price is recorded: the operator, "Coupons are a multiple time thing not one time thing". Beside it (with coupon; list): DLL OFF + 50 % add-on $130.20 ($185; add-on "+$14.70"); DLL ON ($1,200) + 40 % $80.50 ($115); DLL ON + 50 % not captured. Billing basis one-time (12945790). HISTORY: reopened 2026-10-30 (D-30, no readable price); before that `$90 DLL-on / $105 DLL-off, one-time`, operator read 2026-10-04 (D-22) — P-05..P-07's recorded basis] | lucidtrading.com pricing card ([evidence/2026-11-05](evidence/2026-11-05/README.md)); [12945790](https://support.lucidtrading.com/en/articles/12945790-lucidflex-evaluation-account); [16226050](https://support.lucidtrading.com/en/articles/16226050-lucidflex-customization) | 2026-11-05 | operator screenshots, recorded D-31 | verified |
| `eval_reset_fee` | reset fee and policy | `115` [$115 per reset, **VERIFIED 2026-11-05 (D-31)** from the same card ("Reset Fee $115", DLL OFF, 40 %; [evidence/2026-11-05](evidence/2026-11-05/README.md)). Beside it: DLL OFF + 50 % $130; DLL ON + 40 % $80. Policy (2026-10-30, D-30): "If a trader fails an evaluation account, they may purchase a reset from the trader dashboard." (11404620); "Traders can manually purchase a reset at any time before that 30-day period expires." (11404632). HISTORY: price unstated 2026-10-30 (D-30); `none_published — failed evals repurchase at $105` 2026-10-04 (D-28), P-05..P-07's recorded basis] | lucidtrading.com pricing card ([evidence/2026-11-05](evidence/2026-11-05/README.md)); [11404620-simulated-account-fees](https://support.lucidtrading.com/en/articles/11404620-simulated-account-fees); [11404632](https://support.lucidtrading.com/en/articles/11404632-inactivity-policy) | 2026-11-05 | operator screenshots, recorded D-31 | verified |
| `eval_count_limit` | simultaneous evaluations allowed | `10` ["Up to 10 active evaluation accounts per household or family."; shared pool: "maximum of 10 accounts in total across evaluation accounts and funded accounts"; reserved evaluations close at a live move (§E 12); re-verified, unchanged] | [11404617-maximum-number-of-accounts](https://support.lucidtrading.com/en/articles/11404617-maximum-number-of-accounts) | 2026-10-30 | rules-verifier agent (D-30) | verified |
| `eval_time_limit` | time limit, if any | `none` ["take as long as you need to pass"; caveat: accounts with < $1 net P/L in 30 calendar days are deleted as abandoned, article 11404632; re-verified, unchanged] | [12945790-lucidflex-evaluation-account](https://support.lucidtrading.com/en/articles/12945790-lucidflex-evaluation-account) | 2026-10-30 | rules-verifier agent (D-30) | verified |

## B. Funded account

| key | rule | value | official page id and URL | date read | verified by | status |
|---|---|---|---|---|---|---|
| `funded_type` | funded account type and activation fee | `sim_funded` [$0 activation: "No activation fees to upgrade to funded account"; activation within 5–30 min; value unchanged. After the 5th payout: **the live review pool, the move at the risk team's discretion** (16558826: "All live transitions occur at the discretion of the Lucid risk team.") — read 2026-10-04 as an automatic move live (D-07)] | [12945795-lucidflex-funded-account](https://support.lucidtrading.com/en/articles/12945795-lucidflex-funded-account) — description: "The LucidFlex funded account is a simulated futures trading account where traders build capital to earn payouts and potentially be moved to live markets."; [16558826-new-live-structure](https://support.lucidtrading.com/en/articles/16558826-new-live-structure) | 2026-10-30 | rules-verifier agent (D-30) | verified |
| `funded_drawdown_amount` | funded drawdown | `2000` [$2,000 MLL, same table as evaluation; re-verified, unchanged] | [12945815-lucidflex-drawdown](https://support.lucidtrading.com/en/articles/12945815-lucidflex-drawdown); [12945795](https://support.lucidtrading.com/en/articles/12945795-lucidflex-funded-account) — "$50,000 \| $2,000 \| Optional \| Yes \| 4 mini or 40 micros" | 2026-10-30 | rules-verifier agent (D-30) | verified |
| `funded_drawdown_type` | funded drawdown type and lock behaviour (incl. after payouts) | `eod_trailing` [same EOD system; locks at $50,100; on payout request: "Once you request a payout from LucidFlex, your MLL automatically adjusts to the Locked MLL Balance"; re-verified, unchanged] | [12945815-lucidflex-drawdown](https://support.lucidtrading.com/en/articles/12945815-lucidflex-drawdown) | 2026-10-30 | rules-verifier agent (D-30) | verified |
| `funded_daily_loss_limit` | funded daily loss limit | `optional_at_checkout` ["LucidFlex funded accounts have an optional Daily Loss Limit, no consistency rule and no payout buffer."; checkout choice carries to funded; NEW: soft breach, DLL ON brings On Demand Payouts (§E 11); value unchanged; **2026-11-05 (D-31)**: the funded rules card reads "DLL (Below Initial Trail) $1,200" — the amount when ON ([evidence/2026-11-05](evidence/2026-11-05/README.md))] | [12945795-lucidflex-funded-account](https://support.lucidtrading.com/en/articles/12945795-lucidflex-funded-account); [16226050](https://support.lucidtrading.com/en/articles/16226050-lucidflex-customization) | 2026-10-30 | rules-verifier agent (D-30) | verified |
| `funded_consistency_rule` | consistency rule on the funded side / for payouts | `none` ["There is no Consistency Percentage on LucidFlex funded accounts"; "Consistency applies to the evaluation only. Funded LucidFlex accounts have no consistency rule."; payouts gated by winning days instead, see §C; re-verified, unchanged] | [12945795-lucidflex-funded-account](https://support.lucidtrading.com/en/articles/12945795-lucidflex-funded-account) | 2026-10-30 | rules-verifier agent (D-30) | verified |
| `funded_position_limit` | position limit and scaling plan | `4 minis / 40 micros, profit-scaled` [2 minis at $0–999, 3 at $1,000–1,999, 4 at $2,000+; "The scaling plan updates at the end of each session, so your limits will not update in real-time throughout the day."; FAQ: payouts may move the tier down; re-verified, unchanged; cross-check 2026-11-05 (D-31): the funded rules card reads "4 Mini OR 40 Micros", "Scaling Plan Yes"] | [12945808-lucidflex-scaling-plan](https://support.lucidtrading.com/en/articles/12945808-lucidflex-scaling-plan) | 2026-10-30 | rules-verifier agent (D-30) | verified |
| `funded_monthly_fee` | recurring funded-account fees | — [still unstated 2026-10-30; the 2026-11-05 funded rules card (D-31) shows activation FREE and no recurring fee — absence is not a statement, row stays open: no recurring fee mentioned anywhere read; one-time billing and $0 activation stated, but absence of a funded monthly/data fee is never stated explicitly — not assumed] | [11404620-simulated-account-fees](https://support.lucidtrading.com/en/articles/11404620-simulated-account-fees) | 2026-10-30 | — | unverified_human_input_required |

## C. Payout policy

| key | rule | value | official page id and URL | date read | verified by | status |
|---|---|---|---|---|---|---|
| `payout_min` | minimum payout | `500` ["Minimum payout request: $500"; re-verified, unchanged] | [12945796-lucidflex-payouts](https://support.lucidtrading.com/en/articles/12945796-lucidflex-payouts) | 2026-10-30 | rules-verifier agent (D-30) | verified |
| `payout_cap` | payout cap per request/period | `min(0.50 * profits, 2000) per request` [$50K: "50% of Profit up to $2,000"; the bullet above the table says "50% of their account balance up to a maximum dollar amount" — the table cell controls; "the maximums here do not scale up with more payouts"; lifetime ≤ 5 payouts per account → ≤ $10,000 sim payouts; re-verified, unchanged] | [12945796-lucidflex-payouts](https://support.lucidtrading.com/en/articles/12945796-lucidflex-payouts) | 2026-10-30 | rules-verifier agent (D-30) | verified |
| `payout_frequency_gate` | when payouts may be requested | `any day, per cycle: net profit >= $1 and 5 days >= $150; max 5 payouts, then the live review pool (discretionary)` [**CHANGED 2026-10-30 in the post-cap wording only** — was "…; max 5 payouts then live" (D-07); gate and 5-payout maximum unchanged: "There is no fixed payout window, you may request a payout any day after meeting all eligibility criteria."; "Traders must earn at least the minimum required profit on 5 separate days during the payout cycle." ($150 on $50K); "Traders must have positive net profit (even just $1) during each payout cycle in order to request a payout."; "Payout 5 represents the maximum payout level" and "All live transitions occur at the discretion of the Lucid risk team." (16558826); DLL-off payouts "follow the regular end-of-day schedule" (16226050); cross-check 2026-11-05 (D-31): the funded rules card reads "Min Days of Profit 5 of $150", "Days to Payout 5", "Payouts to Live: 5", activation FREE ([evidence/2026-11-05](evidence/2026-11-05/README.md))] | [12945796-lucidflex-payouts](https://support.lucidtrading.com/en/articles/12945796-lucidflex-payouts); [16558826](https://support.lucidtrading.com/en/articles/16558826-new-live-structure) | 2026-10-30 | rules-verifier agent (D-30) | verified |
| `payout_split` | profit split | `0.90` ["All LucidFlex funded account payouts are split 90% to the trader and 10% to Lucid Trading."; re-verified, unchanged] | [12945796-lucidflex-payouts](https://support.lucidtrading.com/en/articles/12945796-lucidflex-payouts) | 2026-10-30 | rules-verifier agent (D-30) | verified |
| `payout_processing_days` | processing time in days | `2` [upper bound: "Payouts will be disbursed to your payment method within 2 business days."; "Funds will be deducted from your account within a few minutes."; payouts "averaging about 15 minutes once approved" (12890325 description); Plaid instant for US, WorkMarket as early as next business day; re-verified, unchanged] | [12945796-lucidflex-payouts](https://support.lucidtrading.com/en/articles/12945796-lucidflex-payouts); [12890325-payout-methods](https://support.lucidtrading.com/en/articles/12890325-payout-methods) | 2026-10-30 | rules-verifier agent (D-30) | verified |
| `payout_fee` | per-payout fee by method | — [still unstated 2026-10-30; no payout fee on the 2026-11-05 cards (D-31), row stays open: methods listed (Plaid, WorkMarket by ADP bank/PayPal, crypto BTC/ETH/LTC/USDT/USDC international-only) but no fee figures stated anywhere read] | [12890325-payout-methods](https://support.lucidtrading.com/en/articles/12890325-payout-methods) | 2026-10-30 | — | unverified_human_input_required |
| `payout_balance_consequence` | what a payout does to the drawdown floor / balance | `MLL locks at start + $100 ($50,100 on $50K) upon payout request` [no buffer: "There is no buffer balance that must be maintained in LucidFlex funded accounts."; re-verified, unchanged] | [12945815-lucidflex-drawdown](https://support.lucidtrading.com/en/articles/12945815-lucidflex-drawdown) | 2026-10-30 | rules-verifier agent (D-30) | verified |

## D. Accounts, conduct, and terms

| key | rule | value | official page id and URL | date read | verified by | status |
|---|---|---|---|---|---|---|
| `max_accounts` | account cap | `5` [funded: "Up to 5 active funded accounts per household or family."; 10 active evaluations; 10 total across eval + funded; 5 live; cap is per HOUSEHOLD/family, not per person; value unchanged. NEW (16558826): "All simulated prop accounts are closed when a trader is moved live, or opts out of trading live via cash-out."; "If one household member is trading live, others may not trade simulated accounts." (§E 12)] | [11404617-maximum-number-of-accounts](https://support.lucidtrading.com/en/articles/11404617-maximum-number-of-accounts); [16558826](https://support.lucidtrading.com/en/articles/16558826-new-live-structure) | 2026-10-30 | rules-verifier agent (D-30) | verified |
| `copy_trading_terms` | copy-trading terms | `permitted` ["Automated trading systems and trade copiers are permitted"; trader responsible for software errors/malfunctions; live: hedging "includes any copytrader issues that may arise"; re-verified, unchanged] | [11404728-other-trading-activities](https://support.lucidtrading.com/en/articles/11404728-other-trading-activities) | 2026-10-30 | rules-verifier agent (D-30) | verified |
| `multi_account_same_strategy` | same strategy on several accounts | `permitted` [copiers expressly allowed → identical trades across accounts allowed; only OPPOSING positions across accounts (incl. mini vs micro of one contract, and correlated, e.g. ES vs NQ) are prohibited as hedging, article 11404734; re-verified, unchanged] | [11404728-other-trading-activities](https://support.lucidtrading.com/en/articles/11404728-other-trading-activities) | 2026-10-30 | rules-verifier agent (D-30) | verified |
| `news_trading_terms` | news-trading restrictions | `allowed` ["Allowed on Flex, Pro and Direct"; "Not allowed on Daily"; re-verified, unchanged] | [11404728-other-trading-activities](https://support.lucidtrading.com/en/articles/11404728-other-trading-activities) | 2026-10-30 | rules-verifier agent (D-30) | verified |
| `prohibited_conduct` | prohibited conduct and stated consequences | `microscalping; hedging (same-account, cross-account, cross-user, cross-firm, correlated opposing); HFT; exploiting platform/sim mechanics` [consequences graded per rule: warning → profit forfeiture / account reset to prior day's balance (NEW: "this does not reset the total remaining drawdown") → breach/permanent restriction; NEW: "Accounts with a Hedging Violation are not eligible for intraday payouts."; appeals allowed; value unchanged; full quotes in rules.yaml and §E] | [11404732-trade-with-integrity](https://support.lucidtrading.com/en/articles/11404732-trade-with-integrity); [11404742](https://support.lucidtrading.com/en/articles/11404742-prohibited-microscalping); [11404734](https://support.lucidtrading.com/en/articles/11404734-prohibited-hedging); [11404736](https://support.lucidtrading.com/en/articles/11404736-prohibited-high-frequency-trading) | 2026-10-30 | rules-verifier agent (D-30) | verified |
| `permitted_products` | permitted instruments | `CME Group futures (CME, CBOT, NYMEX, COMEX): equity index, currency, energy, metals, agricultural; minis and micros` [ES $1.75 / MES $0.50 per side; NQ $1.75 / MNQ $0.50; seven FX pairs $2.40 (the 2026-10-04 note said six); full schedule in rules.yaml; re-verified, unchanged] | [11508978-approved-products-and-commissions](https://support.lucidtrading.com/en/articles/11508978-approved-products-and-commissions) | 2026-10-30 | rules-verifier agent (D-30) | verified |

## E. Behavioural rules with no single parameter

Quote and cite the terms that shape the model but carry no number (how breaches are
reviewed, discretion clauses, sim-fill language). Each entry: the quote, page id, URL,
date read. Items 1–9 were read 2026-10-04 on `intercom.help/lucid-trading`; items 2–9 were
re-read 2026-10-30 on `support.lucidtrading.com` (D-30) and say what changed; items 10–14
are new on 2026-10-30. Nothing in §E is modelled unless a row above carries it.

1. **Plan types at the $50K tier (tier scope, D-06).** The help centre lists seven
   programs: LucidFlex (captured), LucidDaily, LucidPro, LucidDirect ("the LucidDirect
   (S2F) plan" — straight to sim-funded, no evaluation), LucidBlack ("(Legacy)"),
   LucidMaxx ("our exclusive straight to live program") and Live Trading ("our standard
   live program"). All three evaluation plans share the $50K geometry $3,000 target /
   $2,000 max loss / 4 minis, and differ in: **LucidPro** — daily loss limit $1,200 on
   $50K ("$50K | $3,000 | $2,000 | $1,200 | 4 mini/40 micros", article 12890029), no
   consistency column, "Pass the evaluation in one trading day"; **LucidDaily** — daily
   payouts, checkout choice of "intraday or end-of-day drawdown types" (intraday =
   "lower evaluation price", article 15996664), news trading not allowed. Help-centre
   index, collections 16914631, 19692910, 16780433, 16780869, 17988163, 16780995,
   19224353. *2026-10-30:* the index (support.lucidtrading.com/en/) still lists the same
   plan collections plus General Info (12931163), Fees, Payments and Payouts (16781120) and
   Rules and Guidelines (12931279); the other plans' own articles were not re-read (not
   modelled).
2. **Finite sim-funded life → the live review pool (CHANGED 2026-10-30).** 2026-10-04:
   "Traders may take up to 5 payouts from each LucidFlex account after which they will be
   moved live." (12945796 — the sentence still stands there, page updated 2026-07-28.)
   2026-10-30, New Live Structure (16558826, page updated 2026-10-14): "Traders enter the
   live review pool when one or more of the following conditions are met: After receiving
   the final payout (Payout 5) on their Flex, Pro, or Direct plan" — also "After being paid
   out a significant amount of capital lifetime", "If they have exceptional performance in
   sim funded", "If they have previously been moved live"; "Payout 5 represents the maximum
   payout level, not a guaranteed minimum for live eligibility."; "All live transitions
   occur at the discretion of the Lucid risk team." With the per-request cap "50% of Profit
   up to $2,000" ($50K), one sim-funded account still pays out at most $10,000. LucidLive
   accounts: "Up to 5 active LucidLive accounts per household or family" (11404617); swing
   trading is not allowed on them (11404729).
3. **Integrity catch-all (the discretion clause here; re-verified 2026-10-30).** "Taking
   advantage of system errors or update delays", "Exploiting discrepancies in simulated
   prices", "Using tactics that do not reflect real-world trading conditions" — these
   "violate the spirit of the program and undermine the integrity of the trading ecosystem
   we are building"; "We're here to fund real traders not opportunists."
   (11404732-trade-with-integrity.) Still no sole-discretion payout-denial language for the
   sim-funded payouts; the new discretion is over the live move (item 2) and live-side
   reviews (item 12).
4. **Graded, published enforcement (tier-2-like, stage-two D-145 framing; re-verified
   2026-10-30).** Microscalping: flagged when "More than 50% of your profits are generated
   from trades held for 5 seconds or less" — manual review, warning, then forfeiture of
   those profits and possible permanent restriction; appeal available (11404742). Hedging:
   first offense "You will receive an email notice & the associated accounts will be reset
   to prior days balance. Despite the balance reset, this does not reset the total
   remaining drawdown on these accounts." (the second sentence is new on record);
   "After repeated offenses all involved accounts will be breached and you may be
   permanently restricted from using Lucid Trading services." (11404734); and "Accounts
   with a Hedging Violation are not eligible for intraday payouts." (16226050). HFT:
   written warning, then profit removal, account closure, permanent restriction; appeal
   available (11404736).
5. **Cross-account hedging includes correlated instruments (re-verified 2026-10-30).**
   Opposing positions in related assets across separate accounts are prohibited ("Example:
   You cannot go long ES in one account and short NQ in a separate account."; "Correlated
   assets go for groupings in equities, metals, energies, etc."), as is opposing a mini
   with a micro of the same contract in separate accounts, and "Hedging between different
   firms or funded platforms" (11404734, page updated 2026-10-06). Same-direction
   coordination across accounts is not restricted anywhere read; copiers are "permitted"
   (11404728). Live: "Hedging live accounts is strictly prohibited by both Lucid and the
   CME. This includes any copytrader issues that may arise. Violations will result in a
   permanent ban." (16558826).
6. **Session mechanics (re-verified 2026-10-30).** "All positions must be closed by 4:45 PM
   EST, Monday through Friday" — remaining positions are auto-closed and "Holding a
   position past this time does not result in a failed account"; "Trading resumes at 6:00
   PM EST, Sunday through Thursday"; on holidays the earlier market close overrides
   (11404729-allowed-trading-times).
7. **Inactivity deletion (re-verified 2026-10-30).** "Accounts that have not been traded
   resulting in at least a net profit or loss of 1$ within 30 calendar days will be deemed
   abandoned and will be permanently deleted from our systems."; breached evaluations:
   "All breached accounts will be automatically deleted after 30 days if not reset." — and
   now on record: "If an evaluation is breached (has hit Max Loss Limit), it is still
   eligible for a reset." / "Traders can manually purchase a reset at any time before that
   30-day period expires." (11404632-inactivity-policy; see `eval_reset_fee`).
8. **Payout latency in practice (re-verified 2026-10-30).** The Payout Methods article is
   described as "payouts averaging about 15 minutes once approved"; Plaid = "Instant bank
   transfers for U.S.-based traders"; WorkMarket by ADP: "Funds can typically be received
   as early as the next business day"; crypto (BTC/ETH/LTC/USDT/USDC) "Available for
   International Traders" (12890325-payout-methods). The payouts page bound is "within 2
   business days" (12945796).
9. **Main-site access.** `lucidtrading.com` returned HTTP 403 to non-browser clients on
   2026-10-04 and was not readable by an agent on 2026-10-30 (bot protection, not worked
   around), so prices (the four checkout configurations, the reset price) and the
   published Terms of Use remain unread; they are the open `unverified_human_input_required`
   rows above, to be read by a human in a browser (H-6).
10. **Checkout customization — four configurations (NEW 2026-10-30).** "LucidFlex gives
    traders the ability to customize their account at the time of purchase. Two settings
    can be adjusted" — "Daily Loss Limit: On or Off" / "Consistency: 40% or 50%" — "These
    settings create four unique LucidFlex account configurations." Option 1 DLL ON + 40 %
    ("Cheapest version of LucidFlex"); Option 2 DLL ON + 50 % ("Pass in as few as 2 days");
    Option 3 DLL OFF + 40 % ("Regular end-of-day payouts"); Option 4 DLL OFF + 50 %
    ("Highest pricing version of LucidFlex"). "Once selected, these settings cannot be
    changed for an active account." (16226050-lucidflex-customization, page updated
    2026-10-20.) The rows carry Option 3 (DLL OFF, standard 40 %); Option 4 is the
    configuration the 2026-10-04 rows described.
    **Prices, 2026-11-05 (D-31; official pricing cards, operator screenshots,
    [evidence/2026-11-05](evidence/2026-11-05/README.md)), $50K with the checkout coupon
    (list):** Option 1 DLL ON + 40 % $80.50 ($115), reset $80; Option 2 not captured;
    Option 3 DLL OFF + 40 % **$115.50** ($165), reset **$115** — the rows' values;
    Option 4 DLL OFF + 50 % $130.20 ($185), reset $130. The cards also carry an "On
    Demand Payouts" switch, ON with the DLL ON and OFF with it OFF, at no price difference.
11. **The DLL as a soft breach and On Demand Payouts (NEW 2026-10-30).** "The DLL is a soft
    breach, so if you hit it you will simply be locked out until the next trading
    session." With the DLL on, the funded account "can request payouts during the trading
    session, from profit made that session (6:00 PM to 3:45 PM ET)", and "After requesting
    an intraday payout, trading on your funded LucidFlex account is paused until the end of
    the trading day."; "With the Daily Loss Limit Off, payouts follow the regular
    end-of-day schedule." (16226050.) The DLL amount is not stated in any LucidFlex article.
    The pricing cards (2026-11-05, D-31) state it: **$1,200** on $50K, on the funded card
    "DLL (Below Initial Trail) $1,200".
12. **What the live move does (NEW 2026-10-30; New Live Structure, 16558826, page updated
    2026-10-14).** "Traders receive one live account per eligible funded account"; "Each
    funded account must have received at least one payout to qualify"; live accounts begin
    with "$0 starting balance", "Daily payouts", "End of Day (EOD) drawdown", "No daily
    loss limit" ($50K: starting live drawdown $2,000, max "4 minis or 40 micros"); "Once a
    trader generates live profits equal to their starting live drawdown, the Max Loss Limit
    locks at $100 and no longer moves." Cash-out instead of live: "This cashout option is
    equal to 50% of a traders live starting balance and is subject to a 90/10 profit
    split. If no choice to cashout is made within 24 hours of receiving the move to live
    email, your accounts will automatically move to Live." **The whole household's sim book
    ends:** "All simulated prop accounts are closed when a trader is moved live, or opts out
    of trading live via cash-out."; "If a funded account is not moved live due to being
    ineligible, the evaluation cost of that account will be refunded, as long as the
    account has equal to or greater than 50% of the total drawdown remaining."; "If you are
    not comfortable with evaluations being closed, do not keep evaluations in reserve.";
    "If one household member is trading live, others may not trade simulated accounts."
    Also: a repeatable Live Bonus ($50K: "$4,000 | 20 | $2,000" — live profit target,
    trading days, bonus; 90/10 split); "Standard cooldown period: 2 weeks" before a new
    evaluation after blowing a live account. Legacy structures (13425130 "Legacy Live
    Structure"; 13424914 "LucidFlex Live (Legacy)" — "This is for accounts purchased/reset
    on 2/27/26 and prior.", six payouts, move-to-live caps and escrow) do not apply to new
    accounts.
13. **Scaling plan and payouts (re-verified 2026-10-30).** "Since payouts reduce your
    simulated balance, your scaling tier may adjust downward to reflect the updated profit
    level."; exceeding the limit by circumvention "may result in having profit wiped for
    the day" (12945808).
14. **Help-centre host (NEW 2026-10-30).** The help centre's canonical URLs are now
    `https://support.lucidtrading.com/en/articles/<id>-<slug>`, with the same article ids
    read on intercom.help/lucid-trading on 2026-10-04 (`intercom.help` did not resolve from
    this machine on 2026-10-30). Every row's URL above points at the new host.
