"""FV3's declared screen (T17 item 3; the card `docs/candidates/cards/drafts/FV3.md`): config/fv3_grid.yaml scored on
NQ's development years -- the mechanics report, the primary family's selection and walk-forward, the era rule, the
per-side drift benchmark and the D-145 gate under the state policy -- all fixed in that file before this script read an
outcome.

    python scripts/score_fv3_grid.py --declaration <D-nnn>

Reads FV3's captures R117-R132, drops FOMC days, refuses any record before 2009-06-01 or on or after 2025-07-01 (the
held-back window, D-237).

**A trade** (`Signals3.outcome`): a recorded signal in the cell's sessions, a continuation where the cell takes them,
a reversion on the triggers the cell admits (a displacement candle under the rule only within the half rung's room,
and never after two losses in the session), entered at two minutes; its stop from the ladder -- half the base stop
with 0.6 to 1.2 base stops of room, the base stop with more, twice it for a continuation on a large opening candle or,
where the cell takes it, a reversion with over three base stops of room -- and its target R x the stop (rounded down
to a whole tick) or fair value's near edge; permitted only with at least 0.8 x the target of room (his 80 %). It is
settled from its profiles (`fv3_core.settle`): stopped when the adverse profile reaches the stop no later than the
favourable one trades through the target; else the target; else the flatten at the worst of 15:07-15:10 less two
ticks (the 15:08 close where none was recorded); and the adverse excursion before its exit is read from the same
profile -- the true MAE, no bound. **Breakeven** (his rule): a trade still open at the next session's open with that
open in its favour has its stop moved to the entry, so it exits there if touched before the target. Costs: the entry
max(1 tick, the recorded spread), the fee of NQ minis with MNQ micros at the trade's micro-equivalent size under the
allowance (D-276, D-289), the exit one tick on a stop or a breakeven, none at a target, two on the flatten. The metric:
the move less the cell's median round-trip cost in R over its candidate trades of 2020 to June 2025, priced as a stop
exit. **Coordination**: per day in signal order, a trade taken only after the previous one's exit bar, at most five.

**The legs' geometry** is the state table's (D-290, D-291): in the behaviour steps the fresh-account geometry --
the Combine at 1R and $1,500 under 50 micros, the XFA at 2.5R and $2,000 under its entry allowance of 20 micros, which
caps the risk at the stop; in the gate every trade's outcome at every R of the menu rides in the blocks (D-162) and the
engine's policy picks R and risk by state, sizing whole micros at the full allowance.

**The mechanics report** (`mechanics` rows): descriptive, over every trigger the primary family can admit, at the
full rung and the base-stop outcomes -- per phase, trigger kind, session, room band, swing strength and era: n,
trades a day, gross and net e, the one-sided 95 % bound over years, hit rate, mean R at 1.5R and at fair value, the
median MAE in R, the share at the target, and the same-side benchmark comparison. Nothing is selected from it.

Writes results/<result-name>.csv (`fv3_grid` by default; D-301's corrected run names its own): `mechanics`, `capped`,
`grid`, `walkforward`, `final`, `eras`, `drift`, `gate_inputs`, `gate` (both placements, D-289: the base case's rows
carry `placement` off and the gate row; the placement-on reading beside), `spa`, `dsr`, `kline`, `summary` rows.

D-301's corrections to D-295's run (its result stays on record, D-298): the displacement axis's `off` is a string
(YAML read a bare off as false); the frequency rule sizes at the Combine's full allowance; the funded leg's drift
benchmark settles at the funded target; the gate's placement is off in the base case; D-272's stand-aside is the
engine's sizing rule per leg (`SizingRule.stand_aside`), so a Combine trade the allowance cannot carry is no trade.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

import score_orb3_search as s3  # noqa: E402
import score_orb5_grid as g5  # noqa: E402
from orb5_exploratory import CAPS, mini_mix_fee  # noqa: E402
from propedge.outcomes.fv3_core import BENCH, MISSING_FV, SESSIONS, settle  # noqa: E402
from propedge.outcomes.orb_core import FLAT_ENTRY, NONE  # noqa: E402

SCRIPT = "scripts/score_fv3_grid.py"
CONFIG = ROOT / "config" / "fv3_grid.yaml"
WF_FIRST, TODAY_FROM = g5.WF_FIRST, g5.TODAY_FROM
AXES = ("sessions", "continuation", "displacement", "double_rung_reversions")
SESSION_NAMES = tuple(s[0] for s in SESSIONS)
MAX_PER_DAY = 5
FLAT_MAX = g5.FLAT_MAX
CAP_MAX = 0.02
STOP_SLIP_TICKS, FLATTEN_SLIP_TICKS = g5.STOP_SLIP_TICKS, g5.FLATTEN_SLIP_TICKS
RR_MENU = (1.0, 1.5, 2.0, 2.5, 3.0)
BENCH_TARGETS = {"r1": 1.0, "r15": 1.5, "r25": 2.5, "r3": 3.0}   # the benchmark settled at each leg's target (D-280 (4); D-301 adds the funded 2.5R; D-306's table takes the funded leg to 3R)


def rr_menu(cfg: dict) -> tuple[float, ...]:
    """The R values the gate's trades carry outcomes at: the config's `fidelity.rr_menu` (D-306: every quarter-R, so a
    Combine trade can close at what the account needs to pass), else the state table's menu."""
    f = cfg.get("fidelity") or {}
    menu = tuple(float(x) for x in f.get("rr_menu", RR_MENU))
    if any(R <= 0 for R in menu) or len(set(menu)) != len(menu) or list(menu) != sorted(menu):
        raise SystemExit(f"REFUSED: fidelity.rr_menu must be distinct, ascending and positive: {menu}.")
    return menu


#: D-312: the campaign's starting cash when the bankroll is an output of the run -- large enough never to bind, the
#: Campaign Studio's own value (SD-04's UNCONSTRAINED_BANKROLL), so the required bankroll is read uncensored
UNBOUND_BANKROLL = 100_000_000.0


def bankroll_output(cfg: dict) -> bool:
    """D-312: whether the gate's bankroll is an output of the run (`gate.campaign.bankroll_mode: output`)."""
    mode = str(cfg["gate"]["campaign"].get("bankroll_mode", "stated"))
    if mode not in ("stated", "output"):
        raise SystemExit(f"REFUSED: gate.campaign.bankroll_mode is 'stated' or 'output', got {mode!r}.")
    return mode == "output"


def bankroll_of(cfg: dict) -> float:
    """The campaign's starting cash: the stated bankroll, or (D-312) cash that never binds when the bankroll is an
    output -- the run then reports the bankroll it needed and the lines read growth on it."""
    if bankroll_output(cfg):
        return UNBOUND_BANKROLL
    return float(cfg["gate"]["campaign"]["bankroll"])


def fidelity_of(cfg: dict) -> dict:
    """D-306's fidelity switches: need-aware Combine exits, and which intention P4 measures the realised risk against."""
    f = cfg.get("fidelity") or {}
    intended = str(f.get("intended", "raw"))
    if intended not in ("raw", "capped"):
        raise SystemExit(f"REFUSED: fidelity.intended is 'raw' or 'capped', got {intended!r}.")
    room = tuple(str(k) for k in (f.get("room_cap") or ()))
    if any(k not in ("combine", "funded") for k in room):
        raise SystemExit(f"REFUSED: fidelity.room_cap names account kinds 'combine' and 'funded' only, got {room!r}.")
    routing = str(f.get("routing", "longest_waiting"))
    if routing not in ("longest_waiting", "able"):
        raise SystemExit(f"REFUSED: fidelity.routing is 'longest_waiting' or 'able', got {routing!r}.")
    costs = str(f.get("costs", "today_median"))
    if costs not in COST_MODES:
        raise SystemExit(f"REFUSED: fidelity.costs is one of {COST_MODES}, got {costs!r}.")
    out = {"need_aware_exits": bool(f.get("need_aware_exits", False)), "intended": intended,
           "consistency_cap_exits": bool(f.get("consistency_cap_exits", False)),   # D-313
           "room_cap": room,                                                        # D-313
           "routing": routing,                                                      # D-318
           "costs": costs}                                                          # D-321, D-324
    if "no_trade_standard_path_only" in f:                                         # D-324
        out["no_trade_standard_path_only"] = bool(f["no_trade_standard_path_only"])
    if "decision_inputs_cents" in f:                                               # D-328
        out["decision_inputs_cents"] = bool(f["decision_inputs_cents"])
    if "cross_account_rule" in f:                                                  # D-339: the firm's rule (D-336 (iv))
        out["cross_account_rule"] = bool(f["cross_account_rule"])
    if "hold_to_own_exit" in f:                                                    # D-351: a position held to its own exit
        out["hold_to_own_exit"] = bool(f["hold_to_own_exit"])
    if "seat_frees" in f:                                                          # D-339: the seat freed (D-336 (i))
        seat = str(f["seat_frees"])
        if seat not in ("next_session", "same_evening"):
            raise SystemExit(f"REFUSED: fidelity.seat_frees is 'next_session' or 'same_evening', got {seat!r}.")
        out["seat_frees"] = seat
    if "xfa_second_trade" in f:                                                    # D-368: FV3-D's second-trade lever
        out["xfa_second_trade"] = bool(f["xfa_second_trade"])
    if f.get("xfa_collect_from") is not None:                                      # D-368: FV3-D's collect-phase lever
        T = float(f["xfa_collect_from"])
        if not (T >= 0 and math.isfinite(T)):
            raise SystemExit(f"REFUSED: fidelity.xfa_collect_from is a balance in dollars, at least 0, got {T!r}.")
        out["xfa_collect_from"] = T
    return out


#: D-321: 'per_trade' -- each trade's own round trip, its fee at the fresh leg's size; D-324: 'per_trade_at_size' -- the
#: fee re-priced in the engine at the contracts each trade holds (as many minis as fit, the rest in micros)
COST_MODES = ("today_median", "per_trade", "per_trade_at_size")


def protocol_params(cfg: dict) -> dict:
    """The protocol's switches the lockstep loop reads (D-306's need-aware exits; D-313's consistency cap; D-324's
    no-trade states for Standard-path accounts only, when declared)."""
    f = fidelity_of(cfg)
    out = {"need_aware_exits": f["need_aware_exits"], "consistency_cap_exits": f["consistency_cap_exits"]}
    if "no_trade_standard_path_only" in f:
        out["no_trade_standard_path_only"] = f["no_trade_standard_path_only"]
    if "decision_inputs_cents" in f:                                               # D-328: the policy reads cents
        out["decision_inputs_cents"] = f["decision_inputs_cents"]
    if "seat_frees" in f:                                                          # D-339: when a funded seat is freed
        out["seat_frees"] = f["seat_frees"]
    if f.get("xfa_second_trade"):                                                  # D-368: only when on, so runs reproduce
        out["xfa_second_trade"] = True
    if f.get("xfa_collect_from") is not None:                                      # D-368: only when declared
        out["xfa_collect_from"] = f["xfa_collect_from"]
    return out


def _select_rows(tab: pd.DataFrame, flt: dict | None) -> pd.DataFrame:
    """The rows of `tab` matching every `column: value` of `flt` (strings compared as text, numbers to float)."""
    sel = tab
    for k, v in (flt or {}).items():
        if k not in sel.columns:
            raise SystemExit(f"REFUSED: the file has no column {k!r} to select the flip's row by.")
        col = sel[k]
        # a numeric column to float, anything else as text (pandas' Arrow-backed strings are not dtype object)
        sel = sel[np.isclose(col.astype(float), float(v)) if pd.api.types.is_numeric_dtype(col) else (col.astype(str) == str(v))]
    return sel


def flip_spec_of(cfg: dict, *, with_info: bool = False):
    """D-339: the flip stream's `FlipSpec` from `streams.flip`, every statistic READ from the result files the block
    names, never typed: the shares at the target, the stop and still open, the cost and the risk a micro from the
    bracket study's pooled row (the same row the table's `funded_flip` reads); the decision slots from the resolution
    map under the declared rule (a slot is taken when its resolved share is at least the minimum overall and, with
    `scope: every_year`, in its worst year), each slot's window its mean minutes to resolution. Refuses when the
    engine's net-edge arithmetic does not reproduce the file's edge field, when the rule's slots are not the slot set
    the study measured its shares on (its manifest's `decision_slots`), or when the table's config names another
    bracket. None without the block; `with_info` adds the provenance for the `flip` rows."""
    s = (cfg.get("streams") or {}).get("flip")
    if not s:
        return (None, {}) if with_info else None
    import hashlib

    from propedge.campaign.flip import FlipSpec
    from propedge.reporting.results import read_result

    if str(s.get("source", "study")) == "flip_map":                 # D-343: the fast, time-boxed bracket's row
        return _flip_spec_from_map(cfg, s, with_info)
    if str(s.get("source", "study")) == "collect_map":              # D-384: the collect menu, priced per period
        return _flip_menu_from_collect(cfg, s, with_info)
    src = ROOT / s["source_file"]
    tab = read_result(src)
    sel = _select_rows(tab, s.get("row"))
    if len(sel) != 1:
        raise SystemExit(f"REFUSED: {s['source_file']} holds {len(sel)} rows for the flip's statistics {s.get('row')}, not one.")
    row = sel.iloc[0]
    sh = s.get("shares") or {}
    p_t, p_s, p_o = (float(row[sh.get("target", "target_share")]), float(row[sh.get("stop", "stop_share")]),
                     float(row[sh.get("open", "open_share")]))
    cost_r = float(row[sh.get("cost", "cost_r")])
    rpc = float(row[sh.get("risk_per_contract", "stop_dollars")])
    edge = float(row[s.get("edge_field", "e_net")])
    lbf = s.get("lower_bound_field", "e_net_lower_bound")
    lb = float(row[lbf]) if lbf in row.index and pd.notna(row[lbf]) else float("nan")
    # the slots: the map's cells under the declared rule
    sfile = ROOT / s["slots_file"]
    cells = _select_rows(read_result(sfile), s.get("slots_row")).sort_values("decision_slot")
    if not len(cells):
        raise SystemExit(f"REFUSED: {s['slots_file']} holds no cell for {s.get('slots_row')}.")
    rule = s["slots_rule"]
    mn = float(rule["resolved_share_min"])
    scope = str(rule.get("scope", "every_year"))
    if scope not in ("pooled", "every_year"):
        raise SystemExit(f"REFUSED: slots_rule.scope is 'pooled' or 'every_year', got {scope!r}.")
    ok = cells["resolved_share"].astype(float) >= mn
    if scope == "every_year":
        ok &= cells["worst_year_share"].astype(float) >= mn
    taken = cells[ok]
    if not len(taken):
        raise SystemExit(f"REFUSED: no slot of {s['slots_file']} resolves at least {mn:.2%} ({scope}); the flip stream has no slot.")
    slots = tuple(int(x) for x in taken["decision_slot"])
    wcol = str(s.get("window", "mean_minutes"))
    minutes = tuple(float(x) for x in taken[wcol])
    # the shares were measured over the study's own slot set: the rule must reproduce it
    man = json.loads(src.with_suffix(src.suffix + ".manifest.json").read_text(encoding="utf-8"))
    measured = [int(x) for x in (man.get("parameters") or {}).get("decision_slots", [])]
    if list(slots) != measured:
        raise SystemExit(f"REFUSED: the slot rule yields {list(slots)}, not the study's decision_slots {measured} the shares "
                         "were measured on; the rule or the file is wrong.")
    spec = FlipSpec(risk=float(s["risk"]), rr=float(s["rr"]), p_target=p_t, p_stop=p_s, p_open=p_o, cost_r=cost_r,
                    risk_per_contract=rpc, slots=slots, mean_minutes=float(np.mean(minutes)), minutes_by_slot=minutes,
                    edge=edge, edge_lower_bound=lb,
                    source=f"{s['source_file']} row {s.get('row')}; slots {s['slots_file']} {s.get('slots_row')} under {rule}")
    if abs(spec.net_edge - edge) > 1e-9:
        raise SystemExit(f"REFUSED: the engine's flip arithmetic gives a net edge of {spec.net_edge:.6f}, the file's "
                         f"{s.get('edge_field', 'e_net')} is {edge:.6f}: the file does not count an open bracket a full loss as "
                         "the engine does, or its cost is not per attempt.")
    # the table's flip action must be this bracket
    tc_path = s.get("table_config")
    if tc_path:
        tc = yaml.safe_load((ROOT / tc_path).read_text(encoding="utf-8"))
        ff = tc.get("funded_flip") or {}
        same = (str(ff.get("source_file")) == str(s["source_file"]) and dict(ff.get("row") or {}) == dict(s.get("row") or {})
                and float(ff.get("risk", float("nan"))) == spec.risk and float(ff.get("rr", float("nan"))) == spec.rr
                and str(ff.get("edge_field", "e_net")) == str(s.get("edge_field", "e_net"))
                and str(ff.get("lower_bound_field", "e_net_lower_bound")) == str(s.get("lower_bound_field", "e_net_lower_bound")))
        if not same:
            raise SystemExit(f"REFUSED: the table's funded_flip in {tc_path} is not the engine's flip stream ({ff} vs {s}).")
    if not with_info:
        return spec
    yearly = _select_rows(tab, {k: v for k, v in (s.get("row") or {}).items() if k != "year"})
    yearly = yearly[yearly["year"].astype(str) != str((s.get("row") or {}).get("year", "pooled"))]
    resolved_by_year = {str(r["year"]): 1.0 - float(r[sh.get("open", "open_share")]) for _, r in yearly.iterrows()}
    worst = min(resolved_by_year, key=resolved_by_year.get) if resolved_by_year else None
    info = {"source_file": str(s["source_file"]), "source_sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
            "source_manifest_decision_slots": measured, "slots_file": str(s["slots_file"]),
            "slots_sha256": hashlib.sha256(sfile.read_bytes()).hexdigest(), "n_slots": len(slots),
            "resolved_share_min": mn, "slots_scope": scope, "cells": cells, "taken": set(slots),
            "resolved_by_year": resolved_by_year, "worst_year": worst,
            "worst_year_resolved_share": resolved_by_year[worst] if worst else float("nan")}
    return spec, info


def _flip_spec_from_map(cfg: dict, s: dict, with_info: bool):
    """D-343: the flip stream's spec from the flip map's result (`scripts/score_flip_map.py`): the row the config names
    (by default the `choice` row the map's declared rules picked) gives the slot, the width in points, the shares at the
    target, the stop and the scratch, the scratches' mean P&L, the cost and the net edge with its bound; the config
    gives the contract's point value, the box and whether the flip is copied. The engine's net-edge arithmetic must
    reproduce the row's `e_net`, the config's risk must be the row's, and the table's config must name the same row."""
    import hashlib

    from propedge.campaign.flip import FlipSpec, slot_from_ct
    from propedge.reporting.results import read_result

    src = ROOT / s["source_file"]
    tab = read_result(src)
    sel = _select_rows(tab, s.get("row"))
    if len(sel) != 1:
        raise SystemExit(f"REFUSED: {s['source_file']} holds {len(sel)} rows for {s.get('row')}, not one.")
    row = sel.iloc[0]
    width = float(row["chosen_width_points"])
    if not np.isfinite(width):
        raise SystemExit(f"REFUSED: the flip map's row {s.get('row')} chose no width: no slot qualified under its rule.")
    pv = float(s.get("contract_point_value", 20.0))
    rpc = width * pv
    risk = float(s["risk"])
    if abs(risk - float(row["risk_dollars"])) > 1e-9:
        raise SystemExit(f"REFUSED: streams.flip.risk {risk} is not the map's risk for the chosen width ({row['risk_dollars']}).")
    p_t, p_s, p_x = float(row["target_share"]), float(row["stop_share"]), float(row["scratch_share"])
    r_x = float(row["scratch_mean_dollars"]) / float(row["risk_dollars"]) if p_x > 0 else 0.0
    edge, lb = float(row["e_net"]), float(row["e_net_lower_bound"]) if pd.notna(row["e_net_lower_bound"]) else float("nan")
    box = float(s["box_minutes"])
    # D-345 (7): the slot on the ENGINE's clock (minutes since 17:00 CT) from the row's clock label; the row's own
    # minute-clock column (or, on a map without one, its `decision_slot`) must agree -- the seconds kit's
    # `decision_slot` is a second offset from its window's start, which the first reader took for the engine's clock
    ct = str(row["decision_ct"])
    slot = slot_from_ct(ct)
    col = "decision_slot_minutes" if ("decision_slot_minutes" in row.index and pd.notna(row["decision_slot_minutes"])) else "decision_slot"
    if int(row[col]) != slot:
        raise SystemExit(f"REFUSED: the flip map's row says {ct} CT but its {col} is {int(row[col])}, not {slot} minutes after "
                         f"17:00 CT on the engine's clock ({s['source_file']}).")
    spec = FlipSpec(risk=risk, rr=float(s["rr"]), p_target=p_t, p_stop=p_s, p_open=0.0, cost_r=float(row["cost_r"]),
                    risk_per_contract=rpc, slots=(slot,), mean_minutes=float(row["mean_minutes"]),
                    edge=edge, edge_lower_bound=lb, p_scratch=p_x, scratch_mean_r=r_x, box_minutes=box,
                    copy=bool(s.get("copy", False)), slot_ct=str(row["decision_ct"]),
                    source=f"{s['source_file']} row {s.get('row')}: {row['decision_ct']} CT, {width:g} points")
    if abs(spec.net_edge - edge) > 1e-9:
        raise SystemExit(f"REFUSED: the engine's flip arithmetic gives {spec.net_edge:.6f}, the map's e_net is {edge:.6f}.")
    # D-346: a map scored under a contract rule names the count it priced; the engine's count (the risk over what one
    # contract risks at the width) must be the same, or the costs in the row are not the costs of the trade
    if "contracts" in row.index and pd.notna(row["contracts"]) and int(row["contracts"]) != spec.contracts():
        raise SystemExit(f"REFUSED: the flip map priced {int(row['contracts'])} contracts, the engine trades {spec.contracts()} "
                         f"(risk {risk:g} over {rpc:g} a contract at {width:g} points x {pv:g}).")
    tc_path = s.get("table_config")
    if tc_path:
        tc = yaml.safe_load((ROOT / tc_path).read_text(encoding="utf-8"))
        ff = tc.get("funded_flip") or {}
        same = (str(ff.get("source_file")) == str(s["source_file"]) and dict(ff.get("row") or {}) == dict(s.get("row") or {})
                and float(ff.get("risk", float("nan"))) == spec.risk and float(ff.get("rr", float("nan"))) == spec.rr
                and str(ff.get("scratch_field", "")) == "scratch_share" and bool(ff.get("copy", False)) == spec.copy)
        if not same:
            raise SystemExit(f"REFUSED: the table's funded_flip in {tc_path} is not the engine's flip stream ({ff} vs {s}).")
    if not with_info:
        return spec
    info = {"source_file": str(s["source_file"]), "source_sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
            "form": "flip_map", "n_slots": 1, "slot_ct": str(row["decision_ct"]), "width_points": width, "contracts": spec.contracts(),
            "instrument": str(row["instrument"]) if "instrument" in row.index and pd.notna(row["instrument"]) else "",
            "resolved_share_min": float(s.get("resolved_in_box_min", float("nan"))),
            "resolved_in_box": float(row["resolved_in_box"]), "resolved_within_5": float(row["resolved_within_5"]),
            "worst_year_resolved_in_box": float(row["worst_year_resolved_in_box"]), "years": int(row["years"]),
            "n": int(row["n"]), "spread_ticks_mean": float(row["spread_ticks_mean"]),
            "late_resolved_in_box": float(row["late_resolved_in_box"]), "late_minus_on_time_e_net": float(row["late_minus_on_time_e_net"]),
            "qualifying_widths": str(row["qualifying_widths"])}
    return spec, info


def _flip_menu_from_collect(cfg: dict, s: dict, with_info: bool):
    """D-384: the collect stream's `FlipMenu` -- the brackets the collect map's `menu` rows name, each priced from the
    capture's counts over `s['years']` (the period the campaign runs on) by the collect scorer's arithmetic; its
    window the bracket's own mean minutes to resolution (no box: D-350 (iii)); its lower-bound arm the target share's
    Wilson bound over the period's days; copied (one shared uniform a day). Refuses a bracket whose engine arithmetic
    does not reproduce its net edge, whose micros are not the map's, or a table config whose `funded_flips` names
    other brackets."""
    import hashlib

    import score_collect_map as scm

    from propedge.campaign.flip import FlipMenu, FlipSpec, slot_from_ct
    from propedge.data import flip_kit as fk
    from propedge.reporting.results import read_result

    q = fk.params_collect()
    files = {k: ROOT / s[k] for k in ("map_file", "counts_file", "spread_file")}
    mp, counts = read_result(files["map_file"]), read_result(files["counts_file"])
    spreads = read_result(files["spread_file"])
    spreads = spreads[spreads["kind"] == "spread"]
    years = [int(y) for y in s["years"]]
    specs, rows = [], []
    for b in scm.menu_brackets(mp):
        st = scm.bracket_stats(counts, spreads, years, b, fee=float(q["fee_round_turn"]), mpv=float(q["micro_point_value"]),
                               tick=float(q["tick"]))
        slot = slot_from_ct(b["decision_ct"])
        if slot != int(b["decision_slot_minutes"]):
            raise SystemExit(f"REFUSED: the collect map's {b['decision_ct']} CT is not slot {int(b['decision_slot_minutes'])}.")
        spec = FlipSpec(risk=float(st["risk_dollars"]), rr=float(st["rr"]), p_target=float(st["target_share"]),
                        p_stop=float(st["stop_share"]), p_open=0.0, cost_r=float(st["cost_r"]),
                        risk_per_contract=float(b["stop_points"]) * float(q["micro_point_value"]), slots=(slot,),
                        mean_minutes=float(st["mean_minutes"]), edge=float(st["e_net"]),
                        edge_lower_bound=float(st["e_net_lower_bound"]), p_scratch=float(st["scratch_share"]),
                        scratch_mean_r=float(st["scratch_mean_dollars"]) / float(st["risk_dollars"]), box_minutes=None,
                        copy=bool(s.get("copy", True)), slot_ct=b["decision_ct"],
                        source=f"{s['counts_file']} over {st['years']}: {b['decision_ct']} CT, {int(b['contracts'])} MNQ, "
                               f"stop {b['stop_multiple']:g}x, box {int(b['box_minutes'])}")
        if abs(spec.net_edge - float(st["e_net"])) > 1e-9:
            raise SystemExit(f"REFUSED: the engine's arithmetic gives {spec.net_edge:.6f} for a collect bracket, the map's "
                             f"arithmetic {st['e_net']:.6f}.")
        if spec.contracts() != int(b["contracts"]):
            raise SystemExit(f"REFUSED: the collect bracket trades {spec.contracts()} micros, the map priced {int(b['contracts'])}.")
        specs.append(spec)
        rows.append({**{k: b[k] for k in scm.MENU_KEYS}, **{k: st[k] for k in ("n", "days", "target_share", "target_share_lb",
                                                                               "stop_share", "scratch_share", "mean_minutes",
                                                                               "cost_dollars", "net_mean", "e_net",
                                                                               "e_net_lower_bound", "risk_dollars", "rr")}})
    menu = FlipMenu(tuple(specs))
    tc_path = s.get("table_config")
    if tc_path:
        tc = yaml.safe_load((ROOT / tc_path).read_text(encoding="utf-8"))
        ff = tc.get("funded_flips") or {}
        same = (str(ff.get("map_file")) == str(s["map_file"]) and str(ff.get("counts_file")) == str(s["counts_file"])
                and bool(ff.get("copy", True)) == menu.copy)
        if not same:
            raise SystemExit(f"REFUSED: the table's funded_flips in {tc_path} is not the engine's collect stream ({ff} vs {s}).")
    if not with_info:
        return menu
    info = {"form": "collect_menu", "years": ",".join(str(y) for y in years), "brackets": rows,
            **{f"{k}_sha256": hashlib.sha256(files[k].read_bytes()).hexdigest() for k in files},
            **{k: str(s[k]) for k in files}}
    return menu, info


def flip_rows(cfg: dict) -> list[dict]:
    """D-339: the `flip` section -- one `bracket` row (the shares, the cost per flip and per winning day, the resolution
    judgements under the declared minimum pooled and in every year of the study, both files' hashes) and one `slot` row
    per cell of the map, taken or not. D-343: for a flip-map bracket, one `bracket` row from the map's chosen row (its
    resolution inside the box pooled and in its worst year against the map's minimum, the late entry beside) and one
    `slot` row. The flip stream is judged here on resolution and cost (its card), never a line. Empty without a flip
    stream."""
    spec, info = flip_spec_of(cfg, with_info=True)
    if spec is None:
        return []
    if info.get("form") == "collect_menu":                         # D-384: one row per bracket of the collect menu
        return [{"section": "flip", "kind": "bracket", "form": "collect_menu", "years": info["years"], **r,
                 "counts_file": info["counts_file"], "counts_file_sha256": info["counts_file_sha256"],
                 "judged_on": "the campaign beside FV3-C by D-382's walk-forward (D-384); reported, never a line"}
                for r in info["brackets"]]
    if info.get("form") == "flip_map":
        from propedge.campaign.flip import slot_from_ct
        from propedge.reporting.results import read_result

        mn = info["resolved_share_min"]
        bracket = {"section": "flip", "kind": "bracket", "form": "flip_map", "risk": spec.risk, "rr": spec.rr, "contracts": spec.contracts(),
                 "risk_per_contract": spec.risk_per_contract, "width_points": info["width_points"], "p_target": spec.p_target,
                 "p_stop": spec.p_stop, "p_scratch": spec.p_scratch, "scratch_mean_r": spec.scratch_mean_r, "cost_r": spec.cost_r,
                 "net_edge": spec.net_edge, "edge_lower_bound": spec.edge_lower_bound,
                 "cost_per_flip": spec.cost_r * spec.risk,                    # D-349 (the v1 audit, finding 12): the cost ...
                 "expected_loss_per_flip": -spec.net_edge * spec.risk,         # ... and the expected net loss, named apart
                 "expected_flips_per_winning_day": (1.0 / spec.p_target) if spec.p_target > 0 else float("nan"),
                 "n_slots": 1, "slots": ",".join(str(x) for x in spec.slots), "slot_ct": info["slot_ct"],
                 "box_minutes": spec.box_minutes, "copy": spec.copy, "mean_minutes": spec.mean_minutes,
                 "resolved_share_min": mn, "resolved_share_pooled": info["resolved_in_box"],
                 "resolution_pooled_ok": bool(np.isfinite(mn) and info["resolved_in_box"] >= mn),
                 "worst_year_resolved_share": info["worst_year_resolved_in_box"],
                 "resolution_every_year_ok": bool(np.isfinite(mn) and info["worst_year_resolved_in_box"] >= mn),
                 "resolved_within_5": info["resolved_within_5"], "late_resolved_in_box": info["late_resolved_in_box"],
                 "late_minus_on_time_e_net": info["late_minus_on_time_e_net"], "years": info["years"], "n": info["n"],
                 "source_file": info["source_file"], "source_sha256": info["source_sha256"],
                 "judged_on": "resolution inside the box and cost (D-343); reported beside the lines, never a line"}
        # D-349 (the v1 audit, finding 11; D-339 (3)): one `slot` row per slot of the map, taken or not
        tab = read_result(ROOT / cfg["streams"]["flip"]["source_file"])
        slots = tab[tab["section"].astype(str) == "slot"]
        out = [bracket]
        for _, r in slots.iterrows():
            ct = str(r["decision_ct"])
            slot = int(r["decision_slot_minutes"]) if ("decision_slot_minutes" in r.index and pd.notna(r["decision_slot_minutes"])) else slot_from_ct(ct)
            chosen = pd.notna(r.get("chosen_width_points"))
            out.append({"section": "flip", "kind": "slot", "slot": slot, "decision_ct": ct,
                        "n": int(r["n"]) if chosen and pd.notna(r.get("n")) else 0,
                        "chosen_width_points": float(r["chosen_width_points"]) if chosen else float("nan"),
                        "contracts": int(r["contracts"]) if chosen and "contracts" in r.index and pd.notna(r["contracts"]) else 0,
                        "risk_dollars": float(r["risk_dollars"]) if chosen and pd.notna(r.get("risk_dollars")) else float("nan"),
                        "resolved_share": float(r["resolved_in_box"]) if chosen else float("nan"),
                        "worst_year_share": float(r["worst_year_resolved_in_box"]) if chosen else float("nan"),
                        "mean_minutes": float(r["mean_minutes"]) if chosen else float("nan"),
                        "cost_r": float(r["cost_r"]) if chosen else float("nan"), "e_net": float(r["e_net"]) if chosen else float("nan"),
                        "taken": bool(slot in spec.slots), "qualifying_widths": str(r.get("qualifying_widths", ""))})
        if len(out) == 1:                                          # a map without `slot` rows: the chosen row's own slot
            out.append({"section": "flip", "kind": "slot", "slot": int(spec.slots[0]), "decision_ct": info["slot_ct"], "n": info["n"],
                        "chosen_width_points": info["width_points"], "contracts": spec.contracts(), "risk_dollars": spec.risk,
                        "resolved_share": info["resolved_in_box"], "worst_year_share": info["worst_year_resolved_in_box"],
                        "mean_minutes": spec.mean_minutes, "cost_r": spec.cost_r, "e_net": spec.edge, "taken": True,
                        "qualifying_widths": info["qualifying_widths"]})
        elif not any(x["taken"] for x in out[1:]):
            raise SystemExit(f"REFUSED: the flip map's slot rows carry no slot {spec.slots[0]} (the chosen one).")
        return out
    pooled = 1.0 - spec.p_open
    rows = [{"section": "flip", "kind": "bracket", "risk": spec.risk, "rr": spec.rr, "contracts": spec.contracts(),
             "risk_per_contract": spec.risk_per_contract, "p_target": spec.p_target, "p_stop": spec.p_stop, "p_open": spec.p_open,
             "cost_r": spec.cost_r, "net_edge": spec.net_edge, "edge_lower_bound": spec.edge_lower_bound,
             "cost_per_flip": spec.cost_r * spec.risk, "expected_loss_per_flip": -spec.net_edge * spec.risk,   # D-349: named apart
             "expected_flips_per_winning_day": (1.0 / spec.p_target) if spec.p_target > 0 else float("nan"),
             "n_slots": info["n_slots"], "slots": ",".join(str(x) for x in spec.slots), "mean_minutes": spec.mean_minutes,
             "resolved_share_min": info["resolved_share_min"], "slots_scope": info["slots_scope"],
             "resolved_share_pooled": pooled, "resolution_pooled_ok": bool(pooled >= info["resolved_share_min"]),
             "worst_year": info["worst_year"], "worst_year_resolved_share": info["worst_year_resolved_share"],
             "resolution_every_year_ok": bool(np.isfinite(info["worst_year_resolved_share"])
                                              and info["worst_year_resolved_share"] >= info["resolved_share_min"]),
             "source_file": info["source_file"], "source_sha256": info["source_sha256"],
             "source_manifest_decision_slots": ",".join(str(x) for x in info["source_manifest_decision_slots"]),
             "slots_file": info["slots_file"], "slots_sha256": info["slots_sha256"],
             "judged_on": "resolution and cost (the card); reported beside the lines, never a line"}]
    for _, c in info["cells"].iterrows():
        slot = int(c["decision_slot"])
        rows.append({"section": "flip", "kind": "slot", "slot": slot, "decision_ct": c.get("decision_ct"), "n": c.get("n"),
                     "resolved_share": float(c["resolved_share"]), "worst_year": c.get("worst_year"),
                     "worst_year_share": float(c["worst_year_share"]), "mean_minutes": float(c["mean_minutes"]),
                     "cost_r": float(c["cost_r"]) if "cost_r" in c.index else float("nan"), "taken": slot in info["taken"]})
    return rows


#: The feasibility every FV3 screen before D-308 applied while its config's wording named only three conditions (the
#: audit of D-307, finding 2): D-154's minimum, the cap share, and ORB5's flatten condition as it then stood (D-212 (2):
#: at most 2 % of a leg's trades at the 15:10 flatten, overall and in every year; a literal here, so the record's
#: configs keep reading as they ran after D-308 raised the ceiling) -- the named 'funded risk sizeable' term being inert.
INHERITED_FEASIBILITY = {"min_setups": "D-154", "cap_share_max": CAP_MAX, "funded_sizeable": False,
                         "flat_share_max": 0.02, "form": "inherited"}


def feasibility_of(cfg: dict) -> dict:
    """The feasibility conditions as declared (D-308: `selection.feasibility` a block naming every condition the scorer
    applies: `min_setups_per_day` (D-154), `cap_share_max`, `funded_sizeable` (every kept funded trade's stop at or
    above the cost floor and buying a whole micro at the fresh funded risk), `flat_share_max` (D-212 (2)'s share; null
    = reported in the `flatten` rows, not enforced)). A config whose wording is the pre-D-308 sentence gets the
    inherited set, so the record's screens read as they ran."""
    f = cfg["selection"]["feasibility"]
    if isinstance(f, str):
        return dict(INHERITED_FEASIBILITY)
    if "cap_share_max" not in f or "flat_share_max" not in f:
        raise SystemExit("REFUSED: selection.feasibility must state cap_share_max and flat_share_max (null = reported, "
                         "not enforced) -- every condition the scorer applies is declared (D-308).")
    fmax = f["flat_share_max"]
    return {"min_setups": str(f.get("min_setups_per_day", "D-154")), "cap_share_max": float(f["cap_share_max"]),
            "funded_sizeable": bool(f.get("funded_sizeable", False)),
            "flat_share_max": None if fmax is None else float(fmax), "form": "declared"}
RUNG_HALF, RUNG_FULL, RUNG_DOUBLE = 0, 1, 2
D47_E_MIN, D47_LB_MIN = 0.10, 0.05                # propsim D-47's research criterion, reported beside every verdict (D-145)
ENTRY_ALLOWANCE_MICROS = 20                       # a fresh XFA's 2 minis (8284223); the Combine's 50 (8284197)
COMBINE_ALLOWANCE_MICROS = 50


def config(path: Path | None = None) -> dict:
    return yaml.safe_load(Path(path or CONFIG).read_text(encoding="utf-8"))


def profile(s) -> np.ndarray:
    """'off:ticks;...' -> an int array of shape (n, 2); empty for no steps."""
    if not isinstance(s, str) or not s:
        return np.zeros((0, 2), int)
    return np.array([[int(y) for y in x.split(":")] for x in s.split(";")], int)


def flat_profile(p: np.ndarray) -> list:
    return p.reshape(-1).tolist()


# ------------------------------------------------------------------------------------------------- the records

def load(rd: Path, runs_dir: Path, cfg: dict) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[int, float]]:
    """(signals, sessions, bench, trading days a year): FOMC days out, the held-back window never read."""
    frames, cells = [], []
    for run in cfg["runs"]:
        f = rd / f"manual_{run.replace('-', '_')}.csv"
        if not f.is_file():
            raise SystemExit(f"REFUSED: {run} is not ingested.")
        t = pd.read_csv(f, low_memory=False)
        cells.append(t[t["kind"] == "session"].assign(run=run))
        frames.append(t[t["kind"] != "session"])
    a = pd.concat(frames, ignore_index=True)
    a["date"] = a["date"].astype(str)
    dt = pd.to_datetime(a["date"]).dt.date
    if (dt >= s3.HELD_BACK).any() or (dt < s3.START).any():
        raise SystemExit("REFUSED: a record outside 2009-06-01 to 2025-06-30 -- the held-back window is never read "
                         "here (D-237).")
    if a[a["kind"] == "day"]["date"].duplicated().any():
        raise SystemExit("REFUSED: a day recorded twice across the runs.")
    sessions = s3.trading_days(pd.concat(cells, ignore_index=True), runs_dir, cfg)
    if sessions is None:
        raise SystemExit("REFUSED: a run record (runs/<run>/ingested.json) is missing: the trading days need it.")
    a = a[~a["date"].isin(s3.fomc_dates(cfg))]
    days = a[a["kind"] == "day"][["date", "base_stop_ticks", "news_day"]]
    ses = a[a["kind"] == "fvsession"].drop(columns=["base_stop_ticks", "news_day"], errors="ignore").merge(
        days, on="date", how="left", validate="many_to_one")
    heads = ses[["date", "session", "stop_ticks", "open_body_ticks", "open_dir"]].rename(
        columns={"stop_ticks": "base_ticks", "open_body_ticks": "open_body", "open_dir": "open_dir_s"})
    sig = a[a["kind"] == "signal"].drop(columns=["stop_ticks", "base_stop_ticks", "news_day", "open_body_ticks", "open_dir"],
                                        errors="ignore").merge(heads, on=["date", "session"], how="left", validate="many_to_one")
    bench = a[a["kind"] == "bench"].drop(columns=["stop_ticks", "base_stop_ticks", "news_day", "open_body_ticks", "open_dir"],
                                         errors="ignore").merge(heads, on=["date", "session"], how="left", validate="many_to_one")
    if sig["base_ticks"].isna().any() or bench["base_ticks"].isna().any():
        raise SystemExit("REFUSED: a signal or benchmark row without its session's base stop.")
    return sig, ses, bench, sessions


class Signals3:
    """Every recorded signal as arrays, in day and time order, with its profiles."""

    def __init__(self, sig: pd.DataFrame, fee_micro: float, fee_mini: float, tick_dollars: float, ladder: dict):
        s = sig.sort_values(["date", "slot"], kind="stable").reset_index(drop=True)
        self.df = s
        self.fm, self.fM, self.td = float(fee_micro), float(fee_mini), float(tick_dollars)
        self.year = pd.to_datetime(s["date"]).dt.year.to_numpy()
        self.day = pd.factorize(s["date"])[0]
        self.session = s["session"].to_numpy()
        f = lambda c: s[c].to_numpy(float)                                       # noqa: E731
        self.slot, self.phase, self.dir, self.bits = f("slot"), f("phase"), f("dir"), f("trigger_bits").astype(int)
        self.room, self.base, self.bar = f("fv_ticks"), f("base_ticks"), f("bar")
        self.open_body = f("open_body")
        self.reanchor, self.swing_bars = f("reanchor").astype(int), f("swing_bars").astype(int)
        self.dfe, self.close, self.worst = f("fv_from_entry_ticks"), f("close_ticks"), f("worst_ticks")
        self.entry2 = f("entry_ticks")
        self.be_open, self.be_fav, self.be_touch = f("be_open_off"), f("be_favour_ticks"), f("be_touch_off")
        sp = f("spread_tenths")
        self.entry_cost = np.where(sp >= 0, np.maximum(1.0, sp / 10.0), 1.0)
        self.fav = [profile(x) for x in s["fav_profile"]]
        self.adv = [profile(x) for x in s["adv_profile"]]
        self.alt = {}
        for L in (0, 5):                     # a CSV reads the codes as numbers: 012 -> 12.0; back to three digits
            codes = s[f"codes_l{L}"].map(lambda x: f"{int(float(x)):03d}").to_numpy()
            if not all(len(c) == 3 and set(c) <= set("0129") for c in codes):
                raise SystemExit(f"REFUSED: a malformed latency-{L} outcome code.")
            self.alt[L] = (s[f"entry_ticks_l{L}"].to_numpy(float), codes)
        # the ladder: each signal's rung from its room. FV3's record scales his 25-point stop by the ATR, so the room is
        # read in base stops; the fidelity protocol (D-306: `mode: fixed_points`) fixes the stops in ticks and reads the
        # room in ticks, expressed here as the same multiples of a 25-point base (100 ticks) so every rule below holds.
        self.fixed_stops: dict[int, float] | None = None
        cont = self.phase == 0
        if str(ladder.get("mode", "atr")) == "fixed_points":
            st = ladder["stops_ticks"]
            self.fixed_stops = {RUNG_HALF: float(st["half"]), RUNG_FULL: float(st["full"]), RUNG_DOUBLE: float(st["double"])}
            rt = ladder["room_ticks"]
            unit = float(rt["full"]) / 1.2                                 # the tick equivalent of one base stop
            self.room_base = self.room / unit
            big_open = self.open_body > float(ladder["continuation_open_body_ticks"]) - 1e-9
            half = (self.room >= float(rt["half"][0]) - 1e-9) & (self.room < float(rt["half"][1]) - 1e-9)
            full = self.room >= float(rt["full"]) - 1e-9
            self.double_room = float(rt["double"]) / unit
        else:
            r = ladder["rungs"]
            self.room_base = np.where(self.base > 0, self.room / np.where(self.base > 0, self.base, 1.0), np.nan)
            big_open = self.open_body > self.base * float(r["double"]["continuation_open_body_frac"]) - 1e-9
            half = (self.room_base >= float(r["half"]["room_min_frac"]) - 1e-9) & (self.room_base < float(r["half"]["room_max_frac"]) - 1e-9)
            full = self.room_base >= float(r["full"]["room_min_frac"]) - 1e-9
            self.double_room = float(ladder.get("double_room_frac", 3.04))     # 76 points at a 25-point base
        self.rung_cont = np.where(big_open, RUNG_DOUBLE, RUNG_FULL)
        self.rung_rev = np.where(half, RUNG_HALF, np.where(full, RUNG_FULL, -1))
        self.room_target_frac = float(ladder["room_target_frac"])
        # `funded_room_min_frac`, declared in FV3's configs, was read and never used (the audit of D-307, finding 6);
        # it is no longer read -- the funded leg's room rule is `permitted` (room >= room_target_frac x the target)
        self.cont = cont

    def rung(self, double_reversions: bool) -> np.ndarray:
        """Each signal's rung under the cell: RUNG_HALF / FULL / DOUBLE, -1 for no rung (too little room)."""
        rev = self.rung_rev.copy()
        if double_reversions:
            rev = np.where((rev >= 0) & (self.room_base >= self.double_room - 1e-9), RUNG_DOUBLE, rev)
        return np.where(self.cont, self.rung_cont, rev)

    def stop_ticks(self, rung: np.ndarray) -> np.ndarray:
        if self.fixed_stops is not None:                                   # D-306: his stops in points, fixed
            fixed = np.where(rung == RUNG_HALF, self.fixed_stops[RUNG_HALF],
                             np.where(rung == RUNG_DOUBLE, self.fixed_stops[RUNG_DOUBLE], self.fixed_stops[RUNG_FULL]))
            return np.where(rung >= 0, fixed, np.nan)
        frac = np.where(rung == RUNG_HALF, 0.5, np.where(rung == RUNG_DOUBLE, 2.0, 1.0))
        return np.where(rung >= 0, np.maximum(1.0, np.floor(frac * self.base + 1e-9)), np.nan)

    def fee(self, stop: np.ndarray, risk: float, cap: int) -> np.ndarray:
        return mini_mix_fee(np.where(stop > 0, stop, 1.0), risk, cap, self.td, self.fm, self.fM)

    def candidates(self, c: dict) -> np.ndarray:
        """The cell's admissible signals: its sessions, continuation where taken, the trigger rule, a rung, a fill."""
        in_ses = np.isin(self.session, list(c["sessions"]))
        cont_ok = (~self.cont) | bool(c["continuation"])
        if c["displacement"] == "off":
            trig = (self.bits & 1) > 0
        else:                                                                   # the rule: a displacement only close to fair
            trig = ((self.bits & 1) > 0) | (((self.bits & 2) > 0) & (self.cont | (self.room_base < float(
                self.room_base_half_max) - 1e-9)))
        rung = self.rung(bool(c["double_rung_reversions"]))
        return in_ses & cont_ok & trig & (rung >= 0) & (self.bar != NONE) & (self.base > 0)

    @property
    def room_base_half_max(self) -> float:
        return 1.2

    def outcome(self, rung: np.ndarray, target: str, R: float | None, risk: float, cap: int) -> dict[str, np.ndarray]:
        """Every signal's outcome at the rung's stop and `target` ('r' at R, or 'fv' fair value's near edge, 2.5R
        for a continuation or where fair value is behind): settled from the profiles with his breakeven rule; the
        room rule in `permitted`."""
        n = len(self.bar)
        st = self.stop_ticks(rung)
        safe = np.where(np.isfinite(st) & (st > 0), st, 1.0)
        if target == "r":
            won = np.floor(R * safe + 1e-9)
            rr = np.full(n, float(R))
        else:
            to_fv = (self.phase == 1) & (self.dfe > 0)
            won = np.where(to_fv, self.dfe, np.floor(2.5 * safe + 1e-9))
            rr = np.where(to_fv, self.dfe / safe, 2.5)
        permitted = np.isfinite(st) & ((self.phase == 0) | (self.room + 1e-9 >= self.room_target_frac * won))
        exit_off = np.full(n, float(NONE))
        kind = np.zeros(n, int)                   # 0 stop, 1 target, 2 flatten, 3 breakeven
        mae = np.zeros(n)
        for i in range(n):
            if not permitted[i] or self.bar[i] == NONE:
                continue
            fav, adv = flat_profile(self.fav[i]), flat_profile(self.adv[i])
            off, k, m = settle(fav, adv, int(safe[i]), float(won[i]))
            # breakeven: open at the next session's open with that open in favour -> the stop moves to the entry
            bo = self.be_open[i]
            if bo != NONE and self.be_fav[i] > 0 and (off == NONE or bo < off):
                touch = self.be_touch[i]
                js = next((fav[j] for j in range(0, len(fav), 2) if fav[j + 1] > won[i]), NONE)
                if touch != NONE and (js == NONE or touch < js):
                    off, k = touch, "breakeven"
                    m = max([adv[j + 1] for j in range(0, len(adv), 2) if adv[j] <= touch] or [0])
                elif js != NONE:
                    off, k = js, "target"
                    m = max([adv[j + 1] for j in range(0, len(adv), 2) if adv[j] <= js] or [0])
                else:
                    off, k = NONE, "open"
                    m = max([adv[j + 1] for j in range(0, len(adv), 2)] or [0])
            exit_off[i] = off
            kind[i] = {"stop": 0, "target": 1, "open": 2, "breakeven": 3}[k]
            mae[i] = m
        stopped, hit, flat, be = kind == 0, kind == 1, kind == 2, kind == 3
        flat_move = np.where(self.worst != MISSING_FV, self.worst - FLATTEN_SLIP_TICKS, self.close)
        move = np.where(stopped, -safe, np.where(hit, won, np.where(be, 0.0, flat_move)))
        gross = np.where(permitted, move / safe, np.nan)
        exit_slot = np.where(exit_off != NONE, self.bar + exit_off, FLAT_ENTRY)
        exit_ticks = np.where(stopped | be, STOP_SLIP_TICKS, np.where(hit, 0.0, FLATTEN_SLIP_TICKS))
        cost = (self.entry_cost * self.td + self.fee(safe, risk, cap) + exit_ticks * self.td) / (safe * self.td)
        return {"gross": gross, "cost": cost, "net": gross - cost, "flat": flat & permitted, "stopped": stopped & permitted,
                "target": hit & permitted, "breakeven": be & permitted, "exit": exit_slot, "rr": rr, "mae_r": mae / safe,
                "stop": st, "permitted": permitted}

    def today_cost(self, cand: np.ndarray, stop: np.ndarray, risk: float, cap: int) -> float:
        sel = cand & (self.year >= TODAY_FROM) & np.isfinite(stop)
        safe = np.where(np.isfinite(stop) & (stop > 0), stop, 1.0)
        c = (self.entry_cost * self.td + self.fee(safe, risk, cap) + STOP_SLIP_TICKS * self.td) / (safe * self.td)
        return float(np.median(c[sel])) if sel.any() else float("nan")

    def kept(self, cand: np.ndarray, exit_slot: np.ndarray, stopped: np.ndarray | None = None,
             two_losses_bos_only: bool = False) -> np.ndarray:
        """Per day in signal order: a trade only after the previous one's exit bar, at most five a day; under the
        rule, after two consecutive losses in a session only a break of structure is taken."""
        out = np.zeros(len(cand), bool)
        idx = np.nonzero(cand)[0]
        day, bar, ex = self.day[idx], self.bar[idx], exit_slot[idx]
        cur, busy, n = -1, -1.0, 0
        ses_cur, losses = None, 0
        for k in range(len(idx)):
            i = idx[k]
            if day[k] != cur:
                cur, busy, n = day[k], -1.0, 0
                ses_cur, losses = None, 0
            if self.session[i] != ses_cur:
                ses_cur, losses = self.session[i], 0
            if n >= MAX_PER_DAY or bar[k] <= busy:
                continue
            if two_losses_bos_only and losses >= 2 and not (self.bits[i] & 1):
                continue
            out[i] = True
            busy, n = ex[k], n + 1
            if stopped is not None:
                losses = losses + 1 if stopped[i] else 0
        return out


# ------------------------------------------------------------------------------------------ the grid's statistics

def cells(cfg: dict) -> list[dict]:
    s = cfg["search"]
    out = []
    for a, ses in enumerate(s["sessions"]):
        for b, cont in enumerate(s["continuation"]):
            for c_, disp in enumerate(s["displacement"]):
                for d, dbl in enumerate(s["double_rung_reversions"]):
                    out.append({"idx": (a, b, c_, d), "sessions": tuple(ses), "continuation": bool(cont),
                                "displacement": str(disp), "double_rung_reversions": bool(dbl)})
    return out


def leg_spec(cfg: dict, leg: str) -> tuple[str, float, float, int]:
    """(target, R, risk, cap micros) of the fresh-account geometry the behaviour steps score (the state table's)."""
    g = cfg["state_policy"]["fresh"]
    if leg == "combine":
        return "r", float(g["combine_rr"]), float(g["combine_risk"]), COMBINE_ALLOWANCE_MICROS
    return "r", float(g["funded_rr"]), float(g["funded_risk"]), ENTRY_ALLOWANCE_MICROS


def leg_stats(S: Signals3, c: dict, cand: np.ndarray, spec: tuple, years: np.ndarray) -> tuple[dict, dict]:
    target, R, risk, cap = spec
    rung = S.rung(bool(c["double_rung_reversions"]))
    o = S.outcome(rung, target, R, risk, cap)
    cand = cand & o["permitted"]
    kept = S.kept(cand, o["exit"], o["stopped"], two_losses_bos_only=(c["displacement"] == "rule"))
    tc = S.today_cost(cand, o["stop"], risk, cap)
    k = np.nonzero(kept)[0]
    yi = np.searchsorted(years, S.year[k])
    metric = o["gross"][k] - tc
    dirs = S.dir[k]
    ny = len(years)

    def bc(w=None, mask=None):
        idx, ww = (yi, w) if mask is None else (yi[mask], None if w is None else w[mask])
        return np.bincount(idx, weights=ww, minlength=ny).astype(float)
    stats = {"n": bc(), "metric": bc(metric), "gross": bc(o["gross"][k]), "net": bc(o["net"][k]),
             "flat": bc(o["flat"][k].astype(float)), "n_long": bc(mask=dirs > 0), "metric_long": bc(metric, dirs > 0),
             "n_short": bc(mask=dirs < 0), "metric_short": bc(metric, dirs < 0), "today_cost": tc}
    return stats, {"k": k, "metric": metric, "o": o, "tc": tc, "kept": kept, "rung": rung}


class EvaluatedFV3(g5.Evaluated):
    """Every cell's two legs' per-year statistics (cells x years) and the static feasibility."""

    def __init__(self, S: Signals3, ses: pd.DataFrame, cfg: dict, sessions: dict[int, float], band: pd.DataFrame,
                 need: float):
        from orb5_prep import sizeable

        self.cfg, self.S = cfg, S
        self.cells = cells(cfg)
        self.years = np.array(sorted(sessions))
        ny, nc = len(self.years), len(self.cells)
        cb = band[(band["state"] == "combine") & (band["market"] == "NQ")].iloc[0]
        today_days = sum(v for y, v in sessions.items() if y >= TODAY_FROM)
        accounts = int(cfg["gate"]["campaign"]["accounts"])
        self.capped = {}
        yr = pd.to_datetime(ses["date"]).dt.year
        for sset in cfg["search"]["sessions"]:
            x = ses[(yr >= TODAY_FROM) & (ses["present"] == 1) & ses["session"].isin(sset)]
            self.capped[tuple(sset)] = float((x["signals_beyond_cap"] > 0).mean()) if len(x) else 1.0
        self.mat = {leg: {k: np.zeros((nc, ny)) for k in ("n", "metric", "gross", "net", "flat", "n_long",
                                                           "metric_long", "n_short", "metric_short")}
                    for leg in ("combine", "funded")}
        self.tc = {leg: np.full(nc, np.nan) for leg in ("combine", "funded")}
        self.feas = feasibility_of(cfg)
        self.need = float(need)
        self.static_ok = np.zeros(nc, bool)
        self.freq = np.zeros(nc)
        self.funded_sizeable = np.full(nc, np.nan)       # D-308: the share of kept funded trades the fresh funded risk can size
        self.frisk = {}
        c_spec = leg_spec(cfg, "combine")
        f_spec = leg_spec(cfg, "funded")
        floor_ticks = int(cfg["state_policy"]["stand_aside"]["combine"]["floor_ticks"])
        f_floor = int(cfg["state_policy"]["stand_aside"].get("funded", {}).get("floor_ticks", floor_ticks))
        for k, c in enumerate(self.cells):
            cand = S.candidates(c)
            cs, ct = leg_stats(S, c, cand, c_spec, self.years)
            fs, ft = leg_stats(S, c, cand, f_spec, self.years)
            for leg, s in (("combine", cs), ("funded", fs)):
                for name, m in self.mat[leg].items():
                    m[k] = s[name]
                self.tc[leg][k] = s["today_cost"]
            kk = ct["k"]
            today = S.year[kk] >= TODAY_FROM
            st = ct["o"]["stop"][kk]
            # D-301: the frequency rule sizes at the Combine's full allowance (D-289) over the declared cost floor,
            # not the stop band's 37-micro cap (D-298's audit, finding 3)
            sized = sizeable(np.where(np.isfinite(st), st, 1.0), c_spec[2], int(c_spec[3]), float(cb["tick_value"]),
                             floor_ticks)
            self.freq[k] = float((today & sized).sum()) / today_days / accounts if today_days else 0.0
            # D-308: the 'funded risk sizeable' term made live -- every kept funded trade's stop at or above the funded
            # cost floor and buying at least one whole micro at the fresh funded risk (the entry allowance aside)
            fst = ft["o"]["stop"][ft["k"]]
            f_ok = np.isfinite(fst) & (fst >= f_floor - 1e-9) & (f_spec[2] + 1e-9 >= fst * S.td)
            self.funded_sizeable[k] = float(f_ok.mean()) if len(fst) else float("nan")
            self.static_ok[k] = bool(self.freq[k] + 1e-9 >= need
                                     and self.capped[tuple(c["sessions"])] <= self.feas["cap_share_max"] + 1e-12
                                     and (not self.feas["funded_sizeable"] or self.funded_sizeable[k] >= 1.0 - 1e-9))
        self.shape = tuple(len(cfg["search"][a]) for a in AXES)

    def _flat_fail(self, ymask: np.ndarray) -> dict[str, np.ndarray]:
        """Per leg, the cells whose flatten share exceeds the declared maximum overall or in a year of `ymask`."""
        fmax = self.feas["flat_share_max"]
        out = {}
        for leg in ("combine", "funded"):
            m = self.mat[leg]
            n, fl = m["n"][:, ymask], m["flat"][:, ymask]
            if fmax is None:
                out[leg] = np.zeros(len(self.cells), bool)
                continue
            share = np.where(n > 0, fl / np.maximum(n, 1), 0.0)
            overall = fl.sum(axis=1) / np.maximum(n.sum(axis=1), 1)
            out[leg] = (overall > fmax + 1e-12) | (share > fmax + 1e-12).any(axis=1)
        return out

    def values(self, ymask: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """(feasible, value) of every cell on the years of `ymask`: the declared conditions (D-308) and a defined value;
        the flatten condition only when `flat_share_max` is declared."""
        ok = self.static_ok.copy()
        ff = self._flat_fail(ymask)
        vals = []
        for leg in ("combine", "funded"):
            m = self.mat[leg]
            n = m["n"][:, ymask]
            has = n > 0
            ok &= ~ff[leg]
            means = np.where(has, m["metric"][:, ymask] / np.maximum(n, 1), np.nan)
            vals.append(g5.bound_rows(means, has))
        v = np.fmin(vals[0], vals[1])
        v = np.where(np.isnan(vals[0]) | np.isnan(vals[1]), np.nan, v)
        return ok & ~np.isnan(v), v

    def reasons(self, ymask: np.ndarray) -> list[str]:
        """Per cell, why it is infeasible on the years of `ymask` ('' when feasible): every failing declared condition."""
        ok, v = self.values(ymask)
        ff = self._flat_fail(ymask)
        fmax = self.feas["flat_share_max"]
        out = []
        for k, c in enumerate(self.cells):
            why = []
            if self.freq[k] + 1e-9 < self.need:
                why.append(f"min_setups_per_day: {self.freq[k]:.4f} < {self.need:g} (D-154)")
            if self.capped[tuple(c["sessions"])] > self.feas["cap_share_max"] + 1e-12:
                why.append(f"cap_share: {self.capped[tuple(c['sessions'])]:.4f} > {self.feas['cap_share_max']:g}")
            if self.feas["funded_sizeable"] and not self.funded_sizeable[k] >= 1.0 - 1e-9:
                why.append(f"funded_sizeable: {self.funded_sizeable[k]:.4f} of the kept funded trades < 1")
            for leg in ("combine", "funded"):
                if ff[leg][k]:
                    m = self.mat[leg]
                    n, fl = m["n"][k][ymask], m["flat"][k][ymask]
                    yrs = self.years[ymask]
                    worst = max(((fl[i] / n[i]) if n[i] else 0.0, int(yrs[i])) for i in range(len(yrs)))
                    why.append(f"flat_share {leg}: {worst[0]:.4f} in {worst[1]} > {fmax:g} (D-212 (2))")
            if np.isnan(v[k]):
                why.append("value undefined (a leg without trades in a year)")
            out.append("; ".join(why) if not ok[k] else "")
        return out

    def flatten_rows(self, k: int) -> list[dict]:
        """D-308: the cell's flatten shares per leg, per year and overall -- reported whether or not enforced."""
        fmax = self.feas["flat_share_max"]
        rows = []
        for leg in ("combine", "funded"):
            m = self.mat[leg]
            n, fl = m["n"][k], m["flat"][k]
            for y, nn, ff in zip(self.years, n, fl):
                rows.append({"section": "flatten", **_key(self.cells[k]), "leg": leg, "year": int(y), "n": int(nn),
                             "flattened": int(ff), "share": float(ff / nn) if nn else float("nan"),
                             "enforced": fmax is not None, "max_share": fmax})
            rows.append({"section": "flatten", **_key(self.cells[k]), "leg": leg, "year": "all", "n": int(n.sum()),
                         "flattened": int(fl.sum()), "share": float(fl.sum() / n.sum()) if n.sum() else float("nan"),
                         "enforced": fmax is not None, "max_share": fmax})
        return rows

    def select(self, ymask: np.ndarray) -> tuple[int | None, float]:
        """No axis is ordered: the feasible cell with the highest value; ties to the earlier. One declared cell (D-310)
        is taken wherever it is feasible on the years of `ymask` under the declared conditions, without the
        yearly-means statistic, which one development year cannot give (D-309's finding 1: 2021 untraded)."""
        if len(self.cells) == 1:
            ff = self._flat_fail(ymask)
            ok1 = bool(self.static_ok[0] and not ff["combine"][0] and not ff["funded"][0])
            _, v = self.values(ymask)
            return (0, float(v[0])) if ok1 else (None, float("nan"))
        ok, v = self.values(ymask)
        score = np.where(ok, v, -np.inf)
        if not ok.any():
            return None, float("nan")
        best = int(np.argmax(score))
        return best, float(score[best])


# ---------------------------------------------------------------------------------------- the mechanics report

def mechanics(S: Signals3, bench_means: dict, cfg: dict, sessions: dict[int, float]) -> list[dict]:
    """Every trigger the primary family can admit (all sessions, both phases, either trigger, any rung), at the full
    rung's stop and the Combine's fresh geometry, grouped by the declared keys; descriptive."""
    mc = cfg["mechanics_report"]
    c_all = {"sessions": SESSION_NAMES, "continuation": True, "displacement": "rule", "double_rung_reversions": False}
    cand = S.candidates(c_all)
    rung = S.rung(False)
    spec = leg_spec(cfg, "combine")
    o15 = S.outcome(rung, "r", 1.5, spec[2], spec[3])
    o1 = S.outcome(rung, "r", 1.0, spec[2], spec[3])
    ofv = S.outcome(rung, "fv", None, spec[2], spec[3])
    tc = S.today_cost(cand, o1["stop"], spec[2], spec[3])
    base_ok = cand & o1["permitted"]
    bm = bench_at(bench_means, "r1", S, np.arange(len(S.bar)), rung)
    # D-308: the eras as declared (the audit of D-307, finding 4), and the whole span
    yrs = sorted(int(y) for y in sessions)
    era_of = {}
    for e in mc.get("eras", []):
        lo, hi = (int(x) for x in str(e).split("-"))
        era_of[str(e)] = (lo, hi)
    era_of["all"] = (yrs[0], yrs[-1]) if yrs else (0, 0)
    band = np.where(S.cont, "cont", np.where(S.room_base < 1.2, "half", np.where(S.room_base < 2.0, "full", np.where(
        S.room_base < 3.04, "funded", "wide"))))
    trig = np.where((S.bits & 1) > 0, np.where((S.bits & 2) > 0, "both", "bos"), "disp")
    sb = np.where(S.swing_bars >= 3, "3+", S.swing_bars.astype(str))
    rows = []
    keys = pd.DataFrame({"phase": np.where(S.cont, "continuation", "reversion"), "trigger": trig, "session": S.session,
                         "band": band, "swing": sb, "reanchor": S.reanchor})
    for era, (lo, hi) in era_of.items():
        em = (S.year >= lo) & (S.year <= hi) & base_ok
        days = sum(n for y, n in sessions.items() if lo <= y <= hi)
        for group in (["phase"], ["phase", "trigger"], ["phase", "session"], ["phase", "band"], ["phase", "trigger", "swing"],
                      ["phase", "reanchor"], ["phase", "trigger", "session"]):
            for vals, idx in keys[em].groupby(group).groups.items():
                i = np.asarray(idx)
                if len(i) < int(mc["min_trades"]):
                    continue
                g1, g15 = o1["gross"][i], o15["gross"][i]
                yr = S.year[i]
                ex = g1 - bm[i]
                row = {"section": "mechanics", "era": era, "group": "+".join(group),
                       **{k: (v if isinstance(vals, tuple) else vals) for k, v in zip(group, vals if isinstance(vals, tuple) else (vals,))},
                       "n": int(len(i)), "per_day": float(len(i) / days) if days else float("nan"),
                       "gross_e_1r": float(np.nanmean(g1)), "net_e_1r_today": float(np.nanmean(g1) - tc),
                       "bound_1r": g5.bound(pd.Series(g1).groupby(yr).mean()),
                       "hit_rate_1r": float(np.nanmean(o1["target"][i])), "mean_r_1p5": float(np.nanmean(g15)),
                       "mean_r_fv": float(np.nanmean(ofv["gross"][i][ofv["permitted"][i]])) if ofv["permitted"][i].any() else float("nan"),
                       "share_at_target_fv": float(np.mean(ofv["target"][i][ofv["permitted"][i]])) if ofv["permitted"][i].any() else float("nan"),
                       "median_mae_r": float(np.nanmedian(o1["mae_r"][i])),
                       "share_breakeven": float(np.nanmean(o1["breakeven"][i])),
                       "excess_vs_benchmark_1r": float(np.nanmean(ex)), "excess_bound": g5.bound(pd.Series(ex).groupby(yr).mean()),
                       "unmatched": int(np.isnan(bm[i]).sum())}
                rows.append(row)
    rows.append({"section": "mechanics", "era": "all", "group": "today_cost", "net_e_1r_today": tc})
    return rows


# ------------------------------------------------------------------------------------------------- the benchmark

def bench_targets(cfg: dict) -> dict[str, float]:
    """The targets the drift benchmark is settled at: BENCH_TARGETS and (D-316) each fresh leg's R where it is not
    among them -- a leg's B line compares its trades with the benchmark at its own target."""
    out = dict(BENCH_TARGETS)
    fresh = cfg["state_policy"]["fresh"]
    for R in (float(fresh["combine_rr"]), float(fresh["funded_rr"])):
        if R not in out.values():
            out[f"r{R:g}"] = R
    return out


def bench_means(bench: pd.DataFrame, fixed_stops: dict[int, float] | None = None,
                targets: dict[str, float] | None = None) -> dict[str, Any]:
    """The unconditional entries' mean move in R per (year, side, session, slot) at each benchmark target, settled from
    their own profiles at the session's ATR base stop -- or, under the fixed-point ladder (D-308; the audit of D-307,
    finding 5), at each rung's fixed stop, keyed by (year, side, session, slot, rung) so a trade is compared with the
    benchmark settled at its own rung's stop, as the config declares."""
    targets = dict(BENCH_TARGETS if targets is None else targets)
    rows: dict[str, list] = {name: [] for name in targets}
    yr = pd.to_datetime(bench["date"]).dt.year.to_numpy()
    stops = sorted(fixed_stops.items()) if fixed_stops else None
    for i, r in enumerate(bench.itertuples(index=False)):
        fav, adv = flat_profile(profile(r.fav_profile)), flat_profile(profile(r.adv_profile))
        flat = (r.bench_worst_ticks - FLATTEN_SLIP_TICKS) if r.bench_worst_ticks != MISSING_FV else r.bench_close_ticks
        for rung, st in (stops if stops else [(None, float(r.base_ticks))]):
            if not st > 0:
                continue
            for name, R in targets.items():
                won = math.floor(R * st + 1e-9)
                _, kind, _ = settle(fav, adv, int(st), float(won))
                g = -1.0 if kind == "stop" else (won / st if kind == "target" else flat / st)
                key = (yr[i], int(r.side), r.session, int(r.bench_after)) + ((int(rung),) if rung is not None else ())
                rows[name].append(key + (g,))
    out: dict[str, Any] = {"_rung_keyed": stops is not None, "_targets": targets}
    cols = ["year", "side", "session", "slot"] + (["rung"] if stops else [])
    for name, rs in rows.items():
        t = pd.DataFrame(rs, columns=cols + ["gross"])
        out[name] = t.groupby(cols)["gross"].mean()
    return out


def bench_at(means: dict[str, Any], name: str, S: Signals3, kk: np.ndarray, rung: np.ndarray) -> np.ndarray:
    """Each signal in `kk`'s benchmark mean at target `name`: by its year, side, session and the latest benchmark slot
    before its bar, and (fixed-point ladder) its rung."""
    slot = bench_slot(S.session[kk], S.bar[kk])
    side = S.dir[kk].astype(int)
    m = means[name]
    if means.get("_rung_keyed"):
        return np.array([m.get((y, sd, ses, sl, int(rg)), np.nan) for y, sd, ses, sl, rg in
                         zip(S.year[kk], side, S.session[kk], slot, rung[kk])], dtype=float)
    return np.array([m.get((y, sd, ses, sl), np.nan) for y, sd, ses, sl in zip(S.year[kk], side, S.session[kk], slot)],
                    dtype=float)


def bench_slot(session: np.ndarray, bar: np.ndarray) -> np.ndarray:
    out = np.full(len(bar), -1)
    for i, (s, b) in enumerate(zip(session, bar)):
        prior = [x for x in BENCH[s] if x < b]
        out[i] = max(prior) if prior else -1
    return out


def drift_value(S: Signals3, means: dict, ev: EvaluatedFV3, k: int) -> tuple[list[dict], float]:
    c = ev.cells[k]
    cand = S.candidates(c)
    rows, vals = [], []
    for leg in ("combine", "funded"):
        spec = leg_spec(ev.cfg, leg)
        _, tr = leg_stats(S, c, cand, spec, ev.years)
        kk, o = tr["k"], tr["o"]
        which = next((name for name, R in means.get("_targets", BENCH_TARGETS).items() if R == float(spec[1])), None)
        if which is None:
            raise SystemExit(f"REFUSED: no benchmark settled at the {leg} leg's target {spec[1]:g}R (D-280 (4)).")
        side = S.dir[kk].astype(int)
        bm = bench_at(means, which, S, kk, tr["rung"])
        ex = o["gross"][kk] - bm
        b = g5.bound(pd.Series(ex).groupby(S.year[kk]).mean())
        vals.append(b)
        for name, mk in (("long", side > 0), ("short", side < 0), ("combined", np.ones(len(kk), bool))):
            rows.append({"section": "drift", "leg": leg, "side": name, "trades": int(mk.sum()),
                         "e_metric": float(tr["metric"][mk].mean()) if mk.any() else float("nan"),
                         "benchmark_gross": float(np.nanmean(bm[mk])) if mk.any() else float("nan"),
                         "excess": float(np.nanmean(ex[mk])) if mk.any() else float("nan"),
                         "excess_bound": g5.bound(pd.Series(ex[mk]).groupby(S.year[kk][mk]).mean()) if mk.any()
                         else float("nan"),
                         "unmatched": int(np.isnan(bm[mk]).sum())})
    value = float(np.fmin(vals[0], vals[1])) if not any(np.isnan(vals)) else float("nan")
    rows.append({"section": "drift", "leg": "value", "excess_bound": value})
    return rows, value


# ------------------------------------------------------------------------------------------------------ the gate

def gate_trades(S: Signals3, ev: EvaluatedFV3, selections: dict[int, int | None], final: dict) -> pd.DataFrame:
    """Each test year's out-of-sample trades of the selection made on the years before it, kept by the fresh
    Combine geometry's exits (one at a time), with every R of the menu's outcome and MAE beside (D-162): the engine
    picks R and risk by state; an R the room does not permit is no trade for that account (NaN). Costs: today's median
    round trip priced as a stop exit, the same for every trade (D-271, D-276); under `fidelity.costs: per_trade`
    (D-321) each trade's own -- its entry spread, its fee at the leg's size, and the exit its outcome at that R took:
    a tick on a stop or a breakeven, none at a target, two on the flatten."""
    out = []
    c_spec = leg_spec(ev.cfg, "combine")
    menu = rr_menu(ev.cfg)
    costs = fidelity_of(ev.cfg)["costs"]
    per_trade = costs in ("per_trade", "per_trade_at_size")   # D-321: each trade's own cost by its exit at each R
    at_size = costs == "per_trade_at_size"                     # D-324: the fee in it, for the engine to re-price
    for y, k in selections.items():
        if k is None:
            continue
        c = ev.cells[k]
        cand = S.candidates(c)
        rung = S.rung(bool(c["double_rung_reversions"]))
        base = S.outcome(rung, "r", c_spec[1], c_spec[2], c_spec[3])
        kept = S.kept(cand & base["permitted"], base["exit"], base["stopped"],
                      two_losses_bos_only=(c["displacement"] == "rule")) & (S.year == y)
        per_r = {R: S.outcome(rung, "r", R, c_spec[2], c_spec[3]) for R in menu}
        tcs = {R: S.today_cost(cand, per_r[R]["stop"], c_spec[2], c_spec[3]) for R in menu}
        st = base["stop"]
        fee_base = S.fee(np.where(np.isfinite(st) & (st > 0), st, 1.0), c_spec[2], c_spec[3]) if at_size else None
        for i in np.nonzero(kept)[0]:
            row = {"date": S.df["date"].iat[i], "year": y, "entry_t": float(S.bar[i]), "exit_t": float(base["exit"][i]),
                   "flat": bool(base["flat"][i]), "stop_ticks": float(base["stop"][i]),
                   "side": "long" if float(S.dir[i]) > 0 else "short"}    # D-348: the signal's side, for the cross-account rule
            for R in menu:
                o = per_r[R]
                ok = bool(o["permitted"][i])
                cost = float(o["cost"][i]) if per_trade else float(tcs[R])
                row[f"r_{R:g}"] = float(o["gross"][i] - cost) if ok else float("nan")
                row[f"mae_{R:g}"] = float(o["mae_r"][i]) if ok else float("nan")
                row[f"exit_t_{R:g}"] = float(o["exit"][i]) if ok else float("nan")   # D-349: the exit at this R, for the rule
            if at_size:
                row["fee_micro_eq"] = float(fee_base[i])            # D-324: the fee a micro-equivalent priced in
            out.append(row)
    return pd.DataFrame(out)


def trade_keys(t: pd.DataFrame) -> list[float]:
    """The R values a gate-trades table carries (its `r_<R>` columns), ascending."""
    return sorted(float(c[2:]) for c in t.columns if c.startswith("r_") and c[2:].replace(".", "", 1).isdigit())


def gate_blocks(t: pd.DataFrame, days: list[str], tick_value: float, keys: Sequence[float] | None = None, *,
                require_sides: bool = False, require_exits: bool = False):
    """One block a trading day, trades in entry order; each trade's risk per micro its own stop (today's regime by
    the era rule enters through the policy's edge); outcomes and MAE at every R for the engine's policy (D-162).
    `keys`: the R values to carry; None reads them from the table's columns. D-339 / D-348: each trade's side reaches
    the block from a `side` column (long / short) or a `dir` column (+1 / -1); `require_sides` -- set when the
    config declares the cross-account rule -- refuses a table that carries neither, so a declared rule can never run
    as a silent no-op (run fv3_gf_v1 did exactly that: `gate_trades` carried no side and no signal was ever refused)."""
    from propedge.outcomes.distribution import DayBlock

    side_col = "side" if "side" in t.columns else ("dir" if "dir" in t.columns else None)
    if require_sides and side_col is None and len(t):
        raise SystemExit("REFUSED: the cross-account rule is declared but the gate's trades carry no side (neither a `side` "
                         "nor a `dir` column): the rule would run as a no-op (D-348).")
    keys_all = [float(R) for R in (trade_keys(t) if keys is None else keys)]
    has_exits = bool(len(t)) and all(f"exit_t_{k:g}" in t.columns for k in keys_all)
    if (require_sides or require_exits) and len(t) and not has_exits:
        raise SystemExit("REFUSED: the cross-account rule or the holding to each trade's own exit is declared but the gate's "
                         "trades carry no exit time at each R (`exit_t_<R>`): a position would be held only to the log's "
                         "single exit (D-349, D-351).")

    def sides_of(g: pd.DataFrame):
        if side_col == "side":
            return np.where(g["side"].astype(str).str.lower() == "long", 1, -1).astype(int)
        if side_col == "dir":
            return np.where(pd.to_numeric(g["dir"], errors="coerce").to_numpy(float) > 0, 1, -1).astype(int)
        return None

    by = {d: g.sort_values("entry_t", kind="stable") for d, g in t.groupby("date")} if len(t) else {}
    blocks = []
    keys = [float(R) for R in (trade_keys(t) if keys is None else keys)]
    for d in days:
        g = by.get(d)
        if g is None or not len(g):
            z = np.zeros(0)
            blocks.append(DayBlock(pnl=z, risked=z, exit_reasons=(), risk_per_contract=z, mae=z, entry_t=z, exit_t=z,
                                   r_by_rr={k: z for k in keys}, mae_by_rr={k: z for k in keys}, sides=np.zeros(0, int)))
            continue
        rpc = g["stop_ticks"].to_numpy(float) * tick_value
        r1 = g["r_1"].to_numpy(float)
        m1 = np.where(np.isnan(r1), np.nan, np.maximum(g["mae_1"].to_numpy(float), -r1))
        blocks.append(DayBlock(pnl=np.where(np.isnan(r1), np.nan, r1 * rpc), risked=rpc.copy(),
                               exit_reasons=tuple("flatten" if x else "bracket" for x in g["flat"]),
                               risk_per_contract=rpc.copy(), mae=np.where(np.isnan(m1), np.nan, m1 * rpc),
                               entry_t=g["entry_t"].to_numpy(float), exit_t=g["exit_t"].to_numpy(float),
                               r_by_rr={k: g[f"r_{k:g}"].to_numpy(float) for k in keys},
                               mae_by_rr={k: np.maximum(g[f"mae_{k:g}"].to_numpy(float), -g[f"r_{k:g}"].to_numpy(float)) for k in keys},
                               fee=g["fee_micro_eq"].to_numpy(float) if "fee_micro_eq" in g.columns else None,   # D-324
                               sides=sides_of(g),                                                                  # D-339 / D-348
                               exit_by_rr=({k: g[f"exit_t_{k:g}"].to_numpy(float) for k in keys} if has_exits else None)))   # D-349
    return blocks, int(len(t))


def policy_for_edge(cfg: dict, lb: float):
    """The exported state policy (D-290) at the declared rent and the grid edge nearest FV3's own funded-leg bound,
    clipped to the grid."""
    from propedge.campaign.risk_policy import RiskPolicy

    sp = cfg["state_policy"]
    pols = json.loads((ROOT / sp["policies_json"]).read_text(encoding="utf-8"))
    edges = sorted({float(k.split("_e")[1].split("_lam")[0]) for k in pols})
    e = min(edges, key=lambda x: abs(x - (lb if np.isfinite(lb) else 0.0)))
    # D-329: a rent of 'fixed_point' names the table solved at the cash rate per slot-day (lambda*), one per edge
    rent = sp["slot_rent"]
    pid = f"state_dp_e{e:+.3f}_lamstar" if str(rent) == "fixed_point" else f"state_dp_e{e:+.3f}_lam{float(rent):g}"
    if pid not in pols:
        raise SystemExit(f"REFUSED: no exported policy {pid} in {sp['policies_json']}.")
    return RiskPolicy.from_dict(pols[pid]), e, pid


def sizing_rule(cfg: dict, tick_value: float):
    """The gate's sizing: the current tier at the declared headroom, with D-272's stand-aside per leg (the config's
    `state_policy.stand_aside`, the floor in ticks converted to dollars a micro) as the engine's rule (D-301)."""
    from dataclasses import replace

    from propedge.campaign.sizing import CURRENT_TIER, SizingRule

    camp = cfg["gate"]["campaign"]
    sa = cfg["state_policy"]["stand_aside"]
    stand = tuple((kind, float(v["min_risk_share"]), float(v["floor_ticks"]) * float(tick_value))
                  for kind, v in sa.items())
    room = fidelity_of(cfg)["room_cap"] or None                       # D-313: never more than the room above the floor
    fees = None
    if fidelity_of(cfg)["costs"] == "per_trade_at_size":             # D-324: the fee at the contracts a trade holds
        from propedge.data.orb_kit import params
        from propedge.execution.fills import FillModel

        q, fm = params("NQ"), FillModel.load("assumed")
        fees = (float(fm.round_turn_by_instrument[q["micro"]]), float(fm.round_turn_by_instrument["NQ"]))
    return replace(SizingRule.from_ledger(CURRENT_TIER, headroom_frac=float(camp["headroom"])), stand_aside=stand,
                   room_cap=room, fee_schedule=fees)


def g_reading(gdf: pd.DataFrame, cfg: dict) -> dict[str, Any]:
    """G's value and the basis it is read on. D-319 (the v6 audit, finding 3): with the bankroll an output (D-312) the
    gate row's growth is read on the bankroll the run needed (`pf_growth_on_base_p50`), as P2 reads it -- not the
    campaign's log growth on cash that never binds; with a stated bankroll the engine's own reading stands. D-334 (the
    audit of D-333, finding 10): both are written on G's kline row."""
    on_base = bool(bankroll_output(cfg) and "pf_growth_on_base_p50" in gdf)
    base = "on" if bool(cfg["gate"]["campaign"]["rtp"]) else "off"
    g = (gdf[(gdf["placement"].astype(str) == base) & (gdf["is_gate_row"].astype(str) == "True")]
         if {"placement", "is_gate_row"} <= set(gdf.columns) else gdf.iloc[0:0])
    col = "pf_growth_on_base_p50" if on_base else "median_log_growth"
    value = float(g[col].iloc[0]) if len(g) and col in g else None
    basis = (f"{col}: the gate row's median growth on the bankroll the run needed (p90 across its paths plus the margin, "
             "D-312; D-319)" if on_base else f"{col}: the engine's own reading on the stated bankroll")
    return {"value": value, "basis": basis, "on_required_bankroll": on_base}


def gate_passed_on_basis(gdf: pd.DataFrame, cfg: dict, passed: bool) -> bool:
    """G's verdict from `g_reading`: positive and finite on the required bankroll; the engine's own `passed` otherwise."""
    r = g_reading(gdf, cfg)
    if not r["on_required_bankroll"] or r["value"] is None:
        return bool(passed)
    return bool(np.isfinite(r["value"]) and r["value"] > 0)


#: D-334 (the audit of D-333, finding 6; D-327, D-332's housekeeping): how a result's manifest counts its variants.
VARIANT_COUNT_RULE = ("distinct configurations recorded in results/variants.jsonl under a result of this family -- the "
                      "result name less its version suffix -- this run included; the state table's solves are counted in "
                      "its own files")


def family_variant_count(counter: Any, result_name: str) -> int:
    """`VARIANT_COUNT_RULE`: the distinct variant ids whose ledger id names a result of `result_name`'s family."""
    family = re.sub(r"_v\d+$", "", result_name)
    return len({r["variant_id"] for r in counter.all()
                if re.sub(r"_v\d+$", "", str(r.get("prereg_id", "")).split(":", 1)[-1]) == family})


def run_gate(blocks, stats: dict, policy, cfg: dict, seed: int, tick_value: float, path_hook=None):
    """The D-145 gate under the state policy at both placements: the declared base case (D-289: `gate.campaign.rtp`,
    off) carries the gate row; the other placement's rows ride beside it, never as the verdict. `path_hook` (D-304:
    the portfolio measures) adds its columns to every row."""
    from propedge.campaign import gate
    from propedge.campaign.payout_method import rules_for_method
    from propedge.campaign.protocols import Protocol

    camp = cfg["gate"]["campaign"]
    fresh = cfg["state_policy"]["fresh"]
    protocol = Protocol(name="fv3", combine_rr=float(fresh["combine_rr"]), combine_risk=float(fresh["combine_risk"]),
                        funded_rr=float(fresh["funded_rr"]), funded_risk=float(fresh["funded_risk"]),
                        trades_per_day=MAX_PER_DAY, payout_path="standard", keep_balance=0.0, payout_frac=1.0,
                        max_concurrent_accounts=int(camp["accounts"]), family="fv3", source="config/fv3_grid.yaml",
                        note="FV3's gate under the state policy (D-290)",
                        params=protocol_params(cfg))                    # D-306, D-313
    keys = [float(R) for R in rr_menu(cfg)]
    e_by = {k: stats[k]["e"] for k in keys}
    lb_by = {k: stats[k]["lb"] for k in keys}
    base = bool(camp["rtp"])
    frames, passed = [], False
    for rtp in (base, not base):
        if path_hook is not None and hasattr(path_hook, "state"):           # D-310: the per-path record names its run
            path_hook.state["label"] = f"gate placement {'on' if rtp else 'off'}"
        df, ok = gate.run_gate(
            blocks, e=e_by[float(fresh["funded_rr"])], lb=lb_by[float(fresh["funded_rr"])], protocol=protocol,
            bankroll=bankroll_of(cfg), horizon_days=int(camp["horizon_days"]), n_paths=int(camp["n_paths"]),
            seed=seed, accounts=int(camp["accounts"]), sizing=sizing_rule(cfg, tick_value),
            rules=rules_for_method(camp["payout_method"]), mode=camp["mode"], settlement=camp["settlement"],
            combines=int(camp["combines"]), total_accounts=int(camp["accounts"]), risk_policy=policy,
            e_by_rr=e_by, lb_by_rr=lb_by, rtp=rtp, path_hook=path_hook, routing=fidelity_of(cfg)["routing"],
            cross_account=bool(fidelity_of(cfg).get("cross_account_rule", False)),   # D-339: the firm's rule, declared
            flip=flip_spec_of(cfg),                                                  # D-339: the flip stream, declared
            hold_to_own_exit=bool(fidelity_of(cfg).get("hold_to_own_exit", False)))  # D-351: the holding, declared
        df["placement"] = "on" if rtp else "off"
        if rtp == base:
            passed = ok
        else:
            df["is_gate_row"] = False                       # D-289: the other placement is reported beside, never as the verdict
        frames.append(df)
    return pd.concat(frames, ignore_index=True), passed


# --------------------------------------------------------------------------------------------------------- main

def _key(c: dict | None) -> dict:
    if c is None:
        return {"sessions": None}
    return {"sessions": "+".join(c["sessions"]), "continuation": c["continuation"], "displacement": c["displacement"],
            "double_rung_reversions": c["double_rung_reversions"]}


def main(argv: list[str] | None = None, *, results_dir: Path | None = None, runs_dir: Path | None = None,
         record: bool = True, data: tuple | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.data.orb_kit import params
    from propedge.execution.fills import FillModel
    from propedge.reporting.results import read_result, write_result
    from propedge.research.model_card import BAND_FILE, setups_minimum

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--declaration", required=True)
    ap.add_argument("--result-name", default="fv3_grid",
                    help="the result file's name (fv3_grid; D-301's corrected run writes fv3_grid_corrected)")
    ap.add_argument("--config", default=None,
                    help="the declaration to run (config/fv3_grid.yaml; D-306's protocol is config/fv3_portfolio.yaml)")
    a = ap.parse_args(argv)
    cfg_path = str(Path(a.config).resolve().relative_to(ROOT)).replace("\\", "/") if a.config else "config/fv3_grid.yaml"
    cfg = config(a.config)
    declared = str(cfg["decision"])
    if a.declaration != declared or f"| {declared} |" not in (ROOT / "DECISIONS.md").read_text(encoding="utf-8"):
        print(f"REFUSED: FV3's screen is declared by {declared} ({cfg_path}, DECISIONS.md); got {a.declaration!r} or the row is missing.")
        return 2
    k_total = math.prod(len(cfg["search"][x]) for x in AXES)
    if k_total != int(cfg["k"]):
        print(f"REFUSED: the grid holds {k_total} configurations, the config declares {cfg['k']}.")
        return 2
    fresh = cfg["state_policy"]["fresh"]
    need = setups_minimum(float(fresh["combine_rr"]), float(fresh["combine_risk"]), 0.0)
    if need is None or need != need:
        print("REFUSED: D-154's minimum for the fresh Combine is not tabulated (results/setups_per_day.csv).")
        return 2
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    sig, ses, bench, sessions = data if data is not None else load(
        rd, Path(runs_dir) if runs_dir is not None else ROOT / "runs", cfg)
    fm = FillModel.load("assumed")
    q = params("NQ")
    S = Signals3(sig, float(fm.round_turn_by_instrument[q["micro"]]), float(fm.round_turn_by_instrument["NQ"]),
                 q["micro_tick"] * q["micro_point_value"], cfg["ladder"])
    band = read_result(BAND_FILE)
    means = bench_means(bench, S.fixed_stops, bench_targets(cfg))   # D-308: at the rungs' fixed stops; D-316: each leg's R
    rows = mechanics(S, means, cfg, sessions)
    ev = EvaluatedFV3(S, ses, cfg, sessions, band, float(need))
    years = list(ev.years)
    wf_first = int(cfg["selection"]["walkforward"].get("first_test_year", WF_FIRST))   # the first test year, declared
    yr_s = pd.to_datetime(ses["date"]).dt.year
    for (y, name), g in ses[ses["present"] == 1].groupby([yr_s[ses["present"] == 1], "session"]):
        rows.append({"section": "capped", "year": int(y), "session": name, "sessions_present": int(len(g)),
                     "sessions_capped": int((g["signals_beyond_cap"] > 0).sum())})
    ok_all, v_all = ev.values(np.ones(len(years), bool))
    why_all = ev.reasons(np.ones(len(years), bool))          # D-308: why a cell is infeasible, in the record
    for k, c in enumerate(ev.cells):
        r = {"section": "grid", **_key(c), "feasible": bool(ok_all[k]), "value": float(v_all[k]),
             "freq_per_account_today": float(ev.freq[k]), "capped_share": ev.capped[tuple(c["sessions"])],
             "funded_sizeable_share": float(ev.funded_sizeable[k]), "infeasible_reason": why_all[k]}
        for leg in ("combine", "funded"):
            n = ev.mat[leg]["n"][k].sum()
            g = float(ev.mat[leg]["gross"][k].sum() / max(n, 1))
            fl = ev.mat[leg]["flat"][k]
            nn = ev.mat[leg]["n"][k]
            r.update({f"{leg}_n": int(n), f"{leg}_metric": float(ev.mat[leg]["metric"][k].sum() / max(n, 1)),
                      f"{leg}_gross": g, f"{leg}_net": float(ev.mat[leg]["net"][k].sum() / max(n, 1)),
                      f"{leg}_flat": float(fl.sum() / max(n, 1)), f"{leg}_today_cost": float(ev.tc[leg][k]),
                      f"{leg}_flat_max_year": float(max((f / x) if x else 0.0 for f, x in zip(fl, nn))) if len(nn) else float("nan")})
        rows.append(r)
        rows += ev.flatten_rows(k)
    rows.append({"section": "feasibility", **{f"declared_{k_}": v_ for k_, v_ in ev.feas.items()}, "min_setups_value": ev.need})
    sels, wf = {}, []
    for T in [y for y in years if y >= wf_first]:
        k, score = ev.select(ev.years < T)
        sels[T] = k
        val = ev.year_value(k, T) if k is not None else float("nan")
        wf.append(val)
        rows.append({"section": "walkforward", "test_year": T, **_key(ev.cells[k] if k is not None else None),
                     "score": score, "oos_value": val})
    wf_s = pd.Series(wf, index=[y for y in years if y >= wf_first])
    w1_lb = g5.bound(wf_s)
    w1 = bool(wf_s.isna().any() or not (w1_lb > 0))
    kf, score = ev.select(np.ones(len(years), bool))
    final = ev.cells[kf] if kf is not None else None
    w2, b_kill, g_kill, gate_passed = True, True, True, False
    pcfg = cfg.get("portfolio")                                  # D-304: present -> the portfolio stage judges the run
    plines, pvalues, gdf = None, {}, None
    paths_rows: list[dict] = []                                  # D-310: the per-path record, written beside the result
    criterion_met_any = False
    if final is not None:
        fv = float(v_all[kf])
        era_rows, flagged, low = g5.era_reading(ev, kf, cfg["selection"]["eras"]["split"], 2000, cfg["seeds"]["eras"])
        fv_used = min(fv, low) if flagged else fv
        w2 = bool(not ok_all[kf] or not (fv_used > 0))
        rows.append({"section": "final", **_key(final), "score": score, "value": fv, "value_used": fv_used,
                     "era_flagged": flagged, "freq_per_account_today": float(ev.freq[kf])})
        rows += [{"section": "eras", **r} for r in era_rows.values()]
        drift_rows, dv = drift_value(S, means, ev, kf)
        rows += drift_rows
        b_kill = bool(not (dv > 0))
        t = gate_trades(S, ev, sels, final)
        stats = {}
        for R in rr_menu(cfg):
            col = f"r_{R:g}"
            v = t[col].dropna() if len(t) else pd.Series(dtype=float)
            by = v.groupby(t.loc[v.index, "year"]).mean() if len(v) else pd.Series(dtype=float)
            stats[float(R)] = {"e": float(v.mean()) if len(v) else float("nan"), "lb": g5.bound(by), "n": int(len(v))}
            rows.append({"section": "gate_inputs", "rr": R, "oos_trades": stats[float(R)]["n"], "e": stats[float(R)]["e"],
                         "lb": stats[float(R)]["lb"]})
        # D-310 (D-309's finding 2): propsim D-47's research criterion written beside at every R -- never the gate (D-145)
        for R in rr_menu(cfg):
            s = stats[float(R)]
            rows.append({"section": "criterion", "rr": R, "e": s["e"], "lb": s["lb"], "e_min": D47_E_MIN, "lb_min": D47_LB_MIN,
                         "met": bool(np.isfinite(s["e"]) and np.isfinite(s["lb"]) and s["e"] >= D47_E_MIN and s["lb"] >= D47_LB_MIN),
                         "rule": "propsim D-47: e at least 0.10 net with a one-sided 95 % bound at least 0.05; reported beside the "
                                 "verdict, not the gate (D-145)"})
        criterion_met_any = bool(any(r["met"] for r in rows if r.get("section") == "criterion"))
        rows += flip_rows(cfg)                                 # D-339: the flip stream's statistics and judgement, from the files
        test_days = sorted(d for d in set(ses["date"]) if int(d[:4]) >= wf_first)
        # D-310 (D-304's P4 'no idle years'): a year of the gate's day set with no gate trade in it
        idle_years = sorted(set(int(d[:4]) for d in test_days) - (set(int(y) for y in t["year"]) if len(t) else set()))
        blocks, n_used = gate_blocks(t, test_days, q["micro_tick"] * q["micro_point_value"], rr_menu(cfg),
                                     require_sides=bool(fidelity_of(cfg).get("cross_account_rule", False)),   # D-348
                                     require_exits=bool(fidelity_of(cfg).get("hold_to_own_exit", False)))     # D-351
        lb_f = stats[float(fresh["funded_rr"])]["lb"]
        if len(t) and np.isfinite(lb_f):
            policy, e_used, pid = policy_for_edge(cfg, lb_f)
            tick_value = q["micro_tick"] * q["micro_point_value"]
            hook = None
            if pcfg is not None:
                import portfolio_stage as ps
                hook = ps.composed_hook(pcfg, sink=paths_rows)       # D-310: every campaign's per-path record
            gdf, gate_passed = run_gate(blocks, stats, policy, cfg, int(cfg["seeds"]["gate"]), tick_value, path_hook=hook)
            for _, gr in gdf.iterrows():
                rows.append({"section": "gate", "policy_id": pid, "policy_edge": e_used,
                             **{kk: vv for kk, vv in gr.items() if not isinstance(vv, (list, dict))}})
            if pcfg is not None:
                # D-304, D-305: the portfolio stage -- the twins, each test year's campaign, the four lines
                rows += ps.twins(blocks, stats, cfg, int(cfg["seeds"]["gate"]), tick_value, policy, hook)
                wf_rows = ps.walkforward_campaigns(t, ses, cfg, int(cfg["seeds"]["gate"]), tick_value, policy, stats, hook)
                rows += wf_rows
                plines, pvalues = ps.kill_lines(gdf, wf_rows, cfg, min(test_days) if test_days else "", idle_years=idle_years)
                for ln, ok in plines.items():
                    # D-319 (the v6 audit, finding 3): each line row names the growth basis its figures are read on
                    rows.append({"section": "pline", "line": ln, "passed": bool(ok), "killed": bool(not ok),
                                 "growth_basis": pvalues.get("growth_basis"),
                                 **{kk: vv for kk, vv in pvalues.items() if kk.startswith(ln)}})
            gate_passed = gate_passed_on_basis(gdf, cfg, gate_passed)
        g_kill = not gate_passed
    feas = np.nonzero(ok_all)[0]
    Y = np.array([[ev.year_value(int(k), y) for y in years] for k in feas]) if len(feas) else np.zeros((0, len(years)))
    rows.append({"section": "spa", "cells": int(len(feas)), "p_value": g5.spa_pvalue(Y, 2000, cfg["seeds"]["spa"])})
    if kf is not None and len(Y):
        srs = Y.mean(axis=1) / np.where(Y.std(axis=1, ddof=1) > 0, Y.std(axis=1, ddof=1), np.nan)
        yf = np.array([ev.year_value(kf, y) for y in years])
        rows.append({"section": "dsr", "n_trials": k_total, "dsr": g5.deflated_sharpe(yf, srs, k_total)})
    # D-308 (the audit of D-307, finding 1): a run that never reached its lines says so -- the reason it closed, and the
    # lines marked not evaluated -- instead of the fallback that named every line as failed
    if final is None:
        closed = "no feasible configuration: " + (why_all[0] if k_total == 1 else
                                                  "; ".join(f"{_key(c)['sessions']} {why}" for c, why in zip(ev.cells, why_all) if why))
    elif pcfg is not None and plines is None:
        closed = "no gate could run: the funded leg's lower bound is undefined or there are no out-of-sample trades"
    else:
        closed = ""
    lines_evaluated = not closed
    lines = {"W1": w1, "W2": w2, "B": b_kill, "G": g_kill}
    role = "beside" if pcfg is not None else "kill"             # D-304: with a portfolio block the W lines are reported beside
    # D-334 (the audit of D-333, finding 10): G's row carries the value it was read on and its basis, as W1's its bound
    g_read = g_reading(gdf, cfg) if gdf is not None else {"value": None, "basis": "no gate ran"}
    for ln, x in lines.items():
        rows.append({"section": "kline", "line": ln, "killed": bool(x) if lines_evaluated or final is not None else None,
                     "role": role, "evaluated": bool(lines_evaluated or final is not None),
                     "value": w1_lb if ln == "W1" else g_read["value"] if ln == "G" else None,
                     "basis": ("the one-sided 95 % lower bound of the walk-forward's yearly out-of-sample values" if ln == "W1"
                               else g_read["basis"] if ln == "G" else None)})
    if closed:
        for ln in ("P1", "P2", "P3", "P4") if pcfg is not None else ():
            rows.append({"section": "pline", "line": ln, "passed": None, "killed": None, "evaluated": False})
        killed = []
        verdict = "closed_at_feasibility" if final is None else "closed_before_the_lines"
        killed_by = ("feasibility: " if final is None else "no gate: ") + closed
        stop_point = (("closed at feasibility: no configuration met the declared conditions" if final is None else
                       "closed before the lines: the gate could not run")
                      + "; P1-P4 and W1 / W2 / B / G were not evaluated (D-308)")
    elif pcfg is not None:
        killed = [ln for ln, ok in plines.items() if not ok]
        verdict = "kill" if killed else "continue"
        killed_by = ",".join(killed)
        stop_point = ("a portfolio line: this declared protocol on these trades closed" if killed else
                      "continue: one confirmation on the held-back window under a registered pre-registration")
    else:
        killed = [ln for ln, x in lines.items() if x]
        verdict = "kill" if killed else "continue"
        killed_by = ",".join(killed)
        stop_point = ("W1: the specification and the fair-value branch as traded by his own rules closed" if w1 else
                      "a later gate: this specification closed" if killed else
                      "continue: one confirmation on the held-back window")
    rows.append({"section": "summary", "verdict": verdict, "killed_by": killed_by,
                 "judged_by": ("portfolio lines P1-P4 (D-304, D-305)" if pcfg is not None else "D-277's lines")
                              + ("" if lines_evaluated else " -- not evaluated"),
                 "lines_evaluated": bool(lines_evaluated),
                 "stopping_point": stop_point, "k": k_total, "years": f"{years[0]}-{years[-1]}",
                 "declaration": declared, "configurations_feasible_all_years": int(ok_all.sum()),
                 "feasibility_form": ev.feas["form"], "d47_criterion_met_any_rr": bool(criterion_met_any),
                 "paths_file": f"{a.result_name}_paths.csv" if paths_rows else ""})
    out = pd.DataFrame(rows)
    status = str(cfg.get("status", "FV3's screen, declared before it ran; EXPLORATORY in that its design is not blind to "
                                   "FV1's and FV2's results; only the held-back confirmation can decide"))
    description = str(cfg.get("description",
                              "FV3's declared screen on NQ 2009 to June 2025: the mechanics report, every configuration "
                              "of the primary family, the selection, its walk-forward from 2013, the era rule, the per-side "
                              "drift benchmark, the D-145 gate under the state policy on the walk-forward's out-of-sample "
                              "trades, and the kill lines W1, W2, B and G with D-277's stopping points, all fixed in "
                              "config/fv3_grid.yaml before the run."))
    # D-334 (the audit of D-333, finding 6): the run is recorded in the ledger before its result is written, so the
    # manifests carry the family's count of recorded configurations with this run among them (`VARIANT_COUNT_RULE`).
    counter = VariantCounter()
    if record:
        counter.record(prereg_id=f"{declared}:{a.result_name}", seed=int(cfg["seeds"]["gate"]), exploratory=True,
                       params={"study": "FV3 grid", "k": k_total, "market": "NQ", "result": a.result_name},
                       label=f"FV3's declared grid: {k_total} configurations ({declared}, {a.result_name})")
    n_var = family_variant_count(counter, a.result_name)
    write_result(out, a.result_name, script=SCRIPT, seed=int(cfg["seeds"]["gate"]), exploratory=True,
                 results_dir=results_dir, variant_count=n_var,
                 notes={"status": status, "variant_count_rule": VARIANT_COUNT_RULE},
                 parameters={"config": cfg_path, "runs": cfg["runs"], "k": k_total,
                             "fill_profile": "assumed", "fee": "NQ minis with MNQ micros (D-276)", "seeds": cfg["seeds"],
                             "decision": declared, "state_policy": cfg["state_policy"], "ladder": cfg["ladder"],
                             "fidelity": cfg.get("fidelity"), "rr_menu": list(rr_menu(cfg)), "portfolio": pcfg,
                             "feasibility": ev.feas},
                 description=description)
    if paths_rows:                                               # D-310: written after the result, which its manifest names
        write_result(pd.DataFrame(paths_rows), f"{a.result_name}_paths", script=SCRIPT, seed=int(cfg["seeds"]["gate"]),
                     exploratory=True, results_dir=results_dir, variant_count=n_var,
                     parameters={"result": f"{a.result_name}.csv", "decision": declared, "config": cfg_path,
                                 "measures": "propedge.campaign.portfolio.path_measures on the run's capital base (`base`: "
                                             "the required bankroll at p90 across the run's paths plus the margin), one row "
                                             "per resampled path of every campaign the scorer ran (`run`, `shift`, "
                                             "`enforcement_p`)"},
                     notes={"status": status, "companion_of": f"{a.result_name}.csv", "variant_count_rule": VARIANT_COUNT_RULE},
                     description=f"The per-path record of {a.result_name}.csv (D-310): each resampled path's final cash, "
                                 "fees, payouts, ruin, drawdown, deepest loss, trades, activity and the portfolio measures, "
                                 "so the campaign measures and the lines can be re-derived from the files.")
    pd.set_option("display.width", 250)
    print(out[out["section"].isin(["final", "eras", "drift", "gate_inputs", "spa", "dsr", "kline", "summary"])]
          .dropna(axis=1, how="all").round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
