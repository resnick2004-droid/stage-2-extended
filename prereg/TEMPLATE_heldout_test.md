# TEMPLATE: the held-out test's declaration -- copy it, never pin it

**What this file is.** The house form for the one declaration that reads NQ's held-out years: the joint
fixed-sequence test of every firm's finalists (CHARTER 3.6 (c), 3.7; E-221, O-1; E-238), the red team's full read of
text v2, M-1, as its re-read (`TEMPLATE_V2_c1_2026-11-20.md`: H-1, H-2, m-2 to m-5) amends it. It is not a
declaration: it names no search, holds no seed, no k and no figure, and its name matches neither the reader's grammar
(`F-` or `RD-` and a number) nor any test's declaration glob (`tests/test_design_search_template.py` holds that).
Every design search is drafted on `prereg/TEMPLATE_design_search.md` and carries no `Judged-block reads:` line; this
declaration carries it. When it stands, this template is pinned by its sha256 in a decision row (m-5), and F-HT cites
that pinned hash: the rules below are fixed by that pin, not by this file's later text.

**Declaration kind: held-out test.** A declaration drafted on this template keeps this line. The marker is valid only
on a declaration written from this template and pinned as F-HT (m-2): the scan of
`tests/test_design_search_template.py` refuses a held-out-marked file whose `Judged-block reads:` line names any
purpose but `heldout_test` and `heldout_stress`, a second held-out-marked `F-` file for the market, a held-out-marked
file without this template's section headings, and one that also carries the design-search marker. Q-194 closes the
reader's side.

**To use it:** copy it to `prereg/DRAFT_F-XX_heldout_test_NQ.md` as soon as every firm is in a terminal state
(section 3), replace every `<...>`, and send it to the red team and the gatekeeper (its own item list,
`.claude/agents/prereg-gatekeeper.md`, "The held-out test's declaration"). The lead pins it by the sha256 of its LF
text; nothing declared is edited. *This declaration chooses nothing.* Every input is cited from the pinned searches;
anything it would add is refused.

## 0. In plain words (for the operator)

<Which firms' searches it tests, how many finalists each brings, the order they are tested in (fixed by section 2's
rule before any search was declared), and what a pass and a fail mean -- a pass carries a design to its registration
and confirmation; a fail at a place stops the sequence there; nothing is rerun.>

## 1. Its inputs: only the pinned searches' finalists' lists

Its inputs come only from the pinned searches' finalists' lists, each by its sha256:

| firm | its state (section 3) | search declaration | the search's pin (its LF sha256) | its go row | its calibration record's sha256 | its finalists' row (newer than its go row) or closing row | its finalists' list file | that list's sha256 | the runner commit that produced the finalists |
|---|---|---|---|---|---|---|---|---|---|
| Topstep | <...> | <...> | <...> | <...> | <...> | <...> | <...> | <...> | <...> |
| My Funded Futures (MFFU) | <...> | <...> | <...> | <...> | <...> | <...> | <...> | <...> | <...> |
| Lucid | <...> | <...> | <...> | <...> | <...> | <...> | <...> | <...> | <...> |

- **Every other input is cited from each search's pinned file, unchanged:** the statistic, J and m, the held-out coin
  field `<S4>` and its keying, the limits and the point-estimate rule, the composite or the fallback, the baselines and
  their convention, the floors, the time leg's conditions, the verdict settings. Each finalist is tested under its own
  search's pinned inputs. **Anything new -- a reading, a baseline, a floor relaxed, a statistic, a seed, code -- is
  refused.**
- **The joint runner** (m-4): the held-out run uses each search's runner at its cited commit, or a new runner with its
  own identity, reproducing that search's search-year outputs path for path before any held-out read (CLAUDE.md:
  every new runner has its own identity). A runner without that identity refuses the run.
- **The joint list file** (outside `prereg/`) lists, in the joint order of section 2, every finalist by its search
  declaration's hash and its finalists' row and list sha256. Its own LF sha256 is the `list` field of this
  declaration's finalists' token (section 5).

## 2. The joint order: a rule fixed now, before any search is declared

**The rule:** the order **alternates by rank across the firms** (H-2): rank 1 of Topstep, rank 1 of My Funded Futures
(MFFU), rank 1 of Lucid, then rank 2 of each in the same firm order, and so on; **a firm whose list is exhausted is
skipped**. A firm's ranks are **the search's own pinned finalist order** (its finalists' row, set by the finalist
order rule its declaration pinned before its survey). The firm order is the program's own, older than every search:
CHARTER 3.6 (c)'s firm list and CLAUDE.md's Topstep-first line. The rule is written here, before any search is
declared, and recorded by the lead's row (E-254, cited by number once committed); this declaration applies it and
states the resulting order. **A researcher's choice after a read is never the order.**

- A firm in state (b) or (c) of section 3 contributes no finalist: it is **listed as none** and **keeps its place**
  in the firm order; the alternation runs over the firms that have finalists.

## 3. The firms' states: a closed list, decided by rule (H-1)

- **The firms are fixed now:** Topstep, My Funded Futures (MFFU), Lucid.
- **Only a firm's latest pinned search counts.** An earlier search's finalists are void once a successor is pinned.
- **A firm's state is one of three, and nothing else:**
  - **(a) finalists:** its latest pinned search has a finalists' row;
  - **(b) none:** its latest pinned search has a closing row;
  - **(c) none:** no search of the firm was ever pinned.
- **The closing row's form**, the first text of the row's third cell, in the reader's positional form:
  `heldout-closed: F-NN @ <its LF sha256> -- <cause> -- <text>`, its cause **one of a closed list**:
  1. `calibration-failed` -- the deciding calibration failed;
  2. `limit-clause-failed` -- the power gate's limit clause failed;
  3. `power-gate-failed` -- the power gate failed;
  4. `every-design-failed-a-gate` -- every surveyed design failed a gate before its outcomes;
  5. `empty-finalist-list` -- the finalist order rule yielded an empty list;
  6. `every-finalist-failed-no-harm` -- every finalist failed its playbook no-harm floor;
  7. `withdrawn` -- a withdrawal under E-005 (d), its reason in the row.
- **This declaration is written as soon as every firm is in a terminal state.** After the third terminal state, **no
  new search may be pinned until this declaration's held-out row is written.**
- **A pinned search that is neither finalised nor closed blocks the declaration.** It must be closed or finalised by
  its own rules, **never waited out by choice**.

## 4. The k and the level

- The next free program k, assigned at its held-out row (E-204): <k>, one-sided level 0.05 / (k (k + 1)); k = 13 next.
  The joint sequence spends this one k; no search takes one.
- Each finalist is tested at the full level of the one k, in the joint order, stopping at the first failure (CHARTER
  3.7; E-203 S-1).

## 5. The rows, in order

1. **The pin row:** this declaration's LF sha256.
2. **The held-out row, which is its finalists' token row (m-3), newer than the pin row:**
   `heldout-finalists: F-HT @ <its LF sha256> list <the joint list's sha256>` as the first text of the row's third
   cell, F-HT this declaration's F-number, k assigned in the row's text (E-204), citing every firm's finalists' or
   closing row. Q-158's rule 1 (`extended/reader.py`) honours a held-out purpose only after a finalists' token for
   this declaration's own hash in a row newer than its pin, so the reader itself enforces "after the held-out row";
   the pin and the token in one row are refused.
3. **The held-out test**, once, from a clean checkout of the held-out row's commit (`scripts/run_clean.py`), under
   `run.lock`; the auditor on its result. **No repeat row** (`repeat="E-NNN"`) is ever written for F-HT.
4. **The verdict row.**

## 6. Power at each place in the joint sequence

A finalist at place i is tested only if every finalist before it passed. **The place-power formula, declared now
(H-2):** pi_j is the three-way design note's power for finalist j at the level the sequence assigns to its place --
the full level 0.05 / (k (k + 1)) at every place -- from its own search's pinned power gate at the size that
matters; under the stated dependence assumption, **independence across finalists**, the power at place i is the
product of pi_1 to pi_i. Beside it, never deciding, the Frechet lower bound, which needs no dependence model:
max(0, pi_1 + ... + pi_i - (i - 1)). Re-state each finalist's power at its place:

| place | firm | rank | finalist | pi (its search's power at the level) | its power at this place (independence) | the Frechet lower bound |
|---|---|---|---|---|---|---|
| <...> | <...> | <...> | <...> | <...> | <...> | <...> |

Exit (B) cites this table.

## 7. The held-out reads

This declaration is the one family that reads NQ's held-out window (Q-158's rule 2). Its line names the two house
purposes and nothing else:

- **Judged-block reads:** `heldout_test`, `heldout_stress`

`heldout_test` reads every finalist and every baseline on the deciding reading, the time leg's groups and regimes, the
long-run gate, and the held-out readings each search puts beside -- the five-minute cell, the as-walked result and the
path-structure edge, the denial ladder, the playbook trigger side's held-out reading and the fill-time law;
`heldout_stress` reads the +1 tick and 10 %-missed stresses and the as-traded floor. Each read is made once, after the
held-out row; the held-out years are read once per market (CHARTER 3.6 (c)).

## 8. What a pass and what a fail mean

- **A pass at a place:** that finalist is carried -- its registration, its playbook, the auditor, and its one
  confirmation against a criterion declared at registration (CHARTER 5 (A)); the sequence goes on to the next place.
- **A fail at a place:** the sequence stops there; every later finalist is untested; nothing is rerun; the k is spent.
- **The confirmation window** (NQ from 2026-07-17) is read only for a carried design, and is a purchase.

## 9. Anything chosen after seeing results

*(Empty at the pin, and nothing is ever added: this declaration chooses nothing.)*
