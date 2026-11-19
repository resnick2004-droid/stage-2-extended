"""Wave 3.2: the martingale-outcome reading's redraw -- the race at the cushion less the stop exit's own cost, R-10's
stopped driftless lattice walk for a trade ending at a time limit, the exit-state map, the plants and the worse-fill
stress (CHARTER 3.2; `docs/plans/THREE_WAY_TEST_design.md` 1.1, 2.4, 4.2; the third read's M-4; measure 29).

**The race** (B-1, N-5, M-4). A trade has a stop of l ticks and a target of g ticks; c is its account's cushion -- the
room to the nearer of the floor and the daily loss limit -- read **after the entry cost is booked**, and x_stop the stop
exit's own cost (commission plus declared stop slippage), x_target the target side's, all in ticks (fractions
allowed). The loss barrier is

    L = min(l, c - x_stop), fractional, never rounded (`adapter.BinaryDraw`'s form; the note's 1.1)

and the driftless first exit wins with p = L / (L + g): +g less x_target, else -L less x_stop. A trade with no room
(L <= 0) is not taken. Every trade's gross expectation is exactly zero; its net is exactly -(entry + p x_target +
(1 - p) x_stop); **a cushion-bound loss ends exactly on the floor, so the account fails and is replaced**, as the
vendored lockstep does, and the engine's clip never binds (`race_net` is the exact-fraction oracle;
`three_way_arith.race_redraw` the reference law it reduces to at one exit cost).

**No rounding (the lead's ruling on Wave 3.2's red-team B-1).** The first build rounded L down to whole ticks: a
cushion-bound loss then left every failing account a fraction of a tick above its floor, never breached, never
replaced, still billed. The race is fractional; inward rounding was N-4's rule for the shared path of overlapping
positions only, deferred to the template. `inward` and `race`'s `lattice` argument stay for that use.

**R-10's stopped walk** (the search template's house form, adopted with the lead's ruling on its residual step). A
symmetric walk from the fill on a lattice of step s ticks, s dividing l and g; its floor-side barrier the race's L
with x_stop replaced by the larger of x_stop and the flatten-side cost, **fractional**; its target g. **Inside the last
lattice step before the floor-side barrier** -- at the last lattice point above -L, rho = L - d s below it -- a step is
a driftless two-point race between the barrier and the lattice point one step up (to the barrier with probability
s / (s + rho)), so no account is stranded below a step and every step is a martingale move. It stops at the first
barrier or after n steps, n = round(sigma^2 T / s^2) (halves up, at least one) from the trade's causal volatility at the
alert and its time to the limit -- both the schedule's fields, never a later bar. Its outcome: +g (target cost), -L
(stop cost) or the walk's value at n (flatten cost). Gross zero exactly (optional stopping), and no exit passes the
floor (`walk_law` and `walk_net` are the exact oracles).

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

#: the race's lattice: none -- the race takes the fractional L = min(l, c - x_stop), `adapter.BinaryDraw`'s form
#: (the lead's ruling on the red team's B-1; inward rounding was N-4's rule for the shared path only)
LATTICE: int | None = None
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


def _bottom(L, s):
    """The walk's floor side: (d, rho) with -d the last lattice index above the barrier -L and rho = L - d s in (0, s]
    the residual below it. Exact for fractions; for floats an exact multiple of s read with `SNAP` of slack."""
    if isinstance(L, Fraction):
        d = math.ceil(L / s) - 1
    else:
        d = int(math.ceil(float(L) / float(s) - SNAP)) - 1
    d = max(d, 0)
    return d, L - d * s


SNAP = 1e-9


def walk_barriers(l: int, g: int, c, x_stop=0, x_flat=0, s: int = 1) -> tuple[int, Fraction] | None:
    """(up, L): the target g / s in steps and the floor-side barrier L = min(l, c - max(x_stop, x_flat)) in ticks,
    **fractional, never rounded** (the lead's ruling on B-1); None when L <= 0 (not taken). Refused unless s divides l
    and g."""
    if not (isinstance(l, (int, np.integer)) and isinstance(g, (int, np.integer)) and isinstance(s, (int, np.integer))):
        raise ValueError("the walk's stop, target and step are whole ticks")
    if s <= 0 or l <= 0 or g <= 0 or l % s or g % s:
        raise ValueError("the lattice step divides the stop and the target")
    xw = max(_frac(x_stop), _frac(x_flat))
    L = min(_frac(l), _frac(c) - xw)
    if L <= 0:
        return None
    return int(g // s), L


def walk_law(up: int, L, s, n: int) -> dict[tuple[str, object], object]:
    """The exact law of the stopped walk's outcome: {(kind, value in ticks): probability}, kind "target" (+g), "stop"
    (-L) or "time" (the walk's value after n steps). The walk moves on the lattice of step s from the fill, one step a
    draw, +s or -s with probability 1/2 each; **at the last lattice point above the floor-side barrier** (index -d,
    rho = L - d s below it) a step is a driftless two-point race between the barrier and the lattice point one step up:
    to -L with probability s / (s + rho), else up one step -- so no account is stranded below a step, and the gross
    expectation stays exactly zero (each step is a martingale move; optional stopping at a bounded time). Fractions in,
    fractions out (the oracle); floats in, floats out (the exact program's, the simulation's own arithmetic)."""
    if up <= 0 or n <= 0 or not L > 0:
        raise ValueError("barriers and steps are positive")
    exact = isinstance(L, Fraction)
    one = Fraction(1) if exact else 1.0
    half = one / 2
    d, rho = _bottom(L, s)
    q_bar = (s / (s + rho)) if exact else float(s) / (float(s) + float(rho))
    live = {0: one}
    done: dict[tuple[str, object], object] = {}

    def add(k, pr):
        done[k] = done.get(k, 0) + pr

    for _ in range(int(n)):
        nxt: dict[int, object] = {}
        for i, pr in live.items():
            if i == -d:
                moves = (("bar", pr * q_bar), (i + 1, pr * (one - q_bar)))
            else:
                moves = ((i + 1, pr * half), (i - 1, pr * half))
            for y, w in moves:
                if y == "bar":
                    add(("stop", -L), w)
                elif y >= up:
                    add(("target", up * s), w)
                else:
                    nxt[y] = nxt.get(y, 0) + w
        live = nxt
    for i, pr in live.items():
        add(("time", i * s), pr)
    return done


def walk_net(l: int, g: int, c_before, n: int, s: int = 1, entry=0, x_target=0, x_stop=0, x_flat=0
             ) -> tuple[Fraction, Fraction, Fraction] | None:
    """The stopped walk's exact oracle from a cushion measured before the entry cost: (gross expectation, net
    expectation, the worst balance change); None when not taken."""
    e, xt, xs, xf = (_frac(v) for v in (entry, x_target, x_stop, x_flat))
    b = walk_barriers(l, g, _frac(c_before) - e, xs, xf, s)
    if b is None:
        return None
    up, L = b
    law = walk_law(up, L, s, n)
    gross = sum(pr * v for (k, v), pr in law.items())
    net, worst = -e, None
    for (k, v), pr in law.items():
        cost = {"target": xt, "stop": xs, "time": xf}[k]
        net += pr * (v - cost)
        worst = v - cost if worst is None else min(worst, v - cost)
    return gross, net, -e + worst


def walk_outcome(us: Sequence[float], up: int, L, s) -> tuple[object, str]:
    """The stopped walk on the uniforms `us` (one a step): (its value in ticks, its exit kind -- "target", "stop" or
    "time"). A plain step is +s where u < 1/2; at the last lattice point above the barrier the step goes to the barrier
    where u < s / (s + rho), else up one."""
    d, rho = _bottom(L, s)
    q_bar = float(s) / (float(s) + float(rho))
    i = 0
    for u in us:
        if i == -d:
            if u < q_bar:
                return -L, "stop"
            i += 1
        else:
            i += 1 if u < 0.5 else -1
        if i >= up:
            return up * s, "target"
    return i * s, "time"


def walk_outcomes(U: np.ndarray, up: np.ndarray, L: np.ndarray, s: int) -> tuple[np.ndarray, np.ndarray]:
    """`walk_outcome` over lanes (U one row a lane, one column a step; L each lane's barrier in ticks, a float):
    (values in ticks, kinds as 1 target, -1 stop, 0 time)."""
    U = np.asarray(U, float)
    lanes, n = U.shape
    L = np.asarray(L, float)
    up = np.broadcast_to(np.asarray(up), (lanes,))
    d = np.maximum(np.ceil(L / s - SNAP).astype(np.int64) - 1, 0)
    rho = L - d * s
    q_bar = s / (s + rho)
    i = np.zeros(lanes, np.int64)
    kind = np.zeros(lanes, np.int64)
    alive = np.ones(lanes, bool)
    for j in range(n):
        u = U[:, j]
        at_bottom = i == -d
        to_bar = alive & at_bottom & (u < q_bar)
        step = np.where(at_bottom, 1, np.where(u < 0.5, 1, -1))
        i = np.where(alive & ~to_bar, i + step, i)
        kind[to_bar] = -1
        alive &= ~to_bar
        hit_up = alive & (i >= up)
        kind[hit_up] = 1
        alive &= ~hit_up
        if not alive.any():
            break
    val = np.where(kind == -1, -L, np.where(kind == 1, up * s, i * s)).astype(float)
    return val, kind


def walk_run(read, lanes: int, up: int, L: np.ndarray, s: int, n: int, chunk: int) -> tuple[np.ndarray, np.ndarray]:
    """`walk_outcomes` read `chunk` steps at a time: `read(rows, first, count)` gives the uniforms of steps first ..
    first + count - 1 of the lanes `rows` (indices into 0 .. lanes - 1). Only lanes still walking are read, and the
    walk stops when every lane is absorbed: the same outcome on the same uniforms as reading all n at once (the
    generator is counter-based), at the cost of the steps actually walked."""
    L = np.asarray(L, float)
    d = np.maximum(np.ceil(L / s - SNAP).astype(np.int64) - 1, 0)
    q_bar = s / (s + (L - d * s))
    i = np.zeros(lanes, np.int64)
    kind = np.zeros(lanes, np.int64)
    alive = np.ones(lanes, bool)
    pos = 0
    while pos < n and alive.any():
        c = min(int(chunk), n - pos)
        rows = np.flatnonzero(alive)
        U = read(rows, pos, c)
        ii, kk, al = i[rows], kind[rows], alive[rows]
        dd, qq = d[rows], q_bar[rows]
        for j in range(c):
            u = U[:, j]
            at_bottom = ii == -dd
            to_bar = al & at_bottom & (u < qq)
            step = np.where(at_bottom, 1, np.where(u < 0.5, 1, -1))
            ii = np.where(al & ~to_bar, ii + step, ii)
            kk[to_bar] = -1
            al &= ~to_bar
            hit = al & (ii >= up)
            kk[hit] = 1
            al &= ~hit
            if not al.any():
                break
        i[rows], kind[rows], alive[rows] = ii, kk, al
        pos += c
    val = np.where(kind == -1, -L, np.where(kind == 1, up * s, i * s)).astype(float)
    return val, kind


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
           "race_dollars", "walk_steps", "walk_barriers", "walk_law", "walk_net", "walk_outcome", "walk_outcomes", "walk_run",
           "worse_fill", "stress_cells"]
