"""Bring an FV3 capture run (R117-R125; T17 item 3) from QuantConnect's web editor into the repository.

    python scripts/ingest_fv3_run.py R117-fv3-NQ-0910 --backtest-id <id> --run-by "<name>" --rounds 0 \\
        --limit-hit none --files runs/R117-fv3-NQ-0910/downloads/logs.txt runs/R117-fv3-NQ-0910/downloads/results.json

FV2's ingest (`scripts/ingest_fv2_run.py`) for FV3's parser (`propedge/data/fv3_parser.py`): the kit is read, a run
already ingested is refused, the ran code is hash-checked against the committed `main.py` -- or attested by the
operator (D-131) -- the downloads are parsed (an incomplete output is refused), the capture is joined to the ORB3 run
whose days it re-walks over its own dates (D-265: the day set and each day's ATR), and the result is saved through
`propedge/data/manual_runs.record_manual_run` with provenance "human-run in QuantConnect web editor"; then
`runs/<run-id>/ingested.json` and `results/manual_run_effort.csv` are written.

FV3-C's confirmation kits (D-355; R139-R141, `confirm` in kit.json) are ingested as NQB1's and NQB2's were (D-229 to
D-232, D-242): the log is judged usable before any record is parsed -- END and HEAD present, no error or time limit in
the log or reported by the operator, HEAD's days at least the period's `min_days` -- and an unusable run is recorded in
`runs/<run>/unusable.json` and never parsed or ingested afterwards; a parser refusal makes it unusable too, its message
kept out of the record (it may carry held-back values); a refusal of the procedure (files, downloads, ran code) is
retried on the same backtest's files; a `results.json` that cannot be decoded is re-downloaded once, then recorded
unusable with `--declare-unreadable`. Nothing is joined: no ORB3 run reads the window (the record says so); the
registration id embedded in the kit must be a runnable row of prereg/REGISTRY.md.

**The order (D-356, from the gatekeeper's refusal of the first draft):** every period is judged before any period's
records are saved, so no run -- a fix kit included, and so the end of 2026 Q3, which is QuantConnect's data end on the
day its kit runs -- can be timed after part of the window has been read. `--usability-only` judges one run completely
(its log, the parser on its output in memory, its days inside the period) and writes `runs/<run>/usable.json`, saving no
record; the ingest that saves records refuses until every period of `config/fv3_confirmation.yaml` has a run judged
usable, and refuses outright once a period is unusable twice (the confirmation then FAILs without any record read).
The records saved for a period are those of the backtest judged usable: `usable.json` carries its backtest id and the
sha256 of its downloaded log and results, the saving ingest refuses any other backtest or files, and `ingested.json`
carries the same hashes for the verdict to check.
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
from propedge.data.fv3_parser import fv3_output_matches_kit, parse_fv3  # noqa: E402
from propedge.data.manual_parsers import UnusableRun  # noqa: E402
from propedge.data.manual_runs import ManualRunRefused, record_manual_run  # noqa: E402

RUNS = ROOT / "runs"


def join_check(df, orb3_run: str, window: tuple[str, str], runs_dir: Path, results_dir: Path | None):
    """D-265 for FV3, exactly FV2's reading: over the run's own dates, the days recorded are ORB3's and each day's
    ATR equals ORB3's."""
    from ingest_fv2_run import join_check as fv2_join

    return fv2_join(df, orb3_run, window, runs_dir, results_dir)


def fv3_usability(log_path: Path, min_days: int, limit_hit: str = "none") -> list[str]:
    """D-230's single test for a confirmation run (D-355), judged from its log alone -- no record is parsed: no END or
    HEAD, an error or a time limit in the log or reported by the operator, or HEAD's days below `min_days`. Empty:
    usable."""
    import re

    from propedge.data.fv3_parser import fv3_head

    out = []
    text = Path(log_path).read_text(encoding="utf-8", errors="replace")
    if re.search(r"runtime error|time ?limit|timed out|exceeded", text, re.IGNORECASE):
        out.append("the log reports an error or a time limit")
    if str(limit_hit).strip().lower() not in ("", "none"):
        out.append(f"the operator reports a limit: {limit_hit}")
    try:
        head = fv3_head(log_path)
    except UnusableRun as exc:
        return out + [str(exc)]
    if int(head.get("days", 0)) < int(min_days):
        out.append(f"HEAD reports {head.get('days')} days, fewer than the {min_days} required")
    return out


def _unusable(kit_dir: Path, a, backtest_name, prereg, why: list[str], what: str) -> None:
    """D-230: record an unusable confirmation run; its records are never read."""
    record = {"run_id": a.run_id, "date_run": a.date_run, "run_by": a.run_by, "qc_backtest_id": str(a.backtest_id),
              "qc_backtest_name": backtest_name, "prereg": prereg,
              "status": f"unusable: not ingested; {what} (D-230, D-355)", "why": why,
              "downloads": f"runs/{a.run_id}/downloads/ (gitignored, kept locally)"}
    (kit_dir / "unusable.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")


def download_hashes(files: dict[str, Path], names) -> dict[str, str]:
    """sha256 of each downloaded file named (the log and the results), as received."""
    import hashlib

    return {n: hashlib.sha256(files[n].read_bytes()).hexdigest() for n in sorted(names) if n in files}


def periods_not_judged(runs_dir: Path) -> tuple[list[str], list[str]]:
    """D-356: (the periods without a run judged usable, the periods unusable twice) over the confirmation config's
    periods -- each period's permitted runs its kit and, once a decision adds it, its `fix_run`."""
    from propedge.data import fv3_kit as kf

    pending, failed = [], []
    for p in kf.confirm_config()["periods"]:
        runs = [str(p["run"])] + ([str(p["fix_run"])] if p.get("fix_run") else [])
        bad = [r for r in runs if (runs_dir / r / "unusable.json").is_file()]
        good = [r for r in runs if (runs_dir / r / "usable.json").is_file() and r not in bad]
        if good:
            continue
        (failed if len(bad) >= 2 else pending).append(str(p["id"]))
    return pending, failed


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
    ap.add_argument("--declare-unreadable", action="store_true",
                    help="D-232: a confirmation run whose results.json from the same backtest still cannot be decoded "
                         "after one re-download is recorded unusable")
    ap.add_argument("--usability-only", action="store_true",
                    help="D-356: judge a confirmation run completely (log, parser, dates) and record usable.json; no "
                         "record is saved")
    a = ap.parse_args(argv)

    kit_dir = (runs_dir or RUNS) / a.run_id
    kit = json.loads((kit_dir / "kit.json").read_text(encoding="utf-8"))
    if kit.get("parser") != "fv3":
        print(f"REFUSED: {a.run_id} is not an FV3 kit (parser {kit.get('parser')!r}); use "
              "scripts/ingest_manual_run.py.")
        return 2
    if (kit_dir / "ingested.json").exists():
        print(f"REFUSED: {a.run_id} is already ingested; a result stays on record.")
        return 2
    confirm = bool(kit.get("confirm"))
    if confirm and (kit_dir / "unusable.json").exists():     # D-232: an unusable run is never ingested afterwards
        print(f"REFUSED: {a.run_id} is recorded unusable; it is never ingested, whatever files are given (D-232).")
        return 2
    prereg = str(kit.get("prereg")) if confirm else None
    if a.usability_only and not confirm:
        print("REFUSED: --usability-only is for a confirmation kit (D-356).")
        return 2
    if confirm:
        from propedge.data.cloud_guard import confirmation_run_authorised

        if not confirmation_run_authorised(prereg):
            print(f"REFUSED: the kit's registration {prereg!r} is not a runnable row of prereg/REGISTRY.md (D-81, D-355).")
            return 2
        if a.usability_only and (kit_dir / "usable.json").exists():
            print(f"REFUSED: {a.run_id} is already judged usable (usable.json); ingest it once every period is judged.")
            return 2
        if not a.usability_only:                              # D-356: every period judged before any record is saved
            if not (kit_dir / "usable.json").exists():
                print(f"REFUSED: {a.run_id} is not judged yet; run this with --usability-only first (D-356).")
                return 2
            judged = json.loads((kit_dir / "usable.json").read_text(encoding="utf-8"))
            given = {Path(f).name: Path(f) for f in a.files}
            mine = download_hashes(given, [n for n in kit["downloads"] if n != kit["ran_code"]])
            if str(a.backtest_id) != str(judged.get("qc_backtest_id")) or mine != judged.get("downloads_sha256"):
                print(f"REFUSED: these are not the backtest and files judged usable for {a.run_id} (backtest "
                      f"{judged.get('qc_backtest_id')}, the sha256 in usable.json): the records saved are those of the "
                      "backtest judged, never a later run (D-356).")
                return 2
            pending, failed = periods_not_judged(runs_dir or RUNS)
            if failed:
                print(f"REFUSED: period(s) {failed} unusable twice -- the confirmation FAILs without any record read "
                      "(D-230); run scripts/confirm_fv3.py.")
                return 2
            if pending:
                print(f"REFUSED: period(s) {pending} have no run judged usable yet; every period is judged "
                      "(--usability-only) before any record is saved (D-356).")
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
    if confirm:                                               # D-355, as D-230: usable before any record is parsed
        why = fv3_usability(files["logs.txt"], int(kit["min_days"]), a.limit_hit)
        if why:
            _unusable(kit_dir, a, backtest_name, prereg, why, "its records were never parsed")
            print(f"REFUSED (D-230): {a.run_id} is unusable -- " + "; ".join(why) + ". Recorded in unusable.json; "
                  "no record was parsed.")
            return 2
    project = a.project_id or f"{kit['project_name']} (by name; numeric id not noted, D-188)"
    ran_code, attested_by = kit_dir / "downloads" / kit["ran_code"], None
    try:
        if a.ran_code_attested:
            attested_by, ran_code = a.run_by, None
            fv3_output_matches_kit(files["logs.txt"], kit["market"])
        df, facts = parse_fv3(files["logs.txt"], files["results.json"], market=kit["market"])
    except UnusableRun as exc:
        if confirm:                                           # the output's integrity (D-231); the message withheld
            local = kit_dir / "downloads" / "parser_refusal.txt"
            local.parent.mkdir(parents=True, exist_ok=True)
            local.write_text(str(exc) + "\n", encoding="utf-8")
            _unusable(kit_dir, a, backtest_name, prereg,
                      ["the parser refused its output (the message is kept in downloads/parser_refusal.txt, gitignored: "
                       "it may carry held-back values)"], "the parser refused its output; no record was used")
            print(f"REFUSED (D-230): {a.run_id} is unusable -- the parser refused its output. Recorded in unusable.json.")
            return 2
        print(f"REFUSED: {exc}")
        return 2
    except ValueError as exc:
        if confirm and a.declare_unreadable:
            _unusable(kit_dir, a, backtest_name, prereg, ["results.json cannot be decoded after a re-download"],
                      "its results could not be decoded; no record was used")
            print(f"REFUSED (D-232): {a.run_id} is unusable -- its results cannot be decoded. Recorded.")
            return 2
        print(f"REFUSED (re-download results.json from this backtest): it cannot be decoded ({exc}).")
        return 2
    if confirm:
        # no ORB3 run reads the held-back window, so D-265's join has nothing to check against; the day set and each
        # day's ATR are the kit's own (D-355), and the period's dates bound the records
        lo, hi = (str(x) for x in kit["window"])
        days = df[df["kind"] == "day"]["date"].astype(str)
        if len(days) and (days.min() < lo or days.max() > hi):
            _unusable(kit_dir, a, backtest_name, prereg, ["a day record outside the period's dates"],
                      "a record outside the period; no record was used")
            print(f"REFUSED (D-230): {a.run_id} is unusable -- a day record outside the period. Recorded in unusable.json.")
            return 2
        join = {"skipped": "no ORB3 run reads the held-back window (D-355); the day set and ATR are the kit's own",
                "days": int(len(days))}
        if a.usability_only:                                  # D-356: judged completely; nothing saved, nothing shown
            record = {"run_id": a.run_id, "date_run": a.date_run, "run_by": a.run_by,
                      "qc_backtest_id": str(a.backtest_id), "qc_backtest_name": backtest_name, "prereg": prereg,
                      "downloads_sha256": download_hashes(files, [n for n in kit["downloads"] if n != kit["ran_code"]]),
                      "status": "usable: its log, the parser on its output and its dates passed; no record saved "
                                "(D-230, D-356)",
                      "downloads": f"runs/{a.run_id}/downloads/ (gitignored, kept locally)"}
            (kit_dir / "usable.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
            print(f"{a.run_id} is usable (usable.json); no record was saved.")
            return 0
    else:
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
            ran_code_attested_by=attested_by, prereg_id=prereg,
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
    if confirm:                                               # D-356: the backtest judged, identified by its files
        record["downloads_sha256"] = download_hashes(files, [n for n in kit["downloads"] if n != kit["ran_code"]])
    (kit_dir / "ingested.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
    effort.write_effort_log()
    print(f"saved {csv.relative_to(ROOT)} with {manifest.name}")
    print(effort.evaluate(effort.load_records(), effort.UpgradeRule.load()).summary())
    print("Commit runs/ and results/ together.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
