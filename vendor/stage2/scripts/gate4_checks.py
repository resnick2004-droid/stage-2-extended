"""EXPLORATORY (D-386; D-382 (B)): the deployment protocol's Gate 4 additions on FV3-C's record -- read beside it, no
gate line changes and nothing is selected by them.

    python scripts/gate4_checks.py              # writes results/fv3c_gate4.csv

* **The screen, checked first** (`screen_check`): FV3's declared screen (config/fv3_grid.yaml, k 32) rebuilt by its
  scorer's own functions from its twenty captures; its 32 grid values and its walk-forward rows must equal
  results/fv3_grid_corrected.csv, or the script refuses.
* **PBO** (`pbo`, `pbo_matrix`): combinatorially symmetric cross-validation over the sixteen years 2010-2025 -- for each
  split into two halves of eight, the screen's own selection on one half and the pick's rank among the cells feasible
  on the other by the same value; PBO is the share of splits whose rank logit is at most zero (a pick infeasible out of
  sample counts as overfit).
* **The plateau audit** (`plateau`): the screen's final cell against every cell one axis away.
* **The literal label shuffle** (`shuffle`): whole trading days reassigned to the screen's years at random, every year
  keeping its count of days, and the screen's walk-forward rerun; p is the share of shuffles at or above the actual.
* **The deflated Sharpe** (`dsr`): P-06's statistic on FV3-C's development record at the trial ledger's N and at the
  variant ledger's count.
* **The standing readings** (`standing`): the longest losing streak per R beside the expected longest; the skew of the
  21-session block means at the fresh funded R.
"""
from __future__ import annotations

import argparse
import copy
import itertools
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/gate4_checks.py"
SCREEN_CONFIG = ROOT / "config" / "fv3_grid.yaml"
SCREEN_RESULT = "fv3_grid_corrected.csv"
FV3C_CONFIG = ROOT / "config" / "fv3_corrected_portfolio.yaml"
PBO_YEARS = tuple(range(2010, 2026))
SHUFFLES, SEED, BLOCK_DAYS = 1000, 20261017, 21
LEGS = ("combine", "funded")


# --------------------------------------------------------------------------------------------- the screen, rebuilt

def build_screen(rd: Path, runs_dir: Path | None = None):
    """(config, Signals3, EvaluatedFV3) exactly as `score_fv3_grid.main` builds them for the declared screen."""
    import score_fv3_grid as gf

    from propedge.data.orb_kit import params
    from propedge.execution.fills import FillModel
    from propedge.reporting.results import read_result
    from propedge.research.model_card import BAND_FILE, setups_minimum

    cfg = gf.config(SCREEN_CONFIG)
    fresh = cfg["state_policy"]["fresh"]
    need = setups_minimum(float(fresh["combine_rr"]), float(fresh["combine_risk"]), 0.0)
    sig, ses, _bench, sessions = gf.load(rd, runs_dir or ROOT / "runs", cfg)
    fm = FillModel.load("assumed")
    q = params("NQ")
    S = gf.Signals3(sig, float(fm.round_turn_by_instrument[q["micro"]]), float(fm.round_turn_by_instrument["NQ"]),
                    q["micro_tick"] * q["micro_point_value"], cfg["ladder"])
    ev = gf.EvaluatedFV3(S, ses, cfg, sessions, read_result(BAND_FILE), float(need))
    return cfg, S, ev


def key_of(c: dict) -> dict:
    return {"sessions": "+".join(c["sessions"]), "continuation": bool(c["continuation"]),
            "displacement": str(c["displacement"]), "double_rung_reversions": bool(c["double_rung_reversions"])}


def walkforward(ev, first: int) -> list[tuple[int, int | None, float]]:
    """The screen's walk-forward: (test year, pick, its value in that year) for every year from `first`."""
    out = []
    for T in [int(y) for y in ev.years if y >= first]:
        k, _ = ev.select(ev.years < T)
        out.append((T, k, float(ev.year_value(k, T)) if k is not None else float("nan")))
    return out


def screen_check(ev, cfg: dict, recorded: pd.DataFrame) -> list[dict]:
    """The rebuilt screen against its record: every cell's value and feasibility, every walk-forward row."""
    rows = []
    ok_all, v_all = ev.values(np.ones(len(ev.years), bool))
    grid = recorded[recorded["section"].astype(str) == "grid"]
    for k, c in enumerate(ev.cells):
        kk = key_of(c)
        m = grid[(grid["sessions"].astype(str) == kk["sessions"])
                 & (grid["continuation"].astype(str) == str(kk["continuation"]))
                 & (grid["displacement"].astype(str) == kk["displacement"])
                 & (grid["double_rung_reversions"].astype(str) == str(kk["double_rung_reversions"]))]
        rec = float(m.iloc[0]["value"]) if len(m) == 1 else float("nan")
        same = len(m) == 1 and ((np.isnan(rec) and np.isnan(v_all[k])) or abs(rec - float(v_all[k])) < 1e-9)
        rows.append({"section": "screen_check", "kind": "grid", **kk, "value": float(v_all[k]), "recorded": rec,
                     "equal": bool(same)})
    wf = recorded[recorded["section"].astype(str) == "walkforward"]
    first = int(cfg["selection"]["walkforward"]["first_test_year"])
    for T, k, val in walkforward(ev, first):
        m = wf[wf["test_year"].astype(float) == float(T)]
        rec = float(m.iloc[0]["oos_value"]) if len(m) == 1 else float("nan")
        pick = key_of(ev.cells[k])["sessions"] if k is not None else None
        same = len(m) == 1 and str(m.iloc[0]["sessions"]) == str(pick) and abs(rec - val) < 1e-9
        rows.append({"section": "screen_check", "kind": "walkforward", "test_year": T, "value": val, "recorded": rec,
                     "equal": bool(same)})
    return rows


# --------------------------------------------------------------------------------------------------------- PBO

def pbo(ev, years=PBO_YEARS) -> tuple[list[dict], list[dict]]:
    """CSCV over `years` (an even count present in the screen): per split the in-sample pick (`ev.select`) and its rank
    logit among the cells feasible out of sample by the same value; (summary rows, the matrix rows)."""
    yrs = [int(y) for y in ev.years]
    use = [y for y in years if y in yrs]
    if len(use) % 2 or len(use) < 4:
        raise ValueError(f"CSCV needs an even number of blocks, at least four; got {len(use)}")
    pos = {y: yrs.index(y) for y in use}
    half = len(use) // 2
    logits, oos_vals, picks, skipped = [], [], [], 0
    for comb in itertools.combinations(range(len(use)), half):
        is_m, oos_m = np.zeros(len(yrs), bool), np.zeros(len(yrs), bool)
        for i, y in enumerate(use):
            (is_m if i in comb else oos_m)[pos[y]] = True
        k, _ = ev.select(is_m)
        if k is None:
            skipped += 1
            continue
        ok, v = ev.values(oos_m)
        feas = ok & np.isfinite(v)
        picks.append(int(k))
        if not feas[k]:
            logits.append(-np.inf)
            oos_vals.append(float(v[k]) if np.isfinite(v[k]) else float("nan"))
            continue
        vals = v[feas]
        rank = float((vals < v[k]).sum()) + 0.5 * float((vals == v[k]).sum() - 1) + 1.0     # 1 = the worst
        w = rank / (len(vals) + 1.0)
        logits.append(math.log(w / (1.0 - w)))
        oos_vals.append(float(v[k]))
    lg = np.array(logits, float)
    ov = np.array(oos_vals, float)
    n = len(lg)
    summary = [{"section": "pbo", "years": f"{use[0]}-{use[-1]}", "blocks": len(use), "splits": n + skipped,
                "splits_without_a_pick": skipped, "pbo": float(np.mean(lg <= 0)) if n else float("nan"),
                "share_pick_negative_oos": float(np.mean(ov[np.isfinite(ov)] < 0)) if np.isfinite(ov).any() else float("nan"),
                "share_pick_infeasible_oos": float(np.mean(~np.isfinite(lg))) if n else float("nan"),
                "distinct_picks": len(set(picks)), "line_reference": "PBO below 0.5; below 0.2 (the reference's two lines)",
                "below_0_5": bool(n and np.mean(lg <= 0) < 0.5), "below_0_2": bool(n and np.mean(lg <= 0) < 0.2),
                **{f"logit_q{q}": float(np.quantile(lg[np.isfinite(lg)], q / 10)) if np.isfinite(lg).any() else float("nan")
                   for q in range(1, 10)}}]
    matrix = [{"section": "pbo_matrix", **key_of(c), "year": y, "value": float(ev.year_value(k, y))}
              for k, c in enumerate(ev.cells) for y in use]
    return summary, matrix


# ----------------------------------------------------------------------------------------------- the plateau

def plateau(ev, first: int) -> list[dict]:
    """The final cell (the screen's selection on every year) against every cell one axis away."""
    allm = np.ones(len(ev.years), bool)
    ok, v = ev.values(allm)
    kf, _ = ev.select(allm)
    if kf is None:
        return [{"section": "plateau", "role": "final", "note": "no feasible cell: nothing to audit"}]
    picks = pd.Series([k for _, k, _ in walkforward(ev, first) if k is not None]).value_counts()
    sd = float(np.nanstd(v[np.isfinite(v)], ddof=1)) if np.isfinite(v).sum() > 1 else float("nan")
    base = ev.cells[kf]["idx"]
    rows = [{"section": "plateau", "role": "final", **key_of(ev.cells[kf]), "value": float(v[kf]), "feasible": bool(ok[kf]),
             "walkforward_picks": int(picks.get(kf, 0)), "cells_sd": sd}]
    gaps = []
    for k, c in enumerate(ev.cells):
        diff = [i for i, (a, b) in enumerate(zip(c["idx"], base)) if a != b]
        if len(diff) != 1:
            continue
        gap = float(v[kf] - v[k]) if (np.isfinite(v[k]) and np.isfinite(v[kf])) else float("nan")
        if ok[k] and np.isfinite(gap):
            gaps.append(gap)
        rows.append({"section": "plateau", "role": "neighbour", "axis": ("sessions", "continuation", "displacement",
                     "double_rung_reversions")[diff[0]], **key_of(c), "value": float(v[k]), "feasible": bool(ok[k]),
                     "gap_to_final": gap, "walkforward_picks": int(picks.get(k, 0))})
    sharp = bool(gaps) and np.isfinite(sd) and all(g > sd for g in gaps)
    rows[0].update({"feasible_neighbours": len(gaps), "sharp_peak": sharp,
                    "rule": "a sharp peak when the final cell beats every feasible neighbour by more than the cells' sd"})
    return rows


# -------------------------------------------------------------------------------------------- the label shuffle

def day_matrices(S, ev, cfg: dict) -> tuple[dict, np.ndarray]:
    """Per cell and leg, the kept trades' count, metric and flattened count per signal day ({leg: {stat: cells x days}}),
    and each day's year index in `ev.years`; checked to sum to the screen's per-year matrices."""
    import score_fv3_grid as gf

    nd = int(S.day.max()) + 1
    day_year = np.zeros(nd, int)
    day_year[S.day] = S.year
    out = {leg: {s: np.zeros((len(ev.cells), nd)) for s in ("n", "metric", "flat")} for leg in LEGS}
    for k, c in enumerate(ev.cells):
        cand = S.candidates(c)
        for leg in LEGS:
            _, det = gf.leg_stats(S, c, cand, gf.leg_spec(cfg, leg), ev.years)
            kk = det["k"]
            d = S.day[kk]
            out[leg]["n"][k] = np.bincount(d, minlength=nd)
            out[leg]["metric"][k] = np.bincount(d, weights=det["metric"], minlength=nd)
            out[leg]["flat"][k] = np.bincount(d, weights=det["o"]["flat"][kk].astype(float), minlength=nd)
    yi = np.searchsorted(ev.years, day_year)
    for leg in LEGS:
        for s in ("n", "metric", "flat"):
            agg = aggregate(out[leg][s], yi, len(ev.years))
            if not np.allclose(agg, ev.mat[leg][s], atol=1e-6):
                raise SystemExit(f"REFUSED: the day matrices do not sum to the screen's {leg} {s} by year.")
    return out, yi


def aggregate(m: np.ndarray, yi: np.ndarray, ny: int) -> np.ndarray:
    onehot = np.zeros((len(yi), ny))
    onehot[np.arange(len(yi)), yi] = 1.0
    return m @ onehot


def with_years(ev, mats: dict, yi: np.ndarray):
    """A shallow copy of the screen with its per-year matrices rebuilt from the days' year labels `yi`."""
    ev2 = copy.copy(ev)
    ev2.mat = {leg: dict(ev.mat[leg]) for leg in LEGS}
    for leg in LEGS:
        for s in ("n", "metric", "flat"):
            ev2.mat[leg][s] = aggregate(mats[leg][s], yi, len(ev.years))
    return ev2


def stitched(ev, first: int) -> tuple[float, float]:
    """The walk-forward's stitched out-of-sample mean and its one-sided 95 % bound (a year without a pick reads 0)."""
    import score_orb5_grid as g5

    vals = pd.Series([0.0 if not np.isfinite(v) else v for _, _, v in walkforward(ev, first)], dtype=float)
    return float(vals.mean()), float(g5.bound(vals))


def shuffle(ev, mats: dict, yi: np.ndarray, first: int, n: int = SHUFFLES, seed: int = SEED) -> list[dict]:
    rng = np.random.default_rng(seed)
    actual_mean, actual_lb = stitched(ev, first)
    means = []
    for _ in range(int(n)):
        m, _ = stitched(with_years(ev, mats, rng.permutation(yi)), first)
        means.append(m)
    x = np.array(means, float)
    return [{"section": "shuffle", "shuffles": int(n), "seed": int(seed), "first_test_year": int(first),
             "actual_stitched_mean": actual_mean, "actual_stitched_lb": actual_lb,
             "shuffled_mean": float(x.mean()), "shuffled_sd": float(x.std(ddof=1)),
             **{f"shuffled_q{q}": float(np.quantile(x, q / 100)) for q in (5, 25, 50, 75, 95)},
             "p_at_or_above_actual": float(np.mean(x >= actual_mean - 1e-12)),
             "share_shuffles_above_zero": float(np.mean(x > 0)),
             "reading": "machinery: shuffled days should not look better than the actual's order or above zero"}]


# ------------------------------------------------------------------------------ the deflated Sharpe and standing

def development_trades(rd: Path):
    import fv3_xfa_time_budget as xb
    import score_fv3_grid as gf

    cfg = gf.config(FV3C_CONFIG)
    t, days, _tv = xb.rebuild_trades(cfg)
    return cfg, t, list(days)


def block_series(t: pd.DataFrame, days: list[str], col: str, block: int = BLOCK_DAYS) -> np.ndarray:
    pos = {d: i // int(block) for i, d in enumerate(days)}
    b = t["date"].astype(str).map(pos)
    return t.assign(_b=b).groupby("_b")[col].mean().dropna().to_numpy()


def dsr_rows(cfg: dict, t: pd.DataFrame, days: list[str], rd: Path) -> list[dict]:
    from propedge.research.haircut import deflated_sharpe
    from propedge.research.ledger import count_n, load_ledger

    fr = float(cfg["state_policy"]["fresh"]["funded_rr"])
    x = block_series(t, days, f"r_{fr:g}")
    ledger_n = count_n(load_ledger(), model="FV3-C", k=1, markets=["NQ"], window=(days[0], days[-1]))
    variants = set()
    with (rd / "variants.jsonl").open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                variants.add(json.loads(line)["variant_id"])
    rows = []
    for name, n in (("trial_ledger", int(ledger_n["N"])), ("variant_ledger", len(variants))):
        d = deflated_sharpe(x, n)
        rows.append({"section": "dsr", "count": name, "n_trials": n, "rr": fr, "blocks": int(len(x)),
                     "block_days": BLOCK_DAYS, **{k: float(v) for k, v in d.items()},
                     "line_reference": "deflated Sharpe above zero (the reference); reported, no line here"})
    return rows


def longest_run(flags: np.ndarray) -> int:
    best = cur = 0
    for f in flags:
        cur = cur + 1 if f else 0
        best = max(best, cur)
    return best


def standing(cfg: dict, t: pd.DataFrame, days: list[str]) -> list[dict]:
    from scipy.stats import skew

    import score_fv3_grid as gf

    order = t.sort_values(["date", "entry_t"], kind="stable")
    rows = []
    for R in [float(r) for r in gf.rr_menu(cfg)]:
        v = order[f"r_{R:g}"].dropna().to_numpy(float)
        if not len(v):
            continue
        lose = v < 0
        q = float(lose.mean())
        rows.append({"section": "standing", "reading": "longest_losing_streak", "rr": R, "trades": int(len(v)),
                     "loss_share": q, "longest": longest_run(lose),
                     "expected_longest": float(math.log(len(v)) / math.log(1.0 / q)) if 0 < q < 1 else float("nan")})
    fr = float(cfg["state_policy"]["fresh"]["funded_rr"])
    x = block_series(t, days, f"r_{fr:g}")
    rows.append({"section": "standing", "reading": "block_skew", "rr": fr, "blocks": int(len(x)), "block_days": BLOCK_DAYS,
                 "skew": float(skew(x)) if len(x) > 2 else float("nan")})
    return rows


# --------------------------------------------------------------------------------------------------------- main

def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result, write_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--shuffles", type=int, default=SHUFFLES)
    a = ap.parse_args(argv)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    print("rebuilding FV3's screen...")
    cfg, S, ev = build_screen(rd)
    rows = screen_check(ev, cfg, read_result(rd / SCREEN_RESULT))
    bad = [r for r in rows if not r["equal"]]
    if bad:
        print(f"REFUSED: the rebuilt screen does not reproduce its record ({len(bad)} rows), e.g. {bad[:3]}")
        return 2
    first = int(cfg["selection"]["walkforward"]["first_test_year"])
    print("PBO...")
    summ, matrix = pbo(ev)
    rows += summ + matrix
    rows += plateau(ev, first)
    print(f"the label shuffle ({a.shuffles})...")
    mats, yi = day_matrices(S, ev, cfg)
    rows += shuffle(ev, mats, yi, first, n=a.shuffles)
    print("FV3-C's development record...")
    ccfg, t, days = development_trades(rd)
    rows += dsr_rows(ccfg, t, days, rd)
    rows += standing(ccfg, t, days)
    out = pd.DataFrame(rows)
    write_result(out, "fv3c_gate4", script=SCRIPT, seed=SEED, exploratory=True, results_dir=results_dir,
                 parameters={"screen_config": "config/fv3_grid.yaml", "screen_result": f"results/{SCREEN_RESULT}",
                             "fv3c_config": "config/fv3_corrected_portfolio.yaml", "pbo_years": list(PBO_YEARS),
                             "shuffles": int(a.shuffles), "block_days": BLOCK_DAYS, "decision": "D-386"},
                 notes={"status": "EXPLORATORY: Gate 4's additions on FV3-C's record (D-382 (B), D-386); reported beside, "
                                  "no gate line changes"},
                 description="EXPLORATORY: Gate 4's additions -- the screen's rebuild checked, PBO by CSCV with its matrix, "
                             "the plateau audit, the literal label shuffle, the deflated Sharpe at two trial counts and the "
                             "standing readings.")
    p = out[out["section"] == "pbo"].iloc[0]
    s = out[out["section"] == "shuffle"].iloc[0]
    print(f"PBO {p['pbo']:.4f}; shuffle p {s['p_at_or_above_actual']:.4f}; written results/fv3c_gate4.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
