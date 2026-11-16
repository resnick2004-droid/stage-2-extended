"""Zero-edge contract arithmetic per plan (Q-12 part 3). Not a simulation; every input is a quoted term.

Bounds (vendor/stage2/vendor/propfirms/docs/T3_CEILINGS_DERIVATION.md section 1, stage one's method):
  evaluation  P(pass) <= Pbar = D / (G + D)            (per phase; a two-phase funnel multiplies)
  funded      E[gross payouts] <= min(C, K)            C = initial cushion to the floor, K = lifetime cap if any
  trader      E[trader payouts per funded account] <= s * min(C, K)   s = the highest split that can apply
  cost        E[fees per funded account] >= F / Pbar + A      F = one evaluation's fee (ONE month if monthly),
                                                              A = activation charged on a pass
  per fee $   E[trader payouts] / E[fees] per attempt <= s * min(C,K) * Pbar / (F + Pbar_A * A)
              (increasing in Pbar, so the Pbar bound keeps it an upper bound; Pbar_A = pass probability of the
              phase after which A is charged)
Usage: python -I arith.py  -> markdown table on stdout
"""
import sys

INF = float("inf")
# key, label, G, D, phases(list of (G,D)) or None, C, K, s_first, s_max, F, F_basis, A, A_after_phase, seats, src
ROWS = [
    ("topstep", "Topstep 50K Combine -> XFA, Standard path (reference)", [(3000, 2000)], 2000, INF, 0.90, 0.90, 49, "monthly", 149, 1, "5", "Stage 2 rules.yaml: combine_profit_target, combine_mll, xfa_mll_start, profit_split, subscription_fee, activation_fee, max_active_funded_accounts"),
    ("topstep_naf", "Topstep 50K, No Activation Fee path (reference)", [(3000, 2000)], 2000, INF, 0.90, 0.90, 95, "monthly", 0, 1, "5", "Stage 2 rules.yaml: subscription_fee note (14289835)"),
    ("lucid", "Lucid LucidFlex 50K", [(3000, 2000)], 2000, 5 * 2000, 0.90, 0.90, 165, "one-time (list; $115.50 with coupon, Stage 2 D-575)", 0, 1, "5", "lucid 12945790, 12945815, 12945795, 12945796, 11404617 (read today)"),
    ("alpha_adv", "Alpha Futures Advanced 50K", [(4000, 1750)], 1750, INF, 0.90, 0.90, 209, "monthly", 0, 1, "3", "alpha.terms"),
    ("alpha_std", "Alpha Futures Standard 50K", [(3000, 2000)], 2000, INF, 0.90, 0.90, 129, "monthly", 0, 1, "5", "alpha.terms_standard"),
    ("aqua_flex", "Aqua Futures Flex Daily Loss 50K", [(3000, 2000)], 2000, INF, 0.90, 0.90, 131, "one-time (promo status unstated)", 0, 1, "5", "aqua.terms_flex_daily_loss_50k"),
    ("aqua_daily", "Aqua Futures Daily 50K", [(3000, 2000)], 2000, INF, 0.90, 0.90, 113, "one-time (promo status unstated)", 0, 1, "5", "aqua.terms_daily_50k"),
    ("blusky", "BluSky Launch 50K (Evaluation, then Buffer)", [(3000, 2000), (3000, 2000)], 2900, 10000, 0.90, 0.90, 59, "monthly, evaluation phase only", 99, 1, "3", "blusky.terms"),
    ("daytraders", "DayTraders.com EOD 50K", [(3000, 2000)], 2000, INF, 1.00, 1.00, 105, "basis unstated (Monthly or Lifetime)", 5, 1, "5", "daytraders.terms"),
    ("e2t", "Earn2Trade Gauntlet Mini 50K -> LiveSim", [(3000, 2000)], 2000, 5000, 0.50, 0.80, 170, "monthly", 0, 1, "3", "e2t.terms ($139 activation is deducted from the first withdrawal: left out of F, so still a ceiling)"),
    ("ffn", "Funded Futures Network STEADY 50K", [(3000, 2000)], 2000, 3 * 1000 + 1250, 0.90, 0.90, 229, "one-time (list)", 0, 1, "5", "ffn.terms (split conflict: FAQ 80/20)"),
    ("fundednext", "FundedNext Futures Flex 50K", [(2500, 1500)], 1500, 5 * 1500, 0.95, 0.95, 141.99, "one-time (list; $74.99 with coupon)", 0, 1, "5", "fundednext.terms"),
    ("funderpro_beg", "FunderPro Futures Beginner 50K", [(3000, 2000)], 2000, INF, 0.80, 0.80, 79, "monthly", 0, 1, "5", "funderpro.terms_beginner"),
    ("funderpro_mid", "FunderPro Futures Mid-Level 50K", [(3000, 2000)], 2000, INF, 0.80, 0.90, 89, "monthly", 129, 1, "5", "funderpro.terms_midlevel"),
    ("fxify", "FXIFY Futures (Futureify) Flex 50K", [(3000, 1750)], 1750, INF, 0.90, 0.90, 179, "one-time (list)", 0, 1, "5 incl. evaluations", "fxify.terms"),
    ("mffu_reod", "My Funded Futures Rapid EOD 50K", [(3000, 2000)], 2000, INF, 0.90, 0.90, 275, "one-time (list; $165 with code)", 0, 1, "3", "mffu.terms"),
    ("mffu_pro", "My Funded Futures Pro 50K", [(3000, 2000)], 2000, INF, 0.80, 0.80, 265, "one-time (list; $159 with code)", 0, 1, "5 (25K/50K pool)", "mffu.terms_pro50k"),
    ("phidias_m", "Phidias Premium 50K, monthly path", [(4000, 2500)], 2500, INF, 0.75, 1.00, 329, "monthly", 149, 1, "5", "phidias.terms"),
    ("phidias_o", "Phidias Premium 50K, one-time path", [(4000, 2500)], 2500, INF, 0.75, 1.00, 723, "one-time", 0, 1, "5", "phidias.terms"),
    ("topone", "Top One Futures Elite Daily V2 50K", [(3000, 2000)], 2000, INF, 0.90, 0.90, 218, "conflict: monthly (help) vs one-time toggle (home)", 0, 1, "5 incl. evaluations", "topone.terms"),
    ("tradeday_fp", "TradeDay Fast Pass EOD 50K", [(3000, 2000)], 2000, 4 * 1500, 0.80, 0.80, 180, "one-time (help table; $99 sale card)", 0, 1, "5", "tradeday.terms_fast_pass_50k (K = 4 Sim payouts; the 5th request moves the account Live)"),
    ("tradeday_qp", "TradeDay Quick Pay EOD 50K", [(3000, 2000)], 2000, 10000, 0.50, 0.80, 175, "one-time (help table; $69 sale card)", 0, 1, "5", "tradeday.terms_quick_pay_eod_50k (funded drawdown intraday)"),
    ("tradeify", "Tradeify Select 50K (Flex path)", [(3000, 2000)], 2000, INF, 0.90, 0.90, 165, "one-time", 0, 1, "5", "tradeify.terms"),
    ("tradingpit", "The Trading Pit Futures Prime 50K", [(3000, 2000)], 2000, INF, 0.80, 0.80, 99, "one-time", 0, 1, "5", "tradingpit.terms (split 'up to 80%')"),
]


def fmt(x, nd=0):
    if x == INF:
        return "none"
    return f"{x:,.{nd}f}"


def main():
    out = []
    rows = []
    for (key, label, phases, C, K, s1, smax, F, Fb, A, A_after, seats, src) in ROWS:
        pbar = 1.0
        pA = None
        for i, (G, D) in enumerate(phases, 1):
            pbar *= D / (G + D)
            if i == A_after:
                pA = pbar
        m = min(C, K)
        value = smax * m
        cost = F / pbar + A * (pA / pbar)
        per_attempt = value * pbar
        fees_attempt = F + A * pA
        ratio = per_attempt / fees_attempt
        ratio2 = per_attempt / (2 * F + A * pA) if Fb.startswith("monthly") else None
        rows.append((ratio, ratio2, key, label, phases, pbar, C, K, m, s1, smax, value, F, Fb, A, cost, per_attempt, fees_attempt, seats, src))
    rows.sort(key=lambda r: -r[0])
    out.append("| rank | plan | G / D (eval) | Pbar = D/(G+D) | C | K | s (first / max) | funded value <= s*min(C,K) | F (basis) | A | fees per funded account >= F/Pbar + A | payouts per fee dollar <= | same, two monthly fees | seats |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for i, r in enumerate(rows, 1):
        (ratio, ratio2, key, label, phases, pbar, C, K, m, s1, smax, value, F, Fb, A, cost, pa, fa, seats, src) = r
        r2 = f"{ratio2:.2f}" if ratio2 is not None else "--"
        gd = " then ".join(f"{G:,} / {D:,}" for G, D in phases)
        out.append(f"| {i} | {label} | {gd} | {pbar:.3f} | {fmt(C)} | {fmt(K)} | {s1:.2f} / {smax:.2f} | {fmt(value)} | ${F:,.2f} ({Fb}) | {fmt(A)} | {fmt(cost)} | **{ratio:.2f}** | {r2} | {seats} |")
    out.append("")
    out.append("Sources of the inputs, per row: " + "; ".join(f"{r[3]}: {r[19]}" for r in rows) + ".")
    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(out))


main()
