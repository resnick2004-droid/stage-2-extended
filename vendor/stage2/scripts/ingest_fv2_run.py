"""Bring an FV2 capture run (R111-R116; T16 item 11, D-283) from QuantConnect's web editor into the repository.

    python scripts/ingest_fv2_run.py R111-fv2-NQ-0911 --backtest-id <id> --run-by "<name>" --rounds 0 \\
        --limit-hit none --files runs/R111-fv2-NQ-0911/downloads/logs.txt runs/R111-fv2-NQ-0911/downloads/results.json

ORB6's ingest (`scripts/ingest_orb6_run.py`) for FV2's parser (`propedge/data/fv2_parser.py`): the kit is read, a run
already ingested is refused, the ran code is hash-checked against the committed `main.py` -- or attested by the
operator (D-131) -- the downloads are parsed (an incomplete output is refused), the capture is joined to the ORB3 run
whose days it re-walks over its own dates, and the result is saved through `propedge/data/manual_runs.record_manual_run`
with provenance "human-run in QuantConnect web editor"; then `runs/<run-id>/ingested.json` and
`results/manual_run_effort.csv` are written.
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
from propedge.data.fv2_parser import fv2_output_matches_kit, parse_fv2  # noqa: E402

RUNS = ROOT / "runs"
MAX_MISMATCH = 0.005                    # D-265: more than 0.5 % of days disagreeing is a misaligned run


def join_check(df, orb3_run: str, window: tuple[str, str], runs_dir: Path,
               results_dir: Path | None) -> tuple[dict, str | None]:
    """D-265 for FV2: over the run's own dates, the days recorded are ORB3's (its 5-minute range's day rows) and each
    day's ATR equals ORB3's. (join facts, a refusal or None)."""
    import pandas as pd

    from propedge import RESULTS_DIR

    res = Path(results_dir) if results_dir is not None else RESULTS_DIR
    rec, src = runs_dir / orb3_run / "ingested.json", res / f"manual_{orb3_run.replace('-', '_')}.csv"
    if not rec.is_file() or not src.is_file():
        return {}, f"{orb3_run} is not ingested (its run record or result file is missing): nothing to join to."
    raw = pd.read_csv(src, low_memory=False, usecols=["kind", "date", "or_minutes", "atr_ticks"])
    o3 = raw[(raw["kind"] == "day") & (raw["or_minutes"].astype(float) == 5)]
    o3 = o3[(o3["date"] >= window[0]) & (o3["date"] <= window[1])].set_index("date")["atr_ticks"]
    mine = df[df["kind"] == "day"].set_index("date")["atr_ticks"]
    both = pd.concat([mine.rename("fv2"), o3.rename("orb3")], axis=1)
    bad = ~(both["fv2"] == both["orb3"])
    n_bad = int(bad.sum())
    join = {"days": int(len(both)), "mismatched": n_bad, "mismatched_dates": list(both.index[bad][:50]),
            "against": orb3_run, "window": list(window)}
    if n_bad > MAX_MISMATCH * len(both):
        return join, (f"{n_bad} of {len(both)} days disagree with {orb3_run}'s over {window} on the day set or the ATR "
                      f"-- more than {MAX_MISMATCH:.1%}: the capture does not describe the same days.")
    return join, None


def main(argv: list[str] | None = None, *, runs_dir: Path | None = None, results_dir: Path | None = None) -> int:
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
    if kit.get("parser") != "fv2":
        print(f"REFUSED: {a.run_id} is not an FV2 kit (parser {kit.get('parser')!r}); use "
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
            fv2_output_matches_kit(files["logs.txt"], kit["market"])
        df, facts = parse_fv2(files["logs.txt"], files["results.json"], market=kit["market"])
    except UnusableRun as exc:
        print(f"REFUSED: {exc}")
        return 2
    except ValueError as exc:
        print(f"REFUSED (re-download results.json from this backtest): it cannot be decoded ({exc}).")
        return 2
    join, problem = join_check(df, kit["joins"], tuple(kit["window"]), runs_dir or RUNS, results_dir)
    if problem:
        print(f"REFUSED: {problem}")
        return 2
    facts = {**facts, "join": join}
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
