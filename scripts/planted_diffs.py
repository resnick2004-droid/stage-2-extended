"""Q-196: the planted-difference check on P-14's point arm on the search years -- that the exact-run comparator Q-172
counted with (`scripts/exact_run_diffs.py`) fires on real paths, so its zero means something (the Q-172 audit's C2).
A check, like an identity: **it writes no file**, prints counts and HELD / FAILED lines only, and exits non-zero if any
planted difference is missed. The plants, the starts, the expectations and every refusal are
`extended/planted_diffs.py`'s, fixed there before any run; nothing is drawn.

    python scripts/run_clean.py --name q196-planted-diffs --task Q-196 --hours 1 --mem-gb 1.5 -- python scripts/planted_diffs.py

**Heavy** (it builds P-14's point-arm job from the licensed atlas, inside the search cut, and runs Stage 2's engine on
it): under the run lock, from a clean checkout, one BLAS thread, one process (the planter replaces a function in this
process, so `workers` is 1). Expected: a few minutes at most, under 1.5 GB -- the same build and per-start cost as
Q-172's clean run (its manifest's `timing` and `peak_working_set_mb`), here for six control starts and about thirty
planted runs per response, two responses.

**The steps, each refusing:**

1. **No argument** is taken: any is refused (exit 2) before anything is read.
2. **The read** (`search_cut.authorise`, purpose `identity`, declaration E-232 -- the row that specified Q-172's count,
   whose power this checks; E-248 the ruling that narrowed it to the point arm): refused, exit 3.
3. **The build**: P-14's point-arm job by U1's own builder inside the cut at 2023-12-29 (`search_cut_identity.
   build_point`: every data read cut or refused, the job's dates checked against the cut).
4. **The dates** (`planted_diffs.refuse_dates`): any date past 2023-12-29, or from 2026-07-17, refused: exit 2.
5. **The identity u1_point** on the declared starts whose 252-session replay ends by 2023-12-29 (the control starts
   and n - 252): their point-arm start rows equal U1's (`vendor/stage2/results/user_journey.csv`, every column), so
   the paths planted on are the registered ones; a failure is exit 4.
6. **The check** (`planted_diffs.run_check`, responses `off` and `denial_25`): the control unperturbed reports no
   difference; every plant is reported at its start and exactly its horizons, by the comparator and by Q-172's
   counting layer. Exit 0 held; 1 a plant missed, a spurious difference or a run check failed; 6 too few starts
   carry the forced plants to show power (never a pass).

Prints no event day, no horizon of a plant, no measure: per response and kind, the plants made, the starts and the
count of differing horizons expected, and HELD or FAILED; on a failure, its lines.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_k, "1")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for _p in (str(ROOT), str(ROOT / "identity")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

TASK = "Q-196"
READ_ROW = "E-232"


def refused(msg: str) -> str:
    return msg if msg.startswith("REFUSED") else f"REFUSED ({TASK}): {msg}"


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:                       # exit 2, before anything is read
        print(refused(f"this check takes no argument ({message})"), flush=True)
        raise SystemExit(2)


def main(argv: list[str] | None = None) -> int:
    _Parser(description=__doc__.split("\n\n")[0]).parse_args(argv)

    from extended import use_vendored_stage2

    use_vendored_stage2()

    import search_cut_identity as SCI

    from extended import planted_diffs as PD
    from extended import reader
    from extended import search_cut as SC
    from extended.procmem import working_set_mb
    from propedge import RESULTS_DIR as RD

    try:
        SC.authorise(purpose="identity", declaration=READ_ROW,
                     what=f"{TASK}: the planted-difference check on P-14's point arm, inside the search cut")
    except (reader.ReadRefused, FileNotFoundError, SC.LateRow) as exc:
        print(refused(str(exc)), flush=True)
        return 3
    t0 = time.time()
    job, c, _log = SCI.build_point(SC.LAST_DAY)
    n = len(job["dates"])
    print(f"  built: P-14's point job on the cut at {SC.LAST_DAY} ({n} days) in {time.time() - t0:.0f} s; "
          f"peak {working_set_mb(peak=True):.0f} MB", flush=True)
    try:
        PD.refuse_dates(job["dates"], what="P-14's point job")
        starts = PD.declared_starts(n)
    except PD.PlantRefused as exc:
        print(refused(str(exc)), flush=True)
        return 2
    comparable = [s for s in starts if s + SCI.X.LONG <= n]
    t1 = time.time()
    outs = SCI.run_off(job, comparable, 1)
    nu1, q = SCI.u1_point(RD, c, outs)
    del outs
    print(f"  identity u1_point: {nu1} of the {len(comparable)} declared starts ending by {SC.LAST_DAY}, in "
          f"{time.time() - t1:.0f} s -- {'HELD' if not q and nu1 == len(comparable) else 'FAILED'}", flush=True)
    if q or nu1 != len(comparable):
        for x in q[:6]:
            print(f"  {x}")
        print(refused("an identity failed; the check is not run"))
        return 4
    t2 = time.time()
    try:
        report = PD.run_check(job, SCI.DESIGN, SCI.ARM)
    except PD.PlantRefused as exc:
        print(refused(str(exc)), flush=True)
        return 2
    print(f"  the check: {len(starts)} declared starts ({sum(g == 'control' for g in starts.values())} control, "
          f"{sum(g == 'cut' for g in starts.values())} cut), {len(report['plants'])} planted runs, in "
          f"{time.time() - t2:.0f} s; peak {working_set_mb(peak=True):.0f} MB", flush=True)
    for line in PD.summary_lines(report):
        print(line, flush=True)
    for x in report["failures"]:
        print(f"  FAILED: {x}", flush=True)
    for x in report["cannot"]:
        print(f"  CANNOT: {x}", flush=True)
    v = PD.verdict(report)
    word = {0: "HELD: every planted difference reported at its start and horizons; the control 0",
            1: "FAILED: a planted difference missed, or a difference reported where none was planted",
            6: "CANNOT: too few starts carry the forced plants to show the comparator firing"}[v]
    print(f"  {TASK} {word}; total {time.time() - t0:.0f} s; peak working set {working_set_mb(peak=True):.0f} MB",
          flush=True)
    return v


if __name__ == "__main__":
    raise SystemExit(main())
