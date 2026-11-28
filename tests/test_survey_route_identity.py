"""Q-215: the plumbing of the route's heavy identity (`identity/survey_route_identity.py`) on synthetic inputs only --
its two comparisons run in process on synthetic walker arrays and a synthetic space (`tests/survey_route_world.py`),
each shown to hold on agreeing inputs and to fail on a planted disagreement. The real-bar run is the lead's, under
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
    spec = DT.rl3_spec("pd", cutoff, {"hi": "fade", "lo": "fade"}, 50)
    hist = toy["hist"]
    ctx = {i: T.context_for(spec.source, toy["cal"], __import__("datetime").date.fromisoformat(d), i, rules=spec.rules)
           for i, d in enumerate(hist.days)}
    out = DT.build_trades(spec, hist, lambda i: ctx[i], day_kinds=toy["kinds"], rr_grid=(1.0,), fresh_rr=RW.FRESH_RR,
                          fee_micro_eq=RW.FEE, tick_value=RW.TICK_VALUE, market_entry_ticks=RW.ENTRY_TICKS)
    return {"trades": int(len(out.trades)), "counts": json.loads(json.dumps(out.counts, sort_keys=True))}


def _run(toy, sp, *, cutoff, record):
    return ID.route_identity(sp, toy["hist"], toy["kinds"], toy["cal"], kind="pd", cutoff=cutoff,
                             rule={"hi": "fade", "lo": "fade"}, early_stop=50, fee_for_stop=lambda s: RW.FEE,
                             fresh_rr=RW.FRESH_RR, tick_value=RW.TICK_VALUE, market_entry_ticks=RW.ENTRY_TICKS,
                             tick=W.TICK, record=record)


def test_i2_holds_on_the_early_looks_cell_and_fails_on_a_planted_disagreement(toy):
    sp = RW.space({"ny_am": 1})
    cutoff = int(ID._early_look().CUTOFF)
    rec = _early(toy, cutoff)
    ok = _run(toy, sp, cutoff=cutoff, record=rec)
    assert ok["holds"] is True and ok["route_trades"] > 5 and ok["route_trades"] == ok["early_trades_on_route_days"]
    assert ok["early_trades"] > ok["route_trades"]                    # the first twenty days stand aside (no T(d))
    other = next(c for c in T.RL3_CUTOFFS if c < cutoff)
    assert _run(toy, sp, cutoff=other, record=_early(toy, other))["holds"] is True
    # planted: the route at one cutoff against the record of another -- the fills or the record differ
    bad = _run(toy, sp, cutoff=other, record=rec)
    assert bad["holds"] is False and bad["fills_equal"] is True and not all(bad["record_equal"].values())
    assert _run(toy, sp, cutoff=cutoff, record=None)["holds"] is False    # no record, no identity
    off = dict(rec, trades=rec["trades"] + 1)
    assert _run(toy, sp, cutoff=cutoff, record=off)["holds"] is False


def test_the_point_is_the_early_looks_cell_in_the_space(toy):
    sp = RW.space({"ny_am": 1})
    d = ID.rl3_point(sp)
    assert sp.check(d) is None
    assert d["ny_am.0.T1"] == "rl3" and d["T7"] == "off"
    for day in sp.days[::50]:
        a = sp.starts(day)["ny_am"]
        assert d["ny_am.0.first"] <= T.LIVE_0900 - a <= d["ny_am.0.last"]
