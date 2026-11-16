"""Family RC -- the resolved coin (D-521, re-declared by D-525): P-14's design with the signal replaced by a seeded coin.
This module holds the family's mechanics: sections 1-4 are D-521's fixed-slot design (kept so `scripts/rc_screen.py`
reproduces D-523's screen); the D-525 section at the end is the re-entry design `scripts/rc_reentry_screen.py` runs --
a coin offered every five minutes, admitted by D-212's resolution test, taken when the strict router finds every
account flat.

**1. The candidate slots** are T24's 23 decision slots (`atlas_walk.t24_slots`: every hour 17:00 to 14:00 CT and
08:30), on the trading-day clock (minutes after 17:00 CT).

**2. The walk.** Every slot on every walked day (A1's day set: normal and BLS-report days; a report day's slots before
the 07:30 CT cut dropped -- `a3_resolution_map.pool_events`' rule) is walked long and short by FV3-C's rung walk
(`fv3_rung_walk`, through `atlas_a3.walk_minutes`, the A3 rung walk's conventions) on FV3-C's two rungs (50 and 100
MNQ ticks, 12.5 and 25 points) at every quarter R to 3R, entered at the first bar opening after the slot
(`DELAY` = 0: a clock entry is known in advance -- D-521 (1); the alert fires before the slot, so the order is working
at it).

**3. The slot rule -- by resolution only, never by R or P&L** (D-521 (2), D-515's rule applied per rung). For each
rung and slot, from the walk's KIND and EXIT-BAR columns alone (`RESOLUTION_COLUMNS`; `resolution_table` refuses any
other input):

  (a) the unresolved share -- the share of walks (both sides pooled: the coin chooses the side) that reach the 15:10
      flatten at the table's largest offered R (`R_RESOLVE` = 3) -- at most `UNRESOLVED_OVERALL` (0.5 %) over the
      window and at most `UNRESOLVED_YEAR` (1.0 %) in every calendar year; a slot with no walk in a year does not
      qualify;
  (b) each qualifying slot is an interval from the slot to the 99th percentile of the walk's latest exit bar over the R
      grid (both sides), plus D-429's five minutes; intervals are picked by earliest end (ties: the earlier slot), each
      starting at or after the last picked interval's end, at most `MAX_SLOTS` (five: one trade an account a session,
      five seats) -- so the previous trade has resolved before the next opens on at least 99 % of days.

**4. The trades.** On every walked day, each scheduled slot of the rung (a report day's before the cut excluded) is
one trade, its side the coin's: `coin_table` draws one fair coin per (date, slot) of the whole grid -- every A1 day x
every T24 slot, in that order -- from `np.random.default_rng(COIN_SEED)`, so both cells see the same side at the same
(date, slot). The trade carries every R of the grid, each settled and costed as `atlas_a3.cell_trades` costs A3's
trades (a tick at entry, the fee a micro-equivalent pays at the fresh Combine's size, the exit's ticks by kind), in
FV3-C's gate-trades shape.
"""
from __future__ import annotations

import math
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

DECISION = "D-521"
COIN_SEED = 20261102                      # D-521 (1): fixed before anything was read
DELAY = 0                                 # bars after the slot (D-521 (1))
RUNGS = (50, 100)                         # FV3-C's rungs in MNQ ticks: 12.5 and 25 points (the family's two cells)
R_RESOLVE = 3.0                           # the table's largest offered R (FV3-C's rr_menu reaches 3R)
UNRESOLVED_OVERALL = 0.005                # D-515 2(a)
UNRESOLVED_YEAR = 0.01
SPACING_Q = 99.0                          # D-515 2(c)
GAP_MINUTES = 5.0                         # D-429's five minutes
MAX_SLOTS = 5                             # one trade an account a session, five seats
FLATTEN_KIND = 2                          # fv3_rung_walk.FLATTEN
KIND_CODE = {0: "s", 1: "t", 2: "f", 3: "b"}   # atlas_a3.KIND_CODE


def cell_name(stop_ticks: int) -> str:
    return f"rc_s{int(stop_ticks)}"


def ct(slot: int) -> str:
    """A trading-day-clock slot (minutes after 17:00 CT) as HH:MM CT."""
    m = (int(slot) + 17 * 60) % (24 * 60)
    return f"{m // 60:02d}:{m % 60:02d}"


# ------------------------------------------------------------------------------------------------ the coin


def coin_table(dates: Sequence[str], slots: Sequence[int], seed: int = COIN_SEED) -> dict[tuple[str, int], int]:
    """{(date, slot): +1 long / -1 short}: one fair coin per cell of the grid, dates sorted, slots ascending."""
    ds, ss = sorted(str(d) for d in dates), sorted(int(s) for s in slots)
    u = np.random.default_rng(int(seed)).random(len(ds) * len(ss))
    side = np.where(u < 0.5, 1, -1)
    return {(d, s): int(side[i * len(ss) + j]) for i, d in enumerate(ds) for j, s in enumerate(ss)}


# ------------------------------------------------------------------------------------------------ the slot rule


def resolution_columns(rungs: Sequence[int], rr_grid: Sequence[float]) -> list[str]:
    """The only walk columns the slot rule reads: each rung's kind at `R_RESOLVE` and its exit bar at every R."""
    out = []
    for S in rungs:
        out.append(f"k{int(S)}_{R_RESOLVE:g}")
        out += [f"x{int(S)}_{float(R):g}" for R in rr_grid]
    return out


def resolution_table(res: pd.DataFrame, rungs: Sequence[int], rr_grid: Sequence[float]) -> pd.DataFrame:
    """Per (rung, slot): walks, the unresolved share at `R_RESOLVE` overall, by year and its worst year, and the 99th
    percentile of the latest exit bar over the R grid. `res` holds `date`, `slot` and `resolution_columns` ONLY -- any
    other column (an R, a gross, a MAE, a side) is refused, so the rule cannot see P&L."""
    allowed = {"date", "slot"} | set(resolution_columns(rungs, rr_grid))
    extra = set(res.columns) - allowed
    if extra:
        raise ValueError(f"the slot rule reads resolution columns only; refused: {sorted(extra)}")
    res = res.assign(year=res["date"].astype(str).str[:4].astype(int))
    rows = []
    for S in rungs:
        k = f"k{int(S)}_{R_RESOLVE:g}"
        xs = [f"x{int(S)}_{float(R):g}" for R in rr_grid]
        latest = res[xs].max(axis=1)
        unres = res[k].astype(int) == FLATTEN_KIND
        for slot, idx in res.groupby("slot", sort=True).groups.items():
            u = unres.loc[idx]
            by_year = u.groupby(res.loc[idx, "year"]).mean()
            r = {"stop_ticks": int(S), "stop_points": int(S) / 4.0, "slot": int(slot), "slot_ct": ct(int(slot)),
                 "walks": int(len(idx)), "unresolved_share": float(u.mean()),
                 "unresolved_worst_year": float(by_year.max()), "unresolved_worst_year_is": int(by_year.idxmax()),
                 "exit_p99": float(np.percentile(latest.loc[idx].to_numpy(float), SPACING_Q))}
            for y, v in by_year.items():
                r[f"unresolved_{int(y)}"] = float(v)
            rows.append(r)
    return pd.DataFrame(rows)


def qualifies(row: Mapping[str, Any], years: Sequence[int]) -> bool:
    """3(a): at most 0.5 % unresolved overall and 1.0 % in every year (a year with no walk fails)."""
    if not float(row["unresolved_share"]) <= UNRESOLVED_OVERALL:
        return False
    for y in years:
        v = row.get(f"unresolved_{int(y)}")
        if v is None or (isinstance(v, float) and math.isnan(v)) or not float(v) <= UNRESOLVED_YEAR:
            return False
    return True


def schedule(cells: pd.DataFrame, max_slots: int = MAX_SLOTS, gap: float = GAP_MINUTES) -> list[int]:
    """3(b): qualifying slots as intervals [slot, exit p99 + gap], picked by earliest end (ties: the earlier slot),
    each starting at or after the last picked interval's end, at most `max_slots`."""
    iv = sorted((float(r["exit_p99"]) + float(gap), int(r["slot"])) for _, r in cells.iterrows())
    picked: list[int] = []
    edge = -math.inf
    for end, slot in iv:
        if slot >= edge:
            picked.append(slot)
            edge = end
            if len(picked) >= int(max_slots):
                break
    return sorted(picked)


def choose(table: pd.DataFrame, years: Sequence[int]) -> dict[int, dict[str, Any]]:
    """{rung: its qualifying slots and schedule} -- every rung is a cell; nothing is chosen between them here."""
    out = {}
    for S in sorted(int(x) for x in table["stop_ticks"].unique()):
        g = table[table["stop_ticks"] == S]
        ok = g[[qualifies(r, years) for _, r in g.iterrows()]]
        out[S] = {"qualifying_slots": [int(x) for x in ok["slot"]], "schedule": schedule(ok)}
    return out


# ------------------------------------------------------------------------------------------------ the trades


def cell_trades(walks: pd.DataFrame, day_kind: Mapping[str, str], slots: Sequence[int], stop_ticks: int,
                coins: Mapping[tuple[str, int], int], fees: Mapping[int, float], *, rr_grid: Sequence[float],
                fresh_rr: float, tick_value: float, entry_ticks: float, cut: int) -> pd.DataFrame:
    """One cell's trades in FV3-C's gate-trades shape (`atlas_a3.cell_trades`' columns and arithmetic): each scheduled
    slot of each walked day -- a report day's ('b') slots before `cut` excluded -- traded on the coin's side at the
    cell's rung, every R of the grid offered and settled as FV3 settles it."""
    from propedge.research.fv3_rung_walk import EXIT_TICKS

    S = int(stop_ticks)
    w = walks[walks["slot"].astype(int).isin([int(x) for x in slots])].copy()
    w["date"] = w["date"].astype(str)
    w["day_kind"] = w["date"].map(dict(day_kind))
    w = w[~((w["day_kind"] == "b") & (w["slot"].astype(int) < int(cut)))]
    want = np.array([coins[(d, int(s))] for d, s in zip(w["date"], w["slot"])], dtype=int)
    w = w[w["side"].astype(int).to_numpy() == want]
    if w.empty:
        return pd.DataFrame()
    w = w.sort_values(["date", "entry_slot", "slot"], kind="stable").reset_index(drop=True)
    t = pd.DataFrame({"date": w["date"], "year": w["date"].str[:4].astype(int),
                      "decision_ct": w["slot"].astype(int).map(ct), "day_kind": w["day_kind"].astype(str),
                      "decision_slot_minutes": w["slot"].astype(int), "S": S, "stop_ticks": float(S),
                      "entry_t": w["entry_slot"].astype(float),
                      "side": np.where(w["side"].astype(int) > 0, "long", "short")})
    fee = float(fees[S])
    t["fee_micro_eq"] = fee
    td = float(tick_value)
    for R in rr_grid:
        kind = w[f"k{S}_{float(R):g}"].astype(int).to_numpy()
        ex = w[f"x{S}_{float(R):g}"].astype(float).to_numpy()
        mae = w[f"a{S}_{float(R):g}"].astype(float).to_numpy()
        gt = w[f"g{S}_{float(R):g}"].astype(float).to_numpy()
        gross = gt / S
        cost = (float(entry_ticks) * td + fee + np.array([float(EXIT_TICKS[int(k)]) for k in kind]) * td) / (S * td)
        t[f"r_{R:g}"] = gross - cost
        t[f"g_{R:g}"] = gross
        t[f"c_{R:g}"] = cost
        t[f"mae_{R:g}"] = mae / S
        t[f"exit_t_{R:g}"] = ex
        t[f"o_{R:g}"] = [KIND_CODE[int(k)] for k in kind]
    base = f"exit_t_{float(fresh_rr):g}"
    t["exit_t"] = t[base] if base in t else t[[f"exit_t_{R:g}" for R in rr_grid]].max(axis=1)
    ob = f"o_{float(fresh_rr):g}"
    t["flat"] = (t[ob] == "f") if ob in t else False
    return t.sort_values(["date", "entry_t"], kind="stable").reset_index(drop=True)


# ================================================================================================ D-525: re-entry when flat
#
# D-525 re-declares the family after the operator found D-521's fault (the fixed-slot rule above judged every slot by
# its slowest 3R night, so the 08:30 open was never traded): a coin entry is OFFERED at every `MARK_STEP` minutes of the
# trading day, each mark admitted only if it resolves (`mark_resolution`, D-212's 5 % for every R the table offers,
# kind columns only), and the engine's strict one-at-a-time router (D-429, P-14's five minutes) takes the next offer at
# least five minutes after the last trade resolves -- re-entry when flat, no schedule. Four windows a customer can keep
# (`WINDOWS`); each (stop, window) is a cell. The D-521 functions above stay, so D-523's screen reproduces.

DECISION_REENTRY = "D-525"
MARK_STEP = 5                             # D-525 (2): an offer every five minutes (the strict rule's gap)
SESSION_END = 22 * 60 + 10                # 15:10 CT on the trading-day clock (minutes after 17:00 CT)
UNRESOLVED_MARK = 0.05                    # D-525 (4), D-212: at most 5 % unresolved, for every offered R
#: D-525 (3): [start, end) on the trading-day clock (minutes after 17:00 CT); each with the trades it offers
WINDOWS = {"all": (0, SESSION_END),       # 17:00 CT to the cutoff
           "asia": (60, 540),             # 18:00 to 02:00 CT
           "london": (540, 930),          # 02:00 to 08:30 CT
           "us": (930, SESSION_END)}      # 08:30 CT to the cutoff


def marks(step: int = MARK_STEP, end: int = SESSION_END) -> list[int]:
    """Every offer mark of the trading day: 17:00 CT and each `step` minutes after it, before `end`."""
    return list(range(0, int(end), int(step)))


def reentry_cell_name(stop_ticks: int, window: str) -> str:
    if window not in WINDOWS:
        raise ValueError(f"unknown window {window!r}; one of {sorted(WINDOWS)}")
    return f"rc_s{int(stop_ticks)}_{window}"


def mark_resolution_columns(rungs: Sequence[int], offered_rr: Sequence[float]) -> list[str]:
    """The only walk columns the cutoff reads: each rung's kind at every R the table offers."""
    return [f"k{int(S)}_{float(R):g}" for S in rungs for R in offered_rr]


def mark_resolution(res: pd.DataFrame, rungs: Sequence[int], offered_rr: Sequence[float]) -> pd.DataFrame:
    """D-525 (4): per (rung, mark), the walks and the unresolved share (the 15:08 flatten without a level, both sides
    pooled -- the coin chooses the side) at every R the table offers, over the whole window; `offered` is True when every
    one is at most `UNRESOLVED_MARK`. `res` holds `date`, `slot` and `mark_resolution_columns` ONLY -- any other column
    (an R, a gross, a MAE, a side, an exit) is refused, so the cutoff cannot see P&L."""
    allowed = {"date", "slot"} | set(mark_resolution_columns(rungs, offered_rr))
    extra = set(res.columns) - allowed
    if extra:
        raise ValueError(f"the cutoff reads resolution columns only; refused: {sorted(extra)}")
    rows = []
    for S in rungs:
        flat = {float(R): (res[f"k{int(S)}_{float(R):g}"].astype(int) == FLATTEN_KIND) for R in offered_rr}
        for slot, idx in res.groupby("slot", sort=True).groups.items():
            shares = {R: float(f.loc[idx].mean()) for R, f in flat.items()}
            worst = max(shares.values()) if shares else float("nan")
            r = {"stop_ticks": int(S), "stop_points": int(S) / 4.0, "slot": int(slot), "slot_ct": ct(int(slot)),
                 "walks": int(len(idx)), "unresolved_worst_r": worst,
                 "offered": bool(shares) and worst <= UNRESOLVED_MARK + 1e-12}
            r.update({f"unresolved_{R:g}": v for R, v in shares.items()})
            rows.append(r)
    return pd.DataFrame(rows)


def offered_marks(table: pd.DataFrame, stop_ticks: int) -> list[int]:
    """The marks the cutoff admits at one rung, ascending."""
    g = table[(table["stop_ticks"].astype(int) == int(stop_ticks)) & table["offered"].astype(bool)]
    return sorted(int(s) for s in g["slot"])


def window_marks(offered: Sequence[int], window: str) -> list[int]:
    """The admitted marks inside a window."""
    lo, hi = WINDOWS[window]
    return [int(m) for m in offered if int(lo) <= int(m) < int(hi)]


#: D-526: the card's stop distribution keeps every 10th trading day of the cell's sorted day set (all offered trades and
#: states on those days); the engine always receives the full candidate set
STOPS_EVERY_DAYS = 10


def subsample_days(dates: Sequence[str], every: int = STOPS_EVERY_DAYS) -> list[str]:
    """D-526: the cell's distinct trading days in date order, those whose index is a multiple of `every`."""
    ds = sorted({str(d) for d in dates})
    return [d for i, d in enumerate(ds) if i % int(every) == 0]



# ================================================================================================ D-533 (2): the release bar
#
# P-15's audit (D-533, finding 1): a report day's marks before the 07:30 CT cut are dropped, but the 07:30 mark itself is
# offered and enters at the open of the release bar (the BLS 08:30 ET release), at most of the maximum size -- tier 1
# (D-145; Topstep 10305426). D-533 (2): the confirmed candidate offers no entry on a report day before 07:35 CT, the
# release bar closed. OFF by default: nothing above calls it, so D-523's, D-525's and P-15's trades are unchanged; a
# caller opts in with `drop_release_minute` on a cell's built trades.

DECISION_RELEASE = "D-533"
REPORT_DAY_KIND = "b"                     # atlas_local: a BLS 08:30 ET release day
RELEASE_CLEAR_CT = (7, 35)                # D-533 (2): the first mark after the release bar has closed


def drop_release_minute(trades: pd.DataFrame, clear: int) -> pd.DataFrame:
    """A cell's built trades without a report day's (`day_kind` 'b') entries at marks before `clear` (minutes after
    17:00 CT on the trading-day clock, `collect_core.c_slot`); every other row unchanged and in order. At the cut the
    cell was built with (07:30 CT) it removes nothing; at `RELEASE_CLEAR_CT` it removes the release bar's mark."""
    if trades is None or len(trades) == 0:
        return trades
    for c in ("day_kind", "decision_slot_minutes"):
        if c not in trades.columns:
            raise ValueError(f"drop_release_minute needs the trades' {c!r} column")
    drop = (trades["day_kind"].astype(str) == REPORT_DAY_KIND) & (trades["decision_slot_minutes"].astype(int) < int(clear))
    return trades[~drop].reset_index(drop=True)


# ================================================================================================ D-536 (2): worse fills
#
# D-536 (2): every trade's cost raised by `ticks` extra ticks a side -- at the entry and at the exit, whatever the exit's
# kind -- on top of FV3's scheme (`cell_trades`: a tick at entry, the fee, the exit's ticks by kind). In R the extra cost
# is 2 x ticks x tick value over the stop's dollar risk (stop ticks x tick value), so 2 x ticks / stop ticks: the tick
# value cancels, as it does in `cell_trades`' own cost. OFF unless a caller opts in: nothing above calls it.

DECISION_FILLS = "D-536"


def add_cost_ticks(trades: pd.DataFrame, ticks_a_side: float) -> pd.DataFrame:
    """A cell's built trades with every offered R's cost raised by `ticks_a_side` extra ticks at entry and at exit:
    `r_R` lowered and `c_R` raised by 2 x ticks / S (S = the row's stop in ticks); gross, MAE, exits and every other
    column unchanged. At 0 the trades are returned unchanged (a copy)."""
    if trades is None or len(trades) == 0:
        return trades
    x = float(ticks_a_side)
    if x < 0:
        raise ValueError("extra ticks must not be negative")
    out = trades.copy()
    if x == 0:
        return out
    if "S" not in out.columns:
        raise ValueError("add_cost_ticks needs the trades' 'S' (stop ticks) column")
    delta = 2.0 * x / out["S"].astype(float)
    for col in [c for c in out.columns if c.startswith("r_")]:
        R = col[2:]
        if f"c_{R}" in out.columns:
            off = out[col].notna()
            out.loc[off, col] = out.loc[off, col] - delta[off]
            out.loc[off, f"c_{R}"] = out.loc[off, f"c_{R}"] + delta[off]
    return out

# ================================================================================================ D-538: wider stops
#
# D-538: the news-safe coin at wider stops than FV3-C's 25-point rung -- 37.5 and 50 points (150 and 200 MNQ ticks) --
# each with D-525's design and D-533's cut. The walk (`fv3_rung_walk`, through `atlas_a3.walk_minutes`), the cutoff
# (`mark_resolution`) and the trades (`cell_trades`) already take any stop in ticks; nothing above changes. The sizing is
# the engine's own (`campaign.sizing.size_trade` under the gate's `SizingRule`): `width_sizing` reads, for each stop, what
# every trading leaf of the table buys there -- the whole micros its dollar risk buys under the phase's allowance, the
# realised risk, whether the allowance binds and whether D-272's stand-aside refuses it -- so a state the stop cannot
# size is reported, never re-solved (D-538 (2)).

DECISION_WIDTH = "D-538"
WIDTH_STOPS = (150, 200)                  # D-538 (1): 37.5 and 50 points
REFERENCE_STOP = 100                      # the 25-point rung (rc_s100_all, P-15's), read beside


def width_sizing(rule: Any, leaves: Sequence[tuple[str, str, float, float | None]], stops: Sequence[int],
                 tick_value: float, *, combine_balance: float = 0.0) -> pd.DataFrame:
    """D-538 (2): per stop (ticks), trading leaf (kind 'combine' or 'funded', name, dollar risk, R) and allowance tier
    (the Combine's one; each rung of the funded ladder, read at its threshold balance): the whole micros the engine
    buys (`size_trade`: floor(risk / risk-per-micro), capped at the tier's cap), the realised risk and its share of the
    intention, whether the cap binds, whether D-272's stand-aside refuses the trade (realised under its minimum share of
    the intention, or a micro's risk under its floor) and whether it is unsized (no micro). The room above the floor is
    the account's state, not the leaf's: the risk of one micro (`risk_per_micro`) is the least room that trades."""
    from propedge.campaign.sizing import size_trade

    rows = []
    for S in stops:
        rpc = float(S) * float(tick_value)
        for kind, name, risk, rr in leaves:
            if not float(risk) > 0:
                continue
            if kind == "combine":
                tiers = [(float(combine_balance), rule.allowance_micros("combine", float(combine_balance)))]
            else:
                lad = rule.ladder
                tiers = [(float(th), rule.allowance_micros("funded", float(th))) for th in lad.thresholds]
            for bal, allowance in tiers:
                cap = rule.cap_micros(kind, bal)
                s = size_trade(float(risk), rpc, cap)
                sa = rule.stand_aside_for(kind)
                stands = bool(sa is not None and (s.realised_risk + 1e-9 < sa[0] * s.intended_risk
                                                  or s.risk_per_contract + 1e-9 < sa[1]))
                rows.append({"section": "sizing", "stop_ticks": int(S), "stop_points": int(S) / 4.0, "kind": kind,
                             "leaf": name, "risk": float(risk), "rr": (float(rr) if rr is not None else float("nan")),
                             "tier_balance": bal, "allowance_micros": int(allowance),
                             "cap_micros": (int(cap) if cap is not None else -1), "risk_per_micro": rpc,
                             "micros": int(s.contracts), "realised_risk": float(s.realised_risk),
                             "realised_share": float(s.realised_risk / s.intended_risk) if s.intended_risk else float("nan"),
                             "at_cap": bool(s.at_cap), "stands_aside": stands, "unsized": bool(s.unsized),
                             "cannot_size": bool(s.unsized or stands)})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------------------------ D-542: the funded cap

DECISION_WIDTH_DIAG = "D-542"

from dataclasses import dataclass as _dataclass, fields as _fields  # noqa: E402

from propedge.campaign.sizing import SizingRule as _SizingRule  # noqa: E402


@_dataclass(frozen=True)
class FundedCapRule(_SizingRule):
    """D-542's diagnostic only: the engine's `SizingRule` with the funded leg's micro cap scaled by `funded_scale`
    (floor). Every sizing path of the engine reads the cap through `cap_micros(kind, balance)` (`TradeLogSizedDraw`'s
    session cap, `can_take`, `trade_dollars`, `can_stretch`), so the cap holds wherever the engine sizes; the Combine's
    cap, the allowance itself, the stand-aside, the room cap and the fee schedule are the base rule's."""

    funded_scale: float = 1.0

    def __post_init__(self) -> None:
        super().__post_init__()
        if not 0.0 < float(self.funded_scale) <= 1.0:
            raise ValueError(f"funded_scale must be in (0, 1], got {self.funded_scale}")

    def cap_micros(self, kind: str, balance: float) -> int | None:
        cap = super().cap_micros(kind, balance)
        if kind != "funded" or cap is None:
            return cap
        return int(math.floor(cap * float(self.funded_scale) + 1e-9))


def funded_cap_rule(rule: Any, ref_stop: int, stop: int) -> Any:
    """D-542: `rule` with the funded cap scaled by `ref_stop / stop` (floor), so at a stop wider than the reference no
    funded state realises more dollars than at the reference stop where the cap binds there; `rule` itself when the stop
    is not wider (nothing to hold)."""
    if int(stop) <= int(ref_stop):
        return rule
    return FundedCapRule(**{f.name: getattr(rule, f.name) for f in _fields(_SizingRule)},
                         funded_scale=float(ref_stop) / float(stop))


def funded_cap_sizing(rule: Any, leaves: Sequence[tuple[str, str, float, float | None]], ref_stop: int, stop: int,
                      tick_value: float) -> pd.DataFrame:
    """D-542: per funded leaf and allowance tier, the realised dollars at the reference stop, at `stop` as the engine
    sizes it, and at `stop` under `funded_cap_rule` (from `width_sizing`; sizing only, no outcome)."""
    funded = [x for x in leaves if x[0] == "funded"]
    keys = ["kind", "leaf", "risk", "rr", "tier_balance"]
    a = width_sizing(rule, funded, (int(ref_stop),), tick_value)
    b = width_sizing(rule, funded, (int(stop),), tick_value)
    c = width_sizing(funded_cap_rule(rule, ref_stop, stop), funded, (int(stop),), tick_value)
    out = a[keys + ["cap_micros", "micros", "realised_risk"]].rename(
        columns={"cap_micros": "cap_ref", "micros": "micros_ref", "realised_risk": "realised_ref"})
    out = out.merge(b[keys + ["micros", "realised_risk"]].rename(
        columns={"micros": "micros_stop", "realised_risk": "realised_stop"}), on=keys, how="left")
    out = out.merge(c[keys + ["cap_micros", "micros", "realised_risk", "cannot_size"]].rename(
        columns={"cap_micros": "cap_capped", "micros": "micros_capped", "realised_risk": "realised_capped",
                 "cannot_size": "cannot_size_capped"}), on=keys, how="left")
    out.insert(0, "section", "funded_sizing")
    out["ref_stop_ticks"], out["stop_ticks"] = int(ref_stop), int(stop)
    out["above_ref"] = out["realised_stop"] > out["realised_ref"] + 1e-9
    out["capped_above_ref"] = out["realised_capped"] > out["realised_ref"] + 1e-9
    out["cap_changes"] = (out["micros_capped"] != out["micros_stop"])
    return out


__all__ = ["DECISION", "COIN_SEED", "DELAY", "RUNGS", "R_RESOLVE", "UNRESOLVED_OVERALL", "UNRESOLVED_YEAR",
           "SPACING_Q", "GAP_MINUTES", "MAX_SLOTS", "cell_name", "ct", "coin_table", "resolution_columns",
           "resolution_table", "qualifies", "schedule", "choose", "cell_trades",
           "DECISION_REENTRY", "MARK_STEP", "SESSION_END", "UNRESOLVED_MARK", "WINDOWS", "marks", "reentry_cell_name",
           "mark_resolution_columns", "mark_resolution", "offered_marks", "window_marks", "STOPS_EVERY_DAYS",
           "subsample_days", "DECISION_RELEASE", "REPORT_DAY_KIND", "RELEASE_CLEAR_CT", "drop_release_minute",
           "DECISION_FILLS", "add_cost_ticks", "DECISION_WIDTH", "WIDTH_STOPS", "REFERENCE_STOP", "width_sizing",
           "DECISION_WIDTH_DIAG", "FundedCapRule", "funded_cap_rule", "funded_cap_sizing"]
