"""The child process of `tests/test_survey_route.py` (Q-215): the vendored tree on its path, synthetic bars only
(`tests/survey_route_world.py`), never the bar store.

    python tests/survey_route_child.py trailing
    python tests/survey_route_child.py gate
    python tests/survey_route_child.py race

`race` (B-1 (c2)): `check_race`'s docstring -- the route's one-component table through the vendored engine on
`early_look`'s toy job, under the route's accounting, the engine's own logs checked.

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


def check_race() -> dict:
    """B-1 (c2): the route's one-component table (RL3, w = 1.5) through the vendored engine on `early_look`'s toy job,
    its protocol's combine and funded R both the design's w, by `survey_route.route_simulate`
    (`three_way_baseline.simulate(log=True)` under the accounting). The engine's own lane logs are checked by
    `check_taken_rr`; a log record moved off its own w and one off the table, both taken from the engine's log, are
    refused. The planted mixed policy (a combine leaf at the own w, a funded leaf at rr=None) is refused by the policy
    check and admitted by round 1's check (`policy_rrs` read as floats); a combine leaf at rr=None, run past the
    policy check, is refused by the accounting (the draw reads the masked pnl channel)."""
    import copy
    import dataclasses as dc
    import importlib.util

    import score_fv3_grid as gf
    import zero_edge_decomposition as zd
    from extended import search_space as SS
    from extended import triggers as T
    from propedge.campaign.risk_policy import Leaf, Phase, RiskPolicy

    spec = importlib.util.spec_from_file_location("early_look_for_route_race", ROOT / "scripts" / "early_look.py")
    el = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = el
    spec.loader.exec_module(el)
    bars = RW.bars()
    hist = T.History.from_bars(bars)
    cal = RW.fake_sources(bars)
    sp = RW.space()
    w = 1.5
    d = RW.with_slot(sp, RW.base_point(sp), "ny_am.0", T1="rl3", T4=None, T5=SS.TICKET, first=30, last=120,
                     S1=0.2, S2=w)
    rt = SR.route(sp, d, side_rules=RW.SIDE_RULES, source_params={"rl3": RW.RL3_PARAMS})
    one = SR.build(rt, hist, **RW.build_kw(hist, cal))
    days = list(hist.days)
    keys = [1.0, w]                                                  # gate_blocks reads r_1: padded (NaN off w = 1)
    blocks, n_used = gf.gate_blocks(zd.pad(one.trades, keys), days, RW.TICK_VALUE, keys, require_sides=True,
                                    require_exits=True)
    facts = SR.facts(one, days, tick_value=RW.TICK_VALUE)
    el.check_alignment(list(blocks), facts)
    args = el.toy_args()
    proto = dc.replace(args["draws"]["protocol"], combine_rr=w, funded_rr=w)
    args["draws"]["protocol"] = proto
    args["path"]["risk_policy"] = RiskPolicy.from_protocol(proto, with_rr=True)
    first = min(facts)[0]
    start, horizon = max(0, first - 1), len(days) - max(0, first - 1)
    run = dict(seed=RW.SEED_ROUTE_COINS, part=0, history=0, block_sessions=len(days), dates=days,
               calendar=frozenset(__import__("datetime").date.fromisoformat(x) for x in days))
    rec, acct = SR.route_simulate(one, list(blocks), args, facts, start, (0, 1, 2), horizon, **run)
    logs = [list(lg) for lg in rec.logs]
    taken = sum(1 for lg in logs for r in lg if r.get("law") not in ("missed", "day_end"))
    own = SR.own_rr(one, days)
    out: dict = {"trades": int(len(one.trades)), "taken": int(taken), "logged": acct["logged"],
                 "lanes": acct["lanes"], "no_outcome": int(sum(t.get("no_outcome", 0) for t in acct["lanes"])),
                 "nan_dropped": int(sum(t.get("nan_dropped", 0) for t in acct["lanes"]))}
    # the engine's own log, moved: off its own w, then off the table
    rec0 = next(r for lg in logs for r in lg)
    refusals = {}
    for name, bad in (("off_w", [dict(rec0, R=2.0)]), ("off_table", [dict(rec0, j=int(rec0["j"]) + 999)])):
        try:
            SR.check_taken_rr(bad, own)
            refusals[name] = False
        except SR.RouteRefused:
            refusals[name] = True
    out["log_refusals"] = refusals
    # the planted mixed policy: refused now; round 1's float check admits it
    mixed = RiskPolicy("probe", Phase(combine=Leaf("c", 500.0, w), funded=Leaf("f", 400.0, None)))
    try:
        SR.check_policy_reads(mixed, one)
        out["mixed_refused"] = False
    except SR.RouteRefused as e:
        out["mixed_refused"] = "pnl channel" in str(e)
    asks = zd.policy_rrs(mixed)
    out["round1_admits_mixed"] = bool(asks) and all(abs(float(R) - w) <= SR.RR_TOL for R in asks)
    # past the policy check, a combine leaf at rr=None: the accounting refuses the draw that reads the pnl channel
    a2 = copy.deepcopy(args)
    a2["path"]["risk_policy"] = RiskPolicy.from_protocol(proto, with_rr=False)
    real = SR.check_policy_reads
    SR.check_policy_reads = lambda policy, rt_trades: {"reads": ["planted"], "flip_exempt": [], "w": w}
    try:
        SR.route_simulate(one, list(blocks), a2, facts, start, (0,), horizon, **run)
        out["accounting_refused"] = False
    except SR.RouteRefused as e:
        out["accounting_refused"] = "pnl channel" in str(e) or "NaN outcome" in str(e)
        out["accounting_why"] = str(e)[:160]
    finally:
        SR.check_policy_reads = real
    out["ok"] = bool(taken > 0 and sum(acct["logged"]) == sum(map(len, logs))
                     and out["no_outcome"] == 0 and out["nan_dropped"] == 0 and all(refusals.values())
                     and out["mixed_refused"] and out["round1_admits_mixed"] and out["accounting_refused"]
                     and n_used == len(one.trades))
    return out


def main(argv: list[str]) -> int:
    if argv == ["race"]:
        out = check_race()
        print(json.dumps(out, sort_keys=True, default=str))
        return 0 if out["ok"] else 1
    if argv == ["gate"]:
        out = check_gate()
        print(json.dumps(out, sort_keys=True))
        return 0 if out["ok"] else 1
    if argv != ["trailing"]:
        raise SystemExit("usage: survey_route_child.py trailing | gate | race")
    out = check_trailing()
    print(json.dumps(out, sort_keys=True))
    return 0 if out["equal"] and not out["mutant_equal"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
