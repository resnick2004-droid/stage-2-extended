# Reader brief: futures prop-firm rules, read on each firm's own pages (Q-12, 2026-11-15)

You read official web pages of futures prop-trading firms and record their contract terms with verbatim quotes.
Today is 2026-11-15. Scratch root (call it S):
`C:/Users/resni/AppData/Local/Temp/claude/197752aa8b2362c7/9862c1b3-c57d-4498-a2d7-44492c7a25e6/scratchpad/wt-firms`

## Hard limits (breaking one voids the work)

- **Official pages only**: the firm's own domain(s), its own help centre (Intercom/Zendesk/HelpScout/GitBook hosts the
  firm links to from its own site count), its own Terms of Use / rules PDF. Never a review site, affiliate page, forum,
  Reddit, YouTube, Trustpilot, a prop-firm comparison site, a search-engine snippet or a cached copy elsewhere. A
  search engine may be used only to *locate* an official URL; its text is never evidence.
- **Never** sign up, log in, fill or submit any form, open a chat widget, start a checkout, click "buy", enter a
  coupon, or send any personal information anywhere. Read only public pages with GET requests.
- **Never work around a block.** If a host serves a Cloudflare challenge or "you have been blocked" (403/503), record
  it as unreadable. Do not change the user agent, do not use a browser tool, do not use a cached/mirror copy. You may
  try the WebFetch tool once on that URL (it is a declared reader, not a disguise); if it is refused too, the host is
  unreadable and its rules are UNVERIFIED.
- Write nothing anywhere except files under `S/raw/<slug>/` (via the fetch script) and `S/firms/<slug>.json`.
  Never touch any git repository.

## How to read a page

Fetch with the script (Git Bash): `bash "S/tools/fetch.sh" <slug> <short-name> "<url>"`. It saves the raw HTML,
`S/raw/<slug>/<short-name>.txt` (visible text; tables as `| a | b |` rows), `<short-name>.scripts.txt` (inline script
bodies, where JavaScript sites keep their text) and logs the URL. Then read or grep the `.txt` (and the `.scripts.txt`
if the `.txt` is nearly empty). Help centres usually list their collections on the front page; follow links from
there (grep the raw `.html` for `href=` to find article URLs). Fetch at a gentle pace (the script waits a second).

Only if a page's text is in neither file (JavaScript-rendered with nothing server-side) use WebFetch, **twice with
differently worded prompts** asking for the exact wording, and use the quote only if both agree word for word; such a
quote's `"file"` is `"webfetch"`.

## What to find, per firm

The comparable product is the firm's **$50,000 futures evaluation** (or the size nearest $50K) on CME equity index
futures (NQ/MNQ, ES/MES): an evaluation, then a funded (usually simulated) account that pays out. If the firm sells
several $50K plans (e.g. intraday-trailing vs end-of-day, one-step vs instant), list each plan briefly in
`plans_seen` with its drawdown type and consistency rule, then capture full terms for **the one plan that best
passes the screen** (if two plans pass and differ materially, capture both, as separate `terms_<plan>` blocks).

### The screen (every firm)

1. drawdown type, evaluation and funded: end-of-day (EOD) trailing, intraday trailing, or static -- and any lock;
2. consistency rule, evaluation and funded (the percentage and what it gates);
3. how many funded accounts can be held at once (and evaluations; per person or per household);
4. conduct rules that bear on a design that holds several accounts and trades by hand: copying trades across own
   accounts (trade copiers), opposite positions across accounts (hedging), news trading, **automated or API order
   entry** (our trades are entered by hand -- record what the firm says about bots/automation either way), and any
   "gambling", all-in, maximum-size, or minimum-hold/scalping rules;
5. verdict: **PASS** if (EOD drawdown on the funded account OR no consistency rule) AND several funded accounts allowed
   AND no rule forbids hand-entered, one-position-at-a-time bracket trading (a stop and a target placed with the
   entry) on NQ/MNQ; **FAIL** with the one-line reason; **UNDETERMINED** if the pages needed cannot be read.

### Full terms (firms that PASS), each its own entry

`eval_profit_target`, `eval_drawdown_amount`, `eval_drawdown_type`, `eval_drawdown_lock`, `eval_daily_loss_limit`,
`eval_consistency_rule`, `eval_min_days`, `eval_position_limit`, `eval_fee` (price and whether one-time or monthly),
`eval_reset_fee`, `activation_fee`, `eval_count_limit`, `eval_time_limit`;
`funded_type` (sim or live; what happens after N payouts), `funded_drawdown_amount`, `funded_drawdown_type`,
`funded_drawdown_lock`, `payout_balance_consequence` (where the floor sits after a payout), `funded_daily_loss_limit`,
`funded_consistency_rule`, `funded_position_limit` (and any scaling plan, tier by tier), `funded_monthly_fee`,
`payout_min`, `payout_cap` (per request and lifetime), `payout_frequency_gate` (days, winning-day thresholds,
buffers), `payout_split`, `payout_processing_days`, `payout_fee`, `payout_count_limit`, `max_accounts`,
`inactivity_rule`; conduct entries `copy_trading_terms`, `cross_account_hedging`, `news_trading_terms`,
`automation_terms`, `sizing_or_gambling_terms`, `other_conduct_bearing`, `permitted_products`.

A term no official page states is **UNVERIFIED** -- a successful outcome. Say what you looked at (`looked_at`).
Absence of a rule on a page is not a statement that the rule is absent, unless the page says so ("no consistency
rule", "None").

## The output: `S/firms/<slug>.json` (UTF-8 JSON, one per firm)

```json
{
  "firm": "Firm Name",
  "slug": "slug",
  "official_domains": ["firm.com", "help.firm.com"],
  "date_read": "2026-11-15",
  "unreadable": [{"url": "https://...", "what": "403 Cloudflare block; WebFetch refused too"}],
  "plans_seen": [{"name": "Plan 50K", "drawdown": "EOD trailing, locks at start+$100", "consistency_eval": "40%",
                  "consistency_funded": "none", "quote": {"file": "raw/slug/page.txt", "url": "https://...",
                  "article_id": "1234", "page_date": "as shown, or null", "text": "verbatim"}}],
  "plan_captured": "Plan 50K",
  "screen": {
    "drawdown_eval": TERM, "drawdown_funded": TERM, "consistency_eval": TERM, "consistency_funded": TERM,
    "max_funded_accounts": TERM, "copy_trading": TERM, "opposite_positions": TERM, "news": TERM,
    "automation": TERM, "sizing_gambling": TERM,
    "verdict": "PASS | FAIL | UNDETERMINED", "verdict_reason": "one line"
  },
  "terms": {"eval_profit_target": TERM, "...": TERM}
}
```

where every `TERM` is

```json
{"value": "the canonical value, e.g. 3000 or \"eod_trailing\" or \"none stated\"",
 "status": "verified | UNVERIFIED",
 "quotes": [{"file": "raw/slug/page.txt", "url": "https://...", "article_id": "id or slug or null",
             "page_date": "the page's own updated date as shown, or null", "text": "VERBATIM text"}],
 "looked_at": "for UNVERIFIED: the URLs read that do not state it",
 "note": "any reading/interpretation, conflict between pages, or caveat"}
```

`"file"` is the path relative to S of the saved `.txt` the quote is in (the checker also looks in the matching
`.scripts.txt` and `.txt.json.txt`). **Every `text` must be copied character for character from that file** (copy
from the file, don't retype from memory); keep quotes short (one sentence, one table row with its header row as a
separate quote if needed). When two official pages conflict, quote both and say so in `note`.

Before you finish, run the checker and fix every MISS (re-copy the exact text, or drop the quote):
`python -I "S/tools/check_quotes.py" "S" <slug> [<slug> ...]`

## Your reply

When done: per firm, the verdict and one line why; the plan captured; the count of terms verified vs UNVERIFIED; the
checker's output line; anything surprising (rule conflicts between official pages, recent rule changes with dates,
hosts unreadable). Keep it short -- the JSON files carry the detail.
