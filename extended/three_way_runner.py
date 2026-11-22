"""Wave 3.2: the seed-paired runner -- it fills `x[s, c]`, a per-unit journey value on start day s under coin seed c,
for a design and **each baseline of the set (naive coin, P-14, P-15, P-16) under the same convention**, every trade's
outcome redrawn at its bracket's driftless first-exit odds (CHARTER 3.2; `docs/plans/THREE_WAY_TEST_design.md` 1.1,
1.5, 2.1, 2.3, 2.4; MEASURES.md 1.4, whose `coin_readings` and `design_coin_readings` read the matrices it fills).

    from extended import three_way_runner as R
    plan = R.Plan(seed=S.issue("tests"), part=S.PARTS["tests"], history=0, starts=range(40), seed_indices=range(64),
                  horizon=63, block_sessions=n, budget=B)
    xs, guard = R.paired(design, baselines, rules, plan, R.p_b)          # {name: x[s, c]}; every key checked
    x, x_twin = R.antithetic(design, rules, plan, R.p_b)                 # the twin: every uniform complemented
    x1, x2 = R.disjoint(design, rules, plan, other_seed_indices, R.p_b)  # two disjoint seed sets
    theta = R.exact_centres(design, baseline, rules, plan)               # E[a(f) - a(b) | H] per start, exactly

**The pairing.** Every arm reads the coin field of the same plan: the same role seed, part and history, the same
starts and seed indices. Two arms deciding at the same moment of the same unit read the same uniform (the note's 1.5);
every key is checked for its unit's start as it is built (N-2), and one sampled `KeyGuard` per call stores the keys of
the plan's first start under its first `three_way_keys.SAMPLE_SEEDS` seed indices across every arm, refusing two
different keys with one `generate_state` (the lead's ruling on B-2: distinctness by the packing, the stored check a
tripwire). The baselines must be exactly the four (`BASELINES`); a stress applies to every arm
alike or the call is refused.

**Choice 3.** Each start is its own user: every coin key carries the start (`three_way_keys.Unit`), so under one seed
the units of different starts draw independently (2.1), which the Hoeffding/McDiarmid bound of 2.2 (a) needs.

**What it reads.** Schedules, rules and the plan -- never a bar (the shift-invariance test: a history enters only
through its schedule, and a unit reads only the sessions of its own window). The block bound refuses a start whose
window passes its block's end (CHARTER 3.6 (d)); a plan with dates refuses held-out sessions unless the joint held-out
test's declaration is named and the reader authorises it (`Plan`; m-10).

**The enforcement stream is seeded apart** (`three_way_keys` kind `enforce`): the denial ladder (beside; 0 % in the
verdict) moves no coin draw, which `tests/test_three_way_runner.py` holds key for key. This is what Wave 3.1's
`user_beside.base_problems` refusal waits for; that refusal is not lifted here (see the hand-back: the vendored engine
derives a flip stream's direction and the denial from one path seed, and the file is in two identities' covers).

No engine, no bar, no file; numpy only.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable, Mapping, Sequence

import numpy as np

from extended import three_way_journey as J
from extended import three_way_keys as K
from extended import three_way_redraw as RD
from extended import three_way_seeds as S

BASELINES = ("naive_coin", "p14", "p15", "p16")


#: E-208's held-out years begin here, and the confirmation window (never read) here
HELD_OUT_FIRST = np.datetime64("2024-01-02")
CONFIRMATION_FIRST = np.datetime64("2026-07-17")


class HeldOutRefused(ValueError):
    """A unit's window reads a held-out session with no joint held-out test's declaration named, or a session of the
    confirmation window."""


@dataclass(frozen=True)
class Plan:
    """The units read: the coin role seed, the part and history indices, the starts and the seed indices, the horizon,
    the block's session count (the window bound), P_B's budget, and -- for a history of real sessions -- each
    session's date and the declaration of the joint held-out test that authorises any held-out session (m-10).

    **The held-out refusal** (the red team's m-10; CHARTER 3.6 (e)): a plan with dates refuses, before any draw, a
    unit whose window holds a session dated 2024-01-02 or later unless `held_out_declaration` names the joint held-out
    test's pinned declaration -- which `extended.reader.authorise` must accept for its held-out purpose -- and refuses
    any session dated 2026-07-17 or later always. A plan without dates is a synthetic history (S1), which has no
    calendar."""

    seed: int
    part: int
    history: int
    starts: tuple[int, ...]
    seed_indices: tuple[int, ...]
    horizon: int
    block_sessions: int
    budget: float | None = None
    dates: tuple | None = None
    held_out_declaration: str | None = None

    def __post_init__(self) -> None:
        if int(self.part) not in S.PARTS.values():          # the red team's 805978a finding 2
            raise S.ProvenanceRefused(f"REFUSED (m-9): a plan's part is a declared part (three_way_seeds.PARTS), "
                                      f"not {self.part}")
        if getattr(self.seed, "role", None) == "tests" and int(self.part) != S.PARTS["tests"]:
            raise S.ProvenanceRefused("REFUSED (m-9): the tests' seed plans only in the tests' part")
        object.__setattr__(self, "starts", tuple(int(s) for s in self.starts))
        object.__setattr__(self, "seed_indices", tuple(int(c) for c in self.seed_indices))
        if len(set(self.starts)) != len(self.starts) or len(set(self.seed_indices)) != len(self.seed_indices):
            raise ValueError("a start or a seed index listed twice")
        for s in self.starts:
            J.check_window(s, self.horizon, self.block_sessions)
        if self.dates is not None:
            self._check_dates()

    def _check_dates(self) -> None:
        d = np.asarray(self.dates, dtype="datetime64[D]")
        if d.size != self.block_sessions or (d.size > 1 and not (np.diff(d) > np.timedelta64(0, "D")).all()):
            raise ValueError("one increasing date a session of the block")
        if (d >= CONFIRMATION_FIRST).any():
            raise HeldOutRefused("REFUSED (CHARTER 3.6): a session of the confirmation window, never read")
        windows = [d[s:s + self.horizon] for s in self.starts]
        held = [w for w in windows if (w >= HELD_OUT_FIRST).any()]
        if not held:
            return
        if self.held_out_declaration is None:
            raise HeldOutRefused("REFUSED (m-10; CHARTER 3.6 (e)): a unit's window reads held-out sessions and no "
                                 "joint held-out test's declaration is named")
        from extended import reader                                     # the one door's authorisation, no bar read

        first = min(w[w >= HELD_OUT_FIRST][0] for w in held)
        last = max(w[-1] for w in held)
        reader.authorise(str(first), str(last), purpose=reader.HELDOUT_TEST, declaration=self.held_out_declaration,
                         what="the three-way runner's held-out units")


#: a per-unit value: one start's records -> one value per seed
ValueFn = Callable[[J.Records], np.ndarray]


def p_b(rec: J.Records) -> np.ndarray:
    """The fallback's per-unit value: P_B's months ahead under the plan's budget over 3 (MEASURES.md section 2)."""
    return J.p_b_values(rec, rec.budget)


def run(schedule: J.Schedule, rules: J.ToyRules, plan: Plan, arm: J.ArmSpec = J.ArmSpec(),
        guard: K.KeyGuard | None = None) -> list[J.Records]:
    """Every start of the plan under every seed index: one `Records` a start."""
    return [J.simulate(schedule, rules, s, plan.seed_indices, plan.horizon, seed=plan.seed, part=plan.part,
                       history=plan.history, block_sessions=plan.block_sessions, arm=arm, budget=plan.budget,
                       guard=guard) for s in plan.starts]


def fill_failures(records: Sequence[J.Records]) -> dict[str, float]:
    """The failures at the fill, reported beside every reading (n-3; the draft's row of a lane that cannot take its
    trade): their mean a unit, the share of units with at least one, and the total."""
    f = np.concatenate([np.asarray(r.fill_failures, float) for r in records])
    return {"fill_failures_per_unit": float(f.mean()) if f.size else 0.0,
            "share_of_units_with_one": float((f > 0).mean()) if f.size else 0.0, "fill_failures": float(f.sum())}


def matrix(records: Sequence[J.Records], value: ValueFn) -> np.ndarray:
    """x[s, c]: one row a start (in the plan's order), one column a seed."""
    x = np.vstack([np.asarray(value(r), float) for r in records])
    if not np.isfinite(x).all():
        raise ValueError("a blank unit: every unit has a value under every seed")
    return x


def paired(design: J.Schedule, baselines: Mapping[str, J.Schedule], rules: J.ToyRules, plan: Plan, value: ValueFn,
           *, design_arm: J.ArmSpec = J.ArmSpec(), base_arm: J.ArmSpec = J.ArmSpec(),
           guard: K.KeyGuard | None = None, beside: dict | None = None) -> tuple[dict[str, np.ndarray], K.KeyGuard]:
    """x[s, c] for the design and each baseline on the same units and keys. Refused: a baseline set other than the
    four, a design named as a baseline, and arms whose convention differs (twin, reading, worse fill, missed share or
    denial) -- only P3's plant, a design-arm device of the power check, may differ."""
    if set(baselines) != set(BASELINES):
        raise ValueError(f"REFUSED (CHARTER 3.8 (b)): the baselines are exactly {BASELINES}, got {sorted(baselines)}")
    if design.name in BASELINES:
        raise ValueError("the design is not one of the baselines")
    if replace(design_arm, plant_eps=0.0) != base_arm:
        raise ValueError("REFUSED (3.8 (b)): every baseline runs under the design's convention (same reading, twin, "
                         "stress and denial)")
    if base_arm.plant_eps:
        raise ValueError("a plant is the design's arm only")
    guard = guard if guard is not None else K.KeyGuard.sampled(plan.starts, plan.seed_indices)
    out = _arms(((design.name, design, design_arm),), rules, plan, value, guard, beside)
    out.update(_arms(((b, baselines[b], base_arm) for b in BASELINES), rules, plan, value, guard, beside))
    return out, guard


def _arms(arms, rules: J.ToyRules, plan: Plan, value: ValueFn, guard: K.KeyGuard, beside: dict | None
          ) -> dict[str, np.ndarray]:
    out = {}
    for name, sch, arm in arms:
        recs = run(sch, rules, plan, arm, guard)
        out[name] = matrix(recs, value)
        if beside is not None:                              # n-3: the failures at the fill, beside each arm's matrix
            beside[name] = fill_failures(recs)
    return out


def baselines_only(baselines: Mapping[str, J.Schedule], rules: J.ToyRules, plan: Plan, value: ValueFn, *,
                   base_arm: J.ArmSpec = J.ArmSpec(), guard: K.KeyGuard | None = None, beside: dict | None = None
                   ) -> tuple[dict[str, np.ndarray], K.KeyGuard]:
    """The four baselines alone (H4's re-baseline, wt/wt-h4 f897cd7): `paired`'s pairing, seeds and refusals with no
    design arm -- exactly the four, one plan's keys for all, no plant on a baseline. Each baseline's matrix equals the
    one a call with a design gives it, key for key (`tests/test_three_way_runner.py`)."""
    if set(baselines) != set(BASELINES):
        raise ValueError(f"REFUSED (CHARTER 3.8 (b)): the baselines are exactly {BASELINES}, got {sorted(baselines)}")
    if base_arm.plant_eps:
        raise ValueError("a plant is the design's arm only")
    guard = guard if guard is not None else K.KeyGuard.sampled(plan.starts, plan.seed_indices)
    return _arms(((b, baselines[b], base_arm) for b in BASELINES), rules, plan, value, guard, beside), guard


def antithetic(schedule: J.Schedule, rules: J.ToyRules, plan: Plan, value: ValueFn, arm: J.ArmSpec = J.ArmSpec()
               ) -> tuple[np.ndarray, np.ndarray]:
    """The same design on U and on its complement 1 - U (2.3 (a)): x and x_twin on the same units."""
    if arm.twin:
        raise ValueError("the arm given is the base; the twin is made here")
    g = K.KeyGuard.sampled(plan.starts, plan.seed_indices)
    x = matrix(run(schedule, rules, plan, arm, g), value)
    xt = matrix(run(schedule, rules, plan, replace(arm, twin=True), g), value)
    return x, xt


def disjoint(schedule: J.Schedule, rules: J.ToyRules, plan: Plan, other_seed_indices: Sequence[int], value: ValueFn,
             arm: J.ArmSpec = J.ArmSpec()) -> tuple[np.ndarray, np.ndarray]:
    """The same design on two disjoint seed sets (2.3 (b)); refused when the sets share a seed index or a key state."""
    other = replace(plan, seed_indices=tuple(other_seed_indices))
    if set(other.seed_indices) & set(plan.seed_indices):
        raise ValueError("REFUSED (2.3 (b)): the seed sets share a seed index")
    g1 = K.KeyGuard.sampled(plan.starts, plan.seed_indices)
    g2 = K.KeyGuard.sampled(other.starts, other.seed_indices)
    x1 = matrix(run(schedule, rules, plan, arm, g1), value)
    x2 = matrix(run(schedule, rules, other, arm, g2), value)
    K.disjoint(g1, g2)
    return x1, x2


def exact_centres(f: J.Schedule, b: J.Schedule, rules: J.ToyRules, plan: Plan, arm: J.ArmSpec = J.ArmSpec()
                  ) -> np.ndarray:
    """E[a(f, u) - a(b, u) | H] for each start of the plan, exactly (P_B's per-unit value by the dynamic program of
    2.4): the centre of the asymmetric null."""
    return np.array([J.expect(f, rules, s, plan.horizon, block_sessions=plan.block_sessions, arm=arm,
                              budget=plan.budget)["p_b"]
                     - J.expect(b, rules, s, plan.horizon, block_sessions=plan.block_sessions, arm=arm,
                                budget=plan.budget)["p_b"] for s in plan.starts])


#: CHARTER 3.8 (c)'s supply stress (measure 28; the red team's m-7): a tenth of the signals missed
MISSED_SHARE = 0.10


def stress_arms() -> dict[str, J.ArmSpec]:
    """The declared stress arms, each run on the design and every baseline alike: measure 29's +1 and +2 ticks
    (`three_way_redraw.WORSE_FILL_TICKS`), and measure 28's missed signals at `MISSED_SHARE`."""
    arms = {f"worse_{int(k)}": J.ArmSpec(worse_ticks=int(k)) for k in RD.WORSE_FILL_TICKS}
    arms[f"missed_{MISSED_SHARE:g}"] = J.ArmSpec(missed_q=MISSED_SHARE)
    return arms


def stress_cells(n_arms: int = 1 + len(BASELINES)) -> int:
    """The stress arms counted: every compared arm at every declared stress."""
    return int(n_arms) * len(stress_arms())


def stress(design: J.Schedule, baselines: Mapping[str, J.Schedule], rules: J.ToyRules, plan: Plan, value: ValueFn
           ) -> dict[str, dict[str, np.ndarray]]:
    """The design and every baseline under each declared stress arm (`stress_arms`), paired on the same units."""
    return {name: paired(design, baselines, rules, plan, value, design_arm=arm, base_arm=arm)[0]
            for name, arm in stress_arms().items()}


def seed_sets(n_seeds: int, m: int) -> list[np.ndarray]:
    """Disjoint seed sets of m consecutive seed columns (the replicates of 2.2 (b)); a remainder is not used."""
    if m < 1 or n_seeds < m:
        raise ValueError("a seed set holds at least one seed and the seeds fill one set")
    return [np.arange(j * m, (j + 1) * m) for j in range(n_seeds // m)]


__all__ = ["BASELINES", "HELD_OUT_FIRST", "CONFIRMATION_FIRST", "HeldOutRefused", "Plan", "ValueFn", "p_b", "run",
           "fill_failures", "matrix", "paired", "baselines_only", "antithetic", "disjoint", "exact_centres",
           "MISSED_SHARE", "stress_arms",
           "stress_cells", "stress", "seed_sets"]
