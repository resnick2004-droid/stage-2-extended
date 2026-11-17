"""Q-108d: the build's measurement of the two runs' cost (the plan's 6.2-6.3: "the lock's hours are set from the
build's measurement") -- on realistic synthetic sizes, never on data. Seeds 81080150-81080159 (outside the program's
2026 space; this script's own).

    python docs/calibration/scripts/q108d/q108_measure.py --out <folder outside the tree>

**The inputs:** synthetic pairs on 657 judged sessions with 141 offers a session (92,637 offers), both sides walked
at 1, 1.5 and 3R with a probit session effect (Q-16's icc 0.35) and a small long-minus-short drift (a mean pair
difference near +0.02 at 1R), so the lax candidates reject more than nominal on the persistent nulls and the scalar
re-decision has rejections to re-decide.

**What it measures:** a sample of each part's nulls at the runs' full replication counts (200,000 in the rule,
100,000 beside), each part's sample in its own process (`--part`), as `scripts/q108_calibrate.py` runs them: every
null's seconds, and each process's peak working set. Then C8's reference (2,000,000 draws) in its own process, and the
parent's aggregation on a full-size table (`--aggregate`). The calibration runs all ten candidates; the validation the
chosen one and C0 (`--validation`, two candidates).

**What it prints:** per null its seconds; per part its peak; the totals, each null kind's mean seconds times its count
in the plan (`null_plan`): the run's time computed from measured per-null times.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

from extended.procmem import working_set_mb  # noqa: E402

BASE = 81080150


def _cal():
    name = "q108_calibrate_measure"
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / "q108_calibrate.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def seeds(C) -> dict:
    s = {r: BASE + i for i, r in enumerate(C.CAL_ROLES)}
    s["tests"] = BASE + 9
    return s


def synthetic_pairs(n: int = 657, per: int = 141, drift: float = 0.04):
    """(pairs frame as `load_pairs` gives it, n): `per` offers a session, vectorised."""
    g = np.random.default_rng([BASE, 0])
    days = pd.bdate_range("2024-01-02", periods=n).strftime("%Y-%m-%d")
    ses = np.repeat(np.arange(n), per)
    slot = np.tile(np.arange(per) * 3, n)
    a = g.standard_normal(n)[ses] * np.sqrt(0.35)
    m = len(ses)
    out = {"date": np.asarray(days)[ses], "slot": slot, "coin": g.choice([-1, 1], size=m), "session": ses}
    for R in (1.0, 1.5, 3.0):
        pl = stats.norm.cdf((a + drift) / np.sqrt(0.65)) * 0.9
        ps = stats.norm.cdf((-a - drift) / np.sqrt(0.65)) * 0.9
        kl = (g.random(m) < pl).astype(int)
        ks = (g.random(m) < ps).astype(int)
        kl = np.where((kl == 0) & (g.random(m) < 0.2), 2, kl)
        ks = np.where((ks == 0) & (g.random(m) < 0.2), 2, ks)
        out[f"kl_{R:g}"], out[f"ks_{R:g}"] = kl, ks
        out[f"rl_{R:g}"] = np.where(kl == 1, R - 0.05, np.where(kl == 2, g.uniform(-1, R, m), -1.05))
        out[f"rs_{R:g}"] = np.where(ks == 1, R - 0.05, np.where(ks == 2, g.uniform(-1, R, m), -1.05))
        out[f"xl_{R:g}"] = slot + 1 + g.integers(5, 60, m)
        out[f"xs_{R:g}"] = slot + 1 + g.integers(5, 60, m)
    p = pd.DataFrame(out).sort_values(["date", "slot"], kind="stable").reset_index(drop=True)
    return p, n


SAMPLES = {
    "fixed": [f"fixed:offered:win1:{m}" for m in ("flip1", "flip5", "flip21", "coin", "markov30", "markov50",
                                                   "markov80", "flip42", "flip55", "flip63", "alt45", "alt55")]
             + [f"fixed:taken:net3:{m}" for m in ("flip1", "markov80", "flip42", "flip63", "alt55")],
    "sub0": [f"sub:200:00:win1:{m}" for m in ("flip1", "flip5", "flip21", "coin", "flip42", "flip55", "flip63",
                                              "alt45", "alt55", "markov30", "markov50", "markov80")]
            + [f"sub:200:05:net3:{m}" for m in ("flip21", "flip42", "markov80")],
    "sub4": [f"sub:5000:00:win1:{m}" for m in ("flip1", "flip5", "flip21", "coin", "flip42", "flip55", "flip63",
                                               "alt45", "alt55", "markov30", "markov50", "markov80")]
            + [f"sub:5000:05:net3:{m}" for m in ("flip21", "flip42", "markov80")],
    "syn": [f"syn:{m}:1000" for m in ("iid", "cluster", "cluster_ar1", "regime01", "volclust")] + ["syn:volclust:5000"],
    "cp": ["cp:ar98s15:1000:win1:persist1", "cp:burst10x:5000:win1:persist21", "cp:ar98s15:200:net3:persist1",
           "cp:burst10x:2000:net3:persist1"],
    "flat": ["flat:1000:win1:flip42", "flat:1000:net3:flip42"],
}


def kind_of(e: dict) -> str:
    if e["group"] in ("fixed", "subset"):
        return f"{e['group']}:{e['kind']}:{e['model']}"
    if e["group"] in ("beside_cp", "beside_flat"):
        return f"{e['group']}:{e['engine']}"
    return e["group"]


def run_part(part: str, out: Path, cands) -> int:
    C = _cal()
    p, n = synthetic_pairs()
    sd = seeds(C)
    sn = C.O.sn_reference([sd["sn_table"], 0], draws=200_000, n=n)            # a stand-in table (its own cost below)
    real_part = part if part in C.PARTS else part
    rows = []
    t0 = time.time()
    res = C.compute_part(real_part, None if part == "syn" else p, n, C.REPS, sd, cands, sn, only=set(SAMPLES[part]),
                         log=lambda m: print(m, flush=True))
    for t in res["meta"]["timing"]:
        rows.append(t)
    plan = {x["null"]: x for x in C.null_plan(sd)}
    for r in rows:
        r["kind_key"] = kind_of(plan[r["null"]])
    info = {"part": part, "candidates": cands, "seconds": time.time() - t0, "peak_mb": working_set_mb(peak=True),
            "nulls": len(rows), "scalar_checked": res["meta"]["scalar_checked"],
            "scalar_mismatched": res["meta"]["scalar_mismatched"], "rows": rows}
    (out / f"part_{part}_{len(cands)}.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
    print(f"PART {part} ({len(cands)} candidates): {len(rows)} nulls, {info['seconds']:.0f} s, peak "
          f"{info['peak_mb']:.0f} MB, re-decided {info['scalar_checked']}, mismatched {info['scalar_mismatched']}",
          flush=True)
    return 0


def run_sn(out: Path) -> int:
    C = _cal()
    t0 = time.time()
    C.O.sn_reference([seeds(C)["sn_table"], 0])
    info = {"seconds": time.time() - t0, "peak_mb": working_set_mb(peak=True)}
    (out / "sn.json").write_text(json.dumps(info), encoding="utf-8")
    print(f"SN reference: {info['seconds']:.0f} s, peak {info['peak_mb']:.0f} MB", flush=True)
    return 0


def run_aggregate(out: Path) -> int:
    """The parent's step at full size: a size table of every null x candidate x scope (counts drawn at random, the
    exact ones as numerators), the eligibility, P, the choice, the spread rows; its seconds, peak and CSV bytes."""
    C = _cal()
    g = np.random.default_rng([BASE, 1])
    plan = C.null_plan(seeds(C))
    rows = []
    t0 = time.time()
    for e in plan:
        den = (C.REPS if e["in_rule"] else C.REPS_BESIDE) if e["kind"] == "mc" else 42 * 2 ** 17
        cnt = {}
        for c in C.O.NAMES:
            for s_ in C.SCOPES:
                fam = np.sort(g.poisson(20, size=8))[::-1] if e["kind"] == "mc" else np.zeros(8, int)
                cnt[(c, s_)] = np.r_[fam, np.sort(g.poisson(200, size=4))]
        res = {"counts": cnt, "den": den, "admitted": den // 2, "trades_mean": 1000.0, "nontie_mean": 300.0}
        rows += C.size_rows(e, res, list(C.O.NAMES))
    t_rows = time.time() - t0
    t0 = time.time()
    size = pd.DataFrame(rows)
    power = []
    for e in plan:
        if e["toy"]:
            for c in C.O.NAMES:
                for s_ in C.SCOPES:
                    for k in C.POWER_KS:
                        power.append({"row": "toy", "null": e["null"], "toy": e["toy"], "candidate": c, "scope": s_,
                                      "k": k, "mdl50": 0.05, "mdl80": 0.08})
    res = C.calibrate_tables([{"size": rows, "power": power, "mismatches": [], "meta": {"nesting_violations": []}}],
                             list(C.O.NAMES))
    secs = time.time() - t0
    f = out / "q108_cal_size_fullsize.csv"
    res["size_out"].to_csv(f, index=False)
    info = {"seconds": secs, "rows_seconds": t_rows, "peak_mb": working_set_mb(peak=True),
            "size_rows": len(res["size_out"]),
            "size_csv_bytes": f.stat().st_size, "choice": res["choice"]["line"], "failed": res["failed"]}
    f.unlink()
    (out / "aggregate.json").write_text(json.dumps(info), encoding="utf-8")
    print(f"AGGREGATE: {secs:.0f} s, peak {info['peak_mb']:.0f} MB, q108_cal_size.csv {info['size_rows']} rows, "
          f"{info['size_csv_bytes'] / 2**20:.1f} MB", flush=True)
    return 0


def summarise(out: Path) -> int:
    C = _cal()
    plan = C.null_plan(seeds(C))
    counts = {}
    for e in plan:
        counts[kind_of(e)] = counts.get(kind_of(e), 0) + 1
    report = {}
    for nc, label in ((10, "calibration"), (2, "validation")):
        per = {}
        peaks = {}
        for f in sorted(out.glob(f"part_*_{nc}.json")):
            d = json.loads(f.read_text(encoding="utf-8"))
            peaks[d["part"]] = d["peak_mb"]
            for r in d["rows"]:
                per.setdefault(r["kind_key"], []).append(r["seconds"])
        total = 0.0
        lines = []
        for k, cnt in sorted(counts.items()):
            if k not in per:
                lines.append(f"  {k}: {cnt} nulls, NOT MEASURED")
                continue
            m = float(np.mean(per[k]))
            total += m * cnt
            lines.append(f"  {k}: {cnt} nulls x {m:.1f} s (measured on {len(per[k])}) = {m * cnt / 3600:.2f} h")
        sn = json.loads((out / "sn.json").read_text(encoding="utf-8")) if label == "calibration" else None
        if sn:
            total += sn["seconds"]
        print(f"{label}: {total / 3600:.2f} h of null computation" + (f" (C8's table {sn['seconds']:.0f} s)" if sn
                                                                      else "") + f"; part peaks {peaks}")
        print("\n".join(lines))
        report[label] = {"hours": total / 3600, "peaks_mb": peaks, "per_kind_s": {k: float(np.mean(v))
                                                                                  for k, v in per.items()}}
    (out / "summary.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--part", default=None)
    ap.add_argument("--validation", action="store_true")
    ap.add_argument("--sn", action="store_true")
    ap.add_argument("--aggregate", action="store_true")
    ap.add_argument("--summarise", action="store_true")
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    if a.part:
        C = _cal()
        return run_part(a.part, a.out, ["cons_m1.5", "cons"] if a.validation else list(C.O.NAMES))
    if a.sn:
        return run_sn(a.out)
    if a.aggregate:
        return run_aggregate(a.out)
    if a.summarise:
        return summarise(a.out)
    for args in [["--sn"]] + [["--part", p] for p in SAMPLES] + [["--part", p, "--validation"] for p in SAMPLES] \
            + [["--aggregate"], ["--summarise"]]:
        r = subprocess.run([sys.executable, __file__, "--out", str(a.out), *args])
        if r.returncode:
            return r.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
