"""The whole-day regime map's QuantConnect kits (config/regime_map.yaml; T15, D-237, D-238): R090-R094.

Each kit runs one market over the whole development period (2009-06-01 to 2025-06-30, D-237) on Topstep's trading day
(17:00 CT the evening before to the 15:10 CT flatten), at actual prices. At every decision -- every 30 minutes from
17:00 to 14:30 CT and every 5 minutes through the market's open -- a long and a short bracket at each fixed stop (points)
and each multiple of the trailing range, walked by `propedge/outcomes/regime_core` (embedded verbatim) to its target at
1, 1.5, 2 and 3R, its stop, or the day's last bar. Only counts leave the cloud (D-120), per calendar year, in order tags
emitted at each year's end:

* `C` per decision and stop: brackets, stops that gapped and their overshoot, the stop's size, and per R the targets
  first, the stops first and the minutes to resolution;
* `S` per decision: the entry minute's bid-ask spread in the micro's ticks;
* `W` per 30-minute window of the day: days, bars, volume and the window's range;
* `D` per year: full sessions, their range and volume, and the trailing range the range stops were cut from.

The kit's own choices, beside the resolution map's (`propedge/data/rmap_kit.py`, whose day, roll, spread and expired-
contract bookkeeping -- version 3, D-223 -- it keeps unchanged):

* **Actual prices** (D-238): no rescaling; a stop in points is what it was that year.
* **Early closes are not counted** (D-238): a day whose last bar ends before 15:00 CT is counted in `early` and adds no
  cell; nor does it enter the trailing range.
* **The trailing range** is the mean of the previous 20 full sessions' ranges (the day's own contract), warm-up days
  included, a day with a bad bar (`bad`: a low at or below zero, or a bar whose high and low do not hold its open and
  close) left out of it; a day without 20 before it counts the fixed stops only (`noatr`).
"""
from __future__ import annotations

import inspect
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from propedge import CONFIG_DIR

REGIME_PREFIX = "RG1"
REGIME_TAG_CHARS = 600
LOG_BUDGET_BYTES = 6000
MARKETS = ("NQ", "ES", "CL", "6E", "NG")
REGIME_RUNS = {m: f"R{90 + i:03d}-regime-{m}" for i, m in enumerate(MARKETS)}
REGIME_KITS = {v: k for k, v in REGIME_RUNS.items()}
TICKERS = {"ES": "ES", "NQ": "NQ", "CL": "CL", "6E": "6E", "NG": "NG"}


def config(path: Path | None = None) -> dict[str, Any]:
    return yaml.safe_load(Path(path or CONFIG_DIR / "regime_map.yaml").read_text(encoding="utf-8"))


def _hm(s: str) -> tuple[int, int]:
    h, m = str(s).split(":")
    return int(h), int(m)


def dates(cfg: dict | None = None) -> tuple[date, date, date]:
    """(warm-up start, window start, window end)."""
    d = (cfg or config())["dates"]
    return tuple(date.fromisoformat(str(d[k])) for k in ("warm", "start", "end"))


def params(market: str, cfg: dict | None = None) -> dict[str, Any]:
    """What the kit and the scorer need for a market: decision slots, fixed stops (points), range multiples, R, the
    micro's tick and point value."""
    from propedge.outcomes.regime_core import decision_slots, slot_of

    cfg = cfg or config()
    mk, w = cfg["markets"][market], cfg["window"]
    times = decision_slots(int(w["decision_every_min"]), slot_of(*_hm(w["last_decision_ct"])),
                           slot_of(*_hm(mk["open_ct"])), int(w["open_step_min"]), int(w["open_span_min"]))
    rr = tuple(sorted(float(r) for r in cfg["rr"]))
    tick = float(mk["micro_tick"])
    return {"market": market, "micro": mk["micro"], "tick": float(mk["tick"]), "micro_tick": tick,
            "micro_point_value": float(mk["micro_point_value"]), "open_ct": str(mk["open_ct"]),
            "stops_points": [float(x) for x in mk["stops_points"]],
            "range_multiples": [float(x) for x in cfg["stops_range"]["multiples"]],
            "range_days": int(cfg["stops_range"]["days"]),
            "spread": {"wide_ticks": float(cfg["spread"]["wide_ticks"]),
                       "cap_ticks": float(cfg["spread"]["cap_ticks"])},
            "times": times, "rr": rr, "p": {"times": times, "slip": tick, "rr": rr}}


def preamble(market: str) -> str:
    from propedge.outcomes import regime_core

    q = params(market)
    _, w0, w1 = dates()
    return f'''
MARKET = "{TICKERS[market]}"
TICK = {q["tick"]!r}                    # the standard contract's tick (the data)
MICRO_TICK = {q["micro_tick"]!r}        # the micro's tick (slippage, spreads, stop sizes)
WIN_START = ({w0.year}, {w0.month}, {w0.day})   # days before this are warm-up: they fill the trailing range only
WIN_END = ({w1.year}, {w1.month}, {w1.day})
FILTER_DAYS = 120
PREFIX = "{REGIME_PREFIX}"
LOG_BUDGET_BYTES = {LOG_BUDGET_BYTES}
TAG_CHARS = {REGIME_TAG_CHARS}
PARAMS = {q["p"]!r}
FIXED_STOPS = {q["stops_points"]!r}     # points, actual prices (D-238)
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
# ---------------------------------------------------------------- end of the embedded core
'''


BODY = """
def setup(self):
    # T15, D-238: the whole-day regime map at actual prices, measured in the cloud on Topstep's trading day; the
    # resolution map's contract bookkeeping, version 3 (D-223).
    self.set_time_zone(TimeZones.CHICAGO)
    self.set_cash(1000000)
    self.future = self.add_future(MARKET, Resolution.MINUTE,
                                  data_normalization_mode=DataNormalizationMode.RAW,
                                  data_mapping_mode=DataMappingMode.OPEN_INTEREST,
                                  contract_depth_offset=0,
                                  extended_market_hours=True)
    self.future.set_filter(0, FILTER_DAYS)
    self.set_security_initializer(CarrierInitializer(
        self.brokerage_model, FuncSecuritySeeder(self.get_last_known_prices)))
    self._active, self._vol = None, {}
    self._seen, self._prev_c = None, None
    self._day, self._rolled, self._done = None, None, False
    self._n, self._warm, self._switches, self._lost, self._late, self._entries = 0, 0, 0, 0, 0, 0
    self._orders, self._early, self._bad, self._bars, self._quotes, self._wide, self._badq = 0, 0, 0, 0, 0, 0, 0
    self._noref, self._noatr, self._ranges = 0, 0, []
    self._acc, self._spr, self._win, self._ses, self._year, self._emitted = {}, {}, {}, {}, None, 0

def _trading_day(self):
    t = self.time + _delta(hours=7)
    return (t.year, t.month, t.day)

def on_data(self, data):
    if self._done:
        return                                   # the window's last day has exported; nothing after it is read
    for sym, b in data.bars.items():
        if sym != self.future.symbol and sym.security_type == SecurityType.FUTURE:
            self._vol[sym] = self._vol.get(sym, 0.0) + float(b.volume)
    if self._active is not None and (self._active not in self.securities
                                     or self._active.id.date.date() < _date(*self._trading_day())):
        # D-223: a held contract past its expiry has no more bars; waiting for one froze version 2 (R079)
        self._active = None
        self._lost += 1
    c = self._active or self.future.mapped
    if c is None or c not in self.securities:
        return
    bar = self.securities[c].cache.get_data(TradeBar)
    if bar is None or (self._seen is not None and bar.end_time == self._seen and self._prev_c == c):
        return
    self._seen, self._prev_c = bar.end_time, c
    td = self._trading_day()
    if self._day is not None and self._day["td"] != td:
        closed = self._day["td"]
        self._close_day()
        if self._rolled != closed:               # no bar in the 15:10-17:00 gap: roll at the next day's first bar
            self._late += 1
            self._roll(c, closed)
            if (self._active or c) != c:
                return                           # this bar is the old contract's; the next is the new one's
        if self._done:
            return
    m = self.time.hour * 60 + self.time.minute
    if m > 17 * 60 or m <= 15 * 60 + 10:
        if self._day is None:
            self._day = {"td": td, "c": c.value, "o": [None] * (FLAT + 1), "h": [None] * (FLAT + 1),
                         "l": [None] * (FLAT + 1), "q": [None] * (FLAT + 1), "v": [None] * (FLAT + 1)}
        j = slot_of(self.time.hour, self.time.minute)
        if c.value == self._day["c"]:
            self._record(self._day, j, bar, c)
        if j == FLAT and self._day["td"] >= WIN_END:
            self._close_day()                    # the window's last day exports while its data still runs
    else:
        if self._day is not None:
            self._close_day()
        if self._rolled != td and not self._done:
            self._roll(c, td)

def _roll(self, c, td):
    day = _date(*td)
    cands = {s: v for s, v in self._vol.items() if s in self.securities and s.id.date.date() > day}
    nxt = max(cands, key=cands.get) if cands else c
    self._vol = {}
    self._rolled = td
    if nxt != c:
        self._switches += 1
    self._active = nxt

def _record(self, d, j, bar, c):
    if j < 1 or j > FLAT or d["o"][j] is not None:
        return
    o, h, l, cl = float(bar.open), float(bar.high), float(bar.low), float(bar.close)
    if not (0 < l <= min(o, cl) and max(o, cl) <= h):
        self._bad += 1
        d["bad"] = True                          # D-238: the day is walked but stays out of the trailing range
    d["o"][j], d["h"][j], d["l"][j], d["v"][j] = o, h, l, float(bar.volume)
    self._bars += 1
    qb = self.securities[c].cache.get_data(QuoteBar)
    if qb is None or qb.bid is None or qb.ask is None or qb.end_time != bar.end_time:
        return
    b, a = float(qb.bid.open), float(qb.ask.open)
    if b <= 0 or a <= 0 or a < b:
        return                                   # one-sided or crossed: not a spread
    ticks = (a - b) / MICRO_TICK
    if ticks > WIDE_SPREAD_CAP:
        self._badq += 1                          # far wider than a market quote: kept out of the mean, counted
        return
    if ticks > WIDE_SPREAD_TICKS:
        self._wide += 1
    d["q"][j] = a - b
    self._quotes += 1

def _close_day(self):
    d = self._day
    self._day = None
    o, h, l, q, v = d["o"], d["h"], d["l"], d["q"], d["v"]
    j = next((i for i in range(FLAT + 1) if o[i] is not None), None)
    ok = j is not None and o[j] > 0
    ls = last_slot(o)
    early = ls is not None and ls < FLAT - 10
    avg = sum(self._ranges) / len(self._ranges) if len(self._ranges) == RANGE_DAYS else None   # before this day
    rng = session_range(h, l, ls) if ok and not early else None
    if rng and not d.get("bad"):
        self._ranges = (self._ranges + [rng])[-RANGE_DAYS:]
    if d["td"] < WIN_START or d["td"] > WIN_END:
        self._warm += 1
        return
    year = d["td"][0]
    if self._year is not None and year != self._year:
        self._emit()
    self._year = year
    self._n += 1
    if not ok:
        self._noref += 1
    elif early:
        self._early += 1                         # D-238: an early close adds no cell
    else:
        if not avg:
            self._noatr += 1
        stops = FIXED_STOPS + range_stops(avg, RANGE_MULTIPLES, MICRO_TICK)
        rows = run_day(o, h, l, PARAMS, stops)
        self._entries += len(rows)
        add_day(self._acc, year, rows, stops, PARAMS["rr"], MICRO_TICK)
        add_spreads(self._spr, year, entry_spreads(o, q, PARAMS), MICRO_TICK)
        add_windows(self._win, year, window_stats(h, l, v, ls), MICRO_TICK)
        add_session(self._ses, year, rng, sum(x for x in v if x), avg, MICRO_TICK)
    if d["td"] >= WIN_END:
        self._emit()
        self._done = True

def _emit(self):
    # one year's (or the rest's) counts, in order tags of at most TAG_CHARS; the accumulators then start afresh.
    # C: brackets, S: spreads, W: 30-minute windows, D: sessions.
    cells = (["C" + x for x in encode_counts(self._acc)] + ["S" + x for x in encode_spreads(self._spr)]
             + ["W" + x for x in encode_windows(self._win)] + ["D" + x for x in encode_sessions(self._ses)])
    self._acc, self._spr, self._win, self._ses = {}, {}, {}, {}
    if not cells:
        return
    chunks, cur = [], ""
    for x in cells:
        if cur and len(cur) + 1 + len(x) > TAG_CHARS:
            chunks.append(cur)
            cur = x
        else:
            cur = x if not cur else cur + "/" + x
    chunks.append(cur)
    self._emitted += 1
    carrier = self._active or self.future.mapped
    for k, x in enumerate(chunks):
        tag = "G|e=" + str(self._emitted) + ";k=" + str(k) + ";K=" + str(len(chunks)) + ";x=" + x
        self._orders += 1
        self.market_order(carrier, 1 if self._orders % 2 else -1, tag=tag)

def on_end_of_algorithm(self):
    if self._day is not None and not self._done:
        self._close_day()
    if self._acc or self._spr or self._win or self._ses:
        self._emit()
    head = (PREFIX + "|HEAD|v=1|market=" + MARKET + "|days=" + str(self._n) + "|warm=" + str(self._warm)
            + "|entries=" + str(self._entries) + "|emits=" + str(self._emitted) + "|orders=" + str(self._orders)
            + "|switches=" + str(self._switches) + "|lost=" + str(self._lost) + "|late=" + str(self._late)
            + "|early=" + str(self._early) + "|noref=" + str(self._noref) + "|noatr=" + str(self._noatr)
            + "|bad=" + str(self._bad) + "|bars=" + str(self._bars) + "|quotes=" + str(self._quotes)
            + "|wide=" + str(self._wide) + "|badq=" + str(self._badq))
    self.log(head[:LOG_BUDGET_BYTES - 80])
    self.log(PREFIX + "|END")
"""


# ---------------------------------------------------------------- NQB2's confirmation (D-242)
# The kit that reads the held-back year once, for the registered pre-registration only: the map's body with nothing
# changed but what it counts -- each registered leg's one stop at its own R, at the registered decision times, by
# calendar month -- so no other cell of the window is counted; session cells carry the day count only (no range or
# volume), for the parser's check.
CONFIRM_RUNS = ("R095-regime-confirm-NQ-2026", "R096-regime-confirm-NQ-2026")    # the run, and its one permitted fix
CONFIRM_RUN = CONFIRM_RUNS[0]
_COUNT = """        if not avg:
            self._noatr += 1
        stops = FIXED_STOPS + range_stops(avg, RANGE_MULTIPLES, MICRO_TICK)
        rows = run_day(o, h, l, PARAMS, stops)
        self._entries += len(rows)
        add_day(self._acc, year, rows, stops, PARAMS["rr"], MICRO_TICK)
        add_spreads(self._spr, year, entry_spreads(o, q, PARAMS), MICRO_TICK)
        add_windows(self._win, year, window_stats(h, l, v, ls), MICRO_TICK)
        add_session(self._ses, year, rng, sum(x for x in v if x), avg, MICRO_TICK)
"""
assert BODY.count(_COUNT) == 1
BODY_CONFIRM = BODY.replace(_COUNT, """        block = year * 100 + d["td"][1]          # D-242: the registered legs only, counted by calendar month
        stops = [stop for stop, R in KEEP]
        for leg, (stop, R) in enumerate(KEEP):
            rows = run_day(o, h, l, {"times": PARAMS["times"], "slip": PARAMS["slip"], "rr": (R,)}, [stop])
            self._entries += len(rows)
            add_day(self._acc, block, [(ti, leg, dd, r) for ti, si, dd, r in rows], stops, (R,), MICRO_TICK)
        add_spreads(self._spr, block, entry_spreads(o, q, PARAMS), MICRO_TICK)
        add_session(self._ses, block, 0, 0, None, MICRO_TICK)    # the day count only
""")


def confirm_config(path: Path | None = None) -> dict[str, Any]:
    return yaml.safe_load(Path(path or CONFIG_DIR / "nqb2_confirmation.yaml").read_text(encoding="utf-8"))


def confirm_params(cfg: dict | None = None) -> dict[str, Any]:
    """The confirmation's parameters: the map's contract terms and rules (`params`) at the registered decision slots
    and legs; `keep` lists each leg's (stop in points, R), in the legs' order (combine, funded)."""
    c = cfg or confirm_config()
    base = params(c["market"])
    legs = [c["legs"][k] for k in ("combine", "funded")]
    keep = [(float(x["stop_points"]), float(x["R"])) for x in legs]
    times = [int(t) for t in c["decision_slots"]]
    rr = tuple(sorted({R for _, R in keep}))
    return dict(base, times=times, rr=rr, stops_points=[s for s, _ in keep], range_multiples=[], keep=keep,
                p={"times": times, "slip": base["micro_tick"], "rr": rr})


def confirm_dates(cfg: dict | None = None) -> tuple[date, date, date]:
    w = (cfg or confirm_config())["window"]
    return tuple(date.fromisoformat(str(w[k])) for k in ("warm", "start", "end"))


def confirm_preamble(cfg: dict | None = None) -> str:
    """The map's preamble at the confirmation's window and parameters, with KEEP."""
    from propedge.outcomes import regime_core

    c = cfg or confirm_config()
    q = confirm_params(c)
    _, w0, w1 = confirm_dates(c)
    return f'''
MARKET = "{TICKERS[c["market"]]}"
TICK = {q["tick"]!r}                    # the standard contract's tick (the data)
MICRO_TICK = {q["micro_tick"]!r}        # the micro's tick (slippage, spreads, stop sizes)
WIN_START = ({w0.year}, {w0.month}, {w0.day})   # days before this are warm-up and record nothing
WIN_END = ({w1.year}, {w1.month}, {w1.day})
FILTER_DAYS = 120
PREFIX = "{REGIME_PREFIX}"
LOG_BUDGET_BYTES = {LOG_BUDGET_BYTES}
TAG_CHARS = {REGIME_TAG_CHARS}
PARAMS = {q["p"]!r}
FIXED_STOPS = {q["stops_points"]!r}     # points, actual prices (D-238)
RANGE_DAYS = {q["range_days"]!r}
RANGE_MULTIPLES = []                    # D-242: no range stop is counted
KEEP = {[list(k) for k in q["keep"]]!r}   # D-242: each leg's (stop in points, R), combine then funded
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
# ---------------------------------------------------------------- end of the embedded core
'''


__all__ = ["REGIME_PREFIX", "REGIME_TAG_CHARS", "MARKETS", "REGIME_RUNS", "REGIME_KITS", "config", "dates", "params",
           "preamble", "BODY", "CONFIRM_RUNS", "CONFIRM_RUN", "BODY_CONFIRM", "confirm_config", "confirm_params",
           "confirm_dates", "confirm_preamble"]
