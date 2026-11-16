"""Family A3, step 0 (D-490 (1)-(2)): the resolution map of A1's events on FV3-C's rungs, and D-490's kill line.

    python scripts/a3_resolution_map.py --check     # A1's walk cache identity and the pool's counts; nothing walked
    python scripts/a3_resolution_map.py             # the one read: results/a3_resolution_map.csv + its manifest

Run once, from a clean tree (D-474), after the commit that adds it. EXPLORATORY (D-490 (2): step 0's read is
exploratory and counted); its variant is recorded under `D-490:a3_step0` in results/variants.jsonl. A second run is
refused while the result file exists.

**The trades walked.** A1's events exactly as A1's walk found them: `data/atlas/A1/events.parquet` and `days.parquet`,
read only, and only when the cache's manifest names the inputs A1's walk would name today
(`atlas_walk.inputs_digest("A1", "NQ")`, the development days, purpose 'development') -- else REFUSED (rebuild A1's walk
with `python scripts/atlas_screen.py --family A1 --walk`; this script never writes there). The pool is A1's fifteen
mechanical patterns (every pattern but `clock_t24`, T24's fixed slots: the null family, not an event); FOMC, early-close
and empty days walk nothing (A1's day kinds 'o', 'e', 'x'); on a BLS report day ('b') an event before the 07:30 CT cut is
dropped, as A1's trades drop it (`atlas_cells.cell_trades`). Both side rules (follow and fade) are pooled, so every
distinct event minute (date, slot) is walked long and short. Each is entered A1's five bars late
(`fast_walk.entry_bar`, `screen_delay_min: 5`) and walked by `propedge/research/fv3_rung_walk.py` on FV3-C's rungs (50,
100 and 200 ticks) at every quarter R to 3R with FV3's breakeven move and FV3-C's 15:10 flatten.

**The map** (section `map`): per event hour (`atlas_cells.hour_label`: the hour start in CT, 08:30-08:59 its own),
rung and R, over the NORMAL days ('n', T24's and A1's eligibility rule, `t24_exec.eligibility`): `offered` (the walks
there), `unresolved` (the share flattened at 15:10 -- a breakeven exit is resolved, D-212, D-308), its worst year,
`eligible` (unresolved at most 5 % overall and in every year with a walk), the target / stop / breakeven shares, and
whether 1:1 is eligible at that hour and rung (step 1's rung rule, beside). Beside each hour: the pooled A1 events per
session at that hour.

**"Pooled A1 events per session at an hour"** (declared here before the run): the number of distinct event minutes
(date, slot) of the pool at that hour -- a minute on which any of the fifteen patterns fires, once however many fire, BLS
days' events before the cut dropped -- divided by the number of sessions walked (the development window's 'n' and 'b'
days). Beside it (never the line): the pattern-events per session (each pattern's event counted) and the distinct minutes
with the clock's slots included.

**D-490's KILL LINE** (section `kill`, then `verdict`): for each rung S and each R in {2.5, 3}, H(S, R) is the set of
hours at which (hour, S, R) is eligible, and A(S, R) is the sum over the hours of H(S, R) of the pooled A1 events per
session at that hour -- the hours' events together, per session. **A3 SURVIVES only if A(S, R) >= 1.0 for some rung S
and some R in {2.5, 3}; otherwise A3 STOPS** (D-490 (2)). Printed beside, never the line: the largest single eligible
hour's rate for each (S, R).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/a3_resolution_map.py"
DECISION = "D-490"
VARIANT_ID = "D-490:a3_step0"
RESULT = "a3_resolution_map"
FAMILY = "A1"
UNRESOLVED_MAX = 0.05
KILL_RS = (2.5, 3.0)
KILL_MIN_PER_SESSION = 1.0
MAP_DAY_KINDS = ("n",)
WALK_DAY_KINDS = ("n", "b")


def hour_of(slot: int) -> str:
    import atlas_cells
    return atlas_cells.hour_label(int(slot))


def hours_of(slots: pd.Series) -> np.ndarray:
    """`hour_of` over a column (each distinct slot labelled once)."""
    s = slots.astype(int)
    lab = {x: hour_of(x) for x in s.unique()}
    return s.map(lab).to_numpy()


def pool_events(events: pd.DataFrame, days: pd.DataFrame, cfg: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(the pool: A1's mechanical patterns' events on walked days, BLS days' events before the cut dropped; the same
    with the clock's slots, beside). Both carry 'date' (str) and 'day_kind'."""
    from propedge.outcomes.collect_core import c_slot

    cut = c_slot(*(int(x) for x in str(cfg["news"]["bls_cut_ct"]).split(":")))
    kinds = dict(zip(days["date"].astype(str), days["day_kind"].astype(str)))
    ev = events.copy()
    ev["date"] = ev["date"].astype(str)
    ev["day_kind"] = ev["date"].map(kinds)
    ev = ev[ev["day_kind"].isin(WALK_DAY_KINDS)]
    ev = ev[~((ev["day_kind"] == "b") & (ev["slot"].astype(int) < cut))]
    clock = [i for i, p in enumerate(cfg["patterns"]) if p["kind"] == "clock"]
    return ev[~ev["pattern"].astype(int).isin(clock)].reset_index(drop=True), ev.reset_index(drop=True)


def walk_pool(pool: pd.DataFrame, arrays: Callable[[str], tuple], delay: int, tick: float):
    """(walks: date, slot, side, entry_slot, day_kind; their kinds, shape (walks, brackets), int8): every distinct event
    minute of the pool walked long and short."""
    from propedge.research import fv3_rung_walk as RW

    metas, kinds = [], []
    mins = pool.drop_duplicates(["date", "slot"]).sort_values(["date", "slot"], kind="stable")
    dk = dict(zip(pool["date"], pool["day_kind"]))
    for day, g in mins.groupby("date", sort=True):
        o, h, l, c = arrays(day)
        ent, res = RW.day_walks(o, h, l, c, g["slot"].astype(int).tolist(), delay, tick)
        if not ent:
            continue
        metas.append(pd.DataFrame(ent, columns=["slot", "side", "entry_slot"]).assign(date=day, day_kind=dk[day]))
        kinds.append(res["kind"].astype(np.int8))
    from propedge.research.fv3_rung_walk import BRACKETS
    if not metas:
        return (pd.DataFrame(columns=["date", "slot", "side", "entry_slot", "day_kind"]),
                np.zeros((0, len(BRACKETS)), np.int8))
    return pd.concat(metas, ignore_index=True)[["date", "slot", "side", "entry_slot", "day_kind"]], np.vstack(kinds)


def per_session(pool: pd.DataFrame, with_clock: pd.DataFrame, sessions: int) -> pd.DataFrame:
    """Per hour: the pooled A1 events per session (distinct event minutes / sessions -- the line's), and beside it the
    pattern-events per session and the distinct minutes with the clock's slots."""
    def by_hour(df: pd.DataFrame, distinct: bool) -> pd.Series:
        x = df.drop_duplicates(["date", "slot"]) if distinct else df
        return x.groupby(hours_of(x["slot"])).size() / float(sessions)

    out = pd.DataFrame({"events_per_session": by_hour(pool, True),
                        "pattern_events_per_session": by_hour(pool, False),
                        "events_per_session_with_clock": by_hour(with_clock, True)}).fillna(0.0)
    out.index.name = "hour"
    return out


def resolution_map(walks: pd.DataFrame, kinds: np.ndarray, rates: pd.DataFrame) -> pd.DataFrame:
    """Section `map`: per hour x rung x R over the normal days' walks."""
    from propedge.research.fv3_rung_walk import BREAKEVEN, BRACKETS, FLATTEN, STOP, TARGET

    m = walks["day_kind"].astype(str).isin(MAP_DAY_KINDS).to_numpy()
    w, k = walks[m].reset_index(drop=True), kinds[m]
    hours = hours_of(w["slot"])
    years = w["date"].astype(str).str[:4].astype(int).to_numpy()
    order = sorted(set(hours) | set(rates.index), key=lambda x: ((int(x[:2]) * 60 + int(x[3:]) - 17 * 60) % 1440))
    rows = []
    for hr in order:
        sel = hours == hr
        n = int(sel.sum())
        for b, (S, R, T) in enumerate(BRACKETS):
            kk = k[sel, b]
            f = kk == FLATTEN
            if n:
                by_year = pd.Series(f).groupby(years[sel]).mean()
                worst_year, worst = int(by_year.idxmax()), float(by_year.max())
                un = float(f.mean())
            else:
                worst_year, worst, un = None, float("nan"), float("nan")
            rows.append({"section": "map", "hour": hr, "stop_ticks": S, "stop_points": S / 4.0, "rr": R,
                         "target_ticks": T, "offered": n, "unresolved": un, "unresolved_worst_year": worst,
                         "worst_year": worst_year,
                         "eligible": bool(n > 0 and un <= UNRESOLVED_MAX + 1e-12 and worst <= UNRESOLVED_MAX + 1e-12),
                         "share_target": float((kk == TARGET).mean()) if n else float("nan"),
                         "share_stop": float((kk == STOP).mean()) if n else float("nan"),
                         "share_breakeven": float((kk == BREAKEVEN).mean()) if n else float("nan"),
                         **{c: float(rates[c].get(hr, 0.0)) for c in rates.columns}})
    out = pd.DataFrame(rows)
    one = out[np.isclose(out["rr"], 1.0)].set_index(["hour", "stop_ticks"])["eligible"]
    out["eligible_1r_same_rung"] = [bool(one.get((h, s), False)) for h, s in zip(out["hour"], out["stop_ticks"])]
    return out


def kill_line(mp: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """Sections `kill` (per rung x R in KILL_RS) and the verdict: SURVIVES only if, for some rung and some R in
    {2.5, 3}, the hours at which it is eligible together carry at least one pooled event minute a session."""
    rows = []
    for S in sorted(mp["stop_ticks"].unique()):
        for R in KILL_RS:
            g = mp[(mp["stop_ticks"] == S) & np.isclose(mp["rr"], R) & mp["eligible"]]
            a = float(g["events_per_session"].sum())
            rows.append({"section": "kill", "stop_ticks": int(S), "stop_points": S / 4.0, "rr": R,
                         "eligible_hours": ",".join(g["hour"]), "n_eligible_hours": int(len(g)),
                         "events_per_session_at_eligible_hours": a,
                         "max_single_hour_events_per_session": float(g["events_per_session"].max()) if len(g) else 0.0,
                         "offered_at_eligible_hours": int(g["offered"].sum()),
                         "reaches": bool(a >= KILL_MIN_PER_SESSION)})
    k = pd.DataFrame(rows)
    verdict = "SURVIVES" if bool(k["reaches"].any()) else "STOPS"
    rule = ("SURVIVES only if, for some rung S and some R in {2.5, 3}, the sum over the hours at which (hour, S, R) is "
            "eligible (<= 5 % unresolved overall and in every year, normal days, breakeven resolved) of the pooled A1 "
            "events per session at that hour (distinct event minutes / sessions walked) is at least 1.0; else STOPS")
    k = pd.concat([k, pd.DataFrame([{"section": "verdict", "verdict": verdict, "rule": rule}])], ignore_index=True)
    return k, verdict


def load_a1(cache: Path | None = None) -> tuple[dict, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """(A1's config, its events and days tables, the cache's inputs) -- read only; REFUSED unless the cache's manifest
    names exactly the inputs A1's walk would name now."""
    import atlas_screen as sc
    from propedge.research import atlas_walk as AW

    cfg = AW.config(FAMILY)
    src, _ = AW.walk_source(FAMILY)
    if src != FAMILY:
        raise SystemExit(f"REFUSED: {FAMILY} reads {src}'s walk")
    days = sc.dev_days(cfg, cfg["market"])
    if not days:
        raise SystemExit(f"REFUSED: no {cfg['market']} bar store in the development window")
    want = {**AW.inputs_digest(FAMILY, cfg["market"]), "days": len(days), "first": min(days), "last": max(days),
            "purpose": "development"}
    d = Path(cache or AW.CACHE / FAMILY)
    man = d / "manifest.json"
    have = json.loads(man.read_text(encoding="utf-8")).get("inputs") if man.is_file() else None
    if have != want:
        raise SystemExit(f"REFUSED: A1's walk cache at {d} does not match A1's inputs now ({have} != {want}); rebuild "
                         "it with `python scripts/atlas_screen.py --family A1 --walk` first -- this script never "
                         "writes there.")
    return cfg, pd.read_parquet(d / "events.parquet"), pd.read_parquet(d / "days.parquet"), want


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.data.bars import read_bars
    from propedge.reporting.results import write_result
    from propedge.research import atlas_local
    from propedge.research import fv3_rung_walk as RW

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="the cache identity and the pool's counts; nothing walked")
    a = ap.parse_args(argv)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    if not a.check and (rd / f"{RESULT}.csv").exists():
        print(f"REFUSED: {RESULT}.csv exists -- step 0's read is made once (D-490 (2)).")
        return 3
    cfg, events, days, inputs = load_a1()
    pool, with_clock = pool_events(events, days, cfg)
    walked = days[days["day_kind"].astype(str).isin(WALK_DAY_KINDS)]
    sessions = int(len(walked))
    delay, tick = int(cfg["screen_delay_min"]), float(cfg["contract"]["tick"])
    n_min = int(len(pool.drop_duplicates(["date", "slot"])))
    print(f"A1's cache matches its inputs; {sessions} sessions walked ({(walked['day_kind'] == 'n').sum()} normal); "
          f"{len(pool)} pattern-events, {n_min} distinct event minutes (x2 sides); delay {delay}", flush=True)
    if a.check:
        return 0

    ds = sorted(pool["date"].unique())
    bars = read_bars(cfg["market"], ds[0], ds[-1], "development", what="A3 step 0 walk (D-490)")
    by_day = {d: g for d, g in bars.groupby("day", sort=False)}

    def arrays(day: str):
        return tuple(np.array([np.nan if x is None else x for x in v], dtype=float)
                     for v in atlas_local.day_arrays(by_day.get(day, bars.iloc[0:0])))

    walks, kinds = walk_pool(pool, arrays, delay, tick)
    print(f"walked {len(walks)} entries on {walks['date'].nunique()} days", flush=True)
    rates = per_session(pool, with_clock, sessions)
    mp = resolution_map(walks, kinds, rates)
    kl, verdict = kill_line(mp)
    out = pd.concat([mp, kl], ignore_index=True)
    params = {"decision": DECISION, "family_walked": FAMILY, "a1_cache_inputs": inputs,
              "a1_config": "config/atlas_a1.yaml", "walk_module": "propedge/research/fv3_rung_walk.py",
              "stops_ticks": list(RW.STOPS_TICKS), "rr_grid": list(RW.RR_GRID),
              "target_rounding": "floor(R x stop + 1e-9) ticks (score_fv3_grid.Signals3.outcome)",
              "delay_bars": delay, "pool": "A1's 15 mechanical patterns (clock_t24 out), both side rules, distinct "
              "event minutes walked long and short; 'n' and 'b' days, a 'b' day's events before 07:30 CT dropped",
              "map_days": list(MAP_DAY_KINDS), "unresolved": "flattened at 15:10 (breakeven resolved)",
              "unresolved_max": UNRESOLVED_MAX, "breakeven": "score_fv3_grid.Signals3.outcome's (fv3_core.next_open)",
              "flatten": "the worst of 15:07-15:10 CT less 2 ticks; the 15:08 close where none (FV3-C's execution.flatten)",
              "sessions": sessions, "walks": int(len(walks)), "distinct_event_minutes": n_min,
              "kill_rs": list(KILL_RS), "kill_min_events_per_session": KILL_MIN_PER_SESSION,
              "events_per_session": "distinct pooled event minutes at the hour / sessions walked ('n' + 'b')",
              "bars": "data/bars/NQ (Databento GLBX.MDP3 ohlcv-1m, D-458)", "verdict": verdict}
    rec = VariantCounter(path=rd / "variants.jsonl").record(
        prereg_id=VARIANT_ID, seed=0, exploratory=True,
        params={"study": "A3 step 0 resolution map", "stops": list(RW.STOPS_TICKS), "rrs": list(RW.RR_GRID),
                "delay": delay, "pool": "A1 mechanical, both sides"},
        label="A3 step 0: A1's events on FV3-C's rungs, D-490 (2)'s kill read")
    write_result(out, RESULT, script=SCRIPT, seed=None, require_seed=False, exploratory=True, variant_count=1,
                 results_dir=results_dir, parameters={**params, "variant_id": rec.variant_id},
                 description="EXPLORATORY (D-490 (2)): A1's events five bars late on FV3-C's rungs (12.5 / 25 / 50 "
                             "points) at every quarter R to 3R with FV3's breakeven move and 15:10 flatten -- the "
                             "resolution map per event hour, rung and R on normal days, and D-490's kill line.",
                 notes={"status": "EXPLORATORY step 0 read (D-490): a kill test, no selection, no money decision",
                        "variant_count_rule": f"one read, recorded under {VARIANT_ID}"})
    kk = kl[kl["section"] == "kill"]
    pd.set_option("display.width", 200)
    print(kk[["stop_points", "rr", "n_eligible_hours", "events_per_session_at_eligible_hours",
              "max_single_hour_events_per_session", "eligible_hours"]].to_string(index=False))
    print(f"D-490 KILL LINE: A3 {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
