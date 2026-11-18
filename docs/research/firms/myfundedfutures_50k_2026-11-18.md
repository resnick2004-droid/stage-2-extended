# My Funded Futures, $50K accounts: every plan's evaluation and funded terms (Q-135d, E-196)

**The question.** For every account type My Funded Futures (MFFU) sells at $50K today, what are the current
evaluation and funded-account terms? Which of them can Stage 2's engine represent against the Topstep $50K reference
(`prereg/RD-01_firm_contracts.md` section 4.1)? And do the rules allow passing in one or two big days ("flip days"),
in the evaluation and up to the funded account's first payout?

**The answer.**
- **Plans on sale at $50K.** There are four plan families, each a one-step evaluation followed by a sim-funded
  account. Two of them have paid variants, so there are seven products: Rapid 50K; Rapid EOD 50K, with or without a
  daily-loss-limit (DLL) variant; Pro 50K, with or without the "One Day" variant; and Builder 50K, with a $2,000 or
  $1,500 drawdown. There is no instant- or direct-funded product. "Core" and "Scale" survive only as dead links in a
  2025 live-account FAQ. Flex 50K sits in the help centre's "Legacy Plans" collection and is not in the site's product
  data. Studio plans come only at $5K, $10K and $20K. Perps is a separate company's product.
- **Every evaluation shares a core.** All seven have a $3,000 target, except Pro One Day at $4,000. All have a $2,000
  end-of-day trailing drawdown, except the Builder add-on at $1,500. Open-equity losses breach it intraday, and it
  locks at $50,100. Every evaluation is a one-time fee, with no activation fee and no renewal. A reset costs the
  purchase price; that figure comes from the site's product data, not from words. The evaluations differ in four
  ways: consistency (30 %, 50 % or none), minimum days (4, 2 or 1), contract cap (3, 4 or 5 minis) and DLL.
- **The funded accounts differ more than the evaluations.**
  - **Rapid EOD:** end-of-day trailing floor locking at +$100; daily payouts above a $2,100 buffer; 90/10 split; no
    cap; no consistency rule.
  - **Rapid:** the same payouts, but the floor trails *intraday on equity including unrealised gains*.
  - **Pro:** first payout 14 calendar days from the first trade; $1,000 minimum; 80/20 split; $100,000 lifetime cap
    per user; the floor moves to $50,100 at the first payout; "3 mini / 3 micro" allowance; a discretionary
    "Consistent Trading Policy".
  - **Builder:** one account per user; per-cycle 50 % consistency and 2 trading days; at most $2,000 a request; at
    most five sim payouts, then a move to live.
- **Flip days.**
  - **Evaluation:** a one-day pass is allowed on Builder (no consistency, 1 day minimum) and Pro One Day ($4,000, no
    consistency). A two-day pass is allowed on Rapid and Pro: 50 % consistency and a 2-day minimum, so two days of
    about $1,500 each. Rapid EOD needs at least four days: 30 % consistency and a 4-day minimum.
  - **First payout:** a one-day path is allowed on Rapid EOD and Rapid. A day that clears the $2,100 buffer plus the
    $500 minimum can be followed by a request 24 hours after the first trade. A single day of $10,000 net moves the
    account to Live automatically, and the excess that day is forfeited. Builder needs at least two trading days and a
    50 % best-day share. Pro allows a big day, but no payout comes before 14 calendar days.
- **Engine fit.**
  - **Expressible as fields:** Rapid EOD and Builder fit the engine's evaluation (`CombineAccount`) almost entirely,
    and Builder's per-cycle rule is the engine's own consistency path (`payout_path` "consistency").
  - **New adapters or gaps:** the buffer gate with a balance kept back, Rapid's intraday equity trail (Stage 2's known
    hard mechanic), Pro's 14-calendar-day clock and 1:1 micro counting, Builder's fifth-payout end and single seat, the
    7-day inactivity closure, the live moves and the funded Tier-1 news blackout.
- **Terms of Use and automated retrieval.** No clause forbids automated access, scraping, robots or data mining
  (section 0).

**Read date and method.** Every page below was read on **2026-11-18 UTC**, from 03:57 to 04:04 UTC; the machine's
local date was 2026-11-17. Each page was fetched with one plain `curl` GET, with no cookies, login, form or account,
nothing sent, and about one request per second. The text was extracted locally. Quotes are verbatim from the
extracted page text. The raw captures are in this session's scratchpad (`q135d/raw/`, with an `INDEX.tsv` of URL,
time and HTTP code) and are not committed. "Plan data" means the product records the site embeds in its own pages
(e.g. `"priceCents":27500`). These are the firm's official pages, but they are machine fields, not statements; every
place a plan-data field carries a term is labelled.

**Source keys.** `H<id>` is `https://help.myfundedfutures.com/en/articles/<id>-...` (Intercom help centre; the page
date printed on the article is given at first use). `P:<plan>` is `https://myfundedfutures.com/plans/<plan>`.
`HOME` is `https://myfundedfutures.com/`. `T s.<n>` is the General Terms and Conditions at
`https://myfundedfutures.com/terms` (no version date printed). `D:<id>` is a home-page plan-data product record (HOME's
embedded data; product ids 71, 93, 251, 135, 138, 84 and 85 are the seven $50K products). The full URL list is in
section 14.

---

## 0. The Terms of Use and automated retrieval (the lead's first question)

- **No clause in the General Terms forbids automated access, scraping, crawling, spidering, robots, bots or data
  mining.** The full text was searched for automat, scrap, robot, bot, spider, crawl, data min, harvest and extract.
  The only hit on "automat" is about the firm's own processing (T s.12.5) and the definition of a one-time plan
  (T s.2).
- The closest clauses govern use and republication of content, not the method of access:
  - T s.22.2: "You are granted a personal, nonexclusive, nontransferable, nonsublicensable, nonassignable, limited, and
    revocable right to access, use, display, and navigate our Sites and Services solely for your personal,
    non-commercial, and non-public use. You shall not reproduce, distribute, modify, create derivative works of,
    publicly display, publicly perform, republish, download, store, or transmit any of our Content, except for your
    personal, non-commercial, and non-public use. You shall not access or use for any commercial purposes any part of
    the Company Products and Content."
  - T s.22.6: "no portion of the Company Products and Content or any Content may be reproduced, altered, removed,
    transmitted, published, or distributed, whether electronically, mechanically, by photocopy, recording, or
    otherwise, without the prior written permission of the Company."
  - T s.23.1.5: "Interfering with, damaging, or disrupting the Sites, Services, or any third-party services;
    Circumventing security features, authentication, or monitoring mechanisms."
  - T s.23.1.8: "Using the Services for commercial purposes without prior written consent."
- **robots.txt.** `myfundedfutures.com/robots.txt` is `User-agent: *` / `Disallow:` (nothing disallowed).
  `help.myfundedfutures.com/robots.txt` disallows only `/not-authorized`, `/not-found`, `/[helpCenterIdentifier]/` and
  `/*=`, with `Crawl-delay: 1`. No page read here is disallowed, and the fetches kept about one second apart.
- **Order of fetching, stated plainly.** The Terms page was fetched after other pages, in the batch with the four
  plan pages. Before it, these had been fetched: HOME, the help-centre home, `/plans`, twelve help-centre collections
  and 37 help articles. The lead's instruction to check the Terms first arrived mid-run. Nothing in the Terms bars
  what had been done, so the reading continued under E-020 (1)'s reading.
- **For the lead (not a retrieval bar).** s.22.2 confines downloading and storing Content to "personal,
  non-commercial, and non-public use". This note quotes short passages in a private research repository; the raw
  captures stay in the scratchpad and are not committed. Whether a private quant project is "personal,
  non-commercial" use is the lead's call. It is recorded here, not decided.

## 1. Plans at $50K

| product (plan-data name, id) | on sale? | list price, one-time | evidence (read 2026-11-18) |
|---|---|---|---|
| Rapid 50K (intraday-trailing funded) | yes | $209 | D:71 `"price": 209`, `"active": true`; P:rapid JSON-LD `"name":"My Funded Futures Rapid Plan 50,000 Account"`, `"price":"209.00"` |
| Rapid EOD 50K, default (no DLL) | yes | $275 | D:93 `"price": 275`; P:rapid-eod `"priceCents":27500` |
| Rapid EOD 50K DLL (variant of 93) | yes | $200 | D:251 `"name": "Rapid EOD 50K DLL"`, `"price": 200`, `"add_on_of": 93`; H18337038 ("Updated this week") |
| Pro 50K | yes | $265 | D:135 `"price": 265`; P:pro `"priceCents":26500` |
| Pro 50K 1 Day (variant of 135) | yes (product `"active": true`) | $379 | D:138 `"name": "Pro 50K 1 Day"`, `"price": 379`, `"add_on_of": 135`; H17573707 column "Pro 50k - One Day" |
| Builder 50K, $2,000 MLL ("Builder 2.0K") | yes | $153 | D:84 `"price": 153`; H14290805 price table "$153" |
| Builder 50K, $1,500 MLL add-on ("Builder 1.5K") | yes | $125 | D:85 `"price": 125`, `"add_on_of": 84`; H14290805 "$125" |
| Flex 50K | **no** (legacy) | -- | in the "Legacy Plans" collection (H15072271 is listed there); not among HOME's 20 product records |
| Studio #001/#002/#003 | not at $50K | -- | H17589665: "$10,000 | $20,000 | $5,000" account sizes |
| instant / direct funded | **none found** | -- | `/plans` lists Rapid, Rapid EOD, Builder and Pro only; HOME's 20 product records are those plans plus Studio |
| "Core", "Scale" | no | -- | only as links in H12109396 (page date November 10, 2025) to `11802648-core-plan-...` and `11802669-scale-plan-...`; neither is in any current collection |
| Perps | out of scope | -- | `/plans` and HOME header: "Perps New24/7 perps trading"; HOME footer: "MyFunded Perpetuals is offered by Funding Perpetuals Holdings, Inc., a company separate from MyFunded Futures, LLC." |

- **Promotions on 2026-11-18.** The banner reads "Save 40% On Any Plan With Code CLUB." and "New to MFFU? Get 50% off
  your first eval.". The plan data carries `"code": "fiftyoff"` (50 %) on six of the seven $50K products and
  `"code": "fortyoff"` (40 %) on Pro 50K 1 Day. The plan pages carry `"couponCode":"CLUB"` with discounted prices of
  $125.40 (Rapid), $165 (Rapid EOD), $159 (Pro) and $91.80 (Builder) (`priceDiscountedCents`). H14290805 shows
  Builder "Discounted Price (40% OFF - 2 uses only) | $92 | $75".
- **The pricing model.** HOME: "One-time payment. No activation fee. No renewals." T s.6.1.1: "Payment is due in full
  at the time of purchase. No further charges will be made in connection with that purchase."

## 2. Firm-wide terms (every plan unless the plan's table says otherwise)

| term | MFFU's term, verbatim where it matters | source (read 2026-11-18) |
|---|---|---|
| activation fee | "all MFFU plans, regardless of account size, come with $0 activation fee." | H12398151 (August 25, 2026) |
| billing | one-time for purchases from the cut-over; legacy subscriptions renew every 30 days. **Conflicting cut-over date:** T says "purchased a subscription-based plan prior to August 20, 2026"; the help centre says "Effective August 25, 2026" | T s.6.1, s.6.1.2, s.6.1.2.5; H16596406 (September 24, 2026) |
| reset | "An account reset is a manual action you take to restore your trading account to its original state, whether it's breached or not." "Resets will continue to work the same way for all accounts, regardless of purchase date." Price: no words; plan data gives `"reset_price"` equal to `"price"` for all seven $50K products (e.g. D:93 `"reset_price": 275`) | H16596406; D:71/93/251/135/138/84/85 |
| reset of a funded account | not possible: "Funded accounts can't be reset, so you'll need to start a new evaluation." | P:rapid FAQ; plan data `"sim_funded_resets": false` on all seven |
| data / platform fees (evaluation and sim funded) | none stated; T s.6.1.1 "No further charges will be made in connection with that purchase." Live accounts pay their own: "CME Professional Data Subscription", "Round-Trip Commissions and Fees", "Platform License or Subscription", "deducted directly from your Live Funded Account balance" | T s.6.1.1; H10101257 (August 24, 2026) |
| commissions in sim P&L | instrument table, column "Total Cost Round Trip": NQ "$4.68", MNQ "$1.90" | H9735811 (no page date printed) |
| products | "standardized futures contracts listed on regulated U.S. exchanges, including those operated by CME Group (CME, CBOT, NYMEX, and COMEX)"; NQ and MNQ listed | every plan page's footer; H9735811 |
| hours, overnight | "Trades may be placed beginning at 6:00 PM EST when the Globex session opens and can remain open until the New York session closes at 4:10 PM EST." "any open positions will be automatically closed at 4:10 PM EST on regular (non-holiday) trading days." Rapid: "Holding overnight will breach the account." Builder: "All positions must be closed before the end of the trading session." Holidays: "auto-liquidation will not occur at the half-time market close ... Failure to close the positions before the market closes will result in breaching of the account" | H9558251 (August 24, 2026); P:rapid FAQ; H14290805 FAQ |
| weekend | no separate rule; the daily flat requirement covers it | as above |
| inactivity | "If a trader does not place a trade for 7 consecutive calendar days, the account could be closed. This includes simulated funded accounts." "An inactivity breach on a Sim Funded account results in the forfeiture of all profits." T s.7: "the Company may, in its sole discretion, deem the applicable account dormant, close it, and treat such closure as a breach" | H16596524 ("Updated over a week ago"); T s.7 |
| time limit | none stated in words. Plan data has `"access_days": 365` on every $50K product and `"max_trading_days": null` | D:* (field only) |
| evaluation drawdown lock | "the Max EOD trailing locks in at $100 plus the initial starting balance" (example: "50k is 52k +$100 which is 52.1k"). Plan data: `"max_drawdown_limit": 50100` on all seven | H8348565 (August 24, 2026; in the "Traders Evaluation" collection); D:* |
| intraday breach of the end-of-day floor | "open equity losses are taken into consideration when calculating whether or not the account failed on this rule. This means that if an open position dips your account balance below the minimum account balance, your evaluation attempt will fail" | H8348565 |
| evaluation-to-funded move | the upgrade is instant from the dashboard once the target and requirements are met: "you can now upgrade your Evaluation Account to a Sim Funded Account instantly—and start trading the very same trading day." Some accounts may "undergo a brief review (typically in less than 24 hours)" | H13523548 (August 24, 2026); H16498635 (September 4, 2026) |
| account limits per person | "Traders may hold a maximum of 10 active Evaluation Accounts at any given time." "Traders may maintain up to 5 active Sim-Funded Accounts when holding only $25K and/or $50K account sizes." Plan-specific: "Rapid EOD $50K: Maximum of 3 Sim-Funded Accounts", "Builder $50K: Maximum of 1 Sim-Funded Accounts". With any $100K/$150K account: 3 in all. T s.23.1.3: "all such accounts must belong to the same verified individual." | H16498635; H11802636 (September 24, 2026); T s.23.1.3 |
| household / devices | no household rule as such; "Each individual trader may not use the same device (tablet, phone or computer) as used by another trader." "The use of shared devices is strictly forbidden and may result in a breach and/or account failure. E.g.: using the same PC or Phone as your partner" | H8444599 ("Updated over 2 weeks ago"); H8230018 (August 24, 2026) |
| hedging | "MyFundedFutures prohibits hedging of any kind. Hedging is defined as a trader entering both buy and sell positions on the same underlying asset, at the same time." "E-Mini and Micro NQ have the same underlying asset which is NQ (Nasdaq)." "hedging through different unrelated assets is permitted". T s.23.1.3.3: no using "multiple accounts to hedge, mirror, copy, or coordinate trades in a manner that provides an unfair advantage or manipulates simulated results" | H12011241 (November 10, 2025); H8444599; T s.23.1.3.3 |
| copy trading (own accounts) | "MyFunded Futures allows copy trading across all account types." (Tradesyncer preferred; the Tradovate group copier allowed). Qualified by T s.23.1.3.3 above; T s.1.6 says the Terms prevail over incorporated documents in a conflict | H10771500 (August 24, 2026); T s.1.6 |
| copy trading (other traders) | "Traders are not permitted to copy trade one another by entering, exiting or cancelling trade positions." "Collaborating with others to execute identical or opposite strategies across unconnected accounts is prohibited." | H8444599 |
| automation | "High-frequency Trading is not allowed on our plans." "Traders may make use of automated trading strategies tailored to their own specific settings so long as these automated tools do not aim to exploit the favorable fills offered in the Simulated Environment." | H8444599 |
| prohibited strategies | "Simultaneously placing multiple limit orders at the same price to manipulate order fills is prohibited." "Profiting from isolated, stale or unrealistic fills in low-liquidity contracts (including back-month contracts) or during low-volume hours is not allowed". "Exploiting the absence of slippage and utilizing tight brackets to gain from favorable fills are not permitted." News: "Utilizing strategies that exploit immediate news bursts, such as straddles or strangles." "Masking news trades as standard strategies." Catch-all: T s.23.1.11 ("high-risk, or otherwise posing an undue risk"); s.23.3 "The Company reserves the right to determine, at its own discretion, whether certain trades, practices, strategies, or situations are Prohibited Conduct." | H8444599; H8230009 (August 31, 2026); T s.23.1.11, s.23.3 |
| news, Tier 1 | "No positions or orders (including limit orders) can be open 2 minutes before and after the release." "if news is at 8:30, positions must be closed by 8:28:00 or earlier, and may only be reopened after 8:32:00". Restricted: "Rapid Sim Funded", "Pro Sim Funded". Unrestricted: "All evaluations", "Builder Plans". T1: "FOMC Meetings, FOMC Minutes, Employment Report, CPI". The page's 2026 calendar image: "Trading during these news events is strictly prohibited on sim funded accounts 2 minutes before and after the event." Times are ET (8:30 AM and 2:00 PM) | H8230009 and its embedded calendar image (downloaded and read) |
| news, every release (ambiguous) | under "Standard Trading Protocols": "Ensuring no open positions or orders are active in the order book 2 minutes before and after any data release." "These protocols apply to all news releases." This sits beside the T1 section that leaves evaluations and Builder unrestricted. See section 11, C-9 | H8230009 |
| 2 % price limit | "we do not allow market participation when a product is trading within 2% of a price limit. This prohibited conduct is enforced in the following accounts: Sim Funded Account and Live Funded Account." For NQ/MNQ overnight limits: "trading is suspended at MyFunded Futures" | H9698984 (August 24, 2026) |
| contract counting | "Orders that combine different instruments (e.g., 2 minis and 20 micros) may technically execute even if they exceed the overall limit ... but this is not permitted!" Plan data: `"micro_scaling_factor": 10` (10 micros = 1 mini) everywhere, except `"micro_scaling_factor_in_funded": 1` on Pro (D:135, D:138) | H10244682 (August 24, 2026); D:* |
| payout processing | "Most payouts are approved instantly. If a manual review is required, processing may take up to 6 to 12 business hours on weekdays." Another page says "All payouts are processed in 6-12 business hours excluding holidays."; the plan pages say "may take up to 24 business hours". Paid via Riseworks ("bank transfer or cryptocurrency"); "Plaid/ACH payouts are available for US traders." | H13745661 (August 25, 2026); H11542406 (August 26, 2026); P:rapid |
| payout fee | none stated on any page read | -- (UNVERIFIED) |
| live, general | "rejecting the move to a Live Funded Account is not possible." "your active Sim Funded Account(s) will be placed in a dormant state." "your Sim Funded Accounts will be merged into one Live Funded Account." Live costs are paid from the live balance | H10101257 |
| live breach | a 21-day cooldown: "All Sim Funded account trading is prohibited." and "New Evaluation purchases, account resets, or additional account acquisitions are prohibited." | H13286746 ("Updated over a month ago"); H14290805; H17573707 |
| sim-funded agreement | T s.29: "If you progress to the Sim Funded stage of the Program, your participation is also governed by the Simulated Trader Agreement and its Appendices" -- which take precedence over the Terms "to the extent of a direct conflict" | T s.29 (the agreement itself: **behind login**) |

## 3. Rapid EOD 50K (default, no DLL; product 93; and the DLL variant, product 251)

### 3a. Rapid EOD evaluation

| term | value | source (read 2026-11-18) |
|---|---|---|
| fee | $275 one-time (DLL variant $200); "One-time purchase, nothing to cancel." | D:93, D:251; P:rapid-eod |
| reset | $275 (DLL $200), plan data only | D:93 `"reset_price": 275`; D:251 `"reset_price": 200` |
| activation | $0: "There are no activation fees on this plan." | H16158363 (August 24, 2026) |
| profit target | $3,000: "Profit Target | $3,000" | H16158363 |
| maximum loss | "Maximum Loss Limit (EOD) | $2,000", end-of-day trailing; open-equity losses breach it intraday; locks at $50,100 (start + $100) | H16158363; H8348565; D:93 `"max_drawdown_limit": 50100` |
| daily loss limit | default: "there is no daily loss limit in the evaluation or sim funded stages of the Rapid EOD Plan." DLL variant: "Daily Loss Limit (DLL Version) | ... | $1,000 (Soft Pause)*", where "Soft Pause means trading stops during the current session. It is not a hard breach." and "The Daily Loss Limit resets daily at 6:00 PM ET." The version is chosen at checkout and cannot be switched | H16158363; H18337038 |
| consistency | "Consistency | 30% (Eval Only)"; rule text in section 7 | H16158363; H11994562 (September 25, 2026) |
| minimum days | "Minimum Trading Days | 4 Days" | H16158363 |
| time limit | none stated; 7-day inactivity rule ("Inactivity Rule | 7 Days") | H16158363; H16596524 |
| contracts | "Max Contract | 3 mini / 30 micro"; no scaling (`"scaling_rule": false`) | H16158363; D:93 |
| T1 news | "T1 News Trading | Yes" (allowed in the evaluation) | H16158363; H8230009 |

### 3b. Rapid EOD funded (sim)

| term | value | source (read 2026-11-18) |
|---|---|---|
| fee | none recurring: "Recurring Costs | None" | P:rapid-eod comparison table |
| starting balance | "Initial Balance | $0" | H16158363 |
| maximum loss | "Maximum Drawdown (MLL) | $2,000", "End-of-Day (EOD) Trailing": "Your Max Loss trails upward each time your account closes at a new end-of-day high." "It does not move intraday – only at the close of each trading session." | H16158363 |
| lock | "Once your trailing Max Loss reaches $100, it locks there." "If your balance goes below $100 → the account is breached." | H16158363 |
| floor at a payout | no words for Rapid EOD; plan data `"move_mll_to_lock_on_first_payout": true`, `"funded_max_drawdown_limit": 100`. With the $2,100 buffer cleared by end-of-day balance, the floor has already locked at $100, so the move changes nothing | D:93 (field only); reasoning |
| daily loss limit | default none; DLL variant $1,000 soft pause, as in the evaluation | H16158363; H18337038 |
| consistency | "Consistency Requirement: None (you don't need to meet a consistency rule to get paid)." | H16158363 |
| contracts | "Max Contract | 3 mini / 30 micro"; no scaling. (The plan page's Live table shows "4 / 40" for the 50K; Live only, section 11 C-2) | H16158363; P:rapid-eod |
| T1 news | "T1 News Trading | No"; the article's sentence reads "No T1 news trading is not allowed on this Sim Funded account." (a double negative; the table, H18337038's "T1 news trading is not allowed on this Sim Funded account." and H8230009's restricted list settle it as not allowed) | H16158363; H18337038; H8230009 |
| seats | "Max # of Funded Accounts | Three (3)"; within 5 in all at $25K/$50K | H16158363; H16498635 |
| inactivity | "Inactivity Rule | 7 Days"; a sim-funded inactivity breach forfeits all profits | H16158363; H16596524 |
| buffer, first payout | "Required Buffer: $2,100". "You must first build at least $2,100 in realized profits in the account before requesting your first payout." "First payout eligible 24 hours after first trade (buffer & minimum profit required)" | H16158363; H13745661 |
| later payouts | "Payout Unlock Rule: Once the buffer clears, each payout after that unlocks once your net profit since your last payout reaches $500." | H16158363 |
| winning days | none: no winning-day count on any page; plan data `"minimum_payout_trading_days": 0`, `"performance_based_requirements": false` | H16158363; D:93 |
| frequency | "Payout Frequency: Daily"; plan data `"initial_withdrawal_days": 1`, `"subsequent_withdrawal_days": 1` | H16158363; D:93 |
| minimum, maximum | "Minimum Payout Request: $500"; "There is no cap on how much you can request per payout cycle." Lifetime cap: none stated (`"sim_funded_total_payout_cap_usd": null`) | H16158363; D:93 |
| how much can be requested | not stated as a formula. "Minimum withdrawal after buffer: $500" and plan data `"within_buffer_split": 0`, `"requestable_pct": 1` read as: the whole profit above $2,100, nothing from inside the buffer. A reading, not a quotation (section 12) | H13745661; D:93 |
| split | "90% to the trader", "10% to MyFundedFutures" | H16158363 |
| processing | section 2 | H13745661 |
| path to live | "Live transition on Rapid EOD 50k follows the same rules as standard Rapid 50k." Triggers: "$10,000 net profit achieved in a single trading day (automatic transition)" -- "any profit exceeding $10,000 for that trading day is forfeited" -- or "Consistent payout performance reviewed and approved by our Risk Management Team". "Up to $5,000 of Sim Funded profits are allocated to Reserve upon transition." "All simulated trading accounts and additional purchases are suspended during Live account operation." "Instead of multiple Live accounts, parameters are combined into one Live account." Rapid Live 50k: $0 start, $2,000 EOD MLL "stops at $0", "3 mini / 30 micro", 90/10, daily | H16158363; H13134718 (September 8, 2026) |
| Reserve / bonus | the Reserve is paid as a "Performance Bonus" after "20 profitable trading days on the Live account" and "$10,000 in cumulative gross payouts from the Live account"; on a Live breach it covers the negative balance, and the rest returns to the dormant sim account (the buffer at 50 % / 80 % by sim trading days below / above 30) | H13286746 |

## 4. Rapid 50K (intraday-trailing funded; product 71)

### 4a. Rapid evaluation

| term | value | source (read 2026-11-18) |
|---|---|---|
| fee, reset, activation | $209 one-time; reset $209 (plan data); $0 activation | D:71; P:rapid ("Activation Fee | $0") |
| profit target | "Profit Target | $3,000" | H13134709 (August 24, 2026) |
| maximum loss | "Maximum Loss Limit (EOD) | $2,000" (evaluation end-of-day trailing: P:rapid "Drawdown Type | EOD"); lock at $50,100 as firm-wide | H13134709; P:rapid; H8348565; D:71 |
| daily loss limit | "Daily Loss Limit | None" | H13134709 |
| consistency | "Consistency | 50% (Eval Only)" | H13134709 |
| minimum days | "Minimum Trading Days | 2 Days" | H13134709 |
| contracts | "Max Contract | 5 mini / 50 micro" | H13134709; P:rapid; D:71 `"max_position_size": 5` |
| T1 news | "T1 News Trading | Yes" | H13134709 |

### 4b. Rapid funded (sim)

| term | value | source (read 2026-11-18) |
|---|---|---|
| starting balance | "Initial Balance: $0" | H13134709 |
| maximum loss | "Max Loss Distance: $2,000 from your equity high-water mark (HWM)"; "Drawdown Type: Intra-day trailing"; "Your Max Loss trails your account equity high-water mark during the day." General definition: "the trailing drawdown is calculated intraday based on your peak balance, which includes both realized and unrealized gains." Plan data `"drawdown_mode_in_funded": "RealTime"` | H13134709; H12802721 (January 8, 2026); D:71 |
| lock | "Once your trailing Max Loss reaches $100, it locks there." P:rapid: "Reach (MLL + $100) in profit and the trailing stops permanently" | H13134709; P:rapid |
| daily loss limit, consistency | none: "Rapid has no daily loss limit in either the evaluation or the funded stage."; "Consistency Rule: None in Sim Funded" | P:rapid FAQ; H13134709 |
| contracts | "Max Contracts: 5 minis / 50 micros"; "Exceeding a total of 5 minis or its equivalent in micros (50 micros) can result in a breach". The Cross Instrument article's example of a Rapid 50k "scaling plan" starting at 2 contracts contradicts this (section 11 C-6) | H13134709; H10244682 |
| T1 news | "No T1 news trading is allowed on this Sim Funded account." | H13134709 |
| seats | "For $25K and $50K Rapid accounts, you can hold up to five active sim funded accounts at once." | P:rapid FAQ; H16498635 |
| buffer, frequency, minimum, split | "Required Buffer: $2,100"; "Payout Frequency: Daily - every 24 hours"; "Your first payout becomes available exactly 24 hours after your first trade on the Sim Funded account (as long as you meet the buffer and minimum)."; "Minimum Payout Request: $500"; "90% to the trader" | H13134709 |
| later payouts | no "$500 since last payout" sentence on the Rapid (intraday) pages; plan data `"minimum_profit_since_last_payout": null` (Rapid EOD's is 500) | H13134709; D:71 vs D:93 |
| cap | none stated per request; none lifetime (`"capped_withdrawals": false`) | D:71 |
| path to live | as Rapid EOD (H13134718) | H13134718 |

## 5. Pro 50K (product 135) and Pro 50K One Day (product 138)

### 5a. Pro evaluation

| term | Pro 50K | Pro 50K One Day | source (read 2026-11-18) |
|---|---|---|---|
| fee, reset, activation | $265; reset $265 (plan data); $0 | $379; reset $379 (plan data); $0 | D:135, D:138; H17573707 (October 14, 2026) |
| profit target | $3,000 | $4,000 | H17573707 "Profit Target | $3,000 | $6,000 | $9,000 | $4,000" |
| maximum loss | $2,000 EOD trailing; lock $50,100 | same | H17573707; P:pro "Pro uses end-of-day trailing drawdown in both eval and sim funded."; D:135/138 |
| daily loss limit | none | none | H17573707 |
| consistency | 50 % | none | H17573707 "Consistency | 50% | 50% | 50% | None" |
| minimum days | 2 | 1 | H17573707 "Minimum Trading Days | 2 Days | 2 Days | 2 Days | 1 Day" |
| contracts | 3 mini / 30 micro | 3 mini / 30 micro | H17573707 "Scaling / Max Contacts | 3 mini / 30 micro | ... | 3 mini / 30 micro" |
| T1 news | allowed | allowed | H17573707 "T1 News Trading | Yes" |

H12879226 ("Pro Plan - 1Day Addon", October 13, 2026) sits in the "Legacy Plans" collection and says "For a limited
time" and "Pass in just one day with the free add-on". The current product is priced $379 (D:138), and H17573707
states "Pro 50k One Day account follow the same rules as the Pro 50k." for the funded stage. Whether "for a limited
time" still binds is not stated.

### 5b. Pro funded (sim) (both variants)

| term | value | source (read 2026-11-18) |
|---|---|---|
| starting balance | not printed in words for sim; plan data `"funded_starting_balance": 50000` (Rapid and Builder: 0) | D:135 |
| maximum loss | "Maximum Loss Limit (EOD) | $2,000"; "The max-loss line trails your equity high at the end of each trading day — not intraday." | H17573707; P:pro FAQ |
| floor at the first payout | "After first payout, MLL moves to $50,100 and remains static." "After your first approved payout, the MLL locks permanently at your starting balance plus $100 and stops trailing entirely. Until that first payout, the MLL continues to trail each time you set a new EOD equity high." Plan data: `"funded_max_drawdown_limit": 50100`, `"limited_max_drawdown": true` (whether the floor can trail above $50,100 before a payout: section 12) | H17573707; P:pro FAQ; D:135 |
| daily loss limit | none | H17573707 |
| consistency | "Consistency | None"; "Once you're funded, there is no hard consistency rule. That said, the Pro plan does carry a Consistent Trading Policy: MFFU monitors sim funded accounts for trading behavior that falls outside professional norms — things like maxing contracts on every trade, contract flipping, inconsistent position sizing, or high-frequency strategies not aligned with your stated approach. Violations can result in restrictions or account termination." The policy article: "Uniform Position Sizing, Stops, and Targets", "Avoidance of Maximum Contract Sizes", "No Flipping Contracts for Activity's Sake"; consequences "Immediate Account Restrictions", "Penalties", "Account Termination" | H17573707; P:pro FAQ; H8694840 (August 24, 2026) |
| contracts | "Scaling / Max Contacts | 3 mini / 3 micro" (sim funded) and P:pro "Max Contracts (Mini / Micro) | 3 / 3"; "3 minis from day one on the $50K. No build-up required." Plan data `"micro_scaling_factor_in_funded": 1`: in funded, a micro counts as a mini, so the limit is **3 contracts of either kind** (not a typo) | H17573707; P:pro; D:135 |
| T1 news | "T1 News Trading | Not Allowed" | H17573707; H8230009 |
| seats | no Pro-specific limit; the general 5 at $25K/$50K applies | H16498635 |
| payout timing | "Qualification for Payouts | 14 calendar days from day of first trade. Buffer must be cleared"; "Request a payout every 14 calendar days from your first trade"; plan data `"initial_withdrawal_days": 14`, `"subsequent_withdrawal_days": 14`; P:pro "Get Paid Bi-Weekly" | H17573707; H13745661; D:135; P:pro |
| buffer | "Payout Buffer Requirement | $2,100". **Conflict:** H13745661 "Withdrawal While in Buffer: You can withdraw up to 60% of your profits before fully clearing the buffer." (plan data `"within_buffer_split": 0.6`) against H17573707 "Buffer must be cleared" (section 11 C-3) | H17573707; H13745661; D:135 |
| winning days | none ("There's no minimum number of trading days you have to clock.") | P:pro |
| minimum, maximum | "Minimum Payout Request | $1,000"; "Maximum Payout (per user) | $100,000"; P:pro: "up to $100,000 in total Sim Funded payouts per user" | H17573707; P:pro |
| split | "Profit Split | 80/20" | H17573707 |
| path to live | reviewed after "Three (3) consecutive payouts on the same Pro account.", "Reaching the $100,000 payout cap. Profits above $100,000 are forfeited.", "An invitation from the risk managements team.", "Reaching $20,000 in profit. This triggers a review only." Live (Blue Row Capital): $0 start, "-$2,000" EOD trailing, "Max Contracts | 2", "Minimum Payout | $250", 80/20; the Reserve as in Rapid with Pro 50K bonus thresholds "20" profitable days and "$10,000" gross live payouts | H17573707 |

## 6. Builder 50K: Default $2,000 MLL (product 84) and Add-On $1,500 MLL (product 85)

### 6a. Builder evaluation

| term | Default | Add-On | source (read 2026-11-18) |
|---|---|---|---|
| fee, reset, activation | $153; reset $153 (plan data); $0 | $125; reset $125 (plan data); $0 | H14290805 ("Updated over a month ago") "Price | $153 | $125"; D:84, D:85 |
| profit target | $3,000 | $3,000 | H14290805 |
| maximum loss | "Max EOD Drawdown (MLL) | $2,000" ("Starting Minimum Balance | $48,000"), EOD trailing; lock "$100 above the starting balance"; open-equity losses count | $1,500 ($48,500) | H14290805 |
| daily loss limit | "$1,000 - soft pause" | same | H14290805; P:builder: "When your session hits $1,000 down for the day, trading pauses until the next session — but the account is not breached." |
| consistency | "Consistency Rule | None" | None | H14290805; H11994562 |
| minimum days | "Minimum Trading Days | 1 Day" | 1 Day | H14290805; H11802636 |
| contracts | "4 Minis / 40 Micros" | same | H14290805 |
| news | "News Trading | Allowed" | Allowed | H14290805; H8230009 ("Builder Plans" unrestricted) |

### 6b. Builder funded (sim)

| term | value (Default; Add-On where different) | source (read 2026-11-18) |
|---|---|---|
| starting balance, maximum loss | "$0"; "Max EOD Drawdown (MLL) | $2,000" ($1,500), "Starting Minimum Balance | -$2,000" (-$1,500); EOD trailing; "The MLL locks permanently once it reaches $100 above the starting balance." | H14290805 |
| floor at the first payout | "After your first payout, the Max Loss Limit resets to $100" | H13745661 |
| daily loss limit | "$1,000 soft pause" | H14290805 |
| contracts | "4 Minis / 40 Micros" | H14290805 |
| seats | "Only one Sim Funded account may be active per user at any time on the Builder Plan. In the event of a breach, the earliest a new Sim Funded account may be activated is the following trading day." | H14290805; H16498635 "Builder $50K: Maximum of 1" |
| news | "News trading is fully unrestricted during the evaluation and sim funded stage." | H14290805 |
| inactivity | "If you do not place a trade within 7 consecutive calendar days on your sim funded account, the account will be closed due to inactivity." | H14290805 |
| buffer | "Buffer (Must Be Cleared to Request) | $2,100 | $1,600"; "The buffer equals your MLL + $100" | H14290805 |
| first payout | "For your first payout: you must have at least $500 in net profit above the buffer." "your account balance must reach at least $2,600 before you can submit your first payout request ($2,100 buffer plus $500 net profit above it)." "You may request a payout 48 hours after your first trade has been placed" | H14290805 |
| later payouts | "For all subsequent payouts: you must have at least $500 in net profit since your last approved payout." Cadence "Every 48 hours" (P:builder); plan data `"subsequent_withdrawal_days": 2` | H14290805; P:builder; D:84 |
| days per cycle | "Minimum Qualifying Days / Cycle | 2 Days"; "You must have traded on at least 2 trading days in the current cycle." | H14290805 |
| consistency per cycle | "The 50% consistency rule applies: your single largest profit day cannot represent more than 50% of your total profits in the cycle. This calculation resets after each approved payout." "This is calculated at the time of your payout request". Breach: "If it does, you will need to trade additional days to bring that ratio into compliance before requesting." (gates the request, does not fail the account) | H14290805 |
| minimum, maximum, count | "Minimum Payout Amount | $500"; "Maximum Payout Per Cycle | $2,000"; "Max Sim Payouts | 5 Payouts" | H14290805 |
| amount requested | the worked example requests the whole profit above the buffer: "builds $3,600 in total sim profits", "Net profit above buffer: $1,500", "Requested payout: $1,500 (within the $2,000 max)" | H14290805 |
| split | "80% Trader / 20% Firm" | H14290805 |
| path to live | "After your 5th approved sim payout, you are eligible for promotion to a live funded account." Live: "$2,000 EOD Trailing" ($1,500), "Static once MLL reaches $0", "Daily Loss Limit (Live) | $1,000", min $250, 80/20, daily, "Max Live Accounts | 1". The payout overview also lists "Reaching the total sim cap of $100k" (unreachable at $50K: five payouts of at most $2,000) | H14290805; H13745661 |

## 7. Consistency rules, exactly

- **Evaluation (Rapid EOD 30 %; Rapid and Pro 50 %; Pro One Day and Builder none).** H11994562 (September 25, 2026):
  "The consistency rule at MyFundedFutures is 30% on our Rapid EOD plans and 50% for Rapid Intraday and Pro plans.
  (Pro Plan One day pass has no consistency rule)". "This consistency rule means no single day's profit should exceed
  30% or 50% of your total evaluation profits made."
  - **Which days count:** every evaluation day. The base is "total evaluation profits made". Whether that is net P&L,
    with losing days subtracting, or the sum of winning days is not stated (section 12). The worked example uses the
    target: "Total Profit Target on a 50k account: $3,000", "Max Profit a Trader should achieve: $1,500",
    "Calculation is: Total profit target / 2 = Max Daily Profit".
  - **What a breach does:** "Exceeding the consistency targets does not breach the account. Traders who achieve more
    than the listed percentage amount of their total profit target in one day simply need to trade additional days
    until consistency is met."
  - "Trade additional days until consistency is met" can only work if the base is total profit, not the fixed target.
    That is the engine's `max(target, best day / share)` (`vendor/stage2/propedge/campaign/lockstep.py:516`). The
    example is the case where the account sits exactly at the target. Stage 2's earlier reading took the same view
    (`vendor/stage2/vendor/propfirms/docs/T4_ENGINE_FIT.md:41`).
- **Funded.**
  - **Rapid EOD and Rapid:** none ("Consistency Requirement: None").
  - **Pro:** no numeric rule, but the discretionary Consistent Trading Policy (5b).
  - **Builder:** 50 % of the cycle's profits. The best day in the cycle is judged at the request; the count resets after
    each approved payout; a breach only delays the request (6b). Which days count: the cycle's trading days. Whether
    the first cycle's base is all profit since activation, including the $2,100 buffer, is not stated in words. The
    example "If your total net profits since the last payout are $1,000, your best single day cannot exceed $500."
    reads that way.

## 8. Flip days: what the rules decide

| plan | evaluation in 1 day? | in 2 days? | first payout from 1 big funded day? | the deciding facts |
|---|---|---|---|---|
| Rapid EOD 50K | no | no | **yes** | eval: 30 % and "Minimum Trading Days | 4 Days", so at least four profitable days. Funded: no consistency, no winning days; first payout "24 hours after first trade" once realised profit clears $2,100 and $500 can be withdrawn. Bound: a single day of "$10,000 net profit" moves the account to Live, excess forfeited (H13134718) |
| Rapid 50K | no | **yes** (e.g. two days of $1,500) | **yes** | eval: 50 %, 2 days. Funded as Rapid EOD, but on an intraday equity trail |
| Pro 50K | no | **yes** | big day allowed; no payout before 14 calendar days | eval: 50 %, 2 days. Funded: no numeric consistency, but the Consistent Trading Policy names "maxing contracts on every trade" and "inconsistent position sizing" (discretionary); a $20,000 profit triggers a live review |
| Pro 50K One Day | **yes** ($4,000 in one day) | yes | as Pro 50K | "Consistency ... None", "Minimum Trading Days ... 1 Day", $4,000 target |
| Builder 50K | **yes** ($3,000 in one day) | yes | **no**: at least 2 trading days, best day at most 50 % of the cycle | eval: no consistency, 1 day. Funded: "at least 2 trading days in the current cycle", 50 % of cycle profits, balance at least $2,600 ($2,100 for the add-on), 48 hours after the first trade |

## 9. New releases and changes in the last six months (since about 2026-05-18)

| date | change | source (read 2026-11-18) |
|---|---|---|
| 2026-08-20 (Terms) / 2026-08-25 (help) | **one-time payment model** for all new purchases; legacy subscribers keep 30-day renewals | T s.6.1.2; H16596406; H16596524 |
| 2026-08-25 | **7-day inactivity rule** for one-time-payment accounts, evaluation and sim funded | H16596524 |
| by 2026-08-24 (launch date not stated) | **Rapid EOD** (EOD funded drawdown, 30 % eval consistency, 4 days, 3 sim-funded seats). Its plan page's comparison is dated "as of July 31, 2026"; its earliest dated article is August 24, 2026 | H16158363; P:rapid-eod |
| about 2026-11-10 to 2026-11-17 | **Rapid EOD "with DLL"** version ($1,000 soft pause), and the default "No DLL, at the updated price". The article is marked "Updated this week" on 2026-11-18. Plan-data price records for Rapid EOD 50K and Rapid EOD 50K DLL show `"created_at": "2026-11-10T11:53:15..."` and `"2026-11-10T11:47:42..."` | H18337038; D:93, D:251 (field only) |
| 2026-10-14 (records created 2026-10-12) | **redesigned Pro**: one-time price, 14-day payout timing, $100,000 per-user cap, MLL to $50,100 at the first payout, Reserve and Blue Row Capital live terms. "Accounts on the old Pro products keep every old rule." | H17573707; D:135 (`"created_at": "2026-10-12..."`) |
| 2026-10-13 | **Pro 50K One Day** add-on ($4,000, no consistency, 1 day), "For a limited time" | H12879226; D:138 |
| 2026-10-14 | Studio #003 ($5K) added; no Studio at $50K | H17589665 |
| undated | **Builder $1,500 add-on** ($125); plan-data price records created 2026-08-25 at the one-time cut-over | H14290805; D:85 |
| 2026-01-12 (outside the window) | Rapid split raised to 90 %: "Earn 90% for Rapid sim funded plans as of January 12th, 2026" | H13745661 |

## 10. Engine fit against the Topstep $50K reference (RD-01 section 4.1)

Topstep's values are quoted from Stage 2's ledger (`vendor/stage2/config/rules.yaml`):

| term (key) | value | ledger line |
|---|---|---|
| target (`combine_profit_target`) | 3,000 | :28 |
| drawdown (`combine_mll`) | 2,000 | :54 |
| consistency (`combine_consistency_max_day_frac`) | 0.55 | :80 |
| evaluation lock (`combine_mll_lock_at`) | 0 | :121 |
| evaluation allowance (`combine_position_size_limit`) | 5 | :136 |
| funded floor start (`xfa_mll_start`) | -2,000 | :211 |
| funded lock (`xfa_lock_at`) | 0 | :231 |
| winning days (`xfa_std_winning_days`) | 5 | :255 |
| winning-day minimum (`xfa_std_winning_day_min`) | 150 | :286 |
| request cap (`xfa_std_cap`) | 2,000 | :304 |
| payout minimum (`payout_min`) | 125 | :400 |
| share of balance (`payout_max_frac_of_balance`) | 0.5 | :414 |
| split (`profit_split`) | 0.9 | :432 |
| profit since payout (`require_profit_since_payout`) | true | :447 |
| fee (`subscription_fee`) | 49 every 21 sessions (`billing_days`) | :466, :498 |
| activation (`activation_fee`) | 149 | :551 |
| seats (`max_active_funded_accounts`) | 5 | :637 |
| funded ladder (`funded_scaling_plan`) | "0:2,1500:3,2000:5" | :950 |

The engine's mechanics are cited from `vendor/stage2/propedge/campaign/lockstep.py`:
- the evaluation floor moves at the close and is capped by `combine_mll_lock_at` (:512-515);
- passing uses `max(target, best_day / share)` (:516-518);
- an optional `dll` ends the day and fails nothing (:477-478, :496);
- the funded floor is `min(xfa_lock_at, max(F, B - mll))` (:784);
- eligibility runs by winning days (`_standard_eligible`, :845-852) or by the consistency path (`w_days >= cons_min_days`, `w_best <= cons_max_day_frac * w_profit`, :802-811);
- the request is `min(payout_max_frac_of_balance * B, cap)`, cut by the policy's `keep_balance` (:813-816), and refused below `payout_min` (:817);
- the floor moves to `xfa_lock_at` at any payout (:832);
- `_after_payout` is the seam for a firm's end-of-life rule (:854).

"field" = a vendored field set to the plan's value; "adapter" = new code in `extended/`; "gap" = not modelled.

| term | Rapid EOD 50K | Rapid 50K | Pro 50K / One Day | Builder 50K |
|---|---|---|---|---|
| eval target, drawdown | field (3,000; 2,000) | field | field (3,000 or 4,000; 2,000) | field (3,000; 2,000 or 1,500) |
| eval lock at start + $100 | field (`combine_mll_lock_at` = 100; TS 0) | field | field | field |
| eval intraday breach on open equity | as engine ("breached by any trade") | as engine | as engine | as engine |
| eval consistency | field 0.30 (TS 0.55) | field 0.50 | field 0.50 / none (share 1.0) | none (share 1.0) |
| eval minimum days | 4: implied by 0.30 only if each counted day is a profit day; otherwise **adapter** (A-4's trading-day count) | 2: implied by 0.50 | 2 / 1 | 1 (moot) |
| eval DLL | none / DLL variant: field (`dll` = 1,000, soft) | none | none | field (`dll` = 1,000) |
| eval allowance | field (30 micros) | field (50 micros) | field (30 micros) | field (40 micros) |
| price, billing | field: one-time, never rebilled; resets at list price (plan data) | field | field | field |
| activation | field ($0) | field | field | field |
| 7-day inactivity closure | **adapter** (A-2's pattern with 7 calendar days and "a trade" as the test; the gate needs a session translation) | adapter | adapter | adapter |
| funded floor | field (`xfa_mll_start` -2,000, `xfa_lock_at` +100; TS 0) | **gap/adapter**: intraday trail on equity including unrealised gains needs each trade's favourable excursion (RD-01 G-1; A-7's bracket; Stage 2's `T4_ENGINE_FIT.md:108-115`) | field (relative start 0 at a $50,000 balance; lock +100) -- **if** the floor may trail above +100 before the first payout and then "moves to $50,100", an adapter (section 12) | field (-2,000 or -1,500; lock +100) |
| floor at payout | field (engine moves the floor to the lock; a no-op here) | field | field (the engine's move is the rule) | field |
| payout gate | **adapter**: no winning days (`xfa_std_winning_days` = 0 is a field), but the **buffer gate** (balance at least $2,600 and at least $2,100 left) is DayTraders A-3's pattern; the engine's `keep_balance` is a policy, not a contract term | adapter, as Rapid EOD | **adapter**: 14-calendar-day clock from the first trade and between payouts, plus the buffer ($2,100, or 60 % inside it: two readings) | consistency path: field (`cons_min_days` 2, `cons_max_day_frac` 0.5) **plus adapter** for the $2,600 / $500-since gate and the 48-hour start |
| request size | field `payout_max_frac_of_balance` = 1 with the buffer kept back (adapter above); no cap | same | cap $100,000 lifetime per user: **adapter** (a per-user cumulative cap, forfeiting the excess) | field `xfa_std_cap` = 2,000 |
| minimum, split | field (500; 0.90) | field | field (1,000; 0.80) | field (500; 0.80) |
| payout count, end | **adapter**: the $10,000-in-one-day automatic Live move (the account ends at that close, the excess that day forfeited); the discretionary Risk-team move is a gap (G-4) | adapter | **adapter/gap**: a review after 3 consecutive payouts (discretionary: G-4, with the account read at both ends); $100,000 cap | **adapter**: ends at the 5th payout (Stage 2's `LucidFundedAccount` pattern through `_after_payout`, `lockstep.py:854`) |
| all sim accounts at a live move | `HOUSEHOLD_CLOSES_AT_LIVE` pattern (Stage 2) | same | same | same (one seat) |
| funded allowance | field ladder "0:3" (30 micros) | field "0:5" | **adapter**: "3 mini / 3 micro" with a micro counted as a mini is a cap in contracts, which the micro-denominated sizing cannot express (3 MNQ, not 30) | field "0:4" (40 micros) |
| funded DLL | none / variant: field | none | none | field 1,000 soft |
| seats | field 3 | field 5 | field 5 | field 1, and a breach's replacement waits a trading day (adapter, or moot under a one-account user) |
| payout lag, request timing | field: lag 0-1 session ("instantly" / up to 12-24 business hours); daily cadence with no request-day exclusion, as Lucid's `REQUEST_4_TO_5PM` mechanics | same | lag as Rapid; one request per 14 days | lag as Rapid; one request per 48 hours (implied by 2 trading days) |
| T1 news blackout (funded) | gap with a count: flat and no resting orders from 2 minutes before to 2 minutes after CPI, the Employment Report, FOMC and FOMC minutes (8:30 / 2:00 PM ET, i.e. 07:28-07:32 / 12:58-13:02 CT). CHARTER s.4 already puts entries after 07:35 CT on BLS 08:30 days and FOMC days out, so only **FOMC minutes days** can reach it -- count trades open or resting at 12:58 CT on minutes days (`docs/research/fomc_minutes_dates_2026-11-16.csv`) | same | same | none (unrestricted) |
| 2 % price limit (funded) | gap (RD-01 G-2's analogue) | gap | gap | gap |
| Pro Consistent Trading Policy | -- | -- | gap, priced by the denial ladder (RD-01 G-8's analogue). The state table varies size by state, against "Uniform Position Sizing" | -- |
| flat time | moot: auto-close 4:10 PM ET = 15:10 CT, the CHARTER's flatten time | moot | moot | moot |
| commissions | cost rule (RD-01 4.8): NQ $4.68, MNQ $1.90 round trip (TS fills: NQ $3.78, MNQ $1.22) | same | same | same |

**What the engine would have to be extended to represent (a short list for the lead):**
- **X-1. A contract buffer gate.** A request needs the balance at least buffer plus minimum, and leaves the buffer.
  Applies to all four plans. DayTraders' A-3 is the precedent; the vendored `keep_balance` is a policy knob
  (`lockstep.py:815`) and must not stand in for a rule.
- **X-2. Rapid's intraday equity trail** on unrealised highs. This needs the favourable excursion that Stage 2's trades
  do not carry (`DayBlock.mae` only; RD-01 G-1). The same hard mechanic was flagged in Stage 2's propfirms work, and
  MFFU's row there was moved to Rapid EOD (`vendor/stage2/vendor/propfirms/docs/T3_CEILINGS_DERIVATION.md:110-124`).
  Without it, Rapid is bracketed or left out.
- **X-3. Calendar payout clocks.** Pro's 14 days from the first trade and between payouts; Rapid's 24 hours and
  Builder's 48 hours are implied by daily resolution plus their day rules.
- **X-4. A per-user lifetime payout cap with forfeiture** (Pro, $100,000) and **ending at the Nth payout** (Builder, 5).
- **X-5. A funded allowance counted in contracts, not micros** (Pro "3 / 3").
- **X-6. The 7-day inactivity closure.** Calendar days, any trade resets it, and funded profits are forfeited.
- **X-7. Live moves.** Rapid's automatic $10,000-in-one-day move (excess forfeited); Pro's review after three
  consecutive payouts; Builder's fifth payout. Each ends the sim account, and every other sim account goes dormant.
- **X-8. The funded Tier-1 window** as a count; the 2 % price-limit rule as a gap.

## 11. Conflicts between official pages (each quoted; none resolved here)

- **C-1. Legacy cut-over date.** T s.6.1.2 says "prior to August 20, 2026"; H16596406 and H16596524 say "Effective
  August 25, 2026".
- **C-2. Rapid Live contracts at 50K.** H13134718 says "3 mini / 30 micro"; P:rapid-eod's Live table says "4 / 40".
  Live only.
- **C-3. Pro buffer.** H17573707 (October 14, 2026) says "Buffer must be cleared". H13745661 (August 25, 2026) says
  "You can withdraw up to 60% of your profits before fully clearing the buffer.", and plan data has
  `"within_buffer_split": 0.6` (D:135). The newer page reads stricter; the live checkout data matches the older.
- **C-4. Pro live parameters.** P:pro FAQ says "live account parameters differ from sim funded, including a daily loss
  limit, reduced contract limits, and a static drawdown floor"; H17573707's Live table says "Max Loss Limit (EOD
  Trailing) | -$2,000" and "Daily Loss Limit | None". Live only.
- **C-5. DLL marketing.** H13745661 says "No daily loss limits on Builder, Rapid or Pro plans"; Builder has a $1,000
  soft-pause DLL in both stages (H14290805).
- **C-6. Rapid scaling.** H10244682's example: "if you are trading a Rapid 50k sim funded plan, you start off with 2
  contracts (2 minis OR 20 micros) due to the scaling plan". H13134709 says "5 minis / 50 micros", and plan data has
  `"scaling_rule_in_funded": false`. The example looks stale.
- **C-7. Builder live trigger.** H14290805 says "After your 5th approved sim payout"; H13745661 says "5 consecutive
  payouts" and also "Reaching the total sim cap of $100k".
- **C-8. Payout processing time.** H13745661 says "up to 6 to 12 business hours on weekdays"; H11542406 says "All
  payouts are processed in 6-12 business hours excluding holidays."; the plan pages say "may take up to 24 business
  hours".
- **C-9. News scope.** H8230009's "Standard Trading Protocols" ("no open positions or orders ... 2 minutes before and
  after any data release", "These protocols apply to all news releases") against its own T1 section ("Trading on T1
  News events is permitted for ... All evaluations", "Builder Plans"), its calendar image ("prohibited on sim funded
  accounts") and H8444599 ("Engaging in trades during tier 1 economic data releases is restricted."). On their plain
  words, the protocol lines would bar resting brackets around every release on every account. The T1 section and the
  image confine the hard rule to T1 on Rapid and Pro sim funded.
- **C-10. Copy trading.** H10771500 says "allows copy trading across all account types"; T s.23.1.3.3 qualifies it
  ("in a manner that provides an unfair advantage or manipulates simulated results"), and T s.1.6 makes the Terms
  prevail.
- **C-11. Rapid EOD's double negative.** "No T1 news trading is not allowed" (H16158363). The table and H18337038 settle
  it: not allowed.

## 12. What could not be verified, and how it could be

| item | status | how to settle |
|---|---|---|
| payout fee (any plan) | UNVERIFIED: none stated on H13745661, H11542406 or the plan pages | the Simulated Trader Agreement (behind login), or a written question to support |
| the Simulated Trader Agreement and its Appendices (T s.29), which control the Terms in a direct conflict | **behind login** (signed at the sim-funded stage) | the operator's account, only if the operator chooses; not to be guessed |
| how much of the balance a Rapid / Rapid EOD request may take | a reading (all profit above $2,100), from H13745661's "Minimum withdrawal after buffer: $500" and plan data `within_buffer_split` 0 and `requestable_pct` 1; no sentence states it | a written question; or declare both ends (whole excess above the buffer; the minimum only) |
| Pro: whether the floor trails above $50,100 before the first payout | ambiguous: words say "continues to trail" until the first payout and then "moves to $50,100"; plan data `limited_max_drawdown: true`, `max_drawdown_limit: 50100` reads as a lock at $50,100 | a written question; or read at both ends |
| Pro: buffer cleared vs 60 % inside it | conflict C-3 | read at both ends; or ask |
| evaluation consistency base: net P&L or sum of winning days; whether a losing day counts as a "trading day" toward the minimum | not stated | ask; the engine's net-balance reading is the declared default candidate |
| the reset price | plan data only (`reset_price` = list price); no page states a reset price in words | the checkout page (lead's browser, public, without buying) |
| evaluation time limit | none stated; plan data `access_days: 365` (field) | ask; treat as no limit within the replay's horizon |
| Pro One Day's "limited time" | H12879226 (legacy collection) vs active product D:138 | the lead's browser on `P:pro` (the add-on toggle is client-side) |
| Rapid (intraday): "$500 since last payout" | not stated on Rapid pages; plan data `minimum_profit_since_last_payout: null` | ask; the $500 minimum plus the buffer implies it under a whole-excess request |
| Builder's first-cycle consistency base (from activation, including the buffer?) | implied by the worked example only | ask |
| live terms (all plans) | conflicts C-2 and C-4; discretionary reviews | not modelled (G-4's pattern) |
| the vacation exception to inactivity ("should notify the customer support team") | stated, but its effect is not | not modelled |
| the inactivity rule's reach on legacy accounts | applies to "purchases made on or after August 25, 2026" | moot for a new user |

**Pages for the lead's browser (public pages only, no login, no purchase):**

- `https://myfundedfutures.com/challenge?id=93` -- also `?id=251`, `?id=135`, `?id=138`, `?id=84`, `?id=85`, `?id=71`.
  - **Why:** the checkout app served an empty shell to `curl` in Stage 2's 2026-11-15 survey (not re-fetched today:
    checkout is out of bounds for this reader).
  - **What is needed:** confirm the list price, the reset price, and whether the DLL and One Day variants are offered
    as toggles. Stop before any payment step.
- `https://myfundedfutures.com/faq` returned HTTP 404 to the fetch. The plan pages link "Visit FAQ Center" without a
  stable URL. Need: the FAQ centre's actual address, and any payout-fee or reset-price line on it.
- Nothing else failed. The two T1-calendar images on H8230009 were downloaded and read directly (2026 dates, ET).

## 13. Differences from what the repository already holds

- The lead's brief says there is no record of this firm. There are two unverified, non-ledger records:
  - Stage 2's 2026-11-15 survey: `docs/research/firms_2026-11-15/firms/mffu.json`, read 2026-11-16 UTC.
  - Stage 2's propfirms engine-fit notes: `vendor/stage2/vendor/propfirms/docs/T4_ENGINE_FIT.md:98-115`,
    `T3_CEILINGS_DERIVATION.md:63, 110-124`.
  - Nothing of MFFU is in `vendor/stage2/config/rules.yaml`, and no MFFU rule is loadable.
- Against the 2026-11-15 survey, today's reading:
  - **adds** the evaluation lock in words: H8348565, "locks in at $100 plus the initial starting balance". The survey
    held it UNVERIFIED.
  - **adds** the intraday open-equity breach (H8348565 NOTE).
  - **adds** Rapid (intraday) evaluation's 5 / 50 allowance.
  - **adds** reset prices (plan data).
  - **adds** the DLL variant's $200 price and Pro One Day's $379.
  - **adds** Builder's $125 add-on price.
  - **adds** Pro's funded micro factor 1. The survey had suspected a typo; the plan data agrees with the printed
    "3 / 3".
  - **adds** the T1 calendar image's sim-funded scope.
  - **adds** H8444599's prohibitions.
  - **adds** the Rapid EOD price records re-created 2026-11-10.
- Nothing the survey recorded as verified was found changed. Its $275 / $165 Rapid EOD and $265 / $159 Pro prices
  stand.

## 14. If this becomes a reading or a family

This is firm research, not a family. If the lead builds MFFU contracts into an RD-01-style described reading, or into
a family under E-196, the declaration would need the following.

- **The cells.** One per product. The seven $50K products:
  - Rapid EOD (no DLL, and DLL variant);
  - Rapid;
  - Pro;
  - Pro One Day;
  - Builder $2,000;
  - Builder $1,500.

  Rapid is either bracketed (X-2) or dropped with a reason. Pro One Day differs from Pro only in the evaluation. Each
  unverified term above (section 12) is read at both ends, which adds corners per cell. The count is the lead's: 7
  products, up to 2 ends each on the Rapid request size, the Pro floor and the Pro buffer.
- **Rules first.** Every row above goes through the rules-verifier with its article id and date (CLAUDE.md). Plan-data
  fields are labelled as such; the verifier decides whether a machine field may carry a term.
- **CHARTER section 4 fit.**
  - **Hand entry, at least five minutes after each alert.** Not restricted by MFFU, whose rules permit automation
    without HFT.
  - **One position per firm.** MFFU forbids opposite positions on the same underlying (NQ and MNQ alike); one position
    satisfies that.
  - **No hedging.** MFFU forbids it.
  - **Flat by 15:10 CT.** This is MFFU's auto-close time.
  - **BLS 07:35 CT and FOMC-day exclusions.** These cover MFFU's T1 windows except FOMC minutes days on Rapid and Pro
    funded (a count).
  - **No maximum size into news.** Satisfied by the above.
- **New conduct exposures to declare.**
  - Pro's Consistent Trading Policy (uniform sizing), priced by the denial ladder.
  - The "tight brackets" sim-fill clause (H8444599), which has no threshold.
  - C-9's broad protocol line.
- **Seats.**
  - Builder: one account, so it cannot carry several-account designs.
  - Rapid EOD: three accounts.
  - Rapid and Pro: five accounts.
- **Supply and mechanism.** No new signal mechanism. This is a contract change on the registered trades, so supply is
  the registered designs' own.

---

**Sources** (all read 2026-11-18 UTC; page dates as printed):

- **Terms:** `https://myfundedfutures.com/terms`.
- **Plan pages:** `https://myfundedfutures.com/plans/rapid`, `/plans/rapid-eod`, `/plans/builder`, `/plans/pro`,
  `/plans`, and `https://myfundedfutures.com/` (with its embedded plan data).
- **robots.txt:** `https://myfundedfutures.com/robots.txt`, `https://help.myfundedfutures.com/robots.txt`.
- **Help articles** (`https://help.myfundedfutures.com/en/articles/`), by topic:
  - **Rapid and Rapid EOD:** 16158363 (Rapid EOD 50k, August 24, 2026); 18337038 (Rapid EOD with DLL, "Updated this
    week"); 13134709 (Rapid 50k, August 24, 2026); 13134718 (Understanding Rapid Live, September 8, 2026); 13286746
    (Reserve Program, "Updated over a month ago"); 12802721 (Intraday Drawdown Explained, January 8, 2026).
  - **Pro:** 17573707 (Redesigned Pro, October 14, 2026); 8694840 (Pro consistency policy, August 24, 2026); 12879226
    (Pro 1Day Addon, October 13, 2026).
  - **Builder:** 14290805 (Builder 50k, "Updated over a month ago").
  - **Evaluation:** 11994562 (Consistency Rule, September 25, 2026); 8348565 (EOD Drawdown, August 24, 2026); 16596406
    (Resets vs Renewals, September 24, 2026); 11802636 (Traders Evaluation Simplified, September 24, 2026); 8528339
    (Evaluation Parameters, August 24, 2026); 13523548 (Instant Sim Funded Upgrade, August 24, 2026).
  - **Funded accounts and fees:** 16498635 (Evaluation to Sim-Funded, September 4, 2026); 12398151 (Activation Fees,
    August 25, 2026); 10244682 (Cross Instrument Policy, August 24, 2026); 9698984 (2 % Price Limit, August 24, 2026);
    8528346 (Managing Your Funded Account, August 24, 2026).
  - **Payouts:** 13745661 (Payout Policy Overview, August 25, 2026); 11542406 (First Payout, August 26, 2026); 11542523
    (Refund & Cancellation, August 27, 2026).
  - **Conduct and trading rules:** 16596524 (Inactivity Rule, "Updated over a week ago"); 9558251 (Permitted Times,
    August 24, 2026); 9735811 (Instrument List); 8230009 (News Trading Policy, August 31, 2026, and its two calendar
    images); 12011241 (Hedging, November 10, 2025); 8444599 (Fair Play, "Updated over 2 weeks ago"); 8230018 (Someone
    Else Trading, August 24, 2026); 10771500 (Copy Trading, August 24, 2026).
  - **Live accounts:** 10101257 (Live Funded Account, August 24, 2026); 12109396 (Live FAQ, November 10, 2025).
  - **Other plans:** 17589665 (Studio Plans, "Updated over 2 weeks ago"); 15072271 (Flex 50K, legacy).
  - **Overview pages:** 11553762 (Overview, August 21, 2026); 16130843 (MyFundedClub, August 28, 2026).
- **Help collections:** 17350372, 18640090, 19480282, 16162798, 19775557, 5808821, 5808827, 5811873, 14650040,
  13517838, 5687009, 19717954.
- **Repository:**
  - `prereg/RD-01_firm_contracts.md:220-249, 359-400`;
  - `vendor/stage2/config/rules.yaml`, lines as cited;
  - `vendor/stage2/propedge/campaign/lockstep.py`, lines as cited;
  - `CHARTER.md` section 4;
  - `docs/research/firms_2026-11-15/firms/mffu.json`;
  - `vendor/stage2/vendor/propfirms/docs/T4_ENGINE_FIT.md`, `T3_CEILINGS_DERIVATION.md`.

**Proposed decision row (one finished line, for the lead to number):**

| E-NNN | 2026-11-18 | **Q-135d (E-196): My Funded Futures $50K terms read from its own pages on 2026-11-18 UTC (`docs/research/firms/myfundedfutures_50k_2026-11-18.md`; uncommitted scout note; nothing loaded).** (1) Its Terms of Use hold no clause against automated access, scraping, robots or data mining (s.22.2 and s.22.6 restrict reproduction and commercial use of Content, s.23.1.5 interference); both robots.txt files allow the pages read; so MFFU may be read by the automated reader under E-020 (1). (2) On sale at $50K: Rapid ($209), Rapid EOD ($275; DLL variant $200), Pro ($265; One Day variant $379) and Builder ($153; $1,500-MLL add-on $125); one-time fees, $0 activation; no instant- or direct-funded product; Flex legacy; Studio not at $50K. (3) The evaluations share a $3,000 target (Pro One Day $4,000) and a $2,000 end-of-day trailing drawdown (Builder add-on $1,500), breached intraday on open equity and locking at $50,100 (H8348565); consistency 30 % (Rapid EOD), 50 % (Rapid, Pro) or none (Pro One Day, Builder), raising the bar and failing nothing (H11994562). (4) A one-day evaluation pass is allowed on Builder and Pro One Day; two days on Rapid and Pro; Rapid EOD needs four. A one-day path to the first payout is allowed on Rapid and Rapid EOD (no funded consistency; a $2,100 buffer; 24 hours; a $10,000 single-day profit forces Live and forfeits the excess), not on Builder (2 days, 50 % per cycle) or before 14 calendar days on Pro. (5) Rapid EOD and Builder fit the engine with fields plus adapters for the buffer gate, 7-day inactivity, Builder's fifth-payout end and single seat; Rapid's intraday equity trail needs the favourable excursion (RD-01 G-1) and Pro needs a 14-calendar-day clock, a $100,000 per-user cap and a contract-counted 3 / 3 allowance. (6) Unverified: the payout fee, the Rapid request size, Pro's pre-payout floor, Pro's buffer (conflict H17573707 vs H13745661), the reset price in words, and the Simulated Trader Agreement (behind login). Next: the rules-verifier records the rows the lead takes, starting with Rapid EOD 50K and Builder 50K. | Q-135d |
