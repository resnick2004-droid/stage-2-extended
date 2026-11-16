# Other firms' futures contracts, read on their own pages (Q-12, 2026-11-15)

Scout note for TASK_QUEUE Q-12, the groundwork for family C (bootstrap 6.3 C; Stage 2's handoff 3.3). Brief:
`docs/briefs/Q-12_2026-11-15.md`. Light work only: web pages read, nothing run, no data read, no outcome computed.
**Nothing here can be used by code yet.** A firm rule becomes usable only when the rules-verifier records it in
`config/rules_extended.yaml` / `docs/RULES_CURRENCY.md` under a decision row (CLAUDE.md, "Firm rules"). This note is
the source list for that work.

> **Struck under E-020 (Q-34, 2026-11-16).** Eight firms' own terms forbid automated retrieval: Tradeify, The Trading
> Pit, Goat, Alpha, The Futures Desk, FunderPro, Aqua and FundedNext. What the readers collected from them is struck:
> their saved pages are deleted, their files in `firms_2026-11-15/firms/` and their Appendix A sections are stubs
> naming the clause (each clause is listed under "How the pages were read"), and their quotes are gone from this
> body. Their screen verdicts and this body's unquoted readings of their terms stay, as a scout's reading only. The
> machine-check counts below are those of 2026-11-15, before the strike.

## The question

Which prop firms sell a futures evaluation comparable to Topstep's $50K (CME index micros and minis, an evaluation
and then a funded account that pays out) with an **end-of-day drawdown or no consistency rule**, several funded
accounts at once, and no rule against hand-entered one-position bracket trading? What are their contract terms,
quoted from each firm's own pages? And on contract arithmetic alone, which look best for the solver-only
contract-fit read that comes next?

## The answer

- **26 firms looked at; 22 could be read.** Four firms block automated readers outright on every host: Apex Trader
  Funding, Elite Trader Funding, TickTickTrader and E8 Futures (curl and WebFetch both got HTTP 403). They are
  UNDETERMINED; the block was not worked around. Of the 22 read, **19 pass the screen**: Lucid, FunderPro Futures,
  DayTraders.com, The Trading Pit, Aqua Futures, Alpha Futures, Tradeify, BluSky, Earn2Trade, FundedNext Futures,
  TradeDay, Top One Futures, FXIFY Futures (now Futureify), Funded Futures Network, My Funded Futures, Phidias,
  Goat Funded Futures, Bulenox and Take Profit Trader. **One fails:** The Futures Desk allows 2 accounts per trader.
  **Two are UNDETERMINED:** Legends' rules knowledge base is blocked, and Purdia's site is a JavaScript app with no
  readable rule page.
- **Most firms sell the same 50K shape as Topstep:** a $3,000 target and a $2,000 end-of-day trailing drawdown that
  locks at or near the starting balance. The exceptions are FundedNext ($2,500 / $1,500), Alpha Advanced
  ($4,000 / $1,750), FXIFY ($3,000 / $1,750), Phidias ($4,000 / $2,500) and BluSky (two $3,000 phases before any
  payout). So the zero-edge ceilings mostly match Topstep's. **What differs is the price, the split, the payout
  gates and caps, how long the account lives, the number of seats, and the conduct rules.**
- **On contract arithmetic alone, no firm clearly beats Topstep's own $50K.** The ceiling on payouts per fee dollar
  is driven by the fee. FunderPro Beginner, DayTraders EOD, The Trading Pit Prime and Aqua Daily sit in Topstep's
  band, and each carries a caveat that the arithmetic cannot see:
  - FunderPro: a 50 % funded consistency rule and a clause against linked accounts.
  - DayTraders: a 30 % funded consistency rule, and the fee's billing basis is not stated.
  - The Trading Pit: a clause against using several accounts from one IP address or network.
  - Aqua: a rule against account rolling.

  Lucid, Stage 2's verified second firm, is mid-table at list price and in that band at its coupon price.
- **What would separate these firms is what the ceiling ignores**, which is the solver-only read's job:
  consistency rules, payout gates and caps, finite sim lives, live moves that close every account in the household,
  news windows that catch a resting bracket, minimum-hold rules, and rules against account rolling.

## How the pages were read (the evidence standard)

- **Official pages only.** Each firm's own domains are listed in Appendix A: its site, the help centre it links to,
  its terms. Two web searches were used only to find candidate names and URLs; nothing in their text is used.
- **An honest reader.** Pages were fetched with curl under its own user agent: GET only, one request a second, no
  cookies, logins, forms, chats or checkouts, and no personal data sent. That came to 596 requests on 2026-11-15,
  between 21:14 and 21:50 HST (the fetch log is in UTC: 07:14Z to 07:50Z on 11-16).
- **Blocks were not worked around.** Where a host served a Cloudflare challenge or block, it is recorded. The user
  agent was not changed, and no browser or mirror was used. WebFetch was tried once per blocked host and was refused
  every time. This follows Stage 2 D-561 for lucidtrading.com.
- **Five readers worked in parallel** under one written brief, a few firms each. This scout re-read Lucid. Every
  quote is saved with the page it came from (in the scout's scratch folder, outside the repository).
- **Two machine checks**, run by this scout over every firm's file:
  - **Verbatim.** Every quote must appear in the saved page text. Whitespace and typographic quotes and dashes are
    folded; nothing else is forgiven. Result: 1,628 quotes, 0 misses.
  - **Provenance.** Every quoted page must have been fetched from that firm's declared official host. Result: no
    problems, with one exception. A Legends quote from legendstrading.com is there only to show that the domain is
    an unrelated options-signals business, not the prop firm (thelegendstrading.com); it is not a rule.
- **Values spot-checked.** A value is the reader's reading of a quote. Against their quotes, these all held:
  - FunderPro Beginner: fee, split, drawdown, cap.
  - DayTraders: split, drawdown, cap.
  - The Trading Pit: split, drawdown.
  - Aqua Daily: cap, drawdown, target.
- **Eight firms' own terms forbid automated retrieval, and what the readers collected from them is struck (E-020).**
  Their saved pages are deleted, their files in `firms_2026-11-15/firms/` and their Appendix A sections are stubs,
  and their quotes are gone from this body (Q-34, 2026-11-16). Each firm's clause, as recorded:
  - Tradeify, Terms of Use: "use any robot, spider, scraper or other automatic device ... to access, harvest,
    monitor, copy or use the Site" without permission (E-009; struck, E-020).
  - The Trading Pit, GTC 4.5.2: "automated retrieval or extraction of data (scraping, crawling, or similar methods)
    without our express written permission" (E-009; struck, E-020).
  - Goat: "Harvesting, scraping, or otherwise collecting any information from the Sites ... without our prior
    written consent" (E-009; struck, E-020).
  - Alpha Futures: "any automated use of the system, such as ... web scraping robots" (E-009; struck, E-020).
  - The Futures Desk, Terms & Conditions: "Using manual or automated software, devices, or processes to "crawl" or
    "spider" any web pages within the Sites or Services." (E-009; struck, E-020).
  - FunderPro Futures, Terms & Conditions 12.5.6: "to use automated means to view, display or collect information
    available through the Website or Services" (Q-26, `config/rules_extended.yaml`; struck, E-020).
  - Aqua Futures, Terms of Service: "You are expressly prohibited from scraping, crawling, framing, posting
    unauthorized links to, aggregating, hacking, performing denial of service (DOS) attacks on, reverse engineering,
    or circumventing technological protection measures of the Services or the Company website." (Q-26; struck,
    E-020).
  - FundedNext Futures, Terms of Service 13.3(c): "The User is expressly prohibited, directly or indirectly, in
    whole or in part, without the Provider's prior written authorisation, from: ... (c) engaging in scraping,
    crawling, harvesting, data mining or using robots, scripts or automated systems to access the Website/Services,
    extract data" (Q-26; struck, E-020).

  The readers saw the first five clauses on 2026-11-15 and stopped fetching from a site once they saw its clause;
  the last three were found in Q-26, after the readers had fetched those sites' pages. **These firms' plans are read,
  if ever, only through the operator's browser** (as Stage 2 D-574/D-575 did for Lucid's prices) **or with the
  firm's written permission** (E-020 (2)).

## 1. The candidates and the screen

The screen (brief, goal 1) asks four things:

- an end-of-day drawdown on the funded account, **or** no funded consistency rule (interpretation: the funded
  account is where the contract pays; a firm that passes only on the second leg is marked);
- several funded accounts at once (read as three or more; P-14 uses five Topstep seats);
- no rule forbidding hand-entered, one-position bracket trading on NQ/MNQ;
- the conduct rules that bear on our designs.

**Hand entry throughout.** Our designs never copy one trade across accounts (Stage 2 D-157) and never automate entry
(CHARTER section 4). So a ban on copiers or bots does not bind them, and a firm's permission for copiers or bots is
irrelevant to them.

| firm (plan read) | funded drawdown | consistency: evaluation / funded | funded seats | conduct that bears on our designs | verdict |
|---|---|---|---|---|---|
| Lucid (LucidFlex 50K) | EOD trailing, locks start + $100; a payout request forces the lock | 40 % (50 % add-on) / none | 5 per household | hedging banned across firms and correlated assets (ES against NQ); news allowed on Flex; the live move closes every sim account | **PASS** (Stage 2's verified second firm, D-561/D-575; re-read today, unchanged) |
| FunderPro Futures (Beginner, Mid-Level 50K) | EOD trailing, locks at start after the first reward | 40 % / **50 %** | 5 | GTC 13.4 bars shared devices or IP addresses and any setup enabling linked or non-independent trading, including between one client's own accounts; >30 % of margin on one idea deemed excessive; Beginner funded ±2 min news (GTC: all plans) | **PASS** (material struck, E-020) |
| DayTraders.com (EOD 50K) | EOD trailing, stops at start | 50 % / **30 % per cycle** | 5 EOD Pro (15 sim in all; one login per household) | hedging banned incl. correlated; news allowed; Martingale banned; on a live call the sim accounts close and excess sim balance is generally forfeited | **PASS** |
| The Trading Pit (Futures Prime 50K) | EOD trailing $2,000 | 40 % / none | 5 | **a clause bars using several accounts from one IP address or network**; news: allowed by the help centre vs GTC ±2 min; gambling policy; > 50 % of profit from trades ≤ 15 s flagged | **PASS** (the IP clause needs a written answer before any multi-seat use; material struck, E-020) |
| Aqua Futures (Daily 50K; Flex Daily Loss 50K) | EOD trailing | 40 % (Daily), 50 % (Flex) / none | 5 | bots banned (hand entry fine); ≥ 50 % of trades and profit held > 10 s; average reward-to-risk ≥ 0.3; < 100 trades a day; account rolling and stacking banned; 7 days without a trade closes the account | **PASS** (material struck, E-020) |
| Alpha Futures (Standard 50K; Advanced 50K) | EOD trailing, stops at start | Std 50 % / **40 %**; Adv 40 % / none | Std 5, Adv **3** per household (pages conflict) | bots banned (hand entry fine); Standard funded ±2 min red-folder news; an all-or-nothing rule; rolling/stacking banned; tight-bracket fill exploitation and < 10-tick/< 2-min scalping banned; T&C 1.3.2: risk kept at the evaluation level | **PASS** (material struck, E-020) |
| Tradeify (Select 50K) | EOD trailing $2,000 | 40 % / none | 5 per individual and household | Funded Trader Agreement: opposite positions banned whatever the intent, incl. the Equity Index group and other firms; very large sizes discouraged, and consistent sizes, stops and targets expected; help centre (which governs) unreadable | **PASS** (11 terms UNVERIFIED; material struck, E-020) |
| BluSky (Launch 50K; Orbit 50K) | Launch: **static** ($3,000 start, $100 floor); Orbit: EOD trailing, locks at start | Launch 50 % (55 % on the homepage), then a 34 % Buffer / none; Orbit none / 40 % | **3** | hedging banned incl. correlated and across firms; a 3-breach clause can cut the trader to 1 account; $10,000 total profit forces a Brokerage Review | **PASS** |
| Earn2Trade (Gauntlet Mini 50K -> LiveSim) | EOD trailing (Live is intraday) | 30 % / none | **3** (at most 1 Live) | "copy-trading and batch execution across multiple accounts is not permitted" (enter each account separately); news allowed | **PASS** |
| FundedNext Futures (Flex 50K) | EOD trailing $1,500, locks $50,100; the first payout resets it there | 40 % / none | 5 per user and household; 10 issued a month | account rolling banned; tight-bracket fill exploitation banned; trades < 10 s making ≥ 40 % of cycle profit deducted; the Disciplined Trader Program bans news | **PASS** (material struck, E-020) |
| TradeDay (Fast Pass EOD 50K; Quick Pay EOD 50K) | Fast Pass: EOD trailing; Quick Pay: **intraday** | FP 45 % / **45 %** (accounts from 2026-07-26); QP 30 % / none | 5 Funded Sim | "auto-liquidate all open positions 2 minutes before TradeDay's tier 1 economic data releases"; no third-party bots or API; > 200 trades a day banned | **PASS** (QP on the no-consistency leg) |
| Top One Futures (Elite Daily V2 50K) | EOD trailing, locks start + $100 | 40 % / none | 5 per household, **evaluations included** | funded ±2 min: "Your trade must not be closed by any means during the restricted news window"; 10-second minimum hold; batch-buying evaluations and letting most fail banned; automation banned (hand entry required); live move disables the other accounts | **PASS** |
| FXIFY Futures / Futureify (Flex 50K) | EOD trailing, locks at start after the first payout | 50 % / **40 %** | 5 **in total, evaluations included** | tight-bracket exploitation and < 10-tick micro-scalping banned; rolling banned; homepage says "Live account credentials", FAQ says simulated | **PASS** |
| Funded Futures Network (STEADY 50K) | EOD trailing, locks start + $100 | 52 % / none | 5 | funded: "no positions or orders (including limit orders) ... 1 minute before and 1 minute after the release"; flat by 4:50 PM ET; Live Review after 4 payouts closes every sim account | **PASS** (rules page and help centre unreadable) |
| My Funded Futures (Rapid EOD 50K; Pro 50K) | EOD trailing, locks + $100 (Pro: static at $50,100 after the first payout) | Rapid EOD 30 % / none; Pro 50 % / no numeric rule | Rapid EOD **3**; 5 across 25K/50K | Rapid EOD funded: no positions or orders ±2 min of Tier 1 releases; "tight brackets to gain from favorable fills" banned; help allows copying, Terms 23.1.3.3 bar it "in a manner that provides an unfair advantage"; a $10,000 day moves you Live and suspends every sim account | **PASS** |
| Phidias (Premium 50K; Express to Live 50K) | EOD trailing, stops at $50,100 (E2L static $650) | none / **30 %** (E2L none) | 5 per plan type, 15 per household/company/IP | robots banned (hand entry fine); consistent position sizes required; a discretionary live move that cannot be refused | **PASS** |
| Goat Funded Futures (Flex 50K) | EOD trailing, locks at start | 50 % / none | 5 Flex | **1-minute rule**: ≥ 70 % of closed trades and ≥ 70 % of net profit from trades held > 1 minute, else the cycle's sub-minute profit is deducted (rule from 9-10 Nov 2026); funded ±2 min news; VPS banned (the trader must place and manage each trade in person); payouts only on the 5th-8th and 20th-23rd, 3 % fee | **PASS** (material struck, E-020) |
| Bulenox (Qualification 50K Option 2 -> Master) | EOD (the option carries to Master) | not stated / a Master consistency rule, % UNVERIFIED | 5 Master-level | copiers and news allowed; Terms (Oct 2026): third-party trading technology needs approval | **PASS** (16 terms UNVERIFIED; help centre unreadable) |
| Take Profit Trader (50K Test -> PRO) | **intraday** trailing (PRO+, live, is EOD) | 50 % / none | 5; 10 activations per 30 days | "No trading bots" (hand entry is what they want); PRO flat with no open orders 1 min around major news; max 50 executions a day; no counter positions | **PASS on the no-consistency leg only** (13 terms UNVERIFIED; terms and help centre blocked) |
| Legends Trading (Elite 50K) | EOD (Master stage) | 40 % / 30 % gates payouts | "multiple", up to $1.5M | conduct rules all on a blocked knowledge base | **UNDETERMINED** |
| Purdia Capital ("Freedom" 50K EOD) | not stated | none (Freedom) | 3 | own-account copying; hedging banned incl. correlated; fully automated trading banned; its two embedded catalogs conflict | **UNDETERMINED** (no readable rule page) |
| The Futures Desk | static or EOD (homepage) | -- / none | **2 per trader** | Topstep affiliate (TS TFD Buyer, LLC); funded accounts are live brokerage accounts | **FAIL** (2 seats; material struck, E-020) |
| Apex Trader Funding; Elite Trader Funding; TickTickTrader; E8 Futures | -- | -- | -- | every host returned 403 to curl and to WebFetch | **UNDETERMINED** (unreadable; an operator browser read could settle them) |

## 2. The firms that pass: their terms

Every term the contract-fit read needs is in **Appendix A**. Firms are in the order of section 3's ranking, then the
others. Each term follows the multi-firm ledger's keys (`vendor/stage2/vendor/propfirms/firms/lucid-trading/rules.yaml`),
which are this repository's form for a non-Topstep firm. Each term carries its value, its status, its verbatim quotes
keyed to the firm's page list (URL, article id, the page's own date; all read 2026-11-15), what was looked at when it
is UNVERIFIED, and the reader's note. Where a firm sells two 50K plans that pass and differ materially, both are
given (`terms_<plan>`).

### UNVERIFIED terms, by firm (generated from the firm files)

- **FunderPro Futures (FunderPro Ltd., Malta)** (6): `terms_beginner.payout_processing_days`, `terms_beginner.payout_fee`, `terms_beginner.payout_count_limit`, `terms_midlevel.payout_processing_days`, `terms_midlevel.payout_fee`, `terms_midlevel.payout_count_limit`
- **DayTraders.com (Day Traders)** (3): `payout_processing_days`, `payout_fee`, `payout_count_limit`
- **The Trading Pit** (2): `payout_min`, `payout_count_limit`
- **Aqua Futures (AquaFutures / AquaFunded Futures)** (3): `terms_flex_daily_loss_50k.eval_reset_fee`, `terms_daily_50k.eval_reset_fee`, `terms_daily_50k.payout_count_limit`
- **Alpha Futures** (1): `payout_fee`
- **Lucid Trading** (3): `funded_monthly_fee`, `payout_fee`, `inactivity_rule`
- **Tradeify** (11): `eval_drawdown_lock`, `eval_count_limit`, `eval_time_limit`, `funded_drawdown_lock`, `payout_balance_consequence`, `funded_position_limit`, `payout_min`, `payout_fee`, `payout_count_limit`, `news_trading_terms`, screen `news`
- **BluSky Trading Company** (4): `eval_drawdown_lock`, `funded_daily_loss_limit`, `payout_fee`, `payout_count_limit`
- **Earn2Trade** (1): `payout_balance_consequence`
- **FundedNext Futures** (2): `eval_min_days`, `payout_fee`
- **TradeDay** (1): `terms_quick_pay_eod_50k.payout_cap`
- **Top One Futures** (2): `payout_processing_days`, `payout_fee`
- **FXIFY Futures (trading as Futureify; FXIFY Futures Limited, Dublin)** (3): `payout_fee`, `payout_count_limit`, `permitted_products`
- **Funded Futures Network** (6): `eval_drawdown_lock`, `eval_time_limit`, `payout_fee`, `inactivity_rule`, `sizing_or_gambling_terms`, screen `sizing_gambling`
- **My Funded Futures (MyFundedFutures, MFFU)** (10): `eval_drawdown_lock`, `eval_reset_fee`, `eval_time_limit`, `payout_balance_consequence`, `payout_fee`, `payout_count_limit`, `terms_pro50k.eval_drawdown_lock`, `terms_pro50k.eval_reset_fee`, `terms_pro50k.eval_time_limit`, `terms_pro50k.payout_fee`
- **Phidias Propfirm** (2): `payout_fee`, `inactivity_rule`
- **Goat Funded Futures (GFF)** (3): `eval_fee`, `eval_reset_fee`, `payout_count_limit`
- **Bulenox** (19): `eval_drawdown_lock`, `eval_consistency_rule`, `activation_fee`, `funded_type`, `funded_drawdown_amount`, `funded_drawdown_lock`, `payout_balance_consequence`, `funded_daily_loss_limit`, `funded_consistency_rule`, `funded_position_limit`, `payout_min`, `payout_cap`, `payout_frequency_gate`, `payout_count_limit`, `inactivity_rule`, `cross_account_hedging`, screen `consistency_eval`, screen `consistency_funded`, screen `opposite_positions`
- **Take Profit Trader (TakeProfitTrader LLC)** (13): `eval_profit_target`, `eval_drawdown_amount`, `eval_position_limit`, `eval_fee`, `eval_reset_fee`, `eval_time_limit`, `funded_drawdown_amount`, `payout_min`, `payout_fee`, `payout_count_limit`, `inactivity_rule`, `copy_trading_terms`, screen `copy_trading`
- **Legends Trading (The Legends Trading Group, Inc.)** (5): screen `copy_trading`, screen `opposite_positions`, screen `news`, screen `automation`, screen `sizing_gambling`
- **Purdia Capital (Purdia Capital LLC)** (2): screen `drawdown_funded`, screen `sizing_gambling`
- **The Futures Desk (TS TFD Buyer, LLC; Topstep affiliate)** (4): screen `drawdown_funded`, screen `consistency_eval`, screen `copy_trading`, screen `news`

What was looked at for each is in Appendix A (`looked at:`). Most gaps are payout fees and payout-count limits that
no page states either way. Three firms are a different case: their **help centres are unreadable** to an honest
reader (Tradeify, Bulenox, Take Profit Trader) and their gaps are structural.

### Official pages that contradict each other (generated from the readers' notes)

- **FunderPro Futures (FunderPro Ltd., Malta)** `consistency_eval`: Conflict: the site's tooltip (funderprofutures.com and /how-it-works) still describes a 45% rule (excess daily profit is added to the target), and the at-a-glance article lists a consistency violation at the time of passing among breach causes (quotes struck, E-020).
- **FunderPro Futures (FunderPro Ltd., Malta)** `consistency_funded`: Conflict: help-centre articles (July 2026) say 50%; the homepage tooltip says 45% (the legacy value).
- **FunderPro Futures (FunderPro Ltd., Malta)** `copy_trading`: Conflict: GTC clause 13.4 prohibits shared devices, shared IP addresses and any setup enabling linked or non-independent trading, whether between accounts of one client or of several (quote struck, E-020). Read literally it clashes with the advertised own-account copy trading.
- **FunderPro Futures (FunderPro Ltd., Malta)** `news`: Conflict: GTC 10.1 and 13.9 restrict opening positions within 2 minutes of Economic Calendar releases without a plan distinction.
- **FunderPro Futures (FunderPro Ltd., Malta)** `sizing_gambling`: Conflict: article 378635 permits martingale strategies (quote struck, E-020).
- **FunderPro Futures (FunderPro Ltd., Malta)** `eval_consistency_rule`: See screen note: 45% tooltip conflict; at-a-glance lists violating it at the time of passing as a breach cause.
- **FunderPro Futures (FunderPro Ltd., Malta)** `funded_consistency_rule`: Homepage tooltip says 45% (conflict).
- **FunderPro Futures (FunderPro Ltd., Malta)** `payout_frequency_gate`: Not stated whether the 5 profitable days reset after each reward. The homepage still offers daily withdrawals after 3 rewards (legacy wording, conflict; quote struck, E-020).
- **FunderPro Futures (FunderPro Ltd., Malta)** `payout_split`: The /how-it-works page still shows the legacy 60/70/80% ladder (conflict).
- **FunderPro Futures (FunderPro Ltd., Malta)** `copy_trading_terms`: See screen copy_trading for the own-account permission and the 13.4 conflict.
- **FunderPro Futures (FunderPro Ltd., Malta)** `other_conduct_bearing`: Overnight conflict: the 2026 at-a-glance article allows overnight holds; the 2025 article and the homepage say positions are flattened daily (quote struck, E-020).
- **FunderPro Futures (FunderPro Ltd., Malta)** `news_trading_terms`: Conflicts with GTC 10.1/13.9 (2-minute news restriction with no plan distinction).
- **DayTraders.com (Day Traders)** `copy_trading`: The Terms of Use (Last Updated March 5, 2025) prohibit 'Sharing trades and strategies with other users or making trades that were not Customer's own creation' -- about other users, not own-account copying; no conflict for own accounts.
- **DayTraders.com (Day Traders)** `other_conduct_bearing`: The Terms are older (last updated March 5, 2025) and link rules articles on help.daytraders.com that were not read; the help-centre articles are newer (~3 weeks). Our design is intraday, so the overnight conflict does not bind it.
- **Aqua Futures (AquaFutures / AquaFunded Futures)** `payout_min`: Conflict: $500 minimum payout vs $100 via crypto.
- **Aqua Futures (AquaFutures / AquaFunded Futures)** `payout_count_limit`: Conflict: the futures page blurb says three rewards then the account closes - that matches the Flex No Daily Loss article, not Flex Daily Loss. Help article value taken for Flex Daily Loss.
- **Alpha Futures** `max_funded_accounts`: CONFLICT: the Advanced product-page FAQ says up to 5; the help centre (July 27, 2026) and T&C Schedule 2 say Advanced = 3. Taken as 3.
- **Alpha Futures** `copy_trading`: CONFLICT between help centre and T&C wording; the help article explicitly addresses copying across one's own Alpha accounts and permits it (quote struck, E-020).
- **Alpha Futures** `eval_min_days`: CONFLICT inside the T&C: clause 8.1.9 says 3, the Schedule 1 Advanced Evaluation row says 2. Homepage card and product page say 3. Taken as 3 (the 40% rule makes 3 the arithmetic minimum anyway).
- **Alpha Futures** `funded_drawdown_amount`: CONFLICT: product/home cards say $1,750 on the 50K Advanced Qualified; T&C Schedule 2 lists Advanced Qualified MLL as 4% (= $2,000). Taken as $1,750 (help centre/product pages, plan-specific).
- **Alpha Futures** `payout_split`: CONFLICT: the General Service Agreement (undated, older company number/address) still has a 70/80/90 tier; the help centre, product pages and T&C Schedule 2 say 90% from the start (quote struck, E-020). Taken as 90%.
- **Alpha Futures** `payout_processing_days`: CONFLICT T&C (3) vs operational update (<= 5). The update follows an unnamed major change (quote struck, E-020) around July 2026 that disrupted payouts; Premium accounts were refunded and Premium payouts are queued in batches.
- **Alpha Futures** `max_accounts`: CONFLICT: T&C Schedule 2 says an active Standard OR Advanced Qualified caps the user at 3; the help centre (same date, July 27, 2026) says only an active Advanced Qualified does (and Standard accounts bought before July 27, 2026 are capped at 3). Product page FAQ says 5 for Advanced. The month-old lead ('5 per household, 3 if an Advanced Qualified is active') matches the help centre.
- **Alpha Futures** `copy_trading_terms`: CONFLICT (see screen.copy_trading). Our design enters by hand on each account, so it does not depend on a copier.
- **Alpha Futures** `max_accounts`: CONFLICT with T&C Schedule 2 (see terms.max_accounts). Standard was relaunched July 27, 2026 (quote struck, E-020).
- **Tradeify** `consistency_eval`: CONFLICT in meaning: the Select landing page FAQ defines the 40% as a share of green days, unlike the usual best-day share of profit; the governing definition is on the unreadable Help Center. The percentage (40%) is verified, its mechanics are not.
- **Tradeify** `eval_fee`: CONFLICT: the /select-plan page's size picker shows 50K at $111 (that page carries an expired sale banner ending 13 November and lorem-ipsum template text; quote struck, E-020). Price before/after coupon not certain.
- **BluSky Trading Company** `consistency_eval`: CONFLICT: help centre (three articles) says 50% for the Launch evaluation; the homepage plan-picker data (page script) says 55% for 50K Launch. Measured as largest profitable day / sum of profitable days (losing days excluded).
- **BluSky Trading Company** `copy_trading`: CONFLICT in wording: table header is '| Account Size | Max Accounts | Trade Copier Allowed' and says Yes; the conduct policy's 'account' could be read to cover copying between one's own accounts. Our design enters by hand on each account.
- **BluSky Trading Company** `eval_consistency_rule`: CONFLICT eval 50% (help) vs 55% (homepage widget data), see screen. The Buffer row's header: '| Account size | Profit target | Drawdown | Consistency | Largest single day'.
- **BluSky Trading Company** `funded_drawdown_amount`: CONFLICT: help centre (Launch article, Sim Funded Processing article) says minimum balance $100; the homepage plan-picker data for 50K Launch says minBalance 1000 (i.e. $2,000 room). $2,900 = $3,000 - $100 is arithmetic on the help-centre figures. The older Sim Funded Payouts article frames the same as a $53,000 'minimum balance' on a $50,000 account (the $3,000 buffer is not withdrawable). If the Risk Team grants more contracts, 'we will also raise the static drawdown limit' (Buffer article).
- **BluSky Trading Company** `funded_position_limit`: CONFLICT: Buffer article's 'Max contracts in Sim Funded' says 5/50 for a 50K; Sim Funded rules and the contract-size article say limits scale with the (small) balance and are lower than in evaluation. Rithmic and Volumetrica do not scale; Tradovate scales by margin.
- **BluSky Trading Company** `copy_trading_terms`: See screen.copy_trading (conflict).
- **BluSky Trading Company** `eval_drawdown`: CONFLICT: the Evaluation Overview (July 31, 2026) lists an Orbit 'Phase 2 - Buffer 50% Consistency'; the Orbit article (Oct 15, 2026) says Orbit has only two phases. Taken as two phases (newer).
- **BluSky Trading Company** `payout_terms`: CONFLICT on frequency: Orbit plan article (Oct 15, 2026) 'payouts every three trading days'; Orbit V2 payouts article (Aug 12, 2026) 'daily withdrawals'. The ceiling row's header: '| Orbit Account | Profit Ceiling'. Sim Funded reset (before any payout) $599 on 50K Orbit.
- **TradeDay** `eval_min_days`: Conflict: help centre and plan card say 3 minimum days; the home FAQ says 'no minimum trading day requirement'; the Terms say a minimum 7-day period. Help centre value taken.
- **TradeDay** `eval_fee`: Conflict: home card (SALE60, 60% off) list $248 / $99 vs help table $180 (Sep 2026). Home card value is current.
- **TradeDay** `eval_min_days`: Terms say a minimum 7-day period (conflict, see Fast Pass block).
- **TradeDay** `eval_fee`: Conflict between sale card and help table, as for Fast Pass.
- **TradeDay** `payout_processing_days`: Same page later says 5:30 pm CT; ET/CT conflict within the page.
- **Top One Futures** `max_funded_accounts`: Conflict: the Elite Daily article allows mixing sizes ('You may mix account sizes within your 5 account limit') while the household and max-accounts articles say all 5 must be the same size; the homepage card shows 'Max Accounts 3 5'. The overview counts 5 funded per trader; the Elite Daily rule article counts eval + funded together per household.
- **Top One Futures** `eval_reset_fee`: Three official figures conflict ($82 / $93 / $104); the differences article says 'From $93 to $297'. Reset only within 14 days of breach; coupons do not apply. Funded reset $499.
- **Top One Futures** `payout_frequency_gate`: Minor conflict: the overview says the 50% rule applies 'For each payout request'; the payout article says 'After your first payout'. The differences article puts the first-payout threshold at 'Reach Buffer + $500'. Next eligibility starts the following trading day.
- **Top One Futures** `max_accounts`: See the screen note: the size-mixing and eval-counting rules conflict between articles. Over-limit accounts: the oldest active account is breached automatically.
- **Top One Futures** `copy_trading_terms`: Conflict: the Terms and Conditions list 'Copy trading, signal-following, or group trading with external accounts.' as prohibited, while the copy-trading article allows copying between your own accounts at other firms.
- **FXIFY Futures (trading as Futureify; FXIFY Futures Limited, Dublin)** `eval_min_days`: Wording conflict, same practical effect.
- **FXIFY Futures (trading as Futureify; FXIFY Futures Limited, Dublin)** `eval_time_limit`: Contradicts the lead 'no evaluation deadline'. Extension fee amount not stated.
- **FXIFY Futures (trading as Futureify; FXIFY Futures Limited, Dublin)** `funded_type`: Conflict between homepage ('Live') and FAQ ('simulated'). No rule on what happens after N payouts was found.
- **Funded Futures Network** `payout_split`: CONFLICT: the FAQ says the Sim Funded Pro account 'has an 80/20 profit split' (written for MAX accounts); the STEADY plan data says 90%.
- **My Funded Futures (MyFundedFutures, MFFU)** `copy_trading`: Re-read 2026-11-15: both texts stand. The help article (Aug 24 2026) is unconditional and names Tradesyncer / the Tradovate group copier; the Terms clause is qualified ('in a manner that provides an unfair advantage or manipulates simulated results'), so plain copying of one's own hand-entered trades is not on its face prohibited, but the qualifier is discretionary. Terms s.1.6 says the Terms prevail over incorporated documents in a conflict. Copying between different traders is prohibited.
- **My Funded Futures (MyFundedFutures, MFFU)** `funded_type`: Rapid Live (50K): $0 start, $2,000 EOD MLL stopping at $0, 90/10, daily payouts, 3 mini/30 micro per help article 13134718 -- but the /plans/rapid-eod Live table shows 4 / 40 for the 50K (conflict, Live only). A Live MLL breach starts a 21-day cooldown on Builder/Pro pages; for Rapid not stated.
- **My Funded Futures (MyFundedFutures, MFFU)** `funded_position_limit`: The Cross Instrument article's example mentions a Rapid 50k 'scaling plan' starting at 2 contracts; that contradicts the current Rapid 50K page (5 minis / 50 micros, no scaling) and looks stale. Rapid EOD pages state no scaling.
- **My Funded Futures (MyFundedFutures, MFFU)** `payout_processing_days`: Minor conflict (12 vs 24 business hours). Paid via Riseworks (bank transfer or crypto); Plaid/ACH for US traders.
- **My Funded Futures (MyFundedFutures, MFFU)** `copy_trading_terms`: Conflict between official pages, quoted both. Hand-entering the same trade in several own accounts is 'copying' in substance; the help article permits it outright.
- **My Funded Futures (MyFundedFutures, MFFU)** `funded_type`: Plan page FAQ says live parameters include 'a daily loss limit, reduced contract limits, and a static drawdown floor', while the help article's Live table shows 'Max Loss Limit (EOD Trailing) | -$2,000' and DLL None: conflict on Live only.
- **My Funded Futures (MyFundedFutures, MFFU)** `payout_frequency_gate`: Conflict: the Pro article (Oct 14 2026, newer) says the buffer must be cleared; the payout overview (Aug 25 2026) allows 60% before clearing. 'Every 14 calendar days' per the overview vs '14 days from first trade' per the article.
- **Phidias Propfirm** `payout_min`: CONFLICT between /rules ($500) and /tou ($1,000).
- **Phidias Propfirm** `fees_and_limits`: CONFLICT: TOU 3.1.1 limits E2L 150K to 1 account; /rules says the 150K counts as one slot within the 5.
- **Bulenox** `copy_trading`: Conflict: the Terms of Use (Oct 2026) require any third-party trading technology to be reviewed and approved by Bulenox before use (see automation).
- **Purdia Capital (Purdia Capital LLC)** `consistency_eval`: The two catalogs disagree on min days (None / 5 / 10), consistency and activation fee ($0 vs $130).

### Rule changes dated on the pages (read 2026-11-15)

- **Goat:** the 1-minute holding rule (9-10 Nov 2026). Funded Flex contract limits now scale from 2/20 to 4/40.
  A 14-day inactivity rule from 7 Nov.
- **Earn2Trade:** the Progression Ladder is gone for evaluations bought on or after 2026-11-02; contract caps are now
  enforced by the system.
- **TradeDay Fast Pass:** accounts opened on or after 2026-07-26 get a 45 % funded consistency rule and a $1,500
  (was $2,000) 50K payout cap.
- **The Trading Pit:**
  - the daily loss limit was removed from Prime Earning accounts on 14 July 2026, though the same article's summary
    table still lists it;
  - the daily profit threshold fell from $200 to $150 on 27 July 2026;
  - accounts created since 26/03/2026 pay no activation fee.
- **FundedNext:** Bolt and the former Rapid stopped selling on 10 July 2026, and Legacy on 11 October.
- **FunderPro:** a new product structure from 15 June 2026; stale pages still show the old 45 % rule and the
  60/70/80 % split ladder.
- **Alpha:** Premium was discontinued (15 Sept 2026 post); Standard was relaunched on 27 July 2026.
- **BluSky:** from 1 October 2026, live accounts start at $0 with sim profits held in a "Bonus Vault" (or a buyout
  at 50 % of the drawdown).
- **Lucid:** articles 11404728 (other trading activities) and 11404734 (hedging) show "Updated today". Their
  sentences quoted in Stage 2's ledger are still there.

## 3. Contract arithmetic, for the solver-only read that comes next

**This is arithmetic, not a simulation.** Each figure is a zero-edge **ceiling** computed from the quoted terms by
the bounds the multi-firm repository adopted as oracles
(`vendor/stage2/vendor/propfirms/docs/T3_CEILINGS_DERIVATION.md` section 1, stage one's method). For each plan:

- **evaluation:** P(pass) ≤ P̄ = D / (G + D) for any fair strategy (a two-phase funnel multiplies the phases);
- **funded:** E[gross payouts] ≤ min(C, K), where C is the cushion to the floor at funding and K the lifetime cap
  if one exists;
- **trader:** E[payouts to the trader per funded account] ≤ s · min(C, K), where s is the highest split that can
  apply;
- **cost:** E[fees per funded account] ≥ F / P̄ + A, where F is one evaluation's fee (**one month** if billed
  monthly) and A the activation fee charged on a pass;
- **per fee dollar:** payouts per fee dollar ≤ s · min(C, K) · P̄ / (F + P̄ · A). This is increasing in P̄, so
  using the bound keeps it a ceiling.

**What a funded loss costs** is only the fees already sunk. No page read here charges the trader for a funded breach
beyond the loss of the account; optional paid reactivations exist, such as Top One's funded reset and BluSky Orbit's
Sim Funded reset (their notes in Appendix A). **What a funded win pays** is at most the "funded value" column.

**How the table was made.** It is computed by a short script (in the scout's scratch folder) from inputs written
beside it, so every figure can be recomputed by hand. The prices are list prices; coupon prices are noted in the F
column. If the lead wants these figures as a result, the solver-only read should regenerate them from the rules
record with a manifest.

| rank | plan | G / D (eval) | Pbar = D/(G+D) | C | K | s (first / max) | funded value <= s*min(C,K) | F (basis) | A | fees per funded account >= F/Pbar + A | payouts per fee dollar <= | same, two monthly fees | seats |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | FunderPro Futures Beginner 50K | 3,000 / 2,000 | 0.400 | 2,000 | none | 0.80 / 0.80 | 1,600 | $79.00 (monthly) | 0 | 198 | **8.10** | 4.05 | 5 |
| 2 | Topstep 50K, No Activation Fee path (reference) | 3,000 / 2,000 | 0.400 | 2,000 | none | 0.90 / 0.90 | 1,800 | $95.00 (monthly) | 0 | 238 | **7.58** | 3.79 | 5 |
| 3 | DayTraders.com EOD 50K | 3,000 / 2,000 | 0.400 | 2,000 | none | 1.00 / 1.00 | 2,000 | $105.00 (basis unstated (Monthly or Lifetime)) | 5 | 268 | **7.48** | -- | 5 |
| 4 | Topstep 50K Combine -> XFA, Standard path (reference) | 3,000 / 2,000 | 0.400 | 2,000 | none | 0.90 / 0.90 | 1,800 | $49.00 (monthly) | 149 | 272 | **6.63** | 4.57 | 5 |
| 5 | The Trading Pit Futures Prime 50K | 3,000 / 2,000 | 0.400 | 2,000 | none | 0.80 / 0.80 | 1,600 | $99.00 (one-time) | 0 | 248 | **6.46** | -- | 5 |
| 6 | Aqua Futures Daily 50K | 3,000 / 2,000 | 0.400 | 2,000 | none | 0.90 / 0.90 | 1,800 | $113.00 (one-time (promo status unstated)) | 0 | 282 | **6.37** | -- | 5 |
| 7 | Alpha Futures Standard 50K | 3,000 / 2,000 | 0.400 | 2,000 | none | 0.90 / 0.90 | 1,800 | $129.00 (monthly) | 0 | 322 | **5.58** | 2.79 | 5 |
| 8 | Aqua Futures Flex Daily Loss 50K | 3,000 / 2,000 | 0.400 | 2,000 | none | 0.90 / 0.90 | 1,800 | $131.00 (one-time (promo status unstated)) | 0 | 328 | **5.50** | -- | 5 |
| 9 | FunderPro Futures Mid-Level 50K | 3,000 / 2,000 | 0.400 | 2,000 | none | 0.80 / 0.90 | 1,800 | $89.00 (monthly) | 129 | 352 | **5.12** | 3.14 | 5 |
| 10 | Lucid LucidFlex 50K | 3,000 / 2,000 | 0.400 | 2,000 | 10,000 | 0.90 / 0.90 | 1,800 | $165.00 (one-time (list; $115.50 with coupon, Stage 2 D-575)) | 0 | 412 | **4.36** | -- | 5 |
| 11 | Tradeify Select 50K (Flex path) | 3,000 / 2,000 | 0.400 | 2,000 | none | 0.90 / 0.90 | 1,800 | $165.00 (one-time) | 0 | 412 | **4.36** | -- | 5 |
| 12 | BluSky Launch 50K (Evaluation, then Buffer) | 3,000 / 2,000 then 3,000 / 2,000 | 0.160 | 2,900 | 10,000 | 0.90 / 0.90 | 2,610 | $59.00 (monthly, evaluation phase only) | 99 | 616 | **4.24** | 2.65 | 3 |
| 13 | Earn2Trade Gauntlet Mini 50K -> LiveSim | 3,000 / 2,000 | 0.400 | 2,000 | 5,000 | 0.50 / 0.80 | 1,600 | $170.00 (monthly) | 0 | 425 | **3.76** | 1.88 | 3 |
| 14 | FundedNext Futures Flex 50K | 2,500 / 1,500 | 0.375 | 1,500 | 7,500 | 0.95 / 0.95 | 1,425 | $141.99 (one-time (list; $74.99 with coupon)) | 0 | 379 | **3.76** | -- | 5 |
| 15 | TradeDay Quick Pay EOD 50K | 3,000 / 2,000 | 0.400 | 2,000 | 10,000 | 0.50 / 0.80 | 1,600 | $175.00 (one-time (help table; $69 sale card)) | 0 | 438 | **3.66** | -- | 5 |
| 16 | TradeDay Fast Pass EOD 50K | 3,000 / 2,000 | 0.400 | 2,000 | 6,000 | 0.80 / 0.80 | 1,600 | $180.00 (one-time (help table; $99 sale card)) | 0 | 450 | **3.56** | -- | 5 |
| 17 | Top One Futures Elite Daily V2 50K | 3,000 / 2,000 | 0.400 | 2,000 | none | 0.90 / 0.90 | 1,800 | $218.00 (conflict: monthly (help) vs one-time toggle (home)) | 0 | 545 | **3.30** | -- | 5 incl. evaluations |
| 18 | FXIFY Futures (Futureify) Flex 50K | 3,000 / 1,750 | 0.368 | 1,750 | none | 0.90 / 0.90 | 1,575 | $179.00 (one-time (list)) | 0 | 486 | **3.24** | -- | 5 incl. evaluations |
| 19 | Funded Futures Network STEADY 50K | 3,000 / 2,000 | 0.400 | 2,000 | 4,250 | 0.90 / 0.90 | 1,800 | $229.00 (one-time (list)) | 0 | 572 | **3.14** | -- | 5 |
| 20 | My Funded Futures Rapid EOD 50K | 3,000 / 2,000 | 0.400 | 2,000 | none | 0.90 / 0.90 | 1,800 | $275.00 (one-time (list; $165 with code)) | 0 | 688 | **2.62** | -- | 3 |
| 21 | Phidias Premium 50K, monthly path | 4,000 / 2,500 | 0.385 | 2,500 | none | 0.75 / 1.00 | 2,500 | $329.00 (monthly) | 149 | 1,004 | **2.49** | 1.34 | 5 |
| 22 | My Funded Futures Pro 50K | 3,000 / 2,000 | 0.400 | 2,000 | none | 0.80 / 0.80 | 1,600 | $265.00 (one-time (list; $159 with code)) | 0 | 662 | **2.42** | -- | 5 (25K/50K pool) |
| 23 | Alpha Futures Advanced 50K | 4,000 / 1,750 | 0.304 | 1,750 | none | 0.90 / 0.90 | 1,575 | $209.00 (monthly) | 0 | 687 | **2.29** | 1.15 | 3 |
| 24 | Phidias Premium 50K, one-time path | 4,000 / 2,500 | 0.385 | 2,500 | none | 0.75 / 1.00 | 2,500 | $723.00 (one-time) | 0 | 1,880 | **1.33** | -- | 5 |

Sources of the inputs, per row: FunderPro Futures Beginner 50K: funderpro.terms_beginner; Topstep 50K, No Activation Fee path (reference): Stage 2 rules.yaml: subscription_fee note (14289835); DayTraders.com EOD 50K: daytraders.terms; Topstep 50K Combine -> XFA, Standard path (reference): Stage 2 rules.yaml: combine_profit_target, combine_mll, xfa_mll_start, profit_split, subscription_fee, activation_fee, max_active_funded_accounts; The Trading Pit Futures Prime 50K: tradingpit.terms (split at most 80%; quote struck, E-020); Aqua Futures Daily 50K: aqua.terms_daily_50k; Alpha Futures Standard 50K: alpha.terms_standard; Aqua Futures Flex Daily Loss 50K: aqua.terms_flex_daily_loss_50k; FunderPro Futures Mid-Level 50K: funderpro.terms_midlevel; Lucid LucidFlex 50K: lucid 12945790, 12945815, 12945795, 12945796, 11404617 (read today); Tradeify Select 50K (Flex path): tradeify.terms; BluSky Launch 50K (Evaluation, then Buffer): blusky.terms; Earn2Trade Gauntlet Mini 50K -> LiveSim: e2t.terms ($139 activation is deducted from the first withdrawal: left out of F, so still a ceiling); FundedNext Futures Flex 50K: fundednext.terms; TradeDay Quick Pay EOD 50K: tradeday.terms_quick_pay_eod_50k (funded drawdown intraday); TradeDay Fast Pass EOD 50K: tradeday.terms_fast_pass_50k (K = 4 Sim payouts; the 5th request moves the account Live); Top One Futures Elite Daily V2 50K: topone.terms; FXIFY Futures (Futureify) Flex 50K: fxify.terms; Funded Futures Network STEADY 50K: ffn.terms (split conflict: FAQ 80/20); My Funded Futures Rapid EOD 50K: mffu.terms; Phidias Premium 50K, monthly path: phidias.terms; My Funded Futures Pro 50K: mffu.terms_pro50k; Alpha Futures Advanced 50K: alpha.terms; Phidias Premium 50K, one-time path: phidias.terms.

**Not computable** (an input is UNVERIFIED):

- Bulenox: the Master drawdown and payout terms.
- Take Profit Trader: G, D and the fee.
- Goat Flex: the price is drawn client-side.
- Legends and Purdia: the funded drawdown.

Lucid at the coupon price Stage 2 models ($115.50, D-575) gives 0.9 × 2,000 × 0.4 / 115.50 = 6.23.

**Reading the table.**

- **The ceiling is set by the fee and the split.** Almost every plan has Topstep's G, D and C, so
  P̄ · min(C, K) = 800 for most rows. K never binds: every lifetime cap here is at or above C.
- **Monthly billing is flattered by the one-month column.** The next column gives the same ceiling for an evaluation
  that runs two months. It halves where there is no activation fee, and falls less where there is one.
- **On this arithmetic the order is roughly:**
  - FunderPro Beginner;
  - Topstep's No Activation Fee path, DayTraders EOD and Topstep's Standard path;
  - The Trading Pit and Aqua Daily;
  - Alpha Standard, Aqua Flex and FunderPro Mid-Level;
  - Lucid and Tradeify at list price.

  The one-time-fee firms with high list prices (MFFU, FFN, Top One, FXIFY) come lower, and so do the plans with a
  thinner D against a larger G (Alpha Advanced, Phidias).
- **What the ceiling cannot see is what the solver-only read must add**, and much of it lowers the reachable
  fraction of the ceiling:
  - funded consistency rules: FunderPro 50 %, DayTraders 30 %, Phidias 30 %, Alpha Standard 40 %, FXIFY 40 %,
    TradeDay Fast Pass 45 %;
  - per-request caps and winning-day gates, which set the payout speed (FunderPro Beginner's cap is $1,000 a
    request);
  - finite sim lives and household-wide live moves;
  - two-phase funnels (BluSky);
  - the seat count, which multiplies supply: five at most firms, three at Alpha Advanced, MFFU Rapid EOD, BluSky
    and Earn2Trade.

**Payout fees.** These are UNVERIFIED at most firms and are charged at zero here, so every figure is also an upper
bound on them, as Stage 2 does for Lucid. Goat's 3 % payout fee is the one stated; Goat's row is not computable for
its price.

**A short ranking for the solver-only read.** This ranks the plans whose arithmetic inputs (G, D, C, s, F, A) are
all verified, in the table's order, with what must be settled before each one's seat count or price is believed:

1. FunderPro Beginner 50K: 50 % funded consistency; **one seat** until GTC 13.4 is answered in writing.
2. DayTraders EOD 50K: 30 % funded consistency; the fee's billing basis (Monthly or Lifetime) still to be read.
3. The Trading Pit Prime 50K: the split is at most 80% (discretionary); **one seat** until the IP clause is answered
   in writing.
4. Aqua Daily 50K and Aqua Flex Daily Loss 50K: the account-rolling ban; the 10-second and 0.3 reward-to-risk tests.
5. Alpha Standard 50K: 40 % funded consistency; 5 or 3 seats (the pages conflict).
6. FunderPro Mid-Level 50K: as Beginner.
7. Lucid LucidFlex 50K: already integrated in Stage 2, and the reference for a second firm.
8. FundedNext Flex 50K: a $74.99 coupon price is on the page.
9. TradeDay Fast Pass and Quick Pay EOD 50K: their sale-card prices are well below the help table's.

**Held back** until a browser read:

- Tradeify: its help centre is unreadable, and it governs (11 terms UNVERIFIED).
- BluSky: the funded minimum balance conflicts, and there are two phases.
- Top One: the billing basis conflicts.

**Open questions for that read:**

- **Which price is the price?** Coupons and sales recur at most of these firms (Stage 2 took Lucid's recurring coupon
  on the operator's word, D-575), so list against coupon is a declared reading.
- **Does a 50 % or 30 % funded consistency rule** cost more than the fee advantage buys? Only the solver can say.
- **How far below the ceiling** do the per-request caps hold the payout path, and at what speed?

## 4. What is unknown, and how it could be found

- **Unreadable hosts:**
  - all of Apex, Elite Trader Funding, TickTickTrader and E8;
  - Tradeify's, Bulenox's and Take Profit Trader's help centres and TPT's terms;
  - Legends' knowledge base;
  - FFN's rules page and help centre;
  - Purdia's whole site;
  - lucidtrading.com;
  - Futureify's terms (a PDF the extractor could not read).

  Each of these could be settled by **an operator browser read, which involves no purchase** (the D-574 pattern:
  screenshots saved unedited with their sha256). That is a `docs/OPERATOR_SETUP.md` item if the lead takes any of
  these firms further.
- **Needing a written answer from the firm** (a support question, which falls to the operator; Stage 2's
  `OPERATOR_SETUP.md` item 5 is the pattern):
  - The Trading Pit: does its clause against several accounts on one IP address or network bar one person
    holding several funded accounts from home?
  - FunderPro: does GTC 13.4 (linked or non-independent trading, including between one client's own accounts) bar
    trading one's own five accounts on one device?
  - My Funded Futures: help article against Terms 23.1.3.3 on copying.
  - Alpha Futures: 3 or 5 Advanced/Standard seats.

  Until such an answer exists, the safe default for these firms is **one seat**.
- **UNVERIFIED terms, by firm:** the list in section 2.
- **Not read at all:** each firm's checkout configurator. Prices drawn client-side (Goat, Take Profit Trader) are
  UNVERIFIED. Prices read from page-embedded data (Tradeify, DayTraders, Aqua, BluSky) are recorded as such in
  their notes.

## 5. What family C would need to declare

The bootstrap (6.3 C) says to run **a solver-only contract-fit read first** (payouts per fee dollar against
Topstep's $50K), and a campaign family only if a plan clears a declared bar. A declaration would need the following.

- **Mechanism.** The contract shape alone: does a firm's evaluation and funded contract return more per fee dollar
  than Topstep's for the same trade supply? EOD trailing keeps intraday excursions from moving the floor, and no
  funded consistency rule removes the best-day gate on payouts. The direction of any trade is not the lever here.
- **Supply.** P-14's and P-16's trade supply and state table, unchanged. The firm adds seats: 5 at most firms, 3 at
  Alpha Advanced, MFFU Rapid EOD, BluSky and Earn2Trade, and **evaluations count against the 5** at Top One and
  FXIFY. Per Stage 2 D-452, the firm can also add a second simultaneous position at another firm, subject to every
  firm's hedging ban:
  - opposite positions **across firms** are banned in writing at Lucid, BluSky, Tradeify and The Trading Pit, and
    Goat's anti-gaming rule names cross-firm hedging;
  - opposite positions in **correlated assets** across one's own accounts (ES against NQ, or NQ against MNQ) are
    banned at Lucid, BluSky, Tradeify, The Trading Pit, DayTraders, FundedNext, FFN, Aqua and Purdia.

  So the two-firm router's rule against opposite positions stays required.
- **Contract-fit constraints** (CHARTER section 4, per firm):
  - **News windows that catch a resting bracket.** The declared rule (no entry before 07:35 CT on a BLS 08:30 day)
    does not keep a bracket from filling at 08:30. A firm's own window must be declared as flat with no resting
    orders across it, or the release day skipped. The firms:
    - MFFU Rapid EOD: ±2 min;
    - Top One: ±2 min, and no close by any means;
    - TradeDay: auto-liquidation ±2 min;
    - FFN: flat ±1 min, including resting orders;
    - Take Profit Trader: flat ±1 min;
    - Goat funded: ±2 min;
    - Alpha Standard: ±2 min;
    - FunderPro: GTC ±2 min;
    - The Trading Pit: GTC ±2 min.
  - **Flatten times.** MFFU auto-closes at 4:10 PM ET, and Top One must be flat by 4:10 PM EST; both equal the
    design's 15:10 CT. FFN flattens at 4:50 PM ET.
  - **Minimum holds.** The 12.5/25-point NQ stops are far above every tick-based threshold, but the time-based ones
    need the design's trade-duration distribution (an engine read under the family, not a scout's):
    - Goat: ≥ 70 % of trades and of profit held > 1 min;
    - Top One: a 10-second minimum hold;
    - Aqua: 50 % of trades and profit held > 10 s, and an average reward-to-risk ≥ 0.3;
    - Tradeify: ≥ 50 % of profit from trades > 10 s;
    - The Trading Pit: > 50 % of profit from trades ≤ 15 s is flagged;
    - FundedNext: trades < 10 s making ≥ 40 % of cycle profit are deducted;
    - Alpha: < 10 ticks and < 2 min;
    - FXIFY: < 10 ticks and < 1 min.
  - **Purchase rate.** P-14 buys up to 20 evaluations in 21 sessions. That meets explicit rules against account
    rolling or stacking (Alpha, Aqua, FundedNext, FXIFY, The Trading Pit) and Top One's ban on "batch-buying
    evaluations and letting most fail". These are tier 3 under D-145 at best (priced, 0 % denial in the verdict),
    and Top One's wording reads closer to tier 1.
  - **Consistent sizing.** Tradeify's agreement, Alpha T&C 1.3.2 (risk kept at the evaluation level),
    Phidias and MFFU Pro's policy may bear on the state table's size changes between evaluation and funded trading.
  - **Live moves that close every sim account in the household:** Lucid, Alpha, FFN, MFFU, Top One, Tradeify, Goat,
    Aqua, BluSky, DayTraders and Phidias. Stage 2 models this for Lucid as `HOUSEHOLD_CLOSES_AT_LIVE`.
- **Cells and their count.** For the solver-only read: one cell per plan in section 3's short ranking. That is 11
  plans:
  - FunderPro Beginner and FunderPro Mid-Level;
  - DayTraders EOD;
  - The Trading Pit Prime;
  - Aqua Daily and Aqua Flex Daily Loss;
  - Alpha Standard;
  - Lucid;
  - FundedNext Flex;
  - TradeDay Fast Pass and TradeDay Quick Pay.

  Topstep is the reference. Each plan is read at its verified seat count, and at one seat where a written answer is
  pending. The family file must fix three things before anything is read:
  - the price reading (list or coupon);
  - the billing-duration reading for monthly plans;
  - the bar a plan must clear to earn a campaign family.

  Every rule enters only through the rules-verifier first. The family's k is the lead's: families are numbered in
  declaration order (E-001).

## Proposed queue line and decision row

- **TASK_QUEUE:**
  `| Q-xx | Family C, step 1: the rules-verifier records the terms of section 3's eleven plans (docs/research/firms_survey_2026-11-15.md, Appendix A) in config/rules_extended.yaml and docs/RULES_CURRENCY.md, one row per term, official pages only; the browser reads of section 4 put in docs/OPERATOR_SETUP.md (no purchase) | wt-firms | queued | Q-12 | light | 0 | -- |`
  and after it, the solver-only contract-fit read declared as a family file before it runs.
- **Decision row:** in the hand-back.

---

## Appendix A. Each firm's terms, verbatim, with their pages

The order follows section 3's ranking, then the firms with incomputable rows, then the rest. This appendix is
rendered from the quote-checked firm files; no quote was retyped. The eight firms struck under E-020 keep only
their heading, their screen verdict without quotes, and one line naming the clause (Q-34).

### FunderPro Futures (FunderPro Ltd., Malta) (`funderpro`) -- PASS

Verdict: **PASS** -- EOD trailing drawdown on funded (50% funded consistency), 5 funded accounts with own-account copy trading, nothing forbids manual bracket trading; GTC 13.4 clause on linked accounts and shared devices and the 30%-margin clause are caveats.

Struck (E-020): the firm's own terms forbid automated retrieval -- Terms & Conditions 12.5.6: "to use automated means to view, display or collect information available through the Website or Services" (as recorded in config/rules_extended.yaml, funderpro.automated_retrieval_terms). Removed on 2026-11-16 (Q-34): the firm's saved pages, the terms and quotes its file held, and this section; its plans are read, if ever, only through the operator's browser or with the firm's written permission.

### DayTraders.com (Day Traders) (`daytraders`) -- PASS

**Pages quoted** (key: URL; article id; the page's own date as shown; all read 2026-11-15)

- [P1] https://daytraders.com/help/articles/17704132-plan-comparison-overview; id 17704132; page date: Updated over 3 weeks ago
- [P2] https://daytraders.com/help/articles/17684729-eod-evaluation; id 17684729; page date: Updated over 3 weeks ago
- [P3] https://daytraders.com/help/articles/17684736-eod-pro-account; id 17684736; page date: Updated over 3 weeks ago
- [P4] https://daytraders.com/help/articles/17684746-eod-drawdown; id 17684746; page date: Updated over 3 weeks ago
- [P5] https://daytraders.com/help/articles/17684741-eod-consistency; id 17684741; page date: Updated over 3 weeks ago
- [P6] https://daytraders.com/help/articles/17704126-maximum-number-of-accounts; id 17704126; page date: Updated over a week ago
- [P7] https://daytraders.com/help/articles/17704093-account-sharing-vpn-vps-and-code-of-conduct; id 17704093; page date: Updated over 3 weeks ago
- [P8] https://daytraders.com/help/articles/17704087-automation-ai-and-trade-copiers; id 17704087; page date: Updated over 3 weeks ago
- [P9] https://daytraders.com/help/articles/17704076-no-hedging; id 17704076; page date: Updated over 3 weeks ago
- [P10] https://daytraders.com/help/articles/17704089-trading-hours-holidays-and-overnight-positions; id 17704089; page date: Updated over 3 weeks ago
- [P11] https://daytraders.com/help/articles/17704078-terms-of-use; id 17704078; page date: Last Updated: March 5, 2025
- [P12] https://daytraders.com/help/articles/17704073-no-martingale; id 17704073; page date: Updated over 3 weeks ago
- [P13] https://daytraders.com/help/articles/17704092-contract-limits; id 17704092; page date: Updated over 3 weeks ago
- [P14] https://daytraders.com/help/articles/17684742-eod-daily-loss-limit; id 17684742; page date: Updated over 3 weeks ago
- [P15] https://daytraders.com/
- [P16] https://daytraders.com/help/articles/17704104-billing; id 17704104; page date: Updated over 3 weeks ago
- [P17] https://daytraders.com/help/articles/17697925-moving-from-pro-or-s2f-to-live; id 17697925; page date: Updated over 3 weeks ago
- [P18] https://daytraders.com/help/articles/17684739-eod-payouts; id 17684739; page date: Updated over 3 weeks ago
- [P19] https://daytraders.com/help/articles/17704072-minimum-activity-policy; id 17704072; page date: Updated over 3 weeks ago
- [P20] https://daytraders.com/help/articles/17704120-market-data-add-ons-and-fees; id 17704120; page date: Updated over 3 weeks ago
- [P21] https://daytraders.com/help/articles/17704074-no-high-frequency-trading; id 17704074; page date: Updated over 3 weeks ago
- [P22] https://daytraders.com/help/articles/17704085-dollar-cost-averaging-dca; id 17704085; page date: Updated over 3 weeks ago
- [P23] https://daytraders.com/help/articles/17704134-instruments-and-commissions; id 17704134


Official domains: daytraders.com, daytraders.com/help (Intercom). Read 2026-11-15.
Plan captured: EOD 50K (evaluation -> EOD Pro Account). It is a futures (CME, Rithmic) evaluation comparable to a $50K one, so the firm is in scope..
Verdict: **PASS** -- EOD 50K: EOD trailing funded drawdown (stops at start), up to 5 EOD Pro accounts (15 sim funded overall, one login per household), copying own trades allowed; nothing forbids hand-entered bracket trading. Funded consistency is 30% per payout cycle.

Plans seen:
- EOD 50K (Rithmic): drawdown EOD trailing $2,000, stops at starting balance (eval and Pro); DLL $1,250 pause; consistency evaluation 50% (small tolerance), funded 30% per payout cycle
  - "| Consistency | 50% eval, 30% Pro | 50% eval, 30% Pro | 50% eval, 30% Pro | 20% per payout cycle | 25% eval, none in live" [P1]
- Trail 50K: drawdown intraday trailing $2,500 (follows peak equity incl. open positions); no DLL; consistency evaluation 50%, funded 30%
  - "| Drawdown type | Intraday trailing | Static (fixed) | End-of-day trailing | End-of-day trailing | Intraday trailing" [P1]
- Static 50K: drawdown static (fixed level that never moves); no DLL; 6 contracts; consistency evaluation 50%, funded 30% (fails the literal screen: not EOD and has a funded consistency rule)
  - "Static: You want a fixed drawdown level that never moves, for predictable risk." [P1]
- S2F 50K (Straight-to-Sim-Funded, sold as 'Instant'; no evaluation): drawdown EOD trailing; DLL on 50K; consistency evaluation n/a, funded 20% per payout cycle; 10 QDays between payouts; max 5 S2F
  - "At checkout, S2F appears as Instant and S2L as Live. Pro Accounts keep the drawdown type and contract limits of the evaluation you passed, and an account can't be changed after purchase." [P1]
- S2L Core 50K (straight-to-live evaluation): drawdown intraday trailing; consistency evaluation 25%, funded none in live; 80/20; only one live account tradeable at a time, all sim closed once live
  - "| Sizes | 25K, 50K, 150K, 300K | 25K, 50K, 100K, 150K | 25K, 50K, 150K, 300K | 25K, 50K, 150K | Core 50K, Edge 150K, Ultra 300K" [P1]

**Screen**

- `drawdown_eval` = **eod_trailing ($2,000), stops at starting balance** (verified)
  - "| Drawdown type | End-of-day (EOD) trailing | End-of-day (EOD) trailing | End-of-day (EOD) trailing | End-of-day (EOD) trailing" [P2]
- `drawdown_funded` = **eod_trailing ($2,000), stops at starting balance ($50,000); intraday balance must stay above it** (verified)
  - "| Drawdown type | End-of-day trailing; stops at starting balance | End-of-day trailing; stops at starting balance | End-of-day trailing; stops at starting balance | End-of-day trailing; stops at starting balance" [P3]
  - "Your balance must stay above it at all times, including intraday." [P4]
- `consistency_eval` = **50% (small tolerance); gates passing and Qualifying Days** (verified)
  - "EOD accounts have two consistency rules: 50% in the evaluation and 30% per payout cycle in the Pro Account." [P5]
- `consistency_funded` = **30% per payout cycle (best day / profit since last payout); a day over the limit is not a Qualifying Day and blocks payout requests** (verified)
  - "Consistency is checked at the end of every trading day. A day that ends over the limit isn't a Qualifying Day, and you can't pass or request a payout until you're back within it." [P5]
- `max_funded_accounts` = **5 EOD Pro accounts, within 15 simulated funded (Pro + S2F) in total; evaluations unlimited; one login per household** (verified)
  - "| EOD Pro Accounts | 5, within the 15" [P6]
  - "| Simulated funded accounts (Pro + S2F) | 15 in total" [P6]
  - "One login per household. If multiple accounts in a household are detected, all accounts may be subject to closure and all simulated or live profits forfeited." [P7]
  - note: Household-level limit (not per person). Terms of Use (Mar 5 2025) also say 'having multiple Day Traders Account's' may be treated as gambling-type ordering -- read as multiple logins, not multiple trading accounts.
- `copy_trading` = **allowed across own accounts, including accounts at other firms; not into others' accounts** (verified)
  - "Trade copiers that copy trades across your own accounts, including accounts at other firms." [P8]
  - "Trading with other firms is allowed, and so is copying the same trades across your own accounts." [P9]
  - note: The Terms of Use (Last Updated March 5, 2025) prohibit 'Sharing trades and strategies with other users or making trades that were not Customer's own creation' -- about other users, not own-account copying; no conflict for own accounts.
- `opposite_positions` = **prohibited within and across own accounts, incl. correlated instruments (long NQ / short ES)** (verified)
  - "Hedging is prohibited within an account and across your accounts." [P9]
  - "Opposite positions in related or correlated instruments, such as long NQ in one account and short ES in another." [P9]
- `news` = **allowed (not recommended); no blackout window** (verified)
  - "Trading around news is allowed but not recommended." [P10]
- `automation` = **AI, scripts, bots, copiers and VPS allowed if not HFT-style; hand entry unaffected** (verified)
  - "You can use AI tools, automations, scripts, custom algorithms and trading bots, as long as they follow all account rules and don't operate as High-Frequency Trading (HFT)." [P8]
  - "Using, such software, AI, high frequency automated trading, mass data entry, or other programs that manipulate or abuse the Pro Accounts or the simulated trading environment give Customer an unfair advantage when using the services;" [P11]
- `sizing_gambling` = **Martingale prohibited; DCA within max contracts allowed; max 10 contracts (10 micros = 1 mini) across all instruments; Terms: no positions substantially larger than your other trades, no grossly overleveraged positions** (verified)
  - "The Martingale strategy, or doubling down after losses, is prohibited on every plan and every instrument." [P12]
  - "| EOD | 25K: 6 · 50K: 10 · 150K: 12 · 300K: 40" [P13]
  - "Engaging in trading practices that are in contradiction of standard risk management rules applicable to the relevant financial market, including but not limited to opening positions of substantially larger sizes than other trades on the Day Traders Accounts;" [P11]
  - note: No minimum hold time; HFT (millisecond order placement/modification) prohibited.

**Terms (`terms`)**

- `eval_profit_target` = **3000** (verified)
  - "| Profit target | $1,500 | $3,000 | $8,500 | $15,000" [P2]
  - note: Columns 25K | 50K | 150K | 300K.
- `eval_drawdown_amount` = **2000** (verified)
  - "| Max drawdown | $1,000 | $2,000 | $4,000 | $6,500" [P2]
- `eval_drawdown_type` = **eod_trailing** (verified)
  - "EOD accounts use an end-of-day trailing drawdown: the level only moves after each trading day closes, based on your closing balance." [P4]
- `eval_drawdown_lock` = **stops at starting balance ($50,000)** (verified)
  - "It stops at your starting balance, in the evaluation and in the Pro Account." [P4]
  - "| 50K | $2,000 | $48,000 | $50,000" [P4]
- `eval_daily_loss_limit` = **1250 USD; help: positions closed and account Paused to the next session (not failed); Terms of Use: 'Hard Breach' auto-liquidated for the session -- CONFLICT in wording** (verified)
  - "| 50K | $1,250" [P14]
  - "Open positions are closed and the account is Paused until the next trading day starts (6:00 PM ET). It isn't failed." [P14]
  - "The DLL is measured from your balance at the start of the day. It doesn't trail intraday." [P14]
  - "the account will hit a Hard Breach and will be auto-liquidated for the remainder of the then current trading session." [P11]
  - note: Both describe a session-long liquidation/pause; the help article (newer) says the account is not failed.
- `eval_consistency_rule` = **50% of total profit since start (small tolerance)** (verified)
  - "Keep your best day at or below 50% of your total profit. A small tolerance applies." [P2]
- `eval_min_days` = **2 Qualifying Days (each >= $200 net profit on 50K, within rules and consistency)** (verified)
  - "Trade at least 2 Qualifying Days: days that meet the minimum daily profit, follow the rules and end within consistency." [P2]
  - "| Min. daily profit | $100 | $200 | $300 | $400" [P2]
- `eval_position_limit` = **10 contracts (100 micros), total across instruments** (verified)
  - "| Max contracts | 6 (60 micros) | 10 (100 micros) | 12 (120 micros) | 40 (400 micros)" [P2]
- `eval_fee` = **105 USD (homepage pricing data for 50K EOD); billing basis Monthly (rebills every 30 days) or Lifetime (one payment) chosen at checkout -- which basis the 105 is: not stated** (verified)
  - ""title":"50K EOD","subtitle":"End-of-Day Drawdown","capital":50000" [P15]
  - ""price":105,"activationFee":5" [P15]
  - "When you buy an account individually, you choose Monthly or Lifetime billing at checkout. This applies to evaluations, S2F and S2L." [P16]
  - note: Price from the homepage pricing widget's embedded data (PS_DATA), not visible text. Lifetime vs Monthly price difference not readable. Bulk purchases are one-time.
- `eval_reset_fee` = **no resets** (verified)
  - "No time limit and no resets." [P2]
- `activation_fee` = **5 USD (Monthly Pro rebills $5 every 30 days; Lifetime once); activate within 10 days of passing or the pass is forfeited** (verified)
  - "Activate your EOD Pro Account within 10 days for $5, or the pass is forfeited." [P2]
  - "A Monthly Pro Account rebills the $5 activation fee every 30 days." [P16]
- `eval_count_limit` = **unlimited** (verified)
  - "| Evaluations (Trail, Static, EOD) | Unlimited" [P6]
- `eval_time_limit` = **none (subject to the minimum activity policy)** (verified)
  - "No time limit and no resets." [P2]
- `funded_type` = **sim funded (EOD Pro Account); Live only by invitation (about 1% of sim funded traders); on a live call all sim accounts close, excess sim balances generally forfeited; Pro accounts without a payout refunded** (verified)
  - "There's no fixed milestone: performance, consistency and rule-following are reviewed continuously, and about 1% of simulated funded traders are currently moved to live." [P17]
  - "Once you're live, your simulated accounts are closed. Excess simulated balances are generally forfeited, but they may be used as performance rewards in live, subject to the Risk Team's discretion." [P17]
  - "$10,000 or more: half is paid to your Payout Method and half becomes your live account's max drawdown." [P17]
- `funded_drawdown_amount` = **2000** (verified)
  - "| Max drawdown | $1,000 | $2,000 | $4,000 | $6,500" [P3]
- `funded_drawdown_type` = **eod_trailing** (verified)
  - "An EOD Pro Account is the simulated funded account you unlock by passing an EOD evaluation. It keeps the evaluation's drawdown type and contract limits." [P3]
- `funded_drawdown_lock` = **stops at starting balance ($50,000)** (verified)
  - "It stops at your starting balance, in the evaluation and in the Pro Account." [P4]
- `payout_balance_consequence` = **request only at balance >= $52,600 and must stay >= $52,000 after the payout (floor locked at $50,000 leaves >= $2,000 cushion)** (verified)
  - "| Size | Min. balance to request | Min. balance after payout | Max per request" [P18]
  - "| 50K | $52,600 | $52,000 | $2,000" [P18]
- `funded_daily_loss_limit` = **1250 USD, pause to next session (not failed); see eval_daily_loss_limit for the Terms wording conflict** (verified)
  - "| Daily Loss Limit | $800 | $1,250 | $2,000 | $3,250" [P3]
- `funded_consistency_rule` = **30% per payout cycle** (verified)
  - "Your best day is no more than 30% of the cycle's profit." [P18]
- `funded_position_limit` = **10 contracts (100 micros), same as evaluation; no scaling plan** (verified)
  - "| Max contracts | 6 (60 micros) | 10 (100 micros) | 12 (120 micros) | 40 (400 micros)" [P3]
  - "Pro Accounts keep the same limits as their evaluation." [P13]
- `funded_monthly_fee` = **Monthly Pro: $5 every 30 days; Lifetime Pro: none** (verified)
  - "Pro Accounts: you choose Monthly or Lifetime at the activation checkout. A Monthly Pro Account rebills the $5 activation fee every 30 days." [P16]
- `payout_min` = **500 USD, in $50 increments** (verified)
  - "EOD Pro Accounts have a 100% split of eligible simulated profit. Requests start at $500, in $50 increments." [P18]
- `payout_cap` = **2000 USD per request; lifetime cap not stated** (verified)
  - "| Max per payout request | $1,000 | $2,000 | $3,500 | $5,000" [P3]
  - note: Lifetime cap: UNVERIFIED (none stated).
- `payout_frequency_gate` = **8 Qualifying Days (each >= $200, within 30% consistency) since last payout or activation; request day not counted** (verified)
  - "8 Qualifying Days since your last payout or activation. The day you request doesn't count." [P18]
- `payout_split` = **100% (of simulated profit)** (verified)
  - "| Profit split | 100% (simulated) | 100% (simulated) | 100% (simulated) | 100% (simulated)" [P3]
- `payout_processing_days` = **UNVERIFIED as a rule (automated approval; the payouts page shows tracked examples of 1-21 hours)** (UNVERIFIED)
  - "Our payout approval process is transparent, automated, and lightning-fast." [P15]
  - looked at: help 17704121, 17684739; https://daytraders.com/payouts (a feed of recent payouts with processing times, not a rule)
- `payout_fee` = **UNVERIFIED** (UNVERIFIED)
  - looked at: help 17704121, 17704120 (fees list: add-ons, $5 activation, commissions -- no payout fee listed), 17704104
- `payout_count_limit` = **UNVERIFIED (none stated)** (UNVERIFIED)
  - looked at: help 17684736, 17684739, 17704121
- `max_accounts` = **5 EOD Pro (within 15 sim funded); evaluations unlimited; live: 5, one tradeable at a time; one login per household** (verified)
  - "| Live accounts | 5, with only one tradeable at a time" [P6]
  - "You can't trade simulated and live accounts at the same time." [P6]
- `inactivity_rule` = **in every rolling 30-day window: >= 4 trading days meeting the minimum daily profit ($200 on 50K) for Lifetime/bulk accounts, >= 1 for Monthly; else Inactive and closed, no reactivation** (verified)
  - "| Lifetime (one-time, including bulk purchases) | At least 4 trading days meeting the minimum daily profit in every rolling 30-day window" [P19]
  - "| Monthly | At least 1 trading day meeting the minimum daily profit in every rolling 30-day window" [P19]
  - "The account is marked Inactive and closed. Inactive accounts can't be reactivated, and a Monthly account stops rebilling." [P19]
  - note: Unusual: activity is measured in PROFITABLE days (>= minimum daily profit), not trades. A losing streak of a month can close a Lifetime account.
- `copy_trading_terms` = **own accounts allowed (rTrader Pro Copier add-on $10/month); not into others' accounts; copier must not hedge or exceed max contracts** (verified)
  - "Using a copier or automation to hedge or to exceed your max contracts." [P8]
  - "| rTrader Pro Copier | $10 per month" [P20]
- `cross_account_hedging` = **prohibited (Terms and help agree)** (verified)
  - "Using hedging trades between the Day Traders Account(s), different accounts under the same account holder, or in concert with any other persons;" [P11]
- `news_trading_terms` = **allowed, not recommended; losses from fast markets not covered** (verified)
  - "Fast markets can hit daily price limits or cause platform lag, and losses from these conditions aren't covered." [P10]
- `automation_terms` = **allowed at normal execution speeds; HFT prohibited** (verified)
  - "High-Frequency Trading (HFT) isn't allowed on any account. Automation is allowed as long as it doesn't trade in an HFT style." [P21]
- `sizing_or_gambling_terms` = **no Martingale; no substantially larger / grossly overleveraged positions vs your other trades (Terms); DCA allowed** (verified)
  - "opening positions that are grossly overleveraged;" [P11]
  - "Dollar Cost Averaging (DCA) is allowed on every plan: evaluations, Pro Accounts, S2F, S2L and live accounts." [P22]
- `other_conduct_bearing` = **overnight: help says allowed and not auto-closed; Terms (Mar 5 2025) say positions must be closed before 5:00 PM and are auto-flattened -- CONFLICT. VPN/VPS allowed. Professionals (Series licences, SEC/NFA registered) excluded.** (verified)
  - "Holding positions overnight or over the weekend is allowed but not recommended, because of mark-to-market adjustments. DayTraders doesn't close your positions for you at the end of the session." [P10]
  - "All trades will be attempted to be automatically flattened upon the relevant market closure. Traders must close all positions prior to 5:00 PM ET;" [P11]
  - "Professionals (people with Series licenses or registered with the SEC, NFA or another regulator) can't take part in our simulated programs, including S2L." [P20]
  - note: The Terms are older (last updated March 5, 2025) and link rules articles on help.daytraders.com that were not read; the help-centre articles are newer (~3 weeks). Our design is intraday, so the overnight conflict does not bind it.
- `permitted_products` = **CME-group futures via Rithmic; ES, NQ, MES, MNQ listed** (verified)
  - "| Equity | E-mini S&P 500 (ES), E-mini Nasdaq-100 (NQ), Mini-Dow (YM), Russell 2000 (RTY), E-mini Midcap 400 (EMD), Nikkei (NKD)" [P23]
  - "| Micros | MES, MNQ, MYM, M2K, Micro Gold (MGC), Micro Crude Oil (MCL), Micro AUD/USD (M6A), Micro EUR/USD (M6E)" [P23]
  - "| Equity | ES, NQ, YM, RTY, EMD, NKD | $3.98" [P23]
  - "| Micros | MES, MNQ, MYM, M2K, MCL | $1.02" [P23]
  - note: Commissions are per contract, round turn, on every simulated account (table 'Group | Symbols | Round turn'): NQ $3.98, MNQ $1.02; profit target is net of commissions.

### The Trading Pit (`tradingpit`) -- PASS

Verdict: **PASS** -- Futures Prime 50K: EOD trailing drawdown on the Earning account and no Earning-phase consistency rule; 5 Earning accounts; hand-entered one-position bracket trades are allowed (stops recommended), subject to the GTC's 2-minute news-bracketing ban.

Struck (E-020): the firm's own terms forbid automated retrieval -- GTC 4.5.2: "automated retrieval or extraction of data (scraping, crawling, or similar methods) without our express written permission" (as recorded under E-009). Removed on 2026-11-16 (Q-34): the firm's saved pages, the terms and quotes its file held, and this section; its plans are read, if ever, only through the operator's browser or with the firm's written permission.

### Aqua Futures (AquaFutures / AquaFunded Futures) (`aqua`) -- PASS

Verdict: **PASS** -- Flex Daily Loss and Daily have EOD funded drawdowns and no funded consistency, 5 funded accounts at once, copiers among own accounts allowed; hand-entered bracket trading is allowed (bots banned; watch the 10-second, 0.3RR and account-rolling rules).

Struck (E-020): the firm's own terms forbid automated retrieval -- Terms of Service: "You are expressly prohibited from scraping, crawling, framing, posting unauthorized links to, aggregating, hacking, performing denial of service (DOS) attacks on, reverse engineering, or circumventing technological protection measures of the Services or the Company website." (as recorded in config/rules_extended.yaml, aqua.automated_retrieval_terms). Removed on 2026-11-16 (Q-34): the firm's saved pages, the terms and quotes its file held, and this section; its plans are read, if ever, only through the operator's browser or with the firm's written permission.

### Alpha Futures (`alpha`) -- PASS

Verdict: **PASS** -- EOD trailing MLL (locks at start) on every plan and no funded consistency on Advanced; 3 Advanced (5 Standard) funded per household; hand-entered bracket trading not forbidden (only tight-bracket sim-fill exploitation and <10-tick/<2-min scalping).

Struck (E-020): the firm's own terms forbid automated retrieval -- "any automated use of the system, such as ... web scraping robots" (as recorded under E-009). Removed on 2026-11-16 (Q-34): the firm's saved pages, the terms and quotes its file held, and this section; its plans are read, if ever, only through the operator's browser or with the firm's written permission.

### Lucid Trading (`lucid`) -- PASS

**Pages quoted** (key: URL; article id; the page's own date as shown; all read 2026-11-15)

- [P1] https://support.lucidtrading.com/en/articles/12945815-lucidflex-drawdown; id 12945815-lucidflex-drawdown; page date: August 26, 2026
- [P2] https://support.lucidtrading.com/en/articles/12945795-lucidflex-funded-account; id 12945795-lucidflex-funded-account; page date: October 13, 2026
- [P3] https://support.lucidtrading.com/en/articles/12945805-lucidflex-consistency; id 12945805-lucidflex-consistency; page date: Updated over a month ago
- [P4] https://support.lucidtrading.com/en/articles/11404617-maximum-number-of-accounts; id 11404617-maximum-number-of-accounts; page date: August 26, 2026
- [P5] https://support.lucidtrading.com/en/articles/11404728-other-trading-activities; id 11404728-other-trading-activities; page date: Updated today (2026-11-15)
- [P6] https://support.lucidtrading.com/en/articles/11404734-hedging; id 11404734-hedging; page date: Updated today (2026-11-15)
- [P7] https://support.lucidtrading.com/en/articles/12945790-lucidflex-evaluation-account; id 12945790-lucidflex-evaluation-account; page date: Updated over a month ago
- [P8] https://support.lucidtrading.com/en/articles/12945796-lucidflex-payouts; id 12945796-lucidflex-payouts; page date: July 28, 2026
- [P9] https://support.lucidtrading.com/en/articles/16558826-new-live-structure; id 16558826-new-live-structure; page date: October 14, 2026


Official domains: lucidtrading.com, support.lucidtrading.com. Read 2026-11-15.
Plan captured: LucidFlex 50K (Stage 2's verified second firm; re-read today).
Verdict: **PASS** -- EOD trailing funded drawdown locking at start + $100, no funded consistency, 5 funded per household; hand entry unrestricted (already Stage 2's verified second firm, D-561/D-575).

Unreadable (not worked around):
- https://lucidtrading.com/ -- Cloudflare challenge ('Just a moment...') to an honest client; not worked around (as Stage 2 D-561)

**Screen**

- `drawdown_eval` = **eod_trailing** (verified)
  - "LucidFlex evaluation and funded accounts use an End-of-Day Drawdown (EOD Drawdown) system to calculate the Max Loss Limit (MLL)." [P1]
- `drawdown_funded` = **eod_trailing** (verified)
  - "LucidFlex funded accounts have an optional Daily Loss Limit, no consistency rule and no payout buffer. 90/10 profit split. EOD trailing drawdown." [P2]
- `consistency_eval` = **40% (50% paid add-on); gates the upgrade, not a breach** (verified)
  - "In LucidFlex evaluation accounts your Consistency Percentage must be 40% or less to be eligible to upgrade to a LucidFlex funded account." [P3]
  - "Largest Single Day Profit / Account Profit = Consistency Percentage" [P3]
- `consistency_funded` = **none** (verified)
  - "There is no Consistency Percentage on LucidFlex funded accounts" [P2]
- `max_funded_accounts` = **5 funded per household** (verified)
  - "Account Limit: Up to 5 active funded accounts per household or family." [P4]
- `copy_trading` = **permitted** (verified)
  - "Automated trading systems and trade copiers are permitted" [P5]
- `opposite_positions` = **prohibited, including across firms and correlated assets (ES against NQ)** (verified)
  - "Hedging between different firms or funded platforms" [P6]
  - "Example: You cannot go long ES in one account and short NQ in a separate account." [P6]
- `news` = **allowed on Flex** (verified)
  - "Traders may enter or exit positions around scheduled or unscheduled news events on these plans without it being a breach" [P5]
- `automation` = **permitted (no bearing on hand entry)** (verified)
  - "Automated trading systems and trade copiers are permitted" [P5]
- `sizing_gambling` = **martingaling discouraged; scaling in allowed** (verified)
  - "While scaling is permitted, martingaling, continuously adding to losing positions in hopes of recovery, is strongly discouraged" [P5]

**Terms (`terms`)**

- `eval_profit_target` = **3000** (verified)
  - "| Account Size | Profit Target | Max Loss Limit | Consistency % | Max Size" [P7]
  - "| $50,000 | $3,000 | $2,000 | 40% (50% with add-on) | 4 mini or 40 micros" [P7]
- `eval_drawdown_amount` = **2000** (verified)
  - "| Account Size | MLL Amount | Initial Trail Balance | Locked MLL Balance" [P1]
  - "| $50,000 | $2,000 | $52,100 | $50,100" [P1]
- `eval_drawdown_type` = **eod_trailing** (verified)
  - "LucidFlex evaluation and funded accounts use an End-of-Day Drawdown (EOD Drawdown) system to calculate the Max Loss Limit (MLL)." [P1]
- `eval_drawdown_lock` = **locks at start + $100 ($50,100) once the balance exceeds $52,100** (verified)
  - "Once your account exceeds the Initial Trail Balance, the MLL locks and no longer moves" [P1]
  - "Once the account exceeds the trail, the MLL locks at the initial balance plus $100" [P1]
- `eval_daily_loss_limit` = **optional at checkout (modelled off)** (verified)
  - "Customize at checkout: Daily Loss Limit On or Off, and 40% or 50% consistency (see LucidFlex Customization)" [P7]
- `eval_consistency_rule` = **40% (50% paid add-on); gates the upgrade, not a breach** (verified)
  - "In LucidFlex evaluation accounts your Consistency Percentage must be 40% or less to be eligible to upgrade to a LucidFlex funded account." [P3]
  - "Largest Single Day Profit / Account Profit = Consistency Percentage" [P3]
- `eval_min_days` = **3** (verified)
  - "Pass in as few as 3 days with 40% consistency, or 2 days with the 50% consistency add-on" [P7]
- `eval_position_limit` = **4 minis / 40 micros** (verified)
  - "| $50,000 | $3,000 | $2,000 | 40% (50% with add-on) | 4 mini or 40 micros" [P7]
- `eval_fee` = **one-time; $115.50 with the recurring coupon (list $165), DLL off, 40% -- Stage 2 D-575 (operator screenshots 2026-11-05)** (verified)
  - "One-time fee, no monthly rebilling, take as long as you need to pass" [P7]
  - note: The billing basis is re-read today; the price is not (lucidtrading.com serves a Cloudflare challenge to an honest client, not worked around). The price is Stage 2's verified row (D-575, the multi-firm repository's D-31): Stage 2's vendored ledger vendor/stage2/vendor/propfirms/firms/lucid-trading/rules.yaml eval_fee.
- `eval_reset_fee` = **$115 (Stage 2 D-575)** (verified in Stage 2, not re-read today)
  - looked at: lucidtrading.com unreadable today; Stage 2's vendored ledger vendor/stage2/vendor/propfirms/firms/lucid-trading/rules.yaml eval_reset_fee
- `activation_fee` = **none** (verified)
  - "No activation fees to upgrade to funded account" [P7]
- `eval_count_limit` = **10 evaluations per household; 10 accounts in total** (verified)
  - "Account Limit: Up to 10 active evaluation accounts per household or family." [P4]
  - "Shared Limit: Traders may hold a maximum of 10 accounts in total across evaluation accounts and funded accounts." [P4]
- `eval_time_limit` = **none** (verified)
  - "One-time fee, no monthly rebilling, take as long as you need to pass" [P7]
- `funded_type` = **sim funded; up to 5 payouts per account, then the live review pool (discretionary)** (verified)
  - "Number of requests per account: Traders may take up to 5 payouts from each LucidFlex account after which they will be moved live." [P8]
  - "All live transitions occur at the discretion of the Lucid risk team." [P9]
- `funded_drawdown_amount` = **2000** (verified)
  - "| $50,000 | $2,000 | Optional | Yes | 4 mini or 40 micros" [P2]
- `funded_drawdown_type` = **eod_trailing** (verified)
  - "LucidFlex funded accounts have an optional Daily Loss Limit, no consistency rule and no payout buffer. 90/10 profit split. EOD trailing drawdown." [P2]
- `funded_drawdown_lock` = **locks at start + $100** (verified)
  - "Once the account exceeds the trail, the MLL locks at the initial balance plus $100" [P1]
- `payout_balance_consequence` = **a payout request forces the lock at $50,100** (verified)
  - "Once you request a payout from LucidFlex, your MLL automatically adjusts to the Locked MLL Balance" [P1]
- `funded_daily_loss_limit` = **optional, chosen at evaluation purchase** (verified)
  - "The ability to customize whether each Flex Funded account has a Daily Loss Limit at the time of evaluation purchase" [P2]
- `funded_consistency_rule` = **none** (verified)
  - "There is no Consistency Percentage on LucidFlex funded accounts" [P2]
- `funded_position_limit` = **4 minis / 40 micros, with a scaling plan (tiers: Stage 2's row funded_position_limit, article 12945808, not re-read today)** (verified)
  - "| $50,000 | $2,000 | Optional | Yes | 4 mini or 40 micros" [P2]
- `funded_monthly_fee` = **None** (UNVERIFIED)
  - looked at: 12945795, 12945796 today; Stage 2 D-561/D-575 found no official statement either way (charged at zero; every Lucid result labelled an upper bound)
- `payout_min` = **500** (verified)
  - "Minimum payout request: $500" [P8]
- `payout_cap` = **50% of profit up to $2,000 per request; does not scale; 5 requests per account** (verified)
  - "| $50,000 | 50% of Profit up to $2,000" [P8]
  - "Unlike our other prop firm funded accounts, the maximums here do not scale up with more payouts. The table above shows the payout maximums for all requests." [P8]
  - note: The same page also says 'Futures traders may request 50% of their account balance up to a maximum dollar amount' (Stage 2 D-561 (3): the table reading is modelled, the other reported beside).
- `payout_frequency_gate` = **any day; per cycle 5 days of >= $150 profit and net profit > 0** (verified)
  - "Traders must earn at least the minimum required profit on 5 separate days during the payout cycle. The minimum profit on trading days reset and must be earned again after every approved payout." [P8]
  - "| $50,000 | $150" [P8]
  - "There is no fixed payout window, you may request a payout any day after meeting all eligibility criteria." [P8]
- `payout_split` = **0.9** (verified)
  - "All LucidFlex funded account payouts are split 90% to the trader and 10% to Lucid Trading." [P8]
- `payout_processing_days` = **within 2 business days** (verified)
  - "Payouts will be disbursed to your payment method within 2 business days." [P8]
- `payout_fee` = **None** (UNVERIFIED)
  - looked at: 12945796 today (no fee stated); Stage 2 D-561
- `payout_count_limit` = **5** (verified)
  - "Number of requests per account: Traders may take up to 5 payouts from each LucidFlex account after which they will be moved live." [P8]
- `max_accounts` = **5 funded per household** (verified)
  - "Account Limit: Up to 5 active funded accounts per household or family." [P4]
- `inactivity_rule` = **None** (UNVERIFIED)
  - looked at: not re-read today; the multi-firm repository's D-07 recorded a 30-day inactivity deletion -- a lead, to be re-read before use
- `copy_trading_terms` = **permitted** (verified)
  - "Automated trading systems and trade copiers are permitted" [P5]
- `cross_account_hedging` = **prohibited, including across firms and correlated assets (ES against NQ)** (verified)
  - "Hedging between different firms or funded platforms" [P6]
  - "Example: You cannot go long ES in one account and short NQ in a separate account." [P6]
- `news_trading_terms` = **allowed on Flex** (verified)
  - "Traders may enter or exit positions around scheduled or unscheduled news events on these plans without it being a breach" [P5]
- `automation_terms` = **permitted (no bearing on hand entry)** (verified)
  - "Automated trading systems and trade copiers are permitted" [P5]
- `sizing_or_gambling_terms` = **martingaling discouraged; scaling in allowed** (verified)
  - "While scaling is permitted, martingaling, continuously adding to losing positions in hopes of recovery, is strongly discouraged" [P5]
- `other_conduct_bearing` = **the live move closes every sim account in the household** (verified)
  - "All simulated prop accounts are closed when a trader is moved live, or opts out of trading live via cash-out." [P9]

### Tradeify (`tradeify`) -- PASS

Verdict: **PASS** -- Select 50K: EOD trailing drawdown on both funded paths and no funded consistency; 5 funded accounts per person/household (FTA 4.2); the agreement expects stops and targets and forbids nothing in hand-entered one-position bracket trading on NQ/MNQ.

Struck (E-020): the firm's own terms forbid automated retrieval -- Terms of Use: "use any robot, spider, scraper or other automatic device ... to access, harvest, monitor, copy or use the Site" without permission (as recorded under E-009). Removed on 2026-11-16 (Q-34): the firm's saved pages, the terms and quotes its file held, and this section; its plans are read, if ever, only through the operator's browser or with the firm's written permission.

### BluSky Trading Company (`blusky`) -- PASS

**Pages quoted** (key: URL; article id; the page's own date as shown; all read 2026-11-15)

- [P1] https://help.blusky.pro/en/articles/14184170-evaluation-overview; id 14184170; page date: July 31, 2026
- [P2] https://help.blusky.pro/en/articles/16300862-propel-plans-phases-rules-and-costs; id 16300862; page date: Updated this week
- [P3] https://help.blusky.pro/en/articles/16300866-orbit-plans-two-phases-faster-payouts; id 16300866; page date: October 15, 2026
- [P4] https://help.blusky.pro/en/articles/16300869-instant-funding-direct-to-funded-and-instant-sim-funded; id 16300869; page date: August 12, 2026
- [P5] https://help.blusky.pro/en/articles/16300846-launch-plans-phases-rules-and-costs; id 16300846; page date: Updated over a week ago
- [P6] https://help.blusky.pro/en/articles/12434059-evaluation-rules; id 12434059; page date: Updated over a month ago
- [P7] https://help.blusky.pro/en/articles/12434458-buffer-stage; id 12434458; page date: Updated this week
- [P8] https://help.blusky.pro/en/articles/12434469-sim-funded-accounts-processing; id 12434469; page date: July 28, 2026
- [P9] https://blusky.pro/
- [P10] https://help.blusky.pro/en/articles/12433943-multiple-accounts-copy-trading; id 12433943; page date: Updated over 3 weeks ago
- [P11] https://help.blusky.pro/en/articles/17297032-sim-funded-accounts-rules; id 17297032; page date: Updated this week
- [P12] https://help.blusky.pro/en/articles/12069208-ethical-trading-conduct-policy-blusky-trading-company; id 12069208; page date: February 23, 2026
- [P13] https://help.blusky.pro/en/articles/17679634-hedging-is-prohibited; id 17679634; page date: Updated over 3 weeks ago
- [P14] https://help.blusky.pro/en/articles/12433870-what-to-expect; id 12433870; page date: February 2, 2026
- [P15] https://help.blusky.pro/en/articles/12434092-resets; id 12434092; page date: Updated over 3 weeks ago
- [P16] https://help.blusky.pro/en/articles/12434108-billing; id 12434108; page date: Updated over 3 weeks ago
- [P17] https://help.blusky.pro/en/articles/17290897-live-brokerage-qualifying-transitioning-and-trading-a-live-account; id 17290897; page date: Updated this week
- [P18] https://help.blusky.pro/en/articles/12292284-sim-funded-payouts; id 12292284; page date: Updated over a month ago
- [P19] https://help.blusky.pro/en/articles/12434429-payouts; id 12434429; page date: Updated this week
- [P20] https://blusky.pro/terms-and-conditions/; page date: Last Modified: July 1, 2026
- [P21] https://help.blusky.pro/en/articles/11490284-blusky-trading-company-llc-dba-blusky-pro-terms-of-use; id 11490284; page date: February 1, 2026
- [P22] https://help.blusky.pro/en/articles/11760172-scaling-contract-size-in-sim-funded-brokerage-accounts; id 11760172; page date: February 1, 2026
- [P23] https://help.blusky.pro/en/articles/17115915-markets-symbols-commissions; id 17115915; page date: September 23, 2026
- [P24] https://help.blusky.pro/en/articles/15756814-orbit-v2-accounts-how-do-payouts-work; id 15756814; page date: August 12, 2026


Official domains: blusky.pro, help.blusky.pro. Read 2026-11-15.
Plan captured: Launch 50K (full terms in 'terms'); Orbit 50K also passes (EOD funded drawdown) and differs materially -- in 'terms_orbit'. Propel 50K = Launch without the $99 launch fee, 55% eval consistency and a higher subscription..
Verdict: **PASS** -- Launch/Propel Sim Funded has no consistency rule (static drawdown); Orbit Sim Funded is EOD-trailing with locking; 3 funded accounts at once; no rule forbids hand-entered bracket trading on NQ/MNQ.

Plans seen:
- Launch 50K: drawdown eval and Buffer: $2,000 EOD trailing; Sim Funded: static (starts at $3,000, minimum balance $100); consistency evaluation 50% (eval), 34% (Buffer), funded none
  - "Phase 1 - Evaluation (after this Phase Launch Fee is due) 50% Consistency Phase 2 - Buffer 34 % Consistency Phase 3 - Sim Funded No Consistency" [P1]
- Propel 50K (formerly 'Premium'): drawdown same as Launch (EOD $2,000 eval/Buffer; static Sim Funded $3,000 start / $100 floor); consistency evaluation 55% (eval), 34% (Buffer), funded none
  - "| 50K | $3,000 | $-2,000 Trailing (EOD) | None | 55% | $1,650(55%) of target)" [P2]
- Orbit 50K (one-time fee, two phases): drawdown eval $2,000 EOD trailing; Sim Funded $2,000 trailing closed daily profit, locks at starting balance after $2,000 net profit; consistency evaluation none, funded 40% (checked at payout request)
  - "A 40% consistency rule applies while Sim Funded, and payouts become available every three trading days once your balance is above the threshold in the table above." [P3]
- Instant Sim Funded 50K (no evaluation): drawdown $2,000 intraday trailing, stops at $51,000; consistency evaluation n/a, funded 21%
  - "| Drawdown | $2,500 static | $2,000 intraday trailing" [P4]
- Direct to Funded ($3,500 account, no evaluation): drawdown $2,500 static; consistency evaluation n/a, funded 21%, plus max 3 negative days per rolling 10 traded days
  - "| Consistency | 21% | 21%" [P4]

**Screen**

- `drawdown_eval` = **eod_trailing $2,000 (Evaluation and Buffer)** (verified)
  - "| 50K | $3,000 | $-2,000 Trailing (EOD) | None | 50% | $1,500 (50% of target)" [P5]
  - "The minimum trailing balance increases with your highest EOD balance. It increases with profits, but it does not decrease with losses, and is calculated from your starting balance at 6PM." [P6]
  - note: No lock of the eval/Buffer EOD trail is stated for Launch 50K (the Buffer article mentions a lock only for 'Premium' accounts and gives no balance).
- `drawdown_funded` = **static (Sim Funded opens at $3,000 with a static $100 minimum balance)** (verified)
  - "This account will have a static drawdown and allow for withdrawals, as indicated by the specified amount below." [P7]
  - "| $50K | $3,000 | $100" [P8]
  - note: Static, not EOD trailing; passes the screen through 'no funded consistency'. Header of the second quote's table: '| Account Size | Starting Balance | Static Minimum Balance'.
- `consistency_eval` = **50% Launch evaluation (55% on the homepage plan widget); 34% Buffer; checked to pass a phase** (verified)
  - "50% in Launch Plans Evaluations Account only (Buffer is still 34% to pass)" [P6]
  - ""launch": mkPlanSky({ profitGoal: 3000, evalStaticDrawdown: "$2,000 Trailing (EOD)", evalConsistency: 55," [P9]
  - note: CONFLICT: help centre (three articles) says 50% for the Launch evaluation; the homepage plan-picker data (page script) says 55% for 50K Launch. Measured as largest profitable day / sum of profitable days (losing days excluded).
- `consistency_funded` = **none (Launch/Propel Sim Funded)** (verified)
  - "Phase 3 - Sim Funded No Consistency" [P1]
  - note: The Launch article's Sim Funded table has no consistency column either. Orbit Sim Funded has 40%.
- `max_funded_accounts` = **3 funded at any time (Sim Funded, Instant Sim Funded or Direct to Funded combined); evaluations unlimited; may be cut to 1 after 3+ funded breaches** (verified)
  - "You can have any number of Evaluation Accounts of any combination. Funded accounts can only be 3 at any time (Sim Funded, Instant Sim Funded or Direct to Funded Accounts." [P10]
  - "If you breach the drawdown on 3 or more Sim Funded or Live Brokerage accounts, we may restrict you to a single active Sim Funded or Live Brokerage account at the Risk Team's discretion." [P11]
  - note: Lead's 'funded cap 3' and '3-breach clause' confirmed.
- `copy_trading` = **trade copier allowed on every plan (help-centre table); the Ethical Conduct Policy forbids 'Account Mirroring' (copying from another trader, account or signal provider)** (verified)
  - "| Launch Plan 50K | Unlimited | Yes" [P10]
  - "Account Mirroring: Copying trades from another trader, account, or signal provider, as this undermines independent trading skill development and risk management." [P12]
  - note: CONFLICT in wording: table header is '| Account Size | Max Accounts | Trade Copier Allowed' and says Yes; the conduct policy's 'account' could be read to cover copying between one's own accounts. Our design enters by hand on each account.
- `opposite_positions` = **prohibited across own/household accounts, including correlated products (ES vs NQ) and even across firms** (verified)
  - "This policy means you cannot use multiple trading accounts to offset risk by placing opposite or correlated trades across them." [P13]
  - "This means you cannot go long in one account and short in another account under you user ID and control." [P10]
- `news` = **allowed (at own risk); no news window stated for eval or Sim Funded** (verified)
  - "Trading news events at your own risk" [P6]
  - note: Listed under 'Things that DONT fail your account'. Sim Funded rules keep 'Trading restrictions when applicable'; Tradovate margin can scale contract limits down during news (article 11760172).
- `automation` = **no general prohibition of automated trading found; automated software (AI, ultra-high speed, bulk data entry) used to manipulate or unfairly influence outcomes is forbidden** (verified)
  - "This includes violating our terms and conditions, or using automated software (AI, ultra-high speed, bulk data entry) to unfairly influence outcomes." [P12]
  - note: Searched all fetched help articles, the Terms of Use, Terms and Conditions (help and site copies) and FAQ for automation/bot/algorithm: no other statement. Hand entry is unaffected.
- `sizing_gambling` = **account cycling and irresponsible funded trading prohibited; Sim Funded profit stops: $5,000/day and $10,000/week** (verified)
  - "Serial Account Depletion (Account Cycling): Aggressively trading an account to hit its Maximum Loss Limit, then repeatedly switching to new accounts to continue similar high-risk approaches." [P12]
  - "Stop trading for the day after reaching $5,000 in daily profit" [P11]
  - note: No minimum-hold or scalping rule found; nothing forbids hand-entered single-position bracket orders.

**Terms (`terms`)**

- `eval_profit_target` = **3000** (verified)
  - "| Account size | Launch fee | Profit target | Drawdown | Contracts" [P5]
  - "| 50K | $99 | $3,000 | $-2,000 Trailing (EOD) | 5 Mini / 50 Micros" [P5]
  - note: Then a second qualification stage, the Buffer Zone: another $3,000 target at 34% consistency under the same $2,000 EOD trail (no daily loss limit); that $3,000 becomes the non-withdrawable Sim Funded starting balance.
- `eval_drawdown_amount` = **2000** (verified)
  - "For example, the 50K evaluation starts with a 48K minimum balance (trailing by $2000)." [P6]
- `eval_drawdown_type` = **eod_trailing** (verified)
  - "If your balance falls to your established EOD minimum balance at any point, the evaluation has failed." [P6]
  - note: Floor set at EOD; breach checked intraday.
- `eval_drawdown_lock` = **none stated for Launch 50K** (UNVERIFIED)
  - looked at: https://help.blusky.pro/en/articles/12434059-evaluation-rules, https://help.blusky.pro/en/articles/16300846-launch-plans-phases-rules-and-costs, https://help.blusky.pro/en/articles/12434458-buffer-stage
  - note: Buffer article: 'Premium accounts: The trailing drawdown that becomes static once you reach the balance indicated in the table below.' -- but the table gives only Sim Funded transfer balances. Practically moot: the eval target ($3,000) exceeds the trail ($2,000).
- `eval_daily_loss_limit` = **none (eval and Buffer)** (verified)
  - "| Account size | Profit target | Drawdown | Daily loss limit | Consistency | Largest single day" [P5]
  - "| 50K | $3,000 | $-2,000 Trailing (EOD) | None | 50% | $1,500 (50% of target)" [P5]
- `eval_consistency_rule` = **50% eval (largest profitable day / sum of profitable days); 34% Buffer; gates passing, never a breach** (verified)
  - "We compare your largest single profitable day against the sum of your profitable days." [P5]
  - "| 50K | $3,000 | $-2,000 Trailing (EOD) | 34% | $1,020 (34% of target)" [P5]
  - "Being out of consistency does not fail your account." [P5]
  - note: CONFLICT eval 50% (help) vs 55% (homepage widget data), see screen. The Buffer row's header: '| Account size | Profit target | Drawdown | Consistency | Largest single day'.
- `eval_min_days` = **2 profitable days (implied by the 50% rule); no stated minimum-day count for Launch** (verified)
  - "Because your biggest day cannot exceed 50% of your profitable days, the target cannot be reached in fewer than 2 profitable days." [P5]
  - "Although our minimum trading days are low (2-4 depending on your account type), don't feel rushed." [P14]
  - note: Buffer at 34% implies at least 3 profitable days.
- `eval_position_limit` = **5 minis / 50 micros** (verified)
  - "| 50K | $99 | $3,000 | $-2,000 Trailing (EOD) | 5 Mini / 50 Micros" [P5]
- `eval_fee` = **$59 per 30 days (recurring during the evaluation only)** (verified)
  - "bkrgExtraInfo: "No Profit Caps /<br> No Payout Caps", price: 59, micMin: "5 Mini / 50 Micros" })," [P9]
  - "Pass it and billing stops immediately — there is nothing to cancel, and nothing at all is charged during the Buffer Zone or once you are Sim Funded." [P5]
  - note: Price from the homepage plan-picker data for '50k' -> 'launch' (page script; list prices 'as of 10/5/2026' per /find-your-plan/). Promotion: 'Welcome26 takes 50% off a new customer's first Launch account'. Renews at the price first paid; a renewal on a failed account includes a free reset.
- `eval_reset_fee` = **49 (evaluation); Buffer resets $250 x3, then +$50 per three** (verified)
  - "50K Launch Evaluation Reset Price is $49" [P15]
  - "Your first three resets are $250 each. The price then rises by $50 for every further three resets" [P15]
  - note: A failed Buffer is reset on its own; the passed evaluation stands.
- `activation_fee` = **$99 one-time Launch fee, due on passing, payable within 14 days or the passed account is forfeited** (verified)
  - "Launch plans carry a one-time Launch Fee that becomes due the moment you pass your evaluation: $99 on the 50K, $149 on the 100K and $179 on the 200K." [P16]
  - "If the fee is unpaid on the due date, the account expires immediately and the passed evaluation is forfeited." [P16]
- `eval_count_limit` = **unlimited evaluations ('Excessive Program Enrollments' without progress is a conduct issue)** (verified)
  - "You can have any number of Evaluation Accounts of any combination." [P10]
  - "Excessive Program Enrollments: Repeatedly purchasing numerous Evaluation Accounts or Resets without demonstrating genuine progress or responsible engagement." [P12]
- `eval_time_limit` = **none; 30-day billing cycle renews and an open account is carried over** (verified)
  - "You have 30 days before your subscription renews, and when that happens, we won't reset your balance if your account is still active and open." [P14]
  - note: Inactivity: accounts inactive 30 consecutive days may be closed (Terms of Use 3.3).
- `funded_type` = **sim (Sim Funded; real payouts); $10,000 total profit incl. payouts -> mandatory stop and Brokerage Review; if approved (from Oct 1, 2026): Live at $0 balance with $2,000 MLL and sim profits to a Bonus Vault, or a one-time buyout of 50% of drawdown ($1,000)** (verified)
  - "Your Sim Funded Account remains simulated. Your orders do not reach the live market until you transition into Live Brokerage." [P11]
  - "Once your total profit, including payouts, reaches $10,000, you must stop trading and request a Brokerage Review." [P11]
  - "If you're approved for Brokerage but do not want to move live, you can choose a one-time cash buyout equal to 50% of your applicable drawdown." [P11]
  - "If you have multiple active Sim Funded Accounts, this applies to all of them, and your qualifying Sim Funded activity is consolidated into one Live Brokerage account with the applicable live risk parameters and Bonus Vault." [P17]
  - note: RECENT CHANGE effective October 1, 2026 (previously sim profits up to $10,000 minus payouts seeded the live balance, max $30,000 across 3 accounts). If not approved, the Sim Funded account may continue or be closed at the Risk Team's discretion; reviews can start at $5K profit. A broker denying the brokerage application forfeits all sim profits.
- `funded_drawdown_amount` = **2900 (balance $3,000 at start, static minimum balance $100)** (verified)
  - "| Account size | Starting balance | Minimum balance | Payout minimum | 7-day payout cap" [P5]
  - "| 50K | $3,000 | $100 | $500 | $2,500" [P5]
  - "bufferConsistency: 34, startingBalance: 3000, fundedExtraInfo: "Payouts Available Daily <br> (M-F) Above Buffer", minBalance: 1000," [P9]
  - note: CONFLICT: help centre (Launch article, Sim Funded Processing article) says minimum balance $100; the homepage plan-picker data for 50K Launch says minBalance 1000 (i.e. $2,000 room). $2,900 = $3,000 - $100 is arithmetic on the help-centre figures. The older Sim Funded Payouts article frames the same as a $53,000 'minimum balance' on a $50,000 account (the $3,000 buffer is not withdrawable). If the Risk Team grants more contracts, 'we will also raise the static drawdown limit' (Buffer article).
- `funded_drawdown_type` = **static** (verified)
  - "You can withdraw profits from your account, but you must maintain the static drawdown in your account." [P8]
- `funded_drawdown_lock` = **n/a (static from the start)** (verified)
  - "| Account Size | Starting Balance | Static Minimum Balance" [P8]
- `payout_balance_consequence` = **only balance above the $3,000 starting balance is withdrawable; the static $100 floor does not move with payouts** (verified)
  - "Payouts can be requested daily, Monday to Friday, on any balance above your starting balance." [P5]
  - "Keep in mind the safety buffer (Minimum balance) is not available for withdrawal." [P18]
  - note: So after any payout the balance stays >= $3,000 with the floor at $100 (room >= $2,900).
- `funded_daily_loss_limit` = **none stated for Sim Funded (Risk Team may impose one)** (UNVERIFIED)
  - "You may set your own Daily Loss Limit where supported." [P11]
  - looked at: https://help.blusky.pro/en/articles/17297032-sim-funded-accounts-rules, https://help.blusky.pro/en/articles/16300846-launch-plans-phases-rules-and-costs, https://help.blusky.pro/en/articles/12434469-sim-funded-accounts-processing
  - note: Sim Funded rules list 'Daily loss limits' among controls the Risk Team 'may also apply'. Daily PROFIT stop of $5,000 applies.
- `funded_consistency_rule` = **none** (verified)
  - "Phase 3 - Sim Funded No Consistency" [P1]
- `funded_position_limit` = **by balance: $3,000 -> 3 minis / 30 micros (initially 1-3 minis, 15-30 micros); increases on request** (verified)
  - "| Account Balance | Minis | Micros" [P11]
  - "| $3,000 | 3 | 30" [P11]
  - "| Premium $50K | 5 minis / 50 micros" [P7]
  - note: CONFLICT: Buffer article's 'Max contracts in Sim Funded' says 5/50 for a 50K; Sim Funded rules and the contract-size article say limits scale with the (small) balance and are lower than in evaluation. Rithmic and Volumetrica do not scale; Tradovate scales by margin.
- `funded_monthly_fee` = **0** (verified)
  - "Nothing is charged during this phase. Your subscription ended at the evaluation." [P5]
  - note: Market-data fees begin only in Live Brokerage ($156 per exchange per month on Tradovate/Volumetrica).
- `payout_min` = **500** (verified)
  - "Minimum Payout - To qualify your Sim Funded for payouts, you must be above your initial starting balance by $500." [P18]
  - note: Standardised to $500 from Oct 1, 2026 (Sim Funded rules 'Minimum payout request: $500'); whole-dollar amounts.
- `payout_cap` = **$2,500 per rolling 7 days (50K); effectively ~$10,000 total profit per account before the mandatory Brokerage Review** (verified)
  - "Your 7-day payout cap is $2,500." [P11]
  - "Each payout individually frees up cap space after 7 days" [P11]
  - "If you don't open this support ticket, you won't get paid for anything over $10,000 and may lose the account." [P8]
- `payout_frequency_gate` = **daily Mon-Fri; at least $500 of new trading profit between requests; no minimum days** (verified)
  - "After submitting a payout request, you must generate at least $500 in new profit through normal trading activity before submitting your next payout request." [P11]
  - "There are NO minimum days to trade to request your first payout, you just need to be above the minimum account balance in your Sim Funded Account." [P18]
  - note: The general Payouts article (Brokerage) says 'one meaningful profitable day between payout requests'. Stop trading after a request until the funds are removed.
- `payout_split` = **90%** (verified)
  - "All payouts are now 90% Trader / 10% BluSky at all times unless changed by a Risk Team Review." [P19]
- `payout_processing_days` = **same business day if requested before 11 AM ET (else next business day); bank transfer 1-3 business days** (verified)
  - "Payouts requested before 11AM ET on trading day (excluding holidays) will be processed on the same day. Transfer times may take from 1-3 business days, depending on your bank and payout method." [P19]
  - note: Payouts must be claimed (Rise/Gusto onboarding) within 14 days or are forfeited.
- `payout_fee` = **none stated** (UNVERIFIED)
  - looked at: https://help.blusky.pro/en/articles/12434429-payouts, https://help.blusky.pro/en/articles/12292284-sim-funded-payouts, https://help.blusky.pro/en/articles/17297032-sim-funded-accounts-rules, https://help.blusky.pro/en/articles/12434108-billing
- `payout_count_limit` = **none stated beyond the rolling cap and the $10,000 review** (UNVERIFIED)
  - looked at: https://help.blusky.pro/en/articles/17297032-sim-funded-accounts-rules, https://help.blusky.pro/en/articles/12434429-payouts
- `max_accounts` = **3 funded (any combination of Sim Funded / Instant / Direct); evaluations unlimited; Live Brokerage max 2 and not alongside Sim Funded; single user/email** (verified)
  - "| Sim Funded Accounts | 3 * | Yes" [P10]
  - "Traders in the same household, must be in control of their own accounts, and must be trading on different machines." [P10]
  - "You will only create a single user under a single email address. Using multiple email addresses to sign-up to bypass max account limits or for any other reason is strictly prohibited." [P20]
  - note: Several household members may each trade (on different machines). 3-breach clause may cut a trader to 1 funded account.
- `inactivity_rule` = **accounts inactive 30 consecutive days may be closed** (verified)
  - "3.3. Abandoned Accounts: Evaluation, BluLive, SimFunded, or brokerage accounts inactive for 30 consecutive days may be closed at our discretion." [P21]
- `copy_trading_terms` = **trade copier allowed (table); conduct policy forbids 'Account Mirroring'** (verified)
  - "| Account Size | Max Accounts | Trade Copier Allowed" [P10]
  - "Account Mirroring: Copying trades from another trader, account, or signal provider" [P12]
  - note: See screen.copy_trading (conflict).
- `cross_account_hedging` = **prohibited (own and household accounts, correlated products, across firms); first offence warning/closure, forfeit of Buffer/Sim Funded payouts** (verified)
  - "This rule applies to All User and Same Household Accounts." [P13]
  - "If done in a Buffer or Sim Funded account , you may forfeit the account and any payouts." [P13]
  - "Hedging even in Sim Environment , especially in a Funded State, will close your account." [P18]
  - note: The policy also lists 'The accounts are with different prop firms' -- relevant to any cross-firm design: opposite positions across firms are forbidden (consistent with Stage 2 D-145 tier 1).
- `news_trading_terms` = **allowed at own risk** (verified)
  - "Trading news events at your own risk" [P6]
  - "Tradovate especially can scale during News events." [P22]
- `automation_terms` = **no general ban found; automated software used to unfairly influence outcomes is forbidden** (verified)
  - "Coordinated Manipulation: Engaging, individually or with others (including across multiple accounts), in trading patterns whose primary intent is to manipulate, abuse, or secure an unfair advantage on our platform." [P12]
  - note: See screen.automation.
- `sizing_or_gambling_terms` = **daily $5,000 / weekly $10,000 profit stops in Sim Funded; account cycling, misuse of funded accounts and over-limit contracts prohibited** (verified)
  - "Stop trading for the week after reaching $10,000 in weekly profit" [P11]
  - "Misuse of Funded Accounts: Operating Sim Funded and Live Brokerage Accounts or other funded programs with consistent irresponsible trading behavior." [P12]
  - "But if you find a way to use more contracts than your terms, we will liquidate and/or restart your account and/or deny brokerage entry entirely when our system detects it; Please do not exploit the system." [P6]
- `other_conduct_bearing` = **no positions within 2% of a lock limit; close before ~4:45 PM ET (auto-liquidation ~15 min before close); no trading while under review; exploitative/latency strategies, off-market fills and 'non-commercial' patterns prohibited** (verified)
  - "Price Limit Infractions: Holding positions when a product's price approaches or enters its defined lock limit (specifically within 2%)." [P12]
  - "We recommend closing all trades before 4:45PM EST; our system attempts to limit when you can trade and will auto-liquidate around 15 minutes before markets close." [P6]
  - "Trading during an active review may result in automatic account loss." [P11]
  - "Exploitative Strategies: Any method designed to take advantage of system glitches, pricing errors, or latency delays within our services." [P12]
  - note: Risk Team reviews can occur at any time (up to 7 trading days; trading and payouts paused). Nothing forbids hand-entered single-position brackets.
- `permitted_products` = **CME Group futures via Tradovate/Rithmic/Volumetrica etc., incl. NQ, MNQ, ES, MES; commissions $2/side minis, $0.50/side micros on Rithmic/Volumetrica evaluations** (verified)
  - "Tradovate lists the major E-mini and Micro index contracts such as NQ, MNQ, ES, MES, YM, MYM, RTY, and M2K." [P23]
  - "| Rithmic & Volumetrica | Evaluation | Minis: $2/side · Micros: $0.50/side | Unavailable" [P23]

**Terms (`terms_orbit`)**

- `eval_profit_target` = **3000** (verified)
  - "| Account size | Profit target | Drawdown | Contracts (evaluation) | Contracts (funded)" [P3]
  - "| 50K | $3,000 | $-2,000 Trailing (EOD) | 5 Mini / 50 Micros | 2 Mini / 20 Micros" [P3]
- `eval_drawdown` = **$2,000 EOD trailing; no daily loss limit; no consistency rule** (verified)
  - "There is no launch fee on any Orbit plan, and no daily loss limit in either phase." [P3]
  - "There is no consistency rule in the Orbit evaluation, which is what allows it to be passed in one day if your trading gets you there." [P3]
  - note: CONFLICT: the Evaluation Overview (July 31, 2026) lists an Orbit 'Phase 2 - Buffer 50% Consistency'; the Orbit article (Oct 15, 2026) says Orbit has only two phases. Taken as two phases (newer).
- `eval_fee` = **$199 one-time; evaluation valid 30 days from purchase; resets do not extend it** (verified)
  - "profitSplit: "90% to the trader", bkrgExtraInfo: "No Profit Caps / <br>No Payout Caps", price: 199," [P9]
  - "You pay once, and the evaluation is valid for 30 days from purchase." [P3]
- `eval_reset_fee` = **129** (verified)
  - "50K Orbit Evaluation Reset Price is $129" [P15]
- `funded_drawdown` = **$2,000 trailing closed daily profit (EOD), locks permanently at the $50,000 starting balance once net profit reaches $2,000** (verified)
  - "| 50K | $50,000 | $2,000 | $2,000 net profit | $52,000 | $500 | $2,000" [P3]
  - "The floor trails your closed daily profit dollar-for-dollar, and once your lifetime net profit matches your starting drawdown it locks permanently at your starting balance." [P3]
  - note: Table header: '| Account size | Starting balance | Drawdown | Locks in after | Payouts unlock above | Payout minimum | 7-day payout cap'. The Sim Funded Processing article (July 28, 2026) describes Orbit funded as a $0-start subaccount with a -$2,000 floor -- an older presentation.
- `funded_consistency_rule` = **40% (largest profitable day / sum of profitable days), checked at each payout request, resets after each approved payout** (verified)
  - "When your account is above its mandatory withdrawal threshold, you can request a payout as long as you are aligned with the 40% consistency rule." [P24]
- `funded_position_limit` = **2 minis / 20 micros** (verified)
  - "sfaContract: "2 Mini / 20 Micros", minPayout: "$500", maxPayout: "$2,000", payoutsUnlocked: "$52,000"" [P9]
- `payout_terms` = **min $500; payouts above $52,000; $2,000 per rolling 7 days; every 3 trading days (Orbit article) vs daily (Orbit payouts article); profit ceiling $10,000 then review; 90% split** (verified)
  - "Daily Flexibility: You can request daily withdrawals starting at a minimum of $500." [P24]
  - "| 50K | $10,000" [P17]
  - note: CONFLICT on frequency: Orbit plan article (Oct 15, 2026) 'payouts every three trading days'; Orbit V2 payouts article (Aug 12, 2026) 'daily withdrawals'. The ceiling row's header: '| Orbit Account | Profit Ceiling'. Sim Funded reset (before any payout) $599 on 50K Orbit.

### Earn2Trade (`e2t`) -- PASS

**Pages quoted** (key: URL; article id; the page's own date as shown; all read 2026-11-15)

- [P1] https://www.earn2trade.com/gauntlet-mini
- [P2] https://help.earn2trade.com/en/articles/6863807-what-is-the-difference-between-the-tcp25-tcp50-and-tcp100; id 6863807; page date: October 17, 2025
- [P3] https://help.earn2trade.com/en/articles/5372687-how-does-end-of-day-drawdown-work; id 5372687; page date: February 1, 2022
- [P4] https://help.earn2trade.com/en/articles/6877364-what-happens-when-i-complete-my-evaluation; id 6877364; page date: Updated over 2 weeks ago
- [P5] https://help.earn2trade.com/en/articles/3849975-what-is-the-maintain-consistency-rule; id 3849975; page date: Updated over a week ago
- [P6] https://help.earn2trade.com/en/articles/5660666-can-i-have-multiple-trader-career-path-gauntlet-mini-and-live-livesim-accounts; id 5660666; page date: June 22, 2026
- [P7] https://help.earn2trade.com/en/articles/12034590-am-i-allowed-to-copy-trades-across-multiple-accounts; id 12034590; page date: Updated over 3 weeks ago
- [P8] https://help.earn2trade.com/en/articles/3224526-are-there-any-restrictions-on-when-i-can-trade-in-my-evaluation-account; id 3224526; page date: November 13, 2025
- [P9] https://help.earn2trade.com/en/articles/9286647-prohibited-conduct-in-earn2trade-evaluations-and-in-the-livesim-live-trading-environment; id 9286647; page date: May 6, 2024
- [P10] https://help.earn2trade.com/en/articles/3395926-how-is-my-daily-loss-calculated; id 3395926; page date: August 27, 2024
- [P11] https://help.earn2trade.com/en/articles/5941958-what-are-the-evaluation-rules; id 5941958; page date: Updated this week
- [P12] https://help.earn2trade.com/en/articles/17779875-how-many-contracts-can-i-trade-on-my-evaluation-or-livesim-live-account; id 17779875; page date: Updated over 2 weeks ago
- [P13] https://help.earn2trade.com/en/articles/11183609-reset-pricing-for-earn2trade-accounts; id 11183609; page date: May 8, 2025
- [P14] https://help.earn2trade.com/en/articles/5452472-what-is-the-withdrawal-policy; id 5452472; page date: Updated over 2 weeks ago
- [P15] https://help.earn2trade.com/en/articles/3313030-what-is-the-livesim; id 3313030; page date: January 6, 2026
- [P16] https://help.earn2trade.com/en/articles/8117088-drawdown-types; id 8117088; page date: August 10, 2026
- [P17] https://help.earn2trade.com/en/articles/8320643-fee-schedule-in-e2t-evaluations-and-on-funded-accounts; id 8320643; page date: May 7, 2026
- [P18] https://www.earn2trade.com/terms-and-conditions
- [P19] https://help.earn2trade.com/en/articles/3320460-what-assets-can-i-trade; id 3320460; page date: September 15, 2023


Official domains: earn2trade.com, help.earn2trade.com. Read 2026-11-15.
Plan captured: Gauntlet Mini 50K (GAU50) -> LiveSim (funded sim).
Verdict: **PASS** -- LiveSim funded account has an EOD drawdown and no consistency rule, 3 funded accounts allowed, news allowed; hand entry is allowed but copiers/batch execution across accounts are banned, so each account's bracket must be entered separately.

Plans seen:
- Gauntlet Mini 50K (GAU50): drawdown eval EOD $2,000; LiveSim EOD $2,000; Live intraday trailing $2,000; all stop at starting balance; consistency evaluation 30%, funded none
  - "Virtual Starting Balance $50,000 Profit Goal $3,000 EOD Drawdown $2,000 Daily Loss Limit $1,100 Contract Limit 4 Maintain Consistency 30%" [P1]
- Trader Career Path TCP50 (growth plan to $100K/$200K/$400K): drawdown eval EOD; LiveSim EOD; Live trailing; $400K fixed; consistency evaluation 30%, funded none
  - "The TCP50 starts with a $50,000 account, and funded traders can grow their accounts to $100,000, $200,000, and $400,000 by achieving the profit goal at each step and withdrawing their profit share." [P2]

**Screen**

- `drawdown_eval` = **eod_trailing** (verified)
  - "The Trader Career Path and Gauntlet Mini™ evaluations calculate drawdown based on the end of the day balance of the trading account." [P3]
  - note: Open equity counts against the floor intraday.
- `drawdown_funded` = **LiveSim: eod_trailing; Live: intraday trailing** (verified)
  - "Drawdown: Funded accounts are subject to drawdown rules. LiveSim® accounts use End of Day (EOD) Drawdown. Live accounts use Trailing Drawdown." [P4]
- `consistency_eval` = **30% (no day > 30% of total profits; breach extends, no fail)** (verified)
  - "The "Maintain Consistency" rule states that over the course of your examination, no single trading day can exceed 30% of your total profits." [P5]
- `consistency_funded` = **none** (verified)
  - "The Maintain Consistency rule does not apply on the LiveSim® and/or Live accounts." [P5]
  - "No Consistency Requirement: There is no consistency rule on funded accounts." [P4]
- `max_funded_accounts` = **3 funded at once (3 LiveSim, or 2 LiveSim + 1 Live); 5 evaluations** (verified)
  - "Traders can have 3 funded trading accounts active concurrently. You can have 3 livesims, or 2 livesims and 1 live account." [P6]
  - "We suggest only trading a single account for the best results and to avoid concentration issues." [P6]
  - note: Household rule not stated on pages read.
- `copy_trading` = **forbidden on all programs, incl. batch execution across accounts** (verified)
  - "To preserve the integrity and realistic nature of the trading experience, copy-trading and batch execution across multiple accounts is not permitted." [P7]
  - note: Our trades are hand-entered, but entering the same bracket on 3 accounts at once may be read as 'batch execution'; trades must be entered per account. Consequence differs: Terms say only one account is kept; help says accounts or withdrawals may be denied.
- `opposite_positions` = **prohibited** (verified)
  - "Hedging between your funded trading accounts is strictly forbidden and your account access will be terminated if you engage in similar behavior." [P6]
- `news` = **allowed (eval and funded)** (verified)
  - "You are allowed to trade during news events — there are no restrictions on trading around economic announcements." [P8]
- `automation` = **no explicit bot/algo ban found; software/AI/ultra-fast entry that manipulates or gives unfair advantage is prohibited** (verified)
  - "Utilizing software, artificial intelligence, or ultra-fast data entry techniques that could potentially manipulate the trading environment or provide an unfair advantage;" [P9]
  - looked at: help.earn2trade.com collections Evaluation, Rules, Funding, General, Billing, Platform: no automation/bot article
  - note: Hand entry unaffected.
- `sizing_gambling` = **gambling-like actions and an unrealistic number of contracts per day prohibited; contract caps enforced by the system for evaluations bought on/after 2026-11-02** (verified)
  - "Executing an unrealistic number of contracts in a single day;" [P9]
  - "Prohibited conduct is enforced to discourage gambling-like actions, prevent rule evasion, and avoid unrealistic order executions." [P9]

**Terms (`terms`)**

- `eval_profit_target` = **3000** (verified)
  - "Profit Goal $3,000 EOD Drawdown $2,000" [P1]
  - note: Effectively raised when best day > 30%.
- `eval_drawdown_amount` = **2000** (verified)
  - "EOD Drawdown $2,000 Daily Loss Limit $1,100" [P1]
- `eval_drawdown_type` = **eod_trailing (open equity counts intraday)** (verified)
  - "Traders must be aware that open equity losses are taken into consideration when calculating whether or not the account failed on this rule." [P3]
- `eval_drawdown_lock` = **stops rising at the starting balance** (verified)
  - "This continues until your Maximum Drawdown reaches the starting balance of your account, or in this case, $100,000, at which point it will no longer rise." [P3]
- `eval_daily_loss_limit` = **1100 (hard fail: PnL incl. open trades and commissions, 5pm-5pm CT)** (verified)
  - "Daily Loss Limit $1,100 Contract Limit 4" [P1]
  - "Daily loss is based on your Profit & Loss, including both open (real-time/unrealized), closed trades and commissions. It’s calculated daily from 5:00 pm to 5:00 pm (Central Time)." [P10]
- `eval_consistency_rule` = **30%** (verified)
  - "Maintain Consistency 30%" [P1]
- `eval_min_days` = **none (consistency implies at least 4 profitable days)** (verified)
  - "There is no minimum number of trading days required to pass. However, due to the 30% consistency rule, a trader will need at least four profitable trading days to complete an evaluation." [P11]
- `eval_position_limit` = **4 standard / 40 micro (fixed, system-enforced for evaluations bought on/after 2026-11-02; legacy Progression Ladder before)** (verified)
  - "| $50,000 | 4 | 40" [P12]
  - "This is a legacy rule that only applies to evaluations, LiveSim and Live accounts purchased before Nov 2, 2026. Evaluations, LiveSims and Live accounts following subscriptions purchased after November 2, 2026 have a fixed maximum number of contracts." [P11]
  - note: Recent rule change dated 2026-11-02.
- `eval_fee` = **$170 per month (recurring every 30 days until pass/cancel); 50% promo for first 60 days under code NEXTSTEP50 until 2026-11-26** (verified)
  - "Begin your GAU50 evaluation today — starting at $170/mo" [P1]
  - "Evaluations are subscription-based and renew automatically every 30 days until you pass or cancel your subscription." [P1]
  - note: Monthly subscription, not one-time.
- `eval_reset_fee` = **dynamic, always below a new subscription; $75 under the current promotion** (verified)
  - "Reset prices for these smaller accounts adjust based on active promotions and are always set below the current price of a new subscription:" [P13]
  - "GAU50 resets – <strike>$100</strike> <strong>$75</strong>" [P1]
  - note: Free reset at each rebill is stated for TCP only.
- `activation_fee` = **$139 one-time per LiveSim account (non-professional), deducted from the first withdrawal only; Live has none (pays data fees)** (verified)
  - "The one-time activation fee of $139 applies to LiveSim accounts and is deducted only from your first successful withdrawal." [P1]
- `eval_count_limit` = **5** (verified)
  - "Yes, you can have up to five evaluation accounts concurrently." [P6]
- `eval_time_limit` = **none while the subscription is active** (verified)
  - "There is no time limit on The Gauntlet Mini™ evaluation. You can take as long as you need to reach the profit goal, as long as you maintain an active subscription." [P1]
- `funded_type` = **LiveSim (simulated) or Live (real capital) offered by a partner prop firm; LiveSim moves to Live automatically after $5,000 total withdrawn (GM 50)** (verified)
  - "*LiveSim Max Withdrawal is the total you can withdraw from a LiveSim account before you are automatically moved to a Live account. It is not a limit on any single withdrawal." [P14]
  - "| GM 50 | Under $2,250 | $2,250+ | $5,000" [P14]
  - "While LiveSim® is offered as an option, the proprietary trading firms, depending on your performance, may decide to provide a Live account instead of a LiveSim®." [P15]
  - note: Only 1 Live account at a time; Live uses intraday trailing drawdown and $140/month per exchange data.
- `funded_drawdown_amount` = **2000** (verified)
  - "Trade with simulated capital using real-time market data. LiveSim®Live Starting Balance $50,000 EOD Drawdown $2,000" [P1]
- `funded_drawdown_type` = **eod_trailing (LiveSim)** (verified)
  - "This drawdown type applies to evaluation accounts and LiveSim® accounts." [P16]
- `funded_drawdown_lock` = **rises until it reaches the starting balance** (verified)
  - "It adjusts upwards as your profit increases until the maximum drawdown reaches the starting balance." [P16]
- `payout_balance_consequence` = **not stated** (UNVERIFIED)
  - looked at: https://help.earn2trade.com/en/articles/5452472-what-is-the-withdrawal-policy, 5372687, 8117088, 6877364
  - note: No page states where the floor sits after a withdrawal.
- `funded_daily_loss_limit` = **1100** (verified)
  - "EOD Drawdown $2,000 Daily Loss Limit $1,100 Contract Limit 4 Profitable Trading Days 5" [P1]
  - "Daily Loss Limit: Funded accounts have a daily loss limit that must not be breached." [P4]
  - note: First quote is the LiveSim card on /gauntlet-mini (the 'EOD Drawdown ... Profitable Trading Days' sequence occurs only on the LiveSim card). Hard vs soft breach on funded not stated beyond 'must not be breached'.
- `funded_consistency_rule` = **none** (verified)
  - "Traders may withdraw regardless of how their profits are distributed across trading days." [P4]
- `funded_position_limit` = **4 standard / 40 micro (no scaling for GAU)** (verified)
  - "These limits apply to Trader Career Path® and The Gauntlet Mini™ evaluation, LiveSim® and Live accounts, according to account size." [P12]
- `funded_monthly_fee` = **none for non-professional LiveSim; Live: $140/month per exchange (Rithmic), $156 (NinjaTrader)** (verified)
  - "On a Live Account: Data fee cost is $140.00/month per exchange for Rithmic users, and $156.00/month per exchange for NinjaTrader Live account holders." [P17]
- `payout_min` = **100** (verified)
  - "The minimum net withdrawal amount is $100." [P14]
- `payout_cap` = **no per-request cap stated; LiveSim lifetime $5,000 before move to Live (GM 50)** (verified)
  - "| GM 50 | Under $2,250 | $2,250+ | $5,000" [P14]
- `payout_frequency_gate` = **5 new profitable days of >= $150 (GM 50, non-consecutive) before every withdrawal; weekly** (verified)
  - "Before every withdrawal: Traders must complete 5 new qualifying profitable trading days before submitting each withdrawal request. Profitable trading days counted toward a previous withdrawal cannot be reused." [P14]
  - "| GM 50 | $150" [P14]
  - note: A profitable day counts even if the balance is below start.
- `payout_split` = **50% for a withdrawal under $2,250, 80% for $2,250+ (per single withdrawal, GM 50)** (verified)
  - "The profit split depends on withdrawal size, is not based on accumulated profit, it is based on the single withdrawal size." [P14]
- `payout_processing_days` = **weekly on Wednesdays; request by 2:00 PM CT the preceding Friday** (verified)
  - "Withdrawals are processed weekly on Wednesdays via Rise or other platforms. Requests must be emailed to the proprietary firm by 2:00 PM CT on the preceding Friday." [P14]
- `payout_fee` = **Rise: $50 per withdrawal non-US, 1.5% US; Deel $50; direct crypto 0.735%** (verified)
  - "| Rise | $50 per withdrawal for non-US customers" [P14]
  - "| | 1.5% for US customers" [P14]
  - note: Plus $139 activation from the first withdrawal.
- `payout_count_limit` = **no count limit; LiveSim ends at $5,000 total withdrawn (then Live)** (verified)
  - "*LiveSim Max Withdrawal is the total you can withdraw from a LiveSim account before you are automatically moved to a Live account." [P14]
- `max_accounts` = **5 evaluations; 3 funded (max 1 Live)** (verified)
  - "Account Limits: Users can have a maximum of 3 funded accounts at any one time, of which up to 3 can be LiveSim®, but only 1 can be Live." [P4]
- `inactivity_rule` = **subscriber account dormant > 120 days is disabled (reactivatable on request); no funded-account inactivity rule found** (verified)
  - "If the account remains dormant for a period of over 120 days, it will be disabled, and can be reactivated by the subscriber upon correspondence requesting to do so." [P18]
- `copy_trading_terms` = **forbidden on evaluation and funded accounts** (verified)
  - "The use of trade copiers is not allowed on any of our programs." [P7]
  - "If you pass the exam and are found to have used trade copiers to pass your accounts, you will receive only one account (LiveSim® or Live Account)." [P18]
  - note: Terms (one account kept) vs help (accounts or withdrawals may be denied): consequence differs.
- `cross_account_hedging` = **prohibited** (verified)
  - "Collaborating to manipulate or abuse the trading environment, which may include trading between connected accounts, multiple accounts across different parties, or executing trades that hedge or pool risks among unrelated accounts;" [P9]
- `news_trading_terms` = **allowed** (verified)
  - "News Trading Permitted: Users are permitted to trade during news events on funded accounts." [P4]
- `automation_terms` = **no explicit ban; manipulative software/AI/ultra-fast entry prohibited** (verified)
  - "Utilizing software, artificial intelligence, or ultra-fast data entry techniques that could potentially manipulate the trading environment or provide an unfair advantage;" [P18]
- `sizing_or_gambling_terms` = **unrealistic daily contract counts and gambling-like actions prohibited** (verified)
  - "Executing an unrealistic number of contracts in a single day;" [P18]
- `other_conduct_bearing` = **flat 3:50-5:00 PM CT, no overnight; no trading on behalf of others; legal name only** (verified)
  - "Trading Hours: All positions and working orders must be closed between 3:50 PM CT and 5:00 PM CT. No overnight positions are permitted." [P4]
- `permitted_products` = **CME/CBOT/NYMEX/COMEX futures incl. micros (MNQ counted as micro); no BTC/ETH futures** (verified)
  - "All CME (CME, CBOT, NYMEX, COMEX) Futures assets can be traded. This includes the Micros." [P19]
  - "*Only MES, MNQ, MYM, M2K, MGC, MCL, M6B, M6E, and MHG are considered micros and can be traded as stated above." [P12]

### FundedNext Futures (`fundednext`) -- PASS

Verdict: **PASS** -- Flex 50K: EOD trailing MLL on the funded account and no funded consistency rule; 5 funded accounts per person/household; hand-entered one-direction bracket trades are not prohibited (only tight two-sided no-slippage bracket straddles, micro-scalping and tick scalping are).

Struck (E-020): the firm's own terms forbid automated retrieval -- Terms of Service 13.3(c): "The User is expressly prohibited, directly or indirectly, in whole or in part, without the Provider's prior written authorisation, from: ... (c) engaging in scraping, crawling, harvesting, data mining or using robots, scripts or automated systems to access the Website/Services, extract data" (as recorded in config/rules_extended.yaml, fundednext.automated_retrieval_terms). Removed on 2026-11-16 (Q-34): the firm's saved pages, the terms and quotes its file held, and this section; its plans are read, if ever, only through the operator's browser or with the firm's written permission.

### TradeDay (`tradeday`) -- PASS

**Pages quoted** (key: URL; article id; the page's own date as shown; all read 2026-11-15)

- [P1] https://www.tradeday.com/
- [P2] https://tradeday.freshdesk.com/en/support/solutions/articles/103000008855-what-is-the-maximum-drawdown-rule-; id 103000008855; page date: Modified on Sun, 31 May at 11:07 AM
- [P3] https://tradeday.freshdesk.com/en/support/solutions/articles/103000008889-what-are-the-rules-for-funded-funded-sim-and-funded-live-traders-; id 103000008889; page date: Modified on Sun, 31 May at 12:48 PM
- [P4] https://tradeday.freshdesk.com/en/support/solutions/articles/103000008849-what-is-the-consistency-objective-; id 103000008849; page date: Modified on Tue, 28 Jul at 3:36 PM
- [P5] https://tradeday.freshdesk.com/en/support/solutions/articles/103000405228-what-is-quick-pay-; id 103000405228; page date: Modified on Thu, 12 Nov at 4:48 AM
- [P6] https://tradeday.freshdesk.com/en/support/solutions/articles/103000404096-fast-pass-funded-sim-payout-policy; id 103000404096; page date: Modified on Tue, 8 Sep at 9:01 AM
- [P7] https://tradeday.freshdesk.com/en/support/solutions/articles/103000008833-can-i-have-multiple-accounts-can-i-use-copy-trader-; id 103000008833; page date: Modified on Tue, 22 Sep at 9:26 AM
- [P8] https://tradeday.freshdesk.com/en/support/solutions/articles/103000354796-multiple-accounts; id 103000354796; page date: Modified on Tue, 8 Sep at 5:44 AM
- [P9] https://tradeday.freshdesk.com/en/support/solutions/articles/103000081072-can-i-trade-news-or-data-releases-; id 103000081072; page date: Modified on Sat, 22 Feb, 2025 at 8:49 AM
- [P10] https://tradeday.freshdesk.com/en/support/solutions/articles/103000085101-automated-algo-and-bot-trading; id 103000085101; page date: Modified on Fri, 28 Nov, 2025 at 9:41 AM
- [P11] https://tradeday.freshdesk.com/en/support/solutions/articles/103000008883-will-tradeday-evaluate-and-fund-scalpers-; id 103000008883; page date: Modified on Fri, 3 Jan, 2025 at 3:56 PM
- [P12] https://tradeday.freshdesk.com/en/support/solutions/articles/103000121031-prohibited-trade-practices; id 103000121031; page date: Modified on Tue, 10 Jun, 2025 at 7:30 AM
- [P13] https://tradeday.freshdesk.com/en/support/solutions/articles/103000304248-what-are-the-differences-between-each-account-size-; id 103000304248; page date: Modified on Tue, 1 Sep at 6:47 AM
- [P14] https://tradeday.freshdesk.com/en/support/solutions/articles/103000008847-what-are-the-objectives-and-rules-of-the-quick-pay-and-fast-pass-evaluation-; id 103000008847; page date: Modified on Thu, 12 Nov at 4:47 AM
- [P15] https://tradeday.freshdesk.com/en/support/solutions/articles/103000250682-funded-accounts-withdrawals-and-the-impact-of-drawdowns; id 103000250682; page date: Modified on Sun, 31 May at 1:58 PM
- [P16] https://tradeday.freshdesk.com/en/support/solutions/articles/103000008850-what-is-the-trade-for-a-minimum-number-of-days-objective-; id 103000008850; page date: Modified on Mon, 1 Jun at 7:43 AM
- [P17] https://www.tradeday.com/terms-and-conditions; page date: Last Modified: August 11, 2026
- [P18] https://tradeday.freshdesk.com/en/support/solutions/articles/103000008894-are-there-any-fees-when-i-am-funded-; id 103000008894; page date: Modified on Sun, 31 May at 11:08 AM
- [P19] https://tradeday.freshdesk.com/en/support/solutions/articles/103000180686-what-is-a-funded-sim-account-and-what-is-a-funded-live-account-; id 103000180686; page date: Modified on Sun, 31 May at 11:08 AM
- [P20] https://tradeday.freshdesk.com/en/support/solutions/articles/103000262630-how-do-i-request-a-payout-withdrawal-and-how-long-does-it-take-; id 103000262630; page date: Modified on Wed, 11 Jun, 2025 at 7:19 PM
- [P21] https://tradeday.freshdesk.com/en/support/solutions/articles/103000335937-quick-pay-funded-sim-payout-policy; id 103000335937; page date: Modified on Wed, 22 Jul at 2:21 PM
- [P22] https://tradeday.freshdesk.com/en/support/solutions/articles/103000008899-are-there-any-inactivity-fees-or-minimum-trading-requirements-; id 103000008899; page date: Modified on Wed, 30 Sep at 6:48 AM
- [P23] https://tradeday.freshdesk.com/en/support/solutions/articles/103000018874-what-is-the-permitted-trading-times-guideline-; id 103000018874; page date: Modified on Mon, 27 Apr at 3:42 PM
- [P24] https://tradeday.freshdesk.com/en/support/solutions/articles/103000008862-what-are-the-permitted-products-guidelines-; id 103000008862; page date: Modified on Tue, 6 Oct at 10:21 AM
- [P25] https://tradeday.freshdesk.com/en/support/solutions/articles/103000008825-what-products-can-i-trade-; id 103000008825; page date: Modified on Sat, 22 Feb, 2025 at 11:14 AM
- [P26] https://tradeday.freshdesk.com/en/support/solutions/articles/103000353468-quick-pay-funded-sim-path-to-live-trading; id 103000353468; page date: Modified on Mon, 31 Aug at 10:54 AM


Official domains: tradeday.com, tradeday.freshdesk.com. Read 2026-11-15.
Plan captured: Fast Pass End of Day 50K (terms_fast_pass_50k) and Quick Pay End of Day 50K (terms_quick_pay_eod_50k): both pass and differ materially (EOD funded drawdown + 45% funded consistency vs intraday funded drawdown + no funded consistency).
Verdict: **PASS** -- Fast Pass has an EOD funded drawdown and Quick Pay has no funded consistency rule; 5 active Funded Sim accounts allowed; hand-entered bracket trading is not barred (tier-1 news flat window, no hedging, no seconds-scalping).

Plans seen:
- Quick Pay Intraday 50K: drawdown intraday trailing $2,000 (eval and funded), trails to starting balance then freezes; consistency evaluation 30%, funded none
  - "Intraday 50k $ 124 $ 49 one-time fee - Profit Target $3,000 - Trailing Max Drawdown $2,000 (calculated Intraday) - Position Limits - 5 Contracts (50 Micros) - Consistency 30% - Min Trading Days 5" [P1]
- Quick Pay End of Day 50K (intraday funded drawdown): drawdown eval EOD trailing $2,000; funded Sim intraday trailing $2,000 based on gross profits; consistency evaluation 30%, funded none
  - "End of Day (Intraday Funded Drawdown) 50k $ 174 $ 69 one-time fee - Profit Target $3,000 - Trailing Max Drawdown $2,000 (calculated End of Day) - Position Limits - 5 Contracts (50 Micros) - Consistency 30% - Min Trading Days 5" [P1]
- Fast Pass End of Day 50K: drawdown EOD trailing $2,000 eval and funded; moves to starting balance at first payout and stays; consistency evaluation 45%, funded 45% (accounts opened on/after 2026-07-26)
  - "End of Day 50k $ 248 $ 99 one-time fee - Profit Target $3,000 - Trailing Max Drawdown $2,000 (calculated End of Day) - Position Limits - 5 Contracts (50 Micros) - Consistency 45% - Min Trading Days 3" [P1]

**Screen**

- `drawdown_eval` = **eod_trailing on Fast Pass and on Quick Pay End of Day; intraday trailing on Quick Pay Intraday** (verified)
  - "TradeDay has two types of Maximum Drawdown limits. An End-of-Day (EOD) limit is calculated from the end-of-day balance, and an Intraday Limit is calculated from unrealized balances within the day." [P2]
  - "Trailing max drawdown limits continues to trail your account growth until they reach the starting account balance." [P2]
  - note: Article 103000008847 says of Fast Pass 'All drawdowns are calculated at the End-of-Day.'
- `drawdown_funded` = **Fast Pass Funded Sim: eod_trailing; Quick Pay Funded Sim: intraday trailing regardless of evaluation type** (verified)
  - "All Fast Pass Funded Sim accounts are set up with End of Day (EOD) Drawdowns." [P3]
  - "All Quick Pay Funded Sim accounts will have an intraday drawdown, regardless of the drawdown had on the evaluation." [P3]
- `consistency_eval` = **Quick Pay 30%, Fast Pass 45% (best day vs total profit; breach raises the target, no fail)** (verified)
  - "The consistency percentage for FastPass accounts is 45%." [P4]
  - "The consistency percentage for QuickPay accounts is 30%." [P4]
  - "If you have a profitable day in excess of the consistency percentage of your profit target you do not fail the evaluation (but your profit target does increase)." [P4]
- `consistency_funded` = **Quick Pay Funded Sim: none; Fast Pass Funded Sim: 45% of gross profits gates each payout (accounts opened on/after 2026-07-26), none for earlier accounts** (verified)
  - "Once you pass, you move into a Funded Sim account with an intraday drawdown, regardless of the drawdown had on the evaluation. There are no milestones, no consistency requirement, and no payout buffer." [P5]
  - "For accounts opened on and after July 26 2026, accounts must satisfy the consistency objective: no single day can make up more than 45% of your total gross profits (gross profits being current profits + payouts)" [P6]
  - note: Recent rule change: Fast Pass funded consistency and lower payout caps apply to accounts opened on/after 2026-07-26.
- `max_funded_accounts` = **10 accounts total; max 5 active Funded Sim (more queue) and 5 Funded Live; one username, one user per household; all accounts on one broker** (verified)
  - "The 10 accounts can be any mix of accounts types, with a max of 10 evaluation accounts, 5 Funded Sim accounts and 5 Funded live accounts" [P7]
  - "The maximum number of active Funded Sim accounts is 5 (If a trader passes 10 evaluations, 5 will be queued, while the other 5 will be active)." [P8]
  - "A trader can only have one username, and we only allow 1 user per household." [P7]
  - note: Funded Live and Eval/Funded Sim positions may not be open at the same time.
- `copy_trading` = **allowed across Evaluation + Funded Sim (2-10 accounts) and across up to 5 Funded Live; not between Live and Sim/Eval** (verified)
  - "Evaluation & Funded Sim: You may copy trade any combination of Evaluation and Funded Sim accounts, with 2 to 10 accounts total." [P7]
- `opposite_positions` = **prohibited (hedging long in one account and short in another, same product)** (verified)
  - "Hedging is prohibited at TradeDay (the practice of simultaneously going long in one account and short in another account for the same product). Users caught hedging will be offboarded and suspended, and will forfeit all profits in funded accounts." [P8]
- `news` = **tier-1 releases banned: auto-liquidation 2 min before to 2 min after (FOMC, CPI, NFP for all products); profits from tier-1 trading not returned** (verified)
  - "TradeDay will auto-liquidate all open positions 2 minutes before TradeDay's tier 1 economic data releases, and open markets back up to trade 2 minutes after these releases." [P9]
- `automation` = **third-party bots/ATS forbidden; own ATS only via supported platforms; no API access; >200 trades/day banned** (verified)
  - "Algos and Bots purchased from a third party and employed by the trader are forbidden." [P10]
  - "We do not make platform APIs available to traders." [P10]
  - note: Hand entry unaffected.
- `sizing_gambling` = **no max-size ban beyond position limits; scalping in seconds for a couple of ticks and >200 trades/day prohibited; bracketing data releases prohibited** (verified)
  - "Strategies that trade in a few seconds, designed to capture just a couple of ticks at a time." [P11]
  - "Continued exploiting the lack of slippage in the sim environment to achieve unrealistic stop-loss execution, such as bracketing data releases." [P12]
  - note: A one-position bracket held beyond seconds and not around tier-1 releases is not barred.

**Terms (`terms_fast_pass_50k`)**

- `eval_profit_target` = **3000** (verified)
  - "End of Day 50k $ 248 $ 99 one-time fee - Profit Target $3,000" [P1]
  - note: Raised if best day exceeds 45% (target = best day / 45%).
- `eval_drawdown_amount` = **2000** (verified)
  - "| Maximum Drawdown | $1,000 | $2,000 | $3,000 | $4,500" [P13]
  - note: Fast Pass table; columns 25K/50K/100K/150K.
- `eval_drawdown_type` = **eod_trailing (enforced intraday against equity)** (verified)
  - "All drawdowns are calculated at the End-of-Day." [P14]
  - "Important: Even though the max drawdown only moves up at day’s end, you must never let your equity fall below the active drawdown level at any point during the day, doing so will still trigger auto-liquidation." [P2]
- `eval_drawdown_lock` = **trails until it reaches the starting balance, then freezes** (verified)
  - "For evaluations and Funded Sims, the Trailing Max Drawdown will trail until they reach the starting account balance, at which time the trailing drawdown will freeze and no longer trail." [P15]
- `eval_daily_loss_limit` = **none stated (only rule is the max drawdown)** (verified)
  - "TradeDay has just one rule - Don't break the Maximum Drawdown Limit!" [P14]
- `eval_consistency_rule` = **45% (no day > 45% of total profits; breach raises target, no fail)** (verified)
  - "Objective 3: Be consistent in your profitability. No day greater than 45% of your total profits." [P14]
- `eval_min_days` = **3** (verified)
  - "For FastPass accounts the minimum number of trading days is 3." [P16]
  - "pass in 3 days with no minimum trading day requirement" [P1]
  - "reach profit targets set for you over a minimum 7-day period" [P17]
  - note: Conflict: help centre and plan card say 3 minimum days; the home FAQ says 'no minimum trading day requirement'; the Terms say a minimum 7-day period. Help centre value taken.
- `eval_position_limit` = **5 contracts / 50 micros** (verified)
  - "| Contracts/Micros | 2/20 | 5/50 | 10/50 | 15/50" [P13]
  - note: Accidental breaches not failed; micro cap 50 lots.
- `eval_fee` = **one-time; $99 on the sale card (list $248) vs $180 in the help-centre table** (verified)
  - "End of Day 50k $ 248 $ 99 one-time fee" [P1]
  - "| Price | $130 | $180 | $320 | $480" [P13]
  - note: Conflict: home card (SALE60, 60% off) list $248 / $99 vs help table $180 (Sep 2026). Home card value is current.
- `eval_reset_fee` = **99** (verified)
  - "the cost of a reset is $99" [P17]
  - note: Terms text; help article 103000008876 says buy another account after a fail.
- `activation_fee` = **none** (verified)
  - "TradeDay no longer has an activation fee. There will be no charge to activate your funded account!" [P18]
  - note: Onboarding article 103000008887 still lists 'Step 1: Pay The Activation Fee' (done automatically).
- `eval_count_limit` = **10 evaluations (within 10 accounts total)** (verified)
  - "A trader can trade up to 10 accounts total." [P7]
- `eval_time_limit` = **none** (verified)
  - "There is no upper time limit" [P16]
  - note: Tradovate archives accounts not logged into for a month.
- `funded_type` = **Funded Sim (simulated, paid from sim profits); moved to a new Funded Live account (90/10, $0 balance, same EOD drawdown) at the 5th payout request** (verified)
  - "You are placed in a simulation account and paid from the simulated profits you make in the account." [P19]
  - "On the 5th payout request the account will be moved from Funded Sim to a new Funded Live account" [P15]
  - "The Funded Live account will start with $0 balance." [P15]
  - note: Live requires $156/month per exchange pro data; losing Live = 3-month cooling-off.
- `funded_drawdown_amount` = **2000** (verified)
  - "Trailing Max Drawdown: $2,000 (calculated EOD)" [P1]
- `funded_drawdown_type` = **eod_trailing** (verified)
  - "All Fast Pass Funded Sim accounts are set up with End of Day (EOD) Drawdowns." [P3]
- `funded_drawdown_lock` = **trails to starting balance then freezes; at the first payout request it jumps to the starting balance and stays** (verified)
  - "On the first payout request, if the Trailing Maximum Drawdown (TMD) has not yet reached the starting account balance, it will automatically move up to the starting account balance and remain fixed there moving forward." [P6]
- `payout_balance_consequence` = **floor fixed at the starting balance from the first payout; balance after payout becomes the new starting point for profitability checks** (verified)
  - "This becomes your new starting balance for future profitability and payout trigger completion." [P6]
  - note: The worked example uses 'balance' to mean profit above $50K.
- `funded_daily_loss_limit` = **none stated** (verified)
  - "Rule 1: Do not hit or exceed the maximum drawdown." [P3]
  - note: Funded rules list only the max drawdown and the 2%-of-price-limit rule.
- `funded_consistency_rule` = **45% of gross profits (current + paid out) per payout, accounts opened on/after 2026-07-26; none before** (verified)
  - "For accounts opened before July 26 2026, there is no consistency objective in the Funded Sim account." [P6]
- `funded_position_limit` = **2 contracts (20 micros), +1 contract per $2k profit at EOD (scaling)** (verified)
  - "Position Limit: 2 contracts (or 20 Micros), scales +1 contract per $2k profit at EOD" [P1]
  - note: No maximum stated for the 50K card (25K card says max 2 minis).
- `funded_monthly_fee` = **none on Funded Sim** (verified)
  - "For Funded Sim traders there is no market data fee to pay. Simulated commission is included in your PnL." [P18]
- `payout_min` = **250** (verified)
  - "The minimum payout request amount is $250" [P6]
- `payout_cap` = **min(50% of balance, $1,500) per request for 50K opened on/after 2026-07-26 ($2,000 before); no lifetime cap stated** (verified)
  - "Payout requests are limited to a maximum of 50% of the account balance and are also capped based on account tier:" [P6]
  - "$1,500 on a 50K," [P6]
  - note: 'Balance' in the examples means profit above the starting balance.
- `payout_frequency_gate` = **5 new profitable days of >= $150 (non-consecutive) per cycle, balance above start, net profit since last payout, 45% consistency; no buffer; no trading while a payout is pending** (verified)
  - "$50K Account: 5 days with at least $150 profit per day" [P6]
  - "Important: Once you submit a payout request, do not resume trading until you have received your payout." [P6]
  - "There is no buffer requirement for Fast Pass Funded Sim accounts." [P6]
- `payout_split` = **80/20 Funded Sim; 90/10 Funded Live** (verified)
  - "Profit split: 80/20 Funded Sim, 90/10 Funded Live" [P1]
- `payout_processing_days` = **within 24 hours (business days) if requested before 5:30 pm CT** (verified)
  - "Requests received before 5:30 pm CT will be processed within 24 hours (business days only)." [P20]
- `payout_fee` = **US wire free; international wire $15; L1 crypto $2.5 + gas; L2 crypto free (Riseworks)** (verified)
  - "International bank wire withdrawals: $15/withdrawal" [P21]
  - "US bank wire withdrawals: Free" [P21]
  - note: Stated on the Quick Pay payout page; Fast Pass page gives no fees (same Riseworks rails).
- `payout_count_limit` = **4 payouts in Funded Sim; the 5th request moves the account to Funded Live (earlier at TradeDay's discretion)** (verified)
  - "If a trader is demonstrating consistency in the funded sim account, TradeDay may move the trader to funded Live before the 5th payout request." [P6]
- `max_accounts` = **10 total; 5 active Funded Sim; 5 Funded Live; one user per household; one broker** (verified)
  - "Traders can only have multiple accounts on 1 broker." [P8]
  - "If a trader has an active Funded Live account, they will not be able to purchase additional accounts until they have been off-boarded from the Funded Live." [P8]
- `inactivity_rule` = **30 days dormant may be offboarded; Tradovate archives after a month without login** (verified)
  - "In addition, any TradeDay account that remains dormant or inactive for 30 days will be considered inactive and may be offboarded." [P22]
- `copy_trading_terms` = **allowed among own Eval/Funded Sim (2-10) and among up to 5 Funded Live; not across Live and Sim/Eval** (verified)
  - "Funded Live: You may copy trade between up to 5 Funded Live accounts." [P7]
  - "No. You cannot have active trades simultaneously across a Funded Live account and an Evaluation or Funded Sim account." [P7]
- `cross_account_hedging` = **prohibited** (verified)
  - "Hedging is prohibited at TradeDay (the practice of simultaneously going long in one account and short in another account for the same product)." [P12]
- `news_trading_terms` = **tier-1 releases banned (flat 2 min before to 2 min after)** (verified)
  - "All profits from trading tier 1 data releases, trading in breach of our permitted times." [P3]
  - note: Tier 1 = FOMC minutes/decision, US CPI, NFP for all products.
- `automation_terms` = **own ATS via supported platforms only; third-party bots forbidden; no API** (verified)
  - "Using trading bots or Automated Trading Systems (ATS) purchased from a third party. Or multiple users using the same trading bots and ATS's." [P12]
- `sizing_or_gambling_terms` = **large single days discounted via consistency; seconds-scalping and >200 trades/day banned; order splitting banned** (verified)
  - "Order splitting. Entering multiple orders at the same price at the same time." [P12]
  - "Using automated trading systems designed to scalp at an extremely high frequency. We do not allow strategies that produce more than 200 trades in a day." [P12]
- `other_conduct_bearing` = **flat 10 min before the close (auto-liquidated 3:50 pm CT); no trading within 2% of a price limit when funded; first payout security review** (verified)
  - "Exit all positions 10 minutes before the close. No holding positions when the market closes." [P23]
  - "Rule 2: Funded Traders are not permitted to trade within 2% of a price limit." [P3]
- `permitted_products` = **CME/CBOT/NYMEX/COMEX futures incl. NQ and MNQ** (verified)
  - "| E-mini Nasdaq-100 Futures | NQ | $5.00 | CME" [P24]
  - "| Micro E-mini Nasdaq-100 Index Futures | MNQ | $0.50 | CME" [P24]
  - "TradeDay traders are allowed to trade Futures products only, we allow trading on the following exchanges: CME, CBOT, NYMEX, and COMEX." [P25]

**Terms (`terms_quick_pay_eod_50k`)**

- `eval_profit_target` = **3000** (verified)
  - "| Profit target | $1,500 | $3,000 | $6,000 | $9,000" [P5]
  - note: Raised if best day exceeds 30%.
- `eval_drawdown_amount` = **2000** (verified)
  - "| Trailing max drawdown | $1,000 | $2,000 | $3,000 | $4,500" [P5]
- `eval_drawdown_type` = **eod_trailing (this variant; an Intraday variant also exists)** (verified)
  - "Quick Pay comes in four account sizes, and each is available with either an Intraday or End of Day trailing drawdown:" [P5]
- `eval_drawdown_lock` = **trails to starting balance, then freezes** (verified)
  - "For evaluations and Funded Sims, the Trailing Max Drawdown will trail until they reach the starting account balance, at which time the trailing drawdown will freeze and no longer trail." [P15]
- `eval_daily_loss_limit` = **none stated** (verified)
  - "There's only one rule on the risk side: don't hit or exceed the maximum drawdown." [P5]
- `eval_consistency_rule` = **30%** (verified)
  - "Third, stay consistent: no single day can account for more than 30% of your total profits." [P5]
- `eval_min_days` = **5** (verified)
  - "For QuickPay accounts the minimum number of trading days is 5." [P16]
  - note: Terms say a minimum 7-day period (conflict, see Fast Pass block).
- `eval_position_limit` = **5 contracts / 50 micros** (verified)
  - "| Position limit | 2 contracts (20 micros) | 5 contracts (50 micros) | 10 contracts (50 micros) | 15 contracts (50 micros)" [P5]
- `eval_fee` = **one-time; $69 on the sale card (list $174) vs $175 in the help-centre table** (verified)
  - "End of Day (Intraday Funded Drawdown) 50k $ 174 $ 69 one-time fee" [P1]
  - "| Price | $120 | $175 | $285 | $395" [P13]
  - note: Conflict between sale card and help table, as for Fast Pass.
- `eval_reset_fee` = **99** (verified)
  - "the cost of a reset is $99" [P17]
- `activation_fee` = **none** (verified)
  - "There are no activation fees, and you can purchase a new evaluation account after failing." [P5]
- `eval_count_limit` = **10 evaluations (within 10 accounts total)** (verified)
  - "A trader can trade up to 10 accounts total." [P7]
- `eval_time_limit` = **none** (verified)
  - "There is no upper time limit" [P16]
- `funded_type` = **Funded Sim; paused at $10,000 gross profit for review, usually moved to Funded Live (excess above $10,000 removed)** (verified)
  - "Funded Sim traders will be reviewed at $10,000 gross profit in each of their funded accounts for a move to Funded Live." [P26]
  - "It’s important to note that any excess profits above the threshold will be removed, and the balance will be revised back to the threshold level." [P26]
  - note: On transfer to Live the drawdown is set to $0 (no additional drawdown).
- `funded_drawdown_amount` = **2000** (verified)
  - "Trailing Max Drawdown: $2,000 (calculated intraday)" [P1]
- `funded_drawdown_type` = **intraday trailing** (verified)
  - "The Trailing Maximum Drawdown (TMD) for all Funded Sim Quick Pay accounts are calculated intraday." [P21]
- `funded_drawdown_lock` = **trails to starting balance then freezes** (verified)
  - "For evaluations and Funded Sims, the Trailing Max Drawdown will trail until they reach the starting account balance, at which time the trailing drawdown will freeze and no longer trail." [P15]
- `payout_balance_consequence` = **TMD keyed to gross profits: a payout lowers the balance but not the floor (floor keeps trailing)** (verified)
  - "When a user requests a payout, the TMD is calculated off of gross profits, not the net profits." [P21]
  - "| Day 1 (after payout) | $0 | $50,000 | $48,500 | $0" [P21]
  - note: Example: $500 profit paid out, balance back to $50,000, TMD stays $48,500.
- `funded_daily_loss_limit` = **none stated** (verified)
  - "Rule 1: Do not hit or exceed the maximum drawdown." [P3]
- `funded_consistency_rule` = **none** (verified)
  - "There are no milestones, no consistency requirement, and no payout buffer." [P5]
- `funded_position_limit` = **5 contracts / 50 micros (no scaling)** (verified)
  - "Position Limit: 5 Contracts (50 Micros)" [P1]
- `funded_monthly_fee` = **none on Funded Sim** (verified)
  - "For Funded Sim traders there is no market data fee to pay. Simulated commission is included in your PnL." [P18]
- `payout_min` = **250** (verified)
  - "The minimum payout request is $250." [P21]
- `payout_cap` = **per-request cap not stated; profits above $10,000 gross per account are removed at the Live review** (UNVERIFIED)
  - "Please note that any profits above the $10,000 gross profit level that are in the account will be forfeited and will not be eligible for payouts, transfer to the Funded Live account, or for any extension offered in the Funded Sim account." [P26]
  - looked at: https://tradeday.freshdesk.com/en/support/solutions/articles/103000335937-quick-pay-funded-sim-payout-policy, 103000405228-what-is-quick-pay-, 103000353468, home page plan cards (none states a per-request cap)
  - note: The $10,000 gross threshold acts as an effective Funded Sim ceiling.
- `payout_frequency_gate` = **any positive balance, from day 1, no buffer** (verified)
  - "You can request your first payout after just one day of trading, and you can withdraw at any time as long as your account balance is positive." [P5]
  - note: Article 103000262630 (2025) still says traders must clear the 'Buffer Zone'; superseded by the 2026 Quick Pay pages.
- `payout_split` = **50/50 on current profit below $4,000, 80/20 above (per account); 90/10 Funded Live** (verified)
  - "Below the $4,000 current profit level, payouts are split 50/50. Above $4,000, the split improves to 80/20 in your favour, but only if the payout still leaves more than $4,000 in current profit in the account after the withdrawal." [P5]
- `payout_processing_days` = **next business day if requested before 5:30 pm** (verified)
  - "We aim to process payout requests submitted before 5:30 pm ET by the next business day." [P21]
  - note: Same page later says 5:30 pm CT; ET/CT conflict within the page.
- `payout_fee` = **US wire free; international wire $15; L1 crypto $2.5 + gas; L2 crypto free** (verified)
  - "International bank wire withdrawals: $15/withdrawal" [P21]
- `payout_count_limit` = **no count limit; account paused at $10,000 gross profit for Live review** (verified)
  - "Each account is evaluated independently at $10,000 for a move to Funded Live." [P26]
- `max_accounts` = **10 total; 5 active Funded Sim; 5 Funded Live** (verified)
  - "Traders can have up to 5 Funded Live accounts. When in Funded Live, you will not be able to purchase additional accounts." [P8]
- `inactivity_rule` = **30 days dormant may be offboarded** (verified)
  - "In addition, any TradeDay account that remains dormant or inactive for 30 days will be considered inactive and may be offboarded." [P22]
- `copy_trading_terms` = **as Fast Pass block** (verified)
  - "Evaluation & Funded Sim: You may copy trade any combination of Evaluation and Funded Sim accounts, with 2 to 10 accounts total." [P7]
- `cross_account_hedging` = **prohibited** (verified)
  - "Users caught hedging will be offboarded and suspended, and will forfeit all profits in funded accounts." [P8]
- `news_trading_terms` = **tier-1 releases banned** (verified)
  - "TradeDay will auto-liquidate all open positions 2 minutes before TradeDay's tier 1 economic data releases, and open markets back up to trade 2 minutes after these releases." [P9]
- `automation_terms` = **third-party bots forbidden; no API** (verified)
  - "Algos and Bots purchased from a third party and employed by the trader are forbidden." [P10]
- `sizing_or_gambling_terms` = **seconds-scalping and >200 trades/day banned** (verified)
  - "Strategies that trade in a few seconds, designed to capture just a couple of ticks at a time." [P11]
- `other_conduct_bearing` = **flat 10 min before close; 2% price-limit rule; frequent/large withdrawals may bar re-entry** (verified)
  - "Traders who make frequent or large withdrawals that leave the account vulnerable to hitting the drawdown may be viewed as mismanaging the account and may not be invited to rejoin the TradeDay team to retake another evaluation." [P15]
  - note: Bears directly on a withdraw-early design under the intraday gross-profit TMD.
- `permitted_products` = **CME Group futures incl. NQ/MNQ** (verified)
  - "| E-mini Nasdaq-100 Futures | NQ | $5.00 | CME" [P24]

### Top One Futures (`topone`) -- PASS

**Pages quoted** (key: URL; article id; the page's own date as shown; all read 2026-11-15)

- [P1] https://help.toponefutures.com/en/articles/15056075-elite-daily-v2-overview; id 15056075; page date: Updated over 2 weeks ago
- [P2] https://help.toponefutures.com/en/articles/14617600-differences-between-elite-elite-access-and-elite-daily-accounts; id 14617600; page date: October 13, 2026
- [P3] https://help.toponefutures.com/en/articles/13449146-top-one-futures-account-comparison-elite-vs-instant-vs-ignite-accounts; id 13449146; page date: Updated over 3 weeks ago
- [P4] https://toponefutures.com/
- [P5] https://help.toponefutures.com/en/articles/13904722-elite-daily-v2-max-loss-limit-mll; id 13904722; page date: Updated over 2 weeks ago
- [P6] https://help.toponefutures.com/en/articles/15056475-elite-daily-v2-40-consistency-target-evaluation-only; id 15056475; page date: October 2, 2026
- [P7] https://help.toponefutures.com/en/articles/15056446-elite-daily-v2-daily-payout-rules; id 15056446; page date: October 2, 2026
- [P8] https://help.toponefutures.com/en/articles/13904864-elite-daily-v2-maximum-account-rules; id 13904864; page date: October 2, 2026
- [P9] https://help.toponefutures.com/en/articles/11532971-what-is-the-limit-for-funded-accounts-per-household; id 11532971; page date: Updated over 3 weeks ago
- [P10] https://help.toponefutures.com/en/articles/11680891-copy-trading-policy; id 11680891; page date: Updated this week
- [P11] https://help.toponefutures.com/en/articles/11021584-prohibited-trading-practices; id 11021584; page date: Updated over 3 weeks ago
- [P12] https://help.toponefutures.com/en/articles/13904852-elite-daily-v2-news-trading-rule-funded-only; id 13904852; page date: October 2, 2026
- [P13] https://www.toponefutures.com/terms-and-conditions; page date: Last updated: November 9, 2026
- [P14] https://help.toponefutures.com/en/articles/15056388-elite-daily-v2-daily-loss-limit-dll-evaluation-phase; id 15056388; page date: Updated this week
- [P15] https://help.toponefutures.com/en/articles/13904734-elite-daily-v2-profit-target-evaluation; id 13904734; page date: October 2, 2026
- [P16] https://help.toponefutures.com/en/articles/13904824-elite-daily-v2-contract-scaling-plan; id 13904824; page date: October 2, 2026
- [P17] https://help.toponefutures.com/en/articles/11021027-how-do-subscriptions-work-on-top-one-futures; id 11021027; page date: October 2, 2026
- [P18] https://help.toponefutures.com/en/articles/15069348-elite-daily-v2-reset-fees; id 15069348; page date: October 13, 2026
- [P19] https://help.toponefutures.com/en/articles/14073378-elite-daily-v2-i-ve-passed-the-evaluation-what-s-next; id 14073378; page date: October 2, 2026
- [P20] https://help.toponefutures.com/en/articles/11003130-path-to-trading-live; id 11003130; page date: October 1, 2026
- [P21] https://help.toponefutures.com/en/articles/11024436-understanding-lock-upon-payout; id 11024436; page date: October 2, 2026
- [P22] https://help.toponefutures.com/en/articles/13904706-elite-daily-v2-daily-loss-limit-dll-funded-phase; id 13904706; page date: Updated this week
- [P23] https://help.toponefutures.com/en/articles/10907367-maximum-payout-until-live-explained; id 10907367; page date: October 2, 2026
- [P24] https://help.toponefutures.com/en/articles/10907463-what-is-the-maximum-number-of-accounts-i-can-trade; id 10907463; page date: Updated over 3 weeks ago
- [P25] https://help.toponefutures.com/en/articles/10907989-inactivity-rule-explained; id 10907989; page date: October 16, 2026
- [P26] https://help.toponefutures.com/en/articles/10907920-can-i-use-ea-s-bots; id 10907920; page date: October 1, 2026
- [P27] https://help.toponefutures.com/en/articles/10907901-can-i-hold-trades-overnight; id 10907901; page date: October 1, 2026
- [P28] https://help.toponefutures.com/en/articles/11021492-trading-instruments-available-at-top-one-futures; id 11021492; page date: October 2, 2026
- [P29] https://help.toponefutures.com/en/articles/12829687-top-one-futures-commissions-and-fees; id 12829687; page date: October 2, 2026


Official domains: toponefutures.com, www.toponefutures.com, help.toponefutures.com (Intercom help centre linked from the site). Read 2026-11-15.
Plan captured: Elite Daily V2 $50K.
Verdict: **PASS** -- Elite Daily V2: EOD trailing drawdown on funded and no funded consistency rule, 5 accounts per household, manual bracket trading not forbidden (copying only same type/size; churning rule and Live transition caveats).

Plans seen:
- Elite Daily V2 $50K (one-phase evaluation, accounts bought on/after 5/11/26): drawdown EOD trailing $2,000 (eval and funded), locks at start + $100; consistency evaluation 40%, funded none
  - "Key highlights: one phase evaluation, End of Day trailing drawdown, 40% consistency rule during the evaluation only, daily payouts from Day 1 with a 50% Daily Progression Rule, 90/10 profit split, no activation fee and a maximum of 5 funded accounts per trader." [P1]
- Elite ACCESS $50K (and Elite ACCESS Intraday): drawdown eval EOD (static during the Black November promotion); funded static (Elite ACCESS) or intraday (Elite ACCESS Intraday); consistency evaluation none, funded 40%
  - "| Consistency Rule | 25% | 40% | None" [P2]
- Elite (classic) $50K evaluation: drawdown EOD trailing; consistency evaluation none, funded 25%
  - "| Consistency Rule | No Consistency Rule | 25%" [P3]
- Instant Sim Funded $50K (no evaluation): drawdown EOD trailing $2,000; consistency evaluation n/a, funded 20%
  - "Trailing max drawdown $2,000 Drawdown mode End of day Max contracts 3 minis (30 micros) Consistency 20%" [P4]
- Ignite Instant Funded $50K (no evaluation): drawdown EOD trailing $2,000; consistency evaluation n/a, funded 15%
  - "Trailing max drawdown $2,000 Drawdown mode End of day Max contracts 3 minis (30 micros) Consistency 15%" [P4]

**Screen**

- `drawdown_eval` = **eod_trailing** (verified)
  - "| Drawdown Type | End of Day (EOD) | End of Day (EOD) | End of Day (EOD) | End of Day (EOD)" [P1]
  - note: The level moves only at end of day, but breach is checked in real time on equity (see MLL article).
- `drawdown_funded` = **eod_trailing, locks at starting balance + $100** (verified)
  - "| Drawdown Type | EOD | EOD | EOD | EOD" [P1]
  - "It moves up only at the end of the day, based on your closing balance. Intraday highs don’t move it." [P5]
- `consistency_eval` = **40% (largest day / total profit, checked when the target is reached; not a fail, keep trading)** (verified)
  - "No single trading day may account for more than 40% of your total profit at the moment the profit target is reached." [P6]
- `consistency_funded` = **none** (verified)
  - "There is no consistency rule once funded." [P6]
  - "There is no consistency target on Elite Daily funded accounts." [P7]
- `max_funded_accounts` = **5 Elite Daily accounts per household (evaluation + funded combined); 38 funded across all categories** (verified)
  - "The limit: a trader's household may trade a maximum of 5 Elite Daily accounts at any time. This includes evaluation accounts, funded accounts, or a combination of both. The 5 account limit is total, not per stage." [P8]
  - "| Elite Daily Funded | 5 | All 5 must be the exact same account size" [P9]
  - note: Conflict: the Elite Daily article allows mixing sizes ('You may mix account sizes within your 5 account limit') while the household and max-accounts articles say all 5 must be the same size; the homepage card shows 'Max Accounts 3 5'. The overview counts 5 funded per trader; the Elite Daily rule article counts eval + funded together per household.
- `copy_trading` = **allowed between own accounts of the exact same type and size (Tradovate group trading provided)** (verified)
  - "However, to maintain risk integrity, copy trading is strictly limited to accounts of the exact same type and exact same size." [P10]
  - note: Same-direction trades on correlated instruments (ES/NQ, NQ/MNQ) across mismatched account types or sizes count as copy trading even when entered by hand.
- `opposite_positions` = **prohibited (hedging between accounts, within the firm or across firms)** (verified)
  - "You may not hedge one account against another, whether within Top One Futures or across other prop firms or brokers." [P11]
- `news` = **evaluation free; Elite Daily funded: no execution, close or stop/target change 2 min before to 2 min after major high-impact news** (verified)
  - "On funded Elite Daily accounts, you may not execute trades 2 minutes before a major news event and 2 minutes after a major news event. The total restricted window is 4 minutes." [P12]
- `automation` = **prohibited; trades must be entered manually or semi-manually** (verified)
  - "Use of any automated trading system, script, bot, Expert Advisor (EA), or high-frequency execution tool is strictly forbidden. All trades must be entered manually or semi-manually by the trader." [P11]
  - note: Hand-entered bracket orders are consistent with this.
- `sizing_gambling` = **churning/batch-buying evaluations and gambling prohibited; 10-second minimum hold** (verified)
  - "Creating multiple evaluation accounts in a short period and using a batch-style approach, such as intentionally letting most accounts fail while focusing on passing just one, is strictly prohibited." [P11]
  - "Gambling or reckless trading, including excessive leverage, over-risking, or large position sizes relative to account norms." [P13]
  - note: Bears directly on a multi-account design that buys several evaluations at once.

**Terms (`terms`)**

- `eval_profit_target` = **3000** (verified)
  - "| Profit Target | $1,500 (6%) | $3,000 (6%) | $6,000 (6%) | $9,000 (6%)" [P1]
  - note: Closed P&L only; all trades must be closed for review.
- `eval_drawdown_amount` = **2000** (verified)
  - "| Trailing Max Drawdown | $1,000 | $2,000 | $3,000 | $4,500" [P1]
- `eval_drawdown_type` = **eod_trailing (level set from closing balance; breach checked in real time on equity)** (verified)
  - "Unlike the Daily Loss Limit, the MLL is based on an End of Day (EOD) trailing drawdown model." [P5]
  - "The breach level is checked in real time. If your equity goes at or below it at any moment, the account is breached." [P5]
- `eval_drawdown_lock` = **locks at starting balance + $100** (verified)
  - "As your account grows, the drawdown level locks in at your starting balance + $100 and does not continue to trail." [P5]
  - note: The MLL article covers evaluation and funded accounts alike; it does not separate the lock by stage.
- `eval_daily_loss_limit` = **1000, soft (pause until next trading day), from previous day's close, includes floating losses** (verified)
  - "| $50,000 | $1,000" [P14]
  - "| Evaluation accounts | Violating the DLL during evaluation results in a pause; your account will automatically unpause the next trading day." [P14]
- `eval_consistency_rule` = **40% of total profit on the largest day, checked when the target is reached; exceeding it delays the pass, does not fail** (verified)
  - "The rule does not automatically fail the account. It simply requires more balanced profit distribution before passing." [P6]
  - note: Based on closed profits only.
- `eval_min_days` = **none stated (the 40% rule implies at least 3 profitable days)** (verified)
  - "Important: although there is no minimum day requirement, the 40% Consistency Rule must still be respected." [P15]
  - note: The 3-day floor is arithmetic from the 40% rule, not a stated rule.
- `eval_position_limit` = **3 minis / 30 micros, full allocation from day one (no scaling in evaluation)** (verified)
  - "| Max Contracts | 1 | 3 | 5 | 7" [P1]
  - "There are no scaling restrictions during the evaluation phase." [P16]
- `eval_fee` = **$218 list ($98 with the current 55% BLACKFRIDAY promotion); help centre says the evaluation is a monthly auto-renewing subscription** (verified)
  - "$50K Evaluation Daily Payouts No Activation Fee $218 $98 55% OFF" [P4]
  - "Monthly Payment One time fee" [P4]
  - "In our evaluation program, we operate on a monthly subscription model that renews automatically each month." [P17]
  - note: The homepage card has a 'Monthly Payment / One time fee' toggle and its checkout link carries billing=onetime; which price belongs to which billing mode could not be read from the static page. A rebill on a breached evaluation resets it.
- `eval_reset_fee` = **$104 (reset-fee article, 13 Oct 2026); conflicting $82 (overview) and $93 (homepage)** (verified)
  - "| Elite Daily Evaluation V2 account | Reset fee" [P18]
  - "| $50,000 | $104" [P18]
  - "| Reset on Evaluation | $66 | $82 | $154 | $215" [P1]
  - "Reset Fee $93" [P4]
  - note: Three official figures conflict ($82 / $93 / $104); the differences article says 'From $93 to $297'. Reset only within 14 days of breach; coupons do not apply. Funded reset $499.
- `activation_fee` = **none** (verified)
  - "| No activation fee | You do not need to pay any upfront or hidden fees to activate your funded account." [P19]
- `eval_count_limit` = **up to 10 evaluation purchases per rolling 30 days; 12 resets per evaluation per 30 days; max 5 Elite Daily accounts (eval + funded) at once** (verified)
  - "| Evaluation purchases | Up to 10 evaluation accounts within any rolling 30-day period starting from the initial purchase date." [P8]
- `eval_time_limit` = **none (subscription renews monthly until passed or cancelled)** (verified)
  - "| Time to Pass | No set limit | 30 Days | No set limit" [P2]
- `funded_type` = **sim funded; after 5 payouts typically moved to Pre-Live/Live (80/20 split, $0 start, $2,000 EOD MLL for 50K); other accounts disabled during the move** (verified)
  - "After successfully completing 5 payouts, traders will typically become eligible to transition to a Live account." [P7]
  - "When transitioning to a live / pre-live account, all other accounts are temporarily disabled while the risk manager evaluates the trader's performance." [P20]
  - "If one person in your home transitions to a Live Funded account, no one else in the household may activate or trade on a Sim Funded account." [P9]
  - note: Being selected for Live cannot be declined (only trade live or close the sim account); deliberately breaching to stay in sim is prohibited. A Live account ends the multi-sim-account phase.
- `funded_drawdown_amount` = **2000** (verified)
  - "| Trailing Drawdown | $1,000 | $2,000 | $2,500 | $3,500" [P1]
- `funded_drawdown_type` = **eod_trailing (breach checked in real time on equity)** (verified)
  - "| End of Day Trailing Drawdown | The breach level trails at the end of the trading day with your highest closed balance, not intraday. The breach level is checked in real time. If your equity goes at or below it at any moment, the account is breached. See Max Loss Limit (MLL)." [P1]
- `funded_drawdown_lock` = **$50,100 (start + $100); the general rule also locks on first payout** (verified)
  - "| Drawdown Locks At | $25,100 | $50,100 | $100,100 | $150,100" [P1]
  - "When you request a payout, your maximum trailing drawdown locks in at the starting balance plus $100." [P21]
  - note: The lock-on-payout article is general (not Elite Daily specific); with a $2,500 buffer the 50K account reaches the $52,100 lock trigger before any payout anyway.
- `payout_balance_consequence` = **balance must stay at or above $52,500 after a payout ($2,500 buffer); floor stays at $50,100** (verified)
  - "| Account size | Max payout per request | Buffer | Minimum balance after payout" [P7]
  - "| $50K | $1,000 | $2,500 | $52,500" [P7]
  - "Once an Elite Daily funded account is breached, profits remaining inside the buffer are not withdrawable." [P7]
  - note: The floor after payout follows from the lock rows; the payout article itself says only that the EOD trailing drawdown remains active.
- `funded_daily_loss_limit` = **1000, soft breach (trading paused for the rest of the day), from previous day's close** (verified)
  - "| $50,000 | $1,000" [P22]
  - "| Soft breach | Trading is paused for the remainder of the trading day." [P22]
- `funded_consistency_rule` = **none** (verified)
  - "There is no consistency target on Elite Daily funded accounts." [P7]
  - note: Replaced by the 50% Daily Progression Rule (see payout_frequency_gate).
- `funded_position_limit` = **scaling on EOD balance: 1 mini ($0-$1,499 profit), 2 minis ($1,500-$1,999), 3 minis ($2,000+)** (verified)
  - "| $0 to $1,499 | 1 Mini / 10 Micros" [P16]
  - "| $1,500 to $1,999 | 2 Minis / 20 Micros" [P16]
  - "| $2,000+ | 3 Minis / 30 Micros (Full Allocation)" [P16]
  - note: These rows are under the $50K heading of the scaling table; increases apply the next trading day; limits do not stack across accounts.
- `funded_monthly_fee` = **none (the evaluation subscription ends on passing)** (verified)
  - "| Elite Daily accounts | There is no activation fee. Your subscription will automatically end once you have passed the evaluation | You must manually cancel the subscription yourself to avoid being charged again" [P17]
  - note: No page states a funded monthly fee; 'none' is read from the subscription ending on pass.
- `payout_min` = **500** (verified)
  - "| Minimum payout | $500. Requests below $500 will not be processed." [P7]
- `payout_cap` = **$1,000 per request (sim); no lifetime cap stated; no caps once Live** (verified)
  - "| Maximum payout per request | See table below. Profits above the maximum payout cap remain in the account." [P7]
  - "Once a trader qualifies for a Live Account, this limit is removed, and traders can withdraw without restriction." [P23]
  - note: The $1,000 figure is in the '$50K | $1,000 | $2,500 | $52,500' row quoted under payout_balance_consequence.
- `payout_frequency_gate` = **every 24 hours; min 1 funded trading day; balance above buffer; after the first payout at least 50% of each payout must be new profit since the last payout** (verified)
  - "Funded traders may request a payout every 24 hours, provided all payout conditions are met." [P7]
  - "| Daily Progression Rule (50% rule) | After your first payout, at least 50% of every future payout request must come from new profits generated since your previous payout. This requirement resets after every approved payout." [P7]
  - "| Min Trading Days (Funded) | 1 | 1 | 1 | 1" [P1]
  - note: Minor conflict: the overview says the 50% rule applies 'For each payout request'; the payout article says 'After your first payout'. The differences article puts the first-payout threshold at 'Reach Buffer + $500'. Next eligibility starts the following trading day.
- `payout_split` = **90/10 (80/20 once Live)** (verified)
  - "| Profit split | 90% Trader / 10% Firm on all funded Elite Daily accounts." [P7]
- `payout_processing_days` = **not stated as a rule (homepage advertises an average under 12 hours)** (UNVERIFIED)
  - "< 12 Hour average payout times" [P4]
  - looked at: ed-15056446 (payout rules), ar-10907392, ar-11024317, ar-15472196, terms-and-conditions
  - note: Marketing average, not a commitment. Payouts go through Rise (verified Rise account required).
- `payout_fee` = **not stated** (UNVERIFIED)
  - looked at: ed-15056446, ar-11024317 (payout platforms), ar-15472196, ar-12829687 (commissions and fees), terms-and-conditions
- `payout_count_limit` = **no cap stated; standard guideline is transition to Live after 5 payouts** (verified)
  - "For most accounts, you need 3 successful payouts. Elite Daily accounts are the exception and require 5 successful payouts." [P20]
  - note: The firm may move a trader to Live sooner.
- `max_accounts` = **5 Elite Daily accounts (eval + funded combined) per household; promotional periods may allow more** (verified)
  - "A trader may maintain no more than 5 active funded accounts at any given time" [P1]
  - "During certain promotional periods, we may allow traders to hold more accounts than these standard limits." [P24]
  - "Max Accounts 3 5 Payout Frequency" [P4]
  - note: See the screen note: the size-mixing and eval-counting rules conflict between articles. Over-limit accounts: the oldest active account is breached automatically.
- `inactivity_rule` = **at least one trade every 14 calendar days (336 hours) or hard breach** (verified)
  - "All traders must place at least one trade every 14 calendar days to keep their account in good standing." [P25]
- `copy_trading_terms` = **allowed between own accounts of identical type and size; firm provides Tradovate group trading; copying between own accounts at other firms allowed** (verified)
  - "You can only copy trades between accounts that belong to the identical program and share the same size." [P10]
  - "Top One Futures allows copy trading between your own accounts at different firms, including through third-party platforms." [P10]
  - note: Conflict: the Terms and Conditions list 'Copy trading, signal-following, or group trading with external accounts.' as prohibited, while the copy-trading article allows copying between your own accounts at other firms.
- `cross_account_hedging` = **prohibited** (verified)
  - "Hedging accounts against each other or arbitraging trades between accounts." [P13]
  - note: Listed under prohibited trading practices.
- `news_trading_terms` = **evaluation unrestricted; funded: 4-minute window around major high-impact events in which no open, close, pending order or stop/target change is allowed; holding through is allowed** (verified)
  - "Your trade must not be closed by any means during the restricted news window." [P12]
  - "| Stops or targets modified inside the window | Violation" [P12]
  - note: A bracket whose stop or target fills inside the window is a violation ('closed by any means'): a funded bracket design must be flat before the window. Violations remove profits / deny payouts rather than hard-breach.
- `automation_terms` = **EAs/bots prohibited on all accounts; manual or semi-manual entry only** (verified)
  - "No, the use of Expert Advisors (EAs) or Bots is not allowed on your accounts." [P26]
- `sizing_or_gambling_terms` = **churning / batch evaluations, breaching within 24-48h and repurchasing, and oversized positions are prohibited** (verified)
  - "This includes consistently breaching accounts within 24 to 48 hours of purchase and then immediately repurchasing new accounts, indicative of toxic trading strategies." [P11]
  - "Rolling or churning accounts—creating multiple accounts to pass some while letting others fail." [P13]
- `other_conduct_bearing` = **10-second minimum hold; all positions closed by 4:10 PM EST (no overnight); one profile per person; hard stops recommended over the DLL** (verified)
  - "All trades must remain open longer than 10 seconds. 10.00 seconds = violation, 10.01 seconds = acceptable." [P11]
  - "No, traders must close all positions by 4:10 PM EST." [P27]
  - "Place hard stop loss orders directly on your trades; any loss beyond your allowed threshold remains the trader's responsibility." [P22]
  - "ES (S&P 500) and NQ (Nasdaq), or YM (Dow Jones) and RTY (Russell 2000) in the same direction across mismatched accounts." [P10]
  - note: Closing any portion of a position within 10 seconds is a violation (a bracket target hit within 10 s would be one). Same-direction NQ/MNQ trades across mismatched account types/sizes count as copy trading.
- `permitted_products` = **CME/CBOT/NYMEX/COMEX futures incl. ES, NQ, MES, MNQ (round turn $5.76 NQ, $1.90 MNQ)** (verified)
  - "| /NQ | NASDAQ-100 | Based on the NASDAQ-100 index, which includes major tech companies" [P28]
  - "| /MNQ | Micro NASDAQ-100 | Micro version of the NASDAQ-100 futures contract" [P28]
  - "| /MNQ (Micro NASDAQ-100) | $1.90" [P29]

### FXIFY Futures (trading as Futureify; FXIFY Futures Limited, Dublin) (`fxify`) -- PASS

**Pages quoted** (key: URL; article id; the page's own date as shown; all read 2026-11-15)

- [P1] https://futureify.com/faqs/general-rules/what-are-futureify-consistency-rules/; id what-are-futureify-consistency-rules; page date: Updated on September 28, 2026
- [P2] https://futureify.com/faqs/general-rules/what-is-the-maximum-loss-limit-mll/; id what-is-the-maximum-loss-limit-mll; page date: Updated on September 28, 2026
- [P3] https://futureify.com/faqs/general-rules/funded-account-parameters-overview/; id funded-account-parameters-overview; page date: Updated on September 28, 2026
- [P4] https://futureify.com/faqs/flex-plan/flex-plan-payout-policy/; id flex-plan-payout-policy; page date: Updated on October 28, 2026
- [P5] https://futureify.com/faqs/general-rules/what-is-the-maximum-number-of-accounts-allowed/; id what-is-the-maximum-number-of-accounts-allowed; page date: Updated on September 28, 2026
- [P6] https://futureify.com/faqs/general-rules/does-futureify-allow-copy-trading/; id does-futureify-allow-copy-trading; page date: Updated on September 28, 2026
- [P7] https://futureify.com/faqs/general-rules/what-trading-strategies-are-prohibited/; id what-trading-strategies-are-prohibited; page date: Updated on September 28, 2026
- [P8] https://futureify.com/faqs/general-rules/news-trading-policy/; id news-trading-policy; page date: Updated on September 28, 2026
- [P9] https://futureify.com/faqs/general-rules/can-i-use-eas-expert-advisors-to-trade/; id can-i-use-eas-expert-advisors-to-trade; page date: Updated on November 4, 2026
- [P10] https://futureify.com/faqs/flex-plan/flex-plan-overview/; id flex-plan-overview; page date: Updated on September 28, 2026
- [P11] https://futureify.com/faqs/general-rules/account-parameters-overview/; id account-parameters-overview; page date: Updated on September 28, 2026
- [P12] https://futureify.com/faqs/general-rules/what-is-the-minimum-trading-days-requirement/; id what-is-the-minimum-trading-days-requirement; page date: Updated on September 28, 2026
- [P13] https://futureify.com/faqs/billing/what-is-futureify-account-payment-structure/; id what-is-futureify-account-payment-structure; page date: Updated on September 28, 2026
- [P14] https://fxifyfutures.com/
- [P15] https://futureify.com/faqs/general-rules/what-happens-after-passing-the-evaluation/; id what-happens-after-passing-the-evaluation; page date: Updated on September 28, 2026
- [P16] https://futureify.com/faqs/general-rules/what-is-the-time-limit-to-complete-the-evaluation/; id what-is-the-time-limit-to-complete-the-evaluation; page date: Updated on September 28, 2026
- [P17] https://futureify.com/faqs/general-rules/what-is-futureify-inactivity-policy/; id what-is-futureify-inactivity-policy; page date: Updated on September 28, 2026
- [P18] https://futureify.com/faqs/general-rules/what-are-the-trading-hours-at-futureify/; id what-are-the-trading-hours-at-futureify; page date: Updated on September 28, 2026


Official domains: fxify.com (links 'FXIFY Futures - Learn more' to fxifyfutures.com and links futureify.com), fxifyfutures.com (serves the Futureify site), futureify.com (site and /faqs help centre). Read 2026-11-15.
Plan captured: Flex Evaluation $50K.
Verdict: **PASS** -- Flex: EOD trailing drawdown on funded (40% funded consistency), 5 accounts total with own-account copy trading, hand bracket trading allowed (caveats: 'tight brackets' fill exploitation and sub-10-tick micro-scalping are prohibited).

Unreadable (not worked around):
- https://fxify.com/futures -- 404 (guessed URL)
- https://futureify.com/terms-and-conditions/ -- served a PDF; the fetch script's HTML-to-text step yields no text, so the Terms were not read (not worked around)

Plans seen:
- Flex Evaluation $50K (one-step): drawdown EOD trailing $1,750, locks at starting balance at +$1,750 profit or first payout; consistency evaluation 50%, funded 40%
  - "- Funded Stage: 40% Consistency Rule. Trading returns from any single trading day cannot exceed 40% of total returns when requesting payouts on a simulated funded account." [P1]
- Direct Instant Funded $50K (no evaluation): drawdown EOD trailing $1,750; consistency evaluation n/a, funded 25%
  - "- 25% Consistency Rule: Trading returns from any single trading day cannot exceed 25% of total returns." [P1]

**Screen**

- `drawdown_eval` = **eod_trailing** (verified)
  - "At Futureify, the Maximum Loss Limit is an End-of-Day (EOD) trailing drawdown based on the highest account balance recorded at market close." [P2]
- `drawdown_funded` = **eod_trailing; locks at starting balance after first withdrawal** (verified)
  - "The maximum allowable loss threshold trails your peak End-of-Day balance to protect account equity:" [P3]
- `consistency_eval` = **50%** (verified)
  - "- Evaluation Stage: 50% Consistency Rule. Trading returns from any single trading day cannot exceed 50% of the total returns made during the evaluation phase." [P1]
- `consistency_funded` = **40% per payout cycle** (verified)
  - "Consistency calculations reset after each payout request and are based only on trading returns generated since the last payout." [P4]
- `max_funded_accounts` = **5 active accounts in total (evaluation + funded + Direct combined)** (verified)
  - "At Futureify, traders can hold a maximum of 5 active accounts in total across all Evaluation and Funded stages combined." [P5]
  - note: Per trader; household rule not found on the pages read.
- `copy_trading` = **allowed between own accounts, enabled by default** (verified)
  - "Yes, copy trading is permitted at Futureify and is enabled by default." [P6]
- `opposite_positions` = **prohibited (reverse trading across separate accounts)** (verified)
  - "- Reverse Trading: Simultaneously taking opposite positions (long and short) on separate accounts to exploit market moves is not allowed at the Evaluation or Funded Phases." [P7]
- `news` = **allowed; high-leverage news gambling prohibited** (verified)
  - "At Futureify, news trading is allowed, and we recognize the significant role news events can play in market movements." [P8]
- `automation` = **EAs and automated scripts permitted, enabled by default** (verified)
  - "Yes, the use of Expert Advisors (EAs) and automated trading scripts is permitted on both Flex and Direct accounts." [P9]
  - note: Hand entry unaffected.
- `sizing_gambling` = **'all or nothing' max-leverage positions, using loss limits as stops, account rolling prohibited** (verified)
  - "Using maximum leverage on a single position or relying on loss limits as a stop-loss strategy is prohibited." [P7]

**Terms (`terms`)**

- `eval_profit_target` = **3000** (verified)
  - "$50,000 Account: $3,000 profit target" [P10]
- `eval_drawdown_amount` = **1750** (verified)
  - "- Initial Threshold: On a $50,000 Flex account with a $1,750 Max Drawdown, your initial minimum allowable balance threshold is set to $48,250." [P2]
  - note: Optional checkout add-on raises it by $250.
- `eval_drawdown_type` = **eod_trailing (on closing balance)** (verified)
  - "Calculated as an End-of-Day (EOD) trailing drawdown based on the account’s closing balance:" [P10]
  - "If your account balance falls to or below your Maximum Loss Limit threshold, all open positions will be closed, and the account will be deactivated:" [P2]
  - note: Not stated whether the breach test uses intraday equity or balance.
- `eval_drawdown_lock` = **locks at starting balance ($50,000) once profit reaches $1,750 or a payout is processed** (verified)
  - "- Locking the Drawdown: Once your account profit equals your initial drawdown cushion (reaching $51,750 on a $50k account), or whenever a payout request is processed, the trailing threshold locks permanently at your starting account balance ($50,000) for the remainder of the account's life." [P2]
- `eval_daily_loss_limit` = **1000, soft breach (read-only for the rest of the day)** (verified)
  - "Caps allowable intraday losses on all account sizes. Hitting this limit sets your account to read-only for the remainder of the trading day:" [P10]
  - "$50,000 Account: $1,000 (2%)" [P10]
  - note: Optional add-on removes the DLL.
- `eval_consistency_rule` = **50% (not a fail; keep trading until compliant)** (verified)
  - "If your trading returns from a single trading day exceed the allowed percentage threshold (50% for Flex Evaluation, 40% for Flex Funded, 25% for Direct), you do not fail your account." [P1]
- `eval_min_days` = **2 (one page states a 2-day minimum; another says none but the 50% rule forces 2)** (verified)
  - "- Flex Plan (Evaluation): 6% of the account balance ($3,000 for $50k, $6,000 for $100k, $9,000 for $150k) with a minimum requirement of 2 trading days." [P11]
  - "- Flex Plan (Evaluation): There is no minimum trading-day requirement across any account size ($50,000, $100,000, and $150,000)." [P12]
  - note: Wording conflict, same practical effect.
- `eval_position_limit` = **3 minis / 30 micros** (verified)
  - "$50,000 Account: Max 3 mini / 30 micro contracts" [P10]
- `eval_fee` = **$179 one-time (homepage promo $107.40 with code; $89.50 each in a bundle of 5)** (verified)
  - "$50,000 Account: $179 one-time fee" [P13]
  - "For $50K account40% off with codeFUTUREIFYCopied!Bundle of 5: $89.50 each account" [P14]
- `eval_reset_fee` = **89** (verified)
  - "Failed evaluation accounts can be reset at any time for a discounted reset fee ($89 for $50k, $149 for $100k, $209 for $150k), which issues a brand-new evaluation account." [P10]
  - note: No resets once funded.
- `activation_fee` = **none** (verified)
  - "There are no activation fees or additional charges required to set up your funded account." [P15]
  - note: Homepage shows 'No activation Fee*' with an asterisk whose footnote was not found.
- `eval_count_limit` = **within the 5-account total** (verified)
  - "- Combined Account Cap: Your 5-account limit includes all active Flex Evaluation accounts, Flex Funded accounts, and Direct accounts combined." [P5]
- `eval_time_limit` = **30 days, extendable for a fee** (verified)
  - "The Flex Evaluation has a 30-day duration to meet your profit target. If you need additional time to reach your goal, you can extend your evaluation duration directly from your account dashboard by paying a small fee." [P16]
  - note: Contradicts the lead 'no evaluation deadline'. Extension fee amount not stated.
- `funded_type` = **simulated funded (help centre); homepage says 'Live account credentials'** (verified)
  - "Designed for traders who want to build discipline and prove consistent risk management, this plan requires reaching a 6% profit target in the evaluation stage to unlock a simulated funded account." [P10]
  - "Then you will be given your Live account credentials." [P14]
  - note: Conflict between homepage ('Live') and FAQ ('simulated'). No rule on what happens after N payouts was found.
- `funded_drawdown_amount` = **1750** (verified)
  - "$50K: 3.5% ($1,750)" [P3]
- `funded_drawdown_type` = **eod_trailing** (verified)
  - "Drawdown Type EOD Trailing" [P14]
- `funded_drawdown_lock` = **starting balance after first withdrawal (or at +$1,750)** (verified)
  - "- Max Drawdown: After first withdrawal, the max drawdown locks at the account’s starting balance." [P4]
- `payout_balance_consequence` = **payout deducted from balance; floor locked at starting balance** (verified)
  - "- Max Drawdown Limit: Locked permanently at $100,000." [P4]
  - note: From the $100K worked example (balance $106,000 - $2,500 = $103,500); the 50K analogue is a $50,000 floor.
- `funded_daily_loss_limit` = **1000, soft breach** (verified)
  - "- Flex Funded Accounts: 2% across all account sizes" [P3]
- `funded_consistency_rule` = **40%, reset after each payout request** (verified)
  - "- Flex Funded Accounts: 40% consistency rule (no single day can account for more than 40% of total trading returns earned)." [P3]
- `funded_position_limit` = **3 minis / 30 micros; no scaling plan stated** (verified)
  - "Max Contracts 3 minis / 30 micros Consistency Rule 40%" [P14]
- `funded_monthly_fee` = **none** (verified)
  - "There are no ongoing fees or charges required to maintain your funded trader status." [P13]
- `payout_min` = **500** (verified)
  - "$50,000 Account: $500 minimum payout" [P4]
- `payout_cap` = **50% of cycle returns, capped at $2,000 per cycle; no lifetime cap stated** (verified)
  - "$50,000 Account → 50% of total trading returns, capped at $2,000 per cycle" [P4]
- `payout_frequency_gate` = **every 5 winning days of $150+; returns at least $500; 40% consistency** (verified)
  - "- Payout Requests: Can be made after every 5 winning days on your funded account." [P4]
  - "$50,000 Account: $150 winning day threshold" [P4]
- `payout_split` = **90/10 (add-on to 100%)** (verified)
  - "- Performance Split: Standard split is 90/10 (90% to trader). An optional add-on is available at checkout to increase the split to 100%." [P4]
  - note: Add-ons cost +15% each (+35% for all three) at checkout.
- `payout_processing_days` = **within 2 business days** (verified)
  - "- Processing Time: Payout requests are processed within 2 business days." [P4]
  - note: Paid via Rise.
- `payout_fee` = **not stated** (UNVERIFIED)
  - looked at: fq-flex-plan-payout-policy, fq-how-to-request-a-payout, fq-what-is-futureify-account-payment-struct, fut-home
- `payout_count_limit` = **not stated** (UNVERIFIED)
  - looked at: fq-flex-plan-payout-policy, fq-flex-plan-overview, fq-funded-account-parameters-overview
- `max_accounts` = **5 total (eval + funded + Direct); bundle discounts up to 5** (verified)
  - "Max Accounts 5 across eval + funded" [P14]
- `inactivity_rule` = **at least 1 trade every 14 calendar days, then 7-day grace before permanent closure** (verified)
  - "- Trading Requirement: You must place at least 1 trade every 14 calendar days across all Evaluation and Funded accounts." [P17]
  - "Inactivity Rule 1 trade every 3 weeks" [P14]
  - note: Homepage's 3 weeks = 2 weeks + 1 week grace.
- `copy_trading_terms` = **own accounts within Futureify, and from own accounts elsewhere; third-party copying prohibited** (verified)
  - "- Copying trades between your own active accounts within Futureify." [P6]
- `cross_account_hedging` = **prohibited** (verified)
  - "- Group Trading: Collaborating with other traders to execute identical or opposite strategies across different accounts is not allowed." [P7]
  - note: Plus Reverse Trading (screen).
- `news_trading_terms` = **allowed; large leveraged positions around major news prohibited** (verified)
  - "- High Leverage News Trading: Placing large, leveraged positions around major news events, akin to gambling without proper risk management." [P7]
- `automation_terms` = **permitted (no latency arbitrage, micro-scalping, glitch exploits or news hedging)** (verified)
  - "- Default Access: EA and automated trading capabilities are enabled by default across all account types. No prior permission or special setup request is required." [P9]
- `sizing_or_gambling_terms` = **account rolling and all-or-nothing prohibited** (verified)
  - "- Account Rolling: Taking extreme leverage positions without a plan or stop-loss, hitting the maximum loss, and then purchasing additional accounts to repeat the cycle, is strictly forbidden." [P7]
- `other_conduct_bearing` = **'tight brackets' to exploit fills prohibited; micro-scalping (under ~1 min, under 3 points / 10 ticks) prohibited; flat by 4:59 PM EST daily; one account per customer** (verified)
  - "- Exploiting Favorable Fills: Attempting to profit by exploiting the absence of slippage, using tight brackets, or manipulating order fills to gain an advantage is prohibited." [P7]
  - "- Tick or Micro Scalping: Taking trades with minimal movement, such as fewer than 10 ticks, without a clear plan, and opening and closing positions quickly to make small profits, is not allowed." [P7]
  - "You can start trading at 6 PM EST to begin a new trading day, but all trades must be closed by 4:59 PM EST each day." [P18]
  - note: A bracket design is allowed, but NQ brackets with very tight stops/targets (under 10 ticks, held seconds) fall inside the prohibited patterns. Terms PDF not read.
- `permitted_products` = **not listed on the pages read (CME rules referenced; MBT/MET/SIL ratios mentioned)** (UNVERIFIED)
  - looked at: fut-home, how, fq-what-is-the-max-position-limit, fq-account-parameters-overview, fq-what-are-the-trading-hours-at-futureify
  - note: The homepage names ES as an example; no instrument list was found.

### Funded Futures Network (`ffn`) -- PASS

**Pages quoted** (key: URL; article id; the page's own date as shown; all read 2026-11-15)

- [P1] https://fundedfuturesnetwork.com/
- [P2] https://fundedfuturesnetwork.com/faq


Official domains: fundedfuturesnetwork.com, app.fundedfuturesnetwork.com, fundedfuturesnetwork.zendesk.com, app.termly.io (Terms of Use host linked from the site). Read 2026-11-15.
Plan captured: STEADY 50K.
Verdict: **PASS** -- STEADY 50K: EOD funded drawdown locking at start + $100 and no funded consistency; 5 Sim Funded accounts at once; FAQ forbids nothing about hand-entered bracket trading (resting orders must be cancelled around T1 news). Caveat: the full rules page (JavaScript) and the Zendesk help centre (Cloudflare) were unreadable.

Unreadable (not worked around):
- https://app.fundedfuturesnetwork.com/nexus/rules -- JavaScript app shell (no server-side text; rules load from an API). WebFetch saw only the title 'Funded Futures Network - Account Portal'. The app bundle (/nexus/assets/index-CQzPKfg5.js, saved as raw/ffn/rules-js) holds no rules text.
- https://fundedfuturesnetwork.zendesk.com/hc/en-us -- 403 Cloudflare bot challenge; not worked around
- https://fundedfuturesnetwork.zendesk.com/hc/en-us/articles/47386113405083 -- 403 Cloudflare bot challenge (Country Restrictions & Product List); WebFetch returned 403 too
- https://app.termly.io/policy-viewer/policy.html?policyUUID=fb76d3c3-5faa-4e01-99e0-ba7b7033df92 -- Terms of Use: JavaScript policy viewer, no server-side text

Plans seen:
- STEADY 50K (one-time fee): drawdown EOD trailing $2,000 (eval and funded); funded locks at starting balance + $100; consistency evaluation 52%, funded none ('No consistency rule'); payouts gated by 5 winning days and a net rule
  - ""friendly": "$50,000", "funded": [{"label": "Payout Frequency", "value": "Same day"}, {"label": "Profit Split", "value": "90%"}, {"label": "Consistency", "value": "No consistency rule"}" [P1]
- MAX Standard 50K (one-time fee): drawdown EOD trailing $2,000 (eval and funded); funded locks at starting balance + $100; daily loss limit $1,250; consistency evaluation 40%, funded 40% (checked at payout request; resets per account after each payout)
  - "provided you have met your account minimum threshold and are within the consistency rule (40% for OG and Standard MAX funded accounts, 25% for Express MAX funded accounts)." [P2]

**Screen**

- `drawdown_eval` = **eod_trailing $2,000** (verified)
  - "| Evaluation Drawdown | End Of Day | Unrealized" [P1]
  - ""50000": {"2d": {"billing": "one_time", "evaluation": [{"label": "Profit Target", "value": "$3,000"}, {"label": "Drawdown Type", "value": "EOD (End of Day)"}, {"label": "Max Drawdown", "value": "$2,000"}" [P1]
  - note: First quote is the homepage comparison row (header '| Feature | FFN | Others'); second is the homepage plan-picker data (page script) for the $50K STEADY account, sku 502D.
- `drawdown_funded` = **eod_trailing $2,000, locks at starting balance + $100** (verified)
  - "{"label": "Consistency", "value": "No consistency rule"}, {"label": "Drawdown Type", "value": "EOD (End of Day)"}, {"label": "Max Drawdown", "value": "$2,000"}, {"label": "Drawdown Lock", "value": "Locks at starting balance + $100"}" [P1]
  - "| Funded Drawdown | Static +100 | Intraday" [P1]
  - note: Comparison row 'Static +100' read as: EOD trailing until it locks (static) at start + $100. The FAQ points to a video for the trailing mechanics; the rules page (JS) was unreadable.
- `consistency_eval` = **52% (STEADY); 40% (MAX Standard)** (verified)
  - "{"label": "Activation Fee", "value": "None"}, {"label": "Max Contracts", "value": "4 Mini (40 Micros)"}, {"label": "Consistency", "value": "52%"}" [P1]
  - note: What the 52% gates (passing, presumably) and its exact formula are not stated on any readable page.
- `consistency_funded` = **none on STEADY funded** (verified)
  - ""friendly": "$50,000", "funded": [{"label": "Payout Frequency", "value": "Same day"}, {"label": "Profit Split", "value": "90%"}, {"label": "Consistency", "value": "No consistency rule"}" [P1]
  - note: The FAQ's payout answer lists funded consistency only for OG/Standard MAX (40%) and Express MAX (25%); STEADY is not mentioned there.
- `max_funded_accounts` = **5 active Sim Funded accounts at once; evaluations unlimited** (verified)
  - "There is no limit on how many evaluations you can buy or hold. You can have up to 5 active Sim Funded accounts at one time." [P2]
  - note: Per person or household is not stated on any readable page. A pass made while holding 5 waits in a queue.
- `copy_trading` = **allowed up to 5 accounts; no more than 5 accounts trading the same product simultaneously** (verified)
  - "You can copy trade a maximum of 5 accounts. You cannot have more than 5 accounts trading at one time on the same product simultaneously." [P2]
- `opposite_positions` = **prohibited within and across the ES/MES/NQ/MNQ family, any size** (verified)
  - "When you are in the Evaluation, Exhibition and Funded stage, hedging is considered a broken rule making you no longer eligible for funding." [P2]
  - "ES, MES, NQ and MNQ count as one family in any size." [P2]
- `news` = **evaluation: allowed; Exhibition/Funded: must be flat (no positions or resting orders) 1 minute before to 1 minute after T1 events (FOMC, FOMC minutes, NFP, CPI) per the Financial Juice calendar** (verified)
  - "You must be flat, meaning no positions or orders (including limit orders) can be open 1 minute before and 1 minute after the release." [P2]
  - "For All Traders in Exhibition and Funded Accounts: FOMC Meetings (Wednesdays 2pm ET), FOMC Minutes, Employment Report (NFP), CPI" [P2]
  - note: A resting bracket counts as not flat: brackets must be cancelled before T1 events.
- `automation` = **automated trading allowed at FFN's discretion; HFT bots and simulator exploitation lose the account** (verified)
  - "Automated trading is allowed but at the discretion of FFN. Any traders implementing HFT trading bots or attempting to exploit the simulated environment will lose access to their account." [P2]
  - note: Hand entry is unaffected.
- `sizing_gambling` = **no gambling/maximum-size/minimum-hold rule found on readable pages; all positions flat by 4:50 PM ET** (UNVERIFIED)
  - "No. ALL positions opened by our traders MUST be closed by 04:50pm EST." [P2]
  - looked at: https://fundedfuturesnetwork.com/, https://fundedfuturesnetwork.com/faq, https://fundedfuturesnetwork.com/accounts (the rules page and Terms were unreadable)

**Terms (`terms`)**

- `eval_profit_target` = **3000** (verified)
  - ""50000": {"2d": {"billing": "one_time", "evaluation": [{"label": "Profit Target", "value": "$3,000"}" [P1]
  - note: All 'terms' values marked from home.txt come from the homepage plan-picker data for '$50K STEADY Account' (sku 502D); the same block appears on /accounts.
- `eval_drawdown_amount` = **2000** (verified)
  - ""sku": "502D", "tier": "$50K STEADY Account", "trailingMaxDrawdown": 2000}" [P1]
- `eval_drawdown_type` = **eod_trailing** (verified)
  - "STEADY EOD · 2 days to pass One-time" [P1]
- `eval_drawdown_lock` = **not stated for the evaluation** (UNVERIFIED)
  - looked at: https://fundedfuturesnetwork.com/, https://fundedfuturesnetwork.com/accounts, https://fundedfuturesnetwork.com/faq
- `eval_daily_loss_limit` = **none** (verified)
  - "{"label": "Max Drawdown", "value": "$2,000"}, {"label": "Daily Loss Limit", "value": "None"}, {"label": "Min. Trading Days", "value": "2 days ($150+ each)"}" [P1]
- `eval_consistency_rule` = **52%** (verified)
  - "{"label": "Max Contracts", "value": "4 Mini (40 Micros)"}, {"label": "Consistency", "value": "52%"}" [P1]
  - note: Formula and what it gates not stated on readable pages.
- `eval_min_days` = **2 days of $150+ each** (verified)
  - "{"label": "Min. Trading Days", "value": "2 days ($150+ each)"}, {"label": "Reset Fee", "value": "$180"}" [P1]
- `eval_position_limit` = **4 minis / 40 micros** (verified)
  - "{"label": "Activation Fee", "value": "None"}, {"label": "Max Contracts", "value": "4 Mini (40 Micros)"}, {"label": "Consistency", "value": "52%"}" [P1]
- `eval_fee` = **$229 one-time (list price)** (verified)
  - ""minimumDays": 2, "price": 229, "profitTarget": 3000," [P1]
  - note: Promotion today: 'Trading Steady? It's 50% off on Onyx. A 50K Steady is $114.50.' Optional 'Skip the Eval' add-on $499. Commissions and fees are charged to the evaluation balance (FAQ).
- `eval_reset_fee` = **180** (verified)
  - "{"label": "Min. Trading Days", "value": "2 days ($150+ each)"}, {"label": "Reset Fee", "value": "$180"}" [P1]
- `activation_fee` = **0** (verified)
  - "Evaluation price shown. No hidden fees. No activation fee after passing." [P1]
- `eval_count_limit` = **unlimited** (verified)
  - "Yes. There is no limit on how many evaluations you can buy or hold." [P2]
- `eval_time_limit` = **not stated** (UNVERIFIED)
  - looked at: https://fundedfuturesnetwork.com/, https://fundedfuturesnetwork.com/accounts, https://fundedfuturesnetwork.com/faq
- `funded_type` = **Sim Funded (simulated); Live Review after 4 payouts on one account or 10 since the last review, which closes all sim accounts; FFN Institution (live) starts with $3,000 of FFN capital, 90/10 split, no consistency** (verified)
  - "{"label": "Live Review", "value": "After 4 payouts on one account or 10 since the last live review"}, {"label": "On Live Review", "value": "All sim accounts close"}" [P1]
  - "Traders promoted to the FFN Institution start with $3,000 of real FFN capital, which can never be withdrawn." [P2]
  - note: The FAQ also mentions an 'Exhibition' stage that 'MAX accounts skip'; whether STEADY passes through an Exhibition account before Sim Funded is not stated on readable pages (the $625 'Exhibition' reset equals the STEADY 'Funded Reset Fee').
- `funded_drawdown_amount` = **2000** (verified)
  - "{"label": "Consistency", "value": "No consistency rule"}, {"label": "Drawdown Type", "value": "EOD (End of Day)"}, {"label": "Max Drawdown", "value": "$2,000"}, {"label": "Drawdown Lock", "value": "Locks at starting balance + $100"}" [P1]
- `funded_drawdown_type` = **eod_trailing** (verified)
  - "{"label": "Consistency", "value": "No consistency rule"}, {"label": "Drawdown Type", "value": "EOD (End of Day)"}" [P1]
- `funded_drawdown_lock` = **locks at starting balance + $100 ($50,100)** (verified)
  - "{"label": "Drawdown Lock", "value": "Locks at starting balance + $100"}, {"label": "Daily Loss Limit", "value": "None"}, {"label": "Buffer", "value": "$2,000"}, {"label": "Winning Days per Payout", "value": "5"}" [P1]
- `payout_balance_consequence` = **withdrawals only above the account minimum threshold ($52,000 for 50K; need >= $500 above it); net rule: balance must exceed the level after the last payout; floor position after payout not stated** (verified)
  - "Account Minimum Thresholds (your balance must be at least $500 above the threshold to qualify for a withdrawal):" [P2]
  - "50K Account: $52,000" [P2]
  - "{"label": "Net Rule", "value": "Balance must exceed the level after your last payout"}" [P1]
  - note: With the floor locked at $50,100 and payouts only from balance above $52,000, a $1,900 cushion remains after any payout (arithmetic; the threshold list is the FAQ's generic one, not STEADY-specific). The plan data also lists 'Buffer' $2,000.
- `funded_daily_loss_limit` = **none** (verified)
  - "{"label": "Drawdown Lock", "value": "Locks at starting balance + $100"}, {"label": "Daily Loss Limit", "value": "None"}, {"label": "Buffer", "value": "$2,000"}" [P1]
- `funded_consistency_rule` = **none** (verified)
  - ""friendly": "$50,000", "funded": [{"label": "Payout Frequency", "value": "Same day"}, {"label": "Profit Split", "value": "90%"}, {"label": "Consistency", "value": "No consistency rule"}" [P1]
- `funded_position_limit` = **scaling: $0-1,000 profit 2 minis/20 micros; $1,001-2,000 3/30; $2,001+ 4/40** (verified)
  - ""scaling": [{"label": "2 Mini (20 Micros)", "value": "$0 - $1,000 (Profit)"}, {"label": "3 Mini (30 Micros)", "value": "$1,001 - $2,000 (Profit)"}, {"label": "4 Mini (40 Micros)", "value": "$2,001+ (Profit)"}], "sku": "502D"" [P1]
- `funded_monthly_fee` = **none stated for Sim Funded; professional market-data fees apply only to Institution accounts** (verified)
  - "Professional market data fees apply to FFN Institution accounts only and do not apply to Sim Funded accounts." [P2]
- `payout_min` = **500** (verified)
  - "{"label": "Winning Days per Payout", "value": "5"}, {"label": "Minimum Payout", "value": "$500"}" [P1]
- `payout_cap` = **$1,000 per payout (payouts 1-3), $1,250 (payout 4+); $10,000 per payout cumulative across all of a user's accounts** (verified)
  - "{"label": "Minimum Payout", "value": "$500"}, {"label": "Payout Cap", "value": "$1,000 (payouts 1–3), $1,250 (payout 4+)"}, {"label": "Payout Cap per User", "value": "$10,000 per payout, all accounts"}, {"label": "Net Rule"" [P1]
  - "This amount is cumulative across all of your accounts and you are not permitted to request several withdrawals across several accounts if they are copy traded." [P2]
  - note: The FAQ clause restricts withdrawing from several copy-traded accounts; its exact scope (same payout window?) is unclear. Lifetime: capped in practice by the Live Review after 4 payouts on one account.
- `payout_frequency_gate` = **5 winning days per payout (threshold not stated) plus the net rule; requestable the same day eligible** (verified)
  - "{"label": "Buffer", "value": "$2,000"}, {"label": "Winning Days per Payout", "value": "5"}" [P1]
  - note: Homepage card note 'Choose your payout schedule later.' suggests selectable schedules not documented on readable pages.
- `payout_split` = **90% (STEADY Sim Funded)** (verified)
  - ""friendly": "$50,000", "funded": [{"label": "Payout Frequency", "value": "Same day"}, {"label": "Profit Split", "value": "90%"}" [P1]
  - note: CONFLICT: the FAQ says the Sim Funded Pro account 'has an 80/20 profit split' (written for MAX accounts); the STEADY plan data says 90%.
- `payout_processing_days` = **same day** (verified)
  - ""friendly": "$50,000", "funded": [{"label": "Payout Frequency", "value": "Same day"}" [P1]
  - note: Payout methods: 'PayPal, Rise, or Wise.' (FAQ).
- `payout_fee` = **not stated** (UNVERIFIED)
  - looked at: https://fundedfuturesnetwork.com/faq, https://fundedfuturesnetwork.com/payouts, https://fundedfuturesnetwork.com/
- `payout_count_limit` = **4 payouts on one account (or 10 overall since the last review) trigger a Live Review that closes all sim accounts** (verified)
  - "{"label": "Live Review", "value": "After 4 payouts on one account or 10 since the last live review"}" [P1]
- `max_accounts` = **5 Sim Funded at once; unlimited evaluations; passes beyond 5 queue** (verified)
  - "If you pass an evaluation while you already hold 5, the pass waits in your queue and its Sim Funded account activates when one of your 5 slots opens." [P2]
  - note: Household scope UNVERIFIED (rules page unreadable).
- `inactivity_rule` = **not stated** (UNVERIFIED)
  - looked at: https://fundedfuturesnetwork.com/faq, https://fundedfuturesnetwork.com/accounts
- `copy_trading_terms` = **allowed, max 5 accounts; >5 accounts on the same product at once makes all of them ineligible** (verified)
  - "If that happens, none of the accounts that took that trade will be eligible for funding." [P2]
- `cross_account_hedging` = **prohibited: long and short at once in the same product or across the ES/MES/NQ/MNQ family (stated without restricting it to one account)** (verified)
  - "Hedging means holding a long and a short position at the same time in the same product, or across the ES and NQ index futures." [P2]
  - note: The app bundle contains a 'HEDGE_ACROSS_ACCOUNTS' block code, consistent with cross-account enforcement.
- `news_trading_terms` = **T1 events (FOMC, FOMC minutes, NFP, CPI): flat incl. no resting orders from 1 min before to 1 min after, on Exhibition and Funded; other news allowed** (verified)
  - "Having a resting order on your chart is not considered flat." [P2]
  - "You must make use of Financial Juice news calendar: no other news calendar is accepted." [P2]
- `automation_terms` = **allowed at FFN's discretion; HFT bots prohibited** (verified)
  - "Automated trading is allowed but at the discretion of FFN." [P2]
- `sizing_or_gambling_terms` = **not stated on readable pages** (UNVERIFIED)
  - looked at: https://fundedfuturesnetwork.com/faq, https://fundedfuturesnetwork.com/accounts, https://fundedfuturesnetwork.com/
- `other_conduct_bearing` = **flat by 4:50 PM ET (overnight session trading allowed from 6 PM ET); closing an account forfeits its profits** (verified)
  - "No. ALL positions opened by our traders MUST be closed by 04:50pm EST." [P2]
  - "If you choose to close your accounts, you will forfeit your profits on any accounts closed." [P2]
- `permitted_products` = **micros MES, MNQ, M2K, MYM, MCL, MBT, MET stated; full list in an unreadable help-centre article** (verified)
  - "Yes, you may trade E-micro products such as MES, MNQ, M2K, MYM, MCL, MBT, and MET." [P2]
  - note: NQ and ES themselves are implied by the hedging rule ('ES, MES, NQ and MNQ count as one family') but the product list is in the Cloudflare-blocked Zendesk article.

### My Funded Futures (MyFundedFutures, MFFU) (`mffu`) -- PASS

**Pages quoted** (key: URL; article id; the page's own date as shown; all read 2026-11-15)

- [P1] https://help.myfundedfutures.com/en/articles/16158363-rapid-eod-50k-a-comprehensive-look; id 16158363; page date: August 24, 2026
- [P2] https://help.myfundedfutures.com/en/articles/18337038-rapid-eod-with-dll-a-detailed-look; id 18337038; page date: Updated this week
- [P3] https://help.myfundedfutures.com/en/articles/13134709-rapid-plan-50k-a-comprehensive-look; id 13134709; page date: August 24, 2026
- [P4] https://help.myfundedfutures.com/en/articles/17573707-comprehensive-look-into-redesigned-pro-plan; id 17573707; page date: October 14, 2026
- [P5] https://help.myfundedfutures.com/en/articles/14290805-builder-plan-50k-a-comprehensive-guide; id 14290805; page date: Updated over 3 weeks ago
- [P6] https://help.myfundedfutures.com/en/articles/17589665-studio-plans-a-comprehensive-guide; id 17589665; page date: Updated over 2 weeks ago
- [P7] https://help.myfundedfutures.com/en/collections/16162798-legacy-plans; id 16162798
- [P8] https://myfundedfutures.com/plans/rapid-eod
- [P9] https://help.myfundedfutures.com/en/articles/11994562-consistency-rule-at-my-fundedfutures; id 11994562; page date: September 25, 2026
- [P10] https://help.myfundedfutures.com/en/articles/16498635-moving-from-evaluation-to-sim-funded-account; id 16498635; page date: September 4, 2026
- [P11] https://myfundedfutures.com/terms; id s.23.1.3
- [P12] https://help.myfundedfutures.com/en/articles/10771500-copy-trading-at-myfundedfutures; id 10771500; page date: August 24, 2026
- [P13] https://myfundedfutures.com/terms; id s.23.1.3.3
- [P14] https://help.myfundedfutures.com/en/articles/8444599-fair-play-and-prohibited-trading-practices; id 8444599; page date: Updated over 2 weeks ago
- [P15] https://help.myfundedfutures.com/en/articles/12011241-hedging-what-you-should-know; id 12011241; page date: November 10, 2025
- [P16] https://help.myfundedfutures.com/en/articles/8230009-news-trading-policy; id 8230009; page date: August 31, 2026
- [P17] https://myfundedfutures.com/terms; id s.23.1.11
- [P18] https://myfundedfutures.com/plans/rapid
- [P19] https://help.myfundedfutures.com/en/articles/16596524-inactivity-rule-one-time-payment-model; id 16596524; page date: Updated over a week ago
- [P20] https://help.myfundedfutures.com/en/articles/13134718-understanding-rapid-live; id 13134718; page date: September 8, 2026
- [P21] https://help.myfundedfutures.com/en/articles/10244682-cross-instrument-policy; id 10244682; page date: August 24, 2026
- [P22] https://help.myfundedfutures.com/en/articles/13745661-payout-policy-overview-best-and-fastest-prop-firm-payouts; id 13745661; page date: August 25, 2026
- [P23] https://help.myfundedfutures.com/en/articles/12109396-comprehensive-faq-live-accounts-at-myfunded-futures; id 12109396; page date: November 10, 2025
- [P24] https://help.myfundedfutures.com/en/articles/9558251-permitted-times-to-trade; id 9558251; page date: August 24, 2026
- [P25] https://help.myfundedfutures.com/en/articles/9698984-2-price-limit-rule; id 9698984; page date: August 24, 2026
- [P26] https://help.myfundedfutures.com/en/articles/9735811-futures-instrument-list; id 9735811
- [P27] https://myfundedfutures.com/plans/pro
- [P28] https://help.myfundedfutures.com/en/articles/8694840-balancing-freedom-and-responsibility-consistency-for-sim-funded-pro-accounts-at-mffu; id 8694840; page date: August 24, 2026
- [P29] https://myfundedfutures.com/terms


Official domains: myfundedfutures.com, help.myfundedfutures.com. Read 2026-11-15.
Plan captured: Rapid EOD 50K (default, no DLL) in `terms`; Pro 50K also passes on both legs and differs materially (14-day first payout, $1,000 minimum, 80/20, MLL static after first payout, $100K per-user cap), so it is captured in `terms_pro50k`. No plan named 'Core' appears on any page read..
Verdict: **PASS** -- Rapid EOD 50K: EOD trailing funded drawdown (locks +$100), no funded consistency, up to 3 funded accounts (5 across 25K/50K); hand-entered one-position bracket trading on NQ/MNQ is not forbidden (caveats: no 'tight brackets' exploiting sim fills, T1 news blackout on funded, no hedging, copy-trading help/ToS tension).

Unreadable (not worked around):
- https://myfundedfutures.com/challenge -- 200 but empty shell (checkout app, no server-side text); not needed, not pursued (checkout is off-limits)

Plans seen:
- Rapid EOD 50K (default, no DLL): drawdown EOD trailing $2,000 in evaluation and sim funded; sim funded MLL locks at +$100 (account starts at $0); consistency evaluation 30%, funded none
  - "| Drawdown Type | End-of-Day (EOD) Trailing" [P1]
- Rapid EOD 50K with DLL add-on: drawdown same as Rapid EOD 50K, plus a $1,000 soft-pause daily loss limit in both stages; consistency evaluation 30%, funded none
  - "Rapid EOD is now available in two versions: the Default (No DLL) version and the Add-on (DLL) version. It is the same plan with the same rules, except that the DLL version adds a Daily Loss Limit." [P2]
- Rapid 50K (intraday): drawdown evaluation EOD $2,000; sim funded intraday trailing $2,000 from equity high-water mark, locks at $100; consistency evaluation 50%, funded none
  - "Drawdown Type: Intra-day trailing" [P3]
- Pro 50K (redesigned Pro, incl. Pro 50K One Day add-on): drawdown EOD trailing $2,000 evaluation and sim funded; after first payout MLL moves to $50,100 and stays static; consistency evaluation 50% (One Day add-on: none, $4,000 target), funded none (but a discretionary 'Consistent Trading Policy')
  - "| Maximum Loss Limit (MLL) | After first payout, MLL moves to $50,100 and remains static. | After first payout, MLL moves to $100,100 and remains static. | After first payout, MLL moves to $150,100 and remains static." [P4]
- Builder 50K (Default $2,000 MLL / Add-On $1,500 MLL): drawdown EOD trailing, locks at +$100; consistency evaluation none, funded 50% per payout cycle; only ONE Builder sim funded account per user -> fails the several-accounts leg
  - "| Active Accounts Allowed | 1 Builder Account per user | 1 Builder Account per user" [P5]
- Studio #001/#002/#003 ($10K/$20K/$5K; no 50K size): drawdown static MLL; consistency evaluation none, funded none; one Studio account at a time; micros only; Hyperprop only
  - "No. One active Studio account at a time — either Evaluation or Sim Funded." [P6]
- Flex 50K (legacy): drawdown not screened: filed under the help centre's 'Legacy Plans' collection; consistency evaluation not read, funded not read
  - "Flex Plan - $50,000 / A Comprehensive Guide" [P7]

**Screen**

- `drawdown_eval` = **eod_trailing ($2,000)** (verified)
  - "| Maximum Loss Limit (EOD) | $2,000" [P1]
  - "EOD drawdown at both stages. No daily loss limit. 90/10 split with daily payouts." [P8]
  - note: Rapid EOD 50K.
- `drawdown_funded` = **eod_trailing ($2,000), locks at +$100 (sim funded starts at $0)** (verified)
  - "| Drawdown Type | End-of-Day (EOD) Trailing" [P1]
  - "Once your trailing Max Loss reaches $100, it locks there." [P1]
  - note: Contrast: the plain Rapid plan trails intraday at the sim funded stage.
- `consistency_eval` = **30% (Rapid EOD); exceeding it does not breach, it delays passing** (verified)
  - "| Consistency | 30% (Eval Only)" [P1]
  - "Exceeding the consistency targets does not breach the account." [P9]
- `consistency_funded` = **none** (verified)
  - "Consistency Requirement: None (you don't need to meet a consistency rule to get paid)." [P1]
- `max_funded_accounts` = **3 Rapid EOD 50K sim funded accounts (plan-specific cap); 5 in total across $25K/$50K plans; 10 active evaluations; per verified individual** (verified)
  - "| Max # of Funded Accounts | Three (3)" [P1]
  - "Rapid EOD $50K: Maximum of 3 Sim-Funded Accounts" [P10]
  - "Traders may hold a maximum of 10 active Evaluation Accounts at any given time." [P10]
  - "While Users may lawfully purchase and maintain multiple evaluation or funded accounts within the Account Limits published by the Company, all such accounts must belong to the same verified individual." [P11]
  - note: Per user (verified individual); no household rule seen. Once any account goes Live, all sim accounts are suspended (see terms.funded_type).
- `copy_trading` = **allowed across own accounts per the help centre; Terms of Use s.23.1.3.3 prohibits using multiple accounts to copy/mirror 'in a manner that provides an unfair advantage or manipulates simulated results' -- CONFLICT** (verified)
  - "MyFunded Futures allows copy trading across all account types." [P12]
  - "Users remain solely responsible for ensuring their copy trading activities comply with all applicable terms of service." [P12]
  - "23.1.3.3. use multiple accounts to hedge, mirror, copy, or coordinate trades in a manner that provides an unfair advantage or manipulates simulated results;" [P13]
  - "Traders are not permitted to copy trade one another by entering, exiting or cancelling trade positions." [P14]
  - note: Re-read 2026-11-15: both texts stand. The help article (Aug 24 2026) is unconditional and names Tradesyncer / the Tradovate group copier; the Terms clause is qualified ('in a manner that provides an unfair advantage or manipulates simulated results'), so plain copying of one's own hand-entered trades is not on its face prohibited, but the qualifier is discretionary. Terms s.1.6 says the Terms prevail over incorporated documents in a conflict. Copying between different traders is prohibited.
- `opposite_positions` = **prohibited (hedging of any kind, same underlying incl. NQ vs MNQ; Terms forbid using multiple accounts to hedge)** (verified)
  - "MyFundedFutures prohibits hedging of any kind. Hedging is defined as a trader entering both buy and sell positions on the same underlying asset, at the same time." [P15]
  - "● Collaborative Trading: Collaborating with others to execute identical or opposite strategies across unconnected accounts is prohibited." [P14]
  - note: The hedging article permits hedging through different unrelated assets but discourages relying on it.
- `news` = **Rapid EOD sim funded: no positions or orders 2 minutes before/after Tier 1 releases (FOMC, FOMC minutes, Employment Report, CPI); evaluation: T1 allowed; all accounts: no straddle/strangle news-burst strategies** (verified)
  - "No T1 news trading is not allowed on this Sim Funded account." [P1]
  - "No positions or orders (including limit orders) can be open 2 minutes before and after the release." [P16]
  - "For All Traders: FOMC Meetings, FOMC Minutes, Employment Report, CPI" [P16]
  - "Utilizing strategies that exploit immediate news bursts, such as straddles or strangles." [P16]
  - note: The Rapid EOD article's sentence is a double negative ('No T1 news trading is not allowed'); its table row says T1 News Trading 'No' on sim funded and the News policy lists 'Rapid Sim Funded' as restricted, so the intent is clearly 'not allowed'. The news policy also has a general 'Ensuring no open positions or orders are active in the order book 2 minutes before and after any data release' under Standard Trading Protocols for all releases -- broader than T1; ambiguous.
- `automation` = **allowed (own automated strategies) if they do not exploit simulated fills; HFT not allowed. Hand entry is unaffected.** (verified)
  - "High-frequency Trading is not allowed on our plans." [P14]
  - "Traders may make use of automated trading strategies tailored to their own specific settings so long as these automated tools do not aim to exploit the favorable fills offered in the Simulated Environment." [P14]
- `sizing_gambling` = **contract cap 3 minis / 30 micros combined (exceeding can breach); 'tight brackets to gain from favorable fills' prohibited; Terms catch-all on 'high-risk' behaviour; positions auto-closed 4:10 PM ET** (verified)
  - "Exceeding a total of 3 minis or its equivalent in micros (30 micros) can result in a breach of the trading account." [P1]
  - "● Slippage and Bracket Usage: Exploiting the absence of slippage and utilizing tight brackets to gain from favorable fills are not permitted." [P14]
  - "23.1.11. Any other type of behavior that the Company deems, in its sole and reasonable discretion, to be unlawful, unethical, deceptive, manipulative, high-risk, or otherwise posing an undue risk to the Company, other users, or the stability, security, or integrity of the Platform or Services." [P17]
  - note: Bracket orders as such are not prohibited; only 'tight brackets' used to exploit sim fills. A stop/target bracket sized to the strategy's normal distances should be fine, but 'tight' is undefined. No gambling/all-in rule on Rapid EOD; the Pro plan has a separate discretionary Consistent Trading Policy (see terms_pro50k).

**Terms (`terms`)**

- `eval_profit_target` = **3000** (verified)
  - "| Profit Target | $3,000" [P1]
- `eval_drawdown_amount` = **2000** (verified)
  - "| Maximum Loss Limit (EOD) | $2,000" [P1]
- `eval_drawdown_type` = **eod_trailing** (verified)
  - "EOD drawdown at both stages. No daily loss limit. 90/10 split with daily payouts." [P8]
- `eval_drawdown_lock` = **UNVERIFIED (plan-page data suggests the evaluation MLL is capped at $50,100 = start + $100)** (UNVERIFIED)
  - ""profitTarget":3000,"maxDrawdown":2000,"maxDrawdownLimit":50100" [P8]
  - "Your maximum drawdown will now lock at +$100 after the drawdown % + $100 has been reached." [P10]
  - looked at: help articles 16158363, 18337038, 11802636, 8348565, 16498635; plan page /plans/rapid-eod
  - note: No page states an evaluation lock in words. The first quote is a machine data field in the plan page's embedded script (not a statement); the second ('will now lock' on moving to sim funded) reads as if the lock is a sim-funded feature. Treat as unknown.
- `eval_daily_loss_limit` = **none (default version); $1,000 soft pause if the DLL add-on is bought** (verified)
  - "A. No, there is no daily loss limit in the evaluation or sim funded stages of the Rapid EOD Plan." [P1]
  - "| Daily Loss Limit (DLL Version) | $500 (Soft Pause)* | $1,000 (Soft Pause)*" [P2]
- `eval_consistency_rule` = **30% of total evaluation profit from any single day; gates passing only (no breach)** (verified)
  - "This consistency rule means no single day's profit should exceed 30% or 50% of your total evaluation profits made." [P9]
  - "Traders who achieve more than the listed percentage amount of their total profit target in one day simply need to trade additional days until consistency is met." [P9]
  - note: Ambiguity: the rule says 'total evaluation profits made' but the example divides the profit TARGET ('Total profit target / 2 = Max Daily Profit'). For Rapid EOD 30% of $3,000 = $900 on the target reading.
- `eval_min_days` = **4** (verified)
  - "| Minimum Trading Days | 4 Days" [P1]
- `eval_position_limit` = **3 minis / 30 micros (combined)** (verified)
  - "| Max Contract | 3 mini / 30 micro" [P1]
- `eval_fee` = **275 USD one-time (list); 165 USD with the site-wide CLUB code (40% off) as served on 2026-11-15** (verified)
  - ""name":"My Funded Futures Rapid EOD Plan 50,000 Account","price":"275.00"" [P8]
  - ""accountSize":50000,"productId":93,"priceId":252,"priceCents":27500,"priceDiscountedCents":16500,"activationFeeCents":0,"couponActive":true,"couponCode":"CLUB"" [P8]
  - "One-time purchase, nothing to cancel." [P8]
  - note: Price is in the page's embedded product data (schema.org Offer + plan JSON), not in visible text for the 50K. Promotions change; the default is 'No DLL, at the updated price' (article 18337038). One-time model effective for purchases from August 25, 2026.
- `eval_reset_fee` = **UNVERIFIED (resets exist 'for a specific fee'; amount not stated)** (UNVERIFIED)
  - "On a Rapid Evaluation, breaching the max drawdown fails that evaluation, but you can reset it for a specific fee and start trading again." [P18]
  - looked at: /plans/rapid-eod, /plans/rapid, help 16596406 (resets vs renewals), 16158363, 18337038
  - note: Stated for Rapid (intraday) evaluations; Rapid EOD reset price not shown. Sim funded accounts cannot be reset.
- `activation_fee` = **0** (verified)
  - "There are no activation fees on this plan." [P1]
- `eval_count_limit` = **10 active evaluation accounts at any time** (verified)
  - "Evaluation Accounts: Up to 10 active accounts" [P10]
- `eval_time_limit` = **UNVERIFIED as a stated limit; one-time payment with no renewal cycle, subject to the 7-day inactivity rule** (UNVERIFIED)
  - "This update applies only to purchases made on or after August 25, 2026 — and for those new evaluations, there is no renewal cycle since the one-time payment model replaces recurring billing entirely." [P19]
  - looked at: help 16596524, 16596406, 16158363; terms; /plans/rapid-eod
  - note: No page says 'no time limit' in so many words.
- `funded_type` = **sim funded; Live via automatic transition on a $10,000 single-day net profit (excess that day forfeited) or Risk-team review; up to $5,000 of sim profit held as Reserve; while Live, all sim accounts are suspended and multiple transitioned Rapid accounts are merged into one Live account** (verified)
  - "Live transition on Rapid EOD 50k follows the same rules as standard Rapid 50k." [P1]
  - "Automatic Live transition occurs when you generate $10,000 in net profit within a single trading session. Upon meeting this criterion, immediate transition to Live account status is initiated, and any profit exceeding $10,000 for that trading day is forfeited." [P20]
  - "Up to $5,000 of Sim Funded profits are allocated to Reserve upon transition." [P20]
  - "All simulated trading accounts and additional purchases are suspended during Live account operation." [P20]
  - "Instead of multiple Live accounts, parameters are combined into one Live account." [P20]
  - note: Rapid Live (50K): $0 start, $2,000 EOD MLL stopping at $0, 90/10, daily payouts, 3 mini/30 micro per help article 13134718 -- but the /plans/rapid-eod Live table shows 4 / 40 for the 50K (conflict, Live only). A Live MLL breach starts a 21-day cooldown on Builder/Pro pages; for Rapid not stated.
- `funded_drawdown_amount` = **2000** (verified)
  - "| Maximum Drawdown (MLL) | $2,000" [P1]
- `funded_drawdown_type` = **eod_trailing** (verified)
  - "Your Max Loss trails upward each time your account closes at a new end-of-day high." [P1]
  - "It does not move intraday – only at the close of each trading session." [P1]
  - note: Whether intraday equity below the EOD-set floor breaches is not spelled out on the Rapid EOD page; the Builder page says 'Open equity losses are counted when determining whether your account has breached the rule at the end of the trading day.'
- `funded_drawdown_lock` = **locks at $100 (sim funded balance starts at $0, so +$100 above start)** (verified)
  - "Once your trailing Max Loss reaches $100, it locks there." [P1]
  - "| Initial Balance | $0" [P1]
- `payout_balance_consequence` = **UNVERIFIED in words for Rapid EOD; plan data flags the MLL moving to its +$100 lock on the first payout** (UNVERIFIED)
  - ""bufferAmount":2100,"fundedMaxDrawdownLimit":100,"moveMllToLockOnFirstPayout":true" [P8]
  - "On Rapid Sim Funded, once your balance is +$100 above your starting balance after your first payout, the floor locks and stops trailing upward permanently." [P18]
  - looked at: help 16158363, 18337038, 13745661, 11542406; /plans/rapid-eod
  - note: The second quote is for Rapid (intraday). The $2,100 buffer = MLL + $100, so a first payout taken from profit above the buffer leaves the balance above the $100 lock. Whether a payout may dip into the buffer is not stated.
- `funded_daily_loss_limit` = **none (default version); $1,000 soft pause with the DLL add-on, resets 6:00 PM ET** (verified)
  - "A. No, there is no daily loss limit in the evaluation or sim funded stages of the Rapid EOD Plan." [P1]
  - "The Daily Loss Limit resets daily at 6:00 PM ET." [P2]
- `funded_consistency_rule` = **none** (verified)
  - "Consistency Requirement: None (you don't need to meet a consistency rule to get paid)." [P1]
- `funded_position_limit` = **3 minis and/or 30 micros total; no scaling plan stated for Rapid EOD** (verified)
  - "You may trade up to 3 minis and/or 30 micros total." [P1]
  - "Orders that combine different instruments (e.g., 2 minis and 20 micros) may technically execute even if they exceed the overall limit (e.g., more than 2 contracts in total), but this is not permitted!" [P21]
  - note: The Cross Instrument article's example mentions a Rapid 50k 'scaling plan' starting at 2 contracts; that contradicts the current Rapid 50K page (5 minis / 50 micros, no scaling) and looks stale. Rapid EOD pages state no scaling.
- `funded_monthly_fee` = **none** (verified)
  - "| Recurring Costs | None | Monthly" [P8]
  - note: Row is 'MFFU Rapid EOD (50K) | Other Firm'; the first value is MFFU's.
- `payout_min` = **500** (verified)
  - "Minimum Payout Request: $500" [P1]
- `payout_cap` = **no cap per request/cycle; lifetime cap not stated** (verified)
  - "There is no cap on how much you can request per payout cycle." [P1]
  - note: Lifetime: UNVERIFIED (none stated for Rapid; the $10,000 single-day profit triggers automatic Live transition, which effectively bounds sim life).
- `payout_frequency_gate` = **first payout after $2,100 realized-profit buffer (and 24h after first trade); each later payout once net profit since last payout reaches $500; daily cadence; no consistency, no winning-day count** (verified)
  - "You must first build at least $2,100 in realized profits in the account before requesting your first payout." [P1]
  - "Payout Unlock Rule: Once the buffer clears, each payout after that unlocks once your net profit since your last payout reaches $500." [P1]
  - "First payout eligible 24 hours after first trade (buffer & minimum profit required)" [P22]
- `payout_split` = **90/10** (verified)
  - "Clearing the $2,100 buffer for your first payout, then reaching $500 in net profit since your last payout to unlock each payout after that, under the 90/10 split." [P1]
- `payout_processing_days` = **most approved instantly; manual review up to 6-12 business hours on weekdays (plan page says up to 24 business hours)** (verified)
  - "Payout processing time: Most payouts are approved instantly. If a manual review is required, processing may take up to 6 to 12 business hours on weekdays." [P22]
  - "A subset routed for manual review may take up to 24 business hours." [P8]
  - note: Minor conflict (12 vs 24 business hours). Paid via Riseworks (bank transfer or crypto); Plaid/ACH for US traders.
- `payout_fee` = **UNVERIFIED** (UNVERIFIED)
  - looked at: help 13745661, 11542406, 16158363; terms (no payout-fee clause found by search)
- `payout_count_limit` = **UNVERIFIED (none stated for Rapid EOD)** (UNVERIFIED)
  - looked at: help 16158363, 18337038, 13745661, 13134718
  - note: Builder caps at 5 sim payouts; Rapid pages state no count limit.
- `max_accounts` = **3 Rapid EOD 50K sim funded; at most 5 sim funded across all $25K/$50K plans (3 if any $100K/$150K held); 10 active evaluations** (verified)
  - "Only $25K/$50K Sim-Funded Accounts: Up to 5 active accounts (subject to plan-specific limits)" [P10]
  - "Rapid EOD $50K: Maximum of 3 Sim-Funded Accounts" [P10]
- `inactivity_rule` = **no trade for 7 consecutive calendar days -> account may be closed; on sim funded all profits forfeited** (verified)
  - "If a trader does not place a trade for 7 consecutive calendar days, the account could be closed. This includes simulated funded accounts." [P19]
  - "An inactivity breach on a Sim Funded account results in the forfeiture of all profits." [P19]
- `copy_trading_terms` = **help centre: allowed across all account types (Tradesyncer preferred); Terms 23.1.3.3: no using multiple accounts to mirror/copy in a manner that provides an unfair advantage -- see screen.copy_trading** (verified)
  - "MyFunded Futures allows copy trading across all account types." [P12]
  - "23.1.3.3. use multiple accounts to hedge, mirror, copy, or coordinate trades in a manner that provides an unfair advantage or manipulates simulated results;" [P13]
  - note: Conflict between official pages, quoted both. Hand-entering the same trade in several own accounts is 'copying' in substance; the help article permits it outright.
- `cross_account_hedging` = **prohibited** (verified)
  - "E-Mini and Micro NQ have the same underlying asset which is NQ (Nasdaq)." [P15]
  - "MyFunded Futures maintains a strict no-hedging policy. We do not allow any kind of hedging, whether you are a sim trader or live." [P23]
- `news_trading_terms` = **funded: flat and no orders from 2 min before to 2 min after T1 releases (FOMC meetings/minutes, Employment Report, CPI); evaluation: T1 allowed** (verified)
  - "All positions must be flattened at least two minutes prior to the scheduled ⁠T1 News event." [P16]
  - "| T1 News Trading | No" [P1]
- `automation_terms` = **own automated strategies allowed if not exploiting sim fills; HFT prohibited; live automated trading under CME guidelines** (verified)
  - "Traders may make use of automated trading strategies tailored to their own specific settings so long as these automated tools do not aim to exploit the favorable fills offered in the Simulated Environment." [P14]
  - note: Nothing on any page read requires or restricts hand entry; our trades are hand-entered either way.
- `sizing_or_gambling_terms` = **contract cap; no tight-bracket fill exploitation; no multiple same-price limit orders to manipulate fills; Terms catch-all on 'high-risk' behaviour** (verified)
  - "● Slippage and Bracket Usage: Exploiting the absence of slippage and utilizing tight brackets to gain from favorable fills are not permitted." [P14]
  - "● Order Placement: Simultaneously placing multiple limit orders at the same price to manipulate order fills is prohibited." [P14]
- `other_conduct_bearing` = **positions auto-closed 4:10 PM ET (no overnight); no trading within 2% of a CME price limit on sim funded/live; no gapped/illiquid-fill profiting; one device per trader, account owner only; Live MLL breach -> 21-day cooldown (Builder/Pro pages)** (verified)
  - "At MyFundedFutures, any open positions will be automatically closed at 4:10 PM EST on regular (non-holiday) trading days." [P24]
  - "To protect our firm and our traders, we do not allow market participation when a product is trading within 2% of a price limit." [P25]
  - "Each individual trader may not use the same device (tablet, phone or computer) as used by another trader." [P14]
  - note: The 2% rule article says equity overnight limits at 5% mean trading 'is suspended at MyFunded Futures' when within 2% of the 7% CME limit -- applies to NQ/MNQ.
- `permitted_products` = **CME Group (CME, CBOT, NYMEX, COMEX) listed futures in the simulated environment; NQ and MNQ listed** (verified)
  - "Permitted Instruments: Participants may trade, within the simulated environment only, standardized futures contracts listed on regulated U.S. exchanges, including those operated by CME Group (CME, CBOT, NYMEX, and COMEX)." [P8]
  - "| E-mini NASDAQ 100 | NQ | Sunday - Friday 17:00 - 16:00 CT Daily Break: 16:00 - 17:00 CT | 0.25 | $5 | $4.68" [P26]
  - "| Micro E-mini Nasdaq-100 | MNQ | Sunday - Friday 17:00 - 16:00 CT Daily Break: 16:00 - 17:00 CT | 0.25 | $0.50 | $1.90" [P26]
  - note: Instrument table header: 'Instrument Name | Code | Trading Hours | Tick Size | Tick Value | Total Cost Round Trip' -- round-trip cost NQ $4.68, MNQ $1.90.

**Terms (`terms_pro50k`)**

- `eval_profit_target` = **3000 (Pro 50K One Day add-on: 4000)** (verified)
  - "| Profit Target | $3,000 | $6,000 | $9,000 | $4,000" [P4]
  - note: Columns: Pro 50k | Pro 100k | Pro 150k | Pro 50k - One Day.
- `eval_drawdown_amount` = **2000** (verified)
  - "| Maximum Loss Limit (EOD) | $2,000 | $3,000 | $4,500 | $2,000" [P4]
- `eval_drawdown_type` = **eod_trailing** (verified)
  - "Pro uses end-of-day trailing drawdown in both eval and sim funded." [P27]
- `eval_drawdown_lock` = **UNVERIFIED** (UNVERIFIED)
  - looked at: help 17573707; /plans/pro
- `eval_daily_loss_limit` = **none** (verified)
  - "| Daily Loss Limit (DLL) | None | None | None | None" [P4]
- `eval_consistency_rule` = **50% (One Day add-on: none)** (verified)
  - "| Consistency | 50% | 50% | 50% | None" [P4]
- `eval_min_days` = **2 (One Day add-on: 1)** (verified)
  - "| Minimum Trading Days | 2 Days | 2 Days | 2 Days | 1 Day" [P4]
- `eval_position_limit` = **3 minis / 30 micros** (verified)
  - "| Scaling / Max Contacts | 3 mini / 30 micro | 6 mini / 60 micro | 9 mimi / 90 micro | 3 mini / 30 micro" [P4]
- `eval_fee` = **265 USD one-time (list); 159 USD with the CLUB code as served 2026-11-15** (verified)
  - ""name":"My Funded Futures Pro Plan 50,000 Account","price":"265.00"" [P27]
  - ""accountSize":50000,"productId":135,"priceId":177,"priceCents":26500,"priceDiscountedCents":15900" [P27]
  - note: One Day add-on price not read.
- `eval_reset_fee` = **UNVERIFIED** (UNVERIFIED)
  - looked at: /plans/pro, help 17573707
- `activation_fee` = **0** (verified)
  - "| Activation Fee | $0 | $0 | $0" [P4]
- `eval_count_limit` = **10 active evaluations (firm-wide)** (verified)
  - "Evaluation Accounts: Up to 10 active accounts" [P10]
- `eval_time_limit` = **UNVERIFIED as a stated limit (one-time payment; 7-day inactivity rule)** (UNVERIFIED)
  - looked at: help 16596524, 17573707
- `funded_type` = **sim funded; reviewed for Live after 3 consecutive payouts on the same Pro account, reaching the $100,000 payout cap, a $20,000 profit review trigger, or invitation; Live at Blue Row Capital, $0 start, $2,000 EOD trailing MLL, 2 contracts** (verified)
  - "Three (3) consecutive payouts on the same Pro account." [P4]
  - "Reaching the $100,000 payout cap. Profits above $100,000 are forfeited." [P4]
  - note: Plan page FAQ says live parameters include 'a daily loss limit, reduced contract limits, and a static drawdown floor', while the help article's Live table shows 'Max Loss Limit (EOD Trailing) | -$2,000' and DLL None: conflict on Live only.
- `funded_drawdown_amount` = **2000** (verified)
  - "| Maximum Loss Limit (EOD) | $2,000 | $3,000 | $4,500" [P4]
- `funded_drawdown_type` = **eod_trailing until first payout, then static** (verified)
  - "After your first approved payout, the MLL locks permanently at your starting balance plus $100 and stops trailing entirely." [P27]
- `funded_drawdown_lock` = **moves to $50,100 (start + $100) on the first payout and stays static** (verified)
  - "| Maximum Loss Limit (MLL) | After first payout, MLL moves to $50,100 and remains static. | After first payout, MLL moves to $100,100 and remains static. | After first payout, MLL moves to $150,100 and remains static." [P4]
- `payout_balance_consequence` = **first payout snaps the MLL up to $50,100 regardless of where it trailed; balance must stay above it** (verified)
  - "After your first approved payout, the MLL locks permanently at your starting balance plus $100 and stops trailing entirely." [P27]
- `funded_daily_loss_limit` = **none** (verified)
  - "| Daily Loss Limit (DLL) | None | None | None" [P4]
- `funded_consistency_rule` = **no numeric rule; discretionary 'Consistent Trading Policy' (no max size on every trade, no contract flipping, uniform sizing)** (verified)
  - "Once you're funded, there is no hard consistency rule." [P27]
  - "Avoidance of Maximum Contract Sizes: While we offer flexibility in choosing contract sizes, resist the urge to employ maximum or oversized contract sizes in every trade." [P28]
- `funded_position_limit` = **3 minis / 3 micros as printed (help article and plan page both); no scaling ('3 minis from day one')** (verified)
  - "| Scaling / Max Contacts | 3 mini / 3 micro | 6 mini / 6 micro | 9 mini / 9 micro" [P4]
  - "3 minis from day one on the $50K. No build-up required." [P27]
  - note: '3 micro' (not 30) is printed consistently for sim funded while the evaluation shows 3/30; possibly a typo but stated twice.
- `funded_monthly_fee` = **none (one-time payment)** (verified)
  - "No activation fee · One-time payment, no renewals" [P27]
- `payout_min` = **1000** (verified)
  - "| Minimum Payout Request | $1,000 | $1,000 | $1,000" [P4]
- `payout_cap` = **100,000 USD per user (sim); profits above it forfeited / routed to Live** (verified)
  - "| Maximum Payout (per user) | $100,000 | $100,000 | $100,000" [P4]
- `payout_frequency_gate` = **14 calendar days from first trade AND $2,100 buffer cleared; payout overview also says up to 60% may be withdrawn before the buffer clears (conflict)** (verified)
  - "| Qualification for Payouts | 14 calendar days from day of first trade. Buffer must be cleared | 14 calendar days from day of first trade. Buffer must be cleared | 14 calendar days from day of first trade. Buffer must be cleared" [P4]
  - "Withdrawal While in Buffer: You can withdraw up to 60% of your profits before fully clearing the buffer." [P22]
  - note: Conflict: the Pro article (Oct 14 2026, newer) says the buffer must be cleared; the payout overview (Aug 25 2026) allows 60% before clearing. 'Every 14 calendar days' per the overview vs '14 days from first trade' per the article.
- `payout_split` = **80/20** (verified)
  - "| Profit Split | 80/20 | 80/20 | 80/20" [P4]
- `payout_processing_days` = **most instant; manual review 6-12 business hours on weekdays** (verified)
  - "Payout processing time: Most payouts are approved instantly. If a manual review is required, processing may take up to 6–12 business hours on weekdays." [P22]
- `payout_fee` = **UNVERIFIED** (UNVERIFIED)
  - looked at: help 13745661, 11542406, 17573707
- `payout_count_limit` = **no fixed count; Live review after 3 consecutive payouts on the same account** (verified)
  - "| Live Transition Trigger | 3 consecutive payouts | 3 consecutive payouts | 3 consecutive payouts" [P27]
- `max_accounts` = **up to 5 sim funded across $25K/$50K plans (no Pro-specific cap listed); 10 evaluations** (verified)
  - "Traders may maintain up to 5 active Sim-Funded Accounts when holding only $25K and/or $50K account sizes." [P10]
  - note: The plan-specific list names Rapid EOD and Builder only; Pro 50K falls under the general 5.
- `inactivity_rule` = **7 consecutive calendar days without a trade -> may be closed; sim funded profits forfeited** (verified)
  - "If a User does not execute at least one (1) trade per seven (7) consecutive calendar day period, whether in an Evaluation Account or a Sim Trading Account, the Company may, in its sole discretion, deem the applicable account dormant, close it, and treat such closure as a breach of these Terms." [P29]
- `copy_trading_terms` = **as for Rapid EOD (help allows; Terms 23.1.3.3 qualifies)** (verified)
  - "MyFunded Futures allows copy trading across all account types." [P12]
- `cross_account_hedging` = **prohibited** (verified)
  - "MyFundedFutures prohibits hedging of any kind." [P15]
- `news_trading_terms` = **T1 news not allowed on Pro sim funded; allowed in evaluation** (verified)
  - "| T1 News Trading | Not Allowed | Not Allowed | Not Allowed" [P4]
- `automation_terms` = **as firm-wide (own automation allowed; HFT prohibited); Pro policy discourages HFT not aligned with stated approach** (verified)
  - "High-frequency Trading is not allowed on our plans." [P14]
- `sizing_or_gambling_terms` = **Consistent Trading Policy: uniform sizing, stops and targets; avoid max size every trade; no flipping; violations -> restrictions, penalties, termination** (verified)
  - "Uniform Position Sizing, Stops, and Targets: A consistent trading plan entails uniformity in position sizes, clear stop-loss and take-profit levels that align with your strategy, and well-defined targets for each trade." [P28]
  - note: Fixed-bracket, fixed-size trading is what this policy asks for.
- `other_conduct_bearing` = **Live breach -> Reserve covers negative balance, 21-day cooldown with no sim trading or purchases** (verified)
  - "The trader cannot buy new evaluations, resets or accounts." [P4]
- `permitted_products` = **CME Group futures; NQ/MNQ** (verified)
  - "Permitted Instruments: Participants may trade, within the simulated environment only, standardized futures contracts listed on regulated U.S. exchanges, including those operated by CME Group (CME, CBOT, NYMEX, and COMEX)." [P27]

### Phidias Propfirm (`phidias`) -- PASS

**Pages quoted** (key: URL; article id; the page's own date as shown; all read 2026-11-15)

- [P1] https://phidiaspropfirm.com/rules; id section 17 Premium Account Rules
- [P2] https://phidiaspropfirm.com/rules; id section 16 Fundamental Account Rules
- [P3] https://phidiaspropfirm.com/rules; id section 15 Express to Live Account Rules
- [P4] https://phidiaspropfirm.com/rules; id section 4 EOD Rules
- [P5] https://phidiaspropfirm.com/rules; id section 10 Consistency Policy
- [P6] https://phidiaspropfirm.com/rules; id section 11 30% Consistency Rule
- [P7] https://phidiaspropfirm.com/tou; id 3.1.1
- [P8] https://phidiaspropfirm.com/rules; id section 20 Account Limits & Copy Trading
- [P9] https://phidiaspropfirm.com/tou; id 3.1.3
- [P10] https://phidiaspropfirm.com/rules; id section 7 Economic News Trading
- [P11] https://phidiaspropfirm.com/rules; id section 1 Foreword
- [P12] https://phidiaspropfirm.com/rules; id section 17
- [P13] https://phidiaspropfirm.com/rules; id section 4
- [P14] https://phidiaspropfirm.com/rules; id section 17 Common Rules
- [P15] https://phidiaspropfirm.com/tou
- [P16] https://phidiaspropfirm.com/accounts
- [P17] https://phidiaspropfirm.com/rules; id section 3
- [P18] https://phidiaspropfirm.com/tou; id 3.1.2
- [P19] https://phidiaspropfirm.com/rules; id section 13
- [P20] https://phidiaspropfirm.com/rules; id section 19
- [P21] https://phidiaspropfirm.com/rules; id section 12
- [P22] https://phidiaspropfirm.com/tou; id 3.1.5
- [P23] https://phidiaspropfirm.com/tou; id 3.1.4
- [P24] https://phidiaspropfirm.com/rules; id section 11
- [P25] https://phidiaspropfirm.com/rules; id section 5
- [P26] https://phidiaspropfirm.com/
- [P27] https://phidiaspropfirm.com/rules; id section 20
- [P28] https://phidiaspropfirm.com/rules; id section 10
- [P29] https://phidiaspropfirm.com/rules; id section 8
- [P30] https://phidiaspropfirm.com/rules; id section 15


Official domains: phidiaspropfirm.com, helpcenter.phidiaspropfirm.com. Read 2026-11-15.
Plan captured: Premium 50K (in 'terms'); E2L 50K also passes (no consistency, static) and differs materially -- in 'terms_e2l'. Fundamental 50K = Premium with 10 days between payouts, fixed 80% split, no overnight, lower price..
Verdict: **PASS** -- Fundamental/Premium funded drawdown is EOD trailing (stops at $50,100) and E2L has no consistency rule at all; up to 5 per plan type / 15 funded per household; hand-entered bracket trading is not forbidden (automation is).

Unreadable (not worked around):
- https://helpcenter.phidiaspropfirm.com/help -- JavaScript-rendered Tickly portal ('Chargement…' only server-side); not needed: the one-page /rules and the /tou terms cover the screen

Plans seen:
- Premium 50K: drawdown EOD trailing $2,500; funded floor stops trailing at $50,100; consistency evaluation none, funded 30% max per day (CASH; gates withdrawals)
  - "Consistency (Funded CASH)30% max per day" [P1]
- Fundamental 50K: drawdown EOD trailing $2,500; funded floor stops at $50,100; consistency evaluation none, funded 30% max per day; 10 trading days between payouts; no overnight
  - "Consistency (Funded)30% max per day" [P2]
- Express to Live (E2L) 50K: drawdown static $650 (liquidation $49,350), eval and CASH; consistency evaluation none, funded none
  - "E2L 50K — Static Drawdown$650" [P3]

**Screen**

- `drawdown_eval` = **eod_trailing $2,500 (Fundamental/Premium); static (E2L)** (verified)
  - "Your authorized drawdown is calculated at the end of each trading day, and this calculation does not change during the day." [P4]
  - "On evaluation accounts: The EOD Drawdown always persists until the end of the evaluation." [P4]
  - note: Liquidation when balance reaches the day's fixed level (intraday breach against the EOD-set floor).
- `drawdown_funded` = **eod_trailing, stops trailing at $50,100 on a 50K** (verified)
  - "On funded accounts: Your EOD Drawdown stops at $50,100 for a 50K account and at $100,100 for a 100K account. Once the EOD Drawdown reaches these limits, it will no longer trail." [P4]
- `consistency_eval` = **none (all three plans)** (verified)
  - "Consistency (Eval)None" [P1]
- `consistency_funded` = **30% of total profit per day on Fundamental/Premium CASH (min. 4-day calculation period; gates withdrawals); none on E2L** (verified)
  - "For CASH accounts only: under no circumstances should the profit balance from a single trading day exceed 30% of the total balance." [P5]
  - "But if it does, no worries — you just need to increase your total profit." [P6]
  - "The 30% Consistency Rule does not apply to Express to Live accounts (25K, 50K, 100K, 150K)." [P6]
  - note: The homepage 'No consistency rule' refers to the evaluation step only.
- `max_funded_accounts` = **15 funded per household/company/internet connection: 5 Premium + 5 Fundamental + 5 E2L (150K counts double / limited)** (verified)
  - "The total limit for the number of simultaneous funded accounts is 15 accounts." [P7]
  - "Thus, the same tax household, the same company or persons benefiting from the same internet connection are limited to 15 funded accounts, regardless of the number of persons included in this unit." [P7]
  - "Max CASH Premium5 accounts" [P8]
- `copy_trading` = **allowed within the account limits (third-party copiers at own risk)** (verified)
  - "Copy trading is allowed within our guidelines regarding the number of authorized accounts." [P8]
  - note: 'If we discover identical strategies exceeding the maximum allowed capital, we reserve the right to suspend these accounts.'
- `opposite_positions` = **prohibited (never buyer in one account and seller in another, own or with others)** (verified)
  - "The User can never be both buyer in one account and seller in another account at the same time." [P9]
- `news` = **authorized on all accounts and stages** (verified)
  - "Yes, you are authorized to trade during news events on all accounts." [P10]
  - note: But 'Full margin trading during high volatility economic announcements' is listed as a lottery-transaction example (section 10).
- `automation` = **robots/fully automated algorithms prohibited; semi-automated allowed if trader monitors and adjusts manually** (verified)
  - "The use of robots, fully automated trading algorithms, or any other form of automated trading is not permitted. Only semi-automated software is permitted, provided the trader actively monitors and manually adjusts all trades." [P5]
- `sizing_gambling` = **lottery/one-time-withdrawal strategies discouraged; consistent position sizes required; scalping explicitly allowed** (verified)
  - "Traders must maintain consistency in their position sizes, number of trading days, and risk management." [P5]
  - "We do not support "one-time withdrawal" strategies." [P5]
  - "Whether you prefer scalping, intraday or swing trading, you have carte blanche as long as your trading is legitimate, in phase with market conditions, and we can replicate your trades on our corporate accounts." [P11]

**Terms (`terms`)**

- `eval_profit_target` = **4000** (verified)
  - "Premium 50K — Profit Target (Eval)$4,000" [P12]
- `eval_drawdown_amount` = **2500** (verified)
  - "Premium 50K — EOD Trailing Drawdown$2,500" [P12]
- `eval_drawdown_type` = **eod_trailing (realized EOD balance peaks only; session ends 10:00 PM UTC+2)** (verified)
  - "When your account balance reaches a new profit peak at the end of the trading day, the drawdown is calculated taking into account only the profits realized at that time, excluding unrealized profits." [P13]
- `eval_drawdown_lock` = **none during the evaluation (trails until the end)** (verified)
  - "On evaluation accounts: The EOD Drawdown always persists until the end of the evaluation." [P13]
- `eval_daily_loss_limit` = **none** (verified)
  - "CASH Account Funded1 trading day after eval pass Daily Loss LimitNone" [P14]
- `eval_consistency_rule` = **none** (verified)
  - "Drawdown TypeEOD trailing Consistency (Eval)None Consistency (Funded CASH)30% max per day" [P14]
- `eval_min_days` = **1** (verified)
  - "Premium 50K — Min. Trading Days (Eval)1" [P12]
  - "requiring a minimum of 3 trading days (Fundamental), 1 trading day (Premium), or 0 trading days (Express to Live)" [P15]
  - note: The General Rules box on /rules still shows 'Min. Trading Days to Pass 3 days' (generic, matches Fundamental).
- `eval_position_limit` = **10 minis / 100 micros** (verified)
  - "Premium 50K — Max Contracts10 E-mini / 100 micro" [P12]
- `eval_fee` = **$329 per month (monthly path, + $149 activation on pass) or $723 one-time (no activation fee); list prices** (verified)
  - ""premium_50k":{"eval":329,"otp":723,"reset":40}" [P16]
  - "The monthly subscription is recurring as long as the account is not validated or canceled." [P17]
  - note: Prices from the /accounts configurator data (page script). Promotion today: 60% off monthly evals, 80% off one-time (code HONOR85 / PHIDIAS80 banners).
- `eval_reset_fee` = **40** (verified)
  - "| 50K PREMIUM | 40€ | $40" [P18]
  - note: Or wait 30 days for the automatic reset on the monthly path.
- `activation_fee` = **$149 one-time per account on the monthly path; $0 on the one-time-payment path** (verified)
  - "50K Premium$149 Lifetime" [P19]
  - "No activation fees for switching to CASH account." [P19]
- `eval_count_limit` = **no limit** (verified)
  - "There is no limit to the number of evaluation accounts subscribed by a User." [P7]
- `eval_time_limit` = **none stated; monthly subscription renews; failed evals auto-reset after 30 days** (verified)
  - "Purchase a reset or wait 30 days for automatic reset" [P17]
- `funded_type` = **sim (Phidias CASH account, simulated); LIVE (Dorman Trading) at Phidias's sole discretion after 5 payouts or $100,000 cumulative profit; transition cannot be refused and resets the split to 80%** (verified)
  - "Traders on simulated CASH accounts keep their full profit split (up to 100% on Premium)." [P20]
  - "A trader becomes eligible for consideration upon reaching 5 successful payouts or $100,000 in cumulative profits across all accounts." [P21]
  - "The User may not refuse the transition, nor elect to remain on their CASH account." [P22]
  - note: RECENT CHANGE (undated): 'Previous thresholds (3 payouts / $75,000) are deprecated and no longer in effect.' LIVE credit up to $750 per active CASH 50K.
- `funded_drawdown_amount` = **2500** (verified)
  - "50K Eval Drawdown $2,500 max loss" [P13]
  - note: The funded CASH account keeps the evaluation's rules ('your evaluation becomes a funded Cash account with the same rules', /accounts FAQ), so $2,500 EOD until the floor reaches $50,100.
- `funded_drawdown_type` = **eod_trailing** (verified)
  - "On funded accounts stops at $50,100 for 50k accounts and at $100,100 for a 100k account." [P23]
- `funded_drawdown_lock` = **floor stops at $50,100 (start + $100)** (verified)
  - "50K Funded Floor $50,100 (trailing stops here)" [P13]
- `payout_balance_consequence` = **request only at balance >= $52,600; balance after withdrawal may not fall below $50,100 (= the locked floor)** (verified)
  - "For a 50k account (Fundamental or Premium): the minimum threshold is $52,600," [P22]
  - "$50,100 for a 50k account (Fundamental or Premium)," [P22]
  - note: So a payout may draw the balance down to the floor itself ('withdraw into that threshold'): after a maximal payout the account sits $0 above liquidation. A payout of at most $2,000 from $52,600 leaves $50,600, $500 above the floor.
- `funded_daily_loss_limit` = **none** (verified)
  - "CASH Account Funded1 trading day after eval pass Daily Loss LimitNone" [P14]
- `funded_consistency_rule` = **30%: no single day > 30% of total profit (min. 4-day calculation period); not a breach, fixed by trading on** (verified)
  - "No single day can exceed 30% of total profit Min. Calculation Period 4 trading days" [P24]
  - "To maintain consistency, the Company imposes profit limits for funded accounts." [P9]
  - note: Whether the 30% window resets after each payout is not stated.
- `funded_position_limit` = **10 minis / 100 micros (no scaling plan stated); overnight/weekend holds allowed on Premium** (verified)
  - "Positions on Premium accounts can remain open overnight and over-week, with a lot size corresponding to the size of your account." [P25]
  - note: Plan grid: 'Premium 50K — Max Contracts10 E-mini / 100 micro'.
- `funded_monthly_fee` = **none (activation fee is lifetime, no monthly fees on CASH)** (verified)
  - "Activation fees are Lifetime on each account (one-time payment per account until failure, no monthly fees)." [P19]
- `payout_min` = **500 (rules page) vs 1000 (Terms of Use)** (verified)
  - "Min. Withdrawal $500" [P21]
  - "The minimum withdrawal amount can never be less than $1,000." [P22]
  - note: CONFLICT between /rules ($500) and /tou ($1,000).
- `payout_cap` = **$2,000 per payment period per 50K account (each account separately); none once LIVE** (verified)
  - "Premium 50K — Payout Cap (per cycle)$2,000" [P12]
  - "If you have multiple accounts, you can withdraw up to the maximum amount from each account during each payment period." [P21]
  - note: TOU also says 'During this initial three-month period, there is also a maximum payment amount' (period not otherwise defined). Premium progressive split 'applies to the payout cap'.
- `payout_frequency_gate` = **5 distinct trading days with >= $150 PnL between requests (Premium; 10 for Fundamental); balance >= $52,600; 30% consistency** (verified)
  - "In other words, a minimum of 10 distinct trading days (5 for Premium) must be respected between each withdrawal request, whether it was approved or refused." [P22]
  - "A trading day is counted only if it shows a positive PnL of at least:" [P21]
  - "50K Account $150 min daily PnL" [P21]
  - note: TOU's FIRST WITHDRAWAL clause says '10 distinct and individual trading days' for any user before the first request -- ambiguous for Premium (5 thereafter).
- `payout_split` = **progressive: 75%, 80%, 85%, 90%, then 100% from payout 5 (Premium CASH)** (verified)
  - "Premium accounts use a progressive profit split: 75/25 on payout 1, 80/20 on payout 2, 85/15 on payout 3, 90/10 on payout 4, 100/0 from payout 5 onwards." [P22]
- `payout_processing_days` = **90% under 30 minutes, always within 24 hours, to the Phidias Wallet; then Rise transfer** (verified)
  - "90% of payouts processed under 30 minutes. Always within 24 hours." [P26]
- `payout_fee` = **none stated beyond the profit split** (UNVERIFIED)
  - looked at: https://phidiaspropfirm.com/rules (sections 12-14), https://phidiaspropfirm.com/tou (3.1.5)
- `payout_count_limit` = **none stated; 5 payouts make the trader eligible for a discretionary, non-refusable LIVE transition** (verified)
  - "A trader becomes eligible for consideration upon reaching 5 successful payouts or $100,000 in cumulative profits." [P22]
- `max_accounts` = **5 Premium CASH (+5 Fundamental +5 E2L, 15 total) per household/company/IP; 150K counts double; evaluations unlimited; excess accounts are lost** (verified)
  - "The limits set above apply across all of the user's login credentials, any user account or person residing at the same address, same IP address, etc." [P27]
  - "Any CASH account beyond this threshold will be considered lost." [P27]
- `inactivity_rule` = **not stated for CASH accounts (LIVE E2L terms elsewhere)** (UNVERIFIED)
  - looked at: https://phidiaspropfirm.com/rules, https://phidiaspropfirm.com/tou
- `copy_trading_terms` = **allowed within account limits; identical strategies beyond max capital may be suspended** (verified)
  - "If we discover identical strategies exceeding the maximum allowed capital, we reserve the right to suspend these accounts." [P27]
- `cross_account_hedging` = **prohibited; groups/partnerships closed and banned** (verified)
  - "Any attempt at groups or partnerships will result in complete closure and confiscation of accounts of both parties, as well as a ban from the Site, tools and programs of the Company;" [P9]
  - "Example: inverse operation (buy vs sell) via multiple accounts on the same asset." [P28]
- `news_trading_terms` = **allowed on all accounts** (verified)
  - "Economic news trading is permitted on all account types." [P28]
  - note: Full-margin trading into high-volatility announcements is a 'lottery transaction' example.
- `automation_terms` = **prohibited (robots, fully automated algorithms, HFT); semi-automated allowed with active manual management** (verified)
  - "Prohibition of automated trading and High frequency trading: the use of robots, fully automated trading algorithms or any form of automated trading is not authorized, except for semi-automated software, provided the User actively monitors and manually adjusts all operations;" [P9]
- `sizing_or_gambling_terms` = **no lottery trades; consistent position sizes; no contract 'reloading' to hit objectives; exploiting the sim environment loses the account** (verified)
  - "Any attempt to exploit the simulated environment results in loss of account access." [P9]
  - "Full margin trading during high volatility economic announcements." [P28]
  - note: Homepage: 'No micro-scalping rules.'
- `other_conduct_bearing` = **trade the front (highest-volume) contract; no calendar spreads; no Treasury arbitrage; defined trading system with stops expected; Premium may hold overnight (Fundamental/E2L flat by 9:59 PM UTC)** (verified)
  - "You are required to trade the highest volume and most recent contract for the instrument you wish to trade." [P28]
  - "This system must include clear rules for entries, stops, profit taking, drawdown management and exits." [P28]
  - note: A stop-and-target bracket fits the 'defined trading system' expectation.
- `permitted_products` = **CME, CBOT, NYMEX, COMEX futures incl. NQ/MNQ/ES/MES (Rithmic commission NQ $2.20/side, MNQ $0.79/side) plus Eurex via dxFeed/Tradovate** (verified)
  - "| NQ | $2.20 / side" [P29]
  - "| MNQ | $0.79 / side" [P29]
  - note: Rows are under the header '| Instrument | Commission' in the 'CME Group (Rithmic)' block. Tradovate/NinjaTrader rates differ (NQ $2.68/side).

**Terms (`terms_e2l`)**

- `eval_and_cash_rules` = **50K: profit target $2,500 (eval, then again on CASH), static drawdown $650 (liquidation $49,350), 5 minis / 50 micros, no consistency, no DLL, 0 min days, no overnight** (verified)
  - "E2L 50K — Profit Target$2,500" [P30]
  - "E2L 50K — Liquidation$49,350" [P30]
  - "Once the evaluation is passed, your account is converted to a funded CASH account with the same rules. Reach the profit target again on the CASH account." [P30]
- `payout` = **no regular payouts: on reaching the CASH target, a fixed $2,000 bonus (80/20 split) to the Wallet plus $1,000 LIVE credit, and the account converts to LIVE (3 lots, $500 min daily payouts, 80% split)** (verified)
  - "E2L 50K — Bonus Payout$2,000 (80/20 split)" [P30]
  - "LIVE from E2L 50K — Max Contracts3 lots" [P30]
  - note: One-shot reward per E2L account; failure of an E2L-derived LIVE account bars new E2L challenges for 1 month.
- `fees_and_limits` = **$278/month + $149 activation, or $723 one-time (list); no resets; max 5 E2L per trader** (verified)
  - ""e2l_50k":{"eval":278,"otp":723,"reset":0}" [P16]
  - "Max E2L Accounts5 per trader (all sizes combined)" [P30]
  - "No reset can occur as part of 10K Drawdown or Express to Live (E2L) account evaluations." [P18]
  - note: CONFLICT: TOU 3.1.1 limits E2L 150K to 1 account; /rules says the 150K counts as one slot within the 5.

### Goat Funded Futures (GFF) (`goat`) -- PASS

Verdict: **PASS** -- Flex 50K: EOD trailing funded drawdown locking at start, no funded consistency percentage, up to 5 Flex funded accounts (copying own trades across them is the stated intended use); hand-entered bracket trading allowed, subject to the 1-minute 70%/70% holding test, funded 2-minute news buffer, no hedging, no overnight.

Struck (E-020): the firm's own terms forbid automated retrieval -- "Harvesting, scraping, or otherwise collecting any information from the Sites ... without our prior written consent" (as recorded under E-009). Removed on 2026-11-16 (Q-34): the firm's saved pages, the terms and quotes its file held, and this section; its plans are read, if ever, only through the operator's browser or with the firm's written permission.

### Bulenox (`bulenox`) -- PASS

**Pages quoted** (key: URL; article id; the page's own date as shown; all read 2026-11-15)

- [P1] https://bulenox.com/accounts-pricing
- [P2] https://bulenox.com/assets/index-C0h3UDdG.js
- [P3] https://bulenox.com/faq
- [P4] https://bulenox.com/legal/Terms_of_Use.pdf; page date: Updated October 2026
- [P5] https://bulenox.com/


Official domains: bulenox.com. Read 2026-11-15.
Plan captured: Qualification 50K, Option 2 (End-of-Day Drawdown) -> Master Account.
Verdict: **PASS** -- EOD drawdown option carries to the Master/Funded account, up to 5 Master-level accounts, copiers and news allowed, nothing bars hand-entered bracket trading on NQ/MNQ (Master consistency % and most payout terms UNVERIFIED: Help Center unreadable).

Unreadable (not worked around):
- https://bulenox.com/help-center -- Single-page app: the help-centre articles (Master Account rules, consistency %, withdrawal rules, scaling plan, Master activation fee, hedging) are loaded at run time from the site's own CMS endpoint (https://bulenox.com/cms/items/help_items...). The HTML and its JS chunk (raw/bulenox/helpjs.txt) hold no article text. A GET of the CMS endpoint was denied by this session's permission system (not attempted again); WebFetch of /help-center returned only the category headings, no article bodies. All help-centre-only terms are therefore UNVERIFIED.

Plans seen:
- Qualification 50K, Option 1 (Trailing Drawdown): drawdown intraday trailing (real time, incl. open positions), $2,500; no daily loss limit; choice locked for life of account; consistency evaluation not stated on readable pages, funded Master payout consistency rule exists; % in Help Center (unreadable)
  - "Your loss limit follows your highest point — including open positions, in real time." [P1]
- Qualification 50K, Option 2 (End-of-Day Drawdown): drawdown EOD trailing $2,500, daily loss limit $1,100 (pauses the day), contract size scales with cash on hand; choice locked for life of account (Qualification, Master, Funded); consistency evaluation not stated on readable pages, funded Master payout consistency rule exists; % in Help Center (unreadable)
  - "{size:`$50,000`,contracts:`7`,contractsEod:`7`,target:`$3,000`,drawdown:`$2,500`,dailyLoss:`$1,100`,price:`$175`,popular:!0}" [P2]
- Momentum 50K (one payment covers Qualification + free Momentum Master): drawdown trailing or EOD option; $2,000; EOD: 4 contracts, DLL $1,200; consistency evaluation none (stated), funded 35% per payout cycle + 5 qualifying profitable days
  - "5 qualifying profitable days and 35% consistency per payout cycle" [P2]
- Fast Track 50K (no evaluation; simulated funded from day one): drawdown trailing or EOD option; $2,000; EOD: 4 contracts, DLL $1,200; $488 one-time; consistency evaluation n/a (no evaluation), funded exists; % in Help Center (unreadable)
  - "{size:`$50,000`,price:`$488`,contracts:`7`,contractsEod:`4`,drawdown:`$2,000`,dailyLoss:`$1,200`,firstPayout:`$3,000`}" [P2]

**Screen**

- `drawdown_eval` = **eod_trailing (Option 2; Option 1 is intraday trailing)** (verified)
  - "Your loss limit moves only once a day — at the close, on realised profit." [P1]
  - "your drawdown updates once a day at the close on realised profit, contract size scales with your Cash On Hand, and a daily loss limit pauses your day instead of ending the account. The choice is locked for the life of the account." [P3]
  - note: Lock level of the EOD drawdown not stated on readable pages.
- `drawdown_funded` = **eod_trailing (the Option 2 choice carries to Master and Funded)** (verified)
  - "This choice is locked for the life of the account." [P1]
  - "The choice is locked for the life of the account." [P3]
  - note: Said of the Option 1 / Option 2 drawdown model at purchase; read as covering the Master stage. No readable page restates the Master drawdown type separately; Master drawdown amount and lock are in the unreadable Help Center.
- `consistency_eval` = **not stated for Qualification; Momentum Qualification: none** (UNVERIFIED)
  - "No minimum trading days and no consistency rule at this stage" [P2]
  - looked at: https://bulenox.com/accounts-pricing, https://bulenox.com/faq, https://bulenox.com/legal/Terms_of_Use.pdf (Help Center unreadable)
  - note: The quote is the Momentum Qualification stage only. The FAQ describes the Qualification as 'reach the profit target within the drawdown rules' with no consistency mention, which is not a statement that none applies.
- `consistency_funded` = **a consistency rule gates Master payout requests (not a violation); percentage for the regular Master is in the unreadable Help Center; Momentum Master 35% per payout cycle** (UNVERIFIED)
  - "The consistency rule keeps your results balanced — your best single trading day should not make up too large a share of your total profit for the payout period. If a request does not meet it, nothing is violated and your account stays open: just keep trading with your usual position size until the balance evens out." [P3]
  - "5 qualifying profitable days and 35% consistency per payout cycle" [P2]
  - looked at: https://bulenox.com/help-center (unreadable; FAQ points to #withdrawal-rules for the Master figure)
  - note: Existence verified; the regular-Master percentage is UNVERIFIED.
- `max_funded_accounts` = **up to 5 Master-level accounts at once (Master, Fast Track, Momentum Master in any combination); Qualification accounts unlimited; one trader profile per household** (verified)
  - "Up to five Master-level accounts at once — Master, Fast Track and Momentum in any combination. Qualification Accounts stay unlimited." [P1]
  - "in total — Master, Fast Track and Momentum Master in any combination. Qualification Accounts stay unlimited, and all of your accounts run under one Rithmic User ID." [P3]
  - "F. you are the sole authorized Bulenox trader profile holder within your household, and no other person residing at the same physical address or sharing the same residential location operates or maintains a Bulenox trader profile, unless such person has obtained prior written approval from Bulenox Compliance." [P4]
- `copy_trading` = **permitted (user-built tools for own use only)** (verified)
  - "Yes. Bots, algorithms and trade copiers are permitted. If you connect to Rithmic through a third-party API or composite software, an additional $100 per month applies. Only user-built tools intended solely for the account owner’s personal use are permitted. Commercial, shared, rented or publicly distributed automation tools are not allowed." [P3]
  - note: Conflict: the Terms of Use (Oct 2026) require any third-party trading technology to be reviewed and approved by Bulenox before use (see automation).
- `opposite_positions` = **not stated on readable pages** (UNVERIFIED)
  - looked at: https://bulenox.com/faq, https://bulenox.com/accounts-pricing, https://bulenox.com/legal/Terms_of_Use.pdf (no hedging clause); Help Center unreadable
  - note: Terms prohibit 'tricking, defrauding or misleading Company' generally; no explicit cross-account hedging rule found.
- `news` = **allowed, no blackout windows** (verified)
  - "Yes. Trade straight through the economic calendar — CPI, FOMC, NFP and every other release. No blackout windows, no forced position closing, no penalties." [P3]
- `automation` = **FAQ: bots/algos permitted if user-built for own use (+$100/month for third-party API/composite connection); Terms: third-party algorithms must be pre-approved, scalping algorithms and DTC Protocol Bridge API abuse prohibited** (verified)
  - "Yes. Bots, algorithms and trade copiers are permitted." [P3]
  - "To avoid performance discrepancies and/or meet applicable compliance requirements, any third-party algorithm, automated trading software, or other third-party trading technology must be reviewed and approved by the Bulenox management team before use." [P4]
  - "It includes but is not limited to using “scalping” algorithms, DTC Protocol Bridge API or automated discretional trading in any of the trading environments." [P4]
  - note: Our trades are hand-entered, so neither version bars the design.
- `sizing_gambling` = **no named gambling/max-size rule on readable pages; Terms bar 'reckless transactions in rough markets' and rapid-fire algorithmic trading** (verified)
  - "Open and close hundreds or thousand of rapid trades by using any trading algorithms. Implementation of reckless transactions in rough markets to benefit from lack of execution." [P4]
  - looked at: Help Center unreadable

**Terms (`terms`)**

- `eval_profit_target` = **3000** (verified)
  - "{size:`$50,000`,contracts:`7`,contractsEod:`7`,target:`$3,000`,drawdown:`$2,500`,dailyLoss:`$1,100`,price:`$175`,popular:!0}" [P2]
  - "Account size$50,000 Contracts7 Profit target$3,000 Drawdown up to$2,500 Min. trading daysNone" [P1]
  - note: The JS object is the pricing page's own tier data (it renders the visible card).
- `eval_drawdown_amount` = **2500** (verified)
  - "{size:`$50,000`,contracts:`7`,contractsEod:`7`,target:`$3,000`,drawdown:`$2,500`,dailyLoss:`$1,100`,price:`$175`,popular:!0}" [P2]
  - note: Pricing labels the same figure 'Drawdown up to' (trailing) or 'EOD Drawdown' (Option 2).
- `eval_drawdown_type` = **eod_trailing** (verified)
  - "Your drawdown threshold stays fixed throughout the trading day." [P1]
- `eval_drawdown_lock` = **not stated** (UNVERIFIED)
  - looked at: https://bulenox.com/accounts-pricing, https://bulenox.com/faq (Help Center unreadable)
- `eval_daily_loss_limit` = **1100** (verified)
  - "{size:`$50,000`,contracts:`7`,contractsEod:`7`,target:`$3,000`,drawdown:`$2,500`,dailyLoss:`$1,100`,price:`$175`,popular:!0}" [P2]
  - "The daily loss limit pauses your trading for the day instead of closing the account." [P1]
  - note: Soft limit (pauses the day). Option 1 (trailing) has no daily loss limit.
- `eval_consistency_rule` = **not stated for Qualification** (UNVERIFIED)
  - looked at: https://bulenox.com/faq, https://bulenox.com/accounts-pricing, Terms PDF; Help Center unreadable
  - note: Momentum Qualification states none.
- `eval_min_days` = **none** (verified)
  - "As long as you need. There is no minimum and no maximum number of trading days — reach the profit target within the drawdown rules and you’re through." [P3]
- `eval_position_limit` = **7 contracts (EOD option, 1 mini = 10 micros); contract size scales with cash on hand under Option 2** (verified)
  - "{size:`$50,000`,contracts:`7`,contractsEod:`7`,target:`$3,000`,drawdown:`$2,500`,dailyLoss:`$1,100`,price:`$175`,popular:!0}" [P2]
  - "1 mini = 10 micros." [P1]
  - note: Scaling tiers (Option 2) are in the unreadable Help Center.
- `eval_fee` = **$175 one-time; access valid for 30 days** (verified)
  - "$175one-time Access valid for 30 days" [P1]
  - "Qualification accounts have no recurring payment — access simply expires at the end of the subscription cycle and nothing is charged again." [P3]
  - note: List price before the always-on coupon; same price for Option 1 and 2.
- `eval_reset_fee` = **78** (verified)
  - "costs $78: your balance returns to its starting value and you keep going on the same account." [P3]
- `activation_fee` = **one-time Master activation fee, amount by account size not on readable pages; Momentum Master free** (UNVERIFIED)
  - "A Master Account has no monthly fee — only a one-time activation, depending on account size." [P3]
  - looked at: Help Center unreadable
  - note: Existence verified; amount UNVERIFIED.
- `eval_count_limit` = **unlimited Qualification accounts** (verified)
  - "Up to five Master-level accounts at once — Master, Fast Track and Momentum in any combination. Qualification Accounts stay unlimited." [P1]
- `eval_time_limit` = **no trading-day limit, but purchased access is valid 30 days** (verified)
  - "Access valid for 30 days" [P1]
  - "As long as you need. There is no minimum and no maximum number of trading days" [P3]
  - note: Read together: no trading-day count, within a 30-day access window.
- `funded_type` = **Master Account (stage after Qualification; trader is paid) leading to a Funded Account; Master sim/live status and Master-to-Funded criteria not on readable pages** (UNVERIFIED)
  - "The classic route. Pass a Qualification Account, activate a Master Account and trade your way to a Funded Account. Lowest entry price, three clear stages." [P5]
  - "After 3 payouts the account is reviewed for a Funded Account." [P3]
  - looked at: Help Center (Master Account / Funded Account tabs) unreadable
  - note: The '3 payouts' review is stated for Fast Track; Fast Track is called 'a simulated funded environment'.
- `funded_drawdown_amount` = **not stated for Master** (UNVERIFIED)
  - looked at: Help Center unreadable
- `funded_drawdown_type` = **eod_trailing (Option 2 locked for the life of the account)** (verified)
  - "This choice is locked for the life of the account." [P1]
- `funded_drawdown_lock` = **not stated** (UNVERIFIED)
  - looked at: Help Center unreadable
- `payout_balance_consequence` = **not stated** (UNVERIFIED)
  - looked at: Help Center (#withdrawal-rules) unreadable
- `funded_daily_loss_limit` = **Option 2 has a daily loss limit that pauses the day; Master amount not stated** (UNVERIFIED)
  - "The daily loss limit pauses your trading for the day instead of closing the account." [P1]
  - looked at: Help Center unreadable
- `funded_consistency_rule` = **applies to Master payout requests; % UNVERIFIED** (UNVERIFIED)
  - "If a request does not meet it, nothing is violated and your account stays open: just keep trading with your usual position size until the balance evens out." [P3]
  - looked at: Help Center unreadable
- `funded_position_limit` = **scales with cash on hand (Option 2); tiers not on readable pages** (UNVERIFIED)
  - "Contract size scales up as your cash on hand grows." [P1]
  - looked at: Help Center unreadable
- `funded_monthly_fee` = **none on Master accounts** (verified)
  - "Once the Master Account is activated, there will be no monthly fees." [P5]
  - note: Professional-status traders pay $116/month CME data; +$100/month for third-party API connection.
- `payout_min` = **not stated** (UNVERIFIED)
  - looked at: https://bulenox.com/faq; Help Center unreadable
- `payout_cap` = **not stated** (UNVERIFIED)
  - looked at: https://bulenox.com/faq; Help Center unreadable
- `payout_frequency_gate` = **Master payouts processed every Wednesday; other gates not stated** (UNVERIFIED)
  - "You can request a payout any day of the week. On Fast Track and Momentum requests are processed the same day; on a regular Master Account they are processed every Wednesday." [P3]
  - looked at: Help Center (#withdrawal-rules) unreadable
  - note: Winning-day/buffer gates for the regular Master UNVERIFIED.
- `payout_split` = **90/10** (verified)
  - "The split is 90/10 in your favour." [P3]
- `payout_processing_days` = **regular Master: processed every Wednesday** (verified)
  - "on a regular Master Account payouts are processed every Wednesday." [P3]
- `payout_fee` = **no payout processing fees** (verified)
  - "No payout processing fees" [P5]
  - note: Payment rails: ACH/wire and PayPal.
- `payout_count_limit` = **not stated for Master** (UNVERIFIED)
  - looked at: Help Center unreadable
- `max_accounts` = **5 Master-level at once; Qualification unlimited; one profile per household** (verified)
  - "Up to five Master-level accounts at once — Master, Fast Track and Momentum in any combination. Qualification Accounts stay unlimited." [P1]
  - "If multiple profiles are identified as belonging to the same household, Bulenox reserves the right to close or consolidate the additional profiles." [P4]
- `inactivity_rule` = **not stated** (UNVERIFIED)
  - looked at: FAQ, pricing, Terms PDF; Help Center unreadable
- `copy_trading_terms` = **permitted for the owner's own user-built tools** (verified)
  - "Only user-built tools intended solely for the account owner’s personal use are permitted. Commercial, shared, rented or publicly distributed automation tools are not allowed." [P3]
  - note: Terms require pre-approval of third-party trading technology.
- `cross_account_hedging` = **not stated** (UNVERIFIED)
  - looked at: FAQ, pricing, Terms PDF; Help Center unreadable
- `news_trading_terms` = **allowed; positions closed by 3:59 pm CT** (verified)
  - "The trading day runs from 5:00 pm to 4:00 pm CT, and all positions must be closed by 3:59 pm CT." [P3]
  - "No blackout windows, no forced position closing, no penalties." [P3]
- `automation_terms` = **allowed if user-built (FAQ); third-party tech must be approved (Terms); $100/month for third-party API** (verified)
  - "If you connect to Rithmic through a third-party API or composite software, an additional $100 per month applies." [P3]
  - "Approval may be subject to additional requirements or conditions established by Bulenox." [P4]
  - note: Pages differ in emphasis (FAQ permissive, Terms approval-gated).
- `sizing_or_gambling_terms` = **no explicit gambling/max-size rule found; abuse clause in Terms** (verified)
  - "If abuse is suspected, we reserve the right to refuse to claim any profit." [P4]
  - looked at: Help Center unreadable
- `other_conduct_bearing` = **one Bulenox profile per household; all accounts under one Rithmic user ID; trade until 15:59 CT** (verified)
  - "Trade until 15:59 CT — later than most." [P5]
- `permitted_products` = **41 CME Group futures incl. NQ/ES and micros** (verified)
  - "41 futures contracts on all four CME Group exchanges — CME, CBOT, NYMEX and COMEX. Equity indices (ES, NQ, YM, RTY, EMD)" [P3]

### Take Profit Trader (TakeProfitTrader LLC) (`tpt`) -- PASS

**Pages quoted** (key: URL; article id; the page's own date as shown; all read 2026-11-15)

- [P1] https://takeprofittrader.com/


Official domains: takeprofittrader.com, takeprofittraderhelp.zendesk.com. Read 2026-11-15.
Plan captured: TPT 50K Test -> PRO (the only structure sold; per-size numbers unreadable).
Verdict: **PASS** -- Reading 'no consistency rule' as the funded rule: PRO has no consistency rule (intraday trailing drawdown, stops at start) and up to 5 funded accounts; nothing readable forbids hand-entered bracket trading. Caveat: FAILS if the screen means no consistency anywhere (Test has 50%), and the Terms/help centre are unreadable (403), so conduct rules there are UNVERIFIED.

Unreadable (not worked around):
- https://takeprofittrader.com/faq -- 403 Cloudflare 'Sorry, you have been blocked' to curl; WebFetch tried once, also HTTP 403
- https://takeprofittrader.com/terms -- 403 Cloudflare block to curl; WebFetch tried once, also HTTP 403. Terms of Service UNREAD.
- https://takeprofittrader.com/about-us -- 403 Cloudflare block to curl (not retried)
- https://takeprofittraderhelp.zendesk.com/hc/en-us -- 403 Cloudflare challenge ('Just a moment') to curl; WebFetch tried once, also HTTP 403. The whole help centre (knowledge base: rules articles 15170316538013 'Rule 6 Be Consistent', 15171769361053 'Are the rules the same', 15172219527581 'PRO Account Profit Split & Withdrawal Rules', 15140989806493 'Resetting Your Test Account') is unreadable.
- https://takeprofittrader.com/ (account-size table) -- homepage readable, but the per-size parameter table ('Choose Your Futures Account Size') is rendered client-side; not in the HTML; WebFetch confirmed 'Not on the page'

Plans seen:
- Test -> PRO (sim funded) -> PRO+ (live); one evaluation type sold in several sizes (12K/25K/50K/75K/100K/150K appear in credit labels): drawdown Test: EOD trailing; PRO: intraday trailing; PRO+: EOD; all stop trailing at the initial balance; consistency evaluation 50%, funded none
  - "The drawdown is End Of Day on test accounts, meaning it updates at the end of the trading day (5PM EST). On the PRO accounts, the drawdown is intraday, meaning it trails your unrealized profit in real time. In PRO+, the drawdown is End Of Day, the same as in the test." [P1]

**Screen**

- `drawdown_eval` = **eod_trailing** (verified)
  - ""table-test-8":"End Of Day","table-pro-8":"Intraday","table-pro-plus-8":"End Of Day"" [P1]
  - note: From the homepage's embedded translation JSON for the Test / PRO / PRO+ comparison table (row 'Drawdown').
- `drawdown_funded` = **intraday_trailing on PRO (sim funded); stops trailing at the initial balance. PRO+ (live) is EOD.** (verified)
  - "On the PRO accounts, the drawdown is intraday, meaning it trails your unrealized profit in real time." [P1]
  - "The drawdown across all three account types will STOP trailing once it has reached the initial account balance." [P1]
  - "In PRO+ you also have end-of-day drawdown and no buffer requirement." [P1]
- `consistency_eval` = **50% (biggest day <= 50% of total profit), in the Test only** (verified)
  - "We require you to show consistency while in test. Your biggest trading day cannot be more than 50% of your total profit." [P1]
- `consistency_funded` = **none** (verified)
  - "Take Profit Trader has no consistency rule in PRO, so your daily withdrawals aren't held back by how your profits are distributed across days." [P1]
  - ""table-test-9":"Yes","table-pro-9":"None","table-pro-plus-9":"None"" [P1]
- `max_funded_accounts` = **5 funded (PRO/PRO+); unlimited Test accounts; at most 10 passed tests activated per 30 calendar days** (verified)
  - "You can trade up to five funded accounts while continuing to trade Test accounts alongside them." [P1]
  - "Traders can have as many test accounts as they want and trade them simultaneously. They can also have up to 5 funded accounts." [P1]
  - "You've reached the limit of 10 test activations per 30 days." [P1]
  - note: Per person vs household: UNVERIFIED (Terms unreadable).
- `copy_trading` = **UNVERIFIED** (UNVERIFIED)
  - looked at: https://takeprofittrader.com/ (all visible text and embedded JSON). /faq, /terms and the Zendesk help centre are blocked (403).
  - note: No statement either way on the readable page.
- `opposite_positions` = **prohibited ('No counter positions': opposing positions in the same or similar products across multiple accounts)** (verified)
  - "Counter positions is when you hold opposing positions in the same, or similar products, across multiple accounts." [P1]
  - ""no-counter-positions":"No counter positions"" [P1]
  - note: The linked 'Counter Positions Rule' article is on the blocked Zendesk host.
- `news` = **PRO and PRO+: flat with no open orders one minute before, during and after major news events; Test: unrestricted** (verified)
  - "All PRO and PRO+ accounts must be out of all positions, and have no open orders, one minute before, during, and after the major news event. This does not apply for test accounts and you are free to trade through all news events." [P1]
  - note: The list of restricted events is on the blocked Zendesk host.
- `automation` = **'No trading bots'; very-short-timeframe algos make an account 'unsuccessful'. Hand entry is what they want.** (verified)
  - "We are looking for discretionary traders, not automated trading robots. Any account traded using trading algos/automated trading systems on very short time frames (seconds) will be considered unsuccessful." [P1]
  - ""no-trading-bots":"No trading bots"" [P1]
- `sizing_gambling` = **PRO: max 50 executions per day; contract limit per size (UNVERIFIED amount); no open positions past session close (17:00 EST in one string, 16:55 ET in the CQG string)** (verified)
  - "In the PRO Accounts, we ask that you do no more than 50 executions per day. An execution is any filled trade, regardless of size of the trade." [P1]
  - "Don't hold open positions past 17:00 EST" [P1]
  - note: No gambling / all-in / minimum-hold rule seen on the readable page; the Terms (which would hold one) are unreadable. 50 executions/day counts each fill: a bracket trade is 2 executions per account, so ~25 round trips per account per day.

**Terms (`terms`)**

- `eval_profit_target` = **UNVERIFIED** (UNVERIFIED)
  - looked at: https://takeprofittrader.com/ (size table JS-rendered; WebFetch 'Not on the page'); /faq, /terms, Zendesk: 403
- `eval_drawdown_amount` = **UNVERIFIED** (UNVERIFIED)
  - looked at: as eval_profit_target
- `eval_drawdown_type` = **eod_trailing** (verified)
  - "The drawdown is End Of Day on test accounts, meaning it updates at the end of the trading day (5PM EST)." [P1]
- `eval_drawdown_lock` = **stops trailing at the initial account balance** (verified)
  - "The drawdown across all three account types will STOP trailing once it has reached the initial account balance." [P1]
- `eval_daily_loss_limit` = **none per the comparison table (Test / PRO / PRO+ all 'None')** (verified)
  - ""table-test-7":"None","table-pro-7":"None","table-pro-plus-7":"None"" [P1]
  - note: Row 'Daily loss rule'. The dashboard rules list also contains a template 'Don't hit or exceed the ${{value}} Daily Loss Limit', so some accounts may carry one; per-size values unreadable.
- `eval_consistency_rule` = **50%: biggest day no more than 50% of total profit; gates passing** (verified)
  - "Your biggest trading day cannot be more than 50% of your total profit." [P1]
- `eval_min_days` = **3 trading days (tests bought from August 17th onward)** (verified)
  - "3 trading days, as long as you've met the profit target and all other test rules." [P1]
  - "The 3-day eval only applies to new test accounts purchased from August 17th onward." [P1]
  - note: 'August 17th' without a year; recent rule change.
- `eval_position_limit` = **UNVERIFIED** (UNVERIFIED)
  - looked at: as eval_profit_target
- `eval_fee` = **monthly subscription; 50K price UNVERIFIED** (UNVERIFIED)
  - "Choose the Futures account size that best fits your trading style. Once you're ready, complete your subscription and continue to the next step." [P1]
  - "Your monthly fees go away completely once you become a PRO Trader." [P1]
  - looked at: as eval_profit_target
  - note: Billing basis (monthly) is verified; the amount is not readable.
- `eval_reset_fee` = **UNVERIFIED (priced per account size since 'Saturday, May 16th')** (UNVERIFIED)
  - "Effective Saturday, May 16th, all test reset pricing is now aligned to each account size." [P1]
  - looked at: the linked Zendesk article 15140989806493 is blocked (403)
- `activation_fee` = **130 USD one-time PRO account setup fee (waived for life under the NOFEE40 promotion advertised on the homepage)** (verified)
  - "Pay a one time $130 PRO Account setup fee, and ZERO monthly fees after that." [P1]
  - "Get 40% Off For Life + Never Pay An Activation Fee! CLICK THIS LINK FOR DETAILS. Use Code: NOFEE40" [P1]
- `eval_count_limit` = **unlimited Test accounts; 10 test activations (passes promoted) per 30 days** (verified)
  - ""table-test-4":"Unlimited","table-pro-4":"5","table-pro-plus-4":"5"" [P1]
  - "TRADER, in this context, has the privilege to activate up to 10 successfully cleared tests within a span of 30 calendar days." [P1]
- `eval_time_limit` = **UNVERIFIED (monthly subscription; no stated limit)** (UNVERIFIED)
  - looked at: homepage; /faq, /terms, Zendesk blocked
- `funded_type` = **PRO = simulated, paid in real money; PRO+ = live (Tradovate), 90/10, EOD drawdown, no buffer; promotion trigger to PRO+ UNVERIFIED** (verified)
  - "Yes, all PRO accounts are simulated (SIM)." [P1]
  - "Take Profit uses Tradovate as its regulated broker for live (PRO+) accounts." [P1]
  - "$5K of Profit will remain frozen as long as your PRO+ account is active" [P1]
  - note: The 'Upgrade to PRO+' criterion is not on the readable page. A UI string says '$5K of Profit will remain frozen as long as your PRO+ account is active'.
- `funded_drawdown_amount` = **UNVERIFIED (equals the buffer; per size not readable)** (UNVERIFIED)
  - looked at: as eval_profit_target
- `funded_drawdown_type` = **intraday_trailing** (verified)
  - "On the PRO accounts, the drawdown is intraday, meaning it trails your unrealized profit in real time." [P1]
- `funded_drawdown_lock` = **stops trailing at the initial account balance** (verified)
  - "The drawdown across all three account types will STOP trailing once it has reached the initial account balance." [P1]
- `payout_balance_consequence` = **withdrawals only from profit above a buffer equal to the max drawdown amount; buffer profits withdrawable only from a disabled PRO account** (verified)
  - "In order to withdraw from an active PRO account, you have to be above the buffer zone. Buffer zone is equal to your maximum drawdown amount. Profits inside the buffer zone can be withdrawn from a disabled PRO account." [P1]
  - note: Since the drawdown stops at the initial balance and the buffer equals the drawdown, the floor sits at start and withdrawals cannot take the balance below start + drawdown (reading; the full rule is in the blocked Zendesk article 15172219527581).
- `funded_daily_loss_limit` = **none per the comparison table** (verified)
  - ""table-test-7":"None","table-pro-7":"None","table-pro-plus-7":"None"" [P1]
- `funded_consistency_rule` = **none** (verified)
  - "Take Profit Trader has no consistency rule in PRO, so your daily withdrawals aren't held back by how your profits are distributed across days." [P1]
- `funded_position_limit` = **same as the Test account (no scaling plan); amount UNVERIFIED** (verified)
  - "At Take Profit Trader, you get the exact same buying power in your PRO Account that you had in your test account." [P1]
- `funded_monthly_fee` = **none once PRO** (verified)
  - "Your monthly fees go away completely once you become a PRO Trader." [P1]
- `payout_min` = **UNVERIFIED** (UNVERIFIED)
  - looked at: homepage; withdrawal rules article on blocked Zendesk
- `payout_cap` = **no maximum withdrawal amount** (verified)
  - "there is NO maximum withdrawal amount at TakeProfit." [P1]
- `payout_frequency_gate` = **from day one of PRO, any profit above the buffer; no minimum profitable days, no payout window** (verified)
  - "No minimum amount of profitable days you need to trade, no maximum amount you can withdraw, and no waiting for some random" [P1]
- `payout_split` = **80/20 on PRO (of profits above the buffer); 90/10 on PRO+** (verified)
  - "In the PRO accounts you keep 80% of your profits above the buffer and 90% in PRO+ accounts." [P1]
- `payout_processing_days` = **typically within one business day (Plaid to US banks, PayPal or Wise)** (verified)
  - "the profits will be paid out either through an automated process via Plaid to US bank accounts or via PayPal or Wise, typically within one business day." [P1]
- `payout_fee` = **UNVERIFIED (the UI has a 'Withdraw fee' field; amount not stated)** (UNVERIFIED)
  - ""withdraw-fee":"Withdraw fee"" [P1]
  - looked at: homepage; blocked withdrawal-rules article
- `payout_count_limit` = **UNVERIFIED** (UNVERIFIED)
  - looked at: homepage
- `max_accounts` = **5 funded; unlimited tests; 10 activations per 30 days** (verified)
  - "You can trade up to five funded accounts while continuing to trade Test accounts alongside them." [P1]
- `inactivity_rule` = **UNVERIFIED** (UNVERIFIED)
  - looked at: homepage; /terms and Zendesk blocked
- `copy_trading_terms` = **UNVERIFIED** (UNVERIFIED)
  - looked at: homepage; /terms, /faq and Zendesk blocked
- `cross_account_hedging` = **prohibited (counter positions across multiple accounts)** (verified)
  - "Counter positions is when you hold opposing positions in the same, or similar products, across multiple accounts." [P1]
- `news_trading_terms` = **PRO/PRO+: flat, no orders, 1 minute before/during/after major news; Test free** (verified)
  - "All PRO and PRO+ accounts must be out of all positions, and have no open orders, one minute before, during, and after the major news event." [P1]
- `automation_terms` = **no trading bots; discretionary traders only** (verified)
  - "We are looking for discretionary traders, not automated trading robots." [P1]
- `sizing_or_gambling_terms` = **50 executions/day on PRO; other sizing/gambling rules UNVERIFIED (Terms unreadable)** (verified)
  - "In the PRO Accounts, we ask that you do no more than 50 executions per day." [P1]
- `other_conduct_bearing` = **close by session end (17:00 EST per rules string; CQG violation string says 16:55 ET and no new positions 16:55-17:00 ET); up to 3 PRO resets; sim commissions $4.50 mini / $1.50 micro round trip** (verified)
  - "hold open positions past 16:55 ET" [P1]
  - "We give you the opportunity to reset your PRO Account up to three times." [P1]
  - ""table-test-13":"$4.50/$1.50 RT","table-pro-13":"$4.50/$1.50 RT"" [P1]
  - note: 17:00 EST vs 16:55 ET: two UI strings differ (the CQG one may be platform-specific).
- `permitted_products` = **futures listed on CME, COMEX, NYMEX, CBOT (no stocks, options, forex, crypto, CFDs)** (verified)
  - "Our platform grants access to an extensive range of futures products exclusively listed on esteemed exchanges, including CME, COMEX, NYMEX, and CBOT." [P1]
  - note: NQ/MNQ specifically: UNVERIFIED (product list behind 'What Futures Can I Trade?', not readable).

### Legends Trading (The Legends Trading Group, Inc.) (`legends`) -- UNDETERMINED

**Pages quoted** (key: URL; article id; the page's own date as shown; all read 2026-11-15)

- [P1] https://thelegendstrading.com/
- [P2] https://www.legendstrading.com/legends-program
- [P3] https://thelegendstrading.com/terms-conditions; page date: This agreement is in effect as of Feb 20, 2023.
- [P4] https://thelegendstrading.com/plans


Official domains: thelegendstrading.com, knowledge.thelegendstrading.com, dashboard.thelegendstrading.com. Read 2026-11-15.
Plan captured: Elite 50K (screen only; verdict UNDETERMINED).
Verdict: **UNDETERMINED** -- EOD drawdown on the Master (funded) stage and multiple accounts are stated, but every conduct rule lives on knowledge.thelegendstrading.com, which serves a Cloudflare block (WebFetch refused too).

Unreadable (not worked around):
- https://knowledge.thelegendstrading.com/ -- 403 Cloudflare challenge to curl; WebFetch refused (HTTP 403). This is the firm's rules knowledge base ('Visit our help center'), so conduct rules, payout gates and account limits are unread.

Plans seen:
- Elite 50K (one-time): drawdown EOD trailing $2,200; no DLL; consistency evaluation 40%, funded Master stage: 30% payout gate per homepage (details UNVERIFIED)
  - "$2,700 Profit Target - $2,200 EOD trailing max loss - Daily Loss Limit: None - Consistency: 40% - Contracts: 4 Minis / 40 Micros - Activation Fee: None" [P1]
- Apprentice 50K (monthly subscription): drawdown EOD trailing $2,000; consistency evaluation 30%, funded Master stage: 30% (UNVERIFIED details)
  - "3.000 profit goal - $2,000 EOD trailing max loss - Consistency 30% - 4 days - $99 Activation Fee" [P1]
- Straight to Master 50K (one-time): drawdown trailing $2,000 (card does not say EOD; FAQ says EOD Max Drawdown on Straight To Master); consistency evaluation 30%, funded 30% (UNVERIFIED details)
  - "$3,000 profit goal - $2,000 trailing max loss - Consistency 30% - 10 days" [P1]

identity quotes:
- "At Legends Trading we are dedicated stock market traders who specialize in options trading." [P2]
- "Welcome to Legends Trading. This website is owned and operated by The Legends Trading Group, Inc." [P3]

**Screen**

- `drawdown_eval` = **eod_trailing; $2,200** (verified)
  - "$2,700 Profit Target - $2,200 EOD trailing max loss - Daily Loss Limit: None" [P1]
  - "We calculate your Max Drawdown at the end of each trading day." [P1]
  - note: Lock level not stated on readable pages.
- `drawdown_funded` = **eod (Master stage 'EOD Max Drawdown'); amount and lock UNVERIFIED** (verified)
  - "On a Master or Straight To Master account, if you exceed your EOD Max Drawdown, your account will liquidated and you will need to purchase a Reset if you plan to continue trading." [P4]
- `consistency_eval` = **40% (Elite); exceeding it 'adjusts the extra' rather than failing** (verified)
  - "Daily Loss Limit: None - Consistency: 40% - Contracts: 4 Minis / 40 Micros" [P1]
  - note: Mechanics (best-day share of what) UNVERIFIED.
- `consistency_funded` = **30% consistency gates payouts (Master stage), mechanics UNVERIFIED** (verified)
  - "Our 30% consistency rule allows flexibility. If you exceed it, we adjust the extra—no account deactivation, no penalties." [P1]
  - "Once you meet the consistency rule, you can request payouts—up to twice per month." [P1]
  - note: The homepage does not say in so many words that the 30% rule applies at the Master stage; the payout sentence implies a consistency gate on payouts.
- `max_funded_accounts` = **multiple accounts allowed, up to $1,500,000 total; per-person count UNVERIFIED** (verified)
  - "Trade up to $1,500,000 on multiple accounts" [P1]
  - "Yes. You can manage multiple accounts at one time using the same credentials." [P4]
  - note: Not stated whether the $1.5M applies to funded (Master) accounts or evaluations, or per household.
- `copy_trading` = **UNVERIFIED** (UNVERIFIED)
  - looked at: https://thelegendstrading.com/ ; https://thelegendstrading.com/plans ; https://thelegendstrading.com/terms-conditions (knowledge base blocked)
- `opposite_positions` = **UNVERIFIED** (UNVERIFIED)
  - looked at: https://thelegendstrading.com/ ; https://thelegendstrading.com/plans ; https://thelegendstrading.com/terms-conditions (knowledge base blocked)
- `news` = **UNVERIFIED** (UNVERIFIED)
  - looked at: https://thelegendstrading.com/ ; https://thelegendstrading.com/plans ; https://thelegendstrading.com/terms-conditions (knowledge base blocked)
- `automation` = **UNVERIFIED** (UNVERIFIED)
  - looked at: https://thelegendstrading.com/ ; https://thelegendstrading.com/plans ; https://thelegendstrading.com/terms-conditions (knowledge base blocked)
  - note: The Terms of Service clause on 'automated ... means' concerns access to the website's Resources, not order entry.
- `sizing_gambling` = **UNVERIFIED** (UNVERIFIED)
  - looked at: https://thelegendstrading.com/ ; https://thelegendstrading.com/plans ; https://thelegendstrading.com/terms-conditions (knowledge base blocked)
- `note`: The readable pages also do not give a per-person account count or the Master-stage drawdown amount.

**Terms (`terms`)**

- `note`: Partial: only what the readable plan pages state for Elite 50K; the verdict is UNDETERMINED, so full terms were not pursued.
- `eval_profit_target` = **2700** (verified)
  - "$2,700 Profit Target - $2,200 EOD trailing max loss" [P1]
- `eval_drawdown_amount` = **2200** (verified)
  - "$2,700 Profit Target - $2,200 EOD trailing max loss" [P1]
- `eval_daily_loss_limit` = **none** (verified)
  - "$2,200 EOD trailing max loss - Daily Loss Limit: None" [P1]
- `eval_position_limit` = **4 minis / 40 micros** (verified)
  - "Max 4 Minis / 40 Micros" [P1]
- `eval_fee` = **$149 one-time list; $96.85 with code LTG** (verified)
  - "$149 $96.85 / one time Save $52.15 with code LTG" [P1]
  - note: Banner says 45% off Elite, but $96.85 / $149 is 35% off; the card's own saving line is quoted.
- `activation_fee` = **none** (verified)
  - "Contracts: 4 Minis / 40 Micros - Activation Fee: None" [P1]
- `payout_split` = **90%** (verified)
  - "Join live funded after 2nd payout, and keep your 90/10 split — a unique industry offer." [P1]
- `payout_frequency_gate` = **after meeting the consistency rule; up to twice per month** (verified)
  - "Once you meet the consistency rule, you can request payouts—up to twice per month." [P1]
- `payout_processing_days` = **1-5 days (stated for funded accounts with funding partners)** (verified)
  - "Simply log into the client portal and request funds which will be processed within 1-5 days." [P4]
- `funded_type` = **Master simulation stage; 'live funded after 2nd payout'** (verified)
  - "After passing the challenge, enter the Master Simulation stage. Manage risk and earn real rewards from your profitable trades" [P1]

**Identity note** (reader's section)

- The starting point given, legendstrading.com, is a different business: 'LegendsTrading LLC', an options-trading signals and education Discord ($149/month chat), with no prop evaluation. The futures prop firm 'Legends Trading' is The Legends Trading Group, Inc. at thelegendstrading.com (Calabasas, CA); that URL was located with a web search (search text not used as evidence) and its identity read from its own Terms of Service and plan pages.

**Access note** (reader's section)

- thelegendstrading.com Terms of Service clause (c) says 'You specifically agree not to access (or attempt to access) any of our Resources through any automated, unethical or unconventional means.' Three pages (home, plans, terms) were fetched by curl before it was read; no further pages were fetched.

**Plan note** (reader's section)

- Cards carry no plan label in the text; mapped to the tab order Apprentice / Elite / Straight to master (monthly cards with '80% off' = Apprentice, matching the '80% off Apprentice' banner; one-time no-DLL 40% cards = Elite; '10 days' cards = Straight to master).

### Purdia Capital (Purdia Capital LLC) (`purdia`) -- UNDETERMINED

**Pages quoted** (key: URL; article id; the page's own date as shown; all read 2026-11-15)

- [P1] https://purdia.com/assets/index-Dq3XZwvY.js


Official domains: purdia.com. Read 2026-11-15.
Plan captured: None.
Verdict: **UNDETERMINED** -- No rendered rule page or help centre can be read (JavaScript app, API-loaded knowledge base). On the bundle's text alone the 'Freedom' 50k EOD Evaluation would pass (no consistency, 3 accounts, manual trading allowed), but the funded drawdown type is unstated and the two embedded catalogs conflict.

Unreadable (not worked around):
- https://purdia.com/ -- single-page JavaScript app: the HTML is an empty shell (<div id="app">); every path (/robots.txt, /sitemap.xml) returns the same shell
- https://purdia.com/rules, /knowledgebase, /trading-policy, /terms -- not fetched as pages: client-side routes of the same shell; the knowledge base loads at run time from an API (/api/v1/workspaces/.../records), which was not called
- https://help.purdia.com/ -- host does not resolve (curl: Could not resolve host)
- https://purdia.com/rules (WebFetch) -- one WebFetch attempt did not run (the tool's safety check returned no verdict); not retried

Plans seen:
- 50k EOD Evaluation - 'Lower Price' option: drawdown EOD $2,000 (evaluation); funded type not stated; consistency evaluation 20% (one catalog), funded 20% / 25% / 30% / 30% across 4 payout cycles, then review for live
  - ""evaluations":{"funding":"After you pass","payouts":"Every 5 days","consistency":"20%","minDays":"None"}" [P1]
- 50k EOD Evaluation - 'Freedom - No Consistency Rule' option: drawdown EOD $2,000 (evaluation); funded type not stated; consistency evaluation none, funded none; 10 min days; daily payouts once qualified
  - ""evaluations":{"funding":"After you pass","payouts":"Daily once qualified","consistency":"None","minDays":"10"}" [P1]
- Instant / Static instant-funded and 'Pilot' accounts (no evaluation): drawdown EOD (instant) or static; consistency evaluation n/a, funded 20% (Lower Price) or none (Freedom)
  - "Lower Price gives you a more affordable account with a consistency rule, while Freedom — No Consistency Rule lets you trade without consistency restrictions for a higher price." [P1]

**Screen**

- `drawdown_eval` = **eod ($2,000 on 50k)** (verified)
  - "slug:"50k-eod-evaluation",title:"50k EOD Evaluation",subtitle:"$50,000 Simulated Capital",flag:"EOD",params:[{profitTarget:"$3,000"},{consistencyRule:"20%"},{drawdownEod:"$2,000"},{dailyLossLimit:"$1,000"}" [P1]
  - note: Bundle text only. Trailing vs static-after-lock not stated for this plan.
- `drawdown_funded` = **not stated** (UNVERIFIED)
  - looked at: raw/purdia/bundle.txt (program cards, FAQ, Terms, Trading Policy)
  - note: Funded rules sit in the API-loaded knowledge base.
- `consistency_eval` = **conflicting catalogs: 20% ('Lower Price') or none ('Freedom'); a second catalog card for the same plan shows no consistency field** (verified)
  - "slug:"50k-eod-evaluation",title:"50k EOD Evaluation",subtitle:"$50,000 Simulated Capital",flag:"EOD",params:[{profitTarget:"$3,000"},{minDays:"5"},{contractSize:"5 Minis / 50 Micros"},{drawdownEod:"$2,000"},{dailyLossLimit:"$1,000"},{profitSplit:"90%"},ki,_s],rulesHref:Va(),priceOriginal:"$179.00",priceMain:"$107.40",priceSuffix:"/ for the first month"" [P1]
  - note: The two catalogs disagree on min days (None / 5 / 10), consistency and activation fee ($0 vs $130).
- `consistency_funded` = **'Freedom' option: none; 'Lower Price': 20/25/30/30% by payout cycle** (verified)
  - "Freedom — No Consistency Rule has no consistency rule." [P1]
  - "A Lower Price 50k account has four payout cycles. Each cycle has a $2,000 target. Consistency steps up across those cycles: 20%, then 25%, then 30%, then 30%. After the fourth cycle, the account is reviewed for a live account." [P1]
- `max_funded_accounts` = **3 accounts (copy trading 'up to 3'); one trader per household/address/IP** (verified)
  - "You can trade up to three accounts. Copy trading is allowed." [P1]
  - "it={copyTrading:3}" [P1]
  - "Unless Purdia Capital grants an exception in writing, only one trader may operate accounts from a given household, residential address, or IP address." [P1]
  - note: The FAQ answer may belong to one program; the catalog sets copyTrading:3 on evaluation cards.
- `copy_trading` = **own accounts only, within product limits** (verified)
  - "Copying trades across a single trader's own accounts is permitted only within published product limits and remains subject to all other rules in this Policy." [P1]
- `opposite_positions` = **hedging prohibited, including offsetting positions in correlated instruments (long ES / short NQ)** (verified)
  - "Hedging is prohibited. This includes holding offsetting positions in closely correlated instruments, such as long ES while short NQ, long CL while short QM, or long 6E while short DX." [P1]
- `news` = **allowed (benefit list)** (verified)
  - "News Trading is Allowed" [P1]
  - note: From a benefits list that may be specific to one program.
- `automation` = **fully automated trading prohibited; semi-automated tools may be allowed with active oversight** (verified)
  - "Fully automated trading is strictly prohibited. This includes unattended systems, 24/7 strategies, and set-and-forget systems that execute trades without active real-time trader management." [P1]
  - "Automation is only permitted in the form your program describes. Undisclosed bots, unapproved copy trading, or latency abuse can trigger review or violations." [P1]
  - note: No date seen on the Terms block; the only 'last updated' string in the bundle (June 7, 2026) closes the risk-disclosure block.
- `sizing_gambling` = **not stated beyond a general anti-exploit clause** (UNVERIFIED)
  - looked at: raw/purdia/bundle.txt (Terms 'Prohibited Trading Practices', Trading Policy)

**Source note** (reader's section)

- Every quote below is from the site's own JavaScript bundle https://purdia.com/assets/index-Dq3XZwvY.js (saved as raw/purdia/bundle.txt), which holds the text the app renders (Terms, Trading Policy, FAQ, program cards). These strings were not seen rendered. The bundle holds two program catalogs that differ for the same 50k EOD Evaluation, and it is not possible to tell which one the live site shows.

### The Futures Desk (TS TFD Buyer, LLC; Topstep affiliate) (`futuresdesk`) -- FAIL

Verdict: **FAIL** -- At most 2 accounts per trader (homepage FAQ): not several funded accounts.

Struck (E-020): the firm's own terms forbid automated retrieval -- Terms & Conditions: "Using manual or automated software, devices, or processes to "crawl" or "spider" any web pages within the Sites or Services." (as recorded under E-009). Removed on 2026-11-16 (Q-34): the firm's saved pages, the terms and quotes its file held, and this section; its plans are read, if ever, only through the operator's browser or with the firm's written permission.
