"""EXPLORATORY (D-599): a confirmation-feasibility study of P-16 -- how often a window of 63, 126, 189 or 252
development sessions, run as P-16's confirmation would be run, passes the gate; selects nothing.

    python scripts/p16_confirm_feasibility.py --check              # the walk on every development day, the
                                                                   #   declaration, the cell's content hash, every
                                                                   #   identity's machinery and the first window of
                                                                   #   each length at 4 paths; no reading printed;
                                                                   #   nothing written
    python scripts/p16_confirm_feasibility.py --workers 1          # the reading (a clean checkout, D-474)

**The declaration** (DECISIONS.md's D-599 row) is pinned by the sha256 of its line and checked phrase by phrase
against this build's constants (`propedge.research.p16_confirm_feasibility.declaration_problems`, as `rc_stop_fine`
pins D-594), with the engine's constants as the earlier screens carry them (`rc_screen`, `rc150_dev_test`,
`rc_stop_walkforward`, `atlas_a3`). A difference refuses.

**The cell and the windows:** P-16's walk at 150 ticks on every development day (`rc_stop_walkforward.walk_stop`); its
day list (the one every P-16 identity runs on, 2020-01-02 .. 2026-07-16; the bar store's window guard and
`window_problems` both refuse a later day) cut into consecutive, non-overlapping windows of 63, 126, 189 and 252
sessions from the first session, a final partial block dropped (`p16_confirm_feasibility.windows`).

**Each window** (`window_row`): `rc_stop_walkforward.cell` on the window's sessions alone (its own mark cutoff from its
own walks' kind columns) and `span_row` (its own pooled one-sided 0.05 bound over its 21-session blocks,
`a3_brk30.check_bounds`; P-14's engine call, `rc_screen.Runner`: v12's no-closure table, five Topstep seats, the
placement off, 0 % denial), campaign seed 20261131, 200 paths. Every offered R resolves by `atlas_a3.resolution` on the
table's offered R (0.25, 1, 1.5, 2, 2.5, 3), overall and in the window's worst calendar year. A window whose bound is
undefined (fewer than two 21-session blocks holding a trade at an R its trades carry) is recorded `too_short`, one whose
cutoff admits no mark `no_mark`; neither is run, neither passes.

**Identities, refusing** (D-599 (4)): (a) the cell on every development day has `rc_width_screen.csv`'s rc_s150_all
count and content hash `rc150_dev_test.TRADES_SHA256`; (b) `span_row` on the whole development history at 500 paths
reproduces `rc_width_screen.csv`'s rc_s150_all (growth on the required bankroll at the bound and point, the required
bankroll; `rc_stop_fine`'s tolerance) -- with the full window's era-rule bound (`atlas_a3.bounds`), the bound that row
was run at: on the whole history the era test flags, so the pooled `check_bounds` is not that row's bound (stated in
the identity row; e is the same under both); (c) `span_row` on 2020-2023 and on 2024-01-01 .. 2026-07-16 at 500 paths
reproduces `rc_stop_walkforward.csv`'s rc_s150_all_early / _late rows (the pooled bound, as there).

**Resume** (D-540, `rc_robust.Resume`): each finished window and identity run kept outside the checkout, keyed by the
commit and the path counts, labelled per window; `--no-resume`, `--resume-dir`; off in --check.

Writes `results/p16_confirm_feasibility.csv` (EXPLORATORY; sections declaration, identity, window, length) with its
manifest; `D-599:p16_confirm_feasibility`, readings, 0 variants (nothing is chosen; no variant recorded, as
`news_minute_exposure`'s readings).
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

import pandas as pd  # noqa: E402

import rc_robust as RR  # noqa: E402
import rc_screen as S  # noqa: E402
from propedge.research import p16_confirm_feasibility as P  # noqa: E402

SCRIPT = "scripts/p16_confirm_feasibility.py"
DECISION = P.DECISION
RESULT = P.RESULT
CHECK_PATHS = 4
CHECK_WINDOWS = 1
READING = ("EXPLORATORY (D-599): P-16's cell on consecutive development windows of 63, 126, 189 and 252 sessions, each "
           "run as its confirmation would be; optimistic (the cell was chosen on these sessions); selects nothing")
#: the columns of `span_row`'s output a window row keeps (renamed where the meaning is narrower here)
SPAN_KEEP = ("candidates", "candidates_per_day", "capacity", "trades_taken_per_session", "growth_on_required",
             "growth_on_required_point", "required_p90")


class Resume(RR.Resume):
    """`rc_robust.Resume` (D-540) under this study's own file name."""

    def __init__(self, folder: Path | None, key: str):
        import json

        self.path = None if folder is None else Path(folder) / f"{RESULT}_{key}.jsonl"
        self.rows = {}
        if self.path is not None and self.path.is_file():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    r = json.loads(line)
                    self.rows[r["_label"]] = r["row"]
            print(f"  resume: {len(self.rows)} finished run(s) read from {self.path}", flush=True)


_cached = RR._cached


# ------------------------------------------------------------------------------------------------ one window


def window_row(I: dict, W: dict, w: dict, n_paths: int, workers: int) -> dict[str, Any]:
    """One window run as P-16's confirmation would be: the cell on its sessions alone, its own bound, the pass rule."""
    import a3_brk30 as B
    import atlas_a3 as A
    import confirm_fv3 as cf
    import rc_stop_walkforward as WF

    days = list(w["days"])
    c = WF.cell(W, P.STOP, days)
    base = {"section": "window", "cell": P.CELL, "window": w["window"], "length": int(w["length"]),
            "index": int(w["index"]), "first": w["first"], "last": w["last"], "sessions": int(w["sessions"]),
            "blocks": int(w["blocks"]), "crosses_eras": bool(w["crosses_eras"]), "marks_offered": len(c["marks"]),
            "first_mark": c["first_mark"], "last_mark": c["last_mark"]}
    t = c["trades"]
    if t is None:
        return {**base, "status": P.NO_MARK, "candidates": 0, "passes": False,
                "fail_reason": "the window's cutoff admits no mark: nothing to run"}
    keys = B.rrs(t)
    short = P.bound_short(cf.edge_stats(t, keys, days, P.BLOCK_DAYS, None))
    if short:
        return {**base, "status": P.TOO_SHORT, "candidates": int(len(t)), "passes": False, "fail_reason": short}
    e_by, lb_by = B.check_bounds(t, days, keys)                    # the bound span_row runs at (recomputed for e)
    r = WF.span_row(S.Runner(I, workers), w["window"], "window", P.STOP, c, days, n_paths, W["offered_rr"])
    res, ok_res = A.resolution(t, W["offered_rr"])
    if bool(ok_res) != bool(r["every_r_resolves"]):
        raise SystemExit(f"REFUSED ({DECISION}): {w['window']}'s resolution is not span_row's.")
    passes, why = P.pass_rule(float(r["growth_on_required"]), bool(ok_res))
    return {**base, "status": P.RAN, **{k: r[k] for k in SPAN_KEEP}, "every_offered_r_resolves": bool(ok_res), **res,
            **P.shift_row(e_by, lb_by), "passes": bool(passes), "fail_reason": why}


def with_reading(out: pd.DataFrame) -> pd.DataFrame:
    """This study's READING as column 1 of every row (`rc_stop_fine.with_reading`'s rule, D-597)."""
    out = out.drop(columns=["reading"], errors="ignore")
    out.insert(1, "reading", READING)
    return out


# ------------------------------------------------------------------------------------------------ main


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="the walk, the declaration, the content hash, every "
                                                         "identity's machinery and a few windows at a few paths; "
                                                         "nothing read, nothing written")
    ap.add_argument("--paths", type=int, default=None, help=f"--check: every run's paths ({CHECK_PATHS})")
    ap.add_argument("--windows", type=int, default=None, help=f"--check: the first N windows of each length "
                                                              f"({CHECK_WINDOWS})")
    ap.add_argument("--lengths", type=int, nargs="+", default=None, help="--check: only these lengths")
    ap.add_argument("--no-identities", action="store_true", help="--check: skip the identity runs (timing a window)")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--no-resume", action="store_true", help="D-540: neither keep nor read finished runs' rows")
    ap.add_argument("--resume-dir", default=None, help="D-540: where finished runs' rows are kept (outside the checkout)")
    a = ap.parse_args(argv)
    if not a.check and (any(x is not None for x in (a.paths, a.windows, a.lengths)) or a.no_identities):
        print(f"REFUSED ({DECISION}): the reading runs every window of every length at {P.N_PATHS} paths and the "
              f"identities at {P.IDENT_PATHS}; a smaller run is --check (writes nothing).")
        return 2
    if not a.check and int(a.workers) != 1:
        print(f"REFUSED ({DECISION}): the reading runs at workers 1.")
        return 2

    import a3_brk30 as B
    import atlas_a3 as A
    import rc150_dev_test as R150
    import rc150_payout_screen as PS
    import rc_dev_test as D
    import rc_stop_walkforward as WF
    import zero_edge_decomposition as zd

    from propedge import RESULTS_DIR
    from propedge.data.windows import assert_readable
    from propedge.reporting.results import read_manifest, read_result, write_result
    from propedge.research import resolved_coin as rc

    full = not a.check
    n_paths = (a.paths or CHECK_PATHS) if a.check else P.N_PATHS
    id_paths = (a.paths or CHECK_PATHS) if a.check else P.IDENT_PATHS
    lengths = tuple(int(n) for n in (a.lengths or P.LENGTHS))
    if any(n not in P.LENGTHS for n in lengths):
        print(f"REFUSED ({DECISION}): the lengths are {list(P.LENGTHS)}.")
        return 2
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    t_all = time.time()
    timing: dict[str, float] = {}

    # ---- the declaration and the engine's constants
    decl = P.declaration()
    bad = P.declaration_problems(decl)
    fixed = {"campaign seed": (S.SEED, P.CAMPAIGN_SEED), "P-16's stop": (R150.STOP, P.STOP),
             "P-16's cell": (R150.CELL, P.CELL), "spans": ({k: tuple(v) for k, v in WF.SPANS.items()}, P.SPANS),
             "unresolved line": (A.UNRESOLVED_MAX, P.UNRESOLVED_MAX), "screen file": (PS.SCREEN_FILE, P.SCREEN_FILE),
             "coin seed": (rc.COIN_SEED, 20261102)}
    bad += [f"{k}: the engine's {v[0]!r} against D-599's {v[1]!r}" for k, v in fixed.items() if v[0] != v[1]]
    if bad:
        print(f"REFUSED ({DECISION}): the build is not D-599's declaration -- " + "; ".join(bad))
        return 2
    print(f"the declaration HOLDS: {DECISION}'s row (sha256 {decl['sha256'][:16]}); lengths {list(P.LENGTHS)}, "
          f"{P.N_PATHS} paths, identities at {P.IDENT_PATHS}", flush=True)

    # ---- the files the identities must reproduce (each read through its manifest)
    srow = PS.screen_row(RESULTS_DIR)
    wf_rows = read_result(RESULTS_DIR / P.WALKFORWARD_FILE)
    shas = {f: read_manifest(RESULTS_DIR / f).sha256 for f in (P.SCREEN_FILE, P.WALKFORWARD_FILE)}
    if shas[P.SCREEN_FILE] != R150.SCREEN_SHA256:
        print(f"REFUSED ({DECISION}): {P.SCREEN_FILE} is not the file P-16 was registered on "
              f"({shas[P.SCREEN_FILE][:16]} against {R150.SCREEN_SHA256[:16]})")
        return 2

    def wf_row(span: str) -> pd.Series:
        r = wf_rows[(wf_rows["section"].astype(str) == span) & (wf_rows["cell"].astype(str) == f"{P.CELL}_{span}")]
        if len(r) != 1:
            raise SystemExit(f"REFUSED ({DECISION}): {P.WALKFORWARD_FILE} holds {len(r)} {P.CELL}_{span} rows")
        return r.iloc[0]

    # ---- the inputs, the walk and the day list
    print("P-14's inputs and the no-closure plan...", flush=True)
    I = S.inputs()
    L = I["L"]
    fresh = L["fcfg"]["state_policy"]["fresh"]
    offered = tuple(sorted(float(R) for R in zd.policy_rrs(I["plan"])))
    eng = {"offered R": (offered, P.OFFERED_R), "fresh Combine R": (float(fresh["combine_rr"]), P.COMBINE_RR),
           "fresh funded R": (float(fresh["funded_rr"]), P.FUNDED_RR),
           "bound blocks": (int(L["cfg"]["bounds"]["block_days"]), P.BLOCK_DAYS),
           "eras": (tuple(tuple(int(y) for y in e) for e in L["cfg"]["bounds"]["eras"]), P.ERAS)}
    bad = [f"{k}: the engine's {v[0]!r} against D-599's {v[1]!r}" for k, v in eng.items() if v[0] != v[1]]
    if bad:
        print(f"REFUSED ({DECISION}): " + "; ".join(bad))
        return 2
    t0 = time.time()
    W = WF.walk_stop(I, P.STOP)
    days = list(W["days"])
    timing["walk"] = time.time() - t0
    bad = P.window_problems(days)
    if tuple(float(x) for x in W["offered_rr"]) != P.OFFERED_R:
        bad.append(f"the walk's offered R {W['offered_rr']} are not {P.OFFERED_R}")
    if bad:
        print(f"REFUSED ({DECISION}): " + "; ".join(bad))
        return 3
    assert_readable("NQ", days[0], days[-1], "development", what=f"{DECISION}'s windows")
    assert days[-1] <= P.DEV_LAST and days[0] == P.DEV_FIRST, (days[0], days[-1])
    windows = P.plan(days, lengths)
    print(f"  {len(days)} development sessions {days[0]} .. {days[-1]}; windows "
          + ", ".join(f"{n}: {sum(w['length'] == n for w in windows)} ({P.dropped(days, n)} dropped)" for n in lengths),
          flush=True)

    idents: list[dict] = []

    def ident(name: str, check: str) -> None:
        idents.append({"section": "identity", "identity": name, "holds": True, "check": check})
        print(f"identity ({name}) HOLDS: {check[:140]}", flush=True)

    # ---- identity (a): the cell on every development day is P-16's
    c_full = WF.cell(W, P.STOP, days)
    t_full = c_full["trades"]
    h = D.trades_hash(t_full)
    bad = []
    if int(len(t_full)) != int(srow["candidates"]):
        bad.append(f"{len(t_full)} candidates against the screen's {int(srow['candidates'])}")
    if h != R150.TRADES_SHA256:
        bad.append(f"content hash {h[:16]} against the pinned {R150.TRADES_SHA256[:16]}")
    if bad:
        print(f"REFUSED ({DECISION}): the cell is not P-16's {P.CELL} -- " + "; ".join(bad))
        return 3
    ident("a", f"the 150-tick cell (rc_stop_walkforward.cell on every development day): {len(t_full)} candidates as "
               f"{P.SCREEN_FILE}'s {P.CELL}; content hash {h} = rc150_dev_test.TRADES_SHA256 (P-16's)")

    resume = None
    if full and not a.no_resume:
        import subprocess

        commit = subprocess.run(["git", "rev-parse", "--short=12", "HEAD"], cwd=ROOT, capture_output=True,
                                text=True).stdout.strip() or "nocommit"
        folder = Path(a.resume_dir) if a.resume_dir else (
            Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "stage2-runs" / "resume")
        resume = Resume(folder, f"{commit}_{n_paths}_{id_paths}")

    # ---- identities (b) and (c): the span machinery reproduces the screen's row and D-551's span rows
    if not a.no_identities:
        t0 = time.time()
        keys = B.rrs(t_full)
        e_pool, lb_pool = B.check_bounds(t_full, days, keys)
        _, e_era, lb_era, _, flagged = A.bounds(t_full, days, keys, L["cfg"])
        if any(abs(float(e_pool[R]) - float(e_era[R])) > 0.0 for R in keys):
            print(f"REFUSED ({DECISION}): the pooled and the era rule's e differ on the whole history.")
            return 3
        lb_same = all(float(lb_pool[R]) == float(lb_era[R]) for R in keys)

        def make_whole():
            return WF.span_row(S.Runner(I, a.workers), f"{P.CELL}_whole", "whole", P.STOP, c_full, days, id_paths,
                               W["rr_grid"], bounds=(e_era, lb_era))

        row = _cached(resume, "identity whole", make_whole)
        if full:
            prob = P.row_problems(row, srow, what=P.SCREEN_FILE)
            if prob:
                print(f"REFUSED ({DECISION}): span_row on the whole history is not {P.SCREEN_FILE}'s {P.CELL} -- "
                      + "; ".join(prob))
                return 3
            ident("b", f"rc_stop_walkforward.span_row on every development day at {P.IDENT_PATHS} paths, seed "
                       f"{P.CAMPAIGN_SEED}, reproduces {P.SCREEN_FILE}'s {P.CELL} (growth on the required bankroll at "
                       "the bound and point, the required bankroll) at that row's bound, the full window's era rule "
                       f"(atlas_a3.bounds; eras flagged {bool(flagged)}, so the pooled check_bounds bound "
                       f"{'equals' if lb_same else 'differs from'} it there; e is the same under both)")
        timing["identity_whole"] = time.time() - t0
        for span, (lo, hi) in P.SPANS.items():
            t0 = time.time()
            sd = WF.span_days(days, lo, hi)

            def make_span(span=span, sd=sd):
                return WF.span_row(S.Runner(I, a.workers), f"{P.CELL}_{span}", span, P.STOP, WF.cell(W, P.STOP, sd),
                                   sd, id_paths, W["rr_grid"])

            row = _cached(resume, f"identity {span}", make_span)
            if full:
                prob = P.row_problems(row, wf_row(span), what=P.WALKFORWARD_FILE)
                if prob:
                    print(f"REFUSED ({DECISION}): span_row on {span} alone is not {P.WALKFORWARD_FILE}'s "
                          f"{P.CELL}_{span} -- " + "; ".join(prob))
                    return 3
            timing[f"identity_{span}"] = time.time() - t0
        if full:
            ident("c", f"rc_stop_walkforward.span_row on {P.SPANS['early'][0]} .. {P.SPANS['early'][1]} and on "
                       f"{P.SPANS['late'][0]} .. {P.SPANS['late'][1]} alone (each span's own cutoff and pooled bound, "
                       f"{P.IDENT_PATHS} paths) reproduces {P.WALKFORWARD_FILE}'s {P.CELL}_early / _late rows")
        else:
            print(f"identities (b), (c): span_row ran on the whole history (the era rule's bound) and on each span at "
                  f"{id_paths} paths; not compared on a --check (no reading printed)", flush=True)
    del t_full, c_full

    # ---- the windows
    if a.check:
        k = int(a.windows or CHECK_WINDOWS)
        windows = [w for n in lengths for w in [x for x in windows if x["length"] == n][:k]]
    rows: list[dict] = []
    for w in windows:
        t0 = time.time()
        label = f"window {w['window']} {w['first']} {w['last']}"
        r = _cached(resume, label, lambda w=w: window_row(I, W, w, n_paths, a.workers))
        rows.append(r)
        timing[w["window"]] = time.time() - t0
        print(f"  {w['window']} ({w['first']} .. {w['last']}, {w['sessions']} sessions): done "
              f"({timing[w['window']]:.0f} s) -- no reading printed", flush=True)
    del W

    seconds = time.time() - t_all
    if a.check:
        print("timings (s): " + ", ".join(f"{k} {v:.0f}" for k, v in timing.items()))
        print(f"--check done: the declaration, identity (a) on {len(days)} sessions, the identity machinery and "
              f"{len(rows)} window(s) at {n_paths} paths; no reading printed; nothing written. {seconds:.0f} s")
        return 0
    lens = P.aggregate(rows, P.LENGTHS, n_sessions=len(days))
    decl_row = {"section": "declaration", "holds": True,
                "check": f"DECISIONS.md's {DECISION} row sha256 {decl['sha256']} (LF line); every phrase and constant "
                         f"agrees; {', '.join(f'{k} sha256 {v}' for k, v in shas.items())}"}
    out = with_reading(pd.DataFrame([decl_row] + idents + [{k: v for k, v in r.items()} for r in rows] + lens))
    write_result(out, RESULT, script=SCRIPT, seed=P.CAMPAIGN_SEED, exploratory=True, results_dir=results_dir,
                 variant_count=P.N_VARIANTS,
                 parameters={"decision": DECISION, "family": P.FAMILY_ID, "declaration_sha256": decl["sha256"],
                             "cell": P.CELL, "stop_ticks": P.STOP, "lengths": list(P.LENGTHS),
                             "campaign_seed": P.CAMPAIGN_SEED, "coin_seed": rc.COIN_SEED, "paths": P.N_PATHS,
                             "identity_paths": P.IDENT_PATHS, "sessions": len(days), "first": days[0],
                             "last": days[-1], "offered_rr": list(P.OFFERED_R), "block_days": P.BLOCK_DAYS,
                             "bound": "each window its own pooled one-sided 0.05 bound over its 21-session blocks "
                                      "(a3_brk30.check_bounds, via rc_stop_walkforward.span_row)",
                             "pass_rule": "growth on the required bankroll at the bound > 0 and every offered R "
                                          "resolves (atlas_a3.resolution: <= 5 % overall and in the worst year)",
                             "trades_sha256": R150.TRADES_SHA256, "reference_files_sha256": shas,
                             "timing_seconds": {k: round(v, 1) for k, v in timing.items()},
                             "workers": int(a.workers), "seconds": round(seconds, 1)},
                 notes={"status": READING, "variant_count_rule": f"readings, 0 variants under {P.FAMILY_ID} "
                                                                 "(nothing is chosen; no variant recorded)",
                        "optimistic": "the windows are P-16's own development history, from which its cell was "
                                      "chosen: a lower bound on the window length needed, never a forecast"},
                 description="EXPLORATORY (D-599): P-16's 37.5-point news-safe coin on consecutive development "
                             "windows of 63, 126, 189 and 252 sessions, each run as its confirmation would be (its own "
                             "cutoff and bound, 200 paths); the share passing by length, the growths, the bound's "
                             "shift and the required bankroll; selects nothing.")
    pd.set_option("display.width", 250)
    show = ["length", "windows", "ran", "too_short", "passing", "share_passing", "growth_at_bound_median",
            "growth_at_bound_min", "growth_at_bound_max", "required_p90_median"]
    print(pd.DataFrame(lens)[show].to_string(index=False))
    print(f"written: {RESULT}.csv ({seconds:.0f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
