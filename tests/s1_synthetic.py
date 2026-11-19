"""The child process of `tests/test_s1_range.py` (Q-171): the vendored tree on its path, synthetic bars only
(`extended/synthetic_bars.py`); Stage 2's calendars (published in advance) through A1's configuration. Never reads the
bar store: the script's reader calls are stood in by recorders returning the toys, and the void calendar by a
synthetic one (every overnight clean, the toys' own last bars).

    python tests/s1_synthetic.py shift|script|refuse

Prints one JSON line last. Seeds (named by role, outside the 2026xxxx range): `SEED_TOY_BARS` 4721 (the toys' bars),
`SEED_SHIFT` 4722 (`synthetic_bars.replace_from`'s arbitrary values; the k-th cut takes the k-th child of it).
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import os
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

from extended import day_calendar as DC  # noqa: E402
from extended import lever_space as LS  # noqa: E402
from extended import price_levels as pl  # noqa: E402
from extended import reader as R  # noqa: E402
from extended import s1_range as S  # noqa: E402
from extended import synthetic_bars as SB  # noqa: E402
from extended import vol_descriptive as V  # noqa: E402

SEED_TOY_BARS = 4721
SEED_SHIFT = 4722

_spec = importlib.util.spec_from_file_location("s1_range_script", ROOT / "scripts" / "s1_range.py")
Sc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(Sc)

from propedge.research import atlas_local, atlas_walk  # noqa: E402


def toy(start: str, end: str, **kw) -> pd.DataFrame:
    return SB.generate(SB.Spec(start=date.fromisoformat(start), end=date.fromisoformat(end), seed=SEED_TOY_BARS, **kw))


def shift_seed(k: int) -> int:
    return int(np.random.SeedSequence(SEED_SHIFT).spawn(k + 1)[k].generate_state(1)[0])


def fake_sources(bars: pd.DataFrame) -> DC.Sources:
    """The void calendar of the toys: their days, their last bars (CT), every overnight clean; nothing else."""
    days = sorted({date.fromisoformat(d) for d in bars["day"].astype(str).unique()})
    last = bars.groupby("day")["ts"].max()
    ct = pd.to_datetime(last.to_numpy(), unit="s", utc=True).tz_convert(SB.CHICAGO)
    lb = {date.fromisoformat(str(d)): f"{t.hour:02d}:{t.minute:02d}" for d, t in zip(last.index, ct)}
    flags = {d: {"day": d.isoformat(), "verdict": "OK", "void": "", "missing_after_reopen": "0", "special": ""}
             for d in days}
    return DC.Sources(days, {}, frozenset(), frozenset(), lb, frozenset(), frozenset(), flags, None)


def days_table(bars: pd.DataFrame) -> pd.DataFrame:
    q = atlas_walk.params(atlas_walk.config("A1"))
    rows = []
    for day, g in bars.groupby("day", sort=True):
        o = np.array([np.nan if x is None else x for x in atlas_local.day_arrays(g)[0]], dtype=float)
        rows.append({"date": str(day), "day_kind": atlas_walk._kind(o, atlas_local.yymmdd(str(day)), q)[0]})
    return pd.DataFrame(rows)


def trails(bars: pd.DataFrame, src: DC.Sources) -> pd.DataFrame:
    fomc, bls, _ = Sc.release_days()
    return S.add_trailing(S.day_table(bars, fomc=fomc, bls=bls, src=src))


# ------------------------------------------------------------------------------------------------ shift


def check_shift() -> dict:
    cols = [f"trail_{s}" for s in S.SESSIONS]
    changed, unread, checked, finite, distinct = [], [], 0, {}, {}
    # a roll (2021-03-12), the US change (03-14), the UK change (03-28); the UK's end (10-31), the US's (11-07) and
    # an early close (11-26)
    for (a, b), cuts in ((("2021-02-01", "2021-04-30"), ["2021-03-12", "2021-03-15", "2021-03-29", "2021-04-01"]),
                         (("2021-10-01", "2021-11-30"), ["2021-11-01", "2021-11-08", "2021-11-29"])):
        bars = toy(a, b)
        src = fake_sources(bars)
        base = trails(bars, src)
        for c in cols:
            finite[c] = finite.get(c, 0) + int(base[c].notna().sum())
            distinct[c] = distinct.get(c, 0) + int(base[c].nunique())
        for k, d in enumerate(cuts):
            checked += 1
            shifted = SB.replace_from(bars, SB.ts_of(d, 17, 0), shift_seed(k))   # from d's reopen on
            got = trails(shifted, src)
            upto = base["date"] <= d
            if not base.loc[upto, cols].reset_index(drop=True).equals(got.loc[upto, cols].reset_index(drop=True)):
                changed.append(d)
            # power: from the previous walked day's reopen on, d's trailing ranges move (that day is read; an early
            # close before d is never read, so it is skipped)
            i = int(np.flatnonzero(base["date"].to_numpy() == d)[0])
            walked = np.flatnonzero(base["day_kind"].isin(S.WALKED_KINDS).to_numpy()[:i])
            prev = str(base["date"].iloc[int(walked[-1])])
            moved = trails(SB.replace_from(bars, SB.ts_of(prev, 17, 0), shift_seed(100 + k)), src)
            if base.loc[i, cols].equals(moved.loc[i, cols]):
                unread.append(d)
    ok = (not changed and not unread and checked >= 4
          and all(finite[c] > 0 and distinct[c] > 1 for c in cols))
    return {"ok": ok, "checked_days": checked, "changed": changed, "previous_day_unread": unread,
            "finite": finite, "distinct": distinct, "sessions": list(S.SESSIONS)}


# ------------------------------------------------------------------------------------------------ the script


class Recorder:
    def __init__(self, bars: pd.DataFrame, table: pd.DataFrame):
        self.bars, self.table = bars, table
        self.spans, self.walk_reads, self.purposes, self.rows = [], [], [], []

    def read_bars(self, start, end, *, purpose=None, declaration=None, columns=None, what="", **kw):
        self.spans.append([str(start), str(end)])
        self.purposes.append(purpose)
        self.rows.append(declaration)
        b = self.bars[(self.bars["day"] >= str(start)) & (self.bars["day"] <= str(end))]
        return b[list(columns)].reset_index(drop=True) if columns else b.reset_index(drop=True)

    def read_walks(self, family, table, start, end, *, columns=None, what="", **kw):
        self.walk_reads.append([family, table, str(start), str(end)])
        t = self.table[(self.table["date"] >= str(start)) & (self.table["date"] <= str(end))]
        return t[list(columns)].reset_index(drop=True)

    @property
    def reads(self) -> int:
        return len(self.spans) + len(self.walk_reads)


def run_main(rec: Recorder, argv: list[str], src: DC.Sources) -> tuple[int, str]:
    R.read_bars, R.read_walks = rec.read_bars, rec.read_walks
    Sc.load_sources = lambda: src
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc_ = Sc.main(argv)
    return rc_, buf.getvalue()


def q121_file(bars: pd.DataFrame, folder: Path, tamper: bool = False) -> Path:
    """Q-121's reading of the toys (its own module, no walk), written with a manifest; the script's pin set to it."""
    from extended import results as XR

    fomc, bls, cut = Sc.release_days()
    sessions, walks = V.describe(bars, fomc=fomc, bls=bls, cut=cut, sets={})
    frame = V.summarise(sessions, walks, sets={})
    if tamper:
        i = frame.index[(frame["section"] == "range") & (frame["measure"] == "trail20_range_pts")
                        & (frame["period_kind"] == "year")][0]
        frame.loc[i, "median"] = float(frame.loc[i, "median"]) + 0.25
    folder.mkdir(parents=True, exist_ok=True)
    csv, _ = XR.write_result(frame, Sc.Q121_NAME, script="tests/s1_synthetic.py", seed=None, require_seed=False,
                             parameters={"toy": True}, results_dir=folder, exploratory=True)
    Sc.Q121_SHA256 = hashlib.sha256(csv.read_bytes()).hexdigest()
    return csv


REASONS = {"sha256 is not": "sha", "its script is": "script", "dirty tree": "dirty", "not a clean run": "clean run",
           "its task is": "task", "not the whole search years": "span", "did not all hold": "identities",
           "its caps are not": "caps", "declared share": "share"}


def check_script() -> dict:
    from extended import results as XR

    start, end = "2021-01-04", "2021-06-30"
    bars = toy(start, end)
    src = fake_sources(bars)
    rec = Recorder(bars, days_table(bars))
    with tempfile.TemporaryDirectory() as tmp:
        q = q121_file(bars, Path(tmp) / "q121")
        out_dir = Path(tmp) / "out"
        out_dir.mkdir()
        t0 = time.time()
        rc_, out = run_main(rec, ["--start", start, "--end", end, "--results-dir", str(out_dir), "--q121", str(q)],
                            src)
        wall = time.time() - t0
        csv = out_dir / f"{S.RESULT}.csv"
        written = csv.is_file()
        ok, _ = XR.verify_result(csv) if written else (False, "")
        frame = pd.read_csv(csv, low_memory=False) if written else pd.DataFrame(columns=list(S.COLUMNS))
        licence = [str(f) for f in pl.scan_path(csv, name="results/s1_range.csv")] if written else ["not written"]
        man = json.loads(XR.manifest_path_for(csv).read_text(encoding="utf-8")) if written else {}
        reasons: set[str] = set()
        try:
            S.load_range(csv, caps=LS.stop_caps())
            reasons.add("loaded")
        except S.RangeRefused as exc:
            reasons = {v for k, v in REASONS.items() if k in str(exc)}
        dirty = bool(man.get("git_dirty"))
        listing = sorted(p.name for p in out_dir.iterdir())
    inside = all(S.SEARCH_START.isoformat() <= a <= b <= S.SEARCH_END.isoformat() for a, b in rec.spans)
    inside &= all(S.SEARCH_START.isoformat() <= w[2] <= w[3] <= S.SEARCH_END.isoformat() for w in rec.walk_reads)
    loader = sorted(reasons - {"dirty"})
    good = (rc_ == 0 and written and bool(ok) and S.output_problems(frame) == [] and licence == [] and inside
            and set(rec.purposes) == {S.PURPOSE} and set(rec.rows) == {S.READ_ROW}
            and ("dirty" in reasons) == dirty and "HELD" in out and "FAILED" not in out
            and man.get("seed") is None and listing == [f"{S.RESULT}.csv", f"{S.RESULT}.csv.manifest.json"])
    return {"ok": good, "exit": rc_, "stdout": out[-2000:], "verified": bool(ok),
            "output_problems": S.output_problems(frame), "licence": licence, "reads": rec.reads,
            "reads_inside": inside, "purposes": sorted(set(map(str, rec.purposes))), "rows": sorted(set(map(str, rec.rows))),
            "loader_refusals": loader, "dirty": dirty, "wall_s": round(wall, 2), "days": int(bars["day"].nunique())}


def check_refuse() -> dict:
    bars = toy("2021-01-04", "2021-03-31")
    src = fake_sources(bars)
    table = days_table(bars)
    out: dict = {}
    os.environ.pop("S2X_CLEAN_RUN", None)
    with tempfile.TemporaryDirectory() as tmp:
        q = q121_file(bars, Path(tmp) / "q121")
        good_pin = Sc.Q121_SHA256
        span = ["--start", "2021-01-04", "--end", "2021-03-31"]
        for case, argv, want in (
                ("end_2024", ["--end", "2024-01-02", "--results-dir", tmp, "--q121", str(q)], 2),
                ("start_2024", ["--start", "2024-01-02", "--end", "2024-01-02", "--results-dir", tmp], 2),
                ("seal_day", ["--end", "2023-12-30", "--results-dir", tmp, "--q121", str(q)], 2),
                ("confirmation", ["--end", "2026-07-17", "--results-dir", tmp, "--q121", str(q)], 2),
                ("results_outside_clean_run", [*span, "--q121", str(q)], 2),
                ("q121_absent", [*span, "--results-dir", tmp, "--q121", str(Path(tmp) / "none.csv")], 2)):
            rec = Recorder(bars, table)
            rc_, s = run_main(rec, argv, src)
            out[case] = {"rc": rc_, "reads": rec.reads, "ok": rc_ == want and rec.reads == 0,
                         "said": s.strip().splitlines()[-1][:200] if s.strip() else ""}
        out["confirmation"]["ok"] &= "confirmation window" in out["confirmation"]["said"]
        Sc.Q121_SHA256 = "0" * 64
        rec = Recorder(bars, table)
        rc_, s = run_main(rec, [*span, "--results-dir", tmp, "--q121", str(q)], src)
        out["q121_off_pin"] = {"rc": rc_, "reads": rec.reads, "ok": rc_ == 2 and rec.reads == 0}
        Sc.Q121_SHA256 = good_pin
    with tempfile.TemporaryDirectory() as tmp:
        q = q121_file(bars, Path(tmp) / "q121", tamper=True)
        o = Path(tmp) / "out"
        o.mkdir()
        rec = Recorder(bars, table)
        rc_, s = run_main(rec, [*span, "--results-dir", str(o), "--q121", str(q)], src)
        out["q121_identity_fails"] = {"rc": rc_, "ok": rc_ == 4 and not any(o.iterdir()) and "q121" in s}
    with tempfile.TemporaryDirectory() as tmp:
        q = q121_file(bars, Path(tmp) / "q121")
        bad = table.copy()
        bad.loc[int(np.flatnonzero(bad["day_kind"].to_numpy() == "n")[0]), "day_kind"] = "e"
        o = Path(tmp) / "out"
        o.mkdir()
        rec = Recorder(bars, bad)
        rc_, s = run_main(rec, [*span, "--results-dir", str(o), "--q121", str(q)], src)
        out["a1_identity_fails"] = {"rc": rc_, "ok": rc_ == 4 and not any(o.iterdir()) and "a1_days" in s}
    return {"ok": all(v["ok"] for v in out.values()), "cases": out}


if __name__ == "__main__":
    check = sys.argv[1]
    t0 = time.time()
    res = {"shift": check_shift, "script": check_script, "refuse": check_refuse}[check]()
    res["seconds"] = round(time.time() - t0, 1)
    print(json.dumps(res, default=str))
