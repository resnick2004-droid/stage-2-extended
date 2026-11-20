"""Synthetic inputs for `tests/test_playbook.py` (the restart plan's Wave 3.5, corrective cycle 1): one carried-design
declaration, a synthetic root (its own `DECISIONS.md`, the pinned declaration file, the two result files with their
manifests), the void calendar's sources for a few search-year days, and the trigger's offers -- all invented: no bar,
no atlas file and no result of this repository is read.

    root = build_root(tmp_path)                         # -> the root; load_carried(DECL_FILE, root=root)
    python tests/playbook_cases.py render <root>        # prints the playbook's sha256 (the hash-seed test)
    python tests/playbook_cases.py results <tmp dir>    # the real verify_result: written by the vendored writer

The fixture exercises rounding: every stop x R is a different product and one is not whole (77 x 1.3), and an alert's
flatten differs from the last entry (a news window after the order goes live). Each component's values differ. No
randomness is drawn here.
"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DESIGN = "X-demo7"
DECL_FILE = "prereg/X-demo7_playbook.json"
EXPECTED_FILE = "results/journey_x.csv"
NO_HARM_FILE = "results/noharm_x.csv"
COMMIT = "abc1234def"

EXPECTED_ROWS = [
    {"section": "journey", "block": "search", "measure": "S3b", "stat": "median", "value": "37.5", "n": "812"},
    {"section": "journey", "block": "search", "measure": "bankroll_stop_1700/share_run_out", "stat": "value",
     "value": "0.1234", "n": "812"},
    {"section": "journey", "block": "search", "measure": "S1", "stat": "p90", "value": "1543.25", "n": "812"},
    {"section": "journey", "block": "held_out", "measure": "S1", "stat": "p90", "value": "1611.5", "n": "40"},
    {"section": "journey", "block": "held_out", "measure": "S3b", "stat": "median", "value": "999", "n": "1"},
]
NO_HARM_ROWS = [
    {"section": "no_harm", "block": "search", "measure": "ldn_brk", "stat": "verdict", "value": "pass", "n": "300"},
    {"section": "no_harm", "block": "search", "measure": "am_rl3", "stat": "verdict", "value": "pass", "n": "250"},
    {"section": "no_harm", "block": "search", "measure": "pm_brk", "stat": "verdict", "value": "pass", "n": "410"},
    {"section": "no_harm", "block": "search", "measure": "pm_brk", "stat": "margin_used", "value": "0.42", "n": "410"},
]
COLUMNS = ("section", "block", "measure", "stat", "value", "n")


def declaration() -> dict:
    return copy.deepcopy({
        "design_id": DESIGN, "row": "E-9001", "firm": "topstep", "plan": "trading_combine", "instrument": "MNQ",
        "accounts": [{"id": "ts_a1", "role": "evaluation"}, {"id": "ts_b2", "role": "funded"},
                     {"id": "ts_c3", "role": "evaluation"}],
        "side": {"no_harm_row": "E-9002", "no_harm_file": NO_HARM_FILE},
        "components": [
            {"name": "ldn_brk", "session": "london", "first": 600, "last": 660, "stop_ticks": 77, "rr": 1.3,
             "contracts": 3, "latency": 5, "side_rule": "with_breakout",
             "trigger": {"source": "p14", "params": {"latency": 5, "entry": "market", "first": 595, "last": 655}}},
            {"name": "am_rl3", "session": "ny_am", "first": 960, "last": 1015, "stop_ticks": 100, "rr": 1.5,
             "contracts": 2, "latency": None, "side_rule": {"hi": "fade", "lo": "break"},
             "trigger": {"source": "rl3", "params": {"kind": "pd", "cutoff": 1020}}},
            {"name": "pm_brk", "session": "ny_pm", "first": 1080, "last": 1260, "stop_ticks": 60, "rr": 2.25,
             "contracts": 1, "latency": 3, "side_rule": "against_breakout",
             "trigger": {"source": "p14", "params": {"latency": 3, "entry": "limit", "first": 1077, "last": 1257}}},
        ],
        "rotation": {"rule": "by_component", "pools": {"pm_brk": ["ts_b2"], "am_rl3": ["ts_a1", "ts_c3"]}},
        "execution": {"gap_minutes": 5, "closed_window": [930, 959], "bls_clear": 875, "limit_window_min": 30,
                      "flatten": 1328, "last_entry": 1328},
        "news_windows": [
            {"source": "CPI (synthetic record key)", "release": 870, "before": 2, "after": 7,
             "dates": ["2021-03-16", "2021-04-07"]},
            {"source": "a synthetic afternoon release", "release": 1140, "before": 3, "after": 6,
             "dates": ["2021-03-17"]},
        ],
        "void_rules": ["fomc", "holiday", "early_close", "short_overnight", "prior_abbreviated"],
        "void_dates": [{"date": "2021-03-19", "reason": "early_close"}],
        "session_anchors": {"london": ["Europe/London", "08:00"], "ny_am": ["America/New_York", "09:30"],
                            "ny_pm": ["America/New_York", "09:30"]},
        "dates": ["2021-03-16", "2021-04-06"],
        "bankroll": {"budget": 1700, "row": "E-9003"},
        "expected": {"file": EXPECTED_FILE, "rows": [
            {"label": "sessions to the first payout", "section": "journey", "block": "search", "measure": "S3b",
             "stat": "median"},
            {"label": "chance of running out at the budget", "section": "journey", "block": "search",
             "measure": "bankroll_stop_1700/share_run_out", "stat": "value"},
            {"label": "bankroll needed, unlucky tenth", "section": "journey", "block": "search", "measure": "S1",
             "stat": "p90"},
            {"label": "bankroll needed, unlucky tenth", "section": "journey", "block": "held_out", "measure": "S1",
             "stat": "p90"},
        ]},
    })


# ------------------------------------------------------------------------------------------------ the synthetic root


def csv_bytes(rows: list[dict]) -> bytes:
    lines = [",".join(COLUMNS)] + [",".join(str(r[c]) for c in COLUMNS) for r in rows]
    return ("\n".join(lines) + "\n").encode()


def manifest(name: str, data: bytes, rows: int, *, design: str = DESIGN, convention: str, **over: Any) -> dict:
    """A manifest as a clean run of a named commit records it (`ResultManifest`'s fields)."""
    m = {"result_file": name, "script": "tests/playbook_cases.py", "git_commit": COMMIT, "seed": None,
         "parameters": {"design_id": design, "convention": convention}, "timestamp": "2021-01-01T00:00:00",
         "sha256": hashlib.sha256(data).hexdigest(), "rows": rows, "columns": list(COLUMNS),
         "description": "synthetic", "exploratory": False, "prereg_id": None, "variant_count": None, "notes": None,
         "provenance": {"clean_run": {"name": "synthetic-run", "checkout": "x", "marker": "S2X_CLEAN_RUN"}},
         "git_dirty": False}
    m.update(over)
    return m


def write_result(root: Path, rel: str, rows: list[dict], *, convention: str, man: dict | None = None,
                 **over: Any) -> str:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    data = csv_bytes(rows)
    p.write_bytes(data)
    m = man if man is not None else manifest(p.name, data, len(rows), convention=convention, **over)
    Path(str(p) + ".manifest.json").write_bytes(json.dumps(m, indent=2, sort_keys=True).encode())
    return m["sha256"]


def decl_bytes(decl: dict) -> bytes:
    return json.dumps(decl, indent=1, sort_keys=True).encode()


def build_root(root: Path, decl: dict | None = None, *, expected_rows: list[dict] | None = None,
               no_harm_rows: list[dict] | None = None, expected_over: dict | None = None,
               no_harm_over: dict | None = None, rows_text: Callable[[dict], dict] | None = None) -> Path:
    """The synthetic root: the declaration pinned in E-9001 with the expected journey's file, the no-harm file pinned
    in E-9002, E-9003 the budget's row. `rows_text` may edit the rows' texts (a test's mutation of the log)."""
    root = Path(root)
    decl = declaration() if decl is None else decl
    data = decl_bytes(decl)
    (root / "prereg").mkdir(parents=True, exist_ok=True)
    (root / DECL_FILE).write_bytes(data)
    exp_rel = decl.get("expected", {}).get("file", EXPECTED_FILE) if isinstance(decl.get("expected"), dict) \
        else EXPECTED_FILE
    nh_rel = decl.get("side", {}).get("no_harm_file", NO_HARM_FILE) if isinstance(decl.get("side"), dict) \
        else NO_HARM_FILE
    h_exp = write_result(root, exp_rel, EXPECTED_ROWS if expected_rows is None else expected_rows,
                         convention="zero_edge", **(expected_over or {}))
    h_nh = write_result(root, nh_rel, NO_HARM_ROWS if no_harm_rows is None else no_harm_rows,
                        convention="no_harm_real_path", **(no_harm_over or {}))
    rows = {
        "E-9001": f"**{DESIGN} carried (synthetic)** `{DECL_FILE}` sha256 `{hashlib.sha256(data).hexdigest()}`; its "
                  f"expected journey `{exp_rel}` sha256 `{h_exp}`.",
        "E-9002": f"**{DESIGN}'s no-harm floor (synthetic)** `{nh_rel}` sha256 `{h_nh}`.",
        "E-9003": "**The bankroll budget (synthetic).**",
    }
    if rows_text is not None:
        rows = rows_text(rows)
    log = "# Decisions (synthetic)\n\n| id | date | decision | basis |\n|---|---|---|---|\n" + "".join(
        f"| {k} | 2021-01-01 | {v} | synthetic |\n" for k, v in rows.items())
    (root / "DECISIONS.md").write_bytes(log.encode())
    return root


def verify_standin(path):
    """The vendored `verify_result`'s check (`propedge.reporting.results.verify_result`: the file and its manifest
    exist and the file's plain sha256 is the manifest's), for the in-process tests, which must not put the vendored
    tree on `sys.path`; the subprocess test (`results`) runs the real one."""
    p = Path(path)
    mp = Path(str(p) + ".manifest.json")
    if not p.is_file() or not mp.is_file():
        return False, "missing"
    want = json.loads(mp.read_bytes())["sha256"]
    got = hashlib.sha256(p.read_bytes()).hexdigest()
    return (got == want), ("verified" if got == want else "modified")


# ------------------------------------------------------------------------------------------------ the day and the offers

DAYS = ("2021-03-15", "2021-03-16", "2021-03-17", "2021-03-18", "2021-03-19", "2021-04-05", "2021-04-06",
        "2021-04-07")


def sources(*, bls=(), fomc=(), rolls=(), early_end=(), calendar=None, flags=None, last_bar=None):
    """The void calendar's sources for `DAYS` (synthetic: every day clean unless named)."""
    from extended import day_calendar as DC

    ds = [date.fromisoformat(d) for d in DAYS]
    fl = {d: {"day": d.isoformat(), "verdict": "OK", "void": "", "missing_after_reopen": "0", "special": ""}
          for d in ds}
    for k, v in (flags or {}).items():
        fl[date.fromisoformat(k)].update(v)
    lb = {d: "15:59" for d in ds}
    for k, v in (last_bar or {}).items():
        lb[date.fromisoformat(k)] = v
    iso = lambda xs: frozenset(date.fromisoformat(x) for x in xs)  # noqa: E731
    return DC.Sources(ds, {date.fromisoformat(k): v for k, v in (calendar or {}).items()}, iso(rolls),
                      iso(early_end), lb, iso(bls), iso(fomc), fl, None)


def p14_offer(**kw):
    """pm_brk's offer: P-14 limit, L = 3, the event at 11:21 CT (slot 1101) a close above the high."""
    from extended import triggers as T

    f = dict(source="p14", session=41, decision=1101, sub=0, alert=1101, live=1104, entry=T.LIMIT, level=18234.75,
             expires=1104 + T.LIMIT_WINDOW - 1, tag="brk30+")
    f.update(kw)
    return T.Offer(**f)


def ldn_offer(**kw):
    """ldn_brk's offer: P-14 market, L = 5, the event at 03:10 CT (slot 610) a close below the low."""
    from extended import triggers as T

    f = dict(source="p14", session=41, decision=610, sub=0, alert=610, live=615, entry=T.MARKET, tag="brk30-")
    f.update(kw)
    return T.Offer(**f)


def rl3_offer(name="hi", role=1, **kw):
    """am_rl3's ticket at the previous day's high (or low), alert 08:30, live 09:00, cutoff 11:00 CT."""
    from extended import triggers as T

    f = dict(source="rl3", session=41, decision=T.RTH_OPEN, sub=T.RL3_SUBS[("pd", name)], alert=T.RTH_OPEN,
             live=T.LIVE_0900, entry=T.TICKET, level=18100.0 if name == "hi" else 17950.0, role=role,
             expires=1020 - 1, group="rl3:pd", rewrite=True, tag=f"pd_{name}")
    f.update(kw)
    return T.Offer(**f)


def scheduled(**kw):
    from extended import components as C

    f = dict(firm="topstep", component="pm_brk", source="p14", session=41, date="2021-03-16", decision=1101,
             alert=1101, live=1104, tag="brk30+", order_kind="limit", ticket_rule="", side=-1, side_source="coin",
             fill_slot=1107, fill_price=18234.75, resting=True, stop_ticks=60, target_ticks=135, rr=2.25,
             exit_slot=1150, exit_kind="t", flatten_slot=1328, window_flatten=False, instrument="MNQ",
             underlying="NQ", gross_ticks=135, net_r=None)
    f.update(kw)
    return C.ScheduledTrade(**f)


# ------------------------------------------------------------------------------------------------ the subprocess halves


def _main(argv: list[str]) -> int:
    from extended import playbook as PB
    if argv[0] == "render":
        print(hashlib.sha256(PB.render_playbook(PB.load_carried(DECL_FILE, root=Path(argv[1]))).text.encode())
              .hexdigest())
        return 0
    if argv[0] == "results":
        import pandas as pd

        from extended.results import write_result as vendored_write

        out: dict[str, str] = {}
        base = Path(argv[1])

        def attempt(name: str, root: Path) -> None:
            try:
                c = PB.load_carried(DECL_FILE, root=root)
                out[name] = "accepted:" + c.expected.commit
            except PB.PlaybookRefused as e:
                out[name] = "refused:" + str(e)[:120]

        def real_root(name: str, *, clean: bool, exp_params: dict | None = None, exploratory: bool = False,
                      tamper: bool = False) -> Path:
            root = base / name
            build_root(root)                                     # the log and the declaration, then real files
            hashes = {}
            for rel, rows, conv in ((EXPECTED_FILE, EXPECTED_ROWS, "zero_edge"),
                                    (NO_HARM_FILE, NO_HARM_ROWS, "no_harm_real_path")):
                p = root / rel
                p.unlink()
                Path(str(p) + ".manifest.json").unlink()
                params = {"design_id": DESIGN, "convention": conv}
                if rel == EXPECTED_FILE and exp_params is not None:
                    params = exp_params
                csv, mp = vendored_write(pd.DataFrame(rows, columns=list(COLUMNS)), p.stem,
                                         script="tests/playbook_cases.py", seed=None, parameters=params,
                                         results_dir=p.parent, require_seed=False,
                                         exploratory=exploratory and rel == EXPECTED_FILE,
                                         description="synthetic test rows; no randomness")
                if clean:                                   # as a clean run of a named commit records it
                    m = json.loads(mp.read_bytes())
                    m.update(git_commit=COMMIT, git_dirty=False,
                             provenance={"clean_run": {"name": "synthetic-run", "checkout": "x",
                                                       "marker": "S2X_CLEAN_RUN"}})
                    mp.write_bytes(json.dumps(m, indent=2, sort_keys=True).encode())
                hashes[rel] = json.loads(mp.read_bytes())["sha256"]
                if tamper and rel == EXPECTED_FILE:
                    csv.write_bytes(csv.read_bytes().replace(b"37.5", b"12.5"))
            log = (root / "DECISIONS.md").read_bytes().decode()
            for rel, h in hashes.items():
                import re
                log = re.sub(r"(`" + re.escape(rel) + r"` sha256 `)[0-9a-f]+(`)", lambda m: m.group(1) + h + m.group(2),
                             log)
            (root / "DECISIONS.md").write_bytes(log.encode())
            return root

        attempt("clean", real_root("clean", clean=True))
        attempt("tampered", real_root("tampered", clean=True, tamper=True))
        attempt("as_written", real_root("as_written", clean=False))                  # outside a clean run
        attempt("other_design", real_root("other_design", clean=False, exploratory=True,
                                          exp_params={"design_id": "SOME-OTHER-DESIGN", "as_traded": True}))
        print(json.dumps(out))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
