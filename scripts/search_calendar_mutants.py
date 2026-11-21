"""Q-197's mutation check: each mechanism of the search calendar (`extended/search_calendar.py`, its builder, form
checks, identities and loader, and `scripts/search_calendar.py`, its writer) broken by one edit, on a scratch copy,
and `tests/test_search_calendar.py` run against it. A mutant is **killed** when the tests fail on it. The unmutated
control must pass and every mutant must be killed; the script exits 1 otherwise.

    python scripts/search_calendar_mutants.py --scratch <a new folder outside the repository>

Light: no bar, no result, no engine run; each pass takes seconds. The scratch folder holds copies of this repository's
`extended/`, `config/`, the script, its test, `conftest.py` and `pyproject.toml`, and of the vendored files the tests
reach (the result writer's package `propedge/` and its `scripts/hashes.py`, the BLS and FOMC calendars) -- never a
junction or a licensed data file; nothing in the repository is written. A failing control stops the check before any
mutant runs (a mutant killed by a broken copy is not killed).
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOD, SCR = "extended/search_calendar.py", "scripts/search_calendar.py"
TEST = "tests/test_search_calendar.py"
COPY_DIRS = ("extended", "config", "vendor/stage2/propedge")
COPY_FILES = (SCR, TEST, "conftest.py", "pyproject.toml", "vendor/stage2/scripts/hashes.py",
              "vendor/stage2/data/release_days_0830_2009_2025.csv", "vendor/stage2/data/release_days_0830_2026.csv",
              "vendor/stage2/config/sources/fomc_statements.csv",
              "vendor/stage2/config/sources/fomc_statements_2020_2024q1.csv",
              "vendor/stage2/config/sources/fomc_statements_2026q3.csv")

#: (name, target, the text replaced, its replacement): each text occurs exactly once in its target
MUTANTS: tuple[tuple[str, str, str, str], ...] = (
    ("sessions left without the start session", MOD, '"sessions_left": n - i,', '"sessions_left": n - i - 1,'),
    ("sessions counted from 0", MOD, '"session": i + 1,', '"session": i,'),
    ("the 08:29 class does not read the 08:29 bar", MOD, '"overnight_0829": (True, True)}',
     '"overnight_0829": (True, False)}'),
    ("the overnight class reads no overnight", MOD, '"overnight": (True, False),', '"overnight": (False, False),'),
    ("every day kind regular", MOD, 'k = row["kind"] if row else "regular"', 'k = "regular"'),
    ("rolls dropped", MOD, '"roll": int(d in src.rolls)', '"roll": 0'),
    ("bls dropped", MOD, '"bls": int(f0.bls)', '"bls": 0'),
    ("weekday shifted", MOD, '"weekday": WEEKDAYS[d.weekday()]', '"weekday": WEEKDAYS[d.isoweekday() % 7]'),
    ("reasons joined by ;", MOD, 'SEP = "|"', 'SEP = ";"'),
    ("no confirmation-window refusal", MOD, "    if d >= CONFIRMATION_START:\n        raise DC.ConfirmationDay",
     "    if False:\n        raise DC.ConfirmationDay"),
    ("the search years end a year late", MOD, "    if d > SEARCH_END:\n        raise DC.HeldOutDay",
     "    if d > date(2024, 12, 31):\n        raise DC.HeldOutDay"),
    ("check_rows guards no date", MOD, "        guard_date(d)\n    if any(b <= a", "        pass\n    if any(b <= a"),
    ("no span check", MOD, "if require_span and (dates[0]", "if False and (dates[0]"),
    ("no ordinal check", MOD, 'if r["session"] != i + 1 or r["sessions_left"] != n - i:', "if False:"),
    ("labels unchecked", MOD, '_LABEL = re.compile(r"[a-z0-9_:;|]*")', '_LABEL = re.compile(r".*")'),
    ("flags not held to 0 / 1", MOD, "if r[k] not in (0, 1):", "if False:"),
    ("a bool taken for an integer", MOD, "if isinstance(v, bool) or not isinstance(v, int):",
     "if not isinstance(v, int):"),
    ("a flag and its reasons may disagree", MOD, 'if bool(r[f"void_{c}"]) != bool(r[f"why_void_{c}"]):', "if False:"),
    ("I-1 without the count", MOD, "if len(dates) != len(h2):", "if False:"),
    ("I-1 without the dates", MOD, "    if dates != h2:\n", "    if False:\n"),
    ("I-2 without the void flags", MOD,
     'if int(r[f"void_{c}"]) != int(ctx.void) or str(r[f"why_void_{c}"]) != SEP.join(f.void):', "if False:"),
    ("I-2 reads the reasons only", MOD,
     'if int(r[f"void_{c}"]) != int(ctx.void) or str(r[f"why_void_{c}"]) != SEP.join(f.void):',
     'if str(r[f"why_void_{c}"]) != SEP.join(f.void):'),
    ("I-2 without prior_void", MOD,
     'if int(r["prior_void"]) != int(ctx.prior_void) or str(r["why_prior_void"]) != SEP.join(f.prior_void):',
     "if False:"),
    ("I-2 without bls / fomc", MOD, 'if int(r["bls"]) != int(ctx.bls) or int(r["fomc"]) != int(ctx.fomc):',
     "if False:"),
    ("I-2 without H2's VOID cross-check", MOD, "    if missed:\n", "    if False:\n"),
    ("the digest without line ends", MOD, '"".join(f"{d}\\n" for d in dates)', '"\\n".join(f"{d}" for d in dates)'),
    ("the loader skips the file's sha256", MOD, 'if man.get("sha256") != sha:', "if False:"),
    ("the loader skips the digest", MOD,
     "if not (isinstance(want, str) and _HEX64.fullmatch(want)) or want != digest:",
     "if not (isinstance(want, str) and _HEX64.fullmatch(want)):"),
    ("the loader reads without a manifest", MOD, "    if not side.is_file():\n        raise CalendarRefused",
     "    if False:\n        raise CalendarRefused"),
    ("the loader takes a partial span", MOD, "dates = tuple(check_rows(rows, require_span=True))",
     "dates = tuple(check_rows(rows, require_span=False))"),
    ("the loader keeps integers as text", MOD, "                row[k] = int(v)", "                row[k] = v"),
    ("sessions_left() without the start", MOD, "return len(self.dates) - self.session(day) + 1",
     "return len(self.dates) - self.session(day)"),
    ("the script reads flags without their manifest", SCR, 'if not Path(str(flags) + ".manifest.json").is_file():',
     "if False:"),
    ("the script skips the identities", SCR, "ident = SC.identities(back, src)", "ident = {}"),
    ("the script takes a partial span", SCR, "dates = SC.check_rows(rows, require_span=True)",
     "dates = SC.check_rows(rows, require_span=False)"),
    ("the script refuses nothing", SCR, "except (DC.HeldOutDay, SC.CalendarRefused, KeyError, ValueError) as exc:",
     "except (KeyError,) as exc:"),
    ("H2's hash of another file", SCR, '"h2_flags": {"file": _rel(flags), "sha256": SC.sha256_file(flags),',
     '"h2_flags": {"file": _rel(flags), "sha256": SC.sha256_file(calendar),'),
    ("the bar manifest's hash of another file", SCR,
     '"bars_manifest": {"file": _rel(manifest), "sha256": SC.sha256_file(manifest),',
     '"bars_manifest": {"file": _rel(manifest), "sha256": SC.sha256_file(calendar),'),
    ("Q-40's hash of another file", SCR,
     '"calendar_early_closes": {"file": _rel(calendar), "sha256": SC.sha256_file(calendar)}',
     '"calendar_early_closes": {"file": _rel(calendar), "sha256": SC.sha256_file(manifest)}'),
    ("the manifest's digest of another list", SCR, '"calendar_sha256": digest, ',
     '"calendar_sha256": SC.calendar_digest(dates[1:]), '),
)


def _copy(scratch: Path) -> None:
    ign = shutil.ignore_patterns("__pycache__", "*.pyc")
    for d in COPY_DIRS:
        shutil.copytree(ROOT / d, scratch / d, ignore=ign)
    for f in COPY_FILES:
        (scratch / f).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / f, scratch / f)
    (scratch / "results").mkdir(exist_ok=True)


def _run(scratch: Path, timeout: int) -> tuple[bool, float, str]:
    env = {**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
           "PYTHONDONTWRITEBYTECODE": "1"}
    env.pop("S2X_CLEAN_RUN", None)
    t0 = time.monotonic()
    p = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-o", "addopts=", "-p", "no:cacheprovider", TEST],
                       cwd=scratch, env=env, capture_output=True, text=True, timeout=timeout)
    tail = (p.stdout.strip().splitlines() or [""])[-1]
    return p.returncode == 0, time.monotonic() - t0, tail


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--scratch", required=True, help="a new, empty folder outside the repository")
    ap.add_argument("--timeout", type=int, default=600, help="seconds a run may take")
    a = ap.parse_args(argv)
    scratch = Path(a.scratch).resolve()
    if scratch == ROOT or ROOT in scratch.parents:
        raise SystemExit("the scratch folder must be outside the repository")
    if scratch.exists() and any(scratch.iterdir()):
        raise SystemExit("the scratch folder must be new or empty")
    scratch.mkdir(parents=True, exist_ok=True)
    _copy(scratch)
    clean = {t: (ROOT / t).read_text(encoding="utf-8") for t in (MOD, SCR)}
    for name, target, old, _ in MUTANTS:
        if clean[target].count(old) != 1:
            raise SystemExit(f"mutant {name!r}: its text occurs {clean[target].count(old)} times in {target}, not once")
    ok, secs, tail = _run(scratch, a.timeout)
    print(f"control (unmutated): {'passes' if ok else 'FAILS'} in {secs:.1f} s  [{tail}]", flush=True)
    if not ok:
        print("the control fails on the scratch copy: no mutant is run", flush=True)
        return 1
    survived = []
    for i, (name, target, old, new) in enumerate(MUTANTS, 1):
        (scratch / target).write_text(clean[target].replace(old, new), encoding="utf-8", newline="\n")
        passed, secs, tail = _run(scratch, a.timeout)
        (scratch / target).write_text(clean[target], encoding="utf-8", newline="\n")
        print(f"{i:2d}. {'SURVIVED' if passed else 'killed  '}  {name}  ({secs:.1f} s)  [{tail}]", flush=True)
        if passed:
            survived.append(name)
    print(f"{len(MUTANTS) - len(survived)} of {len(MUTANTS)} mutants killed; control "
          f"{'passes' if ok else 'FAILS'}", flush=True)
    return 0 if ok and not survived else 1


if __name__ == "__main__":
    sys.exit(main())
