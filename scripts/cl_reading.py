"""RD-03's reading (`prereg/RD-03_contract_levers.md`, pinned under E-152; section 15, steps 3 to 5; its build Q-119):
contract-use levers on P-14's and P-16's registered trades, described, never carried -- each step from a clean checkout
of a named commit, under the run lock, after the lead's row records the step before.

    python scripts/run_clean.py --name cl-step3 --commit <sha> --task RD-03 --hours <h> --mem-gb <g> \\
        -- python scripts/cl_reading.py --step 3 --stage0-row E-NNN --workers 2
    python scripts/run_clean.py ... -- python scripts/cl_reading.py --step 4 --after E-NNN
    python scripts/run_clean.py ... -- python scripts/cl_reading.py --step 5 --after E-NNN
    python scripts/cl_reading.py --step 3 --synthetic --results-dir <a temporary folder>   # the pipeline on toys

(Step 1 is `identity/cl_fit_identity.py` and `identity/cl_identity.py`; step 2 is `scripts/cl_fit.py`.)

**Refusing, before any of the engine's work** (exit 3, nothing written, nothing ledgered):

* outside a clean run (`extended.results.clean_run_problem`), in the real mode;
* **the waits of section 15**, all before step 3, by the positional token (`identity-holds: <id> @ <sha> -- ...`, the
  third cell of a row; `extended/identity_tokens.py`, E-104) at this run's HEAD or an ancestor with the identity's
  cover unchanged since (Q-111's covers: `extended/identity_cover.cover(id)` for the shared ones, never less; for this
  reading's own and for Q-05, `BASE`, the instrument and its import closure, `identity_cover.imports`):
  - Q-115 merged (`levers_terms.unmerged_keys()` empty: every key read from the working record);
  - the shared identities held again after it: Q-05, Q-80, Q-93 (with Q-100's seams), Q-101;
  - the pinning row (the declaration hashing to its pin in DECISIONS.md);
  - Q-44's file (`results/user_beside_starts.csv`) on the tree and verifying;
  - step 1's `cl_identity` held; and step 2 recorded (`--stage0-row`, a row naming `cl_fit`), whatever its outcome;
  - two workers only once `cl_t10w2` (T-10 at two workers, A-1 (d)) is held;
* steps 4 and 5: `--after`, the lead's row recording the step before (a row naming `cl_reading`);
* E-015's limits read only from `e015-limits:` rows (RD-02's parser, `pp_run.limit_rows`);
* unless the adapters' files are the commit's (their blob ids recorded);
* the judged-block purposes of the step (`levers_scorecard` and `levers_gate_beside` in step 3, `levers_ladder_beside`
  in step 4, `levers_ftp_beside` in step 5) all checked first by `reader.authorise`, then each ledgered by
  `reader.authorise_engine_read` **just before its stage**; once each; a further run only with `--repeat E-NNN`.

**Then** `extended.cl_reading` (its order and checks); any failed check refuses and writes nothing. **Written**
through `extended.results.write_result`, each with its manifest: step 3 `cl_reading.csv` (sections identity, oracle,
mechanics, scorecard, guard, paired, diverge, coverage), `cl_gate.csv`, `cl_menu.csv`; step 4 `cl_reading_ladder.csv`
(sections identity, ladder, rtp); step 5 `cl_reading_ftp.csv` (sections identity, ftp) and `cl_menu_beside.csv` (the
menu's beside sections) -- a result file is never overwritten, so the beside sections that section 15 names in
`cl_reading.csv` are written in files of their own, each naming the step-3 file it sits beside.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable, Sequence

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for _p in (str(ROOT), str(ROOT / "identity")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from extended import identity_cover as _IC  # noqa: E402
from extended import reader, use_vendored_stage2  # noqa: E402

use_vendored_stage2()

SCRIPT = "scripts/cl_reading.py"
VENDOR = ROOT / "vendor" / "stage2"
MAX_WORKERS = 2
BASE: tuple[str, ...] = tuple(_IC.BASE)
#: each own wait's instrument
WAIT_SCRIPTS = {"cl_identity": "identity/cl_identity.py", "cl_t10w2": "tests/cl_synthetic.py",
                "Q-05": "identity/stage2_identity.py"}
OWN_WHAT = {"cl_identity": "RD-03's own identity (9.1 items 1 and 2): the reference through A-1 by A-2 and A-3",
            "cl_t10w2": "T-10 at two workers: the counters' channel on the replay and the gate (A-1 (d))",
            "Q-05": "U1's start rows reproduced (identity/stage2_identity.py, E-010)"}
OWN_SEARCH = {"cl_identity": tuple(_IC.SEARCH), "cl_t10w2": (*_IC.SEARCH, "tests"), "Q-05": tuple(_IC.SEARCH)}
SHARED_WAITS = {"Q-80": "the gate through its re-composed campaign, 500 paths, every arm (E-049)",
                "Q-93": "U1's start rows through run_starts with a declared class and Q-100's seams (E-059 (1))",
                "Q-101": "U1's start rows with the replay recorder on (E-068)"}
STEP_PURPOSES = {3: ("levers_scorecard", "levers_gate_beside"), 4: ("levers_ladder_beside",),
                 5: ("levers_ftp_beside",)}
RESULTS = {3: ("cl_reading", "cl_gate", "cl_menu"), 4: ("cl_reading_ladder",), 5: ("cl_reading_ftp", "cl_menu_beside")}


def own_cover(ident: str, root: Path | str = ROOT) -> tuple[str, ...]:
    """An own wait's cover by Q-111's rule: `BASE`, the instrument and every repository file its imports reach."""
    c = _IC.imports(WAIT_SCRIPTS[ident], root, OWN_SEARCH[ident])
    return tuple(dict.fromkeys((*BASE, WAIT_SCRIPTS[ident], *sorted(set(c.files) - {WAIT_SCRIPTS[ident]}))))


def wait_table(root: Path | str = ROOT) -> dict[str, tuple[str, tuple[str, ...]]]:
    out = {k: (OWN_WHAT[k], own_cover(k, root)) for k in ("Q-05", "cl_identity")}
    out.update({k: (w, tuple(_IC.cover(k))) for k, w in SHARED_WAITS.items()})
    out["cl_t10w2"] = (OWN_WHAT["cl_t10w2"], own_cover("cl_t10w2", root))
    return out


def _git(repo: Path | str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def wait_problems(text: str, workers: int, repo: Path | str, head: str, waits: dict | None = None) -> tuple[list[str],
                                                                                                          dict]:
    """Section 15's identity waits through Q-110's parser: no breach of the token rules first, then each wait met at
    `head` (`IT.held_report`); two workers only once `cl_t10w2` is met. Returns (problems, the tokens met)."""
    from extended import identity_tokens as IT

    waits = wait_table(repo) if waits is None else waits
    breaches = IT.problems(text)
    if breaches:
        return [f"DECISIONS.md breaches the identity-holds rule, so no wait is read: {b}" for b in breaches], {}
    out: list[str] = []
    met: dict[str, Any] = {}
    for k, (what, cov) in waits.items():
        if k == "cl_t10w2" and int(workers) < 2:
            continue
        try:
            tok, why = IT.held_report(text, k, repo, head, list(cov))
        except ValueError as exc:
            out.append(f"the wait for {k}: {exc}")
            continue
        met[k] = tok
        if tok is None:
            out.append(f"the wait for {k} ({what}) is not met at {head[:12]}: " + "; ".join(why))
    if int(workers) < 1 or int(workers) > MAX_WORKERS:
        out.append(f"--workers {workers}: one or {MAX_WORKERS} only (the machine's rule)")
    return out, met


def row_problems(text: str, row: str | None, must_name: str, what: str) -> list[str]:
    """A row of DECISIONS.md that exists and names `must_name` (the lead's record of the step before)."""
    import re

    if not row:
        return [f"{what}: give the lead's row recording it"]
    for line in text.splitlines():
        if re.match(rf"^\|\s*{re.escape(row)}\s*\|", line):
            return [] if must_name in line else [f"{what}: {row} does not name {must_name}"]
    return [f"{what}: no row {row} in DECISIONS.md"]


def pin_problems(text: str, root: Path = ROOT) -> list[str]:
    from extended import cl_reading as CL
    from extended import pp_run as PR

    p = root / CL.DECLARATION
    if not p.is_file():
        return [f"{CL.DECLARATION} is not on the tree (the pin renames the draft)"]
    pins = reader.pins(text).get(CL.DECLARATION) or set()
    return [] if PR.sha256_lf(p) in pins else [f"{CL.DECLARATION} does not hash to its pin in DECISIONS.md"]


def authorise_check(purposes: Sequence[str], *, files: Sequence[Path], repeat: str | None, what: str) -> None:
    """Every purpose of the step checked by `reader.authorise` (reads nothing, writes nothing), and the engine's files
    found, before any is ledgered."""
    from extended import cl_reading as CL

    for purpose in purposes:
        reader.authorise(reader.CHOICE_START, reader.JUDGED_END, purpose=purpose, declaration=CL.DECLARATION,
                         repeat=repeat, what=f"{what}: {purpose}")
    absent = [str(f) for f in files if not Path(f).is_file()]
    if absent:
        raise FileNotFoundError(f"{what}: {absent[:3]} do not exist")


def ledger(purpose: str, *, files: Sequence[Path], repeat: str | None, what: str) -> Any:
    """One purpose ledgered by `reader.authorise_engine_read`, just before its stage."""
    from extended import cl_reading as CL

    return reader.authorise_engine_read(reader.CHOICE_START, reader.JUDGED_END, purpose=purpose,
                                        declaration=CL.DECLARATION, repeat=repeat, files=files,
                                        what=f"{what}: {purpose}")


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--step", type=int, choices=(3, 4, 5), required=True)
    ap.add_argument("--stage0-row", default=None, help="step 3: the lead's row recording step 2 (stage 0)")
    ap.add_argument("--after", default=None, help="steps 4 and 5: the lead's row recording the step before")
    ap.add_argument("--repeat", default=None, help="a further run's row (E-NNN) naming the declaration (E-053)")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--synthetic", action="store_true", help="the pipeline on toy campaigns into --results-dir")
    ap.add_argument("--results-dir", default=None, help="with --synthetic: where the files go")
    ap.add_argument("--days", type=int, default=160, help="with --synthetic: the toy's sessions")
    ap.add_argument("--paths", type=int, default=3, help="with --synthetic: the toy gates' paths")
    ap.add_argument("--stage0-stopped", action="store_true", help="step 3: stage 0 stopped (its row --stage0-row)")
    return ap


def main(argv: list[str] | None = None) -> int:
    a = parser().parse_args(argv)
    import stage2_identity as SI

    from extended import cl_reading as CL
    from extended import levers_terms as LT
    from extended import pp_run as PR
    from extended import results as XR

    t0 = time.time()
    text = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    head = _git(ROOT, "rev-parse", "HEAD").stdout.strip()
    met: dict[str, Any] = {}
    limits, limit_rows_used = [], []
    files = SI.engine_files(VENDOR, bars=True)
    what = f"RD-03's reading ({SCRIPT}), step {a.step}"
    if a.synthetic:
        if not a.results_dir or XR.protected(a.results_dir):
            print("REFUSED (RD-03): --synthetic writes to a --results-dir outside this repository's results/ only")
            return 3
        from extended import cl_toy_inputs as TI

        inputs, designs, seed, reps = TI.ToyInputs(n_days=a.days, n_paths=a.paths), TI.DESIGNS, None, 20
        target = Path(a.results_dir)
        exists = [n for n in RESULTS[a.step] if (target / f"{n}_synthetic.csv").exists()]
        if exists:
            print(f"REFUSED (RD-03, m7): {exists} already exist in {target}")
            return 3
        seed = CL.declared_seed(CL.HONESTY_ROLE, ROOT, strict=False)
        authorise_gate = None
    else:
        if a.results_dir:
            print("REFUSED (RD-03): --results-dir is the synthetic run's only")
            return 2
        probs: list[str] = []
        prob = XR.clean_run_problem()
        if prob:
            probs.append(f"the reading runs only from a clean checkout -- {prob}")
        unmerged = LT.unmerged_keys()
        if unmerged:
            probs.append(f"Q-115 is not merged: {unmerged} are read from {LT.Q115_COMMIT} (4.1, 15's waits)")
        wp, met = wait_problems(text, a.workers, ROOT, head)
        probs += wp + pin_problems(text)
        if a.step == 3:
            probs += row_problems(text, a.stage0_row, "cl_fit", "step 2 recorded (stage 0)")
        else:
            probs += row_problems(text, a.after, "cl_reading", f"step {a.step - 1} recorded")
        q44 = ROOT / "results" / "user_beside_starts.csv"
        ok, msg = XR.verify_result(q44) if q44.is_file() else (False, "absent")
        if not ok:
            probs.append(f"Q-44's per-start file (9.1 item 6): {msg}")
        limits, limit_rows_used, lp, _ = PR.limit_rows(text)
        probs += lp
        inputs, designs, reps, target = CL.CLInputs(), CL.DESIGNS, None, None
        if not probs:
            probs += inputs.preflight(designs)
        if probs:
            print("REFUSED (RD-03, section 15's waits): " + "; ".join(probs))
            print("EXIT 3", flush=True)
            return 3
        exists = [n for n in RESULTS[a.step] if (ROOT / "results" / f"{n}.csv").exists()]
        if exists:
            print(f"REFUSED (RD-03, m7): {exists} already exist; a result is never overwritten -- nothing ledgered")
            print("EXIT 3", flush=True)
            return 3
        try:
            CL.adapter_provenance(ROOT, strict=True)
            authorise_check(STEP_PURPOSES[a.step], files=files, repeat=a.repeat, what=what)
            ledger(STEP_PURPOSES[a.step][0], files=files, repeat=a.repeat, what=what)
        except (reader.ReadRefused, FileNotFoundError, CL.Refused) as exc:
            print(SI.refusal(exc) if isinstance(exc, (reader.ReadRefused, FileNotFoundError)) else f"REFUSED: {exc}")
            print("EXIT 3", flush=True)
            return 3
        seed = None

        def authorise_gate() -> None:                        # step 3 (c): just before the gates
            ledger(STEP_PURPOSES[3][1], files=files, repeat=a.repeat, what=what)
    kw = {} if reps is None else {"honesty_reps": reps}
    try:
        prov = CL.adapter_provenance(ROOT, strict=not a.synthetic)
        if a.step == 3:
            out = CL.run_scorecard(inputs, designs=designs, workers=a.workers, honesty_seed=seed,
                                   approved_limits=limits, authorise_gate=authorise_gate,
                                   solver_view=solver_view(a, target), **kw)
            frames = {"cl_reading": out["reading"], "cl_gate": out["gate"], "cl_menu": out["menu"]}
        else:
            stage = "ladder" if a.step == 4 else "ftp"
            gate_file = (target / "cl_gate_synthetic.csv") if a.synthetic else ROOT / "results" / "cl_gate.csv"
            ok, msg = XR.verify_result(gate_file) if gate_file.is_file() else (False, "absent")
            if not ok:
                raise CL.Refused(f"step 3's gate file {gate_file.name} (M3): {msg}")
            gg = CL.gate_guard_from_file(XR.read_result(gate_file))
            out = CL.run_beside(inputs, stage, designs=designs, workers=a.workers, honesty_seed=seed, gate_guard=gg,
                                **kw)
            frames = {RESULTS[a.step][0]: out["reading"]}
            if a.step == 5:
                frames["cl_menu_beside"] = out["menu"]
    except CL.Refused as exc:
        print(f"REFUSED (RD-03): {exc} -- nothing written", flush=True)
        print("EXIT 3", flush=True)
        return 3
    from propedge.reporting.results import sha256_of

    params = {
        "reading": "RD-03 (reading CL): described, not carried", "pinning_row": CL.PIN_ROW, "step": a.step,
        "declaration": CL.DECLARATION, "purposes": list(STEP_PURPOSES[a.step]),
        "waits": ({k: {"row": t.row, "commit": t.sha} if t else None for k, t in met.items()}
                  if not a.synthetic else "the synthetic run waits for nothing"),
        "stage0_row": a.stage0_row, "after": a.after, "head": head,
        "runs": [list(r) for r in out["runs"]], "run_count": len(out["runs"]),
        "counts_declared": {"new_cells": len(CL.NEW_CELLS), "references": 2, "replays_beside": 360,
                            "reference_checks": 28, "gates": 30},
        "seeds": {"honesty_series": out["honesty_seed"],
                  "ladder": "Q-17's lockstep.child_seed(20261920, 0, start_day), as run_starts draws them",
                  "gates": "inherited: P-14's 20261131, P-16's 20261206 (their registered gate calls)"},
        "readings_4_3": {r.name: {"value": r.value, "cites": r.cites, "label": r.label}
                         for r in __import__("extended.levers_readings", fromlist=["READINGS"]).READINGS},
        "record": {"dates_read": LT.record_dates(), "sources": {k: LT.record_source(k) for k in LT.RECORD_KEYS}},
        "adapter": prov, "calendars_checked": out.get("calendars_checked", "not read in this step"),
        "data_manifest_sha256": sha256_of(ROOT / "vendor" / "DATA_MANIFEST_stage2.sha256"),
        "limits": ({"rows": limit_rows_used, "limits": limits} if limits else
                   "none approved before the run's commit: no e015-limits row in DECISIONS.md"),
        "repeat": a.repeat, "workers": int(a.workers), "synthetic": bool(a.synthetic),
        "seconds": round(time.time() - t0, 1),
    }
    notes = {"status": "described, not carried (E-023 (1)): no level, no pass line, no pick; every cell labelled so"}
    names = []
    for name, df in frames.items():
        csv, man = XR.write_result(df, name if not a.synthetic else f"{name}_synthetic", script=SCRIPT,
                                   seed=int(out["honesty_seed"]), parameters=params, results_dir=target,
                                   description=f"RD-03 step {a.step}: {name}", exploratory=False,
                                   prereg_id=CL.PREREG_ID, variant_count=len(out["runs"]), notes=notes)
        XR.read_result(csv)
        names += [csv.name, man.name]
    print(f"written: {names}; {time.time() - t0:.0f} s", flush=True)
    pm = SI.peak_memory()
    if pm:
        print(pm)
    print("EXIT 0", flush=True)
    return 0


def solver_view(a: Any, target: Path | None) -> Any:
    """M7: stage 0's view for the menu -- `cl_fit.csv`'s `solver_view` section, verified (in the synthetic run, a file
    in the results folder if one is there); "stage 0 stopped (row ...)" when it stopped; None when not given."""
    from extended import cl_reading as CL

    if a.stage0_stopped:
        return f"stage 0 stopped (row {a.stage0_row}): no solver's view"
    path = (target / "cl_fit_synthetic.csv") if a.synthetic else ROOT / "results" / "cl_fit.csv"
    if not path.is_file():
        if a.synthetic:
            return None
        raise CL.Refused("results/cl_fit.csv is not on the tree (step 2's output, or --stage0-stopped)")
    return CL.solver_view_frame(path)


if __name__ == "__main__":
    sys.exit(main())
