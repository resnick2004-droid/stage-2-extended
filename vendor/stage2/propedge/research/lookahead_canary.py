"""L3, the look-ahead canary (D-195): every bar after each decision is perturbed, and the decision's inputs and the
entries decided up to it must not change.

On synthetic sessions (`planted_effect.synthetic_session`: trending and driftless days, missing minutes, sessions
whose first bars are missing), for every decision time t of every session:

* **The perturbation.** Every bar after t is replaced -- a walk from a level a few percent away, new highs, lows and
  volumes -- with two things kept: which minutes have a bar (a missing bar changes what the rules count, not what they
  foresee), and the open of the first bar after t, which is the entry's fill by rule (P-04 §3: the entry fills at the
  next bar's open). Everything else that bar carries is perturbed.
* **What must not change** -- for the kit's core (`im2_core`): the decision's inputs at t (the close, sigma, VWAP, both
  bands, the side), computed by the core's own functions; and every entry `run_day` takes at a decision time up to t,
  its side, decision and fill slots, close, bands and VWAP (its walk, exit and lowest price come after t and may
  change). For the second implementation (`propedge/verification/im2x_core.py`, D-200): every signal it reports at a
  decision time up to t.
* **The canary itself is checked**: two planted look-aheads must be caught -- `run_day` deciding on the next minute's
  close (`planted_leak_close`), and VWAP taken over the whole session (`planted_leak_vwap`). A canary that cannot see
  a planted leak proves nothing.
"""
from __future__ import annotations

from typing import Any, Callable

import numpy as np

from propedge.data.qc_algorithms import im2_params
from propedge.outcomes import im2_core as core
from propedge.research.planted_effect import START, synthetic_session

SEED = 20261201
MARKETS = ("ES", "CL", "6E", "NG")
SESSIONS = 90                     # decided sessions per market, after the 14 that fill the lookback
LOOKBACK = 14


def perturb_after(s: tuple, t: int, rng: np.random.Generator, tick: float) -> tuple:
    """A copy of session `s` with every bar after slot t replaced (see the module docstring); minutes without a bar
    stay without one and the next bar's open (the fill) is kept."""
    o, h, l, c, v = (list(x) for x in s)
    after = [j for j in range(t + 1, len(o)) if o[j] is not None]
    if not after:
        return o, h, l, c, v
    fill = after[0]
    base = (c[t] if c[t] is not None else o[fill]) * (1.0 + float(rng.choice([-1, 1])) * float(rng.uniform(0.02, 0.05)))
    px = round(base / tick)
    step = max(1, int(round(abs(base) * 5e-4 / tick)))
    for j in after:
        op = round(o[j] / tick) if j == fill else px
        px = op + int(rng.integers(-3 * step, 3 * step + 1))
        o[j] = op * tick
        c[j] = px * tick
        h[j] = (max(op, px) + int(rng.integers(0, 2 * step))) * tick
        l[j] = (min(op, px) - int(rng.integers(0, 2 * step))) * tick
        v[j] = float(rng.integers(1, 2000))
    return o, h, l, c, v


def core_inputs(s: tuple, pc: float, profiles: list, P: dict, t: int, *, vwap_fn: Callable = core.vwap_series) -> tuple:
    """The decision's inputs at slot t by the core's own functions: ('mis',) with no bar, ('nbd',) with no sigma or
    VWAP, else (close, sigma, VWAP, upper band, lower band, side)."""
    o, h, l, c, v = s
    if o[t] is None:
        return ("mis",)
    sig, vw = core.sigma_at(profiles[-P["lookback"]:], t), vwap_fn(h, l, c, v)[t]
    if sig is None or vw is None:
        return ("nbd",)
    ref = core.session_open(o)
    ub, lb = max(ref, pc) * (1.0 + P["mult"] * sig), min(ref, pc) * (1.0 - P["mult"] * sig)
    side = 1 if (c[t] > ub and c[t] > vw) else (-1 if (c[t] < lb and c[t] < vw) else 0)
    return (c[t], sig, vw, ub, lb, side)


def _full_session_vwap(h, l, c, v):
    """A planted leak: every slot's VWAP is the whole session's."""
    num = sum((h[j] + l[j] + c[j]) / 3.0 * v[j] for j in range(len(c)) if c[j] is not None and v[j])
    den = sum(v[j] for j in range(len(c)) if c[j] is not None and v[j])
    return [num / den if den else None] * len(c)


def _next_close(s: tuple) -> tuple:
    """A planted leak: each bar's close replaced by the next bar's (the decision sees one minute ahead)."""
    o, h, l, c, v = s
    nxt = [next((c[k] for k in range(j + 1, len(c)) if c[k] is not None), c[j]) if c[j] is not None else None
           for j in range(len(c))]
    hh = [None if x is None else max(x, y, z) for x, y, z in zip(h, nxt, o)]
    ll = [None if x is None else min(x, y, z) for x, y, z in zip(l, nxt, o)]
    return o, hh, ll, nxt, v


def _entries_up_to(res: dict, t: int) -> list[tuple]:
    return [(e["d"], e["t"], e["j0"], e["cl"], e["ub"], e["lb"], e["vw"]) for e in res["entries"] if e["t"] <= t]


def run_canary(market: str, *, seed: int = SEED, sessions: int = SESSIONS) -> list[dict[str, Any]]:
    """One row per implementation checked on `market` (see the module docstring): decisions checked, those whose
    inputs or prior entries changed, and whether the row passed (no change for the implementations; at least one
    change caught for each planted leak)."""
    from propedge.verification import im2x_core as x

    q = im2_params(market)
    P, F, tick = q["p"], q["fills"], q["tick"]
    xp = {"open": q["open_min"], "close": q["close_min"], "lookback": P["lookback"], "multiplier": P["mult"],
          "decision_every": 30, "decision_margin": 30, "min_coverage": q["min_cov"]}
    rng = np.random.default_rng(seed + MARKETS.index(market))
    kinds = ("im2_core", "im2x_core", "planted_leak_close", "planted_leak_vwap")
    stats = {k: {"decisions": 0, "with_entry": 0, "changed": 0} for k in kinds}

    def bars(z):
        return [(q["open_min"] + i + 1, z[0][i], z[1][i], z[2][i], z[3][i], z[4][i]) for i in range(len(z[0]))
                if z[0][i] is not None]

    store, pc = [], None
    for k in range(LOOKBACK + sessions):
        kind = k % 6            # three trending days, a gap at the open, many holes, a driftless day
        s = synthetic_session(market, rng, drift=(0.4 if kind in (0, 1, 2) else 0.0),
                              holes=0.25 if kind == 4 else 0.01, gap_start=P["times"][0] + 1 if kind == 3 else 0,
                              level=START[market] * (1 + float(rng.normal(0, 0.01))))
        if len(store) >= LOOKBACK and pc is not None:
            profiles = [core.move_profile(p[0], p[3]) for p in store[-LOOKBACK:]]
            base = core.run_day(*s, pc, profiles, P, F, q["p_ref"])
            leak_base = core.run_day(*_next_close(s), pc, profiles, P, F, q["p_ref"])
            xs_base = x.evaluate_session(bars(s), pc, [bars(p) for p in store[-LOOKBACK:]], xp)
            for t in P["times"]:
                z = perturb_after(s, t, rng, tick)
                got = core.run_day(*z, pc, profiles, P, F, q["p_ref"])
                same = (core_inputs(s, pc, profiles, P, t) == core_inputs(z, pc, profiles, P, t)
                        and _entries_up_to(base, t) == _entries_up_to(got, t))
                stats["im2_core"]["decisions"] += 1
                stats["im2_core"]["with_entry"] += any(e["t"] == t for e in base["entries"])
                stats["im2_core"]["changed"] += not same
                tm = q["open_min"] + t + 1
                xs = x.evaluate_session(bars(z), pc, [bars(p) for p in store[-LOOKBACK:]], xp)
                stats["im2x_core"]["decisions"] += 1
                stats["im2x_core"]["changed"] += ([g for g in xs_base["signals"] if g[0] <= tm]
                                                  != [g for g in xs["signals"] if g[0] <= tm])
                leak = core.run_day(*_next_close(z), pc, profiles, P, F, q["p_ref"])
                stats["planted_leak_close"]["decisions"] += 1
                stats["planted_leak_close"]["changed"] += _entries_up_to(leak_base, t) != _entries_up_to(leak, t)
                stats["planted_leak_vwap"]["decisions"] += 1
                stats["planted_leak_vwap"]["changed"] += (core_inputs(s, pc, profiles, P, t, vwap_fn=_full_session_vwap)
                                                          != core_inputs(z, pc, profiles, P, t,
                                                                         vwap_fn=_full_session_vwap))
        o, c = s[0], s[3]
        if o[-1] is not None and core.complete(o, len(o) - 1, q["min_cov"]):
            store.append(s)
        pc = c[-1]
    rows = []
    for k in kinds:
        leak = k.startswith("planted")
        st = stats[k]
        rows.append({"market": market, "implementation": k, "expected": "caught" if leak else "no change",
                     "decisions": st["decisions"],
                     "decisions_with_entry": st["with_entry"] if k == "im2_core" else None,
                     "changed": st["changed"], "passed": bool(st["changed"] > 0 if leak else st["changed"] == 0)})
    return rows


__all__ = ["SEED", "MARKETS", "perturb_after", "core_inputs", "run_canary"]
