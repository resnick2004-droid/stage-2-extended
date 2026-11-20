# TEMPLATE: the held-out test's declaration -- copy it, never pin it

**What this file is.** The house form for the one declaration that reads NQ's held-out years: the joint
fixed-sequence test of every firm's finalists (CHARTER 3.6 (c), 3.7; E-221, O-1; E-238), the red team's full read of
text v2, M-1. It is not a declaration: it names no search, holds no seed, no k and no figure, and its name matches
neither the reader's grammar (`F-` or `RD-` and a number) nor any test's declaration glob
(`tests/test_design_search_template.py` holds that). Every design search is drafted on
`prereg/TEMPLATE_design_search.md` and carries no `Judged-block reads:` line; this declaration carries it.

**Declaration kind: held-out test.** A declaration drafted on this template keeps this line.

**To use it:** copy it to `prereg/DRAFT_F-XX_heldout_test_NQ.md` when every firm's search has a finalists' row or a
closing row (section 3), replace every `<...>`, and send it to the red team and the gatekeeper (its own item list,
`.claude/agents/prereg-gatekeeper.md`, "The held-out test's declaration"). The lead pins it by the sha256 of its LF
text; nothing declared is edited. *This declaration chooses nothing.* Every input is cited from the pinned searches;
anything it would add is refused.

## 0. In plain words (for the operator)

<Which firms' searches it tests, how many finalists each brings, the order they are tested in (fixed by section 2's
rule before any search ran), and what a pass and a fail mean -- a pass carries a design to its registration and
confirmation; a fail at a place stops the sequence there; nothing is rerun.>

## 1. Its inputs: only the pinned searches' finalists' lists

Its inputs come only from the pinned searches' finalists' lists, each by its sha256:

| firm | search declaration | the search's pin (its LF sha256) | its finalists' row | its finalists' list file | that list's sha256 |
|---|---|---|---|---|---|
| Topstep | <...> | <...> | <... or "none", with the closing row> | <...> | <...> |
| My Funded Futures (MFFU) | <...> | <...> | <...> | <...> | <...> |
| Lucid | <...> | <...> | <...> | <...> | <...> |

- **Every other input is cited from each search's pinned file, unchanged:** the statistic, J and m, the held-out coin
  field `<S4>` and its keying, the limits and the point-estimate rule, the composite or the fallback, the baselines and
  their convention, the floors, the time leg's conditions, the verdict settings. Each finalist is tested under its own
  search's pinned inputs. **Anything new -- a reading, a baseline, a floor relaxed, a statistic, a seed -- is
  refused.**
- **The joint list file** (outside `prereg/`) lists, in the joint order of section 2, every finalist by its search
  declaration's hash and its finalists' row and list sha256. Its own LF sha256 is the `list` field of this
  declaration's finalists' token (section 5).

## 2. The joint order: a rule fixed now, before any search-year result

**The rule:** firms in the fixed order **Topstep, My Funded Futures (MFFU), Lucid**; within a firm, **the search's
own pinned finalist order** (its finalists' row, set by the finalist order rule its declaration pinned before its
survey). The rule is written here, in this template, before any search-year result exists; this declaration applies
it and states the resulting order. **A researcher's choice after a read is never the order.**

- **A firm whose search closes without finalists contributes none.** It is listed as none, with its closing row
  (a failed power gate, every design failing a gate, every finalist failing its no-harm floor), and **keeps its
  place** in the firm order; the sequence runs over the firms that have finalists.

## 3. When it is written

Only when **every firm's search has a finalists' row or a closing row** (E-221, O-1). Until then the held-out years
stay held; no firm's search reads them alone.

## 4. The k and the level

- The next free program k, assigned at its held-out row (E-204): <k>, one-sided level 0.05 / (k (k + 1)); k = 13 next.
  The joint sequence spends this one k; no search takes one.
- Each finalist is tested at the full level of the one k, in the joint order, stopping at the first failure (CHARTER
  3.7; E-203 S-1).

## 5. The rows, in order

1. **The pin row:** this declaration's LF sha256.
2. **Its finalists' token row, newer than the pin row:**
   `heldout-finalists: F-HT @ <its LF sha256> list <the joint list's sha256>` as the first text of the row's third
   cell, F-HT this declaration's F-number. Q-158's rule 1 (`extended/reader.py`) honours a held-out purpose only after
   a finalists' token for this declaration's own hash in a row newer than its pin, so the pin and the token in one row
   are refused.
3. **The held-out row** (k assigned, E-204), citing this hash, the token row and every search's finalists' or closing
   row.
4. **The held-out test**, once, from a clean checkout of the held-out row's commit (`scripts/run_clean.py`), under
   `run.lock`; the auditor on its result.
5. **The verdict row.**

## 6. Power at each place in the joint sequence

A finalist at place i is tested only if every finalist before it passed, so its power is conditional on those passes.
Re-state each finalist's power at its place, from its own search's pinned power gate (m-7):

| place | firm | finalist | its search's power at the size that matters | its power at this place |
|---|---|---|---|---|
| <...> | <...> | <...> | <...> | <...> |

Exit (B) cites this table.

## 7. The held-out reads

This declaration is the one family that reads NQ's held-out window (Q-158's rule 2). Its line names the two house
purposes and nothing else:

- **Judged-block reads:** `heldout_test`, `heldout_stress`

`heldout_test` reads every finalist and every baseline on the deciding reading, the time leg's groups and regimes, the
long-run gate, and the held-out readings each search puts beside -- the five-minute cell, the as-walked result and the
path-structure edge, the denial ladder, the playbook trigger side's held-out reading and the fill-time law;
`heldout_stress` reads the +1 tick and 10 %-missed stresses and the as-traded floor. Each read is made once, after the
token row and the held-out row; the held-out years are read once per market (CHARTER 3.6 (c)).

## 8. What a pass and what a fail mean

- **A pass at a place:** that finalist is carried -- its registration, its playbook, the auditor, and its one
  confirmation against a criterion declared at registration (CHARTER 5 (A)); the sequence goes on to the next place.
- **A fail at a place:** the sequence stops there; every later finalist is untested; nothing is rerun; the k is spent.
- **The confirmation window** (NQ from 2026-07-17) is read only for a carried design, and is a purchase.

## 9. Anything chosen after seeing results

*(Empty at the pin, and nothing is ever added: this declaration chooses nothing.)*
