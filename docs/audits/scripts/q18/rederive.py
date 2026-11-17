"""Independent audit of results/p14_validation.csv -- reads CSVs only, imports nothing of the repo or vendor code."""
import hashlib, json, math, sys
import numpy as np
import pandas as pd
from scipy import stats

ROOT = r"c:/Users/resni/OneDrive/Desktop/Stage 2 - Extended"
F = ROOT + "/results/p14_validation.csv"
REG = ROOT + "/vendor/stage2/results/a3_brk30_cb20_gate.csv"
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40); pd.set_option("display.max_rows", 400)

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

man = json.load(open(F + ".manifest.json"))
print("sha csv", sha(F), "manifest", man["sha256"], sha(F) == man["sha256"])
rman = json.load(open(REG + ".manifest.json"))
print("registered sha", sha(REG) == rman["sha256"])
d = pd.read_csv(F)
print("rows", len(d), "manifest rows", man["rows"], "cols equal", list(d.columns) == man["columns"])

# any date-like string from 2026-07-17 on?
import re
txt = open(F, encoding="utf-8").read()
dates = sorted(set(re.findall(r"20\d\d-\d\d-\d\d", txt)))
print("dates in csv", dates)

R = pd.read_csv(REG)
z = np.isclose(R["enforcement_p"].astype(float), 0.0)
rb = R[(R.section == "gate_at_ledger_n") & (R["shift"] == "lower_bound") & z]
rp = R[(R.section == "gate") & (R["shift"] == "point") & z]
r05b = R[(R.section == "gate") & (R["shift"] == "lower_bound") & z]
print("registered rows", len(rb), len(rp), len(r05b))
rb, rp, r05b = rb.iloc[0], rp.iloc[0], r05b.iloc[0]
READ = ["pf_growth_on_base_p50", "pf_required_p90", "pf_required_p50", "pf_required_p99", "mean_max_drawdown",
        "mean_combine_purchases"]
print("REGISTERED verdict arm:", {c: rb[c] for c in READ + ["mean_r_used", "median_payouts_per_path", "ruin_probability", "median_days_to_first_payout", "share_accounts_ever_paid"]})
print("REGISTERED point arm:", {c: rp[c] for c in READ + ["mean_r_used", "median_payouts_per_path", "ruin_probability", "median_days_to_first_payout"]})
print("REGISTERED 0.05 bound:", {c: r05b[c] for c in READ})

BOUND, POINT = "verdict (0.05/370)", "point"
ALLREAD = ["pf_growth_on_base_p50", "pf_required_p90", "pf_required_p50", "pf_required_p99", "v1_share_below_start",
           "mean_max_drawdown", "v1_payout_drought_p90", "v1_payouts_per_path_p50", "mean_combine_purchases"]

def check_rows(sub, name):
    bad = 0
    for _, r in sub.iterrows():
        ref = rb if r["arm"] == BOUND else rp
        for c in ALLREAD:
            v, g, df = r[c], r["registered_" + c], r["diff_" + c]
            if c in ref.index and not (pd.isna(g) and pd.isna(ref[c])) and not np.isclose(g, ref[c], rtol=0, atol=1e-9):
                print(f"  {name}: registered_{c} {g} != registered file {ref[c]}"); bad += 1
            if not (pd.isna(df) and (pd.isna(v) or pd.isna(g))) and not np.isclose(df, v - g, rtol=0, atol=1e-6):
                print(f"  {name}: diff_{c} {df} != {v}-{g}"); bad += 1
        ga = bool(np.isfinite(r["pf_growth_on_base_p50"]) and r["pf_growth_on_base_p50"] > 0)
        if bool(r["growth_above_zero"]) != ga:
            print(f"  {name}: growth_above_zero flag wrong"); bad += 1
    print(f"{name}: rows {len(sub)} consistency problems {bad}")

# ---------------- identity rows
print("\nIDENTITY rows")
for _, r in d[d.section.isin(["identity", "declaration"])].iterrows():
    print(" ", r["section"], r["holds"], str(r["check"])[:150])

# ---------------- A1
a1 = d[d.section == "a1"].copy()
check_rows(a1, "a1")
print(a1[["arm", "scheme", "mean_block", "control", "pf_growth_on_base_p50", "registered_pf_growth_on_base_p50",
          "diff_pf_growth_on_base_p50", "growth_se", "pf_required_p90", "diff_pf_required_p90", "required_p90_se",
          "growth_above_zero"]].to_string())
for _, r in a1.iterrows():
    if pd.notna(r["growth_se"]) and r["growth_se"] > 0:
        print(f"  {r['arm']:20s} {r['scheme']:32s} growth diff/SE {r['diff_pf_growth_on_base_p50']/r['growth_se']:+.2f}  "
              f"req90 diff/SE {r['diff_pf_required_p90']/r['required_p90_se']:+.2f}  rel growth {r['pf_growth_on_base_p50']/r['registered_pf_growth_on_base_p50']:.3f} rel req90 {r['pf_required_p90']/r['registered_pf_required_p90']:.3f}")
print(a1[["arm", "scheme"] + ["v1_share_below_start", "mean_max_drawdown", "v1_payout_drought_p90",
                              "v1_payouts_per_path_p50", "mean_combine_purchases", "pf_required_p50", "pf_required_p99",
                              "mean_r_used", "paths", "horizon_days", "v1_net_p10", "v1_net_p50",
                              "median_days_to_first_payout"]].to_string())
# registered row in a1 equals registered file
reg_a1 = a1[a1.scheme == "independent (registered)"]
for _, r in reg_a1.iterrows():
    ref = rb if r["arm"] == BOUND else rp
    print("  a1 registered row vs file:", {c: (r[c], ref[c]) for c in ["pf_growth_on_base_p50", "pf_required_p90", "mean_r_used", "mean_max_drawdown", "mean_combine_purchases"]})

# ---------------- B2
print("\nB2")
c = d[d.section == "b2_curve"].copy()
print(c[["scheme", "mean_block", "step", "shift_r", "bound_fresh_funded_r", "pf_growth_on_base_p50", "growth_above_zero",
         "pf_required_p90", "mean_r_used"]].to_string())
b2 = d[d.section == "b2"]
print(b2[["scheme", "mean_block", "registered_bound_fresh_funded_r", "break_even_e_fresh_funded_r", "bracketed",
          "break_even_shift", "margin", "margin_at_least", "steps_run", "first_step_at_or_below_zero"]].to_string())
for sch, g in c.groupby("scheme", sort=False):
    g = g.sort_values("step")
    shifts = g["shift_r"].to_numpy(float); gr = g["pf_growth_on_base_p50"].to_numpy(float)
    exp = np.array([-(0.02 * k) for k in g["step"]])
    print(f"  {sch}: shifts as declared {np.allclose(shifts, exp)}; steps {list(g['step'])}")
    reg_lb = b2[b2.scheme == sch]["registered_bound_fresh_funded_r"].iloc[0]
    print("   bound column = registered + shift:", np.allclose(g["bound_fresh_funded_r"], reg_lb + shifts))
    turned = next((i for i, x in enumerate(gr) if not (np.isfinite(x) and x > 0)), None)
    # stopping rule: stop one step after first growth <= 0, at most 8
    exp_steps = min(9, (turned + 1) if turned is not None else 9)
    print(f"   first non-positive index {turned}; steps run {len(gr)}, expected {exp_steps}")
    if turned is None:
        print(f"   my margin_at_least {-shifts[-1]:.4f}; bracketed False")
    else:
        s0, g0, s1, g1 = shifts[turned-1], gr[turned-1], shifts[turned], gr[turned]
        star = s0 + (s1 - s0) * g0 / (g0 - g1)
        print(f"   my break-even shift {star}, margin {-star}, e {reg_lb + star}")
    print("   growth monotone non-increasing:", bool(np.all(np.diff(gr) <= 0)), "growth at last step", gr[-1], "first", gr[0])
# step 0 equals registered / A1 21
i0 = c[(c.scheme == "independent") & (c.step == 0)].iloc[0]
print("  B2 indep step0 growth", i0["pf_growth_on_base_p50"], "registered", rb["pf_growth_on_base_p50"])
s0 = c[(c.scheme != "independent") & (c.step == 0)].iloc[0]
a21 = a1[(a1.arm == BOUND) & (a1.mean_block == 21)].iloc[0]
print("  B2 stat step0 growth", s0["pf_growth_on_base_p50"], "A1 block21 bound", a21["pf_growth_on_base_p50"])
print("  registered fresh-funded bound in registered edge rows:")
er = R[R.section == "edge"][["rr", "e", "lb", "lb_at_ledger_n", "lb_gate", "lb_gate_at_ledger_n", "n"]]
print(er.to_string())

# ---------------- A0
print("\nA0")
a0 = d[d.section == "a0"]
for _, r in a0.iterrows():
    n = int(r["n"])
    acfs = np.array([r[f"acf_{k}"] for k in range(1, 22)])
    band = r["white_noise_band"]
    print(f"  {r['series']}: n {n}, band {band} (1.96/sqrt(n) = {1.96/math.sqrt(n):.6f}), lags outside band "
          f"{[k+1 for k in range(21) if abs(acfs[k]) > band]}, acf1 {acfs[0]:.4f}")
    for L in (5, 10, 21):
        q = n * (n + 2) * sum(acfs[k] ** 2 / (n - k - 1) for k in range(L))
        p = stats.chi2.sf(r[f"ljung_box_q_{L}"], L)
        print(f"    LB{L}: Q reported {r[f'ljung_box_q_{L}']:.4f}, mine from acf {q:.4f}; p reported {r[f'ljung_box_p_{L}']:.4g}, mine {p:.4g}")
    print(f"    PW b_sb {r['pw_b_sb']}, auto_block {r['auto_block']}, ceil {math.ceil(r['pw_b_sb']) if pd.notna(r['pw_b_sb']) else None}")
    if pd.notna(r.get("runs_n")):
        n1, n2, rr_ = r["runs_positive"], r["runs_negative"], r["runs_runs"]
        mu = 2 * n1 * n2 / (n1 + n2) + 1
        var = 2 * n1 * n2 * (2 * n1 * n2 - n1 - n2) / ((n1 + n2) ** 2 * (n1 + n2 - 1))
        zz = (rr_ - mu) / math.sqrt(var)
        print(f"    runs: n {r['runs_n']} zeros {r['runs_zeros']} +{n1} -{n2} runs {rr_}; expected {r['runs_expected']} mine {mu:.4f}; z {r['runs_z']} mine {zz:.4f}; p {r['runs_p']} mine {2*stats.norm.sf(abs(zz)):.4g}")
    print(f"    rr {r['rr']}, days {r['days']}")

# ---------------- B1
print("\nB1")
b1 = d[d.section == "b1"].copy()
print("  blocks", sorted(b1.mean_block.unique()), "rules", b1.rule.unique(), "levels", b1.level.unique(), "rr", sorted(b1.rr.unique()))
print("  replicates+undefined", (b1.replicates + b1.undefined).unique())
bad = 0
for _, r in b1.iterrows():
    k, n = int(r["exceed"]), int(r["replicates"])
    a = 0.05 if r["level"] == "0.05" else 0.05 / 370
    lo = 0.0 if k == 0 else stats.beta.ppf(0.025, k, n - k + 1)
    hi = 1.0 if k == n else stats.beta.ppf(0.975, k + 1, n - k)
    ok = (np.isclose(r["nominal"], a) and np.isclose(r["share_exceed"], k / n) and np.isclose(r["share_lo"], lo)
          and np.isclose(r["share_hi"], hi) and np.isclose(r["ratio_to_nominal"], k / n / a)
          and bool(r["nominal_inside_interval"]) == bool(lo <= a <= hi)
          and bool(r["verdict_level"]) == (r["level"] != "0.05"))
    if not ok:
        bad += 1; print("   bad", r[["rule", "mean_block", "rr", "level", "exceed", "replicates"]].to_dict())
print("  B1 arithmetic problems", bad)
# truth equals registered e
em = R[R.section == "edge"].set_index("rr")["e"]
print("  truth == registered e:", all(np.isclose(r["truth"], em[float(r["rr"])]) for _, r in b1.iterrows()))
print("  auto block flag", b1[b1.block_is_auto].mean_block.unique())
pv = b1.pivot_table(index=["rule", "level", "mean_block"], columns="rr", values="share_exceed")
print(pv.to_string())
pv2 = b1.pivot_table(index=["rule", "level", "mean_block"], columns="rr", values="ratio_to_nominal")
print(pv2.round(3).to_string())
print(b1.groupby(["rule", "level"]).agg(exceed_total=("exceed", "sum"), nominal_inside=("nominal_inside_interval", "mean"), max_ratio=("ratio_to_nominal", "max"), min_ratio=("ratio_to_nominal", "min")).to_string())
leg = b1[b1.leg.notna()][["rule", "level", "mean_block", "rr", "leg", "exceed", "replicates", "share_exceed", "share_lo", "share_hi", "ratio_to_nominal", "nominal_inside_interval", "truth", "mean_bound", "truth_lower_era", "share_exceed_lower_era"]]
print(leg.to_string())

# ---------------- C1
print("\nC1")
c1 = d[d.section == "c1"].copy()
check_rows(c1, "c1")
print(c1[["arm", "scheme", "realisation", "realisation_seed", "trades_offered", "trades_left", "sessions_missed",
          "pf_growth_on_base_p50", "diff_pf_growth_on_base_p50", "pf_required_p90", "growth_above_zero"]].to_string())
for (sch,), g in c1.groupby(["scheme"]):
    tl = g.trades_left.iloc[0]
    print(f"  {sch}: share trades left {g.trades_left.unique()/g.trades_offered.iloc[0]}, sessions missed {g.sessions_missed.unique()} of 1691 = {g.sessions_missed.unique()/1691}")
cs = d[d.section == "c1_summary"]
bad = 0
for _, s in cs.iterrows():
    g = c1[(c1.scheme == s["scheme"]) & (c1.arm == s["arm"])]
    if len(g) != 3: bad += 1
    if not np.isclose(s["share_realisations_growth_above_zero"], g.growth_above_zero.astype(bool).mean()): bad += 1
    for col in ALLREAD + ["trades_left", "sessions_missed"]:
        v = g[col].astype(float)
        for k, x in (("mean", v.mean()), ("min", v.min()), ("max", v.max()), ("range", v.max() - v.min())):
            if not np.isclose(s[f"{col}_{k}"], x, rtol=1e-12, atol=1e-9):
                bad += 1; print("   bad", s["scheme"], s["arm"], col, k, s[f"{col}_{k}"], x)
print("  c1_summary problems", bad)
print(cs[["arm", "scheme", "realisations", "share_realisations_growth_above_zero", "pf_growth_on_base_p50_mean",
          "pf_growth_on_base_p50_min", "pf_growth_on_base_p50_max", "pf_required_p90_mean"]].to_string())
for _, s in cs.iterrows():
    ref = rb if s["arm"] == BOUND else rp
    print(f"  {s['arm']:20s} {s['scheme']:10s} growth min/registered {s['pf_growth_on_base_p50_min']/ref['pf_growth_on_base_p50']:.3f}  mean/reg {s['pf_growth_on_base_p50_mean']/ref['pf_growth_on_base_p50']:.3f}  req90 mean/reg {s['pf_required_p90_mean']/ref['pf_required_p90']:.3f}")
# seeds distinct
print("  realisation seeds distinct:", c1.realisation_seed.nunique(), "of", c1.drop_duplicates(["scheme", "realisation"]).shape[0])

# ---------------- SLIP
print("\nSLIP")
sl = d[d.section == "slip"].copy()
check_rows(sl, "slip")
print(sl[["arm", "scheme", "family", "level", "entry_slip_ticks", "stop_slip_ticks", "flatten_slip_ticks",
          "target_slip_ticks", "added_ticks_s", "added_ticks_t", "added_ticks_f", "added_ticks_b", "e_fresh_funded_r",
          "bound_fresh_funded_r", "e_fresh_combine_r", "bound_fresh_combine_r", "era_flagged"]].to_string())
print(sl[["arm", "scheme", "pf_growth_on_base_p50", "diff_pf_growth_on_base_p50", "pf_required_p90", "growth_above_zero", "mean_r_used", "v1_share_below_start", "mean_max_drawdown"]].to_string())
# declared D-583 arms
decl = {"base": (1, 1, 2), "A_stop2": (1, 2, 3), "A_stop3": (1, 3, 4), "A_stop5": (1, 5, 6), "A_stop8": (1, 8, 9),
        "A_stop12": (1, 12, 13), "B_slip2": (2, 2, 3), "B_slip3": (3, 3, 4), "B_slip5": (5, 5, 6)}
for _, r in sl[sl.arm == BOUND].iterrows():
    e, s_, f = decl[r["scheme"]]
    ok = (r.entry_slip_ticks, r.stop_slip_ticks, r.flatten_slip_ticks, r.target_slip_ticks) == (e, s_, f, 0)
    print(f"  {r['scheme']}: ticks as D-583 {ok}")
srd = d[d.section == "slip_reading"]
print(srd[["arm", "family", "levels", "arms_read", "lowest_level_growth_at_bound_at_or_below_zero"]].to_string())
for fam in ("A", "B"):
    g = sl[(sl.arm == BOUND) & ((sl.family == fam) | (sl.scheme == "base"))].sort_values("level")
    low = next((int(r.level) for _, r in g.iterrows() if not r.growth_above_zero), "none")
    print(f"  my lowest level family {fam}: {low}; levels {list(g.level)}")
base = sl[(sl.scheme == "base")]
for _, r in base.iterrows():
    ref = rb if r["arm"] == BOUND else rp
    print("  base arm == registered:", r["arm"], np.isclose(r["pf_growth_on_base_p50"], ref["pf_growth_on_base_p50"]), r["e_fresh_funded_r"], r["bound_fresh_funded_r"])

# ---------------- headline candidates
print("\nHEADLINES")
allg = d[d.section.isin(["a1", "c1", "slip", "b2_curve"])]
for arm in (BOUND, POINT):
    g = allg[allg.arm == arm]
    print(f"  {arm}: min growth over a1/c1/slip/b2 rows {g.pf_growth_on_base_p50.min()} ; rows with growth<=0: {int((~g.growth_above_zero.astype(bool)).sum())} of {len(g)}")
    for sec in ("a1", "c1", "slip", "b2_curve"):
        gg = g[g.section == sec]
        if len(gg):
            print(f"     {sec}: n {len(gg)} min growth {gg.pf_growth_on_base_p50.min():.6g} max req90 {gg.pf_required_p90.max():.6g}  max share_below_start {gg.v1_share_below_start.max():.4g}")
nd = d[d.section == "not_done"]
print(nd["note"].tolist())
