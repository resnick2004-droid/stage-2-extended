"""RD-01's reading (`prereg/RD-01_firm_contracts.md`): a described reading, unnumbered (E-023 (1)) -- other firms'
contracts on the registered trades, the user scorecard per plan paired with Topstep by month, and beside it E-007
(e)'s readings, the denial ladder and the gate. Nothing is chosen, nothing carried; no pass line.

    python scripts/run_clean.py --name rd01-scorecard --task <Q> --hours <h> --mem-gb 3 -- \\
        python scripts/rd01_reading.py --purpose firm_scorecard --identity-row E-NNN
    python scripts/run_clean.py --name rd01-ladder ... -- python scripts/rd01_reading.py --purpose firm_ladder_beside \\
        --identity-row E-NNN
    python scripts/run_clean.py --name rd01-gate ... -- python scripts/rd01_reading.py --purpose firm_gate_beside \\
        --identity-row E-NNN

**One purpose, one clean run** (section 6 item 6): `--purpose` is one of the text's three judged-block purposes
(`firm_scorecard`, `firm_ladder_beside`, `firm_gate_beside`); each is authorised once through
`extended.reader.authorise_engine_read` (declaration `prereg/RD-01_firm_contracts.md`, pinned; the development window;
the engine's files) before anything is read, refused outside a clean run of a committed tree, and a second run under
the same purpose is refused unless `--repeat E-NNN` names a decision row naming the declaration.

**The identity stage first** (9.1): `--identity-row E-NNN` must be a decision row that names
`identity/firms_identity.py` and says its identities hold; otherwise nothing runs.

**What each purpose writes** (through `extended.results`, each file with its manifest: the commit, the blobs run, the
parameters; only inside a clean run; never over an existing file):

* `firm_scorecard` -> `results/rd01_scorecard.csv` (sections `counts` and `tier1_count` -- 9.3's mechanics, printed
  first --, `scorecard`, `extra`, `path`, `response` -- U1's card, E-007 (e)'s measures and the path measures per run and
  arm --, `paired` and `paired_card` -- each plan less TS by month and block with 10.2's reading --, `price_grid` and
  `break_even` -- A-10) and `results/rd01_scorecard_starts.csv` (one row a start, run and arm). The 30 replays of 7.3,
  or 34 when P-16's count of 5.5 is not zero (decided from the trades' times before any outcome).
* `firm_ladder_beside` -> `results/rd01_ladder.csv`: the denial ladder (10, 25, 50 %) on TS-16 and P-16's eight
  corners, the verdict arm, each start's draws from seed 20261990 (A-9's seed base), Q-17's exact-length rule.
* `firm_gate_beside` -> `results/rd01_gate.csv` and `results/rd01_gate_paths.csv`: the 16 corners' gates at 500 paths
  at the stream's registered gate seed, point and bound and the zero-edge twin, paired with TS's registered gate paths;
  Quick Pay by E-089's ruling (`extended.firm_reading.gate_rows`).

No smaller run exists: every judged-block read is the reading's own, once (a check on real data would spend the
purpose's one read). The pipeline is checked end to end on toy campaigns (`tests/rd01_reading_synthetic.py`).

**Estimates** (not measured): the scorecard is 30 or 34 replays, each both arms on every start through A-9 and once
more directly (A-10 and 9.3's ledger counts), about twice U1's full pass per replay -- tens of hours at one worker;
the ladder 27 replays of one arm; the gate 16 corners x 500 paths x (two shifts and a twin), Quick Pay's at one worker.
Peak memory about one U1 pass (about 3 GB at one worker).
"""
from __future__ import annotations

import argparse
import gc
import os
import pickle
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for _p in (str(ROOT), str(ROOT / "identity")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from extended import RUNS_DIR, use_vendored_stage2  # noqa: E402

use_vendored_stage2()

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from extended import firm_reading as R  # noqa: E402
from extended import firm_terms as T  # noqa: E402
from extended import reader  # noqa: E402
from extended import user_beside as B  # noqa: E402
from extended import user_readings as UR  # noqa: E402

SCRIPT = "scripts/rd01_reading.py"
VENDOR = ROOT / "vendor" / "stage2"
RESULTS = {"firm_scorecard": ("rd01_scorecard", "rd01_scorecard_starts"), "firm_ladder_beside": ("rd01_ladder",),
           "firm_gate_beside": ("rd01_gate", "rd01_gate_paths")}
READING = ("DESCRIBED (RD-01, E-023 (1)): other firms' contracts on the registered trades; no pass line, nothing chosen "
           "or carried; 0 % denial and the placement off in the headline (E-008)")
LADDER_PLANS = ("LU", "DT", "FP", "QP")
PATHS = 500
#: the build's readings printed in every manifest (the red team's n1, n2, n4, n8; E-092)
CONVENTIONS = {
    "dt_inactivity": "windows of 30 calendar days from the purchase (an evaluation) or the activation (a Pro account): "
                     "the first [that date, that date + 29 days]; a later purchase dated its session's date, a day-0 "
                     "purchase the calendar day before the first session; the account ends at the first close at which "
                     "a window has ended, or will end before the next session, without a $200 day; 21 sessions in the "
                     "gate",
    "dt_30_percent": "the cycle's best day and profit as the engine's Consistency path keeps them (w_best, w_profit): "
                     "the request day's P&L out of the cycle",
    "qp_ceiling": "read at the close (an intraday crossing that falls back by the close is not a pause)",
    "dt_inactivity_flag": "an evaluation closed for inactivity carries the engine's `abandoned` flag; counted as "
                          "`inactive_closed`, never as a cash refusal",
    "qp_bracket": "A-7 classifies won-at-R on the run's point outcomes on every arm (M3)",
    "a4_logging": "a day-logging trade at one micro under the design's own stand-aside, its intended risk the table's",
}
#: the seeds the readings use (section 12; the gate's are each stream's registered gate seed)
SEEDS = {"ladder": 20261990, "coverage": 20261991, "gate_p16": 20261206, "gate_p14": 20261131}


def _commit() -> str:
    out = subprocess.run(["git", "rev-parse", "--short=12", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    return out.stdout.strip() or "nocommit"


#: the code a reading runs, recorded in every manifest by its git blob as read from disk (the files actually run)
CODE = ("scripts/rd01_reading.py", "extended/firm_reading.py", "extended/firms.py", "extended/firm_accounts.py",
        "extended/firm_terms.py", "extended/firm_counts.py", "extended/firm_uncertainty.py", "extended/user_beside.py",
        "extended/user_readings.py", "extended/user_measures.py", "extended/gate.py", "extended/campaign.py",
        "identity/user_beside_identity.py", "config/rules_extended.yaml", "config/calendar_fomc_minutes.csv",
        "config/calendar_early_closes.csv", "prereg/RD-01_firm_contracts.md")


def code_blobs() -> dict[str, str]:
    """{path: git blob id} of each file the reading runs, hashed from the file on disk (`git hash-object`)."""
    out = {}
    for rel in CODE:
        r = subprocess.run(["git", "hash-object", str(ROOT / rel)], cwd=ROOT, capture_output=True, text=True)
        out[rel] = r.stdout.strip() if r.returncode == 0 else "missing"
    return out


def identity_row_problems(row_id: str | None) -> list[str]:
    """9.1: the reading starts only once the identity stage has printed that its identities hold -- a decision row
    that names `identity/firms_identity.py` and says they hold."""
    if not row_id:
        return ["no --identity-row: the identity stage (9.1) runs first, under its own decision row"]
    row = reader.decision_row(reader._decisions(ROOT), str(row_id))
    if row is None:
        return [f"{row_id} is no decision row of DECISIONS.md"]
    low = row.lower()
    bad = []
    if "firms_identity" not in low:
        bad.append(f"{row_id} does not name identity/firms_identity.py")
    if "hold" not in low:
        bad.append(f"{row_id} does not say the identities hold")
    return bad


class Resume:
    """Each finished cell kept outside the checkout, keyed by the commit (D-540's pattern)."""

    def __init__(self, folder: Path | None):
        self.folder = folder
        if folder is not None:
            folder.mkdir(parents=True, exist_ok=True)

    def get(self, key: str):
        p = None if self.folder is None else self.folder / (key.replace("|", "__") + ".pkl")
        if p is None or not p.is_file():
            return None
        with p.open("rb") as f:
            return pickle.load(f)

    def put(self, key: str, value) -> None:
        if self.folder is None:
            return
        p = self.folder / (key.replace("|", "__") + ".pkl")
        tmp = p.with_suffix(".tmp")
        with tmp.open("wb") as f:
            pickle.dump(value, f)
        os.replace(tmp, p)


# ------------------------------------------------------------------------------------------------ the scorecard


def _tag(rows: list[dict], **head: Any) -> list[dict]:
    return [{**head, **r} for r in rows]


def scorecard_reading(streams: dict[str, dict[str, Any]], runs: list[T.Run], starts: int | None, *,
                      coverage: bool = True, resume: Resume | None = None) -> tuple[list[dict], pd.DataFrame, list[str]]:
    """The 7.3 runs: (rows, the per-start table, the refusing problems). `streams`: {"p16"|"p14": {"jobs": {arm: job},
    "config": U1's config def}}. TS's run of a stream comes first (its cells are the pairing's other side)."""
    import user_journey as UJ

    resume = resume or Resume(None)
    off = B.BY_NAME["off"]
    rows: list[dict] = []
    starts_parts: list[pd.DataFrame] = []
    problems: list[str] = []
    for name, st in streams.items():
        pt = st["jobs"]["point"]
        rows += R.tier1_count_rows(name, pt["blocks"], pt["dates"])
        rows += [{"section": "counts", "stream": name, "measure": k, "value": float(v)}
                 for k, v in R.exit_problems(pt["blocks"], pt["dates"]).items()]
    conditional = R.p16_count_nonzero([r for r in rows if r["section"] == "tier1_count"])
    runs = [r for r in runs if not r.conditional or conditional]
    runs = sorted(runs, key=lambda r: (r.plan != "TS",))
    ts_cells: dict[tuple[str, str], dict] = {}
    pending_grid: dict[tuple[str, str, str], tuple[dict, float]] = {}
    for run in runs:
        s = T.settings_for(run.plan, run.corner, run.flip)
        name = R.stream_of(run)
        st = streams[name]
        for arm in UJ.ARMS:
            key = f"{run.name}|{arm}"
            got = resume.get(key)
            t0 = time.time()
            if got is None:
                job = st["jobs"][arm]
                chosen = UJ.start_choice(len(job["blocks"]), starts)
                blocks, point_ref, a11 = R.arm_inputs(st["jobs"]["point"], job, s, arm)
                cjob, kw = R.cell_job(job, s, blocks)
                cell = R.run_cell(name, arm, off, cjob, s, chosen, kw, point_ref, direct=True)
                outs = R.reading_outs(cell, name, arm, off, s)
                srows, table = UR.summary(name, arm, off, outs)
                probs = list(cell["problems"]) + UR.consistency_problems(srows, outs, key)
                head = {"run": run.name, "plan": run.plan, "stream": run.stream, "arm": arm, "corner": run.corner,
                        "flip": run.flip or "", "kind": run.kind, "request_rule": s.request or ""}
                crows = _tag(srows, **head)
                crows += _tag(R.account_count_rows(cell), **head)
                crows += _tag([{"section": "counts", "measure": f"a11_{k}", "value": float(v)} for k, v in a11.items()],
                              **head)
                crows += _tag([{"section": "identity_items_4_5", "measure": k, "value": float(v)}
                               for k, v in cell["checks"].items()], **head)
                recs = [o["rec"] for o in outs]
                got = {"rows": crows, "table": UR.rounded(table).assign(run=run.name), "problems": probs,
                       "recs": recs, "cell": R.compact(cell) if run.plan == "TS" else None, "head": head}
                if run.plan != "TS":
                    ts = ts_cells[(name, arm)]
                    got["rows"] += _tag(R.ledger_rows(cell, s, ts["cell"]) + R.differs_rows(cell, ts["cell"]), **head)
                    got["rows"] += _tag(R.paired_rows(recs, ts["recs"], coverage=coverage)
                                        + R.paired_scorecard_rows(recs, ts["recs"]), **head)
                    if run.kind == "corner" or run.flip == "price":
                        grows, at = R.grid_rows(cell, name, arm, off, s, ts["recs"])
                        got["rows"] += _tag(grows, **head)
                        if run.corner == T.STRICT and run.flip is None and run.plan != "LU":
                            other = T.price_ends(run.plan)[1]
                            pending_grid[(run.plan, name, arm)] = ({"price": other, "recs": at.get(other)}, other)
                        if run.flip == "price" and (run.plan, name, arm) in pending_grid:
                            mine, other = pending_grid.pop((run.plan, name, arm))
                            got["problems"] += [f"{key}: A-10 {p}" for p in
                                                R.grid_problems({other: mine["recs"]}, {"outs": outs}, other)]
                if not got["problems"]:
                    resume.put(key, got)
                del cell
            if run.plan == "TS":
                ts_cells[(name, arm)] = got
            problems += got["problems"]
            rows += got["rows"]
            starts_parts.append(got["table"])
            print(f"timing: {run.name} {arm}: {time.time() - t0:.0f} s", flush=True)
            gc.collect()
    return rows, (pd.concat(starts_parts, ignore_index=True) if starts_parts else pd.DataFrame()), problems


# ------------------------------------------------------------------------------------------------ the ladder


def ladder_reading(streams: dict[str, dict[str, Any]], starts: int | None) -> tuple[list[dict], list[str]]:
    """10.1 item 7: 10, 25 and 50 % on TS-16 and P-16's eight corners, verdict arm, A-9's seed base 20261990."""
    import user_journey as UJ

    st = streams["p16"]
    job = st["jobs"]["verdict"]
    chosen = UJ.start_choice(len(job["blocks"]), starts)
    rows, problems = [], []
    cells = [("TS-16", T.settings_for("TS", "reference"))]
    cells += [(f"{p}-16-{c[0]}", T.settings_for(p, c)) for p in LADDER_PLANS for c in (T.STRICT, T.LENIENT)]
    for name, s in cells:
        blocks, point_ref, _ = R.arm_inputs(st["jobs"]["point"], job, s, "verdict")
        cjob, kw = R.cell_job(job, s, blocks, ladder=True)
        for resp_name in R.LADDER:
            resp = B.BY_NAME[resp_name]
            cell = R.run_cell("p16", "verdict", resp, cjob, s, chosen, kw, point_ref, direct=s.plan == "DT")
            outs = R.reading_outs(cell, "p16", "verdict", resp, s)
            srows, _t = UR.summary("p16", "verdict", resp, outs)
            problems += list(cell["problems"]) + UR.consistency_problems(srows, outs, f"{name} {resp_name}")
            rows += _tag(srows, run=name, plan=s.plan, stream="P-16", seed_base=R.F.LADDER_SEED)
            del cell
            gc.collect()
    return rows, problems


# ------------------------------------------------------------------------------------------------ the gate


def registered_gate(design: str, n_paths: int) -> dict[str, Any]:
    """The stream's registered gate call, made as `identity/gate_identity.py` makes it (P-16: seed 20261206 after its
    trades' hash; P-14: seed 20261131), with a hook factory so each call has its own sink; and TS's registered paths."""
    import a3_brk30 as B3
    import a3_brk30_cb20 as C3
    import atlas_a3 as A3
    import fv3d_lever_test as lt
    import portfolio_stage as ps
    import rc150_dev_test as P
    import rc_dev_test as D
    import rc_screen as S
    import score_fv3_grid as gf
    import stage2_identity as SI

    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result

    if design == "p16":
        sp = P.SPEC
        I, b = sp.build()
        t, days = b["cells"][sp.cell]["trades"], b["days"]
        if D.trades_hash(t) != sp.trades_sha256:
            raise SystemExit("REFUSED: P-16's trades are not its registered trades")
        seed, gap, budget, ref_file = SI.P16_SEED, C3.STRICT_GAP, C3.BUDGET, SI.P16_PATHS
    else:
        I = S.inputs()
        t, days = B3.cell_trades(I["L"])
        seed, gap, budget, ref_file = S.SEED, S.STRICT_GAP, S.BUDGET, S.P14_PATHS
    L = I["L"]
    cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
    keys = B3.rrs(t)
    _, e_by, lb_by, _, _ = A3.bounds(t, days, keys, cfg)
    blocks, n_used = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise SystemExit("REFUSED: the gate blocks hold a different number of trades")
    pcfg = fcfg["portfolio"]

    def hook_factory(label: str):
        sink: list[dict] = []
        inner = ps.composed_hook({"margin": float(pcfg["margin"]), "block_days": int(pcfg["block_days"])}, sink=sink)
        ps._label(inner, f"rd01_{design}_{label}")
        return lt.lever_hook(inner), sink

    hook, _ = hook_factory("unused")
    kw = A3.gate_kwargs(blocks, fcfg, tv, I["plan"], e_by, lb_by, hook, seed=seed, n_paths=int(n_paths),
                        horizon=int(fcfg["gate"]["campaign"]["horizon_days"]), capacity=B3.capacity(t, fcfg),
                        levels=(0.0,), rtp=False, one_at_a_time=gap, purchase_budget=budget)
    return {"blocks": kw.pop("blocks"), "kw": kw, "hook_factory": hook_factory,
            "ref": read_result(RESULTS_DIR / ref_file)}


def paired_paths(sink: list[dict], ref: pd.DataFrame, shift: str, n: int) -> list[dict]:
    """The plan's gate paths against TS's registered ones, path for path (same seeds), each PATH_COLS column."""
    import zero_edge_decomposition as zd

    a = pd.DataFrame([r for r in sink if r["shift"] == shift and float(r["enforcement_p"]) == 0.0])
    b = ref[(ref["run"].astype(str) == "gate") & (ref["shift"].astype(str) == shift)
            & np.isclose(ref["enforcement_p"].astype(float), 0.0)].sort_values("path").head(n)
    if a.empty or len(b) != len(a):
        return [{"section": "gate_paired", "shift": shift, "measure": "paths", "stat": "unpaired", "value": float(len(a))}]
    a = a.sort_values("path").reset_index(drop=True)
    b = b.reset_index(drop=True)
    out = []
    for c in zd.PATH_COLS:
        x, y = pd.to_numeric(a[c], errors="coerce").to_numpy(float), pd.to_numeric(b[c], errors="coerce").to_numpy(float)
        d = x - y
        out += [{"section": "gate_paired", "shift": shift, "measure": c, "stat": "plan_mean", "value": float(np.nanmean(x))},
                {"section": "gate_paired", "shift": shift, "measure": c, "stat": "ts_mean", "value": float(np.nanmean(y))},
                {"section": "gate_paired", "shift": shift, "measure": c, "stat": "mean_diff", "value": float(np.nanmean(d))},
                {"section": "gate_paired", "shift": shift, "measure": c, "stat": "share_above",
                 "value": float(np.mean(d > 1e-9))}]
    return out


def gate_reading(n_paths: int, workers: int, gates: dict[str, dict] | None = None, run_gate=None
                 ) -> tuple[list[dict], pd.DataFrame, list[str]]:
    """10.1 item 8 on the 16 corners: the gate's rows and its paths, paired with TS's registered paths."""
    if run_gate is None:
        from extended.gate import run_gate
    rows, path_parts = [], []
    for design in ("p16", "p14"):
        g = (gates or {}).get(design) or registered_gate(design, n_paths)
        for plan in LADDER_PLANS:
            for corner in (T.STRICT, T.LENIENT):
                s = T.settings_for(plan, corner)
                w = 1 if plan == "QP" else int(workers)          # Quick Pay's shifted classes do not pickle
                grows, sinks, labels = R.gate_rows(g["blocks"], g["kw"], s, run_gate, workers=w,
                                                   hook_factory=g.get("hook_factory"))
                head = {"run": f"{plan}-{design[1:]}-{corner[0]}", "plan": plan, "stream": design, "corner": corner}
                rows += _tag(grows, **head)
                for label, sink in sinks.items():
                    if sink:
                        path_parts.append(pd.DataFrame(sink).assign(**head, call=label))
                    ref = g.get("ref")
                    if ref is not None and label in ("plan", "plan_point", "plan_bound"):
                        for shift in (("point", "lower_bound") if label == "plan" else
                                      (("point",) if label == "plan_point" else ("lower_bound",))):
                            rows += _tag(paired_paths(sink, ref, shift, int(n_paths)), **head)
                gc.collect()
    return rows, (pd.concat(path_parts, ignore_index=True) if path_parts else pd.DataFrame()), []


# ------------------------------------------------------------------------------------------------ main


def streams_of(rd: Path) -> dict[str, dict[str, Any]]:
    import user_beside_identity as UBI

    out = {}
    for name in ("p16", "p14"):
        jobs, c, probs = UBI.build(rd, name)
        if probs:
            raise SystemExit("REFUSED: " + "; ".join(probs[:4]))
        out[name] = {"jobs": jobs, "config": c}
    return out


def write_all(purpose: str, frames: list[pd.DataFrame], params: dict[str, Any], target: Path | None) -> list[str]:
    from extended.results import read_result, write_result

    names = RESULTS[purpose]
    wrote = []
    for nm, df in zip(names, frames):
        seed = {"firm_scorecard": SEEDS["coverage"], "firm_ladder_beside": SEEDS["ladder"],
                "firm_gate_beside": SEEDS["gate_p16"]}[purpose]
        p, m = write_result(df, nm, script=SCRIPT, seed=seed, parameters={**params, "file": nm}, results_dir=target,
                            prereg_id="RD-01",
                            description=f"RD-01 {purpose}: {READING}", exploratory=False, variant_count=1,
                            notes={"status": READING, "purpose": purpose})
        read_result(p)
        wrote += [p.name, m.name]
    return wrote


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--purpose", choices=R.PURPOSES, default="firm_scorecard")
    ap.add_argument("--identity-row", default=None)
    ap.add_argument("--repeat", default=None, help="E-NNN: a decision row naming the declaration (a further read)")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--no-resume", action="store_true")
    a = ap.parse_args(argv)
    bad = identity_row_problems(a.identity_row)
    if bad:
        print("REFUSED (RD-01 9.1): " + "; ".join(bad))
        return 3
    try:
        import stage2_identity as SI

        reader.authorise_engine_read(reader.CHOICE_START, reader.JUDGED_END, purpose=a.purpose,
                                     declaration=R.DECLARATION, repeat=a.repeat,
                                     files=SI.engine_files(VENDOR, bars=True),
                                     what=f"RD-01's {a.purpose} ({SCRIPT}): every start, every run, {PATHS} paths")
    except (reader.ReadRefused, FileNotFoundError) as exc:
        print(f"REFUSED: {exc}", flush=True)
        return 3
    from propedge import RESULTS_DIR

    t0 = time.time()
    commit = _commit()
    runs = list(T.RUNS)
    params = {"declaration": R.DECLARATION, "purpose": a.purpose, "identity_row": a.identity_row,
              "repeat": a.repeat, "commit_read": commit, "starts": "every start", "runs": [r.name for r in runs],
              "paths": PATHS, "workers": a.workers, "seeds": SEEDS, "code_blobs": code_blobs(),
              "conventions": CONVENTIONS}
    if a.purpose == "firm_gate_beside":
        rows, paths, probs = gate_reading(PATHS, a.workers)
        frames = [pd.DataFrame(rows), paths]
    else:
        streams = streams_of(RESULTS_DIR)
        if a.purpose == "firm_scorecard":
            resume = Resume(None if a.no_resume else RUNS_DIR / "resume" / f"rd01-scorecard_{commit}")
            rows, table, probs = scorecard_reading(streams, runs, None, resume=resume)
            frames = [pd.DataFrame(rows), table]
        else:
            rows, probs = ladder_reading(streams, None)
            frames = [pd.DataFrame(rows)]
    if probs:
        print("REFUSED (RD-01): nothing written -- " + "; ".join(probs[:12]), flush=True)
        return 3
    params["seconds"] = round(time.time() - t0, 1)
    wrote = write_all(a.purpose, frames, params, None)
    print(f"written: {wrote} ({time.time() - t0:.0f} s)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
