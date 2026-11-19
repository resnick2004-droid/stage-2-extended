"""H3-A's inputs, every one fixed here before the run (the lead's ruling on the red team's B-3: nothing chosen or written
at run time). `prereg/DRAFT_H3_three_way.md` Appendix C prints this module (through
`docs/plans/scripts/three_way/h3a_inputs.py`) and `tests/test_h3_draft.py` holds the two equal, so the declaration's
text and the values the run reads are one. **No value here is a firm's**: the toy rules and the S1 parameters are
stylised, chosen without any outcome read, for design checks only (CHARTER 3.7: H3-A chooses no rule).

What is fixed, per part:
- **every part:** the toy rules (`TOY_RULES`; A2's `TOY_RULES_EXACT`), S1's parameters (`S1_PARAMS`; A2's
  `S1_PARAMS_EXACT`), the starts (`STARTS`, of each history), the horizon (`HORIZON`), the seed indices (`SEEDS`), and the
  placeholder budget of `P_B` (`BUDGET`);
- **A1** (the same-design nulls): the design (`A1_DESIGN`), the baselines (`BASELINES`), the disjoint null's two seed
  sets (`DISJOINT`), the size tests' seed sets of `J_PRIME` seeds, the feasible levels (`LEVELS`), both placeholder
  composites (`P_B` alone, and `TOY_COMPOSITE`);
- **A2** (the exact-centred toy null): the pair (`A2_PAIR`);
- **A3** (the history null on S1): the stream pair (`A3_PAIR`, D on stream A and D' the same on B) and the shortcut's
  subset (`SHORTCUT_HISTORIES`, run in full at the test's J);
- **A4** (the plants): P2's lever changes (`P2_LEVERS`), P3's grid of epsilon (`P3_EPS`), P4's grid of a and its
  switching rate (`P4_A`, `P4_SWITCH`), and the grid of sizes for the conjoint MDL (`SIZE_GRID`);
- **the kill rule's centring test** (`CENTRING_Z`): a null pool is not centred when |its mean| exceeds `CENTRING_Z`
  standard errors (two-sided);
- **the smaller-J rule's report in H3-A** (`SMALLER_J_MODEL`): both bounds' J on `three_way_stats.SMALLER_J_GRID` with
  `SMALLER_J_DRAWS` draws, the normal model at each pool's own sd (H3-D's model is the bootstrap of H4's replicates).
"""
from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass

from extended import three_way_journey as J
from extended import three_way_s1 as S1
from extended import three_way_stats as ST

#: the toy account (stylised; no firm's)
TOY_RULES = J.ToyRules(combine_fee=40.0, billing=21, target=2500.0, mll=1500.0, dll=800.0, activation_fee=100.0,
                       funded_mll=1500.0, win_day=100.0, payout_days=5, payout_share=0.5, payout_cap=3000.0, split=0.9,
                       payout_lag=3, combine_lock=0.0)
#: A2's account for the exact program: whole dollars, no daily limit, so its states stay few
TOY_RULES_EXACT = J.ToyRules(combine_fee=40.0, billing=21, target=600.0, mll=400.0, dll=None, activation_fee=100.0,
                             funded_mll=400.0, win_day=100.0, payout_days=3, payout_share=0.5, payout_cap=1000.0,
                             split=1.0, payout_lag=2, combine_lock=0.0)
#: S1's generator (the starts and horizon need STARTS[-1] + HORIZON sessions)
S1_PARAMS = S1.S1Params(n_sessions=200, vol_mean=6.0, phi=0.9, vol_sd=0.15, regime_amp=0.2, regime_switch=0.02,
                        rate=1.5, rate_beta=1.0, hold_mean=30.0, hold_stop=40.0, time_limit=90.0)
S1_PARAMS_EXACT = S1.S1Params(n_sessions=200, vol_mean=6.0, phi=0.9, vol_sd=0.15, regime_amp=0.0, regime_switch=0.02,
                              rate=0.3, rate_beta=1.0, hold_mean=30.0, hold_stop=40.0, time_limit=90.0)
STARTS = tuple(range(120))
HORIZON = 63
SEEDS = 10_000
BUDGET = 1000.0

#: costs a contract (stylised): a side's commission, the stop one tick and the flatten two ticks of slippage at $5
COST, STOP_SLIP, FLAT_SLIP, TICK = 2.12, 5.0, 10.0, 5.0
A1_DESIGN = S1.DesignSpec("a1_design", stream="A", k_stop=6.0, stop_lo=8, stop_hi=120, rr=1.0, contracts=1,
                          tick_value=TICK, entry_cost=COST, x_target=COST, x_stop=7.12, x_flat=12.12, walk_step=2,
                          latency=5, per_session=3)
#: the baselines' toys on S1, under the design's cost convention (every side the commission, the stop one tick and the
#: flatten two ticks of slippage)
BASELINES = S1.toy_baselines(tick_value=TICK, cost=COST, stop_slip=STOP_SLIP, flat_slip=FLAT_SLIP)
#: the disjoint null's two seed sets (by seed index), and the size tests' seed sets
DISJOINT = ((0, SEEDS // 2), (SEEDS // 2, SEEDS))
J_PRIME = 100
LEVELS = (0.05, 0.01, 0.001)
#: the clipped toy composite (every dimension an unconditional mean with an arithmetic bound, clipped by definition)
TOY_COMPOSITE = (
    ST.Dimension("P_B", "mean", 63, a=0.0, r=1.0, source="arithmetic", lo=0.0, hi=1.0, weight=0.5),
    ST.Dimension("paid_by_63", "mean", 63, a=0.0, r=1.0, source="arithmetic", lo=0.0, hi=0.6, weight=0.3),
    ST.session_count("sessions_saved_to_payout", 63, 63, lo=0.0, hi=64.0, weight=0.2),
)
#: A2: two designs that differ in bracket and size, barrier trades only (R-10 walks excluded: per_session 1, a short
#: hold), so the exact program centres them
A2_PAIR = (S1.DesignSpec("a2_x1", stream="A", fixed_stop=20, rr=1.0, tick_value=TICK, per_session=1),
           S1.DesignSpec("a2_x2", stream="A", fixed_stop=40, rr=0.5, tick_value=TICK, per_session=1))
A3_PAIR = S1.stream_pair(S1.DesignSpec("a3_D", stream="A", fixed_stop=10, rr=1.0, tick_value=TICK, per_session=1))
A3_HISTORIES = 200
SHORTCUT_HISTORIES = tuple(range(5))
#: A4: P2's lever changes (on TOY_RULES), P3's edge plant, P4's regime-varying plant, the sizes' grid
P2_LEVERS = {"fee_less_a_fifth": {"combine_fee": 32.0}, "payout_lag_one": {"payout_lag": 1},
             "activation_halved": {"activation_fee": 50.0}}
P3_EPS = (0.0025, 0.005, 0.01, 0.02)
P4_A = (0.0, 0.5, 1.0)
P4_SWITCH = 0.02
SIZE_GRID = (0.0025, 0.005, 0.01, 0.02, 0.04)
CENTRING_Z = 4.0
SMALLER_J_MODEL = "normal at each pool's own sd (H3-A); H3-D: three_way_stats.bootstrap_draw of H4's replicates"


def _show(v) -> str:
    if is_dataclass(v):
        return f"{type(v).__name__}(" + ", ".join(f"{f.name}={_show(getattr(v, f.name))}" for f in fields(v)
                                                if f.name != "stat") + ")"
    if isinstance(v, dict):
        return "{" + ", ".join(f"{k}: {_show(x)}" for k, x in v.items()) + "}"
    if isinstance(v, tuple):
        return "(" + ", ".join(_show(x) for x in v) + ")"
    return repr(v)


def declared() -> list[tuple[str, str]]:
    """Every declared input as (name, its value written out)."""
    out = []
    for name in ("TOY_RULES", "TOY_RULES_EXACT", "S1_PARAMS", "S1_PARAMS_EXACT", "STARTS", "HORIZON", "SEEDS",
                 "BUDGET", "COST", "STOP_SLIP", "FLAT_SLIP", "TICK", "A1_DESIGN", "BASELINES", "DISJOINT", "J_PRIME",
                 "LEVELS", "TOY_COMPOSITE", "A2_PAIR", "A3_PAIR", "A3_HISTORIES", "SHORTCUT_HISTORIES", "P2_LEVERS",
                 "P3_EPS", "P4_A", "P4_SWITCH", "SIZE_GRID", "CENTRING_Z", "SMALLER_J_MODEL"):
        v = globals()[name]
        if name == "STARTS":
            out.append((name, f"range({STARTS[0]}, {STARTS[-1] + 1})"))
        else:
            out.append((name, _show(v)))
    out.append(("SMALLER_J_GRID", _show(ST.SMALLER_J_GRID)))
    out.append(("SMALLER_J_DRAWS", _show(ST.SMALLER_J_DRAWS)))
    return out


__all__ = ["TOY_RULES", "TOY_RULES_EXACT", "S1_PARAMS", "S1_PARAMS_EXACT", "STARTS", "HORIZON", "SEEDS", "BUDGET",
           "A1_DESIGN", "BASELINES", "DISJOINT", "J_PRIME", "LEVELS", "TOY_COMPOSITE", "A2_PAIR", "A3_PAIR",
           "A3_HISTORIES", "SHORTCUT_HISTORIES", "P2_LEVERS", "P3_EPS", "P4_A", "P4_SWITCH", "SIZE_GRID",
           "CENTRING_Z", "SMALLER_J_MODEL", "declared", "asdict"]
