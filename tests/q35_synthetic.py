"""Q-35's synthetic check (`tests/test_q35_openings.py` runs it in a process of its own: the vendored tree goes on its
`sys.path`): the ledger-on replay of `extended.openings`, the openings and their placing, on a deterministic synthetic
campaign through the vendored engine -- no bar, no atlas, no generator (every value is a function of the day's and the
trade's index; the shared-day seed is `user_beside.SEED_BLOCK[1]`, as `identity/user_beside_identity.py --synthetic`
uses it, and a replay draws nothing with it).

    python tests/q35_synthetic.py <repository root>             # the mechanics; prints one JSON line
    python tests/q35_synthetic.py <repository root> pipeline    # scripts/q35_openings.py's main on this campaign

What it reports (the test asserts each):

* `_task` on four starts: no ledger problem; openings carry `OPENING_KEYS` only;
* the ledger changes nothing: each start's plain adapter replay (no ledger) has the same closes, funded accounts,
  payout days and trades, and the same U1 record (`user_beside.long_record`), as the ledger-on replay;
* each opening is its account's first ledger row by (day, slot), found by brute force; one per account that traded;
* the trade table (built from rows scrambled inside each day, outcome columns present) keeps `TRADE_COLUMNS` only,
  equals every block (and refuses a block whose entry order is changed), and its day kinds agree with the report-day
  calendar (and refuse a calendar missing a report day);
* every opening placed on its own planted trade: date, mark, entry minute, entry delay, report day;
* the frame of counts passes `output_problems`;
* `ledger_args` refuses arguments already carrying `record_trades`, and arguments with the placement on;
* Stage 2's calendars: the report days equal A1's BLS 08:30 files inside the window; the FOMC days hold every 2020 to
  2024 statement date inside it; nothing outside 2020-01-02 to 2026-07-16.

`pipeline`: `scripts/q35_openings.py`'s `main --check --starts 3` with this campaign standing in for both designs (the
build, the calendars and U1's file replaced; the read's authorisation recorded) -- what it prints, the frame it hands
`extended.results.write_result` (into a temporary folder), and the same run with the U1 comparison failing.
"""
import json, sys
from pathlib import Path

REPO = Path(sys.argv[1])
sys.path.insert(0, str(REPO))
from extended import use_vendored_stage2

use_vendored_stage2()
import numpy as np
import pandas as pd

from extended import openings as O
from extended import user_beside as B
from propedge.campaign.lockstep import ConductModel
from propedge.campaign.payout_method import payout_method_terms
from propedge.campaign.protocols import Protocol
from propedge.contract.adapter import rules_from_ledger
from propedge.contract.rules import load_rules
from propedge.outcomes.distribution import DayBlock
from propedge.research import user_journey as U

out = {}
# -- a deterministic synthetic campaign (no generator: every value from the day's and the trade's index)
days = [d.date().isoformat() for d in pd.bdate_range("2023-10-02", periods=90)
        if d.date().isoformat() not in ("2023-12-25", "2024-01-01")]
MARKS = (0, 130, 610, 920, 930, 945, 960, 1000)
blocks, trows = [], []
for i, d in enumerate(days):
    k = (i * 5) % 4
    ms = sorted({MARKS[(i + 3 * j) % len(MARKS)] for j in range(k)})
    delay = [5 if (i + j) % 3 == 0 else 0 for j in range(len(ms))]
    et = np.array([m + 1 + dl for m, dl in zip(ms, delay)], float)
    win = np.array([((i * 7 + j) % 5) < 3 for j in range(len(ms))])
    pnl = np.where(win, 1000.0, -500.0)
    sides = np.array([1 if (i + j) % 2 else -1 for j in range(len(ms))], int)
    blocks.append(DayBlock(pnl=pnl, risked=np.full(len(ms), 500.0), exit_reasons=tuple("bracket" for _ in ms),
                           entry_t=et, exit_t=et + 3.0, sides=sides))
    for j, m in enumerate(ms):
        trows.append({"date": d, "decision_slot_minutes": m, "entry_t": et[j], "stop_ticks": 150.0 if j % 2 else 100.0,
                      "side": "long" if sides[j] > 0 else "short", "day_kind": "b" if i % 9 == 0 else "n",
                      "r_1": float(pnl[j]) / 500.0, "pnl": float(pnl[j]), "exit_t": et[j] + 3.0})
trades = pd.DataFrame(trows[::-1]).sort_values("date", kind="stable")     # each day's rows reversed
rules = rules_from_ledger()
proto = Protocol(name="q35_synthetic", combine_rr=2.0, combine_risk=500.0, funded_rr=2.0, funded_risk=500.0,
                 trades_per_day=4, max_concurrent_accounts=5)
lag = int(payout_method_terms("aeropay", ledger=load_rules()).lag_days)
args = {"draws": {"protocol": proto, "mode": "rotation", "flip": None},
        "path": dict(edge=0.0, rules=rules, initial_bankroll=1e9, max_concurrent_accounts=5,
                     subscription=float(rules.subscription), billing_days=int(rules.billing_days),
                     activation=float(rules.activation), payout_lag_days=lag, max_concurrent_combines=5,
                     max_total_accounts=5, conduct=ConductModel(rtp=False, enforcement_p=0.0), combine_max_days=2000,
                     funded_horizon_days=100_000),
        "seed": B.SEED_BLOCK[1]}


def pipeline() -> dict:
    """`scripts/q35_openings.py`'s `main --check --starts 3` on this campaign standing in for both designs: the build,
    the calendars and U1's file replaced (the U1 comparison is the synthetic check's `record_same` above, and the
    real run's), the read's authorisation recorded; then the same with the U1 comparison failing."""
    import contextlib
    import importlib.util
    import io

    import extended.results as XR

    spec = importlib.util.spec_from_file_location("q35_script", REPO / "scripts" / "q35_openings.py")
    M = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(M)
    authorised, compared, saved = [], [], {}
    M.reader.authorise_engine_read = lambda *a, **k: authorised.append(k.get("design"))
    report = frozenset(d for i, d in enumerate(days) if i % 9 == 0)
    M.load_calendars = lambda: (O.Calendars(report, frozenset(), {}), {"synthetic": True})
    M.build_design = lambda rd, name: ({arm: {"engine": "single", "blocks": blocks, "dates": days, "args": args}
                                        for arm in ("verdict", "point")}, trades.copy(), {"config": name}, [])
    M.I.u1_reference = lambda rd, designs: {"designs": list(designs)}
    fail = []

    def compare(name, c, arm, outs, ref, n, starts):
        compared.append([name, arm, len(outs), n, starts])
        return list(fail)

    M.I.u1_compare_outs = compare
    real = XR.write_result

    def keep(df, name, **kw):
        saved["df"], saved["name"] = df.copy(), name
        saved["kw"] = {k: kw.get(k) for k in ("seed", "variant_count", "exploratory", "results_dir")}
        saved["parameters"] = sorted(kw["parameters"])
        return real(df, name, **kw)

    XR.write_result = keep
    got = {"authorised": authorised, "compared": compared}
    for case in ("holds", "fails"):
        if case == "fails":
            fail.append("p14 point first_payout_cash: 1 of 3 starts differ (first: start 5: 123.456 against the "
                        "file's 124.789)")
            saved.clear()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = M.main(["--check", "--starts", "3"])
        got[case] = {"rc": rc, "stdout": buf.getvalue(), "written": bool(saved)}
        if case == "holds" and saved:
            df = saved["df"]
            got["frame"] = {"name": saved["name"], "columns": list(df.columns), "rows": int(len(df)),
                            "sections": sorted(set(df["section"].astype(str))),
                            "identity_rows": int((df["section"] == "identity").sum()),
                            "designs": sorted(set(df.loc[df["section"] != "identity", "design"].astype(str))),
                            "problems": O.output_problems(df), **saved["kw"], "parameters": saved["parameters"],
                            "temp": "q35_openings_check_" in str(saved["kw"]["results_dir"])}
    return got


if len(sys.argv) > 2 and sys.argv[2] == "pipeline":
    print(json.dumps(pipeline(), default=str))
    raise SystemExit(0)

starts = [0, 7, 30, len(days) - 3]
res = O._task(("syn", "point", blocks, days, args, starts))
out["starts"] = len(res)
out["problems"] = [p for x in res for p in x["problems"]]
out["openings"] = sum(len(x["openings"]) for x in res)
out["opening_keys"] = sorted({k for x in res for o in x["openings"] for k in o})

# -- the ledger changes nothing: the plain adapter's replay (no ledger) gives the same path and the same U1 record
plain = B.response_args(args, B.BY_NAME["off"])
lagged = O.ledger_args(args)
same, rec_same, first_ok, n_funded_traded = [], [], [], 0


def pay(lp, obs):
    return U.payout_arrivals([(f.activation_day, lag, f.payout_days, f.payout_cash) for f in lp.funded], obs)


def totals(lp):
    return lp.path.total_fees, lp.path.total_payouts


for x, s in zip(res, starts):
    L = min(U.HORIZON, len(blocks) - s)
    p0 = B.replay(blocks[s:s + L], plain, B.start_seed(s))
    p1 = B.replay(blocks[s:s + L], lagged, B.start_seed(s))
    same.append(bool(np.array_equal(p0.path.cash_series, p1.path.cash_series)) and len(p0.trades) == 0
                and len(p1.trades) > 0 and [(f.index, f.payout_days, f.trades) for f in p0.funded]
                == [(f.index, f.payout_days, f.trades) for f in p1.funded])
    r0 = B.long_record(s, days[s], p0, pay, totals)
    rec_same.append(json.dumps(r0["rec"], sort_keys=True, default=str) == json.dumps(x["rec"], sort_keys=True,
                                                                                   default=str))
    # each opening is the account's first ledger row, found by brute force on the full rows
    for f in p1.funded:
        rows = sorted((r for r in p1.trades if r["kind"] == "funded" and r["index"] == f.index),
                      key=lambda r: (r["day"], r["slot"]))
        if rows:
            n_funded_traded += 1
            o = next(o for o in x["openings"] if o["account"] == f.index)
            first_ok.append((o["day"], o["slot"], o["historical_day"], o["trade_index"])
                            == (rows[0]["day"], rows[0]["slot"], rows[0]["historical_day"], rows[0]["trade_index"]))
out["path_same"] = same
out["record_same"] = rec_same
out["first_ok"] = all(first_ok) and len(first_ok) == out["openings"]
out["funded_traded"] = n_funded_traded

# -- the table: the blocks are its days; every opening placed on its own planted trade
table = O.TradeTable(trades)
out["table_columns"] = list(table.columns)
out["block_problems"] = table.block_problems(blocks, days)
report = frozenset(d for i, d in enumerate(days) if i % 9 == 0)
out["day_kind_problems"] = table.day_kind_problems(report)
dropped = next(d for d in sorted(report) if table.day(d) is not None)         # a report day with trades
out["day_kind_problems_wrong"] = table.day_kind_problems(report - {dropped})
bad_blocks = list(blocks)
k = next(i for i, b in enumerate(blocks) if len(b) >= 2)
b = blocks[k]
bad_blocks[k] = DayBlock(pnl=b.pnl, risked=b.risked, exit_reasons=b.exit_reasons, entry_t=b.entry_t[::-1].copy(),
                         exit_t=b.exit_t, sides=b.sides)
out["bad_block_problems"] = table.block_problems(bad_blocks, days)
cal = O.Calendars(report_days=report, fomc_days=frozenset(), calendar_kind={})
placed = [O.place(o, days, table, cal) for x in res for o in x["openings"]]
planted = {(r["date"], j): r for d, g in trades.groupby("date") for j, (_, r) in
           enumerate(g.sort_values("entry_t", kind="stable").iterrows())}
ok = []
for p, o in zip(placed, [o for x in res for o in x["openings"]]):
    d = days[o["start_day"] + o["historical_day"]]
    r = planted[(d, o["trade_index"])]
    blk = blocks[o["start_day"] + o["historical_day"]]
    ok.append(p["date"] == d and p["mark"] == int(r["decision_slot_minutes"])
              and p["entry_minute"] == int(r["entry_t"]) - 1 and float(blk.entry_t[o["trade_index"]]) == r["entry_t"]
              and p["entry_delay"] in (0, 5) and p["report_day"] == (d in report))
out["placed_ok"] = all(ok) and len(ok) == out["openings"]
out["blocks_seen"] = sorted({p["block"] for p in placed})
rows = []
for arm in ("verdict", "point"):
    rows += O.count_rows(placed, "syn", arm, "P-00")
df = O.frame(rows, "synthetic")
out["output_problems"] = O.output_problems(df)
out["n_rows"] = len(df)

# -- Stage 2's calendars: the BLS 08:30 files A1 names, and the FOMC statements, inside the window
rep, fomc, prov = O.stage2_calendars()
data = REPO / "vendor" / "stage2" / "data"
want = set()
for f in ("release_days_0830_2009_2025.csv", "release_days_0830_2026.csv"):
    want |= {d for d in pd.read_csv(data / f)["date"].astype(str) if "2020-01-02" <= d <= "2026-07-16"}
out["bls_equal"] = set(rep) == want and len(want) > 0
fs = pd.read_csv(REPO / "vendor" / "stage2" / "config" / "sources" / "fomc_statements_2020_2024q1.csv", comment="#")
fw = {d for d in fs["date"].astype(str) if "2020-01-02" <= d <= "2026-07-16"}
out["fomc_includes"] = fw <= set(fomc) and len(fw) > 0
out["calendar_late"] = max(set(rep) | set(fomc)) <= "2026-07-16" and min(set(rep) | set(fomc)) >= "2020-01-02"

# -- refusals: the ledger set twice; a response switched on (user_beside.response_args, through ledger_args)
refusals = {}
try:
    O.ledger_args({**args, "path": {**args["path"], "record_trades": False}})
    refusals["record_trades_twice"] = False
except O.OpeningsRefused:
    refusals["record_trades_twice"] = True
try:
    O.ledger_args({**args, "path": {**args["path"], "conduct": ConductModel(rtp=True, enforcement_p=0.0)}})
    refusals["placement_on"] = False
except ValueError:
    refusals["placement_on"] = True
out["refusals"] = refusals
print(json.dumps(out, default=str))
