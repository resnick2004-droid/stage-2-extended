"""RD-01's cost, measured on synthetic campaigns of the development window's length (the third read's (g): "measure, do
not estimate"). Reads no bar, no atlas and no result file; writes nothing but its own temporary files; draws only from
children of section 12's toy seed. Each stage runs in a process of its own so its peak memory is its own.

    python scripts/rd01_cost_probe.py                 # every stage, one process each; prints one JSON line a stage
    python scripts/rd01_cost_probe.py --stage scorecard --starts 12

**The campaign.** 1,640 sessions from 2020-01-02 (the development window's count of trading sessions), 0 to 3 trades a
session at a P-16-like 150-tick stop (P-14-like 50- and 100-tick stops for the second stream), outcomes at every quarter
R from 0.25R to 3R, a two-leaf toy state table, Topstep's ledger rules, five seats, the purchase budget and the
registered never-binding bankroll. Real trades and the registered tables differ: these are orders of magnitude, measured.

**The stages.**
- `scorecard`: one cell's single pass (`firm_reading.run_cell`) on evenly spaced starts at TS, LU, DT, FP and QP's strict
  corners, and the cell's readings on those starts (U1's summary, 9.3's counts, the pairing, M1's lines, A-10's grid
  and break-even): seconds a start-run each.
- `ladder`: one denial-ladder cell (A-9 alone, 10 %, Q-17's exact-length rule).
- `gate`: one corner's gate (`firm_reading.gate_rows`: the plan call and the twin, two arms each) at a few paths of the
  gate's 504-session horizon: seconds a path.
- `coverage`: 10.2 item 7's coverage, one shape: seconds a series.
- `files`: the reading's file at the run's structure (the toy's own rows, each scorecard run-arm carried to the
  window's starts): the frame through the spill, the CSV, the menu step on it, and their peak memory.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for _p in (str(ROOT), str(ROOT / "identity"), str(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

STAGES = ("scorecard", "ladder", "gate", "coverage", "files")
N_SESSIONS = 1640
RS = tuple(0.25 * k for k in range(1, 13))


def campaign(seed, stops: tuple[int, ...]):
    import numpy as np
    import pandas as pd

    from extended import walker as W
    from propedge.outcomes.distribution import DayBlock

    TV, FEE = 0.5, 1.22
    rng = np.random.default_rng(seed)
    days = [d.date().isoformat() for d in pd.bdate_range("2020-01-02", periods=N_SESSIONS)]
    blocks = []
    for _ in range(N_SESSIONS):
        k = int(rng.integers(0, 4))
        S = rng.choice(stops, size=k).astype(float)
        c = (TV + FEE) / (S * TV)
        mfe = rng.exponential(S * 1.6)
        stop = rng.random(k) < 0.55
        p = np.floor(mfe * rng.uniform(0, 0.9, size=k))
        term = np.where(stop, -1.0 - (2 * TV + FEE) / (S * TV), (p - 2) / S - c)
        entry = np.array([W.bar_of(8, 40) + 60 * j for j in range(k)], float)
        r_by, mae_by, ex_by = {}, {}, {}
        for R in RS:
            tt = np.array([W.target_ticks(R, int(x)) for x in S], float)
            won = mfe >= tt
            r_by[R] = np.where(won, tt / S - c, term)
            mae_by[R] = np.where(won, 0.4, np.maximum(0.4, -term))
            ex_by[R] = entry + np.where(won, 25.0, 50.0)
        risked = S * TV * 10
        blocks.append(DayBlock(pnl=r_by[2.0] * risked, risked=risked, exit_reasons=tuple("x" for _ in range(k)),
                               risk_per_contract=S * TV, mae=mae_by[2.0] * risked, entry_t=entry, exit_t=ex_by[2.0],
                               r_by_rr=r_by, mae_by_rr=mae_by, fee=np.full(k, FEE), sides=np.ones(k), exit_by_rr=ex_by))
    return blocks, days


def setup():
    from extended import use_vendored_stage2

    use_vendored_stage2()
    import numpy as np
    import score_fv3_grid as gf

    from extended import firm_reading as R
    from extended import firm_terms as T
    from extended import user_beside as B
    from propedge.campaign.gate import shifted_blocks
    from propedge.campaign.lockstep import ConductModel
    from propedge.campaign.payout_method import payout_method_terms
    from propedge.campaign.protocols import Protocol
    from propedge.campaign.risk_policy import Leaf, Phase, RiskPolicy, Tiers
    from propedge.campaign.sizing import CURRENT_TIER, SizingRule
    from propedge.contract.adapter import rules_from_ledger
    from propedge.contract.rules import load_rules

    kids = np.random.SeedSequence(R.F.LADDER_SEED + 2).spawn(4)
    rules = rules_from_ledger()
    sizing = dataclasses.replace(SizingRule.from_ledger(CURRENT_TIER), fee_schedule=T.fee_schedule("TS"))
    proto = Protocol(name="rd01_probe", combine_rr=2.0, combine_risk=1500.0, funded_rr=2.0, funded_risk=1000.0,
                     trades_per_day=4, max_concurrent_accounts=5)
    policy = RiskPolicy(id="rd01_probe", root=Phase(
        combine=Tiers("balance", ((-1e9, Leaf("combine base", 1500.0, 2.0)),
                                  (3000.0, Leaf("combine top", 500.0, 1.5)))),
        funded=Tiers("request_day", ((0.0, Leaf("funded", 1000.0, 2.0)), (1.0, Leaf("request day", 750.0, 1.5))))))
    lag = int(payout_method_terms("aeropay", ledger=load_rules()).lag_days)
    args = {"draws": {"protocol": proto, "mode": "rotation", "flip": None, "sizing": sizing},
            "path": dict(edge=0.0, rules=rules, initial_bankroll=float(gf.UNBOUND_BANKROLL), max_concurrent_accounts=5,
                         subscription=float(rules.subscription), billing_days=int(rules.billing_days),
                         activation=float(rules.activation), payout_lag_days=lag, max_concurrent_combines=5,
                         max_total_accounts=5, conduct=ConductModel(rtp=False, enforcement_p=0.0),
                         combine_max_days=2000, funded_horizon_days=100_000, purchase_budget=(20, 21),
                         risk_policy=policy),
            "seed": B.SEED_BLOCK[1]}
    delta = {R_: -0.03 - 0.005 * i for i, R_ in enumerate(RS)}
    pt, days = campaign(kids[0], (150,))
    vd = shifted_blocks(pt, delta[2.0], delta)
    stream = {"jobs": {"point": {"engine": "single", "blocks": pt, "dates": days, "args": args},
                       "verdict": {"engine": "single", "blocks": vd, "dates": days, "args": args}},
              "config": None, "delta": {"verdict": (delta[2.0], delta)}}
    return stream, {"proto": proto, "policy": policy, "sizing": sizing, "rules": rules, "delta": delta, "kids": kids}


def stage_scorecard(n_starts: int) -> dict:
    import user_journey as UJ

    from extended import firm_reading as R
    from extended import firm_terms as T
    from extended import user_beside as B
    from extended import user_readings as UR

    stream, _ = setup()
    off = B.BY_NAME["off"]
    pt = stream["jobs"]["point"]
    ctx = R.stream_context("p16", pt)
    starts = UJ.start_choice(len(pt["blocks"]), n_starts)
    out, ts = {}, None
    for plan, corner in (("TS", "reference"), ("LU", T.STRICT), ("DT", T.STRICT), ("FP", T.STRICT), ("QP", T.STRICT)):
        s = T.settings_for(plan, corner)
        blocks, ref, _ = R.arm_inputs(pt, pt, s, "point")
        cj, kw = R.cell_job(pt, s, blocks)
        t0 = time.time()
        cell = R.run_cell("p16", "point", off, cj, s, starts, kw, ref, direct=True, ctx=ctx,
                          ts=None if ts is None else ts["compact"], keep_ts=plan == "TS")
        t_pass = time.time() - t0
        if cell["problems"]:
            raise SystemExit(f"{plan}: {cell['problems'][:3]}")
        t0 = time.time()
        outs = R.reading_outs(cell, "p16", "point", off, s)
        srows, table = UR.summary("p16", "point", off, outs, blocks=UR.READING_BLOCKS)
        recs = [o["rec"] for o in outs]
        R.count_rows(cell["stats"], recs)
        R.u1_reported_rows(recs)
        t_read = time.time() - t0
        t_pair = t_grid = 0.0
        if ts is not None:
            t0 = time.time()
            R.paired_rows(recs, ts["recs"], coverage=False)
            R.paired_scorecard_rows(recs, ts["recs"])
            R.u1_reported_rows(recs, paired_with=ts["recs"])
            R.u1_reported_rows(ts["recs"], paired_with=recs)
            R.diverge_rows(cell["stats"], ts["stats"], recs)
            t_pair = time.time() - t0
            if plan != "LU":
                t0 = time.time()
                rows, _ = R.grid_rows(cell, "p16", "point", off, s, ts["recs"])
                t_grid = time.time() - t0
                out[f"{plan}_break_even_recompositions"] = sum(r.get("n", 0) for r in rows
                                                               if r["subsection"] == "break_even")
                plain, _ = R.grid_rows(cell, "p16", "point", off, s, ts["recs"], search="plain")
                # the second build's search recomposed at every call of every measure
                out[f"{plan}_break_even_calls_plain"] = sum(r.get("measure_calls", 0) for r in plain
                                                            if r["subsection"] == "break_even")
                out[f"{plan}_grid_prices"] = len({r["price"] for r in rows if r["subsection"] == "price_grid"})
        else:
            ts = {"recs": recs, "stats": cell["stats"], "compact": cell["ts"]}
            t0 = time.time()                                  # the second build's two passes, on the same starts
            R.F.run_plan("p16", "point", off, cj, s, starts, kw, point=ref)
            for st in starts:
                R.direct_start("p16", "point", off, cj, s, int(st), kw, ref, 1)
            out["TS_two_pass_s_per_start"] = round((time.time() - t0) / len(starts), 3)
        trades = sum(x.get("trades_taken", 0) for x in cell["stats"].values())
        out[plan] = {"starts": len(starts), "s_per_start_pass": round(t_pass / len(starts), 3),
                     "s_per_start_readings": round(t_read / len(starts), 3),
                     "s_per_start_pairing": round(t_pair / len(starts), 3),
                     "s_per_start_grid": round(t_grid / len(starts), 3),
                     "trades_per_start": round(trades / len(starts), 1)}
    return out


def stage_ladder(n_starts: int) -> dict:
    import user_journey as UJ

    from extended import firm_reading as R
    from extended import firm_terms as T
    from extended import user_beside as B
    from extended import user_readings as UR

    stream, _ = setup()
    job = stream["jobs"]["verdict"]
    starts = UJ.start_choice(len(job["blocks"]), n_starts)
    out = {}
    for plan, corner in (("TS", "reference"), ("DT", T.STRICT), ("QP", T.STRICT)):
        s = T.settings_for(plan, corner)
        blocks, ref, _ = R.arm_inputs(stream["jobs"]["point"], job, s, "verdict", stream["delta"]["verdict"])
        cj, kw = R.cell_job(job, s, blocks, ladder=True)
        resp = B.BY_NAME["denial_10"]
        t0 = time.time()
        cell = R.run_cell("p16", "verdict", resp, cj, s, starts, kw, ref, direct=s.plan == "DT")
        outs = R.reading_outs(cell, "p16", "verdict", resp, s)
        UR.summary("p16", "verdict", resp, outs, blocks=UR.READING_BLOCKS)
        out[plan] = {"starts": len(starts), "s_per_start": round((time.time() - t0) / len(starts), 3)}
    return out


def stage_gate(n_paths: int) -> dict:
    import numpy as np

    from extended import firm_reading as R
    from extended import firm_terms as T
    from extended.gate import run_gate

    stream, k = setup()
    pt = stream["jobs"]["point"]["blocks"]
    e_by = {R_: float(np.nanmean(np.concatenate([b.r_by_rr[R_] for b in pt if len(b.pnl)]))) for R_ in RS}
    lb_by = {R_: e_by[R_] + k["delta"][R_] for R_ in RS}
    kw = dict(e=e_by[2.0], lb=lb_by[2.0], e_by_rr=e_by, lb_by_rr=lb_by, protocol=k["proto"], bankroll=1e6,
              horizon_days=504, n_paths=int(n_paths), seed=R.F.LADDER_SEED + 2, accounts=5, sizing=k["sizing"],
              rules=k["rules"], levels=(0.0,), risk_policy=k["policy"], purchase_budget=(20, 21), rtp=False)
    out = {}
    for plan in ("DT", "QP"):
        s = T.settings_for(plan, T.STRICT)
        t0 = time.time()
        R.gate_rows(pt, kw, s, run_gate, fresh_rr=2.0)
        out[plan] = {"paths": int(n_paths), "s_per_path_all_four_arms": round((time.time() - t0) / n_paths, 3)}
    return out


def stage_coverage(n_series: int) -> dict:
    from extended import firm_uncertainty as FU

    out = {}
    for h, nw in ((63, 13), (126, 6)):
        t0 = time.time()
        FU.coverage("persistent_p0.05_s0.0025", h=h, n_w=nw, n_series=int(n_series), seed=FU.SEED)
        out[f"{h}:{nw}"] = {"series": int(n_series), "ms_per_series": round(1000 * (time.time() - t0) / n_series, 3),
                            "shapes": len(FU.coverage_shapes())}
    return out


def stage_files(n_starts: int) -> dict:
    """The reading's files at the run's structure: the toy run's own rows (their shapes and columns) with each of its
    16 scorecard run-arms carried to `n_starts` start rows (consecutive start days and their dates, U1's observed
    sessions), its summary rows as they are; built through the spill and read back as the run does, the CSV written,
    and the menu step on it. The run has 68 scorecard run-arms and 27 ladder cells: its menu scales with the
    run-arms, its CSV with the rows."""
    import numpy as np
    import pandas as pd

    from extended import firm_menu as FM
    import rd01_reading as RDR

    with tempfile.TemporaryDirectory(prefix="rd01_probe_") as td:
        dump = Path(td) / "toy.pkl"
        env = {**__import__("os").environ, "RD01_PROBE_DUMP": str(dump), "OMP_NUM_THREADS": "1"}
        subprocess.run([sys.executable, str(ROOT / "tests" / "rd01_reading_synthetic.py"), str(ROOT)],
                       capture_output=True, text=True, timeout=1800, env=env, check=True)
        base = pd.read_pickle(dump)
        dates = [d.date().isoformat() for d in pd.bdate_range("2020-01-02", periods=int(n_starts))]
        sp = RDR.Spill(Path(td) / "rows")
        sp.add(base[base["subsection"] != "start"].to_dict("records"))
        cells = 0
        for _, g in base[(base["subsection"] == "start") & (base["section"] == "scorecard")].groupby(["run", "arm"]):
            idx = np.arange(int(n_starts)) % len(g)
            x = g.iloc[idx].copy()
            x["start_day"] = np.arange(int(n_starts))
            x["start_date"] = dates
            x["observed"] = np.minimum(252, int(n_starts) - np.arange(int(n_starts)))
            sp.add(x.to_dict("records"))
            cells += 1
        t0 = time.time()
        fr = RDR.frame(sp, RDR.SECTIONS)
        t_frame = time.time() - t0
        n_rows = len(fr)
        t0 = time.time()
        p = Path(td) / "fc_reading.csv"
        fr.to_csv(p, index=False)
        t_csv = time.time() - t0
        size = p.stat().st_size
        del fr, sp
        t0 = time.time()
        back = pd.read_csv(p, low_memory=False)
        menu = FM.menu(back, None)
        t_menu = time.time() - t0
    return {"scorecard_run_arms": cells, "starts_each": int(n_starts), "rows": n_rows, "menu_rows": len(menu),
            "csv_mb": round(size / 2 ** 20, 1), "s_frame": round(t_frame, 1), "s_csv": round(t_csv, 1),
            "s_read_and_menu": round(t_menu, 1)}


def peak() -> str | None:
    import stage2_identity as SI

    return SI.peak_memory()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--stage", choices=STAGES, default=None)
    ap.add_argument("--starts", type=int, default=12)
    ap.add_argument("--paths", type=int, default=4)
    ap.add_argument("--series", type=int, default=400)
    ap.add_argument("--files-starts", type=int, default=N_SESSIONS)
    a = ap.parse_args(argv)
    if a.stage is None:
        for st in STAGES:
            p = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--stage", st, "--starts", str(a.starts),
                                "--paths", str(a.paths), "--series", str(a.series), "--files-starts", str(a.files_starts)],
                               capture_output=True, text=True, timeout=7200)
            line = [x for x in p.stdout.splitlines() if x.startswith("{")]
            print(line[-1] if line else json.dumps({"stage": st, "failed": p.stderr[-2000:]}), flush=True)
        return 0
    from extended import use_vendored_stage2

    use_vendored_stage2()
    t0 = time.time()
    fn = {"scorecard": lambda: stage_scorecard(a.starts), "ladder": lambda: stage_ladder(a.starts),
          "gate": lambda: stage_gate(a.paths), "coverage": lambda: stage_coverage(a.series),
          "files": lambda: stage_files(a.files_starts)}[a.stage]
    res = fn()
    print(json.dumps({"stage": a.stage, "seconds": round(time.time() - t0, 1), "peak": peak(), **res}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
