"""R11's acceptance on record (D-483): the full reproductions of P-06, P-09, P-10 and P-11 against their registered files.

    python scripts/r11_reproductions.py [--repro-dir %LOCALAPPDATA%/stage2-repro]

Reads each `<repro-dir>/<P-xx>/reproduction.json` that `scripts/reproduce_registered.py` wrote (D-479) and compares,
again and independently of that tool, each reproduced file with the registered one in `results/`: as written text,
cell for cell, on every registered column (read with `dtype=str`, so no parser can round a value), plus the sha256 of
both files. A reproduced file may carry columns the registered one lacks -- reporting columns added to the engine after
the registration -- and those are listed with the values they hold, never compared and never hidden. Writes
`results/r11_reproductions.csv` with its manifest: a deterministic reading, nothing drawn, no seed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import pandas as pd  # noqa: E402

from propedge import RESULTS_DIR  # noqa: E402
from propedge.reporting.results import write_result  # noqa: E402

SCRIPT = "scripts/r11_reproductions.py"
PREREGS = ("P-06", "P-09", "P-10", "P-11")


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def compare(registered: Path, reproduced: Path) -> dict:
    a = pd.read_csv(registered, dtype=str, keep_default_na=False, low_memory=False)
    b = pd.read_csv(reproduced, dtype=str, keep_default_na=False, low_memory=False)
    missing = [c for c in a.columns if c not in b.columns]
    added = [c for c in b.columns if c not in a.columns]
    same_rows = len(a) == len(b)
    differing = {c: int((a[c] != b[c]).sum()) for c in a.columns if c in b.columns and same_rows and (a[c] != b[c]).any()}
    order_kept = [c for c in b.columns if c in a.columns] == [c for c in a.columns if c in b.columns]
    ok = same_rows and not missing and not differing and order_kept
    added_values = {c: sorted(set(b[c])) for c in added}
    if ok and not added:
        status = "IDENTICAL"
    elif ok:
        status = "REGISTERED COLUMNS IDENTICAL, COLUMNS ADDED"
    else:
        status = "DIFFERS"
    return {"rows": len(a), "registered_columns": a.shape[1], "reproduced_columns": b.shape[1], "status": status,
            "byte_identical": _sha(registered) == _sha(reproduced), "registered_sha256": _sha(registered),
            "reproduced_sha256": _sha(reproduced), "missing_columns": ";".join(missing),
            "added_columns": ";".join(added), "added_column_values": json.dumps(added_values, sort_keys=True),
            "differing_cells": json.dumps(differing, sort_keys=True), "column_order_kept": order_kept}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repro-dir", default=str(Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "stage2-repro"))
    a = ap.parse_args(argv)
    rows = []
    for pid in PREREGS:
        rec = json.loads((Path(a.repro_dir) / pid / "reproduction.json").read_text(encoding="utf-8"))
        for name in rec["comparison"]:
            c = compare(RESULTS_DIR / name, Path(a.repro_dir) / pid / name)
            rows.append({"prereg": pid, "file": f"results/{name}", "script": rec["script"],
                         "engine_commit": rec["git_commit"], "paths": rec["registered_paths"] if rec["paths"] is None
                         else rec["paths"], "seconds": rec["seconds"], "tool_line": rec["comparison"][name]["line"], **c})
    df = pd.DataFrame(rows)
    csv, _ = write_result(df, "r11_reproductions", script=SCRIPT, seed=None, require_seed=False, exploratory=False,
                          parameters={"decision": "D-483", "preregs": list(PREREGS), "tool": "scripts/reproduce_registered.py",
                                      "comparison": "as written text, cell for cell, every registered column"},
                          notes={"status": "R11's acceptance: reproductions of registered runs, never verdicts",
                                 "seed": "none: a reading of files"},
                          description="R11 (D-483): each registered file of P-06, P-09, P-10 and P-11 against its full "
                                      "reproduction on the current engine (D-479's tool, from a clean checkout): "
                                      "status, byte identity, added reporting columns and their values.")
    print(df[["prereg", "file", "status", "byte_identical", "added_columns"]].to_string(index=False))
    print(f"wrote {csv.relative_to(ROOT)}")
    return 0 if (df["status"] != "DIFFERS").all() else 1


if __name__ == "__main__":
    raise SystemExit(main())
