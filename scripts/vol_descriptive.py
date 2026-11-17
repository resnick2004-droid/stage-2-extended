"""EXPLORATORY (Q-121, E-157 (a1)): NQ's session range in points and in percent, and the side-free first-exit time of
fixed and range-scaled bands, by calendar year and quarter, on the **choice block only** (2020-01-02 to 2023-12-29) --
a property of the bars: no sign, no target-against-stop split, no win share, no trade of any design. Beside; it decides
nothing. The definitions are `extended/vol_descriptive.py`'s docstring.

    python scripts/run_clean.py --name q121-vol-descriptive --task Q-121 --hours 1 --mem-gb 1.5 -- python scripts/vol_descriptive.py
    python scripts/vol_descriptive.py --results-dir <a temporary folder>          # anywhere but results/: no clean run

**Refusals, before anything is read** (exit 2): a span reaching past 2023-12-29 (`vol_descriptive.check_span`: the
judged block, from 2024-01-02, is (a2)'s under a pinned described reading, never this script's); `results/` outside a
clean checkout (`extended.results.clean_run_problem`); a result file that exists (never overwritten).

**The reads**, through `extended.reader` only, inside the choice block (no purpose tag, not ledgered, E-019): the bars
(`ts`, `day`, `open`, `high`, `low`, `close`) and Stage 2's A1 `days` table (`date`, `day_kind`) for the identity;
Stage 2's FOMC and BLS calendars (published in advance) through the vendored `atlas_walk.params` on A1's configuration,
exactly as A1's walk read them. Every returned day is checked again (`check_days`) before anything is computed.

**Identities, each refusing** (exit 4, nothing written; a failure prints the identity, the count of differences and the
first differing session's date and mark, never a value):

* **days** -- every described session's day kind equals Stage 2's A1 `days` table (`vendor/stage2/data/atlas/A1/
  days.parquet`, column `day_kind`) on its date, and every A1 date of the span that has a bar is described;
* **walk** -- on every walked session, each set's entries equal `fv3_rung_walk.entries` (the same marks, a report day's
  before the cut dropped, at the set's delay), and every walk the breakeven cannot touch (no next FV3 session open, or
  that open not in the walk's favour: `be_open`, `be_favour`) has, at each fixed band (50, 100, 150 ticks) and every R
  of the grid, the first-exit bar of `fv3_rung_walk.walk` (its `exit` where its `kind` is a stop or a target) and is
  open exactly where its kind is the 15:08 flatten -- both directions, tolerance zero (whole bars). The count compared
  is printed.

**Writes** `results/q121_vol_descriptive_a1.csv` (sections `session`, `range`, `band`, `band_mark`) with its manifest
through `extended.results` (exploratory; no seed: nothing is drawn; variant count 1). Prints the identity lines, the
section row counts, the timing and the peak working set -- no range, time or share.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from extended import reader  # noqa: E402
from extended import vol_descriptive as V  # noqa: E402
from extended.procmem import working_set_mb  # noqa: E402

TASK = "Q-121"
RESULT = "q121_vol_descriptive_a1"
SCRIPT = "scripts/vol_descriptive.py"
BAR_COLUMNS = ["ts", "day", "open", "high", "low", "close"]
DAYS_FAMILY, DAYS_TABLE = "A1", "days"
DATA_FILES = ("data/bars/NQ/bars.parquet", "data/atlas/A1/days.parquet")


def refused(msg: str) -> str:
    return msg if msg.startswith("REFUSED") else f"REFUSED ({TASK}): {msg}"


def release_days() -> tuple[set[int], set[int], int]:
    """(FOMC days, BLS 08:30 ET report days, the cut's slot) as A1's walk read them (`atlas_walk.params`)."""
    from propedge.research import atlas_walk

    q = atlas_walk.params(atlas_walk.config(DAYS_FAMILY))
    return {int(x) for x in q["fomc"]}, {int(x) for x in q["bls"]}, int(q["bls_cut"])


def kind_problems(sessions: pd.DataFrame, days: pd.DataFrame) -> list[str]:
    """The days identity: each session's kind is A1's on its date; each A1 date with a bar is a session."""
    a1 = dict(zip(days["date"].astype(str), days["day_kind"].astype(str)))
    mine = dict(zip(sessions["date"].astype(str), sessions["day_kind"].astype(str)))
    missing = sorted(d for d in mine if d not in a1)
    differ = sorted(d for d in mine if d in a1 and a1[d] != mine[d])
    absent = sorted(d for d, k in a1.items() if k != "x" and d not in mine)
    out = []
    for what, ds in (("described sessions not in A1's days table", missing),
                     ("sessions whose day kind differs from A1's", differ),
                     ("A1 dates with a bar not described", absent)):
        if ds:
            out.append(f"days: {len(ds)} {what} (first {ds[0]})")
    return out


def walk_problems(walks: dict, sets=V.SETS, cut: int = V.BLS_CUT) -> tuple[int, list[str]]:
    """The walk identity against `fv3_rung_walk` (entries, and every breakeven-free walk's exit at the fixed bands):
    (walks x brackets compared, problems)."""
    from propedge.research import fv3_rung_walk as F

    bl = F.brackets(stops=V.FIXED_BANDS_TICKS, rrs=V.RR_GRID)
    compared, bad_entries, bad_exits = 0, [], []
    for i, day in enumerate(walks["dates"]):
        o, h, l, c = walks["arrays"][day]
        kind = walks["kinds"][i]
        for name, (marks, delay) in sets.items():
            ms = [int(m) for m in marks if not (kind == "b" and int(m) < cut)]
            ent = F.entries(o, ms, delay)
            mine = V.entries(o, marks, delay, cut if kind == "b" else None)
            if [(t, j) for t, d, j in ent if d > 0] != mine or [(t, j) for t, d, j in ent if d < 0] != mine:
                bad_entries.append(f"{day} {name}")
                continue
            if not ent:
                continue
            res = F.walk(o, h, l, c, [d for _, d, _ in ent], [j for _, _, j in ent], V.TICK, bl)
            codes = walks[name][i]                                     # (marks, 2, bands, R)
            pos = {int(m): r for r, m in enumerate(marks)}
            free = (res["be_open"] == -1) | (res["be_favour"] <= 0)
            for w, (t, d, j) in enumerate(ent):
                if not free[w]:
                    continue
                for b in range(len(bl)):
                    s_i, k_i = divmod(b, len(V.RR_GRID))
                    got = int(codes[pos[t], 1 if d > 0 else 0, s_i, k_i])
                    kd, ex = int(res["kind"][w, b]), int(res["exit"][w, b])
                    want = V.OPEN if kd == F.FLATTEN else (ex - j + 1 if kd in (F.STOP, F.TARGET) else None)
                    compared += 1
                    if want is None or got != want:
                        bad_exits.append(f"{day} {name} mark {V.ct(t)} band {V.BANDS[s_i]}")
    out = []
    if bad_entries:
        out.append(f"walk: {len(bad_entries)} session-sets whose entries differ from fv3_rung_walk.entries "
                   f"(first {bad_entries[0]})")
    if bad_exits:
        out.append(f"walk: {len(bad_exits)} walk-brackets whose first exit differs from fv3_rung_walk.walk "
                   f"(first {bad_exits[0]})")
    if compared == 0:
        out.append("walk: nothing compared")
    return compared, out


def data_manifest() -> dict[str, str]:
    """The data manifest's sha256 of the files read (`vendor/DATA_MANIFEST_stage2.sha256`; the files are not hashed
    here)."""
    p = ROOT / "vendor" / "DATA_MANIFEST_stage2.sha256"
    out = {}
    if p.is_file():
        for line in p.read_text(encoding="utf-8").splitlines():
            parts = line.split(None, 1)
            if len(parts) == 2 and parts[1].strip().lstrip("*") in DATA_FILES:
                out[parts[1].strip().lstrip("*")] = parts[0]
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--start", default=V.FIRST_DAY.isoformat())
    ap.add_argument("--end", default=V.LAST_DAY.isoformat())
    ap.add_argument("--results-dir", default=None, help="default: results/ (only from a clean checkout)")
    a = ap.parse_args(argv)
    try:
        start, end = V.check_span(a.start, a.end)
    except (V.BeyondChoiceBlock, ValueError) as exc:
        print(refused(str(exc)))
        return 2
    from extended import results as XR

    target = Path(a.results_dir) if a.results_dir else XR.RESULTS_DIR
    if XR.protected(target):
        why = XR.clean_run_problem()
        if why:
            print(refused(f"{target} is written only from a clean checkout -- {why}. python scripts/run_clean.py "
                          f"--name q121-vol-descriptive --task {TASK} --hours 1 --mem-gb 1.5 -- python {SCRIPT}"))
            return 2
    csv = target / f"{RESULT}.csv"
    if csv.exists() or XR.manifest_path_for(csv).exists():
        print(refused(f"{csv} exists; a result file is never overwritten"))
        return 2
    t0 = time.time()
    bars = reader.read_bars(start, end, columns=BAR_COLUMNS,
                            what=f"{TASK}: the choice block's bars for the bars-only volatility descriptive")
    V.check_days(bars["day"].astype(str).unique())
    fomc, bls, cut = release_days()
    if cut != V.BLS_CUT:
        print(refused(f"A1's BLS cut is slot {cut}, not {V.BLS_CUT}"))
        return 4
    sessions, walks = V.describe(bars, fomc=fomc, bls=bls, cut=cut, keep_arrays=True)
    del bars
    walks["kinds"] = sessions.loc[sessions["walked"], "day_kind"].astype(str).tolist()
    t_describe = time.time() - t0
    days = reader.read_walks(DAYS_FAMILY, DAYS_TABLE, start, end, columns=["date", "day_kind"],
                             what=f"{TASK}: A1's day kinds for the days identity")
    problems = kind_problems(sessions, days)
    print(f"  identity days: {len(sessions)} sessions against A1's days table -- "
          f"{'HELD' if not problems else 'FAILED'}", flush=True)
    compared, wp = walk_problems(walks, cut=cut)
    print(f"  identity walk: {compared} walk-brackets against fv3_rung_walk -- {'HELD' if not wp else 'FAILED'}",
          flush=True)
    problems += wp
    if problems:
        for p in problems:
            print(f"  {p}")
        print(refused("an identity failed; nothing is written"))
        return 4
    walks.pop("arrays")
    frame = V.summarise(sessions, walks)
    bad = V.output_problems(frame)
    if bad:
        print(refused(f"the frame is not this reading's: {bad[:3]}"))
        return 5
    params = {
        "task": TASK, "decision": V.DECISION, "span": [start.isoformat(), end.isoformat()],
        "last_day_refused_after": V.LAST_DAY.isoformat(), "session": "atlas_local.day_arrays (17:01-15:10 CT bar ends)",
        "walked_kinds": list(V.WALKED_KINDS), "trail_sessions": V.TRAIL, "range_fractions": list(V.RANGE_FRACTIONS),
        "fixed_bands_ticks": list(V.FIXED_BANDS_TICKS), "rr_grid": list(V.RR_GRID), "bands": list(V.BANDS),
        "sets": {k: {"marks": len(m), "first": V.ct(m[0]), "last": V.ct(m[-1]), "delay": d}
                 for k, (m, d) in V.SETS.items()},
        "bls_cut_slot": cut, "walk_end": "the bar ending 15:08 CT", "quantiles": "inverted empirical CDF",
        "identities": {"days": f"{len(sessions)} sessions vs A1 days.day_kind", "walk": f"{compared} walk-brackets "
                       "vs fv3_rung_walk.walk (breakeven-free walks, fixed bands, every R), tolerance 0"},
        "data_manifest": data_manifest(),
    }
    paths = XR.write_result(frame, RESULT, script=SCRIPT, seed=None, require_seed=False, parameters=params,
                            results_dir=target, exploratory=True, variant_count=1,
                            description=("Q-121 (E-157 (a1)): the choice block's session range in points and percent "
                                         "and the side-free first-exit time of fixed and range-scaled bands, by year "
                                         "and quarter; bars only, no side, no outcome; descriptive, decides nothing"))
    counts = frame["section"].value_counts()
    print("  rows: " + ", ".join(f"{s} {int(counts.get(s, 0))}" for s in V.SECTIONS))
    print(f"  wrote {paths[0].name}; describe {t_describe:.0f} s, total {time.time() - t0:.0f} s, peak working set "
          f"{working_set_mb(peak=True):.0f} MB", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
