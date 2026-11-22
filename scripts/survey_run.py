"""The one entry of a pinned design search's survey (Wave 5; `extended/survey.py`, M-4).

    python scripts/run_clean.py --name <job> -- python scripts/survey_run.py prereg/F-NN_<name>.md

Exactly one argument, the declaration's path relative to the repository. The survey refuses unless this script is the
process's `__main__`, invoked as exactly `python scripts/survey_run.py <declaration>` (no `-c`, `-m`, `-i`, `-X` or
other flag; no PYTHONSTARTUP, PYTHONINSPECT or PYTHONPATH; Q-186 m-4), inside a clean run of a clean tree, so no step
can be patched in process; this script's own sha256 is bound by the declaration's `objective.code_sha256`. It writes
only under `results/`, its outputs named `<F-NN>_survey_*`, and records the run once in
`%LOCALAPPDATA%/stage2-extended-runs/survey_once.jsonl` before its first cell (m-5). Prints the token and the list
file's sha256 (or that the search closes).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

USAGE = "usage: python scripts/survey_run.py prereg/F-NN_<name>.md   (one argument, under scripts/run_clean.py)"


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else list(argv)
    if len(args) != 1 or args[0].startswith("-"):
        print(USAGE, file=sys.stderr)
        return 2
    from extended import survey as SV

    decl = ROOT / args[0]
    spec = SV.load_spec(decl.read_bytes())
    out = SV.run_survey(decl, results_dir=ROOT / "results", name=f"{spec.prereg_id}_survey")
    print(json.dumps({"token": out.token, "list": str(out.list_path.relative_to(ROOT)), "list_sha256": out.list_sha256,
                      "finalists": len(out.finalists), "cells": out.counts["cells"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
