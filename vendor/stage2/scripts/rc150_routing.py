"""EXPLORATORY (D-568): the routing-rule screen on P-16's cell -- which account each coin trade is offered to first --
with D-568's three guards against hindsight. Selects nothing by itself: a rule passing every guard would follow
D-568 (3) to its own registered development test.

    python scripts/rc150_routing.py --check --paths 4 --g2-paths 4 --coins 2 --starts 6   # every guard at 4 paths;
                                                                                          #   nothing written
    python scripts/rc150_routing.py --workers 2                                           # the screen (a clean
                                                                                          #   checkout, D-474)

**The cell** (P-16, D-544, D-547): `rc_s150_all` -- the 37.5-point news-safe coin, all-day window -- built by
`rc_stop_walkforward.walk_stop` / `cell` on every development day (identity: its count against
`rc_width_screen.csv`'s row and its content hash against `rc150_dev_test.TRADES_SHA256`), through P-14's engine call
(`rc_screen.Runner`: the no-closure table, 20 purchases and resets in 21 trading days, the strict one-at-a-time rule,
five Topstep seats, the placement off, 0 % denial).

**The menu** (D-568 (1); the router's opt-in `routing_rule`, `propedge.campaign.shared_days.ROUTING_RULES`; every
other routing check unchanged, ties to the longest-waiting account):

    R0 longest_waiting   the current rule (D-318's `able`), the reference -- `routing_rule` None
    R1 fixed_order       accounts in a fixed cycle by their position in the day's list, after the last one that traded
    R2 combine_first     Combines before funded accounts
    R3 funded_first      funded accounts before Combines
    R4 most_room         the largest cushion above the loss limit (balance less floor at the session's start)
    R5 closest_to_goal   the highest progress -- a Combine's balance over its $3,000 target, a funded account's winning
                         days over the five the Standard path needs (a unit-free share, so the kinds rank together)
    R6 random            a seeded random order for every trade (seed 20261500 with the path's seed), the noise check

**Guard 1 -- paired** (G1): every rule on the same trades, campaign seed 20261131, coin seed 20261102, 500 paths; growth
on the required bankroll at the bound and the point, the required bankroll, the zero-edge twin (same rule), trades taken
a session, D-518's journey on the verdict arm and D-509's four slice lines against FV3-C (FV3-C's slices read from
`customer_slices.csv`, pinned, never rerun); the reference must reproduce `rc_width_screen.csv`'s `rc_s150_all` row.
**Guard 2 -- across coins** (G2): every rule and the reference on 50 coin seeds (20261600 + i), 200 paths each, the
reference re-run for each coin; a rule's wins = coins on which it grows more at the bound than the reference; it passes
with at least 40 of 50 (D-568 (2)). **Guard 3 -- early then late** (G3): every rule on 2020-01-01 .. 2023-12-31 and on
2024-01-01 .. 2026-07-16 alone (D-551's split, `rc_stop_walkforward`: each span's own cutoff and pooled bound), 500 paths;
the rule other than the reference with the highest early growth at the bound must also beat the reference late.

**The rule** (D-568 (3)): a rule passing G2 and G3, growing more than the reference at the bound in G1 by more than 0.05,
resolving every offered R and holding the four slice lines, would become a candidate; else the current rule stands.

**Resume** (D-540's form): each finished run kept outside the checkout, keyed by commit and counts; off in --check.

**G2's entry (D-570, the coordinator's ruling before the run):** after G1, G2 runs only for the rules whose G1 growth on
the required bankroll at the bound exceeds R0's (any positive difference) -- a rule that does not cannot become a
candidate under D-568 (3) anyway; the output's `g2_entry` rows say which entered and why, and each rule left out carries
a `g2_summary` row "not run: did not beat R0 in G1". 50 coin seeds, 200 paths and the 40-of-50 line unchanged; G3 runs
for every rule.

Writes `results/rc150_routing.csv` (EXPLORATORY; sections identity, g1, journey, slice_lines, g2_entry, g2, g2_summary, g3,
g3_choice, verdict) with its manifest; variants under `D-568:rc150_routing` (the seven rules).
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Any

if __name__ == "__main__":                 # one BLAS thread, before numpy loads (D-464 (5))
    for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import rc_screen as S  # noqa: E402

SCRIPT = "scripts/rc150_routing.py"
DECISION = "D-568"
RESULT = "rc150_routing"
FAMILY_ID = f"{DECISION}:rc150_routing"
CELL = "rc_s150_all"
STOP = 150
N_PATHS = S.N_PATHS
G2_PATHS = 200
COIN_SEEDS = tuple(20261600 + i for i in range(50))   # D-568 (2), fixed before any read
G2_WINS = 40
MARGIN = 0.05
#: (name, the router's rule) -- R0 the reference first
RULES = (("R0_longest_waiting", None), ("R1_fixed_order", "fixed_order"), ("R2_combine_first", "combine_first"),
         ("R3_funded_first", "funded_first"), ("R4_most_room", "most_room"),
         ("R5_closest_to_goal", "closest_to_goal"), ("R6_random", "random"))
REFERENCE = "R0_longest_waiting"
#: D-570 (the coordinator's ruling before the run): G2 runs only for the rules whose G1 growth on the required bankroll at
#: the bound exceeds R0's (any positive difference) -- a rule that does not beat R0 in G1 cannot become a candidate under
#: D-568 (3) anyway; G1 and G3 run for every rule as declared
G2_ENTRY = "D-570: G2 runs for a rule only if its G1 growth at the bound exceeds R0's"
READING = "EXPLORATORY (D-568): the routing-rule screen on P-16's cell with three guards; selects nothing by itself"


# ------------------------------------------------------------------------------------------------ pure parts (tested)


def g2_summary(rows: list[dict], names=None, wins_needed: int = G2_WINS) -> list[dict]:
    """Per rule: on how many coins it grows more at the bound than the reference on the same coin, and whether that
    reaches `wins_needed`. `rows` hold (coin_seed, rule, growth_on_required)."""
    by = {}
    for r in rows:
        by.setdefault(int(r["coin_seed"]), {})[str(r["rule"])] = float(r["growth_on_required"])
    names = [n for n, _ in RULES if n != REFERENCE] if names is None else list(names)
    out = []
    for n in names:
        diffs = [v[n] - v[REFERENCE] for v in by.values() if n in v and REFERENCE in v]
        wins = int(sum(d > 0 for d in diffs))
        out.append({"section": "g2_summary", "rule": n, "coins": len(diffs), "wins": wins,
                    "mean_difference": float(np.mean(diffs)) if diffs else float("nan"),
                    "wins_needed": int(wins_needed), "passes_g2": bool(len(diffs) and wins >= wins_needed)})
    return out


def g2_entry(g1: dict[str, dict]) -> list[dict]:
    """D-570: per rule other than the reference, whether it enters G2 -- its G1 growth at the bound above R0's -- and
    why."""
    ref = float(g1[REFERENCE]["growth_on_required"])
    out = []
    for n, _ in RULES:
        if n == REFERENCE:
            continue
        diff = float(g1[n]["growth_on_required"]) - ref
        enters = bool(np.isfinite(diff) and diff > 0)
        out.append({"section": "g2_entry", "rule": n, "g1_growth_minus_reference": diff, "enters_g2": enters,
                    "why": ("its G1 growth at the bound exceeds R0's" if enters
                            else "not run: did not beat R0 in G1")})
    return out


def g3_choice(early: dict[str, float], late: dict[str, float]) -> dict[str, Any]:
    """D-568's guard 3: the rule other than the reference with the highest early growth at the bound (ties to the menu's
    order), and whether it beats the reference late."""
    cands = [n for n, _ in RULES if n != REFERENCE and n in early and np.isfinite(early[n])]
    if not cands:
        return {"section": "g3_choice", "early_choice": "", "passes_g3": False}
    best = max(early[n] for n in cands)
    pick = next(n for n in cands if early[n] >= best - 1e-12)
    lg, lr = late.get(pick, float("nan")), late.get(REFERENCE, float("nan"))
    return {"section": "g3_choice", "early_choice": pick, "early_growth": float(early[pick]),
            "early_reference": float(early.get(REFERENCE, float("nan"))), "late_growth": float(lg),
            "late_reference": float(lr), "passes_g3": bool(np.isfinite(lg) and np.isfinite(lr) and lg > lr)}


def verdict(g1: dict[str, dict], g2: list[dict], g3: dict[str, Any], resolves: bool) -> list[dict]:
    """D-568 (3) per rule: every guard and line."""
    ref = float(g1[REFERENCE]["growth_on_required"])
    p2 = {r["rule"]: bool(r.get("passes_g2", False)) for r in g2}
    out = []
    for n, _ in RULES:
        if n == REFERENCE:
            continue
        r = g1[n]
        diff = float(r["growth_on_required"]) - ref
        checks = {"g1_beats_by_margin": bool(diff > MARGIN), "every_r_resolves": bool(resolves),
                  "slice_lines_hold": bool(r.get("slice_lines_hold", False)), "passes_g2": p2.get(n, False),
                  "passes_g3": bool(g3.get("passes_g3")) and g3.get("early_choice") == n}
        out.append({"section": "verdict", "rule": n, "growth_minus_reference": diff, **checks,
                    "candidate": bool(all(checks.values()))})
    return out


# ------------------------------------------------------------------------------------------------ the runs


def resume_for(folder: Path, key: str):
    """D-540's resume file under this study's own name (the payout screen's class, its path renamed)."""
    import rc150_payout_screen as PS

    class Resume(PS.Resume):
        def __init__(self, folder, key):
            self.path = Path(folder) / f"{RESULT}_{key}.jsonl"
            self.rows = {}
            if self.path.is_file():
                import json

                for line in self.path.read_text(encoding="utf-8").splitlines():
                    if line.strip():
                        r = json.loads(line)
                        self.rows[r["_label"]] = r["payload"]
                print(f"  resume: {len(self.rows)} finished run(s) read from {self.path}", flush=True)

    return Resume(folder, key)


def run_rule(I: dict, label: str, rule: str | None, t: pd.DataFrame, days: list[str], n_paths: int, workers: int,
             bounds=None, twin: bool = False) -> dict[str, Any]:
    """One rule's gate run (and, with `twin`, its zero-edge twin) through P-14's engine call."""
    import rc150_payout_screen as PS

    R = S.Runner(I, workers)
    df = R.run(label, t, days, n_paths, routing_rule=rule, bounds=bounds)
    tw = R.run(f"{label} twin", t, days, n_paths, twin=True, routing_rule=rule, bounds=bounds) if twin else None
    if tw is not None:
        return {"df": df, **PS.gate_reading(label, df, tw, R.sink)}
    g = df[(df["shift"] == "lower_bound") & np.isclose(df["enforcement_p"].astype(float), 0.0)].iloc[0]
    p = df[(df["shift"] == "point") & np.isclose(df["enforcement_p"].astype(float), 0.0)].iloc[0]
    return {"df": df, "growth_on_required": float(g["pf_growth_on_base_p50"]),
            "growth_on_required_point": float(p["pf_growth_on_base_p50"]), "required_p90": float(g["pf_required_p90"])}


def journey_and_lines(I: dict, t: pd.DataFrame, days: list[str], rule: str | None, name: str, fsl: pd.DataFrame,
                      workers: int, starts: int | None) -> dict[str, Any]:
    """D-518's journey on the verdict arm's replay and D-509's four lines against FV3-C, under the rule."""
    import a3_brk30 as B
    import a3_brk30_cb20 as C
    import atlas_a3 as A
    import customer_slices as cs
    import rc150_dev_test as R150
    import rc_dev_test as D

    from propedge.research import customer_journey as cj

    L = I["L"]
    keys = B.rrs(t)
    _, e_by, lb_by, _, _ = A.bounds(t, days, keys, L["cfg"])
    cap = B.capacity(t, L["fcfg"])
    camp = D.rc_campaign(I, t, days, e_by, lb_by, cap, R150.SPEC)
    if rule is not None:
        camp.kw["routing_rule"] = rule              # reaches the replay's draws (customer_slices.engine_args)
    units, rsl = D.journey_and_slices(camp, I["plan"], C.BUDGET, workers, starts, name)
    sub = float(camp.kw["rules"].subscription)
    journey = [{"section": "journey", "rule": name, "arm": "verdict", "source": "replay",
                "key": cj.metric_key(m["milestone"], m["measure"], m["at_days"]), **m} for m in cj.metrics(units, sub)]
    f = fsl if starts is None else fsl[fsl["start_day"].astype(int) < int(starts)]
    summ = cs.summarise(pd.concat([rsl, f], ignore_index=True))
    lines = [{**r, "section": "slice_lines", "rule": name} for r in C.slice_lines(summ, candidate=name, reference="fv3c")]
    return {"journey": journey, "lines": lines, "lines_hold": bool(all(r["holds"] for r in lines))}


def coin_cell(W: dict, I: dict, seed: int, days: list[str]) -> pd.DataFrame | None:
    """The cell's trades with the coin's seed replaced (the same walk; `resolved_coin.coin_table` over the development
    days in the walk's order and every mark)."""
    import rc_stop_walkforward as WF

    from propedge.research import resolved_coin as rc

    dd = I["L"]["days"]["date"].astype(str).tolist()
    W2 = {**W, "coins": rc.coin_table(dd, rc.marks(), seed=int(seed))}
    return WF.cell(W2, STOP, days)["trades"]


# ------------------------------------------------------------------------------------------------ main


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    import a3_brk30 as B
    import atlas_a3 as A
    import rc150_dev_test as R150
    import rc150_payout_screen as PS
    import rc_dev_test as D
    import rc_stop_walkforward as WF

    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import write_result
    from propedge.research import resolved_coin as rc

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="every guard at the given counts; nothing written")
    ap.add_argument("--paths", type=int, default=N_PATHS, help="G1 and G3 paths (500 for the screen)")
    ap.add_argument("--g2-paths", type=int, default=G2_PATHS, help="G2 paths (200 for the screen)")
    ap.add_argument("--coins", type=int, default=len(COIN_SEEDS), help="test seam: the first coin seeds of G2")
    ap.add_argument("--g2-rules", default=None, help="test seam / runtime option: comma-separated rule names for G2 "
                                                     "(the reference always runs); the screen runs every rule")
    ap.add_argument("--starts", type=int, default=None, help="test seam: the journey's first starts")
    ap.add_argument("--sections", default="g1,g2,g3", help="test seam: which guards to run")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--no-resume", action="store_true")
    ap.add_argument("--resume-dir", default=None)
    a = ap.parse_args(argv)
    full = (int(a.paths) == N_PATHS and int(a.g2_paths) == G2_PATHS and int(a.coins) == len(COIN_SEEDS)
            and a.starts is None and a.g2_rules is None and a.sections == "g1,g2,g3")
    if not a.check and not full:
        print(f"REFUSED ({DECISION}): the reading runs every guard at the declared counts; a smaller run is --check.")
        return 2
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    sections = set(a.sections.split(","))
    t_all = time.time()
    srow = PS.screen_row(RESULTS_DIR)
    print("P-14's inputs, the no-closure plan and the 37.5-point walk...", flush=True)
    I = S.inputs()
    W = WF.walk_stop(I, STOP)
    days = list(W["days"])
    full_cell = WF.cell(W, STOP, days)
    t = full_cell["trades"]
    h = D.trades_hash(t)
    bad = []
    if int(len(t)) != int(srow["candidates"]):
        bad.append(f"{len(t)} candidates against the screen's {int(srow['candidates'])}")
    if h != R150.TRADES_SHA256:
        bad.append(f"content hash {h[:16]} against the pinned {R150.TRADES_SHA256[:16]}")
    if bad:
        print(f"REFUSED ({DECISION}): the cell is not P-16's {CELL} -- " + "; ".join(bad))
        return 3
    print(f"identity HOLDS: the cell = P-16's {CELL} ({len(t)} candidates; content hash {h[:16]})", flush=True)
    idents = [{"section": "identity", "holds": True,
               "check": f"the cell's trades (rc_stop_walkforward.cell on every development day): {len(t)} candidates as "
                        f"{PS.SCREEN_FILE}'s {CELL}; content hash {h} = rc150_dev_test.TRADES_SHA256"}]
    hc = D.trades_hash(coin_cell(W, I, rc.COIN_SEED, days))
    if hc != h:
        print(f"REFUSED ({DECISION}): rebuilding the cell with the declared coin seed gives {hc[:16]}, not {h[:16]} -- "
              "guard 2's coin swap would not be the same construction.")
        return 3
    idents.append({"section": "identity", "holds": True,
                   "check": "guard 2's construction (the same walk, `coin_table` re-drawn) at the candidate's coin seed "
                            f"{rc.COIN_SEED} reproduces the cell's content hash"})
    print("identity HOLDS: guard 2's coin swap at the candidate's seed = the cell", flush=True)
    res_cols, resolves = A.resolution(t, W["rr_grid"])
    resume = None
    if not a.check and not a.no_resume:
        import subprocess

        commit = subprocess.run(["git", "rev-parse", "--short=12", "HEAD"], cwd=ROOT, capture_output=True,
                                text=True).stdout.strip() or "nocommit"
        folder = Path(a.resume_dir) if a.resume_dir else (
            Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "stage2-runs" / "resume")
        resume = resume_for(folder, f"{commit}_{a.paths}_{a.g2_paths}")

    # ---- guard 1: paired
    g1: dict[str, dict] = {}
    g1_extra: list[dict] = []
    if "g1" in sections:
        fsl = PS.fv3c_slices(RESULTS_DIR)
        for name, rule in RULES:
            t0 = time.time()

            def make(name=name, rule=rule):
                r = run_rule(I, name, rule, t, days, a.paths, a.workers, twin=True)
                df = r.pop("df")
                if name == REFERENCE and int(a.paths) == N_PATHS:
                    prob = PS.growth_problems(df, srow)
                    if prob:
                        raise SystemExit(f"REFUSED ({DECISION}): the reference is not {PS.SCREEN_FILE}'s {CELL} -- "
                                         + "; ".join(prob))
                jl = journey_and_lines(I, t, days, rule, name, fsl, a.workers, a.starts)
                row = {"section": "g1", "rule": name, "routing_rule": rule or "longest_waiting (D-318, reference)",
                       **r, "slice_lines_hold": jl["lines_hold"]}
                return {"row": row, "journey": jl["journey"], "lines": jl["lines"]}

            res = PS.cached(resume, f"g1 {name}", make)
            g1[name] = res["row"]
            g1_extra += res["journey"] + res["lines"]
            print(f"  G1 {name}: done ({time.time() - t0:.0f} s)", flush=True)
        if int(a.paths) == N_PATHS:
            idents.append({"section": "identity", "holds": True,
                           "check": f"the reference rule at seed {S.SEED}, {N_PATHS} paths, reproduces "
                                    f"results/{PS.SCREEN_FILE}'s {CELL} growth at the bound and point and its required "
                                    "bankroll"})
            print(f"identity HOLDS: the reference at {N_PATHS} paths = {PS.SCREEN_FILE}'s {CELL}", flush=True)
        ref = float(g1[REFERENCE]["growth_on_required"])
        for r in g1.values():
            r["growth_minus_reference"] = float(r["growth_on_required"]) - ref

    # ---- guard 2: across coins
    g2_rows: list[dict] = []
    entry = g2_entry(g1) if g1 else []
    if a.g2_rules is not None:                     # a --check seam only (the full run refuses it)
        g2_names = [REFERENCE] + [n for n in a.g2_rules.split(",") if n != REFERENCE]
    elif entry:                                    # D-570: the rules that beat R0 in G1
        g2_names = [REFERENCE] + [r["rule"] for r in entry if r["enters_g2"]]
    else:                                          # --check without G1: every rule
        g2_names = [n for n, _ in RULES]
    if not a.check:                                # (in --check the entry would read a few paths: not printed)
        print(f"  G2 entry ({G2_ENTRY}): {[n for n in g2_names if n != REFERENCE] or 'none'}", flush=True)
    if "g2" in sections and len(g2_names) > 1:
        for s in COIN_SEEDS[:int(a.coins)]:
            t0 = time.time()
            ts = coin_cell(W, I, s, days)
            for name, rule in RULES:
                if name not in g2_names:
                    continue

                def make(name=name, rule=rule, s=s, ts=ts):
                    r = run_rule(I, f"g2 {s} {name}", rule, ts, days, a.g2_paths, a.workers)
                    r.pop("df")
                    return {"section": "g2", "coin_seed": int(s), "rule": name, **r}

                g2_rows.append(PS.cached(resume, f"g2 {s} {name}", make))
            print(f"  G2 coin {s}: done ({time.time() - t0:.0f} s)", flush=True)
    g2s = g2_summary(g2_rows, [n for n in g2_names if n != REFERENCE]) if g2_rows else []
    g2s += [{"section": "g2_summary", "rule": r["rule"], "coins": 0, "wins": 0, "wins_needed": int(G2_WINS),
             "passes_g2": False, "note": r["why"]} for r in entry if not r["enters_g2"]]

    # ---- guard 3: early then late
    g3_rows: list[dict] = []
    g3c: dict[str, Any] = {"section": "g3_choice", "early_choice": "", "passes_g3": False}
    if "g3" in sections:
        growth: dict[str, dict[str, float]] = {}
        for span, (lo, hi) in WF.SPANS.items():
            sd = WF.span_days(days, lo, hi)
            c = WF.cell(W, STOP, sd)
            ts = c["trades"]
            keys = B.rrs(ts)
            bounds = B.check_bounds(ts, sd, keys)
            for name, rule in RULES:
                def make(name=name, rule=rule, span=span, ts=ts, sd=sd, bounds=bounds):
                    r = run_rule(I, f"g3 {span} {name}", rule, ts, sd, a.paths, a.workers, bounds=bounds)
                    r.pop("df")
                    return {"section": "g3", "span": span, "span_first": sd[0], "span_last": sd[-1],
                            "sessions": len(sd), "rule": name, **r}

                row = PS.cached(resume, f"g3 {span} {name}", make)
                g3_rows.append(row)
                growth.setdefault(span, {})[name] = float(row["growth_on_required"])
            print(f"  G3 {span}: done", flush=True)
        g3c = g3_choice(growth.get("early", {}), growth.get("late", {}))

    seconds = time.time() - t_all
    if a.check:
        print(f"every guard ran ({sorted(sections)}; G1/G3 at {a.paths} paths, G2 at {a.g2_paths} paths on "
              f"{int(a.coins)} coin(s)); no reading printed; nothing written (--check). {seconds:.0f} s")
        return 0
    verd = verdict(g1, g2s, g3c, resolves)
    out = pd.DataFrame(idents + list(g1.values()) + g1_extra + entry + g2_rows + g2s + g3_rows + [g3c] + verd)
    out.insert(1, "reading", READING)
    counter = VariantCounter(path=rd / "variants.jsonl")
    for name, rule in RULES:
        counter.record(prereg_id=FAMILY_ID, seed=S.SEED, exploratory=True,
                       params={"study": "D-568's routing-rule screen", "cell": CELL, "rule": name,
                               "routing_rule": rule, "g1_paths": N_PATHS, "g2_coins": len(COIN_SEEDS),
                               "g2_paths": G2_PATHS, "g3_spans": list(WF.SPANS)},
                       label=f"D-568's routing screen: {name}" + (" (reference)" if name == REFERENCE else ""))
    write_result(out, RESULT, script=SCRIPT, seed=S.SEED, exploratory=True, results_dir=results_dir,
                 variant_count=len(RULES),
                 parameters={"decision": DECISION, "cell": CELL, "stop_ticks": STOP, "rules": [list(r) for r in RULES],
                             "reference": REFERENCE, "seed": S.SEED, "coin_seed": rc.COIN_SEED,
                             "random_rule_seed": 20261500, "g1_paths": N_PATHS, "g2_coin_seeds":
                             [COIN_SEEDS[0], COIN_SEEDS[-1]], "g2_paths": G2_PATHS, "g2_wins_needed": G2_WINS,
                             "g3_spans": {k: list(v) for k, v in WF.SPANS.items()}, "margin": MARGIN,
                             "g2_entry": G2_ENTRY, "g2_rules_run": [n for n in g2_names if n != REFERENCE],
                             "cell_trades_sha256": h, "every_r_resolves": bool(resolves),
                             "fv3c_slices": "results/customer_slices.csv (sha256 pinned), read, never rerun",
                             "workers": int(a.workers), "seconds": round(seconds, 1)},
                 notes={"status": READING, "selection": "D-568 (3): a rule passing every guard would become a "
                                                         "candidate with its own registered test"},
                 description="EXPLORATORY (D-568): P-16's cell (the 37.5-point news-safe coin) under seven routing rules "
                             "-- the current longest-waiting rule and six state-based ones -- each paired (500 paths, "
                             "zero-edge twin, journey, slice lines), across 50 coin seeds (200 paths) and early/late "
                             "(2020-2023 / 2024-2026); the verdict per D-568 (3).")
    print(pd.DataFrame(verd).to_string(index=False))
    print(f"written: {RESULT}.csv ({seconds:.0f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
