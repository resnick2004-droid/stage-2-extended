"""FV3-C's one confirmation on NQ's held-back window (D-355): the frozen inputs at registration, then the verdict, read
once.

    python scripts/confirm_fv3.py --freeze     # after registration, once 2026's release days are on record, before any kit
    python scripts/confirm_fv3.py              # once every period is ingested or recorded unusable: the verdict

Everything it does is `config/fv3_confirmation.yaml` (the periods and their kits R139-R141, the counted-period rule,
the 21-session blocks, the lines C1-C4) over the frozen candidate `config/fv3_corrected_portfolio.yaml` (FV3-C, D-353,
frozen at c561ec9 by D-354), with the development scorer's own machinery imported, never copied or edited: the window's
records are read exactly as `score_fv3_grid.load` reads the development captures (FOMC days out), each period's label
standing in the scorer's opaque `year` slot; the one declared cell's trades (`gate_trades`); each R's net edge pooled
and its one-sided 95 % t bound over the window's 21-session blocks (the development yearly formula on monthly blocks,
D-237 (4)); the gate (`run_gate`, both placements, the denial ladder) at the state table's edge cell nearest the funded
leg's bound; the twins; each counted period's own campaign; the flatten shares (`EvaluatedFV3.flatten_rows`); the lines.

**Refusals:** the registration is not a runnable row of prereg/REGISTRY.md; the frozen inputs' hashes differ from
`config/fv3_confirmation_frozen.json` (written by --freeze, which itself refuses unless the campaign engine and the
scorer equal FV3-C's freeze commit); the tree is dirty; a period is neither ingested nor recorded unusable, or recorded
unusable without its permitted fix having run; a verdict exists (the window is read once). A period unusable twice is a
FAIL written without reading any record (D-230).

**PASS requires C1, C2, C3 and C4 (D-355).** C2 reads each counted period's campaign on its trades' outcomes as measured
(the point arm), as the development walk-forward's P1 did; C1 and C3 read the gate at the bound. Beside the verdict
(D-356): each R's gross edge, cost and net edge (`costs` rows; the cost drag as a fraction of dollars risked). Writes
results/fv3_confirmation.csv and its per-path companion, each with its manifest, `exploratory: false`, the registration's
id. The audit that follows reads it the same way whatever the verdict (D-355 (5)).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

SCRIPT = "scripts/confirm_fv3.py"
CONFIG = ROOT / "config" / "fv3_confirmation.yaml"
FROZEN = ROOT / "config" / "fv3_confirmation_frozen.json"
RESULT = "fv3_confirmation"

#: what the freeze pins (D-355): the campaign engine and the scorer, which must equal FV3-C's freeze commit, and the
#: inputs the verdict reads
ENGINE_PATHS = ("propedge/campaign", "propedge/contract", "propedge/execution", "propedge/outcomes",
                "propedge/reporting/results.py", "scripts/score_fv3_grid.py", "scripts/portfolio_stage.py",
                "scripts/score_orb5_grid.py", "scripts/score_orb3_search.py", "scripts/orb5_exploratory.py",
                "scripts/orb5_prep.py")
INPUT_FILES = ("config/fills.yaml", "config/rules.yaml", "results/stop_band.csv", "results/setups_per_day.csv")
#: D-356 (the gatekeeper's second review): what decides which records of the window are read -- the kits' generator,
#: the parser and the ingest that enforces the order -- pinned by the freeze too (not compared with c561ec9: they were
#: built for the confirmation after it)
WINDOW_FILES = ("propedge/data/fv3_kit.py", "propedge/data/fv3_parser.py", "propedge/data/manual_parsers.py",
                "scripts/ingest_fv3_run.py")


# ------------------------------------------------------------------------------------------------------- the config

def config(path: Path | None = None) -> dict:
    return yaml.safe_load(Path(path or CONFIG).read_text(encoding="utf-8"))


def candidate(conf: dict) -> dict:
    return yaml.safe_load((ROOT / conf["candidate_config"]).read_text(encoding="utf-8"))


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def pinned_files(conf: dict) -> list[str]:
    """Every file the freeze hashes: the engine and the scorer (each .py under ENGINE_PATHS), this script, the two
    configs, the state table the candidate names, the FOMC and release-day sources, the fill and rule ledgers."""
    cand = candidate(conf)
    out: set[str] = set()
    for p in ENGINE_PATHS:
        q = ROOT / p
        if q.is_dir():
            out |= {str(f.relative_to(ROOT)).replace("\\", "/") for f in q.rglob("*.py")}
        else:
            out.add(p)
    out |= {SCRIPT, "config/fv3_confirmation.yaml", str(conf["candidate_config"]), str(cand["state_policy"]["file"]),
            str(cand["state_policy"]["policies_json"]), str(conf["news_2026"]), *map(str, conf["fomc"]), *INPUT_FILES,
            *WINDOW_FILES}
    return sorted(out)


def sha256(path: Path) -> str:
    """The file's sha256 with line endings normalised (CRLF to LF), as `stop_band.input_hashes` hashes: every pinned
    file is text, and a git checkout on this machine (core.autocrlf) may rewrite LF as CRLF without changing a value
    (D-358, the data-integrity report's finding 1)."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def engine_changes(conf: dict) -> list[str]:
    """The engine and scorer paths that differ from FV3-C's freeze commit (tracked changes and untracked files)."""
    commit = str(conf["engine_commit"])
    paths = [*ENGINE_PATHS, str(conf["candidate_config"])]
    changed = [x for x in _git("diff", "--name-only", commit, "--", *paths).splitlines() if x.strip()]
    untracked = [x for x in _git("ls-files", "--others", "--exclude-standard", "--", *paths).splitlines() if x.strip()]
    return sorted(set(changed) | set(untracked))


def freeze(conf: dict, *, path: Path = FROZEN) -> dict:
    """D-355, D-356: after registration, once 2026's release days are on record and before any kit -- the id a runnable
    row, N and the sd written, the engine equal to the freeze commit -- the sha256 of every pinned file, to `path`."""
    from propedge.data.cloud_guard import confirmation_run_authorised

    pid = str(conf.get("prereg_id") or "pending")
    if not confirmation_run_authorised(pid):
        raise SystemExit(f"REFUSED: {pid!r} is not a runnable row of prereg/REGISTRY.md; freeze after registration (D-355).")
    if str(conf.get("ledger_n", "pending")).lower() == "pending" or str(conf.get("assumed_sd", "pending")).lower() == "pending":
        raise SystemExit("REFUSED: ledger_n and assumed_sd must be written into the config before the freeze (D-355).")
    bad = engine_changes(conf)
    if bad:
        raise SystemExit(f"REFUSED: the engine or the candidate differs from FV3-C's freeze {conf['engine_commit']}: "
                         + ", ".join(bad[:12]) + (" ..." if len(bad) > 12 else ""))
    files = {f: sha256(ROOT / f) for f in pinned_files(conf)}
    record = {"prereg": pid, "engine_commit": str(conf["engine_commit"]), "head": _git("rev-parse", "HEAD").strip(),
              "written_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "files": files}
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
    return record


def frozen_problems(conf: dict, path: Path = FROZEN) -> list[str]:
    """The pinned files whose hash differs from the frozen record (or why the record cannot be read)."""
    if not path.is_file():
        return [f"{path.name} does not exist: run --freeze at registration"]
    rec = json.loads(path.read_text(encoding="utf-8"))
    out = []
    if rec.get("prereg") != str(conf.get("prereg_id")):
        out.append(f"the frozen record names {rec.get('prereg')!r}, the config {conf.get('prereg_id')!r}")
    want = rec.get("files", {})
    have = set(pinned_files(conf))
    for f in sorted(have | set(want)):
        p = ROOT / f
        if f not in want:
            out.append(f"{f}: pinned now, not in the frozen record")
        elif not p.is_file():
            out.append(f"{f}: missing")
        elif sha256(p) != want[f]:
            out.append(f"{f}: changed since the freeze")
    return out


# ------------------------------------------------------------------------------------------------------ the periods

def judged_mismatch(run_dir: Path) -> str:
    """D-356: '' when the run saved is the backtest judged usable -- `usable.json` present, its backtest id and the
    sha256 of its downloaded files equal to `ingested.json`'s; else why not."""
    u, i = run_dir / "usable.json", run_dir / "ingested.json"
    if not u.is_file():
        return "saved without a usability judgement (usable.json); every period is judged before any record is saved"
    ju, ji = (json.loads(f.read_text(encoding="utf-8")) for f in (u, i))
    if str(ju.get("qc_backtest_id")) != str(ji.get("qc_backtest_id")):
        return "the backtest saved is not the backtest judged usable"
    if not ju.get("downloads_sha256") or ju.get("downloads_sha256") != ji.get("downloads_sha256"):
        return "the files saved are not the files judged usable (their sha256 differ or are missing)"
    return ""


def period_state(p: dict, results_dir: Path, runs_dir: Path) -> tuple[str, str | None, str]:
    """(state, the run to read, why): `ingested` (that run), `unusable` (both permitted runs unusable: a FAIL),
    `pending` (not yet run, or unusable with its fix still to run)."""
    runs = [str(p["run"])] + ([str(p["fix_run"])] if p.get("fix_run") else [])
    ing = [r for r in runs if (runs_dir / r / "ingested.json").is_file()
           and (results_dir / f"manual_{r.replace('-', '_')}.csv").is_file()]
    bad = [r for r in runs if (runs_dir / r / "unusable.json").is_file()]
    both = sorted(set(ing) & set(bad))
    if both:
        return "pending", None, f"{', '.join(both)} is recorded unusable and also ingested; an unusable run is never read"
    if ing:
        if len(ing) > 1:
            return "pending", None, f"two runs ingested for period {p['id']}: {ing}"
        if ing[0] != runs[0] and runs[0] not in bad:
            return "pending", None, f"{ing[0]} is ingested but {runs[0]} is not recorded unusable; the fix runs only after it"
        why = judged_mismatch(runs_dir / ing[0])
        if why:
            return "pending", None, f"{ing[0]}: {why}"
        return "ingested", ing[0], ""
    if len(bad) >= 2:
        return "unusable", None, f"period {p['id']}: both permitted runs unusable (D-230)"
    if bad:
        return "pending", None, f"period {p['id']}: {bad[0]} is unusable and its fix has not run (a decision declares it)"
    return "pending", None, f"period {p['id']}: {runs[0]} is neither ingested nor recorded unusable"


def load_window(conf: dict, cand: dict, chosen: dict[str, str], results_dir: Path, runs_dir: Path):
    """(signals, sessions, bench, sessions per period label, the window's trading days, each day's label): the counted
    and uncounted periods' records read exactly as `score_fv3_grid.load` reads the development captures -- FOMC days
    out, a record outside its period's dates refused."""
    import score_orb3_search as s3

    frames, cells, label_of_day, sessions_by = [], [], {}, {}
    for p in conf["periods"]:
        run = chosen.get(str(p["id"]))
        if run is None:
            continue
        t = pd.read_csv(results_dir / f"manual_{run.replace('-', '_')}.csv", low_memory=False)
        rec = t[t["kind"] != "session"].copy()
        rec["date"] = rec["date"].astype(str)
        lo, hi = str(p["start"]), str(p["end"])
        if len(rec) and (rec["date"].min() < lo or rec["date"].max() > hi):
            raise SystemExit(f"REFUSED: {run} holds a record outside its period {lo}..{hi} (D-355).")
        frames.append(rec)
        c = t[t["kind"] == "session"]
        early = int(json.loads((runs_dir / run / "ingested.json").read_text(encoding="utf-8"))["summary"]["early"])
        full = float(c["days"].sum())
        sessions_by[int(p["label"])] = full + float(early)             # s3.trading_days's rule, keyed by the period
        cells.append(c)
        for d in rec[rec["kind"] == "day"]["date"]:
            label_of_day[str(d)] = int(p["label"])
    if not frames:
        raise SystemExit("REFUSED: no period's records to read.")
    a = pd.concat(frames, ignore_index=True)
    if a[a["kind"] == "day"]["date"].duplicated().any():
        raise SystemExit("REFUSED: a day recorded twice across the periods.")
    a = a[~a["date"].isin(s3.fomc_dates({"fomc": conf["fomc"]}))]
    days = a[a["kind"] == "day"][["date", "base_stop_ticks", "news_day"]]
    ses = a[a["kind"] == "fvsession"].drop(columns=["base_stop_ticks", "news_day"], errors="ignore").merge(
        days, on="date", how="left", validate="many_to_one")
    heads = ses[["date", "session", "stop_ticks", "open_body_ticks", "open_dir"]].rename(
        columns={"stop_ticks": "base_ticks", "open_body_ticks": "open_body", "open_dir": "open_dir_s"})
    drop = ["stop_ticks", "base_stop_ticks", "news_day", "open_body_ticks", "open_dir"]
    sig = a[a["kind"] == "signal"].drop(columns=drop, errors="ignore").merge(heads, on=["date", "session"], how="left",
                                                                            validate="many_to_one")
    bench = a[a["kind"] == "bench"].drop(columns=drop, errors="ignore").merge(heads, on=["date", "session"], how="left",
                                                                             validate="many_to_one")
    if sig["base_ticks"].isna().any() or bench["base_ticks"].isna().any():
        raise SystemExit("REFUSED: a signal or benchmark row without its session's base stop.")
    window_days = sorted(set(ses["date"].astype(str)))
    return sig, ses, bench, sessions_by, window_days, label_of_day


# -------------------------------------------------------------------------------------------------- the statistics

def bound_at(values: pd.Series, alpha: float) -> float:
    """The one-sided (1 - alpha) t bound of the mean of `values` (the development `bound` at alpha 0.05)."""
    from scipy import stats

    y = values.dropna().astype(float)
    if len(y) < 2:
        return float("nan")
    return float(y.mean() - stats.t.ppf(1.0 - alpha, len(y) - 1) * y.std(ddof=1) / math.sqrt(len(y)))


def block_of(dates: pd.Series, window_days: list[str], block_days: int) -> np.ndarray:
    """Each date's 21-session block: its position among the window's trading days, integer-divided."""
    pos = {d: i for i, d in enumerate(window_days)}
    idx = dates.astype(str).map(pos)
    if idx.isna().any():
        raise SystemExit("REFUSED: a trade on a day outside the window's trading days.")
    return (idx.astype(int).to_numpy() // int(block_days)).astype(int)


def edge_stats(t: pd.DataFrame, menu: list[float], window_days: list[str], block_days: int, n_trials: int | None
               ) -> dict[float, dict[str, float]]:
    """Each R's net edge pooled over the window, its one-sided 95 % bound over the 21-session blocks, and (D-189,
    beside) its bound at one-sided 0.05/N."""
    blk = pd.Series(block_of(t["date"], window_days, block_days), index=t.index) if len(t) else pd.Series(dtype=int)
    out = {}
    for R in menu:
        v = t[f"r_{R:g}"].dropna() if len(t) else pd.Series(dtype=float)
        by = v.groupby(blk.loc[v.index]).mean() if len(v) else pd.Series(dtype=float)
        out[float(R)] = {"e": float(v.mean()) if len(v) else float("nan"), "lb": bound_at(by, 0.05), "n": int(len(v)),
                         "blocks": int(len(by)), "sd": float(v.std(ddof=1)) if len(v) > 1 else float("nan"),
                         "lb_at_n": bound_at(by, 0.05 / float(n_trials)) if n_trials else float("nan")}
    return out


def cost_rows(S, ev, sels: dict, cand: dict, menu: list[float], t: pd.DataFrame, label_of: dict[int, str]) -> list[dict]:
    """D-356 (the gatekeeper's finding 3; the template's 'cost drag as a fraction of dollars risked'): for the gate's
    trades, each R's gross edge, cost and net edge in units of intended risk at the fresh Combine's size -- the cost
    each trade's outcome at that R took, `gate_trades`' own (`Signals3.outcome`) -- pooled and per period at the two
    fresh legs' R; the net checked equal to the gate's trades. The engine re-prices the fee at the contracts a trade
    holds (D-324); the campaign rows carry the fees paid."""
    import score_fv3_grid as gf

    c_spec = gf.leg_spec(cand, "combine")
    fresh = cand["state_policy"]["fresh"]
    legs = {float(fresh["combine_rr"]), float(fresh["funded_rr"])}
    parts: dict[float, list[tuple[int, float, float]]] = {float(R): [] for R in menu}
    dates: list[str] = []
    for y, k in sels.items():
        if k is None:
            continue
        c = ev.cells[k]
        cand_ = S.candidates(c)
        rung = S.rung(bool(c["double_rung_reversions"]))
        base = S.outcome(rung, "r", c_spec[1], c_spec[2], c_spec[3])
        kept = S.kept(cand_ & base["permitted"], base["exit"], base["stopped"],
                      two_losses_bos_only=(c["displacement"] == "rule")) & (S.year == y)
        idx = np.nonzero(kept)[0]
        dates += [str(S.df["date"].iat[i]) for i in idx]
        for R in menu:
            o = S.outcome(rung, "r", float(R), c_spec[2], c_spec[3])
            parts[float(R)] += [(int(y), float(o["gross"][i]), float(o["cost"][i])) for i in idx if o["permitted"][i]]
    if dates != (list(t["date"].astype(str)) if len(t) else []):
        raise SystemExit("REFUSED: the cost rows' trades differ from the gate's trades.")
    rows = []
    for R in menu:
        a = pd.DataFrame(parts[float(R)], columns=["year", "gross", "cost"])
        net = (a["gross"] - a["cost"]).to_numpy()
        want = t[f"r_{R:g}"].dropna().to_numpy() if len(t) else np.zeros(0)
        if len(net) != len(want) or not np.allclose(net, want):
            raise SystemExit(f"REFUSED: the cost rows' net at {R:g}R differs from the gate's trades.")
        groups = [("all", a)] + ([(label_of[int(y)], g) for y, g in a.groupby("year")] if float(R) in legs else [])
        for name, g in groups:
            rows.append({"section": "costs", "rr": float(R), "period": name, "n": int(len(g)),
                         "gross_e": float(g["gross"].mean()) if len(g) else float("nan"),
                         "cost_r": float(g["cost"].mean()) if len(g) else float("nan"),
                         "net_e": float((g["gross"] - g["cost"]).mean()) if len(g) else float("nan"),
                         "basis": "units of intended risk at the fresh Combine's size; cost_r is the cost drag as a "
                                  "fraction of dollars risked"})
    return rows


# ----------------------------------------------------------------------------------------------------------- lines

def lines(gdf: pd.DataFrame, period_rows: list[dict], flatten: list[dict], cand: dict, conf: dict) -> tuple[dict, dict]:
    """C1-C4 (D-355) from the gate rows, the counted periods' campaigns and the flatten rows; the values beside."""
    import score_fv3_grid as gf

    pcfg = cand["portfolio"]
    gcol = "pf_growth_on_base_p50" if gf.bankroll_output(cand) else "median_log_growth"
    off = gdf[gdf["placement"].astype(str) == "off"]
    g = off[off["is_gate_row"].astype(str) == "True"].iloc[0]
    d10 = float(pcfg.get("gate_denial_still_positive", 0.10))
    g10 = off[(off["shift"] == "lower_bound") & np.isclose(off["enforcement_p"].astype(float), d10)]
    counted = [r for r in period_rows if r["counted"]]
    fmax = float(conf["flatten_share_max"])
    fl_all = {r["leg"]: r["share"] for r in flatten if r["year"] == "all"}
    fl_counted = [r for r in flatten if r["year"] != "all" and int(r["year"]) in {int(c["label"]) for c in counted}]
    capped = gf.fidelity_of(cand)["intended"] == "capped"
    v = {"growth_basis": "the required bankroll at p90 (D-312)" if gf.bankroll_output(cand) else "the stated bankroll",
         "C1_growth": float(g.get(gcol, float("nan"))),
         "C1_required_p50": float(g.get("pf_required_p50", float("nan"))),
         "C1_required_p90": float(g.get("pf_required_p90", float("nan"))),
         "C1_required_p99": float(g.get("pf_required_p99", float("nan"))),
         "C1_required_worst": float(g.get("pf_required_worst", float("nan"))),
         "C2_counted_periods": ",".join(str(c["id"]) for c in counted),
         "C2_growth_min": float(min((c.get("growth", float("nan")) for c in counted), default=float("nan"))),
         "C2_activity_min": float(min((c.get("activity", float("nan")) for c in counted), default=float("nan"))),
         "C2_sharpe_flip_max": float(max((c.get("sharpe_flip", float("nan")) for c in counted), default=float("nan"))),
         "C3_break_even_denial": float(g.get("pf_break_even_denial_p50", float("nan"))),
         "C3_gate_at_denial": float(g10[gcol].iloc[0]) if len(g10) and gcol in g10 else float("nan"),
         "C4_realised_to_intended": float(g.get("pf_realised_to_intended_capped" if capped else "pf_realised_to_intended",
                                               float("nan"))),
         "C4_realised_to_intended_raw": float(g.get("pf_realised_to_intended", float("nan"))),
         "C4_flatten_combine": float(fl_all.get("combine", float("nan"))),
         "C4_flatten_funded": float(fl_all.get("funded", float("nan"))),
         "C4_flatten_max_counted_period": float(max((r["share"] for r in fl_counted if r["share"] == r["share"]),
                                                    default=float("nan"))),
         "C4_counted_periods": len(counted),
         "C4_counted_periods_without_trade": ",".join(str(c["id"]) for c in counted if not c["trades"])}

    def ok(x: float, test) -> bool:
        return bool(np.isfinite(x) and test(x))

    c2 = bool(counted) and all(ok(c.get("growth", float("nan")), lambda x: x > 0)
                               and ok(c.get("activity", float("nan")), lambda x: x > 0.5)
                               and ok(c.get("sharpe_flip", float("nan")), lambda x: x == 0) for c in counted)
    flat_ok = (all(ok(fl_all.get(leg, float("nan")), lambda x: x <= fmax + 1e-12) for leg in ("combine", "funded"))
               and all(r["share"] != r["share"] or r["share"] <= fmax + 1e-12 for r in fl_counted))
    out = {"C1": ok(v["C1_growth"], lambda x: x > 0),
           "C2": c2,
           "C3": ok(v["C3_break_even_denial"], lambda x: x >= float(pcfg["break_even_denial_min"]))
                 and ok(v["C3_gate_at_denial"], lambda x: x > 0),
           "C4": ok(v["C4_realised_to_intended"], lambda x: x >= float(pcfg["realised_to_intended_min"]))
                 and flat_ok and not v["C4_counted_periods_without_trade"]
                 and len(counted) >= int(conf["counted_periods_min"])}
    return out, v


# ------------------------------------------------------------------------------------------------------------ main

def _fail_unreadable(conf: dict, why: list[str], results_dir: Path | None, rd: Path) -> int:
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import write_result

    pid = str(conf["prereg_id"])
    out = pd.DataFrame([{"section": "summary", "verdict": "FAIL", "reason": "; ".join(why), "prereg": pid}])
    counter = VariantCounter(path=rd / "variants.jsonl")
    counter.record(prereg_id=pid, seed=0, exploratory=False,
                   params={"study": "FV3-C confirmation", "candidate_config": conf["candidate_config"], "market": "NQ",
                           "window": conf["window"], "result": RESULT},
                   label=f"FV3-C's one confirmation on NQ's held-back window ({pid}): a period unusable twice")
    write_result(out, RESULT, script=SCRIPT, seed=None, require_seed=False, exploratory=False, prereg_id=pid,
                 results_dir=results_dir, provenance={"prereg": pid}, variant_count=counter.count(pid),
                 parameters={"config": "config/fv3_confirmation.yaml", "prereg": pid},
                 notes={"status": f"PRE-REGISTERED ({pid}): FAIL, a period unusable twice -- no record read"},
                 description=f"FV3-C's confirmation under {pid}: FAIL, a period unusable twice (D-230, D-355).")
    print(f"VERDICT ({pid}): FAIL -- " + "; ".join(why))
    return 0


def main(argv: list[str] | None = None, *, results_dir: Path | None = None, runs_dir: Path | None = None,
         config_path: Path | None = None, checks: bool = True, n_paths: int | None = None,
         horizon_days: int | None = None, period_paths: int | None = None, reproduce: Path | None = None) -> int:
    """`checks` False (tests only) skips the registry, the frozen hashes and the clean tree; `n_paths`, `horizon_days`
    and `period_paths` (tests only) shrink the campaigns. `reproduce` (R11, `scripts/reproduce_registered.py` only) is
    a directory outside the repository: the completed registration's computation rerun from the same inputs, without
    the registry, frozen-hash, clean-tree and read-once checks and the variant ledger's append, its files written there
    by `propedge.reporting.reproduction.writer`, exploratory and labelled a reproduction. The command line exposes none
    of them."""
    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.data.cloud_guard import confirmation_run_authorised
    from propedge.data.orb_kit import params
    from propedge.execution.fills import FillModel
    from propedge.reporting.results import read_result, write_result
    from propedge.research.model_card import BAND_FILE, setups_minimum

    import portfolio_stage as ps
    import score_fv3_grid as gf

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--freeze", action="store_true", help="at registration: write the frozen inputs' hashes")
    a = ap.parse_args(argv)
    conf = config(config_path)
    if a.freeze:
        rec = freeze(conf)
        print(f"froze {len(rec['files'])} files for {rec['prereg']} at {rec['head'][:7]} -> {FROZEN.relative_to(ROOT)}")
        return 0
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    rund = Path(runs_dir) if runs_dir is not None else ROOT / "runs"
    pid = str(conf.get("prereg_id") or "pending")
    if reproduce is not None:                              # R11: checked before any work; the same call, relabelled
        from propedge.reporting.reproduction import writer

        write_result = writer(pid, reproduce)              # noqa: F811 -- outside the repository, exploratory
    if checks and reproduce is None:
        if not confirmation_run_authorised(pid):
            print(f"REFUSED: {pid!r} is not a runnable row of prereg/REGISTRY.md (D-81, D-355).")
            return 2
        bad = frozen_problems(conf)
        if bad:
            print("REFUSED: the frozen inputs differ: " + "; ".join(bad[:10]))
            return 2
        if _git("status", "--porcelain").strip():
            print("REFUSED: the tree is dirty; the verdict is computed from a clean tree.")
            return 2
    if reproduce is None and (rd / f"{RESULT}.csv").exists():
        print(f"REFUSED: {RESULT}.csv exists; the held-back window is read once (D-237, D-355).")
        return 2
    states = {str(p["id"]): period_state(p, rd, rund) for p in conf["periods"]}
    unusable = [why for s, _, why in states.values() if s == "unusable"]
    if unusable:                                              # D-230: a period unusable twice is a FAIL; nothing read
        if reproduce is not None:                             # a reproduction writes no verdict
            print("REFUSED (reproduction): " + "; ".join(unusable) + ".")
            return 2
        return _fail_unreadable(conf, unusable, results_dir, rd)
    pending = [why for s, _, why in states.values() if s == "pending"]
    if pending:
        print("REFUSED: " + "; ".join(pending) + ".")
        return 2
    chosen = {k: run for k, (s, run, _) in states.items() if s == "ingested"}

    cand = candidate(conf)
    if int(cand["k"]) != 1:
        print("REFUSED: the frozen candidate must be one declared cell (k = 1).")
        return 2
    sig, ses, bench, sessions_by, window_days, label_of_day = load_window(conf, cand, chosen, rd, rund)
    fm = FillModel.load("assumed")
    q = params("NQ")
    tv = q["micro_tick"] * q["micro_point_value"]
    S = gf.Signals3(sig, float(fm.round_turn_by_instrument[q["micro"]]), float(fm.round_turn_by_instrument["NQ"]), tv,
                    cand["ladder"])
    S.year = np.array([label_of_day[str(d)] for d in S.df["date"]], dtype=int)   # each period's label in the year slot
    fresh = cand["state_policy"]["fresh"]
    need = setups_minimum(float(fresh["combine_rr"]), float(fresh["combine_risk"]), 0.0)
    ev = gf.EvaluatedFV3(S, ses, cand, sessions_by, read_result(BAND_FILE), float(need))
    final = ev.cells[0]
    sels = {int(y): 0 for y in ev.years}
    t = gf.gate_trades(S, ev, sels, final)
    menu = [float(R) for R in gf.rr_menu(cand)]
    n_trials = None if str(conf.get("ledger_n", "pending")).lower() == "pending" else int(conf["ledger_n"])
    stats = edge_stats(t, menu, window_days, int(conf["block_days"]), n_trials)
    rows: list[dict[str, Any]] = []
    for R in menu:
        s = stats[R]
        rows.append({"section": "gate_inputs", "rr": R, "oos_trades": s["n"], "e": s["e"], "lb": s["lb"],
                     "blocks": s["blocks"], "sd": s["sd"], "lb_at_n": s["lb_at_n"], "n_trials": n_trials})
        rows.append({"section": "criterion", "rr": R, "e": s["e"], "lb": s["lb"], "e_min": gf.D47_E_MIN,
                     "lb_min": gf.D47_LB_MIN, "met": bool(np.isfinite(s["e"]) and np.isfinite(s["lb"])
                                                          and s["e"] >= gf.D47_E_MIN and s["lb"] >= gf.D47_LB_MIN)})
    rows += cost_rows(S, ev, sels, cand, menu, t, {int(p["label"]): str(p["id"]) for p in conf["periods"]})
    flatten = ev.flatten_rows(0)
    rows += flatten
    paths_rows: list[dict] = []
    camp = cand["gate"]["campaign"]
    if n_paths is not None or horizon_days is not None or period_paths is not None:     # tests only
        cand = {**cand, "gate": {**cand["gate"], "campaign": {**camp, "n_paths": int(n_paths or camp["n_paths"]),
                                                                "horizon_days": int(horizon_days or camp["horizon_days"])}},
                "portfolio": {**cand["portfolio"], "walkforward_paths": int(period_paths or cand["portfolio"]["walkforward_paths"])}}
    seed = int(cand["seeds"]["gate"])
    fr = float(fresh["funded_rr"])
    lb_f = stats[fr]["lb"]
    period_rows: list[dict] = []
    gdf = None
    blocks = None
    if len(t) and np.isfinite(lb_f):
        blocks, n_used = gf.gate_blocks(t, window_days, tv, menu, require_sides=True, require_exits=True)
        if n_used != len(t):
            print("REFUSED: the blocks hold a different number of trades.")
            return 2
        policy, e_used, pol_id = gf.policy_for_edge(cand, lb_f)
        hook = ps.composed_hook(cand["portfolio"], sink=paths_rows)
        gdf, _ = gf.run_gate(blocks, stats, policy, cand, seed, tv, path_hook=hook)
        for _, gr in gdf.iterrows():
            rows.append({"section": "gate", "policy_id": pol_id, "policy_edge": e_used,
                         **{kk: vv for kk, vv in gr.items() if not isinstance(vv, (list, dict))}})
        rows += ps.twins(blocks, stats, cand, seed, tv, policy, hook)
        e_by, lb_by = ps._by(stats, "e"), ps._by(stats, "lb")
        for p in conf["periods"]:
            lab = int(p["label"])
            days_p = [d for d in window_days if label_of_day.get(d) == lab]
            tp = t[t["year"] == lab]
            pr = {"id": str(p["id"]), "label": lab, "run": chosen.get(str(p["id"])), "days": len(days_p),
                  "counted": len(days_p) >= int(conf["period_min_days"]), "trades": int(len(tp))}
            if days_p and len(tp):
                bp, _ = gf.gate_blocks(tp, days_p, tv, menu, require_sides=True, require_exits=True)
                ps._label(hook, f"period {p['id']}")
                df = ps.run_campaign(bp, cand, seed, tv, policy, e=e_by[fr], lb=lb_by[fr], e_by=e_by, lb_by=lb_by,
                                     levels=(0.0,), n_paths=int(cand["portfolio"]["walkforward_paths"]),
                                     horizon=len(days_p), hook=hook)
                r = df[df["shift"] == "point"].iloc[0]
                gcol = "pf_growth_on_base_p50" if gf.bankroll_output(cand) else "median_log_growth"
                pr.update({"growth": float(r.get(gcol, float("nan"))),
                           "activity": float(r.get("pf_activity_bound_p50", float("nan"))),
                           "sharpe_flip": float(r.get("pf_share_sharpe_sign_changed_without_idle", float("nan")))})
                rows.append({"section": "period_campaign", **pr,
                             **{kk: vv for kk, vv in r.items() if not isinstance(vv, (list, dict)) and kk not in pr}})
            period_rows.append(pr)
            rows.append({"section": "period", **pr})
    else:
        for p in conf["periods"]:
            lab = int(p["label"])
            days_p = [d for d in window_days if label_of_day.get(d) == lab]
            pr = {"id": str(p["id"]), "label": lab, "run": chosen.get(str(p["id"])), "days": len(days_p),
                  "counted": len(days_p) >= int(conf["period_min_days"]), "trades": int((t["year"] == lab).sum()) if len(t) else 0}
            period_rows.append(pr)
            rows.append({"section": "period", **pr})
    if gdf is not None:
        ok, values = lines(gdf, period_rows, flatten, cand, conf)
        why = ""
    else:
        ok = {"C1": False, "C2": False, "C3": False, "C4": False}
        values = {}
        why = "the result cannot be computed: no trade in the window or the funded leg's bound undefined (a FAIL)"
    for ln in ("C1", "C2", "C3", "C4"):
        rows.append({"section": "line", "line": ln, "passed": bool(ok[ln]), "rule": conf["lines"][ln],
                     **{k: v for k, v in values.items() if k.startswith(ln)}})
    # beside the verdict, never as it: the funded leg's edge series' deflated Sharpe over the blocks at the ledger's N,
    # and the realised per-trade sd at the fresh Combine's R against the registered assumption
    from propedge.research.haircut import deflated_sharpe

    blk_series = (t.assign(_b=block_of(t["date"], window_days, int(conf["block_days"])))
                  .groupby("_b")[f"r_{fr:g}"].mean().dropna().to_numpy()) if len(t) else np.zeros(0)
    dsr = deflated_sharpe(blk_series, int(n_trials)) if n_trials else {"dsr": float("nan")}
    cr = float(fresh["combine_rr"])
    verdict = "PASS" if all(ok.values()) else "FAIL"
    rows.append({"section": "summary", "verdict": verdict, "failed_lines": ",".join(k for k, x in ok.items() if not x),
                 "reason": why, "prereg": pid, "model": str(conf["model"]),
                 "counted_periods": sum(1 for r in period_rows if r["counted"]),
                 "window_days": len(window_days), "window_first": window_days[0] if window_days else "",
                 "window_last": window_days[-1] if window_days else "",
                 "trades": int(len(t)), "deflated_sharpe_funded_blocks": float(dsr.get("dsr", float("nan"))),
                 "n_trials": n_trials, "realised_sd_combine_rr": stats[cr]["sd"],
                 "assumed_sd": conf.get("assumed_sd"),
                 "d47_criterion_met_any_rr": bool(any(r.get("met") for r in rows if r.get("section") == "criterion")),
                 "paths_file": f"{RESULT}_paths.csv" if paths_rows else ""})
    out = pd.DataFrame(rows)
    frozen_sha = sha256(FROZEN) if FROZEN.is_file() else None
    status = f"PRE-REGISTERED ({pid}): FV3-C's one confirmation on NQ's held-back window, read once (D-355)"
    # the run in the variant ledger before its result is written (D-334's order): one configuration, the frozen candidate
    counter = VariantCounter(path=rd / "variants.jsonl")
    if reproduce is None:                                     # a reproduction is not a configuration tried (R11)
        counter.record(prereg_id=pid, seed=seed, exploratory=False,
                       params={"study": "FV3-C confirmation", "candidate_config": conf["candidate_config"],
                               "market": "NQ", "window": conf["window"], "result": RESULT},
                       label=f"FV3-C's one confirmation on NQ's held-back window ({pid})")
    n_var = counter.count(pid)
    write_result(out, RESULT, script=SCRIPT, seed=seed, exploratory=False, prereg_id=pid, results_dir=results_dir,
                 variant_count=n_var, provenance={"prereg": pid, "engine_commit": str(conf["engine_commit"]),
                                              "frozen_record_sha256": frozen_sha, "runs": chosen},
                 parameters={"config": "config/fv3_confirmation.yaml", "candidate_config": conf["candidate_config"],
                             "prereg": pid, "periods": conf["periods"], "block_days": conf["block_days"],
                             "period_min_days": conf["period_min_days"], "lines": conf["lines"], "seed": seed},
                 notes={"status": status},
                 description=f"FV3-C's confirmation under {pid}: the gate, each counted period's campaign and the lines "
                             "C1-C4 on NQ's held-back window, read once (D-355).")
    if paths_rows:
        write_result(pd.DataFrame(paths_rows), f"{RESULT}_paths", script=SCRIPT, seed=seed, exploratory=False,
                     prereg_id=pid, results_dir=results_dir, variant_count=n_var,
                     parameters={"result": f"{RESULT}.csv", "prereg": pid},
                     notes={"status": status, "companion_of": f"{RESULT}.csv"},
                     description=f"The per-path record of {RESULT}.csv: every resampled path of every campaign the "
                                 "confirmation ran, so its lines can be re-derived from the files.")
    head = "REPRODUCTION, not a verdict" if reproduce is not None else "VERDICT"
    print(f"{head} ({pid}): {verdict} -- " + ", ".join(f"{k} {'met' if x else 'NOT met'}" for k, x in ok.items())
          + (f" ({why})" if why else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
