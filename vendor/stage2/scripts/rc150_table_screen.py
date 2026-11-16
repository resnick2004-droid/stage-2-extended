"""EXPLORATORY (D-559): the account-state table re-solved on the 37.5-point news-safe coin's own outcomes, screened
against P-16's cell with v12's no-closure table -- the contract's own lever, not a fit to prices.

    python scripts/rc150_table_screen.py --solve-only           # the table solved, its oracles and its differences from
                                                                 # v12's no-closure table; no campaign; nothing written
    python scripts/rc150_table_screen.py --check --paths 4      # the solve, the cell's identity and every run at 4 paths;
                                                                 # nothing written, no growth printed
    python scripts/rc150_table_screen.py --workers 2            # the reading (500 paths); writes the files

**The table** (FV3-C's solver, `scripts/state_policy_dp.py`, as family A2 and T24 re-solved it per cell): v12's
declared config exactly (`config/state_policy_v12.yaml`: its menus, the Combine's and the funded leg's rules, the rent's
fixed point, the oracles, the export bands, version 12) with three changes, each the cell's own: (1) **no closure at
request** -- `funded_rules.abandon` false (`a3_compliance.noclose_config`, D-501 (1a)), as P-14's and P-16's table;
(2) **one rung at the cell's stop** -- 150 ticks at the declared tick value (a micro's risk at the stop), its share one,
the Combine's 50-micro allowance and the funded ladder (0: 20, 1,500: 30, 2,000: 50) and the exit grid as v12's, each
exit-grid R's availability the share of the cell's offered trades carrying an outcome at that R; (3) **the edge** -- the
cell's own one-sided 0.05 bound at the fresh funded leg's R (`atlas_a3.bounds`, the era rule, the gate's shift), as
`score_fv3_grid.policy_for_edge` reads a cell's bound to pick v12's grid edge -- here solved at that bound exactly,
not the nearest grid edge. The oracles first (stage one's ceilings at zero edge without fees; refused if one fails);
the export at the rent's fixed point (lambda*); refused if any funded or paid state closes the account. The policy is
written beside the result (`results/rc150_table_screen_policies.json`) and its line-ending-free sha256 recorded in the
manifest (D-503).

**The screen**, through `rc_screen.Runner` (P-14's / P-16's engine call: the purchase budget, the strict rule, five
Topstep seats, the placement off, 0 % denial, the table's own sizing) at the screen's seeds (campaign 20261131, coin
20261102), 500 paths: the cell with v12's no-closure table (`v12`) and with the re-solved table (`resolved`), each with
its zero-edge twin; the gate rows at the bound and the point, the required bankroll, the trades taken a session; the
funded and Combine realised dollars per trading leaf of each table at 150 ticks (`resolved_coin.width_sizing`, sizing
only); the table's differences from v12's no-closure table state by state (section `table_diff`, from the tables only).

**Identities first, each refusing:** the cell's trades as `rc_width_screen.build` builds them, their content hash equal
to `rc150_dev_test.TRADES_SHA256` (D-543) and their count to the screen's `rc_s150_all` row; at 500 paths the `v12` arm
reproduces `results/rc_width_screen.csv`'s `rc_s150_all` growth at the bound and the point and its required bankroll.

Writes `results/rc150_table_screen.csv` with its manifest and the policies file (EXPLORATORY; variants under
`D-559:rc150_table`). A run below 500 paths is `--check` and writes nothing.
"""
from __future__ import annotations

import argparse
import copy
import dataclasses
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

if __name__ == "__main__":                 # one BLAS thread, before numpy loads (D-464 (5))
    for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import rc_screen as S  # noqa: E402
import rc_width_screen as W  # noqa: E402

SCRIPT = "scripts/rc150_table_screen.py"
DECISION = "D-559"
RESULT = "rc150_table_screen"
FAMILY_ID = f"{DECISION}:rc150_table"
CELL = "rc_s150_all"
STOP = 150
N_PATHS = S.N_PATHS
TABLE_VERSION = 12
SCREEN_FILE = "rc_width_screen.csv"
POLICIES = f"{RESULT}_policies.json"
READING = ("EXPLORATORY (D-559): the state table re-solved on the 37.5-point coin's own outcomes, screened beside v12's "
           "no-closure table; no verdict")
IDENT_COLS = (("growth_on_required", "lower_bound", "pf_growth_on_base_p50"),
              ("growth_on_required_point", "point", "pf_growth_on_base_p50"),
              ("required_p90", "lower_bound", "pf_required_p90"))
#: the phases the table decides and the state grid its differences are read on (band midpoints of both tables' cuts)
PHASES = ("combine", "funded", "paid")


# ------------------------------------------------------------------------------------------------ the table


def cell_rungs(t: pd.DataFrame, v12_rungs: Any, stop_ticks: int, tick_value: float):
    """One rung at the cell's stop: a micro's risk there, share one, v12's allowances and exit grid, each exit-grid R's
    availability the share of the cell's trades carrying an outcome (`r_<R>` finite) at that R."""
    from propedge.campaign import state_policy as sp

    grid = tuple(float(x) for x in v12_rungs.exit_grid)
    av = []
    for R in grid:
        col = f"r_{R:g}"
        share = float(np.isfinite(pd.to_numeric(t[col], errors="coerce")).mean()) if col in t.columns else 0.0
        av.append((R, share))
    return sp.Rungs(risk_per_contract=(float(stop_ticks) * float(tick_value),), shares=(1.0,),
                    combine_cap=int(v12_rungs.combine_cap), funded_caps=tuple(v12_rungs.funded_caps),
                    exit_grid=grid, availability=(tuple(av),))


def cell_edge(t: pd.DataFrame, days: list[str], I: dict[str, Any]) -> tuple[float, float, dict, dict]:
    """(the fresh funded leg's R, the cell's 0.05 bound there, e by R, the bound by R) -- `atlas_a3.bounds`, the era
    rule, as `rc_screen.Runner` reads them for the gate's shift."""
    import a3_brk30 as B
    import atlas_a3 as A

    L = I["L"]
    _, e_by, lb_by, _, _ = A.bounds(t, days, B.rrs(t), L["cfg"])
    fr = float(L["fcfg"]["state_policy"]["fresh"]["funded_rr"])
    if fr not in lb_by or not np.isfinite(float(lb_by[fr])):
        raise SystemExit(f"REFUSED ({DECISION}): the cell has no bound at the fresh funded R {fr:g}.")
    return fr, float(lb_by[fr]), {float(k): float(v) for k, v in e_by.items()}, \
        {float(k): float(v) for k, v in lb_by.items()}


def solve_table(t: pd.DataFrame, edge: float, tick_value: float, *, stop_ticks: int = STOP) -> dict[str, Any]:
    """v12's config with no closure and one rung at the cell's stop, solved at `edge`: the oracles (refused when one
    fails), lambda*, the tie-broken export at version 12. Returns the policy, its rows and its inputs."""
    import a3_compliance as a3
    import state_policy_dp as dp

    from propedge.campaign import state_policy as sp
    from propedge.campaign.payout_method import rules_for_method

    cfg = a3.noclose_config(dp.config(dp.config_for(TABLE_VERSION)))
    if dp.rent_mode(cfg) != "fixed_point":
        raise SystemExit(f"REFUSED ({DECISION}): v12's rent is not the fixed point.")
    rules = rules_for_method(cfg["campaign_check"]["payout_method"])
    base = dp.menu_of(cfg)
    rungs = cell_rungs(t, base.rungs, stop_ticks, tick_value)
    menu = dataclasses.replace(base, rungs=rungs)
    if menu.abandon:
        raise SystemExit(f"REFUSED ({DECISION}): the funded menu still offers closure at request.")
    orows, ok = dp.oracles(cfg, rules, menu)
    if not ok:
        raise SystemExit(f"REFUSED ({DECISION}): an oracle failed at the cell's rung; the table is wrong, not the "
                         "contract -- " + "; ".join(f"{r['check']} {r['value']:.6f}" for r in orows if not r["held"]))
    t0 = time.time()
    lam, objs, rounds = dp.solve_rent(cfg, rules, float(edge), menu, float(cfg["rent_fixed_point"]["start"]))
    f, fsol, ff, c, csol, cf = objs
    cash, days, rate = dp.cycle_rate(rules, ff, cf)
    pid = f"rc150_table_e{float(edge):+.4f}_lamstar_noclose"
    bands = cfg["export"]
    pol, info = sp.export_policy(pid, c, cf["visitation"], f, ff["visitation"], float(bands["balance_band"]),
                                 float(bands["cushion_band"]), version=TABLE_VERSION, c_pol0=csol.policy[0],
                                 f_pol0=fsol.policy[0],
                                 description=dp.export_description(cfg, float(edge), lam, TABLE_VERSION)
                                 + f" -- D-559: v12 with no closure, one rung at {stop_ticks} ticks (the 37.5-point "
                                   "coin's), solved at the cell's own bound; EXPLORATORY")
    pol.validate()
    leaves = a3.abandon_leaves(pol)
    if leaves["funded"] or leaves["paid"]:
        raise SystemExit(f"REFUSED ({DECISION}): the re-solved table closes funded accounts ({leaves}).")
    row = dp.row_of("dp", float(edge), lam, "dp", rules, fsol, ff, csol, cf)
    row.update({"section": "table", "policy_id": pid, "rent_rate": rate, "cycle_cash": cash, "cycle_slot_days": days,
                "rent_rounds": len([x for x in rounds if not x["tie_break"]]),
                "combine_p_abandon": cf.get("p_abandon", 0.0), "xfa_p_abandoned": ff.get("p_abandoned", 0.0),
                "risk_per_contract": float(stop_ticks) * float(tick_value),
                "availability": " ".join(f"{R:g}:{s:.4f}" for R, s in rungs.availability[0]),
                "combine_skip_mass": info["combine_skip_mass"], "funded_skip_mass": info["funded_skip_mass"],
                "paid_skip_mass": info["paid_skip_mass"], "conduct_flags": "; ".join(pol.conduct_flags()),
                "abandon_leaves": json.dumps(leaves), "seconds": round(time.time() - t0, 1)})
    return {"policy": pol, "lam": float(lam), "row": row, "oracles": [{**r, "section": "oracle"} for r in orows],
            "rounds": [{"section": "rent_round", **r} for r in rounds], "rungs": rungs}


def policies_payload(pol) -> tuple[str, str]:
    """(the policies file's text, its line-ending-free sha256, D-503)."""
    payload = json.dumps({pol.id: pol.as_dict()}, indent=1).replace("\r\n", "\n")
    return payload, hashlib.sha256(payload.encode("utf-8")).hexdigest()


# ------------------------------------------------------------------------------------------------ the differences


def _cuts(node: dict, on: str, out: set) -> None:
    if not isinstance(node, dict):
        return
    if node.get("type") == "tiers" and node.get("on") == on:
        out.update(float(x["from"]) for x in node.get("tiers", []))
    for v in node.values():
        if isinstance(v, dict):
            _cuts(v, on, out)
        elif isinstance(v, list):
            for x in v:
                if isinstance(x, dict):
                    _cuts(x.get("policy", x), on, out)


def state_grid(*pols) -> list[dict[str, Any]]:
    """Every (phase, balance, cushion) at the midpoints of both tables' balance and cushion bands (the union of their
    cuts; the last band read 125 dollars in), with the cushion no larger than the balance can carry."""
    out = []
    for phase in PHASES:
        bal, cush = set(), set()
        for p in pols:
            node = p.as_dict()["root"].get(phase, {})
            _cuts(node, "balance", bal)
            _cuts(node, "cushion", cush)
        bal, cush = sorted(bal), sorted(cush)
        bmid = [(a + b) / 2 for a, b in zip(bal, bal[1:])] + ([bal[-1] + 125.0] if bal else [])
        cmid = [(a + b) / 2 for a, b in zip(cush, cush[1:])] + ([cush[-1] + 125.0] if cush else [])
        for b in bmid:
            for c in cmid:
                if c > b + 2000.0 + 1e-9:          # the cushion above the floor cannot exceed the balance less -$2,000
                    continue
                out.append({"phase": phase, "balance": float(b), "cushion": float(c), "cushion_frac": float(c) / 2000.0,
                            "days_in_state": 0, "day": 0, "win_days": 0, "line_gap": 0.0, "request_day": 0})
    return out


def table_diff(new, old) -> pd.DataFrame:
    """The states (on `state_grid`) where the two tables decide differently: risk, R, the session's trade limit or
    closure."""
    rows = []
    for s in state_grid(new, old):
        a, b = new.decide(s), old.decide(s)
        ka = (a.risk, a.rr, a.max_trades, a.abandon)
        kb = (b.risk, b.rr, b.max_trades, b.abandon)
        if ka != kb:
            rows.append({"section": "table_diff", "phase": s["phase"], "balance": s["balance"], "cushion": s["cushion"],
                         "resolved_risk": a.risk, "resolved_rr": a.rr, "resolved_max_trades": a.max_trades,
                         "resolved_abandon": bool(a.abandon), "v12_risk": b.risk, "v12_rr": b.rr,
                         "v12_max_trades": b.max_trades, "v12_abandon": bool(b.abandon)})
    return pd.DataFrame(rows)


def diff_summary(diff: pd.DataFrame, n_states: int) -> list[str]:
    """Plain lines: per phase, how many grid states differ and the commonest change."""
    out = [f"{len(diff)} of {n_states} grid states decide differently"]
    if diff.empty:
        return out
    for ph, g in diff.groupby("phase", sort=False):
        ch = (g["v12_risk"].astype(str) + "@" + g["v12_rr"].astype(str) + " -> " + g["resolved_risk"].astype(str) + "@"
              + g["resolved_rr"].astype(str))
        top = ch.value_counts().head(4)
        out.append(f"  {ph}: {len(g)} states; " + "; ".join(f"{k} ({v})" for k, v in top.items()))
    return out


# ------------------------------------------------------------------------------------------------ the screen


def screen_row(rd: Path) -> pd.Series:
    from propedge.reporting.results import read_result

    d = read_result(Path(rd) / SCREEN_FILE)
    c = d[(d["section"].astype(str) == "cell") & (d["cell"].astype(str) == CELL)]
    if len(c) != 1:
        raise SystemExit(f"REFUSED ({DECISION}): {SCREEN_FILE} holds {len(c)} {CELL} rows.")
    return c.iloc[0]


def growth_problems(df: pd.DataFrame, row: pd.Series) -> list[str]:
    out = []
    for col, shift, src in IDENT_COLS:
        g = df[(df["shift"] == shift) & np.isclose(df["enforcement_p"].astype(float), 0.0)]
        mine, want = float(g[src].iloc[0]), float(row[col])
        if not np.isclose(mine, want, rtol=0, atol=1e-9):
            out.append(f"{col}: {mine!r} against {SCREEN_FILE}'s {want!r}")
    return out


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    import rc150_dev_test as R150
    import rc_dev_test as D
    import rc_reentry_screen as RS
    import score_fv3_grid as gf

    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import write_result
    from propedge.research import resolved_coin as rc

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="the solve, the identity and every run; nothing written")
    ap.add_argument("--solve-only", action="store_true", help="the table and its differences only; nothing written")
    ap.add_argument("--paths", type=int, default=N_PATHS)
    ap.add_argument("--workers", type=int, default=1)
    a = ap.parse_args(argv)
    if not (a.check or a.solve_only) and int(a.paths) != N_PATHS:
        print(f"REFUSED ({DECISION}): the reading runs {N_PATHS} paths; a smaller run is --check (writes nothing).")
        return 2
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    t_all = time.time()
    srow = screen_row(RESULTS_DIR)
    print("P-14's inputs, the no-closure plan and the 37.5-point walk...", flush=True)
    I = S.inputs()
    L = I["L"]
    fcfg, tv = L["fcfg"], float(L["tv"])
    b = W.build(I, (STOP,))
    c = b["cells"][CELL]
    t, days = c["trades"], b["days"]
    h = D.trades_hash(t)
    bad = []
    if int(len(t)) != int(srow["candidates"]):
        bad.append(f"{len(t)} candidates against the screen's {int(srow['candidates'])}")
    if h != R150.TRADES_SHA256:
        bad.append(f"content hash {h[:16]} against the pinned {R150.TRADES_SHA256[:16]}")
    if bad:
        print(f"REFUSED ({DECISION}): the cell is not P-16's {CELL} -- " + "; ".join(bad))
        return 3
    print(f"identity HOLDS: the cell = P-16's {CELL} ({len(t)} candidates; content hash {h[:16]})", flush=True)
    fr, edge, e_by, lb_by = cell_edge(t, days, I)
    print(f"the cell's 0.05 bound at the fresh funded R {fr:g}: {edge:+.4f} (v12's table: its e = -0.050 cell)",
          flush=True)
    print("the table re-solved (v12, no closure, one rung at 150 ticks, the cell's edge)...", flush=True)
    sol = solve_table(t, edge, tv)
    new, old = sol["policy"], I["plan"]
    diff = table_diff(new, old)
    n_states = len(state_grid(new, old))
    for line in diff_summary(diff, n_states):
        print(line, flush=True)
    if a.solve_only:
        print(f"the table solved and compared; nothing written (--solve-only). {time.time() - t_all:.0f} s")
        return 0
    base = gf.sizing_rule(fcfg, tv)
    sizing = pd.concat([rc.width_sizing(base, W.policy_leaves(p), (STOP,), tv).assign(table=name)
                        for name, p in (("resolved", new), ("v12", old))], ignore_index=True)
    sizing["section"] = "sizing"                     # width_sizing's own section label replaced: one section a block
    Rv = S.Runner(I, a.workers)
    idents = [{"section": "identity", "cell": CELL, "holds": True,
               "check": f"the cell's trades as rc_width_screen.build builds them: {len(t)} candidates as the screen's "
                        f"{CELL} row; content hash {h} = rc150_dev_test.TRADES_SHA256"}]
    df_v12 = Rv.run(f"{CELL} v12", t, days, a.paths)
    if int(a.paths) == N_PATHS:
        bad = growth_problems(df_v12, srow)
        if bad:
            print(f"REFUSED ({DECISION}): {CELL} with v12's table is not the screen's -- " + "; ".join(bad))
            return 3
        print(f"identity HOLDS: {CELL} with v12's no-closure table at {N_PATHS} paths = {SCREEN_FILE}'s growth and "
              "required bankroll", flush=True)
        idents.append({"section": "identity", "cell": CELL, "holds": True,
                       "check": f"{CELL} with v12's no-closure table, seed {S.SEED}, {N_PATHS} paths, reproduces "
                                f"results/{SCREEN_FILE}'s growth at the bound and point and its required bankroll"})
    else:
        print(f"  the v12 identity needs {N_PATHS} paths; not compared at {a.paths}", flush=True)
    tw_v12 = Rv.run(f"{CELL} v12 twin", t, days, a.paths, twin=True)
    Rn = S.Runner(dict(I, plan=new), a.workers)
    df_new = Rn.run(f"{CELL} resolved", t, days, a.paths)
    tw_new = Rn.run(f"{CELL} resolved twin", t, days, a.paths, twin=True)
    if a.check:
        print(f"every identity run held; both tables and their twins ran at {a.paths} paths; trades taken a session "
              f"{RS.taken_per_session(Rv.sink, f'{CELL} v12', 'lower_bound'):.2f} (v12), "
              f"{RS.taken_per_session(Rn.sink, f'{CELL} resolved', 'lower_bound'):.2f} (re-solved) -- no growth "
              f"printed; nothing written (--check). {time.time() - t_all:.0f} s")
        return 0
    rows = []
    for name, df, tw, R in (("v12", df_v12, tw_v12, Rv), ("resolved", df_new, tw_new, Rn)):
        r = RS.cell_row(f"{CELL} {name}", c, df, tw, R.sink, days, b["rr_grid"], fcfg)
        r.update({"section": "cell", "cell": CELL, "table": name,
                  "policy_id": (new.id if name == "resolved" else old.id), "reading": READING})
        rows.append(r)
    payload, sha = policies_payload(new)
    seconds = time.time() - t_all
    res = pd.DataFrame(idents + rows + [sol["row"]] + sol["oracles"] + sol["rounds"] + diff.to_dict("records")
                       + sizing.to_dict("records"))
    res["reading"] = res["reading"].fillna(READING) if "reading" in res else READING
    VariantCounter(path=rd / "variants.jsonl").record(
        prereg_id=FAMILY_ID, seed=S.SEED, exploratory=True,
        params={"study": "D-559's re-solved table", "cell": CELL, "stop_ticks": STOP, "edge": edge,
                "policy_id": new.id, "paths": N_PATHS},
        label=f"D-559's re-solved table: {CELL} with the table solved on its own outcomes")
    write_result(res, RESULT, script=SCRIPT, seed=S.SEED, exploratory=True, results_dir=results_dir, variant_count=1,
                 parameters={"decision": DECISION, "cell": CELL, "stop_ticks": STOP, "table_version": TABLE_VERSION,
                             "edge": edge, "edge_rule": f"the cell's 0.05 bound at the fresh funded R {fr:g} "
                                                        "(atlas_a3.bounds, the era rule)",
                             "lambda_star": sol["lam"], "policy_id": new.id, "v12_policy_id": old.id,
                             "policies_json": f"results/{POLICIES}", "policies_sha256": sha,
                             "rung": {"risk_per_contract": STOP * tv, "share": 1.0,
                                      "availability": [list(x) for x in sol["rungs"].availability[0]]},
                             "changes": "v12's config with funded_rules.abandon false, one rung at the cell's stop, "
                                        "solved at the cell's edge; everything else v12's",
                             "seed": S.SEED, "coin_seed": rc.COIN_SEED, "paths": N_PATHS, "cell_trades_sha256": h,
                             "workers": int(a.workers), "seconds": round(seconds, 1)},
                 notes={"status": READING, "selection": "none; a re-solved table that grows more at the bound than "
                        "v12's would become a new candidate with its own registered test (D-559)"},
                 description="EXPLORATORY (D-559): the 37.5-point news-safe coin (all-day) with the state table "
                             "re-solved on its own rung and bound, beside v12's no-closure table; both with their "
                             "zero-edge twins; the table's differences state by state and each table's realised sizing.")
    pj = (Path(results_dir) if results_dir is not None else rd) / POLICIES
    pj.write_text(payload, encoding="utf-8", newline="\n")
    print(pd.DataFrame(rows)[["table", "growth_on_required", "growth_on_required_point", "required_p90",
                              "growth_zero_edge_twin", "trades_taken_per_session"]].to_string(index=False))
    print(f"written: {RESULT}.csv and {POLICIES} ({seconds:.0f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
