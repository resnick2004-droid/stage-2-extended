"""Q-17: the user's replay under the firm's responses (`extended/user_beside.py`), by its identities
(`identity/user_beside_identity.py`), each in its own process (the vendored tree goes on its `sys.path`).

* light (`--synthetic`): on synthetic binary-draw campaigns -- the path seed feeds only the enforcement stream; the
  seed decides the denials; all-accounts forfeiture closes everything at the denial's close, buys nothing after it,
  takes out every later arrival and passes U1's own payout and fee checks, and is the off arm where nothing is denied;
  the placement and a Focused Trader model reach the engine; the adapter refuses a non-vendored call and a flip stream;
  the binding models are the vendored grid's; the start seeds are distinct. On its six path seeds it is slow-tier
  since Q-96 (21 s); the fast tier runs the same `synthetic_problems`, every check, on the first two seeds.
* slow (`--u1-starts 4`): with every response off, the adapter reproduces `results/user_journey.csv`'s start rows for
  P-14 and P-16 at 4 starts, both arms, every column (E-010's comparison).
* Q-76, slow (`--u1-starts 4 --funded-cls both`) and heavy (`--u1-starts all --funded-cls both`): the same at the
  class keyword's default and with the gate's pass-through class given; the class run's outputs are the default's
  apart from naming. The keyword's synthetic checks are `tests/test_user_beside_class.py` (fast).
* Q-100, slow (`--u1-starts 4 --q100 both`) and heavy (`--u1-starts all --q100 both`): the same at the household route's
  and the seed base's defaults and with `household_closure=False` and `seed_base=20261920` given; the given run's
  outputs are the default's apart from naming. The keywords' synthetic checks are `tests/test_user_beside_seams.py`
  (fast).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "vendor" / "stage2" / "data"
SCRIPT = ROOT / "identity" / "user_beside_identity.py"


def run(*args: str, timeout: int = 900) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, timeout=timeout)


@pytest.mark.slow          # Q-96: 21 s; the fast tier keeps the smoke below (the same check on two path seeds)
def test_the_adapters_mechanics_on_synthetic_campaigns():
    r = run("--synthetic")
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    assert "synthetic identity HOLDS" in r.stdout, r.stdout


#: the smoke's child: the identity's own `synthetic_problems`, on the first two of its six path seeds
SYNTHETIC_SMOKE = """
import json, sys
sys.path.insert(0, {identity!r})
import user_beside_identity as UI
UI.SYN_PATH_SEEDS = UI.SYN_PATH_SEEDS[:2]
probs, seen = UI.synthetic_problems()
print(json.dumps({{"problems": probs, "seeds": list(UI.SYN_PATH_SEEDS), "denied": seen["denied"]}}))
"""


def test_the_adapters_mechanics_on_synthetic_campaigns_smoke():
    """Q-96: the fast tier's cover for the case above (slow): the identity's `synthetic_problems` -- every one of its
    checks, the not-vacuous ones included (a payout denied at 50 % on some path, two seeds giving two paths) -- on the
    first two of its six path seeds, with no problem."""
    import json

    code = SYNTHETIC_SMOKE.format(identity=str(ROOT / "identity"))
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    out = json.loads(r.stdout.strip().splitlines()[-1])
    assert out["problems"] == [], out["problems"][:12]
    assert len(out["seeds"]) == 2 and any(d > 0 for d in out["denied"]), out


@pytest.mark.slow
@pytest.mark.heavy         # Q-134: reads the real bars or atlas; the lock guard skips it while run.lock is held
def test_every_response_off_reproduces_u1s_start_rows():
    if not ((DATA / "bars").is_dir() and (DATA / "atlas").is_dir()):
        pytest.skip("bars and atlas not copied (scripts/vendor_stage2.py --data)")
    r = run("--u1-starts", "4", timeout=1800)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    assert r.stdout.count("identity HOLDS: Q-17 U1") == 2, r.stdout


@pytest.mark.slow
@pytest.mark.heavy         # Q-134: reads the real bars or atlas; the lock guard skips it while run.lock is held
def test_u1s_start_rows_at_the_class_keywords_default_and_with_the_pass_through_class():
    """Q-76: the same identity at `funded_account_cls`'s default and with the gate's pass-through class given -- U1's
    start rows for both, and the class run's outputs the default's bit for bit apart from its naming."""
    if not ((DATA / "bars").is_dir() and (DATA / "atlas").is_dir()):
        pytest.skip("bars and atlas not copied (scripts/vendor_stage2.py --data)")
    r = run("--u1-starts", "4", "--funded-cls", "both", timeout=3600)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    assert r.stdout.count("identity HOLDS: Q-17 U1") == 2, r.stdout
    assert r.stdout.count("and with the pass-through class (Q-76)") == 2, r.stdout


@pytest.mark.heavy
def test_u1s_start_rows_every_start_at_the_class_keywords_default_and_with_the_pass_through_class():
    """Q-76, heavy (the run lock; the lead's): the same at every start of P-14 and P-16, both arms, all 68 columns."""
    if not ((DATA / "bars").is_dir() and (DATA / "atlas").is_dir()):
        pytest.skip("bars and atlas not copied (scripts/vendor_stage2.py --data)")
    r = run("--u1-starts", "all", "--funded-cls", "both", timeout=4 * 3600)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    assert r.stdout.count("identity HOLDS: Q-17 U1") == 2, r.stdout
    assert r.stdout.count("and with the pass-through class (Q-76)") == 2, r.stdout


@pytest.mark.slow
@pytest.mark.heavy         # Q-134: reads the real bars or atlas; the lock guard skips it while run.lock is held
def test_u1s_start_rows_at_q100s_defaults_and_with_its_keywords_given():
    """Q-100: the same identity at `household_closure`'s and `seed_base`'s defaults and with `household_closure=False`
    and `seed_base=20261920` given -- U1's start rows for both, and the given run's outputs the default's bit for bit
    apart from its naming (`identity/user_beside_identity.py --q100 both`)."""
    if not ((DATA / "bars").is_dir() and (DATA / "atlas").is_dir()):
        pytest.skip("bars and atlas not copied (scripts/vendor_stage2.py --data)")
    r = run("--u1-starts", "4", "--q100", "both", timeout=3600)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    assert r.stdout.count("identity HOLDS: Q-17 U1") == 2, r.stdout
    assert r.stdout.count("and with Q-100's household_closure=False, seed_base=20261920 given") == 2, r.stdout


@pytest.mark.heavy
def test_u1s_start_rows_every_start_at_q100s_defaults_and_with_its_keywords_given():
    """Q-100, heavy (the run lock; the lead's): the same at every start of P-14 and P-16, both arms, all 68 columns --
    E-010's comparison at the keywords' defaults and with them given."""
    if not ((DATA / "bars").is_dir() and (DATA / "atlas").is_dir()):
        pytest.skip("bars and atlas not copied (scripts/vendor_stage2.py --data)")
    r = run("--u1-starts", "all", "--q100", "both", timeout=4 * 3600)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    assert r.stdout.count("identity HOLDS: Q-17 U1") == 2, r.stdout
    assert r.stdout.count("and with Q-100's household_closure=False, seed_base=20261920 given") == 2, r.stdout


@pytest.mark.slow
@pytest.mark.heavy         # Q-134: reads the real bars or atlas; the lock guard skips it while run.lock is held
def test_the_readings_pipeline_on_four_starts():
    """`scripts/user_beside.py --check`: the identity first, every reading's refusing checks, both files written with
    their manifests to a temporary folder and read back through their hashes -- one response of each kind."""
    if not ((DATA / "bars").is_dir() and (DATA / "atlas").is_dir()):
        pytest.skip("bars and atlas not copied (scripts/vendor_stage2.py --data)")
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "user_beside.py"), "--check", "--starts", "4",
                        "--designs", "p14", "--responses", "off,denial_50,forfeit_10,rtp,ftp_corrective_lost_3"],
                       capture_output=True, text=True, timeout=1800)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    assert "every identity holds; the pipeline ran" in r.stdout, r.stdout
    assert "FAILS" not in r.stdout and r.stdout.count("identity HOLDS") == 11, r.stdout


@pytest.mark.slow
@pytest.mark.heavy         # Q-134: reads the real bars or atlas; the lock guard skips it while run.lock is held
def test_the_comparison_refuses_a_response_switched_on():
    """The negative control: the same comparison with the placement on (P-14, 4 starts) must be refused."""
    if not ((DATA / "bars").is_dir() and (DATA / "atlas").is_dir()):
        pytest.skip("bars and atlas not copied (scripts/vendor_stage2.py --data)")
    r = run("--u1-starts", "4", "--configs", "p14", "--control", "rtp", timeout=1800)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    assert "negative control HOLDS" in r.stdout, r.stdout
