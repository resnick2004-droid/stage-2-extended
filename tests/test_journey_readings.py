"""Wave 3.1 (`docs/MEASURES.md` section 6): the journey's window on Q-17's adapter (`user_beside.run_starts(...,
journey=True)`) and the readings on it (`extended/user_readings.py`) -- on synthetic inputs only (no bar, no atlas, no
result file). The engine's part runs in a process of its own (`tests/w31_synthetic.py`); this file asserts what it
reports:

* absent, the adapter is master c35cf40's bit for bit on all 19 responses (outputs and tasks), and the readings with
  Q-44's blocks named are c35cf40's bit for bit (rows and per-start table, both finding no problem) on a campaign with
  no net in (0, 1e-6] -- the one place m-11's "ahead above 1e-6" could change a registered row;
* the default is the search years, and it refuses whole-window outputs; the registered blocks refuse journeys;
* with the keyword, every long run stops at its block's last session and reads no session of another block; uncut
  starts equal the absent run apart from the `journey` key (before `seed`); the journey's fields are its run's;
* a calendar with a date outside both blocks, out of order, or a keyword not a bool, is refused before any start;
* the keyword composes with a declared funded class; the task carries `True` fourteenth;
* on journeys the readings hold their refusing checks, `P_B` and its sub-reading equal a second code path's
  (`journey_measures.p_bankroll` from each journey's `rel`), and (24)'s three states sum to one.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tests" / "w31_synthetic.py"


@pytest.fixture(scope="module")
def got() -> dict:
    env = {**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    r = subprocess.run([sys.executable, str(SCRIPT), str(ROOT)], capture_output=True, text=True, timeout=900,
                       env=env, cwd=str(ROOT))
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    return json.loads(r.stdout.strip().splitlines()[-1])


def test_the_references_are_the_code_before_wave_3_1(got):
    assert all(got["base_sha_ok"].values()), got["base_sha_ok"]


def test_absent_the_adapter_is_as_before_bit_for_bit(got):
    assert len(got["absent_diff"]) == 19
    assert all(v is None for v in got["absent_diff"].values()), {k: v for k, v in got["absent_diff"].items() if v}
    assert all(got["absent_tasks_same"].values()), got["absent_tasks_same"]
    assert got["absent_keyed_journey"] == []


def test_the_registered_readings_are_as_before_with_their_blocks_named(got):
    assert got["residue_nets"] == 0, "the campaign holds a net in (0, 1e-6]: the comparison would test m-11"
    assert all(v is None for v in got["readings_diff"].values()), got["readings_diff"]
    assert all(v is None for v in got["table_diff"].values()), got["table_diff"]
    assert all(v == [] for v in got["problems_old"].values()), got["problems_old"]
    assert all(v == [] for v in got["problems_new"].values()), got["problems_new"]


def test_the_default_is_the_search_years_and_refuses_whole_window_outputs(got):
    assert got["defaults"] == {"BLOCKS": ["search"], "Q44_BLOCKS": ["all", "judged"]}
    assert all(v == "ValueError" for v in got["default_refuses_legacy"].values()), got["default_refuses_legacy"]
    assert all(v == "ValueError" for v in got["journey_refuses_registered_blocks"].values())
    assert got["journey_default_block"] == ["search"]


def test_the_journey_stops_at_its_blocks_last_session(got):
    assert got["journey_window_ok"]
    assert got["journey_other_block"] == []
    last = got["last_search"]
    # the cut starts: those whose whole-window run would cross 2023-12-29 -- start 200, last - 40, last
    cut = {int(k.split("|")[1]) for k in got["journey_cut"]}
    assert cut == {200, last - 40, last}, cut
    assert len(got["journey_cut"]) == 3 * 5


def test_uncut_journeys_equal_the_absent_run_apart_from_their_key(got):
    assert got["journey_uncut_compared"] == 5 * 5          # against the absent run with every start checked
    assert got["journey_uncut_diff"] == {}, got["journey_uncut_diff"]
    assert got["journey_key_placed"]
    assert got["journey_rel_ok"] and got["journey_peak_ok"] and got["journey_arrivals_ok"]
    assert got["journey_accounts"] > 0 and got["paid_starts_journey_off"] > 0


def test_a_calendar_outside_the_blocks_is_refused_before_any_start(got):
    assert got["refusals"] == {"holiday": "ValueError", "confirmation": "ValueError", "unordered": "ValueError",
                               "not_a_bool": "TypeError"}
    assert got["refusals_reached_pool"] == 0
    assert got["absent_accepts_any_calendar"]                  # absent: as before


def test_the_keyword_composes(got):
    assert got["journey_task"] == [14, True, True]
    assert got["class_composes"]


def test_the_readings_on_journeys(got):
    for name, s in got["journey_summary"].items():
        assert s["sections"] == ["extra", "journey", "path", "response", "scorecard"], (name, s)
        assert s["blocks"] == ["held_out", "search"], (name, s)
    assert all(v == [] for v in got["journey_problems"].values()), got["journey_problems"]
    assert all(got["journey_pb_equals_recomputed"].values()), got["journey_pb_equals_recomputed"]
    assert all(got["journey_sub_equals_recomputed"].values()), got["journey_sub_equals_recomputed"]
    assert all(got["journey_states_sum_to_one"].values())
    assert all(got["journey_peak_columns"].values())


def test_the_journey_rows_are_not_vacuous(got):
    ex = got["journey_exercised"]
    assert {"share_paid_within", "share_run_out", "share_peak_over"} <= set(ex["states_nonzero"]), ex
    assert ex["accounts"] > 0 and ex["lost"] > 0 and ex["e252"] > 0, ex
    assert any(0 < v < 1 for v in ex["p_b"]), ex


# ------------------------------------------------------------------------------------------------ corrective cycle 1


def test_the_block_check_is_independent_and_catches_the_whole_window_length(got):
    """N-8: the block check is recomputed from the dates alone; the whole-window length (the mutation) crosses the
    block's end on exactly the cut starts, and the runner's own check (`journey_run_problems`) refuses it there and
    passes the journey's length."""
    last = got["last_search"]
    assert {int(k.split("|")[1]) for k in got["legacy_crosses"]} == {200, last - 40, last}
    assert len(got["legacy_crosses"]) == 3 * 5
    assert got["guard_catches_the_mutation"]


def test_m3_a_search_call_never_replays_or_tables_a_held_out_start(got):
    m3 = got["m3"]
    for k in ("default_mixed", "held_out_named_given_search", "block_without_journey", "unknown_block"):
        assert m3[k] == "ValueError", (k, m3[k])
    assert m3["reached_pool"] == 0                          # refused before the pool
    assert m3["default_search_ran"] and m3["held_named_ran"]
    assert m3["search_table_starts"] and m3["search_table_blocks"] == ["search"]


def test_m2_every_start_is_checked_and_a_difference_refuses_unless_declared(got):
    m2 = got["m2"]
    assert got["journey_every_start_checked"]               # exact_every defaults to 1 under the journey
    assert m2["unchecked_refused"] == "ValueError"          # exact_every=21 given: 20 in 21 unchecked
    assert m2["dense_reads"]
    assert m2["difference_refused"] == "ValueError" and m2["difference_refused_by_user_readings"] == "ValueError"
    assert m2["explained_reads"] and m2["empty_reason_refused"] == "ValueError"
    assert m2["cost_ratio_every_start_against_one_in_21"] > 1.0       # reported: the check's cost


def test_m1_p_b_reads_ahead_and_the_peak_from_one_record(got):
    """A start whose exact 63-session run differs (an injected record: the same events, a peak above the budget)
    loses exactly its month-3 count from P_B; with the long run's peak (the mutation) P_B would not move. A missing
    exact peak refuses."""
    m1 = got["m1"]
    assert m1["drop_is_one_month"] and m1["pb_after"] < m1["pb_before"], m1
    assert m1["missing_exact_peak_refused"] == "ValueError"
    assert m1["peak_exact_held"]
