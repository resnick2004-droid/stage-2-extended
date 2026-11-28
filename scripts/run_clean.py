"""Run a command from a clean, detached checkout of one commit, then bring its result files home (Stage 2 D-474, ported).

    python scripts/run_clean.py --name u1-identity --hours 1 --mem-gb 1.5 --task Q-05 -- python identity/stage2_identity.py --only u1 --u1-starts all
    python scripts/run_clean.py --name f01-a --commit 1a2b3c4 -- python scripts/<script>.py   # no lock: light only
    python scripts/run_clean.py --name f01-a --collect      # copy the run's result files into this tree
    python scripts/run_clean.py --name f01-a --remove       # unlink the stores, remove the checkout

A result's manifest reads the tree's git state when the CSV is written (Stage 2 D-178); in a shared tree any other
session's file would stamp it `-dirty`. So a run gets its own tree:

1. `git worktree add --detach` at the commit (default HEAD; this tree must then be clean, so HEAD is what was meant)
   in `%LOCALAPPDATA%/stage2-extended-runs/<name>`, outside OneDrive (OneDrive locks files under a running job).
2. The git-ignored licensed stores `vendor/stage2/data/bars` and `vendor/stage2/data/atlas` are linked in from **this
   tree's** copy as directory junctions (`scripts/worktrees.py`'s `link`), read where they are, never copied; the
   checkout's `git status` must be empty before the command runs.
3. The command runs inside the checkout with one BLAS thread, no bytecode, and the clean-run marker
   `S2X_CLEAN_RUN=<name>` -- the only condition under which `extended.results.write_result` writes into `results/`
   and `extended.reader` lets a family read the judged block -- and the run id `S2X_RUN_ID=<name>@<UTC time>`, new
   for every run (a reused checkout included), by which the reader's once-rule tells runs apart (Q-32).
   Under the lock it also sets `S2X_LOCK_HOLDER=<name>` (the lock's job), by which the root `conftest.py` lets this
   command, and no other process, run tests marked `heavy` while the lock is held (Q-118).
   Its output goes to `<name>.log` beside the checkout (never inside it: an untracked log would stamp it `-dirty`),
   starting with a `host: <name> (<platform>)` line (Q-229) and ending with an `EXIT <code>` line.
4. **The lock** (E-005, E-006): with `--hours H --mem-gb G` (and `--task`), `run.lock` is taken through
   `scripts/run_lock.py` before anything else, the command's pid and log are recorded in it, and it is released after,
   whatever the exit; a refused lock (held: 3; memory short: 4) means the command does not run. Heavy runs use it.
5. `--collect` copies every file the run changed or created into this tree, refusing (nothing copied) a file this
   tree or a later commit changed since the run's commit, a file the run deleted, and any existing file under
   `results/` it would replace -- a result file is never overwritten (DIRECTIVE Part 1). The append-only files
   (`APPEND_ONLY`: the variant log `results/variants.jsonl` and the judged block's read ledger
   `results/read_ledger.jsonl`, Q-32) come home as a **union** (Q-67, E-044 (4)): their lines are independent records,
   so two runs made from commits whose copies lack each other's lines must both come home, whichever is collected
   first. For such a file the base is its copy at the run's commit, as the checkout holds it (`git cat-file
   --filters`; empty if the commit has none), and the collection is refused (nothing copied) unless the run's copy
   starts with that base byte for byte (the run only appended) and its appended part ends in a newline (no cut line)
   and holds no blank line (a union would drop it silently), and this tree's copy -- which later commits and earlier collections may have extended -- ends in a newline and has
   lost no line of the base, nor of this tree's HEAD (`extended.reader.missing_lines`, a multiset); then each line of
   the run's copy this tree's copy lacks (counted with multiplicity, so collecting twice is a no-op) is appended to
   it, in the run's order, the result verified (the ledger by `extended.reader.read_ledger`) and put in place
   atomically. A later commit's or this tree's own change to such a file is no clash: the union's conditions replace
   that check for it.
6. `--remove` refuses while a file the run produced is not home (`--collect` first, or `--discard` to drop it), then
   unlinks the junctions -- never through them -- and removes the checkout. An append-only file is home when every
   line of the run's copy is in this tree's (a multiset; other lines beside them do not matter).
7. **The verified input supply** (Q-230, E-302 (2), E-297 (3)): `--supply <commit>=<path>` (repeatable; the path a
   result CSV or a glob of them, e.g. `.../h3a-a4-1/results/h3a_a4_1_*.csv`) copies finished results another clean run
   wrote into the new checkout's `results/` before the command -- H3-A's reports (their slots' outputs), a run that
   needs S1's git-ignored `results/s1_range.csv`, H4-B's merge from held parts. **Nothing runs** (no lock taken, no
   checkout made) unless every supplied CSV has its sidecar manifest beside it, `extended.results.verify_result`
   passes on the source (run in a process of its own), the manifest names the file (`result_file`), its sha256 is the
   file's, its `git_commit` is the declared commit (resolved to its full sha) and `git_dirty` is False; the checkout
   must be new (a supply is made at a checkout's creation) and no destination `results/<same name>` (CSV or manifest)
   may exist in it (never overwritten). The copies (CSV and manifest) are byte-checked against their sources and made
   read-only; each one's path, source and sha256 go in the record `<name>.supply.json` beside the log (never inside
   the checkout). The clean check before the command then admits exactly the supplied files (an ignored one, like
   S1's, is not seen at all) and nothing else, and re-checks every supplied file's sha256. For the command's own git
   (the vendored writer's dirty check, Stage 2 D-178) the supplied paths -- exactly those, anchored -- are excluded
   through `core.excludesFile` set in its environment (`GIT_CONFIG_COUNT`; the file `<name>.supply.exclude` beside
   the log, the user's global excludes copied in first), so a result the command writes is stamped clean when the code
   is; the checkout is shown clean under that exclusion before the command starts. After the command every supplied
   file is re-checked: one changed or missing is named in the log and makes run_clean exit non-zero (the command's
   own code, or `SUPPLY_CHANGED` = 7 when that was 0). `--collect` never brings a supplied file back (and refuses,
   nothing copied, while one differs from its record); `--remove` counts the supplied files as inputs, not output,
   makes them writable again to remove the checkout, and renames the record `<name>.supply.removed-<UTC>.json`. A
   reused checkout with a record re-applies it (admitted, excluded, re-checked); a record without its checkout
   refuses a new checkout of that name until the lead moves it.
"""
from __future__ import annotations

import argparse
import filecmp
import glob
import hashlib
import json
import os
import re
import shutil
import socket
import stat
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _p in (str(HERE.parent), str(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import run_lock as RL  # noqa: E402
import worktrees as W  # noqa: E402  (this tree's root is W.ROOT; its stores are W.STORES)

from extended import CLEAN_RUN_ENV, RUN_ID_ENV, RUNS_DIR  # noqa: E402
from extended.lock_guard import LOCK_HOLDER_ENV  # noqa: E402  (the heavy-test guard's holder mark, Q-118)
from extended.reader import LEDGER_REL, LedgerError, missing_lines, read_ledger  # noqa: E402  (no engine, no path)

RUNS = RUNS_DIR
BLAS = {"OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
#: files under results/ that are not results: the append-only variant log and read ledger, collected as a union of
#: their lines (Q-67), never replaced
APPEND_ONLY = ("results/variants.jsonl", LEDGER_REL)
#: run_clean's exit when the command exited 0 but a supplied file changed or went missing under it (Q-230)
SUPPLY_CHANGED = 7
#: a sidecar manifest's suffix (the vendored writer's `MANIFEST_SUFFIX`)
MANIFEST_SUFFIX = ".manifest.json"
#: a supplied result's name: plain, so its anchored exclude line needs no escaping
SUPPLY_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\.csv")
#: `extended.results.verify_result` on each source, in a process of its own (importing it puts the vendored tree on
#: `sys.path`); this repository's root is argv[1], the paths come on stdin as JSON
_VERIFY = ("import json, sys\n"
           "sys.path.insert(0, sys.argv[1])\n"
           "from extended.results import verify_result\n"
           "out = [[p, *verify_result(p)] for p in json.loads(sys.stdin.read())]\n"
           "print('S2X-VERIFY ' + json.dumps(out))\n")


def _git(*args: str, cwd: Path | None = None, env: dict[str, str] | None = None) -> str:
    out = subprocess.run(["git", *args], cwd=cwd or W.ROOT, capture_output=True, text=True, encoding="utf-8", env=env)
    if out.returncode:
        raise SystemExit(f"git {' '.join(args)} (in {cwd or W.ROOT}): {out.stderr.strip()}")
    return out.stdout


def _changed(cwd: Path, env: dict[str, str] | None = None) -> list[str]:
    """Paths `git status` reports in `cwd`, untracked files included (a rename gives its new path)."""
    parts = _git("status", "--porcelain", "-z", "--untracked-files=all", cwd=cwd, env=env).split("\0")
    paths, skip = [], False
    for p in parts:
        if skip:
            skip = False
            continue
        if len(p) > 3:
            paths.append(p[3:])
            skip = p[0] in "RC"
    return paths


def create(name: str, commit: str) -> Path:
    root = W.ROOT
    if commit == "HEAD" and _changed(root):
        raise SystemExit(f"this tree has uncommitted changes ({_changed(root)[:5]}): commit them, or name the commit "
                         "with --commit")
    sha = _git("rev-parse", "--verify", f"{commit}^{{commit}}").strip()
    wt = RUNS / name
    if wt.exists():
        raise SystemExit(f"{wt} exists: --remove it first")
    RUNS.mkdir(parents=True, exist_ok=True)
    _git("worktree", "add", "--detach", str(wt), sha)
    linked = []
    for s in W.STORES:
        if (root / s).is_dir():
            W.link(wt, s)
            linked.append(s)
    dirty = _changed(wt)
    if dirty:
        raise SystemExit(f"the checkout is not clean after linking the stores: {dirty[:5]}")
    print(f"checkout {wt} at {sha[:7]}, clean; stores linked: {linked}", flush=True)
    return wt


def checkout(name: str, commit: str) -> Path:
    """The run's checkout: made at `commit`, or the existing one (which must be at `commit` when one is named)."""
    wt = RUNS / name
    if not wt.exists():
        return create(name, commit)
    head = _git("rev-parse", "HEAD", cwd=wt).strip()
    if commit != "HEAD" and _git("rev-parse", "--verify", f"{commit}^{{commit}}").strip() != head:
        raise SystemExit(f"{wt} exists at {head[:7]}, not at {commit}: --remove it first")
    print(f"reusing checkout {wt} at {head[:7]}", flush=True)
    return wt


def host_line() -> str:
    """The log's first line (Q-229): the machine the run ran on, so a run from a second host (the Mac) names it even
    when its commit's manifests predate their own host field."""
    return f"host: {socket.gethostname()} ({sys.platform})"


# ------------------------------------------------------------------ Q-230: the verified input supply (item 7)


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def supply_record_path(wt: Path) -> Path:
    """The supply's record, beside the run's log (never inside the checkout)."""
    return wt.parent / f"{wt.name}.supply.json"


def _exclude_path(wt: Path) -> Path:
    return wt.parent / f"{wt.name}.supply.exclude"


def _verify_sources(paths: list[Path]) -> dict[str, tuple[bool, str]]:
    """`extended.results.verify_result` on each path, in a process of its own (this repository's, not the vendored
    tree's, on its `sys.path`)."""
    env = {**os.environ, **BLAS, "PYTHONDONTWRITEBYTECODE": "1"}
    out = subprocess.run([sys.executable, "-c", _VERIFY, str(HERE.parent)], input=json.dumps([str(p) for p in paths]),
                         capture_output=True, text=True, encoding="utf-8", env=env, timeout=600)
    line = [x for x in out.stdout.splitlines() if x.startswith("S2X-VERIFY ")]
    if out.returncode or len(line) != 1:
        raise SystemExit(f"REFUSED (supply): the manifest check could not run (exit {out.returncode}): "
                         f"{(out.stderr or out.stdout).strip()[-400:]}; nothing runs")
    return {p: (bool(ok), str(msg)) for p, ok, msg in json.loads(line[0][len("S2X-VERIFY "):])}


def _expand(pattern: str) -> list[Path]:
    """The supplied CSVs one `--supply` path names: the file, or every CSV a glob matches (their manifests beside
    them are taken with them, never named on their own)."""
    if not glob.has_magic(pattern):
        return [Path(pattern)]
    hits = sorted(Path(h) for h in glob.glob(pattern) if not h.endswith(MANIFEST_SUFFIX))
    if not hits:
        raise SystemExit(f"REFUSED (supply): {pattern!r} matches no result file; nothing runs")
    return hits


def plan_supply(specs: list[str]) -> list[dict[str, str]]:
    """Each `<commit>=<path>` resolved and checked (item 7): one entry per supplied CSV, `{"name", "source",
    "manifest_source", "commit", "sha256", "manifest_sha256"}`. Raises SystemExit (nothing runs) on any refusal."""
    plan: list[dict[str, str]] = []
    for spec in specs:
        if "=" not in spec:
            raise SystemExit(f"REFUSED (supply): {spec!r} is not <commit>=<path>; nothing runs")
        ref, pattern = spec.split("=", 1)
        sha = _git("rev-parse", "--verify", f"{ref.strip()}^{{commit}}").strip()
        for src in _expand(pattern):
            plan.append({"name": src.name, "source": str(src.resolve()), "commit": sha,
                         "manifest_source": str(Path(str(src) + MANIFEST_SUFFIX).resolve())})
    if not plan:
        raise SystemExit("REFUSED (supply): no file named; nothing runs")
    names = [e["name"] for e in plan]
    twice = sorted({n for n in names if names.count(n) > 1})
    if twice:
        raise SystemExit(f"REFUSED (supply): two sources for one destination: {twice}; nothing runs")
    for e in plan:
        src, man = Path(e["source"]), Path(e["manifest_source"])
        if not SUPPLY_NAME.fullmatch(e["name"]):
            raise SystemExit(f"REFUSED (supply): {src} is not a plainly named result CSV ({SUPPLY_NAME.pattern}); "
                             "nothing runs")
        if not src.is_file():
            raise SystemExit(f"REFUSED (supply): {src} does not exist; nothing runs")
        if not man.is_file():
            raise SystemExit(f"REFUSED (supply): {src.name} has no sidecar manifest beside it ({man.name}); nothing "
                             "runs")
    verdict = _verify_sources([Path(e["source"]) for e in plan])
    for e in plan:
        src, man = Path(e["source"]), Path(e["manifest_source"])
        ok, msg = verdict.get(str(src), (False, "not checked"))
        if not ok:
            raise SystemExit(f"REFUSED (supply): {src.name} does not verify (extended.results.verify_result: {msg}); "
                             "nothing runs")
        try:
            m = json.loads(man.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise SystemExit(f"REFUSED (supply): {man.name} is not readable JSON ({exc}); nothing runs") from None
        why = []
        if m.get("result_file") != src.name:
            why.append(f"its manifest names {m.get('result_file')!r}, not {src.name}")
        if m.get("git_commit") != e["commit"]:
            why.append(f"it was written at {str(m.get('git_commit'))[:12]!r}, not the declared commit "
                       f"{e['commit'][:12]}")
        if m.get("git_dirty") is not False:
            why.append(f"its manifest's git_dirty is {m.get('git_dirty')!r}, not False")
        e["sha256"], e["manifest_sha256"] = _sha256(src), _sha256(man)
        if m.get("sha256") != e["sha256"]:
            why.append("its sha256 is not its manifest's")
        if why:
            raise SystemExit(f"REFUSED (supply): {src.name}: " + "; ".join(why) + "; nothing runs")
    return plan


def supplied_paths(record: dict | None) -> list[str]:
    """Every path (relative to the checkout) a supply put there: each CSV and its manifest."""
    return [f["path"] for f in record["files"]] if record else []


def load_record(wt: Path) -> dict | None:
    p = supply_record_path(wt)
    if not p.is_file():
        return None
    try:
        rec = json.loads(p.read_text(encoding="utf-8"))
        assert isinstance(rec.get("files"), list) and all({"path", "sha256", "source"} <= set(f) for f in rec["files"])
    except (OSError, ValueError, AssertionError, AttributeError) as exc:
        raise SystemExit(f"the supply record {p} is not readable ({exc!r}): the lead looks first") from None
    return rec


def place_supply(wt: Path, plan: list[dict[str, str]]) -> dict:
    """Copy the planned files into `wt/results/`, byte-checked and read-only, and write the record beside the log.
    Every destination is checked absent before the first copy (never overwritten)."""
    pairs = []
    for e in plan:
        rel = f"results/{e['name']}"
        pairs.append((Path(e["source"]), rel, e["sha256"], e))
        pairs.append((Path(e["manifest_source"]), rel + MANIFEST_SUFFIX, e["manifest_sha256"], e))
    there = [rel for _, rel, _, _ in pairs if os.path.lexists(wt / rel)]
    if there:
        raise SystemExit(f"REFUSED (supply): these exist in the checkout already; a file is never overwritten: "
                         f"{there[:5]}; nothing runs")
    files = []
    (wt / "results").mkdir(exist_ok=True)
    for src, rel, sha, e in pairs:
        dst = wt / rel
        shutil.copyfile(src, dst)
        got = _sha256(dst)
        if got != sha:
            raise SystemExit(f"REFUSED (supply): the copy of {src} is not its source byte for byte (it changed while "
                             f"it was copied?); nothing runs -- --remove --discard the checkout")
        os.chmod(dst, stat.S_IREAD)
        files.append({"path": rel, "source": str(src), "sha256": got, "declared_commit": e["commit"]})
    record = {"supply": 1, "run": wt.name, "checkout_commit": _git("rev-parse", "HEAD", cwd=wt).strip(),
              "made": datetime.now(timezone.utc).isoformat(timespec="seconds"), "files": files}
    supply_record_path(wt).write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"supplied {len(plan)} result file(s) with their manifests into {wt / 'results'} (read-only; record "
          f"{supply_record_path(wt)})", flush=True)
    return record


def check_supply(wt: Path, record: dict | None) -> list[str]:
    """Each supplied file that is missing or no longer its recorded sha256, with why."""
    bad = []
    for f in (record or {}).get("files", []):
        p = wt / f["path"]
        if not p.is_file():
            bad.append(f"{f['path']}: missing")
        elif _sha256(p) != f["sha256"]:
            bad.append(f"{f['path']}: changed (sha256 is not the record's {f['sha256'][:12]}...)")
    return bad


def _global_excludes(wt: Path) -> str:
    """The user's own excludes file's text (`core.excludesFile`, else git's default `<XDG>/git/ignore`): setting
    `core.excludesFile` replaces it, so it is copied in first."""
    out = subprocess.run(["git", "config", "--get", "--path", "core.excludesFile"], cwd=wt, capture_output=True,
                         text=True, encoding="utf-8")
    if out.returncode == 0 and out.stdout.strip():
        p = Path(os.path.expanduser(out.stdout.strip()))
    else:
        xdg = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
        p = Path(xdg) / "git" / "ignore"
    try:
        return p.read_text(encoding="utf-8") if p.is_file() else ""
    except (OSError, UnicodeDecodeError):
        return ""


def supply_env(wt: Path, record: dict) -> dict[str, str]:
    """The command's git environment: the supplied paths (exactly those, anchored) excluded through
    `core.excludesFile`, set by `GIT_CONFIG_COUNT` after any the caller set."""
    lines = [f"/{rel}" for rel in supplied_paths(record)]
    for line in lines:
        if not re.fullmatch(r"/results/[A-Za-z0-9][A-Za-z0-9._-]*", line):
            raise SystemExit(f"the supply record names {line!r}, not a plain results/ file: the lead looks first")
    mine = _global_excludes(wt)
    text = (mine if not mine or mine.endswith("\n") else mine + "\n")
    text += f"# Q-230: the files supplied into {wt.name}, read-only inputs (record {supply_record_path(wt).name})\n"
    text += "".join(f"{x}\n" for x in lines)
    ex = _exclude_path(wt)
    ex.write_text(text, encoding="utf-8")
    try:
        n = int(os.environ.get("GIT_CONFIG_COUNT", "0") or 0)
    except ValueError:
        raise SystemExit("GIT_CONFIG_COUNT is set and not a number: unset it") from None
    return {"GIT_CONFIG_COUNT": str(n + 1), f"GIT_CONFIG_KEY_{n}": "core.excludesFile",
            f"GIT_CONFIG_VALUE_{n}": str(ex)}


def admit(wt: Path, record: dict | None) -> dict[str, str]:
    """The clean check before the command (item 7): the checkout's changes are exactly supplied files, each its
    record's; under the command's exclusion it is clean. Returns the command's extra environment (empty without a
    supply). Raises SystemExit (nothing runs) otherwise."""
    allowed = set(supplied_paths(record))
    dirty = [p for p in _changed(wt) if p not in allowed]
    if dirty:
        raise SystemExit(f"{wt} is not clean: {dirty[:5]}")
    if record is None:
        return {}
    bad = check_supply(wt, record)
    if bad:
        raise SystemExit(f"REFUSED (supply): a supplied file is not its record's before the command: {bad[:5]}; "
                         "nothing runs")
    extra = supply_env(wt, record)
    seen = _changed(wt, env={**os.environ, **extra})
    if seen:
        raise SystemExit(f"REFUSED (supply): under the command's exclusion the checkout is not clean: {seen[:5]}; "
                         "nothing runs")
    return extra


def _writable(wt: Path, record: dict | None) -> None:
    for rel in supplied_paths(record):
        p = wt / rel
        if p.is_file():
            os.chmod(p, stat.S_IREAD | stat.S_IWRITE)


def run(wt: Path, cmd: list[str], lock_job: str | None = None, extra_env: dict[str, str] | None = None,
        record: dict | None = None) -> int:
    run_id = f"{wt.name}@{datetime.now(timezone.utc):%Y%m%dT%H%M%S.%fZ}"
    env = {**os.environ, **BLAS, "PYTHONUNBUFFERED": "1", "PYTHONDONTWRITEBYTECODE": "1", CLEAN_RUN_ENV: wt.name,
           RUN_ID_ENV: run_id, **(extra_env or {})}
    if lock_job is not None:
        env[LOCK_HOLDER_ENV] = lock_job               # the lock's holder: its heavy tests may run (Q-118)
    log = wt.parent / f"{wt.name}.log"
    print(f"running in {wt}: {' '.join(cmd)}  (log: {log}; run id {run_id})", flush=True)
    with log.open("w", encoding="utf-8") as f:
        host = host_line()
        f.write(host + "\n")
        f.flush()
        print(host, flush=True)
        p = subprocess.Popen(cmd, cwd=wt, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                             encoding="utf-8", errors="replace")
        if lock_job is not None:
            RL.main(["set-pid", "--job", lock_job, "--pid", str(p.pid), "--log", str(log)])
        assert p.stdout is not None
        for line in p.stdout:
            f.write(line)
            f.flush()
            sys.stdout.write(line)
            sys.stdout.flush()
        rc = p.wait()
        if record is not None:                        # Q-230: every supplied file re-checked after the command
            bad = check_supply(wt, record)
            for b in bad:
                msg = f"SUPPLY CHANGED: {b} -- the command changed or removed a supplied input"
                f.write(msg + "\n")
                print(msg, flush=True)
            if bad and rc == 0:
                rc = SUPPLY_CHANGED
            if not bad:
                f.write(f"supply re-checked after the command: {len(record['files'])} file(s) unchanged\n")
        f.write(f"EXIT {rc}\n")
    print(f"EXIT {rc}", flush=True)
    return rc


def _text(p: Path) -> str | None:
    """A file's text (UTF-8), "" when absent, None when it is not UTF-8."""
    if not p.is_file():
        return ""
    try:
        return p.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        return None


def _home(wt: Path, p: str) -> bool:
    """The run's copy of `p` is in this tree: the same file (both absent counts), or, for an append-only file, every
    line of the run's copy in this tree's copy, counted with multiplicity (Q-67)."""
    a, b = wt / p, W.ROOT / p
    if not a.exists() and not b.exists():
        return True
    if p in APPEND_ONLY and a.is_file():
        run, tree = _text(a), _text(b)
        return run is not None and tree is not None and not missing_lines(run, tree)
    return a.is_file() and b.is_file() and filecmp.cmp(a, b, shallow=False)


def _blob(rev: str, p: str, cwd: Path, *, as_checked_out: bool) -> bytes:
    """`p` at commit `rev` (b"" when the commit has no such file): as a checkout in `cwd` holds it (its end-of-line
    conversion applied, `git cat-file --filters`), or the blob as committed."""
    ls = subprocess.run(["git", "ls-tree", "-z", "--name-only", rev, "--", p], cwd=cwd, capture_output=True)
    if ls.returncode:
        raise SystemExit(f"git ls-tree {rev[:10]} -- {p} (in {cwd}): {ls.stderr.decode('utf-8', 'replace').strip()}")
    if p.encode("utf-8") not in ls.stdout.split(b"\0"):
        return b""
    out = subprocess.run(["git", "cat-file", "--filters" if as_checked_out else "blob", f"{rev}:{p}"], cwd=cwd,
                         capture_output=True)
    if out.returncode:
        raise SystemExit(f"git cat-file {rev[:10]}:{p} (in {cwd}): {out.stderr.decode('utf-8', 'replace').strip()}")
    return out.stdout


def _union(wt: Path, sha: str, p: str) -> tuple[bytes | None, int]:
    """This tree's copy of the append-only file `p` with the run's new lines appended, and how many: (None, 0) when
    every line of the run's copy is home already. Raises SystemExit (nothing copied) on any refusal (module docstring,
    item 5)."""
    dst = W.ROOT / p
    run = (wt / p).read_bytes()
    base = _blob(sha, p, wt, as_checked_out=True)
    if not run.startswith(base):
        raise SystemExit(f"the run's copy of {p} does not start with its commit's ({sha[:7]}) copy byte for byte -- the "
                         "run did more than append (a line edited, dropped or moved); nothing copied")
    added = run[len(base):]
    if added and not added.endswith(b"\n"):
        raise SystemExit(f"the run's copy of {p} does not end in a newline -- its last line was cut; nothing copied")
    tree = dst.read_bytes() if dst.is_file() else b""
    if tree and not tree.endswith(b"\n"):
        raise SystemExit(f"this tree's copy of {p} does not end in a newline -- a line was cut or edited; nothing "
                         "copied (the lead looks first)")
    try:
        run_t, base_t, tree_t = run.decode("utf-8"), base.decode("utf-8"), tree.decode("utf-8")
        added_t = added.decode("utf-8")
        head_t = _blob("HEAD", p, W.ROOT, as_checked_out=False).decode("utf-8")
    except UnicodeDecodeError:
        raise SystemExit(f"a copy of {p} is not UTF-8 text; nothing copied") from None
    # missing_lines skips blank lines, so the union would drop one silently; neither writer writes one
    blank = [i for i, line in enumerate(added_t.split("\n")[:-1], 1) if not line.strip()]
    if blank:
        raise SystemExit(f"the run's copy of {p} has a blank line in what it appended (its appended line {blank[0]}) "
                         "-- one record a line; nothing copied (the lead looks first)")
    lost = missing_lines(base_t, tree_t)
    if lost:
        raise SystemExit(f"this tree's copy of {p} has lost {len(lost)} line(s) of the run's commit's ({sha[:7]}) copy, "
                         f"e.g. {lost[0][:160]} -- an append-only file only grows; nothing copied")
    lost = missing_lines(head_t, tree_t)
    if lost:
        raise SystemExit(f"this tree's working copy of {p} has lost {len(lost)} line(s) committed at HEAD, e.g. "
                         f"{lost[0][:160]} -- an append-only file only grows; nothing copied")
    new = missing_lines(run_t, tree_t)
    if not new:
        return None, 0
    if missing_lines("\n".join(new), added_t):                        # by construction (the base is in the tree)
        raise SystemExit(f"the union of {p} would take a line that is not in the run's appended part; nothing copied")
    return tree + "".join(f"{line}\n" for line in new).encode("utf-8"), len(new)


def collect(wt: Path) -> list[str]:
    root = W.ROOT
    if not wt.is_dir():
        raise SystemExit(f"{wt} does not exist")
    sha = _git("rev-parse", "HEAD", cwd=wt).strip()
    record = load_record(wt)                                          # Q-230: supplied inputs are never output
    bad = check_supply(wt, record)
    if bad:
        raise SystemExit(f"a supplied input is not its record's (the run changed it?): {bad[:5]}; nothing copied (the "
                         "lead looks first)")
    supplied = set(supplied_paths(record))
    produced = [p for p in _changed(wt) if p not in supplied]
    if not produced:
        print("the run changed no file")
        return []
    # an append-only file is checked by its union's own conditions (Q-67), not as a clash
    plain = [p for p in produced if p not in APPEND_ONLY]
    here = set(_changed(root))
    clash = [p for p in plain if p in here]
    if clash:
        raise SystemExit(f"this tree changed these since the run's commit; nothing copied: {clash}")
    if _git("rev-parse", "HEAD").strip() != sha:
        moved = set(_git("diff", "--name-only", sha, "HEAD").split())
        clash = [p for p in plain if p in moved]
        if clash:
            raise SystemExit(f"commits since {sha[:7]} changed these; nothing copied: {clash}")
    gone = [p for p in produced if not (wt / p).is_file()]
    if gone:
        raise SystemExit(f"the run deleted these; nothing copied: {gone}")
    over = []
    for p in plain:
        if not p.startswith("results/") or not (root / p).is_file() or _home(wt, p):
            continue
        over.append(p)
    if over:
        raise SystemExit(f"these would replace existing files under results/ -- a result file is never overwritten "
                         f"(DIRECTIVE Part 1); nothing copied: {over}")
    staged: list[tuple[Path, Path, str, int]] = []                    # (temporary file, destination, path, new lines)
    try:
        for p in produced:
            if p not in APPEND_ONLY:
                continue
            data, n = _union(wt, sha, p)
            if data is None:
                print(f"{p}: every line of the run's copy is home already; nothing appended")
                continue
            dst = root / p
            dst.parent.mkdir(parents=True, exist_ok=True)
            tmp = dst.parent / f".{dst.name}.{os.getpid()}.collect"
            staged.append((tmp, dst, p, n))
            tmp.write_bytes(data)
            if p == LEDGER_REL:
                try:
                    read_ledger(tmp)
                except LedgerError as exc:
                    raise SystemExit(f"the union of {p} does not verify ({exc}); nothing copied") from None
        # the unions first: each is idempotent, so a union that cannot be put in place leaves no plain file copied
        # and a second --collect finishes the job
        for tmp, dst, p, n in staged:
            try:
                os.replace(tmp, dst)
            except OSError as exc:
                raise SystemExit(f"{p} could not be put in place ({exc}); the run's other files were not copied -- "
                                 "--collect again (a union already home appends nothing)") from None
            print(f"appended {n} line(s) of the run's to {p}")
        for p in plain:
            dst = root / p
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(wt / p, dst)
            print(f"copied {p}")
    finally:
        for tmp, *_ in staged:
            if tmp.exists():
                tmp.unlink()
    return produced


def remove(name: str, discard: bool = False) -> None:
    wt = RUNS / name
    if not wt.exists():
        raise SystemExit(f"{wt} does not exist")
    record = load_record(wt)                                          # Q-230: supplied inputs are not the run's
    supplied = set(supplied_paths(record))
    if not discard:
        left = [p for p in _changed(wt) if p not in supplied and not _home(wt, p)]
        if left:
            raise SystemExit(f"{wt} holds files not brought home: {left[:5]} -- --collect first, or --remove --discard")
    for s in W.STORES:
        W.unlink(wt, s)
    if any(W.is_link(wt / s) for s in W.STORES):
        raise SystemExit("a junction is still in place; not removing the checkout")
    _writable(wt, record)                                             # read-only copies: writable to be removed
    _git("worktree", "remove", "--force", str(wt))
    if record is not None:                                            # the record is kept, renamed
        rp = supply_record_path(wt)
        rp.rename(rp.with_name(f"{wt.name}.supply.removed-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"))
        ex = _exclude_path(wt)
        if ex.is_file():
            ex.unlink()
    print(f"removed {wt}")


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd: list[str] = []
    if "--" in argv:
        i = argv.index("--")
        argv, cmd = argv[:i], argv[i + 1:]
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--name", required=True, help="the checkout's folder under %%LOCALAPPDATA%%/stage2-extended-runs")
    ap.add_argument("--commit", default="HEAD")
    ap.add_argument("--collect", action="store_true", help="copy the run's result files into this tree")
    ap.add_argument("--remove", action="store_true", help="unlink the stores and remove the checkout")
    ap.add_argument("--discard", action="store_true", help="with --remove: drop files the run produced, not collected")
    ap.add_argument("--hours", type=float, default=None, help="take run.lock for this long (with --mem-gb)")
    ap.add_argument("--mem-gb", type=float, default=None, help="the memory the job needs (run_lock refuses short)")
    ap.add_argument("--task", default=None, help="the TASK_QUEUE id, recorded in the lock (required with it)")
    ap.add_argument("--holder", default=None, help="who holds the lock (default: run_clean from this tree)")
    ap.add_argument("--supply", action="append", default=[], metavar="COMMIT=PATH",
                    help="copy a verified result CSV (or a glob of them) with its manifest, written clean at COMMIT, "
                         "into the new checkout's results/ before the command (repeatable; Q-230)")
    a = ap.parse_args(argv)
    if a.supply and (a.remove or a.collect):
        ap.error("--supply goes with a command, not with --collect or --remove")
    if a.remove:
        remove(a.name, a.discard)
        return 0
    if a.collect:
        collect(RUNS / a.name)
        return 0
    if not cmd:
        ap.error("give the command after --")
    if (a.hours is None) != (a.mem_gb is None):
        ap.error("--hours and --mem-gb go together (they take the run lock)")
    wt0 = RUNS / a.name
    if a.supply and wt0.exists():
        raise SystemExit(f"REFUSED (supply): {wt0} exists; a supply is made at a checkout's creation -- --remove it "
                         "first; nothing runs")
    if not wt0.exists() and supply_record_path(wt0).exists():
        raise SystemExit(f"REFUSED (supply): {supply_record_path(wt0)} is the record of a checkout of this name that "
                         "is gone; the lead moves it before a new one is made; nothing runs")
    plan = plan_supply(a.supply) if a.supply else None             # every refusal before the lock and the checkout
    locked = a.hours is not None
    if locked:
        if not a.task:
            ap.error("--task is required with the lock")
        holder = a.holder or f"run_clean ({W.ROOT.name})"
        rc = RL.main(["take", "--job", a.name, "--task", a.task, "--holder", holder, "--hours", str(a.hours),
                      "--mem-gb", str(a.mem_gb), "--cmd", " ".join(cmd)])
        if rc != 0:
            print(f"REFUSED: the run lock was not taken (exit {rc}); the command does not run", flush=True)
            return rc
    try:
        wt = checkout(a.name, a.commit)
        record = place_supply(wt, plan) if plan else load_record(wt)
        extra = admit(wt, record)                                   # exactly the supplied files, nothing else
        return run(wt, cmd, a.name if locked else None, extra_env=extra, record=record)
    finally:
        if locked:
            RL.main(["release", "--job", a.name])


if __name__ == "__main__":
    raise SystemExit(main())
