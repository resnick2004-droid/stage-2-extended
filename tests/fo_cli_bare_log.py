"""F-03's runner (`scripts/fo_opening.py`) run through its own `main`, its waited identities read from this tree's
decision log **with every positional token row removed** (Q-109g, as Q-113 did for RD-01 in `rd01_cli_bare_log.py`):
the log gains token rows as identities hold, so a test meaning "with no token the run refuses" feeds the runner the
log as it stood before any was recorded, and the refusal holds whatever rows the lead has added since. Only the log's
text is replaced -- `opening_run.pre_run` is the runner's own, called with that text when the runner gives none;
nothing else of the runner is touched. Run by `tests/test_family_o_runner.py`:

    python tests/fo_cli_bare_log.py <repository root> [runner arguments ...]       # prints `EXIT <code>`, exits so
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(sys.argv[1])
for _p in (str(REPO), str(REPO / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import fo_opening as FO  # noqa: E402

from extended import identity_tokens as IT  # noqa: E402
from extended import opening_run as R  # noqa: E402

_log = (REPO / "DECISIONS.md").read_text(encoding="utf-8")
BARE = "".join(line + "\n" for line in _log.splitlines() if not IT.parse(line))
assert IT.parse(BARE) == [], "the log without its token rows still carries a token"
_own = R.pre_run


def _bare_pre_run(repo, *args, decisions_text: str | None = None, **kw):
    return _own(repo, *args, decisions_text=BARE if decisions_text is None else decisions_text, **kw)


R.pre_run = _bare_pre_run
_code = FO.main(sys.argv[2:])
print(f"EXIT {_code}", flush=True)
raise SystemExit(_code)
