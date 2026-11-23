"""The test suite's own memory hygiene (Q-211): two releases the root `conftest.py` makes, neither touching a test.

    from extended import suite_memory    # the root conftest's pytest_runtest_protocol calls after_test

Q-211 measured the fast tier in one process, test by test (private bytes after each test, in collection order). Two
of the things it found keep memory alive that no test needs any more; both are released here, at points where pytest
has already made and logged every report of the item, so no outcome, assertion or report can change. Both run once
a test's whole protocol has ended (`after_test`, from a wrapper of `pytest_runtest_protocol`: its reports logged,
its teardown done -- with its file's module fixtures at the file's end -- and its `funcargs` dropped, which pytest does
only after the teardown hook), the exception first, so the collection that follows can free what it held:

1. **The last raised exception** (`drop_last_exception`, after every test). pytest's
   `pytest_runtest_call` stores the exception of a call that raised -- every expected failure (`xfail`) and every
   failure -- in `sys.last_type`, `sys.last_value`, `sys.last_traceback` and (Python 3.12) `sys.last_exc`, for an
   interactive post-mortem, and deletes them only when the next test's call begins. The traceback holds the test's
   frames and so every local it had: in `tests/test_lift_bound.py` an expected failure left its large arrays alive
   through the next file's module fixtures (and, as a session's last raise, to the session's end). The reports never
   read them (`--pdb` uses the call's own exception info); nothing in this repository does. The exception and the
   frame of pytest's `CallInfo.from_call` that caught it hold each other (a reference cycle), so once dropped it is
   freed by the collection below, at the latest at the file's end.
2. **Cyclic garbage at a module's end** (`collect_at_module_end`, after an item when the next item is in another
   file, or there is none). A module-scoped fixture's value, or a file's synthetic data, that sits in a
   reference cycle is freed only by the cyclic collector, whose oldest generation runs rarely in a long session; one
   `gc.collect()` once the file's module fixtures are torn down frees it before the next file allocates its own.

What it does not release, and why (Q-211's hand-back): memory the allocator keeps after the objects are gone (Python
3.12's interned identifiers, immortal, scatter through the obmalloc arenas an AST scan used, so those arenas are never
returned), and the peak inside one test (a test's own data at once) -- neither is a holder a teardown can drop.
"""
from __future__ import annotations

import gc
import os
import sys
from pathlib import Path

#: the attributes pytest's `pytest_runtest_call` sets on a raise (`last_exc` from Python 3.12)
LAST_EXCEPTION_ATTRS = ("last_type", "last_value", "last_traceback", "last_exc")


def drop_last_exception() -> list[str]:
    """Delete `sys.last_*` (each that is set); the names deleted. Safe when none is set."""
    gone = []
    for name in LAST_EXCEPTION_ATTRS:
        if hasattr(sys, name):
            try:
                delattr(sys, name)
                gone.append(name)
            except AttributeError:                 # a race with another deleter: already gone
                pass
    return gone


def _file_of(item) -> str | None:
    path = getattr(item, "path", None)
    if path is None:
        path = getattr(item, "fspath", None)
    return None if path is None else str(Path(os.fspath(path)))


def module_ends(item, nextitem) -> bool:
    """True when `item` is the last test of its file in this run: no next item, or the next is in another file."""
    if nextitem is None:
        return True
    return _file_of(item) != _file_of(nextitem)


def collect_at_module_end(item, nextitem, collect=gc.collect) -> bool:
    """After `item`: one full collection when its file has ended (its module fixtures are torn down by then);
    whether it collected."""
    if module_ends(item, nextitem):
        collect()
        return True
    return False


def after_test(item, nextitem, collect=gc.collect) -> tuple[list[str], bool]:
    """The root conftest's call once `item`'s protocol has ended: drop the last raised exception, then collect if
    the file has ended -- in that order, so a raise's frames are free to be collected. (names deleted, whether it
    collected)"""
    gone = drop_last_exception()
    return gone, collect_at_module_end(item, nextitem, collect)


__all__ = ["LAST_EXCEPTION_ATTRS", "drop_last_exception", "module_ends", "collect_at_module_end", "after_test"]
