"""Bring a regime-map run (R090-R094; T15, D-238) from QuantConnect's web editor into the repository.

    python scripts/ingest_regime_run.py R090-regime-NQ --backtest-id <id> --run-by "<name>" --rounds 0 \\
        --limit-hit none --files runs/R090-regime-NQ/downloads/logs.txt runs/R090-regime-NQ/downloads/results.json

The resolution map's steps (`scripts/ingest_rmap_run.py`; D-81, D-82, D-131, D-188) for the regime map's parser
(`propedge/data/regime_parser.py`): the kit is read, a run already ingested is refused, the ran code is hash-checked
against the committed `main.py` -- or attested by the operator (D-131), allowed because the output is checked field by
field against the kit -- the downloads are parsed (an incomplete output is refused), and the result is saved through
`propedge/data/manual_runs.record_manual_run` with provenance "human-run in QuantConnect web editor"; then
`runs/<run-id>/ingested.json` and `results/manual_run_effort.csv` are written.

NQB2's confirmation kit (D-242) is ingested as NQB1's was (D-229 to D-232): its log is judged usable before any count is
parsed -- an unusable run is recorded in `unusable.json` and never parsed or ingested afterwards; a parser refusal makes
it unusable too; a refusal of the procedure (files, downloads, ran code) is retried on the same backtest's files; a
`results.json` that cannot be decoded is re-downloaded once, then recorded unusable with `--declare-unreadable`.
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
from propedge.data.regime_parser import kit_grid, parse_regime, regime_output_matches_kit  # noqa: E402

RUNS = ROOT / "runs"


def _unusable(kit_dir: Path, a, backtest_name, prereg, why: list[str], what: str) -> None:
    """D-230: record an unusable confirmation run; its counts are not used."""
    record = {"run_id": a.run_id, "date_run": a.date_run, "run_by": a.run_by, "qc_backtest_id": str(a.backtest_id),
              "qc_backtest_name": backtest_name, "prereg": prereg,
              "status": f"unusable: not ingested; {what} (D-230)", "why": why,
              "downloads": f"runs/{a.run_id}/downloads/ (gitignored, kept locally)"}
    (kit_dir / "unusable.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")


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
    ap.add_argument("--declare-unreadable", action="store_true",
                    help="D-232: a confirmation run whose results.json from the same backtest still cannot be decoded "
                         "after one re-download is recorded unusable")
    a = ap.parse_args(argv)

    kit_dir = (runs_dir or RUNS) / a.run_id
    kit = json.loads((kit_dir / "kit.json").read_text(encoding="utf-8"))
    if kit.get("parser") != "regime":
        print(f"REFUSED: {a.run_id} is not a regime-map kit (parser {kit.get('parser')!r}); use "
              "scripts/ingest_manual_run.py.")
        return 2
    if (kit_dir / "ingested.json").exists():
        print(f"REFUSED: {a.run_id} is already ingested; a result stays on record.")
        return 2
    if (kit_dir / "unusable.json").exists():                 # D-232: an unusable run is never ingested afterwards
        print(f"REFUSED: {a.run_id} is recorded unusable; it is never ingested, whatever files are given (D-232).")
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
    prereg = kit.get("prereg") if kit.get("confirm") else None
    if kit.get("confirm"):                                    # D-242, as D-230: usable before any count is parsed
        from propedge.data.regime_kit import confirm_config
        from propedge.data.regime_parser import regime_usability

        why = regime_usability(files["logs.txt"], int(confirm_config()["min_days"]), a.limit_hit)
        if why:
            _unusable(kit_dir, a, backtest_name, prereg, why, "its counts were never parsed")
            print(f"REFUSED (D-230): {a.run_id} is unusable -- " + "; ".join(why) + ". Recorded in unusable.json; "
                  "no count was parsed.")
            return 2
    try:
        if a.ran_code_attested:
            attested_by, ran_code = a.run_by, None
            regime_output_matches_kit(files["logs.txt"], kit["market"])
    except UnusableRun as exc:
        print(f"REFUSED (procedure, retry on this backtest's own files): {exc}")
        return 2
    try:
        if kit.get("confirm"):
            from propedge.data.regime_kit import confirm_config, confirm_params
            from propedge.data.regime_parser import parse_regime_confirm

            df, facts = parse_regime_confirm(files["logs.txt"], files["results.json"], confirm_params(),
                                             list(confirm_config()["months"]))
        else:
            df, facts = parse_regime(files["logs.txt"], files["results.json"], market=kit["market"], q=kit_grid(kit))
    except UnusableRun as exc:                                # the output's integrity (D-231)
        if kit.get("confirm"):
            _unusable(kit_dir, a, backtest_name, prereg, [f"the output's integrity: {exc}"],
                      "the parser refused its output; no count was used")
            print(f"REFUSED (D-230): {a.run_id} is unusable -- the parser refused its output: {exc}. Recorded in "
                  "unusable.json.")
            return 2
        print(f"REFUSED: {exc}")
        return 2
    except ValueError as exc:                                 # D-232: a results.json that cannot be decoded
        if kit.get("confirm") and a.declare_unreadable:
            _unusable(kit_dir, a, backtest_name, prereg, ["results.json cannot be decoded after a re-download"],
                      "its results could not be decoded; no count was used")
            print(f"REFUSED (D-232): {a.run_id} is unusable -- its results cannot be decoded. Recorded.")
            return 2
        print(f"REFUSED (procedure, re-download results.json from this backtest): it cannot be decoded ({exc}).")
        return 2
    try:
        name = "manual_" + a.run_id.replace("-", "_")
        csv, manifest = record_manual_run(
            df, name, algorithm_path=kit["algorithm_file"], ran_code_path=ran_code, project_id=project,
            backtest_id=a.backtest_id, date_run=a.date_run, run_by=a.run_by, downloaded_files=list(files.values()),
            description=f"{kit['title']} ({a.run_id}), run by hand in the web editor.",
            ran_code_attested_by=attested_by, prereg_id=prereg,
            provenance={k: v for k, v in (("lean_version", facts.get("lean_version")),
                                          ("qc_project_name", kit["project_name"]),
                                          ("qc_backtest_name", backtest_name)) if v} or None)
    except (ManualRunRefused, FileNotFoundError) as exc:
        print(f"REFUSED (procedure, retry on this backtest's own files): {exc}")
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
