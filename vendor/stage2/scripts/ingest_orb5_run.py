"""Bring an ORB5 capture run (R105-R107; T16 item 3, D-264) from QuantConnect's web editor into the repository.

    python scripts/ingest_orb5_run.py R105-orb5-NQ-0914 --backtest-id <id> --run-by "<name>" --rounds 0 \\
        --limit-hit none --files runs/R105-orb5-NQ-0914/downloads/logs.txt runs/R105-orb5-NQ-0914/downloads/results.json

The regime map's steps (`scripts/ingest_regime_run.py`; D-81, D-82, D-131, D-188) for ORB5's parser
(`propedge/data/orb5_parser.py`): the kit is read, a run already ingested is refused, the ran code is hash-checked
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
from propedge.data.orb5_parser import orb5_output_matches_kit, parse_orb5  # noqa: E402

RUNS = ROOT / "runs"


JOIN_KEYS = ("dir", "fill_slot", "at_open", "close_ticks", "atr_ticks")
HEAD_KEYS = ("days", "entries", "early", "noatr")
MAX_MISMATCH = 0.005                    # D-265: more than 0.5 % of rows disagreeing with ORB3's is a misaligned run
#: D-266: where the hand-traded entry is the original fill, its stop, 1.5R and 2R passages are ORB3's
SAME_KEYS = (("lat_a_{i}", "a_{i}"), ("lat_f15_{i}", "f15_{i}"), ("lat_f2_{i}", "f2_{i}"))


def join_check(df, facts: dict, orb3_run: str, runs_dir: Path, results_dir: Path | None) -> tuple[dict, str | None]:
    """D-265: the capture against the ORB3 run whose days it re-walks -- HEAD's day counts equal, and each day and
    range's direction, fill bar, at-open flag, 15:08 close and ATR equal; D-266: where the hand-traded entry is the
    original fill, its stop, 1.5R and 2R passages equal ORB3's. (join facts, a refusal or None)."""
    import pandas as pd

    from propedge import RESULTS_DIR

    rec = runs_dir / orb3_run / "ingested.json"
    src = (Path(results_dir) if results_dir is not None else RESULTS_DIR) / f"manual_{orb3_run.replace('-', '_')}.csv"
    if not rec.is_file() or not src.is_file():
        return {}, f"{orb3_run} is not ingested (its run record or result file is missing): nothing to join to."
    theirs = json.loads(rec.read_text(encoding="utf-8"))["summary"]
    off = {k: (facts.get(k), theirs.get(k)) for k in HEAD_KEYS if int(facts.get(k, -1)) != int(theirs.get(k, -2))}
    if off:
        return {}, f"HEAD's day counts differ from {orb3_run}'s: {off} -- the run does not re-walk the same days."
    raw = pd.read_csv(src, low_memory=False)
    raw = raw[raw["kind"] == "day"].astype({"or_minutes": int}).set_index(["date", "or_minutes"])
    o3 = raw[list(JOIN_KEYS)]
    days5 = df[df["kind"] == "day"].astype({"or_minutes": int}).set_index(["date", "or_minutes"])
    o5 = days5[list(JOIN_KEYS)]
    both = o5.join(o3, how="outer", lsuffix="_5", rsuffix="_3")
    bad = pd.Series(False, index=both.index)
    for k in JOIN_KEYS:
        bad |= ~(both[f"{k}_5"] == both[f"{k}_3"])
    pairs = [(a.format(i=i), b.format(i=i)) for a, b in SAME_KEYS for i in range(len(stops_of(df)))]
    have = [(a, b) for a, b in pairs if a in days5.columns and b in raw.columns]
    if have:
        same = days5[days5["lat_kind"] == 0]
        ref = raw.reindex(same.index)
        off = pd.Series(False, index=same.index)
        for a, b in have:
            off |= ~(same[a] == ref[b])
        bad = bad | off.reindex(both.index, fill_value=False)
    n_bad = int(bad.sum())
    join = {"rows": int(len(both)), "mismatched": n_bad, "same_entry_checked": [b for _, b in have][:3],
            "mismatched_keys": [f"{d}/{m}" for d, m in both.index[bad][:50]], "against": orb3_run}
    if n_bad > MAX_MISMATCH * len(both):
        return join, (f"{n_bad} of {len(both)} day-and-range rows disagree with {orb3_run}'s on {JOIN_KEYS} or, where "
                      f"the hand-traded entry is the original, its passages -- more than {MAX_MISMATCH:.1%}: the capture "
                      "does not describe ORB3's trades.")
    return join, None


def stops_of(df) -> list[int]:
    """The stop widths' indices in the capture's columns (`lat_a_<i>`)."""
    return sorted(int(c.rsplit("_", 1)[1]) for c in df.columns if c.startswith("lat_a_"))


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
    if kit.get("parser") != "orb5":
        print(f"REFUSED: {a.run_id} is not an ORB5 kit (parser {kit.get('parser')!r}); use "
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
            orb5_output_matches_kit(files["logs.txt"], kit["market"])
        df, facts = parse_orb5(files["logs.txt"], files["results.json"], market=kit["market"],
                               stops=tuple(kit["stops"]))
    except UnusableRun as exc:
        print(f"REFUSED: {exc}")
        return 2
    except ValueError as exc:
        print(f"REFUSED (re-download results.json from this backtest): it cannot be decoded ({exc}).")
        return 2
    join, problem = join_check(df, facts, kit["joins"], runs_dir or RUNS, results_dir)
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
