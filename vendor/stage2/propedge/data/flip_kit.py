"""The flip map's QuantConnect kit (config/flip_map.yaml; D-343): R137-flipmap-NQ.

One kit, NQ, 2020-01-01 to 2025-06-30 at actual prices, on Topstep's trading day (17:00 CT the evening before to the
15:10 CT flatten): at every hour start from 17:00 to 14:00 CT and at the 08:30 CT open, a long and a short bracket in one
NQ mini at each fixed width in points (1:1), entered on time (the slot's first bar's open) and one minute late (the next
bar's open), one tick adverse, read for at most `box_minutes` bars by `propedge/outcomes/flip_core` (embedded verbatim)
to its target, its stop, or a scratch at the box's last bar. Only counts leave the cloud (D-120): per year, slot, width
and entry delay the brackets at the target, at the stop and scratched, the minutes to resolution, how many resolved
within five minutes, the scratches' P&L in ticks, and per year and slot the entry minute's bid-ask spread in ticks.
They leave in order tags, a year's cells at the year's end.

The kit's day, roll, spread and early-close bookkeeping is the resolution map's version 3 (`propedge/data/rmap_kit.py`,
D-214, D-215, D-223), with the close of each bar recorded too (a scratch exits at a close) and no rescaling.
"""
from __future__ import annotations

import inspect
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from propedge import CONFIG_DIR

FLIP_PREFIX = "FM1"
FLIP_TAG_CHARS = 600
LOG_BUDGET_BYTES = 6000
FLIP_RUN = "R137-flipmap-NQ"


def config(path: Path | None = None) -> dict[str, Any]:
    return yaml.safe_load(Path(path or CONFIG_DIR / "flip_map.yaml").read_text(encoding="utf-8"))


def windows(cfg: dict | None = None) -> tuple[date, date, date]:
    """(warm-up start, window start, window end)."""
    cfg = cfg or config()
    return tuple(date.fromisoformat(str(cfg["window"][k])) for k in ("warm", "start", "end"))


def params(cfg: dict | None = None) -> dict[str, Any]:
    """What the kit and the scorer need: the decision slots (every hour start and the extra decisions, sorted), the
    widths in points, the tick, the slip, the box and the delays in bars, the contract's terms."""
    from propedge.outcomes.flip_core import slot_of

    cfg = cfg or config()
    day = cfg["day"]
    last = slot_of(*map(int, str(day["last_decision_ct"]).split(":")))
    times = set(range(0, last + 1, int(day["decision_every_min"])))
    for hm in day.get("extra_decisions_ct") or ():
        times.add(slot_of(*map(int, str(hm).split(":"))))
    times = sorted(times)
    k = cfg["contract"]
    tick = float(k["tick"])
    return {"market": str(cfg["market"]), "ticker": str(k["ticker"]), "tick": tick, "point_value": float(k["point_value"]),
            "micro": str(k["micro"]), "micro_point_value": float(k["micro_point_value"]),
            "widths_points": [float(x) for x in cfg["widths_points"]],
            "delays": [int(x) for x in cfg["entry_delays_min"]], "box": int(cfg["box_minutes"]),
            "within": int(cfg["within_minutes"]),
            "spread": {"wide_ticks": float(cfg["spread"]["wide_ticks"]), "cap_ticks": float(cfg["spread"]["cap_ticks"])},
            "p": {"times": times, "widths": [float(x) for x in cfg["widths_points"]], "slip": tick * float(cfg["slip_ticks"]),
                  "box": int(cfg["box_minutes"]), "delays": [int(x) for x in cfg["entry_delays_min"]]}}


def preamble(cfg: dict | None = None) -> str:
    from propedge.outcomes import flip_core

    cfg = cfg or config()
    q = params(cfg)
    _, w0, w1 = windows(cfg)
    return f'''
MARKET = "{q["ticker"]}"
TICK = {q["tick"]!r}                    # the contract's tick: the slip at entry and at a scratch exit, the spread's unit
WIN_START = ({w0.year}, {w0.month}, {w0.day})   # days before this are warm-up and record nothing
WIN_END = ({w1.year}, {w1.month}, {w1.day})
FILTER_DAYS = 120
PREFIX = "{FLIP_PREFIX}"
LOG_BUDGET_BYTES = {LOG_BUDGET_BYTES}
TAG_CHARS = {FLIP_TAG_CHARS}
PARAMS = {q["p"]!r}
WIDE_SPREAD_TICKS = {q["spread"]["wide_ticks"]!r}   # D-215: counted (wide)
WIDE_SPREAD_CAP = {q["spread"]["cap_ticks"]!r}     # D-215: kept out of the mean, counted (badq)
from datetime import timedelta as _delta


class CarrierInitializer(BrokerageModelSecurityInitializer):
    """Zero fees: the carrier orders' own P&L is never used, so nothing is modelled on them."""

    def initialize(self, security):
        super().initialize(security)
        security.set_fee_model(ConstantFeeModel(0))


# ---------------------------------------------------------------- embedded verbatim from
# ---------------------------------------------------------------- propedge/outcomes/flip_core.py
{inspect.getsource(flip_core)}
# ---------------------------------------------------------------- end of the embedded core
'''


BODY = """
def setup(self):
    # D-343: the flip map, measured in the cloud on Topstep's trading day; the resolution map's version 3 bookkeeping
    # (D-214, D-215, D-223) with each bar's close recorded and no rescaling (actual prices).
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
    self._noref = 0
    self._acc, self._acc_e, self._spr, self._year, self._emitted = {}, {}, {}, None, 0

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
                         "l": [None] * (FLAT + 1), "cl": [None] * (FLAT + 1), "q": [None] * (FLAT + 1)}
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
    d["o"][j], d["h"][j], d["l"][j], d["cl"][j] = o, h, l, cl
    self._bars += 1
    qb = self.securities[c].cache.get_data(QuoteBar)
    if qb is None or qb.bid is None or qb.ask is None or qb.end_time != bar.end_time:
        return
    b, a = float(qb.bid.open), float(qb.ask.open)
    if b <= 0 or a <= 0 or a < b:
        return                                   # one-sided or crossed: not a spread
    ticks = (a - b) / TICK
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
    if d["td"] < WIN_START or d["td"] > WIN_END:
        self._warm += 1
        return
    year = d["td"][0]
    if self._year is not None and year != self._year:
        self._emit()
    self._year = year
    self._n += 1
    o, h, l, cl, q = d["o"], d["h"], d["l"], d["cl"], d["q"]
    j = next((i for i in range(FLAT + 1) if o[i] is not None), None)
    if j is None or o[j] <= 0:
        self._noref += 1
    else:
        ls = last_slot(o)
        early = ls is not None and ls < FLAT - 10
        if early:
            self._early += 1                     # D-215: an early close's brackets are counted apart
        rows = run_day_flip(o, h, l, cl, PARAMS)
        self._entries += len(rows)
        add_day_flip(self._acc_e if early else self._acc, year, rows, TICK)
        add_spreads(self._spr, year, entry_spreads(o, q, PARAMS), TICK)
    if d["td"] >= WIN_END:
        self._emit()
        self._done = True

def _emit(self):
    # one year's (or the rest's) counts, in order tags of at most TAG_CHARS; the accumulators then start afresh.
    # C: full sessions, E: early closes (D-215), S: spreads.
    cells = (["C" + x for x in encode_flip(self._acc)] + ["E" + x for x in encode_flip(self._acc_e)]
             + ["S" + x for x in encode_spreads(self._spr)])
    self._acc, self._acc_e, self._spr = {}, {}, {}
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
        tag = "F|e=" + str(self._emitted) + ";k=" + str(k) + ";K=" + str(len(chunks)) + ";x=" + x
        self._orders += 1
        self.market_order(carrier, 1 if self._orders % 2 else -1, tag=tag)

def on_end_of_algorithm(self):
    if self._day is not None and not self._done:
        self._close_day()
    if self._acc or self._acc_e or self._spr:
        self._emit()
    head = (PREFIX + "|HEAD|v=1|market=" + MARKET + "|days=" + str(self._n) + "|warm=" + str(self._warm)
            + "|entries=" + str(self._entries) + "|emits=" + str(self._emitted) + "|orders=" + str(self._orders)
            + "|switches=" + str(self._switches) + "|lost=" + str(self._lost) + "|late=" + str(self._late)
            + "|early=" + str(self._early) + "|noref=" + str(self._noref) + "|bad=" + str(self._bad)
            + "|bars=" + str(self._bars) + "|quotes=" + str(self._quotes) + "|wide=" + str(self._wide)
            + "|badq=" + str(self._badq))
    self.log(head[:LOG_BUDGET_BYTES - 80])
    self.log(PREFIX + "|END")
"""


# ---------------------------------------------------------------- the second-resolution kit (D-344): R138-flipmap-NQ-seconds
# The minute map found the slots (08:30 and 09:00 CT) but its walk decides most of those brackets on their entry bar, a bar
# touching both sides being the stop's. This kit measures the same brackets on one-second bars for the two slots: the
# minute bars serve only the day's roll and early-close bookkeeping, and at each trading day's close one history request
# brings the window's second bars of the day's contract, walked by the same core. Trade bars only; the entry minute's
# spread is the minute kit's measurement, read by the scorer.
FLIP_SECONDS_RUN = "R138-flipmap-NQ-seconds"
FLIP_SECONDS_PREFIX = "FM2"
SECONDS_HEAD_EXTRA = ("secbars", "nosec", "short")                 # integer HEAD fields beyond the minute kit's
SECONDS_HEAD_TEXT = ("hform", "hempty", "hdt", "hshift", "hcols", "herr")   # diagnostic text fields: which history form
#                                       answered, which came back empty, the first bar's offset from the window's start, the
#                                       whole-hour shift applied to the frame's stamps (the data's time zone, not the
#                                       algorithm's), the frame's shape, the first error (an empty run says why)


def config_seconds(path: Path | None = None) -> dict[str, Any]:
    return yaml.safe_load(Path(path or CONFIG_DIR / "flip_map_seconds.yaml").read_text(encoding="utf-8"))


def windows_seconds(cfg: dict | None = None) -> tuple[date, date, date]:
    cfg = cfg or config_seconds()
    return tuple(date.fromisoformat(str(cfg["window"][k])) for k in ("warm", "start", "end"))


def params_seconds(cfg: dict | None = None) -> dict[str, Any]:
    """The second-resolution kit's parameters: the window (its start and length in seconds), the decision slots as
    second offsets from the window's start with their clock labels, the widths, the box, the five-minute line and the
    entry delays in seconds; the parser's prefix and HEAD fields."""
    cfg = cfg or config_seconds()
    w = cfg["window_ct"]
    h0, m0 = map(int, str(w["start"]).split(":"))
    h1, m1 = map(int, str(w["end"]).split(":"))
    length = (h1 * 60 + m1 - h0 * 60 - m0) * 60
    labels = [str(x) for x in cfg["slots_ct"]]
    times = [(int(x.split(":")[0]) * 60 + int(x.split(":")[1]) - h0 * 60 - m0) * 60 for x in labels]
    if any(t <= 0 or t >= length for t in times):
        raise ValueError("every slot must lie inside the window")
    k = cfg["contract"]
    tick = float(k["tick"])
    return {"market": str(cfg["market"]), "ticker": str(k["ticker"]), "tick": tick, "point_value": float(k["point_value"]),
            "window_ct": [str(w["start"]), str(w["end"])], "window_start_hm": (h0, m0), "window_seconds": length,
            "slot_labels": labels, "widths_points": [float(x) for x in cfg["widths_points"]],
            "delays": [int(x) for x in cfg["entry_delays_seconds"]], "box": int(cfg["box_seconds"]),
            "within": int(cfg["within_seconds"]), "time_unit": "second", "prefix": FLIP_SECONDS_PREFIX,
            "head_extra": list(SECONDS_HEAD_EXTRA), "head_text": list(SECONDS_HEAD_TEXT),
            "p": {"times": times, "widths": [float(x) for x in cfg["widths_points"]], "slip": tick * float(cfg["slip_ticks"]),
                  "box": int(cfg["box_seconds"]), "delays": [int(x) for x in cfg["entry_delays_seconds"]]}}


def preamble_seconds(cfg: dict | None = None) -> str:
    from propedge.outcomes import flip_core

    cfg = cfg or config_seconds()
    q = params_seconds(cfg)
    _, w0, w1 = windows_seconds(cfg)
    h0, m0 = q["window_start_hm"]
    return f'''
MARKET = "{q["ticker"]}"
TICK = {q["tick"]!r}                    # the contract's tick: the slip at entry and at a scratch exit
WIN_START = ({w0.year}, {w0.month}, {w0.day})   # days before this are warm-up and record nothing
WIN_END = ({w1.year}, {w1.month}, {w1.day})
FILTER_DAYS = 120
PREFIX = "{FLIP_SECONDS_PREFIX}"
LOG_BUDGET_BYTES = {LOG_BUDGET_BYTES}
TAG_CHARS = {FLIP_TAG_CHARS}
PARAMS = {q["p"]!r}
WIN_H0, WIN_M0 = {h0}, {m0}             # the window's start, CT: the second bars requested each day begin here
WINDOW_SECONDS = {q["window_seconds"]}  # the window's length; a slot is a second offset from its start (a bar's END time)
WITHIN_UNITS = {q["within"]}            # resolved within five minutes: by the end of this many one-second bars
from datetime import timedelta as _delta
from datetime import datetime as _dt


class CarrierInitializer(BrokerageModelSecurityInitializer):
    """Zero fees: the carrier orders' own P&L is never used, so nothing is modelled on them."""

    def initialize(self, security):
        super().initialize(security)
        security.set_fee_model(ConstantFeeModel(0))


def _clean(text):
    """A diagnostic string fit for a HEAD field: no field or record separators, no spaces, at most 160 characters."""
    out = "".join((ch if (ch.isalnum() or ch in ".,:_-[]()") else "_") for ch in str(text))
    return out[:160] if out else "none"


def iter_history_bars(hist):
    """(end time, open, high, low, close) per row of a history frame -- LEAN indexes a futures contract's history by
    (expiry, symbol, time), so the time is the LAST index level whatever the depth; columns open/high/low/close; nothing
    for an empty or missing frame. Written here so the fake LEAN loop of the tests can hand the same shape."""
    try:
        if hist is None or len(hist) == 0:
            return
        df = hist
        idx = df.index
        times = idx.get_level_values(-1) if getattr(idx, "nlevels", 1) > 1 else idx
        for t, bo, bh, bl, bc in zip(times, df["open"], df["high"], df["low"], df["close"]):
            if isinstance(t, tuple):
                t = t[-1]
            t = t.to_pydatetime() if hasattr(t, "to_pydatetime") else t
            yield t, float(bo), float(bh), float(bl), float(bc)
    except Exception:
        return


# ---------------------------------------------------------------- embedded verbatim from
# ---------------------------------------------------------------- propedge/outcomes/flip_core.py
{inspect.getsource(flip_core)}
# ---------------------------------------------------------------- end of the embedded core
WITHIN = WITHIN_UNITS                   # D-344: the core's five-minute line in this kit's units (one-second bars)
FLAT_MIN = FLAT                         # the minute clock's last bar (15:10 CT), for the day's minute bookkeeping
FLAT = WINDOW_SECONDS                   # the core's day end in THIS kit's units: the window's last second (the fourth run of
#                                         R138 never walked the 09:00 slot, which sat past the minute clock's 1,330)
'''


BODY_SECONDS = """
def setup(self):
    # D-344: the flip map at second resolution for the two open slots -- the resolution map's version 3 day and roll
    # bookkeeping on minute bars (D-214, D-215, D-223), and at each trading day's close one history request for the
    # window's second bars of the day's contract, walked by the embedded core; nothing else of the day is read.
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
    self._orders, self._early, self._bad, self._bars, self._nosec, self._secbars, self._short = 0, 0, 0, 0, 0, 0, 0
    self._noref = 0
    self._herr, self._hform, self._hcols, self._hdt, self._hempty, self._hshift = None, None, None, None, None, None
    self._acc, self._acc_e, self._year, self._emitted = {}, {}, None, 0

def _trading_day(self):
    t = self.time + _delta(hours=7)
    return (t.year, t.month, t.day)

def on_data(self, data):
    if self._done:
        return
    for sym, b in data.bars.items():
        if sym != self.future.symbol and sym.security_type == SecurityType.FUTURE:
            self._vol[sym] = self._vol.get(sym, 0.0) + float(b.volume)
    if self._active is not None and (self._active not in self.securities
                                     or self._active.id.date.date() < _date(*self._trading_day())):
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
        if self._rolled != closed:
            self._late += 1
            self._roll(c, closed)
            if (self._active or c) != c:
                return
        if self._done:
            return
    m = self.time.hour * 60 + self.time.minute
    if m > 17 * 60 or m <= 15 * 60 + 10:
        if self._day is None:
            self._day = {"td": td, "c": c.value, "sym": c, "o": [None] * (FLAT_MIN + 1)}
        j = slot_of(self.time.hour, self.time.minute)
        if c.value == self._day["c"] and 1 <= j <= FLAT_MIN and self._day["o"][j] is None:
            self._day["o"][j] = float(bar.open)
            self._bars += 1
        if j == FLAT_MIN and self._day["td"] >= WIN_END:
            self._close_day()
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

def _seconds(self, d):
    # the window's second bars of the day's contract, by one history request at the day's close: arrays indexed by the
    # second after the window's start (a bar's END time), None where no bar. Three request forms are tried in turn until
    # one returns bars; the first exception's text, the form that answered and the first frame's shape go to HEAD, so an
    # empty run says why (the second run of R138 came back empty with the reason swallowed).
    start = _dt(*d["td"]) + _delta(hours=WIN_H0, minutes=WIN_M0)
    end = start + _delta(seconds=WINDOW_SECONDS)
    n = WINDOW_SECONDS + 1
    o, h, l, cl = [None] * n, [None] * n, [None] * n, [None] * n
    sym = d["sym"]
    forms = (("sym", lambda: self.history(sym, start - _delta(seconds=1), end, Resolution.SECOND)),
             ("list", lambda: self.history([sym], start - _delta(seconds=1), end, Resolution.SECOND)),
             ("typed", lambda: self.history(TradeBar, sym, start - _delta(seconds=1), end, Resolution.SECOND)))
    hist, got = None, 0
    for name, call in forms:
        try:
            hist = call()
        except Exception as exc:
            if self._herr is None:
                self._herr = _clean(name + ":" + type(exc).__name__ + ":" + str(exc))
            continue
        if hist is not None and len(hist) > 0:
            if self._hform is None:
                self._hform = name
                try:
                    self._hcols = _clean("idx:" + ",".join(str(x) for x in (hist.index.names or [])) + " cols:"
                                         + ",".join(str(x) for x in list(hist.columns)[:8]))
                except Exception as exc:
                    self._hcols = _clean("shape:" + type(exc).__name__)
            break
        if self._hform is None and self._hempty is None:
            self._hempty = name
    if hist is None or len(hist) == 0:
        return o, h, l, cl, 0
    bars = []
    first = None
    for t, bo, bh, bl, bc in iter_history_bars(hist):
        k = int(round((t - start).total_seconds()))
        if first is None:
            first = k
        bars.append((k, bo, bh, bl, bc))
    if self._hdt is None and first is not None:
        self._hdt = first                            # the first bar's offset from the window's start, seconds
    # the frame's stamps are the data's time zone, not the algorithm's (the third run of R138: every bar one hour late):
    # the whole-hour shift that puts the most bars inside the window is taken, and recorded
    best_shift, best_in = 0, -1
    for shift in (0, 3600, -3600, 7200, -7200):
        inside = sum(1 for k, bo, bh, bl, bc in bars if 0 <= k - shift < n)
        if inside > best_in:
            best_shift, best_in = shift, inside
    if self._hshift is None:
        self._hshift = best_shift
    for k, bo, bh, bl, bc in bars:
        k -= best_shift
        if 0 <= k < n and o[k] is None and bo == bo and bo > 0:   # a quote-only second has no trade bar (NaN)
            o[k], h[k], l[k], cl[k] = bo, bh, bl, bc
            got += 1
    if got == 0 and self._herr is None:
        self._herr = _clean("rows:" + str(len(hist)) + ":first_offset:" + str(first) + ":shift:" + str(best_shift))
    return o, h, l, cl, got

def _close_day(self):
    d = self._day
    self._day = None
    if d["td"] < WIN_START or d["td"] > WIN_END:
        self._warm += 1
        return
    year = d["td"][0]
    if self._year is not None and year != self._year:
        self._emit()
    self._year = year
    self._n += 1
    ls = last_slot(d["o"])
    if ls is None:
        self._noref += 1
    else:
        early = ls < FLAT_MIN - 10
        if early:
            self._early += 1
        o, h, l, cl, got = self._seconds(d)
        self._secbars += got
        if got == 0:
            self._nosec += 1
        else:
            if got < WINDOW_SECONDS // 2:
                self._short += 1                     # a thin window: counted, still walked
            rows = run_day_flip(o, h, l, cl, PARAMS)
            self._entries += len(rows)
            add_day_flip(self._acc_e if early else self._acc, year, rows, TICK)   # WITHIN is the seconds line (the preamble)
    if d["td"] >= WIN_END:
        self._emit()
        self._done = True

def _emit(self):
    cells = (["C" + x for x in encode_flip(self._acc)] + ["E" + x for x in encode_flip(self._acc_e)])
    self._acc, self._acc_e = {}, {}
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
        tag = "F|e=" + str(self._emitted) + ";k=" + str(k) + ";K=" + str(len(chunks)) + ";x=" + x
        self._orders += 1
        self.market_order(carrier, 1 if self._orders % 2 else -1, tag=tag)

def on_end_of_algorithm(self):
    if self._day is not None and not self._done:
        self._close_day()
    if self._acc or self._acc_e:
        self._emit()
    head = (PREFIX + "|HEAD|v=1|market=" + MARKET + "|days=" + str(self._n) + "|warm=" + str(self._warm)
            + "|entries=" + str(self._entries) + "|emits=" + str(self._emitted) + "|orders=" + str(self._orders)
            + "|switches=" + str(self._switches) + "|lost=" + str(self._lost) + "|late=" + str(self._late)
            + "|early=" + str(self._early) + "|noref=" + str(self._noref) + "|bad=" + str(self._bad)
            + "|bars=" + str(self._bars) + "|quotes=0|wide=0|badq=0"
            + "|secbars=" + str(self._secbars) + "|nosec=" + str(self._nosec) + "|short=" + str(self._short)
            + "|hform=" + str(self._hform or "none") + "|hempty=" + str(self._hempty or "none")
            + "|hdt=" + str(self._hdt if self._hdt is not None else "none")
            + "|hshift=" + str(self._hshift if self._hshift is not None else "none")
            + "|hcols=" + str(self._hcols or "none") + "|herr=" + str(self._herr or "none"))
    self.log(head[:LOG_BUDGET_BYTES - 80])
    self.log(PREFIX + "|END")
"""


# ---------------------------------------------------------------- the flip-direction atlas (D-371): R142-flipdir-NQ
# The 08:30 flip is a coin flip; this kit asks whether anything known before 08:30 CT tells the side of the open's first
# move. On every trading day it records the minute bars' open, high, low and close (the measures read bars ending up to
# 08:30), carries each day's summary and the full-session range to the next day (ATR20), and at the day's close brings the
# 08:29-08:42 CT second bars by one history request (R138's, D-344) and walks the 08:30 brackets both ways at the day's
# widths -- fractions of ATR20 and the declared flip's fixed 20 points -- on time and one minute late. One record a day
# leaves the cloud (`flipdir_core.encode_day`): per-day numbers, never bars (D-120; the atlas's convention, D-126).
FLIPDIR_RUN = "R142-flipdir-NQ"
FLIPDIR_PREFIX = "FM3"
DIRECTION_HEAD_EXTRA = ("secbars", "nosec", "short", "records", "noatr", "noprev", "nomeas", "minwalk")


def config_direction(path: Path | None = None) -> dict[str, Any]:
    return yaml.safe_load(Path(path or CONFIG_DIR / "flip_direction.yaml").read_text(encoding="utf-8"))


def windows_direction(cfg: dict | None = None) -> tuple[date, date, date]:
    cfg = cfg or config_direction()
    return tuple(date.fromisoformat(str(cfg["window"][k])) for k in ("warm", "start", "end"))


def params_direction(cfg: dict | None = None) -> dict[str, Any]:
    """The direction kit's parameters: the second window and the slot as a second offset from its start, the ATR
    fractions and fixed widths (in ticks), which widths carry their seconds and scratch P&L (the primary fraction and
    the fixed flip), the box, the delays; the parser's prefix and HEAD fields."""
    cfg = cfg or config_direction()
    w = cfg["window_ct"]
    h0, m0 = map(int, str(w["start"]).split(":"))
    h1, m1 = map(int, str(w["end"]).split(":"))
    length = (h1 * 60 + m1 - h0 * 60 - m0) * 60
    sh, sm = map(int, str(cfg["slot_ct"]).split(":"))
    slot = (sh * 60 + sm - h0 * 60 - m0) * 60
    if not 0 < slot < length:
        raise ValueError("the slot must lie inside the window")
    k = cfg["contract"]
    tick = float(k["tick"])
    wd = cfg["widths"]
    fractions = [float(x) for x in wd["atr_fractions"]]
    fixed_ticks = [int(round(float(x) / tick)) for x in wd["fixed_points"]]
    primary = fractions.index(float(wd["primary_fraction"]))
    labels = [f"atr{f:g}" for f in fractions] + [f"pts{float(x):g}" for x in wd["fixed_points"]]
    delays = [int(x) for x in cfg["entry_delays_seconds"]]
    if delays[0] != 0 or int(cfg["box_seconds"]) + max(delays) + slot >= length:
        raise ValueError("the window must hold the on-time entry, the late entry and the box")
    return {"market": str(cfg["market"]), "ticker": str(k["ticker"]), "tick": tick, "point_value": float(k["point_value"]),
            "window_ct": [str(w["start"]), str(w["end"])], "window_start_hm": (h0, m0), "window_seconds": length,
            "slot_ct": str(cfg["slot_ct"]), "slot": slot, "fractions": fractions, "fixed_ticks": fixed_ticks,
            "min_ticks": int(wd["min_ticks"]), "atr_days": int(cfg["atr_days"]), "width_labels": labels,
            "primary": primary, "extra_widths": [primary, len(fractions)], "delays": delays,
            "box": int(cfg["box_seconds"]), "within": int(cfg["within_seconds"]), "time_unit": "second",
            "prefix": FLIPDIR_PREFIX, "head_extra": list(DIRECTION_HEAD_EXTRA), "head_text": list(SECONDS_HEAD_TEXT),
            "min_slot": 930, "min_box": int(cfg["box_seconds"]) // 60, "min_delays": [d // 60 for d in delays],
            "p": {"times": [slot], "slip": tick * float(cfg["slip_ticks"]), "box": int(cfg["box_seconds"]),
                  "delays": delays}}


def preamble_direction(cfg: dict | None = None) -> str:
    from propedge.outcomes import flip_core, flipdir_core

    cfg = cfg or config_direction()
    q = params_direction(cfg)
    _, w0, w1 = windows_direction(cfg)
    h0, m0 = q["window_start_hm"]
    return f'''
MARKET = "{q["ticker"]}"
TICK = {q["tick"]!r}                    # the contract's tick: the measures' unit, the slip at entry and at a scratch exit
WIN_START = ({w0.year}, {w0.month}, {w0.day})   # days before this are warm-up: they feed ATR20 and the previous day, nothing leaves
WIN_END = ({w1.year}, {w1.month}, {w1.day})
FILTER_DAYS = 120
PREFIX = "{FLIPDIR_PREFIX}"
LOG_BUDGET_BYTES = {LOG_BUDGET_BYTES}
TAG_CHARS = {FLIP_TAG_CHARS}
PARAMS = {q["p"]!r}
FRACTIONS = {q["fractions"]!r}          # the 1:1 widths as fractions of ATR20
FIXED_TICKS = {q["fixed_ticks"]!r}      # the declared flip's fixed width, in ticks
MIN_TICKS = {q["min_ticks"]}
ATR_DAYS = {q["atr_days"]}
DELAYS = {q["delays"]!r}
EXTRA_WIDTHS = {q["extra_widths"]!r}    # the widths whose seconds and scratch P&L travel in the record
MIN_SLOT = {q["min_slot"]}             # the fallback walk (a day the history cannot serve): the decision on the minute clock,
MIN_BOX = {q["min_box"]}               #   the box in minute bars, and the delays in minute bars beside the seconds' DELAYS
MIN_DELAYS = {q["min_delays"]!r}
WIN_H0, WIN_M0 = {h0}, {m0}             # the window's start, CT: the second bars requested each day begin here
WINDOW_SECONDS = {q["window_seconds"]}  # the window's length; the slot is a second offset from its start (a bar's END time)
WITHIN_UNITS = {q["within"]}
from datetime import timedelta as _delta
from datetime import datetime as _dt


class CarrierInitializer(BrokerageModelSecurityInitializer):
    """Zero fees: the carrier orders' own P&L is never used, so nothing is modelled on them."""

    def initialize(self, security):
        super().initialize(security)
        security.set_fee_model(ConstantFeeModel(0))


def _clean(text):
    """A diagnostic string fit for a HEAD field: no field or record separators, no spaces, at most 160 characters."""
    out = "".join((ch if (ch.isalnum() or ch in ".,:_-[]()") else "_") for ch in str(text))
    return out[:160] if out else "none"


def iter_history_bars(hist):
    """(end time, open, high, low, close) per row of a history frame -- the time is the LAST index level whatever the
    depth (LEAN's futures history is indexed by expiry, symbol, time); nothing for an empty or missing frame."""
    try:
        if hist is None or len(hist) == 0:
            return
        df = hist
        idx = df.index
        times = idx.get_level_values(-1) if getattr(idx, "nlevels", 1) > 1 else idx
        for t, bo, bh, bl, bc in zip(times, df["open"], df["high"], df["low"], df["close"]):
            if isinstance(t, tuple):
                t = t[-1]
            t = t.to_pydatetime() if hasattr(t, "to_pydatetime") else t
            yield t, float(bo), float(bh), float(bl), float(bc)
    except Exception:
        return


# ---------------------------------------------------------------- embedded verbatim from
# ---------------------------------------------------------------- propedge/outcomes/flip_core.py
{inspect.getsource(flip_core)}
# ---------------------------------------------------------------- end of the embedded core
# ---------------------------------------------------------------- embedded verbatim from
# ---------------------------------------------------------------- propedge/outcomes/flipdir_core.py
{inspect.getsource(flipdir_core)}
# ---------------------------------------------------------------- end of the embedded core
WITHIN = WITHIN_UNITS                   # the walk's five-minute line in this kit's units (one-second bars)
FLAT_MIN = FLAT                         # the minute clock's last bar (15:10 CT): the day's minute bookkeeping
FLAT = WINDOW_SECONDS                   # the walk's day end in THIS kit's units: the window's last second
'''


BODY_DIRECTION = """
def setup(self):
    # D-371: the flip-direction atlas -- the resolution map's version 3 day and roll bookkeeping on minute bars (D-214,
    # D-215, D-223) with each bar's open, high, low and close recorded for the measures, the previous day's summary and
    # ATR20 carried day to day, and at each trading day's close R138's history request for the 08:29-08:42 CT second bars
    # of the day's contract, walked by the embedded core; one record a day leaves.
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
    self._orders, self._early, self._bad, self._bars, self._nosec, self._secbars, self._short = 0, 0, 0, 0, 0, 0, 0
    self._noref, self._records, self._noatr, self._noprev, self._nomeas, self._minwalk = 0, 0, 0, 0, 0, 0
    self._herr, self._hform, self._hcols, self._hdt, self._hempty, self._hshift = None, None, None, None, None, None
    self._recs, self._year, self._emitted = [], None, 0
    self._prev, self._ranges = None, []

def _trading_day(self):
    t = self.time + _delta(hours=7)
    return (t.year, t.month, t.day)

def on_data(self, data):
    if self._done:
        return
    for sym, b in data.bars.items():
        if sym != self.future.symbol and sym.security_type == SecurityType.FUTURE:
            self._vol[sym] = self._vol.get(sym, 0.0) + float(b.volume)
    if self._active is not None and (self._active not in self.securities
                                     or self._active.id.date.date() < _date(*self._trading_day())):
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
        if self._rolled != closed:
            self._late += 1
            self._roll(c, closed)
            if (self._active or c) != c:
                return
        if self._done:
            return
    m = self.time.hour * 60 + self.time.minute
    if m > 17 * 60 or m <= 15 * 60 + 10:
        if self._day is None:
            n = FLAT_MIN + 1
            self._day = {"td": td, "c": c.value, "sym": c, "o": [None] * n, "h": [None] * n, "l": [None] * n,
                         "cl": [None] * n}
        j = slot_of(self.time.hour, self.time.minute)
        d = self._day
        if c.value == d["c"] and 1 <= j <= FLAT_MIN and d["o"][j] is None:
            o, h, l, cl = float(bar.open), float(bar.high), float(bar.low), float(bar.close)
            if not (0 < l <= min(o, cl) and max(o, cl) <= h):
                self._bad += 1
            d["o"][j], d["h"][j], d["l"][j], d["cl"][j] = o, h, l, cl
            self._bars += 1
        if j == FLAT_MIN and d["td"] >= WIN_END:
            self._close_day()
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

def _seconds(self, d):
    # R138's request (D-344): the window's second bars of the day's contract at the day's close, three request forms
    # tried in turn, the data's whole-hour time-zone shift detected and removed; arrays indexed by the second after the
    # window's start (a bar's END time), None where no bar.
    start = _dt(*d["td"]) + _delta(hours=WIN_H0, minutes=WIN_M0)
    end = start + _delta(seconds=WINDOW_SECONDS)
    n = WINDOW_SECONDS + 1
    o, h, l, cl = [None] * n, [None] * n, [None] * n, [None] * n
    sym = d["sym"]
    forms = (("sym", lambda: self.history(sym, start - _delta(seconds=1), end, Resolution.SECOND)),
             ("list", lambda: self.history([sym], start - _delta(seconds=1), end, Resolution.SECOND)),
             ("typed", lambda: self.history(TradeBar, sym, start - _delta(seconds=1), end, Resolution.SECOND)))
    hist, got = None, 0
    for name, call in forms:
        try:
            hist = call()
        except Exception as exc:
            if self._herr is None:
                self._herr = _clean(name + ":" + type(exc).__name__ + ":" + str(exc))
            continue
        if hist is not None and len(hist) > 0:
            if self._hform is None:
                self._hform = name
                try:
                    self._hcols = _clean("idx:" + ",".join(str(x) for x in (hist.index.names or [])) + " cols:"
                                         + ",".join(str(x) for x in list(hist.columns)[:8]))
                except Exception as exc:
                    self._hcols = _clean("shape:" + type(exc).__name__)
            break
        if self._hform is None and self._hempty is None:
            self._hempty = name
    if hist is None or len(hist) == 0:
        return o, h, l, cl, 0
    bars = []
    first = None
    for t, bo, bh, bl, bc in iter_history_bars(hist):
        k = int(round((t - start).total_seconds()))
        if first is None:
            first = k
        bars.append((k, bo, bh, bl, bc))
    if self._hdt is None and first is not None:
        self._hdt = first
    best_shift, best_in = 0, -1
    for shift in (0, 3600, -3600, 7200, -7200):
        inside = sum(1 for k, bo, bh, bl, bc in bars if 0 <= k - shift < n)
        if inside > best_in:
            best_shift, best_in = shift, inside
    if self._hshift is None:
        self._hshift = best_shift
    for k, bo, bh, bl, bc in bars:
        k -= best_shift
        if 0 <= k < n and o[k] is None and bo == bo and bo > 0:
            o[k], h[k], l[k], cl[k] = bo, bh, bl, bc
            got += 1
    if got == 0 and self._herr is None:
        self._herr = _clean("rows:" + str(len(hist)) + ":first_offset:" + str(first) + ":shift:" + str(best_shift))
    return o, h, l, cl, got

def _close_day(self):
    d = self._day
    self._day = None
    if d["td"] > WIN_END:
        return
    in_win = d["td"] >= WIN_START
    o, h, l, cl = d["o"], d["h"], d["l"], d["cl"]
    lsm = _last_at_or_before(o, FLAT_MIN)
    if not in_win:
        self._warm += 1
    if lsm is None:
        if in_win:
            self._n += 1
            self._noref += 1
        return
    early = lsm < FLAT_MIN - 10
    summ = day_summary(o, h, l, cl)
    prev = self._prev["s"] if (self._prev is not None and self._prev["c"] == d["c"]) else None
    if in_win:
        year = d["td"][0]
        if self._year is not None and year != self._year:
            self._emit()
        self._year = year
        self._n += 1
        if early:
            self._early += 1
        m = day_measures(o, h, l, cl, prev, TICK)
        atr = int(round(sum(self._ranges) / len(self._ranges))) if len(self._ranges) >= ATR_DAYS else None
        if atr is None:
            self._noatr += 1
        if prev is None:
            self._noprev += 1
        wt = day_widths(atr, FRACTIONS, FIXED_TICKS, MIN_TICKS)
        walked = [(i, w) for i, w in enumerate(wt) if w is not None]
        outs = "-" * (len(wt) * len(DELAYS) * len(DIR_SIDES))
        ex = [None] * (2 * len(DIR_SIDES) * len(EXTRA_WIDTHS))
        res = 0
        if m is None:
            self._nomeas += 1
        else:
            so, sh, sl, sc, got = self._seconds(d)
            self._secbars += got
            if got == 0:
                self._nosec += 1
                # D-371: a day the history cannot serve is walked on its own minute bars -- a bar touching both sides is
                # the stop's for both, so such a day can dilute an effect, never make one; flagged in the record
                rows = self._minute_rows(o, h, l, cl, walked, lsm)
                if rows:
                    res = 2
                    self._minwalk += 1
            else:
                if got < WINDOW_SECONDS // 2:
                    self._short += 1
                P = dict(PARAMS)
                P["widths"] = [w * TICK for _, w in walked]
                rows = run_day_flip(so, sh, sl, sc, P)
                res = 1
            self._entries += len(rows)
            outs, ex = day_outcomes(rows, [i for i, _ in walked], len(wt), DELAYS, TICK, EXTRA_WIDTHS)
        self._recs.append(encode_day(d["td"], 1 if early else 0, 1 if prev is not None else 0, atr, res, m, wt, outs,
                                     ex))
        self._records += 1
    # the day's summary and its full-session range carry to the next day, warm-up days included
    self._prev = {"c": d["c"], "s": summ} if summ is not None else None
    if summ is not None and not early and summ["hi"] is not None and summ["lo"] is not None:
        self._ranges.append(int(round((summ["hi"] - summ["lo"]) / TICK)))
        self._ranges = self._ranges[-ATR_DAYS:]
    if d["td"] >= WIN_END:
        self._emit()
        self._done = True

def _minute_rows(self, o, h, l, cl, walked, last):
    # the fallback walk on the day's minute bars, in run_day_flip's row shape with the seconds' delay labels and the
    # minutes counted in seconds
    rows = []
    widths = [w * TICK for _, w in walked]
    for dl_s, dl_m in zip(DELAYS, MIN_DELAYS):
        for side in DIR_SIDES:
            r = walk_boxed(o, h, l, cl, MIN_SLOT, side, widths, PARAMS["slip"], last, MIN_BOX, dl_m)
            if r is None:
                continue
            for wi, (j0, kind, units, x) in enumerate(r):
                rows.append((0, wi, dl_s, side, kind, units * 60, x))
    return rows

def _emit(self):
    cells = self._recs
    self._recs = []
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
        tag = "F|e=" + str(self._emitted) + ";k=" + str(k) + ";K=" + str(len(chunks)) + ";x=" + x
        self._orders += 1
        self.market_order(carrier, 1 if self._orders % 2 else -1, tag=tag)

def on_end_of_algorithm(self):
    if self._day is not None and not self._done:
        self._close_day()
    if self._recs:
        self._emit()
    head = (PREFIX + "|HEAD|v=1|market=" + MARKET + "|days=" + str(self._n) + "|warm=" + str(self._warm)
            + "|entries=" + str(self._entries) + "|emits=" + str(self._emitted) + "|orders=" + str(self._orders)
            + "|switches=" + str(self._switches) + "|lost=" + str(self._lost) + "|late=" + str(self._late)
            + "|early=" + str(self._early) + "|noref=" + str(self._noref) + "|bad=" + str(self._bad)
            + "|bars=" + str(self._bars) + "|quotes=0|wide=0|badq=0"
            + "|secbars=" + str(self._secbars) + "|nosec=" + str(self._nosec) + "|short=" + str(self._short)
            + "|records=" + str(self._records) + "|noatr=" + str(self._noatr) + "|noprev=" + str(self._noprev)
            + "|nomeas=" + str(self._nomeas) + "|minwalk=" + str(self._minwalk)
            + "|hform=" + str(self._hform or "none") + "|hempty=" + str(self._hempty or "none")
            + "|hdt=" + str(self._hdt if self._hdt is not None else "none")
            + "|hshift=" + str(self._hshift if self._hshift is not None else "none")
            + "|hcols=" + str(self._hcols or "none") + "|herr=" + str(self._herr or "none"))
    self.log(head[:LOG_BUDGET_BYTES - 80])
    self.log(PREFIX + "|END")
"""


# ---------------------------------------------------------------- the any-time direction atlas (D-373): R143-flipany-NQ
# The measures at every half hour of the regular session and a 1:1 bracket both ways at each slot, sized to that slot's
# typical ten-minute range over the previous 20 days; one second-bar history request a slot (R138's method). One record
# a day leaves (`flipany_core.any_record`): per slot the widths, the measures and the outcomes (D-120).
FLIPANY_RUN = "R143-flipany-NQ"
FLIPANY_PREFIX = "FM4"
ANYTIME_HEAD_EXTRA = ("secbars", "nosec", "short", "records", "nomeas", "small", "closed", "nohist", "walked")


def config_anytime(path: Path | None = None) -> dict[str, Any]:
    return yaml.safe_load(Path(path or CONFIG_DIR / "flip_anytime.yaml").read_text(encoding="utf-8"))


def windows_anytime(cfg: dict | None = None) -> tuple[date, date, date]:
    cfg = cfg or config_anytime()
    return tuple(date.fromisoformat(str(cfg["window"][k])) for k in ("warm", "start", "end"))


def params_anytime(cfg: dict | None = None) -> dict[str, Any]:
    """The any-time kit's parameters: the slots on the minute clock with their CT labels and their windows' starts, the
    width fractions, the minimum width, the walk's parameters (the slot a `pre_seconds` offset into each window)."""
    from propedge.outcomes.flip_core import slot_of

    cfg = cfg or config_anytime()
    labels = [str(x) for x in cfg["slots_ct"]]
    slots = [slot_of(*map(int, x.split(":"))) for x in labels]
    pre, length, box = int(cfg["pre_seconds"]), int(cfg["window_seconds"]), int(cfg["box_seconds"])
    delays = [int(x) for x in cfg["entry_delays_seconds"]]
    if delays[0] != 0 or pre + box + max(delays) >= length:
        raise ValueError("each window must hold the on-time entry, the late entry and the box")
    if max(slots) + 11 > 22 * 60 + 10:
        raise ValueError("every slot's box must end before the 15:10 CT flatten")
    k = cfg["contract"]
    tick = float(k["tick"])
    wd = cfg["widths"]
    fractions = [float(x) for x in wd["range_fractions"]]
    if fractions.index(float(wd["primary_fraction"])) != 0:
        raise ValueError("the primary width must be the first fraction (its seconds and scratch travel in the record)")
    return {"market": str(cfg["market"]), "ticker": str(k["ticker"]), "tick": tick, "point_value": float(k["point_value"]),
            "slot_labels": labels, "slots": slots, "pre_seconds": pre, "window_seconds": length, "fractions": fractions,
            "primary": fractions.index(float(wd["primary_fraction"])), "min_ticks": int(wd["min_ticks"]),
            "range_days": int(cfg["range_days"]), "delays": delays, "box": box, "time_unit": "second",
            "width_labels": [f"r{f:g}" for f in fractions],
            "prefix": FLIPANY_PREFIX, "head_extra": list(ANYTIME_HEAD_EXTRA), "head_text": list(SECONDS_HEAD_TEXT),
            "p": {"times": [pre], "slip": tick * float(cfg["slip_ticks"]), "box": box, "delays": delays}}


def preamble_anytime(cfg: dict | None = None) -> str:
    from propedge.outcomes import flip_core, flipany_core

    cfg = cfg or config_anytime()
    q = params_anytime(cfg)
    _, w0, w1 = windows_anytime(cfg)
    return f'''
MARKET = "{q["ticker"]}"
TICK = {q["tick"]!r}
WIN_START = ({w0.year}, {w0.month}, {w0.day})   # earlier days are warm-up: they feed the widths' history, nothing leaves
WIN_END = ({w1.year}, {w1.month}, {w1.day})
FILTER_DAYS = 120
PREFIX = "{FLIPANY_PREFIX}"
LOG_BUDGET_BYTES = {LOG_BUDGET_BYTES}
TAG_CHARS = {FLIP_TAG_CHARS}
PARAMS = {q["p"]!r}
SLOTS = {q["slots"]!r}                  # the decision slots on the minute clock (bar END times after 17:00 CT)
FRACTIONS = {q["fractions"]!r}          # the widths: fractions of the slot's mean ten-minute range
MIN_TICKS = {q["min_ticks"]}
RANGE_DAYS = {q["range_days"]}
DELAYS = {q["delays"]!r}
PRE_SECONDS = {q["pre_seconds"]}        # a slot's window starts this many seconds before it ...
WINDOW_SECONDS = {q["window_seconds"]}  # ... and runs this long
from datetime import timedelta as _delta
from datetime import datetime as _dt


class CarrierInitializer(BrokerageModelSecurityInitializer):
    """Zero fees: the carrier orders' own P&L is never used."""

    def initialize(self, security):
        super().initialize(security)
        security.set_fee_model(ConstantFeeModel(0))


def _clean(text):
    out = "".join((ch if (ch.isalnum() or ch in ".,:_-[]()") else "_") for ch in str(text))
    return out[:160] if out else "none"


def iter_history_bars(hist):
    """(end time, open, high, low, close) per row; the time is the LAST index level (expiry, symbol, time)."""
    try:
        if hist is None or len(hist) == 0:
            return
        idx = hist.index
        times = idx.get_level_values(-1) if getattr(idx, "nlevels", 1) > 1 else idx
        for t, bo, bh, bl, bc in zip(times, hist["open"], hist["high"], hist["low"], hist["close"]):
            if isinstance(t, tuple):
                t = t[-1]
            t = t.to_pydatetime() if hasattr(t, "to_pydatetime") else t
            yield t, float(bo), float(bh), float(bl), float(bc)
    except Exception:
        return


# ---------------------------------------------------------------- embedded verbatim from
# ---------------------------------------------------------------- propedge/outcomes/flip_core.py
{inspect.getsource(flip_core)}
# ---------------------------------------------------------------- end of the embedded core
# ---------------------------------------------------------------- embedded verbatim from
# ---------------------------------------------------------------- propedge/outcomes/flipany_core.py
{inspect.getsource(flipany_core)}
# ---------------------------------------------------------------- end of the embedded core
FLAT_MIN = FLAT                         # the minute clock's last bar (15:10 CT)
FLAT = WINDOW_SECONDS                   # the walk's day end in THIS kit's units: a window's last second
'''


BODY_ANYTIME = """
def setup(self):
    # D-373: the any-time atlas -- the resolution map's version 3 day and roll bookkeeping on minute bars (D-214, D-215,
    # D-223) with each bar recorded, the previous day's summary and each slot's ten-minute ranges carried day to day,
    # and at each day's close one second-bar history request a slot, walked by the embedded core; one record a day.
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
    self._orders, self._early, self._bad, self._bars, self._nosec, self._secbars, self._short = 0, 0, 0, 0, 0, 0, 0
    self._noref, self._records, self._nomeas, self._small, self._closed, self._nohist, self._walked = 0, 0, 0, 0, 0, 0, 0
    self._herr, self._hform, self._hcols, self._hdt, self._hempty, self._hshift = None, None, None, None, None, None
    self._recs, self._year, self._emitted = [], None, 0
    self._prev, self._r10 = None, [[] for _ in SLOTS]

def _trading_day(self):
    t = self.time + _delta(hours=7)
    return (t.year, t.month, t.day)

def on_data(self, data):
    if self._done:
        return
    for sym, b in data.bars.items():
        if sym != self.future.symbol and sym.security_type == SecurityType.FUTURE:
            self._vol[sym] = self._vol.get(sym, 0.0) + float(b.volume)
    if self._active is not None and (self._active not in self.securities
                                     or self._active.id.date.date() < _date(*self._trading_day())):
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
        if self._rolled != closed:
            self._late += 1
            self._roll(c, closed)
            if (self._active or c) != c:
                return
        if self._done:
            return
    m = self.time.hour * 60 + self.time.minute
    if m > 17 * 60 or m <= 15 * 60 + 10:
        if self._day is None:
            n = FLAT_MIN + 1
            self._day = {"td": td, "c": c.value, "sym": c, "o": [None] * n, "h": [None] * n, "l": [None] * n,
                         "cl": [None] * n}
        j = slot_of(self.time.hour, self.time.minute)
        d = self._day
        if c.value == d["c"] and 1 <= j <= FLAT_MIN and d["o"][j] is None:
            o, h, l, cl = float(bar.open), float(bar.high), float(bar.low), float(bar.close)
            if not (0 < l <= min(o, cl) and max(o, cl) <= h):
                self._bad += 1
            d["o"][j], d["h"][j], d["l"][j], d["cl"][j] = o, h, l, cl
            self._bars += 1
        if j == FLAT_MIN and d["td"] >= WIN_END:
            self._close_day()
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

def _seconds(self, sym, start):
    # R138's request (D-344) for one slot's window: three forms tried in turn, the whole-hour time-zone shift removed;
    # arrays indexed by the second after the window's start, None where no bar
    end = start + _delta(seconds=WINDOW_SECONDS)
    n = WINDOW_SECONDS + 1
    o, h, l, cl = [None] * n, [None] * n, [None] * n, [None] * n
    forms = (("sym", lambda: self.history(sym, start - _delta(seconds=1), end, Resolution.SECOND)),
             ("list", lambda: self.history([sym], start - _delta(seconds=1), end, Resolution.SECOND)),
             ("typed", lambda: self.history(TradeBar, sym, start - _delta(seconds=1), end, Resolution.SECOND)))
    hist, got = None, 0
    for name, call in forms:
        try:
            hist = call()
        except Exception as exc:
            if self._herr is None:
                self._herr = _clean(name + ":" + type(exc).__name__ + ":" + str(exc))
            continue
        if hist is not None and len(hist) > 0:
            if self._hform is None:
                self._hform = name
                try:
                    self._hcols = _clean("idx:" + ",".join(str(x) for x in (hist.index.names or [])) + " cols:"
                                         + ",".join(str(x) for x in list(hist.columns)[:8]))
                except Exception as exc:
                    self._hcols = _clean("shape:" + type(exc).__name__)
            break
        if self._hform is None and self._hempty is None:
            self._hempty = name
    if hist is None or len(hist) == 0:
        return o, h, l, cl, 0
    bars = [(int(round((t - start).total_seconds())), bo, bh, bl, bc) for t, bo, bh, bl, bc in iter_history_bars(hist)]
    if self._hdt is None and bars:
        self._hdt = bars[0][0]
    best_shift, best_in = 0, -1
    for shift in (0, 3600, -3600, 7200, -7200):
        inside = sum(1 for k, bo, bh, bl, bc in bars if 0 <= k - shift < n)
        if inside > best_in:
            best_shift, best_in = shift, inside
    if self._hshift is None:
        self._hshift = best_shift
    for k, bo, bh, bl, bc in bars:
        k -= best_shift
        if 0 <= k < n and o[k] is None and bo == bo and bo > 0:
            o[k], h[k], l[k], cl[k] = bo, bh, bl, bc
            got += 1
    return o, h, l, cl, got

def _close_day(self):
    d = self._day
    self._day = None
    if d["td"] > WIN_END:
        return
    in_win = d["td"] >= WIN_START
    o, h, l, cl = d["o"], d["h"], d["l"], d["cl"]
    lsm = _any_last(o, FLAT_MIN)
    if not in_win:
        self._warm += 1
    if lsm is None:
        if in_win:
            self._n += 1
            self._noref += 1
        return
    early = lsm < FLAT_MIN - 10
    prev = self._prev["s"] if (self._prev is not None and self._prev["c"] == d["c"]) else None
    if in_win:
        year = d["td"][0]
        if self._year is not None and year != self._year:
            self._emit()
        self._year = year
        self._n += 1
        if early:
            self._early += 1
        blocks = []
        for si, s in enumerate(SLOTS):
            hist = self._r10[si]
            widths = [None] * len(FRACTIONS)
            outs, ex = "-" * (len(FRACTIONS) * len(DELAYS) * 2), [None] * 4
            m = any_measures(o, h, l, cl, s, prev, TICK)
            if len(hist) < RANGE_DAYS:
                self._nohist += 1
            else:
                mean = sum(hist) / len(hist)
                widths = [int(round(f * mean)) for f in FRACTIONS]
            walk = [(i, w) for i, w in enumerate(widths) if w is not None and w >= MIN_TICKS]
            if m is None:
                self._nomeas += 1
            elif s + 11 > lsm:
                self._closed += 1                    # the session ends before the slot's box
            elif not walk:
                if widths[0] is not None:
                    self._small += 1                 # narrower than the minimum: not walked
            else:
                hh, mm = divmod((17 * 60 + s) % (24 * 60), 60)
                start = _dt(*d["td"]) + _delta(hours=hh, minutes=mm) - _delta(seconds=PRE_SECONDS)
                so, sh, sl, sc, got = self._seconds(d["sym"], start)
                self._secbars += got
                if got == 0:
                    self._nosec += 1
                else:
                    if got < WINDOW_SECONDS // 2:
                        self._short += 1
                    P = dict(PARAMS)
                    P["widths"] = [w * TICK for _, w in walk]
                    rows = run_day_flip(so, sh, sl, sc, P)
                    self._entries += len(rows)
                    self._walked += 1
                    outs, ex = day_outcomes_any(rows, [i for i, _ in walk], len(FRACTIONS), DELAYS, TICK)
            blocks.append(any_block(widths, m, outs, ex))
        self._recs.append(any_record(d["td"], 1 if early else 0, 1 if prev is not None else 0, blocks))
        self._records += 1
    summ = any_summary(o, cl)
    self._prev = {"c": d["c"], "s": summ} if summ is not None else None
    if not early:
        for si, s in enumerate(SLOTS):
            r = any_range10(h, l, s, TICK)
            if r is not None:
                self._r10[si] = (self._r10[si] + [r])[-RANGE_DAYS:]
    if d["td"] >= WIN_END:
        self._emit()
        self._done = True

def _emit(self):
    cells = self._recs
    self._recs = []
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
        tag = "F|e=" + str(self._emitted) + ";k=" + str(k) + ";K=" + str(len(chunks)) + ";x=" + x
        self._orders += 1
        self.market_order(carrier, 1 if self._orders % 2 else -1, tag=tag)

def on_end_of_algorithm(self):
    if self._day is not None and not self._done:
        self._close_day()
    if self._recs:
        self._emit()
    head = (PREFIX + "|HEAD|v=1|market=" + MARKET + "|days=" + str(self._n) + "|warm=" + str(self._warm)
            + "|entries=" + str(self._entries) + "|emits=" + str(self._emitted) + "|orders=" + str(self._orders)
            + "|switches=" + str(self._switches) + "|lost=" + str(self._lost) + "|late=" + str(self._late)
            + "|early=" + str(self._early) + "|noref=" + str(self._noref) + "|bad=" + str(self._bad)
            + "|bars=" + str(self._bars) + "|quotes=0|wide=0|badq=0"
            + "|secbars=" + str(self._secbars) + "|nosec=" + str(self._nosec) + "|short=" + str(self._short)
            + "|records=" + str(self._records) + "|nomeas=" + str(self._nomeas) + "|small=" + str(self._small)
            + "|closed=" + str(self._closed) + "|nohist=" + str(self._nohist) + "|walked=" + str(self._walked)
            + "|hform=" + str(self._hform or "none") + "|hempty=" + str(self._hempty or "none")
            + "|hdt=" + str(self._hdt if self._hdt is not None else "none")
            + "|hshift=" + str(self._hshift if self._hshift is not None else "none")
            + "|hcols=" + str(self._hcols or "none") + "|herr=" + str(self._herr or "none"))
    self.log(head[:LOG_BUDGET_BYTES - 80])
    self.log(PREFIX + "|END")
"""


# ---------------------------------------------------------------- the flip design map (D-375): R144-flipdesign-NQ
# The 08:30 flip at fixed widths from 20 to 100 points, both sides, on time and a minute late, in a thirty-minute box,
# with each bracket's seconds to resolution and the price at the shorter boxes' ends, beside D-371's pre-08:30 measures;
# one second-bar history request a day (R138's method). One record a day leaves (`flipdesign_core.design_record`).
FLIPDESIGN_RUN = "R144-flipdesign-NQ"
FLIPDESIGN_PREFIX = "FM5"
DESIGN_HEAD_EXTRA = ("secbars", "nosec", "short", "records", "noprev", "nomeas", "noentry")


def config_design(path: Path | None = None) -> dict[str, Any]:
    return yaml.safe_load(Path(path or CONFIG_DIR / "flip_design.yaml").read_text(encoding="utf-8"))


def windows_design(cfg: dict | None = None) -> tuple[date, date, date]:
    cfg = cfg or config_design()
    return tuple(date.fromisoformat(str(cfg["window"][k])) for k in ("warm", "start", "end"))


def params_design(cfg: dict | None = None) -> dict[str, Any]:
    """The design kit's parameters: the second window and the slot's offset in it, the widths in points, the marks, the
    box and the delays; the parser's prefix and HEAD fields."""
    cfg = cfg or config_design()
    w = cfg["window_ct"]
    h0, m0 = map(int, str(w["start"]).split(":"))
    h1, m1 = map(int, str(w["end"]).split(":"))
    length = (h1 * 60 + m1 - h0 * 60 - m0) * 60
    sh, sm = map(int, str(cfg["slot_ct"]).split(":"))
    slot = (sh * 60 + sm - h0 * 60 - m0) * 60
    delays = [int(x) for x in cfg["entry_delays_seconds"]]
    box = int(cfg["box_seconds"])
    marks = [int(x) for x in cfg["marks_seconds"]]
    if delays[0] != 0 or slot + box + max(delays) >= length or max(marks) > box:
        raise ValueError("the window must hold the on-time entry, the late entry and the box, and every mark the box")
    k = cfg["contract"]
    tick = float(k["tick"])
    widths = [float(x) for x in cfg["widths_points"]]
    return {"market": str(cfg["market"]), "ticker": str(k["ticker"]), "tick": tick, "point_value": float(k["point_value"]),
            "window_ct": [str(w["start"]), str(w["end"])], "window_start_hm": (h0, m0), "window_seconds": length,
            "slot_ct": str(cfg["slot_ct"]), "slot": slot, "widths_points": widths, "marks": marks, "delays": delays,
            "box": box, "time_unit": "second", "prefix": FLIPDESIGN_PREFIX, "head_extra": list(DESIGN_HEAD_EXTRA),
            "head_text": list(SECONDS_HEAD_TEXT),
            "p": {"times": [slot], "widths": widths, "slip": tick * float(cfg["slip_ticks"]), "box": box,
                  "delays": delays}}


def preamble_design(cfg: dict | None = None) -> str:
    from propedge.outcomes import flip_core, flipdesign_core, flipdir_core

    cfg = cfg or config_design()
    q = params_design(cfg)
    _, w0, w1 = windows_design(cfg)
    h0, m0 = q["window_start_hm"]
    return f'''
MARKET = "{q["ticker"]}"
TICK = {q["tick"]!r}
WIN_START = ({w0.year}, {w0.month}, {w0.day})   # earlier days are warm-up: they feed the previous day, nothing leaves
WIN_END = ({w1.year}, {w1.month}, {w1.day})
FILTER_DAYS = 120
PREFIX = "{FLIPDESIGN_PREFIX}"
LOG_BUDGET_BYTES = {LOG_BUDGET_BYTES}
TAG_CHARS = {FLIP_TAG_CHARS}
PARAMS = {q["p"]!r}
SLOT = {q["slot"]}                      # the slot: a second offset into the window
MARKS = {q["marks"]!r}                  # seconds after the entry bar at which the price is recorded
DELAYS = {q["delays"]!r}
WIN_H0, WIN_M0 = {h0}, {m0}             # the window's start, CT
WINDOW_SECONDS = {q["window_seconds"]}
from datetime import timedelta as _delta
from datetime import datetime as _dt


class CarrierInitializer(BrokerageModelSecurityInitializer):
    """Zero fees: the carrier orders' own P&L is never used."""

    def initialize(self, security):
        super().initialize(security)
        security.set_fee_model(ConstantFeeModel(0))


def _clean(text):
    out = "".join((ch if (ch.isalnum() or ch in ".,:_-[]()") else "_") for ch in str(text))
    return out[:160] if out else "none"


def iter_history_bars(hist):
    """(end time, open, high, low, close) per row; the time is the LAST index level (expiry, symbol, time)."""
    try:
        if hist is None or len(hist) == 0:
            return
        idx = hist.index
        times = idx.get_level_values(-1) if getattr(idx, "nlevels", 1) > 1 else idx
        for t, bo, bh, bl, bc in zip(times, hist["open"], hist["high"], hist["low"], hist["close"]):
            if isinstance(t, tuple):
                t = t[-1]
            t = t.to_pydatetime() if hasattr(t, "to_pydatetime") else t
            yield t, float(bo), float(bh), float(bl), float(bc)
    except Exception:
        return


# ---------------------------------------------------------------- embedded verbatim from
# ---------------------------------------------------------------- propedge/outcomes/flip_core.py
{inspect.getsource(flip_core)}
# ---------------------------------------------------------------- end of the embedded core
# ---------------------------------------------------------------- embedded verbatim from
# ---------------------------------------------------------------- propedge/outcomes/flipdir_core.py
{inspect.getsource(flipdir_core)}
# ---------------------------------------------------------------- end of the embedded core
# ---------------------------------------------------------------- embedded verbatim from
# ---------------------------------------------------------------- propedge/outcomes/flipdesign_core.py
{inspect.getsource(flipdesign_core)}
# ---------------------------------------------------------------- end of the embedded core
FLAT_MIN = FLAT                         # the minute clock's last bar (15:10 CT)
FLAT = WINDOW_SECONDS                   # the walk's day end in THIS kit's units: the window's last second
'''


BODY_DESIGN = """
def setup(self):
    # D-375: the flip design map -- the resolution map's version 3 day and roll bookkeeping on minute bars (D-214, D-215,
    # D-223) with each bar recorded for D-371's measures and the previous day carried, and at each day's close R138's
    # history request for the window's second bars, walked by the embedded core; one record a day.
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
    self._orders, self._early, self._bad, self._bars, self._nosec, self._secbars, self._short = 0, 0, 0, 0, 0, 0, 0
    self._noref, self._records, self._noprev, self._nomeas, self._noentry = 0, 0, 0, 0, 0
    self._herr, self._hform, self._hcols, self._hdt, self._hempty, self._hshift = None, None, None, None, None, None
    self._recs, self._year, self._emitted, self._prev = [], None, 0, None

def _trading_day(self):
    t = self.time + _delta(hours=7)
    return (t.year, t.month, t.day)

def on_data(self, data):
    if self._done:
        return
    for sym, b in data.bars.items():
        if sym != self.future.symbol and sym.security_type == SecurityType.FUTURE:
            self._vol[sym] = self._vol.get(sym, 0.0) + float(b.volume)
    if self._active is not None and (self._active not in self.securities
                                     or self._active.id.date.date() < _date(*self._trading_day())):
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
        if self._rolled != closed:
            self._late += 1
            self._roll(c, closed)
            if (self._active or c) != c:
                return
        if self._done:
            return
    m = self.time.hour * 60 + self.time.minute
    if m > 17 * 60 or m <= 15 * 60 + 10:
        if self._day is None:
            n = FLAT_MIN + 1
            self._day = {"td": td, "c": c.value, "sym": c, "o": [None] * n, "h": [None] * n, "l": [None] * n,
                         "cl": [None] * n}
        j = slot_of(self.time.hour, self.time.minute)
        d = self._day
        if c.value == d["c"] and 1 <= j <= FLAT_MIN and d["o"][j] is None:
            o, h, l, cl = float(bar.open), float(bar.high), float(bar.low), float(bar.close)
            if not (0 < l <= min(o, cl) and max(o, cl) <= h):
                self._bad += 1
            d["o"][j], d["h"][j], d["l"][j], d["cl"][j] = o, h, l, cl
            self._bars += 1
        if j == FLAT_MIN and d["td"] >= WIN_END:
            self._close_day()
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

def _seconds(self, d):
    # R138's request (D-344): the window's second bars of the day's contract, three forms tried in turn, the whole-hour
    # time-zone shift removed; arrays indexed by the second after the window's start, None where no bar
    start = _dt(*d["td"]) + _delta(hours=WIN_H0, minutes=WIN_M0)
    end = start + _delta(seconds=WINDOW_SECONDS)
    n = WINDOW_SECONDS + 1
    o, h, l, cl = [None] * n, [None] * n, [None] * n, [None] * n
    sym = d["sym"]
    forms = (("sym", lambda: self.history(sym, start - _delta(seconds=1), end, Resolution.SECOND)),
             ("list", lambda: self.history([sym], start - _delta(seconds=1), end, Resolution.SECOND)),
             ("typed", lambda: self.history(TradeBar, sym, start - _delta(seconds=1), end, Resolution.SECOND)))
    hist, got = None, 0
    for name, call in forms:
        try:
            hist = call()
        except Exception as exc:
            if self._herr is None:
                self._herr = _clean(name + ":" + type(exc).__name__ + ":" + str(exc))
            continue
        if hist is not None and len(hist) > 0:
            if self._hform is None:
                self._hform = name
                try:
                    self._hcols = _clean("idx:" + ",".join(str(x) for x in (hist.index.names or [])) + " cols:"
                                         + ",".join(str(x) for x in list(hist.columns)[:8]))
                except Exception as exc:
                    self._hcols = _clean("shape:" + type(exc).__name__)
            break
        if self._hform is None and self._hempty is None:
            self._hempty = name
    if hist is None or len(hist) == 0:
        return o, h, l, cl, 0
    bars = [(int(round((t - start).total_seconds())), bo, bh, bl, bc) for t, bo, bh, bl, bc in iter_history_bars(hist)]
    if self._hdt is None and bars:
        self._hdt = bars[0][0]
    best_shift, best_in = 0, -1
    for shift in (0, 3600, -3600, 7200, -7200):
        inside = sum(1 for k, bo, bh, bl, bc in bars if 0 <= k - shift < n)
        if inside > best_in:
            best_shift, best_in = shift, inside
    if self._hshift is None:
        self._hshift = best_shift
    for k, bo, bh, bl, bc in bars:
        k -= best_shift
        if 0 <= k < n and o[k] is None and bo == bo and bo > 0:
            o[k], h[k], l[k], cl[k] = bo, bh, bl, bc
            got += 1
    return o, h, l, cl, got

def _close_day(self):
    d = self._day
    self._day = None
    if d["td"] > WIN_END:
        return
    in_win = d["td"] >= WIN_START
    o, h, l, cl = d["o"], d["h"], d["l"], d["cl"]
    lsm = _last_at_or_before(o, FLAT_MIN)
    if not in_win:
        self._warm += 1
    if lsm is None:
        if in_win:
            self._n += 1
            self._noref += 1
        return
    early = lsm < FLAT_MIN - 10
    prev = self._prev["s"] if (self._prev is not None and self._prev["c"] == d["c"]) else None
    if in_win:
        year = d["td"][0]
        if self._year is not None and year != self._year:
            self._emit()
        self._year = year
        self._n += 1
        if early:
            self._early += 1
        if prev is None:
            self._noprev += 1
        nw = len(PARAMS["widths"])
        outs, units, marks = "-" * (nw * len(DELAYS) * 2), [None] * (nw * 2), [None] * len(MARKS)
        m = day_measures(o, h, l, cl, prev, TICK)
        if m is None:
            self._nomeas += 1
        else:
            so, sh, sl, sc, got = self._seconds(d)
            self._secbars += got
            if got == 0:
                self._nosec += 1
            else:
                if got < WINDOW_SECONDS // 2:
                    self._short += 1
                rows = run_day_flip(so, sh, sl, sc, PARAMS)
                self._entries += len(rows)
                outs, units = design_outcomes(rows, nw, DELAYS)
                j0 = design_entry(so, SLOT, 0)
                if j0 is None:
                    self._noentry += 1
                else:
                    marks = design_marks(so, sc, j0, MARKS, TICK)
        self._recs.append(design_record(d["td"], 1 if early else 0, 1 if prev is not None else 0, m, DIR_MEASURES,
                                        outs, units, marks))
        self._records += 1
    summ = day_summary(o, h, l, cl)
    self._prev = {"c": d["c"], "s": summ} if summ is not None else None
    if d["td"] >= WIN_END:
        self._emit()
        self._done = True

def _emit(self):
    cells = self._recs
    self._recs = []
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
        tag = "F|e=" + str(self._emitted) + ";k=" + str(k) + ";K=" + str(len(chunks)) + ";x=" + x
        self._orders += 1
        self.market_order(carrier, 1 if self._orders % 2 else -1, tag=tag)

def on_end_of_algorithm(self):
    if self._day is not None and not self._done:
        self._close_day()
    if self._recs:
        self._emit()
    head = (PREFIX + "|HEAD|v=1|market=" + MARKET + "|days=" + str(self._n) + "|warm=" + str(self._warm)
            + "|entries=" + str(self._entries) + "|emits=" + str(self._emitted) + "|orders=" + str(self._orders)
            + "|switches=" + str(self._switches) + "|lost=" + str(self._lost) + "|late=" + str(self._late)
            + "|early=" + str(self._early) + "|noref=" + str(self._noref) + "|bad=" + str(self._bad)
            + "|bars=" + str(self._bars) + "|quotes=0|wide=0|badq=0"
            + "|secbars=" + str(self._secbars) + "|nosec=" + str(self._nosec) + "|short=" + str(self._short)
            + "|records=" + str(self._records) + "|noprev=" + str(self._noprev) + "|nomeas=" + str(self._nomeas)
            + "|noentry=" + str(self._noentry)
            + "|hform=" + str(self._hform or "none") + "|hempty=" + str(self._hempty or "none")
            + "|hdt=" + str(self._hdt if self._hdt is not None else "none")
            + "|hshift=" + str(self._hshift if self._hshift is not None else "none")
            + "|hcols=" + str(self._hcols or "none") + "|herr=" + str(self._herr or "none"))
    self.log(head[:LOG_BUDGET_BYTES - 80])
    self.log(PREFIX + "|END")
"""


# ---------------------------------------------------------------- the collect map (D-381): R145-collect-NQ
# Uneven brackets whose $200 target alone makes a winning day, stops one to eight times the target, at every slot of the
# flip map (R137's), in boxes of 10 to 120 minutes, on time and a minute late, both sides pooled; walked on minute bars by
# `propedge/outcomes/collect_core` (embedded verbatim), every minute that first reaches a bracket's target and its stop
# settled on its second bars by one history request per run of tied minutes. FOMC days and early closes carry no
# bracket; on a BLS 08:30 ET release day a bracket still open is closed before 07:30 CT. Only counts leave (D-120).
COLLECT_RUN = "R145-collect-NQ"
COLLECT_PREFIX = "FM6"
COLLECT_HEAD_EXTRA = ("fomc", "bls", "ties", "secreq", "secbars", "nosec", "nosecbar")
COLLECT_GROUP_MINUTES = 15            # a run of tied minutes shares one history request while it spans less than this


def config_collect(path: Path | None = None) -> dict[str, Any]:
    return yaml.safe_load(Path(path or CONFIG_DIR / "collect_map.yaml").read_text(encoding="utf-8"))


def windows_collect(cfg: dict | None = None) -> tuple[date, date, date]:
    cfg = cfg or config_collect()
    return tuple(date.fromisoformat(str(cfg["window"][k])) for k in ("warm", "start", "end"))


def _yymmdd(s: str) -> int:
    y, m, d = map(int, str(s)[:10].split("-"))
    return (y % 100) * 10000 + m * 100 + d


def collect_release_days(cfg: dict | None = None) -> tuple[list[int], list[int]]:
    """(FOMC days, BLS 08:30 ET release days) inside the window as yymmdd integers, from the config's files -- FV3's
    sources (`scripts/score_orb3_search.fomc_dates`' reading; `data/release_days_0830_2009_2025.csv`)."""
    import io

    import pandas as pd

    cfg = cfg or config_collect()
    root = CONFIG_DIR.parent
    _, w0, w1 = windows_collect(cfg)
    lo, hi = w0.isoformat(), w1.isoformat()
    fomc: set[str] = set()
    for rel in cfg["news"]["fomc"]:
        lines = [ln for ln in (root / rel).read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
        t = pd.read_csv(io.StringIO("\n".join(lines)))
        if "code" in t.columns:
            t = t[t["code"] == "FOMC"]
        fomc |= {str(x) for x in t["date"]}
    files = cfg["news"]["bls"]                            # D-439: one file, or a list (a window across two files)
    files = [files] if isinstance(files, str) else list(files)
    bls = set().union(*(set(pd.read_csv(root / f)["date"].astype(str)) for f in files))
    return (sorted(_yymmdd(s) for s in fomc if lo <= s <= hi), sorted(_yymmdd(s) for s in bls if lo <= s <= hi))


def params_collect(cfg: dict | None = None) -> dict[str, Any]:
    """The collect kit's parameters: R137's slots with their clock labels, the brackets (the target in points for each
    micro count -- the gross target over the micros' dollars a point, a whole tick, its win after the round turn at
    least the operator's net minimum -- and each stop multiple's stop), the distances the walk passes, each bracket's
    (target, stop) indices, the boxes and delays in bars, the BLS cut, the release days; the parser's fields."""
    from propedge.execution.fills import FillModel
    from propedge.outcomes.collect_core import c_slot

    cfg = cfg or config_collect()
    day = cfg["day"]

    def hm(x):
        return tuple(map(int, str(x).split(":")))

    last = c_slot(*hm(day["last_decision_ct"]))
    times = set(range(0, last + 1, int(day["decision_every_min"])))
    for x in day.get("extra_decisions_ct") or ():
        times.add(c_slot(*hm(x)))
    times = sorted(times)
    labels = [f"{((17 * 60 + t) % 1440) // 60:02d}:{(17 * 60 + t) % 60:02d}" for t in times]
    k = cfg["contract"]
    tick, mpv = float(k["tick"]), float(k["micro_point_value"])
    tg = cfg["target"]
    gross, net_min = float(tg["gross_dollars"]), float(tg["net_min_dollars"])
    fee = float(FillModel.load("assumed").round_turn_by_instrument[str(k["micro"])])
    contracts = [int(x) for x in tg["contracts"]]
    mults = [float(x) for x in cfg["stop_multiples"]]

    def on_tick(x: float, what: str) -> float:
        if abs(x / tick - round(x / tick)) > 1e-9:
            raise ValueError(f"{what} of {x:g} points is not a whole number of ticks")
        return round(x / tick) * tick

    targets = [on_tick(gross / (n * mpv), f"the target for {n} micros") for n in contracts]
    for n in contracts:
        if gross - n * fee < net_min - 1e-9:
            raise ValueError(f"{n} micros win ${gross - n * fee:.2f} after the round turn, under the ${net_min:g} minimum")
    stops = [[on_tick(m * T, f"the {m:g}x stop for {n} micros") for m in mults] for n, T in zip(contracts, targets)]
    levels = sorted({*targets, *(s for row in stops for s in row)})
    pairs = [[(levels.index(T), levels.index(s)) for s in row] for T, row in zip(targets, stops)]
    boxes = [int(x) for x in cfg["boxes_minutes"]]
    delays = [int(x) for x in cfg["entry_delays_min"]]
    if boxes != sorted(boxes) or delays[0] != 0 or sorted(mults) != mults:
        raise ValueError("boxes and stop multiples ascend; the first delay is on time")
    fomc, bls = collect_release_days(cfg)
    _, w0, _ = windows_collect(cfg)
    return {"market": str(cfg["market"]), "ticker": str(k["ticker"]), "tick": tick, "point_value": float(k["point_value"]),
            "micro": str(k["micro"]), "micro_point_value": mpv, "fee_round_turn": fee, "gross_dollars": gross,
            "net_min_dollars": net_min, "slots": times, "slot_labels": labels, "contracts": contracts,
            "targets_points": targets, "stop_multiples": mults, "stops_points": stops, "boxes": boxes,
            "delays": delays, "bls_cut": c_slot(*hm(cfg["news"]["bls_cut_ct"])), "fomc_days": fomc, "bls_days": bls,
            "y0": w0.year, "time_unit": "minute", "prefix": COLLECT_PREFIX, "head_extra": list(COLLECT_HEAD_EXTRA),
            "head_text": list(SECONDS_HEAD_TEXT),
            "p": {"slots": times, "delays": delays, "boxes": boxes, "levels": levels,
                  "slip": tick * float(cfg["slip_ticks"]), "pairs": pairs, "tick": tick}}


def preamble_collect(cfg: dict | None = None) -> str:
    from propedge.outcomes import collect_core

    cfg = cfg or config_collect()
    q = params_collect(cfg)
    _, w0, w1 = windows_collect(cfg)
    return f'''
MARKET = "{q["ticker"]}"
TICK = {q["tick"]!r}
WIN_START = ({w0.year}, {w0.month}, {w0.day})   # earlier days are warm-up and record nothing
WIN_END = ({w1.year}, {w1.month}, {w1.day})
Y0 = {q["y0"]}
FILTER_DAYS = 120
PREFIX = "{COLLECT_PREFIX}"
LOG_BUDGET_BYTES = {LOG_BUDGET_BYTES}
TAG_CHARS = {FLIP_TAG_CHARS}
PARAMS = {q["p"]!r}
BLS_CUT = {q["bls_cut"]}                # the last bar before a BLS 08:30 ET release (07:30 CT) on the trading-day clock
GROUP = {COLLECT_GROUP_MINUTES}
FOMC = frozenset(int(x) for x in "{",".join(str(x) for x in q["fomc_days"])}".split(","))   # yymmdd: no bracket
BLS = frozenset(int(x) for x in "{",".join(str(x) for x in q["bls_days"])}".split(","))     # yymmdd: closed by BLS_CUT
from datetime import timedelta as _delta
from datetime import datetime as _dt


class CarrierInitializer(BrokerageModelSecurityInitializer):
    """Zero fees: the carrier orders' own P&L is never used."""

    def initialize(self, security):
        super().initialize(security)
        security.set_fee_model(ConstantFeeModel(0))


def _clean(text):
    out = "".join((ch if (ch.isalnum() or ch in ".,:_-[]()") else "_") for ch in str(text))
    return out[:160] if out else "none"


def iter_history_bars(hist):
    """(end time, open, high, low, close) per row; the time is the LAST index level (expiry, symbol, time)."""
    try:
        if hist is None or len(hist) == 0:
            return
        idx = hist.index
        times = idx.get_level_values(-1) if getattr(idx, "nlevels", 1) > 1 else idx
        for t, bo, bh, bl, bc in zip(times, hist["open"], hist["high"], hist["low"], hist["close"]):
            if isinstance(t, tuple):
                t = t[-1]
            t = t.to_pydatetime() if hasattr(t, "to_pydatetime") else t
            yield t, float(bo), float(bh), float(bl), float(bc)
    except Exception:
        return


# ---------------------------------------------------------------- embedded verbatim from
# ---------------------------------------------------------------- propedge/outcomes/collect_core.py
{inspect.getsource(collect_core)}
# ---------------------------------------------------------------- end of the embedded core
'''


BODY_COLLECT = """
def setup(self):
    # D-381: the collect map -- the flip map's minute bookkeeping (D-214, D-215, D-223) with each bar's close; at each
    # day's close every slot's walks both ways, the tied minutes' second bars by history request (R138's), the counts.
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
    self._orders, self._early, self._bad, self._bars, self._noref = 0, 0, 0, 0, 0
    self._fomc, self._bls, self._ties, self._secreq, self._secbars, self._nosec, self._nosecbar = 0, 0, 0, 0, 0, 0, 0
    self._herr, self._hform, self._hcols, self._hdt, self._hempty, self._hshift = None, None, None, None, None, None
    self._acc, self._aux, self._year, self._emitted = {}, {}, None, 0

def _trading_day(self):
    t = self.time + _delta(hours=7)
    return (t.year, t.month, t.day)

def on_data(self, data):
    if self._done:
        return
    for sym, b in data.bars.items():
        if sym != self.future.symbol and sym.security_type == SecurityType.FUTURE:
            self._vol[sym] = self._vol.get(sym, 0.0) + float(b.volume)
    if self._active is not None and (self._active not in self.securities
                                     or self._active.id.date.date() < _date(*self._trading_day())):
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
        if self._rolled != closed:
            self._late += 1
            self._roll(c, closed)
            if (self._active or c) != c:
                return
        if self._done:
            return
    m = self.time.hour * 60 + self.time.minute
    if m > 17 * 60 or m <= 15 * 60 + 10:
        if self._day is None:
            n = C_FLAT + 1
            self._day = {"td": td, "c": c.value, "sym": c, "o": [None] * n, "h": [None] * n, "l": [None] * n,
                         "cl": [None] * n}
        j = c_slot(self.time.hour, self.time.minute)
        d = self._day
        if c.value == d["c"] and 1 <= j <= C_FLAT and d["o"][j] is None:
            o, h, l, cl = float(bar.open), float(bar.high), float(bar.low), float(bar.close)
            if not (0 < l <= min(o, cl) and max(o, cl) <= h):
                self._bad += 1
            d["o"][j], d["h"][j], d["l"][j], d["cl"][j] = o, h, l, cl
            self._bars += 1
        if j == C_FLAT and d["td"] >= WIN_END:
            self._close_day()
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

def _seconds(self, sym, start, length):
    # R138's request (D-344) for one window of `length` seconds: three forms tried in turn, the whole-hour time-zone
    # shift removed; arrays indexed by a bar's END second after the window's start, None where no bar
    end = start + _delta(seconds=length)
    n = length + 1
    o, h, l = [None] * n, [None] * n, [None] * n
    forms = (("sym", lambda: self.history(sym, start - _delta(seconds=1), end, Resolution.SECOND)),
             ("list", lambda: self.history([sym], start - _delta(seconds=1), end, Resolution.SECOND)),
             ("typed", lambda: self.history(TradeBar, sym, start - _delta(seconds=1), end, Resolution.SECOND)))
    hist = None
    for name, call in forms:
        try:
            hist = call()
        except Exception as exc:
            if self._herr is None:
                self._herr = _clean(name + ":" + type(exc).__name__ + ":" + str(exc))
            continue
        if hist is not None and len(hist) > 0:
            if self._hform is None:
                self._hform = name
                try:
                    self._hcols = _clean("idx:" + ",".join(str(x) for x in (hist.index.names or [])) + " cols:"
                                         + ",".join(str(x) for x in list(hist.columns)[:8]))
                except Exception as exc:
                    self._hcols = _clean("shape:" + type(exc).__name__)
            break
        if self._hform is None and self._hempty is None:
            self._hempty = name
    if hist is None or len(hist) == 0:
        return o, h, l, 0
    bars = [(int(round((t - start).total_seconds())), bo, bh, bl) for t, bo, bh, bl, bc in iter_history_bars(hist)]
    if self._hdt is None and bars:
        self._hdt = bars[0][0]
    best_shift, best_in = 0, -1
    for shift in (0, 3600, -3600, 7200, -7200):
        inside = sum(1 for k, bo, bh, bl in bars if 0 < k - shift < n)
        if inside > best_in:
            best_shift, best_in = shift, inside
    if self._hshift is None:
        self._hshift = best_shift
    got = 0
    for k, bo, bh, bl in bars:
        k -= best_shift
        if 0 < k < n and o[k] is None and bo == bo and bo > 0:
            o[k], h[k], l[k] = bo, bh, bl
            got += 1
    return o, h, l, got

def _tied(self, d, need):
    # each run of tied minutes spanning less than GROUP minutes is one history request; {minute: its second bars}
    out, i = {}, 0
    self._ties += len(need)
    while i < len(need):
        m0, k = need[i], i
        while k + 1 < len(need) and need[k + 1] - m0 < GROUP:
            k += 1
        start = _dt(*d["td"]) - _delta(days=1) + _delta(hours=17, minutes=m0 - 1)
        so, sh, sl, got = self._seconds(d["sym"], start, (need[k] - m0 + 1) * 60)
        self._secreq += 1
        self._secbars += got
        if got == 0:
            self._nosec += 1
        for j in need[i:k + 1]:
            a = (j - m0) * 60 + 1
            seg = (so[a:a + 60], sh[a:a + 60], sl[a:a + 60])
            if any(x is not None for x in seg[0]):
                out[j] = seg
            else:
                self._nosecbar += 1
        i = k + 1
    return out

def _close_day(self):
    d = self._day
    self._day = None
    if d["td"] < WIN_START or d["td"] > WIN_END:
        self._warm += 1
        return
    year = d["td"][0]
    if self._year is not None and year != self._year:
        self._emit()
    self._year = year
    self._n += 1
    o, h, l, cl = d["o"], d["h"], d["l"], d["cl"]
    key = (year % 100) * 10000 + d["td"][1] * 100 + d["td"][2]
    last = c_last(o)
    if last is None:
        self._noref += 1
    elif last < C_FLAT - 10:
        self._early += 1
    elif key in FOMC:
        self._fomc += 1
    else:
        cut = None
        if key in BLS:
            cut = BLS_CUT
            self._bls += 1
        walks = c_walks(o, h, l, cl, PARAMS, cut)
        self._entries += len(walks)
        secs = self._tied(d, sorted(c_ties(walks, PARAMS)))

        def tie(j, entry, dd, T, S):
            s = secs.get(j)
            return None if s is None else c_tie(s[0], s[1], s[2], entry, dd, T, S)

        c_count(walks, PARAMS, tie, self._acc, self._aux, year)
    if d["td"] >= WIN_END:
        self._emit()
        self._done = True

def _emit(self):
    cells = c_encode(self._acc, self._aux, Y0)
    self._acc, self._aux = {}, {}
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
        tag = "F|e=" + str(self._emitted) + ";k=" + str(k) + ";K=" + str(len(chunks)) + ";x=" + x
        self._orders += 1
        self.market_order(carrier, 1 if self._orders % 2 else -1, tag=tag)

def on_end_of_algorithm(self):
    if self._day is not None and not self._done:
        self._close_day()
    if self._acc or self._aux:
        self._emit()
    head = (PREFIX + "|HEAD|v=1|market=" + MARKET + "|days=" + str(self._n) + "|warm=" + str(self._warm)
            + "|entries=" + str(self._entries) + "|emits=" + str(self._emitted) + "|orders=" + str(self._orders)
            + "|switches=" + str(self._switches) + "|lost=" + str(self._lost) + "|late=" + str(self._late)
            + "|early=" + str(self._early) + "|noref=" + str(self._noref) + "|bad=" + str(self._bad)
            + "|bars=" + str(self._bars) + "|quotes=0|wide=0|badq=0"
            + "|fomc=" + str(self._fomc) + "|bls=" + str(self._bls) + "|ties=" + str(self._ties)
            + "|secreq=" + str(self._secreq) + "|secbars=" + str(self._secbars) + "|nosec=" + str(self._nosec)
            + "|nosecbar=" + str(self._nosecbar)
            + "|hform=" + str(self._hform or "none") + "|hempty=" + str(self._hempty or "none")
            + "|hdt=" + str(self._hdt if self._hdt is not None else "none")
            + "|hshift=" + str(self._hshift if self._hshift is not None else "none")
            + "|hcols=" + str(self._hcols or "none") + "|herr=" + str(self._herr or "none"))
    self.log(head[:LOG_BUDGET_BYTES - 80])
    self.log(PREFIX + "|END")
"""


# ---------------------------------------------------------------- the clock check (D-386 (7)): R146-dst-NQ
# Per trading day the high less low of six one-minute bars -- those starting at 06:30, 07:30 and 08:30 CT and at 12:00,
# 13:00 and 14:00 CT -- on the kits' own clock (the collect kit's minute bookkeeping, no second bars). One short record a
# day leaves (`dst_core.dst_record`).
DST_RUN = "R146-dst-NQ"
DST_PREFIX = "FM7"
DST_HEAD_EXTRA = ("records", "missing")


def config_dst(path: Path | None = None) -> dict[str, Any]:
    return yaml.safe_load(Path(path or CONFIG_DIR / "dst_check.yaml").read_text(encoding="utf-8"))


def windows_dst(cfg: dict | None = None) -> tuple[date, date, date]:
    cfg = cfg or config_dst()
    return tuple(date.fromisoformat(str(cfg["window"][k])) for k in ("warm", "start", "end"))


def params_dst(cfg: dict | None = None) -> dict[str, Any]:
    """The clock kit's parameters: the six bars by their START time and their END slots on the trading-day clock."""
    from propedge.outcomes.dst_core import dst_end_slot

    cfg = cfg or config_dst()
    labels = [str(x) for x in cfg["bars_start_ct"]]
    slots = [dst_end_slot(*map(int, x.split(":"))) for x in labels]
    k = cfg["contract"]
    return {"market": str(cfg["market"]), "ticker": str(k["ticker"]), "tick": float(k["tick"]), "bar_labels": labels,
            "slots": slots, "time_unit": "minute", "prefix": DST_PREFIX, "head_extra": list(DST_HEAD_EXTRA),
            "head_text": []}


def preamble_dst(cfg: dict | None = None) -> str:
    from propedge.outcomes import collect_core, dst_core

    cfg = cfg or config_dst()
    q = params_dst(cfg)
    _, w0, w1 = windows_dst(cfg)
    return f'''
MARKET = "{q["ticker"]}"
TICK = {q["tick"]!r}
WIN_START = ({w0.year}, {w0.month}, {w0.day})   # earlier days are warm-up and record nothing
WIN_END = ({w1.year}, {w1.month}, {w1.day})
FILTER_DAYS = 120
PREFIX = "{DST_PREFIX}"
LOG_BUDGET_BYTES = {LOG_BUDGET_BYTES}
TAG_CHARS = {FLIP_TAG_CHARS}
SLOTS = {q["slots"]!r}                  # the END slots of the bars starting {", ".join(q["bar_labels"])} CT
from datetime import timedelta as _delta


class CarrierInitializer(BrokerageModelSecurityInitializer):
    """Zero fees: the carrier orders' own P&L is never used."""

    def initialize(self, security):
        super().initialize(security)
        security.set_fee_model(ConstantFeeModel(0))


# ---------------------------------------------------------------- embedded verbatim from
# ---------------------------------------------------------------- propedge/outcomes/collect_core.py
{inspect.getsource(collect_core)}
# ---------------------------------------------------------------- end of the embedded core
# ---------------------------------------------------------------- embedded verbatim from
# ---------------------------------------------------------------- propedge/outcomes/dst_core.py
{inspect.getsource(dst_core)}
# ---------------------------------------------------------------- end of the embedded core
'''


BODY_DST = """
def setup(self):
    # D-386 (7): the clock check -- the collect kit's minute bookkeeping (D-214, D-215, D-223); at each day's close the
    # six bars' ranges in ticks, one record a day.
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
    self._orders, self._early, self._bad, self._bars, self._noref, self._records, self._missing = 0, 0, 0, 0, 0, 0, 0
    self._recs, self._year, self._emitted = [], None, 0

def _trading_day(self):
    t = self.time + _delta(hours=7)
    return (t.year, t.month, t.day)

def on_data(self, data):
    if self._done:
        return
    for sym, b in data.bars.items():
        if sym != self.future.symbol and sym.security_type == SecurityType.FUTURE:
            self._vol[sym] = self._vol.get(sym, 0.0) + float(b.volume)
    if self._active is not None and (self._active not in self.securities
                                     or self._active.id.date.date() < _date(*self._trading_day())):
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
        if self._rolled != closed:
            self._late += 1
            self._roll(c, closed)
            if (self._active or c) != c:
                return
        if self._done:
            return
    m = self.time.hour * 60 + self.time.minute
    if m > 17 * 60 or m <= 15 * 60 + 10:
        if self._day is None:
            n = C_FLAT + 1
            self._day = {"td": td, "c": c.value, "o": [None] * n, "h": [None] * n, "l": [None] * n}
        j = c_slot(self.time.hour, self.time.minute)
        d = self._day
        if c.value == d["c"] and 1 <= j <= C_FLAT and d["o"][j] is None:
            o, h, l, cl = float(bar.open), float(bar.high), float(bar.low), float(bar.close)
            if not (0 < l <= min(o, cl) and max(o, cl) <= h):
                self._bad += 1
            d["o"][j], d["h"][j], d["l"][j] = o, h, l
            self._bars += 1
        if j == C_FLAT and d["td"] >= WIN_END:
            self._close_day()
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

def _close_day(self):
    d = self._day
    self._day = None
    if d["td"] < WIN_START or d["td"] > WIN_END:
        self._warm += 1
        return
    year = d["td"][0]
    if self._year is not None and year != self._year:
        self._emit()
    self._year = year
    self._n += 1
    last = c_last(d["o"])
    if last is None:
        self._noref += 1
    else:
        if last < C_FLAT - 10:
            self._early += 1
        r = dst_ranges(d["h"], d["l"], SLOTS, TICK)
        self._missing += sum(1 for x in r if x is None)
        self._entries += sum(1 for x in r if x is not None)
        self._recs.append(dst_record(d["td"], r))
        self._records += 1
    if d["td"] >= WIN_END:
        self._emit()
        self._done = True

def _emit(self):
    cells = self._recs
    self._recs = []
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
        tag = "F|e=" + str(self._emitted) + ";k=" + str(k) + ";K=" + str(len(chunks)) + ";x=" + x
        self._orders += 1
        self.market_order(carrier, 1 if self._orders % 2 else -1, tag=tag)

def on_end_of_algorithm(self):
    if self._day is not None and not self._done:
        self._close_day()
    if self._recs:
        self._emit()
    head = (PREFIX + "|HEAD|v=1|market=" + MARKET + "|days=" + str(self._n) + "|warm=" + str(self._warm)
            + "|entries=" + str(self._entries) + "|emits=" + str(self._emitted) + "|orders=" + str(self._orders)
            + "|switches=" + str(self._switches) + "|lost=" + str(self._lost) + "|late=" + str(self._late)
            + "|early=" + str(self._early) + "|noref=" + str(self._noref) + "|bad=" + str(self._bad)
            + "|bars=" + str(self._bars) + "|quotes=0|wide=0|badq=0"
            + "|records=" + str(self._records) + "|missing=" + str(self._missing))
    self.log(head[:LOG_BUDGET_BYTES - 80])
    self.log(PREFIX + "|END")
"""


__all__ = ["FLIP_PREFIX", "FLIP_TAG_CHARS", "FLIP_RUN", "config", "windows", "params", "preamble", "BODY",
           "DST_RUN", "DST_PREFIX", "DST_HEAD_EXTRA", "config_dst", "windows_dst", "params_dst", "preamble_dst",
           "BODY_DST",
           "COLLECT_RUN", "COLLECT_PREFIX", "COLLECT_HEAD_EXTRA", "config_collect", "windows_collect",
           "collect_release_days", "params_collect", "preamble_collect", "BODY_COLLECT",
           "FLIPDESIGN_RUN", "FLIPDESIGN_PREFIX", "DESIGN_HEAD_EXTRA", "config_design", "windows_design",
           "params_design", "preamble_design", "BODY_DESIGN",
           "FLIP_SECONDS_RUN", "FLIP_SECONDS_PREFIX", "SECONDS_HEAD_EXTRA", "config_seconds", "windows_seconds",
           "params_seconds", "preamble_seconds", "BODY_SECONDS", "FLIPDIR_RUN", "FLIPDIR_PREFIX",
           "DIRECTION_HEAD_EXTRA", "config_direction", "windows_direction", "params_direction", "preamble_direction",
           "BODY_DIRECTION", "FLIPANY_RUN", "FLIPANY_PREFIX", "ANYTIME_HEAD_EXTRA", "config_anytime",
           "windows_anytime", "params_anytime", "preamble_anytime", "BODY_ANYTIME"]
