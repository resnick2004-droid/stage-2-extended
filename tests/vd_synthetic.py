"""The child process of `tests/test_vol_descriptive.py` (Q-121): the vendored tree on its path, synthetic bars only
(`extended/synthetic_bars.py`); Stage 2's calendars (published in advance) through A1's configuration. Never reads the
bar store: the script's reader calls are stood in by recorders returning the toys.

    python tests/vd_synthetic.py identity|shift|script|refuse

Prints one JSON line last. Seeds (named by role, outside the 2026xxxx range): `SEED_TOY_BARS` 4221 (the toys' bars),
`SEED_SHIFT` 4222 (`synthetic_bars.replace_from`'s arbitrary values).
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from extended import reader as R  # noqa: E402
from extended import synthetic_bars as SB  # noqa: E402
from extended import vol_descriptive as V  # noqa: E402

SEED_TOY_BARS = 4221
SEED_SHIFT = 4222

_spec = importlib.util.spec_from_file_location("vol_descriptive_script", ROOT / "scripts" / "vol_descriptive.py")
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

from propedge.outcomes.collect_core import C_FLAT, c_slot  # noqa: E402
from propedge.outcomes.orb_core import FLAT_ENTRY  # noqa: E402
from propedge.research import atlas_local, atlas_walk  # noqa: E402
from propedge.research import fv3_rung_walk as F  # noqa: E402
from propedge.research import resolved_coin as rc  # noqa: E402


def toy(start: str, end: str, **kw) -> pd.DataFrame:
    return SB.generate(SB.Spec(start=date.fromisoformat(start), end=date.fromisoformat(end), seed=SEED_TOY_BARS, **kw))


def a1_params() -> dict:
    return atlas_walk.params(atlas_walk.config("A1"))


def days_table(bars: pd.DataFrame, q: dict) -> pd.DataFrame:
    rows = []
    for day, g in bars.groupby("day", sort=True):
        o = np.array([np.nan if x is None else x for x in atlas_local.day_arrays(g)[0]], dtype=float)
        rows.append({"date": str(day), "day_kind": atlas_walk._kind(o, atlas_local.yymmdd(str(day)), q)[0]})
    return pd.DataFrame(rows)


def check_identity() -> dict:
    bars = toy("2021-01-04", "2021-05-28", early_closes=frozenset({date(2021, 2, 10)}))
    fomc, bls, cut = S.release_days()
    sessions, walks = V.describe(bars, fomc=fomc, bls=bls, cut=cut, keep_arrays=True)
    walks["kinds"] = sessions.loc[sessions["walked"], "day_kind"].astype(str).tolist()
    compared, problems = S.walk_problems(walks, cut=cut)
    late = {"p16_marks": ([m for m in V.P16_MARKS if m >= 1205], 0)}
    late_walks = dict(walks)
    rows = [i for i, m in enumerate(V.P16_MARKS) if m >= 1205]
    late_walks["p16_marks"] = walks["p16_marks"][:, rows]
    compared_late, late_problems = S.walk_problems(late_walks, sets=late, cut=cut)
    per_set = {}
    for name in V.SETS:
        n, p = S.walk_problems(walks, sets={name: V.SETS[name]}, cut=cut)
        per_set[name] = n if not p else -1
    tampered = dict(walks)
    E = walks["p16_marks"].copy()
    E[0, rows[0], 1, 0, 3] = 5 if E[0, rows[0], 1, 0, 3] != 5 else 6
    tampered["p16_marks"] = E
    _, tampered_problems = S.walk_problems(tampered, cut=cut)
    q = a1_params()
    table = days_table(bars, q)
    mine = dict(zip(sessions["date"], sessions["day_kind"]))
    kinds_equal = all(mine[d] == k for d, k in zip(table["date"], table["day_kind"]) if d in mine)
    bad_table = table.copy()
    i = int(np.flatnonzero(bad_table["day_kind"].to_numpy() == "n")[0])
    bad_table.loc[i, "day_kind"] = "o"
    t24_hours = sorted(set(atlas_walk.t24_slots()) - {c_slot(8, 30)})
    return {"compared": compared, "walk_problems": problems + late_problems, "compared_late": compared_late,
            "sets_compared": sorted(k for k, v in per_set.items() if v > 0),
            "tampered_walk": tampered_problems, "kinds_equal_atlas_walk": bool(kinds_equal),
            "kinds_seen": sorted(set(mine.values())), "kind_problems": S.kind_problems(sessions, table),
            "tampered_kinds": S.kind_problems(sessions, bad_table),
            "rr_grid_is_fv3s": tuple(V.RR_GRID) == tuple(F.RR_GRID),
            "marks_are_resolved_coins": list(V.P16_MARKS) == rc.marks() and rc.DELAY == 0,
            "cut_is_a1s": cut == V.BLS_CUT == int(q["bls_cut"]) and V.SESSION_END == C_FLAT
            and V.FLAT_ENTRY == FLAT_ENTRY and list(V.P14_SLOTS) == t24_hours and int(q["screen_delay"]) == 5}


def _replace(bars: pd.DataFrame, day: str, hh: int, mm: int, k: int) -> pd.DataFrame:
    return SB.replace_from(bars, SB.ts_of(day, hh, mm), SEED_SHIFT + k)


def _arrays(g: pd.DataFrame):
    return tuple(np.array([np.nan if x is None else x for x in a], dtype=float) for a in atlas_local.day_arrays(g))


def check_shift() -> dict:
    fomc, bls, cut = S.release_days()
    few = {"p14_slots": V.SETS["p14_slots"]}
    trail_cols = ["trail20_range_pts", "trail20_range_pct", "band_ticks_010", "band_ticks_025"]
    trail_changed, walk_changed, range_changed = [], [], []
    finite = distinct = 0
    cuts = 0
    for (a, b), days in ((("2021-02-01", "2021-03-31"), ["2021-03-02", "2021-03-11", "2021-03-12", "2021-03-15",
                                                          "2021-03-16", "2021-03-31"]),
                         (("2021-10-01", "2021-11-30"), ["2021-11-05", "2021-11-08", "2021-11-09", "2021-11-26"])):
        bars = toy(a, b)
        base, _ = V.describe(bars, fomc=fomc, bls=bls, cut=cut, sets=few)
        finite += int(base["trail20_range_pts"].notna().sum())
        distinct += int(base["trail20_range_pts"].nunique())
        for k, d in enumerate(days):
            cuts += 1
            # every bar from the session's 17:00 CT open on replaced: the trailing columns at d and before unchanged
            shifted = _replace(bars, d, 17, 0, k)
            got, _ = V.describe(shifted[shifted["day"] <= d], fomc=fomc, bls=bls, cut=cut, sets=few)
            upto = base[base["date"] <= d].reset_index(drop=True)
            if not upto[trail_cols].equals(got[trail_cols]):
                trail_changed.append(d)
            if not upto.loc[upto["date"] < d, ["range_pts", "range_pct"]].equals(
                    got.loc[got["date"] < d, ["range_pts", "range_pct"]]):
                trail_changed.append(f"{d} earlier ranges")
            row = base[base["date"] == d].iloc[0]
            bt = [*V.FIXED_BANDS_TICKS, *(None if pd.isna(x) else int(x) for x in (row.band_ticks_010,
                                                                                  row.band_ticks_025))]
            # from 15:08 CT on (the bar stamped 15:08 ends 15:09, after the walk's last bar): d's walks unchanged
            o, h, l, c = _arrays(bars[bars["day"] == d])
            w0 = V.walk_session(o, h, l, row.day_kind, bt, V.SETS, cut)
            late = _replace(bars, d, 15, 8, 100 + k)
            o2, h2, l2, _ = _arrays(late[late["day"] == d])
            w1 = V.walk_session(o2, h2, l2, row.day_kind, bt, V.SETS, cut)
            walked = row.day_kind in V.WALKED_KINDS                     # an early close walks nothing at all
            if not all(np.array_equal(w0[s], w1[s]) for s in V.SETS) or                     walked != any((w0[s] != V.NONE).any() for s in V.SETS):
                walk_changed.append(d)
            # from 15:10 CT on: d's range unchanged
            later = _replace(bars, d, 15, 10, 200 + k)
            o3, h3, l3, _ = _arrays(later[later["day"] == d])
            if V.session_measures(o3, h3, l3) != V.session_measures(o, h, l):
                range_changed.append(d)
            # and the bar stamped 15:09 (ending 15:10) IS read: the test can fail
            if (bars["ts"] == SB.ts_of(d, 15, 9)).any():                # (an early close has no such bar)
                moved = _replace(bars, d, 15, 9, 300 + k)
                o4, h4, l4, _ = _arrays(moved[moved["day"] == d])
                if V.session_measures(o4, h4, l4) == V.session_measures(o, h, l):
                    range_changed.append(f"{d} the 15:09 bar unread")
    return {"cuts": cuts, "trail_changed": trail_changed, "walk_changed": walk_changed,
            "range_changed": range_changed, "trail_finite": finite, "trail_distinct": distinct}


class Recorder:
    def __init__(self, bars: pd.DataFrame, table: pd.DataFrame):
        self.bars, self.table = bars, table
        self.spans, self.walk_reads = [], []

    def read_bars(self, start, end, *, columns=None, what="", **kw):
        self.spans.append([str(start), str(end)])
        b = self.bars[(self.bars["day"] >= str(start)) & (self.bars["day"] <= str(end))]
        return b[list(columns)].reset_index(drop=True) if columns else b.reset_index(drop=True)

    def read_walks(self, family, table, start, end, *, columns=None, what="", **kw):
        self.walk_reads.append([family, table])
        t = self.table[(self.table["date"] >= str(start)) & (self.table["date"] <= str(end))]
        return t[list(columns)].reset_index(drop=True)

    @property
    def reads(self) -> int:
        return len(self.spans) + len(self.walk_reads)


def run_main(rec: Recorder, argv: list[str]) -> tuple[int, str]:
    R.read_bars, R.read_walks = rec.read_bars, rec.read_walks
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc_ = S.main(argv)
    return rc_, buf.getvalue()


def results_listing() -> list[str]:
    d = ROOT / "results"
    return sorted(p.name for p in d.iterdir()) if d.is_dir() else []


def check_script() -> dict:
    from extended import results as XR

    before = results_listing()
    bars = toy("2021-01-04", "2021-06-30")
    rec = Recorder(bars, days_table(bars, a1_params()))
    with tempfile.TemporaryDirectory() as tmp:
        t0 = time.time()
        rc_, out = run_main(rec, ["--start", "2021-01-04", "--end", "2021-06-30", "--results-dir", tmp])
        wall = time.time() - t0
        csv = Path(tmp) / f"{S.RESULT}.csv"
        written = csv.is_file()
        ok, _ = XR.verify_result(csv) if written else (False, "")
        frame = pd.read_csv(csv, low_memory=False) if written else pd.DataFrame()
        man = XR.read_manifest(csv) if written else None
        size = csv.stat().st_size if written else 0
    sections = [s for s in V.SECTIONS if s in set(frame.get("section", pd.Series(dtype=str)))]
    return {"rc": rc_, "stdout": out, "written": written, "verified": bool(ok),
            "problems": V.output_problems(frame) if written else ["not written"],
            "manifest_seed": man.seed if man else "none", "exploratory": man.exploratory if man else None,
            "sections": sections, "read_spans": rec.spans, "walk_reads": rec.walk_reads,
            "results_untouched": results_listing() == before, "wall_s": wall,
            "sessions": int(bars["day"].nunique()), "csv_bytes": size}


def check_refuse() -> dict:
    bars = toy("2021-01-04", "2021-02-26")
    table = days_table(bars, a1_params())
    out = {}
    with tempfile.TemporaryDirectory() as tmp:
        for case, argv in (("end_2024", ["--end", "2024-01-02", "--results-dir", tmp]),
                           ("start_2024", ["--start", "2024-01-02", "--end", "2024-01-02", "--results-dir", tmp]),
                           ("seal_day", ["--end", "2023-12-30", "--results-dir", tmp]),
                           ("results_outside_clean_run", [])):
            rec = Recorder(bars, table)
            rc_, s = run_main(rec, argv)
            out[case] = {"rc": rc_, "reads": rec.reads, "stdout": s}
    bad = table.copy()
    bad.loc[int(np.flatnonzero(bad["day_kind"].to_numpy() == "n")[0]), "day_kind"] = "e"
    with tempfile.TemporaryDirectory() as tmp:
        rec = Recorder(bars, bad)
        rc_, s = run_main(rec, ["--start", "2021-01-04", "--end", "2021-02-26", "--results-dir", tmp])
        out["identity_fails"] = {"rc": rc_, "stdout": s, "written": any(Path(tmp).iterdir())}
    return out


if __name__ == "__main__":
    checks = {"identity": check_identity, "shift": check_shift, "script": check_script, "refuse": check_refuse}
    res = checks[sys.argv[1]]()
    print(json.dumps(res, default=str))
