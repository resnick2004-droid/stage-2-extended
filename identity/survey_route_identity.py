"""Q-215's identity (heavy; the lead runs it under `run.lock`): the survey's real-bar route (`extended.survey_route`)
on the search years' bars, against two independent records of the same quantities.

    python scripts/run_clean.py --name q215-identity --hours 1 --mem-gb 3 --task Q-215 -- python identity/survey_route_identity.py
    python identity/survey_route_identity.py --part trailing      # I-1 only (needs no S1 file)

**I-1, the stop's unit** (`--part trailing`): the route's trailing range `survey_route.trailing`, on the walker arrays
the route is fed (`atlas_a3.bar_arrays` through `design_trades.history_from_arrays`) and Stage 2's day kinds, equals
Q-171's own (`s1_range.add_trailing` of `s1_range.day_table` on the same arrays, its day kinds by
`vol_descriptive.day_kind` with A1's FOMC and BLS days), in every session, NaN for NaN, tolerance zero; and the two kind
sources disagree on no day's walked status (part of `holds`).

**I-2, a survey point through the route** (`--part route`): RL3's early-look base cell as a survey point of the real
lever space (`search_space.from_lever_space(slots={"ny_am": 1})`: `ny_am.0` on, `rl3`, the window holding 09:00, S1
the midpoint of `lever_space.stop_width("ny_am")`, S2 the midpoint of S2's range, every design-wide lever at its first
cell or low end, T7 off) routed with the early look's declared kind, cutoff and side rule (`scripts/early_look.py`'s
`KIND`, `CUTOFF`, `RULE`). Three comparisons, each at tolerance zero:
- **the fills**: on every day the route trades, its fills -- date, alert, fill bar, side, the alert's volatility --
  equal those of the early look itself, rebuilt by **`early_look.build`** (its spec at its 50-tick stop, its A3 grid
  `A.rrs(cfg)`, its own facts and job blocks), row for row (a fill and its side do not depend on the stop);
- **the stops and outcomes**: for every stop group of the route (the days its S1 stop is one value), the route's rows
  equal `design_trades.build_trades(rl3_spec(kind, cutoff, rule, stop))` on those days at the route's own w, column for
  column (the **trade frame**: stop, costs, outcome, MAE, exit and kind at w; the aux frame is not compared here);
- **the stand-aside days**: the route's stand-aside reason on **every day** (`no_trail`, `below_floor`, `above_cap`,
  or none), day by day -- not only the counts, which two compensating days would leave equal -- equals the one
  computed apart from `survey_route.stops`: `s1_range.add_trailing` of `s1_range.day_table` on the same arrays (its
  own day kinds), `ny`'s trailing range times k against `lever_space.stop_caps()`, both edges inclusive;
- **the record**: the rebuilt early look's `trades_sha256` (`search_cut.trades_subhash` of its padded table), trade
  count and counts equal those its committed result records (`results/early_look_rl3_pd_fade.csv.manifest.json`), so
  the reference is the one that run read.
**I-2 needs S1 to load** (`results/s1_range.csv`, git-ignored, E-245): a checkout without it refuses I-2 by name
(F-13's build item 6, `run_clean.py` supplying the file in place, comes first).

Why not P-16's registered trades hash through a survey point: no point of the lever space expresses P-16 -- F-13's T1
offers `p14` and `rl3` only (`p16` has no playbook side, `trigger_sides.NO_SIDE`), P-16's registered walk keeps FV3's
breakeven move (S7 is dropped here) and its sides are `coin_table`'s, not a trigger's. Q-213's identity already holds
`design_trades` itself to that hash; this one holds the route's mapping to the early look's reading of `design_trades`.

Heavy: it reads the search years' bars inside `extended.search_cut`, after `search_cut.authorise`. Prints one JSON line;
exits 0 when every part run holds, 1 otherwise. Writes no file. Draws no randomness.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import sys
import time
from datetime import date
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

if __name__ == "__main__":
    for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

LAST = "2023-12-29"
PARTS = ("trailing", "route")
EARLY_RECORD = "results/early_look_rl3_pd_fade.csv.manifest.json"
FILL_COLUMNS = ("date", "decision_slot_minutes", "entry_t", "side")
SLOT = "ny_am.0"


def _early_look() -> Any:
    name = "early_look_for_q215_identity"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / "early_look.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    return sys.modules[name]


def _same(a: np.ndarray, b: np.ndarray) -> bool:
    a, b = np.asarray(a, float), np.asarray(b, float)
    return a.shape == b.shape and bool(np.array_equal(np.isnan(a), np.isnan(b))) and \
        bool(np.array_equal(a[~np.isnan(a)], b[~np.isnan(b)]))


# ------------------------------------------------------------------------------------------------ I-1


def trailing_identity(days: Sequence[str], arrays: Mapping[str, tuple], kinds: Mapping[str, str], cal: Any,
                      fomc: Sequence[int], bls: Sequence[int]) -> dict[str, Any]:
    """I-1 on given arrays (the module docstring)."""
    from extended import design_trades as DT
    from extended import s1_range as S1R
    from extended import survey_route as SR

    hist = DT.history_from_arrays(list(days), arrays)
    frame = pd.DataFrame({"day": list(days)})
    ref = S1R.add_trailing(S1R.day_table(frame, fomc=fomc, bls=bls, src=cal,
                                         day_arrays=lambda g: arrays[str(g["day"].iloc[0])]))
    got = SR.trailing(hist, day_kinds=kinds, cal=cal)
    per = {s: _same(got[s], ref[f"trail_{s}"].to_numpy(float)) for s in S1R.SESSIONS}
    finite = {s: int(np.isfinite(got[s]).sum()) for s in S1R.SESSIONS}
    walked_ref = ref["day_kind"].astype(str).isin(S1R.WALKED_KINDS).to_numpy()
    walked_mine = np.array([str(kinds[d]) in S1R.WALKED_KINDS for d in ref["date"].astype(str)])
    disagree = int((walked_ref != walked_mine).sum())
    return {"part": "trailing", "holds": bool(all(per.values()) and all(v > 0 for v in finite.values())
                                             and disagree == 0),
            "equal_by_session": per, "finite_by_session": finite, "days": len(days),
            "walked_status_disagreements": disagree, "tolerance": 0}


# ------------------------------------------------------------------------------------------------ I-2


def base_point(sp: Any) -> dict[str, Any]:
    """Every design-wide lever at its first cell or its low end (T7 off, A4 standard, A12 zero), every slot off: the
    identity's choice, on levers the compared columns never read (they are the firm path's)."""
    from extended import search_space as SS

    d: dict[str, Any] = {}
    for dim in sp.dims:
        if dim.slot is not None:
            d[dim.name] = SS.OFF if dim.name == SS.slot_dim(dim.slot, "on") else None
        elif dim.kind == SS.CAT:
            d[dim.name] = dim.values[0]
        else:
            d[dim.name] = int(dim.lo) if dim.kind == SS.INT else float(dim.lo)
    d.update({"T7": "off", "A4": "standard", "A12": 0})
    return d


def rl3_point(sp: Any) -> dict[str, Any]:
    """The early look's cell as a point: `ny_am.0` on, `rl3`, its window the offsets of 09:00 to 30 minutes after on
    every date, S1 and S2 at their ranges' midpoints (computed from the loaded space, never typed)."""
    from extended import search_space as SS
    from extended import triggers as T

    d = base_point(sp)
    starts = sorted({int(sp.starts(day)["ny_am"]) for day in sp.days})
    live = sorted({int(T.LIVE_0900) - a for a in starts})
    s1, s2 = sp.dim(SS.slot_dim(SLOT, "S1")), sp.dim(SS.slot_dim(SLOT, "S2"))
    step = int(sp.dim(SS.slot_dim(SLOT, "first")).step)
    d.update({SS.slot_dim(SLOT, "on"): SS.ON, SS.slot_dim(SLOT, "T1"): "rl3", SS.slot_dim(SLOT, "T4"): None,
              SS.slot_dim(SLOT, "T5"): SS.TICKET, SS.slot_dim(SLOT, "first"): live[0],
              SS.slot_dim(SLOT, "last"): live[-1] + 6 * step,
              SS.slot_dim(SLOT, "S1"): 0.5 * (float(s1.lo) + float(s1.hi)),
              SS.slot_dim(SLOT, "S2"): 0.5 * (float(s2.lo) + float(s2.hi))})
    return d


def early_fills(early: Mapping[str, Any]) -> pd.DataFrame:
    """The early look's fills from `early_look.build`'s output, in its (block day, index) order: the date, the alert,
    the fill bar's end, the side (its job blocks' `sides`) and the alert's volatility (its facts)."""
    rows = []
    for (di, j), f in early["facts"].items():
        side = int(np.asarray(early["blocks"][di].sides)[j])
        rows.append({"date": str(early["dates"][di]), "decision_slot_minutes": int(f.decision),
                     "entry_t": float(f.entry), "side": "long" if side > 0 else "short", "sigma": float(f.sigma)})
    return pd.DataFrame(rows, columns=list(FILL_COLUMNS) + ["sigma"])


def record_problems(early: Mapping[str, Any], record: Mapping[str, Any] | None) -> list[str]:
    """The rebuilt early look against its committed record: `trades_sha256`, `trades` and `counts`."""
    if record is None:
        return ["no record of the early look"]
    out = []
    for k in ("trades_sha256", "trades"):
        if early.get(k) != record.get(k):
            out.append(f"{k}: rebuilt {early.get(k)!r}, recorded {record.get(k)!r}")
    if json.loads(json.dumps(early.get("counts"), sort_keys=True)) != record.get("counts"):
        out.append("counts differ")
    return out


def stand_aside_apart(hist: Any, cal: Any, *, k: float, fomc: Sequence[int], bls: Sequence[int], tick: float
                      ) -> list[str]:
    """The NY AM slot's stand-aside reason on every day ('' where it trades), computed apart from
    `survey_route.stops`: Q-171's own trailing range (`s1_range.add_trailing` of `s1_range.day_table` on the
    history's arrays, its day kinds by `vol_descriptive.day_kind` with `fomc` and `bls`), `ny`'s times k, against
    `lever_space.stop_caps()`, edges inclusive."""
    from extended import lever_space as LS
    from extended import s1_range as S1R

    days = list(hist.days)
    arrays = {d: hist.day(i) for i, d in enumerate(days)}
    ref = S1R.add_trailing(S1R.day_table(pd.DataFrame({"day": days}), fomc=fomc, bls=bls, src=cal,
                                         day_arrays=lambda g: arrays[str(g["day"].iloc[0])]))
    caps = LS.stop_caps()
    out = []
    for t in ref["trail_ny"].to_numpy(float):
        if not np.isfinite(t):
            out.append("no_trail")
        elif float(k) * t < int(caps["floor_ticks"]) * tick:
            out.append("below_floor")
        elif float(k) * t > int(caps["cap_ticks"]) * tick:
            out.append("above_cap")
        else:
            out.append("")
    return out


def aside_problems(route: Sequence[str], apart: Sequence[str], days: Sequence[str]) -> list[str]:
    """The days whose stand-aside reason differs between the route and the apart computation (equal counts by
    reason are not enough: two compensating days would pass)."""
    if len(route) != len(apart):
        return [f"the route reads {len(route)} days, the apart computation {len(apart)}"]
    return [f"{d}: route {a or 'trades'!r}, apart {b or 'trades'!r}" for d, a, b in zip(days, route, apart) if a != b]


def route_identity(sp: Any, hist: Any, kinds: Mapping[str, str], cal: Any, *, kind: str, cutoff: int,
                   rule: Mapping[str, str], early: Mapping[str, Any], record: Mapping[str, Any] | None,
                   fee_for_stop: Callable[[int], float], tick_value: float, market_entry_ticks: float, tick: float,
                   fomc: Sequence[int] = (), bls: Sequence[int] = (), route_side: str | None = None) -> dict[str, Any]:
    """I-2 on a given space and history (the module docstring). `early` is `early_look.build`'s output, `record` its
    committed result's parameters (or None: then I-2 does not hold). `route_side` plants a side rule on the route
    alone (a light test's fault); the references keep the declared rule."""
    from extended import design_trades as DT
    from extended import survey_route as SR
    from extended import triggers as T

    side = "fade" if set(rule.values()) == {"fade"} else None
    if side is None:
        raise ValueError(f"the early look's rule {rule!r} is not one word for every level")
    rt = SR.route(sp, rl3_point(sp), side_rules={"rl3": route_side or side},
                  source_params={"rl3": {"kind": kind, "cutoff": cutoff}})
    trail = SR.trailing(hist, day_kinds=kinds, cal=cal)
    out = SR.build(rt, hist, cal=cal, day_kinds=kinds, news_windows=None, fee_for_stop=fee_for_stop,
                   tick_value=tick_value, market_entry_ticks=market_entry_ticks, trail=trail, tick=tick)
    w = float(rt.slots[0].w)
    groups: dict[int, list[int]] = {}
    for i, (s, _) in enumerate(SR.stops(rt, trail, tick=tick)[SLOT]):
        if s is not None:
            groups.setdefault(int(s), []).append(i)
    traded = {hist.days[i] for ds in groups.values() for i in ds}
    # the fills, against the early look itself
    ef = early_fills(early)
    ef = ef[ef["date"].isin(traded)].reset_index(drop=True)
    if len(out.trades):
        mine = out.trades.loc[:, list(FILL_COLUMNS)].reset_index(drop=True)
        mine["sigma"] = out.aux["sigma"].to_numpy(float)
    else:
        mine = pd.DataFrame(columns=list(FILL_COLUMNS) + ["sigma"])
    fills = len(mine) > 0 and len(mine) == len(ef) and all(
        np.array_equal(mine[c].astype(str).to_numpy(), ef[c].astype(str).to_numpy()) for c in ("date", "side")) \
        and all(np.array_equal(mine[c].to_numpy(float), ef[c].to_numpy(float))
                for c in ("decision_slot_minutes", "entry_t", "sigma"))
    # the stops and outcomes, group by group, against design_trades on the declared spec
    bad_groups: list[int] = []
    ctxs: dict[int, Any] = {}
    for s, ds in sorted(groups.items()):
        spec = DT.rl3_spec(kind, cutoff, dict(rule), s)
        for i in ds:
            if i not in ctxs:
                ctxs[i] = T.context_for(spec.source, cal, date.fromisoformat(hist.days[i]), i, rules=spec.rules)
        ref = DT.build_trades(spec, hist, lambda i: ctxs[i], day_kinds=kinds, rr_grid=(w,), fresh_rr=w,
                              fee_micro_eq=float(fee_for_stop(s)), tick_value=tick_value,
                              market_entry_ticks=market_entry_ticks, days=ds, tick=tick)
        on = out.trades["date"].isin([hist.days[i] for i in ds]).to_numpy() if len(out.trades) \
            else np.zeros(0, bool)
        if int(on.sum()) != len(ref.trades):
            bad_groups.append(s)
        elif len(ref.trades) and not out.trades.loc[on, list(ref.trades.columns)].reset_index(drop=True).equals(
                ref.trades.reset_index(drop=True)):
            bad_groups.append(s)
    rec = record_problems(early, record)
    apart = stand_aside_apart(hist, cal, k=float(rt.slots[0].k), fomc=fomc, bls=bls, tick=tick)
    route_why = [why for _, why in SR.stops(rt, trail, tick=tick)[SLOT]]
    aside_bad = aside_problems(route_why, apart, hist.days)
    aside = not aside_bad
    holds = bool(fills and groups and not bad_groups and not rec and aside)
    return {"part": "route", "holds": holds, "fills_equal": bool(fills), "stand_aside_equal": bool(aside),
            "stand_aside_days_unequal": aside_bad[:10],
            "stand_aside_apart": {r: apart.count(r) for r in ("no_trail", "below_floor", "above_cap")},
            "stop_groups": len(groups),
            "stop_groups_unequal": bad_groups[:10], "record_problems": rec, "route_trades": int(len(out.trades)),
            "early_trades_on_route_days": int(len(ef)), "early_trades": int(len(early_fills(early))),
            "route_days": len(traded), "stand_aside": out.counts[SLOT]["stand_aside"], "k": rt.slots[0].k, "w": w,
            "tolerance": 0}


# ------------------------------------------------------------------------------------------------ the run


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--part", choices=PARTS + ("all",), default="all")
    args = ap.parse_args(argv)
    t0 = time.perf_counter()
    from extended import VENDOR_STAGE2, use_vendored_stage2
    from extended import day_calendar as DC
    from extended import design_trades as DT
    from extended import h4_audit as HA
    from extended import lever_space as LS
    from extended import search_cut as SC
    from extended import search_space as SS
    from extended import three_way_firm as TF

    use_vendored_stage2()
    import atlas_a3 as A
    import rc_screen as RS

    EL = _early_look()
    spec_s1 = _load_script("s1_range_for_q215", ROOT / "scripts" / "s1_range.py")
    cal = DC.load_sources(flags=ROOT / "results" / "h2_overnight_flags.csv", manifest=TF.MANIFEST,
                          calendar=ROOT / "config" / "calendar_early_closes.csv")
    SC.authorise(purpose="survey_route_identity", declaration=None,
                 what="Q-215 identity: the survey route's trailing range and an RL3 survey point on the search years",
                 last=LAST, bars=True, root=VENDOR_STAGE2)
    with SC.cut(last=LAST, root=VENDOR_STAGE2) as cut_log:
        I_in = RS.inputs()
        L = I_in["L"]
        cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
        days_df = L["days"].copy()
        days_df["date"] = days_df["date"].astype(str)
        days_df = days_df.sort_values("date", kind="stable").reset_index(drop=True)
        days = days_df["date"].tolist()
        SC.check_calendar(days, calendar_path=ROOT / HA.H4_SEARCH_CALENDAR_REL, last=LAST)
        kinds = dict(zip(days_df["date"], days_df["day_kind"].astype(str)))
        arr_fn = A.bar_arrays(dict(cfg), list(days))
        arrays = {str(d): arr_fn(str(d)) for d in days}
        fomc, bls, _ = spec_s1.release_days()
        problems = cut_log.problems()
    if problems:
        print(json.dumps({"identity": "Q-215", "holds": False, "why": f"search_cut problems: {problems}"}))
        return 1
    results: list[dict[str, Any]] = []
    if args.part in ("trailing", "all"):
        results.append(trailing_identity(days, arrays, kinds, cal, sorted(fomc), sorted(bls)))
    if args.part in ("route", "all"):
        try:
            LS.bounds("S1")
            sp = SS.from_lever_space(slots={"ny_am": 1})
        except LS.LeverRefused as e:
            results.append({"part": "route", "holds": False,
                            "why": f"REFUSED: S1 does not load in this checkout ({type(e).__name__}: {e}); "
                                   "results/s1_range.csv is git-ignored (E-245) -- F-13's build item 6 first"})
        else:
            hist = DT.history_from_arrays(days, arrays)
            del arrays
            rec_path = ROOT / EARLY_RECORD
            record = json.loads(rec_path.read_text(encoding="utf-8")).get("parameters") if rec_path.is_file() else None
            early = EL.build(ROOT)                    # the early look itself: its spec, grid, facts and job blocks
            fees: dict[int, float] = {}

            def fee(s: int) -> float:
                if s not in fees:
                    fees[s] = float(A.fee_by_stop(fcfg, (int(s),), tv)[int(s)])
                return fees[s]

            results.append(route_identity(sp, hist, kinds, cal, kind=EL.KIND, cutoff=int(EL.CUTOFF), rule=EL.RULE,
                                          early=early, record=record, fee_for_stop=fee, tick_value=tv,
                                          market_entry_ticks=float(cfg["slip_ticks"]),
                                          tick=float(cfg["contract"]["tick"]), fomc=sorted(fomc), bls=sorted(bls)))
    holds = bool(results) and all(r.get("holds") for r in results)
    print(json.dumps({"identity": "Q-215 survey route", "holds": holds, "parts": results,
                      "seconds": round(time.perf_counter() - t0, 1)}, sort_keys=True, default=str))
    return 0 if holds else 1


def _load_script(name: str, path: Path) -> Any:
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    return sys.modules[name]


if __name__ == "__main__":
    raise SystemExit(main())
