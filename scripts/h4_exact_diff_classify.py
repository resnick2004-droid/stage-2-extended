"""Q-188b, B-2: classify H4-B's exact-run differences by kind on the 1 % audit sample's units (the red team's c2 note,
`docs/reviews/BUILD_H4_31c507e_c2_2026-11-26.md` B-2 remedy 1).

For one baseline, the search-year schedule is rebuilt exactly as H4-B builds it (`h4_rebaseline.build_bundle`), and for
every unit (start, seed index) of the audit sample (`h4_audit.is_sampled_unit`, `h4_sample` in part H4-U) the long run
(min(252, sessions left) closes) and the exact-length runs at every `EXACT_HORIZONS` h below it are re-made on each arm
named (default `off`), on the coin field H4-B drew (`h4b_coins`, part H4-B) -- the same keys, so the same records the
parts compared. Each (unit, arm, h) is classified by `h4_audit.classify_exact_difference`:

    event_day | arrival_cash | rel_only_at_h | rel_only_before_h | same

and written one row each (dates, closes, kinds and flags; no price, no dollar figure) to
`results/h4_exact_diffs_<baseline>[_tag].csv`, the tally by arm, horizon and kind in its manifest. Reads the bars
(heavy): one slot under `run.lock`, from a clean checkout:

    python scripts/run_clean.py --name h4-exact-p14 --hours 3 --mem-gb 2.5 --task Q-188 -- \\
        python scripts/h4_exact_diff_classify.py --baseline p14 --workers 2

The treatment of each kind is the lead's (B-2 remedy 2), not this script's. Lanes are independent (each unit's coin
keys are its own (start, seed index); the auditor's replay of 64 of the 128 seeds rests on the same property), so
re-making a sampled unit alone re-makes the record the part made for it. The script does not read the parts' units
files; its total over the sample is comparable to the parts' `exact_differs` only as a rate.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import os
import sys
import time
from pathlib import Path
from typing import Any, Sequence

if __name__ == "__main__":
    for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd  # noqa: E402

from extended import h4_audit as HA  # noqa: E402
from extended import journey_measures as JM  # noqa: E402
from extended import three_way_baseline as TB  # noqa: E402
from extended import three_way_seeds as S  # noqa: E402
from extended import wave42 as W42  # noqa: E402

SCRIPT = "scripts/h4_exact_diff_classify.py"
COLUMNS = ("baseline", "arm", "start", "start_date", "seed", "h", "kind", "first_pass_moved", "first_pay_moved",
           "arrival_day_moved", "arrival_cash_moved", "rel_differs", "rel_first_close", "rel_closes_differing",
           "rel_diff_over_1usd")


def sampled_units(n_sessions: int, seeds: Sequence[int], *, seed: Any = None, part: int | None = None
                  ) -> dict[int, list[int]]:
    """{start: [seed indices]} of H4's 1 % audit sample over every start and the J seeds (H4-U's own draw)."""
    out: dict[int, list[int]] = {}
    for s_idx in range(int(n_sessions)):
        got = [int(c) for c in seeds if HA.is_sampled_unit(s_idx, int(c), seed=seed, part=part)]
        if got:
            out[s_idx] = got
    return out


def classify_start(ctx: dict[str, Any], s_idx: int, lanes: Sequence[int]) -> list[dict[str, Any]]:
    """Every (arm, h) of one start's sampled lanes, classified (`HA.classify_exact_difference`)."""
    import scripts.h4_rebaseline as H4R

    dates, n_sess = ctx["dates"], len(ctx["dates"])
    obs = min(JM.YEAR, n_sess - int(s_idx))
    rows: list[dict[str, Any]] = []
    for arm_name, _tag, outcome_mode, arm_spec, _every in ctx["arms"]:
        kw = dict(seed=S.issue("h4b_coins"), part=S.PARTS["H4-B"], history=0, block_sessions=n_sess, dates=dates,
                  arm=arm_spec, outcome=outcome_mode, calendar=ctx["calendar"])
        rec = TB.simulate(ctx["blocks"], ctx["args"], ctx["facts"], int(s_idx), list(lanes), obs, **kw)
        for h in H4R.EXACT_HORIZONS:
            if h >= obs:
                continue
            rec_ex = TB.simulate(ctx["blocks"], ctx["args"], ctx["facts"], int(s_idx), list(lanes), int(h), **kw)
            for j, c_idx in enumerate(lanes):
                c = HA.classify_exact_difference(
                    int(h), first_pass_long=int(rec.first_pass[j]), first_pay_long=int(rec.first_pay[j]),
                    rel_long=rec.rel[j], arrivals_long=rec.arrivals[j], first_pass_exact=int(rec_ex.first_pass[j]),
                    first_pay_exact=int(rec_ex.first_pay[j]), rel_exact=rec_ex.rel[j],
                    arrivals_exact=rec_ex.arrivals[j])
                rows.append({"baseline": ctx["baseline"], "arm": arm_name, "start": int(s_idx),
                             "start_date": str(dates[s_idx]), "seed": int(c_idx), "h": int(h),
                             **{k: c[k] for k in COLUMNS if k in c}})
    return rows


_CTX: dict[str, Any] = {}


def _init(ctx: dict[str, Any]) -> None:
    import scripts.h4_rebaseline as H4R

    H4R._setup_vendor()
    _CTX.clear()
    _CTX.update(ctx)


def _work(job: tuple[int, list[int]]) -> list[dict[str, Any]]:
    return classify_start(_CTX, job[0], job[1])


def run(baseline: str, *, arms: Sequence[str] = ("off",), workers: int = 2, tag: str = "", starts_limit: int | None = None,
        root: Path = ROOT, results_dir: Path | None = None) -> dict[str, Any]:
    import scripts.h4_rebaseline as H4R
    from datetime import date

    from extended import RESULTS_DIR
    from extended import results as RES

    rdir = Path(results_dir) if results_dir is not None else RESULTS_DIR
    pre = HA.assert_h4_preconditions(root, require_clean=True, require_lock=True, require_disk=False)
    specs = tuple(a for a in H4R.ARM_SPECS if a[0] in set(arms))
    if len(specs) != len(set(arms)):
        raise ValueError(f"arms must be among {[a[0] for a in H4R.ARM_SPECS]}, got {list(arms)}")
    t0 = time.perf_counter()
    bundle = H4R.build_bundle(baseline, last_day=W42.SEARCH_LAST, root=root)
    HA.check_job_ends_search_window(bundle.dates, f"exact-diff classify {baseline}")
    jobs = sorted(sampled_units(len(bundle.dates), range(HA.H4_J)).items())
    if starts_limit is not None:
        jobs = jobs[: int(starts_limit)]
    ctx = {"baseline": baseline, "dates": bundle.dates, "blocks": bundle.blocks, "args": bundle.args,
           "facts": bundle.facts, "arms": specs, "calendar": frozenset(date.fromisoformat(d) for d in bundle.dates)}
    rows: list[dict[str, Any]] = []
    w = max(1, min(int(workers), H4R.H4B_MAX_WORKERS))
    if w == 1:
        _init(ctx)
        for jb in jobs:
            rows.extend(_work(jb))
    else:
        with cf.ProcessPoolExecutor(max_workers=w, initializer=_init, initargs=(ctx,)) as ex:
            for out in ex.map(_work, jobs, chunksize=8):
                rows.extend(out)
    tally: dict = HA.new_exact_tally()
    by_cell: dict[tuple[str, int, int], list[str]] = {}
    for r in rows:
        by_cell.setdefault((r["arm"], int(r["h"]), int(r["start"])), []).append(str(r["kind"]))
    for (arm, h, _s), kinds in sorted(by_cell.items()):
        HA.tally_exact(tally, arm, h, kinds)
    suf = f"_{tag}" if tag else ""
    params = {"part": f"exact-diff-classify{suf}", "baseline": baseline, "arms": list(arms),
              "exact_horizons": list(H4R.EXACT_HORIZONS), "sampled_starts": len(jobs),
              "sampled_units": int(sum(len(v) for _, v in jobs)), "tally": tally,
              "kinds": list(HA.EXACT_KINDS), "schedules_sha256": bundle.trades_sha256,
              "kept_trades_sha256": bundle.meta.get("kept_trades_sha256"),
              "seed_roles": ["h4b_coins", "h4_sample"] + (["h4s_schedule_side"] if baseline == "naive_coin" else []),
              "workers": w, "elapsed_s": round(time.perf_counter() - t0, 2), "preconditions": pre,
              "threads": H4R.thread_env()}
    csv_p, _ = RES.write_result(pd.DataFrame(rows, columns=list(COLUMNS)), f"h4_exact_diffs_{baseline}{suf}",
                                script=SCRIPT, seed=None, require_seed=False, exploratory=False, prereg_id="H4",
                                results_dir=rdir, parameters=params,
                                description=f"Q-188b B-2: H4-B's exact-run differences on the 1 % audit sample of "
                                            f"{baseline}, classified by kind (arm, horizon, unit); no price.")
    return {"csv": str(csv_p), "tally": tally, "units": params["sampled_units"]}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--baseline", required=True, choices=("naive_coin", "p14", "p15", "p16"))
    ap.add_argument("--arms", default="off", help="comma-separated arms (default: off)")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--tag", default="")
    a = ap.parse_args(argv)
    res = run(a.baseline, arms=[x.strip() for x in a.arms.split(",") if x.strip()], workers=a.workers, tag=a.tag)
    print(f"exact-diff classify {a.baseline}: {res['units']} sampled units -> {res['csv']}")
    for arm, by_h in res["tally"].items():
        for h, cell in sorted(by_h.items(), key=lambda kv: int(kv[0])):
            print(f"  {arm} h={h}: " + ", ".join(f"{k}={v}" for k, v in cell.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
