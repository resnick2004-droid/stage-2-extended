"""F-03 (family O, `prereg/F-03_opening_timing.md` section 13) the scorecard's parts in `extended/opening_journey.py` on
synthetic inputs: the choice block's purge, the wait as a user feels it, every measure's uncertainty and design against
luck, the evenness trade-off curve, `bm63c`'s place and the frontier's directions. The vendored comparisons run in a
process of their own (`tests/fo_journey_vendored.py`); run 2 end to end with these parts is
`tests/test_family_o_stage_c.py`'s slow test.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from extended import opening_journey as J

ROOT = Path(__file__).resolve().parent.parent


def _table(n_sessions: int = 255, first: int = 20) -> pd.DataFrame:
    dates = [str(d.date()) for d in pd.bdate_range("2023-01-02", periods=n_sessions)]
    starts = list(range(first, n_sessions))
    t = pd.DataFrame({"start_day": starts, "start_date": [dates[s] for s in starts],
                      "observed": [min(252, n_sessions - s) for s in starts]})
    for m in J.OUTCOME_MONTHS:
        t[f"net_month_{m}"] = np.where(t["observed"] >= 21 * m, 1.0, np.nan)
    t["months_ahead"] = np.where(t["observed"] >= 63, 2.0, np.nan)
    return t


def test_the_purge_cuts_each_start_to_the_blocks_last_start_and_blanks_what_lies_past_it():
    t = _table()
    p = J.purged_table(t)
    last = int(t["start_day"].max())
    assert (p["observed"] == np.minimum(t["observed"], last - t["start_day"])).all()
    k = p["start_day"] == last - 63
    assert int(p.loc[k, "observed"].iloc[0]) == 63 and np.isfinite(p.loc[k, "net_month_3"]).all()
    k = p["start_day"] == last - 62                               # its month 3 would reach the last start's session
    assert np.isnan(p.loc[k, "net_month_3"]).all() and np.isnan(p.loc[k, "months_ahead"]).all()
    assert J.eligible(p, "choice", 63).sum() == (t["start_day"] <= last - 63).sum()


def test_the_judged_block_is_the_starts_from_2024_with_the_horizon_left():
    t = pd.DataFrame({"start_day": [0, 1, 2], "start_date": ["2023-12-28", "2024-01-02", "2024-01-03"],
                      "observed": [252, 252, 10]})
    assert J.eligible(t, "judged", 21).tolist() == [False, True, False]
    with pytest.raises(ValueError):
        J.eligible(t, "all", 21)


def test_p14s_choice_series_takes_the_same_purge():
    dates = [str(d.date()) for d in pd.bdate_range("2020-01-02", "2023-12-29")]
    a = pd.Series(1.0, index=dates)
    got = J.p14_choice(a, dates)
    assert got.index.min() == "2021-01-04" and got.index.max() == dates[len(dates) - 1 - 63]


def test_the_wait_as_felt_pools_trades_over_live_account_days():
    opens = pd.DataFrame({"start_day": [0, 0, 1], "opening_session": [0, 5, 2],
                          "offer": ["2024-01-02|60", "2024-01-03|900", "2024-01-03|300"]})
    funded = pd.DataFrame({"start_day": [0, 0, 0, 1], "account": [0, 0, 1, 0], "day": [3, 3, 9, 4]})
    accounts = pd.DataFrame({"start_day": [0, 0, 1], "account": [0, 1, 0], "days": [10, 6, 4]})
    rows, pooled = J.wait_rows("design", "judged", opens, funded, accounts, np.array([30.0, 90.0, 60.0]))
    assert pooled["trades_per_live_account_day"] == pytest.approx(4 / 20)
    assert pooled["share_account_sessions_without_trade"] == pytest.approx(1 - 3 / 20)
    assert pooled["slot_minutes"] == pytest.approx(60.0)
    by = {(r["measure"], r["stat"]): r["value"] for r in rows}
    assert by[("trades_per_live_account_day", "p50")] == pytest.approx((3 / 16 + 1 / 4) / 2)
    assert by[("opened_inside_wait", "share")] == pytest.approx(2 / 3)
    assert by[("opening_hour", "share_18")] == pytest.approx(1 / 3)          # slot 60 is 18:00 CT
    assert by[("opening_hour", "share_08")] == pytest.approx(1 / 3)          # slot 900 is 08:00 CT
    d = J.against({"design": pooled, "p16": {k: v / 2 for k, v in pooled.items()}}, "judged")
    assert {r["measure"] for r in d} == set(pooled) and all(r["against"] == "p16" for r in d)


def test_slot_minutes_read_the_exit_at_the_openings_own_r():
    trades = pd.DataFrame({"date": ["2024-01-02", "2024-01-02"], "decision_slot_minutes": [60, 120],
                           "entry_t": [61.0, 121.0], "exit_t_3": [151.0, 300.0], "exit_t_1": [70.0, 130.0]})
    opens = pd.DataFrame({"offer": ["2024-01-02|60", "2024-01-02|120"], "rr": [3.0, 1.0]})
    assert J.slot_minutes(opens, trades).tolist() == [90.0, 9.0]
    with pytest.raises(ValueError):
        J.slot_minutes(pd.DataFrame({"offer": ["2024-01-02|65"], "rr": [3.0]}), trades)


def test_time_to_event_measures_are_read_censored_and_money_among_the_reached():
    t = pd.DataFrame({"start_day": [0, 1, 2], "start_date": ["2024-01-02"] * 3, "observed": [252] * 3,
                      "first_pass": [10.0, np.nan, 500.0], "spent_before_first_pass": [100.0, 200.0, 300.0]})
    assert J.measure_values(t, "judged", "first_pass", 126, "censored").tolist() == [10.0, 127.0, 127.0]
    assert J.measure_values(t, "judged", "spent_before_first_pass", 126, "reached:first_pass").tolist() == [100.0]


def test_the_evenness_curve_orders_designs_and_prices_each_step():
    rows = []
    for d, P, e in (("design", 0.50, 0.6), ("twin", 0.45, 0.5), ("p16", 0.55, 0.4)):
        base = {"block": "judged", "arm": "verdict", "design": d, "response": "off"}
        rows += [{**base, "section": "scorecard", "measure": "P", "stat": "value", "value": P},
                 {**base, "section": "path", "measure": "share_months_positive", "stat": "p50", "value": e}]
    cur = [r for r in J.evenness_curve_rows(rows, ("design", "twin", "p16"))
           if r["measure"] == "share_months_positive"]
    assert [r["design"] for r in cur] == ["p16", "twin", "design"]          # least even to most even
    assert cur[1]["P_change"] == pytest.approx(-0.10) and cur[1]["evenness_gained"] == pytest.approx(0.1)
    assert cur[1]["P_change_per_unit_evenness"] == pytest.approx(-1.0)
    assert cur[2]["P_change_per_unit_evenness"] == pytest.approx(0.5)


def test_bm63c_is_a_note_until_its_table_is_pinned_and_a_wrong_pin_refuses(tmp_path):
    assert J.BM63C_TABLE is None and J.bm63c_table() is None
    r = J.bm63c_rows("design", "p14", np.zeros(300), None)
    assert len(r) == 1 and np.isnan(r[0]["value"]) and "not pinned" in r[0]["note"]
    f = tmp_path / "t.csv"
    f.write_text("level,critical\n0.05,2.5\n", encoding="utf-8")
    with pytest.raises(ValueError):
        J.bm63c_table(("t.csv", "0" * 64), root=tmp_path)
    tab = J.bm63c_table(("t.csv", hashlib.sha256(f.read_bytes()).hexdigest()), root=tmp_path)
    assert tab == {0.05: 2.5}


def test_against_the_vendored_definitions():
    env = {**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    r = subprocess.run([sys.executable, str(ROOT / "tests" / "fo_journey_vendored.py"), str(ROOT)],
                       capture_output=True, text=True, timeout=600, env=env, cwd=str(ROOT))
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    got = json.loads(r.stdout.strip().splitlines()[-1])
    assert all(got["purge_same"].values()), got["purge_same"]
    assert got["purge_drops_more_than_the_end"] == 1          # Stage 2's purge drops one start more than the job's end
    assert got["frontier_same"]
    assert got["luck_same"] and got["luck_shares_sum"] == pytest.approx(1.0)
    assert got["n_eff_lags"] == {f"net_month_{m}": 21 * m for m in (1, 2, 3, 6, 12)} and got["n_eff_same"]   # x1
