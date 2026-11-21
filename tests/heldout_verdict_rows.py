"""Q-194b: the synthetic decision rows that make a registered design's held-out read the reader's to admit -- the
joint held-out test's declaration pinned, its finalists' token, its verdict token (`heldout-verdict: F-NN @ <sha256>
-- ...`), in that order. A test tree's log carries them when the read under test is one made after the verdict; the
reader's own refusal before the verdict is `tests/test_reader_q194b.py`'s. Synthetic only: no such declaration file is
needed (the reader checks the log's rows, not the file), and none of this repository's."""
from __future__ import annotations

HT_ID = "F-98"
HT_PATH = "prereg/F-98_heldout_test.md"
HT_SHA = "8" * 64
HT_LIST = "7" * 64
PIN_ROW = (f"| E-980 | 2026-11-19 | **{HT_ID} declared** (a synthetic joint held-out test), `{HT_PATH}` sha256 "
           f"`{HT_SHA}` | test |")
FINALISTS_ROW = f"| E-981 | 2026-11-19 | heldout-finalists: {HT_ID} @ {HT_SHA} list {HT_LIST} -- the joint list | test |"
VERDICT_ROW = f"| E-982 | 2026-11-19 | heldout-verdict: {HT_ID} @ {HT_SHA} -- the joint held-out test's verdict | test |"
#: the three rows, in order: a registered design's held-out read is admitted after them (rule 3 then decides)
VERDICT_ROWS = (PIN_ROW, FINALISTS_ROW, VERDICT_ROW)
