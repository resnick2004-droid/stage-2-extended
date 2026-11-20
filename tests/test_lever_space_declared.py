"""The lever table's four rows that were "to declare" -- T2b (the NY AM / NY PM boundary), A15 (routing), A16 (the
mix's shares and assignment), A17 (the state rule) -- declared and loading (`extended/lever_space.py`,
`docs/plans/LEVER_TABLE_topstep50k.md`). Each loads with its source kind; every other lever's output is the one it
had before (master 89be4b3, loaded from git; compared with the readings S1 and T7 absent), save the NY split that T2b
now puts into `session_windows()`; A9 and A19 stay refused by their unstated keys; the router takes A15's values and
deals A16's pools in opening order. The sampler test (`extended.search_space`) is **skipped until Q-186 merges**; at
that merge it must run, not skip, and the sampler must refuse any `ny_boundary` but T2b's. Pure Python on the record,
the calendar and one Stage 2 config only (no bar, no result file); fast.
"""
from __future__ import annotations

import calendar
import importlib.util
import math
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from extended import day_calendar as DC
from extended import lever_space as LS
from extended import modes_rules as MR
from extended import modes_terms as M
from extended import router as R
from extended.firm_terms import UnverifiedTerm

ROOT = Path(__file__).resolve().parent.parent
BASE = "89be4b3"                                        # master before this item: the levers' outputs to keep
NEW = ("T2b", "A15", "A16", "A17")


@pytest.fixture
def no_s1_reading(tmp_path, monkeypatch):
    """The readings absent: S1's, and T7's where the loader has one (wt-har; `raising=False` holds on either branch)."""
    monkeypatch.setattr(LS, "S1_PATH", tmp_path / "absent" / "s1_range.csv")
    monkeypatch.setattr(LS, "T7_PATH", tmp_path / "absent" / "t7_forecast.csv", raising=False)


def _weekdays(a: date, b: date) -> list[date]:
    out, d = [], a
    while d <= b:
        if d.weekday() < calendar.SATURDAY:
            out.append(d)
        d += timedelta(days=1)
    return out


# ------------------------------------------------------------------------------------------------ the four rows load


def test_the_four_rows_load_with_their_source_and_nothing_is_left_to_declare() -> None:
    assert not [i for i, lv in LS.LEVERS.items() if lv.source == LS.TODECL]
    for i in NEW:
        lv = LS.LEVERS[i]
        assert lv.source == LS.DECL, (i, lv.source)
        r = LS.bounds(i)
        assert r.lever == i and r.values, i
    assert LS.LEVERS["T2b"].cls == LS.FIXED and LS.bounds("T2b").kind == "fixed"
    assert LS.LEVERS["A15"].cls == LS.SEARCHED and LS.bounds("A15").kind == "choices"
    assert LS.LEVERS["A16"].cls == LS.FIXED and LS.bounds("A16").kind == "fixed"
    assert LS.LEVERS["A17"].cls == LS.SEARCHED and LS.bounds("A17").kind == "choices"


def test_a9_a19_and_the_readings_stay_refused(no_s1_reading) -> None:
    with pytest.raises(UnverifiedTerm):
        LS.bounds("A9")
    with pytest.raises(UnverifiedTerm):
        LS.bounds("A19")
    with pytest.raises(LS.NotComputed):
        LS.bounds("T7")
    with pytest.raises(LS.NotComputed):
        LS.bounds("S1")
    assert set(LS.refusals()) == {"T7", "S1", "A9", "A19", "S6", "S7", "S8", "S9", "A13", "A14"}


# ------------------------------------------------------------------------------------------------ T2b


def _ny_noon_offset(d: date) -> int:
    """Noon New York on trading day d, in minutes after the 17:00 CT reopen of the evening before (independent of the
    loader: zoneinfo directly)."""
    reopen = datetime(d.year, d.month, d.day, 17, 0, tzinfo=ZoneInfo("America/Chicago")) - timedelta(days=1)
    noon = datetime(d.year, d.month, d.day, 12, 0, tzinfo=ZoneInfo("America/New_York"))
    return int((noon - reopen) // timedelta(minutes=1))


def test_t2b_is_noon_new_york_inside_ny_on_every_search_weekday() -> None:
    r = LS.bounds("T2b")
    b = r.values[0]
    td = LS.trading_day()
    step = int(LS.declared("mark_step_min"))
    days = _weekdays(DC.SEARCH_START, DC.SEARCH_END)
    assert r.detail["days_checked"] == len(days)
    for d in days:
        assert LS.ny_boundary(d) == b == _ny_noon_offset(d), d
        ny = DC.anchored_starts(d)["ny"]
        assert ny < b < td["last_entry_offset"] < td["length"], d
    assert b % step == 0
    # the two US zones change clocks on the same dates: the boundary is one CT clock time, through every change
    for d in (date(2021, 3, 12), date(2021, 3, 15), date(2021, 11, 5), date(2021, 11, 8)):
        assert LS.ny_boundary(d) == b
    am, pm = r.detail["ny_am"], r.detail["ny_pm"]
    assert am[1] == pm[0] == b and pm[1] == td["length"]


@pytest.mark.parametrize("local", [("America/New_York", 8, 0), ("America/New_York", 16, 30),
                                   ("America/New_York", 12, 3),
                                   ("America/New_York", 16, 10),     # the 15:10 CT flat: after the last new entry
                                   ("Europe/London", 16, 0)])        # inside NY, on the grid, but two values a year
def test_t2b_refuses_a_boundary_off_ny_or_off_the_mark_grid(monkeypatch, local) -> None:
    bad = dict(LS.DECLARED)
    bad["ny_split_local"] = LS.Declared(local, "test")
    monkeypatch.setattr(LS, "DECLARED", bad)
    with pytest.raises(LS.LeverRefused):
        LS.bounds("T2b")


def test_t2b_is_enforced_where_ny_is_split() -> None:
    """L-M2: `session_windows()` splits NY at T2b's value, and any other boundary a caller passes is refused."""
    b = LS.bounds("T2b").values[0]
    w = LS.session_windows()
    assert w["ny_am"] == (w["ny_am"][0], b) and w["ny_pm"] == (b, LS.trading_day()["length"])
    assert LS.check_ny_boundary(b) == b
    step = int(LS.declared("mark_step_min"))
    for bad in (b + step, b - step, None, True, str(b), b + 0.5):
        with pytest.raises(LS.LeverRefused):
            LS.check_ny_boundary(bad)
    LS.check_design({"T2b": b})
    with pytest.raises(LS.LeverRefused):
        LS.check_design({"T2b": b + step})


def test_t2b_matches_stage_twos_late_morning_window() -> None:
    """L-n1: the boundary on the firm's clock is the start of Stage 2's `late_morning` window (D-244, D-245)."""
    import yaml

    cfg = yaml.safe_load((DC.VENDOR_STAGE2 / "config" / "session_setups.yaml").read_text(encoding="utf-8"))
    found = [w for v in cfg.values() if isinstance(v, list) for w in v
             if isinstance(w, dict) and w.get("name") == "late_morning"]
    assert len(found) == 1
    assert LS.bounds("T2b").detail["ct_clock"] == found[0]["start_ct"]


# ------------------------------------------------------------------------------------------------ A15 and A16


def test_a15_is_the_routers_rotations_with_the_base_first() -> None:
    r = LS.bounds("A15")
    assert r.values == R.ROTATIONS
    assert r.values[0] == "longest_waiting" == r.detail["base"]
    for rot in r.values:                                  # every value is one the router stands behind
        R.Routing(rot, ("c",) if rot == "by_component" else ())
    with pytest.raises(R.RoutingRefused):                 # never a second cell of the base (L-M2)
        R.Routing("by_component")


def test_a16_deals_every_account_to_one_pool_and_every_component_a_pool() -> None:
    assert LS.bounds("A16").values == ("dealt",)
    comps = ("am", "pm", "eve")
    for n in range(1, 8):
        accs = tuple(f"a{j}" for j in range(n))
        pools = LS.deal_pools(comps, accs)
        assert list(pools) == list(comps) and all(pools[c] for c in comps)
        if n >= len(comps):                               # a partition of the accounts
            flat = [a for c in comps for a in pools[c]]
            assert sorted(flat) == sorted(accs) and len(flat) == len(set(flat))
            assert max(map(len, pools.values())) - min(map(len, pools.values())) <= 1
        else:                                             # each component one account, dealt in turn
            assert [pools[c] for c in comps] == [(accs[i % n],) for i in range(len(comps))]
        assert LS.deal_pools(comps, accs) == pools        # deterministic
        opened = {a: 0 for a in accs}                     # all opened together: ties by account id
        assert LS.deal_pools(comps, tuple(reversed(accs)), opened=opened) == pools
    assert LS.deal_pools(("x", "y"), ("a", "b", "c", "d", "e")) == {"x": ("a", "c", "e"), "y": ("b", "d")}
    for bad in ((), ("a",)), (("x",), ()), (("x", "x"), ("a",)), (("x",), ("a", "a")):
        with pytest.raises(LS.LeverRefused):
            LS.deal_pools(*bad)


def test_a16_deals_in_opening_order_whatever_the_order_given() -> None:
    """L-m1: the account order is the opening order (index ascending, ties by id), never the caller's."""
    opened = {"z": 0, "b": 1, "a": 1, "c": 2}
    want = {"x": ("z", "c"), "y": ("a",), "w": ("b",)}
    for accs in (("a", "b", "c", "z"), ("c", "z", "b", "a"), ("z", "a", "b", "c")):
        assert LS.deal_pools(("x", "y", "w"), accs, opened=opened) == want
    assert LS.deal_pools(("x", "y", "w"), ("z", "a", "b", "c")) == want             # the sequence's order, declared
    with pytest.raises(LS.LeverRefused):
        LS.deal_pools(("x",), ("a", "q"), opened=opened)                              # q has no opening index


# ------------------------------------------------------------------------------------------------ A17


def test_a17_values_and_its_rule_read_states() -> None:
    r = LS.bounds("A17")
    assert r.values == ("none", "floor", "target", "floor_target") and r.values[0] == "none"
    t = M.eval_terms("TS-S")
    assert r.detail["eval"] == {"goal": float(t.target), "start_room": MR.start_room(M.EVAL, t)}
    for mode in ("TS/std", "TS/con"):
        f = M.funded_terms(mode)
        assert r.detail[mode] == {"goal": MR.b_star(f)["b_star"], "start_room": MR.start_room(M.FUNDED, f)}
    assert r.read["combine_profit_target"] == LS.rule("combine_profit_target")


TV = 0.5                                                   # a synthetic tick value: the arithmetic only


def _risk(rule, r, *, room, start, goal, s=40, tt=60):
    return LS.state_risk(rule, r, room=room, start_room=start, to_goal=goal, stop_ticks=s, target_ticks=tt,
                         tick_value=TV)


def test_a17_state_risk_arithmetic() -> None:
    one = 40 * TV                                          # one micro at the stop: 20 dollars
    r, start = 400.0, 2000.0
    # none: the mode's r in every state
    assert _risk("none", r, room=10.0, start=start, goal=1.0) == r
    # floor: r scaled by the room's share of the start room, never above r, never below one micro
    assert _risk("floor", r, room=start, start=start, goal=1.0) == r
    assert _risk("floor", r, room=3 * start, start=start, goal=1.0) == r
    assert _risk("floor", r, room=start / 2, start=start, goal=1e9) == pytest.approx(r / 2)
    assert _risk("floor", r, room=1.0, start=start, goal=1e9) == one
    # target: the fewest whole micros whose win (60 ticks) reaches the goal, never above r
    assert _risk("target", r, room=start, start=start, goal=1e9) == r
    assert _risk("target", r, room=start, start=start, goal=90.0) == 3 * one     # 3 x 30 >= 90 > 2 x 30
    assert _risk("target", r, room=start, start=start, goal=91.0) == 4 * one
    assert _risk("target", r, room=start, start=start, goal=5.0) == one
    # floor_target: the smaller of the two cuts
    assert _risk("floor_target", r, room=start / 4, start=start, goal=90.0) == pytest.approx(min(r / 4, 3 * one))
    assert _risk("floor_target", r, room=start / 2, start=start, goal=91.0) == 4 * one
    assert _risk("floor_target", r, room=start / 8, start=start, goal=1e9) == pytest.approx(r / 8)   # the floor binds
    # an r below one micro is the base's to stand aside; the rule never raises it
    assert _risk("floor", 10.0, room=1.0, start=start, goal=1.0) == 10.0
    with pytest.raises(ValueError):
        _risk("buffer", r, room=start, start=start, goal=1.0)


def test_a17_never_raises_a_trades_risk() -> None:
    import random

    rng = random.Random(20261120)                          # a fixed seed for the property draw
    for _ in range(2000):
        rule = rng.choice(LS.declared("state_rules"))
        r = rng.uniform(1.0, 3000.0)
        got = _risk(rule, r, room=rng.uniform(-100.0, 5000.0), start=2000.0, goal=rng.uniform(-10.0, 4000.0),
                    s=rng.randint(8, 200), tt=rng.randint(4, 600))
        assert got <= r + 1e-9 and got > 0


# ------------------------------------------------------------------------------------------------ every other lever


def _old_module(tmp_path: Path):
    try:
        text = subprocess.run(["git", "show", f"{BASE}:extended/lever_space.py"], cwd=ROOT, capture_output=True,
                              check=True, text=True, encoding="utf-8").stdout
    except (OSError, subprocess.CalledProcessError):
        pytest.skip(f"git or commit {BASE} unavailable")
    p = tmp_path / f"lever_space_{BASE}.py"
    p.write_text(text, encoding="utf-8")
    spec = importlib.util.spec_from_file_location(f"lever_space_{BASE}", p)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _outcome(mod, i: str) -> str:
    try:
        return repr(mod.bounds(i))
    except Exception as e:                                # the refusal's class and message
        return f"{type(e).__name__}: {e}"


def test_every_other_lever_is_bit_for_bit_the_one_before(tmp_path, monkeypatch, no_s1_reading) -> None:
    old = _old_module(tmp_path)
    monkeypatch.setattr(old, "S1_PATH", tmp_path / "absent" / "s1_range.csv")
    monkeypatch.setattr(old, "T7_PATH", tmp_path / "absent" / "t7_forecast.csv", raising=False)
    b = LS.bounds("T2b").values[0]

    def split(w):                                         # 89be4b3's windows with T2b's split put in (L-M2)
        w = dict(w)
        w["ny_am"], w["ny_pm"] = (w["ny_am"][0], b), (b, w["ny_pm"][1])
        return w
    try:
        assert list(old.LEVERS) == list(LS.LEVERS)
        for i, lv in old.LEVERS.items():
            if i in NEW:
                continue
            nv = LS.LEVERS[i]
            assert (lv.layer, lv.name, lv.cls, lv.source, lv.keys, lv.depends) == \
                (nv.layer, nv.name, nv.cls, nv.source, nv.keys, nv.depends), i
            if i == "T2":                                 # its detail carries the windows: T2b's split, nothing else
                o, n = old.bounds(i), LS.bounds(i)
                assert repr(split(o.detail["windows"])) == repr(n.detail["windows"])
                assert repr(o.__class__.__name__) == repr(n.__class__.__name__)
                assert (o.lever, o.kind, o.values, o.lo, o.hi, o.step, o.unit, repr(o.read)) == \
                    (n.lever, n.kind, n.values, n.lo, n.hi, n.step, n.unit, repr(n.read))
                assert repr({k: v for k, v in o.detail.items() if k != "windows"}) == \
                    repr({k: v for k, v in n.detail.items() if k != "windows"})
                continue
            assert _outcome(old, i) == _outcome(LS, i), i
        for k, d in old.DECLARED.items():
            assert LS.DECLARED[k].value == d.value and LS.DECLARED[k].cite == d.cite, k
        assert repr(split(old.session_windows())) == repr(LS.session_windows())
        assert repr(old.trading_day()) == repr(LS.trading_day()) and repr(old.stop_caps()) == repr(LS.stop_caps())
        for s in LS.declared("sources"):
            assert old.latency_cells(s) == LS.latency_cells(s)
    finally:
        sys.modules.pop(f"lever_space_{BASE}", None)


# ------------------------------------------------------------------------------------------------ the sampler


def test_the_sampler_draws_the_new_rows() -> None:
    SS = pytest.importorskip("extended.search_space")
    days = (date(2021, 3, 12), date(2021, 3, 15), date(2022, 6, 1))
    b = int(LS.bounds("T2b").values[0])
    space = SS.from_lever_space(slots={"ny_am": 1, "ny_pm": 1}, ny_boundary=b, days=days)
    assert {"A15", "A17"} <= set(space.names)
    assert space.fixed["T2b"] == (b,) and space.fixed["A16"] == ("dealt",)
    with pytest.raises(Exception):                         # L-M2: no boundary but T2b's
        SS.from_lever_space(slots={"ny_am": 1, "ny_pm": 1}, ny_boundary=b + int(LS.declared("mark_step_min")),
                            days=days)
    ledger = SS.CellLedger()
    designs = SS.Sampler(space, seed=20261120, method="sobol").survey(16, ledger=ledger)
    assert designs
    for d in designs:
        assert d["A15"] in R.ROTATIONS and d["A17"] in LS.declared("state_rules")
