"""scripts/tree_peak_memory.py (Q-174): the sampler that measured the fast tier's peak for the lock's slot reserve."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "tree_peak_memory.py"

pytestmark = pytest.mark.skipif(os.name != "nt", reason="the sampler reads Windows process memory")

CHILD = ("import subprocess, sys, time; a = bytearray(150 * 2**20); "
         "subprocess.run([sys.executable, '-c', 'b = bytearray(100 * 2**20); import time; time.sleep(1.5)']); "
         "sys.exit(3)")


def test_it_sums_the_whole_tree_and_returns_the_commands_code(tmp_path):
    out = tmp_path / "peak.json"
    p = subprocess.run([sys.executable, str(SCRIPT), "--out", str(out), "--every", "0.2", "--", sys.executable, "-c",
                        CHILD], capture_output=True, text=True, timeout=120)
    assert p.returncode == 3, p.stderr
    rec = json.loads(out.read_text(encoding="utf-8"))
    assert rec["exit"] == 3 and rec["samples"] >= 3
    assert rec["peak_tree_processes"] >= 2, "the child was not counted"
    assert rec["peak_tree_working_set_gb"] >= 0.2, rec               # 150 MB + 100 MB, both alive at once


def test_attach_samples_a_running_process_until_it_exits(tmp_path):
    target = subprocess.Popen([sys.executable, "-c", "a = bytearray(120 * 2**20); import time; time.sleep(2)"])
    try:
        out = tmp_path / "peak.json"
        p = subprocess.run([sys.executable, str(SCRIPT), "--out", str(out), "--every", "0.2", "--attach",
                            str(target.pid)], capture_output=True, text=True, timeout=120)
        assert p.returncode == 0, p.stderr
        rec = json.loads(out.read_text(encoding="utf-8"))
        assert rec["samples"] >= 3 and rec["peak_tree_working_set_gb"] >= 0.1
    finally:
        target.wait(timeout=60)
