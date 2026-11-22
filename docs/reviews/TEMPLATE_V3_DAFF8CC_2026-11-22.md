# Red-team diff check: the templates' pre-pin fixes (wt/wt-lit df7ab29..daff8cc)

**Reviewer:** red team. The note is dated 2026-11-22 because the brief uses that date; the machine date is 2026-11-21.

**Target:** `git diff df7ab29 daff8cc` over six files:
- `prereg/TEMPLATE_design_search.md` ("T")
- `prereg/TEMPLATE_heldout_test.md` ("HT")
- `.claude/agents/prereg-gatekeeper.md` ("GK")
- `extended/go_token.py` ("GT")
- `tests/test_design_search_template.py` ("TT")
- `tests/test_declarations_fixed.py` ("DF")

Line numbers are at daff8cc. `extended/reader.py` at daff8cc is byte-identical to master 5f7bb8e (an empty diff).

**The brief.** It lists the findings to check (B-1 to B-3, C-1 to C-6, n-a to n-d), the lead's rulings, and seven
attacks. I took the rulings as fixed and checked each fix against its ruling. Where a ruling is followed but still
leaves a hole, I say so. The brief hints at no verdict.

**Method.**
- **Detached checkout:** `C:\Users\resni\AppData\Local\stage2-extended-runs\rt-tmpl-daff8cc` (`git worktree add
  --detach`), with no data junctions. I removed it at the end, and wt-lit's tree is untouched (`git status` is empty).
- **Probes:** synthetic logs and files only, under `scratchpad\rt_daff8cc\`:
  - `probe_go2.py`: whether each kind of problem can be recovered; closing rows; the runner; line ends;
  - `probe_scope2.py`: whether the scope fails closed;
  - `probe_cw.py`: the confirmation window row;
  - `probe_real.py`: the real logs;
  - `mutate2.py`: 59 one-line mutants and a control.
- **What I read:** no bars, no atlas, no result file, nothing from 2026-07-17 on. I quote no seed literal.

**Tests.** All runs used `OMP_NUM_THREADS=1` and a timeout.

| run | result |
|---|---|
| TT, DF and `tests/test_reader*.py` | exit 0, no failure and no skip |
| TT and DF (the control in `mutate2.py`) | 68 passed |

---

## Verdict: **BLOCK**. Do not pin daff8cc's `go_token.py`. The text needs only small edits; no new cycle is needed

**The block.** B-3 is only half fixed.
- **What is fixed:** fences and voids now come from the reader, and voiding a valid row does nothing.
- **What remains:** every problem raised by an **exact** go token can never be cleared. That covers a wrong sha, an
  unpinned F-number, a second go row, a go row after a closing row, and a go row in its own pin's row. So does a
  malformed go row that also carries a pin, and a malformed row whose void is hidden by an earlier mistyped void.
- **The cost of one such row:** one typo in the log refuses `go_row_present` for every survey of every market, for
  good.
- **The text says otherwise:** T l.651-655 calls a closed search's go row and a second go row hygiene problems that
  last "until a later `heldout-void` ... voids it". The code never clears either.
- **Why it matters now:** this module is about to be pinned by sha256 (n-a), so fixing it after the pin means pinning
  the templates again.

**What holds.**
- **B-1:** fixed, in wording and needles. There is no code path yet, and none counts power over a subset.
- **B-2:** fixed for NQ itself. MNQ remains open (finding 7).
- **n-a and n-b:** both are enforced by DF as described, in a weaker form than intended (findings 8 and 9).
- **The C-4, C-5 and n-c rulings:** each is in the text, copied where it should be, and needled.
- **Mutation:** 49 of my 59 mutants are killed.

Counts: **0 CHANGES-A-CONCLUSION, 1 MATERIAL, 9 MINOR, 7 NOTE.**

| # | label | file:line | one line |
|---|---|---|---|
| 1 | MATERIAL | GT l.104-106, 114-115, 134, 138-147 | Every problem from an exact go token (wrong sha, unpinned F-number, second go row, go after closing, go in its own pin's row) is permanent; so are a voided malformed row that carries a pin, and a malformed row behind an earlier mistyped void. Each one refuses every survey for good, and the reader stays clean. This contradicts T l.651-655. |
| 2 | MINOR | GT l.180-194; T l.656-660, 669-673 | U-1 is not bound in code. `go_row_present` takes no HEAD, and nothing compares `go_runner` with the checkout. A clean checkout of the runner commit cannot contain the go row that names it, so "run on that runner commit" and "`go_row_present` holds" cannot both be read literally. |
| 3 | MINOR | GT l.60-61, 107-111 | A malformed closing row (`power gate failed`, `Heldout-closed:`) is neither a closing row nor a problem. A go row after it counts, fixes the membership event and lets a closed search's survey run: C-3 (i) reopened. A cause outside the eight is accepted. |
| 4 | MINOR | GT l.66-73, 225-227, 262 | The scope still fails open: market `NQZ6`, `NQH26`, `ENQ` or `NQQ`; firm `MFF`, `Top step`, `MyFundedFutures` or `TS`; an unfilled `<firm, plan>`; marker variants with renumbered headings. `Lucid, Topstep 50K` is read as Lucid, and a fenced marker puts a file in scope. In every case `go_row_present` is True. |
| 5 | MINOR | HT l.132-134, 195-197; T l.117-119, 728-730; TT l.2104; GK l.98 | C-5: a second `heldout-window: NQ 2026-07-17 ...` row written after the finalists re-chooses the end, and the reader takes the newest row; nothing refuses it. "Never chosen with a finalist known" cannot be enforced. The end "as purchased" needs the purchase before the first finalists' token. GK lacks the rule. |
| 6 | MINOR | HT l.100-104 | C-4 bounds the date of the **check**, not of the **failure**. A check committed before the event can be made to fail by a change after it. |
| 7 | MINOR | T l.99-101, HT l.111-112, GK l.93-95 | B-2's "another market's bars" admits MNQ's 2024-01-02 to 2026-07-16. MNQ shares NQ's underlying (the accepted reading), and the reader keys markets by code. "Here" is ambiguous. |
| 8 | MINOR | GT l.51-62; DF l.58 | n-a pins `go_token.py` but not the reader rules it imports. Two reader mutants that change GT's behaviour survive (r06, r07). TT's fence-equality assertion is a tautology. |
| 9 | MINOR | DF l.59, 70 | n-b's "W42-R1 pin" is any line mentioning the file's sha256: fenced, a draft, never hash-checked. Nothing asserts `DO_NOTHING_EPS`. |
| 10 | MINOR (mutation) | TT | 10 of 59 mutants survive. Among them are fenced pins counting (g30), fenced closing rows counting (g29) and two firm lines (g11). |
| n1 | NOTE | reader l.750-776, 827-865 | The reader itself deadlocks on a pin-carrying malformed held-out row, on a stray fence after a non-row line, and on a first void that hides a later one. That is the reader's owner's. |
| n2 | NOTE | HT l.132-134 | A `heldout-window` row is a new **held-out** window in the reader's rules 2 and 3, not a confirmation window. The decision row that opens the confirmation must say which. |
| n3 | NOTE | GK l.253 | "exit (B) cites it" appears twice. A k > 20 re-statement from the runner commit needs a gate that takes k as an input. |
| n4 | NOTE | T l.101-103 | "A later search ... reads NQ's held-out years ... as a description only" omits "after F-HT's verdict row (reader rule 4)". This text is unchanged context. |
| n5 | NOTE | GT l.57 | The go token accepts impossible dates (`2026-13-45`). |
| n6 | NOTE | T l.503-504 | B-1 reading: "not above the floor" should mean both floors, the screen's and the verdict's, each a fail. |
| n7 | NOTE | — | `go_problems` is [] on master's and wt-lit's logs. `declared_scope` is {} on the main tree. No membership event exists yet. |

---

## 1 (MATERIAL). B-3 residue: the problems raised by exact go tokens can never be cleared

**Where.**
- GT l.138-147: the five problems raised by an *exact* token (no pin strictly before it, another sha, after its
  closing row, a second go row) are appended with no check for a void.
- l.134: a malformed row is cleared only `if voided_later(row, i) and not RD.PIN.search(line)`.
- l.104-106 and 114-115: `voids.setdefault(target, pos)` keeps only the **first** void naming a row.

**Evidence.** `probe_go2.py`, with master's reader. Every log below is clean to the reader, has one go problem, and
gives `go_row_present` False with `membership` refused, even after the void:

| log | the problem that stays |
|---|---|
| R1: a go row at a wrong sha, `heldout-void` of it, then a correct go row | "at a sha256 that is not its first pin's" |
| R2: a go row for F-31 (a typo for F-13), void, correct go row | "with no pin strictly before it" |
| R3: a second go row for F-13, void of it | "a second go token for F-13" |
| R4: a go row after F-13's closing row, void of it | "after its closing row" |
| R5: a go row written into its own pin row, void | "no pin strictly before it" |
| R6: a malformed go row (39-hex runner) carrying another declaration's pin, void | "go-like but not exactly" |
| R7: a mistyped `heldout-void: E-902` written before E-902 exists, then a malformed E-902, then a proper void | "go-like but not exactly" |

**The failure it allows.**
- **Input:** the likeliest slips when writing a go row. Examples: the sha of the CRLF bytes or of a pre-final draft
  (R1), a mistyped F-number (R2), or a later row that restates the token (R3).
- **Output:**
  - `go_problems` is never empty again;
  - `membership` refuses;
  - `go_row_present` is False for every declaration, so no design-search survey can ever start;
  - the gatekeeper cannot read F-HT's membership by code.
- **Effect:** fail closed and permanent in an append-only log. It contradicts T l.651-655: "a go-like row that is not
  exactly the token is a hygiene problem that refuses every membership reading until a later `heldout-void` ... row
  voids it ...; **so are a go row for a closed search and a second go row for one declaration**". It is also the only
  route TT's own fixture takes: TT's E-903 row is a go row carrying a pin, the R6 shape. Once n-a pins this file,
  fixing it means pinning both templates again.

**Remedy.** These are code changes, plus tests:
1. In `_scan`, before appending any problem for a token that is not counted (l.140-147), add
   `if voided_later(row, i): continue`. A void of a **counted** token stays a no-op, because the counted branch
   (l.148-150) never checks voids.
2. Drop `and not RD.PIN.search(line)` at l.134. GT reads pins in `_first_pins` without regard to voids, so a void
   never unpins anything. The reader's reason for the clause, that a void never voids a pin row, does not apply.
3. Make a void count if **any** void of that row comes after it: `voids[row]` becomes a list, and the check is
   `any(p > i for p in voids[row])`.
4. TT: R1 to R7 each recover after a void, while a void of the counted token, and a void of a pin row, still leave
   membership unchanged.

## 2 (MINOR). U-1's runner commit is not bound in code, and the literal reading cannot hold

**Where.**
- GT l.180-194: `go_row_present(text, decl, sha, root)` takes no HEAD. `go_runner` (l.167-172) is an accessor that
  nothing calls.
- T l.656-660: "the survey and every round run on that runner commit, bound by its sha".
- T l.669-672: the refusal list names only `go_row_present`.

**Evidence.**
- The go row names the runner commit, so it is committed after that commit. A clean checkout of the runner commit
  therefore holds a `DECISIONS.md` without the go row, and `go_row_present` on that checkout's log is False.
- A runner built from the text must do one of two things:
  - read the log from outside its checkout, so the survey runs on the runner commit but nothing binds the log; or
  - run on a later commit, which "on that runner commit" forbids and no code compares.
- **Attack (4)'s answer: yes.** A go row can name runner X while the survey and the rounds run on Y, with no refusal.
  The rounds come after round results are seen, so a change to the deciding code between rounds is a choice made
  after outcomes, and U-1 is its only guard.

**Remedy.**
- Use the hold-commit pattern this repository already has (`extended/cl_reading.py` l.1136-1150).
- `go_row_present(text, decl, sha, root, head)` also requires that `head` descends from `go_runner(...)`, and that
  every deciding path is byte-identical at `head` and at the runner commit. The deciding paths are a list the
  declaration fixes, at least the survey runner, the engine adapters, `extended/go_token.py` and `extended/reader.py`.
- T step 4 says the survey reads the checkout's own log, at a commit after the go row, held to the runner commit by
  those paths.
- TT probes: a mismatched head, and a changed deciding file.

## 3 (MINOR). A malformed closing row is invisible, and a go row after it counts

**Where.**
- GT l.60-61: `CLOSED_TOKEN`'s cause is any `[a-z-]+`.
- GT l.107-111: only exact closing rows are read, and nothing flags one that only looks like a closing row.
- The reader's `HELDOUT_TOKEN_LIKE` does not cover `closed` either.

**Evidence** (`probe_go2.py`):
- **C1:** `heldout-closed: F-13 @ <sha> -- power gate failed -- x` (spaces in the cause), then a go row for F-13.
  There are no problems, `go_row_present` is True, and membership is `('E-902', {'Topstep': 'F-13'})`.
- **C4:** the same with `Heldout-closed:`.
- **C2:** cause `preference` is accepted as a closing row.
- Mutant g27 (any cause text) and mutant g29 (fenced closing rows counted) both survive.

**The failure it allows.**
- A search closed with a one-character slip still has its go row counted.
- That go row fixes the membership event, so every firm not yet pinned goes to state (c).
- The closed search's survey runs. C-3 (i) is back.

**Remedy.**
- Treat a third cell that looks like a closing row (`heldout[-_ ]?closed\s*[:=]`, any case, after marks) as a
  hygiene problem unless it is exactly `CLOSED_TOKEN` with a cause among HT's eight. It can be voided, as in finding
  1.
- TT probes C1, C2 and C4, and a fenced closing row.

## 4 (MINOR). The scope still fails open on forms that are not listed

**Where.**
- GT l.66: `_MARKET_LINE` accepts any upper-case code, and l.73 `_NQ = {"NQ", "MNQ"}`.
- GT l.71: `_FIRM_NAMES` refuses only names that contain the fragments `topstep`, `funded futures`, `mffu` or `lucid`.
- GT l.225-227: a file is a design search only by the exact marker at a line's start, or by three numbered headings.
- GT l.262: `declared_scope` looks for the marker on **all** lines, but `scope_problems` looks only at unfenced ones.

**Evidence** (`probe_scope2.py`). Each draft is made from T by filling the two fields. `scope = {}` and
`go_row_present = True` for each of these:
- market `NQZ6`, `NQH26`, `ENQ` or `NQQ`;
- firm `MFF`, `Top step`, `MyFundedFutures` or `TS`;
- the firm field left as `<firm, plan>`;
- the marker in a blockquote, or `**Declaration kind: design search**.`, in each case with headings 5 to 7
  renumbered.

Also:
- `Lucid, Topstep 50K` is read as `{'F-20': 'Lucid'}`: two firms pass.
- A file whose only marker is inside a fence, with unfenced field lines and no headings, is read as
  `{'F-20': 'Topstep'}`: a file that is not a design search is put in scope.
- Mutants g11 (two firm lines), g24 (fenced marker), g31 (two files) and g33 (marker anywhere in the line) survive.

**The failure it allows.** Topstep's NQ search is pinned with firm `Top step, 50K`, or with market `NQZ6`. Its go row
is valid, so its survey runs. The membership event is never fixed, and MFFU or Lucid can pin after seeing Topstep's
search-year results. That is H-1''s hole through a typo. The lead's reading, that firm names count only in their exact
form, is kept. But a form that is not exact must then be **refused**, not quietly dropped from the scope.

**Remedy.** Fail closed by listing what is allowed, not by blacklisting fragments:
- The market must be one of the reader's or the data's known market codes, else refused.
- The firm field must be exactly a `FIRMS` key, or exactly an entry of a declared list of firms outside the line
  (Apex, Tradeify, ...), else refused.
- No second firm name may appear in the firm field.
- Every `prereg/F-*.md` pinned after the template carries exactly one known `Declaration kind` marker at a line's
  start. Any line containing `declaration kind`, in any case or emphasis, that is not exactly a known marker is
  refused.
- l.262 reads unfenced lines only.
- TT probes each row above.

## 5 (MINOR). C-5: the end can be chosen again after the finalists, and parts of the rule cannot be checked

**Where.**
- HT l.132-134 and l.195-197, T l.117-119 and l.728-730: the rule as ruled.
- TT l.2104 `_cw_problems`: an NQ window row from 2026-07-17 must come before the first finalists' token.
- GK l.98: item 2 does not carry the rule.

**Evidence and failure.**
- **(a) A later window row re-chooses the end.** `probe_cw.py` builds a window row, the finalists' row, then
  `heldout-window: NQ 2026-07-17 to 2026-10-30`. `_cw_problems` gives [] and the reader gives no problem.
  `RD.heldout_window(log, "NQ", 2026-07-20, 2026-08-01)` returns the **later** row, so the newest window governs. The
  same holds for an overlapping row starting 2026-07-20. Nothing stops the end from being re-cut after a carried
  design's confirmation has been read. That would be optional stopping on the confirmation, which the text forbids
  ("never chosen with a finalist known") but no check refuses. The reader still refuses every read from 2026-07-17 on,
  so this only bites once a decision row opens the confirmation.
- **(b) "Never chosen with a finalist known" cannot be enforced as worded.** A member's finalists exist in its result
  files before its finalists' token is written, and the window row may be written in between.
- **(c) The end "as purchased" ties the purchase to the finalists.** The purchase must come before the first
  finalists' token, F-HT's held-out row included, because `_cw_problems` counts every finalists' token. Until the
  operator buys, no member can record its finalists. Also, "the last complete NQ session" can only be learned by
  looking at bars from 2026-07-17, unless it is taken from the order.
- **(d)** The gatekeeper has no item that refuses a finalists' row without the window row.

**Remedy.**
- **The first row governs.** The first `heldout-window` row for NQ starting 2026-07-17 governs. Any later NQ window row
  touching 2026-07-17 or after is refused, in `_cw_problems` (better, in the reader's hygiene) and in GK's held-out
  item 2.
- **The end comes from the order.** It is the last session in the vendor order's stated range, never read from bars.
- **The purchase is the operator's task.** State in T section 15 and `docs/OPERATOR_SETUP.md` that the purchase comes
  before the first finalists' token.
- **"With a finalist known".** Either reword it as "fixed by the purchase, which may follow a member's search-year
  results and moves only the confirmation's power", or move the row to before the membership event. Moving it is the
  lead's call, because it changes the ruling.

## 6 (MINOR). C-4 bounds when the check was written, not when the defect began

**Where.** HT l.100-104: "a failed check on record ..., committed at or before the membership event's commit, or one
of the search's own declared refusals or identities, ... the auditor's note confirming that it cannot be fixed without
changing a declared input".

**The failure it allows.**
- **Input:** after Topstep's finalists, the loader is tightened. An old test, committed long before the event, now
  fails on a key MFFU declared ("a firm key the loader now refuses").
- **Why the text accepts it:** the check is dated before the event, and changing the key would change a declared
  input.
- **The guard it rests on:** only the auditor's judgement, that reverting the loader (not a declared input) would fix
  it.
- **Output:** MFFU closes `defect-on-record`. That is W-1's drop by another route: it raises the later places' power
  and changes the joint list. It does not change the level.

**Remedy.** Add "**and failing when run at the search's go-row runner commit**, the commit it ran on". The defect then
existed when the search ran, and later edits elsewhere cannot create it. This tightens the ruling and changes nothing
else. Needle it.

## 7 (MINOR). B-2: "another market's bars" admits MNQ's held-out years

**Where.** T l.99-101, HT l.111-112, GK l.93-95: "NQ bars after the confirmation window's end, or another market's bars
that no declaration here has read; never NQ's search years, held-out years or confirmation window".

**Evidence.**
- The lead accepted that MNQ is in NQ's scope, as one underlying (GT l.72-73; MFFU's `hedging_rule` counts NQ and MNQ
  as one).
- MNQ 2024-01-02 to 2026-07-16, once purchased, is "another market's bars that no declaration here has read", yet it
  is NQ's held-out years tick for tick.
- The reader keys rule 2 by market code, so a non-member family would be the first to read MNQ's window, and the
  reader would allow it.
- "Here" in a declaration can mean "this file".

**Remedy.**
- Change the wording to: "another underlying's bars that no declaration of this repository has read (NQ and MNQ are
  one underlying); never NQ's or MNQ's search years, held-out years or confirmation window".
- Make the same change in all three copies, and in `DEF_NEVER_READ`.

## 8 (MINOR). n-a pins `go_token.py`, but not the reader rules it imports

**Where.**
- GT l.51-62 imports `RD._HO_HEAD`, `_HO_TAIL`, `_HO_THIRD_CELL`, `_HO_MARKS`, `_fence_state`, `ROW`, `PIN` and
  `heldout_tokens`.
- DF l.58 pins only `extended/go_token.py`.

**Evidence.**
- **A rename fails loudly.** A missing name raises at import, so every caller crashes. That is safe.
- **A change in meaning does not.** I ran seven reader mutants against TT and DF, with GT's sha unchanged:
  - five are killed by TT's battery: r01 four-space fences, r02 a looser tail, r03 marks reduced to spaces, r04 fence
    recovery off, r05 a strict `ROW`;
  - two survive: r06 `PIN` accepting upper-case hex, and r07 the void without its tail.
- The membership rule can therefore change after the pin with `go_token.py`'s sha256 unchanged.
- TT l.2039, `GT.fences(log)[0] == RD._fence_state(log)[0]`, is a tautology, because `GT.fences` *is* the reader's
  function.

**Remedy.**
- Commit a golden fixture: the battery's logs and the probes R1 to R7, C1 to C4 and M1 to M8, with their expected
  `go_problems`, `membership` and `go_row_present`.
- Pin it by sha256 in the template pin row beside `go_token.py`, and replay it in TT.
- Alternatively, or as well, give the reader public aliases for the names GT uses, with a reader test that lists them
  as GT's dependencies.

## 9 (MINOR). n-b's W42-R1 pin is any mention of the file's sha

**Where.** DF l.59 and l.70: `_W42_PIN.search(ln)` on every line, whether fenced, inside a row or not, and with the sha
never compared with the file.

**Evidence.**
- No test hashes `docs/plans/WAVE42_SETTING_RULE.md` or `extended/wave42.py` (DF's other pins cover only `prereg/F|RD`,
  `config/`, `docs/calibration/` and playbook JSON).
- So an earlier row that cites a draft's sha, or a fenced quotation, satisfies "W42-R1 first".
- The earlier remedy, that TT asserts `extended/wave42.py` exposes `DO_NOTHING_EPS` and `do_nothing_floor` once a
  template is pinned, is not in the diff.
- `extended/wave42.py` is not on daff8cc, and no template pin row exists yet, so the test passes vacuously today.

**Remedy.**
- Count a W42 pin only on an unfenced decision row, with its sha matching the file at the root.
- When a template pin row exists, require that `extended/wave42.py` is present and exposes those two names.

## 10 (MINOR). Mutation: 10 of 59 survive

`mutate2.py` applies one replacement each, then runs TT and DF with `-x`. The control passes (68 passed).

| killed (49) | surviving (10) |
|---|---|
| g01 same-row pin; g02 sha; g03 closing row; g04 second go; g05, g06 present after finalists or closing; g07 scope; g08 file hash; g09 MNQ; g10 two market lines; g12 inexact firm; g13 fenced market line; g14 fenced go; g16 premature void; g17 unclosed fence; g18 `Go:`; g19 runner optional; g20 event scope; g21 R-1; g22 pin at the event; g23 refusal; g25 headings; g26 `TopstepX`; g28 `go_runner`; g32 lower-case market; t01 to t15 (B-1, C-4 x3, C-5 x2, n-c x2, B-2, C-1, B-3, C-3, the runner form, n-a, the firm sentence); d01 to d04; r01 to r05 | **g11** two firm lines; **g15** pin rows voidable (by design: finding 1 removes the clause); **g24** fenced marker marks; **g27** any cause text; **g29** fenced closing rows count; **g30** fenced pins count; **g31** two files for one F-number; **g33** marker anywhere; **r06** reader `PIN` upper hex; **r07** reader void without its tail |

**Remedy.**
- Add probes for g11, g24, g27, g29, g30, g31 and g33.
- g30 matters most: a fenced quotation of a draft's pin must never become the first pin. If it did, the real go row
  would fall to finding 1's sha problem.
- Kill r06 and r07 with finding 8's golden fixture.

## Notes

- **n1. The reader's own deadlocks**, outside this diff and shared by GT:
  - a voided malformed held-out row that carries a pin;
  - a stray fence after a heading or prose line, which no void can close (probe R8; the reader reports 2 problems);
  - a first void that hides a later one.
  These are the reader's owner's.
- **n2. The window row's meaning.** The confirmation is recorded in a `heldout-window` row, which the reader's rules 2
  and 3 treat as a **new held-out window**: a registered design's read of it needs a counted verdict for that window.
  The decision row that one day opens the confirmation must say that this window is a confirmation and not a second
  held-out test.
- **n3. GK l.253.** The phrase "exit (B) cites it" is repeated. A k > 20 re-statement "from the go row's runner commit"
  needs a gate whose k is an input, not a range fixed in code: a build requirement.
- **n4. T l.101-103** (unchanged context). "A later search on the same bars reads NQ's held-out years and F-HT's
  results as a description only" should add "after F-HT's verdict row (reader rule 4)".
- **n5. GT l.57.** `\d{4}-\d{2}-\d{2}` accepts `2026-13-45` (probe M1). The reader's window token checks real dates;
  the go token could too.
- **n6. B-1 reading.** "A planted design not above the floor counts as a fail" should read as both of section 10 (c)'s
  floors: the screen's on the search years and the verdict's on the held-out years. No power-gate code exists yet
  (`extended/three_way_stats.py` `power_of` on wt-firmpath has no floor), so this is a build requirement.
- **n7. The real logs.** `go_problems` is [] and the reader is clean on master's `DECISIONS.md` (the main tree) and on
  daff8cc's. `go_tokens` is [] and `declared_scope` is {}. No go row or template pin row exists, so every fix can land
  before the pin.

## What I tried that found nothing

- **B-1.** The new phrase is in T section 9. "Counted only over" is gone from T, HT and GK, with a bad needle. HT
  section 6 inherits the gate's power unchanged. A search for other conditional wording (power ... above, over, among
  or conditional ... floor) in the tree outside reviews and `vendor/` finds nothing. No power-gate code exists to count
  over a subset.
- **B-2 for NQ itself.** In all three copies the definition excludes NQ's search years, held-out years and
  confirmation window, and the old clauses ("as ledgered", "end date declared", "never read for a non-member") are
  gone, each with a bad needle. The reader still refuses every read from 2026-07-17 on.
- **B-3, what is fixed:**
  - GT uses the reader's `_fence_state`, `ROW`, `PIN`, `_HO_*` and void token.
  - A void of a counted go row, of a pin row or of a valid finalists' row does nothing.
  - A stray fence after a row clears as the reader clears it.
  - A fenced quotation of the go row, voided, clears.
  - CRLF, CR-only and mixed trailing-CR logs agree with the reader (M3 to M5).
  - `Go:` and `go :` are problems.
  - An NBSP after `go:` is a problem (fail closed).
  - An HTML comment is read as the reader reads it (n-d, as ruled).
- **C-1, the listed cases.** All of TT's twenty cases behave as listed, as do my df7ab29 table's: backticks, bold,
  lower case, two codes, `TopstepX`, `Lucid Trading`, a renamed field, two market lines, a rewritten marker, and a
  fenced `ES` line above the real one, which is now read correctly. `go_row_present` refuses whenever the scope
  refuses.
- **C-3's other parts.** A go row after a valid closing row is a problem. A second go row is a problem. After a
  finalists' or closing row, `go_row_present` is False. `go_runner` returns the runner sub-form.
- **C-4, as ruled.** The three clauses (at or before the event, or declared; cannot be fixed; counted) are in HT cause 8,
  in T step 4 and in GK, needled, and modelled in `_firm_states`, where each piece is required.
- **C-5, as ruled.** The rule's text is in T sections 2 and 15 and in HT sections 5 and 8. `_cw_problems` refuses a
  finalists' token with no window row before it, or with a window not starting 2026-07-17.
- **n-a and n-b, as described.** DF refuses a template pin row without `go_token.py`'s sha, with an edited
  `go_token.py`, with an edited template, or before a W42 mention (d01 to d04 killed). The real log passes,
  vacuously, because no template pin row exists yet.
- **n-c.** The clause is in T section 9, T section 13, HT section 6 and GK, needled (t07 and t08 killed).

## What I could not check

- **The survey runner's call.** No survey runner calls `go_row_present` or `go_runner` on wt-lit. The v3 runner on
  wt-survey (5c5cb93) does not reference `go_token`.
- **W42-R1's pin.** Neither its pin row nor `extended/wave42.py` is on master or daff8cc, so n-b's live check is
  untested.
- **Which market codes the reader and the data know.** The allowed list in finding 4 needs the lead to name its source,
  for example `config/windows.yaml` or the bars' directory.
- **Power-gate code.** None exists to check against B-1's reading (n6).
