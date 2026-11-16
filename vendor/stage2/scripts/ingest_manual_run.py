"""Bring a manual run from QuantConnect's web editor into the repository (D-81, D-82).

    python scripts/ingest_manual_run.py R001-dataset-checks --project-id 12345678 \\
        --backtest-id 0a1b2c... --run-by "Ryan Resnick" --minutes 18 --rounds 0 \\
        --limit-hit none --files runs/R001-dataset-checks/downloads/logs.txt

In order, and it stops at the first refusal:

1. reads the kit (`runs/<run-id>/kit.json`);
2. parses the downloaded files. An incomplete output (no END line, truncated) is refused;
3. checks that `downloads/ran_main.py` -- the code as it stood in the editor -- hashes to the
   **committed** `runs/<run-id>/main.py`, and saves the result through the results writer with
   provenance "human-run in QuantConnect web editor", who ran it and the date
   (`propedge/data/manual_runs.py`). **A hash mismatch is refused**;
4. writes `runs/<run-id>/ingested.json` and regenerates `results/manual_run_effort.csv`;
5. for the dataset checks, records each fact in `config/data_sources.yaml` with method
   `manual_run` and regenerates `docs/DATA_SOURCES.md`;
6. prints the upgrade-rule evaluation (D-82).

A run already ingested is refused: a result stays on record. A rerun after a fix is a new kit.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from propedge.data import effort  # noqa: E402
from propedge.data.manual_parsers import (  # noqa: E402
    UnusableRun, parse_coverage_checks, parse_dataset_checks, parse_gap_evidence, parse_leg_evidence,
    parse_openrev_rescore, parse_reconciliation,
)

#: Parsers whose facts are recorded in config/data_sources.yaml.
FACT_PARSERS = {"dataset_checks": "parse_dataset_checks", "coverage_checks": "parse_coverage_checks",
                "data_extras": "parse_extras", "data_options": "parse_options"}
from propedge.data.manual_runs import ManualRunRefused, record_manual_run  # noqa: E402

RUNS = ROOT / "runs"


def _backtest_name(results_path: Path | None) -> str | None:
    """The name QuantConnect gave the backtest (its downloads carry it), from the results JSON, or None (D-188)."""
    if results_path is None or not Path(results_path).is_file():
        return None
    try:
        doc = json.loads(Path(results_path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    for key in ("algorithmConfiguration", "AlgorithmConfiguration"):
        name = (doc.get(key) or {}).get("name") or (doc.get(key) or {}).get("Name")
        if name:
            return str(name)
    return None


def _record_facts(facts: dict, *, run_id: str, project_id: str, backtest_id: str,
                  result_csv: str, run_by: str, date_run: str, log_name: str,
                  parser_fn: str = "parse_dataset_checks") -> None:
    """Write each fact into config/data_sources.yaml as read by manual_run, then regenerate."""
    import yaml  # noqa: F401  (validation happens in DataSources.load below)

    from propedge.data.sources import DataSources

    path = ROOT / "config" / "data_sources.yaml"
    text = path.read_text(encoding="utf-8")
    ident = f"runs/{run_id} project {project_id} backtest {backtest_id} -> results/{result_csv}"
    for key, value in facts.items():
        start = text.index(f"\n  {key}:\n") + 1
        stop = text.index("    note: null\n", start) + len("    note: null\n")
        block = text[start:stop]
        if "    status: unread\n" not in block:
            raise ManualRunRefused(f"{key} is already read; a fact is not overwritten silently.")
        q = block.split("    question: ", 1)[1].split("\n", 1)[0]
        req = block.split("    requires: ", 1)[1].split("\n", 1)[0]
        v = json.dumps(value) if not isinstance(value, bool) else str(value).lower()
        text = text[:start] + (
            f"  {key}:\n    question: {q}\n    requires: {req}\n    value: {v}\n"
            f"    status: read\n"
            f"    what_read: >\n      The run's summary lines in {log_name}, parsed by "
            f"propedge/data/manual_parsers.py ({parser_fn}).\n"
            f"    method: manual_run\n    identifier: {ident}\n    date_read: {date_run}\n"
            f"    read_by: {run_by} (human-run in QuantConnect web editor), ingested by "
            f"scripts/ingest_manual_run.py\n    note: null\n") + text[stop:]
    path.write_text(text, encoding="utf-8", newline="\n")
    DataSources.load(path)                       # refuses the write if provenance is incomplete
    sys.path.insert(0, str(ROOT / "scripts"))
    import gen_data_sources
    gen_data_sources.main()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("run_id")
    ap.add_argument("--project-id", default=None,
                    help="QuantConnect's numeric project id when noted; otherwise omitted and the run is found by the "
                         "kit's project name and the backtest name its downloads carry (D-188)")
    ap.add_argument("--backtest-id", required=True)
    ap.add_argument("--run-by", required=True)
    ap.add_argument("--date-run", default=date.today().isoformat())
    ap.add_argument("--minutes", type=float, default=None,
                    help="operator minutes; optional since D-110 (recorded as null if omitted)")
    ap.add_argument("--rounds", type=int, required=True)
    ap.add_argument("--limit-hit", required=True, help='the limit message, or "none"')
    ap.add_argument("--files", nargs="+", required=True, help="the downloaded result files")
    ap.add_argument("--ran-code-attested", action="store_true",
                    help="D-131: no ran_main.py; --run-by attests the committed file was pasted unchanged "
                         "(atlas kits only, which get a structural check of their output instead)")
    a = ap.parse_args(argv)

    kit_dir = RUNS / a.run_id
    kit = json.loads((kit_dir / "kit.json").read_text(encoding="utf-8"))
    if (kit_dir / "ingested.json").exists():
        print(f"REFUSED: {a.run_id} is already ingested; a result stays on record.")
        return 2
    files = {Path(f).name: Path(f) for f in a.files}
    missing = [n for n in kit["downloads"] if n != kit["ran_code"] and n not in files]
    if missing:
        print(f"REFUSED: missing downloaded file(s) {missing}; see {kit_dir / 'RUN.md'}.")
        return 2
    # D-188: the run is found in QuantConnect by its project's name (the kit's) and its backtest's name, the name
    # its downloads carry; the numeric project id is recorded when the operator noted it.
    backtest_name = _backtest_name(files.get("results.json"))
    if a.project_id is None and backtest_name is None:
        print("REFUSED: no --project-id and no backtest name in the downloads (results.json); one of them is "
              "needed to find this run in QuantConnect again (D-188).")
        return 2
    project = a.project_id or f"{kit['project_name']} (by name; numeric id not noted, D-188)"
    ran_code = kit_dir / "downloads" / kit["ran_code"]
    attested_by = None
    if a.ran_code_attested:
        if kit["parser"] not in ("atlas", "grid_check", "fv1", "bmap", "im2", "im2x", "release"):
            print("REFUSED: an attested ran code (D-131) is allowed only for kits whose output is checked field by "
                  "field against the committed kit (atlas, FV1, BMAP, IM2 and its second implementation, the release "
                  "kits under D-165) and the R044 grid check (a diagnostic whose per-year lines are checked for their "
                  "fields); supply ran_main.py.")
            return 2
        attested_by = a.run_by
        ran_code = None

    try:
        if attested_by is not None and kit["parser"] == "atlas":
            from propedge.data.manual_parsers import atlas_output_matches_kit
            atlas_output_matches_kit(files["logs.txt"], files["results.json"], kit["market"],
                                     int(kit.get("kit_version", 1)))
        if attested_by is not None and kit["parser"] == "fv1":
            from propedge.data.manual_parsers import fv_output_matches_kit
            fv_output_matches_kit(files["logs.txt"], kit["market"])
        if attested_by is not None and kit["parser"] == "bmap":
            from propedge.data.manual_parsers import bmap_output_matches_kit
            bmap_output_matches_kit(files["logs.txt"], kit["market"])
        if attested_by is not None and kit["parser"] == "im2":
            from propedge.data.manual_parsers import im2_output_matches_kit
            im2_output_matches_kit(files["logs.txt"], kit["market"])
        if attested_by is not None and kit["parser"] == "im2x":
            from propedge.data.manual_parsers import im2x_output_matches_kit
            im2x_output_matches_kit(files["logs.txt"], kit["market"])
        if attested_by is not None and kit["parser"] == "grid_check":
            from propedge.data.manual_parsers import grid_output_matches_kit
            grid_output_matches_kit(files["logs.txt"])
        if attested_by is not None and kit["parser"] == "release":
            from propedge.data.manual_parsers import release_output_matches_kit
            release_output_matches_kit(files["logs.txt"], files["results.json"], kit["market"],
                                       int(kit["events_scheduled"]))
        if kit["parser"] == "dataset_checks":
            df, facts = parse_dataset_checks(files["logs.txt"])
        elif kit["parser"] == "coverage_checks":
            df, facts = parse_coverage_checks(files["logs.txt"])
        elif kit["parser"] == "data_extras":
            from propedge.data.manual_parsers import parse_extras
            df, facts = parse_extras(files["logs.txt"])
        elif kit["parser"] == "data_options":
            from propedge.data.manual_parsers import parse_options
            df, facts = parse_options(files["logs.txt"])
        elif kit["parser"] == "reconciliation":
            df, facts = parse_reconciliation(files["logs.txt"], files["results.json"])
        elif kit["parser"] == "leg_evidence":
            df, facts = parse_leg_evidence(files["logs.txt"], files["results.json"])
        elif kit["parser"] == "gap_evidence":
            df, facts = parse_gap_evidence(files["logs.txt"], files["results.json"])
        elif kit["parser"] == "openrev_rescore":
            df, facts = parse_openrev_rescore(files["logs.txt"], files["results.json"])
        elif kit["parser"] == "atlas":
            from propedge.data.manual_parsers import parse_atlas
            df, facts = parse_atlas(files["logs.txt"], files["results.json"])
        elif kit["parser"] == "release":
            from propedge.data.manual_parsers import parse_release
            df, facts = parse_release(files["logs.txt"], files["results.json"])
        elif kit["parser"] == "fv1":
            from propedge.data.manual_parsers import parse_fv
            df, facts = parse_fv(files["logs.txt"], files["results.json"])
        elif kit["parser"] == "bmap":
            from propedge.data.manual_parsers import parse_bmap
            df, facts = parse_bmap(files["logs.txt"], files["results.json"])
        elif kit["parser"] == "im2":
            from propedge.data.manual_parsers import parse_im2
            df, facts = parse_im2(files["logs.txt"], files["results.json"])
        elif kit["parser"] == "im2x":
            from propedge.data.manual_parsers import parse_im2x
            df, facts = parse_im2x(files["logs.txt"], files["results.json"])
        elif kit["parser"] == "grid_check":
            from propedge.data.manual_parsers import parse_grid_check
            df, facts = parse_grid_check(files["logs.txt"])
        elif kit["parser"] == "gamma_diagnostic":
            from propedge.data.manual_parsers import parse_gamma_diagnostic
            df, facts = parse_gamma_diagnostic(files["logs.txt"])
        elif kit["parser"] == "atlas_context":
            from propedge.data.manual_parsers import parse_context
            df, facts = parse_context(files["logs.txt"], files["results.json"])
        elif kit["parser"] == "openrev_nq":
            from propedge.data.qc_algorithms import OPENREV_PREFIX_NQ
            df, facts = parse_openrev_rescore(files["logs.txt"], files["results.json"], prefix=OPENREV_PREFIX_NQ)
        else:
            raise SystemExit(f"unknown parser {kit['parser']!r}")
        name = "manual_" + a.run_id.replace("-", "_")
        csv, manifest = record_manual_run(
            df, name,
            algorithm_path=kit["algorithm_file"], ran_code_path=ran_code,
            project_id=project, backtest_id=a.backtest_id,
            date_run=a.date_run, run_by=a.run_by,
            downloaded_files=list(files.values()),
            description=f"{kit['title']} ({a.run_id}), run by hand in the web editor.",
            ran_code_attested_by=attested_by,
            # D-184: the cloud engine that ran the kit; D-188: the project's and the backtest's names in QuantConnect
            provenance={k: v for k, v in (("lean_version", facts.get("lean_version")),
                                          ("qc_project_name", kit["project_name"]),
                                          ("qc_backtest_name", backtest_name)) if v} or None,
        )
    except (UnusableRun, ManualRunRefused, FileNotFoundError) as exc:
        print(f"REFUSED: {exc}")
        return 2

    record = {
        "run_id": a.run_id, "date_run": a.date_run, "run_by": a.run_by,
        "minutes": a.minutes, "rounds": a.rounds, "limit_hit": a.limit_hit,
        "qc_project_id": str(project), "qc_backtest_id": str(a.backtest_id),
        "qc_project_name": kit["project_name"], "qc_backtest_name": backtest_name,
        "result_file": csv.name, "algorithm_sha256_normalised": kit["algorithm_sha256_normalised"],
        "ran_code": "attested by " + attested_by + " (D-131)" if attested_by else "captured and hash-matched",
        "summary": None if kit["parser"] in FACT_PARSERS else facts,
    }
    (kit_dir / "ingested.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8",
                                           newline="\n")
    effort.write_effort_log()
    print(f"saved {csv.relative_to(ROOT)} with {manifest.name}")

    if kit["parser"] in FACT_PARSERS:
        _record_facts(facts, run_id=a.run_id, project_id=project, backtest_id=a.backtest_id,
                      result_csv=csv.name, run_by=a.run_by, date_run=a.date_run,
                      log_name="logs.txt", parser_fn=FACT_PARSERS[kit["parser"]])

    verdict = effort.evaluate(effort.load_records(), effort.UpgradeRule.load())
    print(verdict.summary())
    print("Commit runs/, results/, config/ and docs/ together.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
