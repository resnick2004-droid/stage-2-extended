"""Q-185c (the lead's ruling on BUILD_FIRMPATH_c3's C3-2): the **common-path law for rungs** -- several trades from one
alert, on one market at one moment, read ONE driftless path, each racing its own barriers on it. Pure: numpy, no engine,
no bar, no draw of its own (the uniforms are the caller's: one stream per alert, keyed at sub 0).

**The construction -- exact for every barrier.** The path is a standard Brownian motion in ticks from the fill,
observed at its successive hitting times of a lattice of step `h` ticks, together with, for each lattice step, **the
extreme it reached on the other side** before arriving:
- each step goes up or down one lattice step with probability one half (uniform `2k`: up where below one half);
- an up step from x to x + h dips first to its minimum m in (x - h, x], whose law, given that the step ends at x + h
  and not at x - h, is P(m <= b) = (b - (x - h)) / ((x + h) - b) for b in (x - h, x]; so m = (a + u c) / (1 + u), a =
  x - h, c = x + h, from uniform `2k + 1`; a down step's maximum M in [x, x + h) mirrors it, M = (c + u a) / (1 + u).
  Both laws are the h-transform of the driftless first-passage odds (P_x(hit b before a) = (x - a)/(b - a),
  conditioned on the step's end).
The step's range -- [m, x + h] up, [x - h, M] down -- is then exactly the set of levels the continuous path touched
during it, so **any level's first touch is read exactly**: the first step whose range reaches it. A rung's race between
its own -L and +G therefore wins with probability L / (L + G) exactly, its bracket's driftless odds, whatever `h` is:
`h` decides only how many uniforms the path uses, never a rung's odds (refused unless the rung's barriers are at least
2h apart, so its two barriers cannot both fall inside one step's range, where their order would not be read).

**Time.** A time-limited rung (R-10's walk to its limit, the move's phases) counts its time in lattice steps, n =
`walk_steps(sigma, T, h)` -- the same discretisation of time as R-10's walk; `h` is fixed per alert by the step rule
`walk_step(sigma, T_max, WALK_MAX)`, T_max the longest time any rung of the alert needs, so every rung's steps are at
most `WALK_MAX`. A rung not absorbed by its limit exits at the path's lattice value there. **Its marginal law is R-10's
time-limited walk read on a finer lattice than its own single-trade step** -- the barriers exact, the clock discretised:
its marginal shares (target, stop, time) are held within `TIMED_TOL` of the rung's own single-trade law (R-10, its own
step, `three_way_redraw.walk_law`) by `tests/test_three_way_rungs.py` on a declared grid. `TIMED_TOL` and the step rule
are **fixed** (classed: fixed, not searched).

**A single-rung alert never reads this module**: it books exactly as before (the single-trade race, walk and move laws,
their identities and oracles unchanged).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np

TARGET, STOP, TIME, BREAKEVEN = 1, -1, 0, 3
#: the time-limited rungs' marginal tolerance against their own single-trade law (fixed; the test's declared grid)
TIMED_TOL = 0.02
#: uniforms are read this many steps at a time
CHUNK = 64


@dataclass
class CommonPath:
    """One alert's path, extended lazily from `read(first, count)` (two uniforms a step). `x[k]` is the lattice value
    after k steps (x[0] = 0), `lo[k]` / `hi[k]` the range step k touched (k >= 1)."""

    read: Callable
    h: float
    x: list = field(default_factory=lambda: [0.0])
    lo: list = field(default_factory=lambda: [0.0])
    hi: list = field(default_factory=lambda: [0.0])

    def _extend(self, upto: int) -> None:
        while len(self.x) <= upto:
            k0 = len(self.x) - 1                       # steps made so far
            u = np.asarray(self.read(2 * k0, 2 * CHUNK), float)
            h = self.h
            for j in range(CHUNK):
                x0 = self.x[-1]
                a, c = x0 - h, x0 + h
                v = float(u[2 * j + 1])
                if float(u[2 * j]) < 0.5:              # up: the minimum on the way, then x0 + h
                    self.lo.append((a + v * c) / (1.0 + v))
                    self.hi.append(c)
                    self.x.append(c)
                else:                                  # down: the maximum on the way, then x0 - h
                    self.lo.append(a)
                    self.hi.append((c + v * a) / (1.0 + v))
                    self.x.append(a)

    def first_touch(self, lo: float, hi: float, start: int, stop: int | None) -> tuple[int, int]:
        """(the kind, the step): the first step k in (start, stop] whose range reaches `lo` (STOP) or `hi` (TARGET);
        (TIME, stop) when neither by `stop` (None: no limit, the path extended until one is reached). Refused if one
        step reaches both (the rung's barriers closer than 2h)."""
        if not lo < self.x[start] < hi:
            raise ValueError("the path starts strictly between the rung's barriers")
        k = start
        while stop is None or k < stop:
            k += 1
            if k >= len(self.x):
                self._extend(k + CHUNK)
            a, b = self.lo[k] <= lo, self.hi[k] >= hi
            if a and b:
                raise RuntimeError("a rung's two barriers fall in one step's range: they are closer than 2h")
            if a:
                return STOP, k
            if b:
                return TARGET, k
        return TIME, int(stop)

    def value(self, k: int) -> float:
        if k >= len(self.x):
            self._extend(k)
        return float(self.x[k])


def check_step(h: float, *gaps: float) -> None:
    """Refused unless every rung's barrier distance (L + G, or the moved phase's G) is at least 2h."""
    bad = [g for g in gaps if not g >= 2.0 * h - 1e-12]
    if bad:
        raise ValueError(f"REFUSED: the common path's step {h} ticks is more than half a rung's barrier distance {bad}")


def race(path: CommonPath, L: float, G: float) -> tuple[int, float]:
    """An untimed rung: (kind, gross ticks) of the race between -L and +G on the path."""
    check_step(path.h, L + G)
    k, _ = path.first_touch(-L, G, 0, None)
    return k, (G if k == TARGET else -L)


def walk(path: CommonPath, L: float, G: float, n: int) -> tuple[int, float]:
    """A time-limited rung: the race between -L and +G for n lattice steps, else the path's value at n."""
    check_step(path.h, L + G)
    k, at = path.first_touch(-L, G, 0, int(n))
    return k, (G if k == TARGET else -L if k == STOP else path.value(at))


def move(path: CommonPath, L: float, G: float, n1: int, n2: int, favour: float = 1.0) -> tuple[int, float, dict]:
    """The time-limited move on the path: phase 1 for n1 steps between -L and +G; at x, at least `favour` ticks in
    favour the stop moves to the entry, then phase 2 for n2 steps between 0 (or -L) and +G. Returns (kind, gross ticks,
    the inputs read: x, moved)."""
    check_step(path.h, L + G)
    k, at = path.first_touch(-L, G, 0, int(n1))
    if k != TIME:
        return k, (G if k == TARGET else -L), {"x": float("nan"), "moved": False}
    x = path.value(int(n1))
    moved = x >= favour
    low = 0.0 if moved else -L
    if moved:
        check_step(path.h, G)
    k2, at2 = path.first_touch(low, G, int(n1), int(n1) + int(n2))
    if k2 == TARGET:
        return TARGET, G, {"x": x, "moved": moved}
    if k2 == STOP:
        return (BREAKEVEN, 0.0, {"x": x, "moved": moved}) if moved else (STOP, -L, {"x": x, "moved": moved})
    return TIME, path.value(at2), {"x": x, "moved": moved}


__all__ = ["TARGET", "STOP", "TIME", "BREAKEVEN", "TIMED_TOL", "CHUNK", "CommonPath", "check_step", "race", "walk",
           "move"]
