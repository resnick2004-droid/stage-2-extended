"""propedge — stage-two research package.

Stage two asks whether a candidate trading strategy has a demonstrated edge (e >= 0.10 net,
one-sided 95 % lower bound >= 0.05, out of sample) and, if so, which protocol maximises
long-run growth of cash under reinvestment. See CHARTER.md.

Layout
------
contract/   adapter to the vendored stage-one engine; the rules loader
execution/  instruments, fills, costs -- everything measured in contracts and ticks (D-03)
outcomes/   trade-log schema; empirical outcome distributions for the contract engine
backtest/   walk-forward harness (refuses unregistered runs); edge metrics and the criterion
campaign/   IRR of dated cash flows; calendar-time reinvestment; the protocol registry
reporting/  result files with sidecar manifests; the trace check

Conventions that hold throughout
--------------------------------
* `vendor/propsim/` is read-only. It is imported, never edited (D-01). `contract.adapter` is
  the only module that touches it.
* Every function that produces a number takes an explicit `seed` where randomness is involved.
  There is no implicit global RNG anywhere in this package.
* Costs are in contracts and ticks, never a fraction of dollar risk (D-03).
* Money decisions use the lower confidence bound of the edge, not the point estimate (D-04).
* A `NotImplementedError` in this package marks a place where a human decision or data is
  required, not an unfinished thought. Its docstring says what is needed and
  `docs/HUMAN_INPUTS.md` lists them all.
"""

__version__ = "0.1.0"

# Repository root, resolved from this file so every module agrees on where config/, results/
# and vendor/ live regardless of the working directory a script is launched from.
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = REPO_ROOT / "config"
RESULTS_DIR = REPO_ROOT / "results"
DATA_DIR = REPO_ROOT / "data"
PREREG_DIR = REPO_ROOT / "prereg"
VENDOR_PROPSIM = REPO_ROOT / "vendor" / "propsim"

__all__ = [
    "__version__",
    "REPO_ROOT",
    "CONFIG_DIR",
    "RESULTS_DIR",
    "DATA_DIR",
    "PREREG_DIR",
    "VENDOR_PROPSIM",
]
