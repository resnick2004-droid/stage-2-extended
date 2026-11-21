"""The restart plan's Wave 3.5, corrective cycle 2 and the final read's fixes: the playbook, the alert and the
not-offered notice (`extended/playbook.py`), on synthetic declarations, carrying records, logs, git histories, result
files, calendars, bars and routers only (`tests/playbook_cases.py`) -- never a bar, never a result of this repository.

What is held (the red team's BUILD_W35, BUILD_W35_v2 and BUILD_W35_c2 findings and the lead's rulings):
* **C2-1, C3-5**: the declaration's margin is the one the log's single margin row pins, before the declaration's pin;
  **C2-2, C3-4, N-c3-3**: the floor's and the journey's runs descend, in git, from the commit that pinned the
  declaration, on HEAD's line; **C3-1**: the previous session is the calendar's, and a store that lacks it refuses;
  **C3-7**: the carrying token pins the joint held-out test's accepted result; **C2-5**: the registration and the carrying row live in the carrying record,
  not the hashed declaration; **C2-7**: "carried" is the row's structured token, no negation or condition;
* **C2-3**: the windows are offsets from each session's local open, per date, through `search_space`'s own
  `windows_on` -- goldens for London and Asia across the daylight-saving changes;
* **C2-4**: every resting order's alert states the void-at-live rule (a golden from the red team's void probe);
* **C2-6**: RL3's tickets rested by hand as plain orders with Auto-OCO brackets, the other cancelled by hand;
* **C2-8**: the result files' columns classed by the pinned list; **C2-9**: every level defined by its bars;
  **C2-10**: identifiers in full, a digit only as `_v<d>`; **C2-11**: the three survivors' tests; **N-c2-1**: the
  router picks among the accounts alive that day; **N-c2-2**: a closure only when the calendar schedules it;
* and the earlier cycles': B-1 to B-6, R-1 to R-13, the minors, the goldens, determinism, no automation hook.
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
from extended import search_space as SS
from extended import triggers as T
from tests import playbook_cases as PC

ROOT = Path(__file__).resolve().parent.parent
MODULE = ROOT / "extended" / "playbook.py"
GOLDEN = ROOT / "tests" / "data" / "playbook_golden.json"
DIGIT = re.compile(r"\d")
CALLS: list[Path] = []
PINS: list[tuple] = []
H = PC.history()
REAL_RUN_AFTER_PIN = PB._run_after_pin


@pytest.fixture(autouse=True)
def _standin(monkeypatch):
    """The vendored verify_result stays out of the test runner's process (it puts the vendored tree on sys.path); the
    stand-in is its check and records the path it is given. The pin order (git) has its own tests (`git_root`)."""
    CALLS.clear()
    PINS.clear()

    def rec(path):
        CALLS.append(Path(path))
        return PC.verify_standin(path)

    def pin(root, text, commit):
        PINS.append((text, commit))
        return True

    monkeypatch.setattr(PB, "_verify_result", rec)
    monkeypatch.setattr(PB, "_run_after_pin", pin)


@pytest.fixture
def root(tmp_path):
    return PC.build_root(tmp_path)


@pytest.fixture
def carried(root):
    return PB.load_carried(PC.RECORD_FILE, root=root)


def _load(tmp_path, decl=None, **kw):
    return PB.load_carried(PC.RECORD_FILE, root=PC.build_root(tmp_path, decl, **kw))


def _refuses(tmp_path, mutate=None, match=None, **kw):
    decl = PC.declaration()
    if mutate is not None:
        mutate(decl)
    with pytest.raises(PB.PlaybookRefused, match=match):
        _load(tmp_path, decl, **kw)


def _alert(c, comp, day, at, *, hist=None, src=None, router=None, offer=True, accounts=PC.ACCOUNTS):
    f = PB.render_offer if offer else PB.render_alert
    return f(c, comp, H if hist is None else hist, PC.day_index(day), at, PC.sources() if src is None else src,
             PC.router() if router is None else router, accounts)


def _ldn(day):
    return PC.event_slot(day, "london")


def _asia(day):
    return PC.event_slot(day, "asia")


# ------------------------------------------------------------------------------------------------ independent checks


def _res(src, path):
    cur = src
    for k in path:
        cur = cur[k]
    return cur


def _label(s):
    m = (int(s) + 17 * 60) % 1440
    return "%02d:%02d" % (m // 60, m % 60)


_ANCHOR = {"london": ("Europe/London", 8, 0), "ny_am": ("America/New_York", 9, 30), "ny": ("America/New_York", 9, 30),
           "ny_pm": ("America/New_York", 12, 0), "asia": ("Asia/Tokyo", 9, 0)}      # NY PM opens at T2b's noon


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
    recomputation from `src` (the module's computed `calc` pieces are held by the goldens instead)."""
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
    # 10 micros a mini; the plan's name as `combine_mll`'s note writes it; RL3's bars (triggers.rl3_levels)
    return {"plan": "50K Trading Combine", "cap": {"ts_a": 50, "ts_b": 20, "ts_c": 50}, "tickets_alert": 930,
            "tickets_live": 960, "hash": "sha256", "prior_first": 930, "prior_last": 1319, "reopen": 0,
            "pre_open": 929, "breakout_last": 1260,
            "sources": {"auto_oco": "14434175", "title": "TopstepX", "order_types": "8765442", "read": "2026-11-21"}}


def _pb_src(c):
    return {"design": PC.declaration(), "library": _library(),
            "file": {"decl": PC.DECL_FILE, "sha": c.decl_sha, "record": PC.RECORD_FILE, "heldout": PC.HELDOUT_FILE,
                     "heldout_commit": PC.COMMIT},
            "carry": {"row": "E-9004", "registration": PC.REGISTRATION},
            "expected": {"file": PC.EXPECTED_FILE, "commit": PC.COMMIT,
                         **{"|".join((r["section"], r["block"], r["measure"], r["stat"])): r["value"]
                            for r in PC.EXPECTED_ROWS}},
            "no_harm": {"file": PC.NO_HARM_FILE, "commit": PC.COMMIT,
                        **{"|".join((r["section"], r["block"], r["measure"], r["stat"])): r["value"]
                           for r in PC.NO_HARM_ROWS}}}


def _void_probe_history():
    """The red team's `probe_void.py` case: the market keeps rising after the 11:21 breakout close, so by 11:24 a SELL
    limit at that close would be marketable (void in the evaluation)."""
    import numpy as np

    i = PC.day_index("2021-03-16")
    arrs = [np.array(x, copy=True) for x in (H.o, H.h, H.l, H.c)]
    for j in (1102, 1103, 1104):
        for x in arrs:
            x[i, j] = PC.HIGH + 20.0
    return T.History(H.days, H.contract, *arrs)


ALERTS = {
    "pm_limit_plain_day": ("pm_brk", "2021-03-16", 1101, None),
    "pm_limit_void_probe_case": ("pm_brk", "2021-03-16", 1101, "void"),
    "pm_limit_window_flatten": ("pm_brk", "2021-03-17", 1101, None),
    "ldn_standard_time": ("ldn_brk", "2021-03-12", _ldn("2021-03-12"), None),
    "ldn_mismatch_week_flatten_at_news": ("ldn_brk", "2021-03-16", _ldn("2021-03-16"), None),
    "ldn_mismatch_week_flatten_at_closed_window": ("ldn_brk", "2021-03-17", _ldn("2021-03-17"), None),
    "asia_standard_time": ("asia_brk", "2021-03-12", _asia("2021-03-12"), None),
    "asia_daylight_time": ("asia_brk", "2021-03-16", _asia("2021-03-16"), None),
    "rl3_pair": ("am_tix", "2021-03-16", 930, None),
    "rl3_one_ticket_left": ("am_tix", "2021-04-06", 930, None),
    "notice_prior_void": ("am_tix", "2021-03-11", 930, None),
}


def goldens(c) -> dict[str, str]:
    out = {"playbook": PB.render_playbook(c).text,
           "notice_coin_trade": PB.render_trade(c, R.RoutedTrade(PC.scheduled(), "ts_b")).text}
    for k, (comp, day, at, hist) in ALERTS.items():
        out[k] = _alert(c, comp, day, at, hist=_void_probe_history() if hist == "void" else None).text
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
    assert check_traced(r, _pb_src(carried)) > 80
    text = r.text
    for row in PC.EXPECTED_ROWS[:4]:
        assert row["value"] in text
    assert "999" not in text                                  # a row the declaration does not name is not shown
    assert "Target: 100 ticks (reward to risk 1.3)" in text  # floor(1.3 x 77) = 100, not 101


def test_playbook_deterministic_across_hash_seeds(carried, root):
    a = PB.render_playbook(carried).text
    assert a == PB.render_playbook(PB.load_carried(PC.RECORD_FILE, root=root)).text
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
    for node in ast.walk(tree):                     # citations and measure ids, not figures (C3-6, C3-8)
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in ("FIGURE_MEASURES",
                                                                                    "PLATFORM_SOURCES")
                                                for t in node.targets):
            docs.update(id(c) for c in ast.walk(node.value) if isinstance(c, ast.Constant))
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
    stdlib = {"__future__", "csv", "fnmatch", "functools", "hashlib", "io", "json", "math", "re", "dataclasses",
              "datetime", "pathlib", "typing", "numpy"}
    own = {"extended", "extended.components", "extended.day_calendar", "extended.lever_space", "extended.modes_terms",
           "extended.router", "extended.search_space", "extended.trigger_sides", "extended.triggers",
           "extended.walker", "extended.results", "extended.price_levels", "extended.pin_order"}
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
    assert "research filters, not trading rules" in text and "bar ending" not in text
    assert "would fill at once when it goes live" in text                                            # C2-4
    assert "OCO order type" not in text and "cancelled by hand the moment one fills" in text          # C2-6
    assert "article 14434175 (\"TopstepX\")" in text and "article 8765442 for the order types" in text  # C3-6
    assert "results/heldout_x.csv" in text and "never after 14:00 CT" in text


def test_windows_are_the_search_spaces_offsets_per_date(carried):
    """C2-3: each component's window on each date is `search_space.Space.windows_on`'s (the session's anchored start
    plus the declared offsets), London and Asia moving in CT across the daylight-saving changes."""
    decl = carried.decl
    space = PB.window_space(decl)
    design = PB._space_design(decl)
    for d in [date.fromisoformat(x) for x in PC.DAYS]:
        want = {name: (a, b) for name, _, a, b in space.windows_on(design, d)}
        got = {c.name: (c.first, c.last) for c in PB.design_on(decl, space, d).components}
        assert got == want
        starts = {k: a for k, (a, _) in SS.session_spans(d, PB._split()).items()}      # split at T2b (Q-188b)
        starts["ny"] = SS.session_spans(d)["ny"][0]
        for c in decl["components"]:
            s = starts[PB.SPACE_SESSION[c["session"]]]
            assert got[c["name"]] == (s + c["first"], s + c["last"])
    byday = {x: {c.name: c.first for c in PB.design_on(decl, space, date.fromisoformat(x)).components}
             for x in ("2021-03-12", "2021-03-16", "2021-04-06")}
    assert [_label(byday[x]["ldn_brk"]) for x in byday] == ["02:00", "03:00", "02:00"]
    assert [_label(byday[x]["asia_brk"]) for x in byday] == ["18:00", "19:00", "19:00"]
    text = PB.render_playbook(carried).text
    assert "on 2021-03-12 (the open at 02:00 CT): 02:00 CT to 03:00 CT" in text
    assert "on 2021-03-16 (the open at 03:00 CT): 03:00 CT to 04:00 CT" in text
    assert "on 2021-03-12 (the open at 18:00 CT): 18:00 CT to 18:55 CT" in text


def test_design_on_equals_the_evaluations_space(carried):
    """N-c3-1: the evaluation's own space (`search_space.from_lever_space`) puts the declaration's slots on the same
    windows on a date of each set of session starts in the search years, and `design_on` builds that day's design."""
    sp = SS.from_lever_space(slots={"asia": 1, "london": 1, "ny_am": 1, "ny_pm": 1})           # split at T2b
    decl = carried.decl
    slot = {"asia_brk": "asia.0", "ldn_brk": "london.0", "am_tix": "ny_am.0", "pm_brk": "ny_pm.0"}
    design = {}
    for c in decl["components"]:
        s = slot[c["name"]]
        design.update({SS.slot_dim(s, "on"): SS.ON, SS.slot_dim(s, "first"): c["first"], SS.slot_dim(s, "last"): c["last"]})
    for _, day in PB._start_dates():
        want = {name: (a, b) for name, _, a, b in sp.windows_on(design, day)}
        d = PB.design_on(decl, carried.space, day)
        assert d.day == day
        assert {slot[c.name]: (c.first, c.last) for c in d.components} == want
        assert {c.session for c in d.components} == {"asia", "london", "ny_am", "ny_pm"}


@pytest.mark.parametrize("key", PB.REQUIRED)
def test_missing_declaration_key_refuses(tmp_path, key):
    _refuses(tmp_path, lambda d: d.pop(key))


@pytest.mark.parametrize("key", PB.COMPONENT_KEYS)
def test_missing_component_key_refuses(tmp_path, key):
    _refuses(tmp_path, lambda d: d["components"][2].pop(key))


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


# the components' indices: 0 asia_brk, 1 ldn_brk, 2 am_tix (RL3), 3 pm_brk
MUTATIONS = {
    "L-undeclared": _set(("components", 3, "latency"), 4),
    "L-not-triggers": lambda d: d["components"][3].update(latency=5),
    "L-of-latency-free": _set(("components", 2, "latency"), 2),
    "coin-trigger": _set(("components", 1, "trigger", "source"), "coin"),
    "p16-no-side-rule": _set(("components", 1, "trigger"), {"source": "p16", "params": {"marks": [600, 630],
                                                                                         "overnight": True}}),
    "p14-k-not-registered": _set(("components", 3, "trigger", "params", "k"), 7),
    "p14-fixed-ct-bounds": _set(("components", 3, "trigger", "params", "first"), 1077),           # C2-3
    "side-rule-free-words": _set(("components", 3, "side_rule"), "toss a fair coin"),
    "side-rule-blank": _set(("components", 3, "side_rule"), ""),
    "rl3-rule-missing-level": _set(("components", 2, "side_rule"), {"hi": "fade"}),
    "offset-off-the-mark-grid": _set(("components", 1, "last"), 61),                              # C2-3
    "offset-beyond-the-session": _set(("components", 1, "last"), 400),
    "offset-negative": _set(("components", 1, "first"), -5),
    "offset-last-before-first": lambda d: d["components"][3].update(first=100, last=50),
    "rl3-window-misses-live": _set(("components", 2, "first"), 35),
    "closed-window-first": _set(("components", 2, "first"), 0),
    "unknown-session": _set(("components", 1, "session"), "sydney"),
    "anchor": _set(("session_anchors", "london"), ["Europe/London", "09:00"]),
    "anchor-ny-pm-not-the-split": _set(("session_anchors", "ny_pm"), ["America/New_York", "09:30"]),  # Q-188b
    "anchor-missing": lambda d: d["session_anchors"].pop("asia"),
    "collision": lambda d: d["components"][3].update(session="ny_am", first=50, last=100),
    "rotation": _set(("rotation", "rule"), "copy_to_all"),
    "hand-built-pools": _set(("rotation", "pools"), {"pm_brk": ["ts_b"]}),                         # L-M2
    "ny-am-crossing-noon": _set(("components", 2, "last"), 200),                                     # Q-188b
    "ny-pm-before-the-split": lambda d: d["components"][3].update(first=-30),
    "void-rule-unknown": lambda d: d["void_rules"].append("my_hunch"),
    "void-rule-dropped": lambda d: d["void_rules"].remove("prior_abbreviated"),
    "void-rule-twice": lambda d: d["void_rules"].append("fomc"),
    "void-rule-research-only": lambda d: d["void_rules"].append("short_bars"),
    "research-filter-dropped": lambda d: d["research_filters"].remove("overnight_missing"),
    "void-date-reason": _set(("void_dates", 0, "reason"), "my_hunch"),
    "void-date-basic-form": _set(("void_dates", 0, "date"), "20210319"),
    "void-date-padded": _set(("void_dates", 0, "date"), " 2021-03-19"),
    "release-date-basic-form": _set(("news_windows", 1, "dates"), ["20210317"]),
    "release-date-short": _set(("news_windows", 1, "dates"), ["2021-3-17"]),
    "release-dates-none": _set(("news_windows", 1, "dates"), []),
    "anchor-date-basic-form": _set(("dates",), ["20210316"]),
    "anchor-dates-none": _set(("dates",), []),
    "news-none-undeclared": _set(("news_windows",), []),
    "news-source-figure": _set(("news_source",), "record v2"),
    "contracts-zero": _set(("components", 2, "contracts"), 0),
    "contracts-500": _set(("components", 3, "contracts"), 500),
    "contracts-over-funded-cap": _set(("components", 3, "contracts"), 21),
    "rl3-pair-over-cap-together": _set(("components", 2, "contracts"), 11),     # 22 together > the funded 20
    "budget-zero": _set(("bankroll", "budget"), 0),
    "margin-negative": _set(("side", "margin"), -0.01),
    "margin-not-a-number": _set(("side", "margin"), "small"),
    "accounts-repeat": lambda d: d["accounts"].append({"id": "ts_a", "role": "evaluation"}),
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
    "registration-in-the-declaration": _set(("registration",), PC.REGISTRATION),                  # C2-5
    "row-in-the-declaration": _set(("row",), "E-9004"),
}


@pytest.mark.parametrize("name", sorted(MUTATIONS))
def test_disagreement_with_the_library_or_the_ledger_refuses(tmp_path, name):
    _refuses(tmp_path, MUTATIONS[name])


def _renamed(old, new):
    """The declaration and its no-harm rows with component `old` renamed `new` everywhere."""
    decl = PC.declaration()
    for c in decl["components"]:
        if c["name"] == old:
            c["name"] = new
    rows = [dict(r, measure=new) if r["measure"] == old else dict(r) for r in PC.NO_HARM_ROWS]
    return decl, rows


@pytest.mark.parametrize("name", ["pm_wins62.5pct", "pm_brk2021", "pm.brk", "pm_brk2", "pm_brk\n", "pm_brk_v12",
                                  "pm_v2_brk"])
def test_identifiers_carry_no_figure(tmp_path, name):
    """m-7, C2-10: renamed everywhere, so only the identifier rule can refuse; a digit only as one trailing `_v<d>`."""
    decl, rows = _renamed("pm_brk", name)
    with pytest.raises(PB.PlaybookRefused, match="identifier"):
        _load(tmp_path, decl, no_harm_rows=rows)


def test_a_trailing_index_is_a_name(tmp_path):
    decl, rows = _renamed("pm_brk", "pm_brk_v2")
    assert _load(tmp_path, decl, no_harm_rows=rows)


@pytest.mark.parametrize("ident", ["X-wins-87", "X-demo7", "X-demo\n"])
def test_design_id_carries_no_figure(tmp_path, ident):
    decl = PC.declaration()
    decl["design_id"] = ident
    with pytest.raises(PB.PlaybookRefused, match="identifier"):
        _load(tmp_path, decl, record_over={"design_id": ident})


@pytest.mark.parametrize("comp,session,first,last", [(3, "ny_pm", 0, 245), (3, "ny_pm", 180, 245),
                                                     (3, "ny_pm", 190, 245), (0, "asia", 0, 415),
                                                     (0, "evening", 0, 55)],
                         ids=["ny-to-its-end", "ny-from-the-last-event", "ny-wholly-past-the-last-event", "asia",
                              "evening-from-the-reopen"])
def test_a_breakout_window_past_its_span_is_clipped(tmp_path, comp, session, first, last):
    """C3-2: a P-14 window the search space allows past 14:00 CT plus L, or from the reopen, loads; its alerts are
    clipped to P-14's span (17:00 to 14:00 CT), as a full-span P-14 and the window's filter give."""
    decl = PC.declaration()
    decl["components"][comp].update(session=session, first=first, last=last)
    c = _load(tmp_path, decl)
    trig = next(x for x in PB.design_on(c.decl, c.space, date(2021, 3, 16)).components
                if x.name == decl["components"][comp]["name"]).trigger
    assert 0 <= trig.first <= trig.last <= T.P14_LAST


def test_ny_is_split_at_noon_new_york(tmp_path, carried):
    """N-c3-2 now the real split (Q-188b): NY PM counts from T2b's noon New York (11:00 CT), its windows read per date;
    a window crossing noon is `ny`, the whole session from 08:30 CT, and as `ny_am` it refuses."""
    assert PB._split() == 1080
    for d in ("2021-03-12", "2021-03-16", "2021-04-06"):
        pm = next(c for c in PB.design_on(carried.decl, carried.space, date.fromisoformat(d)).components
                  if c.name == "pm_brk")
        assert (pm.session, _label(pm.first), _label(pm.last)) == ("ny_pm", "11:00", "14:00")
    decl = PC.declaration()
    decl["components"][3].update(session="ny", first=150, last=330)
    decl["session_anchors"]["ny"] = ["America/New_York", "09:30"]
    c = _load(tmp_path, decl)
    pm = next(x for x in PB.design_on(c.decl, c.space, date(2021, 3, 16)).components if x.name == "pm_brk")
    assert (pm.session, _label(pm.first), _label(pm.last)) == ("ny", "11:00", "14:00")
    decl["components"][3]["session"] = "ny_am"
    decl["session_anchors"].pop("ny")
    with pytest.raises(PB.PlaybookRefused, match="search space refuses"):
        _load(tmp_path / "am", decl)


def test_news_none_declared_with_its_reason_loads(tmp_path):
    decl = PC.declaration()
    decl["news_windows"] = []
    decl["news_none"] = "the record holds no release in these sessions"
    assert "(none: the record holds no release in these sessions)" in PB.render_playbook(_load(tmp_path, decl)).text


def test_coin_refused_as_the_evaluations_device(tmp_path):
    _refuses(tmp_path, _set(("components", 1, "trigger", "source"), "coin"), match="evaluation's device")


@pytest.mark.parametrize("raw", [
    lambda b: b.replace(b'"contracts": 1,', b'"contracts": 1,\n   "contracts": 9,'),
    lambda b: b.replace(b'"rr": 2.25', b'"rr": NaN'),
    lambda b: b.replace(b'"budget": 1700', b'"budget": Infinity'),
    lambda b: b.replace(b'"flatten": 1328', b'"flatten": NaN'),
], ids=["duplicate-key", "nan", "infinity", "nan-where-only-the-parser-refuses"])
def test_declaration_json_strict(tmp_path, raw):
    """m-4: the pinned bytes are the declaration: a duplicate key, NaN or Infinity refuses, even pinned."""
    data = raw(PC.json_bytes(PC.declaration()))
    assert data != PC.json_bytes(PC.declaration())
    with pytest.raises(PB.PlaybookRefused, match="twice|non-finite"):
        PB.load_carried(PC.RECORD_FILE, root=PC.build_root(tmp_path, raw=data))


# ------------------------------------------------------------------------------------------------ the carrying record (C2-5)


@pytest.mark.parametrize("over", [{"registration": "REG-other"}, {"design_id": "X-other"}, {"row": "E-9002"},
                                  {"declaration": "prereg/other.json"}, {"declaration_sha256": "e" * 64},
                                  {"extra": "a key off the list"}, {"heldout_file": "results/other.csv"},
                                  {"heldout_script": "scratch/x.py"}, {"heldout_family": "F-other"}],
                         ids=["registration", "design", "row", "declaration-path", "declaration-sha", "extra-key",
                              "heldout-file", "heldout-script", "heldout-family"])
def test_carrying_record_must_match(tmp_path, over):
    with pytest.raises(PB.PlaybookRefused):
        _load(tmp_path, record_over=over)


def test_carrying_record_unpinned_or_strict(tmp_path):
    with pytest.raises(PB.PlaybookRefused, match="not the file pinned"):
        _load(tmp_path / "a", edit_rows=lambda rows: {**rows, "E-9004": re.sub(
            r"(X-demo_carried\.json` sha256 `)[0-9a-f]+", lambda m: m.group(1) + "c" * 64, rows["E-9004"])})
    rec = PC.json_bytes(PC.record("0" * 64)).replace(b'"row": "E-9004"', b'"row": "E-9004", "row": "E-9002"')
    with pytest.raises(PB.PlaybookRefused, match="twice"):
        PB.load_carried(PC.RECORD_FILE, root=PC.build_root(tmp_path / "b", raw_record=rec))


def test_declaration_carries_no_registration_and_is_pinned_without_one(carried):
    """C2-5: the declaration (and so the result files' binding) holds neither the registration nor the carrying row."""
    decl = carried.decl
    assert "registration" not in decl and "row" not in decl
    assert carried.registration == PC.REGISTRATION and carried.row == "E-9004"


# ------------------------------------------------------------------------------------------------ R-7, C2-7: pins and rows


def test_declaration_edited_after_its_pin_refuses(root):
    p = root / PC.DECL_FILE
    p.write_bytes(p.read_bytes().replace(b'"contracts": 1', b'"contracts": 2'))
    with pytest.raises(PB.PlaybookRefused, match="not the one the carrying record binds"):
        PB.load_carried(PC.RECORD_FILE, root=root)


def test_declaration_pinned_with_crlf_reads_as_lf(root):
    for f in (PC.DECL_FILE, PC.RECORD_FILE):
        p = root / f
        p.write_bytes(p.read_bytes().replace(b"\n", b"\r\n"))
    assert PB.load_carried(PC.RECORD_FILE, root=root).decl_sha


@pytest.mark.parametrize("path,value", [(("side", "no_harm_row"), "E-0"), (("side", "no_harm_row"), "pending"),
                                        (("bankroll", "row"), "E-9999"), (("side", "margin_row"), "E-77")],
                         ids=["no-harm-short", "no-harm-pending", "bankroll-missing", "margin-row-missing"])
def test_a_cited_row_not_in_the_log_refuses(tmp_path, path, value):
    _refuses(tmp_path, _set(path, value))


def test_the_carrying_row_missing_refuses(tmp_path):
    with pytest.raises(PB.PlaybookRefused, match="carrying row"):
        _load(tmp_path, record_over={"row": "E-99999999"})


def _sub(row, old, new):
    return lambda rows: {**rows, row: rows[row].replace(old, new)}


def _reorder(*ids):
    return lambda rows: {k: rows[k] for k in ids}


ROW_EDITS = {
    "token-another-design": _sub("E-9004", f"carried: {PC.DESIGN} @", "carried: X-other @"),            # C2-7
    "token-another-registration": _sub("E-9004", f"-- {PC.REGISTRATION} --", "-- REG-other --"),
    "token-another-hash": lambda rows: {**rows, "E-9004": re.sub(r"(carried: \S+ @ )[0-9a-f]+",
                                                                 lambda m: m.group(1) + "f" * 64, rows["E-9004"])},
    "token-missing": lambda rows: {**rows, "E-9004": re.sub(r"carried: \S+ @ \S+ -- \S+ -- \S+;", "carried.",
                                                            rows["E-9004"])},
    "token-twice": lambda rows: {**rows, "E-9004": rows["E-9004"] + " " + re.search(
        r"carried: \S+ @ \S+ -- REG-demo -- [0-9a-f]+", rows["E-9004"]).group(0) + "."},
    "token-without-the-heldout-result": lambda rows: {**rows, "E-9004": re.sub(r"(-- REG-demo) -- [0-9a-f]+", r"\1",
                                                                               rows["E-9004"])},          # C3-7
    "token-another-heldout-hash": lambda rows: {**rows, "E-9004": re.sub(r"(-- REG-demo -- )[0-9a-f]+",
                                                                         lambda m: m.group(1) + "a" * 64,
                                                                         rows["E-9004"])},
    "withdrawn": _sub("E-9004", "(synthetic)", "(synthetic; withdrawn after the held-out test failed)"),
    "reverted": _sub("E-9004", "(synthetic)", "(synthetic; reverted under E-2)"),
    "would-be": _sub("E-9004", "(synthetic)", "(synthetic; would be the record had the test passed)"),
    "not-run": _sub("E-9004", "(synthetic)", "(synthetic; the joint held-out test was not run)"),
    "not-yet-carried": _sub("E-9004", "(synthetic)**", "(synthetic): not yet carried**"),
    "conditional": _sub("E-9004", "(synthetic)**", "(synthetic): to be carried only if the held-out test passes**"),
    "a-draft": _sub("E-9004", "(synthetic)", "(DRAFT for red-team review)"),
    "pending": _sub("E-9004", "(synthetic)", "(pending the joint test)"),
    "no-harm-names-another-design": _sub("E-9002", PC.DESIGN, "X-demo70"),
    "expected-unpinned": lambda rows: {**rows, "E-9004": re.sub(r"; its expected journey `results/journey_x\.csv` "
                                                                r"sha256 `[0-9a-f]+`", "", rows["E-9004"])},
    "expected-manifest-unpinned": lambda rows: {**rows, "E-9004": re.sub(
        r"; its manifest `results/journey_x\.csv\.manifest\.json` sha256 `[0-9a-f]+`", "", rows["E-9004"])},
    "no-harm-unpinned": lambda rows: {**rows, "E-9002": "**no pin here**"},
    "no-harm-manifest-unpinned": lambda rows: {**rows, "E-9002": rows["E-9002"].split("; its manifest")[0]},
    "heldout-unpinned": lambda rows: {**rows, "E-9004": rows["E-9004"].split("; the joint held-out")[0]},
    "heldout-manifest-unpinned": lambda rows: {**rows, "E-9004": rows["E-9004"].rsplit("; its manifest", 1)[0]},
    "floor-before-the-declaration": lambda rows: {k: v for k, v in rows.items() if k != "E-9001"},
    "declaration-pinned-after-floor": _reorder("E-9000", "E-9002", "E-9001", "E-9004"),
    "floor-after-the-carrying-row": _reorder("E-9000", "E-9001", "E-9004", "E-9002"),                    # C2-11 Y1
    "margin-row-after-the-pin": _reorder("E-9001", "E-9000", "E-9002", "E-9004"),                        # C3-5
    "a-second-margin-row": lambda rows: {"E-8998": "**Another design's no-harm margin `0.05`.**", **rows},
    "a-path-pinned-twice": lambda rows: {**rows, "E-9004": rows["E-9004"].replace(
        "(synthetic)**", "(synthetic)** the reviewed record `" + PC.RECORD_FILE + "` sha256 `" + "b" * 64 + "`, revised"
                         " to")},
    "margin-row-silent": _sub("E-9000", ", and the no-harm margin `0.05`", ""),                         # C2-1
    "margin-row-twice": _sub("E-9000", "`0.05`.", "`0.05`, then no-harm margin `0.1`."),
    "margin-row-not-bare": _sub("E-9000", "`0.05`", "`0.05 or so`"),
}


@pytest.mark.parametrize("edit", sorted(ROW_EDITS))
def test_rows_must_order_name_carry_and_pin(tmp_path, edit):
    with pytest.raises(PB.PlaybookRefused):
        _load(tmp_path, edit_rows=ROW_EDITS[edit])


@pytest.mark.parametrize("edit,match", [
    ("floor-after-the-carrying-row", "before its no-harm row"), ("a-path-pinned-twice", "twice"),
    ("not-yet-carried", "negated or conditional"), ("conditional", "negated or conditional"),
    ("token-twice", "one token"), ("margin-row-twice", "exactly once"), ("withdrawn", "negated or conditional"),
    ("reverted", "negated or conditional"), ("would-be", "negated or conditional"), ("not-run", "negated or conditional"),
    ("margin-row-after-the-pin", "comes before the declaration's pin"),
    ("a-second-margin-row", "exactly one row of the log states the no-harm margin"),
    ("token-without-the-heldout-result", "one token")])
def test_row_refusals_say_why(tmp_path, edit, match):
    """The refusals that another guard could mask, each matched to its own message."""
    with pytest.raises(PB.PlaybookRefused, match=match):
        _load(tmp_path, edit_rows=ROW_EDITS[edit])


def test_the_margin_is_the_one_its_row_pins(tmp_path):
    """C2-1 (the note's P1): a floor computed, recorded and declared at a looser margin than the 3.9 row's refuses."""
    decl = PC.declaration()
    decl["side"]["margin"] = 0.5
    rows = [dict(r) for r in PC.NO_HARM_ROWS]
    for r in rows:
        if r["stat"] == "margin":
            r["value"] = "0.5"
        if r["measure"] == "am_tix" and r["stat"] == "trigger_composite":
            r["value"] = "0.0"
    with pytest.raises(PB.PlaybookRefused, match="not the one its margin row pins"):
        _load(tmp_path, decl, no_harm_rows=rows, no_harm_over={"parameters_update": {"margin": 0.5}})
    assert _load(tmp_path / "ok", decl, no_harm_rows=rows, no_harm_over={"parameters_update": {"margin": 0.5}},
                 margin="0.5")


@pytest.mark.parametrize("verdict", ["rejected", "", "accepted "])
def test_the_heldout_result_must_accept_the_design(tmp_path, verdict):
    """C3-7: the joint held-out test's file, pinned in the carrying row and accepted as a result file, records this
    design as accepted."""
    rows = [dict(PC.HELDOUT_ROWS[0], value=verdict)]
    with pytest.raises(PB.PlaybookRefused, match="held-out test as accepted|bare|blank"):
        _load(tmp_path, heldout_rows=rows)
    with pytest.raises(PB.PlaybookRefused, match="held-out test as accepted"):
        _load(tmp_path / "other", heldout_rows=[dict(PC.HELDOUT_ROWS[0], measure="X-other")])


@pytest.mark.parametrize("over", [dict(exploratory=True), dict(parameters_update={"declaration_sha256": "e" * 64}),
                                  dict(script="scratch/x.py"), dict(prereg_id=PC.FAMILY), dict(git_dirty=True)],
                         ids=["exploratory", "another-declaration", "script", "family", "dirty"])
def test_the_heldout_result_is_a_clean_bound_result(tmp_path, over):
    with pytest.raises(PB.PlaybookRefused):
        _load(tmp_path, heldout_over=over)


def test_an_unrelated_row_pinning_twice_does_not_block(tmp_path):
    rows_edit = lambda rows: {"E-8999": "`prereg/other.json` sha256 `" + "c" * 64 + "` then `prereg/other.json` "  # noqa
                              "sha256 `" + "d" * 64 + "`", **rows}
    assert _load(tmp_path, edit_rows=rows_edit).decl_sha


def test_a_repeated_row_in_the_log_refuses(root):
    log = root / "DECISIONS.md"
    log.write_bytes(log.read_bytes() + b"| E-9002 | 2021-01-02 | again | synthetic |\n")
    with pytest.raises(PB.PlaybookRefused, match="twice"):
        PB.load_carried(PC.RECORD_FILE, root=root)


def test_a_carried_design_is_made_only_by_the_loader(carried):
    with pytest.raises(PB.PlaybookRefused):
        PB.Carried(carried.record_file, carried.record_sha, carried.registration, carried.row, carried.decl_file,
                   carried.decl_sha, carried.decl_bytes, carried.rows, carried.space, carried.expected,
                   carried.no_harm, carried.heldout)
    for kw in (dict(decl_bytes=carried.decl_bytes + b" "), dict(expected=carried.no_harm),
               dict(registration="REG-other"), dict(heldout=carried.expected)):
        with pytest.raises(PB.PlaybookRefused):
            dataclasses.replace(carried, **kw)
    with pytest.raises(PB.PlaybookRefused):
        PB.render_playbook(PC.declaration())


def test_playbook_declarations_are_in_the_pin_test():
    """m-9: tests/test_declarations_fixed.py holds a playbook declaration's pin as it holds a family's."""
    text = (ROOT / "tests" / "test_declarations_fixed.py").read_text(encoding="utf-8")
    assert "_playbook" in text and "json" in text


# ------------------------------------------------------------------------------------------------ C2-2: the pin before the run, in git


@pytest.mark.parametrize("floor,journey,ok", [("pin", "pin", True), ("before", "pin", False), ("side", "pin", False),
                                               ("pin", "before", False), ("pin", "side", False)],
                         ids=["after-the-pin", "floor-before", "floor-on-an-unmerged-branch", "journey-before",
                              "journey-on-an-unmerged-branch"])
def test_the_runs_follow_the_pin_in_git(tmp_path, monkeypatch, floor, journey, ok):
    """C2-2, C3-4, N-c3-3: a real history -- the floor's and the journey's run commits descend from the commit that
    first pinned the declaration and lie on HEAD's line; a run before the pin, or on a branch never merged, refuses."""
    monkeypatch.setattr(PB, "_run_after_pin", REAL_RUN_AFTER_PIN)
    root = PC.git_root(tmp_path, floor=floor, journey=journey)
    if ok:
        assert PB.load_carried(PC.RECORD_FILE, root=root)
    else:
        with pytest.raises(PB.PlaybookRefused, match="does not descend"):
            PB.load_carried(PC.RECORD_FILE, root=root)


def test_the_pin_order_needs_a_repository(tmp_path, monkeypatch):
    monkeypatch.setattr(PB, "_run_after_pin", REAL_RUN_AFTER_PIN)
    with pytest.raises(PB.PlaybookRefused, match="does not descend"):
        PB.load_carried(PC.RECORD_FILE, root=PC.build_root(tmp_path))          # no git: the order is unknown


def test_the_pin_order_is_asked_of_both_runs_with_the_declarations_pin(carried):
    assert PINS == [(f"`{PC.DECL_FILE}` sha256 `{carried.decl_sha}`", PC.COMMIT)] * 2


# ------------------------------------------------------------------------------------------------ B-1, B-3: the bindings


def _flip(d):
    d["components"][3]["side_rule"] = "with_breakout"


def _other_stop(d):
    d["components"][1]["stop_ticks"] = 20


def _other_rotation(d):
    d["rotation"] = {"rule": "longest_waiting"}


@pytest.mark.parametrize("change", [_flip, _other_stop, _other_rotation], ids=["side-rule-flipped", "stop", "rotation"])
def test_results_bound_to_another_declaration_refuse(tmp_path, change):
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
    ("pm_brk", "side_rule", "with_breakout"), ("am_tix", "side_rule", "hi=break;lo=fade"),
    ("am_tix", "margin", "0.1"), ("am_tix", "trigger_composite", "0.23"), ("pm_brk", "coin_composite", "0.46"),
    ("ldn_brk", "trigger_composite", "pass"), ("ldn_brk", "coin_composite", "nan"),
    ("asia_brk", "trigger_composite", "0.22 pts"),
], ids=["p14-rule", "rl3-rule", "margin", "rl3-failed", "p14-failed", "not-a-number", "not-finite", "a-unit"])
def test_no_harm_row_mismatch_or_failure_refuses(tmp_path, comp, stat, value):
    with pytest.raises(PB.PlaybookRefused, match="no-harm floor|not a bare number|not finite"):
        _load(tmp_path, no_harm_rows=_nh_rows(comp, stat, value))


@pytest.mark.parametrize("stat", PB.NO_HARM_STATS)
def test_no_harm_row_absent_refuses(tmp_path, stat):
    rows = [r for r in PC.NO_HARM_ROWS if not (r["measure"] == "ldn_brk" and r["stat"] == stat)]
    with pytest.raises(PB.PlaybookRefused, match="absent"):
        _load(tmp_path, no_harm_rows=rows)


def test_no_harm_pass_is_recomputed_at_the_margin(tmp_path):
    with pytest.raises(PB.PlaybookRefused, match="failed"):
        _load(tmp_path, no_harm_rows=_nh_rows("am_tix", "trigger_composite", "0.2399"))
    assert _load(tmp_path / "ok", no_harm_rows=_nh_rows("am_tix", "trigger_composite", "0.25"))


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
    "declaration-sha": dict(parameters_update={"declaration_sha256": "e" * 64}),
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
    mp = Path(str(root / PC.EXPECTED_FILE) + PC.MANIFEST)
    m = json.loads(mp.read_bytes())
    m["description"] = "edited after the pin"
    mp.write_bytes(json.dumps(m, indent=2, sort_keys=True).encode())
    with pytest.raises(PB.PlaybookRefused, match="manifest is not the one pinned"):
        PB.load_carried(PC.RECORD_FILE, root=root)


@pytest.mark.parametrize("row,name", [("E-9004", "journey_x"), ("E-9002", "noharm_x"), ("E-9004", "heldout_x")])
def test_the_csv_pin_in_the_row_must_be_the_manifests(tmp_path, row, name):
    edit = lambda rows: {**rows, row: re.sub("(" + name + r"\.csv` sha256 `)[0-9a-f]+", lambda m: m.group(1) + "a" * 64,  # noqa
                                            rows[row])}
    with pytest.raises(PB.PlaybookRefused, match="do not agree on its hash|one token"):   # the held-out pin is the token's
        _load(tmp_path, edit_rows=edit)


def test_result_read_from_one_resolved_path(carried, root):
    assert sorted(CALLS) == sorted({(root / f).resolve() for f in (PC.EXPECTED_FILE, PC.NO_HARM_FILE,
                                                                       PC.HELDOUT_FILE)})


def test_tampered_or_missing_result_refuses(root):
    p = root / PC.EXPECTED_FILE
    p.write_bytes(p.read_bytes().replace(b"37.5", b"12.5"))
    with pytest.raises(PB.PlaybookRefused):
        PB.load_carried(PC.RECORD_FILE, root=root)
    p.unlink()
    with pytest.raises(PB.PlaybookRefused):
        PB.load_carried(PC.RECORD_FILE, root=root)


@pytest.mark.parametrize("rel", ["results/s1_range.csv", "results/q121_vol_descriptive_a1.csv",
                                 "results/scratch/x.csv", "elsewhere/journey_x.csv", "results/../journey_x.csv",
                                 "results/journey_x.txt"])
def test_licensed_ignored_or_misplaced_result_refuses(tmp_path, rel):
    decl = PC.declaration()
    decl["expected"]["file"] = rel
    with pytest.raises(PB.PlaybookRefused):
        _load(tmp_path, decl)


@pytest.mark.parametrize("measure,value", [("mean_entry_price", "18234.75"), ("mean_entry_price", "18234.37"),
                                           ("S3b", "6250")])
def test_a_band_figure_in_value_needs_a_pinned_measure(tmp_path, measure, value):
    """C3-8 (the note's probe): a price in `value` refuses, on the grid or off it, unless the measure is a pinned dollar
    or count measure (S1 holds 6250 in the fixture)."""
    rows = [dict(r) for r in PC.EXPECTED_ROWS]
    rows[4].update(measure=measure, value=value)
    with pytest.raises(PB.PlaybookRefused, match="value column"):
        _load(tmp_path, expected_rows=rows)


def test_an_exponent_is_a_bare_number(tmp_path):
    """C3-8: a small probability as Python writes it (`1e-05`) is printed."""
    rows = [dict(r) for r in PC.EXPECTED_ROWS]
    rows[1]["value"] = "1e-05"
    assert "chance of running out at the budget: 1e-05" in PB.render_playbook(_load(tmp_path, expected_rows=rows)).text


def test_figures_and_counts_in_their_columns_are_printed(carried):
    """C2-8 (the note's P5, P5b): a whole-dollar figure and a count of the price band are figures, not prices."""
    text = PB.render_playbook(carried).text
    assert "bankroll needed, unlucky tenth: 6250" in text and "bankroll needed, unlucky tenth: 6611.5" in text


@pytest.mark.parametrize("where,cell", [("measure", "level_18234.37"), ("stat", "18234.75 pts"), ("section", "18,234"),
                                        ("block", "x 7000"), ("measure", "p_under_bankroll_6250")])
def test_a_price_band_number_in_a_label_column_refuses(tmp_path, where, cell):
    """C2-8 (the note's P4, P4b): on the grid or off it, with or without a unit, in any label column."""
    rows = [dict(r) for r in PC.EXPECTED_ROWS]
    rows[4][where] = cell
    with pytest.raises(PB.PlaybookRefused, match="label column"):
        _load(tmp_path, expected_rows=rows)


def test_a_column_off_the_pinned_list_refuses(tmp_path):
    rows = [dict(r, close="1") for r in PC.EXPECTED_ROWS]
    with pytest.raises(PB.PlaybookRefused, match="pinned list"):
        _load(tmp_path, expected_rows=rows, expected_columns=PC.COLUMNS + ("close",))


@pytest.mark.parametrize("value", ["6250 pts", "$6250", "6,250", "6250.", " 6250", "inf", "1e5x"])
def test_a_printed_figure_is_a_bare_number(tmp_path, value):
    rows = [dict(r) for r in PC.EXPECTED_ROWS]
    rows[2]["value"] = value
    with pytest.raises(PB.PlaybookRefused, match="bare number|not finite"):
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
    for name, (comp, day, at, hist) in ALERTS.items():
        r = _alert(carried, comp, day, at, hist=_void_probe_history() if hist else None)
        assert check_traced(r, {"design": carried.decl, "day": day, "library": _library()}) >= 1
        t = r.text
        for price in ("18000", "18100", "17900", "17990", "18110", "18120", "18050", "18234"):
            assert price not in t, (name, price)
        assert not re.search(r"\d{3,}\.\d", t)
        assert "bar ending" not in t
        for hook in ("http", "webhook", "json", "{", "api"):
            assert hook not in t.lower()


def test_resting_orders_state_the_void_at_live_rule(carried):
    """C2-4: every resting order (P-14's limit, RL3's limit and stop) carries the walker's void-at-live rule; a market
    order does not; the red team's void probe renders the same alert (the rule is the user's to apply at live)."""
    rule = ("compare the market with your order: if a BUY limit is at or above the market, a SELL limit at or below "
            "it, a BUY stop at or below it or a SELL stop at or above it, ")
    pm = _alert(carried, "pm_brk", "2021-03-16", 1101).text
    assert "Each time you place it (the bar stamped 11:24 CT), " + rule + "do not place it: no trade today." in pm
    assert _alert(carried, "pm_brk", "2021-03-16", 1101, hist=_void_probe_history()).text == pm
    pair = _alert(carried, "am_tix", "2021-03-16", 930).text                                   # C3-3: per ticket
    assert pair.count(rule + "do not place this ticket: the other ticket stands or falls by its own check.") == 2
    assert "no trade today" not in pair
    assert rule not in _alert(carried, "ldn_brk", "2021-03-16", _ldn("2021-03-16")).text


def test_levels_are_defined_by_their_bars(carried):
    """C2-9: the alert names the bars each level is made from, and warns that the platform's own level may differ."""
    t = _alert(carried, "am_tix", "2021-03-16", 930).text
    assert "the high of the previous day's bars stamped 08:30 CT to 14:59 CT" in t
    assert "today's bars" not in PB.render_playbook(carried).text                                # N-c3-4
    assert "the low of the previous day's bars stamped 08:30 CT to 14:59 CT" in t
    assert "(the close of the bar stamped 08:29 CT)" in t and PB.PLATFORM_LEVEL in t


def test_the_offer_is_recomputed_from_the_bars_closed_at_the_alert(carried):
    """B-2, the feature-rules shift-invariance test."""
    for comp, day, at, _ in ALERTS.values():
        i = PC.day_index(day)
        want = _alert(carried, comp, day, at).text
        for seed in (11, 12, 13):
            assert _alert(carried, comp, day, at, hist=PC.scrambled(H, i, at, seed)).text == want


def test_the_cut_keeps_only_the_bars_closed_at_the_alert():
    """feature-rules section 1, C2-11 (Y3): the days up to `i` (the arrays' rows too), and of day `i` the columns up
    to `at`; every later bar NaN."""
    import numpy as np

    for i, at in ((3, 1101), (3, 610), (5, 930)):
        cut = PB.cut_history(H, i, at)
        assert cut.days == H.days[: i + 1] and len(cut) == i + 1
        for a, b in ((cut.o, H.o), (cut.h, H.h), (cut.l, H.l), (cut.c, H.c)):
            assert a.shape == (i + 1, b.shape[1])
            assert np.array_equal(a[:i], b[:i], equal_nan=True)
            assert np.array_equal(a[i, : at + 1], b[i, : at + 1], equal_nan=True)
            assert np.isnan(a[i, at + 1:]).all()
    assert not np.isnan(H.c[3, 1102:]).all()


def test_the_side_comes_from_the_bars(carried):
    import numpy as np

    i = PC.day_index("2021-03-16")
    arrs = [np.array(x, copy=True) for x in (H.o, H.h, H.l, H.c)]
    arrs[1][i, 1101] = PC.HIGH
    arrs[2][i, 1101] = arrs[3][i, 1101] = PC.LOW - 10.0
    down = T.History(H.days, H.contract, *arrs)
    assert "Side BUY (long): the breakout was a close below" in _alert(carried, "pm_brk", "2021-03-16", 1101,
                                                                       hist=down).text
    arrs = [np.array(x, copy=True) for x in (H.o, H.h, H.l, H.c)]
    arrs[3][i, 930] = PC.HIGH + 50.0
    t = _alert(carried, "am_tix", "2021-03-16", 930, hist=T.History(H.days, H.contract, *arrs)).text
    assert "Ticket 1 of 2: Side BUY (long)" in t and "a support" in t


def test_no_offer_object_and_no_trade_is_accepted(carried):
    off = T.Offer("p14", 3, 1101, 0, 1101, 1104, T.LIMIT, 18110.0, expires=1133, tag="brk30-")
    for bad in (off, PC.scheduled(), R.RoutedTrade(PC.scheduled(), "ts_b")):
        with pytest.raises(PB.AlertRefused) as e:
            PB.render_offer(carried, "pm_brk", bad, PC.day_index("2021-03-16"), 1101, PC.sources(), PC.router(),
                            PC.ACCOUNTS)
        assert e.value.reason == "mismatch"


@pytest.mark.parametrize("comp,at", [("pm_brk", 1102), ("pm_brk", 1100), ("ldn_brk", 611), ("am_tix", 931),
                                     ("ldn_brk", 550)])
def test_no_offer_at_that_moment_refuses(carried, comp, at):
    """The last case: 02:10 CT is London's breakout on a standard-time date, not on 2021-03-16 (its open at 03:00)."""
    with pytest.raises(PB.AlertRefused) as e:
        _alert(carried, comp, "2021-03-16", at)
    assert e.value.reason == "no_offer"


@pytest.mark.parametrize("label", ["coin", "trigger"])
def test_a_scheduled_trade_gets_the_not_offered_notice(carried, label):
    tr = PC.scheduled(side_source=label)
    for x in (tr, R.RoutedTrade(tr, "ts_b")):
        r = PB.render_trade(carried, x)
        assert r.text.startswith("NOT OFFERED today") and "evaluation's coin" in r.text
    with pytest.raises(PB.AlertRefused):
        PB.render_trade(carried, PC.scheduled(source="rl3"))


def test_rl3_pair_is_one_alert_in_one_account_placed_by_hand(carried, tmp_path):
    """B-4, C2-6: the pair in one alert, one account, rested as plain orders with Auto-OCO brackets, the other
    cancelled by hand, the double fill flattened; its size counted together."""
    t = _alert(carried, "am_tix", "2021-03-16", 930).text
    assert PB.PAIR_WORDS in t and "OCO order type" not in t
    assert "The moment one fills, cancel the other by hand" in t
    assert "close every position and cancel every working order in this account, brackets included, at once" in t
    assert "set the Auto-OCO stop and target to the ticks given below for each ticket" in t
    assert "article 14434175 (\"TopstepX\") for the Auto-OCO brackets and the DOM's OCO switch" in t
    assert "Never split them across accounts" in t and "these tickets count as one order" in t
    assert t.count("account ts_") == 1 and "Ticket 1 of 2" in t and "Ticket 2 of 2" in t
    assert "2 contracts on each ticket, 4 for the tickets together" in t
    decl = PC.declaration()
    decl["components"][2]["side_rule"] = {"hi": "break", "lo": "break"}
    decl["components"][2]["contracts"] = 10      # every account may be dealt the tickets: the funded cap binds
    c = _load(tmp_path, decl, no_harm_rows=_nh_rows("am_tix", "side_rule", "hi=break;lo=break"))
    t = _alert(c, "am_tix", "2021-03-16", 930).text
    assert "Ticket 1 of 2: Side BUY (long)" in t and "Ticket 2 of 2: Side SELL (short)" in t
    assert "STOP 1 tick above the level" in t and "STOP 1 tick below the level" in t
    assert "10 contracts on each ticket, 20 for the tickets together (the firm's verified limit for this account: 50)" in t


def test_account_is_the_routers_pick_among_the_accounts_alive(carried, tmp_path):
    """m-5, N-c2-1, Q-188b: under by_component the router's own pools, dealt over the accounts alive today in opening
    order and the components in window order (asia_brk, ldn_brk, am_tix, pm_brk); under longest_waiting the firm's
    longest-waiting account; a router under another rotation, none, or accounts not the declaration's refuse."""
    assert "account ts_c:" in _alert(carried, "am_tix", "2021-03-16", 930).text       # the third of three accounts
    assert "account ts_a:" in _alert(carried, "pm_brk", "2021-03-16", 1101).text      # four components, three accounts
    assert "account ts_a:" in _alert(carried, "am_tix", "2021-03-16", 930, accounts=("ts_a", "ts_b")).text
    decl = PC.declaration()
    decl["rotation"] = {"rule": "longest_waiting"}
    c = _load(tmp_path, decl)
    r = PC.router(decl, ts_a=5000, ts_b=4000)
    assert "account ts_c:" in _alert(c, "pm_brk", "2021-03-16", 1101, router=r).text
    assert "account ts_b:" in _alert(c, "pm_brk", "2021-03-16", 1101, router=r, accounts=("ts_a", "ts_b")).text
    for bad in (("ts_a", "ts_z"), (), "ts_a", ("ts_a", "ts_a")):
        with pytest.raises(PB.AlertRefused):
            _alert(c, "pm_brk", "2021-03-16", 1101, accounts=bad)
    other, _ = _renamed("pm_brk", "pm_other")                         # by_component over another window order
    for bad in (PC.router(decl), PC.router(other), None):
        with pytest.raises(PB.AlertRefused, match="router"):
            PB.render_offer(carried, "pm_brk", H, PC.day_index("2021-03-16"), 1101, PC.sources(), bad, PC.ACCOUNTS)


@pytest.mark.parametrize("rule", ["longest_waiting", "round_robin", "by_component"])
def test_peek_writes_no_state_and_equals_routes_pick(rule):
    """C2-11 (Y6): `Router.peek` leaves the router's state and book unchanged, under each rotation, and names the
    account `route` then gives the trade."""
    from extended import components as C

    decl = PC.declaration()
    decl["rotation"] = {"rule": rule}
    r = PC.router(decl)
    first = C.DaySchedule("topstep", 98, "2021-03-15", trades=[])
    r.route([first], {"topstep": ("ts_c",)}, date="2021-03-15")        # ts_c opened a day before the others
    r.last_busy.update({("topstep", "ts_a"): 5000, ("topstep", "ts_b"): 100})
    r.last_account["topstep"] = "ts_a"

    def state():
        return (dict(r.last_busy), dict(r.last_account), list(r.book.positions), dict(r.opened), list(r.routed),
                r.day_no)

    before = state()
    picks = [r.peek("topstep", "pm_brk", PC.ACCOUNTS) for _ in range(3)]
    assert state() == before
    assert len(set(picks)) == 1
    tr = PC.scheduled(session=99, date="2021-03-16")
    day = C.DaySchedule("topstep", 99, "2021-03-16", trades=[tr])
    assert r.route([day], {"topstep": PC.ACCOUNTS}, date="2021-03-16")[0].account == picks[0]


@pytest.mark.parametrize("day", ["2024-05-01", "2026-08-03"], ids=["held-out", "confirmation-window"])
def test_a_day_after_the_search_years_refuses(carried, day):
    hist = T.History((day,), ("NQM4",), H.o[3:4], H.h[3:4], H.l[3:4], H.c[3:4])
    with pytest.raises(PB.AlertRefused) as e:
        PB.render_offer(carried, "pm_brk", hist, 0, 1101, PC.sources(), PC.router(), PC.ACCOUNTS)
    assert e.value.reason == "mismatch"


@pytest.mark.parametrize("day", ["20210316", "2021-3-16"])
def test_a_history_day_not_strict_iso_refuses(carried, day):
    days = list(H.days)
    days[3] = day
    hist = T.History(tuple(days), H.contract, H.o, H.h, H.l, H.c)
    with pytest.raises(PB.AlertRefused):
        PB.render_offer(carried, "pm_brk", hist, 3, 1101, PC.sources(), PC.router(), PC.ACCOUNTS)


def test_the_caller_cannot_supply_the_day(carried):
    with pytest.raises(PB.AlertRefused):
        PB.render_offer(carried, "pm_brk", H, 3, 1101, T.DayContext(3, "2021-03-16"), PC.router(), PC.ACCOUNTS)


CLOSURE = {"2021-04-02": {"kind": "holiday", "close_ct": ""}}
KNOWN_AT_ALERT = [
    ("fomc", "pm_brk", "2021-03-16", 1101, dict(fomc=("2021-03-16",)), "fomc"),
    ("scheduled-close", "pm_brk", "2021-03-16", 1101,
     dict(calendar={"2021-03-16": {"kind": "early_close", "close_ct": "12:00"}}), "calendar"),
    ("declared-void-date", "pm_brk", "2021-03-19", 1101, {}, "declared_void"),
    ("prior-void-first-day", "am_tix", "2021-03-11", 930, {}, "prior_void"),
    ("prior-void-roll", "am_tix", "2021-03-16", 930, dict(rolls=("2021-03-16",)), "prior_void"),
    ("prior-void-after-scheduled-closure", "am_tix", "2021-04-05", 930, dict(calendar=CLOSURE), "prior_void"),
    ("prior-void-after-scheduled-close", "am_tix", "2021-03-17", 930,
     dict(calendar={"2021-03-16": {"kind": "early_close", "close_ct": "12:00"}}), "prior_void"),
    ("prior-void-after-a-scheduled-close-the-store-lacks", "am_tix", "2021-04-05", 930,                # C3-1
     dict(calendar={"2021-04-02": {"kind": "early_close", "close_ct": "12:00"}}), "prior_void"),
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
    note = _alert(carried, "am_tix", "2021-03-16", 930, hist=PC.history(no_0829=("2021-03-16",)))
    assert PB.REASON_WORDS["no_ref_bar"] in note.text


RESEARCH_ONLY = [
    ("short-last-bar", "ldn_brk", "2021-03-16", 610, dict(last_bar={"2021-03-16": "14:00"})),
    ("early-end", "pm_brk", "2021-03-16", 1101, dict(early_end=("2021-03-16",))),
    ("data-defect", "pm_brk", "2021-03-16", 1101,
     dict(calendar={"2021-03-16": {"kind": "data_defect_candidate", "close_ct": ""}})),
    ("h2-void", "ldn_brk", "2021-03-16", 610, dict(flags={"2021-03-16": {"verdict": "VOID", "void": "synthetic"}})),
    ("h2-missing", "ldn_brk", "2021-03-16", 610, dict(flags={"2021-03-16": {"missing_after_reopen": "999"}})),
]


@pytest.mark.parametrize("case,comp,day,at,src", RESEARCH_ONLY, ids=[k[0] for k in RESEARCH_ONLY])
def test_research_filters_never_decide_an_alert(carried, case, comp, day, at, src):
    """B-5 (the note's P10), N-c2-2: what is known only after the alert, or is a data defect, never voids it."""
    want = _alert(carried, comp, day, at).text
    assert want.startswith("TRADE ALERT")
    assert _alert(carried, comp, day, at, src=PC.sources(**src)).text == want


@pytest.mark.parametrize("src", [dict(early_end=("2021-03-15",)), dict(last_bar={"2021-03-15": "14:00"}),
                                 dict(calendar={"2021-03-15": {"kind": "data_defect_candidate", "close_ct": ""}})],
                         ids=["early-end", "short-last-bar", "data-defect"])
def test_a_data_void_previous_day_refuses(carried, src):
    """The lead's ruling on C3-1 (interpretation 1): a prior-level alert whose bars' previous day is itself data-void
    refuses -- its levels would come from a defective day, which the evaluation voids; one reading no previous day
    stands."""
    with pytest.raises(PB.AlertRefused, match="data-void") as e:
        _alert(carried, "am_tix", "2021-03-16", 930, src=PC.sources(**src))
    assert e.value.reason == "mismatch"
    assert _alert(carried, "pm_brk", "2021-03-16", 1101, src=PC.sources(**src)).text.startswith("TRADE ALERT")


@pytest.mark.parametrize("comp,day,at", [("am_tix", "2021-04-05", 930)])
def test_a_store_without_the_calendars_previous_session_refuses(carried, comp, day, at, tmp_path):
    """C3-1 (the lead's ruling, withdrawing N-c2-2): the calendar's previous session of 2021-04-05 is 2021-04-02; the
    store's previous day is 2021-03-19, so a component reading the previous day refuses as a data mismatch -- never a
    level, role or side from another day; one reading no previous day is offered."""
    with pytest.raises(PB.AlertRefused, match="do not hold the previous session") as e:
        _alert(carried, comp, day, at)
    assert e.value.reason == "mismatch"
    decl = PC.declaration()
    decl["components"][2]["trigger"]["params"]["kind"] = "on"
    c = _load(tmp_path, decl, no_harm_rows=_nh_rows("am_tix", "side_rule", "hi=fade;lo=break"))
    assert _alert(c, comp, day, at).text.startswith("TRADE ALERT")


def test_prior_void_reaches_pdc_too(tmp_path):
    """m-9's X4: a `pdc` component (the previous day's close) is void on a roll day as `pd` is."""
    decl = PC.declaration()
    decl["components"][2]["trigger"]["params"]["kind"] = "pdc"
    decl["components"][2]["side_rule"] = {"lvl": "fade"}
    c = _load(tmp_path, decl, no_harm_rows=_nh_rows("am_tix", "side_rule", "lvl=fade"))
    t = _alert(c, "am_tix", "2021-03-16", 930).text
    assert t.startswith("TRADE ALERT") and "the close of the previous day's bar stamped 14:59 CT" in t
    note = _alert(c, "am_tix", "2021-03-16", 930, src=PC.sources(rolls=("2021-03-16",)))
    assert PB.REASON_WORDS["prior_void"] in note.text


def test_news_window_from_the_declared_record(carried):
    import numpy as np

    i = PC.day_index("2021-03-17")
    arrs = [np.array(x, copy=True) for x in (H.o, H.h, H.l, H.c)]
    arrs[1][i, 1138] = arrs[3][i, 1138] = PC.HIGH + 30.0
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
    t = _alert(_load(tmp_path, decl), "am_tix", "2021-03-16", 930).text
    assert "Working on the bars stamped 09:00 CT through 09:28 CT" in t
    assert "(it ends at 09:29 CT), when a news window starts (a synthetic morning release)" in t
    assert "Working on the bars stamped 09:35 CT through 09:59 CT" in t
    assert t.count("Each time you place it (again, the bar stamped 09:35 CT)") == 2              # C3-3: re-placed


def test_not_offered_reasons_are_a_closed_vocabulary(carried):
    with pytest.raises(PB.AlertRefused):
        PB._notice(carried, "pm_brk", 1104, "price 18234.75")
    r = PB._notice(carried, "pm_brk", 1104, "position")
    assert check_traced(r, {"design": carried.decl, "offer": {"live": 1104}}) == 2
    assert "a position is already open" in r.text


def test_brief_command_forbids_licensed_quotes_and_automation():
    text = (ROOT / ".claude" / "commands" / "brief.md").read_text(encoding="utf-8")
    assert "Never quote anything from a licensed-price derivative" in text and "git-ignored" in text
    assert "never suggest automating orders" in text and "never a command that writes a file" in text
