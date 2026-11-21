"""A pytest plugin that records what a fast-tier run collected and each test's outcome (Q-193).

    python -m pytest -o addopts= -q -m "not slow and not heavy" -p extended.fasttier_report --s2x-report r.json ...

`scripts/fasttier_xdist.py` loads it in each of its three pytest runs -- the serial collection, the parallel run and the
serial rerun of the tests that failed in parallel -- to compare their counts and to name the tests that needed the
rerun. It changes nothing about which tests run or how: it adds one option, and without that option it does nothing.

**What it writes** (JSON, at the session's end, only in the main process -- an xdist worker loads the plugin, because
xdist passes the command line on, and does nothing):

- `collected`: the node ids the session selected, in order -- from the session itself in a serial run (`-m` already
  applied), or from the workers under xdist (each worker collects the whole selection; `worker_collections` holds each
  worker's count and `workers_agree` whether every worker collected the same list);
- `outcomes`: node id -> one of passed, failed, error, skipped, xfailed, xpassed (`outcome_of`), over every report a
  test produced (setup, call, teardown);
- `collect_errors`: the node ids of collectors that failed to collect;
- `exitstatus`: the session's exit status.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

OPTION = "--s2x-report"

#: the outcomes `outcome_of` returns; the two that fail a run are BAD
OUTCOMES = ("passed", "failed", "error", "skipped", "xfailed", "xpassed")
BAD = ("failed", "error")


def outcome_of(reports: list[tuple[str, str, bool]]) -> str:
    """One test's outcome from its reports, each (when, outcome, wasxfail), as pytest's own summary counts it.

    A failed setup or teardown is an `error` (even after a passed call); a failed call is `failed`; a skip in setup or
    call is `skipped`, or `xfailed` when it was an expected failure; a passed call is `passed`, or `xpassed` when an
    expected failure passed (a strict xpass is reported by pytest as a failed call). No report -- or no call or skip
    report -- is an `error`: the test never completed."""
    by_when: dict[str, tuple[str, bool]] = {}
    for when, outcome, wasxfail in reports:
        prev = by_when.get(when)
        if prev is None or outcome == "failed":
            by_when[when] = (outcome, wasxfail)
    for when in ("setup", "teardown"):
        if by_when.get(when, ("", False))[0] == "failed":
            return "error"
    call = by_when.get("call")
    if call is not None:
        outcome, wasxfail = call
        if outcome == "failed":
            return "failed"
        if outcome == "skipped":
            return "xfailed" if wasxfail else "skipped"
        if outcome == "passed":
            return "xpassed" if wasxfail else "passed"
    setup = by_when.get("setup")
    if setup is not None and setup[0] == "skipped":
        return "xfailed" if setup[1] else "skipped"
    return "error"


class Recorder:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.collected: list[str] | None = None
        self.worker_ids: dict[str, list[str]] = {}
        self.reports: dict[str, list[tuple[str, str, bool]]] = {}
        self.order: list[str] = []
        self.collect_errors: list[str] = []

    def pytest_collection_finish(self, session) -> None:
        self.collected = [item.nodeid for item in session.items]

    @pytest.hookimpl(optionalhook=True)
    def pytest_xdist_node_collection_finished(self, node, ids) -> None:
        wid = getattr(getattr(node, "gateway", None), "id", None) or str(node)
        self.worker_ids[str(wid)] = list(ids)

    def pytest_collectreport(self, report) -> None:
        if report.failed:
            self.collect_errors.append(report.nodeid)

    def pytest_runtest_logreport(self, report) -> None:
        if report.nodeid not in self.reports:
            self.reports[report.nodeid] = []
            self.order.append(report.nodeid)
        self.reports[report.nodeid].append((report.when, report.outcome, bool(getattr(report, "wasxfail", False))))

    @pytest.hookimpl(trylast=True)
    def pytest_sessionfinish(self, session, exitstatus) -> None:
        lists = list(self.worker_ids.values())
        collected = self.collected
        if collected is None and lists:
            collected = lists[0]
        rec = {
            "collected": collected if collected is not None else [],
            "worker_collections": {k: len(v) for k, v in self.worker_ids.items()},
            "workers_agree": all(v == lists[0] for v in lists) if lists else None,
            "outcomes": {nid: outcome_of(self.reports[nid]) for nid in self.order},
            "collect_errors": self.collect_errors,
            "exitstatus": int(exitstatus),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(rec, indent=1), encoding="utf-8")


def pytest_addoption(parser) -> None:
    parser.addoption(OPTION, dest="s2x_report", default=None,
                     help="Q-193: write the collected node ids and each test's outcome to this JSON file")


def pytest_configure(config) -> None:
    path = config.getoption("s2x_report", None)
    if path and not hasattr(config, "workerinput"):       # an xdist worker reports to the controller, which records
        config.pluginmanager.register(Recorder(Path(path)), "s2x-fasttier-recorder")
