"""Wave 3.4: the round proposer (`extended/proposer.py`), on synthetic objectives with known optima.

What is asserted: on a smooth function with a known minimum the survey and the declared rounds find it within the
budget (16 surveyed and 6 rounds of 4: forty readings), better than the survey alone and better than forty
space-filling designs; under a limit it proposes inside the limit and finds the constrained optimum; **on pure noise
the search's best design is no plateau** (the plateau check refuses it) while the smooth optimum is one, under the same
rule; every round proposes exactly its batch, every proposal is a ledger cell with the round's seed, rounds are
reproducible, and held-out readings are refused. Thresholds were set before the first run. **Mutations**: the
acquisition's sign flipped, proposals left uncounted, the batch's budget broken.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import search_toys as TY  # noqa: E402

from extended import plateau as PL  # noqa: E402
from extended import proposer as P  # noqa: E402
from extended import search_space as SS  # noqa: E402

SURVEY_SEED, ROUND_SEED = 31337, 27182
SPEC = P.RoundSpec(batch=4, pool=512, acquisition="ei")
RULE = PL.PlateauRule(steps={"x1": 0.05, "x2": 0.05, "x3": 0.05, "n": 1}, radius=1, tolerance=0.25, side="worse",
                      min_share=1.0, min_neighbours=4)


def search(fn, spec=SPEC, rounds=6, **kw):
    led = SS.CellLedger()
    readings, rounds_ = TY.run_search(TY.toy_space(), fn, survey_n=16, rounds=rounds, spec=spec,
                                      survey_seed=SURVEY_SEED, round_seed=ROUND_SEED, ledger=led, **kw)
    return readings, rounds_, led


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


# ------------------------------------------------------------------------------------------------ noise and plateaus


def test_pure_noise_gives_no_plateau_and_the_smooth_optimum_is_one(smooth_run):
    noisy, _, led = search(TY.noise)
    v = PL.check(best(noisy), TY.toy_space(), RULE, TY.evaluator(TY.noise), ledger=led, ledger_seed=ROUND_SEED)
    assert not v.accepted and v.reason.startswith("refused: a spike")
    readings, _, led2 = smooth_run
    v2 = PL.check(best(readings), TY.toy_space(), RULE, TY.evaluator(TY.smooth), ledger=SS.CellLedger(),
                  ledger_seed=ROUND_SEED)
    assert v2.accepted, v2.reason


# ------------------------------------------------------------------------------------------------ budget and count


def test_every_round_proposes_its_batch_and_every_proposal_is_counted(smooth_run):
    readings, rounds, led = smooth_run
    c = led.counts()
    assert c["by_role"] == {"survey": 16, **{f"round-{i}": 4 for i in range(1, 7)}}
    for r in rounds:
        assert len(r.designs) == SPEC.batch and r.seed == ROUND_SEED
        rows = [x for x in led.rows if x["role"] == f"round-{r.index}"]
        assert [x["design"] for x in rows] == r.designs and {x["seed"] for x in rows} == {ROUND_SEED}
        assert {x["round"] for x in rows} == {r.index}
        assert r.fit.n == 16 + 4 * (r.index - 1) and r.fit.seed == ROUND_SEED
        assert r.candidates["valid"] >= SPEC.batch
    ids = [SS.design_id(d) for r in rounds for d in r.designs] + [SS.design_id(x.design) for x in readings[:16]]
    assert len(ids) == len(set(ids))                                     # nothing proposed twice or re-proposed


def test_a_round_is_reproducible_and_refuses_what_it_must(smooth_run):
    readings, rounds, _ = smooth_run
    base = readings[:16]
    a = P.propose(TY.toy_space(), base, spec=SPEC, round_index=1, seed=ROUND_SEED, ledger=SS.CellLedger())
    assert a.designs == rounds[0].designs and a.acquisition == rounds[0].acquisition
    b = P.propose(TY.toy_space(), base, spec=SPEC, round_index=1, seed=ROUND_SEED + 1, ledger=SS.CellLedger())
    assert b.designs != a.designs
    with pytest.raises(SS.HeldOutInput):
        P.propose(TY.toy_space(), base + [TY.reading(base[0].design, 0.0, tag="held_out")], spec=SPEC,
                  round_index=1, seed=ROUND_SEED, ledger=SS.CellLedger())
    with pytest.raises(P.ProposerRefused):
        P.propose(TY.toy_space(), base, spec=SPEC, round_index=0, seed=ROUND_SEED, ledger=SS.CellLedger())
    with pytest.raises(P.ProposerRefused):
        P.propose(TY.toy_space(), base, spec=P.RoundSpec(batch=40, pool=16, acquisition="ei", local=0),
                  round_index=1, seed=ROUND_SEED, ledger=SS.CellLedger())
    with pytest.raises(P.ProposerRefused):
        P.propose(TY.toy_space(), base, spec=SPEC, round_index=1, seed=ROUND_SEED, ledger=SS.CellLedger(),
                  limits=(P.Limit("reach", 0.4, "<="),))
    for bad in ({"batch": 4, "pool": 500, "acquisition": "ei"}, {"batch": 4, "pool": 512, "acquisition": "pi"},
                {"batch": 0, "pool": 512, "acquisition": "ei"}):
        with pytest.raises(P.ProposerRefused):
            P.RoundSpec(**bad)


def test_round_candidates_respect_the_space_and_slot_rounds_work():
    sp = TY.slot_space(routing=("longest_wait", "copy_trade_across_accounts"))
    led = SS.CellLedger()
    ds = SS.Sampler(sp, seed=SURVEY_SEED, method="sobol").survey(16, ledger=led)
    f = [d["risk"] / 900.0 + sum(d[f"{s.name}.on"] == SS.ON for s in sp.slots) for d in ds]
    r = P.propose(sp, [TY.reading(d, v) for d, v in zip(ds, f)], spec=SPEC, round_index=1, seed=ROUND_SEED,
                  ledger=led)
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
    real = SS.CellLedger.record

    def survey_only(self, space, design, *, role, seed, refusal, round_index=None):
        if role.startswith("round-"):
            return None
        return real(self, space, design, role=role, seed=seed, refusal=refusal, round_index=round_index)

    monkeypatch.setattr(SS.CellLedger, "record", survey_only)
    _, _, led = search(TY.smooth, rounds=2)
    assert led.counts()["by_role"] != {"survey": 16, "round-1": 4, "round-2": 4}


def test_mutation_budget_broken_is_caught(monkeypatch):
    real = P.propose

    def one_more(space, readings, *, spec, **kw):
        import dataclasses
        return real(space, readings, spec=dataclasses.replace(spec, batch=spec.batch + 1), **kw)

    monkeypatch.setattr(P, "propose", one_more)
    _, rounds, _ = search(TY.smooth, rounds=2)
    assert any(len(r.designs) != SPEC.batch for r in rounds)
