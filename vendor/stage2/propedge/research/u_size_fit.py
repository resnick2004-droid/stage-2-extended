"""EXPLORATORY (D-666; program U's U4): the account-size fit read -- each Topstep account size's evaluation and funded
contract solved by the base designs' own state-table solver, before any campaign. No campaign, no variant counted,
nothing selected; the pieces here are pure (rules, sizing, menus, rungs, the per-R outcome model, the bounds, the
readings and the rule) and `scripts/u_size_fit.py` drives them.

**The sizes (D-623, D-645):** `rules_for_size` builds the engine's `Rules` for $50K, $100K or $150K through
`rules_for_method('aeropay', **overrides)` -- the overrides are that size's verified rows of `config/rules.yaml` (the
profit target, the loss limit and the funded account's starting limit, the Standard and Consistency caps, the
subscription, reset and activation fees), read through the ledger's verified-status gate; every other field (the
consistency fraction, the winning days and their minimum, the payout minimum and share, the split, the billing days,
the locks) is single-valued and stays the 50K row's (D-666 (5)). At $50K no override is passed, so the rules are the
base's exactly. **The lock:** a larger funded account's lock balance is stated on no page (D-623); the solver's 1:1
trail (the floor starting at minus the loss limit and locking at the start, `FundedDP`'s own model) is applied and every
larger-size row carries `lock_assumed_1to1`.

**The sizing and allowances:** `sizing_for_size` is the gate's sizing rule's ledger part (`SizingRule.from_ledger`, the
current tier at FV3-C's declared headroom of 1.0, D-289's full allowance) with `dataclasses.replace` setting that size's
Combine limit (`combine_position_size_limit<_size>` minis, ten micros each) and its funded ladder
(`ScalingLadder.parse(funded_scaling_plan<_size>)`); `rungs_for_size` puts the same allowances on the table's `Rungs`
(`dataclasses.replace`), the base's stops, shares, availability and exit grid unchanged.

**The menus:** the base table's menus (`config/state_policy_v12.yaml`, the no-closure leaf of D-501/D-502) with each
risk list extended above its top by the menu's top spacing, $500, up to the size's loss limit (every risk on the $50
grid; at $50K nothing is added, both lists already reach $2,000); the funded balance cap raised to the larger of v12's
$6,000 and twice the size's Standard cap (D-666 (1)); every other setting v12's.

**The outcome model (D-666 (1)):** stage one's binary process p = (1 + e) / (1 + R), with the engine's race against the
floor, at **each R's own edge** -- the base's registered gate's bound arm (`lb_by_rr`, the `lb_gate` column of its edge
rows) or zero. `FundedByR` and `CombineByR` subclass the solver (no engine file; `state_policy.py` is not one): a trade's
win probability is read at the edge of the R it is offered at, and a Combine trade that closes early -- at the need (the
need-aware exit) or at the consistency allowance -- at the edge of the exit-grid R it closes on, as the gate's bound arm
reads an outcome at that R. With one edge at every R both are the solver to the bit (the identity checks it). Each R's
edge is net of the trades' own costs per contract (D-324), and a cost per contract is the same fraction of a risk at any
number of contracts, so a larger size changes no edge (D-666 (5)).

**The bounds (D-666 (2), (4)):** at zero edge without fees, P(pass) is at most the static-floor bound loss / (loss +
target) at every size (2/5 at $50K) -- and at $50K stage one's supremum 0.327131 and 16/49 for 1:1 at $1,500 -- and a
funded account's expected gross payouts are at most its loss limit ($2,000 at $50K). A reading outside a bound is an
engine error (refused), never a finding.

**The readings and the rule (D-666 (2), (3)):** `attempt_readings` -- an attempt's P(pass), its expected net payouts
and fees, the payouts per fee dollar, the attempt's value, the sessions to a first payout under the table's model;
`rule_rows` -- a larger size goes on only if, on at least one base, its payouts per fee dollar at the bound edge exceed
the $50K solve's by more than 10 %.
"""
from __future__ import annotations

import copy
import dataclasses
from contextlib import contextmanager
from functools import partial
from typing import Any, Iterable, Mapping

import numpy as np

from propedge.campaign import state_policy as sp

DECISION = "D-666"
SIZES = ("50k", "100k", "150k")
SUFFIX = {"50k": "", "100k": "_100k", "150k": "_150k"}
BASES = ("p14", "p16")
BASE_NAMES = {"p14": "P-14 (A3-BRK30-CB20, its 12.5- and 25-point rungs)",
              "p16": "P-16 (rc_s150_all, its 37.5-point stop)"}
EDGE_SETS = ("bound", "zero")
RULE_MARGIN = 0.10                     # D-666 (3): more than 10 % above the $50K solve's payouts per fee dollar
MENU_STEP_ABOVE = 500.0                # the menus' top spacing ($1,500 -> $2,000 -> ... ; $2,500 -> $3,000)
V12_BALANCE_CAP = 6000.0
GRID = 50.0
STAGE_ONE_SUP = 0.327131               # stage one's supremum of the Combine's P(pass) over fair strategies ($50K)
STAGE_ONE_1TO1 = 16.0 / 49.0           # 1:1 at $1,500 ($50K)
STAGE_ONE_GROSS = 2000.0               # expected gross payouts at zero edge ($50K)
LOCK_LABEL = "lock_assumed_1to1"
#: D-666 (5)'s other assumptions, labelled on the rows they touch
SIZE_LABELS = ("consistency_target_same_fraction",)
ALL_LABELS = ("costs_per_R_scaled_per_contract", "consistency_path_not_read", "dll_election_not_read",
              "no_activation_fee_plan_not_read")
#: the rows of a size that change: (Rules field or reading key, ledger key)
SIZE_RULE_KEYS = (("profit_target", "combine_profit_target"), ("mll", "combine_mll"),
                  ("xfa_mll_start", "xfa_mll_start"), ("std_cap", "xfa_std_cap"), ("cons_cap", "xfa_cons_cap"),
                  ("subscription", "subscription_fee"), ("reset_fee", "reset_fee"), ("activation", "activation_fee"))
SIZE_OTHER_KEYS = (("position_limit_minis", "combine_position_size_limit"), ("scaling_plan", "funded_scaling_plan"))


def labels_for(size: str) -> str:
    """The D-666 (5) labels a row of `size` carries ('; '-joined)."""
    lab = (LOCK_LABEL, *SIZE_LABELS) if size != "50k" else ()
    return "; ".join((*lab, *ALL_LABELS))


# ------------------------------------------------------------------------------------------------ rules and sizing


def _ledger(ledger=None):
    if ledger is not None:
        return ledger
    from propedge.contract.rules import RulesLedger

    return RulesLedger.load()


def size_rows(size: str, ledger=None) -> dict[str, Any]:
    """The size's verified rows (each through the ledger's verified-status gate), keyed by the Rules field or the
    reading's name, with the ledger key each came from."""
    if size not in SIZES:
        raise ValueError(f"size is one of {SIZES}, got {size!r}")
    led = _ledger(ledger)
    out: dict[str, Any] = {}
    for field, key in SIZE_RULE_KEYS + SIZE_OTHER_KEYS:
        k = key + SUFFIX[size]
        out[field] = led.value(k)
        out[f"{field}__key"] = k
    return out


def rules_for_size(size: str, ledger=None):
    """The engine's Rules at `size`: `rules_for_method('aeropay')` with the size's verified rows as overrides (none at
    $50K, so the base's rules exactly)."""
    from propedge.campaign.payout_method import rules_for_method

    if size == "50k":
        return rules_for_method("aeropay")
    rows = size_rows(size, ledger)
    ov = {f: float(rows[f]) for f, _ in SIZE_RULE_KEYS}
    return rules_for_method("aeropay", **ov)


def sizing_for_size(size: str, headroom_frac: float = 1.0, ledger=None):
    """The gate's sizing rule's ledger part at `size` (`SizingRule.from_ledger`, the current tier, FV3-C's headroom)
    with the size's Combine limit and funded ladder set by `dataclasses.replace`."""
    from propedge.campaign.sizing import CURRENT_TIER, MICROS_PER_MINI, ScalingLadder, SizingRule

    rows = size_rows(size, ledger)
    base = SizingRule.from_ledger(CURRENT_TIER, headroom_frac=float(headroom_frac))
    ladder = ScalingLadder.parse(str(rows["scaling_plan"]), source=f"{rows['scaling_plan__key']} (D-623, D-645)")
    return dataclasses.replace(base, ladder=ladder,
                               combine_limit_micros=int(rows["position_limit_minis"]) * MICROS_PER_MINI)


def rungs_for_size(base_rungs: sp.Rungs, sizing) -> sp.Rungs:
    """The base's rungs with the size's allowances: the Combine's fixed limit and the funded ladder in micros."""
    lad = sizing.ladder
    caps = tuple((float(th), int(m) * int(lad.micros_per_mini)) for th, m in zip(lad.thresholds, lad.minis))
    return dataclasses.replace(base_rungs, combine_cap=int(sizing.allowance_micros("combine", 0.0)), funded_caps=caps)


# ------------------------------------------------------------------------------------------------ menus and config


def extended_risks(risks: Iterable[float], loss_limit: float, step: float = MENU_STEP_ABOVE) -> tuple[float, ...]:
    """The menu's risks, then its top raised by `step` while it stays at or below the loss limit (on the $50 grid)."""
    rs = [float(x) for x in risks]
    top = max(rs)
    while top + step <= float(loss_limit) + 1e-9:
        top += step
        rs.append(top)
    if any(not sp.on_grid(r, GRID) for r in rs):
        raise ValueError("every risk on the menu lies on the $50 grid")
    return tuple(rs)


def balance_cap_for(std_cap: float) -> float:
    """The funded balance cap: v12's $6,000, raised to twice the size's Standard cap where that is more (D-666 (1))."""
    return max(V12_BALANCE_CAP, 2.0 * float(std_cap))


def size_config(cfg: dict, rules) -> dict:
    """The base table's config at a size: each menu's risks extended to the loss limit, the balance cap raised."""
    out = copy.deepcopy(cfg)
    out["menu"]["risks"] = list(extended_risks(cfg["menu"]["risks"], rules.mll))
    out["combine_menu"]["risks"] = list(extended_risks(cfg["combine_menu"]["risks"], rules.mll))
    out["funded"]["balance_cap"] = balance_cap_for(rules.std_cap)
    return out


def size_menu(cfg_size: dict, base_menu: sp.Menu, rungs: sp.Rungs) -> sp.Menu:
    """The funded menu at a size (its risks from `size_config`, the size's rungs); everything else the base's."""
    return dataclasses.replace(base_menu, risks=tuple(float(x) for x in cfg_size["menu"]["risks"]), rungs=rungs)


# ------------------------------------------------------------------------------------------------ the bases' inputs


def p14_rungs(rung_rows, n_trades: int, exit_grid: tuple[float, ...], tick_value: float) -> sp.Rungs:
    """P-14's two rungs from its registered gate's `rung` rows (one per hour: its stop, its trade count, the R's its
    trades carry an outcome at): each stop's share of the trades, each R's availability the share of the stop's trades
    offering it. The allowances are placeholders, set per size by `rungs_for_size`."""
    import pandas as pd

    r = pd.DataFrame(rung_rows).copy()
    r["stop_ticks"] = r["stop_ticks"].astype(float)
    r["cell_trades"] = r["cell_trades"].astype(float)
    total = float(r["cell_trades"].sum())
    if int(round(total)) != int(n_trades):
        raise ValueError(f"the rung rows hold {total:g} trades, the gate's verdict {n_trades}")
    stops = sorted(r["stop_ticks"].unique())
    rpc, shares, avail = [], [], []
    for s in stops:
        g = r[r["stop_ticks"] == s]
        n = float(g["cell_trades"].sum())
        rpc.append(float(s) * float(tick_value))
        shares.append(n / total)
        tab = []
        for R in exit_grid:
            off = sum(float(x.cell_trades) for x in g.itertuples()
                      if any(abs(float(v) - float(R)) < 1e-9 for v in str(x.offered).split(",") if v.strip()))
            tab.append((float(R), off / n))
        avail.append(tuple(tab))
    return sp.Rungs(risk_per_contract=tuple(rpc), shares=tuple(shares), combine_cap=50,
                    funded_caps=((0.0, 20), (1500.0, 30), (2000.0, 50)), exit_grid=tuple(float(x) for x in exit_grid),
                    availability=tuple(avail))


def one_rung(stop_ticks: int, offered: Mapping[float, float], candidates: int, exit_grid: tuple[float, ...],
             tick_value: float) -> sp.Rungs:
    """P-16's one rung at its stop: share one, each R's availability its offered count over the candidates."""
    av = tuple((float(R), float(offered.get(float(R), 0.0)) / float(candidates)) for R in exit_grid)
    return sp.Rungs(risk_per_contract=(float(stop_ticks) * float(tick_value),), shares=(1.0,), combine_cap=50,
                    funded_caps=((0.0, 20), (1500.0, 30), (2000.0, 50)), exit_grid=tuple(float(x) for x in exit_grid),
                    availability=(av,))


def needed_rs(menu: sp.Menu, combine_menu: sp.Menu) -> set[float]:
    """Every R an outcome is read at: the menus' and the exit grid's."""
    rs = ({float(R) for r, R in menu.actions() if r > 0 and R != sp.COLLECT_R}
          | {float(R) for r, R in combine_menu.actions() if r > 0})
    if menu.rungs is not None:
        rs |= {float(x) for x in menu.rungs.exit_grid}
    return rs


# ------------------------------------------------------------------------------------------------ the outcome model


class _EdgeBook:
    """Each R's edge and its Outcomes (stage one's process at that edge)."""

    def __init__(self, edges: Mapping[float, float], rules):
        if not edges:
            raise ValueError("an edge per R is needed")
        self.keys = np.array(sorted(float(k) for k in edges), float)
        self.vals = tuple(float(edges[k]) for k in sorted(edges, key=float))
        self.outs = tuple(sp.Outcomes(e, rules) for e in self.vals)

    def index(self, R) -> np.ndarray:
        R = np.asarray(R, float)
        j = np.clip(np.searchsorted(self.keys, R - 1e-9), 0, len(self.keys) - 1)
        off = np.atleast_1d(np.abs(self.keys[j] - R) >= 1e-9)
        if off.any():
            bad = sorted(set(np.round(np.atleast_1d(R)[off], 6).tolist()))
            raise ValueError(f"no edge at R = {bad}")
        return j

    def out(self, R: float) -> sp.Outcomes:
        return self.outs[int(self.index(float(R)))]


class FundedByR(sp.FundedDP):
    """The funded table with each trade's win probability read at its offered R's own edge (see the module)."""

    def __init__(self, rules, menu, edge, horizon, lam=0.0, *, edges: Mapping[float, float], **kw):
        self._book = _EdgeBook(edges, rules)
        super().__init__(rules, menu, edge, horizon, lam, **kw)

    def _transition(self, r, R, flip=False, flip_out=None):
        if r > 0 and not flip and R != sp.COLLECT_R:
            saved = self.out
            self.out = self._book.out(R)
            try:
                return super()._transition(r, R, flip=flip, flip_out=flip_out)
            finally:
                self.out = saved
        return super()._transition(r, R, flip=flip, flip_out=flip_out)


class CombineByR(sp.CombineDP):
    """The Combine's table under D-313's two rules with each outcome read at its R's own edge: the action's R for a
    trade held to its target, the exit-grid R for one closed at the need or at the consistency allowance. The body
    of `_transition_d313` is the solver's, line for line, but for the edge each state's probability is read at."""

    def __init__(self, rules, menu, edge, horizon, lam=0.0, *, edges: Mapping[float, float], **kw):
        self._book = _EdgeBook(edges, rules)
        super().__init__(rules, menu, edge, horizon, lam, **kw)
        if not (self.room_cap and self.consistency_cap):
            raise ValueError("CombineByR models the Combine under D-313's room and consistency caps only")

    def _p_groups_e(self, mask, real, rr, eidx) -> np.ndarray:
        """`_p_groups` with each state's edge: grouped by (risk, R) rounded as the solver rounds them, and the edge."""
        p = np.ones(self.nS)
        idx = np.nonzero(mask)[0]
        if not len(idx):
            return p
        keys = np.round(np.stack([real[idx], rr[idx]], axis=1), 9)
        full = np.column_stack([keys, np.asarray(eidx, float)[idx]])
        uniq, inv = np.unique(full, axis=0, return_inverse=True)
        inv = np.asarray(inv).ravel()
        for j, (rv, rrv, ei) in enumerate(uniq):
            sel = idx[inv == j]
            p[sel] = self._book.outs[int(ei)].p_win(self.cushion[sel], float(rv), float(rrv))
        return p

    def _transition_d313(self, r: float, R: float):
        if r < 0:                                                      # D-329: abandon
            return self._abandon_stack()
        same = np.where(self.alive, np.arange(self.nS), self.DEAD).astype(np.int32)
        if r == 0:
            return self._stack([same] * self.nR, [same] * self.nR, [np.ones(self.nS)] * self.nR)
        EPS = sp.EPS
        grid = np.asarray(self.rungs.exit_grid, float)
        allow = self.frac * self.target_eff[self.K]
        need = self.target_eff[self.K] - self.B
        pass_ok = (need > EPS) & ((need <= self.frac * self.B / (1.0 - self.frac) + EPS) if self.frac < 1.0
                                  else np.ones(self.nS, bool))
        e_nom = int(self._book.index(float(R)))
        e_grid = self._book.index(grid)
        iws, ils, ps = [], [], []
        for k in range(self.nR):
            real = np.full(self.nS, self._combine_realised(r, k))
            if self.room_cap:
                rpc = float(self.rungs.risk_per_contract[k])
                real = np.minimum(real, np.floor(np.maximum(self.cushion, 0.0) / rpc + 1e-9) * rpc)
            W = np.asarray(self._grid(real * R), float)
            L = np.asarray(self._stake(real), float)
            traded = self.alive & (real > 0) & (W > 0) & (L > 0)
            safe = np.where(real > 0, real, 1.0)
            Wf = np.where(traded, W, 0.0)
            gi = np.searchsorted(grid, need / safe - 1e-9)
            gi_c = np.minimum(gi, len(grid) - 1)
            at_need = traded & pass_ok & (need < Wf - EPS) & (gi < len(grid)) & (grid[gi_c] <= R + 1e-9)
            gc = np.searchsorted(grid, allow / safe - 1e-9)
            gc_c = np.minimum(gc, len(grid) - 1)
            at_cap = (traded & ~at_need & (Wf > allow + EPS) & (gc < len(grid)) & (grid[gc_c] <= R + 1e-9)
                      if self.consistency_cap else np.zeros(self.nS, bool))
            rr = np.where(at_need, grid[gi_c], np.where(at_cap, grid[gc_c], W / safe))
            Wwin = np.where(at_cap, allow, W)
            on = L == real
            if not on[traded].all():
                tgt = np.where(at_need, safe * grid[gi_c], np.where(at_cap, safe * grid[gc_c], W))
                rr = np.where(on, rr, tgt / np.where(L > 0, L, 1.0))
            # the edge each state's outcome is read at: the exit-grid R it closes on, else the action's own R
            eidx = np.where(at_need, e_grid[gi_c], np.where(at_cap, e_grid[gc_c], e_nom))
            p = self._p_groups_e(traded, L, rr, eidx)
            Bw = self.B + Wwin
            Pw = np.maximum(self.P, Bw)
            kw = self.K if self.consistency_cap else np.maximum(self.K, np.array([self.class_of(w) for w in Wwin]))
            passed = at_need | (Bw >= self.target_eff[kw] - EPS)
            iw = np.where(~traded, same, np.where(passed, self.PASS, self.index(Bw, Pw, kw))).astype(np.int32)
            c = np.minimum(L, self.cushion)
            Bl = self.B - c
            dead = Bl <= self.F + EPS
            il = np.where(~traded, same, np.where(dead, self.DEAD, self.index(np.where(dead, self.B, Bl), self.P, self.K))
                          ).astype(np.int32)
            iws.append(iw), ils.append(il), ps.append(np.where(traded, p, 1.0))
        return self._stack(iws, ils, ps)


@contextmanager
def by_r_solver(edges: Mapping[float, float]):
    """Within the block, `scripts/state_policy_dp.py`'s `cell` (and so its `solve_rent`) builds `FundedByR` and
    `CombineByR` at `edges` in place of the solver's classes; nothing else is touched and the module is restored after.
    The zero-edge oracles are never solved inside it."""
    import state_policy_dp as dp

    real = dp.sp

    class _Proxy:
        def __getattr__(self, k):
            return getattr(real, k)

    px = _Proxy()
    px.FundedDP = partial(FundedByR, edges=dict(edges))
    px.CombineDP = partial(CombineByR, edges=dict(edges))
    dp.sp = px
    try:
        yield
    finally:
        dp.sp = real


# ------------------------------------------------------------------------------------------------ the bounds


def bounds_for(size: str, rules) -> dict[str, float]:
    """The zero-edge bounds at a size: the static floor's on P(pass) and the loss limit on gross payouts; at $50K
    stage one's supremum, 16/49 and $2,000 too."""
    out = {"p_pass_static": float(rules.mll) / (float(rules.mll) + float(rules.profit_target)),
           "gross_payouts": float(rules.mll)}
    if size == "50k":
        out.update({"p_pass_sup": STAGE_ONE_SUP, "p_pass_1to1_1500": STAGE_ONE_1TO1, "gross_stage_one": STAGE_ONE_GROSS})
    return out


def oracle_values(cfg_size: dict, rules, menu: sp.Menu) -> dict[str, float]:
    """The zero-edge, fee-free values the bounds hold (`state_policy_dp.oracles`' three tables at the size's config):
    the fixed 1:1 at $1,500 (no rungs), the best fair Combine table's P(pass) under the Combine's rules, and the best
    funded table's expected gross payouts."""
    import state_policy_dp as dp

    r0 = dataclasses.replace(rules, subscription=0.0, activation=0.0, reset_fee=0.0, payout_fee=0.0, profit_split=1.0)
    T = int(cfg_size["horizon_days"])
    c = sp.CombineDP(r0, sp.Menu.fixed(1500.0, 1.0, menu.step), 0.0, T)
    v1 = c.forward(c.solve(np.ones(T)))["p_pass"]
    c = sp.CombineDP(r0, dp.combine_menu_of(cfg_size, menu), 0.0, T,
                     **{k: v for k, v in dp.combine_rules(cfg_size).items() if k in ("room_cap", "consistency_cap")})
    vmax = c.solve(np.ones(T)).value
    f = sp.FundedDP(r0, dp.without_flip(menu), 0.0, T, balance_cap=float(cfg_size["funded"]["balance_cap"]),
                    payout_grid_step=float(cfg_size["funded"]["payout_grid_step"]), **dp.funded_rules(cfg_size))
    g = f.forward(f.solve())["mean_gross_paid"]
    return {"p_pass_1to1_1500": float(v1), "max_p_pass": float(vmax), "max_gross_payouts": float(g)}


def oracle_checks(size: str, rules, vals: Mapping[str, float]) -> list[dict[str, Any]]:
    """Each oracle against its bound: (check, value, bound, relation, held)."""
    b = bounds_for(size, rules)
    tol = 1e-6
    rows = [("max_p_pass_static_bound", vals["max_p_pass"], b["p_pass_static"], "at_most"),
            ("p_pass_1to1_1500_static_bound", vals["p_pass_1to1_1500"], b["p_pass_static"], "at_most"),
            ("max_gross_payouts_loss_limit", vals["max_gross_payouts"], b["gross_payouts"], "at_most")]
    if size == "50k":
        rows += [("max_p_pass_stage_one_sup", vals["max_p_pass"], b["p_pass_sup"], "at_most"),
                 ("p_pass_1to1_1500_is_16_49", vals["p_pass_1to1_1500"], b["p_pass_1to1_1500"], "equal"),
                 ("max_gross_payouts_stage_one", vals["max_gross_payouts"], b["gross_stage_one"], "at_most")]
    out = []
    for check, v, bound, rel in rows:
        held = (abs(v - bound) < tol) if rel == "equal" else (v <= bound + tol)
        out.append({"check": check, "value": float(v), "bound": float(bound), "relation": rel, "held": bool(held)})
    return out


def reading_checks(size: str, rules, rd: Mapping[str, float], edges: Mapping[float, float]) -> list[dict[str, Any]]:
    """A solved table's own P(pass) and gross payouts per funded account against the zero-edge bounds -- binding at
    zero edge, and at any edge set no R of which is positive (a fair or unfavourable game cannot beat them)."""
    if max(float(v) for v in edges.values()) > 1e-12:
        return []
    b = bounds_for(size, rules)
    rows = [("p_pass_static_bound", rd["p_pass"], b["p_pass_static"]),
            ("gross_per_funded_loss_limit", rd["gross_payouts_per_funded"], b["gross_payouts"])]
    if size == "50k":
        rows.append(("p_pass_stage_one_sup", rd["p_pass"], b["p_pass_sup"]))
    return [{"check": c, "value": float(v), "bound": float(bd), "relation": "at_most", "held": bool(v <= bd + 1e-6)}
            for c, v, bd in rows]


# ------------------------------------------------------------------------------------------------ the readings


def first_payout_by_day(f: sp.FundedDP, sol: sp.Solution) -> np.ndarray:
    """The mass of first payouts at each day's close: `FundedDP.forward`'s loop, its first-payout sum kept by day."""
    dist = np.zeros(f.nS)
    dist[f.fresh] = 1.0
    first = np.zeros(f.T)
    vis = np.zeros((f.nS, len(f.actions)), np.float32)
    mbuf = np.zeros(f.nS)
    acc = f._scatter_acc(f.nS + 3)[:f.nS]
    for t in range(f.T):
        if dist.sum() < 1e-15:
            break
        new = f._push(dist, sol.policy[t], vis)
        dist = new[:f.nS].copy()
        ch = sol.payout[t]
        moved = np.zeros(f.nS)
        held = np.flatnonzero(dist > 0)
        for j, pos in sp._groups(ch[held]):
            if j == 0:
                continue
            idx, mask = f.pay_idx[j - 1], f.pay_mask[j - 1]
            s = held[pos]
            s = s[mask[s]]
            mbuf[s] = dist[s]
            tot = mbuf.sum()
            if tot <= 0:
                mbuf[s] = 0.0
                continue
            first[t] += mbuf[:f.nU].sum()
            sp._scatter_add(moved, acc, idx[s], mbuf[s])
            dist[s] = dist[s] - mbuf[s]
            mbuf[s] = 0.0
        dist = dist + moved
    return first


def attempt_readings(rules, ff: Mapping[str, Any], cf: Mapping[str, Any], first_by_day: np.ndarray) -> dict[str, float]:
    """One attempt's readings from the solved table's forward summaries. Fees: the subscription at purchase and as the
    engine bills it (every 21 trading days held; `mean_subscriptions_engine`), the activation at a pass -- a failed
    attempt's next purchase is the reset (both prices equal at every size, so one purchase an attempt); beside, the
    table's own accrual (the subscription at purchase plus a twenty-first a day held, `cycle_rate`'s). Payouts: net of
    the split and the method's fee (what a user receives)."""
    p = float(cf["p_pass"])
    pay_net = p * float(ff["mean_cash"])
    pay_gross = p * float(ff["mean_gross_paid"])
    fees = float(cf["mean_subscriptions_engine"]) + p * float(rules.activation)
    fees_accrued = float(rules.subscription) + float(cf["mean_subscriptions_accrued"]) + p * float(rules.activation)
    n_first = float(first_by_day.sum())
    days_first = (float((first_by_day * (np.arange(len(first_by_day)) + 1)).sum() / n_first) if n_first > 0
                  else float("nan"))
    return {"p_pass": p, "p_fail": float(cf["p_fail"]), "p_unresolved": float(cf["p_unresolved"]),
            "combine_mean_days": float(cf["mean_days"]), "combine_days_to_pass": float(cf["mean_days_to_pass"]),
            "payouts_per_funded": float(ff["mean_cash"]), "gross_payouts_per_funded": float(ff["mean_gross_paid"]),
            "p_paid_funded": float(ff["p_paid"]), "payout_count_per_funded": float(ff["mean_payouts"]),
            "funded_mean_days": float(ff["mean_days"]), "funded_p_closed": float(ff["p_closed"]),
            "payouts_per_attempt": pay_net, "gross_payouts_per_attempt": pay_gross,
            "fees_per_attempt": fees, "payouts_per_fee_dollar": pay_net / fees if fees > 0 else float("nan"),
            "attempt_value": pay_net - fees,
            "fees_per_attempt_accrued": fees_accrued,
            "payouts_per_fee_dollar_accrued": pay_net / fees_accrued if fees_accrued > 0 else float("nan"),
            "attempt_value_accrued": pay_net - fees_accrued,
            "p_first_payout_per_attempt": p * n_first,
            "funded_days_to_first_payout": days_first,
            "sessions_to_first_payout": float(cf["mean_days_to_pass"]) + days_first}


UNITS = {"p_pass": "probability", "p_fail": "probability", "p_unresolved": "probability",
         "combine_mean_days": "sessions", "combine_days_to_pass": "sessions", "payouts_per_funded": "dollars",
         "gross_payouts_per_funded": "dollars", "p_paid_funded": "probability", "payout_count_per_funded": "count",
         "funded_mean_days": "sessions", "funded_p_closed": "probability", "payouts_per_attempt": "dollars",
         "gross_payouts_per_attempt": "dollars", "fees_per_attempt": "dollars", "payouts_per_fee_dollar": "ratio",
         "attempt_value": "dollars", "fees_per_attempt_accrued": "dollars", "payouts_per_fee_dollar_accrued": "ratio",
         "attempt_value_accrued": "dollars", "p_first_payout_per_attempt": "probability",
         "funded_days_to_first_payout": "sessions", "sessions_to_first_payout": "sessions"}


# ------------------------------------------------------------------------------------------------ the rule


def rule_rows(ppfd: Mapping[tuple[str, str], float], measure: str = "payouts_per_fee_dollar") -> tuple[list[dict], str]:
    """D-666 (3): for each base and larger size, whether its payouts per fee dollar at the bound edge exceed the $50K
    solve's on the same base by more than 10 %; the verdict ('a size family follows' if any does, else 'account size
    closes') and its line. `ppfd`: {(base, size): payouts per fee dollar}."""
    rows, any_clear = [], False
    for base in BASES:
        ref = ppfd.get((base, "50k"))
        if ref is None or not np.isfinite(ref):
            raise ValueError(f"no $50K reading on {base}")
        for size in SIZES[1:]:
            v = ppfd.get((base, size))
            if v is None or not np.isfinite(v):
                raise ValueError(f"no reading at {size} on {base}")
            ratio = v / ref if ref > 0 else float("inf") if v > 0 else float("nan")
            clears = bool(v > (1.0 + RULE_MARGIN) * ref) if ref > 0 else bool(v > 0)
            any_clear |= clears
            rows.append({"base": base, "size": size, "measure": measure, "value": float(v), "ref_50k": float(ref),
                         "ratio_to_50k": float(ratio), "clears": clears})
    verdict = "a size family follows" if any_clear else "account size closes"
    cleared = [f"{r['base']} at {r['size']}" for r in rows if r["clears"]]
    line = (f"D-666 (3): {verdict} -- " + (f"{', '.join(cleared)} exceed{'s' if len(cleared) == 1 else ''} the $50K "
                                           f"solve's payouts per fee dollar at the bound edge by more than 10 %"
                                           if cleared else "no larger size's payouts per fee dollar at the bound edge "
                                           "exceeds the $50K solve's by more than 10 % on either base"))
    return rows, line


# ------------------------------------------------------------------------------------------------ the identity


def policy_problems(mine: dict, stored: dict, lam: float, stored_lam: float, *, ignore=("description",)) -> list[str]:
    """A re-solved export against the one on file: every field but `ignore` equal (the whole tree, so the same
    decision in every state), the rent to 1e-9."""
    import json

    def norm(d):
        d = json.loads(json.dumps(d, default=lambda x: x.item() if isinstance(x, np.generic) else str(x)))
        return {k: v for k, v in d.items() if k not in ignore}

    a, b = norm(mine), norm(stored)
    out = []
    if a != b:
        keys = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
        out.append(f"the export differs from the one on file (fields {keys})")
    if not abs(float(lam) - float(stored_lam)) <= 1e-9:
        out.append(f"lambda* {lam!r} against the file's {stored_lam!r}")
    return out


__all__ = ["DECISION", "SIZES", "BASES", "EDGE_SETS", "RULE_MARGIN", "rules_for_size", "sizing_for_size",
           "rungs_for_size", "extended_risks", "balance_cap_for", "size_config", "size_menu", "p14_rungs", "one_rung",
           "FundedByR", "CombineByR", "by_r_solver", "bounds_for", "oracle_values", "oracle_checks",
           "reading_checks", "first_payout_by_day", "attempt_readings", "rule_rows", "policy_problems", "labels_for"]
