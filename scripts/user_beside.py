"""EXPLORATORY (Q-17, E-007 (e)): the user scorecard of P-14, P-15 and P-16 read beside the verdict under the firm's
responses -- the denial ladder, all-accounts forfeiture, the placement on, the binding Focused Trader models -- with
E-007 (e)'s extra measures and the operator's path measures (2026-11-15). Beside, never deciding: R* stays P-14 and
the verdict stays at 0 % denial with the placement off (E-008 (2)); nothing is chosen from these readings.

    python scripts/user_beside.py --check --starts 4                     # the pipeline on 4 starts a design and arm;
                                                                         #   identity lines and timing only; written
                                                                         #   to a temporary folder, removed
    python scripts/user_beside.py --check --starts 4 --designs p14 --responses off,denial_50,forfeit_10
    python scripts/run_clean.py --name user-beside --task Q-17 --hours 7 --mem-gb 2.2 -- python scripts/user_beside.py

**Identity first, refusing.** For each design, before any of its responses is run: with every response off, the
adapter's start rows equal `vendor/stage2/results/user_journey.csv`'s section `start` for that design and both arms
on every start, every column (`identity/user_beside_identity.py`'s comparison, E-010's); D-620's declaration, the
builders' identity rows; the vendored Focused Trader grid's binding models under the design's purchase budget equal
the declared ten. Then for every reading: every run's payouts and fees against the engine's own totals, the extra P
equal to the card's, the bankroll-limited P ordered below P, every share in [0, 1]. Any failure: nothing written.

**The readings** (`extended.user_beside.RESPONSES`, 19 a design and arm: off, denial 10/25/50, forfeiture 10/25/50,
the placement on with 0 and 3 warnings, ten Focused Trader models), every start of each design's window, both arms
(`verdict`, `point`): `results/user_beside.csv` (sections `identity`, `scorecard`, `extra`, `path`, `response`) and
`results/user_beside_starts.csv` (one row a start: the per-start values behind the `path` and `extra` sections, money
to the cent), each with its manifest through `extended.results` -- only from a clean checkout. Variant count: 3 designs
x 2 arms x 19 responses = 114 readings, exploratory, no family (they are beside, E-007 (e)).

A resume folder outside the checkout keyed by the code's commit keeps each finished reading (D-540's pattern), so a
run killed by the machine resumes where it stopped; `--no-resume` turns it off.
"""
from __future__ import annotations

import argparse
import os
import pickle
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for _p in (str(ROOT), str(ROOT / "identity")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from extended import RUNS_DIR, use_vendored_stage2  # noqa: E402

use_vendored_stage2()

import pandas as pd  # noqa: E402

import user_beside_identity as I  # noqa: E402

from extended import user_beside as B  # noqa: E402
from extended import user_readings as R  # noqa: E402

SCRIPT = "scripts/user_beside.py"
RESULT = "user_beside"
STARTS_RESULT = "user_beside_starts"
DESIGNS = ("p14", "p15", "p16")
TASK = "Q-17"
READING = ("EXPLORATORY (Q-17, E-007 (e)): beside the verdict, never deciding; R* stays P-14; the verdict stays at 0 % "
           "denial with the placement off (E-008 (2))")


def _commit() -> str:
    out = subprocess.run(["git", "rev-parse", "--short=12", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    return out.stdout.strip() or "nocommit"


class Resume:
    """Each finished reading kept outside the checkout (one pickle a design, arm and response), keyed by the commit."""

    def __init__(self, folder: Path | None):
        self.folder = folder
        if folder is not None:
            folder.mkdir(parents=True, exist_ok=True)

    def _p(self, key: str) -> Path:
        return self.folder / (key.replace("|", "__") + ".pkl")

    def get(self, key: str):
        if self.folder is None or not self._p(key).is_file():
            return None
        with self._p(key).open("rb") as f:
            return pickle.load(f)

    def put(self, key: str, value) -> None:
        if self.folder is None:
            return
        tmp = self._p(key).with_suffix(".tmp")
        with tmp.open("wb") as f:
            pickle.dump(value, f)
        os.replace(tmp, self._p(key))


def main(argv: list[str] | None = None) -> int:
    import gc

    import user_journey as UJ

    from extended.results import read_result, write_result
    from propedge import RESULTS_DIR
    from propedge.reporting.results import sha256_of

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="the pipeline on --starts starts; written to a temporary folder")
    ap.add_argument("--starts", type=int, default=None, help="with --check: this many starts a design and arm")
    ap.add_argument("--designs", default=None, help="with --check: a comma-separated subset of p14,p15,p16")
    ap.add_argument("--responses", default=None, help="with --check: a comma-separated subset of the responses")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--no-resume", action="store_true")
    a = ap.parse_args(argv)
    if not a.check and (a.starts is not None or a.designs is not None or a.responses is not None):
        print("REFUSED (Q-17): the readings run every start of every design and response; a smaller run is --check.")
        return 2
    designs = DESIGNS if a.designs is None else tuple(x for x in a.designs.split(",") if x)
    responses = B.RESPONSES if a.responses is None else tuple(B.BY_NAME[x] for x in a.responses.split(",") if x)
    if responses[0].name != "off" or any(d not in DESIGNS for d in designs):
        print("REFUSED (Q-17): the responses start with 'off' (the identity arm); designs are p14, p15, p16")
        return 2
    rd = RESULTS_DIR
    t_all = time.time()
    commit = _commit()
    resume = Resume(None if (a.check or a.no_resume) else RUNS_DIR / "resume" / f"user-beside_{commit}")
    ref = I.u1_reference(rd, designs)
    rows: list[dict] = []
    starts_parts: list[pd.DataFrame] = []
    timing: dict[str, dict] = {}
    idents: list[dict] = []

    def ident(design, arm, check, problems, compared=None):
        idents.append({"section": "identity", "design": design, "arm": arm, "response": "off", "measure": check,
                       "stat": "holds", "value": float(not problems), "n": compared if compared is not None else 0,
                       "note": "; ".join(problems[:4])})
        word = "HOLDS" if not problems else "FAILS"
        print(f"identity {word}: {design} {arm}: {check}" + (f" -- {'; '.join(problems[:6])}" if problems else ""),
              flush=True)
        return not problems

    for name in designs:
        t0 = time.time()
        print(f"the inputs of {name} (user_journey.BUILDERS)...", flush=True)
        jobs, c, bad = I.build(rd, name)
        for arm in UJ.ARMS:
            bad += [f"{arm}: the binding Focused Trader models under the budget {b} are not the declared ten"
                    for b in [jobs[arm]["args"]["path"].get("purchase_budget")] if tuple(B.binding_ftp(b)) != B.FTP_BINDING]
        if not ident(name, "", "D-620's declaration; the builder's identity rows; the vendored 0 %, placement-off "
                     "replay call; the binding Focused Trader models", bad):
            print("REFUSED (Q-17): nothing written")
            return 3
        print(f"timing: the inputs of {name}: {time.time() - t0:.0f} s", flush=True)
        for arm in UJ.ARMS:
            job = jobs[arm]
            chosen = UJ.start_choice(len(job["blocks"]), a.starts)
            for resp in responses:
                key = f"{name}|{arm}|{resp.name}"
                got = resume.get(key)
                if got is None:
                    t1 = time.time()
                    outs = B.run_starts(name, arm, resp, job, chosen, a.workers)
                    probs = []
                    if resp.name == "off":
                        probs = I.u1_compare_outs(name, c, arm, outs, ref, len(job["blocks"]), a.starts)
                    srows, table = R.summary(name, arm, resp, outs)
                    probs += R.consistency_problems(srows, outs, key)
                    got = {"rows": srows, "table": R.rounded(table), "problems": probs, "starts": len(outs),
                           "seconds": time.time() - t1,
                           "exact_checked": int(sum(1 for x in outs if x["checked"])),
                           "exact_differing": int(sum(len(x["differs"]) for x in outs))}
                    del outs
                    if not probs:
                        resume.put(key, got)
                what = ("the off arm's start rows equal results/user_journey.csv's (every column, "
                        f"{'every start' if a.starts is None else f'{a.starts} starts'}); " if resp.name == "off" else "")
                if not ident(name, arm, f"{resp.name}: {what}every run's payouts and fees against the engine's totals; "
                             "the extra P equal to the card's; the limits' P ordered; shares in [0, 1]",
                             got["problems"], got["starts"]):
                    print("REFUSED (Q-17): nothing written")
                    return 3
                rows += got["rows"]
                starts_parts.append(got["table"])
                timing[key] = {"starts": got["starts"], "seconds": round(got["seconds"], 1),
                               "starts_with_exact_runs": got["exact_checked"],
                               "exact_runs_differing": got["exact_differing"]}
                idents.append({"section": "identity", "design": name, "arm": arm, "response": resp.name,
                               "measure": "exact-length runs whose event days differ from the long replay's (read "
                               "from the exact run where made)", "stat": "count", "value": float(got["exact_differing"]),
                               "n": got["exact_checked"], "note": "every start" if resp.name == "off" else
                               f"the starts whose index is a multiple of {B.EXACT_EVERY}"})
                print(f"timing: {key}: {got['starts']} starts in {got['seconds']:.0f} s", flush=True)
        del jobs
        gc.collect()

    res = pd.DataFrame(idents + rows)
    res.insert(1, "reading", READING)
    st = pd.concat(starts_parts, ignore_index=True)
    seconds = time.time() - t_all
    n_read = len(designs) * len(UJ.ARMS) * len(responses)
    params = {"task": TASK, "decisions": ["E-007 (e)", "E-008 (2)", "E-013 (1)"], "designs": list(designs),
              "arms": list(UJ.ARMS), "responses": [r.as_dict() for r in responses],
              "starts": "every start of each design's development window" if a.starts is None else int(a.starts),
              "denial_seed": B.DENIAL_SEED, "start_seed": "lockstep.child_seed(20261920, 0, start_day): one per start, "
              "the same for every design, arm and response (common random numbers)",
              "seed_block": [B.SEED_BLOCK[0], B.SEED_BLOCK[-1]], "ftp_window_days": B.FTP_WINDOW,
              "ftp_budget": list(B.FTP_BUDGET), "exact_runs": {"off": "every start", "other responses":
                                                               f"every start index a multiple of {B.EXACT_EVERY}"},
              "blocks": {"all": "every start with the reading's horizon left",
                                                           "judged": "D-621 (4)(b)'s late block: starts from 2024"},
              "bankroll_limits": list(R.BANKROLL_LIMITS), "n_eff": f"Bartlett, lag {R.N_EFF_LAG}",
              "mdd": R.MDD_NOTE, "first_window": R.FIRST_WINDOW, "year_window": R.YEAR_WINDOW,
              "u1_reference": {"file": f"vendor/stage2/results/{I.SI.U1_FILE}", "sha256": sha256_of(rd / I.SI.U1_FILE)},
              "timing": timing, "workers": int(a.workers), "seconds": round(seconds, 1), "commit_read": commit,
              "conventions": {
                  "forfeiture": "the denied payout's close ends every live account (the engine's household rule, "
                                "raised by the denial), no pass waiting activates, nothing more is bought; every payout "
                                "whose cash would arrive after that close is taken out; cash arriving on it is kept",
                  "bankroll_limit": "a start counts as ahead at a month only if its cash spent before the first payout "
                                    "is within the limit (the replay's own path, not a re-run with a wallet)",
                  "path_measures": "each start's long replay (daily closes); the scorecard and extra sections read an "
                                   "exact-length run where its event days differed (user_journey.Views)",
                  "break_even": "the first close k >= 1 with cumulative net at or above zero (to 1e-6)",
                  "months": "sessions 21(m-1)+1 .. 21m are month m; a payout belongs to the month its cash arrives in"}}
    notes = {"status": READING, "variant_count_rule": "one reading a design, arm and response; exploratory, no family "
             "(beside, E-007 (e))", "selection": "none"}
    desc = ("EXPLORATORY (Q-17): P-14, P-15 and P-16's user scorecard (D-621), the extra measures of E-007 (e) and the "
            "operator's path measures, each design and arm under 19 firm responses (off, per-payout denial 10/25/50 %, "
            "all-accounts forfeiture 10/25/50 %, the placement on at 0 and 3 warnings, ten binding Focused Trader "
            "models) on every start of the development window; all starts and the judged block. Beside, never deciding.")

    def write(target: Path | None) -> list[str]:
        a_ = write_result(res, RESULT, script=SCRIPT, seed=B.DENIAL_SEED, parameters=params, results_dir=target,
                          description=desc, exploratory=True, variant_count=n_read, notes=notes)
        b_ = write_result(st, STARTS_RESULT, script=SCRIPT, seed=B.DENIAL_SEED, results_dir=target,
                          parameters={"result": f"{RESULT}.csv", "task": TASK, "columns": list(R.START_COLS),
                                      "money": "to the cent", "values": "each start's long replay; exact_runs_differing "
                                      "names the exact-length runs whose event days differed"},
                          description="EXPLORATORY (Q-17): one row a start, design, arm and response -- the per-start "
                                      "values behind user_beside.csv's extra and path sections.",
                          exploratory=True, variant_count=n_read, notes={"status": READING, "companion_of":
                                                                         f"{RESULT}.csv"})
        for p in (a_[0], b_[0]):
            read_result(p)                               # the manifest's hash verified on the way back
        return [p.name for p in (*a_, *b_)]

    if a.check:
        with tempfile.TemporaryDirectory(prefix="user_beside_check_") as td:
            wrote = write(Path(td))
        print(f"every identity holds; the pipeline ran on {'every' if a.starts is None else a.starts} start(s) of "
              f"{list(designs)} at both arms and {len(responses)} responses and wrote {wrote} ({len(res)} and "
              f"{len(st)} rows) to a temporary folder, since removed; nothing written to results/, no reading printed "
              f"(--check). {seconds:.0f} s", flush=True)
    else:
        wrote = write(None)
        print(f"written: {wrote} ({len(res)} and {len(st)} rows); {seconds:.0f} s", flush=True)
    mem = I.SI.peak_memory()
    if mem:
        print(mem, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
