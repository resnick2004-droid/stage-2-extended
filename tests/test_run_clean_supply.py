"""Q-230 (E-302 (2), E-297 (3)): `scripts/run_clean.py --supply <commit>=<path>`, the verified input supply.

Finished results another clean run wrote (H3-A's slot outputs, S1's git-ignored file, H4-B's held parts) are copied into
a new checkout's `results/` before the command. Every refusal is shown on a planted defect, with nothing run (the
command's marker absent, no lock taken, nothing copied):

* the source's manifest does not verify (`extended.results.verify_result`), or is missing;
* the manifest names another commit than the declared one, or is dirty (`git_dirty` not False);
* a destination exists in the checkout (a tracked CSV, a tracked manifest) -- never overwritten; a reused checkout;
* an extra untracked file beside the supplied ones (the clean check admits exactly the supplied files);
* a supplied file changed or removed by the command (run_clean exits non-zero, the log names the file), and `--collect`
  then refuses;
* a supplied file is never collected back as the run's output (a tracked-path name and a git-ignored one, S1's case).

The positive end to end runs a toy command in the checkout that reads the supplied file through
`extended.results.read_result` and writes its own result through `extended.results.write_result`; its manifest names the
checkout's commit, clean -- and a positive control shows the command's exclusion is what keeps it clean.

All on a temporary git repository: a toy copy of this repository's `extended` package and the vendored writer's three
files (a toy tree the clean-run marker recognises), a dummy store (never the licensed data), a temporary lock file.
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import run_lock as RL  # noqa: E402
import worktrees as W  # noqa: E402


def _load():
    """This repository's run_clean.py by its path (the vendored tree has a run_clean.py too)."""
    spec = importlib.util.spec_from_file_location("s2x_run_clean_supply", SCRIPTS / "run_clean.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


RC = _load()

#: the files a toy tree needs for `extended.results.write_result` to run in its clean checkout
TOY_FILES = ("pyproject.toml", "extended/__init__.py", "extended/results.py", "extended/reader.py",
             "vendor/stage2/propedge/__init__.py", "vendor/stage2/propedge/reporting/__init__.py",
             "vendor/stage2/propedge/reporting/results.py", "vendor/stage2/scripts/hashes.py")

TOY_WRITE = '''import sys
import pandas as pd
from extended import results as RES
name, vals = sys.argv[1], [int(v) for v in sys.argv[2:]]
RES.write_result(pd.DataFrame({"x": vals}), name, script="toy_write.py", seed=None, require_seed=False,
                 parameters={"vals": vals})
print("WROTE", name)
'''

TOY_READ = '''import sys
import pandas as pd
from extended import results as RES
out, srcs = sys.argv[1], sys.argv[2:]
total = 0
for s in srcs:
    df = RES.read_result(s)
    total += int(df["x"].sum())
RES.write_result(pd.DataFrame({"total": [total]}), out, script="toy_read.py", seed=None, require_seed=False,
                 parameters={"inputs": srcs})
print("READ", total)
'''

TOY_TAMPER = '''import os, stat, sys
from pathlib import Path
how, name, code = sys.argv[1], sys.argv[2], int(sys.argv[3])
p = Path("results") / name
os.chmod(p, stat.S_IREAD | stat.S_IWRITE)
if how == "change":
    p.write_bytes(p.read_bytes() + b"9" + bytes([10]))
else:
    p.unlink()
raise SystemExit(code)
'''

TOY_MARK = '''import sys
from pathlib import Path
Path(sys.argv[1]).write_text("ran")
'''


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


@pytest.fixture()
def repo(tmp_path, monkeypatch):
    """A toy tree of this repository at one commit; its clean checkouts under `<tmp>/stage2-extended-runs` (the
    command's own `extended.RUNS_DIR`, through LOCALAPPDATA)."""
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-q", "-b", "master")
    git(root, "config", "user.email", "t@example.invalid")
    git(root, "config", "user.name", "t")
    git(root, "config", "core.autocrlf", "false")
    (root / ".gitignore").write_text("vendor/stage2/data/bars/\nvendor/stage2/data/atlas/\n__pycache__/\n"
                                     "results/s1_like.csv\nresults/s1_like.csv.manifest.json\n", encoding="utf-8")
    for rel in TOY_FILES:
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, root / rel)
    (root / "vendor/stage2/data").mkdir(parents=True, exist_ok=True)
    (root / "vendor/stage2/data/README.md").write_text("tracked\n", encoding="utf-8")
    (root / "results").mkdir()
    (root / "results/old.csv").write_text("a\n1\n", encoding="utf-8")
    for name, body in (("toy_write.py", TOY_WRITE), ("toy_read.py", TOY_READ), ("toy_tamper.py", TOY_TAMPER),
                       ("toy_mark.py", TOY_MARK)):
        (root / name).write_text(body, encoding="utf-8")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "first")
    for s, f in (("bars", "bars.parquet"), ("atlas", "walks.parquet")):
        d = root / "vendor/stage2/data" / s
        d.mkdir()
        (d / f).write_text(f"store {s}\n", encoding="utf-8")
    assert git(root, "status", "--porcelain") == ""
    runs = tmp_path / "stage2-extended-runs"
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr(W, "ROOT", root)
    monkeypatch.setattr(RC, "RUNS", runs)
    monkeypatch.setattr(RL, "LOCK", tmp_path / "run.lock")
    monkeypatch.setattr(RL, "available_gb", lambda: 8.0)
    yield root
    if runs.is_dir():                     # never leave a junction behind for the temp cleaner to walk
        for wt in runs.iterdir():
            if wt.is_dir():
                for s in W.STORES:
                    W.unlink(wt, s)
                for p in wt.rglob("*.csv*"):
                    os.chmod(p, stat.S_IREAD | stat.S_IWRITE)


PY = sys.executable


def source(repo: Path, run: str, *files: tuple[str, list[int]]) -> Path:
    """A clean run of the toy tree at HEAD that writes each `(name, values)` through `write_result`: the supply's
    source, a real result with a real manifest, each in its own checkout. Returns a folder holding them all (as
    `h4b-held` holds H4-B's parts), outside the runs folder."""
    out = RC.RUNS.parent / f"{run}-held"
    out.mkdir()
    for i, (name, vals) in enumerate(files):
        wt = f"{run}-{i}"
        assert RC.main(["--name", wt, "--", PY, "toy_write.py", name, *map(str, vals)]) == 0, name
        d = RC.RUNS / wt / "results"
        for p in (d / f"{name}.csv", d / f"{name}.csv.manifest.json"):
            shutil.copy2(p, out / p.name)
    return out


def manifest(p: Path) -> dict:
    return json.loads(Path(str(p) + ".manifest.json").read_text(encoding="utf-8"))


def write_manifest(p: Path, m: dict) -> None:
    Path(str(p) + ".manifest.json").write_text(json.dumps(m, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def head(repo: Path) -> str:
    return git(repo, "rev-parse", "HEAD")


def refused(repo: Path, tmp_path: Path, name: str, supply: list[str], match: str, *, made: bool = False,
            placed: bool = False) -> None:
    """The supply run refuses with `match`: its command never ran, no lock is left, and (`made` False) no checkout was
    made -- or (`made` True) the checkout was made but no supply record written (`placed` True: the copies were made
    and the refusal came at the clean check)."""
    marker = tmp_path / f"{name}.ran"
    args = ["--name", name, *[x for s in supply for x in ("--supply", s)], "--", PY, "toy_mark.py", str(marker)]
    with pytest.raises(SystemExit, match=match):
        RC.main(args)
    assert not marker.exists(), "the command never ran"
    assert not RL.LOCK.exists()
    wt = RC.RUNS / name
    if not made:
        assert not wt.exists(), "no checkout was made"
    elif not placed:
        assert not RC.supply_record_path(wt).exists(), "no supply record"


# ------------------------------------------------------------------------------------------------- the end to end


def test_a_supplied_result_is_read_by_the_command_which_writes_its_own_clean_result(repo):
    sha = head(repo)
    src = source(repo, "slot", ("a", [1, 2, 3]))
    a = src / "a.csv"
    assert manifest(a)["git_commit"] == sha and manifest(a)["git_dirty"] is False, "a real clean source"
    assert RC.main(["--name", "rep", "--supply", f"{sha[:7]}={a}", "--", PY, "toy_read.py", "out", "a.csv"]) == 0
    wt = RC.RUNS / "rep"
    log = (RC.RUNS / "rep.log").read_text(encoding="utf-8").splitlines()
    assert "READ 6" in log and log[-1] == "EXIT 0", log
    assert "supply re-checked after the command: 2 file(s) unchanged" in log
    # the command's own result: written in the checkout from its commit, clean, beside the supplied input
    out = manifest(wt / "results/out.csv")
    assert out["git_commit"] == sha and out["git_dirty"] is False, out["git_commit"]
    assert out["provenance"]["clean_run"]["name"] == "rep"
    # the copies: the source's bytes, read-only; the record beside the log, never inside the checkout
    for rel, p in (("results/a.csv", a), ("results/a.csv.manifest.json", Path(str(a) + ".manifest.json"))):
        assert (wt / rel).read_bytes() == p.read_bytes()
        assert not os.access(wt / rel, os.W_OK), f"{rel} is read-only"
    rec = json.loads(RC.supply_record_path(wt).read_text(encoding="utf-8"))
    assert RC.supply_record_path(wt).parent == wt.parent
    got = {f["path"]: f for f in rec["files"]}
    assert set(got) == {"results/a.csv", "results/a.csv.manifest.json"}
    assert got["results/a.csv"]["source"] == str(a.resolve()) and got["results/a.csv"]["declared_commit"] == sha
    assert got["results/a.csv"]["sha256"] == manifest(a)["sha256"]
    assert not list(wt.rglob("*.supply.*")), "nothing of the supply's record inside the checkout"
    # collected: the command's output comes home; the supplied input never does
    assert RC.main(["--name", "rep", "--collect"]) == 0
    assert (repo / "results/out.csv").is_file() and (repo / "results/out.csv.manifest.json").is_file()
    assert not (repo / "results/a.csv").exists() and not (repo / "results/a.csv.manifest.json").exists()
    # removed: the supplied inputs do not hold it up; the record is kept, renamed
    assert RC.main(["--name", "rep", "--remove"]) == 0
    assert not wt.exists() and not RC.supply_record_path(wt).exists()
    assert len(list(RC.RUNS.glob("rep.supply.removed-*.json"))) == 1


def test_the_commands_exclusion_is_what_keeps_its_result_clean(repo, monkeypatch):
    """Positive control: without the supplied paths excluded for the command's git, the vendored writer sees them
    untracked and stamps the command's own result -dirty (so the exclusion is load-bearing, and checked)."""
    sha = head(repo)
    a = source(repo, "slot", ("a", [4])) / "a.csv"
    real = RC.run

    def unexcluded(wt, cmd, lock_job=None, extra_env=None, record=None):          # the plant: no exclusion
        return real(wt, cmd, lock_job, extra_env={}, record=record)
    monkeypatch.setattr(RC, "run", unexcluded)
    assert RC.main(["--name", "rep", "--supply", f"{sha}={a}", "--", PY, "toy_read.py", "out", "a.csv"]) == 0
    out = manifest(RC.RUNS / "rep/results/out.csv")
    assert out["git_dirty"] is True and out["git_commit"].endswith("-dirty")


def test_an_exclusion_that_does_not_hide_the_supplied_files_is_refused_before_the_command(repo, tmp_path, monkeypatch):
    """The clean check under the command's exclusion: an exclusion that hides nothing (the plant) means nothing runs."""
    sha = head(repo)
    a = source(repo, "slot", ("a", [4])) / "a.csv"
    monkeypatch.setattr(RC, "supply_env", lambda wt, record: {})
    refused(repo, tmp_path, "rep", [f"{sha}={a}"], "under the command's exclusion", made=True,
            placed=True)


def test_a_glob_supplies_every_csv_it_matches_with_its_manifest(repo):
    sha = head(repo)
    src = source(repo, "slot", ("h_000", [1]), ("h_001", [2]))
    assert RC.main(["--name", "rep", "--supply", f"{sha}={src / 'h_*.csv'}", "--", PY, "toy_read.py", "out",
                    "h_000.csv", "h_001.csv"]) == 0
    assert "READ 3" in (RC.RUNS / "rep.log").read_text(encoding="utf-8")
    rec = json.loads(RC.supply_record_path(RC.RUNS / "rep").read_text(encoding="utf-8"))
    assert sorted(f["path"] for f in rec["files"]) == ["results/h_000.csv", "results/h_000.csv.manifest.json",
                                                       "results/h_001.csv", "results/h_001.csv.manifest.json"]


def test_a_git_ignored_supplied_file_is_admitted_as_ignored_and_never_collected(repo):
    """S1's case: `results/s1_like.csv` is git-ignored (a licensed derivative), so a clean checkout lacks it; supplied,
    it is not seen by git at all, the command reads it, and `--collect` brings back only the command's output."""
    sha = head(repo)
    s1 = source(repo, "s1", ("s1_like", [7, 8])) / "s1_like.csv"
    assert RC.main(["--name", "use", "--supply", f"{sha}={s1}", "--", PY, "toy_read.py", "out", "s1_like.csv"]) == 0
    wt = RC.RUNS / "use"
    assert "results/s1_like.csv" not in RC._changed(wt), "ignored: git does not see it"
    assert manifest(wt / "results/out.csv")["git_dirty"] is False
    assert RC.main(["--name", "use", "--collect"]) == 0
    assert not (repo / "results/s1_like.csv").exists() and (repo / "results/out.csv").is_file()


def test_a_supply_under_the_lock_takes_and_releases_it_as_before(repo, tmp_path):
    sha = head(repo)
    a = source(repo, "slot", ("a", [1])) / "a.csv"
    assert RC.main(["--name", "rep", "--hours", "0.5", "--mem-gb", "1", "--task", "Q-230", "--supply", f"{sha}={a}",
                    "--", PY, "toy_read.py", "out", "a.csv"]) == 0
    assert not RL.LOCK.exists(), "released"
    assert manifest(RC.RUNS / "rep/results/out.csv")["git_dirty"] is False


def test_a_held_lock_with_a_supply_runs_nothing_and_copies_nothing(repo, tmp_path):
    sha = head(repo)
    a = source(repo, "slot", ("a", [1])) / "a.csv"
    assert RL.main(["take", "--job", "other", "--task", "Q-00", "--holder", "t", "--hours", "1", "--mem-gb", "1"]) == 0
    marker = tmp_path / "ran"
    assert RC.main(["--name", "rep", "--hours", "1", "--mem-gb", "1", "--task", "Q-230", "--supply", f"{sha}={a}",
                    "--", PY, "toy_mark.py", str(marker)]) == 3
    assert not marker.exists() and not (RC.RUNS / "rep").exists()
    assert json.loads(RL.LOCK.read_text())["job"] == "other"


# ------------------------------------------------------------------------------- the refusals, each on a planted defect


def test_a_manifest_that_does_not_verify_is_refused(repo, tmp_path):
    sha = head(repo)
    a = source(repo, "slot", ("a", [1, 2])) / "a.csv"
    a.write_bytes(a.read_bytes() + b"3\n")                           # the plant: the CSV edited after it was written
    refused(repo, tmp_path, "rep", [f"{sha}={a}"], "does not verify")


def test_a_missing_manifest_is_refused(repo, tmp_path):
    sha = head(repo)
    a = source(repo, "slot", ("a", [1])) / "a.csv"
    Path(str(a) + ".manifest.json").unlink()                         # the plant
    refused(repo, tmp_path, "rep", [f"{sha}={a}"], "no sidecar manifest")


def test_the_wrong_commit_is_refused(repo, tmp_path):
    first = head(repo)
    a = source(repo, "slot", ("a", [1])) / "a.csv"
    (repo / "code.txt").write_text("v2\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "second")
    refused(repo, tmp_path, "rep", [f"{head(repo)}={a}"], "not the declared commit")  # the plant: another commit
    assert RC.main(["--name", "rep", "--supply", f"{first}={a}", "--", PY, "toy_read.py", "out", "a.csv"]) == 0


@pytest.mark.parametrize("plant", [{"git_dirty": True}, {"git_dirty": None}], ids=["dirty", "dirty-none"])
def test_a_dirty_manifest_is_refused(repo, tmp_path, plant):
    sha = head(repo)
    a = source(repo, "slot", ("a", [1])) / "a.csv"
    write_manifest(a, {**manifest(a), **plant})                      # the plant; the CSV's sha256 still verifies
    refused(repo, tmp_path, "rep", [f"{sha}={a}"], "git_dirty")


def test_a_manifest_naming_another_file_is_refused(repo, tmp_path):
    sha = head(repo)
    src = source(repo, "slot", ("a", [1]))
    b = src / "b.csv"
    for x, y in (("a.csv", "b.csv"), ("a.csv.manifest.json", "b.csv.manifest.json")):
        shutil.copy2(src / x, src / y)                               # the plant: a renamed result
    refused(repo, tmp_path, "rep", [f"{sha}={b}"], "manifest names")


@pytest.mark.parametrize("which", ["csv", "manifest"])
def test_an_existing_destination_is_refused_and_nothing_is_copied(repo, tmp_path, which):
    """The run's commit tracks `results/a.csv` (or its manifest): the supply would overwrite it -- refused, and the
    other file of the pair is not copied either."""
    first = head(repo)
    a = source(repo, "slot", ("a", [1])) / "a.csv"
    rel = "results/a.csv" if which == "csv" else "results/a.csv.manifest.json"
    (repo / rel).write_text("tracked\n", encoding="utf-8")           # the plant: a destination the commit holds
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "a tracked destination")
    refused(repo, tmp_path, "rep", [f"{first}={a}"], "never overwritten", made=True)
    wt = RC.RUNS / "rep"
    assert (wt / rel).read_text(encoding="utf-8") == "tracked\n"
    other = "results/a.csv.manifest.json" if which == "csv" else "results/a.csv"
    assert not (wt / other).exists(), "nothing copied"


def test_a_supply_into_an_existing_checkout_is_refused(repo, tmp_path):
    sha = head(repo)
    a = source(repo, "slot", ("a", [1])) / "a.csv"
    assert RC.main(["--name", "rep", "--", PY, "toy_mark.py", str(tmp_path / "first")]) == 0
    with pytest.raises(SystemExit, match="made at a checkout's creation"):
        RC.main(["--name", "rep", "--supply", f"{sha}={a}", "--", PY, "toy_mark.py", str(tmp_path / "second")])
    assert not (tmp_path / "second").exists() and not (RC.RUNS / "rep/results/a.csv").exists()


def test_two_sources_for_one_destination_are_refused(repo, tmp_path):
    sha = head(repo)
    a1 = source(repo, "s-one", ("a", [1])) / "a.csv"
    a2 = source(repo, "s-two", ("a", [2])) / "a.csv"
    refused(repo, tmp_path, "rep", [f"{sha}={a1}", f"{sha}={a2}"], "two sources")


@pytest.mark.parametrize("how", ["fresh", "reused"])
def test_an_extra_untracked_file_beside_the_supplied_ones_is_refused(repo, tmp_path, monkeypatch, how):
    """The clean check admits exactly the supplied files: a stray file planted beside them (at the supply, or in a
    reused checkout before its second run) means nothing runs."""
    sha = head(repo)
    a = source(repo, "slot", ("a", [1])) / "a.csv"
    marker = tmp_path / "ran"
    if how == "fresh":
        place = RC.place_supply

        def planted(wt, plan):
            rec = place(wt, plan)
            (wt / "results/stray.csv").write_text("x\n", encoding="utf-8")     # the plant
            return rec
        monkeypatch.setattr(RC, "place_supply", planted)
        args = ["--name", "rep", "--supply", f"{sha}={a}", "--", PY, "toy_mark.py", str(marker)]
    else:
        assert RC.main(["--name", "rep", "--supply", f"{sha}={a}", "--", PY, "-c", "pass"]) == 0
        (RC.RUNS / "rep/results/stray.csv").write_text("x\n", encoding="utf-8")  # the plant
        args = ["--name", "rep", "--", PY, "toy_mark.py", str(marker)]
    # the first layer's own message (the exclusion's check behind it would refuse too, with its own)
    with pytest.raises(SystemExit, match=r"rep is not clean: \['results/stray.csv'\]"):
        RC.main(args)
    assert not marker.exists()


def test_a_reused_checkout_without_a_supply_is_held_to_the_clean_check_as_before(repo, tmp_path):
    """Unchanged behaviour: with no record, nothing is admitted -- a stray file in a reused checkout refuses."""
    assert RC.main(["--name", "plain", "--", PY, "-c", "pass"]) == 0
    (RC.RUNS / "plain/results/stray.csv").write_text("x\n", encoding="utf-8")             # the plant
    marker = tmp_path / "ran"
    with pytest.raises(SystemExit, match=r"plain is not clean: \['results/stray.csv'\]"):
        RC.main(["--name", "plain", "--", PY, "toy_mark.py", str(marker)])
    assert not marker.exists()


def test_a_reused_checkout_re_applies_its_record_and_re_checks_it_before_the_command(repo, tmp_path):
    sha = head(repo)
    a = source(repo, "slot", ("a", [1])) / "a.csv"
    assert RC.main(["--name", "rep", "--supply", f"{sha}={a}", "--", PY, "-c", "pass"]) == 0
    # reused, unchanged: admitted and excluded again, so its output is clean
    assert RC.main(["--name", "rep", "--", PY, "toy_read.py", "out2", "a.csv"]) == 0
    assert manifest(RC.RUNS / "rep/results/out2.csv")["git_dirty"] is False
    # the plant: a supplied file changed between runs -- the next run refuses before its command
    assert RC.main(["--name", "rep2", "--supply", f"{sha}={a}", "--", PY, "-c", "pass"]) == 0
    assert RC.main(["--name", "rep2", "--", PY, "-c", "pass"]) == 0
    p = RC.RUNS / "rep2/results/a.csv"
    os.chmod(p, stat.S_IREAD | stat.S_IWRITE)
    p.write_bytes(p.read_bytes() + b"5\n")
    marker = tmp_path / "ran"
    with pytest.raises(SystemExit, match="before the command"):
        RC.main(["--name", "rep2", "--", PY, "toy_mark.py", str(marker)])
    assert not marker.exists()


@pytest.mark.parametrize("how,code,want", [("change", 0, RC.SUPPLY_CHANGED), ("delete", 0, RC.SUPPLY_CHANGED),
                                           ("change", 5, 5)], ids=["changed", "deleted", "changed-and-failed"])
def test_a_supplied_file_changed_by_the_command_fails_the_run_naming_it(repo, how, code, want):
    sha = head(repo)
    a = source(repo, "slot", ("a", [1])) / "a.csv"
    rc = RC.main(["--name", "rep", "--supply", f"{sha}={a}", "--", PY, "toy_tamper.py", how, "a.csv", str(code)])
    assert rc == want and rc != 0
    log = (RC.RUNS / "rep.log").read_text(encoding="utf-8").splitlines()
    word = "changed" if how == "change" else "missing"
    assert any(x.startswith(f"SUPPLY CHANGED: results/a.csv: {word}") for x in log), log
    assert log[-1] == f"EXIT {want}"
    with pytest.raises(SystemExit, match="supplied input is not its record's"):
        RC.main(["--name", "rep", "--collect"])                      # nothing copied while it differs
    assert not (repo / "results/a.csv").exists()


def test_a_supplied_file_is_not_collected_back_when_the_command_wrote_nothing(repo):
    sha = head(repo)
    a = source(repo, "slot", ("a", [1])) / "a.csv"
    assert RC.main(["--name", "rep", "--supply", f"{sha}={a}", "--", PY, "-c", "pass"]) == 0
    assert RC.main(["--name", "rep", "--collect"]) == 0
    assert not (repo / "results/a.csv").exists() and not (repo / "results/a.csv.manifest.json").exists()
    assert RC.main(["--name", "rep", "--remove"]) == 0                # supplied inputs are not output left behind


def test_a_record_without_its_checkout_refuses_a_new_checkout_of_that_name(repo, tmp_path):
    RC.RUNS.mkdir(parents=True, exist_ok=True)
    RC.supply_record_path(RC.RUNS / "rep").write_text('{"files": []}\n', encoding="utf-8")   # the plant
    with pytest.raises(SystemExit, match="is gone"):
        RC.main(["--name", "rep", "--", PY, "toy_mark.py", str(tmp_path / "ran")])
    assert not (tmp_path / "ran").exists() and not (RC.RUNS / "rep").exists()


@pytest.mark.parametrize("spec,match", [("no-equals-sign", "not <commit>=<path>"),
                                        ("HEAD={tmp}/nothing_*.csv", "matches no result file"),
                                        ("HEAD={tmp}/absent.csv", "does not exist")])
def test_a_malformed_supply_is_refused(repo, tmp_path, spec, match):
    refused(repo, tmp_path, "rep", [spec.format(tmp=tmp_path)], match)


def test_the_supply_goes_with_a_command_only(repo):
    with pytest.raises(SystemExit):
        RC.main(["--name", "rep", "--collect", "--supply", "HEAD=x.csv"])
