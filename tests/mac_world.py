"""Q-229's synthetic world for the Mac run agent's tests: a fake origin (`git init --bare` in a temporary folder), the
lead's seed tree that pushes master to it, the Mac's clone (the agent's tree) and the PC's clone (the collect's), and a
fake run command (`scripts/fake_run.py` in the fake repository) that writes result files with sidecar manifests in the
vendored writer's form. No real bars, no engine, no run lock of this machine (the lock is a temporary file)."""
from __future__ import annotations

import atexit
import contextlib
import dataclasses
import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

FAKE_RUN = r'''"""A fake run (Q-229 tests): writes each --out CSV and a manifest in the vendored writer's form."""
import hashlib, json, os, subprocess, sys
from pathlib import Path

args = sys.argv[1:]
mode = args[args.index("--mode") + 1]
outs = [args[i + 1] for i, a in enumerate(args) if a == "--out"]
print("fake run", mode, flush=True)
if mode == "fail":
    print("Traceback (most recent call last): a planted failure", flush=True)
    sys.exit(1)
head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
for o in outs:
    p = Path(o)
    p.parent.mkdir(parents=True, exist_ok=True)
    if mode == "price":
        body = "row,close\n" + "".join(f"{i},{15000 + i * 0.25}\n" for i in range(10))
    else:
        body = "unit,value\n" + "".join(f"{i},{i * 3}\n" for i in range(10))
    p.write_bytes(body.encode())
    commit = "0" * 40 if mode == "wrongcommit" else head
    # as extended/results.py writes it (no host: the file is frozen), the checkout as the Mac's would be named
    clean = {"name": os.environ["S2X_CLEAN_RUN"], "marker": "S2X_CLEAN_RUN",
             "checkout": "/Users/op/stage2-extended-runs/" + os.environ["S2X_CLEAN_RUN"]}
    m = {"result_file": p.name, "script": "scripts/fake_run.py", "seed": None, "parameters": {"mode": mode},
         "timestamp": "2026-11-27T00:00:00+00:00", "rows": 10, "columns": body.split("\n")[0].split(","),
         "git_commit": commit + ("-dirty" if mode == "dirty" else ""), "git_dirty": mode == "dirty",
         "sha256": hashlib.sha256(b"tampered" if mode == "badsha" else p.read_bytes()).hexdigest(),
         "provenance": {"clean_run": clean}}
    Path(o + ".manifest.json").write_text(json.dumps(m, indent=2, sort_keys=True) + "\n")
if mode == "extra":
    Path("results/not_assigned.csv").write_text("a\n1\n")
'''

ALLOWLIST = "file,rule,column,reason\n"


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def load_run_clean():
    spec = importlib.util.spec_from_file_location("s2x_run_clean_q229", SCRIPTS / "run_clean.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@dataclass
class World:
    tmp: Path
    origin: Path
    lead: Path          # the lead's tree: edits master, pushes
    mac: Path           # the agent's clone
    pc: Path            # the collect's clone
    runs: Path
    state: Path
    commit: str         # the commit the runs are made from

    def assign(self, runs: list[dict], acks: tuple[str, ...] = ()) -> None:
        doc = {"version": 1, "about": "test", "runs": runs, "failures_acknowledged": list(acks)}
        (self.lead / "config").mkdir(exist_ok=True)
        (self.lead / "config" / "mac_assignments.json").write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        git(self.lead, "add", "-A")
        git(self.lead, "commit", "-q", "-m", "assignments")
        git(self.lead, "push", "-q", "origin", "master")

    def entry(self, name: str = "t-run", mode: str = "ok", outputs: tuple[str, ...] = ("results/t_units.csv",
                                                                                         "results/t_trades.csv"),
              **kw) -> dict:
        cmd = f"python scripts/fake_run.py --mode {mode}" + "".join(f" --out {o}" for o in outputs)
        e = {"name": name, "commit": self.commit, "command": cmd, "hours": 1.0, "mem_gb": 1.0, "task": "Q-229",
             "outputs": list(outputs)}
        e.update(kw)
        return e

    def remote_refs(self) -> dict[str, str]:
        out = git(self.origin, "for-each-ref", "--format=%(refname) %(objectname)")
        return dict(line.split(" ", 1) for line in out.splitlines() if line) if out else {}

    def mac_refs_on_origin(self) -> list[str]:
        return [r for r in self.remote_refs() if r.startswith("refs/heads/mac/")]


def make_world(tmp: Path) -> World:
    tmp.mkdir(parents=True, exist_ok=True)
    origin = tmp / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "master", str(origin)], check=True, capture_output=True)
    lead = tmp / "lead"
    lead.mkdir()
    git(lead, "init", "-q", "-b", "master")
    for k, v in (("user.email", "t@example.invalid"), ("user.name", "t"), ("core.autocrlf", "false")):
        git(lead, "config", k, v)
    (lead / "scripts").mkdir()
    (lead / "scripts" / "fake_run.py").write_text(FAKE_RUN, encoding="utf-8")
    (lead / "tests").mkdir()
    (lead / "tests" / "price_level_allowlist.csv").write_text(ALLOWLIST, encoding="utf-8")
    (lead / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
    git(lead, "add", "-A")
    git(lead, "commit", "-q", "-m", "code")
    commit = git(lead, "rev-parse", "HEAD")
    git(lead, "remote", "add", "origin", str(origin))
    git(lead, "push", "-q", "origin", "master")
    clones = []
    for name in ("mac", "pc"):
        subprocess.run(["git", "clone", "-q", str(origin), str(tmp / name)], check=True, capture_output=True)
        git(tmp / name, "config", "core.autocrlf", "false")
        clones.append(tmp / name)
    return World(tmp=tmp, origin=origin, lead=lead, mac=clones[0], pc=clones[1], runs=tmp / "runs",
                 state=tmp / "state", commit=commit)


PARTS = ("origin.git", "lead", "mac", "pc")
_BUILT: dict[str, "World"] = {}


def copy_world(src: "World", tmp: Path) -> "World":
    """A full copy of `src`'s four repositories under `tmp`, each clone's remote repointed at the copy's own origin
    (checked: no copy names the source's folder afterwards, so no test can push into a shared template)."""
    for part in PARTS:
        shutil.copytree(src.tmp / part, tmp / part, symlinks=True)
    new = (tmp / "origin.git").as_posix()
    for part in ("lead", "mac", "pc"):
        cfg = tmp / part / ".git" / "config"
        t = cfg.read_text(encoding="utf-8")
        for form in (str(src.origin).replace("\\", "\\\\"), str(src.origin), src.origin.as_posix()):
            t = t.replace(form, new)
        cfg.write_text(t, encoding="utf-8")
        here = cfg.read_text(encoding="utf-8")
        forms = (src.tmp.as_posix(), str(src.tmp), str(src.tmp).replace("\\", "\\\\"))
        assert not any(f in here for f in forms), f"{cfg} still names the template"
    return dataclasses.replace(src, tmp=tmp, origin=tmp / "origin.git", lead=tmp / "lead", mac=tmp / "mac",
                               pc=tmp / "pc", runs=tmp / "runs", state=tmp / "state")


def templated(key: str, build: Callable[[Path], "World"], tmp: Path) -> "World":
    """`build`'s world, made once a process for `key`, copied into `tmp` for each test (Q-226's method)."""
    src = _BUILT.get(key)
    if src is None:
        base = Path(tempfile.mkdtemp(prefix=f"s2x_mac_world_{key}_"))
        atexit.register(shutil.rmtree, base, True)
        src = _BUILT[key] = build(base / "w")
    return copy_world(src, tmp)


def in_process_run_clean(RC):
    """The real `scripts/run_clean.py`'s `main`, in this process (its module's tree and folders monkeypatched by the
    caller), its output captured: the agent's `run_clean` hook."""
    calls: list[list[str]] = []

    def call(args: list[str]) -> tuple[int, list[str]]:
        calls.append(list(args))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            try:
                rc = RC.main(list(args))
            except SystemExit as exc:
                print(exc.code)
                rc = exc.code if isinstance(exc.code, int) else 1
        return int(rc), buf.getvalue().splitlines()

    call.calls = calls          # type: ignore[attr-defined]
    return call
