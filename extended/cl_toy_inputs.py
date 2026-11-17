"""RD-03's synthetic inputs (Q-119): the reading's whole pipeline on toy campaigns -- for `scripts/cl_reading.py
--synthetic` and for the cost measurement of section 15 (E-117's form: synthetic campaigns of the window's length,
measured before step 3). Reads no bar and no atlas; its draws come from section 12's toy seed, read from the
declaration (`cl_reading.declared_seed`), never typed.

    from extended import use_vendored_stage2; use_vendored_stage2()
    from extended import cl_toy_inputs as TI
    inputs = TI.ToyInputs(n_days=TI.WINDOW_SESSIONS, n_paths=500)
"""
from __future__ import annotations

from typing import Any, Sequence

import numpy as np
import pandas as pd

from extended import ROOT, use_vendored_stage2

use_vendored_stage2()

from extended import pp_inputs as PI  # noqa: E402

#: the development window's sessions (NQ, 2020-01-02 to 2026-07-16): the length the synthetic campaigns take
WINDOW_START, WINDOW_END = "2020-01-02", "2026-07-16"
WINDOW_SESSIONS = len(pd.bdate_range(WINDOW_START, WINDOW_END))
DESIGNS = ("t14", "t16")


def toy_seed() -> int:
    from extended import cl_reading as CL

    return CL.declared_seed(CL.TOY_ROLE, ROOT, strict=False)


def toy_blocks(n_days: int, seed: int, key: int, win_p: float = 0.6, bad_every: int = 13) -> list:
    """`n_days` synthetic days of one to four trades at $500 risk (2R targets), every `bad_every`-th pair of days lost
    whole (breaches, so the stacking pattern and the losses Back2Funded acts on occur)."""
    from propedge.outcomes.distribution import DayBlock

    rng = np.random.default_rng([int(seed), int(key)])
    out = []
    for i in range(int(n_days)):
        k = 1 + (i % 4)
        et = np.array([500.0 + 60.0 * j for j in range(k)])
        bad = (i % bad_every) in (bad_every - 2, bad_every - 1)
        win = np.array([(not bad) and rng.random() < win_p for _ in range(k)])
        out.append(DayBlock(pnl=np.where(win, 1000.0, -500.0), risked=np.full(k, 500.0),
                            exit_reasons=tuple("target" if w else "stop" for w in win), entry_t=et, exit_t=et + 30.0))
    return out


class ToyInputs(PI.Inputs):
    """Toy designs `t14` and `t16` (no registered file behind them): U1-shaped jobs on both arms, a gate call per
    design, no reference to compare (the identities are the real run's)."""

    def __init__(self, n_days: int = 160, n_paths: int = 3, start: str = WINDOW_START, seed: int | None = None):
        self.n_days, self._n_paths, self.start = int(n_days), int(n_paths), str(start)
        self.seed = toy_seed() if seed is None else int(seed)
        self._jobs: dict[str, Any] = {}

    def n_paths(self) -> int:
        return self._n_paths

    def _rules(self):
        from propedge.contract.adapter import rules_from_ledger

        return rules_from_ledger()

    def protocol(self, design: str):
        from propedge.campaign.protocols import Protocol
        from extended import levers_terms as LT

        return Protocol(name=f"cl_toy_{design}", combine_rr=2.0, combine_risk=500.0, funded_rr=2.0, funded_risk=500.0,
                        trades_per_day=4, max_concurrent_accounts=LT.funded_cap())

    def jobs(self, design: str) -> dict[str, dict[str, Any]]:
        if design in self._jobs:
            return self._jobs[design]
        from propedge.campaign.lockstep import ConductModel
        from propedge.campaign.payout_method import payout_method_terms
        from propedge.contract.rules import load_rules

        from extended import levers_terms as LT
        from extended import user_beside as B

        rules = self._rules()
        cap = LT.funded_cap()
        lag = int(payout_method_terms("aeropay", ledger=load_rules()).lag_days)
        days = [d.date().isoformat() for d in pd.bdate_range(self.start, periods=self.n_days)]
        out = {}
        for j, arm in enumerate(("verdict", "point")):
            blocks = toy_blocks(self.n_days, self.seed, 10 + 2 * DESIGNS.index(design) + j,
                                win_p=0.58 if arm == "verdict" else 0.6)
            args = {"draws": {"protocol": self.protocol(design), "mode": "rotation", "flip": None},
                    "path": dict(edge=0.0, rules=rules, initial_bankroll=1e9, max_concurrent_accounts=cap,
                                 subscription=float(rules.subscription), billing_days=int(rules.billing_days),
                                 activation=float(rules.activation), payout_lag_days=lag, max_concurrent_combines=cap,
                                 max_total_accounts=cap, conduct=ConductModel(rtp=False, enforcement_p=0.0),
                                 combine_max_days=2000, funded_horizon_days=100_000, purchase_budget=(20, 21)),
                    "seed": B.SEED_BLOCK[1]}
            out[arm] = {"engine": "single", "blocks": blocks, "dates": days, "args": args}
        self._jobs[design] = out
        return out

    def identity_problems(self, design: str, arm: str, outs: Sequence[dict]) -> list[str]:
        return []

    def ladder_problems(self, design: str, response: str, outs: Sequence[dict]) -> list[str]:
        return []

    def gate_call(self, design: str, cell: str, twin: bool) -> dict[str, Any]:
        """The toy's gate call: its blocks at 0 %, the placement off, its own seat limits and budget (and, for the
        twin, every trade's outcome at zero edge)."""
        import portfolio_stage as ps

        from extended import levers_terms as LT

        # the twin at zero edge: a 2R target won a third of the time (and no lost spell), so 9.2's oracles apply
        blocks = toy_blocks(self.n_days, self.seed, 20 + DESIGNS.index(design), win_p=1.0 / 3.0 if twin else 0.6,
                            bad_every=10 ** 9 if twin else 13)
        cap = LT.funded_cap()
        sink: list[dict] = []
        hook = ps.composed_hook({}, sink=sink)
        label = f"{design}_ref{'_twin' if twin else ''}"
        ps._label(hook, label)
        kw = dict(blocks=blocks, e=0.0 if twin else 0.2, lb=0.0 if twin else 0.1, protocol=self.protocol(design),
                  bankroll=5000.0, horizon_days=504, n_paths=self._n_paths, seed=self.seed, accounts=cap,
                  sizing=None, rules=self._rules(), combines=cap, total_accounts=cap, purchase_budget=(20, 21),
                  rtp=False, levels=(0.0,), path_hook=hook)
        return {"kw": kw, "sink": sink, "label": label}


__all__ = ["WINDOW_START", "WINDOW_END", "WINDOW_SESSIONS", "DESIGNS", "toy_seed", "toy_blocks", "ToyInputs"]
