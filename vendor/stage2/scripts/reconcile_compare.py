"""Run the docs/PIPELINE.md section 5 reconciliation comparison on ingested manual runs (D-83, D-94).

    python scripts/reconcile_compare.py            # version 2 (R006-R008), every stage ingested
    python scripts/reconcile_compare.py A          # one stage of version 2
    python scripts/reconcile_compare.py --v1       # version 1 (R002-R004); refuses if already run

For each stage it reads the ingested trade records (`results/manual_R00n_recon_<X>.csv`, checked
against their manifests), replays every trade through propedge's fill model under the stage's
profile -- A `zero_cost_gap_fill`, B `assumed`, C against `zero_cost_gap_fill` -- and writes
`results/reconciliation_stage_<X>.csv` (version 1) or `results/reconciliation_v2_stage_<X>.csv`
(version 2) with a verdict in its manifest.

Version 1 mixed price series and failed on all three stages (D-93); its results stay on record and
it is not rerun, which is why `--v1` refuses when its result files exist. Version 2 (D-94) reads one
series, refuses off-grid evidence as unusable, and runs stage C as planted faults.

Only when **all three** stages of a version pass does it write `results/reconciliation_status.json`
via `qc_provenance.record_reconciliation`, keyed on the fingerprint of stage B's cost model.
Measurements refuse to run until then. A failed stage is kept on record and diagnosed; it is never
rerun until it passes (CLAUDE.md, the failure protocol).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from propedge import RESULTS_DIR  # noqa: E402
from propedge.data.qc_provenance import record_reconciliation  # noqa: E402
from propedge.data.reconciliation import (  # noqa: E402
    STAGE_NAMES, STAGE_NAMES_V2, UnusableEvidence, compare, compare_v2, verdict, verdict_v2,
)
from propedge.data.run_kit import RECON_PROFILE, RECON_V2_RUNS  # noqa: E402
from propedge.execution.fills import FillModel  # noqa: E402
from propedge.reporting.results import read_manifest, read_result, write_result  # noqa: E402

RUN_OF = {"A": "R002-recon-A", "B": "R003-recon-B", "C": "R004-recon-C"}
VERSIONS = {
    1: dict(runs=RUN_OF, compare=compare, verdict=verdict, names=STAGE_NAMES,
            out="reconciliation_stage_{}"),
    2: dict(runs=RECON_V2_RUNS, compare=compare_v2, verdict=verdict_v2, names=STAGE_NAMES_V2,
            out="reconciliation_v2_stage_{}"),
}


def run_stage(stage: str, version: int = 2):
    v = VERSIONS[version]
    run_id = v["runs"][stage]
    src = RESULTS_DIR / ("manual_" + run_id.replace("-", "_") + ".csv")
    if not src.is_file():
        return None
    trades = read_result(src)                        # raises if the manifest does not match
    fm = FillModel.load(RECON_PROFILE[stage])
    try:
        cmp = v["compare"](trades, fm)
    except UnusableEvidence as exc:
        print(f"stage {stage}: UNUSABLE -- {exc}")
        return False
    vd = v["verdict"](stage, cmp)
    src_manifest = read_manifest(src)
    write_result(
        cmp, v["out"].format(stage),
        script="scripts/reconcile_compare.py", seed=None, require_seed=False,
        parameters={"stage": stage, "version": version, "input": src.name,
                    "input_sha256": src_manifest.sha256, "run_id": run_id, "profile": fm.name,
                    "profile_provenance": fm.provenance()},
        description=(f"PIPELINE.md section 5 stage {stage} (version {version}): LEAN's fills from "
                     f"a manual run against propedge's replay under {fm.name}. Deterministic; "
                     f"no seed."),
        notes={"verdict": "PASS" if vd.passed else "FAIL", "detail": vd.detail},
    )
    return vd


def main(argv: list[str]) -> int:
    version = 1 if "--v1" in argv else 2
    stages = [a for a in argv if a != "--v1"] or ["A", "B", "C"]
    cfg = VERSIONS[version]
    if version == 1:
        done = [s for s in stages if (RESULTS_DIR / (cfg["out"].format(s) + ".csv")).is_file()]
        if done:
            print(f"version 1 stages {done} are already on record (D-93); not rerun.")
            return 1
    verdicts = {}
    for s in stages:
        vd = run_stage(s, version)
        if vd is None:
            print(f"stage {s}: not ingested yet ({cfg['runs'][s]})")
            continue
        if vd is False:
            continue
        verdicts[s] = vd
        print(vd.summary())
    if set(verdicts) == {"A", "B", "C"} and all(vd.passed for vd in verdicts.values()):
        kit = json.loads((ROOT / "runs" / cfg["runs"]["B"] / "kit.json").read_text(encoding="utf-8"))
        runs = ", ".join(cfg["runs"][s] for s in "ABC")
        record_reconciliation(kit["config_fingerprint"],
                              stages_passed=[cfg["names"][s] for s in "ABC"],
                              note=f"scripts/reconcile_compare.py version {version}; runs {runs}")
        print("reconciliation PASSED on all three stages; recorded.")
    elif stages:
        print("reconciliation NOT passed: measurements stay blocked. Keep any failure on record "
              "and diagnose it; do not rerun until it passes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
