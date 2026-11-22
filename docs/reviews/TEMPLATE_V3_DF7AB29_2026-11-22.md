# Red-team diff check: the templates' last pre-pin fixes (wt/wt-lit a611a65..df7ab29)

**Reviewer:** red team. The note is dated 2026-11-22 because the brief uses that date; the machine date is 2026-11-21.

**Target:** commit df7ab29 on `wt/wt-lit`, read as `git diff a611a65 df7ab29`. The five files are:
- `prereg/TEMPLATE_design_search.md` ("T")
- `prereg/TEMPLATE_heldout_test.md` ("HT")
- `.claude/agents/prereg-gatekeeper.md` ("GK")
- `extended/go_token.py` ("GT", new)
- `tests/test_design_search_template.py` ("TT")

Line numbers are at df7ab29. wt-lit's HEAD is still df7ab29, but its tree is in the middle of merging master, with
conflicts in `.gitignore` and `.claude/commands/brief.md`. I touched nothing in wt-lit.

**The brief.** It lists the items to attack and hints at no verdict. I checked each claimed fix against the finding it
answers (`TEMPLATE_V3_PREPIN_2026-11-22`) and against master's reader at 5f7bb8e, which carries Q-194e.

**Method.**
- **Detached checkout:** `C:\Users\resni\AppData\Local\stage2-extended-runs\rt-tmpl-df7ab29`, made with `git worktree
  add --detach`. I removed it at the end.
- **Probes:** synthetic logs and files only, under `scratchpad\rt_df7ab29\`: `probe_go.py`, `probe_scope.py`,
  `probe_void.py`, `probe_spacing.py`, `mutate.py` and `mutate_tail.py`.
- **What I read:** no bars, no atlas and no result file. Nothing from 2026-07-17 on. I quote no seed literal.

**Tests.** All runs used `OMP_NUM_THREADS=1` and a timeout.

| run | result |
|---|---|
| `tests/test_design_search_template.py tests/test_reader*.py` with df7ab29's own reader | 198 passed, 2 skipped (the two n-6 tests) |
| TT with master's `extended/reader.py` overlaid | 60 passed; the n-6 assertions run and hold |

---

## Verdict: **BLOCK**. Do not pin df7ab29's text as it stands. The fixes are wording plus small code changes; no new cycle is needed

- **Two MATERIAL wording defects in text that is about to be pinned:**
  - **B-1:** the power gate's new do-nothing clause can be read as conditional power.
  - **B-2:** CW-2's new definition of "data this line has never read" admits NQ's held-out years, and its new
    end-date clause forbids the only NQ route it is meant to describe.
- **A fail-closed disagreement with master's reader:** `go_token`'s void and fence rules can deadlock every survey
  permanently, through the reader's own prescribed recovery (B-3).
- **Six MINOR findings and four NOTEs.**

**What holds:**
- The other claimed fixes are present: DN-1's section 7 row and section 10 (c), GK-1, K-1r, L-1r, Q-1, n-2 and n-5.
- They are needled, and 24 of my 37 one-line mutants are killed.
- The held-out file name, the marker, the ten headings and the verdict form agree with master's reader (n-6).
- I found no reading that lets a non-member use NQ from 2026-07-17. The text bars it in every copy, and the reader
  refuses that window outright.

Counts: **0 CHANGES-A-CONCLUSION, 3 MATERIAL, 6 MINOR, 4 NOTE.**

| id | label | one line |
|---|---|---|
| B-1 | MATERIAL (wording) | T l.499-500: "the whole pass line's power ... **counted only over designs above the do-nothing floor**" reads as P(pass \| above floor), not P(pass and above floor). A planted design at the size that matters that lands below the floor drops out of the count instead of counting as a fail, so the gate can pass a search with almost no power and spend NQ's one held-out read. |
| B-2 | MATERIAL (wording) | T l.96-98, HT l.107-109, GK l.92-96: "Data this line has never read is bars after the last date any search of the line has read, as ledgered in `results/read_ledger.jsonl`". Choice-block reads are never ledgered (reader l.193), and searches read only 2020-2023, so the definition includes 2024-01-02 to 2026-07-16. "Data after that end is never read for a non-member" then removes the "later purchase" route that the sentence before it promises. |
| B-3 | MATERIAL (code; fail-closed liveness; disagrees with the reader) | GT l.102-103 and l.140-145. (a) An unclosed fence is a problem with no row, which no void can clear. The reader's Q-194e closes it with a void naming the row before the fence. (b) A void naming a counted go token, a first pin row, or **any** row that starts `heldout-finalists:` or `heldout-verdict:`, malformed or not, is a permanent problem. The reader treats such a void as a no-op, and its prescribed recovery of a *malformed* finalists row is exactly such a void. Either case refuses `go_row_present` for every declaration in the repository, forever, with an append-only log. |
| C-1 | MINOR | GT l.184-195: `declared_scope` fails open on formatting. These are all silently out of scope: `` `NQ` ``, `**NQ**`, `nq`, `**Topstep**`, `TopstepX`, a missing or renamed market field, and a fenced `- **The market:** ES` line above the real one. `go_row_present` (l.157-162) ignores scope, so such a search's survey runs while the membership event stays unfixed. That is H-1''s hole, reopened by a typo. |
| C-2 | MINOR (disagrees with the reader) | GT l.47-50: a row is only `\| E-NNN \|` with exactly one space each side. The reader's `ROW` takes `\|\s*E-NNN\s*\|`, and its `pins()` and `test_declarations_fixed.py` take a pin from any unfenced line. A hash row written `\|E-901\|` is a pin to the reader but not to GT. The firm is then put silently in state (c), and a second Topstep pin with odd spacing escapes R-1. |
| C-3 | MINOR | GT has no knowledge of closing rows, repeat go rows or the runner commit. A go token for a search already closed (`heldout-closed: F-NN @ ...`) counts and fixes the event. A second go token for the same declaration counts, possibly naming another runner commit (U-1). `go_row_present` is true after a finalists' row too, so a survey could rerun. |
| C-4 | MINOR | HT l.98-100 (cause 8): "a failed check on record at a named commit" can be any commit, including a test written after Topstep's finalists are read. The prior remedy's "that it cannot be fixed without changing a declared input" was dropped. D-1r is half answered. |
| C-5 | MINOR | The confirmation window's end is "declared at F-HT's held-out row" (HT l.128-129), after every member's search-year results and finalists exist. No rule fixes it. It is an unlabelled choice made after outcomes, and it sets the confirmation's power. It is also not tied to the reader's `heldout-window` form. |
| C-6 | MINOR (mutation) | 13 survivors among my 37 one-line mutants. Among them: the fence rules (4), "strictly after" in the same row, first-pin-wins, protected finalists and verdict rows, the design-search marker in scope, the date cell, case-insensitive go-like, T's section 2 end-date copy, and GK item 9's token copy. |
| n-a | NOTE | `extended/go_token.py` carries the membership rule but is cited by name, not by sha256. An edit after the pin re-defines the event. |
| n-b | NOTE | W42-R1's "pinning row" does not exist on master, and `extended/wave42.py` is on wt-infra only. The prior DN-1 remedy 6 (pin order) is not enforced anywhere. |
| n-c | NOTE | The k > 20 re-statement run (T l.503, l.614-615; GK l.248) has no stated consequence if it falls below the power target, and HT section 6 lacks the clause. |
| n-d | NOTE | GT counts a go token inside an HTML comment (`<!-- ... -->`), as the reader counts held-out tokens there. In the reader, a *closed* fence holding an exact held-out token is unvoidable; that is outside this diff. |

---

## B-1 (MATERIAL, wording). The power gate's do-nothing clause can be read as conditional power

**Where.** T l.499-500: "**The power gate**, before the go row: the whole pass line's power at the level it assumes,
**counted only over designs above the do-nothing floor** (E-255; section 7)". TT l.1899-1901 needles the phrase
word for word, so the defect is now protected by a test.

**Evidence.**
- "Power ... counted only over designs above the floor" reads naturally as power computed over the subset of planted
  designs whose composite clears the floor. That is P(pass | above floor).
- The pass line that decides is P(pass and above floor). It is the floor that the section 7 row and section 10 (c)
  impose ("a design not above it is no finalist"; at the verdict "a fail at its place").
- The do-nothing composite is a constant fixed by W42-R1's values. On wt-infra 01e896a, `null_composites` scores a
  journey with no fee and no trade through `composite_per_seed`.
- The planted improvement is "the size that matters" **over the baselines**. When the baselines sit below do-nothing,
  which the prior DN-1 called possible under zero edge, a plant of that size can sit mostly below the floor.

**The failure it allows.**
- **Input:** the baselines' composites are below the do-nothing floor, and the planted design clears the floor on 5 %
  of synthetic draws and passes the rest of the line on 90 % of those.
- **Output:** under the conditional reading the gate reports 0.90 and passes. The unconditional power is 0.045.
- **Consequences:**
  - The search gets its go row.
  - Exit (B) and HT section 6's place powers inherit 0.90.
  - The joint test spends NQ's one held-out read (CHARTER 3.6 (c)) on a line that cannot pass.
- **What it does not change:** the size. The floor only adds failures.

**Remedy.** Replace the phrase with: "the whole pass line's power at the level it assumes, **the do-nothing floor
included: a planted design whose composite is not above the floor counts as a fail and never leaves the count**
(E-255; section 7)". Re-needle TT l.1899-1901 to the new text, and add a bad needle for "counted only over".

## B-2 (MATERIAL, wording). CW-2's definition admits the held-out years, and its end clause removes the route it describes

**Where.** The same sentence appears in three places, and TT's `DEF_NEVER_READ` (l.1866-1868) needles it in all
three:
- T l.96-98;
- HT l.107-109;
- GK l.92-96.

> **Data this line has never read** is bars after the last date any search of the line has read, as ledgered in
> `results/read_ledger.jsonl`; the confirmation window ends at a date declared at F-HT's held-out row, and data after
> that end is never read for a non-member (CW-2).

**Evidence.**
1. Master's reader (l.193): "**Choice-block reads are not ledgered** (the brief: judged reads only)". A search reads
   only the search years. So no search read is ever in `results/read_ledger.jsonl`, and "the last date ... as
   ledgered" is undefined.
2. On any sensible reading, the last date a search has read is at most 2023-12-29. "Bars after" it therefore include
   **NQ's held-out years 2024-01-02 to 2026-07-16**. F-HT reads those years, but F-HT is not "a search of the line".
3. The definition is used in the very next breath: "its candidates are tested only on data this line has never read
   (a later purchase), under its own k". So the text now *admits* a non-member testing its candidates on NQ's held-out
   years. That is the reading CW-2 asked to close, and it contradicts E-259 (3) and Rule 2 (one held-out read per
   market).
4. "Data after that end is never read for a non-member" forbids NQ after the window, for every non-member, forever.
   That includes every later line's searches, which are all non-members of this F-HT. It contradicts "(a later
   purchase)" and T l.98-100's "moves its held-out years to data not yet read (a purchase ...)".

**What stops a wrong read today.** Code: the reader refuses 2026-07-17 on, whatever the purpose; it allows a market's
held-out window only to its one held-out declaration (Q-194e); and Rule 2 holds. The defect is in the declared rule,
which is about to be frozen.

**Remedy (one sentence, copied to the three places and needled).** "**Data this line has never read** is NQ bars
after the confirmation window's end, or another market's bars that no declaration of this repository has read;
never NQ's search years, never NQ's held-out years (2024-01-02 to 2026-07-16), and never the confirmation window."
Drop the ledger clause, which can never hold a search's read, and drop "never read for a non-member".

## B-3 (MATERIAL, code). `go_token`'s void and fence rules disagree with master's reader and can deadlock every survey

**Where.**
- GT l.102-103: the unclosed fence is recorded as `(None, -1, ...)`. l.142 keeps every problem whose row is None.
- GT l.140-145: a void whose target is in `counted`, `pin_rows` or `protected` is appended as a problem.
- `_PROTECTED` (l.52) matches any row that *starts* `heldout-finalists: ` or `heldout-verdict: `, valid or not.
- Problems that come from voids are never clearable, because a void naming a void row does nothing (l.143-145
  iterate voids only).

Master's reader (5f7bb8e) does otherwise:
- `_fence_state` (l.750-776) closes a fence left open just after row E-NNN at a later `heldout-void: E-NNN` row.
- `heldout_token_problems` (l.826-865) ignores a voided *malformed* row, and "a void naming a valid token row or a pin
  row does nothing".

**Evidence** (`probe_go.py`, `probe_void.py`; the reader is master's):

| log | reader problems | `go_problems` | `go_row_present(F-13)` |
|---|---|---|---|
| pins 13 and 14, a stray "```" after E-901, the go row, pin 15, then `heldout-void: E-901` | 0 | 3 (unclosed fence; E-902 and E-904 "inside a fence") | False |
| a valid log, then `heldout-void: E-902`, the counted go row (a typo for E-903) | 0 | 1 | False |
| the same, then `heldout-void: E-906`, naming the bad void | 0 | 1 (unchanged) | False |
| F-HT pinned, a malformed `heldout-finalists:` (short sha), then the reader's prescribed `heldout-void` of it | 0 | 1 | False |
| a counted go row E-902, and a fenced quotation of that same row (same E-id), then `heldout-void: E-902` | (fenced exact held-out tokens only) | 1 | False |

**The failure it allows.**
- **Input:** one stray fence, one mistyped void, the reader's own recovery of a malformed finalists row, or a fenced
  quotation of the real go row.
- **Output:**
  - `go_problems` is never empty again.
  - `membership` refuses.
  - `go_row_present` is False for **every** declaration of every market, so no design-search survey can ever start.
  - The gatekeeper can never read F-HT's membership by code.
- **Effect:** fail-closed, so nothing untrue is produced. But it is permanent, the log is append-only, and the text
  promises a recovery: T l.644-648 says "refuses every membership reading until a later `heldout-void` ... row voids
  it", and HT l.143-144 says "A malformed row or fence is voided by a later row `heldout-void`".

**Remedy.**
1. Build GT's fences and voids on the reader: import `extended.reader._fence_state` (or a public alias) and its void
   regex, instead of re-implementing them.
2. Treat a void naming a counted go token, a pin row, or a *valid* held-out token row as a no-op, as the reader does,
   not as a problem.
3. Protect only valid finalists and verdict tokens (`RD.heldout_tokens`), not any row with that prefix.
4. Make an unclosed fence clearable by the reader's rule.
5. Add a test that, for a battery of logs (the table above plus the reader's own fence fixtures), `GT.fences(log)[0]`
   equals the reader's fenced vector, and that the reader-clean logs are GT-clean.
6. Reword HT l.143-144 and GK l.229-231 as "a void never voids a **valid** verdict, finalists or pin row" (the
   reader's meaning).

## C-1 (MINOR). The scope fails open on formatting, and the runner's check ignores scope

**Where.** GT l.57-59, l.184-195 (`declared_scope`), and l.157-162 (`go_row_present`).

**Evidence** (`probe_scope.py`, drafts made from T by filling the two fields):

| market field / firm line | `declared_scope` |
|---|---|
| `` `NQ` ``, `**NQ**`, `nq`, `MNQ` | out of scope |
| `NQ` / `**Topstep**, 50K` | out of scope |
| `NQ` / `TopstepX, 50K` | out of scope |
| `NQ` / `Lucid Trading, ...` | Lucid |
| `NQ` / `My Funded Futures (MFFU), ...` | MFFU |
| `NQ, ES` | Topstep (NQ) |
| `NQ` / `Topstep and Lucid, 50K` | Topstep (R-1 by hand only) |
| a fenced `- **The market:** ES` above the real NQ field | out of scope (`.search` reads the fenced line first) |
| the marker rewritten `**Declaration kind:** design search.` | out of scope |
| the field renamed `- **Market:** NQ` | out of scope |

**The failure it allows.**
- **Input:** Topstep's NQ search pins with `` - **The market:** `NQ` ``, and its go row is valid.
- **Output:**
  - `go_row_present` is True, so the survey runs and Topstep's search-year results exist.
  - `membership` reports no event, because F-13 is not in scope.
  - MFFU or Lucid can now pin, having seen Topstep's results, and become members. That is H-1''s hole.
  - F-13 itself is in no membership at all.
- **What it does not change:** the size of the held-out test. The hole is in selection, not in the held-out years.

**Remedy.**
- `declared_scope` refuses (raises) for any `prereg/F-*.md` that carries the design-search marker but does not have
  exactly one unfenced market line and one unfenced firm line in the template's exact form.
- `go_row_present` refuses when the declaration carries the marker and its scope cannot be decided.
- TT asserts every row of the table above.
- T l.44 adds "a market field not in this exact form (a bare market code) is refused at the pin".

## C-2 (MINOR). GT's row form is narrower than the reader's

**Where.** GT l.47 (`_ROW = \| (?P<row>E-\d+) \|`), l.43 (`GO_TOKEN`), and l.88 (`_first_pins` reads pins only in
rows of that form). Against them: the reader's `ROW = \|\s*(E-\d+)\s*\|` (reader l.258), and its `pins()` (l.467-477)
and `test_declarations_fixed.py` l.14, which take a pin from any unfenced line.

**Evidence** (`probe_spacing.py`):
- MFFU's hash row written `|E-901| ...` before Topstep's go row. The reader's `_pin_rows` finds it at E-901, but GT's
  membership is `('E-902', {'Topstep': 'F-13'})`: MFFU is silently in state (c).
- A second Topstep pin `|E-899 | ...` before the event: GT returns members with no R-1 refusal, while the reader sees
  the pin.
- A go row `|  E-902 |`: neither a token nor a problem. This one fails closed, because `go_row_present` is False.

**Remedy.**
- Use the reader's `ROW` and `PIN` in GT, so a pin is a pin wherever the reader and `test_declarations_fixed.py`
  count it.
- Make a go-like third cell in any reader-row a problem when it is not the exact token.
- Test both spacing cases.

## C-3 (MINOR). The go token ignores closing rows, repeat go rows and the runner commit

**Where.** GT `_scan` and `go_row_present` (l.95-162). `grep closed` in GT finds only fence wording.

**The failure it allows.**
- **(i) A closed search fixes the event.** F-13 closes `power-gate-failed`, then a go row for F-13 is written by
  mistake. It counts, fixes the membership event, and puts every firm not yet pinned in state (c). It also lets a
  closed search's survey start.
- **(ii) The runner commit is unbound.** A second `go: F-13 @ <same sha> -- <names another runner commit>` counts
  silently. U-1 ("bound by its sha; a change to deciding code after it is a new declaration") is not checked by code.
- **(iii) A survey can rerun.** `go_row_present` stays True after F-13's finalists' row.

**Remedy.**
- In GT: a go token whose declaration has an earlier `heldout-closed: F-NN @ <sha>` row is a problem, and so is a
  second counted go token for one declaration.
- Give GT an accessor that returns the runner commit the go row names, in a fixed sub-form, e.g. `... -- runner
  <40 hex>; ...`, which the survey runner compares with its HEAD.
- `go_row_present` is False once the declaration has a finalists' or closing row.

## C-4 (MINOR). Cause 8 still accepts a check written after the fact

**Where.** HT l.98-100: "a failed check on record at a named commit (a test or an identity failing, or a firm key the
loader now refuses), cited by its file and sha256 and by its diagnosis row, with the auditor's note confirming it". T
l.656-657 and GK l.218-219 repeat it. TT's `_firm_states` (l.1207-1210) checks only that `commit`, `check` and
`auditor_note` are non-empty.

**The failure it allows.**
- **Input:** after Topstep's finalists' row, the lead commits a new test that MFFU's runner fails (or tightens the
  loader so it "now refuses" a key MFFU uses), writes a diagnosis row, and the auditor confirms the test fails.
- **Output:** MFFU closes as `defect-on-record`. That is W-1's drop under another name. It raises the later places'
  powers and changes the joint list.
- **What it does not change:** the level.
- **What was dropped:** the prior remedy's guard, "confirming that it cannot be fixed without changing a declared
  input".

**Remedy.** Add to the cause's text:
- "the check committed at or before the membership event's commit, or one of the search's own declared refusals or
  identities";
- "the auditor confirming it cannot be fixed without changing a declared input";
- "every such close counted beside the verdict".

In `_firm_states`, refuse a check whose commit is marked as after the event.

## C-5 (MINOR). The confirmation window's end is chosen after the search-year outcomes

**Where.**
- T l.114 and l.717, and HT l.187: "NQ from 2026-07-17 to the end date declared at F-HT's held-out row".
- HT l.128-129: "declaring the confirmation window's end date (CW-2)".

**Evidence.**
- F-HT's held-out row is written after every member's finalists exist.
- The end date sets how much data, and so how much power, the carried designs' one confirmation has.
- No rule fixes it. It is neither fixed by an outside source nor searched in a declared walk-forward, so it is an
  unlabelled choice made after outcomes.
- It is also free text: the reader's window grammar is `heldout-window: NQ <start> to <end>` (reader l.289-290), and
  that row "opens nothing for a test until a decision row makes that rule".

**Remedy.**
- Fix the end now by a rule. Either "2026-07-17 to 2027-07-16, the reader's example window, extended only by a
  purchase", or "the length the registration's confirmation criterion needs at its declared power, computed from the
  pinned power gate".
- Say whether a `heldout-window` row records it.

## C-6 (MINOR). Mutation: 13 of 37 one-line mutants survive

**Method.** `mutate.py` / `mutate_tail.py`: one replacement each in the detached checkout, then TT with `-x`.

| killed (24) | surviving (13) |
|---|---|
| G1 fenced rows not skipped; G2 unclosed fence ignored; G4 sha unchecked; G5 tail optional; G7 marks not skipped; G8 void before its target clears; G9 void of a counted token allowed; G10 a pin in the event's row counts; G11 R-1 removed; G12 scope ignores market; G14 present ignores sha; G15 membership skips hygiene; G21 pin rows unprotected; G22 Apex in scope; G23 voids ignored; G24 scope ignored for the event; G27 void tail optional; T3 to T14 except T1 and T2 (the do-nothing, CW, void, cause 8, scope and end-date needles) | **G3** a go token in its own hash row counts (`>=` to `>`); **G6** go-like case-sensitive (`Go:` silently ignored); **G13** the design-search marker not required for scope; **G16** last pin wins (not the first); **G17** a fence closed by the other character; **G18** the info-string backtick rule removed; **G19** a fence closed by a shorter run; **G25** a 4-space indent opens a fence; **G20** finalists and verdict rows unprotected; **G26** the date cell not required; **T1** T l.114's end-date copy removed; **T2** GK item 9's token copy removed |

The control survives (60 passed), so the harness discriminates.

**Remedy.**
- Add the B-3 fence-agreement battery, which kills G17, G18, G19 and G25.
- Add a same-row pin-and-go probe (G3), a `Go:` probe (G6), a marker-less F- file in the scope fixture (G13), a
  re-pin row (G16), a void of a valid finalists row (G20) and a bad-date go row (G26).
- Needle T l.114's copy and GK item 9's token.

## Notes

- **n-a.** `extended/go_token.py` now *is* the membership rule (T l.644-648, l.660; HT l.82), but it is cited by path.
  Remedy: the template pins name the module's LF sha256 beside the template's, or GK refuses a go row whose runner
  commit has a different `go_token.py`.
- **n-b.** W42-R1 has no pinning row on master, and `extended/wave42.py` is at wt-infra 01e896a only. T's section 7
  row cites "W42-R1 at its pinning row", a forward reference. The prior DN-1 remedy 6 ("`extended/wave42.py` with
  `DO_NOTHING_EPS` is on master before either template is pinned") is in no test and no text. Remedy: the lead pins
  W42-R1 first, and TT asserts that `extended/wave42.py` exposes `DO_NOTHING_EPS` and `do_nothing_floor` once the
  template is pinned.
- **n-c.** T l.503 and l.614-615 and GK l.248 require a re-statement run when k > 20, but say neither what happens if
  it falls below the power target after finalists exist (a closing row is refused then) nor that it runs from the go
  row's runner commit with the gate's pinned seeds. HT section 6 lacks the clause. Remedy: "a re-statement only; it
  closes nothing; exit (B) cites it; from the go row's runner commit at the gate's pinned seeds", copied into HT
  section 6.
- **n-d.** A go row inside `<!-- ... -->` counts (probe "go token in HTML comment"). The reader does the same for
  held-out tokens. Also, outside this diff: in master's reader a properly closed fence holding an exact held-out token
  is a problem that no void clears (the fenced branch checks only the fence-recovery set). That belongs to the
  reader's owner.

## What I tried that found nothing

- **The claimed fixes are in the text and needled:**
  - DN-1: the section 7 row, section 10 (c), GK item 10, GK held-out item 2, and HT section 8's citation;
  - G-2's text in T step 4, HT section 3 and GK items 1 and 4;
  - CW-2's T section 15 copy;
  - K-1r: all three remnants gone, with bad needles;
  - GK-1: Q-194d's file name, marker and headings in GK held-out item 1;
  - L-1r: "it has no held-out part";
  - Q-1: "every commit ... merges included" and the void sentence;
  - n-1, n-2 and n-5: one token form, the old form refused.
- **Agreement with master's reader (5f7bb8e).** With master's reader overlaid, TT's n-6 tests run, not skip, and
  pass:
  - `_verdict_rx` equals `HELDOUT_TOKENS["verdict"]`;
  - `HELDOUT_HEADINGS`, `HELDOUT_MARKER` and `HELDOUT_PATH` equal the template's;
  - the verdict form in every copy is the reader's.
- **GT's fence scanner** (`fences`) is line-for-line the reader's `_fence_scan`: the same open regex, the info-string
  rule and the close rule. Without voids, the two agree on every probe, including a tilde fence closed by backticks
  (both refuse), a backtick fence with a backtick info string (both read it as no fence), a 4-space indent (both read
  it as no fence) and CRLF.
- **Tokens that count when they should not.** Refused: a fenced go row, a go row before its hash row, a wrong sha,
  bold, backticks, no tail, `Go:`, a malformed tail, a go row naming an unpinned search (TT's P5), and a void placed
  before its target. Not counted, and the runner refuses: `go -`, `**Go (F-13).** go:`, leading spaces and odd
  spacing (C-2 aside).
- **The do-nothing floor's path to ranking.** The floor is applied "before ranking and before the finalists' row" (T
  l.438, l.532-535). The joint order takes only each search's pinned finalist order (HT section 2), so a design below
  the floor cannot be ranked unless a search violates its own section 7 row, which GK refuses. The floor is
  data-independent: on wt-infra 01e896a it is a constant from W42-R1's values, so comparing it with a held-out
  composite is well defined. B-1 is the one path by which power is counted over it.
- **NQ from 2026-07-17 for a non-member.** The four sites forbid it (T l.96, l.114, l.717; HT l.107, l.187; GK l.92),
  and so does the new end clause. The reader refuses that window for every purpose. Only B-2's definition
  misdirects, and only toward the held-out years, which code refuses.
- **The k wording (K-1r, n-1).** No "its k spent" or "its k is spent" remains in T. A search spends no k. The level
  arithmetic is k = 13, 0.05 / 182. One residue is n-c.
- **The real logs.** `go_problems` is [] for wt-lit's and master's `DECISIONS.md`. `declared_scope` is {} on both
  trees, because no F- file there carries the design-search marker. So no membership event exists yet, and the fixes
  can land before any go row.

## What I could not check

- **Whether a survey runner calls `go_row_present`.** No runner exists on wt-lit. The survey runner v3 is on another
  branch, so T l.659-660's "checked by code" is still a build requirement.
- **W42-R1's pinned values.** `null_composites` at its pin is not on master, so I could not check that the
  do-nothing composite is above every baseline's or below it on H4's readings. That decides how often B-1 bites.
- **wt-lit's in-progress merge of master.** I did not read the merge result. If it changes any of the five files, this
  note does not cover the result.
