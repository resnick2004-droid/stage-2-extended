"""EXPLORATORY (D-505): D-501's compliance study repeated on FV3-C itself -- the only confirmed candidate and the first
in the shadow-period queue -- on two campaigns, each first reproduced from its registered per-path file. Not a
candidate search and not a verdict: read beside FV3-C's development run and P-06, for the shadow period's protocol
choice (`prereg/DRAFT_shadow_fv3c.md`).

    python scripts/fv3c_compliance.py --check --paths 4     # both campaigns' first paths reproduced; nothing written
    python scripts/fv3c_compliance.py --check --paths 4 --campaign p06_confirmation   # one campaign's check
    python scripts/fv3c_compliance.py                       # the study (needs D-502's no-closure table on record)
    python scripts/fv3c_compliance.py --workers 2           # each campaign's paths across path workers (R11; bit for bit)

**The campaigns, each by its own protocol exactly** (FV3-C's: no funded room cap, no strict one-at-a-time rule -- none
is added here; the seat freed the same evening; the MAE settlement; the 45-tick stand-aside; capacity five a day):

==================  ========================================================  =========================================
campaign            built as                                                   reproduced from (gate placement off, 0 %)
==================  ========================================================  =========================================
fv3c_dev            FV3-C's development campaign: `ftp_sweep.fv3c_campaign`,  `results/fv3_corrected_v1_paths.csv`
                    which is `zero_edge_decomposition.run_fv3c`'s engine call
                    argument for argument (`portfolio_stage.run_campaign`
                    under `config/fv3_corrected_portfolio.yaml`, the v12 table
                    at its own cell, the development scorer's yearly bound,
                    seed 20261019)
p06_confirmation    P-06's gate arm on NQ's held-back window as                `results/fv3_confirmation_paths.csv`
                    `scripts/confirm_fv3.py` builds it (and
                    `scripts/reproduce_registered.py`'s P-06 mapping reruns
                    it): the ingested periods R139-R141 read by
                    `confirm_fv3.load_window`, the frozen cell's gate trades,
                    each R's bound over 21-session blocks
                    (`confirm_fv3.edge_stats`), the table at the funded leg's
                    bound (`state_dp_e-0.050_lamstar`), `score_fv3_grid.run_gate`'s
                    engine call at the declared placement (off), seed 20261019
==================  ========================================================  =========================================

P-06's window was read once by its verdict (D-361); this is a description of that window under each restraint, never a
second confirmation (D-505).

**First, both campaigns' references -- each campaign's own configuration -- must reproduce their registered per-path
records' gate run (placement off, 0 % denial, point and bound), path for path on `zero_edge_decomposition.PATH_COLS`
(the first `--paths` with --check; all 500 in the study); otherwise nothing more runs and nothing is written.** Then
D-501's 9 variants (`a3_compliance.variants()`: the no-closure table, D-502's
`results/state_policy_v12_noclose_policies.json` read through its result's manifest and hashed line-ending-free,
D-503; a self-imposed budget of K Combine purchases and resets in any 21 trading days, K = 10, 20, 30, 40; both) on each
campaign, each on the same trades, bounds, seed and paths.

**Readings per variant** (D-501 (2), `a3_compliance.READ`): growth on the required bankroll at the 0.05 bound and the
point, the required bankroll, the share of funded accounts closed at request, Combine purchases in any 21 days, the
share of payouts exposed, the break-even denial, the budget's own counts, and the Focused Trader Program's 16 declared
models (D-497's grid, `ftp_sweep.models()`) run by `gate.ftp_sweep` on the variant's campaign at `FTP_PATHS` = 150
paths (D-501's declaration) -- their minimum and median growth at the bound -- each with its change from the campaign's
reference. Each variant's run without the program at 150 paths must equal the first 150 paths of its own run; the
development campaign's reference's 16 models must equal `results/ftp_sweep.csv`'s `fv3c` rows (D-495's sweep, the same
campaign at 150 paths: growth on the required bankroll, the required bankroll and the share placed, at both arms);
else nothing is written.

Written: `results/fv3c_compliance.csv` (sections `variant`, `campaign`, `ftp`, `identity`, each row carrying its
`study_campaign`) and `results/fv3c_compliance_paths.csv` (the per-path record of the 20 campaigns at 500 paths).
EXPLORATORY: the 9 variants of each campaign recorded in `results/variants.jsonl` under `D-505:fv3c_compliance` (each
reference is a registered configuration, not a variant); the program's models on each of the 20 campaigns under
`D-505:fv3c_compliance_ftp`. Read beside FV3-C and P-06, never a gate (D-234).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Callable

if __name__ == "__main__":                 # one BLAS thread, before numpy loads (D-464 (5))
    for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/fv3c_compliance.py"
DECISION = "D-505"
RESULT = "fv3c_compliance"
FAMILY_ID = f"{DECISION}:fv3c_compliance"          # the 9 variants on each campaign
FTP_FAMILY_ID = f"{DECISION}:fv3c_compliance_ftp"  # the program's 16 models on each campaign (D-499's precedent)
SEED = 20261019                                    # FV3-C's gate seed: both campaigns' (fv3_corrected_portfolio.yaml)
N_PATHS = 500                                      # both registered runs' gate paths
FTP_PATHS = 150                                    # D-501's declared program path count (D-497's convention)
POLICY_ID = "state_dp_e-0.050_lamstar"             # both campaigns' v12 cell (each run's gate rows, checked)
CAMPAIGNS = ("fv3c_dev", "p06_confirmation")
#: each campaign's registered per-path record and the run its reference must reproduce (placement off, 0 %)
REFERENCES = {"fv3c_dev": ("fv3_corrected_v1_paths.csv", "gate placement off"),
              "p06_confirmation": ("fv3_confirmation_paths.csv", "gate placement off")}
FTP_SWEEP_FILE = "ftp_sweep.csv"                   # D-495's sweep: FV3-C's development campaign at 150 paths
FTP_SWEEP_COLS = ("growth_on_required", "required_p90", "share_paths_ftp_placed")
READING = "EXPLORATORY (D-505): beside FV3-C's development run and P-06, never a gate (D-234)"
#: the measured cost (2026-10-31, the build's timing run: 20 paths, one process, one BLAS thread, beside other jobs)
COST_NOTE = ("measured: a path-run (one path through 504 sessions, one shift) on the variant's own run 0.27-0.33 s "
             "(fv3c_dev) and 0.28-0.37 s (p06_confirmation), on the program's runs 0.21 s and 0.14 s; a variant at 500 "
             "paths plus its 17 program runs at 150 paths is about 1,000 x 0.31 + 5,100 x 0.21 = 1,380 s (fv3c_dev) "
             "and 1,000 x 0.36 + 5,100 x 0.14 = 1,070 s (p06_confirmation), so the 20 campaigns about 6.8 hours in "
             "one process; --workers 2 about halves it where the memory guard grants the second worker")


@dataclass
class Campaign:
    """One campaign: its blocks and `gate.run_gate`'s arguments (all but `blocks`, `path_hook`, `n_paths`, `workers`
    and `purchase_budget`), its registered per-path record, and how its reference's program rows are checked."""
    name: str
    blocks: list
    kw: dict
    seed: int
    policy_id: str
    ref_file: str
    ref_run: str
    margin: float
    block_days: int
    info: dict = field(default_factory=dict)
    ftp_ref: Callable[[pd.DataFrame, Path, int], list[str]] | None = None


# ------------------------------------------------------------------------------------------------ the campaigns


def fv3c_dev_campaign(rd: Path) -> Campaign:
    """FV3-C's development campaign: `ftp_sweep.fv3c_campaign` (= `zero_edge_decomposition.run_fv3c`'s engine call,
    argument for argument: the v12 table at FV3-C's cell, the yearly bound, seed 20261019)."""
    import ftp_sweep as fs
    import score_fv3_grid as gf
    import zero_edge_decomposition as zd

    blocks, kw, seed = fs.fv3c_campaign(rd, n_paths=N_PATHS, horizon=zd.HORIZON)
    kw = dict(kw)
    kw.pop("n_paths")
    if int(seed) != SEED or kw["risk_policy"].id != POLICY_ID:
        raise SystemExit(f"REFUSED: FV3-C's development campaign is not seed {SEED} at {POLICY_ID}.")
    cfg = zd.fv3_config()
    return Campaign("fv3c_dev", list(blocks), kw, int(seed), POLICY_ID, *REFERENCES["fv3c_dev"],
                    margin=float(cfg["portfolio"]["margin"]), block_days=int(cfg["portfolio"]["block_days"]),
                    info={"config": str(zd.FV3_CONFIG.relative_to(ROOT)).replace("\\", "/"),
                          "built_as": "ftp_sweep.fv3c_campaign (zero_edge_decomposition.run_fv3c's engine call)",
                          "bound": "yearly (the development scorer's)", "blocks": len(blocks),
                          "capacity": int(kw["protocol"].trades_per_day), "one_at_a_time": None,
                          "room_cap": list(getattr(kw["sizing"], "room_cap", ()) or ()),
                          "menu": [float(k) for k in kw["e_by_rr"]], "max_per_day": int(gf.MAX_PER_DAY)},
                    ftp_ref=ftp_sweep_problems)


def p06_campaign(rd: Path, runs_dir: Path | None = None) -> Campaign:
    """P-06's gate arm exactly as `confirm_fv3.main` builds it (the steps of its body up to `score_fv3_grid.run_gate`,
    each by the function it calls) and `score_fv3_grid.run_gate`'s engine call at the declared placement (off)."""
    import confirm_fv3 as cf
    import score_fv3_grid as gf

    from propedge.data.orb_kit import params
    from propedge.execution.fills import FillModel
    from propedge.reporting.results import read_result
    from propedge.research.model_card import BAND_FILE, setups_minimum

    rund = Path(runs_dir) if runs_dir is not None else ROOT / "runs"
    conf = cf.config()
    states = {str(p["id"]): cf.period_state(p, rd, rund) for p in conf["periods"]}
    bad = [why for s, _, why in states.values() if s != "ingested"]
    if bad:
        raise SystemExit("REFUSED: P-06's periods are not all ingested -- " + "; ".join(bad))
    chosen = {k: run for k, (s, run, _) in states.items()}
    cand = cf.candidate(conf)
    if int(cand["k"]) != 1:
        raise SystemExit("REFUSED: the frozen candidate must be one declared cell (k = 1).")
    sig, ses, bench, sessions_by, window_days, label_of_day = cf.load_window(conf, cand, chosen, rd, rund)
    fm = FillModel.load("assumed")
    q = params("NQ")
    tv = q["micro_tick"] * q["micro_point_value"]
    S = gf.Signals3(sig, float(fm.round_turn_by_instrument[q["micro"]]), float(fm.round_turn_by_instrument["NQ"]), tv,
                    cand["ladder"])
    S.year = np.array([label_of_day[str(d)] for d in S.df["date"]], dtype=int)
    fresh = cand["state_policy"]["fresh"]
    need = setups_minimum(float(fresh["combine_rr"]), float(fresh["combine_risk"]), 0.0)
    ev = gf.EvaluatedFV3(S, ses, cand, sessions_by, read_result(BAND_FILE), float(need))
    final = ev.cells[0]
    sels = {int(y): 0 for y in ev.years}
    t = gf.gate_trades(S, ev, sels, final)
    menu = [float(R) for R in gf.rr_menu(cand)]
    n_trials = None if str(conf.get("ledger_n", "pending")).lower() == "pending" else int(conf["ledger_n"])
    stats = cf.edge_stats(t, menu, window_days, int(conf["block_days"]), n_trials)
    fr = float(fresh["funded_rr"])
    if not (len(t) and np.isfinite(stats[fr]["lb"])):
        raise SystemExit("REFUSED: P-06's window gives no gate campaign.")
    blocks, n_used = gf.gate_blocks(t, window_days, tv, menu, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise SystemExit("REFUSED: the blocks hold a different number of trades.")
    policy, e_used, pid = gf.policy_for_edge(cand, stats[fr]["lb"])
    if pid != POLICY_ID:
        raise SystemExit(f"REFUSED: P-06's window reads the v12 cell {pid}, not {POLICY_ID} (the no-closure table's).")
    kw = p06_gate_kwargs(cand, stats, menu, policy, tv)
    protocol = kw["protocol"]
    if int(kw["seed"]) != SEED:
        raise SystemExit(f"REFUSED: P-06's gate seed is not {SEED}.")
    return Campaign("p06_confirmation", list(blocks), kw, int(kw["seed"]), pid, *REFERENCES["p06_confirmation"],
                    margin=float(cand["portfolio"]["margin"]), block_days=int(cand["portfolio"]["block_days"]),
                    info={"config": str(conf["candidate_config"]), "built_as": "scripts/confirm_fv3.py's gate arm",
                          "periods": chosen, "trades": int(len(t)), "days": int(len(window_days)),
                          "bound": f"{int(conf['block_days'])}-session blocks over the window",
                          "capacity": int(protocol.trades_per_day), "one_at_a_time": None,
                          "room_cap": list(getattr(kw["sizing"], "room_cap", ()) or ()), "menu": menu,
                          "policy_edge": float(e_used)})


def p06_gate_kwargs(cand: dict, stats: dict, menu: list[float], policy, tv: float) -> dict:
    """`score_fv3_grid.run_gate`'s engine call at the candidate's declared placement (off), all but `blocks`,
    `n_paths` and `path_hook`, with the gate's 0 % alone (`levels`): its Protocol is `portfolio_stage.protocol_of`'s
    fields with its own note."""
    import portfolio_stage as ps
    import score_fv3_grid as gf

    from propedge.campaign.payout_method import rules_for_method

    camp, fresh = cand["gate"]["campaign"], cand["state_policy"]["fresh"]
    if bool(camp["rtp"]):
        raise SystemExit("REFUSED: the candidate's declared placement is not off (D-289).")
    fr = float(fresh["funded_rr"])
    e_by = {float(k): stats[k]["e"] for k in menu}
    lb_by = {float(k): stats[k]["lb"] for k in menu}
    f = gf.fidelity_of(cand)
    return dict(e=e_by[fr], lb=lb_by[fr], protocol=replace(ps.protocol_of(cand),
                                                         note="FV3's gate under the state policy (D-290)"),
                bankroll=gf.bankroll_of(cand), horizon_days=int(camp["horizon_days"]), seed=int(cand["seeds"]["gate"]),
                accounts=int(camp["accounts"]), sizing=gf.sizing_rule(cand, tv),
                rules=rules_for_method(camp["payout_method"]), mode=camp["mode"], settlement=camp["settlement"],
                combines=int(camp["combines"]), total_accounts=int(camp["accounts"]), risk_policy=policy,
                e_by_rr=e_by, lb_by_rr=lb_by, levels=(0.0,), rtp=False, routing=f["routing"],
                cross_account=bool(f.get("cross_account_rule", False)), flip=gf.flip_spec_of(cand),
                hold_to_own_exit=bool(f.get("hold_to_own_exit", False)))


BUILDERS: dict[str, Callable[[Path], Campaign]] = {"fv3c_dev": fv3c_dev_campaign, "p06_confirmation": p06_campaign}


# ------------------------------------------------------------------------------------------------ the identities


def reference_problems(c: Campaign, sink: list[dict], rd: Path, n: int) -> list[str]:
    """The campaign's reference against its registered per-path record: the first `n` paths of its gate run (placement
    off, 0 %), point and bound."""
    import zero_edge_decomposition as zd

    from propedge.reporting.results import read_result

    ref = read_result(Path(rd) / c.ref_file)
    return zd.path_problems(sink, ref, [("reference", s, c.ref_run, s) for s in ("point", "lower_bound")], int(n))


def ftp_sweep_problems(fdf: pd.DataFrame, rd: Path, n: int) -> list[str]:
    """FV3-C's development reference's program rows against D-495's sweep of the same campaign (`results/ftp_sweep.csv`,
    its `fv3c` rows): each model's and the run without it, at both arms -- at the sweep's own path count only."""
    import ftp_sweep as fs

    from propedge.reporting.results import read_result

    if int(n) != int(fs.N_PATHS):
        return []                                      # a different path count: nothing on record to compare
    ref = read_result(Path(rd) / FTP_SWEEP_FILE)
    ref = ref[(ref["section"] == "sweep") & (ref["campaign"].astype(str) == "fv3c")]
    out = []
    for (lbl, shift), g in fdf.groupby(["ftp_label", "shift"]):
        r = ref[(ref["ftp_label"].astype(str) == str(lbl)) & (ref["shift"].astype(str) == str(shift))]
        if len(r) != 1 or int(r["paths"].iloc[0]) != int(n):
            out.append(f"{lbl} {shift}: {len(r)} rows in {FTP_SWEEP_FILE} at {n} paths, not one")
            continue
        for col in FTP_SWEEP_COLS:
            x, y = float(g[col].iloc[0]), float(r[col].iloc[0])
            if not ((np.isnan(x) and np.isnan(y)) or np.isclose(x, y, rtol=1e-12, atol=1e-9)):
                out.append(f"{lbl} {shift} {col}: {x!r} against the sweep's {y!r}")
    if fdf.groupby(["ftp_label", "shift"]).ngroups != len(ref):
        out.append(f"{fdf.groupby(['ftp_label', 'shift']).ngroups} program rows against the sweep's {len(ref)}")
    return out


# ------------------------------------------------------------------------------------------------ the study


def hook_of(c: Campaign, sink: list[dict]):
    """(the path hook, its inner portfolio hook): `zero_edge_decomposition.hook_for`'s, at the campaign's own margin
    and block (both the frozen candidate's, 49 and 21)."""
    import fv3d_lever_test as lt
    import portfolio_stage as ps

    inner = ps.composed_hook({"margin": float(c.margin), "block_days": int(c.block_days)}, sink=sink)
    return lt.lever_hook(inner), inner


def run_kwargs(c: Campaign, plan, budget, n: int) -> dict:
    """`gate.run_gate`'s arguments for one variant: the campaign's own, its plan, the path count, the budget (a switch
    that is off is not passed: the registered call exactly)."""
    kw = {**c.kw, "risk_policy": plan, "n_paths": int(n)}
    if budget is not None:
        kw["purchase_budget"] = tuple(budget)
    return kw


def run_reference(c: Campaign, plan, sink: list, hook, inner, n: int, workers: int) -> pd.DataFrame:
    import portfolio_stage as ps

    from propedge.campaign import gate

    ps._label(inner, "reference")
    df, _ = gate.run_gate(c.blocks, path_hook=hook, workers=int(workers), **run_kwargs(c, plan, None, n))
    df["placement"] = "off"
    return df


def study(rd: Path, results_dir: Path | None, *, builders: dict[str, Callable[[Path], Campaign]] | None = None,
          campaigns: tuple[str, ...] = CAMPAIGNS, n_paths: int = N_PATHS, ftp_paths: int = FTP_PATHS, workers: int = 1,
          check_only: bool = False, which: list[str] | None = None, record: bool = True,
          plans_override: dict | None = None) -> int:
    """Both campaigns' references reproduced first, then each campaign's variants with their program readings; the
    files. `builders`, `which` and `plans_override` are test seams (toy campaigns, a subset of variants, a stand-in for
    the no-closure table)."""
    import a3_compliance as a3
    import ftp_sweep as fs
    import portfolio_stage as ps

    from propedge.campaign import gate
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import write_result

    builders = BUILDERS if builders is None else builders
    grid = fs.models()
    if len(grid) != 16:
        raise SystemExit(f"REFUSED: the program's grid holds {len(grid)} models, not 16 (D-497).")
    todo = a3.variants() if not which else [v for v in a3.variants() if v["variant"] in set(which) | {"reference"}]
    noclose = None
    if not check_only and any(v["table"] == "noclose" for v in todo):
        noclose = (plans_override or {}).get("noclose") or a3.noclose_policy(rd)
    built: dict[str, dict[str, Any]] = {}
    idents: list[dict] = []
    # ---- 1: every campaign's reference reproduced before any variant runs
    for name in campaigns:
        t0 = time.time()
        c = builders[name](rd)
        sink: list[dict] = []
        hook, inner = hook_of(c, sink)
        df = run_reference(c, c.kw["risk_policy"], sink, hook, inner, n_paths, workers)
        secs = time.time() - t0
        bad = reference_problems(c, sink, rd, n_paths)
        print(f"{name}: reference growth bound "
              f"{float(df.loc[df['shift'] == 'lower_bound', 'pf_growth_on_base_p50'].iloc[0]):+.4f} point "
              f"{float(df.loc[df['shift'] == 'point', 'pf_growth_on_base_p50'].iloc[0]):+.4f} ({n_paths} paths, "
              f"{secs:.0f} s with the build) -- identity with {c.ref_file}: {'HOLDS' if not bad else 'FAILS'}",
              flush=True)
        if bad:
            print(f"REFUSED (D-505): {name}'s reference does not reproduce its per-path record -- " + "; ".join(bad[:8]))
            return 3
        idents.append({"section": "identity", "study_campaign": name, "variant": "reference", "holds": True,
                       "paths": int(n_paths), "seconds_reference": secs,
                       "check": f"the campaign's own configuration reproduces the first {n_paths} paths of "
                                f"results/{c.ref_file}'s '{c.ref_run}' run at 0 %, point and bound"})
        built[name] = {"c": c, "sink": sink, "hook": hook, "inner": inner, "ref_df": df}
    if check_only:
        print("every reference holds; nothing written (--check).")
        return 0
    # ---- 2: each campaign's variants and the program on each
    rows_all, camp_parts, ftp_parts = [], [], []
    t_all = time.time()
    for name in campaigns:
        b = built[name]
        c, sink, hook, inner = b["c"], b["sink"], b["hook"], b["inner"]
        plans = {"v12": c.kw["risk_policy"], "noclose": noclose}
        rows = []
        for v in todo:
            vn = v["variant"]
            t0 = time.time()
            if vn == "reference":
                df = b["ref_df"].copy()
            else:
                ps._label(inner, vn)
                df, _ = gate.run_gate(c.blocks, path_hook=hook, workers=int(workers),
                                      **run_kwargs(c, plans[v["table"]], v["budget"], n_paths))
                df["placement"] = "off"
                print(f"{name} {vn}: growth bound "
                      f"{float(df.loc[df['shift'] == 'lower_bound', 'pf_growth_on_base_p50'].iloc[0]):+.4f} point "
                      f"{float(df.loc[df['shift'] == 'point', 'pf_growth_on_base_p50'].iloc[0]):+.4f} "
                      f"({n_paths} paths, {time.time() - t0:.0f} s)", flush=True)
            df.insert(0, "variant", vn)
            df.insert(0, "study_campaign", name)
            df.insert(0, "section", "campaign")
            camp_parts.append(df)
            t1 = time.time()
            fkw = run_kwargs(c, plans[v["table"]], v["budget"], ftp_paths)
            fdf = gate.ftp_sweep(c.blocks, grid, include_off=True, path_hook=hook, workers=int(workers),
                                 on_run=lambda lbl, vn=vn: ps._label(inner, f"{vn} ftp {lbl}"), **fkw)
            bad = a3.own_off_problems(sink, vn, ftp_paths)
            if vn == "reference" and c.ftp_ref is not None:
                bad += c.ftp_ref(fdf, rd, ftp_paths)
            if bad:
                print(f"REFUSED (D-505): {name} {vn}'s program runs are not its own campaign's (or D-495's sweep's) -- "
                      + "; ".join(bad[:8]))
                return 3
            idents.append({"section": "identity", "study_campaign": name, "variant": vn, "holds": True,
                           "paths": int(ftp_paths), "seconds_variant": time.time() - t0,
                           "seconds_program": time.time() - t1,
                           "check": f"the run without the program at {ftp_paths} paths equals the first {ftp_paths} "
                                    "of the variant's own run" + (
                                        f"; the 16 models and the run without equal results/{FTP_SWEEP_FILE}'s fv3c "
                                        f"rows ({', '.join(FTP_SWEEP_COLS)})"
                                        if vn == "reference" and c.ftp_ref is not None
                                        and int(ftp_paths) == int(fs.N_PATHS) else "")})
            base = fdf[fdf["ftp_label"] == "off"].set_index("shift")["growth_on_required"]
            fdf["growth_change_from_off"] = fdf["growth_on_required"].astype(float) - fdf["shift"].map(base).astype(float)
            fdf["arm"] = np.where(fdf["shift"] == "point", "point", "bound")
            fdf["is_gate_row"] = False
            fdf.insert(0, "variant", vn)
            fdf.insert(0, "study_campaign", name)
            fdf.insert(0, "section", "ftp")
            ftp_parts.append(fdf)
            r = a3.variant_row(v, df, fdf)
            r.update({"study_campaign": name, "reading": READING, "seed": int(c.seed)})
            rows.append(r)
            print(f"  {name} {vn}: the program at {ftp_paths} paths: growth at the bound min "
                  f"{r['ftp_growth_bound_min']:+.4f} ({r['ftp_growth_bound_min_model']}), median "
                  f"{r['ftp_growth_bound_median']:+.4f} ({time.time() - t1:.0f} s; {time.time() - t_all:.0f} s so "
                  "far)", flush=True)
        rows_all += a3.with_changes(rows)
    res = pd.concat([pd.DataFrame(rows_all), *camp_parts, *ftp_parts, pd.DataFrame(idents)], ignore_index=True)
    first = ["section", "study_campaign", "variant"]
    res = res[first + [k for k in res.columns if k not in first]]
    n_var = sum(1 for v in todo if v["variant"] != "reference") * len(campaigns)
    if record:
        counter = VariantCounter(path=rd / "variants.jsonl")
        for name in campaigns:
            for v in todo:
                if v["variant"] != "reference":
                    counter.record(prereg_id=FAMILY_ID, seed=SEED, exploratory=True,
                                   params={"study": "FV3-C compliance (D-505)", "campaign": name,
                                           "variant": v["variant"], "table": v["table"],
                                           "budget": list(v["budget"]) if v["budget"] else None,
                                           "paths": int(n_paths)},
                                   label=f"D-505's compliance study on {name}: {v['variant']}")
                for mdl in grid:
                    counter.record(prereg_id=FTP_FAMILY_ID, seed=SEED, exploratory=True,
                                   params={"study": "FV3-C compliance: the Focused Trader Program", "campaign": name,
                                           "variant": v["variant"], **mdl.as_dict(), "paths": int(ftp_paths)},
                                   label=f"Focused Trader Program beside D-505's {name} {v['variant']}: {mdl.label}")
    tab_man = {}
    tp = rd / f"{a3.TABLE_RESULT}.csv.manifest.json"
    if tp.is_file():
        tab_man = json.loads(tp.read_text(encoding="utf-8"))
    params = {"decision": DECISION, "campaigns": {n: {"reference": f"results/{built[n]['c'].ref_file} "
                                                                    f"'{built[n]['c'].ref_run}'",
                                                      "seed": built[n]["c"].seed, "policy_v12": built[n]["c"].policy_id,
                                                      **built[n]["c"].info} for n in campaigns},
              "variants": [{**v, "budget": list(v["budget"]) if v["budget"] else None} for v in todo],
              "budgets": list(a3.BUDGETS), "budget_window_days": a3.BUDGET_WINDOW, "seed": SEED,
              "paths": int(n_paths), "ftp_paths": int(ftp_paths), "levels": [0.0], "placement": "off",
              "one_at_a_time": None, "strict_rule": "none (FV3-C's protocol as frozen)",
              "policy_v12": f"results/{a3.V12_POLICIES} {POLICY_ID}",
              "policy_noclose": f"results/{a3.TABLE_RESULT}_policies.json {a3.NOCLOSE_ID}",
              "policy_noclose_sha256": (tab_man.get("parameters") or {}).get("policies_sha256"),
              "table_result_sha256": tab_man.get("sha256"),
              "ftp_models": [m.as_dict() for m in grid], "ftp_variant_label": FTP_FAMILY_ID, "cost": COST_NOTE,
              "workers": int(workers),
              "metric": "pf_growth_on_base_p50 on pf_required_p90 (the scoreboard's, D-312)"}
    write_result(res, RESULT, script=SCRIPT, seed=SEED, exploratory=True, results_dir=results_dir,
                 variant_count=n_var, parameters=params,
                 notes={"status": READING + "; no selection, no money decision; P-06's window was read once by its "
                                            "verdict -- this describes it, never a second confirmation",
                        "variant_count_rule": "D-501's 9 variants on each of the two campaigns (each reference is a "
                                              "registered configuration); the program's models under " + FTP_FAMILY_ID},
                 description="EXPLORATORY (D-505): D-501's compliance study on FV3-C -- its development campaign and "
                             "P-06's confirmation gate arm, each reproduced first -- under each restraint: the v12 "
                             "table re-solved without closure at request, a self-imposed budget of K Combine purchases "
                             "and resets in any 21 trading days (K = 10, 20, 30, 40), and both; 500 paths at FV3-C's "
                             "seed; growth on the required bankroll at the bound and the point, the required bankroll, "
                             "closures at request, purchases in 21 days, payouts exposed, the break-even denial, and "
                             "the Focused Trader Program's 16 models' minimum and median growth at the bound.")
    parts = []
    for name in campaigns:
        p = pd.DataFrame([r for r in built[name]["sink"] if " ftp " not in str(r["run"])])
        p.insert(0, "study_campaign", name)
        parts.append(p)
    write_result(pd.concat(parts, ignore_index=True), f"{RESULT}_paths", script=SCRIPT, seed=SEED, exploratory=True,
                 results_dir=results_dir, variant_count=n_var, parameters={"result": f"{RESULT}.csv",
                                                                           "decision": DECISION},
                 notes={"status": READING, "companion_of": f"{RESULT}.csv"},
                 description=f"The per-path record of {RESULT}.csv: every path of each campaign's reference and "
                             "variants (point and bound, 0 %), labelled by campaign and variant; the program's runs "
                             "are summarised in their rows, not kept here.")
    show = pd.DataFrame(rows_all).set_index(["study_campaign", "variant"])[
        ["growth_bound", "growth_point", "required_p90_bound", "share_xfa_closed_at_request",
         "mean_max_combine_purchases_21d", "ftp_growth_bound_min", "ftp_growth_bound_median"]]
    pd.set_option("display.width", 200)
    print(show.round(4).to_string())
    return 0


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="each campaign's first --paths reproduced; nothing written")
    ap.add_argument("--paths", type=int, default=None, help="with --check: how many paths (default all 500)")
    ap.add_argument("--campaign", choices=CAMPAIGNS, default=None, help="with --check: one campaign")
    ap.add_argument("--workers", type=int, default=1, help="path workers per campaign (R11; bit for bit)")
    a = ap.parse_args(argv)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    if a.check:
        return study(rd, results_dir, campaigns=(a.campaign,) if a.campaign else CAMPAIGNS,
                     n_paths=int(a.paths or N_PATHS), workers=a.workers, check_only=True, record=False)
    if a.paths is not None or a.campaign is not None:
        print("REFUSED: the study runs both campaigns at 500 paths; --paths and --campaign are for --check.")
        return 2
    return study(rd, results_dir, workers=a.workers)


if __name__ == "__main__":
    raise SystemExit(main())
