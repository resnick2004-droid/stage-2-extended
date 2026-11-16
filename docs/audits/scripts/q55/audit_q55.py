"""Independent audit of Q-55's five result files. Reads the CSVs (and the Q-16 note's text for comparison) only;
imports nothing from the repository or the vendored engine."""
import hashlib
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

R = Path(r"C:/Users/resni/OneDrive/Desktop/Stage 2 - Extended/results")
NOTE = Path(r"C:/Users/resni/OneDrive/Desktop/Stage 2 - Extended/docs/research/calibration_2026-11-15.md")
FILES = ("calibration_lift", "calibration_p", "calibration_two_sample", "calibration_power", "bm63c_table")
KS = [11, 12, 13, 14, 15]


def lev(k):
    return 0.05 / (k * (k + 1))


out = []


def say(*a):
    s = " ".join(str(x) for x in a)
    out.append(s)
    print(s)


# ------------------------------------------------------------------ 1. manifests
D = {}
for f in FILES:
    p = R / f"{f}.csv"
    man = json.loads((R / f"{f}.csv.manifest.json").read_text(encoding="utf-8"))
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    df = pd.read_csv(p, low_memory=False)
    D[f] = df
    say(f"MANIFEST {f}: sha256 {'MATCH' if h == man['sha256'] else 'MISMATCH'}; rows {len(df)} vs {man['rows']}; "
        f"columns {'MATCH' if list(df.columns) == man['columns'] else 'MISMATCH'}; commit {man['git_commit']}; "
        f"exploratory {man['exploratory']}; seed {man['seed']}; prereg {man['prereg_id']}; ts {man['timestamp']}")

L, P, T, W, B = (D[f] for f in FILES)

# ------------------------------------------------------------------ 2. arithmetic per row
def cp(k, n):
    lo = 0.0 if k <= 0 else stats.beta.ppf(0.025, k, n - k + 1)
    hi = 1.0 if k >= n else stats.beta.ppf(0.975, k + 1, n - k)
    return lo, hi


def arith(df, name):
    d = df[df["rejections"].notna()].copy()
    bad = 0
    kbad = 0
    cibad = 0
    for _, r in d.iterrows():
        k, n, a = int(r["rejections"]), int(r["reps"]), float(r["level"])
        if abs(r["rate"] - k / n) > 1e-15 or abs(r["ratio"] - (k / n) / a) > 1e-9 * max(1, r["ratio"]):
            bad += 1
        if pd.notna(r["k"]):
            if abs(lev(int(r["k"])) - a) > 1e-15:
                kbad += 1
        else:
            if any(abs(lev(kk) - a) < 1e-15 for kk in KS):
                kbad += 1
        lo, hi = cp(k, n)
        if abs(lo - r["ci_lo"]) > 1e-12 or abs(hi - r["ci_hi"]) > 1e-12:
            cibad += 1
    levels = sorted(d["level"].unique())
    say(f"ARITH {name}: {len(d)} rows; rate/ratio mismatches {bad}; k-level mismatches {kbad}; "
        f"Clopper-Pearson mismatches {cibad}; levels {len(levels)}: "
        + ", ".join(f"{x:.6g}" for x in levels))


arith(L[L["section"] == "size"], "lift size")
arith(L[L["section"] == "boot"], "lift boot")
arith(P, "p size")
arith(T, "two_sample size")

# ------------------------------------------------------------------ 3. structure
ls = L[L["section"] == "size"]
real = ls["null"].str.startswith("real:")
STRESS = ("syn:cluster_ar5:", "syn:regime03:", "syn:regime10:", "syn:skew:")
stress = ls["null"].str.startswith(STRESS)
syn = ls["null"].str.startswith("syn:") & ~stress
say(f"STRUCT lift: real nulls {ls[real]['null'].nunique()}, realistic synthetic {ls[syn]['null'].nunique()} "
    f"({sorted(set(x.split(':')[1] for x in ls[syn]['null']))}), stress {ls[stress]['null'].nunique()} "
    f"({sorted(set(x.split(':')[1] for x in ls[stress]['null']))}); methods {sorted(ls['method'].unique())}; "
    f"reps {sorted(ls['reps'].unique())}")
lb = L[L["section"] == "boot"]
say(f"STRUCT boot: nulls {lb['null'].nunique()}, methods {sorted(lb['method'].unique())}, reps {sorted(lb['reps'].unique())}, "
    f"draws {sorted(lb['draws'].unique())}")
# trades per replication on the real streams: fixed by construction (a sign flip keeps the counts)
tm = ls[real].assign(stream=ls[real]["null"].str.split(":").str[1]).groupby("stream")["trades_mean"].agg(["min", "max"])
say("STRUCT real streams' trades per replication (min, max):", tm.to_dict("index"))
say(f"STRUCT p: nulls {P['null'].nunique()} (real {P[P['null'].str.startswith('real:')]['null'].nunique()}, syn "
    f"{P[P['null'].str.startswith('syn:')]['null'].nunique()}); methods {sorted(P['method'].unique())}; reps by method "
    + str(P.groupby('method')['reps'].unique().apply(lambda x: sorted(int(v) for v in x)).to_dict())
    + f"; stage values {P['stage'].dropna().unique().tolist()} on methods {sorted(P[P['stage'].notna()]['method'].unique())}")
for rule in ("treated", "all"):
    t = T[T["df_rule"] == rule]
    say(f"STRUCT two_sample {rule}: forms " + str(t.groupby("form")["null"].nunique().to_dict())
        + f"; methods {sorted(t['method'].unique())}; reps {sorted(t['reps'].unique())}")
say("STRUCT power rows by part/df_rule/form: "
    + str(W.fillna({"df_rule": "-", "form": "-"}).groupby(["part", "df_rule", "form"]).size().to_dict()))
say(f"STRUCT bm63c_table: {len(B)} rows; calibration_nulls {B['calibration_nulls'].unique().tolist()}; reps_each "
    f"{B['reps_each'].unique().tolist()}")

# ------------------------------------------------------------------ 4. invariants
def inv_cons(df, name, members, cname, keys):
    d = df[df["rejections"].notna()]
    piv = d.pivot_table(index=keys, columns="method", values="rejections", aggfunc="first")
    m = piv[list(members)].min(axis=1)
    viol = int((piv[cname] > m).sum())
    say(f"INVARIANT {name}: {cname} rejections <= min({','.join(members)}) on the same replications: "
        f"{len(piv)} null x level cells, violations {viol}")


inv_cons(ls, "lift", ("t21w", "t42w", "t63w"), "cons", ["null", "level"])
for rule in ("treated", "all"):
    inv_cons(T[T["df_rule"] == rule], f"two_sample {rule}", ("t21w", "t42w", "t63w"), "cons", ["null", "level"])
inv_cons(P, "p", ("bm63", "obm126", "ft63"), "pcons", ["null", "level"])


def inv_mono(df, name, keys):
    d = df[df["rejections"].notna()].sort_values("level")
    v = 0
    n = 0
    for _, g in d.groupby(keys):
        x = g["rejections"].to_numpy()
        n += 1
        if np.any(np.diff(x) < 0):
            v += 1
    say(f"INVARIANT {name}: rejections non-decreasing in the level: {n} null x method series, violations {v}")


inv_mono(ls, "lift", ["null", "method"])
inv_mono(lb, "boot", ["null", "method"])
inv_mono(P, "p", ["null", "method"])
inv_mono(T, "two_sample", ["df_rule", "null", "method"])

# power: lift cons mdl80 >= every member's; k = 15 >= k = 11
wl = W[W["part"] == "lift"]
pv = wl.pivot_table(index=["null", "level"], columns="method", values="mdl80", aggfunc="first")
v = int((pv["cons"] < pv[["t21w", "t42w", "t63w"]].max(axis=1) - 1e-12).sum())
say(f"INVARIANT lift power: cons mdl80 >= max(member mdl80): {len(pv)} cells, violations {v}")
pv = wl.pivot_table(index=["null", "method"], columns="k", values="mdl80", aggfunc="first")
say(f"INVARIANT lift power: mdl80 at k=15 >= k=11: {len(pv)} cells, violations {int((pv[15.0] < pv[11.0] - 1e-12).sum())}")
say(f"INVARIANT lift power: mdl80 >= mdl50: violations {int((wl['mdl80'] < wl['mdl50'] - 1e-12).sum())} of {len(wl)}")
ws = W[(W["part"] == "two_sample") & (W["form"] == "placebo-selection")]
chk = ws[ws["shift80"].notna()]
say(f"INVARIANT selection power: difference80 = shift80 x (1 - selected share): "
    f"{int((abs(chk['difference80'] - chk['shift80'] * (1 - chk['selected_share_of_offers'])) > 1e-12).sum())} "
    f"violations of {len(chk)}; empty shift80 <=> empty difference80: "
    f"{int((ws['shift80'].isna() != ws['difference80'].isna()).sum())} violations")
for rule in ("treated", "all"):
    s = ws[ws["df_rule"] == rule]
    pv = s.pivot_table(index=["null", "k"], columns="method", values="difference80", aggfunc="first", dropna=False)
    a = pv["t21w"].to_numpy()
    c = pv["cons"].to_numpy()
    viol = int(np.sum((np.isnan(a) & ~np.isnan(c)) | (~np.isnan(a) & ~np.isnan(c) & (c < a - 1e-12))))
    say(f"INVARIANT selection power ({rule}): cons difference80 >= t21w's (empty counts as infinite): violations {viol} of {len(pv)}")

# ------------------------------------------------------------------ 5. the pin condition
def pin_table(df, mask, label):
    rows = []
    for k in KS:
        g = df[mask & (df["k"] == k)]
        a = lev(k)
        worst = g.loc[g["ratio"].idxmax()]
        rows.append({"label": label, "k": k, "nulls": len(g), "point_above": int((g["rate"] > a).sum()),
                     "ci_wholly_above": int((g["ci_lo"] > a).sum()), "max_ratio": round(float(worst["ratio"]), 4),
                     "max_rate": float(worst["rate"]), "max_ci_lo": float(worst["ci_lo"]), "at": worst["null"]})
    return rows


rows = []
c = ls[ls["method"] == "cons"]
cr = c["null"].str.startswith("real:")
cst = c["null"].str.startswith(STRESS)
cs = c["null"].str.startswith("syn:") & ~cst
rows += pin_table(c, cr, "one-sample cons: real")
rows += pin_table(c, cs, "one-sample cons: realistic synthetic")
rows += pin_table(c, cst, "one-sample cons: stress (beside)")
for rule in ("treated", "all"):
    t = T[(T["df_rule"] == rule) & (T["method"] == "cons")]
    rows += pin_table(t, t["form"] == "placebo-selection", f"two-sample cons ({rule}): placebo-selection")
    rows += pin_table(t, t["form"] == "two-sample (C1')", f"two-sample cons ({rule}): C1'")
pin = pd.DataFrame(rows)
with pd.option_context("display.width", 250, "display.max_columns", 20, "display.max_rows", 200):
    say("PIN\n" + pin.to_string(index=False))
# every single member and the other candidates, for E-035's claim that only cons holds
rows = []
for m in ("t21e", "t21w", "t42w", "t63w", "hac21", "cons"):
    g = ls[ls["method"] == m]
    for gname, msk in (("real", g["null"].str.startswith("real:")),
                       ("realistic", g["null"].str.startswith("syn:") & ~g["null"].str.startswith(STRESS))):
        gg = g[msk]
        rows.append({"method": m, "group": gname,
                     **{f"ci_above_k{k}": int((gg[gg['k'] == k]['ci_lo'] > lev(k)).sum()) for k in KS},
                     **{f"pt_above_k{k}": int((gg[gg['k'] == k]['rate'] > lev(k)).sum()) for k in KS}})
with pd.option_context("display.width", 250, "display.max_columns", 20):
    say("LIFT CANDIDATES (count of nulls above nominal; ci = 95 % interval wholly above)\n" + pd.DataFrame(rows).to_string(index=False))
rows = []
for m in ("d621", "bm63", "bm126", "obm63", "obm126", "ft63", "pcons", "bm63c"):
    g = P[P["method"] == m]
    for gname, msk in (("real", g["null"].str.startswith("real:")),
                       ("realistic", g["null"].str.startswith("syn:") & (g["null"] != "syn:path_edge")),
                       ("stress", g["null"] == "syn:path_edge")):
        gg = g[msk]
        rows.append({"method": m, "group": gname, "nulls": gg["null"].nunique(),
                     **{f"ci_above_k{k}": int((gg[gg['k'] == k]['ci_lo'] > lev(k)).sum()) for k in KS},
                     **{f"pt_above_k{k}": int((gg[gg['k'] == k]['rate'] > lev(k)).sum()) for k in KS}})
with pd.option_context("display.width", 250, "display.max_columns", 20):
    say("P CANDIDATES\n" + pd.DataFrame(rows).to_string(index=False))
rows = []
for rule in ("treated", "all"):
    for m in ("t21w", "t42w", "t63w", "cons"):
        for form in ("placebo-selection", "two-sample (C1')"):
            gg = T[(T["df_rule"] == rule) & (T["method"] == m) & (T["form"] == form)]
            rows.append({"rule": rule, "method": m, "form": form, "nulls": gg["null"].nunique(),
                         **{f"ci_above_k{k}": int((gg[gg['k'] == k]['ci_lo'] > lev(k)).sum()) for k in KS},
                         **{f"pt_above_k{k}": int((gg[gg['k'] == k]['rate'] > lev(k)).sum()) for k in KS}})
with pd.option_context("display.width", 250, "display.max_columns", 20):
    say("TWO-SAMPLE CANDIDATES\n" + pd.DataFrame(rows).to_string(index=False))

# ------------------------------------------------------------------ 6. family O's drop rule
for cell, model in (("s1", "window"), ("s2", "window"), ("s3", "block21"), ("u3", "block5")):
    sel = W[(W["part"] == "two_sample") & (W["df_rule"] == "treated") & (W["form"] == "placebo-selection")
            & (W["method"] == "cons") & (pd.to_numeric(W["k"]) == 15) & (W["value"] == "net3")
            & (pd.to_numeric(W["share"]) == 0.25) & (W["model"] == model)]
    say(f"DROP {cell} ({model}): rows selected {len(sel)}; difference80 "
        + ("EMPTY" if len(sel) == 1 and pd.isna(sel['difference80'].iloc[0]) else
           "NOT EMPTY" if len(sel) == 1 else "n/a")
        + f"; null {sel['null'].tolist()}; reps {sel['reps'].tolist()}; csv line(s) {[int(i) + 2 for i in sel.index]}")

# raw-text check of the same rows (no pandas parsing of empties)
import csv
with open(R / "calibration_power.csv", newline="") as fh:
    rd = csv.reader(fh)
    hdr = next(rd)
    ix = {h: i for i, h in enumerate(hdr)}
    for line_no, row in enumerate(rd, start=2):
        if (row[ix["part"]] == "two_sample" and row[ix["df_rule"]] == "treated" and row[ix["form"]] == "placebo-selection"
                and row[ix["method"]] == "cons" and row[ix["k"]] and float(row[ix["k"]]) == 15
                and row[ix["value"]] == "net3" and row[ix["share"]] and float(row[ix["share"]]) == 0.25
                and row[ix["model"]] in ("window", "block21", "block5")):
            say(f"DROP raw line {line_no}: model {row[ix['model']]} k '{row[ix['k']]}' share '{row[ix['share']]}' "
                f"difference80 field {'empty' if row[ix['difference80']] == '' else 'non-empty'}; shift80 field "
                f"{'empty' if row[ix['shift80']] == '' else 'non-empty'}")

pd.to_pickle(pin, Path(__file__).with_name("pin.pkl"))
Path(__file__).with_name("audit_out.txt").write_text("\n".join(out), encoding="utf-8")
