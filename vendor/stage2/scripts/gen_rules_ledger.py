"""Generate RULES_LEDGER.md's tables from config/rules.yaml.

The ledger is a generated artefact. `tests/test_rules_ledger_agreement.py` compares the two files
field by field in both directions, and hand-maintaining 35 rows across two files is exactly how
they drift -- so the Markdown is produced from the yaml, and the test then checks the generated
artefact against its source.

The prose above the first `## A.` heading is preserved; everything from there down is rewritten.

Run: python scripts/gen_rules_ledger.py
"""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
YAML = ROOT / "config" / "rules.yaml"
MD = ROOT / "RULES_LEDGER.md"

MD_STATUS = {
    "verified": "verified",
    "carried_from_stage_one_reverify": "carried from stage one — RE-VERIFY",
    "unverified_human_input_required": "UNVERIFIED — HUMAN INPUT REQUIRED",
    "third_party": "third-party",
}

TITLE = {
    "combine_profit_target": "Combine profit target (50K)",
    "combine_mll": "Combine maximum loss limit, trailing",
    "combine_consistency_max_day_frac": "Combine consistency rule",
    "combine_mll_lock_at": "Combine MLL locks at starting balance",
    "combine_count_limit": "Number of Combines",
    "combine_position_size_limit": "50K Combine maximum position size",
    "xfa_mll_start": "Funded MLL starting offset",
    "xfa_lock_at": "Funded floor lock; $0 permanently after each payout",
    "xfa_std_winning_days": "Standard path: winning days required",
    "xfa_std_winning_day_min": "Standard path: what counts as a winning day",
    "xfa_std_cap": "Standard payout cap (no-DLL)",
    "xfa_cons_min_days": "Consistency path: trading days required",
    "xfa_cons_max_day_frac": "Consistency path: best day share",
    "xfa_cons_cap": "Consistency payout cap (no-DLL)",
    "payout_min": "Minimum payout request",
    "payout_max_frac_of_balance": "Payout capped at a share of balance",
    "profit_split": "Profit split to the trader",
    "require_profit_since_payout": "Later Standard payouts need net > $0 since the last payout",
    "subscription_fee": "Combine subscription (Standard path)",
    "billing_days": "Subscription billing period, ENGINE UNITS",
    "billing_period_calendar_days": "Subscription billing period, OFFICIAL UNITS",
    "activation_fee": "Funded account activation (Standard path)",
    "reset_fee": "Combine reset (Standard path)",
    "payout_fee": "Per-payout processing fee",
    "max_active_funded_accounts": "Maximum active funded accounts",
    "hold_queue_behaviour": "A pass at the cap waits; fee due on activation",
    "hold_expiry_days": "Does a pass on hold expire?",
    "multi_account_same_strategy": "One strategy across several accounts; copy trading",
    "funded_scaling_entry_tier_minis": "Funded scaling plan: ENTRY tier only",
    "funded_scaling_plan": "Funded scaling plan: the full tier ladder",
    "scaling_tier_after_payout": "Does the tier fall back when a payout cuts the balance?",
    "payout_methods_and_fees": "Payout methods, fees and processing time",
    "payout_lag_days_aeropay": "Payout lag, Aeropay (US baseline), ENGINE UNITS",
    "payout_lag_days_ach": "Payout lag, ACH (conservative US), ENGINE UNITS",
    "payout_fee_ach": "Per-payout processing fee, ACH",
    "dll_offer_status": "Daily Loss Limit offer status",
    "permitted_products": "Permitted products and hours",
    "cross_account_hedging": "Cross-account hedging",
    "prohibited_trading_strategies": "Prohibited Trading Strategies",
    "prohibited_conduct": "Prohibited Conduct",
    "responsible_trading_program": "Responsible Trading Program",
}

GLOSS = {
    "combine_profit_target": "$3,000",
    "combine_mll": "$2,000",
    "combine_consistency_max_day_frac": "55 % — official; third-party guides say 50 %",
    "combine_mll_lock_at": "lock at 0",
    "combine_count_limit": "no limit",
    "combine_position_size_limit": "minis; 50 micros at 10:1 — **source conflict, see note**",
    "xfa_mll_start": "−$2,000",
    "xfa_lock_at": "",
    "xfa_std_winning_days": "days of $150+ net",
    "xfa_std_winning_day_min": "$150",
    "xfa_std_cap": "$2,000 → **$4,000 with the DLL**",
    "xfa_cons_min_days": "trading days",
    "xfa_cons_max_day_frac": "40 %",
    "xfa_cons_cap": "$3,000 → **$6,000 with the DLL**",
    "payout_min": "$125",
    "payout_max_frac_of_balance": "50 % of balance",
    "profit_split": "90 / 10",
    "require_profit_since_payout": "first payout exempt",
    "subscription_fee": "$49/mo — **$95 on the No-Activation-Fee path**",
    "billing_days": "**trading days** — = 30 calendar days; propsim D-31 stands",
    "billing_period_calendar_days": "**the official figure**",
    "activation_fee": "$149 — **$0 on the No-Activation-Fee path**",
    "reset_fee": "$49 — often free via banked Reset Credits",
    "payout_fee": "$0 Aeropay/Wise/P2B; **$30 ACH and wire**",
    "max_active_funded_accounts": "an LFA also blocks activation",
    "hold_queue_behaviour": "not forfeited; duration not stated",
    "hold_expiry_days": "HUMAN INPUT REQUIRED",
    "multi_account_same_strategy": "first-party Trade Copier; six restrictions",
    "funded_scaling_entry_tier_minis": "minis at a $0 balance = 20 micros — **textually quoted**",
    "funded_scaling_plan": 'read from the chart image, screenshot in `docs/evidence/` — **D-32**; the unsourced D-28 thresholds were withdrawn by D-31',
    "scaling_tier_after_payout": '**page-verified 2026-09-27**: "If a Payout reduces your balance to a lower tier, your maximum contract size decreases accordingly." — **couples payout policy to sizing**; source moved from 8284223',
    "payout_methods_and_fees": "fee and lag are one joint method choice",
    "payout_lag_days_aeropay": "trading days; **derived** slow-end sum: approval 1-3 + instant; pairs with `payout_fee` 0.0",
    "payout_lag_days_ach": "trading days; **derived** slow-end sum: approval 1-3 + transfer 1-3; pairs with `payout_fee_ach`",
    "payout_fee_ach": "$30 ACH and wire; pairs with the 6-day lag — ($30, 3) does not exist",
    "dll_offer_status": "doubles BOTH caps; expiry announced off the help centre",
    "prohibited_trading_strategies": "7 strategies + SIM-fill examples",
    "prohibited_conduct": "19 items; catch-all unchanged",
    "responsible_trading_program": '6 triggers — **trigger 1 bites a correlated campaign**; placement follows a Risk Team review (warnings often first, direct placement on severity); **the only exit is through a Live Funded Account with $10,000 of LFA profit, and Live closes every XFA, so in an XFA campaign placement is permanent**; in RTP a −$1,000 DLL (50K) goes on **every new Combine, a reset Combine and every new XFA**, including an XFA from a Combine bought before placement; new XFAs are Consistency-only **except** those from a Combine bought before placement, which may be Standard or Consistency; a Standard XFA active at placement is unaffected',
}

HEAD = (
    "| key | rule | value | official article id and URL | date read | verified by | status |\n"
    "|---|---|---|---|---|---|---|"
)


def canonical(value) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return repr(value)
    return str(value)


def row(key: str, entry: dict) -> str:
    cite = " — ".join(
        x for x in [str(entry.get("article_id") or ""), entry.get("url") or ""] if x
    ) or "—"
    gloss = GLOSS.get(key, "")
    value = canonical(entry["value"]) + (f" ({gloss})" if gloss else "")
    return (
        f"| `{key}` | {TITLE.get(key, key)} | {value} | {cite} | "
        f"{entry.get('date_read') or '—'} | {entry.get('verified_by') or '—'} | "
        f"{MD_STATUS[entry['status']]} |"
    )


def main() -> int:
    rules = yaml.safe_load(YAML.read_text(encoding="utf-8"))["rules"]
    missing = [k for k in rules if k not in TITLE]
    if missing:
        raise SystemExit(
            f"add a TITLE (and ideally a GLOSS) for new rule key(s): {missing}"
        )

    verified = [k for k in rules if rules[k]["status"] == "verified"]
    unverified = [k for k in rules if rules[k]["status"] != "verified"]

    doc = MD.read_text(encoding="utf-8")
    head = doc[: doc.index("## A.")]

    body = f"""## A. Verified — read on the official help centre in T1, 2026-09-22

{len(verified)} of {len(rules)} rules. Read by the **rules-verifier** agent, each quote fetched two to
four times with differently-worded prompts; the load-bearing ones were independently spot-checked in
the session. Full quotes are in the `note` of each key in [`config/rules.yaml`](config/rules.yaml).

Two rows were re-read on 2026-09-27 (T11). Each page's raw HTML was fetched twice, with identical text both
times, and quoted from the article body rather than through a summarising tool. The two rows are
`scaling_tier_after_payout`, now page-verified on 8284233, and `responsible_trading_program`, whose note now
states the scope of the RTP daily loss limit. The behavioural rules read the same day are in §C.

One row was re-read on 2026-10-01: `responsible_trading_program`. The page had been edited since 2026-09-27. Its note
now records how the program ends (only through a Live Funded Account, which closes every XFA) and that placement
follows a Risk Team review (D-219).

{HEAD}
{chr(10).join(row(k, rules[k]) for k in verified)}

### Rows that need reading carefully

**`billing_days` is in TRADING days** because that is the engine's index;
`billing_period_calendar_days` carries the official 30-calendar-day figure. Conflating them caused a
real error — see D-29.

**The scaling plan is verified in full.** The 50K ladder (`funded_scaling_plan`: below $1,500 → 2 lots,
$1,500–$2,000 → 3, above $2,000 → 5) was read from the chart image on 8284223. The screenshot is saved at
`docs/evidence/8284223_scaling_plan_2026-09-22.png` (D-32), after D-31 withdrew the unsourced D-28 thresholds.
The entry tier also rests on the article's own textual example, *"$50K XFA, 2-lot Scaling Plan: 2 Minis, OR 20
Micros, OR Any combo equal to 2 Minis"*. The fall in tier after a payout (`scaling_tier_after_payout`) is stated in
text on 8284233 (re-read 2026-09-27): *"If a Payout reduces your balance to a lower tier, your maximum contract
size decreases accordingly."*

**The Combine and the XFA lock their days at different times.** A Combine day locks at 3:10 PM CT (8284208) and an
XFA day at 4:00 PM CT (8284233); see §C.

## B. Not verified — blockers

{HEAD}
{chr(10).join(row(k, rules[k]) for k in unverified)}

As of 2026-09-27 every key in `config/rules.yaml` is verified. The scaling ladder was read from the chart image
(D-32), and the tier after a payout is page-verified on 8284233 (2026-09-27), so neither is open any more.

`hold_expiry_days` is marked "not required under D-34". That is a design fact, not a rule reading. The firm's own
behaviour is still unstated: 8284215, re-read 2026-09-27, says only *"If you pass a Trading Combine® while at the
limit, the new XFA goes on hold until one closes."* The question reopens if D-34 is relaxed (PARKING_LOT.md).

## C. Behavioural rules with no configurable parameter

Quotes are verbatim. Rows dated 2026-09-27 were read from each page's raw HTML, fetched twice with identical text
(T11).

| rule | how it is encoded | article id | date read |
|---|---|---|---|
| **Combine day lock: 3:10 PM CT.** "Your best day updates throughout the session as your P&L moves. At 3:10 PM CT, that day's value locks into your trading history and cannot be changed." Same-day profit adds to the best day: "If your best day was set during the current trading session (before 3:10 PM CT), any additional profit you earn today adds directly to that best day total — which raises your adjusted Profit Target even further." The trading day (8284197): "The trading day runs from 5:00 PM CT through 3:10 PM CT the next calendar day." | Pass checked at the engine day's close. Code comments call that close "16:00 CT", which is **wrong for the Combine**. There is no numeric effect on a path that is flat by 3:10 PM CT, because nothing trades between 3:10 PM and 5:00 PM CT | 8284208; 8284197 | 2026-09-27 |
| **XFA day lock: 4:00 PM CT, both payout paths.** Standard: "A day locks in at 4:00 PM CT." Consistency: "Days lock in at 4:00 PM CT." | lock at 16:00 CT (matches) | 8284233 | 2026-09-27 |
| MLL trails end-of-day balance; breach real-time incl. unrealised | ratchet at lock, truncate at floor | 8284204 | 2026-09-22 |
| The payout day does not count as a winning day | payout resets the counter | 8284233 | 2026-09-22 |
| **Payout request day, all account types.** "Please note: the trading day your Payout is requested will not count toward your winning days for the next Payout cycle. The trading day runs from 5:00 PM CT to 3:10 PM CT the following day. A request submitted after 5:00 PM CT belongs to the next trading day — that day becomes the Payout request day and is excluded from the new cycle. This applies to all account types." Example: "A Payout request submitted at 5:59 PM CT on Monday belongs to the Tuesday trading session. Tuesday is the Payout request day and does not count. The new cycle begins on Wednesday." Availability: "Available during CME market hours: Sunday 5 PM CT – Friday 5 PM CT (excluding holidays)". FAQ: "please keep in mind the Payout processing times to determine which trading day will not count toward winning day objectives." | **Not yet modelled** (T11 engine fix). The engine requests at the close of the eligible day, after its 16:00 CT lock, and counts the next day toward the new cycle (`propedge/campaign/lockstep.py`). That matches the page only for a request placed after the 4:00 PM CT lock and before 5:00 PM CT. A request after 5:00 PM CT loses one more trading day per cycle. **UNVERIFIED:** whether a request can be placed between 4:00 and 5:00 PM CT, since the page does not say whether that daily halt is inside "CME market hours"; and what the FAQ's processing-time sentence adds to the request-day rule | 8284233 | 2026-09-27 |
| **XFA inactivity.** "XFAs with no trading activity for more than 30 days may be closed. XFAs can't be put on hold." | **Not modelled.** Binds only if an XFA goes more than 30 days without a trade. The page does not say whether these are calendar or trading days | 8284215 | 2026-09-27 |
| **RTP consequences and their scope** (full quotes in `responsible_trading_program`'s note). "All new Trading Combines® and XFAs automatically get a Daily Loss Limit (DLL):" / "50K accounts = -$1,000". A reset Combine "will be a Consistency Trading Combine account with a Daily Loss Limit (DLL)". A Combine bought before placement "may be activated as either a Standard XFA or Consistency XFA", and "XFAs activated from Trading Combines purchased before your RTP placement can be Standard or Consistency with a Daily Loss Limit." An XFA already active: "Your existing Standard XFA account is unaffected." | **Partly modelled** (D-145): the DLL on Combines bought after placement, and Consistency-only XFAs after placement. **Not applied:** the DLL on funded accounts activated after placement, and on a Combine reset during RTP (audit finding 1). The path is decided on the activation day, not the Combine's purchase day, so a Combine bought before placement is wrongly forced onto Consistency (finding 2). T11 engine fixes | 13620045 | 2026-09-27 |
| Back2Funded ($599 at 50K, max 2, pre-first-payout, 30-day window) | not modelled; parked | 12060405 | 2026-09-22 |
| **Price lock limit (Prohibited Conduct).** "Holding a position within 2% of a product’s price lock limit — see How to Ensure I Am Not Trading Within 2% of a Price Limit". Responses listed for any Prohibited Conduct violation: "Warning"; "Deletion of the impacted trading day"; "Account Reset"; "Permanent account closure"; "Delay or denial of a Payout request". "Violations are reviewed case-by-case based on severity and history." The linked article (8284225, last updated 2026-05-29): "Price limits are calculated from the previous day’s settlement price. They update at 4:05 PM CT after each session and vary by product, contract month, and time of day."; "Stop trading above: Settlement × (1 + Price Limit% − 2%)"; "Stop trading below: Settlement × (1 − Price Limit% + 2%)"; "Example: 5% limit → stop trading at 3% net change. 7% limit → stop trading at 5% net change."; "Update: Equity products ES, MES, NQ, MNQ, RTY, M2K, YM, and MYM overnight price limits have expanded from 5% to 7%." | **Not modelled by the engine.** IM2 flags ES trades whose lowest price held reaches the prior close x 0.95 and forfeits their gains (P-04 §3, D-172); CL, NG and 6E have dynamic circuit breakers, not a lock | 10296582; 8284225 | 2026-09-27 |
| Max contracts do not increase mid-session | scaling tier fixed within a session | 8284223 | 2026-09-22 |
| **Temporary position-limit adjustments** (last updated 2026-09-24). "During extreme volatility, we may temporarily tighten position limits on affected products." Current restrictions for the Trading Combine and XFA, 50K / 100K / 150K: "Crude Oil (CL) = 3/6/9", "Micro Crude Oil (MCL) = 30/60/90", "E-Mini Crude Oil (QM) = 3/6/9", "RBOB Gasoline (RB) = 3/6/9", "Heating Oil (HO) = 3/6/9", "Gold (GC) = 3/6/9", "Micro Gold (MGC) = 30/60/90", "Silver (SI) = 0", "Micro Silver (SIL) = 2/4/6", "Copper (HG) = 0", "Micro Copper (MHG) = 2/4/6", "Platinum (PL) = 0". "For Express Funded Accounts, position limits for restricted products have a ceiling of the contracts listed above (CL = 3/6/9, for example)." "However, a trader's actual limit may be lower depending on their current account balance, as the Scaling Plan applies independently." For the 50K XFA on CL, QM, MCL, HO, RB, GC, MGC and SIL: "Below $1500 balance = 1 contract", "$1,500 balance = 1 contract", "$2,000 balance = 3 contracts". "Temporary: Restrictions remain in place only while volatility levels are elevated" | **Not modelled. First recorded 2026-09-27, outside T11's list.** It bears on IM2's CL leg, traded as MCL: the 50K Combine ceiling is 30 micros, not 50, and the 50K XFA ladder for restricted symbols is 1 / 1 / 3, not 2 / 3 / 5. **UNVERIFIED:** whether "1 contract" means one mini-equivalent (10 MCL), and how long the restriction lasts. MNG, MES and M6E are not listed | 13613539 | 2026-09-27 |

### Reference readings: not rules, recorded for T11

| reading | used for | article id | date read |
|---|---|---|---|
| **Economic releases Topstep lists** ("Common Economic Releases", last updated 2026-09-10). Verbatim, as [Release; Time (CT); Products Affected]: ["Unemployment Rate"; "7:30 AM"; "ES, NKD, NQ, 6A, 6B, 6C, 6E, 6J, 6S, E7, GE, YM, UB, ZT, ZF, ZN, ZB, GC, RTY, SI, HG, TN, 6M, M6A, M6E, 6N, MBT, MET"], ["FOMC Statement"; "1:00 PM"; "All products"], ["Crude Oil Inventories (EIA)"; "9:30 AM / 10:00 AM\\*"; "CL, QM, MCL, RB"], ["Natural Gas Inventories (EIA)"; "9:30 AM"; "NG, QG"], ["Crop Production"; "11:00 AM"; "ZC, ZS, ZW, ZM, ZL"]. Footnotes: "\\*Pending abbreviated trading hours. Times are subject to change — Traders are responsible for knowing what releases are scheduled and when." and "\\*\\*Micro contracts also apply." Conduct: "Topstep doesn't require you to flatten positions during economic releases — in SIM or Funded Accounts."; "Trades impacted by economic releases are not eligible for exceptions or Reset credits" | The source list for IM2's release calendar (T11). Only these five releases are listed: no CPI, GDP, retail sales, jobless claims or ISM. The only prohibition tied to news is 10305426's "Purposefully trading your full Maximum Position Size directly into a scheduled major news event." No page read lists what counts as a "major news event" | 8284211; 10305426 | 2026-09-27 |
| **CPI window restriction**, enforced by TopstepX (13613539). "Ahead of Consumer Price Index (CPI) releases, Topstep temporarily restricts new opening transactions on equity index products (ES, RTY, YM, NQ, NKD) in SIM to protect Traders from extreme volatility." "Minis (ES, RTY, YM, NQ, NKD, GC, SI, HG, PL): No new opening transactions permitted during the 10-minute window surrounding the release (5 minutes before, 5 minutes after)." "Micros (MES, M2K, MYM, MNQ, MGC, SIL, MHG): Opening transactions limited to 1, 3, 6, 9, and 15 contracts for the $25K, $50K, $100K, $150K, and $250K account sizes, respectively, during the window" "Non-equity/metals products (energies, rates, FX, etc.) are unaffected." The page does not state the release time; it refers to positions held "prior to 7:25 AM CT" | The release calendar: at 50K, MES opening size is capped at 3 in the window. Not modelled | 13613539 | 2026-09-27 |
| **MCL and MNG round turns after the 2026-10-01 fee rise** (8284213, displayed "Updated yesterday" when read 2026-10-01). The table now reads "Micro Crude Oil (MCL)" / "$1.72" and "Micro Henry Hub Natural Gas (MNG)" / "$1.92" (column "Total Round-Turn Cost (RT)"); "E-mini S&P 500 (ES)" / "$3.78", "Micro E-mini S&P 500 (MES)" / "$1.22", "E-mini NASDAQ 100 (NQ)" / "$3.78", "Micro E-mini NASDAQ 100 (MNQ)" / "$1.22" and "Micro EUR/USD (M6E)" / "$1.00" unchanged. The notice is still shown, same wording: "Exchange fee increase starting the October 1, 2026 trading day", "MCL: $0.50 to $0.60 per side ($1.20 round turn)", "MNG: $0.60 to $0.70 per side ($1.40 round turn)", "That's $0.10 more per side." Reads of 2026-09-26, 2026-09-27 and 2026-09-30 showed "$1.52" and "$1.72" and no post-change total | **Stated totals equal the derived floors.** `config/fills.yaml` has carried MCL 1.72 and MNG 1.92 since 2026-09-30 as P-04's derived floors (D-209); from this read they are the page's stated totals, values unchanged. Each decomposes into the new exchange fee ($1.20 / $1.40 round turn) + the $0.02 NFA fee + the $0.50 micro commission | 8284213 | 2026-10-01 |
"""
    MD.write_text(head + body, encoding="utf-8", newline="\n")
    print(f"RULES_LEDGER.md regenerated: {len(verified)} verified, {len(unverified)} not")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
