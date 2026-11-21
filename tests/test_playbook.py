"""The restart plan's Wave 3.5, corrective cycle 2: the playbook, the alert and the not-offered notice
(`extended/playbook.py`), on synthetic declarations, logs, result files, calendars, bars and routers only
(`tests/playbook_cases.py`) -- never a bar, never a result of this repository.

What is held (the red team's BUILD_W35 and BUILD_W35_v2 findings and the lead's rulings):
* **B-1, the no-harm floor bound to the design**: its manifest carries the pinned declaration's sha256 and path, the
  margin, the declared script and family; its rows the side rule, the margin and both composites, and the pass is
  recomputed; a mismatch on each field refuses; the declaration is pinned in a row before the floor's; P-14's k is the
  registered one;
* **B-2, offers recomputed**: the alert takes the day's bars and computes the trigger's own offers from the bars closed
  at the alert (the shift-invariance test: scrambling every later bar changes nothing); no offer object is accepted;
* **B-3**: the expected journey bound by the same declaration sha256;
* **B-4**: an RL3 kind's tickets are one alert, one account, one OCO order, checked against the size cap together;
* **B-5**: "offered today" reads only what is known before the alert; the data-defect filters never void an alert;
* **B-6**: every date strict ISO, compared as a date;
* the minors: the manifest pinned, "carried" checked, no price cell, duplicate JSON keys and NaN refused, the account
  the router's, one bar-time wording, no figure in identifiers, an empty news list declared, the pin test;
* and cycle 1's: a scheduled (coin-sided) trade gets the notice, the layout held by goldens reviewed line by line,
  every value piece recomputed independently, determinism, no automation hook.
No randomness is drawn but the scrambles' fixed seeds.
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
H = PC.history()


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


def _refuses(tmp_path, mutate=None, match=None, **kw):
    decl = PC.declaration()
    if mutate is not None:
        mutate(decl)
    with pytest.raises(PB.PlaybookRefused, match=match):
        _load(tmp_path, decl, **kw)


def _alert(c, comp, day, at, *, hist=None, src=None, router=None, offer=True):
    f = PB.render_offer if offer else PB.render_alert
    return f(c, comp, H if hist is None else hist, PC.day_index(day), at, PC.sources() if src is None else src,
             PC.router() if router is None else router)


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
    "stamp": lambda s: _label(int(s) - 1),
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
    return {"plan": "50K Trading Combine", "cap": {"ts_a1": 50, "ts_b2": 20, "ts_c3": 50}, "tickets_alert": 930,
            "tickets_live": 960, "hash": "sha256"}


def _pb_src(c):
    return {"design": PC.declaration(), "library": _library(), "file": {"decl": PC.DECL_FILE, "sha": c.decl_sha},
            "expected": {"file": PC.EXPECTED_FILE, "commit": PC.COMMIT,
                         **{"|".join((r["section"], r["block"], r["measure"], r["stat"])): r["value"]
                            for r in PC.EXPECTED_ROWS}},
            "no_harm": {"file": PC.NO_HARM_FILE, "commit": PC.COMMIT,
                        **{"|".join((r["section"], r["block"], r["measure"], r["stat"])): r["value"]
                           for r in PC.NO_HARM_ROWS}}}


ALERTS = {
    "pm_limit_plain_day": ("pm_brk", "2021-03-16", 1101),
    "pm_limit_window_flatten": ("pm_brk", "2021-03-17", 1101),
    "ldn_market_flatten_at_news": ("ldn_brk", "2021-03-16", 610),
    "ldn_market_flatten_at_closed_window": ("ldn_brk", "2021-03-17", 610),
    "rl3_oco_pair": ("am_rl3", "2021-03-16", 930),
    "rl3_one_ticket_left": ("am_rl3", "2021-04-06", 930),
    "notice_prior_void": ("am_rl3", "2021-03-15", 930),
}


def goldens(c) -> dict[str, str]:
    out = {"playbook": PB.render_playbook(c).text,
           "notice_coin_trade": PB.render_trade(c, R.RoutedTrade(PC.scheduled(), "ts_b2")).text}
    out.update({k: _alert(c, *v).text for k, v in ALERTS.items()})
    return out


# ------------------------------------------------------------------------------------------------ the playbook


def test_goldens_hold_the_layout(carried):
    """R-8: the whole text, every line, against the reviewed goldens."""
    want = json.loads(GOLDEN.read_bytes())
    got = goldens(carried)
    assert sorted(got) == sorted(want)
    for k in want:
        assert got[k].splitlines() == want[k].splitlines(), k


def test_playbook_every_number_traces_to_an_input(carried):
    r = PB.render_playbook(carried)
    assert check_traced(r, _pb_src(carried)) > 70
    text = r.text
    for row in PC.EXPECTED_ROWS[:4]:
        assert row["value"] in text
    assert "999" not in text                                  # a row the declaration does not name is not shown
    assert "Target: 100 ticks (reward to risk 1.3)" in text  # floor(1.3 x 77) = 100, not 101


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
    src = MODULE.read_text(encoding="utf-8")
    tree = ast.parse(src)
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
    stdlib = {"__future__", "csv", "fnmatch", "hashlib", "io", "json", "math", "re", "dataclasses", "datetime",
              "pathlib", "typing", "numpy"}
    own = {"extended", "extended.components", "extended.day_calendar", "extended.lever_space", "extended.modes_terms",
           "extended.router", "extended.trigger_sides", "extended.triggers", "extended.walker", "extended.results",
           "extended.price_levels"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            names = [base] if base != "extended" else [f"extended.{a.name}" if a.name != "ROOT" else base
                                                       for a in node.names]
        else:
            continue
        for n in names:
            assert n in own or n.split(".")[0] in stdlib, f"import {n}: no network, process or broker hook"
    for word in ("open(", "write_text", "write_bytes", "mkdir", "unlink", "socket", "subprocess", "requests"):
        assert word not in src, f"{word}: the playbook writes nothing and opens no channel"


def test_playbook_states_the_rules(carried):
    text = PB.render_playbook(carried).text
    assert "HAND ENTRY ONLY" in text and "no automated or API order entry" in text
    assert "NEVER HOLD OPPOSITE POSITIONS AT ONCE across your accounts or firms" in text
    assert "Never copy a trade to several accounts" in text and "Never put size into major news" in text
    assert "the years this design was chosen on" in text and "held-out years, reported beside" in text
    assert "research filters, not trading rules" in text and "bar ending" not in text                       # m-6


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
    "L-of-latency-free": _set(("components", 1, "latency"), 2),
    "coin-trigger": _set(("components", 0, "trigger", "source"), "coin"),
    "p16-no-side-rule": _set(("components", 0, "trigger"), {"source": "p16", "params": {"marks": [600, 630],
                                                                                         "overnight": True}}),
    "p14-k-not-registered": _set(("components", 2, "trigger", "params", "k"), 7),                    # B-1
    "side-rule-free-words": _set(("components", 2, "side_rule"), "toss a fair coin"),
    "side-rule-blank": _set(("components", 2, "side_rule"), ""),
    "rl3-rule-missing-level": _set(("components", 1, "side_rule"), {"hi": "fade"}),
    "trigger-before-window": _set(("components", 2, "trigger", "params", "first"), 1000),
    "trigger-after-window": _set(("components", 2, "trigger", "params", "last"), 1258),
    "rl3-window-misses-live": _set(("components", 1, "first"), 965),
    "anchor": _set(("session_anchors", "london"), ["Europe/London", "09:00"]),
    "anchor-missing": lambda d: d["session_anchors"].pop("london"),                                   # X35
    "collision": _set(("components", 2, "first"), 1000),
    "rotation": _set(("rotation", "rule"), "copy_to_all"),
    "pool-account": _set(("rotation", "pools", "pm_brk"), ["ts_zz"]),
    "pool-component": _set(("rotation", "pools", "no_such"), ["ts_a1"]),
    "void-rule-unknown": lambda d: d["void_rules"].append("my_hunch"),
    "void-rule-dropped": lambda d: d["void_rules"].remove("prior_abbreviated"),
    "void-rule-twice": lambda d: d["void_rules"].append("fomc"),
    "void-rule-research-only": lambda d: d["void_rules"].append("short_bars"),                        # B-5
    "research-filter-dropped": lambda d: d["research_filters"].remove("overnight_missing"),
    "void-date-reason": _set(("void_dates", 0, "reason"), "my_hunch"),
    "void-date-basic-form": _set(("void_dates", 0, "date"), "20210319"),                              # B-6
    "void-date-padded": _set(("void_dates", 0, "date"), " 2021-03-19"),
    "release-date-basic-form": _set(("news_windows", 1, "dates"), ["20210317"]),                     # B-6, X37
    "release-date-short": _set(("news_windows", 1, "dates"), ["2021-3-17"]),
    "release-dates-none": _set(("news_windows", 1, "dates"), []),
    "anchor-date-basic-form": _set(("dates",), ["20210316"]),                                         # X36
    "news-none-undeclared": _set(("news_windows",), []),                                              # m-8
    "news-source-figure": _set(("news_source",), "record v2"),
    "contracts-zero": _set(("components", 1, "contracts"), 0),
    "contracts-500": _set(("components", 2, "contracts"), 500),
    "contracts-over-funded-cap": _set(("components", 2, "contracts"), 21),
    "rl3-pair-over-cap-together": _set(("components", 1, "contracts"), 26),                           # B-4
    "budget-zero": _set(("bankroll", "budget"), 0),
    "margin-negative": _set(("side", "margin"), -0.01),
    "margin-not-a-number": _set(("side", "margin"), "small"),
    "accounts-repeat": lambda d: d["accounts"].append({"id": "ts_a1", "role": "evaluation"}),
    "no-account": lambda d: d.update(accounts=[], rotation={"rule": "longest_waiting"}),
    "role-unknown": _set(("accounts", 0, "role"), "prop"),
    "label-with-figure": _set(("expected", "rows", 0, "label"), "pass rate 87% (sessions to the first payout)"),
    "label-blank": _set(("expected", "rows", 0, "label"), " "),
    "news-window-source-figure": _set(("news_windows", 0, "source"), "CPI at 7:30"),
    "news-window-off-clock": _set(("news_windows", 0, "release"), 5000),
    "expected-no-rows": _set(("expected", "rows"), []),
    "expected-row-twice": lambda d: d["expected"]["rows"].append(dict(d["expected"]["rows"][0])),
    "expected-block": _set(("expected", "rows", 0, "block"), "all_years"),
    "firm-lucid": _set(("firm",), "lucid"),
    "firm-unknown": _set(("firm",), "not_a_firm"),
    "plan-unknown": _set(("plan",), "the 50K plan"),
    "instrument": _set(("instrument",), "ES"),
    "design-id": _set(("design_id",), "two words"),
}


@pytest.mark.parametrize("name", sorted(MUTATIONS))
def test_disagreement_with_the_library_or_the_ledger_refuses(tmp_path, name):
    _refuses(tmp_path, MUTATIONS[name])


@pytest.mark.parametrize("name", ["pm_wins62.5pct", "pm_brk2021", "pm.brk"])
def test_identifiers_carry_no_figure(tmp_path, name):
    """m-7: the component renamed everywhere (pools, no-harm rows), so only the identifier rule can refuse it."""
    decl = PC.declaration()
    decl["components"][2]["name"] = name
    decl["rotation"]["pools"][name] = decl["rotation"]["pools"].pop("pm_brk")
    rows = [dict(r, measure=name) if r["measure"] == "pm_brk" else dict(r) for r in PC.NO_HARM_ROWS]
    with pytest.raises(PB.PlaybookRefused, match="identifier"):
        _load(tmp_path, decl, no_harm_rows=rows)
    decl["components"][2]["name"] = "pm_brk2"                          # a short suffix is a name, not a figure
    decl["rotation"]["pools"]["pm_brk2"] = decl["rotation"]["pools"].pop(name)
    rows = [dict(r, measure="pm_brk2") if r["measure"] == "pm_brk" else dict(r) for r in PC.NO_HARM_ROWS]
    assert _load(tmp_path / "ok", decl, no_harm_rows=rows)


def test_news_none_declared_with_its_reason_loads(tmp_path):
    decl = PC.declaration()
    decl["news_windows"] = []
    decl["news_none"] = "the record holds no release in these sessions"
    assert "(none: the record holds no release in these sessions)" in PB.render_playbook(_load(tmp_path, decl)).text


def test_coin_refused_as_the_evaluations_device(tmp_path):
    _refuses(tmp_path, _set(("components", 0, "trigger", "source"), "coin"), match="evaluation's device")


@pytest.mark.parametrize("raw", [
    lambda b: b.replace(b'"contracts": 1,', b'"contracts": 1,\n   "contracts": 9,'),
    lambda b: b.replace(b'"rr": 2.25', b'"rr": NaN'),
    lambda b: b.replace(b'"budget": 1700', b'"budget": Infinity'),
    lambda b: b.replace(b'"flatten": 1328', b'"flatten": NaN'),
], ids=["duplicate-key", "nan", "infinity", "nan-where-only-the-parser-refuses"])
def test_declaration_json_strict(tmp_path, raw):
    """m-4: the pinned bytes are the declaration: a duplicate key, NaN or Infinity refuses, even pinned."""
    data = raw(PC.decl_bytes(PC.declaration()))
    assert data != PC.decl_bytes(PC.declaration())
    with pytest.raises(PB.PlaybookRefused, match="twice|non-finite"):
        PB.load_carried(PC.DECL_FILE, root=PC.build_root(tmp_path, raw=data))


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
                                        (("bankroll", "row"), "E-9999"), (("side", "margin_row"), "E-77")],
                         ids=["carrying-missing", "carrying-short", "no-harm-short", "no-harm-pending",
                              "bankroll-missing", "margin-row-missing"])
def test_a_cited_row_not_in_the_log_refuses(tmp_path, path, value):
    _refuses(tmp_path, _set(path, value))


def _sub(row, old, new):
    return lambda rows: {**rows, row: rows[row].replace(old, new)}


ROW_EDITS = {
    "carrying-names-another-design": _sub("E-9004", f"**{PC.DESIGN} carried", "**X-other carried"),
    "carrying-without-registration": _sub("E-9004", PC.REGISTRATION, "REG-other"),
    "carrying-not-carried": _sub("E-9004", "carried, registration", "not carried, registration"),        # m-2
    "carrying-a-draft": _sub("E-9004", "(synthetic)", "(DRAFT for red-team review)"),
    "carrying-never-says-carried": _sub("E-9004", "carried, registration", "pinned, registration"),
    "no-harm-names-another-design": _sub("E-9001", PC.DESIGN, "X-demo70"),
    "expected-unpinned": lambda rows: {**rows, "E-9004": rows["E-9004"].split("; its expected")[0]},
    "expected-manifest-unpinned": lambda rows: {**rows, "E-9004": rows["E-9004"].split("; its manifest")[0]},
    "no-harm-unpinned": lambda rows: {**rows, "E-9001": "**no pin here**"},
    "no-harm-manifest-unpinned": lambda rows: {**rows, "E-9001": rows["E-9001"].split("; its manifest")[0]},
    "floor-before-the-declaration": lambda rows: {k: v for k, v in rows.items() if k != "E-9000"},   # B-1
    "declaration-pinned-after-floor": lambda rows: {"E-9001": rows["E-9001"], "E-9000": rows["E-9000"],
                                                    "E-9002": rows["E-9002"], "E-9004": rows["E-9004"]},
    "a-path-pinned-twice": lambda rows: {**rows, "E-9004": rows["E-9004"].replace(                     # N-3
        "(synthetic)**", "(synthetic)** the reviewed text `" + PC.DECL_FILE + "` sha256 `" + "b" * 64 + "`, revised to")},
}


@pytest.mark.parametrize("edit", sorted(ROW_EDITS))
def test_rows_must_order_name_carry_and_pin(tmp_path, edit):
    with pytest.raises(PB.PlaybookRefused):
        _load(tmp_path, edit_rows=ROW_EDITS[edit])


def test_a_cited_row_pinning_a_path_twice_refuses_for_that(tmp_path):
    """N-3: the reviewed text and its revision pinned in one row -- refused as such, not by the later pin's luck."""
    with pytest.raises(PB.PlaybookRefused, match="pins prereg/X-demo7_playbook.json twice"):
        _load(tmp_path, edit_rows=ROW_EDITS["a-path-pinned-twice"])


def test_an_unrelated_row_pinning_twice_does_not_block(tmp_path):
    rows_edit = lambda rows: {"E-8999": "`prereg/other.json` sha256 `" + "c" * 64 + "` then `prereg/other.json` "  # noqa
                              "sha256 `" + "d" * 64 + "`", **rows}
    assert _load(tmp_path, edit_rows=rows_edit).decl_sha


def test_a_repeated_row_in_the_log_refuses(root):
    log = root / "DECISIONS.md"
    log.write_bytes(log.read_bytes() + b"| E-9002 | 2021-01-02 | again | synthetic |\n")
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


def test_playbook_declarations_are_in_the_pin_test():
    """m-9: tests/test_declarations_fixed.py holds a playbook declaration's pin as it holds a family's."""
    text = (ROOT / "tests" / "test_declarations_fixed.py").read_text(encoding="utf-8")
    assert "_playbook" in text and "json" in text


# ------------------------------------------------------------------------------------------------ B-1, B-3: the bindings


def _flip(d):
    d["components"][2]["side_rule"] = "with_breakout"


def _other_stop(d):
    d["components"][0]["stop_ticks"] = 20


def _other_rotation(d):
    d["rotation"] = {"rule": "longest_waiting"}


@pytest.mark.parametrize("change", [_flip, _other_stop, _other_rotation], ids=["side-rule-flipped", "stop", "rotation"])
def test_results_bound_to_another_declaration_refuse(tmp_path, change):
    """B-1, B-3 (the note's P3, P4): the declaration changed and re-pinned, the result files those of the old one."""
    decl = PC.declaration()
    change(decl)
    with pytest.raises(PB.PlaybookRefused, match="bound to this pinned declaration"):
        _load(tmp_path, decl, bind=PC.declaration())


NO_HARM_MANIFEST_FAULTS = {
    "declaration-sha": dict(parameters_update={"declaration_sha256": "e" * 64}),
    "declaration-file": dict(parameters_update={"declaration_file": "prereg/other_playbook.json"}),
    "margin": dict(parameters_update={"margin": 0.1}),
    "margin-absent": dict(parameters_update={"margin": None}),
    "script": dict(script="scratch/anything.py"),
    "family": dict(prereg_id=None),
    "design": dict(parameters_update={"design_id": "X-other"}),
    "convention": dict(parameters_update={"convention": "zero_edge"}),
}


@pytest.mark.parametrize("fault", sorted(NO_HARM_MANIFEST_FAULTS))
def test_no_harm_manifest_field_mismatch_refuses(tmp_path, fault):
    with pytest.raises(PB.PlaybookRefused):
        _load(tmp_path, no_harm_over=NO_HARM_MANIFEST_FAULTS[fault])


def _nh_rows(comp, stat, value):
    rows = [dict(r) for r in PC.NO_HARM_ROWS]
    for r in rows:
        if r["measure"] == comp and r["stat"] == stat:
            r["value"] = value
    return rows


@pytest.mark.parametrize("comp,stat,value", [
    ("pm_brk", "side_rule", "with_breakout"), ("am_rl3", "side_rule", "hi=break;lo=fade"),
    ("am_rl3", "margin", "0.1"), ("am_rl3", "trigger_composite", "0.23"), ("pm_brk", "coin_composite", "0.46"),
    ("ldn_brk", "trigger_composite", "pass"), ("ldn_brk", "coin_composite", "nan"),
], ids=["p14-rule", "rl3-rule", "margin", "rl3-failed", "p14-failed", "not-a-number", "not-finite"])
def test_no_harm_row_mismatch_or_failure_refuses(tmp_path, comp, stat, value):
    with pytest.raises(PB.PlaybookRefused, match="no-harm floor|not a number|not finite"):
        _load(tmp_path, no_harm_rows=_nh_rows(comp, stat, value))


@pytest.mark.parametrize("stat", PB.NO_HARM_STATS)
def test_no_harm_row_absent_refuses(tmp_path, stat):
    rows = [r for r in PC.NO_HARM_ROWS if not (r["measure"] == "ldn_brk" and r["stat"] == stat)]
    with pytest.raises(PB.PlaybookRefused, match="absent"):
        _load(tmp_path, no_harm_rows=rows)


def test_no_harm_pass_is_recomputed_at_the_margin(tmp_path):
    """The floor at its edge: the trigger side's composite exactly the coin's less the margin passes; a hair below
    refuses."""
    rows = _nh_rows("am_rl3", "trigger_composite", "0.24")          # 0.29 - 0.05 = 0.24 (in binary, just above)
    tc, cc = 0.24, 0.29
    if tc < cc - PC.MARGIN:
        with pytest.raises(PB.PlaybookRefused, match="failed"):
            _load(tmp_path, no_harm_rows=rows)
    else:
        assert _load(tmp_path, no_harm_rows=rows)
    with pytest.raises(PB.PlaybookRefused, match="failed"):
        _load(tmp_path / "b", no_harm_rows=_nh_rows("am_rl3", "trigger_composite", "0.2399"))


EXPECTED_MANIFEST_FAULTS = {
    "no-clean-run": dict(provenance=None),
    "clean-run-unnamed": dict(provenance={"clean_run": {"name": ""}}),
    "commit-unknown": dict(git_commit="unknown", git_dirty=None),
    "commit-dirty": dict(git_commit=PC.COMMIT + "-dirty", git_dirty=True),
    "dirty-flag": dict(git_dirty=True),
    "dirty-unrecorded": dict(git_dirty=None),
    "commit-blank": dict(git_commit=""),
    "exploratory": dict(exploratory=True),
    "other-design": dict(parameters_update={"design_id": "SOME-OTHER-DESIGN"}),
    "as-traded": dict(parameters={"design_id": PC.DESIGN, "as_traded": True}),
    "other-convention": dict(parameters_update={"convention": "no_harm_real_path"}),
    "declaration-sha": dict(parameters_update={"declaration_sha256": "e" * 64}),          # B-3
    "declaration-file": dict(parameters_update={"declaration_file": "prereg/other.json"}),
    "script": dict(script="scratch/anything.py"),
    "family": dict(prereg_id="F-other"),
    "hash-not-the-files": dict(sha256="0" * 64),
}


@pytest.mark.parametrize("fault", sorted(EXPECTED_MANIFEST_FAULTS))
def test_expected_file_manifest_fault_refuses(tmp_path, fault):
    with pytest.raises(PB.PlaybookRefused):
        _load(tmp_path, expected_over=EXPECTED_MANIFEST_FAULTS[fault])


def test_manifest_edited_after_its_pin_refuses(root):
    """m-1 (the note's P16): an exploratory manifest relabelled after its CSV was pinned."""
    mp = Path(str(root / PC.EXPECTED_FILE) + PC.MANIFEST)
    m = json.loads(mp.read_bytes())
    m["description"] = "edited after the pin"
    mp.write_bytes(json.dumps(m, indent=2, sort_keys=True).encode())
    with pytest.raises(PB.PlaybookRefused, match="manifest is not the one pinned"):
        PB.load_carried(PC.DECL_FILE, root=root)


@pytest.mark.parametrize("row,name", [("E-9004", "journey_x"), ("E-9001", "noharm_x")])
def test_the_csv_pin_in_the_row_must_be_the_manifests(tmp_path, row, name):
    """The CSV's own pin (its manifest's pin left right) must equal the hash its manifest records."""
    edit = lambda rows: {**rows, row: re.sub("(" + name + r"\.csv` sha256 `)[0-9a-f]+", lambda m: m.group(1) + "a" * 64,  # noqa
                                            rows[row])}
    with pytest.raises(PB.PlaybookRefused, match="do not agree on its hash"):
        _load(tmp_path, edit_rows=edit)


def test_result_read_from_one_resolved_path(carried, root):
    assert sorted(CALLS) == sorted({(root / PC.EXPECTED_FILE).resolve(), (root / PC.NO_HARM_FILE).resolve()})


def test_tampered_or_missing_result_refuses(root):
    p = root / PC.EXPECTED_FILE
    p.write_bytes(p.read_bytes().replace(b"37.5", b"12.5"))
    with pytest.raises(PB.PlaybookRefused):
        PB.load_carried(PC.DECL_FILE, root=root)
    p.unlink()
    with pytest.raises(PB.PlaybookRefused):
        PB.load_carried(PC.DECL_FILE, root=root)


@pytest.mark.parametrize("rel", ["results/s1_range.csv", "results/q121_vol_descriptive_a1.csv",
                                 "results/scratch/x.csv", "elsewhere/journey_x.csv", "results/../journey_x.csv",
                                 "results/journey_x.txt"])
def test_licensed_ignored_or_misplaced_result_refuses(tmp_path, rel):
    decl = PC.declaration()
    decl["expected"]["file"] = rel
    with pytest.raises(PB.PlaybookRefused):
        _load(tmp_path, decl)


@pytest.mark.parametrize("where", ["value", "n"])
def test_one_price_cell_refuses(tmp_path, where):
    """m-3 (the note's P7): one cell inside the band and on the tick grid, anywhere in the file."""
    rows = [dict(r) for r in PC.EXPECTED_ROWS]
    rows[3][where] = "18234.75"
    with pytest.raises(PB.PlaybookRefused, match="price cell"):
        _load(tmp_path, expected_rows=rows)


def test_result_row_absent_twice_or_blank_refuses(tmp_path):
    with pytest.raises(PB.PlaybookRefused):
        _load(tmp_path / "a", expected_rows=PC.EXPECTED_ROWS[1:])
    with pytest.raises(PB.PlaybookRefused):
        _load(tmp_path / "b", expected_rows=PC.EXPECTED_ROWS + PC.EXPECTED_ROWS[:1])
    blank = [dict(r) for r in PC.EXPECTED_ROWS]
    blank[0]["value"] = " "
    with pytest.raises(PB.PlaybookRefused, match="blank"):
        _load(tmp_path / "c", expected_rows=blank)


def test_result_files_through_the_real_verify_result(tmp_path):
    """The vendored writer and verify_result, in their own process: a clean, bound file is accepted; a tampered one,
    one written outside a clean run, and the red team's first probe 2 (exploratory, another design) refuse."""
    env = dict(os.environ, OMP_NUM_THREADS="1")
    out = subprocess.run([sys.executable, str(ROOT / "tests" / "playbook_cases.py"), "results", str(tmp_path)],
                         env=env, capture_output=True, text=True, timeout=600, cwd=str(ROOT))
    assert out.returncode == 0, out.stderr
    got = json.loads(out.stdout.strip().splitlines()[-1])
    assert got["clean"] == "accepted:" + PC.COMMIT
    for k in ("tampered", "as_written", "other_design"):
        assert got[k].startswith("refused:"), (k, got[k])


# ------------------------------------------------------------------------------------------------ the alert


def test_alerts_trace_and_never_print_a_price(carried):
    for name, (comp, day, at) in ALERTS.items():
        r = _alert(carried, comp, day, at)
        assert check_traced(r, {"design": carried.decl, "day": day, "library": _library()}) >= 1
        t = r.text
        for price in ("18000", "18100", "17900", "17990", "18110", "18234"):
            assert price not in t, (name, price)
        assert not re.search(r"\d{3,}\.\d", t)
        assert "bar ending" not in t                                                             # m-6
        for hook in ("http", "webhook", "json", "{", "api"):
            assert hook not in t.lower()


def test_the_cut_keeps_only_the_bars_closed_at_the_alert():
    """feature-rules section 1: at slot `at` of day `i`, the days up to `i`, and of day `i` the walker's columns up to
    `at` (the bars stamped before it); every later bar NaN."""
    import numpy as np

    for i, at in ((1, 1101), (1, 610), (3, 930)):
        cut = PB.cut_history(H, i, at)
        assert cut.days == H.days[: i + 1] and len(cut) == i + 1
        for a, b in ((cut.o, H.o), (cut.h, H.h), (cut.l, H.l), (cut.c, H.c)):
            assert np.array_equal(a[:i], b[:i], equal_nan=True)
            assert np.array_equal(a[i, : at + 1], b[i, : at + 1], equal_nan=True)
            assert np.isnan(a[i, at + 1:]).all()
    assert not np.isnan(H.c[1, 1102:]).all()                           # the cut, not the fixture, holds the NaNs


def test_the_offer_is_recomputed_from_the_bars_closed_at_the_alert(carried):
    """B-2, the feature-rules shift-invariance test: every bar not closed at the alert, and every later day, replaced
    by a random walk (fixed seeds), changes nothing."""
    for comp, day, at in ALERTS.values():
        i = PC.day_index(day)
        want = _alert(carried, comp, day, at).text
        for seed in (11, 12, 13):
            assert _alert(carried, comp, day, at, hist=PC.scrambled(H, i, at, seed)).text == want


def test_the_side_comes_from_the_bars(carried):
    """B-2 (the note's P1, P2): the same moment with the breakout the other way gives the other side, and a level on
    the other side of the reference gives the other role -- read from the bars, never from the caller."""
    import numpy as np

    i = PC.day_index("2021-03-16")
    arrs = [np.array(x, copy=True) for x in (H.o, H.h, H.l, H.c)]
    arrs[1][i, 1101] = PC.HIGH                       # no close above the high at 11:21 ...
    arrs[2][i, 1101] = arrs[3][i, 1101] = PC.LOW - 10.0     # ... but one below the low
    down = T.History(H.days, H.contract, *arrs)
    assert "Side BUY (long): the breakout was a close below" in _alert(carried, "pm_brk", "2021-03-16", 1101,
                                                                       hist=down).text
    arrs = [np.array(x, copy=True) for x in (H.o, H.h, H.l, H.c)]
    arrs[3][i, 930] = PC.HIGH + 50.0                 # the price at the alert above the previous day's high
    t = _alert(carried, "am_rl3", "2021-03-16", 930, hist=T.History(H.days, H.contract, *arrs)).text
    assert "regular-session high, a support" in t and "Ticket 1 of 2: Side BUY (long)" in t


def test_no_offer_object_and_no_trade_is_accepted(carried):
    off = T.Offer("p14", 1, 1101, 0, 1101, 1104, T.LIMIT, 18110.0, expires=1133, tag="brk30-")
    for bad in (off, PC.scheduled(), R.RoutedTrade(PC.scheduled(), "ts_b2")):
        with pytest.raises(PB.AlertRefused) as e:
            PB.render_offer(carried, "pm_brk", bad, PC.day_index("2021-03-16"), 1101, PC.sources(), PC.router())
        assert e.value.reason == "mismatch"


@pytest.mark.parametrize("comp,at", [("pm_brk", 1102), ("pm_brk", 1100), ("ldn_brk", 611), ("am_rl3", 931)])
def test_no_offer_at_that_moment_refuses(carried, comp, at):
    with pytest.raises(PB.AlertRefused) as e:
        _alert(carried, comp, "2021-03-16", at)
    assert e.value.reason == "no_offer"


@pytest.mark.parametrize("label", ["coin", "trigger"])
def test_a_scheduled_trade_gets_the_not_offered_notice(carried, label):
    tr = PC.scheduled(side_source=label)
    for x in (tr, R.RoutedTrade(tr, "ts_b2")):
        r = PB.render_trade(carried, x)
        assert r.text.startswith("NOT OFFERED today") and "evaluation's coin" in r.text
    with pytest.raises(PB.AlertRefused):
        PB.render_trade(carried, PC.scheduled(source="rl3"))


def test_rl3_pair_is_one_oco_alert_in_one_account(carried, tmp_path):
    """B-4: the pair in one alert, one account, as one OCO order, its size counted together."""
    t = _alert(carried, "am_rl3", "2021-03-16", 930).text
    assert "ONE-CANCELS-OTHER" in t and "When one fills, cancel the other at once" in t
    assert "Never split them across accounts" in t and "this pair counts as one order" in t
    assert t.count("account ts_") == 1 and "Ticket 1 of 2" in t and "Ticket 2 of 2" in t
    assert "2 contracts on each ticket, 4 for the pair together" in t
    decl = PC.declaration()
    decl["components"][1]["side_rule"] = {"hi": "break", "lo": "break"}
    decl["components"][1]["contracts"] = 25
    rows = [dict(r) for r in PC.NO_HARM_ROWS]
    for r in rows:
        if r["measure"] == "am_rl3" and r["stat"] == "side_rule":
            r["value"] = "hi=break;lo=break"
    c = _load(tmp_path, decl, no_harm_rows=rows)
    t = _alert(c, "am_rl3", "2021-03-16", 930).text
    assert "Ticket 1 of 2: Side BUY (long)" in t and "Ticket 2 of 2: Side SELL (short)" in t
    assert "STOP 1 tick above the level" in t and "STOP 1 tick below the level" in t
    assert "25 contracts on each ticket, 50 for the pair together (the firm's verified limit for this account: 50)" in t


def test_account_is_the_routers_pick(carried, tmp_path):
    """m-5: under by_component the pool's longest-waiting account; under longest_waiting the firm's; a router under
    another rotation, or none, refuses."""
    assert "account ts_a1:" in _alert(carried, "am_rl3", "2021-03-16", 930).text
    busy = PC.router(ts_a1=5000)
    assert "account ts_c3:" in _alert(carried, "am_rl3", "2021-03-16", 930, router=busy).text
    decl = PC.declaration()
    decl["rotation"] = {"rule": "longest_waiting"}
    c = _load(tmp_path, decl)
    r = PC.router(decl, ts_a1=5000, ts_b2=4000)
    assert "account ts_c3:" in _alert(c, "pm_brk", "2021-03-16", 1101, router=r).text
    for bad in (PC.router(decl), None):
        with pytest.raises(PB.AlertRefused):
            PB.render_offer(carried, "pm_brk", H, PC.day_index("2021-03-16"), 1101, PC.sources(), bad)


@pytest.mark.parametrize("day", ["2024-05-01", "2026-08-03"], ids=["held-out", "confirmation-window"])
def test_a_day_after_the_search_years_refuses(carried, day):
    hist = T.History((day,), ("NQM4",), H.o[1:2], H.h[1:2], H.l[1:2], H.c[1:2])
    with pytest.raises(PB.AlertRefused) as e:
        PB.render_offer(carried, "pm_brk", hist, 0, 1101, PC.sources(), PC.router())
    assert e.value.reason == "mismatch"


@pytest.mark.parametrize("day", ["20210316", "2021-3-16"])
def test_a_history_day_not_strict_iso_refuses(carried, day):
    days = list(H.days)
    days[1] = day
    hist = T.History(tuple(days), H.contract, H.o, H.h, H.l, H.c)
    with pytest.raises(PB.AlertRefused):
        PB.render_offer(carried, "pm_brk", hist, 1, 1101, PC.sources(), PC.router())


def test_the_caller_cannot_supply_the_day(carried):
    with pytest.raises(PB.AlertRefused):
        PB.render_offer(carried, "pm_brk", H, 1, 1101, T.DayContext(1, "2021-03-16"), PC.router())


KNOWN_AT_ALERT = [
    ("fomc", "pm_brk", "2021-03-16", 1101, dict(fomc=("2021-03-16",)), "fomc"),
    ("scheduled-close", "pm_brk", "2021-03-16", 1101,
     dict(calendar={"2021-03-16": {"kind": "early_close", "close_ct": "12:00"}}), "calendar"),
    ("declared-void-date", "pm_brk", "2021-03-19", 1101, {}, "declared_void"),
    ("prior-void-first-day", "am_rl3", "2021-03-15", 930, {}, "prior_void"),
    ("prior-void-roll", "am_rl3", "2021-03-16", 930, dict(rolls=("2021-03-16",)), "prior_void"),
    ("prior-void-after-closure", "am_rl3", "2021-04-05", 930, {}, "prior_void"),
    ("prior-void-after-scheduled-close", "am_rl3", "2021-03-17", 930,
     dict(calendar={"2021-03-16": {"kind": "early_close", "close_ct": "12:00"}}), "prior_void"),
    ("bls-overnight-entry", "ldn_brk", "2021-03-16", 610, dict(bls=("2021-03-16",)), "bls"),
]


@pytest.mark.parametrize("case,comp,day,at,src,reason", KNOWN_AT_ALERT, ids=[k[0] for k in KNOWN_AT_ALERT])
def test_the_calendar_known_at_the_alert_voids_the_offer(carried, case, comp, day, at, src, reason):
    with pytest.raises(PB.AlertRefused) as e:
        _alert(carried, comp, day, at, src=PC.sources(**src), offer=False)
    assert e.value.reason == reason
    note = _alert(carried, comp, day, at, src=PC.sources(**src))
    assert note.text.startswith("NOT OFFERED today") and PB.REASON_WORDS[reason] in note.text


def test_the_missing_0829_bar_is_seen_in_the_bars_at_the_alert(carried):
    note = _alert(carried, "am_rl3", "2021-03-16", 930, hist=PC.history(no_0829=("2021-03-16",)))
    assert PB.REASON_WORDS["no_ref_bar"] in note.text


RESEARCH_ONLY = [
    ("short-last-bar", "ldn_brk", 610, dict(last_bar={"2021-03-16": "14:00"})),
    ("early-end", "pm_brk", 1101, dict(early_end=("2021-03-16",))),
    ("data-defect", "pm_brk", 1101, dict(calendar={"2021-03-16": {"kind": "data_defect_candidate", "close_ct": ""}})),
    ("h2-void", "ldn_brk", 610, dict(flags={"2021-03-16": {"verdict": "VOID", "void": "synthetic"}})),
    ("h2-missing", "ldn_brk", 610, dict(flags={"2021-03-16": {"missing_after_reopen": "999"}})),
    ("prior-day-data-void", "am_rl3", 930, dict(early_end=("2021-03-15",))),
]


@pytest.mark.parametrize("case,comp,at,src", RESEARCH_ONLY, ids=[k[0] for k in RESEARCH_ONLY])
def test_research_filters_never_decide_an_alert(carried, case, comp, at, src):
    """B-5 (the note's P10): what is known only after the alert never voids it."""
    want = _alert(carried, comp, "2021-03-16", at).text
    assert want.startswith("TRADE ALERT")
    assert _alert(carried, comp, "2021-03-16", at, src=PC.sources(**src)).text == want


def test_prior_void_reaches_pdc_too(tmp_path):
    """m-9's X4: a `pdc` component (the previous day's close) is void on a roll day as `pd` is."""
    decl = PC.declaration()
    decl["components"][1]["trigger"]["params"]["kind"] = "pdc"
    decl["components"][1]["side_rule"] = {"lvl": "fade"}
    rows = [dict(r) for r in PC.NO_HARM_ROWS]
    for r in rows:
        if r["measure"] == "am_rl3" and r["stat"] == "side_rule":
            r["value"] = "lvl=fade"
    c = _load(tmp_path, decl, no_harm_rows=rows)
    assert _alert(c, "am_rl3", "2021-03-16", 930).text.startswith("TRADE ALERT")
    note = _alert(c, "am_rl3", "2021-03-16", 930, src=PC.sources(rolls=("2021-03-16",)))
    assert PB.REASON_WORDS["prior_void"] in note.text


def test_news_window_from_the_declared_record(carried):
    """R-4, B-6: the window comes from the declaration's dated record (2021-03-17's afternoon release, bars stamped
    11:57 to 12:06 CT), dates compared as dates; an order live inside it is not offered."""
    import numpy as np

    i = PC.day_index("2021-03-17")
    arrs = [np.array(x, copy=True) for x in (H.o, H.h, H.l, H.c)]
    arrs[1][i, 1138] = arrs[3][i, 1138] = PC.HIGH + 30.0           # a breakout at 11:58 CT, live at 12:01
    hist = T.History(H.days, H.contract, *arrs)
    with pytest.raises(PB.AlertRefused) as e:
        _alert(carried, "pm_brk", "2021-03-17", 1138, hist=hist, offer=False)
    assert e.value.reason == "news"
    t = _alert(carried, "pm_brk", "2021-03-17", 1101).text
    assert "(it ends at 11:57 CT), when a news window starts (a synthetic afternoon release)" in t


def test_rl3_ticket_rewritten_after_a_window(tmp_path):
    decl = PC.declaration()
    decl["news_windows"].append({"source": "a synthetic morning release", "release": 990, "before": 1, "after": 4,
                                 "dates": ["2021-03-16"]})
    t = _alert(_load(tmp_path, decl), "am_rl3", "2021-03-16", 930).text
    assert "Working on the bars stamped 09:00 CT through 09:28 CT" in t
    assert "(it ends at 09:29 CT), when a news window starts (a synthetic morning release)" in t
    assert "Working on the bars stamped 09:35 CT through 09:59 CT" in t


def test_not_offered_reasons_are_a_closed_vocabulary(carried):
    with pytest.raises(PB.AlertRefused):
        PB._notice(carried, "pm_brk", 1104, "price 18234.75")
    r = PB._notice(carried, "pm_brk", 1104, "position")
    assert check_traced(r, {"design": carried.decl, "offer": {"live": 1104}}) == 2
    assert "a position is already open" in r.text


def test_brief_command_forbids_licensed_quotes_and_automation():
    """N-2: `/brief` never quotes a licensed-price derivative and never suggests automating orders."""
    text = (ROOT / ".claude" / "commands" / "brief.md").read_text(encoding="utf-8")
    assert "Never quote anything from a licensed-price derivative" in text and "git-ignored" in text
    assert "never suggest automating orders" in text and "never a command that writes a file" in text
