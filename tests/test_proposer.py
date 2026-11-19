"""Wave 3.4: the round proposer (`extended/proposer.py`), on synthetic objectives with known optima.

What is asserted: on a smooth function with a known minimum the survey and the declared rounds find it within the
budget (16 surveyed and 6 rounds of 4: forty readings), better than the survey alone and better than forty
space-filling designs; under a limit, read on the same protocol, it proposes inside the limit and finds the
constrained optimum; **on a rugged surface the search's best design is no plateau** (the plateau check, re-reading the
finalist on fresh seeds, refuses it) while the smooth optimum is one, under the same rule; every round proposes exactly
its batch, every proposal is a ledger cell with the round's seed, a round number is drawn once (a second round one,
under any seed, is refused, and so is a round out of order), a read design is never proposed again, the incumbent is
the lowest predicted mean, rounds are reproducible, and held-out or uncounted readings are refused. Every threshold here
was set before the first run and is unchanged. **Mutations**: the acquisition's sign flipped, proposals left uncounted,
the batch's budget broken.
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import search_toys as TY  # noqa: E402

from extended import plateau as PL  # noqa: E402
from extended import proposer as P  # noqa: E402
from extended import search_space as SS  # noqa: E402
from extended import surrogate as SG  # noqa: E402

SURVEY_SEED, ROUND_SEED, PLATEAU_SEED = 31337, 27182, 16180
SPEC = P.RoundSpec(batch=4, pool=512, acquisition="ei")
STEPS = {"x1": 0.05, "x2": 0.05, "x3": 0.05, "n": 1, "c": PL.CELLS}
RULE = PL.PlateauRule(steps=STEPS, radius=1, tolerance_se=PL.critical_z(0.05, 10), margin=0.35, side="worse",
                      min_share=1.0, min_neighbours=4, min_per_lever=1)
SEED_SD = 0.4                                          # the coin seeds' noise on every reading of the plateau test


def search(fn, spec=SPEC, rounds=6, **kw):
    led = SS.CellLedger()
    readings, rounds_ = TY.run_search(TY.toy_space(), fn, survey_n=16, rounds=rounds, spec=spec,
                                      survey_seed=SURVEY_SEED, round_seed=ROUND_SEED, ledger=led, **kw)
    return readings, rounds_, led


def survey_ledger(n=16, seed=SURVEY_SEED, space=None):
    led = SS.CellLedger()
    ds = SS.Sampler(space or TY.toy_space(), seed=seed, method="sobol").survey(n, ledger=led)
    return ds, led


@pytest.fixture(scope="module")
def smooth_run():
    return search(TY.smooth)


def best(readings):
    return min(readings, key=lambda r: r.value)


# ------------------------------------------------------------------------------------------------ the optimum


def test_it_finds_the_known_optimum_within_its_budget(smooth_run):
    readings, rounds, _ = smooth_run
    assert len(readings) == 16 + 6 * 4
    b = best(readings)
    assert b.value - TY.SMOOTH_MIN <= 0.02
    assert b.design["c"] == TY.SMOOTH_ARGMIN["c"] and b.design["n"] == TY.SMOOTH_ARGMIN["n"]
    assert b.value < best(readings[:16]).value
    sobol40 = SS.Sampler(TY.toy_space(), seed=SURVEY_SEED, method="sobol").survey(40, ledger=SS.CellLedger())
    assert b.value < min(TY.smooth(d) for d in sobol40)


def test_lcb_finds_it_too():
    readings, _, _ = search(TY.smooth, spec=P.RoundSpec(batch=4, pool=512, acquisition="lcb", kappa=2.0))
    assert best(readings).value - TY.SMOOTH_MIN <= 0.05


def test_under_a_limit_it_proposes_inside_the_limit():
    """The limit x1 <= 0.4 excludes the free optimum (x1 = 0.62); the constrained one is at x1 = 0.4, value
    3 (0.22)^2."""
    lim = P.Limit("reach", 0.4, "<=")
    readings, rounds, _ = search(TY.smooth, limits=(lim,), limit_fns={"reach": lambda d: d["x1"]})
    late = [d for r in rounds[-3:] for d in r.designs]
    assert sum(d["x1"] <= 0.4 for d in late) >= 0.75 * len(late)
    feasible = [r for r in readings if r.design["x1"] <= 0.4]
    assert best(feasible).value <= 3 * 0.22 ** 2 + 0.05
    assert all(0.0 <= p <= 1.0 for r in rounds for p in r.p_feasible)
    assert set(rounds[0].limit_fits) == {"reach"}
    assert rounds[0].limit_fits["reach"].blocks == TY.PROTOCOL.blocks          # one protocol across the measures


def test_a_limit_read_on_another_protocol_is_refused(smooth_run):
    readings, _, _ = smooth_run
    ds, led = survey_ledger()
    rs = [TY.reading(d, TY.smooth(d)) for d in ds]
    off = [TY.reading(d, d["x1"], measure="reach", seeds=(7, 8, 9)) for d in ds]
    with pytest.raises(SS.OffProtocol):
        P.propose(TY.toy_space(), rs, spec=SPEC, round_index=1, seed=ROUND_SEED, ledger=led, protocol=TY.PROTOCOL,
                  limits=(P.Limit("reach", 0.4, "<="),), limit_readings={"reach": off})


# ------------------------------------------------------------------------------------------------ noise and plateaus


def test_a_rugged_surface_gives_no_plateau_and_the_smooth_optimum_is_one(smooth_run):
    noisy, _, led = search(TY.noise, sd=SEED_SD)
    v = PL.check(best(noisy), TY.toy_space(), RULE, TY.evaluator(TY.noise, SEED_SD), ledger=led,
                 protocol=TY.PROTOCOL, reread=TY.REREAD, ledger_seed=PLATEAU_SEED)
    assert not v.accepted and v.reason.startswith("refused: a spike"), v.reason
    readings, _, led2 = smooth_run
    v2 = PL.check(best(readings), TY.toy_space(), RULE, TY.evaluator(TY.smooth, SEED_SD), ledger=copy.deepcopy(led2),
                  protocol=TY.PROTOCOL, reread=TY.REREAD, ledger_seed=PLATEAU_SEED)
    assert v2.accepted, v2.reason
    assert v2.form == PL.FORM and v2.reread_seeds == TY.REREAD_SEEDS and v2.rule == RULE.sha256()


# ------------------------------------------------------------------------------------------------ budget and count


def test_every_round_proposes_its_batch_and_every_proposal_is_counted(smooth_run):
    readings, rounds, led = smooth_run
    c = led.counts()
    assert c["by_role"] == {"survey": 16, **{f"round-{i}": 4 for i in range(1, 7)}}
    for r in rounds:
        assert len(r.designs) == SPEC.batch and r.seed == ROUND_SEED and r.libs == SS.LIBS
        rows = [x for x in led.rows if x["role"] == f"round-{r.index}"]
        assert [x["design"] for x in rows] == r.designs and {x["seed"] for x in rows} == {ROUND_SEED}
        assert {x["round"] for x in rows} == {r.index} and all(x["libs"] == dict(SS.LIBS) for x in rows)
        assert r.fit.n == 16 + 4 * (r.index - 1) and r.fit.seed == ROUND_SEED
        assert r.candidates["valid"] >= SPEC.batch
    ids = [SS.design_id(d) for r in rounds for d in r.designs] + [SS.design_id(x.design) for x in readings[:16]]
    assert len(ids) == len(set(ids))                                     # nothing proposed twice or re-proposed


def test_a_round_is_drawn_once_and_in_order():
    """The red team's B-1 (3): a second round one under another seed would let the reader choose between them."""
    ds, led = survey_ledger()
    rs = [TY.reading(d, TY.smooth(d)) for d in ds]
    with pytest.raises(SS.LedgerRefused):
        P.propose(TY.toy_space(), rs, spec=SPEC, round_index=2, seed=ROUND_SEED, ledger=led, protocol=TY.PROTOCOL)
    P.propose(TY.toy_space(), rs, spec=SPEC, round_index=1, seed=11, ledger=led, protocol=TY.PROTOCOL)
    for seed in (12, 11):
        with pytest.raises(SS.LedgerRefused):
            P.propose(TY.toy_space(), rs, spec=SPEC, round_index=1, seed=seed, ledger=led, protocol=TY.PROTOCOL)
    assert led.counts()["by_role"] == {"survey": 16, "round-1": 4}
    with pytest.raises(SS.LedgerRefused):
        led.record(TY.toy_space(), ds[0], role="round-1", seed=12, refusal=None, round_index=1)


def test_a_read_design_is_never_proposed_again():
    """A space of twelve cells, eight of them read: the pool holds every read cell many times over, and none of them
    is proposed (the red team's m-7, survivor 1)."""
    sp = SS.Space((SS.Dim("n", SS.INT, lo=1, hi=4, step=1), SS.Dim("c", SS.CAT, values=("a", "b", "c"))))
    led = SS.CellLedger()
    ds = SS.Sampler(sp, seed=SURVEY_SEED, method="sobol").survey(8, ledger=led)
    rs = [TY.reading(d, float(d["n"]) + {"a": 0.0, "b": 0.5, "c": 1.0}[d["c"]]) for d in ds]
    r = P.propose(sp, rs, spec=P.RoundSpec(batch=2, pool=64, acquisition="ei"), round_index=1, seed=ROUND_SEED,
                  ledger=led, protocol=TY.PROTOCOL)
    read = {SS.design_id(d) for d in ds}
    assert r.candidates["repeats"] > 0 and not read & {SS.design_id(d) for d in r.designs}


def test_the_incumbent_is_the_lowest_predicted_mean(smooth_run):
    """The red team's m-7, survivor 3: the expected improvement's incumbent is the lowest predicted mean over the read
    designs, not the highest."""
    readings, rounds, led = smooth_run
    base = readings[:16]
    sg = SG.Surrogate(TY.toy_space(), seed=ROUND_SEED, restarts=SPEC.restarts, key=(1, 0))
    sg.fit(base, ledger=led, protocol=TY.PROTOCOL)
    mu = sg.predict([r.design for r in base]).mean
    assert rounds[0].incumbent == pytest.approx(float(np.min(mu))) and rounds[0].incumbent < float(np.max(mu))


def test_a_round_is_reproducible_and_refuses_what_it_must(smooth_run):
    readings, rounds, _ = smooth_run
    base = readings[:16]
    _, led_a = survey_ledger()
    a = P.propose(TY.toy_space(), base, spec=SPEC, round_index=1, seed=ROUND_SEED, ledger=led_a,
                  protocol=TY.PROTOCOL)
    assert a.designs == rounds[0].designs and a.acquisition == rounds[0].acquisition
    _, led_b = survey_ledger()
    b = P.propose(TY.toy_space(), base, spec=SPEC, round_index=1, seed=ROUND_SEED + 1, ledger=led_b,
                  protocol=TY.PROTOCOL)
    assert b.designs != a.designs
    for bad, cls in (([TY.reading(base[0].design, 0.0, tag="held_out")], SS.HeldOutInput),
                     ([TY.reading(TY.SMOOTH_ARGMIN, 0.0)], SS.Uncounted)):
        _, led = survey_ledger()
        with pytest.raises(cls):
            P.propose(TY.toy_space(), base + bad, spec=SPEC, round_index=1, seed=ROUND_SEED, ledger=led,
                      protocol=TY.PROTOCOL)
    _, led = survey_ledger()
    with pytest.raises(P.ProposerRefused):
        P.propose(TY.toy_space(), base, spec=SPEC, round_index=0, seed=ROUND_SEED, ledger=led, protocol=TY.PROTOCOL)
    with pytest.raises(P.ProposerRefused):
        P.propose(TY.toy_space(), base, spec=P.RoundSpec(batch=40, pool=16, acquisition="ei", local=0),
                  round_index=1, seed=ROUND_SEED, ledger=led, protocol=TY.PROTOCOL)
    with pytest.raises(SS.LedgerRefused):                                # that refused round one was still drawn
        P.propose(TY.toy_space(), base, spec=SPEC, round_index=1, seed=ROUND_SEED, ledger=led, protocol=TY.PROTOCOL)
    _, led = survey_ledger()
    with pytest.raises(P.ProposerRefused):
        P.propose(TY.toy_space(), base, spec=SPEC, round_index=1, seed=ROUND_SEED, ledger=led, protocol=TY.PROTOCOL,
                  limits=(P.Limit("reach", 0.4, "<="),))
    for bad in ({"batch": 4, "pool": 500, "acquisition": "ei"}, {"batch": 4, "pool": 512, "acquisition": "pi"},
                {"batch": 0, "pool": 512, "acquisition": "ei"}):
        with pytest.raises(P.ProposerRefused):
            P.RoundSpec(**bad)


def test_round_candidates_respect_the_space_and_slot_rounds_work():
    sp = TY.slot_space(routing=("longest_wait", "copy_trade_across_accounts"))
    ds, led = survey_ledger(space=sp)
    f = [d["risk"] / 900.0 + sum(d[f"{s.name}.on"] == SS.ON for s in sp.slots) for d in ds]
    r = P.propose(sp, [TY.reading(d, v) for d, v in zip(ds, f)], spec=SPEC, round_index=1, seed=ROUND_SEED,
                  ledger=led, protocol=TY.PROTOCOL)
    assert all(sp.check(d) is None for d in r.designs)
    assert all(d["routing"] != "copy_trade_across_accounts" for d in r.designs)
    assert r.candidates["pool_refused"] > 0


# ------------------------------------------------------------------------------------------------ mutations


def test_mutation_acquisition_sign_flipped_is_caught(monkeypatch):
    real = P.expected_improvement
    monkeypatch.setattr(P, "expected_improvement", lambda mu, sd, b, xi: -real(mu, sd, b, xi) - mu)
    readings, _, _ = search(TY.smooth)
    assert not best(readings).value - TY.SMOOTH_MIN <= 0.02


def test_mutation_proposals_uncounted_is_caught(monkeypatch):
    """Round proposals left out of the ledger: the next round's door refuses their readings as uncounted."""
    real = SS.CellLedger.record

    def survey_only(self, space, design, *, role, seed, refusal, round_index=None):
        if role.startswith("round-"):
            return None
        return real(self, space, design, role=role, seed=seed, refusal=refusal, round_index=round_index)

    monkeypatch.setattr(SS.CellLedger, "record", survey_only)
    with pytest.raises(SS.Uncounted):
        search(TY.smooth, rounds=2)


def test_mutation_budget_broken_is_caught(monkeypatch):
    real = P.propose

    def one_more(space, readings, *, spec, **kw):
        import dataclasses
        return real(space, readings, spec=dataclasses.replace(spec, batch=spec.batch + 1), **kw)

    monkeypatch.setattr(P, "propose", one_more)
    _, rounds, _ = search(TY.smooth, rounds=2)
    assert any(len(r.designs) != SPEC.batch for r in rounds)
