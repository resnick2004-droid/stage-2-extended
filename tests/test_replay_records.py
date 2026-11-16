"""Q-94 (E-055, E-059; family O's draft 18.1 item 4 and A2): place recording on Q-17's U1 replay -- the same compact
records Q-70 makes for a gate campaign (`extended/place_records.py`), made on the replay through
`extended/user_beside.py`'s declared, off-by-default `recorder` keyword (`extended/replay_records.py`).

The engine's part runs in a process of its own (`tests/q94_synthetic.py`, synthetic inputs only: no bar, no atlas, no
result file); this file asserts what it reports:

* absent, the adapter is Q-76's (`git show 50e31d3:extended/user_beside.py`, pinned by sha256) bit for bit, on all 19
  responses, also with the pass-through class;
* recording changes nothing: every start's output -- its U1 record and everything else -- is the unrecorded run's bit
  for bit, on all 19 responses, with the pass-through class on the 9 it can run, and on P-14's table at both arms;
* the records are consistent with the trades (the ledger's rows in order, the engine's funded records, the openings
  the replay ledger's by Q-35's reading, every routed trade on its own session, the places Q-70's rule's and every one
  reached), the R is the table's, the offers the trade table's, and the wait is the engine's `FundedAccount.days`;
* a hand-checked start; the checks bite on a tampered run; the refusals; a worker's task.

The real-data identity -- U1's start rows for P-16 and P-14 with recording on, every start, against
`vendor/stage2/results/user_journey.csv` (E-010's comparison) -- is `identity/replay_records_identity.py`, heavy, run
only under the lock (the last test here, marked heavy).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "vendor" / "stage2" / "data"
SCRIPT = ROOT / "tests" / "q94_synthetic.py"
IDENTITY = ROOT / "identity" / "replay_records_identity.py"
PLACES = ("b_evaluation", "c_funded_opening", "d_funded_later", "e_paid")


@pytest.fixture(scope="module")
def got() -> dict:
    env = {**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    r = subprocess.run([sys.executable, str(SCRIPT), str(ROOT)], capture_output=True, text=True, timeout=900,
                       env=env, cwd=str(ROOT))
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    return json.loads(r.stdout.strip().splitlines()[-1])


def test_the_reference_is_the_adapter_before_q94(got):
    assert got["base_sha_ok"], "git show 50e31d3:extended/user_beside.py is not the pinned text"
    assert got["base_had_no_recorder"]
    assert got["signature"]                                      # the keyword defaults to None


def test_absent_every_output_and_task_is_as_before_bit_for_bit(got):
    assert len(got["absent_diff"]) == 19
    assert all(v is None for v in got["absent_diff"].values()), {k: v for k, v in got["absent_diff"].items() if v}
    assert all(got["absent_tasks_same"].values()), got["absent_tasks_same"]
    assert len(got["absent_with_class_same"]) == 9 and all(got["absent_with_class_same"].values())


def test_recording_changes_no_output_on_any_response(got):
    assert len(got["on_diff"]) == 19
    assert all(v is None for v in got["on_diff"].values()), {k: v for k, v in got["on_diff"].items() if v}
    assert all(got["on_tasks"].values()), got["on_tasks"]


def test_recording_changes_nothing_with_the_pass_through_class(got):
    assert len(got["pt_on_diff"]) == 9
    assert all(v is None for v in got["pt_on_diff"].values()), {k: v for k, v in got["pt_on_diff"].items() if v}
    assert all(got["pt_tasks"].values()), got["pt_tasks"]
    assert all(v is None for v in got["pt_records_same_as_without"].values()), got["pt_records_same_as_without"]


def test_the_records_have_the_replay_schema_and_no_problem(got):
    assert all(got["columns"].values()), got["columns"]
    assert all(not v for v in got["problems"].values()), {k: v for k, v in got["problems"].items() if v}
    assert all(got["starts_in_order"].values()) and all(got["recorded_keys"].values())
    assert got["campaign_columns"] and got["level_column"]


def test_every_place_is_reached_and_the_counts_are_the_rows(got):
    assert all(got["places_off"][p] > 0 for p in PLACES), got["places_off"]
    assert got["places_off"]["a_every_trade"] == sum(got["places_off"][p] for p in PLACES)
    assert got["places_rows_agree"]


def test_the_records_are_the_replay_ledgers_rows(got):
    d = got["direct"]
    assert d["n_trades"] > 100 and d["n_openings"] >= 5, d
    for k in ("rows", "accounts", "openings", "routed_own_session", "offer_names", "wait_rel_day"):
        assert d[k], (k, d)


def test_q35s_replay_gives_the_same_openings_and_records(got):
    q = got["q35"]
    assert q["openings_same"] and q["records_same"] and q["no_problems"] and q["n"] >= 5, q


def test_the_wait_is_the_engines_funded_days_at_routing(got):
    w = got["probe_wait"]
    assert w["checked"] >= 5 and w["equal"] and w["outputs_as_pass_through"], w


def test_the_hand_checked_start(got):
    h = got["hand"]
    assert h["start_date"] == HAND["start_date"]
    assert h["first_pass"] == HAND["first_pass"] and h["first_funded"] == HAND["first_funded"], h
    assert h["accounts"] == HAND["accounts"], h["accounts"]
    assert h["openings"] == HAND["openings"], h["openings"]
    assert h["trades_by_place"] == HAND["trades_by_place"], h["trades_by_place"]


def test_the_p14_table_r_offers_and_both_arms(got):
    t = got["p14_table"]
    for arm in ("verdict", "point"):
        a = t[arm]
        assert a["on_equals_off"] is None and a["pt_on_equals_off"] is None, a
        assert a["pt_records_same"] is None, a
        assert a["problems"] == [] and a["offers"] == [], a
        assert a["rr_finite"] and a["rr_is_table"] and a["rr_on_menu"] and a["rr_used_le"], a
        assert len(a["rr_used"]) >= 2, a                              # the R field is exercised
        assert a["trades"] > 0 and a["openings"] > 0, a
        assert a["places"]["b_evaluation"] > 0 and a["places"]["c_funded_opening"] > 0, a


def test_the_checks_bite_on_a_tampered_run(got):
    b = got["bite"]
    assert b["clean"] == [], b
    for k in ("opening_removed", "day_row_removed", "trade_moved"):
        assert b[k], (k, b)
    assert got["plain_is_unrecorded"]


def test_the_refusals(got):
    assert len(got["refused"]) == 9 and all(got["refused"].values()), got["refused"]
    assert got["carrying_without_recorder_runs"]


def test_kept_columns_and_a_workers_task(got):
    assert all(got["kept"].values()), got["kept"]
    t = got["task_given"]
    assert t["length"] == 10 and t["class"] and t["pickles_back"] and t["reducer"], t
    assert t["same_outputs"] and t["same_records"], t


def test_the_field_lists_are_documented():
    from extended import place_fields as PF

    assert PF.problems() == []
    assert PF.REPLAY_TRADE_COLUMNS[:7] == ("design", "arm", "response", "enforcement_p", "start_day", "start_date",
                                           "start_seed")
    for name in ("offer", "rr", "place", "account", "account_session", "pnl", "balance_after", "session_balance"):
        assert name in PF.REPLAY_TRADE_COLUMNS, name
    for name in ("opened", "opening_day", "opening_session", "activation_day", "days"):
        assert name in PF.REPLAY_ACCOUNT_COLUMNS, name
    assert not ((set(PF.GATE_CAMPAIGN) - {"enforcement_p"}) & set(PF.REPLAY_TRADE_COLUMNS))


@pytest.mark.parametrize("argv", [[], ["--u1-starts", "0"], ["--u1-starts", "4", "--funded-cls", "another"]])
def test_the_identitys_arguments_are_refused_before_anything_is_read(argv):
    r = subprocess.run([sys.executable, str(IDENTITY), *argv], capture_output=True, text=True, timeout=300)
    assert r.returncode == 2, r.stdout[-2000:] + r.stderr[-2000:]
    assert "identity HOLDS" not in r.stdout


def test_the_identity_is_refused_without_its_decision_row():
    # Q-48's rule: the read is authorised under the identity's own row first; a row that is not in the log is refused
    # (E-99999 can never be a row of this log, so this test never starts a real read)
    r = subprocess.run([sys.executable, str(IDENTITY), "--u1-starts", "4", "--row", "E-99999"], capture_output=True,
                       text=True, timeout=300)
    out = r.stdout + r.stderr
    assert r.returncode == 3, out[-4000:]
    assert "REFUSED" in r.stdout and "EXIT 3" in r.stdout, out[-4000:]
    assert "the inputs" not in r.stdout and "identity HOLDS" not in r.stdout, out[-4000:]


@pytest.mark.heavy
def test_u1s_start_rows_with_recording_on_every_start():
    """Heavy (the run lock; the lead's): U1's start rows for P-16 and P-14, both arms, every start, all 68 columns, with
    the replay's place recording on -- and every start's records consistent."""
    if not ((DATA / "bars").is_dir() and (DATA / "atlas").is_dir()):
        pytest.skip("bars and atlas not copied (scripts/vendor_stage2.py --data)")
    r = subprocess.run([sys.executable, str(IDENTITY), "--u1-starts", "all"], capture_output=True, text=True,
                       timeout=4 * 3600)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    assert r.stdout.count("identity HOLDS: Q-94 U1") == 2, r.stdout
    assert r.stdout.count("records HOLD: Q-94") == 2, r.stdout


#: start 14 of the simple campaign (its first session 2023-01-20, the window's block 14), checked by hand for funded
#: accounts 0 to 2 from the start's ledger, day rows and the blocks' formula (the rest pinned as found, their agreement
#: with the engine held by the probe and the direct replay above). Funded 0: Combine 2's balance 1000, 2000, 1500, 2500,
#: 3500 on days 1, 3, 5, 7, 9 passes the $3,000 target on day 9, the account is activated that day (U1's first pass and
#: first funding, 9) and its first session is day 10; day 10's four offers go to Combines 3, 4, 0, 1, which last traded
#: before its stamp, so its session 0 has no trade; day 11's one offer (block 24, 2023-02-03, #0 at 500, in the losing
#: spell 24 mod 13 = 11: -500) is its opening, at session 1 = its relative session 1. Funded 1: Combine 0 passes on day
#: 14 (2500 + 1000), first session 15; days 15 and 16 hand their offers to accounts that waited longer; its opening is
#: day 17's #1 (block 30, 2023-02-13, entry 560, (30 x 7 + 1) mod 5 = 1 < 3: +1000), wait 2. Funded 2: Combine 1 passes
#: on day 17 (2000 + 1000), first session 18 (four offers, four accounts ahead of it), opening day 19's only offer
#: (block 32, 2023-02-15, #0 at 500, (32 x 7) mod 5 = 4: -500), wait 1. Funded 9 is activated on the replay's last
#: close: no session, no opening, its wait censored (-1).
_ACCT = ("account", "activation_day", "days", "trades", "opened", "opening_day", "opening_rel_day", "opening_session")
_OPEN = ("account", "day", "historical_day", "trade_index", "date", "offer", "entry_t", "rel_day", "account_session",
         "pnl", "balance_before")
HAND: dict = {
    "start_date": "2023-01-20", "first_pass": 9.0, "first_funded": 9.0,
    "accounts": [dict(zip(_ACCT, r)) for r in (
        (0, 9, 17, 9, True, 11, 1, 1), (1, 14, 24, 12, True, 17, 2, 2), (2, 17, 24, 12, True, 19, 1, 1),
        (3, 22, 124, 63, True, 25, 2, 2), (4, 22, 26, 13, True, 25, 2, 2), (5, 49, 97, 49, True, 50, 0, 0),
        (6, 54, 92, 46, True, 57, 2, 2), (7, 62, 84, 42, True, 65, 2, 2), (8, 83, 34, 17, True, 85, 1, 1),
        (9, 146, 0, 0, False, -1, -1, -1))],
    "openings": [dict(zip(_OPEN, r)) for r in (
        (0, 11, 10, 0, "2023-02-03", "2023-02-03#0", 500.0, 1, 1, -500.0, 0.0),
        (1, 17, 16, 1, "2023-02-13", "2023-02-13#1", 560.0, 2, 2, 1000.0, 0.0),
        (2, 19, 18, 0, "2023-02-15", "2023-02-15#0", 500.0, 1, 1, -500.0, 0.0),
        (3, 25, 24, 0, "2023-02-23", "2023-02-23#0", 500.0, 2, 2, -500.0, 0.0),
        (4, 25, 24, 1, "2023-02-23", "2023-02-23#1", 560.0, 2, 2, -500.0, 0.0),
        (5, 50, 49, 3, "2023-03-30", "2023-03-30#3", 680.0, 0, 0, -500.0, 0.0),
        (6, 57, 56, 1, "2023-04-10", "2023-04-10#1", 560.0, 2, 2, 1000.0, 0.0),
        (7, 65, 64, 1, "2023-04-20", "2023-04-20#1", 560.0, 2, 2, 1000.0, 0.0),
        (8, 85, 84, 2, "2023-05-18", "2023-05-18#2", 620.0, 1, 1, -500.0, 0.0))],
    "trades_by_place": {"b_evaluation": 104, "c_funded_opening": 9, "d_funded_later": 78, "e_paid": 176},
}
