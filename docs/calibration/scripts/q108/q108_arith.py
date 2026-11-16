"""Q-108's plan, section 1 and 4: arithmetic only -- no data, no randomness. The judged block's 657 sessions, Q-16's
sign-flip phases, the family levels 0.05/(k(k+1)) at k = 13..20, binomial quantiles at 200,000 replications.

    python docs/calibration/scripts/q108/q108_arith.py

A(L): the aligned pattern's probability averaged over phases (a test rejecting it at every phase has at least this
size). H1(L): aligned and every single-block flip, (1 + B) 2^-B. H2(L): with every two-block flip added. A_eff(63):
A(63) with an edge flip block of at most 3 sessions not counted as a block (no real decision)."""
import math

import numpy as np
from scipy import stats

N = 657
KS = tuple(range(13, 21))
LEV = {k: 0.05 / (k * (k + 1)) for k in KS}
R = 200_000


def blocks(p: int, L: int, n: int = N) -> int:
    return (n - 1 + p) // L - p // L + 1


def main() -> None:
    print("levels:", {k: f"{a:.4e}" for k, a in LEV.items()})
    print("log2(1/level):", {k: round(-math.log2(a), 2) for k, a in LEV.items()})
    for L in (21, 42, 55, 63):
        Bs = [blocks(p, L) for p in range(L)]
        cnt = {b: Bs.count(b) for b in sorted(set(Bs))}
        A = sum(2.0 ** -b for b in Bs) / L
        H1 = sum((1 + b) * 2.0 ** -b for b in Bs) / L
        H2 = sum((1 + b + b * (b - 1) / 2) * 2.0 ** -b for b in Bs) / L
        print(f"L={L}: blocks by phase {cnt}; A={A:.4e}  H1={H1:.4e}  H2={H2:.4e}")
        for name, x in (("A", A), ("H1", H1), ("H2", H2)):
            print(f"   {name}/level k13..20: " + " ".join(f"{x / LEV[k]:.3f}" for k in KS))
    aeff = 0.0
    for p in range(63):
        sizes = np.bincount((np.arange(N) + p) // 63)
        b = len(sizes) - int(sizes[0] <= 3) - int(sizes[-1] <= 3)
        aeff += 2.0 ** -b
    aeff /= 63
    print(f"A_eff(63)={aeff:.4e}; /level k13..20: " + " ".join(f"{aeff / LEV[k]:.3f}" for k in KS))
    # the most 63-session blocks any side constant on them can have on n sessions: floor((n - 1)/63) + 2
    for n in (657, 1006):
        print(f"n={n}: at most {(n - 1) // 63 + 2} blocks of 63 sessions, so at most that many runs")
    # validation (4.3): the smallest count whose Clopper-Pearson lower limit exceeds the level (a failure)
    fail = {}
    for k, a in LEV.items():
        c = int(a * R)
        while stats.beta.ppf(0.025, c, R - c + 1) <= a:
            c += 1
        fail[k] = c
    print("nominal counts at 200,000:", {k: round(a * R, 1) for k, a in LEV.items()})
    print("validation failure: at least", fail, "rejections")
    print("t critical values, df 4 / 9 at k=13:", round(stats.t.isf(LEV[13], 4), 3), round(stats.t.isf(LEV[13], 9), 3))
    # 4.2's P(HOLDS) for one Monte Carlo null with true rates rho x nominal at every k: nested binomials, by dynamic
    # programming over the counts (exact; the same computation the calibration script makes from its counts)
    for rho in (0.5, 0.7, 0.8, 1.0):
        print(f"one null at {rho} x nominal: P(it fails 4.3) = {1 - p_holds([rho * LEV[k] for k in KS], fail):.2e}")
    # detection of a bad-subset rate b in S independent subsets: 1 - (1 - b)^S
    for b, S in ((0.02, 23), (0.10, 23), (0.02, 60), (0.02, 115), (0.04, 60), (0.05, 25), (0.10, 25)):
        print(f"P(at least one bad subset | rate {b}, {S} subsets) = {1 - (1 - b) ** S:.3f}")


def p_holds(rates, fail, reps=R):
    """P(X_k < fail_k at every k) for X_13 ~ Bin(reps, rates[0]), X_{k+1} | X_k ~ Bin(X_k, rates[i+1] / rates[i])."""
    f = [fail[k] for k in KS]
    xs = np.arange(f[0])
    prob = stats.binom.pmf(xs, reps, rates[0])
    for i in range(1, len(KS)):
        q = rates[i] / rates[i - 1] if rates[i - 1] > 0 else 0.0
        nxt = np.zeros(f[i])
        for x, w in zip(xs, prob):
            if w == 0.0:
                continue
            y = np.arange(min(x, f[i] - 1) + 1)
            nxt[y] += w * stats.binom.pmf(y, x, q)
        xs, prob = np.arange(f[i]), nxt
    return float(prob.sum())


def alternating() -> None:
    """The alternating models' granularity: 2L equally likely configurations, so an exact size is 0 or >= 1/(2L)."""
    for L in (45, 55):
        print(f"alternating L={L}: one configuration is 1/{2 * L} = {1 / (2 * L):.4e}, "
              + " ".join(f"{1 / (2 * L) / LEV[k]:.0f}x" for k in KS) + " the levels k13..20")


if __name__ == "__main__":
    main()
    alternating()
