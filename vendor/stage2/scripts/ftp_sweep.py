"""EXPLORATORY (D-495 (4)): Topstep's Focused Trader Program (10551016) read beside two registered campaigns -- the growth
on the required bankroll that survives each declared threshold, on each of the program's two paths, never a verdict.

    python scripts/ftp_sweep.py                    # both campaigns: the identity checks, then the declared grid
    python scripts/ftp_sweep.py --check            # the identity checks only (nothing written)
    python scripts/ftp_sweep.py --campaign fv3c    # one campaign (fv3c or p11)
    python scripts/ftp_sweep.py --workers 2        # each campaign's paths across path workers (R11; bit for bit)

**Why** (D-495): the program's own page names the pattern FV3-C's and A3's money comes from -- "Excessive Resets and
Trading Combine purchases", "Activating and losing many Express Funded Accounts in a short period of time" (the
Slowdown Path), "Excessive recycling of Trading Combines® or XFAs" (the Corrective Path) -- and publishes no threshold,
no window and no rule for which path applies. So both are swept here, each threshold watched alone, each path declared.
The engine's model and its reading of each consequence are `propedge.campaign.lockstep.FocusedTraderModel`'s (the
ledger row `focused_trader_program`, read 2026-10-30).

**The threshold grid, declared here before any run** (its size is the manifest's variant count: 16 models a campaign,
32 in all; the campaign without the program is the reference, not a variant):

=====================================================  =====================  ==========================
measure (counted over the last 21 trading days)        thresholds             paths
=====================================================  =====================  ==========================
Combine purchases and resets                           10, 20, 30, 40, 60     Slowdown, Corrective
funded accounts lost (breach, closure at request,      3, 5, 10               Slowdown, Corrective
a tier-3 denial's closure)
=====================================================  =====================  ==========================

Every model: placement at the close of the first day the measure reaches its threshold, binding from the next day; at
most one account at a time once placed (Slowdown: no purchase or reset while the accounts open at placement remain, for
the rest of the path; Corrective: every account closed at that close, the payouts not yet arrived denied, one account
for 126 trading days, then the measures watched again from the day after).

**The campaigns, each by its own configuration** (150 paths over 504 sessions, the screens' convention; each at its own
gate seed, so the run without the program is the first 150 paths of its registered per-path file):

* `fv3c` -- FV3-C's development campaign, exactly as `scripts/zero_edge_decomposition.py`'s cell (a) builds it
  (`run_fv3c`: `portfolio_stage.run_campaign` under `config/fv3_corrected_portfolio.yaml`, FV3-C's v12 table at its own
  cell, the development scorer's yearly bound, seed 20261019); the engine call is `run_campaign`'s, argument for
  argument, with the program added;
* `p11` -- A1-INS15's registered development campaign (P-11), exactly as `scripts/a1_ins15.py`'s trades and
  `scripts/zero_edge_decomposition.py`'s `run_p11` (T24-GF15b's plan, 21-session block bound, seed 20261028).

Each arm is read as the scoreboard reads it: growth on the bankroll the run itself required (`pf_growth_on_base_p50` at
`pf_required_p90`, D-312), at the point estimate and at the one-sided 95 % lower bound, 0 % denial, placement off -- and
beside it the share of paths placed, the median placement day, what a Corrective placement closed and denied, and the
pattern measures' rolling maxima.

**The identity checks, before any model is read:** each campaign's run without the program must equal the first 150
paths of its registered per-path record on every compared column -- `results/fv3_corrected_v1_paths.csv` (gate,
placement off, both shifts) and `results/a1_ins15_gate_paths.csv` (gate, both shifts). Either failing refuses the run:
nothing is written. Development data only, files already on record; nothing past each campaign's own window.

Writes `results/ftp_sweep.csv` (sections `sweep`, `identity`) with its manifest; each model recorded in
`results/variants.jsonl` under `D-495:ftp_sweep`. EXPLORATORY: no verdict, no selection, no money decision; the gate's
0 % denial (D-234) is not changed by this reading.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

if __name__ == "__main__":                 # one BLAS thread, before numpy loads (D-464 (5))
    for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/ftp_sweep.py"
DECISION = "D-495"
RESULT = "ftp_sweep"
FAMILY_ID = f"{DECISION}:ftp_sweep"
N_PATHS, HORIZON = 150, 504                 # the screens' convention
WINDOW_DAYS = 21
#: the declared grid (above): thresholds of each measure, watched alone, on each path
PURCHASE_THRESHOLDS = (10, 20, 30, 40, 60)
LOST_THRESHOLDS = (3, 5, 10)
PATHS = ("slowdown", "corrective")
CAMPAIGNS = ("fv3c", "p11")
#: each campaign's registered per-path file and the (run, shift) pairs its run without the program must reproduce
REFERENCES = {"fv3c": ("fv3_corrected_v1_paths.csv", (("gate placement off", "point"),
                                                      ("gate placement off", "lower_bound"))),
              "p11": ("a1_ins15_gate_paths.csv", (("gate", "point"), ("gate", "lower_bound")))}
#: the gate row's columns kept beside the sweep's own
KEEP = ("pf_growth_on_base_p10", "pf_required_p50", "pf_required_p99", "pf_net_p50", "median_log_growth",
        "mean_combine_purchases", "mean_accounts_funded", "share_accounts_ever_paid", "median_days_to_first_payout",
        "mean_payouts_per_path", "pf_break_even_denial_p50", "ruin_probability", "mean_max_drawdown")
FTP_COLS = ("ftp_label", "ftp_path", "ftp_window_days", "ftp_combine_purchases", "ftp_funded_lost",
            "ftp_account_limit", "ftp_corrective_days", "ftp_repeat", "share_paths_ftp_placed",
            "share_paths_ftp_slowdown", "share_paths_ftp_corrective", "ftp_first_placed_day_p50", "mean_ftp_placements",
            "mean_ftp_combines_closed", "mean_ftp_funded_closed", "mean_ftp_passes_removed", "mean_ftp_payouts_denied",
            "mean_ftp_payout_cash_denied", "mean_ftp_purchase_days_blocked", "mean_ftp_resets_refused",
            "mean_ftp_max_combine_purchases_in_window", "mean_ftp_max_funded_lost_in_window")


def models() -> list:
    """The declared grid: 16 `FocusedTraderModel`s, path-major, purchases before losses."""
    from propedge.campaign.gate import ftp_models

    return ftp_models(PATHS, combine_purchases=PURCHASE_THRESHOLDS, funded_lost=LOST_THRESHOLDS,
                      window_days=WINDOW_DAYS)


# ------------------------------------------------------------------------------------------------ the campaigns


def fv3c_campaign(rd: Path, n_paths: int = N_PATHS, horizon: int = HORIZON) -> tuple[list, dict, int]:
    """FV3-C's development campaign as `zero_edge_decomposition.run_cell("a")` builds it -- (blocks, `run_gate`'s
    arguments, seed): `portfolio_stage.run_campaign`'s engine call, argument for argument."""
    import portfolio_stage as ps
    import score_fv3_grid as gf
    import zero_edge_decomposition as zd

    from propedge.campaign.payout_method import rules_for_method

    cfg = zd.fv3_config()
    pid = zd.fv3_cell(rd)
    t, days, tv = zd.fv3_trades(rd)
    pol = zd.plan("v12", cfg, pid)
    t = zd.pad(t, sorted(set(zd.rr_keys(t)) | set(zd.policy_rrs(pol))))
    keys = zd.rr_keys(t)
    stats = zd.stats_of(t, days, keys, "yearly")
    own = gf.policy_for_edge(cfg, stats[3.0]["lb"])[2]
    if own != pid:
        raise SystemExit(f"REFUSED: FV3-C's trades read the v12 cell {own}, not {zd.FV3_RUN}'s {pid}.")
    blocks, n_used = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise SystemExit("REFUSED: the blocks hold a different number of trades.")
    e_by, lb_by = ps._by(stats, "e"), ps._by(stats, "lb")
    fr = 3.0                                                # FV3-C's key for the log's single outcome (zd.campaign)
    camp = cfg["gate"]["campaign"]
    kw = dict(e=e_by[fr], lb=lb_by[fr], protocol=ps.protocol_of(cfg), bankroll=gf.bankroll_of(cfg),
              horizon_days=int(horizon), n_paths=int(n_paths), seed=int(zd.SEED), accounts=int(camp["accounts"]),
              sizing=gf.sizing_rule(cfg, tv), rules=rules_for_method(camp["payout_method"]), mode=camp["mode"],
              settlement=camp["settlement"], combines=int(camp["combines"]), total_accounts=int(camp["accounts"]),
              risk_policy=pol, e_by_rr=e_by, lb_by_rr=lb_by, levels=(0.0,), rtp=False,
              routing=gf.fidelity_of(cfg)["routing"],
              cross_account=bool(gf.fidelity_of(cfg).get("cross_account_rule", False)),
              flip=gf.flip_spec_of(cfg),
              hold_to_own_exit=bool(gf.fidelity_of(cfg).get("hold_to_own_exit", False)))
    return blocks, kw, int(zd.SEED)


def p11_campaign(rd: Path, n_paths: int = N_PATHS, horizon: int = HORIZON) -> tuple[list, dict, int]:
    """P-11's campaign as `zero_edge_decomposition.run_p11` calls it, on A1-INS15's trades checked against the rescreen
    fixed at registration -- (blocks, `run_gate`'s arguments, seed)."""
    import a1_ins15 as a1
    import portfolio_stage as ps
    import score_fv3_grid as gf
    import t24_wide as tw
    import zero_edge_decomposition as zd

    from propedge.campaign.payout_method import rules_for_method

    t, days = zd.a1_trades(rd)
    pol = zd.plan("gf15b", {}, "")
    keys = zd.rr_keys(t)
    stats = zd.stats_of(t, days, keys, "blocks21")
    blocks, n_used = gf.gate_blocks(t, days, 0.5, keys, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise SystemExit("REFUSED: the blocks hold a different number of trades.")
    e_by, lb_by = ps._by(stats, "e"), ps._by(stats, "lb")
    kw = dict(e=e_by[1.0], lb=lb_by[1.0], protocol=a1.protocol_for(t), bankroll=gf.UNBOUND_BANKROLL,
              horizon_days=int(horizon), n_paths=int(n_paths), seed=int(zd.P11_SEED), accounts=tw.ACCOUNTS,
              sizing=tw.sizing(), rules=rules_for_method("aeropay"), mode="rotation", settlement="pessimistic",
              combines=tw.ACCOUNTS, total_accounts=tw.ACCOUNTS, risk_policy=pol, e_by_rr=e_by, lb_by_rr=lb_by,
              levels=(0.0,), rtp=False, routing="able", cross_account=True, hold_to_own_exit=True,
              one_at_a_time=tw.GAP)
    return blocks, kw, int(zd.P11_SEED)


BUILDERS = {"fv3c": fv3c_campaign, "p11": p11_campaign}


# ------------------------------------------------------------------------------------------------ the reading


def sweep_rows(name: str, df: pd.DataFrame, seed: int) -> list[dict]:
    """One campaign's sweep: a row per model (and the run without it) and arm, with the change in growth on the
    required bankroll from the run without the program at the same arm."""
    base = df[df["ftp_label"] == "off"].set_index("shift")["growth_on_required"]
    out = []
    for _, r in df.iterrows():
        g = float(r["growth_on_required"])
        off = float(base.get(r["shift"], float("nan")))
        thr = (r.get("ftp_combine_purchases") if r["ftp_label"] != "off" else float("nan"))
        measure = ("off" if r["ftp_label"] == "off" else "combine_purchases"
                   if np.isfinite(float(r.get("ftp_combine_purchases", float("nan")))) else "funded_lost")
        out.append({"section": "sweep", "campaign": name, "seed": seed, "paths": int(r["paths"]),
                    "horizon": int(r["horizon_days"]), "arm": "point" if r["shift"] == "point" else "bound",
                    "shift": r["shift"], "enforcement_p": float(r["enforcement_p"]), "rtp": bool(r["rtp"]),
                    "measure": measure,
                    "threshold": (float(thr) if measure == "combine_purchases" else
                                  float(r.get("ftp_funded_lost", float("nan"))) if measure == "funded_lost"
                                  else float("nan")),
                    "growth_on_required": g, "required_p90": float(r["required_p90"]),
                    "growth_change_from_off": g - off,
                    **{c: r.get(c) for c in FTP_COLS if c in r.index},
                    **{c: r.get(c) for c in KEEP if c in r.index}})
    return out


def identity_problems(name: str, sink: list[dict], rd: Path, n_paths: int) -> list[str]:
    """The run without the program against the first `n_paths` of the campaign's registered per-path record."""
    import zero_edge_decomposition as zd

    from propedge.reporting.results import read_result

    ref_file, pairs = REFERENCES[name]
    ref = read_result(Path(rd) / ref_file)
    return zd.path_problems(sink, ref, [(f"{name} off", shift, run, shift) for run, shift in pairs], int(n_paths))


def run_campaign(name: str, rd: Path, *, check_only: bool, n_paths: int = N_PATHS, workers: int = 1
                 ) -> tuple[list[dict], dict]:
    """One campaign: the run without the program and its identity check, then (unless `check_only`) every model.
    Returns (sweep rows, identity row); raises SystemExit on a failed identity."""
    import portfolio_stage as ps
    import zero_edge_decomposition as zd

    from propedge.campaign import gate

    blocks, kw, seed = BUILDERS[name](rd, n_paths=n_paths)
    sink: list[dict] = []
    hook, inner = zd.hook_for(sink)
    t0 = time.time()
    off = gate.ftp_sweep(blocks, [], path_hook=hook, on_run=lambda lbl: ps._label(inner, f"{name} {lbl}"),
                         workers=int(workers), **kw)
    bad = identity_problems(name, sink, rd, n_paths)
    print(f"{name}: the run without the program, {n_paths} paths, {time.time() - t0:.0f} s -- identity with "
          f"{REFERENCES[name][0]}: {'HOLDS' if not bad else 'FAILS'}", flush=True)
    if bad:
        raise SystemExit(f"REFUSED (identity, {name}): " + "; ".join(bad[:8]))
    ident = {"section": "identity", "campaign": name, "seed": seed, "paths": n_paths,
             "check": f"the run without the program equals the first {n_paths} paths of {REFERENCES[name][0]}",
             "compared": ",".join(zd.PATH_COLS), "holds": True}
    if check_only:
        return [], ident
    parts = [off]
    for m in models():
        t1 = time.time()
        df = gate.ftp_sweep(blocks, [m], include_off=False, path_hook=hook,
                            on_run=lambda lbl: ps._label(inner, f"{name} {lbl}"), workers=int(workers), **kw)
        parts.append(df)
        g = df.set_index("shift")["growth_on_required"]
        print(f"  {m.label}: placed {float(df['share_paths_ftp_placed'].iloc[0]):.2f}, growth point "
              f"{g.get('point', float('nan')):+.4f} bound {g.get('lower_bound', float('nan')):+.4f} "
              f"({time.time() - t1:.0f} s)", flush=True)
    return sweep_rows(name, pd.concat(parts, ignore_index=True), seed), ident


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import write_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="the identity checks only; nothing written")
    ap.add_argument("--campaign", choices=CAMPAIGNS, action="append", help="one campaign (repeatable); default both")
    ap.add_argument("--workers", type=int, default=1, help="path workers per campaign (R11; bit for bit)")
    a = ap.parse_args(argv)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    names = tuple(a.campaign) if a.campaign else CAMPAIGNS
    grid = models()
    rows, idents = [], []
    for name in names:
        r, ident = run_campaign(name, rd, check_only=a.check, workers=a.workers)
        rows += r
        idents.append(ident)
    if a.check:
        print("identity checks hold; nothing written (--check).")
        return 0
    counter = VariantCounter(path=rd / "variants.jsonl")
    seeds = {}
    for name in names:
        seed = int(next(x["seed"] for x in idents if x["campaign"] == name))
        seeds[name] = seed
        for m in grid:
            counter.record(prereg_id=FAMILY_ID, seed=seed, exploratory=True,
                           params={"campaign": name, **m.as_dict(), "paths": N_PATHS, "horizon": HORIZON},
                           label=f"Focused Trader Program sweep (D-495 (4)): {name} {m.label}")
    res = pd.DataFrame(rows + idents)
    write_result(res, RESULT, script=SCRIPT, seed=seeds[names[0]], exploratory=True, results_dir=results_dir,
                 variant_count=len(grid) * len(names),
                 parameters={"decision": DECISION, "campaigns": list(names), "seeds": seeds, "paths": N_PATHS,
                             "horizon": HORIZON, "window_days": WINDOW_DAYS,
                             "purchase_thresholds": list(PURCHASE_THRESHOLDS), "lost_thresholds": list(LOST_THRESHOLDS),
                             "ftp_paths": list(PATHS), "models": [m.as_dict() for m in grid],
                             "levels": [0.0], "placement": "off", "workers": int(a.workers),
                             "fv3c": "zero_edge_decomposition cell (a): config/fv3_corrected_portfolio.yaml, v12 at "
                                     "its own cell, yearly bound",
                             "p11": "a1_ins15 trades, T24-GF15b's plan, 21-session block bound",
                             "metric": "pf_growth_on_base_p50 on pf_required_p90 (the scoreboard's)",
                             "references": [f"results/{REFERENCES[n][0]}" for n in names],
                             "rules_row": "focused_trader_program (10551016, read 2026-10-30)"},
                 notes={"status": "EXPLORATORY (D-495 (4)): the Focused Trader Program read beside registered "
                                  "campaigns at declared thresholds; no verdict, no selection, no money decision; "
                                  "never the gate (D-234)",
                        "variant_count_rule": "each model of the declared grid on each campaign one configuration; "
                                              "the run without the program is the reference",
                        "identity": "each campaign's run without the program equals the first 150 paths of its "
                                    "registered per-path record"},
                 description="EXPLORATORY (D-495 (4)): Topstep's Focused Trader Program on FV3-C's development "
                             "campaign and P-11's -- each Combine-purchase threshold (10-60 in 21 days) and each "
                             "funded-accounts-lost threshold (3-10 in 21 days) alone, on the Slowdown and the "
                             "Corrective path, 150 paths over 504 sessions at each campaign's own seed -- growth on "
                             "the required bankroll at the point and the bound, the share of paths placed and what a "
                             "placement closed and denied, beside the run without the program.")
    show = res[res["section"] == "sweep"].pivot_table(index=["campaign", "ftp_label"], columns="arm",
                                                      values="growth_on_required", sort=False)
    pd.set_option("display.width", 200)
    print(show.round(4).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
