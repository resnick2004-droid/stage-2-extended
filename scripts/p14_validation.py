"""EXPLORATORY (TASK_QUEUE Q-18; E-007 (f)): Stage 2 D-663's validation readings on P-14 (A3-BRK30-CB20, Stage 2
D-509/D-513), the row to beat, which never had them -- read beside P-14's registered verdict; changes it not, selects
nothing, creates no candidate.

    python scripts/p14_validation.py --check                  # 4 paths, small replicates: every identity, every
                                                              #   part's smoke; no reading printed, nothing written
    python scripts/p14_validation.py --check --part B1        # one part's smoke
    python scripts/run_clean.py --name p14-validation --task Q-18 --hours <h> --mem-gb <g> \
        -- python scripts/p14_validation.py                   # the run: results/p14_validation.csv (a clean checkout)

**The subject** is P-14's registered gate (`vendor/stage2/results/a3_brk30_cb20_gate.csv`): A3-BRK30's trades
(`a3_brk30.cell_trades`) through P-14's engine call exactly as `a3_brk30_cb20._registered_run` makes it --
`atlas_a3.gate_kwargs` with the no-closure table (`rc_screen.inputs`), 20 purchases and resets in 21 trading days,
the strict rule at 5 minutes, the day capacity at the busiest day, the placement off, 0 % denial, 500 paths, the
registered horizon and P-14's campaign seed 20261131 (`a3_brk30_cb20.SEED`, Stage 2 D-512). P-14 PASSED at 0.05/N
with N = 370, the bounds the lower era's (the eras flagged), so -- as V1 read P-16 (S1) -- its two arms are the verdict
arm (every R at its bound at one-sided 0.05/370 by the era rule, `a3_brk30.bounds_at_n`; the file's
`gate_at_ledger_n` row) and the point arm (the file's `gate` point row), both from one call.

**Identity first, refusing** (before any reading): the vendored V1 build is D-663's and the slippage arms D-583's
(their declarations' sha256 and words); P-14's constants; the no-closure table's fresh decisions v12's; P-14's trades
and bounds against its registered file (the verdict row's trades, days, busiest day, capacity, N and era flag; every
R's e, pooled bound, count, blocks, sd, bound at N and gate bounds at 0.05 and 0.05/N; every R's resolution row);
D-583's base ticks the walk's; and the engine -- the registered call with every stress off reproduces the file's
`gate_at_ledger_n` (bound) and `gate` (point) rows on `v1_validation.IDENT_COLS` exactly at 500 paths, and the same
call at the 0.05 bound its `gate` bound and point rows (in --check: the first 4 paths of
`a3_brk30_cb20_gate_paths.csv`'s runs, every PATH_COLS column).

**The readings** (Stage 2 RESEARCH_PROTOCOL step 7 from D-663; the vendored parts unless named):
A1 -- the gate row with each path's days block-resampled (`gate.run_gate(mean_block=)`, the stationary bootstrap) at
mean block 1 (the control), 5, 21 and 63 sessions, the required bankroll's p50, p90 and p99 under each (`part_a1`);
B2 -- the break-even e and its margin: the verdict arm's outcomes shifted below the registered bound in steps of 0.02 R,
at most 8, under the independent draw and at mean block 21, the table frozen (`part_b2`); A0 -- the day series'
dependence and its automatic block (`part_a0`); B1 -- the bound's coverage at 0.05 and at its registered level
0.05/370 on 200,000 stationary-bootstrap histories at mean block 1, 5, 21 and A0's, by the registered era rule and the
pooled rule beside (`extended.v1_adapter.part_b1`); C1 -- offered trades dropped with p 0.10 and 0.25 and whole
sessions missed with p 0.10, three seeded realisations each (`extended.v1_adapter.part_c1`); SLIP -- Stage 2 D-583's
slippage families, (A) stop slip 2, 3, 5, 8, 12 ticks and (B) entry = stop slip 2, 3, 5 (`extended.v1_adapter.
part_slip`), e and the bound re-read at 0.05/370 by the era rule on the stressed trades, the table frozen.
**Not done:** V1's A2 (the real-order replay against resampled paths) and B3 (a family's false pass) -- not in Q-18.

**Seeds** (the brief's range, fixed here before any run): B1's histories `SEED_B1` = 20261950, C1's realisations
`SEED_C1` = 20261951, each run's Monte-Carlo error `SEED_MC` = 20261952; every engine run at P-14's registered
campaign seed 20261131 (Stage 2's, as V1 ran each subject at its own). The slippage draws nothing.

**Resume** (Stage 2 D-540's form, V1's): each finished engine run kept outside the checkout
(`%LOCALAPPDATA%/stage2-extended-resume/`), keyed by the commit and the paths; off in --check; the manifest records how
many runs were read back. Every engine run beyond the two reproductions is a variant (`results/variants.jsonl`,
`Q-18:p14_validation`, exploratory) and the manifest's `variant_count`.

Writes `results/p14_validation.csv` (EXPLORATORY) with its manifest, only from a clean checkout (`scripts/run_clean.py`;
refused at the start otherwise), workers 1 by default.

**The read (Q-58, E-037).** Before P-14 is built `main` authorises the engine's read through
`extended.reader.authorise_engine_read`: purpose `registered_design`, declaration **E-026** (the row that merged Q-18),
design P-14, the window 2020-01-02 to 2026-07-16, the files P-14's inputs open -- A1's events and days and A3's cached
walk (`rc_screen.inputs`; no walk is made afresh, so not the bars). A refusal ends the run (exit 3) before anything is
read; ledgered only inside a clean run, `--check` or not.
"""
from __future__ import annotations

import argparse
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

from extended import reader  # noqa: E402
from extended import v1_adapter as X  # noqa: E402

VS, V, ps16 = X.VS, X.V, X.ps16

SCRIPT = "scripts/p14_validation.py"
TASK = "Q-18"
#: Q-58: the row that admits P-14's re-read (E-037) and the Stage 2 tree the engine reads
READ_ROW = "E-026"
VENDOR = ROOT / "vendor" / "stage2"
RESULT = "p14_validation"
VARIANT_ID = f"{TASK}:{RESULT}"
P14_GATE, P14_PATHS = "a3_brk30_cb20_gate.csv", "a3_brk30_cb20_gate_paths.csv"
P14_LEDGER_N = 370                         # the registered N (the file's verdict row and manifest; checked)
P14_CAMPAIGN_SEED = 20261131               # a3_brk30_cb20.SEED (Stage 2 D-512; checked)
SEED_B1, SEED_C1, SEED_MC = 20261950, 20261951, 20261952
PARTS = ("A1", "B2", "A0", "B1", "C1", "SLIP")   # V1's order: the decisive rows first
IDENTITY_LABELS = ("registered", "registered at 0.05")
CHECK_PATHS, CHECK_REPS, CHECK_VERIFY, CHECK_B2_STEPS = 4, 2000, 2, 2
RESUME_DIR = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "stage2-extended-resume"
READING = ("EXPLORATORY (Q-18): Stage 2 D-663's validation readings on P-14 (A3-BRK30-CB20) -- block-resampled days, the "
           "bound's coverage, the break-even e, missed trades and sessions, D-583's slippage; beside P-14's registered "
           "verdict, changes none, selects nothing")


# ------------------------------------------------------------------------------------------------ the registered rows


def _zero(d: pd.DataFrame) -> pd.Series:
    return pd.Series(np.isclose(d["enforcement_p"].astype(float), 0.0), index=d.index)


def p14_rows(d: pd.DataFrame, bound_section: str) -> dict[str, pd.Series]:
    """{'bound': the `bound_section` section's lower_bound row at 0 %, 'point': the `gate` section's point row at 0 %}
    of P-14's registered file -- exactly one each, refusing otherwise."""
    sec, sh, z = d["section"].astype(str), d["shift"].astype(str), _zero(d)
    b = d[(sec == bound_section) & (sh == "lower_bound") & z]
    p = d[(sec == "gate") & (sh == "point") & z]
    if len(b) != 1 or len(p) != 1:
        raise X.refused(f"{P14_GATE} holds {len(b)} {bound_section} bound rows and {len(p)} gate point rows at 0 %.")
    return {"bound": b.iloc[0], "point": p.iloc[0]}


# ------------------------------------------------------------------------------------------------ the subject


def build_p14() -> tuple[VS.Subject, list[dict]]:
    """P-14's registered campaign as a V1 `Subject`, and the build's identity rows (each refusing)."""
    import a3_brk30 as B
    import a3_brk30_cb20 as C
    import atlas_a3 as A
    import fv3d_lever_test as lt
    import portfolio_stage as ps
    import rc_screen as S
    import score_fv3_grid as gf

    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_manifest
    from propedge.research.fv3_rung_walk import EXIT_TICKS

    idents: list[dict] = []

    def ident(check: str, bad: list[str]) -> None:
        if bad:
            raise X.refused(f"{check} -- " + "; ".join(bad[:8]))
        idents.append({"section": "identity", "subject": "P14", "holds": True, "check": check})
        print(f"identity HOLDS: {check}", flush=True)

    ident("the vendored V1 build is Stage 2 D-663's (v1_validation.declaration_problems: the row's sha256, every "
          "constant's words)", V.declaration_problems(V.declaration(VENDORED), declared=True))
    ident("the vendored slippage arms are Stage 2 D-583's (p16_slip_stress.declaration_problems)",
          ps16.declaration_problems(ps16.declaration(VENDORED / "DECISIONS.md")))
    ident(f"P-14's constants: campaign seed {P14_CAMPAIGN_SEED}, budget (20, 21), strict rule 5 minutes "
          "(a3_brk30_cb20; rc_screen.inputs checks the same)",
          [] if (int(C.SEED) == P14_CAMPAIGN_SEED and tuple(C.BUDGET) == (20, 21) and float(C.STRICT_GAP) == 5.0)
          else [f"seed {C.SEED}, budget {C.BUDGET}, strict {C.STRICT_GAP}"])
    I = S.inputs()
    L = I["L"]
    cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
    nc = I["plan"]
    ident("the no-closure table's fresh decisions are v12's (a3_brk30_cb20.fresh_problems; P-13's stop distribution, "
          "not vendored, not read)", C.fresh_problems(nc, B.policy(L)))
    t, days = B.cell_trades(L)
    keys = [float(R) for R in B.rrs(t)]
    path = RESULTS_DIR / P14_GATE
    reg = B._exact(path)                                  # its manifest verified, every float to its last digit
    man = read_manifest(path)
    v = reg[reg["section"].astype(str) == "verdict"]
    bad: list[str] = []
    if len(v) != 1:
        raise X.refused(f"{P14_GATE} holds {len(v)} verdict rows.")
    v = v.iloc[0]
    n_led = int(float(v["ledger_n"]))
    if n_led != P14_LEDGER_N or int(man.parameters["ledger_n"]) != P14_LEDGER_N:
        bad.append(f"N {n_led} (verdict row), {man.parameters['ledger_n']} (manifest), not {P14_LEDGER_N}")
    st, e_by, lb05_by, lbn_by, _, flagged = B.bounds_at_n(t, days, cfg, n_led)
    for k, mine in (("trades", len(t)), ("days", len(days)), ("busiest_day", B.busiest(t)),
                    ("trades_per_day_capacity", B.capacity(t, fcfg)), ("era_flagged", bool(flagged))):
        if not B._same(mine, v[k]):
            bad.append(f"{k}: {mine!r} against the verdict row's {v[k]!r}")
    er = reg[reg["section"].astype(str) == "edge"].copy()
    er["rr"] = er["rr"].astype(float)
    er = er.set_index("rr")
    if sorted(er.index) != sorted(keys):
        bad.append(f"edge rows at R {sorted(er.index)} against the trades' {keys}")
    else:
        for R in keys:
            mine = {"e": st[R]["e"], "lb": st[R]["lb"], "n": st[R]["n"], "blocks": st[R]["blocks"], "sd": st[R]["sd"],
                    "lb_at_ledger_n": st[R]["lb_at_n"], "lb_gate": lb05_by[R], "lb_gate_at_ledger_n": lbn_by[R]}
            bad += [f"R {R:g} {k}: {x!r} against {er.loc[R, k]!r}" for k, x in mine.items()
                    if not B._same(x, er.loc[R, k])]
    rs = reg[reg["section"].astype(str) == "resolution"].copy()
    rs["rr"] = rs["rr"].astype(float)
    rs = rs.set_index("rr")
    mine_rows = B.resolution_rows(t, keys)
    if sorted(rs.index) != sorted(float(r["rr"]) for r in mine_rows):
        bad.append("the resolution rows' R differ")
    else:
        bad += [f"resolution R {r['rr']:g} {k}: {r[k]!r} against {rs.loc[float(r['rr']), k]!r}" for r in mine_rows
                for k in ("offered", "unresolved", "unresolved_worst_year", "resolves")
                if not B._same(r[k], rs.loc[float(r["rr"]), k])]
    ident(f"P-14's trades and bounds are results/{P14_GATE}'s: the verdict row's trades, days, busiest day, capacity, "
          f"N = {P14_LEDGER_N} (and the manifest's) and era flag; every R's e, pooled bound, count, blocks, sd, bound at "
          "N and gate bounds at 0.05 and 0.05/N (a3_brk30.bounds_at_n); every R's resolution row", bad)
    ident("D-583's base ticks are the walk's (p16_slip_stress.base_problems: fv3_rung_walk.EXIT_TICKS by "
          "atlas_a3.KIND_CODE, the config's entry slip)",
          ps16.base_problems(EXIT_TICKS, A.KIND_CODE, float(cfg["slip_ticks"])))
    blocks, n_used = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise X.refused("the blocks hold a different number of trades.")
    horizon = int(fcfg["gate"]["campaign"]["horizon_days"])
    # a3_brk30_cb20's go("gate_at_ledger_n", blocks, e_by, lbn_by): its engine call, the bound at 0.05/N
    kw = A.gate_kwargs(blocks, fcfg, tv, nc, e_by, lbn_by, None, seed=int(C.SEED), n_paths=V.N_PATHS, horizon=horizon,
                       capacity=B.capacity(t, fcfg), levels=(0.0,), rtp=False, one_at_a_time=C.STRICT_GAP,
                       focused_trader=None, purchase_budget=C.BUDGET)
    kw.pop("blocks")
    kw.pop("path_hook")
    pcfg = {"margin": float(fcfg["portfolio"]["margin"]), "block_days": int(fcfg["portfolio"]["block_days"])}

    def hook_base(sink: list):
        inner = ps.composed_hook(pcfg, sink=sink)
        return inner, lt.lever_hook(inner)

    fr = fcfg["state_policy"]["fresh"]
    spans = tuple(tuple(int(y) for y in x) for x in cfg["bounds"]["eras"])
    sub = VS.Subject(
        name="P14", describe=f"P-14 (A3-BRK30-CB20, Stage 2 D-509/D-513): the registered development gate, the bound "
                             f"at 0.05/{n_led}",
        t=t, days=list(days), keys=keys, tv=tv, e_by=dict(e_by), lb_by=dict(lbn_by), kw=kw, blocks=list(blocks),
        margin=pcfg["margin"], block_days=int(cfg["bounds"]["block_days"]), crr=float(fr["combine_rr"]),
        frr=float(fr["funded_rr"]), n_led=n_led, alpha_verdict=V.ALPHA / n_led, seed=int(C.SEED),
        hook_base=hook_base, arm_names={"bound": f"verdict (0.05/{n_led})", "point": "point"}, ref_file=P14_GATE,
        ref_rows=lambda d: p14_rows(d, "gate_at_ledger_n"), ref_paths=P14_PATHS,
        ref_pairs={"bound": ("gate_at_ledger_n", "lower_bound"), "point": ("gate", "point")}, full=True,
        extra={"lb05_by": dict(lb05_by), "flagged": bool(flagged), "era_spans": spans, "pooled": st,
               "plan": getattr(nc, "id", None), "cfg": cfg})
    if sub.crr not in keys or sub.frr not in keys:
        raise X.refused("the fresh legs' R are not among the trades' R.")
    return sub, idents


def rebound_fn(sub: VS.Subject):
    """D-583 on P-14: the stressed trades' e and bound by P-14's registered rule at its verdict level
    (`a3_brk30.bounds_at_n` at N = 370: the era rule's lower era when flagged)."""
    import a3_brk30 as B

    def rebound(tt: pd.DataFrame):
        _, e_by, _, lbn_by, _, flagged = B.bounds_at_n(tt, sub.days, sub.extra["cfg"], sub.n_led)
        return dict(e_by), dict(lbn_by), {"era_flagged": bool(flagged)}

    return rebound


# ------------------------------------------------------------------------------------------------ the identities


def gate05_identity(eng: X.Engine, declared: bool) -> dict:
    """The same call at P-14's 0.05 bound reproduces the registered file's `gate` rows (bound and point at 0 %) on
    IDENT_COLS exactly (in --check: its first paths equal the per-path file's `gate` run, both shifts). Refusing."""
    import a3_brk30 as B
    import zero_edge_decomposition as zd

    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result

    sub = eng.sub
    label = IDENTITY_LABELS[1]
    res = eng.run(label, lb_by=sub.extra["lb05_by"])
    if declared:
        bad = VS.row_problems(res, p14_rows(B._exact(RESULTS_DIR / P14_GATE), "gate"))
        how = (f"at {eng.n_paths} paths and seed {sub.seed}, every R at its 0.05 bound, reproduces results/{P14_GATE}'s "
               f"gate bound and point rows on {', '.join(VS.IDENT_COLS)} exactly")
    else:
        mine = f"{sub.name} {label}"
        bad = zd.path_problems(eng.sink, read_result(RESULTS_DIR / P14_PATHS),
                               [(mine, s, "gate", s) for s in ("lower_bound", "point")], eng.n_paths)
        how = f"the first {eng.n_paths} paths at the 0.05 bound equal results/{P14_PATHS}'s gate run, both shifts"
    if bad:
        raise X.refused(f"P-14's call at the 0.05 bound is not {P14_GATE}'s gate rows -- " + "; ".join(bad[:8]))
    print(f"identity HOLDS: P14's call at the 0.05 bound -- {how}", flush=True)
    return {"section": "identity", "subject": sub.name, "holds": True, "check": f"P14 ({sub.describe}): {how}"}


# ------------------------------------------------------------------------------------------------ writing


def write_reading(rows: list[dict], params: dict, runs: list[str], results_dir: Path | None, seed: int) -> Path:
    """The variants (every engine run beyond the reproductions, once each) into the ledger beside the file, then the
    file and its manifest through `extended.results.write_result` (refusing outside a clean run)."""
    from extended.results import RESULTS_DIR as OWN, write_result
    from propedge.backtest.harness import VariantCounter

    target = Path(results_dir) if results_dir is not None else OWN
    counter = VariantCounter(path=target / "variants.jsonl")
    for label in runs:
        counter.record(prereg_id=VARIANT_ID, seed=int(seed), exploratory=True,
                       params={"study": "Q-18: Stage 2 D-663's validation readings on P-14", "subject": "P14",
                               "run": label, "paths": params["paths"]},
                       label=f"{VARIANT_ID}: P14 {label}")
    out = pd.DataFrame(rows)
    out.insert(1, "reading", READING)
    csv, _ = write_result(out, RESULT, script=SCRIPT, seed=int(seed), parameters=params, results_dir=target,
                          exploratory=True, variant_count=len(runs),
                          notes={"status": READING, "selection": "none: beside P-14's registered verdict",
                                 "readings": "scripts/p14_validation.py's and extended/v1_adapter.py's docstrings"},
                          description="EXPLORATORY (Q-18): Stage 2 D-663's validation readings on P-14's registered "
                                      "gate (block-resampled days, the bound's coverage, the break-even e, missed "
                                      "trades and sessions, D-583's slippage) -- beside its verdict, changing none.")
    print(f"written: {csv.name} ({len(rows)} rows)", flush=True)
    return csv


def params_of(sub: VS.Subject, n_paths: int, parts: list[str], workers: int, secs: dict[str, float],
              eng: X.Engine, resumed: int, autos: dict) -> dict[str, Any]:
    return {"task": TASK, "subject": sub.describe, "registered_file": P14_GATE, "registered_paths_file": P14_PATHS,
            "arms": dict(sub.arm_names), "verdict_arm": "gate_at_ledger_n, lower_bound, 0 %", "point_arm":
            "gate, point, 0 %", "paths": int(n_paths), "horizon_days": int(sub.kw["horizon_days"]),
            "campaign_seed": int(sub.seed), "ledger_n": int(sub.n_led), "era_flagged": bool(sub.extra["flagged"]),
            "seeds": {"B1": SEED_B1, "C1": SEED_C1, "mc_error": SEED_MC, "campaign": int(sub.seed)},
            "seed_forms": {"B1": "np.random.default_rng([SEED_B1, 0, mean block, 0 pooled / 1 era rule])",
                           "C1": "lockstep.child_seed(SEED_C1, arm index, realisation) (extended.v1_adapter.c1_seed)",
                           "mc_error": "np.random.default_rng(SEED_MC) for every run (v1_validation.mc_error)"},
            "parts": parts, "mean_blocks": list(V.MEAN_BLOCKS),
            "b1": {"blocks": list(V.B1_BLOCKS), "auto": autos, "replicates": V.B1_REPS, "verified": V.B1_VERIFY,
                   "levels": ["0.05", f"0.05/{sub.n_led}"]},
            "b2": {"step": V.B2_STEP, "max_steps": V.B2_MAX_STEPS, "mean_block": V.B2_MEAN_BLOCK},
            "c1": {"arms": [list(x) for x in V.C1_ARMS], "realisations": V.C1_REALISATIONS},
            "slip": {"arms": [a["arm"] for a in ps16.arms()], "base": dict(ps16.BASE), "levels_a": list(ps16.LEVELS_A),
                     "levels_b": list(ps16.LEVELS_B), "bound": f"a3_brk30.bounds_at_n at N {sub.n_led}, re-read"},
            "identity_columns": list(VS.IDENT_COLS), "identity_runs": list(IDENTITY_LABELS),
            "not_done": ["V1's A2 (real order against resampled paths)", "V1's B3 (a family's false pass)"],
            "declarations": {"D-663": V.DECLARATION_SHA256, "D-583": ps16.DECLARATION_SHA256},
            "engine_keyword": "gate.run_gate(mean_block=...), shared_days.StationaryDayTable (Stage 2 D-663)",
            "workers": int(workers), "seconds": {k: round(x, 1) for k, x in secs.items()},
            "engine_seconds": [round(x, 1) for x in eng.seconds], "resumed_runs": int(resumed),
            "vendored": "vendor/stage2 (E-002), imported, never edited"}


# ------------------------------------------------------------------------------------------------ main


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="a smoke at 4 paths and small replicates; no reading "
                                                         "printed; nothing written")
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
                  f"python scripts/run_clean.py --name p14-validation --task {TASK} --hours <h> --mem-gb <g> -- "
                  f"python {SCRIPT}")
            return 2
    if str(ROOT / "identity") not in sys.path:
        sys.path.append(str(ROOT / "identity"))      # after the vendored tree: the data files' names only
    import stage2_identity as SI

    try:                                            # Q-58: the engine's read authorised (ledgered in a clean run only)
        reader.authorise_engine_read(
            reader.CHOICE_START, reader.JUDGED_END, purpose=reader.REGISTERED_DESIGN, declaration=READ_ROW,
            design=["P-14"], files=SI.engine_files(VENDOR, bars=False),
            what=f"{READ_ROW}'s readings ({SCRIPT}, {TASK}): Stage 2 D-663's validation readings on P-14, parts "
                 f"{', '.join(parts)}" + (" (--check)" if a.check else ""))
    except (reader.ReadRefused, FileNotFoundError) as exc:
        print(SI.refusal(exc), flush=True)
        return 3
    t_all = time.time()
    n_paths = V.N_PATHS if declared else CHECK_PATHS
    t0 = time.time()
    sub, idents = build_p14()
    print(f"P14 built: {len(sub.days)} sessions, {len(sub.t)} offered trades ({time.time() - t0:.0f} s)", flush=True)
    resume = VS.Resume(None, "check")
    if declared and not a.no_resume:
        commit = subprocess.run(["git", "rev-parse", "--short=12", "HEAD"], cwd=ROOT, capture_output=True,
                                text=True).stdout.strip() or "nocommit"
        resume = VS.Resume(RESUME_DIR, f"p14_{commit}_{n_paths}")
    resumed = len(resume.rows)
    eng = X.Engine(sub, n_paths, a.workers, resume, mc_seed=SEED_MC)
    reg, ident = VS.registered_run(eng, declared)
    idents.append({**ident, "subject": sub.name})
    idents.append(gate05_identity(eng, declared))
    rows: list[dict] = []
    secs: dict[str, float] = {}
    autos: dict[str, int] = {}

    def auto() -> int:
        if "P14" not in autos:
            r0 = VS.part_a0(sub)
            autos["P14"] = int(next(r["auto_block"] for r in r0 if r["series"] == "day_r"))
        return autos["P14"]

    for p in parts:
        t1 = time.time()
        if p == "A1":
            rows += VS.part_a1(eng, reg)
        elif p == "B2":
            rows += VS.part_b2(eng, reg, V.B2_MAX_STEPS if declared else CHECK_B2_STEPS)
        elif p == "A0":
            rows += VS.part_a0(sub)
        elif p == "B1":
            rows += X.part_b1(sub, seed=SEED_B1, reps=V.B1_REPS if declared else CHECK_REPS,
                              verify=V.B1_VERIFY if declared else CHECK_VERIFY, auto=auto())
        elif p == "C1":
            rows += X.part_c1(eng, reg, seed=SEED_C1)
        elif p == "SLIP":
            rows += X.part_slip(eng, reg, rebound_fn(sub))
        secs[p] = time.time() - t1
        print(f"part {p}: {secs[p]:.0f} s", flush=True)
    runs = [lab for lab in eng.labels if lab not in IDENTITY_LABELS]
    if a.check:
        print(f"--check done: parts {parts}; {len(rows)} rows built, none printed, nothing written; {len(runs)} engine "
              f"runs beyond the identities at {n_paths} paths; engine seconds {[round(x, 1) for x in eng.seconds]}; "
              f"{time.time() - t_all:.0f} s", flush=True)
    else:
        rows.append({"section": "not_done", "subject": sub.name,
                     "note": "V1's A2 (the real-order replay against each scheme's resampled paths) and B3 (a family's "
                             "familywise false pass) are not in Q-18's brief; not run"})
        head = [{"section": "declaration", "subject": sub.name, "holds": True,
                 "check": f"the readings Stage 2 D-663 put in RESEARCH_PROTOCOL step 7, read on P-14 under TASK_QUEUE "
                          f"{TASK} (E-007 (f)); seeds {SEED_B1}, {SEED_C1}, {SEED_MC} fixed in {SCRIPT} before the run"}]
        write_reading(head + idents + rows, params_of(sub, n_paths, parts, a.workers, secs, eng, resumed, autos),
                      runs, None, sub.seed)
        print(f"done: {len(runs)} engine runs beyond the identities ({resumed} read back from the resume file); "
              f"{time.time() - t_all:.0f} s", flush=True)
    mem = X.peak_memory()
    if mem:
        print(mem, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
