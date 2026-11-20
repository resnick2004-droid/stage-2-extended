"""The restart plan's Wave 3.5, corrective cycle 1: the playbook, the alert and the not-offered notice
(`extended/playbook.py`), on synthetic declarations, logs, result files, calendars and offers only
(`tests/playbook_cases.py`) -- never a bar, never a result of this repository.

What is held (the red team's BUILD_W35 findings and the lead's rulings):
* **R-1, the side**: an alert's side is `trigger_sides.trigger_side`'s, from the offer's tag or ticket and the declared
  rule; a scheduled trade -- coin-stamped, or relabelled "trigger" -- gets the not-offered notice, never an alert; a
  failed or absent no-harm verdict, a side rule outside the vocabulary, P-16 and the coin refuse;
* **R-2 to R-4, the alert checks the offer itself**: its decision, alert, live = alert + L, entry, expiry, tag, group,
  window, account pool, size cap; the day's flags from the void calendar's sources (void, FOMC, prior_void for a
  prior-levels reader, H2's overnight void for an overnight reader), the news windows from the declaration's dated
  record, the flatten at a window's start;
* **R-5, no price**: no alert holds the offer's level or any price; a git-ignored or price-holding result refuses;
* **R-6, result files**: each manifest condition (clean run, named commit, not dirty, not exploratory, this design, the
  convention, the pinned hash, verify_result on the one resolved path), in process and through the real
  `extended.results.verify_result` in a subprocess;
* **R-7, the declaration**: loaded from the file pinned by sha256 in its carrying row; every cited row looked up;
* **R-8, the layout**: the playbook and five alerts equal goldens (`tests/data/playbook_golden.json`) written by hand
  from the fixture and reviewed line by line; every value piece is recomputed independently from its paths; one
  refusal test per guard;
* **R-9, R-10, R-12, R-13**: firm and plan from the verified ledger only; no digit in labels, sources, reasons; a
  latency-free source's L is its single cell; the firm's state is stated as a condition the user checks;
* determinism (byte-identical text across hash seeds) and no automation hook.
No randomness is drawn.
"""
from __future__ import annotations

import ast
import dataclasses
import hashlib
import json
import math
import os
import re
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from extended import playbook as PB
from extended import router as R
from extended import triggers as T
from tests import playbook_cases as PC

ROOT = Path(__file__).resolve().parent.parent
MODULE = ROOT / "extended" / "playbook.py"
GOLDEN = ROOT / "tests" / "data" / "playbook_golden.json"
DIGIT = re.compile(r"\d")
CALLS: list[Path] = []


@pytest.fixture(autouse=True)
def _standin(monkeypatch):
    """The vendored verify_result stays out of the test runner's process (it puts the vendored tree on sys.path); the
    stand-in is its check, and records the path it is given."""
    CALLS.clear()

    def rec(path):
        CALLS.append(Path(path))
        return PC.verify_standin(path)

    monkeypatch.setattr(PB, "_verify_result", rec)


@pytest.fixture
def root(tmp_path):
    return PC.build_root(tmp_path)


@pytest.fixture
def carried(root):
    return PB.load_carried(PC.DECL_FILE, root=root)


def _load(tmp_path, decl=None, **kw):
    return PB.load_carried(PC.DECL_FILE, root=PC.build_root(tmp_path, decl, **kw))


def _refuses(tmp_path, mutate=None, **kw):
    decl = PC.declaration()
    if mutate is not None:
        mutate(decl)
    with pytest.raises(PB.PlaybookRefused):
        _load(tmp_path, decl, **kw)


# ------------------------------------------------------------------------------------------------ independent checks


def _res(src, path):
    cur = src
    for k in path:
        cur = cur[k]
    return cur


def _label(s):
    m = (int(s) + 17 * 60) % 1440
    return "%02d:%02d" % (m // 60, m % 60)


_ANCHOR = {"london": ("Europe/London", 8, 0), "ny_am": ("America/New_York", 9, 30),
           "ny_pm": ("America/New_York", 9, 30), "asia": ("Asia/Tokyo", 9, 0)}


def _anchor_ct(day, session):
    d = date.fromisoformat(day)
    ct = ZoneInfo("America/Chicago")
    lo = datetime(d.year, d.month, d.day, 17, 0, tzinfo=ct) - timedelta(days=1)
    tz, h, m = _ANCHOR[session]
    for cand in (d - timedelta(days=1), d):
        t = datetime(cand.year, cand.month, cand.day, h, m, tzinfo=ZoneInfo(tz)).astimezone(ct)
        if lo <= t < lo + timedelta(days=1):
            return "%02d:%02d" % (t.hour, t.minute)
    raise AssertionError("no anchor")


EXPECT = {
    "text": lambda v: repr(v) if isinstance(v, float) else str(v),
    "ct": _label,
    "target": lambda stop, rr: str(math.floor(rr * stop + 1e-9)),
    "anchor_ct": _anchor_ct,
    "side": lambda s: {1: "BUY (long)", -1: "SELL (short)"}[s],
    "order": lambda k: k.upper(),
    "yesno": lambda b: "yes" if b else "no",
}


def check_traced(rendered, src):
    """No literal piece holds a digit; every value piece whose path root is in `src` equals its independent
    recomputation from `src` (the alert's computed `calc` pieces are held by the goldens instead)."""
    n = 0
    for p in rendered.pieces:
        if p.transform is None:
            assert not DIGIT.search(p.text), f"a template literal holds a digit: {p.text!r}"
        elif all(path[0] in src for path in p.paths):
            want = EXPECT[p.transform](*[_res(src, path) for path in p.paths])
            assert p.text == want, (p, want)
            n += 1
    assert "".join(p.text for p in rendered.pieces) == rendered.text
    return n


def _library():
    # the firm's verified ledger (vendor/stage2/config/rules.yaml): 5 minis in the Combine, the XFA's entry tier 2 minis,
    # 10 micros a mini; the plan's name as `combine_mll`'s note writes it
    return {"plan": "50K Trading Combine", "cap": {"ts_a1": 50, "ts_b2": 20, "ts_c3": 50}, "max_latency": 5,
            "tickets_alert": 930, "tickets_live": 960, "hash": "sha256"}


def _pb_src(c):
    return {"design": PC.declaration(), "library": _library(), "file": {"decl": PC.DECL_FILE, "sha": c.decl_sha},
            "expected": {"file": PC.EXPECTED_FILE, "commit": PC.COMMIT,
                         **{"|".join((r["section"], r["block"], r["measure"], r["stat"])): r["value"]
                            for r in PC.EXPECTED_ROWS}},
            "no_harm": {"file": PC.NO_HARM_FILE, "commit": PC.COMMIT}}


def _alerts(c):
    """The five alerts and two notices the goldens hold."""
    src = PC.sources()
    return {
        "pm_limit_plain_day": PB.render_alert(c, PC.p14_offer(), "pm_brk", "ts_b2", "2021-03-16", src),
        "pm_limit_window_flatten": PB.render_alert(c, PC.p14_offer(), "pm_brk", "ts_b2", "2021-03-17", src),
        "ldn_market_overnight": PB.render_alert(c, PC.ldn_offer(), "ldn_brk", "ts_a1", "2021-03-16", src),
        "rl3_fade_resistance": PB.render_alert(c, PC.rl3_offer(), "am_rl3", "ts_c3", "2021-03-16", src),
        "rl3_break_support": PB.render_alert(c, PC.rl3_offer("lo", -1), "am_rl3", "ts_a1", "2021-03-16", src),
        "notice_coin_trade": PB.render_trade(c, R.RoutedTrade(PC.scheduled(), "ts_b2")),
        "notice_prior_void": PB.render_offer(c, PC.rl3_offer(), "am_rl3", "ts_a1", "2021-03-15", src),
    }


def goldens(c) -> dict[str, str]:
    out = {"playbook": PB.render_playbook(c).text}
    out.update({k: v.text for k, v in _alerts(c).items()})
    return out


# ------------------------------------------------------------------------------------------------ the playbook


def test_goldens_hold_the_layout(carried):
    """R-8: the whole text, every line, against the reviewed goldens (a value from a wrong path, a swapped pair, a
    dropped line or a rounding change shows here)."""
    want = json.loads(GOLDEN.read_bytes())
    got = goldens(carried)
    assert sorted(got) == sorted(want)
    for k in want:
        assert got[k].splitlines() == want[k].splitlines(), k


def test_playbook_every_number_traces_to_an_input(carried):
    r = PB.render_playbook(carried)
    assert check_traced(r, _pb_src(carried)) > 60
    text = r.text
    for row in PC.EXPECTED_ROWS[:4]:
        assert row["value"] in text
    assert "999" not in text                                  # a row the declaration does not name is not shown
    assert "Target: 100 ticks (reward to risk 1.3)" in text  # floor(1.3 x 77) = 100, not 101
    assert "Target: 135 ticks (reward to risk 2.25)" in text and "Target: 150 ticks (reward to risk 1.5)" in text


def test_playbook_deterministic_across_hash_seeds(carried, root):
    a = PB.render_playbook(carried).text
    assert a == PB.render_playbook(PB.load_carried(PC.DECL_FILE, root=root)).text
    want = hashlib.sha256(a.encode()).hexdigest()
    for seed in ("0", "1", "4242"):
        env = dict(os.environ, PYTHONHASHSEED=seed, OMP_NUM_THREADS="1")
        out = subprocess.run([sys.executable, str(ROOT / "tests" / "playbook_cases.py"), "render", str(root)], env=env,
                             capture_output=True, text=True, timeout=300, cwd=str(ROOT))
        assert out.returncode == 0, out.stderr
        assert out.stdout.strip() == want


def test_module_has_no_typed_number_and_no_automation_hook():
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    docs = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef)) and node.body and isinstance(
                node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
            docs.add(id(node.body[0].value))
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and id(node) not in docs:
            if isinstance(node.value, str):
                assert not DIGIT.search(node.value), f"a string constant holds a digit: {node.value!r}"
            elif isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
                assert node.value in (0, 1, -1), f"a typed number: {node.value!r}"
    allowed = {"__future__", "csv", "fnmatch", "hashlib", "io", "json", "math", "re", "dataclasses", "datetime",
               "pathlib", "typing", "extended"}
    for node in ast.walk(tree):
        names = ([a.name for a in node.names] if isinstance(node, ast.Import) else
                 [node.module or ""] if isinstance(node, ast.ImportFrom) else [])
        for n in names:
            assert n.split(".")[0] in allowed, f"import {n}: the playbook has no network, process or broker hook"
    assert "open(" not in MODULE.read_text(encoding="utf-8").replace("re.compile(", "")      # no file is written


def test_playbook_states_the_rules(carried):
    text = PB.render_playbook(carried).text
    assert "HAND ENTRY ONLY" in text and "no automated or API order entry" in text
    assert "NEVER HOLD OPPOSITE POSITIONS AT ONCE across your accounts or firms" in text
    assert "Never copy a trade to several accounts" in text and "Never put size into major news" in text
    assert "the years this design was chosen on" in text and "held-out years, reported beside" in text     # N-3


@pytest.mark.parametrize("key", PB.REQUIRED)
def test_missing_declaration_key_refuses(tmp_path, key):
    _refuses(tmp_path, lambda d: d.pop(key))


@pytest.mark.parametrize("key", PB.COMPONENT_KEYS)
def test_missing_component_key_refuses(tmp_path, key):
    _refuses(tmp_path, lambda d: d["components"][1].pop(key))


@pytest.mark.parametrize("key", PB.EXECUTION_KEYS)
def test_missing_or_changed_execution_rule_refuses(tmp_path, key):
    _refuses(tmp_path / "a", lambda d: d["execution"].pop(key))

    def bump(d):
        v = d["execution"][key]
        d["execution"][key] = [v[0] + 1, v[1]] if isinstance(v, list) else v + 1
    _refuses(tmp_path / "b", bump)


def _set(path, value):
    def f(d):
        cur = d
        for k in path[:-1]:
            cur = cur[k]
        cur[path[-1]] = value
    return f


MUTATIONS = {
    "L-undeclared": _set(("components", 2, "latency"), 4),
    "L-not-triggers": _set(("components", 2, "latency"), 5),
    "L-of-latency-free": _set(("components", 1, "latency"), 2),                                   # R-12
    "coin-trigger": _set(("components", 0, "trigger", "source"), "coin"),
    "p16-no-side-rule": _set(("components", 0, "trigger"), {"source": "p16", "params": {"marks": [600, 630],
                                                                                         "overnight": True}}),
    "side-rule-free-words": _set(("components", 2, "side_rule"), "toss a fair coin"),
    "side-rule-blank": _set(("components", 2, "side_rule"), ""),
    "rl3-rule-missing-level": _set(("components", 1, "side_rule"), {"hi": "fade"}),
    "trigger-before-window": _set(("components", 2, "trigger", "params", "first"), 1000),         # R-12
    "trigger-after-window": _set(("components", 2, "trigger", "params", "last"), 1258),
    "rl3-window-misses-live": _set(("components", 1, "first"), 965),
    "anchor": _set(("session_anchors", "london"), ["Europe/London", "09:00"]),
    "collision": _set(("components", 2, "first"), 1000),
    "rotation": _set(("rotation", "rule"), "copy_to_all"),
    "pool-account": _set(("rotation", "pools", "pm_brk"), ["ts_zz"]),
    "pool-component": _set(("rotation", "pools", "no_such"), ["ts_a1"]),                          # G9
    "void-rule-unknown": lambda d: d["void_rules"].append("my_hunch"),
    "void-rule-dropped": lambda d: d["void_rules"].remove("prior_abbreviated"),
    "void-rule-twice": lambda d: d["void_rules"].append("fomc"),
    "void-date-reason": _set(("void_dates", 0, "reason"), "my_hunch"),                            # G5
    "contracts-zero": _set(("components", 1, "contracts"), 0),
    "contracts-500": _set(("components", 2, "contracts"), 500),                                    # R-4
    "contracts-over-funded-cap": _set(("components", 2, "contracts"), 21),                         # 20 for ts_b2
    "contracts-over-eval-cap": _set(("components", 1, "contracts"), 51),
    "budget-zero": _set(("bankroll", "budget"), 0),
    "accounts-repeat": lambda d: d["accounts"].append({"id": "ts_a1", "role": "evaluation"}),       # G1
    "no-account": lambda d: d.update(accounts=[], rotation={"rule": "longest_waiting"}),           # G8
    "role-unknown": _set(("accounts", 0, "role"), "prop"),
    "label-with-figure": _set(("expected", "rows", 0, "label"), "pass rate 87% (sessions to the first payout)"),
    "label-blank": _set(("expected", "rows", 0, "label"), " "),
    "news-source-figure": _set(("news_windows", 0, "source"), "CPI at 7:30"),
    "news-window-off-clock": _set(("news_windows", 0, "release"), 5000),
    "expected-no-rows": _set(("expected", "rows"), []),                                            # G4
    "expected-row-twice": lambda d: d["expected"]["rows"].append(dict(d["expected"]["rows"][0])),
    "expected-block": _set(("expected", "rows", 0, "block"), "all_years"),
    "firm-lucid": _set(("firm",), "lucid"),                                                        # R-9
    "firm-unknown": _set(("firm",), "not_a_firm"),
    "plan-unknown": _set(("plan",), "the 50K plan"),
    "instrument": _set(("instrument",), "ES"),
    "design-id": _set(("design_id",), "two words"),
}


@pytest.mark.parametrize("name", sorted(MUTATIONS))
def test_disagreement_with_the_library_or_the_ledger_refuses(tmp_path, name):
    _refuses(tmp_path, MUTATIONS[name])


def test_coin_refused_as_the_evaluations_device(tmp_path):
    decl = PC.declaration()
    decl["components"][0]["trigger"]["source"] = "coin"
    with pytest.raises(PB.PlaybookRefused, match="evaluation's device"):
        _load(tmp_path, decl)


# ------------------------------------------------------------------------------------------------ R-7: pins and rows


def test_declaration_edited_after_its_pin_refuses(root):
    p = root / PC.DECL_FILE
    p.write_bytes(p.read_bytes().replace(b'"contracts": 1', b'"contracts": 2'))
    with pytest.raises(PB.PlaybookRefused, match="not the file pinned"):
        PB.load_carried(PC.DECL_FILE, root=root)


def test_declaration_pinned_with_crlf_reads_as_lf(root):
    p = root / PC.DECL_FILE
    p.write_bytes(p.read_bytes().replace(b"\n", b"\r\n"))
    assert PB.load_carried(PC.DECL_FILE, root=root).decl_sha


@pytest.mark.parametrize("path,value", [(("row",), "E-99999999"), (("row",), "E-0"),
                                        (("side", "no_harm_row"), "E-0"), (("side", "no_harm_row"), "pending"),
                                        (("bankroll", "row"), "E-9999"), (("bankroll", "row"), "E-77")],
                         ids=["carrying-missing", "carrying-short", "no-harm-short", "no-harm-pending",
                              "bankroll-missing", "bankroll-short"])
def test_a_cited_row_not_in_the_log_refuses(tmp_path, path, value):
    _refuses(tmp_path, _set(path, value))


@pytest.mark.parametrize("edit", [
    lambda rows: {**rows, "E-9001": rows["E-9001"].replace(f"**{PC.DESIGN} carried", "**X-other carried")},
    lambda rows: {**rows, "E-9002": rows["E-9002"].replace(PC.DESIGN, "X-demo70")},
    lambda rows: {**rows, "E-9001": rows["E-9001"].split("; its expected")[0]},
    lambda rows: {**rows, "E-9002": "**no pin here**"},
], ids=["carrying-names-another-design", "no-harm-names-another-design", "expected-unpinned", "no-harm-unpinned"])
def test_rows_must_name_the_design_and_pin_its_files(tmp_path, edit):
    with pytest.raises(PB.PlaybookRefused):
        _load(tmp_path, rows_text=edit)


def test_a_repeated_row_in_the_log_refuses(root):
    log = root / "DECISIONS.md"
    log.write_bytes(log.read_bytes() + b"| E-9003 | 2021-01-02 | again | synthetic |\n")
    with pytest.raises(PB.PlaybookRefused, match="twice"):
        PB.load_carried(PC.DECL_FILE, root=root)


def test_a_carried_design_is_made_only_by_the_loader(carried):
    with pytest.raises(PB.PlaybookRefused):
        PB.Carried(carried.decl_file, carried.decl_sha, carried.decl_bytes, carried.rows, carried.design,
                   carried.expected, carried.no_harm)
    for kw in (dict(decl_bytes=carried.decl_bytes + b" "), dict(expected=carried.no_harm)):
        with pytest.raises(PB.PlaybookRefused):
            dataclasses.replace(carried, **kw)
    with pytest.raises(PB.PlaybookRefused):
        PB.render_playbook(PC.declaration())


# ------------------------------------------------------------------------------------------------ R-6 / R-5: result files


def test_result_read_from_one_resolved_path(carried, root):
    assert sorted(CALLS) == sorted({(root / PC.EXPECTED_FILE).resolve(), (root / PC.NO_HARM_FILE).resolve()})
    assert all(p.is_absolute() for p in CALLS)


MANIFEST_FAULTS = {
    "no-clean-run": dict(provenance=None),
    "clean-run-unnamed": dict(provenance={"clean_run": {"name": ""}}),
    "commit-unknown": dict(git_commit="unknown", git_dirty=None),
    "commit-dirty": dict(git_commit=PC.COMMIT + "-dirty", git_dirty=True),
    "dirty-flag": dict(git_dirty=True),
    "dirty-unrecorded": dict(git_dirty=None),
    "commit-blank": dict(git_commit=""),
    "exploratory": dict(exploratory=True),
    "other-design": dict(parameters={"design_id": "SOME-OTHER-DESIGN", "convention": "zero_edge"}),
    "as-traded": dict(parameters={"design_id": PC.DESIGN, "as_traded": True}),
    "other-convention": dict(parameters={"design_id": PC.DESIGN, "convention": "no_harm_real_path"}),
    "hash-not-the-files": dict(sha256="0" * 64),
}


@pytest.mark.parametrize("fault", sorted(MANIFEST_FAULTS))
def test_expected_file_manifest_fault_refuses(tmp_path, fault):
    with pytest.raises(PB.PlaybookRefused):
        _load(tmp_path, expected_over=MANIFEST_FAULTS[fault])


@pytest.mark.parametrize("fault", ["no-clean-run", "commit-dirty", "exploratory", "other-design"])
def test_no_harm_file_manifest_fault_refuses(tmp_path, fault):
    over = dict(MANIFEST_FAULTS[fault])
    if "parameters" in over:
        over["parameters"] = {**over["parameters"], "convention": "no_harm_real_path"}
    with pytest.raises(PB.PlaybookRefused):
        _load(tmp_path, no_harm_over=over)


def test_tampered_or_missing_result_refuses(root):
    p = root / PC.EXPECTED_FILE
    p.write_bytes(p.read_bytes().replace(b"37.5", b"12.5"))
    with pytest.raises(PB.PlaybookRefused):
        PB.load_carried(PC.DECL_FILE, root=root)
    p.unlink()
    with pytest.raises(PB.PlaybookRefused):
        PB.load_carried(PC.DECL_FILE, root=root)


def test_pin_in_the_row_must_be_the_manifests(tmp_path):
    with pytest.raises(PB.PlaybookRefused):
        _load(tmp_path, rows_text=lambda rows: {**rows, "E-9001": re.sub(r"(journey_x\.csv` sha256 `)[0-9a-f]+",
                                                                           lambda m: m.group(1) + "a" * 64,
                                                                           rows["E-9001"])})


@pytest.mark.parametrize("rel", ["results/s1_range.csv", "results/q121_vol_descriptive_a1.csv",
                                 "results/scratch/x.csv", "elsewhere/journey_x.csv", "results/../journey_x.csv",
                                 "results/journey_x.txt"])
def test_licensed_ignored_or_misplaced_result_refuses(tmp_path, rel):
    decl = PC.declaration()
    decl["expected"]["file"] = rel
    with pytest.raises(PB.PlaybookRefused):
        _load(tmp_path, decl)


def test_result_holding_price_levels_refuses(tmp_path):
    rows = [dict(r) for r in PC.EXPECTED_ROWS]
    for r, v in zip(rows, ("18234.75", "18100.25", "17950.5", "18000.0", "18012.25")):
        r["value"] = v
    with pytest.raises(PB.PlaybookRefused, match="licence guard"):
        _load(tmp_path, expected_rows=rows)


def test_result_row_absent_twice_or_blank_refuses(tmp_path):
    with pytest.raises(PB.PlaybookRefused):
        _load(tmp_path / "a", expected_rows=PC.EXPECTED_ROWS[1:])
    with pytest.raises(PB.PlaybookRefused):
        _load(tmp_path / "b", expected_rows=PC.EXPECTED_ROWS + PC.EXPECTED_ROWS[:1])
    blank = [dict(r) for r in PC.EXPECTED_ROWS]
    blank[0]["value"] = " "
    with pytest.raises(PB.PlaybookRefused, match="blank"):                                         # G6
        _load(tmp_path / "c", expected_rows=blank)


@pytest.mark.parametrize("verdict", ["fail", "", None])
def test_no_harm_floor_failed_or_absent_refuses(tmp_path, verdict):
    rows = [dict(r) for r in PC.NO_HARM_ROWS]
    if verdict is None:
        rows = [r for r in rows if r["measure"] != "am_rl3"]
    else:
        rows[1]["value"] = verdict
    with pytest.raises(PB.PlaybookRefused, match="no-harm floor"):
        _load(tmp_path, no_harm_rows=rows)


def test_result_files_through_the_real_verify_result(tmp_path):
    """The vendored writer and verify_result, in their own process: a clean run's file is accepted; a tampered one, one
    written outside a clean run (commit dirty or unknown), and the red team's probe 2 (exploratory, another design,
    as-traded) refuse."""
    env = dict(os.environ, OMP_NUM_THREADS="1")
    out = subprocess.run([sys.executable, str(ROOT / "tests" / "playbook_cases.py"), "results", str(tmp_path)],
                         env=env, capture_output=True, text=True, timeout=600, cwd=str(ROOT))
    assert out.returncode == 0, out.stderr
    got = json.loads(out.stdout.strip().splitlines()[-1])
    assert got["clean"] == "accepted:" + PC.COMMIT
    for k in ("tampered", "as_written", "other_design"):
        assert got[k].startswith("refused:"), (k, got[k])


# ------------------------------------------------------------------------------------------------ the alert


def _offer_src(c, offer, account, day):
    return {"design": c.decl, "offer": {f.name: getattr(offer, f.name) for f in dataclasses.fields(offer)
                                        if f.name != "level"},
            "account": account, "day": day, "library": _library()}


def test_alerts_trace_and_never_print_a_price(carried):
    cases = [(PC.p14_offer(), "ts_b2", "2021-03-16"), (PC.ldn_offer(), "ts_a1", "2021-03-16"),
             (PC.rl3_offer(), "ts_c3", "2021-03-16"), (PC.rl3_offer("lo", -1), "ts_a1", "2021-03-16")]
    comps = ["pm_brk", "ldn_brk", "am_rl3", "am_rl3"]
    for (off, acct, day), comp in zip(cases, comps):
        r = PB.render_alert(carried, off, comp, acct, day, PC.sources())
        assert check_traced(r, _offer_src(carried, off, acct, day)) > 10
        t = r.text
        assert repr(off.level) not in t and str(off.level) not in t                                 # R-5
        assert not re.search(r"\d{3,}\.\d", t), "a price-like number in an alert"
        assert all("level" not in p for piece in r.pieces for path in piece.paths for p in path if isinstance(p, str))
        for hook in ("http", "webhook", "json", "{", "api"):
            assert hook not in t.lower()
        assert "exit" not in t.lower() and "fill_" not in t                                       # no outcome
        assert "enter only if, at this firm, no position is open" in t                             # R-13


def test_side_is_the_triggers_own(carried):
    src = PC.sources()
    t = PB.render_alert(carried, PC.p14_offer(tag="brk30-"), "pm_brk", "ts_b2", "2021-03-16", src).text
    assert "Side BUY (long)" in t                              # against a downward breakout
    t = PB.render_alert(carried, PC.ldn_offer(tag="brk30+"), "ldn_brk", "ts_a1", "2021-03-16", src).text
    assert "Side BUY (long)" in t                              # with an upward breakout
    t = PB.render_alert(carried, PC.rl3_offer("hi", -1), "am_rl3", "ts_a1", "2021-03-16", src).text
    assert "Side BUY (long)" in t and "Order LIMIT at the level itself" in t       # fade at a support: buy limit


@pytest.mark.parametrize("label", ["coin", "trigger", "relabelled"])
def test_a_scheduled_trade_gets_the_not_offered_notice(carried, label):
    """R-1: whatever its label, a scheduled trade's side is the coin's -- never an alert."""
    tr = PC.scheduled(side_source="coin")
    if label != "coin":
        tr = dataclasses.replace(tr, side_source="trigger")
    for x in (tr, R.RoutedTrade(tr, "ts_b2")):
        r = PB.render_trade(carried, x)
        assert r.text.startswith("NOT OFFERED today") and "evaluation's coin" in r.text
        with pytest.raises(PB.AlertRefused):
            PB.render_alert(carried, x, "pm_brk", "ts_b2", "2021-03-16", PC.sources())


P14_FAULTS = {
    "alert-after-trigger-last": dict(decision=1258, alert=1258, live=1261, expires=1261 + T.LIMIT_WINDOW - 1),
    "alert-before-trigger-first": dict(decision=1076, alert=1076, live=1079, expires=1079 + T.LIMIT_WINDOW - 1),
    "live-not-alert-plus-L": dict(live=1160, expires=1160 + T.LIMIT_WINDOW - 1),
    "decision-not-alert": dict(decision=1000),
    "overnight-for-ny-pm": dict(decision=100, alert=100, live=103, expires=103 + T.LIMIT_WINDOW - 1),
    "market-on-a-limit-component": dict(entry=T.MARKET, expires=None),
    "market-with-the-limit-expiry": dict(entry=T.MARKET),
    "ticket-on-a-limit-component": dict(entry=T.TICKET, role=1),
    "ticket-without-role": dict(entry=T.TICKET),
    "expiry-not-the-limit-window": dict(expires=1200),
    "tag-other-k": dict(tag="brk15+"),
    "tag-coin": dict(tag="coin"),
    "sub-not-zero": dict(sub=1),
    "group": dict(group="rl3:pd"),
    "rewrite": dict(rewrite=True),
    "source-coin": dict(source="coin"),
}


@pytest.mark.parametrize("fault", sorted(P14_FAULTS))
def test_p14_offer_that_is_not_the_triggers_refuses(carried, fault):
    with pytest.raises(PB.AlertRefused) as e:
        PB.render_offer(carried, PC.p14_offer(**P14_FAULTS[fault]), "pm_brk", "ts_b2", "2021-03-16", PC.sources())
    assert e.value.reason == "mismatch"


RL3_FAULTS = {
    "live-not-nine": dict(live=961),
    "alert-not-the-open": dict(alert=929, decision=929),
    "other-kind": dict(tag="on_hi", sub=T.RL3_SUBS[("on", "hi")]),
    "sub-not-the-levels": dict(sub=1),
    "expiry-not-the-cutoff": dict(expires=1049),
    "group-other": dict(group="rl3:on"),
    "not-rewritten": dict(rewrite=False),
    "market": dict(entry=T.MARKET),
}


@pytest.mark.parametrize("fault", sorted(RL3_FAULTS))
def test_rl3_offer_that_is_not_the_triggers_refuses(carried, fault):
    with pytest.raises(PB.AlertRefused) as e:
        PB.render_offer(carried, PC.rl3_offer(**RL3_FAULTS[fault]), "am_rl3", "ts_a1", "2021-03-16", PC.sources())
    assert e.value.reason == "mismatch"


def test_rl3_ticket_without_role_refuses(carried):
    with pytest.raises(PB.AlertRefused) as e:
        PB.render_offer(carried, PC.rl3_offer(role=0), "am_rl3", "ts_a1", "2021-03-16", PC.sources())
    assert e.value.reason == "mismatch"


@pytest.mark.parametrize("args", [("pm_brk", "ts_a1"), ("pm_brk", "ts_zz"), ("am_rl3", "ts_b2"), ("nope", "ts_b2"),
                                  ("ldn_brk", "ts_b2")],
                         ids=["outside-pool", "unknown-account", "outside-rl3-pool", "unknown-component",
                              "wrong-component"])
def test_account_or_component_mismatch_refuses(carried, args):
    comp, acct = args
    with pytest.raises(PB.AlertRefused) as e:
        PB.render_offer(carried, PC.p14_offer(), comp, acct, "2021-03-16", PC.sources())
    assert e.value.reason == "mismatch"


def test_the_caller_cannot_supply_the_day(carried):
    with pytest.raises(PB.AlertRefused):
        PB.render_alert(carried, PC.p14_offer(), "pm_brk", "ts_b2", "2021-03-16", T.DayContext(41, "2021-03-16"))


@pytest.mark.parametrize("day", ["2024-05-01", "2026-08-03", "2021-03-20", "16 March"],
                         ids=["held-out", "confirmation-window", "not-stored", "not-iso"])
def test_a_day_the_calendar_does_not_give_refuses(carried, day):
    with pytest.raises(PB.AlertRefused) as e:
        PB.render_offer(carried, PC.p14_offer(), "pm_brk", "ts_b2", day, PC.sources())
    assert e.value.reason == "mismatch"


@pytest.mark.parametrize("case,comp,offer,day,src,reason", [
    ("fomc", "pm_brk", PC.p14_offer, "2021-03-16", dict(fomc=("2021-03-16",)), "fomc"),
    ("early-end", "pm_brk", PC.p14_offer, "2021-03-16", dict(early_end=("2021-03-16",)), "calendar"),
    ("short-last-bar", "pm_brk", PC.p14_offer, "2021-03-16", dict(last_bar={"2021-03-16": "14:00"}), "calendar"),
    ("declared-void-date", "pm_brk", PC.p14_offer, "2021-03-19", {}, "declared_void"),
    ("prior-void-first-day", "am_rl3", PC.rl3_offer, "2021-03-15", {}, "prior_void"),
    ("prior-void-roll", "am_rl3", PC.rl3_offer, "2021-03-16", dict(rolls=("2021-03-16",)), "prior_void"),
    ("prior-void-after-closure", "am_rl3", PC.rl3_offer, "2021-04-05", {}, "prior_void"),
    ("h2-void-overnight-reader", "ldn_brk", PC.ldn_offer, "2021-03-16",
     dict(flags={"2021-03-16": {"verdict": "VOID", "void": "synthetic"}}), "calendar"),
    ("no-0829-bar-rl3", "am_rl3", PC.rl3_offer, "2021-03-16",
     dict(flags={"2021-03-16": {"special": "no_0829_bar"}}), "calendar"),
    ("bls-overnight-entry", "ldn_brk", PC.ldn_offer, "2021-03-16", dict(bls=("2021-03-16",)), "bls"),
])
def test_the_calendar_voids_the_offer(carried, case, comp, offer, day, src, reason):
    acct = {"pm_brk": "ts_b2", "am_rl3": "ts_a1", "ldn_brk": "ts_a1"}[comp]
    with pytest.raises(PB.AlertRefused) as e:
        PB.render_alert(carried, offer(), comp, acct, day, PC.sources(**src))
    assert e.value.reason == reason
    note = PB.render_offer(carried, offer(), comp, acct, day, PC.sources(**src))
    assert note.text.startswith("NOT OFFERED today") and PB.REASON_WORDS[reason] in note.text


def test_prior_void_and_h2_void_reach_only_the_components_that_read_them(carried):
    src = PC.sources(rolls=("2021-03-16",), flags={"2021-03-16": {"verdict": "VOID", "void": "synthetic"}})
    t = PB.render_alert(carried, PC.p14_offer(), "pm_brk", "ts_b2", "2021-03-16", src).text   # reads neither
    assert t.startswith("TRADE ALERT")


def test_news_window_from_the_declared_record(carried):
    """R-4: the window comes from the declaration's dated record (2021-03-17's afternoon release, 11:57 to 12:06 CT),
    not from the caller; an order live inside it is not offered; one live before it is closed at its start."""
    off = PC.p14_offer(decision=1138, alert=1138, live=1141, expires=1141 + T.LIMIT_WINDOW - 1)
    with pytest.raises(PB.AlertRefused) as e:
        PB.render_alert(carried, off, "pm_brk", "ts_b2", "2021-03-17", PC.sources())
    assert e.value.reason == "news"
    assert PB.render_alert(carried, off, "pm_brk", "ts_b2", "2021-03-16", PC.sources()).text   # no release that day
    t = PB.render_alert(carried, PC.p14_offer(), "pm_brk", "ts_b2", "2021-03-17", PC.sources()).text
    assert "closed at 11:57 CT, when a news window starts (a synthetic afternoon release)" in t
    assert "the bars from 11:57 CT through 12:06 CT" in t and "15:08" not in t


def test_rl3_ticket_rewritten_after_a_window(carried, tmp_path):
    decl = PC.declaration()
    decl["news_windows"].append({"source": "a synthetic morning release", "release": 990, "before": 1, "after": 4,
                                 "dates": ["2021-03-18"]})
    c = _load(tmp_path, decl)
    t = PB.render_alert(c, PC.rl3_offer(), "am_rl3", "ts_a1", "2021-03-18", PC.sources()).text
    assert "Working from 09:00 CT through the bar stamped 09:28 CT" in t
    assert "a position from it is closed at 09:29 CT, when a news window starts" in t
    assert "Working from 09:35 CT through the bar stamped 09:59 CT" in t


def test_not_offered_reasons_are_a_closed_vocabulary(carried):
    off = PC.p14_offer()
    with pytest.raises(PB.AlertRefused):
        PB.render_not_offered(carried, off, "pm_brk", "price 18234.75")                   # R-10
    with pytest.raises(PB.AlertRefused):
        PB.render_not_offered(carried, off, "am_rl3", "position")                        # not its trigger's offer
    r = PB.render_not_offered(carried, off, "pm_brk", "position")
    assert check_traced(r, {"design": carried.decl, "offer": {"live": 1104}}) == 2
    assert "a position is already open" in r.text


def test_brief_command_forbids_licensed_quotes_and_automation():
    """N-2: `/brief` never quotes a licensed-price derivative and never suggests automating orders."""
    text = (ROOT / ".claude" / "commands" / "brief.md").read_text(encoding="utf-8")
    assert "Never quote anything from a licensed-price derivative" in text and "git-ignored" in text
    assert "never suggest automating orders" in text and "never a command that writes a file" in text
