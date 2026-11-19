"""Wave 3.2: a mutation of each core piece of the three-way runner is killed by its check -- the record that the checks
have teeth (fast; no engine, no bar).

Each mutant is the module's own source with one textual change (`_mutant`: the change must match exactly once),
compiled apart; its pieces are patched over the real module's for the one check, which must then fail. The unmutated
check passes in its own test file.

**The build's own** (746a245, updated to corrective cycle 1's code):

| mutant | the piece | the check that kills it |
|---|---|---|
| M1 | the race's barrier at the full cushion, min(l, c) | `check_race_oracles` (a loss passes the floor) |
| M2 | the race's barrier at the target side's cost | `check_race_oracles` (unequal exit costs, M-4) |
| M3 | the shared path's lattice rounded outward | `check_race_oracles` at lattice 1 |
| M5 | the journey's barrier at the target side's cost | the journey's floor invariant, near the floor with a daily loss limit |
| M6 | the twin reading u, not 1 - u | `test_the_antithetic_complement_is_exact` |
| M7 | the coin key without its start (choice 3) | the start check at construction, in `test_keys_collide_nowhere_...` |
| M8 | the denial ladder drawn from the coin's race stream | `test_the_enforcement_stream_is_apart_from_the_coin` |
| M9 | McDiarmid's c_u without its factor 2 | `check_fallback_is_hoeffding` |
| M10 | a source-(ii) clip not applied | `check_clips_bind` |
| M11 | overlapping positions admitted | `test_overlap_and_shared_moments_and_windows_are_refused` |
| M12 | the exact program's race probabilities swapped | `test_the_exact_program_is_a_brute_force_enumeration` |
| M13 | the empirical-Bernstein bound at ln(1/alpha) | `test_the_empirical_bernstein_bound_is_the_notes_script` |
| M14 | the resample's held-out refusal removed | `test_the_resampled_size_reads_the_search_years_only` |
| M15 | Hoeffding's width dropped | `test_a_planted_edge_is_found_at_the_stated_power_and_none_under_the_null` |
| M16 | the block bound removed | `test_overlap_and_shared_moments_and_windows_are_refused` |
| M17 | vacuity at more than one half (not at least) | `test_the_time_legs_sizes_and_vacuity` |
| M18 | the key guard comparing integers, not `generate_state` | `test_the_guard_refuses_the_traps_and_a_key_without_its_start` |

**The red team's survivors** (`docs/reviews/BUILD_W32_H3_2026-11-19.md`, its driver's texts, re-pointed at this code
where B-1's fix moved them), each now killed by the named behaviour test:

| mutant | the piece | the check that kills it |
|---|---|---|
| W | the simulation's race at the unraced p = l / (l + g) | `test_m1_the_journeys_race_books_race_net_on_a_fractional_grid` |
| A | the journey's race rounded to whole ticks (B-1's stranding) | `test_b1_the_forced_loss_toy_fails_and_replaces_every_account` |
| B | the simulation's walk: the time exit charged the stop's cost | `test_m2_the_simulations_walk_step_books_the_walks_outcome` |
| B2 | the simulation's walk: the step size dropped from the value | `test_m2_the_simulations_walk_step_books_the_walks_outcome` |
| C | the exact program's walk: the step size dropped | `test_m2_the_exact_programs_walk_step_is_walk_net` |
| K | the betting bound's variance not predictable | `test_the_betting_bounds_bets_are_predictable` |
| O | a group of exactly n_min starts dropped | `test_the_time_legs_sizes_and_vacuity` |
| P | the gate at the upper quantile | `test_the_gate_at_h_g_and_the_limit_check` (quantiles straddling zero) |
| P2 | the gate's median over starts replaced by the mean | `test_the_gate_at_h_g_and_the_limit_check` (a skewed g) |
| R | the resample's refusal admitting 2024-01-02 itself | `test_the_resampled_size_reads_the_search_years_only` (the boundary date, by behaviour) |
| R2 | the runner's held-out refusal admitting 2024-01-02 itself | `test_m10_held_out_sessions_are_refused_unless_the_joint_test_is_named` |
| S | the resample not centred | `test_the_resampled_size_reads_the_search_years_only` (a constant added changes nothing) |
| U | the exact program's denial keeping the account | `test_u_the_exact_programs_denial_is_the_simulations` |

The red team's U as its driver wrote it (`d.dead` left False) is **an equivalent mutant**: the denied copies are replaced
by `_replace_accounts` whatever their flag, and `dead` is read no more that close, so no test can kill it. The mutant
recorded here is the one that changes the law: the denied account kept, not replaced.

**This cycle's fixes:**

| mutant | the piece | the check that kills it |
|---|---|---|
| N1 | the exact program's state without its pass (m-11) | `test_m11_the_exact_programs_passed_survives_its_merges` |
| N2 | a functional through `stat` admitted (m-3) | `test_admission` |
| N3 | the role table not enforced (m-9) | `test_m9_each_seed_draws_only_its_role` |
| N4 | the guard's sample storing nothing (B-2) | `test_b2_the_guard_checks_every_start_and_stores_its_sample_only` |
| N5 | R-10's residual step at one half (the barrier not raced) | `check_walk_oracles` |
| N6 | a negative half-width admitted (m-6) | `test_the_gate_at_h_g_and_the_limit_check` |
| N7 | the walk's chunks read from step zero | `test_the_walk_read_in_chunks_is_the_walk_read_whole` |
| N8 | the runner's held-out refusal removed (m-10) | `test_m10_held_out_sessions_are_refused_unless_the_joint_test_is_named` |
| N9 | the vectorised denial drawn from the coin kind | `test_the_wrappers_and_the_refusals` |
"""
from __future__ import annotations

import sys
import types

import numpy as np
import pytest

from extended import three_way_fastkeys as F
from extended import three_way_journey as J
from extended import three_way_keys as K
from extended import three_way_redraw as RD
from extended import three_way_runner as RU
from extended import three_way_seeds as SE
from extended import three_way_stats as ST


def _mutant(module: types.ModuleType, old: str, new: str) -> types.ModuleType:
    src = open(module.__file__, encoding="utf-8").read()
    assert src.count(old) == 1, f"the mutation's text must match exactly once in {module.__name__}: {old!r}"
    m = types.ModuleType(module.__name__ + "_mutant")
    m.__file__ = module.__file__
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
    with pytest.raises((AssertionError, ValueError, RuntimeError, TypeError, SE.ProvenanceRefused,
                        pytest.fail.Exception)):
        check(*args)


def _mp(request):
    return request.getfixturevalue("monkeypatch")


# ------------------------------------------------------------------------------------------------ the build's own


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


def test_m3_outward_rounding_on_the_shared_paths_lattice(monkeypatch) -> None:
    from tests.test_three_way_redraw import check_race_oracles

    m = _mutant(RD, "    return q * math.floor(L / q)", "    return q * math.ceil(L / q)")
    _patch(monkeypatch, RD, m, "inward", "race", "race_net")
    _killed(check_race_oracles, (1,))


def _near_floor_run() -> None:
    rules = J.ToyRules(combine_fee=20, billing=21, target=1000, mll=60, dll=35, activation_fee=20, funded_mll=60,
                       win_day=50, payout_days=2, payout_share=0.5, payout_cap=400, split=1.0, payout_lag=1)
    sch = J.Schedule("near", tuple(J.Trade(session=s, decision=600 + 60 * i, entry=605 + 60 * i, exit=650 + 60 * i,
                                           exit_reason="target", g=10, l=10, tick_value=5.0, entry_cost=0.5,
                                           x_target=0.25, x_stop=3.0) for s in range(40) for i in range(3)))
    plan = RU.Plan(seed=SE.issue("tests"), part=SE.PARTS["tests"], history=0, starts=(0,),
                   seed_indices=tuple(range(64)), horizon=30, block_sessions=40)
    RU.run(sch, rules, plan)


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

    old = ('        key = seed_key(self.seed, "enforce", part=self.part, history=self.history, seed_index=self.seed_index,\n'
           '                       start=self.start, account=int(account), request=int(request))')
    m = _mutant(K, old, "        key = self.coin_key(int(account) * 64 + int(request), RACE)")
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

    m = _mutant(K, "        st = key_state(k)\n", "        st = k\n")
    _patch(monkeypatch, K, m, "KeyGuard")
    _killed(test_the_guard_refuses_the_traps_and_a_key_without_its_start)


# ------------------------------------------------------------------------------------------------ the red team's survivors


def test_w_the_unraced_p(monkeypatch) -> None:
    from tests.test_three_way_runner import test_m1_the_journeys_race_books_race_net_on_a_fractional_grid as check

    m = _mutant(J, "        p = Lt / (Lt + float(t.g))\n        u = coins.coin(t, K.RACE)",
                "        p = float(t.l) / (float(t.l) + float(t.g))\n        u = coins.coin(t, K.RACE)")
    _patch(monkeypatch, J, m, "_trade_mc")
    _killed(check, monkeypatch)


def test_a_the_race_rounded_to_whole_ticks(request) -> None:
    from tests.test_three_way_runner import test_b1_the_forced_loss_toy_fails_and_replaces_every_account as check

    mp = _mp(request)
    m = _mutant(J, "    return np.where(Lt * t.tvn > EPS, Lt, 0.0)",
                "    Lt = np.floor(Lt + 1e-9)\n    return np.where(Lt * t.tvn > EPS, Lt, 0.0)")
    _patch(mp, J, m, "_barrier")
    _killed(check, mp)


def test_b_the_time_exit_at_the_stops_cost(monkeypatch) -> None:
    from tests.test_three_way_runner import test_m2_the_simulations_walk_step_books_the_walks_outcome as check

    m = _mutant(J, "        cost = np.where(kind == 1, xt, np.where(kind == -1, xs, xf))",
                "        cost = np.where(kind == 1, xt, np.where(kind == -1, xs, xs))")
    _patch(monkeypatch, J, m, "_trade_mc")
    _killed(check)


def test_b2_the_walks_step_size_dropped_in_the_simulation(monkeypatch) -> None:
    from tests.test_three_way_runner import test_m2_the_simulations_walk_step_books_the_walks_outcome as check

    m = _mutant(RD, "        pos += c\n    val = np.where(kind == -1, -L, np.where(kind == 1, up * s, i * s))",
                "        pos += c\n    val = np.where(kind == -1, -L, np.where(kind == 1, up * s, i))")
    _patch(monkeypatch, RD, m, "walk_run")
    _killed(check)


def test_c_the_walks_step_size_dropped_in_the_exact_program(monkeypatch) -> None:
    from tests.test_three_way_runner import test_m2_the_exact_programs_walk_step_is_walk_net as check

    m = _mutant(J, "np.full(len(b), -e + float(v) * t.tvn - cost)", "np.full(len(b), -e + float(v) / s * t.tvn - cost)")
    _patch(monkeypatch, J, m, "_trade_dp")
    _killed(check)


def test_k_the_betting_variance_not_predictable(monkeypatch) -> None:
    from tests.test_three_way_stats import test_the_betting_bounds_bets_are_predictable as check

    m = _mutant(ST, "    sq = np.concatenate([[0.0], np.cumsum((y - mus) ** 2)[:-1]])", "    sq = np.cumsum((y - mus) ** 2)")
    _patch(monkeypatch, ST, m, "bets")
    _killed(check)


def test_o_a_group_of_exactly_n_min_dropped(monkeypatch) -> None:
    from tests.test_three_way_stats import test_the_time_legs_sizes_and_vacuity as check

    m = _mutant(ST, "    ok = [g for g in delta_hat if int(counts[g]) >= int(n_min)]",
                "    ok = [g for g in delta_hat if int(counts[g]) > int(n_min)]")
    _patch(monkeypatch, ST, m, "condition")
    _killed(check)


def test_p_the_gate_at_the_upper_quantile(monkeypatch) -> None:
    from tests.test_three_way_stats import test_the_gate_at_h_g_and_the_limit_check as check

    m = _mutant(ST, "    lowq = float(np.quantile(med, q))", "    lowq = float(np.quantile(med, 1.0 - q))")
    _patch(monkeypatch, ST, m, "long_run_gate", "gate_reading")
    _killed(check)


def test_p2_the_gates_mean_over_starts(monkeypatch) -> None:
    from tests.test_three_way_stats import test_the_gate_at_h_g_and_the_limit_check as check

    m = _mutant(ST, "    med = np.median(g, axis=0)", "    med = np.mean(g, axis=0)")
    _patch(monkeypatch, ST, m, "long_run_gate", "gate_reading")
    _killed(check)


def test_r_the_resample_admits_the_first_held_out_day(monkeypatch) -> None:
    from tests.test_three_way_stats import test_the_resampled_size_reads_the_search_years_only as check

    m = _mutant(ST, "    if (d >= HELD_OUT_FIRST).any():", "    if (d > HELD_OUT_FIRST).any():")
    _patch(monkeypatch, ST, m, "refuse_held_out", "resampled_size")
    _killed(check)


def test_r2_the_runner_admits_the_first_held_out_day(monkeypatch) -> None:
    from tests.test_three_way_runner import test_m10_held_out_sessions_are_refused_unless_the_joint_test_is_named as check

    m = _mutant(RU, "        held = [w for w in windows if (w >= HELD_OUT_FIRST).any()]",
                "        held = [w for w in windows if (w > HELD_OUT_FIRST).any()]")
    _patch(monkeypatch, RU, m, "Plan")
    _killed(check)


def test_s_the_resample_not_centred(monkeypatch) -> None:
    from tests.test_three_way_stats import test_the_resampled_size_reads_the_search_years_only as check

    m = _mutant(ST, "    x = x - x.mean()\n    n = x.size", "    n = x.size")
    _patch(monkeypatch, ST, m, "resampled_size")
    _killed(check)


def test_u_the_denial_keeps_the_account(monkeypatch) -> None:
    from tests.test_three_way_runner import test_u_the_exact_programs_denial_is_the_simulations as check

    m = _mutant(J, "        p = _replace_accounts(parts[0], np.ones(len(parts[0]), bool), np.zeros(len(parts[0]), bool), rules)",
                "        p = parts[0]")
    _patch(monkeypatch, J, m, "_close")
    _killed(check)


# ------------------------------------------------------------------------------------------------ this cycle's fixes


def test_n1_the_state_without_its_pass(monkeypatch) -> None:
    from tests.test_three_way_runner import test_m11_the_exact_programs_passed_survives_its_merges as check

    m = _mutant(J, "within, L.ahead, L.first_pass > 0]", "within, L.ahead]")
    _patch(monkeypatch, J, m, "_state_key")
    _killed(check)


def test_n2_a_stat_admitted(monkeypatch) -> None:
    from tests.test_three_way_stats import test_admission as check

    m = _mutant(ST, "        if self.stat is not None:", "        if False:")
    _patch(monkeypatch, ST, m, "Dimension")
    _killed(check)


def test_n3_roles_not_enforced(monkeypatch) -> None:
    from tests.test_three_way_keys import test_m9_each_seed_draws_only_its_role as check

    m = _mutant(SE, "    use = ROLE_USE[seed.role]\n    if use is None:", "    use = ROLE_USE[seed.role]\n    if True:")
    _patch(monkeypatch, SE, m, "check_use")
    _killed(check)


def test_n4_the_sample_storing_nothing(monkeypatch) -> None:
    from tests.test_three_way_runner import test_b2_the_guard_checks_every_start_and_stores_its_sample_only as check

    m = _mutant(K, "        return start in self.sample_starts and", "        return False and")
    _patch(monkeypatch, K, m, "KeyGuard")
    _killed(check)


def test_n5_the_residual_step_at_one_half(monkeypatch) -> None:
    from tests.test_three_way_redraw import check_walk_oracles

    m = _mutant(RD, "    q_bar = (s / (s + rho)) if exact else float(s) / (float(s) + float(rho))",
                "    q_bar = Fraction(1, 2) if exact else 0.5")
    _patch(monkeypatch, RD, m, "walk_law", "walk_net")
    _killed(check_walk_oracles)


def test_n6_a_negative_half_width_admitted(monkeypatch) -> None:
    from tests.test_three_way_stats import test_the_gate_at_h_g_and_the_limit_check as check

    m = _mutant(ST, "    if not halfwidth >= 0:", "    if False:")
    _patch(monkeypatch, ST, m, "limit_check")
    _killed(check)


def test_n7_the_walks_chunks_from_step_zero(monkeypatch) -> None:
    from tests.test_three_way_runner import check_chunk_invariance as check

    m = _mutant(J, "first=first, record=False)", "first=0, record=False)")
    _patch(monkeypatch, J, m, "_trade_mc")
    _killed(check, monkeypatch, m)                                       # the chunk set where the mutant reads it


def test_n8_the_runners_held_out_refusal_removed(monkeypatch) -> None:
    from tests.test_three_way_runner import test_m10_held_out_sessions_are_refused_unless_the_joint_test_is_named as check

    m = _mutant(RU, "        if self.dates is not None:\n            self._check_dates()", "        if False:\n            pass")
    _patch(monkeypatch, RU, m, "Plan")
    _killed(check)


def test_n9_the_vectorised_denial_on_the_coin_kind(monkeypatch) -> None:
    from tests.test_three_way_fastkeys import test_the_wrappers_and_the_refusals as check

    m = _mutant(F, '    M = key_matrix(seed, "enforce", part=part, history=history, seed_index=seed_index, start=start, account=account,\n'
                   '                   request=request)',
                '    M = key_matrix(seed, "coin", part=part, history=history, seed_index=seed_index, start=start, underlying=1,\n'
                '                   moment=account, draw_kind=request * 0 + 2)')
    _patch(monkeypatch, F, m, "enforce_uniforms")
    _killed(check)
