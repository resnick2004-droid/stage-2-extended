"""RD-01's adapters on toy campaigns through the vendored engine (`prereg/RD-01_firm_contracts.md` 14.3: T-1 to T-7,
T-10, T-12 to T-15's engine parts). `tests/rd01_synthetic.py` runs them in a process of its own (seed 20261992; no bar,
no atlas) and prints its findings; each test here asserts one. The oracles are the declaration's words, recomputed in
the script independently of the adapters' code."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


@lru_cache(maxsize=1)
def found() -> dict:
    env = {**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    p = subprocess.run([sys.executable, str(ROOT / "tests" / "rd01_synthetic.py"), str(ROOT)], capture_output=True,
                       text=True, timeout=900, env=env)
    if p.returncode != 0:
        raise AssertionError(f"the toy campaigns failed:\n{p.stderr[-4000:]}")
    return json.loads(p.stdout.strip().splitlines()[-1])


def test_t1_every_adapter_at_its_topstep_setting_is_the_vendored_class_bit_for_bit():
    r = found()
    assert r["t1_base_paid"] > 0 and r["t1_base_passes"] > 0            # the toy campaign pays: not vacuous
    assert r["t1_twins"] == {k: None for k in ("A-2", "A-3", "A-4", "A-5", "A-7", "A-4+A-7")}
    assert r["t1_ts_args_unchanged"] is True                            # A-1 at TS: the arguments as they are


def test_t2_daytraders():
    r = found()
    assert r["t2_problems"] == []
    seen = r["t2_seen"]
    assert seen["passes"] > 0 and seen["payouts"] > 0 and seen["qd_held"] > 0
    assert seen["rounded"] > 0 and seen["gate_or_share_held"] > 0       # the $50 increment; the held reading
    n_dll, worst, survived = r["t2_dll_run"]
    assert n_dll > 0 and worst >= -1250.0 - 1e-6 and survived > 0       # the soft limit reached, and survived
    assert seen["inactive_c"] + seen["inactive_f"] > 0                  # the closure on the toy's quiet spell
    assert seen["rd_excluded"] > 0                                      # the request day excluded from the count
    assert r["t2_dll"] == [1250.0]
    assert r["t2_top_cell_regimes"] == ["combine top"]                  # at target with days owed: the top cell
    assert r["t2_rules"] == [5, 200.0]
    assert r["t2_gate_window"] == 21 and r["t2_gate_class_has_no_calendar"] is True
    assert r["t2_pro_fee_days_ok"] is True and r["t2_pro_fee_days_n"] > 0
    assert r["t2_fee_basis"] == [pytest.approx([1.74, 6.76]), pytest.approx([1.02, 3.98])]


def test_t3_fast_pass():
    r = found()["t3"]
    for end in ("unpaid", "paid"):
        x = r[end]
        assert x["problems"] == [], end
        assert x["forced"] > 0, end                                     # a request-day cell that trades, forced
        assert x["request_days_traded"] == 0, end                       # ... and no request day traded
        assert x["redealt"] > 0, end                                    # its signal taken by another account
        assert x["ladder"] == [[0.0, 2000.0, 4000.0, 6000.0], [2, 3, 4, 5]], end
        assert x["fifth_ended"] > 0, end
    assert r["unpaid"]["fifth_payouts"] == [4] and r["unpaid"]["fifth_unpaid"] == r["unpaid"]["fifth_ended"]
    assert r["paid"]["fifth_payouts"] == [5] and r["paid"]["fifth_unpaid"] == 0


def test_t4_quick_pay_page_examples_and_bounds():
    t = found()["t4"]
    assert t["floor_at_500"] == [500.0, -1500.0, None]                  # $50,500 with the floor at $48,500
    assert t["after_500_payout"] == [0.0, -1500.0, 250.0, 500.0]        # after $500: $50,000, the floor still $48,500
    assert t["split_6000_3000"] == [pytest.approx(2100.0), 1]           # $1,600 plus $500
    assert t["ceiling_strict"] == [None, 10000.0, 1, 500.0, 0, 0.0]
    assert t["ceiling_lenient"] == [pytest.approx(6800.0), 0.0, 1, 500.0, 1, pytest.approx(6800.0)]
    assert t["cadence"] == [False, False, False, False, True, False, False]
    assert t["every"] == [False, False, True, 5]
    assert t["brackets"] == {"won_at_2": {"won": True, "R_lo": 1.5, "R_hi": 2.0},
                             "lo_1_flatten": {"won": False, "R_lo": 1.0, "R_hi": 1.5},
                             "none": {"won": False, "R_lo": 0.0, "R_hi": 1.0}}
    p = t["peaks"]
    assert p["won_at_2_pess"][:2] == [197.5, -802.5]                    # a tick short of its target
    assert p["won_at_2_opt"][0] == pytest.approx(p["won_at_2_opt"][2])  # the peak is its exit
    assert p["lo_1_flatten_pess"][0] == 147.5                           # a tick short of R_hi's target
    assert p["lo_1_flatten_opt"][0] == 100.0                            # R_lo's target over the flatten's exit
    assert p["none_pess"][0] == 97.5 and p["none_opt"][:2] == [0.0, -1000.0]
    # the trade's own exit ($50 less its loss) stays above the floor it started at (-$150): only its peak breaches it
    assert t["raised_floor_breach"][:3] == [-52.5, -2.5, 1] and 50.0 + t["raised_floor_breach"][3] > -150.0
    assert t["won_at"] == [True, True, False] and t["won_at_refuses_above"] is True


def test_t4_quick_pay_on_the_toy_campaign():
    r = found()["t4_runs"]
    for req in ("every", "cadence"):
        assert r[req]["problems"] == [], req
        assert r[req]["payouts"] > 0 and r[req]["rises"] > 0, req


def test_t5_tradeday_minimum_days_and_the_day_logging_micro():
    r = found()["t5"]
    for k, x in r.items():
        assert x["problems"] == [], k
        assert x["two_a_session"] == 0 and x["one_micro"] is True, k
        assert x["logging_sessions"] == x["logging_oracle"], k
    assert r["FP7"]["logging_sessions"] > 0 and r["FP7"]["redealt"] > 0
    assert r["FP3"]["passes"] >= r["FP7"]["passes"] > 0


def test_t6_the_fee_arithmetic():
    r = found()
    assert r["t6_records_same"] is None and r["t6_never_binds"] is True
    assert r["t6_cash_max_diff"] < 1e-6 and r["t6_subscriptions"] > 0
    assert all(v < 1e-6 for v in r["t6_fields"].values())
    assert r["t6_break_even"][0] == pytest.approx(30.0, abs=1e-5) and r["t6_break_even"][1:] == [None, None]


def test_t7_the_oracles():
    for plan, x in found()["t7"].items():
        assert x["n_funded"] > 0 and x["n_resolved"] > 0, plan
        assert x["mean_gross"] <= 2000.0 + 3.0 * x["se"], plan
        assert x["pass_rate"] <= 0.4 + 3.0 * x["pass_se"], plan
        assert x["fee_bad"] == 0, plan


def test_t10_t12_t13_compositions():
    r = found()
    assert r["t10_ts_unchanged"] is True
    assert r["t10_dt_seams"] == ["combine_account_cls", "funded_account_cls", "payout_lag_days", "payout_timing"]
    assert r["t13_gate_has_no_tier1"] is True
    for k, (sched, twenty_six, want) in r["t12"].items():
        assert twenty_six == pytest.approx(want), k                     # 26 micros: two minis and six micros
    assert r["t12"]["TS"][0] == [1.22, 3.78] and r["t12"]["FP"][0] == pytest.approx([1.90, 5.76])
    assert r["t12_micros_per_mini"] == 10
    assert r["t13_minutes_day"] is not None
    (n_st, n_wk) = r["t13_counts"]
    assert n_st == n_wk and n_st["open_at_start"] > 0
    assert r["t13_untouched_same"] is True
    per_acct, brute, n, n_led = r["t13_martingale"]
    assert per_acct == brute and n == n_led
    assert r["t13_sessions"]["sessions_above_line"] == 0


def test_t14_the_table_inputs():
    r = found()
    assert r["t14_rules"] == {"TS": [5, 150.0], "DT": [5, 200.0], "FP": [5, 150.0], "QP": [5, 150.0]}
    assert r["t14_fp_problems"] == []


def test_t15_a9_keywords():
    r = found()
    assert r["t15_ts_runner_same"] is None                              # the runner at TS: A-9's own outputs
    assert r["t15_lu_keywords"] == [["funded_account_cls", "household_closure"], False,
                                    "propedge.contract.lucid.LucidFundedAccount", ["funded_account_cls", "seed_base"],
                                    20261990]
    assert r["t15_lu_base_problems"] == []
    assert r["t15_lu_path"] == ["4_to_5pm_ct", False, False]
    assert all(hc is False and cls.endswith("LucidFundedAccount") for hc, cls in r["t15_lu_named"])
    assert r["t15_ladder_seed"] == [20261990, True]
    names, counts = r["t15_dt_runner"][:2], r["t15_dt_runner"][2:]
    assert all(n.endswith("DayTradersFundedInactiveAtCalendar") for n in names) and all(c > 0 for c in counts)
