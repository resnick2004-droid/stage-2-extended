"""Wave 3.2: S1, the synthetic schedule-level histories of the three-way test's size and power checks
(`docs/plans/THREE_WAY_TEST_design.md` 2.6, 2.7), and the stylised designs that read them. No bar exists here: a
history is a volatility per session and **two trigger streams, A and B, independent and identically distributed given
the day's common factor** (the volatility; the news flag is not modelled here), so swapping them (`swap`) is a symmetry
of the generator -- the history null's construction on S1 (2.7, symmetry 1).

**The generator** (its parameters stylised in H3-A, fitted on the search years only in H3-D): log volatility an AR(1)
around its mean with an optional slow two-state regime (`family_stats.slow_sign`); each stream's arrivals a Poisson
count whose rate follows the volatility, at uniform decision slots in a declared window; each arrival's holding time
exponential, lengthening with the bracket over the volatility, and a time limit reached with a probability that grows
with it. All draws come from one stream keyed `history` (part, history) under the role's seed
(`extended.three_way_keys.seed_key`).

**The designs** (`DesignSpec`) are stylised: a stream (or fixed marks), a stop in volatility units with tick caps, a
reward ratio, a size, costs per contract, the walk's lattice step, the latency, and at most so many trades a session.
Each design takes a stream's arrivals in time order, skipping any that would enter while its position is open, so its
schedule never overlaps (the runner refuses one that does). **The baselines here are toys standing in for naive coin,
P-14, P-15 and P-16 on synthetic histories, never the registered designs**: their real schedules come from their
registered trades in H4, through the same runner.

numpy only; reads no file and no bar.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Sequence

import numpy as np

from extended import family_stats as FS
from extended import three_way_journey as J
from extended import three_way_keys as K
from extended import three_way_redraw as RD

STREAMS = ("A", "B")
#: the decision slots a stylised day reads (08:30 to 14:00 CT on the engine's clock: minutes after 17:00 CT)
FIRST_SLOT, LAST_SLOT = 930, 1260
#: R-10's clock unit: the volatility is read in ticks per square root of a minute
MINUTE = 1.0


@dataclass(frozen=True)
class S1Params:
    """The generator's parameters (declared per part; stylised in H3-A)."""

    n_sessions: int
    vol_mean: float = 6.0          # ticks per sqrt(minute), the mean of the volatility
    phi: float = 0.9               # the log volatility's AR(1) persistence
    vol_sd: float = 0.15           # its innovation's sd
    regime_amp: float = 0.0        # the slow regime's amplitude in log volatility (0: none)
    regime_switch: float = 0.02    # its switching probability a session
    rate: float = 1.5              # arrivals a stream a session at the mean volatility
    rate_beta: float = 1.0         # the rate's elasticity to the volatility
    hold_mean: float = 30.0        # minutes to resolution at the mean volatility, for a stop of `hold_stop` ticks
    hold_stop: float = 40.0
    time_limit: float = 90.0       # minutes: a hold past it ends at the time limit (R-10's walk)


@dataclass(frozen=True)
class Arrival:
    slot: int
    hold: float
    stream: str


@dataclass(frozen=True)
class S1History:
    params: S1Params
    vol: np.ndarray
    regime: np.ndarray
    streams: dict = field(repr=False)        # stream -> tuple over sessions of tuples of Arrival

    def swap(self) -> "S1History":
        """The generator's symmetry: streams A and B exchanged (each arrival keeps its own label's stream)."""
        sw = {"A": self.streams["B"], "B": self.streams["A"]}
        return S1History(self.params, self.vol, self.regime, sw)


def generate(seed: int, part: int, history: int, params: S1Params) -> S1History:
    """One S1 history from the key `history` (part, history) under `seed` (a role seed of H3's block, issued)."""
    rng = np.random.default_rng(K.seed_key(seed, "history", part=part, history=history))
    n = int(params.n_sessions)
    regime = FS.slow_sign(rng, n, params.regime_switch) if params.regime_amp > 0 else np.zeros(n)
    eps = rng.standard_normal(n) * params.vol_sd
    lv = np.zeros(n)
    for t in range(1, n):
        lv[t] = params.phi * lv[t - 1] + eps[t]
    vol = params.vol_mean * np.exp(lv + params.regime_amp * regime)
    streams: dict[str, list] = {}
    for s in STREAMS:
        day = []
        rate = params.rate * (vol / params.vol_mean) ** params.rate_beta
        counts = rng.poisson(rate)
        for t in range(n):
            slots = np.sort(rng.integers(FIRST_SLOT, LAST_SLOT + 1, counts[t]))
            holds = rng.exponential(params.hold_mean, counts[t])
            day.append(tuple(Arrival(int(a), float(h), s) for a, h in zip(slots, holds)))
        streams[s] = tuple(day)
    return S1History(params, vol, regime, streams)


@dataclass(frozen=True)
class DesignSpec:
    """A stylised design (or a baseline's toy): where its trades come from and their shape."""

    name: str
    stream: str | None = "A"        # a stream of S1, or None for fixed marks
    marks: tuple[int, ...] = ()     # fixed decision slots (when stream is None)
    k_stop: float = 6.0             # the stop in volatility units (ticks per sqrt(minute) times this)
    stop_lo: int = 8
    stop_hi: int = 120
    fixed_stop: int | None = None   # a fixed stop in ticks (overrides k_stop)
    rr: float = 1.0
    contracts: int = 1
    tick_value: float = 5.0
    entry_cost: float = 0.0          # dollars a contract
    x_target: float = 0.0
    x_stop: float = 0.0
    x_flat: float = 0.0
    walk_step: int = 2
    latency: int = 5
    per_session: int = 3

    def stop(self, v: float) -> int:
        if self.fixed_stop is not None:
            return int(self.fixed_stop)
        s = int(round(self.k_stop * v))
        s = min(max(s, self.stop_lo), self.stop_hi)
        return max(self.walk_step, self.walk_step * int(round(s / self.walk_step)))


def schedule(spec: DesignSpec, hist: S1History) -> J.Schedule:
    """The design's trades on the history: each arrival (or mark) in time order, skipped while a position is open;
    the hold scaled by the stop over the volatility; a hold past the time limit ends there (R-10's walk with its
    steps from the volatility at the alert and the time to the limit)."""
    p = hist.params
    out: list[J.Trade] = []
    for t in range(p.n_sessions):
        v = float(hist.vol[t])
        if spec.stream is None:
            arr = [Arrival(int(m), p.hold_mean, "M") for m in spec.marks]
        else:
            arr = list(hist.streams[spec.stream][t])
        busy_until, taken = -1, 0
        for sub, a in enumerate(arr):
            if taken >= spec.per_session or sub >= K.MOMENT_SUBS:
                break
            entry = a.slot + spec.latency
            if entry < busy_until or entry >= K.DAY_SLOTS - 1:
                continue
            l = spec.stop(v)
            g = max(spec.walk_step, spec.walk_step * int(round(spec.rr * l / spec.walk_step)))
            hold = a.hold * (l / p.hold_stop) * (p.vol_mean / v) ** 2
            timed = hold > p.time_limit
            dur = int(math.ceil(min(hold, p.time_limit)))
            ex = min(entry + max(dur, 1), K.DAY_SLOTS)
            if ex <= entry:
                continue
            n_steps = RD.walk_steps(v / math.sqrt(MINUTE), max(ex - entry, 1), spec.walk_step) if timed else 1
            c = spec.contracts
            out.append(J.Trade(session=t, decision=a.slot, sub=sub, entry=entry, exit=ex,
                               exit_reason="flatten" if timed else "target", g=g, l=l, tick_value=spec.tick_value,
                               contracts=c, entry_cost=spec.entry_cost * c, x_target=spec.x_target * c,
                               x_stop=spec.x_stop * c, x_flat=spec.x_flat * c, walk_step=spec.walk_step,
                               walk_n=n_steps))
            busy_until, taken = ex, taken + 1
    return J.Schedule(spec.name, tuple(out))


def toy_baselines(tick_value: float = 5.0, cost: float = 0.0) -> dict[str, DesignSpec]:
    """Stylised stand-ins for the baseline set on S1 (names as the runner requires; never the registered designs)."""
    return {
        "naive_coin": DesignSpec("naive_coin", stream=None, marks=(960, 1080), fixed_stop=40, rr=1.0,
                                 tick_value=tick_value, entry_cost=cost, x_target=cost, x_stop=cost, x_flat=cost),
        "p14": DesignSpec("p14", stream=None, marks=(1000,), fixed_stop=50, rr=2.0, tick_value=tick_value,
                          entry_cost=cost, x_target=cost, x_stop=cost, x_flat=cost),
        "p15": DesignSpec("p15", stream=None, marks=(1020,), fixed_stop=100, rr=1.0, tick_value=tick_value,
                          entry_cost=cost, x_target=cost, x_stop=cost, x_flat=cost),
        "p16": DesignSpec("p16", stream=None, marks=(1140,), fixed_stop=150, rr=1.0, tick_value=tick_value,
                          entry_cost=cost, x_target=cost, x_stop=cost, x_flat=cost),
    }


__all__ = ["STREAMS", "FIRST_SLOT", "LAST_SLOT", "S1Params", "Arrival", "S1History", "generate", "DesignSpec",
           "schedule", "toy_baselines"]
