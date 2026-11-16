# Other firms' futures contracts, read on their own pages (Q-12, 2026-11-15)

Scout note for TASK_QUEUE Q-12, the groundwork for family C (bootstrap 6.3 C; Stage 2's handoff 3.3). Brief:
`docs/briefs/Q-12_2026-11-15.md`. Light work only: web pages read, nothing run, no data read, no outcome computed.
**Nothing here can be used by code yet.** A firm rule becomes usable only when the rules-verifier records it in
`config/rules_extended.yaml` / `docs/RULES_CURRENCY.md` under a decision row (CLAUDE.md, "Firm rules"). This note is
the source list for that work.

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
  - The Trading Pit: "One Account Per IP / Network".
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
- **Some sites' own terms forbid automated reading.** These terms forbid automated retrieval, crawling or scraping
  of the site:
  - Tradeify: "use any robot, spider, scraper or other automatic device ... to access, harvest, monitor, copy or use
    the Site" without permission.
  - The Trading Pit, GTC 4.5.2: "automated retrieval or extraction of data (scraping, crawling, or similar methods)
    without our express written permission".
  - Goat: "Harvesting, scraping, or otherwise collecting any information from the Sites ... without our prior
    written consent".
  - Alpha Futures: "any automated use of the system, such as ... web scraping robots".
  - The Futures Desk: the readers report a "crawl" clause; it is in a script-rendered page and not quoted here.

  These reads were a few dozen public GETs at one a second, and readers stopped fetching from a site once they saw
  its clause. **Future re-reads of these sites should go through the operator's browser** (as Stage 2 D-574/D-575
  did for Lucid's prices) or with the firm's written permission. This is recorded here, not resolved.

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
| FunderPro Futures (Beginner, Mid-Level 50K) | EOD trailing, locks at start after the first reward | 40 % / **50 %** | 5 | GTC 13.4 bars "shared IP addresses, or any other technical or operational setup that enables coordinated, linked, or non-independent trading behaviour, whether between accounts owned by the same Client"; >30 % of margin on one idea deemed excessive; Beginner funded ±2 min news (GTC: all plans) | **PASS** |
| DayTraders.com (EOD 50K) | EOD trailing, stops at start | 50 % / **30 % per cycle** | 5 EOD Pro (15 sim in all; one login per household) | hedging banned incl. correlated; news allowed; Martingale banned; on a live call the sim accounts close and excess sim balance is generally forfeited | **PASS** |
| The Trading Pit (Futures Prime 50K) | EOD trailing $2,000 | 40 % / none | 5 | **"One Account Per IP / Network -- accessing multiple accounts from the same IP address or network is not allowed."**; news: help centre "allowed" vs GTC ±2 min; gambling policy; > 50 % of profit from trades ≤ 15 s flagged | **PASS** (the IP clause needs a written answer before any multi-seat use) |
| Aqua Futures (Daily 50K; Flex Daily Loss 50K) | EOD trailing | 40 % (Daily), 50 % (Flex) / none | 5 | bots banned (hand entry fine); ≥ 50 % of trades and profit held > 10 s; average reward-to-risk ≥ 0.3; < 100 trades a day; "Account Rolling"/"Account Stacking" banned; 7 days without a trade closes the account | **PASS** |
| Alpha Futures (Standard 50K; Advanced 50K) | EOD trailing, stops at start | Std 50 % / **40 %**; Adv 40 % / none | Std 5, Adv **3** per household (pages conflict) | bots banned (hand entry fine); Standard funded ±2 min red-folder news; "All or Nothing", rolling/stacking banned; tight-bracket fill exploitation and < 10-tick/< 2-min scalping banned; T&C 1.3.2: "maintain the same level of risk" | **PASS** |
| Tradeify (Select 50K) | EOD trailing $2,000 | 40 % / none | 5 per individual and household | Funded Trader Agreement: opposite positions banned "without regard to intent" incl. the Equity Index group and other firms; "avoid maximum or larger contract sizes", "consistent ... size, stops, and targets"; help centre (which governs) unreadable | **PASS** (11 terms UNVERIFIED) |
| BluSky (Launch 50K; Orbit 50K) | Launch: **static** ($3,000 start, $100 floor); Orbit: EOD trailing, locks at start | Launch 50 % (55 % on the homepage), then a 34 % Buffer / none; Orbit none / 40 % | **3** | hedging banned incl. correlated and across firms; a 3-breach clause can cut the trader to 1 account; $10,000 total profit forces a Brokerage Review | **PASS** |
| Earn2Trade (Gauntlet Mini 50K -> LiveSim) | EOD trailing (Live is intraday) | 30 % / none | **3** (at most 1 Live) | "copy-trading and batch execution across multiple accounts is not permitted" (enter each account separately); news allowed | **PASS** |
| FundedNext Futures (Flex 50K) | EOD trailing $1,500, locks $50,100; the first payout resets it there | 40 % / none | 5 per user and household; 10 issued a month | "Account rolling" banned; tight-bracket fill exploitation banned; trades < 10 s making ≥ 40 % of cycle profit deducted; the Disciplined Trader Program bans news | **PASS** |
| TradeDay (Fast Pass EOD 50K; Quick Pay EOD 50K) | Fast Pass: EOD trailing; Quick Pay: **intraday** | FP 45 % / **45 %** (accounts from 2026-07-26); QP 30 % / none | 5 Funded Sim | "auto-liquidate all open positions 2 minutes before TradeDay's tier 1 economic data releases"; no third-party bots or API; > 200 trades a day banned | **PASS** (QP on the no-consistency leg) |
| Top One Futures (Elite Daily V2 50K) | EOD trailing, locks start + $100 | 40 % / none | 5 per household, **evaluations included** | funded ±2 min: "Your trade must not be closed by any means during the restricted news window"; 10-second minimum hold; batch-buying evaluations and letting most fail banned; automation banned (hand entry required); live move disables the other accounts | **PASS** |
| FXIFY Futures / Futureify (Flex 50K) | EOD trailing, locks at start after the first payout | 50 % / **40 %** | 5 **in total, evaluations included** | tight-bracket exploitation and < 10-tick micro-scalping banned; rolling banned; homepage says "Live account credentials", FAQ says simulated | **PASS** |
| Funded Futures Network (STEADY 50K) | EOD trailing, locks start + $100 | 52 % / none | 5 | funded: "no positions or orders (including limit orders) ... 1 minute before and 1 minute after the release"; flat by 4:50 PM ET; Live Review after 4 payouts closes every sim account | **PASS** (rules page and help centre unreadable) |
| My Funded Futures (Rapid EOD 50K; Pro 50K) | EOD trailing, locks + $100 (Pro: static at $50,100 after the first payout) | Rapid EOD 30 % / none; Pro 50 % / no numeric rule | Rapid EOD **3**; 5 across 25K/50K | Rapid EOD funded: no positions or orders ±2 min of Tier 1 releases; "tight brackets to gain from favorable fills" banned; help allows copying, Terms 23.1.3.3 bar it "in a manner that provides an unfair advantage"; a $10,000 day moves you Live and suspends every sim account | **PASS** |
| Phidias (Premium 50K; Express to Live 50K) | EOD trailing, stops at $50,100 (E2L static $650) | none / **30 %** (E2L none) | 5 per plan type, 15 per household/company/IP | robots banned (hand entry fine); consistent position sizes required; a discretionary live move that cannot be refused | **PASS** |
| Goat Funded Futures (Flex 50K) | EOD trailing, locks at start | 50 % / none | 5 Flex | **1-minute rule**: ≥ 70 % of closed trades and ≥ 70 % of net profit from trades held > 1 minute, else the cycle's sub-minute profit is deducted (rule from 9-10 Nov 2026); funded ±2 min news; VPS banned, "you personally place and manage your trades"; payouts only on the 5th-8th and 20th-23rd, 3 % fee | **PASS** |
| Bulenox (Qualification 50K Option 2 -> Master) | EOD (the option carries to Master) | not stated / a Master consistency rule, % UNVERIFIED | 5 Master-level | copiers and news allowed; Terms (Oct 2026): third-party trading technology needs approval | **PASS** (16 terms UNVERIFIED; help centre unreadable) |
| Take Profit Trader (50K Test -> PRO) | **intraday** trailing (PRO+, live, is EOD) | 50 % / none | 5; 10 activations per 30 days | "No trading bots" (hand entry is what they want); PRO flat with no open orders 1 min around major news; max 50 executions a day; no counter positions | **PASS on the no-consistency leg only** (13 terms UNVERIFIED; terms and help centre blocked) |
| Legends Trading (Elite 50K) | EOD (Master stage) | 40 % / 30 % gates payouts | "multiple", up to $1.5M | conduct rules all on a blocked knowledge base | **UNDETERMINED** |
| Purdia Capital ("Freedom" 50K EOD) | not stated | none (Freedom) | 3 | own-account copying; hedging banned incl. correlated; fully automated trading banned; its two embedded catalogs conflict | **UNDETERMINED** (no readable rule page) |
| The Futures Desk | "Static or EOD" (homepage) | -- / none | **2 per trader** | Topstep affiliate (TS TFD Buyer, LLC); funded accounts are live brokerage accounts | **FAIL** (2 seats) |
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

- **FunderPro Futures (FunderPro Ltd., Malta)** `consistency_eval`: Conflict: the site's tooltip (funderprofutures.com and /how-it-works) still describes a 45% rule ('If daily profit exceeds 45% of the target, the excess will be added to your target'), and the at-a-glance article lists 'Violating the consistency rule at the time of passing the profit target' among breach causes.
- **FunderPro Futures (FunderPro Ltd., Malta)** `consistency_funded`: Conflict: help-centre articles (July 2026) say 50%; the homepage tooltip says 45% (the legacy value).
- **FunderPro Futures (FunderPro Ltd., Malta)** `copy_trading`: Conflict: GTC clause 13.4 prohibits any 'shared devices ... shared IP addresses, or any other technical or operational setup that enables coordinated, linked, or non-independent trading behaviour, whether between accounts owned by the same Client or multiple Clients' (quoted under other_conduct_bearing). Read literally it clashes with the advertised own-account copy trading.
- **FunderPro Futures (FunderPro Ltd., Malta)** `news`: Conflict: GTC 10.1 and 13.9 restrict opening positions within 2 minutes of Economic Calendar releases without a plan distinction.
- **FunderPro Futures (FunderPro Ltd., Malta)** `sizing_gambling`: Conflict: article 378635 says 'Yes — martingale strategies are permitted.'
- **FunderPro Futures (FunderPro Ltd., Malta)** `eval_consistency_rule`: See screen note: 45% tooltip conflict; at-a-glance lists violating it at the time of passing as a breach cause.
- **FunderPro Futures (FunderPro Ltd., Malta)** `funded_consistency_rule`: Homepage tooltip says 45% (conflict).
- **FunderPro Futures (FunderPro Ltd., Malta)** `payout_frequency_gate`: Not stated whether the 5 profitable days reset after each reward. The homepage still says 'Claim 3 rewards and unlock daily withdrawals' (legacy wording, conflict).
- **FunderPro Futures (FunderPro Ltd., Malta)** `payout_split`: The /how-it-works page still shows the legacy 60/70/80% ladder (conflict).
- **FunderPro Futures (FunderPro Ltd., Malta)** `copy_trading_terms`: See screen copy_trading for the own-account permission and the 13.4 conflict.
- **FunderPro Futures (FunderPro Ltd., Malta)** `other_conduct_bearing`: Overnight conflict: the 2026 at-a-glance article allows overnight holds; the 2025 article and the homepage ('At the end of each trading day, all positions are flattened for you') say positions are flattened daily.
- **FunderPro Futures (FunderPro Ltd., Malta)** `news_trading_terms`: Conflicts with GTC 10.1/13.9 (2-minute news restriction with no plan distinction).
- **DayTraders.com (Day Traders)** `copy_trading`: The Terms of Use (Last Updated March 5, 2025) prohibit 'Sharing trades and strategies with other users or making trades that were not Customer's own creation' -- about other users, not own-account copying; no conflict for own accounts.
- **DayTraders.com (Day Traders)** `other_conduct_bearing`: The Terms are older (last updated March 5, 2025) and link rules articles on help.daytraders.com that were not read; the help-centre articles are newer (~3 weeks). Our design is intraday, so the overnight conflict does not bind it.
- **Aqua Futures (AquaFutures / AquaFunded Futures)** `payout_min`: Conflict: $500 minimum payout vs $100 via crypto.
- **Aqua Futures (AquaFutures / AquaFunded Futures)** `payout_count_limit`: Conflict: the futures page blurb says three rewards then the account closes - that matches the Flex No Daily Loss article, not Flex Daily Loss. Help article value taken for Flex Daily Loss.
- **Alpha Futures** `max_funded_accounts`: CONFLICT: the Advanced product-page FAQ says up to 5; the help centre (July 27, 2026) and T&C Schedule 2 say Advanced = 3. Taken as 3.
- **Alpha Futures** `copy_trading`: CONFLICT between help centre and T&C wording; the help article explicitly addresses copying across one's own Alpha accounts ('Can I copy across my Alpha Futures Accounts?') and permits it.
- **Alpha Futures** `eval_min_days`: CONFLICT inside the T&C: clause 8.1.9 says 3, the Schedule 1 Advanced Evaluation row says 2. Homepage card and product page say 3. Taken as 3 (the 40% rule makes 3 the arithmetic minimum anyway).
- **Alpha Futures** `funded_drawdown_amount`: CONFLICT: product/home cards say $1,750 on the 50K Advanced Qualified; T&C Schedule 2 lists Advanced Qualified MLL as 4% (= $2,000). Taken as $1,750 (help centre/product pages, plan-specific).
- **Alpha Futures** `payout_split`: CONFLICT: the General Service Agreement (undated, older company number/address) still has a 70/80/90 tier; the help centre, product pages and T&C Schedule 2 ('90% split') say 90% from the start. Taken as 90%.
- **Alpha Futures** `payout_processing_days`: CONFLICT T&C (3) vs operational update (<= 5). The update follows an unnamed 'major change' around July 2026 that disrupted payouts; Premium accounts were refunded and Premium payouts are queued in batches.
- **Alpha Futures** `max_accounts`: CONFLICT: T&C Schedule 2 says an active Standard OR Advanced Qualified caps the user at 3; the help centre (same date, July 27, 2026) says only an active Advanced Qualified does (and Standard accounts bought before July 27, 2026 are capped at 3). Product page FAQ says 5 for Advanced. The month-old lead ('5 per household, 3 if an Advanced Qualified is active') matches the help centre.
- **Alpha Futures** `copy_trading_terms`: CONFLICT (see screen.copy_trading). Our design enters by hand on each account, so it does not depend on a copier.
- **Alpha Futures** `max_accounts`: CONFLICT with T&C Schedule 2 (see terms.max_accounts). Standard was relaunched July 27, 2026 ('Standard Account is back with some upgrades!').
- **Tradeify** `consistency_eval`: CONFLICT in meaning: the Select landing page FAQ defines the 40% as a share of green days, unlike the usual best-day share of profit; the governing definition is on the unreadable Help Center. The percentage (40%) is verified, its mechanics are not.
- **Tradeify** `eval_fee`: CONFLICT: the /select-plan page's size picker shows 50K at $111 (that page carries an expired 'ENDS 13 NOVEMBER' banner and lorem-ipsum template text). Price before/after coupon not certain.
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

Sources of the inputs, per row: FunderPro Futures Beginner 50K: funderpro.terms_beginner; Topstep 50K, No Activation Fee path (reference): Stage 2 rules.yaml: subscription_fee note (14289835); DayTraders.com EOD 50K: daytraders.terms; Topstep 50K Combine -> XFA, Standard path (reference): Stage 2 rules.yaml: combine_profit_target, combine_mll, xfa_mll_start, profit_split, subscription_fee, activation_fee, max_active_funded_accounts; The Trading Pit Futures Prime 50K: tradingpit.terms (split 'up to 80%'); Aqua Futures Daily 50K: aqua.terms_daily_50k; Alpha Futures Standard 50K: alpha.terms_standard; Aqua Futures Flex Daily Loss 50K: aqua.terms_flex_daily_loss_50k; FunderPro Futures Mid-Level 50K: funderpro.terms_midlevel; Lucid LucidFlex 50K: lucid 12945790, 12945815, 12945795, 12945796, 11404617 (read today); Tradeify Select 50K (Flex path): tradeify.terms; BluSky Launch 50K (Evaluation, then Buffer): blusky.terms; Earn2Trade Gauntlet Mini 50K -> LiveSim: e2t.terms ($139 activation is deducted from the first withdrawal: left out of F, so still a ceiling); FundedNext Futures Flex 50K: fundednext.terms; TradeDay Quick Pay EOD 50K: tradeday.terms_quick_pay_eod_50k (funded drawdown intraday); TradeDay Fast Pass EOD 50K: tradeday.terms_fast_pass_50k (K = 4 Sim payouts; the 5th request moves the account Live); Top One Futures Elite Daily V2 50K: topone.terms; FXIFY Futures (Futureify) Flex 50K: fxify.terms; Funded Futures Network STEADY 50K: ffn.terms (split conflict: FAQ 80/20); My Funded Futures Rapid EOD 50K: mffu.terms; Phidias Premium 50K, monthly path: phidias.terms; My Funded Futures Pro 50K: mffu.terms_pro50k; Alpha Futures Advanced 50K: alpha.terms; Phidias Premium 50K, one-time path: phidias.terms.

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
3. The Trading Pit Prime 50K: the split is "up to 80%" (discretionary); **one seat** until the IP clause is answered
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
  - The Trading Pit: does "One Account Per IP / Network" bar one person holding several funded accounts from home?
  - FunderPro: does GTC 13.4 ("linked ... trading behaviour ... between accounts owned by the same Client") bar
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
  - **Consistent sizing.** Tradeify's agreement, Alpha T&C 1.3.2 ("the same level of risk" as the evaluation),
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
rendered from the quote-checked firm files; no quote was retyped.

### FunderPro Futures (FunderPro Ltd., Malta) (`funderpro`) -- PASS

**Pages quoted** (key: URL; article id; the page's own date as shown; all read 2026-11-15)

- [P1] https://support.funderprofutures.com/en/articles/709493-important-changes-to-funderpro-futures-june-2026-and-what-they-mean-for-you; id 709493; page date: July 2, 2026
- [P2] https://support.funderprofutures.com/en/articles/709492-everything-you-need-to-know-about-the-mid-level-challenge; id 709492; page date: July 14, 2026
- [P3] https://support.funderprofutures.com/en/articles/726460-everything-you-need-to-know-about-the-professional-challenge; id 726460; page date: July 14, 2026
- [P4] https://support.funderprofutures.com/en/articles/709496-funderpro-futures-trading-rules-at-a-glance; id 709496; page date: July 14, 2026
- [P5] https://support.funderprofutures.com/en/articles/709498-funderpro-futures-reward-rules-and-requirements; id 709498; page date: July 2, 2026
- [P6] https://funderprofutures.com/
- [P7] https://funderprofutures.com/terms-conditions; id clause 4.10
- [P8] https://support.funderprofutures.com/en/articles/378635-what-strategies-and-tools-are-allowed-during-the-funderpro-futures-challenge; id 378635; page date: June 15, 2026
- [P9] https://funderprofutures.com/terms-conditions; id clause 10.3
- [P10] https://support.funderprofutures.com/en/articles/378530-can-i-trade-during-news-on-funderpro-futures; id 378530; page date: July 14, 2026
- [P11] https://funderprofutures.com/terms-conditions; id clause 13.13
- [P12] https://support.funderprofutures.com/en/articles/709491-everything-you-need-to-know-about-the-beginner-challenge; id 709491; page date: July 14, 2026
- [P13] https://support.funderprofutures.com/en/articles/709494-funderpro-futures-all-fees-and-costs-explained; id 709494; page date: July 2, 2026
- [P14] https://support.funderprofutures.com/en/articles/378467-what-is-the-maximum-number-of-accounts-allowed; id 378467; page date: June 15, 2026
- [P15] https://support.funderprofutures.com/en/articles/378417-do-i-trade-on-a-live-or-demo-account; id 378417; page date: October 23, 2025
- [P16] https://funderprofutures.com/terms-conditions; id clause 11.7
- [P17] https://funderprofutures.com/how-it-works
- [P18] https://support.funderprofutures.com/en/articles/378476-what-is-the-inactivity-rule; id 378476; page date: June 15, 2026
- [P19] https://funderprofutures.com/terms-conditions; id clause 13.10
- [P20] https://funderprofutures.com/terms-conditions; id clause 13.4
- [P21] https://funderprofutures.com/terms-conditions; id clause 13.11
- [P22] https://funderprofutures.com/terms-conditions; id clause 13.15
- [P23] https://support.funderprofutures.com/en/articles/378527-can-i-hold-trades-overnight; id 378527; page date: August 7, 2025
- [P24] https://support.funderprofutures.com/en/articles/378454-can-i-only-have-one-challenge-account-at-a-time; id 378454; page date: June 15, 2026
- [P25] https://funderprofutures.com/terms-conditions; id clause 10.2
- [P26] https://funderprofutures.com/terms-conditions; id clause 13.5


Official domains: funderpro.com (links 'Futures' to funderprofutures.com), funderprofutures.com, support.funderprofutures.com (Intercom help centre linked from funderprofutures.com). Read 2026-11-15.
Plan captured: Beginner Challenge $50K and Mid-Level Challenge $50K (both pass and differ materially in fees, payout caps, split and funded news rule); Professional listed only.
Verdict: **PASS** -- EOD trailing drawdown on funded (50% funded consistency), 5 funded accounts with own-account copy trading, nothing forbids manual bracket trading; GTC 13.4 'linked accounts / shared devices' clause and the 30%-margin clause are caveats.

Unreadable (not worked around):
- https://funderpro.com/futures/ -- 404 (guessed URL); the futures product lives on funderprofutures.com

Plans seen:
- Beginner Challenge $50K (purchases from 15 June 2026): drawdown EOD trailing $2,000, stops trailing at starting balance; locks at starting balance after 1st reward; consistency evaluation 40%, funded 50%
  - "Consistency rule: 40% during challenge, 50% on funded account" [P1]
- Mid-Level Challenge $50K: drawdown EOD trailing $2,000, same lock; consistency evaluation 40%, funded 50%
  - "End-of-day (EOD) trailing drawdown. It trails upward as your account grows and stops trailing once it reaches your initial starting balance." [P2]
- Professional Challenge $50K: drawdown EOD trailing $2,000, same lock; consistency evaluation 40%, funded 50%
  - "| Monthly Fee | $219 | $329 | $449 | $559" [P3]
- Classic (original) challenge, purchases before 15 June 2026 (legacy, no longer sold): drawdown EOD trailing; consistency evaluation 45%, funded 45% for first 3 rewards
  - "| Consistency rule (challenge) | 45% | 40%" [P1]

**Screen**

- `drawdown_eval` = **eod_trailing, stops trailing at starting balance** (verified)
  - "Your maximum drawdown is calculated at the end of each trading day, not intra-day." [P4]
  - note: No page says whether the breach is also checked intraday on equity; the wording suggests an end-of-day check.
- `drawdown_funded` = **eod_trailing; locks at starting balance after the 1st reward** (verified)
  - "| Maximum Drawdown | 4% ($50K) or 3% ($100K+), EOD trailing | Same, locks at starting balance after 1st reward" [P4]
- `consistency_eval` = **40%** (verified)
  - "No single trading day can account for more than 40% of your total profit during the challenge, or 50% on a funded account." [P4]
  - note: Conflict: the site's tooltip (funderprofutures.com and /how-it-works) still describes a 45% rule ('If daily profit exceeds 45% of the target, the excess will be added to your target'), and the at-a-glance article lists 'Violating the consistency rule at the time of passing the profit target' among breach causes.
- `consistency_funded` = **50%** (verified)
  - "| Consistency Rule (Funded) | 50% (no single day above 50% of total profit)" [P5]
  - "For Funded Accounts: the same 45% rule applies on your highest profit day." [P6]
  - note: Conflict: help-centre articles (July 2026) say 50%; the homepage tooltip says 45% (the legacy value).
- `max_funded_accounts` = **5 active funded; unlimited challenges; extra passes queue** (verified)
  - "You may hold a maximum of five (5) active FunderPro Futures Funded Phase accounts at any given time." [P7]
  - note: Per person ('per individual'); no household rule found on the pages read.
- `copy_trading` = **allowed between own accounts (advertised feature); copying other people prohibited** (verified)
  - "Yes — copy trading is allowed but only between your own accounts. You are not allowed to copy trades from other traders or from accounts you don't own." [P8]
  - "Copy trading across challenge and funded accounts" [P6]
  - note: Conflict: GTC clause 13.4 prohibits any 'shared devices ... shared IP addresses, or any other technical or operational setup that enables coordinated, linked, or non-independent trading behaviour, whether between accounts owned by the same Client or multiple Clients' (quoted under other_conduct_bearing). Read literally it clashes with the advertised own-account copy trading.
- `opposite_positions` = **prohibited** (verified)
  - "The wrongful or fraudulent use of hedging strategies, such as holding opposite positions in different accounts either alone or with other traders, is strictly prohibited." [P9]
- `news` = **challenge: allowed; funded: Beginner restricted 2 min before/after high-impact events, Mid-Level and Professional allowed** (verified)
  - "| Beginner | Allowed | Restricted (2-min window)" [P10]
  - note: Conflict: GTC 10.1 and 13.9 restrict opening positions within 2 minutes of Economic Calendar releases without a plan distinction.
- `automation` = **EAs/bots permitted if they do not exploit the system (third-party EAs: own the source code; no HFT/tick-scalping EAs)** (verified)
  - "Yes — automated trading tools, bots, and Expert Advisors (EAs) are permitted on FunderPro Futures, as long as they do not exploit system vulnerabilities and remain compliant with our trading rules." [P8]
  - note: Hand-entered trading is unaffected.
- `sizing_gambling` = **more than 30% of available margin on one trade idea (or correlated group) deemed excessive; abrupt lot-size changes may count as gambling** (verified)
  - "For the purposes of this clause, using more than thirty percent (30%) of the available margin on a single trade idea (or a group of correlated trades) will be deemed excessive and may constitute a breach of acceptable trading conduct." [P11]
  - note: Conflict: article 378635 says 'Yes — martingale strategies are permitted.'

**Terms (`terms_beginner`)**

- `eval_profit_target` = **3000** (verified)
  - "| Profit Target | $3,000 (6%) | $6,000 (6%) | $9,000 (6%)" [P12]
- `eval_drawdown_amount` = **2000** (verified)
  - "| Maximum Drawdown | $2,000 (4%) | $3,000 (3%) | $4,500 (3%)" [P12]
- `eval_drawdown_type` = **eod_trailing** (verified)
  - "The drawdown is calculated at end of day (EOD), not intra-day." [P12]
- `eval_drawdown_lock` = **stops trailing at the starting balance ($50,000)** (verified)
  - "It trails upward as your account grows but stops trailing once it reaches your initial starting balance." [P12]
- `eval_daily_loss_limit` = **none during the challenge** (verified)
  - "| Daily Pause (Challenge) | None | None | None" [P12]
- `eval_consistency_rule` = **40%** (verified)
  - "| Consistency Rule (Challenge) | 40% | 40% | 40%" [P12]
  - note: See screen note: 45% tooltip conflict; at-a-glance lists violating it at the time of passing as a breach cause.
- `eval_min_days` = **none** (verified)
  - "| Min Trading Days | None | None | None" [P12]
  - note: The 40% rule implies at least 3 profitable days.
- `eval_position_limit` = **5 standard / 50 micros** (verified)
  - "| Contracts (Std / Micro) | 5 / 50 | 10 / 100 | 15 / 150" [P12]
- `eval_fee` = **$79 per month (30-day subscription)** (verified)
  - "| Monthly Fee | $79 | $149 | $219" [P12]
  - note: If no active account exists at rebilling, a new account is created (GTC 5.1).
- `eval_reset_fee` = **69** (verified)
  - "| $50K | $69 | $79 | $189" [P13]
  - note: Columns: Beginner | Mid-Level | Professional. A reset does not change the billing date.
- `activation_fee` = **0** (verified)
  - "| Beginner | $0 (free)" [P13]
- `eval_count_limit` = **unlimited challenges** (verified)
  - "There’s no limit to the number of Challenge accounts you can purchase with FunderPro Futures." [P14]
- `eval_time_limit` = **none (billed every 30 days)** (verified)
  - "| Challenge Duration | Unlimited (billed every 30 days) | Unlimited (billed every 30 days) | Unlimited (billed every 30 days)" [P12]
- `funded_type` = **simulated; firm may copy trades to the live market itself; no trader live-transition rule stated** (verified)
  - "You receive a Funded Account, which still operates in a simulated environment," [P15]
  - "The Company may, in its sole discretion, decide to copy the simulated trades the Client makes within the FunderPro Futures Funded Phase into the live market." [P16]
  - note: Funded phase governed by a separate Funded Trader Service Agreement (GTC 11.6), not read.
- `funded_drawdown_amount` = **2000** (verified)
  - "| Maximum Drawdown | 4% ($50K) or 3% ($100K+), EOD trailing | Same, locks at starting balance after 1st reward" [P4]
- `funded_drawdown_type` = **eod_trailing** (verified)
  - "The maximum drawdown will trail based on your End-of-Day (EOD) balance until it reaches your starting balance, at which point it becomes fixed at that level." [P6]
- `funded_drawdown_lock` = **starting balance ($50,000): when trailing reaches it, or at the 1st reward** (verified)
  - "After your first reward request on a funded account, the drawdown locks at the starting balance regardless of how much profit you have earned." [P4]
- `payout_balance_consequence` = **reward deducted from balance; floor stays at starting balance ($50,000)** (verified)
  - "The reward amount is deducted from your account balance, but your drawdown level does not move down with it." [P5]
- `funded_daily_loss_limit` = **2% = $1,000, pause (not a breach); positions closed, frozen until 16:05 CT next day** (verified)
  - "| Daily Pause (Funded) | 2% of account size | 2% of account size | 2% of account size" [P12]
  - "If you lose this amount in a day, your positions will close, and your account will be frozen until 16:05 CT the next trading day." [P6]
- `funded_consistency_rule` = **50%** (verified)
  - "| Consistency Rule (Funded) | 50% | 50% | 50%" [P12]
  - note: Homepage tooltip says 45% (conflict).
- `funded_position_limit` = **scaling: 2 std ($0-$2,500 profit), 3 std (above $2,500), 5 std (above $5,000)** (verified)
  - "| Profit Earned | $50K | $100K | $150K" [P12]
  - "| $0 to $2,500 | 2 / 20 | 3 / 30 | 4 / 40" [P12]
  - "| Above $2,500 | 3 / 30 | 4 / 40 | 5 / 50" [P12]
  - "| Above $5,000 | 5 / 50 | 7 / 70 | 9 / 90" [P12]
- `funded_monthly_fee` = **none** (verified)
  - "There are no recurring fees on funded accounts." [P13]
  - note: Optional market data upgrades only (L1 CME free).
- `payout_min` = **250** (verified)
  - "| Minimum Reward Request | 0.5% of account size ($250 on $50K, $500 on $100K, $750 on $150K)" [P12]
- `payout_cap` = **$1,000 per request (2%); no lifetime cap stated** (verified)
  - "| Maximum Reward Request | 2% of account size ($1,000 on $50K, $2,000 on $100K, $3,000 on $150K)" [P12]
- `payout_frequency_gate` = **5 profitable days of $100+ (non-consecutive), minimum amount, 50% consistency; no fixed calendar cadence** (verified)
  - "| Requirements | 5 profitable trading days with $100+ profit each" [P12]
  - "On Beginner and Mid-Level, you can request once you meet the profitable-days requirement and minimum amount. There is no fixed calendar cadence." [P5]
  - note: Not stated whether the 5 profitable days reset after each reward. The homepage still says 'Claim 3 rewards and unlock daily withdrawals' (legacy wording, conflict).
- `payout_split` = **80% flat** (verified)
  - "| Reward Share | 80% flat (from your first reward onward)" [P12]
  - note: The /how-it-works page still shows the legacy 60/70/80% ladder (conflict).
- `payout_processing_days` = **same day (stated only in a stale section of /how-it-works)** (UNVERIFIED)
  - "Reward requests are processed on the same day." [P17]
  - looked at: ar-709498 (points to an article 'What reward payment methods do you support?' not found in the collections), ar-378526, ar-709494
  - note: The sentence sits next to the legacy 60/70/80% reward terms, so it may not describe the current product.
- `payout_fee` = **not stated** (UNVERIFIED)
  - looked at: ar-709494 (all fees), ar-709498, ar-378526, terms-conditions
- `payout_count_limit` = **not stated** (UNVERIFIED)
  - looked at: ar-709498, ar-709491, ar-709493, terms-conditions
- `max_accounts` = **5 active funded; unlimited challenges; extra passes queue and activate when a funded account is breached** (verified)
  - "You can have a maximum of 5 active Funded Accounts at any given time." [P14]
  - note: Old and new product accounts count together.
- `inactivity_rule` = **funded: terminated after 30 consecutive days of inactivity; challenges: none** (verified)
  - "However in the Funded Phase where you are no longer being billed monthly, we have a limit of 30 consecutive days of inactivity before we terminate the account." [P18]
  - note: Article sits in the legacy collection but is dated June 15, 2026.
- `copy_trading_terms` = **own accounts only** (verified)
  - "Copy trading, mirror trading, or using third-party tools like expert advisors (“EAs”) to replicate trades among multiple Clients is strictly forbidden." [P19]
  - note: See screen copy_trading for the own-account permission and the 13.4 conflict.
- `cross_account_hedging` = **prohibited, including opposing positions across own accounts** (verified)
  - "This includes, but is not limited to, executing opposing positions across multiple accounts, engaging in group trading arrangements, trade signaling, or any activity designed to create artificial trading activity or outcomes." [P20]
- `news_trading_terms` = **Beginner funded: no opening or closing 2 min before/after high-impact news; positions opened earlier may stay open** (verified)
  - "Positions opened before the restricted window can remain open, but new trades cannot be opened or closed during that timeframe." [P12]
  - note: A bracket exit filling inside the window would breach this on Beginner funded accounts.
- `automation_terms` = **permitted with limits** (verified)
  - "The use of third-party EAs designed for tick scalping, rollover scalping, or high-frequency trading strategies is prohibited. Clients using third-party EAs must own the source code of the software." [P21]
- `sizing_or_gambling_terms` = **30%-of-margin cap per trade idea; consistent lot sizes required** (verified)
  - "Abrupt or unjustified changes in lot sizes—such as trading one (1) lot followed by ten (10) lots without a clear strategic basis—may be deemed as reckless behavior or gambling rather than disciplined trading." [P22]
  - note: See screen sizing_gambling (13.13, 30% of margin).
- `other_conduct_bearing` = **no shared devices/IP/VPS setups enabling linked trading (13.4, literal reading conflicts with own-account copying); no weekend holding; overnight holding conflicting** (verified)
  - "The use of shared trading environments, shared devices, shared virtual private servers (“VPS”), shared IP addresses, or any other technical or operational setup that enables coordinated, linked, or non-independent trading behaviour, whether between accounts owned by the same Client or multiple Clients, is prohibited." [P20]
  - "| Overnight Holding | Allowed (positions flatten at EOD Friday) | Allowed (positions flatten at EOD Friday)" [P4]
  - "No, you cannot hold trades overnight or over the weekend." [P23]
  - note: Overnight conflict: the 2026 at-a-glance article allows overnight holds; the 2025 article and the homepage ('At the end of each trading day, all positions are flattened for you') say positions are flattened daily.
- `permitted_products` = **CME, COMEX, NYMEX, CBOT, EUREX incl. NQ, MNQ, ES, MES (cost per side NQ $1.90, MNQ $0.62)** (verified)
  - "| E-mini NASDAQ 100 | NQ | Sunday – Friday 17:00–16:00 CT" [P17]
  - "| Micro E-mini NASDAQ 100 | MNQ | Sunday – Friday 17:00–16:00 CT" [P17]

**Terms (`terms_midlevel`)**

- `eval_profit_target` = **3000** (verified)
  - "| Profit Target | $3,000 (6%) | $6,000 (6%) | $9,000 (6%) | $12,000 (6%)" [P2]
- `eval_drawdown_amount` = **2000** (verified)
  - "| Maximum Drawdown | $2,000 (4%) | $3,000 (3%) | $4,500 (3%) | $6,000 (3%)" [P2]
- `eval_drawdown_type` = **eod_trailing** (verified)
  - "End-of-day (EOD) trailing drawdown. It trails upward as your account grows and stops trailing once it reaches your initial starting balance." [P2]
- `eval_drawdown_lock` = **stops trailing at the starting balance** (verified)
  - "Once you are in profit by the drawdown amount, your downside is capped permanently." [P2]
- `eval_daily_loss_limit` = **none stated for the challenge (2% only on funded)** (verified)
  - "On the Funded Account, a 2% daily loss limit applies." [P2]
  - note: The Mid-Level table lists a Daily Loss Limit only for Funded; the at-a-glance article says the daily pause is 'not applicable during eval'.
- `eval_consistency_rule` = **40%** (verified)
  - "| Consistency Rule (Challenge) | 40% | 40% | 40% | 40%" [P2]
- `eval_min_days` = **none** (verified)
  - "| Min Trading Days | None | None | None | None" [P2]
- `eval_position_limit` = **5 standard / 50 micros** (verified)
  - "| Contracts (Std / Micro) | 5 / 50 | 10 / 100 | 15 / 150 | 20 / 200" [P2]
- `eval_fee` = **$89 per month** (verified)
  - "| Monthly Fee | $89 | $149 | $229 | $339" [P2]
- `eval_reset_fee` = **79** (verified)
  - "| Reset Fee | $79 | $129 | $199 | $289" [P2]
- `activation_fee` = **129** (verified)
  - "| Activation Fee | $129 | $129 | $129 | $129" [P2]
  - note: One-time, on passing.
- `eval_count_limit` = **unlimited challenges** (verified)
  - "There’s no restriction on how many Challenges you can purchase with FunderPro Futures." [P24]
- `eval_time_limit` = **none (billed every 30 days)** (verified)
  - "| Challenge Duration | Unlimited (billed every 30 days) | Unlimited (billed every 30 days) | Unlimited (billed every 30 days) | Unlimited (billed every 30 days)" [P2]
- `funded_type` = **simulated (as Beginner)** (verified)
  - "3. Pay the $129 activation fee and receive your simulated FunderPro Futures funded account." [P2]
  - note: No live-transition rule stated.
- `funded_drawdown_amount` = **2000** (verified)
  - "| $50K | $2,000 | 4%" [P4]
  - note: Same for all challenge types.
- `funded_drawdown_type` = **eod_trailing** (verified)
  - "| Maximum Drawdown | 4% ($50K) or 3% ($100K+), EOD trailing | Same, locks at starting balance after 1st reward" [P4]
- `funded_drawdown_lock` = **starting balance after the 1st reward (at-a-glance; the rewards article states it explicitly only for Beginner)** (verified)
  - "| Drawdown lock | After 1st reward | After 1st reward (unchanged)" [P1]
- `payout_balance_consequence` = **reward deducted; floor at starting balance after 1st reward** (verified)
  - "After your first reward request on a funded account, the drawdown locks at the starting balance regardless of how much profit you have earned." [P4]
- `funded_daily_loss_limit` = **2% = $1,000, pause not breach** (verified)
  - "| Daily Loss Limit (Funded) | 2% | 2% | 2% | 2%" [P2]
- `funded_consistency_rule` = **50%** (verified)
  - "| Consistency Rule (Funded) | 50% | 50% | 50% | 50%" [P2]
- `funded_position_limit` = **scaling: 2 std ($0-$2,500), 3 std (above $2,500), 5 std (above $5,000)** (verified)
  - "| $0 to $2,500 | 2 / 20 | 3 / 30 | 4 / 40 | 5 / 50" [P2]
  - "| Above $5,000 | 5 / 50 | 7 / 70 | 9 / 90 | 11 / 100" [P2]
- `funded_monthly_fee` = **none** (verified)
  - "Once activated, your monthly subscription stops and you trade without ongoing charges." [P13]
- `payout_min` = **200** (verified)
  - "| Minimum Reward Request | $200" [P2]
- `payout_cap` = **per request on 50K: 1st $1,500, 2nd $1,750, 3rd $2,000, 4th $2,500, 5th+ $3,500; no lifetime cap stated** (verified)
  - "| 1st | $1,500 (3%) | $3,000 (3%) | $4,500 (3%) | $6,000 (3%)" [P5]
  - "| 5th+ | $3,500 (7%) | $5,000 (5%) | $7,500 (5%) | $10,000 (5%)" [P5]
  - note: Columns: $50K | $100K | $150K | $200K.
- `payout_frequency_gate` = **5 profitable days of $200+ each, minimum $200, 50% consistency** (verified)
  - "| Requirements | 5 profitable trading days with $200+ profit each" [P2]
  - note: Whether the 5 days reset per reward is not stated.
- `payout_split` = **80% (1st) / 85% (2nd) / 90% (3rd onward)** (verified)
  - "| Reward Share | 80% (1st reward) → 85% (2nd) → 90% (3rd onward)" [P2]
- `payout_processing_days` = **see terms_beginner (stale same-day sentence only)** (UNVERIFIED)
  - looked at: ar-709498, ar-709492, how-it-works
- `payout_fee` = **not stated** (UNVERIFIED)
  - looked at: ar-709494, ar-709498, terms-conditions
- `payout_count_limit` = **not stated** (UNVERIFIED)
  - looked at: ar-709498, ar-709492
- `max_accounts` = **5 active funded (all FunderPro Futures types and old/new products together); unlimited challenges** (verified)
  - "Yes, as long as you are within the maximum number of accounts allowed." [P1]
  - note: See terms_beginner.max_accounts.
- `inactivity_rule` = **funded: 30 consecutive days** (verified)
  - "We do not have an inactivity rule for Challenges, as they are billed monthly every 30 days, covering costs for you to hold on to an account for as long as you like." [P18]
- `copy_trading_terms` = **own accounts only (see screen)** (verified)
  - "Yes — copy trading is allowed but only between your own accounts. You are not allowed to copy trades from other traders or from accounts you don't own." [P8]
- `cross_account_hedging` = **prohibited** (verified)
  - "Additionally, colluding to exploit opposite positions is prohibited, and any and all profits and losses generated by such prohibited practice will be annulled." [P25]
- `news_trading_terms` = **allowed in challenge and funded** (verified)
  - "News trading is allowed on FunderPro Futures Mid-Level accounts during both the evaluation and funded phases." [P2]
  - note: Conflicts with GTC 10.1/13.9 (2-minute news restriction with no plan distinction).
- `automation_terms` = **permitted with limits (as Beginner)** (verified)
  - "Clients must not use high-frequency trading (“HFT”) systems, AI-driven tools, or any mass data entry methods that manipulate or exploit inefficiencies in the system." [P26]
- `sizing_or_gambling_terms` = **as Beginner (13.13 30% margin cap; 13.15 lot consistency)** (verified)
  - "Engaging in gambling behavior, such as risking large portions of capital on a single high-stakes trade, one-sided bets or account rolling is strictly prohibited." [P11]
- `other_conduct_bearing` = **as Beginner: no weekend holding; 13.4 linked-setup clause** (verified)
  - "| Weekend Holding | No | No | No | No" [P2]
- `permitted_products` = **as Beginner** (verified)
  - "| Instruments | CME, COMEX, NYMEX, CBOT, EUREX | Same (unchanged)" [P1]

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

**Pages quoted** (key: URL; article id; the page's own date as shown; all read 2026-11-15)

- [P1] https://support.thetradingpit.com/en/articles/836071-futures-prime-rules; id 836071; page date: Updated over a week ago
- [P2] https://www.thetradingpit.com/futures
- [P3] https://support.thetradingpit.com/en/articles/836080-futures-prime-platforms-conditions; id 836080; page date: Updated over a week ago
- [P4] https://support.thetradingpit.com/en/articles/836068-futures-prime-how-it-works; id 836068; page date: October 6, 2026
- [P5] https://www.thetradingpit.com/general-terms-and-conditions; id GTC V5.08.26, Schedule B; page date: V5.08.26
- [P6] https://www.thetradingpit.com/general-terms-and-conditions; id GTC V5.08.26, 6.5.1.1; page date: V5.08.26
- [P7] https://www.thetradingpit.com/
- [P8] https://support.thetradingpit.com/en/articles/835066-costs-fees-extras; id 835066; page date: October 2, 2026
- [P9] https://support.thetradingpit.com/en/articles/836079-futures-prime-rewards; id 836079; page date: Updated over 2 weeks ago
- [P10] https://www.thetradingpit.com/general-terms-and-conditions; id GTC V5.08.26, A.3; page date: V5.08.26
- [P11] https://www.thetradingpit.com/general-terms-and-conditions; id GTC V5.08.26, A.7; page date: V5.08.26
- [P12] https://www.thetradingpit.com/general-terms-and-conditions; id GTC V5.08.26, A.8; page date: V5.08.26
- [P13] https://support.thetradingpit.com/en/articles/835070-trading-device-ip-network-policy; id 835070; page date: October 2, 2026
- [P14] https://www.thetradingpit.com/general-terms-and-conditions; id GTC V5.08.26, 6.8.1; page date: V5.08.26
- [P15] https://support.thetradingpit.com/en/articles/835071-gambling-policy; id 835071; page date: October 2, 2026


Official domains: thetradingpit.com, support.thetradingpit.com. Read 2026-11-15.
Plan captured: Futures Prime 50K.
Verdict: **PASS** -- Futures Prime 50K: EOD trailing drawdown on the Earning account and no Earning-phase consistency rule; 5 Earning accounts; hand-entered one-position bracket trades are allowed (stops recommended), subject to the GTC's 2-minute news-bracketing ban.

Plans seen:
- Futures Prime 50K (one-phase challenge): drawdown EOD trailing $2,000 on closed balance, locks at starting balance (challenge and earning); consistency evaluation 40% (raises target; never fails), funded none
  - "Applies to the Challenge only — never to a Futures Earning Account — and it never fails your account." [P1]
- Futures Instant 50K (no challenge): drawdown EOD trailing $2,000, fixed at starting balance; dynamic daily pause from $1,200; consistency evaluation n/a, funded 20% (best day <= 20% of total profit before payout)
  - "You can have maximum 2 Futures Instant accounts." [P2]

comparability quotes:
- "Equity indices (ES, NQ, YM, RTY and their micros)." [P3]
- "Once you pass, you receive a funded demo Earning Account where you can request rewards on the profit you generate." [P4]

**Screen**

- `drawdown_eval` = **eod_trailing; $2,000; locks at starting balance $50,000** (verified)
  - "Your Max Drawdown (see the table) trails your end-of-day balance — based on closed P&L, not intraday peaks — upward, until it reaches your starting balance, then locks." [P1]
- `drawdown_funded` = **eod_trailing; same $2,000 rule in the Earning phase** (verified)
  - "| Max Drawdown (Trailing EOD) | Challenge & Earning | Hard — Breach" [P1]
- `consistency_eval` = **40% of profit target per day; overshoot raises target to best day / 0.40 (accounts created on/after 14 July 2026)** (verified)
  - "Created on or after 14 July 2026 — the target is recalculated so your highest day equals 40% of it (Highest Day ÷ 0.40 = new target)." [P1]
- `consistency_funded` = **none** (verified)
  - "Applies to the Challenge only — never to a Futures Earning Account — and it never fails your account." [P1]
  - note: But the 'account rolling' signs include 'One trade or one day produces more than 40% of the net profit', and GTC A.2.4 makes 'consistency of the trading strategy' part of Compliant Trading Data for rewards.
- `max_funded_accounts` = **5 active Earning accounts; no limit on challenge purchases** (verified)
  - "In the Earning Phase you can hold a maximum of 5 active Earning accounts; if you pass a Challenge while already at the cap, the upgrade is queued until one of your Earning accounts closes." [P1]
  - note: Per-household not stated. CAVEAT: the Device/IP policy says 'accessing multiple accounts from the same IP address or network is not allowed' (read in context as several people's accounts, since one trader may hold 5).
- `copy_trading` = **allowed from own accounts only, up to 5 challenges or 5 earning accounts** (verified)
  - "You may copy trades, manually or automatically, across up to 5 of your own Challenges or 5 of your own Earning accounts." [P1]
- `opposite_positions` = **prohibited within an account, across own accounts, and in correlated instruments across accounts** (verified)
  - "This includes opposing positions in a single account, a BUY on one account and a SELL on another, and offsetting positions opened in correlated instruments across accounts." [P1]
- `news` = **CONFLICT: help centre says allowed on Futures Prime; GTC Schedule B prohibits opening or closing positions within 2 minutes before/after a high-impact release** (verified)
  - "Allowed on Futures Prime in both the Challenge and Earning Phase." [P1]
  - "News Bracketing: Placing or opening orders in anticipation of the release of high-impact economic data or events; in particular, opening or closing positions within two (2) minutes before or after such a release is prohibited;" [P5]
  - note: Safe default: no entry or exit (including a resting stop/target filling) within 2 minutes of a high-impact release. The GTC (6.6) say the most up-to-date list is in the Help Center, which says news trading is allowed; the futures page also lists 'News trading Allowed' for Instant.
- `automation` = **not prohibited as such; EAs with prohibited functions, HFT, and automated tools used to manipulate or evade monitoring are prohibited; only Replikanto Compliance Edition allowed as copier on NinjaTrader** (verified)
  - "AI and Automated Tools: Use of artificial intelligence, automated trading systems, ultra-high-speed tools, or mass data entry to manipulate the Trading Platform, circumvent our monitoring systems, or gain an unfair trading advantage in the generation of Trading Data; and" [P5]
  - "Yes, but only Replikanto FlowBots – Compliance Edition is permitted." [P3]
  - note: Hand entry raises no issue.
- `sizing_gambling` = **gambling policy (overleveraging, overexposure, one-sided bets, hyperactivity); impermissible risk allocation; account rolling; lot-size manipulation; micro-scalping flag (> 50% of profit from trades held <= 15 s)** (verified)
  - "6.5.1.1 using a disproportionate portion of the account balance or equity to open positions (impermissible risk allocation);" [P6]
  - "Automated monitoring flags accounts where, for example, over 50% of profits come from trades held 15 seconds or less, or where ultra-fast entries and exits are combined with disproportionate sizing." [P1]
- `note`: Two design-relevant frictions: (1) GTC news-bracketing ban conflicts with the help centre's 'news allowed'; (2) Earning-phase contract scaling starts at 2 standard / 20 micros on 50K per the futures page, versus the 5/50 limit in the rules article.

**Terms (`terms`)**

- `eval_profit_target` = **3000** (verified)
  - "| Account size | Profit Target | Max Drawdown | Daily Pause | Max Contracts (STD / Micro)" [P4]
  - "| $50,000 | $3,000 | $2,000 | $1,000 | 5 / 50" [P4]
- `eval_drawdown_amount` = **2000** (verified)
  - "| $50,000 | $3,000 | $2,000 | $1,000 | 5 / 50" [P4]
- `eval_drawdown_type` = **eod_trailing (closed P&L end-of-day balance)** (verified)
  - "Your Max Drawdown (see the table) trails your end-of-day balance — based on closed P&L, not intraday peaks — upward, until it reaches your starting balance, then locks." [P1]
  - "If your balance falls to the drawdown level, the account is breached." [P1]
- `eval_drawdown_lock` = **locks at starting balance ($50,000)** (verified)
  - "Your maximum drawdown will trail based on your End-Of-Day (EOD) balance until it reaches your starting balance, after which it will remain fixed at the starting balance amount." [P2]
- `eval_daily_loss_limit` = **Daily Pause $1,000 (soft: positions closed, paused until next day)** (verified)
  - "On Challenge Phase only. If your equity drops below the Daily Drawdown limit, open positions will be closed, and your account will be paused until the next trading day (16:05 CT)." [P2]
  - "| $50,000 | $3,000 | $2,000 | $1,000 | 5 / 50" [P4]
- `eval_consistency_rule` = **40% of profit target per day; overshoot raises target (best day / 0.40); never fails the account** (verified)
  - "Your highest trading day is capped at 40% of your Profit Target; going over simply raises the target." [P1]
- `eval_min_days` = **3** (verified)
  - "For the Challenge to register as passed you must place a trade on at least 3 unique trading days." [P1]
- `eval_position_limit` = **5 standard / 50 micro (fewer as balance falls)** (verified)
  - "$50K → 5 standard / 50 micro" [P1]
  - "There is no minimum, and the lower your current balance, the fewer contracts you’re allowed to trade." [P1]
- `eval_fee` = **$99 one-time (Black Friday code BF40 40% off until Nov 30)** (verified)
  - "Account Balance: $50,000 Price $99 One Time Fee" [P2]
  - "Valid on all Instant Accounts and Prime Challenges of $10K and up. Use code BF40." [P7]
  - note: Level 1 CME data free; Level 2 CME $16/month optional. Commissions $0.50 per standard/mini contract, $0.20 per micro.
- `eval_reset_fee` = **79** (verified)
  - "Reset $79 You can purchase a Reset anytime and as many times as you like, receiving a new account with the remaining challenge days." [P2]
  - note: A reset keeps the remaining challenge days; 'Extend' ($99) adds the initial 30 days. Reset breached accounts may face an activation fee (see activation_fee).
- `activation_fee` = **$0 for new accounts created on/after 26/03/2026 (existing and reset-breached accounts may pay one; futures page shows $129 struck to $0)** (verified)
  - "Activation fee: new accounts created on or after 26/03/2026 have no activation fee ($0). Existing accounts and reset breached accounts may be subject to an activation fee before progressing to the Earning Phase." [P4]
  - "Activation Fee $129 $0" [P2]
  - note: The costs article says reset breached accounts 'are subject to' an activation fee (firmer than 'may be'); amount for a reset account presumably $129, not stated explicitly.
- `eval_count_limit` = **no limit on purchases** (verified)
  - "There is no limit on how many Futures accounts you can purchase." [P1]
  - note: Copying the same strategy across more than 5 accounts 'can lead to upgrades being denied'.
- `eval_time_limit` = **30 days (extendable for $99)** (verified)
  - "Challenge duration: 30 days across all account sizes." [P4]
  - "Extend $99 Add the initial number of Challenge days to your account for more time to reach the profit target." [P2]
- `funded_type` = **simulated (demo) Earning Account with buying-power scaling; live transition not described for Prime** (verified)
  - "All trading takes place on demo accounts using simulated funds." [P4]
  - "In our Futures Prime Program, we will scale your Earning Account's buying power based on your end-of-day profit. Scale-ups will be calculated and adjusted daily at 16:00 CT." [P2]
- `funded_drawdown_amount` = **2000** (verified)
  - "| Max Drawdown (Trailing EOD) | Challenge & Earning | Hard — Breach" [P1]
  - "| $50,000 | $3,000 | $2,000 | $1,000 | 5 / 50" [P4]
  - note: Whether the Earning account starts with a fresh trail from $48,000 is implied, not stated.
- `funded_drawdown_type` = **eod_trailing** (verified)
  - "| Max Drawdown (Trailing EOD) | Challenge & Earning | Hard — Breach" [P1]
- `funded_drawdown_lock` = **locks at starting balance** (verified)
  - "Your maximum drawdown will trail based on your End-Of-Day (EOD) balance until it reaches your starting balance, after which it will remain fixed at the starting balance amount." [P2]
- `payout_balance_consequence` = **floor not stated to move at payout (it locks at the starting balance once reached); next reward needs balance above the last post-payout balance** (verified)
  - "Your balance must exceed your last post-payout balance (by at least $0.01) to request the next reward." [P2]
  - note: What a payout does to the drawdown level is not stated; the 50%-of-buffer cap keeps half the profit as cushion.
- `funded_daily_loss_limit` = **none since 14 July 2026 (Daily Pause removed from Earning accounts) - CONFLICT with the same article's summary table** (verified)
  - "Applies during the Challenge phase only. It was removed from Futures Prime Earning accounts on 14 July 2026." [P1]
  - "| Daily Pause (Daily Loss Limit) | Challenge & Earning | Auto-Close For The Day" [P1]
  - note: The futures product page agrees with 'Challenge Phase only'. Safe default for modelling: test both (no DLL, and a $1,000 soft pause).
- `funded_consistency_rule` = **none** (verified)
  - "| 40% Consistency (Raises The Target) * | Challenge only | Soft — Adjusts Target" [P1]
- `funded_position_limit` = **scaling by EOD profit (50K): 0-$2,500 profit 2 std / 20 micro; above $2,500 3 / 30; above $5,000 4 / 40 (futures page) - CONFLICT with rules article's 5 / 50 for 'Challenge & Earning'** (verified)
  - "| $50,000 ACCOUNT | $100,000 ACCOUNT | $150,000 ACCOUNT | 0-$2,500 Profit | 2 Standard / 20 Micros" [P2]
  - "| If Profit Above $2,500 | 3 Standard / 30 Micros" [P2]
  - "| If Profit Above $5,000 | 4 Standard / 40 Micros" [P2]
  - "| Max Contracts Per Account Size | Challenge & Earning | Position Limit" [P1]
  - note: Read: the product page's scaling table is specific to the Earning account; the rules page gives the ceiling. Safe default: 2 NQ / 20 MNQ at the start of the Earning phase.
- `funded_monthly_fee` = **none (only the one-time product fee; optional market-data add-ons are monthly)** (verified)
  - "The only expense on your part is the one-time initial purchase of one of our Challenges." [P8]
- `payout_min` = **UNVERIFIED (Prime: only 'positive net profit of at least $0.01' after the first reward; Instant has a $500 minimum)** (UNVERIFIED)
  - looked at: https://support.thetradingpit.com/en/articles/836079-futures-prime-rewards ; https://www.thetradingpit.com/futures ; https://www.thetradingpit.com/general-terms-and-conditions (Schedule A.6 refers to minimum amounts 'published on our Website')
- `payout_cap` = **per request: up to 50% of the current profit buffer, capped at $2,500 (50K); lifetime not stated** (verified)
  - "You can request up to 50% of your current profit buffer, capped by account size:" [P9]
  - "| $50,000 | $2,500" [P9]
- `payout_frequency_gate` = **5 profitable days of >= $150 (not necessarily consecutive) per reward; at most every 7 days; later rewards need net profit > $0 since the last payout** (verified)
  - "Second and later rewards: generate a positive net profit of at least $0.01 since your last payout, and complete 5 new profitable trading days, each with at least $150 profit." [P9]
  - "You can request a reward every 7 days." [P9]
  - "To request a reward, you must complete 5 profitable trading days with at least $150 profit per day, which do not need to be consecutive. You can request a reward every 7 days." [P2]
  - note: Changed 27 July 2026: daily threshold lowered from $200 to $150.
- `payout_split` = **up to 80% (discretionary: reward rate may be set below the maximum)** (verified)
  - "On Futures Prime, you can receive a reward of up to 80% of the notional profit you generate in the Earning Phase." [P9]
  - "The Reward rate may be set below the maximum Reward rate" [P10]
- `payout_processing_days` = **no later than 30 calendar days after TTP's determination; reviews generally within 14 days** (verified)
  - "payment shall be made by bank transfer or via approved payment service providers to the account registered in the Client Area, no later than thirty (30) Calendar Days after that determination." [P11]
  - "We generally complete reviews within fourteen (14) Calendar Days; if a review exceeds thirty (30) Calendar Days, we will inform you of its status and expected duration." [P12]
- `payout_fee` = **international transfer costs and FX losses borne by trader; fee schedule in the general rewards info (not read)** (verified)
  - "Costs for international transfers and exchange rate losses shall be borne by you." [P11]
  - "Withdrawal methods, currencies and reward fees follow The Trading Pit’s general reward policy — rewards are paid by bank wire or cryptocurrency." [P9]
- `payout_count_limit` = **UNVERIFIED (none stated)** (UNVERIFIED)
  - looked at: https://support.thetradingpit.com/en/articles/836079-futures-prime-rewards ; https://support.thetradingpit.com/en/articles/836071-futures-prime-rules ; https://www.thetradingpit.com/futures ; https://www.thetradingpit.com/general-terms-and-conditions
- `max_accounts` = **5 active Earning accounts; unlimited challenge purchases; one Client Account per user** (verified)
  - "In the Earning Phase you can hold a maximum of 5 active Earning accounts; if you pass a Challenge while already at the cap, the upgrade is queued until one of your Earning accounts closes." [P1]
  - "One Account Per IP / Network — accessing multiple accounts from the same IP address or network is not allowed." [P13]
  - note: The IP rule, read literally, would forbid one trader working 5 Earning accounts from one home network; in context (shared/coordinated access) it targets several people. A question to put to the firm's support in writing before relying on 5 accounts from one IP - not resolvable from the pages.
- `inactivity_rule` = **breach after 21 consecutive days with no trade (countdown from purchase)** (verified)
  - "If 21 consecutive days pass without placing a single trade, the account is considered inactive and breached." [P1]
- `copy_trading_terms` = **own accounts only, up to 5 challenges or 5 earning accounts, manual or automatic; copier failures are the trader's risk; >5 accounts on the same strategy can block upgrades** (verified)
  - "You may only copy from your own accounts. Copying from other traders or sources is prohibited. Copying between Futures Challenges and Futures Earning accounts is allowed." [P1]
  - "Running the same strategy across more than 5 accounts can lead to upgrades being denied." [P1]
  - "Copy Trading / Trade Coordination: Coordinated trading, or copying the trades of other traders or accounts;" [P5]
  - note: The GTC wording 'copying the trades of other ... accounts' reads broader than the help centre's own-account allowance; GTC 6.6 points to the Help Center as the up-to-date list.
- `cross_account_hedging` = **prohibited (same instrument or correlated instruments, within or across accounts; also coordinated external hedging with other firms)** (verified)
  - "A BUY and a SELL held at the same time is prohibited." [P1]
  - "in particular coordinated external hedging, copy trading, or arbitrage strategies carried out across accounts held with TTP, with Affiliated Companies, or with third-party proprietary trading firms or brokers" [P14]
- `news_trading_terms` = **CONFLICT: allowed (help centre, Prime rules) vs. no opening/closing within 2 minutes of a high-impact release (GTC Schedule B 'News Bracketing'); pattern of trading only around news may be reviewed** (verified)
  - "If our Risk Team identifies a consistent pattern of trading exclusively around news events in a way that resembles gambling behavior, excessive risk-taking, or an attempt to exploit extreme market volatility rather than sustainable trading performance, the Risk Team reserves the right to review the account and take appropriate measures in accordance with our Terms & Conditions." [P1]
  - "News Bracketing: Placing or opening orders in anticipation of the release of high-impact economic data or events; in particular, opening or closing positions within two (2) minutes before or after such a release is prohibited;" [P5]
- `automation_terms` = **Schedule B practices banned whether manual or automated; EAs with prohibited functions and manipulative automated tools banned; HFT banned; no blanket ban on automation found** (verified)
  - "Except where stated otherwise, the practices below are prohibited regardless of whether they are carried out manually or by automated means." [P5]
  - "Not allowed on any account: executing multiple trades per second, dozens of trades within a minute, rapid-fire entries and exits, or any attempt to exploit speed, latency or feed delays." [P1]
- `sizing_or_gambling_terms` = **gambling policy (overleveraging, overexposure, one-sided bets, hyperactivity); impermissible risk allocation; lot-size manipulation; account rolling (>40% of net profit from one trade/day is a warning sign)** (verified)
  - "One-Sided Bets — avoid trading predominantly in one direction without proper market analysis." [P15]
  - "Lot Size Manipulation: Using significantly smaller lot sizes after a large trade with the aim of formally meeting minimum trading-day requirements;" [P5]
  - "One trade or one day produces more than 40% of the net profit." [P1]
- `other_conduct_bearing` = **no overnight/weekend positions (force-closed 14:55 CT); micro-scalping flag (> 50% of profit from trades <= 15 s); personal device only, one account per IP/network; Replikanto only in Compliance Edition; temporary micro commodity limits** (verified)
  - "Any position still open 5 minutes before the market close (14:55 CT) is force-closed by our Risk Team." [P1]
  - "Personal Device Only — all trading must be carried out from a personal device used exclusively by the account holder." [P13]
  - "Not mandatory on every trade, but strongly recommended." [P1]
  - note: Stops/targets: 'not mandatory ... strongly recommended' - bracket orders are welcome.
- `permitted_products` = **CME equity index futures ES, NQ, YM, RTY and micros (plus FX, energy, metals, ags, rates, micro crypto, Eurex)** (verified)
  - "Equity indices (ES, NQ, YM, RTY and their micros)." [P3]
  - "Standard and mini contracts: $0.50 per contract." [P3]

**Comparability** (reader's section)

- Yes: Futures Prime is a one-phase $50K evaluation on CME Group futures (ES, NQ and micros) leading to a simulated funded 'Earning Account' that pays rewards.

**Access note** (reader's section)

- GTC clause 4.5.2 lists 'automated retrieval or extraction of data (scraping, crawling, or similar methods) without our express written permission' among prohibited uses; the pages were fetched one at a time by curl before this was read.

### Aqua Futures (AquaFutures / AquaFunded Futures) (`aqua`) -- PASS

**Pages quoted** (key: URL; article id; the page's own date as shown; all read 2026-11-15)

- [P1] https://intercom.help/aquafutures-help-center/en/articles/16934765-flex-daily-loss-faq; id 16934765; page date: October 5, 2026
- [P2] https://intercom.help/aquafutures-help-center/en/articles/17296868-flex-no-daily-loss-faq; id 17296868; page date: October 5, 2026
- [P3] https://intercom.help/aquafutures-help-center/en/articles/16934774-standard-account-rules; id 16934774; page date: September 30, 2026
- [P4] https://intercom.help/aquafutures-help-center/en/articles/16934770-daily-account-rules; id 16934770; page date: September 30, 2026
- [P5] https://intercom.help/aquafutures-help-center/en/articles/16941660-payout-policy; id 16941660; page date: September 30, 2026
- [P6] https://intercom.help/aquafutures-help-center/en/articles/15863787-how-many-funded-accounts-am-i-allowed-at-once; id 15863787; page date: September 30, 2026
- [P7] https://intercom.help/aquafutures-help-center/en/articles/15863742-prohibited-trading-strategies; id 15863742; page date: September 30, 2026
- [P8] https://www.aquafunded.com/futures
- [P9] https://intercom.help/aquafutures-help-center/en/articles/17341251-what-is-the-aquafunded-futures-live-account; id 17341251; page date: October 5, 2026
- [P10] https://intercom.help/aquafutures-help-center/en/articles/15692179-ip-usage-devices-and-location; id 15692179; page date: September 30, 2026
- [P11] https://intercom.help/aquafutures-help-center/en/articles/16759305-inactivity-rule; id 16759305; page date: September 30, 2026
- [P12] https://intercom.help/aquafutures-help-center/en/articles/15692209-trading-hours; id 15692209; page date: September 30, 2026
- [P13] https://intercom.help/aquafutures-help-center/en/articles/15692102-futures-instrument-list-codes; id 15692102; page date: September 30, 2026


Official domains: aquafutures.io, aquafunded.com, intercom.help/aquafutures-help-center. Read 2026-11-15.
Plan captured: Flex Daily Loss 50K (terms_flex_daily_loss_50k) and Daily 50K (terms_daily_50k): both have EOD funded drawdown and no funded consistency; they differ materially in payout mechanics (5 winning days / 50% of profit up to $2,000, no buffer vs daily payouts up to $1,100 above a $2,100 buffer).
Verdict: **PASS** -- Flex Daily Loss and Daily have EOD funded drawdowns and no funded consistency, 5 funded accounts at once, copiers among own accounts allowed; hand-entered bracket trading is allowed (bots banned; watch the 10-second, 0.3RR and account-rolling rules).

Plans seen:
- Flex Daily Loss 50K (site config 'One Step Flex'): drawdown EOD trailing $2,000 eval and funded, locks at starting balance; DLL $1,200 soft; consistency evaluation 50%, funded none
  - "| Consistency | 50% Challenge Only | 50% Challenge Only | 50% Challenge Only" [P1]
- Flex No Daily Loss 50K (site config 'One Step Flex DLL'): drawdown EOD trailing $2,000, no DLL; consistency evaluation 50%, funded none; but only one funded account at a time and 3 rewards then the account closes
  - "Traders may have unlimited Evaluation accounts, but only one active Funded Account at a time." [P2]
- Standard 50K: drawdown EOD trailing $2,000 eval and funded, locks at $52,100; DLL $1,000 soft; consistency evaluation none, funded 40% per payout cycle
  - "Unlike the Flex and Daily models, the Standard Model has no consistency requirement during the Evaluation. Instead, a 40% Consistency Rule applies only on the Funded Account." [P3]
- Daily 50K: drawdown EOD trailing $2,000 eval and funded, locks at $52,100; DLL $1,000 soft; consistency evaluation 40%, funded none
  - "The Consistency Rule applies only during the Evaluation. There is no Consistency Rule once the trader reaches the Funded Account." [P4]
- Instant 50K (no evaluation): drawdown EOD $2,000; consistency evaluation n/a, funded 20% per payout cycle
  - "A fixed 20% Consistency Rule applies to every Instant Account payout cycle." [P5]

**Screen**

- `drawdown_eval` = **eod_trailing (all current futures models)** (verified)
  - "The Maximum Trailing Drawdown varies depending on the account size and follows an End-of-Day (EOD) trailing model during both the Challenge and Funded stages." [P1]
- `drawdown_funded` = **eod_trailing** (verified)
  - "The trailing drawdown adjusts based on the account’s closed balance at the end of each trading day." [P1]
- `consistency_eval` = **Flex 50%; Daily 40%; Standard none** (verified)
  - "The trader’s highest-profit trading day cannot account for more than 50% of their total Challenge profits." [P1]
  - note: Not met = keep trading, not a breach.
- `consistency_funded` = **Flex: none; Daily: none; Standard: 40%; Instant: 20%** (verified)
  - "There is no Consistency Rule on the Flex Daily Loss Funded Account." [P1]
- `max_funded_accounts` = **5 active funded at once (extra funded accounts held until a slot opens); evaluations unlimited; Flex No Daily Loss: one funded at a time** (verified)
  - "You may have as many Evaluation accounts as you wish. However, you can only have up to 5 active Funded accounts trading at the same time." [P6]
  - note: Household: allowed with disclosure to support.
- `copy_trading` = **allowed between accounts the same trader owns; copying others prohibited** (verified)
  - "Copy trading is allowed on AquaFunded Futures Flex Daily Loss Accounts, including the use of trade copier software, provided that all accounts involved are legally owned and operated by the same trader." [P1]
  - note: The IP/devices article says multiple accounts must be 'used independently' - a soft tension with the copier permission.
- `opposite_positions` = **prohibited across Aqua accounts, people and firms; also NQ vs MNQ offsetting** (verified)
  - "Hedging between multiple AquaFutures accounts is strictly prohibited." [P7]
- `news` = **allowed (Tier-1 releases may be restricted at Aqua's discretion)** (verified)
  - "News trading is allowed during both the Challenge and Funded stages." [P1]
  - "Trading during major Tier-1 economic releases may also be restricted depending on market conditions, volatility levels, and platform stability requirements." [P7]
  - note: Model pages allow news; the prohibited-strategies page reserves restriction.
- `automation` = **fully automated systems, bots, AI execution prohibited; semi-automated only with trader present; < 100 trades/day** (verified)
  - "The use of fully automated systems, unattended algorithms, trading bots, AI-driven execution software, latency arbitrage systems, or any form of self-operating execution mechanism is strictly prohibited across all AquaFutures account types." [P7]
  - note: Hand entry is exactly what is allowed.
- `sizing_gambling` = **gambling/all-or-nothing, oversized positions, account rolling/stacking prohibited; >=50% of trades and of profits from trades held > 10 s; average RR > 0.3** (verified)
  - "To maintain fair and sustainable trading conditions, AquaFutures requires that at least 50% of all closed trades remain open for longer than 10 seconds. In addition, at least 50% of total generated profits must come from trades held longer than 10 seconds. Traders are also expected to maintain an average risk-to-reward ratio above 0.3RR across their overall trading activity." [P7]
  - "This often includes repeatedly breaching accounts, continuously cycling through new accounts after hitting Maximum Loss Limits, purchasing excessive numbers of accounts simultaneously, or maintaining large numbers of backup accounts intended solely for replacement purposes." [P7]
  - note: Account-rolling clause bears on a many-account design; brackets are barred only when 'ultra-tight ... intended solely for fill exploitation'.

**Terms (`terms_flex_daily_loss_50k`)**

- `eval_profit_target` = **3000** (verified)
  - "| Profit Target | $3,000 | $6,000 | $9,000" [P1]
- `eval_drawdown_amount` = **2000** (verified)
  - "| Maximum Drawdown | $2,000 | $3,000 | $4,500" [P1]
- `eval_drawdown_type` = **eod_trailing (closed balance)** (verified)
  - "This means intraday unrealized profits do not cause the drawdown threshold to trail upward." [P1]
  - note: Whether the floor is enforced against intraday equity is not stated on this page.
- `eval_drawdown_lock` = **locks at the starting balance ($50,000)** (verified)
  - "Once the trailing drawdown reaches the account’s original starting balance, the drawdown locks and no longer trails upward." [P1]
- `eval_daily_loss_limit` = **1200 (soft: day stopped, account not breached)** (verified)
  - "| Daily Loss Limit | $1,200 | $1,700 | $3,000" [P1]
  - "If the Daily Loss Limit is reached, trading will be restricted for the remainder of that trading day rather than permanently breaching the account." [P1]
- `eval_consistency_rule` = **50% (pass needs best day <= 50% of challenge profits)** (verified)
  - "A 50% Consistency Rule applies during the AquaFunded Futures Flex Daily Loss Challenge." [P1]
- `eval_min_days` = **none (2 days minimum in effect via the 50% rule)** (verified)
  - "Due to the 50% Consistency Rule, traders can complete the Flex Daily Loss Challenge in as little as 2 trading days." [P1]
- `eval_position_limit` = **4 mini / 40 micro, no scaling** (verified)
  - "| Maximum Position Size | 4 Mini / 40 Micro | 8 Mini / 80 Micro | 12 Mini / 120 Micro" [P1]
- `eval_fee` = **$131 one-time (site configurator value for 50K Flex; refundable per page)** (verified)
  - "prices: { '50k': 131, '100k': 191, '150k': 365 }" [P8]
  - "One-time fee • 100% refundable" [P8]
  - note: From the futures page's own price table (key 'flex' = 'One Step Flex', whose spec rows match the Flex Daily Loss article). Whether 131 is before or after the 25% HONOR promo / multi-account discounts is not stated. aquafutures.io redirects to www.aquafunded.com/futures.
- `eval_reset_fee` = **not stated** (UNVERIFIED)
  - looked at: https://www.aquafunded.com/futures (lists 'Account resets' as a feature, no price), help collections Models, Trading Rules, Reward Information
- `activation_fee` = **none** (verified)
  - "AquaFunded Futures does not require an activation fee before receiving your Flex Daily Loss Funded Account." [P1]
- `eval_count_limit` = **unlimited** (verified)
  - "You may have as many Evaluation accounts as you wish." [P6]
  - note: Subject to the account-rolling/stacking prohibition.
- `eval_time_limit` = **unlimited (but 7-day inactivity closure)** (verified)
  - "{"label": "Time Limit", "values": ["Unlimited", "—"]}" [P8]
- `funded_type` = **simulated Funded Account; Live Review possible after Reward 5 (not guaranteed); on promotion all eligible funded accounts merge into one Live account** (verified)
  - "Unlike Evaluation and Funded Accounts, Live Accounts operate using real CME market execution with real capital through our partnered brokerage infrastructure." [P9]
  - "Successfully reaching Reward 5 on a Funded Account" [P9]
  - "Once approved, all of your eligible Funded Accounts will automatically transition into one Live Account." [P9]
  - note: Live: $0 start, EOD drawdown, combined drawdown cap $15,000, no consistency, daily rewards.
- `funded_drawdown_amount` = **2000** (verified)
  - "| Maximum Drawdown | $2,000 | $3,000 | $4,500" [P1]
- `funded_drawdown_type` = **eod_trailing** (verified)
  - "| Drawdown Mode | EOD | EOD | EOD" [P1]
- `funded_drawdown_lock` = **locks at $50,000 (starting balance); after any payout locks at $50,100** (verified)
  - "Once the account has generated enough closed profit for the trailing threshold to reach the original $50,000 starting balance, the threshold locks at $50,000 and will no longer trail upward." [P1]
- `payout_balance_consequence` = **after any approved payout the floor locks permanently at starting balance + $100 ($50,100)** (verified)
  - "After a payout from a $50,000 Flex Daily Loss Funded Account, the account's drawdown floor will be permanently locked at $50,100." [P1]
- `funded_daily_loss_limit` = **1200 soft** (verified)
  - "A Daily Loss Limit applies during both the Challenge and Funded stages." [P1]
- `funded_consistency_rule` = **none** (verified)
  - "There is no Consistency Rule on the Flex Daily Loss Funded Account." [P1]
- `funded_position_limit` = **4 mini / 40 micro, no scaling** (verified)
  - "There is no progressive position scaling on Flex Daily Loss Accounts." [P1]
- `funded_monthly_fee` = **none** (verified)
  - "Is There a Monthly Fee or Activation Fee? No." [P1]
- `payout_min` = **$500 (payout policy); withdrawal minimum $100 crypto / $500 Rise** (verified)
  - "Minimum payout is $500." [P5]
  - "Minimum Withdrawal: $100 via Crypto and $500 via Rise." [P1]
  - note: Conflict: $500 minimum payout vs $100 via crypto.
- `payout_cap` = **50% of available profits, max $2,000 per request; no lifetime cap stated** (verified)
  - "| $50,000 | 50% of profits, up to $2,000" [P1]
  - "These payout caps apply to every payout request and do not disappear after a certain number of payouts." [P5]
- `payout_frequency_gate` = **5 winning days of >= $200 per cycle (reset after each reward); from reward #2, net profit >= $1,000 since last reward; no buffer** (verified)
  - "| $50,000 | $200 | $1,000 | $2,000" [P1]
  - "From reward #2 onward, Flex Daily Loss Funded Accounts must also satisfy a Net Profit Requirement." [P1]
  - "For payouts #2 through #5, traders must also meet the applicable Net Profit Requirement." [P5]
  - note: Payout policy limits the net-profit gate to payouts #2-#5; the Flex Daily Loss FAQ says 'from reward #2 onward'.
- `payout_split` = **90%** (verified)
  - "The 90% Profit Split applies from the first reward onward." [P1]
- `payout_processing_days` = **within 24 business hours** (verified)
  - "Processing Time: Within 24 business hours." [P1]
- `payout_fee` = **3% processing fee on all payouts** (verified)
  - "All AquaFutures payouts are subject to a 3% processing fee to cover payment processing and transaction costs." [P5]
- `payout_count_limit` = **no limit while the account is active** (verified)
  - "There is no limit on the total number of rewards a trader can receive from a Flex Daily Loss Funded Account while the account remains active and all reward requirements continue to be satisfied." [P1]
  - "The original most popular flex model with no path to live. Three rewards per account then account closes, unlimited accounts available." [P8]
  - note: Conflict: the futures page blurb says three rewards then the account closes - that matches the Flex No Daily Loss article, not Flex Daily Loss. Help article value taken for Flex Daily Loss.
- `max_accounts` = **5 active funded; unlimited evaluations; household allowed with disclosure** (verified)
  - "Traders may have up to 5 active Flex Daily Loss Funded Accounts trading at the same time." [P1]
  - "Yes. You can manage multiple accounts as long as they all belong to you and are used independently." [P10]
- `inactivity_rule` = **closed after 7 consecutive calendar days with no trade; not reinstatable** (verified)
  - "If no trade is executed on your account for 7 consecutive calendar days, the account will be considered inactive and will automatically closed." [P11]
  - "Accounts closed due to the 7-Day Inactivity Rule cannot be reinstated or reset." [P11]
  - note: Binding for a design that parks accounts.
- `copy_trading_terms` = **own accounts only** (verified)
  - "Traders may copy their own trades between accounts they personally own." [P1]
- `cross_account_hedging` = **prohibited, incl. NQ/MNQ offsetting** (verified)
  - "Examples may include simultaneously holding NQ and MNQ positions in offsetting directions or using Micro contracts to hedge larger Mini contract exposure." [P7]
- `news_trading_terms` = **allowed; Tier-1 may be restricted** (verified)
  - "Traders are free to open, manage and close positions during high-impact news events." [P1]
- `automation_terms` = **bots/fully automated prohibited; manual or supervised semi-automated only** (verified)
  - "While traders may use tools for charting assistance, alerts, or trade management, all trading activity must remain actively supervised and manually managed by the trader at all times." [P7]
- `sizing_or_gambling_terms` = **no oversized/all-or-nothing trades; microscalping restricted; < 100 trades/day** (verified)
  - "This includes taking oversized positions without proper risk planning, trading without stop losses while exposing the account to excessive risk, repeatedly using maximum leverage without a structured strategy, or attempting unrealistic “all-or-nothing” trades." [P7]
  - "Traders may not execute 100 or more trades within a single trading day." [P7]
- `other_conduct_bearing` = **brackets barred only when ultra-tight for fill exploitation; excessive bracket manipulation barred; open trades auto-closed at market close** (verified)
  - "This includes systems dependent on perfect execution, ultra-tight stop-loss and take-profit brackets intended solely for fill exploitation, or rapid entry-and-exit behavior relying primarily on simulated execution precision rather than genuine market structure." [P7]
  - "All open trades will automatically close when the market closes." [P12]
- `permitted_products` = **CME futures incl. NQ and MNQ** (verified)
  - "| E-mini NASDAQ 100 | NQ | Sunday - Friday 17:00 - 16:00 CT Daily Break: 16:00 - 17:00 CT | 0.25 | $5 | 1.9" [P13]
  - "| Micro E-mini Nasdaq-100 | MNQ | Sunday - Friday 17:00 - 16:00 CT Daily Break: 16:00 - 17:00 CT | 0.25 | $0.50 | 0.62" [P13]

**Terms (`terms_daily_50k`)**

- `eval_profit_target` = **3000** (verified)
  - "| Profit Target | $3,000 | $6,000 | $9,000" [P4]
- `eval_drawdown_amount` = **2000** (verified)
  - "| Max Drawdown | $2,000 | $2,500 | $3,500" [P4]
- `eval_drawdown_type` = **eod_trailing** (verified)
  - "The Daily Account uses an End-of-Day (EOD) trailing drawdown during both the Evaluation and Funded stages." [P4]
- `eval_drawdown_lock` = **locks at $52,100** (verified)
  - "For the Daily Model, the drawdown locks at:" [P4]
  - "| $50,000 | $52,100" [P4]
  - note: Oddity: lock $52,100 (above start) while the post-payout floor is $50,100; a $2,000 EOD trail would reach $52,100 only at a $54,100 close. Read literally.
- `eval_daily_loss_limit` = **1000 soft** (verified)
  - "| Daily Loss Limit | $1,000 | $1,250 | $1,750" [P4]
  - "The Daily Loss Limit is a soft breach." [P4]
- `eval_consistency_rule` = **40% (evaluation only)** (verified)
  - "Your highest-profit trading day cannot account for more than 40% of your total profits during the Evaluation." [P4]
- `eval_min_days` = **none** (verified)
  - "There are no minimum trading days required to complete the Daily Evaluation." [P4]
- `eval_position_limit` = **4 mini / 40 micro, no scaling** (verified)
  - "There is no position scaling on AquaFutures Daily Accounts." [P4]
- `eval_fee` = **$113 one-time (site configurator value for 50K Daily; refundable per page)** (verified)
  - "prices: { '50k': 113, '100k': 173, '150k': 267 }" [P8]
  - note: Before/after promo not stated.
- `eval_reset_fee` = **not stated** (UNVERIFIED)
  - looked at: futures page; help collections
- `activation_fee` = **none** (verified)
  - "AquaFutures does not require any monthly subscription or activation fee before receiving your Daily Funded Account." [P4]
- `eval_count_limit` = **unlimited** (verified)
  - "You may have as many Evaluation accounts as you wish." [P6]
- `eval_time_limit` = **unlimited** (verified)
  - "{"label": "Time Limit", "values": ["Unlimited", "—"]}" [P8]
  - note: 7-day inactivity closure applies.
- `funded_type` = **simulated Funded Account; Live Review possible** (verified)
  - "Live Accounts are not automatically awarded and cannot be purchased." [P9]
- `funded_drawdown_amount` = **2000** (verified)
  - "| Max Drawdown | $2,000 | $2,500 | $3,500" [P4]
- `funded_drawdown_type` = **eod_trailing** (verified)
  - "The trailing drawdown adjusts based on your closed account balance at the end of each trading day." [P4]
- `funded_drawdown_lock` = **$52,100; after any payout floor locks at $50,100** (verified)
  - "Once the drawdown reaches this level, it will no longer trail upward." [P4]
  - note: See oddity note on eval_drawdown_lock.
- `payout_balance_consequence` = **floor locks permanently at $50,100 after any payout; $2,100 buffer must stay intact** (verified)
  - "For example, after a payout from a $50,000 Daily Funded Account, the permanent drawdown floor becomes $50,100." [P4]
- `funded_daily_loss_limit` = **1000 soft** (verified)
  - "Daily Accounts include a fixed Daily Loss Limit during both the Evaluation and Funded stages." [P4]
- `funded_consistency_rule` = **none** (verified)
  - "The Consistency Rule applies only during the Evaluation. There is no Consistency Rule once the trader reaches the Funded Account." [P4]
- `funded_position_limit` = **4 mini / 40 micro, no scaling** (verified)
  - "| $50,000 | 4 Mini / 40 Micro Contracts" [P4]
- `funded_monthly_fee` = **none** (verified)
  - "AquaFutures does not require any monthly subscription or activation fee before receiving your Daily Funded Account." [P4]
- `payout_min` = **500** (verified)
  - "The minimum payout amount is $500 across all Daily Account sizes." [P4]
- `payout_cap` = **$1,100 per day (daily, not lifetime); only above the $52,100 threshold** (verified)
  - "| $50,000 | $1,100" [P4]
  - "The maximum payout is a daily cap, not a lifetime cap." [P4]
- `payout_frequency_gate` = **daily; balance above $52,100 buffer threshold; from payout #2 new net profit >= $550; no winning-day count** (verified)
  - "| $50,000 | $2,100 | $52,100" [P4]
  - "| $50,000 | $550" [P4]
  - "There is no Winning Day requirement." [P5]
- `payout_split` = **90%** (verified)
  - "AquaFutures Daily Funded Traders receive a 90% Reward Split from the first payout onward." [P4]
- `payout_processing_days` = **within 24 business hours** (verified)
  - "| Processing Time | Within 24 business hours" [P5]
- `payout_fee` = **3%** (verified)
  - "All AquaFutures payouts are subject to a 3% processing fee to cover payment processing and transaction costs." [P5]
- `payout_count_limit` = **not stated** (UNVERIFIED)
  - looked at: https://intercom.help/aquafutures-help-center/en/articles/16934770-daily-account-rules, 16941660-payout-policy
  - note: 'daily cap, not a lifetime cap' concerns amount, not count.
- `max_accounts` = **5 active funded; unlimited evaluations** (verified)
  - "If passing an Evaluation account or purchasing an Instant Funded account would take you above the 5-account limit, the additional Funded account will be placed on hold until a space becomes available." [P6]
- `inactivity_rule` = **closed after 7 calendar days with no trade** (verified)
  - "Simply execute at least one trade within every 7-day period." [P11]
- `copy_trading_terms` = **own accounts only (third-party copier software allowed)** (verified)
  - "Copy trading is allowed, including the use of third-party trade copier software, provided that all accounts involved are legally owned and operated by the same trader." [P4]
- `cross_account_hedging` = **prohibited** (verified)
  - "Hedging between multiple AquaFutures accounts is strictly prohibited." [P7]
- `news_trading_terms` = **allowed; Tier-1 may be restricted** (verified)
  - "News trading is allowed on both Evaluation and Funded Daily Accounts." [P4]
- `automation_terms` = **bots prohibited; manual/supervised only** (verified)
  - "The use of fully automated systems, unattended algorithms, trading bots, AI-driven execution software, latency arbitrage systems, or any form of self-operating execution mechanism is strictly prohibited across all AquaFutures account types." [P7]
- `sizing_or_gambling_terms` = **as Flex block; microscalping < 50% of profits from < 10 s trades** (verified)
  - "Less than 50% of your total profits may come from trades held for under 10 seconds." [P4]
- `other_conduct_bearing` = **account rolling/stacking prohibited** (verified)
  - "AquaFutures also prohibits behavior commonly referred to as “Account Rolling” or “Account Stacking.”" [P7]
- `permitted_products` = **CME futures incl. NQ/MNQ** (verified)
  - "| Micro E-mini Nasdaq-100 | MNQ | Sunday - Friday 17:00 - 16:00 CT Daily Break: 16:00 - 17:00 CT | 0.25 | $0.50 | 0.62" [P13]

### Alpha Futures (`alpha`) -- PASS

**Pages quoted** (key: URL; article id; the page's own date as shown; all read 2026-11-15)

- [P1] https://help.alpha-futures.com/en/articles/11634907-advanced-account-overview; id 11634907; page date: July 22, 2026
- [P2] https://help.alpha-futures.com/en/articles/11632512-standard-account-overview; id 11632512; page date: July 27, 2026
- [P3] https://help.alpha-futures.com/en/articles/11771813-zero-account-overview; id 11771813; page date: Updated over 2 weeks ago
- [P4] https://help.alpha-futures.com/en/articles/15838742-direct-account-overview; id 15838742; page date: July 9, 2026
- [P5] https://alpha-futures.com/posts/alpha-futures-payout-update-five-business-days-or-less; page date: Updated September 15, 2026
- [P6] https://help.alpha-futures.com/en/articles/9491999-maximum-loss-limit-mll; id 9491999; page date: July 15, 2026
- [P7] https://alpha-futures.com/
- [P8] https://help.alpha-futures.com/en/articles/9492048-consistency-rule; id 9492048; page date: July 27, 2026
- [P9] https://help.alpha-futures.com/en/articles/9492088-maximum-allocation; id 9492088; page date: July 27, 2026
- [P10] https://alpha-futures.com/product/advanced
- [P11] https://help.alpha-futures.com/en/articles/10573989-copy-trading; id 10573989; page date: July 17, 2026
- [P12] https://alpha-futures.com/terms-and-conditions; page date: Effective from July 27, 2026
- [P13] https://help.alpha-futures.com/en/articles/9508585-prohibited-trading-practices; id 9508585; page date: Updated over a week ago
- [P14] https://help.alpha-futures.com/en/articles/9492063-news-trading-policy; id 9492063; page date: July 27, 2026
- [P15] https://help.alpha-futures.com/en/articles/9492014-daily-loss-guard; id 9492014; page date: July 15, 2026
- [P16] https://help.alpha-futures.com/en/articles/9492068-monthly-subscription; id 9492068; page date: Updated over 2 weeks ago
- [P17] https://help.alpha-futures.com/en/articles/9492077-reset; id 9492077; page date: Updated over 2 weeks ago
- [P18] https://help.alpha-futures.com/en/articles/10743344-path-to-live-structure; id 10743344; page date: Updated this week
- [P19] https://alpha-futures.com/how-it-works
- [P20] https://help.alpha-futures.com/en/articles/9492051-payout-policy; id 9492051; page date: July 27, 2026
- [P21] https://help.alpha-futures.com/en/articles/9492025-scaling-plan; id 9492025; page date: July 24, 2026
- [P22] https://help.alpha-futures.com/en/articles/10491202-maximum-withdrawal-request; id 10491202; page date: Updated over 2 weeks ago
- [P23] https://alpha-futures.com/general-service-agreement
- [P24] https://help.alpha-futures.com/en/articles/12757982-inactivity-rule; id 12757982; page date: November 5, 2025
- [P25] https://help.alpha-futures.com/en/articles/9492096-what-and-when-you-can-trade; id 9492096; page date: July 17, 2026
- [P26] https://help.alpha-futures.com/en/articles/9806068-price-limit-trading; id 9806068; page date: August 30, 2024
- [P27] https://alpha-futures.com/product/standard


Official domains: alpha-futures.com, help.alpha-futures.com. Read 2026-11-15.
Plan captured: Advanced 50K (full terms in 'terms'); Standard 50K also passes and differs materially (5 qualified accounts, 40% funded consistency, DLG, scaling, news window) -- its differing terms are in 'terms_standard'.
Verdict: **PASS** -- EOD trailing MLL (locks at start) on every plan and no funded consistency on Advanced; 3 Advanced (5 Standard) funded per household; hand-entered bracket trading not forbidden (only tight-bracket sim-fill exploitation and <10-tick/<2-min scalping).

Plans seen:
- Advanced 50K: drawdown EOD trailing $1,750, stops trailing at starting balance (eval and qualified); consistency evaluation 40%, funded none
  - "| Consistency | 40% on Evaluation only | 40% on Evaluation only | 40% on Evaluation only" [P1]
- Standard 50K: drawdown EOD trailing $2,000, stops trailing at starting balance; consistency evaluation 50%, funded 40% (gates each withdrawal; resets after each request); a +$70 checkout add-on 'No Consistency Rule On your Qualified account' is offered
  - "| Consistency | 50% on Evaluation 40% on Qualified | 50% on Evaluation 40% on Qualified | 50% on Evaluation 40% on Qualified" [P2]
- Zero 50K: drawdown EOD trailing $2,000, stops trailing at starting balance; Daily Loss Guard $1,000 on eval and qualified; consistency evaluation none, funded 40% (gates withdrawals)
  - "| Consistency | 40% on Qualified only | 40% on Qualified only | 40% on Qualified only" [P3]
- Direct 50K (no evaluation, one-time $519): drawdown EOD MLL $2,000; Daily Loss Guard $1,000; consistency evaluation n/a (no evaluation), funded 20% plus a withdrawal profit target ($3,000 first, $2,000 after)
  - "| Consistency Rule | 20% | 20% | 20% | 20%" [P4]
- Premium (discontinued): drawdown n/a; consistency evaluation n/a, funded n/a
  - "We have now refunded all active Premium Accounts while continuing to support current traders and accounts." [P5]

**Screen**

- `drawdown_eval` = **eod_trailing, stops trailing at starting balance** (verified)
  - "The Maximum Loss Limit (MLL) is EOD (end of day) trailing on all of our accounts here at Alpha Futures. None of our accounts utilize intraday trailing drawdown you will see elsewhere in industry." [P6]
  - "Maximum Loss Limit stops trailing at the account starting balance on all of our accounts." [P6]
  - note: Breach is on floating equity or closed balance: 'If you break MLL at any point, floating equity or closed balance of account, your account will be liquidated.'
- `drawdown_funded` = **eod_trailing, stops trailing at starting balance** (verified)
  - "The Maximum Loss Limit (MLL) is EOD (end of day) trailing on all of our accounts here at Alpha Futures." [P6]
  - "Every plan uses an EOD trailing Maximum Loss Limit, based on the highest end-of-day balance. It stops trailing at the starting balance." [P7]
  - note: Same rule on every account type including Qualified.
- `consistency_eval` = **40% (Advanced; 50% Standard; none Zero) -- gates passing the evaluation** (verified)
  - "The Consistency Rule on Advanced Evaluations is 40%. This means that during your Evaluation, profits from one single trading day cannot be larger than 40% of your net profits made." [P8]
  - "You will not pass your Evaluation until this rule is satisfied." [P8]
- `consistency_funded` = **none on Advanced Qualified (40% on Standard/Zero Qualified, 20% on Direct; gates withdrawals)** (verified)
  - "There is NO Consistency Rule on Advanced Qualified Accounts." [P8]
  - "There is a 40% Consistency Rule on Zero and Standard Qualified Accounts." [P8]
  - note: The month-old lead's '40% consistency gating payouts' is true of Standard/Zero Qualified, not of Advanced Qualified.
- `max_funded_accounts` = **3 Advanced Qualified per user (any user with an active Advanced Qualified is limited to 3); 5 Qualified per household for Standard/Zero/Direct; one individual per household** (verified)
  - "Advanced Account: 3 Qualified Accounts" [P9]
  - "Any user that has an active Advanced Qualified account will be limited to 3." [P9]
  - "You can run up to 5 accounts at the same time. See the full account rules in our Help Center." [P10]
  - note: CONFLICT: the Advanced product-page FAQ says up to 5; the help centre (July 27, 2026) and T&C Schedule 2 say Advanced = 3. Taken as 3.
- `copy_trading` = **permitted across one's own accounts (single individual) per help centre; T&C 8.1.5 says only external-to-Alpha copying is allowed** (verified)
  - "Copy trading in general is permitted as long as it is a single user executing the trades, and it is the single individual listed on the Alpha Futures Accounts." [P11]
  - "8.1.5 the only copy trading allowed is that from your own external account to your Alpha Futures Account." [P12]
  - note: CONFLICT between help centre and T&C wording; the help article explicitly addresses copying across one's own Alpha accounts ('Can I copy across my Alpha Futures Accounts?') and permits it.
- `opposite_positions` = **prohibited (across accounts and within one account)** (verified)
  - ""Reverse Trading" or Hedging, meaning going short on one account, and long on the other is strictly prohibited at Evaluation and Qualified Phase." [P13]
- `news` = **no restriction on evaluations or Advanced Qualified; Standard/Zero/Direct Qualified: no orders executed 2 min before to 2 min after red-folder (ForexFactory) events** (verified)
  - "There are no news trading restrictions for any Evaluation Accounts." [P14]
  - "You may hold through news releases following your trading plan, but no orders may be executed within 2 minutes before or 2 minutes after high impact news events." [P14]
- `automation` = **AI/bots/automated trading prohibited on all accounts; semi-automated signals allowed if the trader places and manages trades by hand** (verified)
  - "The use of AI, bots, and other automated trading mechanisms is strictly prohibited across all account types." [P13]
  - note: Hand entry is what the firm requires; compatible with our design.
- `sizing_gambling` = **'All or Nothing' max-leverage single positions, account rolling/stacking, gambling prohibited; tick scalping (<10 ticks AND <2 min) and tight-bracket exploitation of no-slippage fills prohibited** (verified)
  - "Using maximum leverage on a single position and using DLL as a stop loss will not be tolerated." [P13]
  - "Exploiting the absence of slippage and utilizing tight brackets to gain from favorable fills are not permitted." [P13]
  - note: The bracket clause targets tight brackets exploiting sim fills, not brackets as such; a design with stops/targets well beyond 10 ticks and holds over 2 minutes stays clear.

**Terms (`terms`)**

- `eval_profit_target` = **4000** (verified)
  - "| Parameters | Advanced 50K | Advanced 100K | Advanced 150K" [P1]
  - "| Profit Target | $4,000 | $8,000 | $12,000" [P1]
  - note: Must 'reach (+ maintain)' the target and satisfy the 40% consistency rule.
- `eval_drawdown_amount` = **1750** (verified)
  - "| Maximum Loss Limit | $1,750 | $3,500 | $5,250" [P1]
  - note: T&C Schedule 1 lists Advanced Evaluation MLL as 3.5% (= $1,750 on 50K), consistent.
- `eval_drawdown_type` = **eod_trailing** (verified)
  - "The Maximum Loss Limit is calculated from your account balance high at the end of each trading day, not intraday equity high like many others out there." [P6]
  - note: Breach is checked on intraday floating equity against the EOD-set floor.
- `eval_drawdown_lock` = **stops trailing at starting balance (floor $50,000 once EOD balance reaches $51,750)** (verified)
  - "Once the Maximum Loss Limit reaches the initial starting balance, it won't continue to trail." [P6]
  - note: $51,750 is the arithmetic for the $1,750 Advanced MLL; the article's worked example uses a $2,000 MLL.
- `eval_daily_loss_limit` = **none** (verified)
  - "| Daily Loss Guard | NONE | NONE | NONE" [P1]
  - "There is no Daily Loss Guard on Advanced Evaluations, but there is on Zero Evaluations." [P15]
- `eval_consistency_rule` = **40%: no single day > 40% of net profit; gates passing (not a breach)** (verified)
  - "The Consistency Rule on Advanced Evaluations is 40%. This means that during your Evaluation, profits from one single trading day cannot be larger than 40% of your net profits made." [P8]
  - "| 50k | $4,000 | $1,600 or less" [P8]
- `eval_min_days` = **3** (verified)
  - "hit the profit target in at least 3 trading days while staying inside your Maximum Loss Limit, and you're Qualified." [P10]
  - "8.1.9 The standard and advanced account assessments consist of 2 and 3 minimum trading days in the one phase evaluation, due to the 50% and 40% Consistency Rule." [P12]
  - "| 2 | 8% | 3.5% | 50k = 5 contracts/50 micros, 100k = 10 contracts/100 micros, 150k = 15 contracts/150 micros | None | starting at $189 | None | 40%" [P12]
  - note: CONFLICT inside the T&C: clause 8.1.9 says 3, the Schedule 1 Advanced Evaluation row says 2. Homepage card and product page say 3. Taken as 3 (the 40% rule makes 3 the arithmetic minimum anyway).
- `eval_position_limit` = **5 minis / 50 micros** (verified)
  - "| Max Position | 5 minis, 50 micros | 10 minis, 100 micros | 15 minis, 150 micros" [P1]
- `eval_fee` = **$209 per month (recurring until passed or cancelled)** (verified)
  - "| Price | $209/month | $349/month | $489/month" [P1]
  - "Your Monthly Evaluation Fee will rebill monthly from the sign-up date until you pass. The Evaluation subscription automatically ends once you pass." [P16]
  - note: Site banner today advertises a code 'ALPHA50 50% off Advanced, Standard & Direct' (promotion, not a contract term). A failed eval is reset to a fresh account at rebill.
- `eval_reset_fee` = **189** (verified)
  - "| Reset | $189 | $319 | $449" [P1]
  - "Resets DO NOT change or affect your monthly rebill date." [P17]
- `activation_fee` = **0** (verified)
  - "| Activation Fee | $0 | $0 | $0" [P1]
  - "9.) Accounts Purchased after July 8, 2026 enjoy No Activation Fees" [P1]
  - note: Recent change: no activation fee only for Advanced accounts bought after July 8, 2026.
- `eval_count_limit` = **no limit on evaluations (but 'Account Stacking' -- excessive evaluations/storing passed accounts -- is prohibited conduct)** (verified)
  - "8.1.3 Analysts may hold multiple active accounts. For Analyst Accounts, there is no maximum total allocation limit." [P12]
  - "More examples of Account Rolling are also known as "Account Stacking", meaning excessive Evaluations and storing multiple passed accounts, so when you withdraw or hit MLL, you can roll right into your next Qualified Account." [P13]
- `eval_time_limit` = **none (monthly rebill until passed)** (verified)
  - "(d) There are no time limits applicable to the Challenges, but you must ensure that all Challenge requirements continue to be achieved throughout the time in which you are taking part in a Challenge." [P12]
  - note: After passing: KYC plus contract signature within 30 days ('You have 30 days to sign this contract from passing your Evaluation, after that is expires.' -- article 9820801).
- `funded_type` = **sim (Qualified Account, simulated); after 5 payouts on one Qualified account (or other triggers) a trader may be called to live, which closes all Qualified accounts** (verified)
  - "Yes. Alpha Futures evaluations and Qualified Accounts use simulated funds." [P7]
  - "5 performance fees on a single Qualified Account" [P18]
  - "When a trader is called to live, all Qualified Accounts are closed" [P18]
  - "Once your simulated Qualified Account reaches +$40,000 in payable balance, or after 5 payout cycles, our team reviews your trading history for the opportunity to move to Alpha Prime." [P19]
  - note: Live: one live account per Qualified account with >=1 payout; 50K -> $0 start balance with $2,000 EOD drawdown, 80% split (Live Program) or 60% + monthly bonus (Alpha Prime). A trader may decline and take 50% of the eligible live drawdown balance, then a 3-month cool-down.
- `funded_drawdown_amount` = **1750** (verified)
  - "50K Advanced Qualified No Fee Once Qualified Days to Payout 5 Days Profit Target None Max Position Size 5 minis / 50 microsNo scaling plan Max Drawdown $1,750" [P10]
  - "| Advanced Qualified | 5 | None | 4% |" [P12]
  - note: CONFLICT: product/home cards say $1,750 on the 50K Advanced Qualified; T&C Schedule 2 lists Advanced Qualified MLL as 4% (= $2,000). Taken as $1,750 (help centre/product pages, plan-specific).
- `funded_drawdown_type` = **eod_trailing** (verified)
  - "Alpha Futures evaluations and Qualified Accounts use an end-of-day trailing Maximum Loss Limit (MLL)." [P7]
- `funded_drawdown_lock` = **stops trailing at starting balance** (verified)
  - "It follows the highest end-of-day account balance rather than intraday profit spikes and stops trailing at the starting balance." [P7]
- `payout_balance_consequence` = **MLL unchanged by a withdrawal (no reset of the floor to start/$0); withdrawal removes cash from the balance, floor stays where it was** (verified)
  - "Your Maximum Loss Limit stays intact from the date of your withdrawal, so you keep your runway after you receive your performance fee." [P7]
  - "If MLL was at $49,200 before payout, it will be after as well." [P2]
  - note: The $49,200 example is on the Standard (and Zero) overview; the homepage statement covers all plans. Only up to 50% of profit may be withdrawn per request, so the balance always stays above the floor after a request.
- `funded_daily_loss_limit` = **none** (verified)
  - "3.) No Daily Loss Guard on Evaluation or Qualified Accounts" [P1]
  - "| 90% split | None | None | None on Advanced Qualified Accounts" [P12]
- `funded_consistency_rule` = **none** (verified)
  - "There is no Consistency Rule on Advanced Qualified Accounts." [P20]
- `funded_position_limit` = **5 minis / 50 micros, no scaling plan** (verified)
  - "There is no Scaling Plan on Advanced Accounts." [P21]
  - "6.) No Scaling Plan on Advanced Accounts. Get access to full contract limit at all times." [P1]
  - note: The scaling tables (Standard/Zero only) were re-read from the HTML table cells and from T&C Schedule 3; they parse cleanly and agree (see terms_standard).
- `funded_monthly_fee` = **0** (verified)
  - "Qualified Traders do not pay a monthly subscription." [P16]
- `payout_min` = **1000** (verified)
  - "The minimum withdrawal request on Advanced Qualified Accounts is $1,000, maximum is industry leading $15,000 on all Advanced Account sizes." [P20]
- `payout_cap` = **per request: min(50% of account profit, $15,000); lifetime: none stated** (verified)
  - "You may request up to 50% of the profit in your account each withdrawal request (up to withdrawal limit), the rest of the balance stays on the account for drawdown or future withdrawals." [P20]
  - "This is per request, per account, more than 3x the industry leaders." [P22]
  - note: No lifetime cap is stated on any page read (looked at payout policy, maximum withdrawal, T&C Schedule 4); the practical ceiling is the call-to-live review after 5 payouts / +$40,000.
- `payout_frequency_gate` = **5 winning days of >= $200 (non-consecutive) accumulated between requests; up to 4 requests per month; no fixed payout dates** (verified)
  - "Traders have the ability to pay themselves up to 4 times a month. Request every 5 winning trading days of $200 profit, or more" [P20]
  - "The winning trading days do not need to be consecutive, but 5 need to be accumulated between each withdrawal request." [P20]
  - note: T&C Schedule 4 1.2.5: all trades must be closed when requesting and trading pauses until the withdrawal is debited.
- `payout_split` = **90% from the first payout** (verified)
  - "All withdrawal requests are the amount that will be removed from your trading account, trader received 90% of this request." [P20]
  - "First two virtual payouts on the account the User receives a 70% Performance Fee, virtual payouts 3 and 4 80%, virtual payouts 5+ on the account the User receives a 90% Performance Fee." [P23]
  - note: CONFLICT: the General Service Agreement (undated, older company number/address) still has a 70/80/90 tier; the help centre, product pages and T&C Schedule 2 ('90% split') say 90% from the start. Taken as 90%.
- `payout_processing_days` = **<= 5 business days after approval (Sept 15, 2026 update); T&C says 3 business days (up to 14 with extra verification)** (verified)
  - "Our current payout timeline is now five business days or less, and we are working towards restoring same-day payouts in the coming weeks." [P5]
  - "within 3 Business Days unless the account requires additional verification checks (as set out above), in which case this could take up to 14 Business Days." [P12]
  - note: CONFLICT T&C (3) vs operational update (<= 5). The update follows an unnamed 'major change' around July 2026 that disrupted payouts; Premium accounts were refunded and Premium payouts are queued in batches.
- `payout_fee` = **no firm payout fee stated; a provider exchange-rate fee applies when paid in a domestic currency** (UNVERIFIED)
  - "An exchange rate fee, as set by the provider from time to time, applies when receiving Analyst Performance Fees in your domestic currencies." [P12]
  - looked at: https://help.alpha-futures.com/en/articles/9492051-payout-policy, https://help.alpha-futures.com/en/articles/10443600-payout-methods, https://alpha-futures.com/terms-and-conditions (Schedule 4)
  - note: No page says 'no payout fee'.
- `payout_count_limit` = **up to 4 per month; no lifetime count stated (5 payouts on one account triggers live review)** (verified)
  - "8.) Pay yourself up to 4 times per month. Withdraw when you want after 5 winning days of $200 or more, no assigned payout dates." [P1]
- `max_accounts` = **funded: 3 Advanced Qualified (5 Qualified per household overall for other plans); evaluations: no maximum; one username per individual, one individual per household** (verified)
  - "Only one username per individual is permitted, and one individual per household may use our services." [P9]
  - "For Qualified Analyst accounts, the maximum total allocation per household is five accounts;" [P12]
  - "Any user that has an active Standard or Advanced Qualified account will be limited to 3." [P12]
  - note: CONFLICT: T&C Schedule 2 says an active Standard OR Advanced Qualified caps the user at 3; the help centre (same date, July 27, 2026) says only an active Advanced Qualified does (and Standard accounts bought before July 27, 2026 are capped at 3). Product page FAQ says 5 for Advanced. The month-old lead ('5 per household, 3 if an Advanced Qualified is active') matches the help centre.
- `inactivity_rule` = **at least one trade every 10 trading days** (verified)
  - "To keep your account active you must place a trade at least once every 10 trading days (does not matter size of trade)." [P24]
  - note: The page does not state the consequence of inactivity.
- `copy_trading_terms` = **allowed across own accounts by the single account holder (help centre); automated/group/reverse trading prohibited** (verified)
  - "Copy trading in general is permitted as long as it is a single user executing the trades, and it is the single individual listed on the Alpha Futures Accounts." [P11]
  - "8.1.5 the only copy trading allowed is that from your own external account to your Alpha Futures Account." [P12]
  - note: CONFLICT (see screen.copy_trading). Our design enters by hand on each account, so it does not depend on a copier.
- `cross_account_hedging` = **prohibited** (verified)
  - "Long NQ and short MNQ on the same account is another example, and strictly prohibited." [P13]
  - "Collaborating with others to execute identical or opposite strategies across unconnected accounts is prohibited." [P13]
- `news_trading_terms` = **no restriction on Advanced eval or Advanced Qualified; gambling during high-volatility events still prohibited** (verified)
  - "An "all or nothing" approach or gambling tendencies still will not be tolerated at any time, especially during high volatility events." [P14]
  - note: Advanced Qualified: 'Advanced Qualified Accounts do not have News Trading Restrictions, but please review the Prohibited Trading Practices.' (same article).
- `automation_terms` = **full automation, AI and bots prohibited; HFT (100+ trades/day) restricted; semi-automated signals permitted with manual placement** (verified)
  - "Semi-Automated Trading, such as a custom indicator that gives buy or sell signals, is permissible under the condition that the user manually places, monitors, and manages the trade while understanding the system and semi-automation's purpose." [P13]
  - "Any form of hands-off, continuous day and night trading, or any other type of full automation is strictly forbidden." [P13]
- `sizing_or_gambling_terms` = **max-leverage single positions using the DLL as a stop, account rolling and account stacking prohibited** (verified)
  - "Gambling tendencies or "Account Rolling", taking max leverage positions with no plan, no stop loss, and hitting max loss on the account then buying more accounts and repeating the process until a trade hits." [P13]
  - "1.3.2. a Qualified Analyst is required to maintain the same level of risk on a Qualified Analyst Account" [P12]
  - note: T&C 1.3.2 asks the qualified account to keep the evaluation's risk level -- a constraint on sizing differently in eval vs funded.
- `other_conduct_bearing` = **tick scalping (<10 ticks AND <2 min, when 50%+ of profit) and tight-bracket no-slippage exploitation prohibited; all trades flat by 4:20 PM ET; no trading within 2% of a CME price limit; VPN prohibited** (verified)
  - ""Tick or Micro Scalping" (trades less than 10 ticks AND less than 2 minutes)" [P13]
  - "This is only an issue when it is a clear pattern in the trader's profit (50%+)." [P13]
  - "You may begin trading at 6PM EST to start a new trading day, but all trades must be closed before 4:20PM EST every day." [P25]
  - "This prohibited conduct is enforced on ALL Alpha Futures Accounts, not just Evaluations." [P26]
  - note: Hand-entered single-position bracket trading on NQ/MNQ is not prohibited by any of these; the bracket must not be 'tight' enough to read as sim-fill exploitation.
- `permitted_products` = **CME Group products (CME, CBOT, NYMEX, COMEX), incl. NQ/MNQ/ES/MES** (verified)
  - "The CME Group Products are available to trade here at Alpha Futures." [P25]

**Terms (`terms_standard`)**

- `eval_profit_target` = **3000** (verified)
  - "| Parameters | Standard 50K | Standard 100K | Standard 150K" [P2]
  - "| Profit Target | $3,000 | $6,000 | $9,000" [P2]
- `eval_drawdown_amount` = **2000** (verified)
  - "| Maximum Loss Limit | $2,000 | $3,000 | $4,500" [P2]
  - note: Drawdown type/lock as in 'terms' (EOD trailing, stops at starting balance).
- `eval_daily_loss_limit` = **none on evaluation; $1,000 on Qualified** (verified)
  - "| Daily Loss Guard (NONE on Evaluation!) | $1,000 | $2,000 | $3,000" [P2]
- `eval_consistency_rule` = **50% (gates passing)** (verified)
  - "The Consistency Rule on Standard Evaluations is 50%." [P8]
- `eval_min_days` = **2** (verified)
  - "hit the profit target in at least 2 trading days while staying inside your Maximum Loss Limit, and you're Qualified." [P27]
- `eval_position_limit` = **5 minis / 50 micros** (verified)
  - "| Max Position | 5 minis, 50 micros | 10 minis, 100 micros | 15 minis, 150 micros" [P2]
- `eval_fee` = **$129 per month** (verified)
  - "| Price | $129/month | $239/month | $349/month" [P2]
  - note: Optional checkout add-on removes the Qualified consistency rule: homepage card 'No Consistency RuleOn your Qualified account OffOn+$70' (50K). Whether the $70 is one-time or monthly is not stated (UNVERIFIED).
- `eval_reset_fee` = **109** (verified)
  - "| Evaluation Reset | $109 | $199 | $289" [P2]
  - note: A Qualified Reset ($599 on 50K) may be used twice on an account that has never reached a payout request, within 7 days of breach (article 9492077).
- `activation_fee` = **0** (verified)
  - "3.) No Activation Fee" [P2]
- `funded_drawdown_amount` = **2000** (verified)
  - "50K Standard Qualified No Fee Once Qualified Minimum Trading Days 5 Profit Target None Max Position Size 5 minis / 50 micros Max Drawdown $2,000" [P7]
- `funded_daily_loss_limit` = **$1,000 soft lock (flatten, locked to next session; not a breach)** (verified)
  - "If you hit the Daily Loss Guard, you do not lose your Account, but your account will be locked until the next trading day (6PM ET)." [P15]
- `funded_consistency_rule` = **40% of net profit since last withdrawal (best day must be < 40%); gates withdrawals, resets each request, not a breach** (verified)
  - "The 40% Consistency Rule states during the Qualified stage, profits from any single trading day cannot be greater than or equal to 40% of net profits accumulated since last withdrawal request." [P8]
  - "This rule resets in between each account withdrawal request." [P8]
- `funded_position_limit` = **scaling plan 50K: <$1,500 profit 2 minis/20 micros; $1,500-2,000 3/30; $2,000+ 5/50** (verified)
  - "| Profit range | $50K minis | $50K micros | $100K minis | $100K micros | $150K minis | $150K micros" [P12]
  - "| Less than $1,500 profit | 2 | 20 | 3 | 30 | 3 | 30" [P12]
  - "| $1,500-2,000 profit | 3 | 30 | 4 | 40 | 4 | 40" [P12]
  - "| $2,000-3,000 profit | 5 | 50 | 5 | 50 | 5 | 50" [P12]
  - note: Help-centre Scaling Plan table (article 9492025, July 24, 2026) re-read cell by cell from the HTML: identical values (one cell reads '$2,000-3,000profit', a missing space -- the only 'garble'). Above $3,000 the 50K stays at 5/50.
- `payout_min` = **500** (verified)
  - "The minimum withdrawal request on Standard Accounts is $500:" [P20]
- `payout_cap` = **per request min(50% of profit, $3,000)** (verified)
  - "50k Standard Qualified Account maximum withdrawal is $3,000" [P20]
- `news_trading_terms` = **no orders 2 min before to 2 min after red-folder events on Qualified; first violation a warning, later ones breach** (verified)
  - "Subsequent violations after warning will lead to breach of the account." [P14]
- `max_accounts` = **5 Standard Qualified (3 for Standard accounts bought before July 27, 2026; T&C says 3 if any Standard or Advanced Qualified is active)** (verified)
  - "Standard Account: 5 Qualified Accounts (any standard accounts prior to July 27th, 2026 are limited to 3)" [P9]
  - note: CONFLICT with T&C Schedule 2 (see terms.max_accounts). Standard was relaunched July 27, 2026 ('Standard Account is back with some upgrades!').

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

**Pages quoted** (key: URL; article id; the page's own date as shown; all read 2026-11-15)

- [P1] https://tradeify.co/
- [P2] https://tradeify.co/select-plan
- [P3] https://tradeify.co/funded-trader-agreement; id section 4.2; page date: Last modified: October 2026
- [P4] https://tradeify.co/funded-trader-agreement; id section 6.7(b); page date: Last modified: October 2026
- [P5] https://tradeify.co/funded-trader-agreement; id section 6.7(c); page date: Last modified: October 2026
- [P6] https://tradeify.co/funded-trader-agreement; id section 6.6; page date: Last modified: October 2026
- [P7] https://tradeify.co/funded-trader-agreement; id section 6.5; page date: Last modified: October 2026
- [P8] https://tradeify.co/funded-trader-agreement; id section 6.8; page date: Last modified: October 2026
- [P9] https://tradeify.co/funded-trader-agreement; id section 5.2; page date: Last modified: October 2026
- [P10] https://tradeify.co/funded-trader-agreement; id section 7.5; page date: Last modified: October 2026
- [P11] https://tradeify.co/funded-trader-agreement; id section 4.5; page date: Last modified: October 2026
- [P12] https://tradeify.co/funded-trader-agreement; id section 4.3; page date: Last modified: October 2026
- [P13] https://tradeify.co/funded-trader-agreement; id section 4.4; page date: Last modified: October 2026
- [P14] https://tradeify.co/funded-trader-agreement; id section 2.5; page date: Last modified: October 2026
- [P15] https://tradeify.co/funded-trader-agreement; id section 6.9; page date: Last modified: October 2026
- [P16] https://tradeify.co/funded-trader-agreement; id section 6.7(h); page date: Last modified: October 2026
- [P17] https://tradeify.co/funded-trader-agreement; id section 6.4; page date: Last modified: October 2026
- [P18] https://tradeify.co/terms-of-use
- [P19] https://tradeify.co/select-plan-paid-daily


Official domains: tradeify.co, help.tradeify.co. Read 2026-11-15.
Plan captured: Select 50K (terms = Select Flex funded path; terms_select_daily = the fields where the Select Daily path differs).
Verdict: **PASS** -- Select 50K: EOD trailing drawdown on both funded paths and no funded consistency; 5 funded accounts per person/household (FTA 4.2); the agreement expects stops and targets and forbids nothing in hand-entered one-position bracket trading on NQ/MNQ.

Unreadable (not worked around):
- https://help.tradeify.co/ -- 403 Cloudflare challenge to curl; WebFetch on https://help.tradeify.co/en/ refused (HTTP 403)
- https://help.tradeify.co/en/articles/12853921-select-evaluation-accounts -- 403 Cloudflare challenge to curl; WebFetch refused (HTTP 403)
- https://help.tradeify.co/en/articles/10495915-growth-evaluation-accounts -- WebFetch refused (HTTP 403)
- https://help.tradeify.co/en/articles/10495938-lightning-funded-accounts -- WebFetch refused (HTTP 403)
- https://help.tradeify.co/en/articles/18370624-miami-plan-faq -- WebFetch refused (HTTP 403)

Plans seen:
- Select 50K (Select Flex / Select Daily funded paths): drawdown EOD trailing $2,000 (eval and both funded paths); lock UNVERIFIED; consistency evaluation 40%, funded none (both paths)
  - "rule2: [ ["Payout Frequency", "5 days", { tooltip: "" }], ["Max Payout", "$2,500", { tooltip: "" }], ["Consistency", "None", { tooltip: "" }], ["Daily Loss Limit", "None", { tooltip: "" }], ["Max Drawdown (EOD)", "$2,000", { tooltip: "" }]," [P1]
- Growth 50K: drawdown EOD trailing $2,000; DLL $1,250 (rises to the drawdown at 6% profit); consistency evaluation none, funded 35%
  - "["Max Contracts", "4 minis / 40 micros", { tooltip: "" }], ], funded: { rule1: [ ["Payout Frequency", "5 Days", { tooltip: "" }], ["Max Accounts", "5", { tooltip: "" }], ["Consistency", "35%", { tooltip: "" }]," [P1]
- Lightning 50K (instant funded, no evaluation): drawdown EOD $2,000; DLL $1,250; consistency evaluation n/a, funded 20% (25% payout 2, 30% payout 3+)
  - ""Consistency requirement moves to 25% for Payout 2 and 30% for Payout 3+"" [P1]
- Inter Miami 50K (limited edition): drawdown static $1,500; soft DLL $900; 30 micros; consistency evaluation none, funded not shown in plan data
  - "['Profit Target', '$3,500', { tooltip: '' }], ['Static Drawdown', '$1,500', { tooltip: '' }]," [P1]

**Screen**

- `drawdown_eval` = **eod_trailing; $2,000** (verified)
  - "evaluation: [ ["Profit Target", "$3,000", { tooltip: "" }], ["Trailing Max Drawdown (EOD)", "$2,000", { tooltip: "" }], ["Daily Loss Limit", "None", { tooltip: "" }], [ "Reset Fee", "$109"," [P1]
  - note: From the homepage plan data (SelectData, Tradovate/WealthCharts/Tradesea entries identical). Lock level UNVERIFIED (Help Center unreadable).
- `drawdown_funded` = **eod_trailing; $2,000 (both Select paths)** (verified)
  - "rule2: [ ["Payout Frequency", "5 days", { tooltip: "" }], ["Max Payout", "$2,500", { tooltip: "" }], ["Consistency", "None", { tooltip: "" }], ["Daily Loss Limit", "None", { tooltip: "" }], ["Max Drawdown (EOD)", "$2,000", { tooltip: "" }]," [P1]
  - "End-of-day drawdown" [P2]
- `consistency_eval` = **40%** (verified)
  - "["Consistency", "40%", { tooltip: "" }], ["Activation Fee", "None", { tooltip: "" }], ["Max Contracts", "4 minis / 40 micros", { tooltip: "" }]," [P1]
  - "It means you need to be profitable on at least 40% of your trading days during evaluation. For example, if you trade 10 days, you need to be green on at least 4 of them." [P2]
  - note: CONFLICT in meaning: the Select landing page FAQ defines the 40% as a share of green days, unlike the usual best-day share of profit; the governing definition is on the unreadable Help Center. The percentage (40%) is verified, its mechanics are not.
- `consistency_funded` = **none** (verified)
  - "No consistency rules once funded. Hit a big day? Get paid." [P2]
  - "rule1: [ ["Payout Frequency", "Daily", { tooltip: "" }], ["Max Payout", "$1,250", { tooltip: "" }], ["Consistency", "None", { tooltip: "" }], ["Daily Loss Limit", "$1,000", { tooltip: "" }], ["Max Drawdown (EOD)", "$2,000", { tooltip: "" }]," [P1]
- `max_funded_accounts` = **5 simulated funded accounts per individual and per household, across all account types** (verified)
  - "The Company limits the maximum number of Simulated Funded Accounts that may be held by any single individual to five (5). This limit applies on a per-individual and per-household basis and across ALL funded account types, including Advanced Challenge funded accounts, Growth Challenge funded accounts, Lightning Funded accounts, Select Flex funded accounts, and Select Daily funded accounts." [P3]
  - note: Evaluation count limit not stated on readable pages.
- `copy_trading` = **copying own trades across own accounts permitted only as far as the Help Center allows (unreadable); copying/mirroring with any other person prohibited** (verified)
  - "For the avoidance of doubt, this Section 6.7(b) restricts trading conduct between the Trader and other persons; the copying or mirroring of the Trader's own trades across the Trader's own Trader-Controlled Accounts is permitted to the extent expressly allowed by the rules published at the Help Center referenced in Section 4.1, provided always that such activity does not result in Opposing Positions prohibited by Section 6.7(c)." [P4]
  - note: The extent of the Help Center allowance is UNVERIFIED.
- `opposite_positions` = **prohibited without regard to intent: same product or same Product Group (Equity Index), within one account, across own accounts, and against accounts at other firms** (verified)
  - "The Trader is strictly prohibited from holding Opposing Positions in (i) the same futures product, or (ii) two or more futures products assigned to the same Product Group." [P5]
- `news` = **UNVERIFIED** (UNVERIFIED)
  - looked at: https://tradeify.co/ ; https://tradeify.co/funded-trader-agreement ; https://tradeify.co/terms-of-use ; https://tradeify.co/select-plan ; https://tradeify.co/select-plan-paid-daily ; https://tradeify.co/tradeify-vs-topstep
  - note: No news-trading rule on any readable tradeify.co page; the Help Center (where it would be) is blocked.
- `automation` = **own bots/algos permitted under conditions (sole ownership, not shared across firms, no HFT bots)** (verified)
  - "6.6 Automated Bots: The use of automated trading bots or algorithms (“bots/algos”) is permitted only under the following conditions:" [P6]
  - "No High-Frequency Trading (HFT) Bots: Personal bots are allowed as long as they are not high-frequency trading (HFT) bots." [P6]
  - note: Hand entry is not restricted.
- `sizing_gambling` = **consistent trading plan required: avoid maximum/larger sizes on single trades, keep sizes consistent, no flipping to register a day, no DCA, no HFT; microscalping guideline (>= 50% of profit from trades held > 10 s)** (verified)
  - "6.5 Consistency in Trading: The Trader must adhere to a consistent trading plan in terms of size, stops, and targets, avoiding maximum or larger contract sizes on single trades, refraining from flipping contracts just to register a “trading day,” maintaining consistent trading sizes, avoiding dollar-cost averaging and high-frequency trading, and demonstrating consistency in the trading plan." [P7]
  - "50% or more of the Trader’s account profit must come from trades held longer than ten (10) seconds." [P8]
- `note`: Pass rests on tradeify.co pages and the signed agreement; Help Center rules (incorporated and prevailing) are unread. FTA 6.5's 'consistent ... size, stops, and targets' and 'avoiding maximum or larger contract sizes on single trades' constrain any sizing schedule that steps size up and down.

**Terms (`terms`)**

- `eval_profit_target` = **3000** (verified)
  - "evaluation: [ ["Profit Target", "$3,000", { tooltip: "" }], ["Trailing Max Drawdown (EOD)", "$2,000", { tooltip: "" }], ["Daily Loss Limit", "None", { tooltip: "" }], [ "Reset Fee", "$109"," [P1]
  - "Meet your 6% profit target with 40% consistency." [P2]
- `eval_drawdown_amount` = **2000** (verified)
  - "evaluation: [ ["Profit Target", "$3,000", { tooltip: "" }], ["Trailing Max Drawdown (EOD)", "$2,000", { tooltip: "" }], ["Daily Loss Limit", "None", { tooltip: "" }], [ "Reset Fee", "$109"," [P1]
- `eval_drawdown_type` = **eod_trailing** (verified)
  - "End-of-day drawdown - no intraday traps" [P1]
- `eval_drawdown_lock` = **UNVERIFIED** (UNVERIFIED)
  - looked at: https://tradeify.co/ (page and inline scripts) ; https://tradeify.co/select-plan ; https://tradeify.co/funded-trader-agreement
  - note: Help Center (blocked) holds the drawdown methodology per FTA 4.1.
- `eval_daily_loss_limit` = **none** (verified)
  - "evaluation: [ ["Profit Target", "$3,000", { tooltip: "" }], ["Trailing Max Drawdown (EOD)", "$2,000", { tooltip: "" }], ["Daily Loss Limit", "None", { tooltip: "" }], [ "Reset Fee", "$109"," [P1]
- `eval_consistency_rule` = **40% (mechanics UNVERIFIED; landing-page FAQ describes it as green on >= 40% of trading days)** (verified)
  - "["Consistency", "40%", { tooltip: "" }], ["Activation Fee", "None", { tooltip: "" }], ["Max Contracts", "4 minis / 40 micros", { tooltip: "" }]," [P1]
  - "This ensures you can pass in 3 days minimum. Once funded, consistency rules disappear." [P2]
  - note: The homepage scripts also carry an unlabelled 'multiConsistencyData' evaluation add-on for Select 50K (price 205, reset $145, max payout daily $1,250 / flex $2,000; plan_addon_id=26) whose rule is not described on any readable page.
- `eval_min_days` = **3 (as stated in marketing: 'as few as 3 trading days')** (verified)
  - "Pass in as few as 3 trading days — one of the fastest evaluation in the industry." [P2]
  - note: Whether 3 is a hard minimum-days rule or a consequence of the 40% rule is not stated; Help Center unreadable.
- `eval_position_limit` = **4 minis / 40 micros** (verified)
  - "["Consistency", "40%", { tooltip: "" }], ["Activation Fee", "None", { tooltip: "" }], ["Max Contracts", "4 minis / 40 micros", { tooltip: "" }]," [P1]
- `eval_fee` = **165 one-time (homepage plan data; coupon NOV 30% off until 30 November)** (verified)
  - "name: "50K", isSelected: true, isVisible: true, price: 165, subscription: "one time payment", couponCode: "select"," [P1]
  - "Get 30% Off with code "NOV" - 45% off 25k accounts (excluding Miami)" [P1]
  - note: CONFLICT: the /select-plan page's size picker shows 50K at $111 (that page carries an expired 'ENDS 13 NOVEMBER' banner and lorem-ipsum template text). Price before/after coupon not certain.
- `eval_reset_fee` = **109** (verified)
  - "evaluation: [ ["Profit Target", "$3,000", { tooltip: "" }], ["Trailing Max Drawdown (EOD)", "$2,000", { tooltip: "" }], ["Daily Loss Limit", "None", { tooltip: "" }], [ "Reset Fee", "$109"," [P1]
- `activation_fee` = **none** (verified)
  - "["Consistency", "40%", { tooltip: "" }], ["Activation Fee", "None", { tooltip: "" }], ["Max Contracts", "4 minis / 40 micros", { tooltip: "" }]," [P1]
  - "No activation fees" [P2]
- `eval_count_limit` = **UNVERIFIED** (UNVERIFIED)
  - looked at: https://tradeify.co/funded-trader-agreement ; https://tradeify.co/terms-of-use ; https://tradeify.co/
  - note: Only the funded cap (5) and one Tradeify login per individual/household are stated.
- `eval_time_limit` = **UNVERIFIED** (UNVERIFIED)
  - looked at: https://tradeify.co/ ; https://tradeify.co/select-plan ; https://tradeify.co/funded-trader-agreement
- `funded_type` = **simulated funded account; discretionary move to Tradeify Elite Live (internal guideline: 10 approved payouts, or 3 on one account); while Live, no other Tradeify accounts for the trader or household** (verified)
  - "three (3) approved payouts on a single Simulated Funded Account." [P9]
  - "Traders who are transitioned to Tradeify Elite Live (Section 5) may NOT hold ANY other funded accounts, challenge accounts, or straight-to-sim accounts while their Elite Live account is active." [P3]
  - note: A Live call-up ends the multi-account design (all other accounts must go).
- `funded_drawdown_amount` = **2000** (verified)
  - "rule2: [ ["Payout Frequency", "5 days", { tooltip: "" }], ["Max Payout", "$2,500", { tooltip: "" }], ["Consistency", "None", { tooltip: "" }], ["Daily Loss Limit", "None", { tooltip: "" }], ["Max Drawdown (EOD)", "$2,000", { tooltip: "" }]," [P1]
- `funded_drawdown_type` = **eod_trailing (labelled 'Max Drawdown (EOD)')** (verified)
  - "rule2: [ ["Payout Frequency", "5 days", { tooltip: "" }], ["Max Payout", "$2,500", { tooltip: "" }], ["Consistency", "None", { tooltip: "" }], ["Daily Loss Limit", "None", { tooltip: "" }], ["Max Drawdown (EOD)", "$2,000", { tooltip: "" }]," [P1]
  - note: Funded label drops 'Trailing'; whether it trails is not stated on readable pages (assume as eval until the Help Center is read).
- `funded_drawdown_lock` = **UNVERIFIED** (UNVERIFIED)
  - looked at: https://tradeify.co/ (inline scripts) ; https://tradeify.co/select-plan ; https://tradeify.co/funded-trader-agreement
- `payout_balance_consequence` = **UNVERIFIED** (UNVERIFIED)
  - looked at: https://tradeify.co/funded-trader-agreement ; https://tradeify.co/select-plan ; https://tradeify.co/
  - note: FTA 4.1 lists 'minimum balance requirements' as Help Center content.
- `funded_daily_loss_limit` = **none (Select Flex)** (verified)
  - "rule2: [ ["Payout Frequency", "5 days", { tooltip: "" }], ["Max Payout", "$2,500", { tooltip: "" }], ["Consistency", "None", { tooltip: "" }], ["Daily Loss Limit", "None", { tooltip: "" }], ["Max Drawdown (EOD)", "$2,000", { tooltip: "" }]," [P1]
- `funded_consistency_rule` = **none** (verified)
  - "Once you your pass eval, decide how you want to get paid. Both paths have zero consistency rules." [P2]
- `funded_position_limit` = **UNVERIFIED (funded Select rows list no contract limit; eval is 4 minis / 40 micros)** (UNVERIFIED)
  - looked at: https://tradeify.co/ (SelectData in inline scripts) ; https://tradeify.co/select-plan
- `funded_monthly_fee` = **none (one-time purchases only)** (verified)
  - "All accounts and services currently offered by the Company are one-time purchases." [P10]
- `payout_min` = **UNVERIFIED** (UNVERIFIED)
  - looked at: https://tradeify.co/ ; https://tradeify.co/select-plan ; https://tradeify.co/select-plan-paid-daily ; https://tradeify.co/funded-trader-agreement
- `payout_cap` = **Select Flex: $2,500 per payout (Select Daily: $1,250); lifetime cap not stated** (verified)
  - "rule2: [ ["Payout Frequency", "5 days", { tooltip: "" }], ["Max Payout", "$2,500", { tooltip: "" }], ["Consistency", "None", { tooltip: "" }], ["Daily Loss Limit", "None", { tooltip: "" }], ["Max Drawdown (EOD)", "$2,000", { tooltip: "" }]," [P1]
  - note: The unlabelled Select 50K add-on variant shows flex $2,000 / daily $1,250 instead.
- `payout_frequency_gate` = **Select Flex: every 5 days (gate details - winning days, buffer - UNVERIFIED)** (verified)
  - "rule2: [ ["Payout Frequency", "5 days", { tooltip: "" }], ["Max Payout", "$2,500", { tooltip: "" }], ["Consistency", "None", { tooltip: "" }], ["Daily Loss Limit", "None", { tooltip: "" }], ["Max Drawdown (EOD)", "$2,000", { tooltip: "" }]," [P1]
  - "Where an evaluation path requires the Trader to choose between payout policies (for example, between Select Flex and Select Daily upon passing a Select Challenge), that choice is permanent and irrevocable for the specific funded account in question." [P11]
- `payout_split` = **90%** (verified)
  - "Unless otherwise specified for a particular account type, profits withdrawn are split90% to the Trader and 10% to the Company." [P12]
  - "You Keep 90% Profits" [P2]
- `payout_processing_days` = **typically 24-48 hours after approval (up to 72 h outside business hours); approval may take to the end of the next payout cycle** (verified)
  - "Once a payout request is approved, funds are withdrawn from the Trader’s account and payment is typically issued within twenty-four to forty-eight (24-48) hours." [P13]
  - "The Company reserves the right to take up to the end of the next payout cycle to approve, review, or deny a payout request." [P13]
  - note: Marketing pages claim payouts in about 60 minutes.
- `payout_fee` = **UNVERIFIED** (UNVERIFIED)
  - looked at: https://tradeify.co/funded-trader-agreement ; https://tradeify.co/terms-of-use ; https://tradeify.co/
- `payout_count_limit` = **UNVERIFIED** (UNVERIFIED)
  - looked at: https://tradeify.co/funded-trader-agreement ; https://tradeify.co/select-plan ; https://tradeify.co/
  - note: No cap stated; a Live call-up (discretionary, guideline 3 payouts on one account) would end sim payouts.
- `max_accounts` = **5 funded per individual and household (all types combined); one Tradeify login per individual and household** (verified)
  - "Example: A trader may NOT hold three (3) Lightning Funded accounts, two (2) Select Flex accounts, and one (1) Growth funded account. The maximum total is five (5) funded accounts in any combination." [P3]
  - "Each individual may register for and hold only one (1) Tradeify account." [P14]
- `inactivity_rule` = **at least one trade per calendar week, else account may be classified inactive** (verified)
  - "To maintain an active account status, the Trader is required to execute at least one trade per calendar week." [P15]
- `copy_trading_terms` = **own-account copying allowed only as the Help Center permits (unread); team/group trading and copying with other persons prohibited** (verified)
  - "Team trading, collaborative trading, group trading, the management of a Trader's account by or on behalf of any third party, and the copying or mirroring of trades between the Trader and any other person are strictly prohibited." [P4]
- `cross_account_hedging` = **prohibited, intent irrelevant, incl. micro vs mini in the same Product Group and versus accounts at other prop firms (NinjaTrader monitoring data may be used)** (verified)
  - "Holding a position in a Trader-Controlled Account opposite a position in an External Account constitutes hedging and is a breach of this Agreement." [P5]
  - "Any breach of this Section 6.7 will result in every account involved in the breach being placed in violation status, and in forfeiture of any profits generated during the period of the violation, whether or not those profits have been requested for payout." [P16]
  - note: 'Opposing Positions' covers positions held at the same time 'whether the positions were entered simultaneously or at different times': a design running independent NQ signals on several accounts must never be long on one and short on another at the same moment (ES vs NQ too, same Equity Index group).
- `news_trading_terms` = **UNVERIFIED** (UNVERIFIED)
  - looked at: https://tradeify.co/funded-trader-agreement ; https://tradeify.co/terms-of-use ; https://tradeify.co/ ; https://tradeify.co/select-plan
- `automation_terms` = **personal bots allowed: sole owner, not used across multiple firms, no HFT bots, documentation on request** (verified)
  - "Exclusive Use: While the Trader may use the bot on the Trader’s personal accounts, using it across multiple firms is against Tradeify’s policy." [P6]
- `sizing_or_gambling_terms` = **avoid maximum or larger contract sizes on single trades; consistent sizes, stops and targets; no flipping to log a day; no DCA** (verified)
  - "6.5 Consistency in Trading: The Trader must adhere to a consistent trading plan in terms of size, stops, and targets, avoiding maximum or larger contract sizes on single trades, refraining from flipping contracts just to register a “trading day,” maintaining consistent trading sizes, avoiding dollar-cost averaging and high-frequency trading, and demonstrating consistency in the trading plan." [P7]
- `other_conduct_bearing` = **microscalping guideline (>= 50% of profit from trades > 10 s); short-term/high-frequency manipulative trades barred; trade only the active contract month; VPS/VM access that masks identity barred** (verified)
  - "Trades executed in less than ten (10) seconds are difficult to reliably replicate or copy, so we have implemented the following guideline: 50% or more of the Trader’s account profit must come from trades held longer than ten (10) seconds." [P8]
  - "This includes short-term or high-frequency trades." [P17]
  - "use a Virtual Private Server (“VPS”), virtual machine, virtualized environment, remote computing environment, or similar technology to access or use Tradeify’s Site, platform, accounts, or services where such technology obscures, alters, masks, or prevents Tradeify from reliably verifying the user’s device, network, location, identity, or account activity; or" [P18]
- `permitted_products` = **futures incl. stock indices (S&P 500, Nasdaq); exact symbol list UNVERIFIED (Help Center)** (verified)
  - "Stock indices like the S&P 500 and Nasdaq, metals like gold and silver, energy like crude oil and natural gas, plus currencies, bonds, and even crops." [P1]

**Terms (`terms_select_daily`)**

- `note`: Fields where the Select Daily funded path differs from Select Flex; all other fields as in terms.
- `funded_daily_loss_limit` = **1000** (verified)
  - "rule1: [ ["Payout Frequency", "Daily", { tooltip: "" }], ["Max Payout", "$1,250", { tooltip: "" }], ["Consistency", "None", { tooltip: "" }], ["Daily Loss Limit", "$1,000", { tooltip: "" }], ["Max Drawdown (EOD)", "$2,000", { tooltip: "" }]," [P1]
- `payout_cap` = **$1,250 per payout** (verified)
  - "rule1: [ ["Payout Frequency", "Daily", { tooltip: "" }], ["Max Payout", "$1,250", { tooltip: "" }], ["Consistency", "None", { tooltip: "" }], ["Daily Loss Limit", "$1,000", { tooltip: "" }], ["Max Drawdown (EOD)", "$2,000", { tooltip: "" }]," [P1]
- `payout_frequency_gate` = **daily (gate details UNVERIFIED)** (verified)
  - "You Keep 90% Profits" [P19]
  - "rule1: [ ["Payout Frequency", "Daily", { tooltip: "" }], ["Max Payout", "$1,250", { tooltip: "" }], ["Consistency", "None", { tooltip: "" }], ["Daily Loss Limit", "$1,000", { tooltip: "" }], ["Max Drawdown (EOD)", "$2,000", { tooltip: "" }]," [P1]

**Access note** (reader's section)

- The Funded Trader Agreement (section 4.1) incorporates the Help Center rules by reference and says they prevail for trading rules, so every rule that lives only there (payout gates, buffers, minimum days, drawdown lock, permitted own-account copying, news) is UNVERIFIED. The terms read here come from tradeify.co: the homepage plan data in its inline scripts, the Select landing pages, the Terms of Use and the Funded Trader Agreement. The Terms of Use forbid 'any robot, spider, scraper or other automatic device' to access the Site without written permission; seven tradeify.co pages were fetched (curl, 1 s apart) before that clause was read, and no more were fetched after it.

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

**Pages quoted** (key: URL; article id; the page's own date as shown; all read 2026-11-15)

- [P1] https://helpfutures.fundednext.com/en/articles/17230245-is-there-any-consistency-rule-to-be-followed-in-the-fundednext-futures-challenge-fundednext-account; id 17230245; page date: Updated over 3 weeks ago
- [P2] https://helpfutures.fundednext.com/en/articles/17229536-fundednext-futures-legacy-challenge-all-rules; id 17229536; page date: Updated over 3 weeks ago
- [P3] https://helpfutures.fundednext.com/en/articles/17242064-how-can-i-withdraw-my-performance-reward; id 17242064; page date: October 12, 2026
- [P4] https://helpfutures.fundednext.com/en/articles/16847874-what-is-the-fundednext-futures-fnl-003-50k-instant-account; id 16847874; page date: September 8, 2026
- [P5] https://helpfutures.fundednext.com/en/articles/17229829-fundednext-futures-flex-challenge-all-rules; id 17229829; page date: October 13, 2026
- [P6] https://helpfutures.fundednext.com/en/articles/17229848-fundednext-futures-flex-fundednext-account-all-rules; id 17229848; page date: Updated over 3 weeks ago
- [P7] https://helpfutures.fundednext.com/en/articles/17225812-how-many-accounts-can-i-hold-with-fundednext-futures-and-what-is-the-maximum-allocation-available; id 17225812; page date: September 30, 2026
- [P8] https://helpfutures.fundednext.com/en/articles/17230319-what-is-copy-group-trading-policy-at-fundednext-futures; id 17230319; page date: September 30, 2026
- [P9] https://helpfutures.fundednext.com/en/articles/14298337-what-are-the-prohibited-trading-strategies-of-fundednext-futures; id 14298337; page date: September 30, 2026
- [P10] https://helpfutures.fundednext.com/en/articles/17225788-fundednext-futures-most-frequently-asked-questions; id 17225788; page date: Updated over a week ago
- [P11] https://helpfutures.fundednext.com/en/articles/17230400-what-is-the-disciplined-trader-program-of-fundednext-futures-and-how-does-it-help-traders-build-consistency; id 17230400; page date: September 30, 2026
- [P12] https://helpfutures.fundednext.com/en/articles/17230388-does-fundednext-futures-allow-high-frequency-trading-hft; id 17230388; page date: September 30, 2026
- [P13] https://helpfutures.fundednext.com/en/articles/17230376-what-is-the-micro-scalping-policy-in-fundednext-futures; id 17230376; page date: September 30, 2026
- [P14] https://helpfutures.fundednext.com/en/articles/17230292-daily-loss-limit-and-maximum-loss-limit-at-fundednext-futures; id 17230292; page date: Updated over 3 weeks ago
- [P15] https://helpfutures.fundednext.com/en/articles/17228852-what-are-the-reset-conditions-and-fees-at-fundednext-futures; id 17228852; page date: Updated over a week ago
- [P16] https://helpfutures.fundednext.com/en/articles/16522296-road-to-live-trading-rapid-flex-direct; id 16522296; page date: Updated over 3 weeks ago
- [P17] https://helpfutures.fundednext.com/en/articles/17242096-what-will-be-my-reward-share-from-the-futures-fundednext-account; id 17242096; page date: October 12, 2026
- [P18] https://helpfutures.fundednext.com/en/articles/17242434-what-is-fundednext-futures-brand-promise; id 17242434; page date: September 30, 2026
- [P19] https://helpfutures.fundednext.com/en/articles/17242085-what-methods-are-available-for-performance-reward-withdrawal-in-fundednext-futures; id 17242085; page date: Updated this week
- [P20] https://helpfutures.fundednext.com/en/articles/17228935-is-there-any-inactivity-period-in-fundednext-futures; id 17228935; page date: October 12, 2026
- [P21] https://helpfutures.fundednext.com/en/articles/17230325-which-order-types-should-i-use-for-stop-loss-and-take-profit-in-futures-trading; id 17230325
- [P22] https://helpfutures.fundednext.com/en/articles/17225740-which-symbols-instruments-can-i-trade-on-fundednext-futures; id 17225740; page date: September 30, 2026
- [P23] https://helpfutures.fundednext.com/en/articles/17229713-fundednext-futures-rapid-pro-fundednext-account-all-rules; id 17229713; page date: Updated over a week ago


Official domains: fundednext.com, helpfutures.fundednext.com. Read 2026-11-15.
Plan captured: Flex 50K.
Verdict: **PASS** -- Flex 50K: EOD trailing MLL on the funded account and no funded consistency rule; 5 funded accounts per person/household; hand-entered one-direction bracket trades are not prohibited (only tight two-sided no-slippage bracket straddles, micro-scalping and tick scalping are).

Plans seen:
- Flex 50K: drawdown EOD trailing $1,500, locks at $50,100 (eval and funded); first withdrawal resets MLL to $50,100; consistency evaluation 40% (best day <= 40% of target, else target recalculated), funded none
  - "| Flex | ✅ 40% | ❌ None" [P1]
- Rapid Pro 50K: drawdown EOD trailing $2,000, locks at $50,100 (eval and funded); optional DLL add-on $1,000; consistency evaluation none, funded 40% (withdrawal gate)
  - "| Rapid Pro | ❌ None | ✅ 40%" [P1]
- Rapid Daily 50K: drawdown EOD trailing $2,000, locks at $50,100; daily loss limit $1,000 (soft) at every stage; funded buffer $52,100; consistency evaluation none, funded none (buffer rule)
  - "| Rapid Daily | ❌ None | ❌ None (uses buffer rule)" [P1]
- Direct Account 50K (no evaluation): drawdown EOD trailing $2,000, locks at $50,100; DLL $1,000; $2,100 buffer; 7-day inactivity breach; consistency evaluation n/a (no challenge), funded 20% perpetual (all-time best day <= 20% of current cycle profit)
  - "| Direct | N/A | ✅ 20%" [P1]
- Legacy 50K (discontinued): drawdown EOD trailing $2,000, locks at initial balance; consistency evaluation 40%, funded none
  - "Important Notice: As of October 11, Legacy Accounts are no longer available for purchase. Existing Legacy Accounts are also not eligible for resets." [P2]
- Bolt 50K (discontinued): drawdown not read (product withdrawn); MLL set to $50,100 after first withdrawal per the withdrawal article; consistency evaluation not read, funded not read
  - "Note: Effective 10 July 2026, Rapid and Bolt accounts will no longer be available for new purchases or account resets." [P3]
- FNL:003 50K Instant (Labs limited release): drawdown EOD trailing, locks at $50,100; consistency evaluation n/a (no challenge), funded 20% perpetual
  - "Each trader can purchase 3 FNL:003 Instant Accounts, and these are not counted against your standard 5 FundedNext Account maximum allocation limit." [P4]

**Screen**

- `drawdown_eval` = **eod_trailing; $1,500; locks at $50,100** (verified)
  - "It follows a Trailing End-of-Day (EOD) system, updating once per day based on your highest balance that day." [P5]
  - "| Account Size | Maximum Loss Limit | MLL Locks At" [P5]
  - "| $50,000 | $1,500 | $50,100" [P5]
  - note: A floating loss that touches the MLL breaches intraday; the level itself moves only at end of day (05:00 PM CT per the loss-limit article).
- `drawdown_funded` = **eod_trailing; $1,500; locks at $50,100; first withdrawal resets MLL to $50,100** (verified)
  - "The Maximum Loss Limit (MLL) continues to apply on your funded account, using the same Trailing End-of-Day (EOD) system as the Challenge:" [P6]
  - "Your first withdrawal resets the MLL to the lock point for your size ($50,100 / $100,100 / $150,100)." [P6]
- `consistency_eval` = **40% of profit target per day; exceeding it raises the target to best day / 0.40 (no breach)** (verified)
  - "Yes. The Consistency Rule applies throughout the Challenge Phase. Your profit on any single day cannot exceed 40% of your total profit target." [P5]
  - "Required Total Profit = Highest Daily Profit ÷ 40%" [P5]
- `consistency_funded` = **none** (verified)
  - "No. Unlike the Challenge Phase, there is no Consistency Rule on the Flex FundedNext Account. You have full flexibility in how much you earn on any given day." [P6]
  - note: The payout gate instead is 5 Benchmark Days of $200 and $500 cycle profit (see terms.payout_frequency_gate).
- `max_funded_accounts` = **5 active FundedNext accounts (per user and per household); max 10 issued per calendar month; challenges up to $750,000 combined allocation** (verified)
  - "FundedNext Accounts: You can hold up to 5 active FundedNext Accounts at any given moment, regardless of individual account sizes or models. This limit applies per user and per household." [P7]
  - "A maximum of 10 FundedNext Accounts can be issued to you within a calendar month." [P7]
  - note: Household = same residential address or IP. A passed challenge beyond the cap is held pending until a slot frees.
- `copy_trading` = **allowed between own accounts (and to own accounts at other prop firms, same registered name); copying others or signals prohibited** (verified)
  - "Copy trading within FundedNext is allowed. Traders can freely copy trades between their own FundedNext Accounts." [P8]
- `opposite_positions` = **prohibited (reverse hedging within or across own accounts, incl. NQ vs MNQ and correlated instruments in the same asset group)** (verified)
  - "Reverse hedging is when a single trader, a single beneficial owner, holds both sides of the offset, buying one and selling the other." [P9]
  - "It can be done across the trader's own accounts or within a single account." [P9]
- `news` = **not restricted (except for traders enrolled in the Disciplined Trader Program)** (verified)
  - "No — FundedNext Futures does not restrict news trading." [P10]
  - "News Trading: Strictly prohibited during high-impact economic events." [P11]
  - note: The prohibition applies only inside the corrective Disciplined Trader Program (entered after a warning for high-risk behaviour).
- `automation` = **EAs/bots allowed (no support; customised, distinct strategy); HFT prohibited and automated systems monitored** (verified)
  - "At FundedNext Futures, you are allowed to use automated trading systems such as Expert Advisors (EAs) and trading bots during both the Challenge and on FundedNext Accounts." [P10]
  - "No, FundedNext Futures does not allow High-Frequency Trading." [P12]
  - note: Our trades are hand-entered; nothing found forbids that.
- `sizing_gambling` = **all-in / account flipping prohibited; contracts over the limit have profits deducted; micro-scalping (trades closed within 10 s) >= 40% of cycle profit is deducted on funded accounts** (verified)
  - "Account flipping and inconsistent contract execution involve using high margin to rapidly grow or blow up accounts through reckless, oversized positions." [P9]
  - "A Micro-Scalping percentage at or above 40% constitutes a violation." [P13]
- `note`: Caveat for the design: the prohibited 'Bracket Strategies' item targets two-sided buy-stop/sell-stop brackets with tight targets exploiting no slippage on NQ; a single entry with its stop and target is not that pattern, but tight targets held < 10 s would fall under micro-scalping. 'Account Rolling' (buying many challenges and sacrificing some) is monitored and can cut purchase rights.

**Terms (`terms`)**

- `eval_profit_target` = **2500** (verified)
  - "| Account Size | Profit Target | Maximum Loss Limit | MLL Locks At" [P5]
  - "| $50,000 | $2,500 | $1,500 | $50,100" [P5]
- `eval_drawdown_amount` = **1500** (verified)
  - "| $50,000 | $2,500 | $1,500 | $50,100" [P5]
- `eval_drawdown_type` = **eod_trailing** (verified)
  - "The MLL adjusts at the end of each trading day, not in real time." [P5]
  - "It updates once per day at the end of the trading day (05:00 PM CT) — not in real time." [P14]
  - note: Intraday floating loss reaching the MLL breaches instantly.
- `eval_drawdown_lock` = **locks at $50,100 (initial + $100)** (verified)
  - "It stops trailing and locks once your balance reaches the lock point for your size ($50,100 / $100,100 / $150,100)." [P5]
  - note: Read as: the MLL level stops trailing once it reaches $50,100 (i.e. after the EOD balance reaches $51,600); the article's wording says 'once your balance reaches the lock point', which is the MLL level.
- `eval_daily_loss_limit` = **none** (verified)
  - "No. The Flex Challenge has no daily loss limit at any stage, giving you more flexibility in trade management." [P5]
- `eval_consistency_rule` = **40% of profit target per day; overshoot recalculates target = best day / 0.40** (verified)
  - "If you earn $1,500 in a day: $1,500 ÷ 0.40 = $3,750. You would now need $3,750 total to pass, instead of $2,500." [P5]
- `eval_min_days` = **UNVERIFIED (no minimum-days rule stated)** (UNVERIFIED)
  - looked at: https://helpfutures.fundednext.com/en/articles/17229829-fundednext-futures-flex-challenge-all-rules ; https://helpfutures.fundednext.com/en/articles/17229807-what-is-fundednext-futures-flex-challenge ; https://helpfutures.fundednext.com/en/articles/17230209-what-are-benchmark-days-at-fundednext-futures
  - note: The Benchmark Days article says no Benchmark Day requirement in any Challenge Phase. The 40% rule implies at least 3 profitable days to reach $2,500 without raising the target (arithmetic, not a stated rule).
- `eval_position_limit` = **3 e-mini / 30 micro (1:10 mix); fixed, no scaling** (verified)
  - "| $50,000 | 3 e-mini / 30 micro e-mini" [P5]
  - "If you exceed the limit, only the excess contracts count as violations: profit from them is deducted, while losses still count." [P5]
- `eval_fee` = **one-time: $141.99 list; $74.99 first 2 purchases, $84.99 from the 3rd (with coupon FNFLEX)** (verified)
  - "| Account Size | Account Price | First 2 Purchases | 3 Purchases Onward" [P5]
  - "| $50,000 | $141.99 | $74.99 | $84.99" [P5]
  - "One-Time Fee Only: A single fee is paid at the start when you purchase a Challenge." [P10]
  - note: The discount offer article says 47% off the first 2 and 40% off from the 3rd with coupon FNFLEX; offer prices may change.
- `eval_reset_fee` = **82.99** (verified)
  - "| Flex 50K | $141.99 | $82.99" [P15]
  - note: Resets are unlimited up to the $750,000 challenge allocation; funded accounts cannot be reset.
- `activation_fee` = **none** (verified)
  - "Free Transition: Moving from a Challenge to a FundedNext Account involves no additional cost." [P10]
- `eval_count_limit` = **no limit on purchases; combined challenge allocation up to $750,000 at a time** (verified)
  - "Challenge Accounts: Up to $750,000 in total allocation at any one time." [P7]
- `eval_time_limit` = **none** (verified)
  - "No. There is no time limit — take as long as you need to reach your profit target while following the rules." [P5]
  - note: Subject to the 30-calendar-day inactivity breach.
- `funded_type` = **simulated FundedNext Account; concluded after the 5th Performance Reward; live review pool after 15 Performance Rewards across the profile** (verified)
  - "After your 5th Performance Reward, the Flex FundedNext Account is concluded." [P6]
  - "New to live: 15 Performance Rewards across your FundedNext journey." [P16]
  - note: On reaching the 15th reward all accounts are closed for review; live selection is discretionary; challenge accounts are closed without refund at transition.
- `funded_drawdown_amount` = **1500** (verified)
  - "| $50,000 | $1,500 | $50,100" [P6]
- `funded_drawdown_type` = **eod_trailing** (verified)
  - "The Maximum Loss Limit (MLL) continues to apply on your funded account, using the same Trailing End-of-Day (EOD) system as the Challenge:" [P6]
- `funded_drawdown_lock` = **locks at $50,100** (verified)
  - "It stops trailing and locks once your balance reaches the lock point for your size ($50,100 / $100,100 / $150,100)." [P6]
- `payout_balance_consequence` = **first withdrawal sets the MLL to $50,100 (initial + $100); withdrawn amount leaves the balance** (verified)
  - "Your first withdrawal resets the MLL to your account initial balance + $100." [P6]
  - "A trader with a $50K Flex FundedNext Account with a 95% Reward Share makes $3,000 growth and decides to withdraw $1,500 (the 50% amount, which is under the limit)." [P17]
  - "Account balance after withdrawal: $51,500" [P17]
  - note: Since the lock is an MLL level, a first payout taken before the MLL has trailed to $50,100 raises the floor immediately to $50,100.
- `funded_daily_loss_limit` = **none** (verified)
  - "No. There is no daily loss limit on the Flex FundedNext Account." [P6]
- `funded_consistency_rule` = **none** (verified)
  - "No. Unlike the Challenge Phase, there is no Consistency Rule on the Flex FundedNext Account." [P6]
- `funded_position_limit` = **3 e-mini / 30 micro; fixed, no scaling plan** (verified)
  - "Your contract limit is fixed at account creation and does not increase with profit. Flex applies the same limits on the FundedNext Account as during the Challenge:" [P6]
  - "| $50,000 | 3 e-mini / 30 micro e-mini" [P6]
- `funded_monthly_fee` = **none** (verified)
  - "No Monthly Subscription Fees: You are not required to pay recurring fees for maintaining a Challenge or FundedNext Account." [P10]
- `payout_min` = **250** (verified)
  - "| Minimum Withdrawal | $250 | $250 | $250" [P6]
  - note: Bank transfer as a method has its own $1,000 minimum.
- `payout_cap` = **per cycle: up to 50% of accumulated profit, max $1,500 (50K); lifetime cap not stated (account concludes after 5 rewards)** (verified)
  - "| Maximum Withdrawal | Up to 50% (max $1,500) | Up to 50% (max $2,500) | Up to 50% (max $4,000)" [P6]
  - "You can withdraw up to 50% of your accumulated profit per cycle, capped by size ($1,500 / $2,500 / $4,000), with a $250 minimum and at least $500 profit in the current cycle." [P6]
  - note: Five rewards at the $1,500 cap would bound gross requests at $7,500 per account; that is arithmetic, not a stated lifetime cap.
- `payout_frequency_gate` = **per cycle: 5 Benchmark Days (days with >= $200 profit) and >= $500 profit in the current cycle; request at end of a day with no new trade** (verified)
  - "| Benchmark Days | 5 days of $200 | 5 days of $200 | 5 days of $250" [P6]
  - "| Minimum Profit (current cycle) | $500 | $500 | $500" [P6]
  - "Please note: placing a trade on the same day removes the transfer-to-wallet option for that day." [P6]
  - note: No buffer rule on Flex. Benchmark days need not be consecutive (not stated either way).
- `payout_split` = **95%** (verified)
  - "You receive a 95% Reward Share of the requested Performance Reward" [P6]
- `payout_processing_days` = **within 24 hours of transfer initiation (Brand Promise, $1,000 compensation if late; excludes bank transfer and manual cases)** (verified)
  - "Timely Processing: Withdrawal requests are processed within 24 hours." [P18]
  - "Note: Performance Reward requests submitted via Bank Transfer are not eligible for the FundedNext Brand Promise." [P19]
  - note: The futures homepage shows '40 hours Avg. Processing Time' (marketing statistic).
- `payout_fee` = **UNVERIFIED** (UNVERIFIED)
  - looked at: https://helpfutures.fundednext.com/en/articles/17242064-how-can-i-withdraw-my-performance-reward ; https://helpfutures.fundednext.com/en/articles/17242085-what-methods-are-available-for-performance-reward-withdrawal-in-fundednext-futures ; https://helpfutures.fundednext.com/en/articles/17242096-what-will-be-my-reward-share-from-the-futures-fundednext-account
  - note: Methods: USDT/USDC, RiseWorks, card, bank transfer (min $1,000), FNmarkets; no fee schedule stated.
- `payout_count_limit` = **5** (verified)
  - "After your 5th Performance Reward, the Flex FundedNext Account is concluded." [P6]
- `max_accounts` = **5 active funded (per user and household), 10 issued per calendar month; challenges up to $750,000 combined** (verified)
  - "A household is defined as family members or multiple users who share the same residential address or IP address." [P7]
  - "Maximum allocation limits are subject to periodic review and may be adjusted at FundedNext’s discretion." [P7]
- `inactivity_rule` = **breach after 30 consecutive calendar days with no trade (challenge and funded)** (verified)
  - "FundedNext Accounts: Marked as inactive and deactivated after 30 consecutive calendar days of no trades." [P20]
- `copy_trading_terms` = **own accounts only (FundedNext and other prop firms under the same registered name); signal services, group trading and copying others prohibited** (verified)
  - "Copy trading between FundedNext and other prop firms is allowed if the trader owns all accounts involved." [P8]
  - "Traders cannot subscribe to any trading signal services or use external signals to guide their trading decisions." [P8]
- `cross_account_hedging` = **prohibited: reverse hedging across own accounts or within one, coordinated hedging, and opposite positions in correlated instruments of the same asset group** (verified)
  - "Reverse hedging (across accounts): A trader opens a buy on NQ in Account A and a sell on MNQ in Account B, both under their control." [P9]
  - "Hedging with correlated instruments means holding opposing positions, one long and one short, at the same time on two different underlyings that move together within the same Asset Group." [P9]
- `news_trading_terms` = **not restricted (FAQ and stop-loss article); prohibited only for traders in the Disciplined Trader Program** (verified)
  - "News trading is allowed, but riskier. FundedNext Futures doesn't restrict news trading, but during news the market can move rapidly and your SL may not fill at your intended price." [P21]
  - "Trading during high-impact economic news events is strictly prohibited, as these periods often lead to heightened volatility and emotionally driven decisions rather than strategic execution." [P11]
  - note: The prohibited-strategies page also bans 'trading within 2% of CME price limits' and gapped/illiquid market trading.
- `automation_terms` = **EAs and bots permitted with conditions (own customised strategy, no identical trades with other traders, no Telegram/WhatsApp-linked EAs, no latency abuse or order flooding); HFT prohibited** (verified)
  - "Each EA or bot is required to employ a distinct strategy, avoiding identical trades across other traders accounts within FundedNext." [P10]
  - "Automated trading systems and algorithms are monitored on FundedNext Futures Accounts." [P12]
- `sizing_or_gambling_terms` = **all-in / oversized flipping prohibited; excess contracts' profit deducted; Disciplined Trader Program (1% max risk, mandatory stop) imposed after warning for gambling-style behaviour** (verified)
  - "A trader qualifies for a FundedNext Account and immediately places an all-in trade, risking the entire account balance on one position." [P9]
  - "Maximum Risk at a Time: Must not exceed 1% of the account’s initial balance." [P11]
  - "Breaching multiple accounts within a short period" [P11]
  - note: 'Breaching multiple accounts within a short period' is listed as a trigger for the program: a design that runs several accounts with correlated losses could trip it.
- `other_conduct_bearing` = **tight/no-slippage bracket strategies prohibited; micro-scalping threshold (trades closed within 10 s, 40% of cycle profit); tick scalping and simulated-execution exploitation prohibited; account rolling monitored; positions closed by 3:10 PM CT** (verified)
  - "Exploiting the lack of slippage or using tight brackets to benefit from favorable trade executions is prohibited." [P9]
  - "Account rolling is a high-risk practice in which multiple Challenge Accounts are purchased with the intention of quickly progressing to FundedNext Accounts, often by intentionally sacrificing some accounts while focusing on passing others." [P9]
  - "Violations may result in restrictions on purchasing new accounts or adjustments to the lifetime allocation limit." [P9]
  - "Tick scalping is the repeated practice of opening and closing positions within a very short window to collect a few ticks of profit per trade from favourable simulated fills, often at large or maximum position size." [P9]
  - "All positions must be closed by 3:10 PM CT each trading day, and any open positions are closed automatically at that time." [P10]
  - note: The bracket prohibition's example is a two-sided buy-stop/sell-stop straddle on NQ with tight targets; a single-direction entry with its stop and target is not described as prohibited. 'Account sharing' is defined oddly as 'a trader manages multiple accounts or allows another individual to trade on their behalf' - read in context as other people's accounts, since 5 own funded accounts are allowed.
- `permitted_products` = **CME equity index futures NQ, MNQ, ES, MES, RTY, M2K (plus FX, metals, energy, ags, YM/MYM)** (verified)
  - "E-mini NASDAQ 100 (NQ), Micro E-mini NASDAQ 100 (MNQ), E-mini S&P 500 (ES), Micro E-mini S&P 500 (MES), E-mini Russell 2000 (RTY), Micro E-mini Russell 2000 (M2K)" [P22]

**Conflicts and changes** (reader's section)

- note: Rapid Pro 50K payout cap conflicts between pages: the Rapid Pro funded-rules article gives $1,000 (withdrawals 1-3) / $1,250 (4-5); the withdrawal how-to article says a maximum of 1,200 for 50K. Not the captured plan.
  - "Once you meet the 40% Consistency Rule and have $500 profit in the cycle, you can withdraw a maximum of 800(25K), 1,200(50K), or 2,500(100K)." [P3]
  - "| 1 to 3 | $250 | $1,000" [P23]
- note: Product changes: Bolt and the former Rapid ended for new purchases on 10 July 2026; Legacy ended for purchase on October 11 (2026). Flex is the current low-cost plan.

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

**Pages quoted** (key: URL; article id; the page's own date as shown; all read 2026-11-15)

- [P1] https://help.goatfundedfutures.com/plans.html; id plans; page date: Updated 14 November 2026
- [P2] https://help.goatfundedfutures.com/plans.html; id plans; page date: Updated 9 November 2026
- [P3] https://help.goatfundedfutures.com/billing.html; id billing
- [P4] https://help.goatfundedfutures.com/flex-challenge.html; id flex-challenge; page date: Updated 14 November 2026
- [P5] https://help.goatfundedfutures.com/payouts.html; id payouts#consistency; page date: Updated 8 September 2026
- [P6] https://help.goatfundedfutures.com/account-security.html; id account-security; page date: Updated 8 September 2026
- [P7] https://help.goatfundedfutures.com/account-security.html; id account-security
- [P8] https://help.goatfundedfutures.com/trading-rules.html; id trading-rules (bots and copy trading); page date: Updated 8 September 2026
- [P9] https://help.goatfundedfutures.com/trading-rules.html; id trading-rules (prohibited practices); page date: Updated 9 November 2026
- [P10] https://help.goatfundedfutures.com/trading-rules.html; id trading-rules (news); page date: Updated 8 September 2026
- [P11] https://help.goatfundedfutures.com/account-security.html; id account-security (VPS); page date: Updated 11 August 2026
- [P12] https://help.goatfundedfutures.com/path-to-live.html; id path-to-live; page date: Updated 9 October 2026
- [P13] https://help.goatfundedfutures.com/drawdown.html; id drawdown
- [P14] https://help.goatfundedfutures.com/payouts.html; id payouts#requirements; page date: Updated 8 September 2026
- [P15] https://help.goatfundedfutures.com/payouts.html; id payouts
- [P16] https://goatfundedfutures.com/
- [P17] https://help.goatfundedfutures.com/payouts.html; id payouts; page date: Updated 9 November 2026
- [P18] https://goatfundedfutures.com/terms-and-condition
- [P19] https://help.goatfundedfutures.com/account-security.html; id account-security; page date: Updated 29 June 2026


Official domains: goatfundedfutures.com, help.goatfundedfutures.com, app.goatfundedfutures.com. Read 2026-11-15.
Plan captured: Flex Challenge 50K (the only 50K plan with BOTH an EOD funded drawdown and no funded consistency; EOD Challenge and 1-Day-Pass pass the screen on the EOD leg but carry 30%/35% funded consistency, Daily Payouts passes on the no-consistency leg with an intraday funded drawdown).
Verdict: **PASS** -- Flex 50K: EOD trailing funded drawdown locking at start, no funded consistency percentage, up to 5 Flex funded accounts (copying own trades across them is the stated intended use); hand-entered bracket trading allowed, subject to the 1-minute 70%/70% holding test, funded 2-minute news buffer, no hedging, no overnight.

Unreadable (not worked around):
- https://goatfundedfutures.com/ (plan tabs other than GOAT DAILY) -- Framer site: only the default GOAT DAILY price cards are server-side; Flex/EOD/1-Day/Instant prices are rendered client-side and were not read. The help centre says 'For the current price and reset fee, see the pricing page or ask us in chat' (chat not used).

Plans seen:
- Flex Challenge 50K: drawdown EOD trailing $2,000 both phases, locks at starting balance; consistency evaluation 50%, funded none
  - "A premium one-phase evaluation with End of Day Trailing drawdown, no consistency rule on funded accounts, and maximum flexibility." [P1]
- EOD Challenge 50K: drawdown EOD trailing $2,000 both phases, locks at starting balance; consistency evaluation 50%, funded 30%
  - "| Consistency, funded | 30% | 35% | 20% | None | None" [P2]
- 1-Day-Pass-Plan 50K: drawdown EOD trailing $2,000, locks at starting balance; 2% DLL both phases (soft pause funded); consistency evaluation none, funded 35%
  - "| Consistency, evaluation | 50% | None | N/A | 50% | 40%" [P2]
- Daily Payouts (GOAT DAILY) 50K: drawdown evaluation EOD trailing; funded INTRADAY trailing on highest equity, locks at start + $100; $1,000 DLL, 3 hits in 30 days closes; consistency evaluation 40%, funded none; manual trading only
  - "| Drawdown type, funded | Trailing EOD | Trailing EOD | Trailing intraday | Trailing EOD | Trailing intraday" [P2]
- Instant Classic 50K (no evaluation): drawdown intraday trailing on highest equity $2,500, locks at starting balance; consistency evaluation n/a, funded 20%; max 3 funded
  - "- Drawdown Type: Intraday Trailing on Highest Equity (locks at starting balance)" [P1]
- Instant Lite 50K (no evaluation, payout target): drawdown EOD trailing, locks at start + $100; daily profit capped at 5% of balance; no resets; consistency evaluation n/a, funded 15% -> 20% -> 25% as payouts complete; manual trading only
  - "- A consistency threshold that widens as you complete payouts, from 15% to 20% to 25%" [P2]
- GOAT Access: drawdown not screened (only mentioned in billing and holding-time articles; no specifications page read); consistency evaluation not read, funded not read
  - "Only on GOAT Access. GOAT Access has a one-time $99 activation fee, paid after you pass the evaluation, before your funded account is issued." [P3]

**Screen**

- `drawdown_eval` = **eod_trailing ($2,000), locks at starting balance** (verified)
  - "It trails up with your profits at the end of each trading day, and stops trailing once it reaches your starting balance. That lock applies in both the evaluation and funded phases." [P4]
- `drawdown_funded` = **eod_trailing ($2,000), locks at starting balance ($50,000)** (verified)
  - "| Drawdown, funded | Intraday trailing | End of day trailing" [P1]
  - "End of day trailing max drawdown, which locks once it reaches your starting balance" [P4]
  - note: First quote's columns: Daily Payouts 50K | Flex 50K.
- `consistency_eval` = **50%; over it you cannot complete the evaluation until the best day falls back to 50% or below** (verified)
  - "During the evaluation, no single day may account for more than 50% of your total profit." [P4]
- `consistency_funded` = **none (no percentage), subject to anti-gaming review** (verified)
  - "On a funded account there is no consistency percentage." [P4]
  - "Having no funded consistency percentage does not override prohibited-strategy or anti-gaming rules." [P5]
  - note: Anti-gaming: loading nearly all profit into one day then placing minimum trades to tick off winning days may get the payout withheld and the big day voided.
- `max_funded_accounts` = **5 Flex funded (each product type has its own limit; Flex 5 + Daily 5 + EOD 5 + 1-Day 5 + Instant Classic 3 can be held together); evaluations unlimited; one registered email/login per person** (verified)
  - "EOD Challenge, 1-Day-Pass-Plan, Flex Challenge and Daily Payouts: up to 5 funded accounts each" [P6]
  - "The limits are counted separately for each product type, so they do not compete with each other." [P6]
  - "There is no limit on the number of evaluation accounts you may purchase." [P6]
  - "You can register only one email address with Goat Funded Futures." [P7]
  - note: Household rule: not stated (IP-region consistency and no device/IP sharing for linked trading are).
- `copy_trading` = **allowed across own accounts (and to own accounts elsewhere); copying other people prohibited** (verified)
  - "You may copy your own trades across your own GFF accounts, and across accounts you hold elsewhere. If you buy a multi account bundle, copying your own trades into each of them is the intended use." [P8]
- `opposite_positions` = **prohibited across accounts (and cross-firm hedging targeted by the anti-gaming rule)** (verified)
  - "holding opposing or hedged positions across accounts" [P9]
  - "It also closely mirrors external and cross account hedging, where one leg of a position is offset on a separate account or at another firm, so the losing side is sacrificed and the winning side is withdrawn here as profit." [P4]
- `news` = **Flex evaluation: unrestricted; funded: cannot open, close or trigger pending orders from 2 min before to 2 min after scheduled high-impact news (positions opened before the window may be held through)** (verified)
  - "Funded: a 2 minute buffer applies around high impact news events. You cannot open, close, or trigger pending orders within 2 minutes before or after a scheduled release. Positions opened before the window began may be held through the event." [P4]
  - "If you execute an order within the restricted timeframe, any profits generated will be deducted upon payout request." [P10]
  - note: A bracket whose stop or target would trigger inside the window violates 'trigger pending orders'; the prohibited-practices tab (9 Nov) says only 'you may not open a new position' and that 'managing or closing' an existing one is fine -- internal inconsistency.
- `automation` = **own automated strategies/EAs allowed on Flex (not exploiting latency/feeds); BUT VPS/remote servers prohibited and the VPS article states a requirement that you personally place and manage your trades** (verified)
  - "On EOD, 1-Day-Pass-Plan, Flex and Instant Classic, your own automated strategies and EAs are allowed, as long as they reflect your own trading and do not exploit latency, data feed anomalies or system vulnerabilities." [P8]
  - "Automation abuse. VPS environments are commonly used to run unattended automated systems 24/7, which conflicts with our requirement that you personally place and manage your trades." [P11]
  - note: Hand entry is consistent with all of it. Daily Payouts and Instant Lite are manual-only.
- `sizing_gambling` = **all-in bets, account rolling and erratic size swings may be treated as gambling; 1 minute holding rule (70% of closed trades and 70% of net profit from trades held > 1 minute, checked at pass and each payout); tick scalping prohibited; 100+ trades a day may trigger review** (verified)
  - "Disproportionate all-in bets on a single position, account rolling, and erratic sizing swings (one micro on one trade, five minis on the next) may be treated as gambling rather than disciplined trading." [P9]
  - "at least 70% of your closed trades were held longer than 1 minute, and" [P4]
  - "at least 70% of your net profit came from trades held longer than 1 minute." [P4]
  - "HFT systems, tick scalping, bulk order-entry, and volume inflation are prohibited, and 100+ trades in a single day may trigger a risk review." [P9]
  - note: The 1-minute rule bears directly on bracket trading: a bracket that hits its target or stop within 60 s counts as a sub-minute trade; failing the 70%/70% test declines the payout and deducts sub-minute profit (not a breach). Rule changed 9 November 2026 (was a 2-minute per-trade deduction; Flex threshold raised from 50% to 70%).

**Terms (`terms`)**

- `eval_profit_target` = **3000** (verified)
  - "| Profit Target | $3,000 (6%) | $6,000 (6%) | $9,000 (6%)" [P4]
- `eval_drawdown_amount` = **2000** (verified)
  - "| 50K | $2,000 (4%)" [P4]
- `eval_drawdown_type` = **eod_trailing** (verified)
  - "Maximum drawdown (end of day trailing)" [P4]
- `eval_drawdown_lock` = **locks at starting balance** (verified)
  - "That lock applies in both the evaluation and funded phases." [P4]
- `eval_daily_loss_limit` = **none by default; optional $1,000 at checkout for a lower price (hard breach, both phases, cannot be changed later)** (verified)
  - "None by default. A Flex account has no daily loss limit in the evaluation phase or on the funded account." [P4]
  - "The limit is $1,000 on a 50K, $1,500 on a 100K and $2,500 on a 150K. It applies in both phases, and hitting it is a hard breach that closes the account." [P4]
- `eval_consistency_rule` = **50% of total profit from any single day; gates completion (not a breach)** (verified)
  - "If you go over, you cannot complete the evaluation until your best day falls back to 50% or below." [P4]
- `eval_min_days` = **none** (verified)
  - "There is no minimum number of trading days." [P4]
  - note: With the 50% consistency rule, passing needs at least 2 trading days in practice.
- `eval_position_limit` = **3 minis / 30 micros** (verified)
  - "| 50K | 3 mini / 30 micro" [P4]
- `eval_fee` = **one-time fee (no subscription); Flex 50K price UNVERIFIED (client-side pricing; the 90/10 add-on is +20% of the challenge price)** (UNVERIFIED)
  - "All six are a one-time fee. There is no monthly subscription on any GFF product." [P2]
  - "Prices change with our promotions. For the current price and reset fee, see the pricing page or ask us in chat." [P1]
  - looked at: https://goatfundedfutures.com/ (only GOAT DAILY cards server-side: 50K $238 list / $107 with GFF55), sitemap (no Flex/pricing page), help plans/flex-challenge/billing
  - note: For reference only, the homepage advertises '50K EOD Plan from $69' (EOD Challenge, not Flex).
- `eval_reset_fee` = **two discounted resets per challenge; amount UNVERIFIED** (UNVERIFIED)
  - "Two resets are available per challenge." [P4]
  - looked at: help manage-account, flex-challenge, plans; homepage
- `activation_fee` = **0** (verified)
  - "| Activation Fee | $0 | $0 | $0" [P4]
- `eval_count_limit` = **unlimited** (verified)
  - "There is no limit on the number of evaluation accounts you may purchase." [P6]
- `eval_time_limit` = **none (but 14-day inactivity breach)** (verified)
  - "| Time Limit | None | None | None" [P4]
- `funded_type` = **sim funded; Live by risk-team review only (no public threshold); on approval ALL sim accounts with >= 1 approved payout are combined into one live account (sizes summed, capped at 150K), unwithdrawn sim profit does not carry over, and it cannot be declined** (verified)
  - "There is no public payout count, dollar target, or numeric milestone that "unlocks" a live account." [P12]
  - "Your live account size is determined by summing your eligible sim account sizes, capped at 150K — GFF's largest live tier." [P12]
  - "Transitioning is the whole point of the Path to Live, so once you are approved it is not something you opt out of." [P12]
  - "Any sim account that has not taken a payout yet is simply closed and its account fee refunded to you." [P12]
  - note: Bears on a multi-account design: a live call collapses the whole book (e.g. 3x50K -> one 150K live, $4,500 drawdown).
- `funded_drawdown_amount` = **2000** (verified)
  - "| 50K | $2,000 (4%)" [P4]
- `funded_drawdown_type` = **eod_trailing** (verified)
  - "Your maximum drawdown is the level your balance or equity cannot fall below." [P4]
  - note: 'balance or equity': intraday equity below the EOD-set floor breaches (hard breach).
- `funded_drawdown_lock` = **locks at starting balance ($50,000; no +$100)** (verified)
  - "EOD, 1-Day-Pass-Plan, Flex and Instant Classic all lock at the starting balance, with no $100 added." [P13]
- `payout_balance_consequence` = **payout does not move or lock the floor; max request 50% of total profit (cap $2,000), the other 50% stays as buffer** (verified)
  - "Requesting or receiving a payout does not automatically move or lock your drawdown at the starting balance. Your drawdown remains wherever it was before the payout." [P13]
  - "The remaining 50% stays in the account and supports your equity into the next payout cycle." [P4]
- `funded_daily_loss_limit` = **none by default (optional $1,000 hard-breach DLL if chosen at checkout)** (verified)
  - "None by default. A Flex account has no daily loss limit in the evaluation phase or on the funded account." [P4]
- `funded_consistency_rule` = **none** (verified)
  - "On a funded account there is no consistency percentage." [P4]
- `funded_position_limit` = **scaling by simulated profit (from 10 Nov 2026): $0-$999: 2 mini/20 micro; $1,000-$1,999: 3/30; $2,000+: 4/40 (top)** (verified)
  - "| Simulated profit | 50K | 100K | 150K" [P4]
  - "| $0 to $999 | 2 mini / 20 micro | 3 mini / 30 micro | 4 mini / 40 micro" [P4]
  - "| $1,000 to $1,999 | 3 mini / 30 micro | 4 mini / 40 micro | 5 mini / 50 micro" [P4]
  - "| $2,000 to $2,999 | 4 mini / 40 micro | 5 mini / 50 micro | 6 mini / 60 micro" [P4]
  - note: New rule effective 10 November 2026 for every funded Flex account.
- `funded_monthly_fee` = **none** (verified)
  - "Unlike many other futures prop firms, we do not charge monthly subscriptions." [P3]
- `payout_min` = **500** (verified)
  - "Minimum request: $500. There is no profit buffer to build up first, so any amount above $500 qualifies." [P4]
- `payout_cap` = **per cycle: 50% of total account profit, up to $2,000 (measured before split); lifetime cap not stated** (verified)
  - "| $50,000 | 50% of Profit up to $2,000" [P4]
  - note: Lifetime cap: UNVERIFIED (none stated).
- `payout_frequency_gate` = **5 winning days (>= $250 net each) per cycle; requests only in windows 5th-8th and 20th-23rd of each month; from the 2nd payout at least 50% of the request must be new profit since last payout (accounts created after 7 Aug 2026); 1-minute holding test at each request** (verified)
  - "Request window: payout requests are submitted through your dashboard between the 5th and 8th, or the 20th and 23rd, of each month." [P4]
  - "Flex 50K: 0.5% — $250" [P4]
  - "At least 50% of the amount you request must come from new profit generated since your previous approved payout." [P14]
  - note: Winning days need not be consecutive; counter resets to zero after each approved payout.
- `payout_split` = **80/20 default; 90/10 with an add-on costing 20% of the challenge price** (verified)
  - "80/20 by default. You can add the optional 90/10 Profit Share Add-On for an extra 20% of the challenge price." [P4]
- `payout_processing_days` = **within two business days (homepage: or an extra $500)** (verified)
  - "GFF processes payout requests within two business days after the request is submitted." [P15]
  - "Rewards in 2 Days or Extra $500" [P16]
- `payout_fee` = **3% of every payout (Rise or crypto)** (verified)
  - "A 3% fee is applied to all payouts to cover payment processing and transaction costs." [P17]
  - note: Crypto payouts capped at $1,800 per cycle across all accounts; the rest via Rise.
- `payout_count_limit` = **UNVERIFIED (none stated for Flex)** (UNVERIFIED)
  - looked at: help flex-challenge, payouts, plans, path-to-live
- `max_accounts` = **5 Flex funded (separate allowance per product type); evaluations unlimited** (verified)
  - "You can hold up to 5 funded accounts." [P4]
- `inactivity_rule` = **no trade for 14 consecutive days -> breached and closed, fee not refunded (from 7 November 2026)** (verified)
  - "Place at least one trade every 14 days. If no trades are placed for 14 consecutive days the account is breached and closed, and the fee is not refunded. This 14-day rule applies from 7 November 2026." [P4]
- `copy_trading_terms` = **own accounts: allowed (incl. TradeSea SecureCopy); others' signals/trades: prohibited, linked accounts may all be suspended** (verified)
  - "You can buy 5 accounts for a discounted bundle price on our checkout, and then you can indeed copy trades into all 5 accounts." [P7]
  - "Trading someone else's calls, whether from a signal provider, a trading group, a third party service, a copy or mirror service, or an EA that follows an external source, is a prohibited trading practice and may result in account termination." [P8]
- `cross_account_hedging` = **prohibited** (verified)
  - "No arbitrage of any kind — latency, hedge, reverse, or rollover." [P9]
- `news_trading_terms` = **evaluation free; funded 2-minute buffer (no open/close/trigger), profits inside window deducted at payout; gap trading around closures/earnings prohibited** (verified)
  - "This applies to all funded account types: EOD, 1-Day-Pass-Plan, Flex, Instant Classic and Daily Payouts." [P10]
- `automation_terms` = **own EAs allowed on Flex; VPS/cloud/remote desktop prohibited on all accounts** (verified)
  - "No. The use of Virtual Private Servers (VPS), cloud-hosted machines, or any form of remote server to access or trade your GFF account is strictly prohibited — on both evaluation and funded accounts, with no exceptions." [P11]
- `sizing_or_gambling_terms` = **no all-in bets / erratic sizing; Terms: 'market standard risk management' not met by substantially larger positions than your other trades** (verified)
  - "Keep your sizing consistent with your strategy and balance." [P9]
  - "You acknowledge that these standards are not met where you open substantially (i) larger position sizes compared to your other trades, or (ii) smaller or larger number of positions compared to your other trades." [P18]
- `other_conduct_bearing` = **1-minute holding rule (70%/70%); no overnight/weekend, auto-flatten 15:55 CT; IP region must stay consistent (VPN may flag); payout-requirement gaming (one big day + token days) voidable** (verified)
  - "If either is not met, the payout request is declined and all profit from trades held under 1 minute in that cycle is deducted from the account. This is not an account breach, and your account stays open." [P4]
  - "Overnight holding is not permitted. Any position still open is closed automatically at 15:55 CT, five minutes before the session ends." [P4]
  - "Once funded, the IP region you use to access the account needs to stay consistent." [P19]
- `permitted_products` = **CME, CBOT, COMEX, NYMEX futures; NQ and MNQ listed** (verified)
  - "GOAT Funded Futures gives you access to trade across all major futures exchanges and a wide range of instruments." [P16]
  - "E-Mini Nasdaq 100 Futures" [P16]
  - "Micro Nasdaq 100 Futures" [P16]
  - note: Homepage instrument list: NQ tick $5, per-side fee $2.88; MNQ tick $0.50.

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

**Pages quoted** (key: URL; article id; the page's own date as shown; all read 2026-11-15)

- [P1] https://thefuturesdesk.com/
- [P2] https://thefuturesdesk.com/terms-conditions; page date: Effective date: Apr 1, 2026


Official domains: thefuturesdesk.com. Read 2026-11-15.
Plan captured: None.
Verdict: **FAIL** -- At most 2 accounts per trader (homepage FAQ): not 'several' funded accounts.

Unreadable (not worked around):
- https://thefuturesdesk.com/knowledge-base -- JavaScript-rendered (static HTML shows only 'Loading knowledge base...'); not read further. WebFetch not tried: the verdict is already fixed by the homepage account cap, and the site's Terms forbid crawling (see note in screen.automation).

Plans seen:
- Assessment Desk / Intern Desk (custom 'loadout'; account sizes and prices not on the static pages): drawdown 'Static or EOD' (stage not specified); consistency evaluation UNVERIFIED, funded none
  - "No consistency or minimum days between payouts (Mon-Fri)" [P1]

**Screen**

- `drawdown_eval` = **static or EOD (stage not specified)** (verified)
  - "Static or EOD" [P1]
  - note: Homepage comparison table only; which mode applies to the assessment vs funded is in the unreadable knowledge base.
- `drawdown_funded` = **UNVERIFIED per stage (homepage: 'Static or EOD')** (UNVERIFIED)
  - looked at: https://thefuturesdesk.com/, https://thefuturesdesk.com/terms-conditions (knowledge base unreadable)
  - note: Funded accounts are live brokerage accounts after a short sim-brokerage period.
- `consistency_eval` = **not stated** (UNVERIFIED)
  - looked at: https://thefuturesdesk.com/, https://thefuturesdesk.com/terms-conditions
- `consistency_funded` = **none** (verified)
  - "Once you are funded with us, we have no payout caps, no consistency, no minimum days — what a modern proprietary trading company should have." [P1]
- `max_funded_accounts` = **2 accounts per trader** (verified)
  - "You can have a max of 2 accounts per trader." [P1]
  - note: Not stated whether the 2 include assessments.
- `copy_trading` = **own-account copying not addressed; coordinated same/opposite strategies across accounts to pool or hedge risk prohibited** (UNVERIFIED)
  - "Coordinated Trading - Coordinating with others, including between unconnected accounts and third parties, to perform the same trading strategy, opposite strategy, or other activities intended to pool or hedge risk across multiple accounts." [P2]
  - looked at: home, terms-conditions
- `opposite_positions` = **prohibited** (verified)
  - "This includes engaging in short-term or high-frequency trading or simultaneously entering opposite positions." [P2]
  - note: Part of 'Market Manipulation', including between connected accounts.
- `news` = **not stated** (UNVERIFIED)
  - looked at: home, terms-conditions
- `automation` = **homepage: 'Microscalping + Algos Allowed'; Terms prohibit automated tools that manipulate or give an unfair advantage** (verified)
  - "Microscalping + Algos Allowed" [P1]
  - "Automated Trading - Using any software, artificial intelligence, ultra-high-speed, or mass data entry tools that could manipulate, abuse, or provide an unfair advantage while using the Site or Services." [P2]
  - "Using manual or automated software, devices, or processes to "crawl" or "spider" any web pages within the Sites or Services." [P2]
  - note: The third quote is the site's ban on crawling (applies to visitors too); only 3 pages were fetched, then reading stopped.
- `sizing_gambling` = **position sizes far from usual patterns, and excessive contracts per day, are prohibited conduct** (verified)
  - "You agree to consistently apply market standard risk management rules while using the Sites and Services, and understand that opening significantly larger or smaller position sizes compared to your usual trading patterns does not meet these standards." [P2]
  - "Excessive Trading - Trading an excessive or unrealistic number of contracts within a single day." [P2]
  - note: Also: flat by 3:10 PM CT unless Swing Trading is enabled; VPN/VPS use forbidden.

**Other notes** (reader's section)

- `funded_is_live` = **funded = live brokerage account after a short sim-brokerage period** (verified)
  - "After that, yes, all traders move to one of our fully regulated live brokerage accounts where all capital is real." [P1]
  - "an affiliate of TS TFD Buyer, LLC" [P1]
  - note: The Futures Desk is a Topstep affiliate (Topstep Brokerage LLC is named as an affiliate of TS TFD Buyer, LLC).
