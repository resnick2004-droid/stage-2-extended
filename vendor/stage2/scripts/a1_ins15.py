"""A1-INS15 (D-472): family A1's selected cell -- the inside-bar break on 15-minute bars, followed -- at T24's m40 stop map
under T24-GF15b's plan, strictly one position at a time, on NQ; and its registered development test.

    python scripts/a1_ins15.py --stop-distribution     # the card's stop distribution (EXPLORATORY: a reading of the trades)
    python scripts/a1_ins15.py --prereg P-xx           # the registered test; refused without a runnable registration

**The cell** (D-460's selection rule: rank 1 of the rescreen, `results/atlas_screen_a1_gf15b.csv`, D-469): pattern
`inside15` of `config/atlas_a1.yaml` (kind `inside`, k 15: the previous completed 15-minute bar lies inside the one before
it; the first one-minute close beyond the inside bar's high or low in the next 15 minutes is the event, on that side,
each side once per inside bar), side rule `follow` (the trade takes the event's side), entered at the open of the fifth
bar after the event (the operator's latency, D-428 (1)), events from 17:00 to 14:00 CT, FOMC days and early closes out,
no trade before the 07:30 CT cut on a BLS report day.

**Its trades** are the screen's: family A1's walk on the local Databento bars (D-458, D-460; the cache `data/atlas/A1`,
git-ignored, rebuilt from the bars only when its inputs change) through `scripts/atlas_cells.py`'s `cell_walks` and
`cell_trades` -- each event hour's stop the widest of 20 and 40 points at which 1:1 resolves (at most 5 % unresolved on
normal days, overall and in every year) and every R that resolves there offered (the m40 map, D-432); each trade's costs
inside its R (the round turn, R137's measured entry spread by hour and year, a tick on a stop) -- with the gap beyond a
stop booked as a cost (`t24_gf15b.gap_as_cost`, net R unchanged). The day set is every day record of the walk (an FOMC
day, an early close or a day without bars is an empty block). Before any campaign the trades are checked against the
rescreen's own rows for the cell -- its rank, its trade count, each R's e, bound and count -- and the rescreen file
against the sha256 fixed at registration (`identity_with_screen`); any difference refuses the run.

**The run** is `scripts/t24_gf15.py`'s registered run under this spec: T24-GF15b's plan (`t24_gf15b.policy`), P-08's
engine and campaign seed (20261028 -- not the screen's 20261030, so the verdict's resampled paths are not the ones the
selection read), 500 paths over 504 days, every arm beside the verdict; A1's development window, check period and eras;
the protocol's day capacity raised to the cell's busiest day only where T24's 23 is too few (D-469); the fidelity line of
docs/SUCCESS_CRITERIA.md §3 (realised risk at least 0.9 of the allowance-capped intention on the gate row); every path of
every campaign in a per-path record (D-465). Beside the verdict, from the same walk: the pattern's fade cell (the same
events, the other side, at its own map) and the long/short-balanced net R per R with the part of e the cell's
long/short lean explains (D-271's drift rule in ORB5's form); and the walk cache's identity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/a1_ins15.py"
DECISION = "D-472"
MODEL = "A1-INS15"
FAMILY, PATTERN, RULE = "A1", "inside15", "follow"
TOP = 40                                    # the m40 map
K = 1                                       # the selected cell; the screens' cells are counted in N (the ledger)
WINDOW = ("2020-01-01", "2026-07-16")       # development (D-461): the local bars' span, the reserve unread
CHECK = ("2025-01-17", "2026-07-16")        # the window's last eighteen months, reported beside (T24's CHECK's role)
ERAS = ((2020, 2022), (2023, 2026))         # the eras (D-271's rule inside the bars' span; 2026 to July 16)
REALISED_MIN = 0.90                         # docs/SUCCESS_CRITERIA.md §3: realised over capped intended risk, gate row
SCREEN = "atlas_screen_a1_gf15b.csv"        # the rescreen the cell was selected from (D-469)
SCREEN_SHA256 = "ec8f36758cec0ac88a783c9d3c5acb8163645ae7edea1cee6ad558182db1c48f"   # written at a4b417b, committed 15f1f81
RRS = (1.0, 1.5, 2.0, 3.0)
COLS = ["date", "year", "decision_ct", "day_kind", "S", "entry_t", "exit_t", "side", "stop_ticks", "flat",
        "fee_micro_eq", *[c for R in RRS for c in (f"r_{R:g}", f"g_{R:g}", f"c_{R:g}", f"o_{R:g}", f"exit_t_{R:g}",
                                                     f"mae_{R:g}")]]       # `t24_exec.trades`' columns


def config_problems(cfg: dict) -> list[str]:
    """What the cell needs of family A1's declaration: the pattern, T24-GF15b's plan (D-469), five bars late, the m40
    map and the follow rule. The problems, empty when it holds."""
    out = []
    ids = [i for i, p in enumerate(cfg.get("patterns") or []) if p.get("name") == PATTERN]
    if len(ids) != 1:
        out.append(f"the config holds {len(ids)} patterns named {PATTERN!r}")
    else:
        p = cfg["patterns"][ids[0]]
        if p.get("kind") != "inside" or int(p.get("k", 0)) != 15:
            out.append(f"{PATTERN} is not the 15-minute inside-bar break: {p}")
    if str(cfg.get("plan")) != "gf15b":
        out.append(f"the plan is {cfg.get('plan')!r}, not T24-GF15b's (D-469)")
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
        raise SystemExit(f"REFUSED: the cell {PATTERN} {rule} has no trades")
    t = tb.gap_as_cost(t)
    rows = [{**r, "cell": f"{PATTERN} {rule}"} for r in rows]
    return t[COLS].reset_index(drop=True), sorted(days["date"].astype(str)), rows


def fade_rows(f: pd.DataFrame, days: list[str]) -> list[dict]:
    """The pattern's fade cell (the same events, the other side, at its own map): each R's net e, its one-sided 95 %
    bound over 21-session blocks and its count -- the directional reading beside the verdict, never part of it."""
    import confirm_fv3 as cf

    st = cf.edge_stats(f, list(RRS), days, 21, None)
    return [{"section": "fade", "rr": R, "e": st[R]["e"], "lb": st[R]["lb"], "n": st[R]["n"]} for R in RRS]


def drift_rows(t: pd.DataFrame) -> list[dict]:
    """D-271's drift rule in ORB5's form (`score_orb5_grid.drift_value`): per offered R, pooled and per year, the long
    and the short trades' mean net R, the long share and the long/short-balanced net R (the mean of the two sides'
    means); `drift_part` is e less the balanced value -- the part of e the cell's lean to one side explains, NQ's drift
    among it. Beside the verdict, never part of it."""
    out = []
    side = t["side"].astype(str)
    for R in RRS:
        r = t[f"r_{R:g}"].astype(float)
        m = np.isfinite(r.to_numpy())
        if not m.any():
            continue
        years = sorted(int(y) for y in t.loc[m, "year"].unique())
        for period, sel in [("all", m)] + [(str(y), m & (t["year"].astype(int) == y).to_numpy()) for y in years]:
            lo, sh = sel & (side == "long").to_numpy(), sel & (side == "short").to_numpy()
            ml = float(r[lo].mean()) if lo.any() else float("nan")
            ms = float(r[sh].mean()) if sh.any() else float("nan")
            e = float(r[sel].mean())
            bal = (ml + ms) / 2.0
            out.append({"section": "drift", "rr": R, "period": period, "n": int(sel.sum()),
                        "long_share": float(lo.sum() / sel.sum()), "long_mean": ml, "short_mean": ms, "e": e,
                        "balanced": bal, "drift_part": e - bal})
    return out


def walk_rows(family: str = FAMILY) -> list[dict]:
    """The walk cache's identity (its manifest's inputs: the bar store's parquet sha256, the config's and the code's)."""
    from propedge.research import atlas_walk as AW

    p = AW.CACHE / family / "manifest.json"
    m = json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}
    inp, rows = m.get("inputs") or {}, m.get("rows") or {}
    return [{"section": "walk", "family": family, **{k: inp.get(k) for k in (
        "bars_parquet_sha256", "config_sha256", "code_sha256", "days", "first", "last", "purpose")},
        **{f"rows_{k}": v for k, v in rows.items()}}]


def trades(rd: Path):
    """The registered run's trades: the cell's (`cell_trades` on family A1's loaded walk), the day set and the rows
    beside the verdict (the map, the walk's identity, the fade cell, the drift rule)."""
    import atlas_cells as ac

    loaded = ac._loaded(FAMILY)
    t, days, rows = cell_trades(loaded)
    f, _, _ = cell_trades(loaded, "fade")
    return t, days, rows + walk_rows() + fade_rows(f, days) + drift_rows(t)


def protocol_for(t: pd.DataFrame):
    """T24's protocol, its day capacity raised to the cell's busiest day only where T24's 23 is too few (D-469: a
    capacity, never a choice -- `atlas_cells.run_cell`'s rule)."""
    from dataclasses import replace

    import t24_wide as tw

    proto = tw.protocol()
    busiest = int(t.groupby("date").size().max()) if len(t) else 0
    return replace(proto, trades_per_day=busiest) if busiest > int(proto.trades_per_day) else proto


def policy():
    """T24-GF15b's plan (D-439): every state closes the account once its room cannot carry its trade."""
    import t24_gf15b as tb

    return tb.policy()


def identity_with_screen(rd: Path, t: pd.DataFrame, days: list[str], *, sha256: str | None = SCREEN_SHA256) -> list[str]:
    """The trades are the screen's cell: the rescreen file is the one fixed at registration (its sha256), the cell is
    its rank 1 with the same trade count, and each R's e, one-sided 95 % bound and count equal its `edge` rows (to
    1e-12; an R offered nowhere NaN in both). The problems, empty when it holds."""
    import confirm_fv3 as cf

    from propedge.reporting.results import read_result

    path = Path(rd) / SCREEN
    out = []
    if sha256 is not None and hashlib.sha256(path.read_bytes()).hexdigest() != sha256:
        out.append(f"{SCREEN} is not the file fixed at registration (sha256 {sha256[:12]})")
    s = read_result(path)
    cell = (s["pattern"].astype(str) == PATTERN) & (s["rule"].astype(str) == RULE)
    scr = s[cell & (s["section"] == "screen")]
    if len(scr) != 1:
        return out + [f"the screen holds {len(scr)} rows for {PATTERN} {RULE}"]
    if int(float(scr.iloc[0]["rank"])) != 1:
        out.append(f"{PATTERN} {RULE} is rank {scr.iloc[0]['rank']} of the screen, not 1 (D-460's rule)")
    if int(float(scr.iloc[0]["trades"])) != len(t):
        out.append(f"{len(t)} trades against the screen's {int(float(scr.iloc[0]['trades']))}")
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


SPEC = {"model": MODEL, "decision": DECISION, "script": SCRIPT, "result": "a1_ins15_gate", "k": K, "label": MODEL,
        "policy": policy, "trades": trades, "window": WINDOW, "check": CHECK, "eras": ERAS, "protocol": protocol_for,
        "realised_min": REALISED_MIN, "paths_file": True,
        "parameters": {"atlas_family": FAMILY, "config": "config/atlas_a1.yaml", "cell": f"{PATTERN} {RULE}",
                       "plan": "gf15b (T24-GF15b's, D-439)", "delay": 5, "screen": f"results/{SCREEN}",
                       "screen_sha256": SCREEN_SHA256, "bars": "data/bars/NQ (Databento GLBX.MDP3 ohlcv-1m, D-458)"},
        "description": ("A1-INS15's registered development test (D-472): family A1's selected cell -- the 15-minute "
                        "inside-bar break, followed, five bars late, at the m40 map -- under T24-GF15b's plan, strictly "
                        "one position at a time, on the local NQ bars; the D-145 gate at 0.05/N and 0.05.")}


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    import t24_gf15 as tg

    from propedge import RESULTS_DIR
    from propedge.reporting.results import write_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--stop-distribution", action="store_true")
    ap.add_argument("--prereg", default=None)
    a = ap.parse_args(argv)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    if a.stop_distribution:
        import atlas_cells as ac

        t, days, _ = cell_trades(ac._loaded(FAMILY))
        busiest = int(t.groupby("date").size().max())
        offered = {f"{R:g}": int(np.isfinite(t[f"r_{R:g}"].astype(float)).sum()) for R in RRS}
        sd_r = {f"{R:g}": float(t[f"r_{R:g}"].astype(float).std(ddof=1)) for R in RRS if offered[f"{R:g}"] > 1}
        write_result(tg.stop_distribution(t), "a1_ins15_stop_distribution", script=SCRIPT, seed=None,
                     require_seed=False, exploratory=True, results_dir=results_dir,
                     parameters={"decision": DECISION, "model": MODEL, "cell": f"{PATTERN} {RULE}", "map": f"m{TOP}",
                                 "trades": len(t), "days": len(days), "trades_per_day": len(t) / len(days),
                                 "busiest_day": busiest, "offered": offered, "sd_r": sd_r, "walk": walk_rows()[0]},
                     notes={"status": "the card's stop distribution (D-472); no campaign",
                            "seed": "none: a reading of the walk"},
                     description="A1-INS15's stops (D-472): one row per trade and state -- the Combine at 1:1 on every "
                                 "trade, the funded growth trade at 1:1.5 where the hour offers it -- its stop in micro "
                                 "ticks, the exit its state's bracket took and its date.")
        print(f"stop distribution: {len(t)} trades on {len(days)} days, the busiest day {busiest}")
        return 0
    from propedge.backtest.harness import PreregRegistry, UnregisteredRunError

    try:
        PreregRegistry.load().require_runnable(a.prereg)
    except UnregisteredRunError as exc:
        print(f"REFUSED ({DECISION}): {exc}")
        return 2
    t, days, rows = trades(rd)
    problems = identity_with_screen(rd, t, days)
    if problems:
        print("REFUSED (D-472): A1-INS15's trades are not the screen's cell -- " + "; ".join(problems))
        return 3
    return tg._registered_run(a.prereg, rd, results_dir, spec={**SPEC, "trades": lambda _rd: (t, days, rows)})


if __name__ == "__main__":
    raise SystemExit(main())