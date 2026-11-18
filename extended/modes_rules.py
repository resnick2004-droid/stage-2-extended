"""RD-05's step 0 (`prereg/RD-05_firm_modes.md` 7, 8, 11 item 1, 16; part of A-15): flip days from the rules alone
(part A), the sizing grid and the size that binds (part B, part E item 1), and the oracle count N of 9.6 -- exact
arithmetic on the record's terms (`extended.modes_terms`), drawing nothing, reading no bar, no trade, no result file.

**Part A (7).** `k_eval` -- the fewest winning sessions that meet every pass condition at once (the target; the
consistency share `c`, so `n >= ceil(1/c)`; the minimum days; within the lifespan), under the recorded semantics
(`extends`) and the other (`fails`); `further_days` -- item 2's raised target and further days after a first day X;
`k_funded` -- `k_F`, the sessions elapsed to the first eligible close when trading every session (2.6: a stated clock
translated by 2.6's rounding, the first trade at session 0, so a wait of `w` sessions makes `k_F = w + 1`), with the
fewest profitable days beside; `b_star` -- section 5's U-25 `b*` at each end, otherwise the smallest balance at which the
plan's own request reaches its largest value; `r_flip` with its cuts at the mode's start state; `implied_days` (N5);
`boundary_cells` (item 8) by the declared conditions, each with its lattice exactness beside (see `boundary_exact`);
`close_only` (item 9); `ceiling_cells` (item 10); the stated-fewest check (refusing, `StatedFewestMismatch`).

**Part B (8).** `size` -- the contracts for `r` at `s` in each mix (MNQ alone, NQ alone, mixed: as many minis as fit,
the rest micros, D-324), the binding constraint (ties named dollar risk, allowance, room, daily limit), D-212's
consistent risk and D-272's stand-aside (the registered rule's `stand_aside`, read), the cost share, the consistency
fit; every state of every mode-corner (`states`).

No rule value is typed here (17.2): every number comes from the terms.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any, Iterable

from extended import modes_terms as M

EPS = 1e-9
MIXES = ("MNQ", "NQ", "mixed")


class StatedFewestMismatch(RuntimeError):
    """7: a computed `k_E` differs from the firm's own statement of the fewest days -- step 0 stops."""


# ------------------------------------------------------------------------------------------------ part A


def _ceil_inv(c: float) -> int:
    return int(math.ceil(1.0 / float(c) - 1e-12))


def k_eval(t: M.EvalTerms, semantics: str | None = None) -> int | None:
    """7 item 1: the least `n` such that `n` winning sessions can meet every pass condition at once (None: no `n`
    within the lifespan). Under both semantics the equal-days bound is the same: `n` days of `T / n` each have the
    best day at most `c` of the total exactly when `n >= 1 / c`."""
    sem = t.consistency_semantics if semantics is None else semantics
    if sem not in ("extends", "fails"):
        raise ValueError(semantics)
    n = 1
    if t.consistency is not None:
        n = max(n, _ceil_inv(t.consistency))
    if t.min_days is not None:
        n = max(n, int(t.min_days))
    if t.lifespan is not None and n > int(t.lifespan):
        return None
    return n


def further_days(t: M.EvalTerms, X: float, semantics: str | None = None) -> dict[str, Any]:
    """7 item 2: after a first day of profit X -- under `extends` the raised target `max(T, X / c)` and the fewest
    further days, none larger than X (and the minimum days); under `fails`, whether the account survives (reading:
    a day above `c` of the base target fails it)."""
    sem = t.consistency_semantics if semantics is None else semantics
    T, c = float(t.target), t.consistency
    raised = T if c is None else max(T, float(X) / float(c))
    if sem == "fails" and c is not None and float(X) > float(c) * T + EPS:
        return {"X": float(X), "semantics": sem, "survives": False, "raised_target": None, "further_days": None}
    need = max(0.0, raised - float(X))
    m = int(math.ceil(need / float(X) - 1e-12)) if need > EPS else 0
    if t.min_days is not None:
        m = max(m, int(t.min_days) - 1)
    if t.lifespan is not None and 1 + m > int(t.lifespan):
        m_out: int | None = None
    else:
        m_out = m
    return {"X": float(X), "semantics": sem, "survives": True, "raised_target": raised, "further_days": m_out}


def first_day_levels(t: M.EvalTerms) -> list[float]:
    """7 item 2's X: `c T` (where the plan has a share), `0.75 T`, `T`, `1.5 T`."""
    out = []
    for x in M.declared("part_a.first_day"):
        if x == "c":
            if t.consistency is not None:
                out.append(float(t.consistency) * float(t.target))
        else:
            out.append(float(x) * float(t.target))
    return out


def _least_share_days(share: float, strict_above_buffer: bool) -> int:
    """The fewest equal winning days whose best day is at most `share` of the base: of the whole profit, `n >= 1/share`;
    of the profit above a buffer (U-18's strict end), `n share > 1` strictly (a finite day size exists)."""
    if strict_above_buffer:
        return int(math.floor(1.0 / float(share) + 1e-12)) + 1
    return _ceil_inv(share)


def k_funded(f: M.FundedTerms) -> dict[str, Any]:
    """7 item 3: `k_F` (sessions elapsed to the first eligible close when trading every session) and the fewest trading
    days with a profit beside it, per gate."""
    g = f.gate
    if g in ("ts_std", "labs_5wd", "lucid"):
        k, wins = int(f.winning_days), int(f.winning_days)
    elif g == "ts_con":
        k = wins = max(int(f.cons_min_days), _ceil_inv(f.cons_share))
    elif g == "labs_daily":
        k, wins = 1 + int(f.request == "labs_daily_strict"), 1           # U-22 strict: the next session's close
    elif g in ("mffu_buffer", "pro_clock"):
        k, wins = int(f.wait_first) + 1, 1
    elif g == "builder":
        share_days = _least_share_days(f.cycle_share, f.first_cycle_base == "above_buffer")
        wins = max(int(f.cycle_days), share_days)
        k = max(int(f.wait_first) + 1, wins)
    else:
        raise ValueError(g)
    return {"k_F": int(k), "fewest_profit_days": int(wins)}


def reference_cap() -> float:
    """`xfa_std_cap`, Stage 2's reference cap (U-25's `b*`)."""
    return float(M.s2("xfa_std_cap"))


def request_amount(f: M.FundedTerms, B: float, *, day_profit: float | None = None) -> float:
    """The coin's request at a balance `B` above start (9.2: the plan's own maximum, cut to every remaining-balance rule;
    U-25 at the corner's end where no cap is stated); 0 when nothing can be requested."""
    B = float(B)
    r = f.request
    if r == "engine" or r == "lucid":
        return max(0.0, min(float(f.frac) * B, float(f.cap)))
    if r in ("labs_daily_strict", "labs_daily_lenient"):
        above = max(0.0, B - float(f.buffer))
        if r == "labs_daily_strict" and day_profit is not None:
            above = min(above, max(0.0, float(day_profit)))
        return min(above, float(f.cap))
    if r == "builder":
        return max(0.0, min(float(f.cap), B - float(f.buffer)))
    withdrawable = max(0.0, B - float(f.buffer))
    if f.within_buffer_share is not None:                   # U-17's lenient end: a request inside the buffer
        withdrawable = max(withdrawable, float(f.within_buffer_share) * B)
    if r == "u25_strict":
        return max(0.0, min(float(f.frac) * B, reference_cap(), withdrawable))
    if r == "u25_lenient":
        return withdrawable
    raise ValueError(r)


def b_star(f: M.FundedTerms) -> dict[str, Any]:
    """7 item 4: the smallest balance above start at which the first request reaches its largest value -- U-25's `b*`
    at its end (the reference cap; the plan's own where lower and verified), elsewhere the plan's own cap. Exact on
    the piecewise-linear request; finite at every plan."""
    if f.request in ("u25_strict", "u25_lenient"):
        cap = reference_cap() if f.cap is None else min(reference_cap(), float(f.cap))
        label = "b* at the reference cap" if f.request == "u25_lenient" else ""
    else:
        cap = float(f.cap)
        label = ""
    cands = []
    if f.request in ("engine", "lucid"):
        cands = [cap / float(f.frac)]
    elif f.request in ("labs_daily_strict", "labs_daily_lenient", "builder"):
        cands = [float(f.buffer) + cap]
    elif f.request == "u25_strict":
        withdraw = [float(f.buffer) + cap]
        if f.within_buffer_share is not None:
            withdraw.append(cap / float(f.within_buffer_share))
        cands = [max(cap / float(f.frac), min(withdraw))]
    elif f.request == "u25_lenient":
        withdraw = [float(f.buffer) + cap]
        if f.within_buffer_share is not None:
            withdraw.append(cap / float(f.within_buffer_share))
        cands = [min(withdraw)]
    b = min(cands)
    if abs(request_amount(f, b, day_profit=b) - cap) > 1e-6 or request_amount(f, b - 1e-3, day_profit=b) >= cap - 1e-9:
        raise AssertionError(f"b* for {f.mode} {f.corner}: {b} is not the least balance reaching {cap}")
    if not math.isfinite(b):
        raise AssertionError(f"b* for {f.mode} {f.corner} is not finite")
    return {"b_star": float(b), "cap_reached": float(cap), "label": label}


def start_room(kind: str, t: Any) -> float:
    """The room above the floor at a mode's start state."""
    return float(t.mll) if kind == M.EVAL else -float(t.floor_start)


def r_flip(kind: str, t: Any, w: float) -> dict[str, Any]:
    """7 item 6: `r_flip` for one `w` and whether the room or the daily limit cuts it at the mode's start state."""
    if kind == M.EVAL:
        k = k_eval(t)
        base = float(t.target)
    else:
        k = k_funded(t)["k_F"]
        base = b_star(t)["b_star"]
    rf = base / (float(k) * float(w))
    room = start_room(kind, t)
    dll = getattr(t, "dll", None)
    cut = min(rf, room) if dll is None else min(rf, room, float(dll))
    by = "none"
    if cut < rf - EPS:
        by = "room" if (dll is None or room <= float(dll)) else "daily_limit"
    return {"k": int(k), "r_flip": float(rf), "cut_at_start": float(cut), "cut_by": by}


def ri_read_set(f: M.FundedTerms, w: float, size: float) -> bool:
    """9.1: `RI`'s funded cell is read only where every trade satisfies `(w + 1) x size <= D`."""
    return (float(w) + 1.0) * float(size) <= float(f.mll) + EPS


def implied_days(t: M.EvalTerms) -> dict[str, Any]:
    """7 item 7 (N5): whether `ceil(1/c)` is at least the plan's minimum days, so A-2 cannot bind on the coin."""
    share_days = None if t.consistency is None else _ceil_inv(t.consistency)
    md = t.min_days
    implied = md is None or (share_days is not None and share_days >= int(md)) or int(md) <= 1
    return {"share_days": share_days, "min_days": md, "implied": bool(implied)}


def boundary_declared(t: M.EvalTerms, w: float, r: float) -> bool:
    """7 item 8's declared conditions: a static floor checked intraday; the daily limit at least `r` (or none); `r`
    dividing the drawdown and `w r` dividing the target; no consistency raise possible (`w r <= c T`); no minimum days
    beyond the share's."""
    if t.floor != "static" or t.close_only:
        return False
    if t.dll is not None and float(t.dll) < float(r) - EPS:
        return False
    D, T = float(t.mll), float(t.target)

    def divides(a: float, b: float) -> bool:
        q = b / a
        return abs(q - round(q)) < 1e-9

    if not divides(float(r), D) or not divides(float(w) * float(r), T):
        return False
    if t.consistency is not None and float(w) * float(r) > float(t.consistency) * T + EPS:
        return False
    imp = implied_days(t)
    if not imp["implied"]:
        return False
    return True


def boundary_exact(t: M.EvalTerms, w: float, r: float) -> bool:
    """Whether every pass ends at exactly `T` on the cell's lattice: the balance moves in steps of `+w r` and `-r`
    from 0, so a balance below `T` that crosses it lands exactly on `T` for every reachable balance only when `w` is 1
    (then the balance is a multiple of `r` and `T - r` is the only balance a win carries across). A declared boundary
    cell at which this fails would breach 9.6's exact identity "every pass at exactly T" on a correct engine."""
    if not boundary_declared(t, w, r):
        return False
    return abs(float(w) - 1.0) < 1e-12


def close_only(m: M.ModeCorner, t: Any) -> bool:
    return bool(m.kind == M.EVAL and getattr(t, "close_only", False))


def ceiling_cells(f: M.FundedTerms) -> list[dict[str, Any]]:
    """7 item 10: the coin cells at which one trade's win can exceed a verified single-day ceiling (A-11)."""
    if f.ceiling is None:
        return []
    out = []
    for w in M.grid_w():
        for r in M.grid_r():
            for pol in ("steady", "flip"):
                size = float(r) if pol == "steady" else r_flip(M.FUNDED, f, w)["r_flip"]
                win = float(w) * size
                if win > float(f.ceiling) + EPS:
                    out.append({"w": w, "r": r, "policy": pol, "win": win, "ceiling": float(f.ceiling)})
    return out


def stated_check(t: M.EvalTerms) -> dict[str, Any] | None:
    """7's stated-fewest check: None where the record quotes no statement; otherwise the row, refusing on a
    difference (`StatedFewestMismatch`)."""
    if t.stated_fewest is None:
        return None
    k = k_eval(t)
    row = {"config": t.config, "corner": t.corner, "k_E": k, "stated": int(t.stated_fewest), "equal": k == t.stated_fewest}
    if not row["equal"]:
        raise StatedFewestMismatch(f"{t.config} {t.corner}: the computed k_E {k} differs from the firm's stated fewest "
                                   f"{t.stated_fewest} -- step 0 stops (7)")
    return row


# ------------------------------------------------------------------------------------------------ part B


@dataclass(frozen=True)
class State:
    """One sizing state of a mode-corner (8): its balance above start, the room and the daily limit, the allowance."""

    name: str
    balance: float
    room: float
    dll: float | None
    minis: int
    micros: int
    counting: str


def _floor_at(f: M.FundedTerms, b: float) -> float:
    if f.floor == "static" or f.lock is None:
        return float(f.floor_start)
    return min(float(f.lock), max(float(f.floor_start), float(b) - float(f.mll)))


def states(m: M.ModeCorner, t: Any) -> list[State]:
    """8's states: the evaluation's fresh state; each funded tier of the plan's ladder (its band's lower balance, the
    floor trailed to it at the close), or the flat allowance."""
    a = t.allowance
    if m.kind == M.EVAL:
        return [State("fresh", 0.0, float(t.mll), t.dll, int(a.minis), int(a.micros), a.counting)]
    mpm = M.micros_per_mini()
    if a.ladder is None:
        return [State("flat", 0.0, -float(t.floor_start), t.dll, int(a.minis), int(a.micros), a.counting)]
    out = []
    for i, (thr, minis) in enumerate(a.ladder):
        room = float(thr) - _floor_at(t, float(thr))
        out.append(State(f"tier{i}@{thr:g}", float(thr), room, t.dll, int(minis), int(minis) * mpm, a.counting))
    return out


def _fee(minis: int, micros: int, schedule: str) -> float:
    mnq, nq = M.round_turn(schedule)
    return int(minis) * nq + int(micros) * mnq


def size(st: State, r: float, s: int, mix: str, schedule: str, kind: str) -> dict[str, Any]:
    """8: the contracts for `r` at `s` ticks in `mix` at state `st`, the binding constraint, D-212's consistent risk,
    D-272's stand-aside, the cost share (the round turn and the entry and stop slippage over the realised risk)."""
    tv = M.tick_values()
    mpm = M.micros_per_mini()
    L = st.room if st.dll is None else min(st.room, float(st.dll))
    s = int(s)

    def n_of(per: float, allow: int) -> tuple[int, str]:
        cands = (("dollar_risk", int(math.floor(float(r) / (s * per) + 1e-9))), ("allowance", int(allow)),
                 ("room", int(math.floor(st.room / (s * per) + 1e-9))))
        if st.dll is not None:
            cands = cands + (("daily_limit", int(math.floor(float(st.dll) / (s * per) + 1e-9))),)
        n = min(c for _, c in cands)
        return max(0, n), next(name for name, c in cands if c == n)

    if mix == "MNQ":
        allow = st.micros if st.counting == "ratio" else st.micros
        n, bind = n_of(tv["MNQ"], allow)
        minis, micros = 0, n
    elif mix == "NQ":
        n, bind = n_of(tv["NQ"], st.minis)
        minis, micros = n, 0
    elif mix == "mixed":
        if st.counting == "ratio":
            n_me, bind = n_of(tv["MNQ"], st.micros)          # micro-equivalents at the 10:1 counting
            minis = min(n_me // mpm, st.minis)
            micros = n_me - minis * mpm
        else:                                   # U-26 strict: each contract counts one against the cap
            minis, bind = n_of(tv["NQ"], st.minis)
            left_r = float(r) - minis * s * tv["NQ"]
            left_L = L - minis * s * tv["NQ"]
            micros = max(0, min(int(math.floor(left_r / (s * tv["MNQ"]) + 1e-9)), st.minis - minis,
                                int(math.floor(left_L / (s * tv["MNQ"]) + 1e-9))))
    else:
        raise ValueError(mix)
    realised = minis * s * tv["NQ"] + micros * s * tv["MNQ"]
    sa = M.registered_stand_aside()["combine" if kind == M.EVAL else "funded"]
    share_ok = (minis + micros) >= 1 and realised >= float(sa[0]) * float(r) - EPS
    floor_ok = s >= int(sa[1])
    slip = M.fill_slippage()
    cost = _fee(minis, micros, schedule) + (slip["entry_slippage_ticks"] + slip["stop_slippage_ticks"]) * (
        minis * tv["NQ"] + micros * tv["MNQ"])
    return {"minis": int(minis), "micros": int(micros), "realised_risk": float(realised), "binding": bind,
            "consistent_risk": bool(share_ok), "cost_floor_ok": bool(floor_ok),
            "stood_aside": not (share_ok and floor_ok),
            "cost_share": (cost / realised) if realised > 0 else float("nan"), "cost": float(cost)}


def headroom_cap(st: State) -> dict[str, int]:
    """8: beside the allowance, Stage 2 D-117's headroom (`DEFAULT_HEADROOM_FRAC`, read) and the registered rule's own,
    of the allowance in micro-equivalents, rounded down."""
    sa = M.registered_stand_aside()
    mpm = M.micros_per_mini()
    me = st.micros if st.counting == "ratio" else st.minis * mpm
    return {"allowance_me": int(me), "d117_cap_me": int(math.floor(sa["d117_headroom"] * me + 1e-9)),
            "registered_cap_me": int(math.floor(sa["headroom"] * me + 1e-9))}


def consistency_fit(t: Any, kind: str, w: float, realised: float) -> bool | None:
    """8: whether one winning trade at `(w, r')` stays within the mode's consistency allowance (None: no share)."""
    if kind == M.EVAL:
        if t.consistency is None:
            return None
        return float(w) * float(realised) <= float(t.consistency) * float(t.target) + EPS
    return None


# ------------------------------------------------------------------------------------------------ the tables


def _schedule(t: Any) -> str:
    return t.commission


def sizeable_at_start(m: M.ModeCorner, t: Any, r: float, s: int) -> bool:
    """9.1: a costed cell runs only where part B finds it sizeable under D-212 at the mode's start state (mixed)."""
    st = states(m, t)[0]
    return not size(st, r, s, "mixed", _schedule(t), m.kind)["stood_aside"]


def coin_cells() -> list[dict[str, Any]]:
    """Every coin run of part C as step 0 fixes it (9.1, 16): mode-corner, `(w, r)`, policy, coin (gross or costed at a
    stop), and whether it runs -- shared gross cells, `RI`'s read set and the costed cells part B finds not sizeable
    are listed with the reason they do not run."""
    rows = []
    shared = set(M.shared_gross_corners())
    for m in M.MODE_CORNERS:
        t = M.mode_corner_terms(m)
        for wi, w in enumerate(M.grid_w()):
            for ri, r in enumerate(M.grid_r()):
                for pol in ("steady", "flip"):
                    why = ""
                    if m.index in shared:
                        why = "gross shared with the strict corner"
                    elif m.kind == M.FUNDED and t.floor == "intraday":
                        sz = r if pol == "steady" else r_flip(m.kind, t, w)["r_flip"]
                        if not ri_read_set(t, w, sz) or (pol == "flip" and not ri_read_set(t, w, r)):
                            why = "not read: a trade can be stopped by the floor its own peak raised"
                    rows.append({"index": m.index, "kind": m.kind, "mode": m.mode, "corner": m.corner, "w_index": wi,
                                 "r_index": ri, "w": w, "r": r, "policy": pol, "coin": "gross", "stop": None,
                                 "runs": why == "", "why": why})
                for s in M.declared("grid.s_costed"):
                    why = ""
                    if not sizeable_at_start(m, t, r, int(s)):
                        why = f"not sizeable at {s}"
                    elif m.kind == M.FUNDED and t.floor == "intraday" and not ri_read_set(t, w, r):
                        why = "not read: a trade can be stopped by the floor its own peak raised"
                    rows.append({"index": m.index, "kind": m.kind, "mode": m.mode, "corner": m.corner, "w_index": wi,
                                 "r_index": ri, "w": w, "r": r, "policy": "steady", "coin": "costed", "stop": int(s),
                                 "runs": why == "", "why": why})
    return rows


def boundary_cells() -> list[dict[str, Any]]:
    """7 item 8: the gross evaluation cells meeting the declared conditions, with their lattice exactness beside."""
    out = []
    for m in M.MODE_CORNERS:
        if m.kind != M.EVAL:
            continue
        t = M.mode_corner_terms(m)
        for w in M.grid_w():
            for r in M.grid_r():
                if boundary_declared(t, w, r):
                    out.append({"index": m.index, "mode": m.mode, "corner": m.corner, "w": w, "r": r,
                                "lifespan": t.lifespan, "exact_by_lattice": boundary_exact(t, w, r)})
    return out


def oracle_count(cells: Iterable[dict[str, Any]] | None = None, bounds: Iterable[dict[str, Any]] | None = None
                 ) -> dict[str, int]:
    """9.6 / 16: N, the statistical oracle checks of steps 1 and 2 -- a fairness check per coin run that runs, a pass
    ceiling per evaluation run outside the close-only corners and the boundary cells, a supremum per `TS-S`
    evaluation run, and the one reference check of 13.1 (b)."""
    cells = list(coin_cells() if cells is None else cells)
    bset = {(b["index"], b["w"], b["r"]) for b in (boundary_cells() if bounds is None else bounds)}
    close = set(M.close_only_corners())
    run = [c for c in cells if c["runs"]]
    fair = len(run)
    ceil = sum(1 for c in run if c["kind"] == M.EVAL and c["index"] not in close
               and not (c["coin"] == "gross" and (c["index"], c["w"], c["r"]) in bset))
    sup = sum(1 for c in run if c["kind"] == M.EVAL and c["mode"] == "TS")
    total = fair + ceil + sup + 1
    if total > int(M.declared("oracle.n_max")):
        raise AssertionError(f"N = {total} exceeds the declared maximum {M.declared('oracle.n_max')}")
    return {"fairness": fair, "pass_ceiling": ceil, "supremum": sup, "reference": 1, "N": total,
            "gross_runs": sum(1 for c in run if c["coin"] == "gross"),
            "costed_runs": sum(1 for c in run if c["coin"] == "costed")}


def part_a_rows() -> dict[str, list[dict[str, Any]]]:
    """7's sections: `flip_days`, `stated_check`, `flip_sizes`, `implied_days`, `boundary_cells`; the stated-fewest
    check refusing."""
    flip_days, stated, sizes, implied = [], [], [], []
    for m in M.MODE_CORNERS:
        t = M.mode_corner_terms(m)
        if m.kind == M.EVAL:
            for sem in ("extends", "fails"):
                lab = "" if sem == t.consistency_semantics else (
                    "if the rule failed instead" if sem == "fails" else "if it extended instead")
                flip_days.append({"index": m.index, "mode": m.mode, "corner": m.corner, "item": "k_E", "semantics": sem,
                                  "label": lab, "value": k_eval(t, sem)})
                for X in first_day_levels(t):
                    fd = further_days(t, X, sem)
                    flip_days.append({"index": m.index, "mode": m.mode, "corner": m.corner, "item": "after_first_day",
                                      "semantics": sem, "label": lab, "X": X, "survives": fd["survives"],
                                      "raised_target": fd["raised_target"], "value": fd["further_days"]})
            flip_days.append({"index": m.index, "mode": m.mode, "corner": m.corner, "item": "largest_day_at_base_target",
                              "semantics": t.consistency_semantics, "label": "",
                              "value": None if t.consistency is None else float(t.consistency) * float(t.target),
                              "single_day_cap": None, "daily_loss_limit": t.dll})
            row = stated_check(t)
            if row is not None:
                stated.append({"index": m.index, **row})
            implied.append({"index": m.index, "mode": m.mode, "corner": m.corner, **implied_days(t)})
        else:
            kf = k_funded(t)
            bs = b_star(t)
            flip_days.append({"index": m.index, "mode": m.mode, "corner": m.corner, "item": "k_F",
                              "semantics": "extends", "label": "", "value": kf["k_F"],
                              "fewest_profit_days": kf["fewest_profit_days"]})
            flip_days.append({"index": m.index, "mode": m.mode, "corner": m.corner, "item": "k_F", "semantics": "fails",
                              "label": "if the rule failed instead", "value": kf["k_F"],
                              "fewest_profit_days": kf["fewest_profit_days"]})
            flip_days.append({"index": m.index, "mode": m.mode, "corner": m.corner, "item": "b_star", "semantics": "",
                              "label": bs["label"], "value": bs["b_star"], "cap_reached": bs["cap_reached"]})
            flip_days.append({"index": m.index, "mode": m.mode, "corner": m.corner, "item": "single_day_bound",
                              "semantics": "", "label": "strict: no Live credit" if t.ceiling is not None else "",
                              "value": t.ceiling, "daily_loss_limit": t.dll})
        for w in M.grid_w():
            rf = r_flip(m.kind, t, w)
            row = {"index": m.index, "kind": m.kind, "mode": m.mode, "corner": m.corner, "w": w, **rf}
            if m.kind == M.FUNDED and t.floor == "intraday":
                row["ri_read_set"] = ri_read_set(t, w, rf["r_flip"])
            if m.kind == M.FUNDED and t.request == "u25_lenient":
                row["label"] = "b* at the reference cap"
            sizes.append(row)
    return {"flip_days": flip_days, "stated_check": stated, "flip_sizes": sizes, "implied_days": implied,
            "boundary_cells": boundary_cells()}


def part_b_rows() -> dict[str, list[dict[str, Any]]]:
    """8's sections: `sizing` (every state, stop, risk and mix, with the headroom caps beside) and `allowed` (every
    `(r, w, s, mix)` sizeable at a state, with the consistency fit); `size_binding` (11 item 1) is the binding column."""
    sizing, allowed, binding = [], [], []
    for m in M.MODE_CORNERS:
        t = M.mode_corner_terms(m)
        for st in states(m, t):
            hc = headroom_cap(st)
            for s in M.grid_s_part_b():
                for r in M.grid_r():
                    for mix in MIXES:
                        z = size(st, r, s, mix, _schedule(t), m.kind)
                        base = {"index": m.index, "kind": m.kind, "mode": m.mode, "corner": m.corner, "state": st.name,
                                "s": s, "r": r, "mix": mix}
                        sizing.append({**base, **z, **hc})
                        binding.append({**base, "binding": z["binding"]})
                        if not z["stood_aside"]:
                            for w in M.grid_w():
                                allowed.append({**base, "w": w, "realised_risk": z["realised_risk"],
                                                "consistency_fit": consistency_fit(t, m.kind, w, z["realised_risk"])})
    return {"sizing": sizing, "allowed": allowed, "size_binding": binding}


def terms_rows() -> list[dict[str, Any]]:
    """18's `terms` section: every mode-corner's terms as read, with the keys they came from and their statuses."""
    out = []
    for m in M.MODE_CORNERS:
        t = M.mode_corner_terms(m)
        d = asdict(t)
        keys = d.pop("keys")
        labels = d.pop("labels")
        allowance = d.pop("allowance")
        sts = []
        for k in keys:
            if k.startswith("lucid:"):
                sts.append(f"{k}=vendored")
            elif k in M.RECORD_KEYS or k.startswith(("labs.", "mffu.")) or k.endswith("_naf_50k"):
                sts.append(f"{k}={M.status(k)}")
            else:
                sts.append(f"{k}=stage2")
        out.append({"index": m.index, "kind": m.kind, "mode": m.mode, "corner": m.corner,
                    "two_ended": " ".join(m.terms), **{k: v for k, v in d.items()}, "allowance": str(allowance),
                    "labels": "; ".join(labels), "keys": "; ".join(sts)})
    return out


__all__ = ["StatedFewestMismatch", "MIXES", "k_eval", "further_days", "first_day_levels", "k_funded", "reference_cap",
           "request_amount", "b_star", "start_room", "r_flip", "ri_read_set", "implied_days", "boundary_declared",
           "boundary_exact", "close_only", "ceiling_cells", "stated_check", "State", "states", "size", "headroom_cap",
           "consistency_fit", "sizeable_at_start", "coin_cells", "boundary_cells", "oracle_count", "part_a_rows",
           "part_b_rows", "terms_rows"]
