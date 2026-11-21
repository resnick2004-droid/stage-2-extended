"""The lever table's four rows that were "to declare" -- T2b (the NY AM / NY PM boundary), A15 (routing), A16 (the
mix's shares and assignment), A17 (the state rule) -- declared and loading (`extended/lever_space.py`,
`docs/plans/LEVER_TABLE_topstep50k.md`). Each loads with its source kind; every other lever's output is the one it
had before (master 3cf17d4, Wave 3.4's per-date sessions and T7's loader, loaded from git; compared with the readings
S1 and T7 absent), save the NY split that T2b now puts into `session_windows(day)` on each date; A9 and A19 stay
refused by their unstated keys; the router takes A15's values and deals A16's pools in opening order. The sampler
(`extended.search_space`, merged with Wave 3.4) runs, and refuses any `ny_boundary` but T2b's (L-M2). T2b follows
both daylight-saving changes of a year (March and November) per date; MFFU and Lucid keep T2b, A15, A16 and A17 "to
declare for this firm" (Q-181c). Pure Python on the record, the calendar and one Stage 2 config only (no bar, no
result file); fast.
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
BASE = "3cf17d4"                                        # master before this item: the levers' outputs to keep
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
    """L-M2: `session_windows(day)` splits NY at T2b's value on each date, and any other boundary a caller passes is
    refused."""
    b = LS.bounds("T2b").values[0]
    for d in (date(2021, 1, 15), date(2021, 7, 15), date(2021, 3, 17)):
        w = LS.session_windows(d)
        assert w["ny_am"] == (DC.anchored_starts(d)["ny"], b) and w["ny_pm"] == (b, LS.trading_day()["length"])
    assert LS.check_ny_boundary(b, firm="topstep") == b
    step = int(LS.declared("mark_step_min"))
    for bad in (b + step, b - step, None, True, str(b), b + 0.5):
        with pytest.raises(LS.LeverRefused):
            LS.check_ny_boundary(bad, firm="topstep")
    LS.check_design({"T2b": b})
    with pytest.raises(LS.LeverRefused):
        LS.check_design({"T2b": b + step})


def _us_changes(year: int) -> tuple[date, date]:
    """The US clock changes of `year` (the second Sunday of March, the first Sunday of November), by the calendar rule
    alone -- independent of zoneinfo and of the loader."""
    mar = [date(year, 3, d) for d in range(1, 15) if date(year, 3, d).weekday() == calendar.SUNDAY][1]
    nov = [date(year, 11, d) for d in range(1, 8) if date(year, 11, d).weekday() == calendar.SUNDAY][0]
    return mar, nov


@pytest.mark.parametrize("year", [2020, 2021, 2022, 2023])
def test_t2b_splits_ny_per_date_across_both_daylight_saving_changes(year: int) -> None:
    """Q-188b: `session_windows(day)` splits NY at noon New York **on that date**: across March's and November's
    changes the split stays at 12:00 New York and 11:00 CT while its UTC instant moves an hour, as the anchors do."""
    utc, ny_tz, chi = ZoneInfo("UTC"), ZoneInfo("America/New_York"), ZoneInfo("America/Chicago")
    for change in _us_changes(year):
        before, after = change - timedelta(days=2), change + timedelta(days=1)      # the Friday before, the Monday after
        hours = {}
        for d in (before, after):
            w = LS.session_windows(d)
            b = w["ny_am"][1]
            assert w["ny_pm"][0] == b == LS.ny_boundary(d) == _ny_noon_offset(d), d
            assert w["ny_am"][0] == DC.anchored_starts(d)["ny"] < b < w["ny_pm"][1] == LS.trading_day()["length"], d
            reopen = datetime(d.year, d.month, d.day, 17, 0, tzinfo=chi) - timedelta(days=1)
            at = (reopen.astimezone(utc) + timedelta(minutes=b)).astimezone(ny_tz)   # the boundary's instant
            assert (at.date(), at.hour, at.minute) == (d, 12, 0), d                   # noon New York, that date
            assert (at.astimezone(chi).hour, at.astimezone(chi).minute) == (11, 0), d
            hours[d] = at.astimezone(utc).hour
        assert abs(hours[before] - hours[after]) == 1, (change, hours)                # the clock changed between them
        assert hours[after] == (16 if change.month == 3 else 17), (change, hours)


def test_t2b_is_converted_on_each_date_and_a_split_t2b_refuses_is_never_made(monkeypatch) -> None:
    """The boundary is the declared local time converted per date (zoneinfo), never one CT minute carried over:
    declared on London's clock (a test value only), `ny_boundary(day)` moves in the weeks when the UK and US clocks
    disagree -- in March and in November -- and not on the other dates checked. T2b refuses such a value, so
    `session_windows(day)` refuses to split at it on every date (the red team's m3: the split equals what
    `bounds("T2b")` loads, or nothing is split)."""
    bad = dict(LS.DECLARED)
    bad["ny_split_local"] = LS.Declared(("Europe/London", 16, 0), "test: a clock that changes on other dates")
    monkeypatch.setattr(LS, "DECLARED", bad)
    same = {d: LS.ny_boundary(d) for d in (date(2021, 1, 15), date(2021, 7, 15), date(2021, 11, 10))}
    moved = {d: LS.ny_boundary(d) for d in (date(2021, 3, 17), date(2021, 11, 3))}
    assert set(same.values()) == {10 * 60 - 17 * 60 + 24 * 60}                       # 16:00 London = 10:00 CT
    assert set(moved.values()) == {11 * 60 - 17 * 60 + 24 * 60}                      # the mismatch weeks: 11:00 CT
    with pytest.raises(LS.LeverRefused):                                              # T2b's own check refuses it
        LS.bounds("T2b")
    for d in list(same) + list(moved):
        with pytest.raises(LS.LeverRefused):
            LS.session_windows(d)


def test_the_split_equals_t2bs_loaded_value_or_refuses(monkeypatch) -> None:
    """m3: a split that differs from `bounds("T2b")` on some date (here a date-dependent boundary standing in for a
    later declaration's or a held-out date's) is refused on that date only; on the declared value they agree on every
    search-year weekday and beyond (2024-2030, calendar arithmetic only)."""
    b = LS.bounds("T2b").values[0]
    for y in range(2020, 2031):
        for d in (date(y, 1, 15), date(y, 3, 17), date(y, 7, 15), date(y, 11, 3)):
            if d.weekday() < calendar.SATURDAY:
                assert LS.session_windows(d)["ny_am"][1] == b == LS.ny_boundary(d), d
    real = LS.ny_boundary
    monkeypatch.setattr(LS, "ny_boundary", lambda d: real(d) + (5 if d == date(2021, 3, 17) else 0))
    assert LS.session_windows(date(2021, 3, 16))["ny_am"][1] == b
    with pytest.raises(LS.LeverRefused, match="not T2b's loaded"):
        LS.session_windows(date(2021, 3, 17))


@pytest.mark.parametrize("firm", ["mffu", "lucid"])
def test_the_split_is_refused_for_mffu_and_lucid(no_s1_reading, firm: str) -> None:
    """Q-181c (wt/wt-payout): T2b, A15, A16 and A17 are **to declare for this firm** -- refused (`NotDeclared`), never
    Topstep's declared values carried over, now that Topstep's rows load for real (not simulated)."""
    from extended import lever_space_firms as LF

    ids = ("T2b", "A15", "A16", "A17")
    for i in ids:
        assert LS.bounds(i).lever == i                                                # Topstep's: declared, loading
        assert LF.levers(firm)[i].source == LS.TODECL
        with pytest.raises(LS.NotDeclared, match="to declare"):
            LF.bounds(firm, i)
        assert LF.vs_topstep(firm, i) == LF.DIFFERS
        assert LF.refusals(firm)[i] == "NotDeclared" and i not in LF.load(firm)
    table = (ROOT / LF.TABLES[firm]).read_text(encoding="utf-8")
    for i in ids:
        row = [ln for ln in table.splitlines() if ln.startswith(f"| {i} |")]
        assert len(row) == 1 and "**to declare for this firm**" in row[0], i
    if firm == "mffu":                       # MFFU's own sessions: NY left whole on every date, DST changes included
        for d in (date(2021, 3, 12), date(2021, 3, 15), date(2021, 11, 5), date(2021, 11, 8), date(2021, 7, 15)):
            w = LF.mffu_session_windows(d)
            assert w["ny_am"][1] is None and w["ny_pm"][0] is None, d
            assert LS.session_windows(d)["ny_am"][1] == LS.ny_boundary(d)              # Topstep's splits, MFFU's not


def test_topsteps_lever_space_loads_complete(no_s1_reading) -> None:
    """Q-188b: Topstep's space loads every lever but the refusals declared to stand -- the two readings absent under
    the pin (S1, T7), the two unstated keys (A9, A19) and the six dropped levers; nothing is to declare, and `load`
    is `space()`."""
    sp, rf = LS.space(), LS.refusals()
    assert set(sp) | set(rf) == set(LS.LEVERS) and not set(sp) & set(rf)
    assert rf == {"T7": "NotComputed", "S1": "NotComputed", "S6": "DroppedLever", "S7": "DroppedLever",
                  "S8": "DroppedLever", "S9": "DroppedLever", "A9": "UnverifiedTerm", "A13": "DroppedLever",
                  "A14": "DroppedLever", "A19": "UnverifiedTerm"}
    assert set(NEW) <= set(sp)
    assert not [i for i, lv in LS.LEVERS.items() if lv.source == LS.TODECL]
    assert {i for i, lv in LS.LEVERS.items() if lv.cls == LS.DROPPED} == {k for k, v in rf.items() if v == "DroppedLever"}
    assert list(LS.load("topstep")) == list(sp)
    assert all(repr(LS.load("topstep")[k]) == repr(v) for k, v in sp.items())


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
    from extended import components as C
    from extended import triggers as T

    d = C.Design("topstep", (C.Component("c", "ny_am", 960, 1000, T.P16Marks((960,)), 40, 1.0),))
    for rot in r.values:                                  # every value is one the router stands behind
        R.Routing(rot, design=d if rot == "by_component" else None, firm="topstep")
    with pytest.raises(R.RoutingRefused):                 # never a second cell of the base (L-M2)
        R.Routing("by_component", firm="topstep")


def test_a16_deals_every_account_to_one_pool_and_every_component_a_pool() -> None:
    assert LS.bounds("A16").values == ("dealt",)
    comps = ("am", "pm", "eve")
    for n in range(1, 8):
        accs = tuple(f"a{j}" for j in range(n))
        pools = LS.deal_pools(comps, accs, firm="topstep")
        assert list(pools) == list(comps) and all(pools[c] for c in comps)
        if n >= len(comps):                               # a partition of the accounts
            flat = [a for c in comps for a in pools[c]]
            assert sorted(flat) == sorted(accs) and len(flat) == len(set(flat))
            assert max(map(len, pools.values())) - min(map(len, pools.values())) <= 1
        else:                                             # each component one account, dealt in turn
            assert [pools[c] for c in comps] == [(accs[i % n],) for i in range(len(comps))]
        assert LS.deal_pools(comps, accs, firm="topstep") == pools        # deterministic
        opened = {a: 0 for a in accs}                     # all opened together: ties by account id
        assert LS.deal_pools(comps, tuple(reversed(accs)), firm="topstep", opened=opened) == pools
    assert LS.deal_pools(("x", "y"), ("a", "b", "c", "d", "e"), firm="topstep") == {"x": ("a", "c", "e"), "y": ("b", "d")}
    for bad in ((), ("a",)), (("x",), ()), (("x", "x"), ("a",)), (("x",), ("a", "a")):
        with pytest.raises(LS.LeverRefused):
            LS.deal_pools(*bad, firm="topstep")


def test_a16_deals_in_opening_order_whatever_the_order_given() -> None:
    """L-m1: the account order is the opening order (index ascending, ties by id), never the caller's."""
    opened = {"z": 0, "b": 1, "a": 1, "c": 2}
    want = {"x": ("z", "c"), "y": ("a",), "w": ("b",)}
    for accs in (("a", "b", "c", "z"), ("c", "z", "b", "a"), ("z", "a", "b", "c")):
        assert LS.deal_pools(("x", "y", "w"), accs, firm="topstep", opened=opened) == want
    assert LS.deal_pools(("x", "y", "w"), ("z", "a", "b", "c"), firm="topstep") == want             # the sequence's order, declared
    with pytest.raises(LS.LeverRefused):
        LS.deal_pools(("x",), ("a", "q"), firm="topstep", opened=opened)                              # q has no opening index


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
    return LS.state_risk(rule, r, firm="topstep", room=room, start_room=start, to_goal=goal, stop_ticks=s, target_ticks=tt,
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

    def split(w):                                         # the base's windows with T2b's split put in (L-M2)
        w = dict(w)
        w["ny_am"], w["ny_pm"] = (w["ny_am"][0], b), (b, w["ny_pm"][1])
        return w

    def split_range(r):                                   # `session_window_range`'s output, split the same way
        rng = {k: dict(v) for k, v in r["range"].items()}
        rng["ny_am"]["end"], rng["ny_pm"]["start"] = (b, b), (b, b)
        return {"span": r["span"], "range": rng,
                "distinct": [dict(e, windows=split(e["windows"])) for e in r["distinct"]]}
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
                assert repr(split_range(o.detail["windows"])) == repr(n.detail["windows"])
                assert repr(o.__class__.__name__) == repr(n.__class__.__name__)
                assert (o.lever, o.kind, o.values, o.lo, o.hi, o.step, o.unit, repr(o.read)) == \
                    (n.lever, n.kind, n.values, n.lo, n.hi, n.step, n.unit, repr(n.read))
                assert repr({k: v for k, v in o.detail.items() if k != "windows"}) == \
                    repr({k: v for k, v in n.detail.items() if k != "windows"})
                continue
            assert _outcome(old, i) == _outcome(LS, i), i
        for k, d in old.DECLARED.items():
            assert LS.DECLARED[k].value == d.value and LS.DECLARED[k].cite == d.cite, k
        for d in (date(2021, 1, 15), date(2021, 3, 12), date(2021, 3, 15), date(2021, 3, 17), date(2021, 7, 15),
                  date(2021, 11, 5), date(2021, 11, 8)):
            assert repr(split(old.session_windows(d))) == repr(LS.session_windows(d)), d
        assert repr(old.trading_day()) == repr(LS.trading_day()) and repr(old.stop_caps()) == repr(LS.stop_caps())
        for s in LS.declared("sources"):
            assert old.latency_cells(s) == LS.latency_cells(s)
    finally:
        sys.modules.pop(f"lever_space_{BASE}", None)


# ------------------------------------------------------------------------------------------------ the sampler


def test_the_sampler_holds_the_new_rows() -> None:
    """Q-186 (Wave 3.4's `extended.search_space`) has merged: this runs, never skips. The sampler holds T2b and A16
    fixed, **holds A15 and A17 at their bases until wired** (m4: fixed, labelled, never dimensions, so no two designs
    differing only there are drawn), refuses a slot in `ny` (m2), and refuses any NY boundary but T2b's (L-M2), in
    `session_spans` itself."""
    from extended import search_space as SS

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import search_toys as TY

    days = (date(2021, 3, 12), date(2021, 3, 15), date(2022, 6, 1))
    b = int(LS.bounds("T2b").values[0])
    space = SS.from_lever_space(slots={"ny_am": 1, "ny_pm": 1}, ny_boundary=b, days=days)
    assert not {"A15", "A17"} & {d.lever for d in space.dims}
    assert space.fixed["T2b"] == (b,) and space.fixed["A16"] == ("dealt",)
    assert space.fixed["A15"] == ("longest_waiting",) and space.fixed["A17"] == ("none",)
    assert dict(space.held) == LS.HELD_UNTIL_WIRED and all(v.startswith("held until wired") for v in space.held.values())
    def shape(sp):
        return [(d.name, d.kind, d.lo, d.hi, d.step, d.values, d.labels, d.active_if) for d in sp.dims]
    assert shape(SS.from_lever_space(slots={"ny_am": 1, "ny_pm": 1}, days=days)) == shape(space)   # T2b's, by default
    assert all(space.fixed[k] == (LS.held_value(k),) for k in LS.HELD_UNTIL_WIRED)
    with pytest.raises(SS.SpaceRefused, match="whole NY"):
        SS.from_lever_space(slots={"ny": 1}, days=days)
    with pytest.raises(SS.SpaceRefused, match="whole NY"):
        SS.Sampler(SS.Space(space.dims, slots=(SS.Slot("ny.0", "ny", 0, 100, 5),)), seed=1, method="sobol")
    step = int(LS.declared("mark_step_min"))
    for bad in (b + step, b - step, b + 0.5, str(b), True):
        with pytest.raises(SS.SpaceRefused):
            SS.from_lever_space(slots={"ny_am": 1, "ny_pm": 1}, ny_boundary=bad, days=days)
        with pytest.raises(SS.SpaceRefused):
            SS.session_spans(days[0], bad)
    for d in days:
        sp = SS.session_spans(d, b)
        assert sp["ny_am"][1] == sp["ny_pm"][0] == b == LS.session_windows(d)["ny_am"][1]
    ledger = SS.CellLedger()
    designs = SS.Sampler(space, seed=20261120, method="sobol").survey(16, ledger=ledger, **TY.SV)
    assert designs
    for d in designs:
        assert "A15" not in d and "A17" not in d
