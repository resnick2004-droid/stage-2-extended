"""EXPLORATORY (D-290): the account-state risk policy by dynamic programming over the contract, and its check in the
campaign engine -- engine-only, no market data, every setting fixed in config/state_policy.yaml before this ran.

    python scripts/state_policy_dp.py --declaration D-290

For each declared edge e and slot rent lambda: the funded DP (the XFA's value over the days left, its payout choice),
then the Combine DP (a pass worth the XFA's value less the activation), the fresh account propagated through each
policy, the fixed legs evaluated as policies by the same machinery (their payout the largest allowed, as the engine's
protocol requests), the DP's decisions projected onto the engine's policy tree, and that policy run through the
lockstep campaign with the engine's own binary draw against the fixed legs on one seed. The zero-edge oracles are
checked first, with the fees off, and the run refuses to continue if one fails.

Writes results/state_policy.csv (`oracle`, `dp`, `baseline`, `policy`, `campaign`, `summary` rows) and, beside it,
results/state_policy_policies.json (the exported engine policies by cell; its sha256 in the CSV's manifest notes).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from typing import Any
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

from propedge.campaign import state_policy as sp  # noqa: E402
from propedge.campaign import state_policy_risk as spr  # noqa: E402

SCRIPT = "scripts/state_policy_dp.py"
DECLARATION = "D-290"
#: D-302 re-exports the same solution with the no-trade states kept (export version 2), under its own result name;
#: D-306 solves the table with the allowance built in (export version 3) from its own config; D-313 adds the Combine's
#: two rules -- the room cap and the consistency cap (export version 4); D-316 the Combine's own menu (5); D-318 each
#: rung's availability -- the share of its trades whose room permits each R (6); D-321 the funded export keyed by its
#: winning days and, once paid, its payout-line band (7); D-325 the funded table solved under the operator's two rules
#: -- the tie-break toward the smaller risk and the risk cap once in profit (8); D-326 the unpaid funded balance band
#: split at the start, so the cap's exemption of the start does not reach the first in-profit states (9); D-329 the
#: slot rent derived as the cash rate per slot-day (the fixed point over the chain), an abandon action in both tables
#: and the Combine's tie-break (10).
#: D-332: every band the state space contains exported, the table's own day-0 decision where the chain never
#: visited (11) -- the same v10 solve.
#: D-333: the funded balance cap's band left out of the export (12) -- the same v10 solve.
#: D-339: the flip stream's action in the funded menu -- a scheduled bracket at its own measured edge, offered every
#: day (`Menu.flip`) -- and each cell's source on its leaf (13): a new solve, the two-stream candidate FV3-G/F.
DECLARATIONS = {"D-290": 1, "D-302": 2, "D-306": 3, "D-313": 4, "D-316": 5, "D-318": 6, "D-321": 7, "D-325": 8,
                "D-326": 9, "D-329": 10, "D-332": 11, "D-333": 12, "D-339": 13, "D-341": 14, "D-345": 15, "D-346": 16,
                "D-379": 17, "D-384": 18,
                "D-405": (19, 20, 21)}       # D-405: FV3-S's three aversions, one export version each (--export-version)
#: D-379: the export versions of the flip (two-stream) line; version 17 is FV3-C's line again (v12 and the collect
#: action), so the flip versions' descriptions do not carry into it
FLIP_VERSIONS = range(13, 17)
CONFIG = ROOT / "config" / "state_policy.yaml"
CONFIG_V3 = ROOT / "config" / "state_policy_v3.yaml"
CONFIG_V4 = ROOT / "config" / "state_policy_v4.yaml"
CONFIG_V5 = ROOT / "config" / "state_policy_v5.yaml"
CONFIG_V6 = ROOT / "config" / "state_policy_v6.yaml"
CONFIG_V7 = ROOT / "config" / "state_policy_v7.yaml"
CONFIG_V8 = ROOT / "config" / "state_policy_v8.yaml"
CONFIG_V9 = ROOT / "config" / "state_policy_v9.yaml"
CONFIG_V10 = ROOT / "config" / "state_policy_v10.yaml"
CONFIG_V11 = ROOT / "config" / "state_policy_v11.yaml"
CONFIG_V12 = ROOT / "config" / "state_policy_v12.yaml"
CONFIG_V13 = ROOT / "config" / "state_policy_v13.yaml"
CONFIG_V14 = ROOT / "config" / "state_policy_v14.yaml"
CONFIG_V15 = ROOT / "config" / "state_policy_v15.yaml"
CONFIG_V16 = ROOT / "config" / "state_policy_v16.yaml"
CONFIG_V17 = ROOT / "config" / "state_policy_v17.yaml"
CONFIG_V18 = ROOT / "config" / "state_policy_v18.yaml"
CONFIG_V19 = ROOT / "config" / "state_policy_v19.yaml"
CONFIG_V20 = ROOT / "config" / "state_policy_v20.yaml"
CONFIG_V21 = ROOT / "config" / "state_policy_v21.yaml"
#: D-405: the export versions solved under exponential utility (FV3-S), v12's table otherwise
CE_VERSIONS = (19, 20, 21)


def config_for(version: int) -> Path:
    """The config an export version is solved from (read at call time, so a test may point it elsewhere)."""
    return {3: CONFIG_V3, 4: CONFIG_V4, 5: CONFIG_V5, 6: CONFIG_V6, 7: CONFIG_V7, 8: CONFIG_V8,
            9: CONFIG_V9, 10: CONFIG_V10, 11: CONFIG_V11, 12: CONFIG_V12, 13: CONFIG_V13,
            14: CONFIG_V14, 15: CONFIG_V15, 16: CONFIG_V16, 17: CONFIG_V17, 18: CONFIG_V18,
            19: CONFIG_V19, 20: CONFIG_V20, 21: CONFIG_V21}.get(int(version), CONFIG)


def aversion_of(cfg: dict) -> float:
    """D-405: the aversion a per dollar the config's `objective` declares -- 0 for the expectation (a text objective,
    every version before 19); for `kind: exponential_utility` the a at which a fair coin to win or lose `coin_stake`
    is worth -`coin_loss` (`state_policy_risk.aversion_for`)."""
    obj = cfg.get("objective")
    if not isinstance(obj, dict):
        return 0.0
    if obj.get("kind") != "exponential_utility":
        raise SystemExit(f"REFUSED: the objective's kind is 'exponential_utility' or a text objective, got {obj.get('kind')!r}.")
    return spr.aversion_for(float(obj["coin_loss"]), float(obj.get("coin_stake", 1000.0)))


def find_rent(value, lo: float, hi: float, *, tol: float, max_rounds: int) -> tuple[float, list[dict]]:
    """D-405: the largest rent at which `value(rent)` (an attempt's worth net of its first subscription, falling with
    the rent) is still at least zero, to `tol`: a bracket [lo, hi] with the attempt worth at least zero at lo and less
    at hi (the upper end doubled while it is still worth more), narrowed by the secant through the bracket's ends --
    kept a quarter of the tolerance inside them -- each followed by a probe nine tenths of the tolerance across it, so a
    worth nearly straight in the rent (as it is: the rent times the slot-days) closes in a few solves; a bisection step
    whenever a secant step leaves the bracket wider than half. Returns lo when hi - lo is within `tol`; `value` may
    return (worth, extra fields) for the round's record. Refused when the attempt is not worth taking at the lower
    end, or when `max_rounds` evaluations do not settle it."""
    rounds: list[dict] = []
    tol = float(tol)

    def at(lam: float) -> float:
        if len(rounds) >= int(max_rounds):
            raise SystemExit(f"REFUSED: the rent's search did not settle in {max_rounds} rounds (last ${lam:.2f}).")
        out = value(float(lam))
        v, extra = (out if isinstance(out, tuple) else (out, {}))
        rounds.append({"round": len(rounds), "tie_break": False, "rent": float(lam), "value_attempt": float(v), **extra})
        return float(v)

    vlo = at(lo)
    if vlo < 0.0:
        raise SystemExit(f"REFUSED: an attempt is not worth taking even at a rent of ${lo:.2f} a slot-day.")
    vhi = at(hi)
    while vhi >= 0.0:
        lo, vlo = hi, vhi
        hi = 2.0 * hi if hi > 0 else 1.0
        vhi = at(hi)

    def take(x: float, vx: float) -> None:
        nonlocal lo, vlo, hi, vhi
        if vx >= 0.0:
            lo, vlo = x, vx
        else:
            hi, vhi = x, vx

    while hi - lo > tol:
        width = hi - lo
        x = lo + vlo * (hi - lo) / (vlo - vhi)                         # the secant's root inside the bracket
        x = min(max(x, lo + 0.25 * tol), hi - 0.25 * tol)
        vx = at(x)
        take(x, vx)
        if hi - lo <= tol:
            break
        y = x + 0.9 * tol if vx >= 0.0 else x - 0.9 * tol             # the probe across the secant's point
        if lo < y < hi:
            take(y, at(y))
        if hi - lo > 0.5 * width and hi - lo > tol:                   # a slow secant: bisect once
            mid = 0.5 * (lo + hi)
            take(mid, at(mid))
    rounds[-1]["converged_by"] = "secant"
    return float(lo), rounds


def v12_rent(cfg: dict, edge: float, results_dir: Path | None = None) -> float:
    """D-405: v12's lambda* at `edge` (the `dp` row of the declared file), the bisection's upper end."""
    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    tab = read_result(rd / Path(cfg["rent_fixed_point"]["ce_bracket_from"]).name)
    row = tab[(tab["section"] == "dp") & np.isclose(tab["edge"].astype(float), float(edge))]
    if len(row) != 1:
        raise SystemExit(f"REFUSED: {cfg['rent_fixed_point']['ce_bracket_from']} has {len(row)} dp rows at e={edge:+.3f}, not one.")
    return float(row.iloc[0]["slot_rent"])


def solve_rent_ce(cfg: dict, rules, edge: float, menu, results_dir: Path | None = None):
    """D-405: the rent in certainty equivalents at `edge` -- the largest at which a fresh attempt is still worth at
    least zero in the table's own objective, by `find_rent` on the exact tables from zero to v12's lambda* there --
    and the exported table solved with the tie-breaks at it. Returns as `solve_rent` does."""
    fp = cfg.get("rent_fixed_point") or {}

    def value(lam: float):
        f, fsol, ff, c, csol, cf = cell(cfg, rules, float(edge), lam, menu, tie_break=False)
        cash, days, rate = cycle_rate(rules, ff, cf)
        v = csol.value - rules.subscription
        print(f"  rent round e={edge:+.3f} (exact, certainty equivalent): ${lam:.2f}/day -> attempt {v:+.2f} "
              f"(expected cash rate ${rate:.2f}/day; p_pass {cf['p_pass']:.3f})", flush=True)
        return v, {"rate": rate, "cycle_cash": cash, "cycle_days": days, "p_pass": cf["p_pass"],
                   "p_abandon_combine": cf.get("p_abandon", 0.0), "p_abandoned_xfa": ff.get("p_abandoned", 0.0)}

    star, rounds = find_rent(value, 0.0, v12_rent(cfg, edge, results_dir), tol=float(fp.get("tolerance", 0.25)),
                             max_rounds=int(fp.get("ce_max_rounds", 14)))
    objs = cell(cfg, rules, float(edge), star, menu, tie_break=True)
    f, fsol, ff, c, csol, cf = objs
    cash, days, rate = cycle_rate(rules, ff, cf)
    rounds.append({"round": len(rounds), "tie_break": True, "rent": star, "rate": rate, "cycle_cash": cash,
                   "cycle_days": days, "value_attempt": csol.value - rules.subscription, "p_pass": cf["p_pass"],
                   "p_abandon_combine": cf.get("p_abandon", 0.0), "p_abandoned_xfa": ff.get("p_abandoned", 0.0),
                   "converged_by": "bisection"})
    print(f"  the exported table e={edge:+.3f} (tie-broken) at the certainty-equivalent rent ${star:.2f}/day: attempt "
          f"{csol.value - rules.subscription:+.2f}, p_pass {cf['p_pass']:.3f}", flush=True)
    return star, objs, rounds


def combine_rules(cfg: dict) -> dict:
    """D-313: the Combine's rules the table is solved under (`combine_rules`: room_cap, consistency_cap), as
    `CombineDP` keywords; D-329 adds its tie-break (`tie_break_tol`, `tie_prefer`). `abandon` is the menu's
    (`abandon_of`), not a solver keyword."""
    c = cfg.get("combine_rules") or {}
    out = {"room_cap": bool(c.get("room_cap", False)), "consistency_cap": bool(c.get("consistency_cap", False))}
    if c.get("tie_break_tol") is not None:
        out["tie_break_tol"] = float(c["tie_break_tol"])
    if c.get("tie_prefer") is not None:
        out["tie_prefer"] = str(c["tie_prefer"])
    return out


def funded_rules(cfg: dict) -> dict:
    """D-325: the funded table's rules (`funded_rules`: tie_break_tol, profit_risk_cap), as `FundedDP` keywords; {}
    without the block, under which every earlier version solves as before. D-329: `tie_prefer` too; `abandon` is the
    menu's (`abandon_of`)."""
    f = cfg.get("funded_rules") or {}
    out = {}
    if f.get("tie_break_tol") is not None:
        out["tie_break_tol"] = float(f["tie_break_tol"])
    if f.get("profit_risk_cap") is not None:
        out["profit_risk_cap"] = float(f["profit_risk_cap"])
    if f.get("tie_prefer") is not None:
        out["tie_prefer"] = str(f["tie_prefer"])
    return out


def abandon_of(cfg: dict, leg: str) -> bool:
    """D-329: whether `leg`'s menu ('combine' or 'funded') offers the abandon action."""
    block = cfg.get("combine_rules" if leg == "combine" else "funded_rules") or {}
    return bool(block.get("abandon", False))


def rent_mode(cfg: dict):
    """D-329: the declared rents -- a list of dollars a slot-day, or 'fixed_point' (lambda* per edge)."""
    r = cfg["slot_rent_per_day"]
    if isinstance(r, str):
        if r != "fixed_point":
            raise SystemExit(f"REFUSED: slot_rent_per_day is a list of rents or 'fixed_point', got {r!r}.")
        return "fixed_point"
    return [float(x) for x in r]


def cycle_rate(rules, ff: dict, cf: dict) -> tuple[float, float, float]:
    """D-329: one attempt's cash and slot-days over the chain -- the Combine's subscription at purchase and accrued
    per trading day, the activation at a pass, the XFA's net payouts; the days the Combine held its slot plus, when
    it passed, the XFA's -- and their ratio, the cash rate per slot-day."""
    cash = cf["p_pass"] * (ff["mean_cash"] - rules.activation) - rules.subscription - cf["mean_subscriptions_accrued"]
    days = cf["mean_days"] + cf["p_pass"] * ff["mean_days"]
    return float(cash), float(days), float(cash / days) if days > 0 else 0.0


def solve_rent(cfg: dict, rules, edge: float, menu, start: float):
    """D-329 / D-331: lambda* at `edge` -- the campaign's cash rate per slot-day, the rent at which a fresh attempt's
    value net of rent is zero -- read from the EXACT tables (the declared rules without their dollar tie-breaks,
    abandon exact), by Dinkelbach's step (solve the chain at the rent, read the policy's cash rate per slot-day, make
    that the rent) until the rate is within the tolerance of the rent it was solved at; the rounds also bracket the
    threshold and bisect it, a safety net should the step ever bounce (as the tie-broken tables' did). Then the table
    that is exported is solved WITH the tie-breaks at lambda*; its own rate is read and recorded beside lambda*, the
    difference being the tie-breaks' price (D-325's and D-329's display rules, a few dollars an attempt). Returns
    lambda*, the exported table's objects, the rounds (the exact rounds, then the final tie-broken solve, flagged),
    and how the fixed point converged. D-405: a table under exponential utility takes its rent from `solve_rent_ce`."""
    if aversion_of(cfg) > 0.0:
        return solve_rent_ce(cfg, rules, edge, menu)
    fp = cfg.get("rent_fixed_point") or {}
    tol = float(fp.get("tolerance", 0.25))
    lam = float(start)
    rounds: list[dict] = []
    lo = None                                                   # (rent, rate): the attempt worth >= 0 there
    hi = None                                                   # rent: the attempt worth < 0 there
    star = None
    for k in range(int(fp.get("max_rounds", 10))):
        objs = cell(cfg, rules, float(edge), lam, menu, tie_break=False)
        f, fsol, ff, c, csol, cf = objs
        cash, days, rate = cycle_rate(rules, ff, cf)
        value = csol.value - rules.subscription
        rounds.append({"round": k, "tie_break": False, "rent": lam, "rate": rate, "cycle_cash": cash,
                       "cycle_days": days, "value_attempt": value, "p_pass": cf["p_pass"],
                       "p_abandon_combine": cf.get("p_abandon", 0.0), "p_abandoned_xfa": ff.get("p_abandoned", 0.0)})
        print(f"  rent round {k} e={edge:+.3f} (exact): solved at ${lam:.2f}/day -> earns ${rate:.2f}/day "
              f"(attempt {value:+.2f}; p_pass {cf['p_pass']:.3f}; abandoned combine "
              f"{cf.get('p_abandon', 0.0):.3f}, xfa {ff.get('p_abandoned', 0.0):.3f})", flush=True)
        del objs, f, fsol, c, csol
        if abs(rate - lam) <= tol:
            rounds[-1]["converged_by"] = "rate"
            star, how = lam, "rate"
            break
        if value >= 0.0:
            if lo is None or lam > lo[0]:
                lo = (lam, rate)
        else:
            hi = lam if hi is None else min(hi, lam)
        if lo is not None and hi is not None:
            if hi - lo[0] <= tol:
                rounds[-1]["converged_by"] = "bracket"
                star, how = lo[0], "bracket"                     # the largest rent the exact attempt still earns
                break
            lam = rate if lo[0] < rate < hi else (lo[0] + hi) / 2.0
        else:
            lam = rate                                           # Dinkelbach's step while there is no bracket
    if star is None:
        raise SystemExit(f"REFUSED: the rent's fixed point at e={edge:+.3f} did not converge in {len(rounds)} rounds "
                         f"(last rent {lam:.2f}, rate {rate:.2f}); the DP is wrong or the tolerance too tight.")
    objs = cell(cfg, rules, float(edge), star, menu, tie_break=True)       # the exported table, at lambda*
    f, fsol, ff, c, csol, cf = objs
    cash, days, rate = cycle_rate(rules, ff, cf)
    rounds.append({"round": len(rounds), "tie_break": True, "rent": star, "rate": rate, "cycle_cash": cash,
                   "cycle_days": days, "value_attempt": csol.value - rules.subscription, "p_pass": cf["p_pass"],
                   "p_abandon_combine": cf.get("p_abandon", 0.0), "p_abandoned_xfa": ff.get("p_abandoned", 0.0),
                   "converged_by": how})
    print(f"  the exported table e={edge:+.3f} (tie-broken) at lambda* ${star:.2f}/day earns ${rate:.2f}/day "
          f"(attempt {csol.value - rules.subscription:+.2f}; p_pass {cf['p_pass']:.3f}; abandoned combine "
          f"{cf.get('p_abandon', 0.0):.3f}, xfa {ff.get('p_abandoned', 0.0):.3f})", flush=True)
    return star, objs, rounds
SUMMARY_KEYS = ("median_log_growth", "share_log_growth_undefined", "mean_final_cash", "median_final_cash",
                "p10_final_cash", "p90_final_cash", "ruin_probability", "mean_max_drawdown", "p90_max_drawdown",
                "median_days_to_first_payout", "share_accounts_ever_paid", "mean_accounts_funded",
                "share_trades_at_tier_cap", "share_trades_unsized")


def config(path: Path | None = None) -> dict:
    return yaml.safe_load(Path(path or CONFIG).read_text(encoding="utf-8"))


def rungs_of(cfg: dict, results_dir: Path | None = None) -> sp.Rungs | None:
    """D-306: the config's `rungs` block -- the fixed stops in ticks times the tick value, the rungs' shares read from
    the declared result file (one row per rung at the declared phase), the allowance per leg and the exit grid."""
    r = cfg.get("rungs")
    if not r:
        return None
    from propedge import RESULTS_DIR

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    shares = pd.read_csv(rd / Path(r["file"]).name)
    shares = shares[shares["phase"].astype(str) == str(r.get("phase", "all"))].set_index("rung")
    names = ("half", "full", "double")
    if any(n not in shares.index for n in names):
        raise SystemExit(f"REFUSED: {r['file']} lacks a share for every rung at phase {r.get('phase', 'all')!r}.")
    availability = ()
    if r.get("availability_file"):                    # D-318: each rung's share of trades whose room permits each R
        av = pd.read_csv(rd / Path(r["availability_file"]).name)
        av = av[av["phase"].astype(str) == str(r.get("phase", "all"))]
        if any(n not in set(av["rung"]) for n in names):
            raise SystemExit(f"REFUSED: {r['availability_file']} lacks a rung at phase {r.get('phase', 'all')!r}.")
        availability = tuple(tuple((float(x.rr), float(x.share)) for x in av[av["rung"] == n].sort_values("rr").itertuples())
                             for n in names)
    return sp.Rungs(risk_per_contract=tuple(float(r["stops_ticks"][n]) * float(r["tick_value"]) for n in names),
                    shares=tuple(float(shares.loc[n, "share"]) for n in names),
                    combine_cap=int(r["combine_cap_micros"]),
                    funded_caps=tuple(sorted((float(k), int(v)) for k, v in r["funded_caps"].items())),
                    exit_grid=tuple(float(x) for x in r.get("exit_grid", ())), availability=availability)


def _select_rows(tab: pd.DataFrame, flt: dict | None) -> pd.DataFrame:
    """The rows of `tab` matching every `column: value` of `flt` -- a numeric column to float, anything else as text
    (pandas' Arrow-backed strings are not dtype object)."""
    sel = tab
    for k, v in (flt or {}).items():
        if k not in sel.columns:
            raise SystemExit(f"REFUSED: the file has no column {k!r} to select the flip's row by.")
        col = sel[k]
        sel = sel[np.isclose(col.astype(float), float(v)) if pd.api.types.is_numeric_dtype(col) else (col.astype(str) == str(v))]
    return sel


def _select_row(tab: pd.DataFrame, flt: dict | None):
    sel = _select_rows(tab, flt)
    if len(sel) != 1:
        raise SystemExit(f"REFUSED: {len(sel)} rows match {flt}, not one.")
    return sel.iloc[0]


def flip_of(cfg: dict, results_dir: Path | None = None) -> tuple[tuple | None, dict]:
    """D-339: the flip stream's action from `funded_flip` -- its risk and R as declared, its net edge READ from the
    bracket statistics on record (the no-edge bracket study's `inputs` row the config names: development data), never
    typed -- and the provenance for the dp row (the file, its sha256, the edge, its lower bound). (None, {}) without
    the block."""
    f = cfg.get("funded_flip")
    if not f:
        return None, {}
    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    path = rd / Path(f["source_file"]).name
    tab = read_result(path)
    sel = _select_rows(tab, f.get("row"))
    if len(sel) != 1:
        raise SystemExit(f"REFUSED: {f['source_file']} holds {len(sel)} rows for the flip's statistics {f.get('row')}, not one.")
    row = sel.iloc[0]
    edge = float(row[f.get("edge_field", "e_net")])
    lb_field = f.get("lower_bound_field", "e_net_lower_bound")
    lb = float(row[lb_field]) if lb_field in row and pd.notna(row[lb_field]) else float("nan")
    # D-343: a time-boxed bracket's scratch share, read from the row when the config names its field
    sf = f.get("scratch_field")
    p_scratch = float(row[sf]) if sf else 0.0
    if not 0.0 <= p_scratch < 1.0:
        raise SystemExit(f"REFUSED: the flip's scratch share {p_scratch} is not in [0, 1).")
    import hashlib

    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    info = {"flip_risk": float(f["risk"]), "flip_rr": float(f["rr"]), "flip_edge": edge, "flip_edge_lower_bound": lb,
            "flip_target_share": float(row["target_share"]) if "target_share" in row else float("nan"),
            "flip_cost_r": float(row["cost_r"]) if "cost_r" in row else float("nan"),
            "flip_scratch_share": p_scratch, "flip_copy": bool(f.get("copy", False)),
            "flip_source_file": str(f["source_file"]), "flip_source_sha256": sha}
    return (float(f["risk"]), float(f["rr"]), edge, p_scratch), info


def flip_menu_of(cfg: dict) -> tuple[tuple, dict]:
    """D-384: the collect menu's actions from `funded_flips` -- the brackets the collect map's `menu` rows name, each
    (risk, R, its net edge per attempt over the risk, its scratch share) priced from the capture's counts over the
    declared `years` by the collect scorer's arithmetic -- and their provenance for the dp rows. ((), {}) without the
    block."""
    f = cfg.get("funded_flips")
    if not f:
        return (), {}
    import hashlib

    import score_collect_map as scm

    from propedge.data import flip_kit as fk
    from propedge.reporting.results import read_result

    q = fk.params_collect()
    files = {k: ROOT / f[k] for k in ("map_file", "counts_file", "spread_file")}
    spreads = read_result(files["spread_file"])
    spreads = spreads[spreads["kind"] == "spread"]
    counts = read_result(files["counts_file"])
    out, notes = [], []
    for b in scm.menu_brackets(read_result(files["map_file"])):
        st = scm.bracket_stats(counts, spreads, f["years"], b, fee=float(q["fee_round_turn"]),
                               mpv=float(q["micro_point_value"]), tick=float(q["tick"]))
        out.append((float(st["risk_dollars"]), float(st["rr"]), float(st["e_net"]), float(st["scratch_share"])))
        notes.append(f"{b['stop_multiple']:g}x ${st['risk_dollars']:g}: e {st['e_net']:+.4f}, scratch {st['scratch_share']:.4f}")
    info = {"flips_menu": "; ".join(notes), "flips_years": ",".join(str(int(y)) for y in f["years"]),
            "flips_copy": bool(f.get("copy", True)),
            **{f"flips_{k}": str(f[k]) for k in files},
            **{f"flips_{k}_sha256": hashlib.sha256(files[k].read_bytes()).hexdigest() for k in files}}
    return tuple(out), info


def flip_risk_per_contract(f: dict, row) -> float | None:
    """D-343: what one contract risks at the flip's stop -- the row's `stop_dollars` (a micro at the study's stop), or
    `risk_per_contract: {field, point_value}` (a width in points times the contract's point value), else None."""
    rpc = f.get("risk_per_contract")
    if isinstance(rpc, dict):
        return float(row[rpc["field"]]) * float(rpc["point_value"])
    if rpc is not None:
        return float(rpc)
    sd = (f.get("row") or {}).get("stop_dollars")
    return float(sd) if sd is not None else None


def menu_of(cfg: dict, results_dir: Path | None = None) -> sp.Menu:
    """The funded leg's menu; D-329: with the abandon action when `funded_rules.abandon` says so; D-339: with the flip
    stream's action when `funded_flip` is declared; D-379: with the collect action at each of `menu.collect_risks`."""
    m = cfg["menu"]
    flip, _ = flip_of(cfg, results_dir)
    flips, _ = flip_menu_of(cfg)                                    # D-384: the collect menu's brackets
    return sp.Menu(risks=tuple(float(x) for x in m["risks"]), rrs=tuple(float(x) for x in m["rrs"]),
                   skip=bool(m["skip"]), step=float(m["step"]), rungs=rungs_of(cfg, results_dir),
                   abandon=abandon_of(cfg, "funded"), flip=flip,
                   collect=tuple(float(x) for x in (m.get("collect_risks") or ())), flips=flips)


def combine_menu_of(cfg: dict, menu: sp.Menu) -> sp.Menu:
    """D-316: the Combine's own menu (`combine_menu`: risks, rrs, min_rr), on the shared menu's grid, skip and rungs;
    without the block the Combine reads the shared menu. D-329: its abandon action from `combine_rules.abandon`.
    D-339: never the flip (no winning-day rule on a Combine)."""
    c = cfg.get("combine_menu")
    ab = abandon_of(cfg, "combine")
    if not c:
        return menu if (menu.abandon == ab and menu.flip is None and not menu.collect and not menu.flips) else sp.Menu(
            risks=menu.risks, rrs=menu.rrs, skip=menu.skip, step=menu.step, rungs=menu.rungs, min_rr=menu.min_rr,
            abandon=ab)
    return sp.Menu(risks=tuple(float(x) for x in c["risks"]), rrs=tuple(float(x) for x in c["rrs"]),
                   skip=menu.skip, step=menu.step, rungs=menu.rungs, min_rr=float(c.get("min_rr", 1.0)), abandon=ab)


def without_flip(menu: sp.Menu) -> sp.Menu:
    """The menu less its flip action (D-339): the zero-edge oracle's funded table, where every action must be fair."""
    if menu.flip is None and not menu.flips:                     # D-384: the collect menu's brackets too
        return menu
    return sp.Menu(risks=menu.risks, rrs=menu.rrs, skip=menu.skip, step=menu.step, rungs=menu.rungs,
                   min_rr=menu.min_rr, abandon=menu.abandon, collect=menu.collect)


def oracles(cfg: dict, rules, menu: sp.Menu | None = None) -> tuple[list[dict], bool]:
    """Stage one's ceilings at zero edge with the fees off (CLAUDE.md): a value outside one is an error. With rungs
    (D-306) the menu's ceiling check runs on the allowance-aware table too: every action is fair on the grid."""
    from dataclasses import replace

    r0 = replace(rules, subscription=0.0, activation=0.0, reset_fee=0.0, payout_fee=0.0, profit_split=1.0)
    T = int(cfg["horizon_days"])
    menu = menu_of(cfg) if menu is None else menu
    o = cfg["oracles"]
    rows, ok = [], True
    c = sp.CombineDP(r0, sp.Menu.fixed(1500.0, 1.0, menu.step), 0.0, T)
    v = c.forward(c.solve(np.ones(T)))["p_pass"]
    rows.append({"section": "oracle", "check": "p_pass_1to1_1500_zero_edge_no_fees", "value": v,
                 "bound": o["zero_edge_no_fees_p_pass_1to1_1500"], "relation": "equal", "held": abs(v - o["zero_edge_no_fees_p_pass_1to1_1500"]) < 1e-6})
    # the contract's ceiling of the fair table: the Combine's rules, without D-329's dollar tie-break (a pass is worth
    # 1 here, so every action would tie within it and abandon would be preferred)
    c = sp.CombineDP(r0, combine_menu_of(cfg, menu), 0.0, T,
                     **{k: v for k, v in combine_rules(cfg).items() if k in ("room_cap", "consistency_cap")})
    v = c.solve(np.ones(T)).value
    rows.append({"section": "oracle", "check": "max_p_pass_zero_edge_no_fees", "value": v,
                 "bound": o["zero_edge_no_fees_max_p_pass"], "relation": "at_most", "held": v <= o["zero_edge_no_fees_max_p_pass"] + 1e-6})
    # D-339: the oracle's funded table without the flip -- the ceiling is of fair actions, and the flip carries its own
    # measured (negative) edge, which could only lower the payouts
    f = sp.FundedDP(r0, without_flip(menu), 0.0, T, balance_cap=float(cfg["funded"]["balance_cap"]),
                    payout_grid_step=float(cfg["funded"]["payout_grid_step"]), **funded_rules(cfg))
    v = f.forward(f.solve())["mean_gross_paid"]
    rows.append({"section": "oracle", "check": "max_gross_payouts_zero_edge_no_fees", "value": v,
                 "bound": o["zero_edge_no_fees_max_gross_payouts"], "relation": "at_most", "held": v <= o["zero_edge_no_fees_max_gross_payouts"] + 1e-6})
    a = aversion_of(cfg)
    if a > 0.0:
        # D-405: the risk-averse tables inside the same ceilings -- the Combine's pass worth stage one's gross-payout
        # ceiling (a pass worth 1 would make the aversion vanish), the XFA's gross payouts under its own policy
        cap = float(o["zero_edge_no_fees_max_gross_payouts"])
        c = spr.CombineCE(r0, combine_menu_of(cfg, menu), 0.0, T, aversion=a,
                          **{k: v for k, v in combine_rules(cfg).items() if k in ("room_cap", "consistency_cap")})
        v = c.forward(c.solve(np.full(T, cap)))["p_pass"]
        rows.append({"section": "oracle", "check": "ce_p_pass_zero_edge_no_fees", "value": v,
                     "bound": o["zero_edge_no_fees_max_p_pass"], "relation": "at_most",
                     "held": v <= o["zero_edge_no_fees_max_p_pass"] + 1e-6})
        f = spr.FundedCE(r0, without_flip(menu), 0.0, T, balance_cap=float(cfg["funded"]["balance_cap"]),
                         payout_grid_step=float(cfg["funded"]["payout_grid_step"]), aversion=a, **funded_rules(cfg))
        v = f.forward(f.solve())["mean_gross_paid"]
        rows.append({"section": "oracle", "check": "ce_gross_payouts_zero_edge_no_fees", "value": v, "bound": cap,
                     "relation": "at_most", "held": v <= cap + 1e-6})
    ok = all(r["held"] for r in rows)
    return rows, ok


def edges_of(cfg: dict) -> list[float]:
    """The edges a table is solved at: the config's `outcomes.edges`, or (D-405) `outcomes.solve_edges` where a
    table declares the subset its runs read."""
    o = cfg["outcomes"]
    return [float(x) for x in (o.get("solve_edges") or o["edges"])]


def _without_tie_break(kw: dict) -> dict:
    return {k: v for k, v in kw.items() if k not in ("tie_break_tol", "tie_prefer")}


def cell(cfg: dict, rules, edge: float, lam: float, menu: sp.Menu, *, payout_choice: str = "optimal",
         tie_break: bool = True):
    """Both DPs at (edge, lambda) under `menu`; returns the DPs, solutions and forward summaries. `tie_break=False`
    (D-331): the exact tables -- the declared rules without their dollar tie-breaks -- which the rent's fixed point
    is read from; the table that is exported is solved with them, at that rent."""
    T = int(cfg["horizon_days"])
    fr, cr = funded_rules(cfg), combine_rules(cfg)
    if not tie_break:
        fr, cr = _without_tie_break(fr), _without_tie_break(cr)
    a = aversion_of(cfg)                                           # D-405: exponential utility; 0 is the expectation
    F, C = (sp.FundedDP, sp.CombineDP) if a <= 0.0 else (spr.FundedCE, spr.CombineCE)
    ka = {} if a <= 0.0 else {"aversion": a}
    f = F(rules, menu, edge, T, lam, balance_cap=float(cfg["funded"]["balance_cap"]),
          payout_grid_step=float(cfg["funded"]["payout_grid_step"]), payout_choice=payout_choice,
          **fr, **ka)                                              # D-325: the rules live in the table, not the fixed legs
    fsol = f.solve()
    ff = f.forward(fsol)
    c = C(rules, combine_menu_of(cfg, menu), edge, T, lam, **cr, **ka)
    csol = c.solve(fsol.fresh_value[1:T + 1] - rules.activation)
    cf = c.forward(csol)
    return f, fsol, ff, c, csol, cf


def row_of(section: str, edge: float, lam: float, name: str, rules, fsol, ff, csol, cf) -> dict:
    r = {"section": section, "edge": edge, "slot_rent": lam, "policy": name,
         "value_attempt": csol.value - rules.subscription,       # the first subscription is paid at purchase
         "value_combine": csol.value, "value_xfa_fresh": fsol.value,
         "p_pass": cf["p_pass"], "p_fail": cf["p_fail"], "p_unresolved": cf["p_unresolved"],
         "combine_mean_days": cf["mean_days"], "combine_mean_days_to_pass": cf["mean_days_to_pass"],
         "subscriptions_accrued": cf["mean_subscriptions_accrued"], "subscriptions_engine": cf["mean_subscriptions_engine"],
         "xfa_mean_cash": ff["mean_cash"], "xfa_mean_gross_paid": ff["mean_gross_paid"],
         "xfa_mean_payouts": ff["mean_payouts"], "xfa_p_paid": ff["p_paid"], "xfa_p_closed": ff["p_closed"],
         "xfa_p_alive_at_end": ff["p_alive_at_end"], "xfa_mean_days": ff["mean_days"]}
    for k, v in ff["alive_at"].items():
        r[f"xfa_alive_at_{k}"] = v
    # cash per attempt from the chain, without the rent: the pass probability times the XFA's cash, less fees
    r["chain_cash_no_rent"] = (cf["p_pass"] * (ff["mean_cash"] - rules.activation) - rules.subscription
                               - cf["mean_subscriptions_accrued"])
    return r


def collect_as_bracket(d: Any, need: float) -> Any:
    """D-379: the policy dict with every collect leaf as a bracket at its risk and R = `need` / risk -- the table's own
    pricing of the collect action without the exit grid -- for the binary campaign check, whose draw has no stretch
    mode; the real campaigns run the leaf through the router and `TierSizedDraw`'s stretch walk."""
    if isinstance(d, dict):
        if d.get("type") == "fixed" and d.get("source") == "collect":
            out = {k: v for k, v in d.items() if k != "source"}
            out.update({"rr": float(need) / float(d["risk"]), "name": str(d.get("name", "collect")) + " (binary check)"})
            return out
        return {k: collect_as_bracket(v, need) for k, v in d.items()}
    if isinstance(d, list):
        return [collect_as_bracket(x, need) for x in d]
    return d


#: D-407: FV3's gate's never-binding cash (`score_fv3_grid.UNBOUND_BANKROLL`, D-312), for a check whose bankroll is an
#: output of the run
UNBOUND_BANKROLL = 100_000_000.0


def check_bankroll(cc: dict) -> float:
    """The campaign check's starting cash: the stated `bankroll`, or (D-407) under `bankroll_mode: output` cash that
    never binds, as FV3's gate reads a campaign (D-312) -- the required bankroll then comes from the paths."""
    mode = str(cc.get("bankroll_mode", "stated"))
    if mode not in ("stated", "output"):
        raise SystemExit(f"REFUSED: campaign_check.bankroll_mode is 'stated' or 'output', got {mode!r}.")
    return UNBOUND_BANKROLL if mode == "output" else float(cc["bankroll"])


def campaign(cfg: dict, rules, edge: float, policy_dict: dict | None, seed: int, results_dir: Path | None = None) -> dict:
    """The lockstep campaign with the engine's binary draw at `edge`, placement off (D-289); `policy_dict` the
    exported policy (None: the fixed legs). A plain function of plain arguments, so it can run in a worker process.
    `results_dir` is where the flip's source file is read from (D-339; the results directory by default)."""
    from propedge.campaign.lockstep import simulate_lockstep_campaign
    from propedge.campaign.protocols import Protocol
    from propedge.campaign.risk_policy import RiskPolicy

    from propedge.campaign.risk_policy import PHASES

    if policy_dict is not None:                                   # D-379: no stretch mode in the binary draw
        policy_dict = collect_as_bracket(policy_dict, float(rules.std_winning_day_min))
    policy = None if policy_dict is None else RiskPolicy.from_dict(policy_dict)
    cc = cfg["campaign_check"]
    legs = cc["fixed_legs"]
    protocol = Protocol(name="state_policy_check", combine_rr=float(legs["combine_rr"]), combine_risk=float(legs["combine_risk"]),
                        funded_rr=float(legs["funded_rr"]), funded_risk=float(legs["funded_risk"]), trades_per_day=1,
                        payout_path="standard", keep_balance=0.0, payout_frac=1.0,
                        max_concurrent_accounts=int(cc["accounts"]), family="state_policy", source="config/state_policy.yaml")
    # D-339: a policy with flip leaves runs them through the table's own binary model of the flip (its edge from the
    # file, as the DP priced it), so the check exercises the exported table as the engine will read it
    flip_for_path = None
    has_flips = policy is not None and any(getattr(l, "source", "strategy") == "flip" for l, _ in policy.root.leaves(frozenset(PHASES)))
    flips_menu, flips_info = flip_menu_of(cfg)                     # D-384: the collect menu's brackets, as priced
    if has_flips and flips_menu:
        from propedge.campaign.lockstep import binary_flip_menu_for_path

        flip_for_path = binary_flip_menu_for_path(flips_menu, copy=bool(flips_info.get("flips_copy", True)))
    elif has_flips:
        from propedge.campaign.lockstep import binary_flip_for_path

        flip, info = flip_of(cfg, results_dir)
        if flip is None:
            raise ValueError("the policy has flip leaves but the config declares no funded_flip (D-339)")
        ff = cfg.get("funded_flip") or {}
        if isinstance(ff.get("risk_per_contract"), dict):          # D-343: a width in points times the point value
            from propedge import RESULTS_DIR
            from propedge.reporting.results import read_result

            rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
            rpc = flip_risk_per_contract(ff, _select_row(read_result(rd / Path(ff["source_file"]).name), ff.get("row")))
        else:
            rpc = flip_risk_per_contract(ff, None)
        flip_for_path = binary_flip_for_path(flip[0], flip[1], flip[2], rpc, p_scratch=flip[3] if len(flip) > 3 else 0.0,
                                             copy=bool(info.get("flip_copy", False)))
    summary, paths = simulate_lockstep_campaign(
        protocol, edge=float(edge), seed=int(seed), initial_bankroll=check_bankroll(cc), rules=rules,
        horizon_days=int(cc["horizon_days"]), n_paths=int(cc["n_paths"]), payout_method=cc["payout_method"],
        max_concurrent_accounts=int(cc["accounts"]), max_concurrent_combines=int(cc["combines"]),
        max_total_accounts=int(cc["accounts"]), require_verified_cap=False, conduct=None, risk_policy=policy,
        flip_for_path=flip_for_path)
    s = summary.as_dict()
    out = {k: s.get(k) for k in SUMMARY_KEYS}
    days = np.array([getattr(a, "days", np.nan) for p in paths for a in p.funded], float)
    paid = np.array([getattr(a, "n_payouts", 0) for p in paths for a in p.funded], float)
    flips = sum(int(getattr(p.path, "funded_flips", 0)) for p in paths)
    won = sum(int(getattr(p.path, "funded_flips_won", 0)) for p in paths)
    out.update({"xfa_n": int(days.size), "xfa_mean_days": float(np.nanmean(days)) if days.size else float("nan"),
                "xfa_median_days": float(np.nanmedian(days)) if days.size else float("nan"),
                "xfa_p90_days": float(np.nanpercentile(days, 90)) if days.size else float("nan"),
                "xfa_share_over_70_days": float(np.nanmean(days > 70)) if days.size else float("nan"),
                "xfa_share_paid": float(np.mean(paid > 0)) if paid.size else float("nan"),
                "combines_per_path": float(np.mean([len(p.combines) for p in paths])),
                "policy_has_flip_leaves": bool(has_flips),                                        # D-339
                "funded_flips_per_path": float(flips / len(paths)) if paths else float("nan"),
                "share_flips_won": float(won / flips) if flips else float("nan")})
    if "margin" in cc:                     # D-405: the steadiness measures and the growth on the required bankroll
        from propedge.campaign import portfolio as pf
        from propedge.campaign import steadiness as st

        pm = pf.measures(paths, margin=float(cc["margin"]))
        out.update({"pf_growth_on_base_p50": pm.get("growth_on_base_p50"), "pf_required_p90": pm.get("required_p90"),
                    **st.measures(paths)})
    return out


def export_description(cfg: dict, e: float, lam: float, export_version: int) -> str:
    """The exported policy's description at (edge, rent) for `export_version` -- `main`'s own text, a function so a
    re-solve of a declared table (scripts/a3_compliance.py, D-501) writes it to the character."""
    return (f"D-290: the DP's policy at edge {e:+.3f}, slot rent ${lam:.2f}/day"
            + (" -- export v17 (D-379): the funded menu's collect action (a routed "
               "signal with a take-profit at the winning-day minimum)"
               if export_version == 17 else "")
            + (" -- export v18 (D-384): the funded menu's collect brackets (08:30 CT, "
               "five MNQ, a $200 target, stops 1x to 4x)"
               if export_version == 18 else "")
            + (f" -- export v{export_version} (D-405, FV3-S): v12's table under "
               "exponential utility, a fair coin to win or lose "
               f"${float(cfg['objective']['coin_stake']):,.0f} worth "
               f"-${float(cfg['objective']['coin_loss']):,.0f}; the rent in "
               "certainty equivalents"
               if export_version in CE_VERSIONS else "")
            + (" -- export v16 (D-346): the flip in five micros ($200 at the same width)"
               if export_version in FLIP_VERSIONS and export_version >= 16 else "")
            + (" -- export v15 (D-345): the flip is the fast bracket the flip map "
               "chose, with its scratch share"
               if export_version in FLIP_VERSIONS and export_version >= 15 else "")
            + (" -- export v14 (D-341): the funded tie-break prefers the flip at "
               "equal risk"
               if export_version in FLIP_VERSIONS and export_version >= 14 else "")
            + (" -- export v13 (D-339): the flip stream's action in the funded "
               "menu at its own measured edge, each leaf's source"
               if export_version in FLIP_VERSIONS and export_version >= 13 else "")
            + (" -- export v12 (D-333): the funded balance cap's band left out"
               if export_version >= 12 else "")
            + (" -- export v11 (D-332): every band the state space contains, the "
               "table's own decision where its chain never visited"
               if export_version >= 11 else "")
            + (" -- export v10 (D-329): the rent is the cash rate per slot-day at "
               "this edge (the fixed point), both tables may abandon the account, "
               "the Combine breaks ties toward the higher R"
               if export_version >= 10 else "")
            + (" -- export v9 (D-326): v8's, the unpaid funded balance band split at "
               "the start so the cap's exemption of the start stays there"
               if export_version >= 9 else "")
            + (" -- export v8 (D-325): v7's export of the funded table solved under "
               "the operator's two rules -- the smallest risk among actions within "
               f"${funded_rules(cfg).get('tie_break_tol', 0):g} of the best value, and "
               f"no more than ${funded_rules(cfg).get('profit_risk_cap', 0):g} at risk "
               "once the balance is above its start"
               if export_version >= 8 else
               " -- export v7 (D-321): v6's table, the funded decisions keyed by their "
               "winning days and, once paid, their payout-line band"
               if export_version >= 7 else
               " -- export v6 (D-318): v5 with each rung's availability -- the share of "
               "its trades whose room permits each R; a day without it is no trade"
               if export_version >= 6 else
               " -- export v5 (D-316): v4 with the Combine's own menu -- higher risks and R "
               "below 1 (the operator)"
               if export_version >= 5 else
               " -- export v4 (D-313): the allowance built in, need-aware Combine exits, "
               "the Combine's room cap and consistency cap"
               if export_version >= 4 else
               " -- export v3 (D-306): solved with the allowance built in, need-aware Combine exits"
               if export_version >= 3 else
               " -- export v2 (D-302): no-trade states kept" if export_version >= 2 else ""))


def _campaign_job(args: tuple) -> dict:
    cfg, rules, e, lam, pid, pol, seed, rd = args
    return {"section": "campaign", "edge": e, "slot_rent": lam, "policy_id": pid,
            **campaign(cfg, rules, float(e), pol, seed, results_dir=rd)}


def main(argv: list[str] | None = None, *, results_dir: Path | None = None, record: bool = True,
         edges: list[float] | None = None, rents: list[float] | None = None, skip_campaign: bool = False,
         workers: int = 4) -> int:
    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.campaign.payout_method import rules_for_method
    from propedge.reporting.results import write_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--declaration", required=True)
    ap.add_argument("--result-name", default="state_policy",
                    help="the result's name (state_policy; D-302's re-export writes state_policy_v2 and its policies file)")
    ap.add_argument("--export-version", type=int, default=None,
                    help="D-405: the version, where one declaration declares several (19, 20 or 21)")
    a = ap.parse_args(argv)
    if a.declaration not in DECLARATIONS or f"| {a.declaration} |" not in (ROOT / "DECISIONS.md").read_text(encoding="utf-8"):
        print(f"REFUSED: the DP is declared by {sorted(DECLARATIONS)} (DECISIONS.md); got {a.declaration!r} or the row is missing.")
        return 2
    export_version = DECLARATIONS[a.declaration]
    if isinstance(export_version, tuple):                        # D-405: one declaration, several versions
        if a.export_version not in export_version:
            print(f"REFUSED: {a.declaration} declares the versions {export_version}; name one with --export-version.")
            return 2
        export_version = int(a.export_version)
    elif a.export_version is not None and a.export_version != export_version:
        print(f"REFUSED: {a.declaration} declares version {export_version}, not {a.export_version}.")
        return 2
    cfg_path = config_for(export_version)
    cfg = config(cfg_path)
    if str(cfg.get("decision")) != a.declaration and export_version >= 3:
        print(f"REFUSED: {cfg_path.name} is declared by {cfg.get('decision')}, not {a.declaration}.")
        return 2
    rules = rules_for_method(cfg["campaign_check"]["payout_method"])
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    menu = menu_of(cfg, rd)
    _, flip_info = flip_of(cfg, rd)                              # D-339: the flip's provenance on every dp row
    flip_info = {**flip_info, **flip_menu_of(cfg)[1]}               # D-384: and the collect menu's
    rows, ok = oracles(cfg, rules, menu)
    for r in rows:
        print(f"oracle {r['check']}: {r['value']:.6f} {r['relation']} {r['bound']} -> {'held' if r['held'] else 'FAILED'}")
    if not ok:
        print("REFUSED: an oracle failed; the DP is wrong, not the contract.")
        return 3
    edges = edges_of(cfg) if edges is None else list(edges)          # D-405: a table's declared subset, else the grid
    declared_rents = rent_mode(cfg)
    fixed_point = declared_rents == "fixed_point" and rents is None       # D-329: lambda* per edge
    rents = ([] if fixed_point else (list(declared_rents) if rents is None else list(rents)))
    bands = cfg["export"]
    policies: dict[str, dict] = {}
    base_rows: dict[tuple[float, str], dict] = {}
    rents_by_edge: dict[float, list[float]] = {}
    pid_of = (lambda e, lam: f"state_dp_e{e:+.3f}_lamstar") if fixed_point else (lambda e, lam: f"state_dp_e{e:+.3f}_lam{lam:g}")
    last_star = float((cfg.get("rent_fixed_point") or {}).get("start", 25.0))
    for e in edges:
        solved = []
        if fixed_point:
            t0 = time.time()
            lam, objs, rounds = solve_rent(cfg, rules, float(e), menu, last_star)
            last_star = lam
            solved.append((lam, objs, rounds))
        else:
            for lam in rents:
                solved.append((float(lam), cell(cfg, rules, float(e), float(lam), menu), None))
        rents_by_edge[float(e)] = [lam for lam, _, _ in solved]
        for lam, (f, fsol, ff, c, csol, cf), rounds in solved:
            t0 = time.time()
            dp_row = row_of("dp", e, lam, "dp", rules, fsol, ff, csol, cf)
            dp_row.update(flip_info)
            rows.append(dp_row)
            if rounds is not None:                                        # D-329 / D-331: the fixed point's record
                cash, days, rate = cycle_rate(rules, ff, cf)
                exact = [x for x in rounds if not x["tie_break"]]
                dp_row.update({"rent_mode": "fixed_point", "rent_rate": rate, "rent_rounds": len(exact),
                               "rent_converged_by": rounds[-1].get("converged_by"),
                               "rent_rate_exact": exact[-1]["rate"],           # the exact table's rate at lambda*
                               "rent_rate_best_round": max(x["rate"] for x in exact),
                               "rent_tie_break_price": exact[-1]["rate"] - rate,   # what the display rules cost a slot-day
                               "cycle_cash": cash, "cycle_slot_days": days,
                               "combine_p_abandon": cf.get("p_abandon", 0.0), "xfa_p_abandoned": ff.get("p_abandoned", 0.0)})
                for rr_ in rounds:
                    rows.append({"section": "rent_round", "edge": e, **rr_})
            pid = pid_of(e, lam)
            pol, info = sp.export_policy(pid, c, cf["visitation"], f, ff["visitation"], float(bands["balance_band"]),
                                         float(bands["cushion_band"]), version=export_version,
                                         c_pol0=csol.policy[0], f_pol0=fsol.policy[0],          # D-332
                                         description=export_description(cfg, e, lam, export_version))
            policies[pid] = pol.as_dict()
            dp_row.update({"policy_id": pid, "combine_skip_mass": info["combine_skip_mass"],
                           "funded_skip_mass": info["funded_skip_mass"], "paid_skip_mass": info["paid_skip_mass"],
                           "no_trade_bands": len(info["idle_bands"]), "conduct_flags": "; ".join(pol.conduct_flags())})
            for phase, b, cu, risk, rr, share, ext, source in info["cells"]:
                rows.append({"section": "policy", "edge": e, "slot_rent": lam, "policy_id": pid, "phase": phase,
                             "balance_from": b, "cushion_from": cu, **{f"{k}_from": v for k, v in ext.items()},
                             "risk": risk, "rr": rr, "share": share, "source": source,
                             "no_trade": bool((phase, b, cu, *ext.values()) in info["idle_bands"]) if export_version >= 2 else False})
            print(f"dp e={e:+.3f} lam={lam:.2f}: attempt {csol.value - rules.subscription:+.1f}, p_pass {cf['p_pass']:.3f}, "
                  f"xfa cash {ff['mean_cash']:.0f}, xfa days {ff['mean_days']:.0f} ({time.time() - t0:.0f}s)")
            del f, fsol, c, csol
        del solved
        rents = rents_by_edge[float(e)]                                   # this edge's rents (one, at the fixed point)
        # the fixed legs: one solve per edge (their forward statistics do not depend on the rent), values at each rent
        for b in cfg["baselines"]:
            t0 = time.time()
            T = int(cfg["horizon_days"])
            fm = sp.Menu.fixed(float(b["funded_risk"]), float(b["funded_rr"]), menu.step, rungs=menu.rungs)
            fb = sp.FundedDP(rules, fm, float(e), T, 0.0, balance_cap=float(cfg["funded"]["balance_cap"]),
                             payout_grid_step=float(cfg["funded"]["payout_grid_step"]), payout_choice="max")
            fsol = fb.solve()
            ffb = fb.forward(fsol)
            cb = sp.CombineDP(rules, sp.Menu.fixed(float(b["combine_risk"]), float(b["combine_rr"]), menu.step, rungs=menu.rungs),
                              float(e), T, 0.0, **combine_rules(cfg))
            csol = cb.solve(fsol.fresh_value[1:T + 1] - rules.activation)
            cfb = cb.forward(csol)
            for lam in rents:
                r = row_of("baseline", e, lam, b["name"], rules, fsol, ffb, csol, cfb)
                # a fixed policy's value at a rent: the rent times the expected account-days, both phases
                r["value_xfa_fresh"] = fsol.value - lam * ffb["mean_days"]
                r["value_combine"] = csol.value - lam * (cfb["mean_days"] + cfb["p_pass"] * ffb["mean_days"])
                r["value_attempt"] = r["value_combine"] - rules.subscription
                rows.append(r)
            base_rows[(e, b["name"])] = rows[-1]
            print(f"baseline {b['name']} e={e:+.3f}: attempt {csol.value - rules.subscription:+.1f}, p_pass {cfb['p_pass']:.3f}, "
                  f"xfa cash {ffb['mean_cash']:.0f}, xfa days {ffb['mean_days']:.0f} ({time.time() - t0:.0f}s)")
            del fb, fsol, cb, csol
    if not skip_campaign:
        seed = int(cfg["campaign_check"]["seed"])
        jobs = []
        ref = {}
        if cfg["campaign_check"].get("reference_policies"):        # D-405: v12's table in the same check, beside
            ref = json.loads((rd / Path(cfg["campaign_check"]["reference_policies"]).name).read_text(encoding="utf-8"))
        for e in edges:
            jobs.append((cfg, rules, e, None, "fixed_legs", None, seed, results_dir))
            for lam in rents_by_edge[float(e)]:
                pid = pid_of(e, lam)
                jobs.append((cfg, rules, e, lam, pid, policies[pid], seed, results_dir))
                if ref:
                    if pid not in ref:
                        raise SystemExit(f"REFUSED: the reference policies hold no {pid}.")
                    jobs.append((cfg, rules, e, None, f"reference:{pid}", ref[pid], seed, results_dir))
        t0 = time.time()
        if workers > 1 and len(jobs) > 1:
            from multiprocessing import Pool

            with Pool(min(int(workers), len(jobs))) as pool:
                done = pool.map(_campaign_job, jobs)
        else:
            done = [_campaign_job(j) for j in jobs]
        for r in done:
            rows.append(r)
            print(f"campaign {r['policy_id']} e={r['edge']:+.3f}: growth {r['median_log_growth']:.3f}, "
                  f"ruin {r['ruin_probability']:.3f}, xfa days {r['xfa_mean_days']:.1f}")
        print(f"campaign checks: {len(jobs)} runs in {time.time() - t0:.0f}s")
    # the policies file is hashed before the result is written and written after it: an untracked file of the run's
    # own would otherwise mark the result's manifest dirty (results.git_commit reads the tree first)
    pj = rd / f"{a.result_name}_policies.json"
    payload = json.dumps(policies, indent=1).replace("\r\n", "\n")
    sha = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    all_rents = sorted({lam for e in edges for lam in rents_by_edge[float(e)]})
    rows.append({"section": "summary", "declaration": a.declaration, "export_version": export_version,
                 "edges": ",".join(f"{x:g}" for x in edges),
                 "slot_rents": ("fixed_point: " if fixed_point else "") + ",".join(f"{x:.2f}" for x in all_rents),
                 "cells": sum(len(rents_by_edge[float(e)]) for e in edges),
                 "horizon_days": int(cfg["horizon_days"]), "policies_json_sha256": sha,
                 "rungs": "" if menu.rungs is None else ";".join(f"{rpc:g}:{s:.4f}" for rpc, s in
                                                                 zip(menu.rungs.risk_per_contract, menu.rungs.shares))})
    out = pd.DataFrame(rows)
    write_result(out, a.result_name, script=SCRIPT, seed=int(cfg["campaign_check"]["seed"]), exploratory=True,
                 results_dir=results_dir,
                 notes={"status": "EXPLORATORY: engine-only, stage one's binary outcomes; a declared input to FV3's "
                                  "card, never a verdict (D-290)", "policies_json": pj.name, "policies_json_sha256": sha},
                 parameters={"config": (str(cfg_path.relative_to(ROOT)) if cfg_path.is_relative_to(ROOT) else str(cfg_path)).replace("\\", "/"),
                             "edges": edges, "slot_rents": ("fixed_point" if fixed_point else rents),
                             "rents_by_edge": {f"{e:+.3f}": v for e, v in rents_by_edge.items()},        # D-329
                             "rent_fixed_point": cfg.get("rent_fixed_point"),
                             "abandon": {"combine": abandon_of(cfg, "combine"), "funded": abandon_of(cfg, "funded")},
                             "outcomes": cfg["outcomes"], "menu": cfg["menu"], "funded": cfg["funded"],
                             "horizon_days": cfg["horizon_days"], "baselines": cfg["baselines"], "oracles": cfg["oracles"],
                             "export": cfg["export"], "campaign_check": cfg["campaign_check"],
                             "rules": "rules_for_method(aeropay), placement off (D-289)", "decision": a.declaration,
                             "export_version": export_version, "rungs": cfg.get("rungs"),
                             "combine_rules": combine_rules(cfg), "combine_menu": cfg.get("combine_menu"),
                             "funded_rules": funded_rules(cfg),                       # D-325
                             "rungs_resolved": (None if menu.rungs is None else
                                                {"risk_per_contract": list(menu.rungs.risk_per_contract),
                                                 "shares": list(menu.rungs.shares), "combine_cap": menu.rungs.combine_cap,
                                                 "funded_caps": [list(x) for x in menu.rungs.funded_caps],
                                                 "exit_grid": list(menu.rungs.exit_grid),
                                                 "availability": [[list(p) for p in tab] for tab in menu.rungs.availability]}),
                             "discretisation_note": "the payout request grid starts at the first grid amount at or "
                                                    "above payout_min ($150 on the $50 grid, the rule's $125)"
                                                    + ("; a realised win is rounded to the $50 grid and its probability "
                                                       "read at the R the grid makes of it (fair at zero edge)" if menu.rungs else "")},
                 description="The account-state risk policy by dynamic programming over the contract (D-290): per edge "
                             "and slot rent the Combine and XFA values, pass and payout statistics, the fixed legs "
                             "evaluated alike, the policy projected onto the engine's tree, and the lockstep campaign "
                             "check against the fixed legs."
                             + (" Export version 3 (D-306): solved with the contract allowance built in -- every risk "
                                "realised as whole micros at each rung's fixed stop, capped by the leg's allowance, "
                                "mixed by the rungs' shares in today's regime -- and need-aware Combine exits."
                                if export_version >= 3 else "")
                             + (" Export version 6 (D-318): each rung's availability -- an action trades at a rung only "
                                "on the share of its trades whose room permits the action's R; otherwise no trade that day."
                                if export_version >= 6 else "")
                             + (" Export version 8 (D-325): the funded table solved under the operator's two rules -- "
                                "among actions within the declared dollars of the state's best value the smallest risk "
                                "(no trade the smallest), and once the balance is above its start no action beyond the "
                                "declared risk cap; the Combine untouched."
                                if export_version >= 8 else "")
                             + (" Export version 11 (D-332): every band the state space contains is exported, the "
                                "table's own day-0 decision standing where its chain never visited, so the engine "
                                "never inherits a neighbouring band's choice."
                                if export_version >= 11 else "")
                             + (" Export version 12 (D-333): the funded balance cap's band is left out -- a modelling "
                                "boundary at which the table abandons and the engine has no cap -- so the engine reads "
                                "the band below it."
                                if export_version >= 12 else "")
                             + (" Export version 13 (D-339): the funded menu carries the flip stream's action -- a "
                                "scheduled bracket at its own measured net edge, offered every day, the two-stream "
                                "candidate's winning-day trade -- and every leaf names its source (strategy or flip); "
                                "the flip's statistics and their file are on the dp rows."
                                if export_version in FLIP_VERSIONS and export_version >= 13 else "")
                             + (" Export version 14 (D-341): the funded table's tie-break prefers the flip at equal risk "
                                "within the tolerance (v13 let the better value decide between the flip and the "
                                "strategy's trade of the same risk, a few dollars either way band by band)."
                                if export_version in FLIP_VERSIONS and export_version >= 14 else "")
                             + (" Export version 15 (D-345): the flip is the fast, time-boxed bracket the flip map chose "
                                "(one NQ mini at the slot and width of its `choice` row), its scratch share a day without a "
                                "trade and the resolving attempts at the edge that keeps the attempt's value the row's; "
                                "copied across the flip-state accounts in the engine."
                                if export_version in FLIP_VERSIONS and export_version >= 15 else "")
                             + (" Export version 16 (D-346): the flip's contract is the operator's rule -- the fewest micros whose "
                                "risk sits on the table's grid and whose win after fees clears the winning-day bar (five MNQ at 20 "
                                "points, $200) -- the map re-scored at that count; the width, slot and shares are v15's."
                                if export_version in FLIP_VERSIONS and export_version >= 16 else "")
                             + (" Export version 17 (D-379): v12's table with the funded menu's collect action -- at each "
                                "declared risk a routed signal with a take-profit at the winning-day minimum, a win "
                                "adding exactly the minimum, its chance read at the smallest exit-grid R its realised "
                                "size needs (the engine's stretch walk); exported as collect leaves."
                                if export_version == 17 else "")
                             + (" Export version 18 (D-384): v12's table with the collect menu -- the collect map's five "
                                "brackets (08:30 CT, five MNQ, a $200 target under stops of 1 to 4 times it), each a funded "
                                "action at its net edge and scratch share over 2020-2021, offered every session, the bracket "
                                "before the strategy's trade at equal risk; exported as flip leaves naming each bracket's "
                                "risk and R."
                                if export_version == 18 else "")
                             + (f" Export version {export_version} (D-405, FV3-S): v12's table to the line, each day's "
                                "outcomes valued at their certainty equivalent under exponential utility (a fair coin to win "
                                f"or lose ${float(cfg['objective']['coin_stake']):,.0f} worth "
                                f"-${float(cfg['objective']['coin_loss']):,.0f}), both legs; the rent per edge the largest at "
                                "which a fresh attempt is still worth at least zero in that objective (bisection on the exact "
                                "tables); the campaign check carries the steadiness measures and v12's table beside."
                                if export_version in CE_VERSIONS else "")
                             + (" Export version 9 (D-326): the unpaid funded balance band split at the start, so the "
                                "cap's exemption of the start does not reach the first in-profit states."
                                if export_version >= 9 else "")
                             + (" Export version 10 (D-329): the slot rent derived per edge as the cash rate per "
                                "slot-day (the fixed point over the Combine -> XFA chain; the rent_round rows), an "
                                "abandon action in both tables (worth 0: a Combine cancelled, an XFA closed, the slot "
                                "freed) and the Combine's tie-break toward the higher R."
                                if export_version >= 10 else ""))
    pj.write_text(payload, encoding="utf-8", newline="\n")
    if record:
        counter = VariantCounter()                              # D-290: every (edge, rent) cell is one study
        for e in edges:
            for lam in rents_by_edge[float(e)]:
                # D-334 (the audit of D-333, finding 6): the export version is in the id, so two exports of one solve
                # (D-332's v11 and D-333's v12 of the v10 solve wrote the same ids) are told apart in the ledger
                counter.record(prereg_id=f"{DECLARATION}:state_policy", seed=int(cfg["campaign_check"]["seed"]),
                               exploratory=True, params={"study": "state policy DP", "edge": float(e), "slot_rent": float(lam),
                                                         "export_version": int(export_version), "declaration": a.declaration,
                                                         **({"coin_loss": float(cfg["objective"]["coin_loss"])}   # D-405
                                                            if export_version in CE_VERSIONS else {})},
                               label=f"The account-state policy DP at edge {e:+.3f}, slot rent ${lam:g}/day (D-290; "
                                     f"export {export_version}, {a.declaration})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
