"""Independent audit of Q-83's five result files (E-052's fresh-seed validation). Reads the CSVs and manifests (and
Q-55's calibration_lift.csv for comparison); imports nothing from the repository or the vendored engine."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

R = Path(r"C:/Users/resni/OneDrive/Desktop/Stage 2 - Extended/results")
FILES = ("q82_validation_one_sample", "q82_validation_two_sample", "q82_count_persistent", "q82_criterion",
         "q82_judged_sessions")
KS = [11, 12, 13, 14, 15]
lev = lambda k: 0.05 / (k * (k + 1))  # noqa: E731
OUT = []


def say(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


def cp(k, n):
    lo = 0.0 if k <= 0 else float(stats.beta.ppf(0.025, k, n - k + 1))
    hi = 1.0 if k >= n else float(stats.beta.ppf(0.975, k + 1, n - k))
    return lo, hi


D, M = {}, {}
for f in FILES:
    m = json.loads((R / f"{f}.csv.manifest.json").read_text(encoding="utf-8"))
    b = (R / f"{f}.csv").read_bytes()
    D[f] = pd.read_csv(R / f"{f}.csv", low_memory=False)
    M[f] = m
    say(f"MANIFEST {f}: sha256 {'MATCH' if hashlib.sha256(b).hexdigest() == m['sha256'] else 'MISMATCH'}; rows "
        f"{len(D[f])}/{m['rows']}; commit {m['git_commit']} dirty {m.get('git_dirty')}; exploratory {m['exploratory']}; "
        f"seed and parameters.seeds all inside parameters.seed_block (E-052's block; values not printed, so this output "
        f"names none of them): {all(int(v) in set(m['parameters']['seed_block']) for v in ([m['seed']] if m['seed'] is not None else []) + list((m['parameters'].get('seeds') or {}).values()))}")
one, two, cpn, crit, js = (D[f] for f in FILES)

# ------------------------------------------------------------------ arithmetic on every size row
for name, df in (("one_sample", one), ("two_sample", two), ("count_persistent", cpn)):
    bad = cib = flag = kb = 0
    for r in df.itertuples():
        k, n, a = int(r.rejections), int(r.reps), float(r.level)
        if abs(r.rate - k / n) > 1e-15 or abs(r.ratio - (k / n) / a) > 1e-9 * max(1.0, r.ratio):
            bad += 1
        lo, hi = cp(k, n)
        if abs(lo - r.ci_lo) > 1e-12 or abs(hi - r.ci_hi) > 1e-12:
            cib += 1
        if bool(str(r.above_nominal).lower() == "true") != (lo > a):
            flag += 1
        if pd.notna(r.k) and abs(lev(int(r.k)) - a) > 1e-15:
            kb += 1
    say(f"ARITH {name}: {len(df)} rows; rate/ratio mismatches {bad}; CP mismatches {cib}; above_nominal flag mismatches "
        f"{flag}; k-level mismatches {kb}; reps {sorted(df['reps'].unique())}; methods {sorted(df['method'].unique())}")

# ------------------------------------------------------------------ (1) the verdicts, re-derived
inc = lambda df: df[df["in_criterion"].astype(str).str.lower() == "true"]  # noqa: E731
size = pd.concat([inc(one), inc(two)], ignore_index=True)
size = size[size["method"] == "cons"]
rows = []
for fn, exp in (("bound", 95), ("two_sample_bound", 56), ("placebo_selection_bound", 55)):
    g = size[size["function"] == fn]
    per = []
    for k in KS:
        gk = g[g["k"] == k]
        a = lev(k)
        lo = np.array([cp(int(x), int(y))[0] for x, y in zip(gk["rejections"], gk["reps"])])
        above = gk[lo > a]
        point = int((gk["rejections"] / gk["reps"] > a).sum())
        per.append(len(above))
        rows.append({"function": fn, "k": k, "nulls": gk["null"].nunique(), "expected": exp, "ci_wholly_above": len(above),
                     "point_above": point, "above": ";".join(above["null"])})
    verdict = "NOT CHECKED" if any(r["nulls"] != exp for r in rows if r["function"] == fn) else (
        "FAILS" if sum(per) else "HOLDS")
    say(f"VERDICT (mine) {fn}: {verdict}")
pin = pd.DataFrame(rows)
with pd.option_context("display.width", 250, "display.max_colwidth", 120):
    say(pin.to_string(index=False))
c = crit[(crit["section"] == "criterion") & (crit["k"].astype(str) == "11-15")]
say("VERDICT (q82_criterion.csv, k = 11-15):", dict(zip(c["statistic"], c["verdict"])))
cc = crit[(crit["section"] == "criterion") & (crit["k"].astype(str) != "11-15")]
mine = {(r["function"], r["k"]): r["ci_wholly_above"] for r in rows}
mism = [(r.statistic, r.k) for r in cc.itertuples() if int(r.nulls_above) != mine[(r.statistic, int(r.k))]]
say(f"criterion rows per k: nulls_above agrees with mine on {len(cc) - len(mism)} of {len(cc)}; mismatches {mism}")

# ------------------------------------------------------------------ (2) the failure, diagnosed
o = inc(one)
oc = o[(o["method"] == "cons") & o["k"].isin(KS)].copy()
oc["lo"] = [cp(int(x), int(y))[0] for x, y in zip(oc["rejections"], oc["reps"])]
fail = oc[oc["lo"] > oc["level"]]
say(f"FAILING cons rows (CI wholly above nominal), of {len(oc)} null x k cells ({oc['null'].nunique()} nulls x 5 k):")
for r in fail.itertuples():
    say(f"  line {r.Index + 2}: {r.null} group={r.group} stream={r.stream} value={r.value} side={r.side} L={r.L} "
        f"model={r.model} size={r.size} k={int(r.k)}: {int(r.rejections)}/{int(r.reps)} ratio {r.ratio:.3f} "
        f"ci_lo/level {r.lo / r.level:.3f} trades_mean {r.trades_mean}")
pt = oc[oc["rejections"] / oc["reps"] > oc["level"]]
say(f"point above nominal: {len(pt)} cells on {pt['null'].nunique()} nulls: "
    + "; ".join(f"{n} k{sorted(int(x) for x in g['k'])}" for n, g in pt.groupby("null")))
# members on the failing nulls
fn_nulls = sorted(set(fail["null"]))
memb = o[o["null"].isin(fn_nulls) & o["k"].isin(KS)].pivot_table(index=["null", "k"], columns="method",
                                                                     values="ratio", aggfunc="first")
with pd.option_context("display.width", 250):
    say("Q-83 ratios on the failing nulls (members and cons):\n" + memb.round(3).to_string())

# Q-55's rows for the same nulls (Q-16's draws)
q55 = pd.read_csv(R / "calibration_lift.csv", low_memory=False)
q55 = q55[(q55["section"] == "size") & q55["k"].isin(KS)]
m55 = q55[q55["null"].isin(fn_nulls)].pivot_table(index=["null", "k"], columns="method", values="ratio",
                                                   aggfunc="first")[["t21w", "t42w", "t63w", "cons"]]
r55 = q55[q55["null"].isin(fn_nulls) & (q55["method"] == "cons")][["null", "k", "rejections", "reps", "ratio", "ci_hi"]]
with pd.option_context("display.width", 250):
    say("Q-55 (Q-16's draws) ratios on the same nulls:\n" + m55.round(3).to_string())
    say("Q-55 cons rows on the same nulls (ci_hi / level beside):\n" + r55.assign(
        hi_over_level=r55["ci_hi"] / r55["k"].map(lev)).to_string(index=False))

# null by null, k = 11: Q-83 against Q-55, by construction group
a = oc[oc["k"] == 11].set_index("null")[["rejections", "reps", "group", "stream", "model", "size", "value", "side"]]
b = q55[(q55["method"] == "cons") & (q55["k"] == 11)].set_index("null")[["rejections", "reps"]]
j = a.join(b, rsuffix="_55", how="left")
say(f"nulls in Q-83's criterion matched in Q-55: {int(j['rejections_55'].notna().sum())} of {len(j)}")
# conditional test of equal rates (same reps): K83 | K83 + K55 ~ Binomial(K83 + K55, 1/2)
def p_two(k1, k2):
    n = int(k1 + k2)
    if n == 0:
        return 1.0
    return float(min(1.0, 2 * min(stats.binom.cdf(k1, n, 0.5), stats.binom.sf(k1 - 1, n, 0.5))))
j["p_equal"] = [p_two(int(x), int(y)) for x, y in zip(j["rejections"], j["rejections_55"])]
j["kind"] = np.where(j["group"] != "real", "synthetic (fresh draws of the same process)",
                     np.where(j["stream"].isin(["offered", "taken"]), "real, same trades (fresh flips only)",
                              "real, thinN (a fresh subset of trades)"))
for kind, g in j.groupby("kind"):
    say(f"k=11 {kind}: nulls {len(g)}; total cons rejections Q-83 {int(g['rejections'].sum())} vs Q-55 "
        f"{int(g['rejections_55'].sum())}; nulls with equal-rate p < 0.01: {int((g['p_equal'] < 0.01).sum())} "
        f"({', '.join(g.index[g['p_equal'] < 0.01])})")
say("k=11 thinN nulls, Q-83 vs Q-55 cons rejections (of 200,000):")
for n_, r in j[j["kind"].str.startswith("real, thinN")].iterrows():
    if r["p_equal"] < 0.01 or n_ in fn_nulls:
        say(f"  {n_}: Q-83 {int(r['rejections'])}, Q-55 {int(r['rejections_55'])}, p {r['p_equal']:.2g}")

# the count against what cons's measured conservatism implies
def p_lo_above(p, n, a):
    """P(Clopper-Pearson lower bound > a) when the true rate is p: P(K >= k*), k* the smallest k with lo(k) > a."""
    ks = np.arange(0, 2000)
    lo = stats.beta.ppf(0.025, np.maximum(ks, 1), n - ks + 1)
    lo[0] = 0.0
    kstar = int(ks[np.argmax(lo > a)])
    return float(stats.binom.sf(kstar - 1, n, p)), kstar
tot_nom, tot_55, tot_55u = 0.0, 0.0, 0.0
for k in KS:
    a = lev(k)
    pn, kstar = p_lo_above(a, 200000, a)
    tot_nom += pn * oc[oc["k"] == k]["null"].nunique()
    say(f"k={k}: the CI is wholly above nominal from {kstar} rejections of 200,000; at a true rate exactly nominal "
        f"P = {pn:.4f} per null")
    g55 = q55[(q55["method"] == "cons") & (q55["k"] == k) & q55["null"].isin(oc["null"])]
    for rr in g55.itertuples():
        tot_55 += p_lo_above(rr.rejections / rr.reps, 200000, a)[0]
        tot_55u += p_lo_above(max(rr.ci_hi, 1e-12), 200000, a)[0]
say(f"expected number of null x k cells with the CI wholly above, of {len(oc)}: at exactly nominal {tot_nom:.2f}; "
    f"at Q-55's measured cons rates {tot_55:.3f}; at Q-55's upper 95 % limits {tot_55u:.3f}; observed {len(fail)} "
    f"(on {fail['null'].nunique()} nulls)")
# the members' and cons's mean ratio at k = 11 across the 95 nulls, Q-83 vs Q-55
for mth in ("t21w", "t42w", "t63w", "cons"):
    x = o[(o["method"] == mth) & (o["k"] == 11)]["ratio"]
    y = q55[(q55["method"] == mth) & (q55["k"] == 11) & q55["null"].isin(o["null"])]["ratio"]
    say(f"mean ratio at k=11 over the 95 criterion nulls, {mth}: Q-83 {x.mean():.3f}, Q-55 {y.mean():.3f}")
# the subsets: trades per replication on thinN in Q-83
tm = o[o["stream"].astype(str).str.startswith("thin")].groupby("stream")["trades_mean"].agg(["min", "max"])
say("Q-83 thinN trades per replication:", tm.to_dict("index"))
say("entropy of the failing nulls (seed shown as its seed_map key):",
    [(r.null, "lift_real" if json.loads(r.entropy)[0] == M["q82_validation_one_sample"]["parameters"]["seed_map"]["lift_real"]
      else "other", json.loads(r.entropy)[1]) for r in fail[["null", "entropy"]].drop_duplicates().itertuples()])

# two-sample: worst rows
t = inc(two)
t = t[(t["method"] == "cons") & t["k"].isin(KS)]
for fn in ("two_sample_bound", "placebo_selection_bound"):
    g = t[t["function"] == fn]
    i = g["ratio"].idxmax()
    say(f"{fn}: worst cons row line {i + 2}: {g.loc[i, 'null']} k={int(g.loc[i, 'k'])} {int(g.loc[i, 'rejections'])}/"
        f"{int(g.loc[i, 'reps'])} ratio {g.loc[i, 'ratio']:.3f}; point above nominal: "
        f"{int((g['rejections'] / g['reps'] > g['level']).sum())} cells")

# beside: the count-persistent nulls (no verdict)
cpc = cpn[(cpn["method"] == "cons") & cpn["k"].isin(KS)].copy()
cpc["lo"] = [cp(int(x), int(y))[0] for x, y in zip(cpc["rejections"], cpc["reps"])]
for (fn, grp), g in cpc.groupby(["function", "group"]):
    ab = g[g["lo"] > g["level"]]
    say(f"BESIDE {fn} / {grp}: {g['null'].nunique()} nulls; cells with CI wholly above {len(ab)} on "
        f"{ab['null'].nunique()} nulls; max ratio {g['ratio'].max():.3f} ({g.loc[g['ratio'].idxmax(), 'null']}, k="
        f"{int(g.loc[g['ratio'].idxmax(), 'k'])})")

# ------------------------------------------------------------------ (3) the judged session list
p = M["q82_judged_sessions"]["parameters"]
dates = js["date"].astype(str).tolist()
h = hashlib.sha256("\n".join(dates).encode("utf-8")).hexdigest()
say(f"JUDGED: rows {len(js)}; columns {list(js.columns)}; first {dates[0]} last {dates[-1]}; sorted "
    f"{dates == sorted(dates)}; unique {len(set(dates)) == len(dates)}; ordinals 0..n-1 "
    f"{js.iloc[:, 0].tolist() == list(range(len(js)))}; my sha256 of the dates joined by LF {h}")
say("JUDGED manifest parameters:", {k: v for k, v in p.items() if any(s in k for s in ("session", "sha", "count", "judged",
                                                                                       "calendar", "n_"))})
Path(__file__).with_name("q83_audit_out.txt").write_text("\n".join(OUT), encoding="utf-8")
