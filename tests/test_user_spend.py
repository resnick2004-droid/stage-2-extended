"""Q-86: money spent and the return on spend, per start day, beside Q-44's readings -- `extended/user_spend.py` and
`scripts/user_spend.py`, on synthetic inputs only (no bar, no atlas, no result file).

* **The cumulative arithmetic** (in this process: `extended.user_spend` imports no engine): a hand-built campaign of
  three start days -- fees and payouts close by close, the evaluations' purchase days, a reset -- gives exactly the
  values worked out by hand: the fees paid and payouts received at the first pass, the first payout and break-even, the
  evaluations and resets bought before the first pass, whether break-even was later lost, the fees, payouts and return
  on spend at each month end 1-6, the totals at the window's end; and the U1 money (fees and net at months 1-12, the
  cash spent before the first pass and payout, the first payout's cash, the pay days).
* **The summary**: on those start days, the hand-worked percentiles, spread and share never there, on all start days
  and the judged block; the windows and eligibility are Q-44's (`extended.user_readings`).
* **The identities refuse**: `ledger_problems` (the engine's day ledger against its cash, its totals and its per-account
  purchase, rebill, activation, reset and payout records) finds nothing on the hand-built campaign and names each
  planted error; `u1_money_problems` (the money against U1's own start-row columns) holds on rows made from the same
  campaign and names the column and the count, never a value, for each planted difference; `spend_args` refuses
  arguments already carrying the day recorder, another activation timing, or a response switched on.
* **The written frame**: `output_problems` passes the frame `frame` makes and refuses a column too many, an unknown
  section, a summary that is not its start rows', a share outside [0, 1], unordered percentiles.
* **The engine, synthetic** (`tests/q86_synthetic.py`, a process of its own): the day recorder changes no path and no
  U1 record; every start's ledger identity holds; rebills, activations, payouts, a reset, break-even reached, lost and
  never reached are all exercised. And the script's `main --check` on that campaign standing in for the three designs:
  every identity line, the frame through `extended.results.write_result` into a temporary folder only, its manifest's
  seed and variant count, nothing printed but identity, timing and the file's name; with the U1 comparison failing it
  is refused and nothing is written.
* **The reader is used** (a child process on a temporary git tree, as `tests/test_q35_openings.py`): `main`
  authorises once, purpose `registered_design`, its decision row, the designs run, the whole window, the files the
  engine opens -- before any work; outside a clean run nothing is ledgered and the declared run is refused (exit 2);
  inside a simulated clean run one ledger line a run; a row not naming a design is refused (exit 3).
* (slow, not in the fast tier: it reads the real bars) `--check --starts 4`.
"""
from __future__ import annotations

import hashlib
import json
import math
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

from extended import reader as R  # noqa: E402
import heldout_verdict_rows as VR  # noqa: E402  (Q-194b: the held-out test's verdict rows)
from extended import user_spend as US  # noqa: E402

DATA = ROOT / "vendor" / "stage2" / "data"
NAN = float("nan")

# ------------------------------------------------------------------------------------------------ the hand-built case
#
# Start 1 (2023-06-01, the choice block; 130 sessions observed). Evaluations A, B bought on day 0 ($49 each); B fails on
# day 5 and C is bought; A rebills on day 22 (0 + 21 + 1), C on 27 and 48; A passes on day 30 and is activated ($149),
# D bought that evening; D rebills on 52; E bought on day 100. Payouts arrive on day 50 ($500), 60 ($1,000), 70 ($800).
#   cumulative fees: d0 98, d5 147, d22 196, d27 245, d30 443, d48 492, d52 541, d100 590
#   net: d50 = 500 - 492 = 8 (break-even, the first close >= 0); d52 = 500 - 541 = -41 (lost again); the deepest
#   net before break-even -492 (closes 48 and 49)
# Start 2 (2024-03-01, judged; 40 sessions): one evaluation on day 0, rebilled on day 22; never passes.
# Start 3 (2024-05-01, judged; 63 sessions): an evaluation on day 0, reset on day 10 ($49), passes on day 15 and is
#   activated ($149); a payout of $300 on day 40: net 300 - 247 = 53, break-even on day 40 and never lost.

FEES = {1: {0: 98.0, 5: 49.0, 22: 49.0, 27: 49.0, 30: 198.0, 48: 49.0, 52: 49.0, 100: 49.0},
        2: {0: 49.0, 22: 49.0},
        3: {0: 49.0, 10: 49.0, 15: 149.0}}
PAYS = {1: {50: 500.0, 60: 1000.0, 70: 800.0}, 2: {}, 3: {40: 300.0}}
OBSERVED = {1: 130, 2: 40, 3: 63}
PURCHASES = {1: [0, 0, 5, 30, 100], 2: [0], 3: [0]}
RESETS = {1: [], 2: [], 3: [10]}
FIRST_PASS = {1: 30.0, 2: NAN, 3: 15.0}
FIRST_PAYOUT = {1: 50.0, 2: NAN, 3: 40.0}
DATES = {1: "2023-06-01", 2: "2024-03-01", 3: "2024-05-01"}


def series(k: int) -> tuple[np.ndarray, np.ndarray]:
    n = OBSERVED[k] + 1
    f, p = np.zeros(n), np.zeros(n)
    for d, v in FEES[k].items():
        f[d] += v
    for d, v in PAYS[k].items():
        p[d] += v
    return f, p


def record(k: int) -> dict:
    f, p = series(k)
    return US.spend_record(f, p, PURCHASES[k], RESETS[k], FIRST_PASS[k], FIRST_PAYOUT[k])


def same(a, b, tol=1e-9) -> bool:
    a, b = float(a), float(b)
    return (math.isnan(a) and math.isnan(b)) or abs(a - b) <= tol


WANT = {
    1: {"first_pass": 30, "fees_at_first_pass": 443, "payouts_at_first_pass": 0, "evaluations_before_first_pass": 3,
        "resets_before_first_pass": 0, "first_payout": 50, "fees_at_first_payout": 492, "payouts_at_first_payout": 500,
        "break_even_day": 50, "fees_at_break_even": 492, "payouts_at_break_even": 500,
        "spent_before_break_even": 492, "break_even_lost": 1.0,
        "fees_month_1": 147, "payouts_month_1": 0, "return_on_spend_month_1": -1.0,
        "fees_month_2": 443, "payouts_month_2": 0, "return_on_spend_month_2": -1.0,
        "fees_month_3": 541, "payouts_month_3": 1500, "return_on_spend_month_3": 959 / 541,
        "fees_month_4": 541, "payouts_month_4": 2300, "return_on_spend_month_4": 1759 / 541,
        "fees_month_5": 590, "payouts_month_5": 2300, "return_on_spend_month_5": 1710 / 590,
        "fees_month_6": 590, "payouts_month_6": 2300, "return_on_spend_month_6": 1710 / 590,
        "fees_end": 590, "payouts_end": 2300, "evaluations_bought": 5, "resets": 0},
    2: {"first_pass": NAN, "fees_at_first_pass": NAN, "payouts_at_first_pass": NAN,
        "evaluations_before_first_pass": NAN, "resets_before_first_pass": NAN, "first_payout": NAN,
        "fees_at_first_payout": NAN, "payouts_at_first_payout": NAN, "break_even_day": NAN, "fees_at_break_even": NAN,
        "payouts_at_break_even": NAN, "spent_before_break_even": NAN, "break_even_lost": NAN,
        "fees_month_1": 49, "payouts_month_1": 0, "return_on_spend_month_1": -1.0,
        **{f"{c}_month_{m}": NAN for m in range(2, 7) for c in ("fees", "payouts", "return_on_spend")},
        "fees_end": 98, "payouts_end": 0, "evaluations_bought": 1, "resets": 0},
    3: {"first_pass": 15, "fees_at_first_pass": 247, "payouts_at_first_pass": 0, "evaluations_before_first_pass": 1,
        "resets_before_first_pass": 1, "first_payout": 40, "fees_at_first_payout": 247, "payouts_at_first_payout": 300,
        "break_even_day": 40, "fees_at_break_even": 247, "payouts_at_break_even": 300,
        "spent_before_break_even": 247, "break_even_lost": 0.0,
        "fees_month_1": 247, "payouts_month_1": 0, "return_on_spend_month_1": -1.0,
        "fees_month_2": 247, "payouts_month_2": 300, "return_on_spend_month_2": 53 / 247,
        "fees_month_3": 247, "payouts_month_3": 300, "return_on_spend_month_3": 53 / 247,
        **{f"{c}_month_{m}": NAN for m in range(4, 7) for c in ("fees", "payouts", "return_on_spend")},
        "fees_end": 247, "payouts_end": 300, "evaluations_bought": 1, "resets": 1},
}


@pytest.mark.parametrize("k", [1, 2, 3])
def test_the_cumulative_arithmetic_is_the_hand_worked_one(k):
    got = record(k)
    assert tuple(got) == US.SPEND_KEYS
    bad = {c: (got[c], WANT[k][c]) for c in US.SPEND_KEYS if not same(got[c], WANT[k][c])}
    assert not bad, bad


def test_the_return_on_spend_is_net_over_cumulative_fees_and_the_month_end_closes_are_21m():
    assert US.SPEND_MONTHS == (1, 2, 3, 4, 5, 6) and US.MONTH == 21
    r = record(1)
    for m in US.SPEND_MONTHS:
        f, p = r[f"fees_month_{m}"], r[f"payouts_month_{m}"]
        assert same(r[f"return_on_spend_month_{m}"], (p - f) / f)
    # an event after the window's last close, or never, has no money at it
    f, p = series(1)
    r = US.spend_record(f, p, PURCHASES[1], [], 500.0, NAN)
    assert math.isnan(r["fees_at_first_pass"]) and math.isnan(r["evaluations_before_first_pass"])
    # fees and payouts of different lengths, or a negative fee, are refused
    with pytest.raises(US.SpendRefused):
        US.spend_record(f[:-1], p, PURCHASES[1], [], 30.0, 50.0)
    with pytest.raises(US.SpendRefused):
        US.spend_record(-f, p, PURCHASES[1], [], 30.0, 50.0)


def test_the_u1_money_is_the_hand_worked_one():
    f, p = series(1)
    m = US.u1_money(f, p, FIRST_PASS[1], FIRST_PAYOUT[1])
    assert same(m["fees_month_1"], 147) and same(m["net_month_1"], -147)
    assert same(m["fees_month_3"], 541) and same(m["net_month_3"], 959)
    assert same(m["fees_month_6"], 590) and same(m["net_month_6"], 1710)
    assert all(math.isnan(m[f"fees_month_{k}"]) and math.isnan(m[f"net_month_{k}"]) for k in range(7, 13))
    # the deepest cash below the start over the closes before the event (U1's `spent_before`)
    assert same(m["spent_before_first_pass"], 245) and same(m["spent_before_first_payout"], 492)
    assert same(m["first_payout_day_cash"], 500) and m["pay_days"] == [50, 60, 70]


# ------------------------------------------------------------------------------------------------ the summary


def table() -> pd.DataFrame:
    rows = [{"design": "p14", "prereg": "P-14", "arm": "verdict", "start_day": k, "start_date": DATES[k],
             "observed": OBSERVED[k], **record(k)} for k in (1, 2, 3)]
    return pd.DataFrame(rows, columns=list(US.START_COLS))


def summary_by() -> dict:
    return {(r["block"], r["measure"], r["stat"]): (r["value"], r["n"]) for r in US.summary_rows(table())}


def test_the_summary_is_the_hand_worked_one():
    s = summary_by()
    # fees by month 1: all three starts have 21 sessions -> [49, 147, 247]; the judged block starts 2 and 3
    assert same(s[("all", "fees_month_1", "p50")][0], 147) and s[("all", "fees_month_1", "p50")][1] == 3
    assert same(s[("all", "fees_month_1", "p10")][0], 49 + 0.2 * 98)
    assert same(s[("all", "fees_month_1", "p25")][0], 49 + 0.5 * 98)
    assert same(s[("all", "fees_month_1", "p90")][0], 147 + 0.8 * 100)
    assert same(s[("all", "fees_month_1", "spread")][0], 147 + 0.8 * 100 - 49 - 0.2 * 98)
    assert same(s[("judged", "fees_month_1", "p50")][0], 148) and s[("judged", "fees_month_1", "p50")][1] == 2
    assert same(s[("judged", "fees_month_1", "p10")][0], 49 + 0.1 * 198)
    # month 3 needs 63 sessions: starts 1 and 3
    assert same(s[("all", "return_on_spend_month_3", "p50")][0], (959 / 541 + 53 / 247) / 2)
    assert s[("all", "return_on_spend_month_3", "p50")][1] == 2
    # month 6 needs 126 sessions: start 1 alone; none in the judged block
    assert same(s[("all", "payouts_month_6", "p75")][0], 2300) and s[("all", "payouts_month_6", "p75")][1] == 1
    assert math.isnan(s[("judged", "payouts_month_6", "p50")][0]) and s[("judged", "payouts_month_6", "p50")][1] == 0
    # the first pass and payout read the starts with 126 sessions (start 1), break-even those with 252 (none)
    assert same(s[("all", "sessions_to_first_pass", "p50")][0], 30) and s[("all", "sessions_to_first_pass", "p50")][1] == 1
    assert same(s[("all", "fees_at_first_pass", "p90")][0], 443)
    assert same(s[("all", "evaluations_before_first_pass", "p50")][0], 3)
    assert same(s[("all", "sessions_to_first_pass", "share_never")][0], 0.0)
    assert same(s[("all", "fees_at_first_payout", "share_never")][0], 0.0)
    assert same(s[("all", "payouts_at_first_payout", "p50")][0], 500)
    assert s[("all", "sessions_to_break_even", "share_never")][1] == 0
    assert math.isnan(s[("all", "sessions_to_break_even", "share_never")][0])
    assert math.isnan(s[("all", "break_even_lost", "share")][0]) and s[("all", "break_even_lost", "share")][1] == 0


def test_the_share_never_there_counts_an_unreached_start_beyond_the_window():
    t = table()
    t.loc[t["start_day"] == 1, "observed"] = 252            # start 1 has the year: it passes, pays and breaks even
    t2 = t.copy()
    t2["start_day"] = t2["start_day"] + 10
    t2["first_pass"] = NAN                                  # a twin that never passes, pays or breaks even
    t2["first_payout"] = NAN
    t2["break_even_day"] = NAN
    for c in US.SPEND_KEYS:
        if c.endswith(("first_pass", "first_payout", "break_even")) or c == "break_even_lost":
            t2[c] = NAN
    s = {(r["block"], r["measure"], r["stat"]): (r["value"], r["n"]) for r in US.summary_rows(pd.concat([t, t2]))}
    for ev in ("first_pass", "first_payout", "break_even"):
        v, n = s[("all", f"sessions_to_{ev}", "share_never")]
        assert n == 2 and same(v, 0.5), (ev, v, n)
        assert same(s[("all", f"fees_at_{ev}", "share_never")][0], 0.5)
        assert s[("all", f"fees_at_{ev}", "p50")][1] == 1       # the money reads the starts that got there
    # half the starts never there: the median day is beyond the window (blank), the spread with it
    assert math.isnan(s[("all", "sessions_to_first_pass", "p90")][0])
    assert math.isnan(s[("all", "sessions_to_first_pass", "spread")][0])
    assert same(s[("all", "break_even_lost", "share")][0], 1.0) and s[("all", "break_even_lost", "share")][1] == 1


def test_every_measure_has_every_stat_on_both_blocks():
    rows = US.summary_rows(table())
    keys = {(r["block"], r["measure"], r["stat"]) for r in rows}
    assert len(keys) == len(rows)
    for b in US.BLOCKS:
        for m, stats in US.SUMMARY_MEASURES.items():
            for st in stats:
                assert (b, m, st) in keys, (b, m, st)
    assert {r["block"] for r in rows} == set(US.BLOCKS)


# ------------------------------------------------------------------------------------------------ the identities


def hand_path(k: int, initial: float = 1e9):
    """The hand-built start as the engine's records would hold it: the day ledger, the cash, the combines (purchase
    day, subscriptions paid, reset days), the funded accounts (activation day, payout requests), the totals."""
    f, p = series(k)
    n = OBSERVED[k] + 1
    sub = np.zeros(n)
    act = np.zeros(n)
    rst = np.zeros(n)
    combines = []
    if k == 1:
        plan = [(0, 2, ()), (0, 1, ()), (5, 3, ()), (30, 2, ()), (100, 1, ())]
        acts = [30]
    elif k == 2:
        plan, acts = [(0, 2, ())], []
    else:
        plan, acts = [(0, 1, (10,))], [15]
    for j, (pd_, paid, resets) in enumerate(plan):
        for i in range(paid):
            sub[pd_ + (i * 21 + 1 if i else 0)] += 49.0
        for d in resets:
            rst[d] += 49.0
        combines.append(SimpleNamespace(index=j, purchase_day=pd_, subscriptions_paid=paid, resets=len(resets),
                                        reset_days=tuple(resets)))
    for d in acts:
        act[d] += 149.0
    assert np.allclose(sub + act + rst, f)
    lag = 3
    pays = sorted(PAYS[k].items())
    funded = []
    for j, d in enumerate(acts):           # every payout from the first funded account, requested `lag` sessions before
        rel_days = tuple(int(day) - lag - d - 1 for day, _ in pays)
        funded.append(SimpleNamespace(index=j, activation_day=d, payout_days=rel_days,
                                      payout_cash=tuple(c for _, c in pays)))
    cash = initial + np.cumsum(p) - np.cumsum(f)
    days = tuple({"day": d, "fee_subscription": float(sub[d]), "fee_activation": float(act[d]),
                  "fee_reset": float(rst[d]), "payouts_in": float(p[d]), "cash": float(cash[d])} for d in range(n))
    path = SimpleNamespace(cash_series=cash, initial_bankroll=initial, total_fees=float(f.sum()),
                           total_payouts=float(p.sum()))
    return SimpleNamespace(path=path, combines=tuple(combines), funded=tuple(funded), campaign_days=days), lag


TERMS = {"subscription": 49.0, "activation": 149.0, "reset_fee": 49.0, "billing_days": 21}


@pytest.mark.parametrize("k", [1, 2, 3])
def test_the_ledger_identity_holds_on_the_hand_built_campaign(k):
    lp, lag = hand_path(k)
    f, p = US.day_ledger(lp)
    assert np.array_equal(f, series(k)[0]) and np.array_equal(p, series(k)[1])
    assert US.ledger_problems(lp, lag=lag, **TERMS) == []


def _planted(k: int, how: str):
    lp, lag = hand_path(k)
    days = [dict(r) for r in lp.campaign_days]
    path = lp.path
    if how == "cash":                                       # a close $1 away from fees and payouts
        cash = np.asarray(path.cash_series, float).copy()
        cash[60:] += 1.0
        path = SimpleNamespace(**{**vars(path), "cash_series": cash})
    elif how == "rebill_day":                               # a rebill booked a day late in the ledger
        days[22]["fee_subscription"] -= 49.0
        days[23]["fee_subscription"] += 49.0
    elif how == "activation":                               # the activation booked as a subscription
        days[30]["fee_activation"] -= 149.0
        days[30]["fee_subscription"] += 149.0
    elif how == "payout_day":                               # a payout arriving a day earlier than its request + lag
        days[60]["payouts_in"] -= 1000.0
        days[59]["payouts_in"] += 1000.0
    elif how == "total":
        path = SimpleNamespace(**{**vars(path), "total_fees": path.total_fees + 49.0})
    elif how == "reset":
        days[10]["fee_reset"] -= 49.0
        days[11]["fee_reset"] += 49.0
    return SimpleNamespace(path=path, combines=lp.combines, funded=lp.funded, campaign_days=tuple(days)), lag


@pytest.mark.parametrize("k, how, word", [(1, "cash", "cash"), (1, "rebill_day", "subscription"),
                                           (1, "activation", "activation"), (1, "payout_day", "payout"),
                                           (1, "total", "total"), (3, "reset", "reset")])
def test_the_ledger_identity_names_each_planted_error(k, how, word):
    lp, lag = _planted(k, how)
    probs = US.ledger_problems(lp, lag=lag, **TERMS)
    assert probs and any(word in p for p in probs), probs


def file_row(k: int) -> dict:
    """U1's start row for the hand-built start, its money columns as `start_record` makes them (from the cash)."""
    f, p = series(k)
    rel = np.cumsum(p) - np.cumsum(f)
    row = {"start_day": k, "observed": OBSERVED[k], "first_pass": FIRST_PASS[k], "first_payout": FIRST_PAYOUT[k],
           "pay_days": " ".join(str(d) for d in sorted(PAYS[k])),
           "first_payout_cash": PAYS[k][min(PAYS[k])] if PAYS[k] else NAN}
    for m in range(1, 13):
        d = 21 * m
        row[f"net_month_{m}"] = float(rel[d]) if d <= OBSERVED[k] else NAN
        row[f"fees_month_{m}"] = float(np.cumsum(f)[d]) if d <= OBSERVED[k] else NAN
    for ev, day in (("pass", FIRST_PASS[k]), ("payout", FIRST_PAYOUT[k])):
        row[f"spent_before_first_{ev}"] = (max(0.0, -float(rel[:int(day)].min())) if int(day) > 0 else 0.0) \
            if not math.isnan(day) else NAN
    return row


def money_by_start() -> dict:
    out = {}
    for k in (1, 2, 3):
        f, p = series(k)
        out[k] = US.u1_money(f, p, FIRST_PASS[k], FIRST_PAYOUT[k])
    return out


def test_the_money_identity_holds_against_u1s_own_columns():
    rows = [file_row(k) for k in (1, 2, 3)]
    assert US.u1_money_problems(money_by_start(), rows, tol=1e-6, what="p14 verdict") == []


@pytest.mark.parametrize("col, delta", [("fees_month_3", 1.0), ("net_month_2", -0.01), ("spent_before_first_payout", 5.0),
                                        ("first_payout_cash", 3.0), ("pay_days", None), ("fees_month_12", 1.0)])
def test_the_money_identity_names_the_column_and_the_count_never_a_value(col, delta):
    rows = [file_row(k) for k in (1, 2, 3)]
    if col == "pay_days":
        rows[0]["pay_days"] = "50 61 70"
    elif col == "fees_month_12":
        rows[0]["fees_month_12"] = 123.0                    # a value where the window holds no such month end
    else:
        rows[0][col] = rows[0][col] + delta
    probs = US.u1_money_problems(money_by_start(), rows, tol=1e-6, what="p14 verdict")
    assert probs == [f"p14 verdict {col}: 1 of 3 starts differ"], probs
    # a start of the file not reproduced, and one of ours not in the file
    probs = US.u1_money_problems(money_by_start(), rows[:2], tol=1e-6, what="p14 verdict")
    assert any("not in U1's file" in p for p in probs), probs


def test_the_tolerance_is_u1s_plus_the_cash_resolution_at_the_bankroll():
    assert US.money_tol(5_000.0) == pytest.approx(1e-6, abs=1e-9)
    assert 1e-6 < US.money_tol(1e9) < 1e-4
    assert US.money_tol(1e9) == pytest.approx(1e-6 + US.TOL_BOOKINGS * float(np.spacing(1e9)) / 2, rel=1e-12)


# ------------------------------------------------------------------------------------------------ the written frame


def good_frame() -> pd.DataFrame:
    t = table()
    idents = [US.identity_row("p14", "P-14", "verdict", "a check that held", 3)]
    return US.frame(idents, [t], US.summary_rows(t), "synthetic")


def test_the_frame_is_the_readings_columns_and_passes_its_checks():
    df = good_frame()
    assert tuple(df.columns) == US.COLUMNS
    assert set(df["section"]) == set(US.SECTIONS)
    assert US.output_problems(df) == []


def test_the_frame_check_refuses_what_it_should():
    df = good_frame()
    bad = df.assign(extra=1.0)
    assert US.output_problems(bad)
    bad = df.copy()
    bad.loc[0, "section"] = "nonsense"
    assert any("section" in p for p in US.output_problems(bad))
    bad = df.copy()
    i = bad.index[(bad["section"] == "summary") & (bad["measure"] == "fees_month_1") & (bad["stat"] == "p50")
                  & (bad["block"] == "all")][0]
    bad.loc[i, "value"] = bad.loc[i, "value"] + 1.0
    assert any("fees_month_1" in p for p in US.output_problems(bad)), US.output_problems(bad)
    bad = df.copy()
    i = bad.index[(bad["section"] == "summary") & (bad["stat"] == "share_never")][0]
    bad.loc[i, "value"] = 1.5
    assert any("share" in p for p in US.output_problems(bad))
    bad = df.copy()
    i = bad.index[(bad["section"] == "start") & (bad["start_day"] == 1)][0]
    bad.loc[i, "fees_month_2"] = 10.0                       # below month 1's: cumulative fees fell
    assert any("cumulative" in p for p in US.output_problems(bad)), US.output_problems(bad)


def test_the_start_rows_hold_money_to_the_cent():
    t = table()
    t.loc[0, "fees_month_1"] = 147.004
    r = US.rounded(t)
    assert r.loc[0, "fees_month_1"] == 147.0 and r.loc[0, "return_on_spend_month_3"] == t.loc[0, "return_on_spend_month_3"]
    assert set(US.MONEY_KEYS) <= set(US.SPEND_KEYS)
    assert all(c.startswith(("fees_", "payouts_", "spent_")) for c in US.MONEY_KEYS)


# ------------------------------------------------------------------------------------------------ the engine, synthetic

ENV = {"OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}


def _synthetic(*argv: str) -> dict:
    env = {k: v for k, v in os.environ.items() if k not in ("S2X_CLEAN_RUN", "S2X_RUN_ID")}
    r = subprocess.run([sys.executable, str(ROOT / "tests" / "q86_synthetic.py"), str(ROOT), *argv],
                       capture_output=True, text=True, timeout=600, env={**env, **ENV})
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    return json.loads(r.stdout.strip().splitlines()[-1])


def test_the_day_recorder_on_a_synthetic_campaign():
    out = _synthetic()
    assert out["starts"] >= 5 and out["problems"] == [], out
    assert all(out["path_same"]) and all(out["record_same"]), out
    seen = out["seen"]
    assert seen["rebills"] > 0 and seen["activations"] > 0 and seen["payouts"] > 0 and seen["resets"] > 0, seen
    assert seen["broke_even"] > 0 and seen["lost"] > 0 and seen["never"] > 0, seen
    assert out["break_even_same"] and out["arrivals_same"] and out["u1_money_problems"] == [], out
    assert out["u1_money_planted"] and all("starts differ" in p for p in out["u1_money_planted"]), out
    assert out["refusals"] == {"record_days_twice": True, "activation_on_pass": True, "placement_on": True}, out
    assert out["judged_first_year"] == US.JUDGED_FIRST_YEAR


#: the only kinds of line the script prints: no count, no share, no money
PRINTED = ("the inputs of ", "identity HOLDS: ", "identity FAILS: ", "timing: ", "  Q-86 ", "    ", "REFUSED (Q-86)",
           "every identity holds; the pipeline ran", "written: ", "peak working set")


def test_the_scripts_pipeline_on_a_synthetic_campaign():
    out = _synthetic("pipeline")
    holds, fails, f = out["holds"], out["fails"], out["frame"]
    assert holds["rc"] == 0 and holds["written"] and "every identity holds; the pipeline ran" in holds["stdout"], holds
    assert holds["stdout"].count("identity HOLDS") == 10 and "FAILS" not in holds["stdout"], holds["stdout"]
    for line in holds["stdout"].splitlines() + fails["stdout"].splitlines():
        assert line.startswith(PRINTED), line
    assert out["authorised"] == [["P-14", "P-15", "P-16"], ["P-14", "P-15", "P-16"]]
    assert [c[:3] for c in out["compared"][:6]] == [["p14", "verdict", 3], ["p14", "point", 3], ["p15", "verdict", 3],
                                                     ["p15", "point", 3], ["p16", "verdict", 3], ["p16", "point", 3]]
    assert f["name"] == "user_spend" and f["columns"] == list(US.COLUMNS) and f["problems"] == [], f
    assert f["designs"] == ["p14", "p15", "p16"] and f["arms"] == ["point", "verdict"] and f["temp"], f
    assert set(f["sections"]) == set(US.SECTIONS) and f["identity_rows"] == 10
    assert f["seed"] == 20261920 and f["variant_count"] == 6 and f["exploratory"] is True
    assert {"seeds", "replay", "conventions", "u1_reference", "read", "windows", "tolerance"} <= set(f["parameters"])
    assert fails["rc"] == 3 and not fails["written"] and "identity FAILS" in fails["stdout"], fails
    assert "1 of 3 starts differ" in fails["stdout"] and "123.456" not in fails["stdout"]
    assert "REFUSED (Q-86): nothing written" in fails["stdout"]


# ------------------------------------------------------------------------------------------------ the reader

A1E, A1D = "vendor/stage2/data/atlas/A1/events.parquet", "vendor/stage2/data/atlas/A1/days.parquet"
A3W = "vendor/stage2/data/atlas/A3/walks.parquet"
BARS = "vendor/stage2/data/bars/NQ/bars.parquet"
A1A3 = (A1E, A1D, A3W)
ALL4 = (A1E, A1D, A3W, BARS)
ROW = US.READ_ROW

DRIVER = r'''
"""Q-86's test driver (tests/test_user_spend.py): scripts/user_spend.py's main on this temporary tree, the reader and
the clean-run check pointed at it, the first step after the authorisation a recorder that stops the run."""
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


spec = importlib.util.spec_from_file_location("q86_script", REPO / "scripts" / "user_spend.py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)
M.VENDOR = TREE / "vendor" / "stage2"
M.I.u1_reference = stop("u1_reference")


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
           ["--check", "--designs", "p13"], ["--check", "--workers", "3"])
INSIDE = ([], ["--check", "--starts", "4", "--designs", "p15"])


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def real_row() -> str | None:
    return R.decision_row((ROOT / "DECISIONS.md").read_text(encoding="utf-8"), ROW)


def log(rows: list[str]) -> str:
    head = "# Decisions (a temporary tree, Q-86's tests)\n\n| id | date | decision | basis |\n|---|---|---|---|\n"
    # Q-194b: after the joint held-out test's verdict, so the reader's rule 3 decides each read here
    return head + "".join(line + "\n" for line in [*rows, *VR.VERDICT_ROWS])


def tokened(line: str, designs: str) -> str:
    """Q-158 (the reader's held-out rule 3): the row with a read token naming `designs` and the driver as the first
    text of its third cell -- the row as a new held-out read needs it."""
    cells = line.split("|")
    cells[3] = f" heldout-read: {designs} by scripts/q86_driver.py --{cells[3]}"
    return "|".join(cells)


def make_tree(base: Path, name: str, decisions: str) -> Path:
    t = base / "runs" / name
    (t / "scripts").mkdir(parents=True)
    (t / "scripts" / "q86_driver.py").write_text(DRIVER, encoding="utf-8")
    (t / "DECISIONS.md").write_bytes(decisions.encode("utf-8"))
    manifest = []
    for rel in ALL4:
        p = t / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(f"a stand-in for {rel} (Q-86's tests; never parsed)\n".encode("utf-8"))
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
    base = tmp_path_factory.mktemp("q86")
    row = real_row()
    assert row is not None
    t = make_tree(base, "q86-reads", log([tokened(row, "P-14,P-15,P-16")]))
    name = t.name
    clean = {"S2X_CLEAN_RUN": name, "S2X_RUN_ID": f"{name}@q86-sim"}
    no_p15 = tokened(row.replace("P-15", "the first coin"), "P-14,P-16")
    missing = log(["| E-904 | 2026-11-16 | **A row about nothing in particular** | test |"])
    phases = [{"name": "outside", "env": {}, "runs": [list(x) for x in OUTSIDE]},
              {"name": "inside", "env": clean, "runs": [list(x) for x in INSIDE]},
              {"name": "no_p15", "decisions": log([no_p15]), "env": {}, "runs": [["--check", "--starts", "4"]]},
              {"name": "no_p15_p14_only", "env": clean, "runs": [["--check", "--starts", "4", "--designs", "p14"]]},
              {"name": "untokened", "decisions": log([row]), "env": clean, "runs": [["--check", "--starts", "4"]]},
              {"name": "missing", "decisions": missing, "env": clean, "runs": [[]]}]
    cfg = base / "q86.json"
    cfg.write_text(json.dumps({"repo": str(ROOT), "phases": phases}), encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k not in ("S2X_CLEAN_RUN", "S2X_RUN_ID")}
    env.update(ENV)
    r = subprocess.run([sys.executable, "scripts/q86_driver.py", str(cfg)], cwd=t, capture_output=True, text=True,
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


def test_the_row_the_reading_names_exists_and_names_the_three_designs():
    row = real_row()
    assert row is not None, f"{ROW} is no decision row of DECISIONS.md"
    for d in ("P-14", "P-15", "P-16"):
        assert R.names_design(row, d), f"{ROW}'s row does not name {d}"
    src = (ROOT / "scripts" / "user_spend.py").read_text(encoding="utf-8")
    assert "READ_ROW = US.READ_ROW" in src or re.search(rf'READ_ROW = "{ROW}"', src)


def test_outside_a_clean_run_the_check_authorises_once_is_refused_before_any_work_and_ledgers_nothing(reads):
    """Q-158 (the reader's held-out rule 3): the whole window reaches the held-out years, so outside a clean run the
    read is refused, even under a row whose token names it."""
    rs = _phase(reads, "outside")
    for r, designs in ((rs[0], ["P-14", "P-15", "P-16"]), (rs[1], ["P-14"])):
        a = _auth(r)
        assert "error" not in r and r.get("rc") == 3 and "stopped" not in r, _explain(r)
        assert "REFUSED" in r["stdout"] and "held-out rule 3" in r["stdout"], _explain(r)
        assert len(a) == 1 and r["events"].index(a[0]) == 0 and _work(r) == [], _explain(r)
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
    for r, designs, files in ((rs[0], ["P-14", "P-15", "P-16"], ALL4), (rs[1], ["P-15"], ALL4)):
        assert "error" not in r and r.get("stopped") == "u1_reference", _explain(r)
        assert r["prefix_kept"] and len(r["new"]) == 1, _explain(r)
        line = r["new"][0]
        assert line["purpose"] == "registered_design" and line["repeat"] is None
        assert line["declaration"] == {"ref": ROW, "sha256": None, "kind": "registered_design", "designs": designs}
        assert line["dates"] == {"start": "2020-01-02", "end": "2026-07-16", "blocks": ["choice", "judged"],
                                 "judged_first": "2024-01-02", "judged_last": "2026-07-16"}
        got = [f["path"] for f in line["what"]["files"]]
        assert sorted(got) == sorted(files)
        who = line["who"]
        assert who["script"] == "scripts/q86_driver.py" and who["clean_run"] == tree.name and who["dirty"] is False
        assert "scripts/user_spend.py:" in who["caller"].replace("\\", "/") and who["caller"].endswith(":main")
    # the inside phase's two lines and no_p15_p14_only's one (Q-158: that phase runs inside the clean run too)
    assert len(R.read_ledger(tree / R.LEDGER_REL)) == 3


def test_a_row_that_does_not_admit_the_reading_is_refused_and_nothing_starts(reads):
    for name, why in (("no_p15", "does not name P-15"), ("missing", "no decision row")):
        r = _phase(reads, name)[0]
        assert r.get("rc") == 3 and "error" not in r and "stopped" not in r, _explain(r)
        assert "REFUSED" in r["stdout"] and why in r["stdout"], _explain(r)
        assert _work(r) == [] and r["new"] == [] and r["prefix_kept"]
    r = _phase(reads, "no_p15_p14_only")[0]                    # the same row still admits P-14 alone
    assert r.get("stopped") == "u1_reference" and _auth(r)[0]["design"] == ["P-14"], _explain(r)
    r = _phase(reads, "untokened")[0]                          # Q-158: the row as it stands admits no new held-out read
    assert r.get("rc") == 3 and "error" not in r and "stopped" not in r, _explain(r)
    assert "REFUSED" in r["stdout"] and "held-out rule 3" in r["stdout"], _explain(r)
    assert _work(r) == [] and r["new"] == [] and r["prefix_kept"]


# ------------------------------------------------------------------------------------------------ the pipeline (slow)


@pytest.mark.slow
@pytest.mark.heavy         # Q-134: reads the real bars or atlas; the lock guard skips it while run.lock is held
def test_the_pipeline_on_four_starts():
    """`--check --starts 4`: every identity holds (U1's start rows at 4 starts with the day recorder on, the ledger and
    the money against U1's columns, the frame) and the file is written to a temporary folder only. Reads the real bars
    (P-15's and P-16's walks): the slow tier, under the run lock."""
    if not ((DATA / "bars").is_dir() and (DATA / "atlas").is_dir()):
        pytest.skip("bars and atlas not copied (scripts/vendor_stage2.py --data)")
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "user_spend.py"), "--check", "--starts", "4"],
                       capture_output=True, text=True, timeout=3600)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    assert "every identity holds; the pipeline ran" in r.stdout and "FAILS" not in r.stdout, r.stdout
    assert r.stdout.count("identity HOLDS") == 10, r.stdout         # 3 builds, 6 replays, the frame
