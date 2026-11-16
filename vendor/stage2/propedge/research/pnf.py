"""EXPLORATORY (D-607): the Point & Figure engine for the operator's P&F catapult -- columns, the signal table, the
bullish and bearish catapult and the plain triple top / bottom, each with its natural bracket, all as D-607 words them.
Pure functions over one series of one-minute bars; `propedge.research.pf_fit` maps the setups to the trading-day clock
and `scripts/pf_fit.py` reads the development bars and writes the descriptive count. Nothing here reads an outcome:
every field of a setup is fixed by the end of its trigger bar (`tests/test_pnf.py` truncates the bars to prove it).

**Prices are integer ticks** (NQ: 0.25 points) inside the engine, so a box edge is exact; `box` and the prices are given
in points and converted (a price off the tick grid, or a box that is not a whole number of ticks, raises).

**The grid (D-607 (1))**: boxes are the multiples of the box size b from zero; one b per chart; reversal 3.

- X column with top H, on each bar: if the high reaches H + b, the top becomes the highest multiple of b at or below the
  high (every box between is filled) and no reversal is checked on that bar (continuation first). Otherwise, if the low
  reaches H - 3b, an O column starts at H - b and fills down to the lowest multiple of b at or above the low. Never both
  on one bar. O columns mirror this.
- The chart starts at the box of its first bar's close: the anchor A = the highest multiple of b at or below that close
  (reading 1). The first bar sets the anchor only. The first column is the first move of 3 boxes from the anchor: a bar
  whose high reaches A + 3b starts an X column filled from A + b up; a bar whose low reaches A - 3b an O column from
  A - b down; both on one bar: no column yet, the anchor kept (wait).
- A box is known at the end of the bar that prints it.
- The chart runs across sessions and restarts at a bar whose `contract` differs from the previous bar's (the roll): the
  restart bar sets the new anchor; every column before it is dropped from every pattern, and a pending alert is lost
  (counted beside, `lost_at_restart_<kind>`).

**Column extremes**: an X column's top is its highest box and its bottom its first box (the previous O column's low + b,
or A + b); an O column's bottom is its lowest box and its top its first box (the previous X column's top - b, or A - b).
"H(k)" is a column's top and "L(k)" its bottom, for either kind (reading 4).

**The signal table (D-607 (2))**: X column k printing H(k-2) + b is a double top buy, a triple top buy when in addition
H(k-2) = H(k-4) exactly (a quadruple top counts as a triple); "spread" off; O columns mirror it (double / triple
bottom sell). One signal per column at most, on the bar that first prints the box.

**The bullish catapult (D-607 (3))**: X column k gives a triple top buy above R = H(k-2) = H(k-4); its top H(k) is
counted against two 7-max readings -- `max7_from_R` H(k) <= R + 7b (the FIXED reading, open choice 1) and
`max7_from_breakout_box` H(k) <= R + 8b (beside); O column k+1's low against two pullback readings --
`above_pattern_low` L(k+1) > L(k-1) (the FIXED reading, open choice 2) and `retest` L(k+1) > R (beside). The alert is
the end of the bar printing X column k+2's first box (L(k+1) is then final and the whole bracket known); the trigger is
the bar on which column k+2 prints H(k) + b (possibly the alert bar itself). A setup is emitted whenever the loosest of
the 2 x 2 readings holds (`max7_from_breakout_box` and `above_pattern_low`; `retest` implies `above_pattern_low` because
L(k-1) <= R - 3b), each setup carrying its four flags, so one pass gives the fixed reading and its alternates. A column
k+2 that reverses before H(k) + b leaves the alert untriggered (counted beside, `untriggered_<kind>`).

- Bracket: entry T = H(k) + b; stop L(k+1) - b; D = T - stop = (H(k) - L(k+1)) + 2b.
- Horizontal count: target = L_p + 6 x 3b, L_p the lowest box of columns k-4 .. k+1; target R = (target - T) / D.

**The bearish catapult** mirrors every rule: O column k gives a triple bottom sell below S = L(k-2) = L(k-4); L(k) >=
S - 7b (fixed) / S - 8b (beside); X column k+1's top H(k+1) < H(k-1) (fixed) / H(k+1) < S (retest); alert at O column
k+2's first box; trigger at its printing L(k) - b. Entry T = L(k) - b; stop H(k+1) + b; D = stop - T; target = H_p -
6 x 3b, H_p the highest box of columns k-4 .. k+1; target R = (T - target) / D (reading 5).

**The plain triple top buy** (the PDF's benchmark): R = H(k-2) = H(k-4); alert at the end of the bar printing X column
k's first box; trigger when column k prints R + b; entry B = R + b; stop L(k-1) - b; target = the lowest box of columns
k-4 .. k-1 + 4 x 3b. The plain triple bottom sell mirrors it.

**The derivation (D-607 (4))**, checked on every setup by `check_bracket` (a violation raises `PnFIdentityError`, never
an `assert`, so `python -O` cannot strip it): D >= 5b on every setup; under the retest reading 5b <= D <= 8b with the
fixed 7-max and <= 9b with the breakout-box 7-max.
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Sequence

import numpy as np

DECISION = "D-607"
TICK = 0.25                                # NQ / MNQ: points a tick
REVERSAL = 3
BOXES = (2.5, 5.0, 7.5, 10.0)              # D-607 (7): points (10, 20, 30, 40 ticks)
COUNT_COLUMNS_CATAPULT = 6                 # D-607 (3): columns k-4 .. k+1
COUNT_COLUMNS_PLAIN = 4                    # columns k-4 .. k-1
MAX7 = 7                                   # open choice 1, fixed: H(k) <= R + 7b
MAX7_BREAKOUT_BOX = 8                      # beside: H(k) <= R + 8b

BULL_CATAPULT = "bull_catapult"
BEAR_CATAPULT = "bear_catapult"
TRIPLE_TOP = "triple_top_buy"
TRIPLE_BOTTOM = "triple_bottom_sell"
KINDS = (BULL_CATAPULT, BEAR_CATAPULT, TRIPLE_TOP, TRIPLE_BOTTOM)
CATAPULTS = (BULL_CATAPULT, BEAR_CATAPULT)
PLAINS = (TRIPLE_TOP, TRIPLE_BOTTOM)
SIGNALS = ("double_top_buy", "triple_top_buy", "double_bottom_sell", "triple_bottom_sell")


class PnFIdentityError(ValueError):
    """A setup breaks D-607 (4)'s derivation (D < 5b, or the retest reading's 8b / 9b ceiling): an engine error."""


def to_ticks(x: Any, tick: float = TICK) -> list[int]:
    """Prices in points as integer ticks; a price off the tick grid raises."""
    a = np.asarray(x, dtype=float)
    t = np.rint(a / tick)
    if a.size and not np.allclose(t * tick, a, rtol=0.0, atol=1e-9):
        raise ValueError(f"a price is off the {tick}-point tick grid")
    return [int(v) for v in t.tolist()]


def box_ticks(box: float, tick: float = TICK) -> int:
    bt = int(round(float(box) / tick))
    if bt <= 0 or abs(bt * tick - float(box)) > 1e-9:
        raise ValueError(f"box {box} is not a whole number of {tick}-point ticks")
    return bt


def check_bracket(s: dict[str, Any], bt: int) -> None:
    """D-607 (4) on one setup (ticks): D >= 5b; under the retest reading D <= 8b (fixed 7-max) or 9b (breakout box)."""
    d = int(s["D"])
    if d < 5 * bt:
        raise PnFIdentityError(f"{s['kind']} at bar {s.get('trigger_bar')}: D {d} ticks < 5b ({5 * bt}) -- D-607 (4)")
    if s["kind"] in CATAPULTS and s.get("retest"):
        cap = (8 if s.get("max7_from_R") else 9) * bt
        if d > cap:
            raise PnFIdentityError(f"{s['kind']} at bar {s.get('trigger_bar')}: D {d} ticks > {cap} under the retest "
                                   "reading -- D-607 (4)")


def scan(high: Sequence[float], low: Sequence[float], close: Sequence[float], contract: Sequence[Any] | None = None,
         *, box: float, tick: float = TICK) -> dict[str, Any]:
    """One pass over the bars (in order): the columns, the signal table, the setups and the counts beside.

    Returns {box_ticks, columns: [{chart, index, dir, top, bottom, start_bar}], signals: [{bar, chart, column, kind,
    level}], setups: [dict, ticks], alerts: [dict, ticks], restarts: [bar index of each restart], counts: Counter}.
    Column indices in signals and setups are chart-relative. Every value is in ticks.

    `alerts` (D-612, additive: the setups and counts are unchanged) holds every pending entry as it was opened -- a
    setup's fields without `trigger_bar`, plus `box_ticks`, `fate` ('triggered', 'untriggered', 'lost_at_restart' or
    'open_at_end'), `end_bar` (the bar that triggered it, killed it or restarted the chart; None if open at the end) and
    `trigger_bar` (None unless triggered). The triggered alerts are exactly the setups."""
    bt = box_ticks(box, tick)
    H, L, C = to_ticks(high, tick), to_ticks(low, tick), to_ticks(close, tick)
    n = len(H)
    if not (len(L) == len(C) == n):
        raise ValueError("high, low and close must have one value a bar")
    con = list(contract) if contract is not None else None
    if con is not None and len(con) != n:
        raise ValueError("contract must have one value a bar")
    rev = REVERSAL * bt

    c_dir: list[int] = []
    c_top: list[int] = []
    c_bot: list[int] = []
    c_start: list[int] = []
    c_chart: list[int] = []
    signals: list[dict] = []
    setups: list[dict] = []
    restarts: list[int] = []
    counts: Counter = Counter()
    pending: list[dict] = []
    alert_list: list[dict] = []            # D-612: every pending entry at its creation, with its fate (additive)
    recs: list[dict] = []                  # the alert record of each pending entry, in step with `pending`
    opened: list[dict] = []                # the entries opened by the column just started
    sig: list = []                         # [level, kind] of the current column's double/triple signal, or empty
    chart, cs, cur, anchor = -1, 0, -1, 0

    def alerts(i: int) -> None:
        """A new column at index j = cur printed its first box(es) on bar i: the previous column is final."""
        nonlocal pending, sig, recs
        for p, a in zip(pending, recs):
            counts[f"untriggered_{p['kind']}"] += 1
            a["fate"], a["end_bar"] = "untriggered", i
        pending, recs = [], []
        sig = []
        j = cur
        r = j - cs
        d = c_dir[j]
        ext = c_top if d > 0 else c_bot     # the extreme the signals compare: tops of X, bottoms of O columns
        if r >= 2:
            lvl = ext[j - 2] + d * bt
            triple = r >= 4 and ext[j - 2] == ext[j - 4]
            sig = [lvl, ("triple_" if triple else "double_") + ("top_buy" if d > 0 else "bottom_sell")]
        # the plain triple top / bottom: column k = j
        if r >= 4 and ext[j - 2] == ext[j - 4]:
            lv = ext[j - 2]
            entry = lv + d * bt
            if d > 0:
                stop = c_bot[j - 1] - bt
                pat = min(c_bot[j - 4:j])
                target = pat + COUNT_COLUMNS_PLAIN * rev
            else:
                stop = c_top[j - 1] + bt
                pat = max(c_top[j - 4:j])
                target = pat - COUNT_COLUMNS_PLAIN * rev
            D = d * (entry - stop)
            opened.append({"kind": TRIPLE_TOP if d > 0 else TRIPLE_BOTTOM, "side": d, "chart": chart, "column": r,
                            "alert_bar": i, "level": lv, "entry": entry, "stop": stop, "D": D,
                            "pattern_extreme": pat, "target": target, "column_k_extreme": None,
                            "pullback_extreme": c_bot[j - 1] if d > 0 else c_top[j - 1],
                            "max7_from_R": None, "max7_from_breakout_box": None, "above_pattern_low": None,
                            "retest": None})
        # the catapult: column k = j - 2, its pullback k + 1 = j - 1, the trigger column k + 2 = j
        if r >= 6 and ext[j - 4] == ext[j - 6] and d * (ext[j - 2] - ext[j - 4]) > 0:
            kind = BULL_CATAPULT if d > 0 else BEAR_CATAPULT
            lv = ext[j - 4]
            hk = ext[j - 2]
            far = c_bot if d > 0 else c_top   # the pullback columns' extremes
            pk1, pkm1 = far[j - 1], far[j - 3]
            m7 = d * (hk - lv) <= MAX7 * bt
            m8 = d * (hk - lv) <= MAX7_BREAKOUT_BOX * bt
            above = d * (pk1 - pkm1) > 0
            retest = d * (pk1 - lv) > 0
            counts[f"candidates_{kind}"] += 1
            if not m8:
                counts[f"rejected_7max_{kind}"] += 1
            if not above:
                counts[f"rejected_new_extreme_{kind}"] += 1
            if m8 and above:
                entry = hk + d * bt
                stop = pk1 - d * bt
                if d > 0:
                    pat = min(c_bot[j - 6:j])
                    target = pat + COUNT_COLUMNS_CATAPULT * rev
                else:
                    pat = max(c_top[j - 6:j])
                    target = pat - COUNT_COLUMNS_CATAPULT * rev
                opened.append({"kind": kind, "side": d, "chart": chart, "column": r - 2, "alert_bar": i, "level": lv,
                                "entry": entry, "stop": stop, "D": d * (entry - stop), "pattern_extreme": pat,
                                "target": target, "column_k_extreme": hk, "pullback_extreme": pk1,
                                "max7_from_R": m7, "max7_from_breakout_box": m8, "above_pattern_low": above,
                                "retest": retest})
        register(i)

    def register(i: int) -> None:
        """D-612: the entries `alerts` opened on bar i become pending, each with its alert record."""
        for p in opened:
            pending.append(p)
            a = dict(p)
            a.update({"box_ticks": bt, "fate": "pending", "end_bar": None, "trigger_bar": None})
            alert_list.append(a)
            recs.append(a)
        opened.clear()

    def reached(i: int) -> None:
        """The current column's extreme moved on bar i: its signal and its pending setups trigger when reached."""
        nonlocal pending, sig, recs
        d = c_dir[cur]
        x = c_top[cur] if d > 0 else c_bot[cur]
        if sig and d * (x - sig[0]) >= 0:
            signals.append({"bar": i, "chart": chart, "column": cur - cs, "kind": sig[1], "level": sig[0]})
            sig = []
        if pending:
            keep, keep_r = [], []
            for p, a in zip(pending, recs):
                if d * (x - p["entry"]) >= 0:
                    s = dict(p)
                    s["trigger_bar"] = i
                    s["box_ticks"] = bt
                    check_bracket(s, bt)
                    setups.append(s)
                    a["fate"], a["end_bar"], a["trigger_bar"] = "triggered", i, i
                else:
                    keep.append(p)
                    keep_r.append(a)
            pending, recs = keep, keep_r

    for i in range(n):
        hi, lo = H[i], L[i]
        if i == 0 or (con is not None and con[i] != con[i - 1]):
            if i:
                restarts.append(i)
                for p, a in zip(pending, recs):
                    counts[f"lost_at_restart_{p['kind']}"] += 1
                    a["fate"], a["end_bar"] = "lost_at_restart", i
            pending, sig, recs = [], [], []
            chart += 1
            cs, cur = len(c_dir), -1
            anchor = (C[i] // bt) * bt
            continue
        if cur < 0:
            up, dn = hi >= anchor + rev, lo <= anchor - rev
            if up == dn:                   # no 3-box move yet, or both on one bar: wait
                if up:
                    counts["first_column_waits_both"] += 1
                continue
            if up:
                c_dir.append(1), c_top.append((hi // bt) * bt), c_bot.append(anchor + bt)
            else:
                c_dir.append(-1), c_top.append(anchor - bt), c_bot.append(-((-lo) // bt) * bt)
            c_start.append(i), c_chart.append(chart)
            cur = len(c_dir) - 1
            alerts(i)
            reached(i)
            continue
        if c_dir[cur] > 0:
            top = c_top[cur]
            if hi >= top + bt:             # continuation first
                c_top[cur] = (hi // bt) * bt
                reached(i)
            elif lo <= top - rev:
                c_dir.append(-1), c_top.append(top - bt), c_bot.append(-((-lo) // bt) * bt)
                c_start.append(i), c_chart.append(chart)
                cur = len(c_dir) - 1
                alerts(i)
                reached(i)
        else:
            bot = c_bot[cur]
            if lo <= bot - bt:
                c_bot[cur] = -((-lo) // bt) * bt
                reached(i)
            elif hi >= bot + rev:
                c_dir.append(1), c_top.append((hi // bt) * bt), c_bot.append(bot + bt)
                c_start.append(i), c_chart.append(chart)
                cur = len(c_dir) - 1
                alerts(i)
                reached(i)
    for p, a in zip(pending, recs):        # alive at the series' end: neither triggered nor dead
        a["fate"] = "open_at_end"
        counts[f"open_at_end_{p['kind']}"] += 1
    starts: dict[int, int] = {}
    columns = []
    for j in range(len(c_dir)):
        ch = c_chart[j]
        starts.setdefault(ch, j)
        columns.append({"chart": ch, "index": j - starts[ch], "dir": c_dir[j], "top": c_top[j], "bottom": c_bot[j],
                        "start_bar": c_start[j]})
    return {"box_ticks": bt, "columns": columns, "signals": signals, "setups": setups, "alerts": alert_list,
            "restarts": restarts,
            "counts": counts}


#: the setup fields that are prices (ticks in the engine, points in a row)
PRICE_FIELDS = ("level", "entry", "stop", "D", "pattern_extreme", "target", "column_k_extreme", "pullback_extreme")


def target_r(s: dict[str, Any]) -> float:
    """(target - T) / D on the trade's side: the bull's (target - T) / D, the bear's (T - target) / D."""
    return float(s["side"]) * (float(s["target"]) - float(s["entry"])) / float(s["D"])


__all__ = ["DECISION", "TICK", "REVERSAL", "BOXES", "COUNT_COLUMNS_CATAPULT", "COUNT_COLUMNS_PLAIN", "MAX7",
           "MAX7_BREAKOUT_BOX", "BULL_CATAPULT", "BEAR_CATAPULT", "TRIPLE_TOP", "TRIPLE_BOTTOM", "KINDS", "CATAPULTS",
           "PLAINS", "SIGNALS", "PnFIdentityError", "to_ticks", "box_ticks", "check_bracket", "scan", "PRICE_FIELDS",
           "target_r"]
