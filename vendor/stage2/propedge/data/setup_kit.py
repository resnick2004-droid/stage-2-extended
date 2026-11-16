"""The session-setup screen's QuantConnect kits (config/session_setups.yaml; T15 item 8, D-245): R097 NQ, R098 ES.

Each kit runs one market over the whole development period (2009-06-01 to 2025-06-30, D-237) on Topstep's trading day
at actual prices. On each full session it finds every rule's first signal in each window
(`propedge/outcomes/setup_core.py`, embedded verbatim after `regime_core`), enters at the next bar's open and walks the
bracket at each trailing-range stop to 1, 1.5, 2 and 3R, its stop, or the day's last bar. Only counts leave the cloud
(D-120), per calendar year, in order tags emitted at each year's end:

* `C` per window, rule, direction and stop: trades, stops that gapped and their overshoot, the stop's size, the entry
  minute's quoted spread, and per R the targets first, the stops first and the minutes to resolution;
* `D` per year: full sessions, their range and volume, and the trailing range.

The body is the regime map's (`propedge/data/regime_kit.py`, version 3 bookkeeping, D-223), changed only where named:
it records each bar's close; it keeps the previous full session's high and low with its contract -- the 17:00
window's prior range, used only on the same contract, never across a roll; an early close or a day with a bad bar does
not replace it -- and it counts setups instead of the map's brackets. A day without the trailing range counts nothing
(`noatr`).
"""
from __future__ import annotations

import inspect
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from propedge import CONFIG_DIR
from propedge.data import regime_kit as rk

SETUP_PREFIX = "SS1"
MARKETS = ("NQ", "ES")
SETUP_RUNS = {m: f"R{97 + i:03d}-setups-{m}" for i, m in enumerate(MARKETS)}
SETUP_KITS = {v: k for k, v in SETUP_RUNS.items()}


def config(path: Path | None = None) -> dict[str, Any]:
    return yaml.safe_load(Path(path or CONFIG_DIR / "session_setups.yaml").read_text(encoding="utf-8"))


def dates(cfg: dict | None = None) -> tuple[date, date, date]:
    d = (cfg or config())["dates"]
    return tuple(date.fromisoformat(str(d[k])) for k in ("warm", "start", "end"))


def start_slot(hm: str) -> int:
    """A window's start as minutes after 17:00 on the trading-day clock: 17:00 is 0 (a decision at slot t enters on
    the bar after it), 02:00 is 540, 08:30 is 930. Not `slot_of`, which keys a bar ENDING at 17:00 to the day before."""
    h, m = map(int, str(hm).split(":"))
    return (h * 60 + m - 17 * 60) % (24 * 60)


def params(market: str, cfg: dict | None = None) -> dict[str, Any]:
    cfg = cfg or config()
    mk = cfg["markets"][market]
    tick = float(mk["micro_tick"])
    windows = [(start_slot(w["start_ct"]), int(w["span_min"])) for w in cfg["windows"]]
    rr = tuple(sorted(float(r) for r in cfg["rr"]))
    rules = [str(r) for r in cfg["rules"]]
    return {"market": market, "micro": mk["micro"], "tick": float(mk["tick"]), "micro_tick": tick,
            "micro_point_value": float(mk["micro_point_value"]),
            "window_names": [str(w["name"]) for w in cfg["windows"]], "windows": windows, "rules": rules,
            "range_multiples": [float(x) for x in cfg["stops_range"]["multiples"]],
            "range_days": int(cfg["stops_range"]["days"]), "rr": rr,
            "spread": {"wide_ticks": float(cfg["spread"]["wide_ticks"]), "cap_ticks": float(cfg["spread"]["cap_ticks"])},
            "p": {"windows": windows, "rules": rules, "slip": tick, "rr": rr}}


def _setup_source() -> str:
    """setup_core's source without its import of regime_core, which the kit embeds just before it."""
    from propedge.outcomes import setup_core

    lines = inspect.getsource(setup_core).splitlines(keepends=True)
    imports = [ln for ln in lines if ln.startswith("from propedge")]
    assert len(imports) == 1, imports
    return "".join(ln for ln in lines if not ln.startswith("from propedge"))


def preamble(market: str) -> str:
    from propedge.outcomes import regime_core

    q = params(market)
    _, w0, w1 = dates()
    return f'''
MARKET = "{market}"
TICK = {q["tick"]!r}                    # the standard contract's tick (the data)
MICRO_TICK = {q["micro_tick"]!r}        # the micro's tick (slippage, spreads, stop sizes)
WIN_START = ({w0.year}, {w0.month}, {w0.day})   # days before this are warm-up: they fill the trailing range only
WIN_END = ({w1.year}, {w1.month}, {w1.day})
FILTER_DAYS = 120
PREFIX = "{SETUP_PREFIX}"
LOG_BUDGET_BYTES = {rk.LOG_BUDGET_BYTES}
TAG_CHARS = {rk.REGIME_TAG_CHARS}
PARAMS = {q["p"]!r}
FIXED_STOPS = []
RANGE_DAYS = {q["range_days"]!r}
RANGE_MULTIPLES = {q["range_multiples"]!r}
WIDE_SPREAD_TICKS = {q["spread"]["wide_ticks"]!r}   # D-215: counted (wide)
WIDE_SPREAD_CAP = {q["spread"]["cap_ticks"]!r}     # D-215: kept out of the mean, counted (badq)
from datetime import timedelta as _delta


class CarrierInitializer(BrokerageModelSecurityInitializer):
    """Zero fees: the carrier orders' own P&L is never used, so nothing is modelled on them."""

    def initialize(self, security):
        super().initialize(security)
        security.set_fee_model(ConstantFeeModel(0))


# ---------------------------------------------------------------- embedded verbatim from
# ---------------------------------------------------------------- propedge/outcomes/regime_core.py
{inspect.getsource(regime_core)}
# ---------------------------------------------------------------- propedge/outcomes/setup_core.py (its import removed)
{_setup_source()}
# ---------------------------------------------------------------- end of the embedded cores
'''


_EDITS = (
    # the bar's close is kept
    ('''                         "l": [None] * (FLAT + 1), "q": [None] * (FLAT + 1), "v": [None] * (FLAT + 1)}''',
     '''                         "l": [None] * (FLAT + 1), "q": [None] * (FLAT + 1), "v": [None] * (FLAT + 1),
                         "cl": [None] * (FLAT + 1)}'''),
    ('''    d["o"][j], d["h"][j], d["l"][j], d["v"][j] = o, h, l, float(bar.volume)''',
     '''    d["o"][j], d["h"][j], d["l"][j], d["v"][j], d["cl"][j] = o, h, l, float(bar.volume), cl'''),
    ('''    self._noref, self._noatr, self._ranges = 0, 0, []''',
     '''    self._noref, self._noatr, self._ranges, self._prev = 0, 0, [], None'''),
    ('''    o, h, l, q, v = d["o"], d["h"], d["l"], d["q"], d["v"]''',
     '''    o, h, l, q, v, cl = d["o"], d["h"], d["l"], d["q"], d["v"], d["cl"]'''),
    # the previous full session's high and low, for the 17:00 window's prior range
    ('''    if d["td"] < WIN_START or d["td"] > WIN_END:
        self._warm += 1
        return''',
     '''    hilo = session_hilo(h, l, ls) if ok and not early and not d.get("bad") else None
    last_full, self._prev = self._prev, ((hilo, d["c"]) if hilo else self._prev)
    # SS1: the 17:00 window's prior range is the last full session's, and only on the same contract -- never across a
    # roll, where the contracts' spread would read as a break (the pre-run review, B1)
    prev = last_full[0] if last_full and last_full[1] == d["c"] else None
    if d["td"] < WIN_START or d["td"] > WIN_END:
        self._warm += 1
        return'''),
    # setups are counted instead of the map's brackets
    (rk._COUNT,
     '''        if not avg:
            self._noatr += 1                     # SS1: no trailing range, no stop, nothing counted
        else:
            stops = range_stops(avg, RANGE_MULTIPLES, MICRO_TICK)
            rows = run_day(o, h, l, cl, PARAMS, stops, prev)
            self._entries += len(rows)
            add_trades(self._acc, year, rows, stops, PARAMS["rr"], MICRO_TICK, q)
        add_session(self._ses, year, rng, sum(x for x in v if x), avg, MICRO_TICK)
'''),
    ('''    cells = (["C" + x for x in encode_counts(self._acc)] + ["S" + x for x in encode_spreads(self._spr)]
             + ["W" + x for x in encode_windows(self._win)] + ["D" + x for x in encode_sessions(self._ses)])''',
     '''    cells = ["C" + x for x in encode_trades(self._acc)] + ["D" + x for x in encode_sessions(self._ses)]'''),
)
BODY = rk.BODY
for _old, _new in _EDITS:
    assert BODY.count(_old) == 1, _old[:60]
    BODY = BODY.replace(_old, _new)
BODY = BODY.replace("# T15, D-238: the whole-day regime map at actual prices",
                    "# T15, D-245: the session-setup screen SS1 at actual prices, on the regime map's body")


__all__ = ["SETUP_PREFIX", "MARKETS", "SETUP_RUNS", "SETUP_KITS", "config", "dates", "start_slot", "params",
           "preamble", "BODY"]
