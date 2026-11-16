"""EXPLORATORY and descriptive (D-607): the P&F catapult's contract-fit count -- step 2 of the research protocol, read
before any outcome. Can the pattern supply the contract's trades at point stops near P-16's 37.5 points, at a sensible
R? NQ's development one-minute bars (2020-01-01 to 2026-07-16), the boxes 2.5, 5, 7.5 and 10 points, reversal 3.

    python scripts/pf_fit.py --check            # 2020-01-02 .. 2020-03-31 (one roll): the identities and the setup
                                                #   counts only; nothing written
    python scripts/pf_fit.py --workers 1        # the count (a clean checkout, scripts/run_clean.py, D-474)

**The engine** is `propedge.research.pnf` (its docstring states every rule and reading); the rows and readings are
`propedge.research.pf_fit`'s. The bars are read once, through `propedge.data.bars.read_bars` with purpose
`development` (the window guard: a read past 2026-07-16 raises), and the chart runs over the whole span, restarting at
each roll.

**Identities first, refusing**: the span ends at or before 2026-07-16; every box is a whole number of ticks; D >= 5b on
every setup (the engine raises on a violation, D-607 (4)) and the retest reading's 8b / 9b ceiling; each catapult's T =
H(k) + b and D = (H(k) - L(k+1)) + 2b, each plain triple's entry R + b and D = (R - L(k-1)) + 2b; the readings nest;
the sums (the catapult = bull + bear; all = asia + london + us + the 17:00-18:00 CT hour); the restarts are the bars
whose contract differs from the previous bar's, and their days are the store manifest's rolls in the span; the
look-ahead: the first setups of each box, recomputed on the bars truncated after their trigger bar, are unchanged.

Writes `results/pf_fit.csv` (sections identity, definition, reading, year, beside) and `results/pf_fit_setups.csv` (one
row per setup), each with its manifest: EXPLORATORY and descriptive, no P&L, no outcome, no seed (deterministic). The
20 definitions D-607 (9) names (4 boxes x (2 x 2 catapult readings + 1 plain)) are recorded in `results/variants.jsonl`
under `D-607:pf_fit` (exploratory; seed 0, nominal: deterministic counts), to be counted in step 2's menu's N.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

if __name__ == "__main__":                 # one BLAS thread, before numpy loads (D-464 (5))
    for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from propedge.data.bars import manifest, read_bars, trading_days  # noqa: E402
from propedge.research import pf_fit as PF  # noqa: E402
from propedge.research import pnf  # noqa: E402

SCRIPT = "scripts/pf_fit.py"
DECISION = PF.DECISION
FAMILY_ID = PF.FAMILY_ID
CHECK_SPAN = ("2020-01-02", "2020-03-31")
LOOKAHEAD_SAMPLE = 10                      # per box: the first setups (by trigger), recomputed on truncated bars
READING = ("EXPLORATORY and descriptive (D-607): the P&F catapult's contract-fit count on NQ development bars -- supply, "
           "stop distance, target R and latency per box and reading; no outcome, no P&L, no seed; selects nothing")
SETUP_COLUMNS_DROPPED = ("alert_bar", "trigger_bar")     # positions in the read frame: not part of the written row


def load(start: str, end: str) -> pd.DataFrame:
    """The charted contract's bars for trading days `start` .. `end`, through the window guard (purpose development)."""
    if str(end) > PF.DEV_END:
        raise SystemExit(f"REFUSED ({DECISION}): the count reads development days only, to {PF.DEV_END}; not {end}")
    bars = read_bars(PF.MARKET, start, end, "development", what="P&F catapult contract fit (D-607)")
    bars = bars.sort_values("ts", kind="stable").reset_index(drop=True)
    return bars[["ts", "day", "contract", "open", "high", "low", "close"]]


def sessions_of(start: str, end: str) -> list[str]:
    """The store's trading days in `start` .. `end` (no bar is read)."""
    return [str(d) for d in trading_days(PF.MARKET) if str(start) <= str(d) <= str(end)]


def lookahead_problems(bars: pd.DataFrame, box: float, rows: pd.DataFrame, k: int = LOOKAHEAD_SAMPLE) -> list[str]:
    """The first `k` setups (by trigger bar) recomputed on the bars truncated after their trigger bar."""
    out = []
    for _, r in rows.sort_values("trigger_bar", kind="stable").head(k).iterrows():
        cut = PF.setup_rows(bars.iloc[: int(r["trigger_bar"]) + 1], box)
        got = cut[(cut["kind"] == r["kind"]) & (cut["chart"] == r["chart"]) & (cut["column_k"] == r["column_k"])
                  & (cut["alert_bar"] == r["alert_bar"])]
        if len(got) != 1:
            out.append(f"box {box:g}: the {r['kind']} triggering {r['trigger_end_ct']} is not one setup on the truncated "
                       "bars")
            continue
        a, b = got.iloc[0], r
        diff = [c for c in rows.columns if not (pd.isna(a[c]) and pd.isna(b[c])) and a[c] != b[c]]
        if diff:
            out.append(f"box {box:g}: the {r['kind']} triggering {r['trigger_end_ct']} changes {diff} when truncated")
    return out


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help=f"{CHECK_SPAN[0]} .. {CHECK_SPAN[1]}: identities and setup "
                                                         "counts only; nothing written")
    ap.add_argument("--workers", type=int, default=1, help="accepted; the count is one pass (1 only)")
    a = ap.parse_args(argv)
    if a.workers != 1:
        print(f"REFUSED ({DECISION}): the count is one deterministic pass; --workers 1 only.")
        return 2

    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import write_result

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    t_all = time.time()
    start, end = CHECK_SPAN if a.check else (PF.DEV_START, PF.DEV_END)
    sessions = sessions_of(start, end)
    bars = load(start, end)
    if len(bars) and str(bars["day"].max()) > PF.DEV_END:
        print(f"REFUSED ({DECISION}): the read holds a day after {PF.DEV_END}.")
        return 3
    print(f"read {len(bars)} bars, {bars['day'].nunique()} trading days {bars['day'].min()} .. {bars['day'].max()} "
          f"(purpose development); {len(sessions)} sessions in the day list", flush=True)

    idents: list[dict] = []
    bad: list[str] = []

    def ident(check: str, problems: list[str]) -> None:
        idents.append({"section": "identity", "holds": not problems, "check": check,
                       "problems": "; ".join(problems)})
        print(("HOLDS: " if not problems else "FAILS: ") + check + ("" if not problems else " -- " + "; ".join(problems)),
              flush=True)
        bad.extend(problems)

    ident(f"the span {start} .. {end} ends at or before the development end {PF.DEV_END} (the window guard read it "
          "with purpose development)", [] if str(bars["day"].max() if len(bars) else start) <= PF.DEV_END else ["late"])
    ident(f"the boxes {list(pnf.BOXES)} points are {[pnf.box_ticks(b) for b in pnf.BOXES]} ticks, reversal "
          f"{pnf.REVERSAL}", [] if [pnf.box_ticks(b) for b in pnf.BOXES] == [10, 20, 30, 40] else ["grid"])
    con = bars["contract"].astype(str).to_numpy()
    changes = [i for i in range(1, len(con)) if con[i] != con[i - 1]]
    roll_days = sorted({str(bars["day"].iloc[i]) for i in changes})
    m = manifest(PF.MARKET)
    if m is not None and m.get("rolls") is not None:
        want = sorted(str(d) for d in m["rolls"] if start <= str(d) <= end and str(d) > str(bars["day"].min()))
        ident(f"the chart's restart days are the store manifest's rolls in the span ({len(want)})",
              [] if want == roll_days else [f"restarts on {roll_days}, the manifest's rolls {want}"])

    t0 = time.time()
    scans: dict[float, dict] = {}
    restart_days: dict[float, list[str]] = {}
    parts = []
    for box in pnf.BOXES:
        tb = time.time()
        res = pnf.scan(bars["high"].to_numpy(), bars["low"].to_numpy(), bars["close"].to_numpy(), con, box=box)
        rows = PF.setup_rows(bars, box, result=res)
        scans[box] = res
        restart_days[box] = [str(bars["day"].iloc[i]) for i in res["restarts"]]
        if res["restarts"] != changes:
            bad.append(f"box {box:g}: restarts {len(res['restarts'])} are not the {len(changes)} contract changes")
        la = lookahead_problems(bars, box, rows)
        ident(f"box {box:g}: the first {min(LOOKAHEAD_SAMPLE, len(rows))} setups are unchanged on the bars truncated "
              "after their trigger bar (look-ahead)", la)
        parts.append(rows)
        print(f"  box {box:g}: {len(res['columns'])} columns, {len(res['signals'])} signals, {len(rows)} setups, "
              f"{len(res['restarts'])} restarts ({time.time() - tb:.0f} s)", flush=True)
    rows = pd.concat(parts, ignore_index=True) if parts else PF.setup_rows(bars.iloc[:0], pnf.BOXES[0])
    ident(f"D >= 5b on every one of the {len(rows)} setups (the engine raises otherwise, D-607 (4)); under the retest "
          "reading D <= 8b (fixed 7-max) / 9b (breakout box); T = H(k) + b and D = (H(k) - L(k+1)) + 2b on every "
          "catapult; entry R + b and D = (R - L(k-1)) + 2b on every plain triple; the readings nest",
          PF.identity_problems(rows))
    ident(f"the chart restarts at every contract change ({len(changes)} in the span) on every box",
          [x for x in bad if "restarts" in x])

    # the sums, and the counts printed (no D, R or latency printed in --check)
    sums = []
    for box in pnf.BOXES:
        rb = rows[np.isclose(rows["box_points"].astype(float), box)]
        for choice in PF.CATAPULT_CHOICES:
            n_b = int(PF.choice_mask(rb, pnf.BULL_CATAPULT, choice).sum())
            n_s = int(PF.choice_mask(rb, pnf.BEAR_CATAPULT, choice).sum())
            if int(PF.choice_mask(rb, "catapult", choice).sum()) != n_b + n_s:
                sums.append(f"box {box:g} {choice}: catapult != bull + bear")
        win = rb["window"]
        if int(PF.in_window(win, "all").sum()) != int(sum((win == w).sum() for w in ("asia", "london", "us", "all"))):
            sums.append(f"box {box:g}: all != asia + london + us + the 17:00-18:00 CT hour")
    ident("the sums: catapult = bull + bear under every reading; all = asia + london + us + the 17:00-18:00 CT hour",
          sums)
    print(f"the scan: {time.time() - t0:.0f} s", flush=True)
    print("setup counts (in Topstep's hours / outside, 15:10-17:00 CT):")
    for box in pnf.BOXES:
        rb = rows[np.isclose(rows["box_points"].astype(float), box)]
        ih = rb["in_hours"].astype(bool).to_numpy()
        line = []
        for group, choice in [(g, c) for g in (pnf.BULL_CATAPULT, pnf.BEAR_CATAPULT) for c in PF.CATAPULT_CHOICES] + \
                [(pnf.TRIPLE_TOP, "plain"), (pnf.TRIPLE_BOTTOM, "plain")]:
            mk = PF.choice_mask(rb, group, choice)
            line.append(f"{group}/{choice} {int((mk & ih).sum())}/{int((mk & ~ih).sum())}")
        print(f"  box {box:g}: " + "; ".join(line))
    if bad:
        print(f"REFUSED ({DECISION}): an identity fails -- " + "; ".join(bad))
        return 3
    seconds = time.time() - t_all
    if a.check:
        print(f"--check done: {start} .. {end}; identities and setup counts only; nothing written. {seconds:.0f} s")
        return 0

    summ = PF.summary(rows, sessions)
    defs = [{"section": "definition", **d} for d in PF.definitions()]
    beside = PF.beside_rows(scans, restart_days)
    out = pd.concat([pd.DataFrame(idents), pd.DataFrame(defs), summ, pd.DataFrame(beside)], ignore_index=True)
    out.insert(1, "reading", READING)
    setups = rows.drop(columns=list(SETUP_COLUMNS_DROPPED))
    setups.insert(0, "reading", READING)
    params = {"decision": DECISION, "family": FAMILY_ID, "market": PF.MARKET, "first_day": start, "last_day": end,
              "purpose": "development", "sessions": len(sessions), "first_session": sessions[0] if sessions else None,
              "last_session": sessions[-1] if sessions else None, "bars_read": int(len(bars)),
              "bar_store_sha256": (m or {}).get("parquet_sha256"), "boxes_points": list(pnf.BOXES),
              "tick": pnf.TICK, "reversal": pnf.REVERSAL, "max7_fixed": f"H(k) <= R + {pnf.MAX7}b",
              "max7_beside": f"H(k) <= R + {pnf.MAX7_BREAKOUT_BOX}b", "pullback_fixed": "L(k+1) > L(k-1)",
              "pullback_beside": "L(k+1) > R", "count_columns": {"catapult": pnf.COUNT_COLUMNS_CATAPULT,
                                                                 "plain": pnf.COUNT_COLUMNS_PLAIN},
              "windows": {k: list(v) for k, v in PF.WINDOWS.items()}, "outside": f"[{PF.HOURS_END}, 1440]",
              "latency_minutes": PF.LATENCY_MIN, "stop_lines_points": list(PF.STOP_LINES),
              "quantiles": list(PF.QUANTILES), "choices": PF.CHOICE_TEXT, "restarts": len(changes),
              "setups": int(len(rows)), "seconds": round(seconds, 1)}
    notes = {"status": READING, "seed": "none: no randomness -- a deterministic count over the bars",
             "outcome": "none: no field of a setup reads a bar after its trigger bar (tests/test_pnf.py truncates)",
             "variant_count_rule": f"D-607 (9): 20 definitions under {FAMILY_ID}, counted in step 2's menu's N; "
                                   "nothing selected here"}
    write_result(out, PF.RESULT, script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 results_dir=results_dir, variant_count=len(defs), parameters=params, notes=notes,
                 description="EXPLORATORY and descriptive (D-607): the P&F catapult's contract-fit count on NQ "
                             "development bars 2020-01-01 to 2026-07-16 -- for boxes 2.5 / 5 / 7.5 / 10 points, the "
                             "bull and bear catapult under the 2 x 2 open-choice readings and the plain triple top / "
                             "bottom: setups per session by window and year, the stop distance D, the horizontal-count "
                             "target R, alert-to-trigger minutes and the missed share at L = 5; no outcome, no P&L.")
    write_result(setups, PF.RESULT_SETUPS, script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 results_dir=results_dir, variant_count=len(defs), parameters=params, notes=notes,
                 description="EXPLORATORY and descriptive (D-607): one row per P&F setup (catapults and plain triples, "
                             "four boxes) on NQ development bars -- dates, alert and trigger bars' ends (CT and clock "
                             "slot), window, R, entry T, stop, D, target and target R, the open choices' flags and the "
                             "latency measures; nothing after a trigger bar is read.")
    counter = VariantCounter(path=rd / "variants.jsonl")
    for d in PF.definitions():
        counter.record(prereg_id=FAMILY_ID, seed=0, exploratory=True,
                       params={"study": "D-607 P&F catapult contract fit", "box_points": d["box_points"],
                               "choice": d["choice"], "definition": d["definition"], "reversal": pnf.REVERSAL},
                       label=f"D-607's P&F contract fit: box {d['box_points']:g}, {d['choice']} (deterministic counts; "
                             "the seed is nominal; selects nothing)")
    print(f"written: {PF.RESULT}.csv ({len(out)} rows), {PF.RESULT_SETUPS}.csv ({len(setups)} setups); 20 definitions "
          f"recorded under {FAMILY_ID}; {seconds:.0f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
