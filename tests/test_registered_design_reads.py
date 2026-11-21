"""Q-58 (E-037): the three readings scripts re-read Stage 2's registered designs through the reader (purpose
`registered_design`), ledgered only inside a clean run.

What is asserted, for `scripts/user_beside.py` (Q-17), `scripts/breakeven_fidelity.py` (Q-20),
`scripts/p14_validation.py` (Q-18) and `scripts/breakeven_fidelity_2.py` (Q-132, under E-024, which names P-15 too):

* each run calls `extended.reader.authorise_engine_read` once, from its `main`, before any of the engine's work, with
  purpose `registered_design`, the decision row that admits it (E-024 for Q-17 and Q-20, E-026 for Q-18), the designs it
  reads (P-14, P-15, P-16 -- the run's own subset), the whole development window and the files the engine opens (A1's
  events and days and A3's cached walk; the bars wherever a walk is made afresh -- P-15's and P-16's coins, and P-14's
  A3 frame re-walked by Q-20);
* Q-158 (the reader's held-out rule 3): the whole window reaches the held-out years, so a run is admitted only under a
  row carrying a read token that names it (here the real rows with the token added, the process script the driver),
  inside a clean run; outside one it is refused (exit 3, nothing ledgered), and the real rows as they stand, without
  the token, refuse every reading inside one too;
* outside a clean run no ledger file appears; inside a simulated one exactly one line a run (its row, purpose, the
  designs, the window, each file with its hash, the script, the clean run, a `caller` in the script's `main`);
* a row missing from the decision log, or present but not naming the run's designs, is refused (the script prints
  REFUSED, exits 3, starts nothing), inside a clean run and outside it; the same runs from a script under `identity/`
  are refused; a design a script does not read is refused by the script before anything (exit 2);
* the rows the scripts name exist in this repository's `DECISIONS.md` and name their designs.

How: as `tests/test_identity_reads.py` -- each script's `main` in a child process on a temporary git tree at
`<tmp>/runs/<name>` (the real rows copied, small stand-in files at the data paths, never parsed), the reader pointed at
that tree, and the first step of the engine's work after the authorisation replaced by a recorder that stops the run.
Nothing vendored runs; the real bars, atlas and ledger are never opened.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import reader as R  # noqa: E402
import heldout_verdict_rows as VR  # noqa: E402  (Q-194b: the held-out test's verdict rows)

A1E, A1D = "vendor/stage2/data/atlas/A1/events.parquet", "vendor/stage2/data/atlas/A1/days.parquet"
A3W = "vendor/stage2/data/atlas/A3/walks.parquet"
BARS = "vendor/stage2/data/bars/NQ/bars.parquet"
A1A3 = (A1E, A1D, A3W)
ALL4 = (A1E, A1D, A3W, BARS)

#: the rows that admit the readings (E-037) and the designs each must name
ROWS = {"E-024": ("P-14", "P-15", "P-16"), "E-026": ("P-14",)}

#: (script, argv, the row, the designs, the files, the recorder that stops the run) -- None: refused before (exit 2)
RUNS = (
    ("user_beside", [], "E-024", ("P-14", "P-15", "P-16"), ALL4, "u1_reference"),
    ("user_beside", ["--check", "--starts", "4", "--designs", "p14"], "E-024", ("P-14",), A1A3, "u1_reference"),
    ("user_beside", ["--check", "--starts", "4", "--designs", "p15,p16"], "E-024", ("P-15", "P-16"), ALL4,
     "u1_reference"),
    ("breakeven_fidelity", [], "E-024", ("P-14", "P-16"), ALL4, "u1_reference"),
    ("breakeven_fidelity", ["--check", "--starts", "4", "--paths", "4", "--designs", "p14"], "E-024", ("P-14",), ALL4,
     "u1_reference"),
    ("p14_validation", ["--check"], "E-026", ("P-14",), A1A3, "build_p14"),
    ("p14_validation", ["--check", "--part", "B1"], "E-026", ("P-14",), A1A3, "build_p14"),
    ("user_beside", ["--check", "--designs", "p13"], None, (), (), None),
    ("breakeven_fidelity", ["--check", "--designs", "p15"], None, (), (), None),
    ("breakeven_fidelity_2", [], "E-024", ("P-14", "P-15", "P-16"), ALL4, "u1_reference"),
    ("breakeven_fidelity_2", ["--check", "--starts", "4", "--paths", "4", "--designs", "p15"], "E-024", ("P-15",),
     ALL4, "u1_reference"),
    ("breakeven_fidelity_2", ["--check", "--designs", "p13"], None, (), (), None),
)
SCRIPTS = ("user_beside", "breakeven_fidelity", "p14_validation", "breakeven_fidelity_2")
FIRST = {s: next(r for r in RUNS if r[0] == s and r[2]) for s in SCRIPTS}

DRIVER = r'''
"""Q-58's test driver (tests/test_registered_design_reads.py): each readings script's main on this temporary tree,
the reader pointed at it, the engine's first step after the authorisation a recorder that stops the run."""
import contextlib, importlib.util, io, json, os, subprocess, sys
from pathlib import Path

cfg = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
REPO = Path(cfg["repo"])
TREE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
os.environ.pop("S2X_CLEAN_RUN", None)
os.environ.pop("S2X_RUN_ID", None)

from extended import reader as R

R.ROOT = TREE
R.RUNS_DIR = TREE.parent
VENDOR = TREE / "vendor" / "stage2"
LEDGER = TREE / "results" / "read_ledger.jsonl"
events = []
_real = R.authorise


def recording(start, end, **k):
    events.append({"event": "authorise", "start": str(start), "end": str(end), "declaration": k.get("declaration"),
                   "purpose": k.get("purpose"), "design": k.get("design")})
    return _real(start, end, **k)


R.authorise = recording


class Stopped(Exception):
    pass


def stop(name):
    def f(*a, **k):
        events.append({"event": "work", "name": name})
        raise Stopped(name)
    f.__name__ = name
    return f


def load(name):
    spec = importlib.util.spec_from_file_location(f"q58_{name}", REPO / "scripts" / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.VENDOR = VENDOR
    return m


MODULES = {n: load(n) for n in ("user_beside", "breakeven_fidelity", "p14_validation", "breakeven_fidelity_2")}
MODULES["user_beside"].I.u1_reference = stop("u1_reference")      # user_beside_identity: both Q-17's and Q-20's
MODULES["p14_validation"].build_p14 = stop("build_p14")


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
        except Stopped as e:
            rec["stopped"] = str(e)
        except BaseException as e:                       # noqa: BLE001 -- recorded, the test reads it
            rec["error"] = type(e).__name__ + ": " + str(e)[:600]
        after = lines()
        rec.update(stdout=buf.getvalue()[-3000:], events=list(events), ledger_exists=LEDGER.exists(),
                   new=[json.loads(x) for x in after[len(before):]], prefix_kept=after[:len(before)] == before)
        out.append(rec)
print(json.dumps(out))
'''


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def real_rows() -> dict[str, str | None]:
    text = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    return {r: R.decision_row(text, r) for r in ROWS}


def log(rows: dict[str, str]) -> str:
    head = "# Decisions (a temporary tree, Q-58's tests)\n\n| id | date | decision | basis |\n|---|---|---|---|\n"
    # Q-194b: after the joint held-out test's verdict, so the reader's rule 3 decides each read here
    return head + "".join(line + "\n" for line in [*rows.values(), *VR.VERDICT_ROWS])


def tokened(rows: dict[str, str | None]) -> dict[str, str]:
    """Q-158 (the reader's held-out rule 3): each real row with a read token naming its designs, as the first text of
    its third cell, the reading's process script the driver -- the rows as a new held-out read needs them."""
    out = {}
    for r, line in rows.items():
        cells = line.split("|")
        cells[3] = f" heldout-read: {','.join(ROWS[r])} by scripts/q58_driver.py --{cells[3]}"
        out[r] = "|".join(cells)
    return out


NO_DESIGN = log({r: f"| {r} | 2026-11-16 | **A row about nothing in particular** | test |" for r in ROWS})
MISSING = log({"E-904": "| E-904 | 2026-11-16 | **A row about nothing in particular** | test |"})


def make_tree(base: Path, name: str, where: str, decisions: str) -> Path:
    t = base / "runs" / name
    (t / where).mkdir(parents=True)
    (t / where / "q58_driver.py").write_text(DRIVER, encoding="utf-8")
    (t / "DECISIONS.md").write_bytes(decisions.encode("utf-8"))
    manifest = []
    for rel in ALL4:
        p = t / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(f"a stand-in for {rel} (Q-58's tests; never parsed)\n".encode("utf-8"))
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
    r = subprocess.run([sys.executable, f"{where}/q58_driver.py", str(cfg)], cwd=t, capture_output=True, text=True,
                       timeout=600, env=env)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    return json.loads(r.stdout.strip().splitlines()[-1])


def clean_env(name: str) -> dict[str, str]:
    return {"S2X_CLEAN_RUN": name, "S2X_RUN_ID": f"{name}@q58-sim"}


@pytest.fixture(scope="module")
def results(tmp_path_factory) -> dict:
    base = tmp_path_factory.mktemp("q58")
    valid = log(tokened(real_rows()))
    runs = [[s, a] for s, a, *_ in RUNS]
    refuse = [[s, FIRST[s][1]] for s in SCRIPTS]
    t = make_tree(base, "q58-scripts", "scripts", valid)
    ok = drive(t, "scripts", [
        {"name": "outside", "env": {}, "runs": runs},
        {"name": "inside", "env": clean_env(t.name), "runs": runs},
        {"name": "untokened_inside", "decisions": log(real_rows()), "env": clean_env(t.name), "runs": refuse},
        {"name": "no_design_outside", "decisions": NO_DESIGN, "env": {}, "runs": refuse},
        {"name": "no_design_inside", "env": clean_env(t.name), "runs": refuse},
        {"name": "missing_outside", "decisions": MISSING, "env": {}, "runs": refuse},
        {"name": "missing_inside", "env": clean_env(t.name), "runs": refuse},
    ])
    s = make_tree(base, "q58-ident", "identity", valid)
    other = drive(s, "identity", [
        {"name": "identity_inside", "env": clean_env(s.name), "runs": refuse},
        {"name": "identity_outside", "env": {}, "runs": refuse},
    ])
    return {"scripts": ok, "identity": other, "tree": t}


def phase(results: dict, which: str, name: str) -> list[dict]:
    return [r for r in results[which] if r["phase"] == name]


def explain(r: dict) -> str:
    return (f"{r['script']} {r['argv']} ({r['phase']}): rc {r.get('rc')} stopped {r.get('stopped')} "
            f"{r.get('error', '')}\n{r['stdout']}")


def authorisations(r: dict) -> list[dict]:
    return [e for e in r["events"] if e["event"] == "authorise"]


def work(r: dict) -> list[str]:
    return [e["name"] for e in r["events"] if e["event"] == "work"]


IDS = [f"{s}:{' '.join(a) or 'the run'}" for s, a, *_ in RUNS]


def test_the_rows_the_readings_name_exist_and_name_their_designs():
    rows = real_rows()
    for r, designs in ROWS.items():
        assert rows[r] is not None, f"{r} is no decision row of DECISIONS.md"
        for d in designs:
            assert re.search(rf"(?<![\w-]){re.escape(d)}(?!\d)", rows[r]), f"{r}'s row does not name {d}"
    assert {row for _, _, row, *_ in RUNS if row} == set(ROWS)


@pytest.mark.parametrize("i", range(len(RUNS)), ids=IDS)
def test_outside_a_clean_run_the_read_is_checked_refused_and_nothing_is_ledgered(results, i):
    """Q-158 (rule 3): the whole window reaches the held-out years, so outside a clean run the read is refused -- even
    under a row whose token names it -- after its one authorisation and before any of the engine's work."""
    script, argv, row, designs, files, first = RUNS[i]
    r = phase(results, "scripts", "outside")[i]
    assert (r["script"], r["argv"]) == (script, argv)
    assert "error" not in r, explain(r)
    if row is None:
        assert r.get("rc") == 2 and authorisations(r) == [] and work(r) == [], explain(r)
    else:
        a = authorisations(r)
        assert r.get("rc") == 3 and "stopped" not in r and work(r) == [], explain(r)
        assert "REFUSED" in r["stdout"] and "held-out rule 3" in r["stdout"] and "clean run" in r["stdout"], explain(r)
        assert len(a) == 1 and r["events"].index(a[0]) == 0, "one authorisation, before any of the engine's work"
        assert a[0]["purpose"] == "registered_design" and a[0]["declaration"] == row
        assert tuple(a[0]["design"]) == designs and (a[0]["start"], a[0]["end"]) == ("2020-01-02", "2026-07-16")
    assert not r["ledger_exists"] and r["new"] == [], "no ledger file outside a clean run"


@pytest.mark.parametrize("script", SCRIPTS)
def test_the_real_rows_without_a_token_admit_no_new_held_out_read(results, script):
    """Q-158 (rule 3): E-024 and E-026 as they stand carry no read token, so inside a clean run each reading is
    refused under them; the lines the inside phase wrote before stay."""
    r = next(x for x in phase(results, "scripts", "untokened_inside") if x["script"] == script)
    assert r.get("rc") == 3 and "error" not in r and "stopped" not in r, explain(r)
    assert "REFUSED" in r["stdout"] and "held-out rule 3" in r["stdout"], explain(r)
    assert work(r) == [] and r["new"] == [] and r["prefix_kept"], "nothing starts, nothing is written"
    assert [a["declaration"] for a in authorisations(r)] == [FIRST[script][2]]


@pytest.mark.parametrize("i", range(len(RUNS)), ids=IDS)
def test_inside_a_clean_run_one_line_per_run(results, i):
    script, argv, row, designs, files, first = RUNS[i]
    r = phase(results, "scripts", "inside")[i]
    tree = results["tree"]
    assert (r["script"], r["argv"]) == (script, argv) and "error" not in r, explain(r)
    assert r["prefix_kept"], "the ledger only grows"
    if row is None:
        assert r.get("rc") == 2 and r["new"] == [] and authorisations(r) == [], explain(r)
        return
    assert r.get("stopped") == first and len(r["new"]) == 1, explain(r)
    line = r["new"][0]
    assert line["purpose"] == "registered_design" and line["repeat"] is None
    assert line["declaration"] == {"ref": row, "sha256": None, "kind": "registered_design", "designs": list(designs)}
    assert line["dates"] == {"start": "2020-01-02", "end": "2026-07-16", "blocks": ["choice", "judged"],
                             "judged_first": "2024-01-02", "judged_last": "2026-07-16"}
    got = [f["path"] for f in line["what"]["files"]]
    assert sorted(got) == sorted(files) and len(got) == len(set(got)), (got, files)
    for f in line["what"]["files"]:
        assert f["sha256"] == hashlib.sha256((tree / f["path"]).read_bytes()).hexdigest() and f["in_data_manifest"]
    assert line["what"]["kind"] == "engine" and line["what"]["description"]
    who = line["who"]
    assert who["script"] == "scripts/q58_driver.py" and who["clean_run"] == tree.name and who["dirty"] is False
    assert who["run_id"] == f"{tree.name}@q58-sim"
    assert f"scripts/{script}.py:" in who["caller"].replace("\\", "/") and who["caller"].endswith(":main"), \
        who["caller"]


def test_inside_a_clean_run_the_lines_are_one_per_run_in_order(results):
    want = [row for _, _, row, *_ in RUNS if row]
    got = [line["declaration"]["ref"] for r in phase(results, "scripts", "inside") for line in r["new"]]
    assert got == want
    assert len(R.read_ledger(results["tree"] / R.LEDGER_REL)) == len(want)


@pytest.mark.parametrize("name", ["no_design_outside", "no_design_inside", "missing_outside", "missing_inside"])
@pytest.mark.parametrize("script", SCRIPTS)
def test_a_row_that_does_not_admit_the_reading_is_refused(results, name, script):
    r = next(x for x in phase(results, "scripts", name) if x["script"] == script)
    why = "does not name" if name.startswith("no_design") else "no decision row"
    assert r.get("rc") == 3 and "error" not in r and "stopped" not in r, explain(r)
    assert "REFUSED" in r["stdout"] and why in r["stdout"], explain(r)
    assert work(r) == [] and r["new"] == [] and r["prefix_kept"], "nothing starts, nothing is written"
    assert [a["declaration"] for a in authorisations(r)] == [FIRST[script][2]]


@pytest.mark.parametrize("name", ["identity_inside", "identity_outside"])
@pytest.mark.parametrize("script", SCRIPTS)
def test_the_reading_from_a_script_under_identity_is_refused(results, name, script):
    r = next(x for x in phase(results, "identity", name) if x["script"] == script)
    assert r.get("rc") == 3 and "error" not in r and "stopped" not in r, explain(r)
    assert "REFUSED" in r["stdout"] and "scripts/" in r["stdout"], explain(r)
    assert work(r) == [] and not r["ledger_exists"], "nothing starts; no ledger file"
