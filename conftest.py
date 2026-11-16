"""The suite's root conftest (Q-04): this repository's root on `sys.path`, so tests import the `extended` package and
the scripts' modules without an install (`pyproject.toml` is left as it is).

Nothing vendored is put on the test runner's path: a test that needs Stage 2's engine runs it in a child process
(CLAUDE.md), because `vendor/stage2/scripts` holds modules (`run_clean`, `status`) whose names this repository's
`scripts/` also uses.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
