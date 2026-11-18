"""RD-05's coin identity (`prereg/RD-05_firm_modes.md` 13.1 item 1), before step 2; purpose `identity`, its own row.
It reads no bar (the coin is synthetic) and writes no result file; it prints one line per check and exits 0 only when
every item holds.

    python identity/modes_coin_identity.py                 # the declared sizes (2,000 accounts a cell; 200,000 for (b))
    python identity/modes_coin_identity.py --accounts 200  # T-11's size (a smaller run of the same checks)

* **(a)** A-0 with every addition off (`spec` None) reproduces `propsim.simulate_combine` and `simulate_xfa`, every
  output array, bit for bit, at every `(w, r)` of the grid, on the `coin_identity` seed (`[seed, w_index, r_index]`).
* **(b)** A-0 at `TS-S`'s terms (the gross steady coin at 1:1, $1,500) reproduces stage one's reference profile --
  `run_combine(Policy(rr=1.0, risk=1500.0), 0.0, 200_000, seed=2026)`, the vendored adapter's, account for account --
  and its pass probability is within 9.6's corrected two-sided width of the exact value in the vendored README.
* **(c)** every adapter's coin form against its account class, and **(d)** the base coin at `TS` against the vendored
  `CombineAccount` / `FundedAccount` and `LU` against `LucidFundedAccount`: **NOT BUILT** (part F's account classes);
  the identity cannot hold until they are, and exits 3.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()

import numpy as np  # noqa: E402

from extended import modes_engine as E  # noqa: E402
from extended import modes_oracles as O  # noqa: E402
from extended import modes_rules as R  # noqa: E402
from extended import modes_terms as M  # noqa: E402

STAGE_ONE_SEED = 2026                     # stage one's quick-reference seed (section 15, inherited; 13.1 (b) only)
STAGE_ONE_ACCOUNTS = 200_000


def item_a(n: int) -> list[str]:
    vp = E._vp
    bad = []
    for wi, w in enumerate(M.grid_w()):
        for ri, r in enumerate(M.grid_r()):
            pol, rules = vp.Policy(rr=w, risk=r), vp.Rules()
            for name, ours, theirs, kw in (("simulate_combine", E.simulate_combine, vp.simulate_combine,
                                            {"max_days": int(M.declared("horizon.eval"))}),
                                           ("simulate_xfa", E.simulate_xfa, vp.simulate_xfa,
                                            {"horizon_days": int(M.declared("horizon.funded"))})):
                a = theirs(rules, pol, 0.0, n, rng=E.stream("coin_identity", wi, ri), **kw)
                b = ours(rules, pol, 0.0, n, rng=E.stream("coin_identity", wi, ri), **kw)
                if set(a) != set(b) or any(not np.array_equal(a[k], b[k]) for k in a):
                    bad.append(f"(a) {name} at (w={w:g}, r={r:g}) differs")
    return bad


def item_b(n: int, N: int) -> list[str]:
    from propedge.contract.adapter import Policy, run_combine

    ref = run_combine(Policy(rr=1.0, risk=1500.0), 0.0, n, seed=STAGE_ONE_SEED)
    t = M.eval_terms("TS-S")
    spec = E.EvalSpec(t, 1.0, 1500.0)
    out = E.run_eval(spec, n, np.random.default_rng(STAGE_ONE_SEED), horizon=2000)
    bad = []
    if not np.array_equal(np.asarray(ref.pass_day), np.asarray(out["pass_day"])):
        bad.append("(b) A-0 at TS-S's terms differs from run_combine's pass days")
    x = int(np.sum(out["passed"]))
    if O.reference_breach(x, n, O.level(N)):
        bad.append(f"(b) the pass probability's interval at level {O.level(N):.3g} excludes "
                   f"{O.stage_one_reference()}")
    return bad


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--accounts", type=int, default=2000)
    args = ap.parse_args(argv)
    E.check_vendored_sources()
    rp = E.recomposition_problems()
    for p in rp:
        print(f"FAILED recomposition: {p}")
    N = R.oracle_count()["N"]
    a = item_a(int(args.accounts))
    print("(a) held" if not a else "\n".join(f"FAILED {x}" for x in a))
    nb = STAGE_ONE_ACCOUNTS if args.accounts >= 2000 else max(int(args.accounts) * 10, 2000)
    b = item_b(nb, N)
    print(f"(b) held at {nb} accounts" if not b else "\n".join(f"FAILED {x}" for x in b))
    print("(c) NOT BUILT: the adapters' account classes (part F) -- the identity cannot hold")
    print("(d) NOT BUILT: the base coin against CombineAccount / FundedAccount and LucidFundedAccount")
    if rp or a or b:
        return 1
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
