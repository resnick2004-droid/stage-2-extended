"""Read the R028 cloud re-score of Test 1 and apply D-122's declared verdict rule.

    python scripts/rescore_test1.py

Step 1, the port check: the cloud's `close`-fill results must reproduce Test 1's diagnosis
(`results/test1_diagnosis.csv`): the same trade counts and the same directional part and net result
to within the 6-decimal export. If they do not, the script stops: the cloud did not compute what
the repository computed, and the corrected numbers would mean nothing.

Step 2, the experiment: the directional part (zero-cost real minus mirror, halved) in the 12
plain-entry cells, Test 1 (`close`) against the corrected fill (`next_open`), day-paired 90 % normal
intervals as in the diagnosis. Verdict, as declared in D-122 before the run:

  measurement-robust  every corrected plain-entry directional part is at or below its Test 1 90 % upper
                      bound and every corrected upper bound is below the +0.23 needed for e >= 0.10
  method-dependent    any corrected plain-entry directional part rises above its Test 1 90 % upper bound,
                      or any corrected lower bound is above zero

Structural cells are reported, not verdict-bearing (too few trades, D-121 P5). Writes
results/test1_rescore.csv (exploratory).
"""
from __future__ import annotations

import math
import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from propedge.outcomes import open_reversion as orv  # noqa: E402
from propedge.reporting.results import read_result, write_result  # noqa: E402

EVIDENCE = ROOT / "results" / "manual_R028_openrev_rescore.csv"
REQUIRED_D = 0.23                     # D-121: the directional part needed for e >= 0.10 after costs
Z90 = 1.6448536269514722
PORT_TOL = 2e-5                       # 6-decimal export of each trade, averaged


def _ci(x):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    if len(x) < 2:
        return float("nan"), float("nan"), float("nan"), len(x)
    se = x.std(ddof=1) / math.sqrt(len(x))
    return float(x.mean()), float(x.mean() - Z90 * se), float(x.mean() + Z90 * se), len(x)


def main() -> int:
    warnings.filterwarnings("ignore")
    cfg = orv.load_design()
    keys = [v["key"] for v in orv.variants(cfg)]
    df = read_result(EVIDENCE)
    days = df[df["cell"] == -1].sort_values("n").reset_index(drop=True)
    days["reason"] = orv.status_from_days(days)
    ok = set(days.loc[days["reason"] == "", "n"])
    cells = df[(df["cell"] >= 0) & df["n"].isin(ok)].copy()
    cells["variant"] = cells["variant_i"].astype(int).map(dict(enumerate(keys)))
    rows = []
    for (fill, scale, entry, variant), g in cells.groupby(["fill", "scale", "entry", "variant"]):
        both = g[g["zr"].notna() & g["zm"].notna()]
        net = g[g["zr"].notna() & g["fu"].notna()]
        for stat, x in (("directional_d", (both["zr"] - both["zm"]) / 2), ("symmetric_s", (both["zr"] + both["zm"]) / 2),
                        ("net_u", net["fu"]), ("price_only_u", net["zr"])):
            m, lo, hi, n = _ci(x)
            rows.append({"fill": fill, "scale": scale, "entry": entry, "variant": variant, "statistic": stat,
                         "mean": m, "lo90": lo, "hi90": hi, "n": n})
    out = pd.DataFrame(rows)

    # ---- step 1: the port check against Test 1
    diag = read_result(ROOT / "results" / "test1_diagnosis.csv")
    diag = diag[diag["section"].isin(["decomp", "direction"])]
    scale_map = {"P_ref_4000": "P_ref_4000", "actual": "actual"}
    mism = []
    for r in out[out["fill"] == "close"].itertuples():
        stat = {"directional_d": "directional_d", "net_u": "net_u", "price_only_u": "price_only_u"}.get(r.statistic)
        if stat is None:
            continue
        ref = diag[(diag["variant"] == r.variant) & (diag["baseline"] == r.entry) &
                   (diag["scale"] == scale_map[r.scale]) & (diag["statistic"] == stat)]
        if len(ref) != 1:
            mism.append((r.variant, r.entry, r.scale, stat, "missing in diagnosis"))
            continue
        ref = ref.iloc[0]
        if int(ref["n"]) != int(r.n) or abs(float(ref["mean"]) - r.mean) > PORT_TOL:
            mism.append((r.variant, r.entry, r.scale, stat, f"n {int(ref['n'])} vs {r.n}, "
                                                            f"mean {float(ref['mean']):+.6f} vs {r.mean:+.6f}"))
    port_ok = not mism
    print("port check:", "PASS" if port_ok else f"FAIL ({len(mism)} mismatches)")
    for m in mism[:12]:
        print("  ", m)

    # ---- step 2: the declared verdict
    verdict_rows = []
    verdict = "not computed: the port check failed" if not port_ok else None
    if port_ok:
        robust, dependent = True, False
        for scale in ("actual", "P_ref_4000"):
            for v in keys:
                sel = lambda fill: out[(out["fill"] == fill) & (out["scale"] == scale) &   # noqa: E731
                                       (out["entry"] == "baseline") & (out["variant"] == v) &
                                       (out["statistic"] == "directional_d")].iloc[0]
                old, new = sel("close"), sel("next_open")
                rises = new["mean"] > old["hi90"]
                positive = new["lo90"] > 0
                reaches = new["hi90"] >= REQUIRED_D
                robust &= not (rises or reaches or positive)
                dependent |= bool(rises or positive)
                verdict_rows.append({"fill": "compare", "scale": scale, "entry": "baseline", "variant": v,
                                     "statistic": "d_change", "mean": new["mean"] - old["mean"],
                                     "lo90": float("nan"), "hi90": float("nan"), "n": int(new["n"]),
                                     "rises_above_test1_upper": bool(rises), "reliably_positive": bool(positive),
                                     "reaches_required": bool(reaches)})
        verdict = ("measurement-robust" if robust else "method-dependent" if dependent
                   else "neither: a corrected upper bound reached the required +0.23 without rising above Test 1's")
    print("verdict:", verdict)
    result = pd.concat([out, pd.DataFrame(verdict_rows),
                        pd.DataFrame([{"fill": "verdict", "statistic": "D-122", "variant": verdict,
                                       "n": len(ok), "port_check": "pass" if port_ok else "fail"}])],
                       ignore_index=True)
    write_result(result, "test1_rescore", script="scripts/rescore_test1.py", seed=None, require_seed=False,
                 exploratory=True,
                 parameters={"evidence": str(EVIDENCE.relative_to(ROOT)), "design": "config/open_reversion.yaml",
                             "required_directional": REQUIRED_D, "port_tolerance": PORT_TOL,
                             "reference": "results/test1_diagnosis.csv"},
                 notes={"decision": "D-122 (declared before the run)",
                        "status": "EXPLORATORY; development data; learning exercise (D-118)",
                        "port_mismatches": [" | ".join(map(str, m)) for m in mism[:20]]},
                 description="Test 1 re-scored in QuantConnect: close vs next-open fills, directional part and "
                             "net result per cell, the port check against Test 1, and D-122's verdict. "
                             "Deterministic.")
    base = out[(out["entry"] == "baseline") & (out["statistic"] == "directional_d")]
    print(base.pivot_table(index=["scale", "variant"], columns="fill", values=["mean", "hi90"]).round(3).to_string())
    return 0 if port_ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
