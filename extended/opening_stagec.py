"""F-03 (family O): stage C's pieces that are not a statistic -- the judged population read from the bars before any
walk, the floors, the beside readings and the journey scorecard's paired readings (sections 12, 13). Engine-free.

**Before any outcome** (12, items 1-2): `population_offers` lays out the judged block's population offers from the
bars alone -- an admitted mark on a walked session, a report day's from 07:40, with a market fill (a bar opening at or
after the mark before the walk's end) -- so K0's judged C1 counts are read before `stage_C_judgement` reads a walk;
`population_problems` holds the walked population to that set.

**The floors** (12): (i) the in-state offers unresolved at 3R at most 5 %, overall and by year (a year with fewer than
63 sessions pooled with its neighbour, D-604), and the design's taken trades flattened at most 5 % overall and by year;
(ii) P-14's registered allowance-capped form: the design's gate row's `realised_to_intended_capped_risk` at least 0.9
(`vendor/stage2/prereg/P-14_a3-brk30-cb20.md`; E-022 (1)); (iii) growth on the required bankroll at the bound above
zero on the design's own gate campaign; (iv) every firm rule verified (Stage 2's ledger, cited); (v) conduct tier 1
(section 3, cited).

**Beside** (12): the kind decomposition of L (its gross part and its cost part, c = gross - cost by the exit's kind);
the kind shares of the in-state offers against their strata; the seeded per-offer twin (stratum-matched, drawn without
replacement by the twin's generator at draw 0); the uniform-lift valuation.

**The scorecard's paired readings** (13): per start the ahead average over months 1-3 (`p_bound.ahead_average`), the
paired differences on common start dates, `pcons` (`p_bound.SHIPPED`) one-sided at 0.05, beside; the per-start
differences' distribution with moving-block intervals by the scorecard's generator; the shares of starts better, equal
and worse at months 1, 2, 3, 6 and 12; the frontier (non-dominated designs) on P, S1, S3a and S5a.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from extended import opening_population as OP
from extended import opening_stats as ST
from extended import walker as W

FLOOR_UNRESOLVED = 0.05
FLOOR_REALISED = 0.9
POOL_SESSIONS = 63
PAIRED_MONTHS = (1, 2, 3, 6, 12)
FRONTIER_MEASURES = ("P", "S1", "S3a", "S5a")
P_LEVEL = 0.05
SCORECARD_DRAWS = 2000
SCORECARD_BLOCK = 63


# ------------------------------------------------------------------------------------------------ the judged population


def population_offers(sessions: Sequence[str], kinds: Mapping[str, str], admitted: Sequence[int],
                      arrays: Mapping[str, tuple]) -> pd.DataFrame:
    """The block's population offers from the bars alone: one row (date, slot, day_kind, year) an admitted population
    mark of a walked session with a market fill under STAGE2 (`walker.market_fill_bars` on the day's arrays)."""
    marks = [int(m) for m in admitted if OP.FIRST_MARK <= int(m) <= OP.LAST_MARK]
    rows = []
    for d in sorted(str(x) for x in sessions):
        k = str(kinds.get(d, ""))
        if k not in OP.WALKED_KINDS or d not in arrays:
            continue
        ms = [m for m in marks if not (k == OP.REPORT_DAY_KIND and m < OP.REPORT_FIRST)]
        fb = W.market_fill_bars(np.asarray(arrays[d][0], float), ms, rules=W.STAGE2)
        rows += [(d, m, k, int(d[:4])) for m, j in zip(ms, fb) if j != W.NONE]
    out = pd.DataFrame(rows, columns=["date", "slot", "day_kind", "year"])
    out["population"] = True
    return out


def population_problems(from_bars: pd.DataFrame, walked: pd.DataFrame) -> list[str]:
    a = set(zip(from_bars["date"].astype(str), from_bars["slot"].astype(int)))
    p = walked[walked["population"]]
    b = set(zip(p["date"].astype(str), p["slot"].astype(int)))
    if a != b:
        return [f"the walked population ({len(b)} offers) is not the one the states read from the bars ({len(a)}); "
                f"first differences {sorted(a ^ b)[:3]}"]
    return []


# ------------------------------------------------------------------------------------------------ the floors


def pooled_years(session_years: Sequence[int]) -> dict[int, int]:
    """{year: the year it is read with}: a year with fewer than 63 sessions pooled with its neighbour (the previous
    year, the next when it is the first) (D-604)."""
    ys, cnt = np.unique(np.asarray(session_years, int), return_counts=True)
    out = {int(y): int(y) for y in ys}
    for i, (y, n) in enumerate(zip(ys, cnt)):
        if n < POOL_SESSIONS and len(ys) > 1:
            out[int(y)] = int(ys[i - 1] if i > 0 else ys[i + 1])
    return out


def floor_resolution(kl: np.ndarray, ks: np.ndarray, selected: np.ndarray, year: np.ndarray,
                     pool: Mapping[int, int]) -> dict[str, Any]:
    """Floor (i)'s first part: the in-state offers' unresolved share at 3R, both sides pooled, overall and by pooled
    year."""
    sel = np.asarray(selected, bool)
    if not sel.any():
        return {"shares": {"overall": float("nan")}, "holds": False}
    yy = np.array([pool[int(y)] for y in np.asarray(year)[sel]], dtype=int)
    fl = np.asarray(kl)[sel] == ST.FLATTEN_KIND
    fs = np.asarray(ks)[sel] == ST.FLATTEN_KIND
    sub = {"overall": float(np.concatenate([fl, fs]).mean())}
    for y in sorted(set(yy)):
        sub[str(y)] = float(np.concatenate([fl[yy == y], fs[yy == y]]).mean())
    return {"shares": sub, "holds": all(v <= FLOOR_UNRESOLVED + 1e-12 for v in sub.values())}


def floor_taken_flattened(trades: pd.DataFrame, offers: pd.DataFrame, pool: Mapping[int, int]) -> dict[str, Any]:
    """Floor (i)'s second part: the design's taken trades (the replay's routed trades) flattened, at their own R on the
    coin's side (`kl_<R>` / `ks_<R>` of their offer), overall and by pooled year."""
    t = trades[trades["source"] == "strategy"]
    t = t[t["offer"].isin(offers.index)]
    if not len(t):
        return {"shares": {}, "holds": False, "trades": 0}
    o = offers.loc[t["offer"].to_numpy()]
    rr = pd.to_numeric(t["rr"], errors="coerce").fillna(OP.R_JUDGED).to_numpy(float)
    kind = np.array([int(r[f"kl_{OP.rkey(R)}"] if int(r["coin"]) > 0 else r[f"ks_{OP.rkey(R)}"])
                     for (_, r), R in zip(o.iterrows(), rr)], dtype=int)
    flat = kind == ST.FLATTEN_KIND
    yy = np.array([pool.get(int(str(d)[:4]), int(str(d)[:4])) for d in t["date"]], dtype=int)
    sh = {"overall": float(flat.mean())}
    for y in sorted(set(yy)):
        sh[str(y)] = float(flat[yy == y].mean())
    return {"shares": sh, "holds": all(v <= FLOOR_UNRESOLVED + 1e-12 for v in sh.values()), "trades": int(len(t))}


def gate_row(rows: pd.DataFrame, shift: str = "lower_bound") -> pd.Series:
    r = rows[(rows["shift"].astype(str) == shift) & np.isclose(pd.to_numeric(rows["enforcement_p"]), 0.0)]
    if len(r) != 1:
        raise ValueError(f"the gate holds {len(r)} rows at {shift}, 0 % denial")
    return r.iloc[0]


def _num(r: pd.Series, c: str) -> float:
    return float(r[c]) if c in r.index and pd.notna(r[c]) else float("nan")


def floor_gate(rows: pd.DataFrame) -> dict[str, Any]:
    """Floors (ii) and (iii) on the design's own gate campaign, and the gate's own beside columns."""
    b, p = gate_row(rows, "lower_bound"), gate_row(rows, "point")
    g = _num(b, "pf_growth_on_base_p50")
    rr = _num(b, "realised_to_intended_capped_risk")
    return {"growth_at_bound": g, "growth_at_point": _num(p, "pf_growth_on_base_p50"),
            "required_p90": _num(b, "pf_required_p90"), "realised_to_intended_capped_risk": rr,
            "break_even_denial": _num(b, "pf_break_even_denial_p50"),
            "share_paths_with_same_day_multi_breach": _num(b, "share_paths_with_same_day_multi_breach"),
            "floor_ii": bool(rr >= FLOOR_REALISED), "floor_iii": bool(g > 0)}


# ------------------------------------------------------------------------------------------------ beside


def kind_shares(L: ST.Layout, kl: np.ndarray, ks: np.ndarray, selected: np.ndarray) -> list[dict[str, Any]]:
    """The in-state offers' exit-kind shares (both sides) against their strata's (each offer's stratum share)."""
    out = []
    for code, name in W.KIND_CODE.items():
        if code == W.AMBIGUOUS:
            continue
        v = ((kl == code).astype(float) + (ks == code).astype(float)) / 2.0
        L.values["_kind"] = v
        y = ST.centred(L, "_kind", L.population)
        out.append({"kind": name, "in_state_share": float(np.nanmean(v[selected & L.population])),
                    "excess_over_strata": ST.lift(L, y, selected)})
    L.values.pop("_kind", None)
    return out


def kind_decomposition(L: ST.Layout, kl: np.ndarray, ks: np.ndarray, selected: np.ndarray, costs: W.Costs,
                       entry_ticks: float) -> dict[str, float]:
    """L = L_gross + L_cost (1 (v) (c)): the gross part (the side-symmetric gross at 3R, centred) and the cost part
    (minus the side-symmetric cost by the exit's kind, centred)."""
    cl = np.where(L.population, W.cost_r(np.where(L.population, kl, 0), OP.STOP, entry_ticks=entry_ticks, costs=costs),
                  np.nan)
    cs = np.where(L.population, W.cost_r(np.where(L.population, ks, 0), OP.STOP, entry_ticks=entry_ticks, costs=costs),
                  np.nan)
    L.values["_cost"] = -(cl + cs) / 2.0
    L.values["_gross"] = L.values["c"] - L.values["_cost"]
    parts = {k: ST.lift(L, ST.centred(L, f"_{k}", L.population), selected) for k in ("gross", "cost")}
    L.values.pop("_cost")
    L.values.pop("_gross")
    return {"L_gross": parts["gross"], "L_cost": parts["cost"], "L": parts["gross"] + parts["cost"]}


def drawn_twin(L: ST.Layout, selected: np.ndarray, cell: int, block: int = ST.BLOCK_JUDGED, draw: int = 0
               ) -> np.ndarray:
    """7.1's seeded per-offer draw beside: in each stratum, as many population offers as the state selects, drawn
    uniformly without replacement (the twin's generator `[seed, cell, block, draw]`, strata in group and mark order)."""
    rng = ST.rng_of(ST.SEED_TWIN, cell, block, draw)
    out = np.zeros_like(selected, dtype=bool)
    for g in range(len(L.groups)):
        rows = np.flatnonzero(L.group == g)
        for k in range(len(L.marks)):
            cand = rows[L.population[rows, k]]
            n = int(selected[cand, k].sum())
            if n:
                out[rng.choice(cand, n, replace=False), k] = True
    return out


def uniform_valuation(c1_bound: float, in_wait_per_year: float, mean_dv: float) -> float:
    """12's uniform-lift valuation beside V_line: C1's bound x the design's in-wait openings a start-year x mean_dv/4."""
    return float(c1_bound) * float(in_wait_per_year) * float(mean_dv) / 4.0


# ------------------------------------------------------------------------------------------------ the scorecard


def ahead(table: pd.DataFrame) -> pd.Series:
    """Each start's ahead average over months 1-3 (starts with 63 sessions observed), by start date (`p_bound`'s)."""
    from extended import p_bound as PB

    return PB.ahead_average(table)


def paired_rows(name: str, a: pd.DataFrame, b: pd.DataFrame, other: str, *, b_ahead: pd.Series | None = None,
                rng_key: Sequence[int] = (ST.SEED_SCORECARD, 0), draws: int = SCORECARD_DRAWS) -> list[dict[str, Any]]:
    """13's paired readings of design `name` (per-start table `a`) against `other` (table `b`, or its ahead series
    `b_ahead` when only that is on record -- P-14's registered start rows): `pcons`' one-sided 0.05 lower limit of the
    paired P difference (beside, never a line); the per-start difference of the ahead average and of the net at months
    1, 2, 3, 6, 12 as distributions (median, p10, p90) with moving-block intervals (63 starts, the scorecard's
    generator); the shares of starts better, equal and worse at each month."""
    from extended import p_bound as PB

    out = []
    A = ahead(a)
    B = ahead(b) if b_ahead is None else b_ahead
    D = PB.paired(A, B)
    lo = float(np.asarray(PB.lower(PB.SHIPPED, D[:, None], level=P_LEVEL)).ravel()[0]) if len(D) >= 2 * 63 else np.nan
    out.append({"design": name, "against": other, "measure": "P_difference", "stat": "mean",
                "value": float(D.mean()) if len(D) else np.nan, "n": int(len(D))})
    out.append({"design": name, "against": other, "measure": "P_difference", "stat": f"{PB.SHIPPED}_lower_0.05",
                "value": lo, "n": int(len(D))})
    if b is None:
        return out
    rng = ST.rng_of(*rng_key)
    m = a.merge(b, on="start_date", suffixes=("", "_o"))
    for mo in PAIRED_MONTHS:
        x = (pd.to_numeric(m[f"net_month_{mo}"]) - pd.to_numeric(m[f"net_month_{mo}_o"])).dropna().to_numpy(float)
        if not len(x):
            continue
        n = len(x)
        nb = max(1, int(np.ceil(n / SCORECARD_BLOCK)))
        st = rng.integers(0, max(1, n - SCORECARD_BLOCK + 1), size=(int(draws), nb))
        idx = np.minimum((st[:, :, None] + np.arange(SCORECARD_BLOCK)[None, None, :]).reshape(int(draws), -1)[:, :n],
                         n - 1)
        med = np.median(x[idx], axis=1)
        out += [{"design": name, "against": other, "measure": f"net_month_{mo}_difference", "stat": s, "value": v,
                 "n": n} for s, v in (("p50", float(np.median(x))), ("p10", float(np.quantile(x, 0.1))),
                                      ("p90", float(np.quantile(x, 0.9))), ("p50_lo95", float(np.quantile(med, 0.025))),
                                      ("p50_hi95", float(np.quantile(med, 0.975))),
                                      ("share_better", float((x > 0).mean())), ("share_equal", float((x == 0).mean())),
                                      ("share_worse", float((x < 0).mean())))]
    return out


def frontier(card: Mapping[str, Mapping[str, float]], higher: Mapping[str, bool] | None = None) -> dict[str, bool]:
    """13's frontier on P, S1, S3a, S5a: {design: on the frontier} -- not dominated by another design on every
    measure (`higher` says which way each measure is better; default higher is better)."""
    hi = {m: True for m in FRONTIER_MEASURES} if higher is None else dict(higher)
    names = list(card)
    out = {}
    for a in names:
        dom = False
        for b in names:
            if a == b:
                continue
            ge = all((card[b][m] >= card[a][m]) if hi[m] else (card[b][m] <= card[a][m]) for m in FRONTIER_MEASURES)
            gt = any((card[b][m] > card[a][m]) if hi[m] else (card[b][m] < card[a][m]) for m in FRONTIER_MEASURES)
            dom = dom or (ge and gt)
        out[a] = not dom
    return out


NOT_MODELLED = ("a user who stops when their own money runs out; the user's time; taxes; the unstated news rules "
                "(E-034): which events count as major news under 10305426 and whether holding an open position "
                "through one counts -- unstated; the GDP release minute -- unstated; the share of openings held through "
                "ISM or GDP -- unknown (no calendar on disk); E-039 (1)'s inheritance: the fallback and non-opening "
                "trades keep P-16's report-day 07:35:00 entry, on the stated end of Topstep's Tier 1 window (U7 (a))")
FTP_NOTE = ("E-007 (e)'s readings without the ten binding Focused Trader models: the engine refuses them for any funded "
            "class but the vendored FundedAccount (lockstep.py 1403-1408; E-059), for all three designs alike")

__all__ = ["population_offers", "population_problems", "pooled_years", "floor_resolution", "floor_taken_flattened",
           "gate_row", "floor_gate", "kind_shares", "kind_decomposition", "drawn_twin", "uniform_valuation", "ahead",
           "paired_rows", "frontier", "NOT_MODELLED", "FTP_NOTE", "FLOOR_UNRESOLVED", "FLOOR_REALISED"]
