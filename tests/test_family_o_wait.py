"""F-03 (family O, `prereg/F-03_opening_timing.md`) T-5 and T-13's synthetic part: the waiting opening through the
vendored router and lockstep loop (section 5.4; 18.1 items 3 and 4; A1 items 4, 5 and 7).

The engine's part runs in a process of its own (`tests/fo_wait_synthetic.py`, synthetic inputs only: Q-70's walked
synthetic trades under P-14's table, sizing, strict rule and `able` routing, replayed through Q-17's adapter); this file
asserts what it reports. The heavy halves -- A0's whole-window identities and A1 at every choice-block start -- are
`identity/family_o_identity.py` and run 1, under the lock.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tests" / "fo_wait_synthetic.py"
W = 5

#: the hand-checked start (start 50 of the synthetic campaign, the placebo set at W = 5): each funded account's
#: (account, wait session, fallback, offer, in the set), read from the run and checked by hand against its declined
#: offers -- an account's declined offers all fall in its wait before its opening, on offers out of the set, and each
#: in-wait opening's offer is in the set
HAND_OPENINGS = [[0, 3, False, "2021-03-25|1061", True], [1, 4, False, "2021-03-26|1151", True],
                 [2, 3, False, "2021-03-29|971", True], [3, 3, False, "2021-03-30|971", True],
                 [4, 3, False, "2021-04-01|1151", True], [5, 1, False, "2021-05-13|1151", True],
                 [6, 2, False, "2021-05-21|1061", True], [7, 3, False, "2021-06-21|971", True]]
HAND_DECLINED = [[0, 7, 1, 2, "2021-03-24|1061"], [1, 7, 1, 2, "2021-03-24|1061"], [0, 8, 0, 3, "2021-03-25|971"],
                 [1, 8, 0, 3, "2021-03-25|971"], [2, 8, 0, 1, "2021-03-25|971"], [3, 8, 0, 0, "2021-03-25|971"],
                 [1, 9, 0, 4, "2021-03-26|971"], [2, 9, 0, 2, "2021-03-26|971"], [3, 9, 0, 1, "2021-03-26|971"],
                 [4, 13, 0, 3, "2021-04-01|971"], [5, 42, 1, 1, "2021-05-13|1061"], [6, 47, 1, 1, "2021-05-20|1061"],
                 [6, 47, 2, 1, "2021-05-20|1151"], [6, 48, 0, 2, "2021-05-21|971"]]


@pytest.fixture(scope="module")
def got() -> dict:
    env = {**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    r = subprocess.run([sys.executable, str(SCRIPT), str(ROOT)], capture_output=True, text=True, timeout=900, env=env,
                       cwd=str(ROOT))
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    return json.loads(r.stdout.strip().splitlines()[-1])


def test_the_fixture_routes_by_able_with_sizing(got):
    assert got["able"] and got["sized"], "the gate needs the router to ask the sized draw (D-318)"
    assert len(got["starts"]) == 6 and got["sessions"] > 100


def test_the_state_always_on_or_w0_is_the_vendored_class_bit_for_bit(got):
    assert got["always_on"] == [], got["always_on"]
    assert got["w0"] == [], got["w0"]


def test_the_wait_off_with_the_recorder_on_is_the_unrecorded_vendored_replay(got):
    assert got["w0_recorded"] == [], got["w0_recorded"]
    assert got["w0_records_same"], "the class with the wait off changed the records"
    assert got["w0_declined"] == 0 and got["w0_problems"] == []


def test_the_state_never_on_delays_every_opening_past_the_wait(got):
    nv = got["never"]
    assert nv["openings"] > 20 and nv["all_fallback"] and nv["min_session"] == W
    assert nv["at_sixth"] >= 0.8 * nv["openings"]            # most open on the sixth live session itself
    assert nv["declined"] > 0 and nv["declined_inside_wait"] and nv["problems"] == []
    assert got["base_min_session"] < W                       # without the wait some open earlier


def test_the_state_the_placebo_set_opens_only_in_set_inside_the_wait(got):
    p = got["placebo"]
    assert p["problems"] == [] and p["record_problems"] == []
    assert p["in_wait"] > 0 and p["declined"] > 0 and p["declined_off_set"]
    assert set(p["wait_sessions"]) <= set(range(W)) and set(p["in_wait_sessions"]) <= set(range(W))
    assert p["fallback"] == 0 or p["fallback_min"] >= W
    assert p["differs_from_base"]                             # the gate bites


def test_the_wait_is_funded_account_days_zero_to_w_minus_one_at_routing(got):
    o = got["off_by_one"]
    assert o["asked"] > 0 and o["days_is_relative_session"] and o["openings_agree"]


def test_the_hand_checked_start(got):
    h = got["hand"]
    assert h["start"] == 50
    assert [x[:5] for x in h["openings"]] == HAND_OPENINGS
    assert h["declined"] == HAND_DECLINED
    assert got["hand_consistent"]
    for acc, hist, j, wait, offer in h["declined"]:              # each declined offer before its account's opening
        op = next(x for x in HAND_OPENINGS if x[0] == acc)
        assert wait <= op[1] and offer != op[3]


def test_the_forfeiture_composes_over_the_class_and_the_focused_trader_models_are_refused(got):
    assert got["forfeit"] == [], got["forfeit"]
    assert got["ftp_refused"]


def test_the_class_reaches_a_worker_and_its_forfeiture_never_pickles(got):
    assert got["pickles"]
    assert got["forfeit_class_pickles"] is False              # made where the replay runs (Q-76)
    assert got.get("worker_outs_same"), got.get("worker_error")
    assert got["worker_declined_same"] and got["worker_declined"] > 0


def test_a_collected_wrapper_is_impossible_and_the_open_gate_refused(got):
    assert got["held"] and got["released_with_account"]
    assert got["refuses_without_able"]


def test_the_gate_with_the_state_always_on_is_the_gate_without_a_class(got):
    g = got["gate_always_on"]
    assert g["rows_same"] and g["flag_same"] and g["names_class"] and g["sink"] == []
    assert got["gate_never_differs"]
