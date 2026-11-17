"""RD-01's terms (`prereg/RD-01_firm_contracts.md` 4.3-4.5, 4.8, 5, 7, 14.2): every plan's rule values from its record,
section 5's declared readings in one table, each plan's per-trade cost schedule, and the runs of 7.3.

**The loader (14.2, T-11).** `record_value(key)` reads this repository's record (`config/rules_extended.yaml`, under
E-020 and Q-59 / E-045) and **refuses** (`UnverifiedTerm`) any entry whose status is not `verified`; `stage2_value(key)`
reads Stage 2's vendored ledger (`vendor/stage2/config/rules.yaml`) the same way. A value stated in text is parsed
fail-loud (`TermParseError`): a record that changed shape stops the build, never a guess.

**Section 5's constants (14.2).** The values the pages leave open come only from `DECLARED`, each entry citing its line
of 5.2 (or 4.8 for Topstep's verified decomposition): `price_ends`, `min_days_ends`, `lag_ends`, `fee_schedule`. No rule
value is typed anywhere else in the adapters (`tests/test_rd01_terms.py` scans them for `RULE_LITERALS`).

Pure Python: the records are read as YAML; nothing here imports the engine.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, replace
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
RECORD = ROOT / "config" / "rules_extended.yaml"
STAGE2_LEDGER = ROOT / "vendor" / "stage2" / "config" / "rules.yaml"
STAGE2_FILLS = ROOT / "vendor" / "stage2" / "config" / "fills.yaml"
LUCID_LEDGER = ROOT / "vendor" / "stage2" / "vendor" / "propfirms" / "firms" / "lucid-trading" / "rules.yaml"
DECLARATION = "prereg/RD-01_firm_contracts.md"
PLANS = ("TS", "LU", "DT", "FP", "QP")
STRICT, LENIENT = "strict", "lenient"


class UnverifiedTerm(ValueError):
    """A rule the adapters would load is not `verified` in its record: it may not be used (CHARTER section 4)."""


class TermParseError(ValueError):
    """A verified record's text no longer parses as the adapters expect: the record changed -- re-derive, never guess."""


# ------------------------------------------------------------------------------------------------ the loaders


@lru_cache(maxsize=1)
def _record() -> dict[str, dict[str, Any]]:
    doc = yaml.safe_load(RECORD.read_text(encoding="utf-8"))
    return {str(e["key"]): e for e in doc["rules"]}


@lru_cache(maxsize=1)
def _stage2() -> dict[str, dict[str, Any]]:
    return yaml.safe_load(STAGE2_LEDGER.read_text(encoding="utf-8"))["rules"]


def record_entry(key: str) -> dict[str, Any]:
    """The record's entry, whatever its status (inspection only)."""
    try:
        return _record()[key]
    except KeyError:
        raise KeyError(f"no entry {key!r} in {RECORD.name}") from None


def record_value(key: str) -> Any:
    """A verified record entry's value; `UnverifiedTerm` for every other status (the record's 'unverified' and
    'unstated' entries are read only by section 5's declared rules, through `DECLARED`)."""
    e = record_entry(key)
    if e.get("status") != "verified":
        raise UnverifiedTerm(f"{key}: status {e.get('status')!r}, not 'verified' -- it may not be loaded; section 5 of "
                             f"{DECLARATION} reads it by a declared rule (`firm_terms.DECLARED`)")
    if e.get("value") is None:
        raise UnverifiedTerm(f"{key}: verified without a value")
    return e["value"]


def stage2_value(key: str) -> Any:
    """A verified entry of Stage 2's vendored ledger; `UnverifiedTerm` otherwise."""
    e = _stage2().get(key)
    if e is None:
        raise KeyError(f"no rule {key!r} in Stage 2's ledger")
    if e.get("status") != "verified":
        raise UnverifiedTerm(f"Stage 2's {key}: status {e.get('status')!r}, not 'verified'")
    return e["value"]


def _flat(text: Any) -> str:
    return " ".join(str(text).split())


def parse(pattern: str, text: Any, where: str) -> re.Match[str]:
    m = re.search(pattern, _flat(text))
    if m is None:
        raise TermParseError(f"{where}: pattern {pattern!r} not found in {text!r}")
    return m


def _num(s: str) -> float:
    return float(s.replace(",", ""))


def parse_money(pattern: str, text: Any, where: str, group: int = 1) -> float:
    return _num(parse(pattern, text, where).group(group))


def rv_money(key: str, pattern: str, group: int = 1) -> float:
    return parse_money(pattern, record_value(key), key, group)


# ------------------------------------------------------------------------------------------------ section 5's table


@dataclass(frozen=True)
class Declared:
    value: Any
    cite: str


#: Section 5's declared readings -- the one place their values are typed (14.2). Each cites its line of 5.2, or 4.8.
DECLARED: dict[str, Declared] = {
    "FP.price.strict": Declared(248.0, "5.2 FP evaluation price, strict end: the highest listed ($248 list card), U-1"),
    "FP.price.lenient": Declared(99.0, "5.2 FP evaluation price, lenient end: the lowest listed ($99 sale card), U-1"),
    "FP.price.listed": Declared((99.0, 180.0, 248.0), "5.2 FP evaluation price: every listed price, printed by the grid"),
    "QP.price.strict": Declared(175.0, "5.2 QP evaluation price, strict end: the highest listed ($175 help table), U-1"),
    "QP.price.lenient": Declared(69.0, "5.2 QP evaluation price, lenient end: the lowest listed ($69 sale card), U-1"),
    "QP.price.listed": Declared((69.0, 174.0, 175.0), "5.2 QP evaluation price: every listed price, printed by the grid"),
    "DT.price.grid": Declared((25.0, 250.0, 25.0), "5.2 DT evaluation price: the grid $25 to $250 in $25 steps, U-2"),
    "FP.min_days.strict": Declared(7, "5.2 FP minimum days, strict end: 'a minimum 7-day period' as seven trading days, U-4"),
    "QP.min_days.strict": Declared(7, "5.2 QP minimum days, strict end: seven trading days, U-4"),
    "QP.min_days.lenient": Declared(5, "5.2 QP minimum days, lenient end: five (the help page), U-4"),
    "fee.unstated": Declared(0.0, "5.2 the fees no page states (LU's two, DT's and FP's payout fee): $0, upper bound, U-3"),
    "topstep.commission_rt": Declared({"MNQ": 0.50, "NQ": 1.00},
                                      "4.8 Topstep's commission alone per round turn (fills.yaml lines 32-35, 8284213)"),
    "topstep.nfa_rt": Declared(0.02, "4.8 the NFA fee per round turn (fills.yaml lines 32-35, 8284213)"),
}

#: The assignments the literal scan skips (`tests/test_rd01_terms.py`): this table, and the scan's own list.
LITERAL_TABLES = ("DECLARED", "RULE_LITERALS")
#: Rule values that must not be typed outside `DECLARED` in the adapters (14.2).
RULE_LITERALS = frozenset({2000.0, 1250.0, 2600.0, 52000.0, 52600.0, 50000.0, 48000.0, 500.0, 250.0, 150.0, 200.0,
                           1500.0, 4000.0, 10000.0, 3000.0, 115.5, 165.0, 248.0, 99.0, 180.0, 175.0, 174.0, 69.0, 0.3,
                           0.45, 0.8, 1.02, 3.98, 0.95, 2.88, 1.9, 5.76, 1.74, 6.76, 1.22, 3.78, 0.7, 2.76, 0.02})


def declared(name: str) -> Any:
    return DECLARED[name].value


def _grid() -> tuple[float, ...]:
    lo, hi, step = declared("DT.price.grid")
    n = int(round((hi - lo) / step))
    return tuple(float(lo + i * step) for i in range(n + 1))


DT_PRICE_GRID = _grid()


def price_ends(plan: str) -> tuple[float, float]:
    """(strict, lenient) evaluation price of a plan whose price is unverified (U-1, U-2)."""
    if plan == "DT":
        return (DT_PRICE_GRID[-1], DT_PRICE_GRID[0])
    if plan in ("FP", "QP"):
        return (float(declared(f"{plan}.price.strict")), float(declared(f"{plan}.price.lenient")))
    raise ValueError(f"{plan}'s price is verified; it has no ends")


def min_days_ends(plan: str) -> tuple[int, int]:
    """(strict, lenient) TradeDay evaluation minimum trading days (U-4). FP's lenient end is the three days its 45 %
    share implies (5.2), computed from the verified share."""
    if plan == "FP":
        implied = int(math.ceil(1.0 / float(record_value("tradeday.fastpass_eod50k.eval_consistency_rule")) - 1e-12))
        return (int(declared("FP.min_days.strict")), implied)
    if plan == "QP":
        return (int(declared("QP.min_days.strict")), int(declared("QP.min_days.lenient")))
    raise ValueError(f"{plan} has no minimum-days term")


def lag_ends(plan: str) -> tuple[int, int]:
    """(strict, lenient) payout lag in sessions for DayTraders, whose processing time is unstated (U-5): the bracket
    of the verified lags of the other plans here -- Topstep's Aeropay and TradeDay's."""
    if plan != "DT":
        raise ValueError(f"{plan}'s lag is verified")
    verified = [int(stage2_value("payout_lag_days_aeropay")),
                int(record_value("tradeday.fastpass_eod50k.payout_processing_days")),
                int(record_value("tradeday.quickpay_eod50k.payout_processing_days"))]
    return (max(verified), min(verified))


@lru_cache(maxsize=1)
def lucid_list_price() -> float:
    """m8: Lucid's struck list price, from the vendored ledger's verified `eval_fee` note."""
    d = yaml.safe_load(LUCID_LEDGER.read_text(encoding="utf-8"))["rules"]["eval_fee"]
    if d.get("status") != "verified":
        raise UnverifiedTerm("Lucid's eval_fee is not verified")
    return parse_money(r"\$([\d,.]+) is the struck list price", d["note"], "lucid eval_fee note")


@lru_cache(maxsize=1)
def _fills() -> dict[str, float]:
    return dict(yaml.safe_load(STAGE2_FILLS.read_text(encoding="utf-8"))["round_turn_by_instrument"]["values"])


def fee_schedule(plan: str, end: str | None = None) -> tuple[float, float]:
    """4.8: the plan's round-turn fee (a micro, a mini) for the sizing rule's fee schedule (Stage 2 D-324)."""
    f = _fills()
    topstep = (float(f["MNQ"]), float(f["NQ"]))
    if plan in ("TS", "LU"):
        return topstep
    if plan in ("FP", "QP"):
        v = record_value("tradeday.commissions")
        parse(r"per lot per side", v, "tradeday.commissions")
        m = parse(r"MNQ \$([\d.]+), NQ \$([\d.]+)", v, "tradeday.commissions")
        return (2 * _num(m.group(1)), 2 * _num(m.group(2)))
    if plan == "DT":
        v = record_value("daytraders.commissions")
        parse(r"round turn", v, "daytraders.commissions")
        m = parse(r"MNQ \$([\d.]+), NQ \$([\d.]+)", v, "daytraders.commissions")
        listed = (_num(m.group(1)), _num(m.group(2)))
        if end == LENIENT:
            return listed
        if end == STRICT:                         # U-12: the listed figures plus exchange and NFA fees, as Topstep's
            comm, nfa = declared("topstep.commission_rt"), float(declared("topstep.nfa_rt"))
            exch = (topstep[0] - comm["MNQ"] - nfa, topstep[1] - comm["NQ"] - nfa)
            return (listed[0] + exch[0] + nfa, listed[1] + exch[1] + nfa)
        raise ValueError("DayTraders' fee basis is read at its two ends: 'strict' or 'lenient'")
    raise ValueError(f"unknown plan {plan!r}")


# ------------------------------------------------------------------------------------------------ the plans' terms


@dataclass(frozen=True)
class PlanTerms:
    """One plan's verified terms as the adapters need them; money is relative to the account's start, as the engine
    keeps it. None where the plan has no such rule."""

    plan: str
    start: float
    eval_target: float
    eval_mll: float
    eval_lock: float
    eval_consistency: float
    eval_position_micros: int
    eval_dll: float | None
    eval_qualifying_days: int | None
    qualifying_day_min: float | None
    funded_mll: float
    funded_lock: float
    funded_dll: float | None
    funded_consistency: float | None
    ladder: tuple[tuple[float, int], ...]
    winning_days: int
    winning_day_min: float | None
    request_gate: float | None
    request_leave: float | None
    request_increment: float | None
    payout_min: float
    payout_cap: float | None
    split: float | None
    split_low: float | None
    split_high: float | None
    split_line: float | None
    profit_ceiling: float | None
    fifth_request: int | None
    activation: float
    funded_recurring_fee: float
    recurring_fee_days: int | None
    billing: str
    lag_days: int | None
    seats: int
    inactivity_days: int | None
    inactivity_window_days: int | None
    payout_fee: float
    micros_per_mini: int


def _start_from(key: str) -> float:
    return rv_money(key, r"starting balance \(\$([\d,]+)\)")


def _lock_at_start(key: str) -> float:
    v = record_value(key)
    parse(r"(stops trailing at|trails (\([^)]*\) )?until it reaches) the starting balance", v, key)
    return 0.0                                      # relative to the start: the floor stops at the starting balance


@lru_cache(maxsize=None)
def plan_terms(plan: str) -> PlanTerms:
    """The verified terms of DT, FP or QP (TS's are the registered rows' own; LU's Stage 2's adapter)."""
    if plan == "DT":
        return _daytraders()
    if plan in ("FP", "QP"):
        return _tradeday(plan)
    raise ValueError(f"{plan}'s terms come from the engine's own loaders (TS: Stage 2's ledger; LU: its adapter)")


def _daytraders() -> PlanTerms:
    p = "daytraders.eod50k."
    start = _start_from(p + "eval_drawdown_lock")
    qd = parse(r"^(\d+) Qualifying Days \(each meeting the \$(\d+) minimum daily profit", record_value(p + "eval_min_days"),
               p + "eval_min_days")
    gate = parse(r"^(\d+) Qualifying Days \(each >= \$(\d+) profit", record_value(p + "payout_frequency_gate"),
                 p + "payout_frequency_gate")
    bal = record_value(p + "payout_balance_consequence")
    req_gate = parse_money(r"needs a balance of at least \$([\d,]+)", bal, p + "payout_balance_consequence") - start
    leave = parse_money(r"must leave at least \$([\d,]+)", bal, p + "payout_balance_consequence") - start
    pmin = parse(r"^(\d+) USD, in \$(\d+) increments", record_value(p + "payout_min"), p + "payout_min")
    per_mini = int(rv_money("daytraders.contract_counting", r"(\d+) micros count as 1 mini"))
    fpos = int(rv_money(p + "funded_position_limit", r"\((\d+) micros\)"))
    rec = parse(r"the \$(\d+) activation fee rebills every (\d+) days", record_value(p + "funded_monthly_fee"),
                p + "funded_monthly_fee")
    billing_v = record_value(p + "eval_billing_basis")
    parse(r"Monthly \(rebills at the original price every (\d+) days\)", billing_v, p + "eval_billing_basis")
    inact = record_value("daytraders.inactivity_rule")
    window = int(parse_money(r"rolling (\d+)-day window", inact, "daytraders.inactivity_rule"))
    inact_days = int(parse_money(r"at least (\d+) trading day meeting the minimum daily profit \(\$\d+ on 50K\) for "
                                 r"Monthly", inact, "daytraders.inactivity_rule"))
    return PlanTerms(
        plan="DT", start=start,
        eval_target=float(record_value(p + "eval_profit_target")),
        eval_mll=float(record_value(p + "eval_drawdown_amount")),
        eval_lock=_lock_at_start(p + "eval_drawdown_lock"),
        eval_consistency=float(record_value(p + "eval_consistency_rule")),
        eval_position_micros=int(rv_money(p + "eval_position_limit", r"\((\d+) micros\)")),
        eval_dll=rv_money(p + "eval_daily_loss_limit", r"^(\d+) USD, soft"),
        eval_qualifying_days=int(qd.group(1)), qualifying_day_min=_num(qd.group(2)),
        funded_mll=float(record_value(p + "funded_drawdown_amount")),
        funded_lock=_lock_at_start(p + "funded_drawdown_lock"),
        funded_dll=rv_money(p + "funded_daily_loss_limit", r"^(\d+) USD, soft"),
        funded_consistency=float(record_value(p + "funded_consistency_rule")),
        ladder=((0.0, fpos // per_mini),),
        winning_days=int(gate.group(1)), winning_day_min=_num(gate.group(2)),
        request_gate=req_gate, request_leave=leave, request_increment=_num(pmin.group(2)),
        payout_min=_num(pmin.group(1)),
        payout_cap=rv_money(p + "payout_cap", r"^(\d+) USD per request"),
        split=float(record_value(p + "payout_split")), split_low=None, split_high=None, split_line=None,
        profit_ceiling=None, fifth_request=None,
        activation=rv_money(p + "activation_fee", r"^(\d+) USD on activation"),
        funded_recurring_fee=_num(rec.group(1)), recurring_fee_days=int(rec.group(2)),
        billing="monthly", lag_days=None,
        seats=int(rv_money("daytraders.max_funded_accounts", r"^(\d+) EOD Pro Accounts")),
        inactivity_days=inact_days, inactivity_window_days=window,
        payout_fee=float(declared("fee.unstated")), micros_per_mini=per_mini,
    )


def _tradeday(plan: str) -> PlanTerms:
    q = "tradeday.fastpass_eod50k." if plan == "FP" else "tradeday.quickpay_eod50k."
    start = _start_from("tradeday.eval_drawdown_lock")
    eval_micros = int(rv_money("tradeday.eval_position_limit", r"\((\d+) micros\)"))
    eval_contracts = int(rv_money("tradeday.eval_position_limit", r"^(\d+) contracts"))
    parse(r"one-time fee", record_value("tradeday.eval_billing_basis"), "tradeday.eval_billing_basis")
    seats = int(rv_money("tradeday.max_funded_accounts", r"^(\d+) active Funded Sim"))
    common = dict(
        plan=plan, start=start,
        eval_target=float(record_value("tradeday.eval_profit_target")),
        eval_mll=float(record_value("tradeday.eval_drawdown_amount")),
        eval_lock=_lock_at_start("tradeday.eval_drawdown_lock"),
        eval_consistency=float(record_value(q + "eval_consistency_rule")),
        eval_position_micros=eval_micros, eval_dll=None, eval_qualifying_days=None, qualifying_day_min=None,
        funded_mll=float(record_value(q + "funded_drawdown_amount")),
        funded_lock=_lock_at_start(q + "funded_drawdown_lock"), funded_dll=None,
        request_gate=None, request_leave=None, request_increment=None,
        payout_min=float(record_value("tradeday.payout_min")),
        activation=float(record_value("tradeday.activation_fee")),
        funded_recurring_fee=float(record_value("tradeday.funded_monthly_fee")), recurring_fee_days=None,
        billing="one_time", lag_days=int(record_value(q + "payout_processing_days")), seats=seats,
        inactivity_days=None, inactivity_window_days=None, micros_per_mini=eval_micros // eval_contracts,
    )
    if plan == "FP":
        pos = parse(r"^(\d+) contracts \(\d+ micros\), plus (\d+) contract per \$(\d+)k profit",
                    record_value(q + "funded_position_limit"), q + "funded_position_limit")
        base, step, per = int(pos.group(1)), int(pos.group(2)), _num(pos.group(3)) * 1000.0
        ladder = tuple((float(i * per), base + i * step) for i in range((eval_contracts - base) // step + 1))
        gate = parse(r"at least (\d+) profitable days of >= \$(\d+)", record_value(q + "payout_frequency_gate"),
                     q + "payout_frequency_gate")
        return PlanTerms(
            **common, funded_consistency=rv_money(q + "funded_consistency_rule", r"^([\d.]+) of total gross profits"),
            ladder=ladder, winning_days=int(gate.group(1)), winning_day_min=_num(gate.group(2)),
            payout_cap=rv_money(q + "payout_cap", r"^(\d+) USD per request"),
            split=float(record_value(q + "payout_split")), split_low=None, split_high=None, split_line=None,
            profit_ceiling=None,
            fifth_request=int(rv_money(q + "payout_count_limit", r"on the (\d+)th payout request")),
            payout_fee=float(declared("fee.unstated")))
    parse(r"^intraday_trailing", record_value(q + "funded_drawdown_type"), q + "funded_drawdown_type")
    parse(r"after one day of trading; then any time the balance is positive", record_value(q + "payout_frequency_gate"),
          q + "payout_frequency_gate")
    split = parse(r"^([\d.]+) on current profit below \$([\d,]+); ([\d.]+) above", record_value(q + "payout_split"),
                  q + "payout_split")
    parse(r"^US bank wire free", record_value(q + "payout_fee"), q + "payout_fee")
    if str(record_value(q + "funded_consistency_rule")) != "none":
        raise TermParseError(f"{q}funded_consistency_rule is no longer 'none'")
    qmicros = int(rv_money(q + "funded_position_limit", r"\((\d+) micros\)"))
    return PlanTerms(
        **common, funded_consistency=None, ladder=((0.0, qmicros // common["micros_per_mini"]),), winning_days=0,
        winning_day_min=None, payout_cap=None, split=None, split_low=_num(split.group(1)),
        split_high=_num(split.group(3)), split_line=_num(split.group(2)),
        profit_ceiling=rv_money(q + "funded_sim_profit_ceiling", r"^(\d+) USD gross profit"), fifth_request=None,
        payout_fee=0.0)                         # verified: "US bank wire free" (parsed above), not U-3's reading


# ------------------------------------------------------------------------------------------------ the corners and runs


@dataclass(frozen=True)
class Settings:
    """One run's reading of each term with two ends (5.2; None where the plan has no such term)."""

    plan: str
    corner: str
    price: float | None = None
    min_days: int | None = None
    lag: int | None = None
    inactivity: bool | None = None
    fee_basis: str | None = None
    fifth_paid: bool | None = None
    peak: str | None = None
    ceiling: str | None = None
    request: str | None = None
    household: bool | None = None
    tier1: str | None = None


def settings_for(plan: str, corner: str, flip: str | None = None) -> Settings:
    """The settings of a corner (5.2's strict or lenient ends) or, with `flip`, the strict corner with one term at its
    lenient end -- or, for QP's `req` and the TradeDay `walked` runs, at the reading beside (7.2)."""
    if corner not in (STRICT, LENIENT, "reference"):
        raise ValueError(f"corner must be strict, lenient or reference, got {corner!r}")
    s = corner == STRICT or corner == "reference"
    if plan == "TS":
        return Settings(plan, corner)
    if plan == "LU":
        out = Settings(plan, corner, household=s)
        return replace(out, household=False) if flip == "household" else out
    if plan == "DT":
        out = Settings(plan, corner, price=price_ends("DT")[0 if s else 1], lag=lag_ends("DT")[0 if s else 1],
                       inactivity=s, fee_basis=STRICT if s else LENIENT)
        flips = {"price": dict(price=price_ends("DT")[1]), "lag": dict(lag=lag_ends("DT")[1]),
                 "inact": dict(inactivity=False), "fees": dict(fee_basis=LENIENT)}
    elif plan == "FP":
        out = Settings(plan, corner, price=price_ends("FP")[0 if s else 1], min_days=min_days_ends("FP")[0 if s else 1],
                       fifth_paid=not s, tier1=STRICT if s else LENIENT)
        flips = {"price": dict(price=price_ends("FP")[1]), "days": dict(min_days=min_days_ends("FP")[1]),
                 "fifth": dict(fifth_paid=True), "news": dict(tier1=LENIENT), "walked": dict(tier1="walked")}
    elif plan == "QP":
        out = Settings(plan, corner, price=price_ends("QP")[0 if s else 1], min_days=min_days_ends("QP")[0 if s else 1],
                       peak="pess" if s else "opt", ceiling=STRICT if s else LENIENT, request="every",
                       tier1=STRICT if s else LENIENT)
        flips = {"price": dict(price=price_ends("QP")[1]), "days": dict(min_days=min_days_ends("QP")[1]),
                 "peak": dict(peak="opt"), "ceil": dict(ceiling=LENIENT), "req": dict(request="cadence"),
                 "news": dict(tier1=LENIENT), "walked": dict(tier1="walked")}
    else:
        raise ValueError(f"unknown plan {plan!r}")
    if flip is None:
        return out
    if corner != STRICT:
        raise ValueError("a one-at-a-time run flips one term from the strict corner (7.2)")
    if flip not in flips:
        raise ValueError(f"{plan} has no term {flip!r}; its flips are {sorted(flips)}")
    return replace(out, **flips[flip])


@dataclass(frozen=True)
class Run:
    name: str
    plan: str
    stream: str
    corner: str
    flip: str | None
    kind: str                 # reference, corner, one_at_a_time, beside
    conditional: bool = False  # run only if P-16's count of 5.5 is not zero


def _runs() -> tuple[Run, ...]:
    out = [Run("TS-16", "TS", "P-16", "reference", None, "reference"),
           Run("TS-14", "TS", "P-14", "reference", None, "reference")]
    for plan in ("LU", "DT", "FP", "QP"):
        for stream in ("16", "14"):
            for c, tag in ((STRICT, "s"), (LENIENT, "l")):
                out.append(Run(f"{plan}-{stream}-{tag}", plan, f"P-{stream}", c, None, "corner"))
        flips = {"LU": (), "DT": ("price", "lag", "inact", "fees"), "FP": ("price", "days", "fifth"),
                 "QP": ("price", "days", "peak", "ceil")}[plan]
        for f in flips:
            out.append(Run(f"{plan}-16-{f}", plan, "P-16", STRICT, f, "one_at_a_time"))
        if plan == "QP":
            out.append(Run("QP-16-req", "QP", "P-16", STRICT, "req", "beside"))
    for plan in ("FP", "QP"):
        out.append(Run(f"{plan}-16-news", plan, "P-16", STRICT, "news", "one_at_a_time", conditional=True))
    for plan in ("FP", "QP"):
        out.append(Run(f"{plan}-16-walked", plan, "P-16", STRICT, "walked", "beside", conditional=True))
    return tuple(out)


RUNS = _runs()


__all__ = ["PLANS", "STRICT", "LENIENT", "UnverifiedTerm", "TermParseError", "record_entry", "record_value",
           "stage2_value", "parse", "parse_money", "Declared", "DECLARED", "LITERAL_TABLES", "RULE_LITERALS", "declared",
           "DT_PRICE_GRID", "price_ends", "min_days_ends", "lag_ends", "lucid_list_price", "fee_schedule", "PlanTerms",
           "plan_terms", "Settings", "settings_for", "Run", "RUNS"]
