"""The Mac run agent (Q-229, E-298 (4)): one assigned heavy run per wake on the operator's Mac, its result files put on
a branch `mac/<run>` for the lead to collect -- never a record, never a merge, never an order.

    python scripts/mac_agent.py              # one wake: at most one run, then exit (by hand, or the launchd timer)
    python scripts/mac_agent.py --status     # the lock, the markers and the next assignment; changes nothing
    python scripts/mac_agent.py --plist      # the launchd timer's plist for this tree, on stdout

Started by the operator in their own clone (`~/stage2x/stage-2-extended`), or every `INTERVAL_S` seconds by the
launchd timer `--plist` prints. Each wake:

(a) `git fetch origin`, then reads `config/mac_assignments.json` **from `origin/master`** (`git show`), never a local
    copy; the schema (`extended.mac_assignments`) refuses the whole file on any problem, and nothing runs.
(b) Skips every run already done -- its branch `mac/<run>` is on origin, or a local done-marker -- and every run that
    failed (a failure marker). While a failure is not acknowledged in the file (`failures_acknowledged`), it starts
    nothing new (exit 6): the lead decides (the failure protocol). A run whose branch was made but not pushed (the
    network failed) is finished first: the guard again, then the push.
(c) Takes the Mac's own `run.lock` through `scripts/run_clean.py --hours --mem-gb --task`, after a look of its own: a
    lock that is held (exit 3), or memory that is short or cannot be read (exit 4), means it does nothing and exits --
    it never steals or breaks a lock. A checkout or log of the run left from an earlier wake with no marker (an
    interrupted run) is a failure: it is never re-run by itself.
(d) Runs the assignment's exact command through `run_clean.py --commit <sha>`: a clean, detached checkout at the named
    commit, one BLAS thread, watched to its exit (the log beside the checkout, `<RUNS_DIR>/<run>.log`). "python" is
    this agent's own interpreter (the venv's).
(e) On exit 0 it checks that the checkout changed exactly the assignment's outputs and their manifests, each manifest
    at the commit and clean, each CSV matching its manifest's sha256; builds, in a temporary index (no hook: no code
    is committed and no commit is made on a branch of the tree), a commit holding only those files, the run's log
    (`run.log`) and a record (`run.json`: the assignment as read, the host, the exit, each file's sha256); runs **the
    price-level guard** (`extended.price_levels.check_tree` on that index, the pre-commit hook's own mode, with
    origin/master's allow-list) on exactly those files, **before any push**; if it refuses, nothing is pushed and the
    run is marked failed, loudly. Then it pushes that one branch, `refs/heads/mac/<run>`, and nothing else -- never
    master, never a `wt/` branch (`push` refuses any other ref).
(f) On a non-zero exit it pushes nothing and writes a failure marker with the log's tail; that assignment is never
    re-run by the agent.
(g) One run per wake, then exit.

It writes no record and no result into the tree it runs from (its markers live in `<RUNS_DIR>/mac-agent/`), reads no
data but what the run reads, and calls no broker or firm. `STOP` in its state folder makes every wake exit at once.

Exit codes: 0 done or nothing to do; 2 the file refused, git failed, a commit not on origin, a push failed (retried
next wake); 3 the lock held (or another agent running); 4 memory short or unreadable; 5 a failure marked now;
6 blocked by an unacknowledged failure.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import plistlib
import re
import socket
import subprocess
import sys
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for _p in (str(ROOT), str(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import run_lock as RL  # noqa: E402

from extended import RUNS_DIR  # noqa: E402
from extended import mac_assignments as MA  # noqa: E402

REMOTE = "origin"
#: the only refs the agent ever pushes
MAC_REF = re.compile(r"refs/heads/mac/" + MA.NAME.pattern)
STATE_NAME = "mac-agent"
LABEL = "com.stage2x.mac-agent"
INTERVAL_S = 1800
TAIL = 60
RECORD, LOG = "run.json", "run.log"
OK, BAD, HELD, MEMORY, FAILED, BLOCKED = 0, 2, 3, 4, 5, 6
#: the identity a `mac/<run>` commit is made under (no personal detail)
IDENT = {"GIT_AUTHOR_NAME": "stage2x mac agent", "GIT_AUTHOR_EMAIL": "mac-agent@localhost.invalid",
         "GIT_COMMITTER_NAME": "stage2x mac agent", "GIT_COMMITTER_EMAIL": "mac-agent@localhost.invalid"}
LOCK_REFUSED = "REFUSED: the run lock was not taken"


class AgentRefused(RuntimeError):
    """Something the agent must never do (a push to a ref that is not `mac/<run>`)."""


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


@contextlib.contextmanager
def single_instance(path: Path) -> Iterator[bool]:
    """True while this process alone holds the agent's own instance lock (an OS lock, gone with the process)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    f = open(path, "w")
    try:
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            yield False
            return
        yield True
    finally:
        f.close()


class Agent:
    """One wake of the agent over the clone `repo` (production: this tree), with its checkouts in `runs` (production:
    `RUNS_DIR`, where `run_clean.py` makes them) and its markers in `state`."""

    def __init__(self, repo: Path = ROOT, runs: Path = RUNS_DIR, state: Path | None = None, *,
                 python: str = sys.executable,
                 run_clean: Callable[[list[str]], tuple[int, list[str]]] | None = None,
                 say: Callable[[str], None] | None = None):
        self.repo, self.runs = Path(repo), Path(runs)
        self.state = Path(state) if state is not None else self.runs / STATE_NAME
        self.tmp = self.state / "tmp"
        self.python = python
        self.run_clean = run_clean or self._run_clean_child
        self._say = say or (lambda s: print(s, flush=True))
        self.remote = REMOTE
        self.trace: list[str] = []          # the order of the guard and the push, for the tests
        self.host = socket.gethostname()

    # ---------------------------------------------------------------------------------------------------- plumbing
    def say(self, s: str) -> None:
        self._say(f"mac_agent: {s}")

    def git(self, *args: str, env: dict[str, str] | None = None, check: bool = True) -> subprocess.CompletedProcess:
        # never a prompt: under the timer no one can answer it (a credential that does not work fails the wake)
        env = {**(env if env is not None else os.environ), "GIT_TERMINAL_PROMPT": "0"}
        out = subprocess.run(["git", *args], cwd=self.repo, capture_output=True, env=env, timeout=600)
        if check and out.returncode:
            raise RuntimeError(f"git {' '.join(args)}: {out.stderr.decode('utf-8', 'replace').strip()}")
        return out

    def text(self, *args: str, env: dict[str, str] | None = None) -> str:
        return self.git(*args, env=env).stdout.decode("utf-8").strip()

    def _index_env(self, idx: Path, extra: dict[str, str] | None = None) -> dict[str, str]:
        env = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")}
        env["GIT_INDEX_FILE"] = str(idx.absolute())
        env.update(extra or {})
        return env

    def _has(self, ref: str) -> str | None:
        out = self.git("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}", check=False)
        return out.stdout.decode().strip() or None if out.returncode == 0 else None

    def _run_clean_child(self, args: list[str]) -> tuple[int, list[str]]:
        """`scripts/run_clean.py` in its own process, its output streamed and its last lines kept."""
        tail: deque[str] = deque(maxlen=TAIL)
        p = subprocess.Popen([self.python, str(self.repo / "scripts" / "run_clean.py"), *args], cwd=self.repo,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                             errors="replace")
        assert p.stdout is not None
        for line in p.stdout:
            line = line.rstrip("\n")
            print(line, flush=True)
            tail.append(line)
        return p.wait(), list(tail)

    # ------------------------------------------------------------------------------------------------------ state
    def marker(self, run: str, kind: str) -> Path:
        return self.state / f"{run}.{kind}"

    def fail(self, run: MA.Run, reason: str, tail: list[str] | None = None) -> int:
        """Mark `run` failed (never re-run by the agent), loudly; nothing is pushed."""
        self.state.mkdir(parents=True, exist_ok=True)
        rec = {"run": run.name, "commit": run.commit, "task": run.task, "host": self.host, "when": _now(),
               "reason": reason, "log_tail": list(tail or [])[-TAIL:]}
        self.marker(run.name, "failed").write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
        bar = "=" * 100
        self.say(bar)
        self.say(f"FAILED: {run.name} ({run.task}) -- {reason}")
        for line in rec["log_tail"][-20:]:
            self.say(f"  | {line}")
        self.say(f"Nothing was pushed. The marker is {self.marker(run.name, 'failed')}. The agent never re-runs this "
                 "assignment by itself: tell the lead (the failure protocol).")
        self.say(bar)
        return FAILED

    def done(self, run: MA.Run, commit: str) -> None:
        self.state.mkdir(parents=True, exist_ok=True)
        self.marker(run.name, "done").write_text(json.dumps(
            {"run": run.name, "branch": f"mac/{run.name}", "commit": commit, "when": _now()}, indent=2) + "\n",
            encoding="utf-8")

    # ------------------------------------------------------------------------------------------------ assignments
    def assignments(self) -> MA.Book:
        out = self.git("show", f"{self.remote}/master:{MA.CONFIG_REL}", check=False)
        if out.returncode:
            raise MA.AssignmentError([f"{self.remote}/master has no {MA.CONFIG_REL}"])
        return MA.parse(out.stdout.decode("utf-8"))

    def on_origin(self, run: MA.Run) -> str | None:
        return self._has(f"refs/remotes/{self.remote}/mac/{run.name}")

    def local(self, run: MA.Run) -> str | None:
        return self._has(f"refs/heads/mac/{run.name}")

    def commit_on_origin(self, sha: str) -> bool:
        if self.git("cat-file", "-e", f"{sha}^{{commit}}", check=False).returncode:
            return False
        out = self.git("branch", "-r", "--contains", sha, check=False)
        return out.returncode == 0 and bool(out.stdout.strip())

    # ---------------------------------------------------------------------------------------------------- the wake
    def wake(self) -> int:
        if (self.state / "STOP").exists():
            self.say(f"STOP is present in {self.state}: nothing started")
            return OK
        with single_instance(self.state / "agent.instance") as alone:
            if not alone:
                self.say("another wake of the agent is running: nothing started")
                return HELD
            return self._wake()

    def _wake(self) -> int:
        try:
            self.git("fetch", "--quiet", self.remote)
        except RuntimeError as exc:
            self.say(f"git fetch failed, nothing started: {exc}")
            return BAD
        try:
            book = self.assignments()
        except MA.AssignmentError as exc:
            self.say(f"REFUSED: {exc}")
            return BAD
        failed = [r for r in book.runs if self.marker(r.name, "failed").exists()]
        for r in failed:
            ack = "acknowledged by the lead" if r.name in book.failures_acknowledged else "NOT acknowledged"
            self.say(f"failed earlier, never re-run by the agent: {r.name} ({ack})")
        blocking = [r.name for r in failed if r.name not in book.failures_acknowledged]
        if blocking:
            self.say(f"BLOCKED: unacknowledged failure(s) {blocking}; nothing new starts until the lead lists them in "
                     f"failures_acknowledged on master")
            return BLOCKED
        nxt = None
        for r in book.runs:
            if self.marker(r.name, "done").exists() or self.marker(r.name, "failed").exists():
                continue
            pushed = self.on_origin(r)
            if pushed:
                self.done(r, pushed)
                continue
            if self.local(r):
                self.say(f"{r.name}: its branch was made but not pushed; the guard again, then the push")
                return self.republish(r)
            nxt = r
            break
        if nxt is None:
            self.say("nothing to run: every assignment is done or failed")
            return OK
        return self.start(nxt)

    def start(self, run: MA.Run) -> int:
        if not self.commit_on_origin(run.commit):
            self.say(f"{run.name}: the commit {run.commit} is not on {self.remote}; nothing started (the lead pushes it)")
            return BAD
        held = RL.read()
        if held is not None:
            self.say(f"the run lock is held, nothing started (never stolen): {RL.describe(held)}")
            return HELD
        gb = RL.available_gb()
        if gb is None:
            self.say("this machine's available memory cannot be read: nothing started")
            return MEMORY
        if gb < run.mem_gb:
            self.say(f"{gb:.2f} GB available, {run.name} needs {run.mem_gb:.2f} GB: nothing started")
            return MEMORY
        wt, log = self.runs / run.name, self.runs / f"{run.name}.log"
        if wt.exists() or log.exists():
            return self.fail(run, f"a checkout or log of this run is left from an earlier wake ({wt}, {log}) with no "
                                  "marker -- an interrupted run; it is not re-run by itself")
        argv = [self.python, *run.argv()[1:]]
        args = ["--name", run.name, "--commit", run.commit, "--hours", repr(run.hours), "--mem-gb", repr(run.mem_gb),
                "--task", run.task, "--holder", f"mac_agent ({self.host})", "--", *argv]
        self.say(f"RUN {run.name} ({run.task}) at {run.commit[:12]}: {run.command}")
        rc, tail = self.run_clean(args)
        if not log.exists():
            if rc in (HELD, MEMORY) and any(line.startswith(LOCK_REFUSED) for line in tail):
                self.say(f"run_clean did not take the lock (exit {rc}); nothing started")
                return rc
            return self.fail(run, f"run_clean exited {rc} before the command ran", tail)
        lines = log.read_text(encoding="utf-8", errors="replace").splitlines()
        last = lines[-1] if lines else ""
        m = re.fullmatch(r"EXIT (-?\d+)", last)
        if rc != 0 or m is None or int(m.group(1)) != 0:
            return self.fail(run, f"the run exited {rc} (its log's last line: {last!r})", lines[-TAIL:])
        self.say(f"{run.name}: exit 0; checking its files")
        return self.publish(run, wt, log)

    # ------------------------------------------------------------------------------------------- the files, pushed
    def changed(self, wt: Path) -> list[str]:
        out = subprocess.run(["git", "status", "--porcelain", "-z", "--untracked-files=all"], cwd=wt,
                             capture_output=True, text=True, encoding="utf-8", check=True).stdout
        paths, skip = [], False
        for p in out.split("\0"):
            if skip:
                skip = False
                continue
            if len(p) > 3:
                paths.append(p[3:])
                skip = p[0] in "RC"
        return paths

    def file_problems(self, run: MA.Run, wt: Path) -> list[str]:
        """Why the checkout's changes are not exactly the assignment's outputs, each at the commit and clean."""
        want, got = MA.expected_files(run), set(self.changed(wt))
        bad = [f"missing: {p}" for p in sorted(want - got)] + [f"not assigned: {p}" for p in sorted(got - want)]
        if bad:
            return bad
        for o in run.outputs:
            try:
                m = json.loads((wt / (o + MA.MANIFEST_SUFFIX)).read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                bad.append(f"{o}: its manifest cannot be read ({exc})")
                continue
            if m.get("git_commit") != run.commit or m.get("git_dirty") is not False:
                bad.append(f"{o}: its manifest's commit is {m.get('git_commit')!r} (dirty {m.get('git_dirty')!r}), not "
                           f"the assignment's {run.commit}, clean")
            if m.get("sha256") != _sha256(wt / o):
                bad.append(f"{o}: the file does not match its manifest's sha256")
        return bad

    def build_index(self, run: MA.Run, files: dict[str, Path]) -> Path:
        self.tmp.mkdir(parents=True, exist_ok=True)
        idx = self.tmp / f"{run.name}.index"
        if idx.exists():
            idx.unlink()
        env = self._index_env(idx)
        for rel, src in sorted(files.items()):
            sha = self.text("hash-object", "-w", "--no-filters", "--", str(src))
            self.git("update-index", "--add", "--cacheinfo", f"100644,{sha},{rel}", env=env)
        return idx

    def guard(self, run: MA.Run, idx: Path) -> list[str]:
        """The price-level guard (Q-131) on exactly the index's files, as the pre-commit hook runs it (`check_tree` on
        the commit's own index), judged against origin/master's allow-list. Its problems; empty when it passes. The
        allow-list's stale entries are not judged here: they are about the whole tree, not these files."""
        self.trace.append("guard")
        from extended import price_levels as PL
        allow_file = self.tmp / "price_level_allowlist.csv"
        out = self.git("show", f"{self.remote}/master:{PL.ALLOWLIST_REL}", check=False)
        if out.returncode:
            return [f"{self.remote}/master has no {PL.ALLOWLIST_REL}"]
        allow_file.write_bytes(out.stdout)
        try:
            rep = PL.check_tree(self.repo, source="index", index_file=str(idx), allow=PL.load_allowlist(allow_file))
        except (OSError, RuntimeError, ValueError) as exc:
            return [f"the guard could not run: {exc}"]
        bad = [f"REFUSED {f}" for f in rep.refused]
        if set(rep.files) != set(run.outputs):
            bad.append(f"the guard scanned {sorted(rep.files)}, not exactly the outputs {sorted(run.outputs)}")
        return bad

    def push(self, ref: str) -> None:
        """Push the one branch `ref` (`refs/heads/mac/<run>`) to origin under its own name; any other ref refused."""
        if not MAC_REF.fullmatch(ref) or self.remote != REMOTE:
            raise AgentRefused(f"REFUSED: the agent pushes only refs/heads/mac/<run> to {REMOTE}, not {ref!r}")
        self.trace.append("push")
        self.git("push", "--porcelain", self.remote, f"{ref}:{ref}")

    def publish(self, run: MA.Run, wt: Path, log: Path) -> int:
        bad = self.file_problems(run, wt)
        if bad:
            return self.fail(run, "the run's files are not the assignment's: " + "; ".join(bad))
        record = {"run": run.name, "assignment": run.as_dict(), "host": self.host, "platform": sys.platform,
                  "python": sys.version.split()[0], "exit": 0, "finished": _now(),
                  "origin_master": self._has(f"refs/remotes/{self.remote}/master"),
                  "agent_head": self._has("HEAD"),
                  "files": {p: _sha256(wt / p) for p in sorted(MA.expected_files(run))}, "log": LOG,
                  "log_sha256": _sha256(log)}
        self.tmp.mkdir(parents=True, exist_ok=True)
        rec = self.tmp / f"{run.name}.{RECORD}"
        rec.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        files = {p: wt / p for p in MA.expected_files(run)}
        files[LOG], files[RECORD] = log, rec
        idx = self.build_index(run, files)
        bad = self.guard(run, idx)
        if bad:
            return self.fail(run, "the price-level guard refused the run's files: " + "; ".join(bad))
        tree = self.text("write-tree", env=self._index_env(idx))
        msg = (f"mac/{run.name}: {run.task} at {run.commit[:12]} on {self.host}, exit 0 (scripts/mac_agent.py, Q-229)")
        commit = self.text("commit-tree", tree, "-m", msg, env=self._index_env(idx, IDENT))
        ref = f"refs/heads/mac/{run.name}"
        self.git("update-ref", ref, commit, "")                       # made only if it does not exist
        return self._push_and_mark(run, ref, commit)

    def republish(self, run: MA.Run) -> int:
        ref = f"refs/heads/mac/{run.name}"
        commit = self.local(run)
        assert commit is not None
        self.tmp.mkdir(parents=True, exist_ok=True)
        idx = self.tmp / f"{run.name}.index"
        if idx.exists():
            idx.unlink()
        self.git("read-tree", f"{commit}^{{tree}}", env=self._index_env(idx))
        have = set(self.text("ls-files", env=self._index_env(idx)).splitlines())
        want = MA.expected_files(run) | {LOG, RECORD}
        if have != want:
            return self.fail(run, f"the unpushed branch {ref} holds {sorted(have)}, not {sorted(want)}")
        bad = self.guard(run, idx)
        if bad:
            return self.fail(run, "the price-level guard refused the run's files: " + "; ".join(bad))
        return self._push_and_mark(run, ref, commit)

    def _push_and_mark(self, run: MA.Run, ref: str, commit: str) -> int:
        try:
            self.push(ref)
        except RuntimeError as exc:
            if isinstance(exc, AgentRefused):
                raise
            self.say(f"the push of {ref} failed ({exc}); it is tried again at the next wake, the guard first")
            return BAD
        self.done(run, commit)
        self.say(f"PUSHED mac/{run.name} ({commit[:12]}): {len(run.outputs)} result file(s) with their manifests, the "
                 "log and the record. Tell the lead it is there.")
        return OK

    # ------------------------------------------------------------------------------------------------------ status
    def status(self) -> int:
        RL.status(None)
        self.say(f"state folder {self.state}{' (STOP present)' if (self.state / 'STOP').exists() else ''}")
        for p in sorted(self.state.glob("*.done")) + sorted(self.state.glob("*.failed")):
            self.say(f"  {p.name}")
        try:
            book = self.assignments()
        except (MA.AssignmentError, RuntimeError) as exc:
            self.say(f"the assignment file (as last fetched) is refused: {exc}")
            return BAD
        todo = [r.name for r in book.runs if not (self.marker(r.name, "done").exists()
                                                  or self.marker(r.name, "failed").exists())]
        self.say(f"assignments as last fetched: {len(book.runs)}; not done or failed: {todo}")
        return OK


def plist(repo: Path = ROOT, runs: Path = RUNS_DIR, python: str = sys.executable) -> bytes:
    """The launchd timer: every `INTERVAL_S` seconds (and at load), under `caffeinate -i` so the Mac does not idle-sleep
    during a run; its output appended to `<RUNS_DIR>/mac-agent/agent.log`."""
    state = Path(runs) / STATE_NAME
    return plistlib.dumps({
        "Label": LABEL,
        "ProgramArguments": ["/usr/bin/caffeinate", "-i", str(python), str(Path(repo) / "scripts" / "mac_agent.py")],
        "WorkingDirectory": str(repo),
        "StartInterval": INTERVAL_S,
        "RunAtLoad": True,
        "StandardOutPath": str(state / "agent.log"),
        "StandardErrorPath": str(state / "agent.log"),
        "EnvironmentVariables": {"PATH": "/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/opt/homebrew/bin",
                                 "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
                                 "PYTHONUNBUFFERED": "1"},
    })


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--status", action="store_true", help="the lock, the markers, the next assignment; no change")
    ap.add_argument("--plist", action="store_true", help="print the launchd timer's plist for this tree")
    a = ap.parse_args(argv)
    if a.plist:
        sys.stdout.buffer.write(plist())
        return OK
    agent = Agent()
    if a.status:
        return agent.status()
    agent.say(f"wake at {_now()} on {agent.host} ({sys.platform})")
    return agent.wake()


if __name__ == "__main__":
    raise SystemExit(main())
