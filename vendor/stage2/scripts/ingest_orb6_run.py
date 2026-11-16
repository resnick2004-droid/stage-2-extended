"""Bring an ORB6 capture run (R108-R110; T16 item 9, D-278) from QuantConnect's web editor into the repository.

    python scripts/ingest_orb6_run.py R108-orb6-NQ-0914 --backtest-id <id> --run-by "<name>" --rounds 0 \\
        --limit-hit none --files runs/R108-orb6-NQ-0914/downloads/logs.txt runs/R108-orb6-NQ-0914/downloads/results.json

ORB5's ingest (`scripts/ingest_orb5_run.py`) for ORB6's parser (`propedge/data/orb6_parser.py`): the kit is read, a run
already ingested is refused, the ran code is hash-checked against the committed `main.py` -- or attested by the
operator (D-131) -- the downloads are parsed on the kit's own stop grid (an incomplete output is refused), the capture
is joined to the ORB3 run whose days it re-walks and to ORB5's capture of the same days, and the result is saved through
`propedge/data/manual_runs.record_manual_run` with provenance "human-run in QuantConnect web editor"; then
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
from propedge.data.manual_parsers import UnusableRun  # noqa: E402
from propedge.data.manual_runs import ManualRunRefused, record_manual_run  # noqa: E402
from propedge.data.orb6_parser import orb6_output_matches_kit, parse_orb6  # noqa: E402

RUNS = ROOT / "runs"


JOIN_KEYS = ("dir", "fill_slot", "atr_ticks")          # what ORB6's record shares with ORB3's
HEAD_KEYS = ("days", "entries", "early", "noatr")
MAX_MISMATCH = 0.005                    # D-265: more than 0.5 % of rows disagreeing is a misaligned run


def _days(path: Path):
    import pandas as pd

    raw = pd.read_csv(path, low_memory=False)
    return raw[raw["kind"] == "day"].astype({"or_minutes": int}).set_index(["date", "or_minutes"])


def join_check(df, facts: dict, orb3_run: str, orb5_run: str, runs_dir: Path,
               results_dir: Path | None) -> tuple[dict, str | None]:
    """D-265 for ORB6: HEAD's day counts equal the ORB3 run's, each day and range's direction, fill bar and ATR equal
    ORB3's, and against ORB5's capture of the same days the hand-traded entry is there in both or in neither, its range
    stop's distance follows from ORB5's fill, and its range walk's passages are no earlier than its bar (its own bar
    only when it fills at the open) and no later than 15:08. (join facts, a refusal or None)."""
    import pandas as pd

    from propedge import RESULTS_DIR
    from propedge.data import orb6_kit as k6
    from propedge.outcomes.orb_core import FLAT_ENTRY
    from propedge.outcomes.orb6_core import RANGE_RR

    res = Path(results_dir) if results_dir is not None else RESULTS_DIR
    files = {}
    for run in (orb3_run, orb5_run):
        rec, src = runs_dir / run / "ingested.json", res / f"manual_{run.replace('-', '_')}.csv"
        if not rec.is_file() or not src.is_file():
            return {}, f"{run} is not ingested (its run record or result file is missing): nothing to join to."
        files[run] = (rec, src)
    theirs = json.loads(files[orb3_run][0].read_text(encoding="utf-8"))["summary"]
    off = {k: (facts.get(k), theirs.get(k)) for k in HEAD_KEYS if int(facts.get(k, -1)) != int(theirs.get(k, -2))}
    if off:
        return {}, f"HEAD's day counts differ from {orb3_run}'s: {off} -- the run does not re-walk the same days."
    days6 = df[df["kind"] == "day"].astype({"or_minutes": int}).set_index(["date", "or_minutes"])
    o3 = _days(files[orb3_run][1])[list(JOIN_KEYS)]
    both = days6[list(JOIN_KEYS)].join(o3, how="outer", lsuffix="_6", rsuffix="_3")
    bad = pd.Series(False, index=both.index)
    for k in JOIN_KEYS:
        bad |= ~(both[f"{k}_6"] == both[f"{k}_3"])
    o5 = _days(files[orb5_run][1])[["lat_kind", "lat_slot", "lat_at_open", "lat_gap_ticks", "at_open"]].reindex(
        days6.index)
    walk = ["hand_range_a"] + [f"hand_range_f{R:g}".replace(".", "") for R in RANGE_RR]
    has6 = days6["hand_range_dist_ticks"] != -1
    has5 = o5["lat_kind"].fillna(-1) != -1
    hand_bad = has6 != has5
    lo = 1 - o5["lat_at_open"].fillna(0)
    for c in walk:
        x = days6[c]
        hand_bad |= has6 & has5 & (x != -1) & ((x < lo) | (o5["lat_slot"] + x > FLAT_ENTRY))
    # the hand entry's fill is ORB5's: its range stop's distance is the range, the slip, ORB5's gap from the original
    # fill and the tick beyond -- exactly where the original filled at the level, at least that where it gapped beyond
    p = k6.params()["p"]
    want = days6["range_ticks"] + o5["lat_gap_ticks"] + round(p["slip"] / p["tick"]) + 1
    got = days6["hand_range_dist_ticks"]
    hand_bad |= has6 & has5 & (((o5["at_open"] == 0) & (got != want)) | ((o5["at_open"] == 1) & (got < want)))
    bad = bad | hand_bad.reindex(both.index, fill_value=True)
    n_bad = int(bad.sum())
    join = {"rows": int(len(both)), "mismatched": n_bad, "hand_entry_mismatched": int(hand_bad.sum()),
            "mismatched_keys": [f"{d}/{m}" for d, m in both.index[bad][:50]], "against": [orb3_run, orb5_run]}
    if n_bad > MAX_MISMATCH * len(both):
        return join, (f"{n_bad} of {len(both)} day-and-range rows disagree with {orb3_run}'s on {JOIN_KEYS} or with "
                      f"{orb5_run}'s hand-traded entry -- more than {MAX_MISMATCH:.1%}: the capture does not describe "
                      "the same trades.")
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
    if kit.get("parser") != "orb6":
        print(f"REFUSED: {a.run_id} is not an ORB6 kit (parser {kit.get('parser')!r}); use "
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
            orb6_output_matches_kit(files["logs.txt"], kit["market"])
        df, facts = parse_orb6(files["logs.txt"], files["results.json"], market=kit["market"],
                               stops=tuple(kit["stops"]))
    except UnusableRun as exc:
        print(f"REFUSED: {exc}")
        return 2
    except ValueError as exc:
        print(f"REFUSED (re-download results.json from this backtest): it cannot be decoded ({exc}).")
        return 2
    join, problem = join_check(df, facts, kit["joins"], kit["captures"], runs_dir or RUNS, results_dir)
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
