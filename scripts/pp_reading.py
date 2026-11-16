"""RD-02's reading (`prereg/RD-02_payout_policy.md`, pinned under E-082; section 14): payout policy in a user's first
months, described, never carried -- the 11 runs on both arms, the 32 replays and 8 gates beside, from a clean checkout,
its reads authorised under the declaration's three purposes, after its identities.

    python scripts/run_clean.py --name pp-reading --task Q-105c --hours 6 --mem-gb 2.0 -- \\
        python scripts/pp_reading.py --identity-row E-a --gate-row E-b --u1-row E-c --recorder-row E-d
    python scripts/pp_reading.py --synthetic --results-dir <a temporary folder>    # the pipeline on a synthetic toy

**Refusing, before any of the engine's work** (exit 3, nothing written):

* outside a clean run (`extended.results.clean_run_problem`), in the real mode;
* unless each named row exists in `DECISIONS.md` and says what it must: `--identity-row` names
  `identity/pp_identity.py` and that it held (8.1 items 1 to 3), `--gate-row` Q-80, `--u1-row` Q-93 and
  `--recorder-row` Q-101 (each held, section 14's waits);
* unless Q-44's per-start file is on the tree and verifies (8.1 item 6);
* unless the adapter's files are the commit's (their blob ids are recorded, Q-102's m7);
* unless the reads are authorised (`extended.reader.authorise_engine_read`) under each of `payout_scorecard`,
  `payout_ladder_beside` and `payout_gate_beside` with the declaration -- once each; a further run only with
  `--repeat E-NNN`, a row naming the file (E-053).

**Then** `extended.pp_run.run_reading` (its order and checks: that module's docstring); any failed check refuses and
writes nothing. **Written** through `extended.results.write_result`, each with its manifest: `pp_reading.csv`
(sections identity, oracle, mechanics, scorecard, paired, diverge, gate, coverage), `pp_gate.csv` (the gate rows) and
`pp_menu.csv` (the menu) -- `prereg_id` RD-02, the pinning row, the run counts, every seed with the retired ones, the
parameters and section 4's assumptions, the class, the adapter's commit and blob ids, the data manifest's and the
calendars' sha256, the E-015 limits flagged (only rows given with `--limits-row`, approved before the run's commit),
`exploratory=False`, every cell "described, not carried".
"""
from __future__ import annotations

import argparse
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for _p in (str(ROOT), str(ROOT / "identity")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from extended import reader, use_vendored_stage2  # noqa: E402

use_vendored_stage2()

SCRIPT = "scripts/pp_reading.py"
VENDOR = ROOT / "vendor" / "stage2"
RESULTS = ("pp_reading", "pp_gate", "pp_menu")
#: what each waited row must say (a keyword guard against naming the wrong row, not a proof: the lead names them)
ROW_NEEDS = {"identity_row": ("pp_identity", "holds"), "gate_row": ("Q-80", "holds"), "u1_row": ("Q-93", "holds"),
             "recorder_row": ("Q-101", "holds")}


def row_problems(a: argparse.Namespace) -> list[str]:
    text = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    out = []
    for attr, words in ROW_NEEDS.items():
        rid = getattr(a, attr)
        row = reader.decision_row(text, rid) if rid else None
        if row is None:
            out.append(f"--{attr.replace('_', '-')} {rid!r}: no such decision row")
            continue
        low = row.lower()
        missing = [w for w in words if w.lower() not in low]
        if missing:
            out.append(f"--{attr.replace('_', '-')} {rid}: the row does not mention {missing}")
    for rid in a.limits_row or []:
        if reader.decision_row(text, rid) is None:
            out.append(f"--limits-row {rid!r}: no such decision row")
    return out


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--identity-row")
    ap.add_argument("--gate-row")
    ap.add_argument("--u1-row")
    ap.add_argument("--recorder-row")
    ap.add_argument("--limits-row", action="append", help="a row recording E-015 limits approved before the run")
    ap.add_argument("--repeat", default=None, help="a further run's row (E-NNN) naming the declaration (E-053)")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--synthetic", action="store_true", help="the pipeline on a synthetic toy into --results-dir")
    ap.add_argument("--results-dir", default=None, help="with --synthetic: where the three files go")
    ap.add_argument("--plant", choices=("identity", "ladder"), default=None, help="with --synthetic: a failing check")
    return ap


def main(argv: list[str] | None = None) -> int:
    a = parser().parse_args(argv)
    import stage2_identity as SI

    from extended import payout_policy as PP
    from extended import pp_run as RUN
    from extended import results as XR

    t0 = time.time()
    if a.synthetic:
        if not a.results_dir:
            print("REFUSED (RD-02): --synthetic writes to --results-dir only")
            return 2
        if XR.protected(a.results_dir):
            print("REFUSED (RD-02): --synthetic never writes to a results/ folder of this repository")
            return 3
        from extended import pp_run_synthetic as SYN

        inputs, designs, starts, reps = SYN.SyntheticInputs(plant=a.plant, n_paths=3), ("syn",), 3, 20
        sens, window, target = "syn", ("08:30", "15:10"), Path(a.results_dir)
        limits: list = []
    else:
        if a.results_dir or a.plant:
            print("REFUSED (RD-02): --results-dir and --plant are the synthetic run's only")
            return 2
        prob = XR.clean_run_problem()
        if prob:
            print(f"REFUSED (RD-02, section 14): the reading runs only from a clean checkout -- {prob}")
            print("EXIT 3", flush=True)
            return 3
        probs = row_problems(a)
        q44 = ROOT / "results" / "user_beside_starts.csv"
        ok, msg = XR.verify_result(q44) if q44.is_file() else (False, "absent")
        if not ok:
            probs.append(f"Q-44's per-start file (8.1 item 6): {msg}")
        if probs:
            print("REFUSED (RD-02, 8.1 and section 14's waits): " + "; ".join(probs))
            print("EXIT 3", flush=True)
            return 3
        try:
            for purpose in RUN.PURPOSES:            # once each (E-053); a further run under --repeat's row
                reader.authorise_engine_read(reader.CHOICE_START, reader.JUDGED_END, purpose=purpose,
                                             declaration=RUN.DECLARATION, repeat=a.repeat,
                                             files=SI.engine_files(VENDOR, bars=True),
                                             what=f"RD-02's reading ({SCRIPT}): {purpose}")
        except (reader.ReadRefused, FileNotFoundError, ValueError) as exc:
            print(SI.refusal(exc) if isinstance(exc, (reader.ReadRefused, FileNotFoundError)) else f"REFUSED: {exc}")
            print("EXIT 3", flush=True)
            return 3
        inputs, designs, starts, reps = RUN.RealInputs(), RUN.DESIGNS, None, None
        sens, window, target = RUN.SENSITIVITY_DESIGN, ("08:30", "15:10"), None
        limits = [{"row": r} for r in (a.limits_row or [])]
    try:
        prov = RUN.adapter_provenance(ROOT, strict=not a.synthetic)
        kw = {} if reps is None else {"honesty_reps": reps}
        out = RUN.run_reading(inputs, designs=designs, starts=starts, workers=a.workers, approved_limits=limits,
                              sensitivity_design=sens, time_window=window, **kw)
    except RUN.Refused as exc:
        print(f"REFUSED (RD-02): {exc} -- nothing written", flush=True)
        print("EXIT 3", flush=True)
        return 3
    from propedge.reporting.results import sha256_of

    params = {
        "reading": "RD-02 (reading PP): described, not carried", "pinning_row": RUN.PIN_ROW,
        "declaration": RUN.DECLARATION, "declaration_sha256_lf": RUN.sha256_lf(ROOT / RUN.DECLARATION),
        "runs": [list(r) for r in out["runs"]], "run_count": len(out["runs"]),
        "beside": {"responses": list(RUN.BESIDE), "arm": "verdict", "cells": "the policy cells (not the sensitivity)"},
        "gates": {"cells": list(RUN.NEW_CELLS), "paths": int(inputs.n_paths()), "twin": True, "levels": [0.0]},
        "seeds": {"honesty_series": out["honesty_seed"], "section_11": RUN.section_11(ROOT),
                  "retired": [r["seed"] for r in RUN.section_11(ROOT) if r["status"].lower().startswith("retired")],
                  "ladder": "Q-17's lockstep.child_seed(20261920, 0, start_day), as run_starts draws it",
                  "inherited": "P-14's 20261131, P-16's 20261206 and 20261102 (their registered gate calls)"},
        "honesty": {"settings": [list(s) for s in out["honesty_settings"]],
                    "series_per_setting": int(reps or RUN.RD.HONESTY_SERIES)},
        "assumptions": ["the request's timing: after 5:00 PM CT (Stage 2 D-175)",
                        "the request's amount: any amount from the minimum to the maximum (E-034: unstated; half "
                        "needs it)"],
        "funded_account_cls": {c: PP.class_name(PP.cell_class(c)) if hasattr(PP, "class_name") else
                               f"{PP.cell_class(c).__module__}.{PP.cell_class(c).__qualname__}" for c in PP.CELLS},
        "adapter": prov, "calendars": dict(RUN.CALENDARS),
        "data_manifest_sha256": sha256_of(ROOT / "vendor" / "DATA_MANIFEST_stage2.sha256"),
        "limits": limits or "none approved before the run's commit", "repeat": a.repeat,
        "synthetic": bool(a.synthetic), "seconds": round(time.time() - t0, 1),
    }
    notes = {"status": "described, not carried (E-023 (1)): no level, no pass line, no pick",
             "not_modelled": out["menu"]["note_not_modelled"].iloc[0] if len(out["menu"]) else ""}
    frames = {"pp_reading": out["reading"], "pp_gate": out["gate"], "pp_menu": out["menu"]}
    desc = {"pp_reading": "RD-02's reading: identity, oracle, mechanics, scorecard, paired, diverge, gate, coverage",
            "pp_gate": "RD-02's gates beside: the new cells' point, bound and zero-edge twin rows",
            "pp_menu": "RD-02's menu: each cell's headline and labels, the counts, the standing notes"}

    def write(where: Path | None) -> list[str]:
        names = []
        for name in RESULTS:
            df = frames[name]
            if name == "pp_gate" and df.empty:
                import pandas as pd

                df = pd.DataFrame({"note": ["no gate run"]})
            csv, man = XR.write_result(df, name if not a.synthetic else f"{name}_synthetic", script=SCRIPT,
                                       seed=int(out["honesty_seed"]), parameters=params, results_dir=where,
                                       description=desc[name], exploratory=False, prereg_id=RUN.PREREG_ID,
                                       variant_count=len(out["runs"]), notes=notes)
            XR.read_result(csv)
            names += [csv.name, man.name]
        return names

    wrote = write(target)
    print(f"written: {wrote}; {time.time() - t0:.0f} s", flush=True)
    pm = SI.peak_memory()
    if pm:
        print(pm)
    print("EXIT 0", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
