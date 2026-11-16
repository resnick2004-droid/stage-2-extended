"""Q-76 (E-046 (3)): Q-17's adapter carries a declared funded-account class, `funded_account_cls` (named after
`extended.gate.run_gate`'s keyword, Q-47) -- on synthetic inputs only (no bar, no atlas, no result file).

The engine's part runs in a process of its own (`tests/q76_synthetic.py`: the vendored tree goes on its `sys.path`); this
file asserts what it reports:

* absent, every behaviour is the adapter's before Q-76 (`git show c7ec122:extended/user_beside.py`, pinned by sha256),
  bit for bit, on all 19 responses: the per-start outputs, the pool's tasks, `response_args`, `base_problems`, the
  default forfeiture class;
* a pass-through class (and the vendored `FundedAccount` given) changes nothing but the naming: one last key a start;
* the probe class has its documented effect (no payout requested or paid; the first pass and funding unchanged);
* the forfeiture is composed over a given class, never over one with a household rule of its own;
* bad classes, a class that cannot reach a worker, a Focused Trader response with another class (the engine's own
  rule) and a path already carrying a class are refused before any start runs;
* the identity's comparison (`class_outs_problems`) holds where it should and refuses where it should.

The slow and heavy real-data identities -- U1's start rows (`results/user_journey.csv`, section `start`, all 68
columns) at the keyword's default and with the pass-through class -- are in `tests/test_user_beside.py`
(`--funded-cls both`), run only under the lock.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tests" / "q76_synthetic.py"


@pytest.fixture(scope="module")
def got() -> dict:
    env = {**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    r = subprocess.run([sys.executable, str(SCRIPT), str(ROOT)], capture_output=True, text=True, timeout=900,
                       env=env, cwd=str(ROOT))
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    return json.loads(r.stdout.strip().splitlines()[-1])


def test_the_reference_is_the_adapter_before_q76(got):
    assert got["base_sha_ok"], "git show c7ec122:extended/user_beside.py is not the pinned text"
    assert got["base_had_no_keyword"]


def test_absent_every_output_is_as_before_bit_for_bit(got):
    assert len(got["absent_diff"]) == 19
    assert all(v is None for v in got["absent_diff"].values()), {k: v for k, v in got["absent_diff"].items() if v}
    assert all(got["absent_tasks_same"].values()), got["absent_tasks_same"]
    assert got["absent_named"] == []


def test_absent_the_replay_arguments_and_refusals_are_as_before(got):
    assert len(got["response_args_same"]) == 19 and all(got["response_args_same"].values()), got["response_args_same"]
    assert all(got["base_problems_same"]), got["base_problems_same"]
    assert got["base_problems_refuses_cls"]
    assert got["forfeit_default_same"]


def test_the_campaign_exercises_every_mechanism(got):
    e = got["exercised"]
    assert e["paid_starts_off"] >= 3 and e["denied_starts_50"] >= 1 and e["forfeit_starts_50"] >= 1, e
    assert e["forfeited_payouts_50"] >= 1 and e["rtp_placed"] >= 1, e      # a pending payout forfeited


def test_a_pass_through_class_changes_nothing_but_the_naming(got):
    assert got["pt_name"] == "extended.gate.PassThroughFundedAccount"
    assert len(got["pt_diff"]) == 9                               # every response but the ten Focused Trader models
    assert all(v is None for v in got["pt_diff"].values()), {k: v for k, v in got["pt_diff"].items() if v}
    assert all(got["pt_named"].values()), got["pt_named"]
    assert all(v is None for v in got["fa_diff"].values()), {k: v for k, v in got["fa_diff"].items() if v}
    assert all(got["fa_named"].values()), got["fa_named"]


def test_the_class_is_named_in_the_parameters_only_when_given(got):
    assert got["class_parameters"] == [{}, {"funded_account_cls": "extended.gate.PassThroughFundedAccount"}]


def test_the_probe_class_has_its_documented_effect(got):
    p = got["probe"]
    assert p["named"] and p["no_payout"] and p["absent_pays"] and p["some_funded"] and p["differs"], p
    assert p["first_pass_same"] and p["first_funded_same"], p
    f = got["probe_forfeit"]
    assert f["none_denied"] and f["none_forfeited"] and f["absent_forfeits"], f


def test_the_forfeiture_is_composed_over_a_given_class(got):
    assert all(got["forfeit_composed"].values()), got["forfeit_composed"]


def test_bad_classes_are_refused_before_any_start_runs(got):
    assert len(got["refused_bad_class"]) == 5 and all(got["refused_bad_class"].values()), got["refused_bad_class"]
    assert all(got["refused_bad_class_args"].values()), got["refused_bad_class_args"]
    assert got["refused_local_two_workers"]
    assert got["local_one_worker_runs"]                           # as the gate: pickling is checked for workers only


def test_a_focused_trader_response_with_another_class_is_refused_as_the_engine_refuses_it(got):
    assert len(got["refused_ftp"]) == 10 and all(got["refused_ftp"].values()), got["refused_ftp"]
    assert got["refused_ftp_args"]
    assert got["engine_refuses_ftp_subclass"]


def test_forfeiture_over_a_class_with_its_own_household_rule_is_refused(got):
    assert len(got["refused_forfeit_own_household"]) == 3
    assert all(got["refused_forfeit_own_household"].values()), got["refused_forfeit_own_household"]
    assert got["own_household_off_runs"]


def test_a_path_already_carrying_a_class_is_still_refused(got):
    assert all(got["refused_path_carrying"].values()), got["refused_path_carrying"]


def test_the_class_reaches_a_worker(got):
    t = got["task_given"]
    assert t["length"] == 9 and t["last_is_class"] and t["pickles_back"] and t["same_outputs"], t


def test_the_keyword_defaults_to_none(got):
    assert all(got["signature"].values()), got["signature"]


def test_the_identitys_comparison_holds_and_refuses(got):
    c = got["identity_compare"]
    assert c["pass_through"] == [], c["pass_through"]
    assert c["probe"] and c["not_named"] and c["named_wrong"] and c["fewer"], c
    assert all(got["canonical"].values()), got["canonical"]


@pytest.mark.parametrize("argv", [["--synthetic", "--funded-cls", "both"],
                                  ["--u1-starts", "4", "--funded-cls", "pass_through", "--control", "rtp"],
                                  ["--u1-starts", "4", "--funded-cls", "another"]])
def test_the_identitys_class_option_is_refused_outside_the_u1_comparison(argv):
    """`identity/user_beside_identity.py --funded-cls` applies to the U1 comparison only, and takes none,
    pass_through or both -- refused (exit 2) before anything is read."""
    r = subprocess.run([sys.executable, str(ROOT / "identity" / "user_beside_identity.py"), *argv],
                       capture_output=True, text=True, timeout=300)
    assert r.returncode == 2, r.stdout[-2000:] + r.stderr[-2000:]
    assert "--funded-cls" in r.stderr, r.stderr[-2000:]
    assert "identity HOLDS" not in r.stdout and "authoris" not in r.stdout.lower(), r.stdout
