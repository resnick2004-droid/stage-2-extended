"""ORB1's QuantConnect kits (config/orb_model.yaml; T15 item 9, D-249): the development runs R099 (NQ) and R100 (ES),
2009-06-01 to 2019-12-31. ORB1's check runs were to follow a pre-registration; ORB1 closed at its development rung
(D-252), and the same kit on the check years is ORB2's screen, R101 (NQ; D-253, D-254).

Each kit runs one market at actual prices on Topstep's trading day and exports one record per full session
(`propedge/outcomes/orb_core.py` `day_record`, embedded verbatim after `regime_core`): the ATR, the overnight gap and the
pre-open's move and volume, and for each of the 5-, 15-, 30- and 60-minute opening ranges (D-250) its direction, size
and relative volume, the signed drift 30, 60 and 120 minutes after it closes and at 15:08, and the paper's trade -- its
fill, its stop, its 15:08 close, and the first time each bracket target was traded through before the stop. Only these
records leave (D-120): no bars.

The body is the regime map's (`propedge/data/regime_kit.py`, version 3 bookkeeping, D-223) with named edits only: it
records each bar's close and every contract's volume in the minute; it keeps the previous 14 full sessions' true ranges,
each opening range's volume and the pre-open's (every contract's), and the previous session's close with its contract
(every day with bars, early closes too; never across a roll); it writes a day's record instead of the map's brackets.
A day without the 14-day histories writes nothing (`noatr`).
"""
from __future__ import annotations

import ast
import inspect
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from propedge import CONFIG_DIR
from propedge.data import regime_kit as rk

ORB_PREFIX = "OR1"
MARKETS = ("NQ", "ES")
ORB_RUNS = {m: f"R{99 + i:03d}-orb-{m}-dev" for i, m in enumerate(MARKETS)}
ORB_KITS = {v: k for k, v in ORB_RUNS.items()}
#: ORB2's screen (D-253): ORB1's kit, unchanged, on the check years -- NQ only
ORB2_SCREEN_RUNS = {"NQ": "R101-orb-NQ-2020"}


def config(path: Path | None = None) -> dict[str, Any]:
    return yaml.safe_load(Path(path or CONFIG_DIR / "orb_model.yaml").read_text(encoding="utf-8"))


def dates(run: str = "dev", cfg: dict | None = None) -> tuple[date, date, date]:
    d = (cfg or config())["runs"][run]
    return tuple(date.fromisoformat(str(d[k])) for k in ("warm", "start", "end"))


def params(market: str, cfg: dict | None = None) -> dict[str, Any]:
    cfg = cfg or config()
    mk, fx = cfg["markets"][market], cfg["fixed"]
    tick = float(mk["micro_tick"])
    rr = tuple(float(r) for r in cfg["exits"]["bracket"]["rr"])
    return {"market": market, "micro": mk["micro"], "tick": float(mk["tick"]), "micro_tick": tick,
            "micro_point_value": float(mk["micro_point_value"]), "rr": rr, "stop_atr": float(fx["stop_atr"]),
            "atr_days": int(fx["atr_days"]), "rv_days": int(fx["relative_volume"]["days"]),
            "rv_min": float(fx["relative_volume"]["min"]),
            "p": {"tick": tick, "slip": tick, "stop_atr": float(fx["stop_atr"]), "rr": rr}}


def _without_docstring(src: str) -> str:
    """A module's source without its leading docstring -- the kit must fit QuantConnect's 32,000-character editor; the
    conventions it states stay in the repository's file, which the kit names."""
    first = ast.parse(src).body[0]
    assert isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str)
    lines = src.splitlines(keepends=True)
    return "".join(lines[:first.lineno - 1] + lines[first.end_lineno:])


def _orb_source() -> str:
    """orb_core's source without its docstring and its import of regime_core, which the kit embeds just before it."""
    from propedge.outcomes import orb_core

    lines = _without_docstring(inspect.getsource(orb_core)).splitlines(keepends=True)
    imports = [ln for ln in lines if ln.startswith("from propedge")]
    assert len(imports) == 1, imports
    return "".join(ln for ln in lines if not ln.startswith("from propedge"))


def preamble(market: str, run: str = "dev") -> str:
    from propedge.outcomes import regime_core

    q = params(market)
    _, w0, w1 = dates(run)
    return f'''
MARKET = "{market}"
TICK = {q["tick"]!r}                    # the standard contract's tick (the data)
MICRO_TICK = {q["micro_tick"]!r}        # the micro's tick (slippage, stop sizes)
WIN_START = ({w0.year}, {w0.month}, {w0.day})   # days before this are warm-up: they fill the histories only
WIN_END = ({w1.year}, {w1.month}, {w1.day})
FILTER_DAYS = 120
PREFIX = "{ORB_PREFIX}"
LOG_BUDGET_BYTES = {rk.LOG_BUDGET_BYTES}
TAG_CHARS = {rk.REGIME_TAG_CHARS}
PARAMS = {q["p"]!r}
ATR_DAYS = {q["atr_days"]!r}
RV_DAYS = {q["rv_days"]!r}
FIXED_STOPS = []
RANGE_DAYS = 20
RANGE_MULTIPLES = []
WIDE_SPREAD_TICKS = 4.0
WIDE_SPREAD_CAP = 50.0
from datetime import timedelta as _delta


class CarrierInitializer(BrokerageModelSecurityInitializer):
    """Zero fees: the carrier orders' own P&L is never used, so nothing is modelled on them."""

    def initialize(self, security):
        super().initialize(security)
        security.set_fee_model(ConstantFeeModel(0))


# ---------------------------------------------------------------- embedded verbatim from
# ---------------------------------------------------------------- propedge/outcomes/regime_core.py (its docstring removed)
{_without_docstring(inspect.getsource(regime_core))}
# ---------------------------------------------------------------- propedge/outcomes/orb_core.py (its docstring and
# ---------------------------------------------------------------- import removed: the fill and walk conventions are there)
{_orb_source()}
# ---------------------------------------------------------------- end of the embedded cores
'''


_EDITS = (
    # every contract's volume in the minute, for the relative volumes (the pre-run review: a roll splits it)
    ('''    for sym, b in data.bars.items():
        if sym != self.future.symbol and sym.security_type == SecurityType.FUTURE:
            self._vol[sym] = self._vol.get(sym, 0.0) + float(b.volume)''',
     '''    self._vt = 0.0
    for sym, b in data.bars.items():
        if sym != self.future.symbol and sym.security_type == SecurityType.FUTURE:
            self._vol[sym] = self._vol.get(sym, 0.0) + float(b.volume)
            self._vt += float(b.volume)'''),
    ('''                         "l": [None] * (FLAT + 1), "q": [None] * (FLAT + 1), "v": [None] * (FLAT + 1)}''',
     '''                         "l": [None] * (FLAT + 1), "q": [None] * (FLAT + 1), "v": [None] * (FLAT + 1),
                         "cl": [None] * (FLAT + 1), "vt": [None] * (FLAT + 1)}'''),
    ('''    d["o"][j], d["h"][j], d["l"][j], d["v"][j] = o, h, l, float(bar.volume)''',
     '''    d["o"][j], d["h"][j], d["l"][j], d["v"][j], d["cl"][j] = o, h, l, float(bar.volume), cl
    d["vt"][j] = self._vt                        # ORB1: every contract's volume in this minute'''),
    ('''    self._noref, self._noatr, self._ranges = 0, 0, []''',
     '''    self._noref, self._noatr, self._ranges = 0, 0, []
    self._tr, self._prv, self._prev, self._recs, self._vt = [], [], None, [], 0.0   # ORB1
    self._orv = {n: [] for n in OR_MINS}      # ORB1: each range's volume history'''),
    ('''    o, h, l, q, v = d["o"], d["h"], d["l"], d["q"], d["v"]''',
     '''    o, h, l, q, v, cl, vt = d["o"], d["h"], d["l"], d["q"], d["v"], d["cl"], d["vt"]'''),
    # the 14-day histories, taken before today's day is added; the previous close never across a roll
    ('''    avg = sum(self._ranges) / len(self._ranges) if len(self._ranges) == RANGE_DAYS else None   # before this day
    rng = session_range(h, l, ls) if ok and not early else None
    if rng and not d.get("bad"):
        self._ranges = (self._ranges + [rng])[-RANGE_DAYS:]''',
     '''    prev = self._prev[0] if self._prev and self._prev[1] == d["c"] else None    # ORB1: never across a roll
    hist = {"atr": sum(self._tr) / len(self._tr) if len(self._tr) == ATR_DAYS else None,
            "or_vol": {n: (sum(x) / len(x) if len(x) == RV_DAYS else None) for n, x in self._orv.items()},
            "pre_vol": sum(self._prv) / len(self._prv) if len(self._prv) == RV_DAYS else None,
            "prev_close": prev}
    avg = hist["atr"] if (hist["atr"] and all(hist["or_vol"].values())) else None   # before this day
    rng = session_range(h, l, ls) if ok and not early else None
    if ok and not early and not d.get("bad"):
        tr = true_range(h, l, ls, prev)
        prw = window_stats(o, h, l, cl, vt, PRE_START, 5)
        if tr:
            self._tr = (self._tr + [tr])[-ATR_DAYS:]
        for n in OR_MINS:
            orw = window_stats(o, h, l, cl, vt, OR_START, n)
            if orw and orw[4] > 0:
                self._orv[n] = (self._orv[n] + [orw[4]])[-RV_DAYS:]
        if prw and prw[4] > 0:
            self._prv = (self._prv + [prw[4]])[-RV_DAYS:]
    if ok:                                       # the previous close: every day with bars, early closes too (review)
        lc = last_close_by(cl, ls)
        if lc is not None:
            self._prev = (lc, d["c"])'''),
    # the record's layout is D-250's (the four ranges): HEAD's version 2, so a D-249 output cannot pass for one
    ('''    head = (PREFIX + "|HEAD|v=1|market=" + MARKET + "|days=" + str(self._n) + "|warm=" + str(self._warm)''',
     '''    head = (PREFIX + "|HEAD|v=2|market=" + MARKET + "|days=" + str(self._n) + "|warm=" + str(self._warm)'''),
    (rk._COUNT,
     '''        if not avg:
            self._noatr += 1                     # ORB1: without the 14-day histories, no record
        else:
            rec = day_record(o, h, l, cl, vt, ls, PARAMS, hist)
            if rec is not None:
                self._entries += 1
                self._recs.append(encode_day(d["td"], rec))
        add_session(self._ses, year, rng, sum(x for x in v if x), avg, MICRO_TICK)
'''),
    ('''    cells = (["C" + x for x in encode_counts(self._acc)] + ["S" + x for x in encode_spreads(self._spr)]
             + ["W" + x for x in encode_windows(self._win)] + ["D" + x for x in encode_sessions(self._ses)])''',
     '''    cells = ["R" + x for x in self._recs] + ["D" + x for x in encode_sessions(self._ses)]
    self._recs = []'''),
)
BODY = rk.BODY
for _old, _new in _EDITS:
    assert BODY.count(_old) == 1, _old[:60]
    BODY = BODY.replace(_old, _new)
BODY = BODY.replace("# T15, D-238: the whole-day regime map at actual prices",
                    "# T15, D-249: ORB1's day records at actual prices, on the regime map's body")


__all__ = ["ORB_PREFIX", "MARKETS", "ORB_RUNS", "ORB_KITS", "ORB2_SCREEN_RUNS", "config", "dates", "params", "preamble",
           "BODY"]
