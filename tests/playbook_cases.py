"""Synthetic inputs for `tests/test_playbook.py` (the restart plan's Wave 3.5, corrective cycle 2 and the final
read's fixes): one design's declaration and its carrying record; a synthetic root (its own `DECISIONS.md` in the
declared order -- the declaration pinned, the no-harm floor, the 3.9 row stating the margin, the carrying row with its
token --, the two pinned JSON files, the two result files bound to the declaration with their manifests); the void
calendar's sources and a synthetic bar history for a few search-year days on both sides of the 2021 daylight-saving
changes; a router; and a real git history for the pin-order check (`git_root`). All invented: no bar, no atlas file
and no result of this repository is read.

    root = build_root(tmp_path)                         # -> the root; load_carried(RECORD_FILE, root=root)
    python tests/playbook_cases.py render <root>        # prints the playbook's sha256 (the hash-seed test)
    python tests/playbook_cases.py results <tmp dir>    # the real verify_result: written by the vendored writer

**The dates.** 2021-03-11 and 2021-03-12: Chicago and London on standard time (London 08:00 is 02:00 CT, Tokyo 09:00
is 18:00 CT the evening before). 2021-03-15 to 2021-03-19: Chicago on daylight time, London not yet (London 08:00 is
03:00 CT, Tokyo 09:00 is 19:00 CT). 2021-04-05 to 2021-04-07: both on summer time (London 08:00 is 02:00 CT).

**The bars** (`history`): every bar at 18000, the regular session's bars (stamped 08:30 to 14:59) ranging 17900 to
18100, each day's bar stamped 14:59 closing at 18050 (the next day's `pdc` level). On 2021-03-12, 03-16 and 03-17 a
close at 17990 ten minutes into London's and Asia's sessions (that date's start + 10: a `brk30-` breakout below the
reference low), and on 03-16, 03-17 and 03-19 a close at 18110 on the bar ending at 11:21 CT (`brk30+`). On 2021-04-05
the regular session's low is 18000, so on 2021-04-06 RL3's `pd` low sits at the reference (`at_reference`). The prices
exist only inside this file.

The fixture exercises rounding (77 x 1.3 is not whole), a flatten other than the last entry, windows that move in CT
across the daylight-saving changes, and different values per component. No randomness is drawn except in `scrambled`,
under an explicit seed.
"""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DESIGN = "X-demo"
FAMILY = "F-demo"
REGISTRATION = "REG-demo"
DECL_FILE = "prereg/X-demo_playbook.json"
RECORD_FILE = "prereg/X-demo_carried.json"
EXPECTED_FILE = "results/journey_x.csv"
NO_HARM_FILE = "results/noharm_x.csv"
EXPECTED_SCRIPT = "scripts/journey_expected.py"
NO_HARM_SCRIPT = "scripts/no_harm_floor.py"
HELDOUT_FILE = "results/heldout_x.csv"
HELDOUT_SCRIPT = "scripts/heldout_joint.py"
HELDOUT_FAMILY = FAMILY_JOINT = "F-joint"
MANIFEST = ".manifest.json"
COMMIT = "abc1234def"
MARGIN = 0.05

EXPECTED_ROWS = [
    {"section": "journey", "block": "search", "measure": "S3b", "stat": "median", "value": "37.5", "n": "812"},
    {"section": "journey", "block": "search", "measure": "bankroll_stop_1700/share_run_out", "stat": "value",
     "value": "0.1234", "n": "812"},
    {"section": "journey", "block": "search", "measure": "S1", "stat": "p90", "value": "6250", "n": "812"},
    {"section": "journey", "block": "held_out", "measure": "S1", "stat": "p90", "value": "6611.5", "n": "10000"},
    {"section": "journey", "block": "held_out", "measure": "S3b", "stat": "median", "value": "999", "n": "1"},
]


def _nh(comp: str, rule: str, tc: str, cc: str, n: str) -> list[dict]:
    return [{"section": "no_harm", "block": "search", "measure": comp, "stat": s, "value": v, "n": n}
            for s, v in (("side_rule", rule), ("margin", str(MARGIN)), ("trigger_composite", tc),
                         ("coin_composite", cc))]


NO_HARM_ROWS = (_nh("asia_brk", "with_breakout", "0.22", "0.2", "280")
                + _nh("ldn_brk", "with_breakout", "0.31", "0.3", "300")
                + _nh("am_tix", "hi=fade;lo=break", "0.27", "0.29", "250")
                + _nh("pm_brk", "against_breakout", "0.4", "0.33", "410"))
COLUMNS = ("section", "block", "measure", "stat", "value", "n")
HELDOUT_ROWS = [{"section": "heldout", "block": "joint", "measure": DESIGN, "stat": "verdict", "value": "accepted",
                 "n": "1"}]


def declaration() -> dict:
    return copy.deepcopy({
        "design_id": DESIGN, "family": FAMILY, "firm": "topstep", "plan": "trading_combine", "instrument": "MNQ",
        "accounts": [{"id": "ts_a", "role": "evaluation"}, {"id": "ts_b", "role": "funded"},
                     {"id": "ts_c", "role": "evaluation"}],
        "side": {"no_harm_row": "E-9002", "no_harm_file": NO_HARM_FILE, "no_harm_script": NO_HARM_SCRIPT,
                 "margin": MARGIN, "margin_row": "E-9000"},
        "components": [
            {"name": "asia_brk", "session": "asia", "first": 0, "last": 55, "stop_ticks": 50, "rr": 1.7,
             "contracts": 2, "latency": 5, "side_rule": "with_breakout",
             "trigger": {"source": "p14", "params": {"latency": 5, "entry": "market"}}},
            {"name": "ldn_brk", "session": "london", "first": 0, "last": 60, "stop_ticks": 77, "rr": 1.3,
             "contracts": 3, "latency": 5, "side_rule": "with_breakout",
             "trigger": {"source": "p14", "params": {"latency": 5, "entry": "market"}}},
            {"name": "am_tix", "session": "ny_am", "first": 30, "last": 85, "stop_ticks": 100, "rr": 1.5,
             "contracts": 2, "latency": None, "side_rule": {"hi": "fade", "lo": "break"},
             "trigger": {"source": "rl3", "params": {"kind": "pd", "cutoff": 1020}}},
            {"name": "pm_brk", "session": "ny_am", "first": 150, "last": 330, "stop_ticks": 60, "rr": 2.25,
             "contracts": 1, "latency": 3, "side_rule": "against_breakout",
             "trigger": {"source": "p14", "params": {"latency": 3, "entry": "limit"}}},
        ],
        "rotation": {"rule": "by_component", "pools": {"pm_brk": ["ts_b"], "am_tix": ["ts_a", "ts_c"]}},
        "execution": {"gap_minutes": 5, "closed_window": [930, 959], "bls_clear": 875, "limit_window_min": 30,
                      "flatten": 1328, "last_entry": 1328},
        "news_source": "the synthetic release record",
        "news_windows": [
            {"source": "CPI (synthetic record key)", "release": 870, "before": 2, "after": 7,
             "dates": ["2021-03-16", "2021-04-07"]},
            {"source": "a synthetic afternoon release", "release": 1140, "before": 3, "after": 6,
             "dates": ["2021-03-17"]},
        ],
        "void_rules": ["fomc", "early_close", "prior_abbreviated"],
        "research_filters": ["short_bars", "overnight_missing"],
        "void_dates": [{"date": "2021-03-19", "reason": "early_close"}],
        "session_anchors": {"asia": ["Asia/Tokyo", "09:00"], "london": ["Europe/London", "08:00"],
                            "ny_am": ["America/New_York", "09:30"]},
        "dates": ["2021-03-12", "2021-03-16", "2021-04-06"],
        "bankroll": {"budget": 1700, "row": "E-9000"},
        "expected": {"file": EXPECTED_FILE, "script": EXPECTED_SCRIPT, "rows": [
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


def record(decl_sha: str, **over: Any) -> dict:
    r = {"design_id": DESIGN, "declaration": DECL_FILE, "declaration_sha256": decl_sha, "registration": REGISTRATION,
         "row": "E-9004", "heldout_file": HELDOUT_FILE, "heldout_script": HELDOUT_SCRIPT,
         "heldout_family": FAMILY_JOINT}
    r.update(over)
    return r


# ------------------------------------------------------------------------------------------------ the synthetic root


def csv_bytes(rows: list[dict], columns=COLUMNS) -> bytes:
    import csv
    import io

    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(columns)
    for r in rows:
        w.writerow([str(r[c]) for c in columns])
    return buf.getvalue().encode()


def json_bytes(obj: dict) -> bytes:
    return json.dumps(obj, indent=1, sort_keys=True).encode()


def decl_sha(decl: dict) -> str:
    return hashlib.sha256(json_bytes(decl)).hexdigest()


def manifest(name: str, data: bytes, rows: int, *, convention: str, sha_decl: str, script: str, **over: Any) -> dict:
    """A manifest as a clean run of a named commit records it (`ResultManifest`'s fields), bound to the declaration.
    `over`: fields replaced; `parameters_update`: parameters changed."""
    params = {"design_id": DESIGN, "convention": convention, "declaration_file": DECL_FILE,
              "declaration_sha256": sha_decl}
    if convention == "no_harm_real_path":
        params["margin"] = MARGIN
    family = FAMILY_JOINT if convention == "heldout_joint_test" else FAMILY
    m = {"result_file": name, "script": script, "git_commit": COMMIT, "seed": None, "parameters": params,
         "timestamp": "2021-01-01T00:00:00", "sha256": hashlib.sha256(data).hexdigest(), "rows": rows,
         "columns": list(COLUMNS), "description": "synthetic", "exploratory": False, "prereg_id": family,
         "variant_count": None, "notes": None,
         "provenance": {"clean_run": {"name": "synthetic-run", "checkout": "x", "marker": "S2X_CLEAN_RUN"}},
         "git_dirty": False}
    for k, v in over.items():
        if k == "parameters_update":
            m["parameters"] = {**m["parameters"], **v}
        else:
            m[k] = v
    return m


def write_result(root: Path, rel: str, rows: list[dict], columns=COLUMNS, **kw: Any) -> tuple[str, str]:
    """The CSV and its manifest; returns (the CSV's sha256, the manifest's)."""
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    data = csv_bytes(rows, columns)
    p.write_bytes(data)
    m = manifest(p.name, data, len(rows), **kw)
    mb = json.dumps(m, indent=2, sort_keys=True).encode()
    Path(str(p) + MANIFEST).write_bytes(mb)
    return m["sha256"], hashlib.sha256(mb).hexdigest()


def rows_text(h_decl: str, h_record: str, exp_rel: str, h_exp: tuple[str, str], nh_rel: str,
              h_nh: tuple[str, str], *, margin: str = str(MARGIN),
              h_ho: tuple[str, str] = ("", "")) -> dict[str, str]:
    return {
        "E-9000": f"**The 3.9 pinning row (synthetic): the bankroll budget, and the no-harm margin `{margin}`.**",
        "E-9001": f"**{DESIGN}'s playbook declaration, pinned before its floor is read (synthetic)** `{DECL_FILE}` "
                  f"sha256 `{h_decl}`.",
        "E-9002": f"**{DESIGN}'s no-harm floor (synthetic)** `{nh_rel}` sha256 `{h_nh[0]}`; its manifest "
                  f"`{nh_rel}{MANIFEST}` sha256 `{h_nh[1]}`.",
        "E-9004": f"**{DESIGN} (synthetic)** carried: {DESIGN} @ {h_decl} -- {REGISTRATION} -- {h_ho[0]}; its carrying "
                  f"record `{RECORD_FILE}` sha256 `{h_record}`; its expected journey `{exp_rel}` sha256 `{h_exp[0]}`; "
                  f"its manifest `{exp_rel}{MANIFEST}` sha256 `{h_exp[1]}`; the joint held-out test's accepted result "
                  f"`{HELDOUT_FILE}` sha256 `{h_ho[0]}`; its manifest `{HELDOUT_FILE}{MANIFEST}` sha256 `{h_ho[1]}`.",
    }


def write_log(root: Path, rows: dict[str, str]) -> None:
    log = "# Decisions (synthetic)\n\n| id | date | decision | basis |\n|---|---|---|---|\n" + "".join(
        f"| {k} | 2021-01-01 | {v} | synthetic |\n" for k, v in rows.items())
    (root / "DECISIONS.md").write_bytes(log.encode())


def build_root(root: Path, decl: dict | None = None, *, expected_rows: list[dict] | None = None,
               no_harm_rows: list[dict] | None = None, expected_over: dict | None = None,
               no_harm_over: dict | None = None, bind: dict | None = None,
               edit_rows: Callable[[dict], dict] | None = None, raw: bytes | None = None,
               record_over: dict | None = None, raw_record: bytes | None = None, margin: str = str(MARGIN),
               expected_columns=COLUMNS, heldout_rows: list[dict] | None = None,
               heldout_over: dict | None = None) -> Path:
    """The synthetic root (the module docstring). `bind`: the declaration the result files are bound to (default the
    declaration itself); `edit_rows` may edit the log's rows; `raw`, `raw_record`: the files' bytes as written."""
    root = Path(root)
    decl = declaration() if decl is None else decl
    data = json_bytes(decl) if raw is None else raw
    h_decl = hashlib.sha256(data).hexdigest()
    (root / "prereg").mkdir(parents=True, exist_ok=True)
    (root / DECL_FILE).write_bytes(data)
    rec = json_bytes(record(h_decl, **(record_over or {}))) if raw_record is None else raw_record
    (root / RECORD_FILE).write_bytes(rec)
    exp_rel = decl["expected"]["file"] if isinstance(decl.get("expected"), dict) and "file" in decl["expected"] \
        else EXPECTED_FILE
    nh_rel = decl["side"]["no_harm_file"] if isinstance(decl.get("side"), dict) and "no_harm_file" in decl["side"] \
        else NO_HARM_FILE
    sha_bound = h_decl if bind is None else decl_sha(bind)
    h_exp = write_result(root, exp_rel, EXPECTED_ROWS if expected_rows is None else expected_rows,
                         columns=expected_columns,
                         **{"convention": "zero_edge", "sha_decl": sha_bound, "script": EXPECTED_SCRIPT,
                            **(expected_over or {})})
    h_nh = write_result(root, nh_rel, NO_HARM_ROWS if no_harm_rows is None else no_harm_rows,
                        **{"convention": "no_harm_real_path", "sha_decl": sha_bound, "script": NO_HARM_SCRIPT,
                           **(no_harm_over or {})})
    h_ho = write_result(root, HELDOUT_FILE, HELDOUT_ROWS if heldout_rows is None else heldout_rows,
                        **{"convention": "heldout_joint_test", "sha_decl": sha_bound, "script": HELDOUT_SCRIPT,
                           **(heldout_over or {})})
    rows = rows_text(h_decl, hashlib.sha256(rec).hexdigest(), exp_rel, h_exp, nh_rel, h_nh, margin=margin,
                     h_ho=h_ho)
    if edit_rows is not None:
        rows = edit_rows(rows)
    write_log(root, rows)
    return root


def _git(root: Path, *args: str) -> str:
    p = subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True, timeout=120)
    if p.returncode:
        raise RuntimeError(f"git {args}: {p.stderr}")
    return p.stdout.strip()


def git_root(root: Path, *, floor: str = "pin", journey: str = "pin") -> Path:
    """The synthetic root as a git history (C2-2, C3-4, N-c3-3): a first commit with no pin; then the 3.9 row and the
    declaration's pinning row; a side branch off the pin that is never merged; then the results and the rest of the
    log on the main line, and a later row citing the pin again. Each of the floor's and the journey's manifests names
    its run's commit: `pin` (the pin's), `before` (the commit before it) or `side` (the unmerged branch's)."""
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    _git(root, "init", "-q")
    for k, v in (("user.email", "synthetic@example.invalid"), ("user.name", "synthetic"), ("core.autocrlf", "false"),
                 ("commit.gpgsign", "false")):
        _git(root, "config", k, v)
    (root / "README").write_bytes(b"synthetic\n")
    _git(root, "add", "README")
    _git(root, "commit", "-q", "-m", "start")
    before = _git(root, "rev-parse", "HEAD")
    decl = declaration()
    data = json_bytes(decl)
    h_decl = hashlib.sha256(data).hexdigest()
    (root / "prereg").mkdir(exist_ok=True)
    (root / DECL_FILE).write_bytes(data)
    first_rows = rows_text(h_decl, "", "", ("", ""), "", ("", ""))
    write_log(root, {k: first_rows[k] for k in ("E-9000", "E-9001")})
    _git(root, "add", "DECISIONS.md", DECL_FILE)
    _git(root, "commit", "-q", "-m", "pin the declaration")
    pinned = _git(root, "rev-parse", "HEAD")
    _git(root, "checkout", "-q", "-b", "side")
    (root / "SIDE").write_bytes(b"an unmerged branch\n")
    _git(root, "add", "SIDE")
    _git(root, "commit", "-q", "-m", "a run on a branch never merged")
    side = _git(root, "rev-parse", "HEAD")
    _git(root, "checkout", "-q", "-")
    commits = {"pin": pinned, "before": before, "side": side}
    build_root(root, expected_over={"git_commit": commits[journey]}, no_harm_over={"git_commit": commits[floor]})
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "the floor, the journey and the carrying row")
    log = (root / "DECISIONS.md").read_bytes().decode()           # a later row citing the pin again: the first
    log += f"| E-9005 | 2021-01-02 | a later note citing `{DECL_FILE}` sha256 `{h_decl}` | synthetic |\n"  # pin counts
    (root / "DECISIONS.md").write_bytes(log.encode())
    _git(root, "add", "DECISIONS.md")
    _git(root, "commit", "-q", "-m", "a later row citing the pin")
    return root


def verify_standin(path):
    """The vendored `verify_result`'s check (`propedge.reporting.results.verify_result`: the file and its manifest
    exist and the file's plain sha256 is the manifest's), for the in-process tests, which must not put the vendored
    tree on `sys.path`; the subprocess test (`results`) runs the real one."""
    p = Path(path)
    mp = Path(str(p) + MANIFEST)
    if not p.is_file() or not mp.is_file():
        return False, "missing"
    want = json.loads(mp.read_bytes())["sha256"]
    got = hashlib.sha256(p.read_bytes()).hexdigest()
    return (got == want), ("verified" if got == want else "modified")


# ------------------------------------------------------------------------------------------------ the day: calendar, bars, router

DAYS = ("2021-03-11", "2021-03-12", "2021-03-15", "2021-03-16", "2021-03-17", "2021-03-18", "2021-03-19",
        "2021-04-05", "2021-04-06", "2021-04-07")
BASE, HIGH, LOW = 18000.0, 18100.0, 17900.0
RTH = (931, 1320)                     # the walker's columns of the bars stamped 08:30 .. 14:59
ACCOUNTS = ("ts_a", "ts_b", "ts_c")


def day_index(day: str) -> int:
    return DAYS.index(day)


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


def event_slot(day: str, session: str) -> int:
    """The slot of the fixture's breakout in `session` on `day`: ten minutes after that date's local open."""
    from extended import day_calendar as DC

    return DC.anchored_starts(date.fromisoformat(day))[session] + 10


def history(*, no_0829=()):
    """The synthetic bars (the module docstring); `no_0829`: days without their bar stamped 08:29."""
    import numpy as np

    from extended import triggers as T

    n = len(DAYS)
    o, h, l, c = (np.full((n, 1441), BASE) for _ in range(4))
    for x in (o, h, l, c):
        x[:, 0] = np.nan
    h[:, RTH[0]:RTH[1] + 1] = HIGH
    l[:, RTH[0]:RTH[1] + 1] = LOW
    c[:, RTH[1]] = HIGH - 50.0                                   # the previous day's close (pdc) above the reference
    for d in ("2021-03-12", "2021-03-16", "2021-03-17"):
        i = day_index(d)
        for sess in ("asia", "london"):
            j = event_slot(d, sess)
            l[i, j] = c[i, j] = BASE - 10.0                      # brk30- ten minutes into the session
    for d in ("2021-03-16", "2021-03-17", "2021-03-19"):
        i = day_index(d)
        h[i, 1101] = c[i, 1101] = HIGH + 10.0                    # brk30+ at 11:21 CT
    l[day_index("2021-04-05"), RTH[0]:RTH[1] + 1] = BASE         # 2021-04-06's pd low at the reference
    for d in no_0829:
        i = day_index(d)
        for x in (o, h, l, c):
            x[i, 930] = np.nan
    return T.History.from_arrays(DAYS, ["NQM1"] * n, o, h, l, c)


def scrambled(hist, i: int, at: int, seed: int):
    """`hist` with every bar not closed at `at` on day `i`, and every later day, replaced by a random walk (explicit
    seed): the feature-rules shift-invariance test's input."""
    import numpy as np

    from extended import triggers as T

    rng = np.random.default_rng(seed)
    arrs = [np.array(x, copy=True) for x in (hist.o, hist.h, hist.l, hist.c)]
    walk = BASE + np.cumsum(rng.normal(0.0, 5.0, size=arrs[0].shape), axis=1)
    for x in arrs:
        x[i, at + 1:] = walk[i, at + 1:]
        x[i + 1:, 1:] = walk[i + 1:, 1:]
    return T.History(hist.days, hist.contract, *arrs)


def router(decl: dict | None = None, **busy: int):
    """The user's router under the declaration's rotation; `busy`: account -> its last busy minute."""
    from extended import router as R

    decl = declaration() if decl is None else decl
    rot = decl["rotation"]
    r = R.Router(R.Routing(rot["rule"], {k: tuple(v) for k, v in rot.get("pools", {}).items()}))
    for acct, t in busy.items():
        r.last_busy[("topstep", acct)] = int(t)
    return r


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
    PB._run_after_pin = lambda root, text, commit: True       # the pin order has its own test (git_root)
    if argv[0] == "render":
        print(hashlib.sha256(PB.render_playbook(PB.load_carried(RECORD_FILE, root=Path(argv[1]))).text.encode())
              .hexdigest())
        return 0
    if argv[0] == "results":
        import pandas as pd

        from extended.results import write_result as vendored_write

        out: dict[str, str] = {}
        base = Path(argv[1])
        sha = decl_sha(declaration())

        def attempt(name: str, root: Path) -> None:
            try:
                c = PB.load_carried(RECORD_FILE, root=root)
                out[name] = "accepted:" + c.expected.commit
            except PB.PlaybookRefused as e:
                out[name] = "refused:" + str(e)[:120]

        def real_root(name: str, *, clean: bool, exp_params: dict | None = None, exploratory: bool = False,
                      tamper: bool = False) -> Path:
            root = base / name
            build_root(root)                                     # the log and the two JSON files, then real results
            hashes: dict[str, tuple[str, str]] = {}
            for rel, rows, conv, script in ((EXPECTED_FILE, EXPECTED_ROWS, "zero_edge", EXPECTED_SCRIPT),
                                            (NO_HARM_FILE, NO_HARM_ROWS, "no_harm_real_path", NO_HARM_SCRIPT)):
                p = root / rel
                p.unlink()
                Path(str(p) + MANIFEST).unlink()
                params = {"design_id": DESIGN, "convention": conv, "declaration_file": DECL_FILE,
                          "declaration_sha256": sha}
                if conv == "no_harm_real_path":
                    params["margin"] = MARGIN
                if rel == EXPECTED_FILE and exp_params is not None:
                    params = exp_params
                csv, mp = vendored_write(pd.DataFrame(rows, columns=list(COLUMNS)), p.stem, script=script,
                                         seed=None, parameters=params, results_dir=p.parent, require_seed=False,
                                         exploratory=exploratory and rel == EXPECTED_FILE, prereg_id=FAMILY,
                                         description="synthetic test rows; no randomness")
                if clean:                                   # as a clean run of a named commit records it
                    m = json.loads(mp.read_bytes())
                    m.update(git_commit=COMMIT, git_dirty=False,
                             provenance={"clean_run": {"name": "synthetic-run", "checkout": "x",
                                                       "marker": "S2X_CLEAN_RUN"}})
                    mp.write_bytes(json.dumps(m, indent=2, sort_keys=True).encode())
                hashes[rel] = (json.loads(mp.read_bytes())["sha256"], hashlib.sha256(mp.read_bytes()).hexdigest())
                if tamper and rel == EXPECTED_FILE:
                    csv.write_bytes(csv.read_bytes().replace(b"37.5", b"12.5"))
            rec = (root / RECORD_FILE).read_bytes()
            ho = Path(str(root / HELDOUT_FILE) + MANIFEST)
            h_ho = (json.loads(ho.read_bytes())["sha256"], hashlib.sha256(ho.read_bytes()).hexdigest())
            write_log(root, rows_text(sha, hashlib.sha256(rec).hexdigest(), EXPECTED_FILE, hashes[EXPECTED_FILE],
                                      NO_HARM_FILE, hashes[NO_HARM_FILE], h_ho=h_ho))
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
