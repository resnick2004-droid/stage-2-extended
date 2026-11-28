"""Q-229 part 2: the Mac run agent (`scripts/mac_agent.py`), its assignment file (`extended/mac_assignments.py`,
`config/mac_assignments.json`), the lead's collect step (`scripts/mac_collect.py`), the lock's TAKEN line with its
memory, and the host named in run_clean's log and in a clean run's manifest.

Each refusal has its planted defect: the schema (a missing field, a short sha, a duplicate name, a command outside
`python scripts/` and `python identity/`, shell syntax, every held-out and confirmation-window marker); a lock held;
memory unreadable or short; the price-level guard refusing; a non-zero exit; a wrong commit (and a dirty one) in a
manifest; a push to a ref that is not `mac/<run>`. The guard runs before the push: `test_guard_refusal_pushes_nothing`
fails if the order is swapped. All on synthetic stand-ins (`tests/mac_world.py`): a fake origin made by
`git init --bare` in a temporary folder, a fake run command, darwin mocked; no real bars, no heavy run, and the run lock
a temporary file, never this machine's.
"""
from __future__ import annotations

import hashlib
import json
import os
import plistlib
import subprocess
import sys
from pathlib import Path

import pytest

import mac_world as MW

ROOT = MW.ROOT
import run_lock as RL  # noqa: E402  (mac_world put scripts/ on the path)
import worktrees as W  # noqa: E402
import mac_agent as AG  # noqa: E402
import mac_collect as CO  # noqa: E402
from extended import mac_assignments as MA  # noqa: E402

RC = MW.load_run_clean()


# ------------------------------------------------------------------------------------------------------ fixtures

def _patch(w: MW.World, set_):
    set_(W, "ROOT", w.mac)                               # run_clean makes its checkouts from the Mac's clone
    set_(RC, "RUNS", w.runs)
    set_(RL, "LOCK", w.tmp / "run.lock")
    set_(RL, "available_gb", lambda: 8.0)


def _cleanup(w: MW.World) -> None:
    if w.runs.is_dir():
        for wt in w.runs.iterdir():
            if wt.is_dir() and (wt / ".git").exists():
                subprocess.run(["git", "worktree", "remove", "--force", str(wt)], cwd=w.mac, capture_output=True)


@pytest.fixture()
def world(tmp_path, monkeypatch):
    w = MW.templated("bare", MW.make_world, tmp_path / "w")
    _patch(w, monkeypatch.setattr)
    yield w
    _cleanup(w)


def _build_pushed(base: Path, mode: str = "ok") -> MW.World:
    """A world in which the agent has run and pushed `mac/t-run` (the collect tests' start), its checkout removed."""
    w = MW.make_world(base)
    mp = pytest.MonkeyPatch()
    try:
        _patch(w, mp.setattr)
        w.assign([w.entry(mode=mode)])
        a, said = agent(w)
        assert a.wake() == AG.OK, said
    finally:
        mp.undo()
        _cleanup(w)
    return w


@pytest.fixture()
def pushed(tmp_path, monkeypatch):
    w = MW.templated("pushed", _build_pushed, tmp_path / "w")
    _patch(w, monkeypatch.setattr)
    yield w
    _cleanup(w)


def agent(w: MW.World, run_clean=None) -> tuple[AG.Agent, list[str]]:
    said: list[str] = []
    rc = run_clean or MW.in_process_run_clean(RC)
    return AG.Agent(repo=w.mac, runs=w.runs, state=w.state, run_clean=rc, say=said.append), said


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def plain_verify(csv: Path) -> tuple[bool, str]:
    """The vendored check's rule (the CSV's sha256 against its manifest's), in this process."""
    m = json.loads(Path(str(csv) + MA.MANIFEST_SUFFIX).read_text(encoding="utf-8"))
    return (sha256(csv.read_bytes()) == m["sha256"]), "sha256"


# --------------------------------------------------------------------------------------------------- the schema

GOOD = {"name": "h4b-naive-p1", "commit": "7ed79fb6e5a8179311548e3574f76a503b38a115",
        "command": "python scripts/h4_rebaseline.py --part H4-B --baseline naive_coin --start-lo 0 --start-hi 150 "
                   "--part-tag p1 --workers 2",
        "hours": 6.0, "mem_gb": 3.0, "task": "Q-188b",
        "outputs": ["results/h4_units_naive_coin_p1.csv", "results/h4_readings_naive_coin_p1.csv",
                    "results/h4_trades_naive_coin_p1.csv"]}


def doc(*runs, acks=()):
    return json.dumps({"version": 1, "about": "x", "runs": list(runs), "failures_acknowledged": list(acks)})


def problems(**change):
    e = dict(GOOD)
    for k, v in change.items():
        if v is None:
            e.pop(k)
        else:
            e[k] = v
    with pytest.raises(MA.AssignmentError) as ei:
        MA.parse(doc(e))
    return " | ".join(ei.value.problems)


def test_a_good_entry_is_accepted():
    book = MA.parse(doc(GOOD))
    assert book.runs[0].name == "h4b-naive-p1" and book.runs[0].argv()[:2] == ["python", "scripts/h4_rebaseline.py"]
    assert MA.expected_files(book.runs[0]) == {p for o in GOOD["outputs"] for p in (o, o + ".manifest.json")}


def test_the_committed_file_is_accepted():
    book = MA.parse((ROOT / MA.CONFIG_REL).read_text(encoding="utf-8"))
    assert isinstance(book.runs, tuple)


@pytest.mark.parametrize("field", MA.FIELDS)
def test_a_missing_field_is_refused(field):
    assert f"the field {field!r} is missing" in problems(**{field: None})


@pytest.mark.parametrize("sha", ["7ed79fb", "7ed79fb6e5a8179311548e3574f76a503b38a11", "7ED79FB6E5A8179311548E3574F76A503B38A115",
                                 "7ed79fb6e5a8179311548e3574f76a503b38a115-dirty", 12345])
def test_a_short_or_malformed_sha_is_refused(sha):
    assert "full 40-character" in problems(commit=sha)


def test_a_duplicate_name_is_refused():
    other = dict(GOOD, outputs=["results/x.csv"])
    with pytest.raises(MA.AssignmentError) as ei:
        MA.parse(doc(GOOD, other))
    assert any("appears more than once" in p for p in ei.value.problems)


@pytest.mark.parametrize("cmd", ["bash scripts/x.sh", "python -c print(1)", "python vendor/stage2/scripts/x.py",
                                 " python scripts/x.py", "python3 scripts/x.py", "python scripts/x.sh",
                                 "python results/x.py", "python  scripts/x.py", "python scripts/../vendor/x.py",
                                 "python scripts"])
def test_a_command_outside_scripts_and_identity_is_refused(cmd):
    assert "command" in problems(command=cmd)


@pytest.mark.parametrize("cmd", ["python scripts/x.py; rm -rf ~", "python scripts/x.py && git push",
                                 "python scripts/x.py | tee y", "python scripts/x.py $(whoami)",
                                 "python scripts/x.py > out.txt", "python scripts/x.py 'quoted'",
                                 "python scripts/x.py `id`"])
def test_shell_syntax_is_refused(cmd):
    assert "characters outside" in problems(command=cmd)


@pytest.mark.parametrize("script", ["scripts/run_clean.py", "scripts/mac_agent.py", "scripts/run_lock.py"])
def test_the_agents_own_scripts_are_refused(script):
    assert "agent's own scripts" in problems(command=f"python {script} --x")


@pytest.mark.parametrize("cmd", [
    "python scripts/x.py --from 2024-01-02", "python scripts/x.py --day 2026-07-17", "python scripts/x.py --d 20260717",
    "python scripts/x.py --start 2025/03/04", "python scripts/x.py --block judged", "python scripts/x.py --block=heldout",
    "python scripts/x.py --journey-block test", "python scripts/x.py --part heldout_test", "python scripts/x.py --held-out",
    "python scripts/x.py --confirmation", "python scripts/x.py --mode verdict", "python scripts/x.py --year 2024",
    "python scripts/x.py --years 2026", "python scripts/x.py --window oos", "python scripts/x.py --end-date 2023-12-30",
    "python identity/stage2_identity.py --only u1 --judged"])
def test_held_out_and_confirmation_markers_are_refused(cmd):
    assert "marks" in problems(command=cmd) or "date" in problems(command=cmd) or "block" in problems(command=cmd) \
        or "year" in problems(command=cmd)


@pytest.mark.parametrize("cmd", ["python scripts/x.py --until 2023-12-29", "python scripts/x.py --block search",
                                 "python scripts/x.py --start-hi 2048 --workers 2", "python scripts/x.py --year 2023",
                                 "python identity/stage2_identity.py --only u1 --u1-starts all"])
def test_search_year_commands_are_not_markers(cmd):
    assert MA.window_markers(cmd) == [] and MA.parse(doc(dict(GOOD, command=cmd)))


def test_markers_in_names_and_outputs_are_refused():
    assert "marks" in problems(name="p14-heldout")
    assert "date" in problems(outputs=["results/x_20240102.csv"])


@pytest.mark.parametrize("change", [dict(hours=0), dict(hours=-1), dict(hours=True), dict(hours="6"),
                                    dict(mem_gb=0), dict(mem_gb=1e9), dict(task="188b"), dict(name="H4B"),
                                    dict(name="a/b"), dict(name="x" * 65), dict(outputs=[]),
                                    dict(outputs=["results/a.csv", "results/a.csv"]), dict(outputs=["out/a.csv"]),
                                    dict(outputs=["results/a.csv.manifest.json"]), dict(outputs=["results/sub/a.csv"]),
                                    dict(extra=1)])
def test_other_malformed_fields_are_refused(change):
    assert problems(**change)


def test_top_level_problems_are_refused():
    for bad in ('{"version": 2, "runs": []}', '{"version": 1, "runs": {}}', '{"version": 1, "runs": [], "x": 1}',
                '{"version": 1, "runs": [], "failures_acknowledged": ["A B"]}', '[]', 'not json',
                '{"version": 1, "version": 1, "runs": []}', '{"version": 1, "runs": [], "about": NaN}'):
        with pytest.raises(MA.AssignmentError):
            MA.parse(bad)


# ------------------------------------------------------------------------------------- the lock's TAKEN line

VM_STAT = """Mach Virtual Memory Statistics: (page size of 16384 bytes)
Pages free:                               65536.
Pages active:                            400000.
Pages inactive:                          131072.
Pages speculative:                        65536.
"""


def test_taken_line_prints_the_memory_on_darwin(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(RL, "LOCK", tmp_path / "run.lock")
    monkeypatch.setattr(RL.sys, "platform", "darwin")
    monkeypatch.setattr(RL.os, "name", "posix")

    class Done:
        stdout = VM_STAT

    monkeypatch.setattr(RL.subprocess, "run", lambda *a, **k: Done())
    assert RL.main(["take", "--job", "j", "--task", "Q-229", "--holder", "t", "--hours", "1", "--mem-gb", "3"]) == 0
    line = [x for x in capsys.readouterr().out.splitlines() if x.startswith("TAKEN")][0]
    rec = json.loads((tmp_path / "run.lock").read_text(encoding="utf-8"))
    assert rec["mem_gb_available_at_start"] == 4.0 and rec["mem_gb_needed"] == 3.0
    assert "memory available at the take 4.00 GB, needed 3.00 GB" in line


@pytest.mark.skipif(os.name != "nt", reason="the Windows reading")
def test_taken_line_prints_the_memory_on_windows(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(RL, "LOCK", tmp_path / "run.lock")
    assert RL.main(["take", "--job", "j", "--task", "Q-229", "--holder", "t", "--hours", "1", "--mem-gb", "0.01"]) == 0
    line = [x for x in capsys.readouterr().out.splitlines() if x.startswith("TAKEN")][0]
    rec = json.loads((tmp_path / "run.lock").read_text(encoding="utf-8"))
    assert f"memory available at the take {rec['mem_gb_available_at_start']:.2f} GB, needed 0.01 GB" in line


def test_memory_words_come_from_the_record():
    assert RL.memory_words({"mem_gb_available_at_start": 5.5, "mem_gb_needed": 2}) == \
        "memory available at the take 5.50 GB, needed 2.00 GB"
    assert "unread" in RL.memory_words({"mem_gb_needed": 2})


# ---------------------------------------------------------------------------------------------- a good run

def test_a_run_is_pushed_to_its_mac_branch_only(world):
    world.assign([world.entry()])
    before = world.remote_refs()
    a, said = agent(world)
    assert a.wake() == AG.OK, said
    assert a.trace == ["guard", "push"]                              # the guard, then the push
    after = world.remote_refs()
    new = {r for r in after if r not in before}
    assert new == {"refs/heads/mac/t-run"}                           # one ref added, nothing else moved
    assert all(after[r] == before[r] for r in before)
    files = MW.git(world.origin, "ls-tree", "-r", "--name-only", "refs/heads/mac/t-run").splitlines()
    assert sorted(files) == sorted(["results/t_units.csv", "results/t_units.csv.manifest.json", "results/t_trades.csv",
                                    "results/t_trades.csv.manifest.json", "run.log", "run.json"])
    log = MW.git(world.origin, "show", "refs/heads/mac/t-run:run.log").splitlines()
    assert log[0].startswith("host: ") and log[-1] == "EXIT 0"      # run_clean names the host in its log
    rec = json.loads(MW.git(world.origin, "show", "refs/heads/mac/t-run:run.json"))
    assert rec["assignment"]["commit"] == world.commit and rec["host"]
    assert (world.state / "t-run.done").is_file()
    assert MW.git(world.mac, "status", "--porcelain") == ""          # nothing written into the agent's tree
    # the exact command was run through run_clean with the lock's figures
    args = a.run_clean.calls[0]
    assert args[:10] == ["--name", "t-run", "--commit", world.commit, "--hours", "1.0", "--mem-gb", "1.0", "--task",
                         "Q-229"]
    assert args[args.index("--") + 1:][1:] == world.entry()["command"].split()[1:]
    # a second wake runs nothing
    a2, said2 = agent(world)
    assert a2.wake() == AG.OK and not a2.run_clean.calls and any("nothing to run" in s for s in said2)


def test_the_assignment_is_read_from_origin_master_not_a_local_edit(world):
    world.assign([])
    cfg = world.mac / MA.CONFIG_REL
    cfg.parent.mkdir(exist_ok=True)
    cfg.write_text(MW.json.dumps({"version": 1, "runs": [world.entry()], "failures_acknowledged": []}),
                   encoding="utf-8")
    MW.git(world.mac, "add", "-A")
    MW.git(world.mac, "-c", "user.email=t@example.invalid", "-c", "user.name=t", "commit", "-q", "-m", "local")
    a, said = agent(world)
    assert a.wake() == AG.OK and not a.run_clean.calls and world.mac_refs_on_origin() == []


def test_a_branch_already_on_origin_is_skipped(world):
    world.assign([world.entry()])
    MW.git(world.lead, "push", "-q", "origin", f"{world.commit}:refs/heads/mac/t-run")
    a, said = agent(world)
    assert a.wake() == AG.OK and not a.run_clean.calls and (world.state / "t-run.done").is_file()


def test_stop_file_starts_nothing(world):
    world.assign([world.entry()])
    world.state.mkdir(parents=True)
    (world.state / "STOP").write_text("")
    a, said = agent(world)
    assert a.wake() == AG.OK and not a.run_clean.calls


def test_a_refused_file_starts_nothing(world):
    world.assign([world.entry(commit="abc1234")])
    a, said = agent(world)
    assert a.wake() == AG.BAD and not a.run_clean.calls and any("full 40-character" in s for s in said)


def test_a_commit_not_on_origin_starts_nothing(world):
    world.assign([world.entry(commit="1" * 40)])
    a, said = agent(world)
    assert a.wake() == AG.BAD and not a.run_clean.calls


# ---------------------------------------------------------------------------------- the lock and the memory

def test_a_held_lock_starts_nothing_and_is_not_stolen(world):
    world.assign([world.entry()])
    RL.LOCK.write_text(json.dumps({"job": "other", "expected_end": "2000-01-01T00:00:00+00:00"}), encoding="utf-8")
    a, said = agent(world)
    assert a.wake() == AG.HELD and not a.run_clean.calls
    assert json.loads(RL.LOCK.read_text(encoding="utf-8"))["job"] == "other"      # stale or not, never taken
    assert not (world.runs / "t-run").exists() and not list(world.state.glob("t-run.*"))


def test_unreadable_memory_starts_nothing(world, monkeypatch):
    world.assign([world.entry()])
    monkeypatch.setattr(RL, "available_gb", lambda: None)
    a, said = agent(world)
    assert a.wake() == AG.MEMORY and not a.run_clean.calls and not RL.LOCK.exists()


def test_short_memory_starts_nothing(world, monkeypatch):
    world.assign([world.entry(mem_gb=6.0)])
    monkeypatch.setattr(RL, "available_gb", lambda: 2.0)
    a, said = agent(world)
    assert a.wake() == AG.MEMORY and not a.run_clean.calls


def test_unreadable_memory_at_run_cleans_take_starts_nothing(world, monkeypatch):
    # the agent's own look passed; run_clean's take (run_lock) then reads no memory: exit 4, no command, no marker
    world.assign([world.entry()])
    rc = MW.in_process_run_clean(RC)

    def unreadable_then(args):
        monkeypatch.setattr(RL, "available_gb", lambda: None)
        return rc(args)

    a, said = agent(world, run_clean=unreadable_then)
    assert a.wake() == AG.MEMORY
    assert not (world.runs / "t-run.log").exists() and not list(world.state.glob("t-run.*"))
    assert world.mac_refs_on_origin() == [] and not RL.LOCK.exists()


def test_a_lock_taken_at_run_cleans_take_starts_nothing(world):
    world.assign([world.entry()])
    rc = MW.in_process_run_clean(RC)

    def held_then(args):
        RL.LOCK.write_text(json.dumps({"job": "other", "expected_end": "2999-01-01T00:00:00+00:00"}), encoding="utf-8")
        return rc(args)

    a, said = agent(world, run_clean=held_then)
    assert a.wake() == AG.HELD and not list(world.state.glob("t-run.*"))
    assert json.loads(RL.LOCK.read_text(encoding="utf-8"))["job"] == "other"


def test_a_second_agent_at_once_starts_nothing(world):
    world.assign([world.entry()])
    with AG.single_instance(world.state / "agent.instance") as alone:
        assert alone
        a, said = agent(world)
        assert a.wake() == AG.HELD and not a.run_clean.calls


# ----------------------------------------------------------------------------------------------- failures

def test_a_non_zero_exit_pushes_nothing_and_is_never_rerun(world):
    world.assign([world.entry(mode="fail"), world.entry(name="t-next")])
    a, said = agent(world)
    assert a.wake() == AG.FAILED
    assert world.mac_refs_on_origin() == [] and "push" not in a.trace
    rec = json.loads((world.state / "t-run.failed").read_text(encoding="utf-8"))
    assert any("planted failure" in x for x in rec["log_tail"]) and rec["log_tail"][-1] == "EXIT 1"
    assert any(s.startswith("mac_agent: FAILED: t-run") for s in said)
    a2, _ = agent(world)                                         # blocked: nothing new until the lead acknowledges
    assert a2.wake() == AG.BLOCKED and not a2.run_clean.calls
    world.assign([world.entry(mode="fail"), world.entry(name="t-next")], acks=("t-run",))
    a3, _ = agent(world)
    assert a3.wake() == AG.OK
    assert [c[1] for c in a3.run_clean.calls] == ["t-next"]       # the failed one is never re-run
    assert world.mac_refs_on_origin() == ["refs/heads/mac/t-next"]


def test_an_interrupted_run_is_a_failure_not_a_rerun(world):
    world.assign([world.entry()])
    (world.runs / "t-run").mkdir(parents=True)
    a, said = agent(world)
    assert a.wake() == AG.FAILED and not a.run_clean.calls and (world.state / "t-run.failed").is_file()


@pytest.mark.parametrize("mode,why", [("wrongcommit", "not the assignment's"), ("dirty", "not the assignment's"),
                                      ("badsha", "sha256"), ("extra", "not assigned")])
def test_a_wrong_manifest_or_file_pushes_nothing(world, mode, why):
    world.assign([world.entry(mode=mode)])
    a, said = agent(world)
    assert a.wake() == AG.FAILED and world.mac_refs_on_origin() == []
    assert why in json.loads((world.state / "t-run.failed").read_text(encoding="utf-8"))["reason"]
    assert a.trace == []                                          # refused before the guard and the push


def test_a_missing_output_pushes_nothing(world):
    e = world.entry()
    e["outputs"] = e["outputs"] + ["results/t_absent.csv"]
    world.assign([e])
    a, said = agent(world)
    assert a.wake() == AG.FAILED and world.mac_refs_on_origin() == []


# ------------------------------------------------------------------------------- the guard, before the push

def test_guard_refusal_pushes_nothing(world):
    """The real guard refuses a CSV with a price level; nothing is pushed. Swapping the guard and the push in
    `publish` makes this fail (the push would have happened)."""
    world.assign([world.entry(mode="price")])
    a, said = agent(world)
    assert a.wake() == AG.FAILED
    assert a.trace == ["guard"] and world.mac_refs_on_origin() == []
    assert not a.local(MA.parse(MW.git(world.lead, "show", "HEAD:" + MA.CONFIG_REL)).runs[0])
    reason = json.loads((world.state / "t-run.failed").read_text(encoding="utf-8"))["reason"]
    assert "price-level guard refused" in reason and "close" in reason


def test_a_refusing_guard_stops_any_run(world, monkeypatch):
    world.assign([world.entry()])
    a, said = agent(world)
    pushed = []
    monkeypatch.setattr(a, "guard", lambda run, idx: (a.trace.append("guard"), ["REFUSED planted"])[1])
    monkeypatch.setattr(a, "push", lambda ref: pushed.append(ref))
    assert a.wake() == AG.FAILED and pushed == [] and world.mac_refs_on_origin() == []


#: an allow-list accepting every finding of the fake run's two files (every rule, any column)
ALLOW_ALL = MW.ALLOWLIST + "".join(f"results/{f}.csv,{rule},*,a test's planted entry\n"
                                   for f in ("t_units", "t_trades") for rule in ("name", "level", "pair", "timestamp"))


def test_the_guard_reads_origin_masters_allow_list(world):
    """A local edit of the allow-list that would accept the price column is not read (the mutant A17's test: the
    entries cover every rule, so only the list's source decides)."""
    world.assign([world.entry(mode="price")])
    (world.mac / "tests" / "price_level_allowlist.csv").write_text(ALLOW_ALL, encoding="utf-8")
    a, said = agent(world)
    assert a.wake() == AG.FAILED and world.mac_refs_on_origin() == []


def test_origin_masters_allow_list_is_the_one_applied(world):
    # the positive control: the same entries committed on master let the run through
    (world.lead / "tests" / "price_level_allowlist.csv").write_text(ALLOW_ALL, encoding="utf-8")
    world.assign([world.entry(mode="price")])
    a, said = agent(world)
    assert a.wake() == AG.OK, said
    assert a.trace == ["guard", "push"] and world.mac_refs_on_origin() == ["refs/heads/mac/t-run"]


def test_a_failed_push_is_retried_with_the_guard_first(world, monkeypatch):
    world.assign([world.entry()])
    a, said = agent(world)
    real = a.git

    def offline(*args, **kw):
        if args and args[0] == "push":
            raise RuntimeError("git push: offline")
        return real(*args, **kw)

    monkeypatch.setattr(a, "git", offline)
    assert a.wake() == AG.BAD and world.mac_refs_on_origin() == [] and not (world.state / "t-run.done").exists()
    a2, said2 = agent(world)
    assert a2.wake() == AG.OK and a2.trace == ["guard", "push"] and not a2.run_clean.calls
    assert world.mac_refs_on_origin() == ["refs/heads/mac/t-run"]


@pytest.mark.parametrize("ref", ["refs/heads/master", "refs/heads/wt/wt-mac", "mac/t-run", "refs/heads/mac/T",
                                 "refs/heads/mac/t-run:refs/heads/master", "refs/heads/mac/../master",
                                 "refs/tags/mac/t-run", "+refs/heads/mac/t-run", "refs/heads/mac/a/b"])
def test_a_push_to_any_other_ref_is_refused(world, ref):
    a, _ = agent(world)
    before = world.remote_refs()
    with pytest.raises(AG.AgentRefused):
        a.push(ref)
    assert world.remote_refs() == before and "push" not in a.trace


def test_a_push_to_another_remote_is_refused(world):
    a, _ = agent(world)
    a.remote = "elsewhere"
    with pytest.raises(AG.AgentRefused):
        a.push("refs/heads/mac/t-run")


# --------------------------------------------------------------------------------------------- the timer, status

def test_the_plist_is_a_launchd_timer_for_this_tree(tmp_path):
    p = plistlib.loads(AG.plist(repo=Path("/Users/op/stage2x/stage-2-extended"), runs=Path("/Users/op/runs"),
                                python="/Users/op/stage2x/venv/bin/python"))
    assert p["Label"] == AG.LABEL and p["StartInterval"] == AG.INTERVAL_S and p["RunAtLoad"] is True
    assert p["ProgramArguments"] == ["/usr/bin/caffeinate", "-i", "/Users/op/stage2x/venv/bin/python",
                                     str(Path("/Users/op/stage2x/stage-2-extended") / "scripts" / "mac_agent.py")]
    assert p["EnvironmentVariables"]["OMP_NUM_THREADS"] == "1"
    assert p["StandardOutPath"].endswith("agent.log")


def test_status_changes_nothing(world, capsys):
    world.assign([world.entry()])
    MW.git(world.mac, "fetch", "-q", "origin")
    a, said = agent(world)
    assert a.status() == AG.OK and not a.run_clean.calls and world.mac_refs_on_origin() == []
    assert any("not done or failed: ['t-run']" in s for s in said)


# ---------------------------------------------------------------------------------------------- the collect

def run_and_push(world, **kw) -> None:
    world.assign([world.entry(**kw)])
    a, said = agent(world)
    assert a.wake() == AG.OK, said


def craft(world, name: str, edit) -> None:
    """Rewrite the run's branch on origin with `edit(files: dict[path, bytes])` applied -- what a broken or forged
    branch would hold (the agent itself refuses these before pushing)."""
    ref = f"refs/heads/mac/{name}"
    files = {p: subprocess.run(["git", "show", f"{ref}:{p}"], cwd=world.origin, capture_output=True,
                               check=True).stdout
             for p in MW.git(world.origin, "ls-tree", "-r", "--name-only", ref).splitlines()}
    edit(files)
    idx = world.tmp / "craft.index"
    if idx.exists():
        idx.unlink()
    env = {**os.environ, "GIT_INDEX_FILE": str(idx)}
    for p, data in files.items():
        blob = subprocess.run(["git", "hash-object", "-w", "--stdin"], cwd=world.origin, input=data,
                              capture_output=True, check=True).stdout.decode().strip()
        subprocess.run(["git", "update-index", "--add", "--cacheinfo", f"100644,{blob},{p}"], cwd=world.origin,
                       env=env, check=True, capture_output=True)
    tree = subprocess.run(["git", "write-tree"], cwd=world.origin, env=env, capture_output=True,
                          check=True).stdout.decode().strip()
    c = subprocess.run(["git", "commit-tree", tree, "-m", "crafted"], cwd=world.origin, capture_output=True, check=True,
                       env={**os.environ, **AG.IDENT}).stdout.decode().strip()
    MW.git(world.origin, "update-ref", ref, c)


def manifest_edit(path: str, **change):
    def edit(files):
        m = json.loads(files[path])
        for k, v in change.items():
            if k == "clean_run":
                m["provenance"]["clean_run"].update(v)
                for kk, vv in list(v.items()):
                    if vv is None:
                        m["provenance"]["clean_run"].pop(kk)
            else:
                m[k] = v
        files[path] = json.dumps(m).encode()
    return edit


def collect(world, name="t-run", hold=None):
    return CO.collect(world.pc, name, hold or world.tmp / "held", verify=plain_verify, say=lambda s: None)


def test_collect_copies_a_good_run(pushed):
    world = pushed
    dest = collect(world)
    assert sorted(p.name for p in dest.iterdir()) == sorted(["t_units.csv", "t_units.csv.manifest.json", "t_trades.csv",
                                                             "t_trades.csv.manifest.json", "run.log", "run.json"])
    body = MW.git(world.origin, "show", "refs/heads/mac/t-run:results/t_units.csv")
    assert (dest / "t_units.csv").read_bytes() == subprocess.run(
        ["git", "show", "refs/heads/mac/t-run:results/t_units.csv"], cwd=world.origin, capture_output=True).stdout
    assert body
    with pytest.raises(CO.CollectRefused, match="never overwritten"):
        collect(world)


M = "results/t_units.csv.manifest.json"


@pytest.mark.parametrize("edit,match", [
    (manifest_edit(M, git_commit="0" * 40), "not the assignment's"),
    (manifest_edit(M, git_commit=None), "not the assignment's"),
    (manifest_edit(M, git_dirty=True), "not clean"),
    (manifest_edit(M, result_file="other.csv"), "is for"),
    (manifest_edit(M, clean_run={"name": "another"}), "not from the clean run"),
    (manifest_edit(M, clean_run={"host": "someone-else"}), "host"),
    (manifest_edit(M, clean_run={"host": None}), "some manifests name a host"),
    (lambda f: f.pop("results/t_trades.csv"), "missing"),
    (lambda f: f.update({"results/more.csv": b"a\n1\n"}), "not assigned"),
    (lambda f: f.update({"run.log": f["run.log"] + b"EXIT 1\n"}), "EXIT 0"),
    (lambda f: f.update({"run.json": f["run.json"].replace(b"Q-229", b"Q-999")}), "assignment is not"),
    (lambda f: f.update({"results/t_units.csv": f["results/t_units.csv"] + b"9,9\n"}), "verify_result"),
])
def test_collect_refuses_a_mismatch(pushed, edit, match):
    world = pushed
    craft(world, "t-run", edit)
    with pytest.raises(CO.CollectRefused, match=match):
        collect(world)
    assert not (world.tmp / "held" / "t-run").exists()


def test_collect_refuses_a_holding_folder_in_results_or_a_tree(pushed):
    world = pushed
    with pytest.raises(CO.CollectRefused, match="results/ folder"):
        collect(world, hold=world.tmp / "results" / "held")
    with pytest.raises(CO.CollectRefused, match="tree of this repository"):
        collect(world, hold=ROOT / "held")


def test_collect_refuses_a_run_not_assigned(pushed):
    world = pushed
    world.assign([world.entry(name="other")])
    with pytest.raises(CO.CollectRefused, match="has no run"):
        collect(world)


@pytest.fixture()
def nohost(tmp_path, monkeypatch):
    w = MW.templated("nohost", lambda base: _build_pushed(base, "nohost"), tmp_path / "w")
    _patch(w, monkeypatch.setattr)
    yield w
    _cleanup(w)


def _nohost_run(world, checkout: str | None, run: bool = False):
    if run:
        run_and_push(world, mode="nohost")
    if checkout is not None:
        def edit(files):
            for p in (M, "results/t_trades.csv.manifest.json"):
                m = json.loads(files[p])
                m["provenance"]["clean_run"]["checkout"] = checkout
                files[p] = json.dumps(m).encode()
        craft(world, "t-run", edit)


def test_a_commit_before_the_host_field_takes_the_host_from_the_log(nohost):
    world = nohost
    _nohost_run(world, "/Users/op/stage2-extended-runs/t-run")
    said = []
    CO.collect(world.pc, "t-run", world.tmp / "held", verify=plain_verify, say=said.append)
    assert "from the run's log and the record" in said[0]


def test_a_commit_before_the_host_field_needs_a_posix_checkout(nohost):
    world = nohost
    _nohost_run(world, "C:\\Users\\x\\stage2-extended-runs\\t-run")
    with pytest.raises(CO.CollectRefused, match="POSIX"):
        collect(world)


def test_a_commit_before_the_host_field_needs_the_logs_host(nohost):
    world = nohost
    _nohost_run(world, "/Users/op/stage2-extended-runs/t-run")
    craft(world, "t-run", lambda f: f.update({"run.log": b"host: elsewhere (darwin)\n" + f["run.log"]}))
    with pytest.raises(CO.CollectRefused, match="does not name the record's host"):
        collect(world)


def test_a_commit_that_records_the_host_needs_it_in_the_manifest(world):
    (world.lead / "extended").mkdir()
    (world.lead / "extended" / "results.py").write_text(f"x = {{{CO.HOST_MARK}}}\n", encoding="utf-8")
    MW.git(world.lead, "add", "-A")
    MW.git(world.lead, "commit", "-q", "-m", "host field")
    world.commit = MW.git(world.lead, "rev-parse", "HEAD")
    _nohost_run(world, "/Users/op/stage2-extended-runs/t-run", run=True)
    with pytest.raises(CO.CollectRefused, match="records the host"):
        collect(world)


def test_this_repositorys_writer_records_the_host_as_the_collect_reads_it():
    assert CO.HOST_MARK in (ROOT / CO.RESULTS_PY).read_text(encoding="utf-8")


def test_the_collect_script_uses_the_vendored_verify(pushed):
    """End to end in its own process (the vendored verify_result imports the engine's results module): a good run is
    collected; a CSV changed after its manifest is refused with nothing copied."""
    world = pushed
    env = {**os.environ, "OMP_NUM_THREADS": "1", "PYTHONDONTWRITEBYTECODE": "1"}
    cmd = [sys.executable, str(ROOT / "scripts" / "mac_collect.py"), "--repo", str(world.pc), "--run", "t-run"]
    ok = subprocess.run([*cmd, "--hold", str(world.tmp / "held")], capture_output=True, text=True, env=env, timeout=300)
    assert ok.returncode == 0 and "COLLECTED" in ok.stdout, ok.stderr
    craft(world, "t-run", lambda f: f.update({"results/t_units.csv": f["results/t_units.csv"] + b"9,9\n"}))
    bad = subprocess.run([*cmd, "--hold", str(world.tmp / "held2")], capture_output=True, text=True, env=env,
                         timeout=300)
    assert bad.returncode == 1 and "has been modified since it was written" in bad.stderr, bad.stderr
    assert not (world.tmp / "held2" / "t-run").exists()


def test_a_commit_missing_from_the_clone_is_refused(nohost, monkeypatch):
    world = nohost
    _nohost_run(world, "/Users/op/stage2-extended-runs/t-run")
    real = CO._git

    def no_commit(repo, *args, check=True):
        if args[:2] == ("cat-file", "-e"):
            return subprocess.CompletedProcess(args, 128, b"", b"missing")
        return real(repo, *args, check=check)

    monkeypatch.setattr(CO, "_git", no_commit)
    with pytest.raises(CO.CollectRefused, match="not in this clone"):
        collect(world)


def test_the_agents_git_never_prompts(world, monkeypatch):
    seen = []
    real = AG.subprocess.run

    def spy(cmd, *a, **kw):
        seen.append((kw.get("env") or {}).get("GIT_TERMINAL_PROMPT"))
        return real(cmd, *a, **kw)

    a, _ = agent(world)
    monkeypatch.setattr(AG.subprocess, "run", spy)
    a.git("rev-parse", "HEAD")
    assert seen == ["0"]
