"""Red team: S5a (month-3 net p10) on the judged block -- R*'s value, the 10 % tolerance, the paired bootstrap sd."""
import numpy as np, pandas as pd
D = r"C:\Users\resni\AppData\Local\Temp\claude\197752aa8b2362c7\9862c1b3-c57d-4498-a2d7-44492c7a25e6\scratchpad\redteam"
st = pd.read_csv(D + r"\starts.csv", low_memory=False)
st = st[(st.arm == "verdict") & (st.observed >= 63) & (st.start_date >= "2024-01-01")]
a = st[st.config == "p14"].set_index("start_date").sort_index()
b = st[st.config == "p16"].set_index("start_date").sort_index()
c = sorted(set(a.index) & set(b.index))
x, y = a.loc[c, "net_month_3"].values, b.loc[c, "net_month_3"].values
p10 = lambda v: np.percentile(v, 10)
print("n", len(c), "P-14 p10", round(p10(x), 2), "tolerance", round(abs(0.1 * p10(x)), 2), "P-16 p10", round(p10(y), 2))
rng = np.random.default_rng(20261700); n = len(c); k = -(-n // 63)
first = rng.integers(0, n - 63 + 1, size=(2000, k)); idx = (first[:, :, None] + np.arange(63)).reshape(2000, -1)[:, :n]
d = np.array([p10(x[i]) - p10(y[i]) for i in idx])
print("paired p10 difference sd (b=63)", round(d.std(ddof=1), 1), "| P-14 p10 own sd", round(np.std([p10(x[i]) for i in idx], ddof=1), 1))
