"""Q-185c: FV3's breakeven move under the **time-limited** move-aware sequential race -- one law for every trade whose
move bar comes before its time limit, whatever its historical exit (the lead's rulings on BUILD_FIRMPATH_c2's C2-4,
C2-5 and N-3). Pure: fractions and numpy, no engine, no bar, no draw of its own (the uniforms are the caller's).

**The law**, every input known at the fill (the steps by `three_way_redraw.walk_step` and `walk_steps` from the
volatility at the alert and the time of each phase):
1. **To the move bar.** R-10's stopped walk from the fill between -L and +G (ticks; a barrier off the lattice reached by
   the two-point last sub-step), on its own lattice `s1` -- the step from the **time to the move bar** (C2-5), not the
   whole limit, so the one-tick test below is resolved finely -- for `n1` steps. Absorbed at +G: the target; at -L:
   the stop.
2. **From the move bar to the limit**, the walk at x ticks: R-10's stopped walk from x on its own lattice `s2` (the
   step from the time left to the limit), for `n2` steps, between
   - **0 and +G when x is at least one tick in favour** (x >= `favour`): the stop moved to the entry -- a touch of 0 is
     the `b` exit, gross 0, at the stop side's cost;
   - **-L and +G otherwise**: the stop where it was.
   Not absorbed by the limit: the flatten at the walk's value (N-3: phase 2 is bounded by the limit, as FV3 flattens a
   moved, untouched trade at 15:10, `bop`).
Its gross expectation is zero exactly: each phase is a martingale stopped at its barriers at a bounded time (optional
stopping). `move_law` is the exact law (fractions in, fractions out), `move_outcomes` the sampler on given uniforms
(one walk stream a lane: phase 1 reads its first `n1` uniforms, phase 2 the next `n2`).

**What the runner (wt/wt-three) must add for the design mode**: `EXIT_LAW["breakeven"] = "move"` -- read for every
trade carrying a move bar before its limit, whatever its exit -- and on the trade the move bar's end index `be_open`
(s + 1 on the bar-end clock), the volatility at the alert and the time limit, with the phases' steps and step counts
from them; `_trade_mc` / `_trade_dp` dispatching to `move_outcomes` / `move_law`.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Callable

import numpy as np

from extended import three_way_redraw as RD

TARGET, STOP, TIME, BREAKEVEN = 1, -1, 0, 3
#: the walk must stand at least this many ticks in favour at the move bar for the stop to move (FV3's `be_fav > 0`,
#: on whole ticks: "a tick or more")
FAVOUR = 1


def move_law(G, L, s1, n1: int, s2, n2: int, favour=FAVOUR) -> dict[tuple[str, object], object]:
    """The exact law: {(kind, gross ticks): probability}, kinds "target" (+G), "stop" (-L), "breakeven" (0) and
    "time" (the walk's value at the limit). Fractions in (G and L as Fractions), fractions out."""
    exact = isinstance(G, Fraction) and isinstance(L, Fraction)
    cast = Fraction if exact else float
    G, L, s1, s2 = cast(G), cast(L), cast(s1), cast(s2)
    if int(n1) < 1 or int(n2) < 1:
        raise ValueError("each phase takes at least one step")
    out: dict[tuple[str, object], object] = {}

    def add(k, pr):
        out[k] = out.get(k, 0) + pr

    for (kind, v), pr in RD.walk_law(G, L, s1, int(n1)).items():
        if kind == "target":
            add(("target", G), pr)
            continue
        if kind == "stop":
            add(("stop", -L), pr)
            continue
        x = cast(v)
        moved = x >= favour
        down = x if moved else x + L                        # the distance to the floor side from x
        for (k2, v2), p2 in RD.walk_law(G - x, down, s2, int(n2)).items():
            if k2 == "target":
                add(("target", G), pr * p2)
            elif k2 == "stop":
                add(("breakeven", 0 * G) if moved else ("stop", -L), pr * p2)
            else:
                add(("time", x + cast(v2)), pr * p2)
    return out


def move_gross(G, L, s1, n1, s2, n2, favour=FAVOUR):
    """The law's gross expectation (zero exactly in fractions)."""
    return sum(pr * v for (_, v), pr in move_law(G, L, s1, n1, s2, n2, favour).items())


def move_outcomes(read: Callable, lanes: int, G, L, s1: int, n1: int, s2: int, n2: int, chunk: int = 32,
                  favour=FAVOUR, detail: bool = False):
    """The law on given uniforms, `read(rows, first, count)` the lanes' walk stream (phase 1 its uniforms 0 .. n1 - 1,
    phase 2 its uniforms n1 .. n1 + n2 - 1). Returns (gross ticks, kinds 1 target / -1 stop / 3 breakeven / 0 time),
    and with `detail` the inputs phase 2 read, for an auditor's replay: `x` (the walk at the move bar; NaN where phase
    1 ended it), `moved`, `G2` (the target's distance from x) and `down2` (the floor side's: x moved, x + L not)."""
    lanes = int(lanes)
    G = np.broadcast_to(np.asarray(G, float), (lanes,)).astype(float)
    L = np.broadcast_to(np.asarray(L, float), (lanes,)).astype(float)
    v, k = RD.walk_run(read, lanes, G, L, int(s1), int(n1), int(chunk))
    gross = np.where(k == 1, G, np.where(k == -1, -L, 0.0)).astype(float)
    kind = np.where(k == 1, TARGET, np.where(k == -1, STOP, TIME)).astype(np.int64)
    live = np.flatnonzero(k == 0)
    det = {"x": np.full(lanes, np.nan), "moved": np.zeros(lanes, bool), "G2": np.full(lanes, np.nan),
           "down2": np.full(lanes, np.nan)}
    if live.size:
        x = v[live]
        moved = x >= favour
        down = np.where(moved, x, x + L[live])

        def read2(rows, first, count):
            return read(live[rows], int(n1) + first, count)

        v2, k2 = RD.walk_run(read2, live.size, G[live] - x, down, int(s2), int(n2), int(chunk))
        g2 = np.where(k2 == 1, G[live], np.where(k2 == -1, np.where(moved, 0.0, -L[live]), x + v2))
        c2 = np.where(k2 == 1, TARGET, np.where(k2 == -1, np.where(moved, BREAKEVEN, STOP), TIME))
        gross[live], kind[live] = g2, c2
        det["x"][live], det["moved"][live], det["G2"][live], det["down2"][live] = x, moved, G[live] - x, down
    return (gross, kind, det) if detail else (gross, kind)


__all__ = ["TARGET", "STOP", "TIME", "BREAKEVEN", "FAVOUR", "move_law", "move_gross", "move_outcomes"]
