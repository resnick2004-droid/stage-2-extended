"""Q-70: the place-recording adapter (`extended/place_records.py`, through `extended/gate.py`'s `recorder` keyword) --
families B's C2 and O's value line record, for every simulated trade of a gate campaign, the offer it took, its R, its
place and what the engine booked. Held to its identities (`identity/place_records_identity.py`), each run in its own
process (the vendored tree goes on its `sys.path`).

* fast, in this process (engine-free): the field list is documented -- every field names its meaning, its engine
  source and the draft lines that need it, every draft source is used, and both drafts name the adapter;
* fast (`--synthetic`): on synthetic campaigns through the vendored engine -- the gate with recording on equals the
  gate with it off (rows exactly, every path's record exactly, the gate flag), on simple synthetic blocks and on P-14's
  own table, sizing, strict rule and budget over trades walked on `extended.synthetic_bars`; every field present; the
  records consistent with the paths (each path's rows its trade count, its places the vendored `records_counts`', its
  balances chained, its offers and dates the blocks', R the table's); two path workers equal one; the refusals;
* heavy (`--paths 4`, under the run lock, the lead's): P-16's registered gate call through the adapter, recording on
  and off, equals the first 4 paths of `rc_s150_all_gate_paths.csv` on every `PATH_COLS` column, both shifts, to 1e-6,
  with the records consistent;
* heavy (`--value-map 100`, under the run lock, the lead's): P-16's and P-14's registered campaigns at 100 paths, the
  bound arm at 0 %, give trades a year by place equal to `u_value_map.csv`'s `trades_per_year_records` (D-668's U2
  records), with the first 100 paths equal to the registered paths files.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "vendor" / "stage2" / "data"
SCRIPT = ROOT / "identity" / "place_records_identity.py"

SYNTHETIC_CHECKS = (
    "sources pinned", "wrong pin refused", "signature mirrors the vendored campaign",
    "simple: recording on equals off", "simple: records consistent and every field present",
    "simple: every place reached", "P-14 table: recording on equals off",
    "P-14 table: records consistent and every field present", "P-14 table: every place reached",
    "P-14 table: offers, dates and sides are the blocks'", "P-14 table: R is the table's",
    "P-14 table: trades a year by place", "kept columns equal the full record's", "two workers equal one",
    "refusals",
)


def run(*args: str, timeout: int = 900) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, timeout=timeout)


def test_the_field_list_is_documented_with_its_draft_sources():
    from extended import place_fields as PF

    assert PF.problems() == []
    names = PF.by_name()
    # the three things both drafts ask of every simulated trade: the offer, its R, its place
    for name in ("offer", "historical_day", "trade_index", "date", "rr", "place"):
        assert name in names, name
        assert any(k.startswith("B-") for k in names[name].needed_by), name
    for name in ("offer", "rr", "place", "account_session"):
        assert any(k.startswith("O-") for k in names[name].needed_by), name
    # the brief's place: path, account, the account's state, session, time, and what the engine booked
    groups = {f.group for f in PF.TRADE_FIELDS}
    assert groups == set(PF.GROUPS)
    for name in ("path", "account", "session_balance", "day", "entry_t", "pnl", "balance_after"):
        assert name in names, name
    assert PF.TRADE_COLUMNS[:2] == ("shift", "enforcement_p")
    assert "opening_session" in PF.ACCOUNT_COLUMNS
    for draft in ("DRAFT_F-B_multifeature.md", "DRAFT_F-O_opening_timing.md"):
        text = (ROOT / "prereg" / draft).read_text(encoding="utf-8")
        assert "place-recording adapter" in text, draft
    assert "trades" in PF.describe()


def test_recording_changes_nothing_and_the_records_are_consistent_on_synthetic_campaigns():
    r = run("--synthetic")
    out = r.stdout + r.stderr
    assert r.returncode == 0, out[-6000:]
    assert "synthetic identity HOLDS" in r.stdout, out[-6000:]
    for check in SYNTHETIC_CHECKS:
        assert f"holds: {check}" in r.stdout, f"{check!r} not reported as holding:\n{out[-6000:]}"


@pytest.mark.parametrize("mode", [("--paths", "4", "--only", "p16"), ("--value-map", "100")])
def test_a_real_data_mode_is_refused_before_any_engine_work_without_its_decision_row(mode):
    # Q-48's rule: the read is authorised under the identity's own row first; a row that is not in the log is refused
    # (E-99999 can never be a row of this log, so this test never starts a real read)
    r = run(*mode, "--row", "E-99999", timeout=300)
    out = r.stdout + r.stderr
    assert r.returncode == 3, out[-4000:]
    assert "REFUSED" in r.stdout and "EXIT 3" in r.stdout, out[-4000:]
    assert "registered gate call" not in r.stdout and "records basis" not in r.stdout, out[-4000:]


@pytest.mark.heavy
def test_the_recording_gate_reproduces_p16_registered_gate_paths_at_four_paths():
    if not ((DATA / "bars").is_dir() and (DATA / "atlas").is_dir()):
        pytest.skip("bars and atlas not copied (scripts/vendor_stage2.py --data)")
    r = run("--paths", "4", "--only", "p16", timeout=3600)
    out = r.stdout + r.stderr
    assert r.returncode == 0, out[-6000:]
    for arm in ("recording off", "recording on"):
        assert f"identity HOLDS: P-16 gate through extended.gate ({arm})" in r.stdout, out[-6000:]
    assert "records HOLD: P-16" in r.stdout, out[-6000:]


@pytest.mark.heavy
def test_the_place_counts_reproduce_the_value_maps_records_at_100_paths():
    if not ((DATA / "bars").is_dir() and (DATA / "atlas").is_dir()):
        pytest.skip("bars and atlas not copied (scripts/vendor_stage2.py --data)")
    r = run("--value-map", "100", timeout=7200)
    out = r.stdout + r.stderr
    assert r.returncode == 0, out[-6000:]
    for design in ("P-16", "P-14"):
        assert f"value-map identity HOLDS: {design}" in r.stdout, out[-6000:]
