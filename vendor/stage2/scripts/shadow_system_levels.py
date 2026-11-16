"""The shadow period's system levels from data (R8; `prereg/DRAFT_shadow_fv3c.md` §6a and §8 item 5): missing minutes.

    python scripts/shadow_system_levels.py [--store PATH]

What it measures. For every normal trading day of NQ's development windows (`config/windows.yaml`: 2020-01-01 to
2026-07-16, the held-back year folded into development by D-461) in the operator's licensed Databento one-minute bars
(the local store, kept out of version control; `--store` names it when run from a worktree, whose own `data/bars` is
empty), read a year at a time through `propedge.data.bars.read_bars` with purpose "development", and for each window:

* ``missing``: the minutes in the window with no bar. Databento's ``ohlcv-1m`` writes a bar only for a minute with at
  least one trade in the charted outright, so a missing minute is a minute without a trade print -- the market's own
  quiet, not a fault: the historical file is the exchange's full trade record.
* ``longest_run``: the longest run of consecutive minutes with no bar. A run of k minutes means the longest silence
  between two trade prints there was at least k minutes and under k + 2.
* ``missing_interior`` (``rth`` only): the minutes with no bar between the window's first and last bar, the count the
  execution terminal's R2 reading makes (`terminal_core.pilot_board.missing_minutes`).

The windows (Chicago time; a bar named by its start; the evening windows on the calendar day before the trading day):
``eve`` 17:00-18:30, ``asia`` 19:00-20:30 and ``ny`` 08:30-10:00 -- FV3-C's three signal windows (its card's Entry,
`docs/candidates/cards/FV3-C.md`); ``signal``, the three together (its longest run the longest within any one);
``rth`` 08:30-15:10 -- the window the draft's R1 names and the terminal's R2 reads (bars closing after 08:30 and by
15:10); ``session`` 17:00-15:10 -- the card's trading window to the firm's flatten, when a position may be open.

Left out, and counted (section ``excluded``): a day whose last bar ends before 15:00 CT (a holiday or an early close:
an hour or more before the normal 16:00 close); a day whose first bar starts an hour or more after the session's 17:00
CT open (a late open -- the same hour on the other side; added after the first run's tail showed trading day
2020-07-01 opening at 19:00 CT in the file, which made the evening window's largest day the whole window, so a
FAIL-SYSTEM above it could never fire; it removes that day alone); and a window the store's imports do not cover in
full (the two Databento files leave 2025-06-30 00:00 to 2025-07-01 00:00 UTC unrequested: trading day 2025-06-30 and
the evening of 2025-07-01).

The levels proposed (section ``level``): a FLAG for a session whose count is above the development's p99 day (nearest
rank: an observed day; at most 1 % of development days are above it), and a FAIL-SYSTEM for one above the development's
largest normal day (a count the market itself never produced on a normal day in the span). Beside each, how often it
would fire on development-like days in a period of `PERIOD_SESSIONS` sessions (the protocol's minimum length): the FLAG
from the share of development days above it, the FAIL-SYSTEM from the exchangeable bound -- a new day exceeds the
largest of n with probability at most 1 / (n + 1). Section ``bars_off_minute``: the development bars whose start is not
on a whole minute (R4's "a bar off its exchange minute"). Section ``tail``: the days above each FLAG, by date, with
their counts, so the tail can be read for exchange events (halts, limit locks).

Writes `results/shadow_system_levels.csv` with its manifest. No bar, price or per-minute row is written (the vendor's
licence: private use, no redistribution; `tests/test_no_raw_bars_in_results.py`): per-day counts only. Deterministic --
nothing is drawn, so no seed. EXPLORATORY: levels proposed for a pre-registration, read on development data the trial
ledger already counts; nothing here is a model test.
"""
from __future__ import annotations

import argparse
import math
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from propedge.data.bars import STORE, manifest as store_manifest, read_bars  # noqa: E402
from propedge.reporting.results import write_result  # noqa: E402

SCRIPT = "scripts/shadow_system_levels.py"
RESULT = "shadow_system_levels"
MARKET = "NQ"
START, END = "2020-01-01", "2026-07-16"      # NQ's development windows (config/windows.yaml, D-459, D-461)
CT = "America/Chicago"
NORMAL_CLOSE = (15, 0)                         # a day whose last bar ends before 15:00 CT is a holiday or early close
SESSION_OPEN = (17, 0)                         # the session's open, the evening before
LATE_OPEN_S = 3600                             # a first bar an hour or more after the open is a late open
PERIOD_SESSIONS = 60                           # the shadow period's minimum length (protocol §3; D-337)
FLAG_Q = 99.0                                  # the FLAG: above the development's p99 day
QUANTILES = (50.0, 90.0, 95.0, 99.0, 99.9)

#: name: (start (h, m), end (h, m), the start on the evening before, the end on the evening before)
WINDOWS: dict[str, tuple[tuple[int, int], tuple[int, int], bool, bool]] = {
    "eve": ((17, 0), (18, 30), True, True),
    "asia": ((19, 0), (20, 30), True, True),
    "ny": ((8, 30), (10, 0), False, False),
    "rth": ((8, 30), (15, 10), False, False),
    "session": ((17, 0), (15, 10), True, False),
}
SIGNAL = ("eve", "asia", "ny")
ORDER = ("eve", "asia", "ny", "signal", "rth", "session")


def nearest_rank(values: np.ndarray, q: float) -> float:
    """The nearest-rank percentile (q in 0-100): an observed value, the smallest with at least q % of values at or
    below it -- the terminal's own rule (`terminal_core.pilot_board.nearest_rank`)."""
    s = np.sort(np.asarray(values, dtype=float))
    return float(s[max(0, math.ceil(q / 100.0 * len(s)) - 1)])


def _epoch(d: date, hm: tuple[int, int]) -> int:
    return int(pd.Timestamp(d.year, d.month, d.day, hm[0], hm[1], tz=CT).tz_convert("UTC").timestamp())


def window_bounds(day: date, name: str) -> tuple[int, int]:
    """The window's [start, end) in epoch seconds UTC for trading day `day` (DST by the zone)."""
    s_hm, e_hm, s_eve, e_eve = WINDOWS[name]
    prev = day - timedelta(days=1)
    return _epoch(prev if s_eve else day, s_hm), _epoch(prev if e_eve else day, e_hm)


def longest_run(absent: np.ndarray) -> int:
    """The longest run of True in a boolean array."""
    if not absent.any():
        return 0
    padded = np.concatenate(([0], absent.astype(np.int8), [0]))
    d = np.diff(padded)
    return int((np.flatnonzero(d == -1) - np.flatnonzero(d == 1)).max())


def window_counts(ts: np.ndarray, lo: int, hi: int, interior: bool = False) -> dict[str, int]:
    """The window's minutes, the minutes with no bar and their longest run (and, with `interior`, the minutes with no
    bar between the window's first and last bar)."""
    grid = np.arange(lo, hi, 60, dtype=np.int64)
    present = np.isin(grid, ts)
    out = {"minutes": int(len(grid)), "missing": int((~present).sum()), "longest_run": longest_run(~present)}
    if interior:
        idx = np.flatnonzero(present)
        out["missing_interior"] = int((~present[idx[0]: idx[-1] + 1]).sum()) if len(idx) else -1
    return out


def coverage(man: dict) -> list[tuple[int, int]]:
    """The store's imported spans, [start, end) in epoch seconds, from each import's Databento query."""
    return [(int(i["query"]["start"]) // 10**9, int(i["query"]["end"]) // 10**9) for i in man.get("imports", [])]


def covered(spans: list[tuple[int, int]], lo: int, hi: int) -> bool:
    return any(s <= lo and hi <= e for s, e in spans)


def measure(store: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Per-day counts for every window, the excluded days and windows, and the bars-off-minute tally."""
    man = store_manifest(MARKET, store)
    if man is None:
        raise SystemExit(f"no bar store manifest for {MARKET} under {store}")
    spans = coverage(man)
    rows, excluded = [], []
    off_minute, bars_read, days_read = 0, 0, 0
    first, last = date.fromisoformat(START), date.fromisoformat(END)
    for year in range(first.year, last.year + 1):
        lo_d, hi_d = max(first, date(year, 1, 1)), min(last, date(year, 12, 31))
        df = read_bars(MARKET, lo_d.isoformat(), hi_d.isoformat(), purpose="development", store=store,
                       what="shadow system levels (missing minutes)")[["ts", "day"]]
        bars_read += len(df)
        off_minute += int((df["ts"].to_numpy() % 60 != 0).sum())
        for day_s, g in df.groupby("day", sort=True):
            days_read += 1
            day = date.fromisoformat(str(day_s))
            ts = np.sort(g["ts"].to_numpy(dtype=np.int64))
            last_end = int(ts[-1]) + 60
            if last_end < _epoch(day, NORMAL_CLOSE):
                s_lo, s_hi = window_bounds(day, "session")
                reason = "import coverage" if not covered(spans, s_lo, s_hi) else "holiday or early close"
                excluded.append({"day": day_s, "window": "day", "reason": reason,
                                 "last_bar_end_ct": pd.Timestamp(last_end, unit="s", tz="UTC").tz_convert(CT)
                                 .strftime("%Y-%m-%d %H:%M")})
                continue
            s_lo, s_hi = window_bounds(day, "session")
            if int(ts[0]) >= s_lo + LATE_OPEN_S and covered(spans, s_lo, s_hi):
                excluded.append({"day": day_s, "window": "day", "reason": "late open",
                                 "last_bar_end_ct": ""})
                continue
            rec: dict[str, object] = {"day": day_s}
            for name in WINDOWS:
                lo, hi = window_bounds(day, name)
                if not covered(spans, lo, hi):
                    excluded.append({"day": day_s, "window": name, "reason": "import coverage",
                                     "last_bar_end_ct": ""})
                    continue
                c = window_counts(ts, lo, hi, interior=(name == "rth"))
                for k, v in c.items():
                    rec[f"{name}_{k}"] = v
            if all(f"{w}_missing" in rec for w in SIGNAL):
                rec["signal_minutes"] = sum(int(rec[f"{w}_minutes"]) for w in SIGNAL)
                rec["signal_missing"] = sum(int(rec[f"{w}_missing"]) for w in SIGNAL)
                rec["signal_longest_run"] = max(int(rec[f"{w}_longest_run"]) for w in SIGNAL)
            rows.append(rec)
        del df
    tally = {"bars_read": bars_read, "bars_off_minute": off_minute, "store_days_read": days_read}
    return pd.DataFrame(rows), pd.DataFrame(excluded), tally


def summarise(per_day: pd.DataFrame, excluded: pd.DataFrame, tally: dict) -> pd.DataFrame:
    """The long-format result: distributions, levels, the tail days, the off-minute tally and the exclusions."""
    out: list[dict] = []
    for w in ORDER:
        measures = ["missing", "longest_run"] + (["missing_interior"] if w == "rth" else [])
        for m in measures:
            col = f"{w}_{m}"
            if col not in per_day:
                continue
            sub = per_day[["day", col]].dropna()
            v = sub[col].to_numpy(dtype=float)
            n = len(v)
            base = {"window": w, "measure": m, "n_days": n}
            out.append({"section": "dist", **base, "stat": "minutes_in_window",
                        "value": float(per_day[f"{w}_minutes"].dropna().median())})
            out.append({"section": "dist", **base, "stat": "share_days_zero", "value": float((v == 0).mean())})
            out.append({"section": "dist", **base, "stat": "mean", "value": float(v.mean())})
            for q in QUANTILES:
                out.append({"section": "dist", **base, "stat": f"p{q:g}".replace(".", "_"),
                            "value": nearest_rank(v, q)})
            mx = float(v.max())
            out.append({"section": "dist", **base, "stat": "max", "value": mx})
            if m == "missing_interior":
                continue
            flag = nearest_rank(v, FLAG_Q)
            share_above = float((v > flag).mean())
            p_flag = 1.0 - (1.0 - share_above) ** PERIOD_SESSIONS
            p_fail = 1.0 - (1.0 - 1.0 / (n + 1)) ** PERIOD_SESSIONS
            out += [
                {"section": "level", **base, "stat": "flag_above", "value": flag,
                 "rule": f"FLAG: the session's {m} in {w} above the development's p{FLAG_Q:g} day (nearest rank)"},
                {"section": "level", **base, "stat": "flag_share_dev_days_above", "value": share_above,
                 "rule": "the share of development days above the FLAG level"},
                {"section": "level", **base, "stat": "flag_p_any_in_period", "value": p_flag,
                 "rule": f"the chance of at least one FLAG in {PERIOD_SESSIONS} development-like sessions"},
                {"section": "level", **base, "stat": "fail_system_above", "value": mx,
                 "rule": f"FAIL-SYSTEM: the session's {m} in {w} above the development's largest normal day"},
                {"section": "level", **base, "stat": "fail_p_any_in_period_bound", "value": p_fail,
                 "rule": f"at most this chance of a FAIL-SYSTEM in {PERIOD_SESSIONS} development-like sessions "
                         "(a new day exceeds the largest of n with probability at most 1/(n+1))"},
            ]
            tail = sub[sub[col] > flag].sort_values([col, "day"], ascending=[False, True])
            for r in tail.itertuples(index=False):
                out.append({"section": "tail", **base, "stat": "day_above_flag", "value": float(getattr(r, col)),
                            "day": r.day})
    out.append({"section": "bars_off_minute", "window": "all", "measure": "bars", "stat": "bars_read",
                "value": float(tally["bars_read"])})
    out.append({"section": "bars_off_minute", "window": "all", "measure": "bars", "stat": "bars_off_minute",
                "value": float(tally["bars_off_minute"])})
    out.append({"section": "days", "window": "all", "measure": "days", "stat": "store_days_read",
                "value": float(tally["store_days_read"])})
    out.append({"section": "days", "window": "all", "measure": "days", "stat": "normal_days",
                "value": float(len(per_day))})
    for r in excluded.itertuples(index=False):
        out.append({"section": "excluded", "window": r.window, "measure": "", "stat": r.reason, "value": float("nan"),
                    "day": r.day, "rule": f"last bar ends {r.last_bar_end_ct} CT" if r.last_bar_end_ct else
                    ("first bar an hour or more after the 17:00 CT open" if r.reason == "late open" else "")})
    cols = ["section", "window", "measure", "stat", "value", "n_days", "day", "rule"]
    return pd.DataFrame(out).reindex(columns=cols)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--store", default=str(STORE), help="the bar store's folder (data/bars of the main checkout)")
    args = ap.parse_args(argv)
    store = Path(args.store)
    per_day, excluded, tally = measure(store)
    out = summarise(per_day, excluded, tally)
    man = store_manifest(MARKET, store) or {}
    write_result(out, RESULT, script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 parameters={"market": MARKET, "span": [START, END], "purpose": "development",
                             "store_parquet_sha256": man.get("parquet_sha256"),
                             "store_imports": [{"csv": i.get("csv"), "csv_sha256": i.get("csv_sha256")}
                                               for i in man.get("imports", [])],
                             "windows_ct": {k: [f"{v[0][0]:02d}:{v[0][1]:02d}", f"{v[1][0]:02d}:{v[1][1]:02d}",
                                                "evening before" if v[2] else "trading day"]
                                            for k, v in WINDOWS.items()},
                             "signal": list(SIGNAL), "normal_close_ct": "15:00", "late_open_after_ct": "18:00", "flag_q": FLAG_Q,
                             "fail_system": "above the largest normal development day",
                             "period_sessions": PERIOD_SESSIONS, "percentile": "nearest rank"},
                 description="The shadow period's R2 levels (and R1's market-silence reading, R4's bars-off-minute) "
                             "from the development's own minute bars: per normal trading day, the minutes without a bar "
                             "and the longest run of them in FV3-C's signal windows, the 08:30-15:10 window and the "
                             "session; their distribution, the FLAG at the p99 day and the FAIL-SYSTEM above the "
                             "largest normal day. Counts only; no bar or price is written. Deterministic: no seed.",
                 notes={"status": "EXPLORATORY: levels proposed for the shadow period's pre-registration (R8); "
                                  "the live feed is not Databento's historical file, so the levels are the market's "
                                  "own quiet, read again against the live-built bars in the burn-in (the draft's §6a)",
                        "post_hoc": "the late-open rule was added after the first run's tail (trading day 2020-07-01 "
                                    "opened at 19:00 CT in the file); it removes that day alone"})
    lv = out[out.section == "level"]
    print(f"wrote results/{RESULT}.csv ({len(out)} rows); normal days {len(per_day)}; "
          f"excluded rows {len(excluded)}; bars off minute {tally['bars_off_minute']} of {tally['bars_read']}")
    for w in ORDER:
        for m in ("missing", "longest_run"):
            f = lv[(lv.window == w) & (lv.measure == m)]
            if len(f):
                g = dict(zip(f.stat, f.value))
                print(f"  {w:8s} {m:12s} FLAG>{g['flag_above']:g} (dev days above "
                      f"{g['flag_share_dev_days_above']:.4f}) FAIL>{g['fail_system_above']:g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
