"""EXPLORATORY (D-343): score the flip map's counts -- at which hour start, and at which width in points, does a fast
1:1 bracket in one NQ mini resolve to target or stop inside a ten-minute box often enough to carry a flip day, and what
does it cost?

    python scripts/score_flip_map.py

Reads the ingested kit (`results/manual_R137_flipmap_NQ.csv`, `propedge/data/flip_parser.py`'s table) and applies what
`config/flip_map.yaml` fixed before any count was read:

* **Per slot, width, entry delay and year** (full sessions; early closes counted apart and reported): the shares at the
  target, at the stop and scratched; the share resolved inside the box and the share resolved within five minutes; the
  mean minutes to resolution; the scratches' mean P&L in ticks and in dollars for one mini; the entry minute's mean
  spread; the cost per attempt in units of the risk (`rules.cost`); the net edge per attempt (`rules.edge`) and, on the
  pooled row, its one-sided 95 % lower bound over the yearly blocks.
* **A width qualifies at a slot** when its share resolved inside the box is at least `rules.resolved_in_box_min` pooled
  and in every year, on the on-time entry; the slot's chosen width is the widest that qualifies (`rules.width_choice`).
* **The slot choice** (`rules.slot_choice`): the slot whose chosen width resolves inside the box most often, ties to the
  earlier slot; the 08:30 and 09:00 CT slots reported beside whatever the rule picks.

Writes results/flip_map_nq.csv, sections `cell` (slot, width, delay, year or pooled), `slot` (each slot's chosen width,
or none), `choice` and `summary`. Nothing here is a verdict: the chosen bracket's statistics feed the two-stream
candidate's table and engine under their own declaration.

`--seconds` (D-344) scores the second-resolution kit with the minute kit's spreads and the corrected slot rule (the
cheapest qualifying flip). `--sizing config/flip_sizing.yaml` (D-346) prices every width at the traded contract's count
under the rule fixed there -- the fewest micros whose risk sits on the table's grid and whose win after fees clears the
winning-day bar -- so the chosen flip is the width rule's width in the fewest contracts that make a winning day; the
default result name then carries `_micros`, so the one-mini reading stays on record beside it.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/score_flip_map.py"
BESIDE_CT = ("08:30", "09:00")


def bound(values) -> float:
    """The one-sided 95 % lower bound of the mean over yearly blocks: mean - t(0.95, n - 1) x SE; NaN below two."""
    from scipy import stats

    v = np.asarray([float(x) for x in values if np.isfinite(x)], float)
    if v.size < 2:
        return float("nan")
    return float(v.mean() - stats.t.ppf(0.95, v.size - 1) * v.std(ddof=1) / math.sqrt(v.size))


def _cell(g: pd.DataFrame, spread_ticks: float, fee: float, tick_dollars: float, point_value: float, width: float) -> dict:
    n, t, s, x = (int(g[k].sum()) for k in ("n", "target", "stop", "scratch"))
    mins = int(g["minutes"].sum())
    t5, s5 = int(g["target_within_5"].sum()), int(g["stop_within_5"].sum())
    xs, xa = int(g["scratch_ticks"].sum()), int(g["scratch_abs_ticks"].sum())
    risk = width * point_value
    resolved = (t + s) / n if n else float("nan")
    scratch_mean_ticks = xs / x if x else 0.0
    # the cost: the round turn, the entry's measured spread beyond the tick the walk charged, one tick on a stop exit
    extra_spread = max(0.0, (spread_ticks if np.isfinite(spread_ticks) else 1.0) - 1.0) * tick_dollars
    cost = fee + extra_spread + (s / n if n else 0.0) * tick_dollars
    edge = ((t - s) / n + (xs * tick_dollars / n) / risk - cost / risk) if n else float("nan")
    return {"n": n, "target": t, "stop": s, "scratch": x, "target_share": t / n if n else float("nan"),
            "stop_share": s / n if n else float("nan"), "scratch_share": x / n if n else float("nan"),
            "resolved_in_box": resolved, "resolved_within_5": (t5 + s5) / n if n else float("nan"),
            "mean_minutes": mins / (t + s) if (t + s) else float("nan"),
            "scratch_mean_ticks": scratch_mean_ticks, "scratch_mean_dollars": scratch_mean_ticks * tick_dollars,
            "scratch_mean_abs_ticks": xa / x if x else 0.0, "spread_ticks_mean": spread_ticks,
            "risk_dollars": risk, "cost_dollars": cost, "cost_r": cost / risk, "e_net": edge}


def contracts_for(width: float, sizing: dict) -> int:
    """D-346: the fewest whole contracts whose risk at `width` points is a multiple of the table's grid and whose win
    after the round-turn fees clears the winning-day bar. `sizing`: point_value, fee_per_contract, grid_dollars,
    bar_dollars (the last read from the ledger by `main`)."""
    pv, fee = float(sizing["point_value"]), float(sizing["fee_per_contract"])
    grid, bar = float(sizing["grid_dollars"]), float(sizing["bar_dollars"])
    for n in range(1, 1001):
        risk = n * float(width) * pv
        if abs(risk / grid - round(risk / grid)) < 1e-9 and risk - n * fee >= bar - 1e-9:
            return n
    raise ValueError(f"no contract count puts {width:g} points on the ${grid:g} grid above the ${bar:g} bar after fees")


def score(table: pd.DataFrame, cfg: dict, fee: float, *, units_per_minute: int = 1, spread_table: pd.DataFrame | None = None,
          slot_rule: str = "resolves_most", sizing: dict | None = None) -> pd.DataFrame:
    """The sections from the parser's table under the config's rules. `units_per_minute` is the kit's bar in a minute
    (1 for the minute kit, 60 for the second-resolution kit, D-344); `spread_table` supplies the entry minute's spread
    rows when the kit carries none (the seconds kit reads the minute kit's, matched by the slot's clock label);
    `slot_rule` is D-343's `resolves_most` or D-344's `cheapest` (the slot whose chosen width has the best net edge).
    `sizing` (D-346): the traded contract's rule (`contracts_for`) -- each width priced at its own count of that
    contract (point value and fee per contract times the count); None prices one of the config's contract at `fee`."""
    if slot_rule not in ("resolves_most", "cheapest"):
        raise ValueError("slot_rule is 'resolves_most' or 'cheapest'")
    from propedge.campaign.flip import slot_from_ct

    k = cfg["contract"]
    tick = float(k["tick"])
    tick_dollars = tick * float(k["point_value"])

    def contract_of(width: float) -> tuple[int, float, float, str]:
        """(contracts, dollars a point, round-turn fee, instrument) for a bracket of `width` points."""
        if sizing is None:
            return 1, float(k["point_value"]), float(fee), str(k["ticker"])
        n = contracts_for(width, sizing)
        return n, n * float(sizing["point_value"]), n * float(sizing["fee_per_contract"]), str(sizing["instrument"])

    rule = cfg["rules"]
    floor = float(rule["resolved_in_box_min"])
    c = table[(table["kind"] == "count")]
    sp = (spread_table if spread_table is not None else table)
    sp = sp[sp["kind"] == "spread"]
    rows = []
    spread_by_label_year = {(str(r.decision_ct), int(r.year)): (float(r.spread_ticks_mean), int(r.quotes))
                            for r in sp.itertuples() if int(r.quotes) > 0}

    def spread(label: str, years) -> float:
        w = [(spread_by_label_year[(label, y)]) for y in years if (label, y) in spread_by_label_year]
        return float(sum(m * q for m, q in w) / sum(q for _, q in w)) if w else float("nan")

    # D-345 (7): `decision_slot` is the KIT's unit (the minute kit's: the engine's clock, minutes since 17:00 CT; the
    # seconds kit's: a second offset from its window's start). Every row also carries the slot on the ENGINE's clock,
    # from its clock label, which is what the engine and the Studio read; on the minute kit the two must agree.
    def engine_slot(slot: int, label: str) -> int:
        m = slot_from_ct(label)
        if units_per_minute == 1 and m != slot:
            raise ValueError(f"the minute kit's decision_slot {slot} is not its label {label} CT on the engine's clock ({m})")
        return m

    pooled: dict[tuple, dict] = {}
    for (slot, width, delay), g in c[c["day_type"] == "full"].groupby(["decision_slot", "width_points", "delay_min"]):
        slot, width, delay = int(slot), float(width), int(delay)
        label = str(g["decision_ct"].iloc[0])
        slot_min = engine_slot(slot, label)
        n_ct, pv, fee_w, inst = contract_of(width)                # D-346: the contract count and its dollars at this width
        td = tick * pv
        years = sorted(int(y) for y in g["year"].unique())
        per_year = []
        for y in years:
            gy = g[g["year"] == y]
            cy = _cell(gy, spread(label, [y]), fee_w, td, pv, width)
            cy["mean_minutes"] = cy["mean_minutes"] / units_per_minute
            cy.update({"contracts": n_ct, "instrument": inst})
            rows.append({"section": "cell", "decision_slot": slot, "decision_slot_minutes": slot_min, "decision_ct": label,
                         "width_points": width, "delay_min": delay, "year": y, **cy})
            per_year.append(cy)
        cp = _cell(g, spread(label, years), fee_w, td, pv, width)
        cp["mean_minutes"] = cp["mean_minutes"] / units_per_minute
        cp.update({"contracts": n_ct, "instrument": inst})
        worst = min(per_year, key=lambda d: d["resolved_in_box"]) if per_year else None
        cp.update({"years": len(years), "worst_year": years[int(np.argmin([d["resolved_in_box"] for d in per_year]))] if per_year else None,
                   "worst_year_resolved_in_box": worst["resolved_in_box"] if worst else float("nan"),
                   "e_net_lower_bound": bound([d["e_net"] for d in per_year]),
                   "qualifies": bool(np.isfinite(cp["resolved_in_box"]) and cp["resolved_in_box"] >= floor
                                     and all(d["resolved_in_box"] >= floor for d in per_year)),
                   "early_n": int(c[(c["day_type"] == "early") & (c["decision_slot"] == slot) & (c["width_points"] == width)
                                    & (c["delay_min"] == delay)]["n"].sum())})
        rows.append({"section": "cell", "decision_slot": slot, "decision_slot_minutes": slot_min, "decision_ct": label,
                     "width_points": width, "delay_min": delay, "year": "pooled", **cp})
        pooled[(slot, width, delay)] = cp
    # each slot's chosen width: the widest qualifying one on the on-time entry; its late-entry reading beside (the late
    # entry is the kit's other delay: one minute on the minute kit, sixty seconds on the seconds kit)
    delays = sorted(int(x) for x in c["delay_min"].unique())
    late_delay = delays[1] if len(delays) > 1 else None
    slot_rows = []
    for slot in sorted({s for s, _, _ in pooled}):
        quals = [w for (s, w, d), cp in pooled.items() if s == slot and d == 0 and cp["qualifies"]]
        ct = str(c[c["decision_slot"] == slot]["decision_ct"].iloc[0])
        slot_min = engine_slot(slot, ct)
        if not quals:
            slot_rows.append({"section": "slot", "decision_slot": slot, "decision_slot_minutes": slot_min, "decision_ct": ct,
                              "chosen_width_points": None, "qualifying_widths": ""})
            continue
        w = max(quals) if str(rule["width_choice"]) == "widest" else min(quals)
        on, late = pooled[(slot, w, 0)], (pooled.get((slot, w, late_delay)) if late_delay is not None else None)
        slot_rows.append({"section": "slot", "decision_slot": slot, "decision_slot_minutes": slot_min, "decision_ct": ct, "chosen_width_points": w,
                          "qualifying_widths": ",".join(f"{x:g}" for x in sorted(quals)),
                          "resolved_in_box": on["resolved_in_box"], "resolved_within_5": on["resolved_within_5"],
                          "mean_minutes": on["mean_minutes"], "e_net": on["e_net"], "e_net_lower_bound": on["e_net_lower_bound"],
                          "cost_r": on["cost_r"], "cost_dollars": on["cost_dollars"], "risk_dollars": on["risk_dollars"],
                          "n": on["n"], "target_share": on["target_share"], "stop_share": on["stop_share"],
                          "scratch_share": on["scratch_share"], "scratch_mean_dollars": on["scratch_mean_dollars"],
                          "spread_ticks_mean": on["spread_ticks_mean"], "years": on["years"],
                          "contracts": on["contracts"], "instrument": on["instrument"],
                          "worst_year_resolved_in_box": on["worst_year_resolved_in_box"],
                          "late_resolved_in_box": late["resolved_in_box"] if late else float("nan"),
                          "late_e_net": late["e_net"] if late else float("nan"),
                          "late_minus_on_time_e_net": (late["e_net"] - on["e_net"]) if late else float("nan")})
    rows += slot_rows
    chosen = [r for r in slot_rows if r.get("chosen_width_points") is not None]
    order = ((lambda r: (-r["resolved_in_box"], r["decision_slot"])) if slot_rule == "resolves_most"
             else (lambda r: (-r["e_net"], r["decision_slot"])))             # D-344: the cheapest qualifying flip
    if chosen:
        best = sorted(chosen, key=order)[0]
        rows.append({"section": "choice", "role": "rule", **{k_: v for k_, v in best.items() if k_ != "section"},
                     "rule": str(rule["slot_choice"]), "slot_rule": slot_rule})
        for ct in BESIDE_CT:
            r = next((x for x in slot_rows if x["decision_ct"] == ct), None)
            if r is not None:
                rows.append({"section": "choice", "role": f"beside {ct}", **{k_: v for k_, v in r.items() if k_ != "section"}})
    rows.append({"section": "summary", "slots": len(slot_rows), "slots_with_a_qualifying_width": len(chosen),
                 "resolved_in_box_min": floor, "width_choice": str(rule["width_choice"]), "slot_rule": slot_rule,
                 "units_per_minute": units_per_minute, "fee_round_turn": fee, "tick_dollars": tick_dollars,
                 "chosen_slot_ct": chosen and sorted(chosen, key=order)[0]["decision_ct"] or None,
                 **({} if sizing is None else {"sizing_instrument": str(sizing["instrument"]), "sizing_point_value": float(sizing["point_value"]),
                                               "sizing_fee_per_contract": float(sizing["fee_per_contract"]),
                                               "sizing_grid_dollars": float(sizing["grid_dollars"]), "sizing_bar_dollars": float(sizing["bar_dollars"])})})
    return pd.DataFrame(rows)


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.data import flip_kit as fk
    from propedge.execution.fills import FillModel
    from propedge.reporting.results import read_result, write_result

    import hashlib

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--result-name", default=None)
    ap.add_argument("--seconds", action="store_true", help="D-344: the second-resolution kit (R138), the minute kit's spreads")
    ap.add_argument("--sizing", default=None, help="D-346: the traded contract's rule (config/flip_sizing.yaml): each width "
                                                  "priced at the fewest micros on the table's grid above the winning-day bar")
    a = ap.parse_args(argv)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    sizing, sizing_note = None, {}
    if a.sizing:
        import yaml

        from propedge.contract.rules import load_rules

        sz_path = ROOT / a.sizing
        sz = yaml.safe_load(sz_path.read_text(encoding="utf-8"))
        fm = FillModel.load("assumed")
        sizing = {"instrument": str(sz["instrument"]), "point_value": float(sz["point_value"]),
                  "fee_per_contract": float(fm.round_turn_by_instrument[str(sz["instrument"])]),
                  "grid_dollars": float(sz["grid_dollars"]), "bar_dollars": float(load_rules().value(str(sz["bar"]))),
                  "bar_rule": str(sz["bar"]), "rule": str(sz["rule"]), "decision": str(sz.get("decision", ""))}
        sizing_note = {"sizing": sizing, "sizing_config": str(a.sizing), "sizing_sha256": hashlib.sha256(sz_path.read_bytes()).hexdigest()}
    if a.seconds:
        cfg = fk.config_seconds()
        run, name = fk.FLIP_SECONDS_RUN, a.result_name or ("flip_map_nq_seconds_micros" if sizing else "flip_map_nq_seconds")
    else:
        cfg = fk.config()
        run, name = fk.FLIP_RUN, a.result_name or ("flip_map_nq_micros" if sizing else "flip_map_nq")
    src = rd / f"manual_{run.replace('-', '_')}.csv"
    if not src.exists():
        print(f"REFUSED: {src.name} is not ingested; run the kit and scripts/ingest_flip_run.py first.")
        return 2
    table = read_result(src)
    fee = float(FillModel.load("assumed").round_turn_by_instrument[cfg["contract"]["ticker"]])
    spread_table, spread_note = None, {}
    if a.seconds:
        sfile = rd / Path(cfg["spread_source"]["file"]).name
        spread_table = read_result(sfile)
        spread_note = {"spread_source": str(cfg["spread_source"]["file"]),
                       "spread_source_sha256": hashlib.sha256(sfile.read_bytes()).hexdigest()}
    out = score(table, cfg, fee, units_per_minute=60 if a.seconds else 1, spread_table=spread_table,
                slot_rule="cheapest" if a.seconds else "resolves_most", sizing=sizing)
    write_result(out, name, script=SCRIPT, seed=None, require_seed=False, exploratory=True, results_dir=results_dir,
                 parameters={"config": "config/flip_map_seconds.yaml" if a.seconds else "config/flip_map.yaml", "run": run,
                             "rules": cfg["rules"], "widths_points": cfg["widths_points"],
                             "box": cfg.get("box_seconds", cfg.get("box_minutes")), "within": cfg.get("within_seconds", cfg.get("within_minutes")),
                             "entry_delays": cfg.get("entry_delays_seconds", cfg.get("entry_delays_min")),
                             "time_unit": "second" if a.seconds else "minute", "slot_rule": "cheapest" if a.seconds else "resolves_most",
                             "fee_round_turn": fee, "decision": ("D-346" if sizing else ("D-344" if a.seconds else "D-343")),
                             "scale": "actual prices", **spread_note, **sizing_note},
                 notes={"status": "EXPLORATORY: a map, not a verdict; the chosen bracket's statistics feed the two-stream "
                                  "candidate under its own declaration (D-343, D-344)"},
                 description=("EXPLORATORY: the flip map at second resolution -- a fast 1:1 bracket in one NQ mini at the two open "
                              "slots, resolved inside a ten-minute box or scratched, on one-second bars; shares, minutes, cost and "
                              "net edge per slot and width; the slot and width the declared rules choose (the cheapest qualifying "
                              "flip, D-344)." if a.seconds else
                              "EXPLORATORY: the flip map -- a fast 1:1 bracket in one NQ mini at every hour start, resolved "
                              "inside a ten-minute box or scratched; shares, minutes, cost and net edge per slot and width; "
                              "the slot and width the declared rules choose."))
    ch = out[(out["section"] == "choice") & (out["role"] == "rule")]
    if len(ch):
        r = ch.iloc[0]
        print(f"chosen: {r['decision_ct']} CT, width {r['chosen_width_points']:g} points, {int(r['contracts'])} x {r['instrument']} "
              f"(${r['risk_dollars']:,.0f} at risk); resolved in box {r['resolved_in_box']:.3f}, "
              f"within 5 min {r['resolved_within_5']:.3f}, e_net {r['e_net']:+.4f} (bound {r['e_net_lower_bound']:+.4f}), cost_r {r['cost_r']:.4f}")
    else:
        print("no slot has a qualifying width under the declared rule")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
