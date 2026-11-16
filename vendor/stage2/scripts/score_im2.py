"""IM2 on the development period (P-04 §4 and §5): the rule audit, e and its bound per R at both scales, the D-145
gate at both scales and the two kill lines.

    python scripts/score_im2.py
    python scripts/score_im2.py --period confirmation [--engine-change D-nnn ...]

Needs the eight development kits R053-R060 ingested (`scripts/ingest_manual_run.py`) and Topstep 8284213 re-read on or
after 2026-10-01 with MCL and MNG recorded in config/fills.yaml; refuses otherwise (`im2_score.fees`). Before anything
is read it refuses unless P-04 is runnable in `prereg/REGISTRY.md` (D-179, the harness's rule), and every file it
writes carries the engine pin -- the hashes of the engine, scorer, rule, fee and instrument files (D-180,
`propedge.reporting.pin`). The confirmation run compares that pin with the development run's and refuses a changed
file unless `--engine-change` cites a DECISIONS.md entry naming it (P-04 §3), and it refuses until the development
chart review (D-185) and the second implementation's comparison with the kit (D-200) have passed. Steps, in the order
P-04 fixes:

1. **The rule audit (D-148).** `trade_audit.im2_checks` on every run at both scales and `im2_cost_checks` on the
   scored table. Any violation stops the scoring: it is a kit or scorer defect, diagnosed under the failure protocol
   (P-04 §5), never a verdict. Written to results/im2_development_audit.csv either way.
2. **e and its bound** per R (1, 2, 3) and scale, on the verdict's outcomes (`v`: net of costs, the price-lock
   treatment applied), beside the net outcomes before it (`u`) and the cost sensitivity (`w`):
   results/im2_development_edge.csv.
3. **The gate** at each scale on `v` (the verdict) and on `w` (the sensitivity, reported beside it), and, reported
   only, on `v` without the entries untradable as micros (`v_micro`, D-198) and without every entry on a micro expiry
   day (`v_expiry`, D-199): results/im2_development_gate.csv, each with the kill-line-1 reading.
4. **The verdict file**: the kill lines at each scale (the model is killed if either line fails at either scale),
   the counts and the descriptive measures P-04 §4 lists: results/im2_development_verdict.csv. The D-148 chart-review
   sample (twenty at random plus the three best and three worst, seed 20261120; D-181), with six entries on a micro's
   own last day added, shared across CL and NG in proportion to their counts (seed 20261121; D-198, D-199):
   results/im2_development_review.csv.
"""
from __future__ import annotations

import argparse
import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from propedge.backtest.harness import PreregRegistry, VariantCounter  # noqa: E402
from propedge.backtest.metrics import meets_criterion  # noqa: E402
from propedge.data.qc_algorithms import IM2_RUNS, im2_params  # noqa: E402
from propedge.reporting.pin import check_lean, check_pin, engine_pin, fee_dates, lean_versions_of  # noqa: E402
from propedge.reporting.results import read_manifest, sha256_of, write_result  # noqa: E402
from propedge.research import im2_score as sc  # noqa: E402
from propedge.research.trade_audit import (  # noqa: E402
    MAX_FILL_DISCREPANCIES, im2_checks, im2_cost_checks, review_sample, review_verdict, run_checks)

SCRIPT = "scripts/score_im2.py"
PREREG = "P-04"
ASSUMED_SD = 1.1
REVIEW_N, REVIEW_EXTREMES = 20, 3                       # D-148: twenty at random plus the three best and three worst
MICRO_REVIEW_N = 6                                      # D-198: extra entries from a micro's own last day
MICRO_OUTCOME = "v_micro"                               # D-198: v without the entries untradable as micros
EXPIRY_OUTCOME = "v_expiry"                             # D-199: v without every entry D-198 flags (both sets)
#: the readings reported beside the verdict and never acted on: outcome -> the verdict file's field prefix
READINGS = {MICRO_OUTCOME: "micro_tradable", EXPIRY_OUTCOME: "no_micro_expiry"}
DEVELOPMENT_PIN_FILE = "im2_development_gate.csv"       # the development manifest the confirmation run checks against
VERIFICATION_FILE = "im2_development_verification.csv"  # D-185: the recorded chart review; scoring is blocked without it
CROSSCHECK_FILE = "im2_second_implementation.csv"       # D-193, D-200: the second implementation against the kit
CRITERION = (f"zero rule violations; at most {MAX_FILL_DISCREPANCIES} fills more than one tick from the modelled "
             "price; any violation fails the run's verification and blocks scoring (D-185)")


def _clock(m: float) -> str:
    m = int(m)
    return f"{m // 60:02d}:{m % 60:02d}"


def _decisions_text() -> str:
    return (ROOT / "DECISIONS.md").read_text(encoding="utf-8")


def input_hashes(results_dir: Path | None = None) -> dict:
    """D-197: {run id: sha256 of its ingested result file}, None where the run is not ingested."""
    base = Path(results_dir) if results_dir is not None else sc.RESULTS_DIR
    out = {}
    for rid in sorted(IM2_RUNS.values()):
        p = base / f"manual_{rid.replace('-', '_')}.csv"
        out[rid] = sha256_of(p) if p.is_file() else None
    return out


def provenance(results_dir: Path | None = None) -> dict:
    """What every IM2 result file records beside its commit (D-180, D-184, D-197): the engine pin, the fee table's read
    dates, the LEAN version each ingested development run reports, and the sha256 of each run's ingested file."""
    return {"engine": engine_pin(), "fees_date_read": fee_dates(),
            "lean_versions": lean_versions_of(sorted(IM2_RUNS.values()), results_dir),
            "inputs_sha256": input_hashes(results_dir)}


def verification_passed(results_dir: Path) -> dict:
    """D-185: the recorded development chart review must exist and pass before anything downstream is scored."""
    path = results_dir / VERIFICATION_FILE
    if not path.is_file():
        raise RuntimeError(f"D-185: the development chart review is not recorded ({VERIFICATION_FILE}); scoring is "
                           "blocked until the operator's completed review sheet is recorded and passes: "
                           "python scripts/score_im2.py --record-review <the completed sheet>")
    row = pd.read_csv(path).iloc[0]
    if not bool(row["passed"]):
        raise RuntimeError("D-185: the recorded development chart review did not pass the acceptance criterion "
                           f"({int(row['rule_violations'])} rule violations, "
                           f"{int(row['fill_discrepancies_over_one_tick'])} fills more than one tick off, complete = "
                           f"{bool(row['complete'])}); a violation is a defect under the failure protocol (P-04 §5): "
                           "fix, rerun with the same seed, review again")
    return dict(row)


def crosscheck_passed(results_dir: Path) -> None:
    """D-193, D-200: IM2's verification waits for its second implementation to agree with the kit on every session of
    the eight development windows (`scripts/crosscheck_im2.py`)."""
    path = results_dir / CROSSCHECK_FILE
    if not path.is_file():
        raise RuntimeError(f"D-200: IM2's second implementation has not been compared with the kit ({CROSSCHECK_FILE});"
                           " the confirmation waits for it: python scripts/crosscheck_im2.py")
    df = pd.read_csv(path)
    if len(df) != len(IM2_RUNS) or not df["passed"].astype(bool).all():
        raise RuntimeError(f"D-200: IM2's second implementation disagrees with the kit ({int(df['mismatches'].sum())} "
                           f"mismatches over {len(df)} windows); each is diagnosed under the failure protocol "
                           "before anything is rerun")


def record_review(sheet_path: Path | str, registry: Path | None = None, results_dir: Path | None = None) -> int:
    """D-185: read the operator's completed chart-review sheet, apply the acceptance criterion and record the verdict
    (`results/im2_development_verification.csv`). Returns 0 on a pass, 1 otherwise."""
    PreregRegistry.load(registry).require_runnable(PREREG)
    base = Path(results_dir) if results_dir is not None else sc.RESULTS_DIR
    sheet = pd.read_csv(sheet_path, dtype=str, keep_default_na=False)
    v = review_verdict(sheet)
    write_result(pd.DataFrame([{**v, "sheet": Path(sheet_path).name, "sheet_sha256": sha256_of(sheet_path)}]),
                 "im2_development_verification", script=SCRIPT, seed=None, require_seed=False, prereg_id=PREREG,
                 provenance=provenance(base), parameters={"criterion": CRITERION}, results_dir=base,
                 description="D-185: the operator's chart review of IM2's development sample against the acceptance "
                             "criterion; the confirmation run refuses unless this passed.")
    print(f"chart review: complete = {v['complete']}, rule violations = {v['rule_violations']}, fills more than one "
          f"tick off = {v['fill_discrepancies_over_one_tick']} (at most {v['max_fill_discrepancies']}): "
          f"{'PASS' if v['passed'] else 'FAIL -- a defect under the failure protocol (P-04 §5)'}")
    return 0 if v["passed"] else 1


def main(period: str = "development", engine_changes: tuple[str, ...] = (), registry: Path | None = None,
         results_dir: Path | None = None) -> int:
    warnings.filterwarnings("ignore")
    PreregRegistry.load(registry).require_runnable(PREREG)    # D-179: refuses an abandoned or unregistered id
    base = Path(results_dir) if results_dir is not None else sc.RESULTS_DIR
    prov = provenance(base)
    if period == "confirmation":
        dev = read_manifest(base / DEVELOPMENT_PIN_FILE)
        if not dev.provenance or "engine" not in dev.provenance:
            raise RuntimeError(f"{DEVELOPMENT_PIN_FILE}'s manifest carries no engine pin; the development run must "
                               "be scored with the pin before a confirmation run (D-180)")
        changed = check_pin(dev.provenance["engine"], prov["engine"], cited=engine_changes,
                            decisions_text=_decisions_text())
        if changed:
            print(f"engine changed since the development run, each change recorded: {changed}")
        verification_passed(base)                                       # D-185
        crosscheck_passed(base)                                         # D-193, D-200
        conf_runs = getattr(sc, "IM2_CONFIRMATION_RUNS", None)
        if not conf_runs:
            raise NotImplementedError("P-04 §2: the confirmation kits (2024-04-01 .. 2026-08-31) are not built; they "
                                      "are built only after both development kill lines pass")
        check_lean(dev.provenance.get("lean_versions") or {}, lean_versions_of(sorted(conf_runs), base),
                   cited=engine_changes, decisions_text=_decisions_text())          # D-184
        raise NotImplementedError("the confirmation scoring is built with its kits, after the checks above")
    if period != "development":
        raise ValueError(f"period {period!r}: 'development' or 'confirmation'")
    cfg = sc.config()
    rt = sc.fees(cfg)                                   # refuses before the 2026-10-01 re-read (P-04 §3)
    specs = sc.micro_specs(cfg)
    pv = {m: s["point_value"] for m, s in specs.items()}
    counter = VariantCounter()
    counter.record(prereg_id=PREREG, params={"model": "IM2", "policy": sc.POLICY_ID, "period": "development"},
                   seed=sc.SEED, exploratory=False, label="P-04's one configuration, chosen from k = 4 policies")

    sessions, tails, tables, audit = {}, {}, [], []
    for m in sc.MARKETS:
        q = im2_params(m)
        parts_s, parts_e, tail = [], [], []
        for (mk, w), rid in sorted(IM2_RUNS.items()):
            if mk != m:
                continue
            days, ent, t = sc.read_run(rid)
            for s in sc.SCALES:
                for name, n in run_checks(ent, im2_checks(q, days, s)).items():
                    audit.append({"run": rid, "market": m, "scale": s, "check": name, "violations": n})
            parts_s.append(days)
            parts_e.append(ent)
            tail += t
        sessions[m], tails[m] = pd.concat(parts_s, ignore_index=True), tail
        tables.append(sc.entry_table(m, sessions[m], pd.concat(parts_e, ignore_index=True), round_turn=rt[m],
                                     spec=specs[m], cfg=cfg))
    table = pd.concat(tables, ignore_index=True)
    for s in sc.SCALES:
        for name, n in run_checks(table, im2_cost_checks(rt, pv, sc.RR_ALL, s)).items():
            audit.append({"run": "all", "market": "all", "scale": s, "check": name, "violations": n})
    audit_df = pd.DataFrame(audit)
    bad = int(audit_df["violations"].sum())
    write_result(audit_df, "im2_development_audit", script=SCRIPT, seed=None, require_seed=False, prereg_id=PREREG,
                 provenance=prov, parameters={"runs": sorted(IM2_RUNS.values()), "round_turn": rt},
                 description="D-148's rule audit of IM2's development kits at both scales, and the scorer's costs.")
    if bad:
        print(f"RULE AUDIT: {bad} violations -- a kit or scorer defect; scoring stops (P-04 §5, failure protocol).")
        print(audit_df[audit_df["violations"] > 0].to_string(index=False))
        return 1

    days = sc.day_set(sessions, tails, *sc.DEVELOPMENT)
    reading_tables = {MICRO_OUTCOME: table[~table["micro_untradable"]],           # D-198: what a micro could take
                      EXPIRY_OUTCOME: table[~(table["micro_untradable"] | table["micro_last_day"])]}   # D-199
    edge_rows, stats = [], {}
    for s in sc.SCALES:
        for col in ("v", "u", "w"):
            for R in sc.RR_ALL:
                st = sc.edge(table, days, R, s, col)
                st["old_criterion_met"] = meets_criterion(st["e"], st["lb"])
                edge_rows.append({"market": "all", **st})
                stats[(s, col, float(R))] = st
        for m in sc.MARKETS:                             # each market's e, descriptive only (P-04 §4)
            for R in sc.RR_ALL:
                st = sc.edge(table[table["market"] == m], days, R, s, "v")
                edge_rows.append({"market": m, **st, "old_criterion_met": meets_criterion(st["e"], st["lb"])})
        for oc, src in reading_tables.items():           # D-198, D-199: v on fewer entries, reported only
            for R in sc.RR_ALL:
                st = {**sc.edge(src, days, R, s, "v"), "outcome": oc}
                st["old_criterion_met"] = meets_criterion(st["e"], st["lb"])
                edge_rows.append({"market": "all", **st})
                stats[(s, oc, float(R))] = st
    edge_df = pd.DataFrame(edge_rows)
    common = {"prereg_id": PREREG, "variant_count": counter.count(PREREG), "provenance": prov}
    write_result(edge_df, "im2_development_edge", script=SCRIPT, seed=sc.SEED, **common,
                 parameters={"days": len(days), "period": list(sc.DEVELOPMENT), "boot_len": sc.BOOT_LEN, "reps": sc.REPS,
                             "round_turn": rt, "assumed_sd": ASSUMED_SD},
                 description="IM2's e and one-sided 95 % lower bound per R and scale (v: the verdict's outcomes; u: "
                             "before the price-lock treatment; w: with the MCL/MNG cost sensitivity; v_micro: v "
                             "without the entries untradable as micros, D-198; v_expiry: v without those and the "
                             "entries on a micro's own last day, D-199; both reported only), all markets and each "
                             "market alone (descriptive).")

    gate_frames, verdict = [], {"days": len(days)}
    for s in sc.SCALES:
        for col in ("v", "w", *READINGS):
            st = {float(R): stats[(s, col, float(R))] for R in sc.RR_GATE}
            src, oc = (reading_tables[col], "v") if col in READINGS else (table, col)
            df, passed = sc.run_gate(sc.blocks(src, days, s, oc), st)
            df.insert(0, "scale", s)
            df.insert(1, "outcome", col)
            df["gate_passed"] = passed
            gate_frames.append(df)
            if col == "v":
                k = sc.kill_lines(df, passed)
                verdict.update({f"{key}_{s}": v for key, v in k.items()})
            elif col == "w":
                verdict[f"sensitivity_gate_passed_{s}"] = passed
            else:                                        # D-198, D-199: the verdict read again, reported, never acted on
                k = sc.kill_lines(df, passed)
                verdict.update({f"{READINGS[col]}_{key}_{s}": v for key, v in k.items()})
    gate_df = pd.concat(gate_frames, ignore_index=True)
    write_result(gate_df, "im2_development_gate", script=SCRIPT, seed=sc.SEED, **common,
                 parameters={"policy": sc.policy().as_dict(), "bankroll": sc.BANKROLL, "horizon_days": sc.HORIZON,
                             "paths": sc.PATHS, "accounts": sc.ACCOUNTS, "settlement": "mae", "mode": "rotation"},
                 description="IM2's D-145 gate on development data at the reference price and at actual prices, on "
                             "the verdict's outcomes (v), with the MCL/MNG cost sensitivity (w), without the entries "
                             "untradable as micros (v_micro, D-198) and without every entry on a micro expiry day "
                             "(v_expiry, D-199), with kill line 1's resolved-Combine days.")

    verdict["killed"] = bool(verdict["killed_p"] or verdict["killed_a"])
    for pre in READINGS.values():                        # D-198, D-199: reported beside the verdict, never instead of it
        verdict[f"{pre}_killed"] = bool(verdict[f"{pre}_killed_p"] or verdict[f"{pre}_killed_a"])
        verdict[f"{pre}_verdict_same"] = verdict[f"{pre}_killed"] == verdict["killed"]
    for m in sc.MICRO_ENDS_EARLY:                        # D-198's counts, per market
        mt = table[table["market"] == m]
        verdict[f"entries_micro_untradable_{m}"] = int(mt["micro_untradable"].sum())
        verdict[f"entries_on_micro_last_day_{m}"] = int(mt["micro_last_day"].sum())
    x = table[table["dist_p"].notna()]
    verdict.update({
        "entries": int(len(table)), "entries_through_actual": int(table["dist_a"].isna().sum()),
        "entries_in_release_minutes": int(table["release_entry"].sum()),
        "exits_2to1_in_release_minutes_p": int(table["release_exit2_p"].sum()),
        "exits_2to1_in_release_minutes_a": int((table["release_exit2_a"] & table["dist_a"].notna()).sum()),
        **{k: v for m in sc.MARKETS for k, v in sc.session_counts(m, sessions[m], days, tails[m]).items()},
        "entries_flagged_price_lock": int(table["lock_flag"].sum()),
        "days_flagged_price_lock": int(table.loc[table["lock_flag"], "d"].nunique()),
        "entries_per_day": float(len(x) / len(days)),
        **{f"entries_per_day_{m}": float((x["market"] == m).sum() / len(days)) for m in sc.MARKETS},
        "sd_r1_p": stats[("p", "v", 1.0)]["sd"], "sd_r2_p": stats[("p", "v", 2.0)]["sd"], "assumed_sd": ASSUMED_SD,
        "harvest_day_share_150": sc.harvest_day_share(table, days),
        **sc.mcl_restriction_exposure(table),
        "verification": "pending: the chart review is recorded with --record-review (D-185)",
    })
    write_result(pd.DataFrame([verdict]), "im2_development_verdict", script=SCRIPT, seed=sc.SEED, **common,
                 parameters={"kill_line_1_days": sc.COMBINE_DAYS_LIMIT, "scales": list(sc.SCALES)},
                 description="IM2's development verdict under P-04 §5: both kill lines at both scales, and the "
                             "counts and descriptive measures of §4.")

    log = table.copy()
    log["entry_ct"] = log["entry_t"].map(_clock)
    log["exit_2to1_ct"] = log["exit_t_p"].map(_clock)
    sample = review_sample(log.reset_index(drop=True), n=REVIEW_N, seed=sc.SEED, extremes=REVIEW_EXTREMES,
                           r_col="v2_p")
    # D-198: over-sample the entries on a micro's own last day; D-199: in proportion to each market's count
    split = sc.review_split({m: int((log["micro_last_day"] & (log["market"] == m)).sum()) for m in sc.MICRO_ENDS_EARLY},
                            MICRO_REVIEW_N)
    extras = [review_sample(log[log["micro_last_day"] & (log["market"] == m)].reset_index(drop=True), n=k,
                            seed=sc.SEED + 1, extremes=0, r_col="v2_p").assign(why="micro expiry day")
              for m, k in split.items() if k]
    if extras:
        sample = (pd.concat([sample, *extras], ignore_index=True)
                  .drop_duplicates(subset=["market", "d", "t"], keep="first")
                  .sort_values(["d", "entry_t"], kind="stable").reset_index(drop=True))
    write_result(sample, "im2_development_review", script=SCRIPT, seed=sc.SEED, prereg_id=PREREG, provenance=prov,
                 parameters={"n": REVIEW_N, "extremes": REVIEW_EXTREMES, "r_col": "v2_p",
                             "micro_expiry_day_extra": MICRO_REVIEW_N, "micro_expiry_day_split": split,
                             "micro_expiry_day_seed": sc.SEED + 1},
                 description="D-148's chart-review sample of IM2's development entries (seeded), times in CT and ET, "
                             "with entries on a micro contract's own last day over-sampled (D-198).")

    print(f"IM2 development: {verdict['entries']} entries over {len(days)} days; killed = {verdict['killed']} "
          f"(reference: lines {verdict['kill_line_1_p']}/{verdict['kill_line_2_p']}; actual: "
          f"{verdict['kill_line_1_a']}/{verdict['kill_line_2_a']})")
    return 0


def _cli(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--period", choices=("development", "confirmation"), default="development")
    ap.add_argument("--engine-change", action="append", default=[], metavar="D-nnn",
                    help="a DECISIONS.md entry naming an engine file or LEAN version changed since the development "
                         "run (D-180, D-184)")
    ap.add_argument("--record-review", metavar="SHEET.csv",
                    help="record the operator's completed chart-review sheet against the acceptance criterion (D-185)")
    a = ap.parse_args(argv)
    if a.record_review:
        return record_review(a.record_review)
    return main(period=a.period, engine_changes=tuple(a.engine_change))


if __name__ == "__main__":
    raise SystemExit(_cli())
