"""The child process of `tests/test_survey_route.py` (Q-215): the vendored tree on its path, synthetic bars only
(`tests/survey_route_world.py`), never the bar store.

    python tests/survey_route_child.py trailing

`trailing`: the route's trailing range (`survey_route.trailing`, on the walker arrays the real run feeds it --
`atlas_local.day_arrays` through `design_trades.history_from_arrays`) against Q-171's own (`s1_range.add_trailing` on
`s1_range.day_table` of the same bars, its default vendored arrays), every session, NaN for NaN; and a planted
look-ahead (the trailing mean reading its own day) shown to differ. Prints one JSON line last.
"""
from __future__ import annotations

import inspect
import json
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for p in (str(ROOT), str(ROOT / "tests")):
    if p not in sys.path:
        sys.path.insert(0, p)

from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()

import numpy as np  # noqa: E402

from extended import design_trades as DT  # noqa: E402
from extended import s1_range as S1R  # noqa: E402
from extended import survey_route as SR  # noqa: E402

import survey_route_world as RW  # noqa: E402
from propedge.research import atlas_local  # noqa: E402


def _same(a: np.ndarray, b: np.ndarray) -> bool:
    a, b = np.asarray(a, float), np.asarray(b, float)
    return a.shape == b.shape and bool(np.array_equal(np.isnan(a), np.isnan(b))) and \
        bool(np.array_equal(a[~np.isnan(a)], b[~np.isnan(b)]))


def check_trailing() -> dict:
    bars = RW.bars()
    cal = RW.fake_sources(bars)
    ref = S1R.add_trailing(S1R.day_table(bars, fomc=(), bls=(), src=cal))
    days = [str(d) for d in ref["date"]]
    by = {str(d): g for d, g in bars.groupby("day", sort=True)}
    arrays = {d: tuple(np.array([np.nan if x is None else x for x in v], dtype=float)
                       for v in atlas_local.day_arrays(by[d])) for d in days}
    hist = DT.history_from_arrays(days, arrays)
    kinds = dict(zip(days, ref["day_kind"].astype(str)))
    got = SR.trailing(hist, day_kinds=kinds, cal=cal)
    equal = all(_same(got[s], ref[f"trail_{s}"].to_numpy(float)) for s in S1R.SESSIONS)
    src = textwrap.dedent(inspect.getsource(SR.trailing))
    old = "out[s] = S1R.trailing_ranges(rng[s], ok)"
    ns: dict = {}
    exec(compile("from __future__ import annotations\n" + src.replace(old, "out[s] = S1R.trailing_ranges("
                 "np.roll(rng[s], -1), np.roll(ok, -1))"), SR.__file__, "exec"), SR.__dict__, ns)
    bad = ns["trailing"](hist, day_kinds=kinds, cal=cal)
    mutant_equal = all(_same(bad[s], ref[f"trail_{s}"].to_numpy(float)) for s in S1R.SESSIONS)
    finite = int(sum(np.isfinite(got[s]).sum() for s in S1R.SESSIONS))
    return {"equal": bool(equal), "mutant_equal": bool(mutant_equal), "finite": finite,
            "sessions": len(S1R.SESSIONS), "days": len(days)}


def main(argv: list[str]) -> int:
    if argv != ["trailing"]:
        raise SystemExit("usage: survey_route_child.py trailing")
    out = check_trailing()
    print(json.dumps(out, sort_keys=True))
    return 0 if out["equal"] and not out["mutant_equal"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
