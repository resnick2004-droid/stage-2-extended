"""Q-185: the firm path's checks run in their own process (`extended/three_way_firm.py` imports the vendored engine):
prints one JSON line, one section per check, read by `tests/test_three_way_firm.py`. Synthetic schedules only: no bar,
no result, a few engine paths per check (light). Every seed is the tests' role seed (`three_way_seeds.issue("tests")`).

- `identity_binary` -- the firm path with the vendored binary draws (`lockstep.binary_draw_factories`) put through its
  router and slots equals the vendored path run with its own default draws, field for field, bit for bit;
- `identity_race` -- the firm path's race at no cost equals the vendored path run with the vendored `RandomDraw` fed
  the same uniforms (the scalar key path, `three_way_keys.uniforms`, not the vectorised one the firm path reads),
  field for field, bit for bit; its records are tied to the engine's own records, each computed independently (the
  first pass from each evaluation's purchase day and pass day, the first arrival from the day recorder's payouts in,
  the ordinal from the attempts and funded counts), and to the path's cash and arrivals;
- `zero_edge` -- under the race (three distinct exit costs, a rule's profit levels, races and walks of step 10,
  Topstep's rules): every trade's barrier, odds and booked value against this file's own arithmetic; the wins against
  the sum of the odds and the walks' target and stop exits against this file's own exact law of the stopped walk,
  each within four standard errors; the mean gross within four standard errors of zero;
- `rb1` -- the floor-bound lanes: a lane whose room is at most the costs fails at the fill (the room booked, the
  account breached and replaced, counted), on a race and on a walk whose flatten costs more than the room; a taken
  walk whose flatten passes the floor is clipped by the engine and fails;
- `pairing` -- the firm path against the toy path, lane for lane: on a deep account (every arm: base, twin, missed,
  worse fill, plant, as-walked; profit levels; distinct costs) the balances and key sets; on accounts that reach the
  floor (Topstep's MLL, the target out of reach) the balances, the ordinals and the fill failures; on RB-1's fixture
  the same; two starts read disjoint keys;
- `seats` -- two seats: two live accounts, the router deals each trade to one of them, both trade, no moment twice;
- `h4` -- H4's three outputs per lane against the engine's ledger and day recorder, on one seat and on two;
- `cost` -- the measured cost per lane-trade on Topstep's rules.
"""
from __future__ import annotations

import dataclasses
import json
import math
import sys
import time
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()

import numpy as np  # noqa: E402

from propedge.campaign import lockstep as LS  # noqa: E402
from propedge.contract.adapter import Policy, RandomDraw  # noqa: E402

from extended import three_way_firm as TF  # noqa: E402
from extended import three_way_journey as J  # noqa: E402
from extended import three_way_keys as K  # noqa: E402
from extended import three_way_seeds as S  # noqa: E402

SEED = S.issue("tests")
PART = S.PARTS["tests"]
BINARY_SEED = int(SEED)           # the tests' role seed, as the engine's path seed on the binary arm
COSTS = dict(entry_cost=1.5, x_target=1.0, x_stop=2.0, x_flat=3.5)      # three distinct exit costs (F8)


def schedule(name: str, n: int, *, g: int = 200, l: int = 100, tick: float = 5.0, costs: dict | None = None,
             per_day: int = 1, walk_every: int = 0, level_every: int = 0, level: float = 45.0, decision: int = 600,
             walked: float | None = None, step: int = 10, steps: int = 40) -> J.Schedule:
    """One trade a slot; every `walk_every`-th a time-limited trade (a walk of `steps` steps of `step` ticks), every
    `level_every`-th a rule's profit level (on a race, a profit-level exit; on a walk, its level)."""
    c = costs or {}
    out = []
    for s in range(n):
        for i in range(per_day):
            d = decision + 120 * i
            k = s * per_day + i
            walk = walk_every and k % walk_every == 0
            lev = level if (level_every and k % level_every == 1) else None
            reason = "flatten" if walk else ("profit_level" if lev is not None else "target")
            out.append(J.Trade(session=s, decision=d, entry=d + 5, exit=d + 60, exit_reason=reason, g=g, l=l,
                               tick_value=tick, walk_step=step if walk else 1, walk_n=steps if walk else 1,
                               walked_ticks=walked, level=lev, **c))
    return J.Schedule(name, tuple(out))


def same(a, b, where: str = "") -> list[str]:
    """Field-for-field, bit-for-bit differences between two engine records."""
    if dataclasses.is_dataclass(a) and not isinstance(a, type):
        if type(a) is not type(b):
            return [f"{where}: {type(a).__name__} against {type(b).__name__}"]
        out = []
        for f in dataclasses.fields(a):
            out += same(getattr(a, f.name), getattr(b, f.name), f"{where}.{f.name}")
        return out
    if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
        a, b = np.asarray(a), np.asarray(b)
        return [] if a.shape == b.shape and np.array_equal(a, b) else [f"{where}: arrays differ"]
    if isinstance(a, (tuple, list)):
        if len(a) != len(b):
            return [f"{where}: {len(a)} against {len(b)} items"]
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out += same(x, y, f"{where}[{i}]")
        return out
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a) != set(b):
            return [f"{where}: keys differ"]
        out = []
        for k in a:
            out += same(a[k], b[k], f"{where}[{k!r}]")
        return out
    if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
        return []
    return [] if a == b else [f"{where}: {a!r} against {b!r}"]


def run(sch, firm, plan, start, lanes, horizon, block, **kw):
    return TF.simulate(sch, firm, plan, start, range(lanes), horizon, seed=SEED, part=PART, history=0,
                       block_sessions=block, **kw)


# ------------------------------------------------------------------------------------------------ the identities


def identity_binary(firm: TF.Firm) -> dict:
    plan = TF.AccountPlan(trades_per_day=1, rr=2.0, risk=500.0)
    horizon, lanes = 126, 6
    sch = schedule("every session", horizon + 5)
    rec = run(sch, firm, plan, 0, lanes, horizon, horizon + 5, outcome="engine_binary", binary_seed=BINARY_SEED,
              keep_paths=True)
    kw = TF.engine_kwargs(firm, plan, horizon)
    theirs = LS.simulate_lockstep_path(plan.protocol(), seed=BINARY_SEED, **kw)
    diffs = []
    for j, p in enumerate(rec.paths):
        diffs += same(p, theirs, f"lane{j}")
    other = LS.simulate_lockstep_path(plan.protocol(), seed=TF.PATH_SEED, **kw)   # not vacuous: another seed differs
    cross = len(same(rec.paths[0], other, "cross"))
    return {"lanes": lanes, "horizon": horizon, "diffs": diffs[:5], "n_diffs": len(diffs), "cross_diffs": cross,
            "passes": sum(int(c.passed) for c in theirs.combines), "fails": sum(int(c.failed) for c in theirs.combines),
            "payouts": sum(len(f.payout_days) for f in theirs.funded)}


class KeyedRandomDraw:
    """The vendored `RandomDraw` at edge 0, its generator replaced by the coin field's uniform of the session's trade
    (the scalar key path)."""

    settlement = "race"

    def __init__(self, unit: K.Unit, sch: J.Schedule, start: int, start_day: int, policy):
        self.unit, self.sch, self.start, self.start_day = unit, sch, int(start), int(start_day)
        self.inner = RandomDraw(policy, 0.0, self, "truncate", "drift")
        self.u = None

    def random(self, n: int) -> np.ndarray:
        out, self.u = np.array([self.u]), None
        return out

    def __call__(self, n, day, slot, cushion):
        cal = self.start_day + 1 + int(day)
        trades = self.sch.by_session.get(self.start + cal - 1, ())
        if slot >= len(trades):
            return np.array([np.nan])
        self.u = float(K.uniforms(self.unit.coin_key(trades[slot].moment, K.RACE), 1)[0])
        return self.inner(n, day, slot, cushion)


def identity_race(firm: TF.Firm) -> dict:
    plan = TF.AccountPlan(trades_per_day=1)
    horizon, lanes, start = 126, 8, 3
    sch = schedule("race at no cost", horizon + 10, g=200, l=100, tick=5.0)
    pol = Policy(rr=2.0, risk=500.0)
    rec = run(sch, firm, plan, start, lanes, horizon, horizon + 10, keep_paths=True, record_days=True)
    kw = TF.engine_kwargs(firm, plan, horizon, record_days=True)
    diffs, cross = [], 0
    bad = {"rel": 0, "arrivals": 0, "first_pass": 0, "first_pay": 0, "accounts": 0}
    passes = pays = 0
    for j in range(lanes):
        unit = K.Unit(SEED, PART, 0, j, start)
        cf = lambda i, d, _u=unit: KeyedRandomDraw(_u, sch, start, d, pol)
        theirs = LS.simulate_lockstep_path(plan.protocol(), seed=TF.PATH_SEED, combine_draw_factory=cf,
                                           funded_draw_factory=cf, **kw)
        diffs += same(rec.paths[j], theirs, f"lane{j}")
        cross += len(same(rec.paths[(j + 1) % lanes], theirs, "cross"))      # not vacuous: another lane's differs
        cash = np.asarray(theirs.path.cash_series, float) - plan.initial_bankroll
        bad["rel"] += int(not np.array_equal(rec.rel[j], cash[:horizon + 1]))
        got = sum(c for _, c in rec.arrivals[j])
        bad["arrivals"] += int(abs(rec.rel[j][-1] - (got - theirs.path.total_fees)) > 1e-6)
        # the records against the engine's own, each computed independently of `records_of`
        fp = [c.purchase_day + 1 + c.pass_day for c in theirs.combines if c.passed]
        bad["first_pass"] += int(rec.first_pass[j] != (min(fp) if fp else -1))
        ins = [int(r["day"]) for r in theirs.campaign_days if float(r["payouts_in"]) > 0 and int(r["day"]) <= horizon]
        bad["first_pay"] += int(rec.first_pay[j] != (min(ins) if ins else -1))
        bad["accounts"] += int(rec.accounts[j] != theirs.path.attempts_started + theirs.path.accounts_funded - 1)
        passes += len(fp)
        pays += int(bool(ins))
    return {"lanes": lanes, "horizon": horizon, "diffs": diffs[:5], "n_diffs": len(diffs), "cross_diffs": cross,
            "bad": bad, "passes": passes, "lanes_paid": pays,
            "accounts_max": int(rec.accounts.max()), "first_pass_set": int((rec.first_pass > 0).sum())}


# ------------------------------------------------------------------------------------------------ zero edge


def walk_exact(G: Fraction, L: Fraction, s: int, n: int) -> tuple[Fraction, Fraction]:
    """This file's own exact law of R-10's stopped walk (the design note's, written here from its statement, not
    from `three_way_redraw`): a lattice of step s from 0; at the last lattice point below the target G (u s, rho_u =
    G - u s above it) a step goes to G with probability s / (s + rho_u), else one step down; at the last point above
    -L (-d s, rho_d = L - d s below it) a step goes to -L with probability s / (s + rho_d), else one step up; where
    one point is both, to G with probability rho_d / (rho_u + rho_d); elsewhere one step either way at one half.
    Returns (P(target), P(stop)) after at most n steps."""
    s = Fraction(s)
    u = max(math.ceil(G / s) - 1, 0)
    d = max(math.ceil(L / s) - 1, 0)
    ru, rd = G - u * s, L - d * s
    half = Fraction(1, 2)
    live, pt, ps = {0: Fraction(1)}, Fraction(0), Fraction(0)
    for _ in range(int(n)):
        nxt: dict[int, Fraction] = {}
        for i, pr in live.items():
            top, bot = i == u, i == -d
            if top and bot:
                up = rd / (ru + rd)
                pt += pr * up
                ps += pr * (1 - up)
                continue
            if top:
                up = s / (s + ru)
                pt += pr * up
                nxt[i - 1] = nxt.get(i - 1, 0) + pr * (1 - up)
            elif bot:
                down = s / (s + rd)
                ps += pr * down
                nxt[i + 1] = nxt.get(i + 1, 0) + pr * (1 - down)
            else:
                nxt[i + 1] = nxt.get(i + 1, 0) + pr * half
                nxt[i - 1] = nxt.get(i - 1, 0) + pr * half
        live = nxt
    return pt, ps


def zero_edge(firm: TF.Firm) -> dict:
    plan = TF.AccountPlan(trades_per_day=2)
    horizon, lanes = 63, 24
    sch = schedule("costs, levels, races and walks", horizon, g=60, l=40, tick=5.0, costs=COSTS, per_day=2,
                   walk_every=3, level_every=4, level=45.0)
    rec = run(sch, firm, plan, 0, lanes, horizon, horizon, log=True)
    by_moment = {t.moment: t for t in sch.trades}
    gross, kinds, bad = [], {}, 0
    wins = p_sum = p_var = 0.0
    wt = ws = 0
    exp_t = exp_s = var_t = var_s = 0.0
    memo: dict = {}
    for rows in rec.logs:
        for cal, slot, name, moment, room, froom, kind, L, p, G, g_, cost, out in rows:
            kinds[kind] = kinds.get(kind, 0) + 1
            if kind not in ("race", "walk"):
                continue
            t = by_moment[moment]
            tv = t.tick_value * t.contracts
            # this file's own as-placed target: a level is the net the trade must make, its costs included (m-3)
            G0 = float(t.g) if t.level is None else min(float(t.g), (t.level + t.entry_cost + t.x_target) / tv)
            L0 = min(t.l * tv, room - t.entry_cost - t.x_stop)
            bad += int(abs(L - L0) > 1e-9 or abs(G - G0) > 0)
            gross.append(g_)
            if kind == "race":
                p0 = L0 / (L0 + G0 * tv)
                win = g_ > 0
                bad += int(abs(p - p0) > 1e-12)
                bad += int(abs(g_ - (G0 * tv if win else -L0)) > 1e-9)
                bad += int(abs(out - (-t.entry_cost + (G0 * tv - t.x_target if win else -L0 - t.x_stop))) > 1e-9)
                wins += win
                p_sum += p0
                p_var += p0 * (1 - p0)
            else:
                ek = int(p)
                c0 = {1: t.x_target, -1: t.x_stop, 0: t.x_flat}[ek]
                bad += int(abs(out - (-t.entry_cost + g_ - c0)) > 1e-9)
                if ek == 1:
                    bad += int(abs(g_ - G0 * tv) > 1e-9)
                elif ek == -1:
                    bad += int(abs(g_ + L0) > 1e-9)
                else:
                    v = g_ / (t.walk_step * tv)
                    bad += int(abs(v - round(v)) > 1e-9 or not (-L0 < g_ < G0 * tv))
                key = (Fraction(G0), Fraction(L0 / tv).limit_denominator(10 ** 9), t.walk_step, t.walk_n)
                if key not in memo:
                    memo[key] = tuple(float(x) for x in walk_exact(*key))
                pt, ps = memo[key]
                wt += ek == 1
                ws += ek == -1
                exp_t += pt
                exp_s += ps
                var_t += pt * (1 - pt)
                var_s += ps * (1 - ps)
    g = np.asarray(gross)
    se = float(g.std(ddof=1) / math.sqrt(len(g)))
    return {"trades": int(len(g)), "mean_gross": float(g.mean()), "se": se, "z": float(g.mean() / se), "bad": bad,
            "kinds": kinds, "race_z": float((wins - p_sum) / math.sqrt(p_var)),
            "walk_target_z": float((wt - exp_t) / math.sqrt(var_t)), "walk_stop_z": float((ws - exp_s) / math.sqrt(var_s)),
            "walk_targets": int(wt), "walk_stops": int(ws), "walk_laws": len(memo)}


# ------------------------------------------------------------------------------------------------ RB-1


def _rb1_schedules(mll: float, tick: float) -> dict[str, J.Schedule]:
    """Session 0 risks all but the room the fixture needs at even odds, no cost. 'race': room $10 against a race of
    costs 6 + 6; 'walk': room $10 against a walk whose flatten costs $30 (the take fails on x_flat alone);
    'flatten': room $40, a taken walk (x_flat $30 < room) whose time exit can pass the floor."""
    def first(room: float) -> J.Trade:
        l0 = int(round((mll - room) / tick))
        return J.Trade(session=0, decision=600, entry=605, exit=650, exit_reason="target", g=l0, l=l0, tick_value=tick)

    return {
        "race": J.Schedule("rb1 race", (first(10.0), J.Trade(
            session=1, decision=600, entry=605, exit=650, exit_reason="target", g=4, l=40, tick_value=tick,
            entry_cost=6.0, x_target=6.0, x_stop=6.0))),
        "walk": J.Schedule("rb1 walk", (first(10.0), J.Trade(
            session=1, decision=600, entry=605, exit=650, exit_reason="flatten", g=40, l=2, tick_value=tick,
            x_flat=30.0, walk_step=1, walk_n=3))),
        "flatten": J.Schedule("rb1 flatten", (first(40.0), J.Trade(
            session=1, decision=600, entry=605, exit=650, exit_reason="flatten", g=40, l=10, tick_value=tick,
            x_flat=30.0, walk_step=1, walk_n=5))),
    }


def rb1(firm: TF.Firm) -> dict:
    plan = TF.AccountPlan(trades_per_day=1)
    horizon, lanes = 3, 64
    out = {}
    for name, sch in _rb1_schedules(float(firm.rules.mll), 5.0).items():
        rec = run(sch, firm, plan, 0, lanes, horizon, horizon, log=True, keep_paths=True, record_trades=True)
        bound = failed_fill = bad = clipped = 0
        for j, (rows, path) in enumerate(zip(rec.logs, rec.paths)):
            r1 = [r for r in rows if r[0] == 2]
            if not r1:
                continue
            cal, slot, acct, moment, room, froom, kind, L, p, G, g_, cost, booked_out = r1[0]
            booked = [t for t in path.trades if t["day"] == 2]
            c0 = path.combines[0]
            if name in ("race", "walk") and abs(room - 10.0) < 1e-9:
                bound += 1
                ok = (kind == "fill_fail" and len(booked) == 1 and abs(booked[0]["pnl"] + room) < 1e-9 and c0.failed
                      and c0.resolved_on == 2 and len(path.combines) == 2 and path.combines[1].purchase_day == 2
                      and rec.fill_failures[j] == 1 and rec.accounts[j] == 1)
                failed_fill += int(kind == "fill_fail")
                bad += int(not ok)
            elif name == "flatten" and abs(room - 40.0) < 1e-9:
                bound += 1
                if kind == "walk" and booked_out < -room - 1e-9:
                    clipped += 1
                    bad += int(not (len(booked) == 1 and abs(booked[0]["pnl"] + room) < 1e-9 and c0.failed
                                    and rec.fill_failures[j] == 0))
                bad += int(kind != "walk")
            else:
                bad += int(rec.fill_failures[j] != 0)
        out[name] = {"bound": bound, "fill_failures": failed_fill, "engine_clipped": clipped, "bad": bad,
                     "total_fill_failures": int(rec.fill_failures.sum())}
    return out


# ------------------------------------------------------------------------------------------------ pairing


def _toy_rules(firm: TF.Firm, mll: float) -> J.ToyRules:
    return J.ToyRules(combine_fee=float(firm.subscription), billing=int(firm.billing_days), target=1e9, mll=mll,
                      dll=None, activation_fee=float(firm.activation), funded_mll=mll, win_day=1e9, payout_days=1,
                      payout_share=0.5, payout_cap=1.0, split=1.0, payout_lag=1)


def _pair(sch, firm, toy_rules, plan, start, lanes, horizon, block, arm=J.ArmSpec()) -> dict:
    gt, gf = K.KeyGuard(), K.KeyGuard()
    toy = J.simulate(sch, toy_rules, start, range(lanes), horizon, seed=SEED, part=PART, history=0,
                     block_sessions=block, arm=arm, guard=gt)
    fp = run(sch, firm, plan, start, lanes, horizon, block, arm=arm, guard=gf)
    return {"max_balance_diff": float(np.max(np.abs(toy.balance - fp.balance))),
            "accounts_equal": bool(np.array_equal(toy.accounts, fp.accounts)),
            "fill_failures_equal": bool(np.array_equal(toy.fill_failures, fp.fill_failures)),
            "fill_failures": int(fp.fill_failures.sum()), "accounts": int(fp.accounts.sum()),
            "spread": float(np.std(fp.balance)), "keys_equal": gt.keys() == gf.keys(), "n_keys": len(gf.keys())}


def pairing(firm: TF.Firm) -> dict:
    plan = TF.AccountPlan(trades_per_day=2)
    deep = dataclasses.replace(firm, rules=dataclasses.replace(firm.rules, mll=1e9, profit_target=1e9),
                               name="TS, deep (a test fixture)")
    horizon, lanes, start = 42, 12, 2
    sch = schedule("pair", horizon + 10, g=60, l=40, tick=5.0, costs=COSTS, per_day=2, walk_every=3, level_every=4,
                   level=45.0, walked=7.0)
    arms = {"base": J.ArmSpec(), "twin": J.ArmSpec(twin=True), "missed": J.ArmSpec(missed_q=0.2),
            "worse": J.ArmSpec(worse_ticks=1), "plant": J.ArmSpec(plant_eps=0.1),
            "as_walked": J.ArmSpec(reading="as_walked")}
    out = {name: _pair(sch, deep, _toy_rules(firm, 1e9), plan, start, lanes, horizon, horizon + 10, arm)
           for name, arm in arms.items()}
    # the floor reached: Topstep's MLL, the target out of reach (no pass, so no funded leg or consistency rule reads)
    floor = dataclasses.replace(firm, rules=dataclasses.replace(firm.rules, profit_target=1e9),
                                name="TS, target out of reach (a test fixture)")
    fsch = schedule("floor", 64, g=60, l=100, tick=5.0, costs=dict(entry_cost=40.0, x_target=10.0, x_stop=60.0,
                                                                     x_flat=120.0),
                    per_day=2, walk_every=3, level_every=4, level=45.0)
    out["floor"] = _pair(fsch, floor, _toy_rules(firm, float(firm.rules.mll)), plan, 0, 24, 63, 64)
    one = TF.AccountPlan(trades_per_day=1)
    for name, rsch in _rb1_schedules(float(firm.rules.mll), 5.0).items():
        out[f"rb1_{name}"] = _pair(rsch, floor, _toy_rules(firm, float(firm.rules.mll)), one, 0, 32, 3, 3)
    g0, g1 = K.KeyGuard(), K.KeyGuard()
    for st, g in ((0, g0), (5, g1)):
        run(sch, deep, plan, st, 4, 21, horizon + 10, guard=g)
    out["starts_disjoint"] = not (g0.keys() & g1.keys())
    out["keys_carry_start"] = (all(K.key_start(k) in (0, None) for k in g0.keys())
                               and all(K.key_start(k) in (5, None) for k in g1.keys()))
    return out


# ------------------------------------------------------------------------------------------------ seats, cost


def seats(firm: TF.Firm) -> dict:
    plan = TF.AccountPlan(name="two seats", trades_per_day=2, max_total_accounts=2, max_concurrent_combines=2)
    horizon, lanes = 42, 8
    sch = schedule("two seats", horizon, g=60, l=40, tick=5.0, costs=COSTS, per_day=3)
    rec = run(sch, firm, plan, 0, lanes, horizon, horizon, log=True, keep_paths=True)
    two_day = both_traded = copied = 0
    for rows, path in zip(rec.logs, rec.paths):
        seen, by_day = set(), {}
        for r in rows:
            copied += int(r[3] in seen)
            seen.add(r[3])
            by_day.setdefault(r[0], set()).add(r[2])
        two_day += sum(1 for v in by_day.values() if len(v) >= 2)
        both_traded += int(len({r[2] for r in rows}) >= 2)
    return {"lanes": lanes, "days_with_two_accounts": two_day, "lanes_two_accounts_traded": both_traded,
            "copied": copied, "day0_combines": min(sum(1 for c in p.combines if c.purchase_day == 0)
                                                  for p in rec.paths)}


def h4(firm: TF.Firm) -> dict:
    """H4's three outputs per lane (`orders_max`, `accounts_max`, `taken_mean`) against the engine's own records,
    computed here independently: the trades of each calendar day from the engine's ledger, the accounts trading it
    from its day recorder; on one seat and on two."""
    out = {}
    for name, plan, per_day in (("one_seat", TF.AccountPlan(trades_per_day=2), 2),
                                ("two_seats", TF.AccountPlan(name="two seats", trades_per_day=2, max_total_accounts=2,
                                                             max_concurrent_combines=2), 3)):
        horizon, lanes = 42, 8
        sch = schedule(f"h4 {name}", horizon, g=60, l=40, tick=5.0, costs=COSTS, per_day=per_day, walk_every=3)
        rec = run(sch, firm, plan, 0, lanes, horizon, horizon, keep_paths=True, record_trades=True, record_days=True)
        bad = 0
        for j, path in enumerate(rec.paths):
            orders = [sum(1 for t in path.trades if int(t["day"]) == k) for k in range(1, horizon + 1)]
            accts = [sum(1 for r in path.account_days if int(r["day"]) == k) for k in range(1, horizon + 1)]
            bad += int(rec.orders_max[j] != max(orders) or rec.accounts_max[j] != max(accts)
                       or abs(rec.taken_mean[j] - sum(orders) / horizon) > 1e-12)
        out[name] = {"bad": bad, "orders_max": float(rec.orders_max.max()), "accounts_max": float(rec.accounts_max.max()),
                     "taken_mean": float(rec.taken_mean.mean()), "lanes": lanes}
    return out


def cost(firm: TF.Firm) -> dict:
    from extended import procmem

    plan = TF.AccountPlan(trades_per_day=2)
    horizon, lanes = 126, 16
    sch = schedule("cost", horizon, g=60, l=40, tick=5.0, costs=COSTS, per_day=2, walk_every=3)
    t0 = time.perf_counter()
    rec = run(sch, firm, plan, 0, lanes, horizon, horizon)
    dt = time.perf_counter() - t0
    offered = lanes * len(sch.window(0, horizon).trades)
    return {"lanes": lanes, "horizon": horizon, "lane_trades": offered, "seconds": dt,
            "us_per_lane_trade": 1e6 * dt / offered, "ms_per_lane_session": 1e3 * dt / (lanes * horizon),
            "peak_mb": procmem.working_set_mb(peak=True), "accounts_mean": float(rec.accounts.mean())}


SECTIONS = ("identity_binary", "identity_race", "zero_edge", "rb1", "pairing", "seats", "h4", "cost")


def main() -> None:
    firm = TF.topstep()
    which = sys.argv[1:] or list(SECTIONS)
    out = {"firm": firm.name, "source": firm.source, "choices": TF.AccountPlan().choices(firm)}
    for name in which:
        out[name] = globals()[name](firm)
    print(json.dumps(out, default=str))


if __name__ == "__main__":
    main()
