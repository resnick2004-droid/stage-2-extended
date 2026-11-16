"""The campaign results viewer: a page built from result files, never from typed numbers (T7a, slice 6).

Reads the dry run's (or, later, T7's) result CSVs **through `read_result`**, so a file whose
sha256 no longer matches its manifest cannot reach the page, embeds the data and the manifests'
provenance into a self-contained HTML template, and writes it. Every number on the page is a
value from a result file, and the page says which files, at which commit, with which seed.

The page itself (`campaign_viewer.html`) renders per-path campaign cash, the per-arm ranking
metric beside ruin, drawdown and latency, and one path's account timelines, with a table view
behind every chart. It carries the manifests' `exploratory` flag as a banner: a dry run at an
assumed edge is labelled as such on the page, not only in the manifest.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from propedge import RESULTS_DIR
from propedge.reporting.results import read_manifest, read_result

TEMPLATE = Path(__file__).with_name("campaign_viewer.html")
FILES = ("arms", "paths", "cash", "accounts")


def _clean(v: Any) -> Any:
    """JSON-safe scalars: NaN becomes None, numpy scalars become Python."""
    if isinstance(v, float) and v != v:
        return None
    if hasattr(v, "item"):
        v = v.item()
        return None if isinstance(v, float) and v != v else v
    return v


def _records(df: pd.DataFrame) -> list[dict[str, Any]]:
    return [{k: _clean(v) for k, v in row.items()} for row in df.to_dict(orient="records")]


def load_payload(results_dir: Path | str | None = None, prefix: str = "t7a_dry_run") -> dict[str, Any]:
    """The page's data: the four result files, verified, plus their provenance."""
    results_dir = Path(results_dir) if results_dir is not None else RESULTS_DIR
    frames: dict[str, pd.DataFrame] = {}
    manifests: dict[str, Any] = {}
    for key in FILES:
        csv = results_dir / f"{prefix}_{key}.csv"
        frames[key] = read_result(csv)               # raises if the hash does not match
        manifests[key] = read_manifest(csv)

    arms = _records(frames["arms"])
    # Cash series are embedded to the cent: the CSV stays exact, the page stays small.
    cash: dict[str, list[list[float]]] = {}
    for arm, g in frames["cash"].groupby("arm", sort=False):
        series = []
        for _, gp in g.groupby("path", sort=True):
            series.append([round(float(x), 2) for x in gp.sort_values("day")["cash"]])
        cash[str(arm)] = series
    accounts: dict[str, list[dict[str, Any]]] = {}
    for arm, g in frames["accounts"].groupby("arm", sort=False):
        rows = []
        for r in _records(g):
            pd_str = r.get("payout_days") or ""
            r["payout_days"] = [int(x) for x in str(pd_str).split(";") if x not in ("", "nan")]
            rows.append(r)
        accounts[str(arm)] = rows
    # Per-arm distribution of the per-path outcomes, not the rows themselves: the page shows
    # quantiles, and the rows stay in the CSV for anyone who wants them.
    path_stats: dict[str, dict[str, Any]] = {}
    for arm, g in frames["paths"].groupby("arm", sort=False):
        fc = g["final_cash"].astype(float)
        path_stats[str(arm)] = {
            "n": int(len(g)),
            "final_cash_p10": round(float(fc.quantile(0.10)), 2),
            "final_cash_p50": round(float(fc.quantile(0.50)), 2),
            "final_cash_p90": round(float(fc.quantile(0.90)), 2),
            "ruined_share": round(float(g["ruined"].astype(bool).mean()), 4),
            "mean_attempts": round(float(g["attempts_started"].mean()), 2),
            "mean_accounts_funded": round(float(g["accounts_funded"].mean()), 2),
        }

    m = manifests["arms"]
    meta = {
        "prefix": prefix,
        "script": m.script,
        "git_commit": m.git_commit,
        "seed": m.seed,
        "timestamp": m.timestamp,
        "exploratory": bool(m.exploratory),
        "description": m.description,
        "notes": m.notes or {},
        "parameters": m.parameters,
        "files": {
            key: {"file": manifests[key].result_file, "sha256": manifests[key].sha256,
                  "rows": manifests[key].rows}
            for key in FILES
        },
    }
    return {"meta": meta, "arms": arms, "cash": cash, "accounts": accounts, "path_stats": path_stats}


def render(payload: dict[str, Any], template: Path | None = None) -> str:
    """The page, with the payload embedded. `</script>` inside the JSON is escaped."""
    template = template or TEMPLATE
    html = template.read_text(encoding="utf-8")
    if "__PAYLOAD__" not in html:
        raise ValueError(f"template {template} has no __PAYLOAD__ marker")
    data = json.dumps(payload, separators=(",", ":"), allow_nan=False).replace("</", "<\\/")
    return html.replace("__PAYLOAD__", data)


def write_viewer(
    out_path: Path | str, *, results_dir: Path | str | None = None, prefix: str = "t7a_dry_run"
) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render(load_payload(results_dir, prefix)), encoding="utf-8", newline="\n")
    return out_path


__all__ = ["TEMPLATE", "FILES", "load_payload", "render", "write_viewer"]
