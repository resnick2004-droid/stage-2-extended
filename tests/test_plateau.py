"""Wave 3.4: the plateau check (`extended/plateau.py`), on planted plateaus and spikes, with and without seed noise.

What is asserted:
- **the comparison is with a re-read of the finalist on fresh declared seeds** (the red team's B-2): its size and power
  on noisy surfaces, against the declared targets below, over declared replications;
- a planted plateau is accepted and a planted spike refused, with the reason; the side rule (`worse` against
  `two_sided`), the margin and the share read a slope as declared;
- **every active lever is stepped** (a rule leaving one out is refused), dependent levers are repaired, too few
  neighbours in all or for one lever refuses, a neighbour outside the bounds is skipped and one the space refuses is a
  refused, reported cell;
- every neighbour is a `plateau:<finalist>` cell carrying the rule's sha256; **a second check of one finalist is
  refused**, under any rule (m-2);
- the finalist must be a counted survey or round cell on the declared protocol; neighbours and the re-read are read
  on the re-read protocol, whose seeds must be fresh; a held-out finalist or reading, a prediction, an uncounted
  finalist and a finalist on another protocol are all refused;
- a categorical's cells and a drawn box work, and the box is reproducible from its seed.
**Mutations**: the tolerance test always true, the side ignored, the echo check removed, `<=` made `<`, inactive
levers stepped.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import search_toys as TY  # noqa: E402

from extended import plateau as PL  # noqa: E402
from extended import search_space as SS  # noqa: E402
from extended import surrogate as SG  # noqa: E402

CENTRE = {"x1": 0.5, "x2": 0.5, "x3": 0.5, "n": 4, "c": "b"}
CORNER = {"x1": 0.0, "x2": 0.0, "x3": 0.0, "n": 1, "c": "a"}
STEPS = {"x1": 0.05, "x2": 0.05, "x3": 0.05, "n": 1, "c": PL.CELLS}
LSEED, SURVEY_SEED = 9, 4747
SD = 0.2                                              # per-seed noise of the planted checks


def rule(**kw):
    base = dict(steps=STEPS, radius=1, tolerance_se=PL.critical_z(0.05, 10), margin=0.0, side="worse",
                min_share=1.0, min_neighbours=4, min_per_lever=1)
    base.update(kw)
    return PL.PlateauRule(**base)


def plateau_fn(d):
    """Flat (zero) within 0.2 of the centre on every real lever and n within 1; a bowl outside; the cell ignored."""
    dist = max(abs(d["x1"] - 0.5), abs(d["x2"] - 0.5), abs(d["x3"] - 0.5), abs(d["n"] - 4) / 5.0)
    return 0.0 if dist <= 0.2 else (dist - 0.2) * 5.0


def spike_fn(d):
    """One everywhere but at the centre itself, minus one."""
    return -1.0 if SS.design_id(d) == SS.design_id(CENTRE) else 1.0


def slope_fn(d):
    return 10.0 * d["x1"]


def counted(design, space=None, role="survey"):
    """A ledger holding `design` as a counted cell of `role` (the test's own survey of one)."""
    led = SS.CellLedger()
    led.begin(role, SURVEY_SEED)
    led.record(space or TY.toy_space(), design, role=role, seed=SURVEY_SEED, refusal=None)
    return led


def run(fn, design=CENTRE, r=None, evaluate=None, sd=SD, space=None, **kw):
    space = space or TY.toy_space()
    led = counted(design, space)
    ev = evaluate or TY.evaluator(fn, sd)
    f = TY.evaluator(fn, sd)(design, protocol=TY.PROTOCOL)
    v = PL.check(f, space, r or rule(), ev, ledger=led, protocol=TY.PROTOCOL, reread=TY.REREAD, ledger_seed=LSEED,
                 **kw)
    return v, led


# ------------------------------------------------------------------------------------------------ size and power


#: the declared targets of the size-and-power test (the red team's setup, the lead's ruling): written before the run,
#: never tuned after it. The selection readings have sd 0.3 (16 seeds, per-seed sd 1.2); the finalist is the best of 64
#: on an exactly flat surface; the spike is 0.6 deep at the finalist; the re-read uses 64 fresh seeds; ten neighbours.
SIZE, POWER, REPS = 0.05, 0.90, 200
SEL_SEEDS = tuple(range(301, 317))
POWER_REREAD = tuple(range(401, 465))
PER_SEED_SD, SPIKE = 1.2, 0.6
POWER_SEED = 8128


def _fast(fn):
    """The runner of the size test: per-seed noise drawn once per (design, seed set)."""
    def evaluate(design, *, protocol):
        h = int(SS.design_id(design), 16) % (2 ** 63)
        e = np.random.default_rng([h, len(protocol.seeds), protocol.seeds[0]]).standard_normal(len(protocol.seeds))
        ps = fn(design) + PER_SEED_SD * e
        return TY.reading(design, float(np.mean(ps)), protocol=protocol, per_seed=list(ps),
                          se=float(np.std(ps, ddof=1) / np.sqrt(len(ps))))
    return evaluate


def size_and_power():
    sel = TY.PROTOCOL.with_seeds(SEL_SEEDS)
    rer = TY.PROTOCOL.with_seeds(POWER_REREAD)
    r = rule(tolerance_se=PL.critical_z(SIZE, 10))
    flat_ok = spike_refused = 0
    for s in np.random.SeedSequence(POWER_SEED).generate_state(REPS):
        led = SS.CellLedger()
        ds = SS.Sampler(TY.toy_space(), seed=int(s), method="sobol").survey(64, ledger=led)
        rs = [_fast(lambda d: 0.0)(d, protocol=sel) for d in ds]
        fin = min(rs, key=lambda x: x.value)
        spike_id = fin.id

        def spiky(d, spike_id=spike_id):
            return -SPIKE if SS.design_id(d) == spike_id else 0.0

        led2 = SS.CellLedger()
        SS.Sampler(TY.toy_space(), seed=int(s), method="sobol").survey(64, ledger=led2)
        flat = PL.check(fin, TY.toy_space(), r, _fast(lambda d: 0.0), ledger=led, protocol=sel, reread=rer,
                        ledger_seed=LSEED)
        fin_s = _fast(spiky)(fin.design, protocol=sel)
        spike = PL.check(fin_s, TY.toy_space(), r, _fast(spiky), ledger=led2, protocol=sel, reread=rer,
                         ledger_seed=LSEED)
        flat_ok += flat.accepted
        spike_refused += not spike.accepted
    return flat_ok / REPS, spike_refused / REPS


def test_size_and_power_on_noisy_surfaces():
    """The red team's B-2 probe, rerun under the re-read: a true plateau is accepted at about 1 - SIZE and a spike
    0.6 deep (twice the selection readings' sd) refused at least at POWER (the module docstring's arithmetic: the
    re-read's 64 seeds give about 0.96 against this spike). The band on the size is three binomial standard errors."""
    accept, power = size_and_power()
    se = (SIZE * (1 - SIZE) / REPS) ** 0.5
    assert abs(accept - (1 - SIZE)) <= 3 * se, accept
    assert power >= POWER, power


def test_critical_z_holds_its_size():
    for k in (1, 4, 10):
        c = PL.critical_z(0.05, k)
        assert PL.p_all_hold(c, k) == pytest.approx(0.95, abs=1e-6)
    assert PL.critical_z(0.05, 10) < 2.5679                              # below Sidak's, the shared re-read
    rng = np.random.default_rng(3)
    z = rng.standard_normal((40000, 1)) * np.sqrt(0.5) + rng.standard_normal((40000, 10)) * np.sqrt(0.5)
    assert abs(float(np.mean(z.max(axis=1) <= PL.critical_z(0.05, 10))) - 0.95) < 0.006


# ------------------------------------------------------------------------------------------------ the verdicts


def test_a_planted_plateau_is_accepted():
    v, led = run(plateau_fn)
    assert v.accepted and v.reason.startswith("accepted") and v.evaluated == 10 and v.held == 10
    role = f"plateau:{SS.design_id(CENTRE)}"
    assert led.counts()["by_role"] == {"survey": 1, role: 10}
    assert {r["seed"] for r in led.rows if r["role"] == role} == {LSEED}
    assert {r["rule"] for r in led.rows if r["role"] == role} == {rule().sha256()}
    assert v.form == PL.FORM and v.reread_seeds == TY.REREAD_SEEDS and v.rule == rule().sha256()
    assert v.per_lever == {"x1": 2, "x2": 2, "x3": 2, "n": 2, "c": 2} and v.libs == SS.LIBS


def test_a_planted_spike_is_refused_with_its_reason():
    v, _ = run(spike_fn)
    assert not v.accepted
    assert v.reason.startswith("refused: a spike") and "0 of 10" in v.reason
    assert v.share == 0.0 and all(not n["holds"] for n in v.neighbours)
    assert v.selection_value < 0 and v.reread_value < 0


def test_the_side_rule_the_margin_and_the_share_read_a_slope_as_declared():
    worse, _ = run(slope_fn)                       # x1 - 1 step is better by 0.5: it holds under 'worse'
    assert not worse.accepted and worse.held == 9
    both, _ = run(slope_fn, r=rule(side="two_sided"))
    assert not both.accepted and both.held == 8
    loose, _ = run(slope_fn, r=rule(margin=0.6, side="two_sided"))
    assert loose.accepted
    share, _ = run(slope_fn, r=rule(min_share=0.85))
    assert share.accepted and share.share == pytest.approx(9 / 10)


def test_holds_is_inclusive_at_the_tolerance():
    """The red team's m-7, survivor 5: a neighbour exactly at the tolerance holds."""
    r = rule(tolerance_se=2.0)
    assert PL.holds(2.0, r) and not PL.holds(2.0 + 1e-12, r)
    assert PL.zscore(0.5, 0.25, r) == pytest.approx(2.0) and PL.zscore(-0.5, 0.25, rule(side="two_sided")) == 2.0
    assert PL.zscore(0.3, 0.1, rule(margin=0.3)) == 0.0


def test_too_few_neighbours_in_all_or_for_one_lever_refuses():
    v, led = run(plateau_fn, design=CORNER, r=rule(min_neighbours=7))
    assert not v.accepted and "minimum 7" in v.reason
    assert len(v.outside) == 4 and v.evaluated == 6
    sp = TY.slot_space(routing=("longest_wait", "fewest_trades"))
    d = slot_design(sp, s1_0=(0, 0))                     # a one-mark window at its session's start
    v2, _ = run(lambda x: 0.0, design=d, r=slot_rule(sp), space=sp)
    assert not v2.accepted and "s1.0.first" in v2.reason and v2.per_lever["s1.0.first"] == 0
    assert any(x["levers"] == ["s1.0.first"] and x["class"] == "invalid" for x in v2.refused)


def slot_design(sp, s1_0=(10, 40)):
    d = {k: None for k in sp.names()}
    d.update({"routing": "longest_wait", "risk": 500.0, "s1.0.on": "on", "s1.0.T1": "a", "s1.0.T4": 5,
              "s1.0.first": s1_0[0], "s1.0.last": s1_0[1], "s1.1.on": "on", "s1.1.T1": "b", "s1.1.T4": None,
              "s1.1.first": 45, "s1.1.last": 60, "s2.0.on": "off"})
    assert sp.check(d) is None
    return d


def slot_rule(sp, **kw):
    steps = {}
    for dim in sp.dims:
        steps[dim.name] = PL.CELLS if dim.kind == SS.CAT else (50.0 if dim.name == "risk" else 5)
    base = dict(steps=steps, radius=1, tolerance_se=3.0, margin=0.0, side="worse", min_share=1.0, min_neighbours=3,
                min_per_lever=1)
    base.update(kw)
    return PL.PlateauRule(**base)


def test_every_active_lever_is_stepped_and_dependents_are_repaired():
    sp = TY.slot_space(routing=("longest_wait", "fewest_trades"))
    d = slot_design(sp)
    with pytest.raises(PL.PlateauRefused, match="unstepped"):
        run(lambda x: 0.0, design=d, r=PL.PlateauRule(steps={"risk": 50.0}, radius=1, tolerance_se=3.0, margin=0.0,
                                                      side="worse", min_share=1.0, min_neighbours=1,
                                                      min_per_lever=1), space=sp)
    v, led = run(lambda x: 0.0, design=d, r=slot_rule(sp), space=sp)
    moved = {n["moved"]: n for n in v.neighbours}
    assert "s1.0.T1 -> 'b'" in moved and "s1.1.T1 -> 'a'" in moved and "s2.0.on -> 'on'" in moved
    assert v.unsteppable == ["s1.1.T4"]                    # a latency-free source's one cell
    nb = {r["id"]: r["design"] for r in led.rows}
    b = nb[moved["s1.0.T1 -> 'b'"]["id"]]
    assert b["s1.0.T4"] is None                            # the latency repaired to the new source's one cell
    on = nb[moved["s2.0.on -> 'on'"]["id"]]
    assert sp.check(on) is None and on["s2.0.first"] is not None
    assert sorted(x["moved"] for x in v.refused) == ["s1.0.last +1 step", "s1.1.first -1 step"]   # collisions
    assert led.counts()["by_class"] == {"collision": 2} and v.accepted


def test_inactive_levers_are_never_stepped():
    """The red team's m-7, survivor 2: an off slot's levers move only through its on/off lever."""
    sp = TY.slot_space(routing=("longest_wait", "fewest_trades"))
    v, _ = run(lambda x: 0.0, design=slot_design(sp), r=slot_rule(sp), space=sp)
    for n in v.neighbours + v.refused:
        assert not any(lv.startswith("s2.0.") and lv != "s2.0.on" for lv in n["levers"]), n


def test_categorical_cells_and_a_drawn_box():
    v, _ = run(plateau_fn)
    assert {n["moved"] for n in v.neighbours if n["levers"] == ["c"]} == {"c -> 'a'", "c -> 'c'"}
    box = rule(neighbourhood="box", draws=12, radius=2)
    a, _ = run(plateau_fn, r=box, seed=5)
    b, _ = run(plateau_fn, r=box, seed=5)
    c, _ = run(plateau_fn, r=box, seed=6)
    assert [n["id"] for n in a.neighbours] == [n["id"] for n in b.neighbours] != [n["id"] for n in c.neighbours]
    assert a.evaluated + len(a.outside) + len(a.refused) == 12
    with pytest.raises(PL.PlateauRefused):
        run(plateau_fn, r=box)                            # a drawn box needs its seed


def test_the_rule_is_validated():
    for bad in (dict(side="either"), dict(radius=0), dict(tolerance_se=-1.0), dict(margin=-0.1), dict(min_share=0.0),
                dict(min_neighbours=0), dict(min_per_lever=0), dict(neighbourhood="ball"),
                dict(neighbourhood="box", draws=0)):
        with pytest.raises(PlateauRefused):
            rule(**bad)
    for steps in (dict(STEPS, n=0.5), dict(STEPS, c=1), dict(STEPS, x1=0.0)):
        with pytest.raises(PlateauRefused):
            run(plateau_fn, r=rule(steps=steps))


PlateauRefused = PL.PlateauRefused


# ------------------------------------------------------------------------------------------------ the protocol


def test_the_re_read_and_the_neighbours_are_read_on_the_fresh_seeds():
    seen = []

    def evaluate(design, *, protocol):
        seen.append(protocol)
        return TY.evaluator(plateau_fn, SD)(design, protocol=protocol)

    run(plateau_fn, evaluate=evaluate)
    assert seen and set(seen) == {TY.REREAD}

    def other_blocks(design, *, protocol):
        return TY.reading(design, 0.0, protocol=protocol, blocks=TY.OTHER_BLOCKS, per_seed=[0.0] * 64)

    with pytest.raises(SS.OffProtocol):
        run(plateau_fn, evaluate=other_blocks)

    def other_design(design, *, protocol):
        return TY.evaluator(plateau_fn, SD)(CENTRE, protocol=protocol)

    with pytest.raises((PL.PlateauRefused, SS.Uncounted)):
        run(plateau_fn, design=dict(CENTRE, x1=0.55), evaluate=other_design)

    def no_per_seed(design, *, protocol):
        return TY.reading(design, 0.0, protocol=protocol)

    with pytest.raises(PL.PlateauRefused, match="per-seed"):
        run(plateau_fn, evaluate=no_per_seed)


def test_the_re_read_protocol_is_fresh_and_the_declared_one():
    led = counted(CENTRE)
    f = TY.evaluator(plateau_fn, SD)(CENTRE, protocol=TY.PROTOCOL)
    for bad in (TY.PROTOCOL, TY.PROTOCOL.with_seeds((TY.SEEDS[0], 999)),
                SS.Protocol("composite", TY.OTHER_BLOCKS, TY.REREAD_SEEDS, 0)):
        with pytest.raises(PL.PlateauRefused):
            PL.check(f, TY.toy_space(), rule(), TY.evaluator(plateau_fn, SD), ledger=led, protocol=TY.PROTOCOL,
                     reread=bad, ledger_seed=LSEED)


def test_a_second_check_of_one_finalist_is_refused_under_any_rule():
    led = counted(CENTRE)
    f = TY.evaluator(plateau_fn, SD)(CENTRE, protocol=TY.PROTOCOL)
    kw = dict(ledger=led, protocol=TY.PROTOCOL, reread=TY.REREAD, ledger_seed=LSEED)
    assert PL.check(f, TY.toy_space(), rule(), TY.evaluator(plateau_fn, SD), **kw).accepted
    for r in (rule(), rule(tolerance_se=9.0)):
        with pytest.raises(SS.LedgerRefused):
            PL.check(f, TY.toy_space(), r, TY.evaluator(plateau_fn, SD), **kw)


def test_finalists_held_out_uncounted_off_protocol_or_predictions_are_refused():
    ev = TY.evaluator(plateau_fn, SD)
    kw = dict(protocol=TY.PROTOCOL, reread=TY.REREAD, ledger_seed=LSEED)
    for tag in ("held_out", "judged"):
        with pytest.raises(SS.HeldOutInput):
            PL.check(TY.reading(CENTRE, 0.0, tag=tag), TY.toy_space(), rule(), ev, ledger=counted(CENTRE), **kw)
    with pytest.raises(SS.Uncounted):                                     # the red team's B-1 (1)
        PL.check(ev(TY.SMOOTH_ARGMIN, protocol=TY.PROTOCOL), TY.toy_space(), rule(), ev, ledger=counted(CENTRE), **kw)
    with pytest.raises(SS.Uncounted):                                     # a plateau cell is never a finalist
        PL.check(ev(CENTRE, protocol=TY.PROTOCOL), TY.toy_space(), rule(), ev,
                 ledger=counted(CENTRE, role="plateau:x"), **kw)
    month = SS.Protocol("composite", (("2021-03-01", "2021-03-31"),), TY.SEEDS, 0)   # the red team's B-1 (2)
    with pytest.raises(SS.OffProtocol):
        PL.check(ev(CENTRE, protocol=month), TY.toy_space(), rule(), ev, ledger=counted(CENTRE), **kw)

    def held(design, *, protocol):
        return TY.reading(design, 0.0, protocol=protocol, tag="held_out", per_seed=[0.0] * len(protocol.seeds))

    with pytest.raises(SS.HeldOutInput):
        PL.check(ev(CENTRE, protocol=TY.PROTOCOL), TY.toy_space(), rule(), held, ledger=counted(CENTRE), **kw)
    with pytest.raises(SS.HeldOutInput):
        PL.check(SG.Surrogate(TY.toy_space(), seed=3, restarts=0), TY.toy_space(), rule(), ev,
                 ledger=counted(CENTRE), **kw)


# ------------------------------------------------------------------------------------------------ mutations


def test_mutation_tolerance_always_true_is_caught(monkeypatch):
    monkeypatch.setattr(PL, "holds", lambda z, r: True)
    v, _ = run(spike_fn)
    assert v.accepted                                     # the spike test would fail


def test_mutation_side_ignored_is_caught(monkeypatch):
    monkeypatch.setattr(PL, "zscore", lambda d, se, r: (abs(d) - r.margin) / se if se > 0 else 0.0)
    v, _ = run(slope_fn)
    assert v.held != 9                                    # the side test would fail


def test_mutation_echo_check_removed_is_caught(monkeypatch):
    monkeypatch.setattr(PL, "echoes", lambda got, design, protocol: True)

    def other_design(design, *, protocol):
        return TY.evaluator(plateau_fn, SD)(CENTRE, protocol=protocol)

    led = counted(CENTRE)
    led.begin("round-1", 1)
    led.record(TY.toy_space(), dict(CENTRE, x1=0.55), role="round-1", seed=1, refusal=None)
    f = TY.evaluator(plateau_fn, SD)(dict(CENTRE, x1=0.55), protocol=TY.PROTOCOL)
    v = PL.check(f, TY.toy_space(), rule(), other_design, ledger=led, protocol=TY.PROTOCOL, reread=TY.REREAD,
                 ledger_seed=LSEED)                         # the re-read of another design passes: the test would fail
    assert v.reread_value == TY.evaluator(plateau_fn, SD)(CENTRE, protocol=TY.REREAD).value


def test_mutation_inclusive_made_strict_is_caught(monkeypatch):
    monkeypatch.setattr(PL, "holds", lambda z, r: z < r.tolerance_se)
    assert not PL.holds(2.0, rule(tolerance_se=2.0))


def test_mutation_inactive_levers_stepped_is_caught(monkeypatch):
    monkeypatch.setattr(PL, "_stepped",
                        lambda space, rule, design: [d.name for d in space.dims if d.name in rule.steps])
    with pytest.raises((TypeError, AssertionError)):     # the named test fails: an inactive lever is stepped
        test_inactive_levers_are_never_stepped()
