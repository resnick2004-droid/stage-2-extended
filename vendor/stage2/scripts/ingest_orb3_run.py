"""Bring an ORB3 run (R102-R104; T15 item 9, D-256) from QuantConnect's web editor into the repository.

    python scripts/ingest_orb3_run.py R102-orb3-NQ-0914 --backtest-id <id> --run-by "<name>" --rounds 0 \\
        --limit-hit none --files runs/R102-orb3-NQ-0914/downloads/logs.txt runs/R102-orb3-NQ-0914/downloads/results.json

The regime map's steps (`scripts/ingest_regime_run.py`; D-81, D-82, D-131, D-188) for ORB3's parser
(`propedge/data/orb3_parser.py`): the kit is read, a run already ingested is refused, the ran code is hash-checked
against the committed `main.py` -- or attested by the operator (D-131), allowed because the output is checked field by
field against the kit -- the downloads are parsed on the kit's own stop grid (an incomplete output is refused), and the
result is saved through `propedge/data/manual_runs.record_manual_run` with provenance "human-run in QuantConnect web
editor"; then `runs/<run-id>/ingested.json` and `results/manual_run_effort.csv` are written.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

from propedge.data import effort  # noqa: E402
from propedge.data.manual_parsers import UnusableRun  # noqa: E402
from propedge.data.manual_runs import ManualRunRefused, record_manual_run  # noqa: E402
from propedge.data.orb3_parser import orb3_output_matches_kit, parse_orb3  # noqa: E402

RUNS = ROOT / "runs"


def main(argv: list[str] | None = None, *, runs_dir: Path | None = None) -> int:
    from ingest_manual_run import _backtest_name

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("run_id")
    ap.add_argument("--project-id", default=None)
    ap.add_argument("--backtest-id", required=True)
    ap.add_argument("--run-by", required=True)
    ap.add_argument("--date-run", default=date.today().isoformat())
    ap.add_argument("--minutes", type=float, default=None)
    ap.add_argument("--rounds", type=int, required=True)
    ap.add_argument("--limit-hit", required=True)
    ap.add_argument("--files", nargs="+", required=True)
    ap.add_argument("--ran-code-attested", action="store_true")
    a = ap.parse_args(argv)

    kit_dir = (runs_dir or RUNS) / a.run_id
    kit = json.loads((kit_dir / "kit.json").read_text(encoding="utf-8"))
    if kit.get("parser") != "orb3":
        print(f"REFUSED: {a.run_id} is not an ORB3 kit (parser {kit.get('parser')!r}); use "
              "scripts/ingest_manual_run.py.")
        return 2
    if (kit_dir / "ingested.json").exists():
        print(f"REFUSED: {a.run_id} is already ingested; a result stays on record.")
        return 2
    files = {Path(f).name: Path(f) for f in a.files}
    missing = [n for n in kit["downloads"] if n != kit["ran_code"] and n not in files]
    if missing:
        print(f"REFUSED: missing downloaded file(s) {missing}; see {kit_dir / 'RUN.md'}.")
        return 2
    backtest_name = _backtest_name(files.get("results.json"))
    if a.project_id is None and backtest_name is None:
        print("REFUSED: no --project-id and no backtest name in the downloads (results.json) (D-188).")
        return 2
    project = a.project_id or f"{kit['project_name']} (by name; numeric id not noted, D-188)"
    ran_code, attested_by = kit_dir / "downloads" / kit["ran_code"], None
    try:
        if a.ran_code_attested:
            attested_by, ran_code = a.run_by, None
            orb3_output_matches_kit(files["logs.txt"], kit["market"])
        df, facts = parse_orb3(files["logs.txt"], files["results.json"], market=kit["market"],
                               stops=tuple(kit["stops"]))
    except UnusableRun as exc:
        print(f"REFUSED: {exc}")
        return 2
    except ValueError as exc:
        print(f"REFUSED (re-download results.json from this backtest): it cannot be decoded ({exc}).")
        return 2
    try:
        name = "manual_" + a.run_id.replace("-", "_")
        csv, manifest = record_manual_run(
            df, name, algorithm_path=kit["algorithm_file"], ran_code_path=ran_code, project_id=project,
            backtest_id=a.backtest_id, date_run=a.date_run, run_by=a.run_by, downloaded_files=list(files.values()),
            description=f"{kit['title']} ({a.run_id}), run by hand in the web editor.",
            ran_code_attested_by=attested_by,
            provenance={k: v for k, v in (("lean_version", facts.get("lean_version")),
                                          ("qc_project_name", kit["project_name"]),
                                          ("qc_backtest_name", backtest_name)) if v} or None)
    except (ManualRunRefused, FileNotFoundError) as exc:
        print(f"REFUSED: {exc}")
        return 2
    record = {"run_id": a.run_id, "date_run": a.date_run, "run_by": a.run_by, "minutes": a.minutes,
              "rounds": a.rounds, "limit_hit": a.limit_hit, "qc_project_id": str(project),
              "qc_backtest_id": str(a.backtest_id), "qc_project_name": kit["project_name"],
              "qc_backtest_name": backtest_name, "result_file": csv.name,
              "algorithm_sha256_normalised": kit["algorithm_sha256_normalised"],
              "ran_code": "attested by " + attested_by + " (D-131)" if attested_by else "captured and hash-matched",
              "summary": facts}
    (kit_dir / "ingested.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
    effort.write_effort_log()
    print(f"saved {csv.relative_to(ROOT)} with {manifest.name}")
    print(effort.evaluate(effort.load_records(), effort.UpgradeRule.load()).summary())
    print("Commit runs/ and results/ together.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
