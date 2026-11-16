"""Q-100 (the firms reading's A-9, `prereg/DRAFT_RD_firms.md` 4.6, 15, 16, T-15; its re-read's n2): Q-17's adapter
(`extended/user_beside.py`) gains two more declared, off-by-default keywords, generic -- `household_closure` (a route
for the engine's household rule, Stage 2 R7) and `seed_base` (the base the start seeds are drawn from) -- on synthetic
inputs only (no bar, no atlas, no result file).

The engine's part runs in a process of its own (`tests/q100_synthetic.py`: the vendored tree goes on its `sys.path`);
this file asserts what it reports:

* absent, every behaviour is master's adapter at be41efd (pinned by sha256), bit for bit, on all 19 responses -- the
  per-start outputs, the pool's tasks, `response_args`, `base_problems` -- also with the pass-through class and with a
  recorder;
* `household_closure=False` equals absent apart from one named key, on all 19 responses, with the class and with a
  recorder (the records the same); on the path as given, the forfeiture keeping its own True;
* `household_closure=True` is refused for Topstep's class on every response, before any start, as the engine refuses
  it; with a class that declares a household rule, every reading (the class's default, True, False) gives what the
  vendored engine gives called directly, the closing reading closes and the counting reading only counts;
* a seed base equal to 20261920 equals the default apart from naming on all 19; another changes every start's seed by
  the same construction, leaves the responses without an enforcement draw equal apart from the seed, changes the
  ladder's draws, equals the engine called directly at those seeds, and is the recorded start seed;
* composed with the class and the recorder; bad values and a path already carrying the reading refused before any
  start; the parameters' entries, the defaults, a worker's task, the identity's comparison.

The slow and heavy real-data identities -- U1's start rows (`results/user_journey.csv`, section `start`, all 68
columns) at the keywords' defaults and with `household_closure=False` and `seed_base=20261920` given -- are in
`tests/test_user_beside.py` (`--q100 both`), run only under the lock.
"""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tests" / "q100_synthetic.py"
N_RESPONSES, N_NON_FTP = 19, 9


@pytest.fixture(scope="module")
def got() -> dict:
    env = {**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    r = subprocess.run([sys.executable, str(SCRIPT), str(ROOT)], capture_output=True, text=True, timeout=900,
                       env=env, cwd=str(ROOT))
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    return json.loads(r.stdout.strip().splitlines()[-1])


def none_differ(d: dict) -> dict:
    return {k: v for k, v in d.items() if v is not None}


def test_the_reference_is_masters_adapter_before_q100(got):
    assert got["base_sha_ok"], "git show be41efd:extended/user_beside.py is not the pinned text"
    assert got["base_had_no_keywords"]
    assert all(got["signature"].values()), got["signature"]               # every keyword defaults to None


def test_absent_every_output_and_task_is_as_before_bit_for_bit(got):
    assert len(got["absent_diff"]) == N_RESPONSES
    assert not none_differ(got["absent_diff"]), none_differ(got["absent_diff"])
    assert len(got["absent_tasks_same"]) == N_RESPONSES and all(got["absent_tasks_same"].values())
    assert got["absent_named"] == []


def test_absent_composed_with_the_class_and_the_recorder_is_as_before(got):
    assert len(got["absent_with_class_same"]) == N_NON_FTP and all(got["absent_with_class_same"].values())
    r = got["absent_with_recorder_same"]
    assert len(r) == 5 and all(v["outputs"] is None and v["records"] is None and v["tasks"] for v in r.values()), r


def test_absent_the_replay_arguments_and_refusals_are_as_before(got):
    assert len(got["response_args_same"]) == N_RESPONSES and all(got["response_args_same"].values())
    assert all(got["base_problems_same"]), got["base_problems_same"]
    assert got["base_problems_refuses_household"]


def test_the_campaign_exercises_payouts_and_the_ladder(got):
    e = got["exercised"]
    assert e["paid_starts_off"] >= 3 and e["denied_starts_50"] >= 1 and e["denied_starts_50_other"] >= 1, e


def test_household_false_equals_absent_apart_from_naming_on_every_response(got):
    assert len(got["hf_diff"]) == N_RESPONSES and not none_differ(got["hf_diff"]), none_differ(got["hf_diff"])
    assert all(got["hf_named"].values()), got["hf_named"]
    assert all(got["hf_tasks"].values()), got["hf_tasks"]
    assert got["np_bool_named_as_bool"]


def test_household_false_composed_with_the_class_and_the_recorder(got):
    assert len(got["hf_pt_diff"]) == N_NON_FTP and not none_differ(got["hf_pt_diff"]), none_differ(got["hf_pt_diff"])
    assert all(got["hf_pt_named"].values()), got["hf_pt_named"]          # the class's key stays last
    r = got["hf_recorder"]
    assert len(r) == 5 and all(v["outputs"] is None and v["records"] is None and v["tasks"] and not v["problems"]
                               for v in r.values()), r


def test_the_reading_reaches_the_path_and_the_forfeiture_keeps_its_own(got):
    assert all(got["paths"].values()), got["paths"]


def test_household_true_is_refused_for_topsteps_class_as_the_engine_refuses_it(got):
    t = got["true_refused"]
    for k in ("absent_class", "vendored_class", "pass_through", "response_args"):
        assert len(t[k]) == N_RESPONSES and all(t[k].values()), (k, t[k])
    assert got["engine_refuses_true_topstep"]


def test_with_a_household_class_every_reading_is_the_engines_own(got):
    h = got["household"]
    assert set(h) == {f"{c}_{r}" for c in ("strict", "count_only") for r in ("default", "true", "false")}
    assert all(v["against_direct"] is None for v in h.values()), {k: v["against_direct"] for k, v in h.items()}
    assert all(v["named"] for v in h.values()), {k: v["named"] for k, v in h.items()}
    assert all(v is None for v in got["household_other_responses"].values()), got["household_other_responses"]


def test_the_closing_reading_closes_and_the_counting_reading_only_counts(got):
    h = got["household"]
    for k in ("strict_default", "strict_true", "count_only_true"):            # closes, as the engine does
        v = h[k]["view"]
        assert v["readings"] == ["closes_household"] and v["closed"] >= 1 and v["others_closed"] >= 1, (k, v)
        assert v["after_close_ok"], (k, v)
    for k in ("strict_false", "count_only_default", "count_only_false"):      # counts only: the trigger ends alone
        v = h[k]["view"]
        assert v["readings"] == ["count_only"] and v["closed"] == 0 and v["triggered"] >= 1, (k, v)
        assert v["count_only_ok"] and v["outlived"] >= 1, (k, v)
    e = got["household_equal"]
    assert e["strict_true_is_default"] is None and e["count_only_false_is_default"] is None, e
    assert e["strict_false_differs"] and e["count_only_true_differs"], e
    assert e["closing_readings_agree"] is None and e["counting_readings_agree"] is None, e


def test_a_household_class_is_still_refused_where_q76_refuses_it(got):
    assert len(got["household_forfeit_refused"]) == 3 and all(got["household_forfeit_refused"].values())
    assert got["household_ftp_refused"]


def test_the_default_seed_base_given_equals_absent_apart_from_naming(got):
    assert len(got["sd_default_diff"]) == N_RESPONSES
    assert not none_differ(got["sd_default_diff"]), none_differ(got["sd_default_diff"])
    assert all(got["sd_default_named"].values()) and all(got["sd_default_tasks"].values())


def test_another_seed_base_changes_the_start_seeds_and_only_the_ladders_draws(got):
    o = got["other_base"]
    assert o["seeds"] and o["seeds_differ"] and o["start_seed_fn"] and o["named"], o
    assert len(o["no_draw_equal"]) == 13 and not none_differ(o["no_draw_equal"]), none_differ(o["no_draw_equal"])
    assert o["ladder_differs"], o                                               # the ladder's draws changed somewhere
    assert all(v is None for v in o["against_direct"].values()), o["against_direct"]
    assert all(v is None for v in o["default_against_direct"].values()), o["default_against_direct"]
    assert got["np_int_named_as_int"]
    r = got["seed_base_recorded"]
    assert r["outputs"] is None and r["start_seed"] and r["per_start"], r


def test_the_keywords_compose_with_the_class_and_the_recorder(got):
    c = got["composed"]
    assert c["against_direct"] is None and c["recorder_changes_nothing"] is None, c
    assert c["named"] and c["tasks"] and c["recorded_seeds"] and c["both_given_pt"], c
    assert not c["problems"], c["problems"]


def test_bad_values_are_refused_before_any_start_runs(got):
    assert len(got["refused_household"]) == 6 and all(got["refused_household"].values()), got["refused_household"]
    assert all(got["refused_household_args"].values()), got["refused_household_args"]
    assert len(got["refused_seed_base"]) == 7 and all(got["refused_seed_base"].values()), got["refused_seed_base"]


def test_a_path_already_carrying_the_reading_is_still_refused(got):
    assert len(got["refused_path_carrying"]) == 5 and all(got["refused_path_carrying"].values())


def test_the_parameters_name_the_keywords_only_when_given(got):
    assert all(got["parameters"].values()), got["parameters"]


def test_the_keywords_reach_a_worker(got):
    t = got["task_given"]
    assert t["length"] == 11 and t["class"] and t["no_reducer"] and t["keywords"] and t["same_outputs"], t


def test_the_identitys_comparison_holds_and_refuses(got):
    c = got["identity_compare"]
    assert c["given"] == [], c["given"]
    assert c["not_named"] and c["named_wrong"] and c["other_base"] and c["fewer"] and c["default_named"], c
    assert got["identity_given"]


@pytest.mark.parametrize("argv", [["--synthetic", "--q100", "both"],
                                  ["--u1-starts", "4", "--q100", "given", "--control", "rtp"],
                                  ["--u1-starts", "4", "--q100", "another"]])
def test_the_identitys_q100_option_is_refused_outside_the_u1_comparison(argv):
    """`identity/user_beside_identity.py --q100` applies to the U1 comparison only, and takes none, given or both --
    refused (exit 2) before anything is read."""
    r = subprocess.run([sys.executable, str(ROOT / "identity" / "user_beside_identity.py"), *argv],
                       capture_output=True, text=True, timeout=300)
    assert r.returncode == 2, r.stdout[-2000:] + r.stderr[-2000:]
    assert "--q100" in r.stderr, r.stderr[-2000:]
    assert "identity HOLDS" not in r.stdout and "authoris" not in r.stdout.lower(), r.stdout


def test_the_identitys_runs_keep_the_default_comparison_as_before():
    """`identity_runs`: both options at `none` is E-010's comparison alone; `--funded-cls` alone runs as before Q-100;
    `both` on either side puts the default first, once."""
    code = ("import sys; sys.path[:0] = [sys.argv[1], sys.argv[1] + '/identity']; import user_beside_identity as I; "
            "print([I.identity_runs(f, q) for f in ('none', 'pass_through', 'both') for q in ('none', 'given', 'both')])")
    r = subprocess.run([sys.executable, "-c", code, str(ROOT)], capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stderr[-2000:]
    got = ast.literal_eval(r.stdout.strip().splitlines()[-1])
    assert got == [["default"], ["q100"], ["default", "q100"],
                   ["pass_through"], ["pass_through", "q100"], ["default", "pass_through", "q100"],
                   ["default", "pass_through"], ["default", "pass_through", "q100"],
                   ["default", "pass_through", "q100"]], got
