"""R11: a completed registration's computation rerun to show the engine still computes it exactly -- never a verdict.

`scripts/reproduce_registered.py` reruns a completed registration's own code path (P-06, P-09, P-10, P-11) after the
engine's changes (D-465, D-467, D-470, D-478) and compares the files with the registered ones: NEXT_STEPS R11's
acceptance. The registered scripts take a `reproduce` keyword whose only effects are its variant-ledger append skipped
(a reproduction is not a configuration tried) and its files written through `writer` below:

* into a directory outside the repository (never `results/`, so the tree and the registered files are untouched);
* `exploratory: true`, no registration id, no variant count;
* the note "reproduction of P-xx, not a verdict (R11)" as the manifest's status, the registered status kept beside it.

What the run computes -- every row, every column, every path -- is the registered code's, and the scripts' default path
(no `reproduce`) makes exactly the calls it made before. The registration check (`PreregRegistry.require_runnable`)
stays in each script's `main`, which a reproduction does not call: a completed registration is never rerun as itself.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from propedge import REPO_ROOT


class ReproductionDirError(ValueError):
    """Raised when a reproduction would write inside the repository."""


def note(pid: str) -> str:
    """The label every reproduced file carries."""
    return f"reproduction of {pid}, not a verdict (R11)"


def check_out_dir(out_dir: Path | str | None) -> Path:
    """The reproduction's output directory, resolved; refused when missing or inside the repository."""
    if out_dir is None:
        raise ReproductionDirError("a reproduction names its output directory (outside the repository)")
    out = Path(out_dir).resolve()
    repo = Path(REPO_ROOT).resolve()
    if out == repo or repo in out.parents:
        raise ReproductionDirError(f"{out} is inside the repository ({repo}); a reproduction writes outside it, never "
                                   "into results/")
    return out


def writer(pid: str, out_dir: Path | str | None) -> Callable[..., Any]:
    """`write_result` for a reproduction of `pid`: the same call, written into `out_dir`, exploratory, no registration
    id or variant count, the status note replaced by `note(pid)` (the registered one kept as `registered_status`)."""
    from propedge.reporting.results import write_result

    out = check_out_dir(out_dir)

    def write(df, name: str, **kw: Any):
        notes = dict(kw.get("notes") or {})
        status = notes.pop("status", None)
        kw.update(results_dir=out, exploratory=True, prereg_id=None, variant_count=None,
                  notes={"status": note(pid), "reproduces": pid,
                         **({"registered_status": status} if status is not None else {}), **notes},
                  description=f"Reproduction of {pid} (R11), not a verdict. " + str(kw.get("description") or ""))
        return write_result(df, name, **kw)

    return write


__all__ = ["ReproductionDirError", "check_out_dir", "note", "writer"]
