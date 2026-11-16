"""Build firms/lucid.json from today's re-read of Lucid's help centre (quotes checked by check_quotes.py)."""
import json
import os
import sys

S = sys.argv[1]
B = "https://support.lucidtrading.com/en/articles/"
pages = {
    "12945790": ("12945790-lucidflex-evaluation-account", "Updated over a month ago"),
    "12945815": ("12945815-lucidflex-drawdown", "August 26, 2026"),
    "12945795": ("12945795-lucidflex-funded-account", "October 13, 2026"),
    "12945796": ("12945796-lucidflex-payouts", "July 28, 2026"),
    "12945805": ("12945805-lucidflex-consistency", "Updated over a month ago"),
    "11404617": ("11404617-maximum-number-of-accounts", "August 26, 2026"),
    "11404728": ("11404728-other-trading-activities", "Updated today (2026-11-15)"),
    "11404734": ("11404734-hedging", "Updated today (2026-11-15)"),
    "16558826": ("16558826-new-live-structure", "October 14, 2026"),
}


def q(pid, text):
    slug, date = pages[pid]
    return {"file": f"raw/lucid/{pid}.txt", "url": B + slug, "article_id": slug, "page_date": date, "text": text}


def T(value, quotes, note=None, status="verified", looked_at=None):
    t = {"value": value, "status": status, "quotes": quotes}
    if note:
        t["note"] = note
    if looked_at:
        t["looked_at"] = looked_at
    return t


STAGE2 = "Stage 2's vendored ledger vendor/stage2/vendor/propfirms/firms/lucid-trading/rules.yaml"
terms = {
    "eval_profit_target": T(3000, [q("12945790", "| Account Size | Profit Target | Max Loss Limit | Consistency % | Max Size"),
                                   q("12945790", "| $50,000 | $3,000 | $2,000 | 40% (50% with add-on) | 4 mini or 40 micros")]),
    "eval_drawdown_amount": T(2000, [q("12945815", "| Account Size | MLL Amount | Initial Trail Balance | Locked MLL Balance"),
                                     q("12945815", "| $50,000 | $2,000 | $52,100 | $50,100")]),
    "eval_drawdown_type": T("eod_trailing", [q("12945815", "LucidFlex evaluation and funded accounts use an End-of-Day Drawdown (EOD Drawdown) system to calculate the Max Loss Limit (MLL).")]),
    "eval_drawdown_lock": T("locks at start + $100 ($50,100) once the balance exceeds $52,100",
                            [q("12945815", "Once your account exceeds the Initial Trail Balance, the MLL locks and no longer moves"),
                             q("12945815", "Once the account exceeds the trail, the MLL locks at the initial balance plus $100")]),
    "eval_daily_loss_limit": T("optional at checkout (modelled off)", [q("12945790", "Customize at checkout: Daily Loss Limit On or Off, and 40% or 50% consistency (see LucidFlex Customization)")]),
    "eval_consistency_rule": T("40% (50% paid add-on); gates the upgrade, not a breach",
                               [q("12945805", "In LucidFlex evaluation accounts your Consistency Percentage must be 40% or less to be eligible to upgrade to a LucidFlex funded account."),
                                q("12945805", "Largest Single Day Profit / Account Profit = Consistency Percentage")]),
    "eval_min_days": T(3, [q("12945790", "Pass in as few as 3 days with 40% consistency, or 2 days with the 50% consistency add-on")]),
    "eval_position_limit": T("4 minis / 40 micros", [q("12945790", "| $50,000 | $3,000 | $2,000 | 40% (50% with add-on) | 4 mini or 40 micros")]),
    "eval_fee": T("one-time; $115.50 with the recurring coupon (list $165), DLL off, 40% -- Stage 2 D-575 (operator screenshots 2026-11-05)",
                  [q("12945790", "One-time fee, no monthly rebilling, take as long as you need to pass")],
                  note="The billing basis is re-read today; the price is not (lucidtrading.com serves a Cloudflare challenge to an honest client, not worked around). The price is Stage 2's verified row (D-575, the multi-firm repository's D-31): " + STAGE2 + " eval_fee."),
    "eval_reset_fee": T("$115 (Stage 2 D-575)", [], status="verified in Stage 2, not re-read today",
                        looked_at="lucidtrading.com unreadable today; " + STAGE2 + " eval_reset_fee"),
    "activation_fee": T("none", [q("12945790", "No activation fees to upgrade to funded account")]),
    "eval_count_limit": T("10 evaluations per household; 10 accounts in total",
                          [q("11404617", "Account Limit: Up to 10 active evaluation accounts per household or family."),
                           q("11404617", "Shared Limit: Traders may hold a maximum of 10 accounts in total across evaluation accounts and funded accounts.")]),
    "eval_time_limit": T("none", [q("12945790", "One-time fee, no monthly rebilling, take as long as you need to pass")]),
    "funded_type": T("sim funded; up to 5 payouts per account, then the live review pool (discretionary)",
                     [q("12945796", "Number of requests per account: Traders may take up to 5 payouts from each LucidFlex account after which they will be moved live."),
                      q("16558826", "All live transitions occur at the discretion of the Lucid risk team.")]),
    "funded_drawdown_amount": T(2000, [q("12945795", "| $50,000 | $2,000 | Optional | Yes | 4 mini or 40 micros")]),
    "funded_drawdown_type": T("eod_trailing", [q("12945795", "LucidFlex funded accounts have an optional Daily Loss Limit, no consistency rule and no payout buffer. 90/10 profit split. EOD trailing drawdown.")]),
    "funded_drawdown_lock": T("locks at start + $100", [q("12945815", "Once the account exceeds the trail, the MLL locks at the initial balance plus $100")]),
    "payout_balance_consequence": T("a payout request forces the lock at $50,100", [q("12945815", "Once you request a payout from LucidFlex, your MLL automatically adjusts to the Locked MLL Balance")]),
    "funded_daily_loss_limit": T("optional, chosen at evaluation purchase", [q("12945795", "The ability to customize whether each Flex Funded account has a Daily Loss Limit at the time of evaluation purchase")]),
    "funded_consistency_rule": T("none", [q("12945795", "There is no Consistency Percentage on LucidFlex funded accounts")]),
    "funded_position_limit": T("4 minis / 40 micros, with a scaling plan (tiers: Stage 2's row funded_position_limit, article 12945808, not re-read today)",
                               [q("12945795", "| $50,000 | $2,000 | Optional | Yes | 4 mini or 40 micros")]),
    "funded_monthly_fee": T(None, [], status="UNVERIFIED",
                            looked_at="12945795, 12945796 today; Stage 2 D-561/D-575 found no official statement either way (charged at zero; every Lucid result labelled an upper bound)"),
    "payout_min": T(500, [q("12945796", "Minimum payout request: $500")]),
    "payout_cap": T("50% of profit up to $2,000 per request; does not scale; 5 requests per account",
                    [q("12945796", "| $50,000 | 50% of Profit up to $2,000"),
                     q("12945796", "Unlike our other prop firm funded accounts, the maximums here do not scale up with more payouts. The table above shows the payout maximums for all requests.")],
                    note="The same page also says 'Futures traders may request 50% of their account balance up to a maximum dollar amount' (Stage 2 D-561 (3): the table reading is modelled, the other reported beside)."),
    "payout_frequency_gate": T("any day; per cycle 5 days of >= $150 profit and net profit > 0",
                               [q("12945796", "Traders must earn at least the minimum required profit on 5 separate days during the payout cycle. The minimum profit on trading days reset and must be earned again after every approved payout."),
                                q("12945796", "| $50,000 | $150"),
                                q("12945796", "There is no fixed payout window, you may request a payout any day after meeting all eligibility criteria.")]),
    "payout_split": T(0.90, [q("12945796", "All LucidFlex funded account payouts are split 90% to the trader and 10% to Lucid Trading.")]),
    "payout_processing_days": T("within 2 business days", [q("12945796", "Payouts will be disbursed to your payment method within 2 business days.")]),
    "payout_fee": T(None, [], status="UNVERIFIED", looked_at="12945796 today (no fee stated); Stage 2 D-561"),
    "payout_count_limit": T(5, [q("12945796", "Number of requests per account: Traders may take up to 5 payouts from each LucidFlex account after which they will be moved live.")]),
    "max_accounts": T("5 funded per household", [q("11404617", "Account Limit: Up to 5 active funded accounts per household or family.")]),
    "inactivity_rule": T(None, [], status="UNVERIFIED",
                         looked_at="not re-read today; the multi-firm repository's D-07 recorded a 30-day inactivity deletion -- a lead, to be re-read before use"),
    "copy_trading_terms": T("permitted", [q("11404728", "Automated trading systems and trade copiers are permitted")]),
    "cross_account_hedging": T("prohibited, including across firms and correlated assets (ES against NQ)",
                               [q("11404734", "Hedging between different firms or funded platforms"),
                                q("11404734", "Example: You cannot go long ES in one account and short NQ in a separate account.")]),
    "news_trading_terms": T("allowed on Flex", [q("11404728", "Traders may enter or exit positions around scheduled or unscheduled news events on these plans without it being a breach")]),
    "automation_terms": T("permitted (no bearing on hand entry)", [q("11404728", "Automated trading systems and trade copiers are permitted")]),
    "sizing_or_gambling_terms": T("martingaling discouraged; scaling in allowed",
                                  [q("11404728", "While scaling is permitted, martingaling, continuously adding to losing positions in hopes of recovery, is strongly discouraged")]),
    "other_conduct_bearing": T("the live move closes every sim account in the household",
                               [q("16558826", "All simulated prop accounts are closed when a trader is moved live, or opts out of trading live via cash-out.")]),
}
screen = {
    "drawdown_eval": terms["eval_drawdown_type"], "drawdown_funded": terms["funded_drawdown_type"],
    "consistency_eval": terms["eval_consistency_rule"], "consistency_funded": terms["funded_consistency_rule"],
    "max_funded_accounts": terms["max_accounts"], "copy_trading": terms["copy_trading_terms"],
    "opposite_positions": terms["cross_account_hedging"], "news": terms["news_trading_terms"],
    "automation": terms["automation_terms"], "sizing_gambling": terms["sizing_or_gambling_terms"],
    "verdict": "PASS",
    "verdict_reason": "EOD trailing funded drawdown locking at start + $100, no funded consistency, 5 funded per household; hand entry unrestricted (already Stage 2's verified second firm, D-561/D-575).",
}
d = {"firm": "Lucid Trading", "slug": "lucid", "official_domains": ["lucidtrading.com", "support.lucidtrading.com"],
     "date_read": "2026-11-15",
     "unreadable": [{"url": "https://lucidtrading.com/", "what": "Cloudflare challenge ('Just a moment...') to an honest client; not worked around (as Stage 2 D-561)"}],
     "plans_seen": [], "plan_captured": "LucidFlex 50K (Stage 2's verified second firm; re-read today)",
     "screen": screen, "terms": terms}
with open(os.path.join(S, "firms", "lucid.json"), "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
print("ok")
