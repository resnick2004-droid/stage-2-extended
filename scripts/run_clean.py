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
   Its output goes to `<name>.log` beside the checkout (never inside it: an untracked log would stamp it `-dirty`),
   ending with an `EXIT <code>` line.
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
   starts with that base byte for byte (the run only appended) and its appended part ends in a newline (no cut line),
   and this tree's copy -- which later commits and earlier collections may have extended -- ends in a newline and has
   lost no line of the base, nor of this tree's HEAD (`extended.reader.missing_lines`, a multiset); then each line of
   the run's copy this tree's copy lacks (counted with multiplicity, so collecting twice is a no-op) is appended to
   it, in the run's order, the result verified (the ledger by `extended.reader.read_ledger`) and put in place
   atomically. A later commit's or this tree's own change to such a file is no clash: the union's conditions replace
   that check for it.
6. `--remove` refuses while a file the run produced is not home (`--collect` first, or `--discard` to drop it), then
   unlinks the junctions -- never through them -- and removes the checkout. An append-only file is home when every
   line of the run's copy is in this tree's (a multiset; other lines beside them do not matter).
"""
from __future__ import annotations

import argparse
import filecmp
import os
import shutil
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
from extended.reader import LEDGER_REL, LedgerError, missing_lines, read_ledger  # noqa: E402  (no engine, no path)

RUNS = RUNS_DIR
BLAS = {"OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
#: files under results/ that are not results: the append-only variant log and read ledger, collected as a union of
#: their lines (Q-67), never replaced
APPEND_ONLY = ("results/variants.jsonl", LEDGER_REL)


def _git(*args: str, cwd: Path | None = None) -> str:
    out = subprocess.run(["git", *args], cwd=cwd or W.ROOT, capture_output=True, text=True, encoding="utf-8")
    if out.returncode:
        raise SystemExit(f"git {' '.join(args)} (in {cwd or W.ROOT}): {out.stderr.strip()}")
    return out.stdout


def _changed(cwd: Path) -> list[str]:
    """Paths `git status` reports in `cwd`, untracked files included (a rename gives its new path)."""
    parts = _git("status", "--porcelain", "-z", "--untracked-files=all", cwd=cwd).split("\0")
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


def run(wt: Path, cmd: list[str], lock_job: str | None = None) -> int:
    run_id = f"{wt.name}@{datetime.now(timezone.utc):%Y%m%dT%H%M%S.%fZ}"
    env = {**os.environ, **BLAS, "PYTHONUNBUFFERED": "1", "PYTHONDONTWRITEBYTECODE": "1", CLEAN_RUN_ENV: wt.name,
           RUN_ID_ENV: run_id}
    log = wt.parent / f"{wt.name}.log"
    print(f"running in {wt}: {' '.join(cmd)}  (log: {log}; run id {run_id})", flush=True)
    with log.open("w", encoding="utf-8") as f:
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
        head_t = _blob("HEAD", p, W.ROOT, as_checked_out=False).decode("utf-8")
    except UnicodeDecodeError:
        raise SystemExit(f"a copy of {p} is not UTF-8 text; nothing copied") from None
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
    if missing_lines("\n".join(new), added.decode("utf-8")):          # by construction (the base is in the tree)
        raise SystemExit(f"the union of {p} would take a line that is not in the run's appended part; nothing copied")
    return tree + "".join(f"{line}\n" for line in new).encode("utf-8"), len(new)


def collect(wt: Path) -> list[str]:
    root = W.ROOT
    if not wt.is_dir():
        raise SystemExit(f"{wt} does not exist")
    sha = _git("rev-parse", "HEAD", cwd=wt).strip()
    produced = _changed(wt)
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
    if not discard:
        left = [p for p in _changed(wt) if not _home(wt, p)]
        if left:
            raise SystemExit(f"{wt} holds files not brought home: {left[:5]} -- --collect first, or --remove --discard")
    for s in W.STORES:
        W.unlink(wt, s)
    if any(W.is_link(wt / s) for s in W.STORES):
        raise SystemExit("a junction is still in place; not removing the checkout")
    _git("worktree", "remove", "--force", str(wt))
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
    a = ap.parse_args(argv)
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
        dirty = _changed(wt)
        if dirty:
            raise SystemExit(f"{wt} is not clean: {dirty[:5]}")
        return run(wt, cmd, a.name if locked else None)
    finally:
        if locked:
            RL.main(["release", "--job", a.name])


if __name__ == "__main__":
    raise SystemExit(main())
