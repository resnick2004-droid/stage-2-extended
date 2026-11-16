# IM2X — notes on the second implementation (D-200)

Written by the implementer, 2026-09-28, as the brief's §6 requires (`docs/verification/im2_second_implementation.md`).

## Files opened in the repository

- `docs/verification/im2_second_implementation.md` (the brief)
- `prereg/P-04_im2_lifecycle_v3.md`
- `docs/candidates/cards/IM2.md`
- `config/model_im2.yaml`
- `config/instruments.yaml`
- `propedge/data/qc_template.py`
- my own files under `propedge/verification/`

Nothing else was opened, searched or globbed. Rendering the kit ran `render_algorithm`, which imports
`propedge.data.cloud_guard` and `propedge.data.window`; I did not open either. The session's `CLAUDE.md` and memory
index were supplied to me automatically at the start; I did not open them. A `git status` showed the names, not the
contents, of other files the commissioning session had changed. The self-checks ran from a scratch folder outside the
repository.

## Documentation relied on

QuantConnect's pages could not be fetched from this machine: `quantconnect.com` and `github.com` refused the
connection, and the QuantConnect documentation search tool failed ("All connection attempts failed"). Each call was
checked against **web search summaries** of these pages instead:

- docs/v2/writing-algorithms/universes/futures and .../futures/requesting-data/universes: `add_future(...,
  extended_market_hours=, data_mapping_mode=DataMappingMode.OPEN_INTEREST, data_normalization_mode=,
  contract_depth_offset=)`, `set_filter(0, 182)` with days, the continuous future's `mapped`
- .../futures/handling-data: `slice.bars`, `is_fill_forward`, and the `fill_forward` argument set when the
  subscription is created
- docs/v2/writing-algorithms/universes/settings: `extended_market_hours`, `contract_depth_offset`
- .../key-concepts/time-modeling/time-zones: `set_time_zone(TimeZones.CHICAGO)`
- .../key-concepts/time-modeling/timeslices: the slice's time is the algorithm's time; a bar arrives at its end time
- docs/v2/writing-algorithms/securities/market-hours, and LEAN's `Common/Securities/SecurityExchangeHours.cs` on
  GitHub: `exchange.hours.holidays`, `early_closes` and `late_opens` (dictionaries keyed by date)
- docs/v2/writing-algorithms/initialization: a `BrokerageModelSecurityInitializer` subclass with
  `SecuritySeeder.NULL`, and `ConstantFeeModel(0)`
- .../trading-and-orders/order-properties and .../order-types/market-orders: `market_order(symbol, quantity, tag=)`
- .../algorithm-framework/universe-selection/futures-universes: `on_securities_changed`, `symbol.is_canonical()`
- .../datasets/algoseek/us-futures: the `Futures.*` tickers, and US futures data from May 2009
- .../trading-and-orders/liquidating-positions: orders placed while the market is closed become market-on-open orders

**Not confirmed by any page I could read** (from my knowledge of LEAN; the first cloud run will show them):
`add_future` taking `market=` and `fill_forward=` as keywords; `Market.CME` and `Market.NYMEX`; `symbol.id.date`
being the contract's expiry; futures market orders going through outside regular hours rather than becoming
market-on-open; and orders placed in `on_end_of_algorithm` being processed and recorded in a backtest (used only
when the data end before the last session's close).

## Open cases and what I decided

1. **What triggers the roll.** The first slice of the session's date, at or after the close and before 16:00 CT,
   that carries a real (not fill-forward) bar of any contract of the future. It does not have to be the active
   contract's bar. The continuous series' own bars are ignored everywhere.
2. **The fallback roll.** This happens at the first such slice dated after the session's date (for example Sunday
   17:01 after a Friday early close). That slice's volume counts toward the roll that ends there.
3. **"Expire after today"** means the expiry date (`symbol.id.date`) is after the date on which the roll happens:
   the session's date normally, the later date at a fallback.
4. **"Most volume."** Only contracts with positive volume since the last roll count. On a tie the active contract is
   kept if it is among the tied; otherwise the earliest expiry wins, then the symbol's value.
5. **The volume window** runs from the bar after the last roll through the roll bar. A holiday session has no roll,
   so its volume carries into the next window.
6. **A session's contract (`c`, and the `roll` test)** is the active contract at the session's first bar. If the
   active contract is replaced mid-session, the later bars come from the new contract.
7. **Replacement.** When the active contract leaves the universe, the next slice takes the continuous future's
   `mapped`. This counts as a switch.
8. **`switches`** counts every change of the active contract over the whole run, warm-up included, but not the first
   naming.
9. **Calendar code precedence:** H, then E, then L, then W, then F.
10. **`hol`, `ec`, `lo`** count each list's entries dated inside the window. A date listed twice counts in both
    lists.
11. **Weekend sessions (W) with bars** are treated literally. They are skipped (`cal`), but they roll, give a prior
    close and can enter the store. Only H has no roll.
12. **`pc` in the tag** is the prior close the session carries, whether or not it qualifies. It is empty only when
    none is carried. A `noprev` session can therefore show an older close.
13. **Integrity fields on skipped sessions** come from `evaluate_session` called with no prior close.
14. **`evaluate_session` details.** Bars outside (open, close] are dropped, and a repeated minute keeps its last bar.
    sigma uses `math.fsum`. The formulas are used as written: `abs(C / O - 1)` and `(h + l + c) / 3 * v`. Decision
    minutes are the multiples of `decision_every` from open + margin to close - margin. `cov` is returned
    unrounded; the tag writes it with `%.4f`.
15. **Chunks.** The 600-character limit applies to `x` alone, packed greedily.
16. **Carriers.** Each session gets an **even number of chunks**: an odd count gets one more, empty, chunk. There is
    one order per chunk, buy then sell. Every contract is therefore flat after every session, and no position is
    held at an expiry. Otherwise LEAN would liquidate at delisting with an order carrying its own, non-IMX tag.
    Orders go to the active contract after the roll. No cash is set: LEAN's default covers one contract.
17. **Fill-forward.** The subscription sets `fill_forward=False`, and any bar with `is_fill_forward` is also
    skipped.
18. **`warm`** counts the session records dated before the window start, of any code.
19. **The window's dates** are `im2x_preamble`'s arguments, checked only for order (warm-up start before window
    start, window start not after window end). They are not required to be one of the config's development windows,
    so the same code can build the confirmation kits later; the template's embedded guard still stops the
    confirmation window. The market's constants are read from `config/model_im2.yaml`.
20. **Unused by design.** The standard contract's tick feeds no rule in this check, so it is not embedded. The
    security cache is not read either: every price comes from the slice's bars.

## What I think is wrong or unclear in the brief

- **Tag length.** QuantConnect's order-properties page says a tag is "any string of up to 100 characters". A
  first-form tag here can run to about 750. The brief says every kit uses this route, so long tags presumably
  survive, but I cannot check that. If they are truncated, `x` is cut silently. The parser should check each
  session's `sig` against its parsed signals.
- **`K` is not comparable across implementations** because of the padding in case 16. Compare `x` joined over the
  chunks instead.
- **The store rule admits W and L sessions** (it excludes only H and E), while P-04 speaks of "complete sessions" of
  the scheduled calendar. This makes no practical difference: no weekend has bars in these session hours, and a late
  open is rarely 90 % complete. I followed the brief.
- **The brief is silent** on case 1 (whose bar triggers the roll), case 3 (today's date at a fallback roll) and
  case 8 (the scope of `switches`). If the first kit chose differently, those are where the two can differ.
- I found nothing in the brief that contradicts P-04 §3's market rules or its entry signal.
