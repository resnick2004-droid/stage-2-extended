"""RD-02's run on a synthetic campaign (Q-105b): the inputs `extended.pp_run.run_reading` takes, made from generated day
blocks and a win-day-keyed table, so the whole pipeline -- the order, every check, every section, the result files --
runs end to end with no bar, no atlas and no result file read. `scripts/pp_reading.py --synthetic` uses it, and
`tests/test_pp_run.py` runs that.

The toy draws from section 11's build seed, taken from its one home in code (`identity/gate_identity.py`'s
`SYN_SEED`), never written here. The references are the vendored engine itself: 8.1 item 2's repeat and item 6 compare
the reference class's outputs with the same replay at no class (equal apart from naming), as Q-76's pass-through
identity does. `plant` makes one check fail, to show that a failure writes nothing.
"""
from __future__ import annotations

import dataclasses
from typing import Any

import numpy as np
import pandas as pd

from extended import use_vendored_stage2

use_vendored_stage2()

from extended import payout_policy as PP  # noqa: E402
from extended import pp_run as RUN  # noqa: E402

N_DAYS = 300
FIRST_DAY = "2023-03-01"
RISK = 300.0
CLASS_KEY = "funded_account_cls"
#: the verdict arm's shift on the toy (every R's outcomes moved by this many R, as the gate's bound arm moves them)
VERDICT_SHIFT = -0.05


def _seed() -> int:
    import gate_identity as GI

    return int(GI.SYN_SEED)


def toy_table() -> Any:
    from propedge.campaign.risk_policy import Leaf, Phase, RiskPolicy, Tiers

    lf = lambda name, risk, mt=None: Leaf(name, risk, None, mt)  # noqa: E731
    funded = Tiers(on="balance", tiers=(
        (-1e9, Tiers(on="win_days", tiers=((0.0, lf("funded low, 0-4", RISK)), (5.0, lf("funded low, 0-4", RISK))))),
        (500.0, Tiers(on="win_days", tiers=((0.0, lf("funded mid, 0-4", RISK)), (5.0, lf("funded mid, 5", RISK, 0))))),
        (1000.0, Tiers(on="win_days", tiers=((0.0, lf("funded high, 0-4", RISK)),
                                             (5.0, lf("funded high, 5", RISK * 2 / 3))))),
    ))
    paid = Tiers(on="win_days", tiers=((0.0, lf("paid, 0-4", RISK)), (5.0, lf("paid, 5", RISK))))
    return RiskPolicy(id="pp_run_toy_table", root=Phase(combine=lf("combine", RISK), funded=funded, paid=paid))


def toy_blocks(n: int = N_DAYS) -> list:
    from propedge.campaign.flip import slot_from_ct
    from propedge.outcomes.distribution import DayBlock

    g = np.random.default_rng([_seed(), 40])
    t0 = float(slot_from_ct("09:10"))
    out = []
    for _ in range(n):
        k = int(g.integers(1, 4))
        win = g.random(k) < 0.45
        et = t0 + 100.0 * np.arange(k, dtype=float)      # the third trade spans 13:00 CT (the minutes count)
        out.append(DayBlock(pnl=np.where(win, 2.0 * RISK, -RISK).astype(float), risked=np.full(k, RISK),
                            exit_reasons=tuple("target" if w else "stop" for w in win), entry_t=et, exit_t=et + 60.0))
    return out


class SyntheticInputs(RUN.Inputs):
    def __init__(self, *, starts: list[int] | None = None, n_paths: int = 4, plant: str | None = None):
        self._starts = starts
        self._n_paths = int(n_paths)
        self.plant = plant
        self._jobs: dict[str, Any] = {}

    def n_paths(self) -> int:
        return self._n_paths

    def jobs(self, design: str) -> dict[str, dict[str, Any]]:
        from extended import user_beside as B
        from propedge.campaign.gate import shifted_blocks
        from propedge.campaign.lockstep import ConductModel
        from propedge.campaign.protocols import Protocol
        from propedge.contract.adapter import rules_from_ledger

        rules = rules_from_ledger()
        blocks = toy_blocks()
        dates = [d.date().isoformat() for d in pd.bdate_range(FIRST_DAY, periods=len(blocks))]
        proto = Protocol(name="pp_run_toy", combine_rr=2.0, combine_risk=RISK, funded_rr=2.0, funded_risk=RISK,
                         trades_per_day=3, max_concurrent_accounts=5)
        path = dict(edge=0.0, rules=rules, initial_bankroll=1e9, max_concurrent_accounts=5,
                    subscription=float(rules.subscription), billing_days=int(rules.billing_days),
                    activation=float(rules.activation), payout_lag_days=3, max_concurrent_combines=5,
                    max_total_accounts=5, conduct=ConductModel(rtp=False, enforcement_p=0.0), combine_max_days=2000,
                    funded_horizon_days=100_000, risk_policy=toy_table(), purchase_budget=(20, 21))
        out = {}
        for arm, blk in (("verdict", shifted_blocks(blocks, VERDICT_SHIFT)), ("point", blocks)):
            out[arm] = {"engine": "single", "blocks": blk, "dates": dates,
                        "args": {"draws": {"protocol": proto, "mode": "rotation", "flip": None}, "path": dict(path),
                                 "seed": B.SEED_BLOCK[1]}}
        self._jobs[design] = out
        return out

    def _plain(self, design: str, arm: str, response: str, outs: list[dict[str, Any]]) -> list[str]:
        """The same replay at no class: the reference class must equal it apart from its naming key."""
        import gate_identity as GI

        from extended import user_beside as B

        starts = [int(x["rec"]["start_day"]) for x in outs]
        plain = B.run_starts(design, arm, B.BY_NAME[response], self._jobs[design][arm], starts, 1)
        mine = [{k: v for k, v in x.items() if k != CLASS_KEY} for x in outs]
        d = GI.deep_difference(plain, mine, "outputs")
        return [] if d is None else [f"the reference class differs from the engine at no class: {d}"]

    def identity_problems(self, design: str, arm: str, outs: list[dict[str, Any]]) -> list[str]:
        if self.plant == "identity":
            return ["a planted failure (the synthetic run's refusal test)"]
        return self._plain(design, arm, "off", outs)

    def ladder_problems(self, design: str, response: str, outs: list[dict[str, Any]]) -> list[str]:
        if self.plant == "ladder":
            return ["a planted failure (the synthetic run's refusal test)"]
        return self._plain(design, "verdict", response, outs)

    def gate_call(self, design: str, cell: str, twin: bool) -> dict[str, Any]:
        import gate_identity as GI

        from propedge.campaign.gate import shifted_blocks

        kw = dict(GI.syn_kwargs(), n_paths=self._n_paths, risk_policy=toy_table(), levels=(0.0,))
        blocks = GI.syn_blocks()
        if twin:
            blocks = shifted_blocks(blocks, -float(kw["e"]))
            kw.update(e=0.0, lb=0.0)
        kw["protocol"] = PP.cell_protocol(kw["protocol"], cell)
        kw["blocks"] = blocks
        return {"kw": kw, "sink": [], "label": f"{design}_{cell}{'_twin' if twin else ''}"}


__all__ = ["SyntheticInputs", "toy_blocks", "toy_table", "N_DAYS", "FIRST_DAY"]
