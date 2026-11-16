"""Effort log for manual runs, and the rule for upgrading to a paid seat (D-82).

Every ingested run leaves `runs/<run-id>/ingested.json`, which carries the operator's minutes,
fix-and-rerun rounds and any limit hit. `results/manual_run_effort.csv` is **regenerated** from
those records on every ingestion, through the results writer, so the log is derived and
reproducible rather than appended by hand.

The upgrade rule lives in `config/manual_runs.yaml`: confirmed 2026-09-23 (D-83), evaluated on runs
2-6 in the order run -- the first run is skipped because it carries one-off setup.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yaml

from propedge import CONFIG_DIR, REPO_ROOT
from propedge.reporting.results import write_result

RUNS_DIR = REPO_ROOT / "runs"
EFFORT_RESULT = "manual_run_effort"
COLUMNS = ["run_id", "date_run", "run_by", "minutes", "rounds", "limit_hit",
           "qc_project_id", "qc_backtest_id", "result_file"]


def load_records(runs_dir: Path = RUNS_DIR) -> list[dict]:
    """Every ingested run, in the order it was run (date, then run id)."""
    recs = [json.loads(p.read_text(encoding="utf-8"))
            for p in sorted(runs_dir.glob("*/ingested.json"))]
    return sorted(recs, key=lambda r: (r["date_run"], r["run_id"]))


def effort_frame(records: list[dict]) -> pd.DataFrame:
    rows = [{c: r.get(c) for c in COLUMNS} for r in records]
    return pd.DataFrame(rows, columns=COLUMNS)


def write_effort_log(*, runs_dir: Path = RUNS_DIR, results_dir: Path | None = None):
    df = effort_frame(load_records(runs_dir))
    return write_result(
        df, EFFORT_RESULT,
        script="scripts/ingest_manual_run.py",
        seed=None, require_seed=False,
        parameters={"source": "runs/*/ingested.json", "rule": str(CONFIG_DIR / "manual_runs.yaml")},
        description=("Operator effort per manual run in the QuantConnect web editor (D-82): minutes, "
                     "fix-and-rerun rounds, limits hit. Reported by the operator at ingestion; no "
                     "randomness, so no seed."),
        results_dir=results_dir,
    )


@dataclass(frozen=True)
class UpgradeRule:
    status: str
    skip_first_runs: int
    evaluate_after_runs: int
    max_mean_minutes: float
    max_mean_rounds: float
    max_runs_hitting_a_limit: int

    @classmethod
    def load(cls, path: Path | None = None) -> "UpgradeRule":
        doc = yaml.safe_load((path or CONFIG_DIR / "manual_runs.yaml").read_text(encoding="utf-8"))
        r = doc["upgrade_rule"]
        return cls(status=r["status"], skip_first_runs=int(r.get("skip_first_runs", 0)),
                   evaluate_after_runs=int(r["evaluate_after_runs"]),
                   max_mean_minutes=float(r["max_mean_minutes"]),
                   max_mean_rounds=float(r["max_mean_rounds"]),
                   max_runs_hitting_a_limit=int(r["max_runs_hitting_a_limit"]))


@dataclass(frozen=True)
class UpgradeVerdict:
    evaluable: bool
    upgrade: bool
    reasons: tuple[str, ...]
    runs_counted: int
    mean_minutes: float | None
    mean_rounds: float | None
    runs_hitting_a_limit: int | None
    rule_status: str

    def summary(self) -> str:
        head = f"upgrade rule ({self.rule_status}): "
        if not self.evaluable:
            return head + (f"not yet evaluable -- {self.runs_counted} run(s) in the evaluation "
                           f"window so far.")
        verdict = "UPGRADE" if self.upgrade else "stay on manual runs"
        mins = (f"mean {self.mean_minutes:.1f} min" if self.mean_minutes is not None
                else "minutes not recorded")
        detail = (f"{self.runs_counted} runs in the window: {mins}, mean "
                  f"{self.mean_rounds:.2f} rounds, {self.runs_hitting_a_limit} hit a limit")
        why = ("; ".join(self.reasons)) if self.reasons else "no threshold exceeded"
        return head + f"{verdict} -- {detail}; {why}."


def _hit(limit) -> bool:
    return bool(limit) and str(limit).strip().lower() not in {"none", "no", ""}


def evaluate(records: list[dict], rule: UpgradeRule) -> UpgradeVerdict:
    """Apply the rule to runs `skip+1` .. `skip+n`, in the order they were run."""
    n, skip = rule.evaluate_after_runs, rule.skip_first_runs
    window = records[skip:skip + n]
    if len(window) < n:
        return UpgradeVerdict(False, False, (), len(window), None, None, None, rule.status)
    first = window
    timed = [float(r["minutes"]) for r in first if r.get("minutes") is not None]
    mm = sum(timed) / len(timed) if timed else None     # D-110: minutes are optional
    mr = sum(int(r["rounds"]) for r in first) / n
    lim = sum(1 for r in first if _hit(r.get("limit_hit")))
    reasons = []
    if mm is not None and mm > rule.max_mean_minutes:
        reasons.append(f"mean minutes {mm:.1f} > {rule.max_mean_minutes:g}")
    if mr > rule.max_mean_rounds:
        reasons.append(f"mean rounds {mr:.2f} > {rule.max_mean_rounds:g}")
    if lim > rule.max_runs_hitting_a_limit:
        reasons.append(f"{lim} runs hit a limit > {rule.max_runs_hitting_a_limit}")
    return UpgradeVerdict(True, bool(reasons), tuple(reasons), n, mm, mr, lim, rule.status)
