"""The one door to Stage 2's bars and walks, and the judged block's seal (Q-32; the Phase 0 audit's R-4, R-5 and H-2,
`docs/audits/phase0/D_protocol.md`; family B's red team m-7; E-019).

    from extended import reader
    bars = reader.read_bars("2020-01-02", "2023-12-29")                         # the choice block: no tag needed
    bars = reader.read_bars("2024-01-02", "2026-07-16", purpose="stage_C_judgement",
                            declaration="prereg/F-11_name.md", what="F-11 stage C: the pick's brackets")
    walks = reader.read_walks("A3", "walks", "2024-01-02", "2026-07-16", purpose=..., declaration=...)
    reader.authorise_engine_read("2020-01-02", "2026-07-16", purpose="identity", declaration="E-004",
                                 files=[...], what="E-004's identity")         # before Stage 2's engine reads itself

**Why.** "The judged block is read once, by a pinned declaration, for a declared purpose" was a promise; this module
makes it a mechanism. A look at the judged block before the pick is frozen does not announce itself -- the numbers
still compute -- so every read of Stage 2's bars (`vendor/stage2/data/bars/<ROOT>/bars.parquet`) and walks
(`vendor/stage2/data/atlas/<family>/<table>.parquet`) by this repository's code comes through here, and a read the
rules do not allow raises **before anything is read** (`tests/test_reader.py` scans this repository's code for any
other parquet read).

**The blocks** (feature-rules section 4; CLAUDE.md "Windows"): the **choice block** 2020-01-02 to 2023-12-29 and the
**judged block** 2024-01-02 to 2026-07-16. The seal starts the day after the choice block ends, so the holiday gap
(2023-12-30 to 2024-01-01) is under it. **Anything from 2026-07-17 is refused outright, whatever the purpose** (NQ's
declared confirmation window; it is not on disk; refused anyway, `ConfirmationWindowRefused`), and so is anything
before 2020-01-02. Stage 2's own guard runs as well: bars come through the vendored `propedge.data.bars.read_bars`
(its `assert_readable` for the purpose `development`), and walks after the same `assert_readable`, so the vendored
`config/windows.yaml` refuses NQ's reserve independently.

**The rules for a read touching the judged block** (`JudgedBlockSealed` otherwise), checked in this order:

1. it declares a `purpose` -- a plain name such as `stage_C_judgement` or `identity` (letters, digits, underscores);
2. **`identity`** -- the identities that must read Stage 2's whole window (E-004, E-010, E-011, E-024, E-028): the
   declaration is the decision row of the identity (`"E-004"`), which must exist in `DECISIONS.md` and mention an
   identity, and the process's script must be one of this repository's identity scripts (`identity/*.py`). Allowed
   in any tree, as often as it runs, and checked wherever it runs; **ledgered only inside a clean run** (E-026, the
   lead's rule: `S2X_CLEAN_RUN` set -- and then the tree must be that run's checkout of a committed tree, with its
   run id, as a family read's must), so a worktree's or the suite's identity runs write nothing (Q-48);
2a. **`registered_design`** -- re-reading Stage 2's own registered designs, already judged in Stage 2 (E-037, Q-58):
   the readings scripts beside them (Q-17's `scripts/user_beside.py`, Q-20's `scripts/breakeven_fidelity.py`, Q-18's
   `scripts/p14_validation.py`). `design=` names the designs read, each one of `REGISTERED_DESIGNS` (P-14, P-15,
   P-16; nothing else, on either block); the declaration is a decision row that exists and names each of them
   (never a family's or a described reading's file: a family can never use this purpose, whatever its line says);
   the process's script must be one of this repository's `scripts/*.py`. On the choice block, checked wherever it runs
   and never limited; **a read touching the held-out years is admitted only under the held-out rule 3 below** (a row
   with a read token naming it, inside a clean run, one run a row; Q-158);
3. every other purpose: a purpose containing a choice or fitting word (`choose`, `choice`, `fit`, `select`, `search`,
   `tune`, `train`, ...) never reads the judged block, whatever a declaration says (the audit's H-2); the declaration
   is a family file `prereg/F-NN_<name>.md` (or its id `F-NN`) or a described reading's `prereg/RD-NN_<name>.md` (or
   `RD-NN`; E-023 (1), E-025 (1), Q-58: on exactly the same rules) that exists, is **pinned** -- its sha256 (of the LF
   text) in a decision row, read exactly as `tests/test_declarations_fixed.py` reads the pins -- and still hashes to
   that pin, and whose text **names the purpose for the judged block** on a line of the form

       - **Judged-block reads:** `stage_C_judgement`, `stage_D_scorecard`

   (a line starting, after list or quote markers, with "Judged-block reads", a colon, and each purpose in backticks;
   a purpose named in prose elsewhere authorises nothing);
4. it runs **inside a clean run** -- the checkout `scripts/run_clean.py` made under `%LOCALAPPDATA%/stage2-extended-
   runs/<name>`, named by `S2X_CLEAN_RUN`, with the run id `S2X_RUN_ID` -- of a **committed** tree (no uncommitted
   change outside `results/`): a judged read is made by a named commit, as a result is (CLAUDE.md "Results");
5. **once**: if the ledger already holds a read of the same declaration and purpose by another run, the read is
   refused (`JudgedBlockReadTwice`) unless `repeat="E-NNN"` names a decision row that names the declaration -- one
   row, one more run. One run may read as often as it needs (bars, then walks; its own workers share the run id).

**The held-out rules** (CHARTER 3.6-3.7, in force since E-210; Q-158; the red team's B-3 of
`docs/reviews/TEMPLATE_AGENTS_2026-11-18.md`). The judged block is E-208's held-out years. On top of the rules above,
each refusal a `HeldOutRefused` (a `JudgedBlockSealed`) whose message begins with its rule's name (`RULES`):

* **rule 1, the finalists' row first.** A family's (F-) judged read -- **every purpose** that reads any held-out
  date, `heldout_test` and `heldout_stress` as any other a family's line names (Q-194, the red team's M-2 of
  `docs/reviews/TEMPLATE_V2_FULL_2026-11-20.md`) -- is honoured only once a decision row carries a finalists' token
  for exactly this pinned declaration (its id and its own sha256), in a row placed after the pin's first row (never
  in the pin's own row); so no
  family reads a held-out day before its finalists are pinned, and a refused read writes no ledger line and spends no
  market's window (rule 2). **The held-out purposes themselves** (`heldout_test`, `heldout_stress`) are read only by
  the one held-out declaration of the read's market (Q-194d, NOTE-6): an F- file named
  `prereg/F-NN_heldout_test_<MARKET>.md` that carries the held-out template's marker (`HELDOUT_MARKER`, at a line's
  start) and every one of its section headings (`HELDOUT_HEADINGS`, as written at wt/wt-lit 13df998 until template v3
  is pinned), not the design-search marker, and is the only held-out-marked `prereg/F-*.md` for the market; any other
  pinned F- with a judged-read line and a finalists' token is refused them. **And no other F- reads a held-out date
  at all** (Q-194e, the red team's P10; template v3 confines every family to the search years): an F- declaration's
  judged read is honoured only for the market's one held-out declaration and only under its two held-out purposes,
  whatever other purpose its line names, with or without a finalists' token; and **no `repeat=` row is ever honoured
  for it** (P9; the template's section 5, step 3). **One run per purpose means a crash spends the test** (the red
  team's NOTE-6 of `READER_Q194e_2026-11-22`): the ledger line is written before any data is read, so a run that dies
  after it and before its result has spent that purpose's held-out read; the once rule refuses another run and no
  repeat row exists, so the test is not rerun (the line can still back a verdict row). A described reading (RD-)
  never takes a held-out purpose; its other purposes are rule 4's.
  Each refusal names the purpose and the declaration. Outside this rule, as E-247's rm-4 rules: the registered
  reproduction identities (purpose `identity`, declared by their decision row, rule-free here) and a registered
  design's re-read (`registered_design`, rule 3) keep their documented form;
* **rule 2, once per market.** A market's held-out window is read for a test by one declaration: the first family (F-)
  whose judged read of it is ledgered, under any purpose. Any other family's judged read touching that window is
  refused, whatever its bytes or purpose -- every window the read touches counts, and every window an earlier read
  touched (Q-194c, MINOR-2: a read straddling a newer window and the base window touches both) -- unless a row opens
  a new window (a window token) that owns the read's days;
* **rule 3, a registered design's held-out read named by its own row.** A `registered_design` read touching the
  held-out years is admitted only by a row whose read token names every design read and this process's script,
  inside a clean run, one run a row; a row without the token (E-021, E-024, E-026, E-035, ...) admits no new one --
  the reads it admitted stay valid as the ledger records them; **and, before any of that, only after the joint
  held-out test's verdict (Q-194b, the lead's ruling on O-7's RD-10 C3 and the red team's L-1 of template v3):** a
  `registered_design` read of any held-out date (the whole seal, 2023-12-30 to 2026-07-16, the holiday gap
  included) is refused, whatever row declares it, until every window the read touches has a **counted verdict
  row** of the read's own market (below); after it, rule 3 stands as above. A search-year read is untouched, and so
  are E-247 rm-4's `identity` reads. The refusal names the purpose and the declaration (and the described readings
  the read is made for) and writes no ledger line;
* **rule 4, a described reading after the verdict.** A described reading (RD-) reads a market's held-out window only
  once every window its read touches has a counted verdict row of that market.

**A counted verdict row** (Q-194c, the lead's rulings on the red team's `READER_Q194_2026-11-21` MINOR-1, MINOR-3,
NOTE-3): one form, `heldout-verdict: <MARKET> F-NN @ <its LF sha256> -- <text>`, the first text of the row's third
cell, counts for a window only when (a) it is placed after the window's opening row; (b) `F-NN` is pinned at that
sha256 and a finalists' token for `F-NN` at that sha256 is placed after the pin and before the verdict; (c) the
ledger of the checkout being run holds that family's `heldout_test` read of the window, of the verdict's market, at
that sha256 under that finalists' row, made in a clean run from a commit whose DECISIONS.md did not yet hold the
verdict row -- the held-out read the verdict reports, which really happened; and (d) **the order is proven**
(Q-194d, MINOR-1; Q-194e for merges; Q-194f for the exact line): for **every** commit of HEAD's whole history,
merge commits included, that adds the exact verdict row -- its patch against some parent (`git log --full-history -m
-p`) holds the line `+<row>`, never judged by a count of the text -- and whose own DECISIONS.md holds it, the ledger
as committed there
already holds that line byte for byte and the read's commit is a proper ancestor of it -- so a verdict row recorded in
a merge commit counts when it follows its read, and one committed anywhere before its read never does; a line the
running process appended itself, or a read made after the verdict was committed, never counts; anything git cannot
answer (a commit gone after a rebase, a shallow clone, an unfetched branch, a call git cannot even take -- an
`OSError`, refused by name) fails closed. The old unbound forms
(`heldout-verdict: NQ F-NN -- ...`, `heldout-verdict: F-NN @ <sha256> -- ...`) are malformed and count for nothing.
**"Newer" is a place in DECISIONS.md** (a later line), never a higher E-number. **Fences** follow CommonMark (Q-194d):
a fence opens on at most three spaces of indent and three or more backticks or tildes and closes only on the same
character, at least as long; an indented line is never a fence; an unclosed fence runs to the end of the file; a line
inside a fence is no row, no pin and no token anywhere in this module (`decision_row`, `pins`, the tokens). **Every
judged read is refused while the log fails its own hygiene** (`LOG_RULE`): an unclosed fence, a malformed or fenced
held-out token -- `heldout_token_problems` not empty -- the refusal naming the problem. **The recovery** (Q-194e,
MINOR-2; Q-194f; the log is append-only): a later row `heldout-void: E-NNN -- <reason>` voids row E-NNN -- the
problem of a malformed row E-NNN (one carrying a pin too: the pin is still read from the row; a void never removes
a pin), or of a token row E-NNN inside a closed fence (it stays fenced, so it is still no row), is then ignored; every
void naming the row counts if it is placed after it; and a fence open when a void row naming the nearest row above
the fence's opening line appears (wherever the fence opened) is closed at the void row's end -- the rows between stay
fenced (none is revived, and none is reported), and the first fence-like line after the void, if it is a bare closer
of that fence, is its closer, not a new fence. **A void never removes a token or a pin**: on the malformed path it
names a row that is no token; on the fence path it names the row the stray fence follows, whatever that row is, and
leaves it as it is. **What the renderers show** (the red team's NOTE-3 of `READER_Q194e_2026-11-22`): a void is a
reader's rule only -- GitHub, VS Code and every CommonMark renderer still show the rows after a stray fence as code
until a closing fence; the lead may append one right after the void (absorbed as above, so the log stays unlocked);
the display's recovery for a row hidden in the fence is a new, correct row after it.

What a counted verdict means, stated with the rule (the red team's NOTE-2, NOTE-3, NOTE-4 of
`READER_Q194c_2026-11-21`):

* **a read of part of a window backs the whole window** -- the verdict reports the joint test's read of the window,
  whatever days of it the ledgered line spans; rule 2 already closes every day of that window to other families;
* **a crashed run's written line still counts** -- the ledger line is written before any data is read, so a run that
  authorised and then crashed is "the read" for the gate (the auditor reads the run's result and log beside it);
* **a later window re-opens days already read** -- a `heldout-window` row lies inside the seal the joint test read, so
  its days were read under the earlier window's verdict, by the joint test and by every registered or described read
  admitted under that verdict; the later window's own test and verdict then govern those days;
* **the joint test's clean run is tagged `heldout-read/<run id>` at its commit** (the lead tags it), so the read's
  commit can always be found; a read whose commit cannot be found backs nothing, failing closed, and since the joint
  test is never rerun its verdict would never count -- the tag is what keeps it reachable.

**Q-173's closures** (the red team's read of the O-7 drafts, `docs/reviews/O7_SEARCH_YEARS_2026-11-19.md`):

* **rule 3, a described reading's replay waits for the verdict (M-3).** A `registered_design` read of the held-out
  years made for a described reading -- its admitting row names an `RD-NN`, or a `prereg/RD-*.md` names the process's
  script -- is refused (under rule 3) until the verdict; since Q-194b every registered design's held-out read waits
  for it, and the refusal names the readings the read is made for. Only the joint held-out test's family declaration
  reads a market's held-out window before its verdict;
* **the supersession rule (N-1).** `SUPERSEDED` lists each superseded declaration as (its path, its LF sha256); a read
  whose declaration is one of them -- by path, or by bytes under any other path -- is refused (`SupersededRefused`),
  on the search years as on the judged block, whatever later rows exist; so is a `registered_design` read made for a
  superseded described reading. The lead fills the list at the O-7 pins (RD-01, RD-02, RD-03, RD-05's part F, RD-04);
* **the identity rule (N-2).** An identity writes nothing to `results/`: an `identity` read of the judged block is
  refused when the identity's script, read as source (`identity_write_problems`), calls `write_result` or writes
  (`open` in a write mode, `write_text`, `write_bytes`, `to_csv`, `to_parquet`, `to_json`) to a path whose literal
  parts name `results`. A static check of the script's own text: a write through a helper in another module, or to a
  path built in a variable elsewhere, is not seen -- the reader's own ledger append is not the script's write.

**The held-out tokens** (`HELDOUT_TOKENS`; `extended/identity_tokens.py`'s positional form): exactly the first text of
a decision row's third cell, the row beginning exactly `| E-NNN | YYYY-MM-DD | `, unquoted, ending ` -- ` and the
row's text, outside any fenced code block; that shape anywhere else is never a token (`heldout_token_problems` lists a
row whose third cell begins token-like but is not exactly one, and a token inside a fence):

    | E-NNN | YYYY-MM-DD | heldout-finalists: F-NN @ <declaration's LF sha256> list <the finalists' sha256> -- <text> |
    | E-NNN | YYYY-MM-DD | heldout-window: NQ 2026-07-17 to 2027-07-16 -- <text> |
    | E-NNN | YYYY-MM-DD | heldout-verdict: NQ F-NN @ <the held-out test's declaration's LF sha256> -- <text> |
    | E-NNN | YYYY-MM-DD | heldout-read: P-14,P-16 by scripts/<name>.py -- <text> |
    | E-NNN | YYYY-MM-DD | heldout-void: E-NNN -- <reason> |

(the shas 64 lowercase hexadecimal characters; a market a root of capitals and digits; the designs P-14, P-15, P-16
joined by commas; the script one of `scripts/*.py`). Each held-out day belongs to the newest (latest-placed) window
row for its market holding it, else to E-208's base window (`BASE_WINDOW_ROW`, the seal's first day to 2026-07-16,
every market); the windows a read touches are its days' (`heldout_windows`), and the window it is recorded under is
the newest of them (Q-194d, NOTE-1; `heldout_window`, the newest window holding all its days, is kept as a query).
**A later window needs its own rule** (the red team's NOTE-3 of `READER_Q194d_2026-11-21`): the market's held-out
declaration has spent its one read and blocks a second held-out declaration of its market, so a `heldout-window` row
opens nothing for a test until a decision row makes that rule; a window row cannot widen what
`span` allows (the confirmation window stays refused here). A family's or described reading's judged line, and a
registered design's held-out line, carry a `heldout` field: the market and window (and `windows`, every window,
when the read touches more than one), the finalists' row and list sha256, the verdict row(s), or the read row and the
verdict row(s)
(`test_verdict`).

**The read ledger** (`results/read_ledger.jsonl` of the tree whose declarations authorise the read): every family's
or described reading's read touching the judged block, and every identity's or registered design's read inside a clean
run (`Authorisation.ledgered`), appends one line **before the data is read** (a ledger that cannot be written means no
read) -- who (the script, its arguments, the calling function, the commit, the dirty flag, the process, the clean run
and run id), what (each file with its sha256, size and whether it matches `vendor/DATA_MANIFEST_stage2.sha256`; the
columns; the description), which dates (the span, the blocks, the judged part), which declaration (its path or row,
its sha256, its kind -- `family`, `described_reading`, `identity`, `registered_design` -- and a registered design's
`designs`) and purpose, and when (UTC). Choice-block reads are not ledgered (the brief: judged reads only). The
ledger is append-only: a line that does not parse, or a file that does not end in a newline, refuses the next read
(`LedgerError`); `ledger_history_problems` reports any line committed in the history that is no longer in HEAD, or in
HEAD that is no longer in the working copy (`tests/test_reader.py` runs it on this repository); the hook
`scripts/hooks/protect_results.py` warns on any tool edit that changes an existing line; `scripts/run_clean.py
--collect` brings a run's new lines home as a union (Q-67): only when the run only appended to its commit's ledger and
this tree's has lost no line, the result verified by `read_ledger` before it replaces this tree's.

**What it does not do.** It cannot see a read made inside a vendored call (Stage 2's engine opens the bars and the
atlas itself in the identities and the U1 replay) -- such a runner calls `authorise_engine_read` with the files the
engine will open, which checks and ledgers exactly as a read here does (every identity's `main` does, Q-48); nor a
script that opens the files by hand
(the scan in the tests is a deterrent for this repository's committed code, not proof). Withdrawn families are not
machine-readable yet (the audit's R-8 registry): a withdrawn family's pinned file authorises a read if it names the
purpose on its line -- F-01 names none.

Importing this module touches no `sys.path` and imports no engine; the vendored tree is put on the path
(`extended.use_vendored_stage2`) only when bars or walks are actually read, so run reads in a process of their own.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

from extended import CLEAN_RUN_ENV, ROOT, RUN_ID_ENV, RUNS_DIR

#: the choice block (feature-rules section 4): every choice, fit and search
CHOICE_START, CHOICE_END = date(2020, 1, 2), date(2023, 12, 29)
#: the judged block: one read of a frozen pick, by a pinned declaration
JUDGED_START, JUDGED_END = date(2024, 1, 2), date(2026, 7, 16)
#: NQ's declared confirmation window opens here (Stage 2 `config/windows.yaml`, reserved): never read
CONFIRMATION_START = date(2026, 7, 17)
#: the seal covers every day after the choice block (the holiday gap before JUDGED_START included)
SEAL_START = CHOICE_END + timedelta(days=1)

IDENTITY = "identity"
#: re-reading Stage 2's own registered, already-judged designs (E-037, Q-58), only these
REGISTERED_DESIGN = "registered_design"
REGISTERED_DESIGNS = ("P-14", "P-15", "P-16")
LEDGER_REL = "results/read_ledger.jsonl"
LEDGER_VERSION = 1
LEDGER_KEYS = ("ledger", "when", "who", "what", "dates", "declaration", "purpose", "repeat")
VENDOR_REL = "vendor/stage2"
STORE_REL = "vendor/stage2/data/bars"
ATLAS_REL = "vendor/stage2/data/atlas"
DATA_MANIFEST_REL = "vendor/DATA_MANIFEST_stage2.sha256"

#: words that mark a purpose as choosing or fitting: such a purpose never reads the judged block (the audit's H-2)
CHOICE_WORDS = frozenset({"choose", "choice", "fit", "fitting", "select", "selection", "search", "tune", "tuning",
                          "train", "training"})
PURPOSE = re.compile(r"[A-Za-z][A-Za-z0-9_]{0,63}")
#: the declared line: "Judged-block reads[ anything]: `purpose`, `purpose`" at a line's start (after markers)
DECLARED_LINE = re.compile(r"^[ \t>*_\-]*judged-block reads\b[^:\n]*:(.*)$", re.IGNORECASE | re.MULTILINE)
PURPOSE_TOKEN = re.compile(r"`([A-Za-z][A-Za-z0-9_]*)`")
#: a pin, exactly as tests/test_declarations_fixed.py reads it: a family's (`F-nn`) or a described reading's (`RD-nn`)
PIN = re.compile(r"`(prereg/(?:F|RD)-\d+[^`]*\.md)` sha256 `([0-9a-f]{64})`")
ROW = re.compile(r"\|\s*(E-\d+)\s*\|")
DECLARATION_PATH = re.compile(r"prereg/(?:F|RD)-\d+[^/`]*\.md")
#: a declaration's id: a family's `F-nn` or a described reading's `RD-nn`
F_ID = re.compile(r"(?:F|RD)-\d+")
DECLARATION_ID = re.compile(r"prereg/((?:F|RD)-\d+)")
E_ID = re.compile(r"E-\d+")
NAME = re.compile(r"[A-Za-z0-9_]+")
THIS_FILE = Path(__file__).resolve()

# --- the held-out rules (CHARTER 3.6-3.7, in force since E-210; Q-158) --------------------------------------------
#: the held-out test's purposes (the design-search template's section 14): honoured only after a finalists' row
HELDOUT_TEST, HELDOUT_STRESS = "heldout_test", "heldout_stress"
HELDOUT_PURPOSES = (HELDOUT_TEST, HELDOUT_STRESS)
#: E-208's split: every market's base held-out window, opened by E-208 -- from the seal's first day (so a read inside
#: the holiday gap falls in it) to the judged block's last; a `heldout-window` row opens another
BASE_WINDOW_ROW = "E-208"
#: each refusal's rule, named in its message
RULES = {1: "held-out rule 1, the finalists' row first (CHARTER 3.7)",
         2: "held-out rule 2, once per market (CHARTER 3.6 (c))",
         3: "held-out rule 3, a registered design's held-out read named by its own row (CHARTER 3.6 (b))",
         4: "held-out rule 4, a described reading only after the market's verdict row (CHARTER 3.6 (a), (c))"}
#: the held-out tokens, each exactly the first text of a decision row's third cell (`extended/identity_tokens.py`'s
#: positional form): the row's exact start, the stem, its fields, ` -- `, then text whose first character is neither a
#: space nor a bar
_HO_HEAD = r"\| (?P<row>E-\d+) \| (?P<date>\d{4}-\d{2}-\d{2}) \| "
_HO_TAIL = r" -- (?=[^\s|])"
_HO_DAY = r"\d{4}-\d{2}-\d{2}"
_HO_MARKET = r"[A-Z][A-Z0-9]{0,7}"
HELDOUT_TOKENS = {
    "finalists": re.compile(_HO_HEAD + r"heldout-finalists: (?P<decl>F-\d+) @ (?P<sha>[0-9a-f]{64}) "
                            r"list (?P<list>[0-9a-f]{64})" + _HO_TAIL),
    "window": re.compile(_HO_HEAD + rf"heldout-window: (?P<market>{_HO_MARKET}) (?P<start>{_HO_DAY}) to "
                         rf"(?P<end>{_HO_DAY})" + _HO_TAIL),
    #: Q-194c: one verdict form, naming the market, the held-out test's declaration and its LF sha256
    "verdict": re.compile(_HO_HEAD + rf"heldout-verdict: (?P<market>{_HO_MARKET}) (?P<decl>F-\d+) @ "
                          r"(?P<sha>[0-9a-f]{64})" + _HO_TAIL),
    #: Q-194e (MINOR-2): the log's recovery -- a later row voids a malformed row, or the row a stray fence follows
    "void": re.compile(_HO_HEAD + r"heldout-void: (?P<target>E-\d+)" + _HO_TAIL),
    "read": re.compile(_HO_HEAD + r"heldout-read: (?P<designs>P-1[456](?:,P-1[456])*) "
                       r"by (?P<script>scripts/[A-Za-z0-9_]+\.py)" + _HO_TAIL),
}
#: a held-out token-like string: what a hand meaning one types (any case, `-`, `_`, a space or nothing as joiners)
HELDOUT_TOKEN_LIKE = re.compile(r"held[-_ ]?out[-_ ]?(?:finalists|window|verdict|read|void)\s*[:=]", re.IGNORECASE)
_HO_THIRD_CELL = re.compile(r"\|\s*E-\d+\s*\|[^|]*\|")
_HO_MARKS = re.compile(r"[\s`*_~]*")
#: a fenced code block's opening line, CommonMark's rule (Q-194d): at most three spaces of indent, then three or more
#: backticks or tildes; a backtick fence's info string holds no backtick. Rows inside one are never rows (Q-194c, -d)
_FENCE_OPEN = re.compile(r"^ {0,3}(?P<fence>`{3,}|~{3,})(?P<info>.*)$")
#: the log's own hygiene (Q-194d): every judged read is refused while `heldout_token_problems` is not empty
LOG_RULE = "the decision log's held-out hygiene, every judged read refused while it fails (Q-194d)"


class ReadRefused(RuntimeError):
    """A read of Stage 2's bars or walks this module does not allow; raised before anything is read."""


class ConfirmationWindowRefused(ReadRefused):
    """The span reaches 2026-07-17 or later: NQ's confirmation window, refused whatever the purpose."""


class JudgedBlockSealed(ReadRefused):
    """The span reaches the judged block without a purpose and a declaration that allow it."""


class JudgedBlockReadTwice(JudgedBlockSealed):
    """Another run already read the judged block under this declaration and purpose."""


class LedgerError(ReadRefused):
    """The read ledger does not verify or cannot be written, or the commit cannot be named: no judged read."""


#: Q-173 (N-1): each superseded declaration as (its path, its LF sha256); filled by the lead's row at the O-7 pins
SUPERSEDED: tuple[tuple[str, str], ...] = ()
SUPERSESSION_RULE = "the supersession rule, a superseded declaration authorises no read (N-1)"
IDENTITY_WRITE_RULE = "the identity rule, an identity writes nothing to results/ (N-2)"
RD_ID = re.compile(r"(?<![\w-])RD-\d+(?!\d)")
#: the calls that write a file (N-2's static check)
WRITE_CALLS = frozenset({"write_text", "write_bytes", "to_csv", "to_parquet", "to_json"})


class SupersededRefused(JudgedBlockSealed):
    """A read authorised by a superseded declaration (`SUPERSEDED`); refused whatever later rows exist."""

    def __init__(self, what: str, why: str):
        super().__init__(f"REFUSED ({SUPERSESSION_RULE}): {what}: {why}")


class HeldOutRefused(JudgedBlockSealed):
    """A read of the held-out years one of the held-out rules (CHARTER 3.6-3.7, Q-158) refuses; `rule` is its number
    (`RULES`), and the message begins with the rule's name."""

    def __init__(self, rule: int, what: str, why: str):
        self.rule = rule
        super().__init__(f"REFUSED ({RULES[rule]}): {what}: {why}")


@dataclass(frozen=True)
class HeldOutToken:
    """A held-out token of a decision row: its kind (`finalists`, `window`, `verdict`, `read`), the row's id and date,
    its fields (finalists: `decl`, `sha`, `list`; window: `market`, `start`, `end`; verdict: `market`, `decl`, `sha`;
    read: `designs` (a tuple), `script`), and its position (`pos`, the line's index in DECISIONS.md: "newer" is a
    later position, never a higher E-number, Q-194c)."""
    kind: str
    row: str
    date: str
    fields: tuple[tuple[str, Any], ...]
    pos: int = -1

    def get(self, key: str) -> Any:
        return dict(self.fields)[key]

    @property
    def number(self) -> int:
        return int(self.row[2:])


@dataclass(frozen=True)
class Authorisation:
    """What a read was allowed to touch, and under what."""
    start: date
    end: date
    blocks: tuple[str, ...]
    judged: bool
    judged_first: date | None
    judged_last: date | None
    purpose: str | None
    declaration: str | None
    declaration_sha256: str | None
    #: "family" | "described_reading" | "identity" | "registered_design" | None (a choice-block read)
    kind: str | None
    repeat: str | None
    #: whether the read appends its line to the ledger: every family's or described reading's judged read; an
    #: identity's or a registered design's only inside a clean run (E-026, E-037); never a choice-block read
    ledgered: bool = False
    #: the registered designs a `registered_design` read re-reads, in `REGISTERED_DESIGNS`' order (else empty)
    designs: tuple[str, ...] = ()
    #: the market read (a root such as "NQ")
    market: str = "NQ"
    #: what the held-out rules checked (Q-158), written to the ledger line as its `heldout` field: for a family's or a
    #: described reading's judged read the market and the window (`window`, the row that opened it), with the
    #: finalists' row (`finalists`, `finalists_list_sha256`) for a family's read under any purpose (Q-194) and the
    #: verdict row (`verdict`) for a described reading; for a registered design's held-out read the row naming it
    #: (`read_row`) and the counted verdict row(s) (`test_verdict`, Q-194b, Q-194c); a read touching more windows
    #: than the one it is recorded under carries them all (`windows`, Q-194c). None otherwise
    heldout: tuple[tuple[str, Any], ...] | None = None


# ------------------------------------------------------------------------------------------------- dates and blocks


def _day(x: Any) -> date:
    if isinstance(x, datetime):                         # a pandas Timestamp is a datetime
        return x.date()
    if isinstance(x, date):
        return x
    if isinstance(x, str):
        try:
            return date.fromisoformat(x)
        except ValueError:
            return datetime.fromisoformat(x).date()
    raise TypeError(f"a day is a date, a datetime or an ISO string, not {type(x).__name__} {x!r}")


def span(start: Any, end: Any, what: str = "read") -> tuple[date, date]:
    """`(start, end)` as days, refused when it reaches the confirmation window (first) or starts before the choice
    block; `ValueError` when it ends before it starts."""
    s, e = _day(start), _day(end)
    if max(s, e) >= CONFIRMATION_START:
        raise ConfirmationWindowRefused(
            f"REFUSED: {what} {s} to {e} reaches {CONFIRMATION_START} or later -- NQ from {CONFIRMATION_START} is the "
            "declared confirmation window (CLAUDE.md 'Windows'; Stage 2 config/windows.yaml, reserved), never read "
            "until a carried candidate is registered, whatever the purpose or declaration")
    if e < s:
        raise ValueError(f"{what}: {e} is before {s}")
    if s < CHOICE_START:
        raise ReadRefused(f"REFUSED: {what} starts {s}, before the development window opens on {CHOICE_START} "
                          "(CLAUDE.md 'Windows': development NQ 2020-01-02 to 2026-07-16 only)")
    return s, e


def blocks_of(start: Any, end: Any) -> tuple[str, ...]:
    """The blocks a span touches: ("choice",), ("judged",) or ("choice", "judged")."""
    s, e = span(start, end)
    return tuple(b for b, on in (("choice", s <= CHOICE_END), ("judged", e >= SEAL_START)) if on)


def check_returned(days: Iterable[Any], start: Any, end: Any) -> None:
    """After a read: every returned day lies inside what was authorised, and none on or after 2026-07-17."""
    s, e = _day(start), _day(end)
    got = {_day(d) for d in days}
    late = sorted(d for d in got if d >= CONFIRMATION_START)
    if late:
        raise ConfirmationWindowRefused(f"REFUSED: the read returned {len(late)} day(s) from {late[0]} on -- the "
                                        f"confirmation window opens {CONFIRMATION_START}; nothing is returned")
    out = sorted(d for d in got if d < s or d > e)
    if out:
        raise ReadRefused(f"REFUSED: the read returned day(s) outside {s} to {e} ({out[:3]}); nothing is returned")


# ---------------------------------------------------------------------------------------------------- declarations


def declared_purposes(text: str) -> frozenset[str]:
    """The purposes a declaration names for the judged block: the backticked names on its 'Judged-block reads:'
    lines."""
    return frozenset(p for m in DECLARED_LINE.finditer(text) for p in PURPOSE_TOKEN.findall(m.group(1)))


def pins(decisions_text: str) -> dict[str, set[str]]:
    """{`prereg/F-..md` or `prereg/RD-..md`: {sha256, ...}} from the decision log, as
    `tests/test_declarations_fixed.py` reads it -- except that a line inside a fenced code block pins nothing
    (Q-194d; this repository's log holds no fence)."""
    out: dict[str, set[str]] = {}
    for _, line, fenced in _log_lines(decisions_text):
        if fenced:
            continue
        for rel, h in PIN.findall(line):
            out.setdefault(rel, set()).add(h)
    return out


def decision_row(decisions_text: str, row_id: str) -> str | None:
    """The decision log's line for `row_id` (`E-NNN`) outside any fenced code block (Q-194d), or None."""
    for _, line, fenced in _log_lines(decisions_text):
        m = ROW.match(line)
        if not fenced and m and m.group(1) == row_id:
            return line
    return None


def sha256_lf(p: Path) -> str:
    """The sha256 of a text file's LF form (the pins are of the LF text, E-003)."""
    return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _decisions(repo: Path) -> str:
    p = repo / "DECISIONS.md"
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def _rel(p: Path, repo: Path) -> str | None:
    for base in (repo, ROOT):
        try:
            return Path(os.path.abspath(p)).relative_to(Path(os.path.abspath(base))).as_posix()
        except ValueError:
            continue
    return None


def _family_ref(declaration: Any, repo: Path, what: str) -> str:
    s = str(declaration).replace("\\", "/")
    if F_ID.fullmatch(s):
        found = sorted(repo.glob(f"prereg/{s}_*.md")) + ([repo / "prereg" / f"{s}.md"]
                                                         if (repo / "prereg" / f"{s}.md").is_file() else [])
        if not found:
            raise JudgedBlockSealed(f"REFUSED: {what}: the declaration {s} does not exist (no prereg/{s}_*.md)")
        if len(found) > 1:
            raise JudgedBlockSealed(f"REFUSED: {what}: {s} names {len(found)} files; name the one by its path")
        return f"prereg/{found[0].name}"
    if Path(s).is_absolute():
        s = _rel(Path(s), repo) or s
    if not DECLARATION_PATH.fullmatch(s):
        raise JudgedBlockSealed(f"REFUSED: {what}: a judged-block read serves a family's or a described reading's "
                                "declaration, a file prereg/F-NN_<name>.md or prereg/RD-NN_<name>.md of this repository "
                                f"(pinned by its decision row), not {s!r}")
    if not (repo / s).is_file():
        raise JudgedBlockSealed(f"REFUSED: {what}: the declaration {s} does not exist in {repo}")
    return s


# ---------------------------------------------------------------------------------------------- process and git


def _main_script() -> Path | None:
    """The process's script (`__main__.__file__`), None for `python -c` or an interactive session."""
    f = getattr(sys.modules.get("__main__"), "__file__", None)
    return Path(f).resolve() if f else None


def _under(p: Path | None, d: Path) -> bool:
    if p is None:
        return False
    a, b = os.path.normcase(os.path.abspath(p)), os.path.normcase(os.path.abspath(d))
    return a.startswith(b.rstrip("\\/") + os.sep)


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8",
                          errors="replace")


def _commit(repo: Path, what: str) -> str:
    r = _git(repo, "rev-parse", "HEAD")
    if r.returncode or not r.stdout.strip():
        raise LedgerError(f"REFUSED: {what}: the commit of {repo} cannot be named ({r.stderr.strip()[:200]}); a "
                          "judged-block read records the commit that made it")
    return r.stdout.strip()


def _dirty(repo: Path) -> list[str]:
    """Tracked files changed outside `results/` (a run's own output is not code)."""
    r = _git(repo, "status", "--porcelain", "--untracked-files=no", "--", ".", ":(exclude)results")
    if r.returncode:
        raise LedgerError(f"REFUSED: git status failed in {repo}: {r.stderr.strip()[:200]}")
    return [line[3:] for line in r.stdout.splitlines() if len(line) > 3]


def _run() -> tuple[str | None, str | None]:
    return os.environ.get(CLEAN_RUN_ENV) or None, os.environ.get(RUN_ID_ENV) or None


def _sanitise(text: str, repo: Path) -> str:
    for base, mark in ((repo, "."), (ROOT, "."), (Path.home(), "~")):
        for form in {str(base), str(base).replace("\\", "/")}:
            if form and form in text:
                text = text.replace(form, mark)
    return text


def _caller(repo: Path) -> str:
    f = sys._getframe(1)
    while f is not None and Path(f.f_code.co_filename).resolve() == THIS_FILE:
        f = f.f_back
    if f is None:
        return "?"
    name = f.f_code.co_filename
    rel = _rel(Path(name), repo) if not name.startswith("<") else None
    return f"{rel or _sanitise(name, repo)}:{f.f_lineno}:{f.f_code.co_name}"


# ---------------------------------------------------------------------------------------------------- authorisation


def _check_purpose(purpose: Any) -> None:
    if not isinstance(purpose, str) or not PURPOSE.fullmatch(purpose):
        raise ValueError(f"a purpose is a plain name (a letter, then letters, digits or underscores, at most 64), "
                         f"such as 'stage_C_judgement' or 'identity'; not {purpose!r}")


def _choice_purpose(purpose: str) -> bool:
    return any(t in CHOICE_WORDS for t in purpose.lower().split("_"))


def _identity(declaration: Any, repo: Path, what: str) -> str:
    script = _main_script()
    if not _under(script, repo / "identity"):
        raise JudgedBlockSealed(
            f"REFUSED: {what}: the purpose 'identity' reads the judged block only from this repository's identity "
            f"scripts (identity/*.py); this process's script is {script or 'none (python -c or an interactive one)'}")
    if declaration is None or not E_ID.fullmatch(str(declaration)):
        raise JudgedBlockSealed(f"REFUSED: {what}: an identity read names the decision row of its identity "
                                f"(declaration='E-NNN', e.g. 'E-004'), not {declaration!r}")
    row = decision_row(_decisions(repo), str(declaration))
    if row is None:
        raise JudgedBlockSealed(f"REFUSED: {what}: {declaration} is no decision row of {repo / 'DECISIONS.md'}")
    if "identit" not in row.lower():
        raise JudgedBlockSealed(f"REFUSED: {what}: {declaration}'s row does not mention an identity")
    _identity_writes(script, what)
    return str(declaration)


def names_design(row: str, design: str) -> bool:
    """Whether a decision row names a registered design (`P-14`, not `P-140` or `XP-14`)."""
    return re.search(rf"(?<![\w-]){re.escape(design)}(?!\d)", row) is not None


def _designs(design: Any, what: str) -> tuple[str, ...]:
    """`design=` as the registered designs it names, in `REGISTERED_DESIGNS`' order; refused unless every name is one
    of them and there is at least one."""
    names = [design] if isinstance(design, str) else list(design) if isinstance(design, (list, tuple, set,
                                                                                        frozenset)) else None
    if not names:
        raise JudgedBlockSealed(f"REFUSED: {what}: the purpose {REGISTERED_DESIGN!r} names the registered design(s) it "
                                f"re-reads (design='P-14' or a list of {', '.join(REGISTERED_DESIGNS)}), not {design!r}")
    bad = [d for d in names if d not in REGISTERED_DESIGNS]
    if bad:
        raise JudgedBlockSealed(f"REFUSED: {what}: {bad[0]!r} is not a registered design this purpose re-reads -- only "
                                f"Stage 2's own judged designs {', '.join(REGISTERED_DESIGNS)} (E-037)")
    return tuple(d for d in REGISTERED_DESIGNS if d in names)


def _registered(declaration: Any, designs: tuple[str, ...], repo: Path, what: str) -> str:
    script = _main_script()
    if not _under(script, repo / "scripts"):
        raise JudgedBlockSealed(
            f"REFUSED: {what}: the purpose {REGISTERED_DESIGN!r} re-reads Stage 2's registered designs only from this "
            f"repository's readings scripts (scripts/*.py, E-037); this process's script is "
            f"{script or 'none (python -c or an interactive one)'}")
    if declaration is None or not E_ID.fullmatch(str(declaration)):
        raise JudgedBlockSealed(
            f"REFUSED: {what}: a registered design's re-read names the decision row that admits it "
            f"(declaration='E-NNN'), never a family's or a described reading's file; not {declaration!r}")
    row = decision_row(_decisions(repo), str(declaration))
    if row is None:
        raise JudgedBlockSealed(f"REFUSED: {what}: {declaration} is no decision row of {repo / 'DECISIONS.md'}")
    missing = [d for d in designs if not names_design(row, d)]
    if missing:
        raise JudgedBlockSealed(f"REFUSED: {what}: {declaration}'s row does not name {', '.join(missing)}; a "
                                "registered design is re-read under a row that names it")
    return str(declaration)


def _family(declaration: Any, purpose: str, repo: Path, what: str) -> tuple[str, str]:
    if _choice_purpose(purpose):
        raise JudgedBlockSealed(
            f"REFUSED: {what}: {purpose!r} is a choice or fitting purpose, and the judged block is sealed during "
            "choice and fitting (the audit's R-4, H-2): choose, fit and search on the choice block 2020-01-02 to "
            "2023-12-29")
    if declaration is None:
        raise JudgedBlockSealed(f"REFUSED: {what}: a read of the judged block for {purpose!r} names no declaration "
                                "(declaration='prereg/F-NN_<name>.md' or 'prereg/RD-NN_<name>.md', pinned, naming the "
                                "purpose)")
    ref = _family_ref(declaration, repo, what)
    sha = sha256_lf(repo / ref)
    pinned = pins(_decisions(repo)).get(ref)
    if not pinned:
        raise JudgedBlockSealed(f"REFUSED: {what}: {ref} is not pinned -- no decision row of DECISIONS.md carries its "
                                "sha256 (a declaration is pinned by the lead's row before any judged read)")
    if pinned != {sha}:
        raise JudgedBlockSealed(f"REFUSED: {what}: {ref} was edited since its pin (its sha256 {sha[:12]} is not the "
                                f"pinned {sorted(h[:12] for h in pinned)}); a change is a new family (or reading)")
    if purpose not in declared_purposes((repo / ref).read_text(encoding="utf-8")):
        raise JudgedBlockSealed(f"REFUSED: {what}: {ref} does not name {purpose!r} on its 'Judged-block reads:' line "
                                "(a purpose named elsewhere in the text authorises nothing)")
    return ref, sha


def _clean_run(repo: Path, what: str) -> None:
    name, run_id = _run()
    if not name:
        raise JudgedBlockSealed(f"REFUSED: {what}: a family's or a described reading's judged-block read runs only "
                                f"inside a clean run (python scripts/run_clean.py), and {CLEAN_RUN_ENV} is not set")
    want = Path(RUNS_DIR) / name
    if os.path.normcase(os.path.abspath(repo)) != os.path.normcase(os.path.abspath(want)):
        raise JudgedBlockSealed(f"REFUSED: {what}: {CLEAN_RUN_ENV}={name!r} but this tree is {repo}, not that clean "
                                f"run's checkout {want}")
    if not run_id:
        raise JudgedBlockSealed(f"REFUSED: {what}: the clean run has no {RUN_ID_ENV} (scripts/run_clean.py sets it "
                                "for each run; the once-rule tells runs apart by it)")
    bad = _dirty(repo)
    if bad:
        raise JudgedBlockSealed(f"REFUSED: {what}: {repo} has uncommitted changes outside results/ ({bad[:5]}); a "
                                "judged-block read is made by a committed commit")


def _once(repo: Path, ref: str, purpose: str, repeat: str | None, what: str) -> None:
    _, run_id = _run()
    earlier = [r for r in read_ledger(ledger_path(repo))
               if (r.get("declaration") or {}).get("ref") == ref and r.get("purpose") == purpose]
    others = sorted({str((r.get("who") or {}).get("run_id")) for r in earlier} - {run_id})
    if repeat is not None:
        if not E_ID.fullmatch(str(repeat)):
            raise ValueError(f"repeat names a decision row 'E-NNN', not {repeat!r}")
        row = decision_row(_decisions(repo), str(repeat))
        fid = DECLARATION_ID.match(ref)
        if row is None or not (ref in row or (fid and re.search(rf"\b{fid.group(1)}\b", row))):
            raise JudgedBlockSealed(f"REFUSED: {what}: {repeat} does not name {ref}; a further judged read is "
                                    "authorised by a decision row naming the declaration")
        used = sorted({str((r.get("who") or {}).get("run_id")) for r in earlier
                       if r.get("repeat") == repeat} - {run_id})
        if used:
            raise JudgedBlockReadTwice(f"REFUSED: {what}: {repeat} already authorised the read of run {used[0]}; one "
                                       "row, one more run")
        return
    if others:
        raise JudgedBlockReadTwice(
            f"REFUSED: {what}: {ref} was read on the judged block for {purpose!r} by run(s) {others[:3]}; the judged "
            "block is read once -- a further read needs a decision row naming the declaration, passed as "
            "repeat='E-NNN' (the failure protocol: never rerun until it passes)")


# ----------------------------------------------------------------------------------- the held-out rules (Q-158)


def _fence_closer(char: str, size: int) -> re.Pattern:
    """CommonMark's closing fence for an opening run of `size` `char`s: at most three spaces of indent, at least as
    many of the same character, then only spaces or tabs."""
    return re.compile(rf" {{0,3}}{re.escape(char)}{{{size},}}[ \t]*")


def _fence_state(decisions_text: str) -> tuple[list[bool], int | None, set[int]]:
    """(fenced, unclosed, voided): CommonMark's fences, with the void's recovery (Q-194e, Q-194f). A fence opens on a
    line of at most three spaces of indent and three or more backticks or tildes (a backtick fence's info string holds
    no backtick) and closes on its own closer (`_fence_closer`); an indented line is never a fence; an unclosed fence
    runs to the end of the file. **The recovery:** inside an open fence, a void row `heldout-void: E-NNN -- ...` naming
    the nearest row above the fence's opening line (wherever the fence opened: after a row, prose, a blank line or an
    earlier closed fence) closes the fence at the void row's end -- the rows between stay fenced, so none is revived;
    and the first fence-like line after the void, if it is a bare closer of the same fence (the renderers' own close),
    is that fence's closer, never a new fence. `voided` holds the lines of every fence so closed: their fenced tokens
    are reported as no problem."""
    lines = decisions_text.splitlines()
    n = len(lines)
    fenced, voided = [False] * n, set()
    i = 0
    while i < n:
        m = _FENCE_OPEN.match(lines[i])
        if not m or (m["fence"][0] == "`" and "`" in m["info"]):
            i += 1
            continue
        opened, closer = i, _fence_closer(m["fence"][0], len(m["fence"]))
        prev = next((j for j in range(opened - 1, -1, -1) if not fenced[j] and ROW.match(lines[j])), None)
        target = ROW.match(lines[prev]).group(1) if prev is not None else None
        fenced[opened] = True
        j, closed = opened + 1, False
        while j < n:
            fenced[j] = True
            if closer.fullmatch(lines[j]):
                closed = True
                break
            v = HELDOUT_TOKENS["void"].match(lines[j])
            if target is not None and v and v["target"] == target:
                voided.update(range(opened, j + 1))
                nxt = next((k for k in range(j + 1, n) if _FENCE_OPEN.match(lines[k])), None)
                if nxt is not None and closer.fullmatch(lines[nxt]):
                    fenced[nxt] = True
                    voided.add(nxt)
                    j = nxt
                closed = True
                break
            j += 1
        if not closed:
            return fenced, opened, voided
        i = j + 1
    return fenced, None, voided


def _fences(decisions_text: str) -> tuple[list[bool], int | None]:
    """CommonMark's fenced code blocks of the log (Q-194d): for each line whether it is fenced (the fence lines
    themselves included), and the index of an opening fence never closed (None when every fence closes). A fence opens
    on a line of at most three spaces of indent and three or more backticks or tildes (a backtick fence's info string
    holds no backtick); it closes only on a line of at most three spaces of indent and at least as many of the **same**
    character, then only spaces or tabs; a line indented four or more is indented code, never a fence; an unclosed
    fence runs to the end of the file."""
    fenced, unclosed, _ = _fence_state(decisions_text)
    return fenced, unclosed


def _log_lines(decisions_text: str) -> Iterable[tuple[int, str, bool]]:
    """(position, line, fenced) for each line of the decision log: the position the line's index, `fenced` whether it
    sits inside a fenced code block by CommonMark's rule (`_fences`)."""
    fenced, _ = _fences(decisions_text)
    for i, line in enumerate(decisions_text.splitlines()):
        yield i, line, fenced[i]


def heldout_tokens(decisions_text: str, kind: str | None = None) -> list[HeldOutToken]:
    """Every held-out token of the decision log, in file order (of one `kind` if given): positional only -- a token
    is exactly `HELDOUT_TOKENS[kind]` at a line's start, outside any fenced code block; that shape anywhere else is
    never one. Each carries its line's position. A window whose end is before its start, or whose days are not dates,
    is no token (`heldout_token_problems` reports it)."""
    out = []
    for i, line, fenced in _log_lines(decisions_text):
        if fenced:
            continue
        for k, rx in HELDOUT_TOKENS.items():
            if kind is not None and k != kind:
                continue
            m = rx.match(line)
            if not m:
                continue
            f = {x: v for x, v in m.groupdict().items() if x not in ("row", "date")}
            if k == "window":
                try:
                    s, e = date.fromisoformat(f["start"]), date.fromisoformat(f["end"])
                except ValueError:
                    continue
                if e < s:
                    continue
                f["start"], f["end"] = s, e
            if k == "read":
                f["designs"] = tuple(d for d in REGISTERED_DESIGNS if d in f["designs"].split(","))
            out.append(HeldOutToken(k, m["row"], m["date"], tuple(sorted(f.items())), i))
    return out


def heldout_token_problems(decisions_text: str) -> list[str]:
    """The decision rows whose third cell begins (after spaces, backticks and emphasis marks) with a held-out
    token-like string (`HELDOUT_TOKEN_LIKE`) that is not exactly a token, every held-out token inside a fenced code
    block (Q-194c), and a fence never closed (Q-194d): such a row authorises nothing. [] is clean; anything else
    refuses every judged read (`LOG_RULE`). The recovery (Q-194e, Q-194f): any later row `heldout-void: E-NNN --
    <reason>` clears the problem of a malformed row E-NNN (a pin on it still pins) or of a fenced token row E-NNN, and
    closes a fence whose nearest row above is E-NNN at the void row's end (`_fence_state`); it never removes a token or
    a pin."""
    out = []
    _, unclosed, voided = _fence_state(decisions_text)
    voids: dict[str, list[int]] = {}                    # a row id -> the places of every void naming it (Q-194f (c))
    for t in heldout_tokens(decisions_text, "void"):
        voids.setdefault(t.get("target"), []).append(t.pos)
    if unclosed is not None:
        out.append(f"line {unclosed + 1}: a fenced code block opened here is never closed, so every line after it is "
                   "fenced (CommonMark); the log is refused for every judged read until the fence is closed")
    for i, line, fenced in _log_lines(decisions_text):
        n = i + 1
        r = ROW.match(line)
        c = _HO_THIRD_CELL.match(line) if r else None
        if not c:
            continue
        if fenced:
            if i not in voided and not any(p > i for p in voids.get(r.group(1), ())) and \
                    any(rx.match(line) for rx in HELDOUT_TOKENS.values()):     # Q-194f (a): voidable in a fence
                out.append(f"{r.group(1)} (line {n}): a held-out token inside a fenced code block is never a token, "
                           "so it authorises nothing")
            continue
        p = _HO_MARKS.match(line, c.end()).end()
        if any(p > i for p in voids.get(r.group(1), ())) and not heldout_tokens(line):
            continue                                    # Q-194e, -f (c), (d): a malformed row voided by any later row
        if HELDOUT_TOKEN_LIKE.match(line, p) and not heldout_tokens(line):
            out.append(f"{r.group(1)} (line {n}): {ascii(line[p:p + 80])} is held-out token-like but not exactly a "
                       "token (heldout-finalists: F-NN @ <sha256> list <sha256> -- ...; heldout-window: NQ <first> to "
                       "<last> -- ...; heldout-verdict: NQ F-NN @ <sha256> -- ...; heldout-read: P-14,P-16 by "
                       "scripts/<x>.py -- ..., each the first text of the row's third cell), so it authorises nothing")
    return out


def _row_number(row: str) -> int:
    return int(row[2:])


def _row_pos(decisions_text: str, row_id: str) -> int:
    """The position of the first row `row_id` outside a fenced block, or -1 (a log without it: before every row)."""
    for i, line, fenced in _log_lines(decisions_text):
        m = ROW.match(line)
        if not fenced and m and m.group(1) == row_id:
            return i
    return -1


def _pin_rows(decisions_text: str, ref: str, sha: str) -> list[tuple[int, str]]:
    """(position, row id) of each row outside a fenced block carrying the pin of `ref` at `sha`, in file order."""
    want = f"`{ref}` sha256 `{sha}`"
    return [(i, m.group(1)) for i, line, fenced in _log_lines(decisions_text)
            if not fenced and (m := ROW.match(line)) and want in line]


def _pin_row(decisions_text: str, ref: str, sha: str) -> tuple[int, str] | None:
    """(position, row id) of the first row carrying the pin of `ref` at `sha`, or None."""
    rows = _pin_rows(decisions_text, ref, sha)
    return rows[0] if rows else None


def heldout_window(decisions_text: str, market: str, first: date, last: date) -> tuple[str, date, date]:
    """(the opening row, first day, last day) of the window a judged read of `market` from `first` to `last` is
    recorded under: the newest (latest-placed) `heldout-window` row for the market whose days contain the read's,
    else E-208's base window (the seal's first day to the judged block's last, every market). The windows the read
    touches are `heldout_windows`'."""
    rows = [t for t in heldout_tokens(decisions_text, "window")
            if t.get("market") == market and t.get("start") <= first and last <= t.get("end")]
    if rows:
        t = max(rows, key=lambda x: x.pos)
        return t.row, t.get("start"), t.get("end")
    return BASE_WINDOW_ROW, SEAL_START, JUDGED_END


def heldout_windows(decisions_text: str, market: str, first: date, last: date) -> tuple[tuple[str, int], ...]:
    """Every window a judged read of `market` from `first` to `last` touches (Q-194c, MINOR-2), as (opening row,
    position), in the log's order: each day belongs to the newest (latest-placed) `heldout-window` row for the market
    holding it, else to E-208's base window (its position -1 when the log has no E-208 row)."""
    wins = [t for t in heldout_tokens(decisions_text, "window")
            if t.get("market") == market and t.get("start") <= last and first <= t.get("end")]
    base = (BASE_WINDOW_ROW, _row_pos(decisions_text, BASE_WINDOW_ROW))
    owners: dict[tuple[str, int], None] = {}
    d = first
    while d <= last:
        cover = [t for t in wins if t.get("start") <= d <= t.get("end")]
        if cover:
            t = max(cover, key=lambda x: x.pos)
            owners[(t.row, t.pos)] = None
        else:
            owners[base] = None
        d += timedelta(days=1)
    return tuple(sorted(owners, key=lambda x: x[1]))


def _line_market(rec: dict[str, Any]) -> str | None:
    """A ledger line's market: its `heldout.market`, else the root of a bar store it read, else None (unknown)."""
    ho = rec.get("heldout") if isinstance(rec.get("heldout"), dict) else {}
    if ho.get("market"):
        return str(ho["market"])
    for f in ((rec.get("what") or {}).get("files") or []):
        m = re.search(r"data/bars/([A-Za-z0-9_]+)/", str((f or {}).get("path", "")))
        if m:
            return m.group(1)
    return None


#: the held-out template's marker and headings (Q-194d, NOTE-6), as written at wt/wt-lit 13df998
#: (`prereg/TEMPLATE_heldout_test.md`) until template v3 is pinned
HELDOUT_MARKER = "**Declaration kind: held-out test.**"
DESIGN_SEARCH_MARKER = "**Declaration kind: design search.**"
HELDOUT_HEADINGS = (
    "## 0. In plain words (for the operator)",
    "## 1. Its inputs: only the pinned searches' finalists' lists",
    "## 2. The joint order: a rule fixed now, before any search is declared",
    "## 3. The firms' states: membership fixed by an event, states decided by rule (H-1'; E-257)",
    "## 4. The k and the level",
    "## 5. The rows, in order",
    "## 6. Power at each place in the joint sequence",
    "## 7. The held-out reads",
    "## 8. What a pass and what a fail mean",
    "## 9. Anything chosen after seeing results",
)
#: a held-out declaration's path names its market: `prereg/F-NN_heldout_test_<MARKET>.md` (the template's own name)
HELDOUT_PATH = re.compile(r"prereg/F-\d+_heldout_test_(?P<market>[A-Z][A-Z0-9]{0,7})\.md")


def _marked(text: str, marker: str) -> bool:
    return any(line.startswith(marker) for line in text.splitlines())


def heldout_declaration_problems(ref: str, repo: Path, market: str) -> list[str]:
    """Why `ref` is not the one held-out declaration of `market` (Q-194d, NOTE-6) -- [] when it is: an F- file named
    `prereg/F-NN_heldout_test_<market>.md`, carrying the held-out template's marker at a line's start and every one of
    its section headings, not the design-search marker, and the only held-out-marked `prereg/F-*.md` for the market
    (a marked file whose name names no market counts for every market)."""
    text = (repo / ref).read_text(encoding="utf-8")
    out = []
    m = HELDOUT_PATH.fullmatch(ref)
    if not m or m["market"] != market:
        out.append(f"its path is not prereg/F-NN_heldout_test_{market}.md")
    if not _marked(text, HELDOUT_MARKER):
        out.append(f"it does not carry the held-out template's marker {HELDOUT_MARKER!r} at a line's start")
    lines = set(text.splitlines())
    missing = [h for h in HELDOUT_HEADINGS if h not in lines]
    if missing:
        out.append(f"it lacks the held-out template's heading(s) {missing[:3]}")
    if _marked(text, DESIGN_SEARCH_MARKER):
        out.append("it also carries the design-search marker")
    for f in sorted((repo / "prereg").glob("F-*.md")):
        rel = f"prereg/{f.name}"
        if rel == ref or not _marked(f.read_text(encoding="utf-8"), HELDOUT_MARKER):
            continue
        fm = HELDOUT_PATH.fullmatch(rel)
        if fm is None or fm["market"] == market:
            out.append(f"another held-out-marked F- file exists for {market}: {rel} (one per market)")
    return out


def _rule1_binds(ref: str, purpose: str) -> bool:
    """Whether rule 1 binds a judged read of the family branch: every family's (F-) purpose (Q-194, M-2) and a held-out
    purpose of a described reading (refused there). The registered reproduction identities (`identity`) and a
    registered design's re-read (`registered_design`) never reach this branch (E-247's rm-4; rule 3)."""
    return ref.startswith("prereg/F-") or purpose in HELDOUT_PURPOSES


def _finalists(ref: str, sha: str, text: str, what: str, purpose: str, repo: Path | None = None,
               market: str = "NQ") -> HeldOutToken:
    """Rule 1: a family's judged read, under any purpose, is honoured only under a finalists' row for exactly this
    pinned declaration, newer than its pin; a described reading never takes a held-out purpose. Each refusal names the
    purpose and the declaration."""
    fid = DECLARATION_ID.match(ref).group(1)
    who = f"the purpose {purpose!r} of {ref}"
    if not fid.startswith("F-"):
        raise HeldOutRefused(1, what, f"{who}: {ref} is a described reading; the held-out purposes "
                                      f"{HELDOUT_PURPOSES} belong to a search's held-out test, after its finalists' "
                                      "row (a token names an F- declaration only)")
    if purpose not in HELDOUT_PURPOSES:                 # Q-194e (P10): families read the search years only
        raise HeldOutRefused(1, what, f"{who}: an F- declaration reads no held-out date except as the market's one "
                                      f"held-out declaration under {HELDOUT_PURPOSES} (Q-194e; template v3: every "
                                      "family is confined to the search years 2020-01-02 to 2023-12-29)")
    probs = heldout_declaration_problems(ref, repo, market) if repo is not None else ["the tree is not known"]
    if probs:
        raise HeldOutRefused(1, what, f"{who}: an F- declaration reads a held-out date only as the one held-out "
                                      f"declaration of {market} (Q-194d, NOTE-6; Q-194e), and {'; '.join(probs)}")
    mine = [t for t in heldout_tokens(text, "finalists") if t.get("decl") == fid]
    if not mine:
        raise HeldOutRefused(1, what, f"{who}: no decision row carries a finalists' token for {fid} "
                                      f"(`heldout-finalists: {fid} @ <its sha256> list <the finalists' sha256> -- ...`, "
                                      "the first text of the row's third cell); a family reads the held-out years, "
                                      "under any purpose, only after its ordered finalists are pinned")
    same = [t for t in mine if t.get("sha") == sha]
    if not same:
        raise HeldOutRefused(1, what, f"{who}: the finalists' row(s) {[t.row for t in mine]} for {fid} carry "
                                      f"{sorted({t.get('sha')[:12] for t in mine})}, not {ref}'s sha256 {sha[:12]}")
    pin = _pin_row(text, ref, sha)
    if pin is None:
        raise HeldOutRefused(1, what, f"{who}: no decision row carries {ref}'s pin at {sha[:12]}, so the finalists' "
                                      "row cannot be shown to follow it")
    after = [t for t in same if t.pos > pin[0]]
    if not after:
        raise HeldOutRefused(1, what, f"{who}: the finalists' row(s) {[t.row for t in same]} for {fid} precede its "
                                      f"pin ({pin[1]}) or sit in its row, by their place in DECISIONS.md; the "
                                      "finalists are chosen on the search years after the pin")
    return max(after, key=lambda t: t.pos)


def _line_windows(rec: dict[str, Any]) -> set[str] | None:
    """The windows a ledger line's read touched: its `heldout.windows`, else its `heldout.window`, else None
    (unrecorded: every window)."""
    ho = rec.get("heldout") if isinstance(rec.get("heldout"), dict) else {}
    if isinstance(ho.get("windows"), list) and ho["windows"]:
        return {str(w) for w in ho["windows"]}
    if ho.get("window"):
        return {str(ho["window"])}
    return None


def _market_once(repo: Path, ref: str, market: str, windows: set[str], what: str) -> None:
    """Rule 2: a market's held-out window is read for a test by one declaration -- the first family whose judged read
    of it is ledgered; any other family's read touching it is refused, whatever its bytes or its purpose. Every window
    the read touches counts (Q-194c, MINOR-2), as does every window an earlier line touched; a line whose market or
    windows are unrecorded counts for every market or window."""
    for r in read_ledger(ledger_path(repo)):
        d = r.get("declaration") if isinstance(r.get("declaration"), dict) else {}
        if d.get("kind") != "family" or d.get("ref") == ref:
            continue
        if not (r.get("dates") or {}).get("judged_first"):
            continue
        m = _line_market(r)
        ws = _line_windows(r)
        if (m is None or m == market) and (ws is None or ws & windows):
            spent = sorted(ws & windows) if ws else sorted(windows)
            raise HeldOutRefused(2, what, f"{market}'s held-out window(s) {', '.join(spent)} were already read for a "
                                          f"test by {d.get('ref')} ({r.get('purpose')!r}, run "
                                          f"{(r.get('who') or {}).get('run_id')}); a window is read by one declaration "
                                          "per market, whatever another's bytes -- a later search reads elsewhere "
                                          "only under a row opening a new window (`heldout-window: <market> <first> "
                                          "to <last> -- ...`)")


def _commit_has_line(repo: Path, commit: Any, line: str) -> bool:
    """Whether `commit`'s DECISIONS.md holds `line`; True when the commit cannot be read (a read whose commit is not
    known is never shown to precede a row)."""
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        return True
    r = _git(repo, "show", f"{commit}:DECISIONS.md")
    if r.returncode != 0:
        return True
    return line in r.stdout.replace("\r\n", "\n").splitlines()


def _commit_holds_line(repo: Path, commit: str, line: str) -> bool | None:
    """Whether `commit`'s DECISIONS.md holds `line` exactly; None when git cannot show it."""
    r = _git(repo, "show", f"{commit}:DECISIONS.md")
    return line in r.stdout.replace("\r\n", "\n").splitlines() if r.returncode == 0 else None


def _verdict_commits(repo: Path, line: str) -> list[str] | None:
    """Every commit of HEAD's whole history, merges included, that **adds the exact line** -- whose patch against some
    parent (`git log --full-history -m -p`; a root commit against the empty tree) holds the line `+<line>` -- and whose
    own DECISIONS.md holds it (Q-194f: by the line itself, never by a count of the text, so an edit in place that keeps
    the count cannot hide the commit), oldest first, deduped; None when git cannot answer."""
    r = _git(repo, "log", "--reverse", "--full-history", "-m", "-p", "--no-color", "--no-ext-diff",
             "--format=%x00%H", "--", "DECISIONS.md")
    if r.returncode != 0:
        return None
    want = "+" + line
    out: list[str] = []
    for chunk in r.stdout.split("\x00")[1:]:
        h, _, body = chunk.partition("\n")
        h = h.strip()
        if not re.fullmatch(r"[0-9a-f]{40}", h):
            return None
        if h in out or not any(x.rstrip("\r") == want for x in body.split("\n")):
            continue
        holds = _commit_holds_line(repo, h, line)
        if holds is None:
            return None
        if holds:
            out.append(h)
    return out


def _verdict_commit(repo: Path, line: str) -> str | None:
    """The first (oldest) commit that adds `line` (`_verdict_commits`), or None."""
    hits = _verdict_commits(repo, line)
    return hits[0] if hits else None


def _committed_ledger(repo: Path, commit: str) -> set[str] | None:
    """The ledger's lines as committed at `commit` (`git show <commit>:results/read_ledger.jsonl`), or None."""
    r = _git(repo, "show", f"{commit}:{LEDGER_REL}")
    return set(r.stdout.replace("\r\n", "\n").splitlines()) if r.returncode == 0 else None


def _proper_ancestor(repo: Path, a: Any, b: str) -> bool:
    """Whether commit `a` is an ancestor of `b` and not `b` itself (`git merge-base --is-ancestor`); False when git
    cannot tell."""
    if not isinstance(a, str) or not re.fullmatch(r"[0-9a-f]{40}", a) or a == b:
        return False
    return _git(repo, "merge-base", "--is-ancestor", a, b).returncode == 0


def _ledger_raw(repo: Path) -> list[tuple[str, dict[str, Any]]]:
    """(the raw line, its record) for each line of the checkout's ledger, verified as `read_ledger` verifies it."""
    recs = read_ledger(ledger_path(repo))
    p = ledger_path(repo)
    raw = p.read_bytes().decode("utf-8").split("\n")[:-1] if recs else []
    return list(zip((x.rstrip("\r") for x in raw), recs))


def _verdict_backed(repo: Path, text: str, v: HeldOutToken, window: str, ledger: list[dict[str, Any]]) -> bool:
    """Whether a verdict token reports a held-out read that happened (Q-194c, MINOR-1): its declaration is pinned at
    its sha256, a finalists' token for the same declaration and sha256 sits after the pin and before the verdict (by
    place in DECISIONS.md), and the checkout's ledger holds that family's `heldout_test` read of `window`, of the
    verdict's market, at that sha256 under that finalists' row, in a clean run, made from a commit whose DECISIONS.md
    did not yet hold the verdict row -- and **the order is proven** (Q-194d, MINOR-1): the ledger as committed in the
    first commit that adds the verdict row already holds the line, byte for byte, and the read's commit is a proper
    ancestor of that commit. A line the running process appended itself is in no commit, so it never counts; anything
    git cannot answer fails closed. `ledger` is `_ledger_raw`'s (raw line, record) pairs."""
    fid, sha, market = v.get("decl"), v.get("sha"), v.get("market")
    pin_at = [p for ref, shas in pins(text).items() if sha in shas and (m := DECLARATION_ID.match(ref))
              and m.group(1) == fid for p, _ in _pin_rows(text, ref, sha)]
    if not pin_at:
        return False
    fins = {f.row for f in heldout_tokens(text, "finalists")
            if f.get("decl") == fid and f.get("sha") == sha and min(pin_at) < f.pos < v.pos}
    if not fins:
        return False
    vline = text.splitlines()[v.pos]
    vcommits = _verdict_commits(repo, vline)            # Q-194e: every commit adding the row, merges included
    if not vcommits:
        return False
    committed_at = {}
    for c in vcommits:
        led = _committed_ledger(repo, c)
        if led is None:
            return False
        committed_at[c] = led
    for raw, r in ledger:
        d = r.get("declaration") if isinstance(r.get("declaration"), dict) else {}
        ho = r.get("heldout") if isinstance(r.get("heldout"), dict) else {}
        who = r.get("who") if isinstance(r.get("who"), dict) else {}
        m = DECLARATION_ID.match(str(d.get("ref") or ""))
        if d.get("kind") != "family" or not m or m.group(1) != fid or d.get("sha256") != sha:
            continue
        if r.get("purpose") != HELDOUT_TEST or ho.get("market") != market or ho.get("finalists") not in fins:
            continue
        if window not in (_line_windows(r) or set()) or not (r.get("dates") or {}).get("judged_first"):
            continue
        if not (who.get("clean_run") and who.get("run_id")) or who.get("dirty"):
            continue
        if _commit_has_line(repo, who.get("commit"), vline):
            continue
        if not all(raw in committed_at[c] and _proper_ancestor(repo, who.get("commit"), c) for c in vcommits):
            continue
        return True
    return False


def _counted_verdicts(repo: Path, text: str, market: str, windows: Sequence[tuple[str, int]], rule: int, what: str,
                      why: str) -> dict[str, HeldOutToken]:
    """Rule 4 and the registered gate (Q-194b, Q-194c): for every window a read touches, the newest verdict row of
    the read's market placed after the window's opening row and backed by its held-out read (`_verdict_backed`);
    refused (under `rule`) when a window has none."""
    ledger = _ledger_raw(repo)
    verdicts = [v for v in heldout_tokens(text, "verdict") if v.get("market") == market]
    out, missing = {}, []
    for w, wpos in windows:
        try:
            good = [v for v in verdicts if v.pos > wpos and _verdict_backed(repo, text, v, w, ledger)]
        except OSError as exc:                          # Q-194e (NOTE-6): git could not even be asked
            raise HeldOutRefused(rule, what, f"git could not be asked whether a verdict row of {market}'s window {w} "
                                             f"is backed ({type(exc).__name__}: {exc}); no verdict counts -- failing "
                                             "closed") from None
        if good:
            out[w] = max(good, key=lambda x: x.pos)
        else:
            missing.append(w)
    if missing:
        raise HeldOutRefused(rule, what, f"no verdict row counts for {market}'s held-out window(s) "
                                         f"{', '.join(missing)} (`heldout-verdict: {market} F-NN @ <its LF sha256> -- "
                                         "...`, the first text of the row's third cell, placed after the window's "
                                         "opening row, for a declaration pinned at that sha256 with its finalists' "
                                         "row between, reporting that family's heldout_test read of the window "
                                         f"ledgered in a clean run before the row); {why}")
    return out


def _rd_after_verdict(repo: Path, text: str, market: str, windows: Sequence[tuple[str, int]], what: str) -> str:
    """Rule 4: a described reading reads a market's held-out window only once a counted verdict row for that market
    and every window it touches exists (`_counted_verdicts`). Returns the verdict rows, comma-joined."""
    got = _counted_verdicts(repo, text, market, windows, 4, what, "a described reading never reads the held-out "
                            "years before the market's held-out test has its verdict")
    return ",".join(got[w].row for w, _ in windows)


def _registered_heldout(declaration: str, designs: tuple[str, ...], repo: Path, what: str) -> HeldOutToken:
    """Rule 3: a registered design's read of the held-out years is admitted only by a row naming that read -- its
    `heldout-read` token naming every design read and this process's script -- inside a clean run, one run a row.
    The rows admitting earlier reads, without the token, admit no new one; those reads stay as the ledger records."""
    row = decision_row(_decisions(repo), declaration) or ""
    toks = heldout_tokens(row, "read")
    if not toks:
        raise HeldOutRefused(3, what, f"{declaration}'s row carries no `heldout-read: <designs> by scripts/<x>.py -- "
                                      "...` token: no new registered_design read of the held-out years without a row "
                                      "naming that read (earlier reads stay valid as the ledger records them)")
    t = toks[0]
    missing = [d for d in designs if d not in t.get("designs")]
    if missing:
        raise HeldOutRefused(3, what, f"{declaration}'s token names {','.join(t.get('designs'))}, not "
                                      f"{', '.join(missing)}")
    script = _main_script()
    rel = _rel(script, repo) if script else None
    if rel != t.get("script"):
        raise HeldOutRefused(3, what, f"{declaration}'s token names the read by {t.get('script')}, and this process's "
                                      f"script is {rel or script or 'none'}")
    if not _run()[0]:
        raise HeldOutRefused(3, what, f"a registered design's held-out read runs only inside a clean run, where it is "
                                      f"ledgered ({CLEAN_RUN_ENV} is not set)")
    return t


def _registered_heldout_once(repo: Path, declaration: str, what: str) -> None:
    _, run_id = _run()
    used = sorted({str((r.get("who") or {}).get("run_id")) for r in read_ledger(ledger_path(repo))
                   if r.get("purpose") == REGISTERED_DESIGN
                   and ((r.get("declaration") or {}) if isinstance(r.get("declaration"), dict) else {}).get("ref")
                   == declaration and (r.get("dates") or {}).get("judged_first")} - {run_id})
    if used:
        raise HeldOutRefused(3, what, f"{declaration} already admitted the held-out read of run {used[0]}; one row, "
                                      "one run")


def _declaration_files(declaration: Any, repo: Path) -> list[Path]:
    """The files a declaration names: an F- or RD-id's `prereg/<id>_*.md`, a path; none for a decision row."""
    s = str(declaration).replace("\\", "/")
    if E_ID.fullmatch(s):
        return []
    if F_ID.fullmatch(s):
        return sorted(repo.glob(f"prereg/{s}_*.md")) + [x for x in [repo / "prereg" / f"{s}.md"] if x.is_file()]
    q = Path(s) if Path(s).is_absolute() else repo / s
    return [q] if q.is_file() else []


def superseded_entry(path: Path, repo: Path) -> tuple[str, str] | None:
    """The `SUPERSEDED` entry a file is, by its path or by its bytes (LF sha256), else None."""
    rel = _rel(path, repo)
    sha = sha256_lf(path) if path.is_file() else None
    for entry in SUPERSEDED:
        if entry[0] == rel or (sha is not None and entry[1] == sha):
            return entry
    return None


def _refuse_superseded(declaration: Any, repo: Path, what: str) -> None:
    """The supersession rule (N-1): a read whose declaration is superseded is refused, whatever later rows exist."""
    if not SUPERSEDED or declaration is None:
        return
    for f in _declaration_files(declaration, repo):
        hit = superseded_entry(f, repo)
        if hit is not None:
            raise SupersededRefused(what, f"{_rel(f, repo) or f} is superseded ({hit[0]}, sha256 {hit[1][:12]}); a "
                                          "superseded declaration authorises no read, whatever later rows say")


def registered_for_readings(row: str, script: str | None, repo: Path) -> tuple[str, ...]:
    """The described readings (RD-NN) a registered_design read is made for: those its admitting row names, and those
    whose `prereg/RD-*.md` names the read's script."""
    ids = set(RD_ID.findall(row))
    if script:
        for f in sorted((repo / "prereg").glob("RD-*.md")):
            if script in f.read_text(encoding="utf-8"):
                m = DECLARATION_ID.search(f"prereg/{f.name}")
                if m:
                    ids.add(m.group(1))
    return tuple(sorted(ids))


def _registered_readings(text: str, row_id: str, script: str | None, repo: Path, what: str) -> tuple[str, ...]:
    """The described readings a registered_design held-out read is made for (M-3), each refused outright if
    superseded (N-1). Since Q-194b every registered held-out read waits for the verdict; the readings are named in its
    refusal and recorded on its ledger line."""
    rds = registered_for_readings(decision_row(text, row_id) or "", script, repo)
    for rd in rds:
        _refuse_superseded(rd, repo, what)
    return rds


def _call_name(node: Any) -> str | None:
    import ast
    f = node.func
    return f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else None


def _strings(node: Any) -> list[str]:
    import ast
    return [n.value for n in ast.walk(node) if isinstance(n, ast.Constant) and isinstance(n.value, str)]


def _names_results(parts: Iterable[str]) -> bool:
    return any(re.search(r"(?:^|[\\/])results(?:$|[\\/])", s) for s in parts)


def identity_write_problems(source: str) -> list[str]:
    """N-2's static check of an identity script's own text: each call that writes a result (`write_result`) or writes
    a file to a path whose literal parts name `results` -- `open` (or `.open`) in a write mode, `write_text`,
    `write_bytes`, `to_csv`, `to_parquet`, `to_json` -- as `line N: <what>`."""
    import ast
    out = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node)
        if name == "write_result":
            out.append(f"line {node.lineno}: calls write_result")
        elif name in WRITE_CALLS and _names_results(_strings(node)):
            out.append(f"line {node.lineno}: {name} to a path under results/")
        elif name == "open":
            mode = [k.value for k in node.keywords if k.arg == "mode"] + [a for a in node.args[1:2]]
            texts = [m.value for m in mode if isinstance(m, ast.Constant) and isinstance(m.value, str)]
            if any(c in m for m in texts for c in "wax+") and _names_results(_strings(node)):
                out.append(f"line {node.lineno}: open for writing under results/")
    return out


def _identity_writes(script: Path | None, what: str) -> None:
    """The identity rule (N-2): refuse an identity whose script writes to results/."""
    if script is None or not script.is_file():
        return
    probs = identity_write_problems(script.read_text(encoding="utf-8"))
    if probs:
        raise JudgedBlockSealed(f"REFUSED ({IDENTITY_WRITE_RULE}): {what}: {script.name} writes to results/ "
                                f"({'; '.join(probs)}); an identity writes pass or fail lines and nothing else")


def _exists(declaration: Any, repo: Path) -> bool:
    """A choice-block read's declaration, if it names one, exists: a decision row, an F- or RD-id, or a file of the
    tree."""
    s = str(declaration).replace("\\", "/")
    if E_ID.fullmatch(s):
        return decision_row(_decisions(repo), s) is not None
    if F_ID.fullmatch(s):
        return bool(list(repo.glob(f"prereg/{s}_*.md"))) or (repo / "prereg" / f"{s}.md").is_file()
    return (Path(s) if Path(s).is_absolute() else repo / s).is_file()


def authorise(start: Any, end: Any, *, purpose: str | None = None, declaration: Any = None,
              repeat: str | None = None, design: Any = None, repo: Path | str | None = None,
              what: str = "read", market: str = "NQ") -> Authorisation:
    """Whether a read of `start` to `end` (trading days, inclusive) of `market` may happen, and under what; raises
    otherwise. Reads nothing and writes nothing. `repo` is the tree whose `DECISIONS.md`, `prereg/`, git state and
    ledger count (this repository's root; tests pass a temporary tree). `design` (a name or a list) belongs to the
    purpose `registered_design` only."""
    tree = Path(repo).resolve() if repo is not None else ROOT
    s, e = span(start, end, what)
    if not isinstance(market, str) or not NAME.fullmatch(market):
        raise ValueError(f"a market is a root such as 'NQ', not {market!r}")
    if purpose is not None:
        _check_purpose(purpose)
    if design is not None and purpose != REGISTERED_DESIGN:
        raise ValueError(f"{what}: design= names Stage 2's registered designs for the purpose {REGISTERED_DESIGN!r} "
                         f"only, not for {purpose!r}")
    designs = _designs(design, what) if purpose == REGISTERED_DESIGN else ()
    blocks = blocks_of(s, e)
    if "judged" not in blocks:
        if declaration is not None and not _exists(declaration, tree):
            raise ReadRefused(f"REFUSED: {what}: the declaration {declaration!r} does not exist in {tree}")
        _refuse_superseded(declaration, tree, what)
        return Authorisation(s, e, blocks, False, None, None, purpose,
                             str(declaration) if declaration is not None else None, None, None, repeat, False,
                             designs, market)
    # the judged part as the judged block names it; a span inside the holiday gap alone keeps its own first day
    first = max(s, JUDGED_START) if e >= JUDGED_START else max(s, SEAL_START)
    head = f"{what} ({s} to {e}) reaches the judged block ({first} to {e})"
    if purpose is None:
        raise JudgedBlockSealed(f"REFUSED: {head} and declares no purpose. A choice-block read needs no tag; a "
                                "judged read declares its purpose and the pinned declaration that names it")
    log_probs = heldout_token_problems(_decisions(tree))
    if log_probs:                                       # Q-194d: a flaw in the log fails every judged read closed
        raise JudgedBlockSealed(f"REFUSED ({LOG_RULE}): {head}, for {purpose!r} under {declaration}: "
                                f"{log_probs[0]}" + (f" (and {len(log_probs) - 1} more)" if len(log_probs) > 1 else ""))
    if purpose == IDENTITY:
        ref = _identity(declaration, tree, head)
        inside = bool(_run()[0])                        # E-026: an identity's read is ledgered only in a clean run,
        if inside:                                      # and a clean run's marker is checked as a family read's is
            _clean_run(tree, head)
        return Authorisation(s, e, blocks, True, first, e, purpose, ref, None, "identity", repeat, inside, (), market)
    if purpose == REGISTERED_DESIGN:
        ref = _registered(declaration, designs, tree, head)
        head = f"{head}, for {purpose!r} under {ref}"            # Q-194b: refusals name the purpose, the declaration
        text = _decisions(tree)
        windows = heldout_windows(text, market, first, e)
        script = _main_script()
        rds = _registered_readings(text, ref, _rel(script, tree) if script else None, tree, head)   # M-3, N-1
        made_for = f" (made for the described reading(s) {', '.join(rds)})" if rds else ""
        verdicts = _counted_verdicts(tree, text, market, windows, 3, head,   # Q-194b/c: the verdict first
                                     f"a registered design{made_for} reads no held-out date before the joint "
                                     "held-out test's verdict, whatever row declares the read (Q-194b)")
        tok = _registered_heldout(ref, designs, tree, head)     # rule 3: a row naming this read, in a clean run
        _clean_run(tree, head)
        _registered_heldout_once(tree, ref, head)
        held = ((("read_row", tok.row),) + ((("readings", ",".join(rds)),) if rds else ())
                + (("test_verdict", ",".join(verdicts[w].row for w, _ in windows)),))
        return Authorisation(s, e, blocks, True, first, e, purpose, ref, None, REGISTERED_DESIGN, repeat, True,
                             designs, market, held)
    _refuse_superseded(declaration, tree, head)             # N-1, before the pin is even looked at
    ref, sha = _family(declaration, purpose, tree, head)
    head = f"{head}, for {purpose!r} under {ref}"        # Q-194: every later refusal names the purpose, the declaration
    text = _decisions(tree)
    windows = heldout_windows(text, market, first, e)
    window = windows[-1][0]                                     # Q-194d (NOTE-1): the newest window the read touches
    held: dict[str, Any] = {"market": market, "window": window}
    if len(windows) > 1:                                        # Q-194c: a read touching more than one window
        held["windows"] = [w for w, _ in windows]
    if _rule1_binds(ref, purpose):                      # rule 1: every family purpose after its finalists' row
        fin = _finalists(ref, sha, text, head, purpose, tree, market)   # Q-194 (M-2); Q-194d (NOTE-6)
        held.update(finalists=fin.row, finalists_list_sha256=fin.get("list"))
    kind = "described_reading" if ref.startswith("prereg/RD-") else "family"
    if kind == "described_reading":                     # rule 4: only after the market's verdict row
        held["verdict"] = _rd_after_verdict(tree, text, market, windows, head)
    if kind == "family" and repeat is not None:         # Q-194e (P9): the held-out declaration is never re-read
        raise HeldOutRefused(1, head, f"{ref} is the market's held-out declaration, read once: no repeat row is ever "
                                      f"honoured for it (repeat={repeat!r}; the held-out template's section 5, step 3)")
    _clean_run(tree, head)
    _once(tree, ref, purpose, repeat, head)
    if kind == "family":                                # rule 2: one declaration per market's window
        _market_once(tree, ref, market, {w for w, _ in windows}, head)
    return Authorisation(s, e, blocks, True, first, e, purpose, ref, sha, kind, repeat, True, (), market,
                         tuple(sorted(held.items())))


# ------------------------------------------------------------------------------------------------------- the ledger


def ledger_path(repo: Path | str | None = None) -> Path:
    return (Path(repo).resolve() if repo is not None else ROOT) / LEDGER_REL


def read_ledger(path: Path | str) -> list[dict[str, Any]]:
    """Every line of a read ledger, verified: each a JSON object with the ledger's keys, the file ending in a newline.
    An absent or empty ledger is []."""
    p = Path(path)
    if not p.is_file():
        return []
    data = p.read_bytes()
    if not data:
        return []
    if not data.endswith(b"\n"):
        raise LedgerError(f"REFUSED: {p} does not end in a newline -- a line was cut or edited; the ledger is "
                          "append-only (no judged read until the lead has looked)")
    out = []
    for i, line in enumerate(data.decode("utf-8").split("\n")[:-1], 1):
        try:
            rec = json.loads(line)
        except ValueError:
            raise LedgerError(f"REFUSED: {p} line {i} is not JSON -- the ledger was edited") from None
        if not isinstance(rec, dict) or any(k not in rec for k in LEDGER_KEYS):
            raise LedgerError(f"REFUSED: {p} line {i} lacks the ledger's fields {LEDGER_KEYS}")
        out.append(rec)
    return out


def _data_manifest(repo: Path) -> dict[str, str]:
    p = repo / DATA_MANIFEST_REL
    if not p.is_file():
        return {}
    out = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        parts = line.split(None, 1)
        if len(parts) == 2:
            out[parts[1].strip().lstrip("*")] = parts[0].lower()
    return out


def _file_entry(p: Path, repo: Path, manifest: dict[str, str]) -> dict[str, Any]:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    digest = h.hexdigest()
    rel = _rel(p, repo)
    try:
        in_vendor = Path(os.path.abspath(p)).relative_to(Path(os.path.abspath(repo / VENDOR_REL))).as_posix()
    except ValueError:
        in_vendor = None
    want = manifest.get(in_vendor) if in_vendor else None
    return {"path": rel or _sanitise(str(p), repo), "sha256": digest, "bytes": p.stat().st_size,
            "in_data_manifest": None if want is None else want == digest}


def _record(a: Authorisation, kind: str, files: Sequence[Path], columns: list[str] | None, what: str,
            repo: Path) -> dict[str, Any]:
    """Append the read's one line to the ledger (before the data is read); raises `LedgerError` if it cannot."""
    commit = _commit(repo, what)
    clean, run_id = _run()
    script = _main_script()
    manifest = _data_manifest(repo)
    rec = {
        "ledger": LEDGER_VERSION,
        "when": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "who": {"script": (_rel(script, repo) or _sanitise(str(script), repo)) if script else None,
                "argv": [_sanitise(str(x), repo) for x in sys.argv[1:]], "caller": _caller(repo),
                "commit": commit, "dirty": bool(_dirty(repo)), "pid": os.getpid(), "clean_run": clean,
                "run_id": run_id},
        "what": {"kind": kind, "files": [_file_entry(Path(f), repo, manifest) for f in files], "columns": columns,
                 "description": what},
        "dates": {"start": a.start.isoformat(), "end": a.end.isoformat(), "blocks": list(a.blocks),
                  "judged_first": a.judged_first.isoformat() if a.judged_first else None,
                  "judged_last": a.judged_last.isoformat() if a.judged_last else None},
        "declaration": {"ref": a.declaration, "sha256": a.declaration_sha256, "kind": a.kind,
                        **({"designs": list(a.designs)} if a.designs else {})},
        "purpose": a.purpose,
        "repeat": a.repeat,
    }
    if a.heldout is not None:                           # Q-158: what the held-out rules checked
        rec["heldout"] = dict(a.heldout)
    path = ledger_path(repo)
    read_ledger(path)                                   # a ledger that does not verify takes no new line
    data = (json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT | getattr(os, "O_BINARY", 0), 0o644)
        try:
            if os.write(fd, data) != len(data):
                raise OSError("short write")
            os.fsync(fd)
        finally:
            os.close(fd)
    except OSError as exc:
        raise LedgerError(f"REFUSED: {what}: the read ledger {path} cannot be written ({exc}); no judged read "
                          "without its line") from None
    return rec


def missing_lines(old: str, new: str) -> list[str]:
    """The non-blank lines of `old` not found in `new`, counted with multiplicity (order not checked: a merge
    interleaves two branches' lines)."""
    have = Counter(new.splitlines())
    out = []
    for line in old.splitlines():
        if not line.strip():
            continue
        if have[line] > 0:
            have[line] -= 1
        else:
            out.append(line)
    return out


def ledger_history_problems(repo: Path | str | None = None, rel: str = LEDGER_REL) -> list[str]:
    """Every way the ledger lost a line: a line committed anywhere in HEAD's history that is not in HEAD, and a line
    of HEAD's that is not in the working copy. [] when the ledger only ever grew (or never existed)."""
    tree = Path(repo).resolve() if repo is not None else ROOT
    if _git(tree, "rev-parse", "--git-dir").returncode:
        return [f"{tree} is not a git repository: the ledger's history cannot be checked"]
    if _git(tree, "rev-parse", "--verify", "-q", "HEAD").returncode:
        return []                                       # a repository with no commit yet has no history to keep
    log = _git(tree, "log", "--format=%H", "--", rel)
    if log.returncode:
        return [f"git log failed in {tree}: {log.stderr.strip()[:200]}"]

    def show(rev: str) -> str | None:
        r = _git(tree, "show", f"{rev}:{rel}")
        return r.stdout if r.returncode == 0 else None

    head = show("HEAD") or ""
    problems = []
    for c in log.stdout.split():
        old = show(c)
        if old is None:
            continue                                    # the commit that deleted it: its parent is checked
        miss = missing_lines(old, head)
        if miss:
            problems.append(f"{c[:10]}: {len(miss)} committed line(s) of {rel} are not in HEAD (rewritten or removed), "
                            f"e.g. {miss[0][:160]}")
    work = tree / rel
    miss = missing_lines(head, work.read_text(encoding="utf-8") if work.is_file() else "")
    if miss:
        problems.append(f"the working copy of {rel} lost {len(miss)} line(s) committed at HEAD, e.g. {miss[0][:160]}")
    return problems


# --------------------------------------------------------------------------------------------------------- the reads


def _schema(path: Path) -> list[str]:
    import pyarrow.parquet as pq

    return list(pq.read_schema(path).names)


def _columns(path: Path, columns: Sequence[str] | None, what: str) -> list[str]:
    have = _schema(path)
    if columns is None:
        return have
    cols = list(columns)
    missing = [c for c in cols if c not in have]
    if missing:
        raise KeyError(f"{what}: {path.name} has no column(s) {missing} (it has {have})")
    return cols


def read_bars(start: Any, end: Any, *, purpose: str | None = None, declaration: Any = None,
              repeat: str | None = None, columns: Sequence[str] | None = None, market: str = "NQ",
              what: str = "bar read", design: Any = None, repo: Path | str | None = None):
    """Stage 2's 1-minute bars of `market` for trading days `start` to `end` (inclusive), after the seal and Stage 2's
    own window guard (the vendored `propedge.data.bars.read_bars`, purpose `development`). A judged-block read is
    ledgered before the bars are read. `columns` selects columns (all by default)."""
    tree = Path(repo).resolve() if repo is not None else ROOT
    if not isinstance(market, str) or not NAME.fullmatch(market):
        raise ValueError(f"a market is a root such as 'NQ', not {market!r}")
    a = authorise(start, end, purpose=purpose, declaration=declaration, repeat=repeat, design=design, repo=tree,
                  what=what, market=market)
    store = tree / STORE_REL
    path = store / market / "bars.parquet"
    if not path.is_file():
        raise FileNotFoundError(f"{what}: no bar store at {path} (python scripts/vendor_stage2.py --data)")
    cols = _columns(path, columns, what)
    from extended import use_vendored_stage2

    use_vendored_stage2()
    from propedge.data.bars import read_bars as vendored_read_bars
    from propedge.data.windows import assert_readable

    assert_readable(market, a.start, a.end, "development", what=what)     # Stage 2's guard first: no line if it refuses
    if a.ledgered:
        _record(a, "bars", [path], cols, what, tree)
    df = vendored_read_bars(market, a.start.isoformat(), a.end.isoformat(), "development", store=store, what=what)
    check_returned(df["day"].unique(), a.start, a.end)
    return df[cols] if columns is not None else df


def read_walks(family: str, table: str, start: Any, end: Any, *, purpose: str | None = None,
               declaration: Any = None, repeat: str | None = None, columns: Sequence[str] | None = None,
               market: str = "NQ", what: str = "walk read", design: Any = None, repo: Path | str | None = None):
    """A table of Stage 2's atlas walks (`vendor/stage2/data/atlas/<family>/<table>.parquet`, e.g. A3 `walks`, A1
    `events`/`days`/`walks`) for dates `start` to `end` (its `date` column), after the seal and Stage 2's own window
    guard (`propedge.data.windows.assert_readable`, purpose `development`). A judged-block read is ledgered before the
    table is read."""
    tree = Path(repo).resolve() if repo is not None else ROOT
    a = authorise(start, end, purpose=purpose, declaration=declaration, repeat=repeat, design=design, repo=tree,
                  what=what, market=market)
    for x in (family, table, market):
        if not NAME.fullmatch(str(x)):
            raise ValueError(f"{what}: {x!r} is not a plain name (a family such as 'A3', a table such as 'walks')")
    path = tree / ATLAS_REL / family / f"{table}.parquet"
    if not path.is_file():
        raise FileNotFoundError(f"{what}: no walk table at {path} (python scripts/vendor_stage2.py --data)")
    cols = _columns(path, columns, what)
    if "date" not in _schema(path):
        raise KeyError(f"{what}: {path.name} has no `date` column, so its dates cannot be sealed")
    from extended import use_vendored_stage2

    use_vendored_stage2()
    from propedge.data.windows import assert_readable

    assert_readable(market, a.start, a.end, "development", what=what)
    if a.ledgered:
        _record(a, "walks", [path], cols, what, tree)
    import pandas as pd

    read = cols if "date" in cols else [*cols, "date"]
    df = pd.read_parquet(path, columns=read,
                         filters=[("date", ">=", a.start.isoformat()), ("date", "<=", a.end.isoformat())])
    check_returned(df["date"].astype(str).unique(), a.start, a.end)
    return df[cols].reset_index(drop=True)


def authorise_engine_read(start: Any, end: Any, *, files: Sequence[Path | str], what: str,
                          purpose: str | None = None, declaration: Any = None, repeat: str | None = None,
                          design: Any = None, repo: Path | str | None = None, market: str = "NQ") -> Authorisation:
    """For a runner whose reads happen inside Stage 2's engine (the identities, the U1 replay, a cell rebuilt by
    `build_cells`): the same checks as a read here, and the same ledger line, for the `files` the engine will open.
    Reads no data; call it before the engine runs. A judged read names its files and they must exist, ledgered or
    not (an identity outside a clean run, E-026)."""
    tree = Path(repo).resolve() if repo is not None else ROOT
    a = authorise(start, end, purpose=purpose, declaration=declaration, repeat=repeat, design=design, repo=tree,
                  what=what, market=market)
    paths = [Path(f) if Path(f).is_absolute() else tree / f for f in files]
    if a.judged:
        if not paths:
            raise ValueError(f"{what}: a judged-block read names the files it opens")
        absent = [str(p) for p in paths if not p.is_file()]
        if absent:
            raise FileNotFoundError(f"{what}: {absent[:3]} do not exist")
    if a.ledgered:
        _record(a, "engine", paths, None, what, tree)
    return a


__all__ = ["CHOICE_START", "CHOICE_END", "JUDGED_START", "JUDGED_END", "CONFIRMATION_START", "SEAL_START", "IDENTITY",
           "LEDGER_REL", "Authorisation", "ReadRefused", "ConfirmationWindowRefused", "JudgedBlockSealed",
           "JudgedBlockReadTwice", "LedgerError", "span", "blocks_of", "check_returned", "declared_purposes", "pins",
           "REGISTERED_DESIGN", "REGISTERED_DESIGNS", "names_design",
           "decision_row", "authorise", "read_bars", "read_walks", "authorise_engine_read", "ledger_path",
           "read_ledger", "missing_lines", "ledger_history_problems",
           "HELDOUT_TEST", "HELDOUT_STRESS", "HELDOUT_PURPOSES", "BASE_WINDOW_ROW", "RULES", "HELDOUT_TOKENS",
           "heldout_windows",
           "HeldOutRefused", "HeldOutToken", "heldout_tokens", "heldout_token_problems", "heldout_window"]
