---
name: feature-rules
description: The rules every feature, label and split obeys -- normalised features only, from bars closed at or before the alert; the bracket label of bootstrap 6.2; purged and embargoed splits; the coin twin as the test. Use when writing or reviewing any code that reads bars, computes a feature or a label, or splits data for a model.
---

# Feature, label and split rules (bootstrap 6.2; E-006)

A model fooled by the future is the most common way a backtest lies, and it never fails loudly. These rules are
checked by tests, not by care.

## 1. Time: what "closed at or before t" means here

- Stage 2's bars carry the bar's **open** time (`vendor/stage2/data/README.md`, `timestamp`: "Bar OPEN time"),
  US/Central. A 1-minute bar stamped 08:25 covers 08:25:00-08:25:59 and **closes at 08:26**.
- So at an alert time `t` (on a minute boundary) the last closed bar is the one stamped **`t - 1 minute`**. A feature at
  `t` reads bars with `timestamp <= t - 1 min` and nothing else. "The 08:25 bar's close" is known at 08:26, not 08:25.
- Entry is no earlier than `t + 5 min` (Stage 2 D-266): a market entry fills at the open of the bar stamped `t + 5`;
  a resting order is live from `t + 5` and can fill only on bars stamped `t + 5` or later.
- Calendars (BLS 08:30 releases `vendor/stage2/data/releases_bls_0830_*.csv`, FOMC days) may be used only as they were
  published in advance; their provenance files say when.
- **Never** read NQ from 2026-07-17 (the confirmation window, `vendor/stage2/config/windows.yaml`).

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

- **Entry:** market at the open of the bar stamped `t + 5`, or a resting order live from `t + 5` -- a stop fills when a
  bar trades at its price (gap-through fills at the bar's open, plus slippage); a **limit fills only on a trade
  through its level by at least one tick**, at the limit price, never better.
- **Stop** from the stop band (`vendor/stage2/results/stop_band.csv`; the registered rungs are 25 and 37.5 NQ points;
  under 45 ticks costs eat the trade, Stage 2 D-527); **targets** at each declared R.
- **Resolution** by 15:10 CT: win (target), loss (stop) or flatten (at 15:10, its actual P&L). No time stop.
- **Ties:** a bar that could hit both stop and target is read **stop first**; on a resting order's fill bar a stop
  touch counts and a target touch does not -- **for one trade's own outcome only.** In a comparison of a resting
  entry with its mirror or coin twin that rule is biased with a predictable sign, because price reaches the fill from
  the rule's side (Phase 0 audit `docs/audits/phase0/D_protocol.md` D-1, D-13): the family declares its fill-bar
  settlement for pairs (the **pair rule** -- a pair whose fill bar touches either trade's stop or target contributes
  zero lift, is counted and its share reported and capped) and books both sides symmetrically about the trigger.
- **Costs:** Stage 2's per-contract costs at the stop (`atlas_a3.fee_by_stop`; `vendor/stage2/config/fills.yaml`),
  the stop exit slipping a tick, a limit target none.
- **Gates before any outcome is read:** signals per session (supply), the unresolved share at every R (at most 5 %
  overall, Stage 2 D-212), realised risk matching intended (Stage 2 D-308).

Stage 2's walks (`vendor/stage2/data/atlas`) already hold the market-entry label for every 5-minute mark; a new walker
must reproduce them (or P-16's pinned trades hash) before it labels anything new.

## 4. Splits for any fitted model

- Walk-forward in **session blocks**: choose on the choice block (2020-01-02 to 2023-12-29), judge on the judged block
  (2024-01-02 to 2026-07-16), as the family declares; folds inside the choice block only.
- **Purge and embargo longer than the longest trade:** a label at `t` resolves by 15:10 CT the same session, and
  features may look back several sessions -- so purge every training sample whose label window overlaps a test fold
  and embargo at least one full session after each test fold (more if a feature's window is longer).
- **Hyperparameters fixed in the declaration, or searched inside the declared walk-forward only**, and every searched
  value is counted in the family's k. A search outside the declared folds is a new family.
- Fitted statistics (scalers, encoders, thresholds) are fitted in-fold and applied out of fold.

## 5. The test of direction

Lift over the **coin twin** on the same brackets -- the same entries with a fair coin choosing the side, so supply,
cost and schedule cancel and only direction is measured -- then valued by the value map
(`vendor/stage2/results/u_value_map.csv`). Rules read off a model afterwards (SHAP and the like) are exploratory and
need their own family.

## Checklist for a reviewer

- [ ] every feature reads `timestamp <= t - 1 min` only; a shift-invariance test exists and passes
- [ ] no normaliser, scaler, threshold or level uses data after `t` (or outside the training fold)
- [ ] entries at `t + 5` or later; limits need a trade-through; stop first on two-barrier bars; flatten at 15:10 CT
- [ ] splits purged and embargoed by at least a session; hyperparameters fixed or searched in-fold and counted
- [ ] no read of NQ from 2026-07-17; nothing chosen after an outcome without the exploratory label
