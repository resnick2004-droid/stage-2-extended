"""The child process of `tests/test_survey_route.py` (Q-215): the vendored tree on its path, synthetic bars only
(`tests/survey_route_world.py`), never the bar store.

    python tests/survey_route_child.py trailing
    python tests/survey_route_child.py gate

`gate` (the red team's m-4): the route's table for the tests' three-component point, with a stop of its own a day
(S1) and a fee a stop (a toy schedule), through the vendored `zero_edge_decomposition.pad` and
`score_fv3_grid.gate_blocks` the engine's jobs are built with: each block trade's risk a contract is its row's stop
times the tick value, its fee its row's, its outcome at its own w its row's and NaN at every other w, and the facts
align with the blocks (`scripts/early_look.check_alignment`). Prints one JSON line last.

`trailing`: the route's trailing range (`survey_route.trailing`, on the walker arrays the real run feeds it --
`atlas_local.day_arrays` through `design_trades.history_from_arrays`) against Q-171's own (`s1_range.add_trailing` on
`s1_range.day_table` of the same bars, its default vendored arrays), every session, NaN for NaN; and a planted
look-ahead (the trailing mean reading its own day) shown to differ. Prints one JSON line last.
"""
from __future__ import annotations

import inspect
import json
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for p in (str(ROOT), str(ROOT / "tests")):
    if p not in sys.path:
        sys.path.insert(0, p)

from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()

import numpy as np  # noqa: E402

from extended import design_trades as DT  # noqa: E402
from extended import s1_range as S1R  # noqa: E402
from extended import survey_route as SR  # noqa: E402

import survey_route_world as RW  # noqa: E402
from propedge.research import atlas_local  # noqa: E402


def _same(a: np.ndarray, b: np.ndarray) -> bool:
    a, b = np.asarray(a, float), np.asarray(b, float)
    return a.shape == b.shape and bool(np.array_equal(np.isnan(a), np.isnan(b))) and \
        bool(np.array_equal(a[~np.isnan(a)], b[~np.isnan(b)]))


def check_trailing() -> dict:
    bars = RW.bars()
    cal = RW.fake_sources(bars)
    ref = S1R.add_trailing(S1R.day_table(bars, fomc=(), bls=(), src=cal))
    days = [str(d) for d in ref["date"]]
    by = {str(d): g for d, g in bars.groupby("day", sort=True)}
    arrays = {d: tuple(np.array([np.nan if x is None else x for x in v], dtype=float)
                       for v in atlas_local.day_arrays(by[d])) for d in days}
    hist = DT.history_from_arrays(days, arrays)
    kinds = dict(zip(days, ref["day_kind"].astype(str)))
    got = SR.trailing(hist, day_kinds=kinds, cal=cal)
    equal = all(_same(got[s], ref[f"trail_{s}"].to_numpy(float)) for s in S1R.SESSIONS)
    src = textwrap.dedent(inspect.getsource(SR.trailing))
    old = "out[s] = S1R.trailing_ranges(rng[s], ok)"
    ns: dict = {}
    exec(compile("from __future__ import annotations\n" + src.replace(old, "out[s] = S1R.trailing_ranges("
                 "np.roll(rng[s], -1), np.roll(ok, -1))"), SR.__file__, "exec"), SR.__dict__, ns)
    bad = ns["trailing"](hist, day_kinds=kinds, cal=cal)
    mutant_equal = all(_same(bad[s], ref[f"trail_{s}"].to_numpy(float)) for s in S1R.SESSIONS)
    finite = int(sum(np.isfinite(got[s]).sum() for s in S1R.SESSIONS))
    return {"equal": bool(equal), "mutant_equal": bool(mutant_equal), "finite": finite,
            "sessions": len(S1R.SESSIONS), "days": len(days)}


def check_gate() -> dict:
    import importlib.util

    import score_fv3_grid as gf
    import zero_edge_decomposition as zd
    from extended import triggers as T

    spec = importlib.util.spec_from_file_location("early_look_for_route_child", ROOT / "scripts" / "early_look.py")
    el = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = el
    spec.loader.exec_module(el)
    bars = RW.bars()
    hist = T.History.from_bars(bars)
    cal = RW.fake_sources(bars)
    sp = RW.space()
    rt = SR.route(sp, RW.point(sp), side_rules=RW.SIDE_RULES, source_params={"rl3": RW.RL3_PARAMS})
    kw = dict(RW.build_kw(hist, cal), fee_for_stop=lambda s: RW.FEE + s / 1000.0)
    out = SR.build(rt, hist, **kw)
    t, a = out.trades, out.aux
    days = list(hist.days)
    keys = sorted(set(out.rr_grid) | {1.0})                       # gate_blocks reads r_1: padded where absent
    t_pad = zd.pad(t, keys)
    facts = SR.facts(out, days, tick_value=RW.TICK_VALUE)
    bad = _gate_problems(gf.gate_blocks(t_pad, days, RW.TICK_VALUE, keys)[0], t, a, days, keys)
    planted = t_pad.copy()                                        # the positive control: one row's fee and stop moved
    planted.loc[planted.index[3], "fee_micro_eq"] += 0.25
    planted.loc[planted.index[7], "stop_ticks"] += 1
    caught = _gate_problems(gf.gate_blocks(planted, days, RW.TICK_VALUE, keys)[0], t, a, days, keys)
    blocks, n = gf.gate_blocks(t_pad, days, RW.TICK_VALUE, keys)
    try:
        el.check_alignment(blocks, facts)
        aligned = True
    except Exception as e:                                         # noqa: BLE001 -- reported, not hidden
        aligned, bad = False, bad + [f"alignment: {e}"]
    return {"ok": not bad and aligned and n == len(t) and len(caught) >= 2, "problems": bad[:5],
            "control_caught": caught[:3], "trades": int(len(t)), "stops": int(t["S"].nunique()),
            "fees": int(t["fee_micro_eq"].nunique()), "aligned": aligned, "keys": keys}


def _gate_problems(blocks, t, a, days, keys) -> list[str]:
    bad: list[str] = []
    p = 0
    for di, b in enumerate(blocks):
        for j in range(len(b.entry_t)):
            r, x = t.iloc[p], a.iloc[p]
            own = float(x["rr"])
            if str(r["date"]) != days[di] or float(b.entry_t[j]) != float(r["entry_t"]):
                bad.append(f"order at {p}")
            if float(b.risk_per_contract[j]) != float(r["S"]) * RW.TICK_VALUE:
                bad.append(f"risk at {p}")
            if float(b.fee[j]) != float(r["fee_micro_eq"]):
                bad.append(f"fee at {p}")
            if float(b.r_by_rr[own][j]) != float(r[f"r_{own:g}"]):
                bad.append(f"own-w outcome at {p}")
            if any(not np.isnan(b.r_by_rr[R][j]) for R in keys if R != own):
                bad.append(f"an outcome at another w at {p}")
            if float(b.exit_by_rr[own][j]) != float(r[f"exit_t_{own:g}"]):
                bad.append(f"own-w exit at {p}")
            p += 1
    if p != len(t):
        bad.append(f"the blocks hold {p} trades, the table {len(t)}")
    return bad


def main(argv: list[str]) -> int:
    if argv == ["gate"]:
        out = check_gate()
        print(json.dumps(out, sort_keys=True))
        return 0 if out["ok"] else 1
    if argv != ["trailing"]:
        raise SystemExit("usage: survey_route_child.py trailing | gate")
    out = check_trailing()
    print(json.dumps(out, sort_keys=True))
    return 0 if out["equal"] and not out["mutant_equal"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
