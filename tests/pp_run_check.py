"""The reading's runner checked on synthetic inputs (RD-02 section 14; Q-105b), run by `tests/test_pp_run.py`, one
section a process (the vendored engine on this process's `sys.path`):

    python tests/pp_run_check.py <repository root> <section> [<temporary folder>]      # one JSON line last

* `e2e` -- `scripts/pp_reading.py --synthetic` into a temporary folder: exit 0, the three files and their manifests,
  each verifying; the manifests' `prereg_id` RD-02, `exploratory` False, the run count, the honesty seed read from the
  pinned file (section 11's), the retired seeds, the adapter's commit and blob ids, the calendars' and the data
  manifest's sha256, the limits; the reading's sections (identity rows all holding, in 14 step 2's order -- `ref` first
  -- and the mechanics, scorecard, paired, diverge, oracle rows), the menu's standing notes and labels, the gate rows.
* `refusals` -- a planted identity failure and a planted ladder failure each refuse and write nothing; the real mode
  outside a clean run refuses before anything; a protected results folder is refused; the waits' rows are checked
  (a missing row, a row not saying what it must).
* `labels` -- `extended.pp_run`'s paired readings on synthetic per-start frames long enough for intervals: the kept
  windows' interval and MDD printed, each interval labelled from the honesty table (the label from gauss, ahead and
  paired only; the rare-shape line beside), the menu counting the intervals and the tenth expected by chance.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(sys.argv[1])
SECTION = sys.argv[2]
TMP = Path(sys.argv[3]) if len(sys.argv) > 3 else None
for _p in (str(REPO), str(REPO / "identity"), str(REPO / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

problems: list[str] = []
out: dict = {}


def check(cond: bool, what: str) -> None:
    if not cond:
        problems.append(what)


def script(*args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ, OMP_NUM_THREADS="1", PYTHONDONTWRITEBYTECODE="1")
    env.pop("S2X_CLEAN_RUN", None)
    return subprocess.run([sys.executable, str(REPO / "scripts" / "pp_reading.py"), *args], cwd=REPO,
                          capture_output=True, text=True, timeout=900, env=env)


def section_e2e() -> None:
    from extended import pp_run as RUN
    from extended import results as XR

    d = TMP / "e2e"
    d.mkdir(parents=True, exist_ok=True)
    r = script("--synthetic", "--results-dir", str(d))
    check(r.returncode == 0 and "EXIT 0" in r.stdout, f"the synthetic run did not finish: {r.stdout[-1500:]}"
                                                      f"{r.stderr[-1500:]}")
    names = ("pp_reading_synthetic", "pp_gate_synthetic", "pp_menu_synthetic")
    for n in names:
        ok, msg = XR.verify_result(d / f"{n}.csv") if (d / f"{n}.csv").is_file() else (False, "absent")
        check(ok, f"{n}: {msg}")
    if problems:
        return
    man = json.loads((d / "pp_reading_synthetic.csv.manifest.json").read_text(encoding="utf-8"))
    par = man.get("parameters", {})
    check(man.get("prereg_id") == "RD-02", f"prereg_id {man.get('prereg_id')!r}")
    check(man.get("exploratory") is False, "the manifest is not exploratory=False")
    check(par.get("run_count") == 7, f"the synthetic run counts {par.get('run_count')} runs, not 7 (one design: ref, "
                                     "three new, three sensitivity)")
    import test_pp_draft as D

    check(par.get("seeds", {}).get("honesty_series") == D.COVERAGE_SEED,
          "the honesty seed is not section 11's (read from the pinned file)")
    check(RUN.declared_seed("9.2 item 7's honesty series", REPO) == D.COVERAGE_SEED, "declared_seed")
    check("retired" in par.get("seeds", {}), "the retired seeds are not listed")
    ad = par.get("adapter", {})
    check(len(ad.get("commit", "")) == 40 and all(ad.get("blobs", {}).get(f) for f in
                                                  ("extended/payout_policy.py", "extended/user_beside.py",
                                                   "extended/gate.py")), f"the adapter's provenance: {ad}")
    check(par.get("calendars") == RUN.CALENDARS and len(par.get("data_manifest_sha256", "")) == 64,
          "the calendars' or the data manifest's sha256")
    check(par.get("limits") == "none approved before the run's commit", f"limits {par.get('limits')!r}")
    rd = pd.read_csv(d / "pp_reading_synthetic.csv")
    secs = set(rd["section"])
    for s in ("identity", "mechanics", "scorecard", "paired", "diverge", "oracle"):
        check(s in secs, f"no {s} section")
    ids = rd[rd["section"] == "identity"]
    check(len(ids) == 18 and ids["value"].eq(1.0).all(), f"identity rows: {len(ids)}, all holding "
                                                         f"{ids['value'].eq(1.0).all()}")
    order = list(ids["measure"])
    check(order[:6] == ["8.1 items 2 and 4"] * 2 + ["8.1 item 6"] * 4 and set(order[6:]) == {"8.1 item 5"},
          f"the order is not 14 step 2's: {order[:8]}")
    mech = rd[(rd["section"] == "mechanics") & (rd["cell"] == "lock") & (rd["arm"] == "verdict")]
    held = mech[mech["measure"] == "first_requests_held"]["value"]
    check(len(held) and float(held.iloc[0]) > 0, "lock held no first request on the toy (the counts' route)")
    check((rd["measure"] == "offered_open_at_minutes_release").any(), "the minutes count is missing")
    ref_mech = rd[(rd["section"] == "mechanics") & (rd["cell"] == "ref") & (rd["measure"].isin(
        ["first_requests_held", "half_cut_below_min", "elig_differs", "held_sessions"]))]
    check(ref_mech["value"].eq(0).all(), "ref's counts are not zero")
    mn = pd.read_csv(d / "pp_menu_synthetic.csv")
    check(len(mn) and mn["labels"].str.contains("described, not carried").all(), "a menu row is not labelled")
    check(mn[mn["cell"].str.contains("half")]["labels"].str.contains("assumption").all(), "half's label")
    lk = mn[(mn["response"] == "rtp") & mn["cell"].str.startswith("lock")]
    check(len(lk) and lk["labels"].str.contains("L1 on Standard-path accounts only").all(), "lock under rtp's label")
    check(mn["note_focused_trader"].str.contains("half").all(), "the Focused Trader gap does not name half")
    g = pd.read_csv(d / "pp_gate_synthetic.csv")
    check(set(g["cell"]) == {"lock", "half", "lock_half"} and set(g["twin"]) == {True, False},
          "the gate rows are not the three new cells with their twins")
    out["e2e"] = {"rows": len(rd), "sections": sorted(secs), "menu_rows": len(mn), "gate_rows": len(g)}


def section_refusals() -> None:
    for plant in ("identity", "ladder"):
        d = TMP / f"plant_{plant}"
        d.mkdir(parents=True, exist_ok=True)
        r = script("--synthetic", "--results-dir", str(d), "--plant", plant)
        check(r.returncode == 3 and "nothing written" in r.stdout, f"the planted {plant} failure did not refuse")
        check(not any(d.iterdir()), f"the planted {plant} failure wrote {list(d.iterdir())}")
    r = script("--identity-row", "E-082", "--gate-row", "E-049", "--u1-row", "E-059", "--recorder-row", "E-068")
    check(r.returncode == 3 and "clean checkout" in r.stdout, f"the real mode outside a clean run: {r.stdout[-400:]}")
    r = script("--synthetic", "--results-dir", str(REPO / "results"))
    check(r.returncode == 3 and "never writes" in r.stdout, "a protected results folder was not refused")
    import pp_reading as S

    ns = argparse.Namespace(identity_row="E-999", gate_row="E-049", u1_row="E-059", recorder_row="E-068",
                            limits_row=None)
    probs = S.row_problems(ns)
    check(any("E-999" in p and "no such" in p for p in probs), f"a missing row: {probs}")
    ns2 = argparse.Namespace(identity_row="E-082", gate_row="E-082", u1_row="E-082", recorder_row="E-082",
                             limits_row=["E-998"])
    probs2 = S.row_problems(ns2)
    check(any("--identity-row E-082" in p for p in probs2), "a row not naming pp_identity and its hold was accepted")
    check(any("--limits-row" in p for p in probs2), "a missing limits row was accepted")
    out["refusals"] = {"row_problems": probs + probs2}


def section_labels() -> None:
    from extended import pp_reading as RD
    from extended import pp_run as RUN

    g = np.random.default_rng([RUN.declared_seed("9.2 item 7's honesty series", REPO), 0, 900])
    n = 1500
    days = [d.date().isoformat() for d in pd.bdate_range("2020-01-02", periods=n)]
    obs = np.arange(n, 0, -1)
    base = pd.DataFrame({"start_day": np.arange(n), "start_date": days, "observed": obs})
    cols = {c for _, c, _, _ in RUN.MEASURES}
    for c in cols:
        base[c] = g.normal(size=n)
    cell = base.copy()
    for c in cols:
        cell[c] = base[c] + g.normal(0.05, 0.5, size=n)
    key = dict(design="syn", arm="verdict", cell="lock", mode="declared", response="off")
    honesty: dict = {}
    rows = RUN.paired_rows(cell, base, key, honesty)
    hon = RUN.honesty_table(list(honesty), RUN.declared_seed("9.2 item 7's honesty series", REPO), 30)
    RUN.label_rows(rows, hon)
    p = pd.DataFrame(rows)
    ci = p[p["stat"] == "ci90_low"]
    lab = p[p["stat"] == "interval_label"]
    check(len(ci) > 0 and len(lab) == len(ci), f"{len(ci)} intervals, {len(lab)} labels")
    check(lab["note"].str.contains("gauss/ahead/paired").all() and lab["note"].str.contains("rare and lumpy").all(),
          "a label without its two readings")
    check(not lab["note"].str.contains("pending").any(), "a label left pending")
    for (h, n_w) in honesty:
        check(len(hon[(hon["h"] == h) & (hon["n_w"] == n_w)]) == 21, f"setting ({h}, {n_w}): not 21 shapes")
    nw = p[p["stat"] == "n_w"].set_index(["block", "measure"])["value"]
    for r in lab.itertuples():
        sub = hon[(hon["h"] == r.h) & (hon["n_w"] == int(nw.loc[(r.block, r.measure)]))]
        want = RD.label(dict(zip(sub["shape"], sub["coverage"])))
        check(bool(r.value) == want, f"{r.block} {r.measure}: the label {bool(r.value)} is not the rule's {want}")
    mdd = p[p["stat"] == "mdd"]
    check(len(mdd) == len(ci), "an interval without its MDD")
    menu = RUN.menu_table(pd.DataFrame(rows), [])
    check(int(menu["intervals_printed"].iloc[0]) == len(ci) and
          float(menu["intervals_expected_to_exclude_zero_by_chance"].iloc[0]) == len(ci) / 10.0,
          "the menu's interval count")
    check(menu["P_label"].iloc[0] != "", "the menu's P label is empty")
    out["labels"] = {"intervals": len(ci), "settings": sorted(honesty)}


SECTIONS = {"e2e": section_e2e, "refusals": section_refusals, "labels": section_labels}

if __name__ == "__main__":
    SECTIONS[SECTION]()
    out.update({"section": SECTION, "problems": problems[:40], "n_problems": len(problems)})
    print(json.dumps(out, default=str))
