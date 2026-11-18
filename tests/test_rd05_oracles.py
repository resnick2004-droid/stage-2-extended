"""RD-05's T-9 (`prereg/RD-05_firm_modes.md` 9.6, 9.5, 4.7 item 5; E-200 R-2, N-1, N-3): the oracles shown to work.

* each oracle fires on a hand-broken engine (a biased coin; a pass above the ceiling; an accounting error);
* **the false-alarm batteries at the null** on the `build_toys` seed: `K_NULL` batteries of `N_MAX` checks each
  (9.6's declared maximum), drawn exactly at the null -- Bernoulli pass indicators at the bound, fair trade sequences of
  the coin's law, and skewed mean-zero sequences shaped like the funded quantity (many small losses, a long right tail)
  -- the share of batteries with any breach at most 0.01 plus three binomial standard errors;
* **the power batteries** (R-2): `K_POWER` batteries, each with one check shifted by its type's declared shift -- the
  probability check at eight standard errors, the fairness checks at the smallest shift giving power 0.999 at the
  battery's N (at least eight; `SHIFT_FAIR`, `SHIFT_SKEW`, computed and written here before this test first ran) --
  the breach share at least the computed power less three binomial standard errors;
* Freedman's bound against a hand-worked case; 9.5's join equal to `propsim.attempt_ev` to 1e-9; the renewal's law
  with 9.4's censoring against a direct simulation of sequential attempts on toy laws; D-145's stacking trigger on
  hand-built records (two breaches inside the 21 sessions ending on the request day fire; one does not; two with one
  on the 22nd session back do not) and the coin's windowed renewal against a direct simulation.

A failure here is under the failure protocol, never cleared by a new seed (R-2).
"""
from __future__ import annotations

import math

import numpy as np
import pytest
from scipy import stats

from extended import modes_engine as E
from extended import modes_join as J
from extended import modes_oracles as O
from extended import modes_terms as M

TOYS = M.seed("build_toys")
N_MAX = int(M.declared("oracle.n_max"))
ALPHA = O.level(N_MAX)
#: R-2's declared battery counts and shifts (fixed in this source before T-9 first ran)
K_NULL = 200
K_POWER = 200
M_NULL = 50                 # trades a fair check in the null batteries
M_POWER = 2000              # trades a fair check in the power batteries
SHIFT_PROB = 8.0            # the probability checks: eight standard errors (power 0.99929 at n 1,000, p0 0.4)
SHIFT_FAIR = 8.64           # the smallest shift giving power 0.999 for M_POWER fair trades (span 1, p 1/2)
SHIFT_SKEW = 8.94           # the same for M_POWER skewed trades (q 0.05: -1, or +(1-q)/q; span 1/q)
POWER = 0.999
SKEW_Q = 0.05


def toy(*key: int) -> np.random.Generator:
    return np.random.default_rng([TOYS, 9, *key])


def _limit(share_bound: float, K: int, upper: bool) -> float:
    se = math.sqrt(share_bound * (1 - share_bound) / K)
    return share_bound + 3 * se if upper else share_bound - 3 * se


def test_freedman_hand_worked() -> None:
    a = 0.01
    L = math.log(2 / a)
    V, b = 100.0, 2.0
    want = L * b / 3 + math.sqrt((L * b / 3) ** 2 + 2 * L * V)
    got = O.freedman_bound(V, b, a)
    assert got == pytest.approx(want)
    assert 2 * math.exp(-got ** 2 / (2 * (V + b * got / 3))) == pytest.approx(a)


def test_each_oracle_fires_on_a_broken_engine() -> None:
    t = M.eval_terms("TS-S")
    # a biased coin: wins at p + 0.1 -- the fairness check breaches
    n, m = 2000, 200
    rng = toy(1)
    hit = rng.random((m, n)) < 0.6
    fair = {"S": float(np.sum((hit - 0.5) * 2.0)), "V": float(m * n * 0.25 * 4.0), "b": 2.0, "trades": m * n}
    assert O.fairness_breach(fair, ALPHA)
    # a pass rate above the ceiling
    x = int(0.5 * 50_000)
    assert O.pass_ceiling_breach(x, 50_000, t, ALPHA) and O.supremum_breach(x, 50_000, ALPHA)
    # an accounting error
    out = {"gross_sum": np.array([100.0]), "B": np.array([90.0]), "costs": np.array([0.0]), "trades": np.array([3])}
    assert O.accounting_problems(out, M.EVAL)
    out["B"] = np.array([100.0])
    assert not O.accounting_problems(out, M.EVAL)
    with pytest.raises(O.OracleBreach):
        O.oracle_rows(M.EVAL, {"fair": fair, "passed": np.zeros(10, bool), "gross_sum": np.zeros(10), "B": np.zeros(10),
                               "costs": np.zeros(10), "trades": np.zeros(10, int)}, t, N=N_MAX, mode="TS",
                      boundary=False, close_only=False)


def test_a_correct_engine_passes_its_oracles() -> None:
    m = next(x for x in M.MODE_CORNERS if x.mode == "TS" and x.kind == M.EVAL)
    spec = E.EvalSpec(M.mode_corner_terms(m), 1.0, 1500.0)
    out = E.run_eval(spec, 5000, toy(2))
    rows = O.oracle_rows(M.EVAL, out, spec.t, N=N_MAX, mode="TS", boundary=False, close_only=False)
    assert {r["check"] for r in rows} == {"fairness", "pass_ceiling", "supremum", "accounting"}
    f = next(x for x in M.MODE_CORNERS if x.mode == "RI" and x.kind == M.FUNDED and x.corner == M.STRICT)
    fs = E.FundedSpec(M.mode_corner_terms(f), 1.0, 500.0)
    fo = E.run_funded(fs, 3000, toy(3), toy(4))
    O.oracle_rows(M.FUNDED, fo, fs.t, N=N_MAX, mode="RI", boundary=False, close_only=False)


def _null_bernoulli(K: int, rng: np.random.Generator, n: int = 1000, p0: float = 0.4) -> float:
    any_breach = 0
    x_star = next(x for x in range(n + 1) if x > 0 and O.cp_lower(x, n, ALPHA) > p0)
    for _ in range(K):
        x = rng.binomial(n, p0, size=N_MAX)
        any_breach += int(np.any(x >= x_star))
    return any_breach / K


def _fair_S(rng: np.random.Generator, size: tuple[int, int], skew: bool) -> tuple[np.ndarray, float, float]:
    if skew:
        q = SKEW_Q
        I = rng.random(size) < q
        inc = np.where(I, (1 - q) / q, -1.0)
        return inc.sum(axis=1), size[1] * (1 - q) / q, 1.0 / q
    I = rng.random(size) < 0.5
    return (I - 0.5).sum(axis=1), size[1] * 0.25, 1.0


def _null_fair(K: int, rng: np.random.Generator, skew: bool) -> float:
    any_breach = 0
    for _ in range(K):
        S, V, b = _fair_S(rng, (N_MAX, M_NULL), skew)
        a = O.freedman_bound(V, b, ALPHA)
        any_breach += int(np.any(np.abs(S) > a))
    return any_breach / K


def test_false_alarm_batteries_at_the_null() -> None:
    lim = _limit(float(M.declared("oracle.level")), K_NULL, upper=True)
    assert _null_bernoulli(K_NULL, toy(10)) <= lim
    assert _null_fair(K_NULL, toy(11), skew=False) <= lim
    assert _null_fair(K_NULL, toy(12), skew=True) <= lim


def _shift_needed(V: float, b: float) -> float:
    return O.freedman_bound(V, b, ALPHA) / math.sqrt(V) + stats.norm.ppf(POWER)


def test_declared_shifts_are_the_smallest_giving_the_power() -> None:
    for shift, V, b in ((SHIFT_FAIR, M_POWER * 0.25, 1.0), (SHIFT_SKEW, M_POWER * (1 - SKEW_Q) / SKEW_Q, 1 / SKEW_Q)):
        need = _shift_needed(V, b)
        assert shift >= 8.0 and shift == pytest.approx(math.ceil(need * 100) / 100), (shift, need)
    n, p0 = 1000, 0.4
    x_star = next(x for x in range(n + 1) if x > 0 and O.cp_lower(x, n, ALPHA) > p0)
    p1 = p0 + SHIFT_PROB * math.sqrt(p0 * (1 - p0) / n)
    assert stats.binom.sf(x_star - 1, n, p1) > POWER


def test_power_batteries() -> None:
    n, p0 = 1000, 0.4
    rng = toy(20)
    x_star = next(x for x in range(n + 1) if x > 0 and O.cp_lower(x, n, ALPHA) > p0)
    p1 = p0 + SHIFT_PROB * math.sqrt(p0 * (1 - p0) / n)
    power_p = float(stats.binom.sf(x_star - 1, n, p1))
    hits = sum(int(rng.binomial(n, p1) >= x_star) for _ in range(K_POWER))
    assert hits / K_POWER >= _limit(power_p, K_POWER, upper=False)
    for skew, shift, key in ((False, SHIFT_FAIR, 21), (True, SHIFT_SKEW, 22)):
        r = toy(key)
        S, V, b = _fair_S(r, (K_POWER, M_POWER), skew)
        a = O.freedman_bound(V, b, ALPHA)
        sig = math.sqrt(V)
        power = float(stats.norm.sf(a / sig - shift) + stats.norm.cdf(-a / sig - shift))
        hits = int(np.sum(np.abs(S + shift * sig) > a))
        assert power >= POWER - 1e-4
        assert hits / K_POWER >= _limit(power, K_POWER, upper=False)


def test_join_equals_attempt_ev() -> None:
    vp = E._vp
    comb = {"p_pass": 0.3125, "mean_sub_fees": 73.5}
    xfa = {"mean_cash": 812.25}
    rules = vp.Rules()
    want = vp.attempt_ev(comb, xfa, rules)
    got = J.attempt_net(comb["p_pass"], comb["mean_sub_fees"], xfa["mean_cash"], rules.activation)
    assert abs(got - want["ev_per_attempt"]) < 1e-9
    assert abs(J.attempt_cost(comb["p_pass"], comb["mean_sub_fees"], rules.activation) - want["cost_per_attempt"]) < 1e-9


def _toy_laws(W: int = 400) -> tuple[dict, dict, dict]:
    """Toy attempt laws: pass, breach, non-breach failure, censored; funded payout times; sampled and as laws."""
    p_pass, p_breach, p_non, p_cens = 0.25, 0.5, 0.15, 0.10
    durs = {"pass": (3, 9), "breach": (1, 6), "nonbreach": (4, 12), "censored": (20, 20)}
    pay_p, pay_d = 0.6, (5, 15)
    ev = {"pass": np.zeros(W + 1), "breach": np.zeros(W + 1), "nonbreach": np.zeros(W + 1)}
    for k, p in (("pass", p_pass), ("breach", p_breach), ("nonbreach", p_non)):
        lo, hi = durs[k]
        ev[k][lo: hi + 1] = p / (hi - lo + 1)
    ev["fail"] = ev["breach"] + ev["nonbreach"]
    ev.update(p_pass=p_pass, p_fail=p_breach + p_non, p_breach=p_breach, p_censored=p_cens)
    fu = {"pay": np.zeros(W + 1), "p_paid": pay_p}
    fu["pay"][pay_d[0]: pay_d[1] + 1] = pay_p / (pay_d[1] - pay_d[0] + 1)
    samp = {"p": (p_pass, p_breach, p_non, p_cens), "durs": durs, "pay": (pay_p, pay_d)}
    return ev, fu, samp


def _draws(samp: dict):
    names = ("pass", "breach", "nonbreach", "censored")

    def ev_draw(rng):
        o = names[int(rng.choice(4, p=samp["p"]))]
        lo, hi = samp["durs"][o]
        return o, int(rng.integers(lo, hi + 1))

    def fu_draw(rng):
        p, (lo, hi) = samp["pay"]
        return int(rng.integers(lo, hi + 1)) if rng.random() < p else None

    return ev_draw, fu_draw


def test_renewal_against_direct_simulation() -> None:
    ev, fu, samp = _toy_laws()
    rn = J.first_payout_law(ev, fu)
    ev_draw, fu_draw = _draws(samp)
    rng = toy(30)
    n = 40_000
    times = []
    for _ in range(n):
        t = 0
        while True:
            o, d = ev_draw(rng)
            t += d
            if o in ("pass", "censored"):
                break
        if o != "pass":
            continue
        p = fu_draw(rng)
        if p is not None:
            times.append(t + p)
    times = np.array(times)
    p_pay = len(times) / n
    se = math.sqrt(p_pay * (1 - p_pay) / n)
    assert abs(p_pay - rn["p_payout"]) < 4 * se
    mean_law = float(np.sum(np.arange(len(rn["law"])) * rn["law"]) / rn["law"].sum())
    assert abs(float(np.mean(times)) - mean_law) < 4 * float(np.std(times)) / math.sqrt(len(times))
    assert rn["censored_attempt"] == pytest.approx(ev["p_censored"] / (1 - ev["p_fail"]))


def test_stacking_trigger_on_records() -> None:
    win = int(M.declared("stacking.window"))
    r = 100
    assert J.stacking_trigger([r - 3, r - 10], r)
    assert J.stacking_trigger([r, r - (win - 1)], r)                   # the request day and 20 back: inside
    assert not J.stacking_trigger([r - 5], r)                          # one breach
    assert not J.stacking_trigger([r - 5, r - win], r)                 # one on the 22nd session back
    assert not J.stacking_trigger([r + 1, r - 2], r)                   # after the request does not count


def test_stacking_windowed_renewal_against_direct_simulation() -> None:
    ev, fu, samp = _toy_laws()
    want = J.stacking_exposure(ev, fu)
    ev_draw, fu_draw = _draws(samp)
    n = 40_000
    got = J.stacking_direct(ev_draw, fu_draw, n, toy(31))
    se = math.sqrt(max(want * (1 - want), 1e-6) / n)
    assert abs(got - want) < 4 * se, (got, want)
    assert want > 0.01
