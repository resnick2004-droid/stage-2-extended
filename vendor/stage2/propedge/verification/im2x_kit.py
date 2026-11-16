"""The IM2X kit: QuantConnect's side of IM2's second implementation (D-200; docs/verification/im2_second_implementation.md).

Rendered through `propedge.data.qc_template.render_algorithm(name=..., start=<warm-up start>, end=<window end>,
body=IM2X_BODY, preamble=im2x_preamble(market, warm_start, window_start, window_end))`. The preamble carries the
market's and the window's constants from `config/model_im2.yaml`, the source of `im2x_core.py` verbatim, and the
helpers below; the rendered algorithm needs only what LEAN provides. It exports each session as order tags and ends
with the HEAD and END log lines, exactly as the brief's section 4 states.
"""
import datetime as _imx_dt
import inspect
from pathlib import Path

import yaml

from propedge.verification import im2x_core

#: config/model_im2.yaml, read by the preamble (brief section 2).
CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "model_im2.yaml"

#: Each market's continuous future in LEAN: its ticker and exchange (P-04 section 3: CME for ES and 6E, NYMEX for CL
#: and NG).
LEAN_FUTURE = {
    "ES": ("ES", "Market.CME"),
    "CL": ("CL", "Market.NYMEX"),
    "6E": ("6E", "Market.CME"),
    "NG": ("NG", "Market.NYMEX"),
}

#: The most characters of signals one chunk's x may hold (brief section 4).
X_LIMIT = 600


# --- helpers embedded in the algorithm (pure Python; tested here) --------------------------------------------------

def _imx_fmt(v):
    """A price or band as the brief writes it: "%.12g"; empty when absent (brief section 4)."""
    return "" if v is None else "%.12g" % v


def _imx_signal_text(s):
    """One signal as `<+|-><HHMM>,<close>,<upper>,<lower>,<vwap>` (brief section 4)."""
    t, side, close, ub, lb, vwap = s
    return "%s%02d%02d,%s,%s,%s,%s" % ("+" if side > 0 else "-", t // 60, t % 60,
                                       _imx_fmt(close), _imx_fmt(ub), _imx_fmt(lb), _imx_fmt(vwap))


def _imx_chunks(items, limit):
    """The signals joined by "/" into chunks of at most `limit` characters each, in order; at least one chunk,
    which may be empty (brief section 4)."""
    chunks = []
    cur = ""
    for it in items:
        if cur and len(cur) + 1 + len(it) > limit:
            chunks.append(cur)
            cur = it
        else:
            cur = (cur + "/" + it) if cur else it
    chunks.append(cur)
    return chunks


def _imx_ymd(d):
    """A date as YYYYMMDD."""
    return "%04d%02d%02d" % (d.year, d.month, d.day)


def _imx_tags(n, d, contract, cal, sk, res, pc, np_, gone, limit):
    """A session's order tags: chunk 0 in the long form, the others in the short form (brief section 4).

    An odd number of chunks gets one more, empty, so a session's carriers (one order each, sides alternating) leave
    the contract flat (IM2X_NOTES.md).
    """
    xs = _imx_chunks([_imx_signal_text(s) for s in res["signals"]], limit)
    if len(xs) % 2:
        xs.append("")
    big_k = len(xs)
    first = ("IMX;n=%d;k=0;K=%d;d=%s;c=%s;cal=%s;sk=%s;st=%d;full=%d;cov=%.4f;ref=%s;pc=%s;np=%d;"
             "sig=%d;mis=%d;nbd=%d;gone=%s;x=%s") % (
        n, big_k, _imx_ymd(d), contract, cal, sk, res["st"], res["full"], res["cov"], _imx_fmt(res["open"]),
        _imx_fmt(pc), np_, res["sig"], res["mis"], res["nbd"], ",".join(_imx_ymd(g) for g in gone), xs[0])
    return [first] + ["IMX;n=%d;k=%d;K=%d;x=%s" % (n, k, big_k, xs[k]) for k in range(1, big_k)]


def _imx_as_date(x):
    """A Python or .NET date-time as a date."""
    if isinstance(x, _imx_dt.datetime):
        return x.date()
    if isinstance(x, _imx_dt.date):
        return x
    try:
        return _imx_dt.date(int(x.year), int(x.month), int(x.day))
    except AttributeError:
        return _imx_dt.date(int(x.Year), int(x.Month), int(x.Day))


def _imx_dates(coll):
    """The dates of a LEAN calendar collection -- a set of dates (holidays) or a dictionary keyed by date (early
    closes, late opens) -- as a set of dates (brief 3.4)."""
    keys = getattr(coll, "keys", None)
    items = coll if keys is None else (keys() if callable(keys) else keys)
    out = set()
    for x in items:
        k = getattr(x, "key", None)
        if k is None:
            k = getattr(x, "Key", None)
        out.add(_imx_as_date(x if k is None else k))
    return out


_EMBEDDED_HELPERS = (_imx_fmt, _imx_signal_text, _imx_chunks, _imx_ymd, _imx_tags, _imx_as_date, _imx_dates)


# --- LEAN-only helpers (need AlgorithmImports; not importable here) -------------------------------------------------

_LEAN_HELPERS = '''
class _ImxZeroFeeInitializer(BrokerageModelSecurityInitializer):
    """The brokerage model's reality models with a zero fee model: the carrier orders cost nothing (brief section 4)."""

    def __init__(self, brokerage_model, security_seeder):
        super().__init__(brokerage_model, security_seeder)

    def initialize(self, security):
        super().initialize(security)
        security.set_fee_model(ConstantFeeModel(0))
'''


# --- the class members -------------------------------------------------------------------------------------------

IM2X_BODY = '''
def setup(self):
    """Subscribe the market's continuous future and read its exchange calendar (brief 3.3, 3.4); the carriers cost
    nothing (brief section 4)."""
    self.set_time_zone(TimeZones.CHICAGO)
    self.set_security_initializer(_ImxZeroFeeInitializer(self.brokerage_model, SecuritySeeder.NULL))
    self._imx_future = self.add_future(IMX_TICKER, Resolution.MINUTE, market=IMX_LEAN_MARKET, fill_forward=False,
                                       extended_market_hours=True,
                                       data_mapping_mode=DataMappingMode.OPEN_INTEREST,
                                       data_normalization_mode=DataNormalizationMode.RAW,
                                       contract_depth_offset=0)
    self._imx_future.set_filter(0, 120)
    hours = self._imx_future.exchange.hours
    self._imx_hol = _imx_dates(hours.holidays)
    self._imx_ec = _imx_dates(hours.early_closes)
    self._imx_lo = _imx_dates(hours.late_opens)
    self._imx_universe = set()
    self._imx_active = None
    self._imx_left = False
    self._imx_vol = {}
    self._imx_cur = None
    self._imx_pc = None
    self._imx_store = []
    self._imx_pos = {}
    self._imx_gone_from = IMX_WINDOW_START
    self._imx_n = 0
    self._imx_warm = 0
    self._imx_signals = 0
    self._imx_orders = 0
    self._imx_switches = 0

def on_securities_changed(self, changes):
    """Track the contracts in the universe; flag the active contract leaving it, so the continuous future names its
    replacement (brief 3.3)."""
    for security in changes.added_securities:
        s = security.symbol
        if s.security_type == SecurityType.FUTURE and not s.is_canonical():
            self._imx_universe.add(s)
    for security in changes.removed_securities:
        s = security.symbol
        self._imx_universe.discard(s)
        if self._imx_active is not None and s == self._imx_active:
            self._imx_left = True

def on_data(self, data):
    """Each minute: a roll a session's missing close left pending, the session's bars, and the roll at the session's
    close bar (brief 3.1, 3.3). Minutes are the algorithm's clock, set to Chicago."""
    bars = {}
    for symbol, bar in data.bars.items():
        if symbol.security_type == SecurityType.FUTURE and not symbol.is_canonical() and not bar.is_fill_forward:
            bars[symbol] = bar
    if not bars:
        return
    t = self.time
    d = _imx_dt.date(t.year, t.month, t.day)
    m = t.hour * 60 + t.minute
    for symbol, bar in bars.items():
        self._imx_vol[symbol] = self._imx_vol.get(symbol, 0.0) + float(bar.volume)
    if self._imx_cur is not None and self._imx_cur["date"] < d:
        self._imx_close_session(None)
    if self._imx_active is None or self._imx_left:
        mapped = self._imx_future.mapped
        if mapped is not None and (self._imx_active is None or mapped != self._imx_active):
            if self._imx_active is not None:
                self._imx_switches += 1
            self._imx_active = mapped
            self._imx_left = False
    if self._imx_active is None:
        return
    bar = bars.get(self._imx_active)
    if bar is not None and IMX_OPEN < m <= IMX_CLOSE:
        if self._imx_cur is None:
            self._imx_cur = {"date": d, "code": self._imx_code(d), "contract": self._imx_active, "bars": []}
        self._imx_cur["bars"].append((m, float(bar.open), float(bar.high), float(bar.low), float(bar.close),
                                      float(bar.volume)))
    if self._imx_cur is not None and self._imx_cur["date"] == d and IMX_CLOSE <= m < IMX_DAY_END:
        self._imx_close_session(bars if m == IMX_CLOSE else None)

def on_end_of_algorithm(self):
    """Close a session the data left open, then log the HEAD line and END (brief section 4)."""
    if self._imx_cur is not None:
        self._imx_close_session(None)
    gone = self._imx_gone(self._imx_gone_from, IMX_WINDOW_END)
    ws, we = IMX_WINDOW_START, IMX_WINDOW_END
    hol = len([x for x in self._imx_hol if ws <= x <= we])
    ec = len([x for x in self._imx_ec if ws <= x <= we])
    lo = len([x for x in self._imx_lo if ws <= x <= we])
    self.log("IMX|HEAD|v=1|market=%s|days=%d|warm=%d|signals=%d|orders=%d|switches=%d|hol=%d|ec=%d|lo=%d|gone=%s"
             % (IMX_MARKET, self._imx_n, self._imx_warm, self._imx_signals, self._imx_orders, self._imx_switches,
                hol, ec, lo, ",".join(_imx_ymd(g) for g in gone)))
    self.log("IMX|END")

def _imx_code(self, d):
    """The date's calendar code: H listed holiday, E listed early close, L listed late open, W weekend, F otherwise
    (brief 3.4; the first that applies)."""
    if d in self._imx_hol:
        return "H"
    if d in self._imx_ec:
        return "E"
    if d in self._imx_lo:
        return "L"
    if d.weekday() >= 5:
        return "W"
    return "F"

def _imx_prev_session(self, d):
    """The exchange's previous session: the last earlier weekday that is not a listed holiday (brief 3.4)."""
    p = d - _imx_dt.timedelta(days=1)
    while p.weekday() >= 5 or p in self._imx_hol:
        p = p - _imx_dt.timedelta(days=1)
    return p

def _imx_gone(self, first, last):
    """Weekdays from first to last that are none of H, E, L (brief 3.4, `gone`); the caller passes a span with no
    session record in it."""
    out = []
    x = first
    while x <= last:
        if self._imx_code(x) == "F":
            out.append(x)
        x = x + _imx_dt.timedelta(days=1)
    return out

def _imx_skip(self, cur, pc, np_):
    """The session's skip reason, the first that applies: cal, noprev, roll, look, late, or empty (brief 3.4)."""
    code = cur["code"]
    if code not in ("F", "L"):
        return "cal"
    if pc is None or pc[2] != self._imx_prev_session(cur["date"]):
        return "noprev"
    if pc[1] != cur["contract"]:
        return "roll"
    if np_ < IMX_PARAMS["lookback"]:
        return "look"
    if code == "L":
        return "late"
    return ""

def _imx_roll(self, d):
    """The roll: switch to the contract in the universe expiring after today (d, the date the roll happens on) with
    the most volume since the previous close bar; keep the active one if there is none, or if it ties for the most
    (brief 3.3)."""
    vol = self._imx_vol
    self._imx_vol = {}
    best = []
    best_vol = 0.0
    for s in self._imx_universe:
        if _imx_as_date(s.id.date) <= d:
            continue
        v = vol.get(s, 0.0)
        if v <= 0:
            continue
        if v > best_vol:
            best, best_vol = [s], v
        elif v == best_vol:
            best.append(s)
    if not best:
        return
    active = self._imx_active
    if active is not None and any(s == active for s in best):
        return
    best.sort(key=lambda s: (_imx_as_date(s.id.date), str(s.value)))
    if active is not None:
        self._imx_switches += 1
    self._imx_active = best[0]
    self._imx_left = False

def _imx_close_session(self, close_bars):
    """Close the open session: its skip reason and evaluation, then the roll, the prior close and the lookback store
    it leaves the next session (brief 3.3, 3.4), then its export or its count as a warm-up session."""
    cur = self._imx_cur
    self._imx_cur = None
    d = cur["date"]
    code = cur["code"]
    pc = self._imx_pc
    np_ = len(self._imx_store)
    sk = self._imx_skip(cur, pc, np_)
    use_pc = pc[0] if (pc is not None and sk in ("", "late")) else None
    res = evaluate_session(cur["bars"], use_pc, self._imx_store, IMX_PARAMS)
    if code != "H":
        self._imx_roll(_imx_dt.date(self.time.year, self.time.month, self.time.day))
        gives = res["full"] == 1 and code != "E"
        new_pc = None
        if gives and close_bars is not None:
            b = close_bars.get(self._imx_active)
            if b is not None:
                new_pc = (float(b.close), self._imx_active, d)
        self._imx_pc = new_pc
        if gives:
            self._imx_store.append(cur["bars"])
            if len(self._imx_store) > IMX_PARAMS["lookback"]:
                del self._imx_store[0]
    if d < IMX_WINDOW_START:
        self._imx_warm += 1
        return
    self._imx_n += 1
    gone = self._imx_gone(self._imx_gone_from, d - _imx_dt.timedelta(days=1))
    self._imx_gone_from = d + _imx_dt.timedelta(days=1)
    self._imx_signals += res["sig"]
    tags = _imx_tags(self._imx_n, d, str(cur["contract"].value), code, sk, res,
                     None if pc is None else pc[0], np_, gone, IMX_X_LIMIT)
    target = self._imx_active if self._imx_active is not None else cur["contract"]
    for tag in tags:
        self._imx_carry(target, tag)

def _imx_carry(self, symbol, tag):
    """One carrier: a market order of one contract, the side alternating so the position stays flat or one contract
    long (brief section 4)."""
    held = self._imx_pos.get(symbol, 0)
    q = -1 if held > 0 else 1
    self.market_order(symbol, q, tag=tag)
    self._imx_pos[symbol] = held + q
    self._imx_orders += 1
'''


def _minutes(hhmm: str) -> int:
    """'HH:MM' as minutes after midnight."""
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def load_config(path: Path = CONFIG_PATH) -> dict:
    """config/model_im2.yaml as a dictionary."""
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def im2x_params(market: str, config: dict | None = None) -> dict:
    """evaluate_session's params for a market, from config/model_im2.yaml (brief section 2 and 3)."""
    cfg = load_config() if config is None else config
    if market not in cfg["markets"]:
        raise ValueError(f"market {market!r} is not in config/model_im2.yaml")
    mk = cfg["markets"][market]
    return {
        "open": _minutes(str(mk["open"])),
        "close": _minutes(str(mk["close"])),
        "lookback": int(cfg["lookback_sessions"]),
        "multiplier": float(cfg["volatility_multiplier"]),
        "decision_every": int(cfg["decision_every_minutes"]),
        "decision_margin": int(cfg["decision_margin_minutes"]),
        "min_coverage": float(cfg["min_coverage"]),
    }


def im2x_preamble(market: str, warm_start: _imx_dt.date, window_start: _imx_dt.date,
                  window_end: _imx_dt.date) -> str:
    """Module-level code placed before the class: the market's and window's constants, im2x_core.py verbatim, and
    the helpers (brief section 2)."""
    if market not in LEAN_FUTURE:
        raise ValueError(f"market {market!r} is not one of {sorted(LEAN_FUTURE)}")
    if not (warm_start < window_start <= window_end):
        raise ValueError(f"expected warm-up start < window start <= window end, got {warm_start}, {window_start}, "
                         f"{window_end}")
    params = im2x_params(market)
    ticker, lean_market = LEAN_FUTURE[market]

    def ymd(d: _imx_dt.date) -> str:
        return f"_imx_dt.date({d.year}, {d.month}, {d.day})"

    head = "\n".join([
        "# IM2X: IM2's noise band and signals, the second implementation (D-200;",
        "# docs/verification/im2_second_implementation.md). Built by propedge/verification/im2x_kit.py.",
        "import datetime as _imx_dt",
        "",
        f"IMX_MARKET = {market!r}",
        f"IMX_TICKER = {ticker!r}",
        f"IMX_LEAN_MARKET = {lean_market}",
        f"IMX_WARM_START = {ymd(warm_start)}",
        f"IMX_WINDOW_START = {ymd(window_start)}",
        f"IMX_WINDOW_END = {ymd(window_end)}",
        f"IMX_PARAMS = {params!r}",
        "IMX_OPEN = IMX_PARAMS['open']",
        "IMX_CLOSE = IMX_PARAMS['close']",
        "IMX_DAY_END = 16 * 60  # 16:00 CT: a roll bar ends at or after the close and before this (brief 3.3)",
        f"IMX_X_LIMIT = {X_LIMIT}",
        "",
    ])
    core = "# --- propedge/verification/im2x_core.py, verbatim ---\n" + inspect.getsource(im2x_core)
    helpers = "# --- helpers from propedge/verification/im2x_kit.py ---\n" + "\n\n".join(
        inspect.getsource(f) for f in _EMBEDDED_HELPERS)
    return "\n\n".join([head, core, helpers, _LEAN_HELPERS.strip("\n")]) + "\n"
