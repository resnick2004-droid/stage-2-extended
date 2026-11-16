"""Provenance for a QuantConnect cloud run, and the reconciliation gate that precedes it.

A cloud backtest happens somewhere this repository cannot see. The only thing that makes its
output a *result* rather than a screenshot is the record attached to it: which code ran, over
which dates, on which dataset, at which resolution, under which cost model. This module builds
that record and refuses to let a measurement run before the fill model has been reconciled.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
#: Where a passed reconciliation is recorded. Written only by the reconciliation run.
RECONCILIATION_RECORD = ROOT / "results" / "reconciliation_status.json"


class ReconciliationNotPassed(RuntimeError):
    """Raised when a measurement is attempted before reconciliation passes on this config."""


@dataclass(frozen=True)
class CloudRunProvenance:
    """Everything needed to reproduce a cloud run, or to know that you cannot."""

    project_id: int | str
    backtest_id: int | str
    code_sha256: str
    start_date: str
    end_date: str
    dataset: str
    resolution: str
    parameters: dict = field(default_factory=dict)
    lean_version: str | None = None
    launched_from: str | None = None          # the committed script that launched it

    def as_manifest_fields(self) -> dict:
        d = asdict(self)
        d["provenance_note"] = (
            "Launched from a script committed in this repository. Nothing was read off the "
            "QuantConnect interface: a number whose provenance is 'I saw it on the site' has no "
            "manifest and cannot be traced."
        )
        return d


def hash_code(code: str) -> str:
    """sha256 of the algorithm exactly as uploaded."""
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def config_fingerprint(fill_profile: dict) -> str:
    """A stable hash of the cost model a reconciliation was established against.

    Reconciliation proves that QuantConnect's fills and ours agree *under a particular cost
    model*. Change the model and that proof no longer applies, so the fingerprint is part of the
    pass record and a mismatch invalidates it.
    """
    blob = json.dumps(fill_profile, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def record_reconciliation(fingerprint: str, *, stages_passed: list[str], note: str = "") -> None:
    """Write the pass record. Called only by the reconciliation run, never by a measurement."""
    RECONCILIATION_RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECONCILIATION_RECORD.write_text(
        json.dumps(
            {
                "config_fingerprint": fingerprint,
                "stages_passed": stages_passed,
                "recorded": date.today().isoformat(),
                "note": note,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def assert_reconciled(fingerprint: str, *, what: str = "measurement") -> None:
    """Raise unless reconciliation has passed on exactly this cost model.

    `docs/PIPELINE.md` §5 requires three stages, the third a **negative control that must fail**
    against LEAN's defaults. A reconciliation with no failing negative control has not been shown
    to work, so all three stage names must be present.
    """
    required = {"A_zero_cost_exact", "B_costs_on", "C_negative_control_failed"}
    if not RECONCILIATION_RECORD.exists():
        raise ReconciliationNotPassed(
            f"{what}: reconciliation has not been run. docs/PIPELINE.md section 5 must pass "
            f"BEFORE any measurement -- until it does, an exported log is unvalidated data "
            f"whatever its schema says."
        )
    rec = json.loads(RECONCILIATION_RECORD.read_text(encoding="utf-8"))
    missing = required - set(rec.get("stages_passed", []))
    if missing:
        raise ReconciliationNotPassed(
            f"{what}: reconciliation is incomplete -- missing {sorted(missing)}. Stage C is the "
            f"negative control that MUST FAIL against LEAN's defaults; a reconciliation that has "
            f"never failed has not been shown to work."
        )
    if rec.get("config_fingerprint") != fingerprint:
        raise ReconciliationNotPassed(
            f"{what}: reconciliation passed against a DIFFERENT cost model "
            f"({rec.get('config_fingerprint', '')[:12]}... vs {fingerprint[:12]}...). Changing "
            f"the fill, fee or slippage settings invalidates the proof that our fills and "
            f"QuantConnect's agree. Re-run reconciliation."
        )
