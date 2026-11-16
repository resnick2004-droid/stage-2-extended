"""A slow, direct reference for `extended.features` (tests only): each feature at one (trading day, alert) computed from
the bars **filtered by timestamp** -- `ts <= alert_ts - 60`, the bar stamped t - 1 minute and earlier -- with the CT
clock recomputed here from `ts` (not taken from the library), loops instead of prefix sums, pandas instead of the
[day, slot] grid. It shares nothing with the library but the registry's names, the calendars and the constants of the
documented formulas, so agreement means the vectorised code computes what the registry documents, from the past only.
"""
from __future__ import annotations

from datetime import date
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

CHI = ZoneInfo("America/Chicago")
NAN = float("nan")


def prepare(bars: pd.DataFrame) -> pd.DataFrame:
    """The bars with the CT clock beside them: `tday` (trading day), `slot` (minutes after 17:00 CT the evening the
    day opens), sorted by ts."""
    b = bars.sort_values("ts", kind="stable").reset_index(drop=True).copy()
    local = pd.to_datetime(b["ts"], unit="s", utc=True).dt.tz_convert(CHI).dt.tz_localize(None)
    mins = local.dt.hour * 60 + local.dt.minute
    b["slot"] = ((mins - 17 * 60) % 1440).astype(int)
    tday = (local + pd.Timedelta(hours=7)).dt.date
    b["tday"] = tday.astype(str)
    return b


def _day_stats(dbars: pd.DataFrame) -> dict:
    rth = dbars[(dbars["slot"] >= 930) & (dbars["slot"] < 1320)]
    return {
        "H": dbars["high"].max(), "L": dbars["low"].min(), "O": dbars["open"].iloc[0], "C": dbars["close"].iloc[-1],
        "contract": dbars["contract"].iloc[0],
        "rH": rth["high"].max() if len(rth) else NAN, "rL": rth["low"].min() if len(rth) else NAN,
        "rO": rth["open"].iloc[0] if len(rth) else NAN,
        "rC": dbars[dbars["slot"] <= 1319]["close"].iloc[-1] if len(rth) else NAN,
    }


def _changes(today: pd.DataFrame) -> pd.Series:
    """Each bar's close change from the previous bar of the same day (NaN for the day's first bar)."""
    return today["close"].diff()


def _rv(today: pd.DataFrame, t: int, w: int) -> float:
    d = _changes(today)
    sel = d[(today["ts"] >= t - 60 * w).to_numpy()].dropna()
    return float(np.sqrt((sel ** 2).mean())) if len(sel) >= 2 else NAN


def _volume_in(dbars: pd.DataFrame, s: int, w: int | None) -> float:
    lo = 0 if w is None else s - w
    return float(dbars[(dbars["slot"] >= lo) & (dbars["slot"] <= s - 1)]["volume"].sum())


def _rv_slots(dbars: pd.DataFrame, s: int, w: int) -> float:
    d = dbars["close"].diff()
    m = ((dbars["slot"] >= s - w) & (dbars["slot"] <= s - 1)).to_numpy()
    sel = d[m].dropna()
    return float(np.sqrt((sel ** 2).mean())) if len(sel) >= 2 else NAN


def _median(vals: list[float], min_count: int = 10) -> float:
    v = [x for x in vals if not np.isnan(x)]
    return float(np.median(v)) if len(v) >= min_count else NAN


def reference(B: pd.DataFrame, day: str, alert_ts: int, cal) -> dict[str, float]:
    """Every registered feature at (day, alert_ts) from `prepare(bars)`."""
    t = int(alert_ts)
    past = B[B["ts"] <= t - 60]
    today = past[past["tday"] == day]
    if today.empty:
        raise ValueError("no closed bar on the day")
    s = int(((pd.Timestamp(t, unit="s", tz="UTC").tz_convert(CHI).hour * 60
              + pd.Timestamp(t, unit="s", tz="UTC").tz_convert(CHI).minute) - 17 * 60) % 1440)
    prior = sorted(d for d in past["tday"].unique() if d < day)
    stats = [_day_stats(B[B["tday"] == d]) for d in prior]
    # true ranges and chained changes of the prior days, each against the day before it in the frame
    trs, chg = [], []
    for j, st in enumerate(stats):
        same = j > 0 and stats[j - 1]["contract"] == st["contract"]
        if same:
            pc = stats[j - 1]["C"]
            trs.append(max(st["H"], pc) - min(st["L"], pc))
            chg.append(st["C"] - pc)
        else:
            trs.append(st["H"] - st["L"])
            chg.append(st["C"] - st["O"])
    A = float(np.mean(trs[-14:])) if len(trs) >= 14 else NAN
    A5 = float(np.mean(trs[-5:])) if len(trs) >= 5 else NAN
    ret5d = float(np.sum(chg[-5:])) / A if len(chg) >= 5 else NAN
    ret20d = float(np.sum(chg[-20:])) / A if len(chg) >= 20 else NAN
    contract = today["contract"].iloc[0]
    p = stats[-1] if stats else None
    cross = p is not None and p["contract"] == contract

    c = float(today["close"].iloc[-1])

    def asof(x_ts: int) -> float:
        q = today[today["ts"] <= x_ts]
        return float(q["close"].iloc[-1]) if len(q) else NAN

    def win(w: int) -> pd.DataFrame:
        return today[today["ts"] >= t - 60 * w]

    f: dict[str, float] = {}
    for w in (5, 15, 30, 60, 120):
        f[f"ret_{w}"] = (c - asof(t - 60 - 60 * w)) / A
    rth = today[today["slot"] >= 930]
    f["ret_rth"] = (c - float(rth["open"].iloc[0])) / A if len(rth) else NAN
    f["ret_day"] = (c - float(today["open"].iloc[0])) / A
    for w in (15, 60):
        q = win(w)
        f[f"rng_{w}"] = (q["high"].max() - q["low"].min()) / A if len(q) else NAN
    hd, ld = today["high"].max(), today["low"].min()
    f["range_day"] = (hd - ld) / A
    f["pos_day"] = (c - ld) / (hd - ld) if hd > ld else NAN
    if len(rth):
        hr, lr = rth["high"].max(), rth["low"].min()
        f["range_rth"] = (hr - lr) / A
        f["pos_rth"] = (c - lr) / (hr - lr) if hr > lr else NAN
        vv = rth["volume"].sum()
        vwap = (((rth["high"] + rth["low"] + rth["close"]) / 3.0) * rth["volume"]).sum() / vv if vv > 0 else NAN
        f["d_vwap"] = (c - vwap) / A
    else:
        f["range_rth"] = f["pos_rth"] = f["d_vwap"] = NAN
    if cross:
        f["pos_prior"] = (c - p["rL"]) / (p["rH"] - p["rL"])
        f["d_pdh"] = (c - p["rH"]) / A
        f["d_pdl"] = (c - p["rL"]) / A
        f["d_pdc"] = (c - p["rC"]) / A
    else:
        f["pos_prior"] = f["d_pdh"] = f["d_pdl"] = f["d_pdc"] = NAN
    on = today[today["slot"] < 930]
    f["d_onh"] = (c - on["high"].max()) / A
    f["d_onl"] = (c - on["low"].min()) / A
    f["range_on"] = (on["high"].max() - on["low"].min()) / A
    f["gap"] = (float(on["close"].iloc[-1]) - p["rC"]) / A if cross and len(on) else NAN
    f["d_round"] = (c - 100.0 * round(c / 100.0)) / A
    orb = today[(today["slot"] >= 930) & (today["slot"] < 960)]
    if s >= 960 and len(orb):
        f["or_width"] = (orb["high"].max() - orb["low"].min()) / A
        f["or_pos"] = (c - orb["low"].min()) / (orb["high"].max() - orb["low"].min())
    else:
        f["or_width"] = f["or_pos"] = NAN
    v5, v30, v60, vday = (float(win(5)["volume"].sum()), float(win(30)["volume"].sum()),
                          float(win(60)["volume"].sum()), float(today["volume"].sum()))
    prior20 = prior[-20:]
    pdays = [B[B["tday"] == d] for d in prior20]
    m5 = _median([_volume_in(x, s, 5) for x in pdays])
    m30 = _median([_volume_in(x, s, 30) for x in pdays])
    mday = _median([_volume_in(x, s, None) for x in pdays])
    mrv = _median([_rv_slots(x, s, 60) for x in pdays])
    f["vol_5"] = np.log((v5 + 1.0) / (m5 + 1.0))
    f["vol_30"] = np.log((v30 + 1.0) / (m30 + 1.0))
    f["vol_day"] = np.log((vday + 1.0) / (mday + 1.0))
    f["vol_accel"] = np.log((v5 / 5.0 + 1.0) / (v60 / 60.0 + 1.0))
    rv15, rv60 = _rv(today, t, 15), _rv(today, t, 60)
    f["rv_ratio"] = rv15 / rv60
    f["rv_tod"] = np.log(rv60 / mrv)
    f["rv_atr"] = rv60 / A
    f["atr_ratio"] = A5 / A
    f["range_prior"] = (p["rH"] - p["rL"]) / A if p else NAN
    f["atr_rel"] = A / c * 1e4
    f["ret_prior"] = (p["rC"] - p["rO"]) / A if p else NAN
    f["ret_5d"], f["ret_20d"] = ret5d, ret20d
    q60 = win(60)
    f["ext_ma60"] = (c - q60["close"].mean()) / A if len(q60) else NAN
    d30 = _changes(today)[(today["ts"] >= t - 60 * 30).to_numpy()].dropna()
    f["up_share_30"] = float((d30 > 0).mean()) if len(d30) else NAN
    path = float(d30.abs().sum())
    f["eff_30"] = abs(c - asof(t - 60 - 60 * 30)) / path if path > 0 else NAN
    f["tod"] = (s - 930) / 60.0
    dd = date.fromisoformat(day)
    f["dow"] = float(dd.weekday())
    f["bls_day"] = float(dd in cal.bls)
    f["bls_major"] = float(dd in cal.bls_major)
    nxt = [(fd - dd).days for fd, until in cal.fomc_scheduled if fd >= dd and (until is None or dd <= until)]
    f["days_to_fomc"] = float(min(30, min(nxt))) if nxt else 30.0
    prv = [(dd - fd).days for fd in cal.fomc_statements if fd < dd]
    f["days_since_fomc"] = float(min(30, min(prv))) if prv else 30.0
    f["norm_atr14"], f["norm_atr5"] = A, A5
    f["norm_v5_med"], f["norm_v30_med"], f["norm_vday_med"], f["norm_rv60_med"] = m5, m30, mday, mrv
    return f
