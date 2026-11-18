---
name: contract-engine
description: How to use Stage 2's vendored engine in this repository -- importing it from vendor/stage2 in its own process, its defaults that point at the read-only tree, the identity that must hold first, the stage-one adapter and its pluggable outcome draw -- and the settled stage-one facts with their sources. Use when simulating evaluation or funded accounts, replaying a design over start days, building an outcome distribution, or citing a Stage 2 or stage-one number.
---

# The contract engine

**Stage 2 is vendored read-only at `vendor/stage2/`** (snapshot of commit f1b42e2, 698 files pinned by
`vendor/MANIFEST_stage2.sha256`, E-002): its engine `vendor/stage2/propedge/`, its runners `vendor/stage2/scripts/`,
its configuration and verified rules ledger `vendor/stage2/config/` and `vendor/stage2/RULES_LEDGER.md`, its results
(evidence, read-only) `vendor/stage2/results/`, and stage one's engine `vendor/stage2/vendor/propsim/` inside it. It is
**imported, never edited.** A hook denies writes under any `vendor/` (in this tree, every worktree and every clean
checkout), and `tests/test_vendor_integrity.py` and `python scripts/vendor_stage2.py --verify` check every byte.

If the engine needs to behave differently, the change goes in **this repository's own package (`extended/`)** as an
adapter, wrapper or subclass -- never in the vendored tree. A newer Stage 2 is a new snapshot under a new decision row.

## Importing it

Run anything that imports the vendored engine **in its own process** (a script or a subprocess, as
`tests/test_stage2_identity.py` runs `identity/stage2_identity.py`), set up as the identity's `_setup` does:

```python
import os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]           # this repository (or the clean checkout it runs from)
VENDORED = ROOT / "vendor" / "stage2"
for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(k, "1")                    # one BLAS thread per process (Stage 2 D-464 (5))
sys.path.insert(0, str(VENDORED))
sys.path.insert(0, str(VENDORED / "scripts"))        # Stage 2's runners import each other as top-level modules
sys.dont_write_bytecode = True                       # no __pycache__ in the vendored tree
```

**Its defaults point at the vendored tree**, because `propedge/__init__.py` resolves them from its own location:
`propedge.REPO_ROOT` is `vendor/stage2/`, `RESULTS_DIR` is `vendor/stage2/results/` (Stage 2's evidence: read it,
never write it), `CONFIG_DIR` is `vendor/stage2/config/` (so the rules are Stage 2's verified ledger), and
`VENDOR_PROPSIM` is `vendor/stage2/vendor/propsim/`. So: read through those defaults freely; **write only through this
repository's paths** -- results through `extended.results.write_result` (skill `result-provenance`), never the vendored
`write_result` with its defaults.

Heavy work -- anything that reads the full bars, a solve, a campaign, the engine beyond a few paths -- runs one at a
time on the machine, under `run.lock` (skill `run-lock`), from a clean checkout, watched to its end. Memory decides
concurrency: a Stage 2 family run peaked near 3 GB.

## The identity first, refusing

`identity/stage2_identity.py` reproduces P-14's and P-16's registered gate rows path for path (every
`zero_edge_decomposition.PATH_COLS` column, point and bound, to 1e-6): 4 paths in the suite, all 500 from a clean
clone (E-002, E-004). U1's start rows for P-14 and P-16 (`vendor/stage2/results/user_journey.csv`, section `start`) are
not yet reproduced (TASK_QUEUE Q-05); **until they are, no result of this repository is believed.** Every new runner
has its own identity against Stage 2's files before any outcome of it is read: with nothing added, a design built on
P-16's schedule reproduces P-16's registered paths.

The identity's own source is the best guide to calling the engine exactly as a registered row was made: P-14 through
`rc_screen.identity_problems`; P-16 through `rc150_dev_test.SPEC`, `atlas_a3.bounds`, `score_fv3_grid.gate_blocks`,
`portfolio_stage.composed_hook`, `atlas_a3.gate_kwargs` and `propedge.campaign.gate.run_gate`. The user-journey replay
over start days (P and the scorecard, Stage 2 D-620, D-621) is `vendor/stage2/scripts/user_journey.py`;
`vendor/stage2/docs/USER_MILESTONES.md` defines every measure.

## The stage-one adapter

Stage 2's seam to stage one's engine is `propedge.contract.adapter` (vendored):

```python
from propedge.contract.adapter import Policy, Rules, run_combine, run_xfa, keep_balance_policy

res = run_combine(Policy(rr=2.0, risk=750.0), edge=0.10, n=100_000, seed=SEED)
res.p_pass, res.mean_days, res.mean_sub_fees
res.pass_day                      # 0-based day each account passed, or -1

funded = run_xfa(keep_balance_policy(1.5, 500.0, keep_balance=8000.0),
                 edge=0.10, n=50_000, seed=SEED, horizon_days=504)
funded.mean_cash, funded.p_any_payout, funded.mean_days_to_first_payout
```

`seed` is **required** -- there is no default-RNG path. A result you cannot reproduce is not a result.

`keep_balance_policy` refuses `rr <= 1`. Construct a `Policy` directly only to reproduce stage one's 1:1 reference
number. `rules_from_ledger()` builds engine `Rules` from Stage 2's `config/rules.yaml` and **raises** for any rule it
needs that is not verified there; a rule verified only in this repository's `config/rules_extended.yaml` reaches the
engine only through an adapter in `extended/`, under its decision row.

## The pluggable draw

Both adapter entry points accept an outcome draw:

```python
draw(n, day, slot, cushion) -> np.ndarray of shape (n,), dollars of P&L
```

`cushion` is `balance - floor` per account; `np.nan` means "no trade in this slot" and is how a day ends early. **The
draw must not enforce the floor** -- the engine applies `np.maximum(pnl, -cushion)` itself when
`rules.liquidate_at_floor`, so a draw that also clamped would truncate twice.

| draw | use |
|---|---|
| `propedge.contract.adapter.BinaryDraw` | Stage one's binary process, with an explicit seed; delegates to the vendored `RandomDraw`, so the floor barrier race and the drift solve are the engine's. Use it to reproduce stage one's numbers |
| `propedge.outcomes.distribution.EmpiricalDraw` | Resampled by day from a trade log |
| `propedge.outcomes.distribution.BinaryOutcomeDraw` | A plain binary process on the same interface, to show the empirical machinery reduces to the binary limit |

`EmpiricalDraw` resamples **whole days**, preserves **intra-day order** and preserves the **15:10 CT flatten**: by day,
because trades within a day share a regime (resampling trades would understate variance, in the optimistic direction);
in order, because the engine applies the floor intraday and ratchets at the 16:00 CT lock; flatten preserved, because
a trade closed at 15:10 CT ends at whatever the market gave (`vendor/stage2/vendor/propsim/HANDOFF.md` section 3:
"record their actual P&L, do not assume binary"). Set the engine's `trades_per_day` to at least
`EmpiricalDraw.max_trades_per_day`, or trades are silently dropped.

## Settled stage-one facts, with sources

Inputs, not findings to re-derive. Cite the file; never retype the number into a document.

### Contract ceilings (zero edge, analytic) -- use as **oracles**

| quantity | value | source |
|---|---|---|
| Combine P(pass), any fair strategy | <= 2/5 | propsim D-02; `vendor/stage2/vendor/propsim/README.md` |
| Funded gross payouts, any fair strategy | <= $2,000 | the martingale bound on balance plus payouts |
| Supremum of P(pass) over **all** fair strategies | 2000^2 / (3350 x 3650) | `vendor/stage2/vendor/propsim/optimality/results_combine_supremum.csv` |
| Best static profile, 1:1 at $1,500 | 16/49, exact Markov chain | `vendor/stage2/vendor/propsim/README.md`; `edge/combine_exact.py` |

A result outside a ceiling is an **engine error, never a finding** -- on the martingale-outcome reading. An as-walked
(reflected) result outside one is the design's path-structure edge, reported beside the verdict, never booked as an
engine error and never "fixed" (CHARTER section 4, amended E-210).

### The criteria, old and current

Stage one's research criterion -- e >= 0.10 net, one-sided 95 % lower bound >= 0.05, out of sample (propsim D-47) -- was
reopened as a gate by Stage 2 D-145 and is **reported beside, never this repository's pass line**. From E-210 this
repository judges a design on the user's journey under zero edge (CHARTER sections 2-3; skill `prereg-discipline`):
on the martingale-outcome reading -- each trade's outcome redrawn at its bracket's driftless first-exit odds against
the nearer barrier, as `adapter.BinaryDraw` does with `edge = 0` -- inside the operator's limits, each baseline beaten
on the pinned composite by the calibrated paired test on the held-out years, with the zero-edge long-run gate as a
floor. Stage 2 D-621 (3) and R\* = P-14 as the row to beat are on record and no longer decide (CHARTER 3.10).

### Sample size

`vendor/stage2/vendor/propsim/edge/results_sample_size.csv` gives the trades a demonstrated e needs at each R -- years
at one trade a day. This is why long histories are needed, why six and a half years of NQ give low power for rare
effects, and why a short live record checks execution, not edge.

### Payout policy is first-order -- but stage one's value is a hint, not a setting

propsim D-45: any payout drops the funded floor to $0, so an early payout strands a small balance. Stage one's best
buffer (`vendor/stage2/vendor/propsim/edge/T5_RESULTS.md` section 3) was exploratory (propsim D-44), on a coarse grid,
and priced no payout latency, reinvestment or per-contract costs. Do not adopt it as a parameter. Stage 2 tested payout
policy for long-run growth only (the handoff, section 3.3); a payout family for a user's first months is one of this
repository's later sides (`TASK_QUEUE.md`), declared in its own row before it is built.

### What stage one did not model

Commissions (folded into a negative edge), contract caps and stop distance, the DLL arm, Back2Funded chaining,
Prohibited Conduct review, cross-account correlation. Stage 2's `propedge/execution/` closes the first two -- in
contracts and ticks, never as a fraction of dollar risk (Stage 2 D-03).

### Conduct

Stage 2 D-145's three tiers supersede stage one's list of bans (it reopened propsim D-34): **tier 1 hard** -- no hedging
across accounts or firms, no simulator-fill exploitation or tight-bracket scalping, no maximum size into major news, no
copying one trade across accounts, nothing that conceals a pattern; **tier 2 modelled** -- the Responsible Trading
Program's triggers and consequences, off in the base case (D-289); **tier 3 priced** -- account stacking and many
purchases, payouts denied with a stated probability, 0 % in the verdict and 10, 25, 50 % beside (D-234).
`vendor/stage2/propedge/campaign/conduct.py` is the one source. Candidates are never ranked or modified by
**detectability** (propsim D-35): a slower or smaller version of a prohibited pattern is still the prohibited pattern.
And no automated or API order entry, ever: every design is traded by hand, at least L minutes from alert to order
(L declared: five the reference, three and two counted variants, E-202 (2)(c)).

## Engine API worth knowing

From `vendor/stage2/vendor/propsim/propsim.py`, re-exported through the adapter:

- `Rules` -- contract parameters: target 3000, MLL 2000, consistency 0.55, `combine_mll_lock_at=0`,
  `xfa_mll_start=-2000`, `xfa_lock_at=0`, payout caps and split, fees, `floor_mode="truncate"`, `edge_mode="drift"`.
- `Policy` -- `rr`, `risk`, `trades_per_day`, `payout_path`, `payout_frac`, `keep_balance`.
- `p_race(a, b, theta)`, `theta_from_edge(r, W, edge)` -- the barrier maths behind `floor_mode="truncate"`.
- `mae_survival_given_win`, `sample_mae_given_win` -- the parameter-free adverse-excursion law.

`floor_mode="none"` is the model stage one **rejected** (propsim D-04): it breaks the 2/5 ceiling. Do not use it.

## Quick reference

| task | how |
|---|---|
| Import the engine | its own process; `vendor/stage2` and `vendor/stage2/scripts` on `sys.path`; one BLAS thread |
| Check the vendored tree and data | `python scripts/vendor_stage2.py --verify` |
| The identity | `python identity/stage2_identity.py --paths 4` (light); `--paths 500` from a clean checkout (heavy) |
| Reproduce stage one | `run_combine(Policy(rr=1.0, risk=1500.0), 0.0, 200_000, seed=2026)` -> 16/49 |
| Replay a design over start days | `vendor/stage2/scripts/user_journey.py`'s replay, through an adapter in `extended/` |
| Rules | Stage 2's ledger (`rules_from_ledger()`); this repository's `config/rules_extended.yaml` only through an adapter and its row |
| Write a result | `extended.results.write_result` -- never the vendored one with its defaults |
| Engine needs to change | An adapter or subclass in `extended/`. **Never** edit `vendor/` |
