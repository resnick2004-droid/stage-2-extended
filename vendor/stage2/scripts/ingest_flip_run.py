"""Bring the flip map's run (R137-flipmap-NQ; D-343; R138, D-344) or the flip-direction atlases' (R142-flipdir-NQ,
D-371; R143-flipany-NQ, D-373; R144-flipdesign-NQ, D-375) or the collect map's (R145-collect-NQ, D-381) from
QuantConnect's web editor into the repository.

    python scripts/ingest_flip_run.py R137-flipmap-NQ --backtest-id <id> --run-by "<name>" --rounds 0 \\
        --limit-hit none --files runs/R137-flipmap-NQ/downloads/logs.txt runs/R137-flipmap-NQ/downloads/results.json

The same steps as `scripts/ingest_rmap_run.py` (D-81, D-82, D-131, D-188) for the flip map's parser
(`propedge/data/flip_parser.py`): the kit is read, a run already ingested is refused, the downloads are parsed (an
incomplete output is refused), the ran code is hash-checked against the committed `main.py` -- or attested by the
operator (D-131), allowed because the output is checked field by field against the kit -- and the result is saved
through `propedge/data/manual_runs.record_manual_run` with provenance "human-run in QuantConnect web editor"; then
`runs/<run-id>/ingested.json` and `results/manual_run_effort.csv` are written.
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
from propedge.data.flip_parser import (flip_output_matches_kit, parse_collect, parse_dst, parse_flip,  # noqa: E402
                                        parse_flipany, parse_flipdesign, parse_flipdir)
from propedge.data.manual_parsers import UnusableRun  # noqa: E402
from propedge.data.manual_runs import ManualRunRefused, record_manual_run  # noqa: E402

RUNS = ROOT / "runs"


def kit_prereg(kit: dict) -> str | None:
    """D-449: a confirmation kit's registration (T24's P-10), which the recorder checks against the id embedded in the
    algorithm and against prereg/REGISTRY.md; a development kit has none."""
    return str(kit["prereg"]) if kit.get("confirm") else None


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
    if kit.get("parser") not in ("flipmap", "flipdir", "flipany", "flipdesign", "collect", "dst", "t23"):
        print(f"REFUSED: {a.run_id} is not a flip-map kit (parser {kit.get('parser')!r}).")
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
    from propedge.data import flip_kit as fk

    # D-344: the kit's own parameters; D-371: the direction atlas's, with its per-day parser
    if kit.get("parser") == "flipdir":
        q, parse = fk.params_direction(), parse_flipdir
    elif kit.get("parser") == "flipany":                                          # D-373
        q, parse = fk.params_anytime(), parse_flipany
    elif kit.get("parser") == "flipdesign":                                       # D-375
        q, parse = fk.params_design(), parse_flipdesign
    elif kit.get("parser") == "collect":                                          # D-381
        q, parse = fk.params_collect(), parse_collect
    elif kit.get("parser") == "dst":                                              # D-386 (7)
        q, parse = fk.params_dst(), parse_dst
    elif kit.get("parser") == "t23":                                              # D-416
        from propedge.data import t23_kit as tk
        from propedge.data.t23_parser import parse_t23

        q, parse = tk.params_t23(a.run_id), parse_t23
    else:
        q, parse = (fk.params_seconds() if kit.get("variant") == "seconds" else fk.params()), parse_flip
    try:
        if a.ran_code_attested:
            attested_by, ran_code = a.run_by, None
            flip_output_matches_kit(files["logs.txt"], kit["market"], q)
        df, facts = parse(files["logs.txt"], files["results.json"], q)
    except UnusableRun as exc:
        print(f"REFUSED: {exc}")
        return 2
    except ValueError as exc:
        print(f"REFUSED (procedure, re-download results.json from this backtest): it cannot be decoded ({exc}).")
        return 2
    try:
        name = "manual_" + a.run_id.replace("-", "_")
        csv, manifest = record_manual_run(
            df, name, algorithm_path=kit["algorithm_file"], ran_code_path=ran_code, project_id=project,
            backtest_id=a.backtest_id, date_run=a.date_run, run_by=a.run_by, downloaded_files=list(files.values()),
            description=f"{kit['title']} ({a.run_id}), run by hand in the web editor.",
            ran_code_attested_by=attested_by, prereg_id=kit_prereg(kit),
            provenance={k: v for k, v in (("lean_version", facts.get("lean_version")),
                                          ("qc_project_name", kit["project_name"]),
                                          ("qc_backtest_name", backtest_name)) if v} or None)
    except (ManualRunRefused, FileNotFoundError) as exc:
        print(f"REFUSED (procedure, retry on this backtest's own files): {exc}")
        return 2
    record = {"run_id": a.run_id, "date_run": a.date_run, "run_by": a.run_by, "minutes": a.minutes,
              "rounds": a.rounds, "limit_hit": a.limit_hit, "qc_project_id": str(project),
              "qc_backtest_id": str(a.backtest_id), "qc_project_name": kit["project_name"],
              "qc_backtest_name": backtest_name, "prereg": kit_prereg(kit), "result_file": csv.name,
              "algorithm_sha256_normalised": kit["algorithm_sha256_normalised"],
              "ran_code": "attested by " + attested_by + " (D-131)" if attested_by else "captured and hash-matched",
              "summary": facts}
    (kit_dir / "ingested.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
    effort.write_effort_log()
    print(f"saved {csv.relative_to(ROOT)} with {manifest.name} ({len(df)} rows; days {facts['days']}, entries "
          f"{facts['entries']}, early {facts['early']}, lost {facts['lost']}, late {facts['late']})")
    print(effort.evaluate(effort.load_records(), effort.UpgradeRule.load()).summary())
    print("Commit runs/ and results/ together.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
