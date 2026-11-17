"""RD-01 T-11 and T-12's arithmetic (`prereg/RD-01_firm_contracts.md` 4.3-4.5, 4.8, 5, 14.2, 14.3): every rule value the
adapters use comes from its record through a loader that refuses an entry not `verified`, a value stated in text
parsed fail-loud; the values of section 5 come from one table of named constants, each citing its line of 5.2; no rule
literal appears in the adapters outside that table; each plan's per-trade cost schedule is 4.8's. Pure Python: the
records are read as YAML; no engine, no bar."""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from extended import firm_terms as T

ROOT = Path(__file__).resolve().parent.parent
ADAPTERS = [ROOT / "extended" / n for n in ("firm_terms.py", "firm_accounts.py", "firms.py")]


def test_the_loader_refuses_an_entry_not_verified():
    assert T.record_value("daytraders.eod50k.eval_profit_target") == 3000.0
    for key, status in (("daytraders.eod50k.eval_fee", "unverified"), ("daytraders.eod50k.payout_fee", "unstated"),
                        ("tradeday.fastpass_eod50k.eval_min_days", "unverified"),
                        ("daytraders.flat_time", "unverified")):
        with pytest.raises(T.UnverifiedTerm, match=status):
            T.record_value(key)
    with pytest.raises(KeyError):
        T.record_value("no.such.key")
    assert T.stage2_value("xfa_std_cap") == 2000.0
    with pytest.raises(T.UnverifiedTerm):
        T.stage2_value("xfa_seat_frees_at")                    # unverified_human_input_required in Stage 2's ledger


def test_a_text_value_is_parsed_fail_loud():
    with pytest.raises(T.TermParseError):
        T.parse_money(r"(\d+) USD per hour", "nothing like it", "probe")


def test_the_plans_terms_are_the_records():
    dt, fp, qp = T.plan_terms("DT"), T.plan_terms("FP"), T.plan_terms("QP")
    assert (dt.eval_target, dt.eval_mll, dt.eval_lock, dt.eval_consistency) == (3000.0, 2000.0, 0.0, 0.5)
    assert (dt.eval_position_micros, dt.eval_dll, dt.eval_qualifying_days, dt.qualifying_day_min) == (100, 1250.0, 2, 200.0)
    assert (dt.funded_mll, dt.funded_lock, dt.funded_dll, dt.funded_consistency) == (2000.0, 0.0, 1250.0, 0.3)
    assert (dt.winning_days, dt.winning_day_min, dt.request_gate, dt.request_leave, dt.request_increment) == \
        (8, 200.0, 2600.0, 2000.0, 50.0)
    assert (dt.payout_min, dt.payout_cap, dt.split, dt.activation, dt.funded_recurring_fee) == (500.0, 2000.0, 1.0, 5.0, 5.0)
    assert dt.ladder == ((0.0, 10),) and dt.billing == "monthly" and dt.seats == 5 and dt.inactivity_days == 1
    assert (fp.eval_consistency, fp.eval_position_micros, fp.funded_consistency, fp.winning_days, fp.winning_day_min) == \
        (0.45, 50, 0.45, 5, 150.0)
    assert fp.ladder == ((0.0, 2), (2000.0, 3), (4000.0, 4), (6000.0, 5))     # capped at the evaluation's 5 (U-6)
    assert (fp.payout_min, fp.payout_cap, fp.split, fp.fifth_request, fp.lag_days, fp.billing) == \
        (250.0, 1500.0, 0.8, 5, 1, "one_time")
    assert (qp.eval_consistency, qp.ladder, qp.funded_consistency, qp.winning_days, qp.payout_cap) == \
        (0.3, ((0.0, 5),), None, 0, None)
    assert (qp.split_low, qp.split_high, qp.split_line, qp.profit_ceiling, qp.payout_fee) == (0.5, 0.8, 4000.0, 10000.0, 0.0)
    assert (qp.activation, qp.funded_recurring_fee, qp.lag_days) == (0.0, 0.0, 1)
    assert dt.start == fp.start == qp.start == 50000.0


def test_section_5s_constants_cite_their_lines():
    for name, entry in T.DECLARED.items():
        assert entry.cite.startswith("5.2") or entry.cite.startswith("4.8") or entry.cite.startswith("U-"), name
    assert T.price_ends("FP") == (248.0, 99.0) and T.price_ends("QP") == (175.0, 69.0)
    assert T.price_ends("DT") == (250.0, 25.0)
    assert T.DT_PRICE_GRID == tuple(float(x) for x in range(25, 251, 25))
    assert T.min_days_ends("FP") == (7, 3) and T.min_days_ends("QP") == (7, 5)
    assert T.lag_ends("DT") == (3, 1)                            # U-5: the bracket of the other plans' verified lags
    assert T.lucid_list_price() == 165.0                          # m8: the struck list price, from the verified note


def test_the_per_trade_cost_schedules_are_4_8s():
    assert T.fee_schedule("TS") == (1.22, 3.78) and T.fee_schedule("LU") == (1.22, 3.78)
    strict, lenient = T.fee_schedule("DT", "strict"), T.fee_schedule("DT", "lenient")
    assert strict == pytest.approx((1.74, 6.76)) and lenient == pytest.approx((1.02, 3.98))
    assert T.fee_schedule("FP") == pytest.approx((1.90, 5.76)) == T.fee_schedule("QP")


def _numbers_outside_declared(path: Path) -> list[tuple[int, float]]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    skip: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(t, ast.Name) and t.id in T.LITERAL_TABLES for t in targets):
                skip |= {id(n) for n in ast.walk(node)}
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            if id(node) not in skip and float(node.value) in T.RULE_LITERALS:
                out.append((node.lineno, float(node.value)))
    return out


def test_no_rule_literal_in_the_adapters_outside_the_constants_table():
    missing = [p.name for p in ADAPTERS if not p.is_file()]
    assert not missing, f"the adapters are not all built: {missing}"
    bad = {p.name: _numbers_outside_declared(p) for p in ADAPTERS}
    assert not any(bad.values()), bad


def test_the_runs_are_7_3s():
    runs = T.RUNS
    assert len([r for r in runs if not r.conditional]) == 30 and len(runs) == 34
    assert sum(r.kind == "reference" for r in runs) == 2 and sum(r.kind == "corner" for r in runs) == 16
    names = {r.name for r in runs}
    assert {"DT-16-fees", "QP-16-req", "QP-16-ceil", "FP-16-news", "QP-16-walked"} <= names
    strict = T.settings_for("DT", "strict")
    flipped = T.settings_for("DT", "strict", flip="fees")
    assert strict.fee_basis == "strict" and flipped.fee_basis == "lenient"
    assert {k: v for k, v in vars(flipped).items() if k != "fee_basis"} == \
        {k: v for k, v in vars(strict).items() if k != "fee_basis"}
    assert T.settings_for("QP", "lenient").request == "every" and T.settings_for("QP", "strict", flip="req").request == "cadence"
