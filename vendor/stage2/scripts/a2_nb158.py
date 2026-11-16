"""A2-NB158 (D-485): family A2's top cell -- the eight-bar break on 15-minute bars, followed -- at T24's m40 stop map,
sized by its own re-solved state table (FV3-C's kind, D-481), strictly one position at a time, on NQ; and its registered
development test.

    python scripts/a2_nb158.py --stop-distribution     # the card's stop distribution and the table's facts (EXPLORATORY)
    python scripts/a2_nb158.py --prereg P-xx           # the registered test; refused without a runnable registration

**The cell** (D-460's rule as D-481 (3) applies it: rank 1 of family A2's screen, `results/atlas_screen_a2.csv`,
D-485): pattern `nbar15x8` of `config/atlas_a2.yaml` (A1's grid, kind `nbar`, k 15, n 8: the first one-minute close
above the highest high, or below the lowest low, of the last eight completed 15-minute bars, in the 15 minutes after the
last of them completes, is the event, on that side, each side once per window), side rule `follow` (the trade takes
the event's side), entered at the open of the fifth bar after the event (the operator's latency, D-428 (1)), events
from 17:00 to 14:00 CT, FOMC days and early closes out, no trade before the 07:30 CT cut on a BLS report day.

**Its trades** are the screen's: family A1's walk on the local Databento bars, read by A2 as it is (D-481 (1), D-482:
`atlas_walk.walk_source`; the cache `data/atlas/A1`, git-ignored, under A1's config digest), through
`scripts/atlas_cells.py`'s `cell_walks` and `cell_trades` at the m40 map, the gap beyond a stop booked as a cost
(`t24_gf15b.gap_as_cost`, net R unchanged) -- `atlas_cells._job`'s steps. The day set is every day record of the walk.
Before anything else the trades are checked against the screen's own rows for the cell (`identity_with_screen`): the
screen file is the one fixed at registration (sha256), its walk-cache inputs are today's, the cell is its rank 1 with the
same trade count as its own row and as A1's row beside it (the screen's refusal rule, D-481 (1)), and each R's e, bound
and count equal its `edge` rows.

**The plan** is the cell's own state table, built once per run exactly as the screen built it (`build_table`:
`atlas_cells.cell_policy("table", ...)` -- `t24_exec.table_policy` at `t24_wide.edge_cell` of the cell's pooled
one-sided 95 % bounds over 21-session blocks; FV3-C's v12 solver configuration, one rung a stop at its share, each R's
availability per rung, the $200 to $2,000 menu; the oracles first). Before any campaign the table's oracle and `table`
rows are checked against the screen's (`table_identity`: every recorded value, D-484's solver being bit-identical); a
failed oracle or any difference refuses the run. The same table sizes every arm of the run.

**The run** is `scripts/t24_gf15.py`'s registered run under this spec, as A1-INS15's (P-11): P-08's engine and campaign
seed (20261028, not the screen's 20261030), 500 paths over 504 days, every arm beside the verdict; A1's development
window, check period and eras; the day capacity raised to the cell's busiest day where T24's 23 is too few (D-469,
`a1_ins15.protocol_for`, the screen's rule); the fidelity line of docs/SUCCESS_CRITERIA.md §3; the per-path record
(D-465); and, because the plan is a table, the fixed-legs twin in P-06's form (docs/SUCCESS_CRITERIA.md §4, D-304,
D-355; D-488): the same campaign under stage one's fixed legs as `config/fv3_portfolio.yaml`'s `portfolio.fixed_legs`
declares them, built by `portfolio_stage.fixed_legs_policy` (the function P-06's twin used), its point arm one row in
section `twin` with `twin` = `fixed_legs`, as P-06 wrote it. Beside it, an extra reading that is NOT P-06's form and
never decides: T24-GF15b's fixed plan (`t24_gf15b.policy`, the plan A1's rescreen sized these trades with), chosen
after the screen, in section `gf15b_twin`. Beside the verdict: the table's oracle, `table` and fresh-state rows; the
pattern's fade cell; the long/short drift rule; the walk cache's identity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from pathlib import Path

if __name__ == "__main__":                 # the registered run's one BLAS thread (D-464 (5)), before numpy loads
    for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/a2_nb158.py"
DECISION = "D-485"
MODEL = "A2-NB158"
FAMILY, WALK_FAMILY = "A2", "A1"            # A2 reads A1's walk (D-481 (1))
PATTERN, RULE = "nbar15x8", "follow"
KIND, KMIN, NBARS = "nbar", 15, 8
TOP = 40                                    # the m40 map
K = 1                                       # the selected cell; the screens' cells are counted in N (the ledger)
WINDOW = ("2020-01-01", "2026-07-16")       # development (D-461): the local bars' span, the reserve unread
CHECK = ("2025-01-17", "2026-07-16")        # the window's last eighteen months, reported beside (P-11's)
ERAS = ((2020, 2022), (2023, 2026))         # P-11's eras (D-271's rule inside the bars' span; 2026 to July 16)
REALISED_MIN = 0.90                         # docs/SUCCESS_CRITERIA.md §3: realised over capped intended risk, gate row
FIXED_LEGS_CONFIG = "config/fv3_portfolio.yaml"   # `portfolio.fixed_legs`: stage one's legs, P-06's twin (D-304, D-488)
SCREEN = "atlas_screen_a2.csv"              # the screen the cell was selected from (D-485)
SCREEN_SHA256 = "343ed6d422a3d886afb258be0e5da488e34c0b66218ad363625a50b0737dc0b7"   # written at 4d77565, committed b0005ed
RRS = (1.0, 1.5, 2.0, 3.0)
COLS = ["date", "year", "decision_ct", "day_kind", "S", "entry_t", "exit_t", "side", "stop_ticks", "flat",
        "fee_micro_eq", *[c for R in RRS for c in (f"r_{R:g}", f"g_{R:g}", f"c_{R:g}", f"o_{R:g}", f"exit_t_{R:g}",
                                                     f"mae_{R:g}")]]       # `t24_exec.trades`' columns
#: the `table` row's fields (`t24_exec.table_policy`) the screen recorded and the run must reproduce
TABLE_COLS = ("map", "edge", "rent", "rate", "cycle_cash", "cycle_slot_days", "value_attempt", "p_pass",
              "combine_p_abandon", "xfa_p_abandoned", "xfa_mean_cash", "rounds", "rung_stops", "rung_shares")
ORACLE_COLS = ("value", "bound", "relation", "held")
TOL = 1e-12                                 # relative and absolute: a re-solved table differs by far more, D-484


def cell_label(rule: str = RULE) -> str:
    return f"{PATTERN} {rule}"


def config_problems(cfg: dict) -> list[str]:
    """What the cell needs of family A2's declaration: the pattern, the table plan (D-481 (2)), A1's walk, five bars
    late, the m40 map and the follow rule. The problems, empty when it holds."""
    out = []
    ids = [i for i, p in enumerate(cfg.get("patterns") or []) if p.get("name") == PATTERN]
    if len(ids) != 1:
        out.append(f"the config holds {len(ids)} patterns named {PATTERN!r}")
    else:
        p = cfg["patterns"][ids[0]]
        if p.get("kind") != KIND or int(p.get("k", 0)) != KMIN or int(p.get("n", 0)) != NBARS:
            out.append(f"{PATTERN} is not the eight-bar break on 15-minute bars: {p}")
    if str(cfg.get("plan")) != "table":
        out.append(f"the plan is {cfg.get('plan')!r}, not the cell's state table (D-481 (2))")
    if str(cfg.get("walk_family") or cfg.get("family")) != WALK_FAMILY:
        out.append(f"the walk is {cfg.get('walk_family')!r}'s, not {WALK_FAMILY}'s (D-481 (1))")
    if int(cfg.get("screen_delay_min", -1)) != 5:
        out.append(f"the entry delay is {cfg.get('screen_delay_min')!r}, not five bars (D-428 (1))")
    if list(cfg.get("stop_maps") or []) != [f"m{TOP}"]:
        out.append(f"the stop maps are {cfg.get('stop_maps')!r}, not m{TOP}")
    if RULE not in (cfg.get("side_rules") or []):
        out.append(f"{RULE!r} is not among the side rules")
    return out


def pattern_id(cfg: dict) -> int:
    return [i for i, p in enumerate(cfg["patterns"]) if p.get("name") == PATTERN][0]


def cell_trades(loaded, rule: str = RULE) -> tuple[pd.DataFrame, list[str], list[dict]]:
    """The cell's trades in `t24_exec.trades`' columns, the day set (every day record of the walk) and the map's rows,
    from a loaded family -- `(cfg, q, (events, walks, days), spread)`, `atlas_cells._loaded`'s tuple -- exactly as the
    screen built them (`atlas_cells._job`): `cell_walks`, `cell_trades` at the m40 map, then the gap booked as a cost."""
    import atlas_cells as ac
    import t24_gf15b as tb

    cfg, q, (events, walks, days), spread = loaded
    bad = config_problems(cfg)
    if bad:
        raise SystemExit("REFUSED: " + "; ".join(bad))
    bix = {(float(T), float(S)): i for i, (T, S) in enumerate(q["bracket_points"])}
    t, rows = ac.cell_trades(ac.cell_walks(events, walks, days, pattern_id(cfg), rule), TOP, spread, bix)
    if t.empty:
        raise SystemExit(f"REFUSED: the cell {cell_label(rule)} has no trades")
    t = tb.gap_as_cost(t)
    rows = [{**r, "cell": cell_label(rule)} for r in rows]
    return t[COLS].reset_index(drop=True), sorted(days["date"].astype(str)), rows


def build_table(t: pd.DataFrame, days: list[str]):
    """(the cell's table policy, its oracle and `table` rows), built as the screen built it (`atlas_cells.run_cell`):
    each R's pooled one-sided 95 % bound over 21-session blocks, `atlas_cells.cell_policy("table", t, lb_by)` --
    `t24_exec.table_policy` at `t24_wide.edge_cell(lb_by)`. A failed oracle raises `t24_wide.OracleRefused`."""
    import atlas_cells as ac
    import confirm_fv3 as cf
    import portfolio_stage as ps
    import t24_wide as tw

    stats = cf.edge_stats(t, list(RRS), days, tw.BLOCK, None)
    pol, rows = ac.cell_policy("table", t, ps._by(stats, "lb"))
    return pol, [{**r, "cell": cell_label()} for r in rows]


def fresh_decisions(pol) -> dict[str, dict]:
    """The table's decision on a fresh Combine and a fresh funded account (balance at the start, the whole $2,000 to the
    floor, no winning day, no payout line): its dollar risk, R, trade cap, abandon and regime -- the card's sizes."""
    from propedge.campaign.risk_policy import MLL, NO_LINE

    base = {"balance": 0.0, "cushion": MLL, "cushion_frac": 1.0, "days_in_state": 0, "day": 0, "win_days": 0,
            "line_gap": NO_LINE, "request_day": 0}
    out = {}
    for phase in ("combine", "funded"):
        d = pol.decide({**base, "phase": phase})
        out[phase] = {"risk": float(d.risk), "rr": None if d.rr is None else float(d.rr),
                      "max_trades": None if d.max_trades is None else int(d.max_trades), "abandon": bool(d.abandon),
                      "regime": str(d.regime)}
    return out


def realised_by_stop(fresh: dict[str, dict], stops: list[int]) -> dict[str, dict[str, float]]:
    """D-312 (1): each fresh state's dollar risk in whole micros at each rung's stop, under the full verified allowance
    (`model_card.full_allowance`: the Combine's 50 micros, a fresh XFA's 20) -- {state: {'<ticks> ticks': $}}."""
    from propedge.research.model_card import full_allowance

    cap = full_allowance()
    out = {}
    for state, d in fresh.items():
        out[state] = {}
        for S in stops:
            ticks = int(round(float(S) / 0.25))
            per = ticks * 0.5                                      # an MNQ tick is $0.50
            out[state][f"{ticks} ticks"] = float(min(math.floor(d["risk"] / per + 1e-9), cap[state]) * per)
    return out


def fresh_rows(pol) -> list[dict]:
    return [{"section": "table_fresh", "cell": cell_label(), "phase": ph, "policy_risk": d["risk"], "policy_rr": d["rr"],
             "policy_max_trades": d["max_trades"], "policy_abandon": d["abandon"], "regime": d["regime"]}
            for ph, d in fresh_decisions(pol).items()]


def stop_distribution(t: pd.DataFrame, combine_rr: float, funded_rr: float) -> pd.DataFrame:
    """The card's stops (D-191, D-212; `t24_gf15.stop_distribution`'s form at the table's fresh R): one row per trade and
    state -- its stop in micro ticks, the R, the exit its state's bracket took and its date: the Combine at the table's
    fresh Combine R, the funded account at its fresh funded R, each where the event hour offers that R."""
    kinds = {"t": "target", "s": "stop", "f": "flatten"}
    rows = []
    for state, R in (("combine", float(combine_rr)), ("funded", float(funded_rr))):
        g = t[t[f"o_{R:g}"].astype(str) != ""]
        rows.append(pd.DataFrame({"market": "NQ", "stop_ticks": g["stop_ticks"].astype(int), "state": state, "rr": R,
                                  "exit": g[f"o_{R:g}"].map(kinds), "date": g["date"]}))
    return pd.concat(rows, ignore_index=True)


def trades(rd: Path):
    """The registered run's trades: the cell's (`cell_trades` on family A2's loaded walk -- A1's), the day set and the
    rows beside the verdict (the map, the walk's identity, the fade cell, the drift rule; A1-INS15's helpers)."""
    import a1_ins15 as a1
    import atlas_cells as ac

    loaded = ac._loaded(FAMILY)
    t, days, rows = cell_trades(loaded)
    f, _, _ = cell_trades(loaded, "fade")
    return t, days, rows + a1.walk_rows(WALK_FAMILY) + a1.fade_rows(f, days) + a1.drift_rows(t)


def protocol_for(t: pd.DataFrame):
    """T24's protocol, its day capacity raised to the cell's busiest day only where T24's 23 is too few (D-469: a
    capacity, never a choice; `atlas_cells.run_cell`'s and `a1_ins15.protocol_for`'s rule)."""
    import a1_ins15 as a1

    return a1.protocol_for(t)


def policy():
    """Never the plan by default: the table is solved on the cell's trades, and `registered` passes it."""
    raise RuntimeError("A2-NB158's plan is the cell's state table, solved on its trades: run through registered()")


def fixed_legs_values() -> dict:
    """Stage one's fixed legs as `FIXED_LEGS_CONFIG` declares them (`portfolio.fixed_legs`: each leg's R and dollar
    risk) -- read from the file, never typed (D-488)."""
    import yaml

    doc = yaml.safe_load((ROOT / FIXED_LEGS_CONFIG).read_text(encoding="utf-8"))
    return dict(doc["portfolio"]["fixed_legs"])


def fixed_legs():
    """The fixed-legs twin's plan in P-06's form (docs/SUCCESS_CRITERIA.md §4, D-304, D-355; D-488): stage one's fixed
    legs from `FIXED_LEGS_CONFIG`, built by `portfolio_stage.fixed_legs_policy`, the function P-06's twin used --
    beside the verdict, never part of it."""
    import portfolio_stage as ps

    return ps.fixed_legs_policy({"fixed_legs": fixed_legs_values()})


def gf15b_plan():
    """An extra reading beside the verdict, NOT P-06's form and never deciding (D-488): T24-GF15b's fixed plan (D-439),
    the plan family A1's rescreen sized these trades with, chosen after the screen as a beside reading."""
    import t24_gf15b as tb

    return tb.policy()


def _exact(path: Path) -> pd.DataFrame:
    """A result CSV checked against its manifest, then read with every float to its last digit (D-471)."""
    from propedge.reporting.results import verify_result

    ok, msg = verify_result(path)
    if not ok:
        raise ValueError(msg)
    return pd.read_csv(path, float_precision="round_trip", low_memory=False)


def _plain(v):
    """A numpy scalar as its Python value, for a manifest."""
    return v.item() if isinstance(v, np.generic) else v


def _same(a, b) -> bool:
    try:
        x, y = float(a), float(b)
    except (TypeError, ValueError):
        return str(a) == str(b)
    return (np.isnan(x) and np.isnan(y)) or bool(np.isclose(x, y, rtol=TOL, atol=TOL))


def _cell(s: pd.DataFrame) -> pd.Series:
    return (s["pattern"].astype(str) == PATTERN) & (s["rule"].astype(str) == RULE)


def identity_with_screen(rd: Path, t: pd.DataFrame, days: list[str], *, sha256: str | None = SCREEN_SHA256,
                         walk_inputs: dict | None = None) -> list[str]:
    """The trades are the screen's cell: the screen file is the one fixed at registration (its sha256); the walk cache
    it read is today's (its manifest's `walk_cache_inputs` against `walk_inputs`, by default A1's cache digest now);
    the cell is its rank 1, its table passed, and its trade count equals the run's and A1's row beside it (the
    screen's refusal rule, D-481 (1)); each R's e, one-sided 95 % bound and count equal its `edge` rows (to 1e-12; an R
    offered nowhere NaN in both). The problems, empty when it holds."""
    import confirm_fv3 as cf

    path = Path(rd) / SCREEN
    out = []
    if sha256 is not None and hashlib.sha256(path.read_bytes()).hexdigest() != sha256:
        out.append(f"{SCREEN} is not the file fixed at registration (sha256 {sha256[:12]})")
    man = json.loads(Path(str(path) + ".manifest.json").read_text(encoding="utf-8"))
    if walk_inputs is None:
        from propedge.research import atlas_walk as AW

        walk_inputs = AW.inputs_digest(WALK_FAMILY, "NQ")
    if (man.get("parameters") or {}).get("walk_cache_inputs") != walk_inputs:
        out.append("the walk cache's inputs (bars, A1's config, the walk's code) are not the ones the screen read")
    s = _exact(path)
    cell = _cell(s)
    scr = s[cell & (s["section"] == "screen")]
    if len(scr) != 1:
        return out + [f"the screen holds {len(scr)} rows for {cell_label()}"]
    row = scr.iloc[0]
    if not (np.isfinite(float(row["rank"])) and int(float(row["rank"])) == 1):
        out.append(f"{cell_label()} is rank {row['rank']} of the screen, not 1 (D-481 (3))")
    if str(row.get("table_passed")) != "True":
        out.append(f"the screen's table for {cell_label()} did not pass its oracles")
    for col in ("trades", f"{WALK_FAMILY.lower()}_trades"):
        if col not in row or not np.isfinite(float(row[col])) or int(float(row[col])) != len(t):
            out.append(f"{len(t)} trades against the screen's {col} {row.get(col)!r}")
    edge = s[cell & (s["section"] == "edge")].set_index("rr")
    st = cf.edge_stats(t, list(RRS), days, 21, None)
    for R in RRS:
        if float(R) not in edge.index:
            out.append(f"the screen has no edge row at R {R:g}")
            continue
        for k in ("e", "lb", "n"):
            a, b = float(st[R][k]), float(edge.loc[float(R), k])
            if not ((np.isnan(a) and np.isnan(b)) or np.isclose(a, b, rtol=0, atol=1e-12)):
                out.append(f"R {R:g} {k}: {a!r} against the screen's {b!r}")
    return out


def table_identity(rd: Path, rows: list[dict]) -> list[str]:
    """The table is the screen's: its `table` row equal to the screen's on every field the screen recorded
    (`TABLE_COLS`), and its oracles the screen's -- the same checks, each value, bound, relation and held. The problems,
    empty when it holds."""
    s = _exact(Path(rd) / SCREEN)
    cell = _cell(s)
    out = []
    want = s[cell & (s["section"] == "table")]
    got = [r for r in rows if r.get("section") == "table"]
    if len(want) != 1 or len(got) != 1:
        return [f"{len(got)} table rows against the screen's {len(want)}"]
    w, g = want.iloc[0], got[0]
    for c in TABLE_COLS:
        if not _same(g.get(c), w.get(c)):
            out.append(f"table {c}: {g.get(c)!r} against the screen's {w.get(c)!r}")
    wo = s[cell & (s["section"] == "oracle")].set_index("check")
    go = {str(r["check"]): r for r in rows if r.get("section") == "oracle"}
    if set(go) != set(wo.index.astype(str)):
        return out + [f"oracles {sorted(go)} against the screen's {sorted(wo.index.astype(str))}"]
    for chk, r in go.items():
        for c in ORACLE_COLS:
            a, b = r.get(c), wo.loc[chk, c]
            if c == "held":
                if bool(a) is not (str(b) == "True"):
                    out.append(f"oracle {chk} held: {a!r} against the screen's {b!r}")
            elif not _same(a, b):
                out.append(f"oracle {chk} {c}: {a!r} against the screen's {b!r}")
    if not all(bool(r.get("held")) for r in go.values()):
        out.append("an oracle failed (D-429): the table is wrong, not the contract")
    return out


SPEC = {"model": MODEL, "decision": DECISION, "script": SCRIPT, "result": "a2_nb158_gate", "k": K, "label": MODEL,
        "policy": policy, "trades": trades, "window": WINDOW, "check": CHECK, "eras": ERAS, "protocol": protocol_for,
        "realised_min": REALISED_MIN, "paths_file": True, "fixed_legs": fixed_legs,
        "beside_plans": (("gf15b_twin", gf15b_plan),),
        "parameters": {"atlas_family": FAMILY, "walk_family": WALK_FAMILY, "config": "config/atlas_a2.yaml",
                       "walk_config": "config/atlas_a1.yaml", "cell": cell_label(),
                       "plan": "table: the cell's own state table (D-481 (2)), t24_exec.table_policy at t24_wide.edge_cell "
                               "of the cell's pooled one-sided 95 % bounds; config/state_policy_v12.yaml's rules, rent "
                               "and export (FV3-C's); solved once, every arm",
                       # T24's plan constants `_registered_run` writes, which this plan does not use (D-485)
                       "family": "table (not T24's gf15)", "two_shot": "not used: the plan is the table",
                       "growth": "not used: the plan is the table", "flip": "not used: the plan is the table",
                       "fixed_legs_twin": "P-06's form (docs/SUCCESS_CRITERIA.md §4, D-304, D-355, D-488): stage "
                                          f"one's fixed legs from {FIXED_LEGS_CONFIG} portfolio.fixed_legs through "
                                          "portfolio_stage.fixed_legs_policy; its point arm, section twin, twin "
                                          "fixed_legs; beside the verdict, never deciding",
                       "fixed_legs": fixed_legs_values(), "fixed_legs_config": FIXED_LEGS_CONFIG,
                       "gf15b_twin": "NOT P-06's form (D-488): T24-GF15b's fixed plan (t24_gf15b.policy, family A1's "
                                     "rescreen's), chosen after the screen as a beside reading; its point and bound "
                                     "rows, section gf15b_twin; never deciding",
                       "delay": 5, "screen": f"results/{SCREEN}", "screen_sha256": SCREEN_SHA256,
                       "bars": "data/bars/NQ (Databento GLBX.MDP3 ohlcv-1m, D-458)"},
        "description": ("A2-NB158's registered development test (D-485): family A2's selected cell -- the 15-minute "
                        "eight-bar break, followed, five bars late, at the m40 map -- sized by its own re-solved state "
                        "table (FV3-C's kind, D-481), strictly one position at a time, on the local NQ bars; the D-145 "
                        "gate at 0.05/N and 0.05; beside it the fixed-legs twin in P-06's form (stage one's fixed "
                        "legs) and, never deciding, T24-GF15b's fixed plan (section gf15b_twin, not P-06's form).")}


def registered(pid: str, rd: Path, results_dir: Path | None, *, reproduce: bool = False) -> int:
    """The registered run of `pid` (after `main`'s registration check): the trades and their identity with the screen,
    the table built once and its identity with the screen's, then `t24_gf15._registered_run` under SPEC with that table
    and those trades. `reproduce` is D-479's seam (`scripts/reproduce_registered.py` only): the same computation,
    written outside the repository as a reproduction, never a verdict."""
    import t24_gf15 as tg
    import t24_wide as tw

    t, days, rows = trades(rd)
    problems = identity_with_screen(rd, t, days)
    if problems:
        print("REFUSED (D-485): A2-NB158's trades are not the screen's cell -- " + "; ".join(problems))
        return 3
    try:
        pol, table_rows = build_table(t, days)
    except tw.OracleRefused as exc:
        print(f"REFUSED (D-485, D-429): {exc}")
        return 3
    problems = table_identity(rd, table_rows)
    if problems:
        print("REFUSED (D-485): A2-NB158's table is not the screen's -- " + "; ".join(problems))
        return 3
    beside = rows + table_rows + fresh_rows(pol)
    return tg._registered_run(pid, rd, results_dir, spec={**SPEC, "policy": lambda: pol,
                                                          "trades": lambda _rd: (t, days, beside)},
                              reproduce=reproduce)


def stop_distribution_main(rd: Path, results_dir: Path | None) -> int:
    """The card's stop distribution and the table's facts (EXPLORATORY: a reading of the cell's trades and of the plan
    D-481 fixed, no campaign): the trades and their identity with the screen, the table and its identity, the fresh
    decisions, the stops at those R, each R's offered count and per-trade sd."""
    import atlas_cells as ac
    import a1_ins15 as a1

    from propedge.reporting.results import write_result

    t, days, _ = cell_trades(ac._loaded(FAMILY))
    problems = identity_with_screen(rd, t, days)
    if problems:
        print("REFUSED (D-485): A2-NB158's trades are not the screen's cell -- " + "; ".join(problems))
        return 3
    pol, trows = build_table(t, days)
    problems = table_identity(rd, trows)
    if problems:
        print("REFUSED (D-485): A2-NB158's table is not the screen's -- " + "; ".join(problems))
        return 3
    fresh = fresh_decisions(pol)
    if any(d["rr"] is None or d["abandon"] or d["max_trades"] == 0 for d in fresh.values()):
        print(f"REFUSED (D-485): a fresh state takes no trade under the table: {fresh}")
        return 3
    tab = next(r for r in trows if r["section"] == "table")
    stops = sorted(int(s) for s in t["S"].unique())
    busiest = int(t.groupby("date").size().max())
    offered = {f"{R:g}": int(np.isfinite(t[f"r_{R:g}"].astype(float)).sum()) for R in RRS}
    sd_r = {f"{R:g}": float(t[f"r_{R:g}"].astype(float).std(ddof=1)) for R in RRS if offered[f"{R:g}"] > 1}
    sd = stop_distribution(t, fresh["combine"]["rr"], fresh["funded"]["rr"])
    write_result(sd, "a2_nb158_stop_distribution", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 results_dir=results_dir,
                 parameters={"decision": DECISION, "model": MODEL, "cell": cell_label(), "map": f"m{TOP}",
                             "trades": len(t), "days": len(days), "trades_per_day": len(t) / len(days),
                             "busiest_day": busiest, "trades_per_day_capacity": int(protocol_for(t).trades_per_day),
                             "offered": offered, "sd_r": sd_r, "stops_points": stops,
                             "long_share": float((t["side"] == "long").mean()),
                             "table": {c: _plain(tab.get(c)) for c in TABLE_COLS},
                             "oracles": {str(r["check"]): {c: _plain(r.get(c)) for c in ORACLE_COLS}
                                         for r in trows if r["section"] == "oracle"},
                             "fresh": fresh, "realised_by_stop": realised_by_stop(fresh, stops),
                             "screen": f"results/{SCREEN}", "screen_sha256": SCREEN_SHA256,
                             "identity_with_screen": "holds (trades, edge rows, table and oracles)",
                             "walk": a1.walk_rows(WALK_FAMILY)[0]},
                 notes={"status": "the card's stop distribution and the table's facts (D-485); no campaign",
                        "seed": "none: a reading of the walk and of the table D-481 fixed"},
                 description="A2-NB158's stops (D-485): one row per trade and state -- the Combine at the table's fresh "
                             "Combine R, the funded account at its fresh funded R, each where the event hour offers it "
                             "-- its stop in micro ticks, the R, the exit its state's bracket took and its date; the "
                             "table's row, oracles and fresh decisions in the manifest.")
    print(f"stop distribution: {len(t)} trades on {len(days)} days, the busiest day {busiest}; fresh Combine "
          f"${fresh['combine']['risk']:,.0f} at {fresh['combine']['rr']:g}R, fresh funded ${fresh['funded']['risk']:,.0f} "
          f"at {fresh['funded']['rr']:g}R; table at edge {tab['edge']:+.3f}, P(pass) {tab['p_pass']:.4f}")
    return 0


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--stop-distribution", action="store_true")
    ap.add_argument("--prereg", default=None)
    a = ap.parse_args(argv)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    if a.stop_distribution:
        return stop_distribution_main(rd, results_dir)
    from propedge.backtest.harness import PreregRegistry, UnregisteredRunError

    try:
        PreregRegistry.load().require_runnable(a.prereg)
    except UnregisteredRunError as exc:
        print(f"REFUSED ({DECISION}): {exc}")
        return 2
    return registered(a.prereg, rd, results_dir)


if __name__ == "__main__":
    raise SystemExit(main())
