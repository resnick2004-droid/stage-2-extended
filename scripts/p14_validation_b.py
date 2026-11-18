"""EXPLORATORY (TASK_QUEUE Q-18b; the lead's E-132, on the audit's caveats E-125 (1)-(5)): the parts of P-14's stress
checks `results/p14_validation.csv` lacks, as Stage 2 declared them -- read beside P-14's registered verdict and beside
that file; changes neither, selects nothing, creates no candidate. `scripts/p14_validation.py` is not touched: its file
stays reproducible byte for byte, and this run re-makes its engine rows and checks them against it, every cell.

    python scripts/p14_validation_b.py --check                 # 4 paths, a few starts: every identity and every
                                                               #   part's smoke; no reading printed, nothing written
    python scripts/p14_validation_b.py --check --part A2       # one part's smoke
    python scripts/run_clean.py --name p14-validation-b --task Q-18b --hours <h> --mem-gb <g> \
        -- python scripts/p14_validation_b.py                  # the run: results/p14_validation_b.csv (a clean checkout)

**The subject** is `scripts/p14_validation.py`'s, built by its own `build_p14` (P-14's registered gate,
`vendor/stage2/results/a3_brk30_cb20_gate.csv`, every identity of that script refusing first), through
`extended.p14_stress_b.Engine` -- the same engine call, its gate row's ruin, share-ever-paid, worst-bankroll and pattern
columns kept beside, each arm's per-path required bankroll kept for the ruin figures.

**The parts** (Stage 2's declarations; `extended/p14_stress_b.py`'s docstring states every reading):

* SLIPB -- D-583's readings the slippage part did not carry (E-125 caveat 1): its nine arms at D-583's own level (the
  0.05 bound by the era rule) beside P-14's verdict level (0.05/370, the existing reading, labelled as fixed in code
  and in no row), each arm's zero-edge twin, its share of accounts ever paid, D-509's four slice lines against FV3-C
  (the 0.05 verdict arm replayed from every start, P-14's registered slices' way and level) and D-212's resolution;
  D-583's reading per family and level: the lowest level with growth at the bound at or below zero and the highest at
  which all four slice lines hold.
* A2 -- D-663's real order of days against the resampled paths (E-125 caveat 3): every 21st session as a start over
  252 sessions, the independent draw and mean blocks 1, 5, 21, 63, 500 paths a scheme, the verdict and point arms
  (`extended.p14_stress_b.part_a2`, the vendored part with its seed an argument).
* RERUN -- A1, B2, C1 and SLIP re-run through the wider engine record (the vendored parts and
  `extended.v1_adapter`'s, unchanged), every re-made row checked against `results/p14_validation.csv`'s, every cell,
  refusing: the ruin figure beside every stressed growth (E-125 caveat 2, Stage 2 D-145 in D-312's form).
* Always: section `ruin` (every run, both arms: Stage 2's ruin figures beside its growth), section `assumptions`
  (E-125 caveat 4: 0 % denial, placement and the Focused Trader Program off, the assumed fills with only slippage
  stressed, the payout model, the purchase budget, the strict rule, the state table, the bankroll an output, the
  breakeven move -- each read from the engine call), section `provenance` (E-125 caveat 5).

**Identities first, refusing** (beyond `build_p14`'s): the registered call at 0.05/370 and at 0.05 reproduces the
registered file's rows exactly (`scripts/p14_validation.py`'s two engine identities) and its kept extra columns equal
the file's; the base arm's zero-edge twin reproduces the registered `zero_edge_twin` row exactly; the base arm's slices
reproduce the registered `slices` summary and its `slice_lines` (to 1e-9, `a3_brk30_cb20._slice_same`); the re-made
A1, B2, C1 and SLIP rows equal `results/p14_validation.csv`'s (its manifest verified first), and the runs re-made are
the runs `results/variants.jsonl` counted for it. In --check the engine identities read the per-path file's first 4
paths (the twin's too) and the file comparisons are skipped (not comparable at 4 paths).

**Seeds:** every engine run at P-14's campaign seed (Stage 2 D-512); each run's Monte-Carlo error and C1's
realisations at `scripts/p14_validation.py`'s seeds (its `SEED_MC`, `SEED_C1`; imported, so the same numbers);
A2's resampled paths at `SEED_A2` = 20261953, the next of the block Q-22's brief reserved for Q-18 (for anything
new; D-663's own A2 seed is its study's alone), fixed here before any run. The slices and the real-order replay draw
nothing.

**Counting.** Every engine run new to this file is a variant (`results/variants.jsonl`, `Q-18b:p14_validation_b`,
exploratory): the eight stressed arms at D-583's level, the eight stressed twins, and A2's ten resampled path sets
(Stage 2 D-665 counts those as engine runs). The re-made runs reproduce runs already counted under
`Q-18:p14_validation` and the base twin reproduces P-14's registered twin: none is counted again.

**Resume** (Stage 2 D-540's form): each finished run kept outside the checkout (`%LOCALAPPDATA%/stage2-extended-
resume/`), keyed by the commit and the paths; a sidecar manifest written beside it at the end (sha256, lines, commit).

**The read (Q-58, E-037):** as `scripts/p14_validation.py`'s -- purpose `registered_design`, the row that merged Q-18
(E-026), design P-14, the window 2020-01-02 to 2026-07-16, A1's events and days and A3's cached walk (no bars).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import use_vendored_stage2  # noqa: E402

VENDORED = use_vendored_stage2()

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from extended import p14_stress_b as Q  # noqa: E402
from extended import reader  # noqa: E402
from extended import v1_adapter as X  # noqa: E402

VS, V, ps16 = X.VS, X.V, X.ps16


def _p14_validation():
    """`scripts/p14_validation.py` as a module (its subject, its identities, its seeds), unchanged."""
    spec = importlib.util.spec_from_file_location("p14_validation", ROOT / "scripts" / "p14_validation.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


P = _p14_validation()

SCRIPT = "scripts/p14_validation_b.py"
TASK = "Q-18b"
READ_ROW = P.READ_ROW
RESULT = "p14_validation_b"
VARIANT_ID = f"{TASK}:{RESULT}"
OLD_RESULT = f"{P.RESULT}.csv"
OLD_VARIANT_ID = P.VARIANT_ID
SEED_A2 = 20261953
PARTS = ("SLIPB", "A2", "RERUN")              # the identities that need a part's own runs first; the long re-run last
RERUN_SECTIONS = ("a1", "b2_curve", "b2", "c1", "c1_summary", "slip", "slip_reading")
TWIN_SECTION = "zero_edge_twin"
CHECK_PATHS, CHECK_B2_STEPS, CHECK_A2_STARTS, CHECK_SLICE_STARTS = P.CHECK_PATHS, P.CHECK_B2_STEPS, 2, 3
RESUME_DIR = P.RESUME_DIR
READING = ("EXPLORATORY (Q-18b): the parts of P-14's stress checks results/p14_validation.csv lacks -- D-583's twin, "
           "share ever paid, slice lines and its own level; D-663's A2; a ruin figure beside every stressed growth; "
           "the standing assumptions -- beside P-14's registered verdict and that file, changes neither, selects nothing")


# ------------------------------------------------------------------------------------------------ provenance


def git_state(root: Path = ROOT) -> dict[str, Any]:
    """The commit this run is made from and whether the tree is clean (E-125 caveat 5: the log names its commit)."""
    def git(*a: str) -> str:
        return subprocess.run(["git", *a], cwd=root, capture_output=True, text=True).stdout.strip()

    return {"commit": git("rev-parse", "HEAD") or None, "dirty": bool(git("status", "--porcelain")),
            "branch": git("rev-parse", "--abbrev-ref", "HEAD") or None}


def provenance_line(state: dict[str, Any], argv: list[str]) -> str:
    return (f"provenance: commit {state['commit']} (dirty {state['dirty']}, {state['branch']}); command: python "
            f"{SCRIPT} {' '.join(argv)}; clean-run marker {os.environ.get('S2X_CLEAN_RUN')!r}; run id "
            f"{os.environ.get('S2X_RUN_ID')!r}; python {sys.version.split()[0]}")


# ------------------------------------------------------------------------------------------------ the parts' wiring


def part_of(label: str) -> str:
    """The part a run label belongs to (section `ruin`)."""
    for head, part in (("registered", "identity"), ("a1 ", "A1"), ("b2 ", "B2"), ("c1 ", "C1"), ("slip05 ", "SLIPB"),
                       ("slip ", "SLIP"), ("twin ", "SLIPB")):
        if label.startswith(head):
            return part
    return "other"


def reference_of(label: str) -> str:
    """The unstressed run a run's ruin figures are read against: the registered call at the same bound level."""
    if label.startswith("twin "):
        return "twin base"
    if label.startswith("slip05 ") or label == P.IDENTITY_LABELS[1]:
        return P.IDENTITY_LABELS[1]
    return P.IDENTITY_LABELS[0]


def new_runs(labels: list[str], a2_sets: list[str]) -> list[str]:
    """The engine runs new to this file (the variants): D-583's level and the stressed twins, A2's path sets."""
    return [x for x in labels if x.startswith("slip05 ") or (x.startswith("twin ") and x != "twin base")] + a2_sets


def remade_runs(labels: list[str]) -> list[str]:
    """The runs that re-make `results/p14_validation.csv`'s (its variants), in the order asked."""
    return [x for x in labels if part_of(x) in ("A1", "B2", "C1", "SLIP")]


def old_variant_runs(results_dir: Path) -> list[str]:
    """The runs `results/variants.jsonl` counted under `scripts/p14_validation.py`'s id."""
    p = Path(results_dir) / "variants.jsonl"
    out = []
    for line in p.read_text(encoding="utf-8").splitlines() if p.is_file() else []:
        if line.strip():
            r = json.loads(line)
            if r.get("prereg_id") == OLD_VARIANT_ID:
                out.append(str((r.get("params") or {}).get("run")))
    return out


def twin_problems(res: dict[str, dict], ref: pd.Series) -> list[str]:
    """The base arm's zero-edge twin (point arm) against P-14's registered `zero_edge_twin` row, exactly."""
    out = []
    for c in VS.IDENT_COLS + Q.EXTRA:
        if c not in ref.index or pd.isna(ref[c]):
            if c in VS.IDENT_COLS:
                out.append(f"{c}: not on the registered row")
            continue
        a, b = res["point"].get(c), float(ref[c])
        if a is None or not (float(a) == b or (np.isnan(float(a)) and np.isnan(b))):
            out.append(f"point {c}: {a!r} against the registered {b!r}")
    return out


def make_slices(sub: VS.Subject, reg_file: pd.DataFrame, resume: VS.Resume, workers: int, declared: bool,
                idents: list[dict]):
    """The slices function `part_slip_b` takes: an arm's verdict arm at the 0.05 bound replayed from every start
    (`customer_slices`' machinery, as `a3_brk30_cb20.run_slices` read P-14's), summarised, its four lines against
    FV3-C's frozen summary in P-14's registered file; the base arm's checked against P-14's registered slices first."""
    import a3_brk30 as B
    import a3_brk30_cb20 as C
    import customer_slices as cs

    fv3c = Q.summary_frame(reg_file[reg_file["section"].astype(str) == "slices"], C.REFERENCE_SLICE)
    reg_cand = Q.summary_frame(reg_file[reg_file["section"].astype(str) == "slices"], C.CANDIDATE_SLICE)
    reg_lines = reg_file[reg_file["section"].astype(str) == "slice_lines"]
    plan = sub.kw["risk_policy"]

    def slices(name: str, blocks: list, e_by: dict, lb05: dict):
        cfg = C.CANDIDATE_SLICE if name == "base" else f"{C.CANDIDATE_SLICE} {name}"
        camp = Q.slice_campaign(sub, cfg, blocks, e_by, lb05, seed=int(B.SEED), strict_gap=float(B.STRICT_GAP))
        blk = cs.arm_blocks(camp, "verdict")
        args = cs.engine_args(camp.kw, "verdict", camp.blocks, risk_policy=plan, purchase_budget=C.BUDGET)
        items = cs.slice_items(len(blk), C.HORIZONS)
        if not declared:
            items = [x for x in items if x[0] < CHECK_SLICE_STARTS]

        def make():
            return [{k: VS._plain(v) for k, v in r.items()}
                    for r in cs.run_slices([(cfg, "verdict", blk, camp.dates, args, items)], workers)]

        sl = pd.DataFrame(VS._cached(resume, f"{sub.name} slices {name} {len(items)}", make),
                          columns=list(cs.SLICE_COLS))
        summ = cs.summarise(sl)
        lines, hold = Q.slice_lines_of(summ, fv3c, cfg, C.slice_lines)
        if name == "base":
            if declared:
                bad = (Q.summary_problems(summ, reg_cand, cs.SUMMARY_COLS, C._slice_same)
                       + Q.lines_problems(lines, reg_lines, C._slice_same))
                if bad:
                    raise Q.refused("the base arm's slices are not P-14's registered slices -- " + "; ".join(bad[:8]))
                how = (f"the base arm's verdict arm at the 0.05 bound, replayed from every start at {list(C.HORIZONS)} "
                       f"sessions, reproduces results/{P.P14_GATE}'s slices summary ({C.CANDIDATE_SLICE}, every "
                       f"summary column) and its four slice_lines rows to {C.TOL:g}")
                print(f"identity HOLDS: {how}", flush=True)
            else:
                how = f"not comparable on {CHECK_SLICE_STARTS} starts a horizon (--check)"
                print(f"identity skipped: the base arm's slices -- {how}", flush=True)
            idents.append({"section": "identity", "subject": sub.name, "holds": declared, "check": how})
        return summ, lines, hold

    return slices


def twin_identity(eng: Q.Engine, reg_file: pd.DataFrame, declared: bool) -> dict:
    """The base arm's zero-edge twin first (refusing): the registered `zero_edge_twin` row exactly, or in --check the
    registered per-path file's first paths."""
    import zero_edge_decomposition as zd

    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result

    sub = eng.sub
    zb, ze, zl = Q.zero_twin(list(sub.blocks), sub.e_by, sub.frr)
    res = eng.run("twin base", blocks=zb, e_by=ze, lb_by=zl)
    if declared:
        z = reg_file[(reg_file["section"].astype(str) == TWIN_SECTION) & (reg_file["shift"].astype(str) == "point")
                     & np.isclose(reg_file["enforcement_p"].astype(float), 0.0)]
        if len(z) != 1:
            raise Q.refused(f"{P.P14_GATE} holds {len(z)} {TWIN_SECTION} point rows at 0 %.")
        bad = twin_problems(res, z.iloc[0])
        how = (f"the base arm's zero-edge twin at {eng.n_paths} paths and seed {sub.seed} reproduces results/"
               f"{P.P14_GATE}'s {TWIN_SECTION} point row on {', '.join(VS.IDENT_COLS)} and the kept extra columns "
               f"exactly")
    else:
        bad = zd.path_problems(eng.sink, read_result(RESULTS_DIR / P.P14_PATHS),
                               [(f"{sub.name} twin base", "point", TWIN_SECTION, "point")], eng.n_paths)
        how = f"the base arm's zero-edge twin's first {eng.n_paths} paths equal results/{P.P14_PATHS}'s {TWIN_SECTION}"
    if bad:
        raise Q.refused("the base arm's zero-edge twin is not P-14's registered twin -- " + "; ".join(bad[:8]))
    print(f"identity HOLDS: {how}", flush=True)
    return {"section": "identity", "subject": sub.name, "holds": True, "check": how}


def assumptions(sub: VS.Subject) -> list[dict]:
    """E-125 caveat 4's rows: `extended.p14_stress_b.assumption_rows` with what the engine call does not carry --
    the payout method `gate.run_gate` hands the campaign clock (aeropay; `customer_slices.engine_args` reads the same)
    and its lag from the verified ledger, the fill model's active profile, D-583's base ticks by exit kind."""
    import atlas_a3 as A
    import yaml

    from propedge.campaign.payout_method import AEROPAY, payout_method_terms
    from propedge.contract.rules import load_rules
    from propedge.research.fv3_rung_walk import EXIT_TICKS

    lag = int(payout_method_terms(AEROPAY, ledger=load_rules()).lag_days)
    fills = yaml.safe_load((VENDORED / "config" / "fills.yaml").read_text(encoding="utf-8"))
    profile = (fills.get("meta") or {}).get("active_profile")
    kinds = {"s": "stop", "t": "target", "f": "flatten", "b": "breakeven"}
    base_ticks = {"entry": int(ps16.BASE["entry"]),
                  **{kinds[str(A.KIND_CODE[int(k)])]: int(v) for k, v in EXIT_TICKS.items()}}
    return Q.assumption_rows(sub, payout_lag_days=lag, payout_method=AEROPAY, fills_profile=profile,
                             base_ticks=base_ticks, plan_id=sub.extra.get("plan"))


# ------------------------------------------------------------------------------------------------ writing


def write_reading(rows: list[dict], params: dict, runs: list[str], results_dir: Path | None, seed: int) -> Path:
    from extended.results import RESULTS_DIR as OWN, write_result
    from propedge.backtest.harness import VariantCounter

    target = Path(results_dir) if results_dir is not None else OWN
    counter = VariantCounter(path=target / "variants.jsonl")
    for label in runs:
        counter.record(prereg_id=VARIANT_ID, seed=int(seed), exploratory=True,
                       params={"study": "Q-18b: the parts of P-14's stress checks results/p14_validation.csv lacks",
                               "subject": "P14", "run": label, "paths": params["paths"],
                               "campaign_seed": int(seed), "mc_seed": params["seeds"]["mc_error"],
                               **({"a2_seed": SEED_A2} if label.startswith("a2 ") else {})},
                       label=f"{VARIANT_ID}: P14 {label}")
    out = pd.DataFrame([{k: v for k, v in r.items() if k != Q.REQUIRED} for r in rows])
    out.insert(1, "reading", READING)
    csv, _ = write_result(out, RESULT, script=SCRIPT, seed=int(seed), parameters=params, results_dir=target,
                          exploratory=True, variant_count=len(runs),
                          notes={"status": READING, "selection": "none: beside P-14's registered verdict and "
                                                                 "results/p14_validation.csv",
                                 "readings": "scripts/p14_validation_b.py's and extended/p14_stress_b.py's docstrings"},
                          description="EXPLORATORY (Q-18b): D-583's zero-edge twin, share ever paid, slice lines and "
                                      "own bound level on P-14's slippage arms; D-663's A2; Stage 2's ruin figures "
                                      "beside every stressed growth; the standing assumptions -- beside P-14's verdict "
                                      "and results/p14_validation.csv, changing neither.")
    print(f"written: {csv.name} ({len(rows)} rows)", flush=True)
    return csv


def params_of(sub: VS.Subject, n_paths: int, parts: list[str], workers: int, secs: dict[str, float], eng: Q.Engine,
              resumed: int, state: dict, resume_file: dict | None) -> dict[str, Any]:
    return {"task": TASK, "subject": sub.describe, "registered_file": P.P14_GATE, "beside_file": OLD_RESULT,
            "arms": dict(sub.arm_names), "paths": int(n_paths), "horizon_days": int(sub.kw["horizon_days"]),
            "campaign_seed": int(sub.seed), "ledger_n": int(sub.n_led), "era_flagged": bool(sub.extra["flagged"]),
            "seeds": {"campaign": int(sub.seed), "mc_error": int(P.SEED_MC), "C1": int(P.SEED_C1), "A2": SEED_A2},
            "seed_forms": {"A2": "lockstep.path_seeds(SEED_A2, 500) for every scheme and arm (v1_validation.part_a2's "
                                 "form, its root seed replaced)",
                           "mc_error": "np.random.default_rng(SEED_MC) for every run (scripts/p14_validation.py's)",
                           "C1": "extended.v1_adapter.c1_seed from SEED_C1 (scripts/p14_validation.py's)"},
            "parts": parts, "bound_levels": {Q.LEVEL_VERDICT: f"0.05/{sub.n_led} by the era rule (P-14's verdict "
                                                              "level; scripts/p14_validation.py's, in no row)",
                                             Q.LEVEL_D583: "0.05 by the era rule (Stage 2 D-583's)"},
            "slices": {"level": "0.05 by the era rule (P-14's registered slices', D-583's)", "horizons": [21, 63, 126],
                       "line_horizon": 63, "seed": "a3_brk30.SEED (P-13's; the replay draws nothing)",
                       "fv3c": f"results/{P.P14_GATE}'s slices rows for fv3c (FV3-C as frozen)"},
            "a2": {"horizon": V.A2_HORIZON, "step": V.A2_STEP, "paths": V.A2_PATHS, "mean_blocks": list(V.MEAN_BLOCKS)},
            "extra_columns": list(Q.EXTRA), "ruin_form": Q.RUIN_FORM,
            "not_done": ["D-518's journey beside the slices (D-583 does not read it)", "V1's B3 (a family's false "
                         "pass; not applicable to one registered cell)", "latency (declared for neither P-14 nor D-583)"],
            "declarations": {"D-663": V.DECLARATION_SHA256, "D-583": ps16.DECLARATION_SHA256},
            "provenance": state, "resume_file": resume_file, "workers": int(workers),
            "seconds": {k: round(x, 1) for k, x in secs.items()}, "engine_seconds": [round(x, 1) for x in eng.seconds],
            "resumed_runs": int(resumed), "vendored": "vendor/stage2 (E-002), imported, never edited"}


# ------------------------------------------------------------------------------------------------ main


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="a smoke at 4 paths and a few starts; no reading printed; "
                                                         "nothing written")
    ap.add_argument("--part", default="all", help=f"{' '.join(PARTS)}, or all (the declared order)")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--no-resume", action="store_true", help="the declared run without its resume file")
    a = ap.parse_args(argv)
    part = a.part.upper()
    parts = list(PARTS) if part == "ALL" else [part]
    if any(p not in PARTS for p in parts):
        print(f"REFUSED ({TASK}): --part is one of {PARTS} or all.")
        return 2
    if not 1 <= int(a.workers) <= 2:
        print(f"REFUSED ({TASK}): at most 2 workers (CLAUDE.md).")
        return 2
    declared = not a.check
    if declared:
        if part != "ALL":
            print(f"REFUSED ({TASK}): the run reads every part; one part is --check.")
            return 2
        from extended.results import clean_run_problem

        why = clean_run_problem()
        if why:
            print(f"REFUSED ({TASK}): results/{RESULT}.csv is written only from a clean checkout -- {why}. "
                  f"python scripts/run_clean.py --name p14-validation-b --task {TASK} --hours <h> --mem-gb <g> -- "
                  f"python {SCRIPT}")
            return 2
    state = git_state()
    print(provenance_line(state, argv), flush=True)
    if str(ROOT / "identity") not in sys.path:
        sys.path.append(str(ROOT / "identity"))
    import stage2_identity as SI

    try:
        reader.authorise_engine_read(
            reader.CHOICE_START, reader.JUDGED_END, purpose=reader.REGISTERED_DESIGN, declaration=READ_ROW,
            design=["P-14"], files=SI.engine_files(P.VENDOR, bars=False),
            what=f"{READ_ROW}'s readings ({SCRIPT}, {TASK}): the parts of P-14's stress checks "
                 f"results/{OLD_RESULT} lacks, parts {', '.join(parts)}" + (" (--check)" if a.check else ""))
    except (reader.ReadRefused, FileNotFoundError) as exc:
        print(SI.refusal(exc), flush=True)
        return 3
    import a3_brk30 as B

    from extended.results import RESULTS_DIR as OWN, verify_result
    from propedge import RESULTS_DIR

    t_all = time.time()
    n_paths = V.N_PATHS if declared else CHECK_PATHS
    old = None
    if declared:
        ok, why = verify_result(OWN / OLD_RESULT)
        if not ok:
            print(f"REFUSED ({TASK}): results/{OLD_RESULT} does not match its manifest -- {why}")
            return 3
        old = Q.read_file(OWN / OLD_RESULT)
    t0 = time.time()
    sub, idents = P.build_p14()
    reg_file = B._exact(RESULTS_DIR / P.P14_GATE)
    print(f"P14 built: {len(sub.days)} sessions, {len(sub.t)} offered trades ({time.time() - t0:.0f} s)", flush=True)
    resume = VS.Resume(None, "check")
    if declared and not a.no_resume:
        resume = VS.Resume(RESUME_DIR, f"p14b_{(state['commit'] or 'nocommit')[:12]}_{n_paths}")
    resumed = len(resume.rows)
    eng = Q.Engine(sub, n_paths, a.workers, resume, mc_seed=P.SEED_MC, keep_sink=not declared)
    reg, ident = VS.registered_run(eng, declared)
    idents.append({**ident, "subject": sub.name})
    idents.append(P.gate05_identity(eng, declared))
    reg05 = eng.results[P.IDENTITY_LABELS[1]]
    if declared:
        bad = (Q.registered_extra_problems(reg, P.p14_rows(reg_file, "gate_at_ledger_n"))
               + Q.registered_extra_problems(reg05, P.p14_rows(reg_file, "gate")))
        if bad:
            print(f"REFUSED ({TASK}): the kept extra columns are not the registered file's -- " + "; ".join(bad[:8]))
            return 3
        how = (f"the registered calls' kept extra columns ({', '.join(Q.EXTRA)}) equal results/{P.P14_GATE}'s "
               "gate_at_ledger_n and gate rows exactly (each column the file holds)")
        print(f"identity HOLDS: {how}", flush=True)
        idents.append({"section": "identity", "subject": sub.name, "holds": True, "check": how})
    rows: list[dict] = []
    secs: dict[str, float] = {}
    a2_sets: list[str] = []
    refs: dict[str, str] = {}
    for p in parts:
        t1 = time.time()
        if p == "SLIPB":
            idents.append(twin_identity(eng, reg_file, declared))
            slices = make_slices(sub, reg_file, resume, a.workers, declared, idents)
            got, srows, r2 = Q.part_slip_b(eng, reg, reg05, Q.rebound_both(sub), slices,
                                           lambda tt: B.resolution_rows(tt, sub.keys))
            rows += got + srows + Q.slip_readings(got, sub.arm_names)
            refs.update(r2)
        elif p == "A2":
            got = Q.part_a2(sub, None if declared else CHECK_A2_STARTS, V.A2_PATHS if declared else 2 * CHECK_PATHS,
                            resume, seed=SEED_A2)
            rows += [{**r, "a2_seed": SEED_A2} for r in got]
            a2_sets = Q.a2_path_sets(got)
        elif p == "RERUN":
            remade = VS.part_a1(eng, reg)
            remade += VS.part_b2(eng, reg, V.B2_MAX_STEPS if declared else CHECK_B2_STEPS)
            remade += X.part_c1(eng, reg, seed=P.SEED_C1)
            remade += X.part_slip(eng, reg, P.rebound_fn(sub))
            if declared:
                bad = Q.file_problems(remade, old, RERUN_SECTIONS)
                want = old_variant_runs(OWN)
                got_runs = remade_runs(eng.labels)
                if sorted(got_runs) != sorted(want):
                    bad.append(f"the re-made runs {len(got_runs)} are not the {len(want)} the ledger counted under "
                               f"{OLD_VARIANT_ID}")
                if bad:
                    print(f"REFUSED ({TASK}): the re-made rows are not results/{OLD_RESULT}'s -- " + "; ".join(bad[:8]))
                    return 3
                how = (f"the re-made sections {', '.join(RERUN_SECTIONS)} equal results/{OLD_RESULT}'s, row for row "
                       f"and every cell they carry (blanks as missing, numbers to the last digit), and the "
                       f"{len(got_runs)} runs re-made are the ones results/variants.jsonl counted under {OLD_VARIANT_ID}")
                print(f"identity HOLDS: {how}", flush=True)
                idents.append({"section": "identity", "subject": sub.name, "holds": True, "check": how})
        secs[p] = time.time() - t1
        print(f"part {p}: {secs[p]:.0f} s", flush=True)
    labels = [P.IDENTITY_LABELS[0]] + [x for x in eng.results if x != P.IDENTITY_LABELS[0]]
    results = {x: eng.results[x] for x in labels}
    ruin = Q.ruin_rows(results, {x: refs.get(x, reference_of(x)) for x in results}, sub.arm_names, part_of, sub.name)
    runs = new_runs(eng.labels, a2_sets)
    if a.check:
        print(f"--check done: parts {parts}; {len(rows) + len(ruin)} rows built, none printed, nothing written; "
              f"{len(runs)} new engine runs and path sets at {n_paths} paths; engine seconds "
              f"{[round(x, 1) for x in eng.seconds]}; {time.time() - t_all:.0f} s", flush=True)
    else:
        resume_file = None
        if resume.path is not None and resume.path.is_file():
            m = Q.file_manifest(resume.path, script=SCRIPT, task=TASK, commit=state["commit"], paths=n_paths,
                                runs=len(resume.rows), what="each finished run's rows, read back by a resumed run "
                                                            "(Stage 2 D-540's form)")
            resume_file = json.loads(m.read_text(encoding="utf-8"))
        prov = [{"section": "provenance", "subject": sub.name, "check": c} for c in (
            f"the log's first line names the commit ({state['commit']}), the tree's state and the command "
            "(E-125 caveat 5: results/p14_validation.csv's log named none; its commit is in its manifest)",
            "the resume file's sidecar manifest (sha256, lines, commit) is written beside it and copied into this "
            "manifest's parameters.resume_file",
            f"results/{OLD_RESULT}'s slip base rows leave era_flagged blank: the base arm's flag is P-14's registered "
            f"one, {bool(sub.extra['flagged'])} (a3_brk30.bounds_at_n, checked against results/{P.P14_GATE}'s "
            "verdict row by build_p14); this file's slip_b base rows carry it",
            "every variant line of this run records its campaign, Monte-Carlo and (A2) path seeds")]
        head = [{"section": "declaration", "subject": sub.name, "holds": True,
                 "check": f"the readings Stage 2 D-583 and D-663 declared and results/{OLD_RESULT} lacks (E-125 "
                          f"caveats 1-5), read on P-14 under TASK_QUEUE {TASK} (E-132); seed {SEED_A2} fixed in "
                          f"{SCRIPT} before the run"}]
        not_done = [{"section": "not_done", "subject": sub.name,
                     "note": "D-518's journey beside the slices (D-583 reads the slice lines only); V1's B3 (a "
                             "family's familywise false pass: not applicable to one registered cell); latency "
                             "(declared for neither P-14 nor D-583); not run"}]
        write_reading(head + idents + prov + assumptions(sub) + rows + ruin + not_done,
                      params_of(sub, n_paths, parts, a.workers, secs, eng, resumed, state, resume_file), runs, None,
                      sub.seed)
        print(f"done: {len(runs)} new engine runs and path sets ({resumed} runs read back from the resume file); "
              f"{time.time() - t_all:.0f} s", flush=True)
    mem = X.peak_memory()
    if mem:
        print(mem, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
