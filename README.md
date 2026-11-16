# Stage 2 Extended

Execution models for a prop-firm user's journey -- a person who starts on any day, buys evaluations, passes, trades
funded accounts and collects payouts -- judged by the share of start days ahead over the first three months (P).
Built on Stage 2's engine, rules and results, vendored read-only at `vendor/stage2/` (commit f1b42e2).

- `CHARTER.md` -- the question, the objective, the row to beat, the exit criterion
- `CLAUDE.md` -- the operating rules
- `DECISIONS.md` -- the decision log (E-xxx)
- `DIRECTIVE.md` -- the lead orchestrator's standing orders (the bootstrap's Parts 1, 3, 5, 6, verbatim)
- `TASK_QUEUE.md` -- the ranked queue (owner worktree, state, dependencies, weight, retries)
- `STATUS.md` -- the live board (identities, run lock, worktrees, NEEDS_OPERATOR)
- `PROGRESS.md` -- the log
- `docs/OPERATOR_SETUP.md` -- the only channel for the operator's manual tasks
- `prereg/` -- family declarations, fixed by sha256 before they are built
- `identity/stage2_identity.py` -- the vendored engine reproduces P-14's and P-16's registered paths
- `scripts/vendor_stage2.py` -- the snapshot and the licensed data (never committed)

Setup on a fresh clone: `python scripts/vendor_stage2.py --source "<path to Stage 2>" --data` (copies and checks the
bars and atlas), then `python -m pytest -q`.
