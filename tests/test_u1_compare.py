"""Q-05: the U1 identity's comparison of start rows (identity/stage2_identity.py `u1_compare`), on synthetic rows --
money and the ratio to 1e-6, counts and days exactly, text exactly, every column of the file, blanks equal to blanks,
a number the reader parsed as a float equal to the same digits as text. Pure Python: nothing vendored is imported."""
from __future__ import annotations

import importlib.util
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("s2x_identity", ROOT / "identity" / "stage2_identity.py")
I = importlib.util.module_from_spec(spec)
spec.loader.exec_module(I)

COLS = ["section", "reading", "config", "arm", "check", "start_day", "start_date", "observed", "pass_days", "payouts",
        "first_pass", "first_payout_cash", "net_month_1", "monthly_mean_over_sd", "exact_runs_differing", "value"]


def ours(**kw):
    r = {"section": "start", "reading": "R", "config": "p14", "arm": "verdict", "start_day": 3,
         "start_date": "2020-01-07", "observed": 252, "pass_days": "12 30", "payouts": 2, "first_pass": 12,
         "first_payout_cash": 1234.5, "net_month_1": -150.25, "monthly_mean_over_sd": 0.4321,
         "exact_runs_differing": ""}
    r.update(kw)
    return r


def ref(**kw):
    # as pandas' default reader hands a mixed file back: numbers as floats, blanks as NaN, day lists as text
    r = {"section": "start", "reading": "R", "config": "p14", "arm": "verdict", "check": math.nan, "start_day": 3.0,
         "start_date": "2020-01-07", "observed": 252.0, "pass_days": "12 30", "payouts": 2.0, "first_pass": 12.0,
         "first_payout_cash": 1234.5, "net_month_1": -150.25, "monthly_mean_over_sd": 0.4321,
         "exact_runs_differing": math.nan, "value": math.nan}
    r.update(kw)
    return r


def test_identical_rows_hold():
    assert I.u1_compare([ours()], [ref()], COLS, "p14 verdict", all_starts=True) == []


def test_money_to_1e6():
    assert I.u1_compare([ours(net_month_1=-150.25 + 5e-7)], [ref()], COLS, "x", all_starts=True) == []
    bad = I.u1_compare([ours(net_month_1=-150.25 + 2e-6)], [ref()], COLS, "x", all_starts=True)
    assert len(bad) == 1 and "net_month_1" in bad[0]


def test_counts_days_and_text_exact():
    for kw, col in (({"payouts": 3}, "payouts"), ({"first_pass": 13}, "first_pass"), ({"pass_days": "12 31"}, "pass_days"),
                    ({"start_date": "2020-01-08"}, "start_date"), ({"reading": "R2"}, "reading")):
        bad = I.u1_compare([ours(**kw)], [ref()], COLS, "x", all_starts=True)
        assert len(bad) == 1 and col in bad[0], (kw, bad)


def test_a_single_day_parsed_as_a_float_is_the_same_text():
    assert I.u1_compare([ours(pass_days="25", exact_runs_differing="21")],
                        [ref(pass_days=25.0, exact_runs_differing=21.0)], COLS, "x", all_starts=True) == []


def test_blanks_and_the_files_other_columns():
    assert I.u1_compare([ours(first_pass=None, monthly_mean_over_sd=math.nan)],
                        [ref(first_pass=math.nan, monthly_mean_over_sd=math.nan)], COLS, "x", all_starts=True) == []
    bad = I.u1_compare([ours(first_pass=None)], [ref()], COLS, "x", all_starts=True)
    assert len(bad) == 1 and "first_pass" in bad[0]
    bad = I.u1_compare([ours()], [ref(value=1.0)], COLS, "x", all_starts=True)     # a column start rows leave blank
    assert len(bad) == 1 and "value" in bad[0]


def test_starts_missing_extra_and_columns_not_in_the_file():
    assert "not in the file" in I.u1_compare([ours(start_day=9)], [ref()], COLS, "x", all_starts=False)[0]
    assert I.u1_compare([ours()], [ref(), ref(start_day=4.0)], COLS, "x", all_starts=False) == []
    assert "not reproduced" in I.u1_compare([ours()], [ref(), ref(start_day=4.0)], COLS, "x", all_starts=True)[0]
    assert "not in the file's columns" in I.u1_compare([ours(extra=1)], [ref()], COLS, "x", all_starts=True)[0]
    assert "twice" in I.u1_compare([ours()], [ref(), ref()], COLS, "x", all_starts=True)[0]
