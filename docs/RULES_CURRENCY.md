# Rules currency -- firm rules verified or re-verified in this repository

The human-readable table behind [`config/rules_extended.yaml`](../config/rules_extended.yaml): one row per entry there,
keyed the same, written together with it by the **rules-verifier** agent (`/verify-rule <rule>`) and never apart.
Stage 2's verified ledger -- `vendor/stage2/RULES_LEDGER.md` and `vendor/stage2/config/rules.yaml`, read on official
pages up to 2026-11-14 -- is vendored read-only (E-002) and is the source of every rule this repository loads until a
row here, under its decision row, says otherwise (CLAUDE.md, "Firm rules").

**What may be used.** A rule is usable only if it is `verified` in Stage 2's ledger, or `verified` here with its
decision row in `DECISIONS.md`. A `changed` row is a verified reading that differs from Stage 2's value: the vendored
engine still carries the old one, and anything resting on the rule is flagged until the lead's row decides. An
`unverified` row is never used.

**Sources.** Official pages only: Topstep's `help.topstep.com` and `topstep.com`; another firm, its own official pages,
whose domains are listed in the yaml's `meta.official_domains` before the first read. Never a third-party guide,
review site, forum, video or cached copy. The verbatim quote is in the yaml's `quote`; agreement with Stage 2's reading
is not evidence about today.

| key | firm | value | status | article id | url | date read | verified by | Stage 2 key | Stage 2 value | row |
|---|---|---|---|---|---|---|---|---|---|---|
| `tou_s8_relative_position_size` | topstep | market-standard risk management is not met where a trader opens substantially larger position sizes, or a smaller or larger number of positions, compared to their other trades (no consequence attached to the sentence itself; Topstep may class a practice as Prohibited Conduct at its discretion; the comparison base is unstated) | verified | terms-of-use s.8 | https://www.topstep.com/terms-of-use | 2026-11-15 | rules-verifier (Q-19, wt-firms) | -- (new) | -- | proposed |
| `tou_s8_relative_position_size_threshold` | topstep | unstated (no number, ratio or example on any page read; not a permission) | verified | terms-of-use s.8; 10406542; 13620045 | https://www.topstep.com/terms-of-use | 2026-11-15 | rules-verifier (Q-19, wt-firms) | -- (new) | -- | proposed |
| `prohibited_strategy_auto_breakeven_sim_fills` | topstep | prohibited, as an example of exploiting the simulator: "Using tight brackets or auto-breakeven to take advantage of favorable SIM fills"; neither term is defined; the page calls the listed behaviours "intentional and systematic" (usually hundreds or thousands of trades per day lasting seconds) | verified | 10305426 | https://help.topstep.com/en/articles/10305426 | 2026-11-15 | rules-verifier (Q-19, wt-firms) | `prohibited_trading_strategies` | true | proposed |
| `coordinated_trading_prohibited` | topstep | prohibited: "performing trades in concert with others (including unconnected accounts or third parties) to pool risk, hedge aggregate positions, or trade the same or opposite strategy simultaneously" (no item covers one trader's own accounts except opposite positions) | verified | 10296582 | https://help.topstep.com/en/articles/10296582 | 2026-11-15 | rules-verifier (Q-19, wt-firms) | `prohibited_conduct` | true | proposed |
| `tou_s27_same_trades_in_concert` | topstep | prohibited: in concert with others, including between unconnected accounts and third parties, the same trading strategy ("the same trades in the same time increments"), the opposite strategy, or other pooling or hedging of risk; "connected" / "unconnected accounts" undefined | verified | terms-of-use s.27 | https://www.topstep.com/terms-of-use | 2026-11-15 | rules-verifier (Q-19, wt-firms) | -- (new; quoted in Stage 2's `cross_account_opposite_positions` note) | -- | proposed |
| `multi_account_same_strategy` | topstep | permitted (same markets across one's own accounts, and Topstep's own Trade Copier on Combines and XFAs; "coordinated trading with others" and opposite positions prohibited) | verified | 8284215 (with 13747047, 14434175) | https://help.topstep.com/en/articles/8284215 | 2026-11-15 | rules-verifier (Q-19, wt-firms) | `multi_account_same_strategy` | permitted | proposed |
