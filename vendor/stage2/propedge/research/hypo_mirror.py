"""HYPOTHETICAL (D-515): the pure-mirror hedge pair -- `hypothetical_hedge` in every row, EXPLORATORY, NEVER A CANDIDATE.

Cross-account and cross-firm hedging are prohibited -- Topstep 13747047 / 10296582, Lucid 11404734 (tier 1, D-145) --
and that does not change. The operator (2026-11-01): "With no signal we can use a standard risk and RR and contract
sizing so that truncation is not an issue" and "make sure the brackets fully resolve". The question: with two exactly
mirrored accounts, how certain, how fast and how costly is a pass, and then a payout.

This module holds the study's mechanics (the walk, the pair's settlement, the resolution rule, the sizing arithmetic,
the day blocks and the deal); `scripts/hypo_mirror.py` runs it.

**1. The walk (an exact mirror, no signal).** At a clock time t (a T24 decision slot, `atlas_walk.t24_slots`: every
hour 17:00 to 14:00 CT and 08:30), the entry bar is A1's (`fast_walk.entry_bar` at delay 0: the first bar with an open
after t -- a clock entry is known in advance, so no reaction latency applies) and the reference price e its open. Both
sides read the SAME two levels, e + S and e - S, from the same bars, in whole ticks (`round(x / tick)`), to the bar
ending 15:08 CT (`orb_core.FLAT_ENTRY`, FV3-C's last held bar), with the repo's conventions for each side alone
(`fast_walk.outcomes`, `fv3_rung_walk.walk`): a target must be traded THROUGH (an excursion beyond S), a stop is
TOUCHED (S or more against), a bar that does both is the stop's (no second bars; marked a tie), a stop on a bar that
opens beyond it fills at that open (a gap, the extra loss counted), an open trade is flattened at the last close by
15:08 CT. So the level touched first settles both sides -- one wins S, the other loses S -- except where the bars
cannot say so: a tie (both stopped), a touch that does not trade through (one side stopped at the level, the other
still open: it can later win, lose or be flattened) and a gap (the loser loses more than S). Each is counted, never
dropped. Costs per micro (FV3's scheme, D-95 / `atlas_a3.cell_trades`): one tick at entry, the assumed fill model's
MNQ round turn (`config/fills.yaml`, Topstep 8284213), and the exit's ticks (a stop one, a target none, the flatten
two); at MNQ a tick is $0.50 a micro and a point $2.

**2. The resolution rule (DECLARED HERE BEFORE ANY RESOLUTION READING, 2026-11-01).** Candidates: stops S of 12.5, 20,
25 and 40 points (FV3-C's 12.5 / 25-point rungs, A1's 20 and 40) at 1:1, at each of T24's 23 slots, on every
development day with an entry (2020-01-02 .. 2026-07-16, A1's day set, the window guard read through
`propedge.data.bars.read_bars(..., "development")`). A pair is UNRESOLVED when either side is flattened at 15:08-15:10.
  (a) a (stop, slot) cell QUALIFIES when its unresolved share is at most 0.5 % over all its days and at most 1.0 % in
      every calendar year 2020-2026;
  (b) a stop is FEASIBLE only when it carries the Combine's two-win size in whole micros inside the Combine's 50-micro
      allowance (section 3);
  (c) for each feasible stop, its schedule: each qualifying slot is an interval from the slot to the 99th percentile
      of the pair's exit (the later side's exit bar) plus D-429's five minutes; intervals are picked by earliest end
      (ties: the earlier slot), each starting at or after the end of the last picked, at most five (one trade per
      account per session -- section 3 -- and five seats a firm), so the previous pair has resolved before the next
      opens on at least 99 % of days;
  (d) the stop chosen is the feasible stop whose schedule holds the most slots; ties go to the WIDER stop (the costs
      per micro are fixed, so a wider stop pays a smaller share of its risk, and a tick of gap or slip is a smaller
      share of it). The chosen stop and slots, and every cell's reading, are written to the result's `resolution` and
      `choice` rows.

**3. Sizing without truncation (rule arithmetic, not a result).** Risk = n micros x S points x $2, n a whole number,
so the dollar risk has no remainder and needs no rounding of contracts; the same n is traded in every state of its
phase (a fixed `RiskPolicy` leaf, no tier sizing and no room cap -- nothing ever cuts a trade's size). A trade's net R
does not depend on n (its costs are per micro, as its risk is), so every account of a phase reads one log.
  * **Combine** -- stage one's 1:1 at $1,500 (propsim D-08: "static 1:1, $1,500, one trade/day", P(pass) 16/49, the
    fastest to resolve) is the anchor: two wins pass ($3,000 target, `combine_profit_target`, 8284197) and two losses
    end it ($2,000 trailing MLL, `combine_mll`). With costs two wins at $1,500 fall short of $3,000 (2 x (1,500 -
    30 x $1.72) at 25 points), so the size is the SMALLEST whole n with 2 x n x (2S - c_t) >= $3,000, c_t = $1.72 a
    micro on a target ($0.50 entry tick + $1.22 round turn), and with one win, n x (2S - c_t), at most 55 % of the
    target ($1,650, `combine_consistency_max_day_frac`, 8284208: a single best day above it raises the target), and
    n <= 50 (`combine_position_size_limit`). 12.5 points: n >= 64.4 -- above 50, infeasible. 20 points: n = 40 ($1,600).
    25 points: n = 32 ($1,600). 40 points: n = 20 ($1,600). The Combine is therefore $1,600 at 1:1 at every feasible
    stop -- T24's "Combine two-shot 1:1 $1,600" (config/atlas_a1.yaml `plan`) -- one trade an account a session (a
    second win the same day would put the day above $1,650). A mirrored fresh pair settles in two trades on WW or LL
    (one passes, the other has lost twice: n x (2S + c_s) x 2 > $2,000, c_s = $2.22 a micro on a stop). THE ROOM: a
    fresh account's room ($2,000) carries the $1,600 stop; after a loss (or a win then a loss, the MLL trailing the
    end-of-day high) the room is $2,000 less one net loss -- $311 at 20 points, $329 at 25, $356 at 40 -- inside the stop: the MLL is then the account's effective stop, so a
    second loss ends it either way and a win whose adverse excursion reaches the room breaches first (the engine's
    `mae` settlement, D-156). No two-win size can avoid it: a room that carries the stop after one loss needs
    S x n <= ($2,000 - costs) / 2, which cannot reach $3,000 in three wins after costs. Those trades are counted
    (`room_cut`), not hidden.
  * **Funded (XFA, Standard path)** -- the entry tier's whole allowance, 2 minis = 20 micros (`funded_scaling_plan`
    0:2,1500:3,2000:5, 8284223; the tier never falls below it, so 20 micros is inside the allowance at every balance
    and after every payout), one trade a session: the most risk the size limit carries (stage one's funded leg is
    1.5:1 $1,000, T5 §2a; at 1:1 here). Payout arithmetic: a win of 20 x (2S - $1.72) is a winning day ($150+,
    `xfa_std_winning_day_min`) at every candidate S; five winning days (`xfa_std_winning_days`) in a row leave
    5 x 20 x (2S - 1.72): $4,828 at 25 points, so 50 % of it (`payout_max_frac_of_balance`) meets the $2,000 cap
    (`xfa_std_cap`) -- $1,800 after the 90 % split; at 20 points $3,828 ($1,914); at 40 points the cap. A loss is
    20 x (2S + 2.22); two of them pass the -$2,000 starting MLL (`xfa_mll_start`) at 25 and 40 points, so an XFA dies
    on its second net loss before its MLL locks.

**4. The deal** (`MirrorRouter`, D-514's `HedgeRouter` with one change): each signal's lead leg exactly as D-514's
(one position at a time per firm with D-429's five minutes, the firm waiting longest, its longest-waiting account
able to take it, on the coin's side); its partner at the other firm on the opposite side is the account of the SAME
KIND (Combine with Combine, funded with funded) in the lead's slot, else that firm's longest-waiting account of the
same kind that can take it, else the slot's account of the other kind (counted `cross_kind`); none -- the lead trades
alone (counted). The unhedged reference deals the lead leg only (D-514's `unhedged`).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from propedge.research import hypo_hedge as hh

TAG = hh.TAG
LABEL = ("HYPOTHETICAL (D-515): hypothetical_hedge -- a pure-mirror cross-firm hedge pair (one account long, one short, "
         "the same bracket and size at the same bar), prohibited at Topstep (13747047, 10296582) and Lucid (11404734), "
         "tier 1; modelled as if the rule did not exist, never a candidate, never ranked, sized or carried into a "
         "protocol.")
VARIANT = "D-515:hypothetical_hedge"
DECISION = "D-515"

# ------------------------------------------------------------------------------------------------ the contract
TICK = 0.25                       # NQ / MNQ tick (config/atlas_a1.yaml `contract`)
MICRO_POINT = 2.0                 # MNQ dollars a point a micro
TICK_DOLLARS = TICK * MICRO_POINT
ENTRY_TICKS = 1                   # D-95: a tick at entry (A1's slip_ticks)
STOP, TARGET, FLAT = 0, 1, 2
EXIT_TICKS = {STOP: 1, TARGET: 0, FLAT: 2}   # fv3_rung_walk.EXIT_TICKS (stop, target, flatten)
KIND_NAME = {STOP: "stop", TARGET: "target", FLAT: "flatten"}

# ------------------------------------------------------------------------------------------------ the declared rule
STOPS_POINTS = (12.5, 20.0, 25.0, 40.0)
DELAY = 0
UNRESOLVED_OVERALL = 0.005
UNRESOLVED_YEAR = 0.01
SPACING_Q = 99.0
GAP_MINUTES = 5.0                 # D-429's five minutes
MAX_SLOTS = 5                     # one trade an account a session, five seats a firm

# ------------------------------------------------------------------------------------------------ the rules
COMBINE_TARGET = 3000.0           # combine_profit_target (8284197)
COMBINE_MLL = 2000.0              # combine_mll
CONSISTENCY_FRAC = 0.55           # combine_consistency_max_day_frac (8284208)
COMBINE_MAX_MICROS = 50           # combine_position_size_limit: 5 minis / 50 micros
FUNDED_ENTRY_MICROS = 20          # funded_scaling_plan's first tier: 2 minis (8284223)
XFA_MLL = 2000.0                  # xfa_mll_start -2000
XFA_WIN_DAYS = 5                  # xfa_std_winning_days
XFA_WIN_DAY_MIN = 150.0           # xfa_std_winning_day_min
XFA_CAP = 2000.0                  # xfa_std_cap
PAYOUT_FRAC = 0.5                 # payout_max_frac_of_balance
SPLIT = 0.9                       # profit_split


def require_label(rows: Sequence[Mapping[str, Any]]) -> None:
    hh.require_label(rows)


def ticks(points: float) -> int:
    t = float(points) / TICK
    if abs(t - round(t)) > 1e-9:
        raise ValueError(f"a stop of {points} points is not a whole number of ticks")
    return int(round(t))


def cost_per_micro(kind: int, fee: float) -> float:
    """Dollars a micro: a tick at entry, the round turn, the exit's ticks."""
    return (ENTRY_TICKS + EXIT_TICKS[int(kind)]) * TICK_DOLLARS + float(fee)


# ------------------------------------------------------------------------------------------------ 1. the walk


@dataclass(frozen=True)
class Side:
    """One side's settlement at one stop: kind, exit bar, gross ticks, MAE ticks (>= 0), gap ticks, tie flag."""

    kind: int
    exit: int
    gross: int
    mae: int
    gap: int
    tie: bool


def side_walks(o, h, l, c, j0: int, end: int, d: int, stops_ticks: Sequence[int]) -> list[Side]:
    """One side (d = +1 long, -1 short) from the entry bar j0's open to bar `end`, at each stop (1:1)."""
    o, h, l, c = (np.asarray(x, dtype=float) for x in (o, h, l, c))
    e = o[j0]
    oo, hh_, ll, cc = o[j0:end + 1], h[j0:end + 1], l[j0:end + 1], c[j0:end + 1]
    ok = ~np.isnan(oo)
    with np.errstate(invalid="ignore"):
        fav = np.where(ok, np.round(((hh_ - e) if d > 0 else (e - ll)) / TICK), -np.inf)
        adv = np.where(ok, np.round(((e - ll) if d > 0 else (hh_ - e)) / TICK), -np.inf)
        aopen = np.where(ok, np.round(((e - oo) if d > 0 else (oo - e)) / TICK), -np.inf)
    rmf = np.maximum.accumulate(fav)
    rma = np.maximum.accumulate(adv)
    idx = np.flatnonzero(~np.isnan(cc))
    mark = int(round(d * (cc[idx[-1]] - e) / TICK)) if idx.size else 0
    out = []
    for S in stops_ticks:
        kt = np.flatnonzero(rmf > S)
        ks = np.flatnonzero(rma >= S)
        kt = int(kt[0]) if kt.size else None
        ks = int(ks[0]) if ks.size else None
        if ks is not None and (kt is None or ks <= kt):
            gap = int(max(0.0, aopen[ks] - S)) if ks > 0 else 0
            out.append(Side(STOP, j0 + ks, -(S + gap), S + gap, gap, kt is not None and kt == ks))
        elif kt is not None:
            out.append(Side(TARGET, j0 + kt, int(S), int(max(0.0, rma[kt])), 0, False))
        else:
            out.append(Side(FLAT, int(end), mark, int(max(0.0, rma[-1])) if np.isfinite(rma[-1]) else 0, 0, False))
    return out


PAIR_CLASSES = ("mirror", "mirror_gap", "mirror_late", "both_stop_tie", "both_stop_touch", "one_flat", "unresolved")


def pair_class(a: Side, b: Side) -> str:
    """How a pair settled: `mirror` (one target, one stop, the same bar), `mirror_gap` (so, the stop beyond its level),
    `mirror_late` (one target, one stop, different bars: a touch that traded through later), `both_stop_tie` (a bar
    that touched both levels), `both_stop_touch` (a touch without trading through, then the other level), `one_flat`
    (one stopped, the other flattened), `unresolved` (both flattened)."""
    kinds = {a.kind, b.kind}
    if kinds == {TARGET, STOP}:
        s = a if a.kind == STOP else b
        if a.exit != b.exit:
            return "mirror_late"
        return "mirror_gap" if s.gap > 0 else "mirror"
    if a.kind == STOP and b.kind == STOP:
        return "both_stop_tie" if (a.tie or b.tie) else "both_stop_touch"
    if a.kind == FLAT and b.kind == FLAT:
        return "unresolved"
    if FLAT in kinds:
        return "one_flat"
    raise AssertionError(f"two targets on one set of levels: {a}, {b}")


def day_pairs(o, h, l, c, slots: Sequence[int], stops_ticks: Sequence[int], *, delay: int = DELAY,
              flat_end: int | None = None) -> list[dict[str, Any]]:
    """Every slot's pair on one day at every stop: [{slot, entry, stop_ticks, long: Side, short: Side}]."""
    from propedge.outcomes.collect_core import C_FLAT
    from propedge.outcomes.orb_core import FLAT_ENTRY
    from propedge.research import fast_walk

    o = np.asarray(o, dtype=float)
    last = fast_walk.last_bar(o, C_FLAT)
    if last is None:
        return []
    end = min(last, FLAT_ENTRY if flat_end is None else int(flat_end))
    rows = []
    for t in slots:
        t = int(t)
        if t >= last:
            continue
        j0 = fast_walk.entry_bar(o, t, int(delay), last)
        if j0 is None or j0 >= end:
            continue
        lo = side_walks(o, h, l, c, j0, end, 1, stops_ticks)
        sh = side_walks(o, h, l, c, j0, end, -1, stops_ticks)
        for S, a, b in zip(stops_ticks, lo, sh):
            rows.append({"slot": t, "entry": int(j0), "stop_ticks": int(S), "long": a, "short": b})
    return rows


def flatten_pairs(date: str, rows: Sequence[Mapping[str, Any]], fee: float) -> list[dict[str, Any]]:
    """One row per (slot, stop) pair: both sides' settlement, net per micro and in R, and the pair's class."""
    out = []
    for r in rows:
        S = int(r["stop_ticks"])
        risk = S * TICK_DOLLARS
        rec = {"date": date, "slot": int(r["slot"]), "entry": int(r["entry"]), "stop_ticks": S,
               "stop_points": S * TICK, "class": pair_class(r["long"], r["short"])}
        for name, sd in (("long", r["long"]), ("short", r["short"])):
            net = sd.gross * TICK_DOLLARS - cost_per_micro(sd.kind, fee)
            rec.update({f"{name}_kind": int(sd.kind), f"{name}_exit": int(sd.exit), f"{name}_gross_ticks": int(sd.gross),
                        f"{name}_mae_ticks": int(sd.mae), f"{name}_gap_ticks": int(sd.gap), f"{name}_tie": bool(sd.tie),
                        f"{name}_net_micro": float(net), f"{name}_r": float(net / risk)})
        rec["pair_exit"] = max(rec["long_exit"], rec["short_exit"])
        rec["minutes_to_resolve"] = rec["pair_exit"] - rec["slot"]
        rec["unresolved"] = bool(rec["long_kind"] == FLAT or rec["short_kind"] == FLAT)
        out.append(rec)
    return out


# ------------------------------------------------------------------------------------------------ 2. the rule


def resolution_table(pairs: pd.DataFrame) -> pd.DataFrame:
    """Per (stop, slot): days, the unresolved share overall and its worst year, the mirror-break shares, and the pair's
    minutes to resolution (p50, p99)."""
    pairs = pairs.assign(year=pairs["date"].astype(str).str[:4].astype(int))
    rows = []
    for (S, t), g in pairs.groupby(["stop_ticks", "slot"], sort=True):
        by_year = g.groupby("year")["unresolved"].mean()
        r = {"stop_ticks": int(S), "stop_points": float(S) * TICK, "slot": int(t), "days": int(len(g)),
             "unresolved_share": float(g["unresolved"].mean()), "unresolved_worst_year": float(by_year.max()),
             "unresolved_worst_year_is": int(by_year.idxmax()),
             "pair_exit_p99": float(np.percentile(g["pair_exit"], SPACING_Q)),
             "minutes_p50": float(np.percentile(g["minutes_to_resolve"], 50)),
             "minutes_p99": float(np.percentile(g["minutes_to_resolve"], SPACING_Q))}
        for y, v in by_year.items():
            r[f"unresolved_{int(y)}"] = float(v)
        for k in PAIR_CLASSES:
            r[f"share_{k}"] = float((g["class"] == k).mean())
        rows.append(r)
    return pd.DataFrame(rows)


def qualifies(row: Mapping[str, Any], years: Sequence[int]) -> bool:
    if not float(row["unresolved_share"]) <= UNRESOLVED_OVERALL:
        return False
    for y in years:
        v = row.get(f"unresolved_{int(y)}")
        if v is None or (isinstance(v, float) and math.isnan(v)) or not float(v) <= UNRESOLVED_YEAR:
            return False
    return True


def schedule(cells: pd.DataFrame, max_slots: int = MAX_SLOTS, gap: float = GAP_MINUTES) -> list[int]:
    """Rule 2(c): qualifying slots as intervals [slot, p99 pair exit + gap], picked by earliest end (ties: the earlier
    slot), each starting at or after the last picked interval's end, at most `max_slots`."""
    iv = sorted(((float(r["pair_exit_p99"]) + float(gap), int(r["slot"])) for _, r in cells.iterrows()))
    picked: list[int] = []
    edge = -math.inf
    for end, slot in iv:
        if slot >= edge:
            picked.append(slot)
            edge = end
            if len(picked) >= int(max_slots):
                break
    return sorted(picked)


def choose(table: pd.DataFrame, years: Sequence[int], fee: float) -> dict[str, Any]:
    """Rule 2: per stop its qualifying slots, feasibility and schedule; the chosen stop and slots."""
    per = []
    for S in sorted(table["stop_ticks"].unique()):
        g = table[table["stop_ticks"] == S]
        ok = g[[qualifies(r, years) for _, r in g.iterrows()]]
        feas = combine_micros(S * TICK, fee) is not None
        sched = schedule(ok) if feas else []
        per.append({"stop_ticks": int(S), "stop_points": float(S) * TICK, "feasible": bool(feas),
                    "qualifying_slots": [int(x) for x in ok["slot"]], "schedule": sched})
    cand = [p for p in per if p["feasible"] and p["schedule"]]
    if not cand:
        raise RuntimeError("REFUSED (D-515): no feasible stop has a qualifying slot under the declared rule")
    best = max(cand, key=lambda p: (len(p["schedule"]), p["stop_ticks"]))
    return {"per_stop": per, "stop_ticks": best["stop_ticks"], "stop_points": best["stop_points"],
            "slots": best["schedule"]}


# ------------------------------------------------------------------------------------------------ 3. the sizing


def combine_micros(stop_points: float, fee: float) -> int | None:
    """The smallest whole n with two wins >= the target after costs, one win within the consistency cap, n <= 50; None
    when no such n exists."""
    win = float(stop_points) * MICRO_POINT - cost_per_micro(TARGET, fee)
    if not win > 0:
        return None
    n = int(math.ceil(COMBINE_TARGET / (2.0 * win) - 1e-12))
    if n > COMBINE_MAX_MICROS or n * win > CONSISTENCY_FRAC * COMBINE_TARGET + 1e-9:
        return None
    return n


def sizing(stop_points: float, fee: float) -> dict[str, Any]:
    """The Combine's and the funded leg's whole-micro sizes at a stop, with the arithmetic that fixes them."""
    S = float(stop_points)
    per_micro = S * MICRO_POINT
    win_c, loss_c = per_micro - cost_per_micro(TARGET, fee), per_micro + cost_per_micro(STOP, fee)
    nc = combine_micros(S, fee)
    if nc is None:
        raise ValueError(f"a {S:g}-point stop cannot carry the Combine's two-win size inside 50 micros")
    nf = FUNDED_ENTRY_MICROS
    cr, fr = nc * per_micro, nf * per_micro
    five = XFA_WIN_DAYS * nf * win_c
    pay = min(PAYOUT_FRAC * five, XFA_CAP)
    out = {
        "stop_points": S, "stop_ticks": ticks(S), "risk_per_micro": per_micro,
        "cost_target_per_micro": cost_per_micro(TARGET, fee), "cost_stop_per_micro": cost_per_micro(STOP, fee),
        "cost_flatten_per_micro": cost_per_micro(FLAT, fee), "fee_round_turn": float(fee),
        "combine_micros": nc, "combine_risk": cr, "combine_risk_remainder": cr - nc * per_micro,
        "combine_win_net": nc * win_c, "combine_loss_net": nc * loss_c,
        "combine_two_wins_net": 2 * nc * win_c, "combine_two_wins_pass": bool(2 * nc * win_c >= COMBINE_TARGET),
        "combine_one_win_within_consistency": bool(nc * win_c <= CONSISTENCY_FRAC * COMBINE_TARGET),
        "combine_fresh_room_carries_stop": bool(COMBINE_MLL >= cr),
        "combine_room_after_loss": COMBINE_MLL - nc * loss_c,
        # a win then a loss: the MLL trails the win's close up by the win, the loss takes the balance down by the loss
        "combine_room_after_win_then_loss": COMBINE_MLL - nc * loss_c,
        "combine_two_losses_breach": bool(2 * nc * loss_c >= COMBINE_MLL),
        "combine_micros_inside_allowance": bool(nc <= COMBINE_MAX_MICROS),
        "funded_micros": nf, "funded_risk": fr, "funded_risk_remainder": fr - nf * per_micro,
        "funded_win_net": nf * win_c, "funded_loss_net": nf * loss_c,
        "funded_win_is_winning_day": bool(nf * win_c >= XFA_WIN_DAY_MIN),
        "funded_five_wins_balance": five, "funded_first_payout_gross": pay, "funded_first_payout_net": SPLIT * pay,
        "funded_payout_at_cap": bool(pay >= XFA_CAP - 1e-9),
        "funded_two_losses_breach": bool(2 * nf * loss_c >= XFA_MLL),
        "funded_room_after_loss": XFA_MLL - nf * loss_c,
    }
    return out


# ------------------------------------------------------------------------------------------------ the day blocks


def coin_sides(n: int, seed: int) -> np.ndarray:
    """The unhedged reference's side for each trade in historical order: a seeded fair coin (+1 long, -1 short)."""
    rng = np.random.default_rng(int(seed))
    return np.where(rng.random(int(n)) < 0.5, 1, -1).astype(int)


def blocks(trades: pd.DataFrame, days: Sequence[str]) -> tuple[list, list]:
    """(cell, opposite) day blocks over `days`: the cell is each pair's coin side, the opposite the other side; one
    micro's dollars (pnl, risked, MAE) -- the draw scales them to the leg's whole-micro risk exactly."""
    from propedge.outcomes.distribution import DayBlock

    by = {d: g.sort_values(["entry", "slot"], kind="stable") for d, g in trades.groupby("date")} if len(trades) else {}
    cell, opp = [], []
    for d in days:
        g = by.get(d)
        if g is None or not len(g):
            z = np.zeros(0)
            for out in (cell, opp):
                out.append(DayBlock(pnl=z, risked=z, exit_reasons=(), risk_per_contract=z, mae=z, entry_t=z, exit_t=z,
                                    r_by_rr={1.0: z}, mae_by_rr={1.0: z}, sides=np.zeros(0, int),
                                    exit_by_rr={1.0: z}))
            continue
        coin = g["coin"].to_numpy(int)
        risk = g["stop_ticks"].to_numpy(float) * TICK_DOLLARS
        for out, flip in ((cell, 1), (opp, -1)):
            side = coin * flip
            pick = lambda col: np.where(side > 0, g[f"long_{col}"].to_numpy(float), g[f"short_{col}"].to_numpy(float))  # noqa: E731
            pnl = pick("net_micro")
            r = pnl / risk
            mae = np.maximum(pick("mae_ticks") * TICK_DOLLARS, -pnl)
            kind = pick("kind").astype(int)
            ex = pick("exit")
            out.append(DayBlock(pnl=pnl, risked=risk.copy(), exit_reasons=tuple("flatten" if k == FLAT else "bracket"
                                                                                  for k in kind),
                                risk_per_contract=risk.copy(), mae=mae, entry_t=g["entry"].to_numpy(float), exit_t=ex,
                                r_by_rr={1.0: r}, mae_by_rr={1.0: mae / risk}, sides=side.astype(int),
                                exit_by_rr={1.0: ex.copy()}))
    return cell, opp


# ------------------------------------------------------------------------------------------------ 4. the deal


class MirrorRouter(hh.HedgeRouter):
    """D-514's `HedgeRouter` (mode `hedged` or `unhedged`) with the partner chosen by kind (the module docstring, 4):
    the same-kind account in the lead's slot at the other firm, else that firm's longest-waiting same-kind account able
    to take it, else the slot's account of the other kind. Records the pairs by kind for the readings."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.funded_pairs: set[tuple[tuple, tuple]] = set()
        self.cross_kind = 0
        self.same_kind_by_wait = 0

    def deal(self, day: int, subs):  # noqa: C901 -- HedgeRouter.deal with the partner rule replaced
        if len(subs) != self.n_firms:
            raise RuntimeError("every firm submits its accounts each day")
        hs = {s.h for s in subs}
        if len(hs) != 1:
            raise RuntimeError(f"the firms' calendars disagree on day {day}: historical days {sorted(hs)}")
        h = hs.pop()
        self.day = int(day)
        out = [{tuple(k): [] for k in s.keys} for s in subs]
        for f, s in enumerate(subs):
            for k in s.keys:
                self.acct_last[f].setdefault(tuple(k), self.tick)
            self._slots(f, [tuple(k) for k in s.keys])
        n = self.stream.n_trades[h] if 0 <= h < len(self.stream.n_trades) else 0
        m = n // 2 if self.doubled else n
        if self.doubled and n % 2:
            raise RuntimeError(f"historical day {h}: a doubled day has an even number of trades, not {n}")
        if not m:
            return out
        entry, exit_, sides = self.stream.entry[h], self.stream.exit[h], self.stream.sides[h]
        exits_rr = self.stream.exits_by_rr[h]
        open_until = [-np.inf] * self.n_firms
        open_side = [0] * self.n_firms
        pos = [{tuple(k): i for i, k in enumerate(s.keys)} for s in subs]
        by_slot = [{s: k for k, s in self.slot_of[f].items()} for f in range(self.n_firms)]

        def exit_for(f, k, j):
            R = subs[f].rrs.get(k)
            if exits_rr and R is not None:
                arr = exits_rr.get(float(R))
                if arr is not None and j < len(arr) and np.isfinite(arr[j]):
                    return float(arr[j])
            return float(exit_[j])

        def can(f, k, j, count=True):
            cap = subs[f].caps.get(k)
            if cap is not None and len(out[f][k]) >= int(cap):
                return False
            if self.able and k in subs[f].states:
                drw = subs[f].router._draws.get(k)
                if drw is not None and not drw.can_take(h, j, *subs[f].states[k]):
                    if count:
                        self.passed_over += 1
                    return False
            return True

        def take(f, k, j, stamp):
            out[f][k].append(j)
            open_until[f], open_side[f] = exit_for(f, k, j), int(sides[j])
            self.firm_last[f] = stamp
            self.acct_last[f][k] = stamp
            self.routed[f] += 1

        for j in sorted(range(m), key=lambda x: (float(entry[x]), x)):
            t, side = float(entry[j]), int(sides[j])
            self.signals += 1
            if any(open_until[f] > t and open_side[f] == -side for f in range(self.n_firms)):
                self.skipped_opposite += 1
                continue
            free = [f for f in range(self.n_firms) if not open_until[f] + self.gap > t]
            if not free:
                self.skipped_busy += 1
                continue
            lead = None
            for f in sorted(free, key=lambda x: (self.firm_last[x], x)):
                for k in sorted(pos[f], key=lambda x: (self.acct_last[f][x], pos[f][x])):
                    if can(f, k, j):
                        lead = (f, k)
                        break
                if lead is not None:
                    break
            if lead is None:
                self.skipped += 1
                continue
            f, k = lead
            partner = None
            if self.mode != hh.UNHEDGED:
                g = 1 - f
                if g not in free:
                    self.partner_missing["firm_busy"] += 1
                else:
                    kb = by_slot[g].get(self.slot_of[f].get(k, -1))
                    if kb is not None and kb[0] == k[0] and can(g, kb, m + j):
                        partner = (g, kb)
                    else:
                        same = [x for x in sorted(pos[g], key=lambda x: (self.acct_last[g][x], pos[g][x]))
                                if x[0] == k[0] and can(g, x, m + j, count=False)]
                        if same:
                            partner = (g, same[0])
                            self.same_kind_by_wait += 1
                        elif kb is not None and can(g, kb, m + j):
                            partner = (g, kb)
                            self.cross_kind += 1
                        elif kb is None:
                            self.partner_missing["no_account_in_slot"] += 1
                        else:
                            self.partner_missing["cannot_take"] += 1
            self.tick += 1.0
            if partner is not None:
                g, kb = partner
                take(g, kb, m + j, self.tick - 0.5)
                take(f, k, j, self.tick)
                self.hedged += 1
                kinds = "-".join(sorted((k[0], kb[0])))
                self.pair_kinds[kinds] = self.pair_kinds.get(kinds, 0) + 1
                key = (k, kb) if f == 0 else (kb, k)
                if k[0] == "combine" and kb[0] == "combine":
                    self.combine_pairs.add(key)
                elif k[0] == "funded" and kb[0] == "funded":
                    self.funded_pairs.add(key)
            else:
                take(f, k, j, self.tick)
                self.alone += 1
            if self.log is not None:
                self.log.append((int(day), int(h), int(j), int(f), k, None if partner is None else partner[1], t,
                                 open_until[f], None if partner is None else open_until[partner[0]], side))
        return out

    def counts(self) -> dict[str, Any]:
        out = super().counts()
        out.update({"cross_kind": self.cross_kind, "same_kind_by_wait": self.same_kind_by_wait,
                    "funded_pairs": len(self.funded_pairs)})
        return out


def run_joint(specs, setup, *, n_firms: int, mode: str, gap: float = GAP_MINUTES, timeout: float = 1800.0):
    """`hypo_hedge.run_joint` with `MirrorRouter` dealing (the doubled blocks)."""
    orig = hh.HedgeRouter
    import propedge.research.hypo_hedge as mod

    mod.HedgeRouter = MirrorRouter            # run_joint builds its router by this name; restored below
    try:
        return hh.run_joint(specs, setup, n_firms=n_firms, mode=mode, doubled=True, gap=gap, timeout=timeout)
    finally:
        mod.HedgeRouter = orig


# ------------------------------------------------------------------------------------------------ the readings


def path_record(jp, *, margin: float, subscription: float, activation: float) -> dict[str, Any]:
    """`hypo_hedge.path_record` plus the mirror's own: Combine fees (subscriptions) and activation fees, funded accounts
    and their ends, payouts per funded account and per funded pair, days from activation to a first payout."""
    r = hh.path_record(jp, margin=margin)
    subs = sum(int(c.subscriptions_paid) for lp in jp.paths for c in lp.combines)
    funded = [(f, a) for f, lp in enumerate(jp.paths) for a in lp.funded]
    pays = {(f, int(a.index)): int(a.n_payouts) for f, a in funded}
    fp = [(("funded", a[1]), ("funded", b[1])) for a, b in getattr(jp.router, "funded_pairs", set())]
    pair_pays = [pays.get((0, a[1]), 0) + pays.get((1, b[1]), 0) for a, b in fp]
    # the account's own trading days to its first payout (the engine's `first_payout_day` is the account's day, 0 the
    # first session after activation, so the count is that plus one)
    first = [int(a.first_payout_day) + 1 for _, a in funded if int(a.n_payouts) > 0 and int(a.first_payout_day) >= 0]
    cdays = [int(c.days) for lp in jp.paths for c in lp.combines if c.passed]
    horizon = int(r["days"]) - 1
    r.update({
        "combine_fees": float(subs) * float(subscription), "activation_fees": float(len(funded)) * float(activation),
        "combines_passed": int(len(r["pass_days"])),
        "funded_accounts": int(len(funded)),
        "funded_breached": int(sum(1 for _, a in funded if a.ended_on is not None and not a.abandoned
                                   and int(a.ended_on) < horizon and float(a.balance) <= float(a.floor) + 1e-6)),
        "funded_ended": int(sum(1 for _, a in funded if a.ended_on is not None)),
        "funded_with_payout": int(sum(1 for _, a in funded if int(a.n_payouts) > 0)),
        "funded_payouts": int(sum(int(a.n_payouts) for _, a in funded)),
        "funded_pairs": int(len(fp)), "funded_pair_payouts": int(sum(pair_pays)),
        "funded_pairs_with_payout": int(sum(1 for x in pair_pays if x >= 1)),
        "days_activation_to_first_payout": first, "combine_days_to_pass": cdays,
        "combine_pair_outcomes": _combine_pair_outcomes(jp),
    })
    return r


def _combine_pair_outcomes(jp) -> dict[str, int]:
    """Each Combine pair (two Combines that traded as a pair at least once) by its two Combines' ends: one pass,
    none (both failed or unresolved), both."""
    end = {}
    for f, lp in enumerate(jp.paths):
        for c in lp.combines:
            end[(f, int(c.index))] = (bool(c.passed), c.resolved_on is not None)
    out = {"one": 0, "none": 0, "both": 0, "open": 0}
    for a, b in jp.router.combine_pairs:
        ea, eb = end.get((0, int(a[1])), (False, False)), end.get((1, int(b[1])), (False, False))
        if not (ea[1] and eb[1]):
            out["open"] += 1
            continue
        n = int(ea[0]) + int(eb[0])
        out[{0: "none", 1: "one", 2: "both"}[n]] += 1
    return out


def readings(recs: Sequence[Mapping[str, Any]], *, margin: float) -> dict[str, Any]:
    """`hypo_hedge.readings` plus the mirror's (D-515 (5))."""
    out = hh.readings(recs, margin=margin)
    def tot(k):  # noqa: E306
        return float(sum(float(r[k]) for r in recs))
    passes, pays = tot("combines_passed"), tot("funded_payouts")
    po = {k: sum(int(r["combine_pair_outcomes"][k]) for r in recs) for k in ("one", "none", "both", "open")}
    closed = po["one"] + po["none"] + po["both"]
    first = [d for r in recs for d in r["days_activation_to_first_payout"]]
    cdays = [d for r in recs for d in r["combine_days_to_pass"]]
    out.update({
        "combine_fees_per_pass": tot("combine_fees") / passes if passes else float("nan"),
        "activation_fees_per_payout": tot("activation_fees") / pays if pays else float("nan"),
        "all_fees_per_payout": tot("fees") / pays if pays else float("nan"),
        "combine_pairs_closed": closed, "combine_pairs_open_at_end": po["open"],
        "share_combine_pairs_one_pass": po["one"] / closed if closed else float("nan"),
        "share_combine_pairs_no_pass": po["none"] / closed if closed else float("nan"),
        "share_combine_pairs_both_pass": po["both"] / closed if closed else float("nan"),
        "funded_accounts_mean": tot("funded_accounts") / len(recs) if recs else float("nan"),
        "share_funded_breached": tot("funded_breached") / tot("funded_accounts") if tot("funded_accounts") else float("nan"),
        "share_funded_with_payout": (tot("funded_with_payout") / tot("funded_accounts") if tot("funded_accounts")
                                     else float("nan")),
        "payouts_per_funded_account": pays / tot("funded_accounts") if tot("funded_accounts") else float("nan"),
        "funded_pairs_mean": tot("funded_pairs") / len(recs) if recs else float("nan"),
        "payouts_per_funded_pair": tot("funded_pair_payouts") / tot("funded_pairs") if tot("funded_pairs") else float("nan"),
        "share_funded_pairs_with_payout": (tot("funded_pairs_with_payout") / tot("funded_pairs") if tot("funded_pairs")
                                           else float("nan")),
        "combine_days_to_pass_p50": float(np.percentile(cdays, 50)) if cdays else float("nan"),
        "combine_days_to_pass_p90": float(np.percentile(cdays, 90)) if cdays else float("nan"),
        "days_activation_to_first_payout_p50": float(np.percentile(first, 50)) if first else float("nan"),
        "days_activation_to_first_payout_p90": float(np.percentile(first, 90)) if first else float("nan"),
        "payout_dollars_per_month_mean": (out["payout_dollars_mean"] / ((int(recs[0]["days"]) - 1) / 21.0)
                                          if recs and int(recs[0]["days"]) > 1 else float("nan")),
    })
    return out


__all__ = ["TAG", "LABEL", "VARIANT", "DECISION", "STOPS_POINTS", "Side", "side_walks", "pair_class", "day_pairs",
           "flatten_pairs", "resolution_table", "qualifies", "schedule", "choose", "combine_micros", "sizing",
           "coin_sides", "blocks", "MirrorRouter", "run_joint", "path_record", "readings", "require_label"]
