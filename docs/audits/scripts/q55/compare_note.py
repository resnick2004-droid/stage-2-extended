"""Rebuild the Q-16 note's tables from Q-55's five CSVs with this auditor's own code, and compare them row by row with
the note's text (docs/research/calibration_2026-11-15.md). Imports nothing from the repository."""
import re
from pathlib import Path

import numpy as np
import pandas as pd

R = Path(r"C:/Users/resni/OneDrive/Desktop/Stage 2 - Extended/results")
NOTE = Path(r"C:/Users/resni/OneDrive/Desktop/Stage 2 - Extended/docs/research/calibration_2026-11-15.md")
KS = [11, 12, 13, 14, 15]
lev = lambda k: 0.05 / (k * (k + 1))  # noqa: E731
f4 = lambda r: f"{r * 1e4:.2f}"  # noqa: E731

L = pd.read_csv(R / "calibration_lift.csv", low_memory=False)
P = pd.read_csv(R / "calibration_p.csv", low_memory=False)
T = pd.read_csv(R / "calibration_two_sample.csv", low_memory=False)
W = pd.read_csv(R / "calibration_power.csv", low_memory=False)
B = pd.read_csv(R / "bm63c_table.csv", low_memory=False)


# ---------------------------------------------------------------- the note's tables, parsed
def note_tables():
    tabs, cur, name = {}, None, None
    for line in NOTE.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^#+ Table (F?\d+[ab]?)\.", line)
        if m:
            name = m.group(1)
            cur = tabs.setdefault(name, [])
            continue
        if line.startswith("#"):
            name, cur = None, None
            continue
        if cur is not None and line.startswith("|") and not line.startswith("|---"):
            cur.append(line.strip())
    return {k: [r for r in v[1:] if not r.startswith("| trades |")] for k, v in tabs.items()}  # drop header rows


# ---------------------------------------------------------------- my rebuild
def worst(df, methods, groups):
    rows = []
    for m in methods:
        for gname, mask in groups:
            g = df[(df["method"] == m) & mask]
            if g.empty:
                continue
            cells = []
            for k in KS:
                gk = g[g["k"] == k]
                # the maximum ratio; ties to the first row in file order
                i = gk.index[int(np.argmax(gk["ratio"].to_numpy()))]
                r = gk.loc[i]
                cells.append(f"**{r['ratio']:.2f}x** ({f4(r['rate'])} [{f4(r['ci_lo'])}, {f4(r['ci_hi'])}]; {r['null']})")
            rows.append(f"| `{m}` | {gname} ({g['null'].nunique()}) | " + " | ".join(cells) + " |")
    return rows


def share(df, methods, groups):
    rows = []
    for m in methods:
        cells = []
        for _, mask in groups:
            g = df[(df["method"] == m) & mask & (df["k"] == 11)]
            cells.append(f"{int((g['ci_lo'] > g['level']).sum())} of {len(g)}")
        rows.append(f"| `{m}` | " + " | ".join(cells) + " |")
    return rows


mine = {}
ls = L[L["section"] == "size"]
STRESS = ("syn:cluster_ar5", "syn:regime03", "syn:regime10", "syn:skew")
real = ls["null"].str.startswith("real:")
stress = ls["null"].str.startswith(STRESS)
syn = ls["null"].str.startswith("syn:") & ~stress
lm = ["t21e", "t21w", "t42w", "t63w", "hac21", "cons"]
groups = [("real", real), ("synthetic", syn), ("stress", stress)]
mine["1"] = worst(ls, lm, groups)
mine["1b"] = share(ls, lm, groups)
rows = []
for st in ("taken", "thin200", "thin1000", "thin5000", "offered"):
    for v in ("win1", "net3"):
        for side in ("persist1", "persist21", "persist63", "coin"):
            nl = f"real:{st}:{v}:{side}"
            g = ls[(ls["null"] == nl) & (ls["k"] == 11)]
            cells = [f"{f4(float(g[g['method'] == m]['rate'].iloc[0]))} ({float(g[g['method'] == m]['ratio'].iloc[0]):.2f}x)"
                     for m in lm]
            rows.append(f"| {nl} | " + " | ".join(cells) + " |")
mine["2"] = rows
lb = L[L["section"] == "boot"]
rows = []
for nl in dict.fromkeys(lb["null"]):
    g = lb[lb["null"] == nl]
    a = g[g["k"] == 11].iloc[0]
    b = g[g["k"] == 15].iloc[0]
    rows.append(f"| {nl} | {int(a['reps'])} | {int(a['draws'])} | {int(a['rejections'])} ({f4(a['rate'])}, {a['ratio']:.2f}x) | "
                f"{int(a['t21w_same_reps'])} | {int(b['rejections'])} ({b['ratio']:.2f}x) | {a['crit_over_t_p10']:.3f}, "
                f"{a['crit_over_t_p50']:.3f}, {a['crit_over_t_p90']:.3f} |")
mine["3"] = rows
wl = W[W["part"] == "lift"]
for tab, base in (("4a", "coin"), ("4b", "persist1")):
    rows = []
    for v, scale in (("win1", 100.0), ("net3", 1.0)):
        for n in (200, 500, 1000, 2000, 5000):
            g = wl[wl["null"] == f"real:thin{n}:{v}:{base}"]
            cells = []
            for m in ("t21w", "t63w", "cons"):
                for k in (11, 15):
                    x = float(g[(g["method"] == m) & (g["k"] == k)]["mdl80"].iloc[0]) * scale
                    cells.append(f"{x:.1f}" if scale > 1 else f"{x:.3f}")
            rows.append(f"| {n} | " + " | ".join(cells) + " |")
    mine[tab] = rows
preal = P["null"].str.startswith("real:")
pstress = P["null"] == "syn:path_edge"
psyn = P["null"].str.startswith("syn:") & ~pstress
pm = ["d621", "bm63", "bm126", "obm63", "obm126", "ft63", "pcons", "bm63c"]
pg = [("real", preal), ("synthetic", psyn), ("stress", pstress)]
mine["5"] = worst(P, pm, pg)
mine["5b"] = share(P, pm, pg)
wp = W[W["part"] == "p"]
rows = []
for nl in ("real:p16v-p14v:centred:flip63", "real:p16v-p14v:centred:flip21", "real:p14p-p14v:centred:flip63",
           "real:p16p-p16v:centred:flip63"):
    g = wp[wp["null"] == nl]
    cells = [f"{float(g[(g['method'] == m) & (g['k'] == k)]['mdd80'].iloc[0]):.3f}"
             for m in ("bm63", "bm126", "ft63", "pcons", "bm63c") for k in (11, 15)]
    rows.append(f"| {nl} | " + " | ".join(cells) + " |")
mine["6"] = rows
rows = []
for _, r in B.iterrows():
    kk = "" if pd.isna(r["k"]) else str(int(r["k"]))
    rows.append(f"| {r['level']:.3g} | {kk} | {r['critical']:.3f} | {r['t8']:.3f} | {r['ratio_to_t8']:.3f} | "
                f"{r['argmax_null']} | {int(r['calibration_nulls'])} x {int(r['reps_each'])} |")
mine["7"] = rows

for rule, pre in (("all", "F"), ("treated", "")):
    ds = T[T["df_rule"] == rule]
    dp = W[(W["part"] == "two_sample") & (W["df_rule"] == rule)]
    dm = ["t21w", "t42w", "t63w", "cons"]
    sel = ds["form"] == "placebo-selection"
    c1p = ds["form"] == "two-sample (C1')"
    g8 = [(f"selection: {m}", sel & (ds["model"] == m)) for m in ("offer", "window", "session", "block5", "block21", "block63")]
    mine[pre + "8"] = worst(ds, dm, g8)
    mine[pre + "8b"] = share(ds, dm, g8)
    pp = dp[dp["form"] == "placebo-selection"]
    rows = []
    seen = []
    for key in zip(pp["model"], pp["value"], pp["share"]):
        if key not in seen:
            seen.append(key)
    for mo, v, sh in seen:
        g = pp[(pp["model"] == mo) & (pp["value"] == v) & (pp["share"] == sh)]
        cells = []
        for m, k in (("t21w", 11), ("cons", 11), ("cons", 15)):
            r = g[(g["method"] == m) & (g["k"] == k)]
            x = float(r["difference80"].iloc[0])
            cells.append("--" if not np.isfinite(x) else (f"{x * 100:.1f}" if v == "win1" else f"{x:.3f}"))
        rows.append(f"| {mo} | {v} | {sh:g} | " + " | ".join(cells) + " |")
    mine[pre + "9"] = rows
    g10 = [(f"C1': {m}", c1p & (ds["model"] == m)) for m in ("shared", "indep", "coin")]
    mine[pre + "10"] = worst(ds, dm, g10)
    mine[pre + "10b"] = share(ds, dm, g10)
    pc = dp[(dp["form"] == "two-sample (C1')") & dp["model"].isin(["shared", "indep"]) & (dp["L"] == 1)]
    seen = []
    for key in zip(pc["level_fills"], pc["value"], pc["model"]):
        if key not in seen:
            seen.append(key)
    rows = []
    for n1, v, mo in seen:
        g = pc[(pc["level_fills"] == n1) & (pc["value"] == v) & (pc["model"] == mo)]
        cells = []
        for m, k in (("t21w", 11), ("cons", 11), ("cons", 15)):
            x = float(g[(g["method"] == m) & (g["k"] == k)]["difference80"].iloc[0])
            cells.append(f"{x * 100:.1f}" if v == "win1" else f"{x:.3f}")
        rows.append(f"| {int(n1)} | {v} | {mo} | " + " | ".join(cells) + " |")
    mine[pre + "11"] = rows

# ---------------------------------------------------------------- compare
note = note_tables()
tot_rows = tot_cells = bad_rows = bad_cells = 0
for name in sorted(set(note) | set(mine), key=lambda s: (s.startswith("F"), int(re.sub(r"\D", "", s)), s)):
    a, b = note.get(name, []), mine.get(name, [])
    if len(a) != len(b):
        print(f"Table {name}: ROW COUNT note {len(a)} vs mine {len(b)}")
    nb = 0
    nc = 0
    cells = 0
    for x, y in zip(a, b):
        xs = [c.strip() for c in x.strip("|").split("|")]
        ys = [c.strip() for c in y.strip("|").split("|")]
        cells += len(xs)
        diff = [(i, p, q) for i, (p, q) in enumerate(zip(xs, ys)) if p != q]
        if len(xs) != len(ys):
            diff.append(("len", len(xs), len(ys)))
        if diff:
            nb += 1
            nc += len(diff)
            print(f"Table {name} DIFF row '{xs[0]} | {xs[1]}': " + "; ".join(f"col {i}: note '{p}' vs mine '{q}'" for i, p, q in diff))
    tot_rows += len(a)
    tot_cells += cells
    bad_rows += nb
    bad_cells += nc
    print(f"Table {name}: {len(a)} rows, {cells} cells compared; rows differing {nb}; cells differing {nc}")
print(f"TOTAL: {tot_rows} rows, {tot_cells} cells; rows differing {bad_rows}; cells differing {bad_cells}")
