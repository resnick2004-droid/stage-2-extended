"""Wave 3.2: a mutation of each core piece of the three-way runner is killed by its check -- the record that the checks
have teeth (fast; no engine, no bar).

Each mutant is the module's own source with one textual change (`_mutant`: the change must match exactly once),
compiled apart; its pieces are patched over the real module's for the one check, which must then fail. The unmutated
check passes in its own test file.

| mutant | the piece | the check that kills it |
|---|---|---|
| M1 | the race's barrier at the full cushion, min(l, c) | the race's exact oracles (a loss passes the floor) |
| M2 | the race's barrier at the target side's cost | the race's exact oracles (unequal exit costs, M-4) |
| M3 | the race's lattice rounded outward | the race's exact oracles |
| M4 | R-10's walk barrier rounded outward | the walk's exact oracles |
| M5 | the journey's barrier at the target side's cost | the journey's floor invariant, near the floor with a daily loss limit |
| M6 | the twin reading u, not 1 - u | the exact-complement test |
| M7 | the coin key without its start (choice 3) | the key-collision test (the guard refuses) |
| M8 | the denial ladder drawn from the coin's race stream | the enforcement-apart test |
| M9 | McDiarmid's c_u without its factor 2 | the fallback-is-Hoeffding test |
| M10 | a source-(ii) clip not applied | the clips-bind test |
| M11 | overlapping positions admitted | the overlap refusal |
| M12 | the exact program's race probabilities swapped | the brute-force enumeration |
| M13 | the empirical-Bernstein bound at ln(1/alpha) | the note's script's bound |
| M14 | the held-out refusal of the resample removed | the search-years-only test |
| M15 | Hoeffding's width dropped | the null-at-the-stated-size check |
| M16 | the block bound removed | the window refusal |
| M17 | vacuity at more than one half (not at least) | the time legs' labels |
| M18 | the key guard comparing integers, not `generate_state` | the trap test |
"""
from __future__ import annotations

import importlib
import types

import numpy as np
import pytest

from extended import three_way_journey as J
from extended import three_way_keys as K
from extended import three_way_redraw as RD
from extended import three_way_stats as ST


def _mutant(module: types.ModuleType, old: str, new: str) -> types.ModuleType:
    src = open(module.__file__, encoding="utf-8").read()
    assert src.count(old) == 1, f"the mutation's text must match exactly once in {module.__name__}: {old!r}"
    m = types.ModuleType(module.__name__ + "_mutant")
    m.__file__ = module.__file__
    import sys
    sys.modules[m.__name__] = m
    try:
        exec(compile(src.replace(old, new), module.__file__ + " (mutant)", "exec"), m.__dict__)
    finally:
        sys.modules.pop(m.__name__, None)
    return m


def _patch(monkeypatch, module, mutant, *names: str) -> None:
    for n in names:
        monkeypatch.setattr(module, n, getattr(mutant, n))


def _killed(check, *args) -> None:
    with pytest.raises((AssertionError, ValueError, RuntimeError, pytest.fail.Exception)):
        check(*args)


def test_m1_race_at_the_full_cushion(monkeypatch) -> None:
    from tests.test_three_way_redraw import check_race_oracles

    m = _mutant(RD, "    L = inward(min(l, c - x), lattice)", "    L = inward(min(l, c), lattice)")
    _patch(monkeypatch, RD, m, "race", "race_net")
    _killed(check_race_oracles)


def test_m2_race_at_the_target_sides_cost(monkeypatch) -> None:
    from tests.test_three_way_redraw import check_race_oracles

    m = _mutant(RD, "    r = race(l, g, _frac(c_before) - e, xs, lattice)", "    r = race(l, g, _frac(c_before) - e, xt, lattice)")
    _patch(monkeypatch, RD, m, "race_net")
    _killed(check_race_oracles)


def test_m3_and_m4_outward_rounding(monkeypatch) -> None:
    from tests.test_three_way_redraw import check_race_oracles, check_walk_oracles

    m = _mutant(RD, "    return q * math.floor(L / q)", "    return q * math.ceil(L / q)")
    _patch(monkeypatch, RD, m, "inward", "race", "race_net", "walk_barriers", "walk_net")
    _killed(check_race_oracles, (RD.LATTICE,))
    _killed(check_walk_oracles)


def _near_floor_run() -> None:
    rules = J.ToyRules(combine_fee=20, billing=21, target=1000, mll=60, dll=35, activation_fee=20, funded_mll=60,
                       win_day=50, payout_days=2, payout_share=0.5, payout_cap=400, split=1.0, payout_lag=1)
    sch = J.Schedule("near", tuple(J.Trade(session=s, decision=600 + 60 * i, entry=605 + 60 * i, exit=650 + 60 * i,
                                           exit_reason="target", g=10, l=10, tick_value=5.0, entry_cost=0.5,
                                           x_target=0.25, x_stop=3.0) for s in range(40) for i in range(3)))
    from extended import three_way_runner as R
    from extended import three_way_seeds as S

    plan = R.Plan(seed=S.issue("tests"), part=S.PARTS["tests"], history=0, starts=(0,), seed_indices=tuple(range(64)),
                  horizon=30, block_sessions=40)
    R.run(sch, rules, plan)


def test_m5_the_journeys_barrier_at_the_target_sides_cost(monkeypatch) -> None:
    _near_floor_run()                                                   # the real barrier: the clip never binds
    m = _mutant(J, '    x = xs if t.law == "race" else max(xs, xf)', '    x = t.x_target + extra')
    _patch(monkeypatch, J, m, "_barrier")
    _killed(_near_floor_run)


def test_m6_the_twin_not_complemented(monkeypatch) -> None:
    from tests.test_three_way_keys import test_the_antithetic_complement_is_exact

    m = _mutant(K, "    if twin:\n        i = np.uint64(TOP) - i", "    if False:\n        i = np.uint64(TOP) - i")
    _patch(monkeypatch, K, m, "to_uniform", "uniforms")
    _killed(test_the_antithetic_complement_is_exact)


def test_m7_the_coin_key_without_its_start(monkeypatch) -> None:
    from tests.test_three_way_keys import test_keys_collide_nowhere_across_starts_seeds_moments_and_kinds

    m = _mutant(K, "start=self.start, underlying=UNDERLYING[underlying]", "start=0, underlying=UNDERLYING[underlying]")
    _patch(monkeypatch, K, m, "Unit")
    _killed(test_keys_collide_nowhere_across_starts_seeds_moments_and_kinds)


def test_m8_the_ladder_on_the_coins_stream(monkeypatch) -> None:
    from tests.test_three_way_runner import test_the_enforcement_stream_is_apart_from_the_coin

    old = ('        return seed_key(self.seed, "enforce", part=self.part, history=self.history, seed_index=self.seed_index,\n'
           '                        start=self.start, account=int(account), request=int(request))')
    m = _mutant(K, old, "        return self.coin_key(int(account) * 64 + int(request), RACE)")
    _patch(monkeypatch, K, m, "Unit")
    _killed(test_the_enforcement_stream_is_apart_from_the_coin)


def test_m9_mcdiarmids_factor(monkeypatch) -> None:
    from tests.test_three_way_stats import check_fallback_is_hoeffding

    m = _mutant(ST, "        c = d.weight * 2.0 * float(d.r)", "        c = d.weight * float(d.r)")
    _patch(monkeypatch, ST, m, "mcdiarmid")
    _killed(check_fallback_is_hoeffding)


def test_m10_the_clip_not_applied(monkeypatch) -> None:
    from tests.test_three_way_stats import check_clips_bind

    m = _mutant(ST, "        return np.clip(v, a, b)", "        return v")
    _patch(monkeypatch, ST, m, "Dimension")
    _killed(check_clips_bind)


def test_m11_overlap_admitted(monkeypatch) -> None:
    from tests.test_three_way_runner import test_overlap_and_shared_moments_and_windows_are_refused

    m = _mutant(J, "            if day and t.entry < day[-1].exit:", "            if False:")
    _patch(monkeypatch, J, m, "Schedule")
    _killed(test_overlap_and_shared_moments_and_windows_are_refused)


def test_m12_the_exact_programs_probabilities_swapped(monkeypatch) -> None:
    from tests.test_three_way_runner import test_the_exact_program_is_a_brute_force_enumeration

    m = _mutant(J, "            b.w = b.w * (p if win else 1.0 - p)", "            b.w = b.w * (1.0 - p if win else p)")
    _patch(monkeypatch, J, m, "_trade_dp")
    _killed(test_the_exact_program_is_a_brute_force_enumeration)


def test_m13_the_eb_constant(monkeypatch) -> None:
    from tests.test_three_way_stats import test_the_empirical_bernstein_bound_is_the_notes_script

    m = _mutant(ST, "    lg = math.log(2.0 / alpha)\n    return float(D.mean()", "    lg = math.log(1.0 / alpha)\n    return float(D.mean()")
    _patch(monkeypatch, ST, m, "eb_lower")
    _killed(test_the_empirical_bernstein_bound_is_the_notes_script)


def test_m14_the_held_out_refusal_removed(monkeypatch) -> None:
    from tests.test_three_way_stats import test_the_resampled_size_reads_the_search_years_only

    m = _mutant(ST, "    if (d >= HELD_OUT_FIRST).any():", "    if False:")
    _patch(monkeypatch, ST, m, "refuse_held_out", "resampled_size")
    _killed(test_the_resampled_size_reads_the_search_years_only)


def test_m15_hoeffdings_width_dropped(monkeypatch) -> None:
    from tests.test_three_way_stats import test_a_planted_edge_is_found_at_the_stated_power_and_none_under_the_null

    m = _mutant(ST, "    return float(d.mean() - math.sqrt(2.0 * math.log(1.0 / alpha) / d.size))", "    return float(d.mean())")
    _patch(monkeypatch, ST, m, "hoeffding_terms")
    _killed(test_a_planted_edge_is_found_at_the_stated_power_and_none_under_the_null)


def test_m16_the_block_bound_removed(monkeypatch) -> None:
    from tests.test_three_way_runner import test_overlap_and_shared_moments_and_windows_are_refused

    m = _mutant(J, "    if start < 0 or horizon < 1 or start + horizon > block_sessions:", "    if start < 0 or horizon < 1:")
    _patch(monkeypatch, J, m, "check_window")
    _killed(test_overlap_and_shared_moments_and_windows_are_refused)


def test_m17_vacuity_at_more_than_one_half(monkeypatch) -> None:
    from tests.test_three_way_stats import test_the_time_legs_sizes_and_vacuity

    m = _mutant(ST, '    return "VACUOUS" if size >= VACUOUS else', '    return "VACUOUS" if size > VACUOUS else')
    _patch(monkeypatch, ST, m, "label")
    _killed(test_the_time_legs_sizes_and_vacuity)


def test_m18_the_guard_comparing_integers(monkeypatch) -> None:
    from tests.test_three_way_keys import test_the_guard_refuses_the_traps_and_a_key_without_its_start

    m = _mutant(K, "        s = key_state(k)\n        prev = self.states.get(s)\n        if prev is not None and prev != k:\n            raise ValueError(f\"REFUSED (2.3): two keys give one generate_state: {prev} and {k}\")\n        self.states[s] = k\n\n    def keys",
                "        s = k\n        prev = self.states.get(s)\n        if prev is not None and prev != k:\n            raise ValueError(f\"REFUSED (2.3): two keys give one generate_state: {prev} and {k}\")\n        self.states[s] = k\n\n    def keys")
    _patch(monkeypatch, K, m, "KeyGuard")
    _killed(test_the_guard_refuses_the_traps_and_a_key_without_its_start)
