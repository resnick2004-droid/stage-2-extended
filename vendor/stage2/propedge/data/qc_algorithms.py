"""Algorithm bodies for manual runs in QuantConnect's free web editor (D-81, D-82).

Each body is rendered through `propedge.data.qc_template.render_algorithm`, so the
confirmation-window guard is embedded in it, and packaged as a run kit by
`propedge/data/run_kit.py`.

**Designed for the free tier** (limits read 2026-09-23 on
quantconnect.com/docs/v2/cloud-platform/organizations/resources: *Free: 10KB of logs per
backtest, 3MB per day; 1 backtest node*; free data *"ranges from minute to daily resolutions"*):

* minute resolution or coarser, never second or tick;
* nothing logged per bar or per trade. Each algorithm writes **one compact summary at the end**,
  measured against `LOG_BUDGET_BYTES` (well under 10 KB). If the summary would exceed the budget,
  it is truncated **and says so** in its last line, so a cut-off run cannot pass as a complete one;
* per-trade evidence for the reconciliation travels in **order tags**, which reach the repository
  through the backtest's *Download Results* JSON (orders included) and are not a log.

Nothing here has been run. The first run of each kit is also the test of the LEAN-side code;
a failure there is a fix-and-rerun round and is counted in the effort log (D-82).
"""
from __future__ import annotations

from datetime import date

#: Summary budget. The free tier allows 10 KB of logs per backtest; LEAN adds its own lines.
LOG_BUDGET_BYTES = 6000

# ================================================================ R001 -- dataset checks

DATASET_FUTURES = ("ES", "NQ", "GC", "CL", "6E", "ZN", "HG", "NG")
#: Starts months before May 2009 so a contract's first bar shows where its data really begins.
#: A first bar on the start date itself means "on or before", and the parser says so.
DATASET_START = date(2008, 11, 3)
DATASET_END = date(2009, 7, 31)
DATASET_PREFIX = "DSCHK"

DATASET_PREAMBLE = f'''
FUTURES = {list(DATASET_FUTURES)!r}
LOG_BUDGET_BYTES = {LOG_BUDGET_BYTES}
PREFIX = "{DATASET_PREFIX}"
'''

DATASET_BODY = '''
def setup(self):
    # Dataset checks (D-82, run R001): membership, first bar, bar period, roll rule.
    # Nothing is logged until on_end_of_algorithm, so the whole output is one compact summary.
    self.set_cash(1000000)
    self._sym, self._n, self._first, self._period = {}, {}, {}, {}
    self._rolls, self._config, self._errors = {}, {}, []
    try:
        self._sym["SPY"] = self.add_equity("SPY", Resolution.MINUTE, fill_forward=False).symbol
    except Exception as e:
        self._errors.append("SPY:" + type(e).__name__ + ":" + str(e)[:60])
    for t in FUTURES:
        try:
            # Defaults on purpose: the roll rule under test is QuantConnect's default.
            self._sym[t] = self.add_future(t, Resolution.MINUTE, fill_forward=False).symbol
        except Exception as e:
            self._errors.append(t + ":" + type(e).__name__ + ":" + str(e)[:60])
    try:
        us = self.universe_settings
        self._defaults = "mapping=%s;normalisation=%s;depth=%s" % (
            us.data_mapping_mode, us.data_normalization_mode, us.contract_depth_offset)
    except Exception as e:
        self._defaults = "unreadable:" + type(e).__name__
    for t, s in self._sym.items():
        self._n[t], self._first[t], self._period[t], self._rolls[t] = 0, None, None, []
        if t == "SPY":
            continue
        try:
            cfgs = self.subscription_manager.subscription_data_config_service \\
                .get_subscription_data_configs(s)
            self._config[t] = sorted(set(
                "%s/%s/%s" % (c.data_mapping_mode, c.data_normalization_mode,
                              c.contract_depth_offset) for c in cfgs))
        except Exception as e:
            self._config[t] = ["unreadable:" + type(e).__name__]

def on_data(self, data):
    for t, s in self._sym.items():
        bar = data.bars.get(s)
        if bar is None:
            continue
        if self._n[t] == 0:
            self._first[t] = str(bar.end_time)
            self._period[t] = str(bar.period)
        self._n[t] += 1
    for s, ev in data.symbol_changed_events.items():
        for t, cs in self._sym.items():
            if cs == s:
                self._rolls[t].append(str(self.time.date()) + ":" + str(ev.new_symbol))

def on_end_of_algorithm(self):
    lines = [PREFIX + "|HEAD|v=1|defaults=" + self._defaults
             + "|errors=" + (";".join(self._errors) or "none")]
    for t in self._sym:
        lines.append(PREFIX + "|SYM|" + t + "|bars=" + str(self._n[t])
                     + "|first=" + str(self._first[t]) + "|period=" + str(self._period[t])
                     + "|config=" + ",".join(self._config.get(t, ["n/a"])))
    for t in self._sym:
        if t != "SPY":
            lines.append(PREFIX + "|ROLL|" + t + "|n=" + str(len(self._rolls[t]))
                         + "|" + ",".join(self._rolls[t]))
    used, kept, truncated = 0, [], False
    for line in lines:
        if used + len(line) + 1 > LOG_BUDGET_BYTES:
            truncated = True
            break
        kept.append(line)
        used += len(line) + 1
    for line in kept:
        self.log(line)
    self.log(PREFIX + "|END|lines=" + str(len(kept)) + "|of=" + str(len(lines))
             + "|bytes=" + str(used) + "|truncated=" + str(truncated).lower())
'''

# ================================================================ R005 -- GC and HG coverage

#: R001 received no GC or HG bars in 2008-11 -> 2009-07. R005 asks again over the rest of the
#: development period. ES is the control: a run in which ES also receives nothing is broken,
#: not informative, and the parser refuses it. The algorithm is R001's, unchanged except for its
#: comment -- R001's own body is not edited, because its committed hash is on record.
COVERAGE_FUTURES = ("GC", "HG", "ES")
COVERAGE_TARGETS = ("GC", "HG")
COVERAGE_CONTROL = "ES"
COVERAGE_START = date(2009, 8, 3)
COVERAGE_END = date(2014, 5, 27)
#: Five years of open-interest rolls on three contracts is more than R001's nine months, so the
#: budget is larger; LEAN's own lines still leave it under the free tier's 10 KB.
COVERAGE_LOG_BUDGET_BYTES = 9000

COVERAGE_PREAMBLE = f'''
FUTURES = {list(COVERAGE_FUTURES)!r}
LOG_BUDGET_BYTES = {COVERAGE_LOG_BUDGET_BYTES}
PREFIX = "{DATASET_PREFIX}"
'''

COVERAGE_BODY = DATASET_BODY.replace("(D-82, run R001)", "(D-82, run R005)")
assert COVERAGE_BODY != DATASET_BODY

# ================================================================ R002-R004 -- reconciliation

#: D-80: ES on a development-period year ending before 2014-05-28.
RECON_START = date(2013, 5, 28)
RECON_END = date(2014, 5, 27)
RECON_PREFIX = "RECON"
#: PIPELINE.md section 5: stop 20 ticks below entry, target 30 above, flatten 15:10 CT.
RECON_STOP_TICKS = 20
RECON_TARGET_TICKS = 30


def recon_preamble(*, mode: str, tick_size: float, slip: dict[str, float],
                   fee_per_side: float) -> str:
    """Module-level code for the reconciliation algorithm in `mode` A, B or C.

    Every number is passed in from configuration by the kit generator, never typed here.
    """
    return f'''
MODE = {mode!r}                         # A zero cost; B costs on; C LEAN defaults (must be caught)
TICK = {tick_size!r}
STOP_TICKS = {RECON_STOP_TICKS}
TARGET_TICKS = {RECON_TARGET_TICKS}
SLIP_TICKS = {slip!r}   # per side, adverse, from config/fills.yaml
FEE_PER_SIDE = {fee_per_side!r}         # USD per contract per side, from config/fills.yaml
PREFIX = "{RECON_PREFIX}"
LOG_BUDGET_BYTES = {LOG_BUDGET_BYTES}


def _fmt(x):
    return ("%.4f" % x).rstrip("0").rstrip(".")


class RepoFillModel(FutureFillModel):
    """Our fill rules (PIPELINE.md section 2), in LEAN. Used in modes A and B only.

    Market: last price, adverse slippage in ticks. Stop (long exit): a bar that OPENS through
    the stop fills at that open -- never at the stop price on a gap -- else at the stop less
    slippage. Target: only on a strict trade-through (high > limit), never a touch, and never
    in a bar where the stop also triggers (tie-break declared: stop first).
    """

    def __init__(self, algo):
        super().__init__()
        self.algo = algo

    def _slip(self, kind, direction):
        s = SLIP_TICKS.get(kind, 0.0) * TICK
        return s if direction == OrderDirection.BUY else -s

    def market_fill(self, asset, order):
        fill = super().market_fill(asset, order)
        if fill.status == OrderStatus.FILLED:
            kind = "entry" if order.direction == OrderDirection.BUY else "flatten"
            fill.fill_price = asset.price + self._slip(kind, order.direction)
        return fill

    def stop_market_fill(self, asset, order):
        fill = OrderEvent(order, self.algo.utc_time, OrderFee.ZERO)
        o, lo = asset.open, asset.low
        stop = order.stop_price
        if order.direction == OrderDirection.SELL and lo <= stop:
            gapped = o <= stop
            fill.fill_price = o if gapped else stop + self._slip("stop", order.direction)
            fill.fill_quantity = order.quantity
            fill.status = OrderStatus.FILLED
            self.algo.note_gap(order.id, gapped)
        return fill

    def limit_fill(self, asset, order):
        fill = OrderEvent(order, self.algo.utc_time, OrderFee.ZERO)
        limit = order.limit_price
        if order.direction == OrderDirection.SELL and asset.high > limit:
            stop = self.algo.stop_for_target(order.id)
            if stop is not None and asset.low <= stop:
                return fill                               # stop wins the tie
            fill.fill_price = limit + self._slip("target", order.direction)
            fill.fill_quantity = order.quantity
            fill.status = OrderStatus.FILLED
        return fill


class RepoSecurityInitializer(BrokerageModelSecurityInitializer):
    """LEAN's defaults first; then, in A and B only, our fill, fee and slippage models.

    Mode C keeps LEAN's default fill and fee models and adds its fraction-of-price slippage
    (ConstantSlippageModel, PIPELINE.md section 3.2): the negative control must be LEAN's
    behaviour, not ours.
    """

    def __init__(self, algo, brokerage_model, seeder):
        super().__init__(brokerage_model, seeder)
        self.algo = algo

    def initialize(self, security):
        super().initialize(security)
        if MODE in ("A", "B"):
            security.set_fill_model(RepoFillModel(self.algo))
            security.set_fee_model(RepoFeeModel() if MODE == "B" else ConstantFeeModel(0))
            security.set_slippage_model(NullSlippageModel())
        else:
            security.set_slippage_model(ConstantSlippageModel(0.0001))


class RepoFeeModel(FeeModel):
    def get_order_fee(self, parameters):
        return OrderFee(CashAmount(FEE_PER_SIDE * abs(parameters.order.quantity), "USD"))
'''


RECON_BODY = '''
def setup(self):
    # PIPELINE.md section 5 (D-80): long 1 ES at the first bar after 09:31 CT, stop 20 ticks
    # below, target 30 above, flatten 15:10 CT. Unadjusted prices, explicit roll.
    self.set_time_zone(TimeZones.CHICAGO)
    self.set_cash(1000000)
    self.future = self.add_future("ES", Resolution.MINUTE,
                                  data_normalization_mode=DataNormalizationMode.RAW,
                                  data_mapping_mode=DataMappingMode.OPEN_INTEREST,
                                  contract_depth_offset=0)
    self.set_security_initializer(RepoSecurityInitializer(
        self, self.brokerage_model, FuncSecuritySeeder(self.get_last_known_prices)))
    self.schedule.on(self.date_rules.every_day(self.future.symbol),
                     self.time_rules.at(15, 10, TimeZones.CHICAGO), lambda: self._flatten("flatten"))
    self.schedule.on(self.date_rules.every_day(self.future.symbol),
                     self.time_rules.before_market_close(self.future.symbol, 2),
                     lambda: self._flatten("flatten_close"))
    self._n, self._day, self._trade, self._pending_tag = 0, None, None, ""
    self._stops, self._gaps, self._counts, self._last_bar = {}, {}, {}, None

def note_gap(self, order_id, gapped):
    self._gaps[order_id] = gapped

def stop_for_target(self, order_id):
    return self._stops.get(order_id)

def on_data(self, data):
    c = self.future.mapped
    if c is None:
        return
    bar = data.bars.get(c) or data.bars.get(self.future.symbol)
    if bar is None:
        return
    t = self._trade
    if t is not None and t.get("open"):
        if self._last_bar is not None:
            lb = self._last_bar
            t["mx"] = lb.high if t["mx"] is None else max(t["mx"], lb.high)
            t["mn"] = lb.low if t["mn"] is None else min(t["mn"], lb.low)
        self._last_bar = bar
    d = self.time.date()
    if (self._day != d and self.time.hour == 9 and self.time.minute >= 32
            and not self.portfolio.invested and (t is None or not t.get("open"))):
        self._day = d
        self._n += 1
        tag = "E|n=" + str(self._n) + "|ref=" + _fmt(self.securities[c].price) + self._pending_tag
        self._pending_tag = ""
        self._trade = {"n": self._n, "c": c, "open": True, "mx": None, "mn": None,
                       "ref": self.securities[c].price, "stop_id": None, "tgt_id": None}
        self._last_bar = None
        self.market_order(c, 1, tag=tag)

def on_order_event(self, ev):
    if ev.status != OrderStatus.FILLED or self._trade is None:
        return
    t = self._trade
    if ev.direction == OrderDirection.BUY:
        t["entry"] = ev.fill_price
        t["efee"] = float(ev.order_fee.value.amount)
        # Levels sit on the tick grid, as a real order must. In A and B the fill is already on
        # it; in C, fraction-of-price slippage moves it off, and an off-grid target could never
        # be merely touched -- the touch-fill failure mode would be untestable.
        base = round(ev.fill_price / TICK) * TICK
        stop = base - STOP_TICKS * TICK
        tgt = base + TARGET_TICKS * TICK
        st = self.stop_market_order(t["c"], -1, stop, tag="S|n=" + str(t["n"]) + "|p=" + _fmt(stop))
        tg = self.limit_order(t["c"], -1, tgt, tag="T|n=" + str(t["n"]) + "|p=" + _fmt(tgt))
        t["stop_id"], t["tgt_id"], t["stop"], t["tgt"] = st.order_id, tg.order_id, stop, tgt
        self._stops[tg.order_id] = stop
        return
    reason = t.pop("pending_reason", None) or (
        "stop" if ev.order_id == t["stop_id"] else "target" if ev.order_id == t["tgt_id"] else "other")
    self._close(t, reason, ev)

def _flatten(self, reason):
    t = self._trade
    if t is None or not t.get("open") or "entry" not in t:
        return
    self.transactions.cancel_open_orders(t["c"])
    t["pending_reason"] = reason
    self.market_order(t["c"], -1, tag="F|n=" + str(t["n"]) + "|r=" + reason)

def _close(self, t, reason, ev):
    if not t.get("open"):
        return
    t["open"] = False
    self.transactions.cancel_open_orders(t["c"])
    sec = self.securities[t["c"]]
    lb = self._last_bar
    same_bar = lb is not None and lb.end_time == self.time
    xb = lb if same_bar else sec
    if not same_bar and lb is not None:
        t["mx"] = lb.high if t["mx"] is None else max(t["mx"], lb.high)
        t["mn"] = lb.low if t["mn"] is None else min(t["mn"], lb.low)
    self._counts[reason] = self._counts.get(reason, 0) + 1
    gap = self._gaps.get(ev.order_id)
    self._pending_tag = (
        "|prev=" + str(t["n"]) + ";c=" + str(t["c"].value) + ";ent=" + _fmt(t["entry"])
        + ";st=" + _fmt(t["stop"]) + ";tg=" + _fmt(t["tgt"]) + ";xr=" + reason
        + ";xf=" + _fmt(ev.fill_price) + ";xt=" + self.time.strftime("%Y%m%d%H%M")
        + ";mx=" + ("" if t["mx"] is None else _fmt(t["mx"]))
        + ";mn=" + ("" if t["mn"] is None else _fmt(t["mn"]))
        + ";xo=" + _fmt(xb.open) + ";xh=" + _fmt(xb.high) + ";xl=" + _fmt(xb.low)
        + ";xc=" + _fmt(xb.close) + ";gap=" + ("" if gap is None else str(gap).lower())
        + ";efee=" + _fmt(t.get("efee", 0.0)) + ";fee=" + _fmt(float(ev.order_fee.value.amount)))
    self._last_bar = None

def on_end_of_algorithm(self):
    counts = ",".join(k + ":" + str(v) for k, v in sorted(self._counts.items()))
    lines = [PREFIX + "|HEAD|v=1|mode=" + MODE + "|trades=" + str(self._n) + "|exits=" + counts,
             PREFIX + "|LAST" + (self._pending_tag or "|none")]
    used = 0
    for line in lines:
        line = line[:LOG_BUDGET_BYTES - used - 80]
        self.log(line)
        used += len(line) + 1
    self.log(PREFIX + "|END|bytes=" + str(used))
'''


# ================================================================ R006-R008 -- reconciliation v2 (D-94)
#
# Version 1 (above, R002-R004) is kept byte-identical so its runs stay reproducible. D-93 found it
# mixed two price series: LEAN's fills, `ref` and the exit bar read the security cache (quote-bar
# midpoints for ES), while the pre-exit extremes read trade bars. Version 2 reads ONE series for
# every fill decision and every evidence field: the contract's latest trade bar from its cache
# (`security.cache.get_data(TradeBar)`, LEAN's own idiom). Stage C no longer runs LEAN's defaults,
# which in current LEAN neither touch-fill targets nor fill gapped stops at the stop (FillModel.cs:
# strict `>`/`<` on the bid bar, stop at min(stop, current)). It runs planted faults instead, and
# each fill that exercises one is labelled in the trade record (`flt=`), so the negative control has
# ground truth.

#: Stage C's planted fraction-of-price entry slippage. A fault magnitude, not a cost assumption:
#: the value LEAN's ConstantSlippageModel used in v1.
RECON_C_FRACTION = 0.0001


def recon_preamble_v2(*, mode: str, tick_size: float, slip: dict[str, float],
                      fee_per_side: float) -> str:
    """Module-level code for reconciliation v2 in `mode` A, B or C (D-94)."""
    return f'''
MODE = {mode!r}                         # A zero cost; B costs on; C planted faults (must be caught)
TICK = {tick_size!r}
STOP_TICKS = {RECON_STOP_TICKS}
TARGET_TICKS = {RECON_TARGET_TICKS}
SLIP_TICKS = {slip!r}   # per side, adverse, from config/fills.yaml
FEE_PER_SIDE = {fee_per_side!r}         # USD per contract per side, from config/fills.yaml
C_FRACTION = {RECON_C_FRACTION!r}         # stage C only: planted fraction-of-price entry slippage
PREFIX = "{RECON_PREFIX}"
LOG_BUDGET_BYTES = {LOG_BUDGET_BYTES}


def _fmt(x):
    return ("%.4f" % x).rstrip("0").rstrip(".")


def _trade_bar(asset):
    """The contract's latest TRADE bar: the one price series every fill and every record uses."""
    return asset.cache.get_data(TradeBar)


def _fresh(asset, order, tb):
    """Only a bar that ended after the order was placed may fill it (LEAN's own stale-data rule)."""
    placed = Extensions.convert_from_utc(order.time, asset.exchange.time_zone)
    return tb is not None and tb.end_time > placed


class RepoFillModel(FutureFillModel):
    """Our fill rules (PIPELINE.md section 2), in LEAN, on trade bars. Stages A and B.

    Market: the last traded price, adverse slippage in ticks. Stop (long exit): a trade bar that
    OPENS through the stop fills at that open, else at the stop less slippage. Target: only on a
    strict trade-through (high > limit), never in a bar where the stop also triggers (stop first).
    """

    def __init__(self, algo):
        super().__init__()
        self.algo = algo

    def _slip(self, kind, direction):
        s = SLIP_TICKS.get(kind, 0.0) * TICK
        return s if direction == OrderDirection.BUY else -s

    def _entry_price(self, tb):
        return tb.close + self._slip("entry", OrderDirection.BUY)

    def market_fill(self, asset, order):
        fill = super().market_fill(asset, order)
        tb = _trade_bar(asset)
        if fill.status == OrderStatus.FILLED:
            if tb is None:
                return OrderEvent(order, self.algo.utc_time, OrderFee.ZERO)
            if order.direction == OrderDirection.BUY:
                fill.fill_price = self._entry_price(tb)
            else:
                fill.fill_price = tb.close + self._slip("flatten", order.direction)
        return fill

    def _stop_price(self, order, o, stop):
        gapped = o <= stop
        return (o if gapped else stop + self._slip("stop", order.direction)), gapped

    def stop_market_fill(self, asset, order):
        fill = OrderEvent(order, self.algo.utc_time, OrderFee.ZERO)
        tb = _trade_bar(asset)
        stop = order.stop_price
        if order.direction == OrderDirection.SELL and _fresh(asset, order, tb) and tb.low <= stop:
            fill.fill_price, gapped = self._stop_price(order, tb.open, stop)
            fill.fill_quantity = order.quantity
            fill.status = OrderStatus.FILLED
            self.algo.note_gap(order.id, gapped)
        return fill

    def _target_hit(self, order, high, limit):
        return high > limit

    def limit_fill(self, asset, order):
        fill = OrderEvent(order, self.algo.utc_time, OrderFee.ZERO)
        tb = _trade_bar(asset)
        limit = order.limit_price
        if (order.direction == OrderDirection.SELL and _fresh(asset, order, tb)
                and self._target_hit(order, tb.high, limit)):
            stop = self.algo.stop_for_target(order.id)
            if stop is not None and tb.low <= stop:
                return fill                               # stop wins the tie
            fill.fill_price = limit + self._slip("target", order.direction)
            fill.fill_quantity = order.quantity
            fill.status = OrderStatus.FILLED
            self._on_target_fill(order, tb.high, limit)
        return fill

    def _on_target_fill(self, order, high, limit):
        pass


class PlantedFaultFillModel(RepoFillModel):
    """Stage C: our rules with three planted faults, each labelled when it decides a fill.

    touch   -- a target fills when the high merely touches it (high == limit);
    gapstop -- a stop the bar opens through fills at the stop price, not the open;
    frac    -- the entry fills at price x (1 + C_FRACTION): fraction-of-price slippage, every trade.
    Zero cost otherwise, so the comparison against stage A's profile sees only the faults.
    """

    def _entry_price(self, tb):
        return tb.close * (1.0 + C_FRACTION)

    def _stop_price(self, order, o, stop):
        if o < stop:
            self.algo.note_fault(order.id, "gapstop")
        return stop, o <= stop

    def _target_hit(self, order, high, limit):
        return high >= limit

    def _on_target_fill(self, order, high, limit):
        if high == limit:                       # labelled only once the touch has decided a fill
            self.algo.note_fault(order.id, "touch")


class RepoSecurityInitializer(BrokerageModelSecurityInitializer):
    """LEAN's defaults first; then our fill model (C: with planted faults), fees and no slippage."""

    def __init__(self, algo, brokerage_model, seeder):
        super().__init__(brokerage_model, seeder)
        self.algo = algo

    def initialize(self, security):
        super().initialize(security)
        model = PlantedFaultFillModel if MODE == "C" else RepoFillModel
        security.set_fill_model(model(self.algo))
        security.set_fee_model(RepoFeeModel() if MODE == "B" else ConstantFeeModel(0))
        security.set_slippage_model(NullSlippageModel())


class RepoFeeModel(FeeModel):
    def get_order_fee(self, parameters):
        return OrderFee(CashAmount(FEE_PER_SIDE * abs(parameters.order.quantity), "USD"))
'''


RECON_BODY_V2 = '''
def setup(self):
    # PIPELINE.md section 5 (D-80, D-94): long 1 ES at the first bar after 09:31 CT, stop 20 ticks
    # below, target 30 above, flatten 15:10 CT. Unadjusted prices, explicit roll. Every price read
    # below is the contract's latest TRADE bar from its cache -- the series the fill model uses.
    self.set_time_zone(TimeZones.CHICAGO)
    self.set_cash(1000000)
    self.future = self.add_future("ES", Resolution.MINUTE,
                                  data_normalization_mode=DataNormalizationMode.RAW,
                                  data_mapping_mode=DataMappingMode.OPEN_INTEREST,
                                  contract_depth_offset=0)
    self.set_security_initializer(RepoSecurityInitializer(
        self, self.brokerage_model, FuncSecuritySeeder(self.get_last_known_prices)))
    self.schedule.on(self.date_rules.every_day(self.future.symbol),
                     self.time_rules.at(15, 10, TimeZones.CHICAGO), lambda: self._flatten("flatten"))
    self.schedule.on(self.date_rules.every_day(self.future.symbol),
                     self.time_rules.before_market_close(self.future.symbol, 2),
                     lambda: self._flatten("flatten_close"))
    self._n, self._day, self._trade, self._pending_tag = 0, None, None, ""
    self._stops, self._gaps, self._faults, self._counts = {}, {}, {}, {}
    self._last_bar, self._seen, self._nobar = None, None, 0

def note_gap(self, order_id, gapped):
    self._gaps[order_id] = gapped

def note_fault(self, order_id, name):
    self._faults[order_id] = name

def stop_for_target(self, order_id):
    return self._stops.get(order_id)

def _fold(self, t, b):
    t["mx"] = b.high if t["mx"] is None else max(t["mx"], b.high)
    t["mn"] = b.low if t["mn"] is None else min(t["mn"], b.low)

def on_data(self, data):
    c = self.future.mapped
    if c is None:
        return
    bar = self.securities[c].cache.get_data(TradeBar)
    if bar is None:
        self._nobar += 1
        return
    if self._seen is not None and bar.end_time == self._seen:
        return                                    # no new trade bar in this slice
    self._seen = bar.end_time
    t = self._trade
    if t is not None and t.get("open"):
        if self._last_bar is not None:
            self._fold(t, self._last_bar)
        self._last_bar = bar
    d = self.time.date()
    if (self._day != d and self.time.hour == 9 and self.time.minute >= 32
            and not self.portfolio.invested and (t is None or not t.get("open"))):
        self._day = d
        self._n += 1
        ref = bar.close
        tag = "E|n=" + str(self._n) + "|ref=" + _fmt(ref) + self._pending_tag
        self._pending_tag = ""
        self._trade = {"n": self._n, "c": c, "open": True, "mx": None, "mn": None,
                       "ref": ref, "stop_id": None, "tgt_id": None}
        self._last_bar = None
        self.market_order(c, 1, tag=tag)

def on_order_event(self, ev):
    if ev.status != OrderStatus.FILLED or self._trade is None:
        return
    t = self._trade
    if ev.direction == OrderDirection.BUY:
        t["entry"] = ev.fill_price
        t["efee"] = float(ev.order_fee.value.amount)
        # Levels on the tick grid, from the entry fill -- except in C, where the planted
        # fraction-of-price fault would move them a tick and contaminate every other check; there
        # they come from the intended price, so each fault is seen on its own.
        base_px = t["ref"] if MODE == "C" else ev.fill_price
        base = round(base_px / TICK) * TICK
        stop = base - STOP_TICKS * TICK
        tgt = base + TARGET_TICKS * TICK
        st = self.stop_market_order(t["c"], -1, stop, tag="S|n=" + str(t["n"]) + "|p=" + _fmt(stop))
        tg = self.limit_order(t["c"], -1, tgt, tag="T|n=" + str(t["n"]) + "|p=" + _fmt(tgt))
        t["stop_id"], t["tgt_id"], t["stop"], t["tgt"] = st.order_id, tg.order_id, stop, tgt
        self._stops[tg.order_id] = stop
        return
    reason = t.pop("pending_reason", None) or (
        "stop" if ev.order_id == t["stop_id"] else "target" if ev.order_id == t["tgt_id"] else "other")
    self._close(t, reason, ev)

def _flatten(self, reason):
    t = self._trade
    if t is None or not t.get("open") or "entry" not in t:
        return
    self.transactions.cancel_open_orders(t["c"])
    t["pending_reason"] = reason
    self.market_order(t["c"], -1, tag="F|n=" + str(t["n"]) + "|r=" + reason)

def _close(self, t, reason, ev):
    if not t.get("open"):
        return
    t["open"] = False
    self.transactions.cancel_open_orders(t["c"])
    xb = self.securities[t["c"]].cache.get_data(TradeBar)       # the bar the fill was decided on
    lb = self._last_bar
    if lb is not None and (xb is None or lb.end_time != xb.end_time):
        self._fold(t, lb)                                       # a pre-exit bar, not the exit bar
    self._counts[reason] = self._counts.get(reason, 0) + 1
    gap = self._gaps.get(ev.order_id)
    self._pending_tag = (
        "|prev=" + str(t["n"]) + ";c=" + str(t["c"].value) + ";ent=" + _fmt(t["entry"])
        + ";st=" + _fmt(t["stop"]) + ";tg=" + _fmt(t["tgt"]) + ";xr=" + reason
        + ";xf=" + _fmt(ev.fill_price) + ";xt=" + self.time.strftime("%Y%m%d%H%M")
        + ";mx=" + ("" if t["mx"] is None else _fmt(t["mx"]))
        + ";mn=" + ("" if t["mn"] is None else _fmt(t["mn"]))
        + ";xo=" + _fmt(xb.open) + ";xh=" + _fmt(xb.high) + ";xl=" + _fmt(xb.low)
        + ";xc=" + _fmt(xb.close) + ";xbt=" + xb.end_time.strftime("%Y%m%d%H%M")
        + ";gap=" + ("" if gap is None else str(gap).lower())
        + ";flt=" + self._faults.get(ev.order_id, "")
        + ";efee=" + _fmt(t.get("efee", 0.0)) + ";fee=" + _fmt(float(ev.order_fee.value.amount)))
    self._last_bar = None

def on_end_of_algorithm(self):
    counts = ",".join(k + ":" + str(v) for k, v in sorted(self._counts.items()))
    lines = [PREFIX + "|HEAD|v=2|mode=" + MODE + "|trades=" + str(self._n) + "|exits=" + counts
             + "|nobar=" + str(self._nobar),
             PREFIX + "|LAST" + (self._pending_tag or "|none")]
    used = 0
    for line in lines:
        line = line[:LOG_BUDGET_BYTES - used - 80]
        self.log(line)
        used += len(line) + 1
    self.log(PREFIX + "|END|bytes=" + str(used))
'''


# ================================================================ R009-R012 -- C-007 leg evidence (D-97)
#
# One kit per C-007 leg. The kit records, for every development day, the evidence the D-43 sd
# measurement needs -- and nothing that depends on a parameter still open in Stage 2B. Windows and
# the sign signal are the combination's (Stage 2B C-007, settlement times D-50); the stop multiplier,
# the floors, the volatility forecast and the sizing are applied IN THIS REPOSITORY from the evidence,
# so a change to those in 2B does not require a new cloud run. Prices come from the contract's trade
# bars only (D-94). Orders are placed only to carry each day's record in their tags (as in R006-R008);
# their fills and P&L are not used for anything.

#: market -> (entry "HH:MM" CT, exit "HH:MM" CT = the leg's CME settlement time, D-50).
#: 6E enters at 13:31, the first minute bar strictly after CL's exit; C-007 says 13:30:30, which
#: minute data cannot express, and the half-minute only exists to avoid an overlap in live trading.
LEG_WINDOWS = {"GC": ("12:00", "12:30"), "CL": ("13:00", "13:30"),
               "6E": ("13:31", "14:00"), "ES": ("14:30", "15:00")}
#: Development spans end before the confirmation window. GC's data begins 2012-11-01 (D-90).
LEG_START = {"GC": date(2012, 11, 1), "CL": date(2009, 6, 1), "6E": date(2009, 6, 1),
             "ES": date(2009, 6, 1)}
LEG_END = date(2014, 5, 27)
LEG_PREFIX = "LEG"


def leg_preamble(market: str) -> str:
    entry, exit_ = LEG_WINDOWS[market]
    return f'''
MARKET = "{market}"
ENTRY_HM = {tuple(int(x) for x in entry.split(":"))!r}      # CT, close of the minute bar ending here
EXIT_HM = {tuple(int(x) for x in exit_.split(":"))!r}       # CT, this leg's CME settlement time (D-50)
PREFIX = "{LEG_PREFIX}"
LOG_BUDGET_BYTES = {LOG_BUDGET_BYTES}

from math import log as _ln   # natural log; aliased so it is never mistaken for a log call


def _fmt(x):
    return ("%.6f" % x).rstrip("0").rstrip(".")


class CarrierInitializer(BrokerageModelSecurityInitializer):
    """Zero fees: the carrier orders' own P&L is never used, so nothing is modelled on them."""

    def initialize(self, security):
        super().initialize(security)
        security.set_fee_model(ConstantFeeModel(0))
'''


LEG_BODY = '''
def setup(self):
    # D-97: C-007 leg evidence for the D-43 sd measurement. Trade bars only (D-94).
    self.set_time_zone(TimeZones.CHICAGO)
    self.set_cash(1000000)
    self.future = self.add_future(MARKET, Resolution.MINUTE,
                                  data_normalization_mode=DataNormalizationMode.RAW,
                                  data_mapping_mode=DataMappingMode.OPEN_INTEREST,
                                  contract_depth_offset=0)
    self.set_security_initializer(CarrierInitializer(
        self.brokerage_model, FuncSecuritySeeder(self.get_last_known_prices)))
    self._seen, self._prev_close, self._prev_c = None, None, None
    self._settle = None            # (contract value, price, date) at the last settlement bar
    self._rvp, self._npre = 0.0, 0 # squared log returns since the last settlement
    self._win = None               # the open window's record
    self._pending, self._n, self._skips, self._held = "", 0, {}, None

def _hm(self):
    return (self.time.hour, self.time.minute)

def on_data(self, data):
    c = self.future.mapped
    if c is None:
        return
    bar = self.securities[c].cache.get_data(TradeBar)
    if bar is None or (self._seen is not None and bar.end_time == self._seen):
        return
    self._seen = bar.end_time
    if self._prev_c is not None and self._prev_c != c:
        self._rvp, self._npre, self._prev_close = 0.0, 0, None    # roll: returns never span contracts
    r2 = 0.0
    if self._prev_close and bar.close > 0:
        r2 = _ln(bar.close / self._prev_close) ** 2
    gap = abs(bar.open - self._prev_close) if self._prev_close else 0.0
    self._prev_close, self._prev_c = bar.close, c
    hm = self._hm()
    w = self._win
    if w is not None:
        w["h"], w["l"] = max(w["h"], bar.high), min(w["l"], bar.low)
        w["rvw"] += r2
        w["nw"] += 1
        w["g"] = max(w["g"], gap)
        if hm >= EXIT_HM or self.time.date() != w["date"]:
            self._close_window(bar)
    else:
        self._rvp += r2
        self._npre += 1
        if hm == ENTRY_HM:
            self._open_window(c, bar)
    if hm == EXIT_HM and self._win is None:
        self._settle = (c.value, bar.close, self.time.date())
        self._rvp, self._npre = 0.0, 0

def _open_window(self, c, bar):
    d = self.time.date()
    s = self._settle
    skip = ""
    if s is None:
        skip = "noprev"
    elif s[0] != c.value:
        skip = "roll"
    elif (d - s[2]).days > 5:
        skip = "stale"
    ps = s[1] if s is not None else 0.0
    sign = 0 if skip else (1 if bar.close > ps else (-1 if bar.close < ps else 0))
    self._n += 1
    rec = {"n": self._n, "date": d, "d": d.strftime("%Y%m%d"), "c": c.value, "ps": ps,
           "pst": "" if s is None else s[2].strftime("%Y%m%d"), "e": bar.close, "dir": sign,
           "sk": skip, "rvp": self._rvp, "np": self._npre, "h": bar.close, "l": bar.close,
           "rvw": 0.0, "nw": 0, "g": 0.0}
    if skip:
        self._skips[skip] = self._skips.get(skip, 0) + 1
    self._win = rec
    self._held = c
    self.market_order(c, 1 if sign >= 0 else -1, tag="E|n=" + str(self._n) + self._pending)
    self._pending = ""

def _close_window(self, bar):
    w = self._win
    self._win = None
    self._settle = (self._held.value, bar.close, self.time.date())
    self._rvp, self._npre = 0.0, 0
    self._pending = ("|rec=" + str(w["n"]) + ";d=" + w["d"] + ";c=" + w["c"] + ";ps=" + _fmt(w["ps"])
        + ";pst=" + w["pst"] + ";e=" + _fmt(w["e"]) + ";x=" + _fmt(bar.close)
        + ";xd=" + self.time.strftime("%Y%m%d") + ";xt=" + self.time.strftime("%H%M") + ";h=" + _fmt(w["h"]) + ";l=" + _fmt(w["l"])
        + ";dir=" + str(w["dir"]) + ";sk=" + w["sk"] + ";rvp=" + ("%.6e" % w["rvp"])
        + ";np=" + str(w["np"]) + ";rvw=" + ("%.6e" % w["rvw"]) + ";nw=" + str(w["nw"])
        + ";g=" + _fmt(w["g"]))
    self.liquidate(self._held, tag="X|n=" + str(w["n"]))

def on_end_of_algorithm(self):
    if self._win is not None:
        self._skips["unclosed"] = self._skips.get("unclosed", 0) + 1
    skips = ",".join(k + ":" + str(v) for k, v in sorted(self._skips.items()))
    lines = [PREFIX + "|HEAD|v=1|market=" + MARKET + "|days=" + str(self._n) + "|skips=" + skips,
             PREFIX + "|LAST" + (self._pending or "|none")]
    used = 0
    for line in lines:
        line = line[:LOG_BUDGET_BYTES - used - 80]
        self.log(line)
        used += len(line) + 1
    self.log(PREFIX + "|END|bytes=" + str(used))
'''


# ================================================================ R013-R016 -- C-007 leg evidence v2 (D-98)
#
# R009 (v1) recorded GC on only 241 of 409 weekdays: QuantConnect's open-interest mapping put GC on
# thin off-cycle months (F, K, V, X) whose minute bars often miss the entry minute. Version 2 chooses
# its own contract: at each settlement bar it takes, for the NEXT session, the contract that traded
# the most volume since the previous settlement -- known before the next window, so no look-ahead.
# The previous settlement and the next entry therefore come from the same contract. Everything else
# is v1's (D-97). v1 stays byte-identical so R009 remains reproducible.

LEG_V2_FILTER_DAYS = 120


# ================================================================ R026 -- opening-gap reversal evidence (D-105)
#
# One kit, ES only. For every development day it records the previous settlement (the 15:00 CT bar
# close of the contract chosen at that settlement by prior-session volume, D-98) and every one-minute
# trade bar whose END time lies in [08:27, 10:30] CT, in ticks relative to a base price. The kit
# computes NO trade: the gap, the trigger, the stop, the target and every variant in
# config/gap_reversal.yaml are scored in the repository from these bars, so the whole grid, the
# permutation null and the sensitivities come from one cloud run, and a scoring bug never needs a
# rerun. Orders exist only to carry the records in their tags -- two per day, the day's bars split in
# half so no tag is long; their fills and P&L mean nothing.

GAP_PREFIX = "GAP"
GAP_MARKET = "ES"
GAP_START = date(2009, 6, 1)
GAP_END = date(2014, 5, 27)
GAP_REC_HM = ((8, 27), (10, 30))     # bars whose END time is in this range, inclusive: 124 slots
GAP_SETTLE_HM = (15, 0)              # ES settlement minute (D-50)
GAP_TICK = 0.25
GAP_SLOTS = (GAP_REC_HM[1][0] - GAP_REC_HM[0][0]) * 60 + GAP_REC_HM[1][1] - GAP_REC_HM[0][1] + 1


def gap_slot_hhmm(i: int) -> str:
    """Slot index -> the bar's END time as HHMM."""
    m = GAP_REC_HM[0][0] * 60 + GAP_REC_HM[0][1] + i
    return "%02d%02d" % (m // 60, m % 60)


def gap_preamble() -> str:
    return f'''
MARKET = "{GAP_MARKET}"
REC_FIRST = {GAP_REC_HM[0]!r}      # CT, END time of the first recorded bar (inclusive)
REC_LAST = {GAP_REC_HM[1]!r}       # CT, END time of the last recorded bar = the 10:30 cutoff
SETTLE_HM = {GAP_SETTLE_HM!r}      # CT, the settlement minute (D-50)
TICK = {GAP_TICK}
SLOTS = {GAP_SLOTS}
SPLIT = {GAP_SLOTS // 2}           # bars carried by the first of the day's two order tags
FILTER_DAYS = {LEG_V2_FILTER_DAYS}
PREFIX = "{GAP_PREFIX}"
LOG_BUDGET_BYTES = {LOG_BUDGET_BYTES}


def _fmt(x):
    return ("%.6f" % x).rstrip("0").rstrip(".")


def _slot(hm):
    return (hm[0] - REC_FIRST[0]) * 60 + (hm[1] - REC_FIRST[1])


def _t(px, ref):
    return str(int(round((px - ref) / TICK)))


class CarrierInitializer(BrokerageModelSecurityInitializer):
    """Zero fees: the carrier orders' own P&L is never used, so nothing is modelled on them."""

    def initialize(self, security):
        super().initialize(security)
        security.set_fee_model(ConstantFeeModel(0))
'''


GAP_BODY = '''
def setup(self):
    # D-105: opening-gap reversal evidence. Bars only; no trade is computed here. Trade bars (D-94),
    # own contract choice by prior-session volume (D-98).
    self.set_time_zone(TimeZones.CHICAGO)
    self.set_cash(1000000)
    self.future = self.add_future(MARKET, Resolution.MINUTE,
                                  data_normalization_mode=DataNormalizationMode.RAW,
                                  data_mapping_mode=DataMappingMode.OPEN_INTEREST,
                                  contract_depth_offset=0)
    self.future.set_filter(0, FILTER_DAYS)
    self.set_security_initializer(CarrierInitializer(
        self.brokerage_model, FuncSecuritySeeder(self.get_last_known_prices)))
    self._active = None            # the contract recorded today, chosen at the previous settlement
    self._vol = {}                 # contract -> volume since the last settlement
    self._seen, self._prev_c = None, None
    self._settle = None            # (contract value, price, date) at the last settlement bar
    self._day = None               # the day being recorded
    self._n, self._skips, self._switches, self._full = 0, {}, 0, 0
    self._last = ""

def _hm(self):
    return (self.time.hour, self.time.minute)

def on_data(self, data):
    for sym, b in data.bars.items():
        if sym != self.future.symbol and sym.security_type == SecurityType.FUTURE:
            self._vol[sym] = self._vol.get(sym, 0.0) + float(b.volume)
    c = self._active or self.future.mapped
    if c is None or c not in self.securities:
        return
    bar = self.securities[c].cache.get_data(TradeBar)
    if bar is None or (self._seen is not None and bar.end_time == self._seen and self._prev_c == c):
        return
    self._seen, self._prev_c = bar.end_time, c
    hm = self._hm()
    d = self._day
    if d is not None and (self.time.date() != d["date"] or hm > REC_LAST):
        self._close_day()
        d = None
    if REC_FIRST <= hm <= REC_LAST:
        if d is None:
            d = self._open_day(c, bar)
        if c.value == d["c"]:
            self._record(d, hm, bar)
        if hm == REC_LAST:
            self._close_day()
    if hm == SETTLE_HM:
        if self._day is not None:
            self._close_day()
        self._roll_at_settlement(c, bar)

def _roll_at_settlement(self, c, bar):
    """Choose tomorrow's contract by this session's volume; record its settlement price."""
    nxt = max(self._vol, key=self._vol.get) if self._vol else c
    self._vol = {}
    price = bar.close
    if nxt != c:
        nb = self.securities[nxt].cache.get_data(TradeBar) if nxt in self.securities else None
        if nb is None or nb.end_time.date() != bar.end_time.date():
            self._settle = None                    # no same-day price for the new contract
            self._active = nxt
            self._switches += 1
            return
        price = nb.close
        self._switches += 1
    self._active = nxt
    self._settle = (nxt.value, price, self.time.date())

def _open_day(self, c, bar):
    dt = self.time.date()
    s = self._settle
    skip = ""
    if s is None:
        skip = "noprev"
    elif s[0] != c.value:
        skip = "roll"
    elif (dt - s[2]).days > 5:
        skip = "stale"
    if skip:
        self._skips[skip] = self._skips.get(skip, 0) + 1
    self._n += 1
    d = {"n": self._n, "date": dt, "d": dt.strftime("%Y%m%d"), "c": c.value, "sym": c,
         "ps": s[1] if s is not None else 0.0, "pst": "" if s is None else s[2].strftime("%Y%m%d"),
         "sk": skip, "base": bar.open, "bars": [""] * SLOTS, "nb": 0, "last": None}
    self._day = d
    return d

def _record(self, d, hm, bar):
    i = _slot(hm)
    if i < 0 or i >= SLOTS or d["bars"][i]:
        return
    d["bars"][i] = (_t(bar.open, d["base"]) + "." + _t(bar.high, bar.open) + "."
                    + _t(bar.open, bar.low) + "." + _t(bar.close, bar.open))
    d["nb"] += 1
    d["last"] = hm

def _head(self, d):
    return ("|rec=" + str(d["n"]) + ";d=" + d["d"] + ";c=" + d["c"] + ";ps=" + _fmt(d["ps"])
            + ";pst=" + d["pst"] + ";sk=" + d["sk"] + ";b=" + _fmt(d["base"]) + ";nb=" + str(d["nb"])
            + ";lt=" + ("%02d%02d" % d["last"] if d["last"] else ""))

def _close_day(self):
    d = self._day
    self._day = None
    if d["nb"] == SLOTS:
        self._full += 1
    head = self._head(d) + ";b1=" + ",".join(d["bars"][:SPLIT])
    tail = "|rec=" + str(d["n"]) + ";b2=" + ",".join(d["bars"][SPLIT:])
    # Two market orders, never liquidate: a liquidate before the buy fills can cancel it and create
    # no sell, losing the tag. The carrier is the tradable contract; the record names its own.
    carrier = self._active or self.future.mapped or d["sym"]
    self.market_order(carrier, 1, tag="E|n=" + str(d["n"]) + head)
    self.market_order(carrier, -1, tag="X|n=" + str(d["n"]) + tail)
    self._last = self._head(d)

def on_end_of_algorithm(self):
    last = self._last
    if self._day is not None:                      # ended inside a window: the record goes to the log
        d = self._day
        last = (self._head(d) + ";b1=" + ",".join(d["bars"][:SPLIT]) + "|rec=" + str(d["n"])
                + ";b2=" + ",".join(d["bars"][SPLIT:]))
    skips = ",".join(k + ":" + str(v) for k, v in sorted(self._skips.items()))
    lines = [PREFIX + "|HEAD|v=1|market=" + MARKET + "|days=" + str(self._n) + "|full=" + str(self._full)
             + "|skips=" + skips + "|switches=" + str(self._switches) + "|slots=" + str(SLOTS),
             PREFIX + "|LAST" + (last or "|none")]
    used = 0
    for line in lines:
        line = line[:LOG_BUDGET_BYTES - used - 80]
        self.log(line)
        used += len(line) + 1
    self.log(PREFIX + "|END|bytes=" + str(used))
'''

#: R028 (D-122): the Test 1 re-score, computed INSIDE QuantConnect (D-120: raw bars stay in the cloud).
#: Collects exactly R027's bars (same contract choice, extended hours), scores every cell of the
#: open-reversion design with the embedded core (`propedge/outcomes/openrev_core.py`, verbatim) under
#: both fill rules, and exports per-day trade outcomes only.
OPENREV_PREFIX = "ORS"


def openrev_preamble(market: str = GAP_MARKET, vehicle: str | None = None, floor_ticks: int | None = None,
                     p_ref: float | None = None, prefix: str = OPENREV_PREFIX) -> str:
    """Module-level code for R028/R029: constants from the repository's configuration, then the core.
    The defaults reproduce R028 byte for byte; R029 (D-124) passes NQ's own market, vehicle, floor and
    price level."""
    import inspect

    from propedge.outcomes import open_reversion as orv
    from propedge.outcomes import openrev_core

    cfg = orv.load_design()
    full = orv.fills_from_config("assumed", vehicle or cfg["instrument"]["vehicle"])
    fills_full = {"entry": full.entry, "stop": full.stop, "target": full.target, "flatten": full.flatten,
                  "round_turn": full.round_turn, "tick_value": full.tick_value, "point_value": full.point_value}
    fills_zero = {**fills_full, "entry": 0.0, "stop": 0.0, "target": 0.0, "flatten": 0.0, "round_turn": 0.0}
    params = {"first": orv.slot_of(cfg["trigger"]["window_ct"][0].replace(":", "")),
              "last": orv.slot_of(cfg["trigger"]["window_ct"][1].replace(":", "")),
              "cutoff": orv.slot_of("1030"), "swing_from": orv.slot_of("0831"),
              "w": float(cfg["trigger"]["displacement_w"]),
              "floor_ticks": int(floor_ticks if floor_ticks is not None
                                 else cfg["features_searched"]["stop_anchor"]["floor_ticks"])}
    variants = [(v["anchor"], float(v["r_min"])) for v in orv.variants(cfg)]
    core_src = inspect.getsource(openrev_core)
    return f'''
MARKET = "{market}"
REC_FIRST = {GAP_REC_HM[0]!r}      # CT, END time of the first recorded bar (inclusive) -- as R027
REC_LAST = {GAP_REC_HM[1]!r}       # CT, END time of the last recorded bar
SETTLE_HM = {GAP_SETTLE_HM!r}      # CT, the settlement minute (D-50)
SLOTS = {GAP_SLOTS}
FILTER_DAYS = {LEG_V2_FILTER_DAYS}
PREFIX = "{prefix}"
LOG_BUDGET_BYTES = {LOG_BUDGET_BYTES}
TAG_CHARS = 600                     # longest record segment per order tag (R027 carried 749 intact)
P_REF = {float(p_ref if p_ref is not None else cfg["scale"]["selection_price_level"])!r}
PARAMS = {params!r}
VARIANTS = {variants!r}             # (stop anchor, minimum reward-to-risk), config/open_reversion.yaml
FILLS_FULL = {fills_full!r}         # config/fills.yaml "assumed" + config/instruments.yaml MES (D-95)
FILLS_ZERO = {fills_zero!r}
FILL_MODES = ("close", "next_open")
SCALES = (None, P_REF)


def _fmt(x):
    return ("%.6f" % x).rstrip("0").rstrip(".")


def _slot(hm):
    return (hm[0] - REC_FIRST[0]) * 60 + (hm[1] - REC_FIRST[1])


def cell_index(fill_i, scale_i, baseline, variant_i):
    return ((fill_i * 2 + scale_i) * 2 + (0 if baseline else 1)) * len(VARIANTS) + variant_i


class CarrierInitializer(BrokerageModelSecurityInitializer):
    """Zero fees: the carrier orders' own P&L is never used, so nothing is modelled on them."""

    def initialize(self, security):
        super().initialize(security)
        security.set_fee_model(ConstantFeeModel(0))


# ---------------------------------------------------------------- embedded verbatim from
# ---------------------------------------------------------------- propedge/outcomes/openrev_core.py
{core_src}
# ---------------------------------------------------------------- end of the embedded core


_KIND = {{"target": "t", "stop": "s", "stop_gap": "g", "time": "m"}}


def score_all_cells(o, h, l, c, ps):
    """Every cell of the design under both fill rules. Returns the encoded cell strings."""
    out = []
    for scale_i, scale_to in enumerate(SCALES):
        so, sh, sl, sc = scaled(o, h, l, c, ps, scale_to)
        pre = (so, sh, sl, sc, swing_table(sh, sl, PARAMS["swing_from"], PARAMS["last"]))
        for fill_i, fill in enumerate(FILL_MODES):
            for baseline in (True, False):
                for v_i, (anchor, r_min) in enumerate(VARIANTS):
                    zr = score_day(o, h, l, c, ps, anchor, r_min, baseline, FILLS_ZERO, PARAMS,
                                   scale_to=scale_to, fill=fill, pre=pre)
                    zm = score_day(o, h, l, c, ps, anchor, r_min, baseline, FILLS_ZERO, PARAMS,
                                   scale_to=scale_to, flip=True, fill=fill, pre=pre)
                    fu = score_day(o, h, l, c, ps, anchor, r_min, baseline, FILLS_FULL, PARAMS,
                                   scale_to=scale_to, fill=fill, pre=pre)
                    if zr["reason"] and zm["reason"] and fu["reason"]:
                        continue
                    num = lambda r: "" if r["reason"] else ("%.6f" % r["u"])   # noqa: E731
                    kind = "" if zr["reason"] else _KIND[zr["exit_kind"]]
                    fl = "" if fu["reason"] else ("1" if fu["floor_bound"] else "0")
                    out.append(str(cell_index(fill_i, scale_i, baseline, v_i)) + ":" + num(zr) + ","
                               + num(zm) + "," + num(fu) + "," + kind + fl)
    return out
'''


#: Version 2 (D-109). R026 came back with the four pre-open bars (ending 08:27-08:30 CT) missing on
#: every one of its 1,285 days: `add_future` without extended market hours delivers regular-session
#: bars only, and ES's regular session opens 08:30. The 14-bar ATR at the 08:40 time trigger needs
#: those bars, so v2 requests extended hours. Nothing else changes; v1 stays byte-identical so R026
#: remains on record as it ran.
OPENREV_BODY = '''
def setup(self):
    # D-122: Test 1 re-score in the cloud. Bars are collected exactly as R027 (D-98 contract choice,
    # D-109 extended hours, trade bars D-94) and scored here; only per-day outcomes leave (D-120).
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
    self._active = None
    self._vol = {}
    self._seen, self._prev_c = None, None
    self._settle = None
    self._day = None
    self._n, self._skips, self._switches, self._full, self._orders = 0, {}, 0, 0, 0
    self._last = ""

def _hm(self):
    return (self.time.hour, self.time.minute)

def on_data(self, data):
    for sym, b in data.bars.items():
        if sym != self.future.symbol and sym.security_type == SecurityType.FUTURE:
            self._vol[sym] = self._vol.get(sym, 0.0) + float(b.volume)
    c = self._active or self.future.mapped
    if c is None or c not in self.securities:
        return
    bar = self.securities[c].cache.get_data(TradeBar)
    if bar is None or (self._seen is not None and bar.end_time == self._seen and self._prev_c == c):
        return
    self._seen, self._prev_c = bar.end_time, c
    hm = self._hm()
    d = self._day
    if d is not None and (self.time.date() != d["date"] or hm > REC_LAST):
        self._close_day()
        d = None
    if REC_FIRST <= hm <= REC_LAST:
        if d is None:
            d = self._open_day(c, bar)
        if c.value == d["c"]:
            self._record(d, hm, bar)
        if hm == REC_LAST:
            self._close_day()
    if hm == SETTLE_HM:
        if self._day is not None:
            self._close_day()
        self._roll_at_settlement(c, bar)

def _roll_at_settlement(self, c, bar):
    """Choose tomorrow's contract by this session's volume; record its settlement price."""
    nxt = max(self._vol, key=self._vol.get) if self._vol else c
    self._vol = {}
    price = bar.close
    if nxt != c:
        nb = self.securities[nxt].cache.get_data(TradeBar) if nxt in self.securities else None
        if nb is None or nb.end_time.date() != bar.end_time.date():
            self._settle = None
            self._active = nxt
            self._switches += 1
            return
        price = nb.close
        self._switches += 1
    self._active = nxt
    self._settle = (nxt.value, price, self.time.date())

def _open_day(self, c, bar):
    dt = self.time.date()
    s = self._settle
    skip = ""
    if s is None:
        skip = "noprev"
    elif s[0] != c.value:
        skip = "roll"
    elif (dt - s[2]).days > 5:
        skip = "stale"
    if skip:
        self._skips[skip] = self._skips.get(skip, 0) + 1
    self._n += 1
    d = {"n": self._n, "date": dt, "d": dt.strftime("%Y%m%d"), "c": c.value, "sym": c,
         "ps": s[1] if s is not None else 0.0, "pst": "" if s is None else s[2].strftime("%Y%m%d"),
         "sk": skip, "o": [None] * SLOTS, "h": [None] * SLOTS, "l": [None] * SLOTS,
         "cl": [None] * SLOTS, "nb": 0, "last": None}
    self._day = d
    return d

def _record(self, d, hm, bar):
    i = _slot(hm)
    if i < 0 or i >= SLOTS or d["o"][i] is not None:
        return
    d["o"][i], d["h"][i], d["l"][i], d["cl"][i] = (float(bar.open), float(bar.high), float(bar.low),
                                                    float(bar.close))
    d["nb"] += 1
    d["last"] = hm

def _head(self, d):
    op = "1" if d["o"][_slot((8, 31))] is not None else "0"
    return ("d=" + d["d"] + ";c=" + d["c"] + ";ps=" + _fmt(d["ps"]) + ";pst=" + d["pst"]
            + ";sk=" + d["sk"] + ";nb=" + str(d["nb"])
            + ";lt=" + ("%02d%02d" % d["last"] if d["last"] else "") + ";op=" + op)

def _close_day(self):
    d = self._day
    self._day = None
    if d["nb"] == SLOTS:
        self._full += 1
    cells = []
    if d["ps"] > 0 and d["o"][_slot((8, 31))] is not None:
        cells = score_all_cells(d["o"], d["h"], d["l"], d["cl"], d["ps"])
    chunks, cur = [], ""
    for s in cells:
        if cur and len(cur) + 1 + len(s) > TAG_CHARS:
            chunks.append(cur)
            cur = ""
        cur = s if not cur else cur + "/" + s
    if cur or not chunks:
        chunks.append(cur)
    carrier = self._active or self.future.mapped or d["sym"]
    for k, ch in enumerate(chunks):
        tag = ("E|n=" + str(d["n"]) + "|rec=" + str(d["n"]) + ";k=" + str(k) + ";K=" + str(len(chunks))
               + (";" + self._head(d) if k == 0 else "") + ";x=" + ch)
        self.market_order(carrier, 1 if k % 2 == 0 else -1, tag=tag)
        self._orders += 1
    if len(chunks) % 2 == 1:
        self.market_order(carrier, -1, tag="Z|n=" + str(d["n"]))
        self._orders += 1
    self._last = "|rec=" + str(d["n"]) + ";K=" + str(len(chunks)) + ";" + self._head(d)

def on_end_of_algorithm(self):
    skips = ",".join(k + ":" + str(v) for k, v in sorted(self._skips.items()))
    lines = [PREFIX + "|HEAD|v=1|market=" + MARKET + "|days=" + str(self._n) + "|full=" + str(self._full)
             + "|skips=" + skips + "|switches=" + str(self._switches) + "|orders=" + str(self._orders)
             + "|open=" + ("1" if self._day is not None else "0"),
             PREFIX + "|LAST" + (self._last or "|none")]
    used = 0
    for line in lines:
        line = line[:LOG_BUDGET_BYTES - used - 80]
        self.log(line)
        used += len(line) + 1
    self.log(PREFIX + "|END|bytes=" + str(used))
'''

#: R029 (D-124): R028's body plus a few per-day measurements computed in the cloud -- the knob-free
#: gate's inputs (x, y30, y45, y60, in percent) and integrity counters (bars failing the OHLC order or
#: the tick grid; the 08:30 bar's range and the mean pre-open range, a clock check). No bar leaves.
OPENREV_PREFIX_NQ = "ORN"
OPENREV_BODY_V2 = OPENREV_BODY.replace(
    '''            + ";lt=" + ("%02d%02d" % d["last"] if d["last"] else "") + ";op=" + op)
''',
    '''            + ";lt=" + ("%02d%02d" % d["last"] if d["last"] else "") + ";op=" + op + self._measures(d))

def _measures(self, d):
    # D-124: derived per-day numbers only (D-120); the knob-free gate's inputs and integrity counters.
    from math import log as _ln    # natural log; aliased so it is never mistaken for a log call
    o, h, l, cl = d["o"], d["h"], d["l"], d["cl"]
    bad = 0
    for i in range(SLOTS):
        if o[i] is None:
            continue
        vals = (o[i], h[i], l[i], cl[i])
        if (not (l[i] <= min(o[i], cl[i]) and max(o[i], cl[i]) <= h[i])
                or any(abs(v * 4 - round(v * 4)) > 1e-9 for v in vals)):
            bad += 1
    s0, s845 = _slot((8, 31)), _slot((8, 45))
    pre = [(h[i] - l[i]) / TICK for i in range(0, s0) if o[i] is not None]
    out = (";bad=" + str(bad) + ";r0=" + ("" if o[s0] is None else _fmt((h[s0] - l[s0]) / TICK))
           + ";rp=" + ("" if not pre else _fmt(sum(pre) / len(pre))))
    cc = ffill(cl)
    fv = o[s0]
    if fv is not None and cc[s845] is not None:
        out += ";ex=" + ("%.6f" % (100.0 * _ln(cc[s845] / fv)))      # "x" carries the cells
        for m in (30, 45, 60):
            j = min(s845 + m, SLOTS - 1)
            out += ";y" + str(m) + "=" + ("%.6f" % (100.0 * _ln(cc[j] / cc[s845])))
    return out
''').replace('"|HEAD|v=1|market="', '"|HEAD|v=2|market="')

GAP_BODY_V2 = GAP_BODY.replace(
    "                                  contract_depth_offset=0)\n",
    "                                  contract_depth_offset=0,\n"
    "                                  extended_market_hours=True)   # D-109: the pre-open bars\n",
).replace('"|HEAD|v=1|', '"|HEAD|v=2|')


#: GC's active months are two apart (G J M Q V Z, with V thin), so after Q expires the next liquid
#: contract, Z, can be ~140 days out -- beyond 120. R013 used 120 and fell back to the thin V13 in
#: Aug-Sep 2013; R017 uses this (D-99). CL is monthly and 6E/ES are quarterly, so 120 suffices there.
LEG_V2_FILTER_DAYS_GC = 200


def leg_preamble_v2(market: str, filter_days: int = LEG_V2_FILTER_DAYS) -> str:
    return leg_preamble(market) + f'''
FILTER_DAYS = {filter_days}   # contracts expiring within this many days are candidates
'''


LEG_BODY_V2 = '''
def setup(self):
    # D-98: C-007 leg evidence, own contract choice by prior-session volume. Trade bars only (D-94).
    self.set_time_zone(TimeZones.CHICAGO)
    self.set_cash(1000000)
    self.future = self.add_future(MARKET, Resolution.MINUTE,
                                  data_normalization_mode=DataNormalizationMode.RAW,
                                  data_mapping_mode=DataMappingMode.OPEN_INTEREST,
                                  contract_depth_offset=0)
    self.future.set_filter(0, FILTER_DAYS)
    self.set_security_initializer(CarrierInitializer(
        self.brokerage_model, FuncSecuritySeeder(self.get_last_known_prices)))
    self._active = None            # the contract traded today, chosen at the previous settlement
    self._vol = {}                 # contract -> volume since the last settlement
    self._seen, self._prev_close, self._prev_c = None, None, None
    self._settle = None            # (contract value, price, date) at the last settlement bar
    self._rvp, self._npre = 0.0, 0
    self._win = None
    self._pending, self._n, self._skips, self._held, self._switches = "", 0, {}, None, 0

def _hm(self):
    return (self.time.hour, self.time.minute)

def on_data(self, data):
    for sym, b in data.bars.items():
        if sym != self.future.symbol and sym.security_type == SecurityType.FUTURE:
            self._vol[sym] = self._vol.get(sym, 0.0) + float(b.volume)
    c = self._active or self.future.mapped
    if c is None or c not in self.securities:
        return
    bar = self.securities[c].cache.get_data(TradeBar)
    if bar is None or (self._seen is not None and bar.end_time == self._seen and self._prev_c == c):
        return
    self._seen = bar.end_time
    if self._prev_c is not None and self._prev_c != c:
        self._rvp, self._npre, self._prev_close = 0.0, 0, None    # returns never span contracts
    r2 = 0.0
    if self._prev_close and bar.close > 0:
        r2 = _ln(bar.close / self._prev_close) ** 2
    gap = abs(bar.open - self._prev_close) if self._prev_close else 0.0
    self._prev_close, self._prev_c = bar.close, c
    hm = self._hm()
    w = self._win
    if w is not None:
        w["h"], w["l"] = max(w["h"], bar.high), min(w["l"], bar.low)
        w["rvw"] += r2
        w["nw"] += 1
        w["g"] = max(w["g"], gap)
        if hm >= EXIT_HM or self.time.date() != w["date"]:
            self._close_window(bar)
            self._roll_at_settlement(c, bar)
    else:
        self._rvp += r2
        self._npre += 1
        if hm == ENTRY_HM:
            self._open_window(c, bar)
        elif hm == EXIT_HM:
            self._roll_at_settlement(c, bar)

def _roll_at_settlement(self, c, bar):
    """Choose tomorrow's contract by this session's volume; record its settlement price."""
    nxt = max(self._vol, key=self._vol.get) if self._vol else c
    self._vol = {}
    price = bar.close
    if nxt != c:
        nb = self.securities[nxt].cache.get_data(TradeBar) if nxt in self.securities else None
        if nb is None or nb.end_time.date() != bar.end_time.date():
            self._settle = None                    # no same-day price for the new contract
            self._active = nxt
            self._switches += 1
            return
        price = nb.close
        self._switches += 1
    self._active = nxt
    self._settle = (nxt.value, price, self.time.date())
    self._rvp, self._npre = 0.0, 0

def _open_window(self, c, bar):
    d = self.time.date()
    s = self._settle
    skip = ""
    if s is None:
        skip = "noprev"
    elif s[0] != c.value:
        skip = "roll"
    elif (d - s[2]).days > 5:
        skip = "stale"
    ps = s[1] if s is not None else 0.0
    sign = 0 if skip else (1 if bar.close > ps else (-1 if bar.close < ps else 0))
    self._n += 1
    rec = {"n": self._n, "date": d, "d": d.strftime("%Y%m%d"), "c": c.value, "ps": ps,
           "pst": "" if s is None else s[2].strftime("%Y%m%d"), "e": bar.close, "dir": sign,
           "sk": skip, "rvp": self._rvp, "np": self._npre, "h": bar.close, "l": bar.close,
           "rvw": 0.0, "nw": 0, "g": 0.0}
    if skip:
        self._skips[skip] = self._skips.get(skip, 0) + 1
    self._win = rec
    self._held = c
    self.market_order(c, 1 if sign >= 0 else -1, tag="E|n=" + str(self._n) + self._pending)
    self._pending = ""

def _close_window(self, bar):
    w = self._win
    self._win = None
    self._pending = ("|rec=" + str(w["n"]) + ";d=" + w["d"] + ";c=" + w["c"] + ";ps=" + _fmt(w["ps"])
        + ";pst=" + w["pst"] + ";e=" + _fmt(w["e"]) + ";x=" + _fmt(bar.close)
        + ";xd=" + self.time.strftime("%Y%m%d") + ";xt=" + self.time.strftime("%H%M")
        + ";h=" + _fmt(w["h"]) + ";l=" + _fmt(w["l"])
        + ";dir=" + str(w["dir"]) + ";sk=" + w["sk"] + ";rvp=" + ("%.6e" % w["rvp"])
        + ";np=" + str(w["np"]) + ";rvw=" + ("%.6e" % w["rvw"]) + ";nw=" + str(w["nw"])
        + ";g=" + _fmt(w["g"]))
    self.liquidate(self._held, tag="X|n=" + str(w["n"]))

def on_end_of_algorithm(self):
    if self._win is not None:
        self._skips["unclosed"] = self._skips.get("unclosed", 0) + 1
    skips = ",".join(k + ":" + str(v) for k, v in sorted(self._skips.items()))
    lines = [PREFIX + "|HEAD|v=2|market=" + MARKET + "|days=" + str(self._n) + "|skips=" + skips
             + "|switches=" + str(self._switches),
             PREFIX + "|LAST" + (self._pending or "|none")]
    used = 0
    for line in lines:
        line = line[:LOG_BUDGET_BYTES - used - 80]
        self.log(line)
        used += len(line) + 1
    self.log(PREFIX + "|END|bytes=" + str(used))
'''


# ================================================================ R030-R035 -- the effect atlas (D-126)
#
# One kit per market. Records the market's bars from its open - 3 minutes to its settlement minute, then
# computes the atlas's per-day measurements in the cloud (`propedge/research/atlas_core.py`, embedded
# verbatim) and exports ONE order tag per day carrying only those numbers (D-120). The contract is chosen
# by prior-session volume at each settlement (D-98), extended hours give the pre-open bars (D-109).
ATLAS_PREFIX = "ATL"
_ATLAS_KEYS = ("bad", "rp", "r0", "cov", "st", "op", "S", "on", "r30", "r60", "rr30", "mid", "l30", "day",
               "rv30", "rvd", "rg30", "gf", "bd", "ba", "br",
               # D-128: session high and low, opening-range close location, volume, quoted spread and imbalance
               "hi", "lo", "cl30", "v30", "vd", "sp", "sp30", "spw", "qcov", "imb30")


def atlas_preamble(market: str) -> str:
    import inspect

    import yaml

    from propedge import CONFIG_DIR
    from propedge.research import atlas_core

    m = yaml.safe_load((CONFIG_DIR / "effect_atlas.yaml").read_text(encoding="utf-8"))["markets"][market]
    oh, om = (int(x) for x in m["open"].split(":"))
    sh, sm = (int(x) for x in m["settle"].split(":"))
    first = oh * 60 + om - 3
    return f'''
MARKET = "{market}"
REC_FIRST = ({first // 60}, {first % 60})     # CT, END time of the first recorded bar: open - 3 minutes
SETTLE_HM = ({sh}, {sm})                      # CT, this market's settlement minute (config/effect_atlas.yaml)
SLOTS = {sh * 60 + sm - first + 1}
TICK = {float(m["tick"])!r}                   # the standard contract's tick
FILTER_DAYS = {int(m["filter_days"])}
PREFIX = "{ATLAS_PREFIX}"
LOG_BUDGET_BYTES = {LOG_BUDGET_BYTES}
KEYS = {_ATLAS_KEYS!r}


def _fmt(x):
    return ("%.10g" % x) if isinstance(x, float) else str(x)


def _slot(hm):
    return (hm[0] - REC_FIRST[0]) * 60 + (hm[1] - REC_FIRST[1])


class CarrierInitializer(BrokerageModelSecurityInitializer):
    """Zero fees: the carrier orders' own P&L is never used, so nothing is modelled on them."""

    def initialize(self, security):
        super().initialize(security)
        security.set_fee_model(ConstantFeeModel(0))


# ---------------------------------------------------------------- embedded verbatim from
# ---------------------------------------------------------------- propedge/research/atlas_core.py
{inspect.getsource(atlas_core)}
# ---------------------------------------------------------------- end of the embedded core
'''


ATLAS_BODY = """
def setup(self):
    # D-126, D-128: effect atlas. Bars and quotes stay in the cloud; one tag per day carries the day's measurements.
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
    self._active = None
    self._vol = {}
    self._seen, self._prev_c = None, None
    self._settle = None
    self._day = None
    self._n, self._skips, self._switches, self._settled = 0, {}, 0, 0
    self._last = ""

def _hm(self):
    return (self.time.hour, self.time.minute)

def on_data(self, data):
    for sym, b in data.bars.items():
        if sym != self.future.symbol and sym.security_type == SecurityType.FUTURE:
            self._vol[sym] = self._vol.get(sym, 0.0) + float(b.volume)
    c = self._active or self.future.mapped
    if c is None or c not in self.securities:
        return
    bar = self.securities[c].cache.get_data(TradeBar)
    if bar is None or (self._seen is not None and bar.end_time == self._seen and self._prev_c == c):
        return
    self._seen, self._prev_c = bar.end_time, c
    hm = self._hm()
    d = self._day
    if d is not None and self.time.date() != d["date"]:
        self._close_day()
        d = None
    if REC_FIRST <= hm <= SETTLE_HM:
        if d is None:
            d = self._open_day(c, bar)
        if c.value == d["c"]:
            self._record(d, hm, bar, data.quote_bars.get(c))
    if hm == SETTLE_HM:
        if self._day is not None:
            self._close_day()
        self._roll_at_settlement(c, bar)

def _roll_at_settlement(self, c, bar):
    nxt = max(self._vol, key=self._vol.get) if self._vol else c
    self._vol = {}
    price = bar.close
    if nxt != c:
        nb = self.securities[nxt].cache.get_data(TradeBar) if nxt in self.securities else None
        if nb is None or nb.end_time.date() != bar.end_time.date():
            self._settle = None
            self._active = nxt
            self._switches += 1
            return
        price = nb.close
        self._switches += 1
    self._active = nxt
    self._settle = (nxt.value, price, self.time.date())

def _open_day(self, c, bar):
    dt = self.time.date()
    s = self._settle
    skip = ""
    if s is None:
        skip = "noprev"
    elif s[0] != c.value:
        skip = "roll"
    elif (dt - s[2]).days > 5:
        skip = "stale"
    if skip:
        self._skips[skip] = self._skips.get(skip, 0) + 1
    self._n += 1
    d = {"n": self._n, "date": dt, "d": dt.strftime("%Y%m%d"), "c": c.value, "sym": c,
         "ps": s[1] if s is not None else 0.0, "pst": "" if s is None else s[2].strftime("%Y%m%d"),
         "sk": skip, "o": [None] * SLOTS, "h": [None] * SLOTS, "l": [None] * SLOTS, "cl": [None] * SLOTS,
         "v": [None] * SLOTS, "qb": [None] * SLOTS, "qa": [None] * SLOTS, "qbs": [None] * SLOTS,
         "qas": [None] * SLOTS}
    self._day = d
    return d

def _record(self, d, hm, bar, q):
    i = _slot(hm)
    if i < 0 or i >= SLOTS or d["o"][i] is not None:
        return
    d["o"][i], d["h"][i], d["l"][i], d["cl"][i] = (float(bar.open), float(bar.high), float(bar.low),
                                                    float(bar.close))
    d["v"][i] = float(bar.volume)
    if q is not None and q.bid is not None and q.ask is not None and q.end_time == bar.end_time:
        # D-128: the active contract's RAW closing quote in the same minute, never an adjusted price
        d["qb"][i], d["qa"][i] = float(q.bid.close), float(q.ask.close)
        d["qbs"][i], d["qas"][i] = float(q.last_bid_size), float(q.last_ask_size)

def _close_day(self):
    d = self._day
    self._day = None
    m = atlas_measures(d["o"], d["h"], d["l"], d["cl"], d["ps"] if d["ps"] > 0 else None, TICK, SLOTS - 1)
    m.update(extra_measures(d["o"], d["h"], d["l"], d["cl"], TICK, SLOTS - 1, d["v"], d["qb"], d["qa"],
                            d["qbs"], d["qas"]))
    if m.get("st"):
        self._settled += 1
    head = ("|rec=" + str(d["n"]) + ";d=" + d["d"] + ";c=" + d["c"] + ";ps=" + _fmt(d["ps"])
            + ";pst=" + d["pst"] + ";sk=" + d["sk"])
    body = "".join(";" + k + "=" + ("" if m.get(k) is None else _fmt(m[k])) for k in KEYS)
    carrier = self._active or self.future.mapped or d["sym"]
    self.market_order(carrier, 1 if d["n"] % 2 else -1, tag="E|n=" + str(d["n"]) + head + body)
    self._last = head

def on_end_of_algorithm(self):
    skips = ",".join(k + ":" + str(v) for k, v in sorted(self._skips.items()))
    lines = [PREFIX + "|HEAD|v=1|market=" + MARKET + "|days=" + str(self._n) + "|settled=" + str(self._settled)
             + "|skips=" + skips + "|switches=" + str(self._switches)
             + "|open=" + ("1" if self._day is not None else "0"),
             PREFIX + "|LAST" + (self._last or "|none")]
    used = 0
    for line in lines:
        line = line[:LOG_BUDGET_BYTES - used - 80]
        self.log(line)
        used += len(line) + 1
    self.log(PREFIX + "|END|bytes=" + str(used))
"""


# ================================================================ R036-R037 -- extra datasets (D-127)
#
# Which of QuantConnect's other free datasets actually arrive on this account over development dates,
# asked before the effect atlas is amended to use any of them. Counts only: nothing is traded and no
# price leaves (D-120). Two kits, so that a dataset this account cannot read stops only its own run.
#
# R036: futures quote bars for ES and NQ (bid and ask present, both sizes present, and the regular-hours
#       spread bucketed in ticks: crossed or locked, 1, 2, 3 or more); VIX futures (VX); the VIX, SPX and
#       NDX index values, minute through the subscription and daily through a history request.
# R037: SPX and NDX index options and ES and NQ futures options at daily resolution from a month before
#       the documented January 2012 start: which days carry a chain, and on how many contracts open
#       interest, implied volatility, gamma and a price are populated. The underlyings are the control.
EXTRAS_PREFIX = "DXT"
EXTRAS_START, EXTRAS_END = GAP_START, GAP_END
EXTRAS_FUTURES = {"es": ("ES", 0.25), "nq": ("NQ", 0.25), "vx": ("VX", 0.05)}   # key: (ticker, tick)
EXTRAS_INDICES = {"vix": "VIX", "spx": "SPX", "ndx": "NDX"}
EXTRAS_SPREAD_SETS = ("es", "nq")
EXTRAS_CONTROL = "es"
#: Six years of counts for six sets, plus notes; LEAN's own lines still leave it under the free tier's 10 KB.
EXTRAS_LOG_BUDGET_BYTES = 9000

OPTIONS_PREFIX = "DXO"
OPTIONS_START, OPTIONS_END = date(2011, 12, 1), GAP_END
OPTIONS_SETS = {"spx": ("index", "SPX"), "ndx": ("index", "NDX"), "es": ("future", "ES"), "nq": ("future", "NQ")}
OPTIONS_STRIKES = 5              # strikes either side of the underlying
OPTIONS_EXPIRY_DAYS = 60         # index options: expiries within this many days
OPTIONS_FIELDS = {"oi": "open_interest", "iv": "implied_volatility", "g": "gamma", "px": "price"}
OPTIONS_CONTROL = "es"

_EXTRAS_SHARED = '''

def _clean(e):
    return (type(e).__name__ + ":" + str(e)).replace("|", "/").replace("\\n", " ")[:80]


def _count(counts, k, y, field, n=1):
    d = counts.setdefault(k, {}).setdefault(y, {})
    d[field] = d.get(field, 0) + n


def _summary(head, keys, first, counts, notes):
    """The lines of one compact summary within LOG_BUDGET_BYTES; the END line says whether it was cut."""
    lines = [PREFIX + "|HEAD|" + head]
    for k in keys:
        lines.append(PREFIX + "|SET|" + k + "|first=" + str(first.get(k)))
        for y in sorted(counts.get(k, {})):
            c = counts[k][y]
            lines.append(PREFIX + "|Y|" + k + "|" + str(y) + "|"
                         + "|".join(f + "=" + str(c[f]) for f in sorted(c)))
    for n in notes:
        lines.append(PREFIX + "|NOTE|" + n)
    used, kept, truncated = 0, [], False
    for line in lines:
        if used + len(line) + 1 > LOG_BUDGET_BYTES:
            truncated = True
            break
        kept.append(line)
        used += len(line) + 1
    return kept + [PREFIX + "|END|lines=" + str(len(kept)) + "|of=" + str(len(lines)) + "|bytes=" + str(used)
                   + "|truncated=" + str(truncated).lower()]
'''

EXTRAS_PREAMBLE = f'''
PREFIX = "{EXTRAS_PREFIX}"
LOG_BUDGET_BYTES = {EXTRAS_LOG_BUDGET_BYTES}
FUTURES = {EXTRAS_FUTURES!r}
INDICES = {EXTRAS_INDICES!r}
SPREAD_SETS = {EXTRAS_SPREAD_SETS!r}   # regular-hours quote bars bucketed by spread in ticks
''' + _EXTRAS_SHARED

EXTRAS_BODY = '''
def setup(self):
    # D-127, run R036: which extra datasets arrive over the development span. Counts only (D-120).
    self.set_time_zone(TimeZones.CHICAGO)
    self.set_cash(1000000)
    self._sym, self._first, self._counts, self._notes = {}, {}, {}, []
    for k, (t, tick) in FUTURES.items():
        try:
            self._sym[k] = self.add_future(t, Resolution.MINUTE).symbol
        except Exception as e:
            self._notes.append(k + ":add:" + _clean(e))
    for k, t in INDICES.items():
        try:
            self._sym[k] = self.add_index(t, Resolution.MINUTE).symbol
        except Exception as e:
            self._notes.append(k + ":add:" + _clean(e))

def on_data(self, data):
    y = self.time.year
    for k, s in self._sym.items():
        tb = data.bars.get(s)
        qb = data.quote_bars.get(s)
        if tb is None and qb is None:
            continue
        if k not in self._first:
            self._first[k] = str(self.time.date())
        if tb is not None:
            _count(self._counts, k, y, "tb")
        if qb is None:
            continue
        _count(self._counts, k, y, "qb")
        bid, ask = qb.bid, qb.ask
        if bid is None or ask is None or not (bid.close > 0 and ask.close > 0):
            continue
        _count(self._counts, k, y, "qok")
        if qb.last_bid_size > 0 and qb.last_ask_size > 0:
            _count(self._counts, k, y, "qsz")
        if k in SPREAD_SETS:
            n = int(round((ask.close - bid.close) / FUTURES[k][1]))
            _count(self._counts, k, y, "s0" if n <= 0 else "s" + str(min(n, 3)))

def on_end_of_algorithm(self):
    for k in INDICES:
        s = self._sym.get(k)
        if s is None:
            continue
        try:
            h = self.history(s, self.start_date, self.end_date, Resolution.DAILY)
            years = [] if h is None or len(h) == 0 else list(h.index.get_level_values(-1).year)
            for yr in years:
                _count(self._counts, k, int(yr), "day")
        except Exception as e:
            self._notes.append(k + ":history:" + _clean(e))
    for line in _summary("v=1|run=R036|notes=" + str(len(self._notes)), list(FUTURES) + list(INDICES),
                         self._first, self._counts, self._notes):
        self.log(line)
'''

OPTIONS_PREAMBLE = f'''
PREFIX = "{OPTIONS_PREFIX}"
LOG_BUDGET_BYTES = {EXTRAS_LOG_BUDGET_BYTES}
SETS = {OPTIONS_SETS!r}
STRIKES = {OPTIONS_STRIKES}
EXPIRY_DAYS = {OPTIONS_EXPIRY_DAYS}
FIELDS = {tuple(OPTIONS_FIELDS)!r}   # open interest, implied volatility, gamma, a price
''' + _EXTRAS_SHARED

OPTIONS_BODY = '''
def setup(self):
    # D-127, run R037: which option datasets arrive and which fields they carry. Daily; counts only (D-120).
    self.set_time_zone(TimeZones.CHICAGO)
    self.set_cash(1000000)
    self.universe_settings.resolution = Resolution.DAILY
    self._first, self._counts, self._notes, self._days, self._errs = {}, {}, [], {}, set()
    self._names, self._under = {}, {}
    for k, (kind, t) in SETS.items():
        try:
            if kind == "index":
                u = self.add_index(t, Resolution.DAILY).symbol
                opt = self.add_index_option(u, Resolution.DAILY)
                opt.set_filter(lambda x: x.strikes(-STRIKES, STRIKES).expiration(0, EXPIRY_DAYS))
            else:
                fut = self.add_future(t, Resolution.DAILY)
                fut.set_filter(0, 95)
                u = fut.symbol
                self.add_future_option(u, lambda x: x.strikes(-STRIKES, STRIKES))
            self._names[t] = k
            self._under[k] = u
        except Exception as e:
            self._notes.append(k + ":add:" + _clean(e))

def on_data(self, data):
    y = self.time.year
    for k, u in self._under.items():
        if data.bars.get(u) is not None:
            _count(self._counts, k, y, "u")
    for cs, chain in data.option_chains.items():
        try:
            k = self._names.get(cs.underlying.id.symbol)
        except Exception:
            k = None
        if k is None:
            continue
        n = 0
        for c in chain:
            n += 1
            _count(self._counts, k, y, "k")
            self._probe(k, y, c)
        if n:
            self._days.setdefault(k, set()).add(self.time.date())
            if k not in self._first:
                self._first[k] = str(self.time.date())

def _probe(self, k, y, c):
    for f in FIELDS:
        try:
            if f == "oi":
                v = c.open_interest
            elif f == "iv":
                v = c.implied_volatility
            elif f == "g":
                v = c.greeks.gamma
            else:
                v = max(c.last_price, c.bid_price, c.ask_price)
            v = float(v)
            if v == v and v != 0.0 and abs(v) != float("inf"):
                _count(self._counts, k, y, f)
        except Exception as e:
            _count(self._counts, k, y, "x" + f)
            if (k, f) not in self._errs:
                self._errs.add((k, f))
                self._notes.append(k + ":" + f + ":" + _clean(e))

def on_end_of_algorithm(self):
    for k, days in self._days.items():
        for d in days:
            _count(self._counts, k, d.year, "days")
    for line in _summary("v=1|run=R037|notes=" + str(len(self._notes)), list(SETS), self._first,
                         self._counts, self._notes):
        self.log(line)
'''


# ================================================================ R038 -- the atlas context (D-128)
#
# Daily, per session: the VIX index close, and the net gamma exposure of SPX and NDX option market makers
# (Baltussen et al. 2021; `propedge/research/gamma_core.py`, embedded verbatim) from each session's chain of
# contracts within CONTEXT_STRIKES listed strikes of the money and CONTEXT_EXPIRY_DAYS days of expiry. One
# order tag per session carries only these numbers (D-120); the final session goes in the LAST log line.
# A session's record is written when the next session's data first arrives, so every part of it is in.
CONTEXT_PREFIX = "CTX"
CONTEXT_START, CONTEXT_END = GAP_START, GAP_END
CONTEXT_OPTIONS = {"gs": "SPX", "gn": "NDX"}     # record key: the index whose options give the exposure
CONTEXT_STRIKES = 40
CONTEXT_EXPIRY_DAYS = 90
CONTEXT_KEYS = ("vix", "gs", "gsl", "gsn", "gn", "gnl", "gnn")


def context_preamble(keys: tuple = CONTEXT_KEYS) -> str:
    import inspect

    from propedge.research import gamma_core

    return f'''
from datetime import timedelta as _td
PREFIX = "{CONTEXT_PREFIX}"
LOG_BUDGET_BYTES = {LOG_BUDGET_BYTES}
OPTIONS = {CONTEXT_OPTIONS!r}
STRIKES = {CONTEXT_STRIKES}                  # listed strikes either side of the money
EXPIRY_DAYS = {CONTEXT_EXPIRY_DAYS}              # expiries within this many days
KEYS = {keys!r}   # g?: exposure with Black-Scholes gamma; g?l: platform gamma; g?n: contracts used


def _fmt(x):
    return ("%.10g" % x) if isinstance(x, float) else str(x)


def _clean(e):
    return (type(e).__name__ + ":" + str(e)).replace("|", "/").replace("\\n", " ")[:80]


class CarrierInitializer(BrokerageModelSecurityInitializer):
    """Zero fees: the carrier orders' own P&L is never used, so nothing is modelled on them."""

    def initialize(self, security):
        super().initialize(security)
        security.set_fee_model(ConstantFeeModel(0))


# ---------------------------------------------------------------- embedded verbatim from
# ---------------------------------------------------------------- propedge/research/gamma_core.py
{inspect.getsource(gamma_core)}
# ---------------------------------------------------------------- end of the embedded core
'''


CONTEXT_BODY = """
def setup(self):
    # D-128, run R038: per session, the VIX close and SPX/NDX option market makers' net gamma exposure.
    # One tag per session carries only these numbers (D-120).
    self.set_time_zone(TimeZones.CHICAGO)
    self.set_cash(1000000)
    self.universe_settings.resolution = Resolution.DAILY
    self.set_security_initializer(CarrierInitializer(
        self.brokerage_model, FuncSecuritySeeder(self.get_last_known_prices)))
    self._carrier = self.add_equity("SPY", Resolution.DAILY).symbol
    self._vix = self.add_index("VIX", Resolution.DAILY, fill_forward=False).symbol
    self._und, self._key = {}, {}
    for key, t in OPTIONS.items():
        u = self.add_index(t, Resolution.DAILY, fill_forward=False).symbol
        opt = self.add_index_option(u, Resolution.DAILY, fill_forward=False)
        opt.set_filter(lambda x: x.strikes(-STRIKES, STRIKES).expiration(0, EXPIRY_DAYS))
        self._und[key] = u
        self._key[t] = key
    self._recs, self._n, self._notes, self._errs = {}, 0, [], set()
    self._cnt = {"vix": 0, "gs": 0, "gn": 0, "both_gs": 0, "agree_gs": 0, "both_gn": 0, "agree_gn": 0}

def _sd(self, t):
    # the session a daily bar describes: its end time falls at or after that session's close
    return (t - _td(hours=2)).date()

def _rec(self, sd):
    for old in sorted(k for k in self._recs if k < sd):
        self._emit(self._recs.pop(old))
    return self._recs.setdefault(sd, {"sd": sd})

def on_data(self, data):
    b = data.bars.get(self._vix)
    if b is not None:
        self._rec(self._sd(b.end_time))["vix"] = float(b.close)
    for key, u in self._und.items():
        b = data.bars.get(u)
        if b is not None:
            self._rec(self._sd(b.end_time))["s_" + key] = float(b.close)
    for cs, chain in data.option_chains.items():
        try:
            key = self._key.get(cs.underlying.id.symbol)
        except Exception:
            key = None
        if key is None:
            continue
        sd = self._sd(self.time)
        r = self._rec(sd)
        s = r.get("s_" + key)
        if s is None:
            try:
                s = float(chain.underlying.price)
            except Exception:
                s = None
        if not s:
            continue
        rows = []
        for c in chain:
            try:
                g = float(c.greeks.gamma)
            except Exception as e:
                g = None
                if (key, "gamma") not in self._errs:
                    self._errs.add((key, "gamma"))
                    self._notes.append(key + ":gamma:" + _clean(e))
            rows.append((c.right == OptionRight.CALL, float(c.strike), (c.expiry.date() - sd).days / 365.0,
                         float(c.implied_volatility), float(c.open_interest), g))
        r[key], r[key + "l"], r[key + "n"] = nge(rows, s)

def _line(self, r):
    self._n += 1
    for k in ("vix", "gs", "gn"):
        if r.get(k) is not None:
            self._cnt[k] += 1
    for k in ("gs", "gn"):
        a, pl = r.get(k), r.get(k + "l")
        if a and pl:
            self._cnt["both_" + k] += 1
            if (a > 0) == (pl > 0):
                self._cnt["agree_" + k] += 1
    return ("|rec=" + str(self._n) + ";d=" + r["sd"].strftime("%Y%m%d")
            + "".join(";" + k + "=" + ("" if r.get(k) is None else _fmt(r[k])) for k in KEYS))

def _emit(self, r):
    line = self._line(r)
    self.market_on_open_order(self._carrier, 1 if self._n % 2 else -1, tag="C|n=" + str(self._n) + line)

def on_end_of_algorithm(self):
    tail = [self._line(self._recs[sd]) for sd in sorted(self._recs)]    # the last session(s), never flushed
    c = self._cnt
    lines = [PREFIX + "|HEAD|v=1|sessions=" + str(self._n) + "|vix=" + str(c["vix"]) + "|gs=" + str(c["gs"])
             + "|gn=" + str(c["gn"]) + "|agree_gs=" + str(c["agree_gs"]) + "/" + str(c["both_gs"])
             + "|agree_gn=" + str(c["agree_gn"]) + "/" + str(c["both_gn"]) + "|notes=" + str(len(self._notes))]
    lines += [PREFIX + "|LAST" + t for t in tail]
    lines += [PREFIX + "|NOTE|" + n for n in self._notes[:10]]
    used = 0
    for line in lines:
        line = line[:LOG_BUDGET_BYTES - used - 80]
        self.log(line)
        used += len(line) + 1
    self.log(PREFIX + "|END|bytes=" + str(used))
"""


# ================================================================ R039 -- gamma diagnostic (failure protocol, D-128)
#
# R038's exposures shrank toward zero after January 2012 with the two gamma computations agreeing in sign only
# by chance. Component test in isolation: on a short span where R038's values had collapsed, read SPX gamma three
# ways for the same sessions and log what each route sees -- (1) SLICE: the subscribed chain in on_data, R038's
# route, whose Greeks come from the platform's live price model; (2) FILTER: the universe the filter function
# receives, whose Greeks, implied volatility and open interest are the platform's pre-computed values from the
# previous session's close; (3) OC: `option_chain()` for the whole chain. For each: the index level used, the
# strikes seen, the exposure (both gammas) and one near-the-money contract's inputs. Logs only; a handful of
# numbers per session (D-120).
GDIAG_PREFIX = "GDG"
GDIAG_START, GDIAG_END = date(2013, 6, 3), date(2013, 6, 14)
GDIAG_SAMPLES = 4

GDIAG_PREAMBLE = f'''
PREFIX = "{GDIAG_PREFIX}"
LOG_BUDGET_BYTES = {COVERAGE_LOG_BUDGET_BYTES}
STRIKES = {CONTEXT_STRIKES}
EXPIRY_DAYS = {CONTEXT_EXPIRY_DAYS}
SAMPLES = {GDIAG_SAMPLES}                   # sessions logged per route


def _fmt(x):
    return ("%.6g" % x) if isinstance(x, float) else str(x)


def _clean(e):
    return (type(e).__name__ + ":" + str(e)).replace("|", "/").replace("\\n", " ")[:70]


def _fields(it, d):
    """(is_call, strike, years, iv, oi, platform gamma) from an OptionUniverse or OptionContract."""
    sym = getattr(it, "symbol", it)
    sid = sym.id
    return (sid.option_right == OptionRight.CALL, float(sid.strike_price), (sid.date.date() - d).days / 365.0,
            float(it.implied_volatility), float(it.open_interest), float(it.greeks.gamma))


def _summary(tag, d, items, und, extra=""):
    rows, bad, err = [], 0, ""
    for it in items:
        try:
            rows.append(_fields(it, d))
        except Exception as e:
            bad += 1
            err = err or _clean(e)
    ks = [r[1] for r in rows]
    nb, nl, n = nge(rows, und) if (rows and und) else (None, None, 0)
    s = (PREFIX + "|" + tag + "|d=" + str(d) + "|type=" + (type(items[0]).__name__ if items else "none")
         + "|n=" + str(len(items)) + "|ok=" + str(len(rows)) + "|bad=" + str(bad) + "|und=" + _fmt(und) + extra
         + "|kmin=" + _fmt(min(ks) if ks else None) + "|kmax=" + _fmt(max(ks) if ks else None)
         + "|nge_b=" + _fmt(nb) + "|nge_l=" + _fmt(nl) + "|used=" + str(n))
    if rows and und:
        a = min(rows, key=lambda r: abs(r[1] - und))
        s += "|atm=" + ",".join(_fmt(v) for v in (a[1], a[2], a[3], a[4], a[5], bs_gamma(und, a[1], a[2], a[3])))
    return s + ("|err=" + err if err else "")


# ---------------------------------------------------------------- embedded verbatim from
# ---------------------------------------------------------------- propedge/research/gamma_core.py
{{gamma_core}}
# ---------------------------------------------------------------- end of the embedded core
'''


def gdiag_preamble() -> str:
    import inspect

    from propedge.research import gamma_core

    return GDIAG_PREAMBLE.replace("{gamma_core}", inspect.getsource(gamma_core))


GDIAG_BODY = """
def setup(self):
    # R039 (failure protocol, D-128): SPX gamma read three ways on the same sessions; logs only.
    self.set_time_zone(TimeZones.CHICAGO)
    self.set_cash(1000000)
    self.universe_settings.resolution = Resolution.DAILY
    self._spx = self.add_index("SPX", Resolution.DAILY, fill_forward=False).symbol
    opt = self.add_index_option(self._spx, Resolution.DAILY, fill_forward=False)
    opt.set_filter(self._flt)
    self._canon = opt.symbol
    self._lines, self._notes, self._seen = [], [], {"FILTER": set(), "SLICE": set(), "OC": set()}
    self._close = {}

def _want(self, route, d):
    if d in self._seen[route] or len(self._seen[route]) >= SAMPLES:
        return False
    self._seen[route].add(d)
    return True

def _flt(self, x):
    try:
        d = self.time.date()
        if self._want("FILTER", d):
            und = None
            try:
                und = float(x.underlying.price)
            except Exception as e:
                self._notes.append("filter.underlying:" + _clean(e))
            self._lines.append(_summary("FILTER", d, list(x), und))
    except Exception as e:
        self._notes.append("filter:" + _clean(e))
    return x.strikes(-STRIKES, STRIKES).expiration(0, EXPIRY_DAYS)

def on_data(self, data):
    b = data.bars.get(self._spx)
    if b is not None:
        self._close[b.end_time.date()] = float(b.close)
        d = self.time.date()
        if self._want("OC", d):
            chain, how = None, ""
            for arg, label in ((self._canon, "canonical"), (self._spx, "underlying")):
                try:
                    chain, how = self.option_chain(arg), label
                    break
                except Exception as e:
                    self._notes.append("option_chain(" + label + "):" + _clean(e))
            if chain is not None:
                try:
                    self._lines.append(_summary("OC", d, list(chain), float(b.close), "|via=" + how))
                except Exception as e:
                    self._notes.append("oc:" + _clean(e))
    for cs, chain in data.option_chains.items():
        d = self.time.date()
        if not self._want("SLICE", d):
            continue
        s = self._close.get(max(self._close)) if self._close else None
        cu = None
        try:
            cu = float(chain.underlying.price)
        except Exception as e:
            self._notes.append("slice.underlying:" + _clean(e))
        items = list(chain)
        extra = "|cu=" + _fmt(cu)
        if items:
            c = min(items, key=lambda it: abs(float(it.strike) - (s or cu or 0)))
            try:
                extra += "|px=" + ",".join(_fmt(float(v)) for v in (c.last_price, c.bid_price, c.ask_price))
            except Exception as e:
                self._notes.append("slice.price:" + _clean(e))
        self._lines.append(_summary("SLICE", d, items, s, extra))

def on_end_of_algorithm(self):
    lines = [PREFIX + "|HEAD|v=1|lines=" + str(len(self._lines)) + "|notes=" + str(len(self._notes))]
    lines += self._lines + [PREFIX + "|NOTE|" + n for n in self._notes[:12]]
    used = 0
    for line in lines:
        line = line[:LOG_BUDGET_BYTES - used - 80]
        self.log(line)
        used += len(line) + 1
    self.log(PREFIX + "|END|bytes=" + str(used))
"""


# ================================================================ R040 -- the atlas context, version 2 (D-129)
#
# R039 found R038's route read open interest as zero on every subscribed contract, so its sums were noise; the
# filter function instead receives the whole chain -- every strike and expiry -- with the platform's
# end-of-day open interest, implied volatility and gamma from the previous session's close. Version 2 computes
# the exposure there, over the whole chain as the paper does, and stamps it with the session the data describes
# (the last index session seen before the filter runs). It subscribes to no option contract of its own choosing
# (the filter's token selection is the day's at-the-money contracts expiring that day, usually none). Integrity per
# session: the universe's underlying price equals that session's index close (g?u = 1).
CONTEXT_KEYS_V2 = CONTEXT_KEYS + ("gsu", "gnu")

_CONTEXT_V2_FIELDS = '''

def _fields(it, d):
    """(is_call, strike, years to expiry from session d, iv, open interest, platform gamma) of an OptionUniverse."""
    sid = it.symbol.id
    return (sid.option_right == OptionRight.CALL, float(sid.strike_price), (sid.date.date() - d).days / 365.0,
            float(it.implied_volatility), float(it.open_interest), float(it.greeks.gamma))
'''


def context_preamble_v2() -> str:
    return context_preamble(CONTEXT_KEYS_V2) + _CONTEXT_V2_FIELDS


CONTEXT_BODY_V2 = """
def setup(self):
    # D-129, run R040: per session, the VIX close and SPX/NDX option market makers' net gamma exposure, read in
    # the filter from the platform's end-of-day option universe (every strike and expiry). One tag per session.
    self.set_time_zone(TimeZones.CHICAGO)
    self.set_cash(1000000)
    self.universe_settings.resolution = Resolution.DAILY
    self.set_security_initializer(CarrierInitializer(
        self.brokerage_model, FuncSecuritySeeder(self.get_last_known_prices)))
    self._carrier = self.add_equity("SPY", Resolution.DAILY).symbol
    self._vix = self.add_index("VIX", Resolution.DAILY, fill_forward=False).symbol
    self._und, self._last_sd, self._close, self._read_sd = {}, {}, {}, {}
    for key, t in OPTIONS.items():
        u = self.add_index(t, Resolution.DAILY, fill_forward=False).symbol
        opt = self.add_index_option(u, Resolution.DAILY, fill_forward=False)
        opt.set_filter(lambda x, key=key: self._flt(key, x))
        self._und[key] = u
    self._recs, self._n, self._notes, self._errs = {}, 0, [], set()
    self._cnt = {"vix": 0, "gs": 0, "gn": 0, "both_gs": 0, "agree_gs": 0, "both_gn": 0, "agree_gn": 0,
                 "und_gs": 0, "und_gn": 0, "late": 0}

def _note(self, key, what, e):
    if (key, what) not in self._errs:
        self._errs.add((key, what))
        self._notes.append(key + ":" + what + ":" + _clean(e))

def _sd(self, t):
    # the session a daily bar describes: its end time falls at or after that session's close
    return (t - _td(hours=2)).date()

def _rec(self, sd):
    for old in sorted(k for k in self._recs if k < sd):
        self._emit(self._recs.pop(old))
    return self._recs.setdefault(sd, {"sd": sd})

def _flt(self, key, x):
    try:
        self._read(key, x)
    except Exception as e:
        self._note(key, "filter", e)
    return x.strikes(0, 0).expiration(0, 0)

def _read(self, key, x):
    sd = self._last_sd.get(key)            # the universe describes the last session whose close has been seen
    if sd is None or self._read_sd.get(key) == sd:
        return
    self._read_sd[key] = sd
    r = self._recs.get(sd)
    if r is None:
        self._cnt["late"] += 1
        return
    und = float(x.underlying.price)
    rows = []
    for it in x:
        try:
            rows.append(_fields(it, sd))
        except Exception as e:
            self._note(key, "contract", e)
    r[key], r[key + "l"], r[key + "n"] = nge(rows, und)
    close = self._close.get((key, sd))
    r[key + "u"] = 1 if (close and abs(und / close - 1.0) < 0.001) else 0

def on_data(self, data):
    b = data.bars.get(self._vix)
    if b is not None:
        self._rec(self._sd(b.end_time))["vix"] = float(b.close)
    for key, u in self._und.items():
        b = data.bars.get(u)
        if b is not None:
            sd = self._sd(b.end_time)
            self._rec(sd)
            self._last_sd[key] = sd
            self._close[(key, sd)] = float(b.close)

def _line(self, r):
    self._n += 1
    for k in ("vix", "gs", "gn"):
        if r.get(k) is not None:
            self._cnt[k] += 1
    for k in ("gs", "gn"):
        a, pl = r.get(k), r.get(k + "l")
        if a and pl:
            self._cnt["both_" + k] += 1
            if (a > 0) == (pl > 0):
                self._cnt["agree_" + k] += 1
        if r.get(k + "u") == 1:
            self._cnt["und_" + k] += 1
    return ("|rec=" + str(self._n) + ";d=" + r["sd"].strftime("%Y%m%d")
            + "".join(";" + k + "=" + ("" if r.get(k) is None else _fmt(r[k])) for k in KEYS))

def _emit(self, r):
    line = self._line(r)
    self.market_on_open_order(self._carrier, 1 if self._n % 2 else -1, tag="C|n=" + str(self._n) + line)

def on_end_of_algorithm(self):
    tail = [self._line(self._recs[sd]) for sd in sorted(self._recs)]    # the last session(s), never flushed
    c = self._cnt
    lines = [PREFIX + "|HEAD|v=2|sessions=" + str(self._n) + "|vix=" + str(c["vix"]) + "|gs=" + str(c["gs"])
             + "|gn=" + str(c["gn"]) + "|agree_gs=" + str(c["agree_gs"]) + "/" + str(c["both_gs"])
             + "|agree_gn=" + str(c["agree_gn"]) + "/" + str(c["both_gn"]) + "|und_gs=" + str(c["und_gs"])
             + "|und_gn=" + str(c["und_gn"]) + "|late=" + str(c["late"]) + "|notes=" + str(len(self._notes))]
    lines += [PREFIX + "|LAST" + t for t in tail]
    lines += [PREFIX + "|NOTE|" + n for n in self._notes[:10]]
    used = 0
    for line in lines:
        line = line[:LOG_BUDGET_BYTES - used - 80]
        self.log(line)
        used += len(line) + 1
    self.log(PREFIX + "|END|bytes=" + str(used))
"""


# ================================================================ atlas kit version 2 (D-132)
#
# R033 (GC) recorded 18 days and then nothing: version 1 rolls, and records the settlement reference, only on the
# active contract's bar at EXACTLY the settlement minute. QuantConnect's open-interest mapping first gave GC a thin
# serial contract with no trade at 12:30 on most days, so the roll never ran; when it finally ran, the volume
# leader since the start was a contract no longer in the universe, and the kit stopped. Version 2 keeps every
# measurement and every definition of version 1 and changes only the contract bookkeeping, as the leg kit v2 did
# (D-98): the roll runs at the first bar at or after the settlement minute (or, if a session had none, at the next
# session's first bar, without a reference); the next contract is the volume leader among contracts still in the
# universe and not expiring that day; an active contract that has left the universe is dropped. The reference
# price is the settlement-minute close only when that bar exists (st = 1), exactly the days version 1 could score.
ATLAS_BODY_V2 = """
def setup(self):
    # D-126, D-128, D-132: effect atlas, version 2 contract bookkeeping. One tag per day carries the day's measurements.
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
    self._active = None
    self._vol = {}
    self._seen, self._prev_c = None, None
    self._settle = None
    self._day = None
    self._rolled, self._last_date = None, None
    self._n, self._skips, self._switches, self._settled = 0, {}, 0, 0
    self._lost, self._late = 0, 0
    self._last = ""

def _hm(self):
    return (self.time.hour, self.time.minute)

def on_data(self, data):
    for sym, b in data.bars.items():
        if sym != self.future.symbol and sym.security_type == SecurityType.FUTURE:
            self._vol[sym] = self._vol.get(sym, 0.0) + float(b.volume)
    if self._active is not None and self._active not in self.securities:
        self._active = None                     # an expired or removed contract is never kept
        self._lost += 1
    c = self._active or self.future.mapped
    if c is None or c not in self.securities:
        return
    bar = self.securities[c].cache.get_data(TradeBar)
    if bar is None or (self._seen is not None and bar.end_time == self._seen and self._prev_c == c):
        return
    self._seen, self._prev_c = bar.end_time, c
    hm = self._hm()
    today = self.time.date()
    if self._last_date is not None and today != self._last_date:
        if self._day is not None:
            self._close_day()
        if self._rolled != self._last_date:     # the last session had no bar at or after the settlement minute
            self._late += 1
            self._roll(c, None, self._last_date)
            if (self._active or c) != c:        # this bar is the old contract's; the next is the new one's
                self._last_date = today
                return
    self._last_date = today
    d = self._day
    if REC_FIRST <= hm <= SETTLE_HM:
        if d is None:
            d = self._open_day(c, bar)
        if c.value == d["c"]:
            self._record(d, hm, bar, data.quote_bars.get(c))
    if hm >= SETTLE_HM and self._rolled != today:
        s = self._close_day() if self._day is not None else None
        self._roll(c, s, today)

def _roll(self, c, price, day):
    cands = {s: v for s, v in self._vol.items() if s in self.securities and s.id.date.date() > day}
    nxt = max(cands, key=cands.get) if cands else c
    self._vol = {}
    self._rolled = day
    if nxt != c:
        self._switches += 1
        self._active = nxt
        nb = self.securities[nxt].cache.get_data(TradeBar)
        if price is None or nb is None or nb.end_time.date() != day:
            self._settle = None
            return
        price = nb.close
    self._active = nxt
    self._settle = (nxt.value, price, day) if price is not None else None

def _open_day(self, c, bar):
    dt = self.time.date()
    s = self._settle
    skip = ""
    if s is None:
        skip = "noprev"
    elif s[0] != c.value:
        skip = "roll"
    elif (dt - s[2]).days > 5:
        skip = "stale"
    if skip:
        self._skips[skip] = self._skips.get(skip, 0) + 1
    self._n += 1
    d = {"n": self._n, "date": dt, "d": dt.strftime("%Y%m%d"), "c": c.value, "sym": c,
         "ps": s[1] if s is not None else 0.0, "pst": "" if s is None else s[2].strftime("%Y%m%d"),
         "sk": skip, "o": [None] * SLOTS, "h": [None] * SLOTS, "l": [None] * SLOTS, "cl": [None] * SLOTS,
         "v": [None] * SLOTS, "qb": [None] * SLOTS, "qa": [None] * SLOTS, "qbs": [None] * SLOTS,
         "qas": [None] * SLOTS}
    self._day = d
    return d

def _record(self, d, hm, bar, q):
    i = _slot(hm)
    if i < 0 or i >= SLOTS or d["o"][i] is not None:
        return
    d["o"][i], d["h"][i], d["l"][i], d["cl"][i] = (float(bar.open), float(bar.high), float(bar.low),
                                                    float(bar.close))
    d["v"][i] = float(bar.volume)
    if q is not None and q.bid is not None and q.ask is not None and q.end_time == bar.end_time:
        # D-128: the active contract's RAW closing quote in the same minute, never an adjusted price
        d["qb"][i], d["qa"][i] = float(q.bid.close), float(q.ask.close)
        d["qbs"][i], d["qas"][i] = float(q.last_bid_size), float(q.last_ask_size)

def _close_day(self):
    # returns the settlement-minute close when that bar was recorded (st = 1), else None
    d = self._day
    self._day = None
    m = atlas_measures(d["o"], d["h"], d["l"], d["cl"], d["ps"] if d["ps"] > 0 else None, TICK, SLOTS - 1)
    m.update(extra_measures(d["o"], d["h"], d["l"], d["cl"], TICK, SLOTS - 1, d["v"], d["qb"], d["qa"],
                            d["qbs"], d["qas"]))
    if m.get("st"):
        self._settled += 1
    head = ("|rec=" + str(d["n"]) + ";d=" + d["d"] + ";c=" + d["c"] + ";ps=" + _fmt(d["ps"])
            + ";pst=" + d["pst"] + ";sk=" + d["sk"])
    body = "".join(";" + k + "=" + ("" if m.get(k) is None else _fmt(m[k])) for k in KEYS)
    carrier = self._active or self.future.mapped or d["sym"]
    self.market_order(carrier, 1 if d["n"] % 2 else -1, tag="E|n=" + str(d["n"]) + head + body)
    self._last = head
    return d["cl"][SLOTS - 1] if m.get("st") else None

def on_end_of_algorithm(self):
    skips = ",".join(k + ":" + str(v) for k, v in sorted(self._skips.items()))
    lines = [PREFIX + "|HEAD|v=2|market=" + MARKET + "|days=" + str(self._n) + "|settled=" + str(self._settled)
             + "|skips=" + skips + "|switches=" + str(self._switches) + "|lost=" + str(self._lost)
             + "|late=" + str(self._late) + "|open=" + ("1" if self._day is not None else "0"),
             PREFIX + "|LAST" + (self._last or "|none")]
    used = 0
    for line in lines:
        line = line[:LOG_BUDGET_BYTES - used - 80]
        self.log(line)
        used += len(line) + 1
    self.log(PREFIX + "|END|bytes=" + str(used))
"""


# ================================================================ atlas kit version 3 (D-134)
#
# R035 (ZN, version 2) lost the reference settlement on every Monday: version 2 rolls at the first bar at or after
# the settlement minute, and the Sunday-evening session's bars (a new calendar date, after 14:00 on the clock) ran a
# roll with no settlement, wiping Friday's; the next midnight then "caught up" a Sunday that had no session. Version 3
# changes only those two conditions: the roll runs on a bar from the settlement minute up to CME's 16:00 CT daily
# break, and a missed roll is caught up only for a date whose regular session was recorded. Everything else is
# version 2's (and so version 1's measurements).
ATLAS_BODY_V3 = ATLAS_BODY_V2
for _old, _new in (
    ("# D-126, D-128, D-132: effect atlas, version 2 contract bookkeeping.",
     "# D-126, D-128, D-132, D-134: effect atlas, version 3 contract bookkeeping."),
    ("    self._rolled, self._last_date = None, None\n",
     "    self._rolled, self._last_date, self._opened = None, None, None\n"),
    ("        if self._rolled != self._last_date:     # the last session had no bar at or after the settlement minute\n",
     "        if self._rolled != self._last_date and self._opened == self._last_date:   # a recorded session, no roll\n"),
    ("    if hm >= SETTLE_HM and self._rolled != today:\n",
     "    if SETTLE_HM <= hm < (16, 0) and self._rolled != today:   # the same afternoon, before CME's daily break\n"),
    ("    self._n += 1\n    d = {\"n\": self._n,",
     "    self._n += 1\n    self._opened = dt\n    d = {\"n\": self._n,"),
    ('"|HEAD|v=2|market="', '"|HEAD|v=3|market="'),
):
    assert ATLAS_BODY_V3.count(_old) == 1, _old
    ATLAS_BODY_V3 = ATLAS_BODY_V3.replace(_old, _new)
del _old, _new


# ================================================================ R044 -- ZN price-grid check (failure protocol)
#
# R043 (ZN) flagged most bars "bad" in 2009-2011 and none in 2012-2014; its exported settlement prices sit off the
# 1/64 grid by at most 0.00032 of a tick, the offset of prices rounded to five decimals. The atlas's bad-bar count
# joins two conditions, so this run separates them, per year, over every ZN contract's minute bars in the
# development window: bars whose open, high, low and close are inconsistent; bars with any price off the grid at
# all; and bars off the grid by MORE than five-decimal rounding can explain. Logs only (D-120).
GRID_PREFIX = "GRD"
GRID_MARKET = "ZN"
GRID_TICK = 0.015625
GRID_ROUNDING_TICKS = 0.5e-5 / GRID_TICK          # five-decimal rounding's largest offset, in ticks

GRID_PREAMBLE = f'''
PREFIX = "{GRID_PREFIX}"
MARKET = "{GRID_MARKET}"
TICK = {GRID_TICK!r}
ROUNDING = {GRID_ROUNDING_TICKS!r}   # five-decimal rounding's largest offset, in ticks
LOG_BUDGET_BYTES = {LOG_BUDGET_BYTES}
'''

GRID_BODY = """
def setup(self):
    # R044 (failure protocol for R043's integrity count): ZN bars counted by year and condition; logs only.
    self.set_time_zone(TimeZones.CHICAGO)
    self.set_cash(1000000)
    self.future = self.add_future(MARKET, Resolution.MINUTE,
                                  data_normalization_mode=DataNormalizationMode.RAW,
                                  data_mapping_mode=DataMappingMode.OPEN_INTEREST,
                                  contract_depth_offset=0,
                                  extended_market_hours=True)
    self.future.set_filter(0, 120)
    self._c = {}

def on_data(self, data):
    y = self.time.year
    for sym, b in data.bars.items():
        if sym == self.future.symbol:
            continue
        c = self._c.setdefault(y, {"n": 0, "ohlc": 0, "off": 0, "beyond": 0, "maxoff": 0.0})
        c["n"] += 1
        o, h, l, cl = float(b.open), float(b.high), float(b.low), float(b.close)
        if not (l <= min(o, cl) and max(o, cl) <= h):
            c["ohlc"] += 1
        worst = max(abs(v / TICK - round(v / TICK)) for v in (o, h, l, cl))
        if worst > 1e-6:
            c["off"] += 1
        if worst > 2.0 * ROUNDING:
            c["beyond"] += 1
        if worst > c["maxoff"]:
            c["maxoff"] = worst

def on_end_of_algorithm(self):
    lines = [PREFIX + "|HEAD|v=1|market=" + MARKET + "|rounding_ticks=" + ("%.6g" % ROUNDING)]
    for y in sorted(self._c):
        c = self._c[y]
        lines.append(PREFIX + "|Y|" + str(y) + "|n=" + str(c["n"]) + "|ohlc=" + str(c["ohlc"]) + "|off="
                     + str(c["off"]) + "|beyond=" + str(c["beyond"]) + "|maxoff=" + ("%.6g" % c["maxoff"]))
    used = 0
    for line in lines:
        line = line[:LOG_BUDGET_BYTES - used - 80]
        self.log(line)
        used += len(line) + 1
    self.log(PREFIX + "|END|bytes=" + str(used))
"""


# ================================================================ R045-R046 -- FV1, the fair-value model (D-142)
#
# The complete JJ-inspired model (config/model_fv.yaml), scored INSIDE QuantConnect: the kit records the market's
# one-minute bars from 08:00 to 15:00 CT with version 3's contract bookkeeping (D-132, D-134), runs
# `propedge/outcomes/fv_core.run_day` for both stop families at both price scales at each day's close, and exports
# only the trades and a few integrity numbers per day (D-120), in order tags of at most FV_TAG_CHARS characters.
FV_PREFIX = "FV1"
FV_RUNS = {"NQ": "R045-fv1-NQ", "ES": "R046-fv1-ES"}
#: FV1 unchanged on the development block D-144 opened (config/model_fv.yaml `extension_1419`).
FV_EXT_RUNS = {"NQ": "R047-fv1-NQ-1419", "ES": "R048-fv1-ES-1419"}
FV_EXT_START, FV_EXT_END = date(2014, 5, 28), date(2019, 12, 31)
FV_TAG_CHARS = 600
FV_FAMILIES = ("atr_bands", "structural")
FV_TAG_CODES = {"cont": "c", "rev": "r", "recont": "k"}


def _minutes(hm: str) -> int:
    h, m = hm.split(":")
    return int(h) * 60 + int(m)


def fv_params(market: str) -> dict:
    """Everything the kit and the repository need from config/model_fv.yaml and config/fills.yaml."""
    import yaml

    from propedge import CONFIG_DIR
    from propedge.execution.fills import FillModel

    cfg = yaml.safe_load((CONFIG_DIR / "model_fv.yaml").read_text(encoding="utf-8"))
    mk = cfg["markets"][market]
    rec0 = _minutes(cfg["recording"]["first"])
    slot = lambda hm: _minutes(hm) - rec0                                     # noqa: E731
    sessions = [{"name": name, "anchor": slot(s["anchor"]) + 1, "first": slot(s["first_signal"]),
                 "cont_until": slot(s["continuation_until"]), "last": slot(s["last_signal"])}
                for name, s in cfg["sessions"].items()]
    fm = FillModel.load("assumed")
    tick = float(mk["tick"])
    fills = {"tick": tick, "entry": fm.entry_slippage_ticks, "stop": fm.stop_slippage_ticks,
             "target": fm.target_slippage_ticks, "flatten": fm.flatten_slippage_ticks,
             "tick_value": float(mk["tick_value"]), "point_value": float(mk["tick_value"]) / tick,
             "round_turn": float(mk["round_turn"])}
    bands = {"hi": 20 / 17000 * 100, "lo": 7 / 17000 * 100, "stop_hi": 50 / 17000 * 100,
             "stop_mid": 25 / 17000 * 100, "stop_lo": 16.5 / 17000 * 100}          # JJ's points at NQ 17,000
    last = slot(cfg["time_exit"])
    return {"rec_first": (rec0 // 60, rec0 % 60), "slots": last + 1, "settle": (last + rec0) // 60,
            "settle_hm": ((last + rec0) // 60, (last + rec0) % 60), "p_ref": float(mk["p_ref"]), "tick": tick,
            "fills": fills,
            "p": {"sessions": sessions, "last_slot": last, "floor_ticks": int(mk["floor_ticks"]), "w": 0.20,
                  "rr": 1.5, "attempts": 2, "max_losses": 2, "bands": bands}}


def fv_preamble(market: str) -> str:
    import inspect

    from propedge.outcomes import fv_core

    q = fv_params(market)
    return f'''
MARKET = "{market}"
REC_FIRST = {q["rec_first"]!r}          # CT, END time of the first recorded bar
SETTLE_HM = {q["settle_hm"]!r}          # CT, the time exit and the day's last recorded bar
SLOTS = {q["slots"]}
TICK = {q["tick"]!r}
P_REF = {q["p_ref"]!r}                  # the price level trades are rescaled to (D-106); the actual level too
FILTER_DAYS = 120
PREFIX = "{FV_PREFIX}"
LOG_BUDGET_BYTES = {LOG_BUDGET_BYTES}
TAG_CHARS = {FV_TAG_CHARS}
FAMILIES = {FV_FAMILIES!r}
TAGS = {FV_TAG_CODES!r}
PARAMS = {q["p"]!r}
FILLS = {q["fills"]!r}
ANCHOR_AM = PARAMS["sessions"][0]["anchor"]


def _fmt(x):
    return ("%.10g" % x) if isinstance(x, float) else str(x)


def _slot(hm):
    return (hm[0] - REC_FIRST[0]) * 60 + (hm[1] - REC_FIRST[1])


def _code(fi, si, tr):
    """One trade: family, scale, session, tag, side, then signal/entry/exit slots, stop ticks, exit kind, R net,
    R at zero cost, MFE and MAE in R, the ATR band."""
    return (str(fi) + str(si) + tr["session"][0] + TAGS[tr["tag"]] + ("+" if tr["d"] > 0 else "-")
            + "," + str(tr["t"]) + "," + str(tr["j0"]) + "," + str(tr["j_exit"]) + "," + str(tr["stop_ticks"])
            + "," + tr["exit_kind"] + "," + ("%.4f" % tr["r_net"]) + "," + ("%.4f" % tr["r_price"])
            + "," + ("%.3f" % tr["mfe"]) + "," + ("%.3f" % tr["mae"]) + "," + str(tr["band"]))


class CarrierInitializer(BrokerageModelSecurityInitializer):
    """Zero fees: the carrier orders' own P&L is never used, so nothing is modelled on them."""

    def initialize(self, security):
        super().initialize(security)
        security.set_fee_model(ConstantFeeModel(0))


# ---------------------------------------------------------------- embedded verbatim from
# ---------------------------------------------------------------- propedge/outcomes/fv_core.py
{inspect.getsource(fv_core)}
# ---------------------------------------------------------------- end of the embedded core
'''


FV_BODY = """
def setup(self):
    # D-142: FV1, the fair-value model, scored in the cloud; version 3 contract bookkeeping (D-132, D-134).
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
    self._active = None
    self._vol = {}
    self._seen, self._prev_c = None, None
    self._settle = None
    self._day = None
    self._rolled, self._last_date, self._opened = None, None, None
    self._n, self._skips, self._switches, self._settled = 0, {}, 0, 0
    self._lost, self._late, self._trades, self._orders = 0, 0, 0, 0
    self._last = ""

def _hm(self):
    return (self.time.hour, self.time.minute)

def on_data(self, data):
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
    hm = self._hm()
    today = self.time.date()
    if self._last_date is not None and today != self._last_date:
        if self._day is not None:
            self._close_day()
        if self._rolled != self._last_date and self._opened == self._last_date:
            self._late += 1
            self._roll(c, None, self._last_date)
            if (self._active or c) != c:
                self._last_date = today
                return
    self._last_date = today
    d = self._day
    if REC_FIRST <= hm <= SETTLE_HM:
        if d is None:
            d = self._open_day(c, bar)
        if c.value == d["c"]:
            self._record(d, hm, bar)
    if SETTLE_HM <= hm < (16, 0) and self._rolled != today:
        s = self._close_day() if self._day is not None else None
        self._roll(c, s, today)

def _roll(self, c, price, day):
    cands = {s: v for s, v in self._vol.items() if s in self.securities and s.id.date.date() > day}
    nxt = max(cands, key=cands.get) if cands else c
    self._vol = {}
    self._rolled = day
    if nxt != c:
        self._switches += 1
        self._active = nxt
        nb = self.securities[nxt].cache.get_data(TradeBar)
        if price is None or nb is None or nb.end_time.date() != day:
            self._settle = None
            return
        price = nb.close
    self._active = nxt
    self._settle = (nxt.value, price, day) if price is not None else None

def _open_day(self, c, bar):
    dt = self.time.date()
    s = self._settle
    skip = ""
    if s is None:
        skip = "noprev"
    elif s[0] != c.value:
        skip = "roll"
    elif (dt - s[2]).days > 5:
        skip = "stale"
    if skip:
        self._skips[skip] = self._skips.get(skip, 0) + 1
    self._n += 1
    self._opened = dt
    d = {"n": self._n, "date": dt, "d": dt.strftime("%Y%m%d"), "c": c.value, "sym": c,
         "ps": s[1] if s is not None else 0.0, "pst": "" if s is None else s[2].strftime("%Y%m%d"),
         "sk": skip, "o": [None] * SLOTS, "h": [None] * SLOTS, "l": [None] * SLOTS, "cl": [None] * SLOTS}
    self._day = d
    return d

def _record(self, d, hm, bar):
    i = _slot(hm)
    if i < 0 or i >= SLOTS or d["o"][i] is not None:
        return
    d["o"][i], d["h"][i], d["l"][i], d["cl"][i] = (float(bar.open), float(bar.high), float(bar.low),
                                                    float(bar.close))

def _close_day(self):
    # D-142: the day's FV1 trades at both scales for both stop families; only the trades and integrity leave.
    d = self._day
    self._day = None
    o, h, l, cl = d["o"], d["h"], d["l"], d["cl"]
    st = 1 if o[SLOTS - 1] is not None else 0
    if st:
        self._settled += 1
    bad = 0
    for i in range(SLOTS):
        if o[i] is None:
            continue
        vals = (o[i], h[i], l[i], cl[i])
        if (not (l[i] <= min(o[i], cl[i]) and max(o[i], cl[i]) <= h[i])
                or any(abs(v / TICK - round(v / TICK)) > 1e-6 for v in vals)):
            bad += 1
    cov = sum(1 for i in range(ANCHOR_AM, SLOTS) if o[i] is not None) / float(SLOTS - ANCHOR_AM)
    r0 = (h[ANCHOR_AM] - l[ANCHOR_AM]) / TICK if o[ANCHOR_AM] is not None else None
    pre = [(h[i] - l[i]) / TICK for i in range(ANCHOR_AM - 4, ANCHOR_AM) if o[i] is not None]
    rp = sum(pre) / len(pre) if pre else None
    ref = o[ANCHOR_AM] if o[ANCHOR_AM] is not None else next((x for x in o if x is not None), None)
    codes = []
    if ref:
        for si, scale_to in enumerate((P_REF, None)):
            so, sh, sl, sc = scaled(o, h, l, cl, ref, scale_to)
            for fi, fam in enumerate(FAMILIES):
                for tr in run_day(so, sh, sl, sc, PARAMS, fam, FILLS):
                    codes.append(_code(fi, si, tr))
    self._trades += len(codes)
    head = (";d=" + d["d"] + ";c=" + d["c"] + ";ref=" + _fmt(ref if ref else 0.0) + ";sk=" + d["sk"]
            + ";st=" + str(st) + ";bad=" + str(bad) + ";cov=" + _fmt(cov)
            + ";r0=" + ("" if r0 is None else _fmt(r0)) + ";rp=" + ("" if rp is None else _fmt(rp)))
    chunks, cur = [], ""
    for x in codes:
        if cur and len(cur) + 1 + len(x) > TAG_CHARS:
            chunks.append(cur)
            cur = x
        else:
            cur = x if not cur else cur + "/" + x
    chunks.append(cur)
    carrier = self._active or self.future.mapped or d["sym"]
    for k, x in enumerate(chunks):
        tag = ("F|n=" + str(d["n"]) + "|rec=" + str(d["n"]) + ";k=" + str(k) + ";K=" + str(len(chunks))
               + (head if k == 0 else "") + ";x=" + x)
        self._orders += 1
        self.market_order(carrier, 1 if self._orders % 2 else -1, tag=tag)
    self._last = "|rec=" + str(d["n"]) + head
    return cl[SLOTS - 1] if st else None

def on_end_of_algorithm(self):
    skips = ",".join(k + ":" + str(v) for k, v in sorted(self._skips.items()))
    lines = [PREFIX + "|HEAD|v=1|market=" + MARKET + "|days=" + str(self._n) + "|settled=" + str(self._settled)
             + "|trades=" + str(self._trades) + "|orders=" + str(self._orders) + "|skips=" + skips
             + "|switches=" + str(self._switches) + "|lost=" + str(self._lost) + "|late=" + str(self._late)
             + "|open=" + ("1" if self._day is not None else "0"),
             PREFIX + "|LAST" + (self._last or "|none")]
    used = 0
    for line in lines:
        line = line[:LOG_BUDGET_BYTES - used - 80]
        self.log(line)
        used += len(line) + 1
    self.log(PREFIX + "|END|bytes=" + str(used))
"""


# ================================================================ the bracket outcome map (D-149)

BMAP_PREFIX = "BM1"
BMAP_RUNS = {("NQ", "0914"): "R049-bmap-NQ-0914", ("NQ", "1419"): "R050-bmap-NQ-1419",
             ("ES", "0914"): "R051-bmap-ES-0914", ("ES", "1419"): "R052-bmap-ES-1419"}
#: (warm-up start, window start, window end): each run starts about a month early to fill D (config: session_scale).
BMAP_WINDOWS = {"0914": (date(2009, 5, 1), date(2009, 6, 1), date(2014, 5, 27)),
                "1419": (date(2014, 4, 25), date(2014, 5, 28), date(2019, 12, 31))}
BMAP_TAG_CHARS = 600
BMAP_TIME_CODES = "abcdefghijkl"


def bmap_params(market: str) -> dict:
    """Everything the kit and the repository need from config/bracket_map.yaml and config/fills.yaml."""
    import yaml

    from propedge import CONFIG_DIR
    from propedge.execution.fills import FillModel

    cfg = yaml.safe_load((CONFIG_DIR / "bracket_map.yaml").read_text(encoding="utf-8"))
    mk = cfg["markets"][market]
    rec0 = _minutes("08:00")
    times = [_minutes(t) - rec0 for t in cfg["decisions"]["times_ct"]]
    if len(times) > len(BMAP_TIME_CODES):
        raise ValueError("more decision times than time codes")
    fm = FillModel.load("assumed")
    tick = float(mk["tick"])
    last = _minutes("15:00") - rec0
    return {"rec_first": (8, 0), "slots": last + 1, "settle_hm": (15, 0), "p_ref": float(mk["p_ref"]), "tick": tick,
            "fills": {"tick": tick, "entry": fm.entry_slippage_ticks},
            "p": {"times": times, "widths": [float(w) for w in cfg["stop_widths_of_D"]], "last_slot": last,
                  "floor_ticks": int(mk["floor_ticks"])},
            "d_sessions": 20, "min_cov": 0.9}


def bmap_preamble(market: str, window: str) -> str:
    import inspect

    from propedge.outcomes import bracket_core

    q = bmap_params(market)
    _, w0, _ = BMAP_WINDOWS[window]
    return f'''
MARKET = "{market}"
REC_FIRST = {q["rec_first"]!r}          # CT, END time of the first recorded bar
SETTLE_HM = {q["settle_hm"]!r}          # CT, the time exit and the day's last recorded bar
SLOTS = {q["slots"]}
TICK = {q["tick"]!r}
P_REF = {q["p_ref"]!r}                  # every walk is on the day rescaled so its 08:30 open maps here (D-106)
WIN_START = ({w0.year}, {w0.month}, {w0.day})   # days before this are warm-up: they fill D and record nothing
D_SESSIONS = {q["d_sessions"]}
MIN_COV = {q["min_cov"]!r}
FILTER_DAYS = 120
PREFIX = "{BMAP_PREFIX}"
LOG_BUDGET_BYTES = {LOG_BUDGET_BYTES}
TAG_CHARS = {BMAP_TAG_CHARS}
TIME_CODES = "{BMAP_TIME_CODES}"
PARAMS = {q["p"]!r}
FILLS = {q["fills"]!r}


def _fmt(x):
    return ("%.10g" % x) if isinstance(x, float) else str(x)


def _slot(hm):
    return (hm[0] - REC_FIRST[0]) * 60 + (hm[1] - REC_FIRST[1])


class CarrierInitializer(BrokerageModelSecurityInitializer):
    """Zero fees: the carrier orders' own P&L is never used, so nothing is modelled on them."""

    def initialize(self, security):
        super().initialize(security)
        security.set_fee_model(ConstantFeeModel(0))


# ---------------------------------------------------------------- embedded verbatim from
# ---------------------------------------------------------------- propedge/outcomes/bracket_core.py
{inspect.getsource(bracket_core)}
# ---------------------------------------------------------------- end of the embedded core
'''


BMAP_BODY = """
def setup(self):
    # D-149: the bracket outcome map, measured in the cloud; version 3 contract bookkeeping (D-132, D-134).
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
    self._active = None
    self._vol = {}
    self._seen, self._prev_c = None, None
    self._settle = None
    self._day = None
    self._rolled, self._last_date, self._opened = None, None, None
    self._n, self._skips, self._switches, self._settled = 0, {}, 0, 0
    self._lost, self._late, self._entries, self._orders, self._warm = 0, 0, 0, 0, 0
    self._ranges, self._prev = [], None
    self._last = ""

def _hm(self):
    return (self.time.hour, self.time.minute)

def on_data(self, data):
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
    hm = self._hm()
    today = self.time.date()
    if self._last_date is not None and today != self._last_date:
        if self._day is not None:
            self._close_day()
        if self._rolled != self._last_date and self._opened == self._last_date:
            self._late += 1
            self._roll(c, None, self._last_date)
            if (self._active or c) != c:
                self._last_date = today
                return
    self._last_date = today
    d = self._day
    if REC_FIRST <= hm <= SETTLE_HM:
        if d is None:
            d = self._open_day(c, bar)
        if c.value == d["c"]:
            self._record(d, hm, bar)
    if SETTLE_HM <= hm < (16, 0) and self._rolled != today:
        s = self._close_day() if self._day is not None else None
        self._roll(c, s, today)

def _roll(self, c, price, day):
    cands = {s: v for s, v in self._vol.items() if s in self.securities and s.id.date.date() > day}
    nxt = max(cands, key=cands.get) if cands else c
    self._vol = {}
    self._rolled = day
    if nxt != c:
        self._switches += 1
        self._active = nxt
        nb = self.securities[nxt].cache.get_data(TradeBar)
        if price is None or nb is None or nb.end_time.date() != day:
            self._settle = None
            return
        price = nb.close
    self._active = nxt
    self._settle = (nxt.value, price, day) if price is not None else None

def _open_day(self, c, bar):
    dt = self.time.date()
    s = self._settle
    skip = ""
    if s is None:
        skip = "noprev"
    elif s[0] != c.value:
        skip = "roll"
    elif (dt - s[2]).days > 5:
        skip = "stale"
    if skip:
        self._skips[skip] = self._skips.get(skip, 0) + 1
    self._opened = dt
    d = {"date": dt, "d": dt.strftime("%Y%m%d"), "c": c.value, "sym": c, "sk": skip,
         "o": [None] * SLOTS, "h": [None] * SLOTS, "l": [None] * SLOTS, "cl": [None] * SLOTS, "v": [0.0] * SLOTS}
    self._day = d
    return d

def _record(self, d, hm, bar):
    i = _slot(hm)
    if i < 0 or i >= SLOTS or d["o"][i] is not None:
        return
    d["o"][i], d["h"][i], d["l"][i], d["cl"][i] = (float(bar.open), float(bar.high), float(bar.low),
                                                    float(bar.close))
    d["v"][i] = float(bar.volume)

def _close_day(self):
    # D-149: every decision's path summary at each stop width, the day's integrity and bucketed features; no prices.
    d = self._day
    self._day = None
    o, h, l, cl, v = d["o"], d["h"], d["l"], d["cl"], d["v"]
    st = 1 if o[SLOTS - 1] is not None else 0
    if st:
        self._settled += 1
    bad = 0
    for i in range(SLOTS):
        if o[i] is None:
            continue
        vals = (o[i], h[i], l[i], cl[i])
        if (not (l[i] <= min(o[i], cl[i]) and max(o[i], cl[i]) <= h[i])
                or any(abs(x / TICK - round(x / TICK)) > 1e-6 for x in vals)):
            bad += 1
    cov = sum(1 for i in range(ANCHOR_AM, SLOTS) if o[i] is not None) / float(SLOTS - ANCHOR_AM)
    D = sum(self._ranges[-D_SESSIONS:]) / D_SESSIONS if len(self._ranges) >= D_SESSIONS else None
    ref = o[ANCHOR_AM]
    prev = self._prev
    rng = session_range_pct(o, h, l, SLOTS - 1) if (st and cov >= MIN_COV) else None
    in_window = (d["date"].year, d["date"].month, d["date"].day) >= WIN_START
    if in_window:
        self._n += 1
        codes, sk, g, pc = [], "", 9, 9
        if ref and D:
            f = P_REF / ref
            so, sh, sl, sc = scaled(o, h, l, cl, ref, P_REF)
            sp = None
            if prev is not None:
                sp = {"close": prev["close"] * f, "high": prev["high"] * f, "low": prev["low"] * f,
                      "same_contract": prev["c"] == d["c"]}
            day = run_day(so, sh, sl, sc, v, PARAMS, FILLS, D, sp)
            if day is not None:
                sk = ",".join(str(x) for x in day["sk"])
                g, pc = day["gap"], day["clv"]
                for t, feats, out in day["rows"]:
                    sides = []
                    for side in (1, -1):
                        sides.append(",".join(encode(out[(side, wi)]) if (side, wi) in out else "-"
                                              for wi in range(len(PARAMS["widths"]))))
                        self._entries += sum(1 for wi in range(len(PARAMS["widths"])) if (side, wi) in out)
                    codes.append(TIME_CODES[PARAMS["times"].index(t)] + "".join(str(x) for x in feats) + "="
                                 + "~".join(sides))
        head = (";d=" + d["d"] + ";c=" + d["c"] + ";sk0=" + d["sk"] + ";st=" + str(st) + ";bad=" + str(bad)
                + ";cov=" + _fmt(cov) + ";D=" + ("" if D is None else "%.4f" % D) + ";sk=" + sk
                + ";g=" + str(g) + ";pc=" + str(pc))
        chunks, cur = [], ""
        for x in codes:
            if cur and len(cur) + 1 + len(x) > TAG_CHARS:
                chunks.append(cur)
                cur = x
            else:
                cur = x if not cur else cur + "/" + x
        chunks.append(cur)
        carrier = self._active or self.future.mapped or d["sym"]
        for k, x in enumerate(chunks):
            tag = ("B|n=" + str(self._n) + "|rec=" + str(self._n) + ";k=" + str(k) + ";K=" + str(len(chunks))
                   + (head if k == 0 else "") + ";x=" + x)
            self._orders += 1
            self.market_order(carrier, 1 if self._orders % 2 else -1, tag=tag)
        self._last = "|rec=" + str(self._n) + head
    else:
        self._warm += 1
    if rng is not None:
        self._ranges.append(rng)
    if st:
        hs = [h[j] for j in range(ANCHOR_AM, SLOTS) if h[j] is not None]
        ls = [l[j] for j in range(ANCHOR_AM, SLOTS) if l[j] is not None]
        self._prev = {"c": d["c"], "close": cl[SLOTS - 1], "high": max(hs), "low": min(ls)} if hs else None
    else:
        self._prev = None
    return cl[SLOTS - 1] if st else None

def on_end_of_algorithm(self):
    skips = ",".join(k + ":" + str(v) for k, v in sorted(self._skips.items()))
    lines = [PREFIX + "|HEAD|v=1|market=" + MARKET + "|days=" + str(self._n) + "|settled=" + str(self._settled)
             + "|entries=" + str(self._entries) + "|orders=" + str(self._orders) + "|skips=" + skips
             + "|switches=" + str(self._switches) + "|lost=" + str(self._lost) + "|late=" + str(self._late)
             + "|warm=" + str(self._warm) + "|open=" + ("1" if self._day is not None else "0"),
             PREFIX + "|LAST" + (self._last or "|none")]
    used = 0
    for line in lines:
        line = line[:LOG_BUDGET_BYTES - used - 80]
        self.log(line)
        used += len(line) + 1
    self.log(PREFIX + "|END|bytes=" + str(used))
"""


# ================================================================ R053-R060 -- IM2, noise-band entries (P-04)
#
# P-04 (2026-09-27, before any IM2 kit ran) carries P-03 forward with the fidelity audits' fixes: orders on the micro's
# tick grid, worst-price fills in release minutes from the embedded calendar (`RELEASES`, exported per session as
# `rel`), and the lowest price while held (`mn`) for Topstep's price-lock rule; HEAD's version is 2.
#
# The paper's noise-band entries (config/model_im2.yaml; P-04 §3), scored INSIDE QuantConnect: the kit records each
# session's one-minute bars with version 3's contract bookkeeping (D-132, D-134), keeps the last 14 complete sessions'
# move profiles and the prior close, reads which sessions the exchange calendar schedules as full ones from the
# market-hours database of the LEAN version it runs on, runs `propedge/outcomes/im2_core.run_day` at each session's
# close, and exports only the entries, their bracket outcomes at 1, 2 and 3 R at both scales, the audit prices and a
# few integrity numbers per session (D-120, D-148, D-156), in order tags of at most IM2_TAG_CHARS characters.
#
# How the kit applies P-04's calendar and roll rules (P-03's, unchanged), fixed before any IM2 data is read (the core's own choices are in
# `im2_core`'s docstring):
# * A full session is a weekday the market-hours database lists as neither a holiday, an early close nor a late open
#   ("scheduled as a full session"). Holidays and early closes are not traded. A late open is not a full session and
#   is not traded either; its entries are computed and exported flagged `sk=late`, for the record only -- they never
#   enter e, its bound or the campaign.
# * A scheduled early close is incomplete whatever its bars show: it gives no sigma profile and no prior close. A date
#   the database lists as a holiday is not a session even if it has bars: no profile, no roll, and the previous
#   session's prior close stands for the next one.
# * The previous session is the last earlier weekday that is not a listed holiday; a session with no bar inside its
#   window is incomplete (and listed in `gone`), so the session after it has no prior close.
# * Bar end times are on the exchange's clock and `self.time` on Chicago's; the roll compares the new contract's bar
#   with the close bar on the exchange clock. A session with no bar in its close minute rolls at the next date's first
#   bar with no prior close (the bracket map's rule).
IM2_PREFIX = "IM2"
IM2_MARKETS = ("ES", "CL", "6E", "NG")
IM2_RUNS = {("ES", "0914"): "R053-im2-ES-0914", ("ES", "1419"): "R054-im2-ES-1419",
            ("CL", "0914"): "R055-im2-CL-0914", ("CL", "1419"): "R056-im2-CL-1419",
            ("6E", "0914"): "R057-im2-6E-0914", ("6E", "1419"): "R058-im2-6E-1419",
            ("NG", "0914"): "R059-im2-NG-0914", ("NG", "1419"): "R060-im2-NG-1419"}
#: D-200: IM2's second implementation (`propedge/verification/`), one kit per development run above, on its window
IM2X_RUNS = {("ES", "0914"): "R063-im2x-ES-0914", ("ES", "1419"): "R064-im2x-ES-1419",
             ("CL", "0914"): "R065-im2x-CL-0914", ("CL", "1419"): "R066-im2x-CL-1419",
             ("6E", "0914"): "R067-im2x-6E-0914", ("6E", "1419"): "R068-im2x-6E-1419",
             ("NG", "0914"): "R069-im2x-NG-0914", ("NG", "1419"): "R070-im2x-NG-1419"}
IM2_TAG_CHARS = 600


def _im2_cfg() -> dict:
    import yaml

    from propedge import CONFIG_DIR

    return yaml.safe_load((CONFIG_DIR / "model_im2.yaml").read_text(encoding="utf-8"))


def im2_windows() -> dict[str, tuple[date, date, date]]:
    """(warm-up start, window start, window end) per development half, from config/model_im2.yaml."""
    return {w: tuple(date.fromisoformat(str(x)) for x in v)
            for w, v in _im2_cfg()["development_windows"].items()}


def im2_params(market: str) -> dict:
    """Everything the kit and the repository need from config/model_im2.yaml and config/fills.yaml."""
    from propedge.execution.fills import FillModel

    cfg = _im2_cfg()
    mk = cfg["markets"][market]
    s0, s1 = _minutes(mk["open"]), _minutes(mk["close"])
    step, margin = int(cfg["decision_every_minutes"]), int(cfg["decision_margin_minutes"])
    first = -(-(s0 + margin) // step) * step
    last = (s1 - margin) // step * step
    fm = FillModel.load(cfg["fill_profile"])
    return {"open_min": s0, "close_min": s1, "rec_first": ((s0 + 1) // 60, (s0 + 1) % 60),
            "settle_hm": (s1 // 60, s1 % 60), "slots": s1 - s0, "tick": float(mk["tick"]),
            "p_ref": float(mk["p_ref"]), "micro": mk["micro"], "min_cov": float(cfg["min_coverage"]),
            "hot_minutes": int(cfg["release_hot_minutes"]),
            "fills": {"tick": float(mk["micro_tick"]), "entry": fm.entry_slippage_ticks,
                      "stop": fm.stop_slippage_ticks, "target": fm.target_slippage_ticks,
                      "flatten": fm.flatten_slippage_ticks},
            "p": {"times": [m - s0 - 1 for m in range(first, last + 1, step)], "last_slot": s1 - s0 - 1,
                  "lookback": int(cfg["lookback_sessions"]), "mult": float(cfg["volatility_multiplier"]),
                  "rr": [int(r) for r in cfg["brackets_r"]], "seq_rr": int(cfg["sequencing_r"]),
                  "wait": int(cfg["wait_minutes"])}}


def im2_releases(market: str, window: str) -> dict[str, list[int]]:
    """P-04: the release minutes (CT) of `market` from its warm-up start to the window's end, from the calendar."""
    from propedge import REPO_ROOT
    from propedge.data.im2_releases import releases

    warm, _, end = im2_windows()[window]
    return releases(market, warm, end, REPO_ROOT / _im2_cfg()["release_calendar"])


def im2_pack_releases(rel: dict[str, list[int]], base: date) -> tuple[str, dict[str, int]]:
    """The calendar packed for the kit, which must stay small (QuantConnect limits a file's characters): one token per
    date, its day count from `base` in three base-36 digits followed by one capital letter per release minute; and
    the letters' minutes. The kit's `_unpack_releases` inverts it (tests/test_im2_kit.py)."""
    import numpy as np

    mins = sorted({m for v in rel.values() for m in v})
    letter = {m: chr(65 + i) for i, m in enumerate(mins)}
    toks = []
    for k, v in rel.items():
        n = (date(int(k[:4]), int(k[4:6]), int(k[6:])) - base).days
        if not 0 <= n < 36 ** 3:
            raise ValueError(f"{k} is outside the packable span from {base}")
        toks.append(np.base_repr(n, 36).lower().rjust(3, "0") + "".join(letter[m] for m in v))
    return ",".join(toks), {c: m for m, c in letter.items()}


def im2_preamble(market: str, window: str) -> str:
    import inspect

    from propedge.outcomes import im2_core

    q = im2_params(market)
    warm, w0, _ = im2_windows()[window]
    packed, codes = im2_pack_releases(im2_releases(market, window), warm)
    return f'''
from datetime import date as _d0, timedelta as _td

MARKET = "{market}"
OPEN_MIN = {q["open_min"]}              # CT minutes after midnight of the session open (slot s starts at OPEN_MIN + s)
HOT_MINUTES = {q["hot_minutes"]}                 # P-04: a release's window, the release minute and the next


def _unpack_releases(packed, base, codes):
    """{{YYYYMMDD: release minutes CT}} from the packed calendar: per date, its day count from `base` in three base-36
    digits, then one letter per release minute (`codes`)."""
    out = {{}}
    for tok in packed.split(","):
        if tok:
            out[(base + _td(days=int(tok[:3], 36))).strftime("%Y%m%d")] = [codes[ch] for ch in tok[3:]]
    return out


# P-04: this market's releases (config/im2_release_calendar.csv: FOMC statements, EIA crude, EIA natural gas), packed
RELEASES = _unpack_releases("{packed}", _d0({warm.year}, {warm.month}, {warm.day}), {codes!r})
REC_FIRST = {q["rec_first"]!r}          # CT, END time of the session's first bar (it starts at the open)
SETTLE_HM = {q["settle_hm"]!r}          # CT, END time of the session's last bar: the close, and the roll
SLOTS = {q["slots"]}
TICK = {q["tick"]!r}                    # the standard contract's tick: the data's price grid
P_REF = {q["p_ref"]!r}                  # each session's open maps here for fills, costs and R (D-106)
WIN_START = ({w0.year}, {w0.month}, {w0.day})   # sessions before this are warm-up: they fill the lookback, record nothing
LOOKBACK = {q["p"]["lookback"]}
MIN_COV = {q["min_cov"]!r}
FILTER_DAYS = 120
PREFIX = "{IM2_PREFIX}"
LOG_BUDGET_BYTES = {LOG_BUDGET_BYTES}
TAG_CHARS = {IM2_TAG_CHARS}
PARAMS = {q["p"]!r}
FILLS = {q["fills"]!r}                  # the traded micro's tick ({q["micro"]}) and the assumed profile (D-95)


def _fmt(x):
    return ("%.10g" % x) if isinstance(x, float) else str(x)


def _slot(hm):
    return (hm[0] - REC_FIRST[0]) * 60 + (hm[1] - REC_FIRST[1])


def _key(d):
    return (d.year, d.month, d.day)


def _date_set(xs):
    """The dates in a market-hours collection -- a set of dates, or a dictionary keyed by date -- as (y, m, d)."""
    out = set()
    for k in xs:
        k = getattr(k, "key", None) or getattr(k, "Key", None) or k
        y = getattr(k, "year", None)
        out.add((y, k.month, k.day) if y is not None else (k.Year, k.Month, k.Day))
    return out


def _walk_code(w):
    if w is None:
        return "-"
    return ("%.10g" % w["dist"]) + "," + ",".join(
        k + str(j) + ":" + ("%.5f" % r) + ":" + ("%.5f" % m) for k, j, r, m in w["br"])


def _code(e):
    """One entry: side and decision slot, entry slot, the decision close, the upper and lower bands, VWAP and the
    lowest price while held (P-04; actual prices); then the walk at the reference price and at actual prices, each the
    stop distance and, per R, exit kind and slot : R after the fills' ticks : MAE in R."""
    return (("+" if e["d"] > 0 else "-") + str(e["t"]) + "," + str(e["j0"]) + "," + _fmt(e["cl"]) + ","
            + _fmt(e["ub"]) + "," + _fmt(e["lb"]) + "," + _fmt(e["vw"]) + "," + _fmt(e["mn"]) + "~"
            + _walk_code(e["walks"][0]) + "~" + _walk_code(e["walks"][1]))


def _hot(key):
    """P-04: the session's release slots (bar STARTS OPEN_MIN + slot), the release minute and the next."""
    return set(m - OPEN_MIN + k for m in RELEASES.get(key, []) for k in range(HOT_MINUTES)
               if 0 <= m - OPEN_MIN + k < SLOTS)


class CarrierInitializer(BrokerageModelSecurityInitializer):
    """Zero fees: the carrier orders' own P&L is never used, so nothing is modelled on them."""

    def initialize(self, security):
        super().initialize(security)
        security.set_fee_model(ConstantFeeModel(0))


# ---------------------------------------------------------------- embedded verbatim from
# ---------------------------------------------------------------- propedge/outcomes/im2_core.py
{inspect.getsource(im2_core)}
# ---------------------------------------------------------------- end of the embedded core
'''


IM2_BODY = """
def setup(self):
    # P-04 (IM2): noise-band entries bracketed at 1, 2 and 3 R, scored in the cloud; version 3 contract bookkeeping
    # (D-132, D-134); the sessions traded are those the market-hours database of this LEAN version schedules.
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
    hours = self.future.exchange.hours
    self._hol = _date_set(hours.holidays)
    self._early = _date_set(hours.early_closes)
    self._late_open = _date_set(hours.late_opens)
    self._active = None
    self._vol = {}
    self._seen, self._prev_c = None, None
    self._settle = None
    self._day = None
    self._rolled, self._last_date, self._opened = None, None, None
    self._cursor = _date(*START)
    self._n, self._skips, self._switches, self._settled, self._complete = 0, {}, 0, 0, 0
    self._lost, self._late, self._entries, self._orders, self._warm = 0, 0, 0, 0, 0
    self._signals, self._dropped, self._through = 0, 0, 0
    self._prof = []
    self._last = ""

def _hm(self):
    return (self.time.hour, self.time.minute)

def _full(self, x):
    # P-04: a full session is a weekday the calendar lists as neither a holiday, an early close nor a late open.
    k = _key(x)
    return x.weekday() < 5 and k not in self._hol and k not in self._early and k not in self._late_open

def _prev_session(self, x):
    # The exchange's previous session: the last earlier weekday that is not a holiday (an early close counts).
    x = x - _td(days=1)
    while x.weekday() >= 5 or _key(x) in self._hol:
        x = x - _td(days=1)
    return x

def on_data(self, data):
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
    hm = self._hm()
    today = self.time.date()
    if self._last_date is not None and today != self._last_date:
        if self._day is not None:
            self._close_day()
        if (self._rolled != self._last_date and self._opened == self._last_date
                and _key(self._last_date) not in self._hol):
            self._late += 1
            self._roll(c, None, self._last_date, None)
            if (self._active or c) != c:
                self._last_date = today
                return
    self._last_date = today
    d = self._day
    if REC_FIRST <= hm <= SETTLE_HM:
        if d is None and self._opened != today:
            d = self._open_day(c, bar)
        if d is not None and c.value == d["c"]:
            self._record(d, hm, bar)
    if SETTLE_HM <= hm < (16, 0) and self._rolled != today:
        s = self._close_day() if self._day is not None else None
        if _key(today) in self._hol:
            self._rolled = today            # a listed holiday is not a session: no roll, the prior close stands
        else:
            self._roll(c, s, today, bar)

def _roll(self, c, price, day, bar):
    # P-04: at the close bar, the contract expiring after today with the most volume since the last close bar; the
    # prior close is the new contract's close at this close bar, and none if it has no bar there. `price` is set only
    # when `bar` is the close bar; bar end times are on the exchange's clock, so the two bars are compared on it.
    cands = {s: v for s, v in self._vol.items() if s in self.securities and s.id.date.date() > day}
    nxt = max(cands, key=cands.get) if cands else c
    self._vol = {}
    self._rolled = day
    if nxt != c:
        self._switches += 1
        self._active = nxt
        nb = self.securities[nxt].cache.get_data(TradeBar)
        if price is None or nb is None or bar is None or nb.end_time != bar.end_time:
            self._settle = None
            return
        price = float(nb.close)
    self._active = nxt
    self._settle = (nxt.value, price, day) if price is not None else None

def _open_day(self, c, bar):
    dt = self.time.date()
    gone, x = [], self._cursor
    while x < dt:
        if _key(x) >= WIN_START and self._full(x):
            gone.append(x.strftime("%Y%m%d"))       # a scheduled full session with no bar inside it
        x = x + _td(days=1)
    self._cursor = dt + _td(days=1)
    k = _key(dt)
    cal = ("H" if k in self._hol else "E" if k in self._early else "L" if k in self._late_open
           else "W" if dt.weekday() >= 5 else "F")
    s = self._settle
    skip, pc = "", None
    if cal not in ("F", "L"):
        skip = "cal"
    elif s is None or s[2] != self._prev_session(dt):
        skip = "noprev"
    elif s[0] != c.value:
        skip = "roll"
    elif len(self._prof) < LOOKBACK:
        skip = "look"
    else:
        pc = s[1]
        if cal == "L":
            skip = "late"                   # not a full session: entries exported for the record, never traded
    win = k >= WIN_START
    if win and skip:
        self._skips[skip] = self._skips.get(skip, 0) + 1
    self._opened = dt
    d = {"date": dt, "d": dt.strftime("%Y%m%d"), "c": c.value, "sym": c, "win": win, "cal": cal, "sk": skip,
         "pc": pc, "gone": gone, "o": [None] * SLOTS, "h": [None] * SLOTS, "l": [None] * SLOTS,
         "cl": [None] * SLOTS, "v": [0.0] * SLOTS}
    self._day = d
    return d

def _record(self, d, hm, bar):
    i = _slot(hm)
    if i < 0 or i >= SLOTS or d["o"][i] is not None:
        return
    d["o"][i], d["h"][i], d["l"][i], d["cl"][i] = (float(bar.open), float(bar.high), float(bar.low),
                                                    float(bar.close))
    d["v"][i] = float(bar.volume)

def _close_day(self):
    # P-04: the session's entries at both scales, its integrity, counts and release minutes; no bar leaves.
    d = self._day
    self._day = None
    o, h, l, c, v = d["o"], d["h"], d["l"], d["cl"], d["v"]
    st = 1 if o[SLOTS - 1] is not None else 0
    cov = sum(1 for x in o if x is not None) / float(SLOTS)
    full = 1 if complete(o, SLOTS - 1, MIN_COV) else 0
    counts = full and d["cal"] not in ("H", "E")     # a listed holiday or early close gives no profile, no prior close
    if d["win"]:
        self._n += 1
        self._settled += st
        self._complete += full
        bad = 0
        for i in range(SLOTS):
            if o[i] is None:
                continue
            vals = (o[i], h[i], l[i], c[i])
            if (not (l[i] <= min(o[i], c[i]) and max(o[i], c[i]) <= h[i])
                    or any(abs(x / TICK - round(x / TICK)) > 1e-6 for x in vals)):
                bad += 1
        res = (run_day(o, h, l, c, v, d["pc"], self._prof, PARAMS, FILLS, P_REF, _hot(d["d"]))
               if d["sk"] in ("", "late") else None)
        codes = [_code(e) for e in res["entries"]] if res else []
        n = (lambda key: res[key] if res else 0)
        self._entries += len(codes)
        self._signals += n("signals")
        self._dropped += n("dropped")
        self._through += n("through")
        ref = session_open(o)
        head = (";d=" + d["d"] + ";c=" + d["c"] + ";cal=" + d["cal"] + ";sk=" + d["sk"] + ";st=" + str(st)
                + ";full=" + str(full) + ";bad=" + str(bad) + ";cov=" + ("%.4f" % cov)
                + ";ref=" + ("" if ref is None else _fmt(ref)) + ";pc=" + ("" if d["pc"] is None else _fmt(d["pc"]))
                + ";np=" + str(len(self._prof)) + ";sig=" + str(n("signals")) + ";drop=" + str(n("dropped"))
                + ";thru=" + str(n("through")) + ";tha=" + str(n("through_actual")) + ";nob=" + str(n("no_bar"))
                + ";mis=" + str(n("missing"))
                + ";nbd=" + str(n("no_band")) + ";E=" + str(len(codes))
                + ";rel=" + ",".join(str(m) for m in RELEASES.get(d["d"], [])) + ";gone=" + ",".join(d["gone"]))
        chunks, cur = [], ""
        for x in codes:
            if cur and len(cur) + 1 + len(x) > TAG_CHARS:
                chunks.append(cur)
                cur = x
            else:
                cur = x if not cur else cur + "/" + x
        chunks.append(cur)
        carrier = self._active or self.future.mapped or d["sym"]
        for k, x in enumerate(chunks):
            tag = ("I|n=" + str(self._n) + "|rec=" + str(self._n) + ";k=" + str(k) + ";K=" + str(len(chunks))
                   + (head if k == 0 else "") + ";x=" + x)
            self._orders += 1
            self.market_order(carrier, 1 if self._orders % 2 else -1, tag=tag)
        self._last = "|rec=" + str(self._n) + head
    else:
        self._warm += 1
    if counts:
        self._prof.append(move_profile(o, c))
        if len(self._prof) > LOOKBACK:
            self._prof.pop(0)
    return c[SLOTS - 1] if counts else None

def on_end_of_algorithm(self):
    skips = ",".join(k + ":" + str(v) for k, v in sorted(self._skips.items()))
    end = _date(*END)
    gone, x = [], self._cursor
    while x <= end:
        if _key(x) >= WIN_START and self._full(x):
            gone.append(x.strftime("%Y%m%d"))
        x = x + _td(days=1)
    span = (lambda ks: str(sum(1 for k in ks if WIN_START <= k <= END)))
    lines = [PREFIX + "|HEAD|v=2|market=" + MARKET + "|days=" + str(self._n) + "|settled=" + str(self._settled)
             + "|complete=" + str(self._complete) + "|entries=" + str(self._entries)
             + "|signals=" + str(self._signals) + "|dropped=" + str(self._dropped)
             + "|through=" + str(self._through) + "|orders=" + str(self._orders) + "|skips=" + skips
             + "|switches=" + str(self._switches) + "|lost=" + str(self._lost) + "|late=" + str(self._late)
             + "|warm=" + str(self._warm) + "|open=" + ("1" if self._day is not None else "0")
             + "|hol=" + span(self._hol) + "|ec=" + span(self._early) + "|lo=" + span(self._late_open)
             + "|gone=" + ",".join(gone),
             PREFIX + "|LAST" + (self._last or "|none")]
    used = 0
    for line in lines:
        line = line[:LOG_BUDGET_BYTES - used - 80]
        self.log(line)
        used += len(line) + 1
    self.log(PREFIX + "|END|bytes=" + str(used))
"""


# ================================================================ R061-R062 -- pre-release drift, family K (D-164)
#
# 2B's F-032 (Kurov, Sancetta, Strasser and Wolfe 2018, JFQA): prices start moving in the direction of the coming
# surprise about 30 minutes before a scheduled macro release, and that drift is about 40 % of the total adjustment.
# One kit per market records, for every scheduled release in config/release_calendar.csv, the pre-release return
# ([t - 30 min, t - 1 min]) and the release return ([t - 1 min, t + 5 min]) on the mapped contract, plus how many
# bars the window had and which contract carried it. Bars stay in the cloud; one order tag per event (D-120).
RELEASE_PREFIX = "REL"
RELEASE_RUNS = {"ES": "R061-release-ES", "ZN": "R062-release-ZN"}
RELEASE_START = date(2009, 6, 1)
RELEASE_END = date(2014, 5, 27)


def release_events(market: str) -> dict[str, list[tuple[int, int, str]]]:
    """{YYYYMMDD: [(hour_ct, minute_ct, codes), ...]} for `market` from config/release_calendar.csv. Events at the
    same minute of the same day are one event whose code joins theirs with '+' (a joint release)."""
    import csv

    from propedge import CONFIG_DIR

    joint: dict[tuple[str, int, int], list[str]] = {}
    with (CONFIG_DIR / "release_calendar.csv").open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if market not in row["markets"].split(","):
                continue
            d = row["date"].replace("-", "")
            h, m = (int(x) for x in row["time_ct"].split(":"))
            joint.setdefault((d, h, m), []).append(row["code"])
    out: dict[str, list[tuple[int, int, str]]] = {}
    for (d, h, m), codes in sorted(joint.items()):
        out.setdefault(d, []).append((h, m, "+".join(sorted(codes))))
    return out


def release_preamble(market: str) -> str:
    import inspect

    import yaml

    from propedge import CONFIG_DIR
    from propedge.research import release_core

    cfg = yaml.safe_load((CONFIG_DIR / "effect_atlas.yaml").read_text(encoding="utf-8"))
    m = cfg["markets"][market]
    events = release_events(market)
    return f'''
MARKET = "{market}"
TICK = {float(m["tick"])!r}                   # the standard contract's tick
FILTER_DAYS = {int(m["filter_days"])}
PREFIX = "{RELEASE_PREFIX}"
LOG_BUDGET_BYTES = {LOG_BUDGET_BYTES}
# Scheduled releases (config/release_calendar.csv, D-164): YYYYMMDD -> [(hour CT, minute CT, codes)], the
# data's time zone. Joint releases at one minute are one event.
EVENTS = {events!r}


def _fmt(x):
    return ("%.10g" % x) if isinstance(x, float) else str(x)


class CarrierInitializer(BrokerageModelSecurityInitializer):
    """Zero fees: the carrier orders' own P&L is never used, so nothing is modelled on them."""

    def initialize(self, security):
        super().initialize(security)
        security.set_fee_model(ConstantFeeModel(0))


# ---------------------------------------------------------------- embedded verbatim from
# ---------------------------------------------------------------- propedge/research/release_core.py
{inspect.getsource(release_core)}
# ---------------------------------------------------------------- end of the embedded core
'''


RELEASE_BODY = """
def setup(self):
    # D-164: pre-release drift (2B F-032). Bars stay in the cloud; one tag per scheduled release carries its returns.
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
    self._seen, self._prev_c = None, None
    self._open = {}
    self._n, self._switches = 0, 0
    self._last_c = None
    self._last = ""
    self._scheduled = sum(len(v) for v in EVENTS.values())

def on_data(self, data):
    c = self.future.mapped
    if c is None or c not in self.securities:
        return
    bar = self.securities[c].cache.get_data(TradeBar)
    if bar is None or (self._seen is not None and bar.end_time == self._seen and self._prev_c == c):
        return
    self._seen, self._prev_c = bar.end_time, c
    if self._last_c is not None and c.value != self._last_c:
        self._switches += 1
    self._last_c = c.value
    d = self.time.strftime("%Y%m%d")
    mod = self.time.hour * 60 + self.time.minute          # minute of day at which this bar ENDS
    self._flush(d, mod)
    for h, m, code in EVENTS.get(d, ()):
        r = h * 60 + m
        # recorded from GRACE minutes before the window, so a missing t-30 bar can take the latest earlier close
        if r - PRE_MIN - GRACE <= mod <= r + POST_MIN:
            ev = self._open.get((d, r))
            if ev is None:
                ev = {"d": d, "r": r, "k": code, "c": c.value, "roll": 0, "cl": {}}
                self._open[(d, r)] = ev
            if c.value != ev["c"]:
                ev["roll"] = 1
            ev["cl"][mod] = float(bar.close)

def _flush(self, d, mod):
    # emit every open event whose window has ended: an earlier date, or this date past release + POST_MIN
    for key in list(self._open):
        ev = self._open[key]
        if ev["d"] < d or (ev["d"] == d and mod > ev["r"] + POST_MIN):
            self._emit(ev)
            del self._open[key]

def _emit(self, ev):
    m = event_measures(ev["cl"], ev["r"])
    self._n += 1
    head = ("|rec=" + str(self._n) + ";d=" + ev["d"] + ";t=" + "%02d%02d" % (ev["r"] // 60, ev["r"] % 60)
            + ";k=" + ev["k"] + ";c=" + ev["c"] + ";roll=" + str(ev["roll"]))
    body = "".join(";" + k + "=" + ("" if m.get(k) is None else _fmt(m[k])) for k in KEYS)
    carrier = self.future.mapped
    self.market_order(carrier, 1 if self._n % 2 else -1, tag="E|n=" + str(self._n) + head + body)
    self._last = head

def on_end_of_algorithm(self):
    for key in list(self._open):
        self._emit(self._open.pop(key))
    lines = [PREFIX + "|HEAD|v=1|market=" + MARKET + "|scheduled=" + str(self._scheduled)
             + "|emitted=" + str(self._n) + "|nodata=" + str(self._scheduled - self._n)
             + "|switches=" + str(self._switches),
             PREFIX + "|LAST" + (self._last or "|none")]
    used = 0
    for line in lines:
        line = line[:LOG_BUDGET_BYTES - used - 80]
        self.log(line)
        used += len(line) + 1
    self.log(PREFIX + "|END|bytes=" + str(used))
"""

