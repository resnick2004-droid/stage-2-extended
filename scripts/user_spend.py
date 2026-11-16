"""EXPLORATORY (Q-86; E-014, E-015): money spent and the return on spend, per start day, for P-14, P-15 and P-16 in U1's
replay -- the fees paid and payouts received at the first pass, the first payout, break-even and each month end 1-6,
the cash out of pocket before break-even, the return on spend at each month end, whether break-even was later lost,
the evaluations bought before the first pass -- with their spread over start days. Beside Q-44's readings and the
verdict; it selects nothing and creates no candidate.

    python scripts/user_spend.py --check --starts 4                     # every identity and the pipeline on 4 starts a
                                                                        #   design and arm; identity lines and timing
                                                                        #   only; written to a temporary folder, removed
    python scripts/user_spend.py --check --starts 4 --designs p14
    python scripts/run_clean.py --name user-spend --task Q-86 --hours 2 --mem-gb 2.2 -- python scripts/user_spend.py

**The replay** (`extended/user_spend.py`'s docstring): U1's (`vendor/stage2/scripts/user_journey.py`) as Q-17 adapted
it (`extended.user_beside`) -- every start of each design's development window, its long run of min(252, sessions
left) sessions, both arms (`verdict`, the cautious reading; `point`, as traded, beside), every firm response off (0 %
denial, the placement off) -- with the engine's day recorder on and nothing else changed. The designs' inputs are
U1's own builders' (`identity/user_beside_identity.py`'s `build`: `user_journey.BUILDERS`, P-15 by its pinned trades
hash), as Q-17's readings build them.

**Identities first, each refusing** (nothing is written if one fails; a failure prints the check, the column and the
count of differing starts, never a value):

* the builder's own rows; D-620's declaration (`u1_reference`); the replay's arguments are the vendored 0 %,
  placement-off call (`user_beside.base_problems`) and take the day recorder (`user_spend.spend_args`), each arm;
  Stage 2's judged block's first year is this reading's;
* **with the day recorder on, every start's record equals U1's file** (`vendor/stage2/results/user_journey.csv`,
  section `start`, the design and arm, every one of its 68 columns: money and the ratio to 1e-6, counts, days, dates
  and text exactly -- E-010's comparison, `identity/user_beside_identity.py`'s `u1_compare_outs`, as Q-35), on every
  start of the window; every run's payouts and fees against the engine's totals;
* **the day ledger against the engine** (`user_spend.ledger_problems`): the cash at every close, the totals, every
  subscription, rebill, activation, reset and payout day against the accounts' own records;
* **the money against U1's own money columns** for each start (`user_spend.u1_money_problems`): fees and net at every
  month end 1-12 inside the window, the cash spent before the first pass and payout, the first payout's cash, the pay
  days;
* the written frame (`user_spend.output_problems`): exactly the reading's columns; the summary is its start rows' by
  the writer's own code; shares in [0, 1]; percentiles in order.

**Writes** `results/user_spend.csv` (EXPLORATORY; sections `identity`, `start`, `summary`) with its manifest through
`extended.results`, **only from a clean checkout** (refused at the start otherwise, exit 2). Seed: the replay draws
nothing (an as-happened replay; its path seed `user_beside.start_seed` feeds only the enforcement stream, unused at
0 %); the manifest records `user_beside.DENIAL_SEED`, the seed of those path seeds. Variant count: 3 designs x 2 arms
= 6 readings, exploratory, no family. Nothing outside the identity lines, the timing and the file's name is printed.

**The read (Q-58, E-037).** Stage 2's engine opens the bars and the atlas itself, so before any of its work `main`
authorises the read through `extended.reader.authorise_engine_read`: purpose `registered_design`, declaration
`extended.user_spend.READ_ROW` (E-024, the row that merged Q-17 -- the replay this reading re-runs -- naming P-14,
P-15 and P-16), the designs run, the window 2020-01-02 to 2026-07-16 (the tables are read whole), the files -- A1's
events and days and A3's cached walk, the bars for P-15's and P-16's walks. A refusal ends the run (exit 3) before
anything is read; the read is ledgered only inside a clean run, `--check` or not.
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

import user_beside_identity as I  # noqa: E402

from extended import reader  # noqa: E402
from extended import user_beside as B  # noqa: E402
from extended import user_spend as US  # noqa: E402

SCRIPT = "scripts/user_spend.py"
RESULT = "user_spend"
TASK = "Q-86"
DESIGNS = US.DESIGNS
DESIGN_IDS = US.DESIGN_IDS
READ_ROW = US.READ_ROW
VENDOR = ROOT / "vendor" / "stage2"
CMD = (f"python scripts/run_clean.py --name user-spend --task {TASK} --hours 2 --mem-gb 2.2 -- python {SCRIPT}")


def refused(msg: str) -> str:
    return msg if msg.startswith("REFUSED") else f"REFUSED ({TASK}): {msg}"


def printable(problems: list[str]) -> list[str]:
    """A problem as printed: the check, the column and the count, never a value (E-010's messages end with the first
    differing start's two values)."""
    return [p.split(" (first: start")[0] for p in problems]


def main(argv: list[str] | None = None) -> int:
    from extended.results import clean_run_problem

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="the pipeline on --starts starts; written to a temporary folder")
    ap.add_argument("--starts", type=int, default=None, help="with --check: this many starts a design and arm")
    ap.add_argument("--designs", default=None, help="with --check: a comma-separated subset of p14,p15,p16")
    ap.add_argument("--workers", type=int, default=1)
    a = ap.parse_args(argv)
    if not a.check and (a.starts is not None or a.designs is not None):
        print(refused("the reading runs every start of the three designs; a smaller run is --check."))
        return 2
    designs = DESIGNS if a.designs is None else tuple(x for x in a.designs.split(",") if x)
    if not designs or any(d not in DESIGNS for d in designs) or len(set(designs)) != len(designs):
        print(refused(f"the designs are {', '.join(DESIGNS)}; got {a.designs!r}"))
        return 2
    designs = tuple(d for d in DESIGNS if d in designs)
    if not 1 <= int(a.workers) <= 2:
        print(refused("at most 2 workers (CLAUDE.md)."))
        return 2
    if not a.check:
        why = clean_run_problem()
        if why:
            print(refused(f"results/{RESULT}.csv is written only from a clean checkout -- {why}. {CMD}"))
            return 2
    try:                                            # Q-58: the engine's read authorised (ledgered in a clean run only)
        reader.authorise_engine_read(
            reader.CHOICE_START, reader.JUDGED_END, purpose=reader.REGISTERED_DESIGN, declaration=READ_ROW,
            design=[DESIGN_IDS[d] for d in designs],
            files=I.SI.engine_files(VENDOR, bars=any(d in I.SI.U1_WALKED for d in designs)),
            what=f"{READ_ROW}'s reading ({SCRIPT}, {TASK}): money spent and the return on spend of "
                 f"{', '.join(DESIGN_IDS[d] for d in designs)} in U1's replay, both arms, "
                 + ("every start" if a.starts is None else f"{a.starts} starts") + (" (--check)" if a.check else ""))
    except (reader.ReadRefused, FileNotFoundError) as exc:
        print(I.SI.refusal(exc), flush=True)
        return 3
    try:
        return _run(a, designs, t_all=time.time())
    except US.SpendRefused as exc:
        print(refused(str(exc)), flush=True)
        return 3


def _run(a: argparse.Namespace, designs: tuple[str, ...], *, t_all: float) -> int:
    """Everything after the read's authorisation: U1's reference, each design's inputs, identities, replay and money,
    the frame's checks and the write."""
    import user_journey as UJ

    from extended.results import read_result, write_result
    from propedge import RESULTS_DIR
    from propedge.reporting.results import sha256_of
    from propedge.research import u_select as S

    rd = RESULTS_DIR
    ref = I.u1_reference(rd, designs)
    idents: list[dict] = []
    tables = []
    summary: list[dict] = []
    timing: dict[str, dict] = {}
    starts_read: dict[str, int] = {}
    tols: dict[str, float] = {}

    def ident(design: str, arm: str, check: str, problems: list[str], compared: int) -> bool:
        word = "HOLDS" if not problems else "FAILS"
        shown = printable(problems)
        who = " ".join(x for x in (design, arm) if x) or "the reading"
        print(f"identity {word}: {who}: {check}" + (f" -- {'; '.join(shown[:6])}" if shown else ""), flush=True)
        if not problems:
            idents.append(US.identity_row(design, DESIGN_IDS.get(design, ""), arm, check, compared))
        return not problems

    if tuple(UJ.ARMS) != US.ARMS:
        print(refused(f"Stage 2's arms are {UJ.ARMS}, not this reading's {US.ARMS}; nothing written"))
        return 3
    st = ref["start"]
    for name in designs:
        t0 = time.time()
        print(f"the inputs of {name} (user_journey.BUILDERS)...", flush=True)
        jobs, c, bad = I.build(rd, name)
        for arm in US.ARMS:
            try:
                US.spend_args(jobs[arm]["args"])
            except (US.SpendRefused, ValueError) as exc:
                bad.append(f"{arm}: {exc}")
        if int(S.JUDGED_FIRST_YEAR) != US.JUDGED_FIRST_YEAR:
            bad.append(f"Stage 2's judged block starts in {S.JUDGED_FIRST_YEAR}, this reading's in "
                       f"{US.JUDGED_FIRST_YEAR}")
        if not ident(name, "", "D-620's declaration; the builder's identity rows; the vendored 0 %, placement-off "
                     "replay call with the day recorder on, each arm; the judged block's first year", bad, 2):
            print(refused("nothing written"))
            return 3
        timing[f"{name}|inputs"] = {"seconds": round(time.time() - t0, 1)}
        print(f"timing: the inputs of {name}: {time.time() - t0:.0f} s", flush=True)
        for arm in US.ARMS:
            job = jobs[arm]
            chosen = UJ.start_choice(len(job["blocks"]), a.starts)
            t1 = time.time()
            outs = US.run_starts(name, arm, job, chosen, a.workers)
            what = f"{name} {arm}"
            probs = I.u1_compare_outs(name, c, arm, outs, ref, len(job["blocks"]), a.starts)
            probs += US.ledger_summary(outs, what)
            rows = st[(st["config"].astype(str) == name) & (st["arm"].astype(str) == arm)].to_dict("records")
            tol = max([float(x["tol"]) for x in outs] or [US.TOL])
            probs += US.u1_money_problems({int(x["rec"]["start_day"]): x["money"] for x in outs}, rows, tol=tol,
                                          what=what)
            if not ident(name, arm, "with the day recorder on, every start's record equals results/user_journey.csv's "
                         f"start row ({'every start' if a.starts is None else f'{a.starts} starts'}, every column); "
                         "every run's payouts and fees against the engine's totals; the day ledger against the cash, "
                         "the totals and the accounts' records; the money against U1's own money columns",
                         probs, len(outs)):
                print(refused("nothing written"))
                return 3
            t = US.start_table(name, DESIGN_IDS[name], arm, outs)
            tables.append(t)
            summary += US.summary_rows(t)
            starts_read[f"{name}|{arm}"] = len(outs)
            tols[f"{name}|{arm}"] = tol
            timing[f"{name}|{arm}"] = {"starts": len(outs), "seconds": round(time.time() - t1, 1)}
            print(f"timing: {name} {arm}: {len(outs)} starts in {time.time() - t1:.0f} s", flush=True)
            del outs
            gc.collect()
        del jobs
        gc.collect()

    res = US.frame(idents, tables, summary, US.READING)
    bad = US.output_problems(res)
    if not ident("", "", "the written frame: exactly the reading's columns; the summary is its start rows' by the "
                 "writer's own code; shares in [0, 1]; the percentiles in order", bad, len(res)):
        print(refused("nothing written"))
        return 3
    res = US.frame(idents, tables, summary, US.READING)        # with the frame's own identity row
    seconds = time.time() - t_all
    n_read = len(designs) * len(US.ARMS)
    params = {
        "task": TASK, "decisions": ["E-014", "E-015", "E-024", "E-037"], "designs": list(designs),
        "prereg": [DESIGN_IDS[d] for d in designs], "arms": list(US.ARMS),
        "starts": "every start of each design's development window" if a.starts is None else int(a.starts),
        "starts_read": starts_read,
        "replay": "U1's (vendor/stage2/scripts/user_journey.py) as Q-17 adapted it (extended.user_beside): each start's "
                  "long run of min(252, sessions left) sessions, every response off (ConductModel(rtp=False, "
                  "enforcement_p=0.0)), the engine's day recorder on (record_days=True), nothing else changed",
        "conventions": {
            "money": "fees: every subscription, rebill, activation and reset fee paid; payouts: the cash arrived (net "
                     "of the firm's split and payout fee); both from the engine's day recorder, close by close",
            "at_an_event": "at the close of the session it happens on, every fee and payout of that session booked",
            "first_pass": "U1's first_pass: the first Combine pass close",
            "first_payout": "U1's first_payout: the first close cash arrived on",
            "break_even": "the first close k >= 1 with payouts received less fees paid at or above zero (to 1e-6)",
            "break_even_lost": "a close after the break-even close below zero (to 1e-6)",
            "spent_before_break_even": "U1's spent_before at the break-even close: the deepest net below zero over "
                                       "the closes before it",
            "month_end": "month m ends at close 21 m",
            "return_on_spend": "the net (payouts received less fees paid) at a month end over the fees paid by then",
            "evaluations_before_first_pass": "the Combines bought on a day before the first pass close (purchases "
                                             "happen at a close's end); resets counted apart",
            "rounding": "the start rows hold money to the cent; the summary is read before rounding"},
        "windows": {"first_pass": US.FIRST_WINDOW, "first_payout": US.FIRST_WINDOW, "break_even": US.YEAR_WINDOW,
                    "month_end": "21 m sessions", "source": "extended.user_readings (Q-44's)"},
        "blocks": {"all": "every start with the reading's window left",
                   "judged": f"the starts from {US.JUDGED_FIRST_YEAR} with the window left (D-621 (4)(b))"},
        "summary": {"stats": list(US.QUANTILES) + ["spread", "share_never"],
                    "spread": "p90 less p10", "share_never": "the share of the eligible starts not there inside the "
                    "window", "percentiles": "numpy linear; days to an event: an unreached start beyond, a percentile "
                    "beyond the window blank (extended.user_measures.days_quantile)"},
        "tolerance": {"by_design_arm": tols, "rule": "U1's 1e-6 plus 1,000 bookings' half-unit rounding at the "
                      "bankroll's magnitude (extended.user_spend.money_tol)"},
        "seeds": {"recorded": B.DENIAL_SEED, "path_seed": "lockstep.child_seed(20261920, 0, start_day) "
                  "(extended.user_beside.start_seed): feeds only the enforcement stream, unused at 0 %",
                  "draws": "none: an as-happened replay (SharedDayDraws(replay=True)) draws no day"},
        "u1_reference": {"file": f"vendor/stage2/results/{I.SI.U1_FILE}", "sha256": sha256_of(rd / I.SI.U1_FILE)},
        "read": {"purpose": reader.REGISTERED_DESIGN, "declaration": READ_ROW},
        "columns": list(US.COLUMNS), "timing": timing, "workers": int(a.workers), "seconds": round(seconds, 1)}
    notes = {"status": US.READING, "variant_count_rule": "one reading a design and arm; exploratory, no family",
             "selection": "none", "beside": "Q-44's readings (results/user_beside.csv): this file adds the money"}
    desc = ("EXPLORATORY (Q-86): P-14's, P-15's and P-16's money per start day in U1's replay (every start, both arms, "
            "every response off): the fees paid and payouts received at the first pass, the first payout, break-even "
            "and each month end 1-6, the cash out of pocket before break-even, the return on spend at each month end, "
            "break-even lost, the evaluations bought before the first pass; and their p10-p90, spread and share never there, on all start days and the judged "
            "block. Beside, never deciding.")

    def write(target: Path | None) -> list[str]:
        csv, man = write_result(res, RESULT, script=SCRIPT, seed=B.DENIAL_SEED, parameters=params,
                                results_dir=target, description=desc, exploratory=True, variant_count=n_read,
                                notes=notes)
        read_result(csv)                             # the manifest's hash verified on the way back
        return [csv.name, man.name]

    if a.check:
        with tempfile.TemporaryDirectory(prefix="user_spend_check_") as td:
            wrote = write(Path(td))
        print(f"every identity holds; the pipeline ran on {'every' if a.starts is None else a.starts} start(s) of "
              f"{list(designs)} at both arms and wrote {wrote} ({len(res)} rows) to a temporary folder, since removed; "
              f"nothing written to results/, no reading printed (--check). {seconds:.0f} s", flush=True)
    else:
        wrote = write(None)
        print(f"written: {wrote} ({len(res)} rows); {seconds:.0f} s", flush=True)
    mem = I.SI.peak_memory()
    if mem:
        print(mem, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
