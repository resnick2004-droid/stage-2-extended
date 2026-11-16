"""EXPLORATORY (D-668; program U's U5): the contract's value map -- what one won trade is worth over one lost trade in
every state of an account's life under P-14's and P-16's own state tables, weighted by where accounts spend their
days, and the campaign value of extra win probability spent in each place. A reading of the solved tables: no
campaign, no variant counted, nothing selected. The pieces here are pure (the leaf's terms, the backward re-run and its
Bellman identity, the forward occupancy, the state keys and bands, the records' day counts, the place values and the
bar); `scripts/u_value_map.py` drives them on D-667's $50K bound solves.

**The solver's outcome model (what a "win" and a "loss" are here).** The table (`propedge/campaign/state_policy.py`)
models one trade a session on stage one's binary process: at each rung (a stop the base's trades come at, with its
share of the trades) the action's dollar risk is realised as whole micros under the allowance, and the trade either
WINS -- its target at the action's R, rounded to the $50 grid; in the evaluation a win may instead close early at the
need (the pass) or at the day's consistency allowance, the solver's need-aware exit and consistency cap (D-306, D-313)
-- or LOSES its realised stake (cut to the room above the floor; a loss that reaches the floor ends the account, worth
0). The win's probability is p = (1 + e) / (1 + R) at the R's own edge (here each R's registered one-sided 0.05 bound,
`lb_by_rr`, the gate's bound arm, read through D-667's per-R classes), with the engine's race against the floor when
the risk exceeds the room: the race lowers p, it adds no third outcome. A day the R is not offered (the rung's
availability) is a day without a trade. **There are no intraday partial outcomes in the solver** -- no scratch, no
time exit, no partial fill: the shifted outcome distribution of the gate's bound arm enters only as each R's lower
win probability. So the value difference here is the solver's own binary one: the value after the leaf's win outcome
(its target, or the early exit the solver applies) less the value after its stop outcome.

**ΔV (`dv`), per state and day:** for the action the table takes in the state (`Solution.policy`), at each rung k with
a trade, V(win_k) - V(loss_k), each read at the NEXT session's value -- for a funded or paid account the value at the
close after the trade, the table's payout choice at that close included (`FundedDP._close_values`); for the
evaluation the next session's value, a pass worth the funded account's value over the days left less the activation
fee, a failure 0 -- averaged over the rungs by `w_k x A_k` (the rung's share times the share of its trades offering the
action's R), i.e. conditional on a trade being taken. `p_trade` = sum_k w_k A_k [a trade at rung k]: the probability
the leaf's trade is taken that session. The value derivative of the session to a uniform rise of p on that trade is
p_trade x dv (`leaf_terms`' `dvw`). `edge_per_dollar` = 1 / dv: the extra win probability at which the leaf's expected
continuation changes by one dollar (blank where no trade or dv <= 0). Values are the solver's objective: expected cash
within the horizon (payouts net of the split and the method's fee; fees as the table accrues them) less the slot rent
lambda* a live account-day.

**The occupancy:** a fresh evaluation forward under the table to its pass, failure or abandonment; a fresh funded
account forward over the solver's whole horizon (the table's cycle accounting, `state_policy_dp.cycle_rate`, as D-667
read it), its unpaid states to its first payout and its paid states after. A state's occupancy is the expected
number of live account-days it holds (a session on which the table abandons holds none, as the solver counts days).
Per state, the value, p_trade and dv shown are occupancy-weighted over the days the state is held (dv weighted by the
trades taken there); the leaf shown is the action holding most of the state's occupancy, with that share.

**The place values (D-668 (2)):** with the table held fixed, a rise of `dp` in the win probability of every trade of
a class C changes an attempt's value by dp x sum over (day, state) in C of occupancy x p_trade x dv to first order --
exactly, at a fixed table; by the envelope theorem a re-solved table gains the same to first order. Per trade
affected it is dp x the trade-weighted mean dv over C. The classes: (a) every trade, (b) the evaluation's trades, (c)
the funded account's opening trade (its first trade: the mass at the fresh state that has never traded -- every
other path leaves the fresh state, so this is a layer of the forward of its own), (d) the funded account's later
trades before its first payout, (e) the paid account's trades. Per attempt a funded class counts P(pass) times its
funded figure. Per year of a five-seat campaign: (forward basis) trades of the class an attempt x attempts a seat-year
(252 sessions over the slot-days an attempt holds, the Combine's plus P(pass) times the funded account's, as
`cycle_rate` counts them) x five seats; (records basis, beside) the class's trades a year in the registered
campaign's records (U2's re-run, 100 paths of 504 sessions at the bound arm).

**The bar (D-668 (3)):** a signal firing N times a year, spent in a place, needs extra win probability dp = target /
(uses x the place's dollars per trade per unit of p), the uses being N or, where the place offers fewer trades a year
than N, the place's trades a year (said in the row).
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

from propedge.campaign import state_policy as sp

DECISION = "D-668"
BASES = ("p14", "p16")
BASE_NAMES = {"p14": "P-14 (A3-BRK30-CB20, its 12.5- and 25-point rungs)",
              "p16": "P-16 (rc_s150_all, its 37.5-point stop)"}
PHASES = ("combine", "funded", "paid")
PHASE_NAMES = {"combine": "the evaluation (Combine)", "funded": "the funded account before its first payout",
               "paid": "the paid account (after its first payout)"}
#: D-668 (2)'s places, in its order
PLACES = ("a_every_trade", "b_evaluation", "c_funded_opening", "d_funded_later", "e_paid")
PLACE_PHASE = {"a_every_trade": "all", "b_evaluation": "combine", "c_funded_opening": "funded",
               "d_funded_later": "funded", "e_paid": "paid"}
PLACE_NAMES = {"a_every_trade": "(a) every trade", "b_evaluation": "(b) the evaluation's trades only",
               "c_funded_opening": "(c) the funded account's opening trade only",
               "d_funded_later": "(d) the funded account's later trades before its first payout",
               "e_paid": "(e) the paid account's trades"}
SINGLE_PLACES = PLACES[1:]
DP = 0.01                                  # one percentage point of win probability
FREQUENCIES = (12, 36, 52, 104, 250)       # D-668 (3)'s signal frequencies, a year
TARGETS = (500.0, 1000.0)                  # dollars a year added to a five-seat campaign
SEATS = 5
SESSIONS_PER_YEAR = 252.0
BASES_OF_YEAR = ("forward", "records")
TOL_BELLMAN = 1e-6


# ------------------------------------------------------------------------------------------------ the leaf's terms


def daily_of(dp: sp._DP, rules) -> float:
    """What a live account-day costs in the table's objective: the Combine's accrued subscription plus the rent; the
    funded account's rent."""
    if isinstance(dp, sp.CombineDP):
        return float(rules.subscription) / float(rules.billing_days) + float(dp.lam)
    return float(dp.lam)


def leaf_terms(dp: sp._DP, a: int, idx: np.ndarray, ext: np.ndarray, daily: float
               ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Action `a` at states `idx` against the values `ext` the day closes on: (its value, the solver's
    `_action_value` in the same order of operations; p_trade; dvw = sum_k w_k A_k [trade at k] (V(win_k) - V(loss_k))).
    A rung where the action takes no trade (no contract at its stop, a stake the grid rounds away, no trade or abandon)
    has its win and loss the same state, and counts in neither p_trade nor dvw."""
    idx = np.asarray(idx, np.intp)
    m = idx.shape[0]
    if a == dp.abandon_action:                                    # D-329: worth exactly 0, no trade
        return np.zeros(m), np.zeros(m), np.zeros(m)
    iw, il, p = dp.trans[a]
    A = None if dp.avail is None else dp.avail[a]
    val = np.full(m, -float(daily))
    pt = np.zeros(m)
    dvw = np.zeros(m)
    for k in range(dp.nR):
        jw, jl = iw[k][idx], il[k][idx]
        vw, vl = np.take(ext, jw), np.take(ext, jl)
        pk = p[k][idx]
        x = pk * vw + (1.0 - pk) * vl
        ak = 1.0
        if A is not None and A[k] < 1.0:                          # D-318: the R not offered today -- no trade
            ak = float(A[k])
            x = ak * x + (1.0 - ak) * np.take(ext, dp.stay[idx])
        val += dp.w[k] * x
        tr = (jw != jl).astype(float)
        pt += dp.w[k] * ak * tr
        dvw += dp.w[k] * ak * tr * (vw - vl)
    return val, pt, dvw


def chosen_values(dp: sp._DP, pol: np.ndarray, ext: np.ndarray, daily: float) -> np.ndarray:
    """Every live state's value under its chosen action (`leaf_terms`' value), 0 at a dead state: the right side of
    the Bellman identity."""
    out = np.zeros(dp.nS)
    live = np.flatnonzero(dp.alive)
    for a, pos in sp._groups(np.asarray(pol)[live]):
        s = live[pos]
        out[s] = leaf_terms(dp, int(a), s, ext, daily)[0]
    return out


def ext_of(dp: sp._DP, V: np.ndarray, *, pass_value: float | None = None) -> np.ndarray:
    """The values a day closes on, with the sentinels the solver appends: DEAD 0, PASS (the Combine's pass value at
    that close; unused by a funded table) and ABANDONED 0."""
    return np.concatenate([V, [0.0, 0.0 if pass_value is None else float(pass_value), 0.0]])


# ------------------------------------------------------------------------------------------------ the backward re-run


def backward(dp: sp._DP, sol: sp.Solution, rules, store, *, pass_value: Sequence[float] | None = None
             ) -> dict[str, Any]:
    """The table's own day loop run again (`CombineDP.solve` / `FundedDP.solve`, the same calls in the same order),
    each day's closing values kept in `store[t]` (an array or memmap of shape [T, nS + 3]); checked against the
    solution: the same action and payout choice in every state on every day, the same fresh value each day, and the
    Bellman identity -- each live state's value equals its chosen action's expected continuation (`chosen_values`) --
    to `TOL_BELLMAN` on every state and day. `value_over_bound_max`: the most a state's value exceeds its bound -- a
    funded state's the split times its cushion (with every edge at or below zero a game pays out no more than the room
    above a floor that never falls), an evaluation state's the best pass value (0 if none is positive); the caller
    applies it only where every edge is at or below zero. Returns the checks."""
    funded = isinstance(dp, sp.FundedDP)
    if not funded and pass_value is None:
        raise ValueError("the Combine's re-run needs its pass values")
    daily = daily_of(dp, rules)
    V = np.zeros(dp.nS)
    worst_bellman = 0.0
    pol_diff = pay_diff = 0
    fresh_diff = 0.0
    worst_bound = -np.inf
    split = float(rules.profit_split)
    dp._drop_plan()
    try:
        for t in range(dp.T - 1, -1, -1):
            if funded:
                Vc, pay = dp._close_values(V)
                pay_diff += int((pay != sol.payout[t]).sum())
                ext = ext_of(dp, Vc)
            else:
                ext = ext_of(dp, V, pass_value=pass_value[t])
            V, pol = dp._day_values(ext, daily)
            pol_diff += int((pol != sol.policy[t]).sum())
            fresh_diff = max(fresh_diff, abs(float(V[dp.fresh]) - float(sol.fresh_value[t])))
            store[t] = ext
            cv = chosen_values(dp, pol, ext, daily)
            worst_bellman = max(worst_bellman, float(np.max(np.abs(cv - V))))
            live = dp.alive
            if funded:
                worst_bound = max(worst_bound, float(np.max(V[live] - split * dp.cushion[live])))
            else:                                                 # no state is worth more than the best pass
                worst_bound = max(worst_bound, float(np.max(V[live])) - max(0.0, float(np.max(pass_value))))
    finally:
        dp._drop_plan()
    return {"policy_differs": pol_diff, "payout_differs": pay_diff, "fresh_value_max_diff": fresh_diff,
            "bellman_max_abs": worst_bellman, "value_over_bound_max": worst_bound}


# ------------------------------------------------------------------------------------------------ the forward


def forward(dp: sp._DP, sol: sp.Solution, rules, store) -> dict[str, Any]:
    """The fresh account forward under the table (the solver's `forward`, its pushes and payout step), the leaf's
    terms read each day at every state holding mass from the closing values in `store`. Returns per state: `occ`
    (expected live account-days), `vsum` (occupancy x value), `tsum` (occupancy x p_trade), `dsum` (occupancy x dvw),
    `neg` (trade mass where dv < 0), `vis` (occupancy by action, as the solver's visitation); and the forward's
    figures to check against the solver's: Combine -- pass, failure and abandonment by day, days; funded -- first
    payouts by day, cash, gross, payouts, the share paid and closed, days; and the opening trade's layer (funded):
    `open_trades` and `open_dsum`, the mass that had never traded times its p_trade and dvw."""
    funded = isinstance(dp, sp.FundedDP)
    daily = daily_of(dp, rules)
    nS, T = dp.nS, dp.T
    dist = np.zeros(nS)
    dist[dp.fresh] = 1.0
    occ, vsum, tsum, dsum, neg = (np.zeros(nS) for _ in range(5))
    vis = np.zeros((nS, len(dp.actions)))
    vis_push = np.zeros((nS, len(dp.actions)))
    days = 0.0
    by = {k: np.zeros(T) for k in ("pass", "fail", "abandon", "first")}
    cash = gross = n_pay = first = dead = 0.0
    untraded = 1.0 if funded else 0.0
    open_trades = open_dsum = 0.0
    min_dv = np.inf
    mbuf = np.zeros(nS)
    acc = dp._scatter_acc(nS + 3)[:nS]
    for t in range(T):
        alive = dist.sum()
        if alive < 1e-15:
            break
        ext = np.asarray(store[t])
        pol = sol.policy[t]
        held = np.flatnonzero(dist > 0)
        for a, pos in sp._groups(pol[held]):
            s = held[pos]
            m = dist[s]
            vis[s, int(a)] += m
            if int(a) == dp.abandon_action:                       # holds no slot that day; worth 0, no trade
                if funded and untraded > 0.0 and bool((s == dp.fresh).any()):
                    untraded = 0.0                                # the never-traded account is closed untraded
                continue
            v, pt, dvw = leaf_terms(dp, int(a), s, ext, daily)
            occ[s] += m
            vsum[s] += m * v
            tsum[s] += m * pt
            dsum[s] += m * dvw
            tr = pt > 0
            if tr.any():
                dv = dvw[tr] / pt[tr]
                min_dv = min(min_dv, float(dv.min()))
                neg[s[tr]] += np.where(dv < 0.0, m[tr] * pt[tr], 0.0)
            if funded and untraded > 0.0:
                hit = np.flatnonzero(s == dp.fresh)
                if len(hit):
                    j = int(hit[0])
                    if untraded > float(m[j]) * (1.0 + 1e-12) + 1e-300:
                        raise RuntimeError("the opening layer holds more mass than the fresh state")
                    open_trades += untraded * float(pt[j])
                    open_dsum += untraded * float(dvw[j])
                    untraded *= (1.0 - float(pt[j]))
        new = dp._push(dist, pol, vis_push)
        days += alive - new[dp.ABANDONED]
        by["fail"][t] = new[dp.DEAD]
        by["abandon"][t] = new[dp.ABANDONED]
        if not funded:
            by["pass"][t] = new[dp.PASS]
            dist = new[:nS]
            continue
        dist = new[:nS].copy()
        dead += new[dp.DEAD]
        ch = sol.payout[t]
        moved = np.zeros(nS)
        hold = np.flatnonzero(dist > 0)
        for j, pos in sp._groups(ch[hold]):                       # FundedDP.forward's payout step, as it runs
            if j == 0:
                continue
            idx, mask, net = dp.pay_idx[j - 1], dp.pay_mask[j - 1], dp.pay_net[j - 1]
            s = hold[pos]
            s = s[mask[s]]
            mbuf[s] = dist[s]
            tot = mbuf.sum()
            if tot <= 0:
                mbuf[s] = 0.0
                continue
            cash += tot * net
            gross += tot * float(dp.q_values[j - 1])
            n_pay += tot
            f1 = mbuf[:dp.nU].sum()
            first += f1
            by["first"][t] += f1
            sp._scatter_add(moved, acc, idx[s], mbuf[s])
            dist[s] = dist[s] - mbuf[s]
            mbuf[s] = 0.0
        dist = dist + moved
    out = {"occ": occ, "vsum": vsum, "tsum": tsum, "dsum": dsum, "neg": neg, "vis": vis, "days": float(days),
           "min_dv": float(min_dv) if np.isfinite(min_dv) else float("nan"), "unresolved": float(dist.sum()),
           "vis_matches_push": bool(np.array_equal(vis, vis_push))}
    d = np.arange(T) + 1.0
    if funded:
        out.update({"first_by_day": by["first"], "cash": cash, "gross": gross, "n_pay": n_pay, "p_paid": first,
                    "p_closed": dead, "open_trades": open_trades, "open_dsum": open_dsum,
                    "never_traded": untraded,
                    "days_to_first_payout": float((by["first"] * d).sum() / first) if first > 0 else float("nan")})
    else:
        passed = float(by["pass"].sum())
        out.update({"pass_by_day": by["pass"], "p_pass": passed, "p_fail": float(by["fail"].sum()),
                    "p_abandon": float(by["abandon"].sum()),
                    "days_to_pass": float((by["pass"] * d).sum() / passed) if passed > 0 else float("nan")})
    return out


def phase_masks(dp: sp._DP) -> dict[str, np.ndarray]:
    """The states of each phase the table holds: the Combine's, or the funded table's unpaid and paid states."""
    if isinstance(dp, sp.CombineDP):
        return {"combine": np.ones(dp.nS, bool)}
    return {"funded": ~dp.paid, "paid": dp.paid.copy()}


def phase_totals(fw: Mapping[str, Any], mask: np.ndarray) -> dict[str, float]:
    """A phase's sums: account-days, trades, the value derivative (sum of occupancy x dvw), the trade mass with dv < 0."""
    return {"days": float(fw["occ"][mask].sum()), "trades": float(fw["tsum"][mask].sum()),
            "dsum": float(fw["dsum"][mask].sum()), "neg": float(fw["neg"][mask].sum())}


# ------------------------------------------------------------------------------------------------ state keys and bands


def _g(x: float) -> str:
    return f"{float(x):g}"


def state_keys(dp: sp._DP, idx: Iterable[int]) -> list[str]:
    """A compact key per state: the evaluation's balance and floor (`B=..|F=..`); a funded account's balance, floor,
    winning days and request-day flag (`B=..|F=..|W=..|Q=..`); a paid account's balance, the balance after its last
    payout, winning days and flag (`B=..|ref=..|W=..|Q=..`). Balances relative to the start, in dollars."""
    out = []
    for s in idx:
        s = int(s)
        if isinstance(dp, sp.CombineDP):
            out.append(f"B={_g(dp.B[s])}|F={_g(dp.F[s])}")
        elif not dp.paid[s]:
            out.append(f"B={_g(dp.B[s])}|F={_g(dp.F[s])}|W={int(dp.wd[s])}|Q={int(dp.Q[s])}")
        else:
            out.append(f"B={_g(dp.B[s])}|ref={_g(dp.ref[s])}|W={int(dp.wd[s])}|Q={int(dp.Q[s])}")
    return out


def band_of(balance: float, cushion: float, phase: str, balance_band: float, cushion_band: float, mll: float) -> str:
    """The exported table's band key of a state (`state_policy.project`'s arithmetic): the balance band (for the funded
    account before its first payout the band holding the start is split, the states just above it keyed 0.01) and the
    cushion band, capped at the loss limit."""
    bb = float(np.floor(float(balance) / balance_band) * balance_band)
    if phase == "funded" and float(balance) > sp.EPS and bb == 0.0:
        bb = sp.START_SPLIT
    cb = float(min(np.floor(float(cushion) / cushion_band) * cushion_band, mll))
    return f"bb={_g(bb)}|cb={_g(cb)}"


def solver_bands(dp: sp._DP, fw: Mapping[str, Any], balance_band: float, cushion_band: float, mll: float
                 ) -> dict[tuple[str, str], float]:
    """The solver's occupancy summed by (phase, band key)."""
    out: Counter = Counter()
    for phase, mask in phase_masks(dp).items():
        idx = np.flatnonzero(mask & (fw["occ"] > 0))
        for s in idx:
            out[(phase, band_of(dp.B[s], dp.cushion[s], phase, balance_band, cushion_band, mll))] += float(fw["occ"][s])
    return dict(out)


# ------------------------------------------------------------------------------------------------ the records


def records_counts(account_days: Sequence[Mapping[str, Any]], trades: Sequence[Mapping[str, Any]],
                   funded: Sequence[Any], *, combine_floor0: float, funded_floor0: float, balance_band: float,
                   cushion_band: float, mll: float) -> dict[str, Counter]:
    """One recorded path's account-days by (phase, band key at the session's start) and by (phase, the leaf the
    engine's table chose that session), and its trades by place. The session's start state is the account's previous
    close as recorded (the fresh start -- balance 0, the floor at its starting value -- on its first session, a new
    Combine attempt's included); the phase of a funded account's session is 'paid' after the session of its first
    payout request (the engine's `first_payout_day`), else 'funded'. Trades: a Combine's are the evaluation's; a funded
    account's first is its opening, its others before or at its first request's session are 'later', the rest paid."""
    fmap = {int(f.index): f for f in funded}
    by_acct: dict[tuple, list] = {}
    for r in account_days:
        kind = str(r["kind"])
        key = (kind, int(r["index"]), int(r.get("attempt") or 0) if kind == "combine" else 0)
        by_acct.setdefault(key, []).append(r)
    days: Counter = Counter()
    leaves: Counter = Counter()
    pos_of: dict[int, dict[int, int]] = {}
    for (kind, index, _), rows in by_acct.items():
        rows = sorted(rows, key=lambda r: int(r["day"]))
        prev_b, prev_f = 0.0, (combine_floor0 if kind == "combine" else funded_floor0)
        if kind == "funded":
            pos_of[index] = {int(r["day"]): k for k, r in enumerate(rows)}
            f = fmap.get(index)
            fp = int(f.first_payout_day) if (f is not None and int(f.n_payouts) > 0) else None
        for k, r in enumerate(rows):
            if kind == "combine":
                phase = "combine"
            else:
                phase = "paid" if (fp is not None and k > fp) else "funded"
            days[(phase, band_of(prev_b, prev_b - prev_f, phase, balance_band, cushion_band, mll))] += 1
            leaves[(phase, str(r.get("regime")))] += 1
            prev_b, prev_f = float(r["balance"]), float(r["floor"])
    places: Counter = Counter()
    first_seen: set[int] = set()
    for r in sorted(trades, key=lambda r: (int(r["day"]), int(r.get("slot") or 0))):
        kind = str(r["kind"])
        if kind == "combine":
            places["b_evaluation"] += 1
            continue
        if kind != "funded":
            places["other"] += 1
            continue
        index = int(r["index"])
        if index not in first_seen:
            first_seen.add(index)
            places["c_funded_opening"] += 1
            continue
        f = fmap.get(index)
        k = pos_of.get(index, {}).get(int(r["day"]))
        if k is None:
            raise ValueError(f"funded account {index}'s trade on day {r['day']} has no day row")
        fp = int(f.first_payout_day) if (f is not None and int(f.n_payouts) > 0) else None
        places["e_paid" if (fp is not None and k > fp) else "d_funded_later"] += 1
    places["a_every_trade"] = sum(v for k, v in places.items() if k in SINGLE_PLACES)
    return {"days": days, "leaves": leaves, "places": places}


# ------------------------------------------------------------------------------------------------ the place values


def place_values(comb: Mapping[str, float], fund: Mapping[str, float], paid: Mapping[str, float],
                 opening: Mapping[str, float], p_pass: float, days_per_attempt: float, *,
                 records_per_year: Mapping[str, float] | None = None, seats: int = SEATS,
                 sessions_per_year: float = SESSIONS_PER_YEAR, dp: float = DP) -> dict[str, dict[str, float]]:
    """D-668 (2): per place, the trades an attempt holds (`trades_per_attempt`), the value derivative an attempt holds
    (`dsum_per_attempt`: d attempt value / d p), the mean dv per trade, the dollars per trade of `dp`, and, per year of
    a `seats`-seat campaign, the trades and dollars of `dp` on the forward basis and (given) the records basis.
    `comb`, `fund`, `paid`: `phase_totals` of the Combine, the funded account's unpaid and paid states (per account);
    `opening`: the opening layer's trades and dsum (per funded account)."""
    pp = float(p_pass)
    base = {
        "b_evaluation": (comb["trades"], comb["dsum"]),
        "c_funded_opening": (pp * opening["trades"], pp * opening["dsum"]),
        "d_funded_later": (pp * (fund["trades"] - opening["trades"]), pp * (fund["dsum"] - opening["dsum"])),
        "e_paid": (pp * paid["trades"], pp * paid["dsum"]),
    }
    base["a_every_trade"] = (sum(v[0] for v in base.values()), sum(v[1] for v in base.values()))
    attempts_a_year = float(seats) * float(sessions_per_year) / float(days_per_attempt)
    out: dict[str, dict[str, float]] = {}
    for place in PLACES:
        n, d = base[place]
        mean_dv = d / n if n > 0 else float("nan")
        row = {"trades_per_attempt": float(n), "dsum_per_attempt": float(d), "mean_dv": float(mean_dv),
               "dollars_per_trade": float(dp * mean_dv), "trades_per_year_forward": float(n * attempts_a_year),
               "dollars_per_year_forward": float(dp * d * attempts_a_year)}
        if records_per_year is not None:
            ny = float(records_per_year.get(place, 0.0))
            row["trades_per_year_records"] = ny
            row["dollars_per_year_records"] = float(dp * mean_dv * ny) if np.isfinite(mean_dv) else float("nan")
        out[place] = row
    return out


def best_place(pv: Mapping[str, Mapping[str, float]]) -> str:
    """The single place (b to e) whose trade is worth most per unit of win probability."""
    cands = [(float(pv[p]["mean_dv"]), p) for p in SINGLE_PLACES if np.isfinite(pv[p]["mean_dv"])]
    if not cands:
        raise ValueError("no place holds a trade")
    return max(cands)[1]


def bar_rows(pv: Mapping[str, Mapping[str, float]], basis: str, *, frequencies: Sequence[int] = FREQUENCIES,
             targets: Sequence[float] = TARGETS) -> list[dict[str, Any]]:
    """D-668 (3): for each frequency and target, the extra win probability a signal needs in the best place and in
    every trade: dp = target / (uses x mean dv), the uses N or, where the place offers fewer trades a year on this
    basis, that many (`capped`)."""
    best = best_place(pv)
    out = []
    for where, place in (("best_place", best), ("every_trade", "a_every_trade")):
        mean_dv = float(pv[place]["mean_dv"])
        supply = float(pv[place][f"trades_per_year_{basis}"])
        for n in frequencies:
            uses = min(float(n), supply)
            for tgt in targets:
                need = float(tgt) / (uses * mean_dv) if (uses > 0 and mean_dv > 0) else float("nan")
                out.append({"where": where, "place": place, "basis": basis, "frequency": int(n), "target": float(tgt),
                            "uses": uses, "capped": bool(supply < float(n)), "supply": supply, "mean_dv": mean_dv,
                            "extra_win_prob": need})
    return out


__all__ = ["DECISION", "BASES", "PHASES", "PLACES", "leaf_terms", "chosen_values", "ext_of", "backward", "forward",
           "phase_masks", "phase_totals", "state_keys", "band_of", "solver_bands", "records_counts", "place_values",
           "best_place", "bar_rows", "daily_of"]
