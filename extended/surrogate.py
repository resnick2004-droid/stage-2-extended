"""Wave 3.4 (the restart plan 4.3 c; CHARTER 3.3 (c)): the surrogate -- a Gaussian process predicting one measure's
search-year reading (the composite, or any measure of `docs/MEASURES.md`) from a design's levers, with its own
uncertainty. It proposes nothing and selects nothing: `extended.proposer` asks it for predictions, and a finalist is
only ever a design that was read (`extended.plateau` refuses anything but a `Reading`).

    from extended import search_space as SS, surrogate as SG
    sg = SG.Surrogate(space, seed=S2, restarts=4)
    record = sg.fit(readings, ledger=ledger)        # the one door (SS.admit): the ledger's protocol, counted cells
    pred = sg.predict(designs)                      # pred.mean, pred.sd (the latent measure's), in its own units

**The one door.** `Surrogate.fit` is the only way data reaches the model. It passes every reading through
`search_space.admit` with the cell ledger, whose survey declared the protocol (the red team's B-1 and RB-2): tagged
``search``, every block and every outcome session inside the search years 2020-01-02 to 2023-12-29 (E-208, CHARTER 3.6
(d)), exactly the ledger's protocol under the surrogate's measure (the protocol's own or a declared limit's), and **a
design that is a counted survey or round cell of the ledger**. No caller hands it a protocol. It refuses a design the
space refuses. A refused fit leaves the surrogate as it was. The model's arrays are private (`_GP`); `believe` adds the
surrogate's **own** predicted means at designs it is asked about (the kriging-believer batch, `extended.proposer`),
never an outside value.

**The model.** Each design is encoded by the space: a real or integer lever scaled to [0, 1] by its bounds (a window's
marks by its slot's), a categorical as its cell's code (an inactive lever holds a code of its own, and 0 on the
continuous scale, the slot's on/off lever carrying the difference). The kernel is
    k(x, x') = s2 * matern52(r) * exp(-sum_c lam_c [x_c != x'_c]),   r^2 = sum_j ((x_j - x'_j) / ell_j)^2,
a product of a Matern 5/2 kernel with one length-scale a continuous lever and a categorical-overlap kernel with one
rate a categorical lever (both positive definite: exp(-lam [a != b]) = e^-lam + (1 - e^-lam) [a == b]). The noise is
a fitted nugget plus each reading's own squared standard error when it gives one. The readings are standardised
(mean 0, standard deviation 1) before the fit and the predictions returned in their units; the constant mean is
integrated out under a unit prior variance (`MEAN_VAR`, a constant kernel term), so a model that finds no structure
still says how well it knows the level.

**The fit** is a **fixed procedure**, to be named as such in the search declaration with `PRIOR_TAU`, `MEAN_VAR`,
`BOUNDS`, `START` and the restarts pinned (the red team's n-4: it is neither of the template's two options, "fixed
here" or "chosen by cross-validation", but the first with a declared prior): the hyperparameters maximise the log
posterior on the admitted search-year readings -- the log marginal likelihood plus
**the SAAS prior** (`PRIOR_TAU`; a half-Cauchy on each inverse squared length-scale and each categorical rate, MAP in
the rates), because the likelihood alone, with one length-scale a lever, reads pure noise as structure (a short
length-scale on a few levers interpolates it; `tests/test_surrogate.py` holds the diagnosis) -- with analytic
gradients (`_GP.nll`, `_GP.neg_log_prior`, checked against finite differences by the tests), by L-BFGS-B inside
declared bounds (`BOUNDS`, in the standardised units), from a fixed start and `restarts` starts drawn from `seed`'s fit
stream; the lowest wins. The seed, the starts, the winning hyperparameters and the numpy and scipy versions are in
the fit's record. No held-out reading can enter, so nothing fitted here can read the held-out years.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np
from scipy.linalg import cho_solve, cholesky, solve_triangular
from scipy.optimize import minimize

from extended import search_space as SS

TASK = "Wave 3.4"
#: the hyperparameters' bounds, in the standardised units (log scale): length-scales on the [0, 1] scale, categorical
#: rates, the signal variance and the nugget. Declared defaults; a search declaration may pin others.
BOUNDS: Mapping[str, tuple[float, float]] = {"ell": (0.02, 20.0), "lam": (1e-3, 20.0), "s2": (1e-3, 20.0),
                                             "noise": (1e-6, 10.0)}
#: the fixed first start (every other start is drawn from the fit stream)
START: Mapping[str, float] = {"ell": 0.5, "lam": 0.5, "s2": 1.0, "noise": 0.1}
#: the SAAS prior's scale (Eriksson and Jankowiak 2021, the sparse axis-aligned subspace prior, its global scale's
#: prior scale): a half-Cauchy of this scale on every inverse squared length-scale and on every categorical rate, so a
#: lever is irrelevant unless the readings demand otherwise. Declared default; a search declaration may pin another.
PRIOR_TAU = 0.1
#: the constant mean's prior variance in the standardised units: the mean is integrated out (a constant kernel term,
#: not fitted), so its uncertainty reaches every prediction instead of the sample mean being taken as known
MEAN_VAR = 1.0
_SQ5 = math.sqrt(5.0)
_JITTER = (0.0, 1e-10, 1e-8, 1e-6)


class SurrogateRefused(ValueError):
    """A fit or a prediction this module cannot stand behind."""


@dataclass(frozen=True)
class Prediction:
    mean: np.ndarray
    sd: np.ndarray


@dataclass(frozen=True)
class FitRecord:
    measure: str
    n: int
    seed: int
    restarts: int
    starts: int
    nll: float
    hyper: Mapping[str, Any]
    readings: tuple[str, ...]
    blocks: tuple[tuple[str, str], ...]
    seeds: tuple[int, ...]
    horizon: int
    libs: tuple[tuple[str, str], ...]


# ------------------------------------------------------------------------------------------------ the encoding


class Encoder:
    """A design as (continuous coordinates in [0, 1], categorical codes), from its space."""

    def __init__(self, space: SS.Space):
        self.space = space
        self.cont = [d for d in space.dims if d.kind != SS.CAT]
        self.cat = [d for d in space.dims if d.kind == SS.CAT]
        # code 0 is an inactive lever's own; a value None (a latency-free source's one cell) takes a code of its own
        self.codes = [{v: i + 1 for i, v in enumerate(d.every_value())} for d in self.cat]

    def encode(self, designs: Sequence[Mapping[str, Any]]) -> tuple[np.ndarray, np.ndarray]:
        xc = np.zeros((len(designs), len(self.cont)))
        xk = np.zeros((len(designs), len(self.cat)), dtype=np.int64)
        for i, des in enumerate(designs):
            for j, d in enumerate(self.cont):
                v = des[d.name]
                if v is not None:
                    xc[i, j] = 0.0 if d.hi == d.lo else (float(v) - float(d.lo)) / (float(d.hi) - float(d.lo))
            for j, d in enumerate(self.cat):
                v = des[d.name]
                if not self.space.active(d, des):
                    continue                                             # code 0
                if v not in self.codes[j]:
                    raise SurrogateRefused(f"{d.name} = {v!r} is not a value of the space")
                xk[i, j] = self.codes[j][v]
        return xc, xk


# ------------------------------------------------------------------------------------------------ the process


def _sqdiff(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """[dims, n, m] squared differences of the continuous coordinates."""
    return (a.T[:, :, None] - b.T[:, None, :]) ** 2


def _mismatch(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """[dims, n, m] 1 where two categorical codes differ."""
    return (a.T[:, :, None] != b.T[:, None, :]).astype(float)


class _GP:
    """The process on encoded arrays (private: data reaches it only through `Surrogate.fit`)."""

    def __init__(self, xc: np.ndarray, xk: np.ndarray, y: np.ndarray, se2: np.ndarray):
        self.xc, self.xk = xc, xk
        self.n, self.dc, self.dk = len(y), xc.shape[1], xk.shape[1]
        self.ymu = float(np.mean(y))
        sd = float(np.std(y))
        self.ysd = sd if sd > 0 else 1.0
        self.y = (y - self.ymu) / self.ysd
        self.se2 = se2 / self.ysd ** 2
        self.D2 = _sqdiff(xc, xc)
        self.M = _mismatch(xk, xk)
        self.theta: np.ndarray | None = None

    # -- the parameter vector: [log ell (dc), log lam (dk), log s2, log noise]
    def bounds(self) -> list[tuple[float, float]]:
        b = ([BOUNDS["ell"]] * self.dc + [BOUNDS["lam"]] * self.dk + [BOUNDS["s2"], BOUNDS["noise"]])
        return [(math.log(lo), math.log(hi)) for lo, hi in b]

    def start(self) -> np.ndarray:
        return np.log(np.array([START["ell"]] * self.dc + [START["lam"]] * self.dk + [START["s2"], START["noise"]]))

    def unpack(self, theta: np.ndarray) -> tuple[np.ndarray, np.ndarray, float, float]:
        t = np.exp(theta)
        return t[:self.dc], t[self.dc:self.dc + self.dk], float(t[-2]), float(t[-1])

    def _kernel_parts(self, theta: np.ndarray, D2: np.ndarray, M: np.ndarray):
        ell, lam, s2, _ = self.unpack(theta)
        r2 = np.tensordot(1.0 / ell ** 2, D2, axes=1) if self.dc else np.zeros(D2.shape[1:])
        r = np.sqrt(np.maximum(r2, 0.0))
        e = np.exp(-_SQ5 * r)
        m52 = (1.0 + _SQ5 * r + 5.0 / 3.0 * r2) * e
        cat = np.exp(-np.tensordot(lam, M, axes=1)) if self.dk else np.ones(D2.shape[1:])
        return s2, r, e, m52, cat

    def nll(self, theta: np.ndarray) -> tuple[float, np.ndarray]:
        """The negative log marginal likelihood and its gradient in theta."""
        ell, lam, s2, noise = self.unpack(theta)
        s2, r, e, m52, cat = self._kernel_parts(theta, self.D2, self.M)
        Kf = s2 * m52 * cat
        K = Kf + MEAN_VAR + np.diag(noise + self.se2)
        L = None
        for j in _JITTER:
            try:
                L = cholesky(K + j * np.eye(self.n), lower=True)
                break
            except np.linalg.LinAlgError:
                continue
        if L is None:
            return 1e25, np.zeros_like(theta)
        alpha = cho_solve((L, True), self.y)
        nll = 0.5 * float(self.y @ alpha) + float(np.sum(np.log(np.diag(L)))) + 0.5 * self.n * math.log(2 * math.pi)
        W = cho_solve((L, True), np.eye(self.n)) - np.outer(alpha, alpha)
        g = np.zeros_like(theta)
        base = s2 * (5.0 / 3.0) * (1.0 + _SQ5 * r) * e * cat
        for j in range(self.dc):
            g[j] = 0.5 * float(np.sum(W * (base * self.D2[j] / ell[j] ** 2)))
        for c in range(self.dk):
            g[self.dc + c] = 0.5 * float(np.sum(W * (-lam[c] * self.M[c] * Kf)))
        g[-2] = 0.5 * float(np.sum(W * Kf))
        g[-1] = 0.5 * noise * float(np.trace(W))
        return nll, g

    def neg_log_prior(self, theta: np.ndarray) -> tuple[float, np.ndarray]:
        """The SAAS prior (`PRIOR_TAU`), MAP in the rates: log(1 + (rho / tau)^2) summed over rho = 1 / ell^2 and
        over the categorical rates lam, with its gradient in theta (log ell, log lam)."""
        g = np.zeros_like(theta)
        t = theta[:self.dc]
        u = (np.exp(-2.0 * t) / PRIOR_TAU) ** 2
        c = theta[self.dc:self.dc + self.dk]
        w = (np.exp(c) / PRIOR_TAU) ** 2
        g[:self.dc] = -4.0 * u / (1.0 + u)
        g[self.dc:self.dc + self.dk] = 2.0 * w / (1.0 + w)
        return float(np.sum(np.log1p(u)) + np.sum(np.log1p(w))), g

    def objective(self, theta: np.ndarray) -> tuple[float, np.ndarray]:
        """The negative log posterior (likelihood and prior) and its gradient: what the fit minimises."""
        v, g = self.nll(theta)
        if v >= 1e24:
            return v, g
        pv, pg = self.neg_log_prior(theta)
        return v + pv, g + pg

    def fit(self, rng: np.random.Generator, restarts: int) -> tuple[float, int]:
        bnds = self.bounds()
        lo = np.array([b[0] for b in bnds])
        hi = np.array([b[1] for b in bnds])
        starts = [self.start()] + [rng.uniform(lo, hi) for _ in range(int(restarts))]
        best = (math.inf, None)
        for s in starts:
            res = minimize(self.objective, s, jac=True, method="L-BFGS-B", bounds=bnds)
            val = float(res.fun)
            if math.isfinite(val) and val < best[0]:
                best = (val, np.array(res.x))
        if best[1] is None:
            raise SurrogateRefused("no start reached a finite likelihood")
        self.set(best[1])
        return best[0], len(starts)

    def set(self, theta: np.ndarray) -> None:
        self.theta = np.array(theta, dtype=float)
        _, _, _, noise = self.unpack(self.theta)
        s2, _, _, m52, cat = self._kernel_parts(self.theta, self.D2, self.M)
        K = s2 * m52 * cat + MEAN_VAR + np.diag(noise + self.se2)
        for j in _JITTER:
            try:
                self.L = cholesky(K + j * np.eye(self.n), lower=True)
                break
            except np.linalg.LinAlgError:
                continue
        else:
            raise SurrogateRefused("the fitted kernel is not positive definite")
        self.alpha = cho_solve((self.L, True), self.y)

    def predict(self, xc: np.ndarray, xk: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """The latent measure's mean and standard deviation, in the readings' units."""
        assert self.theta is not None
        s2, _, _, m52, cat = self._kernel_parts(self.theta, _sqdiff(self.xc, xc), _mismatch(self.xk, xk))
        ks = s2 * m52 * cat + MEAN_VAR                                   # [n, m]
        mu = ks.T @ self.alpha
        v = solve_triangular(self.L, ks, lower=True)
        var = np.maximum(s2 + MEAN_VAR - np.sum(v * v, axis=0), 1e-12)
        return mu * self.ysd + self.ymu, np.sqrt(var) * self.ysd

    def with_points(self, xc: np.ndarray, xk: np.ndarray, y: np.ndarray) -> "_GP":
        """The same hyperparameters, conditioned on more points (values in the readings' units)."""
        g = _GP.__new__(_GP)
        g.xc, g.xk = np.vstack([self.xc, xc]), np.vstack([self.xk, xk])
        g.n, g.dc, g.dk = len(g.xc), self.dc, self.dk
        g.ymu, g.ysd = self.ymu, self.ysd
        g.y = np.concatenate([self.y, (y - self.ymu) / self.ysd])
        g.se2 = np.concatenate([self.se2, np.zeros(len(y))])
        g.D2, g.M = _sqdiff(g.xc, g.xc), _mismatch(g.xk, g.xk)
        g.set(self.theta)
        return g


# ------------------------------------------------------------------------------------------------ the surrogate


class Surrogate:
    """One measure's surrogate over a space (the module docstring). `seed` explicit; `restarts` the drawn starts;
    `key` the fit stream's spawn key under the seed (a round's index, a limit's), so one role seed serves every
    round."""

    def __init__(self, space: SS.Space, *, seed: int, restarts: int, measure: str = "composite",
                 key: Sequence[int] = ()):
        SS.child_rng(seed)
        if int(restarts) < 0:
            raise SurrogateRefused("restarts is a count")
        self.space, self.seed, self.restarts, self.measure = space, int(seed), int(restarts), measure
        self.key = tuple(int(k) for k in key)
        self.encoder = Encoder(space)
        self._gp: _GP | None = None
        self.record: FitRecord | None = None

    def fit(self, readings: Sequence[Any], *, ledger: SS.CellLedger) -> FitRecord:
        """The one door (the module docstring): admit (the ledger's protocol), check, encode, fit."""
        rs = SS.admit(readings, ledger=ledger, measure=self.measure, roles=SS.searched)
        protocol = ledger.protocol_for(self.measure)
        if len(rs) < 2:
            raise SurrogateRefused("a fit needs at least two readings")
        for r in rs:
            why = self.space.check(r.design)
            if why is not None:
                raise SurrogateRefused(f"a reading of a design the space refuses ({why[0]}: {why[1]})")
        blocks, seeds = protocol.blocks, protocol.seeds
        xc, xk = self.encoder.encode([r.design for r in rs])
        y = np.array([float(r.value) for r in rs])
        se2 = np.array([0.0 if r.se is None else float(r.se) ** 2 for r in rs])
        gp = _GP(xc, xk, y, se2)
        nll, starts = gp.fit(SS.child_rng(self.seed, SS.STREAM_FIT, *self.key), self.restarts)
        ell, lam, s2, noise = gp.unpack(gp.theta)
        hyper = {"ell": {d.name: float(v) for d, v in zip(self.encoder.cont, ell)},
                 "lam": {d.name: float(v) for d, v in zip(self.encoder.cat, lam)},
                 "s2": s2, "noise": noise, "y_mean": gp.ymu, "y_sd": gp.ysd}
        self._gp = gp
        self.record = FitRecord(self.measure, len(rs), self.seed, self.restarts, starts, float(nll), hyper,
                                tuple(r.id for r in rs), blocks, seeds, protocol.horizon, SS.LIBS)
        return self.record

    @property
    def fitted(self) -> bool:
        return self._gp is not None

    def _need(self) -> _GP:
        if self._gp is None:
            raise SurrogateRefused("the surrogate is not fitted")
        return self._gp

    def predict(self, designs: Sequence[Mapping[str, Any]]) -> Prediction:
        gp = self._need()
        xc, xk = self.encoder.encode(list(designs))
        mu, sd = gp.predict(xc, xk)
        return Prediction(mu, sd)

    def believe(self, designs: Sequence[Mapping[str, Any]]) -> "Surrogate":
        """A copy conditioned on its own predicted means at `designs` (the kriging believer), same hyperparameters."""
        gp = self._need()
        xc, xk = self.encoder.encode(list(designs))
        mu, _ = gp.predict(xc, xk)
        out = Surrogate.__new__(Surrogate)
        out.__dict__.update(self.__dict__)
        out._gp = gp.with_points(xc, xk, mu)
        return out

    def noise_share(self) -> float:
        """The fitted nugget's share of the variance **across the read designs**: noise / (noise + s2 (1 - the mean
        correlation between two read designs)). A length-scale at its bound makes the kernel a constant there, whose
        variance is an uncertain offset, not a difference between designs, so it is not counted as signal. Near one,
        the model reads the differences between designs as noise."""
        gp = self._need()
        _, _, s2, noise = gp.unpack(gp.theta)
        _, _, _, m52, cat = gp._kernel_parts(gp.theta, gp.D2, gp.M)
        corr = m52 * cat
        n = corr.shape[0]
        mean_off = float((np.sum(corr) - np.trace(corr)) / (n * (n - 1))) if n > 1 else 1.0
        return noise / (noise + s2 * max(0.0, 1.0 - mean_off))


__all__ = ["TASK", "BOUNDS", "START", "PRIOR_TAU", "MEAN_VAR", "SurrogateRefused", "Prediction", "FitRecord",
           "Encoder", "Surrogate"]
