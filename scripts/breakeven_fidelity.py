"""EXPLORATORY (Q-20; E-012 (2), E-013 (2)): P-14's and P-16's trades re-walked with the breakeven move's two fidelity
defects corrected -- (a) the stop first on a bar after the move that both touches the entry and trades through the
target, (b) the move made five minutes after the session open -- each alone and both; P, the guarded measures and the
gate row read beside the registered rows. Beside, never deciding: R* stays P-14 unless the operator rules otherwise;
nothing is chosen from these readings.

    python scripts/breakeven_fidelity.py --check --starts 4 --paths 4    # the pipeline: every identity at its size,
                                                                         #   written to a temporary folder, removed
    python scripts/run_clean.py --name breakeven-fidelity --task Q-20 --hours 4 --mem-gb 1.8 -- python scripts/breakeven_fidelity.py

**The substitution** (`extended/breakeven.py`): only the trades' walk -- Stage 2's entries walked by
`extended.walker` under each rule set (`stage2` = `STAGE2`, `stop_first`, `delay5`, `both`) -- in A3's cached walk's
place for P-14 (`atlas_a3.cached_walk`, nothing written) and in `atlas_a3.walk_minutes`' place for P-16's one walk
call (E-011's narrow substitution). Every other step is Stage 2's: the cells, the bounds (recomputed from the trades by
the design's own rule), the campaigns, U1's jobs, the gate.

**Identities first, refusing** (rule set `stage2`): P-14's re-walked A3 frame equals the cache's frame exactly; P-16's
re-walked cell has P-16's pinned content hash; each design's gate through this runner reproduces its registered
per-path rows (`zero_edge_decomposition.path_problems`, every `PATH_COLS` column, both shifts; the first `--paths`)
and, at 500 paths, its registered gate row's columns (`extended.breakeven.GATE_COLS`, to 1e-6 relative); with every
response off, the adapter's U1 start rows equal `user_journey.csv`'s (every column, both arms, the starts run). Then
every reading's checks (`extended.user_readings.consistency_problems`). Any failure: nothing written.

**The readings** (`results/breakeven_fidelity.csv`): section `identity`; `trades` (per design, rule set and R: the
trades, the share of each exit kind, the mean net R, the trades whose kind or gross moved from Stage 2's walk); `gate`
(per design, rule set and shift: `GATE_COLS`, beside the registered file's rows, rule set `registered`); `scorecard`,
`extra`, `path` (`extended.user_readings`, response `off`, both arms, all starts and the judged block). Gate seeds:
the registered campaigns' (P-14 20261131, P-16 20261206) -- common random numbers with the registered rows; the U1
replay draws nothing at 0 % (its path seeds are Q-17's). Variant count 6 (three corrections x two designs).

**The read (Q-58, E-037).** Before any of the engine's work `main` authorises it through
`extended.reader.authorise_engine_read`: purpose `registered_design`, declaration **E-024** (the row that merged Q-20),
the designs run (P-14, P-16), the window 2020-01-02 to 2026-07-16, the files -- A1's events and days, A3's cached walk
and the bars for either design (P-14's A3 frame is re-walked from the bars, `extended.breakeven.a3_frame`; P-16's cell
by `rc_width_screen.build`). A refusal ends the run (exit 3) before anything is read; ledgered only inside a clean run.
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
from extended import reader  # noqa: E402
from extended import user_beside as B  # noqa: E402
from extended import user_readings as R  # noqa: E402

SCRIPT = "scripts/breakeven_fidelity.py"
RESULT = "breakeven_fidelity"
TASK = "Q-20"
DESIGNS = ("p14", "p16")
#: Q-58: the registered designs' names, the row that admits their re-read (E-037), the Stage 2 tree the engine reads
DESIGN_IDS = {"p14": "P-14", "p16": "P-16"}
READ_ROW = "E-024"
VENDOR = ROOT / "vendor" / "stage2"
FULL_PATHS = 500
READING = ("EXPLORATORY (Q-20; E-012 (2), E-013 (2)): beside the registered rows, never deciding; R* stays P-14 unless "
           "the operator rules otherwise")


def main(argv: list[str] | None = None) -> int:
    import rc150_dev_test as P
    import rc_dev_test as D
    import user_journey as UJ

    from extended.results import read_result, write_result
    from propedge import RESULTS_DIR
    from propedge.reporting.results import sha256_of

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--starts", type=int, default=None, help="with --check: U1 starts a design and arm")
    ap.add_argument("--paths", type=int, default=FULL_PATHS, help="gate paths (500 for the readings)")
    ap.add_argument("--designs", default=None, help="with --check: p14, p16 or both")
    ap.add_argument("--workers", type=int, default=1)
    a = ap.parse_args(argv)
    if not a.check and (a.starts is not None or a.paths != FULL_PATHS or a.designs is not None):
        print("REFUSED (Q-20): the readings run every start and 500 gate paths of both designs; a smaller run is --check")
        return 2
    designs = DESIGNS if a.designs is None else tuple(x for x in a.designs.split(",") if x)
    if not designs or any(d not in DESIGNS for d in designs):
        print(f"REFUSED (Q-20): the designs are {', '.join(DESIGNS)}, not {', '.join(designs) or 'none'}")
        return 2
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
    timing: dict[str, float] = {}

    def ident(design: str, rules: str, check: str, problems: list[str]) -> bool:
        rows.append({"section": "identity", "design": design, "rules": rules, "measure": check, "stat": "holds",
                     "value": float(not problems), "note": "; ".join(problems[:4])})
        print(f"identity {'HOLDS' if not problems else 'FAILS'}: {design} {rules}: {check}"
              + (f" -- {'; '.join(problems[:6])}" if problems else ""), flush=True)
        return not problems

    def refuse() -> int:
        print("REFUSED (Q-20): nothing written", flush=True)
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
            df, bad = (BE.p14_gate if design == "p14" else BE.p16_gate)(b, a.paths, a.workers)
            mine = BE.gate_rows(df)
            if name == "stage2":
                if not ident(design, name, f"the gate's first {a.paths} paths equal the registered per-path rows "
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
                rows += [{**{k: v for k, v in r.items() if k not in ("response", "kind", "enforcement_p", "rtp",
                                                                       "rtp_warnings", "ftp_label")},
                          "rules": name} for r in srows if r["section"] != "response"]
                timing[f"{design}|{name}|{arm}"] = round(time.time() - t2, 1)
                del outs
            print(f"timing: {design} {name}: {time.time() - t0:.0f} s", flush=True)
            del b
            gc.collect()
        del X
        gc.collect()

    res = pd.DataFrame(rows)
    res.insert(1, "reading", READING)
    cols = ["section", "reading", "design", "rules", "arm", "shift", "rr", "block", "measure", "stat", "value", "n",
            "note"]
    res = res[[c for c in cols if c in res.columns] + [c for c in res.columns if c not in cols]]
    seconds = time.time() - t_all
    params = {"task": TASK, "decisions": ["E-012 (2)", "E-013 (2)"], "designs": list(designs),
              "rule_sets": {n: {"name": r.name, "breakeven_tie": r.breakeven_tie, "breakeven_delay": r.breakeven_delay}
                            for n, r in BE.RULE_SETS},
              "corrections": {"stop_first": "on a bar after the move that touches the entry and trades through the "
                                            "target, the stop first (Stage 2's walk books the target, "
                                            "fv3_rung_walk.py:184-185)",
                              "delay5": "the move decided on the session's open bar's open, in force from the first "
                                        "present bar opening five minutes after it (D-266); the original bracket "
                                        "governs until then"},
              "gate_paths": int(a.paths), "gate_seeds": {"p14": BE.P14_GATE_SEED, "p16": BE.P16_GATE_SEED},
              "gate_cols": list(BE.GATE_COLS), "u1_starts": "every start" if a.starts is None else int(a.starts),
              "u1_response": "off (0 % denial, the placement off, no Focused Trader model)",
              "u1_path_seeds": "Q-17's: lockstep.child_seed(20261920, 0, start_day); nothing drawn at 0 %",
              "bounds": "recomputed from each rule set's trades by the design's own rule (atlas_a3.bounds)",
              "references": {f: sha256_of(rd / f) for f in (BE.P14_GATE_FILE, BE.P16_GATE_FILE, I.SI.U1_FILE)},
              "timing": timing, "workers": int(a.workers), "seconds": round(seconds, 1)}
    desc = ("EXPLORATORY (Q-20): P-14's and P-16's trades re-walked with the breakeven move corrected -- the stop first "
            "on a bar touching the entry and trading through the target after the move, the move five minutes after "
            "the session open, each alone and both -- read beside the registered rows: the trades' exit kinds and net "
            "R, the gate row (500 paths at the registered seeds), and the user scorecard, E-007 (e)'s measures and the "
            "operator's path measures through Q-17's adapter (every start, both arms). Beside, never deciding.")

    def write(target: Path | None) -> list[str]:
        csv, man = write_result(res, RESULT, script=SCRIPT, seed=B.DENIAL_SEED, parameters=params, results_dir=target,
                                description=desc, exploratory=True, variant_count=3 * len(designs),
                                notes={"status": READING, "variant_count_rule": "three corrections a design; Stage 2's "
                                       "walk is the identity, not a variant", "selection": "none"})
        read_result(csv)
        return [csv.name, man.name]

    if a.check:
        with tempfile.TemporaryDirectory(prefix="breakeven_fidelity_check_") as td:
            wrote = write(Path(td))
        print(f"every identity holds; the pipeline ran on {list(designs)} ({a.paths} gate paths, "
              f"{'every' if a.starts is None else a.starts} start(s)) and wrote {wrote} ({len(res)} rows) to a "
              f"temporary folder, since removed; nothing written to results/, no reading printed (--check). "
              f"{seconds:.0f} s", flush=True)
    else:
        wrote = write(None)
        print(f"written: {wrote} ({len(res)} rows); {seconds:.0f} s", flush=True)
    mem = I.SI.peak_memory()
    if mem:
        print(mem, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
