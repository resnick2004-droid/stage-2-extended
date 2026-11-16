"""EXPLORATORY (D-386 (7)): the clock check across daylight-saving changes, by the rule fixed in config/dst_check.yaml
before its data was read.

    python scripts/score_dst_check.py           # reads results/manual_R146_dst_NQ.csv

Each release day's three bars -- for a BLS 08:30 ET release the bars starting 06:30, 07:30 and 08:30 CT, for a
scheduled FOMC statement at 2:00 PM ET those starting 12:00, 13:00 and 14:00 CT -- read as ratios of their range to the
median range of the same bar on the year's days without a release (BLS or FOMC). A day with a ratio of at least the
declared spike ratio at any of its three bars has a spike; its peak is the bar of the largest ratio. **It holds** when
on every release day within seven calendar days of a US daylight-saving change that has a spike, the peak is the
release's own bar (07:30 or 13:00 CT); a peak an hour away is the error the check looks for. Release days away from the
changes are reported beside as the control. Writes results/dst_check_nq.csv with its manifest.
"""
from __future__ import annotations

import argparse
import io
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

SCRIPT = "scripts/score_dst_check.py"
CONFIG = ROOT / "config" / "dst_check.yaml"
RUN = "R146-dst-NQ"
TRIPLES = {"bls": (("06:30", "07:30", "08:30"), "07:30"), "fomc": (("12:00", "13:00", "14:00"), "13:00")}


def col(label: str) -> str:
    return "r_" + label.replace(":", "")


def changes(years) -> list[date]:
    """The US daylight-saving changes: the second Sunday of March and the first Sunday of November."""
    out = []
    for y in years:
        mar = date(y, 3, 1)
        out.append(mar + timedelta(days=(6 - mar.weekday()) % 7 + 7))
        nov = date(y, 11, 1)
        out.append(nov + timedelta(days=(6 - nov.weekday()) % 7))
    return sorted(out)


def release_days(cfg: dict) -> dict[str, str]:
    """{date: 'bls' | 'fomc'} -- BLS's 08:30 ET days and the FOMC's scheduled 2:00 PM ET statements (a day with both is
    read as each, the FOMC entry under its own key)."""
    out: dict[str, str] = {}
    bls = pd.read_csv(ROOT / cfg["releases"]["bls"])
    for d in bls["date"].astype(str):
        out[d] = "bls"
    for rel in cfg["releases"]["fomc"]:
        lines = [ln for ln in (ROOT / rel).read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
        t = pd.read_csv(io.StringIO("\n".join(lines)))
        if "code" in t.columns:
            t = t[(t["code"] == "FOMC") & (t["time_et"].astype(str) == "14:00")]
        elif "release_line" in t.columns:
            t = t[t["release_line"].astype(str).str.contains("2:00 p.m.", regex=False)]
        for d in t["date"].astype(str):
            out[d + "#fomc"] = "fomc"
    return out


def score(df: pd.DataFrame, cfg: dict, releases: dict[str, str]) -> pd.DataFrame:
    ratio_min, near = float(cfg["spike_ratio"]), int(cfg["near_change_days"])
    days = df.copy()
    days["date"] = days["date"].astype(str)
    plain = {k.split("#")[0] for k in releases}
    base = days[~days["date"].isin(plain)]
    med = {(int(y), c): float(g[c].median()) for y, g in base.groupby("year") for c in [col(x) for x in cfg["bars_start_ct"]]}
    ch = changes(sorted({int(y) for y in days["year"]}))
    by_date = days.set_index("date")
    rows = []
    for key, kind in sorted(releases.items()):
        d = key.split("#")[0]
        if d not in by_date.index:
            continue
        r = by_date.loc[d]
        trio, own = TRIPLES[kind]
        ratios = {}
        for lab in trio:
            m = med.get((int(r["year"]), col(lab)), float("nan"))
            v = r[col(lab)]
            ratios[lab] = float(v) / m if (pd.notna(v) and m and np.isfinite(m) and m > 0) else float("nan")
        dd = date.fromisoformat(d)
        gap = min(abs((dd - c).days) for c in ch)
        finite = {k: v for k, v in ratios.items() if np.isfinite(v)}
        peak = max(finite, key=finite.get) if finite else None
        spike = bool(finite) and max(finite.values()) >= ratio_min
        rows.append({"section": "day", "date": d, "kind": kind, "days_to_change": int(gap), "near_change": gap <= near,
                     **{f"ratio_{lab.replace(':', '')}": ratios[lab] for lab in trio}, "release_bar": own,
                     "peak_bar": peak, "spike": spike, "at_release": bool(spike and peak == own),
                     "an_hour_off": bool(spike and peak is not None and peak != own)})
    d = pd.DataFrame(rows)
    out = [d]
    summ = []
    for (kind, nr), g in d.groupby(["kind", "near_change"]):
        sp = g[g["spike"]]
        summ.append({"section": "summary", "kind": kind, "near_change": bool(nr), "days": int(len(g)),
                     "spikes": int(len(sp)), "at_release": int(sp["at_release"].sum()),
                     "an_hour_off": int(sp["an_hour_off"].sum()), "quiet": int((~g["spike"]).sum())})
    out.append(pd.DataFrame(summ))
    near_sp = d[d["near_change"] & d["spike"]]
    out.append(pd.DataFrame([{"section": "verdict", "rule": cfg["rule"], "near_change_spike_days": int(len(near_sp)),
                              "near_change_at_release": int(near_sp["at_release"].sum()),
                              "holds": bool(len(near_sp) > 0 and near_sp["at_release"].all()),
                              "changes": ",".join(c.isoformat() for c in ch)}]))
    return pd.concat(out, ignore_index=True)


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result, write_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.parse_args(argv)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    if cfg.get("status") != "fixed":
        print("REFUSED: config/dst_check.yaml is not fixed.")
        return 2
    src = rd / f"manual_{RUN.replace('-', '_')}.csv"
    if not src.exists():
        print(f"REFUSED: {src.name} is not ingested; run the kit and scripts/ingest_flip_run.py first.")
        return 2
    out = score(read_result(src), cfg, release_days(cfg))
    write_result(out, "dst_check_nq", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 results_dir=results_dir,
                 parameters={"config": "config/dst_check.yaml", "run": RUN, "decision": "D-386"},
                 notes={"status": "EXPLORATORY: Gate 4's clock check across daylight-saving changes (D-386 (7))"},
                 description="EXPLORATORY: the clock check -- each release day's three bars' ranges over the year's "
                             "non-release medians, the peak's bar, the near-change days' verdict and the control.")
    v = out[out["section"] == "verdict"].iloc[0]
    print(f"near-change spike days {int(v['near_change_spike_days'])}, at the release's bar {int(v['near_change_at_release'])}; "
          f"holds: {bool(v['holds'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
