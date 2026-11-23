---
name: prereg-discipline
description: How a design search (or an RD reading) is declared in this repository (prereg/ files drafted on prereg/TEMPLATE_design_search.md, pinned by sha256 in a decision row), how a declared search is run and read under the journey objective (E-210), and the failure protocol for a check that fails. Use when writing a declaration, building or running a declared search, interpreting a result, or deciding whether something counts as exploratory.
---

# Declaration discipline

## Why it is enforced rather than encouraged

A design search is a search over configurations. If the hypothesis can be adjusted after the result, the search
always succeeds: given enough variants, something clears any threshold. The only defence is to write down what would
count as success **before** looking, and then not move it.

In this repository that is mechanical, not a matter of good intentions:

- A **search** is declared in `prereg/F-NN_<slug>.md` and **pinned by the sha256 of its LF text in a decision row**
  (E-001 (b), E-003). `tests/test_declarations_fixed.py` re-hashes every pinned file on every run, the fast tier
  included, so a byte changed after the pin fails the suite and the pre-commit hook. **Nothing declared is edited: a
  change is a new declaration** under a new row.
- The **scout**'s challenger brief (Q-150) and the **red-team** read a draft -- look-ahead, leakage into the held-out
  years, selection after the fact, peak-picking, seed reuse, unpaired comparisons, limits set after a result,
  miscounted tests -- without being told the expected answer, each finding labelled blocking or minor (E-207 (2));
  then the **prereg-gatekeeper** approves or refuses it and returns the pinning row. Only the lead appends it (the
  single-writer rule, E-005).
- **The multiplicity budget continues Stage 2's program U** (E-001 (a)): one k per **held-out test** (CHARTER 3.7),
  numbered in declaration order across both repositories, judged at **0.05 / (k (k + 1))** -- so the program spends at
  most 5 % however long it runs. F-01 (k = 10) was withdrawn with its k spent, F-02's k = 11 retired unspent, F-03 spent
  k = 12; the next is k = 13. **A search's k is assigned at its held-out row** (E-204): if another declaration pins
  between its held-out run and that row, the held-out run is repeated at the new level. The finalists are tested in a
  fixed sequence at one k; the confirmation spends none. Every design tried is counted in `results/variants.jsonl`.
- **Only a carried design takes a registration id**: a search is declared, not registered; the design it carries is
  then registered, audited and confirmed once on data never read.

Stage 2's harness gate (`propedge.backtest.harness`, which refuses an id not in Stage 2's `prereg/REGISTRY.md`) reads
Stage 2's registry, not this repository's; this repository's mechanical form check is `scripts/decl_lint.py` (Q-210), and the pin, the
challenger brief, the red team, the gatekeeper's reading and the template's test
(`tests/test_design_search_template.py`) are the gate here.

## Writing one

`/prereg <title>` copies **`prereg/TEMPLATE_design_search.md`** (E-210; the restart plan's Wave 2.1) to
`prereg/DRAFT_F-XX_<slug>.md`. `prereg/TEMPLATE_family.md` is superseded for new work and kept for the record. Fill
every section. The ones people get wrong:

**The years and the ledger, as dates, now.** Development is NQ 2020-01-02 to 2026-07-16 only. The **search years**
(2020-01-02 to 2023-12-29) are the only years the search, its lever ranges, volatility units, regime thresholds,
schedules, limits, budgets and weights may read; the **held-out years** (2024-01-02 to 2026-07-16, on
`results/q82_judged_sessions.csv`) are read once, by the held-out test (E-208). Fixed before anything runs and never
revisited -- extending one after a near miss turns an out-of-sample reading into an in-sample one. **The held-out read
ledger** carries every past read of the held-out years for the search's comparators and triggers; while it is not
empty the level is printed nominal. **The confirmation window is declared before any development read**: NQ from
2026-07-17 (`vendor/stage2/config/windows.yaml`), not on disk, never read until a carried design is registered, and a
purchase.

**Every lever classed fixed / searched / dropped, with its value or range and its source.** The operator is not a
quant: each lever is named, explained in a phrase and classed, from the lever table
(`docs/plans/LEVER_TABLE_topstep50k.md`, loaded by `extended/lever_space.py`). A range comes from contract arithmetic,
a verified rule or an RD map's search-year rows -- never from the held-out years. The survey size, the surrogate
method, the number of rounds and the batch size are fixed numbers, never extended after a look.

**Every input of CHARTER 3.9 written in the file before its pin, so before the survey.** The limits,
the bankroll budgets, the dimensions with their normalisers and caps, the weights, the composite **or** the fallback
(one, never both), the size that matters and the power target, the regimes and "most years", the finalist order and
plateau rules, the gate's quantile and the minimum complete held-out starts, the no-harm margin, the L values. A value
set after a result is a new declaration.

**Seeds, now, by role.** Every seed an integer in the file with one role, found nowhere else (in Stage 2 or here); the
held-out test's coin seeds disjoint from every search-year seed; keys of fixed length per draw kind. A seed chosen
after seeing a result is a variant.

**The pass line (CHARTER 3.8, in force from E-210).** A finalist passes, in its place in the fixed sequence, on the
**martingale-outcome reading** (each trade's outcome redrawn at its bracket's driftless first-exit odds against the
nearer barrier net of the stop-side exit cost -- the loss barrier min(l, c - x_stop), fractional, never rounded,
everything decided at the fill by L_fill, no "not taken" state, a trade sized to zero contracts ending the account
out of room (C-1) (the template's section 5) -- the same seed keying for the design
and every baseline), when (a) the point estimate governs each limit -- inside it passes, outside it fails,
never a second margin, the one-sided check reported beside (E-221, E-230, O-5); (b) its composite (or the pinned
fallback, P under the bankroll stop) is above **each** baseline's -- naive coin, P-14, P-15, P-16, each under the
design's convention -- by the calibrated paired coin-seed leg on the held-out years at the full level, the time leg's
conditions met; and (c) the floors hold: verified rules, conduct tier 1, CHARTER section 4, hand entry at least L
minutes, the zero-edge long-run gate, the +1 tick and 10 %-missed stresses, and the no-harm and as-traded floors read
on the real path. The verdict at 0 % payout denial, the placement off and the Focused Trader Program off; the level
printed nominal while the ledger is not empty, the history-level false-pass rate beside. **The level bounds coin luck
given the held-out history, not a favourable history.** The trades' lift over the coin twin, its value-map bar, R\* =
P-14 and Stage 2 D-621 (3) are on record and no longer decide (CHARTER 3.10).

Weakening the line -- a looser level, a dropped floor, a limit loosened, the fallback tried after the composite, a
judgement on the search years -- needs the operator (the objective changes only with them, DIRECTIVE Part 1); a
declaration may not do it on its own. Gates on supply, resolution and realised risk come before any outcome.

**And state what a fail means.** "The search closes, its k spent", not "we investigate further". If nothing happens on
a fail, the reading is not informative and is not worth running.

## Running one

- **The identity first, refusing.** The runner reproduces Stage 2's files before any outcome of it is believed
  (`identity/stage2_identity.py`; every new runner has its own; each baseline's runner reproduces its registered trade
  times and brackets path for path).
- **In the declared order** (the template's section 14): the reads of the draft; the pin of the whole renamed file by
  one hash (section 7 never alone; the limits, budgets, weights and size that matters the lead's from H4, E-221); the
  calibration and the power gate on the inputs that file fixed, their outputs pinned in E-115's form; the go row; the
  survey and the rounds on the search years only; the finalists' row; the held-out row; the held-out test once, its
  `heldout_*` reads only after those two rows and once per market (Q-158, built at E-220, the reader's guard; no
  design search pins before it merges).
- **From a clean checkout of a named commit** (`python scripts/run_clean.py`: a detached checkout under
  `%LOCALAPPDATA%\stage2-extended-runs\`, the data junctions linked, `git status` empty before the command, the log
  beside it), **one heavy run at a time on the machine under `run.lock`** (skill `run-lock`), watched to its end.
- **Written with its manifest** through `extended.results.write_result` (skill `result-provenance`) with `prereg_id`
  the declaration's id, the design count, every seed and parameter; every design tried in `results/variants.jsonl`; no
  held-out result where a later search can read it.
- **Reported** with the program's running count, every measure of `docs/MEASURES.md` as a distribution over start days
  and coin seeds, the frontier and a menu under the limits, each baseline beside, the as-walked result and the
  path-structure edge beside, never credited.

**Then record the outcome** -- pass or fail -- in a new decision row, proposed by whoever read it as one finished
line `| E-NNN | ... |` and numbered and committed by the lead. **Not in the declaration**: it is pinned, and its hash
test would fail. A search with no recorded outcome is an unreported result, and the closing checklist will not pass
while one exists.

## The failure protocol

When a declared check fails, do this and nothing else:

1. **Keep the verdict on record.** It is a result, not a mistake to be erased.
2. **Terminal states** -- are the end states what the rules imply?
3. **Stage decomposition** -- which stage holds the discrepancy?
4. **The component in isolation** -- the smallest piece that reproduces it.
5. **Replication with seeds fixed *before* running.**

**Never rerun until it passes.** "Try another seed and see" converts a result into a search, and a search that stops
when it succeeds has no error rate at all. At most two corrective cycles per item, then `NEEDS_OPERATOR` on the board
(DIRECTIVE Part 5, step 3).

Stage one applied this protocol to its own failed check -- T4 check 2 failed and was diagnosed as a false alarm by a
pooled replication (propsim D-40). The verdict stayed on the record with the diagnosis. That is what made the account
credible: a repository that reports no failures is not a repository that had none.

## Exploratory work

Anything chosen **after** seeing results is exploratory. Label it, report it separately, set `exploratory=True` in its
result manifest, and record it in its own decision row (never in the pinned declaration).

This is not a demotion. Stage one's most interesting finding -- that payout policy is first-order (propsim D-45) -- was
exploratory, chosen after the declared results (propsim D-44). Labelling it is what let the declared set stay
trustworthy. What is forbidden is presenting a post-hoc choice as though it had been declared. The **auditor** looks for
exactly this: a lever or input in a result that appears nowhere in the declaration, a measure introduced after the
fact, a subset or exclusion with no declared justification, or `exploratory=False` on a run whose parameters came from
an earlier result.

## Quick reference

| situation | what to do |
|---|---|
| New search | `/prereg <title>`: draft on the design-search template, challenger brief, red-team, gatekeeper; the lead pins it by sha256 in its row |
| Gatekeeper refuses | Normal for a first draft. Fill the gaps; do not argue the rule down |
| A declared file needs a change | It cannot change. A new declaration, citing the old, under a new row |
| Check fails | Record it, run the failure protocol, do **not** rerun |
| Idea arrived after seeing a result | Exploratory: label it, report it apart, `exploratory=True`, its own row |
| Want to read the held-out years again | You may not: one held-out test per market (CHARTER 3.6 (c)); a later reading there is a description only |
| A design is carried | It takes a registration id, its playbook, the auditor, one confirmation against a criterion declared at registration (a purchase) |
