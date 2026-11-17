"""m1 (the red team's build review of RD-03): the reading's pipeline, steps 3, 4 and 5, `--synthetic` on a small toy into a
temporary folder, and M1 to M4 asserted on the files it writes. Prints one JSON line.

    python tests/cl_run_check.py <repository root> <a temporary folder>
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

problems: list[str] = []
DAYS = "70"


def step(n: int) -> str:
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "cl_reading.py"), "--step", str(n), "--synthetic",
                        "--results-dir", str(OUT), "--days", DAYS, "--paths", "3"], cwd=ROOT, capture_output=True,
                       text=True, timeout=3000)
    if "EXIT 0" not in r.stdout:
        problems.append(f"step {n} did not run: {r.stdout[-1500:]} {r.stderr[-1500:]}")
    return r.stdout


for n in (3, 4, 5):
    step(n)
if not problems:
    from extended import levers_readings as LR
    from extended import results as XR

    names = ("cl_reading", "cl_gate", "cl_menu", "cl_reading_ladder", "cl_reading_ftp", "cl_menu_beside")
    f = {}
    for n in names:
        p = OUT / f"{n}_synthetic.csv"
        ok, msg = XR.verify_result(p) if p.is_file() else (False, "absent")
        if not ok:
            problems.append(f"{n}: {msg}")
        else:
            f[n] = pd.read_csv(p, low_memory=False)
    house = ("house_stop_none", "house_stop_30", "house_zero_none", "house_zero_30")
    from extended import cl_reading as CL

    for n in ("cl_menu", "cl_menu_beside"):                          # M2, M3: no P without its guard row
        m = f.get(n)
        if m is None or not len(m):
            problems.append(f"{n}: empty")
            continue
        try:
            CL.check_menu(m)
        except CL.Refused as exc:
            problems.append(f"{n}: {exc}")
        for _, r in m.iterrows():
            if np.isfinite(float(r.get("P_level", np.nan))):
                bad = [g for g in CL.GATE_GUARD if not np.isfinite(float(r.get(f"guard_{g}", np.nan)))]
                if bad:
                    problems.append(f"{n}: {r['design']} {r['cell']} {r.get('response')}: P beside no gate entry {bad}")
                    break
    for n in ("cl_reading", "cl_reading_ladder", "cl_reading_ftp"):    # M4: every house-money row labelled
        t = f.get(n)
        if t is None:
            continue
        hm = t[t["cell"].astype(str).isin(house) | t["base"].astype(str).isin(house)]
        bad = hm[~hm["note"].fillna("").str.contains(LR.LABEL_GAMING_P, regex=False)]
        if (len(hm) == 0 and n != "cl_reading_ftp") or len(bad):     # step 5 runs no house-money cell
            problems.append(f"{n}: {len(bad)} of {len(hm)} house-money rows unlabelled")
    g, m = f.get("cl_gate"), f.get("cl_menu")                      # M1: the entry is D-312's column
    if g is not None and m is not None:
        rows = g[(g["part"] == "row") & (g["twin"].astype(str) == "False") & (g["shift"] == "lower_bound")]
        for _, r in m[m["cell"] != "ref"].iterrows():
            x = rows[(rows["design"] == r["design"]) & (rows["cell"] == r["cell"])]
            if len(x) != 1 or abs(float(x["pf_growth_on_base_p50"].iloc[0]) -
                                  float(r["guard_growth_on_required_bankroll"])) > 1e-12:
                problems.append(f"M1: {r['design']} {r['cell']}: the guard's growth is not the gate's "
                                "pf_growth_on_base_p50")
                break
        refs = m[m["cell"] == "ref"]
        if not len(refs) or not refs["guard_gate_label"].astype(str).str.contains("registered gate").all():
            problems.append("M2: ref's gate entry is not its registered row")
    # m7: a rerun into the same folder refuses before anything runs
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "cl_reading.py"), "--step", "3", "--synthetic",
                        "--results-dir", str(OUT), "--days", DAYS], cwd=ROOT, capture_output=True, text=True,
                       timeout=600)
    if "already exist" not in r.stdout:
        problems.append("m7: a second run into the same folder did not refuse first")

print(json.dumps({"problems": problems}))
