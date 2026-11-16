"""Q-35 (E-021 (2)): where P-14's and P-16's routed funded openings fall -- `extended/openings.py` and
`scripts/q35_openings.py`, on synthetic inputs only (no bar, no atlas, no result file).

* **The counts** (in this process: `extended.openings` imports no engine): a hand-built trade table, calendars and eight
  openings placed by `place` and counted by `count_rows` give exactly the counts and shares worked out by hand in
  every section (supply, mark, hour, entry delay, the 08:30-09:00 windows by mark and by entry with the end exclusive
  and inclusive, report day and its marks, FOMC day, the early-close calendar, weekday, year, stop), on the choice
  block, the judged block and both, with the distinct historical trades beside the openings.
* **No outcome**: the ledger's rows lose every field but `OPENING_KEYS`; the trade table keeps `TRADE_COLUMNS` only;
  the written columns are `COLUMNS`, none carrying an outcome word; `output_problems` refuses a frame with a P&L,
  win or pass column, a tampered count, a block that does not add up; `count_rows` refuses a placed opening carrying
  anything else.
* **The engine, synthetic** (`tests/q35_synthetic.py`, a process of its own): the ledger-on replay changes no path and
  no U1 record; each opening is its account's first ledger row; the blocks are the table's days; each opening lands
  on its planted trade; Stage 2's calendars are A1's files. And the script's `main --check` on that campaign standing
  in for both designs: every identity line, the frame (no outcome column, every check) written to a temporary folder
  only, the manifest's seed and variant count, nothing printed but identity, timing and the file's name; with the U1
  comparison failing it is refused, nothing written, the differing values never printed.
* **The reader is used** (a child process on a temporary git tree at `<tmp>/runs/<name>`, as
  `tests/test_registered_design_reads.py` does for the other readings scripts): `main` authorises once, purpose
  `registered_design`, declaration E-021, the designs run, the whole window, the files the engine opens -- before any
  work (the first step after it replaced by a recorder that stops the run); outside a clean run nothing is ledgered
  and the declared run is refused before the authorisation (exit 2); inside a simulated clean run one ledger line a
  run; a decision log without E-021, or with an E-021 not naming P-16, is refused (exit 3) and nothing starts.
* (slow, not in the fast tier: it reads the real bars) `--check --starts 4` on both designs: every identity holds and
  the file is written to a temporary folder only.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import openings as O  # noqa: E402
from extended import reader as R  # noqa: E402

DATA = ROOT / "vendor" / "stage2" / "data"

# ------------------------------------------------------------------------------------------------ the hand-built case
#
# Four sessions: 2023-12-28 (Thu, choice, a report day), 2023-12-29 (Fri, choice), 2024-01-02 (Tue, judged, an FOMC
# day), 2024-01-03 (Wed, judged, an early close by the synthetic calendar). Marks on the trading-day clock (minutes after
# 17:00 CT): 925 = 08:25, 930 = 08:30, 955 = 08:55, 960 = 09:00, 965 = 09:05, 100 = 18:40, 0 = 17:00. `entry_t` is the
# entry bar's END index: mark + 1 enters at the mark; mark + 6 five minutes late.

DATES = ["2023-12-28", "2023-12-29", "2024-01-02", "2024-01-03"]
TRADES = [  # date, mark, entry_t, stop ticks -- listed out of entry order inside a day, with outcome columns beside
    ("2023-12-28", 960, 961.0, 150.0), ("2023-12-28", 925, 926.0, 150.0), ("2023-12-28", 930, 931.0, 150.0),
    ("2023-12-29", 955, 961.0, 150.0), ("2023-12-29", 100, 101.0, 100.0),
    ("2024-01-02", 965, 966.0, 150.0),
    ("2024-01-03", 0, 1.0, 150.0),
]
# per date, in entry order: 12-28: 0 = 08:25, 1 = 08:30, 2 = 09:00; 12-29: 0 = 18:40 (stop 100), 1 = 08:55 (+5 min);
# 01-02: 0 = 09:05; 01-03: 0 = 17:00
OPS = [  # (start_day, account, historical_day, trade_index): the date is DATES[start + historical day]
    (0, 0, 0, 0),   # op1 12-28 08:25
    (0, 1, 0, 1),   # op2 12-28 08:30
    (0, 5, 0, 1),   # op3 12-28 08:30 -- the same historical trade as op2
    (0, 2, 0, 2),   # op4 12-28 09:00
    (1, 0, 0, 1),   # op5 12-29 08:55, entry 09:00
    (1, 1, 0, 0),   # op6 12-29 18:40, stop 25 points
    (1, 2, 1, 0),   # op7 01-02 09:05
    (2, 0, 1, 0),   # op8 01-03 17:00
]
CAL = O.Calendars(report_days=frozenset({"2023-12-28"}), fomc_days=frozenset({"2024-01-02"}),
                  calendar_kind={"2024-01-03": "early_close", "2023-12-25": "holiday"})


def trade_frame() -> pd.DataFrame:
    rows = [{"date": d, "decision_slot_minutes": m, "entry_t": e, "stop_ticks": s, "side": "long",
             "day_kind": "b" if d == "2023-12-28" else "n", "r_3": 2.9, "pnl": 1.0, "exit_t": e + 30, "o_3": "t",
             "flat": False} for d, m, e, s in TRADES]
    return pd.DataFrame(rows)


def ops() -> list[dict[str, int]]:
    return [{"start_day": s, "account": a, "day": h + 1, "slot": 0, "historical_day": h, "trade_index": j}
            for s, a, h, j in OPS]


def placed() -> list[dict]:
    table = O.TradeTable(trade_frame())
    return [O.place(o, DATES, table, CAL) for o in ops()]


def counts(rows: list[dict], arm: str = "point") -> dict:
    """{(block, section, group): (openings, share, distinct, distinct share, block openings, block distinct)}"""
    return {(r["block"], r["section"], r["group"]): (r["openings"], r["share"], r["distinct_trades"],
                                                     r["distinct_share"], r["block_openings"], r["block_distinct"])
            for r in rows if r["arm"] == arm}


#: (section, group) -> (openings, distinct) on the block `all`: worked out by hand from OPS
WANT_ALL = {
    ("supply", O.EVERY): (8, 7),
    ("mark", "17:00"): (1, 1), ("mark", "18:40"): (1, 1), ("mark", "08:25"): (1, 1), ("mark", "08:30"): (2, 1),
    ("mark", "08:55"): (1, 1), ("mark", "09:00"): (1, 1), ("mark", "09:05"): (1, 1),
    ("hour", "17"): (1, 1), ("hour", "18"): (1, 1), ("hour", "08"): (4, 3), ("hour", "09"): (2, 2),
    ("entry_delay", "+0 min"): (7, 6), ("entry_delay", "+5 min"): (1, 1),
    ("window", "mark before 08:30 CT"): (3, 3), ("window", "mark in [08:30, 09:00) CT"): (3, 2),
    ("window", "mark at 09:00 CT"): (1, 1), ("window", "mark after 09:00 CT"): (1, 1),
    ("window", "mark in [08:30, 09:00] CT"): (4, 3), ("window", "entry in [08:30, 09:00) CT"): (2, 1),
    ("window", "entry in [08:30, 09:00] CT"): (4, 3),
    ("report_day", O.REPORT): (4, 3), ("report_day", O.NOT_REPORT): (4, 4),
    ("report_day_mark", "08:25"): (1, 1), ("report_day_mark", "08:30"): (2, 1), ("report_day_mark", "09:00"): (1, 1),
    ("fomc_day", O.FOMC): (1, 1), ("fomc_day", O.NOT_FOMC): (7, 6),
    ("calendar", O.NO_CALENDAR): (7, 6), ("calendar", "early_close"): (1, 1),
    ("weekday", "Tue"): (1, 1), ("weekday", "Wed"): (1, 1), ("weekday", "Thu"): (4, 3), ("weekday", "Fri"): (2, 2),
    ("year", "2023"): (6, 5), ("year", "2024"): (2, 2),
    ("stop", "25 points"): (1, 1), ("stop", "37.5 points"): (7, 6),
}
#: the choice block's (openings, distinct) where they are not all's; the judged block is all less choice
WANT_CHOICE = {
    ("supply", O.EVERY): (6, 5),
    ("mark", "17:00"): None, ("mark", "09:05"): None, ("hour", "17"): None, ("hour", "09"): (1, 1),
    ("entry_delay", "+0 min"): (5, 4),
    ("window", "mark before 08:30 CT"): (2, 2), ("window", "mark after 09:00 CT"): None,
    ("report_day", O.NOT_REPORT): (2, 2), ("fomc_day", O.FOMC): None, ("fomc_day", O.NOT_FOMC): (6, 5),
    ("calendar", O.NO_CALENDAR): (6, 5), ("calendar", "early_close"): None,
    ("weekday", "Tue"): None, ("weekday", "Wed"): None, ("year", "2024"): None, ("stop", "37.5 points"): (5, 4),
}


def want_block(block: str) -> dict:
    if block == "all":
        return dict(WANT_ALL)
    choice = {k: WANT_CHOICE.get(k, v) for k, v in WANT_ALL.items()}
    choice = {k: v for k, v in choice.items() if v is not None}
    if block == "choice":
        return choice
    judged = {}
    for k, (n, d) in WANT_ALL.items():
        c = choice.get(k, (0, 0))
        if n - c[0] > 0:
            judged[k] = (n - c[0], None)
    return judged


# ------------------------------------------------------------------------------------------------ the clock


def test_the_clock_is_stage2s_trading_day_clock_in_central_time():
    assert O.clock_ct(0) == "17:00" and O.clock_ct(100) == "18:40" and O.clock_ct(420) == "00:00"
    assert O.clock_ct(930) == "08:30" and O.clock_ct(960) == "09:00" and O.clock_ct(1330) == "15:10"
    assert (O.OPEN_0830, O.MARK_0900) == (930, 960)
    assert O.entry_minute(931.0) == 930 and O.entry_minute(1.0) == 0          # the entry bar's open: END index - 1


def test_the_blocks_are_the_readers_and_nothing_outside_them_is_placed():
    assert O.block_of("2020-01-02") == "choice" and O.block_of("2023-12-29") == "choice"
    assert O.block_of("2024-01-02") == "judged" and O.block_of("2026-07-16") == "judged"
    for d in ("2023-12-30", "2024-01-01", "2019-12-31"):
        with pytest.raises(O.OpeningsRefused, match="neither"):
            O.block_of(d)
    with pytest.raises(O.OpeningsRefused, match="confirmation window"):
        O.block_of("2026-07-17")


# ------------------------------------------------------------------------------------------------ the ledger


def _ledger_row(kind, index, day, slot, h, j, **extra):
    return {"day": day, "kind": kind, "index": index, "rel_day": 0, "slot": slot, "pnl": 123.0, "balance_before": 0.0,
            "balance_after": 123.0, "floor": -2000.0, "historical_day": h, "trade_index": j, "risk": 500.0,
            "u": 0.25, "mae": 1.0, "source": "strategy", **extra}


def test_an_opening_is_the_funded_accounts_first_ledger_row_and_keeps_where_and_when_only():
    rows = [_ledger_row("combine", 0, 2, 0, 1, 0),
            _ledger_row("funded", 0, 6, 1, 5, 3), _ledger_row("funded", 0, 6, 0, 5, 1),
            _ledger_row("funded", 0, 9, 0, 8, 0), _ledger_row("funded", 2, 11, 0, 10, 2)]
    got = O.openings_from_ledger(rows, start_day=7)
    assert got == [{"start_day": 7, "account": 0, "day": 6, "slot": 0, "historical_day": 5, "trade_index": 1},
                   {"start_day": 7, "account": 2, "day": 11, "slot": 0, "historical_day": 10, "trade_index": 2}]
    assert all(tuple(o) == O.OPENING_KEYS for o in got)
    with pytest.raises(O.OpeningsRefused, match="source"):
        O.openings_from_ledger([_ledger_row("funded", 0, 6, 0, 5, 1, source="flip")], 0)
    with pytest.raises(O.OpeningsRefused, match="historical day"):
        O.openings_from_ledger([{**_ledger_row("funded", 0, 6, 0, 5, 1), "historical_day": None}], 0)


def test_the_ledger_is_held_to_the_engines_counts():
    rows = [_ledger_row("funded", 0, 6, 0, 5, 1), _ledger_row("funded", 0, 7, 0, 6, 0)]
    funded = [SimpleNamespace(index=0, trades=2, activation_day=4), SimpleNamespace(index=1, trades=0,
                                                                                   activation_day=5)]
    ops_ = O.openings_from_ledger(rows, 0)
    assert O.ledger_problems(rows, funded, ops_) == []
    assert any("ledger rows" in p for p in O.ledger_problems(rows[:1], funded, O.openings_from_ledger(rows[:1], 0)))
    early = [SimpleNamespace(index=0, trades=2, activation_day=6), funded[1]]
    assert any("before its first session" in p for p in O.ledger_problems(rows, early, ops_))
    shifted = [{**ops_[0], "day": 9}]
    assert any("historical day" in p for p in O.ledger_problems(rows, funded, shifted))
    ghost = ops_ + [{"start_day": 0, "account": 4, "day": 3, "slot": 0, "historical_day": 2, "trade_index": 0}]
    assert any("does not hold" in p for p in O.ledger_problems(rows, funded, ghost))


# ------------------------------------------------------------------------------------------------ the table


class _Block:
    def __init__(self, entry_t, sides=None):
        self.entry_t = np.asarray(entry_t, float)
        self.sides = None if sides is None else np.asarray(sides, int)

    def __len__(self):
        return len(self.entry_t)


def test_the_trade_table_keeps_where_and_when_only_and_orders_each_day_as_the_blocks():
    t = O.TradeTable(trade_frame())
    assert t.columns == O.TRADE_COLUMNS and t.n == len(TRADES)
    assert list(t.day("2023-12-28")["mark"]) == [925, 930, 960] and list(t.day("2023-12-29")["mark"]) == [100, 955]
    blocks = [_Block([926, 931, 961], [1, 1, 1]), _Block([101, 961], [1, 1]), _Block([966]), _Block([1], [1])]
    assert t.block_problems(blocks, DATES) == []
    bad = [_Block([931, 926, 961]), *blocks[1:]]
    assert "entry bars" in t.block_problems(bad, DATES)[0]
    short = [_Block([926, 931]), *blocks[1:]]
    assert "2 trades in the block, 3 in the table" in t.block_problems(short, DATES)[0]
    sides = [_Block([926, 931, 961], [1, -1, 1]), *blocks[1:]]
    assert "sides" in t.block_problems(sides, DATES)[0]
    assert "not session dates" in t.block_problems(blocks[1:] + [_Block([])], DATES[1:] + ["2024-01-04"])[-1]
    assert t.day_kind_problems(frozenset({"2023-12-28"})) == []
    assert "disagree" in t.day_kind_problems(frozenset({"2023-12-29"}))[0]
    with pytest.raises(O.OpeningsRefused, match="no column"):
        O.TradeTable(trade_frame().drop(columns=["decision_slot_minutes"]))


def test_an_opening_is_placed_on_its_session_trade_and_calendars():
    p = placed()
    assert all(tuple(x) == O.PLACED_KEYS for x in p)
    p5 = p[4]
    assert (p5["date"], p5["mark_ct"], p5["entry_ct"], p5["entry_delay"], p5["hour_ct"]) == \
        ("2023-12-29", "08:55", "09:00", 5, "08")
    assert (p5["block"], p5["weekday"], p5["year"], p5["report_day"], p5["fomc_day"], p5["calendar"]) == \
        ("choice", "Fri", 2023, False, False, O.NO_CALENDAR)
    assert p[5]["stop_points"] == 25.0 and p[0]["stop_points"] == 37.5
    assert (p[6]["block"], p[6]["fomc_day"], p[7]["calendar"]) == ("judged", True, "early_close")
    assert p[1]["trade_key"] == p[2]["trade_key"] != p[3]["trade_key"]
    table = O.TradeTable(trade_frame())
    with pytest.raises(O.OpeningsRefused, match="not in the trade table"):
        O.place({**ops()[0], "trade_index": 3}, DATES, table, CAL)
    with pytest.raises(O.OpeningsRefused, match="outside"):
        O.place({**ops()[0], "start_day": 4}, DATES, table, CAL)


# ------------------------------------------------------------------------------------------------ the counts


@pytest.mark.parametrize("block", O.BLOCKS)
def test_the_counts_and_shares_are_the_hand_worked_ones(block):
    rows = O.count_rows(placed(), "p16", "point", "P-16")
    got = {(s, g): v for (b, s, g), v in counts(rows).items() if b == block}
    want = want_block(block)
    assert set(got) == set(want), (sorted(set(got) ^ set(want)))
    n, nd = want[("supply", O.EVERY)]
    nd = nd if nd is not None else len({x["trade_key"] for x in placed() if x["block"] == block})
    for k, (c, d) in want.items():
        o, share, dist, dshare, bn, bd = got[k]
        assert o == c and bn == n and bd == nd, (k, got[k])
        assert share == pytest.approx(c / n), k
        if d is not None:
            assert dist == d and dshare == pytest.approx(d / nd), (k, got[k])


def test_the_rows_come_in_session_order_and_every_block_adds_up():
    rows = O.count_rows(placed(), "p16", "verdict", "P-16")
    marks = [r["group"] for r in rows if r["block"] == "all" and r["section"] == "mark"]
    assert marks == ["17:00", "18:40", "08:25", "08:30", "08:55", "09:00", "09:05"]
    hours = [r["group"] for r in rows if r["block"] == "all" and r["section"] == "hour"]
    assert hours == ["17", "18", "08", "09"]
    win = [r["group"] for r in rows if r["block"] == "all" and r["section"] == "window"]
    assert win == [w for w, _ in O.WINDOWS]
    df = O.frame(rows + O.count_rows(placed(), "p16", "point", "P-16"), "a test")
    assert O.output_problems(df) == []
    assert set(df["reading"]) == {"a test"} and set(df["prereg"]) == {"P-16"}


def test_a_block_without_openings_reads_zero_and_no_share():
    rows = O.count_rows([x for x in placed() if x["block"] == "choice"], "p14", "point")
    j = [r for r in rows if r["block"] == "judged"]
    assert len(j) == 1 and j[0]["section"] == "supply" and j[0]["openings"] == 0 and np.isnan(j[0]["share"])
    assert O.output_problems(O.frame(rows, "x")) == []


# ------------------------------------------------------------------------------------------------ no outcome


def test_no_written_column_carries_an_outcome():
    assert O.outcome_columns(O.COLUMNS) == []
    for c in ("pnl", "win_rate", "passes", "payout_days", "exit_t", "r_3", "net_month_1", "balance_after", "fees",
              "mae_1", "loss_share", "outcome", "first_pass", "cash"):
        assert O.outcome_columns([c]) == [c], c


def test_the_frame_check_refuses_an_outcome_a_tampered_count_or_a_block_that_does_not_add_up():
    df = O.frame(O.count_rows(placed(), "p16", "point", "P-16"), "x")
    assert O.output_problems(df) == []
    assert any("outcome" in p for p in O.output_problems(df.assign(pnl=0.0)))
    assert any("columns" in p for p in O.output_problems(df.rename(columns={"share": "win_share"})))
    t = df.copy()
    i = t.index[(t["block"] == "all") & (t["section"] == "mark") & (t["group"] == "08:30")][0]
    t.loc[i, "openings"] = 3
    probs = O.output_problems(t)
    assert any("mark: the groups add to 9, not 8" in p for p in probs), probs
    assert any("choice + judged" in p for p in probs), probs
    u = df.copy()
    u.loc[u.index[(u["section"] == "report_day_mark") & (u["block"] == "choice")][0], "openings"] = 0
    assert any("report_day_mark" in p for p in O.output_problems(u))
    v = df.copy()
    v.loc[v.index[(v["section"] == "window") & (v["group"] == "mark in [08:30, 09:00] CT")][0], "openings"] = 1
    assert any("inclusive window" in p for p in O.output_problems(v))
    w = df.copy()
    w.loc[w.index[0], "share"] = 1.5
    assert any("outside [0, 1]" in p for p in O.output_problems(w))
    assert any("unknown section" in p for p in O.output_problems(df.assign(section="pass_rate")))


def test_count_rows_refuses_an_opening_carrying_anything_but_where_and_when():
    p = placed()
    with pytest.raises(O.OpeningsRefused, match="pnl"):
        O.count_rows([{**p[0], "pnl": 1.0}], "p16", "point")


def test_the_calendar_rows_by_date():
    rows = [{"date": "2020-01-20", "kind": "holiday"}, {"date": "2020-11-27", "kind": "early_close"},
            {"date": "2020-11-27", "kind": "data_defect_candidate"}]
    assert O.calendar_kinds(rows) == {"2020-01-20": "holiday", "2020-11-27": "early_close+data_defect_candidate"}
    assert O.iso_of_yymmdd(200102) == "2020-01-02" and O.iso_of_yymmdd(260716) == "2026-07-16"


# ------------------------------------------------------------------------------------------------ the engine, synthetic


def test_the_ledger_on_replay_on_a_synthetic_campaign():
    r = subprocess.run([sys.executable, str(ROOT / "tests" / "q35_synthetic.py"), str(ROOT)], capture_output=True,
                       text=True, timeout=600,
                       env={**os.environ, "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"})
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    out = json.loads(r.stdout.strip().splitlines()[-1])
    assert out["starts"] == 4 and out["problems"] == [] and out["openings"] > 5, out
    assert out["opening_keys"] == sorted(O.OPENING_KEYS)
    assert all(out["path_same"]) and all(out["record_same"]) and out["first_ok"], out
    assert out["funded_traded"] == out["openings"]
    assert out["table_columns"] == list(O.TRADE_COLUMNS) and out["block_problems"] == []
    assert out["day_kind_problems"] == [] and len(out["day_kind_problems_wrong"]) == 1
    assert "entry bars" in out["bad_block_problems"][0]
    assert out["placed_ok"] and out["blocks_seen"] == ["choice", "judged"] and out["output_problems"] == []
    assert out["bls_equal"] and out["fomc_includes"] and out["calendar_late"], out
    assert out["refusals"] == {"record_trades_twice": True, "placement_on": True}


#: the only kinds of line the script prints: no count, no share
PRINTED = ("the inputs of ", "identity HOLDS: ", "identity FAILS: ", "timing: ", "  Q-35 ", "    ", "REFUSED (Q-35)",
           "every identity holds; the pipeline ran", "written: ", "peak working set")


def test_the_scripts_pipeline_on_a_synthetic_campaign_writes_no_outcome_and_prints_no_count():
    """`main --check --starts 3` on the synthetic campaign standing in for both designs (the build, the calendars and
    U1's file replaced; the read's authorisation recorded): every identity line, the frame through
    `extended.results.write_result` into a temporary folder, its manifest's seed and variant count; then with the U1
    comparison failing -- refused, nothing written, the differing values never printed."""
    r = subprocess.run([sys.executable, str(ROOT / "tests" / "q35_synthetic.py"), str(ROOT), "pipeline"],
                       capture_output=True, text=True, timeout=600,
                       env={**os.environ, "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"})
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    out = json.loads(r.stdout.strip().splitlines()[-1])
    holds, fails, f = out["holds"], out["fails"], out["frame"]
    assert holds["rc"] == 0 and holds["written"] and "every identity holds; the pipeline ran" in holds["stdout"], holds
    assert holds["stdout"].count("identity HOLDS") == 7 and "FAILS" not in holds["stdout"]
    for line in holds["stdout"].splitlines() + fails["stdout"].splitlines():
        assert line.startswith(PRINTED), line
    assert out["authorised"] == [["P-14", "P-16"], ["P-14", "P-16"]]
    assert [c[:3] for c in out["compared"][:4]] == [["p14", "verdict", 3], ["p14", "point", 3], ["p16", "verdict", 3],
                                                     ["p16", "point", 3]]
    assert f["name"] == "q35_openings" and f["columns"] == list(O.COLUMNS) and f["problems"] == [], f
    assert f["identity_rows"] == 7 and f["designs"] == ["p14", "p16"] and f["temp"]
    assert set(f["sections"]) == set(O.SECTIONS)
    assert f["seed"] == 20261920 and f["variant_count"] == 4 and f["exploratory"] is True
    assert {"seeds", "replay", "opening", "blocks", "calendars", "u1_reference", "read", "windows"} <= set(f["parameters"])
    assert fails["rc"] == 3 and not fails["written"] and "identity FAILS" in fails["stdout"], fails
    assert "1 of 3 starts differ" in fails["stdout"] and "123.456" not in fails["stdout"]
    assert "124.789" not in fails["stdout"] and "REFUSED (Q-35): nothing written" in fails["stdout"]


# ------------------------------------------------------------------------------------------------ the reader

A1E, A1D = "vendor/stage2/data/atlas/A1/events.parquet", "vendor/stage2/data/atlas/A1/days.parquet"
A3W = "vendor/stage2/data/atlas/A3/walks.parquet"
BARS = "vendor/stage2/data/bars/NQ/bars.parquet"
A1A3 = (A1E, A1D, A3W)
ALL4 = (A1E, A1D, A3W, BARS)
ROW = "E-021"

DRIVER = r'''
"""Q-35's test driver (tests/test_q35_openings.py): scripts/q35_openings.py's main on this temporary tree, the reader
and the clean-run check pointed at it, the first step after the authorisation a recorder that stops the run."""
import contextlib, importlib.util, io, json, os, subprocess, sys
from pathlib import Path

cfg = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
REPO = Path(cfg["repo"])
TREE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
for k in ("S2X_CLEAN_RUN", "S2X_RUN_ID"):
    os.environ.pop(k, None)

from extended import reader as R
import extended.results as XR

R.ROOT = TREE
R.RUNS_DIR = TREE.parent
XR.ROOT = TREE
XR.RUNS_DIR = TREE.parent
LEDGER = TREE / "results" / "read_ledger.jsonl"
events = []
_real = R.authorise


def recording(start, end, **k):
    events.append({"event": "authorise", "start": str(start), "end": str(end), "declaration": k.get("declaration"),
                   "purpose": k.get("purpose"), "design": k.get("design")})
    return _real(start, end, **k)


R.authorise = recording


class Stopped(Exception):
    pass


def stop(name):
    def f(*a, **k):
        events.append({"event": "work", "name": name})
        raise Stopped(name)
    return f


spec = importlib.util.spec_from_file_location("q35_script", REPO / "scripts" / "q35_openings.py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)
M.VENDOR = TREE / "vendor" / "stage2"
M.load_calendars = stop("load_calendars")


def lines():
    return LEDGER.read_text(encoding="utf-8").splitlines() if LEDGER.exists() else []


def git(*args):
    subprocess.run(["git", "-C", str(TREE), *args], check=True, capture_output=True)


out = []
for phase in cfg["phases"]:
    if phase.get("decisions") is not None:
        (TREE / "DECISIONS.md").write_bytes(phase["decisions"].encode("utf-8"))
        git("add", "DECISIONS.md")
        git("commit", "-q", "-m", "the decision log for phase " + phase["name"])
    for k in ("S2X_CLEAN_RUN", "S2X_RUN_ID"):
        os.environ.pop(k, None)
    os.environ.update(phase.get("env") or {})
    for argv in phase["runs"]:
        events.clear()
        before = lines()
        buf = io.StringIO()
        rec = {"phase": phase["name"], "argv": argv}
        try:
            with contextlib.redirect_stdout(buf):
                rec["rc"] = M.main(list(argv))
        except Stopped as e:
            rec["stopped"] = str(e)
        except BaseException as e:                       # noqa: BLE001 -- recorded, the test reads it
            rec["error"] = type(e).__name__ + ": " + str(e)[:600]
        after = lines()
        rec.update(stdout=buf.getvalue()[-3000:], events=list(events), ledger_exists=LEDGER.exists(),
                   new=[json.loads(x) for x in after[len(before):]], prefix_kept=after[:len(before)] == before)
        out.append(rec)
print(json.dumps(out))
'''

OUTSIDE = (["--check", "--starts", "4"], ["--check", "--starts", "4", "--designs", "p14"], [], ["--starts", "4"],
           ["--check", "--designs", "p15"], ["--check", "--workers", "3"])
INSIDE = ([], ["--check", "--starts", "4", "--designs", "p16"])


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def real_row() -> str | None:
    return R.decision_row((ROOT / "DECISIONS.md").read_text(encoding="utf-8"), ROW)


def log(rows: list[str]) -> str:
    head = "# Decisions (a temporary tree, Q-35's tests)\n\n| id | date | decision | basis |\n|---|---|---|---|\n"
    return head + "".join(line + "\n" for line in rows)


def make_tree(base: Path, name: str, decisions: str) -> Path:
    t = base / "runs" / name
    (t / "scripts").mkdir(parents=True)
    (t / "scripts" / "q35_driver.py").write_text(DRIVER, encoding="utf-8")
    (t / "DECISIONS.md").write_bytes(decisions.encode("utf-8"))
    manifest = []
    for rel in ALL4:
        p = t / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(f"a stand-in for {rel} (Q-35's tests; never parsed)\n".encode("utf-8"))
        manifest.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {rel.removeprefix('vendor/stage2/')}\n")
    (t / "vendor" / "DATA_MANIFEST_stage2.sha256").write_text("".join(manifest), encoding="utf-8")
    (t / ".gitignore").write_text("vendor/stage2/data/\n", encoding="utf-8")
    git(t, "init", "-q", "-b", "master")
    git(t, "config", "user.email", "t@example.invalid")
    git(t, "config", "user.name", "t")
    git(t, "config", "core.autocrlf", "false")
    git(t, "add", "-A")
    git(t, "commit", "-q", "-m", "the temporary tree")
    return t


@pytest.fixture(scope="module")
def reads(tmp_path_factory) -> dict:
    base = tmp_path_factory.mktemp("q35")
    row = real_row()
    assert row is not None
    t = make_tree(base, "q35-reads", log([row]))
    name = t.name
    clean = {"S2X_CLEAN_RUN": name, "S2X_RUN_ID": f"{name}@q35-sim"}
    no_p16 = row.replace("P-16", "the coin")
    missing = log(["| E-904 | 2026-11-16 | **A row about nothing in particular** | test |"])
    phases = [{"name": "outside", "env": {}, "runs": [list(x) for x in OUTSIDE]},
              {"name": "inside", "env": clean, "runs": [list(x) for x in INSIDE]},
              {"name": "no_p16", "decisions": log([no_p16]), "env": {}, "runs": [["--check", "--starts", "4"]]},
              {"name": "no_p16_p14_only", "env": {}, "runs": [["--check", "--starts", "4", "--designs", "p14"]]},
              {"name": "missing", "decisions": missing, "env": clean, "runs": [[]]}]
    cfg = base / "q35.json"
    cfg.write_text(json.dumps({"repo": str(ROOT), "phases": phases}), encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k not in ("S2X_CLEAN_RUN", "S2X_RUN_ID")}
    env.update({"OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"})
    r = subprocess.run([sys.executable, "scripts/q35_driver.py", str(cfg)], cwd=t, capture_output=True, text=True,
                       timeout=600, env=env)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    return {"runs": json.loads(r.stdout.strip().splitlines()[-1]), "tree": t}


def _phase(reads: dict, name: str) -> list[dict]:
    return [r for r in reads["runs"] if r["phase"] == name]


def _auth(r: dict) -> list[dict]:
    return [e for e in r["events"] if e["event"] == "authorise"]


def _work(r: dict) -> list[str]:
    return [e["name"] for e in r["events"] if e["event"] == "work"]


def _explain(r: dict) -> str:
    return f"{r['argv']} ({r['phase']}): rc {r.get('rc')} stopped {r.get('stopped')} {r.get('error', '')}\n{r['stdout']}"


def test_the_row_the_reading_names_exists_and_names_both_designs():
    row = real_row()
    assert row is not None, f"{ROW} is no decision row of DECISIONS.md"
    for d in ("P-14", "P-16"):
        assert R.names_design(row, d), f"{ROW}'s row does not name {d}"
    src = (ROOT / "scripts" / "q35_openings.py").read_text(encoding="utf-8")
    assert re.search(rf'READ_ROW = "{ROW}"', src)


def test_outside_a_clean_run_the_check_authorises_once_before_any_work_and_ledgers_nothing(reads):
    rs = _phase(reads, "outside")
    for r, designs, files in ((rs[0], ["P-14", "P-16"], ALL4), (rs[1], ["P-14"], A1A3)):
        a = _auth(r)
        assert "error" not in r and r.get("stopped") == "load_calendars", _explain(r)
        assert len(a) == 1 and r["events"].index(a[0]) == 0 and _work(r) == ["load_calendars"], _explain(r)
        assert a[0]["purpose"] == "registered_design" and a[0]["declaration"] == ROW and a[0]["design"] == designs
        assert (a[0]["start"], a[0]["end"]) == ("2020-01-02", "2026-07-16")
        assert not r["ledger_exists"] and r["new"] == []


def test_the_declared_run_and_a_wrong_argument_are_refused_before_the_read(reads):
    rs = _phase(reads, "outside")
    declared = rs[2]
    assert declared.get("rc") == 2 and "REFUSED" in declared["stdout"] and "clean checkout" in declared["stdout"], \
        _explain(declared)
    for r in rs[2:]:
        assert r.get("rc") == 2 and _auth(r) == [] and _work(r) == [] and "error" not in r, _explain(r)
        assert "REFUSED" in r["stdout"]


def test_inside_a_clean_run_one_ledger_line_a_run(reads):
    tree = reads["tree"]
    rs = _phase(reads, "inside")
    for r, designs, files in ((rs[0], ["P-14", "P-16"], ALL4), (rs[1], ["P-16"], ALL4)):
        assert "error" not in r and r.get("stopped") == "load_calendars", _explain(r)
        assert r["prefix_kept"] and len(r["new"]) == 1, _explain(r)
        line = r["new"][0]
        assert line["purpose"] == "registered_design" and line["repeat"] is None
        assert line["declaration"] == {"ref": ROW, "sha256": None, "kind": "registered_design", "designs": designs}
        assert line["dates"] == {"start": "2020-01-02", "end": "2026-07-16", "blocks": ["choice", "judged"],
                                 "judged_first": "2024-01-02", "judged_last": "2026-07-16"}
        got = [f["path"] for f in line["what"]["files"]]
        assert sorted(got) == sorted(files)
        for f in line["what"]["files"]:
            assert f["sha256"] == hashlib.sha256((tree / f["path"]).read_bytes()).hexdigest() and f["in_data_manifest"]
        who = line["who"]
        assert who["script"] == "scripts/q35_driver.py" and who["clean_run"] == tree.name and who["dirty"] is False
        assert "scripts/q35_openings.py:" in who["caller"].replace("\\", "/") and who["caller"].endswith(":main")
    assert len(R.read_ledger(tree / R.LEDGER_REL)) == 2


def test_a_row_that_does_not_admit_the_reading_is_refused_and_nothing_starts(reads):
    for name, why in (("no_p16", "does not name P-16"), ("missing", "no decision row")):
        r = _phase(reads, name)[0]
        assert r.get("rc") == 3 and "error" not in r and "stopped" not in r, _explain(r)
        assert "REFUSED" in r["stdout"] and why in r["stdout"], _explain(r)
        assert _work(r) == [] and r["new"] == [] and r["prefix_kept"]
    r = _phase(reads, "no_p16_p14_only")[0]                    # the same row still admits P-14 alone
    assert r.get("stopped") == "load_calendars" and _auth(r)[0]["design"] == ["P-14"], _explain(r)


# ------------------------------------------------------------------------------------------------ the pipeline (slow)


@pytest.mark.slow
def test_the_pipeline_on_four_starts():
    """`--check --starts 4`: every identity holds (U1's start rows at 4 starts with the ledger on, the blocks against
    the trade table, the day kinds, the frame) and the file is written to a temporary folder only. Reads the real bars
    (P-16's walk): the slow tier, under the run lock."""
    if not ((DATA / "bars").is_dir() and (DATA / "atlas").is_dir()):
        pytest.skip("bars and atlas not copied (scripts/vendor_stage2.py --data)")
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "q35_openings.py"), "--check", "--starts", "4"],
                       capture_output=True, text=True, timeout=3600)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    assert "every identity holds; the pipeline ran" in r.stdout and "FAILS" not in r.stdout, r.stdout
    assert r.stdout.count("identity HOLDS") == 7, r.stdout          # 2 builds, 4 replays, the frame
