"""A signal-atlas family on the local bars (R5/R6, D-460): the walk, the identity against QuantConnect, the screen.

    python scripts/atlas_screen.py --family A1 --walk        # walk the development window into data/atlas/A1/
    python scripts/atlas_screen.py --family A1 --identity    # the clock pattern against R149-R151 (QuantConnect)
    python scripts/atlas_screen.py --family A1 --screen      # every declared cell through the campaign (EXPLORATORY)
    python scripts/atlas_screen.py --family A2 --screen      # D-481: A1's cells on A1's walk, each sized by its own
                                                             # re-solved state table -> results/atlas_screen_a2.csv
    python scripts/atlas_screen.py --family A3 --walk        # D-492: A1's events walked on FV3-C's rungs (data/atlas/A3)
    python scripts/atlas_screen.py --family A3 --screen      # D-492: FV3-C's v12 policy and protocol on each cell's rung
                                                             # trades (scripts/atlas_a3.py) -> results/atlas_screen_a3.csv

**A family on another's walk** (`walk_family` in its config; D-481: A2 reads A1's): the walk is that family's in every
respect -- its parameters, days and cache under `data/atlas/<walk family>/`, the cache's identity under that family's
config digest (`atlas_walk.walk_source`), so a change to its config or the bars forces the rebuild that family would do
and nothing else is ever written there; the borrowing family must declare every walk key identically, and `--rebuild`
and `--identity` are refused under it (run them under the walk's own family). Its screen holds each cell's row from the
walk family's screen beside it and refuses a cell whose trades differ from that row's.

**The identity** (the handoff's R5 acceptance; R12's comparison): the clock pattern's walks -- T24's 23 slots, on time
and five bars late, both sides, the twelve brackets -- against R149-R152's captures on 2020-01 to 2026-07-16, walk for
walk. QuantConnect settles a minute that reaches a target and a stop together on its second bars; locally every such
minute is the stop's, marked: those are counted apart. Everything else that differs is the data (Databento against
AlgoSeek), measured and declared, never adjusted away. Writes `results/atlas_identity_<family>.csv` (exploratory).

**The screen**: each cell -- a pattern and a side rule (follow its direction, or fade it; the clock its seeded coin) --
becomes a T24-format trades table: its events five bars late at the m40 map's stops (each event hour's widest stop to 40
points at which 1:1 resolves, every resolving R offered there), costs at R137's measured spreads by hour and year and the
micro fee, report-day trades before the 07:30 CT cut dropped; then T24's gf15 plan through the campaign engine, strictly
one position at a time, 150 paths at the point and at each R's one-sided 95 % bound over 21-session blocks. Ranked by
growth on the required bankroll at the bound. Writes `results/atlas_screen_<family>.csv` (exploratory: a screen; the
registered development verdict is the family's pre-registration's, at 500 paths and 0.05/N).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/atlas_screen.py"
IDENTITY_RUNS = ("results/manual_R149_t24_NQ_2021.csv", "results/manual_R150_t24_NQ_2023.csv",
                 "results/manual_R151_t24_NQ_2025.csv",
                 # D-473: P-10's capture of 2025-07-01 .. 2026-07-16 -- the same T24 capture line (brackets, slots,
                 # delays and cut identical), its window development since D-461 -- so the identity covers the whole
                 # development window, the second Databento file included (the gatekeeper's refusal, item 1)
                 "results/manual_R152_t24c_NQ_2026.csv")
IDENTITY_END = "2026-07-16"
FIELDS = ("o", "m", "g", "x")


def dev_days(cfg: dict, root: str) -> list[str]:
    from propedge.data.bars import manifest
    m = manifest(root) or {}
    lo, hi = str(cfg["development"]["start"]), str(cfg["development"]["end"])
    # every stored day: a short one is classified by the kits' own rule (an early close walks nothing), as on QuantConnect
    return [d for d in (m.get("day_list") or []) if lo <= d <= hi]


def load_walk(family: str, rebuild: bool = False):
    """(the family's own config, the walk's parameters, the walk's tables). The walk is the family's own, or the one
    its `walk_family` names (D-481: A2 reads A1's) -- that family's parameters, days and cache, under that family's
    config digest (`atlas_walk.walk_source`); the config returned is always the family's own (its plan and screen)."""
    from propedge.research import atlas_walk as AW
    cfg = AW.config(family)
    src, wcfg = AW.walk_source(family)
    q = AW.params(wcfg)
    days = dev_days(wcfg, wcfg["market"])
    return cfg, q, AW.cached(src, wcfg["market"], days, q, "development", rebuild=rebuild)


def identity(family: str) -> int:
    from propedge.reporting.results import read_result, write_result
    from propedge.research import atlas_walk as AW

    cfg, q, (events, walks, days) = load_walk(family)
    slots = set(AW.t24_slots())
    qc = pd.concat([read_result(ROOT / p) for p in IDENTITY_RUNS], ignore_index=True)
    qw = qc[qc["kind"] == "walk"].copy()
    qd = qc[qc["kind"] == "day"][["date", "day_kind"]].astype(str)
    lw = walks[(walks["slot"].isin(slots)) & (walks["date"].astype(str) <= IDENTITY_END)].copy()
    lw = lw.rename(columns={"slot": "decision_slot_minutes"})
    for d in (qw, lw):
        d["date"] = d["date"].astype(str)
        for k in ("decision_slot_minutes", "delay", "side"):
            d[k] = d[k].astype(int)
    key = ["date", "decision_slot_minutes", "delay", "side"]
    qdays = set(qd["date"])
    lw = lw[lw["date"].isin(qdays)]
    m = qw.merge(lw, on=key, how="outer", suffixes=("_qc", "_loc"), indicator=True)
    both = m[m["_merge"] == "both"]
    rows = [{"section": "coverage", "qc_walks": int((m["_merge"] != "right_only").sum()),
             "local_walks": int((m["_merge"] != "left_only").sum()), "both": int(len(both)),
             "only_qc": int((m["_merge"] == "left_only").sum()), "only_local": int((m["_merge"] == "right_only").sum())}]
    dk = qd.merge(days.astype(str), on="date", how="outer", suffixes=("_qc", "_loc"), indicator=True)
    rows.append({"section": "days", "both": int((dk["_merge"] == "both").sum()),
                 "only_qc": int((dk["_merge"] == "left_only").sum()), "only_local": int((dk["_merge"] == "right_only").sum()),
                 "kind_differs": int(((dk["_merge"] == "both") & (dk["day_kind_qc"] != dk["day_kind_loc"])).sum())})
    entry_same = (both["entry_slot_qc"].astype(int) == both["entry_slot_loc"].astype(int))
    for b, (T, S) in enumerate(q["bracket_points"]):
        oq, ol = both[f"o{b}_qc"].astype(str), both[f"o{b}_loc"].astype(str)
        mq, ml = both[f"m{b}_qc"].astype(int), both[f"m{b}_loc"].astype(int)
        same = (oq == ol) & (mq == ml)
        tie_loc = both[f"u{b}_loc"].astype(bool)
        tie_qc_t = tie_loc & (oq == "t")
        for y, g in both.groupby(both["date"].str[:4]):
            ix = g.index
            rows.append({"section": "bracket", "target": T, "stop": S, "year": int(y), "walks": int(len(g)),
                         "same_outcome_and_minutes": float(same.loc[ix].mean()),
                         "same_outcome": float((oq.loc[ix] == ol.loc[ix]).mean()),
                         "entry_same": float(entry_same.loc[ix].mean()),
                         "local_ties": int(tie_loc.loc[ix].sum()), "qc_target_where_local_tie": int(tie_qc_t.loc[ix].sum()),
                         "differ_not_tie": int((~same.loc[ix] & ~tie_loc.loc[ix]).sum())})
    out = pd.DataFrame(rows)
    write_result(out, f"atlas_identity_{family.lower()}", script=SCRIPT, seed=None, require_seed=False,
                 exploratory=True,
                 parameters={"family": family, "qc_runs": list(IDENTITY_RUNS), "end": IDENTITY_END,
                             "key": key, "brackets": [list(x) for x in q["bracket_points"]],
                             "bars": "data/bars/NQ (Databento GLBX.MDP3 ohlcv-1m, D-458)"},
                 description="The local walk (Databento bars, numpy walk, ties the stop's) against QuantConnect's "
                             "R149-R151 captures (AlgoSeek bars, ties on second bars), walk for walk: the data-source "
                             "and tie differences measured, never adjusted (R5, R12's comparison).",
                 notes={"status": "EXPLORATORY measurement of a second data source (D-460)"})
    c = rows[0]
    br = out[out["section"] == "bracket"]
    print(f"walks: {c['both']} in both, {c['only_qc']} only QuantConnect, {c['only_local']} only local; "
          f"same outcome and minutes {br['same_outcome_and_minutes'].mean():.4f} (mean over brackets and years); "
          f"local ties {int(br['local_ties'].sum())}, of them QuantConnect's target {int(br['qc_target_where_local_tie'].sum())}; "
          f"other differences {int(br['differ_not_tie'].sum())}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--family", required=True)
    ap.add_argument("--walk", action="store_true")
    ap.add_argument("--rebuild", action="store_true")
    ap.add_argument("--identity", action="store_true")
    ap.add_argument("--screen", action="store_true")
    a = ap.parse_args(argv)
    from propedge.research import atlas_walk as AW
    src, _ = AW.walk_source(a.family)
    if src != a.family and (a.rebuild or a.identity):
        # D-481 (1): the walk is the walk family's, read as it is -- rebuilt (when its inputs change) only by the same
        # rebuild that family would do, and its identity is that family's measurement
        print(f"REFUSED: {a.family} reads {src}'s walk; run --rebuild or --identity under --family {src}.")
        return 3
    if str(AW.config(a.family).get("plan")) == "v12_exact":
        # D-492: A3 reads A1's events (A1's cache, read only and checked) and walks them on FV3-C's rungs into its own
        # cache; its screen is FV3-C's campaign path (scripts/atlas_a3.py), not atlas_cells'
        import atlas_a3
        rc = atlas_a3.build_walk(a.family) if a.walk else 0
        return atlas_a3.screen(a.family) if (a.screen and rc == 0) else rc
    if a.walk:
        _, _, (ev, w, d) = load_walk(a.family, rebuild=a.rebuild)
        print(f"{len(d)} days ({(d['day_kind'] == 'n').sum()} normal), {len(ev)} events, {len(w)} walks")
    if a.identity:
        return identity(a.family)
    if a.screen:
        import atlas_cells
        return atlas_cells.screen(a.family)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
