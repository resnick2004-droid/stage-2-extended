"""Red team: P per start, the judged block's paired series, its dependence, and line (3)(i) as coded.
Independent re-implementation (written from the vendored docstrings, not from any auditor's script)."""
import numpy as np
import pandas as pd

D = r"C:\Users\resni\AppData\Local\Temp\claude\197752aa8b2362c7\9862c1b3-c57d-4498-a2d7-44492c7a25e6\scratchpad\redteam"
st = pd.read_csv(D + r"\starts.csv", low_memory=False)
st = st[st["arm"] == "verdict"].copy()
st["start_day"] = st["start_day"].astype(int)


def A(cfg):
    s = st[(st["config"] == cfg) & (st["observed"] >= 63)].sort_values("start_day")
    a = ((s[["net_month_1", "net_month_2", "net_month_3"]] > 0).sum(axis=1) / 3.0).values
    return pd.Series(a, index=s["start_date"].values)


def boot_idx(n, b, draws=2000, seed=20261700):
    rng = np.random.default_rng(seed)
    k = -(-n // b)
    first = rng.integers(0, n - b + 1, size=(draws, k))
    return (first[:, :, None] + np.arange(b)[None, None, :]).reshape(draws, k * b)[:, :n]


a14, a15, a16 = A("p14"), A("p15"), A("p16")
for nm, a in (("p14", a14), ("p15", a15), ("p16", a16)):
    print(nm, "P all", round(a.mean(), 6), "n", len(a))

# identity of the bootstrap: the file's paired row p14 vs p16, periodic share_positive at 63 (all starts)
pr = pd.read_csv(D + r"\paired.csv", low_memory=False)
row = pr[(pr["config"] == "p14") & (pr["arm"] == "verdict") & (pr["reference"] == "p16") & (pr["group"] == "periodic")
         & (pr["measure"] == "share_positive") & (pr["at_days"] == 63) & pr["year"].isna()]
print(row[["value", "reference_value", "difference", "lo", "hi", "block", "n"]].to_string())
s14 = st[(st["config"] == "p14") & (st["observed"] >= 63)].set_index("start_date")
s16 = st[(st["config"] == "p16") & (st["observed"] >= 63)].set_index("start_date")
common = sorted(set(s14.index) & set(s16.index))
x = (s14.loc[common, "net_month_3"] > 0).astype(float).values
y = (s16.loc[common, "net_month_3"] > 0).astype(float).values
idx = boot_idx(len(x), 63)
bt = x[idx].mean(1) - y[idx].mean(1)
print("my identity: diff", x.mean() - y.mean(), "lo", np.percentile(bt, 2.5), "hi", np.percentile(bt, 97.5), "n", len(x))

# the judged block
J = [d for d in common if d >= "2024-01-01"]
for nm, ref in (("p16", a16), ("p15", a15)):
    dj = (a14.loc[J] - ref.loc[J]).values
    n = len(dj)
    print(f"\n== P-14 minus {nm}, judged block: n {n}, first {J[0]}, last {J[-1]}, mean {dj.mean():+.4f}, sd {dj.std(ddof=1):.3f}")
    xc = dj - dj.mean()
    acf = [np.dot(xc[:-L], xc[L:]) / np.dot(xc, xc) for L in range(1, 120)]
    print("acf lags 1,2,5,10,21,42,63:", [round(acf[L - 1], 3) for L in (1, 2, 5, 10, 21, 42, 63)],
          "first lag <=0:", 1 + next(i for i, v in enumerate(acf) if v <= 0))
    se_iid = dj.std(ddof=1) / np.sqrt(n)
    nb = n // 63
    bm = dj[: nb * 63].reshape(nb, 63).mean(1)
    se_bm = bm.std(ddof=1) / np.sqrt(nb)
    # Bartlett long-run variance
    g0 = np.dot(xc, xc) / n
    for L in (63, 126):
        lrv = g0 + 2 * sum((1 - l / (L + 1)) * np.dot(xc[:-l], xc[l:]) / n for l in range(1, L + 1))
        print(f"Bartlett L={L}: se {np.sqrt(lrv / n):.4f}  n_eff {n * g0 / lrv:.0f}")
    print(f"se iid {se_iid:.4f}; batch means (b=63, {nb} batches) se {se_bm:.4f}, n_eff {n * g0 / (se_bm**2 * n):.0f}")
    idx = boot_idx(n, 63)
    bt = dj[idx].mean(1)
    lev = 0.05 / 110
    lo = np.percentile(bt, 100 * lev)
    print(f"rule (3)(i) at 0.05/110, seed 20261700: lower {lo:+.4f}; boot sd {bt.std(ddof=1):.4f}; boot centre {bt.mean():+.4f} "
          f"vs sample {dj.mean():+.4f}; min draw {bt.min():+.4f}, 2nd {np.sort(bt)[1]:+.4f}; index pos {1999 * lev:.3f}")
    # weights of the non-circular bootstrap
    cnt = np.bincount(idx.ravel(), minlength=n) / idx.shape[0]
    print("expected weight per start: first", round(cnt[0], 3), "last", round(cnt[-1], 3), "middle", round(cnt[n // 2], 3))
    wmean = np.dot(cnt, dj) / cnt.sum()
    print("weighted mean (bootstrap centre, exact)", round(wmean, 4))
    from scipy import stats
    for se, lab in ((0.051, "b63"), (se_bm, "batch")):
        z = stats.norm.ppf(1 - lev) + stats.norm.ppf(0.8)
        print(f"MDD80 nominal z with se {se:.4f} ({lab}): {z * se:.3f}; t(df {nb - 1}) version: "
              f"{(stats.t.ppf(1 - lev, nb - 1) + stats.t.ppf(0.8, nb - 1)) * se:.3f}")
    # the judged P values
    print("judged P: p14", round(a14.loc[J].mean(), 4), nm, round(ref.loc[J].mean(), 4))

np.save(D + r"\d_judged_p14_p16.npy", (a14.loc[J] - a16.loc[J]).values)
np.save(D + r"\d_all_p14_p16.npy", (a14.loc[common] - a16.loc[common]).values)
