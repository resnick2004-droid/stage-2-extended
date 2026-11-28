"""Q-215: the survey's real-bar route (`extended/survey_route.py`) on synthetic bars only (`tests/survey_route_world.py`:
the real Topstep $50K lever space with S1 stood in, synthetic NQ bars and void calendar; no store, no result file).

* every lever of the table is mapped, passed to the firm path, held by the library or dropped -- a partition held
  equal to `lever_space.LEVERS`;
* every refusal refuses, by name, and each is shown to bite: a one-line source edit removing it (the red team's
  mutplugin form, `_edit`) lets the point through, so the test fails on that mutant;
* P-14's trigger on a date is the playbook's (`playbook._trigger_on`), and the route's trades are `design_trades`'
  frame for frame on one component's days (one plumbing);
* entries at alert + L or later, every offer live inside its window, the stop S1's translation (stand-asides
  counted), the target floor(w x stop), the facts' entry ticks each component's;
* stop first on a two-barrier bar (a planted bar; its target-only twin the positive control);
* shift invariance: every decision with alert <= t unchanged when every bar stamped t or later is replaced, over many
  t on days around a roll and a clock change, each session's first minutes and offers' own alerts among them; two
  planted look-aheads (the trailing range reading its own day, a limit level read at its alert's bar) are caught;
* the trailing range equals `s1_range.add_trailing` on the vendored walker arrays (a child process, synthetic bars).
"""
from __future__ import annotations

import dataclasses
import inspect
import json
import math
import subprocess
import sys
import textwrap
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import design_trades as DT  # noqa: E402
from extended import lever_space as LS  # noqa: E402
from extended import playbook as PB  # noqa: E402
from extended import search_space as SS  # noqa: E402
from extended import survey_route as SR  # noqa: E402
from extended import synthetic_bars as SB  # noqa: E402
from extended import triggers as T  # noqa: E402
from extended import vol_descriptive as V  # noqa: E402
from extended import walker as W  # noqa: E402

import survey_route_world as RW  # noqa: E402  (tests/ is on sys.path under pytest's rootdir)


# ------------------------------------------------------------------------------------------------ fixtures


@pytest.fixture(scope="module")
def sp():
    return RW.space()


@pytest.fixture(scope="module")
def world():
    b = RW.bars()
    hist = T.History.from_bars(b)
    cal = RW.fake_sources(b)
    return {"bars": b, "hist": hist, "cal": cal, "kinds": RW.day_kinds(hist)}


@pytest.fixture(scope="module")
def built(sp, world):
    rt = SR.route(sp, RW.point(sp), side_rules=RW.SIDE_RULES, source_params={"rl3": RW.RL3_PARAMS})
    out = SR.build(rt, world["hist"], **RW.build_kw(world["hist"], world["cal"]))
    return rt, out


def _route(sp, d, **kw):
    kw.setdefault("side_rules", RW.SIDE_RULES)
    kw.setdefault("source_params", {"rl3": RW.RL3_PARAMS})
    return SR.route(sp, d, **kw)


def _edit(fn_name: str, old: str, new: str):
    """A one-line source edit of `extended.survey_route.<fn_name>`, compiled with the module's own globals: the mutant
    is the function with `old` replaced by `new`, exactly once."""
    orig = getattr(SR, fn_name)
    src = textwrap.dedent(inspect.getsource(orig))
    assert src.count(old) == 1, (fn_name, old)
    ns: dict = {}
    exec(compile("from __future__ import annotations\n" + src.replace(old, new), SR.__file__, "exec"), SR.__dict__, ns)
    return ns[fn_name]


# ------------------------------------------------------------------------------------------------ the levers


def test_every_lever_of_the_table_has_one_handling():
    assert set(SR.LEVER_ROUTE) == set(LS.LEVERS)
    assert set(SR.LEVER_ROUTE.values()) <= {SR.ROUTE, SR.LIBRARY, SR.FIRM_PATH, SR.DROPPED}
    dropped = {k for k, lv in LS.LEVERS.items() if lv.cls == LS.DROPPED}
    assert {k for k, v in SR.LEVER_ROUTE.items() if v == SR.DROPPED} == dropped
    assert {k for k, v in SR.LEVER_ROUTE.items() if v == SR.LIBRARY} == {"T2b", "T6", "T8"}


def test_the_slot_dimensions_are_the_routes(sp):
    for dim in sp.dims:
        if dim.slot is not None:
            sub = dim.name[len(dim.slot) + 1:]
            assert SR.SLOT_KEYS[sub] == dim.lever, dim.name
            assert SR.LEVER_ROUTE[dim.lever] == SR.ROUTE


def test_the_point_routes_and_passes_the_firm_levers_unchanged(sp):
    d = RW.point(sp)
    rt = _route(sp, d)
    assert [s.name for s in rt.slots] == ["london.0", "ny_am.0", "ny_pm.0"]
    firm = {dim.name for dim in sp.dims if dim.slot is None and SR.LEVER_ROUTE[dim.lever] == SR.FIRM_PATH}
    assert firm <= set(rt.firm_levers) and all(rt.firm_levers[k] == d[k] for k in firm)
    assert rt.firm_levers["A15"] == sp.fixed["A15"] and rt.firm_levers["A17"] == sp.fixed["A17"]
    assert "T7" in rt.provenance and "T8" in rt.provenance
    assert rt.slots[1].params == RW.RL3_PARAMS and rt.slots[1].entry_kind == "resting"
    assert rt.slots[0].entry_kind == "market" and rt.slots[2].entry_kind == "resting"


def _bad_point(sp, what):
    d = RW.point(sp)
    if what == "coin":
        d["london.0.T1"] = "coin"
    elif what == "p16":
        d["ny_am.0.T1"], d["ny_am.0.T5"], d["ny_am.0.T4"] = "p16", "market", None
    elif what == "t7":
        d["T7"] = "admit"
    elif what == "collide":
        d["ny_am.0.last"] = d["ny_am.0.first"] - 5
    return d


#: (case, how the point is made bad, the refusal's words, the mutant that removes the refusal: fn, old, new)
REFUSALS = {
    "t7-admit": ("t7", {}, "T7 = 'admit'", ("route", "if value not in T7_MAPPED:", "if False:")),
    "coin-source": ("coin", {}, "offers no playbook side", ("_slot", "if src in TS.NO_SIDE:", "if False:")),
    "p16-source": ("p16", {}, "offers no playbook side", ("_slot", "if src in TS.NO_SIDE:", "if False:")),
    "space-refuses": ("collide", {}, "a point the space refuses", ("route", "if why is not None:", "if False:")),
    "no-side-rule": (None, {"side_rules": {"rl3": "fade"}}, "no declared side rule",
                     ("_slot", "if src not in side_rules:", "if False:")),
    "rl3-params-missing": (None, {"source_params": {}}, "RL3's declared parameters",
                           ("_slot", "if not isinstance(got, Mapping) or sorted(got) != sorted(RL3_PARAMS):",
                            "if False:")),
    "rl3-params-extra": (None, {"source_params": {"rl3": {**RW.RL3_PARAMS, "stop": 50}}}, "RL3's declared parameters",
                         ("_slot", "if not isinstance(got, Mapping) or sorted(got) != sorted(RL3_PARAMS):",
                          "if False:")),
}


def _mutated(monkeypatch, fn, old, new):
    m = _edit(fn, old, new)
    if fn == "route":
        return m
    monkeypatch.setattr(SR, fn, m)
    return SR.route


@pytest.mark.parametrize("case", sorted(REFUSALS))
def test_each_refusal_refuses_by_name_and_its_mutant_is_killed(sp, monkeypatch, case):
    what, kw, words, (fn, old, new) = REFUSALS[case]
    d = _bad_point(sp, what) if what else RW.point(sp)
    with pytest.raises(SR.RouteRefused, match=words.replace("(", r"\(").replace(")", r"\)")):
        _route(sp, d, **kw)
    r = _mutated(monkeypatch, fn, old, new)
    kw = {"side_rules": RW.SIDE_RULES, "source_params": {"rl3": RW.RL3_PARAMS}, **kw}
    try:
        r(sp, d, **kw)
        refused = False
    except (SR.RouteRefused, Exception) as e:     # the mutant may crash downstream; it must not refuse by name
        refused = isinstance(e, SR.RouteRefused) and words in str(e)
    assert not refused, f"mutant {case} still refuses: the test could not tell it from the route"


def test_a_lever_without_a_handling_refuses_by_name(sp, monkeypatch):
    d = RW.point(sp)
    monkeypatch.setitem(SR.LEVER_ROUTE, "A6", None)
    monkeypatch.delitem(SR.LEVER_ROUTE, "A6")
    with pytest.raises(SR.RouteRefused, match="'A6'.*neither maps nor passes"):
        _route(sp, d)
    tail = "\n            raise RouteRefused(f\"REFUSED: the point's key"
    m = _edit("route", "if how is None:" + tail, "if False:" + tail)
    with pytest.raises(Exception) as e:                 # the mutant reaches the firm-path branch's else and errs
        m(sp, d, side_rules=RW.SIDE_RULES, source_params={"rl3": RW.RL3_PARAMS})
    assert "neither maps nor passes" not in str(e.value)


def test_a_design_wide_lever_the_route_does_not_read_refuses(sp, monkeypatch):
    d = RW.point(sp)
    monkeypatch.setitem(SR.LEVER_ROUTE, "A6", SR.LIBRARY)
    with pytest.raises(SR.RouteRefused, match="'A6' .* is not a design-wide lever the route reads"):
        _route(sp, d)
    tail = '\n            firm[key] = value\n            prov[key] = "firm path (passed on unchanged)"'
    m = _edit("route", "if how == FIRM_PATH:" + tail, "if how in (FIRM_PATH, LIBRARY):" + tail)
    assert m(sp, d, side_rules=RW.SIDE_RULES, source_params={"rl3": RW.RL3_PARAMS}).firm_levers["A6"] == d["A6"]


def test_a_space_without_s1_refuses_and_never_types_a_stop():
    bare = RW.space(with_s1=False)
    assert "S1" in bare.refused
    d = RW.point(bare)
    for k in [k for k in d if k.endswith(".S1")]:
        del d[k]
    with pytest.raises(SR.RouteRefused, match="no stop width: S1 is not a lever of the space"):
        _route(bare, d)
    m = _edit("_slot", 'if SS.slot_dim(name, "S1") not in space.names():', "if False:")
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(SR, "_slot", m)
        with pytest.raises(Exception) as e:
            _route(bare, d)
        assert "no stop width" not in str(e.value)


def test_another_firms_space_and_another_t8_refuse(sp):
    other = dataclasses.replace(sp, firm="mffu")
    with pytest.raises(SR.RouteRefused, match="Topstep"):
        _route(other, RW.point(sp))
    t8 = dataclasses.replace(sp, fixed={**sp.fixed, "T8": ("trigger",)})
    with pytest.raises(SR.RouteRefused, match="T8 is fixed"):
        _route(t8, RW.point(sp))
    m = _edit("route", "if tuple(value) != (T8_EVALUATION,):", "if False:")
    m(t8, RW.point(sp), side_rules=RW.SIDE_RULES, source_params={"rl3": RW.RL3_PARAMS})   # the mutant lets it pass


def test_the_firm_refusal_has_teeth(sp):
    other = dataclasses.replace(sp, firm="mffu")
    m = _edit("route", 'if getattr(space, "firm", None) != FIRM:', "if False:")
    assert m(other, RW.point(sp), side_rules=RW.SIDE_RULES, source_params={"rl3": RW.RL3_PARAMS}).slots


def test_the_spaces_fixed_levers_refuse_by_name(sp):
    """A fixed lever the route has no handling for, a fixed slot lever, and a T6 off the library's limit window."""
    d = RW.point(sp)
    unknown = dataclasses.replace(sp, fixed={**sp.fixed, "ZZ": (1,)})
    with pytest.raises(SR.RouteRefused, match="the space fixes 'ZZ', which the route neither maps"):
        _route(unknown, d)
    tail = '\n            raise RouteRefused(f"REFUSED: the space fixes {key!r}, which the route neither'
    m = _edit("route", "if how is None:" + tail, "if False:" + tail)
    with pytest.raises(Exception) as e:
        m(unknown, d, side_rules=RW.SIDE_RULES, source_params={"rl3": RW.RL3_PARAMS})
    assert "neither maps" not in str(e.value)
    with pytest.raises(SR.RouteRefused, match="the space fixes 'T1'"):
        _route(dataclasses.replace(sp, fixed={**sp.fixed, "T1": ("p14",)}), d)
    t6 = dataclasses.replace(sp, fixed={**sp.fixed, "T6": (T.LIMIT_WINDOW + 1,)})
    with pytest.raises(SR.RouteRefused, match="T6 is fixed"):
        _route(t6, d)
    m = _edit("route", "if tuple(value) != (T.LIMIT_WINDOW,):", "if False:")
    assert m(t6, d, side_rules=RW.SIDE_RULES, source_params={"rl3": RW.RL3_PARAMS}).slots


def _slot_call(fn, sp, d, name):
    sl = next(s for s in sp.slots if s.name == name)
    return fn(sp, d, sl, 0, RW.SIDE_RULES, {"rl3": RW.RL3_PARAMS})


#: a slot's own refusals, reached past the space's check (the space admits none of these points): (slot, the point's
#: change, the words, the mutant's line)
SLOT_REFUSALS = {
    "p14-entry": ("london.0", {"T5": SS.TICKET}, "P-14 takes an entry",
                  'if entry not in T.ENTRIES or lat not in LS.latency_cells("p14"):'),
    "rl3-entry": ("ny_am.0", {"T5": "market"}, "RL3 takes its tickets", "if entry != SS.TICKET or lat is not None:"),
    "unknown-source": ("london.0", {"T1": "xyz"}, "is not one of the route's sources", "if src not in SIDED:"),
    "non-positive-w": ("london.0", {"S2": 0.0}, "S1 and S2 are positive",
                       "if not (math.isfinite(k) and k > 0 and math.isfinite(w) and w > 0):"),
}


@pytest.mark.parametrize("case", sorted(SLOT_REFUSALS))
def test_each_slot_refusal_refuses_and_its_mutant_is_killed(sp, case):
    name, change, words, line = SLOT_REFUSALS[case]
    d = RW.point(sp)
    d.update({SS.slot_dim(name, k): v for k, v in change.items()})
    with pytest.raises(SR.RouteRefused, match=words):
        _slot_call(SR._slot, sp, d, name)
    m = _edit("_slot", line, "if False:")
    try:
        _slot_call(m, sp, d, name)
        refused = False
    except Exception as e:                          # the mutant may fail downstream; it must not refuse by name
        refused = isinstance(e, SR.RouteRefused) and words in str(e)
    assert not refused


def test_two_ws_sharing_a_column_label_refuse(sp):
    d = RW.point(sp)
    d["london.0.S2"], d["ny_pm.0.S2"] = 1.2345671, 1.2345674
    rt = _route(sp, d)
    with pytest.raises(SR.RouteRefused, match="share a column label"):
        SR.rr_grid(rt)
    m = _edit("rr_grid", "if len(set(labels)) != len(labels):", "if False:")
    assert len(m(rt)) == 3                                  # the mutant's grid holds both, under one label


def test_missing_day_kinds_and_a_bad_fee_refuse(sp, world):
    rt = _route(sp, RW.point(sp))
    kw = RW.build_kw(world["hist"], world["cal"])
    kinds = dict(kw["day_kinds"])
    kinds.pop(world["hist"].days[5])
    with pytest.raises(SR.RouteRefused, match="day kinds are given for every day"):
        SR.build(rt, world["hist"], **{**kw, "day_kinds": kinds})
    with pytest.raises(SR.RouteRefused, match="the fee at stop"):
        SR.build(rt, world["hist"], **{**kw, "fee_for_stop": lambda s: float("nan")})
    m = _edit("_kinds", "if missing:", "if False:")
    with pytest.raises(KeyError):                           # the mutant reaches the missing day itself
        m(world["hist"], kinds)
    mb = _edit("build", "if not (math.isfinite(fee) and fee >= 0):", "if False:")
    out = mb(rt, world["hist"], **{**kw, "fee_for_stop": lambda s: float("nan")})
    assert len(out.trades) and out.trades["fee_micro_eq"].isna().all()   # the mutant lets the NaN fee into the table


def test_a_held_out_history_refuses(sp):
    days = ["2023-12-28", "2024-01-02"]
    arr = tuple(np.full(W.C_FLAT + 1, 1.0) for _ in range(4))
    with pytest.raises(DT.DesignRefused, match="E-208"):
        DT.history_from_arrays(days, {d: arr for d in days})
    hist = T.History.from_arrays(days, ("", ""), *[np.vstack([a, a]) for a in arr])
    with pytest.raises(DT.DesignRefused, match="E-208"):
        SR.trailing(hist, day_kinds={d: "n" for d in days}, cal=RW.calendar_of(["2023-12-28"]))


# ------------------------------------------------------------------------------------------------ one convention


def test_p14s_trigger_on_a_date_is_the_playbooks():
    sl = SR.SlotRoute("x.0", "ny_pm", 0, "p14", 5, "limit", 0, 0, 0.2, 1.0, "with_breakout")
    seen = 0
    for lat in LS.latency_cells("p14"):
        sl = dataclasses.replace(sl, latency=lat)
        for a, b in ((935, 1000), (1080, 1290), (1250, 1300), (1265, 1320), (600, 640)):
            comp = {"trigger": {"source": "p14", "params": {"entry": "limit"}}, "latency": lat}
            assert sl.trigger(a, b) == PB._trigger_on(comp, a, b), (lat, a, b)
            seen += 1
    assert seen == 15
    m = _edit("p14_alerts", "lo = min(max(int(first) - lat, 0), T.P14_LAST)", "lo = min(max(int(first), 0), T.P14_LAST)")
    assert m(1000, 1100, 5) != SR.p14_alerts(1000, 1100, 5)


def test_the_routes_rows_are_design_trades_frame_for_frame(sp, world, built):
    """One component's days with one stop: `design_trades.build_trades` on the spec built by hand (RL3's base cell
    builder, `design_trades.rl3_spec`) gives exactly the route's rows for those days."""
    rt, out = built
    hist, kw = world["hist"], RW.build_kw(world["hist"], world["cal"])
    sl = rt.slots[1]
    trail = SR.trailing(hist, day_kinds=kw["day_kinds"], cal=world["cal"])
    st = SR.stops(rt, trail)[sl.name]
    by: dict[int, list[int]] = {}
    for i, (s, _) in enumerate(st):
        if s is not None:
            by.setdefault(s, []).append(i)
    s, days = max(by.items(), key=lambda kv: len(kv[1]))
    spec = DT.rl3_spec(RW.RL3_PARAMS["kind"], RW.RL3_PARAMS["cutoff"], {"hi": "fade", "lo": "fade"}, s)
    ctx = {i: T.context_for(spec.source, world["cal"], date.fromisoformat(hist.days[i]), i, rules=T.JOURNEY)
           for i in days}
    ref = DT.build_trades(spec, hist, lambda i: ctx[i], day_kinds=kw["day_kinds"], rr_grid=out.rr_grid,
                          fresh_rr=RW.FRESH_RR, fee_micro_eq=RW.FEE, tick_value=RW.TICK_VALUE,
                          market_entry_ticks=RW.ENTRY_TICKS, days=days)
    mine = (out.aux["component"] == sl.name) & out.trades["date"].isin([hist.days[i] for i in days]).to_numpy()
    assert len(ref.trades) > 0 and int(mine.sum()) == len(ref.trades)
    pd.testing.assert_frame_equal(out.trades[mine].reset_index(drop=True), ref.trades.reset_index(drop=True),
                                  check_exact=True)
    keep = [c for c in ref.aux.columns]
    pd.testing.assert_frame_equal(out.aux.loc[mine, keep].reset_index(drop=True), ref.aux.reset_index(drop=True),
                                  check_exact=True)


# ------------------------------------------------------------------------------------------------ the trades


def test_the_table_entries_stops_and_counts(sp, world, built):
    rt, out = built
    t, a = out.trades, out.aux
    assert len(t) > 30 and len(a) == len(t)
    assert set(a["component"]) == {"london.0", "ny_am.0", "ny_pm.0"}
    assert out.rr_grid == (1.0, 1.5, 2.0)
    wins = {d: rt.windows_on(date.fromisoformat(d)) for d in sorted(set(t["date"]))}
    lat = {s.name: s.latency for s in rt.slots}
    for p in range(len(t)):
        r, x = t.iloc[p], a.iloc[p]
        comp, dec, ent = x["component"], int(r["decision_slot_minutes"]), int(r["entry_t"])
        lo, hi = wins[r["date"]][comp]
        live = T.LIVE_0900 if x["source"] == "rl3" else dec + int(lat[comp])
        assert lo <= live <= hi                                  # the order goes live inside the window
        assert ent - 1 >= live and live >= dec + (5 if lat[comp] is None else int(lat[comp]))   # t + L or later
        assert int(r["S"]) == int(x["stop_ticks"]) >= LS.stop_caps()["floor_ticks"]
        assert float(x["rr"]) == {s.name: s.w for s in rt.slots}[comp]
    # the stop is S1's translation: k x T(d), whole ticks half up
    kw = RW.build_kw(world["hist"], world["cal"])
    trail = SR.trailing(world["hist"], day_kinds=kw["day_kinds"], cal=world["cal"])
    di = {d: i for i, d in enumerate(world["hist"].days)}
    for p in range(0, len(t), 7):
        x = a.iloc[p]
        sl = next(s for s in rt.slots if s.name == x["component"])
        T_d = float(trail[sl.s1_session][di[t.iloc[p]["date"]]])
        assert int(x["stop_ticks"]) == V.band_ticks(T_d, sl.k) == int(math.floor(sl.k * T_d / W.TICK + 0.5))
    # counts: every history day either traded or stood aside, every fill a row
    for sl in rt.slots:
        c = out.counts[sl.name]
        assert c["traded_days"] + sum(c["stand_aside"].values()) == len(world["hist"])
        assert c["filled"] == int((a["component"] == sl.name).sum())
    assert out.counts["ny_pm.0"]["stand_aside"]["no_trail"] >= 20            # the first twenty days have no T(d)
    assert sum(out.counts["ny_pm.0"]["stand_aside"].values()) > out.counts["ny_pm.0"]["stand_aside"]["no_trail"]


def test_the_facts_follow_with_each_components_entry_ticks(world, built):
    rt, out = built
    f = SR.facts(out, world["hist"].days, tick_value=RW.TICK_VALUE)
    assert len(f) == len(out.trades)
    for (key, x), p in zip(f.items(), range(len(out.aux))):
        ax, tr = out.aux.iloc[p], out.trades.iloc[p]
        assert x.e_ticks == (RW.ENTRY_TICKS if ax["source"] == "p14" and tr["decision_slot_minutes"] >= 0
                             and next(s for s in rt.slots if s.name == ax["component"]).entry == "market" else 0.0)
        assert x.stop_ticks == int(tr["S"]) and sorted(x.kinds) == list(out.rr_grid)
        assert x.be_open is None and not x.has_move                          # S7 dropped: no breakeven move
        assert x.decision <= x.entry <= x.limit and x.sigma > 0
    m = _edit("facts", "return {key: dataclasses.replace(f, e_ticks=float(x)) for (key, f), x in zip(got.items(), e)}",
              "return got")
    g = m(out, world["hist"].days, tick_value=RW.TICK_VALUE)
    assert any(g[k].e_ticks != f[k].e_ticks for k in f)                      # the mutant's facts differ


def _flat_days(n: int, base: float = 18000.0, half: float = 50.0):
    """n flat days, each a regular-session high of base + half at 10:00 and a low of base - half at 11:00."""
    days = [str(d.date()) for d in pd.bdate_range("2021-02-01", periods=n)]
    arrs = {}
    for d in days:
        o, h, l, c = (np.full(W.C_FLAT + 1, np.nan) for _ in range(4))
        for j in range(1, W.C_FLAT + 1):
            o[j] = h[j] = l[j] = c[j] = base
        for j in range(1, T.RTH_OPEN, 2):                              # overnight closes alternate by a tick
            c[j] = h[j] = base + W.TICK
        h[W.bar_of(10, 0)], l[W.bar_of(11, 0)] = base + half, base - half
        arrs[d] = (o, h, l, c)
    return days, arrs


def _two_barrier(sp, both: bool):
    days, arrs = _flat_days(23)
    o, h, l, c = arrs[days[-1]]
    for j in range(W.bar_of(10, 0), W.C_FLAT + 1):                       # the last day holds at the high after 10:00
        o[j] = h[j] = l[j] = c[j] = 18050.0
    h[W.bar_of(10, 0)] = 18050.0 + W.TICK                                # a tick through the high: the fade sells 18050
    j = W.bar_of(10, 30)
    if both:
        h[j], l[j] = 18050.0 + 21.0, 18050.0 - 21.0                      # stop (+20 pts) and target (-20 pts) in one bar
    else:
        h[j], l[j] = 18050.0, 18050.0 - 21.0                             # the target alone
    hist = DT.history_from_arrays(days, arrs)
    d = RW.with_slot(sp, RW.base_point(sp), "ny_am.0", T1="rl3", T4=None, T5=SS.TICKET, first=30, last=120,
                     S1=0.2, S2=1.0)
    rt = _route(sp, d)
    kw = dict(RW.build_kw(hist, RW.calendar_of(days)), cal=RW.calendar_of(days))
    return SR.build(rt, hist, **kw)


def test_stop_first_on_a_two_barrier_bar(sp):
    both, alone = _two_barrier(sp, True), _two_barrier(sp, False)
    for out in (both, alone):
        last = out.trades[out.trades["date"] == out.trades["date"].max()]
        assert len(last) == 1 and int(last.iloc[0]["S"]) == 80 and last.iloc[0]["side"] == "short"
    assert both.trades.iloc[-1]["o_1"] == "s"                            # both barriers: the stop
    assert alone.trades.iloc[-1]["o_1"] == "t"                           # the positive control: the target


# ------------------------------------------------------------------------------------------------ shift invariance


def _cuts(rt, world, n_days=(25, 45, 47, 48, 50, 70)):
    """(day index, t): each session's first minutes, around the roll (2021-03-12) and the clock change (03-15), and
    the day's own offers' alerts."""
    hist, kw = world["hist"], RW.build_kw(world["hist"], world["cal"])
    out = []
    for i in n_days:
        d = date.fromisoformat(hist.days[i])
        starts = sorted({a for a, _ in rt.windows_on(d).values()})
        recs = SR.decisions(rt, hist, i, cal=world["cal"], day_kinds=kw["day_kinds"], news_windows=None)
        alerts = sorted({r["alert"] for r in recs if r["kind"] == "offer"})
        ts = set(starts) | {s + 1 for s in starts} | set(alerts[:3]) | set(alerts[-2:]) | {T.RTH_OPEN, T.LIVE_0900}
        out += [(i, int(t)) for t in sorted(ts)]
    return out


def _shift_problems(rt, world, cuts, decisions=None):
    dec = decisions or SR.decisions
    hist, b, cal = world["hist"], world["bars"], world["cal"]
    kinds = RW.build_kw(hist, cal)["day_kinds"]
    base = {i: dec(rt, hist, i, cal=cal, day_kinds=kinds, news_windows=None) for i, _ in cuts}
    bad, compared = [], 0
    for k, (i, t) in enumerate(cuts):
        shifted = SB.replace_from(b, RW.ts_of_slot(hist.days[i], t), RW.shift_seed(k))
        h2 = T.History.from_bars(shifted)
        assert h2.days == hist.days
        got = dec(rt, h2, i, cal=cal, day_kinds=kinds, news_windows=None)
        keep = lambda rs: [r for r in rs if r["alert"] <= t]       # noqa: E731
        a, g = keep(base[i]), keep(got)
        compared += len(a)
        if json.dumps(a, sort_keys=True, default=str) != json.dumps(g, sort_keys=True, default=str):
            bad.append((hist.days[i], t))
    return bad, compared


def test_every_decision_is_shift_invariant(sp, world, built):
    rt, _ = built
    cuts = _cuts(rt, world)
    bad, compared = _shift_problems(rt, world, cuts)
    assert bad == [] and len(cuts) >= 40 and compared >= 200
    recs = [r for i, _ in cuts[::5] for r in SR.decisions(rt, world["hist"], i, cal=world["cal"],
                                                           day_kinds=RW.day_kinds(world["hist"]), news_windows=None)]
    sig = [r["sigma"] for r in recs if r["kind"] == "offer" and r["sigma"] is not None]
    st = [r["stop"] for r in recs if r["kind"] == "stop" and r["stop"] is not None]
    assert len(set(sig)) > 5 and len(set(st)) > 3                              # neither all-NaN nor constant


def test_a_trailing_range_reading_its_own_day_is_caught(sp, world, built, monkeypatch):
    rt, _ = built
    m = _edit("trailing", "out[s] = S1R.trailing_ranges(rng[s], ok)",
              "out[s] = S1R.trailing_ranges(np.roll(rng[s], -1), np.roll(ok, -1))")
    monkeypatch.setattr(SR, "trailing", m)
    bad, _ = _shift_problems(rt, world, [(i, T.RTH_OPEN) for i in (30, 40, 50, 60)])
    assert bad, "the look-ahead mutant passed the shift test"


def test_a_limit_level_read_at_its_alerts_bar_is_caught(sp, world, built, monkeypatch):
    rt, _ = built
    real = T._limit_level
    monkeypatch.setattr(T, "_limit_level", lambda o, c, alert: (float(c[int(alert) + 1]), "")
                        if math.isfinite(float(c[int(alert) + 1])) else real(o, c, alert))
    cuts = [(i, t) for i, t in _cuts(rt, world, (45, 47, 50)) if t >= 1078]    # the NY PM limit's alerts among them
    bad, _ = _shift_problems(rt, world, cuts)
    assert bad, "the look-ahead mutant passed the shift test"


# ------------------------------------------------------------------------------------------------ S1 against Q-171


def test_the_trailing_range_is_s1_ranges_on_the_vendored_arrays():
    r = subprocess.run([sys.executable, str(ROOT / "tests" / "survey_route_child.py"), "trailing"], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8", timeout=900)
    lines = [ln for ln in r.stdout.splitlines() if ln.startswith("{")]
    assert r.returncode == 0 and lines, r.stderr[-3000:]
    out = json.loads(lines[-1])
    assert out["equal"] is True and out["finite"] >= 200 and out["sessions"] == 4, out
    assert out["mutant_equal"] is False, out                                   # the look-ahead mutant differs
