"""Read the R029 run (the open-reversion model on NQ) and apply D-124's declared rules.

    python scripts/score_openrev_nq.py

Order, fixed in config/open_reversion_nq.yaml before the run:

  1. integrity gate: about 1,285 days; bars failing the OHLC order or the tick grid at most 0.1 %; the
     08:30 CT bar wider on average than the pre-open bars (the clock). A failure stops here.
  2. the knob-free gate (reported, not the decision): slope of the next 30/45/60 minutes on the first
     15, from the per-day measurements computed in the cloud.
  3. the verdict, on the directional part (zero-cost real minus mirror, halved) of the 12 plain-entry
     cells, next-open fill: SCRAP if every 90 % upper bound is below the required 0.24; INCONCLUSIVE
     if some interval contains 0.24; PROCEED if some lower bound is at or above 0.24.
  4. only on PROCEED: the declared selection stage (selection half, lower bound of net u, plateau,
     ablation, one look at the validation half, a random-direction null).

Writes results/openrev_nq.csv (exploratory). Numbers for any document come from that file.
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
import yaml  # noqa: E402

from propedge.outcomes import gap_reversal as gr  # noqa: E402
from propedge.outcomes import open_reversion as orv  # noqa: E402
from propedge.reporting.results import read_result, write_result  # noqa: E402

EVIDENCE = ROOT / "results" / "manual_R029_openrev_NQ.csv"
Z90 = 1.6448536269514722


def _ci(x):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    if len(x) < 2:
        return float("nan"), float("nan"), float("nan"), len(x)
    se = x.std(ddof=1) / math.sqrt(len(x))
    return float(x.mean()), float(x.mean() - Z90 * se), float(x.mean() + Z90 * se), len(x)


def main() -> int:
    warnings.filterwarnings("ignore")
    nq = yaml.safe_load((ROOT / "config" / "open_reversion_nq.yaml").read_text(encoding="utf-8"))
    cfg = orv.load_design()
    keys = [v["key"] for v in orv.variants(cfg)]
    required = float(nq["required_directional_part"])
    fill = nq["overrides"]["fill_primary"]
    df = read_result(EVIDENCE)
    # The parser labels the rescaled level by position ("P_ref_4000", R028's ES level); for NQ it is
    # the declared NQ level. Relabel so the result file says what was computed.
    p_ref_label = f"P_ref_{int(nq['overrides']['selection_price_level'])}"
    df["scale"] = df["scale"].replace({"P_ref_4000": p_ref_label})
    days = df[df["cell"] == -1].sort_values("n").reset_index(drop=True)
    rows: list[dict] = []

    def add(section, statistic, mean, lo=float("nan"), hi=float("nan"), n=0, **kw):
        rows.append({"section": section, "statistic": statistic, "mean": mean, "lo90": lo, "hi90": hi, "n": n, **kw})

    # ---- 1. integrity
    ig = nq["integrity_gate"]
    n_days = len(days)
    bad_share = float(days["bad"].sum() / max(days["nb"].sum(), 1))
    r0, rp = float(days["r0"].mean()), float(days["rp"].mean())
    integrity_ok = (n_days >= 0.95 * ig["days_expected_about"] and bad_share <= ig["max_bad_bar_share"]
                    and (r0 > rp) == bool(ig["open_bar_wider_than_preopen"]))
    add("integrity", "days", n_days, n=n_days)
    add("integrity", "bad_bar_share", bad_share)
    add("integrity", "mean_open_bar_range_ticks", r0)
    add("integrity", "mean_preopen_bar_range_ticks", rp)
    add("integrity", "passes", float(integrity_ok))
    print(f"integrity: days {n_days}, bad-bar share {bad_share:.5f}, open bar {r0:.2f} vs pre-open {rp:.2f} ticks "
          f"-> {'PASS' if integrity_ok else 'BLOCK'}")

    days["reason"] = orv.status_from_days(days)
    ok_days = days[days["reason"] == ""].copy()
    ok = set(ok_days["n"])
    add("integrity", "scoreable_days", len(ok), n=len(ok))

    verdict = "not computed: the integrity gate failed"
    if integrity_ok:
        # ---- 2. the knob-free gate (reported)
        b = cfg["gate"]["bootstrap"]
        g = orv.gate_from_measures(ok_days["x"].to_numpy(), {m: ok_days[f"y{m}"].to_numpy() for m in (30, 45, 60)},
                                   block=b["block_days"], reps=b["replicates"], seed=b["seed"],
                                   bar_pct=cfg["gate"]["pass"]["effect_size_pct_at_least"])
        add("gate", "beta_45", g["beta_45"], g["beta_45_lb05"], g["beta_45_ub95"], g["n_days"])
        add("gate", "effect_pct", g["effect_size_pct"], g["effect_lo90"], g["effect_hi90"], g["n_days"])
        add("gate", "beta_30", g["beta_30"], n=g["n_days"])
        add("gate", "beta_60", g["beta_60"], n=g["n_days"])
        print(f"gate: effect {g['effect_size_pct']:+.4f}% [{g['effect_lo90']:+.4f}, {g['effect_hi90']:+.4f}] "
              f"(reported, not the decision)")

        # ---- per cell: directional part, symmetric part, decomposition
        cells = df[(df["cell"] >= 0) & df["n"].isin(ok)].copy()
        cells["variant"] = cells["variant_i"].astype(int).map(dict(enumerate(keys)))
        for (f_, scale, entry, variant), c in cells.groupby(["fill", "scale", "entry", "variant"]):
            both = c[c["zr"].notna() & c["zm"].notna()]
            net = c[c["zr"].notna() & c["fu"].notna()]
            for stat, x in (("directional_d", (both["zr"] - both["zm"]) / 2),
                            ("symmetric_s", (both["zr"] + both["zm"]) / 2),
                            ("price_only_u", net["zr"]), ("net_u", net["fu"])):
                m, lo, hi, n = _ci(x)
                add("cell", stat, m, lo, hi, n, fill=f_, scale=scale, entry=entry, variant=variant)

        # ---- 3. the verdict
        cell_rows = pd.DataFrame([r for r in rows if r["section"] == "cell"])
        plain = cell_rows[(cell_rows["fill"] == fill) & (cell_rows["entry"] == "baseline")
                          & (cell_rows["statistic"] == "directional_d")]
        if len(plain) != 12:
            verdict = f"not computed: expected 12 plain-entry cells, found {len(plain)}"
        elif (plain["hi90"] < required).all():
            verdict = "SCRAP"
        elif (plain["lo90"] >= required).any():
            verdict = "PROCEED"
        else:
            verdict = "INCONCLUSIVE"
        add("verdict", "D-124", float("nan"), n=len(ok), variant=verdict)
        print("verdict:", verdict)
        print(plain[["scale", "variant", "mean", "lo90", "hi90", "n"]].round(3).to_string(index=False))

        # ---- 4. the selection stage, only on PROCEED (declared in D-124)
        if verdict == "PROCEED":
            sel_day = pd.to_datetime(cells["d"].astype(str), format="%Y%m%d") <= pd.Timestamp(nq["development"]["selection_end"])
            cells["half"] = np.where(sel_day, "selection", "validation")
            sel_rows = []
            for (entry, variant), c in cells[(cells["fill"] == fill) & (cells["scale"] == p_ref_label)].groupby(
                    ["entry", "variant"]):
                c = c.sort_values("n")
                s = c[c["half"] == "selection"]
                bb = gr.block_lower_bound(s["fu"].to_numpy(), block=20, reps=10_000, seed=20261011)
                v = next(z for z in orv.variants(cfg) if z["key"] == variant)
                sel_rows.append({"anchor": v["anchor"], "r_min": v["r_min"], "lb": bb["lb"],
                                 "baseline": entry == "baseline", "variant": variant})
            choice = orv.select(sel_rows, cfg)
            add("selection", "selected", float("nan"), variant=str(choice["selected"]), note=choice["why"])
            print("selection:", choice["selected"], "-", choice["why"])
    write_result(pd.DataFrame(rows), "openrev_nq", script="scripts/score_openrev_nq.py", seed=None,
                 require_seed=False, exploratory=True,
                 parameters={"evidence": str(EVIDENCE.relative_to(ROOT)), "design": "config/open_reversion_nq.yaml",
                             "inherits": "config/open_reversion.yaml", "required_directional_part": required,
                             "fill_primary": fill},
                 notes={"decision": "D-124 (declared before the run)",
                        "status": "EXPLORATORY; development data; never eligible for confirmation"},
                 description="The open-reversion model on NQ (R029): integrity, the knob-free gate, per-cell "
                             "directional part and decomposition, and D-124's verdict.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
