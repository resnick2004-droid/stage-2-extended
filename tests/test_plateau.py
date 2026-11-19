"""Wave 3.4: the plateau check (`extended/plateau.py`), on planted plateaus and spikes.

What is asserted: a planted plateau is accepted and a planted spike refused, with the reason; the side rule (`worse`
against `two_sided`) reads a slope as declared; too few neighbours refuses; a neighbour outside the bounds is skipped
and one the space refuses is a refused cell; every neighbour read is a `plateau` cell; neighbours are read on the
finalist's own blocks and seeds, and a reading on other blocks stops the check; a held-out finalist, a held-out
neighbour reading and a prediction are refused; a categorical's cells and a drawn box neighbourhood work and the box
is reproducible from its seed. **Mutations**: the tolerance test always true, the side ignored, the echo check removed.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import search_toys as TY  # noqa: E402

from extended import plateau as PL  # noqa: E402
from extended import search_space as SS  # noqa: E402
from extended import surrogate as SG  # noqa: E402

CENTRE = {"x1": 0.5, "x2": 0.5, "x3": 0.5, "n": 4, "c": "b"}
CORNER = {"x1": 0.0, "x2": 0.0, "x3": 0.0, "n": 1, "c": "a"}
STEPS = {"x1": 0.05, "x2": 0.05, "x3": 0.05, "n": 1}
LSEED = 9


def rule(**kw):
    base = dict(steps=STEPS, radius=1, tolerance=0.1, side="worse", min_share=1.0, min_neighbours=4)
    base.update(kw)
    return PL.PlateauRule(**base)


def plateau_fn(d):
    """Flat (zero) within 0.2 of the centre on every real lever and n within 1; a bowl outside."""
    dist = max(abs(d["x1"] - 0.5), abs(d["x2"] - 0.5), abs(d["x3"] - 0.5), abs(d["n"] - 4) / 5.0)
    return 0.0 if dist <= 0.2 else (dist - 0.2) * 5.0


def spike_fn(d):
    """One everywhere but at the centre itself, minus one."""
    return -1.0 if SS.design_id(d) == SS.design_id(CENTRE) else 1.0


def slope_fn(d):
    return 10.0 * d["x1"]


def run(fn, design=CENTRE, r=None, evaluate=None, **kw):
    led = SS.CellLedger()
    v = PL.check(TY.reading(design, fn(design)), TY.toy_space(), r or rule(), evaluate or TY.evaluator(fn),
                 ledger=led, ledger_seed=LSEED, **kw)
    return v, led


# ------------------------------------------------------------------------------------------------ the verdicts


def test_a_planted_plateau_is_accepted():
    v, led = run(plateau_fn)
    assert v.accepted and v.reason.startswith("accepted") and v.evaluated == 8 and v.held == 8
    assert led.counts()["by_role"] == {"plateau": 8} and {r["seed"] for r in led.rows} == {LSEED}


def test_a_planted_spike_is_refused_with_its_reason():
    v, _ = run(spike_fn)
    assert not v.accepted
    assert v.reason.startswith("refused: a spike") and "0 of 8" in v.reason and "+2" in v.reason
    assert v.share == 0.0 and all(not n["holds"] for n in v.neighbours)


def test_the_side_rule_reads_a_slope_as_declared():
    worse, _ = run(slope_fn)                                     # x1 - 1 step is better by 0.5: it holds under 'worse'
    assert not worse.accepted and worse.held == 7
    both, _ = run(slope_fn, r=rule(side="two_sided"))
    assert not both.accepted and both.held == 6
    loose, _ = run(slope_fn, r=rule(tolerance=0.6, side="two_sided"))
    assert loose.accepted
    share, _ = run(slope_fn, r=rule(min_share=0.85))
    assert share.accepted and share.share == pytest.approx(7 / 8)


def test_too_few_neighbours_refuses_and_outside_is_skipped():
    v, led = run(plateau_fn, design=CORNER, r=rule(min_neighbours=5))
    assert not v.accepted and "fewer than" in v.reason
    assert v.skipped["outside"] == 4 and v.evaluated == 4 and led.counts()["cells"] == 4


def test_a_neighbour_the_space_refuses_is_a_refused_cell():
    sp = TY.slot_space(routing=("longest_wait", "fewest_trades"))
    d = {k: None for k in sp.names()}
    d.update({"routing": "longest_wait", "risk": 500.0, "s1.0.on": "on", "s1.0.T1": "a", "s1.0.T4": 5,
              "s1.0.first": 10, "s1.0.last": 40, "s1.1.on": "on", "s1.1.T1": "b", "s1.1.T4": None,
              "s1.1.first": 45, "s1.1.last": 60, "s2.0.on": "off"})
    assert sp.check(d) is None
    led = SS.CellLedger()
    r = PL.PlateauRule(steps={"s1.1.first": 5, "s1.0.last": 5, "risk": 50.0}, radius=1, tolerance=1.0,
                       side="worse", min_share=1.0, min_neighbours=3)
    v = PL.check(TY.reading(d, 0.0), sp, r, TY.evaluator(lambda x: 0.0), ledger=led, ledger_seed=LSEED)
    assert v.skipped["refused"] == 2                     # s1.1.first - 5 and s1.0.last + 5 collide
    assert led.counts()["by_class"] == {"collision": 2} and v.evaluated == 4 and v.accepted


def test_categorical_cells_and_a_drawn_box():
    v, _ = run(plateau_fn, r=rule(steps={"c": PL.CELLS}, min_neighbours=2))
    assert v.evaluated == 2 and {n["moved"] for n in v.neighbours} == {"c -> 'a'", "c -> 'c'"}
    box = rule(neighbourhood="box", draws=12, radius=2)
    a, _ = run(plateau_fn, r=box, seed=5)
    b, _ = run(plateau_fn, r=box, seed=5)
    c, _ = run(plateau_fn, r=box, seed=6)
    assert [n["id"] for n in a.neighbours] == [n["id"] for n in b.neighbours] != [n["id"] for n in c.neighbours]
    assert a.evaluated + a.skipped["outside"] == 12
    with pytest.raises(PL.PlateauRefused):
        run(plateau_fn, r=box)                            # a drawn box needs its seed


def test_the_rule_is_validated():
    for bad in (dict(side="either"), dict(radius=0), dict(tolerance=-1.0), dict(min_share=0.0),
                dict(min_neighbours=0), dict(neighbourhood="ball"), dict(neighbourhood="box", draws=0)):
        with pytest.raises(PL.PlateauRefused):
            rule(**bad)
    for steps in ({"n": 0.5}, {"c": 1}, {"x1": 0.0}):
        with pytest.raises(PL.PlateauRefused):
            run(plateau_fn, r=rule(steps=steps))


# ------------------------------------------------------------------------------------------------ the protocol


def test_neighbours_are_read_on_the_finalists_blocks_and_seeds():
    seen = []

    def evaluate(design, *, blocks, seeds):
        seen.append((blocks, seeds))
        return TY.reading(design, plateau_fn(design), blocks=blocks, seeds=seeds)

    run(plateau_fn, evaluate=evaluate)
    assert seen and set(seen) == {(TY.BLOCKS, TY.SEEDS)}

    def other_blocks(design, *, blocks, seeds):
        return TY.reading(design, plateau_fn(design), blocks=TY.OTHER_BLOCKS, seeds=seeds)

    with pytest.raises(PL.PlateauRefused):
        run(plateau_fn, evaluate=other_blocks)

    def other_design(design, *, blocks, seeds):
        return TY.reading(CENTRE, 0.0, blocks=blocks, seeds=seeds)

    with pytest.raises(PL.PlateauRefused):
        run(plateau_fn, evaluate=other_design)


def test_held_out_finalists_and_readings_and_predictions_are_refused():
    led = SS.CellLedger()
    for tag in ("held_out", "judged"):
        with pytest.raises(SS.HeldOutInput):
            PL.check(TY.reading(CENTRE, 0.0, tag=tag), TY.toy_space(), rule(), TY.evaluator(plateau_fn), ledger=led,
                     ledger_seed=LSEED)

    def held(design, *, blocks, seeds):
        return TY.reading(design, 0.0, blocks=blocks, seeds=seeds, tag="held_out")

    with pytest.raises(SS.HeldOutInput):
        PL.check(TY.reading(CENTRE, 0.0), TY.toy_space(), rule(), held, ledger=led, ledger_seed=LSEED)
    sg = SG.Surrogate(TY.toy_space(), seed=3, restarts=0)
    with pytest.raises(SS.HeldOutInput):
        PL.check(sg, TY.toy_space(), rule(), TY.evaluator(plateau_fn), ledger=led, ledger_seed=LSEED)
    with pytest.raises(PL.PlateauRefused):
        PL.check(TY.reading(dict(CENTRE, n=9), 0.0), TY.toy_space(), rule(), TY.evaluator(plateau_fn), ledger=led,
                 ledger_seed=LSEED)


# ------------------------------------------------------------------------------------------------ mutations


def test_mutation_tolerance_always_true_is_caught(monkeypatch):
    monkeypatch.setattr(PL, "holds", lambda delta, r: True)
    v, _ = run(spike_fn)
    assert v.accepted                                     # the spike test would fail


def test_mutation_side_ignored_is_caught(monkeypatch):
    monkeypatch.setattr(PL, "holds", lambda delta, r: abs(delta) <= r.tolerance)
    v, _ = run(slope_fn)
    assert v.held != 7                                    # the side test would fail


def test_mutation_echo_check_removed_is_caught(monkeypatch):
    monkeypatch.setattr(PL, "echoes", lambda got, design, f: True)

    def other_blocks(design, *, blocks, seeds):
        return TY.reading(design, plateau_fn(design), blocks=TY.OTHER_BLOCKS, seeds=seeds)

    v, _ = run(plateau_fn, evaluate=other_blocks)        # no PlateauRefused: the protocol test would fail
    assert v.evaluated == 8
