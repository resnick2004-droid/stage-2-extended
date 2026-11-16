"""Q-55 (E-035 (4)): Q-16's calibration end to end, as one command for a clean run, written as result files.

    python scripts/run_clean.py --name q55-calibration --task Q-55 --hours 4 --mem-gb 1.2 -- python scripts/q55_calibration.py
    python scripts/q55_calibration.py --results-dir <tmp> --work <tmp> --pairs <dir> --days <file> --reps 2000 ...  # a test

**What it runs, in order, each step a process of its own** (one at a time; the vendored engine only in the first):
1. `scripts/q16_p16_pairs.py`: P-16's coin-twin pairs rebuilt with the vendored walk, refusing unless its three
   identities hold (the screen's marks, its cell row, `TRADES_SHA256`). Its read of the bars and A1's tables is
   authorised through `extended.reader` first (purpose `registered_design`, declaration E-035; E-037): **a refusal
   ends this run before anything is read** (exit 3) -- until the reader admits that purpose (TASK_QUEUE Q-58), it
   refuses.
2. `scripts/q16_calibrate.py --part lift` (the lift's 70 real and 45 synthetic nulls, the bootstrap's 12),
   `--part p` (the P comparison's 29 nulls, `bm63c`'s two stages), `--part select` (the two-sample forms with the
   treated-cluster block count) and `--part select --diff-df all` (the first form, failed, kept on record).
3. `scripts/q16_tables.py` on each part (the note's tables, printed into the run's log).

Step outputs go to a work folder **outside** the checkout (`<RUNS_DIR>/<name>.work` in a clean run), so the checkout
stays clean for the reader and the writer. A failed step stops the run: nothing is written.

**What it writes** (`extended.results.write_result`, each with its manifest; into this tree's `results/` only inside
the clean run `scripts/run_clean.py` made -- refused at once otherwise, before any step):

| file | rows |
|---|---|
| `calibration_lift.csv` | the lift's size rows (`section` `size`: every null x candidate x level, rejections, rate, Clopper-Pearson interval, ratio) and the bootstrap's (`section` `boot`) |
| `calibration_p.csv` | the P comparison's size rows, `bm63c` from its fresh replications (`stage`) |
| `calibration_two_sample.csv` | the placebo-selection twin's and C1''s size rows, `df_rule` `treated` (the module's) and `all` (the first form) |
| `calibration_power.csv` | every minimum detectable effect: `part` `lift`, `p`, `two_sample` (with `df_rule`) |
| `bm63c_table.csv` | `bm63c`'s calibrated critical values (`level`, `critical`, ...): the table `extended.p_bound.load_bm63c_critical` reads, to be pinned under a decision row |

`scripts/q16_tables.py --results results/` rebuilds the note's tables from these five files alone (each checked
against its manifest). Seeds: Q-16's (20261910-20261919), as `scripts/q16_calibrate.py` fixes them; recorded in every
manifest. `--pairs` (a test's seam) skips step 1 and is recorded in every manifest (`pairs_supplied`): such files are
not the calibration's.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from extended import CLEAN_RUN_ENV, RESULTS_DIR, RUNS_DIR  # noqa: E402

SCRIPT = "scripts/q55_calibration.py"
RESULT_FILES = ("calibration_lift", "calibration_p", "calibration_two_sample", "calibration_power", "bm63c_table")
SEEDS = {"lift_real": 20261915, "lift_syn": 20261916, "p_real": 20261917, "p_syn": 20261918, "fixed_b": 20261913,
         "boot": 20261914, "p_fixed_b": 20261919, "tests": [20261910, 20261911, 20261912]}
DECISION = "E-035"


def _log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S', time.gmtime())} UTC] {msg}", flush=True)


def _step(name: str, args: list[str]) -> None:
    _log(f"step {name}: {' '.join(args)}")
    t0 = time.time()
    r = subprocess.run([sys.executable, *args], cwd=str(ROOT))
    if r.returncode != 0:
        _log(f"step {name} FAILED (exit {r.returncode}); nothing written")
        raise SystemExit(r.returncode if r.returncode in (2, 3) else 1)
    _log(f"step {name}: done, {time.time() - t0:.0f} s")


def _meta(d: Path, part: str) -> dict:
    return json.loads((d / f"calibrate_{part}.json").read_text(encoding="utf-8"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--results-dir", type=Path, default=None, help="default: this tree's results/ (clean run only)")
    ap.add_argument("--work", type=Path, default=None)
    ap.add_argument("--pairs", type=Path, default=None, help="a pairs folder already made (a test's seam)")
    ap.add_argument("--days", type=Path, default=None, help="a trading-day calendar (a test's seam)")
    ap.add_argument("--reps", type=int, default=200_000)
    ap.add_argument("--boot-reps", type=int, default=20_000)
    ap.add_argument("--d621-reps", type=int, default=20_000)
    ap.add_argument("--power-reps", type=int, default=5_000)
    a = ap.parse_args(argv)
    t0 = time.time()

    from extended import results as XR                  # the vendored writer: this process only

    target = Path(a.results_dir) if a.results_dir is not None else RESULTS_DIR
    if XR.protected(target):                             # refuse at once, never after three hours of work
        bad = XR.clean_run_problem()
        if bad:
            print(f"REFUSED: {target} is a results/ folder of this repository and this process is not a clean run "
                  f"-- {bad}. Run it as: python scripts/run_clean.py --name q55-calibration --task Q-55 --hours 4 "
                  "--mem-gb 1.2 -- python scripts/q55_calibration.py", flush=True)
            return 3
    clash = [n for n in RESULT_FILES if (target / f"{n}.csv").exists() or (target / f"{n}.csv.manifest.json").exists()]
    if clash:
        print(f"REFUSED: {clash} exist in {target}; a result file is never overwritten", flush=True)
        return 3
    name = os.environ.get(CLEAN_RUN_ENV)
    work = Path(a.work) if a.work is not None else (Path(RUNS_DIR) / f"{name}.work" if name
                                                     else Path(tempfile.mkdtemp(prefix="q55_")))
    work.mkdir(parents=True, exist_ok=True)
    if (ROOT / "results").resolve() in [work.resolve(), *work.resolve().parents] or ROOT.resolve() in \
            [work.resolve(), *work.resolve().parents]:
        print(f"REFUSED: the work folder {work} must lie outside this tree (the checkout stays clean)", flush=True)
        return 3
    _log(f"Q-55: target {target}, work {work}, clean run {name or 'none'}")

    pairs = Path(a.pairs) if a.pairs is not None else work / "pairs"
    if a.pairs is None:
        _step("pairs", ["scripts/q16_p16_pairs.py", "--out", str(pairs)])
    pq = pairs / "p16_pairs.parquet"
    common = ["--reps", str(a.reps)] + (["--days", str(a.days)] if a.days is not None else [])
    dirs = {"lift": work / "lift", "p": work / "p", "select": work / "select", "select_all": work / "select_all"}
    _step("lift", ["scripts/q16_calibrate.py", "--out", str(dirs["lift"]), "--pairs", str(pq), "--part", "lift",
                   "--boot-reps", str(a.boot_reps)] + common)
    _step("p", ["scripts/q16_calibrate.py", "--out", str(dirs["p"]), "--part", "p", "--d621-reps", str(a.d621_reps)]
          + common)
    for sub, rule in (("select", "treated"), ("select_all", "all")):
        _step(f"two-sample ({rule})", ["scripts/q16_calibrate.py", "--out", str(dirs[sub]), "--pairs", str(pq),
                                       "--part", "select", "--diff-df", rule, "--power-reps", str(a.power_reps)]
              + common)
    for sub, d in dirs.items():
        _step(f"tables ({sub})", ["scripts/q16_tables.py", "--dir", str(d)])

    import pandas as pd

    rd = lambda p: pd.read_csv(p, low_memory=False)      # noqa: E731
    pairs_meta = json.loads((pairs / "p16_pairs.json").read_text(encoding="utf-8"))
    metas = {"lift": _meta(dirs["lift"], "lift"), "p": _meta(dirs["p"], "p"),
             "two_sample_treated": _meta(dirs["select"], "select"), "two_sample_all": _meta(dirs["select_all"], "select")}
    params = {"argv": sys.argv[1:], "reps": a.reps, "boot_reps": a.boot_reps, "d621_reps": a.d621_reps,
              "power_reps": a.power_reps, "seeds": SEEDS, "pairs_supplied": a.pairs is not None,
              "days": str(a.days) if a.days is not None else "vendor/stage2/data/atlas/A1/days.parquet",
              "pairs_sha256": pairs_meta.get("parquet_sha256"), "trades_sha256": pairs_meta.get("trades_sha256"),
              "pairs_identity": pairs_meta.get("identity"),
              "parts": {k: {x: m.get(x) for x in ("script", "commit", "dirty", "seconds", "peak_working_set_mb")}
                        for k, m in metas.items()},
              "read": {"purpose": "registered_design", "declaration": DECISION, "files": [
                  "vendor/stage2/data/atlas/A1/events.parquet", "vendor/stage2/data/atlas/A1/days.parquet",
                  "vendor/stage2/data/bars/NQ/bars.parquet"]}}
    frames = {
        "calibration_lift": pd.concat([rd(dirs["lift"] / "lift_size.csv").assign(section="size"),
                                       rd(dirs["lift"] / "lift_boot.csv").assign(section="boot")], ignore_index=True),
        "calibration_p": rd(dirs["p"] / "p_size.csv"),
        "calibration_two_sample": pd.concat([rd(dirs["select"] / "diff_size.csv").assign(df_rule="treated"),
                                             rd(dirs["select_all"] / "diff_size.csv").assign(df_rule="all")],
                                            ignore_index=True),
        "calibration_power": pd.concat([rd(dirs["lift"] / "lift_power.csv").assign(part="lift"),
                                        rd(dirs["p"] / "p_power.csv").assign(part="p"),
                                        rd(dirs["select"] / "diff_power.csv").assign(part="two_sample",
                                                                                     df_rule="treated"),
                                        rd(dirs["select_all"] / "diff_power.csv").assign(part="two_sample",
                                                                                         df_rule="all")],
                                       ignore_index=True),
        "bm63c_table": rd(dirs["p"] / "p_bm63c_critical.csv")}
    descriptions = {
        "calibration_lift": "Q-16's lift calibration (E-035): each candidate's rejection rate at a true zero, by null "
                            "and level, with its Clopper-Pearson interval; the bootstrap's rows beside",
        "calibration_p": "Q-16's P-comparison calibration (E-035): each candidate's rejection rate by null and level",
        "calibration_two_sample": "Q-16's two-sample forms (E-022's C1', E-023's placebo-selection twin): rejection "
                                  "rates, both block-count rules (treated: the module's; all: the first form, failed)",
        "calibration_power": "Q-16's minimum detectable effects at 80 % power, every part",
        "bm63c_table": "bm63c's critical values calibrated on the declared nulls (stage 1 of two; extended.p_bound)"}
    notes = {"why": "E-035 (4): the calibration's figures are cited only from a clean run; TASK_QUEUE Q-55",
             "exploratory_because": "the statistics' configuration (candidates, nulls, the treated block count, bm63c) "
                                    "was fixed in Q-16 after exploratory runs; this run changes none of it",
             "tables": "python scripts/q16_tables.py --results <this folder>"}
    for n, df in frames.items():
        csv, man = XR.write_result(df, n, script=SCRIPT, seed=SEEDS["lift_real"], parameters=params,
                                   results_dir=target, description=descriptions[n], exploratory=True, notes=notes)
        _log(f"wrote {csv} ({len(df)} rows) and {man.name}")
    _log(f"EXIT 0 ({time.time() - t0:.0f} s)")
    print("EXIT 0", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
