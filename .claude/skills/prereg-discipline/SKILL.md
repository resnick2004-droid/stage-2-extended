---
name: prereg-discipline
description: How a family is declared in this repository (prereg/F-xx files pinned by sha256 in a decision row), how a declared family is run and read, and the failure protocol for a check that fails. Use when writing a declaration, building or running a declared family, interpreting a result, or deciding whether something counts as exploratory.
---

# Declaration discipline

## Why it is enforced rather than encouraged

A screen or a campaign is a search over configurations. If the hypothesis can be adjusted after the result, the search
always succeeds: given enough variants, something clears any threshold. The only defence is to write down what would
count as success **before** looking, and then not move it.

In this repository that is mechanical, not a matter of good intentions:

- A **family** is declared in `prereg/F-NN_<slug>.md` and **pinned by the sha256 of its LF text in a decision row**
  (E-001 (b), E-003). `tests/test_declarations_fixed.py` re-hashes every pinned file on every run, the fast tier
  included, so a byte changed after the pin fails the suite and the pre-commit hook. **Nothing declared is edited: a
  change is a new family** under a new row.
- The **red-team** agent reviews a draft for look-ahead, leakage, selection after the fact, multiple-testing errors and
  unlabelled choices, without being told the expected answer; then the **prereg-gatekeeper** approves or refuses it
  and returns the pinning row. Only the lead appends it (the single-writer rule, E-005).
- **The multiplicity budget continues Stage 2's program U** (E-001 (a)): families are numbered in declaration order
  across both repositories, this repository's first is k = 10 (F-01), and family k is judged one-sided at
  **0.05 / (k (k + 1))** -- so the program spends at most 5 % however long it runs. One cell per family reaches
  judgement. Every cell run is counted under its family's row.
- **Only a carried candidate takes a registration id** (Stage 2 D-621 (9)'s house form): a family is declared, not
  registered; the design it carries is then registered, audited and confirmed once on data never read.

Stage 2's harness gate (`propedge.backtest.harness`, which refuses an id not in Stage 2's `prereg/REGISTRY.md`) reads
Stage 2's registry, not this repository's, and there is no `validate_prereg` for F-files: the pin, the red team and
the gatekeeper's reading are the gate here.

## Writing one

`/prereg <title>` drafts `prereg/F-XX_<slug>.md` from `vendor/stage2/prereg/TEMPLATE.md` and
`vendor/stage2/prereg/FAMILY_TEMPLATE.md`, adapted; `prereg/F-01_resting_order_level_atlas.md` is the house example.
Fill every section. The ones people get wrong:

**The data and the windows, as dates, now.** Development is NQ 2020-01-02 to 2026-07-16 only. The choice block and
the judged block are dates (the charter's: chosen on the starts of 2020-2023, judged on the starts from the first
session of 2024), fixed before anything runs and never revisited -- extending one after a near miss, or sliding it to a
friendlier regime, turns an out-of-sample reading into an in-sample one. **The confirmation window is declared before
any development read**: NQ from 2026-07-17 (`vendor/stage2/config/windows.yaml`), not on disk, never read until a
carried candidate is registered, and a purchase.

**Every parameter classed fixed / searched / dropped, with its value.** The operator is not a quant: each parameter
is named, explained in a phrase and classed. A parameter left "to be optimised" is not a detail to fill in later; it is
a variant, and a declaration containing one is declaring a search. If a parameter genuinely must be chosen from data,
choose it on the choice block by a rule the file fixes -- that is a rule, and it can be declared. No fitted values:
grids are contract arithmetic and verified rule values (Stage 2 D-621 (4)(d)).

**The cells counted.** `k_cells` as a product and a number; the program family number k and its level written out
(k = 10: 0.05 / 110).

**Seeds, now.** Every bootstrap, coin twin and campaign seed an integer in the file; a campaign seed one never used
before (in Stage 2 or here). A seed chosen after seeing a result is a variant.

**The selection rule (the operator, E-008, E-014, E-015).** A design is **judged on its trades first**: the lift over
the coin twin on the same brackets, on the judged block, one-sided at the family's level 0.05/(k(k+1)) by **the
calibrated statistic** (TASK_QUEUE Q-16), its value-map price at that bound at least the family's declared bar; the
long-run gate (growth on the required bankroll at the bound, Stage 2 D-145), every offered R resolving, verified rules
and conduct tier 1 as floors. **The user scorecard is beside, never the pass line**: P and the guarded measures
against **R\* = P-14**, the frontier, E-007 (e)'s readings and CHARTER section 2's journey scorecard, each measure a
distribution over start days, the operator's limits as menu flags only; the verdict at 0 % denial with the placement
off, the rest beside. *For the record only -- Stage 2 D-621 (3), which no longer decides (its line (i) does not
deliver its level, E-007):* a design CARRIED against **R\* = P-14** at the family's level -- the paired P difference's moving-block interval (63-session blocks, seed
20261700, 2,000 draws) excluding zero; no guarded measure worse by more than five points on a share or ten per cent on
dollars, sessions and ratios; **the long-run gate (growth on the required bankroll at the bound, Stage 2 D-145) as a
floor**, above zero and above P-06's row at a fresh campaign seed, every R resolving, every rule verified; a coin
design beating R\* under at least 40 of 50 coin sequences; not worse in more than one of the seven start years. Stage
one's e >= 0.10 with bound >= 0.05 (propsim D-47) is reported beside, never a line. Kill lines on supply, resolution
and realised risk come before any outcome.

Weakening the rule -- the point arm, a looser level, a dropped tolerance, the floor left out -- needs the operator (the
objective changes only with them, DIRECTIVE Part 1); a declaration may not do it on its own.

**And state what a fail means.** "The family closes", not "we investigate further". If nothing happens on a fail, the
reading is not informative and is not worth running.

## Running one

- **The identity first, refusing.** The runner reproduces Stage 2's files before any outcome of it is believed
  (`identity/stage2_identity.py`; every new runner has its own). Until U1's start rows are reproduced (TASK_QUEUE Q-05),
  no result of this repository is believed.
- **From a clean checkout of a named commit** (`python scripts/run_clean.py`: a detached checkout under
  `%LOCALAPPDATA%\stage2-extended-runs\`, the data junctions linked, `git status` empty before the command, the log
  beside it), **one heavy run at a time on the machine under `run.lock`** (skill `run-lock`), watched to its end.
- **Written with its manifest** through `extended.results.write_result` (skill `result-provenance`) with `prereg_id` the
  F-id, the cell count, every seed and parameter.
- **Reported** with the program's running family count and the family's cells, P with its guarded measures, the
  frontier and the gate floor beside.

**Then record the outcome** -- pass or fail -- in a new decision row, proposed by whoever read it as one finished
line `| E-NNN | ... |` and numbered and committed by the lead. **Not in the F-file**: the declaration is pinned, and its
hash test would fail. A family with no recorded outcome is an unreported result, and the closing checklist will not
pass while one exists.

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
result manifest, and record it in its own decision row (never in the pinned F-file).

This is not a demotion. Stage one's most interesting finding -- that payout policy is first-order (propsim D-45) -- was
exploratory, chosen after the declared results (propsim D-44). Labelling it is what let the declared set stay
trustworthy. What is forbidden is presenting a post-hoc choice as though it had been declared. The **auditor** looks for
exactly this: a parameter in a result that appears nowhere in the declaration, a measure introduced after the fact, a
subset or exclusion with no declared justification, or `exploratory=False` on a run whose parameters came from an
earlier result.

## Quick reference

| situation | what to do |
|---|---|
| New family | `/prereg <title>`: draft, red-team, gatekeeper; the lead pins it by sha256 in its row |
| Gatekeeper refuses | Normal for a first draft. Fill the gaps; do not argue the rule down |
| A declared file needs a change | It cannot change. A new family, citing the old, under a new row |
| Check fails | Record it, run the failure protocol, do **not** rerun |
| Idea arrived after seeing a result | Exploratory: label it, report it apart, `exploratory=True`, its own row |
| Want to rerun a judged family | You may not. New question, new family citing the old |
| A design is carried | It takes a registration id, its registered test, the auditor, one confirmation (a purchase) |
