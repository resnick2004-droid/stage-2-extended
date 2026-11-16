"""Lucid Trading (LucidFlex $50,000, the DLL-off checkout) in Stage 2's campaign engine (R7, docs/TWO_FIRMS.md).

Every number here comes from a VERIFIED row of the multi-firm repository's Lucid ledger, vendored read-only at
`vendor/propfirms/firms/lucid-trading/` (its revision in `vendor/MANIFEST_propfirms.sha256`: the 2026-10-30
re-verification, its D-30, and the prices read from the official pricing cards on 2026-11-05, its D-31) and read through `propedge.contract.firms.FirmLedger` (pinned bytes; a row that is not
verified raises). Where a verified row states a figure only inside its value text or its quoted note, the figure is
parsed fail-loud with the patterns of the multi-firm repository's validated fit (`vendor/propfirms/propfirms/contract/
evals.py`, `engine.py`; its P-03, D-20); a test holds Stage 2's mapping equal to that fit (`tests/test_lucid_oracles.py`).

**The configurations.** Lucid's checkout sets two things (16226050): the Daily Loss Limit on or off, and the
evaluation's consistency at 40 % (standard) or 50 % (a paid add-on) -- four configurations. The engine runs the DLL-off
ones (the multi-firm repository's T4 §1):

* `STANDARD_40` ("lucidflex_50k_standard40"): the largest day at most 40 % of the evaluation profit, a pass in as few
  as three days -- the `eval_consistency_rule` and `eval_min_days` rows' values (12945805, 12945790);
* `ADDON_50` ("lucidflex_50k_addon50"): at most 50 %, as few as two days -- the same verified rows' quoted text ("If you
  added the 50% consistency add-on at checkout, it must be 50% or less"; "or 2 days with the 50% consistency
  add-on"). The multi-firm repository's earlier Lucid results (its P-01..P-07, at the then-only 50 % rule) describe it.

How Lucid maps onto the engine (the multi-firm repository's T4 finding, `vendor/propfirms/docs/T4_ENGINE_FIT.md`):

* **The evaluation is Topstep's Combine with other parameters** -- the same EOD-trailing floor with intraday breach,
  the same `max(target, best day / frac)` consistency semantics: target $3,000, MLL $2,000, the floor locking at start
  + $100, the best day at most the configuration's fraction of the profit (which implies its stated minimum days,
  checked), no daily loss limit, a one-time fee. So `CombineAccount` runs it unchanged on `lucid_rules()`.
* **The funded account is Topstep's Standard path with three differences**, which `LucidFundedAccount` adds: the cycle
  needs a net profit of at least $1 (every cycle, the first included); the account ends after its fifth payout (the
  sim-funded seat frees; the household enters Lucid's live review pool); and there is no "Payout request day"
  excluded from the next cycle (Topstep's 8284233 rule). The rest is Topstep's form at Lucid's values: $2,000
  EOD-trailing MLL from -$2,000, locking at start + $100 and forced to the lock by a payout request; five winning days
  of at least $150 a cycle; a request of 50 % of the balance above start, at most $2,000 and at least $500; a 90 %
  split; no consistency rule; no daily loss limit; $0 activation.

**What is not verified, and what that blocks.**

* The evaluation's price and the reset's (`eval_fee`, `eval_reset_fee`) are VERIFIED again (multi-firm D-31, from
  the official pricing cards, the operator's screenshots of 2026-11-05; stage-two D-574): the DLL-off 40 % evaluation
  $115.50 one-time with the checkout coupon (which applies to every purchase), its reset $115; the 50 % add-on $130.20,
  reset $130 (the same rows' configuration lines). `lucid_price` maps them fail-loud (`_verified_price`). A Lucid
  campaign buys no resets unless it asks (`reset_failed_combines`); a failed evaluation is replaced by a new purchase at
  the evaluation fee. Should the rows ever reopen, `lucid_rules()` again raises `UnpricedLucidRules` (naming the rows
  and `OPERATOR_PRICE_READ`) and only the engine's own checks pass `unpriced=ENGINE_CHECKS_ONLY`, at the labelled
  former basis -- $105 one-time, a failed evaluation repurchased (multi-firm D-22, D-28; `ENGINE_CHECK_EVAL_FEE`);
  while the rows are verified that argument changes nothing.
* The funded account's recurring fee and the per-payout fee (`funded_monthly_fee`, `payout_fee`): never loaded.
  `lucid_rules(open_rows="upper_bound")` charges neither, and every result built on it is an UPPER BOUND in those two
  rows -- the multi-firm repository's own reading (its D-28) -- labelled in its provenance. Nothing defaults silently.

**The household rule** (multi-firm D-30's T2a flag; the New Live Structure, 16558826, quoted in the verified
`max_accounts` row): after the fifth payout an account enters the live review pool, the live move is at the risk
team's discretion, and "All simulated prop accounts are closed when a trader is moved live, or opts out of trading
live via cash-out." `LucidFundedAccount` declares the rule with `HOUSEHOLD_CLOSES_AT_LIVE = True` -- the conservative
reading, D-30's: the first fifth payout ends every simulated Lucid account of the campaign at that close and the
campaign buys no more (`propedge.campaign.lockstep`, `household_closure`). False is the optimistic reading, reported
beside: the event is counted and nothing else closes. No live trading is modelled.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field, replace
from functools import lru_cache
from typing import Any, ClassVar

from propedge.campaign.lockstep import EPS, FundedAccount
from propedge.contract.firms import FirmLedger
from propedge.contract.payout_timing import REQUEST_4_TO_5PM, request_day_excluded
from propedge.contract.rules import UnverifiedRuleError

SLUG = "lucid-trading"

#: The evaluation fee is one-time ("One-time fee, no monthly rebilling", 12945790): never rebilled inside any horizon.
ONE_TIME_BILLING_DAYS = 10**9

#: The DLL-off checkout configurations the engine runs (16226050 sells four: the DLL on or off x 40 % or 50 %).
STANDARD_40 = "lucidflex_50k_standard40"
ADDON_50 = "lucidflex_50k_addon50"
CONFIGURATIONS = (STANDARD_40, ADDON_50)

#: The one reading of Lucid's two open fee rows a run may take: neither is charged, so the result is an upper bound.
OPEN_ROWS_UPPER_BOUND = "upper_bound"
OPEN_ROWS = ("funded_monthly_fee", "payout_fee")
OPEN_ROWS_NOTE = ("Lucid's funded_monthly_fee and payout_fee rows are unverified (multi-firm ledger, H-6; its D-28, "
                  "D-30): neither is charged, so every Lucid figure is an UPPER BOUND in them")

#: The rows a study needs that the 2026-10-30 re-read left unverified (multi-firm D-30, its H-6) and its D-31 verified
#: again from the official pricing cards: the evaluation's price and the reset's. Were either open, Lucid's rules would
#: refuse a study.
PRICE_ROWS = ("eval_fee", "eval_reset_fee")
OPERATOR_PRICE_READ = ("docs/OPERATOR_SETUP.md item 4 (Lucid's checkout prices for the LucidFlex 50K configurations and "
                       "the reset, read in a browser by the operator; no purchase)")
ENGINE_CHECKS_ONLY = "engine_checks_only"
#: Engine checks only, while PRICE_ROWS are open: the multi-firm repository's former price basis -- the DLL-off
#: evaluation at $105, one-time (its D-22, verified then, reopened by its D-30; the fixed basis of its P-05..P-07) -- and
#: no reset bought, a failed evaluation repurchased at that price (its D-28). Not Lucid's current price for either
#: configuration; no study runs on it (a test holds it equal to the figure the vendored row's history records).
ENGINE_CHECK_EVAL_FEE = 105.0
ENGINE_CHECK_PRICE_NOTE = ("ENGINE CHECK PRICE, not Lucid's: the evaluation at $105 one-time and a failed evaluation "
                           "repurchased (the multi-firm repository's former basis, its D-22 and D-28, reopened by its "
                           "D-30); eval_fee and eval_reset_fee are unverified")


class UnpricedLucidRules(UnverifiedRuleError):
    """A row a Lucid study needs -- the evaluation's price or the reset's -- is not verified (multi-firm D-30)."""


#: Lucid's payout timing in the engine's vocabulary: the request at the eligible day's close, the next session counting
#: toward the new cycle -- no Lucid rule excludes it ("you may request a payout any day after meeting all eligibility
#: criteria", 12945796). The 4-5 PM CT wording of the constant is Topstep's; for Lucid only its mechanics apply.
LUCID_PAYOUT_TIMING = REQUEST_4_TO_5PM
LUCID_PAYOUT_TIMING_NOTE = ("Lucid: request at the eligible day's close; no request day is excluded from the next cycle "
                            "(12945796: 'no fixed payout window')")

#: The household rule's quote (16558826), required in the verified max_accounts row's note.
HOUSEHOLD_RULE_QUOTE = ("All simulated prop accounts are closed when a trader is moved live, or opts out of trading "
                        "live via cash-out.")


class LucidFitError(ValueError):
    """A verified row's text no longer parses the way the fit expects -- the ledger changed. Re-derive; never guess."""


def _flat(text: Any) -> str:
    """A row's text on one line (the ledger's notes wrap)."""
    return " ".join(str(text).split())


def _require(pattern: str, text: Any, where: str) -> re.Match[str]:
    m = re.search(pattern, _flat(text))
    if m is None:
        raise LucidFitError(f"pattern {pattern!r} not found in {where}: {text!r}")
    return m


def _check_configuration(configuration: str) -> None:
    if configuration not in CONFIGURATIONS:
        raise ValueError(f"Lucid configuration {configuration!r} is not one the engine runs: {CONFIGURATIONS}")


@dataclass(frozen=True)
class LucidTerms:
    """Lucid's contract as the engine needs it, each field from a verified row (`citations` names the row)."""

    eval_target: float
    eval_mll: float
    eval_lock: float
    eval_consistency: float         # the standard configuration's (the row's value)
    eval_min_days: int              # the standard configuration's fastest pass (the row's value)
    eval_consistency_addon: float   # the 50 % add-on's (the same row's quote)
    eval_min_days_addon: int        # the add-on's fastest pass (the same row's quote)
    eval_count_limit: int
    eval_position_micros: int
    funded_mll: float
    funded_lock: float
    activation_fee: float
    winning_day_min: float
    winning_days: int
    cycle_net_min: float
    payout_frac_of_profit: float
    request_cap: float
    payout_min: float
    split: float
    max_payouts: int
    payout_processing_days: int
    max_funded: int
    max_total_accounts: int
    funded_ladder: tuple[tuple[float, int], ...]     # (profit threshold, minis), ascending
    cross_firm_hedging_prohibited: bool
    commissions_per_side: tuple[tuple[str, float], ...]
    price_rows_open: tuple[str, ...]                 # PRICE_ROWS not verified in the vendored ledger
    citations: tuple[tuple[str, str], ...]
    provenance: tuple[tuple[str, Any], ...]

    def citation(self, key: str) -> str:
        return dict(self.citations)[key]

    def consistency(self, configuration: str = STANDARD_40) -> float:
        _check_configuration(configuration)
        return self.eval_consistency if configuration == STANDARD_40 else self.eval_consistency_addon

    def min_days(self, configuration: str = STANDARD_40) -> int:
        _check_configuration(configuration)
        return self.eval_min_days if configuration == STANDARD_40 else self.eval_min_days_addon


@lru_cache(maxsize=1)
def lucid_terms() -> LucidTerms:
    """Lucid's terms from the vendored ledger's verified rows. Raises if any row it needs is not verified, or if a
    verified row's text no longer parses as the fit expects. The price rows are not read here (`lucid_price`)."""
    L = FirmLedger.load(SLUG)
    used: list[str] = []

    def v(key: str) -> Any:
        used.append(key)
        return L.value(key)

    def note(key: str) -> str:
        used.append(key)
        return L.verified_note(key)

    if v("eval_drawdown_type") != "eod_trailing" or v("funded_drawdown_type") != "eod_trailing":
        raise LucidFitError("Lucid's drawdown is no longer EOD-trailing in both phases -- refit (the engine's floor)")
    eval_lock = float(_require(r"^locks_at_start_plus_(\d+)$", v("eval_drawdown_lock"), "eval_drawdown_lock").group(1))
    if v("eval_daily_loss_limit") != "optional_at_checkout" or v("funded_daily_loss_limit") != "optional_at_checkout":
        raise LucidFitError("Lucid's daily loss limit is no longer a checkout option -- the DLL-off variant needs refit")
    # the two consistency configurations: the standard from the row's value, the add-on from its quote (12945805)
    frac = float(v("eval_consistency_rule"))
    cons_note = note("eval_consistency_rule")
    std_pct = int(_require(r"Consistency Percentage must be (\d+)% or less", cons_note, "eval_consistency_rule").group(1))
    add = _require(r"If you added the (\d+)% consistency add-on at checkout, it must be (\d+)% or less", cons_note,
                   "eval_consistency_rule")
    if not math.isclose(std_pct / 100.0, frac) or add.group(1) != add.group(2):
        raise LucidFitError(f"eval_consistency_rule's value {frac} and its quote ({std_pct} %, add-on {add.group(1)} / "
                            f"{add.group(2)} %) disagree -- refit")
    frac_addon = int(add.group(2)) / 100.0
    min_days = int(v("eval_min_days"))
    fast = _require(r"Pass in as few as (\d+) days with (\d+)% consistency, or (\d+) days with the (\d+)% consistency "
                    r"add-on", note("eval_min_days"), "eval_min_days")
    if (int(fast.group(1)), int(fast.group(2)), int(fast.group(4))) != (min_days, std_pct, int(add.group(2))):
        raise LucidFitError(f"eval_min_days ({min_days}) and its quote {fast.group(0)!r} disagree -- refit")
    min_days_addon = int(fast.group(3))
    for f, d in ((frac, min_days), (frac_addon, min_days_addon)):
        if math.ceil(1.0 / f - 1e-12) < d:
            raise LucidFitError(f"the consistency rule {f} no longer implies the {d}-day minimum the engine relies on")
    pos = _require(r"(\d+) minis / (\d+) micros", v("eval_position_limit"), "eval_position_limit")
    if v("eval_time_limit") != "none":
        raise LucidFitError("Lucid's evaluation now has a time limit -- refit")
    _require(r"One-time fee, no monthly rebilling", note("eval_time_limit"), "eval_time_limit note")
    if v("funded_type") != "sim_funded":
        raise LucidFitError("Lucid's funded account is no longer sim-funded -- refit")
    _require(r"No activation fees to upgrade to funded account", note("funded_type"), "funded_type note")
    if v("funded_consistency_rule") != "none":
        raise LucidFitError("Lucid's funded account now has a consistency rule -- refit")
    lock = float(_require(r"start \+ \$(\d+)", v("payout_balance_consequence"), "payout_balance_consequence").group(1))
    if lock != eval_lock:
        raise LucidFitError(f"the funded lock {lock} and the evaluation lock {eval_lock} differ -- refit")
    gate = str(v("payout_frequency_gate"))
    _require(r"live review pool", gate, "payout_frequency_gate")        # the D-30 wording the household rule reads
    cap = _require(r"min\((0\.\d+) \* profits, (\d+)\)", v("payout_cap"), "payout_cap")
    ladder = [(float(t.replace(",", "")), int(m)) for m, t in
              re.findall(r"(\d+) at \$([\d,]+)", str(v("funded_position_limit")))]
    if not ladder or ladder[0][0] != 0.0 or [t for t, _ in ladder] != sorted(t for t, _ in ladder):
        raise LucidFitError(f"the funded scaling ladder no longer parses: {v('funded_position_limit')!r}")
    accounts_note = note("max_accounts")
    total = int(_require(r"maximum of (\d+) accounts in total", accounts_note, "max_accounts note").group(1))
    if total != int(v("eval_count_limit")):
        raise LucidFitError("the total-account cap and the evaluation cap differ -- refit the caps")
    _require(re.escape(HOUSEHOLD_RULE_QUOTE), accounts_note, "max_accounts note (the household rule, 16558826)")
    conduct = str(v("prohibited_conduct"))
    _require(r"cross-firm", conduct, "prohibited_conduct")
    comm = tuple((s, float(x)) for s, x in re.findall(r"\b(ES|MES|NQ|MNQ) \$(\d+\.\d+)", note("permitted_products")))
    for k in ("eval_profit_target", "eval_drawdown_amount", "funded_drawdown_amount", "payout_min", "payout_split",
              "payout_processing_days", "max_accounts"):
        used.append(k)
    terms = LucidTerms(
        eval_target=float(L.value("eval_profit_target")),
        eval_mll=float(L.value("eval_drawdown_amount")),
        eval_lock=eval_lock,
        eval_consistency=frac,
        eval_min_days=min_days,
        eval_consistency_addon=frac_addon,
        eval_min_days_addon=min_days_addon,
        eval_count_limit=int(L.value("eval_count_limit")),
        eval_position_micros=int(pos.group(2)),
        funded_mll=float(L.value("funded_drawdown_amount")),
        funded_lock=lock,
        activation_fee=0.0,
        winning_day_min=float(_require(r"daily profit >= \$(\d+)", gate, "payout_frequency_gate").group(1)),
        winning_days=int(_require(r"(\d+) days with", gate, "payout_frequency_gate").group(1)),
        cycle_net_min=float(_require(r"net profit >= \$(\d+)", gate, "payout_frequency_gate").group(1)),
        payout_frac_of_profit=float(cap.group(1)),
        request_cap=float(cap.group(2)),
        payout_min=float(L.value("payout_min")),
        split=float(L.value("payout_split")),
        max_payouts=int(_require(r"max (\d+) payouts", gate, "payout_frequency_gate").group(1)),
        payout_processing_days=int(L.value("payout_processing_days")),
        max_funded=int(L.value("max_accounts")),
        max_total_accounts=total,
        funded_ladder=tuple(ladder),
        cross_firm_hedging_prohibited=True,
        commissions_per_side=comm,
        price_rows_open=tuple(k for k in PRICE_ROWS if not L.entry(k).is_verified),
        citations=tuple((k, L.entry(k).citation()) for k in dict.fromkeys(used)),
        provenance=tuple(sorted(L.provenance().items())),
    )
    if terms.eval_mll != terms.funded_mll:
        raise LucidFitError("Lucid's evaluation and funded MLL differ; the engine's Rules carries one mll -- refit")
    return terms


@dataclass(frozen=True)
class LucidPrice:
    """What one configuration's evaluation and reset cost a campaign, and whether that is a verified price."""

    configuration: str
    eval_fee: float                 # one-time
    reset_fee: float                # math.inf: no reset is bought; a failed evaluation is repurchased at eval_fee
    verified: bool
    note: str


def lucid_price(configuration: str = STANDARD_40, *, unpriced: str | None = None) -> LucidPrice:
    """The configuration's evaluation and reset price from verified rows (multi-firm D-31; `_verified_price`) -- or,
    were `PRICE_ROWS` open, a refusal (`UnpricedLucidRules`, naming the rows and the operator's price read) unless the
    caller is one of the engine's own checks (`unpriced=ENGINE_CHECKS_ONLY`), which gets the labelled engine-check
    basis. With the rows verified, `unpriced` changes nothing."""
    _check_configuration(configuration)
    t = lucid_terms()
    if t.price_rows_open:
        if unpriced != ENGINE_CHECKS_ONLY:
            raise UnpricedLucidRules(
                f"Lucid's {', '.join(t.price_rows_open)} row(s) are not verified (the 2026-10-30 re-read, the "
                f"multi-firm repository's D-30): the {configuration} evaluation and its reset have no verified price, "
                f"so no Lucid study may run. Needed first: {OPERATOR_PRICE_READ}; then the rows verified in the "
                "multi-firm ledger and re-vendored here (scripts/vendor_propfirms.py) under a decision. Only the "
                f"engine's own checks pass unpriced={ENGINE_CHECKS_ONLY!r} (ENGINE_CHECK_EVAL_FEE, labelled).")
        return LucidPrice(configuration, ENGINE_CHECK_EVAL_FEE, math.inf, False, ENGINE_CHECK_PRICE_NOTE)
    return _verified_price(configuration)


#: The configuration lines of the verified price rows' notes (multi-firm D-31): "DLL OFF + 40 %: $115.50" for the
#: standard configuration (the row's value), "DLL OFF + 50 % add-on: $130.20" for the add-on.
_PRICE_LINE = {STANDARD_40: r"DLL OFF \+ 40 %: \$([\d,]+(?:\.\d+)?)",
               ADDON_50: r"DLL OFF \+ 50 % add-on: \$([\d,]+(?:\.\d+)?)"}


def _money(m: re.Match[str]) -> float:
    return float(m.group(1).replace(",", ""))


@lru_cache(maxsize=None)
def _verified_price(configuration: str) -> LucidPrice:
    """The verified price rows (multi-firm D-31: the official pricing cards, the operator's screenshots of 2026-11-05)
    mapped onto one DLL-off configuration. The rows' values are the standard configuration's (DLL off, 40 %); the
    add-on's figures are the same rows' quoted configuration lines. Every figure is parsed fail-loud and the standard
    line must equal the row's value -- a ledger that changed shape raises `LucidFitError`, never a guess."""
    L = FirmLedger.load(SLUG)
    fee_row, reset_row = L.entry("eval_fee"), L.entry("eval_reset_fee")
    fee_note, reset_note = L.verified_note("eval_fee"), L.verified_note("eval_reset_fee")
    # the basis: the coupon price, paid on every purchase (the operator, D-31), one-time, at the DLL-off checkout
    _require(r"W/ COUPON AT CHECKOUT", fee_note, "eval_fee note (the card's coupon price)")
    _require(r"multiple time thing", fee_note, "eval_fee note (the coupon applies to every purchase)")
    _require(r"one-time", fee_note, "eval_fee note (billing basis)")
    _require(r"DLL OFF", fee_note, "eval_fee note (the modelled DLL-off checkout)")
    std_fee = _money(_require(_PRICE_LINE[STANDARD_40], fee_note, "eval_fee note"))
    std_reset = _money(_require(_PRICE_LINE[STANDARD_40], reset_note, "eval_reset_fee note"))
    if not (math.isclose(std_fee, float(fee_row.value)) and math.isclose(std_reset, float(reset_row.value))):
        raise LucidFitError(f"the price rows' values ({fee_row.value}, {reset_row.value}) and their standard "
                            f"configuration lines ({std_fee}, {std_reset}) disagree -- refit")
    if configuration == STANDARD_40:
        fee, reset = std_fee, std_reset
    else:
        fee = _money(_require(_PRICE_LINE[configuration], fee_note, "eval_fee note"))
        reset = _money(_require(_PRICE_LINE[configuration], reset_note, "eval_reset_fee note"))
    pct = "40 % standard" if configuration == STANDARD_40 else "50 % add-on"
    return LucidPrice(
        configuration, fee, reset, True,
        f"VERIFIED (multi-firm D-31; the official pricing card, operator screenshots 2026-11-05): LucidFlex 50K, DLL "
        f"off, {pct} consistency -- ${fee:,.2f} one-time with the checkout coupon (applies to every purchase), reset "
        f"${reset:,.2f}; {fee_row.citation()}")


def lucid_rules(*, open_rows: str | None = None, unpriced: str | None = None, configuration: str = STANDARD_40,
                **overrides: Any) -> Any:
    """The vendored engine's `Rules` for Lucid in one checkout configuration (`STANDARD_40`, the default, or
    `ADDON_50`): the evaluation and the funded account from verified rows only.

    The evaluation fee (one-time) and the reset fee are the configuration's verified price (`lucid_price`, multi-firm
    D-31). Were the price rows open, a study would get `UnpricedLucidRules`.

    `open_rows` must be `OPEN_ROWS_UPPER_BOUND`: the caller acknowledges that Lucid's two unverified fee rows are not
    charged and the result is an upper bound in them (`OPEN_ROWS_NOTE`). Anything else raises -- the gate never lets
    an unverified row default quietly. `payout_fee`, `subscription`, `reset_fee` and `consistency_max_day_frac` cannot
    be overridden (open rows, price rows, and the configuration's rule).

    Fields Lucid does not have are set so that reading them cannot pass for a Lucid rule: the Consistency payout path
    (`cons_*`, NaN: `LucidFundedAccount` refuses that path) and Topstep's back-to-funded product (`b2f_max` 0).
    """
    price = lucid_price(configuration, unpriced=unpriced)
    if open_rows != OPEN_ROWS_UPPER_BOUND:
        raise ValueError(
            f"Lucid's {OPEN_ROWS} rows are unverified; pass open_rows={OPEN_ROWS_UPPER_BOUND!r} to run with neither "
            "charged and every figure labelled an upper bound in them, or verify the rows first"
        )
    if "payout_fee" in overrides:
        raise ValueError("Lucid's payout_fee is an open row; it cannot be set here")
    fixed = sorted({"subscription", "reset_fee", "consistency_max_day_frac"} & set(overrides))
    if fixed:
        raise ValueError(f"{fixed} come from Lucid's price rows and the configuration ({configuration}); they cannot be "
                         "set here")
    from propedge.contract.adapter import Rules

    t = lucid_terms()
    rules = replace(
        Rules(),
        profit_target=t.eval_target,
        mll=t.eval_mll,
        consistency_max_day_frac=t.consistency(configuration),
        combine_mll_lock_at=t.eval_lock,
        xfa_mll_start=-t.funded_mll,
        xfa_lock_at=t.funded_lock,
        std_winning_days=t.winning_days,
        std_winning_day_min=t.winning_day_min,
        std_cap=t.request_cap,
        cons_min_days=0,
        cons_max_day_frac=float("nan"),
        cons_cap=float("nan"),
        payout_min=t.payout_min,
        payout_max_frac_of_balance=t.payout_frac_of_profit,
        profit_split=t.split,
        payout_fee=0.0,
        # the base class's reading of a per-cycle profit; LucidFundedAccount applies Lucid's own ($1, every cycle)
        require_profit_since_payout=True,
        subscription=price.eval_fee,
        billing_days=ONE_TIME_BILLING_DAYS,
        activation=t.activation_fee,
        reset_fee=price.reset_fee,
        b2f_max=0,
    )
    return replace(rules, **overrides) if overrides else rules


def lucid_sizing_rule(mode: str | None = None, *, headroom_frac: float | None = None, **kw: Any) -> Any:
    """A `SizingRule` with Lucid's verified limits: the evaluation's full 40 micros from day one ("There is no scaling
    plan in the evaluation phase", 12945808) and the funded ladder 2 / 3 / 4 minis at $0 / $1,000 / $2,000 of profit
    ("updates at the end of each session"). Mode and headroom as `SizingRule` (Topstep's defaults)."""
    from propedge.campaign.sizing import (CURRENT_TIER, DEFAULT_HEADROOM_FRAC, MICROS_PER_MINI, ScalingLadder,
                                          SizingRule)

    t = lucid_terms()
    ladder = ScalingLadder(thresholds=tuple(x for x, _ in t.funded_ladder), minis=tuple(m for _, m in t.funded_ladder),
                           micros_per_mini=MICROS_PER_MINI,
                           source=f"lucid funded_position_limit ({t.citation('funded_position_limit')})")
    return SizingRule(mode=CURRENT_TIER if mode is None else mode, ladder=ladder,
                      combine_limit_micros=int(t.eval_position_micros),
                      headroom_frac=DEFAULT_HEADROOM_FRAC if headroom_frac is None else float(headroom_frac), **kw)


def _lucid_max_payouts() -> int:
    return lucid_terms().max_payouts


def _lucid_cycle_net_min() -> float:
    return lucid_terms().cycle_net_min


@dataclass
class LucidFundedAccount(FundedAccount):
    """A LucidFlex funded account, stepped a day at a time: Topstep's `FundedAccount` at Lucid's `Rules`
    (`lucid_rules()`), with Lucid's three differences (the module docstring). The path builds it when given
    `funded_account_cls=LucidFundedAccount`, and applies the household rule it declares."""

    FIRM: ClassVar[str] = SLUG
    #: The household rule (multi-firm D-30; 16558826): the engine's default reading for this class is the conservative
    #: one -- the first fifth payout ends every simulated Lucid account of the campaign (`propedge.campaign.lockstep`,
    #: `household_closure`; False is the optimistic reading, reported beside).
    HOUSEHOLD_CLOSES_AT_LIVE: ClassVar[bool] = True
    max_payouts: int = field(default_factory=_lucid_max_payouts)
    cycle_net_min: float = field(default_factory=_lucid_cycle_net_min)
    # took its last allowed payout: the sim account ends and the household enters the live review pool (12945796; the
    # live move is at the risk team's discretion, 16558826). The name is the 2026-10-04 reading's, kept.
    moved_live: bool = False

    def __post_init__(self) -> None:
        super().__post_init__()
        if request_day_excluded(self.payout_timing):
            raise ValueError(
                "Lucid has no Payout request day excluded from the next cycle (that is Topstep's 8284233 rule); run "
                f"the Lucid accounts at payout_timing={LUCID_PAYOUT_TIMING!r} ({LUCID_PAYOUT_TIMING_NOTE})"
            )
        if self.dll is not None or self.policy_override is not None:
            raise ValueError("the Responsible Trading Program is Topstep's: a Lucid account takes no RTP daily loss limit "
                             "or Consistency path (run the Lucid campaign with conduct=None)")

    @property
    def closes_household(self) -> bool:
        """The household rule's trigger (the path reads it at each close): this account took its fifth payout."""
        return self.moved_live

    def trade_day(self, rules: Any, policy: Any, cap: float, rel_day: int, calendar_day: int,
                  ledger: list[dict[str, Any]] | None = None, second_trade: bool = False,
                  collect: bool = False) -> float | None:
        if policy.payout_path != "standard":
            raise ValueError("LucidFlex has one payout path; the funded policy's payout_path must be 'standard'")
        return super().trade_day(rules, policy, cap, rel_day, calendar_day, ledger=ledger,
                                 second_trade=second_trade, collect=collect)

    def _standard_eligible(self, rules: Any) -> bool:
        """12945796: five days of at least $150 since the last payout, a net profit of at least $1 in the cycle (the
        first included), and fewer than the account's lifetime payouts."""
        return (self.win_days >= rules.std_winning_days
                and self.since_pay >= self.cycle_net_min - EPS
                and self.n_payouts < self.max_payouts)

    def _after_payout(self, calendar_day: int) -> None:
        """12945796: "Traders may take up to 5 payouts from each LucidFlex account after which they will be moved
        live" -- since 2026-10 into the live review pool, the move at the risk team's discretion (16558826). The
        sim-funded account ends at the close of its last payout; its seat frees as after any ending."""
        if self.n_payouts >= self.max_payouts:
            self.moved_live = True
            self.ended_on = int(calendar_day)

    def deny_last_payout(self, calendar_day: int) -> None:
        super().deny_last_payout(calendar_day)
        self.moved_live = False


def lucid_provenance(configuration: str = STANDARD_40, *, unpriced: str | None = None,
                     household_closes_at_live: bool = True) -> dict[str, Any]:
    """What a result built on Lucid records: the vendored ledger, the rows used with their citations, the
    configuration, the price and whether it is verified, the open rows and how they are read, the household rule's
    reading, and the modelling choices. Refused like `lucid_rules` while the price rows are open."""
    t = lucid_terms()
    price = lucid_price(configuration, unpriced=unpriced)
    pct = round(100 * t.consistency(configuration))
    return {
        **dict(t.provenance),
        "rows_used": dict(t.citations),
        "configuration": configuration,
        "variant": (f"LucidFlex 50K, DLL off at checkout, {pct} % evaluation consistency "
                    f"({'standard' if configuration == STANDARD_40 else 'the paid add-on'})"),
        "eval_consistency": t.consistency(configuration),
        "eval_min_days": t.min_days(configuration),
        "price": {"eval_fee": price.eval_fee,
                  "reset": ("none bought; a failed evaluation is repurchased at the evaluation fee"
                            if math.isinf(price.reset_fee) else price.reset_fee),
                  "verified": price.verified, "note": price.note},
        "price_rows_open": list(t.price_rows_open),
        "open_rows": list(OPEN_ROWS),
        "open_rows_reading": OPEN_ROWS_NOTE,
        "household_closure": {
            "closes_at_live": bool(household_closes_at_live),
            "reading": ("conservative (multi-firm D-30): the first fifth payout ends every simulated Lucid account of the "
                        "campaign and no more are bought" if household_closes_at_live else
                        "optimistic: the fifth payout ends its own account only; the event is counted"),
            "rule": f"16558826: {HOUSEHOLD_RULE_QUOTE}",
        },
        "payout_timing": LUCID_PAYOUT_TIMING_NOTE,
        "assumptions": [
            "pass checked at the day close (stage one's convention; the multi-firm fit's)",
            "'profits' in the 50 % request cap read as the balance above start (the multi-firm fit's reading)",
            "an account that took its fifth payout ends in the campaign; its sim balance is not credited and no live "
            "account is modelled (the live move is discretionary, 16558826)",
            "the household's live move or cash-out is taken at the close of the first fifth payout (the conservative "
            "reading) or never (the optimistic one)",
        ],
    }


__all__ = ["SLUG", "ONE_TIME_BILLING_DAYS", "STANDARD_40", "ADDON_50", "CONFIGURATIONS", "OPEN_ROWS", "OPEN_ROWS_NOTE",
           "OPEN_ROWS_UPPER_BOUND", "PRICE_ROWS", "OPERATOR_PRICE_READ", "ENGINE_CHECKS_ONLY", "ENGINE_CHECK_EVAL_FEE",
           "ENGINE_CHECK_PRICE_NOTE", "HOUSEHOLD_RULE_QUOTE", "UnpricedLucidRules", "LUCID_PAYOUT_TIMING",
           "LUCID_PAYOUT_TIMING_NOTE", "LucidFitError", "LucidTerms", "lucid_terms", "LucidPrice", "lucid_price",
           "lucid_rules", "lucid_sizing_rule", "LucidFundedAccount", "lucid_provenance"]
