"""EXPLORATORY (D-564): a payout-policy screen of P-16's cell -- the buffer kept after a payout and the share of the
allowed payout requested -- on the 37.5-point news-safe coin, beside P-16's own take-the-maximum policy.

    python scripts/rc150_payout_screen.py --check --paths 4 --starts 6   # the identity and every cell at 4 paths, the
                                                                          #   journey on the first 6 starts; nothing
                                                                          #   written, no reading printed
    python scripts/rc150_payout_screen.py --workers 2                     # the screen (from a clean checkout, D-474)

**The cell** (P-16, D-544, D-547): `rc_s150_all` as `rc_width_screen.build` builds it at the 150-tick stop with D-533's
news-safe cut -- identity by its count against the screen's row and its content hash against
`rc150_dev_test.TRADES_SHA256` -- through P-14's engine call (`rc_screen.Runner`: the no-closure table, 20 Combine
purchases and resets in any 21 trading days, the strict one-at-a-time rule, five Topstep seats, the placement off, 0 %
denial), at the screen's seeds (campaign 20261131, coin 20261102), 500 paths, each run with its zero-edge twin.

**The grid** (D-564): the gate's `Protocol` with `keep_balance` in {0, 1000, 2000} and `payout_frac` in {1.0, 0.5}
(`dataclasses.replace`, nothing else touched); (0, 1.0) is P-16's own policy -- the reference, whose 500-path run must
reproduce `results/rc_width_screen.csv`'s `rc_s150_all` row (growth at the bound and point, required bankroll) or
nothing is written. Beside, never eligible: the reference with the request made between 4:00 and 5:00 PM CT
(`payout_timing.REQUEST_4_TO_5PM` -- the eligible day itself the request day; rests on the operator's first-hand answer
D-177, not on a help-centre page; the table was solved for the after-5 PM request day).

**What `keep_balance` means in the engine's units** (`lockstep.FundedAccount.trade_day`): the request is
`min(payout_frac x min(0.5 x B, cap), max(B - keep_balance, 0))` and is paid only when eligible and at least the
$125 minimum, where `B` is the funded account's balance ABOVE ITS STARTING BALANCE (an XFA starts at $0; its floor
trails from -$2,000 and locks at $0 on the first payout). So `keep_balance` = the dollars of profit balance left in the
account after the request -- the brief's "dollars of balance kept after the request", measured from the account's
start. Because the rule already caps a request at half the balance, a keep of K binds only while the balance is below
2K (K = 1000: below $2,000; K = 2000: below $4,000); `payout_frac` 0.5 halves the request, which then needs a balance of
at least $500 to reach the $125 minimum. The state table's paid leaves are keyed on the balance's distance to the payout
line (`line_gap`) and its grid stops at a $6,000 funded balance, so a larger kept balance falls on the band below the
cap -- a caveat on what the table "knows", read beside.

**Readings per cell:** growth on the required bankroll at the bound and the point, the required bankroll, the zero-edge
twin, trades taken a session, the gate rows' payout measures (days to the first payout, payouts per path, payouts a
month where the gate row holds them), D-518's journey readings on the verdict arm (`customer_journey.metrics` on the
replay, `rc_dev_test.journey_and_slices` with the cell's protocol), and D-509's four slice lines against FV3-C's
development configuration (FV3-C's slices read from `results/customer_slices.csv`, sha256 pinned, never rerun).

**Resume** (D-540's form): each finished cell's rows kept outside the checkout, keyed by the code's commit and the path
and start counts, so a run killed by the machine resumes; off in `--check`.

Writes `results/rc150_payout_screen.csv` with its manifest (EXPLORATORY; sections identity, cell, journey, slice_lines,
slices_summary); variants under `D-564:rc150_payout` (the six grid cells and the beside). Selects nothing: a policy that
beats P-16's would follow D-564's rule.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import replace
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

SCRIPT = "scripts/rc150_payout_screen.py"
DECISION = "D-564"
RESULT = "rc150_payout_screen"
FAMILY_ID = f"{DECISION}:rc150_payout"
CELL = "rc_s150_all"
STOP = 150
N_PATHS = S.N_PATHS
SCREEN_FILE = "rc_width_screen.csv"
KEEPS = (0.0, 1000.0, 2000.0)
FRACS = (1.0, 0.5)
REFERENCE = (0.0, 1.0)
BESIDE = "timing_4_to_5pm"
READING = ("EXPLORATORY (D-564): payout policy (buffer kept, share requested) on P-16's cell; beside, never a gate; "
           "selects nothing")
IDENT_COLS = (("growth_on_required", "lower_bound", "pf_growth_on_base_p50"),
              ("growth_on_required_point", "point", "pf_growth_on_base_p50"),
              ("required_p90", "lower_bound", "pf_required_p90"))
#: the gate-row payout measures carried when present
PAYOUT_COLS = ("median_days_to_first_payout", "median_payouts_per_path", "mean_payouts_per_path", "mean_payout_gross",
               "st_payouts_per_month_p50", "share_accounts_ever_paid", "share_payouts_exposed",
               "pf_break_even_denial_p50", "pf_net_p50")


def grid() -> list[tuple[float, float]]:
    """D-564's six (keep_balance, payout_frac) cells, the reference first."""
    cells = [(k, f) for k in KEEPS for f in FRACS]
    cells.sort(key=lambda c: c != REFERENCE)
    return cells


def label(keep: float, frac: float) -> str:
    return f"keep{int(keep)}_frac{frac:g}"


def fields(keep: float, frac: float) -> dict[str, float]:
    """The Protocol fields a cell replaces -- exactly these two."""
    return {"keep_balance": float(keep), "payout_frac": float(frac)}


def protocol_for(base, keep: float, frac: float):
    """The gate's Protocol with only the two payout fields replaced."""
    return replace(base, **fields(keep, frac))


# ------------------------------------------------------------------------------------------------ the resume cache


def _jsonable(x: Any) -> Any:
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, np.floating):
        return float(x)
    if isinstance(x, np.bool_):
        return bool(x)
    return str(x)


class Resume:
    """D-540's form: each finished cell's rows kept outside the checkout (an untracked file inside it would stamp the
    result -dirty), keyed by the code's commit and the counts; a rerun reads a finished cell instead of recomputing it
    (every run is deterministic at its seeds). Rows are stored as they read back from JSON."""

    def __init__(self, folder: Path | None, key: str):
        self.path = None if folder is None else Path(folder) / f"{RESULT}_{key}.jsonl"
        self.rows: dict[str, Any] = {}
        if self.path is not None and self.path.is_file():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    r = json.loads(line)
                    self.rows[r["_label"]] = r["payload"]
            print(f"  resume: {len(self.rows)} finished cell(s) read from {self.path}", flush=True)

    def get(self, key: str) -> Any:
        return self.rows.get(key)

    def put(self, key: str, payload: Any) -> Any:
        payload = json.loads(json.dumps(payload, default=_jsonable))
        self.rows[key] = payload
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps({"_label": key, "payload": payload}, default=_jsonable) + "\n")
        return payload


def cached(resume: "Resume | None", key: str, make) -> Any:
    hit = resume.get(key) if resume is not None else None
    if hit is not None:
        return hit
    out = make()
    return resume.put(key, out) if resume is not None else json.loads(json.dumps(out, default=_jsonable))


# ------------------------------------------------------------------------------------------------ the readings


def screen_row(rd: Path) -> pd.Series:
    from propedge.reporting.results import read_result

    d = read_result(Path(rd) / SCREEN_FILE)
    c = d[(d["section"].astype(str) == "cell") & (d["cell"].astype(str) == CELL)]
    if len(c) != 1:
        raise SystemExit(f"REFUSED ({DECISION}): {SCREEN_FILE} holds {len(c)} {CELL} rows.")
    return c.iloc[0]


def growth_problems(df: pd.DataFrame, row: pd.Series) -> list[str]:
    out = []
    for col, shift, src in IDENT_COLS:
        g = df[(df["shift"] == shift) & np.isclose(df["enforcement_p"].astype(float), 0.0)]
        mine, want = float(g[src].iloc[0]), float(row[col])
        if not np.isclose(mine, want, rtol=0, atol=1e-9):
            out.append(f"{col}: {mine!r} against {SCREEN_FILE}'s {want!r}")
    return out


def gate_reading(name: str, df: pd.DataFrame, twin: pd.DataFrame, sink: list[dict]) -> dict[str, Any]:
    import rc_reentry_screen as RS

    at = {s: df[(df["shift"] == s) & np.isclose(df["enforcement_p"].astype(float), 0.0)].iloc[0]
          for s in ("point", "lower_bound")}
    tw = twin[twin["shift"] == "point"].iloc[0]
    out = {"growth_on_required": float(at["lower_bound"]["pf_growth_on_base_p50"]),
           "growth_on_required_point": float(at["point"]["pf_growth_on_base_p50"]),
           "required_p90": float(at["lower_bound"]["pf_required_p90"]),
           "growth_zero_edge_twin": float(tw["pf_growth_on_base_p50"]),
           "trades_taken_per_session": RS.taken_per_session(sink, name, "lower_bound"),
           "trades_taken_per_session_point": RS.taken_per_session(sink, name, "point")}
    for c in PAYOUT_COLS:
        if c in at["lower_bound"].index:
            v = pd.to_numeric(pd.Series([at["lower_bound"][c]]), errors="coerce").iloc[0]
            out[c] = float(v) if pd.notna(v) else float("nan")
    return out


def fv3c_slices(rd: Path) -> pd.DataFrame:
    """FV3-C's development configuration's verdict slices, read from `customer_slices.csv` (sha256 pinned)."""
    import a3_brk30_cb20 as C
    import customer_slices as cs

    ref = C._pinned(Path(rd), C.SLICES_REFERENCE, C.SLICES_REFERENCE_SHA256)
    ref = ref[(ref["section"] == "slice") & (ref["arm"].astype(str) == "verdict") & (ref["config"].astype(str) == "fv3c")]
    return ref[list(cs.SLICE_COLS)].reset_index(drop=True)


def journey_and_lines(I: dict, t: pd.DataFrame, days: list[str], proto_fields: dict, name: str, fsl: pd.DataFrame,
                      workers: int, starts: int | None) -> dict[str, Any]:
    """D-518's journey on the verdict arm's replay and D-509's four lines against FV3-C, the cell's protocol replaced."""
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
    camp.kw["protocol"] = replace(camp.kw["protocol"], **proto_fields)
    units, rsl = D.journey_and_slices(camp, I["plan"], C.BUDGET, workers, starts, name)
    sub = float(camp.kw["rules"].subscription)
    journey = [{"section": "journey", "cell": name, "arm": "verdict", "source": "replay",
                "key": cj.metric_key(m["milestone"], m["measure"], m["at_days"]), **m} for m in cj.metrics(units, sub)]
    f = fsl if starts is None else fsl[fsl["start_day"].astype(int) < int(starts)]
    summ = cs.summarise(pd.concat([rsl, f], ignore_index=True))
    lines = [{**r, "cell": name} for r in C.slice_lines(summ, candidate=name, reference="fv3c")]
    sumrows = [{**r, "section": "slices_summary", "cell": name} for r in summ.to_dict("records")
               if str(r["config"]) == name]
    return {"journey": journey, "lines": lines, "summary": sumrows,
            "lines_hold": bool(all(r["holds"] for r in lines))}


# ------------------------------------------------------------------------------------------------ main


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    import rc150_dev_test as R150
    import rc_dev_test as D
    import rc_width_screen as W

    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.contract.payout_timing import REQUEST_4_TO_5PM
    from propedge.reporting.results import write_result
    from propedge.research import resolved_coin as rc

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="every cell at --paths; nothing written, no reading printed")
    ap.add_argument("--paths", type=int, default=N_PATHS)
    ap.add_argument("--starts", type=int, default=None, help="test seam (with --check): the journey's first starts")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--no-resume", action="store_true")
    ap.add_argument("--resume-dir", default=None)
    a = ap.parse_args(argv)
    if not a.check and (int(a.paths) != N_PATHS or a.starts is not None):
        print(f"REFUSED ({DECISION}): the reading runs {N_PATHS} paths and every start; a smaller run is --check.")
        return 2
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    t_all = time.time()
    srow = screen_row(RESULTS_DIR)
    print("P-14's inputs, the no-closure plan and the 37.5-point walk...", flush=True)
    I = S.inputs()
    b = W.build(I, (STOP,))
    c = b["cells"][CELL]
    t, days = c["trades"], b["days"]
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
    idents = [{"section": "identity", "cell": CELL, "holds": True,
               "check": f"the cell's trades as rc_width_screen.build builds them: {len(t)} candidates as the screen's "
                        f"{CELL} row; content hash {h} = rc150_dev_test.TRADES_SHA256"}]
    resume = None
    if not a.check and not a.no_resume:
        import subprocess

        commit = subprocess.run(["git", "rev-parse", "--short=12", "HEAD"], cwd=ROOT, capture_output=True,
                                text=True).stdout.strip() or "nocommit"
        folder = Path(a.resume_dir) if a.resume_dir else (
            Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "stage2-runs" / "resume")
        resume = Resume(folder, f"{commit}_{a.paths}_{'all' if a.starts is None else a.starts}")
    fsl = fv3c_slices(RESULTS_DIR)
    cells: list[dict] = []
    for keep, frac in grid() + [(None, None)]:
        beside = keep is None
        name = BESIDE if beside else label(keep, frac)
        pf = fields(*REFERENCE) if beside else fields(keep, frac)
        timing = REQUEST_4_TO_5PM if beside else None
        t0 = time.time()

        def make(name=name, pf=pf, timing=timing, beside=beside, keep=keep, frac=frac):
            R = S.Runner(I, a.workers)
            df = R.run(name, t, days, a.paths, protocol_fields=pf, payout_timing=timing)
            if (keep, frac) == REFERENCE and int(a.paths) == N_PATHS:
                prob = growth_problems(df, srow)
                if prob:
                    raise SystemExit(f"REFUSED ({DECISION}): the reference is not {SCREEN_FILE}'s {CELL} -- "
                                     + "; ".join(prob))
            tw = R.run(f"{name} twin", t, days, a.paths, twin=True, protocol_fields=pf, payout_timing=timing)
            row = {"section": "cell", "cell": name, "keep_balance": pf["keep_balance"],
                   "payout_frac": pf["payout_frac"], "payout_timing": timing or "after_5pm_ct (default)",
                   "eligible": not beside, "reference": (keep, frac) == REFERENCE, **gate_reading(name, df, tw, R.sink)}
            out = {"row": row, "journey": [], "lines": [], "summary": []}
            if not beside:                       # the beside timing changes the replay's request day: not replayed
                jl = journey_and_lines(I, t, days, pf, name, fsl, a.workers, a.starts)
                row["slice_lines_hold"] = jl["lines_hold"]
                out.update({k: jl[k] for k in ("journey", "lines", "summary")})
            return out

        res = cached(resume, name, make)
        cells.append(res)
        print(f"  {name}: done ({time.time() - t0:.0f} s)", flush=True)
        if (keep, frac) == REFERENCE and int(a.paths) == N_PATHS:
            print(f"identity HOLDS: the reference (keep 0, frac 1.0) at {N_PATHS} paths = {SCREEN_FILE}'s {CELL}",
                  flush=True)
            idents.append({"section": "identity", "cell": CELL, "holds": True,
                           "check": f"the reference policy (keep_balance 0, payout_frac 1.0 -- P-16's) at seed {S.SEED}, "
                                    f"{N_PATHS} paths, reproduces results/{SCREEN_FILE}'s {CELL} growth at the bound "
                                    "and point and its required bankroll"})
    if a.check:
        print(f"every cell ran at {a.paths} paths (journey on {a.starts or 'every'} starts); no reading printed; "
              f"nothing written (--check). {time.time() - t_all:.0f} s")
        return 0
    rows = [x["row"] for x in cells]
    ref = next(r for r in rows if r["reference"])
    for r in rows:
        r["growth_minus_reference"] = float(r["growth_on_required"]) - float(ref["growth_on_required"])
        r["reading"] = READING
    out = pd.DataFrame(idents + rows + [j for x in cells for j in x["journey"]]
                       + [j for x in cells for j in x["lines"]] + [j for x in cells for j in x["summary"]])
    out["reading"] = out["reading"].fillna(READING) if "reading" in out else READING
    seconds = time.time() - t_all
    counter = VariantCounter(path=rd / "variants.jsonl")
    for r in rows:
        counter.record(prereg_id=FAMILY_ID, seed=S.SEED, exploratory=True,
                       params={"study": "D-564's payout screen", "cell": CELL, "keep_balance": r["keep_balance"],
                               "payout_frac": r["payout_frac"], "payout_timing": r["payout_timing"],
                               "eligible": r["eligible"], "paths": N_PATHS},
                       label=f"D-564's payout screen: {r['cell']}" + ("" if r["eligible"] else " (beside, not eligible)"))
    write_result(out, RESULT, script=SCRIPT, seed=S.SEED, exploratory=True, results_dir=results_dir,
                 variant_count=len(rows),
                 parameters={"decision": DECISION, "cell": CELL, "stop_ticks": STOP, "keeps": list(KEEPS),
                             "fracs": list(FRACS), "reference": list(REFERENCE), "beside": BESIDE,
                             "keep_balance_units": "dollars of the funded account's balance above its starting balance "
                                                   "left after the request (lockstep.FundedAccount.trade_day: request = "
                                                   "min(frac x min(0.5 B, cap), max(B - keep, 0)))",
                             "seed": S.SEED, "coin_seed": rc.COIN_SEED, "paths": N_PATHS, "cell_trades_sha256": h,
                             "fv3c_slices": "results/customer_slices.csv (sha256 pinned), read, never rerun",
                             "workers": int(a.workers), "seconds": round(seconds, 1)},
                 notes={"status": READING,
                        "selection": "none here; D-564's rule decides whether a policy becomes a candidate"},
                 description="EXPLORATORY (D-564): P-16's cell (the 37.5-point news-safe coin, all-day) under six payout "
                             "policies -- a balance kept after the request of $0 / $1,000 / $2,000 and the full or half "
                             "allowed request -- each with its zero-edge twin, D-518's journey and D-509's slice lines; the "
                             "4-5 PM request beside, not eligible.")
    show = ["cell", "growth_on_required", "growth_on_required_point", "required_p90", "growth_zero_edge_twin",
            "trades_taken_per_session", "median_days_to_first_payout", "slice_lines_hold"]
    print(pd.DataFrame(rows)[[c for c in show if c in pd.DataFrame(rows).columns]].to_string(index=False))
    print(f"written: {RESULT}.csv ({seconds:.0f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
