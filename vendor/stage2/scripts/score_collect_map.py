"""EXPLORATORY (D-381): the collect map's choice -- the XFA's winning-day bracket (its hour, its micro count, its box) and
the menu of stops the funded table may choose from -- by the rules fixed in config/collect_map.yaml before its data was
read.

    python scripts/score_collect_map.py          # reads results/manual_R145_collect_NQ.csv

Every bracket has the same $200 target (5, 10 or 20 MNQ at 20, 10 or 5 points) and a stop of one to eight times the
target. Per period (CHOICE 2021-2023, CHECK 2024 to June 2025, 2020 beside), slot, micro count, stop multiple, box and
entry delay, both sides pooled: the shares at the target, the stop and the scratch; the share resolved inside the box;
the mean minutes to resolution; the dollars at the bracket's micros -- +$200 at the target, the stop's dollars at the
stop, the scratch's P&L -- less the cost per attempt (the MNQ round turn, the slot's entry spread beyond the walk's tick
from R137's spread rows, a tick on a stop exit and the slot's measured gap beyond the stop); the cost per winning day
(the cost over the target share) and the trading days to four winning days at one attempt a day (four over the target
share). **The rules:** a bracket qualifies on CHOICE (on time) when it resolves inside its box at least 90 % of the time
pooled and in every CHOICE year, its expected entry slippage (the spread beyond the tick plus the walk's tick, at its
micros) fits inside the operator's margin ($175 less the winning-day bar, read), and the one-minute-late entry's target
share is at most 0.03 below on time. At the reference stop (three times the target) each (slot, micros) takes its
shortest qualifying box; the lowest cost per winning day is chosen (ties within 2 % to the faster mean resolution, the
fewer micros, the earlier slot), every (slot, micros) within 10 % of it listed as an alternative, and the chosen (slot,
micros)'s menu is every stop multiple that qualifies, each in its shortest qualifying box. **Before any choice**, the
5-micro 1:1 bracket at 08:30 in the 10-minute box must read R138's second-resolution shares within 0.02 each.

Writes results/collect_map_nq.csv with its manifest; every on-time CHOICE (slot, micros, stop, box) is recorded in
results/variants.jsonl under D-381:collect_map.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

SCRIPT = "scripts/score_collect_map.py"
CONFIG = ROOT / "config" / "collect_map.yaml"
RUN = "R145-collect-NQ"
IDENTITY = {"decision_ct": "08:30", "contracts": 5, "stop_multiple": 1.0, "box_minutes": 10, "delay_min": 0}
IDENTITY_TOL = 0.02             # the config's identity: each share within 0.02 of R138's
TIE_TOL = 0.02                  # the config's choice: "ties within 2 %"


def bound(values) -> float:
    """The one-sided 95 % lower bound of the mean over yearly blocks: mean - t(0.95, n - 1) x SE; NaN below two."""
    from scipy import stats

    v = np.asarray([float(x) for x in values if np.isfinite(x)], float)
    if v.size < 2:
        return float("nan")
    return float(v.mean() - stats.t.ppf(0.95, v.size - 1) * v.std(ddof=1) / math.sqrt(v.size))


def years_of(span) -> list[int]:
    a, b = (int(str(x)[:4]) for x in span)
    return list(range(a, b + 1))


def spread_of(spreads: dict, label: str, years) -> float:
    """The entry minute's mean two-sided spread in ticks at the slot over `years` (quote-weighted), NaN without one."""
    w = [spreads[(label, y)] for y in years if (label, y) in spreads]
    return float(sum(m * n for m, n in w) / sum(n for _, n in w)) if w else float("nan")


def gap_of(gaps: dict, label: str, years, level: float) -> float:
    """Ticks beyond the stop per stop reached at `level` points at the slot over `years` (an open past the stop)."""
    w = [gaps[(label, y, level)] for y in years if (label, y, level) in gaps]
    n = sum(r for r, _ in w)
    return float(sum(t for _, t in w) / n) if n else 0.0


def stats(g: pd.DataFrame, *, contracts: int, target_points: float, stop_points: float, spread_ticks: float,
          gap_ticks: float, fee: float, mpv: float, tick: float) -> dict:
    """One bracket's numbers from its count rows (`g`, any years)."""
    N = int(g["n"].sum())
    t, s, x = (int(g[k].sum()) for k in ("target", "stop", "scratch"))
    mins, xs = int(g["minutes"].sum()), int(g["scratch_ticks"].sum())
    gross, risk = contracts * target_points * mpv, contracts * stop_points * mpv
    tick_d = tick * mpv * contracts                      # one tick at the bracket's micros
    sp = spread_ticks if np.isfinite(spread_ticks) else 1.0
    fees = fee * contracts
    if not N:
        return {"n": 0}
    cost = fees + max(0.0, sp - 1.0) * tick_d + (s / N) * (1.0 + gap_ticks) * tick_d
    net = (t * gross - s * risk + xs * tick_d) / N - cost
    ts = t / N
    return {"n": N, "target": t, "stop": s, "scratch": x, "target_share": ts, "stop_share": s / N, "scratch_share": x / N,
            "resolved": (t + s) / N, "mean_minutes": mins / (t + s) if (t + s) else float("nan"),
            "scratch_mean_dollars": (xs * tick_d / x) if x else 0.0, "gross_dollars": gross, "risk_dollars": risk,
            "rr": gross / risk, "win_after_fees": gross - fees, "spread_ticks_mean": spread_ticks,
            "gap_ticks_per_stop": gap_ticks, "slippage_dollars": max(sp, 1.0) * tick_d, "cost_dollars": cost,
            "cost_r": cost / risk, "net_mean": net, "e_net": net / risk,
            "cost_per_win": cost / ts if ts > 0 else float("inf"), "days_to_four": 4.0 / ts if ts > 0 else float("inf")}


# ------------------------------------------------------------------ D-384: a menu bracket's numbers over chosen years
MENU_KEYS = ("decision_ct", "decision_slot_minutes", "contracts", "target_points", "stop_multiple", "stop_points",
             "box_minutes")
Z95 = 1.6448536269514722            # the one-sided 95 % normal quantile


def menu_brackets(map_table: pd.DataFrame) -> list[dict]:
    """The collect map's menu (its `menu` rows): each bracket's slot, micros, target, stop and box, in stop order."""
    m = map_table[map_table["section"].astype(str) == "menu"].sort_values("stop_multiple")
    if not len(m):
        raise ValueError("the collect map holds no menu rows (D-383)")
    return [{k: (str(r[k]) if k == "decision_ct" else float(r[k])) for k in MENU_KEYS} for _, r in m.iterrows()]


def wilson_lower(p: float, n: float, z: float = Z95) -> float:
    """The one-sided Wilson score lower bound of a share `p` over `n` observations."""
    if not n > 0:
        return float("nan")
    d = 1.0 + z * z / n
    return float((p + z * z / (2 * n) - z * math.sqrt(max(p * (1 - p) / n + z * z / (4 * n * n), 0.0))) / d)


def bracket_stats(counts: pd.DataFrame, spread_rows: pd.DataFrame, years, bracket: dict, *, fee: float, mpv: float,
                  tick: float, delay: int = 0) -> dict:
    """D-384: one menu bracket's numbers over `years` from the capture's counts (`results/manual_R145_collect_NQ.csv`)
    -- the collect map's own arithmetic (`stats`, the slot's spreads from R137's rows over the same years, the measured
    gap at the stop's distance) -- and the lower-bound arm's reading: the target share's one-sided 95 % Wilson bound over
    the period's days (a day's long and short one observation, so half the pooled attempts), as a net edge with the
    shortfall moved from the target to the stop (`FlipSpec.shifted`'s form)."""
    yrs = [int(y) for y in years]
    c = counts[(counts["kind"] == "count") & counts["year"].isin(yrs) & (counts["delay_min"] == int(delay))]
    for k in MENU_KEYS:
        c = c[c[k].astype(str) == str(bracket[k])] if k == "decision_ct" else c[np.isclose(c[k].astype(float), float(bracket[k]))]
    if not len(c):
        raise ValueError(f"no counts for the bracket {bracket} in {yrs}")
    spreads = {(str(r.decision_ct), int(r.year)): (float(r.spread_ticks_mean), int(r.quotes))
               for r in spread_rows.itertuples() if int(r.quotes) > 0}
    gp = counts[(counts["kind"] == "gap") & counts["year"].isin(yrs)]
    gaps = {}
    if len(gp):
        for (lab, y, lv), g in gp.groupby(["decision_ct", "year", "level_points"]):
            gaps[(str(lab), int(y), float(lv))] = (int(g["stops_reached"].sum()), int(g["gap_ticks"].sum()))
    lab = str(bracket["decision_ct"])
    st = stats(c, contracts=int(bracket["contracts"]), target_points=float(bracket["target_points"]),
               stop_points=float(bracket["stop_points"]), spread_ticks=spread_of(spreads, lab, yrs),
               gap_ticks=gap_of(gaps, lab, yrs, float(bracket["stop_points"])), fee=fee, mpv=mpv, tick=tick)
    days = st["n"] / 2.0
    lb = wilson_lower(st["target_share"], days)
    st.update({"years": ",".join(str(y) for y in yrs), "days": days, "target_share_lb": lb,
               "e_net_lower_bound": st["e_net"] + (lb - st["target_share"]) * (1.0 + st["rr"])})
    return st


def score(table: pd.DataFrame, cfg: dict, q: dict, *, fee: float, bar: float, spread_rows: pd.DataFrame,
          identity_row: dict) -> pd.DataFrame:
    """Every section from the parser's table under the config's rules; `q` is `flip_kit.params_collect(cfg)`, `bar`
    the ledger's winning-day minimum, `identity_row` R138's chosen shares."""
    tick, mpv = float(q["tick"]), float(q["micro_point_value"])
    per = {"choice": years_of(cfg["periods"]["choice"]), "check": years_of(cfg["periods"]["check"]),
           "beside": years_of(cfg["periods"]["beside"])}
    qual = cfg["qualify"]
    floor, drop = float(qual["resolved_min"]), float(qual["late_entry_max_drop"])
    margin = float(q["net_min_dollars"]) - float(bar)
    ref = float(cfg["reference_multiple"])
    alt_tol = float(cfg["alternatives"])
    spreads = {(str(r.decision_ct), int(r.year)): (float(r.spread_ticks_mean), int(r.quotes))
               for r in spread_rows.itertuples() if int(r.quotes) > 0}
    gp = table[table["kind"] == "gap"]
    gaps = {}
    if len(gp):
        for (lab, y, lv), g in gp.groupby(["decision_ct", "year", "level_points"]):
            gaps[(str(lab), int(y), float(lv))] = (int(g["stops_reached"].sum()), int(g["gap_ticks"].sum()))
    c = table[table["kind"] == "count"]
    keys = ["decision_ct", "decision_slot_minutes", "contracts", "target_points", "stop_multiple", "stop_points",
            "box_minutes", "delay_min"]

    def numbers(g, key, years):
        lab, _, n, T, m, S, b, dl = key
        return stats(g, contracts=int(n), target_points=float(T), stop_points=float(S),
                     spread_ticks=spread_of(spreads, str(lab), years), gap_ticks=gap_of(gaps, str(lab), years, float(S)),
                     fee=fee, mpv=mpv, tick=tick)

    rows, by = [], {}
    for key, g in c.groupby(keys):
        for pname, years in per.items():
            gy = g[g["year"].isin(years)]
            if not len(gy):
                continue
            row = {"section": "cell", "period": pname, **dict(zip(keys, key)), **numbers(gy, key, years)}
            yearly = [numbers(gy[gy["year"] == y], key, [y]) for y in years if (gy["year"] == y).any()]
            row["years"] = len(yearly)
            row["worst_year_resolved"] = min(r["resolved"] for r in yearly)
            row["net_lb"] = bound([r["net_mean"] for r in yearly])
            row["e_net_lower_bound"] = row["net_lb"] / row["risk_dollars"] if np.isfinite(row["net_lb"]) else float("nan")
            rows.append(row)
            by[(pname, *key)] = row
    for row in rows:                                     # the late entry beside, and the CHOICE qualification
        if row["delay_min"] != 0:
            continue
        late = by.get((row["period"], row["decision_ct"], row["decision_slot_minutes"], row["contracts"],
                       row["target_points"], row["stop_multiple"], row["stop_points"], row["box_minutes"], 1))
        row["late_target_share_drop"] = (row["target_share"] - late["target_share"]) if late else float("nan")
        if row["period"] == "choice":
            row["qualifies"] = bool(row["resolved"] >= floor - 1e-12 and row["worst_year_resolved"] >= floor - 1e-12
                                    and row["slippage_dollars"] <= margin + 1e-9
                                    and np.isfinite(row["late_target_share_drop"])
                                    and row["late_target_share_drop"] <= drop + 1e-12)
    cells = pd.DataFrame(rows)
    out = [cells]

    # the identity: the 5-micro 1:1 bracket at 08:30 in the 10-minute box, on time, every year pooled, against R138
    idg = c[(c["decision_ct"] == IDENTITY["decision_ct"]) & (c["contracts"] == IDENTITY["contracts"])
            & (c["stop_multiple"] == IDENTITY["stop_multiple"]) & (c["box_minutes"] == IDENTITY["box_minutes"])
            & (c["delay_min"] == IDENTITY["delay_min"])]
    N = int(idg["n"].sum())
    ours = {k: (float(idg[k].sum()) / N if N else float("nan")) for k in ("target", "stop", "scratch")}
    diffs = {k: ours[k] - float(identity_row[f"{k}_share"]) for k in ours}
    ok = bool(N and all(abs(v) <= IDENTITY_TOL for v in diffs.values()))
    out.append(pd.DataFrame([{"section": "identity", **{f"{k}_share": ours[k] for k in ours},
                              **{f"r138_{k}_share": float(identity_row[f"{k}_share"]) for k in ours},
                              **{f"{k}_share_diff": diffs[k] for k in ours}, "n": N, "tolerance": IDENTITY_TOL,
                              "identity_holds": ok}]))
    verdict = {"section": "verdict", "identity_holds": ok, "reference_multiple": ref, "margin_dollars": margin,
               "resolved_min": floor, "late_entry_max_drop": drop}
    if not ok:
        verdict["note"] = "the walk does not reproduce R138: nothing is chosen (D-381)"
        out.append(pd.DataFrame([verdict]))
        return pd.concat(out, ignore_index=True)

    ch = cells[(cells["period"] == "choice") & (cells["delay_min"] == 0)]
    elig = []
    for (lab, slot, n), g in ch[ch["stop_multiple"] == ref].groupby(["decision_ct", "decision_slot_minutes", "contracts"]):
        g = g[g["qualifies"] == True].sort_values("box_minutes")      # noqa: E712
        if len(g):
            elig.append(g.iloc[0])
    verdict["eligible"] = len(elig)
    if not elig:
        verdict["note"] = "no (slot, micros) qualifies at the reference stop"
        out.append(pd.DataFrame([verdict]))
        return pd.concat(out, ignore_index=True)
    e = pd.DataFrame(elig)
    best = float(e["cost_per_win"].min())
    near = e[e["cost_per_win"] <= best * (1 + TIE_TOL) + 1e-12]
    pick = near.sort_values(["mean_minutes", "contracts", "decision_slot_minutes"]).iloc[0]
    e = e.assign(section="choice", role=["rule" if (r.decision_ct == pick.decision_ct and r.contracts == pick.contracts)
                                         else ("alternative" if r.cost_per_win <= float(pick.cost_per_win) * (1 + alt_tol) + 1e-12
                                               else "eligible") for r in e.itertuples()])
    out.append(e)
    menu = []
    sel = cells[(cells["decision_ct"] == pick.decision_ct) & (cells["contracts"] == pick.contracts) & (cells["delay_min"] == 0)]
    for m, g in sel[sel["period"] == "choice"].groupby("stop_multiple"):
        g = g[g["qualifies"] == True].sort_values("box_minutes")      # noqa: E712
        if not len(g):
            continue
        r = g.iloc[0].to_dict()
        k = sel[(sel["period"] == "check") & (sel["stop_multiple"] == m) & (sel["box_minutes"] == r["box_minutes"])]
        chk = k.iloc[0].to_dict() if len(k) else {}
        for f in ("n", "target_share", "stop_share", "scratch_share", "resolved", "mean_minutes", "cost_dollars",
                  "net_mean", "net_lb", "cost_per_win", "days_to_four", "e_net", "e_net_lower_bound"):
            r[f"check_{f}"] = chk.get(f, float("nan"))
        r["check_resolved_ok"] = bool(chk) and chk["resolved"] >= floor - 1e-12
        r["check_target_share_change"] = r["check_target_share"] - r["target_share"]
        r.update({"section": "menu", "role": "menu"})
        menu.append(r)
    out.append(pd.DataFrame(menu))
    verdict.update({"chosen_ct": pick.decision_ct, "chosen_slot_minutes": int(pick.decision_slot_minutes),
                    "chosen_contracts": int(pick.contracts), "chosen_target_points": float(pick.target_points),
                    "chosen_box_minutes": int(pick.box_minutes), "chosen_cost_per_win": float(pick.cost_per_win),
                    "alternatives": int((e["role"] == "alternative").sum()),
                    "menu_multiples": ",".join(f"{r['stop_multiple']:g}" for r in menu),
                    "menu_check_resolved_ok": all(r["check_resolved_ok"] for r in menu) if menu else False})
    out.append(pd.DataFrame([verdict]))
    return pd.concat(out, ignore_index=True)


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.contract.rules import load_rules
    from propedge.data import flip_kit as fk
    from propedge.reporting.results import read_result, write_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.parse_args(argv)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    if cfg.get("status") != "fixed":
        print("REFUSED: config/collect_map.yaml is not fixed.")
        return 2
    src = rd / f"manual_{RUN.replace('-', '_')}.csv"
    if not src.exists():
        print(f"REFUSED: {src.name} is not ingested; run the kit and scripts/ingest_flip_run.py first.")
        return 2
    q = fk.params_collect(cfg)
    bar = float(load_rules().value("xfa_std_winning_day_min"))
    spread_rows = read_result(rd / "manual_R137_flipmap_NQ.csv")
    spread_rows = spread_rows[spread_rows["kind"] == "spread"]
    r138 = read_result(rd / "flip_map_nq_seconds_micros.csv")
    r138 = r138[(r138["section"] == "choice") & (r138["role"] == "rule")]
    if len(r138) != 1:
        print("REFUSED: results/flip_map_nq_seconds_micros.csv holds no single chosen row for the identity.")
        return 2
    out = score(read_result(src), cfg, q, fee=float(q["fee_round_turn"]), bar=bar, spread_rows=spread_rows,
                identity_row=r138.iloc[0].to_dict())
    counter = VariantCounter(path=rd / "variants.jsonl")
    cells = out[(out["section"] == "cell") & (out["period"] == "choice") & (out["delay_min"] == 0)]
    for _, r in cells.iterrows():
        counter.record(prereg_id="D-381:collect_map", seed=0, exploratory=True,
                       params={"slot_ct": str(r["decision_ct"]), "contracts": int(r["contracts"]),
                               "stop_multiple": float(r["stop_multiple"]), "box_minutes": int(r["box_minutes"]),
                               "config": "config/collect_map.yaml", "run": RUN},
                       label=f"collect map: {r['decision_ct']} CT, {int(r['contracts'])} MNQ, stop {r['stop_multiple']:g}x, "
                             f"{int(r['box_minutes'])} minutes (D-381)")
    n_var = len({r["variant_id"] for r in counter.all() if r.get("prereg_id") == "D-381:collect_map"})
    write_result(out, "collect_map_nq", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 results_dir=results_dir, variant_count=n_var,
                 parameters={"config": "config/collect_map.yaml", "run": RUN, "fee_micro": float(q["fee_round_turn"]),
                             "winning_day_bar": bar, "spread_source": "results/manual_R137_flipmap_NQ.csv (spread rows)",
                             "identity_source": "results/flip_map_nq_seconds_micros.csv (section choice, role rule)",
                             "decision": "D-381"},
                 notes={"status": "EXPLORATORY: the XFA's winning-day bracket chosen by a declared rule on 2021-2023 and "
                                  "reported on 2024 to June 2025; its money is tested in the funded table against FV3-C by "
                                  "its own declaration"},
                 description="EXPLORATORY: the collect map -- $200-target brackets with stops one to eight times the "
                             "target at every hour of the trading day, in boxes to two hours, both sides pooled: shares, "
                             "resolution, cost, the cost per winning day and the days to four winning days; the identity "
                             "against R138; the chosen hour, micro count and box, the alternatives, the menu of stops.")
    v = out[out["section"] == "verdict"].iloc[0]
    if not bool(v["identity_holds"]):
        print("the identity does NOT hold: nothing is chosen (see the identity row)")
    elif isinstance(v.get("chosen_ct"), str):
        print(f"chosen: {v['chosen_ct']} CT, {int(v['chosen_contracts'])} MNQ ({v['chosen_target_points']:g}-point target), "
              f"{int(v['chosen_box_minutes'])}-minute box at the reference stop; alternatives {int(v['alternatives'])}; "
              f"menu stops {v['menu_multiples']}")
    else:
        print(f"nothing chosen: {v.get('note')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
