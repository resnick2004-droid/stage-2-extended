# Red team: the reader's go-token rules (Q-212) and the templates resting on them

**Reviewer:** red team, 2026-11-22.

**Targets**
- **Reader:** `wt/wt-verify`, `git diff 462fbc3 51384fe -- extended/reader.py tests/`, master merges skipped. That covers
  0e2d9ab (Q-194f), a4bd24c (Q-179, `SUPERSEDED`) and 51384fe (Q-212). Reader line numbers below are at 51384fe.
- **Templates:** `wt/wt-lit` 0fb43a0: `prereg/TEMPLATE_design_search.md` (T), `prereg/TEMPLATE_heldout_test.md` (HT),
  `.claude/agents/prereg-gatekeeper.md` (GK) and `tests/test_declarations_fixed.py` (DF). Line numbers are at 0fb43a0.
  wt-lit's working tree holds uncommitted edits: the two pending items, a deciding-files line and MFFU's exact form. I
  read the committed blobs and report neither pending item.

**What the brief hints at.** The brief says "g33 is claimed unkillable". I tested that claim rather than taking it
(section 7).

**Method**
- **Checkouts.** Three detached checkouts under `%LOCALAPPDATA%\stage2-extended-runs\rt-q212\`: `reader` (51384fe),
  `lit` (0fb43a0) and `mut` (51384fe, for mutants), made with `git worktree add --detach`, with no data junctions.
  All three were removed at the end and `git worktree prune` was run. wt-verify's `git status` is empty. wt-lit shows
  only its worker's own three uncommitted files, which were there before I started.
- **Probes,** under `scratchpad\rt_q212\`, synthetic logs, files and git trees only:
  - `probe_perm.py`: a search for permanent states;
  - `probe_count.py`: counting and scope;
  - `probe_verdict.py`: Q-194f's commit search;
  - `probe_real.py`: the real logs;
  - `g33_equiv.py`: whether g33 is equivalent;
  - `mutate.py`, `mutate2.py`, `mutate3.py`: 64 one-line mutants.
- **What I read and quote.** No bars, no atlas, no result file, nothing from 2026-07-17 on. No seed literal is quoted.
- **Tests.** Every run used `OMP_NUM_THREADS=1` and a timeout:
  - control on `reader`: `tests/test_reader_go.py`, `test_reader_q194f.py` and `test_reader_superseded.py`, 130 passed
    (28 s);
  - on `lit`: DF and `tests/test_design_search_template.py` pass, with 1 skip, the Q-212 names test, because that
    tree's reader predates Q-212.

## Verdict: **BLOCK**, narrowly, on the template side. The reader passes with minors

**What blocks.** DF's new template-pin check (finding 1) is a permanent state:
- Once the template pin row exists, any later change to `extended/reader.py` fails the fast tier for good.
- A re-pin under a new row does not clear it, because the old row is still checked.
- The confirmation window cannot be read without a reader change (`span` refuses every read from 2026-07-17 on), so
  this check collides with a change the program must make.
- The fix is a few lines in DF and must land before the pin.

**The reader's new rules hold under attack.**
- **(1) Permanence.** No reachable log state is permanent: 251 generated states, each recoverable by at most three
  appended rows.
- **(2) Counting.** Every listed fault refuses, but the binding trusts its caller (finding 2).
- **(3) The membership event.** It is exactly the first counted in-scope go row, but it is recomputed from today's
  `prereg/`, not fixed (finding 3).
- **(4) Supersession.** Every judged-block route for RD-01 to RD-04 refuses. RD-05's part F is not covered
  (finding 7).
- **(5) The verdict order.** Q-194f holds across merges and octopus merges, but not across a binary blob or a replace
  ref (finding 8).
- **(8) The real logs.** Clean.

**Counts: 0 CHANGES-A-CONCLUSION, 1 MATERIAL, 9 MINOR, 6 NOTE.**

| # | label | side | file:line | one line |
|---|---|---|---|---|
| 1 | MATERIAL | template | DF l.80-97 | The template pin row freezes `extended/reader.py` for good: every template pin row, old ones included, must still hash to today's reader, so any later reader change (the confirmation window's opening among them) fails the fast tier permanently |
| 2 | MINOR | reader | reader l.2015-2049 | `go_row_present` binds the tree the caller's `declaration_path` lies in and the log text the caller passes, not the running checkout's committed log. An uncommitted go row passes. A nested `prereg/` dodges the working-tree check. skip-worktree and assume-unchanged hide an edited deciding file |
| 3 | MINOR | reader + HT | reader l.1875-1980, 2000-2012; HT l.84-87 | The membership event is recomputed from today's `prereg/` and reader, never fixed. A second `prereg/F-13_*.md` plus the void that unlocks the log moves the event to a later go row, and a firm pinned after the true event becomes a member |
| 4 | MINOR | reader | reader l.1790, 1866-1868 | "No second firm in the field" is a blacklist of eight names. `Topstep, 50K Combine and Alpha Futures 50K`, `Topstep, 50K (via MFF)` and `... Elite Trader Funding` are in scope |
| 5 | MINOR | reader | reader l.773, 820-825, 1878 | `str.splitlines` splits on U+2028, U+0085, FF, VT and FS/GS/RS, which git and CommonMark do not. A go row, a pin or a finalists' token placed mid-line after one of them counts |
| 6 | MINOR | reader | reader l.2030-2034 | A malformed finalists' row for the search leaves `go_row_present` True: rounds can go on after finalists were meant to be recorded. A malformed closing row stops them; the two are asymmetric |
| 7 | MINOR | reader | reader l.164-167, 346-357 | E-271 supersedes RD-05's part F, but RD-05's three judged purposes (all part F's) still authorise. The docstring says the list holds "RD-05's part F". Search-year supersession is nominal: `declaration="E-080"` or `None` is allowed |
| 8 | MINOR | reader | reader l.1119-1143 | `_verdict_commits` cannot see a commit whose DECISIONS.md blob git calls binary, and it honours replace refs. A verdict token committed before the read and then edited in place to new bytes is also not seen |
| 9 | MINOR | template (or reader) | T l.99-103; HT l.110-115; GK l.94-96 | The successor route "another underlying's bars" can never run: the reader's allow-list makes any non-NQ/MNQ go row a problem that locks every survey until voided, and a voided go row never counts |
| 10 | MINOR (mutation) | reader tests | `tests/go_cases.py`, `tests/test_reader_go.py` | Of 64 mutants, 13 survive: 10 are test gaps (m10, m12, m20, m29, m32, m53, m55, m59, m60, m47b) and 3 are equivalent (g33, m37, m45b). g33 is equivalent while the variant rule stands (0 of 145 inputs differ), but the variant rule itself is untested (m29 changes 16 inputs) |
| n1 | NOTE | template | TT l.1893-1936; reader `heldout_window` | C-5's "any later NQ window row ... is refused" is TT's `_cw_problems` on the real log. The reader still takes the newest window, and an MNQ window row escapes `_cw_problems` |
| n2 | NOTE | template | T l.46-49; HT l.72-73; GK l.89-92 | "Refused at the pin" (scope, and one member per firm) has no code at the pin. The reader refuses only at the go row; the rest is GK's reading |
| n3 | NOTE | reader | reader l.1788; ruling n-d | Free text after the market's ` -- ` (`NQ -- and ES on the same days`) is in scope. Field lines inside an HTML comment are read while the rendered page shows another market |
| n4 | NOTE | reader | reader l.2000-2011 | `membership_event`'s default `prereg_dir` is the reader module's own `ROOT/prereg`, not the tree the log came from |
| n5 | NOTE | — | — | No reachable state is permanent (attack 1): 251 states. A fence opened before any row clears by an appended closer |
| n6 | NOTE | — | — | The real logs are clean (master 6502d87, wt-verify 51384fe, wt-lit 0fb43a0): no go or held-out problem, no fence, no event, no hidden line break; `pins` matches DF's regex |

---

## 1 (MATERIAL, template-side). DF freezes the reader at the template pin, for good

**Where.** DF l.80-97, `_template_pin_problems`:
- for **every** unfenced row carrying a template pin (`rows`), each `extended/reader.py` sha256 on it must equal
  `_lf(root / "extended/reader.py")` today (l.94-96);
- `test_the_templates_pin_row_carries_the_reader_and_follows_w42r1` asserts `[]` on the real log.

**Evidence** (the synthetic tree, DF's own function):

| state | DF's output |
|---|---|
| templates pinned with reader `r1` | `[]` |
| the reader then changed | `['line 2: extended/reader.py does not hash to its pin (n-a)']` |
| a new row re-pinning the templates at the new reader | the same line 2 problem: the old row is still checked |

**The failure it allows.**
- **Input:** any commit to `extended/reader.py` after the template pin row: a bug fix, the rule that opens the
  confirmation window, a C-5 rule in the reader (n1), or finding 2's or 5's fix.
- **Output:** the fast tier fails on that commit and on every later one. The pre-commit hook then either refuses the
  commit, freezing the reader, or the test must be weakened, which is a safeguard change E-207 does not cover.
- **Why the confirmation needs a change:** the reader refuses every read from 2026-07-17 on, "whatever the purpose or
  declaration" (`span`). The program's own confirmation window (T section 15, HT section 8) therefore needs a reader
  change after the templates are pinned. The pin as written makes the confirmation unreachable without a weakened test.
- **What it adds:** nothing a search needs. Each search's reader is already bound per search: `extended/reader.py` is a
  required deciding file, byte-identical at the go row's runner commit (reader l.1831, 2041-2049).

**Remedy, either of these:**
- **(a)** Check each template pin row's reader sha256 against the reader **as committed at that row's commit**
  (`git log -S` on the row, then `git show <commit>:extended/reader.py`), not against the working tree. Then require
  that the newest template pin row, if older than the current reader, be followed by a re-pin row before any new go
  row.
- **(b)** Pin the go token's behaviour, not the reader's bytes: pin `tests/data/go_token_golden.json` by sha256 in the
  template row, and have DF replay it against today's reader.

Either way:
- the template phrase "`extended/reader.py` at its pinning row's sha256" should read "at the go row's runner commit"
  for a search;
- the membership event should be recorded at the moment it occurs (finding 3), so that a later reader cannot move it.

## 2 (MINOR, reader-side). `go_row_present` trusts its caller for the tree and for the log

**Where.** reader l.2015-2049:
- `root = p.parent.parent` comes from `declaration_path`;
- `log_text` is whatever the caller passes;
- the working tree is checked by `git diff --quiet HEAD -- <deciding>`, run with `-C root`.

**Evidence** (`probe_count.py` and a nested-path check):

| case | `go_row_present` |
|---|---|
| HEAD's `DECISIONS.md` has no go row, and a log string holding one is passed | True |
| a deciding file edited in the working tree | False (correct) |
| the same edit, marked `--skip-worktree` | True |
| the same edit, marked `--assume-unchanged` | True |
| the declaration passed as `<tree>/x/prereg/F-13_x.md` (root `<tree>/x`), with `scripts/survey.py` dirty at the repository top | True |

**Why the nested case passes.** `_blob` reads paths from the repository's top, but the diff pathspec is relative to
`<tree>/x`, so it names files that do not exist.

**The failure it allows.**
- A survey round starts on an uncommitted go row, or on one present only in another tree's log.
- A runner run from checkout A passes checkout B's declaration path, and A's own code is never compared with the runner
  commit.
- T l.661-664 promises more: "the survey reads its own checkout's log, at a commit after the go row, bound as the
  reader binds it".

**Remedy.**
- Bind to the **running** checkout: `ROOT` of the imported reader, or require
  `git rev-parse --show-toplevel == p.parents[1]`.
- Read the log as `git show HEAD:DECISIONS.md` and require the working-tree `DECISIONS.md` to be byte-equal to it
  (drop `log_text`, or assert it equals HEAD's).
- Compare each deciding file's working-tree bytes with the HEAD blob directly (`git hash-object --path=<p> <p>`), not
  through `git diff`, which honours the skip-worktree and assume-unchanged flags.
- Add tests for the four True cases above.

## 3 (MINOR, reader and HT). The membership event is recomputed, not fixed

**Where.**
- reader l.1875-1980: a pin counts only while `prereg/<F>_*.md` is exactly one file hashing to it, and a go row's
  scope is read from today's file.
- l.2000-2012: `membership_event` recomputes all of it at every call.
- HT l.84-87: "This F-HT's membership is fixed at that moment". No row records the moment.

**Evidence** (`probe_count.py`). Log: P13, G13 (E-902), P14 (pinned after E-902), G14 (E-904).

| state | `membership_event` |
|---|---|
| as written | E-902 |
| a second `prereg/F-13_y.md` added, with no change to the log | refused |
| the lead voids E-902 to unlock the log | E-904, so F-14, pinned after the true event, is now before it and a member |
| the stray file removed, the void still standing | E-902 again (a void of a valid row is a no-op) |

So the event depends on the state of `prereg/` at read time. It also depends on the reader version: any change to
`design_search_problems` re-judges old go rows (see finding 1's remedy).

**The failure it allows.** This is H-1''s hole by a filesystem accident followed by the prescribed recovery. MFFU or
Lucid, pinned after Topstep's real event and after its search-year results, becomes a member. DF guards edits to
pinned files, but not a second file under the same F-number.

**Remedy.**
- At the event, the lead writes a row that records it, for example `heldout-membership: E-NNN @ <sha256 of the go
  row's line> -- <members>`; F-HT cites it; and `membership_event` refuses when its answer differs from the recorded
  row.
- Or: a go row, once counted at its own commit (judged with the reader and `prereg/` of that commit), is never
  voidable, and a later loss of its pin is a hard refusal that the lead must repair in `prereg/`, never by a void.
- Test: the four states above.

## 4 (MINOR, reader-side). The second-firm check is a blacklist

**Where.**
- reader l.1789: `_FIRM_LINE` lets anything follow `, ` or ` -- `.
- l.1790: `_FIRM_NAMES` lists only `topstep|mffu|lucid|funded futures|apex|tradeify|take profit|bulenox`.

**Evidence** (`probe_count.py`). Each of these is IN SCOPE:
- `Topstep, 50K Combine and Alpha Futures 50K`
- `Topstep, 50K (via MFF)`
- `Topstep, 50K; Elite Trader Funding`
- `Topstep -- also FundedNext`
- `Lucid, LucidFlex 50K -- shared with Earn2Trade`

**The failure it allows.** A two-firm search (R-1 refuses it) gets a counted go row and can be the membership event.
Ruling (c) asks for "exactly one firm".

**Remedy.** Allow-list the rest of the field too: `<Firm>, <plan>` where the plan is one of that firm's plan ids in the
verified record (for example `50K Combine`, `Rapid 50K`, `LucidFlex 50K`), with nothing but ` -- <text>` after it, and
refuse `and`, `;`, `/`, `+` and `via` in the plan part. Test the five cases above.

## 5 (MINOR, reader-side). Line breaks the reader sees and git does not

**Where.** `_fence_state` l.773, `_log_lines` l.820-825 and `_go_scan` l.1878 all use `str.splitlines()`.
`_verdict_commits` splits on `"\n"`.

**Evidence** (`probe_count.py`). For each of U+2028, U+0085, FF, VT and U+001E, placed in a prose row's text and
followed by a go row's text:
- git counts 2 lines; the reader counts 3;
- `membership_event` returns the hidden E-902;
- a pin row hidden the same way is in `R.pins` and pins the go row;
- a finalists' token hidden the same way is in `heldout_tokens`.

The verdict row is the exception: it fails closed, because `"+" + fragment` never equals a diff line.

**The failure it allows.**
- A token that every renderer and `git diff` shows mid-row counts as a row of its own.
- The one parser and the one display disagree on what a row is, the very thing rulings (c) and (e) key on.
- The characters arrive by pasting from PDFs and web pages (U+2028, U+0085).

**Remedy.**
- Split on `"\n"` only, stripping one trailing `"\r"`, everywhere the log is read.
- Report any line holding `  \x85\x0b\x0c\x1c-\x1e` as a hygiene problem, voidable like the others.
- Test each character.

## 6 (MINOR, reader-side). A malformed finalists' row does not stop the rounds

**Where.** reader l.2030-2034: `decl in s["finals"]` reads exact finalists' tokens only, and `go_row_present` never
looks at `heldout_token_problems`.

**Evidence.**

| row added after a counted go row | `go_row_present` | held-out problems |
|---|---|---|
| an exact finalists' row | False | 0 |
| a finalists' row with a 63-hex list | **True** | 1 |
| `Heldout-finalists:` | **True** | 1 |
| a malformed closing row | False | 0 (1 go problem) |

**The failure it allows.**
- The lead means to record the finalists, mistypes, and a further round still starts.
- That is a round after the finalists, which T step 6 forbids ("never extended").
- A malformed closing row, by contrast, stops the survey.

**Remedy.** `go_row_present` is False while `heldout_token_problems(log)` is not empty (the log's whole hygiene), or at
least while a token-like row names this declaration. Test both malformed forms.

## 7 (MINOR, reader-side). RD-05's part F is superseded but still authorises; search-year supersession is nominal

**Where.**
- reader l.346-357: `SUPERSEDED` holds RD-01 to RD-04.
- l.164-167: "The lead fills the list at the O-7 pins (RD-01, RD-02, RD-03, RD-05's part F, RD-04)".
- E-271: part F "superseded, never run under RD-05, and run under RD-09 only".
- `prereg/RD-05_firm_modes.md` l.64 and l.677: its judged-block reads are "part F only", the three purposes
  `modes_scorecard`, `modes_ladder_beside`, `modes_gate_beside`.

**Evidence.**
- `_refuse_superseded("RD-05", ...)` passes.
- RD-05's three judged purposes therefore authorise under rule 4 after NQ's verdict row, though E-271 says part F never
  runs under RD-05.
- On the search years, `authorise(..., declaration="E-080")` (RD-01's pin row) and `declaration=None` are both allowed.
  Path, id, backslash, `./`, absolute and upper-case forms are refused.

**The failure it allows.** A described reading of the held-out years, after the verdict, under a superseded part. The
docstring states a coverage the code does not have.

**Remedy.**
- Let a `SUPERSEDED` entry carry the purposes it supersedes, (path, sha256, purposes or `*`), with RD-05's three
  purposes listed.
- Resolve an E-row declaration to the pins it carries before the check.
- Say in the docstring that a search-year read needs no declaration, so supersession there binds only reads that name
  one; "never run" rests on `write_result`'s `prereg_id`.
- Test RD-05's three purposes on the judged block.

## 8 (MINOR, reader-side). Q-194f's commit search is blind to binary blobs and replace refs

**Where.** reader l.1124-1125: `git log --reverse --full-history -m -p --no-color --no-ext-diff --format=%x00%H --
DECISIONS.md`.

**Evidence** (`probe_verdict.py`).

| case | `_verdict_commits` returns | right? |
|---|---|---|
| (a) the row added on a branch, then merged | the branch commit and the merge | yes |
| (b) an evil merge that adds the row | the merge | yes |
| (c) an octopus merge that adds the row | the octopus | yes |
| (e) `.gitattributes: DECISIONS.md -diff` | `[]`, which fails closed | yes |
| (g) the row first added with a trailing CR | that first commit | yes |
| **(d)** X adds V with a NUL byte; Y drops the NUL and V; Z adds V again | `['Z']` only | no: X added V first and is not seen |
| **(f)** `git replace X X'`, where X' lacks V | `['Z']` only | no |
| **(h)** X adds `V + " "`, a valid verdict token; Y edits it to V | `['Y']` only | no: the read's check (c), "a commit whose DECISIONS.md did not yet hold the row", passes as well, since it looks for the exact bytes |

**The failure it allows.** A verdict token committed before its held-out read, hidden from the order proof by a NUL
byte, a local replace ref, or an edit in place to new bytes. That is the "committed anywhere before its read never
counts" guarantee broken. It needs a deliberate act, or an edit to an append-only log.

**Remedy.**
- Run with `git --no-replace-objects log ... --text --no-textconv --root`.
- Refuse a shallow repository (`git rev-parse --is-shallow-repository`).
- Identify the verdict's commits by the **token**, not the bytes: every commit whose patch adds a line matching
  `HELDOUT_TOKENS["verdict"]` with the same row id (or the same market, declaration and sha256) must follow the read.
  Apply the same key in `_commit_has_line` for check (c).
- Test (d), (f) and (h).

## 9 (MINOR, template-side, or the reader's). The "another underlying" successor route cannot run

**Where.**
- T l.99-103, HT l.110-115 and GK l.94-96 send a non-member successor search's candidates to "another underlying's
  bars that no declaration of this repository has read".
- The reader (l.1788-1789; ruling (c)) makes any go row whose declaration's market is not `NQ`/`MNQ`, or whose firm
  is not one of the three, a go problem.

**The failure it allows.**
- Such a successor's go row locks `go_row_present` for every survey of every firm until it is voided.
- Once voided, the go row never counts, so that search can never start.
- The templates offer a route the code forbids. A lead who follows the text locks the program with a correct row.

**Remedy.** Either:
- T, HT and GK say that a search outside NQ/MNQ needs a new decision row, and a reader rule, before its go row is
  written; or
- the reader separates "in this F-HT's scope" from "a valid design search outside it" (a declared `outside F-HT`
  marker with its own allow-list of purchased markets), so that the latter's go row counts without being a
  membership candidate.

The choice is the lead's.

## 10 (MINOR, mutation). 13 of 64 mutants survive; g33's claim checked

**How they were run.** Each mutant was run against `test_reader_go.py`, `test_reader_q194f.py` and
`test_reader_superseded.py` with `-x`. m45, m45b and m47b were run again with `test_reader_q194e.py`,
`test_reader_q194d.py` and `test_reader_q173.py` added. The file was restored after each, and `git status` was empty
at the end.

**Killed (51):**
- m02 to m07, m09, m11, m13, m14, m16 to m19, m21 to m27, m29b, m30, m31, m33, m33b, m34, m35, m35b, m36, m36b,
  m37b, m38 to m44, m45 (by the Q-194e tests), m45c, m46, m47, m48 to m52, m54, m56;
- m05 was killed once corrected; my first form was not a mutant.

**Surviving test gaps (10):**

| mutant | what it changes |
|---|---|
| m10 | a pin counts with two files for its F-number (it bites closing rows, which skip `file_problems`) |
| m12 | a closing row in its own pin's row |
| m20 | a closing row's impossible date |
| **m29** | the "Declaration kind" variant rule removed |
| m32 | a deciding path listed twice |
| m53 | two deciding-files lines |
| m55 | the go token's ` -- <text>` tail optional |
| m59 | a closing row with no pin at all |
| m60 | the absorbed closer is the first bare closer anywhere later, not the first fence-like line, so a "```python" block after a void becomes unfenced |
| m47b | supersession by bytes only: an edited RD-01 at its own path would pass a search-year read |

**Equivalent survivors (3):**
- g33, the marker accepted anywhere in a line (see the claim below);
- m37: `go_row_present`'s sha comparison is implied by the pin count;
- m45b: the verdict commits matched by substring only adds commits, so it fails closed.

**g33's claim.** `g33_equiv.py` builds the mutant in memory and compares the verdict on all 145 placements of 12
marker-like lines (0 to 2 extra lines):
- g33 alone changes the verdict on **0** of them. The claim holds: while the variant rule stands, any line holding the
  marker mid-line contains "declaration kind" and is refused by that rule.
- The variant rule removed (m29) changes the verdict on 16 of them, and the suite does not notice. An example is a
  correct marker plus a second `x **Declaration kind: design search.**` or `> ...` line.
- g33 and m29 together change 81, and that pair is killed. So the variant rule carries g33's whole guard, untested.

**Remedy.** Add cases to `tests/go_cases.py`, one for each surviving gap, m29 first: a correct marker plus a mid-line or
blockquoted second marker, refused.

## Notes

- **n1. C-5 lives in a template test, not in the reader.** TT's `_cw_problems` (l.1893-1936) enforces "the first window
  row governs" on the real log. The reader's `heldout_window` and `heldout_windows` take the **newest** row. When a
  reader change opens the confirmation window, that change must take the first (finding 1 makes that change
  impossible). `_cw_problems` keys on `market == "NQ"` only, so an `MNQ 2026-07-17 ...` row after the finalists
  escapes, though NQ and MNQ are one underlying (B-2).
- **n2. "Refused at the pin" has no code at the pin.** The phrase appears in T l.46-49 (scope), HT l.72-73 and GK
  l.89-92 (one member per firm). The reader refuses only the go row. A pin row of an out-of-scope or second-per-firm
  search is not flagged by any test. That is GK's reading only, and should be said so.
- **n3. Free text and HTML comments.**
  - `- **The market:** NQ -- and ES on the same days` is in scope.
  - Under ruling n-d, an HTML comment holding `- **The market:** NQ` is read, while the rendered page shows a market
    line for ES (probe: in scope).
  - These are by ruling. The gatekeeper should read the raw text.
- **n4.** `membership_event(log)` without `prereg_dir` reads the reader module's own `ROOT/prereg`, not that of the tree
  the log came from. Callers outside the repository's root get a silently different answer. Make the argument
  required.
- **n5. Attack (1), nothing permanent found.** The search covered:
  - 21 malformed rows of every token kind (finalists, window, verdict, void, read, go, closed), each after a good go
    row and before any go, with LF and CRLF, with and without a premature void;
  - 10 fence shapes: backticks, tildes, four backticks, after a row, a heading, prose, a blank line or a closed fence,
    an info string, three-space indent, two stray fences, each with four kinds of inner row;
  - 3 HTML-comment states.

  In each state the problems cleared after at most three appended rows. Even a fence opened above the first row clears
  with an appended closer and a void. Voids placed before their row, voids naming the wrong row, two voids, and a void
  of a void all behave as ruled.
- **n6. Attack (8), the real logs.** For `DECISIONS.md` on master 6502d87, wt-verify 51384fe and wt-lit 0fb43a0:
  - `go_problems`, `heldout_token_problems`: both [];
  - `membership_event`: None;
  - no fenced line;
  - no character that `splitlines` splits on and git does not;
  - no go-like or closing-like row;
  - `R.pins` equals DF's regex;
  - the counted F pins are F-01 and F-03; F-02 was never pinned, and no file is a design search yet.

## What I tried that found nothing

- **Attack (2), as listed.** Each of these refuses, by the case table and by my own probes:
  - a wrong sha;
  - an unpinned F-number;
  - a second go row;
  - a go row after a closing row;
  - a go row in its own pin's row;
  - scope faults: 39 forms refused, 6 allowed;
  - a HEAD that does not descend from the runner;
  - a deciding file changed in the working tree, or committed.

  Also refused: a go row for the held-out declaration itself, and a go row after a voided wrong-sha go of another
  search.
- **Attack (3).** `membership_event` returns the first counted go row:
  - after a voided problem row;
  - after a `withdrawn` closing row placed before any go;
  - before a later close of its own search;
  - never the last row (m39 is killed).
- **Attack (4), the judged block.** RD-01 to RD-04 are refused by path, id, backslash, `./`, absolute path,
  upper-case path, a byte-identical copy and through a `registered_design` row naming them. A one-byte-changed copy
  needs its own pin row, so it is a new declaration. Each `SUPERSEDED` sha256 equals its file's LF sha256 at the
  reviewed commit.
- **Attack (5), merges.** Q-194f holds for a branch then merge, an evil merge, an octopus merge, a trailing-CR first
  add and a `-diff` attribute (fails closed). The Q-194e tests kill m45 (no `-m`).
- **Attack (6), citations.** The names `go_problems`, `go_row_present`, `go_runner`, `membership_event` and
  `design_search_problems` exist and are exported. These match the reader:
  - the token forms;
  - the eight causes;
  - "strictly after the hash row";
  - "a void of a valid row is a no-op";
  - "False once a finalists' or closing row exists";
  - `withdrawn` only before the event;
  - "a closing row after the finalists is refused";
  - CRLF and HTML-comment handling.

  T filled with a market and a firm gives only the pending deciding-files problem. The mismatches are findings 1, 2,
  3, 9, n1 and n2.

## What I could not check

- **A survey runner's real call.** No runner calls `go_row_present` yet, so the caller-trust of finding 2 is shown on
  the function, not on a runner.
- **Two platform behaviours:** git's binary heuristic beyond a NUL byte, and `log.showRoot` or `log.follow` user
  settings (finding 8's `--root` covers the first of these settings). Windows-only case folding of `prereg/` file names
  is also unchecked.
- **The pending items' final text.** The deciding-files line and MFFU's form are in wt-lit's uncommitted tree, not at
  0fb43a0. That tree's in-progress TT test expects `design_search_problems(draft) == []` for a filled template, which
  fits the reader as reviewed.
