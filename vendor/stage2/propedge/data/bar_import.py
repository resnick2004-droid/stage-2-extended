"""Import a Databento 1-minute batch zip into the local bar store (R3, D-458), keeping only declared windows' days.

The zip is the operator's purchase as `docs/OPERATOR_SETUP.md` specifies it (`GLBX.MDP3`, `ohlcv-1m`, CSV with pretty
prices and timestamps, symbols mapped, parent symbology). The import, modelled on the Studio's
(`Stage 2C - Campaign Studio/studio/bars.py`, SD-09, SD-30):

* checks the CSV against the zip's own manifest hash and the schema in its metadata, or refuses the file;
* drops calendar spreads (symbols with "-"), refuses duplicate bars, prices off the tick and bars whose high and low
  do not bracket their open and close;
* assigns each bar to its trading day (Chicago time plus seven hours: a session opens at 17:00);
* **keeps only days inside the market's declared development, spent and confirmation windows** (`config/windows.yaml`);
  a day in a reserved window, or before the first window, is dropped and counted, never stored -- so the reserve is
  never on disk. Storing a confirmation window's days does not open them: the reader's guard refuses them to any read
  without a registration naming the window;
* keeps, for each trading day, the charted contract: the outright with the most volume on the previous trading day
  (the first day, its own), the kits' rule (D-98). The manifest's `leaders` holds the stored days' leaders only -- a
  dropped day's is used for the cut and never written (the NQ data report's F1) -- so a later file's first day chains
  from the last stored day, and a window opened later recomputes its days' leaders from its own file;
* replaces the days it carries and keeps the root's other days, so a later purchase joins an earlier one;
* records each stored day's first and last bar (Chicago time) beside `short_days`, with the days that start after the
  17:00 open (a purchase's seam, an outage) and those whose last bar starts before 15:00 (an early close), and each
  import's `condition.json` -- Databento's per-date availability inside the windows this market stores: the count by
  condition and the dates that are not "available" (a reserved date is neither counted nor named: D-458 (2)).
"""
from __future__ import annotations

import hashlib
import io
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from propedge.data.bars import COLUMNS, LICENCE, STORE, root_dir
from propedge.data.windows import WINDOWS_PATH, Window, windows_of

KEEP_STATUSES = ("development", "spent", "confirmation")
#: a stored day with fewer charted bars than this is listed in the manifest's `short_days` (a holiday session, or a
#: day a purchase's edge cut, e.g. 2025-06-30 between the two NQ files); readers decide what to do with it
SHORT_DAY_BARS = 1000
#: a session opens at 17:00 Chicago the evening before its trading day; a stored day whose first bar starts later is
#: listed in `late_start_days` (e.g. 2025-07-01, whose first two hours fell in the gap between the two NQ files)
SESSION_OPEN_CT = "17:00"
#: a stored day whose last bar starts before 15:00 Chicago is listed in `early_end_days` (an exchange early close, or a
#: day a purchase's edge cut, e.g. 2025-06-30's evening-only bars)
EARLY_END_CT = "15:00"
RAW = ["ts_event", "open", "high", "low", "close", "volume", "symbol"]
#: tick size by root (CME contract specifications; the micros share their root's tick)
TICK = {"NQ": 0.25, "ES": 0.25, "YM": 1.0, "RTY": 0.1, "CL": 0.01, "GC": 0.1}


class BarImportError(ValueError):
    """The file failed a check; nothing was stored."""


def _sha256_member(z: zipfile.ZipFile, name: str) -> str:
    h = hashlib.sha256()
    with z.open(name) as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def trading_day(ts_utc: pd.Series) -> pd.Series:
    """The trading day of each UTC timestamp: Chicago time plus seven hours, its date (a session opens at 17:00)."""
    return (ts_utc.dt.tz_convert("America/Chicago") + pd.Timedelta(hours=7)).dt.strftime("%Y-%m-%d")


def root_of(parent_symbol: str) -> str:
    return str(parent_symbol).split(".")[0].upper()


def _window_status(days: pd.Series, ws: tuple[Window, ...]) -> pd.Series:
    d = pd.to_datetime(days).dt.date
    status = pd.Series("outside", index=days.index, dtype=object)
    for w in ws:
        m = (d >= w.start) & ((d <= w.end) if w.end is not None else True)
        status[m] = w.status
    return status


def volume_leaders(df: pd.DataFrame) -> dict[str, str]:
    """Each trading day's outright with the most volume (ties to the first symbol)."""
    vol = df.groupby(["day", "contract"])["volume"].sum().reset_index()
    best = vol.sort_values(["day", "volume", "contract"], ascending=[True, False, True]).drop_duplicates("day")
    return dict(zip(best["day"], best["contract"]))


def charted_contracts(leaders: dict[str, str], days: list[str]) -> dict[str, str]:
    """Each of `days`' charted contract: the volume leader of the previous trading day in `leaders` (which may hold
    days from an earlier import); a day with no earlier day, its own leader (D-98)."""
    known = sorted(leaders)
    pos = {d: i for i, d in enumerate(known)}
    return {d: leaders[known[pos[d] - 1]] if pos[d] else leaders[d] for d in days}


def _session_minute(hhmm: str) -> int:
    """Minutes from the session's 17:00 Chicago open to the wall-clock time `hhmm` (a session is under a day long)."""
    h, m = (int(x) for x in hhmm.split(":"))
    o_h, o_m = (int(x) for x in SESSION_OPEN_CT.split(":"))
    return (h * 60 + m - o_h * 60 - o_m) % 1440


def day_bounds(df: pd.DataFrame) -> tuple[dict[str, list[str]], list[str], list[str]]:
    """Each day's first and last bar start, Chicago wall-clock "HH:MM"; the days whose first bar starts after the
    17:00 open; the days whose last bar starts before 15:00 (both read in session time, so a day whose bars end at
    18:59 the evening before -- 2025-06-30 -- ends early)."""
    g = df.groupby("day")["ts"].agg(["min", "max"])
    hhmm = {k: pd.to_datetime(g[k], unit="s", utc=True).dt.tz_convert("America/Chicago").dt.strftime("%H:%M").tolist()
            for k in ("min", "max")}
    days = [str(d) for d in g.index]
    early = _session_minute(EARLY_END_CT)
    bounds = {d: [a, b] for d, a, b in zip(days, hhmm["min"], hhmm["max"])}
    late_start = [d for d, a in zip(days, hhmm["min"]) if _session_minute(a) > 0]
    early_end = [d for d, b in zip(days, hhmm["max"]) if _session_minute(b) < early]
    return bounds, late_start, early_end


def condition_record(raw: Any, sha256: str, ws: tuple[Window, ...]) -> dict[str, Any]:
    """The import's `condition.json`: its sha256, and inside the windows this market stores (UTC dates, as Databento
    gives them) the count of dates by condition and the dates whose condition is not "available". A date in a reserved
    window, or outside every window, is neither counted nor named: what the reserve's data looks like is not on disk
    (D-458 (2); the data-integrity report's F3, 2026-10-30)."""
    if not isinstance(raw, list) or not all(isinstance(e, dict) and "date" in e and "condition" in e for e in raw):
        raise BarImportError("condition.json is not Databento's per-date list of {date, condition}")
    entries = sorted((str(e["date"]), str(e["condition"])) for e in raw)
    if entries:
        keep = _window_status(pd.Series([d for d, _ in entries]), ws).isin(KEEP_STATUSES).tolist()
        entries = [e for e, k in zip(entries, keep) if k]
    counts: dict[str, int] = {}
    for _, c in entries:
        counts[c] = counts.get(c, 0) + 1
    named = {d: c for d, c in entries if c != "available"}
    return {"sha256": sha256, "counts": dict(sorted(counts.items())), "not_available": named}


def import_zip(src: Path | str, *, store: Path | None = None, windows: Path | str = WINDOWS_PATH) -> dict[str, Any]:
    """Import one zip; returns the root's new manifest. Refuses the whole file on any failed check."""
    src = Path(src)
    if not src.is_file():
        raise BarImportError(f"no file at {src}")
    with zipfile.ZipFile(src) as z:
        names = z.namelist()
        csvs = [n for n in names if n.endswith(".csv")]
        if len(csvs) != 1 or "manifest.json" not in names or "metadata.json" not in names:
            raise BarImportError("expected a Databento batch zip: one CSV, manifest.json and metadata.json")
        csv_name = csvs[0]
        meta = json.loads(z.read("metadata.json"))
        listed = {f["filename"]: f.get("hash", "") for f in json.loads(z.read("manifest.json")).get("files", [])}
        want = str(listed.get(csv_name, "")).removeprefix("sha256:")
        got = _sha256_member(z, csv_name)
        if not want or want != got:
            raise BarImportError(f"{csv_name}: sha256 {got} does not match the zip's manifest ({want or 'none listed'})")
        cond_raw, cond_sha = None, None                         # a zip without condition.json records null
        if "condition.json" in names:
            cond_sha = _sha256_member(z, "condition.json")
            want_c = str(listed.get("condition.json", "")).removeprefix("sha256:")
            if want_c and want_c != cond_sha:
                raise BarImportError(f"condition.json: sha256 {cond_sha} does not match the zip's manifest ({want_c})")
            try:
                cond_raw = json.loads(z.read("condition.json"))
            except ValueError as exc:
                raise BarImportError(f"condition.json is not JSON: {exc}") from exc
        q = meta.get("query", {})
        if q.get("schema") != "ohlcv-1m":
            raise BarImportError(f"expected 1-minute OHLCV bars (schema ohlcv-1m), got {q.get('schema')!r}")
        root = root_of((q.get("symbols") or ["?"])[0])
        ws = windows_of(root, windows)                         # raises when the market has no declared windows
        cond = condition_record(cond_raw, str(cond_sha), ws) if cond_raw is not None else None
        tick = TICK.get(root)
        if tick is None:
            raise BarImportError(f"{root}: no tick size declared in propedge.data.bar_import.TICK")
        parts, n_rows, n_spread = [], 0, 0
        with z.open(csv_name) as f:
            for chunk in pd.read_csv(io.TextIOWrapper(f, encoding="utf-8"), usecols=RAW, chunksize=500_000):
                n_rows += len(chunk)
                spread = chunk["symbol"].astype(str).str.contains("-", regex=False)
                n_spread += int(spread.sum())
                parts.append(chunk[~spread])
    df = pd.concat(parts, ignore_index=True).rename(columns={"symbol": "contract"})
    ts = pd.to_datetime(df["ts_event"], utc=True)
    if ((ts.dt.second != 0) | (ts.dt.microsecond != 0)).any():
        raise BarImportError("a bar's timestamp is not a whole minute")
    df["ts"] = ts.dt.as_unit("s").astype("int64")
    df["day"] = trading_day(ts)
    if df.duplicated(["ts", "contract"]).any():
        raise BarImportError("a contract has two bars in one minute")
    px = df[["open", "high", "low", "close"]].to_numpy(float)
    if not np.allclose(np.round(px / tick) * tick, px, rtol=0.0, atol=1e-9):     # no relative slack at ~20,000
        raise BarImportError(f"a price is off the {tick} tick")
    if ((df["high"] < df[["open", "close"]].max(axis=1)) | (df["low"] > df[["open", "close"]].min(axis=1))).any():
        raise BarImportError("a bar's high and low do not bracket their open and close")
    # the charted contract: the previous trading day's volume leader, an earlier import's (stored) days included and
    # this file's dropped days too (a dropped day's leader may chart the stored day after it, and is never written)
    out = root_dir(root, store)
    prev = json.loads((out / "manifest.json").read_text(encoding="utf-8")) if (out / "manifest.json").is_file() else {}
    leaders = {**dict(prev.get("leaders") or {}), **volume_leaders(df)}
    charted = charted_contracts(leaders, sorted(df["day"].unique().tolist()))
    df = df[df["contract"].to_numpy() == df["day"].map(charted).to_numpy()]
    status = _window_status(df["day"], ws)
    keep = status.isin(KEEP_STATUSES)
    dropped = {str(k): int(v) for k, v in status[~keep].value_counts().items()}
    dropped_days = sorted(df.loc[~keep, "day"].unique().tolist())
    df = df[keep][COLUMNS].reset_index(drop=True)
    if df.empty:
        raise BarImportError("no day of the file lies in a window this market may store")
    out.mkdir(parents=True, exist_ok=True)
    pq = out / "bars.parquet"
    if pq.is_file():
        old = pd.read_parquet(pq)
        old = old[~old["day"].isin(set(df["day"]))]
        df = pd.concat([old, df], ignore_index=True)
    df = df.sort_values(["ts"], kind="stable").reset_index(drop=True)
    tmp = out / "bars.parquet.tmp"
    df.to_parquet(tmp, index=False)
    tmp.replace(pq)
    days = sorted(df["day"].unique().tolist())
    by_day = df.groupby("day")["contract"].first()
    per_day = df.groupby("day").size()
    short = {str(d): int(n) for d, n in per_day.items() if n < SHORT_DAY_BARS}
    bounds, late_start, early_end = day_bounds(df)
    rolls = [d for i, d in enumerate(days) if i and by_day[d] != by_day[days[i - 1]]]
    this = {"source": src.name, "source_bytes": src.stat().st_size, "csv": csv_name, "csv_sha256": got, "query": q,
            "rows_read": n_rows, "spread_rows_dropped": n_spread, "charted_bars_dropped_by_window": dropped,
            "days_dropped_by_window": len(dropped_days),
            "first_dropped_day": dropped_days[0] if dropped_days else None, "condition": cond,
            "imported": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    imports = [m for m in prev.get("imports", []) if m.get("csv_sha256") != got] + [this]
    man = {"decision": "D-458", "root": root, "licence": LICENCE, "tick": tick,
           "windows": [{"name": w.name, "status": w.status, "start": str(w.start), "end": str(w.end) if w.end else None}
                       for w in ws],
           "stored_statuses": list(KEEP_STATUSES), "days": len(days), "first_day": days[0], "last_day": days[-1],
           "contracts": sorted(df["contract"].unique().tolist()), "rolls": rolls, "rows": int(len(df)),
           "short_days": short, "late_start_days": late_start, "early_end_days": early_end, "day_bounds": bounds,
           "parquet_sha256": hashlib.sha256(pq.read_bytes()).hexdigest(), "day_list": days,
           # the stored days' leaders only: a dropped (reserved or outside) day's leader is never written
           "leaders": {d: leaders[d] for d in days if d in leaders}, "imports": imports}
    (out / "manifest.json").write_text(json.dumps(man, indent=1, default=str) + "\n", encoding="utf-8")
    return man
