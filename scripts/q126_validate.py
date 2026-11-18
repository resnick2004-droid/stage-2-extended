"""Q-126 (E-187): the validation of each statistic the calibration chose -- heavy, on the validation seeds only, from
the pinned plan `docs/calibration/Q-126_one_sample_plan_2.md` (its 4.3 and 6.3). Nothing is re-chosen.

    python scripts/run_clean.py --name q126-validate --task Q-126 --hours <from the build's measurement> --mem-gb 1.5 -- python scripts/q126_validate.py

**When:** only after a decision row records the choice: a row of `DECISIONS.md` naming the choice file by path and
sha256, in the form `results/q126_choice.csv` sha256 `<64 hex>`. Until such a row exists, and the file matches it and
its manifest (written by `scripts/q126_calibrate.py` in a clean run, not exploratory), the run refuses. **NONE** at
the choice: the validation block is retired, never drawn (the plan's 7 item 1) -- the run refuses before any read.

**What it computes:** Q-108's class (the plan's 3.1: 2,293 nulls in the criterion and 84 beside) on the validation
block's seeds -- 23 fresh subsets a size, j = 0..22, the exact null index 0..1,169 -- and the drift nulls beside, for
each chosen statistic (the primary in its scope; the second statistic in scope Q, when there is one) and `cons` beside,
every one in both scopes on the same draws, with the calibration's code (`scripts/q126_calibrate.py`, imported).

**The criterion (the plan's 4.3, E-052's, unchanged):** Q-108's validation code's `criterion`, imported, applied to
each chosen statistic on its own. It HOLDS if at every k in 13..20 on every one of the 2,293 nulls a Monte Carlo
null's 95 % Clopper-Pearson interval does not lie wholly above nominal and an exact null's exact size is at or below
nominal; FAILS if any null breaks either; NOT CHECKED -- never a pass -- if any null is missing. It prints
`criterion (Q-126) <name> (scope <s>): HOLDS | FAILS | NOT CHECKED` for each. Beside, never in the verdict: `cons` in
scope Q, the count-persistent nulls, the `flat` form, the drift nulls, the power on the validation toys.

**The parts (6.3):** `core`, `drift`, `criterion`, under the one lock, the calibration's crash rule. **Writes**
(through `extended.results`, all or none, only inside a clean run): `q126_val_size.csv`, `q126_val_drift.csv`,
`q126_val_power.csv`, `q126_val_cells.csv`, `q126_val_criterion.csv`.

**Refusals (exit 3, before any read):** outside a clean run; the lock not this run's; a result file that exists; no
choosing row, the choice file not matching it or its manifest, or NONE; `lift_one_sample2.py` other than the blob the
calibration ran; any other pinned file; a seed map other than the plan's validation table (its spare included) as
parsed from the pinned plan; the provenance assertion; the guard; a failed part on record.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import re
import sys
import time
from pathlib import Path

for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_k] = "1"                                   # forced, one BLAS thread a process (F3)

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from extended import RESULTS_DIR, RUNS_DIR  # noqa: E402
from extended import lift_one_sample2 as L2  # noqa: E402


def _load(name: str, rel: str):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


#: the calibration runner, imported: its null plans, generators, enumeration, re-decision, provenance assertion,
#: guard, work folder and rows
CALQ = _load("q126_calibrate_for_validate", "scripts/q126_calibrate.py")
#: Q-108's validation runner, imported for its criterion and beside table only (E-052's, unchanged; neither reads a
#: seed). Its own retired validation map is replaced by a refusal in this private copy; the calibration module it
#: shares with Q-108's own tests (`q108_calibrate_for_validate`) is left untouched.
VAL108 = _load("q108_validate_for_q126", "scripts/q108_validate.py")
VAL108.SEEDS = CALQ.RetiredSeedMap("Q-108's validation seed map")

SCRIPT = CALQ.VALIDATE_SCRIPT
DECISION = CALQ.DECISION
TASK = CALQ.TASK
WORK_NAME = "q126-validate.work"
RUN_CMD = ("python scripts/run_clean.py --name q126-validate --task Q-126 --hours <measured> --mem-gb 1.5 -- "
           "python scripts/q126_validate.py")

# ---- the validation seed map (the plan's 4.1) ----
SEEDS = {
    "tests": 20263020,          # the validation build's tests
    "fixed_mc": 20263021,       # the fixed-data streams' Monte Carlo side draws, in the calibration's order
    "subsets": 20263022,        # the thinned subsets, j = 0..22 only
    "subset_mc": 20263023,      # the core subsets' Monte Carlo side draws
    "synthetic": 20263024,      # the realistic synthetic nulls
    "beside_cp": 20263025,      # the count-persistent nulls beside
    "beside_flat": 20263026,    # the `flat` form beside
    "exact_sample": 20263027,   # the exact nulls' seeded sample of cells
    "drift": 20263028,          # the drift populations beside
}
SPARE = (20263029,)
# ---- end of the validation seed map ----

#: each role's use as the plan's 4.1 validation table words it (held in the calibration runner, which checks every
#: manifest's seed map against the table)
ROLE_TEXT = CALQ.VAL_ROLE_TEXT
DRAW_ROLES = ("fixed_mc", "subsets", "subset_mc", "synthetic", "beside_cp", "beside_flat", "exact_sample", "drift")
#: the validation draws no sizing subset (B-14): 23 a size, j = 0..22
N_SUBSETS_VAL = 23
PARTS = ("core", "drift", "criterion")
RESULT_FILES = ("q126_val_size", "q126_val_drift", "q126_val_power", "q126_val_cells", "q126_val_criterion")
CHOICE_FILE = "results/q126_choice.csv"
CHOICE_PIN = re.compile(r"`results/q126_choice\.csv` sha256 `([0-9a-f]{64})`")
ROW = re.compile(r"^\|\s*(E-\d+)\s*\|", re.MULTILINE)
#: the criterion's nulls (Q-108's class)
WANT = {"rule": 2293}
REFUSED, FAILED_CHECK = CALQ.REFUSED, CALQ.FAILED_CHECK
VERDICTS = ("HOLDS", "FAILS", "NOT CHECKED")


def _log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S', time.gmtime())} UTC] {msg}", flush=True)


# ================================================================================================ the choosing row


def choosing_row(decisions_text: str) -> tuple[str | None, str | None]:
    """(row id, the choice file's pinned sha256) of the last decision row naming it."""
    found = (None, None)
    for line in decisions_text.splitlines():
        m = ROW.match(line)
        if m:
            c = CHOICE_PIN.search(line)
            if c:
                found = (m.group(1), c.group(1))
    return found


DECISION_LINE = re.compile(r"CHOSEN (\S+) \(scope ([DQ])\)(?:; SECOND (\S+) \(scope Q\)|; SECOND NONE)?")


def parse_decision(line: str) -> dict | None:
    """The choice file's decision: {"primary": (name, scope), "second": (name, "Q") or None}; None for NONE; refuses
    any line the plan's 4.2 does not allow (a second statistic only beside a scope-D primary, from the scope-Q
    branch)."""
    if line == "NONE":
        return None
    m = DECISION_LINE.fullmatch(line)
    if not m:
        raise ValueError(f"the decision {line!r} is not one the plan's 4.2 prints")
    p, s, q = m.group(1), m.group(2), m.group(3)
    if p not in L2.NAMES or not L2.in_rule(p, s):
        raise ValueError(f"{p} in scope {s} is not a pair in the rule")
    if s == "D" and "; SECOND" not in line:
        raise ValueError("a scope-D choice prints its SECOND line")
    if s == "Q" and "; SECOND" in line:
        raise ValueError("a scope-Q primary has no second statistic")
    if q is not None and q not in L2.Q_BRANCH:
        raise ValueError(f"the second statistic {q} is not in the scope-Q branch")
    return {"primary": (p, s), "second": (q, "Q") if q else None}


def choice_problems(repo: Path = ROOT) -> tuple[list[str], dict]:
    """The choosing row and the calibration's choice file: (problems, what was read)."""
    from extended import results as XR

    repo = Path(repo)
    dec = (repo / "DECISIONS.md").read_text(encoding="utf-8") if (repo / "DECISIONS.md").is_file() else ""
    row, pin = choosing_row(dec)
    if row is None:
        return [f"no decision row records the choice: the validation runs only after a row naming `{CHOICE_FILE}` "
                "sha256 (the plan's 6.3)"], {}
    info = {"row": row}
    p = repo / CHOICE_FILE
    if not p.is_file():
        return [f"{CHOICE_FILE} is not in this tree"], info
    ok, msg = XR._vendored.verify_result(p)
    if not ok:
        return [f"{CHOICE_FILE}: {msg}"], info
    man = json.loads(Path(str(p) + XR.MANIFEST_SUFFIX).read_text(encoding="utf-8"))
    probs = []
    if man.get("script") != CALQ.SCRIPT:
        probs.append(f"{CHOICE_FILE} was written by {man.get('script')!r}, not {CALQ.SCRIPT}")
    if not (man.get("provenance") or {}).get("clean_run"):
        probs.append(f"{CHOICE_FILE} was not written inside a clean run")
    if man.get("exploratory"):
        probs.append(f"{CHOICE_FILE} is marked exploratory")
    if CALQ._sha(p) != pin:
        probs.append(f"{CHOICE_FILE} does not hash to {row}'s pin")
    if probs:
        return probs, info
    ch = pd.read_csv(p, low_memory=False)
    d = ch[ch["row"] == "decision"]
    if len(d) != 1:
        return [f"{CHOICE_FILE} holds {len(d)} decision rows, not one"], info
    line = str(d["decision"].iloc[0])
    info["decision"] = line
    try:
        parsed = parse_decision(line)
    except ValueError as exc:
        return [str(exc)], info
    if parsed is None:
        return ["the calibration chose NONE: the validation block is retired, never drawn (the plan's 7 item 1)"], info
    info.update(parsed)
    blobs = (man.get("parameters") or {}).get("blobs", {})
    for rel in (CALQ.MODULE, CALQ.SCRIPT):                 # the module and the runner the validation imports (F6)
        want = blobs.get(rel)
        got = CALQ.blob_id(repo / rel) if (repo / rel).is_file() else None
        if want != got:
            probs.append(f"{rel} is blob {str(got)[:12]}, not the {str(want)[:12]} the calibration ran (the chosen "
                         "statistics and their procedure are that code)")
    return probs, info


def statistics(info: dict) -> list[tuple[str, str]]:
    """The statistics judged, each on its own: the primary in its scope, the second in scope Q when there is one."""
    return [info["primary"]] + ([info["second"]] if info.get("second") else [])


def candidates_for(stats_: list[tuple[str, str]]) -> list[str]:
    out = []
    for c, _ in stats_:
        if c not in out:
            out.append(c)
    if "cons" not in out:
        out.append("cons")                                         # Q-108's C0 beside (the plan's 4.3)
    return out


# ================================================================================================ the plan of nulls


def core_plan(seeds: dict) -> list[dict]:
    """Q-108's class on the validation seeds: 23 subsets a size, the exact null index 0..1,169."""
    return CALQ.core_plan(seeds, n_subsets=N_SUBSETS_VAL)


def drift_plan(seeds: dict) -> list[dict]:
    return CALQ.drift_plan(seeds)


def provenance(plan: list[dict], seeds: dict) -> list[str]:
    return CALQ.provenance_problems(plan, seeds, CALQ.VAL_BLOCK, n_subsets=N_SUBSETS_VAL, max_j=N_SUBSETS_VAL)


# ================================================================================================ the criterion


def criterion_tables(size: pd.DataFrame, stats_: list[tuple[str, str]], cands, want: dict | None = None) -> dict:
    """The plan's 4.3 for each chosen statistic on its own (Q-108's `criterion`, imported, unchanged), and the beside
    table (Q-108's `beside`). The nesting in k and in m is asserted first, over the core's nulls."""
    want = WANT if want is None else want
    nest = []
    fam = CALQ._fam(size)
    rise = np.flatnonzero((np.diff(fam, axis=1) > 0).any(axis=1))
    if rise.size:
        nest.append(f"counts rise with k on {rise.size} rows, first {size['null'].iloc[rise[0]]}")
    nest += CALQ.nesting_in_m_table(size)
    if nest:
        return {"failed": [f"the nesting assertion fails: {nest[:3]}"]}
    crit, verdicts = [], {}
    d = size[size["group"] != "drift"]
    for c, s_ in stats_:
        t = VAL108.criterion(d, c, s_, want)
        t["statistic"] = "primary" if (c, s_) == stats_[0] else "second"
        crit.append(t)
        verdicts[(c, s_)] = str(t[t["k"].astype(str) == "13-20"]["verdict"].iloc[0])
    beside = VAL108.beside(d, cands)
    return {"failed": [], "criterion": pd.concat(crit, ignore_index=True, sort=False), "beside": beside,
            "verdicts": verdicts}


# ================================================================================================ the commands


def work_dir() -> Path:
    return Path(RUNS_DIR) / WORK_NAME


def preflight(target: Path, part: str | None, *, seeds: dict | None = None, guard: bool = True,
              repo: Path = ROOT, work: Path | None = None) -> tuple[list[str], dict]:
    """The refusals before any read, in order."""
    from extended import results as XR

    seeds = SEEDS if seeds is None else seeds
    bad = XR.clean_run_problem()
    if bad:
        return [f"this process is not a clean run -- {bad}. Run it as: {RUN_CMD}"], {}
    bad = CALQ.lock_problem()
    if bad:
        return [bad], {}
    bad = CALQ.thread_problems()
    if bad:
        return bad, {}
    if part in (None, "criterion"):
        clash = CALQ.result_clash(target, RESULT_FILES)
        if clash:
            return [f"{clash} exist in {target}; a result file is never overwritten"], {}
    probs, info = choice_problems(repo)
    if probs:
        return probs, info
    probs = CALQ.pin_problems(repo)
    probs += CALQ.seed_map_problems(seeds, CALQ.VAL_BLOCK, DRAW_ROLES + ("tests",), plan_block="validation",
                                    role_text=ROLE_TEXT, spare=SPARE, repo=repo)
    if probs:
        return probs, info
    probs = provenance(core_plan(seeds) + drift_plan(seeds), seeds)
    if probs:
        return [f"the seed-provenance assertion refuses: {probs[:5]}"], info
    work = work_dir() if work is None else Path(work)
    if not CALQ._outside_tree(work, repo):
        return [f"the work folder {work} must lie outside this tree"], info
    bad = CALQ.failed_record_problems(work, "validate")
    if bad:
        return bad, info
    if guard:
        sp, notes = CALQ.seed_block_problems(repo)
        for x in notes:
            _log(f"seed blocks: {x}")
        if sp:
            return ["the plan's seed blocks are not unused -- " + "; ".join(sp[:10])], info
    return [], info


def part_main(part: str, work: Path, info: dict, *, seeds: dict, reps: int | None = None,
              reps_beside: int | None = None) -> int:
    t0 = time.time()
    reps = CALQ.REPS if reps is None else reps
    reps_beside = CALQ.REPS_BESIDE if reps_beside is None else reps_beside
    stats_ = statistics(info)
    cands = candidates_for(stats_)
    record = sorted(set(stats_))

    def provenance_failed(probs):
        CALQ.record_failed(work, part, [f"the seed-provenance assertion: {x}" for x in probs[:20]], runner="validate")
        print(f"FAILED CHECK: the seed-provenance assertion refuses: {probs[:5]}", flush=True)
        return FAILED_CHECK

    def check_failed(exc):
        CALQ.record_failed(work, part, [f"a check raised {type(exc).__name__}: {exc}"], runner="validate")
        print(f"FAILED CHECK: {type(exc).__name__}: {exc}", flush=True)
        return FAILED_CHECK

    extra = {"choosing_row": info["row"], "choice": info["decision"], "statistics": [list(x) for x in stats_],
             "candidates": cands}
    if part == "core":
        import shutil
        import subprocess

        plan = core_plan(seeds)
        probs = provenance(plan, seeds)                                  # before any read and any draw
        if probs:
            return provenance_failed(probs)
        cal, sha, src = CALQ.read_calendar()
        bad = CALQ.calendar_problems(cal, sha)
        if bad:
            print("REFUSED: " + "; ".join(bad), flush=True)
            return REFUSED
        scratch = Path(work) / f".core.inputs-{os.getpid()}"
        if scratch.exists():
            shutil.rmtree(scratch)
        scratch.mkdir(parents=True)
        try:
            calf = scratch / "judged_sessions.csv"
            pd.DataFrame({"date": cal}).to_csv(calf, index=False, lineterminator="\n")
            r = subprocess.run([sys.executable, "scripts/q16_p16_pairs.py", "--out", str(scratch / "pairs")],
                               cwd=str(ROOT))
            if r.returncode:
                return 1
            p, pinfo = CALQ.Q82.load_pairs(scratch / "pairs" / "p16_pairs.parquet", cal)
            inp = CALQ.CAL.Inputs(p, len(cal), seeds)
            try:
                out = CALQ.compute_nulls(part, plan, inp, len(cal), reps, cands, reps_beside=reps_beside,
                                         record=record)
            except CALQ.CHECK_ERRORS as exc:
                return check_failed(exc)
            extra.update({"calendar_sha256": sha, "calendar_source": src, "pairs_sha256": pinfo.get("parquet_sha256"),
                          "pairs_identity": pinfo.get("identity")})
            return CALQ.finish_part(work, part, out, {**CALQ._manifest_base(seeds, extra), **CALQ._time_fields(t0),
                                                      "timing": out["timing"]}, runner="validate",
                                    extra_dirs={"judged_sessions.csv": calf, "pairs": scratch / "pairs"})
        finally:
            shutil.rmtree(scratch, ignore_errors=True)
    if part == "drift":
        plan = drift_plan(seeds)
        probs = provenance(plan, seeds)
        if probs:
            return provenance_failed(probs)
        n = CALQ.N_SESSIONS
        try:
            out = CALQ.compute_nulls(part, plan, None, n, reps, cands, drift_inputs=CALQ.drift_inputs_for(n),
                                     record=record)
        except CALQ.CHECK_ERRORS as exc:
            return check_failed(exc)
        return CALQ.finish_part(work, part, out, {**CALQ._manifest_base(seeds, extra), **CALQ._time_fields(t0),
                                                  "timing": out["timing"]}, runner="validate")
    raise ValueError(f"no part {part!r}")


def criterion_main(work: Path, info: dict, *, seeds: dict) -> int:
    from extended import results as XR

    commit = CALQ.git_head()
    need = ("core", "drift")
    probs = []
    for p in need:
        probs += CALQ.part_problems(work, p, commit=commit, seeds=seeds)
    probs += CALQ.versions_problems(work, need)
    if probs:
        print("REFUSED: " + "; ".join(probs[:8]), flush=True)
        return REFUSED
    bad = CALQ.ledger_choice_problems(work, need, commit, "validate")
    if bad["missing"]:
        print("REFUSED: " + "; ".join(bad["missing"][:8]), flush=True)
        return REFUSED
    if bad["differs"]:
        CALQ.record_failed(work, "criterion", bad["differs"], runner="validate", commit=commit)
        print("FAILED CHECK: " + "; ".join(bad["differs"][:5]), flush=True)
        return FAILED_CHECK
    parts = {p: CALQ.read_part_frames(work, p) for p in need}
    for p in need:
        if parts[p]["manifest"].get("choice") != info["decision"]:
            print(f"REFUSED: the part {p} validated another choice", flush=True)
            return REFUSED
    stats_ = statistics(info)
    cands = candidates_for(stats_)
    size = pd.concat([parts["core"]["size"], parts["drift"]["size"]], ignore_index=True, sort=False)
    try:
        res = criterion_tables(size, stats_, cands)
    except CALQ.CHECK_ERRORS as exc:
        res = {"failed": [f"a check raised {type(exc).__name__}: {exc}"]}
    if res["failed"]:
        CALQ.record_failed(work, "criterion", res["failed"], runner="validate", commit=commit)
        for f in res["failed"]:
            print(f"FAILED CHECK: {f}", flush=True)
        return FAILED_CHECK
    probs = CALQ.manifest_seed_problems(seeds)
    if probs:
        print(f"REFUSED: the seed map to be recorded is not the plan's: {probs[:3]}", flush=True)
        return REFUSED
    man0 = parts["core"]["manifest"]
    core = parts["core"]["size"]
    frames = {"q126_val_size": pd.concat([core, pd.DataFrame(CALQ.spread_rows(core))], ignore_index=True, sort=False),
              "q126_val_drift": CALQ.wide(parts["drift"]["size"], cands),
              "q126_val_power": parts["core"]["power"],
              "q126_val_cells": pd.concat([x["cells"] for x in parts.values() if len(x["cells"])], ignore_index=True,
                                          sort=False) if any(len(x["cells"]) for x in parts.values()) else
              pd.DataFrame(columns=["null", "candidate", "scope", "cell"]),
              "q126_val_criterion": pd.concat([res["criterion"], res["beside"]], ignore_index=True, sort=False)}
    roles = {"q126_val_size": ("fixed_mc", DRAW_ROLES[:-1]), "q126_val_drift": ("drift", ("drift",)),
             "q126_val_power": ("subset_mc", ("subsets", "subset_mc", "synthetic")),
             "q126_val_cells": ("subsets", ("subsets", "exact_sample", "drift")), "q126_val_criterion": (None, ())}
    verdict_line = "; ".join(f"{c} (scope {s}) {v}" for (c, s), v in res["verdicts"].items())
    common = {"decision": DECISION, "task": TASK, "plan": man0["plan"], "plan_sha256": CALQ.PLAN_SHA256,
              "choosing_row": info["row"], "choice": info["decision"], "statistics": [list(x) for x in stats_],
              "candidates": cands, "choice_sha256": CALQ._sha(ROOT / CHOICE_FILE), "reps": CALQ.REPS,
              "reps_beside": CALQ.REPS_BESIDE, "n_sessions": CALQ.N_SESSIONS,
              "calendar_sha256": man0.get("calendar_sha256"), "pairs_sha256": man0.get("pairs_sha256"),
              "blobs": man0["blobs"], "versions": man0["versions"], "seed_map": {k: int(v) for k, v in seeds.items()},
              "spare_seeds": list(SPARE), "seed_block": list(CALQ.VAL_BLOCK),
              "parts": {p: {"files": parts[p]["manifest"]["files"], "time": parts[p]["manifest"].get("time")}
                        for p in need},
              "criterion": "the plan's 4.3 (E-052's): at every k in 13..20, on every one of the 2,293 nulls, no Monte "
                           "Carlo null's 95 % interval wholly above nominal and no exact size above nominal",
              "verdicts": verdict_line}
    desc = {nm: f"the validation -- {nm}; {verdict_line}" for nm in RESULT_FILES}
    rc = CALQ.write_results(frames, {nm: roles[nm] for nm in RESULT_FILES}, desc, common, seeds, target=RESULTS_DIR,
                            work=work, runner="validate", commit=commit, script=SCRIPT)
    if rc:
        return rc
    for (c, s), v in res["verdicts"].items():
        print(f"criterion (Q-126) {c} (scope {s}): {v}", flush=True)
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--parts", default=None)
    ap.add_argument("--part", default=None, help=argparse.SUPPRESS)
    ap.add_argument("--work", type=Path, default=None, help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    t0 = time.time()
    bad = CALQ.gate_problem(a.work, a.part)
    if bad:
        print(f"REFUSED: {bad}", flush=True)
        return REFUSED
    work = work_dir() if a.work is None else Path(a.work)
    try:
        probs, info = preflight(RESULTS_DIR, a.part, work=work)
    except CALQ.ProvenanceRefused as exc:
        probs, info = [str(exc)], {}
    if probs:
        print("REFUSED: " + "; ".join(probs), flush=True)
        return REFUSED
    if not CALQ._outside_tree(work):
        print(f"REFUSED: the work folder {work} must lie outside this tree", flush=True)
        return REFUSED
    work.mkdir(parents=True, exist_ok=True)
    if a.part is not None:
        if a.part not in PARTS:
            print(f"REFUSED: no part {a.part!r}; the parts are {PARTS}", flush=True)
            return REFUSED
        if a.part == "criterion":
            return criterion_main(work, info, seeds=SEEDS)
        return part_main(a.part, work, info, seeds=SEEDS)
    parts = PARTS if a.parts is None else tuple(x for x in PARTS if x in a.parts.split(","))
    _log(f"the choice ({info['row']}): {info['decision']}; statistics {statistics(info)}; seed map {SEEDS}")
    rc = CALQ.driver(parts, work, SCRIPT, runner="validate", final="criterion")
    _log(f"EXIT {rc} ({time.time() - t0:.0f} s)")
    return rc


if __name__ == "__main__":
    sys.exit(main())
