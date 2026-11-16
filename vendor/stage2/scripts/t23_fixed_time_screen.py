"""EXPLORATORY (D-410): T23's fixed-time version, screened on the collect map's own cells -- for each contract count and
each stop of D-383's range, the hourly slots that meet R3 (the collect map's CHOICE qualification) and the largest day
schedule of them that never overlaps (R1, R2), flat by 15:10 CT. A reading of `results/collect_map_nq.csv`; nothing is
computed from counts and nothing is chosen.

    python scripts/t23_fixed_time_screen.py

Writes results/t23_fixed_time_screen.csv (`slot`, `schedule` and `verdict` rows) with its manifest.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import pandas as pd  # noqa: E402

SCRIPT = "scripts/t23_fixed_time_screen.py"
DECISION = "D-410"
SOURCE = "results/collect_map_nq.csv"
STOPS = (1.0, 1.5, 2.0, 3.0, 4.0)          # R3: one to four times the target (D-383's menu range)
CONTRACTS = (5, 10, 20)
FLATTEN_MIN = 22 * 60 + 10                 # 15:10 CT on the slot clock (minutes from 17:00 CT)
LATE_GUARD_MIN = 1                         # the late-entry guard: a trade may start one minute after its slot
MIN_SIGNALS = 5                            # R1


def largest_schedule(slots: list[tuple[int, int]]) -> list[int]:
    """The largest set of (start, box) slots, on the slot clock, in which each trade's latest end (start + the guard +
    its box) is at or before the next chosen start and no trade ends after 15:10 CT -- earliest end first (optimal for
    interval scheduling). Returns the chosen starts in time order."""
    ok = [(s + LATE_GUARD_MIN + b, s) for s, b in slots if s + LATE_GUARD_MIN + b <= FLATTEN_MIN]
    chosen, free_at = [], -1
    for end, start in sorted(ok):
        if start >= free_at:
            chosen.append(start)
            free_at = end
    return sorted(chosen)


def clock(minutes: int) -> str:
    """The slot clock's minutes from 17:00 CT as HH:MM CT."""
    t = (17 * 60 + int(minutes)) % (24 * 60)
    return f"{t // 60:02d}:{t % 60:02d}"


def screen(cells: pd.DataFrame) -> pd.DataFrame:
    c = cells[cells["section"] == "cell"]                # other sections carry no delay (NaN)
    c = c[c["delay_min"].astype(int) == 0]
    ch, ck = c[c["period"] == "choice"], c[c["period"] == "check"]
    rows = []
    for n in CONTRACTS:
        for m in STOPS:
            g = ch[(ch["contracts"].astype(int) == n) & ((ch["stop_multiple"].astype(float) - m).abs() < 1e-9)]
            q = g[g["qualifies"].astype(str).str.lower() == "true"]
            best = q.sort_values("box_minutes").groupby("decision_slot_minutes").head(1).sort_values("decision_slot_minutes")
            slots = [(int(r.decision_slot_minutes), int(r.box_minutes)) for r in best.itertuples()]
            sched = largest_schedule(slots)
            for r in best.itertuples():
                k = ck[(ck["contracts"].astype(int) == n) & ((ck["stop_multiple"].astype(float) - m).abs() < 1e-9)
                       & (ck["decision_slot_minutes"].astype(int) == int(r.decision_slot_minutes))
                       & (ck["box_minutes"].astype(int) == int(r.box_minutes))]
                kk = k.iloc[0] if len(k) else None
                rows.append({"section": "slot", "contracts": n, "stop_multiple": m, "decision_ct": str(r.decision_ct),
                             "decision_slot_minutes": int(r.decision_slot_minutes), "box_minutes": int(r.box_minutes),
                             "in_schedule": int(r.decision_slot_minutes) in sched, "target_share": float(r.target_share),
                             "resolved": float(r.resolved), "worst_year_resolved": float(r.worst_year_resolved),
                             "mean_minutes": float(r.mean_minutes), "cost_per_win": float(r.cost_per_win),
                             "net_mean": float(r.net_mean), "risk_dollars": float(r.risk_dollars),
                             "late_target_share_drop": float(r.late_target_share_drop),
                             "check_resolved": float(kk["resolved"]) if kk is not None else float("nan"),
                             "check_cost_per_win": float(kk["cost_per_win"]) if kk is not None else float("nan"),
                             "check_target_share": float(kk["target_share"]) if kk is not None else float("nan")})
            in_s = best[best["decision_slot_minutes"].astype(int).isin(sched)]
            rows.append({"section": "schedule", "contracts": n, "stop_multiple": m, "qualifying_slots": len(slots),
                         "schedule_size": len(sched), "meets_r1": len(sched) >= MIN_SIGNALS,
                         "schedule": " ".join(clock(s) for s in sched),
                         "schedule_cost_per_win_mean": float(in_s["cost_per_win"].mean()) if len(in_s) else float("nan"),
                         "schedule_target_share_mean": float(in_s["target_share"].mean()) if len(in_s) else float("nan"),
                         "schedule_net_mean": float(in_s["net_mean"].mean()) if len(in_s) else float("nan")})
    out = pd.DataFrame(rows)
    sc = out[out["section"] == "schedule"]
    met = sc[sc["meets_r1"] == True]                                     # noqa: E712
    verdict = {"section": "verdict", "pairs_meeting_r1_r3": len(met),
               "pairs": "; ".join(f"{int(r.contracts)} MNQ at {r.stop_multiple:g}x ({int(r.schedule_size)} slots)"
                                  for r in met.itertuples()),
               "largest_schedule": int(sc["schedule_size"].max()) if len(sc) else 0}
    return pd.concat([out, pd.DataFrame([verdict])], ignore_index=True)


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import read_result, write_result

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    res = screen(read_result(rd / Path(SOURCE).name))
    write_result(res, "t23_fixed_time_screen", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 results_dir=results_dir,
                 parameters={"decision": DECISION, "source": SOURCE, "stops": list(STOPS), "contracts": list(CONTRACTS),
                             "flatten_ct": "15:10", "late_guard_min": LATE_GUARD_MIN, "min_signals": MIN_SIGNALS,
                             "qualification": "the collect map's CHOICE `qualifies` (R3, D-381)"},
                 notes={"status": "EXPLORATORY: T23's fixed-time version screened on the collect map's cells (D-410)",
                        "seed": "none: no randomness -- a reading of a result file on record and an exact schedule"},
                 description="EXPLORATORY: T23's fixed-time version (D-410) -- per contract count and stop, the hourly "
                             "slots meeting R3 and the largest non-overlapping day schedule (R1, R2), flat by 15:10 CT.")
    counter = VariantCounter(path=rd / "variants.jsonl")          # after the result: a failed run records nothing
    for n in CONTRACTS:
        for m in STOPS:
            counter.record(prereg_id=f"{DECISION}:t23_fixed_time", seed=0, exploratory=True,
                           params={"study": "T23 fixed-time schedule", "contracts": n, "stop_multiple": m},
                           label=f"T23's fixed-time schedule (D-410): {n} MNQ, stop {m:g}x the $200 target")
    pd.set_option("display.width", 220)
    print(res[res["section"] != "slot"].dropna(axis=1, how="all").to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
