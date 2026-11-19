"""Wave 3.2: the martingale-outcome reading's redraw -- the race at the cushion less the stop exit's own cost, R-10's
stopped driftless lattice walk for a trade ending at a time limit, the exit-state map, the plants and the worse-fill
stress (CHARTER 3.2; `docs/plans/THREE_WAY_TEST_design.md` 1.1, 2.4, 4.2; the third read's M-4; measure 29).

**The race** (B-1, N-5, M-4). A trade has a stop of l ticks and a target of g ticks; c is its account's cushion -- the
room to the nearer of the floor and the daily loss limit -- read **after the entry cost is booked**, and x_stop the stop
exit's own cost (commission plus declared stop slippage), x_target the target side's, all in ticks (fractions
allowed). The loss barrier is

    L = min(l, c - x_stop), rounded inward to the lattice (whole ticks by default: `LATTICE`)

and the driftless first exit wins with p = L / (L + g): +g less x_target, else -L less x_stop. A trade with L <= 0 is
not taken. Every trade's gross expectation is exactly zero; its net is exactly -(entry + p x_target + (1 - p) x_stop);
a costed loss lands at most on the floor, so the engine's clip never binds (`race_net` is the exact-fraction oracle;
`three_way_arith.race_redraw` is the reference law it reduces to at one exit cost and no rounding).

**Inward rounding (the brief; N-4).** A stop is placed at a tick, so the loss is a whole number of ticks: the race's L
is rounded down to the lattice (`LATTICE` = 1 tick, declared; `None` keeps fractions, the form `adapter.BinaryDraw` uses
at no cost, which a test holds equal on the same uniforms). Rounding down keeps gross zero and the floor unpassed;
rounding outward and clipping would bring B-1's edge back.

**R-10's stopped walk** (the search template's house form, `prereg/TEMPLATE_design_search.md` on wt/wt-lit, adopted as
written there; Wave 2.5 reads it). A symmetric walk from the fill on a lattice of step s ticks, s dividing l and g; its
loss barrier the race's L with x_stop replaced by the larger of x_stop and the flatten-side cost, rounded inward to the
lattice; its target g; it stops at the first barrier or after n steps, n = round(sigma^2 T / s^2) (halves up, at least
one) from the trade's causal volatility at the alert and its time to the limit -- both the schedule's fields, never a
later bar. Its outcome: +g (target cost), -L (stop cost) or the walk's value at n (flatten cost). Gross zero exactly
(optional stopping), and no exit passes the floor (`walk_law` and `walk_net` are the exact oracles).

**The exit-state map** (R-10's table): `EXIT_LAW` maps every terminal state of the run to its law; an exit reason it
does not name is refused.

**The plants** (4.2): P3's edge plant raises the race's win probability by epsilon (`u < p + eps`), on the design's arm
only. **The worse-fill stress** (measure 29; `WORSE_FILL_TICKS`): every fill k ticks worse -- the entry and the exit,
whichever it is -- for the design and every baseline alike; the stop side's k ticks enter the race's barrier.

Pure: fractions and numpy; no draw (the uniforms are the caller's), no bar, no file.
"""
from __future__ import annotations

import math
from fractions import Fraction
from typing import Sequence

import numpy as np

#: the race's lattice in ticks (inward rounding of L): a stop sits at a tick
LATTICE: int | None = 1
#: R-10's table: every terminal state of the run, and the law its redraw takes
EXIT_LAW: dict[str, str] = {
    "target": "race",          # its target
    "stop": "race",            # its stop
    "stop_gap": "race",        # its stop gapped through (the gap's extra fill read beside, as-walked)
    "floor": "race",           # the floor or the daily loss limit, before its stop (the cushion is the nearer barrier)
    "flatten": "walk",         # the 15:10 CT flatten
    "news": "walk",            # a news window's start (E-202 (2)(a))
    "max_hold": "walk",        # its max hold
    "other": "walk",           # an unscheduled release's flatten, a rule's exit
}
#: measure 29's stress arms, declared and counted: every fill this many ticks worse
WORSE_FILL_TICKS = (1, 2)


def law_of(exit_reason: str) -> str:
    """The redraw's law for a terminal state of the run; refused for a state R-10's table does not name."""
    if exit_reason not in EXIT_LAW:
        raise ValueError(f"REFUSED (R-10): the exit reason {exit_reason!r} is not in the table {sorted(EXIT_LAW)}")
    return EXIT_LAW[exit_reason]


def _frac(v) -> Fraction:
    return v if isinstance(v, Fraction) else Fraction(v)


def inward(L: Fraction, lattice: int | Fraction | None) -> Fraction:
    """L rounded down to a multiple of the lattice (None: unchanged)."""
    if lattice is None:
        return L
    q = _frac(lattice)
    if q <= 0:
        raise ValueError("a lattice step is positive")
    return q * math.floor(L / q)


def race(l, g, c, x_stop=0, lattice: int | Fraction | None = LATTICE) -> tuple[Fraction, Fraction, Fraction] | None:
    """(p, win, loss) in ticks for stop l, target g, cushion c after the entry cost, stop-side cost x_stop: the race of
    the nearer barrier at L = min(l, c - x_stop) rounded inward; None when L <= 0 (the trade is not taken)."""
    l, g, c, x = (_frac(v) for v in (l, g, c, x_stop))
    if l <= 0 or g <= 0 or x < 0:
        raise ValueError("stop and target are positive, the exit cost non-negative")
    L = inward(min(l, c - x), lattice)
    if L <= 0:
        return None
    return L / (L + g), g, L


def race_net(l, g, c_before, entry=0, x_target=0, x_stop=0, lattice: int | Fraction | None = LATTICE
             ) -> tuple[Fraction, Fraction, Fraction] | None:
    """The exact oracle from a cushion measured before the entry cost: (gross expectation, net expectation, the worst
    balance change); None when the trade is not taken."""
    e, xt, xs = _frac(entry), _frac(x_target), _frac(x_stop)
    r = race(l, g, _frac(c_before) - e, xs, lattice)
    if r is None:
        return None
    p, win, loss = r
    gross = p * win - (1 - p) * loss
    net = -e + p * (win - xt) + (1 - p) * (-loss - xs)
    return gross, net, -(e + loss + xs)


def race_outcome(u: np.ndarray, p: np.ndarray, eps: float = 0.0) -> np.ndarray:
    """The race's win indicator for uniforms u: `u < p` (`u < p + eps` under P3's edge plant)."""
    return np.asarray(u, float) < (np.asarray(p, float) + float(eps))


def race_dollars(u: np.ndarray, risk: float, win: float, cushion: np.ndarray, x_stop: float = 0.0,
                 x_target: float = 0.0, lattice: float | None = None) -> np.ndarray:
    """The race in dollars, vectorised (`adapter.BinaryDraw`'s form at no cost and no lattice): the loss barrier
    min(risk, cushion - x_stop) rounded down to `lattice` dollars, p = L / (L + win); +win - x_target where u < p,
    else -L - x_stop; 0 where L <= 0 (not taken)."""
    cush = np.asarray(cushion, float)
    L = np.minimum(float(risk), cush - float(x_stop))
    if lattice is not None:
        L = float(lattice) * np.floor(L / float(lattice))
    L = np.maximum(L, 0.0)
    with np.errstate(invalid="ignore", divide="ignore"):
        p = np.where(L > 0, L / (L + float(win)), 0.0)
    out = np.where(np.asarray(u, float) < p, float(win) - float(x_target), -L - float(x_stop))
    return np.where(L > 0, out, 0.0)


# ------------------------------------------------------------------------------------------------ R-10's stopped walk


def walk_steps(sigma: float, T: float, s: float) -> int:
    """R-10's number of steps n = round(sigma^2 T / s^2), halves up, at least one (sigma in ticks per sqrt of T's unit,
    T the time from the fill to the limit, s the lattice step in ticks)."""
    if not (sigma > 0 and T > 0 and s > 0):
        raise ValueError("sigma, T and the step are positive")
    v = sigma * sigma * T / (s * s)
    return max(1, int(math.floor(v + 0.5)))


def walk_barriers(l: int, g: int, c, x_stop=0, x_flat=0, s: int = 1) -> tuple[int, int] | None:
    """(up, down) in steps: the target g / s and the loss barrier min(l, c - max(x_stop, x_flat)) rounded inward to the
    lattice of step s, over s; None when the barrier is at or below zero (not taken). Refused unless s divides l and g."""
    if not (isinstance(l, (int, np.integer)) and isinstance(g, (int, np.integer)) and isinstance(s, (int, np.integer))):
        raise ValueError("the walk's stop, target and step are whole ticks")
    if s <= 0 or l <= 0 or g <= 0 or l % s or g % s:
        raise ValueError("the lattice step divides the stop and the target")
    xw = max(_frac(x_stop), _frac(x_flat))
    L = inward(min(_frac(l), _frac(c) - xw), s)
    if L <= 0:
        return None
    return int(g // s), int(L // s)


def walk_law(up: int, down: int, n: int) -> dict[int, Fraction]:
    """The exact law of the stopped walk's terminal position in steps: absorbed at +up or -down, else its position
    after n steps (a forward dynamic program in exact fractions)."""
    if up <= 0 or down <= 0 or n <= 0:
        raise ValueError("barriers and steps are positive")
    half = Fraction(1, 2)
    live = {0: Fraction(1)}
    done: dict[int, Fraction] = {}
    for _ in range(int(n)):
        nxt: dict[int, Fraction] = {}
        for x, pr in live.items():
            for y in (x + 1, x - 1):
                if y >= up or y <= -down:
                    done[y] = done.get(y, Fraction(0)) + pr * half
                else:
                    nxt[y] = nxt.get(y, Fraction(0)) + pr * half
        live = nxt
    for x, pr in live.items():
        done[x] = done.get(x, Fraction(0)) + pr
    return done


def walk_net(l: int, g: int, c_before, n: int, s: int = 1, entry=0, x_target=0, x_stop=0, x_flat=0
             ) -> tuple[Fraction, Fraction, Fraction] | None:
    """The stopped walk's exact oracle from a cushion measured before the entry cost: (gross expectation, net
    expectation, the worst balance change); None when not taken."""
    e, xt, xs, xf = (_frac(v) for v in (entry, x_target, x_stop, x_flat))
    b = walk_barriers(l, g, _frac(c_before) - e, xs, xf, s)
    if b is None:
        return None
    up, down = b
    law = walk_law(up, down, n)
    gross = sum(pr * x * s for x, pr in law.items())
    net = -e
    worst = None
    for x, pr in law.items():
        cost = xt if x >= up else xs if x <= -down else xf
        v = x * s - cost
        net += pr * v
        worst = v if worst is None else min(worst, v)
    return gross, net, -e + worst


def walk_outcome(us: Sequence[float], up: int, down: int) -> tuple[int, str]:
    """The stopped walk on the uniforms `us` (one a step: +1 where u < 1/2): (its terminal position in steps, its exit
    kind -- "target", "stop" or "time")."""
    x = 0
    for u in us:
        x += 1 if u < 0.5 else -1
        if x >= up:
            return x, "target"
        if x <= -down:
            return x, "stop"
    return x, "time"


def walk_outcomes(U: np.ndarray, up: np.ndarray, down: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """`walk_outcome` over lanes (U one row a lane, one column a step): (positions, kinds as 1 target, -1 stop,
    0 time)."""
    U = np.asarray(U, float)
    lanes, n = U.shape
    x = np.zeros(lanes, np.int64)
    kind = np.zeros(lanes, np.int64)
    alive = np.ones(lanes, bool)
    up, down = np.asarray(up), np.asarray(down)
    for j in range(n):
        step = np.where(U[:, j] < 0.5, 1, -1)
        x = np.where(alive, x + step, x)
        hit_up = alive & (x >= up)
        hit_dn = alive & (x <= -down)
        kind[hit_up], kind[hit_dn] = 1, -1
        alive &= ~(hit_up | hit_dn)
        if not alive.any():
            break
    return x, kind


def worse_fill(entry: float, x_target: float, x_stop: float, x_flat: float, ticks: int, tick_dollars: float
               ) -> tuple[float, float, float, float]:
    """Measure 29: every fill `ticks` ticks worse -- the entry and each exit -- at `tick_dollars` a tick (the tick
    value times the contracts)."""
    if ticks < 0:
        raise ValueError("a worse fill is a non-negative number of ticks")
    d = float(ticks) * float(tick_dollars)
    return entry + d, x_target + d, x_stop + d, x_flat + d


def stress_cells(n_arms: int) -> int:
    """The stress arms counted: each compared arm (the design and every baseline) at each declared worse fill."""
    return int(n_arms) * len(WORSE_FILL_TICKS)


__all__ = ["LATTICE", "EXIT_LAW", "WORSE_FILL_TICKS", "law_of", "inward", "race", "race_net", "race_outcome",
           "race_dollars", "walk_steps", "walk_barriers", "walk_law", "walk_net", "walk_outcome", "walk_outcomes",
           "worse_fill", "stress_cells"]
