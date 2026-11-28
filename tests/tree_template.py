"""Q-226 (the fast tier's time): a synthetic git tree built once a process and copied for each test that asks for it.

Several reader test files build the same small repository for every test (a dozen files, `git init`, three `git
config`, `git add`, `git commit`: about half a second each on this machine, hundreds of times a tier). `copied` builds
it once for a key -- everything the builder reads besides the key is a module constant -- under a temporary folder of
its own, and gives each test a full copy (`shutil.copytree`, the `.git` folder with it) at the very path the builder
would have made, then refreshes the copy's index (`git update-index -q --refresh`) so its stat data are the copy's own,
as a tree just committed has them. Each test still gets a tree of its own that no other test sees; only the commit's
timestamp (and so its hash) is shared among the copies of one key, as it was never asserted.
"""
from __future__ import annotations

import atexit
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable, Hashable

_BUILT: dict[Hashable, Path] = {}


def copied(key: Hashable, build: Callable[[Path], Path], dest: Path) -> Path:
    """`dest`, a copy of the tree `build(<a base folder>)` returns for `key` (built on the first call only)."""
    src = _BUILT.get(key)
    if src is None:
        base = Path(tempfile.mkdtemp(prefix="s2x_tree_template_"))
        atexit.register(shutil.rmtree, base, True)
        src = _BUILT[key] = build(base)
    shutil.copytree(src, dest, symlinks=True)
    subprocess.run(["git", "update-index", "-q", "--refresh"], cwd=dest, capture_output=True, text=True, check=False)
    return dest
