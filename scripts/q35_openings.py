"""EXPLORATORY (Q-35, E-021 (2)): where P-14's and P-16's routed funded openings fall in U1's replay -- the marks, the
hours (CT), the day kinds and the shares inside 08:30-09:00 CT and on report days -- **a supply count, no outcome**.
Beside the registered verdicts; it selects nothing and creates no candidate.

    python scripts/q35_openings.py --check --starts 4                    # every identity and the pipeline on 4 starts a
                                                                         #   design and arm; identity lines and timing
                                                                         #   only; written to a temporary folder, removed
    python scripts/q35_openings.py --check --starts 4 --designs p14
    python scripts/run_clean.py --name q35-openings --task Q-35 --hours 1.5 --mem-gb 1.6 -- python scripts/q35_openings.py

**The replay** (`extended/openings.py`'s docstring): U1's (`vendor/stage2/scripts/user_journey.py`) as Q-17 adapted it
(`extended.user_beside`) -- every start of each design's development window, its long run of min(252, sessions left)
sessions, both arms (`verdict`, `point`), every firm response off -- with the engine's per-trade ledger on and nothing
else changed. A funded account's opening is its first executed trade (U2's `opening_trade`); it is placed on the
design's trade table (the session, the decision mark, the entry bar, the stop) and on the calendars (Stage 2's BLS
08:30 report days and FOMC days, the early-close calendar `config/calendar_early_closes.csv`, the weekday, the year).

**The designs' inputs** are built by the calls `user_journey.BUILDERS` makes -- P-14 as `build_d518` makes it
(`customer_journey.Inputs` and `replay_jobs`), P-16 as `build_p16` (`rc150_dev_test.build_cells`, `_rc_campaign`,
`_single_jobs`) -- here with the trade table those blocks were built from kept beside them (`build_design`); the
identities below hold the result to U1's file.

**Identities first, each refusing** (nothing is written if one fails; a failure prints the column and the count of
differing starts, never a value):

* the builder's own rows (P-16: its trades are the screen's cell and its registered content hash,
  `rc_dev_test.trade_problems`); the replay's arguments are the vendored 0 %, placement-off call
  (`user_beside.base_problems`), each arm;
* every block of each arm is the trade table's day -- the same trades in the same order: count, entry bars, sides
  (`TradeTable.block_problems`) -- so a ledger row's (historical day, trade index) names one row of the table;
* the trades' own day kind ('b') is Stage 2's report-day calendar exactly (`TradeTable.day_kind_problems`);
  the early-close calendar is E-029's pin (its LF sha256);
* **with the ledger on, every start's record equals U1's file** (`vendor/stage2/results/user_journey.csv`, section
  `start`, the design and arm, every column: money and the ratio to 1e-6, counts, days, dates and text exactly --
  E-010's comparison, `identity/user_beside_identity.py`'s `u1_compare_outs`), on every start of the window (U1 read no
  start from an exact-length run for P-14 or P-16, its manifest's `starts_read_from_an_exact_run`, so the long replay
  alone is U1's record); every run's payouts and fees against the engine's totals;
* the ledger against the engine's counts: each funded account's ledger rows number its trades, one opening for each
  account that traded, none before its first session, its calendar day its historical day + 1;
* the written frame (`openings.output_problems`): exactly `openings.COLUMNS`, none carrying an outcome word; shares in
  [0, 1]; every partition adds to its block; choice + judged = all.

**Writes** `results/q35_openings.csv` (EXPLORATORY; sections `identity`, `supply`, `mark`, `hour`, `entry_delay`,
`window`, `report_day`, `report_day_mark`, `fomc_day`, `calendar`, `weekday`, `year`, `stop`; per design, arm and block
-- choice, judged, all -- each group's openings and distinct historical trades with their shares) with its manifest
through `extended.results`, **only from a clean checkout** (refused at the start otherwise, exit 2). Seed: the replay
draws nothing (an as-happened replay; its path seed `user_beside.start_seed` feeds only the enforcement stream, unused
at 0 %); the manifest records `user_beside.DENIAL_SEED`, the seed of those path seeds. Variant count: 2 designs x 2
arms = 4 readings, exploratory, no family. Nothing outside the identity lines, the timing and the file's name is
printed: no count, no share.

**The read (Q-58, E-037).** Stage 2's engine opens the bars and the atlas itself, so before any of its work `main`
authorises the read through `extended.reader.authorise_engine_read`: purpose `registered_design`, declaration
**E-021** (the row that queued Q-35 and names P-14 and P-16), the designs run, the window 2020-01-02 to 2026-07-16 (the
tables are read whole), the files -- A1's events and days and A3's cached walk, the bars for P-16's walk. A refusal
ends the run (exit 3) before anything is read; the read is ledgered only inside a clean run, `--check` or not.
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

from extended import openings as O  # noqa: E402
from extended import reader  # noqa: E402
from extended import user_beside as B  # noqa: E402

SCRIPT = "scripts/q35_openings.py"
RESULT = "q35_openings"
TASK = "Q-35"
DESIGNS = ("p14", "p16")
DESIGN_IDS = {"p14": "P-14", "p16": "P-16"}
#: the decision row that admits the re-read (E-037): the row that queued Q-35, naming P-14 and P-16
READ_ROW = "E-021"
VENDOR = ROOT / "vendor" / "stage2"
CALENDAR = ROOT / "config" / "calendar_early_closes.csv"
#: E-029's pin of the early-close calendar (sha256 of its LF text)
CALENDAR_SHA256 = "72db4941f95320900aac29c6c047742da176cd9b55c925cc9275a18fb3e67fb2"
READING = ("EXPLORATORY (Q-35, E-021 (2)): where P-14's and P-16's routed funded openings fall in U1's replay -- a "
           "supply count, no outcome; beside the registered verdicts, selects nothing")


def refused(msg: str) -> str:
    return msg if msg.startswith("REFUSED") else f"REFUSED ({TASK}): {msg}"


def printable(problems: list[str]) -> list[str]:
    """A problem as printed: the column and the count, never a value (E-010's messages end with the first differing
    start's two values)."""
    return [p.split(" (first: start")[0] for p in problems]


def load_calendars() -> tuple[O.Calendars, dict]:
    """Stage 2's report and FOMC days (`openings.stage2_calendars`) and the early-close calendar (E-029's pin)."""
    from extended import calendar_early_closes as C

    got = reader.sha256_lf(CALENDAR)
    if got != CALENDAR_SHA256:
        raise O.OpeningsRefused(refused(f"config/calendar_early_closes.csv's sha256 {got[:12]} is not E-029's pin "
                                        f"{CALENDAR_SHA256[:12]}"))
    report, fomc, prov = O.stage2_calendars()
    cal = O.Calendars(report_days=report, fomc_days=fomc, calendar_kind=O.calendar_kinds(C.read_calendar(CALENDAR)))
    prov = {**prov, "early_closes": {"file": "config/calendar_early_closes.csv", "sha256_lf": CALENDAR_SHA256,
                                     "pinned": "E-029"}}
    return cal, prov


def build_design(rd: Path, name: str) -> tuple[dict, pd.DataFrame, dict, list[str]]:
    """(the two arms' jobs as `user_journey.BUILDERS` makes them, the trade table those blocks were built from --
    `openings.TRADE_COLUMNS` only --, U1's configuration definition, the builder's refusing identity failures)."""
    import user_journey as UJ

    defs = {c["config"]: c for c in UJ.CONFIG_DEFS}
    c = defs[name]
    if name == "p14":                    # user_journey.build_d518 for p14: D-518's own job builder
        import a3_brk30 as Bk
        import customer_journey as CJ

        cfgs = [x for x in CJ.CONFIGS if x["config"] == name]
        inp = CJ.Inputs(rd, cfgs)
        jobs = {}
        for kind, tk in CJ.replay_jobs(inp, cfgs[0], 1):
            if kind != "single":
                raise O.OpeningsRefused(refused(f"{name} is not a single-firm replay"))
            _, arm, blk, dates, args, _ = tk
            jobs[arm] = {"engine": "single", "blocks": blk, "dates": dates, "args": args,
                         "sub": inp.subscription(cfgs[0])}
        t, days = Bk.cell_trades(inp.p13_L)              # the trades P-13's and P-14's blocks are built from
        bad = [] if [str(d) for d in days] == [str(d) for d in jobs["verdict"]["dates"]] else \
            ["a3_brk30.cell_trades' day set is not the campaign's session dates"]
        table = t.loc[:, list(O.TRADE_COLUMNS)].copy()
        del t, inp
    elif name == "p16":                  # user_journey.build_p16 for p16: rc150_dev_test's cell
        import a3_brk30_cb20 as C
        import rc150_dev_test as R
        import rc_dev_test as D

        inp, b = R.build_cells()
        bad = D.trade_problems(rd, b, inp["L"]["fcfg"], spec=R.SPEC)
        camp = UJ._rc_campaign(inp, b, R.SPEC.cell, R.SPEC)
        jobs = UJ._single_jobs(camp, inp["plan"], C.BUDGET)
        table = b["cells"][R.SPEC.cell]["trades"].loc[:, list(O.TRADE_COLUMNS)].copy()
        del inp, b, camp
    else:
        raise O.OpeningsRefused(refused(f"the designs are {DESIGNS}, not {name!r}"))
    for arm in UJ.ARMS:
        bad += [f"{arm}: {p}" for p in B.base_problems(jobs[arm]["args"])]
    gc.collect()
    return jobs, table, c, bad


def main(argv: list[str] | None = None) -> int:
    from extended.results import clean_run_problem

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="the pipeline on --starts starts; written to a temporary folder")
    ap.add_argument("--starts", type=int, default=None, help="with --check: this many starts a design and arm")
    ap.add_argument("--designs", default=None, help="with --check: p14, p16 or both (comma-separated)")
    ap.add_argument("--workers", type=int, default=1)
    a = ap.parse_args(argv)
    if not a.check and (a.starts is not None or a.designs is not None):
        print(refused("the reading runs every start of both designs; a smaller run is --check."))
        return 2
    designs = DESIGNS if a.designs is None else tuple(x for x in a.designs.split(",") if x)
    if not designs or any(d not in DESIGNS for d in designs) or len(set(designs)) != len(designs):
        print(refused(f"the designs are {', '.join(DESIGNS)}; got {a.designs!r}"))
        return 2
    if not 1 <= int(a.workers) <= 2:
        print(refused("at most 2 workers (CLAUDE.md)."))
        return 2
    if not a.check:
        why = clean_run_problem()
        if why:
            print(refused(f"results/{RESULT}.csv is written only from a clean checkout -- {why}. python "
                          f"scripts/run_clean.py --name q35-openings --task {TASK} --hours 1.5 --mem-gb 1.6 -- python "
                          f"{SCRIPT}"))
            return 2
    try:                                            # Q-58: the engine's read authorised (ledgered in a clean run only)
        reader.authorise_engine_read(
            reader.CHOICE_START, reader.JUDGED_END, purpose=reader.REGISTERED_DESIGN, declaration=READ_ROW,
            design=[DESIGN_IDS[d] for d in designs],
            files=I.SI.engine_files(VENDOR, bars=any(d in I.SI.U1_WALKED for d in designs)),
            what=f"{READ_ROW}'s reading ({SCRIPT}, {TASK}): where {', '.join(DESIGN_IDS[d] for d in designs)}'s funded "
                 "openings fall in U1's replay, both arms, "
                 + ("every start" if a.starts is None else f"{a.starts} starts") + (" (--check)" if a.check else ""))
    except (reader.ReadRefused, FileNotFoundError) as exc:
        print(I.SI.refusal(exc), flush=True)
        return 3
    try:
        return _run(a, designs, t_all=time.time())
    except O.OpeningsRefused as exc:
        print(refused(str(exc)), flush=True)
        return 3


def _run(a: argparse.Namespace, designs: tuple[str, ...], *, t_all: float) -> int:
    """Everything after the read's authorisation: the calendars, U1's reference, each design's inputs, identities,
    replay and counts, the frame's checks and the write."""
    import user_journey as UJ

    from extended.results import read_result, write_result
    from propedge import RESULTS_DIR
    from propedge.reporting.results import sha256_of

    cal, cal_prov = load_calendars()
    rd = RESULTS_DIR
    ref = I.u1_reference(rd, designs)
    rows: list[dict] = []
    timing: dict[str, dict] = {}
    starts_read: dict[str, int] = {}

    def ident(design: str, arm: str, check: str, problems: list[str], compared: int) -> bool:
        word = "HOLDS" if not problems else "FAILS"
        shown = printable(problems)
        who = " ".join(x for x in (design, arm) if x) or "the reading"
        print(f"identity {word}: {who}: {check}" + (f" -- {'; '.join(shown[:6])}" if shown else ""), flush=True)
        if not problems:
            rows.append(O.identity_row(design, DESIGN_IDS.get(design, ""), arm, check, compared))
        return not problems

    for name in designs:
        t0 = time.time()
        print(f"the inputs of {name} (user_journey.BUILDERS' calls, the trade table kept)...", flush=True)
        jobs, trades, c, bad = build_design(rd, name)
        table = O.TradeTable(trades)
        del trades
        for arm in UJ.ARMS:
            bad += [f"{arm}: {p}" for p in table.block_problems(jobs[arm]["blocks"], jobs[arm]["dates"])]
        bad += table.day_kind_problems(cal.report_days)
        if not ident(name, "", "the builder's identity rows; the vendored 0 %, placement-off replay call; every block "
                     "of each arm is the trade table's day (count, entry bars, sides); the trades' day kind 'b' is "
                     "Stage 2's report-day calendar", bad, table.n):
            print(refused("nothing written"))
            return 3
        timing[f"{name}|inputs"] = {"seconds": round(time.time() - t0, 1)}
        print(f"timing: the inputs of {name}: {time.time() - t0:.0f} s", flush=True)
        for arm in UJ.ARMS:
            job = jobs[arm]
            chosen = UJ.start_choice(len(job["blocks"]), a.starts)
            t1 = time.time()
            outs = O.run_starts(name, arm, job, chosen, a.workers)
            probs = I.u1_compare_outs(name, c, arm, outs, ref, len(job["blocks"]), a.starts)
            probs += [p for x in outs for p in x["problems"]]
            if not ident(name, arm, "with the ledger on, every start's record equals results/user_journey.csv's start "
                         f"row ({'every start' if a.starts is None else f'{a.starts} starts'}, every column); every "
                         "run's payouts and fees against the engine's totals; the ledger against the engine's counts",
                         probs, len(outs)):
                print(refused("nothing written"))
                return 3
            placed = [O.place(op, job["dates"], table, cal) for x in outs for op in x["openings"]]
            rows += O.count_rows(placed, name, arm, DESIGN_IDS[name])
            starts_read[f"{name}|{arm}"] = len(outs)
            timing[f"{name}|{arm}"] = {"starts": len(outs), "seconds": round(time.time() - t1, 1)}
            print(f"timing: {name} {arm}: {len(outs)} starts in {time.time() - t1:.0f} s", flush=True)
            del outs, placed
            gc.collect()
        del jobs, table
        gc.collect()

    res = O.frame(rows, READING)
    bad = O.output_problems(res)
    if not ident("", "", "the written frame: exactly the reading's columns, none an outcome; shares in [0, 1]; every "
                 "partition adds to its block; choice + judged = all", bad, len(res)):
        print(refused("nothing written"))
        return 3
    res = O.frame(rows, READING)                    # with the frame's own identity row
    seconds = time.time() - t_all
    n_read = len(designs) * len(UJ.ARMS)
    params = {
        "task": TASK, "decisions": ["E-021 (2)", "E-037", "E-039 (1)", "E-029"], "designs": list(designs),
        "prereg": [DESIGN_IDS[d] for d in designs], "arms": list(UJ.ARMS),
        "starts": "every start of each design's development window" if a.starts is None else int(a.starts),
        "starts_read": starts_read,
        "replay": "U1's (vendor/stage2/scripts/user_journey.py) as Q-17 adapted it (extended.user_beside): each start's "
                  "long run of min(252, sessions left) sessions, every response off (ConductModel(rtp=False, "
                  "enforcement_p=0.0)), the engine's per-trade ledger on (record_trades=True), nothing else changed",
        "opening": "a funded account's first executed trade in the engine's ledger, first by (day, slot) -- U2's "
                   "opening_trade (vendor/stage2/scripts/u_xfa_day_budget.py)",
        "session": "dates[start + historical_day] (ReplayTable: calendar day = historical day + 1, checked); a trading "
                   "day runs 17:00 CT the evening before to 15:10 CT",
        "mark": "decision_slot_minutes, minutes after 17:00 CT (the trading-day clock), as HH:MM CT",
        "entry": "entry_t - 1: the open of the entry bar, whose END index on the clock is entry_t",
        "blocks": {"choice": [str(reader.CHOICE_START), str(reader.CHOICE_END)],
                   "judged": [str(reader.JUDGED_START), str(reader.JUDGED_END)], "all": "both",
                   "by": "the opening's own session date"},
        "windows": [w for w, _ in O.WINDOWS],
        "counted": {"openings": "each start's funded accounts' openings (the same historical trade opens accounts in "
                                "many starts' replays)",
                    "distinct_trades": "the distinct historical trades (date, index in the day) among them"},
        "calendars": cal_prov, "trade_columns": list(O.TRADE_COLUMNS), "opening_keys": list(O.OPENING_KEYS),
        "columns": list(O.COLUMNS), "outcome_words_refused": list(O.OUTCOME_WORDS),
        "seeds": {"recorded": B.DENIAL_SEED, "path_seed": "lockstep.child_seed(20261920, 0, start_day) "
                  "(extended.user_beside.start_seed): feeds only the enforcement stream, unused at 0 %",
                  "draws": "none: an as-happened replay (SharedDayDraws(replay=True)) draws no day"},
        "u1_reference": {"file": f"vendor/stage2/results/{I.SI.U1_FILE}", "sha256": sha256_of(rd / I.SI.U1_FILE)},
        "read": {"purpose": reader.REGISTERED_DESIGN, "declaration": READ_ROW},
        "timing": timing, "workers": int(a.workers), "seconds": round(seconds, 1)}
    notes = {"status": READING, "variant_count_rule": "one reading a design and arm; exploratory, no family",
             "selection": "none", "no_outcome": "no P&L, win, loss, exit, pass or payout is written or printed"}
    desc = ("EXPLORATORY (Q-35): where P-14's and P-16's routed funded openings fall in U1's replay (every start, both "
            "arms, every response off): the marks, hours (CT), entry delays, the shares inside 08:30-09:00 CT and on "
            "BLS report days, FOMC days, the early-close calendar's kinds, weekdays, years and stops, on the choice "
            "block, the judged block and both. A supply count: no outcome.")

    def write(target: Path | None) -> list[str]:
        csv, man = write_result(res, RESULT, script=SCRIPT, seed=B.DENIAL_SEED, parameters=params,
                                results_dir=target, description=desc, exploratory=True, variant_count=n_read,
                                notes=notes)
        read_result(csv)                             # the manifest's hash verified on the way back
        return [csv.name, man.name]

    if a.check:
        with tempfile.TemporaryDirectory(prefix="q35_openings_check_") as td:
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
