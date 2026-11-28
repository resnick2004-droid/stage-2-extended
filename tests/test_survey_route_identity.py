"""Q-215: the plumbing of the route's heavy identity (`identity/survey_route_identity.py`) on synthetic inputs only --
its two comparisons run in process on synthetic walker arrays and a synthetic space (`tests/survey_route_world.py`),
each shown to hold on agreeing inputs and to fail on a planted disagreement: I-1 on other day kinds; I-2's
fills on a route-side fault, its stop groups on a planted walk, its record on another hash or count. The real-bar run is the lead's, under
`run.lock`:

    python scripts/run_clean.py --name q215-identity --hours 1 --mem-gb 3 --task Q-215 -- python identity/survey_route_identity.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import design_trades as DT  # noqa: E402
from extended import triggers as T  # noqa: E402
from extended import walker as W  # noqa: E402

import survey_route_world as RW  # noqa: E402

_spec = importlib.util.spec_from_file_location("survey_route_identity_light", ROOT / "identity" / "survey_route_identity.py")
ID = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ID)


@pytest.fixture(scope="module")
def toy():
    b = RW.bars()
    h = T.History.from_bars(b)
    days = list(h.days)
    arrays = {d: tuple(x[i][:W.C_FLAT + 1].copy() for x in (h.o, h.h, h.l, h.c)) for i, d in enumerate(days)}
    hist = DT.history_from_arrays(days, arrays)
    return {"days": days, "arrays": arrays, "hist": hist, "cal": RW.fake_sources(b), "kinds": RW.day_kinds(hist)}


def test_i1_holds_on_agreeing_inputs_and_fails_on_other_day_kinds(toy):
    ok = ID.trailing_identity(toy["days"], toy["arrays"], toy["kinds"], toy["cal"], (), ())
    assert ok["holds"] is True and ok["walked_status_disagreements"] == 0 and ok["days"] == len(toy["days"])
    bad_kinds = dict(toy["kinds"])
    for d in toy["days"][5:25:3]:
        bad_kinds[d] = "e"                                        # seven walked days called early closes
    bad = ID.trailing_identity(toy["days"], toy["arrays"], bad_kinds, toy["cal"], (), ())
    assert bad["holds"] is False and bad["walked_status_disagreements"] == 7


def _early(toy, cutoff):
    """`early_look.build`'s output, stood in on the toys: its spec at its 50-tick stop, its facts, its job blocks'
    sides, its trade count, counts and a trades hash."""
    import hashlib
    from datetime import date
    from types import SimpleNamespace

    spec = DT.rl3_spec("pd", cutoff, {"hi": "fade", "lo": "fade"}, 50)
    hist = toy["hist"]
    ctx = {i: T.context_for(spec.source, toy["cal"], date.fromisoformat(d), i, rules=spec.rules)
           for i, d in enumerate(hist.days)}
    out = DT.build_trades(spec, hist, lambda i: ctx[i], day_kinds=toy["kinds"], rr_grid=(1.0,), fresh_rr=1.0,
                          fee_micro_eq=RW.FEE, tick_value=RW.TICK_VALUE, market_entry_ticks=RW.ENTRY_TICKS)
    facts = DT.facts_for(out.trades, out.aux, hist.days, tick_value=RW.TICK_VALUE, rr_cols=(1.0,), entry_ticks=0.0)
    blocks = []
    for d in hist.days:
        g = out.trades[out.trades["date"] == d]
        blocks.append(SimpleNamespace(sides=np.where(g["side"].to_numpy() == "long", 1, -1)))
    sha = hashlib.sha256(out.trades.to_csv(index=False).encode("utf-8")).hexdigest()
    return {"dates": tuple(hist.days), "facts": facts, "blocks": blocks, "trades_sha256": sha,
            "trades": int(len(out.trades)), "counts": json.loads(json.dumps(out.counts, sort_keys=True))}


def _record(early):
    return {k: early[k] for k in ("trades_sha256", "trades", "counts")}


def _run(toy, sp, *, cutoff, early, record, route_side=None):
    return ID.route_identity(sp, toy["hist"], toy["kinds"], toy["cal"], kind="pd", cutoff=cutoff,
                             rule={"hi": "fade", "lo": "fade"}, early=early, record=record,
                             fee_for_stop=lambda s: RW.FEE + s / 1000.0, tick_value=RW.TICK_VALUE,
                             market_entry_ticks=RW.ENTRY_TICKS, tick=W.TICK, route_side=route_side)


@pytest.fixture(scope="module")
def sp1():
    return RW.space({"ny_am": 1})


def test_i2_holds_on_the_early_looks_cell(toy, sp1):
    cutoff = int(ID._early_look().CUTOFF)
    early = _early(toy, cutoff)
    ok = _run(toy, sp1, cutoff=cutoff, early=early, record=_record(early))
    assert ok["holds"] is True and ok["fills_equal"] is True and ok["record_problems"] == [], ok
    assert ok["route_trades"] > 5 and ok["route_trades"] == ok["early_trades_on_route_days"]
    assert ok["stop_groups"] > 3 and ok["stop_groups_unequal"] == []
    assert ok["early_trades"] > ok["route_trades"]                    # the first twenty days stand aside (no T(d))
    assert ok["stand_aside_equal"] is True and ok["stand_aside_apart"]["no_trail"] >= 20


def test_i2s_stand_aside_count_fails_on_a_planted_stop_rule(toy, sp1, monkeypatch):
    """m-3: the route's floor planted higher (its stand-aside rule, not the trailing range): the days it stands aside
    no longer equal those computed apart from `survey_route.stops`."""
    import inspect
    import textwrap

    from extended import survey_route as SR

    src = textwrap.dedent(inspect.getsource(SR.stop_on))
    old = 'if x < int(caps["floor_ticks"]) * tick:'
    assert src.count(old) == 1
    ns: dict = {}
    exec(compile("from __future__ import annotations\n" + src.replace(old, 'if x < (int(caps["floor_ticks"]) + 60) * '
                                                                            'tick:'), SR.__file__, "exec"),
         SR.__dict__, ns)
    monkeypatch.setattr(SR, "stop_on", ns["stop_on"])
    cutoff = int(ID._early_look().CUTOFF)
    early = _early(toy, cutoff)
    bad = _run(toy, sp1, cutoff=cutoff, early=early, record=_record(early))
    assert bad["holds"] is False and bad["stand_aside_equal"] is False, bad


def test_i2s_fill_comparison_fails_on_a_planted_route_fault(toy, sp1):
    """m-5: the route's side rule planted `break` (the references keep `fade`): the fills differ, so do the groups."""
    cutoff = int(ID._early_look().CUTOFF)
    early = _early(toy, cutoff)
    bad = _run(toy, sp1, cutoff=cutoff, early=early, record=_record(early), route_side="break")
    assert bad["holds"] is False and bad["fills_equal"] is False and bad["stop_groups_unequal"]


def test_i2s_stop_and_outcome_comparison_fails_on_a_planted_walk(toy, sp1, monkeypatch):
    """m-5: the route walked one tick wider than its stop: the fills hold, the stop groups' frames do not."""
    import inspect
    import textwrap

    from extended import survey_route as SR

    src = textwrap.dedent(inspect.getsource(SR.build))
    old = "sl.side_of(trig), int(s), T.JOURNEY,"
    assert src.count(old) == 1
    ns: dict = {}
    exec(compile("from __future__ import annotations\n" + src.replace(old, "sl.side_of(trig), int(s) + 1, T.JOURNEY,"),
                 SR.__file__, "exec"), SR.__dict__, ns)
    monkeypatch.setattr(SR, "build", ns["build"])
    cutoff = int(ID._early_look().CUTOFF)
    early = _early(toy, cutoff)
    bad = _run(toy, sp1, cutoff=cutoff, early=early, record=_record(early))
    assert bad["holds"] is False and bad["fills_equal"] is True and bad["stop_groups_unequal"]


def test_i2s_record_check_fails_on_another_hash_count_or_none(toy, sp1):
    cutoff = int(ID._early_look().CUTOFF)
    early = _early(toy, cutoff)
    for k, v in (("trades_sha256", "0" * 64), ("trades", early["trades"] + 1)):
        bad = _run(toy, sp1, cutoff=cutoff, early=early, record={**_record(early), k: v})
        assert bad["holds"] is False and any(x.startswith(k) for x in bad["record_problems"]), bad
    assert _run(toy, sp1, cutoff=cutoff, early=early, record=None)["holds"] is False
    other = next(c for c in T.RL3_CUTOFFS if c < cutoff)             # the early look at another cutoff: fills differ
    assert _run(toy, sp1, cutoff=cutoff, early=_early(toy, other), record=_record(early))["fills_equal"] is False


def test_the_point_is_the_early_looks_cell_in_the_space(toy):
    sp = RW.space({"ny_am": 1})
    d = ID.rl3_point(sp)
    assert sp.check(d) is None
    assert d["ny_am.0.T1"] == "rl3" and d["T7"] == "off"
    for day in sp.days[::50]:
        a = sp.starts(day)["ny_am"]
        assert d["ny_am.0.first"] <= T.LIVE_0900 - a <= d["ny_am.0.last"]
