"""Q-48: every identity's real-data read goes through the reader (`extended/reader.py`, purpose `identity`), and is
ledgered only inside a clean run (E-026, the lead's rule: worktree and suite runs stay clean).

What is asserted, for each of the five identity scripts (`identity/*.py`):

* every mode that has Stage 2's engine read the bars or the atlas calls `extended.reader.authorise_engine_read` once,
  from its `main`, before any of the engine's work, naming the decision row that registered the identity (E-004 the
  gate rows and E-010 U1's start rows for `stage2_identity`, E-011 `walker_identity`, E-024 `user_beside_identity` and
  `breakeven_identity`, E-028 `gate_identity`), the whole development window, and the files the engine opens in that
  mode; a mode that reads no data (the synthetic ones, the walker's substitution check) calls it not at all;
* **outside a clean run** (`S2X_CLEAN_RUN` unset) no ledger file appears, whatever runs;
* **inside a simulated clean run** exactly one line is appended per identity run of a real-data mode, none for the
  others: the identity's row, purpose `identity`, the window, each file with its hash, the script and the clean run;
* a run whose row is missing from the decision log, or does not mention an identity, is refused -- exit 3, none of the
  engine's work started, no line -- outside a clean run and inside one (the authorisation is checked everywhere); the
  same runs from a script outside `identity/` are refused the same way;
* the rows the scripts name exist in this repository's `DECISIONS.md` and mention an identity.

How. Each identity's `main` runs in a child process (the vendored tree goes on `sys.path` only in a process of its
own, CLAUDE.md), on a temporary tree -- a git repository at `<tmp>/runs/<name>` holding the identities' decision rows
copied from this repository's log and small stand-in files at the paths of Stage 2's bars and atlas tables (never
parsed) -- with the reader pointed at that tree and the engine's work replaced by recorders, so nothing vendored runs
and the real bars, atlas and ledger are never opened. The driver is a script inside the tree (`identity/` or
`scripts/`), so the reader's script check sees it as it would see an identity.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import reader as R  # noqa: E402  (importing the reader touches no sys.path, imports no engine)

A1E, A1D = "vendor/stage2/data/atlas/A1/events.parquet", "vendor/stage2/data/atlas/A1/days.parquet"
A3W = "vendor/stage2/data/atlas/A3/walks.parquet"
BARS = "vendor/stage2/data/bars/NQ/bars.parquet"
A1A3 = (A1E, A1D, A3W)
ALL4 = (A1E, A1D, A3W, BARS)
DATA = ALL4

#: the decision rows that registered each identity (the brief; E-004/E-010 split by part, see stage2_identity.py)
ROWS = ("E-004", "E-010", "E-011", "E-024", "E-028")

#: (script, argv, the row it must name or None when it reads no data, the files, the engine's work it runs)
RUNS = (
    ("stage2_identity", ["--paths", "4"], "E-004", ALL4, ["p14", "p16"]),
    ("stage2_identity", ["--only", "p14", "--paths", "4"], "E-004", A1A3, ["p14"]),
    ("stage2_identity", ["--only", "p16", "--paths", "4"], "E-004", ALL4, ["p16"]),
    ("stage2_identity", ["--only", "u1", "--u1-starts", "4"], "E-010", ALL4, ["u1"]),
    ("stage2_identity", ["--only", "u1", "--u1-configs", "p14", "--u1-starts", "4"], "E-010", A1A3, ["u1"]),
    ("stage2_identity", ["--paths", "4", "--u1-starts", "all", "--u1-configs", "p15"], "E-010", ALL4,
     ["p14", "p16", "u1"]),
    ("walker_identity", ["--synthetic"], None, (), ["synthetic"]),
    ("walker_identity", ["--substitution"], None, (), ["substitution"]),
    ("walker_identity", ["--smoke-days", "10"], "E-011", (A1E, A1D, BARS), ["smoke"]),
    ("walker_identity", [], "E-011", ALL4, ["full"]),
    ("user_beside_identity", ["--synthetic"], None, (), ["synthetic"]),
    ("user_beside_identity", ["--u1-starts", "4"], "E-024", ALL4, ["u1"]),
    ("user_beside_identity", ["--u1-starts", "4", "--configs", "p14"], "E-024", A1A3, ["u1"]),
    ("user_beside_identity", ["--u1-starts", "4", "--control", "denial_50"], "E-024", ALL4, ["u1"]),
    ("user_beside_identity", ["--synthetic", "--u1-starts", "all", "--configs", "p14,p15,p16"], "E-024", ALL4,
     ["synthetic", "u1"]),
    ("breakeven_identity", ["--synthetic"], None, (), ["synthetic"]),
    ("breakeven_identity", ["--substitution"], "E-024", A1A3, ["substitution"]),
    ("breakeven_identity", ["--smoke-days", "10"], "E-024", ALL4, ["smoke"]),
    ("breakeven_identity", ["--synthetic", "--substitution", "--smoke-days", "10"], "E-024", ALL4,
     ["synthetic", "substitution", "smoke"]),
    ("gate_identity", ["--synthetic"], None, (), ["synthetic"]),
    ("gate_identity", ["--paths", "4"], "E-028", ALL4, ["p14", "p16"]),
    ("gate_identity", ["--paths", "4", "--only", "p14"], "E-028", A1A3, ["p14"]),
    ("gate_identity", ["--paths", "4", "--only", "p16", "--cls", "none"], "E-028", ALL4, ["p16"]),
    ("gate_identity", ["--paths", "500", "--workers", "1", "--cls", "all"], "E-028", ALL4, ["p14", "p16"]),   # Q-71
)
SCRIPTS = ("stage2_identity", "walker_identity", "user_beside_identity", "breakeven_identity", "gate_identity")
#: one real-data run a script, for the refusals
FIRST_REAL = {s: next(r for r in RUNS if r[0] == s and r[2] is not None) for s in SCRIPTS}

# ------------------------------------------------------------------------------------------------------- the driver

DRIVER = r'''
"""Q-48's test driver (tests/test_identity_reads.py): each identity's main on this temporary tree, the engine's work
replaced by recorders, the reader pointed at this tree. Prints one JSON line."""
import contextlib, io, json, os, subprocess, sys
from pathlib import Path

cfg = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
REPO = Path(cfg["repo"])
TREE = Path(__file__).resolve().parent.parent
for p in (str(REPO), str(REPO / "identity")):
    sys.path.insert(0, p)
os.environ.pop("S2X_CLEAN_RUN", None)
os.environ.pop("S2X_RUN_ID", None)

from extended import reader as R

R.ROOT = TREE                                   # the reader's tree: this one (DECISIONS.md, git, the ledger)
R.RUNS_DIR = TREE.parent                        # so this tree is the simulated clean run's checkout
VENDOR = TREE / "vendor" / "stage2"
LEDGER = TREE / "results" / "read_ledger.jsonl"
events = []
_real = R.authorise


def recording(start, end, **k):
    # `authorise` (which `authorise_engine_read` calls first) is recorded, not `authorise_engine_read` itself: a
    # wrapper there would stand between the identity's main and the ledger line's `caller`
    events.append({"event": "authorise", "start": str(start), "end": str(end), "declaration": k.get("declaration"),
                   "purpose": k.get("purpose")})
    return _real(start, end, **k)


R.authorise = recording


def work(name, value):
    def f(*a, **k):
        events.append({"event": "work", "name": name})
        return value(*a, **k) if callable(value) else value
    f.__name__ = name
    return f


def u1_rows(configs, problems=()):
    return {c: {"problems": list(problems), "starts": 4, "of": 4, "seconds": 0.0, "columns": 68,
                "arms": ("verdict", "point"), "trades_check": "a recorder"} for c in configs}


import stage2_identity as SI
import walker_identity as WI
import user_beside_identity as UB
import breakeven_identity as BE
import gate_identity as GI

SI.DEFAULT_ROOT = VENDOR
SI._setup = work("setup", None)
SI.p14_problems = work("p14", [])
SI.p16_problems = work("p16", [])
SI.u1_problems = work("u1", lambda starts, workers, configs=SI.U1_CONFIGS: u1_rows(configs))
SI.peak_memory = lambda: None
WI.VENDOR = VENDOR
WI._setup = work("setup", None)
WI.synthetic = work("synthetic", [])
WI.substitution_problems = work("substitution", [])
WI.smoke = work("smoke", [])
WI.full = work("full", [])
WI.peak_gb = lambda: None
UB.VENDOR = VENDOR
UB.synthetic_problems = work("synthetic", ([], {"denied": [], "forfeited_paths": 0, "payouts_forfeited": 0,
                                                "no_denial_paths": 0}))
UB.u1_problems = work("u1", lambda configs, starts, workers, response="off":
                      u1_rows(configs, () if response == "off" else ("a recorder: the response differs",)))
BE.VENDOR = VENDOR
BE.synthetic_problems = work("synthetic", [])
BE.substitution_problems = work("substitution", [])
BE.smoke_problems = work("smoke", [])
GI.VENDOR = VENDOR
GI.synthetic_problems = work("synthetic", {})
GI.p14_problems = work("p14", lambda n, workers, arms: {a: [] for a in arms})
GI.p16_problems = work("p16", lambda n, workers, arms: {a: [] for a in arms})
MODULES = {"stage2_identity": SI, "walker_identity": WI, "user_beside_identity": UB, "breakeven_identity": BE,
           "gate_identity": GI}


def lines():
    return LEDGER.read_text(encoding="utf-8").splitlines() if LEDGER.exists() else []


def git(*args):
    subprocess.run(["git", "-C", str(TREE), *args], check=True, capture_output=True)


out = []
for phase in cfg["phases"]:
    if phase.get("decisions") is not None:
        (TREE / "DECISIONS.md").write_bytes(phase["decisions"].encode("utf-8"))
        git("add", "DECISIONS.md")
        git("commit", "-q", "-m", "the decision log for phase " + phase["name"])
    for k in ("S2X_CLEAN_RUN", "S2X_RUN_ID"):
        os.environ.pop(k, None)
    os.environ.update(phase.get("env") or {})
    for script, argv in phase["runs"]:
        events.clear()
        before = lines()
        buf = io.StringIO()
        rec = {"phase": phase["name"], "script": script, "argv": argv}
        try:
            with contextlib.redirect_stdout(buf):
                rec["rc"] = MODULES[script].main(list(argv))
        except BaseException as e:                       # noqa: BLE001 -- recorded, the test reads it
            rec["error"] = type(e).__name__ + ": " + str(e)[:600]
        after = lines()
        rec.update(stdout=buf.getvalue()[-3000:], events=list(events), ledger_exists=LEDGER.exists(),
                   lines_before=len(before), new=[json.loads(x) for x in after[len(before):]],
                   prefix_kept=after[:len(before)] == before)
        out.append(rec)
print(json.dumps(out))
'''


# ------------------------------------------------------------------------------------------------------ the tree


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def real_rows() -> dict[str, str]:
    text = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    return {r: R.decision_row(text, r) for r in ROWS}


def log(rows: dict[str, str]) -> str:
    head = "# Decisions (a temporary tree, Q-48's tests)\n\n| id | date | decision | basis |\n|---|---|---|---|\n"
    return head + "".join(line + "\n" for line in rows.values())


NO_IDENTITY = log({r: f"| {r} | 2026-11-16 | **A row about nothing in particular** | test |" for r in ROWS})
MISSING = log({"E-904": "| E-904 | 2026-11-16 | **A row about nothing in particular** | test |"})


def make_tree(base: Path, name: str, where: str, decisions: str) -> Path:
    """A git repository at `<base>/runs/<name>`: the decision log, the driver at `<where>/q48_driver.py`, a Stage 2
    tree with an (empty) engine folder and stand-in data files (git-ignored, as the real ones are) listed with their
    hashes in a data manifest; everything else committed."""
    t = base / "runs" / name
    (t / where).mkdir(parents=True)
    (t / where / "q48_driver.py").write_text(DRIVER, encoding="utf-8")
    (t / "DECISIONS.md").write_bytes(decisions.encode("utf-8"))
    (t / "vendor" / "stage2" / "propedge").mkdir(parents=True)
    (t / "vendor" / "stage2" / "propedge" / "README.md").write_text("a stand-in for the engine's folder\n",
                                                                     encoding="utf-8")
    manifest = []
    for rel in DATA:
        p = t / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(f"a stand-in for {rel} (Q-48's tests; never parsed)\n".encode("utf-8"))
        manifest.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {rel.removeprefix('vendor/stage2/')}\n")
    (t / "vendor" / "DATA_MANIFEST_stage2.sha256").write_text("".join(manifest), encoding="utf-8")
    (t / ".gitignore").write_text("vendor/stage2/data/\n", encoding="utf-8")
    git(t, "init", "-q", "-b", "master")
    git(t, "config", "user.email", "t@example.invalid")
    git(t, "config", "user.name", "t")
    git(t, "config", "core.autocrlf", "false")
    git(t, "add", "-A")
    git(t, "commit", "-q", "-m", "the temporary tree")
    return t


def drive(t: Path, where: str, phases: list[dict]) -> list[dict]:
    cfg = t.parent.parent / f"{t.name}.json"
    cfg.write_text(json.dumps({"repo": str(ROOT), "phases": phases}), encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k not in ("S2X_CLEAN_RUN", "S2X_RUN_ID")}
    env.update({"OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"})
    r = subprocess.run([sys.executable, f"{where}/q48_driver.py", str(cfg)], cwd=t, capture_output=True, text=True,
                       timeout=600, env=env)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    return json.loads(r.stdout.strip().splitlines()[-1])


def clean_env(name: str) -> dict[str, str]:
    return {"S2X_CLEAN_RUN": name, "S2X_RUN_ID": f"{name}@q48-sim"}


@pytest.fixture(scope="module")
def results(tmp_path_factory) -> dict[str, list[dict]]:
    """Both drivers' runs, once for the module: the identity driver (outside, inside, then the two wrong logs, each
    outside and inside) and the driver under `scripts/` (inside and outside)."""
    base = tmp_path_factory.mktemp("q48")
    valid = log(real_rows())
    real = [[s, a] for s, a, *_ in RUNS]
    refuse = [[s, FIRST_REAL[s][1]] for s in SCRIPTS]
    t = make_tree(base, "q48-ident", "identity", valid)
    ident = drive(t, "identity", [
        {"name": "outside", "env": {}, "runs": real},
        {"name": "inside", "env": clean_env(t.name), "runs": real},
        {"name": "no_identity_outside", "decisions": NO_IDENTITY, "env": {}, "runs": refuse},
        {"name": "no_identity_inside", "env": clean_env(t.name), "runs": refuse},
        {"name": "missing_outside", "decisions": MISSING, "env": {}, "runs": refuse},
        {"name": "missing_inside", "env": clean_env(t.name), "runs": refuse},
    ])
    s = make_tree(base, "q48-scripts", "scripts", valid)
    other = drive(s, "scripts", [
        {"name": "scripts_inside", "env": clean_env(s.name), "runs": refuse},
        {"name": "scripts_outside", "env": {}, "runs": refuse},
    ])
    return {"ident": ident, "scripts": other, "ident_tree": [str(t)], "scripts_tree": [str(s)]}


def phase(results: dict, which: str, name: str) -> list[dict]:
    return [r for r in results[which] if r["phase"] == name]


def explain(r: dict) -> str:
    return f"{r['script']} {r['argv']} ({r['phase']}): rc {r.get('rc')} {r.get('error', '')}\n{r['stdout']}"


def authorisations(r: dict) -> list[dict]:
    return [e for e in r["events"] if e["event"] == "authorise"]


def work_done(r: dict) -> list[str]:
    return [e["name"] for e in r["events"] if e["event"] == "work" and e["name"] != "setup"]


def authorised_first(r: dict) -> bool:
    """The one authorisation comes before any of the engine's work (putting the engine on `sys.path` included)."""
    at = [i for i, e in enumerate(r["events"]) if e["event"] == "authorise"]
    work = [i for i, e in enumerate(r["events"]) if e["event"] == "work"]
    return len(at) == 1 and bool(work) and at[0] < min(work)


# -------------------------------------------------------------------------------------------------------- the tests


def test_the_rows_the_identities_name_exist_and_mention_an_identity():
    rows = real_rows()
    for r in ROWS:
        assert rows[r] is not None, f"{r} is no decision row of DECISIONS.md"
        assert "identit" in rows[r].lower(), f"{r}'s row does not mention an identity"
    named = {row for _, _, row, _, _ in RUNS if row}
    assert named == set(ROWS), "every row is exercised, and no other"


@pytest.mark.parametrize("i", range(len(RUNS)), ids=[f"{s}:{' '.join(a) or 'full'}" for s, a, *_ in RUNS])
def test_outside_a_clean_run_the_read_is_checked_and_nothing_is_ledgered(results, i):
    script, argv, row, files, work = RUNS[i]
    runs = phase(results, "ident", "outside")
    r = runs[i]
    assert (r["script"], r["argv"]) == (script, argv)
    assert r.get("rc") == 0 and "error" not in r, explain(r)
    assert work_done(r) == work, explain(r)
    a = authorisations(r)
    assert len(a) == (1 if row else 0), explain(r)
    if row:
        assert a[0]["declaration"] == row and a[0]["purpose"] == "identity"
        assert (a[0]["start"], a[0]["end"]) == ("2020-01-02", "2026-07-16")
        assert authorised_first(r), explain(r)
    # no ledger file appears outside a clean run -- after this run, nor after any earlier one
    assert not r["ledger_exists"] and r["new"] == [], explain(r)


@pytest.mark.parametrize("i", range(len(RUNS)), ids=[f"{s}:{' '.join(a) or 'full'}" for s, a, *_ in RUNS])
def test_inside_a_clean_run_one_line_per_identity_run(results, i):
    script, argv, row, files, work = RUNS[i]
    r = phase(results, "ident", "inside")[i]
    tree = Path(results["ident_tree"][0])
    assert (r["script"], r["argv"]) == (script, argv)
    assert r.get("rc") == 0 and "error" not in r, explain(r)
    assert work_done(r) == work, explain(r)
    assert r["prefix_kept"], "the ledger only grows"
    if row is None:
        assert r["new"] == [] and authorisations(r) == [], "a mode that reads no data writes no line"
        return
    assert len(r["new"]) == 1, explain(r)
    assert authorised_first(r) and authorisations(r)[0]["declaration"] == row, explain(r)
    line = r["new"][0]
    assert line["purpose"] == "identity" and line["repeat"] is None
    assert line["declaration"] == {"ref": row, "sha256": None, "kind": "identity"}
    assert line["dates"] == {"start": "2020-01-02", "end": "2026-07-16", "blocks": ["choice", "judged"],
                             "judged_first": "2024-01-02", "judged_last": "2026-07-16"}
    got = [f["path"] for f in line["what"]["files"]]
    assert sorted(got) == sorted(files) and len(got) == len(set(got)), (got, files)
    for f in line["what"]["files"]:
        assert f["sha256"] == hashlib.sha256((tree / f["path"]).read_bytes()).hexdigest() and f["in_data_manifest"]
    assert line["what"]["kind"] == "engine" and line["what"]["columns"] is None and line["what"]["description"]
    who = line["who"]
    assert who["script"] == "identity/q48_driver.py"
    assert who["clean_run"] == tree.name and who["run_id"] == f"{tree.name}@q48-sim" and who["dirty"] is False
    assert who["commit"] == git(tree, "rev-list", "--max-parents=0", "HEAD"), "the tree's first commit made it"
    assert f"identity/{script}.py:" in who["caller"].replace("\\", "/") and who["caller"].endswith(":main"), \
        f"the call is in {script}'s main: {who['caller']}"


def test_inside_a_clean_run_the_lines_are_one_per_real_run_in_order(results):
    runs = phase(results, "ident", "inside")
    want = [row for _, _, row, _, _ in RUNS if row]
    assert [line["declaration"]["ref"] for r in runs for line in r["new"]] == want
    tree = Path(results["ident_tree"][0])
    assert len(R.read_ledger(tree / R.LEDGER_REL)) == len(want), "the ledger verifies and holds those lines only"


@pytest.mark.parametrize("name", ["no_identity_outside", "no_identity_inside", "missing_outside", "missing_inside"])
@pytest.mark.parametrize("script", SCRIPTS)
def test_a_row_that_does_not_authorise_the_identity_is_refused(results, name, script):
    runs = phase(results, "ident", name)
    r = next(x for x in runs if x["script"] == script)
    why = "does not mention an identity" if name.startswith("no_identity") else "no decision row"
    assert r.get("rc") == 3 and "error" not in r, explain(r)
    assert "REFUSED" in r["stdout"] and why in r["stdout"], explain(r)
    assert work_done(r) == [] and not [e for e in r["events"] if e["event"] == "work"], \
        "nothing of the engine's work starts"
    assert r["new"] == [] and r["prefix_kept"], "a refused read writes nothing"
    assert len(authorisations(r)) == 1 and authorisations(r)[0]["declaration"] == FIRST_REAL[script][2]


@pytest.mark.parametrize("name", ["scripts_inside", "scripts_outside"])
@pytest.mark.parametrize("script", SCRIPTS)
def test_the_call_from_a_script_outside_identity_is_refused(results, name, script):
    r = next(x for x in phase(results, "scripts", name) if x["script"] == script)
    assert r.get("rc") == 3 and "error" not in r, explain(r)
    assert "REFUSED" in r["stdout"] and "identity/" in r["stdout"], explain(r)
    assert not [e for e in r["events"] if e["event"] == "work"], "nothing of the engine's work starts"
    assert not r["ledger_exists"] and r["new"] == [], "no ledger file for a refused read"
