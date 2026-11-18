"""RD-05's coin identity (`prereg/RD-05_firm_modes.md` 13.1 item 1), before step 2; purpose `identity`, its own row.
It reads no bar (the coin is synthetic) and writes no result file; it prints one line per check and exits 0 only when
every item holds.

    python identity/modes_coin_identity.py                 # the declared sizes (2,000 accounts a cell; 200,000 for (b))
    python identity/modes_coin_identity.py --accounts 200  # T-11's size (a smaller run of the same checks)

* **(a)** A-0 with every addition off (`spec` None) reproduces `propsim.simulate_combine` and `simulate_xfa`, every
  output array, bit for bit, at every `(w, r)` of the grid, on the `coin_identity` seed (`[seed, w_index, r_index]`);
  **and with the specs on at Topstep's terms** (S-2; 4.3's "every switch at its Topstep setting"): `EvalSpec(TS-S)`,
  `FundedSpec(TS/con)` and `FundedSpec(TS/std)` with A-16 off (the one listed difference) against the vendored
  functions at Stage 2's `rules_from_ledger()`, every vendored output array, at every `(w, r)`.
* **(b)** A-0 at `TS-S`'s terms (the gross steady coin at 1:1, $1,500) reproduces stage one's reference profile --
  `run_combine(Policy(rr=1.0, risk=1500.0), 0.0, 200_000, seed=2026)`, the vendored adapter's, every array of its
  raw result account for account (S-2) -- and its pass probability is within 9.6's corrected two-sided width of the
  exact value in the vendored README.
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
#: 13.1 (b)'s reference profile as the skill's quick reference states it (stage one's, not a rule read here)
REFERENCE_PROFILE: dict[str, float] = {"rr": 1.0, "risk": 1500.0, "max_days": 2000, "min_accounts": 2000,
                                       "scale": 10}


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


def item_a_specs(n: int) -> list[str]:
    """S-2: the specs on at Topstep's terms against the vendored functions at `rules_from_ledger()`."""
    from dataclasses import replace

    from propedge.contract.adapter import rules_from_ledger

    vp = E._vp
    led = rules_from_ledger()
    bad = []
    for wi, w in enumerate(M.grid_w()):
        for ri, r in enumerate(M.grid_r()):
            pol = vp.Policy(rr=w, risk=r)
            a = vp.simulate_combine(led, pol, 0.0, n, rng=E.stream("coin_identity", wi, ri),
                                    max_days=int(M.declared("horizon.eval")))
            b = E.run_eval(E.EvalSpec(M.eval_terms("TS-S"), w, r), n, E.stream("coin_identity", wi, ri))
            if any(not np.array_equal(a[k], b[k]) for k in a):
                bad.append(f"(a) EvalSpec(TS-S) at (w={w:g}, r={r:g}) differs")
            for mode in ("TS/con", "TS/std"):
                t = M.funded_terms(mode)
                if mode == "TS/std":
                    t = replace(t, request_day_excluded=False)                 # the listed difference, off
                fs = E.FundedSpec(t, w, r)
                a = vp.simulate_xfa(led, fs.policy_obj(), 0.0, n, rng=E.stream("coin_identity", wi, ri),
                                    horizon_days=int(M.declared("horizon.funded")))
                b = E.run_funded(fs, n, E.stream("coin_identity", wi, ri))
                if any(not np.array_equal(a[k], b[k]) for k in a):
                    bad.append(f"(a) FundedSpec({mode}) at (w={w:g}, r={r:g}) differs")
    return bad


def item_b(n: int, N: int) -> list[str]:
    from propedge.contract.adapter import Policy, run_combine

    rp = REFERENCE_PROFILE
    ref = run_combine(Policy(rr=rp["rr"], risk=rp["risk"]), 0.0, n, seed=STAGE_ONE_SEED)
    t = M.eval_terms("TS-S")
    spec = E.EvalSpec(t, rp["rr"], rp["risk"])
    out = E.run_eval(spec, n, np.random.default_rng(STAGE_ONE_SEED), horizon=int(rp["max_days"]))
    bad = []
    for k, v in ref.raw.items():                                               # S-2: every array
        if not np.array_equal(np.asarray(v), np.asarray(out[k])):
            bad.append(f"(b) A-0 at TS-S's terms differs from run_combine's {k}")
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
    a = item_a(int(args.accounts)) + item_a_specs(int(args.accounts))
    print("(a) held" if not a else "\n".join(f"FAILED {x}" for x in a))
    rp = REFERENCE_PROFILE
    lo = int(rp["min_accounts"])
    nb = STAGE_ONE_ACCOUNTS if args.accounts >= lo else max(int(args.accounts) * int(rp["scale"]), lo)
    b = item_b(nb, N)
    print(f"(b) held at {nb} accounts" if not b else "\n".join(f"FAILED {x}" for x in b))
    print("(c) NOT BUILT: the adapters' account classes (part F) -- the identity cannot hold")
    print("(d) NOT BUILT: the base coin against CombineAccount / FundedAccount and LucidFundedAccount")
    if rp or a or b:
        return 1
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
