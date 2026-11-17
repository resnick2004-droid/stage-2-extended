"""F-03's synthetic fixture for the runners' end-to-end tests (imported by `tests/fo_run1_synthetic.py`,
`tests/fo_run2_synthetic.py` and `tests/fo_t3_synthetic.py`, each run in a process of its own with the vendored tree on
the path). Synthetic only: `extended/synthetic_bars.py`'s bars, never the licensed data or anything derived from it.

**The calendar.** A "choice block" of 2020-06-01 .. 2020-12-31 and the first quarter of 2021, 2022 and 2023 (each year of
stage A's span), and a "judged block" of the first half of 2024 -- the runners' blocks by date, so every split by
2023-12-29 / 2024-01-02 is the real one's; fast bars (`vol_scale` 10) so overnight 3R brackets resolve. Report days
(`b`) are the first Friday of each month, one FOMC day (`f`) a block. Every mark 17:00 .. 09:00 is admitted.

**The context** (`SynCtx`, the runner's `Ctx` with its reads replaced): the day tables, spans and grids from the
fixture; P-16's configuration, plan and money side from the vendored tree, but no registered outcome -- the per-R
shift a synthetic constant, the capacity a constant, `mean_dv` a constant, a*'s (b) zero, no P-14 rows; every judged
"read" recorded in order (`authorised`) and nothing ledgered. `judged_seed` makes the judged block's bars another
synthetic walk (T-3).
"""
from __future__ import annotations

from datetime import date
from typing import Any

import numpy as np
import pandas as pd

from extended import features as F
from extended import opening_population as OP
from extended import synthetic_bars as sb
from extended import walker as W

ADMITTED = list(range(0, F.slot(9, 0) + 1, 5))
FIXTURE_SEED = (20261988, 700)          # section 16's test block


def _kinds(days, fomc: str) -> dict[str, str]:
    k = {d.isoformat(): ("b" if (d.weekday() == 4 and d.day <= 7) else "n") for d in days}
    k[fomc] = "f"
    return k


def choice_bars() -> pd.DataFrame:
    spec = sb.Spec(date(2020, 6, 1), date(2023, 3, 31), seed=[*FIXTURE_SEED, 0], rolls=((date(2021, 1, 15), "NQM1"),),
                   first_contract="NQH1", holidays=frozenset(), early_closes=frozenset(), vol_scale=10.0)
    b = sb.generate(spec)
    d = pd.to_datetime(b["day"])
    keep = (d.dt.year == 2020) | ((d.dt.year >= 2021) & (d.dt.month <= 3) & (d.dt.year <= 2023))
    return b[keep].reset_index(drop=True)


def judged_bars(seed: int = 1) -> pd.DataFrame:
    spec = sb.Spec(date(2024, 1, 2), date(2024, 6, 28), seed=[*FIXTURE_SEED, int(seed)], rolls=((date(2024, 3, 15),
                   "NQM4"),), first_contract="NQH4", holidays=frozenset(), early_closes=frozenset(), vol_scale=10.0,
                   base_price=16000.0)
    return sb.generate(spec)


class Fixture:
    def __init__(self, judged_seed: int = 1):
        self.cb = choice_bars()
        self.jb = judged_bars(judged_seed)
        self.gc, self.gj = F.grid(self.cb), F.grid(self.jb)
        self.cdays = [d.isoformat() for d in self.gc.days]
        self.jdays = [d.isoformat() for d in self.gj.days]
        kc, kj = _kinds(self.gc.days, "2021-01-27"), _kinds(self.gj.days, "2024-03-20")
        self.A1c = pd.DataFrame({"date": self.cdays, "day_kind": [kc[d] for d in self.cdays]})
        self.A1j = pd.DataFrame({"date": self.jdays, "day_kind": [kj[d] for d in self.jdays]})
        self.arr = {}
        for g in (self.gc, self.gj):
            for i, d in enumerate(g.days):
                self.arr[d.isoformat()] = tuple(np.r_[np.nan, X[i][:1330]] for X in (g.O, g.H, g.L, g.C))

    @property
    def judged_sessions(self) -> list[str]:
        return list(self.jdays)


def syn_ctx_class(FO):
    """`SynCtx` over the runner module `FO` (imported by the caller from `scripts/fo_opening.py`)."""

    class SynCtx(FO.Ctx):
        fx: Fixture = None

        def a1_days(self, start, end):
            return self.fx.A1c.copy()

        def span(self, start, end, all_dates):
            return OP.build_span(self.fx.cdays[0], self.fx.cdays[-1], all_dates,
                                 arrays_for=lambda chunk: (lambda d: self.fx.arr[d]), days_table=self.fx.A1c,
                                 admitted=ADMITTED, log=lambda m: None)

        def grid(self, start, end, walked):
            b = self.fx.cb
            return F.grid(b[b["day"].astype(str).isin(walked)].reset_index(drop=True))

        def p16(self) -> dict[str, Any]:
            import a3_brk30_cb20 as Cb
            import atlas_a3 as A
            import zero_edge_decomposition as zd

            from propedge import RESULTS_DIR

            cfg = A.config(A.FAMILY)
            fcfg = A.fv3_config(cfg)
            plan = Cb.noclose_plan(RESULTS_DIR)
            keys = sorted(set(float(x) for x in A.rrs(cfg)) | set(zd.policy_rrs(plan)))
            return {"cfg": cfg, "fcfg": fcfg, "tv": float(A.TICK_VALUE), "plan": plan,
                    "e_by": {k: 0.02 for k in keys}, "lb_by": {k: -0.02 for k in keys}, "cap": 200, "keys": keys}

        def restricted_replay_problems(self, job, starts, workers):
            return []

        def mean_dv(self):
            return 1000.0

        # ---- run 2's judged "reads": recorded, nothing ledgered
        def authorise(self, purpose):
            self.authorised.append(purpose)

        def judged_days(self):
            assert self.authorised and self.authorised[-1] == "stage_C_states"
            return self.fx.A1j.copy()

        def states_grid(self, walked_choice, walked_judged):
            assert self.authorised[-1] == "stage_C_states"
            b = pd.concat([self.fx.cb, self.fx.jb], ignore_index=True)
            keep = set(walked_choice) | set(walked_judged)
            return F.grid(b[b["day"].astype(str).isin(keep)].reset_index(drop=True))

        def admitted(self):
            return list(ADMITTED)

        def judged_span(self, all_dates):
            assert self.authorised[-1] == "stage_C_judgement"
            return OP.build_span(self.fx.jdays[0], self.fx.jdays[-1], all_dates,
                                 arrays_for=lambda chunk: (lambda d: self.fx.arr[d]), days_table=self.fx.A1j,
                                 admitted=ADMITTED, log=lambda m: None, extra_rules={"be_both": W.STAGE2_BE_BOTH})

        def gate(self, trades, days, P, **kw):
            assert self.authorised[-1] == "stage_C_campaign"
            return FO.gate_campaign(trades, days, P, **kw)

        def follow_lifts(self):
            return 0.0, []

        def p14_ahead(self, arm):
            return None

        def p14_ahead_choice(self, arm, dates):
            return None

    return SynCtx
