"""RD-01's runner (`scripts/rd01_reading.py`) run through its own `main`, its waited identities read from this tree's
decision log **with every positional token row removed** (Q-113): the log gains token rows as identities hold, so a
test meaning "with no token the run refuses" feeds the runner the log as it stood before any was recorded, and the
refusal holds whatever rows the lead has added since. Only the log's text is replaced -- `identity_problems` is the
runner's own, called with that text; nothing else of the runner is touched. Run by `tests/test_rd01_reading.py`:

    python tests/rd01_cli_bare_log.py <repository root> [runner arguments ...]       # the runner's exit code
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(sys.argv[1])
for _p in (str(REPO), str(REPO / "identity"), str(REPO / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import rd01_reading as RDR  # noqa: E402

from extended import identity_tokens as IT  # noqa: E402

_log = (REPO / "DECISIONS.md").read_text(encoding="utf-8")
BARE = "".join(line + "\n" for line in _log.splitlines() if not IT.parse(line))
assert IT.parse(BARE) == [], "the log without its token rows still carries a token"
_own = RDR.identity_problems


def _bare_identity_problems(repo: Path = REPO, decisions_text: str | None = None):
    return _own(repo, decisions_text=BARE if decisions_text is None else decisions_text)


RDR.identity_problems = _bare_identity_problems
raise SystemExit(RDR.main(sys.argv[2:]))
