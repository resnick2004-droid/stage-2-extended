"""m1 (the red team's build review of RD-03): the reading's pipeline, steps 3, 4 and 5, `--synthetic` on a small toy into a
temporary folder, and M1 to M4 asserted on the files it writes; cycle 3: R2 (U-6's label by variant), m-a (the guard
excuse only where a horizon exceeds the toy's sessions), note 2 (every gate label "the gate at 0 %") and the window
measurement's `--starts` (step 4 on every 5th start, into a folder of its own). Prints one JSON line.

    python tests/cl_run_check.py <repository root> <a temporary folder>
"""
from __future__ import annotations

import json
import shutil
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


def _expect_excused() -> set[str]:
    """m-a: the guard entries with no start on a DAYS-session toy -- those whose month's horizon exceeds DAYS."""
    from extended import cl_reading as CL
    from extended import pp_reading as RD

    return {g for g in CL.GUARD_COLUMNS if RD.month_horizon(int(g.split("_m")[1].split("_")[0])) > int(DAYS)}


def refused_strict(m) -> bool:
    """The real run's check (no excuse) refuses a toy menu that excuses entries."""
    from extended import cl_reading as CL

    try:
        CL.check_menu(m)
    except CL.Refused:
        return True
    return False


def step(n: int, out: Path = OUT, extra: tuple[str, ...] = ()) -> str:
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "cl_reading.py"), "--step", str(n), "--synthetic",
                        "--results-dir", str(out), "--days", DAYS, "--paths", "3", *extra], cwd=ROOT,
                       capture_output=True, text=True, timeout=3000)
    if "EXIT 0" not in r.stdout:
        problems.append(f"step {n} did not run: {r.stdout[-1500:]} {r.stderr[-1500:]}")
    return r.stdout


for n in (3, 4, 5):
    step(n)
from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()
EXPECT_EXCUSED = _expect_excused()
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
            CL.check_menu(m, excuse_guard=True)
        except CL.Refused as exc:
            problems.append(f"{n}: {exc}")
        if not refused_strict(m):
            problems.append(f"{n}: the real run's check accepts the toy's excused rows (m-a)")
        for _, r in m.iterrows():                                  # m-a: excused exactly where a horizon exceeds DAYS
            if not np.isfinite(float(r.get("P_level", np.nan))):
                continue
            got = set(CL.excused_names(r.get("guard_reason")))
            if got != EXPECT_EXCUSED:
                problems.append(f"{n}: {r['design']} {r['cell']} {r.get('response')}: excused {sorted(got)}, not the "
                                f"entries whose horizon exceeds {DAYS} sessions {sorted(EXPECT_EXCUSED)} (m-a)")
                break
        lab = m[np.isfinite(m["P_level"].astype(float))]["guard_gate_label"].astype(str)   # note 2
        if not len(lab) or not lab.str.contains("the gate at 0 %", regex=False).all():
            problems.append(f"{n}: a gate entry's label lacks 'the gate at 0 %' (note 2)")
        for _, r in m[m["cell"].isin(CL.B2F_CELLS)].iterrows():   # R2: one U-6 label, its variant's
            parts = str(r["labels"]).split("; ")
            want = CL.u6_label("" if r["variant"] == "declared" else str(r["variant"]))
            if parts.count(want) != 1 or sum(parts.count(x) for x in CL.U6_LABELS) != 1:
                problems.append(f"{n}: {r['design']} {r['cell']} {r['response']} {r['variant']}: U-6's labels (R2)")
                break
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
    t = f.get("cl_reading_ftp")                                    # R2: U-6's label on every Back2Funded row
    if t is not None:
        notes = t["note"].fillna("").astype(str).str.split("; ")
        b2f = (t["cell"].astype(str).str.split(",").apply(lambda xs: any(x in CL.B2F_CELLS for x in xs))
               | t["base"].astype(str).isin(CL.B2F_CELLS) | (t["mode"].astype(str) == CL.CONSERVATIVE))
        if not b2f.any() or not (t["mode"].astype(str) == CL.CONSERVATIVE).any():
            problems.append("cl_reading_ftp: no Back2Funded rows of both variants to label (R2)")
        for i in np.flatnonzero(b2f.to_numpy()):
            parts = notes.iloc[i]
            want = CL.u6_label("" if t["mode"].iloc[i] == "declared" else str(t["mode"].iloc[i]))
            if parts.count(want) != 1 or sum(parts.count(x) for x in CL.U6_LABELS) != 1:
                problems.append(f"cl_reading_ftp: row {i} ({t['cell'].iloc[i]}, {t['mode'].iloc[i]}): U-6's labels "
                                "(R2)")
                break
        other = [i for i in np.flatnonzero(~b2f.to_numpy()) if any(x in CL.U6_LABELS for x in notes.iloc[i])]
        if other:
            problems.append(f"cl_reading_ftp: {len(other)} rows naming no Back2Funded cell carry a U-6 label (R2)")
    for n in ("cl_reading_ladder", "cl_reading_ftp"):                # cycle 4's m1: the beside rates a year
        t = f.get(n)
        if t is None:
            continue
        r = t[(t["part"] == "mechanics") & t["measure"].astype(str).str.endswith("_per_year")]
        v = r["value"].astype(float)
        labelled = r["note"].fillna("").astype(str).str.startswith(CL.NO_FULL_YEAR) & (r["n"].astype(float) == 0)
        ok = (v.isna() & labelled).all() if int(DAYS) < 252 else (np.isfinite(v) & ~labelled).all()
        if not len(r) or not ok:
            problems.append(f"{n}: the beside rates a year are not NaN and labelled '{CL.NO_FULL_YEAR}' exactly where "
                            f"--days {DAYS} is under 252 (m1)")
    mb = f.get("cl_menu_beside")
    if mb is not None and len(mb):
        nan = ~np.isfinite(mb["evaluations_bought_per_year"].astype(float))
        if (mb.loc[nan, "per_year_note"].fillna("").astype(str) == "").any():
            problems.append("cl_menu_beside: a rate a year printed NaN without its reason (m1)")
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
    # the window measurement: step 4 on every 5th start, beside step 3's gate file, in a folder of its own
    thin = OUT / "thin"
    thin.mkdir()
    for x in (OUT / "cl_gate_synthetic.csv", XR.manifest_path_for(OUT / "cl_gate_synthetic.csv")):
        if x.is_file():
            shutil.copy(x, thin / x.name)
    step(4, thin, ("--starts", "5"))
    p = thin / "cl_reading_ladder_synthetic.csv"
    if p.is_file():
        par = XR.read_manifest(p).parameters
        want = len(range(0, int(DAYS), 5))
        counts = par.get("start_counts") or {}
        if par.get("start_every") != 5 or not counts or set(counts.values()) != {want}:
            problems.append(f"--starts 5: the manifest says every {par.get('start_every')}, counts "
                            f"{sorted(set(counts.values()))}, not {want} starts a run")
    else:
        problems.append("--starts 5: step 4 wrote nothing")

print(json.dumps({"problems": problems}))
