"""RD-02's reading (`prereg/RD-02_payout_policy.md`, pinned under E-082; section 14): payout policy in a user's first
months, described, never carried -- the 11 runs on both arms, the 32 replays and 8 gates beside, from a clean checkout,
its reads authorised under the declaration's three purposes, after its identities.

    python scripts/run_clean.py --name pp-reading --commit <the run's commit> --task Q-105 --hours 8 --mem-gb 2.5 \\
        -- python scripts/pp_reading.py --workers 2
    python scripts/pp_reading.py --synthetic --results-dir <a temporary folder>    # the pipeline on a synthetic toy

**Refusing, before any of the engine's work** (exit 3, nothing written, nothing ledgered):

* outside a clean run (`extended.results.clean_run_problem`), in the real mode;
* **section 14's waits (the second read's R3)**: unless, for each waited identity, a row of `DECISIONS.md` carries the
  literal token the lead marks a holding identity with (`WAITS`): `identity-holds: pp_identity` (8.1 items 1 to 3,
  step 1), `identity-holds: Q-80` (the re-composed gate), `identity-holds: Q-93` (U1's start rows with a class),
  `identity-holds: Q-101` (with the recorder) and `identity-holds: t10w2` (T-10 at two workers). The token is matched
  exactly (`identity-holds: Q-8` is not `identity-holds: Q-80`); the rows carrying each are named in every manifest
  (r4). `--workers` above 2 is refused, and 2 only with `identity-holds: t10w2` (r5);
* unless Q-44's per-start file is on the tree and verifies (8.1 item 6), and the inputs' preflight holds (Q-44's file
  read as text with its columns and rows; each design's registered gate row, one a shift);
* unless every E-015 limit given (`--limit ROW COLUMN max|min BOUND`) names a row of `DECISIONS.md` -- in the checkout,
  so approved before the run's commit -- that mentions E-015, and a menu column (`pp_run.limit_columns`);
* unless the adapter's files are the commit's (their blob ids are recorded, Q-102's m7);
* unless the reads are authorised under each of `payout_scorecard`, `payout_ladder_beside` and `payout_gate_beside`
  with the declaration -- **all three checked first by `reader.authorise` (which reads and writes nothing) and the
  engine's files found, before any is ledgered by `reader.authorise_engine_read`** (n1); once each; a further run only
  with `--repeat E-NNN`, a row naming the file (E-053).

**Then** `extended.pp_run.run_reading` (its order and checks: that module's docstring); any failed check refuses and
writes nothing. **Written** through `extended.results.write_result`, each with its manifest: `pp_reading.csv` (sections
identity, oracle, mechanics, scorecard, paired, diverge, coverage and beside, each row's `part` within it),
`pp_gate.csv` (the gate rows, the pairing with the base's registered paths, the gate's reading and divergences, the held
counts) and `pp_menu.csv` (the menu) -- `prereg_id` RD-02, the pinning row, the waited rows, the run counts, every seed
with the retired ones, the parameters and section 4's assumptions, the class, the adapter's commit and blob ids, the
data manifest's and the calendars' sha256, the E-015 limits flagged, `exploratory=False`, every cell "described, not
carried".
"""
from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path
from typing import Any, Callable, Sequence

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
#: section 14's waits (R3): each waited identity and the literal token a row of DECISIONS.md must carry for it
WAITS = {"pp_identity": "identity-holds: pp_identity", "Q-80": "identity-holds: Q-80",
         "Q-93": "identity-holds: Q-93", "Q-101": "identity-holds: Q-101", "t10w2": "identity-holds: t10w2"}
MAX_WORKERS = 2


def token_pattern(token: str) -> re.Pattern:
    """The token matched exactly: not inside a longer word or id (`identity-holds: Q-80` is not `... Q-801`)."""
    return re.compile(r"(?<![\w-])" + re.escape(token) + r"(?![\w-])")


def wait_rows(text: str) -> dict[str, list[str]]:
    """{waited identity: the ids of the DECISIONS.md rows carrying its token}."""
    out: dict[str, list[str]] = {}
    pats = {k: token_pattern(tok) for k, tok in WAITS.items()}
    for line in text.splitlines():
        m = reader.ROW.match(line)
        if not m:
            continue
        for k, p in pats.items():
            if p.search(line):
                out.setdefault(k, []).append(m.group(1))
    return out


def wait_problems(text: str, workers: int) -> list[str]:
    """Section 14's waits (R3, r5): a row carrying each token; at most `MAX_WORKERS`, two only once T-10 held at two."""
    got = wait_rows(text)
    out = [f"no row of DECISIONS.md carries `{tok}` (the wait for {k} is not met)" for k, tok in WAITS.items()
           if not got.get(k)]
    if int(workers) < 1 or int(workers) > MAX_WORKERS:
        out.append(f"--workers {workers}: one or {MAX_WORKERS} only (the machine's rule)")
    if int(workers) > 1 and not got.get("t10w2"):
        out.append(f"--workers {workers}: two workers need T-10 held at two workers (`{WAITS['t10w2']}`, r5)")
    return out


def parse_limits(raw: Sequence[Sequence[str]] | None, text: str) -> tuple[list[dict[str, Any]], list[str]]:
    """`--limit ROW COLUMN KIND BOUND` -> the limits and their problems: the row in DECISIONS.md (the checkout's, so
    approved before the run's commit) mentioning E-015; the column, kind and bound as `pp_run.limit_problems` asks."""
    from extended import pp_run as RUN

    limits, probs = [], []
    for item in raw or []:
        rid, col, kind, bound = item
        row = reader.decision_row(text, rid)
        if row is None:
            probs.append(f"--limit {rid}: no such decision row")
        elif "E-015" not in row:
            probs.append(f"--limit {rid}: the row does not mention E-015")
        try:
            b = float(bound)
        except ValueError:
            b = float("nan")
        limits.append({"row": rid, "column": col, "kind": kind, "bound": b})
    probs += RUN.limit_problems(limits)
    return limits, probs


def authorise_all(purposes: Sequence[str], *, files: Sequence[Path], declaration: str, repeat: str | None, what: str,
                  check: Callable[..., Any] | None = None, ledger: Callable[..., Any] | None = None) -> list[Any]:
    """n1: every purpose checked by `reader.authorise` (reads nothing, writes nothing) and every file found before any
    purpose is ledgered by `reader.authorise_engine_read`; a refusal leaves nothing ledgered."""
    check = reader.authorise if check is None else check
    ledger = reader.authorise_engine_read if ledger is None else ledger
    for purpose in purposes:
        check(reader.CHOICE_START, reader.JUDGED_END, purpose=purpose, declaration=declaration, repeat=repeat,
              what=f"{what}: {purpose}")
    absent = [str(f) for f in files if not Path(f).is_file()]
    if absent:
        raise FileNotFoundError(f"{what}: {absent[:3]} do not exist")
    return [ledger(reader.CHOICE_START, reader.JUDGED_END, purpose=purpose, declaration=declaration, repeat=repeat,
                   files=files, what=f"{what}: {purpose}") for purpose in purposes]


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--limit", nargs=4, action="append", metavar=("ROW", "COLUMN", "KIND", "BOUND"),
                    help="an E-015 limit approved before the run's commit: its row, a menu column, max or min, a bound")
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
    text = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    waits: dict[str, list[str]] = {}
    if a.synthetic:
        if not a.results_dir:
            print("REFUSED (RD-02): --synthetic writes to --results-dir only")
            return 2
        if XR.protected(a.results_dir):
            print("REFUSED (RD-02): --synthetic never writes to a results/ folder of this repository")
            return 3
        if a.limit:
            print("REFUSED (RD-02): --limit is the real run's only")
            return 2
        from extended import pp_run_synthetic as SYN

        inputs, designs, starts, reps = SYN.SyntheticInputs(plant=a.plant, n_paths=3), SYN.DESIGNS, SYN.STARTS, 20
        sens, window, target = SYN.DESIGNS[0], ("08:30", "15:10"), Path(a.results_dir)
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
        probs = wait_problems(text, a.workers)
        waits = wait_rows(text)
        limits, lp = parse_limits(a.limit, text)
        probs += lp
        q44 = ROOT / "results" / "user_beside_starts.csv"
        ok, msg = XR.verify_result(q44) if q44.is_file() else (False, "absent")
        if not ok:
            probs.append(f"Q-44's per-start file (8.1 item 6): {msg}")
        inputs, designs, starts, reps = RUN.RealInputs(), RUN.DESIGNS, None, None
        if not probs:
            probs += inputs.preflight(designs)
        if probs:
            print("REFUSED (RD-02, 8.1 and section 14's waits): " + "; ".join(probs))
            print("EXIT 3", flush=True)
            return 3
        try:
            RUN.adapter_provenance(ROOT, strict=True)
            authorise_all(RUN.PURPOSES, files=SI.engine_files(VENDOR, bars=True), declaration=RUN.DECLARATION,
                          repeat=a.repeat, what=f"RD-02's reading ({SCRIPT})")
        except (reader.ReadRefused, FileNotFoundError, ValueError, RUN.Refused) as exc:
            print(SI.refusal(exc) if isinstance(exc, (reader.ReadRefused, FileNotFoundError)) else f"REFUSED: {exc}")
            print("EXIT 3", flush=True)
            return 3
        sens, window, target = RUN.SENSITIVITY_DESIGN, ("08:30", "15:10"), None
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

    sec11 = RUN.section_11(ROOT)
    runs = out["runs"]
    params = {
        "reading": "RD-02 (reading PP): described, not carried", "pinning_row": RUN.PIN_ROW,
        "declaration": RUN.DECLARATION, "declaration_sha256_lf": RUN.sha256_lf(ROOT / RUN.DECLARATION),
        "waits": ({k: {"token": tok, "rows": waits.get(k, [])} for k, tok in WAITS.items()} if not a.synthetic else
                  "the synthetic run waits for nothing"),
        "runs": [list(r) for r in runs], "run_count": len(runs),
        "run_counts": {"policy_runs": sum(1 for r in runs if r[2] == "declared"),
                       "new": sum(1 for r in runs if r[2] == "declared" and r[1] != "ref"),
                       "references": sum(1 for r in runs if r[1] == "ref"),
                       "rule_sensitivity": sum(1 for r in runs if r[2] == "minimal"),
                       "replays_beside": len(RUN.BESIDE) * sum(1 for r in runs if r[2] == "declared"),
                       "gates": len(RUN.NEW_CELLS) * len(designs),        # the new cells' gates (section 12),
                       "gate_twins": len(RUN.NEW_CELLS) * len(designs)},  # each with its zero-edge twin (9.1 item 8)
        "beside": {"responses": list(RUN.BESIDE), "arm": "verdict", "cells": "the policy cells (not the sensitivity)"},
        "gates": {"cells": list(RUN.NEW_CELLS), "paths": int(inputs.n_paths()), "twin": True, "levels": [0.0]},
        "recorder_columns": list(RUN.RECORD_COLUMNS),
        "seeds": {"honesty_series": out["honesty_seed"], "section_11": sec11,
                  "retired": [r["seed"] for r in sec11 if r["status"].lower().startswith("retired")],
                  "ladder": "Q-17's lockstep.child_seed(20261920, 0, start_day), as run_starts draws them",
                  "inherited": "P-14's 20261131, P-16's 20261206 and 20261102 (their registered gate calls)"},
        "honesty": {"settings": [list(s) for s in out["honesty_settings"]],
                    "series_per_setting": int(reps or RUN.RD.HONESTY_SERIES)},
        "assumptions": ["the request's timing: after 5:00 PM CT (Stage 2 D-175)",
                        "the request's amount: any amount from the minimum to the maximum (E-034: unstated; half "
                        "needs it)", "the payout method: Aeropay, $0, 3 trading days (D-24)",
                        "the placement off (D-289) and 0 % denial (D-234) in the headline"],
        "no_effect_on_these_trades": [list(k) for k in out["no_effect"]],
        "funded_account_cls": {c: f"{PP.cell_class(c).__module__}.{PP.cell_class(c).__qualname__}" for c in PP.CELLS},
        "adapter": prov, "calendars": dict(RUN.CALENDARS),
        "data_manifest_sha256": sha256_of(ROOT / "vendor" / "DATA_MANIFEST_stage2.sha256"),
        "limits": limits or "none approved before the run's commit", "repeat": a.repeat,
        "workers": int(a.workers), "synthetic": bool(a.synthetic), "seconds": round(time.time() - t0, 1),
    }
    notes = {"status": "described, not carried (E-023 (1)): no level, no pass line, no pick",
             "not_modelled": out["menu"]["note_not_modelled"].iloc[0] if len(out["menu"]) else ""}
    frames = {"pp_reading": out["reading"], "pp_gate": out["gate"], "pp_menu": out["menu"]}
    desc = {"pp_reading": "RD-02's reading: identity, oracle, mechanics, scorecard, paired, diverge, coverage, beside",
            "pp_gate": "RD-02's gates beside: the new cells' rows, their pairing with the base's registered paths, the "
                       "gate reading and divergences beside the base's registered row, the held counts",
            "pp_menu": "RD-02's menu: each cell's headline, guarded measures, flags and labels, the counts, the notes"}

    def write(where: Path | None) -> list[str]:
        import pandas as pd

        names = []
        for name in RESULTS:
            df = frames[name]
            if name == "pp_gate" and df.empty:
                df = pd.DataFrame({"note": ["no gate run"]})
            csv, man = XR.write_result(df, name if not a.synthetic else f"{name}_synthetic", script=SCRIPT,
                                       seed=int(out["honesty_seed"]), parameters=params, results_dir=where,
                                       description=desc[name], exploratory=False, prereg_id=RUN.PREREG_ID,
                                       variant_count=len(runs), notes=notes)
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
