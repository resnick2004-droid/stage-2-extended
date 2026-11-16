# Family B's drafter (Q-43, Q-56): a scratch check behind prereg/DRAFT_F-B_multifeature.md section 12 -- EXPLORATORY,
# synthetic only, seeds fixed before running, one small process; selects nothing (the third review's m3-7).
# What it checks: M3-2: R-squared of the opening-range quantities on the 37 features (with `dow` indicators) at 10:05, 10:30 and 12:00, a synthetic year (seed [20261968, 70]).

# Scratch (exploratory): linear recoverability of opening-range quantities from family B's 37 features.
import sys
sys.path.insert(0, r"C:\Users\resni\AppData\Local\stage2-extended-wt\wt-scout"); sys.path.insert(0, r"C:\Users\resni\AppData\Local\stage2-extended-wt\wt-scout\tests")
from datetime import date
import numpy as np, pandas as pd
from extended import features as F, synthetic_bars as sb
import test_family_b_opening_range as T
bars = sb.generate(sb.Spec(date(2021, 1, 4), date(2021, 12, 31), seed=int(np.random.default_rng([20261968, 70]).integers(1, 2**31))))
cal = F.load_calendars()
alerts = [F.slot(10, 5), F.slot(10, 30), F.slot(12, 0)]
X = F.compute(bars, alerts, cal, normalisers=True)
X = X[X["day"] >= "2021-02-05"].reset_index(drop=True)
q = T._or_quantities(bars, X)
local = pd.to_datetime(bars["ts"], unit="s", utc=True).dt.tz_convert(sb.CHICAGO).dt.tz_localize(None)
slot = ((local.dt.hour * 60 + local.dt.minute - 1020) % 1440).to_numpy()
b = bars.assign(slot=slot)
def asof(day, s):
    x = b[(b["day"] == day) & (b["slot"] <= s)]; return float(x["close"].iloc[-1])
or60 = np.array([asof(d, F.slot(9, 29)) for d in X["day"]]); o830 = np.array([float(b[(b.day == d) & (b.slot >= 930)].open.iloc[0]) for d in X["day"]])
q["move60"] = (or60 - o830) / X["norm_atr14"].to_numpy()
cols = list(T.FAMILY_B_FEATURES)
for s in alerts:
    r = (X["slot"] == s).to_numpy()
    Z = X.loc[r, cols].copy(); Z = pd.get_dummies(Z, columns=["dow"], drop_first=True, dtype=float)
    ok = np.isfinite(Z.to_numpy(dtype=float)).all(1)
    out = []
    for name, v in q.items():
        y = v[r]; m = ok & np.isfinite(y)
        A = np.c_[np.ones(m.sum()), Z.to_numpy(dtype=float)[m]]
        beta, *_ = np.linalg.lstsq(A, y[m], rcond=None); res = y[m] - A @ beta
        out.append("%s R2 %.3f" % (name, 1 - res.var() / y[m].var()))
    print(F.slot_label(s), int(ok.sum()), "rows,", A.shape[1] - 1, "cols |", " | ".join(out))

# Printed (run 2026-11-16):
# 10:05 226 rows, 40 cols | width R2 0.703 | position R2 0.794 | move R2 0.951 | vwap R2 0.955 | move60 R2 0.979
# 10:30 226 rows, 40 cols | width R2 0.678 | position R2 0.756 | move R2 0.721 | vwap R2 0.924 | move60 R2 1.000
# 12:00 226 rows, 40 cols | width R2 0.693 | position R2 0.747 | move R2 0.598 | vwap R2 0.931 | move60 R2 0.773
