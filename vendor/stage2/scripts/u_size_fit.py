"""EXPLORATORY (D-666; program U's U4): the account-size fit read -- for each Topstep account size ($50K, $100K,
$150K) and each base design (P-14, A3-BRK30-CB20 on its 12.5- and 25-point rungs; P-16, `rc_s150_all` on its
37.5-point stop), the base's state-table solver on that size's verified rows, at the base's own bound edge and at zero
edge, before any campaign. No campaign is run, no variant counted, nothing selected; the reading is D-666's row's.

    python scripts/u_size_fit.py --check                     # the static identities, the $50K oracles, then every
                                                             #   size x base x edge solved at a short horizon; identity
                                                             #   lines and cost only; written to a temporary folder,
                                                             #   since removed
    python scripts/u_size_fit.py --check --identity          # the same plus the two table identities (full horizon)
    python scripts/u_size_fit.py                             # the read (one worker; from a clean checkout, D-474)

**What is solved (D-666 (1); `propedge/research/u_size_fit.py`):** `config/state_policy_v12.yaml` with the no-closure
leaf (`a3_compliance.noclose_config`, D-501/D-502 -- the table P-14 and P-16 trade), solved as `state_policy_dp`
solves it (the oracles first, the rent's fixed point lambda* from the config's start on the exact tables, the
tie-broken table at lambda*), with, per size: the size's verified rules (`rules_for_size`), its Combine limit and
funded ladder (`sizing_for_size` -> `rungs_for_size`), each menu's risks extended to its loss limit on the $50 grid and
the funded balance cap raised to twice its Standard cap where that is above v12's $6,000 (`size_config`); per base:
its own rungs (P-14: the stops, shares and per-R availability its registered gate recorded, section `rung`; P-16: one
rung at 150 ticks, availability from its gate's `resolution` rows over its candidates) and each R's edge -- the bound
arm's `lb_by_rr` its registered gate used (`lb_gate` of its `edge` rows; set `bound`) and zero (set `zero`), read
through `FundedByR` / `CombineByR` (each outcome at its R's own edge).

**Identities first, each refusing (D-666 (4)); nothing is written if one fails:**

* the read files' manifests verify (sha256); the no-closure table's and D-559's policies files hash as their
  manifests record;
* at $50K the rules built here are `rules_for_method('aeropay')`, the sizing's allowances are v12's rungs', the size's
  config and menus are v12's no-closure ones (nothing extended, the cap $6,000); at every size the Rules carry the
  ledger's rows;
* P-14's rungs add up to its gate's trades and, R by R, to its `resolution` rows' offered counts; P-16's rung is
  D-559's (`results/rc150_table_screen.csv`'s manifest: its risk a micro and availability);
* every R either menu or the exit grid reads has an edge in each base's edge rows;
* the $50K oracles computed here equal `state_policy_dp.oracles`' and hold stage one's ceilings (0.327131, 16/49,
  $2,000) and the static bound 2/5;
* **the table on file:** v12's no-closure config re-solved at one edge, FV3-C's e = -0.050 at every R, through the
  per-R classes, reproduces `results/state_policy_v12_noclose_policies.json`'s `state_dp_e-0.050_lamstar_noclose` --
  the whole exported tree but its description (so the same decision in every state; checked again state by state on
  `rc150_table_screen.state_grid`) and its rent to 1e-9 -- the table P-14 and P-16 trade, solved at one edge for
  both; and **D-559's one-rung table:** P-16's rung at $50K at D-559's single edge reproduces
  `results/rc150_table_screen_policies.json` and its rent the same way. These are the identity set; the readings are
  the second set, at each base's own per-R edges.
* at every size and base the zero-edge, fee-free oracles hold the size's bounds, and every solved table at an edge set
  with no positive R holds them too (P(pass) and gross payouts per funded account): a value outside is an engine
  error.

**Readings** (D-666 (2)): per size, base and edge set -- an attempt's P(pass); its expected net payouts (the split
and the method's fee taken) and gross payouts; its expected fees (the subscription as the engine bills it, at purchase
and every 21 trading days held, until the pass or the failure -- the reset is the next attempt's purchase, priced the
same at every size -- and the activation at a pass); the payouts per fee dollar; the attempt's value (payouts less
fees); the same three on the table's own accrual (`*_accrued`, beside); the sessions to a first payout under the
table's model (the Combine's days to its pass plus the fresh funded account's days to its first payout, among the
attempts that reach one; no activation latency, one trade a session); the funded account's own readings beside.
**The rule** (D-666 (3)): section `rule`, a row per base and larger size (the ratio to the $50K solve's payouts per
fee dollar at the bound edge; `clears` when above 1.10) and the verdict row, its line computed here.

**The file** `results/u_size_fit.csv` (EXPLORATORY; no variant recorded; no seed -- an exact chain), long format:
`section, size, base, edge, subject, measure, value, n, unit, note, label`. Sections: `identity` (each check, value 1
when it held), `rules` (each size's rows used), `sizing` (allowances), `menu`, `rungs` (per base: stop, share, R's
availability), `edge` (per base, R and edge set), `oracle` (value rows and their `_bound` rows, `note` the relation
and held), `reading`, `reading_check`, `rent` (lambda* and its rounds), `rule` (the per-base rows: measure
`payouts_per_fee_dollar`, `ratio_to_50k`, `clears`; and `verdict`, value 1 when a size family follows, `note` the
line), `rule_beside` (the same comparison on the accrual fees, beside, never the verdict). `label` on every row of a
larger size carries `lock_assumed_1to1` and D-666 (5)'s assumptions. The manifest records each solve's seconds and the
process's peak memory, the read files' sha256 and every interpretation (`interpretations`).
"""
from __future__ import annotations

import argparse
import gc
import json
import os
import shutil
import sys
import tempfile
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

from propedge.research import u_size_fit as U  # noqa: E402

SCRIPT = "scripts/u_size_fit.py"
RESULT = "u_size_fit"
TABLE_VERSION = 12
V12_DECLARATION = "D-333"
IDENT_EDGE = -0.05                                   # FV3-C's cell, the table on file's single edge
NOCLOSE_CSV = "state_policy_v12_noclose.csv"
NOCLOSE_JSON = "state_policy_v12_noclose_policies.json"
NOCLOSE_ID = "state_dp_e-0.050_lamstar_noclose"
D559_CSV = "rc150_table_screen.csv"
D559_JSON = "rc150_table_screen_policies.json"
P14_GATE = "a3_brk30_cb20_gate.csv"
P16_GATE = "rc_s150_all_gate.csv"
P16_SCREEN = "rc_width_screen.csv"
P16_CELL = "rc_s150_all"
P16_STOP = 150
CHECK_HORIZON = 42
#: D-666 (1): a solve's estimated memory above this is not run (the row allows no coarser grid): stop and report
MEMORY_LIMIT_GB = 6.0
INTERPRETATIONS = (
    "The table on file (state_dp_e-0.050_lamstar_noclose) was solved at one edge for both bases (e = -0.050 at "
    "every R, FV3-C's cell, on FV3-C's three rungs); it is reproduced as the identity set, and the readings are a "
    "second set at each base's own rungs and per-R edges.",
    "Each R's bound edge is the lb_gate column of the base's registered gate's edge rows (the lb_by_rr its bound arm "
    "used, atlas_a3.bounds' era rule); read from the result file, its manifest verified, not recomputed from trades.",
    "A Combine trade closed early (at the need or at the consistency allowance) is read at the exit-grid R's own "
    "edge; a trade held to its target, and every funded trade, at the action's R's edge.",
    "Each menu's risks are extended above its top by its top spacing, $500, to the size's loss limit (funded: "
    "$2,500 and $3,000 at $100K, to $4,500 at $150K; the Combine's list already reaches $3,000, so $3,500 to $4,500 at "
    "$150K only); nothing at $50K.",
    "The funded balance cap is the larger of v12's $6,000 and twice the size's Standard cap: $6,000 at $50K and $100K, "
    "$10,000 at $150K.",
    "The funded profit-risk cap ($500), the tie-break tolerances ($5), the winning-day minimum ($150), the payout "
    "minimum and share, the split and the consistency fraction stay single-valued, as the base's (D-666 (5)).",
    "Fees per attempt: the subscription as the engine bills it (at purchase and every 21 trading days held) plus the "
    "activation at a pass; the reset is the next attempt's purchase (reset and subscription priced equal at every "
    "size); the table's own accrual is reported beside (_accrued), and the rule's comparison on it is a beside row.",
    "Payouts per attempt are net of the split and the method's fee (what a user receives): P(pass) x the fresh funded "
    "account's expected net payouts over the horizon, as the table's cycle accounting reads them.",
    "Sessions to a first payout: the Combine's mean days to its pass plus the fresh funded account's mean days to its "
    "first payout, each among those that reach it (the table's model: no activation latency, one trade a session).",
    "The zero-edge bound checks apply to the fee-free oracle tables at every size and base, and to every solved "
    "table whose edges are all at or below zero (both bases' bound edges are), since a fair or unfavourable game "
    "cannot beat them.",
)


# ------------------------------------------------------------------------------------------------ inputs


def _verified(rd: Path, name: str) -> pd.DataFrame:
    from propedge.reporting.results import verify_result

    ok, msg = verify_result(rd / name)
    if not ok:
        raise SystemExit(f"REFUSED ({U.DECISION}): {name}: {msg}")
    return pd.read_csv(rd / name, float_precision="round_trip", low_memory=False)


def _manifest(rd: Path, name: str) -> dict:
    return json.loads((rd / f"{name}.manifest.json").read_text(encoding="utf-8"))


def _policies(rd: Path, name: str, want_sha: str) -> dict:
    import hashlib

    text = (rd / name).read_text(encoding="utf-8").replace("\r\n", "\n")
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if sha != want_sha:
        raise SystemExit(f"REFUSED ({U.DECISION}): {name} hashes {sha[:16]}, its manifest records {want_sha[:16]}.")
    return json.loads(text)


def load_inputs(rd: Path) -> dict[str, Any]:
    """Every file the read rests on, each verified; the base table's config; the bases' rungs and edges."""
    import a3_compliance as a3
    import atlas_a3 as A
    import state_policy_dp as dp

    cfg = dp.config(dp.config_for(TABLE_VERSION))
    if str(cfg.get("decision")) != V12_DECLARATION or dp.rent_mode(cfg) != "fixed_point":
        raise SystemExit(f"REFUSED ({U.DECISION}): config/state_policy_v12.yaml is not D-333's fixed-point table.")
    nc = a3.noclose_config(cfg)
    import yaml

    acfg = yaml.safe_load((ROOT / "config" / "atlas_a3.yaml").read_text(encoding="utf-8"))
    fcfg = A.fv3_config(acfg)
    fresh_fr = float(fcfg["state_policy"]["fresh"]["funded_rr"])
    headroom = float(fcfg["gate"]["campaign"]["headroom"])
    files = {}
    for name in (NOCLOSE_CSV, D559_CSV, P14_GATE, P16_GATE, P16_SCREEN):
        files[name] = _verified(rd, name)
    nm, dm = _manifest(rd, NOCLOSE_CSV), _manifest(rd, D559_CSV)
    noclose_pols = _policies(rd, NOCLOSE_JSON, nm["parameters"]["policies_sha256"])
    d559_pols = _policies(rd, D559_JSON, dm["parameters"]["policies_sha256"])
    tv = float(cfg["rungs"]["tick_value"])
    grid = tuple(float(x) for x in cfg["rungs"]["exit_grid"])
    bases: dict[str, dict] = {}
    for base, name in (("p14", P14_GATE), ("p16", P16_GATE)):
        d = files[name]
        e = d[d["section"].astype(str) == "edge"]
        edges = {float(r.rr): float(r.lb_gate) for r in e.itertuples()}
        res = d[d["section"].astype(str) == "resolution"]
        offered = {float(r.rr): float(r.offered) for r in res.itertuples()}
        bases[base] = {"edges": edges, "offered": offered, "gate_file": name}
    d14 = files[P14_GATE]
    n14 = int(d14[d14["section"].astype(str) == "verdict"]["trades"].iloc[0])
    rung_rows = d14[d14["section"].astype(str) == "rung"][["hour", "stop_ticks", "cell_trades", "offered"]]
    bases["p14"]["rungs"] = U.p14_rungs(rung_rows.to_dict("records"), n14, grid, tv)
    bases["p14"]["n_trades"] = n14
    sc = files[P16_SCREEN]
    row = sc[(sc["section"].astype(str) == "cell") & (sc["cell"].astype(str) == P16_CELL)]
    if len(row) != 1:
        raise SystemExit(f"REFUSED ({U.DECISION}): {P16_SCREEN} holds {len(row)} {P16_CELL} rows.")
    n16 = int(row["candidates"].iloc[0])
    bases["p16"]["rungs"] = U.one_rung(P16_STOP, bases["p16"]["offered"], n16, grid, tv)
    bases["p16"]["n_trades"] = n16
    stored_rent = files[NOCLOSE_CSV]
    srow = stored_rent[(stored_rent["section"] == "dp") & (stored_rent["policy_id"].astype(str) == NOCLOSE_ID)]
    if len(srow) != 1:
        raise SystemExit(f"REFUSED ({U.DECISION}): {NOCLOSE_CSV} holds {len(srow)} dp rows for {NOCLOSE_ID}.")
    return {"cfg": cfg, "noclose": nc, "fresh_fr": fresh_fr, "headroom": headroom, "tv": tv, "grid": grid,
            "bases": bases, "noclose_pol": noclose_pols[NOCLOSE_ID], "noclose_rent": float(srow["slot_rent"].iloc[0]),
            "d559": dm["parameters"], "d559_pols": d559_pols,
            "sha": {n: _manifest(rd, n)["sha256"] for n in files}}


# ------------------------------------------------------------------------------------------------ rows


class Rows:
    def __init__(self):
        self.rows: list[dict[str, Any]] = []

    def add(self, section: str, measure: str, value, *, size: str = "", base: str = "", edge: str = "",
            subject: str = "", n=None, unit: str = "", note: str = "") -> None:
        lab = U.labels_for(size) if size else "; ".join(U.ALL_LABELS)
        self.rows.append({"section": section, "size": size, "base": base, "edge": edge, "subject": subject,
                          "measure": measure, "value": float(value) if value is not None else float("nan"),
                          "n": n, "unit": unit, "note": note, "label": lab})

    def ident(self, check: str, note: str) -> None:
        self.add("identity", "holds", 1.0, subject=check, note=note)
        print(f"identity HOLDS: {check} -- {note}", flush=True)


def refuse(msg: str) -> None:
    raise SystemExit(f"REFUSED ({U.DECISION}): {msg}")


# ------------------------------------------------------------------------------------------------ the static checks


def static_identities(I: dict, out: Rows) -> dict[str, dict]:
    """The size objects, each checked; returns {size: {rules, sizing, cfg}}."""
    import dataclasses

    import state_policy_dp as dp

    from propedge.campaign.payout_method import rules_for_method
    from propedge.contract.rules import RulesLedger

    nc = I["noclose"]
    led = RulesLedger.load()
    sizes: dict[str, dict] = {}
    for size in U.SIZES:
        rules = U.rules_for_size(size)
        rows = U.size_rows(size, led)
        bad = [f for f, _ in U.SIZE_RULE_KEYS if float(getattr(rules, f)) != float(rows[f])]
        if bad:
            refuse(f"the {size} rules do not carry the ledger's rows: {bad}")
        if rules.xfa_mll_start != -rules.mll or rules.xfa_lock_at != 0.0:
            refuse(f"the {size} funded floor is not the solver's 1:1 trail (start at minus the loss limit, lock at 0)")
        sizing = U.sizing_for_size(size, I["headroom"], led)
        cfg_s = U.size_config(nc, rules)
        sizes[size] = {"rules": rules, "sizing": sizing, "cfg": cfg_s, "rows": rows}
        for f, key in U.SIZE_RULE_KEYS + U.SIZE_OTHER_KEYS:
            v = rows[f]
            out.add("rules", f, float(v) if not isinstance(v, str) else float("nan"), size=size, subject=rows[f"{f}__key"],
                    unit="dollars" if f not in ("position_limit_minis", "scaling_plan") else "",
                    note=str(v) if isinstance(v, str) else "")
        out.add("sizing", "combine_allowance_micros", sizing.allowance_micros("combine", 0.0), size=size, unit="micros")
        for th, m in zip(sizing.ladder.thresholds, sizing.ladder.minis):
            out.add("sizing", "funded_allowance_micros", int(m) * sizing.ladder.micros_per_mini, size=size,
                    subject=f"balance_from_{th:g}", unit="micros")
        out.add("menu", "funded_risks_max", max(cfg_s["menu"]["risks"]), size=size, n=len(cfg_s["menu"]["risks"]),
                unit="dollars", note=",".join(f"{x:g}" for x in cfg_s["menu"]["risks"]))
        out.add("menu", "combine_risks_max", max(cfg_s["combine_menu"]["risks"]), size=size,
                n=len(cfg_s["combine_menu"]["risks"]), unit="dollars",
                note=",".join(f"{x:g}" for x in cfg_s["combine_menu"]["risks"]))
        out.add("menu", "funded_balance_cap", cfg_s["funded"]["balance_cap"], size=size, unit="dollars")
    r50 = sizes["50k"]
    if r50["rules"] != rules_for_method("aeropay"):
        refuse("the $50K rules built here are not rules_for_method('aeropay')")
    out.ident("rules_50k", "the $50K Rules built here equal rules_for_method('aeropay') field for field")
    v12_menu = dp.menu_of(nc)
    if U.rungs_for_size(v12_menu.rungs, r50["sizing"]) != v12_menu.rungs:
        refuse("the $50K sizing's allowances are not v12's rungs'")
    out.ident("sizing_50k", "the $50K sizing's Combine limit (50 micros) and funded ladder (0: 20, 1,500: 30, 2,000: "
                            "50 micros) put on v12's rungs give v12's rungs exactly")
    if r50["cfg"] != nc:
        refuse("the $50K config built here is not v12's no-closure config (a menu extended or the cap moved)")
    if U.size_menu(r50["cfg"], v12_menu, v12_menu.rungs) != v12_menu:
        refuse("the $50K funded menu built here is not v12's no-closure menu")
    out.ident("menus_50k", "the $50K config and funded menu built here are v12's no-closure ones (nothing extended, "
                           "the balance cap $6,000)")
    for size in U.SIZES[1:]:
        out.ident(f"rules_{size}", f"the {size} Rules carry the ledger's verified {size} rows "
                                   f"({', '.join(sizes[size]['rows'][f'{f}__key'] for f, _ in U.SIZE_RULE_KEYS)})")
    # the bases' rungs and edges
    b14, b16 = I["bases"]["p14"], I["bases"]["p16"]
    r14 = b14["rungs"]
    for R in I["grid"]:
        tot = sum(sh * b14["n_trades"] * r14.avail(k, R) for k, sh in enumerate(r14.shares))
        want = b14["offered"].get(float(R), 0.0)
        if abs(tot - want) > 1e-6:
            refuse(f"P-14's rungs offer {tot:g} trades at R = {R:g}, its resolution rows {want:g}")
    stops = ", ".join(f"{x / I['tv']:g}" for x in r14.risk_per_contract)
    out.ident("p14_rungs", f"P-14's two rungs (stops of {stops} ticks) add up to its gate's {b14['n_trades']} trades and, R by R, to its "
                           "resolution rows' offered counts")
    d559 = I["d559"]["rung"]
    r16 = b16["rungs"]
    if (abs(float(d559["risk_per_contract"]) - r16.risk_per_contract[0]) > 1e-12
            or [tuple(map(float, x)) for x in d559["availability"]] != list(r16.availability[0])):
        refuse("P-16's rung is not D-559's (risk a micro or availability)")
    out.ident("p16_rung", "P-16's rung (150 ticks, $75 a micro, availability its offered counts over its "
                          f"{b16['n_trades']} candidates) equals D-559's recorded rung")
    for base in U.BASES:
        rungs = I["bases"][base]["rungs"]
        for size in U.SIZES:
            m = U.size_menu(sizes[size]["cfg"], v12_menu, U.rungs_for_size(rungs, sizes[size]["sizing"]))
            need = U.needed_rs(m, dp.combine_menu_of(sizes[size]["cfg"], m))
            miss = sorted(R for R in need if not any(abs(R - k) < 1e-9 for k in I["bases"][base]["edges"]))
            if miss:
                refuse(f"{base} has no edge at R = {miss}")
    out.ident("edges", "every R the menus and the exit grid read has an edge in each base's registered edge rows")
    for base in U.BASES:
        b = I["bases"][base]
        for k, (rpc, sh) in enumerate(zip(b["rungs"].risk_per_contract, b["rungs"].shares)):
            out.add("rungs", "share", sh, base=base, subject=f"risk_per_micro_{rpc:g}", n=b["n_trades"], unit="share")
            for R, s in b["rungs"].availability[k]:
                out.add("rungs", "availability", s, base=base, subject=f"risk_per_micro_{rpc:g}_R_{R:g}", unit="share")
        for R in sorted(b["edges"]):
            out.add("edge", "lb_by_rr", b["edges"][R], base=base, edge="bound", subject=f"R_{R:g}", unit="edge",
                    note=f"results/{b['gate_file']} edge rows, lb_gate")
    return sizes


# ------------------------------------------------------------------------------------------------ solves


def solve(cfg: dict, rules, menu, edges: dict[float, float], scalar_edge: float) -> dict[str, Any]:
    """lambda* and the tie-broken table at it (`state_policy_dp.solve_rent` through the per-R classes); the
    readings from its forward summaries; seconds and memory."""
    import state_policy_dp as dp
    import u_xfa_day_budget as UX

    t0 = time.time()
    with U.by_r_solver(edges):
        lam, objs, rounds = dp.solve_rent(cfg, rules, float(scalar_edge), menu, float(cfg["rent_fixed_point"]["start"]))
    f, fsol, ff, c, csol, cf = objs
    first = U.first_payout_by_day(f, fsol)
    if not abs(float(first.sum()) - float(ff["p_paid"])) <= 1e-12 * max(1.0, float(ff["p_paid"])):
        refuse(f"the first-payout timing sums to {first.sum()!r}, the forward's p_paid {ff['p_paid']!r}")
    rd = U.attempt_readings(rules, ff, cf, first)
    peak, now = UX.memory_mb()
    return {"lam": float(lam), "rounds": rounds, "objs": objs, "readings": rd, "seconds": time.time() - t0,
            "peak_mb": peak, "nS_funded": int(f.nS), "nS_combine": int(c.nS), "nA_funded": len(f.actions),
            "nA_combine": len(c.actions), "nR": int(f.nR)}


def estimate_gb(cfg: dict, rules, menu, T: int) -> float:
    """A solve's memory, from its funded table's size (calibrated on the $50K solve: transitions, their gathers and
    complements, the day policies, the visitation)."""
    cap, mll, step = float(cfg["funded"]["balance_cap"]), float(rules.mll), float(menu.step)
    nW = int(rules.std_winning_days) + 1
    nS = (int(round((cap + mll) / step)) + 1) * (int(round(mll / step)) + 1) * nW * 2 \
        + int(round(cap / step)) * (int(round(cap / step)) + 1) * nW * 2
    nA = len(menu.actions())
    nR = len(menu.rungs) if menu.rungs is not None else 1
    return (nS * nA * nR * 32 + 2 * T * nS + nS * nA * 12) / 1e9


def identity_solves(I: dict, sizes: dict, out: Rows) -> None:
    """The two table identities (full horizon), each refusing."""
    import rc150_table_screen as T
    import state_policy_dp as dp

    from propedge.campaign import state_policy as sp
    from propedge.campaign.risk_policy import RiskPolicy

    nc, r50 = I["noclose"], sizes["50k"]["rules"]
    menu = dp.menu_of(nc)
    print("the table on file re-solved through the per-R classes at e = -0.050 at every R ...", flush=True)
    edges = {R: IDENT_EDGE for R in U.needed_rs(menu, dp.combine_menu_of(nc, menu))}
    s = solve(nc, r50, menu, edges, IDENT_EDGE)
    f, fsol, ff, c, csol, cf = s["objs"]
    bands = nc["export"]
    pol, _ = sp.export_policy(NOCLOSE_ID, c, cf["visitation"], f, ff["visitation"], float(bands["balance_band"]),
                              float(bands["cushion_band"]), version=TABLE_VERSION, c_pol0=csol.policy[0],
                              f_pol0=fsol.policy[0], description=dp.export_description(nc, IDENT_EDGE, s["lam"],
                                                                                       TABLE_VERSION))
    bad = U.policy_problems(pol.as_dict(), I["noclose_pol"], s["lam"], I["noclose_rent"])
    if not str(I["noclose_pol"]["description"]).startswith(dp.export_description(nc, IDENT_EDGE, s["lam"],
                                                                                   TABLE_VERSION)):
        bad.append("the description's rent is not the file's")
    diff = T.table_diff(pol, RiskPolicy.from_dict(I["noclose_pol"]))
    if len(diff):
        bad.append(f"{len(diff)} grid states decide differently")
    if bad:
        refuse("the solver as built here does not reproduce the table on file -- " + "; ".join(bad))
    out.ident("table_on_file", f"v12's no-closure config at $50K, e = -0.050 at every R through FundedByR/CombineByR, "
                               f"reproduces results/{NOCLOSE_JSON}'s {NOCLOSE_ID} (the whole tree but its description; "
                               f"0 of {len(T.state_grid(pol, pol))} grid states differ) and its rent to 1e-9 "
                               f"({s['seconds']:.0f} s)")
    out.add("rent", "lambda_star", s["lam"], size="50k", base="identity_v12", edge="uniform_-0.050", unit="dollars/slot-day")
    del s, f, fsol, ff, c, csol, cf
    gc.collect()
    d = I["d559"]
    e559 = float(d["edge"])
    r16 = U.rungs_for_size(I["bases"]["p16"]["rungs"], sizes["50k"]["sizing"])
    m16 = U.size_menu(nc, menu, r16)
    print(f"D-559's one-rung table re-solved at its edge {e559:+.6f} at every R ...", flush=True)
    edges = {R: e559 for R in U.needed_rs(m16, dp.combine_menu_of(nc, m16))}
    s = solve(nc, r50, m16, edges, e559)
    f, fsol, ff, c, csol, cf = s["objs"]
    pid = f"rc150_table_e{e559:+.4f}_lamstar_noclose"
    if pid != d["policy_id"]:
        refuse(f"D-559's policy id {d['policy_id']} is not {pid}")
    pol, _ = sp.export_policy(pid, c, cf["visitation"], f, ff["visitation"], float(bands["balance_band"]),
                              float(bands["cushion_band"]), version=TABLE_VERSION, c_pol0=csol.policy[0],
                              f_pol0=fsol.policy[0], description="")
    bad = U.policy_problems(pol.as_dict(), I["d559_pols"][pid], s["lam"], float(d["lambda_star"]))
    if bad:
        refuse("P-16's rung does not reproduce D-559's table -- " + "; ".join(bad))
    out.ident("d559_table", f"P-16's rung at $50K, D-559's edge at every R, reproduces results/{D559_JSON}'s {pid} "
                            f"(the whole tree but its description) and its rent to 1e-9 ({s['seconds']:.0f} s)")
    out.add("rent", "lambda_star", s["lam"], size="50k", base="identity_d559", edge=f"uniform_{e559:+.6f}",
            unit="dollars/slot-day")
    del s, f, fsol, ff, c, csol, cf
    gc.collect()


def oracles_50k_identity(I: dict, sizes: dict, out: Rows) -> None:
    """The $50K oracles computed here equal state_policy_dp.oracles' (v12's no-closure menu) and hold."""
    import state_policy_dp as dp

    nc, r50 = I["noclose"], sizes["50k"]["rules"]
    menu = dp.menu_of(nc)
    rows, ok = dp.oracles(nc, r50, menu)
    if not ok:
        refuse("state_policy_dp.oracles fails at $50K")
    mine = U.oracle_values(nc, r50, menu)
    want = {"p_pass_1to1_1500": rows[0]["value"], "max_p_pass": rows[1]["value"], "max_gross_payouts": rows[2]["value"]}
    if mine != want:
        refuse(f"the oracles computed here {mine} are not state_policy_dp.oracles' {want}")
    chk = U.oracle_checks("50k", r50, mine)
    if not all(c["held"] for c in chk):
        refuse("a $50K oracle fails: " + "; ".join(f"{c['check']} {c['value']:.6f}" for c in chk if not c["held"]))
    out.ident("oracles_50k", "the $50K zero-edge fee-free oracles on v12's menu equal state_policy_dp.oracles' and "
                             "hold 16/49 (1:1 at $1,500), the supremum 0.327131, 2/5 and $2,000")


# ------------------------------------------------------------------------------------------------ main


def run(I: dict, out: Rows, *, horizon: int | None, only: set[tuple[str, str]] | None, cost: dict,
        guard: bool = True) -> dict:
    import state_policy_dp as dp

    sizes = static_identities(I, out)
    oracles_50k_identity(I, sizes, out)
    v12_menu = dp.menu_of(I["noclose"])
    readings: dict[tuple[str, str, str], dict] = {}
    for base in U.BASES:
        b = I["bases"][base]
        for size in U.SIZES:
            if only is not None and (size, base) not in only:
                continue
            S = sizes[size]
            cfg_s = dict(S["cfg"])
            if horizon is not None:
                cfg_s = {**cfg_s, "horizon_days": int(horizon)}
            rules = S["rules"]
            rungs = U.rungs_for_size(b["rungs"], S["sizing"])
            menu = U.size_menu(cfg_s, v12_menu, rungs)
            est = estimate_gb(cfg_s, rules, menu, int(cfg_s["horizon_days"]))
            print(f"{base} {size}: estimated {est:.2f} GB a solve", flush=True)
            if guard and est > MEMORY_LIMIT_GB:
                refuse(f"{base} at {size} would need about {est:.1f} GB, above {MEMORY_LIMIT_GB:g} GB, and D-666 "
                       "allows no coarser grid")
            t0 = time.time()
            vals = U.oracle_values(cfg_s, rules, menu)
            chk = U.oracle_checks(size, rules, vals)
            for c in chk:
                out.add("oracle", c["check"], c["value"], size=size, base=base, edge="zero_no_fees",
                        unit="probability" if "p_pass" in c["check"] else "dollars",
                        note=f"{c['relation']} {c['bound']!r}; {'held' if c['held'] else 'FAILED'}")
                out.add("oracle", c["check"] + "_bound", c["bound"], size=size, base=base, edge="zero_no_fees",
                        unit="probability" if "p_pass" in c["check"] else "dollars", note=c["relation"])
            if not all(c["held"] for c in chk):
                refuse(f"ENGINE ERROR at {base} {size}: " + "; ".join(
                    f"{c['check']} {c['value']:.6f} against {c['bound']:.6f}" for c in chk if not c["held"]))
            print(f"  oracles held at {size} ({time.time() - t0:.0f} s): " + ", ".join(
                f"{c['check']} {c['value']:.6f} <= {c['bound']:.6f}" for c in chk if c["relation"] == "at_most"),
                flush=True)
            for es in U.EDGE_SETS:
                edges = b["edges"] if es == "bound" else {R: 0.0 for R in b["edges"]}
                scalar = float(edges[min(edges, key=lambda k: abs(k - I["fresh_fr"]))])
                s = solve(cfg_s, rules, menu, edges, scalar)
                rd = s["readings"]
                cost[f"{base}_{size}_{es}"] = {"seconds": round(s["seconds"], 1), "peak_mb": round(s["peak_mb"], 1),
                                               "rent_rounds": len(s["rounds"]), "nS_funded": s["nS_funded"],
                                               "nS_combine": s["nS_combine"], "nA_funded": s["nA_funded"],
                                               "nA_combine": s["nA_combine"], "rungs": s["nR"],
                                               "estimated_gb": round(est, 2)}
                print(f"  {es}: lambda* {s['lam']:.4f}, {len(s['rounds'])} rounds, {s['seconds']:.0f} s, peak "
                      f"{s['peak_mb']:.0f} MB", flush=True)
                for k, v in rd.items():
                    out.add("reading", k, v, size=size, base=base, edge=es, unit=U.UNITS.get(k, ""))
                out.add("rent", "lambda_star", s["lam"], size=size, base=base, edge=es, n=len(s["rounds"]),
                        unit="dollars/slot-day")
                for c in U.reading_checks(size, rules, rd, edges):
                    out.add("reading_check", c["check"], c["value"], size=size, base=base, edge=es,
                            note=f"at_most {c['bound']!r}; {'held' if c['held'] else 'FAILED'}")
                    if not c["held"]:
                        refuse(f"ENGINE ERROR at {base} {size} {es}: {c['check']} {c['value']:.6f} above "
                               f"{c['bound']:.6f}")
                readings[(base, size, es)] = rd
                del s
                gc.collect()
    return readings


def rule_section(readings: dict, out: Rows) -> str:
    rows, line = U.rule_rows({(b, s): readings[(b, s, "bound")]["payouts_per_fee_dollar"]
                              for b in U.BASES for s in U.SIZES})
    for r in rows:
        for m in ("value", "ratio_to_50k", "clears"):
            out.add("rule", r["measure"] if m == "value" else m, float(r[m]), size=r["size"], base=r["base"],
                    edge="bound", note=f"the $50K solve's {r['ref_50k']!r}")
    follows = "follows" in line.split(" -- ")[0]
    out.add("rule", "verdict", 1.0 if follows else 0.0, edge="bound", subject="D-666 (3)", note=line)
    brows, bline = U.rule_rows({(b, s): readings[(b, s, "bound")]["payouts_per_fee_dollar_accrued"]
                                for b in U.BASES for s in U.SIZES}, measure="payouts_per_fee_dollar_accrued")
    for r in brows:
        out.add("rule_beside", "ratio_to_50k", r["ratio_to_50k"], size=r["size"], base=r["base"], edge="bound",
                note="the same comparison on the table's own fee accrual; beside, never the verdict")
    out.add("rule_beside", "verdict_beside", 1.0 if "follows" in bline.split(" -- ")[0] else 0.0, edge="bound",
            note="beside, never the verdict: " + bline)
    return line


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.reporting.results import write_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="identities and every solve at a short horizon; written to a "
                    "temporary folder, since removed")
    ap.add_argument("--identity", action="store_true", help="with --check: the two table identities too (full horizon)")
    ap.add_argument("--horizon", type=int, default=None, help=f"--check only: the horizon (default {CHECK_HORIZON})")
    ap.add_argument("--only", default=None, help="--check only: size:base pairs, comma-separated (e.g. 150k:p14)")
    a = ap.parse_args(argv)
    if not a.check and (a.identity or a.horizon is not None or a.only):
        print(f"REFUSED ({U.DECISION}): --identity, --horizon and --only are --check options; the read runs whole.")
        return 2
    t_all = time.time()
    I = load_inputs(RESULTS_DIR)
    out = Rows()
    cost: dict[str, Any] = {}
    only = None
    if a.only:
        only = {tuple(x.strip().split(":")) for x in a.only.split(",") if x.strip()}
    if not a.check or a.identity:
        sizes = static_identities(I, Rows())
        identity_solves(I, sizes, out)
    readings = run(I, out, horizon=(a.horizon or CHECK_HORIZON) if a.check else None, only=only, cost=cost)
    line = None
    if not a.check or only is None:
        line = rule_section(readings, out)
    df = pd.DataFrame(out.rows)
    params = {"decision": U.DECISION, "sizes": list(U.SIZES), "bases": U.BASE_NAMES, "edge_sets": list(U.EDGE_SETS),
              "config": "config/state_policy_v12.yaml with funded_rules.abandon false (a3_compliance.noclose_config)",
              "horizon_days": int(I["noclose"]["horizon_days"]) if not a.check else int(a.horizon or CHECK_HORIZON),
              "rule_margin": U.RULE_MARGIN, "identity_edge": IDENT_EDGE, "d559_edge": float(I["d559"]["edge"]),
              "fresh_funded_rr": I["fresh_fr"], "headroom": I["headroom"], "read_files_sha256": I["sha"],
              "interpretations": list(INTERPRETATIONS), "cost": cost, "memory_limit_gb": MEMORY_LIMIT_GB,
              "seconds": round(time.time() - t_all, 1)}
    notes = {"status": "EXPLORATORY (D-666): a solver-only fit read; no campaign, no variant counted, selects nothing",
             "labels": "every larger-size row: lock_assumed_1to1 (D-623: the lock balance is stated on no page; the "
                       "1:1 trail applied) and D-666 (5)'s assumptions", "verdict_line": line}
    desc = ("EXPLORATORY (D-666, program U's U4): the account-size fit read -- the base designs' state-table solver "
            "(v12's no-closure table) on each Topstep size's verified rows ($50K, $100K, $150K) under P-14's and "
            "P-16's own rungs and per-R edges (the bound arm's and zero): the zero-edge oracles against each size's "
            "bounds, an attempt's P(pass), payouts, fees, payouts per fee dollar, value and sessions to a first "
            "payout; D-666 (3)'s rule and verdict. The identities first (section identity). No campaign; no seed "
            "(an exact chain).")
    if a.check:
        tmp = Path(tempfile.mkdtemp(prefix="u_size_fit_check_"))
        try:
            csv, _ = write_result(df, RESULT, script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                                  results_dir=tmp, parameters=params, notes=notes, description=desc)
            print(f"--check: {len(df)} rows written to a temporary folder (removed); cost {json.dumps(cost)}; "
                  f"{time.time() - t_all:.0f} s")
            if line:
                print(f"(--check at a short horizon; its rule line is not the read's) {line}")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        return 0
    csv, _ = write_result(df, RESULT, script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                          results_dir=results_dir, parameters=params, notes=notes, description=desc)
    print(line)
    print(f"written: {csv} ({time.time() - t_all:.0f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
