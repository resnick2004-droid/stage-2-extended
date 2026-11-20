---
name: feature-rules
description: The rules every feature, trigger, label and split obeys -- normalised features only, from bars closed at or before the alert; the bracket label of bootstrap 6.2; purged and embargoed splits inside the search years; the zero-edge convention and the journey as the test (E-210). Use when writing or reviewing any code that reads bars, computes a feature, a trigger or a label, or splits data for a model or the surrogate.
---

# Feature, label and split rules (bootstrap 6.2; E-006; E-210)

A model fooled by the future is the most common way a backtest lies, and it never fails loudly. These rules are
checked by tests, not by care. Under the journey objective (E-210) a feature no longer has to predict direction: it
sets **when** a component trades (timing, resolution speed, clustering) and feeds the lever space's volatility units.
The rules bind every source that reads bars all the same -- a trigger that peeks at the future changes a design's
supply and timing as surely as a side model's accuracy.

## 1. Time: what "closed at or before t" means here

- Stage 2's bar store (`bars.parquet`, `vendor/stage2/data/README.md`) carries **`ts`, the bar's START**, in epoch
  seconds **UTC** (the README's generic input schema calls it `timestamp`, "Bar OPEN time"); session times are read in
  US/Central after converting (DST-aware). A 1-minute bar stamped 08:25 covers 08:25:00-08:25:59 and **closes at
  08:26**.
- So at an alert time `t` (on a minute boundary) the last closed bar is the one stamped **`t - 1 minute`**. A feature at
  `t` reads bars with `timestamp <= t - 1 min` and nothing else. "The 08:25 bar's close" is known at 08:26, not 08:25.
- Entry is no earlier than `t + L min` (Stage 2 D-266; L = 5 the reference, 3 and 2 declared and counted variants,
  E-202 (2)(c)): a market entry fills at the open of the bar stamped `t + L`; a resting order is live from `t + L` and
  can fill only on bars stamped `t + L` or later.
- Calendars (BLS 08:30 releases `vendor/stage2/data/releases_bls_0830_*.csv`, FOMC days) may be used only as they were
  published in advance; their provenance files say when.
- **Never** read NQ from 2026-07-17 (the confirmation window, `vendor/stage2/config/windows.yaml`).
- **Never** let anything a search chooses or fits -- a normaliser's window, a threshold, a level list, a cap, a regime
  cut -- read the held-out years (2024-01-02 to 2026-07-16, E-208). A causal look-back from a held-out start into the
  search years is allowed (CHARTER 3.6 (d)); the reverse is never.

## 2. Features

- **Normalised, never raw price levels.** Differences and ranges divided by a rolling ATR; spreads by the session's
  own spread; volume by a time-of-day median. A raw price may enter only inside a difference or a ratio.
- **Every normaliser is computed from the past only** -- rolling or expanding windows ending at `t - 1 min`, or, for a
  fitted scaler, fitted inside the training fold only. A time-of-day median, a z-score or a quantile computed over
  the whole sample is look-ahead.
- **Levels** (prior day high/low, overnight range, opening range, VWAP bands, swing points) are frozen when their
  window's last bar closes and are used only after that.
- **The shift-invariance test (required for every feature):** replace every bar stamped `>= t` with arbitrary values
  (a fixed-seed random walk, or a constant) and assert every feature at `t` is unchanged; run it over many `t` across
  sessions, including the session's first minutes and around a roll and a DST change. Also assert a feature is not
  all-NaN and not constant.
- Each feature has one line of documentation: its formula, its window, its normaliser, the bars it reads.

## 3. The label (the bracket outcome; bootstrap 6.2, handoff 4.2)

For each candidate alert `t`:

- **Entry:** market at the open of the bar stamped `t + L`, or a resting order live from `t + L` -- a stop fills when a
  bar trades at its price (gap-through fills at the bar's open, plus slippage); a **limit fills only on a trade
  through its level by at least one tick**, at the limit price, never better.
- **Stop** from the stop band (`vendor/stage2/results/stop_band.csv`, which also holds the cost-drag floor of 45 ticks
  -- Stage 2 D-271 (3), not D-527; the registered designs trade 12.5 and 25 points (P-14) and 25 and 37.5 points (the
  coins P-15, P-16)); **targets** at each declared R.
- **Resolution** by 15:10 CT: win (target), loss (stop) or flatten (at 15:10, its actual P&L). No time stop.
- **Ties:** a bar that could hit both stop and target is read **stop first**; on a resting order's fill bar a stop
  touch counts and a target touch does not -- **for one trade's own outcome only.** Kept as a fill-realism rule: in a
  comparison of a resting entry with its mirror (or its reflection) that rule is biased with a predictable sign: price
  reaches the fill from the side of the trade's target, so stop first on the fill bar throws away the real trade's
  target touches and stops out the reflected trade, whose stop now lies on the pre-fill side -- it favours the real
  resting side by construction (Phase 0 audit `docs/audits/phase0/D_protocol.md` D-1, D-13). So **wherever a reading
  compares a resting entry with its reflection or mirror** -- the **no-harm floor** (the real resting side against the
  reflected one, search years) and the **as-traded floor** (held-out years), both deciding and read on the real path
  (CHARTER 3.8), and the path-structure gap -- the **pair rule** settles the fill bar: a pair whose fill bar touches
  either trade's stop or target **contributes zero lift** -- both legs are booked at the
  as-walked leg's settled outcome for that pair, each with its own (equal) costs, so the pair's
  difference is exactly zero by construction -- is counted, and its share reported and capped; both sides are booked
  symmetrically about the trigger. The as-walked and as-traded readings use this label; the deciding reading redraws
  it (section 5).
- **Costs:** Stage 2's per-contract costs at the stop (`atlas_a3.fee_by_stop`; `vendor/stage2/config/fills.yaml`),
  the stop exit at `stop_slippage_ticks`, a limit target at `target_slippage_ticks` (the profile in use).
- **Gates before any outcome is read:** signals per session (supply), the unresolved share at every R (at most 5 %
  overall, Stage 2 D-212), realised risk matching intended (Stage 2 D-308).

Stage 2's walks (`vendor/stage2/data/atlas`) already hold the market-entry label for every 5-minute mark; a new walker
must reproduce them (or P-16's pinned trades hash) before it labels anything new.

## 4. Splits for any fitted model

- Walk-forward in **session blocks** inside the **search years** (2020-01-02 to 2023-12-29): every fit, the surrogate
  of the lever map included, chooses there, with its folds there only; the **held-out years** (2024-01-02 to
  2026-07-16) are read once, by the held-out test, never by a fit, a fold or a tuning step (E-208; CHARTER 3.6).
- **Purge and embargo longer than the longest trade:** a label at `t` resolves by 15:10 CT the same session, and
  features may look back several sessions -- so purge every training sample whose label window overlaps a test fold
  and embargo at least one full session after each test fold (more if a feature's window is longer).
- **Hyperparameters fixed in the declaration, or searched inside the declared walk-forward only**, and every searched
  value is counted in the variants ledger. A search outside the declared folds is a new declaration.
- Fitted statistics (scalers, encoders, thresholds) are fitted in-fold and applied out of fold.

## 5. The test: zero edge and the journey (CHARTER 3.2, 3.8; E-210)

A trigger or a feature is judged by what it adds to a design's journey under zero edge, never by a lift over the coin
twin (CHARTER 3.10). Its fills come from the real order; the path after each fill is reflected with probability one
half (direction removed); and the deciding reading is the **martingale-outcome reading** -- each trade's outcome
redrawn at its bracket's driftless first-exit odds against the nearer barrier net of the stop-side exit cost -- the
loss barrier L = min(l, c - x_stop) -- c the room to the nearer of the floor and the daily loss limit after the entry
cost, x_stop the stop-side exit cost (commission plus `stop_slippage_ticks`) -- fractional, never rounded (E-237),
p = L / (L + g), L_fill = min(l, c - max(x_stop, x_flat)), the fill's decision (x_flat the flatten-side exit
cost): L_fill <= 0 where the floor binds fails the account at the fill, where the daily loss limit binds
the day stops; a trade sized to zero contracts at a positive room ends the account out of room, failed and
counted apart (C-1, Stage 2 D-318, D-335) (no "not taken" state) (the design-search template's section 5;
`adapter.BinaryDraw` is its cost-free case) -- over seeds paired with every baseline's. What a feature can still
change, and what the search rewards, is supply, timing, resolution speed for a given shape, clustering and how
differently a component is timed from the others. The as-walked result's gap from the martingale-outcome result is the
design's path-structure edge, reported beside, never credited. Rules read off a model afterwards (SHAP and the like)
are exploratory and need their own declaration.

## Checklist for a reviewer

- [ ] every feature and trigger reads `timestamp <= t - 1 min` only; a shift-invariance test exists and passes
- [ ] no normaliser, scaler, threshold or level uses data after `t` (or outside the training fold), and none reads the
      held-out years
- [ ] entries at `t + L` or later (L declared: 5, or a counted 3 or 2); limits need a trade-through; stop first on
  two-barrier bars; flatten at 15:10 CT
- [ ] splits inside the search years, purged and embargoed by at least a session; hyperparameters fixed or searched
      in-fold and counted
- [ ] no read of NQ from 2026-07-17; nothing chosen after an outcome without the exploratory label
