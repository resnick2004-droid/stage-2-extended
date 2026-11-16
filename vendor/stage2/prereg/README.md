# prereg/ — pre-registrations

**Every test in this stage is pre-registered before it is run.** The hypothesis, the data
period, the fixed rules, the metrics, the pass/fail criteria and the seed are written down
first, so that the result can only confirm or refute — not be reshaped to fit.

This is enforced, not encouraged: `propedge/backtest/harness.py` raises
`UnregisteredRunError` unless its `prereg_id` names a runnable row in `REGISTRY.md`. There is
no flag to skip it.

## Files

| file | purpose |
|---|---|
| [`TEMPLATE.md`](TEMPLATE.md) | the form. Every section must be filled |
| [`REGISTRY.md`](REGISTRY.md) | `id \| date \| title \| status \| outcome` — the index the harness reads |
| `P-01_*.md`, `P-02_*.md`, … | the pre-registrations themselves |

## Workflow

1. `/prereg <title>` copies the template to `P-XX_<slug>.md`.
2. Fill **every** section. A section you cannot fill is a decision you have not made yet, and
   making it after seeing results is the failure this whole directory exists to prevent.
3. The **prereg-gatekeeper** agent reviews it. It refuses to register one missing the data
   period, the fixed rules, the metrics, the pass/fail criteria or the seed. It then assigns
   the id and adds the row to `REGISTRY.md`.
4. Run, using the assigned id.
5. **Record the outcome** — pass or fail — in the pre-registration's Outcome section and in
   `REGISTRY.md`.

## The confirmation window is counted (D-107)

Every registered confirmation test on a market's held-out window is one more look at the same
data, and enough looks will pass something by luck. The count per market is kept here, in this
registry, reported with every verdict, and **capped at three per market**. A fourth needs an
operator decision recorded in `DECISIONS.md` and is reported with the family count. Withdrawn
drafts that were never registered do not count. `confirmation_tests_on_this_market` is a
machine-checked field the gatekeeper refuses without.

## Two rules that are easy to bend and must not be

**A failed check is kept and diagnosed, not rerun.** The protocol (propsim D-40, applied by
stage one to its own failed check):

1. keep the verdict on record;
2. terminal-state audit;
3. stage decomposition;
4. component test in isolation;
5. replication with seeds fixed **before** running.

Never rerun until it passes. "Run it again with a different seed and see" converts a result
into a search.

**Anything chosen after seeing results is exploratory.** Label it, report it separately, and
set `exploratory=True` in its result manifest. This is not a demotion — stage one's most
interesting finding (the payout buffer, propsim D-45) was exploratory, and labelling it is
precisely what let the pre-registered set stay trustworthy. What is forbidden is presenting a
post-hoc choice as though it had been registered.
