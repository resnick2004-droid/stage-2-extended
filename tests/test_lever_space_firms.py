"""Q-151b: the per-firm lever spaces (`extended/lever_space_firms.py`; `docs/plans/LEVER_TABLE_mffu.md`,
`docs/plans/LEVER_TABLE_lucid.md`), on the real record.

- **Topstep unchanged, bit for bit**: every Topstep lever's metadata and `bounds` outcome equals the snapshot written
  from master 1b29e07 before this change (`tests/data/lever_space_topstep_golden.json`, `scripts/lever_space_golden.py`),
  and `lever_space.load('topstep')` is `space()`.
- **Every bound reads its rule key**: each loaded range's `read` holds every key its lever names, equal to the firm's
  reader; hand-breaking any one of them refuses the lever (`UnverifiedTerm`); the numbers equal the keys' own values,
  and agree with RD-05's build and Stage 2's Lucid adapter (the identities below).
- **An unverified key refuses** (`NotVerified`): absent keys, `unverified` and `unstated` entries, and the record winning
  over Stage 2's Lucid ledger.
- **Conduct tier 1 is refused at sampling for every firm**: each marker, each tier-1 lever value, a tampered space.
- The tables and the code list the same levers (layer, class, source kind, keys, the comparison with Topstep), the work
  lists name every unverified key, and no rule value is typed in the loader or in a rule row.

Pure Python on the rules; reads no bar, atlas, trade or result file. S1's Topstep reading is pointed at an absent file
(`no_s1_reading`), so the comparison with Topstep is the one before that reading exists.
"""
from __future__ import annotations

import ast
import builtins
import copy
import importlib.util
import io
import json
import math
import re
from pathlib import Path

import pytest

from extended import firm_terms as FT
from extended import lever_space as LS
from extended import lever_space_firms as LF
from extended import modes_rules as MR
from extended import modes_terms as M
from extended.firm_terms import UnverifiedTerm

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "extended" / "lever_space_firms.py"
GOLDEN = ROOT / "tests" / "data" / "lever_space_topstep_golden.json"
OTHER = ("mffu", "lucid")
_ROW = re.compile(r"^\| (?P<id>[TSA]\d+b?) \|")
_KIND = {"rule": LS.RULE, "arithmetic": LS.ARITH, "declared": LS.DECL,
         "a search-year reading, to compute": LS.COMPUTE, "to declare": LS.TODECL}
SEEDS = (20261120, 20261121, 20261122)          # Q-151b's test draws (synthetic designs; no outcome is read)


@pytest.fixture(autouse=True)
def no_s1_reading(tmp_path, monkeypatch):
    monkeypatch.setattr(LS, "S1_PATH", tmp_path / "absent" / "s1_range.csv")


# ------------------------------------------------------------------------------------------------ Topstep, unchanged


def _golden_module():
    spec = importlib.util.spec_from_file_location("lever_space_golden", ROOT / "scripts" / "lever_space_golden.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_topsteps_loader_output_is_unchanged_bit_for_bit() -> None:
    old = json.loads(GOLDEN.read_text(encoding="utf-8"))
    new = _golden_module().snapshot()
    assert json.loads(json.dumps(new)) == old
    assert list(LS.LEVERS) == [k for k in old if not k.startswith("__")]


def test_topsteps_load_is_its_space() -> None:
    assert repr(LS.load()) == repr(LS.load("topstep")) == repr(LS.space()) == repr(LF.load("topstep"))
    for i in LS.LEVERS:
        try:
            a = repr(LS.bounds(i))
        except (LS.LeverRefused, UnverifiedTerm) as e:
            a = type(e).__name__
        try:
            b = repr(LF.bounds("topstep", i))
        except (LS.LeverRefused, UnverifiedTerm) as e:
            b = type(e).__name__
        assert a == b, i
    assert repr(LS.load("mffu")) == repr(LF.load("mffu"))


# ------------------------------------------------------------------------------------------------ the tables and the code


def _doc_rows(firm: str) -> dict[str, list[str]]:
    rows = {}
    for line in (ROOT / LF.TABLES[firm]).read_text(encoding="utf-8").splitlines():
        if _ROW.match(line):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            assert len(cells) == 9, f"{firm} row {cells[0]} has {len(cells)} cells, not 9"
            assert cells[0] not in rows, f"{firm} row {cells[0]} twice"
            rows[cells[0]] = cells
    return rows


def _kind(cell: str) -> str:
    text = cell.replace("*", "").strip().lower()
    for word in sorted(_KIND, key=len, reverse=True):
        if text.startswith(word):
            return _KIND[word]
    raise AssertionError(f"source cell names no kind: {cell!r}")


@pytest.mark.parametrize("firm", OTHER)
def test_the_table_and_the_code_list_the_same_levers(firm: str) -> None:
    rows = _doc_rows(firm)
    lv = LF.levers(firm)
    assert list(rows) == list(lv) == list(LS.LEVERS), sorted(set(rows) ^ set(lv))
    cmp = LF.compare(firm)
    for i, cells in rows.items():
        assert cells[1] == lv[i].layer, (i, cells[1])
        assert cells[7] == lv[i].cls, (i, cells[7])
        assert _kind(cells[4]) == lv[i].source, (i, cells[4])
        assert cells[8].replace("*", "").split()[0] == cmp[i], (i, cells[8], cmp[i])
        for k in lv[i].keys:
            assert f"`{k}`" in " ".join(cells), (i, k)


@pytest.mark.parametrize("firm", OTHER)
def test_the_tables_lists_and_work_list_follow_the_code(firm: str) -> None:
    text = (ROOT / LF.TABLES[firm]).read_text(encoding="utf-8")
    cmp = LF.compare(firm)
    for label in (LF.IDENTICAL, LF.DIFFERS, LF.REFUSED):
        m = re.search(rf"^\*\*{label}\*\* \((?P<n>\d+)\): (?P<ids>.*)$", text, re.M)
        assert m, label
        ids = [x.strip() for x in m.group("ids").rstrip(".").split(",")]
        assert ids == [i for i, v in cmp.items() if v == label], label
        assert int(m.group("n")) == len(ids)
    work = text.split("## 6.", 1)[1]
    for k in LF.unverified_keys(firm):
        assert f"`{k}`" in work, k


@pytest.mark.parametrize("firm", OTHER)
def test_no_rule_value_typed_in_the_rule_rows(firm: str) -> None:
    for i, cells in _doc_rows(firm).items():
        if LF.levers(firm)[i].source != LS.RULE:
            continue
        text = re.sub(r"`[^`]*`", "", cells[3])
        text = re.sub(r"\b[A-Z]+-\d+[a-z]?\b", "", text)
        nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", text)]
        assert all(x in (0.0, 1.0) for x in nums), (firm, i, nums)


@pytest.mark.parametrize("firm", OTHER)
def test_counts_and_partition(firm: str) -> None:
    c = LF.counts(firm)
    assert sum(sum(v.values()) for v in c.values()) == len(LS.LEVERS)
    sp, rf = LF.load(firm), LF.refusals(firm)
    assert set(sp) | set(rf) == set(LS.LEVERS) and not set(sp) & set(rf)
    for i, lv in LF.levers(firm).items():
        if lv.cls == LS.DROPPED:
            assert rf[i] == "DroppedLever"
        elif lv.source == LS.COMPUTE:
            assert rf[i] == "NotComputed"
        elif lv.source == LS.TODECL:
            assert rf[i] == "NotDeclared"
    assert {i for i, v in LF.compare(firm).items() if v == LF.REFUSED} == {i for i, v in rf.items()
                                                                           if v == "NotVerified"}


# ------------------------------------------------------------------------------------------------ every bound reads its key


def _break(monkeypatch, firm: str, key: str, status: str = "unverified") -> None:
    rec = copy.deepcopy(FT._record())
    s2 = copy.deepcopy(FT._stage2())
    lu = copy.deepcopy(LF._lucid_ledger())
    ledger, _ = LF.rule_status(firm, key)
    if ledger == "record":
        rec[key]["status"] = status
    elif ledger == "stage2":
        s2[key]["status"] = status
    elif ledger == "stage2_lucid":
        lu[key[len(LF.LUCID_P):]]["status"] = status
    else:
        raise AssertionError(f"{key} is in no ledger")
    monkeypatch.setattr(FT, "_record", lambda: rec)
    monkeypatch.setattr(FT, "_stage2", lambda: s2)
    monkeypatch.setattr(LF, "_lucid_ledger", lambda: lu)


@pytest.mark.parametrize("firm", OTHER)
def test_every_loaded_bound_reads_each_of_its_keys(firm: str) -> None:
    sp = LF.load(firm)
    assert sp
    for i, r in sp.items():
        for k in LF.levers(firm)[i].keys:
            assert k in r.read and r.read[k] == LF.rule(firm, k), (i, k)


@pytest.mark.parametrize("firm", OTHER)
def test_a_hand_broken_key_refuses_its_lever(monkeypatch, firm: str) -> None:
    pairs = [(i, k) for i in LF.load(firm) for k in LF.levers(firm)[i].keys]
    assert len(pairs) >= len(LF.load(firm)) // 2
    for i, k in pairs:
        with monkeypatch.context() as m:
            _break(m, firm, k)
            with pytest.raises(UnverifiedTerm):
                LF.bounds(firm, i)
        LF.bounds(firm, i)                                 # loads again on the record as it stands


def _rv(key: str):
    return FT.record_value(key)


def test_mffu_bounds_equal_their_keys() -> None:
    P = LF.MFFU_P
    assert LF.bounds("mffu", "A6").hi == float(re.search(r"Rapid EOD 50K at most (\d+)",
                                                          _rv("mffu.max_funded_accounts")).group(1))
    assert LF.bounds("mffu", "A7").hi == float(min(LS.declared("evals_max"), int(_rv("mffu.max_eval_accounts"))))
    assert LF.bounds("mffu", "S3").hi == float(re.match(r"(\d+) USD", _rv(P + "eval_drawdown")).group(1))
    assert LF.bounds("mffu", "S4").hi == float(re.search(r"(\d+) USD below it", _rv(P + "funded_drawdown")).group(1))
    con = LF.bounds("mffu", "S5").detail["contracts"]
    for phase, key in (("evaluation", "eval_position_limit"), ("funded", "funded_position_limit")):
        a, b = re.match(r"(\d+) mini / (\d+) micro", _rv(P + key)).groups()
        assert con[phase] == (int(a), int(b))
    a1 = LF.bounds("mffu", "A1").detail["RE"]
    c, d, T = float(_rv(P + "eval_consistency")), int(_rv(P + "eval_min_days")), float(_rv(P + "eval_profit_target"))
    assert a1["k_E"] == max(math.ceil(1 / c - 1e-12), d)
    for w, rf in a1["r_flip_by_w"].items():
        assert rf["r_flip"] == pytest.approx(T / (a1["k_E"] * w))
    a5 = LF.bounds("mffu", "A5").detail
    assert a5["payout_min"] == float(_rv(P + "payout_min")) and a5["split"] == float(_rv(P + "payout_split"))
    assert LF.bounds("mffu", "A3").detail["cap_evaluation"]["RE"] == pytest.approx(c * T)


def _lu(key: str):
    return LF._lucid_ledger()[key]["value"]


def test_lucid_bounds_equal_their_keys() -> None:
    assert LF.bounds("lucid", "A6").hi == float(_lu("max_accounts"))
    assert LF.bounds("lucid", "S3").hi == float(_lu("eval_drawdown_amount"))
    assert LF.bounds("lucid", "S4").hi == float(_lu("funded_drawdown_amount"))
    assert LF.bounds("lucid", "A4").detail["one_time_price"]["LU40"] == float(_lu("eval_fee"))
    assert LF.bounds("lucid", "A1").detail["LU40"]["k_E"] == max(math.ceil(1 / float(_lu("eval_consistency_rule"))
                                                                           - 1e-12), int(_lu("eval_min_days")))
    a2 = LF.bounds("lucid", "A2").detail["LU"]
    frac, cap = re.match(r"min\((0\.\d+) \* profits, (\d+)\)", _lu("payout_cap")).groups()
    assert a2["b_star"] == pytest.approx(float(cap) / float(frac))
    assert LF.bounds("lucid", "A5").detail["payout_min"] == float(_lu("payout_min"))


# ------------------------------------------------------------------------------------------------ identities


def test_identity_mffu_against_rd05s_build() -> None:
    """RD-05's `RE` terms (`modes_terms.eval_terms('RE')`, `funded_terms('RE')`), at both corners: the same target,
    room, share, days, contracts, funded floor, buffer and figures."""
    s5 = LF.bounds("mffu", "S5").detail["contracts"]
    a5 = LF.bounds("mffu", "A5").detail
    for corner in (M.STRICT, M.LENIENT):
        t = M.eval_terms("RE", corner)
        f = M.funded_terms("RE", corner)
        assert (t.target, t.mll, t.consistency, t.min_days) == (LF._mffu_eval().target, LF.bounds("mffu", "S3").hi,
                                                                LF._mffu_eval().consistency, LF._mffu_eval().min_days)
        assert (t.allowance.minis, t.allowance.micros) == s5["evaluation"]
        assert (f.allowance.minis, f.allowance.micros) == s5["funded"] and f.allowance.ladder is None
        assert -f.floor_start == LF.bounds("mffu", "S4").hi
        assert (f.buffer, f.since_min, f.payout_min, f.split) == (a5["buffer"], a5["since_min"], a5["payout_min"],
                                                                  a5["split"])
        assert MR.k_eval(t) == LF.bounds("mffu", "A1").detail["RE"]["k_E"]


def test_identity_lucid_against_stage_twos_adapter() -> None:
    """Stage 2's Lucid adapter (`propedge.contract.lucid.lucid_terms`, `lucid_price`; RD-05's `LU40`, `LU50`, `LU`):
    every figure this loader parses equals the adapter's, and the flip arithmetic equals RD-05's."""
    t = M.lucid()
    cons = LF._lucid_consistency()
    assert (cons["LU40"]["consistency"], cons["LU40"]["min_days"]) == (t.eval_consistency, t.eval_min_days)
    assert (cons["LU50"]["consistency"], cons["LU50"]["min_days"]) == (t.eval_consistency_addon, t.eval_min_days_addon)
    assert LF.bounds("lucid", "S3").hi == t.eval_mll and LF.bounds("lucid", "S4").hi == t.funded_mll
    s5 = LF.bounds("lucid", "S5").detail["contracts"]
    assert s5["evaluation"][1] == t.eval_position_micros and s5["funded_ladder"] == t.funded_ladder
    g = LF._lucid_gate()
    assert (g["winning_days"], g["winning_day_min"], g["cycle_net_min"], g["max_payouts"]) == (
        t.winning_days, t.winning_day_min, t.cycle_net_min, t.max_payouts)
    assert LF._lucid_cap() == {"frac": t.payout_frac_of_profit, "cap": t.request_cap}
    acc = LF._lucid_accounts()
    assert (acc["funded"], acc["total"], acc["evaluations"]) == (t.max_funded, t.max_total_accounts,
                                                                 t.eval_count_limit)
    prices = LF.bounds("lucid", "A4").detail["one_time_price"]
    for cfg in LF.LUCID_CONFIGS:
        assert prices[cfg] == M.lucid_one_time(M._lucid_config(cfg))
        et = M.eval_terms(cfg)
        a1 = LF.bounds("lucid", "A1").detail[cfg]
        assert a1["k_E"] == MR.k_eval(et)
        assert a1["r_flip_by_w"] == {w: MR.r_flip(M.EVAL, et, w) for w in M.grid_w()}
    ft = M.funded_terms("LU")
    a2 = LF.bounds("lucid", "A2").detail["LU"]
    assert a2["k_F"] == MR.k_funded(ft)["k_F"] and a2["b_star"] == MR.b_star(ft)["b_star"]
    assert a2["r_flip_by_w"] == {w: MR.r_flip(M.FUNDED, ft, w) for w in M.grid_w()}


# ------------------------------------------------------------------------------------------------ unverified keys refuse


def test_unverified_keys_on_the_real_record_refuse() -> None:
    assert LF.rule_status("mffu", "mffu.trading_hours") == ("absent", "absent")
    for lever, key in (("T2", "mffu.trading_hours"), ("A4", LF.MFFU_P + "eval_fee"),
                       ("A2", LF.MFFU_P + "payout_request_amount"), ("A8", "mffu.hold_queue_behaviour"),
                       ("A21", "mffu.payout_fee")):
        with pytest.raises(LF.NotVerified, match=re.escape(key)):
            LF.bounds("mffu", lever)
    for lever, key in (("T2", LF.LUCID_P + "trading_hours"), ("A19", LF.LUCID_P + "payout_request_amount_choice"),
                       ("A21", LF.LUCID_P + "payout_fee")):
        with pytest.raises(LF.NotVerified, match=re.escape(key)):
            LF.bounds("lucid", lever)
    with pytest.raises(LF.NotVerified):
        LF.ready("mffu")
    with pytest.raises(LF.NotVerified):
        LF.ready("lucid")
    LF.ready("topstep")


def test_the_record_wins_over_stage_twos_lucid_ledger(monkeypatch) -> None:
    assert LF.rule_status("lucid", LF.LUCID_P + "payout_fee") == ("record", "unstated")
    assert LF._lucid_ledger()["payout_fee"]["status"] != "verified"
    rec = copy.deepcopy(FT._record())
    key = LF.LUCID_P + "max_accounts"
    assert key not in rec
    LF.bounds("lucid", "A6")
    rec[key] = {"key": key, "firm": "lucid", "value": None, "status": "unverified"}
    monkeypatch.setattr(FT, "_record", lambda: rec)
    with pytest.raises(LF.NotVerified):
        LF.bounds("lucid", "A6")


def test_a_firm_reads_only_its_own_keys() -> None:
    with pytest.raises(ValueError):
        LF.rule("mffu", "combine_mll")
    with pytest.raises(ValueError):
        LF.rule("lucid", "mffu.max_eval_accounts")
    with pytest.raises(LF.NotVerified):
        LF.rule("lucid", "lucid.flex50k.no_such_rule")


# ------------------------------------------------------------------------------------------------ conduct tier 1 at sampling


@pytest.mark.parametrize("firm", LF.FIRMS)
def test_sampled_designs_hold_every_floor(firm: str) -> None:
    for seed in SEEDS:
        a = LF.sample(firm, seed=seed, n=25)
        assert a == LF.sample(firm, seed=seed, n=25)              # the seed fixes the draws
        sp = LF.load(firm)
        for d in a:
            LF.conduct_check(d)
            assert not any(d.get(m) for m in LF.TIER1_MARKERS)
            for lever, bad in LF.TIER1_VALUES.items():
                assert d.get(lever) not in bad
            for i, v in d.items():
                if not (i == "T4" and v is None):
                    assert LF._inside(sp[i], v), (firm, i, v)
            if firm == "lucid":
                assert d["A6"] + d["A7"] <= LF._lucid_accounts()["total"]
    assert LF.sample(firm, seed=SEEDS[0], n=25) != LF.sample(firm, seed=SEEDS[1], n=25)


@pytest.mark.parametrize("firm", LF.FIRMS)
def test_conduct_tier_one_is_refused_for_every_firm(firm: str) -> None:
    base = LF.sample(firm, seed=SEEDS[0], n=1)[0]
    LF.check_design(firm, base)
    for marker in LF.TIER1_MARKERS:
        with pytest.raises(LF.TierOneRefused):
            LF.check_design(firm, {**base, marker: True})
    with pytest.raises(LF.TierOneRefused):
        LF.check_design(firm, {**base, "accounts_per_trade": 2})
    for lever, bad in LF.TIER1_VALUES.items():
        for v in bad:
            with pytest.raises(LF.TierOneRefused):
                LF.check_design(firm, {**base, lever: v})
    with pytest.raises(LF.HardLimitRefused):
        LF.check_design(firm, {**base, "order_entry": "api"})


@pytest.mark.parametrize("firm", LF.FIRMS)
@pytest.mark.parametrize("lever,value", [("T8", "opposite"), ("A15", "copy"), ("T5", "multiple_limits_one_price")])
def test_a_tampered_space_is_refused_at_sampling(monkeypatch, firm: str, lever: str, value: str) -> None:
    real = LF.load(firm)

    def tampered(f: str) -> dict:
        sp = dict(real)
        sp[lever] = LS.Range(lever, "fixed", values=(value,))
        return sp

    monkeypatch.setattr(LF, "load", tampered)
    with pytest.raises(LF.TierOneRefused):
        LF.sample(firm, seed=SEEDS[0], n=1)


def test_lucid_refuses_accounts_beyond_the_household_total() -> None:
    base = LF.sample("lucid", seed=SEEDS[0], n=1)[0]
    total = LF._lucid_accounts()["total"]
    hi6, hi7 = LF.bounds("lucid", "A6").hi, LF.bounds("lucid", "A7").hi
    assert hi6 + hi7 > total                                   # the combination binds inside the ranges
    with pytest.raises(LS.LeverRefused):
        LF.check_design("lucid", {**base, "A6": hi6, "A7": hi7})


def test_a_setting_outside_its_range_or_on_a_refused_lever_is_refused() -> None:
    base = LF.sample("mffu", seed=SEEDS[0], n=1)[0]
    with pytest.raises(LS.LeverRefused):
        LF.check_design("mffu", {**base, "A6": LF.bounds("mffu", "A6").hi + 1})
    with pytest.raises(LS.LeverRefused):
        LF.check_design("mffu", {**base, "A4": "standard"})       # refused at this commit (its price unverified)


# ------------------------------------------------------------------------------------------------ hygiene


def _read_rule_numbers() -> set[float]:
    out: set[float] = set()
    for firm in OTHER:
        keys = {k for lv in LF.levers(firm).values() for k in lv.keys} | {k for k, _ in LF.PREREQUISITES[firm]}
        for k in keys:
            try:
                v = LF.rule(firm, k)
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
            if any(isinstance(t, ast.Name) and t.id == "FIRM_DECLARED" for t in targets):
                skip |= {id(n) for n in ast.walk(node)}
    values = _read_rule_numbers()
    assert values
    bad = [(n.lineno, n.value) for n in ast.walk(tree)
           if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool)
           and id(n) not in skip and float(n.value) in values]
    assert not bad, bad


def test_the_loader_reads_rules_only(monkeypatch) -> None:
    opened: list[str] = []
    real_open, real_io_open = builtins.open, io.open

    def spy(file, *a, **k):
        opened.append(str(file))
        return real_open(file, *a, **k)

    def spy_io(file, *a, **k):
        opened.append(str(file))
        return real_io_open(file, *a, **k)

    LF._lucid_ledger.cache_clear()
    FT._record.cache_clear()
    monkeypatch.setattr(builtins, "open", spy)
    monkeypatch.setattr(io, "open", spy_io)
    for firm in OTHER:
        LF.load(firm)
        LF.refusals(firm)
        LF.sample(firm, seed=SEEDS[0], n=3)
    norm = [p.replace("\\", "/") for p in opened]
    forbidden = ("/data/bars", "/data/atlas", "/results/", ".parquet", ".csv")
    assert not [p for p in norm if any(f in p for f in forbidden)], norm


def test_the_declared_table_cites_every_entry() -> None:
    for name, d in LF.FIRM_DECLARED.items():
        assert d.cite and len(d.cite) > 10, name
