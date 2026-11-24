"""Synthetic unit tests for `identity/h4_registered_constants.py` (E-286, E-247 rm-4).

Pure synthetic files and DataFrames only -- never imports or executes the vendored engine, never reads licensed bars.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import pandas as pd
import pytest

from identity import h4_registered_constants as HRC


def _write_csv(path: Path, header: list[str], rows: list[list[object]]) -> str:
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        for r in rows:
            w.writerow(r)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_read_p14_registered_capacity_and_sha_refusal(tmp_path):
    man = tmp_path / HRC.P14_GATE_MANIFEST
    man.write_text(json.dumps({"parameters": {"trades_per_day_capacity": 44}}), encoding="utf-8")
    sha = hashlib.sha256(man.read_bytes()).hexdigest()
    got = HRC.read_p14_registered_capacity(tmp_path, expected_sha256=sha)
    assert got["design"] == "p14" and got["capacity"] == 44 and got["source_sha256"] == sha

    with pytest.raises(HRC.ConstantsError, match="sha256"):
        HRC.read_p14_registered_capacity(tmp_path, expected_sha256="0" * 64)

    man.write_text(json.dumps({"parameters": {"trades_per_day_capacity": True}}), encoding="utf-8")
    sha2 = hashlib.sha256(man.read_bytes()).hexdigest()
    with pytest.raises(HRC.ConstantsError, match="trades_per_day_capacity"):
        HRC.read_p14_registered_capacity(tmp_path, expected_sha256=sha2)


def test_read_rc_screen_constants_and_mismatch_refusals(tmp_path):
    p = tmp_path / "screen.csv"
    sha = _write_csv(
        p,
        ["section", "cell", "stop_ticks", "slot", "offered", "marks_offered", "busiest_day", "capacity"],
        [
            ["cell", "rc_s100_all", 100, "", "", 3, 25, 25],
            ["marks", "", 100, 0, True, "", "", ""],
            ["marks", "", 100, 5, False, "", "", ""],
            ["marks", "", 100, 10, True, "", "", ""],
            ["marks", "", 100, 20, True, "", "", ""],
            ["marks", "", 50, 0, True, "", "", ""],
        ],
    )
    got = HRC.read_rc_screen_constants(
        tmp_path, design="p15", screen_file="screen.csv", expected_sha256=sha, cell="rc_s100_all", stop_ticks=100
    )
    assert got["busiest_day"] == 25 and got["capacity"] == 25
    assert got["marks_count"] == 3 and got["offered_marks_slots"] == "0 10 20"

    with pytest.raises(HRC.ConstantsError, match="sha256"):
        HRC.read_rc_screen_constants(
            tmp_path, design="p15", screen_file="screen.csv", expected_sha256="a" * 64, cell="rc_s100_all", stop_ticks=100
        )

    # marks_offered mismatch refused
    sha_bad = _write_csv(
        p,
        ["section", "cell", "stop_ticks", "slot", "offered", "marks_offered", "busiest_day", "capacity"],
        [
            ["cell", "rc_s100_all", 100, "", "", 4, 25, 25],
            ["marks", "", 100, 0, True, "", "", ""],
            ["marks", "", 100, 10, True, "", "", ""],
            ["marks", "", 100, 20, True, "", "", ""],
        ],
    )
    with pytest.raises(HRC.ConstantsError, match="offered marks count"):
        HRC.read_rc_screen_constants(
            tmp_path, design="p15", screen_file="screen.csv", expected_sha256=sha_bad, cell="rc_s100_all", stop_ticks=100
        )


def test_search_year_subhash_excludes_heldout_and_is_order_sensitive():
    df_whole = pd.DataFrame(
        {
            "date": ["2020-01-02", "2023-12-29", "2024-01-02"],
            "slot": [0, 5, 10],
            "side": ["long", "short", "long"],
        }
    )
    df_search_only = df_whole[df_whole["date"] <= "2023-12-29"].reset_index(drop=True)
    h1 = HRC.search_year_subhash(df_whole)
    h2 = HRC.search_year_subhash(df_search_only)
    assert h1 == h2
    assert h1["search_trades"] == 2
    assert h1["search_first_date"] == "2020-01-02"
    assert h1["search_last_date"] == "2023-12-29"

    # Mutating a held-out row does not change the search-year sub-hash
    df_whole_mut = df_whole.copy()
    df_whole_mut.loc[2, "side"] = "short"
    assert HRC.search_year_subhash(df_whole_mut) == h1

    # Mutating a search-year row changes the sub-hash
    df_search_mut = df_search_only.copy()
    df_search_mut.loc[0, "side"] = "short"
    assert HRC.search_year_subhash(df_search_mut)["search_trades_sha256"] != h1["search_trades_sha256"]


def test_load_registered_constants_roundtrip_and_tamper_refusal(tmp_path):
    csv_p = tmp_path / "h4_registered_constants.csv"
    rows = [
        ["p14", "a3_brk30_cb20", 0, 44, 44, 0, "", 100, "2020-01-02", "2023-12-29", "1" * 64, "m.json", "2" * 64],
        ["p15", "rc_s100_all", 100, 228, 228, 2, "0 5", 200, "2020-01-02", "2023-12-29", "3" * 64, "s1.csv", "4" * 64],
        ["p16", "rc_s150_all", 150, 210, 210, 2, "0 10", 180, "2020-01-02", "2023-12-29", "5" * 64, "s2.csv", "6" * 64],
    ]
    sha = _write_csv(csv_p, list(HRC.COLUMNS), rows)
    Path(str(csv_p) + ".manifest.json").write_text(json.dumps({"sha256": sha}), encoding="utf-8")

    got = HRC.load_registered_constants(csv_p, expected_sha256=sha)
    assert got["p14"]["capacity"] == 44 and got["p14"]["offered_marks"] == ()
    assert got["p15"]["offered_marks"] == (0, 5)
    assert got["p16"]["offered_marks"] == (0, 10)

    with pytest.raises(HRC.ConstantsError, match="sha256"):
        HRC.load_registered_constants(csv_p, expected_sha256="f" * 64)

    # Tampered CSV fails manifest check even when expected_sha256=None
    csv_p.write_bytes(csv_p.read_bytes() + b"\n")
    with pytest.raises(HRC.ConstantsError, match="manifest"):
        HRC.load_registered_constants(csv_p)


def test_identity_script_obeys_identity_write_rule_and_refuses_results_payload(tmp_path):
    from extended import reader as R

    src = Path(HRC.__file__).read_text(encoding="utf-8")
    assert R.identity_write_problems(src) == []
    with pytest.raises(HRC.ConstantsError, match="IDENTITY_WRITE_RULE"):
        HRC._ensure_outside_results(tmp_path / "results" / "payload.json")
    assert HRC._ensure_outside_results(tmp_path / "scratch" / "payload.json") == tmp_path / "scratch" / "payload.json"

