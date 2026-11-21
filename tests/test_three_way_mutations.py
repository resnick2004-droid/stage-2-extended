"""Wave 3.2: a mutation of each core piece of the three-way runner is killed by its check, and **the same check passes on
an identity mutant** -- the record that the checks have teeth and that the harness is not what kills (corrective cycle 2,
the red team's rm-1; fast; no engine, no bar).

**The harness.** `_mutant` compiles the module's own source with one textual change (it must match exactly once) as a
module apart, and **binds every exception class the source module defines to the real module's class**, so a check's
`pytest.raises(R.HeldOutRefused)` catches the mutant's refusal as it would the real one (rm-1: four kills had counted a
mutant's own exception class escaping). `_killed` counts only an `AssertionError`, a pytest failure, or one of the
build's own refusals (an exception whose message begins "REFUSED", raised by the code under test catching the mutation);
any other exception propagates and fails the test. The mutant is patched in through **the harness's own
`pytest.MonkeyPatch`**, undone after the check, so a check that undoes its own monkeypatch part-way never undoes the
mutant (the third re-read's m-1). Every mutant below has two tests: `test_mutant_killed[<id>]` (the
real change must fail its check) and `test_identity_control_survives[<id>]` (the source compiled apart with no change,
through the same harness and check, must pass).

| id | the piece | the check that kills it |
|---|---|---|
| M1 | the race's barrier at the full cushion, min(l, c) | `check_race_oracles` |
| M2 | the race's barrier at the target side's cost | `check_race_oracles` (unequal exit costs, M-4) |
| M3 | the shared path's lattice rounded outward | `check_race_oracles` at lattice 1 |
| M5 | the journey's barrier at the target side's cost | the journey's floor invariant, near the floor with a daily limit |
| M6 | the twin reading u, not 1 - u | `test_the_antithetic_complement_is_exact` |
| M7 | the coin key without its start (choice 3) | the start check at construction |
| M8 | the denial ladder drawn from the coin's race stream | `test_the_enforcement_stream_is_apart_from_the_coin` |
| M9 | McDiarmid's c_u without its factor 2 | `check_fallback_is_hoeffding` |
| M10 | a source-(ii) clip not applied | `check_clips_bind` |
| M11 | overlapping positions admitted | `test_overlap_and_shared_moments_and_windows_are_refused` |
| M12 | the exact program's race probabilities swapped | `test_the_exact_program_is_a_brute_force_enumeration` |
| M13 | the empirical-Bernstein bound at ln(1/alpha) | `test_the_empirical_bernstein_bound_is_the_notes_script` |
| M14 | the resample's held-out refusal removed | `test_the_resampled_size_reads_the_search_years_only` |
| M15 | Hoeffding's width dropped | `test_a_planted_edge_is_found_at_the_stated_power_and_none_under_the_null` |
| M16 | the block bound removed | `test_overlap_and_shared_moments_and_windows_are_refused` |
| M17 | vacuity at more than one half | `test_the_time_legs_sizes_and_vacuity` |
| M18 | the key guard comparing integers, not `generate_state` | `test_the_guard_refuses_the_traps_and_a_key_without_its_start` |
| W | the simulation's race at the unraced p = l / (l + g) | `test_m1_the_journeys_race_books_race_net_on_a_fractional_grid` |
| A | the journey's race rounded to whole ticks | `test_b1_the_forced_loss_toy_fails_and_replaces_every_account` |
| B | the simulation's walk: the time exit at the stop's cost | `test_m2_the_simulations_walk_step_books_the_walks_outcome` |
| B2 | the simulation's walk: the step size dropped | `test_m2_the_simulations_walk_step_books_the_walks_outcome` |
| C | the exact program's walk: the step size dropped | `test_m2_the_exact_programs_walk_step_is_walk_net` |
| K | the betting bound's variance not predictable | `test_the_betting_bounds_bets_are_predictable` |
| O | a group of exactly n_min starts dropped | `test_the_time_legs_sizes_and_vacuity` |
| P | the gate at the upper quantile | `test_the_gate_at_h_g_and_the_limit_check` |
| P2 | the gate's median over starts replaced by the mean | `test_the_gate_at_h_g_and_the_limit_check` |
| R | the resample's refusal admitting 2024-01-02 itself | `test_the_resampled_size_reads_the_search_years_only` |
| R2 | the runner's held-out refusal admitting 2024-01-02 itself | `test_m10_held_out_sessions_are_refused_unless_the_joint_test_is_named` |
| S | the resample not centred | `test_the_resampled_size_reads_the_search_years_only` |
| U | the exact program's denied account kept, not replaced | `test_u_the_exact_programs_denial_is_the_simulations` |
| N1 | the exact program's state without its pass (m-11) | `test_m11_the_exact_programs_passed_survives_its_merges` |
| N2 | a functional through `stat` admitted (m-3) | `test_admission` |
| N3 | the role table not enforced (m-9) | `test_m9_each_seed_draws_only_its_role` |
| N4 | the guard's sample storing nothing (B-2) | `test_b2_the_guard_checks_every_start_and_stores_its_sample_only` |
| N5 | R-10's residual step at one half | `check_walk_oracles` |
| N6 | a negative half-width admitted (m-6) | `test_the_gate_at_h_g_and_the_limit_check` |
| N7 | the walk's chunks read from step zero | `check_chunk_invariance` (the chunk set where the mutant reads it) |
| N8 | the runner's held-out refusal removed (m-10) | `test_m10_held_out_sessions_are_refused_unless_the_joint_test_is_named` |
| N9 | the vectorised denial drawn from the coin kind | `test_the_wrappers_and_the_refusals` |
| RB1 | a lane below its costs left untaken, simulation and exact program (the first cycle's rule) | `test_rb1_no_unit_is_stranded_at_h3as_costs` |
| RB1a | a lane below its costs left untaken in the simulation only | `test_rb1_the_exact_program_shares_the_fix` |
| RB1b | a lane below its costs left untaken in the exact program only | `test_rb1_the_exact_program_shares_the_fix` |
| RB1c | the walk's flatten not clipped at the floor | `test_rb1_the_walks_flatten_is_clipped_at_the_floor_and_fails_the_account` |
| RB1d | the journey's walk barrier back at max(x_stop, x_flat) | `test_m2_the_exact_programs_walk_step_is_walk_net` |
| TF | the take read from the exit's law (the template read's m-1) | `test_m1_the_take_does_not_read_the_exit` |
| PL | a profit-level exit sent to the walk (m-2) | `test_the_exit_state_map_is_r10s_and_refuses_any_other` |
| PLg | the profit level ignored, the race at g | `test_m2_a_profit_level_races_at_min_g_level` |
| LVg | the profit level booked as gross ticks, not the engine's net need (m-3) | `test_m2_a_profit_level_races_at_min_g_level` |
| RB1w | a walk-only reversion of the failure at the fill (the third re-read's m-1) | `test_rb1_no_unit_is_stranded_at_h3as_costs` (its walk half) |
| RB1e | the failure at the fill booked at half the room, not the clip (m-2) | `test_rb1_forced_losses_breach_and_replace_every_account` |
| WG | the simulation's walk at g, not the level's target (m-4 (a)) | `test_m4_the_journeys_walk_with_a_profit_level` |
| WGd | the exact program's walk at g (m-4 (a)) | `test_m4_the_journeys_walk_with_a_profit_level` |
| WD | the walk's flatten clipped at the floor's room where the daily limit binds (m-4 (b)) | `test_m4_the_walks_clip_where_the_daily_limit_binds` |
| N2c | a daily limit below a trade's costs admitted (n-2) | `test_n2_a_daily_limit_below_a_trades_costs_is_refused` |
| N3m | the failures at the fill dropped by the exact program's merge (n-3) | `test_n3_the_failures_at_the_fill_are_reported_and_kept_exactly` |
| FF | a failure at the fill not counted apart (B-2) | `test_b2_an_account_below_its_costs_fails_at_the_fill_and_one_above_takes_the_race` |
| SCf | the walk's step rounded down, not up (s-c) | `test_s_c_the_walks_step_by_the_governing_rule` |
| SCr | the walk refusing a step that does not divide the bracket (s-c) | `test_s_c_the_walks_step_by_the_governing_rule` |
| SCx | S1's step from the realised exit, not the limit (s-c) | `test_s_c_the_walk_never_reads_the_realised_exit` |
| SCn | S1's steps from the realised exit, not the limit (s-c) | `test_s_c_the_walk_never_reads_the_realised_exit` |
| SCt | S1's s and n from the time limit, not the limit capped at the flatten (MINOR-1) | `test_minor1_a_flatten_bound_walks_t_is_the_minutes_to_the_flatten` |
| HT | H4's tests seed drawing in H4-0's and H4-B's fields again (MINOR-3) | `test_minor3_h4s_tests_seed_draws_only_in_its_own_part` |
| HS | the coin's schedule-side seed drawing in H4-B's field too (wt/wt-h4 0727615) | `test_h4s_schedule_side_seed_draws_only_coin_keys_in_h4_s` |
| TN | the tests' seed unrestricted again (the gatekeeper's item 5) | `test_gk5_the_tests_seed_draws_in_the_tests_part_only` |
| FR | the field rules not applied (H4-S, H4-U, the smaller-J report) | `test_gk5_the_field_rules_hold_h4s_h4u_and_the_smaller_j_report` |
| FM | `key_matrix` checking a part's fields on its first row only | `test_gk5_the_field_rules_hold_h4s_h4u_and_the_smaller_j_report` |

The red team's U as its driver wrote it (`d.dead` left False) is **an equivalent mutant**: the denied copies are replaced
by `_replace_accounts` whatever their flag, so no test can kill it; U here is the law-changing form.
"""
from __future__ import annotations

import importlib
import sys
import types

import pytest

from extended import three_way_fastkeys as F
from extended import three_way_journey as J
from extended import three_way_keys as K
from extended import three_way_redraw as RD
from extended import three_way_runner as RU
from extended import three_way_s1 as S1
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
    for name, obj in vars(module).items():                 # rm-1: the real module's exception classes
        if isinstance(obj, type) and issubclass(obj, BaseException) and obj.__module__ == module.__name__:
            m.__dict__[name] = obj
    return m


def _killed(check, *args) -> None:
    try:
        check(*args)
    except (AssertionError, pytest.fail.Exception):
        return
    except Exception as exc:                                # noqa: BLE001
        if str(exc).startswith("REFUSED"):
            return
        raise
    pytest.fail("the mutant survived its check")


def _near_floor_run() -> None:
    rules = J.ToyRules(combine_fee=20, billing=21, target=1000, mll=60, dll=35, activation_fee=20, funded_mll=60,
                       win_day=50, payout_days=2, payout_share=0.5, payout_cap=400, split=1.0, payout_lag=1)
    sch = J.Schedule("near", tuple(J.Trade(session=s, decision=600 + 60 * i, entry=605 + 60 * i, exit=650 + 60 * i,
                                           exit_reason="target", g=10, l=10, tick_value=5.0, entry_cost=0.5,
                                           x_target=0.25, x_stop=3.0) for s in range(40) for i in range(3)))
    plan = RU.Plan(seed=SE.issue("tests"), part=SE.PARTS["tests"], history=0, starts=(0,),
                   seed_indices=tuple(range(64)), horizon=30, block_sessions=40)
    RU.run(sch, rules, plan)


def check_near_floor() -> None:
    """The floor invariant on a near-floor run: no booked change passes the floor or the daily limit."""
    _near_floor_run()


#: id -> (module, old, new, names patched, (the check's module, the check's name), its arguments' kind)
#: kinds: "" none; "mp" the monkeypatch; "mp_m" the monkeypatch and the mutant; "lat1" lattice 1
MUTANTS = {
    "M1": (RD, "    L = inward(min(l, c - x), lattice)", "    L = inward(min(l, c), lattice)", ("race", "race_net"),
           ("tests.test_three_way_redraw", "check_race_oracles"), ""),
    "M2": (RD, "    r = race(l, g, _frac(c_before) - e, xs, lattice)", "    r = race(l, g, _frac(c_before) - e, xt, lattice)",
           ("race_net",), ("tests.test_three_way_redraw", "check_race_oracles"), ""),
    "M3": (RD, "    return q * math.floor(L / q)", "    return q * math.ceil(L / q)", ("inward", "race", "race_net"),
           ("tests.test_three_way_redraw", "check_race_oracles"), "lat1"),
    "M5": (J, "    e, xs = t.entry_cost + extra, t.x_stop + extra\n    return np.minimum(",
           "    e, xs = t.entry_cost + extra, t.x_target + extra\n    return np.minimum(", ("_barrier", "_classes"),
           ("tests.test_three_way_mutations", "check_near_floor"), ""),
    "M6": (K, "    if twin:\n        i = np.uint64(TOP) - i", "    if False:\n        i = np.uint64(TOP) - i",
           ("to_uniform", "uniforms"), ("tests.test_three_way_keys", "test_the_antithetic_complement_is_exact"), ""),
    "M7": (K, "start=self.start, underlying=UNDERLYING[underlying]", "start=0, underlying=UNDERLYING[underlying]",
           ("Unit",), ("tests.test_three_way_keys", "test_keys_collide_nowhere_across_starts_seeds_moments_and_kinds"),
           ""),
    "M8": (K, '        key = seed_key(self.seed, "enforce", part=self.part, history=self.history, seed_index=self.seed_index,\n'
              '                       start=self.start, account=int(account), request=int(request))',
           "        key = self.coin_key(int(account) * 64 + int(request), RACE)", ("Unit",),
           ("tests.test_three_way_runner", "test_the_enforcement_stream_is_apart_from_the_coin"), ""),
    "M9": (ST, "        c = d.weight * 2.0 * float(d.r)", "        c = d.weight * float(d.r)", ("mcdiarmid",),
           ("tests.test_three_way_stats", "check_fallback_is_hoeffding"), ""),
    "M10": (ST, "        return np.clip(v, a, b)", "        return v", ("Dimension",),
            ("tests.test_three_way_stats", "check_clips_bind"), ""),
    "M11": (J, "            if day and t.entry < day[-1].exit:", "            if False:", ("Schedule",),
            ("tests.test_three_way_runner", "test_overlap_and_shared_moments_and_windows_are_refused"), ""),
    "M12": (J, "            b.w = b.w * (p if win else 1.0 - p)", "            b.w = b.w * (1.0 - p if win else p)",
            ("_trade_dp",), ("tests.test_three_way_runner", "test_the_exact_program_is_a_brute_force_enumeration"), ""),
    "M13": (ST, "    lg = math.log(2.0 / alpha)\n    return float(D.mean()", "    lg = math.log(1.0 / alpha)\n    return float(D.mean()",
            ("eb_lower",), ("tests.test_three_way_stats", "test_the_empirical_bernstein_bound_is_the_notes_script"), ""),
    "M14": (ST, "    if (d >= HELD_OUT_FIRST).any():", "    if False:", ("refuse_held_out", "resampled_size"),
            ("tests.test_three_way_stats", "test_the_resampled_size_reads_the_search_years_only"), ""),
    "M15": (ST, "    return float(d.mean() - math.sqrt(2.0 * math.log(1.0 / alpha) / d.size))", "    return float(d.mean())",
            ("hoeffding_terms",),
            ("tests.test_three_way_stats", "test_a_planted_edge_is_found_at_the_stated_power_and_none_under_the_null"), ""),
    "M16": (J, "    if start < 0 or horizon < 1 or start + horizon > block_sessions:", "    if start < 0 or horizon < 1:",
            ("check_window",), ("tests.test_three_way_runner", "test_overlap_and_shared_moments_and_windows_are_refused"),
            ""),
    "M17": (ST, '    return "VACUOUS" if size >= VACUOUS else', '    return "VACUOUS" if size > VACUOUS else', ("label",),
            ("tests.test_three_way_stats", "test_the_time_legs_sizes_and_vacuity"), ""),
    "M18": (K, "        st = key_state(k)\n", "        st = k\n", ("KeyGuard",),
            ("tests.test_three_way_keys", "test_the_guard_refuses_the_traps_and_a_key_without_its_start"), ""),
    "W": (J, "        p = Lt / (Lt + G)\n        win = RD.race_outcome(u, p, arm.plant_eps)",
          "        p = float(t.l) / (float(t.l) + G)\n        win = RD.race_outcome(u, p, arm.plant_eps)",
          ("_trade_mc",), ("tests.test_three_way_runner",
                           "test_m1_the_journeys_race_books_race_net_on_a_fractional_grid"), "mp"),
    "A": (J, "    return np.minimum(float(t.l), (room - e - xs) / t.tvn)",
          "    return np.floor(np.minimum(float(t.l), (room - e - xs) / t.tvn) + 1e-9)", ("_barrier", "_classes"),
          ("tests.test_three_way_runner", "test_b1_the_forced_loss_toy_fails_and_replaces_every_account"), "mp"),
    "B": (J, "        cost = np.where(kind == 1, xt, np.where(kind == -1, xs, xf))",
          "        cost = np.where(kind == 1, xt, np.where(kind == -1, xs, xs))", ("_trade_mc",),
          ("tests.test_three_way_runner", "test_m2_the_simulations_walk_step_books_the_walks_outcome"), ""),
    "B2": (RD, "        pos += c\n    val = np.where(kind == -1, -L, np.where(kind == 1, G, i * float(s)))",
           "        pos += c\n    val = np.where(kind == -1, -L, np.where(kind == 1, G, i))", ("walk_run",),
           ("tests.test_three_way_runner", "test_m2_the_simulations_walk_step_books_the_walks_outcome"), ""),
    "C": (J, "np.full(len(b), -e + float(v) * t.tvn - cost)", "np.full(len(b), -e + float(v) / s * t.tvn - cost)",
          ("_trade_dp",), ("tests.test_three_way_runner", "test_m2_the_exact_programs_walk_step_is_walk_net"), ""),
    "K": (ST, "    sq = np.concatenate([[0.0], np.cumsum((y - mus) ** 2)[:-1]])", "    sq = np.cumsum((y - mus) ** 2)",
          ("bets",), ("tests.test_three_way_stats", "test_the_betting_bounds_bets_are_predictable"), ""),
    "O": (ST, "    ok = [g for g in delta_hat if int(counts[g]) >= int(n_min)]",
          "    ok = [g for g in delta_hat if int(counts[g]) > int(n_min)]", ("condition",),
          ("tests.test_three_way_stats", "test_the_time_legs_sizes_and_vacuity"), ""),
    "P": (ST, "    lowq = float(np.quantile(med, q))", "    lowq = float(np.quantile(med, 1.0 - q))",
          ("long_run_gate", "gate_reading"), ("tests.test_three_way_stats", "test_the_gate_at_h_g_and_the_limit_check"), ""),
    "P2": (ST, "    med = np.median(g, axis=0)", "    med = np.mean(g, axis=0)", ("long_run_gate", "gate_reading"),
           ("tests.test_three_way_stats", "test_the_gate_at_h_g_and_the_limit_check"), ""),
    "R": (ST, "    if (d >= HELD_OUT_FIRST).any():", "    if (d > HELD_OUT_FIRST).any():", ("refuse_held_out", "resampled_size"),
          ("tests.test_three_way_stats", "test_the_resampled_size_reads_the_search_years_only"), ""),
    "R2": (RU, "        held = [w for w in windows if (w >= HELD_OUT_FIRST).any()]",
           "        held = [w for w in windows if (w > HELD_OUT_FIRST).any()]", ("Plan",),
           ("tests.test_three_way_runner", "test_m10_held_out_sessions_are_refused_unless_the_joint_test_is_named"), ""),
    "S": (ST, "    x = x - x.mean()\n    n = x.size", "    n = x.size", ("resampled_size",),
          ("tests.test_three_way_stats", "test_the_resampled_size_reads_the_search_years_only"), ""),
    "U": (J, "        p = _replace_accounts(parts[0], np.ones(len(parts[0]), bool), np.zeros(len(parts[0]), bool), rules)",
          "        p = parts[0]", ("_close",),
          ("tests.test_three_way_runner", "test_u_the_exact_programs_denial_is_the_simulations"), ""),
    "N1": (J, "within, L.ahead, L.first_pass > 0]", "within, L.ahead]", ("_state_key",),
           ("tests.test_three_way_runner", "test_m11_the_exact_programs_passed_survives_its_merges"), ""),
    "N2": (ST, "        if self.stat is not None:", "        if False:", ("Dimension",),
           ("tests.test_three_way_stats", "test_admission"), ""),
    "N3": (SE, "    use = ROLE_USE[seed.role]\n    if use is None:", "    use = ROLE_USE[seed.role]\n    if True:",
           ("check_use",), ("tests.test_three_way_keys", "test_m9_each_seed_draws_only_its_role"), ""),
    "N4": (K, "        return start in self.sample_starts and", "        return False and", ("KeyGuard",),
           ("tests.test_three_way_runner", "test_b2_the_guard_checks_every_start_and_stores_its_sample_only"), ""),
    "N5": (RD, "    if bot:\n        return rho_d / (s + rho_d)", "    if bot:\n        return s / (s + s)",
           ("_p_up", "walk_law", "walk_net"),
           ("tests.test_three_way_redraw", "check_walk_oracles"), ""),
    "N6": (ST, "    if not halfwidth >= 0:", "    if False:", ("limit_check",),
           ("tests.test_three_way_stats", "test_the_gate_at_h_g_and_the_limit_check"), ""),
    "N7": (J, "first=first, record=False)", "first=0, record=False)", ("_trade_mc",),
           ("tests.test_three_way_runner", "check_chunk_invariance"), "mp_m"),
    "N8": (RU, "        if self.dates is not None:\n            self._check_dates()", "        if False:\n            pass",
           ("Plan",), ("tests.test_three_way_runner",
                       "test_m10_held_out_sessions_are_refused_unless_the_joint_test_is_named"), ""),
    "N9": (F, '    M = key_matrix(seed, "enforce", part=part, history=history, seed_index=seed_index, start=start, account=account,\n'
              '                   request=request)',
           '    M = key_matrix(seed, "coin", part=part, history=history, seed_index=seed_index, start=start, underlying=1,\n'
           '                   moment=account, draw_kind=request * 0 + 2)', ("enforce_uniforms",),
           ("tests.test_three_way_fastkeys", "test_the_wrappers_and_the_refusals"), ""),
    "RB1": (J, "    fail = act & ~take & floor_bound\n", "    fail = act & ~take & floor_bound & False\n",
            ("_classes",), ("tests.test_three_way_runner", "test_rb1_no_unit_is_stranded_at_h3as_costs"), "mp"),
    "RB1w": (J, "    fail = act & ~take & floor_bound\n", "    fail = act & ~take & floor_bound & (t.law == 'race')\n",
             ("_classes",), ("tests.test_three_way_runner", "test_rb1_no_unit_is_stranded_at_h3as_costs"), "mp"),
    "RB1e": (J, "        _settle(L, fail, -room, rules)\n    taken = normal", "        _settle(L, fail, -0.5 * room, rules)\n    taken = normal",
             ("_trade_mc",), ("tests.test_three_way_runner", "test_rb1_forced_losses_breach_and_replace_every_account"),
             "mp"),
    "RB1a": (J, "    if fail.any():                                          # failed at the fill: to the floor, breached, counted",
             "    if False:", ("_trade_mc",), ("tests.test_three_way_runner", "test_rb1_the_exact_program_shares_the_fix"),
             ""),
    "RB1b": (J, "    if fail.any():                                          # failed at the fill (RB-1, B-2): one branch, certain",
             "    if False:", ("_trade_dp",), ("tests.test_three_way_runner", "test_rb1_the_exact_program_shares_the_fix"),
             ""),
    "RB1c": (J, "        change = np.where(normal, np.maximum(-e + val * t.tvn - cost, -room), change)",
             "        change = np.where(normal, -e + val * t.tvn - cost, change)", ("_trade_mc",),
             ("tests.test_three_way_runner",
              "test_rb1_the_walks_flatten_is_clipped_at_the_floor_and_fails_the_account"), ""),
    "RB1d": (J, "    e, xs = t.entry_cost + extra, t.x_stop + extra\n    return np.minimum(",
             "    e, xs = t.entry_cost + extra, (t.x_stop if t.law == 'race' else max(t.x_stop, t.x_flat)) + extra\n    return np.minimum(",
             ("_barrier", "_classes"), ("tests.test_three_way_runner", "test_m2_the_exact_programs_walk_step_is_walk_net"),
             ""),
    "TF": (J, "    return np.minimum(float(t.l), (room - e - max(xs, xf)) / t.tvn)",
           "    return np.minimum(float(t.l), (room - e - (xs if t.law == 'race' else max(xs, xf))) / t.tvn)",
           ("_l_fill", "_classes"), ("tests.test_three_way_runner", "test_m1_the_take_does_not_read_the_exit"), ""),
    "PL": (RD, '    "profit_level": "race",', '    "profit_level": "walk",', ("EXIT_LAW",),
           ("tests.test_three_way_redraw", "test_the_exit_state_map_is_r10s_and_refuses_any_other"), ""),
    "PLg": (J, "        return min(float(self.g), (float(self.level) + float(e) + float(xt)) / self.tvn)",
            "        return float(self.g)", ("Trade",),
            ("tests.test_three_way_runner", "test_m2_a_profit_level_races_at_min_g_level"), ""),
    "LVg": (J, "        return min(float(self.g), (float(self.level) + float(e) + float(xt)) / self.tvn)",
            "        return min(float(self.g), float(self.level))", ("Trade",),
            ("tests.test_three_way_runner", "test_m2_a_profit_level_races_at_min_g_level"), ""),
    "WG": (J, "RD.walk_run(read, rows_all.size, G, Lt[rows_all]", "RD.walk_run(read, rows_all.size, float(t.g), Lt[rows_all]",
           ("_trade_mc",), ("tests.test_three_way_runner", "test_m4_the_journeys_walk_with_a_profit_level"), ""),
    "WGd": (J, "law = RD.walk_law(G, float(Lv), s, int(t.walk_n))", "law = RD.walk_law(float(t.g), float(Lv), s, int(t.walk_n))",
            ("_trade_dp",), ("tests.test_three_way_runner", "test_m4_the_journeys_walk_with_a_profit_level"), ""),
    "WD": (J, "        change = np.where(normal, np.maximum(-e + val * t.tvn - cost, -room), change)",
           "        change = np.where(normal, np.maximum(-e + val * t.tvn - cost, -(L.bal - L.floor)), change)",
           ("_trade_mc",), ("tests.test_three_way_runner", "test_m4_the_walks_clip_where_the_daily_limit_binds"), ""),
    "N2c": (J, "    if rules.dll is None:\n        return\n    for t in schedule.trades:",
            "    if True:\n        return\n    for t in schedule.trades:", ("check_costs",),
            ("tests.test_three_way_runner", "test_n2_a_daily_limit_below_a_trades_costs_is_refused"), ""),
    "N3m": (J, "    out.ffail = np.where(w > 0, wf / np.where(w > 0, w, 1.0), 0.0)\n", "", ("_merge",),
            ("tests.test_three_way_runner", "test_n3_the_failures_at_the_fill_are_reported_and_kept_exactly"), ""),
    "FF": (J, "        L.ffail = L.ffail + fail.astype(np.int64)\n        _settle(L, fail, -room, rules)\n    taken = normal",
           "        _settle(L, fail, -room, rules)\n    taken = normal", ("_trade_mc",),
           ("tests.test_three_way_runner",
            "test_b2_an_account_below_its_costs_fails_at_the_fill_and_one_above_takes_the_race"), ""),
    "SCf": (RD, "    return max(1, int(math.ceil(sigma * math.sqrt(T) / math.sqrt(walk_max) - 1e-12)))",
            "    return max(1, int(math.floor(sigma * math.sqrt(T) / math.sqrt(walk_max) - 1e-12)))", ("walk_step",),
            ("tests.test_three_way_redraw", "test_s_c_the_walks_step_by_the_governing_rule"), ""),
    "SCr": (RD, "    if s <= 0 or l <= 0 or g <= 0:\n        raise ValueError(\"the stop, the target and the lattice step",
            "    if s <= 0 or l <= 0 or g <= 0 or l % s or g % s:\n        raise ValueError(\"the stop, the target and the lattice step",
            ("walk_barriers",), ("tests.test_three_way_redraw", "test_s_c_the_walks_step_by_the_governing_rule"), ""),
    "SCx": (S1, "            step = RD.walk_step(v / math.sqrt(MINUTE), limit, J.WALK_MAX) if timed else spec.walk_step",
            "            step = RD.walk_step(v / math.sqrt(MINUTE), max(ex - entry, 1), J.WALK_MAX) if timed else spec.walk_step",
            ("schedule",), ("tests.test_three_way_runner", "test_s_c_the_walk_never_reads_the_realised_exit"), ""),
    "SCn": (S1, "            n_steps = RD.walk_steps(v / math.sqrt(MINUTE), limit, step) if timed else 1",
            "            n_steps = RD.walk_steps(v / math.sqrt(MINUTE), max(ex - entry, 1), step) if timed else 1",
            ("schedule",), ("tests.test_three_way_runner", "test_s_c_the_walk_never_reads_the_realised_exit"), ""),
    "SCt": (S1, "            step = RD.walk_step(v / math.sqrt(MINUTE), limit, J.WALK_MAX) if timed else spec.walk_step\n"
                "            n_steps = RD.walk_steps(v / math.sqrt(MINUTE), limit, step) if timed else 1",
            "            step = RD.walk_step(v / math.sqrt(MINUTE), float(p.time_limit), J.WALK_MAX) if timed else "
            "spec.walk_step\n"
            "            n_steps = RD.walk_steps(v / math.sqrt(MINUTE), float(p.time_limit), step) if timed else 1",
            ("schedule",),
            ("tests.test_three_way_runner", "test_minor1_a_flatten_bound_walks_t_is_the_minutes_to_the_flatten"), ""),
    "HT": (SE, '    "h4_tests": (frozenset({"test", "history", "coin", "enforce"}), frozenset({"H4-T"})),',
           '    "h4_tests": (frozenset({"test", "history", "coin", "enforce"}), frozenset({"H4-T", "H4-0", "H4-B"})),',
           ("ROLE_USE",), ("tests.test_three_way_keys", "test_minor3_h4s_tests_seed_draws_only_in_its_own_part"), ""),
    "HS": (SE, '    "h4s_schedule_side": (frozenset({"coin"}), frozenset({"H4-S"})),',
           '    "h4s_schedule_side": (frozenset({"coin"}), frozenset({"H4-S", "H4-B"})),',
           ("ROLE_USE",),
           ("tests.test_three_way_keys", "test_h4s_schedule_side_seed_draws_only_coin_keys_in_h4_s"), ""),
    "TN": (SE, '    if part is None or names.get(int(part)) not in parts:',
           '    if seed.role == "tests":\n        return\n    if part is None or names.get(int(part)) not in parts:',
           ("check_use",),
           ("tests.test_three_way_keys", "test_gk5_the_tests_seed_draws_in_the_tests_part_only"), ""),
    "FR": (SE, "    rule = FIELD_RULES.get(seed.role, {}).get((kind, names[int(part)]))",
           "    rule = None", ("check_use",),
           ("tests.test_three_way_keys", "test_gk5_the_field_rules_hold_h4s_h4u_and_the_smaller_j_report"), ""),
    "FM": (F, "                S.check_use(seed, kind, int(pt), {nm: set(np.unique(c.ravel()[rows]).tolist())",
           "                S.check_use(seed, kind, int(pt), {nm: {int(c.ravel()[rows][0])}", ("key_matrix",),
           ("tests.test_three_way_keys", "test_gk5_the_field_rules_hold_h4s_h4u_and_the_smaller_j_report"), ""),
}


def _check(ref):
    mod, name = ref
    return getattr(importlib.import_module(mod), name)


def _run(mid: str, harness: pytest.MonkeyPatch, monkeypatch, identity: bool):
    """The mutant patched in through the harness's own `MonkeyPatch` (the third re-read's m-1): a check that undoes
    its own monkeypatch part-way never undoes the mutant with it."""
    module, old, new, names, ref, kind = MUTANTS[mid]
    m = _mutant(module, old, old if identity else new)
    for n in names:
        harness.setattr(module, n, getattr(m, n))
    args = {"": (), "mp": (monkeypatch,), "mp_m": (monkeypatch, m), "lat1": ((1,),)}[kind]
    return _check(ref), args


@pytest.mark.parametrize("mid", list(MUTANTS))
def test_mutant_killed(mid: str, monkeypatch) -> None:
    harness = pytest.MonkeyPatch()
    try:
        check, args = _run(mid, harness, monkeypatch, identity=False)
        _killed(check, *args)
    finally:
        monkeypatch.undo()
        harness.undo()


@pytest.mark.parametrize("mid", list(MUTANTS))
def test_identity_control_survives(mid: str, monkeypatch) -> None:
    """The source compiled apart unchanged, through the same harness: the check passes (rm-1)."""
    harness = pytest.MonkeyPatch()
    try:
        check, args = _run(mid, harness, monkeypatch, identity=True)
        check(*args)
    finally:
        monkeypatch.undo()
        harness.undo()
