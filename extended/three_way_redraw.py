"""Wave 3.2: the martingale-outcome reading's redraw -- the race at the cushion less the stop exit's own cost, R-10's
stopped driftless lattice walk for a trade ending at a time limit, the exit-state map, the plants and the worse-fill
stress (CHARTER 3.2; `docs/plans/THREE_WAY_TEST_design.md` 1.1, 2.4, 4.2; the third read's M-4; measure 29).

**The race** (B-1, N-5, M-4). A trade has a stop of l ticks and a target of g ticks; c is its account's cushion -- the
room to the nearer of the floor and the daily loss limit -- read **after the entry cost is booked**, and x_stop the stop
exit's own cost (commission plus declared stop slippage), x_target the target side's, all in ticks (fractions
allowed). The loss barrier is

    L = min(l, c - x_stop), fractional, never rounded (`adapter.BinaryDraw`'s form; the note's 1.1)

and the driftless first exit wins with p = L / (L + g): +g less x_target, else -L less x_stop. **The take** is
decided at the fill (below): a lane that cannot take its trade fails at the fill where its floor binds, or ends its day
where the daily limit binds (`three_way_journey._classes`). Every trade taken has gross expectation exactly zero; a
race's net is exactly -(entry + p x_target + (1 - p) x_stop); **a cushion-bound loss ends exactly on the floor, so the
account fails and is replaced**, as the vendored lockstep does. The engine's clip binds only where the engine's own
would: at a walk's flatten whose cost would pass the floor, and at an account failed at the fill (`race_net` is the
exact-fraction oracle; `three_way_arith.race_redraw` the reference law it reduces to at one exit cost).

**No rounding (the lead's ruling on Wave 3.2's red-team B-1).** The first build rounded L down to whole ticks: a
cushion-bound loss then left every failing account a fraction of a tick above its floor, never breached, never
replaced, still billed. The race is fractional; inward rounding was N-4's rule for the shared path of overlapping
positions only, deferred to the template. `inward` and `race`'s `lattice` argument stay for that use.

**The take, at the fill** (the template's N-1; the red team's m-1 on the runner): a trade is taken when
L_fill = min(l, c - max(x_stop, x_flat)) is above zero -- both exit costs, never the run's exit -- for every law.

**R-10's stopped walk** (the search template's house form, with the lead's rulings on its residual step and, in
corrective cycle 2, on its barrier and, by s-c, its step). A symmetric walk from the fill on a lattice of step s
ticks, **s = max(1, ceil(sigma sqrt(T) / sqrt(WALK_MAX)))** from the volatility at the alert and T the time limit known at
the fill (never the realised exit; the same T for s and n: `walk_step`), **s need not divide the stop or the target** --
a barrier off the lattice is reached by the two-point last sub-step below;
its floor-side barrier **the race's own, L = min(l, c - x_stop), fractional** (the red team's RB-1 remedy, first form:
a cushion-bound stop then ends exactly on the floor, never x_flat - x_stop above it); its target g. **Inside the last
lattice step before a barrier** -- the floor side's -L, and a target +G made fractional by a rule's profit level
(m-2) -- a step is a driftless two-point race between the barrier and the lattice point one step back (`_p_up`), so
either barrier is reached exactly and every step is a martingale move. It stops at the first barrier or
after n steps, n = round(sigma^2 T / s^2) (halves up, at least one) from the trade's causal volatility at the alert and
its time to the limit -- both the schedule's fields, never a later bar. Its outcome: +g (target cost), -L (stop cost)
or the walk's value at n (flatten cost). **A flatten exit whose cost would take the account below its floor is clipped
at the floor and fails the account, as the engine clips** (`lockstep.py`: `max(pnl, -cushion)`); the time exit lies
above -L, so the clip takes at most x_flat - x_stop. Gross zero exactly (optional stopping); the net is minus the
expected costs less that clip; no exit passes the floor (`walk_law` and `walk_net` are the exact oracles).

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
    "profit_level": "race",    # a rule's exit at a profit level: the race at the as-placed target min(g, level) (m-2)
    "other": "walk",           # an unscheduled release's flatten, or another exit at a real time limit
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
    the nearer barrier at L = min(l, c - x_stop) (rounded inward only at a declared `lattice`); None when L <= 0 (no
    race: the journey's take at the fill then fails the lane or ends its day)."""
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
    balance change); None when there is no race (L <= 0)."""
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
    else -L - x_stop; 0 where L <= 0 (no race; the journey's take at the fill decides that lane)."""
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


def walk_step(sigma: float, T: float, walk_max: int = 1024) -> int:
    """The walk's lattice step (the lead's governing rule, s-c): s = max(1, ceil(sigma sqrt(T) /
    sqrt(walk_max))) ticks, sigma the volatility at the alert in ticks per sqrt of T's unit, T the time limit known at
    the fill -- never the realised exit -- so that n = round(sigma^2 T / s^2) <= walk_max. A trade is never refused
    because of its step."""
    if not (sigma > 0 and T > 0 and walk_max >= 1):
        raise ValueError("sigma, T and the cap are positive")
    return max(1, int(math.ceil(sigma * math.sqrt(T) / math.sqrt(walk_max) - 1e-12)))


def walk_steps(sigma: float, T: float, s: float) -> int:
    """R-10's number of steps n = round(sigma^2 T / s^2), halves up, at least one (sigma in ticks per sqrt of T's unit,
    T the time from the fill to the limit, s the lattice step in ticks)."""
    if not (sigma > 0 and T > 0 and s > 0):
        raise ValueError("sigma, T and the step are positive")
    v = sigma * sigma * T / (s * s)
    return max(1, int(math.floor(v + 0.5)))


def _bottom(L, s):
    """An end of the walk: (d, rho) with d the last lattice index strictly inside the barrier at distance L (in ticks)
    and rho = L - d s in (0, s] the residual beyond it. Exact for fractions; for floats an exact multiple of s read with
    `SNAP` of slack. The same function serves the floor side (-L) and the target side (+G)."""
    if isinstance(L, Fraction):
        d = math.ceil(L / s) - 1
    else:
        d = int(math.ceil(float(L) / float(s) - SNAP)) - 1
    d = max(d, 0)
    return d, L - d * s


SNAP = 1e-9


def walk_barriers(l: int, g: int, c, x_stop=0, x_flat=0, s: int = 1, g_cap=None) -> tuple[Fraction, Fraction] | None:
    """(G, L) in ticks: the as-placed target G = min(g, g_cap) -- `g_cap` the target a rule's profit level sets, in
    gross ticks (the journey converts the engine's net need into it: `three_way_journey.Trade.target`; m-3) -- and
    the floor-side barrier L = min(l, c - x_stop) -- the race's own (corrective cycle 2, RB-1),
    **fractional, never rounded** (B-1); None when the take at the fill fails, L_fill = min(l, c - max(x_stop, x_flat))
    <= 0 (the template's N-1; the red team's m-1: the take reads both exit costs, never the exit). The step s need not
    divide l or g (s-c): a barrier off the lattice is reached by the two-point last sub-step; G may be fractional."""
    if not (isinstance(l, (int, np.integer)) and isinstance(g, (int, np.integer)) and isinstance(s, (int, np.integer))):
        raise ValueError("the walk's stop, target and step are whole ticks")
    if s <= 0 or l <= 0 or g <= 0:
        raise ValueError("the stop, the target and the lattice step are positive")
    c, xs, xf = _frac(c), _frac(x_stop), _frac(x_flat)
    if min(_frac(l), c - max(xs, xf)) <= 0:
        return None
    G = _frac(g) if g_cap is None else min(_frac(g), _frac(g_cap))
    if G <= 0:
        raise ValueError("a target cap is positive")
    return G, min(_frac(l), c - xs)


def _p_up(top: bool, bot: bool, s, rho_u, rho_d):
    """The chance a step goes up: one half on a plain step; at the last lattice point below the target (rho_u from
    it) s / (s + rho_u); at the last point above the floor-side barrier (rho_d from it) rho_d / (s + rho_d); at a point
    that is both, rho_d / (rho_u + rho_d) -- each a driftless move to its two neighbours (the barrier itself where it
    lies within a step)."""
    if top and bot:
        return rho_d / (rho_u + rho_d)
    if top:
        return s / (s + rho_u)
    if bot:
        return rho_d / (s + rho_d)
    return (Fraction(1, 2) if isinstance(s, Fraction) or isinstance(rho_d, Fraction) else 0.5)


def walk_law(G, L, s, n: int) -> dict[tuple[str, object], object]:
    """The exact law of the stopped walk's outcome: {(kind, value in ticks): probability}, kind "target" (+G), "stop"
    (-L) or "time" (the walk's value after n steps). The walk moves on the lattice of step s from the fill, one step a
    draw (`_p_up`): a plain step +s or -s at one half; **inside the last lattice step before a barrier** a driftless
    two-point race between the barrier and the lattice point one step back, so either barrier -- the floor side's L,
    and a target G made fractional by a profit level -- is reached exactly, and the gross expectation stays exactly
    zero (each step a martingale move; optional stopping at a bounded time). Fractions in, fractions out (the oracle);
    floats in, floats out (the exact program's, the simulation's own arithmetic)."""
    if n <= 0 or not L > 0 or not G > 0:
        raise ValueError("barriers and steps are positive")
    exact = isinstance(L, Fraction) and isinstance(G, Fraction)
    if exact:
        s = Fraction(s)
    else:
        s, L, G = float(s), float(L), float(G)
    one = Fraction(1) if exact else 1.0
    d, rho_d = _bottom(L, s)
    u, rho_u = _bottom(G, s)
    live = {0: one}
    done: dict[tuple[str, object], object] = {}

    def add(k, pr):
        done[k] = done.get(k, 0) + pr

    for _ in range(int(n)):
        nxt: dict[int, object] = {}
        for i, pr in live.items():
            top, bot = i == u, i == -d
            q = _p_up(top, bot, s, rho_u, rho_d)
            if top:
                add(("target", G), pr * q)
            else:
                nxt[i + 1] = nxt.get(i + 1, 0) + pr * q
            if bot:
                add(("stop", -L), pr * (one - q))
            else:
                nxt[i - 1] = nxt.get(i - 1, 0) + pr * (one - q)
        live = nxt
    for i, pr in live.items():
        add(("time", i * s), pr)
    return done


def walk_net(l: int, g: int, c_before, n: int, s: int = 1, entry=0, x_target=0, x_stop=0, x_flat=0, g_cap=None
             ) -> tuple[Fraction, Fraction, Fraction] | None:
    """The stopped walk's exact oracle from a cushion measured before the entry cost: (gross expectation, net
    expectation, the worst balance change), every exit's change clipped at the floor (-c_before) as the engine clips;
    None when the take at the fill fails."""
    e, xt, xs, xf = (_frac(v) for v in (entry, x_target, x_stop, x_flat))
    c0 = _frac(c_before)
    b = walk_barriers(l, g, c0 - e, xs, xf, s, g_cap)
    if b is None:
        return None
    G, L = b
    law = walk_law(G, L, Fraction(s), n)
    gross = sum(pr * v for (k, v), pr in law.items())
    net, worst = Fraction(0), None
    for (k, v), pr in law.items():
        cost = {"target": xt, "stop": xs, "time": xf}[k]
        ch = max(-e + v - cost, -c0)
        net += pr * ch
        worst = ch if worst is None else min(worst, ch)
    return gross, net, worst


def walk_outcome(us: Sequence[float], G, L, s) -> tuple[object, str]:
    """The stopped walk on the uniforms `us` (one a step, up where u < `_p_up`): (its value in ticks, its exit kind --
    "target", "stop" or "time")."""
    d, rho_d = _bottom(float(L), float(s))
    u_, rho_u = _bottom(float(G), float(s))
    i = 0
    for u in us:
        top, bot = i == u_, i == -d
        q = _p_up(top, bot, float(s), rho_u, rho_d)
        if u < q:
            if top:
                return float(G), "target"
            i += 1
        else:
            if bot:
                return -float(L), "stop"
            i -= 1
    return i * float(s), "time"


def _walk_lanes(U, i, kind, alive, u_, d, q_top, q_bot, q_both, n_steps):
    """Advance lanes by `n_steps` columns of U (in place on copies; returns the new i, kind, alive)."""
    for j in range(n_steps):
        u = U[:, j]
        top, bot = i == u_, i == -d
        q = np.where(top & bot, q_both, np.where(top, q_top, np.where(bot, q_bot, 0.5)))
        up = u < q
        hit_t = alive & up & top
        hit_b = alive & ~up & bot
        i = np.where(alive & up & ~top, i + 1, np.where(alive & ~up & ~bot, i - 1, i))
        kind = np.where(hit_t, 1, np.where(hit_b, -1, kind))
        alive = alive & ~(hit_t | hit_b)
        if not alive.any():
            break
    return i, kind, alive


def _ends_lanes(G, L, s, lanes):
    L = np.broadcast_to(np.asarray(L, float), (lanes,))
    G = np.broadcast_to(np.asarray(G, float), (lanes,))
    d = np.maximum(np.ceil(L / s - SNAP).astype(np.int64) - 1, 0)
    rho_d = L - d * s
    u_ = np.maximum(np.ceil(G / s - SNAP).astype(np.int64) - 1, 0)
    rho_u = G - u_ * s
    return G, L, u_, d, s / (s + rho_u), rho_d / (s + rho_d), rho_d / (rho_u + rho_d)


def walk_outcomes(U: np.ndarray, G, L: np.ndarray, s: int) -> tuple[np.ndarray, np.ndarray]:
    """`walk_outcome` over lanes (U one row a lane, one column a step; G and L each lane's barriers in ticks):
    (values in ticks, kinds as 1 target, -1 stop, 0 time)."""
    U = np.asarray(U, float)
    lanes, n = U.shape
    G, L, u_, d, qt, qb, qbb = _ends_lanes(G, L, float(s), lanes)
    i, kind, alive = _walk_lanes(U, np.zeros(lanes, np.int64), np.zeros(lanes, np.int64), np.ones(lanes, bool), u_, d,
                                 qt, qb, qbb, n)
    val = np.where(kind == -1, -L, np.where(kind == 1, G, i * float(s))).astype(float)
    return val, kind


def walk_run(read, lanes: int, G, L: np.ndarray, s: int, n: int, chunk: int) -> tuple[np.ndarray, np.ndarray]:
    """`walk_outcomes` read `chunk` steps at a time: `read(rows, first, count)` gives the uniforms of steps first ..
    first + count - 1 of the lanes `rows` (indices into 0 .. lanes - 1). Only lanes still walking are read, and the
    walk stops when every lane is absorbed: the same outcome on the same uniforms as reading all n at once (the
    generator is counter-based), at the cost of the steps actually walked."""
    G, L, u_, d, qt, qb, qbb = _ends_lanes(G, L, float(s), lanes)
    i = np.zeros(lanes, np.int64)
    kind = np.zeros(lanes, np.int64)
    alive = np.ones(lanes, bool)
    pos = 0
    while pos < n and alive.any():
        c = min(int(chunk), n - pos)
        rows = np.flatnonzero(alive)
        U = read(rows, pos, c)
        ii, kk, al = _walk_lanes(U, i[rows], kind[rows], alive[rows], u_[rows], d[rows], qt[rows], qb[rows],
                                 qbb[rows], c)
        i[rows], kind[rows], alive[rows] = ii, kk, al
        pos += c
    val = np.where(kind == -1, -L, np.where(kind == 1, G, i * float(s))).astype(float)
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
           "race_dollars", "walk_step", "walk_steps", "walk_barriers", "walk_law", "walk_net", "walk_outcome", "walk_outcomes", "walk_run",
           "worse_fill", "stress_cells"]
