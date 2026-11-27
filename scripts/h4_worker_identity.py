"""Q-188b: the units identity at a new H4-B worker count (the lead's ruling on the sizing scout, 2026-11-27).

H4-B's outputs should not depend on its worker count: `run_h4_b` submits its 21-start batches in order and collects
them in the same order (`scripts/h4_rebaseline.py`, the `ProcessPoolExecutor` block: `futs` in batch order, each
`fut.result()` appended in that order), every batch's coin keys are its own (start, seed index) under `h4b_coins` in
part H4-B, and every worker starts from the same context. This script is the check of that claim on real data: a part
re-run at the new count over the first starts of a finished part (`--new`) must equal the finished part's rows for the
same starts (`--ref`) **byte for byte**, row for row, in file order, header included.

    python scripts/h4_worker_identity.py --new <run>/results/h4_units_p14_wid3.csv \\
        --ref "<main tree>/results/h4_units_p14_p1.csv" [--trades-new ... --trades-ref ...] [--tag wid3]

Both files are checked against their sidecar manifests first. The audit-sample trade logs are compared beside, on
their shared columns (a log written since Q-188b carries two more, `need` and `need_logged`). Light (two CSV reads);
writes `results/h4_worker_identity[_tag].csv` with its manifest from a clean run, or prints only with `--no-write`.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SCRIPT = "scripts/h4_worker_identity.py"


class IdentityRefused(RuntimeError):
    """A file fails its manifest, or the two files cannot be compared."""


def _checked(path: Path) -> str:
    raw = Path(path).read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    side = Path(f"{path}.manifest.json")
    if not side.is_file():
        raise IdentityRefused(f"{path} has no sidecar manifest")
    if json.loads(side.read_text(encoding="utf-8")).get("sha256") != sha:
        raise IdentityRefused(f"{path} does not match its manifest's sha256")
    return sha


def _lines(path: Path) -> list[str]:
    return Path(path).read_bytes().decode("utf-8").splitlines()


def units_identity(new: Path, ref: Path, *, key: str = "start_idx") -> dict[str, Any]:
    """The new file's rows against the reference's rows of the same starts (`key`), byte for byte, in order."""
    a, b = _lines(new), _lines(ref)
    if not a or not b:
        raise IdentityRefused("an empty units file")
    head_equal = a[0] == b[0]
    cols = next(csv.reader([a[0]]))
    if key not in cols:
        raise IdentityRefused(f"the units files carry no {key!r} column")
    k = cols.index(key)
    starts = {next(csv.reader([ln]))[k] for ln in a[1:]}
    ref_rows = [ln for ln in b[1:] if next(csv.reader([ln]))[k] in starts]
    new_rows = a[1:]
    n = max(len(new_rows), len(ref_rows))
    differing = sum(1 for i in range(n) if i >= len(new_rows) or i >= len(ref_rows) or new_rows[i] != ref_rows[i])
    return {"what": "units", "starts": len(starts), "rows_new": len(new_rows), "rows_ref": len(ref_rows),
            "header_equal": bool(head_equal), "rows_differing": int(differing),
            "holds": bool(head_equal and differing == 0 and len(new_rows) == len(ref_rows) and new_rows)}


def trades_identity(new: Path, ref: Path, starts: set[str] | None = None) -> dict[str, Any]:
    """Beside: the audit-sample logs of the same starts equal on their shared columns, value for value as written."""
    import pandas as pd

    a = pd.read_csv(new, dtype=str, keep_default_na=False)
    b = pd.read_csv(ref, dtype=str, keep_default_na=False)
    st = set(a["start"].unique()) if starts is None else starts
    b = b[b["start"].isin(st)].reset_index(drop=True)
    shared = [c for c in b.columns if c in a.columns]
    same = a[shared].reset_index(drop=True).equals(b[shared])
    return {"what": "trades (shared columns)", "starts": len(st), "rows_new": len(a), "rows_ref": len(b),
            "header_equal": list(a.columns[: len(b.columns)]) == list(b.columns),
            "rows_differing": 0 if same else -1, "holds": bool(same and len(a) == len(b))}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--new", type=Path, required=True)
    ap.add_argument("--ref", type=Path, required=True)
    ap.add_argument("--trades-new", type=Path, default=None)
    ap.add_argument("--trades-ref", type=Path, default=None)
    ap.add_argument("--workers-new", type=int, default=None, help="the new run's worker count, for the record")
    ap.add_argument("--tag", default="")
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args(argv)
    shas = {"new": _checked(a.new), "ref": _checked(a.ref)}
    rows = [units_identity(a.new, a.ref)]
    if a.trades_new is not None and a.trades_ref is not None:
        shas["trades_new"], shas["trades_ref"] = _checked(a.trades_new), _checked(a.trades_ref)
        rows.append(trades_identity(a.trades_new, a.trades_ref))
    for r in rows:
        print(f"{r['what']}: holds={r['holds']} starts={r['starts']} rows new/ref={r['rows_new']}/{r['rows_ref']} "
              f"header_equal={r['header_equal']} differing={r['rows_differing']}")
    if not a.no_write:
        import pandas as pd

        from extended import results as RES

        RES.write_result(pd.DataFrame(rows), f"h4_worker_identity{'_' + a.tag if a.tag else ''}", script=SCRIPT,
                         seed=None, require_seed=False, exploratory=False, prereg_id="H4",
                         parameters={"files": {k: str(v) for k, v in (("new", a.new), ("ref", a.ref),
                                                                       ("trades_new", a.trades_new),
                                                                       ("trades_ref", a.trades_ref)) if v},
                                     "sha256": shas, "workers_new": a.workers_new},
                         description="Q-188b: H4-B units at a new worker count against a finished part's rows for "
                                     "the same starts, byte for byte (the trade logs beside).")
    return 0 if all(r["holds"] for r in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
