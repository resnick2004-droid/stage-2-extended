"""Q-16: the calibration behind `docs/research/calibration_2026-11-15.md` -- each candidate statistic's rejection rate at
a true zero on nulls with the data's own dependence and on declared synthetic nulls, with Monte Carlo intervals, and
its minimum detectable effect. EXPLORATORY figures for the note; writes only to `--out` (never `results/`).

    python scripts/q16_calibrate.py --out <dir> --pairs <dir>/p16_pairs.parquet --part lift   # section 1
    python scripts/q16_calibrate.py --out <dir> --part p                                     # section 2
    python scripts/q16_calibrate.py --out <dir> --synthetic-only --part lift --reps 2000     # the slow test's size

**Section 1, the trades-first lift** (`extended.lift_bound`). The judged block's calendar is A1's trading days from
2024-01-02 (`vendor/stage2/data/atlas/A1/days.parquet`, read-only: a calendar). The real nulls take P-16's own pairs
(`scripts/q16_p16_pairs.py`'s output, its identity held) on that block, `v = (outcome(long) - outcome(short)) / 2` at the
same bracket -- in win probability at 1R (`win1`) and in net R at 3R (`net3`) -- and flip the sign of every pair
difference by blocks of L sessions (L = 1, 5, 21, 63; a random phase each replication): the dependence within a flip
block stays (a rule whose side holds for L sessions), the mean is zero by construction. `coin` uses the coin's own
side (`coin x v`) flipped by session. Streams: every offered candidate (`offered`, about 141 a session), the
re-entry-when-flat schedule at the fresh Combine's 1.5R (`taken`, the next mark at least 5 minutes after the coin
side's exit), and seeded uniform thinnings of the offered candidates to 200 ... 5,000 trades (`thinN`). The synthetic
nulls are declared in `SYNTHETIC` below. Every null is mean-zero by construction.

**Section 2, the P comparison** (`extended.p_bound`): the judged block's paired series from `user_journey.csv` section
`start` (P-16 against P-14 on both arms; each design's point arm against its verdict arm), centred or raw, flipped by
blocks of 21, 63 and 126 starts; and the synthetic nulls in `P_SYNTHETIC`. Identities first (refusing): P-14's judged P
equals `u_budget.csv`'s, and Stage 2's bootstrap as re-implemented reproduces `user_journey.csv`'s paired row. Beside
the module's candidates, `bm63c`: the batch-means t with its critical value calibrated on the declared nulls -- stage 1
takes, at each level, the largest (1 - level) quantile of bm63's t over the real and realistic synthetic nulls; stage 2
reports its rejection rate on fresh replications of every null (`default_rng([seed, 1000 + null index])`).

**Replications** (`--reps`, default 200,000 for the t-type statistics): at the smallest family level, 0.05/240, a
binomial test that separates the nominal rate from twice it (two-sided 5 %, power 90 %) needs about
(1.96 + 1.28 sqrt 2)^2 / level = 68,000 replications; at 0.05/132, 37,600. 200,000 leaves margin: the expected count
at 0.05/240 is 42 and its 95 % interval excludes twice the nominal. The bootstrap (`--boot-reps`) is costlier per
replication (96,000 draws each) and runs on the nulls in `BOOT_NULLS` only.

**Seeds** (Q-16's, fixed in the brief): 20261915 the lift's real nulls (flips, thinning), 20261916 its synthetic nulls,
20261917 the P comparison's real nulls, 20261918 its synthetic nulls; `extended.lift_bound` holds 20261913 (fixed-b
table) and 20261914 (the bootstrap's resample matrix); `extended.p_bound` 20261919. Each null draws from
`default_rng([seed, null index])`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path

for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

from extended import lift_bound as LB  # noqa: E402
from extended.procmem import working_set_mb  # noqa: E402

SEED_LIFT_REAL = 20261915
SEED_LIFT_SYN = 20261916
SEED_P_REAL = 20261917
SEED_P_SYN = 20261918

JUDGED_FIRST = "2024-01-02"
DEV_LAST = "2026-07-16"
DAYS_FILE = ROOT / "vendor" / "stage2" / "data" / "atlas" / "A1" / "days.parquet"
JOURNEY_FILE = ROOT / "vendor" / "stage2" / "results" / "user_journey.csv"
BUDGET_FILE = ROOT / "vendor" / "stage2" / "results" / "u_budget.csv"

FAMILY_LEVELS = [LB.family_level(k) for k in LB.K_RANGE]
EXTRA_LEVELS = [0.001, 0.005, 0.025]
LEVELS = FAMILY_LEVELS + EXTRA_LEVELS
FAST = ("t21e", "t21w", "t42w", "t63w", "hac21", "cons")
SIZES = (200, 500, 1000, 2000, 5000)
R_SCHED = 1.5                        # the fresh Combine's R (FV3-C's config, `state_policy.fresh.combine_rr`)
STRICT_GAP = 5                       # minutes from a trade's exit to the next offer (P-14's strict rule)
BATCH = 10_000

#: the declared synthetic nulls for the lift: name -> (count model, outcome model, parameters); every one mean zero.
#: `icc` is the latent session effect's share of a trade's latent variance (0.35 gives a binary pair difference an
#: intra-session correlation near 0.22; P-16's offered pairs show 0.19 at 1R and 0.35 at 3R); `ar` the session effect's
#: lag-1 autocorrelation across sessions (P-16's session means: about 0.03); `regime` the share of the session effect
#: that is one value per 63-session block, random phase (P-16's by-year spread of the long-minus-short mean, about
#: +-0.013 against a session-effect sd near 0.2, is a share near 0.005). Rows marked stress go well past the data.
SYNTHETIC = {
    "iid":         dict(counts="poisson", outcome="tern", icc=0.0, ar=0.0, regime=0.0),
    "cluster":     dict(counts="negbin", outcome="sign", icc=0.35, ar=0.0, regime=0.0),
    "cluster_ar1": dict(counts="negbin", outcome="sign", icc=0.35, ar=0.1, regime=0.0),
    "cluster_ar5": dict(counts="negbin", outcome="sign", icc=0.35, ar=0.5, regime=0.0),      # stress
    "regime01":    dict(counts="negbin", outcome="sign", icc=0.35, ar=0.0, regime=0.01),
    "regime03":    dict(counts="negbin", outcome="sign", icc=0.35, ar=0.0, regime=0.03),     # stress
    "regime10":    dict(counts="negbin", outcome="sign", icc=0.35, ar=0.0, regime=0.10),     # stress
    "volclust":    dict(counts="negbin", outcome="gauss", icc=0.35, ar=0.1, regime=0.0),
    "skew":        dict(counts="negbin", outcome="skew", icc=0.0, ar=0.0, regime=0.0),
}


def _sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    except Exception:                                   # noqa: BLE001
        return ""


def _dirty() -> bool:
    try:
        return bool(subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True,
                                   text=True).stdout.strip())
    except Exception:                                   # noqa: BLE001
        return True


# ================================================================================================ section 1: the lift


def judged_calendar() -> list[str]:
    d = pd.read_parquet(DAYS_FILE)  # one-door-exempt: E-035 -- this repository's own derived file (P-16's registered pairs or its day calendar), not Stage 2's bars or walks
    ds = sorted(str(x) for x in d["date"])
    return [x for x in ds if JUDGED_FIRST <= x <= DEV_LAST]


def real_streams(pairs_path: Path) -> tuple[dict, int, dict]:
    """{stream: (session ordinals, v_win1, v_net3, coin)} on the judged block, the number of sessions, the inputs."""
    meta_p = Path(pairs_path).with_suffix(".json")
    meta = json.loads(meta_p.read_text(encoding="utf-8"))
    if not str(meta.get("identity", "")).startswith("HOLDS") or meta.get("parquet_sha256") != _sha(pairs_path):
        raise SystemExit(f"REFUSED: {pairs_path} is not the identity-checked output of scripts/q16_p16_pairs.py")
    cal = judged_calendar()
    pos = {d: i for i, d in enumerate(cal)}
    p = pd.read_parquet(pairs_path, columns=["date", "slot", "coin", "kl_1", "ks_1", "rl_3", "rs_3",  # one-door-exempt: E-035 -- this repository's own derived file (P-16's registered pairs or its day calendar), not Stage 2's bars or walks
                                             f"xl_{R_SCHED:g}", f"xs_{R_SCHED:g}"])
    p = p[(p["date"].astype(str) >= JUDGED_FIRST) & (p["date"].astype(str) <= DEV_LAST)].copy()
    p["date"] = p["date"].astype(str)
    if not p["date"].isin(pos).all():
        raise SystemExit("REFUSED: a judged trade's date is not in A1's calendar")
    p = p.sort_values(["date", "slot"], kind="stable").reset_index(drop=True)
    s = p["date"].map(pos).to_numpy(np.int64)
    win1 = 0.5 * ((p["kl_1"] == 1).astype(float) - (p["ks_1"] == 1).astype(float)).to_numpy()
    net3 = 0.5 * (p["rl_3"].astype(float) - p["rs_3"].astype(float)).to_numpy()
    coin = p["coin"].astype(int).to_numpy()
    out = {"offered": (s, win1, net3, coin)}
    # the re-entry-when-flat schedule: per session, the first offer, then the first offer at least STRICT_GAP minutes
    # after the coin side's exit at R_SCHED
    xl = p[f"xl_{R_SCHED:g}"].to_numpy(int)
    xs = p[f"xs_{R_SCHED:g}"].to_numpy(int)
    slot = p["slot"].to_numpy(int)
    take = np.zeros(len(p), dtype=bool)
    free, cur = -1, -1
    for i in range(len(p)):
        if s[i] != cur:
            cur, free = s[i], -1
        if slot[i] >= free:
            take[i] = True
            free = (xl[i] if coin[i] > 0 else xs[i]) + STRICT_GAP
    out["taken"] = tuple(a[take] for a in (s, win1, net3, coin))
    rng = np.random.default_rng([SEED_LIFT_REAL, 999])
    for n in SIZES:
        idx = np.sort(rng.choice(len(p), size=n, replace=False))
        out[f"thin{n}"] = tuple(a[idx] for a in (s, win1, net3, coin))
    info = {"pairs": str(pairs_path), "pairs_sha256": meta["parquet_sha256"], "trades_sha256": meta["trades_sha256"],
            "days_sha256": _sha(DAYS_FILE), "judged_sessions": len(cal), "judged_offered": int(len(p)),
            "taken": int(take.sum()), "taken_per_session": float(take.sum() / len(cal))}
    return out, len(cal), info


def _flip_signs(rng, n: int, L: int, reps: int) -> np.ndarray:
    """(n, reps) signs: one fair sign per block of L consecutive sessions, the blocks' phase random per replication."""
    phase = rng.integers(0, L, size=reps)
    nb = (n + L) // L + 1
    sg = rng.choice(np.array([-1.0, 1.0]), size=(nb, reps))
    fid = (np.arange(n)[:, None] + phase[None, :]) // L
    return np.take_along_axis(sg, fid, axis=0)


def real_null_specs(streams: dict) -> list[dict]:
    specs = []
    for st in streams:
        for val in ("win1", "net3"):
            for L in (1, 5, 21, 63):
                specs.append({"null": f"real:{st}:{val}:persist{L}", "kind": "real", "stream": st, "value": val,
                              "side": "persist", "L": L})
            specs.append({"null": f"real:{st}:{val}:coin", "kind": "real", "stream": st, "value": val, "side": "coin",
                          "L": 1})
    return specs


def real_batch(spec: dict, streams: dict, n: int, rng, reps: int):
    s, win1, net3, coin = streams[spec["stream"]]
    v = win1 if spec["value"] == "win1" else net3
    if spec["side"] == "coin":
        v = coin * v
    V = np.bincount(s, weights=v, minlength=n)
    N = np.bincount(s, minlength=n).astype(float)
    sg = _flip_signs(rng, n, int(spec["L"]), reps)
    return V[:, None] * sg, np.repeat(N[:, None], reps, axis=1)


def syn_batch(spec: dict, n: int, rng, reps: int):
    """One batch of a declared synthetic null's session sums (n, reps) and counts."""
    p = SYNTHETIC[spec["model"]]
    lam = float(spec["trades"]) / n
    if p["counts"] == "poisson":
        N = rng.poisson(lam, size=(n, reps)).astype(float)
    else:                                                # negative binomial, size 1 (variance lam + lam^2)
        N = rng.negative_binomial(1.0, 1.0 / (1.0 + lam), size=(n, reps)).astype(float)
    icc, ar, reg = p["icc"], p["ar"], p["regime"]
    a = np.zeros((n, reps))
    if icc > 0:
        z = rng.standard_normal((n, reps))
        if ar > 0:
            e = z.copy()
            for j in range(1, n):
                e[j] = ar * e[j - 1] + math.sqrt(1 - ar * ar) * z[j]
            z = e
        if reg > 0:
            L = 63
            phase = rng.integers(0, L, size=reps)
            nb = (n + L) // L + 1
            rz = rng.standard_normal((nb, reps))
            fid = (np.arange(n)[:, None] + phase[None, :]) // L
            z = math.sqrt(1 - reg) * z + math.sqrt(reg) * np.take_along_axis(rz, fid, axis=0)
        a = math.sqrt(icc) * z
    Ni = N.astype(np.int64)
    if p["outcome"] == "tern":                          # +-1/2 with 0.47 each, 0 with 0.06
        k = rng.binomial(Ni, 0.94)
        up = rng.binomial(k, 0.5)
        S = 0.5 * (2 * up - k)
    elif p["outcome"] == "sign":                        # 1/2 sign(a + e), e ~ N(0, 1 - icc): a probit cluster
        pr = stats.norm.cdf(a / math.sqrt(1 - icc))
        up = rng.binomial(Ni, pr)
        S = 0.5 * (2 * up - Ni)
    elif p["outcome"] == "gauss":                       # continuous (net R like), clustered, volatility clustered
        h = np.zeros((n, reps))
        eta = rng.standard_normal((n + 100, reps))
        hh = np.zeros(reps)
        for j in range(n + 100):
            hh = 0.97 * hh + 0.25 * eta[j]
            if j >= 100:
                h[j - 100] = hh
        vol = np.exp(h / 2)
        S = vol * (N * a + np.sqrt(N * (1 - icc)) * rng.standard_normal((n, reps)))
    elif p["outcome"] == "skew":                        # +1/2 with 0.8, -2 with 0.2: mean 0, rare large losses
        k = rng.binomial(Ni, 0.8)
        S = 0.5 * k - 2.0 * (Ni - k)
    else:
        raise ValueError(p["outcome"])
    return S.astype(float), N


def syn_specs() -> list[dict]:
    return [{"null": f"syn:{m}:{t}", "kind": "syn", "model": m, "trades": t} for m in SYNTHETIC for t in SIZES]


def _calibrate(specs, gen, reps: int, seed: int, methods, log) -> tuple[list[dict], list[dict]]:
    size_rows, power_rows = [], []
    for ni, spec in enumerate(specs):
        t0 = time.time()
        rng = np.random.default_rng([seed, ni])
        rej = {(m, a): 0 for m in methods for a in LEVELS}
        mdl = {(m, a): [] for m in methods for a in (FAMILY_LEVELS[0], FAMILY_LEVELS[-1])}
        ntr, done = [], 0
        while done < reps:
            r = min(BATCH, reps - done)
            S, N = gen(spec, rng, r)
            ntr.append(N.sum(axis=0))
            for m in methods:
                rj, md = LB.many_levels(m, S, N, LEVELS)
                for i, a in enumerate(LEVELS):
                    rej[(m, a)] += int(rj[i].sum())
                mdl[(m, FAMILY_LEVELS[0])].append(md[0])
                mdl[(m, FAMILY_LEVELS[-1])].append(md[len(FAMILY_LEVELS) - 1])
            done += r
        nt = np.concatenate(ntr)
        for (m, a), k in rej.items():
            lo, hi = LB.clopper_pearson(k, reps)
            size_rows.append({**{k_: v for k_, v in spec.items()}, "method": m, "level": a,
                              "k": next((kk for kk in LB.K_RANGE if abs(LB.family_level(kk) - a) < 1e-15), None),
                              "reps": reps, "rejections": k, "rate": k / reps, "ci_lo": lo, "ci_hi": hi,
                              "ratio": (k / reps) / a, "trades_mean": float(nt.mean())})
        for (m, a), parts in mdl.items():
            d = np.concatenate(parts)
            power_rows.append({**{k_: v for k_, v in spec.items()}, "method": m, "level": a,
                               "k": next((kk for kk in LB.K_RANGE if abs(LB.family_level(kk) - a) < 1e-15), None),
                               "reps": reps, "mdl50": float(np.quantile(d, 0.5)), "mdl80": float(np.quantile(d, 0.8)),
                               "trades_mean": float(nt.mean())})
        k11 = {m: rej[(m, FAMILY_LEVELS[0])] for m in methods}
        log(f"  {spec['null']}: rejections at 0.05/132 of {reps}: {k11}; {time.time() - t0:.0f} s, "
            f"ws {working_set_mb():.0f} MB")
    return size_rows, power_rows


#: the nulls the bootstrap is calibrated on (its cost: 96,000 draws a replication)
BOOT_NULLS = ("real:taken:win1:persist1", "real:taken:net3:persist1", "real:taken:win1:persist21",
              "real:offered:win1:persist21", "real:thin200:win1:coin", "real:thin200:net3:persist1",
              "real:thin1000:win1:persist5", "real:thin5000:net3:persist21", "syn:cluster:1000", "syn:skew:500",
              "syn:regime03:2000", "syn:cluster_ar5:5000")


def _boot(specs, gens, reps: int, log, boot_batch: int = 16) -> list[dict]:
    draws = LB.draws_for(min(FAMILY_LEVELS))
    rows = []
    for ni, spec in specs:
        t0 = time.time()
        rng = np.random.default_rng([spec["seed"], ni])
        rej = {a: 0 for a in LEVELS}
        rej_t = {a: 0 for a in LEVELS}
        ratio = []
        done = 0
        while done < reps:
            r = min(boot_batch, reps - done)
            S, N = gens[spec["kind"]](spec, rng, r)
            est, se, df = LB.t_stats(S, N, block=21, weight="trades")
            crit = LB.cbb_crit_many(S, N, levels=LEVELS, block=21, draws=draws)
            for i, a in enumerate(LEVELS):
                rej[a] += int(((est - crit[i] * se) > 0).sum())
                tc = stats.t.ppf(1 - a, df)
                rej_t[a] += int(((est - tc * se) > 0).sum())
            ratio.append(crit[0] / stats.t.ppf(1 - FAMILY_LEVELS[0], df))
            done += r
        rt = np.concatenate(ratio)
        for a in LEVELS:
            lo, hi = LB.clopper_pearson(rej[a], reps)
            rows.append({"null": spec["null"], "method": "cbb21", "level": a,
                         "k": next((kk for kk in LB.K_RANGE if abs(LB.family_level(kk) - a) < 1e-15), None),
                         "reps": reps, "draws": draws, "rejections": rej[a], "rate": rej[a] / reps, "ci_lo": lo,
                         "ci_hi": hi, "ratio": rej[a] / reps / a, "t21w_same_reps": rej_t[a],
                         "crit_over_t_p10": float(np.quantile(rt, 0.1)), "crit_over_t_p50": float(np.quantile(rt, 0.5)),
                         "crit_over_t_p90": float(np.quantile(rt, 0.9))})
        log(f"  boot {spec['null']}: {rej[FAMILY_LEVELS[0]]} of {reps} at 0.05/132 (t21w on the same: "
            f"{rej_t[FAMILY_LEVELS[0]]}); crit/t median {np.median(rt):.3f}; {time.time() - t0:.0f} s")
    return rows


def lift_part(a, log) -> dict:
    info: dict = {}
    specs_syn = syn_specs()
    n = 657
    gens = {"syn": lambda spec, rng, r: syn_batch(spec, n, rng, r)}
    rows_s, rows_p = [], []
    streams = None
    if not a.synthetic_only:
        streams, n_real, info = real_streams(Path(a.pairs))
        if n_real != n:
            raise SystemExit(f"REFUSED: the judged calendar has {n_real} sessions, not {n}")
        gens["real"] = lambda spec, rng, r: real_batch(spec, streams, n, rng, r)
        specs_real = real_null_specs(streams)
        log(f"real streams: { {k: int(len(v[0])) for k, v in streams.items()} }; {info}")
        s1, p1 = _calibrate(specs_real, gens["real"], a.reps, SEED_LIFT_REAL, FAST, log)
        rows_s += s1
        rows_p += p1
    s2, p2 = _calibrate(specs_syn, gens["syn"], a.reps, SEED_LIFT_SYN, FAST, log)
    rows_s += s2
    rows_p += p2
    pd.DataFrame(rows_s).to_csv(Path(a.out) / "lift_size.csv", index=False)
    pd.DataFrame(rows_p).to_csv(Path(a.out) / "lift_power.csv", index=False)
    if a.boot_reps > 0:
        allspecs = ([] if a.synthetic_only else real_null_specs(streams)) + specs_syn
        idx = {s["null"]: i for i, s in enumerate(allspecs)}
        chosen = []
        for name in BOOT_NULLS:
            if name in idx:
                sp = dict(allspecs[idx[name]])
                sp["seed"] = SEED_LIFT_SYN if sp["kind"] == "syn" else SEED_LIFT_REAL
                chosen.append((10_000 + idx[name], sp))
        if a.synthetic_only and not chosen:
            sp = dict(specs_syn[0])
            sp["seed"] = SEED_LIFT_SYN
            chosen = [(10_000, sp)]
        brows = _boot(chosen, gens, a.boot_reps, log)
        pd.DataFrame(brows).to_csv(Path(a.out) / "lift_boot.csv", index=False)
    return info


# ================================================================================================ section 2: P


P_PAIRS = {"p16v-p14v": (("p16", "verdict"), ("p14", "verdict")), "p16p-p14p": (("p16", "point"), ("p14", "point")),
           "p14p-p14v": (("p14", "point"), ("p14", "verdict")), "p16p-p16v": (("p16", "point"), ("p16", "verdict"))}
P_FAST = ("bm63", "bm126", "obm63", "obm126", "ft63", "pcons")
P_STRESS = ("syn:path_edge",)
P_BATCH = 4000
#: the declared synthetic nulls for P (n = 595 starts): Gaussian moving averages, and the red team's structural null --
#: two exchangeable designs' daily P&L (common and own shocks, shared volatility clustering), each start ahead at month
#: m when its cumulative P&L over 21 m sessions beats a fee offset (rt_cal.py's 'path': mu 0.21, F 4.98, common 0.3,
#: log-volatility AR 0.97 sd 0.25); 'path_slow' raises the volatility's persistence to 0.995 (same stationary sd);
#: 'path_edge' adds a mean-zero difference in the two designs' daily edge, AR(1) 0.995 across sessions (sd 0.10), so
#: the paired series is dependent well past a month-3 window (stress).
P_SYNTHETIC = {"ma21": dict(kind="ma", q=21), "ma63": dict(kind="ma", q=63),
               "path": dict(kind="path", phi=0.97, edge=0.0), "path_slow": dict(kind="path", phi=0.995, edge=0.0),
               "path_edge": dict(kind="path", phi=0.97, edge=0.10)}


def p_real_specs():
    out = []
    for nm in P_PAIRS:
        for form in ("centred", "raw"):
            for L in (21, 63, 126):
                out.append({"null": f"real:{nm}:{form}:flip{L}", "kind": "real", "pair": nm, "form": form, "L": L})
    return out


def p_syn_batch(spec, rng, reps, n=595):
    q = P_SYNTHETIC[spec["model"]]
    if q["kind"] == "ma":
        e = rng.standard_normal((n + q["q"] - 1, reps))
        c = np.cumsum(np.vstack([np.zeros((1, reps)), e]), axis=0)
        return (c[q["q"]:] - c[:-q["q"]])[:n] / math.sqrt(q["q"])
    T = n + 63
    h = np.zeros(reps)
    vol = np.empty((T, reps))
    eta = rng.standard_normal((T + 100, reps))
    sd = 0.25 * math.sqrt((1 - 0.97 ** 2) / (1 - q["phi"] ** 2))
    for t in range(T + 100):
        h = q["phi"] * h + sd * eta[t]
        if t >= 100:
            vol[t - 100] = np.exp(h / 2)
    com = rng.standard_normal((T, reps))
    edge = np.zeros((T, reps))
    if q["edge"] > 0:
        z = rng.standard_normal((T + 500, reps))
        e = np.zeros(reps)
        for t in range(T + 500):
            e = 0.995 * e + math.sqrt(1 - 0.995 ** 2) * z[t]
            if t >= 500:
                edge[t - 500] = q["edge"] * e
    A = []
    for i in (0, 1):
        pnl = 0.21 + (0.5 if i == 0 else -0.5) * edge + vol * (math.sqrt(0.3) * com
                                                                + math.sqrt(0.7) * rng.standard_normal((T, reps)))
        c = np.vstack([np.zeros((1, reps)), np.cumsum(pnl, axis=0)])
        s_ = np.arange(n)
        A.append(sum(((c[s_ + 21 * k] - c[s_]) - 4.98 > 0).astype(float) for k in (1, 2, 3)) / 3.0)
    return A[0] - A[1]


def p_part(a, log) -> dict:
    from extended import p_bound as PB

    t0 = time.time()
    starts = PB.load_starts(JOURNEY_FILE)
    j14 = PB.judged(starts[("p14", "verdict")])
    reg = PB.registered_p14_judged(BUDGET_FILE)
    if len(j14) != 595 or abs(float(j14.mean()) - reg) > 5e-7:
        raise SystemExit(f"REFUSED: P-14's judged P {float(j14.mean())!r} over {len(j14)} starts is not the families' "
                         f"{reg!r}")
    lo, hi, nn = PB.paired_row_identity()
    row = PB.registered_paired_row()
    if abs(lo - float(row["lo"])) > 1e-9 or abs(hi - float(row["hi"])) > 1e-9:
        raise SystemExit("REFUSED: the Stage 2 line's bootstrap does not reproduce user_journey.csv's paired row")
    series = {}
    for nm, (x, y) in P_PAIRS.items():
        series[nm] = PB.paired(PB.judged(starts[x]), PB.judged(starts[y]))
    info = {"journey_sha256": _sha(JOURNEY_FILE), "budget_sha256": _sha(BUDGET_FILE), "p14_judged_P": float(j14.mean()),
            "identity": "HOLDS: P-14's judged P = u_budget.csv's; the paired row's lo/hi re-derived",
            "series": {k: {"n": int(len(v)), "mean": float(v.mean()), "sd": float(v.std(ddof=1))}
                       for k, v in series.items()}}
    log(f"P: identities hold; {info['series']}; {time.time() - t0:.0f} s")

    def gen(spec, rng, r):
        if spec["kind"] == "real":
            d = series[spec["pair"]]
            d = d - d.mean() if spec["form"] == "centred" else d
            return d[:, None] * _flip_signs(rng, len(d), int(spec["L"]), r)
        return p_syn_batch(spec, rng, r)

    specs = p_real_specs() + [{"null": f"syn:{m}", "kind": "syn", "model": m} for m in P_SYNTHETIC]
    if a.synthetic_only:
        specs = [s_ for s_ in specs if s_["kind"] == "syn"]
    size_rows, power_rows = [], []
    tstat = {}
    allm = P_FAST + ("d621",)
    for ni, spec in enumerate(specs):
        t1 = time.time()
        rng = np.random.default_rng([SEED_P_REAL if spec["kind"] == "real" else SEED_P_SYN, ni])
        rej = {(m, al): 0 for m in allm for al in LEVELS}
        mdd = {(m, al): [] for m in allm for al in (FAMILY_LEVELS[0], FAMILY_LEVELS[-1])}
        done, done_d = 0, 0
        tb = []
        while done < a.reps:
            r = min(P_BATCH, a.reps - done)
            D = gen(spec, rng, r)
            e_, s_, _ = PB.batch_t(D, batches=D.shape[0] // 63)
            with np.errstate(invalid="ignore", divide="ignore"):
                tb.append(np.where(s_ > 0, e_ / s_, -np.inf))
            ms = P_FAST + (("d621",) if done_d < a.d621_reps else ())
            for m in ms:
                rj, md = PB.many_levels(m, D, LEVELS)
                for i_, al in enumerate(LEVELS):
                    rej[(m, al)] += int(rj[i_].sum())
                mdd[(m, FAMILY_LEVELS[0])].append(md[0])
                mdd[(m, FAMILY_LEVELS[-1])].append(md[len(FAMILY_LEVELS) - 1])
            if done_d < a.d621_reps:
                done_d += r
            done += r
        for (m, al), k in rej.items():
            R = done_d if m == "d621" else done
            lo_, hi_ = LB.clopper_pearson(k, R)
            size_rows.append({**spec, "method": m, "level": al,
                              "k": next((kk for kk in LB.K_RANGE if abs(LB.family_level(kk) - al) < 1e-15), None),
                              "reps": R, "rejections": k, "rate": k / R, "ci_lo": lo_, "ci_hi": hi_,
                              "ratio": k / R / al})
        for (m, al), parts in mdd.items():
            d = np.concatenate(parts)
            power_rows.append({**spec, "method": m, "level": al,
                               "k": next((kk for kk in LB.K_RANGE if abs(LB.family_level(kk) - al) < 1e-15), None),
                               "reps": len(d), "mdd50": float(np.quantile(d, 0.5)),
                               "mdd80": float(np.quantile(d, 0.8))})
        tstat[spec["null"]] = np.concatenate(tb)
        k11 = {m: rej[(m, FAMILY_LEVELS[0])] for m in allm}
        log(f"  {spec['null']}: rejections at 0.05/132 ({a.reps}; d621 of {done_d}): {k11}; {time.time() - t1:.0f} s, "
            f"ws {working_set_mb():.0f} MB")

    # `bm63c`, two stages: (1) its critical value at each level is the largest (1 - level) quantile of bm63's t over
    # the real nulls and the realistic synthetic ones (stage 1: the replications above); (2) it is validated on FRESH
    # replications of every null (rng [seed, 1000 + null index]) -- the rates reported are stage 2's only
    calib = [nl for nl in tstat if nl.startswith("real:") or (nl.startswith("syn:") and nl not in P_STRESS)]
    cstar = {al: max(float(np.quantile(tstat[nl], 1.0 - al, method="higher")) for nl in calib) for al in LEVELS}
    crit_rows = [{"level": al, "k": next((kk for kk in LB.K_RANGE if abs(LB.family_level(kk) - al) < 1e-15), None),
                  "critical": c, "t8": float(stats.t.ppf(1 - al, 8)), "ratio_to_t8": c / float(stats.t.ppf(1 - al, 8)),
                  "argmax_null": max(calib, key=lambda nl: float(np.quantile(tstat[nl], 1.0 - al, method="higher"))),
                  "calibration_nulls": len(calib), "reps_each": a.reps} for al, c in cstar.items()]
    pd.DataFrame(crit_rows).to_csv(Path(a.out) / "p_bm63c_critical.csv", index=False)
    log(f"  bm63c critical values (stage 1): { {round(al, 7): round(c, 3) for al, c in cstar.items()} }")
    for ni, spec in enumerate(specs):
        t1 = time.time()
        rng = np.random.default_rng([SEED_P_REAL if spec["kind"] == "real" else SEED_P_SYN, 1000 + ni])
        rej = {al: 0 for al in LEVELS}
        mdd = {al: [] for al in (FAMILY_LEVELS[0], FAMILY_LEVELS[-1])}
        done = 0
        while done < a.reps:
            r = min(P_BATCH, a.reps - done)
            D = gen(spec, rng, r)
            e_, s_, _ = PB.batch_t(D, batches=D.shape[0] // 63)
            for al in LEVELS:
                lo_ = e_ - cstar[al] * s_
                rej[al] += int(((e_ > 0) & (lo_ > 0)).sum())
                if al in mdd:
                    mdd[al].append(np.maximum(-e_, -lo_))
            done += r
        for al, k in rej.items():
            lo_, hi_ = LB.clopper_pearson(k, done)
            size_rows.append({**spec, "method": "bm63c", "level": al,
                              "k": next((kk for kk in LB.K_RANGE if abs(LB.family_level(kk) - al) < 1e-15), None),
                              "reps": done, "rejections": k, "rate": k / done, "ci_lo": lo_, "ci_hi": hi_,
                              "ratio": k / done / al, "stage": "validation (fresh replications)"})
        for al, parts in mdd.items():
            d = np.concatenate(parts)
            power_rows.append({**spec, "method": "bm63c", "level": al,
                               "k": next((kk for kk in LB.K_RANGE if abs(LB.family_level(kk) - al) < 1e-15), None),
                               "reps": len(d), "mdd50": float(np.quantile(d, 0.5)), "mdd80": float(np.quantile(d, 0.8))})
        log(f"  bm63c validation {spec['null']}: {rej[FAMILY_LEVELS[0]]} of {done} at 0.05/132; {time.time() - t1:.0f} s")
    pd.DataFrame(size_rows).to_csv(Path(a.out) / "p_size.csv", index=False)
    pd.DataFrame(power_rows).to_csv(Path(a.out) / "p_power.csv", index=False)
    info["bm63c_critical"] = {str(al): c for al, c in cstar.items()}
    return info


# ================================================================================================ the two-sample forms
#
# E-023: a filter keeping the coin's side, against its placebo-selection twin (the selected offers' own outcome minus
# every offer's: the expectation of a random filter firing on the same share); E-022: F-02's C1' (the level fills' lift
# minus the placebo fills'). Both are `extended.lift_bound.diff_*`. Real data: P-16's offered candidates on the judged
# block (the pairs above). Seeds: derived from 20261915 (`default_rng([20261915, 5000 + i])` for the selections,
# `[20261915, 7000 + i]` for C1', `[20261915, 9000 + i]` for C1''s subsets).

SHARES = (0.02, 0.05, 0.10, 0.25, 0.50)
SEL_MODELS = ("offer", "window", "session", "block5", "block21", "block63")
DIFF_FAST = ("t21w", "t42w", "t63w", "cons")


def judged_offers(pairs_path: Path):
    """Every judged offer in (session, slot) order: session ordinal, the coin side's own win at 1R and net R at 3R, the
    pair differences (long minus short)/2 at those, the coin."""
    meta = json.loads(Path(pairs_path).with_suffix(".json").read_text(encoding="utf-8"))
    if not str(meta.get("identity", "")).startswith("HOLDS") or meta.get("parquet_sha256") != _sha(pairs_path):
        raise SystemExit(f"REFUSED: {pairs_path} is not the identity-checked output of scripts/q16_p16_pairs.py")
    cal = judged_calendar()
    pos = {d: i for i, d in enumerate(cal)}
    p = pd.read_parquet(pairs_path, columns=["date", "slot", "coin", "kl_1", "ks_1", "rl_3", "rs_3"])  # one-door-exempt: E-035 -- this repository's own derived file (P-16's registered pairs or its day calendar), not Stage 2's bars or walks
    p["date"] = p["date"].astype(str)
    p = p[(p["date"] >= JUDGED_FIRST) & (p["date"] <= DEV_LAST)].sort_values(["date", "slot"], kind="stable")
    s = p["date"].map(pos).to_numpy(np.int64)
    c = p["coin"].astype(int).to_numpy()
    wl, ws = (p["kl_1"] == 1).to_numpy(float), (p["ks_1"] == 1).to_numpy(float)
    rl, rs = p["rl_3"].to_numpy(float), p["rs_3"].to_numpy(float)
    return {"s": s, "y_win1": np.where(c > 0, wl, ws), "y_net3": np.where(c > 0, rl, rs),
            "v_win1": 0.5 * (wl - ws), "v_net3": 0.5 * (rl - rs), "coin": c, "n": len(cal)}


def _sel_batch(model, share, O, yname, rng, reps):
    """(A, B): the selected offers' outcome sums and counts per session, (n, reps), for a selection independent of the
    outcomes."""
    n, s, y = O["n"], O["s"], O[yname]
    M = np.bincount(s, minlength=n).astype(np.int64)
    C = np.bincount(s, weights=y, minlength=n)
    if model == "offer":                                        # each offer independently; binary outcomes only
        W = C.astype(np.int64)
        B = rng.binomial(np.repeat(M[:, None], reps, 1), share)
        A = rng.hypergeometric(np.repeat(W[:, None], reps, 1), np.repeat((M - W)[:, None], reps, 1), B)
        return A.astype(float), B.astype(float)
    if model == "window":                                       # a contiguous run of offers each session, random start
        L = np.maximum(1, np.rint(share * M)).astype(np.int64) * (M > 0)
        off = np.r_[0, np.cumsum(2 * M)[:-1]]
        y2 = np.concatenate([np.r_[y[s == j], y[s == j]] for j in range(n)])
        cs = np.r_[0.0, np.cumsum(y2)]
        a = np.floor(rng.random((n, reps)) * np.maximum(M, 1)[:, None]).astype(np.int64)
        lo = off[:, None] + a
        A = cs[lo + L[:, None]] - cs[lo]
        B = np.repeat(L[:, None].astype(float), reps, 1)
        return A, B
    if model == "session":
        f = rng.random((n, reps)) < share
    else:
        Lb = int(model[5:])
        phase = rng.integers(0, Lb, size=reps)
        nb = (n + Lb) // Lb + 1
        fb = rng.random((nb, reps)) < share
        f = np.take_along_axis(fb, (np.arange(n)[:, None] + phase[None, :]) // Lb, axis=0)
    return f * C[:, None], f * M[:, None].astype(float)


def select_part(a, log) -> dict:
    O = judged_offers(Path(a.pairs))
    n = O["n"]
    C = {v: np.bincount(O["s"], weights=O[f"y_{v}"], minlength=n) for v in ("win1", "net3")}
    M = np.bincount(O["s"], minlength=n).astype(float)
    rows_s, rows_p = [], []
    specs = [(m, sh, v) for m in SEL_MODELS for sh in SHARES for v in ("win1", "net3") if not (m == "offer" and v == "net3")]
    for ni, (model, share, v) in enumerate(specs):
        t1 = time.time()
        rng = np.random.default_rng([SEED_LIFT_REAL, 5000 + ni])
        rej = {(m, al): 0 for m in DIFF_FAST for al in LEVELS}
        done, keepA, keepB = 0, [], []
        while done < a.reps:
            r = min(BATCH, a.reps - done)
            A, B = _sel_batch(model, share, O, f"y_{v}", rng, r)
            Cr, Mr = C[v][:, None], M[:, None]                      # broadcast: the population is fixed
            for m in DIFF_FAST:
                rj, _ = LB.diff_many_levels(m, A, B, Cr, Mr, LEVELS, df_rule=a.diff_df)
                for i_, al in enumerate(LEVELS):
                    rej[(m, al)] += int(rj[i_].sum())
            if done < a.power_reps:
                keepA.append(A[:, : a.power_reps - done])
                keepB.append(B[:, : a.power_reps - done])
            done += r
        null = f"select:{model}:{share:g}:{v}"
        for (m, al), k in rej.items():
            lo_, hi_ = LB.clopper_pearson(k, done)
            rows_s.append({"null": null, "form": "placebo-selection", "model": model, "share": share, "value": v,
                           "method": m, "level": al,
                           "k": next((kk for kk in LB.K_RANGE if abs(LB.family_level(kk) - al) < 1e-15), None),
                           "reps": done, "rejections": k, "rate": k / done, "ci_lo": lo_, "ci_hi": hi_,
                           "ratio": k / done / al})
        # power by firing share: the selected trades' outcomes shifted by d (a filter that picks better trades);
        # the detectable difference is the selected mean minus the twin's, d (1 - selected share of offers)
        A0, B0 = np.concatenate(keepA, axis=1), np.concatenate(keepB, axis=1)
        R0 = A0.shape[1]
        Cr, Mr = C[v][:, None], M[:, None]
        e0, se0, _ = LB.diff_stats(A0, B0, Cr, Mr, block=21, df_rule=a.diff_df)
        unit = float(np.nanmedian(se0))
        pi = float(np.nanmean(B0.sum(axis=0) / M.sum()))
        grid = unit * np.geomspace(0.5, 40.0, 28)
        for m in ("t21w", "cons"):
            for al in (FAMILY_LEVELS[0], FAMILY_LEVELS[-1]):
                pw = []
                for dd in grid:
                    rj, _ = LB.diff_many_levels(m, A0 + dd * B0, B0, Cr + dd * B0, Mr, [al], df_rule=a.diff_df)
                    pw.append(float(rj[0].mean()))
                pw = np.maximum.accumulate(np.asarray(pw))
                d80 = float(np.interp(0.8, pw, grid)) if pw[-1] >= 0.8 else float("nan")
                rows_p.append({"null": null, "form": "placebo-selection", "model": model, "share": share, "value": v,
                               "method": m, "level": al,
                               "k": next((kk for kk in LB.K_RANGE if abs(LB.family_level(kk) - al) < 1e-15), None),
                               "reps": R0, "selected_share_of_offers": pi, "shift80": d80,
                               "difference80": d80 * (1 - pi) if np.isfinite(d80) else float("nan")})
        log(f"  {null}: at 0.05/132 of {done}: { {m: rej[(m, FAMILY_LEVELS[0])] for m in DIFF_FAST} }; "
            f"{time.time() - t1:.0f} s, ws {working_set_mb():.0f} MB")
    # F-02's C1': level fills and placebo fills (five times as many), two disjoint seeded subsets of the offers, the pair
    # difference's sign flipped by L-session blocks -- shared (one rule's side, both samples) or independent
    rng0 = np.random.default_rng([SEED_LIFT_REAL, 9000])
    specs2 = [(n1, v, side, L) for n1 in (200, 500, 1000, 2000) for v in ("win1", "net3")
              for side, L in (("shared", 1), ("shared", 21), ("shared", 63), ("indep", 1), ("indep", 21), ("indep", 63),
                              ("coin", 1))]
    subsets = {}
    for n1 in (200, 500, 1000, 2000):
        idx = rng0.permutation(len(O["s"]))[: 6 * n1]
        subsets[n1] = (np.sort(idx[:n1]), np.sort(idx[n1:]))
    for ni, (n1, v, side, L) in enumerate(specs2):
        t1 = time.time()
        rng = np.random.default_rng([SEED_LIFT_REAL, 7000 + ni])
        i1, i2 = subsets[n1]
        x = O[f"v_{v}"] * (O["coin"] if side == "coin" else 1)
        V1 = np.bincount(O["s"][i1], weights=x[i1], minlength=n)
        V2 = np.bincount(O["s"][i2], weights=x[i2], minlength=n)
        N1 = np.bincount(O["s"][i1], minlength=n).astype(float)
        N2 = np.bincount(O["s"][i2], minlength=n).astype(float)
        rej = {(m, al): 0 for m in DIFF_FAST for al in LEVELS}
        mdl = {(m, al): [] for m in DIFF_FAST for al in (FAMILY_LEVELS[0], FAMILY_LEVELS[-1])}
        done = 0
        while done < a.reps:
            r = min(BATCH, a.reps - done)
            g1 = _flip_signs(rng, n, L, r)
            g2 = g1 if side in ("shared", "coin") else _flip_signs(rng, n, L, r)
            S1, S2 = V1[:, None] * g1, V2[:, None] * g2
            N1r, N2r = N1[:, None], N2[:, None]
            for m in DIFF_FAST:
                rj, md = LB.diff_many_levels(m, S1, N1r, S2, N2r, LEVELS, df_rule=a.diff_df)
                for i_, al in enumerate(LEVELS):
                    rej[(m, al)] += int(rj[i_].sum())
                mdl[(m, FAMILY_LEVELS[0])].append(md[0])
                mdl[(m, FAMILY_LEVELS[-1])].append(md[len(FAMILY_LEVELS) - 1])
            done += r
        null = f"c1p:{n1}:{v}:{side}{L if side != 'coin' else ''}"
        for (m, al), k in rej.items():
            lo_, hi_ = LB.clopper_pearson(k, done)
            rows_s.append({"null": null, "form": "two-sample (C1')", "model": side, "share": None, "value": v,
                           "method": m, "level": al, "L": L, "level_fills": n1, "placebo_fills": 5 * n1,
                           "k": next((kk for kk in LB.K_RANGE if abs(LB.family_level(kk) - al) < 1e-15), None),
                           "reps": done, "rejections": k, "rate": k / done, "ci_lo": lo_, "ci_hi": hi_,
                           "ratio": k / done / al})
        for (m, al), parts in mdl.items():
            d = np.concatenate(parts)
            rows_p.append({"null": null, "form": "two-sample (C1')", "model": side, "value": v, "method": m,
                           "level": al, "L": L, "level_fills": n1,
                           "k": next((kk for kk in LB.K_RANGE if abs(LB.family_level(kk) - al) < 1e-15), None),
                           "reps": len(d), "difference80": float(np.quantile(d, 0.8))})
        log(f"  {null}: at 0.05/132 of {done}: { {m: rej[(m, FAMILY_LEVELS[0])] for m in DIFF_FAST} }; "
            f"{time.time() - t1:.0f} s")
    pd.DataFrame(rows_s).to_csv(Path(a.out) / "diff_size.csv", index=False)
    pd.DataFrame(rows_p).to_csv(Path(a.out) / "diff_power.csv", index=False)
    return {"pairs_sha256": _sha(Path(a.pairs)), "offers": int(len(O["s"])), "sessions": n, "diff_df": a.diff_df}


# ================================================================================================ main


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--pairs", type=Path, default=None)
    ap.add_argument("--part", choices=("lift", "p", "select", "all"), default="all")
    ap.add_argument("--power-reps", type=int, default=5_000)
    ap.add_argument("--diff-df", choices=("treated", "all"), default=LB.DIFF_DF_RULE,
                    help="the two-sample form's block count (all: the first form, kept to reproduce its failure)")
    ap.add_argument("--reps", type=int, default=200_000)
    ap.add_argument("--boot-reps", type=int, default=20_000)
    ap.add_argument("--synthetic-only", action="store_true")
    ap.add_argument("--d621-reps", type=int, default=20_000)
    ap.add_argument("--days", type=Path, default=None,
                    help="the trading-day calendar (default A1's days.parquet; a test passes a synthetic one)")
    a = ap.parse_args(argv)
    global DAYS_FILE
    if a.days is not None:
        DAYS_FILE = Path(a.days)
    out = Path(a.out).resolve()
    if (ROOT / "results").resolve() in [out, *out.parents]:
        print("REFUSED: the calibration writes no result file (Q-16's brief); choose a scratch --out")
        return 3
    out.mkdir(parents=True, exist_ok=True)
    if a.part in ("lift", "select", "all") and not a.synthetic_only and a.pairs is None:
        print("REFUSED: --pairs (scripts/q16_p16_pairs.py's output) is needed for the real nulls")
        return 3
    t0 = time.time()
    logf = open(out / f"calibrate_{a.part}.log", "a", encoding="utf-8")

    def log(msg: str) -> None:
        line = f"[{time.time() - t0:7.0f} s] {msg}"
        print(line, flush=True)
        logf.write(line + "\n")
        logf.flush()

    meta = {"script": "scripts/q16_calibrate.py", "argv": sys.argv[1:], "commit": _commit(), "dirty": _dirty(),
            "seeds": {"lift_real": SEED_LIFT_REAL, "lift_syn": SEED_LIFT_SYN, "p_real": SEED_P_REAL,
                      "p_syn": SEED_P_SYN, "fixed_b": LB.FIXED_B_SEED, "boot": LB.BOOT_SEED},
            "levels": LEVELS, "reading": "EXPLORATORY (Q-16): calibration of statistics; no design's outcome"}
    log(f"start: {meta}")
    if a.part in ("lift", "all"):
        meta["lift"] = lift_part(a, log)
    if a.part in ("p", "all"):
        meta["p"] = p_part(a, log)
    if a.part in ("select", "all"):
        meta["select"] = select_part(a, log)
    meta["seconds"] = round(time.time() - t0, 1)
    meta["peak_working_set_mb"] = round(working_set_mb(peak=True), 1)
    (out / f"calibrate_{a.part}.json").write_text(json.dumps(meta, indent=1, default=str), encoding="utf-8")
    log(f"EXIT 0; peak working set {meta['peak_working_set_mb']} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
