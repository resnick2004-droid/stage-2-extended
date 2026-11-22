# Red-team full read: the design-search and held-out test templates, text v3 (wt/wt-lit 13df998)

**Reviewer:** red team, 2026-11-21 (machine date 2026-11-20).

**Target:** `wt/wt-lit` at 13df998, in the worktree `C:\Users\resni\AppData\Local\stage2-extended-wt\wt-lit`. I edited
nothing there. The one command I ran in it was the brief's
`timeout 600 python -m pytest -q -o addopts= tests/test_design_search_template.py`. Result: **49 passed, 1 skipped**
in 15 s. The skip is `test_m5`'s last check: "E-258 ... is not yet in DECISIONS.md on this tree". `git status` is clean
before and after.

**What I read:**
- In full: `prereg/TEMPLATE_design_search.md` (696 lines), `prereg/TEMPLATE_heldout_test.md` (158),
  `.claude/agents/prereg-gatekeeper.md` (297), `tests/test_design_search_template.py` (1448), and
  `git diff fad9461..13df998` (all four files).
- Beside them:
  - the lead's rulings (`lead\hold\template_v3_rulings.md`) and the pending rows `e257.txt` and `e258.txt`;
  - my earlier notes (V2_FULL, V2_c1, V2_c2);
  - CHARTER 3.6 (c)-(e) and 5;
  - `extended/reader.py`'s rules and tokens (l.20-120, l.190-206);
  - `tests/test_declarations_fixed.py`;
  - the design note's S2 line (l.473).

**Line references:** "T l.N" is the design-search template at 13df998, "HT l.N" the held-out template, "GK l.N" the
gatekeeper and "TT l.N" the test file.

**The brief's framing.** The brief lists points to attack and gives the lead's ruling, "at most one member search per
firm". It hints at no verdict. I took the ruling as a rule to check the text against. I did not take it as evidence
that the rule is sound.

**Probes.** All are under `scratchpad\rt_v3\`, all synthetic, and each ran in seconds. I read no bars, no atlas, no
result file, and nothing from 2026-07-17 on.
- `base\` is a `git archive` of 13df998, in CRLF; the test file reads it LF. Its test file passes there (49 + 1 skip).
- `pinready.py` runs the test file's own `_pin_ready`, `_firm_states` and `_joint_order` on the template, on master's
  working `DECISIONS.md` (which carries E-255 to E-258), and on synthetic event lists.
- `mutate_v3.py` makes 20 mutants plus 1 control, each one text replacement in `base\`. A mutant is "killed" when the
  test file fails.
- `walkgap.py` is an exact DP of the template's walk (the test's own `_walk_law`), set against barrier-rounding
  controls.

---

## Verdict: **PASS WITH MINORS** (stands with readings)

v3 answers H-1'. Membership is now fixed by an event, the first go row, that comes before any design survey can run.
State (c) is fixed at that event. An empty history is never due. Successors and post-event searches never enter. A
firm's finalists are never voided. M-5 (c) and every minor of the re-read (s-a, s-b, m-c, m-d, m-e, M-4r, N-b) are also
answered.

**Nothing I found makes the held-out test pass a design it should not.** Three findings are MATERIAL, and each is
fixed by one or two sentences and a test assertion:
- R-1: the lead's one-member ruling is not yet in the text. v3 declares the opposite rule.
- W-1: a member can be withdrawn after the event.
- CW-1: non-members are routed to the confirmation window.

The lead can make all three in the pending records batch, alongside E-257 and E-258, both still uncommitted. A diff
check is enough; no new cycle is needed.

**Why none of the three blocks:**
- None of them touches the held-out test's size.
- R-1 is the lead's own ruling, to be written in.
- W-1 can only remove a member. It cannot add one.
- CW-1 lies downstream of a purchase. The reader refuses 2026-07-17 outright (`span`, reader l.21, l.303-309).

Counts: **0 CHANGES-A-CONCLUSION, 3 MATERIAL, 8 MINOR, 7 NOTE.**

| id | label | one line |
|---|---|---|
| R-1 | MATERIAL (wording + test; the lead's ruling) | v3 provides for several member searches per firm (HT l.65-67, l.73-74, l.90-91; T l.77-78; GK l.83-85, l.194-195, l.197-198), and `_firm_states` admits a second Topstep member (probe). The exact wording change is below. |
| W-1 | MATERIAL (wording) | `withdrawn` is allowed until the member's own go row (HT l.86-88; T l.624-625; GK l.201). After the event, the lead can drop a member with another member's search-year finalists and its own power gate in hand, which re-orders the joint sequence. There is no deadline (HT l.98-99). |
| CW-1 | MATERIAL (wording; the lead's ruling) | "Its candidates go to the confirmation window under its own k" (T l.87-88, l.472; HT l.94; GK l.87, l.164) against "NQ from 2026-07-17, read once, only for a carried design" (T l.104-105, l.684; CLAUDE.md; CHARTER 5 (A)). A non-member's test can use up the carried design's fresh history, or the reverse. Neither the order nor D-107's count is ruled. |
| D-1 | MINOR | After its go row, a member closes only by causes 1-6. A defect on record (an identity failure, a rule turned `changed`, a runner bug) has no cause, so the member blocks F-HT for good or is closed under a wrong cause. |
| G-1 | MINOR | The go row, which is the event, has no token, and no code finds it. HT and GK say "by the event" while T l.86 says "before". "Any firm's design search" (HT l.72) does not limit the event to NQ searches of the three firms. |
| K-1 | MINOR | GK's k section is stale. "A search assigns its k at its held-out row", "if a draft reverses the order, its held-out run is repeated ... under a repeat row" (GK l.221-229), and the approving row "k = <k> if none takes a k first" (GK l.266) contradict T §13 ("no search holds a k") and HT §5 ("No repeat row"). TT l.483 needles hold the stale words. |
| K-2 | MINOR | The place-power re-statement is a lookup only to k = 15 (T l.486, l.592-593). Non-member searches "under its own k" can take k's first, and nothing covers k ≥ 16. |
| U-1 | MINOR | `EPS` (T l.274-275) and `WALK_MAX` (T l.311-313) have no slot in the declaration. The runner commit is not fixed between the calibration (T l.616) and the survey and rounds (T l.629-630), so the calibration may validate other code. |
| L-1 | MINOR | The baseline runner identity's window is unstated (T l.52-54). Run "path for path" over Stage 2's window, it runs the design's convention on the held-out years under `identity`. A `registered_design` held-out read is allowed by a lead's row before the verdict (T l.666-667; GK l.74-75). |
| N-1 | MINOR | 16 of 20 v3 mutants survive. Among them: HT's member definition (W8), the firm-state rule brought back as "latest member search" (W3), the closed causes' descriptions (W11, W12), T step 4's withdrawal window (W1), the last row's T (W5), and GK item 3's order (W13). |
| T-1 | MINOR | A pinned search that deletes its design-search marker escapes `_pin_ready` and the line scan (probe). `_pin_ready` also does not check that E-258's row comes before the pin row. |
| X-1 | MINOR (wording) | "them" in T l.88-90 now refers to "a member's finalists". "The line" is undefined (T l.469; GK l.161). "after any gate" is unclear on whether a failed calibration counts. E-258 (ii)'s token `-- <cause>` is not the one form `-- <cause> -- <text>`. |
| n-1 | NOTE | s-a is answered. The template's walk is 0.0003 or less from the one-tick walk, the rounded controls are 0.006 or more, and the tolerance of 0.002 sits between them. |
| n-2 | NOTE | s-b is answered by T_fill for both s and n. This changes the last row's walk horizon: still mean-zero, declared, and its share reported. |
| n-3 | NOTE | m-c is answered. `_pin_ready(template, master's log) == []`. A wrapped citation is refused, which is the fail-safe side. |
| n-4 | NOTE | When the first go row is written, and which firms pin before it, are the lead's choices. They can be informed by H4's and RD maps' search-year readings, but by no design-survey outcome. This has no effect on the level. |
| n-5 | NOTE | Place power: the product under independence understates the joint power when finalists are positively dependent. pi is one number per search (N-d, carried). The fixed sequence stops at Topstep's rank 1; a fallback procedure would keep later places' power, as an option rather than a defect. |
| n-6 | NOTE | Carried: the templates' own pins are held by no test (N-c), and T l.73-74 still lets H4 "compute" a sealed held-out output (N-e). |
| n-7 | NOTE | TT's LF check `"\r\n" not in text` (TT l.60, l.932) cannot fail, because `_text` uses `read_text`'s universal newlines. It is harmless, since every pin hashes LF-normalised bytes. |

---

## R-1 (MATERIAL). The one-member ruling: v3 declares the opposite, and the test admits it

**Where.**
- HT l.65-67: "A firm with more than one member search in state (a) ranks their finalists search by search, in the
  order of their hash rows, each in its own pinned finalist order."
- HT l.73-74: "every design search with a hash row by the event is a **member**".
- HT l.90-91: "(a) if any of its member searches is in (a); (b) if every member search of it is in (b)".
- T l.77-78: "each design search of Topstep, My Funded Futures and Lucid with a hash row by the membership event".
- GK l.83-85 (item 1), l.194-195 (item 3: "a firm's ranks its member searches' own pinned finalist orders, search by
  search in the order of their hash rows"), l.197-198 (item 4).
- TT `_firm_states` (l.1140-1200): a pin before the event is appended to `pins` whenever no earlier search of the
  firm is closed.

**Evidence** (`pinready.py`). These events:

```
pin Topstep F-13, pin Topstep F-14, pin MFFU F-15, go Topstep F-13, finalists F-13 [a1, a2], finalists F-14 [b1], closed F-15 power-gate-failed
```

give `{Topstep: (a, [a1, a2, b1]), MFFU: (b), Lucid: (c)}`, the declaration due, and the joint order
`a1, a2, b1`. No refusal. HT §1's table has one row per firm, so it already assumes one search a firm. The
multi-member sentence contradicts the table.

**The failure it allows.**
- **Input:** before the event, the lead pins a second Topstep search (for example a variant, or a 150K plan).
- **Wrong output:** Topstep brings two searches' finalists into the one test, ranked "search by search" in an order
  the lead set by the order of the pins.
- **Consequence:** a firm's place in the alternation then carries extra candidates by the lead's choice. More
  searches mean more chances to have finalists, and the ranks inside the firm are set by pin order, not by any pinned
  finalist order rule.

**Remedy: the exact wording (one block per site).**
1. **HT l.65-67.** Replace the sentence with: "**At most one member search per firm** (the lead's ruling, E-2xx): a
   second hash row for a firm before the membership event is refused at its pin, whether or not the first search is
   closed; a firm's ranks are its one member search's pinned finalist order."
2. **HT l.73-74.** Replace "every design search with a hash row by the event is a **member**" with: "each firm's one
   design search with a hash row before the event is that firm's **member** (at most one per firm)".
3. **HT l.90-91.** Replace with: "**A firm's state** is its member search's, (a) or (b); (c) if it has none."
4. **T l.77-78.** Replace "each design search of Topstep, My Funded Futures and Lucid with a hash row by" with: "the
   one design search of each of Topstep, My Funded Futures and Lucid with a hash row before". After "(H-1'; E-257)"
   add: "-- at most one per firm, a second hash row for a firm before the event refused at its pin".
5. **T §1 l.43** ("The firm and account: <firm, plan>"). Add: "**exactly one firm**; a search naming several firms is
   refused".
6. **T §14 step 2 (l.613).** After "**A search pinned after the membership event is never a member of this F-HT**
   (H-1'; E-257)." add: "**At most one member search per firm:** a second hash row for a firm before the membership
   event is refused at its pin."
7. **GK item 1 (after l.85).** Add: "**At most one member search per firm:** refuse a design search for a pin before
   the membership event when its firm already has a hash row, closed or not."
8. **GK item 3 (l.194-195).** Replace with: "a firm's ranks its one member search's own pinned finalist order".
9. **GK item 4 (l.197-198).** Replace "the members are the design searches with a hash row by the membership event"
   with: "the members are the design searches with a hash row before the membership event, at most one per firm".
10. **TT `_firm_states`.** On `pin` while `members is None` and the firm already has a pin (closed or not), raise
    `Refused`. Then:
    - assert `[pin Topstep F-13, pin Topstep F-14]` is refused;
    - add a positive control: after the event, `pin Topstep F-14` lands in `outside` (unless the no-new-pin bar
      holds);
    - needle sentences 1, 3, 6, 7 and 8;
    - add bad needles "more than one member search" and "search by search in the order of their hash rows".
11. **The record.** The ruling gets its row, or a clause in E-257 (2), before the commit.

**What the ruling means.** Before the event, every pin would be a member, so a non-member pin for a firm that already
has one is impossible. After the event, a further search of the firm may pin, outside F-HT. That asymmetry is the
ruling's intent. The text should say it so that nobody reads "refused" as "refused for good".

## W-1 (MATERIAL). Withdrawal after the event is a choice of membership after a look

**Where.**
- HT l.86-88: "`withdrawn` -- ... **only before that search's go row**; after its go row a search closes only by
  causes 1 to 6."
- Copies: T l.624-625, GK l.201.
- HT l.98-99: "never waited out by choice". No deadline is set.

**Evidence.**
- The event is the first go row of **any** search, so every other member's go row comes after it.
- Between the event and a member's own go row:
  - the first member's survey and rounds may run, and its search-year finalists may exist;
  - the member's own calibration and power gate run and are read (section 9 comes before the go row).
- With the lead's plan (all three pinned before Topstep's go row), MFFU and Lucid can each be held pinned and un-gone
  while Topstep's finalists are read, then withdrawn or sent on. `pinready.py`: `pin T, pin M, pin L, go T,
  finalists T [t1, t2], closed M withdrawn` is accepted; MFFU becomes (b) after Topstep's finalists exist.
- The placeholder variant is the same channel. Pinning a weak placeholder early buys a free keep-or-drop option,
  exercisable after the event. The one-member ruling stops a swap, but not a drop.

**The failure it allows.**
- **Input:** Topstep's search-year finalists look strong, and MFFU's power gate passed near its target.
- **What the lead does:** withdraws MFFU before its go row, with "its reason in the row".
- **Output:**
  - Lucid's rank 1 moves from place 3 to place 2, and Topstep's rank 2 from place 4 to place 3;
  - each later place's power rises by a factor 1/pi_MFFU;
  - a likely failure ahead of them is gone.
- **What it does not change:** the family-wise level. The order still reads no held-out coin draw.
- **What it does change:** which designs can be carried, by a researcher's choice made after a search-year read,
  which HT l.62 forbids ("A researcher's choice after a read is never the order").

**Remedy (one sentence each).**
1. "`withdrawn` -- only before **the membership event**; after it, a member closes only by causes 1 to 6 or by cause
   8 (D-1)."
2. Give the "never waited out" clause a checkable form: "a member's calibration and power gate run as soon as the
   run lock is free after its pin; a member with no go row or closing row N sessions after the event is a defect on
   record" (N the lead's, fixed in the row). Or, more simply: "each member's go row, or its closing row, before any
   member's survey runs".
3. TT: `withdrawn` after the event is refused.

## CW-1 (MATERIAL). Two uses of one confirmation window

**Where.**
- The non-member route: T l.87-88 ("its candidates go to the confirmation window under its own k"), T l.472 (the
  no-retry clause), HT l.94, GK l.87 and l.164.
- Against it: T l.104-105 ("never read until a carried design is registered"), T l.684 ("read once, only for a carried
  design"), CLAUDE.md ("never read until a carried candidate is registered"), and CHARTER 5 (A) ("The confirmation is
  the only test on a fresh history").
- CHARTER 3.6 (c) lets "a later search" move its held-out years to "the confirmation window, or more history" under
  its own k. So the route has a source, but its order against the carried design's confirmation is unruled.
- GK item 2 records that NQ's held-back window was spent by P-05, P-06 and P-10 (D-107's three), and that "NQ's
  reserve becomes a confirmation window only by the operator's decision".
- The reader would admit such a read through a `heldout-window: NQ 2026-07-17 to ...` row (reader l.69-71, l.85),
  once `span` stops refusing 2026-07-17.

**The failure it allows.**
- **Input:** a post-event or successor search's candidates are tested on 2026-07-17 onward under k = 14, before
  F-HT's carried design is registered.
- **Wrong output:** the carried design's "one confirmation on unread data" is then on read data, and the program's
  honesty sentence (T l.598-599) is false.
- **The reverse order:** the non-member's "held-out years" are not unread, and its k-level test is on data a carried
  design's confirmation already read.

**Remedy (the lead's sentence).** For example: "A non-member's candidates are tested only on data not yet read by any
test or confirmation: more history (the operator's setup), or the confirmation window only after every carried
design's confirmation is read there, and never before a carried design is registered or F-HT's verdict row exists;
each such test is a purchase, the operator's, and counted against D-107." Copy it to HT l.94 and GK l.87 and l.164.
Needle it.

---

## D-1 (MINOR). A member with a defect after its go row has no way out

**Where.** HT l.80-88 (the closed list); HT l.98-99.

**Evidence.** Causes 1-6 are failures of a calibration, a gate, a list or a floor. None of them covers:
- an identity that stops holding;
- a firm rule that turns `changed` or `unstated` (the loader then refuses the search's keys);
- a runner defect found by the failure protocol.

The firms change their rules often (CHARTER 3.1).

**The failure it allows.** A member stuck after its go row blocks F-HT for good. Or it is closed as
`every-design-failed-a-gate`, which records a false cause.

**Remedy.** Add "8. `defect-on-record` -- a defect named by the failure protocol, cited by its record's path and
sha256; never a preference". Hold it in TT's `CAUSES`.

## G-1 (MINOR). The event is prose, its boundary is "by" or "before", and its scope is wider than NQ

**Where.**
- HT l.72-73 ("the first go row of any firm's design search").
- HT l.73-74 and GK l.84 and l.198 say "by the event"; T l.86 says "(its hash row before the membership event)".
- T l.619 (the go row cites two hashes; no token).

**Evidence.**
- `pins()` counts any row carrying a declaration's path and sha256 (TT l.415-417 counts the go row too).
- No code finds the first go row or a closing row (n-3 of the c2 note); the event is located by reading.
- "By" admits a hash row written in the same row as the first go row.
- A fourth firm's search (`_firm_states` asserts the firm list), or another market's, would fix NQ's membership by its
  go row.

**The failure it allows.**
- Whether the event has happened, and which row it is, is the lead's reading.
- A same-row pin is a member under HT and not under T.

**Remedy.**
- Use "before" everywhere: a strictly earlier row.
- Make the event "the first go row of an NQ design search of Topstep, My Funded Futures or Lucid".
- Give the go row a positional token, for example `go: F-NN @ <sha> calibration <sha> -- <text>`, as the first text of
  its third cell.
- A small parser of `DECISIONS.md` (the pin, go, finalists and closed rows) running TT's state machine on the real log
  belongs to F-HT's build. It must hold before F-HT's pin.

## K-1 (MINOR). The gatekeeper's k section still gives a search a k, and a repeat route

**Where.**
- GK l.221-229: "**A search assigns its k at its held-out row** ... if a draft reverses the order, its held-out run is
  repeated at the new level under a repeat row. At the pin, write 'k assigned at the held-out row', state the k it
  would take ... the search must re-state its power gate's reading" and "a search withdrawn after its held-out row
  still spends its k".
- GK l.266 (the approving row): "k = <k> if none takes a k first, level 0.05 / <k(k+1)>".
- GK l.3: "its k is assigned later".
- TT l.483 needles "takes a k first", "E-005 (d)" and "re-state" in GK, which holds the stale text in place.

**Evidence.**
- T §13 says no search holds a k, and HT §5 says no repeat row is ever written for F-HT.
- The reader admits a second judged read with `repeat="E-NNN"` naming the declaration (reader l.58-60). So the only
  bar on a repeat is a sentence, and GK's text gives one.

**Remedy.**
- Rewrite GK's k section for F-HT: F-HT's k is assigned at its held-out row, and a search's pin row states "no k
  (F-HT's, k = 13 next)".
- Delete the repeat clause and say "no repeat row for F-HT, ever".
- Move the needles to the new sentences.

## K-2 (MINOR). The lookup stops at k = 15

**Where.** T l.484-486 and l.590-593.

**Evidence.** Non-member searches "under its own k", and any other declaration, can take k's before F-HT's held-out
row. A gate that reports power at k = 13, 14 and 15 cannot give the power at k = 16 without a new run. Power falls as k
rises, so k = 15 bounds nothing above it.

**Remedy.** Do one of the following:
- the gate reports power over a level grid down to a declared floor;
- no k-taking held-out row of a non-member is written before F-HT's held-out row (one sentence).

## U-1 (MINOR). Runner constants and the runner commit

**Where.**
- T l.274-275: "the runner's declared tolerance `EPS`".
- T l.311-313: "the runner's limit `WALK_MAX`".
- T l.459-461: section 9's inputs.
- T l.616-630: the calibration, then the go row, the survey and the rounds, each from "a named commit".

**Evidence.**
- Neither constant has a `<...>` slot, so a draft that omits them is not "a section left as the template wrote it",
  and GK does not refuse it.
- No sentence makes the survey's commit the calibration's.
- `WALK_MAX`'s effect is small (`walkgap.py`: 0.0006 or less in P(stop)). A different runner after calibration is not
  small in principle.

**Remedy.**
- Add slots: "`EPS`: <...>; `WALK_MAX`: <...>", in section 5 and in section 9's inputs.
- Add to the go row: "names the runner commit; the survey and rounds run from it; a change to deciding code after it
  is a new declaration".

## L-1 (MINOR). Two routes to held-out outcomes of the comparators before F-HT

**Where.** T l.52-54 (each baseline's runner identity, path for path, its window unstated); T l.666-667 and GK l.74-75
("no new `registered_design` read ... without a decision row naming it").

**Evidence.**
- The `identity` purpose reads the judged block in any tree (reader l.30-35).
- A baseline runner run under the design's convention on 2020-2026 for its identity computes the baselines' held-out
  outcomes under the deciding reading.
- Rule 3 admits a `registered_design` held-out read by a lead's row at any time.

**The failure it allows.** The baselines' held-out composite is known before the members' finalists' rows. The
finalists are rule-chosen, but the playbook text, the shapes and the no-harm margin readings are written by people.

**Remedy.**
- "Each baseline's runner identity is checked on the search years only; any held-out part compares trade times and
  brackets only, writes no outcome, and is entered in the held-out read ledger."
- "No `registered_design` read of the held-out years between the membership event and the market's verdict row", as
  the RD rule reads.

**Covered elsewhere.** The history null's blocks: the design note adopted at 181eb44 fixes "block resamples of the
search years" (S2, l.473), so that part needs no change.

## N-1 (MINOR). What the needles still miss

`mutate_v3.py` (20 mutants and a control):
- **The harness discriminates.** The control C0 ("The membership event is the first finalists' row") is killed, and so
  are W17 (T step 2's membership sentence deleted), W19 (HT: "its candidates join this F-HT at its end") and W20 (s-b's
  "decides neither s nor n" changed to "decides n").
- **16 survive.** In the core of H-1':
  - **W8:** HT "every design search with a hash row by the event is a member" changed to "with a finalists' row by the
    end".
  - **W3:** the firm state changed to "if its latest member search is in (a)", which is v2's voiding rule under a new
    word that evades the bad needle "latest pinned search counts".
  - **W2:** T "(its hash row before the membership event)" changed to "before its own go row".
  - **W9:** "no later search replaces them" changed to "unless a later search replaces them".
  - **W10:** T's "A member's finalists are never voided." deleted.
- In the closed list:
  - **W11:** cause 4 changed to "most surveyed designs failed a gate after their outcomes";
  - **W12:** cause 6 changed to "the lead judged the finalists weak".
- Elsewhere:
  - **W1:** T step 4's "`withdrawn` only before the search's go row" changed to "finalists' row";
  - **W4 and W13:** HT's and GK item 3's order changed to "in the order the lead names";
  - **W5:** the last row's T changed to "T to the realised exit";
  - **W15:** HT "To use it" changed to "when the lead judges it ready";
  - **W16:** HT §6 "or half of it after the first place";
  - **W7:** T §13's lookup changed to "a new gate run";
  - **W6 and W14:** additive retry clauses ("A lead's row may set new limits", "without a row").

The header (TT l.13-14) rightly says that needles hold sentences and that additive contradictions are for the readers.
But W8, W3, W2 and W11/W12 are **substitutions inside the rule this version exists for**.

**Remedy.**
- Needle the member definition (HT and T), the firm-state sentence, each closed cause's description (the pair, not only
  the name), T step 4's withdrawal clause, the last row's T cell, HT's "To use it" timing, and R-1's new sentences.
- Add "may set", "unless a later", "the lead names" and "judges it ready" to `FORBIDDEN_FORMS`.

## T-1 (MINOR). The reading-row check can be escaped by dropping the marker

**Where.** TT l.1377-1380 (`_pin_ready` only on files carrying `MARK_SEARCH`); TT l.983-1006 (`_line_problems`).

**Evidence** (`pinready.py`). With the marker line changed to "**Declaration kind.**" and every citation replaced by
"the lead's ruling":
- the file carries neither marker;
- `_line_problems` returns `[]`;
- `_pin_ready` would refuse it, but is never called on it.

**Remedy.**
- Every `prereg/F-NN_*.md` with NN ≥ 13 carries exactly one of the two markers (a test).
- `_pin_ready` also asserts that the cited row comes before the file's first pin row in `DECISIONS.md`.

## X-1 (MINOR). Wording

- **T l.88-90.** After v3's insert, "A later search on the same bars reads **them** as a description only" refers to
  "A member's finalists". Write "reads NQ's held-out years and F-HT's results as a description only".
- **"The line"** (T l.469; GK l.161; E-258 (iii)) is undefined. Write "every search, of any firm, whose section 7
  applies W42-R1".
- **"after any gate that read them".** Write "after any calibration or gate that read them". The calibration reads
  the whole rule (T l.475-476). This is belt-and-braces, since successors never enter F-HT.
- **E-258 (ii)** gives the closing token as `heldout-closed: F-NN @ <sha> -- <cause>`. The template's one form (N-b,
  TT l.1408-1414) is `` `heldout-closed: F-NN @ <its LF sha256> -- <cause> -- <text>` ``. Align the pending row before
  it is committed.

## Notes

- **n-1 (s-a answered).** `walkgap.py` measures |ΔP(stop)| against the one-tick walk:

  | case | the template's walk | barriers rounded | rounded inward |
  |---|---|---|---|
  | 37/55, s = 2, n = 258 | 0.00026 | 0.01438 | 0.01438 |
  | 21/43, s = 2, n = 258 | 0.00013 | 0.02161 | 0.02118 |
  | 37/55, s = 2, n = 1024 | 0.00006 | 0.01168 | 0.00812 |
  | 33/65, s = 2, n = 258 | 0.00024 | 0.01630 | 0.01630 |
  | 37/55, s = 4, n = 577 | 0.00000 | 0.01096 | 0.00579 |

  E[X²] is within 0.2 % in every case. The tolerance of 0.002 sits three times or more from each side. The test holds
  its own reading of the rule, not wt-three's runner (s-c is still with wt-three).
- **n-2 (s-b answered).** v3 takes neither remedy I offered. It sets T_fill as the walk's horizon for the last row
  too. An unscheduled exit's redraw now spans longer than the trade lived: mean-zero, booked at the run's exit time,
  and its share reported. That is a declared modelling choice, and the fill-time law reading equals the deciding one
  on that row.
- **n-3 (m-c answered).** `_pin_ready(template, master's DECISIONS.md) == []`. E-258's title begins `CHARTER's "pin"
  read`. A bare number, a deleted citation, the placeholder, or any other row is refused. A citation wrapped across a
  line is counted short and refused, which is the fail-safe side.
- **n-4 (timing of the event).** The lead decides when the first go row is written and which firms pin before it
  ("where ready"). Before the event no design survey can run (no go row), so membership reads no design outcome. It
  can read H4's baselines and the RD maps on the search years. That moves no level.
- **n-5 (place power).** The product under independence understates the joint power when finalists are positively
  dependent (one held-out history, shared baselines), so the table is conservative. pi is the search's gate power,
  one number a search (N-d, carried). The fixed sequence stops at the first failure: Topstep's rank 1 failing leaves
  MFFU and Lucid untested. A fallback or graphical procedure would keep later places' power at the same family-wise
  level. That is the lead's option, not a defect.
- **n-6 (carried).**
  - N-c: `tests/test_declarations_fixed.py` holds F-, RD-, config and calibration pins, not `prereg/TEMPLATE_*.md`.
    So "fixed by that pin" (HT l.10-11) is held by nothing until a test is added.
  - N-e: T l.73-74 still lets H4 "compute" a held-out output, sealed.
- **n-7.** TT l.60 and l.932 assert `"\r\n" not in text` on `read_text` output, which never contains CRLF. Read bytes
  to make it bite. It is harmless, because every pin hashes LF-normalised bytes.

---

## What I tried that found nothing

- **A search reading NQ's held-out years.**
  - The template carries no `Judged-block reads:` line (TT l.190), and the reader honours a judged purpose only from
    that line (rule 3).
  - Choice or fitting words never read the block.
  - Rule 1 needs a finalists' token newer than the pin, and rule 2 gives the window to the first ledgered family. F-HT
    is the only file with the line, and the scan refuses a second held-out-marked F- file.
  - The confirmation window is refused in `span` whatever the purpose.
  - Nothing in v3's diff widens any of this.
- **Look-ahead in the walk.** sigma is read on bars closed at or before the alert. Under open-time stamps that is the
  bar stamped t-1 and earlier. s and n now read only T_fill and sigma, so no post-fill path enters.
- **The step bound.** s = ceil(r/√W) gives round(r²/s²) ≤ W. "Halves up" cannot cross W, because r²/s² ≤ W. sigma = 0
  gives n = 1 (one-tick variance, negligible).
- **The level and k.** One k for F-HT at 0.05 / (k (k + 1)). The fixed sequence at the full level controls the
  family-wise error for any order fixed without the held-out coin draws. Intersection-union across each finalist's
  baselines is unchanged. The alternation is a function of the pinned lists. A search's withdrawal before F-HT's
  held-out row spends nothing.
- **The no-retry clause (M-5 (c)).**
  - The sentence is word for word in T §9 and GK item 9, and needled.
  - It closes the retry: changed limits put every search under them outside F-HT.
  - Since no successor is ever a member, a retry cannot reach F-HT at all. The residual is only the non-member route
    (CW-1).
- **The membership event, cold.**
  - Its definition reads no outcome, and state (c) is fixed at it. An empty history is not due.
  - The no-new-pin bar is refused in the helper.
  - A closing row after a finalists' row is refused, so finalists are never voided.
  - With R-1, the only membership choice left after the event is W-1's.
- **E-258's check against the real log.** `_pin_ready` against master's working `DECISIONS.md` returns `[]`. The
  test's visible skip will turn into an assertion on master.
- **Typed figures.** None found. The tightened scans (four-digit, three-digit, x.yy) pass both templates.
- **The joint runner and the inputs (m-4).** Unchanged and needled.

## What I could not check

- **E-257, E-258 and the one-member ruling's row** are in a pending commit on master. I read their texts from the
  hold folder only.
- **wt-three's `walk_step_for` (s-c).** I did not re-read it. Section 9 calibrates "the R-10 estimator (section 5)",
  so H3's deciding run must use the rule of T l.311.
- **Q-194 (wt-verify)**, unread.
- **How often W-1 or CW-1 would bite.** That depends on the lead's schedule for MFFU's and Lucid's gates and go rows
  against Topstep's survey, and on a purchase. Neither is something an experiment settles.
- **D-1's frequency.** That is how often a firm's verified rule turns `changed` mid-search. It is a fact about the
  firms, not an experiment.
