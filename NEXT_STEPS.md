# Next steps

Ordered so that work which can cancel later work comes first. Something needed that is not here is added under a
decision row before it is done.

## Done (the handoff's section 7)

- [x] **1. Charter** -- `CHARTER.md` (E-001).
- [x] **2. Stage 2 vendored read-only with its identity** -- `vendor/stage2/`, `identity/stage2_identity.py`,
  `tests/` (E-002); the identity holding at all 500 registered paths from a clean clone (E-004).
- [x] **3. First family declared before it is built** -- `prereg/F-01_resting_order_level_atlas.md` (E-003).

## Open

1. **F-01's build** (in a worktree, tests first), in the order the family file's section 7 fixes: the walker's
   identity against P-16's pinned trades hash; no-look-ahead and synthetic fill tests; the mirror's zero on random
   bars. The build's readings recorded in a decision row before any run.
2. **F-01 stage A** (supply, cutoff, K1-K4, planning power) -- counts and barrier columns only; then stage B, C and
   (only if C holds) D, each read in its own row from the result file.
3. **The house tools this repository still lacks** (carry from Stage 2 as needed, each its own row): a results writer
   in this repository's package (or the vendored one's, imported), a trace check, a clean-run helper and job watcher,
   the auditor, prereg-gatekeeper and results-tracer agents adapted to this tree.
4. **Next family, declared only after F-01 closes or carries:** the multi-feature model (handoff 3.3: one pre-
   registered classifier on 30-50 normalised OHLCV features, purged walk-forward, judged out of fold against the coin
   on the same brackets and valued by the value map).
5. **Later sides (handoff 3.3), each a family:** other firms' contracts (end-of-day drawdown, no consistency rule;
   rules verified on each firm's own pages); payout policy for a user's first months.

## Closing checklist (CHARTER section 5)

- [ ] every declaration and outcome on record; the decision log complete
- [ ] every number in a document traced to a result file with a manifest
- [ ] `vendor/stage2/` unedited (`tests/test_vendor_integrity.py`) and its identity holding
- [ ] (A) a carried design, registered, audited and confirmed on unread data -- or (B) the documented negative result
