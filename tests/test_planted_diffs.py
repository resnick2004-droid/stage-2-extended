"""Q-196: the planted-difference check (`extended/planted_diffs.py`, `scripts/planted_diffs.py`) on synthetic data only
(no bar, no atlas, no result file). Pure parts in this process: the declared starts (six; at n = 1034 the starts
0, 399, 777, 782, 874, 934), the date refusals (past 2023-12-29; the confirmation window named), the plans and their
expectations (each kind's replay, span and horizons; a start without an event, or with its first event past its last
horizon, carries no forced plant; `late_long` only where a session follows the last horizon), the perturbations (a
blanked block holds no trade, a stopped block only full stops, NaN targets kept), the planter (exactly the one replay
named perturbed, any other start's or slice's replay refused, restored after), the oracle, the counting layer's check,
`cannot` and the verdict. The engine's part runs in a process of its own (`tests/planted_synthetic.py`): the check
holds on a synthetic campaign under both responses, every mutant of the comparator and of the planter fails it, a
campaign with no event cannot show power (verdict 6), and the refusals come before any run. The script refuses an
argument before any read. No seed (nothing is drawn).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import types
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pytest

from extended import exact_run_diffs as X
from extended import planted_diffs as PD

ROOT = Path(__file__).resolve().parent.parent
SYN = ROOT / "tests" / "planted_synthetic.py"


@dataclass(frozen=True)
class Blk:
    """A stand-in day block (the perturbations are generic over a dataclass's fields)."""

    pnl: np.ndarray
    risked: np.ndarray
    exit_reasons: tuple
    mae: np.ndarray | None = None
    r_by_rr: dict | None = None
    mae_by_rr: dict | None = None
    entry_t: np.ndarray | None = None

    def __len__(self) -> int:
        return len(self.pnl)


def blk(i: int) -> Blk:
    return Blk(pnl=np.array([100.0 * (i + 1), -50.0]), risked=np.array([50.0, 50.0]), exit_reasons=("target", "stop"),
               mae=np.array([10.0, np.nan]), r_by_rr={1.0: np.array([1.0, -1.0]), 2.0: np.array([np.nan, -1.0])},
               mae_by_rr={1.0: np.array([0.2, 1.0]), 2.0: np.array([np.nan, 1.0])}, entry_t=np.array([1.0, 2.0]))


# ------------------------------------------------------------------------------------------------ starts and dates


def test_the_declared_starts():
    assert PD.declared_starts(1034) == {0: "control", 399: "control", 777: "control", 782: "cut", 874: "cut",
                                        934: "cut"}
    st = PD.declared_starts(347)
    assert st == {0: "control", 42: "control", 84: "control", 95: "cut", 187: "cut", 247: "cut"}
    groups = X.choose_starts(347)
    assert all(groups[s] == g for s, g in st.items())
    with pytest.raises(PD.PlantRefused):
        PD.declared_starts(253)                      # one control start only
    assert PD.long_length(934, 1034) == 100 and PD.long_length(0, 1034) == 252


def test_the_dates_are_refused_past_the_search_years_and_in_the_confirmation_window():
    ok = ["2023-12-27", "2023-12-28", "2023-12-29"]
    assert PD.date_problems(ok) == [] and PD.date_problems(ok, [(0, 2)]) == []
    late = PD.date_problems([*ok, "2024-01-02"])
    assert len(late) == 1 and "past 2023-12-29" in late[0]
    conf = PD.date_problems([*ok, "2026-07-17"])
    assert any("confirmation window" in x for x in conf) and any("past 2023-12-29" in x for x in conf)
    assert PD.date_problems(ok, [(1, 3)]) and PD.date_problems(ok, [(-1, 1)])
    with pytest.raises(PD.PlantRefused, match="confirmation window"):
        PD.refuse_dates(["2026-07-20"])
    with pytest.raises(PD.PlantRefused):
        PD.refuse_dates(["2024-01-02"])
    assert PD.LAST_DAY.isoformat() == "2023-12-29" and PD.CONFIRMATION_START.isoformat() == "2026-07-17"


# ------------------------------------------------------------------------------------------------ the plans


def by_kind(ps):
    return {p.kind: p for p in ps}


def test_the_plans_and_their_expectations():
    n = 1034
    ps = by_kind(PD.plans_for(0, "control", n, [21, 63, 90, 126], 30))
    assert set(ps) == set(PD.KINDS)
    b = ps["blank_exact"]
    assert (b.target, b.length, b.span, b.expected) == ("exact", 63, (0, 30), (63,))
    s = ps["stops_exact"]
    assert (s.target, s.length, s.span, s.expected) == ("exact", 63, (0, 30), (63,))
    bl = ps["blank_long"]
    assert (bl.target, bl.length, bl.span, bl.expected) == ("long", 252, (0, 30), (63, 90, 126))
    sh = ps["shift_exact"]
    assert (sh.target, sh.length, sh.expected) == ("exact", 126, None)
    ll = ps["late_long"]
    assert (ll.target, ll.length, ll.span, ll.expected) == ("long", 252, (127, 251), ())
    # an event on the horizon itself: the whole exact run emptied
    ps = by_kind(PD.plans_for(0, "control", n, [21, 63, 90, 126], 21))
    assert ps["blank_exact"].span == (0, 20) and ps["blank_exact"].expected == (21,)
    assert ps["blank_long"].span == (0, 21) and ps["blank_long"].expected == (21, 63, 90, 126)
    # a cut start, L = 100: checked at 21, 63, 90; late_long over sessions 91 .. 99
    ps = by_kind(PD.plans_for(934, "cut", n, [21, 63, 90], 70))
    assert ps["blank_exact"].length == 90 and ps["blank_long"].expected == (90,)
    assert ps["late_long"].span == (91, 99) and ps["shift_exact"].length == 90
    # L = 91: no session after the last horizon, so no late_long
    assert "late_long" not in by_kind(PD.plans_for(943, "cut", n, [21, 63, 90], 5))
    # no event, or the first after the last horizon: no forced plant
    for d in (None, 127):
        assert set(by_kind(PD.plans_for(0, "control", n, [21, 63, 90, 126], d))) == {"shift_exact", "late_long"}
    # nothing checked: no plan; checked off the runner's rule: refused
    assert PD.plans_for(1034 - 21, "cut", n, [], 3) == []
    with pytest.raises(PD.PlantRefused):
        PD.plans_for(0, "control", n, [21, 63], 3)
    assert PD.plant_horizon(None, [21]) is None and PD.plant_horizon(22, [21, 63]) == 63
    assert PD.first_event({"pass_days": [9, 40], "funded_days": [12], "pay_days": []}) == 9
    assert PD.first_event({"pass_days": [], "funded_days": [], "pay_days": [7]}) == 7
    assert PD.first_event({"pass_days": [], "funded_days": [], "pay_days": []}) is None


def test_cannot_and_the_verdict():
    n = 1034
    good = (PD.plans_for(0, "control", n, [21, 63, 90, 126], 10) + PD.plans_for(399, "control", n, [21, 63, 90, 126], 5)
            + PD.plans_for(782, "cut", n, [21, 63, 90, 126], 50))
    assert PD.cannot_problems(good, "off") == []
    two = PD.plans_for(0, "control", n, [21, 63, 90, 126], 10) + PD.plans_for(782, "cut", n, [21, 63, 90, 126], 5)
    assert PD.cannot_problems(two, "off")                        # fewer than three
    one_group = (PD.plans_for(0, "control", n, [21, 63, 90, 126], 10)
                 + PD.plans_for(399, "control", n, [21, 63, 90, 126], 5)
                 + PD.plans_for(777, "control", n, [21, 63, 90, 126], 5)
                 + PD.plans_for(782, "cut", n, [21, 63, 90, 126], None))
    assert PD.cannot_problems(one_group, "off") == ["off: no cut start carries the forced plants"]
    assert PD.verdict({"failures": [], "cannot": []}) == 0
    assert PD.verdict({"failures": ["x"], "cannot": ["y"]}) == 1
    assert PD.verdict({"failures": [], "cannot": ["y"]}) == 6


# ------------------------------------------------------------------------------------------------ the perturbations


def test_a_blanked_block_holds_no_trade_and_a_stopped_block_only_full_stops():
    b = blk(0)
    e = PD.blank_block(b)
    assert len(e) == 0 and e.exit_reasons == () and len(e.risked) == 0 and len(e.mae) == 0 and len(e.entry_t) == 0
    assert set(e.r_by_rr) == {1.0, 2.0} and all(len(v) == 0 for v in e.r_by_rr.values())
    assert len(b) == 2                                          # the original untouched
    s = PD.stops_block(b)
    assert list(s.pnl) == [-50.0, -50.0] and s.exit_reasons == ("stop", "stop")
    assert list(s.r_by_rr[1.0]) == [-1.0, -1.0]
    assert np.isnan(s.r_by_rr[2.0][0]) and s.r_by_rr[2.0][1] == -1.0      # a target not permitted stays so
    assert s.mae[0] == 50.0 and np.isnan(s.mae[1])
    assert list(s.mae_by_rr[1.0]) == [1.0, 1.0] and np.isnan(s.mae_by_rr[2.0][0])
    assert list(s.entry_t) == [1.0, 2.0] and list(b.pnl) == [100.0, -50.0]
    with pytest.raises(PD.PlantRefused):
        PD.blank_block(("not", "a", "dataclass"))


def test_the_perturbed_replay():
    jb = [blk(i) for i in range(10)]
    p = PD.plans_for(0, "control", 300, [21, 63, 90, 126], 2)[0]   # blank_exact; span (0, 2)
    given = jb[3:8]
    out = PD.perturbed(PD.Plan("blank_exact", 3, "control", "exact", 5, (0, 2), (5,)), jb, given)
    assert [len(x) for x in out] == [0, 0, 0, 2, 2] and out[3] is jb[6] and out[4] is jb[7]
    sh = PD.perturbed(PD.Plan("shift_exact", 3, "control", "exact", 5, (0, 4), None), jb, given)
    assert all(a is b for a, b in zip(sh, jb[4:9])) and len(sh) == 5
    with pytest.raises(PD.PlantRefused):
        PD.perturbed(PD.Plan("shift_exact", 5, "control", "exact", 5, (0, 4), None), jb, jb[5:10])
    assert p.kind == "blank_exact"


class FakeB:
    """`user_beside`'s two names the planter reads: `replay` (here: returns its blocks) and `start_seed`."""

    def __init__(self):
        self.replay = self._real

    @staticmethod
    def _real(blocks, args, seed):
        return list(blocks)

    @staticmethod
    def start_seed(s):
        return 1000 + int(s)


def test_the_planter_perturbs_only_the_replay_it_names():
    n = 300
    jb = [blk(i) for i in range(n)]
    job = {"blocks": jb}
    B = FakeB()
    real = B.replay
    plan = PD.plans_for(10, "control", n, [21, 63, 90, 126], 4)[0]      # blank_exact at 21, sessions 0 .. 4
    with PD.Planter(B, job, plan) as pl:
        long_ = B.replay(jb[10:262], None, 1010)
        ex = {h: B.replay(jb[10:10 + h], None, 1010) for h in (21, 63, 90, 126)}
    assert B.replay is real and pl.applied == 1 and pl.calls == [252, 21, 63, 90, 126]
    assert [len(x) for x in ex[21][:6]] == [0, 0, 0, 0, 0, 2]
    for h in (63, 90, 126):
        assert all(a is b for a, b in zip(ex[h], jb[10:10 + h]))
    assert all(a is b for a, b in zip(long_, jb[10:262])) and pl.long_run is long_ and pl.planted_run is ex[21]
    bl = [p for p in PD.plans_for(10, "control", n, [21, 63, 90, 126], 4) if p.kind == "blank_long"][0]
    with PD.Planter(B, job, bl) as pl:
        long_ = B.replay(jb[10:262], None, 1010)
        ex21 = B.replay(jb[10:31], None, 1010)
    assert pl.applied == 1 and [len(x) for x in long_[:6]] == [0, 0, 0, 0, 0, 2] and len(ex21[0]) == 2
    with PD.Planter(B, job, plan):
        with pytest.raises(PD.PlantRefused):
            B.replay(jb[10:31], None, 1011)                   # another start's seed
        with pytest.raises(PD.PlantRefused):
            B.replay(list(jb[10:30]) + [blk(99)], None, 1010)  # not the start's slice of the job
        with pytest.raises(PD.PlantRefused):
            B.replay(jb[11:32], None, 1010)                   # the slice of another start
    assert B.replay is real


def test_the_oracle_reads_event_days_up_to_h():
    a = (None, 0.0, [5, 40], [6], [30, 70])
    b = (None, 0.0, [5, 41], [6], [30])
    assert PD.events_upto(a, 21) == ((5,), (6,), ())
    assert PD.oracle_differs(a, b, 39) == () and PD.oracle_differs(a, b, 40) == (40,)
    assert PD.oracle_differs(a, b, 70) == (70,)


def rec(s, passes=(5,), funded=(6,), pays=(30,)):
    return {"start_day": s, "start_date": f"d{s}", "pass_days": list(passes), "funded_days": list(funded),
            "pay_days": list(pays)}


def output(s, n, differs=(), alt=None):
    r = rec(s)
    if alt:
        r["alt"] = alt
    return {"rec": r, "checked": X.expected_checked(s, n), "differs": list(differs), "pay_bad": 0, "cash_bad": 0,
            "fee_bad": 0, "record_same": True}


def test_the_counting_layers_check():
    n = 1034
    p = PD.plans_for(0, "control", n, [21, 63, 90, 126], 5)[0]          # blank_exact at 21
    o = output(0, n, [21], {"21": rec(0, passes=(), funded=(), pays=())})
    assert PD.count_problems(o, p, n, (21,), "p14", "point", "off") == []
    assert PD.count_problems(o, p, n, (63,), "p14", "point", "off")
    assert PD.count_problems(output(0, n), p, n, (21,), "p14", "point", "off")
    refused = output(0, n, [21])                                           # no exact record: the count refuses
    assert "refused" in PD.count_problems(refused, p, n, (21,), "p14", "point", "off")[0]
    pl = types.SimpleNamespace(applied=1, planted_run=None, long_run=None)
    probs, exp = PD.plan_problems(o, p, pl, n, "p14", "point", "off")
    assert probs == [] and exp == (21,)
    missed = PD.plan_problems(output(0, n), p, pl, n, "p14", "point", "off")[0]
    assert "off start 0 blank_exact: reported [], planted [21]" in missed          # named by the comparator's line
    assert any("counted [], planted [('control', 21)]" in x for x in missed)       # and by the count's
    pl.applied = 2
    assert PD.plan_problems(o, p, pl, n, "p14", "point", "off")[0]
    pl.applied = 1
    assert PD.plan_problems({**o, "fee_bad": 1}, p, pl, n, "p14", "point", "off")[0]
    assert PD.plan_problems({**o, "record_same": None}, p, pl, n, "p14", "point", "off")[0]
    sh = [q for q in PD.plans_for(0, "control", n, [21, 63, 90, 126], 5) if q.kind == "shift_exact"][0]
    assert PD.plan_problems(output(0, n), sh, pl, n, "p14", "point", "off")[0]   # the oracle has no runs


# ------------------------------------------------------------------------------------------------ the engine's part


@pytest.fixture(scope="module")
def got() -> dict:
    env = {**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    r = subprocess.run([sys.executable, str(SYN), str(ROOT)], capture_output=True, text=True, timeout=900, env=env,
                       cwd=str(ROOT))
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    return json.loads(r.stdout.strip().splitlines()[-1])


def test_the_check_holds_on_the_synthetic_campaign(got):
    m = got["main"]
    assert m["verdict"] == 0 and m["failures"] == [] and m["cannot"] == [], m
    assert all(c["held"] and c["starts"] == 6 for c in m["control"].values()) and set(m["control"]) == {"off",
                                                                                                         "denial_25"}
    for r in ("off", "denial_25"):
        k = {kind: m["kinds"][f"{r}|{kind}"] for kind in PD.KINDS}
        assert all(v["held"] for v in k.values()), k
        assert k["blank_exact"]["plants"] == k["stops_exact"]["plants"] == k["blank_long"]["plants"] == 6
        assert k["blank_exact"]["expected"] == 6 and k["late_long"]["expected"] == 0
        assert k["blank_long"]["expected"] > 6                       # several horizons per start
        assert m["groups_forced"][r] == {"cut": 3, "control": 3}


def test_a_later_first_event_is_planted_at_its_own_horizon(got):
    assert 21 < got["first_event_42"] <= 63
    plans = {k: (t, ln, span, exp) for k, t, ln, span, exp in got["plans_42"]}
    d = got["first_event_42"]
    assert plans["blank_exact"] == ("exact", 63, [0, d], [63])
    assert plans["blank_long"] == ("long", 252, [0, d], [63, 90, 126])


def test_every_mutant_of_the_comparator_and_the_planter_fails_the_check(got):
    mu = got["mutants"]
    assert set(mu) == {"blind", "wrong_horizon", "spurious", "inert", "swapped_count"}
    for name, r in mu.items():
        assert r["verdict"] == 1 and r["failures"] > 0, (name, r)
    assert "reports [21] unplanted" in mu["spurious"]["first"][0]                 # the control's own line
    assert "reported [], planted [" in mu["blind"]["first"][0]
    assert "reported [63], planted [21]" in mu["wrong_horizon"]["first"][0]


def test_a_campaign_without_events_cannot_pass(got):
    ne = got["no_events"]
    assert ne["verdict"] == 6 and ne["failures"] == [] and ne["control"]["off"]["held"], ne
    assert any("fewer than 3" in x for x in ne["cannot"])


def test_the_refusals_come_before_any_run(got):
    rf = got["refusals"]
    assert rf["late"] and "past 2023-12-29" in rf["late"]
    assert rf["confirmation"] and "confirmation window" in rf["confirmation"]
    assert rf["workers"] and "workers must be 1" in rf["workers"]


# ------------------------------------------------------------------------------------------------ the script


def test_the_script_refuses_an_argument_before_any_read():
    env = {k: v for k, v in os.environ.items() if k != "S2X_CLEAN_RUN"}
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "planted_diffs.py"), "--starts", "3"],
                       capture_output=True, text=True, timeout=600, cwd=str(ROOT), env=env)
    assert r.returncode == 2, (r.stdout[-800:], r.stderr[-800:])
    assert "built" not in r.stdout


def test_the_script_writes_nothing_and_reads_only_through_the_cut():
    src = (ROOT / "scripts" / "planted_diffs.py").read_text(encoding="utf-8")
    for call in ("read_parquet(", "read_bars(", "read_walks(", "read_csv(", "write_result(", "to_csv(", ".write_text(",
                 "open("):
        assert call not in src, call
    assert "SCI.build_point(SC.LAST_DAY)" in src and "SC.authorise(" in src
