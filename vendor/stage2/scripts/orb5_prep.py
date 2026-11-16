"""ORB5's preparation (T16 items 2(a) and 2(c); D-272): what the contract allows and what the entries cost, from R102-R107
with no outcome read -- stops, fills, the hand-traded entry's kind and distance, and the recorded quotes only.

    python scripts/orb5_prep.py

**The stand-aside rule** (D-272 (1), D-212 applied to each trade): a trade is taken in an account state only if its
whole-micro size under the state's cap (`results/stop_band.csv`: 37 micros in the Combine, 15 in a funded account below
+$2,000) carries at least 90 % of the state's dollar risk and its stop is at or above the market's cost-drag floor.

Sections of results/orb5_prep.csv, each per era -- 2009-2017, 2018 on, and 2020 to June 2025 (today's stops):

* `sizing` -- per stop width of ORB3's grid, account state and dollar risk: the trading days, the share sizeable, the
  realised risk's 10th, 50th and 90th percentiles over every day and the median over the sizeable ones;
* `funded_risk` -- per stop width, the largest of $1,000, $750 and $500 at which at least 90 % of 2020 to June 2025's
  days are sizeable (D-272 (3)), and the Combine's sizeable share at $1,500;
* `fills` -- per set of ranges: breakouts a day, those on the side of the day's first fill (the direction lock, D-269),
  and the hand-traded entries a day under each missed-trigger policy (D-266);
* `hand` -- per range: the shares of the hand-traded entry's kinds, and per stop width the median and 90th percentile of
  its distance from the original fill in R (a chase or a late stop is worse by this much before any outcome);
* `spread` -- the recorded bid-ask spread (NQ's quote, D-265) at the fill minute, the minute after and the 15:07-15:09
  opens: median and 90th percentile in micro ticks and, per stop width, the median in R;
* `setups` -- D-154's minimum setups a day for each Combine size `results/setups_per_day.csv` holds, at zero edge.

FOMC days are out, as in ORB3. Deterministic, no seed.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import score_orb3_search as s3  # noqa: E402

SCRIPT = "scripts/orb5_prep.py"
RISK_FLOOR = 0.90                                    # D-212: at least 90 % of the state's dollar risk
COMBINE_RISKS = (500.0, 750.0, 1000.0, 1200.0, 1500.0, 2000.0)
FUNDED_RISKS = (1000.0, 750.0, 500.0)               # D-253's candidates, largest first
FUNDED_SHARE = 0.90                                  # D-272 (3)
ERAS = {"2009-2017": (2009, 2017), "2018-2025": (2018, 2025), "2020-2025": (2020, 2025)}
RANGE_SETS = ((5,), (5, 15), (5, 15, 30), (5, 15, 30, 60))
CAPTURES = ("R105-orb5-NQ-0914", "R106-orb5-NQ-1519", "R107-orb5-NQ-2025")
POLICIES = {"skip": (0,), "rest": (0, 2), "chase": (0, 1, 2)}
KINDS = {-1: "none", 0: "same", 1: "chase", 2: "late_stop"}


def realised(stop_ticks, risk: float, cap: int, tick_value: float) -> np.ndarray:
    """Whole-micro dollar risk under the cap: min(floor(risk / stop $), cap) x stop $."""
    per = np.asarray(stop_ticks, dtype=float) * tick_value
    return np.minimum(np.floor(risk / per + 1e-9), cap) * per


def sizeable(stop_ticks, risk: float, cap: int, tick_value: float, floor_ticks: int) -> np.ndarray:
    """D-272 (1): the size carries at least 90 % of the risk and the stop clears the cost-drag floor."""
    st = np.asarray(stop_ticks, dtype=float)
    return (realised(st, risk, cap, tick_value) >= RISK_FLOOR * risk - 1e-9) & (st >= floor_ticks)


def era_mask(years: pd.Series, era: str) -> pd.Series:
    a, b = ERAS[era]
    return (years >= a) & (years <= b)


def load(rd: Path):
    cfg = s3.config()
    d, _, have = s3.load(rd, cfg)
    if set(have) != set(cfg["runs"]):
        raise SystemExit(f"REFUSED: ORB3's three runs are needed, ingested: {have}.")
    caps = []
    for run in CAPTURES:
        f = rd / f"manual_{run.replace('-', '_')}.csv"
        if not f.is_file():
            raise SystemExit(f"REFUSED: {run} is not ingested.")
        t = pd.read_csv(f, low_memory=False)
        caps.append(t[t["kind"] == "day"])
    c = pd.concat(caps, ignore_index=True)
    c["or_minutes"] = c["or_minutes"].astype(int)
    d["date"], c["date"] = d["date"].astype(str), c["date"].astype(str)
    keep = ["date", "or_minutes", "lat_kind", "lat_slot", "lat_gap_ticks", "spread_fill_tenths",
            "spread_after_fill_tenths", "spread_1507_tenths", "spread_1508_tenths", "spread_1509_tenths"]
    m = d.merge(c[keep], on=["date", "or_minutes"], how="inner", validate="one_to_one")
    if len(m) != len(d) or len(m) != len(c):
        raise SystemExit("REFUSED: ORB3's records and the captures do not cover the same days and ranges.")
    m = m[~m["date"].isin(s3.fomc_dates(cfg))].copy()
    m["year"] = pd.to_datetime(m["date"]).dt.year
    return cfg, m


def sizing_rows(m: pd.DataFrame, cfg: dict, band: pd.DataFrame) -> list[dict]:
    rows = []
    days = m[m["or_minutes"] == 5]                                   # one row a day carries the day's stops
    states = [("combine", r, "combine") for r in COMBINE_RISKS] + [("funded", r, "funded_below_2000")
                                                                   for r in FUNDED_RISKS]
    for i, width in enumerate(cfg["search"]["stop_atr"]):
        st = days[f"stop_ticks_{i}"]
        for state, risk, cap_state in states:
            b = band[(band["state"] == cap_state) & (band["market"] == "NQ")].iloc[0]
            cap, tv, flo = int(b["cap_micros"]), float(b["tick_value"]), int(b["cost_drag_floor_ticks"])
            for era in ERAS:
                s = st[era_mask(days["year"], era)]
                got = realised(s, risk, cap, tv)
                ok = sizeable(s, risk, cap, tv, flo)
                q = np.percentile(got, [10, 50, 90]) if len(s) else [np.nan] * 3
                rows.append({"section": "sizing", "era": era, "stop_atr": width, "state": state, "risk": risk,
                             "cap_micros": cap, "days": int(len(s)), "share_sizeable": float(ok.mean()) if len(s)
                             else np.nan, "realised_p10": q[0], "realised_p50": q[1], "realised_p90": q[2],
                             "realised_p50_sizeable": float(np.median(got[ok])) if ok.any() else np.nan,
                             "stop_ticks_p50": float(s.median()) if len(s) else np.nan})
    return rows


def funded_rows(sz: pd.DataFrame, cfg: dict) -> list[dict]:
    rows = []
    today = sz[sz["era"] == "2020-2025"]
    for width in cfg["search"]["stop_atr"]:
        w = today[today["stop_atr"] == width]
        pick = next((r for r in FUNDED_RISKS if float(w[(w["state"] == "funded") & (w["risk"] == r)]
                                                       ["share_sizeable"].iloc[0]) >= FUNDED_SHARE), np.nan)
        comb = float(w[(w["state"] == "combine") & (w["risk"] == 1500.0)]["share_sizeable"].iloc[0])
        rows.append({"section": "funded_risk", "era": "2020-2025", "stop_atr": width, "funded_risk": pick,
                     "combine_1500_share_sizeable": comb})
    return rows


def fill_rows(m: pd.DataFrame) -> list[dict]:
    rows = []
    for era in ERAS:
        e = m[era_mask(m["year"], era)]
        n_days = e["date"].nunique()
        for rs in RANGE_SETS:
            f = e[e["or_minutes"].isin(rs) & (e["fill_slot"] != -1) & (e["dir"] != 0)]
            f = f.sort_values(["date", "fill_slot", "or_minutes"])
            first = f.groupby("date")["dir"].transform("first")
            row = {"section": "fills", "era": era, "ranges": "+".join(map(str, rs)), "days": int(n_days),
                   "breakouts_per_day": len(f) / n_days, "locked_per_day": int((f["dir"] == first).sum()) / n_days}
            for pol, kinds in POLICIES.items():
                row[f"hand_{pol}_per_day"] = int(f["lat_kind"].isin(kinds).sum()) / n_days
            rows.append(row)
    return rows


def hand_rows(m: pd.DataFrame, cfg: dict) -> list[dict]:
    rows = []
    for era in ERAS:
        e = m[era_mask(m["year"], era) & (m["fill_slot"] != -1)]
        for n in (5, 15, 30, 60):
            r = e[e["or_minutes"] == n]
            row = {"section": "hand", "era": era, "or_minutes": n, "filled": int(len(r))}
            for k, name in KINDS.items():
                row[f"share_{name}"] = float((r["lat_kind"] == k).mean()) if len(r) else np.nan
            rows.append(row)
        for i, width in enumerate(cfg["search"]["stop_atr"]):
            for k in (1, 2):
                r = e[e["lat_kind"] == k]
                gap_r = r["lat_gap_ticks"] / r[f"stop_ticks_{i}"]
                rows.append({"section": "hand", "era": era, "stop_atr": width, "kind": KINDS[k], "n": int(len(r)),
                             "gap_r_p50": float(gap_r.median()) if len(r) else np.nan,
                             "gap_r_p90": float(gap_r.quantile(0.9)) if len(r) else np.nan})
    return rows


def spread_rows(m: pd.DataFrame, cfg: dict) -> list[dict]:
    rows = []
    for era in ERAS:
        e = m[era_mask(m["year"], era) & (m["fill_slot"] != -1)]
        for col in ("spread_fill_tenths", "spread_after_fill_tenths", "spread_1507_tenths", "spread_1508_tenths",
                    "spread_1509_tenths"):
            x = e[col][e[col] >= 0] / 10.0                                   # micro ticks; -1 = none recorded
            row = {"section": "spread", "era": era, "where": col.replace("_tenths", ""), "n": int(len(x)),
                   "ticks_p50": float(x.median()) if len(x) else np.nan,
                   "ticks_p90": float(x.quantile(0.9)) if len(x) else np.nan,
                   "share_missing": float((e[col] < 0).mean()) if len(e) else np.nan}
            for i, width in enumerate(cfg["search"]["stop_atr"]):
                ok = e[col] >= 0
                row[f"r_p50_{width:g}"] = float((e[col][ok] / 10.0 / e[f"stop_ticks_{i}"][ok]).median()) \
                    if ok.any() else np.nan
            rows.append(row)
    return rows


def setup_rows() -> list[dict]:
    from propedge.reporting.results import read_result
    from propedge.research.model_card import SETUPS_FILE

    t = read_result(SETUPS_FILE)
    t = t[t["edge"] == 0.0].drop_duplicates(["rr", "risk"])
    return [{"section": "setups", "rr": float(r["rr"]), "risk": float(r["risk"]),
             "min_setups_per_day": float(r["min_setups_per_day"])} for _, r in t.iterrows()]


def main(results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result, write_result
    from propedge.research.model_card import BAND_FILE

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    cfg, m = load(rd)
    band = read_result(BAND_FILE)
    sz = pd.DataFrame(sizing_rows(m, cfg, band))
    rows = (sz.to_dict("records") + funded_rows(sz, cfg) + fill_rows(m) + hand_rows(m, cfg) + spread_rows(m, cfg)
            + setup_rows())
    out = pd.DataFrame(rows)
    write_result(out, "orb5_prep", script=SCRIPT, seed=None, require_seed=False, exploratory=False,
                 results_dir=results_dir,
                 parameters={"runs": list(cfg["runs"]) + list(CAPTURES), "risk_floor": RISK_FLOOR,
                             "combine_risks": list(COMBINE_RISKS), "funded_risks": list(FUNDED_RISKS),
                             "funded_share": FUNDED_SHARE, "eras": {k: list(v) for k, v in ERAS.items()},
                             "decision": "D-272"},
                 notes={"status": "outcome-free: stops, fills, entries and quotes only; no trade result is read"},
                 description="ORB5's preparation: the contract's sizing and stand-aside per stop width and era, the "
                             "entries a day, the hand-traded entry's kinds and distance in R, the recorded spreads, "
                             "D-154's minimum setups. No outcome read. Deterministic, no seed.")
    pd.set_option("display.width", 250)
    print(out[out["section"] == "funded_risk"].dropna(axis=1, how="all").round(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
