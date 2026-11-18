"""RD-05's joins (`prereg/RD-05_firm_modes.md` 9.3-9.5, 4.7 item 5; E-200 N-3): what each coin run measures, the fee
columns, the two modes joined by exact arithmetic, the renewal to the first payout, and the coin's stacking exposure.

**One convention for an attempt unresolved at the horizon** (9.4): censored -- a terminal outcome of its own, neither a
pass nor a failure; its fees counted as paid up to the horizon; the censored share printed beside every fee and time
reading. A user's sequence of attempts ends at the first pass or the first censored attempt.

**Laws as defective arrays.** A duration law is an array `f[t]` on sessions `0..W` (W the renewal window, 2,520): the
probability that the attempt ends that way and occupies exactly `t` sessions (an attempt ending at session index `d`
occupies `d + 1`); its total is the probability of that ending. Convolutions are exact on the window; the mass beyond
it is printed as such.

**The renewal** (9.5): failures one after another (their number geometric in the failure probability), then the
terminal attempt -- a pass (then the funded account from the next session to its first payout) or a censored end; the
law of the sessions from the first purchase to the first payout is `R * f_pass * f_pay`, `R = sum_g f_fail^{*g}`.

**The stacking exposure on the coin** (4.7 item 5, N-3): the probability that the first payout request falls within
the 21 trading sessions ending on it (that day included) of the second-to-last floor breach -- the window state carries
floor breaches only (expiry and inactivity are failures but not breaches): `P_prefix x P(suffix <= 20)`, the prefix any
failures ending in a breach, the suffix the non-breach failures, one breach, the non-breach failures, the pass and the
funded sessions to the first payout.
"""
from __future__ import annotations

import math
from typing import Any, Sequence

import numpy as np

from extended import modes_terms as M

EPS = 1e-12


def window() -> int:
    return int(M.declared("renewal.window"))


def law(durations: np.ndarray, mask: np.ndarray, n: int, W: int | None = None) -> np.ndarray:
    """A defective duration law from per-account durations (sessions occupied) under `mask`, over `n` accounts."""
    W = window() if W is None else int(W)
    f = np.zeros(W + 1)
    d = np.asarray(durations)[np.asarray(mask, bool)].astype(int)
    d = d[(d >= 0) & (d <= W)]
    np.add.at(f, d, 1.0)
    return f / float(n)


def conv(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """The convolution of two laws truncated to the shorter window."""
    W = min(len(a), len(b)) - 1
    return np.convolve(a, b)[: W + 1]


def renewal(f_fail: np.ndarray) -> np.ndarray:
    """`R = sum_g f_fail^{*g}` (g = 0, 1, ...) on the window: `R[t] = 1{t = 0} + sum_{s>=1} f_fail[s] R[t - s]`."""
    if f_fail[0] > 0:
        raise ValueError("a failure occupies at least one session")
    W = len(f_fail) - 1
    R = np.zeros(W + 1)
    R[0] = 1.0
    for t in range(1, W + 1):
        R[t] = float(np.dot(f_fail[1: t + 1], R[t - 1:: -1][:t]))
    return R


def eval_laws(out: dict[str, Any], W: int | None = None) -> dict[str, Any]:
    """An evaluation run's laws: pass, failure (floor, lifespan, inactivity) and its breach part, and the censored
    share (sessions occupied: the ending session index plus one)."""
    n = len(out["passed"])
    occ = np.asarray(out["days"], int)
    fail = out["failed"] | out.get("expired", np.zeros(n, bool)) | out.get("inactive", np.zeros(n, bool))
    return {"n": n, "pass": law(np.asarray(out["pass_day"]) + 1, out["passed"], n, W),
            "fail": law(occ, fail, n, W), "breach": law(occ, out["failed"], n, W),
            "nonbreach": law(occ, fail & ~out["failed"], n, W),
            "p_pass": float(np.mean(out["passed"])), "p_fail": float(np.mean(fail)),
            "p_breach": float(np.mean(out["failed"])), "p_censored": float(np.mean(out["unresolved"]))}


def funded_laws(out: dict[str, Any], W: int | None = None) -> dict[str, Any]:
    n = len(out["first_payout_day"])
    paid = np.asarray(out["first_payout_day"]) >= 0
    return {"n": n, "pay": law(np.asarray(out["first_payout_day"]) + 1, paid, n, W), "p_paid": float(np.mean(paid))}


def first_payout_law(ev: dict[str, Any], fu: dict[str, Any], R: np.ndarray | None = None) -> dict[str, Any]:
    """9.5's renewal: the law of the sessions from the first purchase to the first payout, its mass beyond the window,
    and the censored masses (a censored attempt; a funded account unpaid at its ending or horizon)."""
    R = renewal(ev["fail"]) if R is None else R
    total = conv(conv(R, ev["pass"]), fu["pay"])
    q = ev["p_fail"]
    p_seq_pass = ev["p_pass"] / (1.0 - q) if q < 1 else 0.0
    p_payout = p_seq_pass * fu["p_paid"]
    return {"law": total, "p_payout": p_payout, "within_window": float(total.sum()),
            "beyond_window": max(0.0, p_payout - float(total.sum())),
            "censored_attempt": ev["p_censored"] / (1.0 - q) if q < 1 else 0.0,
            "censored_funded": p_seq_pass * (1.0 - fu["p_paid"])}


def stacking_exposure(ev: dict[str, Any], fu: dict[str, Any], Rn: np.ndarray | None = None) -> float:
    """4.7 item 5 on the coin (N-3): the probability that the journey's first payout request falls within the 21
    sessions ending on it of the second-to-last floor breach (two breaches in that window)."""
    win = int(M.declared("stacking.window"))
    q = ev["p_fail"]
    if q >= 1:
        return 0.0
    p_prefix = ev["p_breach"] / (1.0 - q)                    # any failures, then a breach (the second-to-last)
    Rn = renewal(ev["nonbreach"]) if Rn is None else Rn
    suffix = conv(conv(conv(conv(Rn, ev["breach"]), Rn), ev["pass"]), fu["pay"])
    return float(p_prefix * suffix[: win].sum())             # the suffix's sessions after it at most 20: lengths 0..20


def stacking_direct(ev_draw, fu_draw, n: int, rng: np.random.Generator) -> float:
    """T-9's direct simulation of the windowed renewal: `ev_draw(rng)` -> (outcome, sessions occupied) with outcome
    one of "pass", "breach", "nonbreach", "censored"; `fu_draw(rng)` -> sessions to the first payout or None."""
    win = int(M.declared("stacking.window"))
    hits = 0
    for _ in range(int(n)):
        t, breaches = 0, []
        while True:
            o, dur = ev_draw(rng)
            t += dur
            if o == "breach":
                breaches.append(t - 1)                       # the breach's session index
            if o in ("pass", "censored"):
                break
        if o != "pass":
            continue
        pay = fu_draw(rng)
        if pay is None:
            continue
        r = t + pay - 1                                      # the request's session index
        if sum(1 for b in breaches if r - b <= win - 1) >= int(M.declared("stacking.breaches")):
            hits += 1
    return hits / float(n)


def stacking_trigger(breach_sessions: Sequence[int], request_session: int) -> bool:
    """4.7 item 5 on records (part F): at least two floor breaches across the campaign's accounts fall in the 21
    trading sessions that end on the request's session, that day included."""
    win = int(M.declared("stacking.window"))
    r = int(request_session)
    return sum(1 for b in breach_sessions if 0 <= r - int(b) <= win - 1) >= int(M.declared("stacking.breaches"))


# ------------------------------------------------------------------------------------------------ 9.4 / 9.5


def eval_fees(out: dict[str, Any], t: M.EvalTerms, *, price: float | None = None) -> np.ndarray:
    """9.4: each attempt's evaluation fees -- a one-time price once (paid at the purchase, so also by a censored attempt);
    a subscription at every `billing` sessions alive (the engine's own `sub_fees` at its price, re-priced exactly by
    `price` -- TS-N's re-pricing of TS-S's runs)."""
    n = len(out["passed"])
    if t.subscription is not None:
        base = float(t.subscription)
        k = np.asarray(out["sub_fees"], float) / base
        return k * (base if price is None else float(price))
    p = t.one_time if price is None else price
    if p is None:
        raise ValueError(f"{t.config}'s price is unverified: read it on U-2's grid (`price`)")
    return np.full(n, float(p))


def mean_fees(mean_periods: float, t: M.EvalTerms, price: float | None = None) -> float:
    """9.4 from a run's mean subscription periods (TS; 1 for a one-time price): the mean fees per attempt at `price`
    (default the plan's own) -- exact, since every attempt pays its periods at one price."""
    if t.subscription is not None:
        return float(mean_periods) * (float(t.subscription) if price is None else float(price))
    p = t.one_time if price is None else price
    if p is None:
        raise ValueError(f"{t.config}'s price is unverified: read it on U-2's grid (`price`)")
    return float(p)


def periods(out: dict[str, Any], t: M.EvalTerms) -> np.ndarray:
    """The subscription periods each attempt paid (TS: `sub_fees / subscription`)."""
    return np.asarray(out["sub_fees"], float) / float(t.subscription)


def attempt_net(p_pass: float, mean_fees: float, funded_mean_net: float, activation: float) -> float:
    """9.5: minus the evaluation's fees plus the pass probability times (the funded mean net less the activation) --
    stage one's `attempt_ev` form."""
    return float(p_pass) * (float(funded_mean_net) - float(activation)) - float(mean_fees)


def attempt_cost(p_pass: float, mean_fees: float, activation: float) -> float:
    return float(mean_fees) + float(p_pass) * float(activation)


def journey(p_pass: float, p_censored: float, mean_fees: float, funded_mean_net: float, activation: float
            ) -> dict[str, float]:
    """9.4 / 9.5 over a user's sequence (Wald's identity; censored attempts terminal): the fees per user, the chance
    the sequence ends in a pass, the fees per pass, the net per funded journey."""
    term = float(p_pass) + float(p_censored)
    if term <= 0:
        return {"fees_per_user": math.inf, "p_ends_pass": 0.0, "fees_per_pass": math.inf, "net_journey": -math.inf,
                "censored_share": float(p_censored)}
    fees_user = float(mean_fees) / term
    p_end = float(p_pass) / term
    return {"fees_per_user": fees_user, "p_ends_pass": p_end,
            "fees_per_pass": fees_user / p_end if p_end > 0 else math.inf,
            "net_journey": -fees_user + p_end * (float(funded_mean_net) - float(activation)),
            "censored_share": float(p_censored) / term}


def under_purchase_limit(p_pass: float, p_censored: float, mean_fees: float, funded_mean_net: float,
                         activation: float, K: int) -> dict[str, float]:
    """9.5 under a purchase limit of `K` attempts (U-24): the chance of a pass within them and the net over them."""
    q = max(0.0, 1.0 - float(p_pass) - float(p_censored))
    attempts = sum(q ** j for j in range(int(K)))              # expected attempts bought (each needs the last failed)
    p_any = float(p_pass) * attempts
    return {"K": int(K), "p_pass_within": p_any, "attempts": attempts,
            "net": -float(mean_fees) * attempts + p_any * (float(funded_mean_net) - float(activation))}


def break_even_price(p_pass: float, funded_mean_net: float, activation: float, periods_mean: float = 1.0) -> float:
    """U-2: the evaluation price at which the per-attempt net is zero (a one-time price: `periods_mean` 1)."""
    return float(p_pass) * (float(funded_mean_net) - float(activation)) / float(periods_mean)


def eval_reading(out: dict[str, Any], t: M.EvalTerms) -> dict[str, Any]:
    """9.3's evaluation measures of one run (the large-days and last-gate readings are `modes_reading`'s)."""
    n = len(out["passed"])
    p = np.asarray(out["passed"], bool)
    x = int(p.sum())
    dp = np.asarray(out["pass_day"])[p] + 1
    pct = (lambda q: float(np.percentile(dp, q)) if x else float("nan"))
    p10, p50, p90 = M.declared("sessions.percentiles")
    from extended.modes_oracles import cp_lower, cp_upper

    return {"n": n, "p_pass": x / n, "p_pass_lo95": cp_lower(x, n, 0.025), "p_pass_hi95": cp_upper(x, n, 0.025),
            "p_floor": float(np.mean(out["failed"])), "p_expired": float(np.mean(out["expired"])),
            "p_inactive": float(np.mean(out["inactive"])), "p_censored": float(np.mean(out["unresolved"])),
            "sessions_mean": float(np.mean(dp)) if x else float("nan"), "sessions_p10": pct(p10), "sessions_p50": pct(p50),
            "sessions_p90": pct(p90), "p_raised": float(np.mean(np.asarray(out["raised"]) & p)),
            "flip_room_cuts": int(np.sum(out["room_cuts"])), "flip_trades": int(np.sum(out["flip_trades"])),
            "no_trade_sessions": int(np.sum(out["no_trade_sessions"]))}


def funded_reading(out: dict[str, Any], t: M.FundedTerms) -> dict[str, Any]:
    n = len(out["first_payout_day"])
    fp = np.asarray(out["first_payout_day"])
    paid = fp >= 0
    w1, w2 = M.declared("first_payout.within")
    return {"n": n, "p_any_payout": float(np.mean(paid)), f"p_first_within_{w1}": float(np.mean(paid & (fp < w1))),
            f"p_first_within_{w2}": float(np.mean(paid & (fp < w2))),
            "sessions_to_first_mean": float(np.mean(fp[paid] + 1)) if paid.any() else float("nan"),
            "p_censored": float(np.mean(out["alive"] & ~paid)), "mean_gross": float(np.mean(out["gross_paid"])),
            "mean_net": float(np.mean(out["cash"])), "mean_payouts": float(np.mean(out["n_payouts"])),
            "p_floor": float(np.mean(out["closed"])), "p_moved_live": float(np.mean(out["moved_live"])),
            "p_inactive": float(np.mean(out["inactive"])), "p_count_end": float(np.mean(out["count_end"])),
            "mean_forfeit": float(np.mean(out["forfeit"])), "activation": float(t.activation),
            "mean_gross_bound": float(-t.floor_start), "flip_room_cuts": int(np.sum(out["room_cuts"])),
            "flip_trades": int(np.sum(out["flip_trades"]))}


__all__ = ["window", "law", "conv", "renewal", "eval_laws", "funded_laws", "first_payout_law", "stacking_exposure",
           "stacking_direct", "stacking_trigger", "eval_fees", "periods", "attempt_net", "attempt_cost", "journey",
           "under_purchase_limit", "break_even_price", "eval_reading", "funded_reading"]
