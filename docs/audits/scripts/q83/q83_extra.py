"""Q-83 audit, second pass: invariants, null sets, persist63 rows across both runs, the discreteness of the L = 63 flip
null. Reads the CSVs only; imports nothing from the repository."""
from pathlib import Path

import numpy as np
import pandas as pd

R = Path(r"C:/Users/resni/OneDrive/Desktop/Stage 2 - Extended/results")
KS = [11, 12, 13, 14, 15]
OUT = []


def say(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


one = pd.read_csv(R / "q82_validation_one_sample.csv", low_memory=False)
two = pd.read_csv(R / "q82_validation_two_sample.csv", low_memory=False)
cpn = pd.read_csv(R / "q82_count_persistent.csv", low_memory=False)
q55 = pd.read_csv(R / "calibration_lift.csv", low_memory=False)
q55 = q55[q55["section"] == "size"]

for name, df in (("one", one), ("two", two), ("count_persistent", cpn)):
    piv = df.pivot_table(index=["null", "level"], columns="method", values="rejections", aggfunc="first")
    v = int((piv["cons"] > piv[["t21w", "t42w", "t63w"]].min(axis=1)).sum())
    mono = 0
    for _, g in df.sort_values("level").groupby(["null", "method"]):
        mono += int(np.any(np.diff(g["rejections"].to_numpy()) < 0))
    say(f"INVARIANT {name}: cons <= min(members) violations {v} of {len(piv)}; non-monotone series {mono}")
crit_one = one[one["in_criterion"].astype(str).str.lower() == "true"]
say("one-sample criterion nulls by group:", crit_one.groupby("group")["null"].nunique().to_dict(),
    "; not in criterion:", int((one["in_criterion"].astype(str).str.lower() != "true").sum()))
say("Q-83 realistic models:", sorted(set(crit_one[crit_one["group"] != "real"]["model"])),
    "; stress nulls present:", sorted(set(x for x in crit_one["null"] if any(s in x for s in ("ar5", "regime03", "regime10", "skew")))))
say("two-sample criterion nulls by function:", two[two["in_criterion"].astype(str).str.lower() == "true"].groupby("function")["null"].nunique().to_dict())
say("Q-83 scalar re-decision columns (sum over cons rows):", int(one[one.method == "cons"]["scalar_checked"].sum() // 9),
    "checked-per-null sum /9 levels;", "mismatched total", int(one["scalar_mismatched"].sum() + two["scalar_mismatched"].sum()))

# every persist63 real null, cons at k = 11 and the members, Q-83 against Q-55
p63 = [n for n in crit_one["null"].unique() if n.endswith(":persist63")]
rows = []
for n in sorted(p63):
    r = {"null": n}
    for tag, df in (("q83", one), ("q55", q55)):
        g = df[(df["null"] == n) & (df["k"] == 11)].set_index("method")["rejections"]
        for m in ("t21w", "t42w", "t63w", "cons"):
            r[f"{tag}_{m}"] = int(g[m])
    rows.append(r)
with pd.option_context("display.width", 250):
    say("persist63 real nulls at k = 11, rejections of 200,000 (nominal 75.76):\n" + pd.DataFrame(rows).to_string(index=False))

# the discreteness of the L = 63 sign-flip null on 657 sessions (q16_calibrate._flip_signs: (n + L) // L + 1 signs drawn)
n, L = 657, 63
nb = (n + L) // L + 1
blocks_touched = sorted({((n - 1) + ph) // L - ph // L + 1 for ph in range(L)})
say(f"L = 63 flip null: {nb} signs drawn a replication; the 657 sessions touch {blocks_touched} blocks across phases; "
    f"one sign pattern's probability 2^-11 = {2.0 ** -11:.3e}, 2^-12 = {2.0 ** -12:.3e}; family levels "
    f"{', '.join(f'{0.05 / (k * (k + 1)):.3e}' for k in KS)}")
r = one[(one["null"] == "real:thin5000:win1:persist63") & (one["method"] == "cons") & (one["k"] == 11)].iloc[0]
say(f"the failing null's cons rate at k = 11: {r['rate']:.3e} = {r['rate'] / 2.0 ** -11:.2f} x 2^-11")
Path(__file__).with_name("q83_extra_out.txt").write_text("\n".join(OUT), encoding="utf-8")
