"""A declared family is fixed by its sha256 in its decision row (E-003): the file on disk must still hash to it."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_every_declared_family_matches_its_pinned_hash():
    log = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    pins = re.findall(r"`(prereg/F-\d+[^`]*\.md)` sha256 `([0-9a-f]{64})`", log)
    assert pins, "no family pinned in DECISIONS.md"
    for rel, want in pins:
        data = (ROOT / rel).read_bytes().replace(b"\r\n", b"\n")
        assert hashlib.sha256(data).hexdigest() == want, rel
