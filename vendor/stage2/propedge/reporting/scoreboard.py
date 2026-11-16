"""The scoreboard (R2; `docs/HANDOFF_RESET_2026-10-29.md` §7 item 6): every registered run's gate rows side by side.

`config/scoreboard.yaml` lists the runs: each names its result file, its engine and its kind (development or
confirmation). This module reads each file through `read_result` (its manifest verified first) and takes:

* **the portfolio engine (D-312)** -- the gate row is the file's section "gate" at the lower bound of e, 0 % denial,
  the Responsible Trading Program's placement off (D-145, D-234, D-289); its metric is growth on the bankroll the
  run itself required, `pf_growth_on_base_p50` on `pf_required_p90`. Beside it, from the same file: the point arm,
  10 / 25 / 50 % denial at the bound and the break-even denial (never a verdict line, D-234), the placement on, the
  zero-edge twin, the bankroll's tail, the first payout, payouts, drawdown, steadiness and the pattern measures.
* **the notional engine** (before D-312) -- only `median_log_growth` on a notional bankroll exists; its declared rows'
  range goes in the `notional_growth_*` columns, never compared with the portfolio engine's growth.
* **the coin screen (D-521 (7), D-527)** -- the resolved coin's carried cell (`rc_reentry_screen.csv`, section "cell"), the
  baseline: its growth on the required bankroll at the bound and the point, its required bankroll and its zero-edge
  twin. Its row is a screen (exploratory), never a registered verdict.

**The lift over the coin (D-521 (7)):** every portfolio-engine row carries `growth_bound_minus_coin` (its growth at the
bound less the coin baseline's -- a like-for-like reading only for runs on the coin's protocol, P-14's, and a ranking
beside for the rest) and `signal_lift_over_zero_edge_twin` (its point growth less its own zero-edge twin's: what its
trades add over the same campaign at zero net edge; below zero, its costs outweigh its edge).

"Beat FV3-C's row or stop" (D-365, D-382, D-452): `beats_row_to_beat` compares a run's growth at the bound with
FV3-C's row of the same kind -- development with FV3-C's development baseline, confirmation with P-06 -- because a
one-year confirmation reads a wider bound than five development years (D-451). The required bankroll is beside it.

**FLAGs** (`docs/SUCCESS_CRITERIA.md` §5, D-457, D-475): each portfolio-engine run's gate row is read against the levels
in `results/success_thresholds.csv` (P-06's lower-bound arm's 90th or 10th percentile path) by
`propedge.campaign.criteria.flags`: `flag_<measure>` is "FLAG" beyond the level in the bad direction, "ok" inside it,
"not applicable" (spelled out: a CSV reader takes "n/a" for a missing value) where the run's file has no such column
(a measure built after its run), the run is notional, or the run's yaml entry says `flags: false` (a campaign of
another kind -- horizon, path count or firm -- than P-06's). A FLAG never changes a verdict.

No number is typed here; the yaml names files and rows, the files hold the numbers.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from propedge import CONFIG_DIR, RESULTS_DIR
from propedge.campaign.criteria import flags as _flags
from propedge.reporting.results import read_manifest, read_result, sha256_of

CONFIG_PATH = CONFIG_DIR / "scoreboard.yaml"
RESULT_NAME = "scoreboard.csv"
#: the FLAG levels (R1, D-457): read, never typed
THRESHOLDS_NAME = "success_thresholds.csv"
#: a FLAG cell with no reading; spelled out because pandas reads "n/a" back as a missing value
NA = "not applicable"
SCRIPT = "scripts/scoreboard.py"

#: The portfolio engine's columns carried to the scoreboard, all read on the gate row (bound, 0 %, placement off).
GATE_COLUMNS = {
    "growth_bound": "pf_growth_on_base_p50",
    "required_p50": "pf_required_p50",
    "required_p90": "pf_required_p90",
    "required_p99": "pf_required_p99",
    "required_worst": "pf_required_worst",
    "break_even_denial_bound": "pf_break_even_denial_p50",
    "days_to_first_payout_p50": "median_days_to_first_payout",
    "payouts_per_month_p50": "st_payouts_per_month_p50",
    "median_payouts_per_path": "median_payouts_per_path",
    "mean_payout_gross": "mean_payout_gross",
    "mean_max_drawdown": "mean_max_drawdown",
    "p90_max_drawdown": "p90_max_drawdown",
    "drawdown_p95": "st_max_drawdown_p95",
    "red_month_share_p50": "st_red_share_p50",
    "month_sd_p50": "st_month_sd_p50",
    "underwater_days_p50": "st_underwater_days_p50",
    "mean_combine_purchases": "mean_combine_purchases",
    "max_combine_purchases_21d": "mean_max_combine_purchases_21d",
    "share_payouts_exposed": "share_payouts_exposed",
    "realised_to_intended_capped_risk": "realised_to_intended_capped_risk",
    "notional_growth_gate_row": "median_log_growth",
}

DENIALS = (0.10, 0.25, 0.50)

#: engines whose growth is on the required bankroll (D-312) and so comparable with FV3-C's row
GROWTH_ENGINES = ("portfolio", "coin_screen")

#: Columns that only the portfolio engine fills.
PORTFOLIO_ONLY = [*GATE_COLUMNS, "growth_point", "break_even_denial_point", "growth_bound_placement_on",
                  "growth_zero_edge_twin", *(f"growth_bound_denial_{int(round(d * 100))}" for d in DENIALS)]


#: the coin screen's columns (its file's section "cell") read as the portfolio engine's
COIN_COLUMNS = {"growth_bound": "growth_on_required", "growth_point": "growth_on_required_point",
                "required_p90": "required_p90", "growth_zero_edge_twin": "growth_zero_edge_twin",
                "share_payouts_exposed": "share_payouts_exposed", "break_even_denial_bound": "break_even_denial_p50",
                "max_combine_purchases_21d": "mean_max_combine_purchases_21d"}


class ScoreboardError(ValueError):
    """A run's file does not hold the rows its engine needs, or a declared verdict disagrees with the file."""


def load_config(path: Path | str = CONFIG_PATH) -> dict[str, Any]:
    cfg = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    ids = [r["id"] for r in cfg["runs"]]
    if len(ids) != len(set(ids)):
        raise ScoreboardError(f"duplicate run ids in {path}: {ids}")
    for kind, rid in cfg["row_to_beat"].items():
        if rid not in ids:
            raise ScoreboardError(f"row_to_beat[{kind}] = {rid} is not a run in {path}")
    coin = cfg.get("coin_baseline")
    if coin is not None and coin not in ids:
        raise ScoreboardError(f"coin_baseline = {coin} is not a run in {path}")
    for r in cfg["runs"]:
        if r["kind"] not in ("development", "confirmation"):
            raise ScoreboardError(f"{r['id']}: kind must be development or confirmation, not {r['kind']!r}")
    return cfg


def _num(x: Any) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return float("nan")


def _placement_off(df: pd.DataFrame) -> pd.Series:
    if "placement" in df.columns:
        return df["placement"].astype(str).eq("off")
    return ~df["rtp"].astype(str).str.lower().eq("true")


def _first(df: pd.DataFrame, mask: pd.Series, what: str, run: str) -> pd.Series:
    rows = df[mask]
    if rows.empty:
        raise ScoreboardError(f"{run}: the file has no {what} row")
    return rows.iloc[0]


def gate_rows(df: pd.DataFrame, run: str) -> dict[str, pd.Series]:
    """The portfolio engine's rows: the gate (bound), the point, each denial at the bound, the placement on, the twin.

    The gate row is the first row of section "gate" at the lower bound, 0 % denial, placement off -- the row each
    verdict script marks `is_gate_row` first. A file without one is refused, never read loosely.
    """
    sec = df["section"].astype(str)
    shift = df["shift"].astype(str)
    den = pd.to_numeric(df["enforcement_p"], errors="coerce")
    off = _placement_off(df)
    in_gate = sec.eq("gate")
    out = {
        "gate": _first(df, in_gate & shift.eq("lower_bound") & den.eq(0.0) & off, "gate (bound, 0 %, off)", run),
        "point": _first(df, in_gate & shift.eq("point") & den.eq(0.0) & off, "point (0 %, off)", run),
    }
    for d in DENIALS:
        out[f"denial_{int(round(d * 100))}"] = _first(
            df, in_gate & shift.eq("lower_bound") & pd.Series(np.isclose(den, d), index=df.index) & off,
            f"bound at {d:.0%} denial", run)
    on = sec.isin(["gate", "placement_on"]) & shift.eq("lower_bound") & den.eq(0.0) & ~off
    out["placement_on"] = _first(df, on, "placement-on bound", run)
    twin = sec.eq("zero_edge_twin")
    if "twin" in df.columns:
        twin |= sec.eq("twin") & df["twin"].astype(str).eq("zero_edge")
    out["zero_edge_twin"] = _first(df, twin & den.eq(0.0) & off, "zero-edge twin", run)
    return out


def file_verdict(df: pd.DataFrame) -> str | None:
    """The verdict word the producing script wrote into the file, if it wrote exactly one."""
    if "verdict" not in df.columns:
        return None
    v = df["verdict"].dropna().astype(str).unique().tolist()
    return v[0] if len(v) == 1 else None


def verdict_agrees(declared: str, in_file: str | None) -> bool:
    """The declared verdict's first word matches the file's (case aside); a file with no verdict cell agrees."""
    if in_file is None or not isinstance(in_file, str) or not in_file.strip():
        return True
    return declared.split()[0].upper() == in_file.split()[0].upper()


def flag_levels(results_dir: Path | str = RESULTS_DIR) -> pd.DataFrame | None:
    """The FLAG rows of `results/success_thresholds.csv` (its manifest verified by `read_result`); None without it."""
    path = Path(results_dir) / THRESHOLDS_NAME
    if not path.is_file():
        return None
    lv = read_result(path)
    return lv[lv["section"].astype(str).eq("flag")].reset_index(drop=True)


def _flag_cells(gate: pd.Series | None, levels: pd.DataFrame | None) -> dict[str, Any]:
    """`flag_<measure>` per FLAG level ("FLAG", "ok" or "not applicable") and `flags_raised`, the count of "FLAG"."""
    names = [] if levels is None else levels["measure"].astype(str).tolist()
    if gate is None or levels is None:
        return {**{f"flag_{m}": NA for m in names}, "flags_raised": float("nan")}
    f = _flags(gate, levels)
    cells = {f"flag_{m}": (NA if v is None else "FLAG" if v else "ok") for m, v in f.items()}
    return {**cells, "flags_raised": float(sum(1 for v in f.values() if v))}


def read_run(run: dict[str, Any], results_dir: Path | str = RESULTS_DIR,
             levels: pd.DataFrame | None = None) -> dict[str, Any]:
    """One scoreboard row from one run's result file; with `levels`, its FLAGs (§5)."""
    path = Path(results_dir) / run["file"]
    df = read_result(path)
    man = read_manifest(path)
    in_file = file_verdict(df)
    if not verdict_agrees(str(run["verdict"]), in_file):
        raise ScoreboardError(f"{run['id']}: declared verdict {run['verdict']!r} but the file says {in_file!r}")
    row: dict[str, Any] = {
        "run": run["id"], "prereg": run.get("prereg") or "", "candidate": run["candidate"], "kind": run["kind"],
        "role": run.get("role", "registered"), "market": run["market"], "window": run["window"],
        "engine": run["engine"], "verdict": run["verdict"], "file_verdict": in_file or "",
        "decision": run.get("decision", ""), "note": run.get("note", ""),
        "source_file": f"results/{run['file']}", "source_sha256": sha256_of(path),
        "source_exploratory": bool(man.exploratory), "source_prereg": man.prereg_id or "",
        "source_commit": man.git_commit,
    }
    if run["engine"] == "portfolio":
        rows = gate_rows(df, run["id"])
        g = rows["gate"]
        for name, col in GATE_COLUMNS.items():
            row[name] = _num(g[col]) if col in g.index else float("nan")
        row["growth_point"] = _num(rows["point"]["pf_growth_on_base_p50"])
        row["break_even_denial_point"] = _num(rows["point"]["pf_break_even_denial_p50"])
        for d in DENIALS:
            k = f"denial_{int(round(d * 100))}"
            row[f"growth_bound_{k}"] = _num(rows[k]["pf_growth_on_base_p50"])
        row["growth_bound_placement_on"] = _num(rows["placement_on"]["pf_growth_on_base_p50"])
        row["growth_zero_edge_twin"] = _num(rows["zero_edge_twin"]["pf_growth_on_base_p50"])
        row["notional_growth_min"] = row["notional_growth_max"] = float("nan")
        row.update(_flag_cells(g if run.get("flags", True) else None, levels))
    elif run["engine"] == "coin_screen":
        cells = df[df["section"].astype(str).eq("cell") & df["cell"].astype(str).eq(str(run["cell"]))]
        if len(cells) != 1:
            raise ScoreboardError(f"{run['id']}: {len(cells)} cell rows named {run['cell']!r}, not one")
        c = cells.iloc[0]
        for name in PORTFOLIO_ONLY:
            row[name] = float("nan")
        for name, col in COIN_COLUMNS.items():
            row[name] = _num(c[col]) if col in c.index else float("nan")
        row["notional_growth_min"] = row["notional_growth_max"] = float("nan")
        row.update(_flag_cells(None, levels))
    elif run["engine"] == "notional":
        sel = pd.Series(True, index=df.index)
        for col, val in (run.get("notional_rows") or {}).items():
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                sel &= pd.Series(np.isclose(pd.to_numeric(df[col], errors="coerce"), float(val)), index=df.index)
            else:
                sel &= df[col].astype(str).eq(str(val))
        vals = pd.to_numeric(df.loc[sel, "median_log_growth"], errors="coerce").dropna()
        if vals.empty:
            raise ScoreboardError(f"{run['id']}: no notional rows match {run.get('notional_rows')}")
        row["notional_growth_min"] = float(vals.min())
        row["notional_growth_max"] = float(vals.max())
        for name in PORTFOLIO_ONLY:
            row[name] = float("nan")
        row.update(_flag_cells(None, levels))
    else:
        raise ScoreboardError(f"{run['id']}: unknown engine {run['engine']!r}")
    return row


LEAD = ["run", "prereg", "candidate", "kind", "role", "market", "window", "verdict", "beats_row_to_beat",
        "growth_bound", "growth_point", "required_p90", "break_even_denial_bound", "days_to_first_payout_p50",
        "payouts_per_month_p50", "flags_raised"]


def build(cfg: dict[str, Any] | None = None, results_dir: Path | str = RESULTS_DIR) -> pd.DataFrame:
    """The scoreboard: one row per run in the yaml's order, with the row-to-beat comparison."""
    cfg = cfg or load_config()
    levels = flag_levels(results_dir)
    sb = pd.DataFrame([read_run(r, results_dir, levels) for r in cfg["runs"]])
    by_id = sb.set_index("run")
    targets = cfg["row_to_beat"]
    beat, target_col, margin = [], [], []
    for r in sb.itertuples(index=False):
        tid = targets.get(r.kind)
        target_col.append(tid or "")
        if tid is None or r.engine not in GROWTH_ENGINES or by_id.loc[tid, "engine"] != "portfolio":
            beat.append("n/a (notional engine)")
            margin.append(float("nan"))
        elif r.run == tid:
            beat.append("row to beat")
            margin.append(0.0)
        else:
            m = float(r.growth_bound) - float(by_id.loc[tid, "growth_bound"])
            margin.append(m)
            beat.append("yes" if m > 0 else "no")
    sb["row_to_beat"] = target_col
    sb["growth_bound_minus_row_to_beat"] = margin
    sb["beats_row_to_beat"] = beat
    coin = cfg.get("coin_baseline")
    growth = sb["engine"].isin(GROWTH_ENGINES)
    if coin is not None:
        if coin not in set(sb["run"]):
            raise ScoreboardError(f"coin_baseline = {coin} is not a run")
        cb = float(by_id.loc[coin, "growth_bound"])
        sb["coin_baseline"] = np.where(growth, coin, "")
        sb["growth_bound_minus_coin"] = np.where(growth, sb["growth_bound"].astype(float) - cb, np.nan)
    sb["signal_lift_over_zero_edge_twin"] = np.where(
        growth, sb["growth_point"].astype(float) - sb["growth_zero_edge_twin"].astype(float), np.nan)
    return sb[LEAD + [c for c in sb.columns if c not in LEAD]]


def comparable(df: pd.DataFrame) -> pd.DataFrame:
    """The scoreboard as it reads back from its CSV: empty text and missing text alike as "" (a CSV keeps no
    difference), numbers as floats -- for comparing a fresh build with the file."""
    out = df.copy()
    for c in out.columns:
        if out[c].dtype == object or pd.api.types.is_string_dtype(out[c]):
            out[c] = out[c].fillna("").astype(str)
    return out


def sources(cfg: dict[str, Any] | None = None, results_dir: Path | str = RESULTS_DIR) -> dict[str, str]:
    """Each run's source file and its sha256 now -- recorded in the scoreboard's manifest, checked by the tests."""
    cfg = cfg or load_config()
    out = {f"results/{r['file']}": sha256_of(Path(results_dir) / r["file"]) for r in cfg["runs"]}
    if (Path(results_dir) / THRESHOLDS_NAME).is_file():
        out[f"results/{THRESHOLDS_NAME}"] = sha256_of(Path(results_dir) / THRESHOLDS_NAME)
    return out
