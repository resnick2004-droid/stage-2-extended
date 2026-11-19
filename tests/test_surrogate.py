"""Wave 3.4: the surrogate (`extended/surrogate.py`), on synthetic objectives with known shape.

What is asserted: the likelihood's analytic gradient equals finite differences; the surrogate recovers a smooth known
function (error small against the function's spread, 95 % intervals covering) and **widens its uncertainty away from
its data**; on pure noise it calls the readings noise and shrinks its predictions; the fit is reproducible from its
seed; **the one door refuses** anything tagged held-out or touching the held-out years, another measure, a refused
design, and readings on other blocks or seeds, leaving the surrogate as it was. Thresholds were set before the first
run. **Mutations**: the gradient's factor, the predictive variance's reduction, the prior removed, the door.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import search_toys as TY  # noqa: E402

from extended import search_space as SS  # noqa: E402
from extended import surrogate as SG  # noqa: E402

SEED = 777


def designs(n: int, seed: int, space=None):
    return SS.Sampler(space or TY.toy_space(), seed=seed, method="sobol").survey(n, ledger=SS.CellLedger())


def fitted(train, fn, seed=SEED, restarts=2):
    sg = SG.Surrogate(TY.toy_space(), seed=seed, restarts=restarts)
    sg.fit([TY.reading(d, fn(d)) for d in train])
    return sg


def gradient_error(gp, which: str = "nll") -> float:
    f = getattr(gp, which)
    rng = np.random.default_rng(5)
    worst = 0.0
    for _ in range(3):
        th = rng.uniform([b[0] for b in gp.bounds()], [b[1] for b in gp.bounds()]) * 0.5
        _, g = f(th)
        for j in range(len(th)):
            e = np.zeros_like(th)
            e[j] = 1e-5
            fd = (f(th + e)[0] - f(th - e)[0]) / 2e-5
            worst = max(worst, abs(fd - g[j]) / max(1.0, abs(fd)))
    return worst


def a_gp():
    sp = TY.toy_space()
    ds = designs(24, 3)
    xc, xk = SG.Encoder(sp).encode(ds)
    y = np.array([TY.smooth(d) for d in ds])
    return SG._GP(xc, xk, y, np.full(len(y), 0.01))


def recovery(sg, test):
    pr = sg.predict(test)
    f = np.array([TY.smooth(d) for d in test])
    rmse = float(np.sqrt(np.mean((pr.mean - f) ** 2)))
    cover = float(np.mean(np.abs(pr.mean - f) <= 1.96 * pr.sd + 1e-9))
    return rmse / float(np.std(f)), cover


def widening(sg_factory):
    near_train = [d for d in designs(400, 11) if max(d["x1"], d["x2"], d["x3"]) < 0.45][:40]
    sg = sg_factory(near_train)
    pool = designs(1200, 12)
    near = [d for d in pool if max(d["x1"], d["x2"], d["x3"]) < 0.45]
    far = [d for d in pool if min(d["x1"], d["x2"], d["x3"]) > 0.75]
    return float(np.mean(sg.predict(far).sd)) / float(np.mean(sg.predict(near).sd)), len(near), len(far)


# ------------------------------------------------------------------------------------------------ the model


def test_the_likelihood_and_prior_gradients_are_exact():
    for which in ("nll", "neg_log_prior", "objective"):
        assert gradient_error(a_gp(), which) < 1e-4, which


def test_it_recovers_a_smooth_known_function():
    sg = fitted(designs(64, 1), TY.smooth)
    err, cover = recovery(sg, designs(300, 2))
    assert err < 0.10                                    # RMSE under a tenth of the function's spread
    assert cover >= 0.85                                 # 95 % intervals cover most of the truth
    assert sg.record.n == 64 and sg.record.seed == SEED and sg.record.starts == 3


def test_it_widens_its_uncertainty_away_from_data():
    ratio, n_near, n_far = widening(lambda tr: fitted(tr, TY.smooth))
    assert n_near >= 20 and n_far >= 10
    assert ratio > 3.0


def noise_reading(seed: int):
    train = designs(64, seed)
    y = np.array([TY.noise(d) for d in train])
    sg = fitted(train, TY.noise)
    spread = float(np.std(sg.predict(designs(200, seed + 1)).mean))
    insample = float(np.corrcoef(sg.predict(train).mean, y)[0, 1])
    return sg.noise_share(), spread / float(np.std(y)), insample


def test_it_calls_pure_noise_noise_and_does_not_chase_it():
    """On record (the failure protocol): the first build fitted the likelihood alone and failed this test -- at this
    seed the length-scales of x3 and n fell to about 0.09 and 0.08, the in-sample correlation with the noise was 0.98
    and the prediction spread 0.72 of the readings' (`test_mutation_prior_removed_is_caught` keeps that reading). The
    SAAS prior (`surrogate.PRIOR_TAU`) was adopted after a comparison over 30 seeds against a dimension-scaled
    log-normal prior and leave-one-out selection, both of which still interpolated noise at some seeds. The first
    `noise_share` counted a constant offset (every length-scale at its bound) as signal; it now reads the variance
    across the read designs. The thresholds 0.8 and 0.5 are the first run's."""
    share, spread, _ = noise_reading(21)
    assert share > 0.8
    assert spread < 0.5


def test_the_fit_is_reproducible_from_its_seed_and_needs_one():
    tr = designs(32, 31)
    a, b = fitted(tr, TY.smooth), fitted(tr, TY.smooth)
    assert a.record.hyper == b.record.hyper and a.record.nll == b.record.nll
    test = designs(20, 32)
    assert np.array_equal(a.predict(test).mean, b.predict(test).mean)
    with pytest.raises(SS.SpaceRefused):
        SG.Surrogate(TY.toy_space(), seed=None, restarts=1)


def test_a_reading_standard_error_widens_the_fit():
    tr = designs(32, 41)
    sp = TY.toy_space()
    tight = SG.Surrogate(sp, seed=SEED, restarts=1)
    tight.fit([TY.reading(d, TY.smooth(d), se=0.0) for d in tr])
    loose = SG.Surrogate(sp, seed=SEED, restarts=1)
    loose.fit([TY.reading(d, TY.smooth(d), se=0.5) for d in tr])
    assert float(np.mean(loose.predict(tr).sd)) > float(np.mean(tight.predict(tr).sd))


def test_believe_conditions_on_its_own_mean_only():
    sg = fitted(designs(32, 51), TY.smooth)
    x = designs(1, 52)
    b = sg.believe(x)
    assert b.predict(x).mean[0] == pytest.approx(sg.predict(x).mean[0], abs=1e-6)
    assert b.predict(x).sd[0] < sg.predict(x).sd[0]
    assert sg.record is b.record and sg._gp is not b._gp


def test_slot_designs_encode_and_fit():
    sp = TY.slot_space(routing=("longest_wait", "fewest_trades"))
    ds = designs(40, 61, space=sp)
    f = [d["risk"] / 900.0 + sum(d[f"{s.name}.on"] == SS.ON for s in sp.slots) for d in ds]
    sg = SG.Surrogate(sp, seed=SEED, restarts=1)
    sg.fit([TY.reading(d, v) for d, v in zip(ds, f)])
    xc, xk = sg.encoder.encode(ds)
    assert xc.shape[0] == xk.shape[0] == 40 and np.all((0 <= xc) & (xc <= 1))
    lat = sg.encoder.cat.index(sp.dim("s1.0.T4"))
    off = [i for i, d in enumerate(ds) if d["s1.0.on"] == SS.OFF]
    free = [i for i, d in enumerate(ds) if d["s1.0.on"] == SS.ON and d["s1.0.T4"] is None]
    assert off and free and set(xk[off, lat]) == {0} and 0 not in set(xk[free, lat])


# ------------------------------------------------------------------------------------------------ the door


def test_the_one_door_refuses_held_out_and_mixed_inputs():
    tr = designs(16, 71)
    good = [TY.reading(d, TY.smooth(d)) for d in tr]
    sg = SG.Surrogate(TY.toy_space(), seed=SEED, restarts=1)
    bad_sets = {
        "tagged": good[:-1] + [TY.reading(tr[-1], 0.0, tag="held_out")],
        "judged": good[:-1] + [TY.reading(tr[-1], 0.0, tag="judged")],
        "block 2024": good[:-1] + [TY.reading(tr[-1], 0.0, blocks=(("2023-01-03", "2024-03-01"),))],
        "prediction": good[:-1] + [sg],
    }
    for name, rs in bad_sets.items():
        with pytest.raises(SS.HeldOutInput):
            sg.fit(rs)
        assert not sg.fitted, name
    for rs in (good[:-1] + [TY.reading(tr[-1], 0.0, measure="ruin")],
               good[:-1] + [TY.reading(tr[-1], 0.0, blocks=TY.OTHER_BLOCKS)],
               good[:-1] + [TY.reading(tr[-1], 0.0, seeds=(1, 2, 3))],
               good[:-1] + [TY.reading(dict(tr[-1], n=99), 0.0)],
               good[:1]):
        with pytest.raises(SG.SurrogateRefused):
            sg.fit(rs)
        assert not sg.fitted
    rec = sg.fit(good)
    with pytest.raises(SS.HeldOutInput):
        sg.fit(good[:-1] + [TY.reading(tr[-1], 0.0, tag="heldout")])
    assert sg.record is rec                                              # a refused fit leaves the last one


# ------------------------------------------------------------------------------------------------ mutations


def test_mutation_gradient_factor_is_caught(monkeypatch):
    real = SG._GP.nll

    def half(self, theta):
        v, g = real(self, theta)
        g = g.copy()
        g[-2] *= 2.0                                     # the signal variance's term without its one half
        return v, g

    monkeypatch.setattr(SG._GP, "nll", half)
    assert gradient_error(a_gp()) > 1e-3


def test_mutation_variance_not_reduced_is_caught(monkeypatch):
    real = SG._GP.predict

    def prior_sd(self, xc, xk):
        mu, _ = real(self, xc, xk)
        _, _, s2, _ = self.unpack(self.theta)
        return mu, np.full(len(mu), np.sqrt(s2) * self.ysd)

    monkeypatch.setattr(SG._GP, "predict", prior_sd)
    ratio, _, _ = widening(lambda tr: fitted(tr, TY.smooth))
    assert not ratio > 3.0


def test_mutation_prior_removed_is_caught(monkeypatch):
    monkeypatch.setattr(SG._GP, "objective", SG._GP.nll)                  # the likelihood alone (the first build)
    share, spread, insample = noise_reading(21)
    assert not (share > 0.8 and spread < 0.5)
    assert insample > 0.9                                               # it interpolates the noise


def test_mutation_door_left_open_is_caught(monkeypatch):
    monkeypatch.setattr(SS, "admit", lambda readings: list(readings))
    tr = designs(16, 81)
    rs = [TY.reading(d, TY.smooth(d)) for d in tr[:-1]] + [TY.reading(tr[-1], 0.0, tag="held_out")]
    SG.Surrogate(TY.toy_space(), seed=SEED, restarts=1).fit(rs)          # the mutant admits it: the door test fails


def test_the_surrogate_and_the_proposer_name_no_finalist():
    """They propose; a finalist is only a design that was read (`plateau.check` takes a `Reading`, never a
    prediction): neither module offers anything that selects, ranks or names one."""
    from extended import proposer as P

    words = ("final", "select", "winner", "best", "rank", "choose")
    names = dir(SG) + dir(SG.Surrogate) + dir(P) + dir(P.Round)
    assert not [n for n in names if not n.startswith("__") and any(w in n.lower() for w in words)]
    with pytest.raises(SS.HeldOutInput):
        SS.admit_one(SG.Prediction(np.zeros(1), np.ones(1)))
