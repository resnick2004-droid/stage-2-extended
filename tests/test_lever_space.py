"""Q-151: the lever table and its loader (`docs/plans/LEVER_TABLE_topstep50k.md`, `extended/lever_space.py`), on the
real record. The table and the code list the same levers with the same layer, class and source kind. Every
rule-derived bound equals its key's value as `firm_terms` reads it. The loader refuses a lever whose source is "to
compute" or "to declare", a dropped lever, and any lever leaning on a key that is not verified -- on the record as it
stands (A9, A19) and on a record hand-broken here. No rule value is typed in the loader outside its declared table. It
reads rules only: no bar, atlas, trade or result file is opened. Pure Python; fast.

S1's reading (Q-171) may exist in a tree once the lead's clean run has written `results/s1_range.csv`; the tests here
that assert S1's refusal point the loader at an absent file (`no_s1_reading`), so they assert the refusal *before the
reading exists* in every tree. Loading it once it exists is `tests/test_s1_range.py`'s.
"""
from __future__ import annotations

import ast
import builtins
import copy
import io
import re
from datetime import date
from pathlib import Path

import pytest

from extended import day_calendar as DC
from extended import firm_terms as FT
from extended import lever_space as LS
from extended import modes_rules as MR
from extended import modes_terms as M
from extended.firm_terms import UnverifiedTerm

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / LS.TABLE
SRC = ROOT / "extended" / "lever_space.py"
_ROW = re.compile(r"^\| (?P<id>[TSA]\d+b?) \|")
_KIND = {"rule": LS.RULE, "arithmetic": LS.ARITH, "declared": LS.DECL,
         "a search-year reading, to compute": LS.COMPUTE, "to declare": LS.TODECL}


def _doc_rows() -> dict[str, list[str]]:
    rows = {}
    for line in DOC.read_text(encoding="utf-8").splitlines():
        if _ROW.match(line):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            assert len(cells) == 8, f"row {cells[0]} has {len(cells)} cells, not 8"
            assert cells[0] not in rows, f"row {cells[0]} twice"
            rows[cells[0]] = cells
    return rows


def _kind(cell: str) -> str:
    text = cell.replace("*", "").strip().lower()
    for word in sorted(_KIND, key=len, reverse=True):
        if text.startswith(word):
            return _KIND[word]
    raise AssertionError(f"source cell names no kind: {cell!r}")


# ------------------------------------------------------------------------------------------------ the table and the code


def test_the_table_and_the_code_list_the_same_levers() -> None:
    rows = _doc_rows()
    assert list(rows) == list(LS.LEVERS), (sorted(set(rows) ^ set(LS.LEVERS)), "or the order differs")
    for i, cells in rows.items():
        lv = LS.LEVERS[i]
        assert cells[1] == lv.layer, (i, cells[1], lv.layer)
        assert cells[7] == lv.cls, (i, cells[7], lv.cls)
        assert _kind(cells[4]) == lv.source, (i, cells[4], lv.source)
        for k in lv.keys:                                 # every key the loader checks is named in the row
            assert f"`{k}`" in " ".join(cells), (i, k)


def test_every_key_named_exists_in_a_ledger() -> None:
    for lv in LS.LEVERS.values():
        for k in lv.keys:
            assert LS.rule_status(k)[1]


def test_no_rule_value_typed_in_the_table_rows_sourced_from_rules() -> None:
    """A rule row's range is written by key: after the keys and the decision ids, only 0 and 1 may remain."""
    for i, cells in _doc_rows().items():
        if LS.LEVERS[i].source != LS.RULE:
            continue
        text = re.sub(r"`[^`]*`", "", cells[3])
        text = re.sub(r"\b[A-Z]+-\d+[a-z]?\b", "", text)
        nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", text)]
        assert all(x in (0.0, 1.0) for x in nums), (i, nums)


def test_the_counts_by_layer() -> None:
    c = LS.counts()
    assert sum(sum(v.values()) for v in c.values()) == len(LS.LEVERS)
    assert set(c) == set(LS.LAYERS)
    for layer in LS.LAYERS:
        assert c[layer][LS.SEARCHED] > 0


# ------------------------------------------------------------------------------------------------ the refusals


@pytest.fixture
def no_s1_reading(tmp_path, monkeypatch):
    """S1's and T7's readings absent (Q-171, T7): the loader pointed at files that do not exist."""
    monkeypatch.setattr(LS, "S1_PATH", tmp_path / "absent" / "s1_range.csv")
    monkeypatch.setattr(LS, "T7_PATH", tmp_path / "absent" / "t7_forecast.csv")


def test_to_compute_and_to_declare_and_dropped_are_refused(no_s1_reading) -> None:
    for i, lv in LS.LEVERS.items():
        if lv.cls == LS.DROPPED:
            with pytest.raises(LS.DroppedLever):
                LS.bounds(i)
        elif lv.source == LS.COMPUTE:
            with pytest.raises(LS.NotComputed):
                LS.bounds(i)
        elif lv.source == LS.TODECL:
            with pytest.raises(LS.NotDeclared):
                LS.bounds(i)
    assert {i for i, lv in LS.LEVERS.items() if lv.source == LS.COMPUTE} == {"T7", "S1"}


def test_unstated_keys_on_the_real_record_are_refused() -> None:
    assert FT.record_entry("payout_request_amount_choice")["status"] != "verified"
    assert FT.record_entry("hold_expiry_days")["status"] != "verified"
    with pytest.raises(UnverifiedTerm):
        LS.bounds("A19")
    with pytest.raises(UnverifiedTerm):
        LS.bounds("A9")


def test_the_record_wins_over_stage_twos_ledger() -> None:
    """`hold_expiry_days` is verified in Stage 2's ledger and unstated in this repository's record: refused."""
    assert FT._stage2()["hold_expiry_days"]["status"] == "verified"
    with pytest.raises(UnverifiedTerm):
        LS.rule("hold_expiry_days")


def _broken(monkeypatch, key: str, status: str = "unverified") -> None:
    rec = copy.deepcopy(FT._record())
    s2 = copy.deepcopy(FT._stage2())
    if key in rec:
        rec[key]["status"] = status
    else:
        s2[key]["status"] = status
    monkeypatch.setattr(FT, "_record", lambda: rec)
    monkeypatch.setattr(FT, "_stage2", lambda: s2)


@pytest.mark.parametrize("lever,key", [("A6", "max_active_funded_accounts"), ("A12", "back2funded_max_reactivations"),
                                       ("A4", "subscription_fee_naf_50k"), ("T2", "trading_hours"),
                                       ("S3", "combine_mll"), ("A21", "payout_lag_days_ach"),
                                       ("A5", "xfa_payout_path_choice")])
def test_a_hand_broken_key_refuses_its_lever(monkeypatch, lever: str, key: str) -> None:
    LS.bounds(lever)                                      # loads on the record as it stands
    _broken(monkeypatch, key)
    with pytest.raises(UnverifiedTerm):
        LS.bounds(lever)


def test_back2funded_under_naf_is_refused_and_latency_free_sources_collapse() -> None:
    with pytest.raises(UnverifiedTerm):
        LS.check_design({"A4": "naf", "A12": 1})
    LS.check_design({"A4": "naf", "A12": 0})
    LS.check_design({"A4": "standard", "A12": 2})
    assert LS.latency_cells("rl3") == (None,) and LS.latency_cells("p16") == (None,)
    assert LS.latency_cells("coin") == LS.latency_cells("p14") == tuple(LS.declared("latency"))
    with pytest.raises(LS.LeverRefused):
        LS.check_design({"T1": "rl3", "T4": 3})
    LS.check_design({"T1": "coin", "T4": 2})


def test_a_stated_bound_stops_a_declared_upper_end(monkeypatch) -> None:
    rec = copy.deepcopy(FT._record())
    s2 = copy.deepcopy(FT._stage2())
    s2["combine_count_limit"]["value"] = "10"
    s2["account_start_rate_limit"]["value"] = "3 per day"
    monkeypatch.setattr(FT, "_record", lambda: rec)
    monkeypatch.setattr(FT, "_stage2", lambda: s2)
    with pytest.raises(FT.TermParseError):
        LS.bounds("A7")
    with pytest.raises(FT.TermParseError):
        LS.bounds("A11")


# ------------------------------------------------------------------------------------------------ the bounds, by key


def test_rule_bounds_equal_their_keys() -> None:
    s = LS.bounds("A6")
    assert (s.lo, s.hi, s.step) == (1.0, float(FT.stage2_value("max_active_funded_accounts")), 1.0)
    b = LS.bounds("A12")
    assert b.hi == float(FT.record_value("back2funded_max_reactivations")) and b.lo == 0.0
    assert b.detail["window_sessions"] == M.calendar_to_sessions(FT.record_value("back2funded_window_days"),
                                                                 wait=False)
    p = LS.bounds("A4")
    assert p.detail["standard"] == (FT.stage2_value("subscription_fee"), FT.stage2_value("activation_fee"))
    assert p.detail["naf"] == (FT.record_value("subscription_fee_naf_50k"), FT.record_value("activation_fee_naf_50k"))
    assert LS.bounds("S3").hi == float(FT.stage2_value("combine_mll"))
    assert LS.bounds("S4").hi == -float(FT.stage2_value("xfa_mll_start"))


def test_the_stop_caps_and_the_risk_floor() -> None:
    c = LS.stop_caps()
    sa = M.registered_stand_aside()
    assert c["floor_ticks"] == max(sa["combine"][1], sa["funded"][1])
    room = max(float(FT.stage2_value("combine_mll")), -float(FT.stage2_value("xfa_mll_start")))
    assert c["cap_ticks"] * M.tick_values()["MNQ"] <= room < (c["cap_ticks"] + 1) * M.tick_values()["MNQ"]
    r = LS.bounds("S3")
    assert r.lo == c["floor_ticks"] * M.tick_values()["MNQ"] and 0 < r.detail["lo_share"] < 1


def test_the_firms_day_and_its_sessions() -> None:
    td = LS.trading_day()
    v = FT.stage2_value("trading_hours")
    assert f"reopen_{td['reopen'] // 60:02d}:{td['reopen'] % 60:02d}_ct" in v
    assert f"flat_by_{td['flat'] // 60:02d}:{td['flat'] % 60:02d}_ct" in v
    assert 0 < td["last_entry_offset"] <= td["length"]
    for day in (date(2021, 1, 15), date(2021, 7, 15), date(2021, 3, 17)):   # winter, summer, the US/UK mismatch
        w = LS.session_windows(day)
        a = DC.anchored_starts(day)
        assert w["evening"][0] == 0 and w["ny_pm"][1] == td["length"]
        assert w["evening"][1] == w["asia"][0] and w["asia"][1] == w["london"][0] and w["london"][1] == w["ny_am"][0]
        assert (w["asia"][0], w["london"][0], w["ny_am"][0]) == (a["asia"], a["london"], a["ny"])
        assert w["ny_am"][1] == w["ny_pm"][0] == LS.ny_boundary(day) == LS.bounds("T2b").values[0]   # T2b (L-M2)
    assert LS.session_windows(date(2021, 1, 15))["asia"][0] != LS.session_windows(date(2021, 7, 15))["asia"][0]
    with pytest.raises(TypeError):
        LS.session_windows()                                          # a trading day's date is required
    rng = LS.bounds("T2").detail["windows"]
    assert rng["span"] == (DC.SEARCH_START.isoformat(), DC.SEARCH_END.isoformat())
    assert sum(x["days"] for x in rng["distinct"]) == len(LS.trading_dates(DC.SEARCH_START, DC.SEARCH_END))
    assert len(rng["distinct"]) > 1 and rng["range"]["asia"]["start"][0] < rng["range"]["asia"]["start"][1]
    e = LS.bounds("T3")
    assert e.lo == 0.0 and e.hi == float(td["last_entry_offset"]) and e.step == float(LS.declared("mark_step_min"))
    assert LS.bounds("T2").values == tuple(LS.declared("sessions"))


def test_a_session_boundary_outside_the_day_is_refused(monkeypatch) -> None:
    real = DC.anchored_starts
    monkeypatch.setattr(DC, "anchored_starts", lambda d: dict(real(d), ny=16 * 60 - 17 * 60 + 1440))   # 16:00 CT
    with pytest.raises(LS.LeverRefused):
        LS.session_windows(date(2021, 1, 15))


def test_flip_arithmetic_is_rd05s() -> None:
    a1 = LS.bounds("A1")
    t = M.eval_terms("TS-S")
    assert a1.detail["k_E"] == MR.k_eval(t)
    for w, rf in a1.detail["r_flip_by_w"].items():
        assert rf["r_flip"] == pytest.approx(float(FT.stage2_value("combine_profit_target")) / (rf["k"] * w))
    a2 = LS.bounds("A2")
    assert a2.detail["TS/std"]["k_F"] == int(FT.stage2_value("xfa_std_winning_days"))
    assert set(a2.detail) == {"TS/std", "TS/con"}


def test_latency_and_the_operators_dimensions() -> None:
    lat = LS.bounds("T4")
    assert lat.values[0] == LS.declared("latency.reference") and len(lat.values) == 3
    assert LS.bounds("T5").values == ("market", "limit")
    assert LS.bounds("A1").values == LS.bounds("A2").values == ("steady", "flip")
    assert set(LS.declared("sessions")) >= {"asia", "london", "ny_am", "ny_pm"}
    assert LS.bounds("A18").values == tuple(LS.declared("payout_first"))
    assert LS.bounds("A21").values == ("aeropay",)


def test_space_and_refusals_partition_the_levers(no_s1_reading) -> None:
    sp, rf = LS.space(), LS.refusals()
    assert set(sp) | set(rf) == set(LS.LEVERS) and not set(sp) & set(rf)
    assert {"T7", "S1", "A9", "A19"} <= set(rf)
    assert {"T2b", "A15", "A16", "A17"} <= set(sp)                    # declared (E-NNN pending)


# ------------------------------------------------------------------------------------------------ the loader's hygiene


def _read_rule_numbers() -> set[float]:
    out: set[float] = set()
    for lv in LS.LEVERS.values():
        for k in lv.keys:
            try:
                v = LS.rule(k)
            except UnverifiedTerm:
                continue
            if isinstance(v, bool):
                continue
            if isinstance(v, (int, float)):
                out.add(float(v))
            else:
                out |= {float(x) for x in re.findall(r"\d+(?:\.\d+)?", str(v))}
    return out - {0.0, 1.0}


def test_no_rule_value_typed_in_the_loader_outside_its_declared_table() -> None:
    tree = ast.parse(SRC.read_text(encoding="utf-8"))
    skip: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(t, ast.Name) and t.id == "DECLARED" for t in targets):
                skip |= {id(n) for n in ast.walk(node)}
    values = _read_rule_numbers()
    assert values
    bad = [(n.lineno, n.value) for n in ast.walk(tree)
           if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool)
           and id(n) not in skip and float(n.value) in values]
    assert not bad, bad


def test_the_loader_reads_rules_only(monkeypatch, no_s1_reading) -> None:
    for f in (FT._record, FT._stage2, FT._fills, M.registered_stand_aside, M.tick_values, M.topstep_round_turn,
              M.fill_slippage):
        f.cache_clear()
    opened: list[str] = []
    real_open, real_io_open = builtins.open, io.open

    def spy(file, *a, **k):
        opened.append(str(file))
        return real_open(file, *a, **k)

    def spy_io(file, *a, **k):
        opened.append(str(file))
        return real_io_open(file, *a, **k)

    monkeypatch.setattr(builtins, "open", spy)
    monkeypatch.setattr(io, "open", spy_io)
    LS.space()
    LS.refusals()
    norm = [p.replace("\\", "/") for p in opened]
    assert any(p.endswith("config/rules_extended.yaml") for p in norm)
    forbidden = ("/data/bars", "/data/atlas", "/results/", ".parquet", ".csv")
    assert not [p for p in norm if any(f in p for f in forbidden)], norm


def test_the_declared_table_cites_every_entry() -> None:
    for name, d in LS.DECLARED.items():
        assert d.cite and len(d.cite) > 10, name
