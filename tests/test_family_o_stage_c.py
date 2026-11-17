"""F-03 (family O, `prereg/F-03_opening_timing.md`) stage C and the scorecard: the pieces of `extended/opening_stagec.py`
on toy inputs (fast), and run 2 end to end, T-3 and T-12 (slow and heavy, each in a process of its own).

* `tests/fo_run2_synthetic.py` (slow, about three minutes): run 1, then run 2 on `tests/fo_synthetic_data.py`'s
  fixture -- the four purposes authorised in stage C's order, just before their stages; every line (K0 both judged
  forms, C1, C1-close, C2, C3), the five floors (floor (iii) on the design's gate campaign under the gate's declared
  seed), the beside readings, the scorecard's sections for the three designs; nothing written, no judged read.
* `tests/fo_t3_synthetic.py` (slow, about three minutes): T-3 on two generated synthetic bar stores read through the
  reader -- run 1's sections other than `identity`, its states, population and forecast hashes byte-identical when every
  judged-block bar is another seeded walk.
* T-12 (heavy, the lead's, under the lock): A0 at 4 paths and 4 starts on the real data and run 1's A1 (items 4-7)
  at 4 starts (n11), run only when `FO_A0_ROW` names A0's identity row.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from extended import features as F
from extended import opening_stagec as SC
from extended import opening_stats as ST

ROOT = Path(__file__).resolve().parent.parent
ENV = {**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}


def test_years_short_of_63_sessions_pool_with_their_neighbour():
    years = [2024] * 252 + [2025] * 252 + [2026] * 40
    assert SC.pooled_years(years) == {2024: 2024, 2025: 2025, 2026: 2025}
    assert SC.pooled_years([2024] * 30 + [2025] * 100) == {2024: 2025, 2025: 2025}


def test_floor_one_reads_both_sides_by_pooled_year():
    kl = np.array([0, 2, 1, 2])
    ks = np.array([1, 0, 1, 0])
    sel = np.array([True, True, False, True])
    yr = np.array([2024, 2024, 2025, 2026])
    f = SC.floor_resolution(kl, ks, sel, yr, {2024: 2024, 2025: 2025, 2026: 2025})
    assert f["shares"]["overall"] == pytest.approx(2 / 6) and not f["holds"]
    assert f["shares"]["2024"] == pytest.approx(1 / 4) and f["shares"]["2025"] == pytest.approx(1 / 2)
    ok = SC.floor_resolution(np.zeros(40, int), np.ones(40, int), np.ones(40, bool), np.full(40, 2024), {2024: 2024})
    assert ok["holds"]


def test_floors_two_and_three_read_the_gate_row():
    rows = pd.DataFrame({"shift": ["point", "lower_bound"], "enforcement_p": [0.0, 0.0],
                         "pf_growth_on_base_p50": [1.5, 0.2], "realised_to_intended_capped_risk": [0.95, 0.91],
                         "pf_required_p90": [3000.0, 3500.0], "pf_break_even_denial_p50": [0.4, 0.3]})
    g = SC.floor_gate(rows)
    assert g["floor_ii"] and g["floor_iii"] and g["growth_at_bound"] == 0.2 and g["break_even_denial"] == 0.3
    rows.loc[1, "realised_to_intended_capped_risk"] = 0.89
    rows.loc[1, "pf_growth_on_base_p50"] = 0.0
    g = SC.floor_gate(rows)
    assert not g["floor_ii"] and not g["floor_iii"]


def test_the_population_from_the_bars_and_its_check():
    o = np.full(1331, np.nan)
    o[1:900] = 100.0                                                 # bars to 08:00 CT: later marks cannot fill
    sess = ["2024-01-05", "2024-01-08", "2024-01-09"]
    kinds = {"2024-01-05": "b", "2024-01-08": "n", "2024-01-09": "f"}
    arr = {d: (o, o, o, o) for d in sess}
    pof = SC.population_offers(sess, kinds, list(range(0, 961, 5)), arr)
    assert set(pof["date"]) == {"2024-01-05", "2024-01-08"}           # never an FOMC day
    assert pof.loc[pof["day_kind"] == "b", "slot"].min() == F.slot(7, 40)
    assert pof["slot"].max() < 900 and pof["slot"].max() <= F.slot(8, 25)
    walked = pof.assign(population=True)
    assert SC.population_problems(pof, walked) == []
    assert SC.population_problems(pof, walked.iloc[1:])


def test_the_drawn_twin_matches_each_strata_count():
    rng = np.random.default_rng([20261988, 800])
    sessions = [str(d.date()) for d in pd.bdate_range("2024-01-02", periods=80)]
    rows = [(s, m, "n", 2024, True) for s in sessions for m in (0, 30, 60)]
    pop = pd.DataFrame(rows, columns=["date", "slot", "day_kind", "year", "population"])
    pop["c"] = rng.normal(size=len(pop))
    pop["state"] = rng.random(len(pop)) < 0.3
    L = ST.layout(pop, sessions, values=("c",), flags=("state",))
    tw = SC.drawn_twin(L, L.flags["state"], cell=0)
    assert np.array_equal(tw.sum(axis=0), L.flags["state"].sum(axis=0))
    assert np.array_equal(tw, SC.drawn_twin(L, L.flags["state"], cell=0))      # the twin's generator, draw 0


def test_the_frontier_and_the_uniform_valuation():
    card = {"design": {"P": 0.5, "S1": 0.4, "S3a": 0.3, "S5a": 0.2},
            "twin": {"P": 0.4, "S1": 0.3, "S3a": 0.3, "S5a": 0.1},
            "p16": {"P": 0.45, "S1": 0.5, "S3a": 0.2, "S5a": 0.2}}
    assert SC.frontier(card) == {"design": True, "twin": False, "p16": True}
    assert SC.uniform_valuation(0.02, 3.0, 1200.0) == pytest.approx(0.02 * 3.0 * 1200.0 / 4.0)


def _script(name: str, *args: str, timeout: int = 1800) -> dict:
    r = subprocess.run([sys.executable, str(ROOT / "tests" / name), str(ROOT), *args], capture_output=True, text=True,
                       timeout=timeout, env=ENV, cwd=str(ROOT))
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    return json.loads(r.stdout.strip().splitlines()[-1])


@pytest.mark.slow
def test_run2_end_to_end_on_synthetic_inputs():
    got = _script("fo_run2_synthetic.py")
    assert got["run1_code"] == 0 and got["code"] == 0
    assert got["authorised"] == ["stage_C_states", "stage_C_judgement", "stage_C_campaign", "stage_C_scorecard"]
    assert set(got["sections"]) == {"level", "judged", "campaign", "floor", "beside"}
    assert set(got["lines"]) >= {"K0", "C1", "C1_close", "C2", "C3", "a_star", "verdict"}
    assert got["k0_forms"] == ["c1_judged", "c2_judged"] and got["c1_bound_finite"]
    assert got["verdict"] in ("CARRIED", "CLOSED", "not claimed: the judged counts make cons lax")
    assert got["floors"] == ["i", "ii", "iii", "iv", "v"] and "SEED_GATE" in got["floor_iii_seed_role"]
    assert {"kind_decomposition", "kind_share", "L_by_year", "L_q20_corrected_moves", "seeded_twin_draw", "V_p16",
            "V_other", "uniform_lift_valuation", "break_even_denial", "placement_on_growth_at_bound",
            "zero_edge_twin_growth", "s_program_guard", "e_bound_d47", "K0_judged"} <= set(got["beside"])
    assert set(got["journey_sections"]) >= {"scorecard", "extra", "path", "response", "paired", "frontier", "note"}
    assert {"design", "p16", "twin"} <= set(got["journey_designs"]) and got["paired_against"] == ["p16", "twin"]
    assert {"identity_rows", "identity_covered", "selection_sha256", "population_sha256", "purposes",
            "seed_roles", "verdict"} <= set(got["params"])
    assert got["written"] == []
    # section 13's parts (Q-109c): the choice-block beside, the wait as felt, uncertainty and design against luck, the
    # evenness curve, bm63c's place, D-621 (3)'s line (i) noted, the frontier on both blocks
    assert {"wait", "uncertainty", "design_vs_luck", "evenness_curve"} <= set(got["journey_sections"])
    assert {"choice", "judged"} <= set(got["journey_blocks"]) and got["paired_blocks"] == ["choice", "judged"]
    assert {"scorecard", "extra", "path", "response", "paired", "wait", "uncertainty", "design_vs_luck",
            "frontier"} <= set(got["choice_sections"])
    assert "bm63c_0.05" in got["paired_stats"] and got["bm63c_note"]
    assert {"slot_minutes", "trades_per_live_account_day", "share_account_sessions_without_trade",
            "sessions_to_opening", "opening_hour"} <= set(got["wait_measures"])
    assert got["wait_designs"] == ["design", "p16", "twin"] and got["wait_against"] > 0
    assert got["evenness_blocks"] == ["choice", "judged"] and got["luck_rows"] > 0
    assert got["frontier_blocks"] == ["choice", "judged"] and got["beside_0735"] == 4
    assert got["floor_iv_v"] == [True, True]                                    # n5: derived from the gate's call
    assert {"identity_commits", "data_manifest_sha256"} <= set(got["params"])


@pytest.mark.slow
def test_t3_run1_ignores_the_judged_block_of_a_synthetic_store(tmp_path):
    got = _script("fo_t3_synthetic.py", str(tmp_path))
    assert got["codes"] == [0, 0] and got["judged_bars_differ"]
    assert got["same_sections"] and got["forecast_same"] and got["states_same"] and got["population_same"]
    assert got["untagged_judged_read_refused"]


@pytest.mark.heavy
def test_t12_a0_at_four_paths_and_four_starts():
    """T-12: A0's items 2 and 3 (and its item 1, which reads the whole window) at 4 paths and 4 starts -- the real
    data, under the lock, with A0's identity row named by `FO_A0_ROW`."""
    row = os.environ.get("FO_A0_ROW")
    if not row or not (ROOT / "vendor" / "stage2" / "data" / "bars" / "NQ" / "bars.parquet").is_file():
        pytest.skip("T-12 runs only under the lock with the data and A0's identity row (FO_A0_ROW)")
    r = subprocess.run([sys.executable, str(ROOT / "identity" / "family_o_identity.py"), "--row", row, "--paths", "4",
                        "--starts", "4", "--workers", "1"], capture_output=True, text=True, timeout=6 * 3600, env=ENV,
                       cwd=str(ROOT))
    assert r.returncode == 0 and r.stdout.strip().endswith("EXIT 0"), r.stdout[-3000:] + r.stderr[-3000:]
    # n11: T-12 is also A1 items 4 to 6 at 4 starts -- run 1's A1 alone on the real choice block, nothing written
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "fo_opening.py"), "--run", "1", "--a1-only", "--starts",
                        "4", "--workers", "1"], capture_output=True, text=True, timeout=6 * 3600, env=ENV, cwd=str(ROOT))
    assert r.returncode == 0 and "A1 (items 4-7) at 4 starts: HOLDS" in r.stdout, r.stdout[-3000:] + r.stderr[-3000:]
