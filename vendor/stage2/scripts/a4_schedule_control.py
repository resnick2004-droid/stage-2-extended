"""EXPLORATORY (D-555 (b)): the schedule control for family A4's campaign winners -- does a winning strategy beat the
SAME entries with its sides replaced by a fair coin? A4's family-wise test (D-550 (4)) asked whether a pattern's
direction beats its own coin twin trade by trade; its campaign pass then compared each survivor with the coin PLAN
(`rc_width_screen.csv`'s cells), which trades a different, denser schedule. This control separates the two: each
winner's own entry times and sizes, its sides either as the pattern chose them or by a coin.

    python scripts/a4_schedule_control.py --check --paths 4 --only brk5_s150_d5   # a smoke; nothing written
    python scripts/a4_schedule_control.py --workers 2                             # the reading (clean checkout, D-474)

**The strategies:** every row of `results/a4_coin_atlas.csv`'s `campaign` section with `beats_coin_plan` True (13 at
D-553's reading), each with its stop, delay and winning side rule from that row and its pattern index from the
`survivors` section. Their events are rebuilt by `a4_coin_atlas.scan(keep=...)` exactly as A4's campaign pass rebuilt
them, and walked once on both sides by the rung walk at the strategy's stop and delay (`walk_events`, which is
`a4_coin_atlas.survivor_trades`' walk); a side map then settles them by `resolved_coin.cell_trades` exactly as
`survivor_trades` does (`trades_on_sides`, checked equal to `survivor_trades` on the strategy's own sides).

**Per strategy:** (i) its own campaign at `CONTROL_PATHS` = 200 paths; (ii) the same events with each (date, minute)'s
side a fair coin (`resolved_coin.coin_table` over the events' dates and minutes), coin seeds `COIN_SEEDS` =
20261400 + i, i = 0..9, 200 paths each; all through P-16's engine call (`rc_screen.Runner`: the no-closure table, the
budget, the strict rule, each run's own 0.05 bound by the era rule) at the screen's campaign seed 20261131. Read: the
strategy's growth on the required bankroll at the bound, the ten coin-sided growths, their mean, sd, maximum, and the
strategy's rank among the eleven.

**The honest reading of ten draws:** ten coins cannot place a 95th percentile. Under the null that the pattern's
sides carry nothing the schedule's coins do not, the strategy and the ten coins are exchangeable, so the chance the
strategy exceeds all ten is 1/11 (about 0.091): "above every coin" is a one-sided rank test at p = 1/11, i.e. the
maximum of ten sits near the 91st percentile, not the 95th. Reported per strategy: `p_rank` = (1 + coins at or
above the strategy) / 11, `above_all_coins`, and beside it a normal-approximation 95th percentile, mean + 1.645 sd of
the ten (labelled an approximation). Over 13 strategies no family-wise claim is possible at p = 1/11; this is a
control, not a test -- a strategy that does not clear its own schedule's coins has shown no value in its sides.

**Identity first (refusing):** in the reading, each strategy's own campaign at 500 paths reproduces A4's `campaign`
row (growth at the bound and point, required bankroll, to 1e-9); with --check, each strategy's trades' content hash is
printed (`rc_dev_test.trades_hash`) and the own-side settlement must equal `survivor_trades`.

**Resume (as D-540):** each finished run's row is kept outside the checkout, keyed by the code's commit and the path
counts, so a run killed by the machine resumes.

Written: `results/a4_schedule_control.csv` (sections identity, strategy, coin), EXPLORATORY, one variant per strategy
under `D-555:a4_schedule_control`.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

if __name__ == "__main__":                 # one BLAS thread, before numpy loads (D-464 (5))
    for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/a4_schedule_control.py"
DECISION = "D-555"
RESULT = "a4_schedule_control"
FAMILY_ID = f"{DECISION}:a4_schedule_control"
ATLAS_FILE = "a4_coin_atlas.csv"
CONTROL_PATHS = 200
IDENTITY_PATHS = 500
COIN_SEEDS = tuple(20261400 + i for i in range(10))
NORMAL_Q95 = 1.6448536269514722
TOL = 1e-9
READING = ("EXPLORATORY (D-555 (b)): each A4 campaign winner against its own schedule's coin-sided twins; a control, "
           "not a test; selects nothing")


# ------------------------------------------------------------------------------------------------ the strategies


def winners(atlas: pd.DataFrame) -> list[dict[str, Any]]:
    """A4's campaign rows that beat the coin plan, each with its pattern index from the survivors section."""
    camp = atlas[(atlas["section"].astype(str) == "campaign")]
    camp = camp[camp["beats_coin_plan"].astype(str).str.lower().isin(("true", "1", "1.0"))]
    surv = atlas[atlas["section"].astype(str) == "survivors"]
    pidx = {str(s): int(p) for s, p in zip(surv["strategy"], surv["pattern_index"])}
    out = []
    for _, r in camp.iterrows():
        s = str(r["strategy"])
        if s not in pidx:
            raise SystemExit(f"REFUSED ({DECISION}): {s} has a campaign row but no survivors row.")
        out.append({"strategy": s, "pattern_index": pidx[s], "stop_ticks": int(float(r["stop_ticks"])),
                    "delay": int(float(r["delay"])), "side_rule": str(r["side_rule"]),
                    "atlas_growth_bound": float(r["growth_on_required"]),
                    "atlas_growth_point": float(r["growth_on_required_point"]),
                    "atlas_required_p90": float(r["required_p90"])})
    return out


# ------------------------------------------------------------------------------------------------ the trades


def walk_events(I: dict[str, Any], picks: list[tuple[str, int, int]], stop: int, delay: int) -> pd.DataFrame:
    """Both sides of every (date, minute) of `picks`, walked by the rung walk at `stop` and `delay` at every R of the
    grid -- `a4_coin_atlas.survivor_trades`' walk, before its side filter."""
    import atlas_a3 as A

    cfg = I["L"]["cfg"]
    rr_grid = A.rrs(cfg)
    by_day: dict[str, set[int]] = {}
    for d, t, _ in picks:
        by_day.setdefault(str(d), set()).add(int(t))
    mins = pd.DataFrame([{"date": d, "slot": t} for d, v in by_day.items() for t in sorted(v)])
    arr = A.bar_arrays(cfg, sorted(by_day))
    return A.walk_minutes(mins, arr, int(delay), float(cfg["contract"]["tick"]), (int(stop),), rr_grid)


def trades_on_sides(I: dict[str, Any], w: pd.DataFrame, want: set[tuple[str, int, int]], stop: int) -> pd.DataFrame:
    """The rows of `w` whose (date, minute, side) is in `want`, settled exactly as `survivor_trades` settles them."""
    import atlas_a3 as A
    import zero_edge_decomposition as zd

    from propedge.research import resolved_coin as rc

    L = I["L"]
    cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
    rr_grid = A.rrs(cfg)
    w = w[[(str(a), int(b), int(c)) in want for a, b, c in zip(w["date"], w["slot"], w["side"])]].copy()
    kinds = dict(zip(L["days"]["date"].astype(str), L["days"]["day_kind"].astype(str)))
    fees = A.fee_by_stop(fcfg, (int(stop),), tv)
    coins = {(str(d), int(t)): int(s) for d, t, s in zip(w["date"], w["slot"], w["side"])}
    t = rc.cell_trades(w, kinds, sorted({int(x) for x in w["slot"]}), int(stop), coins, fees, rr_grid=rr_grid,
                       fresh_rr=float(fcfg["state_policy"]["fresh"]["combine_rr"]), tick_value=tv,
                       entry_ticks=float(cfg["slip_ticks"]), cut=0)
    return zd.pad(t, sorted(set(float(R) for R in rr_grid) | set(zd.policy_rrs(I["plan"]))))


def own_sides(picks: list[tuple[str, int, int]]) -> set[tuple[str, int, int]]:
    return {(str(d), int(t), int(s)) for d, t, s in picks}


def coin_sides(picks: list[tuple[str, int, int]], seed: int) -> set[tuple[str, int, int]]:
    """Each (date, minute) of the strategy's events on a fair coin's side (`resolved_coin.coin_table` over the events'
    dates and minutes, the coin's seed)."""
    from propedge.research import resolved_coin as rc

    cells = sorted({(str(d), int(t)) for d, t, _ in picks})
    table = rc.coin_table(sorted({d for d, _ in cells}), sorted({t for _, t in cells}), int(seed))
    return {(d, t, int(table[(d, t)])) for d, t in cells}


# ------------------------------------------------------------------------------------------------ the readings


def rank_reading(own: float, coins: list[float]) -> dict[str, Any]:
    """The strategy against its schedule's coins: rank among the eleven, p = (1 + coins at or above it) / (1 + n),
    above every coin, and the normal-approximation 95th percentile (mean + 1.645 sd) beside."""
    c = np.asarray(coins, float)
    n = int(len(c))
    ge = int(np.sum(c >= float(own)))
    mean = float(c.mean()) if n else float("nan")
    sd = float(c.std(ddof=1)) if n > 1 else float("nan")
    return {"coins": n, "coin_growth_mean": mean, "coin_growth_sd": sd,
            "coin_growth_min": float(c.min()) if n else float("nan"),
            "coin_growth_max": float(c.max()) if n else float("nan"),
            "coins_at_or_above": ge, "p_rank": float((1 + ge) / (1 + n)) if n else float("nan"),
            "above_all_coins": bool(n and ge == 0),
            "coin_q95_normal_approx": mean + NORMAL_Q95 * sd if n > 1 else float("nan"),
            "above_q95_normal_approx": bool(n > 1 and float(own) > mean + NORMAL_Q95 * sd),
            "z_vs_coins": (float(own) - mean) / sd if n > 1 and sd > 0 else float("nan")}


class Resume:
    """D-540's resume file (as `rc_robust.Resume`), named for this study."""

    def __init__(self, folder: Path | None, key: str):
        self.path = None if folder is None else Path(folder) / f"{RESULT}_{key}.jsonl"
        self.rows: dict[str, dict] = {}
        if self.path is not None and self.path.is_file():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    r = json.loads(line)
                    self.rows[r["_label"]] = r["row"]
            print(f"  resume: {len(self.rows)} finished run(s) read from {self.path}", flush=True)

    def get(self, label: str) -> dict | None:
        return self.rows.get(label)

    def put(self, label: str, row: dict) -> None:
        self.rows[label] = row
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps({"_label": label, "row": row}, default=_jsonable) + "\n")


def _jsonable(x: Any) -> Any:
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, np.floating):
        return float(x)
    if isinstance(x, np.bool_):
        return bool(x)
    return str(x)


def cached(resume: Resume | None, label: str, make) -> dict:
    row = resume.get(label) if resume is not None else None
    if row is None:
        row = json.loads(json.dumps(make(), default=_jsonable))
        if resume is not None:
            resume.put(label, row)
    return row


def gate_reading(df: pd.DataFrame) -> dict[str, float]:
    def g(shift: str, col: str = "pf_growth_on_base_p50") -> float:
        r = df[(df["shift"] == shift) & (np.isclose(df["enforcement_p"].astype(float), 0.0))]
        return float(r[col].iloc[0])

    return {"growth_bound": g("lower_bound"), "growth_point": g("point"),
            "required_p90": g("lower_bound", "pf_required_p90")}


# ------------------------------------------------------------------------------------------------ the study


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    import a4_coin_atlas as AT
    import rc_dev_test as D
    import rc_screen as S

    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.outcomes.collect_core import c_slot
    from propedge.reporting.results import read_result, write_result
    from propedge.research import a4_coin_atlas as A4

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="a smoke: nothing written, no growth printed")
    ap.add_argument("--paths", type=int, default=None, help="with --check: paths a run")
    ap.add_argument("--only", default=None, help="with --check: one strategy")
    ap.add_argument("--days", type=int, default=None, help="with --check: the first N development days")
    ap.add_argument("--coins", type=int, default=len(COIN_SEEDS), help="with --check: how many coin seeds")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--no-resume", action="store_true")
    ap.add_argument("--resume-dir", default=None)
    a = ap.parse_args(argv)
    if not a.check and (a.paths is not None or a.only or a.days is not None or int(a.coins) != len(COIN_SEEDS)):
        print(f"REFUSED ({DECISION}): the reading runs every winner at {CONTROL_PATHS} paths with every coin; a "
              "smaller run is --check (writes nothing).")
        return 2
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    paths = CONTROL_PATHS if a.paths is None else int(a.paths)
    t_all = time.time()
    W = winners(read_result(RESULTS_DIR / ATLAS_FILE))
    if a.only:
        W = [w for w in W if w["strategy"] == a.only]
        if not W:
            print(f"REFUSED ({DECISION}): no winner named {a.only}.")
            return 2
    print(f"{len(W)} winners from {ATLAS_FILE}'s campaign section: {[w['strategy'] for w in W]}", flush=True)
    I = S.inputs()
    cfg = I["L"]["cfg"]
    lh, lm = (int(x) for x in str(cfg["day"]["last_decision_ct"]).split(":"))
    patterns, _ = A4.build_menu(A4._clock(cfg["day"]["first_decision_ct"]), int(c_slot(lh, lm)))
    keep = {(w["pattern_index"], w["stop_ticks"], w["delay"]): (1 if w["side_rule"] == "follow" else -1) for w in W}
    t0 = time.time()
    sc = AT.scan(I, patterns, days_limit=a.days, keep=keep)
    days_all = sorted(sc["days"])
    print(f"the events rebuilt (a4_coin_atlas.scan): {time.time() - t0:.0f} s", flush=True)
    R = S.Runner(I, a.workers)
    resume = None
    if not a.check and not a.no_resume:
        import subprocess

        commit = subprocess.run(["git", "rev-parse", "--short=12", "HEAD"], cwd=ROOT, capture_output=True,
                                text=True).stdout.strip() or "nocommit"
        folder = Path(a.resume_dir) if a.resume_dir else (
            Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "stage2-runs" / "resume")
        resume = Resume(folder, f"{commit}_{paths}_{IDENTITY_PATHS}")
    seeds = COIN_SEEDS[:int(a.coins)]
    idents, srows, crows = [], [], []
    for w in W:
        k = (w["pattern_index"], w["stop_ticks"], w["delay"])
        picks = sc["kept"][k]
        label = f"{w['strategy']}_{w['side_rule']}"
        t1 = time.time()
        wb = walk_events(I, picks, w["stop_ticks"], w["delay"])
        t_own = trades_on_sides(I, wb, own_sides(picks), w["stop_ticks"])
        ref = AT.survivor_trades(I, picks, w["stop_ticks"], w["delay"])
        if D.trades_hash(t_own) != D.trades_hash(ref):
            print(f"REFUSED ({DECISION}): {label}'s own-side settlement is not survivor_trades'.")
            return 3
        h = D.trades_hash(t_own)
        print(f"  {label}: {len(t_own)} candidates, hash {h[:16]}, walk {time.time() - t1:.0f} s", flush=True)
        if not a.check:
            def make_id(t=t_own, label=label):
                return gate_reading(R.run(f"{label} identity", t, days_all, IDENTITY_PATHS))

            idr = cached(resume, f"{label} identity", make_id)
            bad = [c for c, want in (("growth_bound", w["atlas_growth_bound"]),
                                     ("growth_point", w["atlas_growth_point"]),
                                     ("required_p90", w["atlas_required_p90"]))
                   if not abs(float(idr[c]) - float(want)) <= TOL]
            if bad:
                print(f"REFUSED ({DECISION}): {label} at {IDENTITY_PATHS} paths is not {ATLAS_FILE}'s campaign row "
                      f"({bad}).")
                return 3
            print(f"  identity HOLDS: {label} at {IDENTITY_PATHS} paths = {ATLAS_FILE}'s campaign row", flush=True)
            idents.append({"section": "identity", "strategy": w["strategy"], "holds": True, "candidates_hash": h,
                           "check": f"the strategy's own campaign at {IDENTITY_PATHS} paths reproduces {ATLAS_FILE}'s "
                                    "campaign row (growth at the bound and point, required bankroll, to 1e-9); its "
                                    "own-side settlement equals a4_coin_atlas.survivor_trades"})

        def make_own(t=t_own, label=label):
            return gate_reading(R.run(f"{label} own", t, days_all, paths))

        own = cached(resume, f"{label} own {paths}", make_own)
        coin_g = []
        for s in seeds:
            def make_coin(s=s, label=label):
                tc = trades_on_sides(I, wb, coin_sides(picks, int(s)), w["stop_ticks"])
                r = gate_reading(R.run(f"{label} coin {int(s)}", tc, days_all, paths))
                r.update({"candidates": int(len(tc)), "long_share": float((tc["side"] == "long").mean())})
                return r

            cr = cached(resume, f"{label} coin {int(s)} {paths}", make_coin)
            coin_g.append(float(cr["growth_bound"]))
            crows.append({"section": "coin", "strategy": w["strategy"], "coin_seed": int(s), **cr})
        rr = rank_reading(float(own["growth_bound"]), coin_g)
        srows.append({"section": "strategy", "strategy": w["strategy"], "side_rule": w["side_rule"],
                      "stop_ticks": w["stop_ticks"], "delay": w["delay"], "candidates": int(len(t_own)),
                      "candidates_hash": h, "paths": paths, "own_growth_bound": float(own["growth_bound"]),
                      "own_growth_point": float(own["growth_point"]), "own_required_p90": float(own["required_p90"]),
                      **rr})
        print(f"  {label}: own and {len(seeds)} coin-sided runs done ({time.time() - t1:.0f} s)"
              + ("" if not a.check else " -- no growth printed"), flush=True)
    secs = time.time() - t_all
    if a.check:
        print(f"--check done in {secs:.0f} s; nothing written.")
        return 0
    res = pd.concat([pd.DataFrame(idents), pd.DataFrame(srows), pd.DataFrame(crows)], ignore_index=True)
    res.insert(1, "reading", READING)
    counter = VariantCounter(path=rd / "variants.jsonl")
    for w in W:
        counter.record(prereg_id=FAMILY_ID, seed=int(S.SEED), exploratory=True,
                       params={"study": "A4 schedule control (D-555 (b))", "strategy": w["strategy"],
                               "coin_seeds": [COIN_SEEDS[0], COIN_SEEDS[-1]], "paths": CONTROL_PATHS},
                       label=f"D-555's schedule control: {w['strategy']} against its own schedule's coins")
    write_result(res, RESULT, script=SCRIPT, seed=int(S.SEED), exploratory=True, results_dir=results_dir,
                 variant_count=len(W),
                 parameters={"decision": DECISION, "atlas_file": ATLAS_FILE,
                             "strategies": [w["strategy"] for w in W], "campaign_seed": int(S.SEED),
                             "coin_seeds": list(COIN_SEEDS), "paths": CONTROL_PATHS,
                             "identity_paths": IDENTITY_PATHS,
                             "reading_rule": "p_rank = (1 + coins at or above) / 11 (exchangeable under the null; "
                                             "above all ten = p 1/11, about the 91st percentile); mean + 1.645 sd of "
                                             "the ten beside, a normal approximation",
                             "workers": int(a.workers), "seconds": round(secs, 1)},
                 notes={"status": READING, "selection": "none; a control on A4's campaign pass"},
                 description="EXPLORATORY (D-555 (b)): each of A4's campaign winners against its own entries with "
                             "fair-coin sides (ten coin seeds, 200 paths each, P-16's engine call), its rank among them.")
    print(f"written: {RESULT}.csv ({len(W)} strategies; {secs:.0f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
