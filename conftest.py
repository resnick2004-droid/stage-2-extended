"""The suite's root conftest (Q-04): this repository's root on `sys.path`, so tests import the `extended` package and
the scripts' modules without an install (`pyproject.toml` is left as it is).

Nothing vendored is put on the test runner's path: a test that needs Stage 2's engine runs it in a child process
(CLAUDE.md), because `vendor/stage2/scripts` holds modules (`run_clean`, `status`) whose names this repository's
`scripts/` also uses.

Q-118 (E-145): the collection hook below skips every test marked `heavy` while `run.lock` is held at the main
repository's root by a job other than this process's (`extended.lock_guard`): a heavy test never runs outside the
lock, whatever `-m` selection was given. Only the command `scripts/run_clean.py` runs under the lock (it sets
`S2X_LOCK_HOLDER=<job>`) may run them while the lock is held; when the main root cannot be found they are skipped.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def pytest_collection_modifyitems(config, items):
    heavy = [item for item in items if item.get_closest_marker("heavy") is not None]
    if not heavy:
        return                                        # no git call for a collection without a heavy test
    from extended.lock_guard import heavy_skip_reason

    reason = heavy_skip_reason(ROOT)
    if reason is None:
        return
    skip = pytest.mark.skip(reason=reason)
    for item in heavy:
        item.add_marker(skip)
