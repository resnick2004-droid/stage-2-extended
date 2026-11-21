"""The child process of `tests/test_t7_forecast.py` (T7): `scripts/t7_fit.py`'s `main` on synthetic bars only
(`extended/synthetic_bars.py`). Never reads the bar store: the script's reader calls are stood in by recorders
returning the toys and a toy A1 day table, and the void calendar by a synthetic one (every overnight clean, the toys'
own last bars). `extended.results` puts the vendored tree on the path, so this runs in a process of its own.

    python tests/t7_synthetic.py script|refuse

Prints one JSON line last. Seeds (named by role, outside the 2026xxxx range): `SEED_TOY_BARS` 4735 (the toys' bars).
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd  # noqa: E402

from extended import day_calendar as DC  # noqa: E402
from extended import price_levels as pl  # noqa: E402
from extended import reader as R  # noqa: E402
from extended import synthetic_bars as SB  # noqa: E402
from extended import t7_forecast as T  # noqa: E402

SEED_TOY_BARS = 4735
SPANS = (("2021-01-04", "2021-04-30"), ("2022-01-03", "2022-04-29"))
NOT_WALKED = ("2021-02-03", "2022-03-16")              # two toy days given a kind outside the frame ('f')

_spec = importlib.util.spec_from_file_location("t7_fit_script", ROOT / "scripts" / "t7_fit.py")
Sc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(Sc)


def toys() -> pd.DataFrame:
    return pd.concat([SB.generate(SB.Spec(start=date.fromisoformat(a), end=date.fromisoformat(b),
                                          seed=SEED_TOY_BARS)) for a, b in SPANS], ignore_index=True)


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
    days = sorted(bars["day"].astype(str).unique())
    return pd.DataFrame({"date": days, "day_kind": ["f" if d in NOT_WALKED else "n" for d in days]})


class Recorder:
    def __init__(self, bars: pd.DataFrame, table: pd.DataFrame):
        self.bars, self.table = bars, table
        self.spans, self.purposes, self.rows, self.walk_reads = [], [], [], 0

    def read_bars(self, start, end, *, purpose=None, declaration=None, columns=None, what="", **kw):
        self.spans.append([str(start), str(end)])
        self.purposes.append(purpose)
        self.rows.append(declaration)
        b = self.bars[(self.bars["day"] >= str(start)) & (self.bars["day"] <= str(end))]
        return b[columns].reset_index(drop=True) if columns else b.reset_index(drop=True)

    def read_walks(self, family, table, start, end, *, columns=None, what="", **kw):
        self.spans.append([str(start), str(end)])
        self.walk_reads += 1
        t = self.table[(self.table["date"] >= str(start)) & (self.table["date"] <= str(end))]
        return t[columns].reset_index(drop=True) if columns else t.reset_index(drop=True)


def run_main(rec: Recorder, argv: list[str], src: DC.Sources) -> tuple[int, str]:
    R.read_bars, R.read_walks = rec.read_bars, rec.read_walks
    Sc.reader.read_bars, Sc.reader.read_walks = rec.read_bars, rec.read_walks
    Sc.load_sources = lambda: src
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc_ = Sc.main(argv)
    return rc_, buf.getvalue()


def _inside(spans: list[list[str]]) -> bool:
    return all(T.SEARCH_START.isoformat() <= a <= b <= T.SEARCH_END.isoformat() for a, b in spans)


def check_script() -> dict:
    from extended import results as XR

    bars = toys()
    rec = Recorder(bars, days_table(bars))
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        rc_, log = run_main(rec, ["--start", SPANS[0][0], "--end", SPANS[1][1], "--results-dir", str(out)],
                            fake_sources(bars))
        csv_path = out / f"{T.RESULT}.csv"
        got: dict = {"exit": rc_, "log": log[-1500:], "reads": len(rec.spans), "reads_inside": _inside(rec.spans),
                     "purposes": sorted(set(rec.purposes)), "rows": sorted(set(rec.rows)),
                     "identities": [ln.strip() for ln in log.splitlines() if "identity" in ln]}
        if rc_ != 0 or not csv_path.is_file():
            got["ok"] = False
            return got
        ok_v, _ = XR.verify_result(csv_path)
        frame = pd.read_csv(csv_path, keep_default_na=False)
        got["verified"] = bool(ok_v)
        got["output_problems"] = T.output_problems(pd.read_csv(csv_path))
        got["licence"] = [f.rule for f in pl.scan_path(csv_path, name="results/t7_forecast.csv")]
        got["identities_held"] = all("HELD" in ln for ln in got["identities"]) and len(got["identities"]) == 2
        refusals = []
        try:
            T.load_forecast(csv_path, q=T.admission_line()[0])
        except T.ForecastRefused as exc:
            msg = str(exc)
            refusals += [k for k, w in (("clean run", "clean run"), ("span", "whole search years"),
                                        ("sha", "sha256"), ("identity", "identities"), ("q", "q is not")) if w in msg]
        got["loader_refusals"] = refusals
        got["frame_rows"] = len(frame)
    got["ok"] = (got["exit"] == 0 and got["verified"] and got["identities_held"] and got["reads_inside"]
                 and rec.walk_reads == 1)
    return got


def check_refuse() -> dict:
    bars = toys()
    src = fake_sources(bars)
    res: dict = {}
    with tempfile.TemporaryDirectory() as tmp:
        for name, end in (("held_out", "2024-01-02"), ("confirmation", "2026-07-17")):
            rec = Recorder(bars, days_table(bars))
            rc_, log = run_main(rec, ["--end", end, "--results-dir", str(Path(tmp) / name)], src)
            res[name] = {"exit": rc_, "reads": len(rec.spans), "refused": "REFUSED" in log}
        rec = Recorder(bars, days_table(bars))
        rc_, log = run_main(rec, ["--start", SPANS[0][0], "--end", SPANS[1][1]], src)
        res["results_dir"] = {"exit": rc_, "reads": len(rec.spans), "refused": "REFUSED" in log}
        short = days_table(bars).iloc[5:]                   # A1's table missing five toy days: a1_days fails
        rec = Recorder(bars, short)
        out = Path(tmp) / "a1"
        rc_, log = run_main(rec, ["--start", SPANS[0][0], "--end", SPANS[1][1], "--results-dir", str(out)], src)
        res["a1_identity"] = {"exit": rc_, "written": out.exists() and any(out.iterdir()),
                              "failed": "identity a1_days" in log and "FAILED" in log}
    ok = (all(res[k]["exit"] == 2 and res[k]["reads"] == 0 and res[k]["refused"]
              for k in ("held_out", "confirmation", "results_dir"))
          and res["a1_identity"]["exit"] == 4 and not res["a1_identity"]["written"] and res["a1_identity"]["failed"])
    return {"ok": ok, **res}


if __name__ == "__main__":
    which = sys.argv[1]
    out = {"script": check_script, "refuse": check_refuse}[which]()
    print(json.dumps(out, default=str))
