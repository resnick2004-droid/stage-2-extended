"""The engine pin (D-180, D-184): what code, configuration and cloud engine a result was computed with, written into
its manifest, and refused at the confirmation run if any of it changed without a decision naming the change.

P-04 §3 promises: "the development run's commit is recorded in its manifests, and the confirmation runs at that
commit's engine unless a `DECISIONS.md` entry records a change in the firm's rules between the two." A commit alone
does not enforce that -- nothing compared commits -- so the pin is the sha256 of every file the verdict depends on
(`ENGINE_FILES`), recorded by `engine_pin()` and compared by `check_pin()`. A changed file is allowed only when the
confirmation run cites a `DECISIONS.md` entry whose row names that file.

The kit that ran in QuantConnect is pinned per run by the ingest (its `main.py` hash and `IM2_KIT_VERSION`); the
cloud engine that ran it is not in this repository, so its version string, as the run's own log and results report
it, is recorded at ingest into the run's manifest (D-184), carried into every IM2 result's provenance
(`lean_versions_of`), and compared at the confirmation run (`check_lean`) under the same rule: a new version must be
named by a cited decision.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Sequence

from propedge import REPO_ROOT

#: Every file the IM2 verdict depends on: the campaign engine, the outcome and settlement code, the scorer, the kit
#: generator and its template, the parser and the ingest, the loaders, the rule, fee and instrument tables, the
#: model's configuration, and the pin of the vendored stage-one engine. Adding a file here is itself a change to
#: record (D-184 added the kit generator, template, parser, ingest, releases and loaders; `contract_spec.yaml` is
#: added the day it exists).
ENGINE_FILES: tuple[str, ...] = (
    "propedge/data/qc_algorithms.py",
    "propedge/data/qc_template.py",
    "propedge/data/manual_parsers.py",
    "propedge/data/manual_runs.py",
    "propedge/data/im2_releases.py",
    "propedge/execution/fills.py",
    "propedge/execution/instruments.py",
    "scripts/ingest_manual_run.py",
    "propedge/campaign/lockstep.py",
    "propedge/campaign/reinvest.py",
    "propedge/campaign/gate.py",
    "propedge/campaign/shared_days.py",
    "propedge/campaign/sizing.py",
    "propedge/campaign/risk_policy.py",
    "propedge/campaign/conduct.py",
    "propedge/campaign/payout_method.py",
    "propedge/campaign/protocols.py",
    "propedge/campaign/irr.py",
    "propedge/outcomes/settlement.py",
    "propedge/outcomes/distribution.py",
    "propedge/outcomes/im2_core.py",
    "propedge/contract/adapter.py",
    "propedge/research/im2_score.py",
    "propedge/research/trade_audit.py",
    "propedge/research/fv_score.py",
    "propedge/backtest/metrics.py",
    "scripts/score_im2.py",
    "config/model_im2.yaml",
    "config/rules.yaml",
    "config/fills.yaml",
    "config/instruments.yaml",
    "config/im2_release_calendar.csv",
    "vendor/MANIFEST.sha256",
)


class EnginePinBroken(RuntimeError):
    """A pinned file differs from the development run's and no cited decision names it."""


def _sha256_normalised(path: Path) -> str:
    """sha256 of a text file with line endings normalised, so a checkout's CRLF/LF setting is not a change."""
    text = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(text).hexdigest()


def engine_pin(root: Path | str | None = None, files: Sequence[str] = ENGINE_FILES) -> dict[str, Any]:
    """{'files': {path: sha256}, 'sha256': one hash over all of them, 'git_commit': the tree's state}. A pinned file
    that does not exist raises: a file that vanished is a change, not an omission."""
    from propedge.reporting.results import git_commit

    root = Path(root) if root is not None else REPO_ROOT
    hashes: dict[str, str] = {}
    for rel in files:
        p = root / rel
        if not p.is_file():
            raise FileNotFoundError(f"pinned file missing: {rel}")
        hashes[rel] = _sha256_normalised(p)
    combined = hashlib.sha256("\n".join(f"{k} {v}" for k, v in sorted(hashes.items())).encode()).hexdigest()
    return {"files": hashes, "sha256": combined, "git_commit": git_commit(root)}


_ROW = re.compile(r"^\|\s*(D-\d+)\s*\|")


def decision_rows(text: str) -> dict[str, str]:
    """{D-id: the row's text} for every decision row in a DECISIONS.md text."""
    out = {}
    for line in text.splitlines():
        m = _ROW.match(line)
        if m:
            out[m.group(1)] = line
    return out


def changed_files(recorded: dict[str, Any], current: dict[str, Any]) -> list[str]:
    """The pinned files whose hash differs, plus any pinned on one side only."""
    a, b = recorded.get("files") or {}, current.get("files") or {}
    return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))


def check_pin(recorded: dict[str, Any], current: dict[str, Any], *, decisions_text: str,
              cited: Sequence[str] = ()) -> list[str]:
    """Compare the development run's pin with the current one. Returns the changed files (empty when identical).
    Raises `EnginePinBroken` when a changed file is not named in the text of a cited decision row, or a cited id is
    not a row of DECISIONS.md."""
    rows = decision_rows(decisions_text)
    missing = [d for d in cited if d not in rows]
    if missing:
        raise EnginePinBroken(f"cited decision(s) not in DECISIONS.md: {missing}")
    changed = changed_files(recorded, current)
    uncovered = [f for f in changed if not any(f in rows[d] for d in cited)]
    if uncovered:
        raise EnginePinBroken(
            "the engine changed since the development run and no cited decision names the change (D-180; "
            f"P-04 §3): {uncovered}. Record the change as a DECISIONS.md entry naming each file, then cite it "
            "with --engine-change D-nnn."
        )
    return changed


def lean_versions_of(run_ids: Sequence[str], results_dir: Path | str | None = None) -> dict[str, str | None]:
    """{run id: the LEAN version its ingested manifest records}, None where the run is not ingested or its manifest
    predates D-184; the manual-run result is `results/manual_<run id with underscores>.csv`."""
    from propedge import RESULTS_DIR
    from propedge.reporting.results import manifest_path_for

    import json

    out: dict[str, str | None] = {}
    base = Path(results_dir) if results_dir is not None else RESULTS_DIR
    for rid in run_ids:
        mpath = manifest_path_for(base / f"manual_{rid.replace('-', '_')}.csv")
        if not mpath.is_file():
            out[rid] = None
            continue
        prov = json.loads(mpath.read_text(encoding="utf-8")).get("provenance") or {}
        out[rid] = prov.get("lean_version")
    return out


def check_lean(recorded: dict[str, str | None], current: dict[str, str | None], *, decisions_text: str,
               cited: Sequence[str] = ()) -> list[str]:
    """D-184: the confirmation runs' LEAN versions against the development runs'. Returns the versions new to the
    confirmation (empty when none). Raises `EnginePinBroken` when a run has no recorded version, or a new version is
    not named in the text of a cited decision row."""
    rows = decision_rows(decisions_text)
    missing = [d for d in cited if d not in rows]
    if missing:
        raise EnginePinBroken(f"cited decision(s) not in DECISIONS.md: {missing}")
    unknown = sorted(r for r, v in {**recorded, **current}.items() if not v)
    if unknown:
        raise EnginePinBroken(f"no LEAN version recorded for {unknown}: an ingested run's manifest must carry the "
                              "version the cloud reported (D-184)")
    new = sorted({v for v in current.values()} - {v for v in recorded.values()})
    uncovered = [v for v in new if not any(v in rows[d] for d in cited)]
    if uncovered:
        raise EnginePinBroken(
            f"the confirmation ran on LEAN {uncovered}, not the development runs' "
            f"{sorted({v for v in recorded.values()})}, and no cited decision names the new version (D-184). Record "
            "it as a DECISIONS.md entry naming the version, then cite it with --engine-change D-nnn."
        )
    return new


def fee_dates(fills_path: Path | str | None = None) -> dict[str, str | None]:
    """{instrument: date_read} from config/fills.yaml's round-turn provenance, for a result's provenance block."""
    import yaml

    from propedge import CONFIG_DIR

    doc = yaml.safe_load(Path(fills_path or CONFIG_DIR / "fills.yaml").read_text(encoding="utf-8"))
    prov = (doc.get("round_turn_by_instrument") or {}).get("provenance") or {}
    return {k: str(v.get("date_read")) if v.get("date_read") is not None else None
            for k, v in prov.items() if isinstance(v, dict)}


__all__ = ["ENGINE_FILES", "EnginePinBroken", "engine_pin", "decision_rows", "changed_files", "check_pin",
           "lean_versions_of", "check_lean", "fee_dates"]
