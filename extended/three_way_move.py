"""Q-185c (H4's RC-1, rc-4): the law of a `b` exit -- FV3's breakeven move -- under the move-aware sequential race,
for the firm path's baseline mode. Pure: fractions and numpy, no engine, no bar, no draw of its own (the uniforms are
the caller's).

**The law** (the red team's RC-1 remedy, item 3; the overlap row's exact form, one driftless path):
1. **To the move bar.** R-10's stopped walk from the fill (`three_way_redraw.walk_run`, lattice step s, the floor-side
   barrier L and the target G in ticks, a barrier off the lattice reached by the two-point last sub-step) for
   `n_move` steps -- the steps from the fill to the move bar's open, from the volatility at the alert and that time,
   both known at the fill. Absorbed at +G: the target; at -L: the stop.
2. **At the move bar**, the walk at x ticks:
   - **x at least one tick in favour (x >= `favour` ticks): the stop moves to the entry.** A driftless race between the
     entry (0) and +G from x: the target with probability x / G, else the moved stop at the entry -- the `b` exit,
     gross 0 (its exit cost the stop side's).
   - **otherwise** the race continues between -L and +G from x: the target with probability (x + L) / (G + L), else
     the stop.
Its gross expectation is zero exactly: each phase is a martingale move stopped at its barriers (optional stopping at a
bounded time, then a fair race). `move_law` is the exact law (fractions in, fractions out), `move_outcomes` the
sampler on given uniforms (the walk's, one a step, then one race uniform a lane).

**What the runner must add for it** (`three_way_journey`, `three_way_redraw`; wt/wt-three): an exit state for the move
in `EXIT_LAW` (`"breakeven": "move"`), and on the trade the steps to the move bar (`move_n`, from the volatility at the
alert and the move bar's open as the walk's `be_open` names it, never a later bar) beside its step; the firm path's
law then reads the walk's uniforms (`K.WALK`) for phase 1 and the race uniform (`K.RACE`) for phase 2, keyed as now.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Callable

import numpy as np

from extended import three_way_redraw as RD

TARGET, STOP, BREAKEVEN = 1, -1, 3
#: the walk must stand at least this many ticks in favour at the move bar for the stop to move (FV3's "a tick or more")
FAVOUR = 1


def move_law(G, L, s, n_move: int, favour=FAVOUR) -> dict[tuple[str, object], object]:
    """The exact law of the move-aware sequential race: {(kind, gross ticks): probability}, kinds "target" (+G),
    "stop" (-L) and "breakeven" (0). Fractions in, fractions out."""
    exact = all(isinstance(v, Fraction) for v in (G, L))
    one = Fraction(1) if exact else 1.0
    G = Fraction(G) if exact else float(G)
    L = Fraction(L) if exact else float(L)
    law = RD.walk_law(G, L, Fraction(s) if exact else float(s), int(n_move))
    out: dict[tuple[str, object], object] = {}

    def add(k, pr):
        out[k] = out.get(k, 0) + pr

    for (kind, v), pr in law.items():
        if kind == "target":
            add(("target", G), pr)
        elif kind == "stop":
            add(("stop", -L), pr)
        elif v >= favour:                                   # the stop moves to the entry: race 0 against +G from v
            q = (Fraction(v) if exact else float(v)) / G
            add(("target", G), pr * q)
            add(("breakeven", 0 * one), pr * (one - q))
        else:                                               # the race continues: -L against +G from v
            q = ((Fraction(v) if exact else float(v)) + L) / (G + L)
            add(("target", G), pr * q)
            add(("stop", -L), pr * (one - q))
    return out


def move_outcomes(read: Callable, lanes: int, G, L: np.ndarray, s: int, n_move: int, u_race: np.ndarray,
                  chunk: int = 32, favour=FAVOUR) -> tuple[np.ndarray, np.ndarray]:
    """The law on given uniforms: phase 1 by `three_way_redraw.walk_run` (`read(rows, first, count)` the walk's),
    phase 2 on `u_race` (one a lane): the target where u < its probability. Returns (gross ticks, kinds 1 / -1 / 3)."""
    L = np.asarray(L, float)
    v, k = RD.walk_run(read, int(lanes), G, L, int(s), int(n_move), int(chunk))
    u = np.asarray(u_race, float)
    G = np.broadcast_to(np.asarray(G, float), (int(lanes),))
    live = k == 0
    moved = live & (v >= favour)
    q = np.where(moved, v / G, (v + L) / (G + L))
    hit = live & (u < q)
    kind = np.where(k == 1, TARGET, np.where(k == -1, STOP,
                    np.where(hit, TARGET, np.where(moved, BREAKEVEN, STOP))))
    gross = np.where(kind == TARGET, G, np.where(kind == STOP, -L, 0.0)).astype(float)
    return gross, kind


def move_gross(G, L, s, n_move: int, favour=FAVOUR):
    """The law's gross expectation (zero exactly in fractions)."""
    return sum(pr * v for (_, v), pr in move_law(G, L, s, n_move, favour).items())


__all__ = ["TARGET", "STOP", "BREAKEVEN", "FAVOUR", "move_law", "move_outcomes", "move_gross"]
