"""The resolution map's QuantConnect kits (config/resolution_map.yaml; D-213 part 2, D-214): R071-R080.

Each kit runs one market over one development half on Topstep's trading day (17:00 CT the evening before to the 15:10
CT flatten): at every hourly decision from 17:00 to 14:00, a long and a short bracket at each fixed stop
(dollars per micro), walked by `propedge/outcomes/resolution_core` (embedded verbatim) to its target at 1R and 2R, its
stop, or the day's last bar. Only counts leave the cloud (D-120): per year, decision, stop and R the brackets at the
target first, at the stop first and still open, with the minutes to resolution, and per year and decision the entry
minute's bid-ask spread in the micro's ticks. They leave in order tags, a year's cells at the year's end, so nothing
depends on orders placed after the data ends.

The kit's own choices, fixed with the config before any of its data is read:

* **The trading day** is keyed by the calendar date of its 15:10 close: a bar ending after 17:00 belongs to the next
  date's day (Sunday evening to Monday). The day closes, and the contract rolls, at the first bar after 15:10 CT
  (CME trades until 16:00); a day whose data has no bar after 15:10 closes at the next day's first bar.
* **The roll** goes to the contract, among those in the universe expiring after the day, with the most volume since
  the last roll (the bracket map's version 3 bookkeeping, D-132, D-134); bars of any other contract are not recorded.
* **Rescaling** (D-106): each day's bars are rescaled so the day's first bar's open maps to the market's `p_ref`, and
  the fixed stops are read in those terms; the spread is measured on the raw quotes, in the micro's tick, and the
  one-tick entry slippage is the micro's tick, unscaled.
* **Spreads** are the standard contract's (the micros did not trade before 2019 or 2021): a reading of the market's
  depth, not of the micro's own book. Only a two-sided, uncrossed quote counts; one wider than the cap is kept out
  of the mean and counted (`badq`), those above the wide line are counted (`wide`) (D-215).
* **Early closes apart** (D-215): a day whose last bar ends before 15:00 CT -- a scheduled early close, or a holiday's
  evening-only day -- is counted in its own `E` cells, so its noon-closed brackets do not join the full sessions' open
  share.
* **The roll's fallback** (D-215): a day with no bar in the 15:10-17:00 gap rolls at the next day's first bar
  (`late`); after the window's last export the kit reads nothing more; a day with no positive opening price is
  skipped (`noref`).
* **An expired contract** (D-223; body version 3, kits R080 and R081): a held contract whose expiry is before the
  current trading day has no more bars, so it is dropped as a contract that left the universe is (`lost`) and the
  kit falls back to the mapped contract and rolls. Version 2 waited for the held contract's next bar and froze when it
  never came: R079 (NG) counted 86 days and nothing after. The eight version-2 runs that counted their full windows
  never held a contract past its expiry -- it would have frozen them -- so version 3 reads them exactly as version 2.
"""
from __future__ import annotations

import inspect
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from propedge import CONFIG_DIR

RMAP_PREFIX = "RM1"
RMAP_TAG_CHARS = 600
LOG_BUDGET_BYTES = 6000
MARKETS = ("ES", "NQ", "CL", "6E", "NG")
HALVES = ("0914", "1419")
_FIRST_RUNS = {(m, h): f"R{71 + 2 * i + j:03d}-rmap-{m}-{h}" for i, m in enumerate(MARKETS)
               for j, h in enumerate(HALVES)}
# D-223: R079 froze on an expired contract and is kept on record, unusable; its half is read from R081, a fixed kit
RMAP_RERUNS = {("NG", "0914"): "R081-rmap-NG-0914"}
RMAP_SUPERSEDED = {"R079-rmap-NG-0914": "froze on an expired contract after 86 days; unusable, not ingested (D-223)"}
RMAP_RUNS = {k: RMAP_RERUNS.get(k, v) for k, v in _FIRST_RUNS.items()}      # the run each market and half is read from
RMAP_KITS = {**{v: k for k, v in _FIRST_RUNS.items()}, **{v: k for k, v in RMAP_RERUNS.items()}}  # every kit: (mk, half)
TICKERS = {"ES": "ES", "NQ": "NQ", "CL": "CL", "6E": "6E", "NG": "NG"}
# D-225 (EXPLORATORY): the map at today's price levels -- the markets whose reference moved, rerun; the rest read from
# their development-scale runs (config/resolution_map_today.yaml)
TODAY_MARKETS = ("ES", "NQ", "CL")
TODAY_RUNS = {(m, h): f"R{82 + 2 * i + j:03d}-rmap-today-{m}-{h}" for i, m in enumerate(TODAY_MARKETS)
              for j, h in enumerate(HALVES)}
RMAP_TODAY_KITS = {v: k for k, v in TODAY_RUNS.items()}
RMAP_TODAY_READ = {k: TODAY_RUNS.get(k, v) for k, v in RMAP_RUNS.items()}   # the run each half is read from, today
BODY_V3_RUNS = frozenset({"R080-rmap-NG-1419", "R081-rmap-NG-0914", *TODAY_RUNS.values()})   # D-223's fix; D-225


def config(path: Path | None = None) -> dict[str, Any]:
    return yaml.safe_load(Path(path or CONFIG_DIR / "resolution_map.yaml").read_text(encoding="utf-8"))


def config_today(path: Path | None = None) -> dict[str, Any]:
    return yaml.safe_load(Path(path or CONFIG_DIR / "resolution_map_today.yaml").read_text(encoding="utf-8"))


def _min(hm: str) -> int:
    h, m = hm.split(":")
    return int(h) * 60 + int(m)


def windows(cfg: dict | None = None) -> dict[str, tuple[date, date, date]]:
    """{half: (warm-up start, window start, window end)}."""
    cfg = cfg or config()
    return {h: tuple(date.fromisoformat(cfg["halves"][h][k]) for k in ("warm", "start", "end")) for h in HALVES}


def params(market: str, cfg: dict | None = None, scale: str = "dev") -> dict[str, Any]:
    """What the kit and the scorer need for a market: decision slots, stops in price at the reference scale, the slip,
    R, the reference price and the micro's tick. `scale` "today" takes the reference price from
    config/resolution_map_today.yaml (D-225); nothing else changes."""
    from propedge.outcomes.resolution_core import slot_of

    cfg = cfg or config()
    mk = dict(cfg["markets"][market])
    if scale == "today":
        mk["p_ref"] = config_today()["p_ref"][market]
    elif scale != "dev":
        raise ValueError(f"scale must be 'dev' or 'today', got {scale!r}")
    w = cfg["window"]
    first = 0                                                    # 17:00, minutes after 17:00
    last = slot_of(*map(int, w["last_decision_ct"].split(":")))
    times = list(range(first, last + 1, int(w["decision_every_min"])))
    pv = float(mk["micro_point_value"])
    return {"market": market, "micro": mk["micro"], "p_ref": float(mk["p_ref"]), "tick": float(mk["tick"]),
            "micro_tick": float(mk["micro_tick"]), "micro_point_value": pv,
            "stop_dollars": [float(x) for x in cfg["stop_dollars_per_micro"]],
            "spread": {"wide_ticks": float(cfg["spread"]["wide_ticks"]),
                       "cap_ticks": float(cfg["spread"]["cap_ticks"])},
            "p": {"times": times, "stops": [float(x) / pv for x in cfg["stop_dollars_per_micro"]],
                  "slip": float(mk["micro_tick"]), "rr": tuple(float(r) for r in cfg["rr"])}}


def preamble(market: str, half: str, scale: str = "dev") -> str:
    _, w0, w1 = windows()[half]
    return _preamble(market, params(market, scale=scale), w0, w1)


def _preamble(market: str, q: dict[str, Any], w0: date, w1: date, extra: str = "") -> str:
    from propedge.outcomes import resolution_core

    return f'''
MARKET = "{TICKERS[market]}"
P_REF = {q["p_ref"]!r}                  # each day rescaled so its first bar's open maps here (D-106)
TICK = {q["tick"]!r}                    # the standard contract's tick (the data)
MICRO_TICK = {q["micro_tick"]!r}        # the micro's tick (slippage, spreads)
WIN_START = ({w0.year}, {w0.month}, {w0.day})   # days before this are warm-up and record nothing
WIN_END = ({w1.year}, {w1.month}, {w1.day})
FILTER_DAYS = 120
PREFIX = "{RMAP_PREFIX}"
LOG_BUDGET_BYTES = {LOG_BUDGET_BYTES}
TAG_CHARS = {RMAP_TAG_CHARS}
PARAMS = {q["p"]!r}
WIDE_SPREAD_TICKS = {q["spread"]["wide_ticks"]!r}   # D-215: counted (wide)
WIDE_SPREAD_CAP = {q["spread"]["cap_ticks"]!r}     # D-215: kept out of the mean, counted (badq)
{extra}from datetime import timedelta as _delta


class CarrierInitializer(BrokerageModelSecurityInitializer):
    """Zero fees: the carrier orders' own P&L is never used, so nothing is modelled on them."""

    def initialize(self, security):
        super().initialize(security)
        security.set_fee_model(ConstantFeeModel(0))


# ---------------------------------------------------------------- embedded verbatim from
# ---------------------------------------------------------------- propedge/outcomes/resolution_core.py
{inspect.getsource(resolution_core)}
# ---------------------------------------------------------------- end of the embedded core
'''


BODY = """
def setup(self):
    # D-214, D-215: the resolution map, measured in the cloud on Topstep's trading day; version 3 contract bookkeeping.
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
    if self._active is not None and self._active not in self.securities:
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
                         "l": [None] * (FLAT + 1), "q": [None] * (FLAT + 1)}
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
    d["o"][j], d["h"][j], d["l"][j] = o, h, l
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
    if d["td"] < WIN_START or d["td"] > WIN_END:
        self._warm += 1
        return
    year = d["td"][0]
    if self._year is not None and year != self._year:
        self._emit()
    self._year = year
    self._n += 1
    o, h, l, q = d["o"], d["h"], d["l"], d["q"]
    j = next((i for i in range(FLAT + 1) if o[i] is not None), None)
    if j is None or o[j] <= 0:
        self._noref += 1
    else:
        ls = last_slot(o)
        early = ls is not None and ls < FLAT - 10
        if early:
            self._early += 1                     # D-215: an early close's brackets are counted apart
        so, sh, sl = scaled(o, h, l, o[j], P_REF)
        rows = run_day(so, sh, sl, PARAMS)
        self._entries += len(rows)
        add_day(self._acc_e if early else self._acc, year, rows)
        add_spreads(self._spr, year, entry_spreads(o, q, PARAMS), MICRO_TICK)
    if d["td"] >= WIN_END:
        self._emit()
        self._done = True

def _emit(self):
    # one year's (or the rest's) counts, in order tags of at most TAG_CHARS; the accumulators then start afresh.
    # C: full sessions, E: early closes (D-215), S: spreads.
    rr = list(PARAMS["rr"])
    cells = (["C" + x for x in encode_counts(self._acc, rr)] + ["E" + x for x in encode_counts(self._acc_e, rr)]
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
        tag = "R|e=" + str(self._emitted) + ";k=" + str(k) + ";K=" + str(len(chunks)) + ";x=" + x
        self._orders += 1
        self.market_order(carrier, 1 if self._orders % 2 else -1, tag=tag)

def on_end_of_algorithm(self):
    if self._day is not None and not self._done:
        self._close_day()
    if self._acc or self._acc_e or self._spr:
        self._emit()
    head = (PREFIX + "|HEAD|v=2|market=" + MARKET + "|days=" + str(self._n) + "|warm=" + str(self._warm)
            + "|entries=" + str(self._entries) + "|emits=" + str(self._emitted) + "|orders=" + str(self._orders)
            + "|switches=" + str(self._switches) + "|lost=" + str(self._lost) + "|late=" + str(self._late)
            + "|early=" + str(self._early) + "|noref=" + str(self._noref) + "|bad=" + str(self._bad)
            + "|bars=" + str(self._bars) + "|quotes=" + str(self._quotes) + "|wide=" + str(self._wide)
            + "|badq=" + str(self._badq))
    self.log(head[:LOG_BUDGET_BYTES - 80])
    self.log(PREFIX + "|END")
"""

_HELD = "    if self._active is not None and self._active not in self.securities:\n"
assert BODY.count(_HELD) == 1
BODY_V3 = BODY.replace(_HELD, (
    "    if self._active is not None and (self._active not in self.securities\n"
    "                                     or self._active.id.date.date() < _date(*self._trading_day())):\n"
    "        # D-223: a held contract past its expiry has no more bars; waiting for one froze version 2 (R079)\n"))


def body(run_id: str) -> str:
    """The algorithm body a kit carries: version 3 for the kits unrun when D-223's fix came, version 2 as run."""
    return BODY_V3 if run_id in BODY_V3_RUNS else BODY


# ---------------------------------------------------------------- NQB1's confirmation (D-229)
# The kit that reads the held-back window once, for the registered pre-registration only: version 3 with nothing changed
# but the brackets it keeps -- each stop at its own leg's R -- so no other cell of the confirmation window is counted.
CONFIRM_RUN = "R088-rmap-confirm-NQ-2026"
_RUN_DAY = "        rows = run_day(so, sh, sl, PARAMS)\n"
assert BODY_V3.count(_RUN_DAY) == 1
BODY_CONFIRM = BODY_V3.replace(_RUN_DAY, (
    "        rows = [(ti, si, d, {R: v for R, v in outs.items() if (si, R) in KEEP})\n"
    "                for ti, si, d, outs in run_day(so, sh, sl, PARAMS)]   # D-229: the registered brackets only\n"))


def confirm_config(path: Path | None = None) -> dict[str, Any]:
    return yaml.safe_load(Path(path or CONFIG_DIR / "nqb1_confirmation.yaml").read_text(encoding="utf-8"))


def confirm_params(cfg: dict | None = None) -> dict[str, Any]:
    """The confirmation's parameters: the development map's contract terms and rules (`params`) at the registered
    reference price, decision slots and brackets; `keep` lists each kept (stop index, R)."""
    c = cfg or confirm_config()
    base = params(c["market"])
    pv = base["micro_point_value"]
    legs = [c["legs"][k] for k in ("combine", "funded")]
    stops = [float(x["stop_dollars"]) for x in legs]
    rr = tuple(sorted({float(x["R"]) for x in legs}))
    p = dict(base["p"], times=[int(t) for t in c["decision_slots"]], stops=[s / pv for s in stops], rr=rr)
    return dict(base, p_ref=float(c["p_ref"]), stop_dollars=stops, p=p,
                keep=[(i, float(x["R"])) for i, x in enumerate(legs)])


def confirm_windows(cfg: dict | None = None) -> tuple[date, date, date]:
    c = cfg or confirm_config()
    return tuple(date.fromisoformat(str(c["window"][k])) for k in ("warm", "start", "end"))


def confirm_preamble(cfg: dict | None = None) -> str:
    c = cfg or confirm_config()
    q = confirm_params(c)
    _, w0, w1 = confirm_windows(c)
    keep = "{" + ", ".join(f"({i}, {R!r})" for i, R in q["keep"]) + "}"
    return _preamble(c["market"], q, w0, w1, extra=f"KEEP = {keep}   # D-229: each stop at its own leg's R only\n")


__all__ = ["RMAP_PREFIX", "RMAP_TAG_CHARS", "MARKETS", "HALVES", "RMAP_RUNS", "RMAP_RERUNS", "RMAP_SUPERSEDED",
           "RMAP_KITS", "TODAY_MARKETS", "TODAY_RUNS", "RMAP_TODAY_KITS", "RMAP_TODAY_READ", "BODY_V3_RUNS", "config",
           "config_today", "windows", "params", "preamble", "BODY", "BODY_V3", "body", "CONFIRM_RUN", "BODY_CONFIRM",
           "confirm_config", "confirm_params", "confirm_windows", "confirm_preamble"]
