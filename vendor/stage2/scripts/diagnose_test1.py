"""Diagnose Test 1 (the exploratory open-reversion run, D-118): where did its result come from?

    python scripts/diagnose_test1.py

Read-only on the Test 1 evidence and results. Writes results/test1_diagnosis.csv (exploratory),
long format: section, variant, baseline, scale, statistic, mean, lo90, hi90, n. Sections:

  gate         the knob-free slope and its 90 % interval, as effect size in % (from openrev_gate.csv)
  decomp       per trade, in units of intended risk: price-only (zero cost), slippage, commission, net
  direction    real minus mirror, halved (the antisymmetric, directional component) and real plus
               mirror, halved (the symmetric component: fill rules plus move-size effects when R != 1),
               at ES 4000 and at actual prices; and the next-minute move after entry in real ticks
  fillrule     the symmetric component on a synthetic driftless walk, where direction is zero by
               construction: the pure cost of the cautious fill rules
  definitions  how the declared definitions behaved on the data (equal adjacent highs/lows, bar range,
               share of stops set by the cost floor)

Every number the audit (docs/audits/test1_open_reversion_diagnosis.md) quotes comes from this file.
Needs results/manual_R027_gap_ES2.csv, which D-120 removes from the working copy; rerunning this
script later needs the R027 kit rerun in QuantConnect (the sha256 in its manifest checks the copy).
"""
from __future__ import annotations

import math
import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from propedge.data.qc_algorithms import gap_slot_hhmm  # noqa: E402
from propedge.outcomes import open_reversion as orv  # noqa: E402
from propedge.reporting.results import read_result, write_result  # noqa: E402

SEED = 20260925
P_REF = 4000.0
Z90 = 1.6448536269514722


def _ci(x) -> tuple[float, float, float, int]:
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    if len(x) < 2:
        return float("nan"), float("nan"), float("nan"), len(x)
    se = x.std(ddof=1) / math.sqrt(len(x))
    return float(x.mean()), float(x.mean() - Z90 * se), float(x.mean() + Z90 * se), len(x)


def main() -> int:
    warnings.filterwarnings("ignore")
    cfg = orv.load_design()
    rows: list[dict] = []

    def add(section, statistic, stats, variant="", baseline="", scale=""):
        m, lo, hi, n = stats
        rows.append({"section": section, "variant": variant, "baseline": baseline, "scale": scale,
                     "statistic": statistic, "mean": m, "lo90": lo, "hi90": hi, "n": n})

    # ---- gate precision, from the committed Test 1 result
    gate = read_result(ROOT / "results" / "openrev_gate.csv")
    for scope in ("all|whole", "all|selection_half", "all|validation_half"):
        g = gate[gate["scope"] == scope].iloc[0]
        add("gate", f"beta_45|{scope}", (g.beta_45, g.beta_45_lb05, g.beta_45_ub95, int(g.n_days)))
        add("gate", f"effect_pct|{scope}", (-g.beta_45 * g.sd_x, -g.beta_45_ub95 * g.sd_x,
                                            -g.beta_45_lb05 * g.sd_x, int(g.n_days)))
    add("gate", "declared_bar_pct", (cfg["gate"]["pass"]["effect_size_pct_at_least"],) * 3 + (0,))

    # ---- the evidence
    p = orv.panel_from_bars(read_result(ROOT / "results" / "manual_R027_gap_ES2.csv"))
    st = orv.day_status(p)
    days = np.flatnonzero(st["reason"].to_numpy() == "")
    full = orv.fills_from_config()
    comm_only = orv.Fills(0, 0, 0, 0, full.round_turn, full.tick_value, full.point_value)

    for v in orv.variants(cfg):
        for base in (True, False):
            kind = "baseline" if base else "structural"
            for scale_name, scale in (("P_ref_4000", P_REF), ("actual", None)):
                z = orv.score_variant(p, st, days, v, cfg, orv.ZERO_COST_MES, scale_to=scale, baseline=base)
                zf = orv.score_variant(p, st, days, v, cfg, orv.ZERO_COST_MES, scale_to=scale, baseline=base,
                                       flip=True)
                f = orv.score_variant(p, st, days, v, cfg, full, scale_to=scale, baseline=base)
                m = z["u"].notna() & f["u"].notna()
                comm = full.round_turn / f.loc[m, "risk"]
                price = z.loc[m, "u"]
                add("decomp", "price_only_u", _ci(price), v["key"], kind, scale_name)
                add("decomp", "slippage_u", _ci(price - (f.loc[m, "u"] + comm)), v["key"], kind, scale_name)
                add("decomp", "commission_u", _ci(comm), v["key"], kind, scale_name)
                add("decomp", "net_u", _ci(f.loc[m, "u"]), v["key"], kind, scale_name)
                add("decomp", "floor_bound_share", _ci(f.loc[m, "floor_bound"].astype(float)), v["key"], kind,
                    scale_name)
                mm = z["u"].notna() & zf["u"].notna()
                ra, rb = z.loc[mm, "u"].to_numpy(), zf.loc[mm, "u"].to_numpy()
                add("direction", "directional_d", _ci((ra - rb) / 2), v["key"], kind, scale_name)
                add("direction", "symmetric_s", _ci((ra + rb) / 2), v["key"], kind, scale_name)
                nxt = []
                for r in z.loc[mm].itertuples():
                    i = int(np.flatnonzero(p.n == r.n)[0])
                    t = int(r.t)
                    if t + 1 < orv.SLOTS and not np.isnan(p.c[i, t + 1]):
                        nxt.append(r.direction * (p.c[i, t + 1] - p.c[i, t]) / orv.TICK)
                add("direction", "next_minute_move_real_ticks", _ci(nxt), v["key"], kind, scale_name)
        print(f"  {v['key']} done")

    # ---- fill-rule cost on a synthetic driftless walk
    rng = np.random.default_rng(SEED)
    n = 1500
    dates = pd.bdate_range("2010-01-04", periods=n)
    syn = []
    for i, dt in enumerate(dates):
        px = P_REF
        for j in range(orv.SLOTS):
            o = px
            c = o + orv.TICK * np.round(rng.normal(0, 2.4))
            syn.append((i + 1, dt.strftime("%Y%m%d"), "ES", P_REF, dates[i - 1].strftime("%Y%m%d") if i else "",
                        "" if i else "noprev", P_REF, orv.SLOTS, "1030", gap_slot_hhmm(j), o,
                        max(o, c) + orv.TICK * rng.integers(0, 6), min(o, c) - orv.TICK * rng.integers(0, 6), c))
            px = c
    q = orv.panel_from_bars(pd.DataFrame(syn, columns=["n", "d", "sym", "ps", "pst", "sk", "base", "nb", "lt",
                                                       "t", "o", "h", "l", "c"]))
    sq = orv.day_status(q)
    qd = np.flatnonzero(sq["reason"].to_numpy() == "")
    for key in ("trigger_bar|r1.0", "swing_extreme|r1.0"):
        v = next(z for z in orv.variants(cfg) if z["key"] == key)
        a = orv.score_variant(q, sq, qd, v, cfg, orv.ZERO_COST_MES, baseline=True)
        b = orv.score_variant(q, sq, qd, v, cfg, orv.ZERO_COST_MES, baseline=True, flip=True)
        mm = a["u"].notna() & b["u"].notna()
        ra, rb = a.loc[mm, "u"].to_numpy(), b.loc[mm, "u"].to_numpy()
        add("fillrule", "symmetric_s_driftless", _ci((ra + rb) / 2), key, "baseline", "synthetic_4000")
        add("fillrule", "directional_d_driftless", _ci((ra - rb) / 2), key, "baseline", "synthetic_4000")

    # ---- how the definitions behaved
    s0, s1 = orv.slot_of("0831"), orv.slot_of("0930")
    h, l = p.h[days][:, s0:s1 + 1], p.l[days][:, s0:s1 + 1]
    add("definitions", "equal_adjacent_highs_share", (float(np.mean(h[:, 1:] == h[:, :-1])),) * 3 + (h.size,))
    add("definitions", "equal_adjacent_lows_share", (float(np.mean(l[:, 1:] == l[:, :-1])),) * 3 + (l.size,))
    rng_ticks = (h - l) / orv.TICK
    add("definitions", "median_bar_range_real_ticks", (float(np.nanmedian(rng_ticks)),) * 3 + (rng_ticks.size,))
    add("definitions", "p_ref_over_price_median", (float(np.median(P_REF / p.ps[days])),) * 3 + (len(days),))
    add("definitions", "scoreable_days_with_missing_minutes", (float((p.nb[days] < orv.SLOTS).sum()),) * 3 + (len(days),))

    out = pd.DataFrame(rows)
    write_result(out, "test1_diagnosis", script="scripts/diagnose_test1.py", seed=SEED, exploratory=True,
                 parameters={"design": "config/open_reversion.yaml", "evidence": "results/manual_R027_gap_ES2.csv",
                             "test1_results": "results/openrev_*.csv", "p_ref": P_REF, "z90": Z90,
                             "synthetic_days": n, "synthetic_minute_sd_ticks": 2.4},
                 notes={"status": "EXPLORATORY diagnosis of Test 1 (D-118, D-121); read-only on the evidence",
                        "interpretation": "docs/audits/test1_open_reversion_diagnosis.md"},
                 description="Test 1 diagnosis: gate precision, per-trade decomposition into price, slippage "
                             "and commission, directional vs symmetric components, fill-rule cost on a "
                             "driftless walk, and how the declared definitions behaved.")
    print(out[out["section"].isin(["gate", "fillrule", "definitions"])].round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
