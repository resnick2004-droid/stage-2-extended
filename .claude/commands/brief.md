---
description: Brief the operator in plain English -- where the work stands, the designs inside the limits, the trade-offs, each baseline, what is theirs to decide -- built only on traced results
argument-hint: [optional focus, e.g. a search id or "baselines"]
allowed-tools: Read, Bash, PowerShell, Glob, Grep
---

Brief the operator: **$ARGUMENTS** (or the whole picture, if no focus is given).

The operator is not a quant (CLAUDE.md). Write in **plain English**: short sentences, no symbols a reader must decode,
every term explained the first time it is used (a "baseline" is a way of trading already known, which a new design
must beat; "P" is the share of users ahead in cash at months 1-3, not a p-value; a "limit" is the operator's own line
on what a user can bear). Every parameter named is explained in a phrase and classed fixed / searched / dropped.

## The one rule: only traced results

**Every number in the brief comes from a result file with a manifest, read now, and is cited beside it** (the file
and the column or row). No number from memory, from a document, from a hand-back, from a decision row's prose, or from
an earlier brief.

1. List the result files the brief will use (`python scripts/status.py`, or `extended.results.list_results`), and
   verify each one's manifest (`extended.results.verify_result`). A file whose manifest does not verify, or whose
   `git_commit` is `-dirty` or `unknown`, is not used; say so.
2. Read each number from its file with a small scratch script in the scratchpad (never `python -c` with backticks),
   and print the file, the column and the value together. Run `python scripts/trace_check.py` when it exists; a number
   it cannot trace is left out of the brief, and the brief says one was left out.
3. A result with `exploratory=True` in its manifest is said to be exploratory where it appears, and kept apart from
   the declared readings.
4. **No held-out figure before its verdict row.** A held-out test's numbers appear only after the lead's verdict row
   records them; until then the brief says only that the test is pending. A sealed file (CHARTER 3.6 (e)) is never
   opened.
5. If nothing traced exists yet for a part, say "no result yet" for that part. Never fill a gap with an estimate.

## What the brief says, in this order (keep it under a page)

1. **Where the work stands** -- in two or three sentences: the wave of the restart plan, the search under way and its
   round, what has finished since the last brief (from `PROGRESS.md`'s dates; facts, not numbers).
2. **The designs inside the limits** -- the menu: each design that stays inside every operator limit, with the
   measures that matter most to a user (the bankroll needed, the time to a first payout, P, the chance of running out
   before the first payout, the monthly income after), each a range over start days, each traced.
3. **The trade-offs** -- what each step on one measure costs on another (the frontier), in the operator's own terms
   ("a faster first payout costs this much more bankroll"), traced.
4. **Against each baseline** -- the naive coin and P-14, P-15, P-16, under the same rules, on the same years; whether a
   design is ahead on the composite or the fallback the operator approved, at the level the test uses, and that the
   level bounds coin luck on those years, not a lucky stretch of history (CHARTER 3.8 (b)).
5. **What the data cannot show** -- the held-out years' size, the test's power from its power gate, that the level is
   nominal while the held-out read ledger is not empty, that the money comes from the firm's rules (a funded loss
   costs only fees), not from predicting the market, and what is not modelled (the user's time, taxes).
6. **What is the operator's** -- the open items (O-1, O-3, O-4, O-5, the data question, any NEEDS_OPERATOR on the
   board), each in one sentence with its consequence; any purchase stated with its cost, **never authorised here**.
   Until O-4 is ruled, no playbook goes to a user: say so if a finalist exists.
7. **The next round** -- the next three to five items in the queue, one line each.

## Limits

Read-only: this command writes nothing (only the lead edits `STATUS.md`, `TASK_QUEUE.md`, `PROGRESS.md`), runs nothing
heavy, reads no bar and no NQ from 2026-07-17. It is a report, not a recommendation to trade: no playbook, no side, no
size is advised to a user from it.
