"""Q-172: the search cut's identities (`extended/search_cut.py`), under the purpose `identity`. **No identity here reads
a day after 2023-12-29** (the O-7 ruling): both builds are made inside the cut, and U1's file is a result file whose
rows for any start whose replay passes 2023-12-29 are dropped as it is read.

    python identity/search_cut_identity.py              # both identities on P-14's point arm; HOLDS / FAILS lines
    python identity/search_cut_identity.py --u1-starts 8 # U1's equality on 8 of the comparable starts (a quick look)

* **nested** -- P-14's point-arm stream built on the cut at 2022-12-30 equals the stream built on the cut at
  2023-12-29, block for block, on every date up to 2022-12-30 (`exact_run_diffs.nested_problems`; blocks compared by
  `canonical`, every float by its hex). With the builder causal at the cut this must hold; it tests the wrapper (a read
  that escaped the cut, a cache serving the other build's rows, a statistic pooled across the cut's end).
* **u1_point** -- the point-arm `start` rows of Stage 2's `vendor/stage2/results/user_journey.csv` (U1, built on the
  whole window) for the search starts whose 252-session replay ends on or before 2023-12-29 equal the cut build's
  rows for those starts, bit for bit on every column of the file (`stage2_identity.u1_compare`, E-010's comparison),
  the cut build's runs made by `user_beside.run_starts(..., journey=True)` with every response off. The verdict arm is
  never compared: its bounds pool 2020-2026 trades (the O-7 red team's B-1; the lead's option 2).

Each build's `CutLog` must show A1's events and days and A3's walk read through the cut, nothing refused, nothing kept
past the cut's day; its dates are checked against the cut (`search_cut.check_dates`). The read is authorised through
`extended.reader` (`search_cut.authorise`, purpose `identity`, declaration E-232) before anything is built.
"""
from __future__ import annotations

import argparse
import dataclasses
import sys
import time
from datetime import date
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for _p in (str(ROOT), str(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()

import numpy as np  # noqa: E402

from extended import exact_run_diffs as X  # noqa: E402
from extended import search_cut as SC  # noqa: E402

DESIGN, ARM = "p14", "point"
READ_ROW = "E-232"
NESTED_LAST = date(2022, 12, 30)
WANT = ("data/atlas/A1/events.parquet", "data/atlas/A1/days.parquet", "data/atlas/A3/walks.parquet")


def canonical(x: Any) -> Any:
    """`user_beside_identity.canonical`, extended to dataclasses and plain objects (by their fields, in order)."""
    if dataclasses.is_dataclass(x) and not isinstance(x, type):
        return ("dc", type(x).__name__, tuple((f.name, canonical(getattr(x, f.name))) for f in dataclasses.fields(x)))
    if isinstance(x, dict):
        return ("dict", tuple((canonical(k), canonical(v)) for k, v in x.items()))
    if isinstance(x, np.ndarray):
        return ("ndarray", str(x.dtype), tuple(x.shape), tuple(canonical(v) for v in x.ravel().tolist()))
    if isinstance(x, (list, tuple)):
        return (type(x).__name__, tuple(canonical(v) for v in x))
    if isinstance(x, (bool, np.bool_)):
        return (type(x).__name__, bool(x))
    if isinstance(x, (float, np.floating)):
        return (type(x).__name__, float(x).hex())
    if isinstance(x, (int, np.integer)):
        return (type(x).__name__, int(x))
    if x is None or isinstance(x, str):
        return (type(x).__name__, x)
    if hasattr(x, "__dict__"):
        return ("obj", type(x).__name__, canonical(dict(vars(x))))
    if hasattr(x, "__slots__"):
        return ("slots", type(x).__name__, tuple((s, canonical(getattr(x, s))) for s in x.__slots__))
    raise TypeError(f"no canonical form for a {type(x).__name__}")


def build_point(last: date, rd: Path | None = None) -> tuple[dict[str, Any], dict[str, Any], SC.CutLog]:
    """(P-14's point-arm job, its definition, the cut's log), built by U1's own builder inside the cut at `last`."""
    import user_beside_identity as I

    from propedge import RESULTS_DIR

    with SC.cut(last) as log:
        jobs, c, bad = I.build(rd or RESULTS_DIR, DESIGN)
    if bad:
        raise SystemExit(f"REFUSED ({X.TASK}): the builder's identity rows fail on the cut at {last}: {bad[:3]}")
    probs = log.problems(WANT)
    if probs:
        raise SystemExit(f"REFUSED ({X.TASK}): the cut at {last}: {probs[:3]}")
    job = jobs[ARM]
    SC.check_dates(job["dates"], last, f"P-14's point job on the cut at {last}")
    return job, c, log


def nested(short: dict[str, Any], long: dict[str, Any]) -> list[str]:
    return X.nested_problems(short, long, NESTED_LAST.isoformat(), canon=canonical)


def comparable_starts(n: int) -> list[int]:
    """The search starts whose 252-session replay ends on or before the cut's last day: s + 252 <= n."""
    return list(range(0, int(n) - X.LONG + 1))


def u1_point(rd: Path, c: dict[str, Any], outs: list[dict[str, Any]]) -> tuple[int, list[str]]:
    """(rows compared, problems): the cut build's point-arm start rows against U1's for the same starts; U1's rows of
    any other start are dropped as the file is read."""
    import stage2_identity as SI
    import user_beside_identity as I
    import user_journey as UJ

    from propedge.research import user_journey as U

    ref = I.u1_reference(rd, [DESIGN])
    days = {int(x["rec"]["start_day"]) for x in outs}
    st = ref["start"]
    st = st[(st["config"] == DESIGN) & (st["arm"] == ARM)]
    theirs = [r for r in st.to_dict("records") if int(float(r["start_day"])) in days]
    del st, ref["start"]
    mine = [{**r, "reading": U.READING} for r in UJ.start_rows(c, ARM, outs)]
    probs = []
    if len(theirs) != len(days):
        probs.append(f"u1_point: U1's file holds {len(theirs)} of our {len(days)} starts")
    late = [r["start_date"] for r in mine if str(r["start_date"]) > SC.LAST_DAY.isoformat()]
    if late:
        probs.append(f"u1_point: a start dated {late[0]}, past the cut")
    probs += SI.u1_compare(mine, theirs, ref["columns"], f"{DESIGN} {ARM}", all_starts=False)
    for k in ("pay", "cash", "fee"):
        n = int(sum(x[f"{k}_bad"] for x in outs))
        if n:
            probs.append(f"u1_point: {n} runs' {k} check against the engine's totals fails")
    return len(theirs), probs


def run_off(job: dict[str, Any], starts: list[int], workers: int) -> list[dict[str, Any]]:
    from extended import user_beside as B

    return B.run_starts(DESIGN, ARM, B.BY_NAME["off"], job, starts, workers, journey=True, journey_block="search")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--u1-starts", type=int, default=None, help="U1's equality on this many comparable starts")
    ap.add_argument("--workers", type=int, default=1)
    a = ap.parse_args(argv)
    from propedge import RESULTS_DIR

    import user_journey as UJ

    SC.authorise(purpose="identity", declaration=READ_ROW, what=f"{X.TASK}: the search cut's identities (nested, "
                 "u1_point) on P-14's point arm, inside the cut")
    t0 = time.time()
    short, _, _ = build_point(NESTED_LAST)
    long, c, _ = build_point(SC.LAST_DAY)
    p = nested(short, long)
    print(f"identity {'HOLDS' if not p else 'FAILS'}: nested: {sum(1 for d in short['dates'])} blocks to "
          f"{NESTED_LAST}" + (f" -- {'; '.join(p)}" if p else ""), flush=True)
    del short
    cs = comparable_starts(len(long["dates"]))
    cs = [cs[i] for i in UJ.start_choice(len(cs), a.u1_starts)]
    outs = run_off(long, cs, a.workers)
    n, q = u1_point(RESULTS_DIR, c, outs)
    print(f"identity {'HOLDS' if not q else 'FAILS'}: u1_point: {n} start rows" + (f" -- {'; '.join(q[:4])}" if q else ""),
          flush=True)
    print(f"{time.time() - t0:.0f} s", flush=True)
    return 0 if not (p or q) else 4


if __name__ == "__main__":
    raise SystemExit(main())
