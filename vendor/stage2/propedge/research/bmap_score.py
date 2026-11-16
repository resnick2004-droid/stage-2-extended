"""Scoring the bracket outcome map (config/bracket_map.yaml, D-149) from its ingested runs.

The outcome of an entry at target multiple k (the recorded path summary, `propedge/outcomes/bracket_core.py`):

    win   if mfe > k            -> +k,   less the round turn
    stop  if hit == 1           -> -1,   less one stop tick and the round turn
    gap   if hit == 2           -> exit, less one stop tick and the round turn
    time  otherwise             -> exit, less one flatten tick and the round turn

all in R at that entry's stop width (the entry's own adverse tick is already in the recorded prices). Costs are the
assumed ones (D-95) in the vehicle's ticks at the day's rescaled price (D-106).

Day filter (declared with the map): the session settled, at least 90 % of its minutes present, and D defined.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from propedge.research.fv_score import block_lower_bound

RR = (0.5, 1.0, 1.5, 2.0, 3.0, 5.0)
WIDTHS = (0.1, 0.2, 0.4)


def split(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(days, entries): entries carry their day's date, D and stop ticks; only days passing the filter keep entries."""
    days = df[df["kind"] == "day"].copy()
    days["date"] = pd.to_datetime(days["d"].astype(str).str.replace(r"\.0$", "", regex=True), format="%Y%m%d")
    days["ok"] = (days["st"] == 1) & (days["cov"] >= 0.9) & days["D"].notna()
    ent = df[df["kind"] == "entry"].copy()
    keep = ["n", "date", "D", "gap", "clv"] + [f"stop_ticks{wi}" for wi in range(len(WIDTHS))]
    ent = ent.drop(columns=[c for c in keep if c in ent.columns and c != "n"]).merge(
        days.loc[days["ok"], keep], on="n", how="inner")
    for c in ("t", "side", "f_fv", "f_vwap", "f_last30", "f_range") + tuple(f"hit{wi}" for wi in range(3)):
        ent[c] = ent[c].astype(int)
    return days, ent.sort_values(["n", "t", "side"]).reset_index(drop=True)


def outcome(ent: pd.DataFrame, wi: int, k: float, fills: dict) -> pd.DataFrame:
    """Per entry at width `wi` and target `k`: its kind (win / stop / gap / time) and R net and gross."""
    mfe, hit, ex = ent[f"mfe{wi}"].to_numpy(float), ent[f"hit{wi}"].to_numpy(int), ent[f"exit{wi}"].to_numpy(float)
    sk = ent[f"stop_ticks{wi}"].to_numpy(float)
    rt = fills["round_turn"] / (sk * fills["tick_value"])
    win = mfe > k + 1e-9
    kind = np.where(win, "win", np.where(hit == 1, "stop", np.where(hit == 2, "gap", "time")))
    gross = np.where(win, k, np.where(hit == 1, -1.0, ex))
    slip = np.where(win, fills["target"], np.where(hit >= 1, fills["stop"], fills["flatten"])) / sk
    ok = np.isfinite(mfe) & (hit >= 0)
    return pd.DataFrame({"n": ent["n"].to_numpy(), "kind": kind, "r_gross": gross, "r_net": gross - slip - rt,
                         "ok": ok})


def summarise(o: pd.DataFrame, day_ns, *, block: int, reps: int, seed: int) -> dict:
    o = o[o["ok"]]
    r = o["r_net"].to_numpy(float)
    by_day = o.groupby("n")["r_net"].agg(["sum", "count"]).reindex(list(day_ns), fill_value=0)
    share = o["kind"].value_counts(normalize=True)
    return {"entries": int(len(r)), "win_rate": float(share.get("win", 0.0)),
            "stop_rate": float(share.get("stop", 0.0) + share.get("gap", 0.0)),
            "time_exit_rate": float(share.get("time", 0.0)),
            "e_gross": float(o["r_gross"].mean()) if len(r) else float("nan"),
            "e": float(r.mean()) if len(r) else float("nan"),
            "e_lb": block_lower_bound(by_day["sum"].to_numpy(), by_day["count"].to_numpy(), block=block, reps=reps,
                                      seed=seed),
            "cost_r": float((o["r_gross"] - o["r_net"]).mean()) if len(r) else float("nan")}


__all__ = ["RR", "WIDTHS", "split", "outcome", "summarise"]
