"""RD-01's reading runner (`scripts/rd01_reading.py`, `extended/firm_reading.py`, `extended/firm_menu.py`): end to end on
toy campaigns into a temporary results folder (`tests/rd01_reading_synthetic.py`, in a process of its own; section 12's
toy seed and its children), the second build read's fixes (`docs/reviews/BUILD_RD-01_v2_2026-11-16.md`: R1-R6, r1-r8)
each asserted, every refusing check shown to refuse, and the runner's refusals before any read. No bar, no atlas."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV = {**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
       "PYTHONDONTWRITEBYTECODE": "1"}
SECTIONS = ["coverage", "diverge", "grid", "identity", "ladder", "mechanics", "oracle", "paired", "scorecard"]


@lru_cache(maxsize=1)
def found() -> dict:
    p = subprocess.run([sys.executable, str(ROOT / "tests" / "rd01_reading_synthetic.py"), str(ROOT)],
                       capture_output=True, text=True, timeout=900, env=ENV)
    if p.returncode != 0:
        raise AssertionError(f"the toy reading failed:\n{p.stderr[-4000:]}")
    return json.loads(p.stdout.strip().splitlines()[-1])


def test_r4_the_files_and_sections_are_section_15s():
    r = found()
    assert r["files"] == sorted(f"{n}{x}" for n in ("fc_reading", "fc_gate", "fc_menu")
                                for x in (".csv", ".csv.manifest.json"))
    assert r["fr_sections"] == SECTIONS
    assert r["fr_status"] == ["described, not carried"] * 3          # every cell of every file
    assert r["fm_sections"] == ["distribution", "evenness", "flags", "menu", "menu_gate", "paired_more",
                                "variance_share"]


def test_r4_every_manifest_field_section_15_lists():
    r = found()
    m = r["manifest"]
    assert m["prereg_id"] == "RD-01" and m["exploratory"] is False and m["variant_count"] == 8
    assert m["keys"] == ["conventions", "cost_and_table_inputs", "data_manifest_sha256", "horizon_of_month",
                         "identity_rows", "pinning_row", "readings", "record_entries", "run_counts", "seeds", "status"]
    assert r["manifest_seeds"] == [10, ["in use", "reserved", "retired"]]      # every seed, reserved and retired too
    assert r["manifest_counts"] == {"replays": 8, "new": 6, "references": 2, "ladder_replays": 27, "gates": 16}
    assert r["manifest_plans"] == ["DT", "FP", "LU", "QP", "TS"]
    assert r["manifest_dt_schedules"] == ["lenient", "strict"]                 # DT's fee basis at both ends
    assert r["manifest_month_9"] == 252 and r["manifest_data_sha"] == 64       # n1; the data manifest's sha256
    assert r["pin"] == ["E-080", []]                                           # the pinning row, the text checked
    n, bad, plans, dated = r["record_entries"]
    assert n > 100 and bad == [] and plans == ["DT", "FP", "FP, QP", "LU", "QP", "TS"] and dated
    assert r["menu_manifest_step"] is True                                     # the menu: a step on the written files


def test_r3_the_runner_waits_on_three_identity_rows_and_none_is_recorded_here():
    held, tasks, admitted = found()["guard_refuses"]
    assert held is True and tasks == ["Q-104", "Q-80", "Q-93"] and admitted == {}


def test_r1_coverage_by_keyword_on_and_every_shape():
    r = found()
    assert r["tiled_coverage_rows"] > 0 and r["tiled_coverage_in_unit"] is True
    assert r["tiled_coverage_settings"] == ["63:5"] and r["coverage_shapes_per_setting"] == [39]
    assert r["coverage_section_rows"] == 40                                    # 39 shapes and the worst


def test_r6_the_early_block_in_every_reading_and_the_ladders_start_table():
    r = found()
    for k in ("sc_paired_blocks", "sc_card_blocks", "sc_extra_blocks", "sc_path_blocks", "count_blocks",
              "diverge_blocks", "ld_blocks"):
        assert r[k] == ["all", "early", "late"], k
    assert r["elig_is_u_select"] is True and r["elig_judged_is_late"] is True
    assert r["ld_start_rows"] == 81 and r["start_rows_by_section"] == {"scorecard": 80, "ladder": 81}


def test_r2_the_oracles_are_built_and_refuse():
    r = found()
    n = r["neg"]
    for k in ("fee_held", "fee_refused", "fee_missing_refused", "fee_26_micros", "qp_split_page_example",
              "dt_request_held", "dt_increment_refused", "dt_left_refused", "dt_net_refused", "qp_split_refused",
              "qp_split_held", "fp_cap_refused", "ts_held", "ts_gross_refused", "twin_held", "twin_refused"):
        assert n[k] is True, k
    assert n["fp_half_counted"] == 1                                           # a U-7 zero check: counted, not refused
    assert n["twin_bounds_dt"] == [2000.0, 0.4]
    assert r["gt_oracle_measures"] == ["twin_gross_per_funded", "twin_pass_rate"]
    assert r["gt_oracle_stats"] == ["ceiling", "se", "value"] and r["gt_twin_ceilings"] == [[2000.0, 0.4]]
    assert r["gt_twin_finite"] is True
    # on the toy's runs every request and fee was checked, at every plan
    assert r["fp_counts"]["oracle_requests_checked"] > 0 and r["dt_counts"]["oracle_requests_checked"] > 0
    assert r["qp_counts"]["oracle_requests_checked"] > 0 and r["qr_requests"] > 0
    assert r["ts_counts"]["oracle_trades_fee_checked"] == r["ts_counts"]["trades_taken"] > 0
    assert r["fp_counts"]["oracle_trades_fee_checked"] == r["fp_counts"]["trades_taken"] > 0
    assert r["qp_counts"]["acct.funded.floor_oracle_breaches"] == 0.0


def test_r5_the_in_run_counts():
    r = found()
    for k in ("g10_funded_sessions_no_trade", "g10_accounts_idle_30", "g10_accounts_drained",
              "g10_sessions_no_trade_per_funded_account", "zero_peak_hold_queue", "zero_resets_bought",
              "zero_fp_request_above_half_profit", "zero_qp_request_above_reference", "zero_qp_request_below_min",
              "zero_refused_for_cash", "fp_uncapped_ladder_differs", "share_fp_uncapped_ladder_differs",
              "realised_to_intended_capped.combine", "realised_to_intended_capped.funded",
              "stood_aside.combine", "stood_aside.funded", "share_contracts_differ.combine",
              "share_contracts_differ.funded", "tier1_executed_in_window", "tier1_signals_skipped_inside",
              "max_trades_session_account", "sessions_above_trade_line", "share_starts_differs_by_63"):
        assert k in r["fp_keys"], k
    for k in ("martingale_accounts_per_account", "martingale_accounts_firm_wide", "martingale_per_account.funded",
              "share_martingale_firm_wide", "dt_limit_capped_trades", "zero_dt_activation_late", "fees_pro"):
        assert k in r["dt_keys"], k
    assert "g10_accounts_drained" in r["qp_keys"] and r["lu_keys"] == ["lu_fifth_payouts", "lu_household_closures"]
    fp = r["fp_counts"]
    assert fp["acct.funded.forced_untraded"] > 0
    assert fp["acct.funded.forced_day_dealt_elsewhere"] + fp["acct.funded.forced_day_dealt_to_none"] > 0
    assert fp["tier1_executed_in_window"] > 0 and fp["tier1_signals_skipped_inside"] > 0
    assert r["toy_tier1"] == {"open": 6, "inside": 3} and r["tier1_rows"] > 0
    assert fp["fp_funded_trades_read"] > 0 and fp["contracts_compared.funded"] > 0 and fp["g10_funded_accounts"] > 0
    assert r["dt_counts"]["fees_pro"] > 0                                     # A-10's Pro fee in 10.1 item 6
    n = r["neg"]
    assert n["g12_lost_after_stop"] == 1 and n["g12_none_when_last"] == 0
    assert n["g12_in_the_adapter"] == [1, 2, -1250.0, False]                  # the limit day; two dealt, not taken
    assert n["failed_while_owed"] == [1, True, 1, 1]
    assert n["fp_forced_day_signals"] == [4, 8]
    assert n["uncapped_none_below_cap"] == 0 and n["uncapped_differs_at_9000"] == 1
    assert r["start_has_item6"] is True and r["diverge_measures"] == sorted(
        ["evaluations_bought", "fees_activation", "fees_evaluations", "fees_payout", "fees_pro", "funded_activated",
         "funded_lost", "payouts_count", "payouts_gross", "payouts_net", "realised_risk", "trades_taken"])


def test_the_menu_flags_labels_and_items_3_4_10():
    r = found()
    assert r["fm_flags"] == ["E-015's limits", "depends on its request rule", "no effect on these trades",
                             "not stable across blocks"]
    assert r["neg"]["flag_unread_terms"] == [True]                            # corners straddling TS are flagged
    assert r["fm_menu_labels_qp"] == ["QP's request rule: every eligible close",
                                      "QP's request rule: the reference's cadence (5.6)"]
    assert r["fm_menu_runs"] == ["DT-16-price", "DT-16-s", "FP-16-s", "LU-16-l", "QP-16-req", "QP-16-s", "TS-14",
                                 "TS-16"]
    assert r["fm_paired_more_measures"] >= 30 and r["fm_distribution_rows"] > 0 and r["fm_evenness_rows"] > 0
    assert r["fm_variance_rows"] > 0


def test_the_scorecard_stages_and_minors():
    r = found()
    assert r["sc_sections"] == ["diverge", "grid", "identity", "mechanics", "oracle", "paired", "scorecard"]
    assert r["sc_kinds"] == ["beside", "corner", "one_at_a_time", "reference"]   # the run's kind, not U1's
    assert r["sc_paired_months"] == [1, 2, 3, 6, 9, 12]
    assert r["sc_grid_prices"] == [float(p) for p in range(25, 251, 25)]
    assert r["sc_grid_P_falls_with_price"] == [2, True]
    assert r["sc_break_even"] == ["P", "S5a", "mean_net_month_3"]
    assert all("Lucid's price is verified; beside" in x for x in r["sc_break_even_lucid"])     # r3
    assert r["sc_a10_held"] == 2                                              # A-10's check, both arms
    assert r["items_4_5"]["starts_compared"] == 80 and r["items_4_5"]["trades"] > 0
    assert r["neg"]["delta_held"] is True and r["neg"]["delta_refused"] is True               # r6
    assert r["neg"]["capture"] == [1, True, True, True] and r["neg"]["captured_reproduces_the_arm"] is True
    assert r["neg"]["scorecard_stops_on_a_wrong_delta"] is True
    assert r["neg"]["stops_at_first_refusal"] is True                                         # r5
    assert r["neg"]["n4_refused"] is True and r["neg"]["n4_held"] is True
    assert r["ld_ran"] == {"ladder_replays": 27} and r["ld_item5"] > 0
    assert r["ld_responses"] == ["denial_10", "denial_25", "denial_50"]
    assert r["gt_ran"] == {"gates": 16} and r["gt_readings_qp"] == ["plan", "zero_edge"]
    assert r["gt_labels_fp"] == ["tier-1 liquidation not applied"]


def _cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(ROOT / "scripts" / "rd01_reading.py"), *args], capture_output=True,
                          text=True, timeout=300, env=ENV, cwd=str(ROOT))


def test_the_runner_refuses_before_any_read_without_the_identity_rows():
    led = ROOT / "results" / "read_ledger.jsonl"
    before = led.read_bytes() if led.is_file() else b""
    p = _cli()
    assert p.returncode == 3 and "REFUSED (RD-01 9.1, 15)" in p.stdout
    for task in ("Q-104", "Q-80", "Q-93"):
        assert f"no row carries a token for {task}" in p.stdout
    assert (led.read_bytes() if led.is_file() else b"") == before            # nothing ledgered: no read authorised
    p = _cli("--plan")
    assert p.returncode == 0 and "would run, in order: firm_scorecard, firm_ladder_beside, firm_gate_beside" in p.stdout
    assert "E-015's limits: none approved" in p.stdout and "the purposes' pre-check" in p.stdout
    assert "refused by the shared parser" not in p.stdout          # every covered path (E-113's cover) is at HEAD
    p = _cli("--purpose", "firm_scorecard")                                   # one run, the three purposes in order
    assert p.returncode == 2


# ------------------------------------------------------------------------------------------------ the third read


def test_g_one_pass_through_a9_is_the_two_pass_route_bit_for_bit():
    sp = found()["single_pass"]
    assert sorted(sp) == sorted(f"{r}|{a}" for r in ("TS-16", "DT-16-s", "FP-16-s", "QP-16-s")
                                for a in ("point", "verdict"))
    assert all(v == [True, True] for v in sp.values())          # outputs unchanged; ledger, counts, logs the same


def test_g_the_break_even_search_gives_the_plain_searchs_answers():
    r = found()
    for cell, by in r["break_even_same"].items():
        assert by and all(v[0] is True for v in by.values()), cell
    for nm, (same, mine, plain) in r["break_even_toy"].items():
        assert same is True and mine < plain, nm                   # the same price, fewer recompositions


def test_m1_s2_s3d_s6_and_q_as_user_milestones_defines_them():
    r = found()
    assert r["u1_lines"] == ["Q", "S2", "S3d", "S6"] and r["fr_u1_lines"] == ["Q", "S2", "S3d", "S6"]
    assert r["u1_keys"] == ["first_pass:days_p90", "first_pass:spent_before_p90", "first_payout:cash_p50",
                            "luck:monthly_mean_over_sd_p10", "luck:monthly_mean_over_sd_p50",
                            "luck:monthly_mean_over_sd_p90", "luck:net_mean", "luck:sd_net_across_starts",
                            "quit:q1_mean_net", "quit:q2_mean_net"]
    assert r["u1_years"] and r["u1_blocks"] == ["all", "early", "late"]
    assert r["u1_luck_runs"] == ["a", "all", "b"] and r["fr_u1_luck"] > 0
    assert r["fr_u1_paired"] == ["plan", "ts"]


def test_m2_m3_drained_only_open_the_ladders_control_and_the_years_on_u1s_months():
    r = found()
    g = r["g10"]
    assert (g["drained_open"], g["drained_ended"], g["drained_breached"]) == (1, 0, 0)
    assert g["idle_gaps"][0] < 31 <= g["idle_gaps"][1] and g["idle_at"] == [0, 1]       # n3: 30 days between
    assert r["uncapped_control"] == [0, 1]
    assert r["fr_months_ahead_u1"] is True and r["fm_year_measures"] == ["P"]


def test_m4_m5_the_twin_at_the_logs_fees_and_over_resolved_evaluations():
    r = found()
    assert r["twin_fees"][0] is not None and r["twin_fees"][1] is None
    assert r["twin_resolved"] == [0.5, 4.0, 2.0]


def test_m6_n5_the_menus_windows_on_start_positions():
    r = found()
    n_w, has_interval, cov, hole, zero_level, zero_paired = r["menu_windows"]
    assert n_w == 4.0 and has_interval is True and cov == 0.9
    assert hole == "a kept window holds no defined value: no interval"
    assert zero_level == "zero on every kept window" and zero_paired == "identical on these trades"
    assert r["coverage_settings"] == [[63, 5]]


def test_m7_and_d1_rows_spilled_and_the_identity_rows_without_the_token():
    r = found()
    assert r["spill_parts"] == 4
    rows, shas, heads, in_csv, in_manifest = r["fr_identity"]
    assert rows == ["E-000"] and shas == ["abab"] and heads == ["cdcd"]
    assert in_csv is False and in_manifest is False                  # the row, sha and HEAD; never the token


# ------------------------------------------------------------------------------------------------ the fourth read


def test_v1_the_references_reproduce_u1s_rows_on_the_readings_route():
    v1 = found()["v1"]
    assert v1 == {"held": 4, "planted_refused": True, "none_refused": True}


def test_v5_the_recorders_own_checks_refuse_and_hold_on_the_toys():
    r = found()
    assert r["v5"] == [1, True, 0]                    # a planted recorder problem stops the cell at its first start
    assert all(v == [True, True] for v in r["single_pass"].values())   # and none on the toys' own replays


def test_n4_a_missing_u1_key_refuses():
    assert found()["n4"] is True


def test_n2_v1_v3_the_identity_stage_runs_the_readings_route_and_times_it():
    r = found()
    assert r["identity_n2"] == {"n2 the reading's in-run refusals": [], "V1 TS on the reading's route": []}
    assert r["identity_timings"] == [20, True]          # 2 streams x 2 arms x 5 plans, each timed with its peak
