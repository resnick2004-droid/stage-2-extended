# Phase 0 audit, track E: are the firm rules the work leans on still current?

Read on 2026-11-15 by audit track E, working independently. Scope: every Topstep rule in Stage 2's ledger
(`vendor/stage2/config/rules.yaml`, 78 keys; `vendor/stage2/RULES_LEDGER.md` §A to §C), the rules that the handoff
(`vendor/stage2/docs/HANDOFF_NEW_REPO_2026-11-15.md` §2.1, §2.4) and this repository's `CLAUDE.md` rely on, and
Lucid's ledger (`vendor/stage2/vendor/propfirms/firms/lucid-trading/`, 32 keys). Nothing under `vendor/` was
written. No result number appears in this note. Every figure below is a firm-rule value quoted from an official page.

**Method.** Each page was fetched as raw HTML with `curl` from the firm's own host (`help.topstep.com`,
`www.topstep.com`, `support.lucidtrading.com`). The article body was extracted to text by a local stdlib parser, so
the quotes below are the page's own characters and were not produced by a summarising tool. Each page was fetched
once. The pages behind the main CHANGED and NEW findings were fetched a second time: 13613539, 8284211, 8284128,
11187768, 8284197 and 16989498, plus the Terms of Use. The extracted text of each second fetch was hashed and
matched the first exactly; the two Terms of Use clauses quoted in N1 and N2 were confirmed present in it. Each page's date is the date it displays, or, where it shows only
"Updated this week", the help centre's own `lastUpdatedDate` timestamp (UTC). The scaling chart was downloaded from
the `src` attribute the page gives and viewed directly. Nothing was submitted, logged into or sent. `lucidtrading.com`
answered HTTP 403 with a bot challenge ("Just a moment..."), and I did not work around it.

---

## 1. Summary

### CHANGED (3): the page now says something different from the ledger

| # | rule | what changed | modelled quantity it would move |
|---|---|---|---|
| C1 | **Tier 1 news restriction** (13613539; ledger §C reference reading "CPI window restriction", 2026-09-27; not a yaml key) | It was **CPI only**. It now covers **CPI, the FOMC rate decision, the FOMC press conference, NFP and PPI**, each with a window from 5 minutes before to 5 minutes after the release (CT 7:25–7:35 for CPI, NFP and PPI; 12:55–1:05 and 1:25–1:35 for FOMC). During a window, opening trades in **NQ** are blocked, and **MNQ** opening trades are capped at **3 micros** on a 50K Combine. On a 50K XFA the cap is **1 micro below a $2,000 balance and 3 above**. Pending orders do not fill inside a window. Positions opened before the window may be held through it. | The engine does not model these windows. The handoff's execution rule (no entry before 07:35 CT on a BLS 08:30 report day, FOMC days excluded; D-525, D-533) avoids them, because the BLS 08:30 day file the engine reads lists the CPI, PPI and Employment Situation release days. What is left is the 07:35 boundary and the basis cited in D-530 (1); see §3. |
| C2 | **Economic releases page** (8284211; ledger §C reference reading, 2026-09-27) | The sentence "Topstep doesn't require you to flatten positions during economic releases" is gone. The page now says "Topstep restricts trading for a short period during Tier 1 News Events." Its release list now includes "CPI Report" and "Producer Price index (PPI)", both at 7:30 AM CT. | No loadable value. D-530 (1) and D-170 described the firm's NQ list as the Unemployment Rate and the FOMC Statement, and that basis is now out of date (§3). |
| C3 | **Temporary position-limit adjustments** (13613539; ledger §C row, 2026-09-27) | Micro Silver (SIL) and Micro Copper (MHG) on the Combine and XFA are now "2/5/7" (were "2/4/6"). The 50K XFA ladder for restricted symbols is now stated in minis and micros: "1 mini / 12 micros", "1 mini / 18 micros", "3 mini / 31 micros" (it was "1 contract", "1 contract", "3 contracts"). Micro Bitcoin (MBT) is now restricted to "5/10/15". The column now names the "Pro Account". | Affects only CL/MCL, metals and MBT, so it matters for IM2's CL leg if that is ever revived. It does not touch NQ or MNQ. It also settles the ledger's open question of what "1 contract" means for MCL: 12 micros. |

### NEW (bearing on the model or on a stated conclusion; the ledger has no row for them)

| # | rule | source | why it matters |
|---|---|---|---|
| N1 | **Automation and API order entry are permitted at Topstep in the Combine and the XFA.** Bots are allowed through the paid TopstepX/ProjectX API. High-frequency trading is prohibited. Orders must originate from the trader's own device: a VPS or remote server may not place orders. The API is not available on Live. **Lucid permits automated systems too.** | 8284197, 8284215, 11187768, 10657969, ToU s.28; Lucid 11404728 | This repository's `CLAUDE.md` says "No automated or API order entry (it gets prop accounts banned)". Neither firm publishes a rule like that: Topstep bans HFT and VPS-originated orders, not automation itself. The project rule can stand as a design choice, but its stated reason is not a firm rule. Any API use would cost $29/month list ($14.50 with the Topstep code), which is a purchase. The engine is unaffected: it models manual execution with a latency of at least 5 minutes (D-266). |
| N2 | **The Terms of Use define poor risk management to include sizing that is inconsistent across trades.** "You acknowledge that these standards are not met where you open substantially (i) larger position sizes compared to your other trades, or (ii) a smaller or larger number of positions compared to your other trades." | Terms of Use s.8 (last updated November 4, 2026) | This is conduct exposure for the handoff's §2.5 state table: an opening funded trade far larger than the later trades on the same account. It gives no threshold, so it belongs with tier 2 and tier 3 (D-145) and changes no value. It sits beside the RTP trigger "You max position a majority of your trades". |
| N3 | **A Reset moves the rebill date.** "Resetting your account pushes your Rebill date out 30 days from the date of purchase." The same applies to a Reset Credit. | 8284128 (September 25, 2026) | The engine's optional reset path (D-146, `CombineAccount.reset`) keeps "The subscription and its billing dates ... unchanged", so with that path on it charges too much, which is the conservative direction. No registered run turns the path on (`reset_failed_combines` is off by default, D-34), so no registered result moves. |
| N4 | **A pending payout is not processed when an account is closed for a violation.** "Pending Payout requests are not processed when an account is closed for a violation." | 16989498 (October 16, 2026) | This agrees with the Focused Trader Program's "Any pending payouts are denied". It does not cover a closure at the trader's request (U1). |
| N5 | **Account hygiene rules.** The Single Profile Policy: "All Trading Combines, Express Funded Accounts, and Live Funded Accounts must be under 1 Topstep profile." No VPN, VPS or proxy. A profile hold: "You can't purchase or request Payouts." / "Wait 7 business days." | 8284197, 10296582 (edited 2026-11-09), ToU s.28 | Not modelled. A hold can delay payouts for up to 7 business days. The rest are compliance facts for the operator's setup. |
| N6 | **Minor, recorded for completeness.** Topstep: "No, warnings alone do not impact your payouts." (hedging, 13747047). Lucid (pages edited today): a new international payout method, "Echlon"; hedging violators are now also excluded from "Intraday account upgrades"; LucidDaily news violators get no On-Demand payouts "for 30 calendar days". | 13747047; Lucid 12890325, 11404734, 11404728 | None is modelled. The DLL-off LucidFlex configuration has no On-Demand payouts, and LucidDaily is not modelled. |

### UNVERIFIED (8)

| # | item | what was tried | what the pages do not say |
|---|---|---|---|
| U1 | `xfa_closure_at_request` (Topstep) | Re-read 8284215, 8284217, 8284233, 8284204, 10657969 (edited 2026-11-12), 12060405, 10551016, 13747178 (edited 2026-11-10), 16989498, 8284121, 14289835, the Terms of Use s.8 (November 4, 2026) and the stale topstep.com/express-funded-account-rules page ("Last updated: June 26, 2025"). Searched the help centre for "close express funded account", "close my account" and "cancel XFA". | No help-centre page says how an XFA is closed at the trader's request, whether there is a fee, when the closure takes effect, what happens to the balance, or what happens to a payout pending at the time. The only closing clause is still on the stale page. |
| U2 | `xfa_seat_frees_at` | 8284215 (edited 2026-11-03), 8284217, 12060405 | No page says when a closed XFA stops counting toward the 5, or whether a seat can be refilled the same evening. |
| U3 | `hold_expiry_days` (a design fact under D-34) | 8284121, 8284217, 8284215 | No page says a passed Combine on hold expires. 8284121 says only that it "remains in "Passed" status until you activate". |
| U4 | Lucid `eval_fee` ($115.50) and `eval_reset_fee` ($115) | lucidtrading.com returned HTTP 403 with a bot challenge. The help centre states the reset policy (11404620, 11404632) but no prices. | These prices were read from the pricing cards on the main site (D-31, the operator's screenshots). This audit could not re-read them. |
| U5 | Lucid `funded_monthly_fee` and `payout_fee` (unverified in the ledger too) | 11404620, 12890325 (edited today), 12945796 | Still no funded recurring fee and no per-method payout fee is stated. 12890325 lists methods only. |
| U6 | The asterisk on 8284206's product list, which marks MES, MNQ, M2K, MYM and the other micros | 8284206 says "See Prohibited Conduct for restrictions on specific products marked with an asterisk (*)." and links to 10296582. | 10296582 (edited 2026-11-09) lists no restriction for specific products other than the 2 % price-lock item. What the asterisk means for MNQ is not stated. |
| U7 | Two edges of the Tier 1 window (C1) | 13613539, 10305426 | (a) Whether the window's end ("7:25 to 7:35 AM") includes 07:35:00 itself. (b) Whether holding a full-size position through a window counts as "Purposefully trading your full Maximum Position Size directly into a scheduled major news event" (D-534 (3)). 13613539 lets existing positions be held as a platform matter, and makes no conduct ruling. |
| U8 | What the recent edits changed | 10296582 (2026-11-09), 8284233 (2026-11-10), 8284121 (2026-11-11), 14434175 (2026-11-10), 10657969 (2026-11-12), 13747178 (2026-11-10) | Every passage the ledger's rows rest on reads the same. What each edit changed was not identified (no earlier full text to compare against). |

### CURRENT

- **Topstep, `rules.yaml`: all 76 verified keys are CURRENT**, the 50K keys and the `_100k`/`_150k` keys alike. The value, and the quoted sentence or table cell behind it, are unchanged. The two unverified keys stay unverified (U1, U2).
- **Topstep, ledger §C behavioural rows: 11 of 12 CURRENT.** One is CHANGED (C3). Of the three reference readings, one is CURRENT (commissions: MNQ "$1.22", NQ "$3.78") and two are CHANGED (C1, C2).
- **Handoff §2.1: every row CURRENT.**
- **Lucid: 28 of 30 verified keys CURRENT** on the help centre. The other two are UNVERIFIED in this audit (U4). The two keys the ledger already marked unverified stay unverified (U5).

---

## 2. Rule by rule

The ledger column gives the key, the value, the article and the date read. The "page read" column gives the
article id and the page's date (displayed date, or `lastUpdatedDate` in UTC). The quotes are verbatim.

### 2.1 Topstep: the Trading Combine

| ledger | page read | verbatim | status |
|---|---|---|---|
| `combine_profit_target` 3000; 8284208; 2026-11-14 | 8284208, https://help.topstep.com/en/articles/8284208-consistency-at-topstep, "September 17, 2026" | "\| $50K \| $3,000 \| Less than $1,650 \|" (columns "Account Size \| Profit Target \| Best Day Recommendation") | CURRENT |
| `combine_mll` 2000, trailing; 8284204; 2026-11-14 | 8284204, …/8284204-what-is-the-maximum-loss-limit, "September 18, 2026" | "\| $50K \| $2,000 \|"; "The MLL is a trailing limit. It rises as your end-of-day balance grows, but never moves down." | CURRENT |
| `combine_mll_lock_at` 0 (locks at the start balance); 8284204; 2026-11-14 | 8284204, as above | "Once it reaches your starting balance, it locks permanently." | CURRENT |
| `combine_consistency_max_day_frac` 0.55; 8284208; 2026-11-14 | 8284208, as above | "Your single best day of profit must stay at or below 55% of your Profit Target. If it exceeds that, your Profit Target increases."; "55% is a hard line. It is not rounded, and there is no buffer." | CURRENT |
| `combine_consistency_boundary_note` at or below; 8284208; 2026-10-10 | 8284208; 8284197, "September 24, 2026" | 8284208 "at or below 55%"; 8284197 "your best single day should stay below 55% of your Profit Target" (the same disagreement in wording the ledger records) | CURRENT |
| `combine_position_size_limit` 5 minis / 50 micros; 8284197; 2026-10-03 | 8284197, …/8284197-trading-combine-parameters, "September 24, 2026" | "\| $50K \| 5 \| 50 \|" ("Account Size \| Max Contracts \| Max Micros"); "Micros and minis count at a 10:1 ratio." | CURRENT |
| `combine_min_trading_days` none stated; 8284197; 2026-10-10 | 8284197 | "No. Big spike days don't build funded traders, consistency does. You can pass in as few as two days" | CURRENT |
| `combine_count_limit` unlimited, but the rate is named conduct; 8284121; 2026-10-30 | 8284121, …/8284121-trading-combine-subscriptions, "Updated this week" (2026-11-11T15:14:22Z); 10370307, "June 18, 2026" | "Yes — no limit on how many you can have at once."; "No limit on Trading Combine purchases" | CURRENT |
| `reset_limit_per_account_per_calendar_day` 2; 10370307; 2026-11-14 | 10370307, …/10370307-reset-purchase-limits | "2 Resets per account per calendar day" | CURRENT |
| `account_start_rate_limit` none stated; 10370307; 2026-11-14 | 10370307; Terms of Use s.3 (November 4, 2026) | "No limit on Trading Combine purchases"; ToU s.3 "if you place an unusually large number of orders for the Services within an unreasonably short period of time, as determined in the sole discretion of Topstep, we reserve the right to suspend any further orders of the Services by you." | CURRENT |
| (new to the record) Reset and rebill | 8284128, …/8284128-what-is-a-reset, "September 25, 2026" | "Resetting your account pushes your Rebill date out 30 days from the date of purchase."; Reset Credits are "Tied to a specific account size AND type (Standard, No Activation Fee, or DLL)" | NEW (N3) |

### 2.2 Topstep: the XFA, its MLL, scaling and payout paths

| ledger | page read | verbatim | status |
|---|---|---|---|
| `xfa_mll_start` −2000; 8284204; 2026-11-14 | 8284204, "September 18, 2026" | "For a 50K XFA, your MLL starts at -$2,000 and trails upward. Once your balance reaches $2,000, the MLL locks at $0 permanently." | CURRENT |
| `xfa_lock_at` 0; the funded MLL floor after the first payout; 8284204; 2026-11-14 | 8284204; 8284233, …/8284233-topstep-payout-policy, "Updated this week" (2026-11-10T20:00:45Z) | 8284204 "After your first Payout: Your MLL is set to $0 regardless of where it was before. The remaining balance becomes your effective loss floor."; 8284233 "After each Payout: Your Maximum Loss Limit (MLL) resets to $0 permanently, and your 5-day count restarts." | CURRENT |
| `funded_scaling_entry_tier_minis` 2; `funded_scaling_plan` 0:2,1500:3,2000:5; 8284223; 2026-10-03 | 8284223, …/8284223-what-is-the-scaling-plan, "July 16, 2026"; the chart image fetched from the page's `src` (PNG 5515×2474) and viewed | Chart: "$50K ACCOUNT" / "Below $1,500" "2 Lots" / "$1,500 - $2,000" "3 Lots" / "Above $2,000" "5 Lots"; text "Example — $50K XFA, 2-lot Scaling Plan:" "2 Minis, OR" "20 Micros"; "Your max contracts do not increase mid-session." | CURRENT |
| `scaling_tier_after_payout` resets with balance; 8284233; 2026-10-03 | 8284233 | "If a Payout reduces your balance to a lower tier, your maximum contract size decreases accordingly." | CURRENT |
| `xfa_std_winning_days` 5; `xfa_std_winning_day_min` 150; 8284233; 2026-11-14 | 8284233 | "5 winning days of $150+ Net P&L. Days don't need to be consecutive. A day locks in at 4:00 PM CT." | CURRENT |
| `require_profit_since_payout` true; 8284233; 2026-11-14 | 8284233 | "Positive net profit since your last Payout. You must have earned at least $0.01 since your last Payout. Your first Payout is exempt." | CURRENT |
| `xfa_cons_min_days` 3; `xfa_cons_max_day_frac` 0.40; 8284208; 2026-11-14 | 8284208; 8284233 | 8284208 "Your Consistency % must be 40% or below to be Payout eligible. This is not rounded."; "A minimum of 3 trading days with at least 1 trade per day"; 8284233 "Stay at or below the 40% Consistency Objective." | CURRENT |
| `xfa_payout_path_choice` chosen at activation, fixed; 8284215; 2026-11-14 | 8284215, …/8284215-express-funded-account-parameters, "Updated over a week ago" (2026-11-03T23:01:38Z) | "At activation, you choose your Payout path: Standard or Consistency."; "Once you select XFA Consistency or Standard, that choice cannot be changed either." | CURRENT |
| `payout_max_frac_of_balance` 0.5; `xfa_std_cap` 2000; `xfa_cons_cap` 3000; 8284233; 2026-11-14 | 8284233 | "Max Payout per request: 50% of your account balance up to the cap below."; "\| $50K \| $2,000 \| $3,000 \|" ("Account Size \| XFA Standard \| XFA Consistency") | CURRENT |
| `profit_split` 0.9; `payout_min` 125; 8284233; 2026-11-14 | 8284233 | "Minimum Payout: $125"; "90/10 profit split — you keep 90%" | CURRENT |
| `dll_offer_status` Combine checkout only, doubles both caps, limited time; 8284233; 2026-11-14 | 8284233 | "\| $50K \| Standard \| $2,000 \| $4,000 \|", "\| $50K \| Consistency \| $3,000 \| $6,000 \|"; "Adding it at the XFA stage doesn't unlock the higher cap."; "Keep an eye on our social channels to find out when this offer will expire" | CURRENT |
| `payout_after_request_survives_mll_breach` true; 8284233; 2026-10-30 | 8284233 | "Yes. Once the Payout amount has been deducted from your balance, hitting the MLL won't affect it." | CURRENT |
| `payout_fee` 0; `payout_fee_ach` 30; `payout_methods_and_fees`; `payout_lag_days_aeropay` 3; `payout_lag_days_ach` 6; 8284233; 2026-11-14 | 8284233 | "\| Aeropay \| US banks only \| Instant after approval \| No Topstep fee** \|"; "\| ACH \| US banks only \| 1-3 business days \| $30 \|"; "\| Wire/SWIFT \| International \| 5-10 business days \| $30 \|"; "Internal approval can take 1-3 business days." | CURRENT |
| (behavioural) the payout request day | 8284233 | "the trading day your Payout is requested will not count toward your winning days for the next Payout cycle." … "This applies to all account types." | CURRENT |

### 2.3 Topstep: fees

| ledger | page read | verbatim | status |
|---|---|---|---|
| `subscription_fee` 49 (Standard path); 14289835; 2026-11-14 | 14289835, …/14289835-topstep-pricing-and-payment-questions, "October 15, 2026" | "\| 50K \| $49/month \| $95/month \|" ("Account Size \| Standard Path \| No Activation Fee Path"); "Paths cannot be changed after purchase." | CURRENT |
| `reset_fee` 49; 14289835; 2026-11-14 | 14289835 | Reset table "\| 50K \| $49 \| $95 \|" | CURRENT |
| `billing_period_calendar_days` 30; `billing_days` 21 (derived); 8284121; 2026-11-14 | 8284121 | "It Rebills every 30 days from your original sign-up date." | CURRENT (see N3 on what a reset does to the rebill date) |
| `activation_fee` 149; 8284217; 2026-11-14 | 8284217, …/8284217-express-funded-account-activation, "September 24, 2026"; 14289835 | "\| Standard Path \| $149 one-time activation fee per XFA \|"; "Standard Path — $149, charged once per XFA earned. No Activation Fee Path — $0." | CURRENT |
| (§C) Back2Funded $599 at 50K, at most 2, before the first payout, 30-day window | 12060405, …/12060405-back2funded-rules-guidelines-and-how-it-works, "September 29, 2026" | "\| $50K XFA \| $599 \|"; "up to 2 Reactivations per account if you lose your Express Funded Account® (XFA) before your first Payout"; "You have 30 calendar days from account closure to decide" | CURRENT |

### 2.4 Topstep: accounts and the cap

| ledger | page read | verbatim | status |
|---|---|---|---|
| `max_active_funded_accounts` 5; 8284215; 2026-10-03 | 8284215 (2026-11-03T23:01:38Z); 8284217 | "You can hold up to 5 active XFAs at a time."; "Shoulder Tap account holders are limited to 1 XFA."; 8284217 "If you already have 5 active XFAs or a Live Funded Account®, the button will be greyed out." | CURRENT |
| `xfa_cap_shared_across_sizes` true; 8284215; 2026-11-14 | 8284215 | "Yes. Example: two 50K XFAs and three 150K XFAs." | CURRENT |
| `hold_queue_behaviour` hold until a slot frees, fee due at activation; 8284217; 2026-11-14 | 8284215; 8284217; 8284121 | "If you pass a Trading Combine® while at the limit, the new XFA goes on hold until one closes."; "You'll need to close an account before activating a new one."; 8284121 "the passed Trading Combine remains in "Passed" status until you activate your Express Funded Account, ensuring you won't lose the account while waiting to activate." | CURRENT |
| `xfa_activation_latency` minutes; 8284215; 2026-10-10 | 8284215; 8284197 | "Minutes after paying the Activation Fee. If you pass on a Friday, your XFA won't be available until markets reopen at 5 PM CT Sunday."; "The status update can take up to 30 minutes." | CURRENT |
| `hold_expiry_days` design fact (D-34) | as above | no expiry is stated | UNVERIFIED (U3); the design fact stands |
| `xfa_seat_frees_at` unverified | 8284215; 12060405 | "the new XFA goes on hold until one closes"; "Back2Funded-eligible XFAs do not count toward your 5-account limit until the Reactivation fee is paid" | UNVERIFIED (U2) |
| `xfa_closure_at_request` unverified | 10657969, "Updated this week" (2026-11-12T14:58:16Z); Terms of Use s.8 | "Once the Risk Team determines you're ready, your options are to move to Live or close your Express Funded Account."; ToU s.8 "You may terminate your Account at any time by contacting Support." (the whole Account, not one XFA) | UNVERIFIED (U1) |
| (behavioural) XFA inactivity | 8284215 | "XFAs with no trading activity for more than 30 days may be closed. XFAs can't be put on hold." | CURRENT |

### 2.5 Topstep: hours, products and news

| ledger | page read | verbatim | status |
|---|---|---|---|
| `trading_hours`: flat by 15:10 CT, reopen 17:00, Friday close 15:10, holiday early close less 15 min; 8284206; 2026-11-14 | 8284206, …/8284206-when-and-what-products-can-i-trade, "Updated over 2 weeks ago" (2026-10-28T13:29:17Z); 13350348, "September 18, 2026" | "All positions must be closed by 3:10 PM CT every weekday. You can resume trading at 5:00 PM CT."; "\| Friday close \| 3:10 PM CT (closed till Sunday at 5:00 PM) \|"; 13350348 "All account types must close positions 15 minutes before any early close." | CURRENT |
| (§C) Risk Managers begin flattening at 3:08 PM CT | 8284206 | "Avoid opening new positions after 3:08 PM CT — Risk Managers begin flattening at that time." The ledger quoted "begin to automatically cancel at 3:10 CST"; the page now reads "at 3:10 PM CST" (wording only) | CURRENT |
| (§C) day locks: Combine 3:10 PM CT, XFA 4:00 PM CT | 8284208; 8284233 | "At 3:10 PM CT, that day's value locks into your trading history and cannot be changed."; "A day locks in at 4:00 PM CT." | CURRENT |
| `permitted_products` all CME Group products; 8284206; 2026-10-03 | 8284206 | "Every tradeable CME Group product, with permitted hours for the Trading Combine and Funded Accounts."; "\| E-mini NASDAQ 100 (NQ) \| Micro E-mini NASDAQ 100 (MNQ)* \|"; "See Prohibited Conduct for restrictions on specific products marked with an asterisk (*)." | CURRENT; the asterisk is UNVERIFIED (U6) |
| (§C reference) the CPI window restriction, read 2026-09-27: "Ahead of Consumer Price Index (CPI) releases, Topstep temporarily restricts new opening transactions on equity index products (ES, RTY, YM, NQ, NKD) in SIM" | 13613539, …/13613539-risk-adjustments-high-risk-high-volatility, "Updated this week" (2026-11-12T15:00:43Z); fetched twice, identical | "Ahead of Tier 1 News Events (for example, CPI, FOMC, NFP, PPI), Topstep temporarily restricts new opening positions on equity index products and metals in SIM to protect Traders from extreme volatility."; "Minis (ES, RTY, YM, NQ, NKD, GC, SI, HG, PL): No new opening transactions permitted during the 10-minute window surrounding the release (5 minutes before, 5 minutes after)."; "\| Consumer Price Index (CPI) \| 7:30 AM \| 7:25 to 7:35 AM \|", "\| FOMC rate decision \| 1:00 PM \| 12:55 to 1:05 PM \|", "\| FOMC press conference \| 1:30 PM \| 1:25 to 1:35 PM \|", "\| Non Farm Payroll (NFP/Unemployment Rate) \| 7:30 AM \| 7:25 to 7:35 AM \|", "\| Producer Price Index (PPI) \| 7:30 AM \| 7:25 to 7:35 AM \|"; "\| 50K Standard \| $50,000 \| 3 \| Blocked \| Capped at 3 micros \|"; "\| $50K XFA \| Below $1500 \| $20,000 \| 0/1 \| 0/1 \|", "\| $50K XFA \| $1500-$2000 \| $30,000 \| 0/1 \| 0/1 \|", "\| $50K XFA \| Above $2000 \| $50,000 \| 0/3 \| 0/2 \|"; "Pending orders are not open positions. They will not fill during the 10-minute window, and new pending orders intended to execute during this timeframe cannot be placed."; "Traders holding existing positions in equity index products and metals prior to 5 minutes before the news event may keep them open and manage them through the Tier 1 News Events window." | **CHANGED (C1)** |
| (§C reference) economic releases, read 2026-09-27: five releases, no CPI or PPI; "Topstep doesn't require you to flatten positions during economic releases — in SIM or Funded Accounts." | 8284211, …/8284211-economic-releases, "Updated this week" (2026-11-10T22:13:54Z); fetched twice, identical | "\| CPI Report \| 7:30 AM \|"; "\| Unemployment Rate (Non-Farm Payroll) \| 7:30 AM \|"; "\| FOMC Statement \| 1:00 PM \|"; "\| Producer Price index (PPI) \| 7:30 AM \|"; "Topstep restricts trading for a short period during Tier 1 News Events." The "doesn't require you to flatten" sentence is no longer on the page. | **CHANGED (C2)** |
| (§C) temporary position-limit adjustments, read 2026-09-27: SIL and MHG "2/4/6"; 50K XFA restricted symbols "1 contract" / "1 contract" / "3 contracts" | 13613539, as above | "Micro Silver (SIL) = 2/5/7", "Micro Copper (MHG) = 2/5/7" (Trading Combine, Express Funded Account, Pro Account column); "Micro Bitcoin (MBT) = 5/10/15"; 50K XFA: "Below $1500 balance = 1 mini / 12 micros", "$1,500 balance = 1 mini / 18 micros", "$2,000 balance = 3 mini / 31 micros"; CL, MCL, QM, RB, HO and GC unchanged ("Crude Oil (CL) = 3/6/9", "Micro Crude Oil (MCL) = 30/60/90") | **CHANGED (C3)** |
| (§C) price-lock limit | 10296582; 8284225, "May 29, 2026" | "Holding a position within 2% of a product's price lock limit"; "Update: Equity products ES, MES, NQ, MNQ, RTY, M2K, YM, and MYM overnight price limits have expanded from 5% to 7%." | CURRENT |
| (§C reference) commissions | 8284213, 2026-09-30T21:00:42Z | "\| Micro E-mini NASDAQ 100 (MNQ) \| $1.22 \|"; "\| E-mini NASDAQ 100 (NQ) \| $3.78 \|" | CURRENT |

### 2.6 Topstep: conduct, copying across accounts, hedging and automation

| ledger | page read | verbatim | status |
|---|---|---|---|
| `cross_account_hedging` prohibited; 13747047; 2026-10-30 | 13747047, …/13747047-understanding-hedging, "July 27, 2026" | "Cross-account hedging means simultaneously going long and short the same or correlated instrument across multiple accounts — such as MES/ES, MNQ/NQ."; "Opposing positions are prohibited even if the overlap is brief or unintentional."; "Hedging attempts are tracked at the Trader level." | CURRENT |
| `cross_account_opposite_positions` prohibited; 13747047; 2026-10-30 | 13747047 | "Yes! You can trade the same markets across different accounts. What's prohibited is holding opposite positions simultaneously in a way that eliminates market risk."; "Trade each account independently based on your own analysis"; also on the page, and new to the record: "No, warnings alone do not impact your payouts." | CURRENT (+ N6) |
| `multi_account_same_strategy` permitted; `trade_copier_own_accounts` permitted; 8284215 / 14434175 | 8284215; 14434175, …/14434175-topstepx, "Updated this week" (2026-11-10T22:29:25Z) | "Yes, up to $750K buying power using a trade copier. See What is a Trade Copier. Hedging across accounts and coordinated trading with others is prohibited."; "The Trade Copier lets you mirror trades from a Lead account to 1 or more Follower accounts automatically — so you can run the same strategy across multiple accounts without placing every order manually."; "The Lead account must have the lowest Maximum Position Size (MPS) of all accounts in the group."; "When a Payout request is submitted, Follower accounts are automatically unlinked." | CURRENT |
| `prohibited_trading_strategies` (7 strategies, the SIM-fill examples); 10305426; 2026-10-30 | 10305426, …/10305426-prohibited-trading-strategies-at-topstep, "June 10, 2026" | "Repeatedly trading aggressively, hitting the Maximum Loss Limit (MLL) in one account, then switching to another account and repeating."; "Purposefully trading your full Maximum Position Size directly into a scheduled major news event."; "Using tight brackets or auto-breakeven to take advantage of favorable SIM fills"; "We retain the right to reject profit claims if abuse is suspected." | CURRENT |
| `prohibited_conduct` (19 items, the catch-all); 10296582; 2026-10-30 | 10296582, …/10296582-prohibited-conduct, "Updated this week" (2026-11-09T15:55:19Z) | Still 19 items, among them "Excessive purchases of Trading Combines or Resets"; "Coordinated trading — performing trades in concert with others (including unconnected accounts or third parties) to pool risk, hedge aggregate positions, or trade the same or opposite strategy simultaneously"; "Cross-account hedging (single-user) — holding opposite positions across multiple accounts simultaneously"; "Unfair technology — using software, AI, ultra-high speed systems, or mass data entry to gain an unfair advantage"; "Any other conduct that Topstep determines, at its sole discretion, is uncommercial, games the market, is not a viable strategy, or is not responsible trading"; responses "Warning" … "Delay or denial of a Payout request"; "Violations are reviewed case-by-case based on severity and history." New to the record: "Do not use a VPN."; the profile hold ("You can't purchase or request Payouts."; "Wait 7 business days.") | CURRENT (+ N5; U8 for what the edit changed) |
| (ToU) s.3, s.8, s.27, which the ledger had not re-read against the November 4 version | https://www.topstep.com/terms-of-use, "Last updated: November 4, 2026"; fetched twice | s.27 "you will not be entitled to receive any withdrawals from any other account maintained with Topstep, all of which will be forfeited and closed immediately."; "In concert with others, including between unconnected accounts and third parties, performing the same trading strategy (i.e., performing the same trades in the same time increments), opposite strategy, or other activity meant to pool or hedge risk of the aggregate, unconnected accounts;" s.8 "You may terminate your Account at any time by contacting Support." s.3 as in 2.1 | CURRENT (each passage the ledger quotes reads the same) |
| (new) ToU s.8 sizing | Terms of Use, as above | "You agree to apply market standard risk management rules for trading on financial markets at all times while using the Sites and Services. You acknowledge that these standards are not met where you open substantially (i) larger position sizes compared to your other trades, or (ii) a smaller or larger number of positions compared to your other trades." | NEW (N2) |
| (new) automation and API order entry | 8284197; 8284215; 11187768, …/11187768-topstepx-api-access, "September 17, 2026" (fetched twice); 10657969; ToU s.28 | 8284197 "Can I use automated trading strategies?" "Yes, with conditions. Topstep won't help set up or troubleshoot automated strategies, and no exceptions are made for errant trades or malfunctions."; 11187768 "Yes. Custom automated strategies and bots are allowed via the TopstepX / ProjectX API, subject to standard platform rules and our prohibition on highfrequency trading (HFT)."; "API Access is $29/month. Topstep Traders get 50% off with code topstep — that's $14.50/month"; "All trading activity must originate from your personal device. The use of VPS, VPNs, and remote servers is prohibited by Topstep's Terms of Use. Running automation on a VPS can result in account suspension or removal from the program."; "A rule violation is treated the same whether it originates from manual trading or third-party automation."; 10657969 "The API Gateway is built for the simulated environment and isn't available on Live"; ToU s.28 "Using any VPN, VPS, proxy (including residential), or other service masking your IP address or location on Accounts … is strictly prohibited" | NEW (N1) |
| (new) the Single Profile Policy | 8284197 | "All Trading Combines, Express Funded Accounts, and Live Funded Accounts must be under 1 Topstep profile."; "Multiple profiles are a Terms of Use violation and can result in account closure or suspension." | NEW (N5) |
| (new) a pending payout at a closure for a violation | 16989498, …/16989498-i-ve-been-banned-what-are-my-options, "October 16, 2026" (fetched twice) | "Pending Payout requests are not processed when an account is closed for a violation." | NEW (N4) |

### 2.7 Topstep: the programs

| ledger | page read | verbatim | status |
|---|---|---|---|
| `responsible_trading_program`: six triggers; DLL −$1,000 at 50K; Consistency-only new XFAs; leaves only through Live with $10,000 of LFA profit; 13620045; 2026-10-30 | 13620045, …/13620045-what-is-the-responsible-trading-program, "October 15, 2026" (the version the 2026-10-30 read saw) | "Multiple accounts hit the Maximum Loss Limit in one day"; "You max position a majority of your trades"; "You don't keep losers smaller than winners"; "You don't use stops"; "You go full port or trade on tilt, FOMO, or revenge"; "You disrespect your daily limits"; "50K accounts = -$1,000"; "Standard XFA is unavailable until RTP is completed"; "Make $10,000 in profit in your Live Funded Account."; "Traders in RTP can request payouts of up to $6,000 every 3 trading days" | CURRENT |
| (10406542) "Use MLL as a stop loss" listed as a Don't | 10406542, "August 13, 2026" | "\| Yes \| No \|" … "Use MLL as a stop loss" | CURRENT |
| `focused_trader_program`; 10551016; 2026-10-30 | 10551016, …/10551016-what-is-the-focused-trader-program, "August 10, 2026" | "Excessive recycling of Trading Combines® or XFAs"; "All current accounts (Live, Express Funded Account, Trading Combine) are closed"; "Any pending payouts are denied"; "Excessive Resets and Trading Combine purchases"; "Activating and losing many Express Funded Accounts in a short period of time"; "You cannot purchase new Trading Combines, Resets, or B2F Reactivations"; "1 active $50K account at a time (Trading Combine, XFA, or LFA)" | CURRENT |
| `dll_amount_50k` 1000 (and 100K 2000, 150K 3000); 10490293; 2026-11-14 | 10490293, …/10490293-daily-loss-limit-…, "June 30, 2026" | "$50K Account: $1,000"; "$100K Account: $2,000"; "$150K Account: $3,000"; "Triggering it is not a rule violation — it's a forced break for the rest of that session." | CURRENT |

### 2.8 Topstep: the 100K and 150K keys (each read from the same tables as its 50K key)

| keys | verbatim | status |
|---|---|---|
| `combine_profit_target_100k` 6000, `_150k` 9000 (8284208) | "\| $100K \| $6,000 \| Less than $3,300 \|", "\| $150K \| $9,000 \| Less than $4,950 \|" | CURRENT |
| `combine_mll_100k` 3000, `_150k` 4500 (8284204) | "\| $100K \| $3,000 \|", "\| $150K \| $4,500 \|" | CURRENT |
| `xfa_mll_start_100k` −3000, `_150k` −4500 (8284204) | "\| $100K XFA \| -$3,000 \|", "\| $150K XFA \| -$4,500 \|"; still no lock balance stated for these sizes: "locks at $0 once reached, same as a brand new XFA." | CURRENT |
| `combine_position_size_limit_100k` 10, `_150k` 15 (8284197) | "\| $100K \| 10 \| 100 \|", "\| $150K \| 15 \| 150 \|" | CURRENT |
| `subscription_fee_100k` 99, `_150k` 199; `reset_fee_100k` 99, `_150k` 199 (14289835) | "\| 100K \| $99/month \| $149/month \|", "\| 150K \| $199/month \| $229/month \|"; reset "\| 100K \| $99 \| $149 \|", "\| 150K \| $199 \| $229 \|" | CURRENT |
| `activation_fee_100k`, `_150k` 149 (8284217) | the single fee "$149 one-time activation fee per XFA" on a page covering "50K, 100K, or 150K" | CURRENT |
| `funded_scaling_plan_100k`, `_150k` (8284223, chart) | "$100K ACCOUNT": "Below $1,500" 3, "$1,500 - $2,000" 4, "$2,000 - $3,000" 5, "Above $3,000" 10 Lots; "$150K ACCOUNT": … "$3,000 - $4,500" 10, "Above $4,500" 15 Lots | CURRENT |
| `xfa_std_cap_100k` 3000, `_150k` 5000; `xfa_cons_cap_100k` 4000, `_150k` 6000 (8284233) | "\| $100K \| $3,000 \| $4,000 \|", "\| $150K \| $5,000 \| $6,000 \|" | CURRENT |

### 2.9 Lucid (LucidFlex $50K; support.lucidtrading.com)

| ledger key, value, date read | page read | verbatim | status |
|---|---|---|---|
| `eval_profit_target` 3000; `eval_drawdown_amount` 2000; `eval_position_limit` 4 minis / 40 micros (2026-10-30) | 12945790, https://support.lucidtrading.com/en/articles/12945790-lucidflex-evaluation-account, 2026-10-19T00:22:28Z | "\| $50,000 \| $3,000 \| $2,000 \| 40% (50% with add-on) \| 4 mini or 40 micros \|" | CURRENT |
| `eval_drawdown_type` EOD trailing; `eval_drawdown_lock` locks at start plus $100; `funded_drawdown_type`; `payout_balance_consequence` | 12945815, …/12945815-lucidflex-drawdown, "August 26, 2026" | "LucidFlex evaluation and funded accounts use an End-of-Day Drawdown (EOD Drawdown) system to calculate the Max Loss Limit (MLL)."; "\| $50,000 \| $2,000 \| $52,100 \| $50,100 \|"; "Once you request a payout from LucidFlex, your MLL automatically adjusts to the Locked MLL Balance" | CURRENT |
| `eval_consistency_rule` 0.40 | 12945805, …/12945805-lucidflex-consistency-percentage, 2026-10-19T00:22:51Z | "In LucidFlex evaluation accounts your Consistency Percentage must be 40% or less to be eligible to upgrade to a LucidFlex funded account." | CURRENT |
| `eval_min_days` 3 | 12945790 | "Pass in as few as 3 days with 40% consistency, or 2 days with the 50% consistency add-on" | CURRENT |
| `eval_daily_loss_limit` optional at checkout; `funded_daily_loss_limit` | 16226050, …/16226050-lucidflex-customization, 2026-10-20T16:28:09Z; 12945795, "October 13, 2026" | "The DLL is a soft breach, so if you hit it you will simply be locked out until the next trading session."; "With the Daily Loss Limit Off, payouts follow the regular end-of-day schedule."; "Once selected, these settings cannot be changed for an active account." | CURRENT |
| `eval_count_limit` 10; `max_accounts` 5 funded per household | 11404617, …/11404617-maximum-number-of-accounts, "August 26, 2026" | "Up to 10 active evaluation accounts per household or family."; "Up to 5 active funded accounts per household or family." | CURRENT |
| `eval_time_limit` none (30-day inactivity deletion) | 12945790; 11404632, "August 26, 2026" | "take as long as you need to pass"; "Accounts that have not been traded resulting in at least a net profit or loss of 1$ within 30 calendar days will be deemed abandoned and will be permanently deleted from our systems." | CURRENT |
| `eval_fee` 115.50; `eval_reset_fee` 115 (2026-11-05, pricing cards) | lucidtrading.com: HTTP 403, bot challenge; 11404620 ("August 26, 2026") states the policy only | "If a trader fails an evaluation account, they may purchase a reset from the trader dashboard." (no price) | UNVERIFIED (U4) |
| `funded_type` sim funded, $0 activation, live move at discretion | 12945790; 16558826, …/16558826-new-live-structure, 2026-10-14T04:58:44Z | "No activation fees to upgrade to funded account"; "All live transitions occur at the discretion of the Lucid risk team." | CURRENT |
| `funded_drawdown_amount` 2000; `funded_consistency_rule` none | 12945795 | "\| $50,000 \| $2,000 \| Optional \| Yes \| 4 mini or 40 micros \|"; "There is no Consistency Percentage on LucidFlex funded accounts" | CURRENT |
| `funded_position_limit` 2 / 3 / 4 minis by profit | 12945808, …/12945808-lucidflex-scaling-plan, "May 6, 2026" | "\| $0 - $999 \|" … "2 minis or 20 micros"; "\| $1,000 - $1,999 \|" … "3 minis or 30 micros"; "\| $2,000 - $2,999 \|" … "4 minis or 40 micros"; "The scaling plan updates at the end of each session" | CURRENT |
| `payout_min` 500; `payout_cap` 50 % of profit up to $2,000; `payout_split` 0.90; `payout_frequency_gate` 5 days of $150, net profit ≥ $1, at most 5 payouts; `payout_processing_days` 2 | 12945796, …/12945796-lucidflex-payouts, "July 28, 2026" | "Minimum payout request: $500"; "\| $50,000 \| 50% of Profitup to $2,000 \|"; "All LucidFlex funded account payouts are split 90% to the trader and 10% to Lucid Trading."; "\| $50,000 \| $150 \|"; "Traders must have positive net profit (even just $1) during each payout cycle"; "Traders may take up to 5 payouts from each LucidFlex account after which they will be moved live."; "Payouts will be disbursed to your payment method within 2 business days." | CURRENT |
| `payout_fee`, `funded_monthly_fee` (both unverified in the ledger) | 12890325, …/12890325-payout-methods, "Updated today" (2026-11-16T03:59:38Z); 11404620 | methods only (Plaid, WorkMarket by ADP, the new "Echlon", crypto); no fee is stated | UNVERIFIED (U5); Echlon is NEW (N6) |
| `copy_trading_terms` permitted; `multi_account_same_strategy` permitted | 11404728, …/11404728-other-trading-activities, "Updated today" (2026-11-16T05:35:24Z) | "Automated trading systems and trade copiers are permitted"; "All automated activity must comply with Lucid Trading rules" | CURRENT |
| `news_trading_terms` allowed on Flex | 11404728 | "Allowed on Flex, Pro and Direct"; "Traders may enter or exit positions around scheduled or unscheduled news events on these plans without it being a breach" | CURRENT |
| `prohibited_conduct` (microscalping, hedging, HFT, sim exploitation) | 11404734, …/11404734-prohibited-hedging, "Updated today" (2026-11-16T05:22:09Z); 11404742, 11404732, 11404736, "August 26, 2026" | "Hedging between different firms or funded platforms"; "Example: You cannot go long ES in one account and short NQ in a separate account."; "Accounts with a Hedging Violation are not eligible for On-Demand payouts, or Intraday account upgrades." (the ledger quoted 16226050's "not eligible for intraday payouts"); "More than 50% of your profits are generated from trades held for 5 seconds or less" | CURRENT (+ N6) |
| `permitted_products` (CME Group futures; MNQ $0.50 a side) | 11508978, "August 26, 2026" | "\| MNQ \| Micro E-mini Nasdaq-100 Index Futures \| 0.50 \| CME \|" | CURRENT |
| §E 6, session mechanics | 11404729, "August 26, 2026" | "All positions must be closed by 4:45 PM EST, Monday through Friday"; "Trading resumes at 6:00 PM EST, Sunday through Thursday" | CURRENT |
| §E 12, the live move | 16558826 | "All simulated prop accounts are closed when a trader is moved live, or opts out of trading live via cash-out."; "\| $50,000 \| $4,000 \| 20 \| $2,000 \|" (Live Bonus) | CURRENT |

---

## 3. Assessment

**No loadable value of the $50K Combine or XFA has changed.** The profit target, the MLL and its lock, the funded
floor after a payout, the 55 % and 40 % consistency rules, the position limit and the scaling ladder, the payout
paths, caps, split and minimum, the payout fees and lags, the subscription, reset and activation fees, the 5-account
cap and the hold on a pass, the 15:10 CT flatten, the RTP, the FTP and the conduct pages all read as the ledger
records them. Every row of the handoff's §2.1 still stands. Lucid's help-centre rules also stand.

**What should be acted on, in order of weight:**

1. **The Tier 1 news windows (C1, C2).** The firm now blocks new NQ opening trades from 07:25 to 07:35 CT on CPI,
   NFP and PPI days, and around both FOMC events. During those windows MNQ opening trades are capped at 3 micros on a
   50K Combine and at 1 micro on a 50K XFA below a $2,000 balance. The handoff's §2.4 rule ("no entry before 07:35 CT
   on a BLS 08:30 release day; FOMC days excluded") already keeps the candidates out of these windows, because the
   engine's BLS 08:30 day file lists the CPI, PPI and Employment Situation release days. Three points remain:
   - **(a) The boundary.** An entry at the 07:35 mark sits on the window's stated end (U7 (a)). If 07:35:00 is
     inside the window, a full-size MNQ entry there would be capped or refused. The safe reading puts the first
     report-day entry strictly after 07:35. This is worth a decision row before the confirmation.
   - **(b) The cited basis.** D-530 (1) and D-170 cite the firm's NQ list as the Unemployment Rate and the FOMC
     Statement only. The list now includes CPI and PPI. The conclusion still holds, but its cited basis should be
     corrected under a new E-row.
   - **(c) Holding through a window.** 13613539 now lets a position opened earlier be held through a window. Whether
     a full-size position held through counts as "trading max size into news" (10305426) is still unstated, so
     D-534 (3)'s question about FV3-C is only half answered.
2. **Sizing conduct (N2).** Terms of Use s.8 says market-standard risk management is "not met" when positions are
   substantially larger than one's other trades. The §2.5 state table opens a funded account with one large trade
   and then trades small. This is another unthresholded conduct exposure of the RTP and catch-all kind (tier 2 and
   tier 3, D-145). It should be named wherever the conduct exposure of a sizing plan is reported. No value changes.
3. **Automation (N1).** This repository's ban on automated or API order entry is the operator's design choice, not
   a published firm rule. Topstep sells API access and allows bots in the Combine and XFA, banning HFT and
   VPS-originated orders; Lucid permits automated systems. The engine's manual-execution model (D-266) is
   unaffected. If the rule's stated reason is kept, it should be recorded as the operator's, not the firm's. Any
   use of the API is a purchase and needs the operator's approval.
4. **Smaller items.** N3: the engine's optional reset path keeps the rebill date fixed, while the firm moves it 30
   days on. That over-bills, but no registered run uses the path. C3 matters only to CL, metals or MBT work. N4 and
   N5 inform `xfa_closure_at_request` and the operator's setup; they change nothing modelled.

**Open, as before.** `xfa_closure_at_request` and `xfa_seat_frees_at` are still not stated on any official page, so
the engine's abandon and same-evening-seat conventions stay declared assumptions (D-336, D-353). Lucid's prices could
not be re-read by an agent; they rest on the operator's screenshots of 2026-11-05 (D-31). The ledger under `vendor/`
is read-only. Under E-002, recording any of the above means a new decision row in this repository, or a new Stage 2
snapshot.
