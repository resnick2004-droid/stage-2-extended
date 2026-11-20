"""Q-172 (`docs/MEASURES.md` section 6, "to run before the held-out runner is declared"; E-232; the lead's option 2):
the count of exact-length-run differences on P-14's **point arm** on the search years -- responses `off` and
`denial_25`, the last 252 search starts plus every 21st earlier one, horizons 21, 63, 90 and 126 -- through
`user_beside.run_starts(..., journey=True)`, P-14's job built by U1's own builder **inside the search cut**
(`extended/search_cut.py`: every row after 2023-12-29 dropped as it is read). Counts only; the definitions and the
caveat (the 126-session count shrinks near the cut) are `extended/exact_run_diffs.py`'s docstring.

    python scripts/run_clean.py --name q172-exact-run-diffs --task Q-172 --hours <H> --mem-gb <G> -- python scripts/exact_run_diffs.py
    python scripts/exact_run_diffs.py --check --starts 4      # a few starts a group; written to a temporary folder

**Heavy** (Stage 2's engine on the atlas): under the run lock, one at a time, one BLAS thread.

**Refusals before anything is read** (exit 2): `results/` outside a clean checkout; a result file that exists;
`--check` writing into `results/`. **The read** (`search_cut.authorise`, before any build): `extended.reader`'s
`authorise_engine_read` for 2020-01-02 to 2023-12-29 and the wrapped files, purpose `exact_run_count_search_years`
under E-232 (the row that specified this count), and the identities' under `identity`; a refusal is exit 3.
**Inside the cut** every data read is cut or refused (`search_cut.UnwrappedRead`); the job's dates are checked against
2023-12-29 (`search_cut.check_dates`), and the runner replays the search block only (`journey_block="search"`).

**Identities, each refusing** (exit 4, nothing written; `identity/search_cut_identity.py`): **nested** (the point-arm
stream on the cut at 2022-12-30 equals the one at 2023-12-29, block for block, to 2022-12-30) and **u1_point** (U1's
point-arm start rows equal the cut build's, every column, on every search start whose 252-session replay ends by
2023-12-29 -- a sample with `--check`); then every run's payouts and fees against the engine's totals, and `_one_start`'s
record equal to the adapter's on every start.

**Writes** `results/exact_run_diffs.csv` (sections `checked`, `moved`; no date, no money, no measure) with its
manifest through `extended.results`: seed the runner's (`user_beside.DENIAL_SEED`, each start's path seed
`lockstep.child_seed(20261920, 0, start_day)`), the record read (m-8: each start's exact h-session run against its
long run cut at the block's end), the `off` records reused from the u1_point identity's runs (`record_reuse`, the
Q-172 audit's C3), the read's ruling (E-248, its C4), the cut's files and the vendored checks switched off (none), the
identities, the timing and peak memory. Prints counts of starts and timings only -- no difference count.
"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile
import time
from pathlib import Path

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_k, "1")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for _p in (str(ROOT), str(ROOT / "identity")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()

import search_cut_identity as SCI  # noqa: E402

from extended import exact_run_diffs as X  # noqa: E402
from extended import reader  # noqa: E402
from extended import search_cut as SC  # noqa: E402
from extended import user_beside as B  # noqa: E402
from extended.procmem import working_set_mb  # noqa: E402

TASK = X.TASK
RESULT = "exact_run_diffs"
SCRIPT = "scripts/exact_run_diffs.py"
PURPOSE = "exact_run_count_search_years"
READ_ROW = "E-232"
DESIGN, ARM = SCI.DESIGN, SCI.ARM


def refused(msg: str) -> str:
    return msg if msg.startswith("REFUSED") else f"REFUSED ({TASK}): {msg}"


def run_problems(outs: list[dict], what: str) -> list[str]:
    out = []
    for k in ("pay", "cash", "fee"):
        n = int(sum(x[f"{k}_bad"] for x in outs))
        if n:
            out.append(f"{what}: {n} runs' {k} check against the engine's totals fails")
    n = sum(1 for x in outs if x["record_same"] is not True)
    if n:
        out.append(f"{what}: {n} starts whose _one_start record is not the adapter's")
    return out


def sample(starts: dict[int, str], k: int | None) -> dict[int, str]:
    """With `--check`: k starts of each group, spread evenly (the last cut starts among them)."""
    import user_journey as UJ

    if k is None:
        return starts
    out = {}
    for g in X.GROUPS:
        ss = [s for s, gg in starts.items() if gg == g]
        out.update({ss[i]: g for i in UJ.start_choice(len(ss), k)})
    return dict(sorted(out.items()))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="a few starts a group; written to a temporary folder")
    ap.add_argument("--starts", type=int, default=None, help="with --check: starts a group (and U1 starts)")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--results-dir", default=None, help="default: results/ (only from a clean checkout)")
    a = ap.parse_args(argv)
    if (a.starts is not None) != a.check:
        print(refused("--starts goes with --check, and --check with --starts"))
        return 2
    from extended import results as XR

    tmp = tempfile.TemporaryDirectory(prefix="exact_run_diffs_check_") if a.check else None
    target = Path(tmp.name) if tmp else (Path(a.results_dir) if a.results_dir else XR.RESULTS_DIR)
    if XR.protected(target):
        why = XR.clean_run_problem()
        if why:
            print(refused(f"{target} is written only from a clean checkout -- {why}"))
            return 2
    csv = target / f"{RESULT}.csv"
    if csv.exists() or XR.manifest_path_for(csv).exists():
        print(refused(f"{csv} exists; a result file is never overwritten"))
        return 2
    try:
        SC.authorise(purpose=PURPOSE, declaration=READ_ROW,
                     what=f"{TASK}: P-14's point-arm job inside the search cut, for the exact-run difference count")
        SC.authorise(purpose="identity", declaration=SCI.READ_ROW,
                     what=f"{TASK}: the search cut's identities (nested, u1_point) inside the cut")
    except (reader.ReadRefused, FileNotFoundError, SC.LateRow) as exc:
        print(refused(str(exc)), flush=True)
        return 3
    from propedge import RESULTS_DIR as RD

    t0 = time.time()
    timing: dict[str, float] = {}
    short, _, _ = SCI.build_point(SCI.NESTED_LAST)
    job, c, log = SCI.build_point(SC.LAST_DAY)
    timing["builds_s"] = round(time.time() - t0, 1)
    print(f"  built: the cut at {SCI.NESTED_LAST} ({len(short['dates'])} days) and at {SC.LAST_DAY} "
          f"({len(job['dates'])} days) in {timing['builds_s']:.0f} s; peak {working_set_mb(peak=True):.0f} MB", flush=True)
    p = SCI.nested(short, job)
    nested_n = len(short["dates"])
    del short
    print(f"  identity nested: {nested_n} blocks -- {'HELD' if not p else 'FAILED'}", flush=True)
    if p:
        for x in p:
            print(f"  {x}")
        print(refused("an identity failed; nothing is written"))
        return 4
    n = len(job["dates"])
    starts = sample(X.choose_starts(n), a.starts)
    comparable = SCI.comparable_starts(n)
    if a.check:
        import user_journey as UJ

        comparable = [comparable[i] for i in UJ.start_choice(len(comparable), a.starts)]
    t1 = time.time()
    u1_outs = SCI.run_off(job, comparable, a.workers)
    timing["u1_point_s"] = round(time.time() - t1, 1)
    nu1, q = SCI.u1_point(RD, c, u1_outs)
    q += run_problems(u1_outs, "u1_point")
    print(f"  identity u1_point: {nu1} start rows in {timing['u1_point_s']:.0f} s -- {'HELD' if not q else 'FAILED'}",
          flush=True)
    if q:
        for x in q[:6]:
            print(f"  {x}")
        print(refused("an identity failed; nothing is written"))
        return 4
    rows: list[dict] = []
    per_start: dict[str, float] = {}
    reuse_off: list[int] = []
    for rname in X.RESPONSES:
        t2 = time.time()
        resp = B.BY_NAME[rname]
        reuse = {int(x["rec"]["start_day"]): x for x in u1_outs} if rname == "off" else {}
        if rname == "off":
            reuse_off = sorted(s for s in starts if s in reuse)
        todo = [s for s in starts if s not in reuse]
        outs = B.run_starts(DESIGN, ARM, resp, job, todo, a.workers, journey=True, journey_block="search")
        outs = sorted([*outs, *(reuse[s] for s in starts if s in reuse)], key=lambda x: int(x["rec"]["start_day"]))
        bad = run_problems(outs, rname)
        if bad:
            for x in bad:
                print(f"  {x}")
            print(refused("a run check failed; nothing is written"))
            return 4
        rows += X.count_rows(outs, design=DESIGN, arm=ARM, response=rname, n=n, groups=starts)
        timing[f"{rname}_s"] = round(time.time() - t2, 1)
        per_start[rname] = round(timing[f"{rname}_s"] / max(1, len(todo)), 2)
        print(f"  {rname}: {len(outs)} starts ({len(todo)} run) in {timing[f'{rname}_s']:.0f} s; peak "
              f"{working_set_mb(peak=True):.0f} MB", flush=True)
        del outs
    frame = X.frame(rows)
    bad = X.output_problems(frame)
    if bad:
        print(refused(f"the frame is not this reading's: {bad[:3]}"))
        return 5
    timing["total_s"] = round(time.time() - t0, 1)
    params = {
        "task": TASK, "decisions": ["E-208", "E-232", "E-248", "MEASURES section 6"], "design": "P-14", "arm": ARM,
        "responses": list(X.RESPONSES), "horizons": list(X.HORIZONS), "purpose": PURPOSE, "read_row": READ_ROW,
        "starts": {"cut": f"the last {X.CUT_STARTS} search starts", "control": f"every {X.CONTROL_EVERY}th earlier",
                   "n_sessions": n, "chosen": len(starts),
                   "check_sample": a.starts},
        "caveat": "an h-session exact run is made only when h < L = min(252, n - s): near the cut the 126 count "
                  "shrinks over the last 126 starts (90, 63, 21 likewise); `checked` per horizon says how many",
        "record_read": "each start's exact h-session run's event days against its long run cut at the search block's "
                       "end (user_beside.run_starts journey=True, exact_every 1); classified against the long "
                       "record's days (exact_run_diffs.classify)",
        "record_reuse": f"under `off`, the records of the chosen starts inside the u1_point identity's set (s + "
                        f"{X.LONG} <= n: {len(reuse_off)} starts) are "
                        "the identity's own runs -- the same run_starts call (response off, journey=True, "
                        "journey_block='search') -- not run again; denial_25 runs every chosen start "
                        "(the Q-172 audit's C3)",
        "read_ruling": "E-248: the point arm only, inputs cut at the read, no held-out read row (narrowing MEASURES "
                       "section 6's 'both of U1's arms'; the Q-172 audit's C4)",
        "cut": {"last": SC.LAST_DAY.isoformat(), "files": log.files_read("cut"),
                "passthrough": log.files_read("passthrough"), "switched_off": SC.switched_off(),
                "day_list": "the bars manifest's day_list read whole, never cut"},
        "identities": {"nested": f"HELD on {nested_n} blocks to {SCI.NESTED_LAST}",
                       "u1_point": f"HELD on {nu1} start rows, every column of user_journey.csv"},
        "seed": {"denial_seed": B.DENIAL_SEED, "start_seed": "lockstep.child_seed(20261920, 0, start_day)"},
        "workers": int(a.workers), "timing": timing, "seconds_per_start_run": per_start,
        "peak_working_set_mb": round(working_set_mb(peak=True), 0),
    }
    paths = XR.write_result(frame, RESULT, script=SCRIPT, seed=B.DENIAL_SEED, parameters=params, results_dir=target,
                            exploratory=False, variant_count=len(X.RESPONSES),
                            description=("Q-172 (MEASURES section 6): exact-length-run differences on P-14's point "
                                         "arm, search years only (the job built inside the search cut), responses "
                                         "off and denial_25, horizons 21/63/90/126; counts only"))
    XR.read_result(paths[0])
    print(f"  wrote {paths[0].name} ({len(frame)} rows){' to a temporary folder (--check)' if a.check else ''}; "
          f"total {timing['total_s']:.0f} s; peak working set {working_set_mb(peak=True):.0f} MB", flush=True)
    print(f"  per start run: {per_start}", flush=True)
    if tmp:
        tmp.cleanup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
