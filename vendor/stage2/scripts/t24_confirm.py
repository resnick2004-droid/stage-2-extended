"""T24-GF15b's one confirmation (D-439): the frozen protocol on NQ's held-back window, 2025-07-01 to 2026-07-16.

    python scripts/t24_confirm.py --prereg P-xx         # refused without a runnable registration

Runnable only once T24-GF15b's development test (its registration, `results/t24_gf15b_gate.csv`) is a PASS or a CONTINUE.
Everything is frozen before the window is read (D-434, D-438, D-439): the m40 map and its offered targets are READ from
`results/t24_exec_m40.csv` (its `map` rows, from the development capture), never recomputed on the window; the coin's
seed, the entry five bars late, the report-day cut, the plan (the Combine 1:1 $1,600 two-shot; the funded growth trade
$1,600 at 1:1.5 at or below the start; $240 flips above it; every state closed once it cannot carry its trade, D-438 (3)),
the gap booked as a cost, the strict rule, the engine and its seed are T24-GF15b's development test's. The
costs: each trade's own inside its R, the slot's measured spread from R137 -- its 2025 value for the window's trades, the
latest year measured (R137 ends in 2025). The verdict is P-06's four lines, all required:

    C1  the gate: growth on the required bankroll above zero with each R's outcomes at the one-sided 95 % bound of its mean
        over 21-session blocks of the window, 0 % denial, the placement off
    C2  every counted period's own campaign (its trades resampled within it, at the point) grows on its required bankroll,
        its activity bound is above one half, and no path's Sharpe changes sign without its idle blocks (D-305) -- 2025 H2
        and 2026 H1; 2026 Q3 (to July 16) is reported, not counted
    C3  the gate row's break-even denial at least 0.25, and the bound arm still growing at 10 % denial
    C4  every offered R resolves -- at most 5 % unresolved overall and in each counted period -- the realised risk is at
        least 0.9 of the allowance-capped intention, and no counted period is without a trade
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

SCRIPT = "scripts/t24_confirm.py"
DECISION = "D-439"
MODEL = "T24-GF15b"
DEV_RESULT = "results/t24_gf15b_gate.csv"
CAPTURE = "results/manual_R152_t24c_NQ_2026.csv"
MAP_FILE = "results/t24_exec_m40.csv"
WINDOW = ("2025-07-01", "2026-07-16")
PERIODS = {"2025H2": ("2025-07-01", "2025-12-31"), "2026H1": ("2026-01-01", "2026-06-30"),
           "2026Q3": ("2026-07-01", "2026-07-16")}
COUNTED = ("2025H2", "2026H1")
SPREAD_YEAR = 2025                          # R137's latest year, for the window's trades
SEED = 20261028                             # P-08's campaign seed
LEVELS = (0.0, 0.10, 0.25, 0.50)
BREAK_EVEN_MIN, REALISED_MIN = 0.25, 0.90
K, DEV_WINDOW = 1, ("2020-01-01", "2025-06-30")


def frozen_map(rd: Path) -> tuple[dict[str, int], dict[tuple[str, int, float], bool]]:
    """The m40 map as P-08's screen recorded it: each time's stop and the targets it offers."""
    from propedge.reporting.results import read_result

    m = read_result(rd / Path(MAP_FILE).name)
    m = m[m["section"] == "map"]
    if not len(m):
        raise SystemExit(f"REFUSED: {MAP_FILE} carries no map rows (D-432).")
    smap, offered = {}, {}
    for r in m.itertuples():
        ct, S = str(r.decision_ct), int(r.stop)
        smap[ct] = S
        rs = {float(x) for x in str(r.offered).split(",") if x}
        for R in (1.0, 1.5, 2.0, 3.0):
            offered[(ct, S, R)] = R in rs
    return smap, offered


def trades(rd: Path) -> tuple[pd.DataFrame, list[str]]:
    """The window's coin trades at the frozen map's stops and targets (NaN where not offered), report-day trades before
    the cut dropped, the costs inside R at the slot's measured spread (its 2025 value), the fee a micro priced in."""
    import t23_choose as tc
    import t24_exec as te
    import t24_wide as tw

    from propedge.reporting.results import read_result

    smap, offered = frozen_map(rd)
    bix = tw.bracket_index("R149-t24-NQ-2021")
    raw = read_result(rd / Path(CAPTURE).name)
    walks, days = raw[raw["kind"] == "walk"].copy(), raw[raw["kind"] == "day"].copy()
    walks["year"] = walks["date"].astype(str).str[:4].astype(int)
    base = walks[walks["delay"].astype(int) == tw.DELAY].copy()
    base["coin"] = tw.coin(base)
    t = base[base["side"].astype(int) == base["coin"]].copy()
    kind = dict(zip(days["date"].astype(str), days["day_kind"].astype(str)))
    t["day_kind"] = t["date"].astype(str).map(kind)
    t = t[t["decision_ct"].astype(str).isin(smap)]
    t = t[~((t["day_kind"].astype(str) == "b") & (t["decision_slot_minutes"].astype(int) < te.CUT))].copy()
    t["S"] = t["decision_ct"].astype(str).map(smap).astype(int)
    sp = read_result(rd / Path(tc.R137).name)
    sp = sp[(sp["kind"] == "spread") & (sp["year"].astype(float) == SPREAD_YEAR)]
    by_slot = {str(r.decision_ct): float(r.spread_ticks_mean) for r in sp.itertuples() if float(r.quotes) > 0}
    spread = {(ct, int(y)): by_slot[ct] for ct in smap if ct in by_slot for y in t["year"].unique()}
    t["entry_t"] = t["entry_slot"].astype(float)
    parts = []
    for S, g in t.groupby("S"):
        g = g.copy()
        for R in te.RRS:
            b = bix[(R * S, float(S))]
            off = np.array([offered[(ct, S, R)] for ct in g["decision_ct"].astype(str)])
            r = tc.trade_r(g, b, R * S, float(S), spread, tw.FEE_MICRO)
            gr, co = tc.trade_parts(g, b, R * S, float(S), spread, tw.FEE_MICRO)
            g[f"r_{R:g}"] = np.where(off, r, np.nan)
            g[f"g_{R:g}"] = np.where(off, gr, np.nan)
            g[f"c_{R:g}"] = np.where(off, co, np.nan)
            g[f"o_{R:g}"] = np.where(off, g[f"o{b}"].astype(str), "")
            g[f"exit_t_{R:g}"] = np.where(off, g["entry_t"] + g[f"m{b}"].astype(float), np.nan)
            g[f"mae_{R:g}"] = np.nan
        g["stop_ticks"] = int(round(S / 0.25))
        parts.append(g)
    t = pd.concat(parts).sort_values(["date", "entry_t"], kind="stable").reset_index(drop=True)
    t["exit_t"] = t[[f"exit_t_{R:g}" for R in te.RRS]].max(axis=1)
    t["flat"] = t["o_1"] == "f"
    t["fee_micro_eq"] = tw.FEE_MICRO
    t["side"] = np.where(t["side"].astype(int) > 0, "long", "short")
    t["date"] = t["date"].astype(str)
    import t24_gf15b as tb

    return tb.gap_as_cost(t), sorted(days["date"].astype(str))


def resolution(t: pd.DataFrame) -> list[dict]:
    """Each offered R's unresolved share overall and in each period (the trades as taken)."""
    out = []
    for R in (1.0, 1.5, 2.0, 3.0):
        o = t[f"o_{R:g}"].astype(str)
        m = o != ""
        if not m.any():
            continue
        row = {"section": "resolution", "rr": R, "offered": int(m.sum()), "unresolved": float((o[m] == "f").mean())}
        for name, (lo, hi) in PERIODS.items():
            pm = m & (t["date"] >= lo) & (t["date"] <= hi)
            row[f"unresolved_{name}"] = float((o[pm] == "f").mean()) if pm.any() else np.nan
        row["resolves"] = bool(row["unresolved"] <= 0.05 and all(
            (row[f"unresolved_{p}"] <= 0.05) for p in COUNTED if np.isfinite(row[f"unresolved_{p}"])))
        out.append(row)
    return out


def lines(gate_df: pd.DataFrame, periods: dict[str, dict], res: list[dict]) -> dict[str, bool]:
    """P-06's four lines on the run's rows (`scripts/confirm_fv3.py`'s, D-355): `periods` maps each period to its point
    campaign's growth, activity bound, Sharpe-flip share and trades."""
    def ok(x, test) -> bool:
        x = float(x)
        return bool(np.isfinite(x) and test(x))

    lb = gate_df[(gate_df["shift"] == "lower_bound")]
    b0 = lb[np.isclose(lb["enforcement_p"].astype(float), 0.0)].iloc[0]
    b10 = lb[np.isclose(lb["enforcement_p"].astype(float), 0.10)].iloc[0]
    counted = [periods.get(p) for p in COUNTED]
    c2 = all(c is not None and ok(c["growth"], lambda x: x > 0) and ok(c["activity"], lambda x: x > 0.5)
             and ok(c["sharpe_flip"], lambda x: x == 0) for c in counted)
    c4 = (all(r["resolves"] for r in res) and ok(b0["realised_to_intended_capped_risk"], lambda x: x >= REALISED_MIN)
          and all(c is not None and c["trades"] > 0 for c in counted))
    return {"C1": ok(b0["pf_growth_on_base_p50"], lambda x: x > 0), "C2": bool(c2),
            "C3": ok(b0["pf_break_even_denial_p50"], lambda x: x >= BREAK_EVEN_MIN)
                  and ok(b10["pf_growth_on_base_p50"], lambda x: x > 0),
            "C4": bool(c4)}


def run(blocks, e_by, lb_by, hook, *, rtp: bool = False, levels=LEVELS) -> pd.DataFrame:
    """T24-GF15b's campaign (its plan; P-08's engine, strict rule and seed -- the same as SEED here)."""
    import t24_gf15 as tg
    import t24_gf15b as tb

    assert tg.SEED == SEED
    return tg.run(blocks, e_by, lb_by, hook, rtp=rtp, levels=levels, pol=tb.policy())


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--prereg", default=None)
    a = ap.parse_args(argv)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    from propedge.backtest.harness import PreregRegistry, UnregisteredRunError

    try:
        PreregRegistry.load().require_runnable(a.prereg)
    except UnregisteredRunError as exc:
        print(f"REFUSED (D-439): {exc}")
        return 2
    word = development_verdict(rd)
    if word not in ("PASS", "CONTINUE"):
        print(f"REFUSED (D-439): T24-GF15b's development test reads {word!r}; the confirmation runs only after a PASS or "
              "a CONTINUE.")
        return 2
    return _registered_run(a.prereg, rd, results_dir)


def development_verdict(rd: Path) -> str:
    """T24-GF15b's development verdict, or 'none' before its test has run."""
    from propedge.reporting.results import read_result

    f = rd / Path(DEV_RESULT).name
    if not f.is_file():
        return "none"
    v = read_result(f)
    v = v[v["section"] == "verdict"]
    return str(v.iloc[0]["verdict"]) if len(v) else "none"


def _registered_run(pid: str, rd: Path, results_dir: Path | None, *, reproduce: bool = False) -> int:
    """The registered confirmation of `pid`: inputs read from `rd`, the file written into `results_dir`. `reproduce`
    (R11, `scripts/reproduce_registered.py` only) reruns the completed registration: the same computation, nothing
    appended to the variant ledger, the file written by `propedge.reporting.reproduction.writer` into `results_dir`
    (outside the repository), exploratory and labelled a reproduction. False -- the default -- is the registered run."""
    import confirm_fv3 as cf
    import fv3d_lever_test as lt
    import portfolio_stage as ps
    import score_fv3_grid as gf
    import t24_gf15 as tg
    import t24_wide as tw

    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import write_result
    from propedge.research import ledger as lg

    if reproduce:                                          # R11: checked before any work; the same call, relabelled
        from propedge.reporting.reproduction import writer

        write_result = writer(pid, results_dir)            # noqa: F811 -- outside the repository, exploratory
    t, days = trades(rd)
    menu = [1.0, 1.5, 2.0, 3.0]
    n_led = lg.count_n(lg.load_ledger(), model=MODEL, k=K, markets=["NQ"], window=DEV_WINDOW)["N"]
    stats = cf.edge_stats(t, menu, days, 21, n_led)
    e_by, lb_by = ps._by(stats, "e"), ps._by(stats, "lb")
    blocks, n_used = gf.gate_blocks(t, days, 0.25 * 2.0, menu, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise SystemExit("REFUSED: the blocks hold a different number of trades.")
    hook = lt.lever_hook(ps.composed_hook({"margin": tw.MARGIN, "block_days": tw.BLOCK}))
    gate_df = run(blocks, e_by, lb_by, hook)
    gate_df.insert(0, "section", "gate")
    on_df = run(blocks, e_by, lb_by, hook, rtp=True, levels=(0.0,))
    on_df.insert(0, "section", "placement_on")
    zero = {k: 0.0 for k in e_by}
    z_df = run(ps.zero_edge_blocks(blocks, e_by, 1.0), zero, zero, hook, levels=(0.0,))
    z_df = z_df[z_df["shift"] == "point"]
    z_df.insert(0, "section", "zero_edge_twin")
    n_df = run(blocks, e_by, ps._by(stats, "lb_at_n"), hook, levels=(0.0,))
    n_df = n_df[n_df["shift"] == "lower_bound"]
    n_df.insert(0, "section", "beside_at_ledger_n")
    per_rows, per_growth = [], {}
    for name, (lo, hi) in PERIODS.items():
        tp, dp = lt.in_period(t, days, lo, hi)
        if not len(tp):
            continue
        st = cf.edge_stats(tp, menu, dp, 21, None)
        bp, _ = gf.gate_blocks(tp, dp, 0.25 * 2.0, menu, require_sides=True, require_exits=True)
        df = run(bp, ps._by(st, "e"), ps._by(st, "lb"), hook, levels=(0.0,))
        df = df[df["shift"] == "point"]
        df.insert(0, "period", name)
        df.insert(0, "section", "period_campaign")
        per_rows.append(df)
        r0 = df.iloc[0]
        per_growth[name] = {"growth": float(r0["pf_growth_on_base_p50"]),
                            "activity": float(r0.get("pf_activity_bound_p50", np.nan)),
                            "sharpe_flip": float(r0.get("pf_share_sharpe_sign_changed_without_idle", np.nan)),
                            "trades": int(len(tp))}
    res = resolution(t)
    ok = lines(gate_df, per_growth, res)
    word = "PASS" if all(ok.values()) else "FAIL"
    edges = pd.DataFrame([{"section": "edge", "rr": R, "e": stats[R]["e"], "lb": stats[R]["lb"], "n": stats[R]["n"],
                           "sd": stats[R]["sd"], "lb_at_ledger_n": stats[R]["lb_at_n"], "ledger_n": n_led,
                           "gross_r": float(np.nanmean(t[f"g_{R:g}"])) if stats[R]["n"] else np.nan,
                           "cost_r": float(np.nanmean(t[f"c_{R:g}"])) if stats[R]["n"] else np.nan} for R in menu])
    verdict = pd.DataFrame([{"section": "verdict", "prereg": pid, "verdict": word, **ok,
                             "failed_lines": ",".join(k for k, v in ok.items() if not v), "trades": len(t),
                             "days": len(days), "window_first": days[0] if days else "", "window_last": days[-1] if days else "",
                             "counted_periods": ",".join(p for p in COUNTED if p in per_growth)}])
    beside = pd.DataFrame(res + tg.sharpe_rows(t, days, menu, n_led))
    out = pd.concat([gate_df, n_df, on_df, z_df, *per_rows, edges, beside, verdict], ignore_index=True)
    counter = VariantCounter(path=rd / "variants.jsonl")
    if not reproduce:                                      # a reproduction is not a configuration tried (R11)
        counter.record(prereg_id=pid, seed=SEED, exploratory=False,
                       params={"study": "T24-GF15b confirmation", "decision": DECISION},
                       label=f"T24-GF15b's confirmation ({pid})")
    write_result(out, "t24_confirmation", script=SCRIPT, seed=SEED, exploratory=False, results_dir=results_dir,
                 prereg_id=pid, variant_count=counter.count(pid),
                 parameters={"decision": DECISION, "prereg": pid, "window": list(WINDOW), "periods": PERIODS,
                             "counted": list(COUNTED), "map_file": MAP_FILE, "spread_year": SPREAD_YEAR,
                             "levels": list(LEVELS), "break_even_min": BREAK_EVEN_MIN, "realised_min": REALISED_MIN,
                             "ledger_n": n_led, "rule": "strict, five minutes", "payout_method": "aeropay"},
                 notes={"status": f"T24-GF15b's one confirmation ({pid}, D-439)"},
                 description="T24-GF15b's confirmation (D-439): the frozen protocol on NQ's held-back window; P-06's four "
                             "lines.")
    print(f"{'REPRODUCTION, not a verdict' if reproduce else 'VERDICT'} ({pid}): {word} -- " + ", ".join(f"{k} {'met' if v else 'NOT met'}" for k, v in ok.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
