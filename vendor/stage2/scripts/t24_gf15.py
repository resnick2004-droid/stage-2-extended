"""T24-GF15 (D-434): the registered test of T24's execution model -- the coin's trades at the bracket each fixed time
resolves (the m40 map, D-432), strictly one trade at a time, through five accounts under the operator's growth-then-flip
plan with the 1:1.5 growth trade, judged by the D-145 gate on development data.

    python scripts/t24_gf15.py --stop-distribution      # the card's stop distribution (no campaign)
    python scripts/t24_gf15.py --prereg P-xx            # the registered test; refused without a runnable id

The protocol, frozen as D-432 declared it and D-433 read it: at each of the 23 fixed times, five bars late, a seeded
coin's side (D-426); the time's stop -- the widest of 20 and 40 points at which 1:1 resolves on normal days overall and
in every year -- and the targets that resolve there; no entry before the 07:30 CT cut on a BLS report day; the Combine
1:1 at $1,600, one a session, closed once the room cannot carry another; a funded account at or below its start one
growth trade a session at $1,600 and 1:1.5, closed once the room cannot carry another; above its start a $240 1:1 flip
a session; strictly one position across all accounts (five minutes flat between).
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

SCRIPT = "scripts/t24_gf15.py"
DECISION = "D-434"
MODEL = "T24-GF15"
TOP = 40                                    # the m40 map
FAMILY = "gf15"
SEED = 20261028                             # the screen's campaign seed: the 0.05 arm reproduces D-433's line
SEED_BOOT, REPS = 20261017, 2000            # the eras' whole-year bootstrap and the day bootstrap (P-07's)
LEVELS = (0.0, 0.10, 0.25, 0.50)
K, WINDOW = 4, ("2020-01-01", "2025-06-30")
CHECK = ("2024-01-01", "2025-06-30")
ERAS = ((2020, 2022), (2023, 2025))


def trades(rd: Path):
    import t24_exec as te

    return te.trades(rd, TOP)


def policy():
    import t24_exec as te

    return te.fixed_policy(FAMILY)


def stop_distribution(t: pd.DataFrame) -> pd.DataFrame:
    """The card's stops (D-191, D-212): one row per trade and state -- its stop in micro ticks, the exit its state's
    bracket took and its date: the Combine and the flips at 1:1 on every trade; the funded growth trade at 1:1.5 where
    the time offers it."""
    kinds = {"t": "target", "s": "stop", "f": "flatten"}
    rows = [pd.DataFrame({"market": "NQ", "stop_ticks": t["stop_ticks"].astype(int), "state": "combine",
                          "exit": t["o_1"].map(kinds), "date": t["date"]})]
    g = t[t["o_1.5"].astype(str) != ""]
    rows.append(pd.DataFrame({"market": "NQ", "stop_ticks": g["stop_ticks"].astype(int), "state": "funded",
                              "exit": g["o_1.5"].map(kinds), "date": g["date"]}))
    return pd.concat(rows, ignore_index=True)


def period_rows(t: pd.DataFrame, days: list[str], menu: list[float], n_led: int, *, window=None, check=None,
                era_spans=None) -> list[dict]:
    """Per period and offered R: e and its bounds over 21-session blocks at 0.05 and 0.05/N, gross, cost and net (gross
    less cost checked equal to the net where offered), the target share and trades a day. `window`, `check` and
    `era_spans` default to T24's WINDOW, CHECK and ERAS (a spec may give its own, D-472)."""
    import confirm_fv3 as cf
    import fv3d_lever_test as lt

    window = WINDOW if window is None else tuple(window)
    check = CHECK if check is None else tuple(check)
    era_spans = ERAS if era_spans is None else tuple(tuple(x) for x in era_spans)
    periods = {"all": window, **{f"{a}-{b}": (f"{a}-01-01", f"{b}-12-31") for a, b in era_spans}, "check": check}
    rows = []
    for name, (lo, hi) in periods.items():
        tp, dp = lt.in_period(t, days, lo, hi)
        st = cf.edge_stats(tp, menu, dp, 21, n_led)
        for R in menu:
            m = np.isfinite(tp[f"r_{R:g}"].astype(float))
            g, c, r = (tp.loc[m, f"{x}_{R:g}"].astype(float) for x in ("g", "c", "r"))
            if m.any() and not np.allclose(g - c, r, atol=1e-9):
                raise SystemExit(f"REFUSED: gross less cost is not the net at R {R:g} ({name}).")
            rows.append({"section": "period", "period": name, "rr": R, "e": st[R]["e"], "lb": st[R]["lb"],
                         "lb_at_ledger_n": st[R]["lb_at_n"], "n": st[R]["n"],
                         "gross_r": float(g.mean()) if m.any() else np.nan,
                         "cost_r": float(c.mean()) if m.any() else np.nan,
                         "net_r": float(r.mean()) if m.any() else np.nan,
                         "target_share": float((tp.loc[m, f"o_{R:g}"] == "t").mean()) if m.any() else np.nan,
                         "trades_per_day": float(m.sum()) / len(dp) if dp else np.nan, "days": len(dp)})
    return rows


def eras(t: pd.DataFrame, days: list[str], menu: list[float], n_led: int, *, reps: int = REPS,
         seed: int = SEED_BOOT, era_spans=None) -> tuple[list[dict], bool, dict, dict]:
    """The card's rule (D-271): per offered R, the two eras' mean gross R by a bootstrap resampling whole years within
    each era (offered trades only); flagged when either R's 95 % interval of the difference excludes zero; each era's
    bounds over 21-session blocks at 0.05 and 0.05/N -- the lower era's read by the gate when flagged. `era_spans`
    defaults to T24's ERAS. An R the map offers at no hour (A1-INS15's 3:1) has no era to compare: its row says so,
    it flags nothing and draws nothing, and its bounds stay NaN as its pooled ones are."""
    import confirm_fv3 as cf
    import fv3d_lever_test as lt

    era_spans = ERAS if era_spans is None else tuple(tuple(x) for x in era_spans)
    rng = np.random.default_rng(seed)
    split = [lt.in_period(t, days, f"{a}-01-01", f"{b}-12-31") for a, b in era_spans]
    rows, flagged, low, low_n = [], False, {}, {}
    for R in menu:
        g = t[f"g_{R:g}"].astype(float)
        m = np.isfinite(g)
        if not m.any():
            low[float(R)], low_n[float(R)] = float("nan"), float("nan")
            rows.append({"section": "eras", "rr": R, "offered": 0, "flagged": False, "seed": seed, "reps": reps})
            continue
        yr = t.loc[m, "date"].astype(str).str[:4].astype(int)
        by_year = {int(y): (float(g[m][yr == y].sum()), int((yr == y).sum())) for y in sorted(yr.unique())}
        pools = [[y for y in by_year if a <= y <= b] for a, b in era_spans]
        diffs = np.empty(reps)
        for i in range(reps):
            mm = []
            for pool in pools:
                pick = rng.choice(pool, size=len(pool), replace=True)
                mm.append(sum(by_year[int(y)][0] for y in pick) / max(sum(by_year[int(y)][1] for y in pick), 1))
            diffs[i] = mm[1] - mm[0]
        lo, hi = np.percentile(diffs, [2.5, 97.5])
        fl = bool(lo > 0 or hi < 0)
        flagged |= fl
        st = [cf.edge_stats(te_, [R], de, 21, n_led)[float(R)] for te_, de in split]
        low[float(R)], low_n[float(R)] = min(s["lb"] for s in st), min(s["lb_at_n"] for s in st)
        rows.append({"section": "eras", "rr": R, "diff_lo": float(lo), "diff_hi": float(hi), "flagged": fl,
                     "era1_lb": st[0]["lb"], "era2_lb": st[1]["lb"], "era1_lb_at_ledger_n": st[0]["lb_at_n"],
                     "era2_lb_at_ledger_n": st[1]["lb_at_n"], "seed": seed, "reps": reps})
    return rows, flagged, low, low_n


def sharpe_rows(t: pd.DataFrame, days: list[str], menu: list[float], n_led: int) -> list[dict]:
    """Beside the verdict (D-189): per offered R, the deflated Sharpe ratio of its 21-session block means at N, and
    `haircut.widened`'s day-bootstrap and normal bounds at 0.05/N (offered trades only)."""
    import confirm_fv3 as cf

    from propedge.research.haircut import deflated_sharpe, widened

    pos = {d: i for i, d in enumerate(days)}
    rows = []
    for R in menu:
        m = np.isfinite(t[f"r_{R:g}"].astype(float))
        if not m.any():                                    # an R the map offers at no hour: nothing to read
            rows.append({"section": "sharpe", "rr": R, "offered": 0, "ledger_n": int(n_led)})
            continue
        tr = t[m]
        r = tr[f"r_{R:g}"].astype(float)
        blk = cf.block_of(tr["date"], days, 21)
        d = deflated_sharpe(r.groupby(blk).mean().dropna().to_numpy(), int(n_led))
        w = widened(r.to_numpy(), tr["date"].astype(str).map(pos).to_numpy(int), len(days), int(n_led), block=21,
                    reps=REPS, seed=SEED_BOOT)
        rows.append({"section": "sharpe", "rr": R, "block_sr": d["sr"], "block_T": d["T"],
                     "deflated_sharpe_blocks": d["dsr"], "lb_bootstrap_widened": w["lb_bootstrap_widened"],
                     "lb_normal_widened": w["lb_normal_widened"], "lb_widened": w["lb_widened"],
                     "deflated_sharpe_daily": w["daily_dsr"], "ledger_n": int(n_led)})
    return rows


def run(blocks, e_by, lb_by, hook, *, rtp: bool, levels=LEVELS, pol=None, proto=None) -> pd.DataFrame:
    """The campaign: T24-GF15's engine call; `pol` the plan (T24-GF15's by default), `proto` the protocol (T24's,
    `t24_wide.protocol()`, by default)."""
    import score_fv3_grid as gf
    import t24_wide as tw

    from propedge.campaign import gate
    from propedge.campaign.payout_method import rules_for_method

    df, _ = gate.run_gate(list(blocks), e=e_by[1.0], lb=lb_by[1.0],
                          protocol=proto if proto is not None else tw.protocol(), bankroll=gf.UNBOUND_BANKROLL,
                          horizon_days=tw.HORIZON, n_paths=tw.N_PATHS, seed=SEED, accounts=tw.ACCOUNTS,
                          sizing=tw.sizing(), rules=rules_for_method("aeropay"), mode="rotation",
                          settlement="pessimistic", combines=tw.ACCOUNTS, total_accounts=tw.ACCOUNTS,
                          risk_policy=pol if pol is not None else policy(), e_by_rr=e_by, lb_by_rr=lb_by,
                          levels=tuple(levels), path_hook=hook,
                          rtp=rtp, routing="able", cross_account=True, hold_to_own_exit=True, one_at_a_time=tw.GAP)
    df["placement"] = "on" if rtp else "off"
    return df


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.reporting.results import write_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--stop-distribution", action="store_true")
    ap.add_argument("--prereg", default=None)
    a = ap.parse_args(argv)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    if a.stop_distribution:
        t, days, _ = trades(rd)
        write_result(stop_distribution(t), "t24_gf15_stop_distribution", script=SCRIPT, seed=None, require_seed=False,
                     exploratory=True, results_dir=results_dir,
                     parameters={"decision": DECISION, "map": f"m{TOP}", "trades": len(t)},
                     notes={"status": "the card's stop distribution (D-434); no campaign",
                            "seed": "none: a reading of the capture"},
                     description="T24-GF15's stops (D-434): one row per trade and state, its stop in micro ticks, the "
                                 "exit its state's bracket took and its date.")
        print(f"stop distribution: {len(t)} trades")
        return 0
    from propedge.backtest.harness import PreregRegistry, UnregisteredRunError

    try:
        PreregRegistry.load().require_runnable(a.prereg)
    except UnregisteredRunError as exc:
        print(f"REFUSED (D-434): {exc}")
        return 2
    return _registered_run(a.prereg, rd, results_dir)


#: D-439: the registered run's identity -- T24-GF15's (P-08) by default; T24-GF15b (`scripts/t24_gf15b.py`) passes its own.
#: D-472 (A1-INS15, `scripts/a1_ins15.py`): the development window, the check period and the eras are the spec's, T24's
#: by default; and five keys whose defaults leave P-08's and P-09's runs exactly as registered -- `protocol` (a callable
#: of the trades returning the campaign's protocol; None: T24's), `realised_min` (None: no fidelity line; a number: the
#: gate row's `realised_to_intended_capped_risk` must reach it, docs/SUCCESS_CRITERIA.md §3), `paths_file` (False: no
#: per-path record; True: every path of every campaign in `<result>_paths.csv`, D-465), `parameters` (extra manifest
#: parameters) and `description` (the result's description; None: T24's).
#: A2-NB158 (`scripts/a2_nb158.py`, D-485, D-488): two keys whose defaults leave P-08's, P-09's and P-11's runs exactly
#: as registered (no campaign, no row, no column added). `fixed_legs` -- None, or a callable returning stage one's fixed
#: legs as a policy: the fixed-legs twin docs/SUCCESS_CRITERIA.md §4 asks beside a verdict whose plan is a table, in
#: P-06's form (`portfolio_stage.twins`, D-304, D-355) -- the same trades, blocks, bounds, protocol and seed under those
#: legs, placement off, 0 % denial, its point arm (as traded) as one row in section `twin` with `twin` = `fixed_legs`
#: (P-06's names; the per-path record's label `twin fixed_legs`, P-06's), beside the verdict and never part of it.
#: `beside_plans` -- empty, or a sequence of (section, callable returning a policy): other plans read on the same
#: trades, blocks, bounds, protocol and seed, placement off, 0 % denial, their point and bound rows in that section (and
#: so labelled in the per-path record) -- extra readings beside the verdict, never deciding, never the fixed-legs twin.
GF15 = {"model": MODEL, "decision": DECISION, "script": SCRIPT, "result": "t24_gf15_gate", "k": K, "label": "T24-GF15",
        "policy": None, "trades": None, "window": WINDOW, "check": CHECK, "eras": ERAS, "protocol": None,
        "realised_min": None, "paths_file": False, "parameters": None, "description": None, "fixed_legs": None,
        "beside_plans": ()}


def _registered_run(pid: str, rd: Path, results_dir: Path | None, spec: dict | None = None, *,
                    reproduce: bool = False) -> int:
    """The registered run of `pid` under `spec`: inputs read from `rd`, files written into `results_dir`. `reproduce`
    (R11, `scripts/reproduce_registered.py` only) reruns a completed registration: the same computation, nothing
    appended to the variant ledger, the files written by `propedge.reporting.reproduction.writer` into `results_dir`
    (outside the repository), exploratory and labelled a reproduction. False -- the default -- is the registered run."""
    import confirm_fv3 as cf
    import fv3d_lever_test as lt
    import portfolio_stage as ps
    import score_fv3_grid as gf
    import t23_d20 as td
    import t24_exec as te
    import t24_wide as tw

    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import write_result
    from propedge.research import ledger as lg

    if reproduce:                                          # R11: checked before any work; the same call, relabelled
        from propedge.reporting.reproduction import writer

        write_result = writer(pid, results_dir)            # noqa: F811 -- outside the repository, exploratory
    sp = {**GF15, **(spec or {})}
    window, check = tuple(sp["window"]), tuple(sp["check"])
    era_spans = tuple(tuple(x) for x in sp["eras"])
    pol = sp["policy"]() if sp["policy"] is not None else policy()
    t, days, map_rows = (sp["trades"] or trades)(rd)
    proto = sp["protocol"](t) if sp["protocol"] is not None else None
    menu = list(te.RRS)
    n_led = lg.count_n(lg.load_ledger(), model=sp["model"], k=sp["k"], markets=["NQ"], window=window)["N"]
    stats = cf.edge_stats(t, menu, days, 21, n_led)
    by_k = cf.edge_stats(t, menu, days, 21, sp["k"])
    era_rows, flagged, low, low_n = eras(t, days, menu, n_led, era_spans=era_spans)
    e_by = ps._by(stats, "e")
    lb_by = low if flagged else ps._by(stats, "lb")
    lbn_by = low_n if flagged else ps._by(stats, "lb_at_n")
    blocks, n_used = gf.gate_blocks(t, days, 0.25 * 2.0, menu, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise SystemExit("REFUSED: the blocks hold a different number of trades.")
    paths_rows: list[dict] = []
    inner = ps.composed_hook({"margin": tw.MARGIN, "block_days": tw.BLOCK}, sink=paths_rows if sp["paths_file"] else None)
    hook = lt.lever_hook(inner)

    def label(text: str) -> None:                          # names each campaign in the per-path record (D-465)
        if sp["paths_file"]:
            ps._label(inner, text)

    label("gate")
    gate_df = run(blocks, e_by, lb_by, hook, rtp=False, pol=pol, proto=proto)
    gate_df.insert(0, "section", "gate")
    label("gate_at_ledger_n")
    n_df = run(blocks, e_by, lbn_by, hook, rtp=False, levels=(0.0,), pol=pol, proto=proto)
    n_df = n_df[n_df["shift"] == "lower_bound"]
    n_df.insert(0, "section", "gate_at_ledger_n")
    label("placement_on")
    on_df = run(blocks, e_by, lb_by, hook, rtp=True, levels=(0.0,), pol=pol, proto=proto)
    on_df.insert(0, "section", "placement_on")
    zero = {k: 0.0 for k in e_by}
    label("zero_edge_twin")
    z_df = run(ps.zero_edge_blocks(blocks, e_by, 1.0), zero, zero, hook, rtp=False, levels=(0.0,), pol=pol, proto=proto)
    z_df = z_df[z_df["shift"] == "point"]
    z_df.insert(0, "section", "zero_edge_twin")
    twins = [z_df]
    if sp["fixed_legs"] is not None:                       # a table's fixed-legs twin, P-06's form (SUCCESS_CRITERIA §4)
        label("twin fixed_legs")
        f_df = run(blocks, e_by, lb_by, hook, rtp=False, levels=(0.0,), pol=sp["fixed_legs"](), proto=proto)
        f_df = f_df[f_df["shift"] == "point"].copy()       # P-06's twins: the point arm, as traded
        f_df.insert(0, "section", "twin")
        f_df["twin"] = "fixed_legs"
        twins.append(f_df)
    for section, plan in sp["beside_plans"]:               # other plans on the same trades: beside, never deciding
        label(section)
        b_df = run(blocks, e_by, lb_by, hook, rtp=False, levels=(0.0,), pol=plan(), proto=proto)
        b_df.insert(0, "section", section)
        twins.append(b_df)
    tc_, dc = lt.in_period(t, days, *check)
    st_c = cf.edge_stats(tc_, menu, dc, 21, None)
    bc, _ = gf.gate_blocks(tc_, dc, 0.25 * 2.0, menu, require_sides=True, require_exits=True)
    label("check_years")
    c_df = run(bc, ps._by(st_c, "e"), ps._by(st_c, "lb"), hook, rtp=False, levels=(0.0,), pol=pol, proto=proto)
    c_df.insert(0, "section", "check_years")
    g_n = float(n_df.iloc[0]["pf_growth_on_base_p50"])
    row = gate_df[(gate_df["shift"] == "lower_bound") & np.isclose(gate_df["enforcement_p"].astype(float), 0.0)].iloc[0]
    g = float(row["pf_growth_on_base_p50"])
    res_rows = te.resolution_rows(t)
    resolves = all(r["resolves"] for r in res_rows)
    fidelity, v_extra = True, {}
    if sp["realised_min"] is not None:                     # docs/SUCCESS_CRITERIA.md §3: realised risk, the gate row
        realised = float(row.get("realised_to_intended_capped_risk", float("nan")))
        fidelity = bool(np.isfinite(realised) and realised >= float(sp["realised_min"]))
        v_extra = {"realised_to_intended_capped_risk": realised, "realised_min": float(sp["realised_min"]),
                   "fidelity": fidelity}
    if proto is not None:
        v_extra["trades_per_day_capacity"] = int(proto.trades_per_day)
    word = td.verdict_of(g, g_n) if (resolves and fidelity) else "FAIL"
    edges = pd.DataFrame([{"section": "edge", "rr": R, "e": stats[R]["e"], "lb": stats[R]["lb"], "n": stats[R]["n"],
                           "sd": stats[R]["sd"], "lb_at_ledger_n": stats[R]["lb_at_n"], "ledger_n": n_led,
                           "lb_at_k": by_k[R]["lb_at_n"], "k": sp["k"], "lb_gate": lb_by[float(R)],
                           "lb_gate_at_ledger_n": lbn_by[float(R)],
                           "d47_met": bool(stats[R]["e"] >= 0.10 and stats[R]["lb"] >= 0.05)} for R in menu])
    verdict = pd.DataFrame([{"section": "verdict", "prereg": pid, "gate_growth_on_base_p50": g,
                             "gate_at_ledger_n_growth_on_base_p50": g_n, "resolves": resolves, "verdict": word,
                             "era_flagged": flagged, "bounds_read": "the lower era's" if flagged else "pooled",
                             "trades": len(t), "days": len(days), **v_extra}])
    beside = pd.DataFrame(map_rows + res_rows
                          + period_rows(t, days, menu, n_led, window=window, check=check, era_spans=era_spans)
                          + era_rows + sharpe_rows(t, days, menu, n_led))
    res = pd.concat([gate_df, n_df, on_df, *twins, c_df, edges, beside, verdict], ignore_index=True)
    counter = VariantCounter(path=rd / "variants.jsonl")
    if not reproduce:                                      # a reproduction is not a configuration tried (R11)
        counter.record(prereg_id=pid, seed=SEED, exploratory=False,
                       params={"study": f"{sp['label']} gate", "decision": sp["decision"]},
                       label=f"{sp['label']}'s registered test ({pid})")
    params = {"decision": sp["decision"], "prereg": pid, "map": f"m{TOP}", "family": FAMILY,
              "model": sp["model"],
              "two_shot": te.TWO_SHOT, "growth": [te.GROWTH_RISK, te.GROWTH[FAMILY]], "flip": list(te.FLIP),
              "n_paths": tw.N_PATHS, "horizon": tw.HORIZON, "levels": list(LEVELS), "k": sp["k"],
              "window": list(window), "check": list(check), "ledger_n": n_led, "eras": [list(x) for x in era_spans],
              "seed_bootstrap": SEED_BOOT, "reps": REPS, "rule": "strict, five minutes",
              "unresolved_max": te.UNRESOLVED_MAX, "cut": te.CUT, "payout_method": "aeropay"}
    if proto is not None:
        params["trades_per_day_capacity"] = int(proto.trades_per_day)
    if sp["realised_min"] is not None:
        params["realised_min"] = float(sp["realised_min"])
    if sp["paths_file"]:
        params["paths_file"] = f"{sp['result']}_paths.csv"
    params.update(sp["parameters"] or {})
    write_result(res, sp["result"], script=sp["script"], seed=SEED, exploratory=False, results_dir=results_dir,
                 prereg_id=pid, variant_count=counter.count(pid), parameters=params,
                 notes={"status": f"the registered test of {sp['label']} ({pid}, {sp['decision']})"},
                 description=sp["description"] or (
                     f"{sp['label']}'s registered test ({sp['decision']}): the coin's trades at the bracket each time "
                     "resolves, strictly one at a time, the growth-then-flip plan; the D-145 gate at 0.05/N and 0.05."))
    if sp["paths_file"]:
        write_result(pd.DataFrame(paths_rows), f"{sp['result']}_paths", script=sp["script"], seed=SEED,
                     exploratory=False, prereg_id=pid, results_dir=results_dir, variant_count=counter.count(pid),
                     parameters={"result": f"{sp['result']}.csv", "prereg": pid, "model": sp["model"]},
                     notes={"status": f"the registered test of {sp['label']} ({pid}, {sp['decision']})",
                            "companion_of": f"{sp['result']}.csv"},
                     description=f"The per-path record of {sp['result']}.csv (D-465): every resampled path of every "
                                 "campaign the registered run ran, labelled by its section, so its rows can be "
                                 "re-derived from the files.")
    print(f"{'REPRODUCTION, not a verdict' if reproduce else 'VERDICT'} ({pid}): {word} -- growth on the required "
          f"bankroll {g:+.4f} at the 95 % bound, {g_n:+.4f} at 0.05/N; resolves {resolves}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
