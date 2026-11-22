"""Q-211: the suite's memory hygiene (`extended.suite_memory`, wired into the root `conftest.py`).

Two layers, as tests/test_heavy_guard.py does for the lock guard: the functions on their own, and the real root
`conftest.py` copied into a temporary tree and run by pytest in a child process -- once as it is, once with an empty
conftest, so the child's probes are shown to fail without the hooks (the test is not vacuous). The child's probes:

- a file whose expected failure (`xfail`) raises while holding an object, then a second file whose module fixture --
  set up before that file's first call, so before pytest's own deletion of `sys.last_*` -- checks the object is
  already gone and `sys.last_value` is unset;
- a file whose module fixture holds an object inside a reference cycle (with the automatic collector switched off, so
  only an explicit collection can free it), then a file whose module fixture checks the cycle was collected once the
  first file's fixtures were torn down.

Nothing here reads the bars; the child runs on synthetic files only.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from extended import suite_memory as SM

ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------------------------- the functions

@pytest.fixture
def last_attrs():
    """sys.last_* as they were, put back afterwards (monkeypatch cannot: the code under test deletes them)."""
    saved = {n: getattr(sys, n) for n in SM.LAST_EXCEPTION_ATTRS if hasattr(sys, n)}
    for n in SM.LAST_EXCEPTION_ATTRS:
        if hasattr(sys, n):
            delattr(sys, n)
    yield
    for n in SM.LAST_EXCEPTION_ATTRS:
        if hasattr(sys, n):
            delattr(sys, n)
    for n, v in saved.items():
        setattr(sys, n, v)


def test_drop_last_exception_deletes_every_attribute_set(last_attrs):
    for name in SM.LAST_EXCEPTION_ATTRS:
        setattr(sys, name, object())
    gone = SM.drop_last_exception()
    assert gone == list(SM.LAST_EXCEPTION_ATTRS)
    assert not any(hasattr(sys, name) for name in SM.LAST_EXCEPTION_ATTRS)


def test_drop_last_exception_is_safe_when_nothing_or_only_some_is_set(last_attrs):
    assert SM.drop_last_exception() == []
    sys.last_value = ValueError("x")                       # pytest's own deletion may leave one alone
    assert SM.drop_last_exception() == ["last_value"]
    assert not hasattr(sys, "last_value")


def test_the_attributes_are_the_ones_pytest_sets():
    import inspect

    from _pytest import runner

    src = inspect.getsource(runner.pytest_runtest_call)
    for name in SM.LAST_EXCEPTION_ATTRS:
        assert f"sys.{name} =" in src, name


def _item(path: str | None):
    return SimpleNamespace(path=None if path is None else Path(path))


def test_module_ends_at_the_last_item_of_a_file_and_at_the_session_end():
    a1, a2, b1 = _item("t/test_a.py"), _item("t/test_a.py"), _item("t/test_b.py")
    assert SM.module_ends(a1, a2) is False
    assert SM.module_ends(a2, b1) is True
    assert SM.module_ends(b1, None) is True
    legacy = SimpleNamespace(fspath="t/test_a.py")                     # an item with only the old path attribute
    assert SM.module_ends(legacy, _item("t/test_a.py")) is False


def test_collect_at_module_end_collects_only_there():
    calls = []
    a1, a2, b1 = _item("t/test_a.py"), _item("t/test_a.py"), _item("t/test_b.py")
    assert SM.collect_at_module_end(a1, a2, collect=lambda: calls.append(1)) is False
    assert calls == []
    assert SM.collect_at_module_end(a2, b1, collect=lambda: calls.append(1)) is True
    assert SM.collect_at_module_end(b1, None, collect=lambda: calls.append(1)) is True
    assert calls == [1, 1]


def test_after_test_drops_the_exception_before_it_collects(last_attrs):
    sys.last_value = ValueError("x")
    seen = []
    gone, collected = SM.after_test(_item("t/test_a.py"), None, collect=lambda: seen.append(hasattr(sys, "last_value")))
    assert gone == ["last_value"] and collected is True
    assert seen == [False]                                   # the collection ran with the exception already dropped
    sys.last_value = ValueError("y")
    gone, collected = SM.after_test(_item("t/test_a.py"), _item("t/test_a.py"), collect=lambda: seen.append(1))
    assert gone == ["last_value"] and collected is False and seen == [False]


def test_the_root_conftest_wires_the_protocol_hook():
    import conftest as C

    assert callable(getattr(C, "pytest_runtest_protocol", None))
    src = (ROOT / "conftest.py").read_text(encoding="utf-8")
    assert "suite_memory.after_test(item, nextitem)" in src


# ---------------------------------------------------------------------------- the real conftest, in a child pytest

STATE = '''import weakref
held = {}
'''

#: the first file: an expected failure raised while its frame holds an object; the probe keeps only a weak reference
XFAIL = '''import pytest
import probe_state


class Big:
    pass


@pytest.mark.xfail(strict=True, reason="raises on purpose, holding `big`")
def test_raises_while_holding():
    big = Big()
    probe_state.held["xfail"] = probe_state.weakref.ref(big)
    assert big is None
'''

#: the next file: its module fixture is set up before its first call, so before pytest itself deletes sys.last_*
AFTER_XFAIL = '''import sys
import pytest
import probe_state


@pytest.fixture(scope="module")
def checked():
    return probe_state.held["xfail"]() is None, hasattr(sys, "last_value")


def test_the_raise_frees_its_frame_before_the_next_file_sets_up(checked):
    freed, still_set = checked
    assert freed and not still_set, checked
'''

#: a file whose module fixture holds an object in a reference cycle, with the automatic collector off
CYCLE = '''import gc
import pytest
import probe_state


class Node:
    pass


@pytest.fixture(scope="module")
def cyclic():
    gc.disable()
    a, b = Node(), Node()
    a.other, b.other = b, a
    probe_state.held["cycle"] = probe_state.weakref.ref(a)
    yield a


def test_uses_the_cycle(cyclic):
    assert cyclic.other.other is cyclic
'''

AFTER_CYCLE = '''import gc
import pytest
import probe_state


@pytest.fixture(scope="module")
def checked():
    freed = probe_state.held["cycle"]() is None
    gc.enable()
    return freed


def test_the_cycle_is_collected_once_its_file_has_ended(checked):
    assert checked
'''

PYPROJECT = '''[tool.pytest.ini_options]
testpaths = ["tests"]
markers = ["heavy: reads the full bars", "slow: the engine"]
'''


def _tree(d: Path, conftest: str) -> None:
    files = {"conftest.py": conftest, "pyproject.toml": PYPROJECT, "tests/probe_state.py": STATE,
             "tests/test_a_xfail.py": XFAIL, "tests/test_b_after_xfail.py": AFTER_XFAIL,
             "tests/test_c_cycle.py": CYCLE, "tests/test_d_after_cycle.py": AFTER_CYCLE}
    for rel, text in files.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")


def _child(d: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.update(PYTHONPATH=str(ROOT), PYTHONDONTWRITEBYTECODE="1", OMP_NUM_THREADS="1")
    env.pop("PYTEST_ADDOPTS", None)
    return subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-p", "no:randomly",
                           "-o", "addopts="], cwd=d, env=env, capture_output=True, text=True, timeout=300)


def test_the_root_conftest_frees_both_holders_in_a_child_pytest(tmp_path):
    real = tmp_path / "real"
    _tree(real, (ROOT / "conftest.py").read_text(encoding="utf-8"))
    out = _child(real)
    assert out.returncode == 0, out.stdout + out.stderr
    assert "3 passed, 1 xfailed" in out.stdout, out.stdout


def test_without_the_hooks_both_probes_fail(tmp_path):
    bare = tmp_path / "bare"
    _tree(bare, "")
    out = _child(bare)
    assert out.returncode == 1, out.stdout + out.stderr
    assert "2 failed, 1 passed, 1 xfailed" in out.stdout, out.stdout
    assert "test_the_raise_frees_its_frame_before_the_next_file_sets_up" in out.stdout
    assert "test_the_cycle_is_collected_once_its_file_has_ended" in out.stdout
