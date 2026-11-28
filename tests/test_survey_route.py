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

import survey_route_policies as PL  # noqa: E402
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
    ref = DT.build_trades(spec, hist, lambda i: ctx[i], day_kinds=kw["day_kinds"], rr_grid=(sl.w,),
                          fresh_rr=sl.w, fee_micro_eq=RW.FEE, tick_value=RW.TICK_VALUE,
                          market_entry_ticks=RW.ENTRY_TICKS, days=days)
    mine = (out.aux["component"] == sl.name) & out.trades["date"].isin([hist.days[i] for i in days]).to_numpy()
    assert len(ref.trades) > 0 and int(mine.sum()) == len(ref.trades)
    pd.testing.assert_frame_equal(out.trades.loc[mine, list(ref.trades.columns)].reset_index(drop=True),
                                  ref.trades.reset_index(drop=True), check_exact=True)
    others = [c for c in out.trades.columns if c not in ref.trades.columns]
    assert others and out.trades.loc[mine, others].isna().all().all()     # every other w's block NaN on its rows
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
        assert x.stop_ticks == int(tr["S"]) and x.entry == int(tr["entry_t"])
        assert list(x.kinds) == [float(ax["rr"])] and list(x.walked) == [float(ax["rr"])]   # its own w only (B-1)
        assert x.be_open is None and not x.has_move                          # S7 dropped: no breakeven move
        assert x.decision <= x.entry <= x.limit and x.sigma > 0
    m = _edit("facts", "rr_cols=(w,), entry_ticks=float(e.pop()))", "rr_cols=(w,), entry_ticks=0.0)")
    g = m(out, world["hist"].days, tick_value=RW.TICK_VALUE)
    assert any(g[k].e_ticks != f[k].e_ticks for k in f)                      # the mutant's facts differ


# ------------------------------------------------------------------------------------------------ B-1: each row its own w


def test_every_row_is_live_at_its_own_w_only(world, built):
    """B-1 (a): each trade's outcome, cost, MAE, exit and kind columns at another component's w are NaN, its own w's
    live, its `exit_t` and `flat` its own w's; the planted unmasked walk (every slot at the whole grid) and the
    planted `exit_t` at the engine's combine R are caught, and the facts refuse an unmasked table."""
    rt, out = built
    hist, kw = world["hist"], RW.build_kw(world["hist"], world["cal"])
    t, a = out.trades, out.aux
    assert SR.masked_problems(out) == []
    for R in out.rr_grid:
        other = a["rr"].to_numpy(float) != R
        assert other.any() and t.loc[other, f"r_{R:g}"].isna().all() and t.loc[other, f"o_{R:g}"].isna().all()
        assert t.loc[~other, f"r_{R:g}"].notna().all()
        assert (t.loc[~other, "exit_t"].to_numpy(float) == t.loc[~other, f"exit_t_{R:g}"].to_numpy(float)).all()
    m = _edit("build", "day_kinds=day_kinds, rr_grid=own,", "day_kinds=day_kinds, rr_grid=grid,")
    bad = m(rt, hist, **kw)
    assert any("at another component's w" in x for x in SR.masked_problems(bad))
    with pytest.raises(SR.RouteRefused, match="not masked"):
        SR.facts(bad, hist.days, tick_value=RW.TICK_VALUE)
    src = textwrap.dedent(inspect.getsource(SR.build))                       # the code before the ruling, both edits
    old = src.replace("day_kinds=day_kinds, rr_grid=own,", "day_kinds=day_kinds, rr_grid=grid,").replace(
        "fresh_rr=own[0], fee_micro_eq=fee,", f"fresh_rr={RW.FRESH_RR!r}, fee_micro_eq=fee,")
    ns: dict = {}
    exec(compile("from __future__ import annotations\n" + old, SR.__file__, "exec"), SR.__dict__, ns)
    probs = SR.masked_problems(ns["build"](rt, hist, **kw))
    assert any("exit_t is not the own w's" in x for x in probs)              # exit_t at the combine R, caught


def _race_log(out, dates, shift=None):
    """A race log as `three_way_baseline` writes it (block day `i`, index `j`, the R read), every trade taken at
    its own w; `shift` plants one trade read at another component's w."""
    own = SR.own_rr(out, dates)
    log = [{"i": i, "j": j, "R": w, "law": "race"} for (i, j), w in own.items()]
    if shift is not None:
        k = next(n for n, r in enumerate(log) if r["R"] != shift)
        log[k] = dict(log[k], R=shift)
    return log, own


def test_every_taken_trade_was_read_at_its_own_w(world, built):
    """B-1 (b): the refusing check where the table meets the engine, its keys the facts' own; a trade the engine read
    at another component's w is refused, and the check with its comparison removed lets it through."""
    rt, out = built
    days = world["hist"].days
    f = SR.facts(out, days, tick_value=RW.TICK_VALUE)
    log, own = _race_log(out, days)
    assert set(own) == set(f) and all(list(f[k].kinds) == [own[k]] for k in f)
    assert SR.check_taken_rr(log, own) == len(f)
    bad, _ = _race_log(out, days, shift=2.0)
    with pytest.raises(SR.RouteRefused, match="not its own w"):
        SR.check_taken_rr(bad, own)
    with pytest.raises(SR.RouteRefused, match="not one of the route's"):
        SR.check_taken_rr([{"i": 0, "j": 99, "R": 1.0}], own)
    m = _edit("check_taken_rr", "if R is None or not abs(float(R) - own[key]) <= RR_TOL:", "if R is None:")
    assert m(bad, own) == len(bad)                                          # the mutant takes the wrong R


@pytest.fixture(scope="module")
def one_w(sp, world):
    """One-component tables: RL3 at w = 1.5, and at w = 1 (where `r_1` is every trade's own outcome)."""
    out = {}
    for w in (1.5, 1.0):
        d = RW.with_slot(sp, RW.base_point(sp), "ny_am.0", T1="rl3", T4=None, T5=SS.TICKET, first=30, last=120,
                         S1=0.2, S2=w)
        out[w] = SR.build(_route(sp, d), world["hist"], **RW.build_kw(world["hist"], world["cal"]))
    return out


def test_the_policy_must_read_every_trade_at_its_own_w(built, one_w):
    """B-1 (b), (c2): the policy's own leaves against each trade's own w. A one-component design (w = 1.5) is admitted
    under leaves at its w, with a flip leaf exempt; refused under the planted mixed policy (a combine leaf at its w, a
    funded leaf at rr=None -- the pnl channel, NaN off w = 1), a leaf at another R, a collect leaf and a policy with no
    trading leaf; at w = 1 the rr=None leaf reads its own outcome and is admitted. Three components' w are refused."""
    one, one1 = one_w[1.5], one_w[1.0]
    rt, out = built
    L = PL.Leaf
    ok = SR.check_policy_reads(PL.policy(L("c", 500.0, 1.5), L("f", 400.0, 1.5)), one)
    assert ok["reads"] == ["c", "f"] and ok["flip_exempt"] == [] and one.trades["r_1.5"].notna().all()
    flip = SR.check_policy_reads(PL.policy(L("c", 500.0, 1.5), L("flip", 300.0, 3.0, source="flip")), one)
    assert flip["reads"] == ["c"] and flip["flip_exempt"] == ["flip"]          # a flip leaf reads no table
    sits = SR.check_policy_reads(PL.policy(L("c", 500.0, 1.5), L("sit", 0.0, None, max_trades=0)), one)
    assert sits["reads"] == ["c"]                                              # a sitting leaf trades nothing
    mixed = PL.policy(L("c", 500.0, 1.5), L("f", 400.0, None))
    cases = ((mixed, "pnl channel"), (PL.policy(L("c", 500.0, 1.0), L("f", 400.0, 1.5)), "asks for R 1.0"),
             (PL.policy(L("c", 500.0, 1.5), L("k", 400.0, None, source="collect")), "collect leaf"),
             (PL.policy(L("c", 0.0, 1.5, max_trades=0), L("f", 0.0, None, abandon=True)), "no trading leaf"))
    for pol, words in cases:
        with pytest.raises(SR.RouteRefused, match=words):
            SR.check_policy_reads(pol, one)
    assert one1.trades["r_1"].notna().all()                                    # at w = 1, r_1 is the own outcome
    assert SR.check_policy_reads(PL.policy(L("c", 500.0, 1.0), L("f", 400.0, None)),
                                 one1)["reads"] == ["c", "f"]
    with pytest.raises(SR.RouteRefused, match="components' w differ"):
        SR.check_policy_reads(PL.policy(L("c", 500.0, 1.5), L("f", 400.0, 1.5)), out)
    with pytest.raises(SR.RouteRefused, match="not a risk policy"):
        SR.check_policy_reads([1.5], one)                                      # round 1's float list: refused
    # the mutants: round 1's blind spot (a leaf without an R skipped), the flip exemption removed, several w admitted
    m = _edit("check_policy_reads", 'refuse_pnl_reader(f"{where} at rr=None (the log\'s own outcome)", rt_trades)',
              "continue")
    assert m(mixed, one)["reads"] == ["c"]                                     # the mixed policy let through
    mf = _edit("check_policy_reads", "if src == FLIP_SOURCE:", "if False:")
    with pytest.raises(SR.RouteRefused, match="unknown leaf source"):
        mf(PL.policy(L("c", 500.0, 1.5), L("flip", 300.0, 3.0, source="flip")), one)
    mw = _edit("check_policy_reads", "if len(ws) != 1:", "if False:")
    assert mw(PL.policy(L("c", 500.0, 1.0), L("f", 400.0, 1.0)), out)["reads"] == ["c", "f"]


def _acct(script, rt, cls=PL.TierSizedDraw, rr=1.5):
    tally: dict = {}
    draw = SR.AccountingDraw(cls(list(script), _rr=rr), tally, rt)
    for _ in script:
        draw(1, 0, 0, np.array([1000.0]))
    return tally


def test_the_race_accounts_for_every_offered_trade(one_w):
    """B-1 (c2): every trade offered to a trading leaf is taken or stood aside by a named rule; a trade dropped with a
    NaN outcome, or with no outcome at the state's R, refuses; a draw reading the pnl channel (not a `TierSizedDraw`,
    or one at rr=None) refuses off w = 1 and is admitted at w = 1. Each refusal's mutant lets its case through."""
    one, one1 = one_w[1.5], one_w[1.0]
    t = _acct(["none", "taken", "stood_aside", "unsized", "taken"], one)
    assert t == {"no_trade": 1, "offered": 4, "taken": 2, "stood_aside": 1, "unsized": 1}
    for case, words in (("nan", "NaN outcome"), ("no_outcome", "no outcome at the state's R")):
        with pytest.raises(SR.RouteRefused, match=words):
            _acct(["taken", case], one)
    with pytest.raises(SR.RouteRefused, match="SharedDayDraw reads the vendored pnl channel"):
        _acct(["taken"], one, cls=PL.SharedDayDraw)
    with pytest.raises(SR.RouteRefused, match="rr=None reads the vendored pnl channel"):
        _acct(["taken"], one, rr=None)
    assert _acct(["taken"], one1, cls=PL.SharedDayDraw)["taken"] == 1         # at w = 1 the channel is the own one
    assert _acct(["taken"], one1, rr=None)["taken"] == 1
    real = SR.AccountingDraw.__call__
    for line, script, kw, words in (("if not math.isfinite(pnl):", ["nan"], {}, "NaN outcome"),
                                    ('if d["no_outcome"]:', ["no_outcome"], {}, "no outcome at the state's R"),
                                    ('if getattr(inner, "_rr", 0.0) is None:', ["taken"], {"rr": None}, "rr=None")):
        src = textwrap.dedent(inspect.getsource(real))
        assert src.count(line) == 1, line
        ns: dict = {}
        exec(compile("from __future__ import annotations\n" + src.replace(line, "if False:"), SR.__file__, "exec"),
             SR.__dict__, ns)
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(SR.AccountingDraw, "__call__", ns["__call__"])
            try:
                _acct(script, one, **kw)
                refused = False
            except SR.RouteRefused as e:
                refused = words in str(e)
            assert not refused, line                                           # the mutant no longer refuses so
    src = textwrap.dedent(inspect.getsource(SR.AccountingDraw.__init__))
    line = 'if type(inner).__name__ != "TierSizedDraw":'
    ns = {}
    exec(compile("from __future__ import annotations\n" + src.replace(line, "if False:"), SR.__file__, "exec"),
         SR.__dict__, ns)
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(SR.AccountingDraw, "__init__", ns["__init__"])
        assert _acct(["taken"], one, cls=PL.SharedDayDraw)["taken"] == 1


def test_the_route_never_hands_its_table_to_a_pnl_reader(one_w):
    """m-2: `route_simulate` refuses `outcome="vendored"` off w = 1 (before any engine is built), and its mutant
    goes on to the engine."""
    one = one_w[1.5]
    with pytest.raises(SR.RouteRefused, match="outcome='vendored' reads the vendored pnl channel"):
        SR.route_simulate(one, [], {}, {}, 0, (0,), 1, dates=(), outcome="vendored")
    m = _edit("route_simulate", 'if kw.get("outcome", "race") == "vendored":', "if False:")
    with pytest.raises(Exception) as e:                                       # the mutant reaches the policy check
        m(one, [], {"path": {"risk_policy": None}}, {}, 0, (0,), 1, dates=(), outcome="vendored")
    assert "outcome='vendored'" not in str(e.value)
    with pytest.raises(SR.RouteRefused, match="gate.mean_r reads"):
        SR.refuse_pnl_reader("gate.mean_r", one)
    SR.refuse_pnl_reader("gate.mean_r", one_w[1.0])                           # at w = 1: admitted


def test_the_engine_takes_the_one_component_design_at_its_own_w():
    """B-1 (c2) end to end (a child process, the vendored engine on `early_look`'s toy job): the trades are taken,
    every lane's own log passes `check_taken_rr` (its records moved off the own w, or off the table, refused), the
    vendored `no_outcome` is 0 and nothing is dropped with a NaN; the planted mixed policy is refused, round 1's float
    check admits it; a combine leaf at rr=None run past the policy check is refused by the accounting."""
    r = subprocess.run([sys.executable, str(ROOT / "tests" / "survey_route_child.py"), "race"], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8", timeout=900)
    lines = [ln for ln in r.stdout.splitlines() if ln.startswith("{")]
    assert r.returncode == 0 and lines, r.stderr[-3000:]
    out = json.loads(lines[-1])
    assert out["ok"] is True and out["taken"] > 0 and sum(out["logged"]) >= out["taken"], out
    assert out["no_outcome"] == 0 and out["nan_dropped"] == 0 and all(out["log_refusals"].values()), out
    assert out["mixed_refused"] and out["round1_admits_mixed"] and out["accounting_refused"], out


# ------------------------------------------------------------------------------------------------ the minor findings


def test_the_side_rules_and_source_parameters_are_in_the_provenance_and_the_id(sp):
    """m-2: RL3's kind and cutoff and the side rules a point uses are written into the provenance and change the
    route's design id (the point's own id beside, unchanged)."""
    d = RW.point(sp)
    a = _route(sp, d)
    other_cut = next(c for c in T.RL3_CUTOFFS if c != RW.RL3_PARAMS["cutoff"])
    b = _route(sp, d, source_params={"rl3": {**RW.RL3_PARAMS, "cutoff": other_cut}})
    c = _route(sp, d, side_rules={**RW.SIDE_RULES, "p14": "against_breakout"})
    assert json.loads(a.provenance["route.source_params"]) == {"rl3": RW.RL3_PARAMS}
    assert json.loads(a.provenance["route.side_rules"]) == RW.SIDE_RULES
    assert len({a.design_id, b.design_id, c.design_id}) == 3 and a.point_id == b.point_id == c.point_id
    assert a.design_id != a.point_id == SS.design_id(d)
    m = _edit("route", 'did = SS.design_id({**design, "route.side_rules": rules, "route.source_params": params})',
              "did = SS.design_id(design)")
    kw = {"side_rules": RW.SIDE_RULES}
    assert m(sp, d, source_params={"rl3": RW.RL3_PARAMS}, **kw).design_id == \
        m(sp, d, source_params={"rl3": {**RW.RL3_PARAMS, "cutoff": other_cut}}, **kw).design_id


def _edit_mod(mod, fn_name: str, old: str, new: str):
    orig = getattr(mod, fn_name)
    src = textwrap.dedent(inspect.getsource(orig))
    assert src.count(old) == 1, (fn_name, old)
    ns: dict = {}
    exec(compile("from __future__ import annotations\n" + src.replace(old, new), mod.__file__, "exec"), mod.__dict__,
         ns)
    return ns[fn_name]


def test_the_survey_never_learns_a_route_refusal_as_an_infeasible_cell(sp):
    """m-3: a runner raising `RouteRefused` is not one of the survey's recorded refusals (`survey._Refused`, which
    `read_all` passes over and records as a refused cell): it propagates and stops the run. The mutant that catches
    it as a refused cell swallows it."""
    from types import SimpleNamespace

    from extended import survey as SV

    assert not issubclass(SR.RouteRefused, SV._Refused)

    def runner(schedule, protocol):
        raise SR.RouteRefused("REFUSED: T7 = 'admit' -- the route maps only ('off',)")

    ctx = SimpleNamespace(E=SimpleNamespace(SS=SS), memo={}, runner=runner, build_schedule=lambda d: d,
                          protocol=SimpleNamespace(seeds=(0,)), readings=[])
    with pytest.raises(SR.RouteRefused, match="T7"):
        SV.read_all(ctx, [RW.point(sp)], "survey")
    m = _edit_mod(SV, "read_all", "        except _Refused:\n            continue",
                  "        except (_Refused, ValueError):\n            continue")
    m(ctx, [RW.point(sp)], "survey")                                        # the mutant swallows it as a refused cell
    assert ctx.readings == []


def test_the_tick_the_overrides_and_a_missing_s2_refuse(sp, world, built):
    """m-8: a tick other than the one `band_ticks` rounds on, a trailing range of another history's length or
    sessions, caps other than `lever_space.stop_caps()`, a space without S2, and a held-out day under `decisions` with
    a trailing range passed: each refuses by name, each with its mutant."""
    rt, _ = built
    hist, kw = world["hist"], RW.build_kw(world["hist"], world["cal"])
    with pytest.raises(SR.RouteRefused, match="band_ticks rounds on"):
        SR.stop_on(0.2, 80.0, LS.stop_caps(), tick=0.5)
    m = _edit("stop_on", "if float(tick) != float(V.TICK):", "if False:")
    assert m(0.2, 200.0, LS.stop_caps(), tick=0.5)[0] is not None
    with pytest.raises(SR.RouteRefused, match="band_ticks rounds on"):
        SR.build(rt, hist, **kw, tick=0.5)                                  # build hands its tick to the stops
    trail = SR.trailing(hist, day_kinds=kw["day_kinds"], cal=world["cal"])
    short = {k: v[:-1] for k, v in trail.items()}
    with pytest.raises(SR.RouteRefused, match="trailing range passed"):
        SR.build(rt, hist, **kw, trail=short)
    with pytest.raises(SR.RouteRefused, match="trailing range passed"):
        SR.decisions(rt, hist, 30, cal=world["cal"], day_kinds=kw["day_kinds"], news_windows=None,
                     trail={k: v for k, v in trail.items() if k != "asia"})
    mt = _edit("check_trail", "if bad:", "if False:")
    assert mt(short, hist) is short
    caps = dict(LS.stop_caps(), floor_ticks=LS.stop_caps()["floor_ticks"] - 1)
    with pytest.raises(SR.RouteRefused, match="not lever_space.stop_caps"):
        SR.stops(rt, trail, caps)
    mc = _edit("check_caps", "if any(k not in caps or caps[k] != real[k] for k in keys):", "if False:")
    assert mc(caps) is caps
    d = RW.point(sp)
    nos2 = dataclasses.replace(sp, dims=tuple(x for x in sp.dims if x.lever != "S2"))
    d2 = {k: v for k, v in d.items() if not k.endswith(".S2")}
    with pytest.raises(SR.RouteRefused, match="no reward-to-risk: S2 is not a lever"):
        _route(nos2, d2)
    ms = _edit("_slot", 'if SS.slot_dim(name, "S2") not in space.names() or g("S2") is None:', "if False:")
    with pytest.raises(TypeError):                                          # the mutant crashes, unnamed
        ms(nos2, d2, next(x for x in nos2.slots if x.name == "london.0"), 0, RW.SIDE_RULES, {"rl3": RW.RL3_PARAMS})
    arr = tuple(np.full((1, W.C_FLAT + 1), 1.0) for _ in range(4))
    late = T.History.from_arrays(["2024-01-02"], [""], *arr)
    lt = {k: np.full(1, np.nan) for k in trail}
    with pytest.raises(DT.DesignRefused, match="E-208"):
        SR.decisions(rt, late, 0, cal=world["cal"], day_kinds={"2024-01-02": "n"}, news_windows=None, trail=lt)
    md = _edit("decisions", "    DT.check_search_days(hist.days)\n", "")
    with pytest.raises(Exception) as e:                                     # the mutant goes on past the held-out day
        md(rt, late, 0, cal=world["cal"], day_kinds={"2024-01-02": "n"}, news_windows=None, trail=lt)
    assert "E-208" not in str(e.value)


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


def test_mixed_stops_and_fees_go_through_the_vendored_pad_and_gate_blocks():
    """m-4: the route's table, a stop a day and a fee a stop, through the vendored `pad` and `gate_blocks` (a child
    process): each block trade's risk a contract, fee, own-w outcome and exit are its row's, every other w NaN, the
    facts align with the blocks; a planted fee and stop on two rows are caught."""
    r = subprocess.run([sys.executable, str(ROOT / "tests" / "survey_route_child.py"), "gate"], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8", timeout=900)
    lines = [ln for ln in r.stdout.splitlines() if ln.startswith("{")]
    assert r.returncode == 0 and lines, r.stderr[-3000:]
    out = json.loads(lines[-1])
    assert out["ok"] is True and out["aligned"] is True and out["problems"] == [], out
    assert out["stops"] > 10 and out["fees"] > 10 and len(out["control_caught"]) >= 2, out


def test_a_tree_without_w42_r2_fails_the_survey_world_never_skips(tmp_path, monkeypatch):
    """m-5 (the red team's, round 2): `tests/survey_world.py` on a tree missing a W42-R2 file fails (`pytest.fail`),
    never skips; the mutant that skips is told apart."""
    import survey_world as SW

    monkeypatch.setattr(SW, "_W42", None)
    monkeypatch.setattr(SW, "ROOT", tmp_path)
    with pytest.raises(pytest.fail.Exception, match="never skips"):
        SW.load_w42(patch_shas=False)
    src = textwrap.dedent(inspect.getsource(SW.load_w42))
    assert src.count("pytest.fail(") == 1
    ns: dict = {}
    exec(compile("from __future__ import annotations\n" + src.replace("pytest.fail(", "pytest.skip(").replace(
        ", pytrace=False)", ")"), SW.__file__, "exec"), SW.__dict__, ns)
    with pytest.raises(pytest.skip.Exception):                               # the mutant skips: not a failure
        ns["load_w42"](patch_shas=False)
