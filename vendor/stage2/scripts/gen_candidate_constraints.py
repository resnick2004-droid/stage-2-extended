"""Generate config/candidate_constraints.yaml from the repository's own sources.

This file is the **interface the literature repository reads**: the machine-readable constraints a
candidate must satisfy before it is worth proposing. Every value is derived from a verified rule, a
config file, or a result file with a manifest -- nothing here is typed by hand, which is the same
rule that governs documents (`CLAUDE.md`).

It is regenerated rather than edited. `tests/test_candidate_constraints.py` regenerates it into a
temporary file and compares, so it cannot drift from its sources: change a rule or rerun an
analysis, and the test fails until this is regenerated.

Run: python scripts/gen_candidate_constraints.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from propedge.backtest.metrics import (  # noqa: E402
    CRITERION_EDGE_MIN,
    CRITERION_LOWER_BOUND_MIN,
)
from propedge.contract.rules import load_rules  # noqa: E402

OUT = ROOT / "config" / "candidate_constraints.yaml"
RESULTS = ROOT / "results"

HEADER = """\
# config/candidate_constraints.yaml
#
# GENERATED -- do not edit. Run `python scripts/gen_candidate_constraints.py`.
# tests/test_candidate_constraints.py fails if this drifts from its sources.
#
# The machine-readable constraints a candidate strategy must satisfy. This is the interface the
# literature repository reads: a candidate that violates any `hard` constraint is not a candidate,
# and one that sits outside the `feasible` region cannot be demonstrated with the data available,
# however good it is.
#
# Every value cites its source: a DECISIONS.md entry, a config key, or a result file with a
# sidecar manifest.
"""


def build() -> dict:
    ledger = load_rules()
    instruments = yaml.safe_load(
        (ROOT / "config" / "instruments.yaml").read_text(encoding="utf-8")
    )
    fills = yaml.safe_load((ROOT / "config" / "fills.yaml").read_text(encoding="utf-8"))

    drag = pd.read_csv(RESULTS / "cost_drag_sensitivity.csv")
    frontier = pd.read_csv(RESULTS / "feasibility_frontier.csv")
    multi = pd.read_csv(RESULTS / "multimarket_frontier.csv")
    spy = pd.read_csv(RESULTS / "spy_proxy_design.csv")
    tex = pd.read_csv(RESULTS / "time_exit_frontier.csv")
    siz = pd.read_csv(RESULTS / "multimarket_sizing.csv")
    legs = pd.read_csv(RESULTS / "leg_schedule.csv")
    port = pd.read_csv(RESULTS / "portfolio_frontier.csv")
    alloc = pd.read_csv(RESULTS / "account_allocation.csv")
    dc = pd.read_csv(RESULTS / "design_c_partitioned.csv")
    slots = pd.read_csv(RESULTS / "slot_supply.csv")
    five = pd.read_csv(RESULTS / "five_account_layouts.csv")
    wide = pd.read_csv(RESULTS / "wide_stop_admissibility.csv")
    lev = pd.read_csv(RESULTS / "cost_share_and_risk_levers.csv")
    veh = pd.read_csv(RESULTS / "vehicle_choice.csv")
    era = pd.read_csv(RESULTS / "era_and_vehicle.csv")

    def params(name: str) -> dict:
        """Read a result's manifest, so window lengths are cited rather than restated."""
        man = json.loads((RESULTS / f"{name}.csv.manifest.json").read_text(encoding="utf-8"))
        return man["parameters"]

    fp, mp, sp = params("feasibility_frontier"), params("multimarket_frontier"), params(
        "spy_proxy_design")
    tp = params("time_exit_frontier")
    zp = params("multimarket_sizing")
    lp = params("leg_schedule")
    pf = params("portfolio_frontier")
    ap = params("account_allocation")
    dp = params("design_c_partitioned")
    sp2 = params("slot_supply")
    wp = params("wide_stop_admissibility")
    lvp = params("cost_share_and_risk_levers")
    vhp = params("vehicle_choice")
    erp = params("era_and_vehicle")

    # --- entry-tier sizing: which pooled sets a fresh funded account can actually express
    sz1 = siz[siz.slippage_ticks_round_trip == 1.0]
    sets_ok, sets_no = [], []
    for name, g in sz1.groupby("pooled_set", sort=False):
        spread = float(g.expressible_risk.max() / max(g.expressible_risk.min(), 1e-9))
        entry = {
            "set": str(name),
            "k_markets": int(g.k_markets.iloc[0]),
            "allocation": {str(r.market): int(r.contracts_at_entry_tier) for r in g.itertuples()},
            "vehicles": {str(r.market): str(r.vehicle) for r in g.itertuples()},
            "micro_equivalents_for_one_each": int(g.set_min_micro_equivalents.iloc[0]),
            "total_expressible_risk_usd": round(float(g.expressible_risk.sum()), 2),
            "risk_spread_max_over_min": round(spread, 2),
        }
        (sets_ok if bool(g.expressible_on_fresh_account.iloc[0]) else sets_no).append(entry)
    per_market_vehicle = {
        str(r.market): {
            "vehicle": str(r.vehicle),
            "tick_value": float(r.tick_value),
            "round_turn_cost": float(r.round_turn_cost),
            "micro_equivalents_per_contract": int(r.micro_equivalents_per_contract),
            "has_micro_on_same_underlying": bool(r.has_micro_on_same_underlying),
            "cost_floor_stop_ticks_at_1_tick_slippage": int(r.cost_floor_stop_ticks),
            "risk_per_contract_usd": round(float(r.risk_per_contract), 2),
        }
        for r in sz1.drop_duplicates("market").itertuples()
    }

    # --- three-way layout comparison at the plausibility-ceiling Sharpe
    d1 = dc[(dc.component_sharpe == 1.0) & (dc.accounts == 4)]
    three_way = []
    for rho, g in d1.groupby("rho"):
        row = {"rho": float(rho)}
        for r in g.itertuples():
            tag = r.layout[0] + str(int(r.strategies_per_account))
            row[tag] = {
                "cross_account_corr": float(r.cross_account_corr),
                "pass": float(r.pass_rate),
                "at_least_one_passes": float(r.at_least_one_passes),
                "years_to_resolve": round(float(r.mean_days_to_resolve) / 252.0, 2),
                "same_day_multi_mll": float(r.multi_mll_same_day),
                "hedging_exposure": str(r.hedging_exposure),
            }
        three_way.append(row)

    # --- slot supply and which layouts it makes staffable
    staff = {}
    for regime, g in slots.groupby("regime"):
        staff[str(regime)] = {
            "groups": int(g.groups.iloc[0]),
            "windows_per_group": int(g.windows_per_group.iloc[0]),
            "slots_available": int(g.slots_available.iloc[0]),
            "staffable_layouts": [
                f"N={int(r.accounts)}/m={int(r.strategies_per_account)}"
                for r in g[g.staffable].itertuples()
            ],
        }

    # --- item 2: permitted instruments with verification status, driven from config
    ci = instruments["candidate_instruments"]
    ag = instruments["additional_candidate_groups"]
    perm = {}
    for mini, micro in (("ES", "MES"), ("NQ", "MNQ")):
        for v in (mini, micro):
            perm[v] = {
                "tick_value": float(instruments["instruments"][v]["tick_value"]),
                "spec_status": "verified",
                "spec_source": str(instruments["instruments"][v]["source"]),
                "modelled": True,
            }
    for v in ("GC", "MGC", "CL", "MCL", "6E", "M6E", "ZN"):
        b = ci[v]
        perm[v] = {
            "tick_value": b.get("tick_value"),
            "spec_status": str(b.get("spec_status")),
            "spec_source": str(b.get("spec_source", "")).strip(),
            "modelled": b.get("tick_value") is not None,
        }
    for name, b in ag.items():
        if name in ("merged_or_rejected", "open_question_asterisk"):
            continue
        for kind in ("standard", "micro"):
            sym = b.get(kind)
            if not sym:
                continue
            perm[str(sym)] = {
                "tick_value": b.get(f"{kind}_tick_value"),
                "spec_status": str(b.get("spec_status", "verified")),
                "spec_source": str(b.get("spec_source", "")).strip(),
                "modelled": False,
            }

    # --- item 4: cost-share thresholds and the C-007 minimum effect
    cs = lev[(lev.block == "cost_share") & (lev.slippage_ticks_round_trip == 1.0)]
    cost_share = {
        str(r.vehicle): {
            "round_trip_cost_usd": float(r.round_trip_cost),
            "breakeven_effect_ticks": int(r.breakeven_effect_ticks),
            "effect_ticks_for_share_below_5pct": int(r.effect_ticks_for_share_5pct),
            "effect_ticks_for_share_below_2pct": int(r.effect_ticks_for_share_2pct),
            "effect_ticks_for_share_below_1pct": int(r.effect_ticks_for_share_1pct),
            "effect_usd_for_share_below_5pct": float(r.effect_usd_for_share_5pct),
        }
        for r in cs.itertuples()
    }
    cbe = lev[lev.block == "cost_share_by_effect"]
    cost_by_effect = {
        str(leg): {int(r.effect_ticks): {"effect_usd": float(r.effect_usd),
                                         "cost_share": float(r.cost_share),
                                         "covers_costs": bool(r.covers_costs)}
                   for r in g.itertuples()}
        for leg, g in cbe.groupby("leg")
    }
    c007 = [
        {"leg": str(r.leg), "vehicle": str(r.vehicle), "window_ct": str(r.window_ct),
         "breakeven_ticks": int(r.breakeven_ticks),
         "effect_ticks_for_5pct": int(r.ticks_for_5pct),
         "effect_ticks_for_2pct": int(r.ticks_for_2pct),
         "effect_ticks_for_1pct": int(r.ticks_for_1pct),
         "usd_for_5pct": float(r.usd_for_5pct)}
        for r in lev[lev.block == "c007_legs"].itertuples()
    ]

    # --- D-74: paired micro/mini cost share and the switching points
    vp = veh[(veh.block == "paired_cost_share") & (veh.slippage_ticks_round_trip == 1.0)]
    paired = {}
    for leg, g2 in vp.groupby("leg"):
        paired[str(leg)] = {
            str(r.kind): {
                "vehicle": str(r.vehicle),
                "cost_per_contract": float(r.cost_per_contract),
                "breakeven_micro_ticks": float(r.breakeven_micro_ticks),
                "cost_share_at_3_micro_ticks": float(r.cost_share_at_3t),
                "cost_share_at_10_micro_ticks": float(r.cost_share_at_10t),
            }
            for r in g2.itertuples()
        }
        mi = g2[g2.kind == "micro"].iloc[0]
        ma = g2[g2.kind == "mini"].iloc[0]
        paired[str(leg)]["mini_cheaper_by"] = round(
            float(mi.cost_share_at_10t / ma.cost_share_at_10t), 2)
    v0 = veh[(veh.block == "paired_cost_share") & (veh.slippage_ticks_round_trip == 0.0)]
    adv_no_slip = {}
    for leg, g2 in v0.groupby("leg"):
        mi = g2[g2.kind == "micro"].iloc[0]
        ma = g2[g2.kind == "mini"].iloc[0]
        adv_no_slip[str(leg)] = round(float(mi.cost_share_at_10t / ma.cost_share_at_10t), 2)
    sw = veh[veh.block == "switching"]
    switching = {}
    for stop, g2 in sw.groupby("stop_micro_ticks"):
        by_leg = {}
        for leg, g3 in g2.groupby("leg"):
            ok = g3[g3.can_use_mini.astype(bool)]
            by_leg[str(leg)] = (float(ok.daily_risk_fraction.min()) if not ok.empty else None)
        switching[int(stop)] = by_leg
    mini_budget = {
        int(stop): {str(r.leg): float(r.one_mini_risk) for r in g2.itertuples()}
        for stop, g2 in veh[veh.block == "mini_budget"].groupby("stop_micro_ticks")
    }

    # --- era dependence, vehicle by era, mixed designs (D-75)
    ecost = era[(era.block == "cost_by_price") & (era.effect_bp == 5.0)
                & (era.kind == "micro")]
    era_ratio = {}
    for leg, g2 in ecost.groupby("leg"):
        lo = g2[g2.price_level == "low"].cost_share.iloc[0]
        hi = g2[g2.price_level == "high"].cost_share.iloc[0]
        era_ratio[str(leg)] = {
            "cost_share_at_low_price": float(lo),
            "cost_share_at_high_price": float(hi),
            "low_over_high": round(float(lo / hi), 2),
        }
    esw = era[era.block == "vehicle_by_era"]
    vehicle_era = {}
    for (leg, bp), g2 in esw.groupby(["leg", "stop_bp"]):
        vehicle_era.setdefault(str(leg), {})[f"{int(bp)}bp"] = {
            str(r.price_level): (float(r.switch_fraction)
                                 if pd.notna(r.switch_fraction) else None)
            for r in g2.itertuples()
        }
    mixed = [
        {"design": str(r.design), "legs": int(r.legs),
         "daily_risk_usd": float(r.daily_risk_usd),
         "fraction_of_cushion": float(r.fraction_of_cushion),
         "mean_cost_share": float(r.mean_cost_share),
         "required_pooled_sharpe": float(r.required_pooled_sharpe)}
        for r in era[era.block == "mixed_designs"].itertuples()
    ]

    # --- item 5: the risk lever
    rl = lev[lev.block == "risk_lever"]
    risk_lever = {}
    for e, g in rl.groupby("edge"):
        best = g.loc[g.log_growth_per_day_barrier_free.idxmax()]
        risk_lever[float(e)] = {
            "kelly_fraction_barrier_free": float(g.kelly_fraction.iloc[0]),
            "kelly_usd_barrier_free": round(float(g.kelly_fraction.iloc[0]) * wp["cushion"], 0),
            "best_fraction_on_tested_grid": float(best.daily_risk_fraction),
            "prob_floor_before_target_at_that_fraction": float(best.prob_floor_before_target),
            "prob_floor_before_target_at_default_eighth": float(
                g[g.daily_risk_fraction == 0.125].prob_floor_before_target.iloc[0]),
        }

    # --- corrected stop band: cost floor and the narrowest stop reaching the cushion
    w1 = wide[wide.slippage_ticks_round_trip == 1.0]
    band = {}
    for veh, g in w1.groupby("vehicle"):
        ok = g[g.drag_within_criterion]
        entry = g[g.tier_minis == g.tier_minis.min()]
        reach = entry[entry.reaches_full_cushion]
        band[str(veh)] = {
            "tick_value": float(g.tick_value.iloc[0]),
            "cost_floor_stop_ticks": int(ok.stop_ticks.min()) if not ok.empty else None,
            "narrowest_stop_reaching_cushion_at_entry_tier": (
                int(reach.stop_ticks.min()) if not reach.empty else None),
            "max_stop_at_1_contract_under_daily_limit": int(
                wp["daily_limit"] / float(g.tick_value.iloc[0])),
            "drag_at_10_ticks": float(g[g.stop_ticks == 10].cost_drag.iloc[0]),
            "drag_at_200_ticks": float(g[g.stop_ticks == 200].cost_drag.iloc[0]),
        }

    # --- five-account layout choice, read from the result file rather than restated
    five_by_rho = {
        str(c): {float(r.rho): float(r.expected_funded_accounts) for r in g.itertuples()}
        for c, g in five.groupby("candidate")
    }
    _fb = five[five.is_best_at_this_rho.astype(bool)].candidate.value_counts()
    five_best = str(_fb.index[0])
    if len(_fb) > 1:
        raise SystemExit(
            "no single layout is best at every rho: " + ", ".join(_fb.index)
            + " -- the recommendation in D-63 assumed one was, and must be revisited."
        )

    # --- portfolio: required component Sharpe by k and rho
    p1 = port[port.cluster_factor == 1.0]
    port_req = {
        int(k): {
            float(r.rho): {
                "required_component_sharpe": float(r.required_component_sharpe),
                "plausible": bool(r.plausible),
                "if_each_component_claimed_alone": float(
                    r.required_sharpe_if_each_claimed_alone),
                "decomposition_cost_multiple": float(r.pooling_advantage_ratio),
            }
            for r in g.itertuples()
        }
        for k, g in p1.groupby("k_strategies")
    }

    # --- allocation: the two summary facts, at the plausibility-ceiling Sharpe
    a1 = alloc[alloc.component_sharpe == 1.0]
    alloc_rows = []
    for (k, rho), g in a1.groupby(["k_strategies", "rho"]):
        a = g[g.allocation.str.startswith("A")].iloc[0]
        b = g[g.allocation.str.startswith("B")].iloc[0]
        alloc_rows.append({
            "k_strategies": int(k), "rho": float(rho), "accounts": int(a.accounts),
            "A_pass": float(a.combine_pass_probability),
            "B_pass": float(b.combine_pass_probability),
            "A_over_B_pass": round(float(a.combine_pass_probability
                                          / b.combine_pass_probability), 3),
            "A_campaign_survival": float(a.prob_at_least_one_passes),
            "B_campaign_survival": float(b.prob_at_least_one_passes),
            "A_years_to_resolve": float(a.expected_years_to_resolve),
            "B_years_to_resolve": float(b.expected_years_to_resolve),
        })

    # --- viable stop range: where gross edge needed to net 0.10 is <= 0.20, i.e. drag <= 0.10
    real = drag[drag.commission_basis == "per_instrument_verified"]
    if real.empty:
        raise SystemExit(
            "results/cost_drag_sensitivity.csv has no 'per_instrument_verified' rows. Rerun "
            "analysis/drag.py -- the flat-commission panel is superseded and must not be used."
        )
    viable = real[real.gross_edge_needed <= 0.20]
    by_symbol = {}
    for sym, d in viable.groupby("symbol"):
        at1 = d[d.slippage_ticks_round_trip == 1.0]
        by_symbol[str(sym)] = {
            "min_stop_ticks_any_slippage": int(d.stop_ticks.min()),
            "min_stop_ticks_at_1_tick_slippage": (
                int(at1.stop_ticks.min()) if not at1.empty else None
            ),
            "viable": not at1.empty,
        }

    # --- single-market frontier: smallest demonstrable edge per R at cluster factor 1
    single = {}
    for R, d in frontier[frontier.cluster_factor == 1.0].groupby("R"):
        ok = d[d.fits_data_window]
        single[float(R)] = {
            "smallest_demonstrable_edge": float(ok.edge.min()) if not ok.empty else None,
            "years_needed": float(ok[ok.edge == ok.edge.min()].total_years_needed.iloc[0])
            if not ok.empty
            else None,
        }
    lost = frontier[frontier.lost_to_data_window]
    lost_cells = [
        {"edge": float(r.edge), "R": float(r.R), "cluster_factor": float(r.cluster_factor),
         "years_needed": float(r.total_years_needed)}
        for r in lost.itertuples()
    ]

    # cheapest e = 0.10 cell at one trade a day, for the frequency trade-off below
    cheapest_010 = float(
        frontier[(frontier.edge == 0.10) & (frontier.cluster_factor == 1.0)]
        .total_years_needed.min()
    )

    # --- time-exit: minimum implied Sharpe to fit the post-2018 window, by k and rho
    te_single = tex[(tex.k_markets == 1) & (tex.cluster_factor == 1.0)]
    # Analytic, not read off the grid: S_needed(k, rho) = S_1 * sqrt([1+(k-1)rho]/k). Taking the
    # smallest FITTING cell's Sharpe instead would make this depend on which (e, sd) pairs the
    # grid happens to sample, which is not a property of the problem.
    s1 = tp["min_sharpe_single_market"]
    te_min_sharpe = {
        int(k): {
            float(rho): round(float(s1 * ((1.0 + (int(k) - 1) * float(rho)) / int(k)) ** 0.5), 3)
            for rho in sorted(tex.rho.unique())
        }
        for k in sorted(tex.k_markets.unique())
    }
    te_max_sd = {}
    for e, d in te_single.groupby("edge"):
        ok = d[d.fits_2014_window]
        te_max_sd[float(e)] = float(ok.sd.max()) if not ok.empty else None
    te_any_plausible = bool(
        (te_single.fits_2014_window & te_single.sharpe_is_plausible).any()
    )

    # --- SPY-development / ES-confirmation proxy
    spy_recovered = [
        {"edge": float(r.edge), "R": float(r.R), "cluster_factor": float(r.cluster_factor),
         "confirmation_years_needed": float(r.confirmation_years_needed)}
        for r in spy[spy.recovered_by_spy].itertuples()
    ]

    # --- multi-market: markets needed to reach e = 0.10, by correlation
    pooled = {}
    for R, d in multi[multi.edge == 0.10].groupby("R"):
        by_rho = {}
        for rho, dd in d.groupby("rho"):
            ok = dd[dd.fits_pooled_window]
            by_rho[float(rho)] = int(ok.k_markets.min()) if not ok.empty else None
        pooled[float(R)] = by_rho

    ticks = {
        s: {"tick_size": b["tick_size"], "tick_value": b["tick_value"],
            "source": b["source"]}
        for s, b in instruments["instruments"].items()
    }

    return {
        "generated_by": "scripts/gen_candidate_constraints.py",
        "generated_for": "the literature repository: the constraints a candidate must satisfy",

        "permitted_instruments": {
            "rule": "the CME Group product set, with permitted hours",
            "source": "config/rules.yaml:permitted_products (help.topstep.com 8284206, read "
                      "2026-09-23)",
            "by_symbol": perm,
            "excluded": ["spot FX (the FUTURES contract 6E is permitted; spot is not)",
                         "swing trading (no overnight positions)"],
            "no_micro_exists": ["ZN"],
            "note": (
                "spec_status is carried PER SYMBOL here rather than in a prose note, because a "
                "note goes stale and a field regenerates (D-68). ZN, CL, GC and 6E were verified "
                "from cmegroup.com in D-47; the crypto micros are permitted but their specs are "
                "NOT read. An unverified spec cannot be sized or costed."
            ),
            "open_question": (
                "8284206 says 'See Prohibited Conduct for restrictions on specific products "
                "marked with an asterisk' and the asterisk is carried by the MICRO versions, but "
                "neither 10296582 nor 10305426 states any such restriction. The pointer is "
                "dangling and the sizing plan rests on micros. On the support list (D-62)."
            ),
        },

        "session": {
            "timezone": "America/Chicago",
            "flatten_ct": "15:10",
            "resume_ct": "17:00",
            "day_lock_ct": "16:00",
            "source": "config/instruments.yaml meta; help.topstep.com 8284206",
            "note": (
                "A trade open at the flatten is closed at market and its ACTUAL P&L recorded -- "
                "never assumed binary. No position may be held overnight."
            ),
        },

        "position_size": {
            "combine_max_minis": ledger.value("combine_position_size_limit"),
            "micro_ratio": 10,
            "micro_ratio_status": "VERIFIED (D-52)",
            "micro_ratio_source": (
                "article 8284223 defines the allowance on the page that sets it -- "
                "'2 Minis, OR 20 Micros, OR Any combo equal to 2 Minis' -- corroborated by "
                "the trader's first-hand platform check on 2026-09-23. Two independent "
                "readings of different kinds, which is the D-35 standard."
            ),
            "micro_ratio_superseded_claim": (
                "topstep.com/blog/new-permitted-products-offered-at-topstep (2026-01-14) "
                "says each micro equals a full contract. SUPERSEDED, not merely outweighed. "
                "It is kept on record because it is still published and a reader finding it "
                "without this note would conclude the opposite. NOT a live dispute."
            ),
            "funded_entry_tier_minis": ledger.value("funded_scaling_entry_tier_minis"),
            "funded_scaling_ladder": ledger.value("funded_scaling_plan"),
            "ladder_units": "balance_usd_threshold:minis",
            "tier_driver": "current account balance",
            "tier_resets_on_payout": ledger.value("scaling_tier_after_payout"),
            "source": "config/rules.yaml; DECISIONS.md D-23, D-32",
            "note": (
                "The FUNDED account binds, not the Combine: a funded account opens at 2 minis "
                "while the Combine allows 5 from the first trade. The allowance is a STATE "
                "VARIABLE moved by the strategy's own P&L, and a payout resets it (D-32)."
            ),
        },

        "costs_and_stops": {
            "round_turn_by_instrument": fills["round_turn_by_instrument"]["values"],
            "round_turn_source": fills["round_turn_by_instrument"]["source"],
            "tick_values": ticks,
            "viable_stop_range_ticks": by_symbol,
            "rule": (
                "cost drag = (round turn + round-trip slippage x tick value) / "
                "(stop_ticks x tick value); it depends on STOP WIDTH, not on bet size"
            ),
            "source": "results/cost_drag_sensitivity.csv; DECISIONS.md D-03, D-33",
            "note": (
                "Below ~30 ticks nothing is viable at realistic slippage. Slippage in "
                "config/fills.yaml is an UNMEASURED assumption and is the largest single driver "
                "of viability."
            ),
            "stop_width_band": {
                "rule": (
                    "Stop width has a COST FLOOR and a POLICY CEILING; the admissible band lies "
                    "between. Drag FALLS as the stop widens, so the narrow end was always the "
                    "binding end."
                ),
                "per_vehicle": band,
                "ceiling_is_policy_not_arithmetic": (
                    "Nothing in the contract stops the entry tier expressing the full $2,000 "
                    "cushion -- 2 ES minis at 80 ticks or 2 NQ minis at 200 reach it exactly. "
                    "What stops it is the daily-risk limit (D-50, provisional under D-54) and "
                    "the guardrail that no single position decides the account. An arithmetic "
                    "limit is a fact to design around; a policy limit is a choice to optimise. "
                    "Conflating them makes a choice look like a constraint (D-65)."
                ),
                "withdrawn_claims": (
                    "Two statements drawn from a 10-30 tick grid and stated as facts about the "
                    "contract are WITHDRAWN (D-64): that a day-one all-in risking the full "
                    "$2,000 cushion is arithmetically impossible, and that a fresh funded "
                    "account caps risk at roughly $250-$750. $750 is exactly 20 MES at 30 ticks "
                    "-- the largest cell in that grid, not a cap."
                ),
                "source": "results/wide_stop_admissibility.csv; DECISIONS.md D-64, D-65",
            },
        },

        "criterion": {
            "edge_min": CRITERION_EDGE_MIN,
            "one_sided_lower_bound_min": CRITERION_LOWER_BOUND_MIN,
            "net_of_costs": True,
            "out_of_sample": True,
            "source": "CHARTER.md; propsim D-47; propedge.backtest.metrics",
            "applies_to_every_trade_shape": True,
            "time_exit_restatement": (
                "REFUSED (D-104, answering 2B R-02). The criterion is a settled stage-one input "
                "(propsim D-47) and applies unchanged to the time-exit shape at the fixed 2.0 "
                "multiplier. It is not restated per shape or in Sharpe terms. A restatement "
                "made after the measured sds showed the candidates failing it would move the "
                "bar to fit them. That the criterion implies a Sharpe above the plausibility "
                "ceiling for this shape is recorded as a finding, not a defect to be repaired."
            ),
            "decision": "DECISIONS.md D-104 (operator, 2026-09-24)",
        },

        "trade_shape": {
            "why_this_key_exists": (
                "Feasibility depends on the SHAPE of the trade, not only on its edge. A bracket "
                "trade resolves at a stop or a target, so its per-trade sd is pinned by geometry. "
                "A time-exit trade's is not and must be measured. Screening a candidate against "
                "the wrong section gives a wrong answer with no sign that anything is amiss -- "
                "which is why the sections name their shape instead of leaving it implied (D-45)."
            ),
            "shapes_covered": ["bracket", "time_exit"],
            "bracket": "feasibility.* -- stop and target both pre-placed; sd from geometry",
            "time_exit": "time_exit.* -- exit on a clock; stop rarely hit; sd is empirical",
        },

        "feasibility": {
            "applies_to_trade_shape": "bracket",
            "design": "development + held-out confirmation; one test at z = 1.645 (D-13)",
            "sd_assumption": "1.5 x binary floor (1+R)sqrt(p(1-p)) -- AN ASSUMPTION, not measured",
            "data_window": {
                "source": fp["data_source"],
                "url": fp["data_source_url"],
                "read": fp["data_source_read"],
                "starts": "May 2009",
                "years": fp["data_window_years"],
                "note": (
                    "THE BINDING CONSTRAINT. Span is not how long a contract has existed, it is "
                    "how much history can be obtained. ES has traded liquidly since ~2000 "
                    f"({fp['contract_history_years_for_comparison']} y) but the data starts May "
                    "2009, so the usable single-market window is "
                    f"{fp['data_window_years']} y. Change the data source and this section "
                    "changes: it is a vendor fact, not a constant of the problem. See D-39."
                ),
                "licence": (
                    "Free inside QuantConnect Cloud for backtesting; a local download needs a "
                    "paid licence, so raw bars stay in their cloud. What crosses into this "
                    "repository is a trade log, not a price series (docs/PIPELINE.md)."
                ),
            },
            "single_market_smallest_demonstrable_edge_by_R": single,
            "single_market_obtainable_years": {
                k: v["obtainable_years"] for k, v in fp["spans"].items()
            },
            "cells_lost_to_the_data_window": lost_cells,
            "frequency_tradeoff": {
                "rule": "years scale as cluster_factor / trades_per_day",
                "cheapest_cell_years_at_1_trade_per_day": cheapest_010,
                "max_cluster_factor_for_edge_0.10_at_2_trades_per_day": round(
                    fp["data_window_years"] / cheapest_010 * 2, 2
                ),
                "note": (
                    "More trades per day buys nothing if they are perfectly correlated within "
                    f"the day. The cheapest e = 0.10 cell needs {cheapest_010} y at one trade a "
                    "day (R = 1.5). Two trades a day bring that inside the "
                    f"{fp['data_window_years']} y window ONLY while the cluster factor stays "
                    f"below {round(fp['data_window_years'] / cheapest_010 * 2, 2)} -- i.e. while "
                    "the second trade is genuinely close to independent of the first. Two "
                    "perfectly correlated trades a day (cluster factor 2) buy nothing at all."
                ),
            },
            "multi_market": {
                "design_effect": "1 + (k-1) * rho",
                "pooled_window_years": mp["pooled_window_years"],
                "pooled_window_basis": mp["pooled_window_basis"],
                "pooled_window_note": (
                    "The pooled window used to be the SHORTEST contract history in the pool "
                    f"({mp['contract_pooled_window_years_for_comparison']} y, from the 2006/07 "
                    "Globex migrations), so every market added shortened it. The data start is "
                    "the SAME for every contract AlgoSeek covers, so adding a market no longer "
                    "costs span -- only correlation. Pooling is cheaper under this source, not "
                    "dearer. See D-39."
                ),
                "markets_needed_for_edge_0.10_by_R_and_rho": pooled,
                "rho_is_an_assumption": True,
                "pooling_assumes_a_common_edge": (
                    "Pooling assumes the SAME edge in every market. If it differs, the pooled "
                    "mean estimates an average that may exist in no market. A pre-registration "
                    "must TEST homogeneity, not assume it."
                ),
            },
            "spy_then_es_proxy": {
                "design": (
                    "develop on SPY 1998-2009.4 (AlgoSeek US Equities), confirm on ES "
                    "2009.4-today (AlgoSeek US Futures)"
                ),
                "confirmation_years_pure_futures": sp["confirmation_cap_pure_futures"],
                "confirmation_years_with_spy": sp["confirmation_cap_spy_then_es"],
                "cells_recovered": spy_recovered,
                "reopens_edge_0.10_single_market": False,
                "assumption": (
                    "SPY and ES track the same index but are not the same instrument: different "
                    "trading hours, costs, contract size, dividend and financing treatment, "
                    "microstructure and participant mix. The gain is CONDITIONAL on the proxy "
                    "holding."
                ),
                "must_be_tested_not_assumed": (
                    "A pre-registration using this design must declare the proxy as a hypothesis "
                    "with its own pass/fail check, run on the post-May-2009 OVERLAP where both "
                    "series exist, declared before the confirmation test. The overlap is part of "
                    "the confirmation window, so the proxy check spends confirmation data and "
                    "must be counted in k."
                ),
                "if_the_proxy_fails": (
                    "The development period was spent on a different problem, so the "
                    "confirmation test becomes the FIRST look at the strategy on its actual "
                    "instrument. That is a WEAKER design than the pure-futures split, not a "
                    "stronger one."
                ),
                "source": "results/spy_proxy_design.csv; DECISIONS.md D-40",
            },
            "source": ("results/feasibility_frontier.csv, results/multimarket_frontier.csv, "
                       "results/spy_proxy_design.csv; D-36, D-37, D-39, D-40"),
        },

        "time_exit": {
            "applies_to_trade_shape": "time_exit",
            "example_combination": tp["combination"],
            "why_the_bracket_frontier_does_not_apply": (
                "The stop sits at twice a forecast of the move being forecast, so it is rarely "
                "hit. The outcome in units of intended risk is a continuous quantity centred "
                "well inside +/-1, not the near-binary -1 / +R of a bracket. Its sd is not set "
                "by geometry and cannot be derived -- it has to be measured (D-43)."
            ),
            "sd_status": tp["sd_status"],
            "sd_range_reported_over": tp["sd_range"],
            "sd_estimation_method": {
                "estimand": (
                    "sd of u_i = pnl_net_i / r_i, where r_i = max(2.0 x vol_forecast_30min, "
                    "40 ticks) x tick_value x contracts -- the INTENDED risk as the stop rule "
                    "defines it. Net, not gross: the criterion is net."
                ),
                "data": "development period only; the confirmation window stays untouched",
                "look_ahead": (
                    "the forecast must be computable strictly before 14:30 CT; checked against "
                    "timestamps by the data-integrity agent, not taken on trust"
                ),
                "estimator": (
                    "sample sd with a 20-day moving-block bootstrap CI, because volatility "
                    "regimes persist across days and an iid interval would be too narrow"
                ),
                "planning_figure": (
                    "the UPPER 95% bound, not the point estimate. For an edge the conservative "
                    "direction is down (D-04); for a dispersion it is up, because underestimating "
                    "sd under-powers the confirmation test."
                ),
                "diagnostics_that_can_invalidate_the_framing": [
                    "stop-hit rate: if the stop is not rarely hit, the outcome is bracket-like "
                    "and this section is the wrong one",
                    "fraction where the 40-tick floor binds, with sd estimated separately in "
                    "floor-bound and forecast-bound days; a material difference makes the pooled "
                    "sd a mixture",
                    "realised/forecast ratio: tests the forecast, not the outcome",
                    "kurtosis",
                    "CLT adequacy, by bootstrapping the t-statistic's upper tail -- the "
                    "sample-size formula assumes a normal mean and 30-minute returns are not",
                ],
                "frozen_before_confirmation": (
                    "written into the pre-registration with the result file's sha256 before the "
                    "confirmation test is registered; never re-estimated after confirmation data "
                    "is seen"
                ),
                "may_not_be_used_to_choose": [
                    "the 2.0 stop multiplier", "the 40-tick floor",
                ],
                "source": "DECISIONS.md D-43",
            },
            "sharpe_invariant": {
                "formula": tp["sharpe_invariant"],
                "sharpe_definition": "S = (edge / sd) * sqrt(252), one trade per day",
                "note": (
                    "e and sd CANCEL. The confirmation span depends only on the per-trade "
                    "information ratio. Verified against the bracket frontier: e = 0.10 at "
                    "R = 1.5 implies S = 0.853 and 14.9 years, which is what "
                    "results/feasibility_frontier.csv gives independently."
                ),
                "criterion_is_not_scale_free_for_this_shape": (
                    "e and sd are both in units of INTENDED RISK, which the stop rule sets. "
                    "Halving the 2.0 multiplier doubles both, leaves S and every span unchanged, "
                    "but moves e across the 0.10 criterion. So the multiplier and the tick floor "
                    "are part of the CRITERION's definition for this shape, not free parameters, "
                    "and a pre-registration must fix them before e >= 0.10 means anything. This "
                    "is a statement about what the criterion measures, NOT an argument for "
                    "relaxing it."
                ),
            },
            "post_publication_confirmation": {
                "design": tp["design"],
                "superseded_design": tp["superseded_design"],
                "confirmation_start_date": tp["confirmation_start_date"],
                "confirmation_start_status": tp["confirmation_start_status"],
                "confirmation_window_years": tp["confirmation_window_years"],
                "confirmation_window_years_superseded": tp[
                    "confirmation_window_years_superseded"],
                "development_available_futures_only": tp["development_futures_only"],
                "development_available_with_spy_proxy": tp["development_with_spy"],
                "development_need_not_match_confirmation": (
                    "For a fully specified combination development only estimates sd (D-43) and "
                    "runs sanity checks, so it need not match the confirmation span. For any "
                    "combination with parameters chosen on data the D-13 split rules still "
                    "apply, and which case a candidate is in must be declared BEFORE the run."
                ),
                "sd_estimation_adequacy": tp["sd_estimation_adequacy"],
                "sd_estimation_worst_case_extra_span": tp["sd_estimation_worst_case_extra_span"],
                "spy_proxy_not_needed_for_sd": (
                    "~1,270 one-a-day trades of futures development pin sd to a few per cent "
                    "even at kurtosis 9 with serial-dependence inflation 2. Planning on D-43's "
                    "upper 95% bound costs at most "
                    f"{tp['sd_estimation_worst_case_extra_span']:.0%} extra confirmation span, "
                    "so the D-40 proxy assumption is not required by this design."
                ),
                "min_implied_sharpe_single_market": tp["min_sharpe_single_market"],
                "min_implied_sharpe_single_market_superseded": tp[
                    "min_sharpe_single_market_superseded"],
                "min_implied_sharpe_by_k_and_rho": te_min_sharpe,
                "max_sd_that_fits_by_edge": te_max_sd,
                "any_fitting_cell_is_also_plausible": te_any_plausible,
                "verdict": (
                    "Under the corrected design (D-49) single-market needs S >= "
                    f"{tp['min_sharpe_single_market']}, down from "
                    f"{tp['min_sharpe_single_market_superseded']}: ON the "
                    f"{tp['plausible_sharpe_ceiling']} plausibility ceiling rather than beyond "
                    "it. So single-market is no longer ruled out outright, but it is marginal. "
                    "Pooling is what puts the requirement comfortably inside plausible "
                    "territory: ES+GC+CL+6E needs 0.469 at rho = 0, 0.593 at rho = 0.2 and "
                    "0.646 at rho = 0.3; any three-market subset needs 0.541 / 0.640 / 0.684."
                ),
                "feasibility_and_plausibility_pull_opposite_ways": (
                    "A cell fits the window only by implying a high per-trade information ratio. "
                    "The cells that fit most comfortably imply Sharpe ratios a published effect "
                    "is least likely to still be delivering. FITTING THE WINDOW IS NOT EVIDENCE "
                    "IN FAVOUR OF A CANDIDATE."
                ),
                "plausible_sharpe_ceiling": tp["plausible_sharpe_ceiling"],
                "plausible_sharpe_ceiling_status": tp["plausible_sharpe_ceiling_status"],
            },
            "source": "results/time_exit_frontier.csv; DECISIONS.md D-43, D-44, D-45",
        },

        "multi_market_sizing": {
            "question": (
                "A frontier that says 'trade three to six markets' is worthless if a fresh funded "
                "account cannot hold a position in three markets at once. This section is that "
                "check (D-47)."
            ),
            "entry_tier_budget_micro_equivalents": zp["budget_micro_equivalents"],
            "cap_is_aggregate_not_per_instrument": zp["aggregate_cap_basis"],
            "per_market_vehicle": per_market_vehicle,
            "no_micro_tracks_zn": (
                "Two CME products look like a micro ZN and neither is. Micro Treasury YIELD "
                "futures are quoted in yield, $10/bp, cash-settled to a BrokerTec yield fixing -- "
                "a different quantity, moving INVERSELY to price. Micro Ultra 10-Year futures "
                "cash-settle to the ULTRA 10-Year note (TN), a different contract from ZN with a "
                "different deliverable basket and DV01. GC, CL and 6E all have true 1/10 micros "
                "on the same underlying. ZN is the exception: full size only, so one contract "
                "costs a whole mini-equivalent -- HALF the entry-tier allowance."
            ),
            "m6e_tick_trap": (
                "M6E is 1/10 the notional of 6E but its tick is 0.0001 against 6E's 0.00005, so "
                "its tick VALUE is 1/5, not 1/10. Never convert a stop in ticks between them by "
                "the size ratio."
            ),
            "allocation_rule": (
                "A pooled test weights markets equally in RISK, not in contracts. Equal contracts "
                "look balanced and are not: one MES contract risks $25 at its cost floor where "
                "one ZN risks $187.50. Allocations below equalise risk subject to the cap."
            ),
            "expressible_on_fresh_account": sets_ok,
            "need_a_higher_tier": sets_no,
            "expressibility_test": (
                "holds at least one contract per market AND per-market risk within 1.5x"
            ),
            "recommended_pool": (
                "ES+GC+CL+6E -- the four-market ZN-free set. 1.1x risk spread, needs only 4 of "
                "20 micro-equivalents to hold one contract each, so it has room to scale within "
                "the entry tier."
            ),
            "stops_used_are_cost_floors": (
                "Each market's stop here is the narrowest keeping cost drag within 0.10, from "
                "that instrument's verified tick value and round turn. It is a COST floor, not a "
                "volatility estimate; the volatility floor (D-46) needs the D-43 measurement and "
                "does not exist yet. A wider real stop raises risk per contract, so these "
                "expressible-risk figures are UPPER bounds."
            ),
            "unresolved_conflict_that_could_void_this": (
                "The micro ratio is disputed in config/rules.yaml: the help centre says 10:1, an "
                "official Topstep blog says each micro counts as a FULL contract. Under the blog "
                "reading the entry-tier budget is "
                f"{zp['budget_under_blog_reading']} contracts TOTAL and NO three-market set is "
                "expressible at all -- the whole pooled route would sit behind a funded account "
                "already scaled past $2,000. A question for support, not something to split."
            ),
            "source": "results/multimarket_sizing.csv; DECISIONS.md D-47",
        },

        "stop_rule_is_part_of_the_criterion": {
            "applies_to_trade_shape": "time_exit",
            "rule": (
                "The stop multiplier and the tick floor are fixed in the pre-registration and "
                "never tuned. A run that changes either is a NEW pre-registration with a new id."
            ),
            "why": (
                "e and sd are both in units of intended risk, which the stop rule sets. "
                "Tightening the stop raises e without changing the strategy by one trade: the "
                "sample-size frontier does not move, but the candidate crosses e >= 0.10. A pass "
                "bought by arithmetic."
            ),
            "floors_are_per_instrument": (
                "A floor stops the rule demanding a stop narrower than that market's own noise, "
                "which is a property of the instrument, not of ES. 40 ticks of MES is $50; of ZN, "
                "$625; of M6E, $50 but twice the price move of 40 ticks of 6E. One tick count "
                "copied across a pooled set imposes several different risk budgets while looking "
                "uniform. Express each floor in that instrument's own volatility or ticks."
            ),
            "two_floors_binding_is_the_wider": {
                "cost_floor": "narrowest stop keeping drag within the criterion; computable now",
                "volatility_floor": "needs the per-instrument measurement in D-43; DOES NOT EXIST YET",
            },
            "source": "DECISIONS.md D-44, D-46",
        },

        "plausibility_rule": {
            "rule": (
                "A cell that fits its confirmation window only by implying a net annual Sharpe "
                "above the stated ceiling is NOT evidence in favour of a candidate."
            ),
            "ceiling": tp["plausible_sharpe_ceiling"],
            "ceiling_status": tp["plausible_sharpe_ceiling_status"],
            "superseded_verdict": (
                "Before D-49 this section read 'single-market post-publication confirmation is "
                "not pursued'. The design correction lengthened the window and the verdict "
                "softened from ruled out to marginal. Recorded rather than overwritten, because "
                "the rule did not change -- only what it implies."
            ),
            "why_the_usual_reading_inverts": (
                "Normally the fitting cells of a feasibility table are the promising ones. Here a "
                "cell fits only by asserting a high per-trade information ratio, and these are "
                "PUBLISHED effects being confirmed on POST-PUBLICATION data, where the prior is "
                "decay toward zero rather than a sustained Sharpe above 1. Fitting the window is "
                "evidence the assumed sd is too optimistic, not that the candidate is strong."
            ),
            "single_market_status": (
                "MARGINAL, not ruled out. Under the superseded design (D-49) it needed S >= "
                "1.113, beyond the ceiling, and was ruled out outright. The 12.32-year window "
                "brings it to 0.937 -- ON the ceiling. It survives only where the fitting and "
                "plausible regions just cross, at the TOP of the stated sd range (sd >= ~1.59 at "
                "e = 0.10, against a 0.5 reference point), because a high sd is what makes a cell "
                "plausible and also what makes it expensive. A single-market design must "
                "therefore argue for a pessimistic sd AND the criterion edge at once."
            ),
            "the_route": (
                "pooling across WEAKLY CORRELATED markets. The requirement falls as "
                "S >= 1.113*sqrt([1+(k-1)rho]/k), but at rho = 0.5 six markets still need 0.85 -- "
                "so the pool is chosen for independence, not merely for count."
            ),
            "what_this_is_not": (
                "Not a relaxation of e >= 0.10, which is untouched, and not a licence to prefer "
                "whichever design implies a comfortable Sharpe. The ceiling labels rows and rules "
                "out a design class; it never filters rows inside a result file. Every cell and "
                "its implied Sharpe stay in the CSV so a reader can apply their own threshold."
            ),
            "source": "results/time_exit_frontier.csv; DECISIONS.md D-44, D-48",
        },

        "leg_schedule_and_daily_risk": {
            "why_this_supersedes_the_book_view": (
                "multi_market_sizing treats the pool as a simultaneous book sharing one "
                "allowance. The legs are in fact SEQUENTIAL -- each market's 30-minute window is "
                "anchored to its own CME daily settlement and the four settle at four different "
                "times -- so the position cap, which limits open positions at an instant, "
                "applies PER LEG. See D-50."
            ),
            "settlement_source": lp["settlement_source"],
            "flatten_ct": lp["flatten_ct"],
            "legs": [
                {k: v for k, v in leg.items()
                 if k in ("market", "vehicle", "settle_ct", "window",
                          "settle_window_source", "cost_floor_ticks", "risk_per_contract")}
                for leg in lp["legs"]
            ],
            "one_instant_of_contact": (
                "CL's exit and 6E's entry are both 13:30:00, so for one instant two positions "
                "are open. Enter 6E at 13:30:30, or budget CL and 6E jointly, and say which in "
                "the pre-registration."
            ),
            "cap_per_leg_micro_equivalents": lp["cap_per_leg_micro_equivalents"],
            "cap_is_not_a_risk_control_here": (
                "One leg at the full 20-micro cap risks ~$600 -- 30% of the cushion in a single "
                "leg, and four such legs would be 120% of it. The cap does not protect the "
                "account at this size."
            ),
            "cushion_usd": lp["cushion_usd"],
            "cushion_source": lp["cushion_source"],
            "mll_is_checked_intraday": (
                "Realised AND unrealised P&L count and the account is liquidated the moment Net "
                "P&L touches the limit, so the RUNNING TOTAL across sequential legs binds, not "
                "the end-of-day figure."
            ),
            "daily_risk_limit": {
                "rule": (
                    "the day's worst case -- every leg stopped -- must not exceed one eighth of "
                    "the cushion"
                ),
                "fraction": lp["recommended_daily_limit_fraction"],
                "usd": round(lp["cushion_usd"] * lp["recommended_daily_limit_fraction"], 2),
                "basis": (
                    "the guardrail 'no single position decides the account' applied to the day: "
                    "for a day of sequential legs the day IS the position, and eight consecutive "
                    "worst-case days are needed to exhaust the cushion"
                ),
                "allocation": {
                    str(r.market): {
                        "vehicle": str(r.vehicle), "contracts": int(r.contracts),
                        "leg_risk_usd": round(float(r.leg_risk), 2),
                        "window_ct": str(r.window_ct),
                    }
                    for r in legs[
                        legs.daily_limit_fraction == lp["recommended_daily_limit_fraction"]
                    ].itertuples()
                },
                "day_worst_case_usd": round(float(legs[
                    legs.daily_limit_fraction == lp["recommended_daily_limit_fraction"]
                ].day_worst_case_loss.iloc[0]), 2),
                "day_worst_case_fraction_of_cushion": round(float(legs[
                    legs.daily_limit_fraction == lp["recommended_daily_limit_fraction"]
                ].day_worst_case_as_fraction_of_cushion.iloc[0]), 4),
                "risk_spread": round(float(legs[
                    legs.daily_limit_fraction == lp["recommended_daily_limit_fraction"]
                ].risk_spread.iloc[0]), 2),
                "days_to_2000_at_criterion": round(float(legs[
                    legs.daily_limit_fraction == lp["recommended_daily_limit_fraction"]
                ].days_to_2000_at_criterion.iloc[0]), 1),
            },
            "granularity_dominates_the_percentage": (
                "One micro per leg is $103.50 worst case and two is $207, with nothing between. "
                "A 10% limit ($200) forbids two-each by $7 and halves position size. The limit "
                "was set at one eighth rather than one tenth for that reason, and the reason is "
                "recorded because choosing a threshold to admit a position size is exactly the "
                "move that needs to be visible (D-50)."
            ),
            "stops_are_cost_floors": (
                "Each leg's stop is the narrowest keeping cost drag within 0.10. The "
                "volatility floor (D-46) needs the D-43 measurement and does not exist yet, so "
                "risk per contract here is a LOWER bound and these position sizes are UPPER "
                "bounds."
            ),
            "source": "results/leg_schedule.csv; DECISIONS.md D-50",
        },

        "cross_account_hedging_prohibited": {
            "status": "HARD CONSTRAINT",
            "rule": (
                "For every correlated instrument group g and every instant t, the SIGN of the "
                "position in g is the same across all accounts. Zero is compatible with any sign."
            ),
            "source_article": "help.topstep.com 13747047 'Understanding Hedging', read "
                              "2026-09-23 by Claude (page text)",
            "verbatim_prohibition": (
                "Cross-account hedging is prohibited at Topstep -- 'simultaneously going long "
                "and short the same or correlated instrument across multiple accounts'."
            ),
            "verbatim_why_monitoring_is_insufficient": (
                "'Opposing positions are prohibited even if the overlap is brief or "
                "unintentional.' Brief AND unintentional are both named, so this is not a "
                "guideline to honour on average, nor a monitor that unwinds breaches after the "
                "fact. A breach lasting one second during order transit is a breach."
            ),
            "verbatim_consequence": (
                "'Accounts closed for hedging violations are not eligible for payouts, and any "
                "associated profits cannot be withdrawn'; such accounts 'cannot be reopened or "
                "reinstated'. Campaign-level, not per-trade."
            ),
            "correlated_groups": {
                "equity_index": ["ES", "MES", "NQ", "MNQ"],
                "gold": ["GC", "MGC"],
                "crude": ["CL", "MCL"],
                "euro_fx": ["6E", "M6E"],
                "rates": ["ZN"],
                "base_metals": ["HG", "MHG"],
                "natural_gas": ["NG", "MNG"],
                "crypto": ["MBT", "MET"],
            },
            "why_all_equity_index_is_one_group": (
                "The article prohibits opposing positions in 'the same or correlated instrument' "
                "and does not define 'correlated', so the grouping is ours and the choice is "
                "ASYMMETRIC. Splitting ES from NQ when Topstep treats them as correlated risks "
                "account closure, payout ineligibility and forfeiture of unwithdrawn profit. "
                "Merging them when Topstep would have allowed a split costs only expressiveness. "
                "A wrong guess is recoverable in one direction and not in the other, so the "
                "conservative reading is taken without waiting for clarification (D-58)."
            ),
            "groups_are_a_design_constraint_not_a_formality": (
                "The partition gives each group to exactly one strategy, so the number of groups "
                "caps the number of strategies a partitioned layout can staff. See "
                "account_layout.staffing_constraint_that_binds."
            ),
            "enforcement": [
                "GROUPS NOT CONTRACTS: the page says 'or correlated instrument', so the unit is "
                "a declared correlated group. ALL equity index futures (ES, MES, NQ, MNQ) are "
                "ONE group under D-58; the full list is in correlated_groups above.",
                "PRIMARY -- instrument partition: each group is assigned to exactly one strategy "
                "for the whole campaign, so two strategies never trade the same group and "
                "opposite positions cannot be constructed.",
                "FALLBACK -- direction lock: where a partition is infeasible, a campaign-level "
                "director holds one signed target per group; a strategy wanting the opposite "
                "sign is FLATTENED TO ZERO, never reversed.",
                "PRE-TRADE GATE: no order is routed unless the resulting sign matches the "
                "campaign sign for that group. A violating order is REJECTED, NOT QUEUED -- a "
                "queue reintroduces the brief overlap the article names.",
                "SEQUENCING: changing a group's sign requires every account FLAT in that group "
                "first, with fills confirmed, before any reversing order is routed. "
                "Flatten-then-enter, never reverse-through-zero. This is the clause that handles "
                "'brief or unintentional', and it costs a round turn at every reversal which the "
                "cost model must carry.",
            ],
            "interaction_with_allocation": (
                "A copier running ONE strategy across accounts satisfies the invariant "
                "automatically. Strategy-per-account is the allocation that needs this "
                "machinery."
            ),
            "source": "config/rules.yaml:cross_account_hedging; DECISIONS.md D-55",
        },

        "portfolio_of_strategies": {
            "design": pf["design"],
            "confirmation_window_years": pf["confirmation_window_years"],
            "required_component_sharpe_by_k_and_rho": port_req,
            "multiplicity": {
                "pooled_claim_costs_nothing_in_z": (
                    "Declaring k strategies in advance and testing ONE pre-specified pooled "
                    "statistic is a single test at z = 1.645. k is paid in DATA, through the "
                    "design effect 1+(k-1)rho, not in the critical value."
                ),
                "component_claim_costs_the_full_bonferroni": (
                    "Claiming any individual component is a second look and needs z at 0.05/k, "
                    "which raises the per-component Sharpe requirement by 1.4x to 2.5x. A design "
                    "must declare IN ADVANCE whether it claims the portfolio or the components."
                ),
                "selection_cost": (
                    "k is the number of variants TRIED, not kept, and it is spent on the "
                    "development period under D-13, not on confirmation."
                ),
            },
            "per_component_checks": pf["per_component_checks"],
            "the_failure_these_guard": (
                "A pooled mean can pass on one live component while the rest are dead. "
                "leave_one_out is decisive: if the result does not survive removing the best "
                "component, it is a single-strategy finding and must be reported as one."
            ),
            "rho_is_an_assumption": (
                "Cross-strategy correlation is NOT measured. Estimate it on development data "
                "before any pooled claim, exactly as D-37 requires for markets."
            ),
            "source": "results/portfolio_frontier.csv; DECISIONS.md D-56",
        },

        "account_allocation": {
            "question": "every strategy in every account, or one strategy per account?",
            "theta_ratio": ap["theta_ratio"],
            "race_source": ap["race_source"],
            "oracle": (
                f"the driftless race reproduces stage one's analytic ceiling exactly: "
                f"{ap['oracle_zero_edge_combine_pass']} = 2/5 zero-edge Combine pass"
            ),
            "at_component_sharpe_1.0": alloc_rows,
            "portfolio_per_account_wins_per_account": (
                "theta_A/theta_B = k/[1+(k-1)rho] exactly, so A always wins per account when "
                "rho < 1 -- pass ratio 1.10 to 1.44 across the grid."
            ),
            "strategy_per_account_wins_campaign_survival": (
                "P(at least one account passes) is higher for B in every cell, by up to +0.073, "
                "most at low Sharpe and high rho, because its failures are imperfectly "
                "correlated."
            ),
            "A_is_slower_because_it_succeeds_more": (
                "Both allocations have the same daily drift, so A is not faster -- it is slower. "
                "A race that runs to +$3,000 takes longer than one stopped at -$2,000, so "
                "raising the pass rate raises expected duration: A resolves in 1.5-2.7 years "
                "against B's 1.2-1.5. A buys certainty and pays in time, which is exactly what "
                "D-14's time-aware objective prices."
            ),
            "neither_dominates_on_conduct": (
                "A puts identical positions in every account, so one bad day hits every MLL at "
                "once -- the first named RTP trigger (D-30), satisfied BY CONSTRUCTION. B breaks "
                "that correlation but lets different strategies take opposite sides of one "
                "instrument in different accounts, which is the prohibited hedge (D-55). The "
                "choice is which prohibited state you engineer against."
            ),
            "assumptions": ap["assumptions"],
            "figures_are_optimistic": (
                "Continuously monitored STATIC barriers calibrated to DAILY aggregates: this "
                "misses within-day excursions against an intraday-monitored limit, and ignores "
                "the MLL's upward trail. Both point the same way. Treat every probability as an "
                "upper bound."
            ),
            "source": "results/account_allocation.csv; DECISIONS.md D-56",
        },

        "portfolio_claim_rule": {
            "status": "HARD CONSTRAINT on pre-registration",
            "rule": (
                "A multi-strategy pre-registration claims the PORTFOLIO: one pre-specified "
                "pooled statistic, tested once at z = 1.645, with the five per-component checks "
                "attached. COMPONENT-LEVEL CLAIMS ARE NOT MADE."
            ),
            "why": (
                "The pooled claim is a single test and costs nothing in z; claiming components "
                "individually needs z at 0.05/k and raises the per-component Sharpe requirement "
                "by 1.4x to 2.5x. Paying that must be decided BEFORE seeing which components "
                "worked, and the honest way not to decide it afterwards is not to reserve the "
                "option."
            ),
            "leave_one_out_is_decisive": (
                "A design whose pooled result does not survive removing the single best "
                "component is REPORTED AS A SINGLE-STRATEGY FINDING, not a portfolio one, and "
                "carries the multiplicity cost of having tried k. That is the outcome this rule "
                "exists to force: the alternative is reporting one live strategy plus noise as a "
                "diversified edge, which is true of the arithmetic and false about the world."
            ),
            "components_remain_as_diagnostics": (
                "Per-component figures stay in the result file. What is forbidden is CLAIMING "
                "them."
            ),
            "source": "DECISIONS.md D-56, D-57",
        },

        "account_layout": {
            "layouts": dp["layouts"],
            "structural_result": (
                "A and C hold the same m strategies per account, so their per-account variance "
                "s^2[1+(m-1)rho]/m and pass probability are IDENTICAL by construction. They "
                "differ only in cross-account correlation: 1 for A, m*rho/[1+(m-1)rho] for C. "
                "C is therefore A's upside with strictly less joint failure whenever rho < 1."
            ),
            "at_component_sharpe_1.0": three_way,
            "verdict_vs_A": (
                "C dominates A in 24 of 24 simulated cells. Not a close comparison."
            ),
            "verdict_vs_B": (
                "C wins per-account pass everywhere and matches or beats campaign survival and "
                "the same-day multi-MLL frequency up to rho ~ 0.3. At rho = 0.5 the advantage "
                "closes: survival converges and B's RTP-trigger frequency becomes the better of "
                "the two, because m*rho/[1+(m-1)rho] rises faster than rho."
            ),
            "why_pooling_raises_cross_account_correlation": (
                "Averaging away idiosyncratic variance leaves the common factor, so accounts "
                "sharing NO strategy still become more alike as each holds more. That is the "
                "cost C pays against B and it is why C's advantage is bounded in rho."
            ),
            "staffing_constraint_that_binds": {
                "rule": dp["staffing_rule"],
                "groups_available": dp["groups_available"],
                "correlated_groups": dp["correlated_groups"],
                "consequence": (
                    "C at N=4 needs 8 strategies at m=2 and 12 at m=3. Only 5 groups exist, so "
                    "THOSE ROWS ARE NOT STAFFABLE under the strict partition. They need the "
                    "direction-lock fallback, which costs exactly the expressiveness the extra "
                    "strategies were bought for. N=2/m=2 and N=5/m=1 fit as they stand, and "
                    "N=5/m=1 IS design B."
                ),
                "honest_conclusion": (
                    "C is the right layout where it can be staffed; its natural size here is "
                    "N = 2 with m = 2. Beyond that the GROUP SUPPLY, not the statistics, is the "
                    "binding constraint."
                ),
            },
            "simulation": {
                "seed": dp["seed"], "paths": dp["paths"], "max_days": dp["max_days"],
                "why_simulated": (
                    "Pass probability and duration have closed forms, but the RTP trigger "
                    "'multiple accounts hit the Maximum Loss Limit in one day' is about the "
                    "joint TIMING of first-passage events, which does not."
                ),
                "discretisation_check": (
                    "Simulated pass exceeds the continuous-barrier p_race by +0.006 on average, "
                    "in the expected direction: daily steps miss within-day excursions against "
                    "an intraday-monitored limit. BOTH are upper bounds; the simulated one is "
                    "the looser."
                ),
            },
            "figures_are_upper_bounds": (
                "Same assumptions as account_allocation: static barriers where the MLL actually "
                "trails upward, daily-calibrated volatility, equal component edges, constant "
                "rho, no consistency rule, and sd = 0.5 risk units from D-44 rather than a "
                "measurement."
            ),
            "source": "results/design_c_partitioned.csv; DECISIONS.md D-59",
        },

        "strategy_slot_supply": {
            "status": "FIRST-CLASS DESIGN CONSTRAINT -- state the slot count before the statistics",
            "why": (
                "D-55 gives each correlated group to exactly one strategy, so a layout needs "
                "accounts x strategies_per_account slots. The layouts that win on statistics are "
                "often the ones that cannot be staffed: C at N=4/m=2 needs 8 slots against the "
                "5 groups D-58 leaves. A reader taking 'C dominates' from D-59 without this "
                "would design something unbuildable (D-60)."
            ),
            "base_groups": sp2["base_groups"],
            "new_groups": sp2["new_groups"],
            "widened_groups": sp2["widened_groups"],
            "regimes": staff,
            "route_1_time_partitioned_slots": {
                "adopted": sp2["time_partition_adopted"],
                "rule_text_permits_it": (
                    "13747047 prohibits SIMULTANEOUSLY going long and short the same or "
                    "correlated instrument. Non-overlapping windows with confirmed-flat "
                    "sequencing never hold opposing positions at any instant, so on the TEXT the "
                    "partition unit may be (group, window)."
                ),
                "why_not_adopted": (
                    "Three readings say otherwise or invite review: surveillance granularity is "
                    "undocumented and may evaluate exposure per day rather than per instant; the "
                    "page threatens to flag hedging BEHAVIOUR, not merely positions, and "
                    "systematic same-group alternation across accounts is what a behavioural "
                    "review looks at; and 'even if the overlap is brief or unintentional' states "
                    "which way they resolve ambiguity. Against closure, payout ineligibility and "
                    "no reinstatement, the D-58 asymmetry argument forbids relying on it. "
                    "SPECIFIED AND UNUSED pending written confirmation from support (D-61)."
                ),
                "specification_if_confirmed": {
                    "partition_unit": "(correlated group, time window)",
                    "minimum_gap_minutes": sp2["min_gap_minutes"],
                    "gap_measured_from": (
                        "last fill CONFIRMED in the group to next order submission in it; "
                        "confirmed-flat is the binding requirement and the gap absorbs clock "
                        "skew, late and partial fills"
                    ),
                    "pre_trade_gate": (
                        "a campaign-level scheduler holds ONE window token per group. An order "
                        "without the token is REJECTED, NOT QUEUED. The token is released only "
                        "when every account is confirmed flat in that group, and cannot be "
                        "reacquired within the gap."
                    ),
                    "windows_per_group": sp2["windows_per_group"],
                    "window_minutes": sp2["window_minutes"],
                    "session_minutes": sp2["session_minutes"],
                },
                "correlation_assumption_makes_it_self_limiting": (
                    "Two windows on ONE group share instrument, day and volatility regime, so "
                    "rho_w exceeds the cross-group rho -- plausibly 0.4-0.6 against 0.0-0.3, an "
                    "ASSUMPTION until measured. C's advantage over B closes as rho rises, so the "
                    "mechanism that makes five-account C layouts staffable is the one that "
                    "erodes what they were staffed for. READ SUCH A LAYOUT OFF THE HIGH-RHO ROW."
                ),
            },
            "route_2_more_groups": {
                "adopted": True,
                "groups_5_to_8": sp2["new_groups"],
                "reaches": "N=4/m=2 and stops; N=5/m=2 needs 10 slots against 8 groups",
                "merged_not_new": (
                    "silver and platinum join gold; RBOB and heating oil join crude; Russell, "
                    "Dow and Nikkei join equity index; every G10 currency joins euro FX"
                ),
                "the_real_loss": (
                    "Corn, wheat, soybeans, meal, oil, lean hogs and live cattle are permitted "
                    "and would be the BEST diversifiers on the list -- weather and supply "
                    "driven, weakly correlated with every financial group -- but NONE has a "
                    "micro contract. Each costs a whole mini-equivalent, so none is expressible "
                    "at the entry tier. They arrive only at higher scaling tiers."
                ),
                "correlations_are_assumptions": (
                    "Natural gas is strongest on mechanism (weather, storage and US production "
                    "drive none of the other five). Crypto's assumed independence is "
                    "REGIME-DEPENDENT: it converges with equity index in risk-off stress, which "
                    "is exactly when a correlated multi-account drawdown matters."
                ),
            },
            "what_binds_next": (
                "Once either route lands there are far more slots than any layout needs, and "
                "MECHANISM SUPPLY binds instead: T4 requires every candidate to arrive with a "
                "stated mechanism, an outside prior and its cost in k. That is a research "
                "constraint and partitioning cannot solve it."
            ),
            "source": "results/slot_supply.csv; DECISIONS.md D-60, D-61, D-62",
        },

        "recommended_five_account_layout": {
            "layout": five_best,
            "slots_used": int(five[five.candidate == five_best].slots_needed.iloc[0]),
            "accounts_used": int(five[five.candidate == five_best].accounts.iloc[0]),
            "objective": sp2["objective_for_layout_choice"],
            "why_not_per_account_pass_rate": (
                "The campaign's return scales with the number of FUNDED accounts, so the "
                "quantity to maximise is accounts x pass rate subject to the slot budget. A "
                "layout that wins per account but idles an account loses on that product."
            ),
            "expected_funded_accounts_by_rho": five_by_rho,
            "why_mixed_wins": (
                "It spends the entire slot budget across all five accounts -- portfolios where "
                "slots allow, single strategies where they do not. Both pure layouts waste "
                "something: B leaves three groups unused, C idles a whole account. The margin "
                "over pure B is about a quarter of an account, which is real but not decisive; "
                "what is decisive is that both pure layouts are dominated at EVERY rho."
            ),
            "needs_nothing_unconfirmed": (
                "Every group is owned by exactly one strategy, so the hedging invariant holds by "
                "construction and no time-partitioning is required. It does not depend on D-61."
            ),
            "conditions": (
                "Assumes eight staffable mechanisms exist, which is now the binding constraint. "
                "Every probability behind it is an upper bound under the D-56 assumptions: "
                "static barriers, daily-calibrated volatility, equal edges, constant rho, no "
                "consistency rule, sd = 0.5 risk units."
            ),
            "source": "results/slot_supply.csv, results/design_c_partitioned.csv; D-63",
        },

        "execution_templates": {
            "document": "docs/CONTRACT_FOUNDATIONS.md",
            "legend": {
                "pre_reg": "a pre-registration must fix this before any run",
                "T7": "a campaign-model choice to be optimised; the stated value is provisional",
                "hard": "a hard constraint, not a parameter",
            },
            "combine_phase": {
                "daily_risk": {"value": "<= 1/8 of the $2,000 cushion ($250)", "fixed_by": "T7",
                               "why": "conduct guardrail applied to the day (D-50); sweep "
                                      "1/12-1/4 in T7 (D-54)"},
                "largest_planned_day": {"value": "< $1,650", "fixed_by": "pre_reg",
                                        "why": "55% consistency cap on a $3,000 target"},
                "stop_width": {"value": "cost floor <= stop <= daily limit / (contracts x tick)",
                               "fixed_by": "pre_reg floor, T7 ceiling",
                               "why": "drag falls as the stop widens (D-65)"},
                "stop_multiplier_and_tick_floor": {
                    "value": "fixed, per instrument, never tuned", "fixed_by": "pre_reg",
                    "why": "part of the criterion's definition for time-exit trades (D-46)"},
                "R": {"value": "> 1; 1.5-3 tested", "fixed_by": "pre_reg",
                      "why": "winners larger than losers; edge amplification is largest at "
                             "SMALL risk, which points the same way as the guardrails"},
                "target_geometry": {"value": "profit spread over >= 2 days; no day >= 55%",
                                    "fixed_by": "pre_reg", "why": "consistency cap"},
                "trades_per_day": {"value": "1 per market per leg, legs sequential",
                                   "fixed_by": "pre_reg",
                                   "why": "CME settlement schedule (D-50); cap applies per leg"},
                "expected_resolution": {"value": "report it with the subscription count",
                                        "fixed_by": "pre_reg",
                                        "why": "fees are a step function in calendar time; this "
                                               "is why the objective is time-aware (D-02)"},
                "excluded_deliberately": (
                    "The R x risk ~ $1,500 ridge. It is the ZERO-EDGE optimum, marked 'not "
                    "admissible' by propsim D-36, and a positive-edge design does not sit on it: "
                    "with an edge, more bets is better, not fewer."
                ),
            },
            "funded_phase": {
                "position_size": {"value": "from the CURRENT tier, re-derived after every "
                                           "withdrawal", "fixed_by": "pre_reg",
                                  "why": "ladder 0:2,1500:3,2000:5 (D-32); a payout drops the "
                                         "tier (D-53)"},
                "daily_risk_limit": {"value": "<= 1/8 of the CURRENT cushion", "fixed_by": "T7",
                                     "why": "computed at the current tier, never the highest "
                                            "reached (D-53)"},
                "per_leg_allocation": {"value": "equal RISK across legs, spread <= 1.5x",
                                       "fixed_by": "pre_reg",
                                       "why": "a pooled test weights markets equally in risk"},
                "payout_trigger": {"value": "a buffer above the minimum; value NOT ported from "
                                            "stage one", "fixed_by": "T7",
                                   "why": "propsim D-45's $8,000 ignored payout latency, "
                                          "reinvestment and per-contract costs -- a hint, not a "
                                          "settled value"},
                "payout_method": {"value": "fee AND lag by method", "fixed_by": "pre_reg input",
                                  "why": "payout_methods_and_fees is UNVERIFIED -- a blocker, "
                                         "not a default"},
                "high_R_payout_timing": {
                    "value": "report the expected delay", "fixed_by": "pre_reg",
                    "why": "the net-profit-since-payout rule stops a high-R profile withdrawing "
                           "while net-negative, so its cash arrives later even when larger"},
                "expected_ratchet": {"value": "reported beside EV", "fixed_by": "pre_reg",
                                     "why": "the leak identity: E[Q] = (1-P_pay)(2000 - "
                                            "E[ratchet]); the leak IS the ratchet"},
                "accounts": {"value": "<= 5 active; layout 3x(m=2) + 2x(m=1)", "fixed_by": "T7",
                             "why": "D-34 cap; layout from D-63 on expected funded accounts"},
                "cross_account_direction": {
                    "value": "one signed direction per correlated group at every instant",
                    "fixed_by": "hard", "why": "D-55; groups per D-58 and D-62"},
            },
            "source": "docs/CONTRACT_FOUNDATIONS.md; vendor/propsim; DECISIONS.md D-64, D-65",
        },

        "two_levers": {
            "identity": lvp["identity"],
            "lever_1_cost_share": (
                "For a BRACKET trade, set by the risk taken -- cost drag = cost / (stop_ticks "
                "x tick_value), which is the right comparison because the criterion e >= 0.10 "
                "is in units of risk. For a TIME-EXIT trade, set by the EXPECTED DIRECTIONAL "
                "PROFIT per contract (D-73). Either way costs are charged per contract and the "
                "denominator is earned per contract, so POSITION SIZE CANCELS: 'trade smaller "
                "to cut costs' is wrong."
            ),
            "lever_2_daily_risk": (
                "contracts x stop_ticks x tick_value. Trades speed against the chance of hitting "
                "the floor, and does NOTHING to cost share."
            ),
            "why_they_get_conflated": (
                "stop_ticks appears in both, which produces a false trade-off between cost and "
                "size where none exists."
            ),
            "time_exit_denominator": lvp["time_exit_denominator"],
            "cost_share_thresholds_at_1_tick_slippage": cost_share,
            "thresholds_are_era_dependent": (
                "These tick counts are valid at ONE price level. The same return "
                "is a different number of ticks in every era -- see era_dependence "
                "and vehicle_switching_by_era (D-75)."
            ),
            "c007_minimum_expected_profit_per_contract": c007,
            "how_to_read_c007": (
                "These are ticks of EXPECTED PROFIT per contract, not ticks of range the window "
                "must travel. A leg whose expected profit is below breakeven loses money however "
                "wide the window swings. D-43's sd measures the SPREAD and CANNOT answer this: "
                "the effect comes from the literature now and the confirmation test later (D-73)."
            ),
            "three_quantities_not_to_conflate": (
                "(1) the SPREAD of the realised move, which D-43 measures as sd and which carries "
                "no direction; (2) the EXPECTED DIRECTIONAL PROFIT per contract, the effect; "
                "(3) COST SHARE = cost / (2), never / (1). Dividing by the realised move "
                "understates cost share by an order of magnitude and makes an unprofitable leg "
                "look cheap."
            ),
            "cost_share_at_a_given_effect": cost_by_effect,
            "the_multiple_that_matters": (
                "For cost share <= s the effect must be at least cost/s: TWENTY TIMES the "
                "round-trip cost at 5%, a hundred times at 1%."
            ),
            "dollar_figure_is_tick_independent": (
                "The USD column is cost/share, so it does not depend on tick value: a large-tick "
                "instrument needs fewer TICKS for the same DOLLARS, not less money."
            ),
            "source": "results/cost_share_and_risk_levers.csv; DECISIONS.md D-69",
        },

        "vehicle_choice": {
            "rule": (
                "'Position size cancels' holds WITHIN a contract type, not ACROSS micro and "
                "mini. Commission per unit of price captured differs, so the VEHICLE is itself a "
                "cost lever (D-74)."
            ),
            "never_compare_ticks_across_different_tick_sizes": (
                "In own-ticks 6E looks only 1.2x cheaper than M6E. That is an artefact: M6E's "
                "tick is 0.0001 against 6E's 0.00005, so a 'tick' is not the same price move on "
                "the two contracts. Per unit of PRICE captured 6E is 2.37x cheaper. Use a common "
                "price unit -- here the micro's own tick."
            ),
            "paired_cost_share_at_1_tick_slippage": paired,
            "advantage_before_slippage": adv_no_slip,
            "slippage_dilutes_it": (
                "One tick of slippage costs a mini ten times what it costs a micro on ten times "
                "the notional, so it is roughly neutral per unit of price. It cuts a 2.4-4.4x "
                "commission advantage to 1.5-2.1x -- and slippage is the UNMEASURED assumption, "
                "so the mini's edge is largest exactly where the cost model is least certain."
            ),
            "one_mini_risk_by_stop_micro_ticks": mini_budget,
            "minis_are_not_cheaper_risk": (
                "A mini's minimum position is one contract, so at a volatility-determined stop "
                "its smallest expressible risk is TEN TIMES the micro's. One mini per leg needs "
                "45% of the cushion at a 20-tick stop, 90% at 40 and 180% at 80. Minis are a "
                "tenfold jump in minimum risk bought for a 1.5-2.1x cut in cost share."
            ),
            "switching_fraction_by_stop_and_leg": switching,
            "nothing_switches_below_half_the_cushion": (
                "At no tested stop does any leg admit a mini below f = 0.5, and at the f = 0.125 "
                "default every leg is on micros with a wide margin. The cheaper vehicle is "
                "UNREACHABLE rather than unused: it sits behind a daily-risk level the conduct "
                "guardrail rules out on other grounds."
            ),
            "t7_requirement": (
                "T7's sweep must report, at each daily-risk level, WHICH VEHICLE each leg can "
                "use and the resulting cost share -- not assume micros throughout."
            ),
            "stop_range_is_stated_not_measured": vhp["stop_status"],
            "source": "results/vehicle_choice.csv; DECISIONS.md D-74",
        },

        "era_dependence": {
            "rule": (
                "Raw points and bare tick counts NEVER enter a signal or a comparison across "
                "periods. Every signal, stop, effect and sd is held in scale-free units: "
                "returns, volatility-scaled quantities, or units of intended risk (D-75)."
            ),
            "ticks_are_not_scale_free": (
                "A tick is a fixed price increment and price is not fixed. A 40-tick NQ stop is "
                "about 0.55% of price near 1,800 and 0.04% near 24,000. Tick counts are "
                "EXECUTION INSTRUCTIONS at a moment, not comparisons across 2009-2026."
            ),
            "scale_free_no_change_needed": [
                "sd in units of intended risk (D-43)",
                "the edge e in units of risk (the criterion)",
                "cost DRAG = cost / risk",
                "the Sharpe identity S = (e/sd)*sqrt(252)",
                "design effect, rho, cluster factor",
                "the daily-risk limit as a FRACTION of the cushion",
            ],
            "era_dependent_now_labelled": [
                "stop and floor widths in ticks (D-46)",
                "cost-share thresholds in ticks (D-69, D-73) -- valid at one price level only",
                "vehicle switching points (D-74) -- recomputed per era below",
            ],
            "the_floor_is_the_era_dependent_half": (
                "The volatility-scaled stop 2.0 x sigma_30 is scale-free; the FLOOR it is maxed "
                "against is not. So the stop rule is scale-free only while the forecast term "
                "binds, and the floor makes it era-dependent in QUIET regimes -- which is "
                "exactly when the floor binds."
            ),
            "cost_share_by_price_level": era_ratio,
            "a_falling_cost_share_is_not_an_improving_edge": (
                "Cost share falls MECHANICALLY as price rises: the same return is more ticks in "
                "a higher market. NQ's cost share is 13.3x heavier at the low price level than "
                "the high one. Any diagnostic reporting cost share by year must report PRICE "
                "ALONGSIDE it, or a rising market will be read as an improving edge."
            ),
            "required_subperiods": ["2014-2018", "2019-2021", "2022 onwards"],
            "subperiods_are_pre_registered": (
                "Every pre-registration declares its subperiods IN ADVANCE and checks that the "
                "pooled result does not depend on a single one. A subperiod chosen after seeing "
                "the pooled result is not a robustness check, it is a second look."
            ),
            "sd_stability_diagnostic": (
                "D-43 gains a diagnostic comparing sd in units of intended risk across "
                "development-period years. A material trend means the planning figure must "
                "account for it rather than averaging over it."
            ),
            "structural_change_to_note": (
                "The post-2022 growth of same-day (0DTE) options is a structural change in "
                "intraday flow and bears directly on C-007's hedging mechanism. A pooled result "
                "spanning it must show the 2022-onwards subperiod separately."
            ),
            "price_levels_are_illustrative": erp["price_level_status"],
            "source": "results/era_and_vehicle.csv; DECISIONS.md D-75",
        },

        "slippage_model": {
            "status": "SPECIFIED, NOT ESTIMATED -- needs quote data (T2)",
            "conditioned_on": ["instrument", "vehicle (micro vs mini)", "time of day", "year"],
            "estimated_from": (
                "QuantConnect quote data (bid-ask spread) on DEVELOPMENT-PERIOD data only; the "
                "cloud guard refuses any run reaching 2014-05-28"
            ),
            "why_each_condition": {
                "instrument": "spreads differ by contract and by liquidity",
                "vehicle": "a micro's spread in ticks is not a mini's; they are separate books",
                "time_of_day": (
                    "each C-007 leg trades a different 30-minute window, and spread varies "
                    "sharply across the session"
                ),
                "year": "liquidity in 2009-2012 is not liquidity today, in either direction",
            },
            "stop_slippage_modelled_separately": (
                "A stop is a market order once touched, so it pays the spread plus whatever the "
                "move through it costs. Around SCHEDULED ANNOUNCEMENTS that is a different "
                "distribution and is modelled separately, not averaged in."
            ),
            "micros_before_may_2019": (
                "Micro E-minis launched 2019-05-06. Before that a micro's fills are SIMULATED "
                "FROM MINI DATA and must be labelled as such in any result -- it is an "
                "assumption about a contract that did not exist, not a measurement."
            ),
            "validation_planned": (
                "Current-era estimates are validated against the trader's own fills once that "
                "export exists. Until then slippage remains the largest unmeasured driver of "
                "viability (config/fills.yaml)."
            ),
            "source": "docs/PIPELINE.md; DECISIONS.md D-76",
        },

        "optional_tradability_filter": {
            "status": "PRE-REGISTRABLE OPTION, not a default",
            "rule": (
                "Skip a leg when the bid-ask spread or the volume at that time of day falls "
                "outside a stated range."
            ),
            "counts_in_k": (
                "It is an ENTRY CONDITION, so it counts as a variant in k and is declared in "
                "advance with its thresholds. Adding it after seeing which days lost money is "
                "the definition of a post-hoc filter."
            ),
            "thresholds_must_be_absolute_not_relative": (
                "A threshold expressed as a percentile of the sample is fitted to the sample. "
                "State it in spread ticks and contracts at that time of day, per era."
            ),
            "source": "DECISIONS.md D-76",
        },

        "vehicle_switching_by_era": {
            "why_it_moves": (
                "A volatility-scaled stop is a fixed RETURN, so its dollar risk per contract "
                "grows with notional. A mini's minimum risk grows with it, and the switch to "
                "minis gets HARDER in a higher market, not easier (D-75)."
            ),
            "switch_fraction_by_leg_stop_and_price_level": vehicle_era,
            "stop_units": "basis points of price (a return), not ticks",
            "source": "results/era_and_vehicle.csv; DECISIONS.md D-75",
        },

        "mixed_vehicle_designs": {
            "at": ("mid price level, 20 bp stop, rho = 0.2, effect 5 bp, "
                   f"{erp['confirmation_window_years']} y window"),
            "designs": mixed,
            "the_trade_off_is_not_what_it_looks_like": (
                "Minis cut cost share, but they raise daily risk tenfold per leg, and the only "
                "way to hold risk down is to DROP LEGS -- which raises the Sharpe the pooled "
                "test requires, because k falls. The choice is cheaper execution against a "
                "HARDER STATISTICAL BAR, not cheaper execution or not."
            ),
            "t7_scores_it_on": ["median log growth", "ruin of the fee bankroll",
                                "payout latency", "subscription cost",
                                "same-day multi-account loss-limit events"],
            "the_250_limit_is_provisional": (
                "D-54: the $250 default is a provisional CHOICE, not a rule. Whether daily risk "
                "around half the cushion is worth the minis' lower cost share is a T7 question, "
                "settled on the five metrics above and never on cost share alone."
            ),
            "source": "results/era_and_vehicle.csv; DECISIONS.md D-75",
        },

        "daily_risk_lever": {
            "default": {"fraction": 0.125, "usd": 250.0,
                        "status": "WITHDRAWN as a default (D-114): a C-007-specific conduct number "
                                  "(D-50), not the campaign's risk setting. The baseline is stage "
                                  "one's admissible pairs below."},
            "baseline_from_stage_one": {
                "source": "vendor/propsim/edge/T5_RESULTS.md section 2a (pre-registered, admissible)",
                "combine": {"low_edge": "2:1 $750", "edge_at_or_above_0.10": "1.5:1 $500"},
                "funded": "1.5:1 $1000",
                "rule": "per-trade risk is set SEPARATELY for the Combine and the funded account, "
                        "starting from these pairs, at R >= 1.5; the strategy test itself is "
                        "size-free (u = pnl / intended risk)",
                "reconciliation_with_the_tier": {
                    "decision": "D-117 (answers 2B R-04)",
                    "contracts": "min(floor(pair_risk / (stop_ticks x tick_value)), headroom_cap)",
                    "headroom_cap": "75 % of the CURRENT tier's micro-equivalent allowance, rounded "
                                    "down: 15 micros at the 2-mini entry tier",
                    "why": "RTP trigger 2 (help.topstep.com 13620045, verbatim: 'You max position a "
                           "majority of your trades') and the carried guardrail 'risk per position "
                           "well below the maximum'. Sizing at the tier maximum is never the default.",
                    "consequence": "the pair's dollar risk is reached only when the stop is wide "
                                   "enough: at the entry tier the funded $1,000 needs an MES stop "
                                   ">= 54 ticks (1000 / (15 x 1.25)); below that the realised risk "
                                   "is capped and reported beside the intended pair",
                    "rtp_metric": "share of trades sized at the tier maximum is reported and must "
                                  "stay below one half; with the headroom cap it is zero by "
                                  "construction",
                    "status": "a declared operating rule; the 75 % is swept in T7 (60-90 %) and "
                              "scored on growth, ruin and latency, never on confirmation data",
                },
            },
            "t7_sweep_range": {"from": 0.125, "to": 1.0,
                               "widened_by": "D-70 (was 1/12 to 1/4 under D-54)",
                               "run_separately_for": ["combine", "funded"],
                               "anchored_on": "stage one's admissible pairs (D-114)"},
            "principle": (
                "Every sizing, risk or protocol parameter starts from stage one's "
                "contract-optimisation results and cites them. The prop structure is the context "
                "the execution model is built for: a strategy is sized to the contract, never the "
                "contract bent to the strategy (D-114)."
            ),
            "t7_scored_on": ["median log growth", "ruin of the fee bankroll", "payout latency",
                             "subscription cost", "same-day multi-account loss-limit events"],
            "barrier_free_reference_by_edge": risk_lever,
            "kelly_is_not_a_target": (
                "f* = e/sd^2 assumes NO absorbing barrier. The MLL is absorbing and takes the "
                "fees already paid with it. At e = 0.10 the barrier-free optimum is f = 0.40 "
                "($800/day) and P(floor before target) there is 0.114, against 0.002 at the "
                "f = 0.125 default. Growth-optimal and survival-optimal are an order of "
                "magnitude apart in ruin, and the guardrail against account-deciding positions "
                "binds long before Kelly does."
            ),
            "sd_assumption": "0.5 risk units, the D-44 reference point, NOT a measurement",
            "budget_sharing_when_an_account_holds_several_strategies": (
                "The daily limit is the ACCOUNT's, split across its m strategies at equal risk "
                "(D/m each), so the day's worst case is D whether m is 1 or 3 -- NOT D per "
                "strategy. Adding a strategy therefore buys diversification at CONSTANT risk, "
                "which is why C beats B per account (D-59), and it is why the limit is enforced "
                "at the account level rather than inside each strategy."
            ),
            "source": "results/cost_share_and_risk_levers.csv; DECISIONS.md D-70",
        },

        "cross_track_hedging_scheduler": {
            "status": "HARD CONSTRAINT -- applies across BOTH tracks",
            "why": (
                "Article 13747047 prohibits opposing positions 'across multiple accounts' with "
                "no notion of which strategy or track placed them. Two accounts are two "
                "accounts. If Track Z were ever adopted (it is not -- D-66), both tracks would "
                "trade the same correlated groups in the same accounts."
            ),
            "the_collision": (
                "C-007's ES leg holds the equity_index group 14:30-15:00 CT, and Track Z's "
                "Combine ridge and funded day-one all-in both want ES."
            ),
            "rules": [
                "TOKEN IS KEYED ON THE GROUP ALONE, never on (group, track). A Track Z request "
                "for equity_index while C-007's ES leg holds it is REJECTED, NOT QUEUED -- "
                "exactly as a same-track request would be.",
                "PRECEDENCE IS PRE-REGISTERED, never resolved at run time, because resolving it "
                "live is a decision made after seeing the market. The EDGE TRACK holds priority "
                "on its pre-registered windows, since those are fixed in a pre-registration and "
                "moving them invalidates the test. TRACK Z YIELDS.",
                "The scheduler publishes a BLACKOUT CALENDAR per group listing every window "
                "reserved by a pre-registered leg. Track Z may request a group only outside its "
                "blackout, and subject to the confirmed-flat and minimum-gap conditions.",
                "TRACK Z'S FUNDED ALL-IN CANNOT SHARE A GROUP AT ALL: it is a day-one "
                "full-cushion position held for an unbounded time, so it can never guarantee to "
                "release the token before a scheduled leg opens. A group used by the all-in is "
                "DEDICATED to it for that account's life.",
                "The pre-trade gate sees only accounts, groups and signs. It is NOT told which "
                "track an order came from, so it cannot be argued into an exception.",
            ],
            "source": "DECISIONS.md D-55, D-71",
        },

        "conduct_guardrails_hard": [
            "winners larger than losers (R > 1)",
            "risk per position well below the maximum",
            "no single position that decides the account",
            "no fail-and-repurchase campaign",
            "no cross-account hedging -- see cross_account_hedging_prohibited for the construction rule; it is a hard invariant, not a guideline (D-55)",
            "no reliance on fills the market would not give",
            "no tight brackets or auto-breakeven that depend on favourable SIM fills",
            "not ranked or modified by detectability",
        ],
        "conduct_source": "CHARTER.md; propsim D-34/D-35/D-36; help.topstep.com 10305426, 10296582",

        "rtp_triggers_to_avoid": {
            "max_positioning": "'You max position a majority of your trades' is an RTP trigger",
            "correlated_multi_account_mll": (
                "'Multiple accounts hit the Maximum Loss Limit in one day' -- a copier-correlated "
                "group satisfies this by construction (D-30)"
            ),
            "source": "help.topstep.com 13620045; DECISIONS.md D-27, D-30",
        },

        "what_a_candidate_must_arrive_with": [
            "a stated mechanism: who is on the other side and why they accept the loss",
            "a prior from outside this dataset (literature, economic argument, market structure)",
            "its cost in k, declared in advance",
            "the development span it consumes",
        ],
        "what_a_candidate_must_arrive_with_source": "NEXT_STEPS.md T4; DECISIONS.md D-36",
    }


def main() -> int:
    doc = build()
    OUT.write_text(
        HEADER + "\n" + yaml.safe_dump(doc, sort_keys=False, width=100, allow_unicode=True),
        encoding="utf-8",
        newline="\n",
    )
    print(f"wrote {OUT.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
