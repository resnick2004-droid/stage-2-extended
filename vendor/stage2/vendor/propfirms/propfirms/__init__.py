"""propfirms — multi-firm prop-firm contract modelling (see CHARTER.md).

The stage-one Topstep engine is vendored read-only at `vendor/propsim/` (D-01) and is
reached only through `propfirms.contract.adapter`.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VENDOR_PROPSIM = REPO_ROOT / "vendor" / "propsim"
FIRMS_DIR = REPO_ROOT / "firms"
RESULTS_DIR = REPO_ROOT / "results"
