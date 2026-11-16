"""EXPLORATORY (D-501): a compliance study on P-13's registered campaign -- does FV3-C's design keep its growth without
the two things P-13's result leans on: closing funded accounts at request (an unverified rule) and heavy Combine buying
(the pattern Topstep's Focused Trader Program names)? Not a candidate search and not a verdict: read beside P-13.

    python scripts/a3_compliance.py --solve-table          # step 1: v12 re-solved as it was (refused unless it
                                                           #   reproduces the stored export), then the no-closure table
    python scripts/a3_compliance.py --check --paths 4      # P-13's first paths reproduced; nothing written
    python scripts/a3_compliance.py                        # step 2: the study (needs step 1's files on record)
    python scripts/a3_compliance.py --workers 2            # each campaign's paths across path workers (R11; bit for bit)

**Step 1, the no-closure table** (`--solve-table`; engine-only, no market data): `config/state_policy_v12.yaml` re-solved
exactly as `scripts/state_policy_dp.py --declaration D-333` solved it, at FV3-C's own edge cell e = -0.050 -- the first
edge of v12's grid, so its rent's fixed point started from the config's `rent_fixed_point.start` ($25), as here: FV3-C's
rungs, shares and availability (`results/fv3_rung_shares_2020.csv`, `results/fv3_rung_availability_2021.csv`), the
oracles first, the rent's fixed point on the exact tables (`state_policy_dp.solve_rent`), the tie-broken table at it
exported as version 12 (`state_policy.export_policy`) with `state_policy_dp.export_description`'s text. **The re-solve
of v12 as it is must reproduce the stored exported policy `state_dp_e-0.050_lamstar` of
`results/state_policy_v12_policies.json` exactly (the whole policy dict) and its rent, `results/state_policy_v12.csv`'s
dp row, to 1e-9; otherwise nothing is solved further and nothing written.** Then the same config with
`funded_rules.abandon: false` -- a funded account ends only by a breach or its payout life; the Combine's cancellation
(8284121) kept -- its oracles first, its own rent's fixed point, exported at the same edge cell as
`state_dp_e-0.050_lamstar_noclose`. Written: `results/state_policy_v12_noclose.csv` (sections `oracle`, `rent_round`,
`dp`, `identity`, one table each) and `results/state_policy_v12_noclose_policies.json` (the no-closure policy; its sha256
in the CSV's manifest).

**Step 2, the study.** P-13's campaign exactly (`a3_brk30`'s trades -- `cell_trades`, the A3 walk read only -- its
0.05 bounds by the screen's era rule, `atlas_a3.run_campaign` under FV3-C's protocol with the day capacity at the busiest
day, the operator's strict rule, 0 % denial, the placement off, the campaign seed 20261028, 500 paths over 504
sessions). **First, P-13's own configuration (the reference) must reproduce `results/a3_brk30_gate_paths.csv`'s `gate`
run, point and bound at 0 %, path for path on `zero_edge_decomposition.PATH_COLS` (its first `--paths`; all 500 in the
study); otherwise nothing more runs and nothing is written.** Then D-501's 9 variants, each on the same trades, bounds,
seed and paths:

==================  ===================================  ===========================================
variant             table                                purchase budget (Combine purchases + resets)
==================  ===================================  ===========================================
reference           v12 (P-13's)                         none
a_noclose           the no-closure table                 none
b_budget{K}         v12                                  K in any 21 trading days, K = 10, 20, 30, 40
c_noclose_budget{K} the no-closure table                 K in any 21 trading days, K = 10, 20, 30, 40
==================  ===================================  ===========================================

The budget is the engine's D-501 option (`lockstep.simulate_lockstep_path(purchase_budget=(K, 21))`): a purchase or a
reset refused while the purchases and resets of the last 21 trading days (that day's included) have reached K.

**Readings per variant (D-501 (2))**, section `variant`: growth on the required bankroll (`pf_growth_on_base_p50` at
`pf_required_p90`, D-312) at the 0.05 bound and at the point, the required bankroll (`pf_required_p90`), the share of
funded accounts closed at request (`pf_share_xfa_abandoned`), Combine purchases in any 21 days
(`mean_max_combine_purchases_21d`), the share of payouts exposed, the break-even denial (`pf_break_even_denial_p50`),
the budget's own counts, and the Focused Trader Program's 16 declared models (D-497's grid, `ftp_sweep.models()`) run
by `gate.ftp_sweep` on the variant's campaign -- their minimum and median growth at the bound, the robust reading --
each with its change from the reference. Every `run_gate` row in section `campaign`, every program row in section
`ftp` (with its change from the variant's own run without the program at the same path count).

**The program's path count is declared here: `FTP_PATHS` = 150** (D-497's sweep's convention), the variants' own runs at
500 -- chosen for cost, measured before the study (`COST_NOTE`: the reference and its 16 models at 20 paths on P-13's
real trades, one process, one BLAS thread, 2026-10-31, beside another job). Each variant's program reading is the 16
models at 150 paths plus the run without the program at 150 paths (whose paths must equal the first 150 of the variant's own run); the
reference's 16 models must also equal the first 150 paths of P-13's own `ftp <model>` runs (the program through
`gate.ftp_sweep` is P-13's program reading), else nothing is written.

Written: `results/a3_compliance.csv` (sections `variant`, `campaign`, `ftp`, `identity`) and
`results/a3_compliance_paths.csv` (the per-path record of the 10 campaigns at 500 paths; the program's runs are not
kept, each a reading summarised in its row). EXPLORATORY: the 9 variants recorded in `results/variants.jsonl` under
`D-501:a3_compliance` (the reference is P-13's registered configuration, not a variant); the program's models on each
of the 10 campaigns under `D-501:a3_compliance_ftp` (D-499's precedent). Read beside P-13, never a gate (D-234); any
variant carried further becomes its own candidate with its own pre-registration and the pool counting this study.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import sys
import time
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

SCRIPT = "scripts/a3_compliance.py"
DECISION = "D-501"
RESULT = "a3_compliance"
FAMILY_ID = f"{DECISION}:a3_compliance"            # D-501 (3): the 9 variants
FTP_FAMILY_ID = f"{DECISION}:a3_compliance_ftp"    # the program's 16 models on each campaign (D-499's precedent)
TABLE_RESULT = "state_policy_v12_noclose"
TABLE_DECLARATION = "D-333"                        # v12's declaration (config/state_policy_v12.yaml's `decision`)
TABLE_VERSION = 12                                 # its export version (state_policy_dp.DECLARATIONS["D-333"])
V12_RESULT = "state_policy_v12.csv"
V12_POLICIES = "state_policy_v12_policies.json"
EDGE = -0.05                                       # FV3-C's own edge cell (P-13's policy, D-492 (3))
POLICY_ID = "state_dp_e-0.050_lamstar"
NOCLOSE_ID = "state_dp_e-0.050_lamstar_noclose"
P13_PATHS = "a3_brk30_gate_paths.csv"              # P-13's per-path record (D-500)
P13_RESULT = "a3_brk30_gate.csv"
BUDGETS = (10, 20, 30, 40)                         # D-501 (1b): K Combine purchases and resets in any 21 trading days
BUDGET_WINDOW = 21
N_PATHS = 500                                      # P-13's paths (a3_brk30.N_PATHS, checked)
FTP_PATHS = 150                                    # the program's path count, declared above (D-497's convention)
#: the measured cost the declaration rests on (filled from the timing run before the study; see the docstring)
COST_NOTE = ("measured: a campaign path-run (one path through 504 sessions, one shift) 0.48 s on the variant's own run "
             "and 0.31 s on the program's runs (placements cut activity); a variant at 500 paths plus its 17 program "
             "runs at 150 paths is about 1,000 x 0.48 + 5,100 x 0.31 = 2,060 s, so the 10 campaigns about 5.7 hours "
             "in one process (budget variants buy less and run faster; --workers 2 about halves it where memory "
             "allows); the program at 500 paths would be about 96 minutes a variant, 16 hours in all")
#: the gate row's columns read into each variant's row (D-501 (2)), at the bound unless named point
READ = {"growth_bound": ("lower_bound", "pf_growth_on_base_p50"), "growth_point": ("point", "pf_growth_on_base_p50"),
        "required_p90_bound": ("lower_bound", "pf_required_p90"), "required_p90_point": ("point", "pf_required_p90"),
        "share_xfa_closed_at_request": ("lower_bound", "pf_share_xfa_abandoned"),
        "share_combines_abandoned": ("lower_bound", "pf_share_combines_abandoned"),
        "mean_max_combine_purchases_21d": ("lower_bound", "mean_max_combine_purchases_21d"),
        "mean_combine_purchases": ("lower_bound", "mean_combine_purchases"),
        "share_payouts_exposed": ("lower_bound", "share_payouts_exposed"),
        "break_even_denial": ("lower_bound", "pf_break_even_denial_p50"),
        "mean_max_mll_breaches_21d": ("lower_bound", "mean_max_mll_breaches_21d"),
        "share_trades_skipped_busy": ("lower_bound", "share_trades_skipped_busy"),
        "realised_to_intended_capped_risk": ("lower_bound", "realised_to_intended_capped_risk"),
        "budget_purchase_days_blocked": ("lower_bound", "mean_budget_purchase_days_blocked"),
        "budget_resets_refused": ("lower_bound", "mean_budget_resets_refused"),
        "budget_max_purchases_in_window": ("lower_bound", "max_budget_purchases_in_window")}
READING = "EXPLORATORY (D-501): beside P-13, never a gate (D-234)"


# ------------------------------------------------------------------------------------------------ the variants


def variants() -> list[dict[str, Any]]:
    """P-13's own configuration (the reference) and D-501's 9 variants, in the order they run."""
    out = [{"variant": "reference", "table": "v12", "budget": None},
           {"variant": "a_noclose", "table": "noclose", "budget": None}]
    out += [{"variant": f"b_budget{k}", "table": "v12", "budget": (int(k), BUDGET_WINDOW)} for k in BUDGETS]
    out += [{"variant": f"c_noclose_budget{k}", "table": "noclose", "budget": (int(k), BUDGET_WINDOW)} for k in BUDGETS]
    return out


# ------------------------------------------------------------------------------------------------ step 1: the table


def _norm(d: Any) -> Any:
    """A policy dict as its JSON file holds it (tuples as lists, numpy scalars as numbers)."""
    return json.loads(json.dumps(d, default=lambda x: x.item() if isinstance(x, np.generic) else str(x)))


def noclose_config(cfg: dict) -> dict:
    """v12's config with the funded table's abandon off (D-501 (1a)); nothing else changes."""
    out = copy.deepcopy(cfg)
    if not bool((out.get("funded_rules") or {}).get("abandon", False)):
        raise SystemExit("REFUSED: the config's funded table has no abandon to turn off.")
    out["funded_rules"]["abandon"] = False
    return out


def abandon_leaves(pol) -> dict[str, int]:
    """The exported policy's abandon leaves by phase ({'combine': n, 'funded': n, 'paid': n})."""
    from propedge.campaign.risk_policy import PHASES

    out = {p: 0 for p in PHASES}
    for leaf, phases in pol.root.leaves(frozenset(PHASES)):
        if getattr(leaf, "abandon", False):
            for p in phases:
                out[p] += 1
    return out


def solve_one(cfg: dict, rules, rd: Path, pid: str, *, description_extra: str = "") -> dict[str, Any]:
    """One table at `EDGE` as `state_policy_dp.main` solves a declared config's first edge: the oracles (refused when one
    fails), the rent's fixed point from the config's start, the tie-broken table at it, exported at `TABLE_VERSION`."""
    import state_policy_dp as dp

    from propedge.campaign import state_policy as sp

    menu = dp.menu_of(cfg, rd)
    orows, ok = dp.oracles(cfg, rules, menu)
    for r in orows:
        print(f"  oracle {r['check']}: {r['value']:.6f} {r['relation']} {r['bound']} -> "
              f"{'held' if r['held'] else 'FAILED'}", flush=True)
    if not ok:
        raise SystemExit("REFUSED: an oracle failed; the DP is wrong, not the contract.")
    t0 = time.time()
    lam, objs, rounds = dp.solve_rent(cfg, rules, EDGE, menu, float(cfg["rent_fixed_point"]["start"]))
    f, fsol, ff, c, csol, cf = objs
    cash, days, rate = dp.cycle_rate(rules, ff, cf)
    exact = [x for x in rounds if not x["tie_break"]]
    row = dp.row_of("dp", EDGE, lam, "dp", rules, fsol, ff, csol, cf)
    row.update({"rent_mode": "fixed_point", "rent_rate": rate, "rent_rounds": len(exact),
                "rent_converged_by": rounds[-1].get("converged_by"), "rent_rate_exact": exact[-1]["rate"],
                "rent_rate_best_round": max(x["rate"] for x in exact), "rent_tie_break_price": exact[-1]["rate"] - rate,
                "cycle_cash": cash, "cycle_slot_days": days, "combine_p_abandon": cf.get("p_abandon", 0.0),
                "xfa_p_abandoned": ff.get("p_abandoned", 0.0), "policy_id": pid})
    bands = cfg["export"]
    pol, info = sp.export_policy(pid, c, cf["visitation"], f, ff["visitation"], float(bands["balance_band"]),
                                 float(bands["cushion_band"]), version=TABLE_VERSION, c_pol0=csol.policy[0],
                                 f_pol0=fsol.policy[0],
                                 description=dp.export_description(cfg, EDGE, lam, TABLE_VERSION) + description_extra)
    row.update({"combine_skip_mass": info["combine_skip_mass"], "funded_skip_mass": info["funded_skip_mass"],
                "paid_skip_mass": info["paid_skip_mass"], "no_trade_bands": len(info["idle_bands"]),
                "conduct_flags": "; ".join(pol.conduct_flags()), "seconds": time.time() - t0})
    print(f"  {pid}: lambda* ${lam:.6f}/day, the exported table earns ${rate:.4f}/day, p_pass {cf['p_pass']:.4f}, "
          f"xfa abandoned {ff.get('p_abandoned', 0.0):.4f} ({time.time() - t0:.0f} s)", flush=True)
    return {"lam": float(lam), "policy": pol, "dp_row": row, "oracles": orows, "rounds": rounds}


def v12_stored(rd: Path) -> tuple[dict, float]:
    """(the stored export at FV3-C's cell, its rent from the v12 file's dp row)."""
    from propedge.reporting.results import verify_result

    ok, msg = verify_result(rd / V12_RESULT)
    if not ok:
        raise SystemExit(f"REFUSED: {V12_RESULT}: {msg}")
    pols = json.loads((rd / V12_POLICIES).read_text(encoding="utf-8"))
    if POLICY_ID not in pols:
        raise SystemExit(f"REFUSED: {V12_POLICIES} holds no {POLICY_ID}.")
    tab = pd.read_csv(rd / V12_RESULT, float_precision="round_trip", low_memory=False)
    row = tab[(tab["section"] == "dp") & (tab["policy_id"].astype(str) == POLICY_ID)]
    if len(row) != 1:
        raise SystemExit(f"REFUSED: {V12_RESULT} holds {len(row)} dp rows for {POLICY_ID}, not one.")
    return pols[POLICY_ID], float(row.iloc[0]["slot_rent"])


def identity_problems(solved: dict, stored: dict, stored_rent: float) -> list[str]:
    """The re-solve of v12 against its stored export: the whole policy dict equal, the rent to 1e-9."""
    out = []
    mine = _norm(solved["policy"].as_dict())
    if mine != _norm(stored):
        keys = sorted(k for k in set(mine) | set(stored) if mine.get(k) != stored.get(k))
        out.append(f"the exported policy differs from the stored {POLICY_ID} (fields {keys})")
    if not abs(solved["lam"] - stored_rent) <= 1e-9:
        out.append(f"lambda* {solved['lam']!r} against the stored {stored_rent!r}")
    return out


def solve_table(rd: Path, results_dir: Path | None, *, cfg: dict | None = None, rules=None,
                stored: tuple[dict, float] | None = None) -> int:
    """Step 1: v12 re-solved as it was (refused unless it is the stored export), then the no-closure table."""
    import state_policy_dp as dp

    from propedge.campaign.payout_method import rules_for_method
    from propedge.reporting.results import write_result

    if cfg is None:
        cfg = dp.config(dp.config_for(TABLE_VERSION))
        if str(cfg.get("decision")) != TABLE_DECLARATION or dp.DECLARATIONS.get(TABLE_DECLARATION) != TABLE_VERSION:
            raise SystemExit("REFUSED: config/state_policy_v12.yaml is not D-333's export version 12.")
        if dp.rent_mode(cfg) != "fixed_point" or not np.isclose(dp.edges_of(cfg)[0], EDGE):
            raise SystemExit("REFUSED: v12's grid does not start at FV3-C's cell, so its rent's start is not the config's.")
    rules = rules_for_method(cfg["campaign_check"]["payout_method"]) if rules is None else rules
    stored_pol, stored_rent = v12_stored(rd) if stored is None else stored
    print(f"v12 re-solved as it is (e = {EDGE:+.3f}):", flush=True)
    v12 = solve_one(cfg, rules, rd, POLICY_ID)
    bad = identity_problems(v12, stored_pol, stored_rent)
    if bad:
        print("REFUSED (D-501): the re-solve of v12 does not reproduce its stored export -- " + "; ".join(bad))
        return 3
    print(f"  identity HOLDS: the re-solved export equals {V12_POLICIES}'s {POLICY_ID} and its rent", flush=True)
    cfg2 = noclose_config(cfg)
    print(f"the no-closure table (funded_rules.abandon false, e = {EDGE:+.3f}):", flush=True)
    nc = solve_one(cfg2, rules, rd, NOCLOSE_ID,
                   description_extra=" -- D-501: re-solved with funded_rules.abandon false (no closure at request: a "
                                     "funded account ends by a breach or its payout life; the Combine's cancellation "
                                     "kept); EXPLORATORY")
    leaves = abandon_leaves(nc["policy"])
    if leaves["funded"] or leaves["paid"]:
        print(f"REFUSED (D-501): the no-closure table still closes funded accounts ({leaves}).")
        return 3
    nc["policy"].validate()
    rows = []
    for name, s in (("v12", v12), ("noclose", nc)):
        rows += [{**r, "table": name} for r in s["oracles"]]
        rows += [{"section": "rent_round", "table": name, "edge": EDGE, **r} for r in s["rounds"]]
        rows.append({**s["dp_row"], "table": name, **{f"abandon_leaves_{k}": v
                                                       for k, v in abandon_leaves(s["policy"]).items()}})
    rows.append({"section": "identity", "table": "v12", "policy_id": POLICY_ID, "holds": True,
                 "check": f"v12 re-solved as D-333 solved it at e={EDGE:+.3f} equals {V12_POLICIES}'s {POLICY_ID} "
                          f"(the whole policy dict) and {V12_RESULT}'s rent to 1e-9",
                 "slot_rent": v12["lam"], "stored_slot_rent": stored_rent})
    payload = json.dumps({NOCLOSE_ID: nc["policy"].as_dict()}, indent=1).replace("\r\n", "\n")
    sha = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    write_result(pd.DataFrame(rows), TABLE_RESULT, script=SCRIPT, seed=int(cfg["campaign_check"]["seed"]),
                 exploratory=True, results_dir=results_dir,
                 parameters={"decision": DECISION, "config": "config/state_policy_v12.yaml",
                             "declaration_solved": TABLE_DECLARATION, "export_version": TABLE_VERSION, "edge": EDGE,
                             "change": "funded_rules.abandon: false (everything else v12's)",
                             "rent_start": float(cfg["rent_fixed_point"]["start"]),
                             "rungs": cfg.get("rungs"), "policy_id": NOCLOSE_ID,
                             "policies_json": f"results/{TABLE_RESULT}_policies.json", "policies_sha256": sha,
                             "v12_identity": f"the re-solve of v12 equals {V12_POLICIES}'s {POLICY_ID} and its rent",
                             "lambda_star_v12": v12["lam"], "lambda_star_noclose": nc["lam"]},
                 notes={"status": "EXPLORATORY (D-501 (1a)): engine-only, stage one's binary outcomes on FV3-C's rungs; "
                                  "an input to the compliance study, not a candidate",
                        "seed": "the config's campaign-check seed, recorded for the manifest; the DP draws nothing"},
                 description="D-501 (1a): FV3-C's v12 table re-solved at its own edge cell exactly as D-333 solved it "
                             "(its stored export reproduced first), then with the funded table's abandon off -- no "
                             "closure at request -- its oracles, its rent's fixed point and its export (version 12) at "
                             "the same cell; the policy in the companion JSON.")
    pj = (Path(results_dir) if results_dir is not None else rd) / f"{TABLE_RESULT}_policies.json"
    pj.write_text(payload, encoding="utf-8", newline="\n")
    print(f"written: {TABLE_RESULT}.csv and its policies file (lambda* v12 ${v12['lam']:.4f}, no closure "
          f"${nc['lam']:.4f})")
    return 0


def noclose_policy(rd: Path):
    """The no-closure table's exported policy, checked against its result file's manifest (its sha256)."""
    from propedge.campaign.risk_policy import RiskPolicy
    from propedge.reporting.results import verify_result

    path = rd / f"{TABLE_RESULT}.csv"
    ok, msg = verify_result(path)
    if not ok:
        raise SystemExit(f"REFUSED: {TABLE_RESULT}.csv: {msg} (run --solve-table first)")
    man = json.loads(Path(str(path) + ".manifest.json").read_text(encoding="utf-8"))
    pj = rd / f"{TABLE_RESULT}_policies.json"
    # D-503: hashed line-ending-free -- git's checkout on Windows turns the committed LF into CRLF (results/*.json are
    # text=auto), which changes the bytes and not one value; the recorded hash is of the LF file the solve wrote
    if hashlib.sha256(pj.read_bytes().replace(b"\r\n", b"\n")).hexdigest() != (man.get("parameters") or {}).get(
            "policies_sha256"):
        raise SystemExit(f"REFUSED: {pj.name} is not the file its result recorded.")
    p = RiskPolicy.from_dict(json.loads(pj.read_text(encoding="utf-8"))[NOCLOSE_ID])
    p.validate()
    leaves = abandon_leaves(p)
    if leaves["funded"] or leaves["paid"]:
        raise SystemExit(f"REFUSED: the no-closure policy closes funded accounts ({leaves}).")
    return p


# ------------------------------------------------------------------------------------------------ step 2: the study


def campaign_inputs(L: dict, t: pd.DataFrame, days: list[str]) -> dict[str, Any]:
    """P-13's campaign inputs exactly as its registered run builds them: the blocks, the 0.05 bounds by the screen's
    era rule (`atlas_a3.bounds`, which `a3_brk30.bounds_at_n` checks against), the day capacity, the policy."""
    import a3_brk30 as B
    import atlas_a3 as A
    import score_fv3_grid as gf

    keys = B.rrs(t)
    _, e_by, lb_by, _, flagged = A.bounds(t, days, keys, L["cfg"])
    blocks, n_used = gf.gate_blocks(t, days, float(L["tv"]), keys, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise SystemExit("REFUSED: the blocks hold a different number of trades.")
    return {"blocks": blocks, "e_by": e_by, "lb_by": lb_by, "flagged": bool(flagged), "cap": B.capacity(t, L["fcfg"]),
            "policy": B.policy(L), "trades": int(len(t)), "days": int(len(days))}


def reference_problems(sink: list[dict], rd: Path, n: int, *, ftp_labels=(), ftp_n: int | None = None) -> list[str]:
    """The reference against P-13's per-path record: its run at 0 %, point and bound, the first `n` paths of P-13's
    `gate`; with `ftp_labels`, each program model's run the first `ftp_n` paths of P-13's `ftp <model>`."""
    import zero_edge_decomposition as zd

    from propedge.reporting.results import read_result

    ref = read_result(rd / P13_PATHS)
    out = zd.path_problems(sink, ref, [("reference", s, "gate", s) for s in ("point", "lower_bound")], int(n))
    if ftp_labels:
        pairs = [(f"reference ftp {lbl}", s, f"ftp {lbl}", s) for lbl in ftp_labels for s in ("point", "lower_bound")]
        out += zd.path_problems(sink, ref, pairs, int(ftp_n))
    return out


def own_off_problems(sink: list[dict], name: str, n: int) -> list[str]:
    """A variant's run without the program at the program's path count against the first `n` paths of its own run."""
    import zero_edge_decomposition as zd

    ref = pd.DataFrame([r for r in sink if r["run"] == name])
    return zd.path_problems(sink, ref, [(f"{name} ftp off", s, name, s) for s in ("point", "lower_bound")], int(n))


def variant_row(v: dict, df: pd.DataFrame, ftp_df: pd.DataFrame | None) -> dict[str, Any]:
    """One variant's readings (D-501 (2)) from its run's rows and its program rows."""
    by = df[np.isclose(df["enforcement_p"].astype(float), 0.0)].set_index("shift")
    row = {"section": "variant", "variant": v["variant"], "table": v["table"],
           "budget_k": float(v["budget"][0]) if v["budget"] else float("nan"),
           "budget_window_days": float(v["budget"][1]) if v["budget"] else float("nan"),
           "risk_policy": str(by.loc["lower_bound", "risk_policy"]), "paths": int(by.loc["lower_bound", "paths"]),
           "reading": READING}
    for k, (shift, col) in READ.items():
        row[k] = float(by.loc[shift, col]) if col in by.columns and pd.notna(by.loc[shift, col]) else float("nan")
    if ftp_df is not None:
        m = ftp_df[ftp_df["ftp_label"] != "off"]
        for arm, shift in (("bound", "lower_bound"), ("point", "point")):
            g = m[m["shift"] == shift]["growth_on_required"].astype(float)
            row[f"ftp_growth_{arm}_min"] = float(g.min()) if len(g) else float("nan")
            row[f"ftp_growth_{arm}_median"] = float(g.median()) if len(g) else float("nan")
        b = m[m["shift"] == "lower_bound"].reset_index(drop=True)
        gb = b["growth_on_required"].astype(float)
        row["ftp_growth_bound_min_model"] = str(b.loc[int(np.nanargmin(gb.to_numpy())), "ftp_label"]) if len(b) else ""
        row["ftp_share_models_growth_bound_positive"] = float((gb > 0).mean()) if len(gb) else float("nan")
        row["ftp_models"] = int(m["ftp_label"].nunique())
        row["ftp_paths"] = int(m["paths"].iloc[0]) if len(m) else 0
        off = ftp_df[(ftp_df["ftp_label"] == "off") & (ftp_df["shift"] == "lower_bound")]
        row["ftp_off_growth_bound"] = float(off["growth_on_required"].iloc[0]) if len(off) else float("nan")
    return row


def with_changes(rows: list[dict]) -> list[dict]:
    """Each variant's readings with their change from the reference's."""
    ref = next(r for r in rows if r["variant"] == "reference")
    keys = [k for k in ("growth_bound", "growth_point", "required_p90_bound", "share_xfa_closed_at_request",
                        "mean_max_combine_purchases_21d", "share_payouts_exposed", "break_even_denial",
                        "ftp_growth_bound_min", "ftp_growth_bound_median") if k in ref]
    return [{**r, **{f"{k}_change": float(r.get(k, float("nan"))) - float(ref[k]) for k in keys}} for r in rows]


def study(rd: Path, results_dir: Path | None, *, L: dict | None = None, t: pd.DataFrame | None = None,
          days: list[str] | None = None, n_paths: int = N_PATHS, ftp_paths: int = FTP_PATHS, workers: int = 1,
          check_only: bool = False, which: list[str] | None = None, record: bool = True) -> int:
    """Step 2: the reference reproduced, then the variants with their program readings; the files."""
    import a3_brk30 as B
    import atlas_a3 as A
    import fv3d_lever_test as lt
    import ftp_sweep as fs
    import portfolio_stage as ps

    from propedge.campaign import gate
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import write_result

    if B.N_PATHS != N_PATHS or B.SEED != 20261028 or B.STRICT_GAP != 5.0:
        raise SystemExit("REFUSED: a3_brk30's registered paths, seed or strict rule are not the ones declared here.")
    if L is None:
        L = B.inputs()
    if t is None:
        t, days = B.cell_trades(L)
    ci = campaign_inputs(L, t, days)
    fcfg = L["fcfg"]
    horizon = int(fcfg["gate"]["campaign"]["horizon_days"])
    grid = fs.models()
    if len(grid) != B.FTP_MODELS:
        raise SystemExit(f"REFUSED: the program's grid holds {len(grid)} models, not {B.FTP_MODELS} (D-497).")
    todo = variants() if not which else [v for v in variants() if v["variant"] in set(which) | {"reference"}]
    plans = {"v12": ci["policy"]}
    if any(v["table"] == "noclose" for v in todo) and not check_only:
        plans["noclose"] = noclose_policy(rd)
    sink: list[dict] = []
    inner = ps.composed_hook({"margin": float(fcfg["portfolio"]["margin"]),
                              "block_days": int(fcfg["portfolio"]["block_days"])}, sink=sink)
    hook = lt.lever_hook(inner)

    def kwargs(v: dict, n: int) -> dict:
        return A.gate_kwargs(ci["blocks"], fcfg, float(L["tv"]), plans[v["table"]], ci["e_by"], ci["lb_by"], hook,
                             seed=B.SEED, n_paths=int(n), horizon=horizon, capacity=ci["cap"], levels=(0.0,),
                             rtp=False, one_at_a_time=B.STRICT_GAP, purchase_budget=v["budget"])

    rows, camp_parts, ftp_parts, idents = [], [], [], []
    t_all = time.time()
    for v in todo:
        name = v["variant"]
        t0 = time.time()
        ps._label(inner, name)
        kw = kwargs(v, n_paths)
        df, _ = gate.run_gate(kw.pop("blocks"), workers=int(workers), **kw)
        df["placement"] = "off"
        print(f"{name}: growth bound {float(df.loc[df['shift'] == 'lower_bound', 'pf_growth_on_base_p50'].iloc[0]):+.4f}"
              f" point {float(df.loc[df['shift'] == 'point', 'pf_growth_on_base_p50'].iloc[0]):+.4f} "
              f"({n_paths} paths, {time.time() - t0:.0f} s)", flush=True)
        if name == "reference":
            bad = reference_problems(sink, rd, n_paths)
            if bad:
                print("REFUSED (D-501): P-13's campaign does not reproduce its per-path record -- " + "; ".join(bad[:8]))
                return 3
            idents.append({"section": "identity", "variant": name, "holds": True, "paths": int(n_paths),
                           "check": f"P-13's configuration reproduces the first {n_paths} paths of {P13_PATHS}'s gate "
                                    "run at 0 %, point and bound"})
            print(f"  P-13 reproduced: the first {n_paths} paths of its gate run, point and bound", flush=True)
            if check_only:
                print("the reference holds; nothing written (--check).")
                return 0
        df.insert(0, "variant", name)
        df.insert(0, "section", "campaign")
        camp_parts.append(df)
        t1 = time.time()
        fkw = kwargs(v, ftp_paths)
        blocks = fkw.pop("blocks")
        fkw.pop("path_hook")
        fdf = gate.ftp_sweep(blocks, grid, include_off=True, path_hook=hook, workers=int(workers),
                             on_run=lambda lbl, name=name: ps._label(inner, f"{name} ftp {lbl}"), **fkw)
        bad = own_off_problems(sink, name, ftp_paths)
        if name == "reference":
            bad += reference_problems(sink, rd, n_paths, ftp_labels=[m.label for m in grid], ftp_n=ftp_paths)
        if bad:
            print(f"REFUSED (D-501): {name}'s program runs are not its own campaign's (or P-13's) -- " + "; ".join(bad[:8]))
            return 3
        idents.append({"section": "identity", "variant": name, "holds": True, "paths": int(ftp_paths),
                       "check": f"the run without the program at {ftp_paths} paths equals the first {ftp_paths} of "
                                f"the variant's own run" + (f"; each of the 16 models equals the first {ftp_paths} "
                                                            f"paths of {P13_PATHS}'s ftp run"
                                                            if name == "reference" else "")})
        base = fdf[fdf["ftp_label"] == "off"].set_index("shift")["growth_on_required"]
        fdf["growth_change_from_off"] = fdf["growth_on_required"].astype(float) - fdf["shift"].map(base).astype(float)
        fdf["arm"] = np.where(fdf["shift"] == "point", "point", "bound")
        fdf["is_gate_row"] = False
        fdf.insert(0, "variant", name)
        fdf.insert(0, "section", "ftp")
        ftp_parts.append(fdf)
        rows.append(variant_row(v, df, fdf))
        r = rows[-1]
        print(f"  the program at {ftp_paths} paths: growth at the bound min {r['ftp_growth_bound_min']:+.4f} "
              f"({r['ftp_growth_bound_min_model']}), median {r['ftp_growth_bound_median']:+.4f} "
              f"({time.time() - t1:.0f} s; {time.time() - t_all:.0f} s so far)", flush=True)
    rows = with_changes(rows)
    res = pd.concat([pd.DataFrame(rows), *camp_parts, *ftp_parts, pd.DataFrame(idents)], ignore_index=True)
    n_var = sum(1 for v in todo if v["variant"] != "reference")
    if record:
        counter = VariantCounter(path=rd / "variants.jsonl")
        for v in todo:
            if v["variant"] != "reference":
                counter.record(prereg_id=FAMILY_ID, seed=B.SEED, exploratory=True,
                               params={"study": "A3-BRK30 compliance (D-501)", "variant": v["variant"],
                                       "table": v["table"], "budget": list(v["budget"]) if v["budget"] else None,
                                       "paths": int(n_paths), "horizon": horizon},
                               label=f"D-501's compliance study on P-13's campaign: {v['variant']}")
            for mdl in grid:
                counter.record(prereg_id=FTP_FAMILY_ID, seed=B.SEED, exploratory=True,
                               params={"study": "A3-BRK30 compliance: the Focused Trader Program", "variant": v["variant"],
                                       **mdl.as_dict(), "paths": int(ftp_paths), "horizon": horizon},
                               label=f"Focused Trader Program beside D-501's {v['variant']}: {mdl.label}")
    tab_man = {}
    tp = rd / f"{TABLE_RESULT}.csv.manifest.json"
    if tp.is_file():
        tab_man = json.loads(tp.read_text(encoding="utf-8"))
    params = {"decision": DECISION, "registration": "P-13", "model": B.MODEL, "cell": B.cell_label(),
              "variants": [{**v, "budget": list(v["budget"]) if v["budget"] else None} for v in todo],
              "budgets": list(BUDGETS), "budget_window_days": BUDGET_WINDOW, "seed": B.SEED, "paths": int(n_paths),
              "ftp_paths": int(ftp_paths), "horizon": horizon, "one_at_a_time": B.STRICT_GAP, "levels": [0.0],
              "placement": "off", "trades": ci["trades"], "days": ci["days"], "capacity": ci["cap"],
              "era_flagged": ci["flagged"], "policy_v12": f"results/{V12_POLICIES} {POLICY_ID}",
              "policy_noclose": f"results/{TABLE_RESULT}_policies.json {NOCLOSE_ID}",
              "policy_noclose_sha256": (tab_man.get("parameters") or {}).get("policies_sha256"),
              "table_result_sha256": tab_man.get("sha256"),
              "ftp_models": [m.as_dict() for m in grid], "ftp_variant_label": FTP_FAMILY_ID,
              "cost": COST_NOTE, "workers": int(workers),
              "reference_identity": f"the reference reproduces the first {n_paths} paths of results/{P13_PATHS}'s gate "
                                    f"run and the first {ftp_paths} of each of its ftp runs",
              "metric": "pf_growth_on_base_p50 on pf_required_p90 (the scoreboard's, D-312)"}
    write_result(res, RESULT, script=SCRIPT, seed=B.SEED, exploratory=True, results_dir=results_dir,
                 variant_count=n_var, parameters=params,
                 notes={"status": READING + "; no selection, no money decision",
                        "variant_count_rule": "D-501's 9 variants (the reference is P-13's registered configuration); "
                                              "the program's models on each campaign under " + FTP_FAMILY_ID},
                 description="EXPLORATORY (D-501): P-13's registered campaign (A3-BRK30) under each restraint -- FV3-C's "
                             "v12 table re-solved without closure at request, a self-imposed budget of K Combine "
                             "purchases and resets in any 21 trading days (K = 10, 20, 30, 40), and both -- 500 paths "
                             "at P-13's seed; growth on the required bankroll at the bound and the point, the required "
                             "bankroll, closures at request, purchases in 21 days, payouts exposed, the break-even "
                             "denial, and the Focused Trader Program's 16 models' minimum and median growth at the "
                             "bound; beside P-13, never a gate.")
    paths = pd.DataFrame([r for r in sink if " ftp " not in str(r["run"])])
    write_result(paths, f"{RESULT}_paths", script=SCRIPT, seed=B.SEED, exploratory=True, results_dir=results_dir,
                 variant_count=n_var, parameters={"result": f"{RESULT}.csv", "decision": DECISION},
                 notes={"status": READING, "companion_of": f"{RESULT}.csv"},
                 description=f"The per-path record of {RESULT}.csv: every path of the reference's and each variant's "
                             "campaign (point and bound, 0 %), labelled by variant; the program's runs are summarised "
                             "in their rows, not kept here.")
    show = pd.DataFrame(rows).set_index("variant")[["growth_bound", "growth_point", "required_p90_bound",
                                                    "share_xfa_closed_at_request", "mean_max_combine_purchases_21d",
                                                    "ftp_growth_bound_min", "ftp_growth_bound_median"]]
    pd.set_option("display.width", 200)
    print(show.round(4).to_string())
    return 0


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--solve-table", action="store_true", help="step 1: v12 re-solved, then the no-closure table")
    ap.add_argument("--check", action="store_true", help="P-13's first --paths reproduced; nothing written")
    ap.add_argument("--paths", type=int, default=None, help="with --check: how many of P-13's paths (default all)")
    ap.add_argument("--workers", type=int, default=1, help="path workers per campaign (R11; bit for bit)")
    a = ap.parse_args(argv)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    if a.solve_table:
        return solve_table(rd, results_dir)
    if a.check:
        return study(rd, results_dir, n_paths=int(a.paths or N_PATHS), workers=a.workers, check_only=True,
                     record=False)
    if a.paths is not None:
        print("REFUSED: the study runs P-13's 500 paths; --paths is for --check.")
        return 2
    return study(rd, results_dir, workers=a.workers)


if __name__ == "__main__":
    raise SystemExit(main())
