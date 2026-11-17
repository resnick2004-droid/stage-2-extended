"""F-03 (family O) W1 of the third build read: a scorecard-stage failure never discards stage C's verdict, and the
choice-block beside's refusing checks run before any judged purpose is authorised (`tests/fo_run2_w1.py`, a process of
its own, synthetic inputs; slow, about five minutes)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.slow
def test_w1_the_verdict_is_written_before_the_scorecard_and_its_checks_come_first(tmp_path):
    env = {**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    r = subprocess.run([sys.executable, str(ROOT / "tests" / "fo_run2_w1.py"), str(ROOT), str(tmp_path)],
                       capture_output=True, text=True, timeout=1800, env=env, cwd=str(ROOT))
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    got = json.loads(r.stdout.strip().splitlines()[-1])
    assert got["run1_code"] == 0
    assert got["precheck"]["code"] == 3 and got["precheck"]["authorised"] == []     # refused before any judged read
    assert got["raised"] and got["judged_written"] and got["judged_path"]
    assert got["authorised"] == ["stage_C_states", "stage_C_judgement", "stage_C_campaign"]   # scorecard never ledgered
    assert got["judged_sections"] == ["beside", "campaign", "floor", "judged", "level"] and got["verdict_row"] == 1
    assert not got["journey_written"]
    # Y1: a W2 mismatch planted after C1 and both K0 forms writes the judged file partial and stops before 13
    y = got["y1"]
    assert y["code"] == 3 and y["written"]
    assert y["authorised"] == ["stage_C_states", "stage_C_judgement", "stage_C_campaign"]
    assert {"K0", "C1", "C1_close", "C3", "C2", "verdict"} <= set(y["lines"])
    assert y["k0_forms"] == ["c1_judged", "c2_judged"]
    assert y["partial"] == [True] and y["verdict"] == [y["status"]]
    assert y["status"] in ("CLOSED", "not formed", FO_LAX)
    assert y["status"] == y["status_by_rule"]
    assert y["floor_i_parts"] == ["in_state_unresolved_3r", "taken_flattened"]       # Z1: before the W2 refusal
    # Z3: an exception planted at floor (iii)'s gate call writes the partial file and still propagates
    z = got["z3"]
    assert z["raised"] and z["written"] and z["manifest_partial"] is True
    assert z["authorised"] == ["stage_C_states", "stage_C_judgement", "stage_C_campaign"]
    assert z["partial"] == [True] and z["verdict"] == [z["status"]] and z["status"] == z["status_by_rule"]
    assert len(z["stopped"]) == 1 and z["stopped"][0].startswith("Planted: a planted stage-C failure")
    assert {"K0", "C1", "C1_close", "C3", "C2", "verdict"} <= set(z["lines"])
    assert z["floors"] == ["i"] and z["floor_i_parts"] == ["in_state_unresolved_3r", "taken_flattened"]   # Z1
    assert not z["journey_written"]


FO_LAX = "not claimed: the judged counts make cons lax"

PARTIAL = r'''
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
sys.path.insert(0, str(root / "scripts"))
import fo_opening as FO
nan = float("nan")
k0 = lambda form, lax: {"section": "level", "line": "K0", "form": form, "lax": lax}
line = lambda ln, **kw: {"section": "level", "line": ln, **kw}
floor = lambda f, part, holds: {"section": "floor", "floor": f, "part": part, "holds": holds}
ok = [k0("c1_judged", False), line("C1", passes=True), line("C1_close", passes=True), line("C3", passes=True)]
cases = {
    "nothing": ok,
    "k0_only": [k0("c1_judged", True)] + ok[1:],
    "k0_and_line": [k0("c1_judged", True), line("C1", passes=False)] + ok[2:],
    "floor_i": ok + [floor("i", "in_state_unresolved_3r", True), floor("i", "taken_flattened", False)],
    "k0_and_floor": [k0("c1_judged", True)] + ok[1:] + [floor("i", "taken_flattened", False)],
    "floor_nan": ok + [floor("i", "taken_flattened", nan), floor("i", "in_state_unresolved_3r", None)],
    "c2_bar": ok + [line("C2", passes_bar=False)],
}
print(json.dumps({k: list(FO.partial_status(v)) for k, v in cases.items()} | {"lax": FO.LAX_VERDICT}))
'''


def test_z1_z2_the_partial_status_counts_the_floors_and_says_the_declared_lax_verdict():
    """Z1: a floor row with `holds` False decides (a missing or NaN `holds`, as read back from CSV, does not); Z2: K0
    alone gives the declared verdict "not claimed: the judged counts make cons lax", K0 with a failed line or floor
    `CLOSED`, naming both."""
    env = {**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    r = subprocess.run([sys.executable, "-c", PARTIAL, str(ROOT)], capture_output=True, text=True, timeout=300,
                       env=env, cwd=str(ROOT))
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    got = json.loads(r.stdout.strip().splitlines()[-1])
    assert got["lax"] == FO_LAX
    assert got["nothing"] == ["not formed", []]
    assert got["k0_only"][0] == FO_LAX and len(got["k0_only"][1]) == 1 and "K0" in got["k0_only"][1][0]
    st, why = got["k0_and_line"]
    assert st == "CLOSED" and len(why) == 2 and any("K0" in w for w in why) and any("C1 fails" in w for w in why)
    st, why = got["floor_i"]
    assert st == "CLOSED" and why == ["floor (i) taken_flattened fails"]
    st, why = got["k0_and_floor"]
    assert st == "CLOSED" and len(why) == 2 and any("K0" in w for w in why) and any("floor (i)" in w for w in why)
    assert got["floor_nan"] == ["not formed", []]
    assert got["c2_bar"] == ["CLOSED", ["C2 fails its bar"]]
