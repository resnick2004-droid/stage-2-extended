"""EXPLORATORY (Q-132; the lead's E-189 on the Q-45 audit, `docs/audits/Q-45_breakeven_fidelity_2026-11-17.md`): the
breakeven move's fidelity reading, second version -- the same rule sets as Q-20's (`extended.breakeven.RULE_SETS`:
`stage2`, `stop_first`, `delay5`, `both`), on P-14, **P-15** and P-16, with per-start rows for every rule set, design
and arm, a paired interval of each corrected rule set against `stage2`, the minimum detectable difference in P, the
assumptions stated and the variants recorded. Beside, never deciding: R* stays P-14 unless the operator rules
otherwise; nothing is chosen from these readings. Never overwrites `results/breakeven_fidelity.csv` (E-188).

    python scripts/breakeven_fidelity_2.py --check --starts 4 --paths 4     # the pipeline: every identity at its
                                                                            #   size, written to a temporary folder
    python scripts/run_clean.py --name breakeven-fidelity-2 --task Q-132 --hours 6 --mem-gb 2.8 -- python scripts/breakeven_fidelity_2.py

**What the audit asked, and where it is answered:**

* **D1** -- `results/breakeven_fidelity_2_starts.csv`: one row a (design, rule set, arm, start), every rule set, design
  and arm (`extended.breakeven_readings.START_FILE_COLS`: the start's U1 record, the exact runs that differed with their
  records, the months ahead P reads, Q-17's path and evenness values; money unrounded). Before anything is written, the
  scorecard, extra and path rows of every (design, rule set, arm) are re-made from that frame's own CSV text and held to
  the runner's (`rederive_problems`, refusing). The summary file's manifest names the start file's sha256.
* **C1** -- P-15 (`rc_s100_all`), built by the same `atlas_a3.walk_minutes` walk as P-16 (`extended.breakeven.p15_build`:
  `rc_dev_test.build_cells`' two lines with the walk substituted for the one call that walks its marks). Its identities
  under `stage2`: its trades are `rc_reentry_screen.csv`'s `rc_s100_all` row and its pinned content hash
  (`rc_dev_test.trade_problems`); with every response off the adapter's start rows equal `user_journey.csv`'s for p15
  (every column, the starts run); at 500 paths its gate row equals `rc_s100_all_gate.csv`'s 0 % rows on `GATE_COLS`
  (1e-6 relative). No per-path file of P-15's gate is vendored, so below 500 paths its gate is not compared (printed).
* **C2** -- section `paired`: each corrected rule set against `stage2`, design, arm and block (all starts, judged), on
  P's per-start unit, by RD-02's section 9.2 (`extended.pp_reading`): the mean (held equal to the cards' difference),
  the kept windows, sign count, n_eff, and with four kept windows the 90 % interval, its MDD and the honesty label
  (section `honesty`: 21 shapes, 20,000 series a setting, seed 20262260 by role). **`mdd_P`** (section `extra`) filled:
  Q-16's shipped `pcons` at 0.05/132, 80 % power, against P-14 on the same rule set and arm, the judged block (seed
  20262261 by role; `extended.breakeven_readings`).
* **C6** -- the log's first line names the commit and whether the tree is clean; the nine variants (three corrections x
  three designs) are recorded in `results/variants.jsonl` through the vendored `VariantCounter`.
* **C7** -- the assumptions (the fill profile, the payout lag and spacing model, the no-closure state table, the move's
  latency, the response off) in the manifest's `parameters.assumptions`, its `notes.assumptions`, and section
  `assumptions` of the file.

**Everything else is Q-20's runner's** (`scripts/breakeven_fidelity.py`, E-024), unchanged: the substitution (only the
trades' walk), P-14's and P-16's identities (P-14's re-walked A3 frame equals the cache's exactly; P-16's re-walked cell
has its pinned trades hash; each gate's first `--paths` paths equal its registered per-path rows, and at 500 paths its
registered row; U1's start rows), the gate at the registered campaign seeds (P-14 20261131, P-15 20261204, P-16
20261206 -- common random numbers with the registered rows), the bounds recomputed from each rule set's trades by the
design's own rule, the U1 replay with every response off (Q-17's start seeds; nothing drawn at 0 %), every reading's
consistency checks. Any failure: nothing written.

**The read (Q-58, E-037).** Before any of the engine's work `main` authorises it through
`extended.reader.authorise_engine_read`: purpose `registered_design`, declaration **E-024** (the row that merged Q-17
and Q-20, which names P-14, P-15 and P-16), the designs run, the window 2020-01-02 to 2026-07-16, A1's events and days,
A3's cached walk and the bars. A refusal ends the run (exit 3) before anything is read; ledgered only inside a clean run.
"""
from __future__ import annotations

import argparse
import gc
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for _p in (str(ROOT), str(ROOT / "identity")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()

import pandas as pd  # noqa: E402

import user_beside_identity as I  # noqa: E402

from extended import breakeven as BE  # noqa: E402
from extended import breakeven_readings as BR  # noqa: E402
from extended import reader  # noqa: E402
from extended import user_beside as B  # noqa: E402
from extended import user_readings as R  # noqa: E402

SCRIPT = "scripts/breakeven_fidelity_2.py"
RESULT = "breakeven_fidelity_2"
STARTS_RESULT = "breakeven_fidelity_2_starts"
TASK = "Q-132"
VARIANT_ID = "Q-132:breakeven_fidelity_2"
DESIGNS = ("p14", "p15", "p16")
DESIGN_IDS = {"p14": "P-14", "p15": "P-15", "p16": "P-16"}
#: the row that admits the re-read (E-037): Q-17's and Q-20's merge row, naming P-14, P-15 and P-16
READ_ROW = "E-024"
VENDOR = ROOT / "vendor" / "stage2"
FULL_PATHS = 500
CORRECTIONS = tuple(n for n, _ in BE.RULE_SETS if n != BR.REFERENCE_RULES)
READING = ("EXPLORATORY (Q-132; the Q-45 audit, E-189): beside the registered rows, never deciding; R* stays P-14 unless "
           "the operator rules otherwise")
COLS = ["section", "reading", "design", "rules", "against", "arm", "shift", "rr", "block", "measure", "stat", "value",
        "n", "h", "n_w", "note"]


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    state = BR.git_state(ROOT)
    print(BR.provenance_line(state, SCRIPT, argv), flush=True)          # C6: the log's head

    import rc150_dev_test as P
    import rc_dev_test as D
    import user_journey as UJ
    import yaml

    from extended.results import read_result, write_result
    from propedge import RESULTS_DIR
    from propedge.reporting.results import sha256_of

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--starts", type=int, default=None, help="with --check: U1 starts a design and arm")
    ap.add_argument("--paths", type=int, default=FULL_PATHS, help="gate paths (500 for the readings)")
    ap.add_argument("--designs", default=None, help="with --check: a comma list of p14, p15, p16")
    ap.add_argument("--workers", type=int, default=1)
    a = ap.parse_args(argv)
    if not a.check and (a.starts is not None or a.paths != FULL_PATHS or a.designs is not None):
        print(f"REFUSED ({TASK}): the readings run every start and 500 gate paths of every design; a smaller run is "
              "--check")
        return 2
    designs = DESIGNS if a.designs is None else tuple(x for x in a.designs.split(",") if x)
    if not designs or any(d not in DESIGNS for d in designs) or len(set(designs)) != len(designs):
        print(f"REFUSED ({TASK}): the designs are {', '.join(DESIGNS)}, not {', '.join(designs) or 'none'}")
        return 2
    designs = tuple(d for d in DESIGNS if d in designs)                  # the declared order
    try:                                            # Q-58: the engine's read authorised (ledgered in a clean run only)
        reader.authorise_engine_read(
            reader.CHOICE_START, reader.JUDGED_END, purpose=reader.REGISTERED_DESIGN, declaration=READ_ROW,
            design=[DESIGN_IDS[d] for d in designs], files=I.SI.engine_files(VENDOR, bars=True),
            what=f"{READ_ROW}'s readings ({SCRIPT}, {TASK}): {', '.join(designs)} re-walked under the breakeven "
                 f"corrections, {a.paths} gate paths, " + ("every start" if a.starts is None else f"{a.starts} starts")
                 + (" (--check)" if a.check else ""))
    except (reader.ReadRefused, FileNotFoundError) as exc:
        print(I.SI.refusal(exc), flush=True)
        return 3
    rd = RESULTS_DIR
    t_all = time.time()
    ref = I.u1_reference(rd, designs)
    defs = {c["config"]: c for c in UJ.CONFIG_DEFS}
    off = B.BY_NAME["off"]
    rows: list[dict] = []
    starts_parts: list[pd.DataFrame] = []
    ahead: dict[tuple[str, str, str, str], dict[str, float]] = {}
    cards: dict[tuple[str, str, str, str], float] = {}
    stage2_jobs: dict[tuple[str, str], dict] = {}
    timing: dict[str, float] = {}
    not_compared: list[str] = []

    def ident(design: str, rules: str, check: str, problems: list[str]) -> bool:
        rows.append({"section": "identity", "design": design, "rules": rules, "measure": check, "stat": "holds",
                     "value": float(not problems), "note": "; ".join(problems[:4])})
        print(f"identity {'HOLDS' if not problems else 'FAILS'}: {design} {rules}: {check}"
              + (f" -- {'; '.join(problems[:6])}" if problems else ""), flush=True)
        return not problems

    def refuse() -> int:
        print(f"REFUSED ({TASK}): nothing written", flush=True)
        return 3

    for design in designs:
        reg = BE.registered_gate(design)
        for shift, vals in reg.items():
            rows += [{"section": "gate", "design": design, "rules": "registered", "shift": shift, "measure": c,
                      "stat": "value", "value": v} for c, v in vals.items()]
        X = BE.a3_inputs() if design == "p14" else None
        t_ref = None
        for name, rules in BE.RULE_SETS:
            t0 = time.time()
            print(f"{design} {name}: the re-walk and the builders...", flush=True)
            if design == "p14":
                frame = BE.a3_frame(rules, X)
                if name == "stage2" and not ident(design, name, "the re-walked A3 frame equals the cache's exactly",
                                                  BE.frame_problems(frame, X["cached"])):
                    return refuse()
                b = BE.p14_build(frame, rd)
                del frame
            elif design == "p15":
                b = BE.p15_build(rules, rd)
                if name == "stage2" and not ident(
                        design, name, f"the re-walked cell is {D.P15.screen_file}'s {D.P15.cell} (count, busiest day, "
                        "capacity, long share, candidates a day, every R's unresolved share) and its content hash is "
                        "P-15's pinned TRADES_SHA256", BE.p15_trade_problems(b, rd)):
                    return refuse()
            else:
                b = BE.p16_build(rules, rd)
                if name == "stage2":
                    th = D.trades_hash(b["trades"])
                    if not ident(design, name, "the re-walked cell's content hash is P-16's pinned TRADES_SHA256",
                                 [] if th == P.SPEC.trades_sha256 else [f"{th} != {P.SPEC.trades_sha256}"]):
                        return refuse()
            gc.collect()
            t = b["trades"]
            if name == "stage2":
                t_ref = t
            rr = sorted(float(c[2:]) for c in t.columns if c.startswith("r_"))
            for r in BE.trade_rows(t, t_ref, rr):
                rr_ = r.pop("rr")
                rows += [{"section": "trades", "design": design, "rules": name, "rr": rr_, "measure": k, "stat": "value",
                          "value": float(v)} for k, v in r.items()]
            timing[f"{design}|{name}|build"] = round(time.time() - t0, 1)
            # the gate
            t1 = time.time()
            gate_fn = {"p14": BE.p14_gate, "p15": BE.p15_gate, "p16": BE.p16_gate}[design]
            df, bad = gate_fn(b, a.paths, a.workers)
            mine = BE.gate_rows(df)
            if name == "stage2":
                if design == "p15":
                    if a.paths != FULL_PATHS:
                        not_compared.append(f"p15's gate below {FULL_PATHS} paths (no per-path file is vendored)")
                        print(f"identity (p15's gate) needs all {FULL_PATHS} paths (no registered per-path file); not "
                              f"compared at {a.paths}", flush=True)
                elif not ident(design, name, f"the gate's first {a.paths} paths equal the registered per-path rows "
                               "(every PATH_COLS column, both shifts)", bad):
                    return refuse()
                if a.paths == FULL_PATHS and not ident(design, name, "the gate row equals the registered row on "
                                                       f"{len(BE.GATE_COLS)} columns (1e-6 relative), both shifts",
                                                       BE.gate_problems(mine, reg)):
                    return refuse()
            for shift, vals in mine.items():
                rows += [{"section": "gate", "design": design, "rules": name, "shift": shift, "measure": c,
                          "stat": "value", "value": v} for c, v in vals.items()]
            timing[f"{design}|{name}|gate"] = round(time.time() - t1, 1)
            del df
            # the user journey through Q-17's adapter, every response off
            for arm in UJ.ARMS:
                t2 = time.time()
                job = b["jobs"][arm]
                if name == "stage2":
                    stage2_jobs[(design, arm)] = {"args": job["args"]}
                chosen = UJ.start_choice(len(job["blocks"]), a.starts)
                outs = B.run_starts(design, arm, off, job, chosen, a.workers)
                if name == "stage2" and not ident(
                        design, f"{name} {arm}", "with every response off the adapter's start rows equal "
                        f"user_journey.csv's (every column, {'every start' if a.starts is None else a.starts})",
                        I.u1_compare_outs(design, defs[design], arm, outs, ref, len(job["blocks"]), a.starts)):
                    return refuse()
                srows, _ = R.summary(design, arm, off, outs, blocks=R.Q44_BLOCKS)          # W3.1: named
                bad = R.consistency_problems(srows, outs, f"{design} {name} {arm}", blocks=R.Q44_BLOCKS)
                if not ident(design, f"{name} {arm}", "every run's payouts and fees against the engine's totals; the "
                             "extra P equal to the card's; the limits' P ordered; shares in [0, 1]", bad):
                    return refuse()
                # D1: the per-start rows, and every scorecard, extra and path row re-made from their CSV text
                st = BR.start_frame(design, name, arm, outs)
                back = BR.read_text_csv(st.to_csv(index=False))
                if not ident(design, f"{name} {arm}", "the scorecard, extra and path rows re-made from the per-start "
                             "rows' CSV text alone equal the runner's (every value to 1e-9, every n)",
                             BR.rederive_problems(back, srows, f"{design} {name} {arm}")):
                    return refuse()
                del back
                starts_parts.append(st)
                records = [x["rec"] for x in outs]
                for block, which in BR.BLOCKS:
                    ahead[(design, name, arm, block)] = BR.p_months_ahead(records, which)
                for r in srows:
                    if r["section"] == "scorecard" and r["measure"] == "P":
                        cards[(design, name, arm, r["block"])] = float(r["value"])
                rows += [{**{k: v for k, v in r.items() if k not in ("response", "kind", "enforcement_p", "rtp",
                                                                       "rtp_warnings", "ftp_label")},
                          "rules": name} for r in srows if r["section"] != "response"]
                timing[f"{design}|{name}|{arm}"] = round(time.time() - t2, 1)
                del outs, records
            print(f"timing: {design} {name}: {time.time() - t0:.0f} s", flush=True)
            del b
            gc.collect()
        del X
        gc.collect()

    # C2: each corrected rule set against stage2, on the same starts (RD-02 9.2), with the honesty series
    t3 = time.time()
    rule_names = [n for n, _ in BE.RULE_SETS]
    _, probs, need = BR.paired_rows(ahead, cards, designs, rule_names, UJ.ARMS)
    if not ident("all", "paired", "every paired mean equals the cards' P difference, on the same starts", probs):
        return refuse()
    hon = BR.honesty(need)
    prow, _, _ = BR.paired_rows(ahead, cards, designs, rule_names, UJ.ARMS, honesty=hon)
    rows += prow + BR.honesty_rows(hon, BR.HONESTY_SEED, BR.HONESTY_SERIES)
    timing["paired_and_honesty"] = round(time.time() - t3, 1)
    # mdd_P (Q-16's comparison against P-14, the judged block)
    t4 = time.time()
    mdd_done = BR.fill_mdd_p(rows, ahead, designs, rule_names, UJ.ARMS)
    timing["mdd_P"] = round(time.time() - t4, 1)
    # C7: the assumptions
    fills = yaml.safe_load((VENDOR / "config" / "fills.yaml").read_text(encoding="utf-8"))
    assumed = BR.assumptions(stage2_jobs, dict(BE.RULE_SETS), (fills.get("meta") or {}).get("active_profile"))
    rows += BR.assumption_rows(assumed)

    res = pd.DataFrame(rows)
    res.insert(1, "reading", READING)
    res = res[[c for c in COLS if c in res.columns] + [c for c in res.columns if c not in COLS]]
    starts = pd.concat(starts_parts, ignore_index=True)
    seconds = time.time() - t_all
    variants = [(d, n, BR.variant_params(d, n, BE.RULES[n], a.paths, "every start" if a.starts is None else
                                         int(a.starts))) for d in designs for n in CORRECTIONS]
    params = {"task": TASK, "decisions": ["E-012 (2)", "E-013 (2)", "E-024", "E-188", "E-189"],
              "audit": "docs/audits/Q-45_breakeven_fidelity_2026-11-17.md (D1, C1, C2, C6, C7)",
              "designs": list(designs), "rule_sets": {n: {"name": r.name, "breakeven_tie": r.breakeven_tie,
                                                           "breakeven_delay": r.breakeven_delay}
                                                       for n, r in BE.RULE_SETS},
              "corrections": {"stop_first": "on a bar after the move that touches the entry and trades through the "
                                            "target, the stop first (Stage 2's walk books the target, "
                                            "fv3_rung_walk.py:184-185)",
                              "delay5": "the move decided on the session's open bar's open, in force from the first "
                                        "present bar opening five minutes after it (D-266); the original bracket "
                                        "governs until then"},
              "gate_paths": int(a.paths), "gate_seeds": {"p14": BE.P14_GATE_SEED, "p15": BE.P15_GATE_SEED,
                                                         "p16": BE.P16_GATE_SEED},
              "gate_cols": list(BE.GATE_COLS), "u1_starts": "every start" if a.starts is None else int(a.starts),
              "u1_response": "off (0 % denial, the placement off, no Focused Trader model)",
              "u1_path_seeds": "Q-17's: lockstep.child_seed(20261920, 0, start_day); nothing drawn at 0 %",
              "bounds": "recomputed from each rule set's trades by the design's own rule (atlas_a3.bounds)",
              "seeds": {"block": [BR.SEED_BLOCK[0], BR.SEED_BLOCK[-1]],
                        "roles": {str(k): v for k, v in BR.SEED_ROLES.items()},
                        "inherited": {"gates": {"p14": BE.P14_GATE_SEED, "p15": BE.P15_GATE_SEED,
                                                "p16": BE.P16_GATE_SEED},
                                      "u1_start_seeds": "user_beside.start_seed (20261920), nothing drawn at 0 %",
                                      "p_bound_fixed_b": "extended.p_bound.SEED (Q-16's 20261919)"}},
              "paired": {"method": "RD-02 9.2 (prereg/RD-02_payout_policy.md; extended.pp_reading): every other "
                                   f"{BR.P_HORIZON}-start window, a two-sided {BR.INTERVAL_LEVEL:.0%} Student t from "
                                   f"{BR.MIN_WINDOWS} kept windows, the sign count, n_eff, the MDD",
                         "unit": "a start's months ahead over three (u_select.months_ahead / 3), the corrected rule "
                                 "set less stage2, on the same starts",
                         "honesty": {"settings": [list(s) for s in sorted(need)],
                                     "series_per_setting": BR.HONESTY_SERIES, "seed": BR.HONESTY_SEED}},
              "mdd_P": {"statistic": "extended.p_bound.SHIPPED", "k": BR.MDD_K, "level": BR.mdd_level(),
                        "power": BR.MDD_POWER, "replications": BR.MDD_REPS, "flip_block": BR.MDD_FLIP_BLOCK,
                        "against": BR.MDD_REFERENCE, "block": "judged", "seed": BR.MDD_SEED, "computed": mdd_done},
              "assumptions": assumed, "not_compared": not_compared,
              "references": {f: sha256_of(rd / f) for f in (*BE.GATE_FILES.values(), I.SI.U1_FILE,
                                                            D.P15.screen_file)},
              "provenance_at_start": state, "variant_id": VARIANT_ID,
              "timing": timing, "workers": int(a.workers), "seconds": round(seconds, 1)}
    notes = {"status": READING, "selection": "none",
             "variant_count_rule": "three corrections a design; Stage 2's walk is the identity, not a variant",
             "assumptions": BR.assumptions_note(assumed),
             "supersedes": "nothing: results/breakeven_fidelity.csv (E-188) stands; this is a second reading"}
    desc = ("EXPLORATORY (Q-132): P-14's, P-15's and P-16's trades re-walked with the breakeven move corrected -- the "
            "stop first on a bar touching the entry and trading through the target after the move, the move five "
            "minutes after the session open, each alone and both -- read beside the registered rows: the trades' exit "
            "kinds, the gate row (500 paths at the registered seeds), the user scorecard and E-007 (e)'s measures with "
            "mdd_P, each corrected rule set's paired interval against stage2 (RD-02 9.2), the assumptions; every "
            "start's rows in the start file. Beside, never deciding.")
    sdesc = ("EXPLORATORY (Q-132): the per-start rows of breakeven_fidelity_2 -- one row a design, rule set, arm and "
             "start: the U1 record with its differing exact runs, the months ahead P reads, Q-17's path values; "
             "every scorecard, extra and path row of breakeven_fidelity_2 is re-made from them.")

    # E-185's licence guard on both tables as they will be written (names and shares only; never a value): printed and
    # recorded, not refusing -- a dollar column's class is the allow-list's (tests/price_level_allowlist.csv), the lead's
    from extended import price_levels as PL

    allow = PL.load_allowlist()
    guard = {}
    for nm, frame_ in ((f"results/{STARTS_RESULT}.csv", starts), (f"results/{RESULT}.csv", res)):
        found, _ = PL.apply_allowlist(PL.scan_lines(nm, frame_.to_csv(index=False).splitlines(True)), allow)
        guard[nm] = [str(f) for f in found]
        print(f"licence guard ({nm}): " + ("no finding" if not found else f"{len(found)} finding(s) the pre-commit hook "
              f"would refuse unless allow-listed -- " + "; ".join(str(f) for f in found[:8])), flush=True)
    params["licence_guard"] = guard

    def write(target: Path | None) -> list[str]:
        where = Path(target) if target is not None else None
        BR.record_variants(where if where is not None else ROOT / "results", VARIANT_ID, B.DENIAL_SEED, variants)
        scsv, sman = write_result(starts, STARTS_RESULT, script=SCRIPT, seed=B.DENIAL_SEED,
                                  parameters={"task": TASK, "of": f"{RESULT}.csv", "columns": list(BR.START_FILE_COLS),
                                              "designs": list(designs), "rule_sets": [n for n, _ in BE.RULE_SETS],
                                              "arms": list(UJ.ARMS), "money": "as the engine booked it, unrounded",
                                              "assumptions": assumed},
                                  results_dir=target, description=sdesc, exploratory=True,
                                  variant_count=len(variants), notes={**notes, "of": f"{RESULT}.csv"})
        read_result(scsv)
        params["start_file"] = {"name": scsv.name, "sha256": sha256_of(scsv), "rows": int(len(starts))}
        csv, man = write_result(res, RESULT, script=SCRIPT, seed=B.DENIAL_SEED, parameters=params, results_dir=target,
                                description=desc, exploratory=True, variant_count=len(variants), notes=notes)
        read_result(csv)
        return [scsv.name, sman.name, csv.name, man.name, "variants.jsonl"]

    if a.check:
        with tempfile.TemporaryDirectory(prefix="breakeven_fidelity_2_check_") as td:
            wrote = write(Path(td))
        print(f"every identity holds; the pipeline ran on {list(designs)} ({a.paths} gate paths, "
              f"{'every' if a.starts is None else a.starts} start(s)) and wrote {wrote} ({len(res)} summary rows, "
              f"{len(starts)} start rows) to a temporary folder, since removed; nothing written to results/, no "
              f"reading printed (--check). {seconds:.0f} s", flush=True)
    else:
        wrote = write(None)
        print(f"written: {wrote} ({len(res)} summary rows, {len(starts)} start rows); {seconds:.0f} s", flush=True)
    mem = I.SI.peak_memory()
    if mem:
        print(mem, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
