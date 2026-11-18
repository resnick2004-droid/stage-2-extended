"""RD-05's T-10 and T-12 (`prereg/RD-05_firm_modes.md` 17.3; 10.1, 11, 12.6, 4.7 item 5): `k*` from A-13's counters
against a sort of hand-built day records; the last gate on hand-built gate records; the menu -- no P without its guard
row, every exposure printed for `flip` and `steady` alike, no cell withheld for conduct, the flags on synthetic menus.
Also the coin's `k*` on a toy flip run against the engine's own counters (`build_toys`). Fast.
"""
from __future__ import annotations

import numpy as np
import pytest

from extended import modes_engine as E
from extended import modes_reading as RD
from extended import modes_terms as M


def test_t10_k_star_from_counts_matches_a_sort() -> None:
    T, w, rf, r = 3000.0, 1.5, 1000.0, 250.0
    rng = np.random.default_rng([M.seed("build_toys"), 10])
    for _ in range(300):
        fw, sw = int(rng.integers(0, 4)), int(rng.integers(0, 12))
        days = [w * rf] * fw + [w * r] * sw + list(-rng.uniform(1, 500, size=int(rng.integers(0, 6))))
        rng.shuffle(days)
        want = RD.k_star_from_days(days, T)
        got = int(RD.k_star_from_counts(np.array([fw]), np.array([sw]), T, w, rf, r)[0])
        assert got == want, (fw, sw, got, want)
    assert RD.k_star_steady(3000.0, 2.0, 500.0) == 3 and RD.k_star_steady(3000.0, 3.0, 1000.0) == 1


def test_t10_k_star_on_a_toy_flip_run() -> None:
    t = M.eval_terms("TS-S")
    spec = E.EvalSpec(t, 1.0, 500.0, policy="flip")
    out = E.run_eval(spec, 2000, np.random.default_rng([M.seed("build_toys"), 11]))
    p = out["passed"]
    ks = RD.k_star_from_counts(out["flip_wins"][p], out["steady_wins"][p], t.target, 1.0, spec.r_flip, 500.0)
    assert np.all(ks >= 1)
    d = RD.k_star_distribution(ks)
    assert d["share_k_le2"] >= d["share_k1"] and d["n"] == int(p.sum())


def test_t10_last_gate_on_hand_built_records() -> None:
    assert RD.last_gate({"base_target": 3, "consistency_target": 5, "min_days": 2}, raised=True) == "consistency_target"
    assert RD.last_gate({"base_target": 3, "consistency_target": 3, "min_days": 3}, raised=False) == "base_target"
    assert RD.last_gate({"base_target": 1, "consistency_target": 1, "min_days": 3}, raised=False) == "min_days"
    assert RD.last_gate({"base_target": 4, "consistency_target": 4, "min_days": 2}, raised=True) == "base_target"
    assert RD.last_funded_gate({"winning_days": 6, "buffer_min": -1, "clock": 2}) == "winning_days"
    assert RD.last_funded_gate({"clock": 9, "buffer_min": 3}) == "clock"
    assert RD.last_funded_gate({"clock": -1}) is None
    assert RD.gate_shares(["a", "a", "b", ""]) == {"a": pytest.approx(2 / 3), "b": pytest.approx(1 / 3)}


def test_t10_engine_last_gate_and_causes() -> None:
    t = M.eval_terms("RE", M.STRICT)
    out = E.run_eval(E.EvalSpec(t, 1.0, 750.0), 2000, np.random.default_rng([M.seed("build_toys"), 12]))
    p = out["passed"]
    assert set(out["last_gate"][p]) <= set(RD.EVAL_GATES)
    assert set(out["cause"][~p]) <= {"floor", "lifespan", "inactivity", "censored"}
    assert not set(out["cause"][p]) - {""}


def _menu() -> list[dict]:
    base = []
    for pol in ("flip", "steady"):
        base.append({"cell": f"C-gross-{pol}", "part": "C", "coin": "gross", "policy": pol,
                     **RD.exposures_row(pol, {"stacking_share": 0.1}), "labels": "upper bound in fees"})
        base.append({"cell": f"C-costed-{pol}", "part": "C", "coin": "costed", "policy": pol,
                     **RD.exposures_row(pol, {"full_allowance_share": 0.2}), "labels": "price unverified: on the grid"})
    base.append({"cell": "F-1", "part": "F", "P": 0.4, "guard": {"m1": 1}, "policy": "steady",
                 **RD.exposures_row("steady", {}), "signs_by_block": [1, -1], "corner_values": (0.3, 0.5),
                 "reference": 0.4, "labels": "from the general article"})
    return base


def test_t12_the_menu_and_its_flags() -> None:
    cells = _menu()
    rows = RD.menu_rows(cells)
    assert RD.menu_problems(rows, cells) == []
    assert len(rows) == len(cells)                                   # nothing withheld for conduct
    g = next(r for r in rows if r["cell"] == "C-gross-flip")
    assert RD.FLAGS["gross"] in g["flags"] and RD.FLAGS["coin"] in g["flags"] and RD.FLAGS["fees_upper"] in g["flags"]
    c = next(r for r in rows if r["cell"] == "C-costed-steady")
    assert RD.FLAGS["gross"] not in c["flags"] and RD.FLAGS["price_grid"] in c["flags"]
    f = next(r for r in rows if r["cell"] == "F-1")
    for k in ("table_fixed", "unstable", "straddle", "general"):
        assert RD.FLAGS[k] in f["flags"]
    flip = {k for k in next(r for r in rows if r["cell"] == "C-gross-flip") if k in RD.EXPOSURES}
    steady = {k for k in next(r for r in rows if r["cell"] == "C-gross-steady") if k in RD.EXPOSURES}
    assert flip == steady == set(RD.EXPOSURES)
    assert "described, not carried" in {r["described"] for r in rows}


def test_t12_menu_problems_fire() -> None:
    cells = _menu()
    rows = RD.menu_rows(cells)
    assert RD.menu_problems(rows[:-1], cells)                         # a cell withheld
    bad = [dict(r) for r in rows]
    bad[-1]["guard"] = None
    assert any("guard" in p for p in RD.menu_problems(bad, cells))
    bad = [dict(r) for r in rows]
    del bad[0]["stacking_share"]
    assert any("exposure" in p for p in RD.menu_problems(bad, cells))
    bad = [dict(r) for r in rows]
    bad[0]["flags"] = ""
    assert RD.menu_problems(bad, cells)
    assert "a tenth" in RD.intervals_note(12)
