"""Q-45a audit: independent re-derivation for results/breakeven_fidelity.csv.

Reads CSV/JSON files only (the result, its manifest, Stage 2's registered user_journey.csv and gate files, the read
ledger, the bars' own manifest.json). Imports nothing from extended/, scripts/ or vendor/; runs no engine; reads no bar.
    python docs/audits/scripts/q45/rederive.py > docs/audits/scripts/q45/rederive_output.txt
"""
import hashlib, json, math, re
import numpy as np, pandas as pd

pd.set_option("display.width", 250); pd.set_option("display.max_rows", 1000); pd.set_option("display.max_columns", 40)
R = r"c:/Users/resni/OneDrive/Desktop/Stage 2 - Extended/"
V = R + "vendor/stage2/results/"
CSV = R + "results/breakeven_fidelity.csv"
man = json.load(open(CSV + ".manifest.json", encoding="utf-8"))
raw = open(CSV, "rb").read()
df = pd.read_csv(CSV)
df["value"] = pd.to_numeric(df["value"], errors="coerce"); df["n"] = pd.to_numeric(df["n"], errors="coerce")
RS = ["stage2", "stop_first", "delay5", "both"]

print("## 1. manifest")
h = hashlib.sha256(raw).hexdigest()
print("sha256 mine", h, "manifest", man["sha256"], "equal", h == man["sha256"])
print("rows mine", len(df), "manifest", man["rows"], "| columns equal", list(df.columns) == man["columns"])
print("git_commit", man["git_commit"], "git_dirty", man["git_dirty"], "exploratory", man["exploratory"], "prereg_id",
      man["prereg_id"], "seed", man["seed"], "variant_count", man["variant_count"], "timestamp", man["timestamp"])
for f, hh in man["parameters"]["references"].items():
    print("reference", f, "mine == manifest:", hashlib.sha256(open(V + f, "rb").read()).hexdigest() == hh)
print("distinct reading labels:", df["reading"].unique().tolist())
print("any ISO date string in the CSV:", bool(re.search(rb"20\d\d-\d\d-\d\d", raw)))
print("any 'CARRIED'/'chosen' in the CSV:", bool(re.search(rb"(?i)carried|chosen", raw)))
bm = json.load(open(R + "vendor/stage2/data/bars/NQ/manifest.json", encoding="utf-8"))
print("bars manifest first_day", bm["first_day"], "last_day", bm["last_day"], "days", bm["days"])
led = [json.loads(l) for l in open(R + "results/read_ledger.jsonl", encoding="utf-8")]
L = led[-1]
print("ledger last line: purpose", L["purpose"], "| declaration", L["declaration"], "| dates", L["dates"],
      "| commit", L["who"]["commit"], "dirty", L["who"]["dirty"], "clean_run", L["who"]["clean_run"], "| when", L["when"])
dm = {l.split()[1]: l.split()[0] for l in open(R + "vendor/DATA_MANIFEST_stage2.sha256", encoding="utf-8") if l.strip()}
for f in L["what"]["files"]:
    print("  ledger file", f["path"], "sha in data manifest equal:", dm.get(f["path"].replace("vendor/stage2/", "")) == f["sha256"])
print("section x rules counts:")
print(df.groupby(["section", "rules"]).size().unstack(fill_value=0).to_string())
idr = df[df.section == "identity"]
print("identity rows", len(idr), "all value 1.0:", bool((idr.value == 1.0).all()))

print("\n## 2. gate: registered rows against the vendored files; stage2 against registered")
GC = man["parameters"]["gate_cols"]
for d, f in (("p14", "a3_brk30_cb20_gate.csv"), ("p16", "rc_s150_all_gate.csv")):
    g = pd.read_csv(V + f, low_memory=False)
    g = g[(g.section == "gate") & np.isclose(pd.to_numeric(g.enforcement_p, errors="coerce").fillna(-1), 0.0)]
    bad1 = bad2 = 0
    for s in ("point", "lower_bound"):
        vr = g[g["shift"] == s]
        assert len(vr) == 1
        for c in GC:
            v = float(vr.iloc[0][c])
            sel = (df.section == "gate") & (df.design == d) & (df["shift"] == s) & (df.measure == c)
            r0 = float(df[sel & (df.rules == "registered")].value.iloc[0])
            s0 = float(df[sel & (df.rules == "stage2")].value.iloc[0])
            bad1 += not ((math.isnan(v) and math.isnan(r0)) or v == r0)
            bad2 += not ((math.isnan(v) and math.isnan(s0)) or abs(s0 - v) <= 1e-6 * max(1, abs(v)))
    print(d, f, "0 % gate rows", len(g), "| registered != file:", bad1, "| stage2 != file (1e-6 rel):", bad2,
          "| rtp", g.rtp.tolist(), "| is_gate_row", g.is_gate_row.tolist())
gt = df[df.section == "gate"].pivot_table(index=["design", "shift", "measure"], columns="rules", values="value",
                                          aggfunc="first")[["registered"] + RS]
for c in RS[1:]:
    gt["d_" + c] = gt[c] - gt["registered"]
print(gt.to_string())
lb = gt.xs("lower_bound", level=1).xs("pf_growth_on_base_p50", level=1)
print("pf_growth_on_base_p50 at the bound > 0, every rule set:", bool((lb[RS] > 0).all().all()))

print("\n## 3. trades section")
t = df[df.section == "trades"].pivot_table(index=["design", "rr", "rules"], columns="measure", values="value", aggfunc="first")
KINDS = ("share_stop", "share_target", "share_flatten", "share_breakeven")
fails = 0
for (d, rr), g in t.groupby(level=[0, 1]):
    g = g.droplevel([0, 1]); s = g.loc["stage2"]; f = g.loc["stop_first"]; n = s.trades
    ok = bool((g.trades == n).all()) and s.changed_kind == 0 and s.changed_gross == 0
    ok &= abs(g[list(KINDS)].sum(axis=1) - 1).max() < 1e-12
    dt = (s.share_target - f.share_target) * n; db = (f.share_breakeven - s.share_breakeven) * n
    ok &= abs(dt - f.changed_kind) < 1e-6 and abs(db - f.changed_kind) < 1e-6
    ok &= abs(f.share_stop - s.share_stop) < 1e-12 and abs(f.share_flatten - s.share_flatten) < 1e-12
    ok &= f.mean_net_r <= s.mean_net_r
    for k in ("delay5", "both"):
        x = g.loc[k]
        ok &= sum(abs((x[c] - s[c]) * n) for c in KINDS) / 2 <= x.changed_kind + 1e-6
    for k in g.index:
        for c in KINDS:
            ok &= abs(g.loc[k, c] * n - round(g.loc[k, c] * n)) < 1e-6
    fails += not ok
print("groups", t.groupby(level=[0, 1]).ngroups, "failing:", fails)
print("mean_net_r by design, R and rule set:")
print(t["mean_net_r"].unstack("rules")[RS].to_string())
print("changed_kind summed over R:", t["changed_kind"].unstack("rules")[RS[1:]].groupby(level=0).sum().to_dict())

print("\n## 4. the stage2 rule set's scorecard, extra and path rows re-derived from user_journey.csv's start rows")
u = pd.read_csv(V + "user_journey.csv", low_memory=False)
st = u[u.section == "start"].copy()
for c in st.columns:
    if c.startswith(("net_month", "fees_month")) or c in ("observed", "first_pass", "first_payout", "start_day",
                                                         "spent_before_first_payout", "spent_before_first_pass"):
        st[c] = pd.to_numeric(st[c], errors="coerce")
print("exact_runs_differing non-blank on p14/p16 start rows:",
      int(st[st.config.isin(["p14", "p16"])].exact_runs_differing.notna().sum()))
NN = st[[f"net_month_{k}" for k in range(1, 13)]].to_numpy(float)
FF = st[[f"fees_month_{k}" for k in range(1, 13)]].to_numpy(float)
PP = NN + FF; mm = np.isfinite(PP)
print("start rows (all configs): implied payouts (net + fees) < 0:", int((PP[mm] < -1e-6).sum()),
      "| fees falling month to month:", int((np.diff(FF, axis=1) < -1e-6).sum()),
      "| payouts falling:", int((np.diff(PP, axis=1) < -1e-6).sum()))
BEY = 1e9


def q(x, p):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    return float(np.percentile(x, p)) if len(x) else np.nan


def dq(first, w, p):
    f = np.asarray(first, float); v = np.where(np.isfinite(f) & (f <= w), f, BEY)
    if not len(v):
        return np.nan
    r = float(np.percentile(v, p))
    return r if r <= w else np.nan


def gap(pdays, obs, w):
    if obs < w:
        return np.nan
    s = str(pdays).strip()
    days = [] if s in ("", "nan", "<NA>", "None") else [int(float(x)) for x in s.split()]
    inw = sorted(d for d in days if d <= w)
    if not inw:
        return np.nan
    m = inw + [w]
    return float(max(b - a for a, b in zip(m, m[1:])))


def conc(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    if not len(x) or not x.sum() > 0:
        return np.nan
    return float(np.sort(x)[::-1][:math.ceil(len(x) / 4)].sum() / x.sum())


def cvar(x, qq=0.10):
    v = np.sort(np.asarray(x, float)[np.isfinite(np.asarray(x, float))])
    k = max(1, int(math.ceil(qq * len(v) - 1e-12)))
    return float(v[:k].mean())


def card(t, block):
    yr = t.start_date.str[:4].astype(int)

    def E(h):
        m = t.observed >= h
        return (m & (yr >= 2024)) if block == "judged" else m

    o = {}
    e = E(63); x = t[e][["net_month_1", "net_month_2", "net_month_3"]].to_numpy(float)
    ok = np.isfinite(x).all(1); a = x[ok] > 0
    o["scorecard:P"] = (a.sum() / (3 * ok.sum()), ok.sum())
    o["extra:P"] = o["scorecard:P"]
    for i in range(3):
        o[f"extra:share_ahead_month_{i+1}"] = (a[:, i].mean(), ok.sum())
        o[f"extra:mean_net_month_{i+1}"] = (np.nanmean(x[:, i]), np.isfinite(x[:, i]).sum())
    o["extra:cvar10_net_month_3"] = (cvar(x[:, 2]), np.isfinite(x[:, 2]).sum())
    sp = t[e]["spent_before_first_payout"].to_numpy(float)
    for lim in (2000, 2500):
        aa = a & (np.where(np.isfinite(sp[ok]), sp[ok], np.inf) <= lim)[:, None]
        o[f"extra:P_bankroll_{lim}"] = (aa.sum() / (3 * ok.sum()), ok.sum())
        s3 = sp[np.isfinite(sp)]
        o[f"extra:share_spent_over_{lim}"] = ((s3 > lim).mean(), len(s3))
    o["extra:n_nonoverlapping"] = (ok.sum() / 63, ok.sum())
    e = E(126); g = t[e]; fp = g.first_payout.to_numpy(float); hit = np.isfinite(fp) & (fp <= 126)
    o["scorecard:S1"] = (q(g.spent_before_first_payout.to_numpy(float)[hit], 90), hit.sum())
    o["scorecard:S3b"] = (dq(fp, 126, 90), e.sum())
    e21 = E(21); f21 = t[e21].first_payout.to_numpy(float)
    o["scorecard:S3a"] = ((np.isfinite(f21) & (f21 <= 21)).mean(), e21.sum())
    e = E(63); g3 = t[e]; nt = g3.net_month_3.to_numpy(float); fe = g3.fees_month_3.to_numpy(float)
    k3 = np.isfinite(nt) & np.isfinite(fe)
    o["scorecard:S3c"] = ((nt[k3] + fe[k3]).sum() / fe[k3].sum(), k3.sum())
    o["scorecard:S5a"] = (q(nt, 10), np.isfinite(nt).sum())
    for k, hz, c in (("S4a", 126, "net_month_6"), ("S4b", 252, "net_month_12")):
        x6 = t[E(hz)][c].to_numpy(float); x6 = x6[np.isfinite(x6)]
        o[f"scorecard:{k}"] = ((x6 > 0).mean(), len(x6))
    gg = np.array([gap(p, ob, 126) for p, ob in zip(g.pay_days, g.observed)]); gg = gg[np.isfinite(gg)]
    o["scorecard:S5b"] = (q(gg, 90), len(gg))
    x6 = g.net_month_6.to_numpy(float)
    o["scorecard:S5c"] = (conc(x6), np.isfinite(x6).sum())
    for ev, spc in (("first_pass", "spent_before_first_pass"), ("first_payout", "spent_before_first_payout")):
        f = g[ev].to_numpy(float); h_ = np.isfinite(f) & (f <= 126)
        for p in (10, 50, 90):
            o[f"path:{ev}_days:p{p}"] = (dq(f, 126, p), len(f))
        o[f"path:{ev}_days:share_by_126"] = (h_.mean(), len(f))
        for p in (10, 50, 90):
            o[f"path:{spc}:p{p}"] = (q(g[spc].to_numpy(float)[h_], p), h_.sum())
    return o


rows = []
for d in ("p14", "p16"):
    for arm in ("verdict", "point"):
        tt = st[(st.config == d) & (st.arm == arm)]
        for b in ("all", "judged"):
            for key, (v, n) in card(tt, b).items():
                parts = key.split(":"); sec, m = parts[0], parts[1]; s = parts[2] if len(parts) > 2 else "value"
                r = df[(df.section == sec) & (df.design == d) & (df.rules == "stage2") & (df.arm == arm)
                       & (df.block == b) & (df.measure == m) & (df.stat == s)]
                rv, rn = (float(r.value.iloc[0]), float(r.n.iloc[0])) if len(r) == 1 else (np.nan, np.nan)
                ag = (math.isnan(v) and math.isnan(rv)) or abs(v - rv) <= 1e-9 * max(1, abs(rv))
                rows.append((d, arm, b, key, rv, v, ag, float(n) == rn))
res = pd.DataFrame(rows, columns=["design", "arm", "block", "row", "reported", "mine", "value_agrees", "n_agrees"])
print("rows compared", len(res), "| value disagreements", int((~res.value_agrees).sum()),
      "| n disagreements", int((~res.n_agrees).sum()))
print(res[res.row.str.startswith("scorecard") & (res.arm == "verdict")].to_string(index=False))
for d in ("p14", "p15", "p16"):
    tt = st[(st.config == d) & (st.arm == "verdict")]
    print(d, "registered start rows", len(tt), "first", tt.start_date.min(), "last", tt.start_date.max(), "cell",
          tt.cell.iloc[0], "| P (all, verdict) from user_journey.csv start rows:", card(tt, "all")["scorecard:P"])

print("\n## 5. internal checks on every rule set (the corrected ones have no start rows in the file)")


def val(sec, d, r, a, b, m, s="value"):
    x = df[(df.section == sec) & (df.design == d) & (df.rules == r) & (df.arm == a) & (df.block == b)
           & (df.measure == m) & (df.stat == s)]
    assert len(x) == 1, (sec, d, r, a, b, m, s, len(x))
    return float(x.value.iloc[0]), float(x.n.iloc[0])


sh = df[df.section.isin(["scorecard", "extra", "path"])]
smask = (sh.measure.isin(["P", "S3a", "S4a", "S4b"]) | sh.measure.str.startswith(("share_", "P_bankroll"))
         | sh.stat.str.startswith("share"))
print("share rows", int(smask.sum()), "outside [0, 1]:", int(((sh.value < 0) | (sh.value > 1))[smask].sum()))
probs = []
for d in ("p14", "p16"):
    for r in RS:
        for a in ("verdict", "point"):
            for b in ("all", "judged"):
                P, n = val("scorecard", d, r, a, b, "P"); Pe, ne = val("extra", d, r, a, b, "P")
                s = [val("extra", d, r, a, b, f"share_ahead_month_{m}") for m in (1, 2, 3)]
                if not (P == Pe and n == ne):
                    probs.append(("card P != extra P", d, r, a, b))
                if abs(P - sum(x[0] for x in s) / 3) > 1e-12 or any(x[1] != n for x in s):
                    probs.append(("P != mean of the three shares", d, r, a, b))
                b2, _ = val("extra", d, r, a, b, "P_bankroll_2000"); b25, _ = val("extra", d, r, a, b, "P_bankroll_2500")
                if not b2 <= b25 <= P:
                    probs.append(("P_bankroll order", d, r, a, b))
                o2, _ = val("extra", d, r, a, b, "share_spent_over_2000"); o25, _ = val("extra", d, r, a, b, "share_spent_over_2500")
                if not o2 >= o25:
                    probs.append(("share_spent_over order", d, r, a, b))
                if abs(val("extra", d, r, a, b, "n_nonoverlapping")[0] - n / 63) > 1e-12:
                    probs.append(("n/63", d, r, a, b))
                if not val("extra", d, r, a, b, "cvar10_net_month_3")[0] <= val("scorecard", d, r, a, b, "S5a")[0]:
                    probs.append(("CVaR10 > p10", d, r, a, b))
                if val("scorecard", d, r, a, b, "S1") != val("path", d, r, a, b, "spent_before_first_payout", "p90"):
                    probs.append(("S1 != path p90", d, r, a, b))
                x1 = val("scorecard", d, r, a, b, "S3b")[0]; x2 = val("path", d, r, a, b, "first_payout_days", "p90")[0]
                if not ((math.isnan(x1) and math.isnan(x2)) or x1 == x2):
                    probs.append(("S3b != path p90", d, r, a, b))
                for m in df[df.section == "path"].measure.unique():
                    try:
                        qq = [val("path", d, r, a, b, m, f"p{p}")[0] for p in (10, 50, 90)]
                    except AssertionError:
                        continue
                    qq = [x for x in qq if not math.isnan(x)]
                    if qq != sorted(qq):
                        probs.append(("percentiles out of order", d, r, a, b, m))
                if r != "stage2":
                    for m in ("P", "S3a", "S3b", "S3c", "S4a", "S4b", "S5a"):
                        if val("scorecard", d, "stage2", a, b, m)[1] != val("scorecard", d, r, a, b, m)[1]:
                            probs.append(("eligible n differs from stage2", d, r, a, b, m))
print("internal problems:", len(probs), probs[:20])
print("mdd_P values:", df[df.measure == "mdd_P"].value.unique().tolist(),
      "| n_eff_bartlett rows non-blank:", int(df[df.measure == "n_eff_bartlett"].value.notna().sum()))
print("paired / interval columns in the CSV:", [c for c in df.columns if c in ("lo", "hi", "reference", "difference", "alpha")])

print("\n## 6. each corrected rule set against the registered row (stage2 = registered, by the identities and section 4)")
sc = df[df.section == "scorecard"]
DIR = {"P": "h", "S1": "l", "S3a": "h", "S3b": "l", "S3c": "h", "S4a": "h", "S4b": "h", "S5a": "h", "S5b": "l", "S5c": "l"}
UNIT = {"P": "share", "S1": "dollars", "S3a": "share", "S3b": "sessions", "S3c": "ratio", "S4a": "share", "S4b": "share",
        "S5a": "dollars", "S5b": "sessions", "S5c": "ratio"}
rows = []
for (d, a, b, m), g in sc.groupby(["design", "arm", "block", "measure"]):
    g = g.set_index("rules"); ref = g.loc["stage2", "value"]
    for r in RS[1:]:
        x = g.loc[r, "value"]; dl = x - ref; worse = -dl if DIR[m] == "h" else dl
        flag = worse > 0.05 if UNIT[m] == "share" else worse > 0.10 * abs(ref)
        rows.append((d, r, a, b, m, ref, x, dl, "better" if worse < 0 else ("same" if worse == 0 else "worse"), bool(flag)))
T = pd.DataFrame(rows, columns=["design", "rules", "arm", "block", "measure", "registered", "corrected", "diff",
                                "direction", "beyond_tolerance"])
for d in ("p14", "p16"):
    print(T[(T.design == d) & (T.arm == "verdict")].sort_values(["block", "rules", "measure"]).to_string(index=False))
print("beyond tolerance (share 0.05; else 10 % of |registered|):")
print(T[T.beyond_tolerance].to_string(index=False))
print(T.groupby(["arm", "rules", "direction"]).size().unstack(fill_value=0).to_string())
