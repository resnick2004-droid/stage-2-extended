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

**Section 2, the P comparison** (`extended.p_bound`): see that module and `p_part` below.

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
    d = pd.read_parquet(DAYS_FILE)
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
    p = pd.read_parquet(pairs_path, columns=["date", "slot", "coin", "kl_1", "ks_1", "rl_3", "rs_3",
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


def p_part(a, log) -> dict:
    from extended import p_bound as PB

    return PB.calibrate(Path(a.out), reps=a.reps, seed_real=SEED_P_REAL, seed_syn=SEED_P_SYN, journey=JOURNEY_FILE,
                        budget=BUDGET_FILE, log=log)


# ================================================================================================ main


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--pairs", type=Path, default=None)
    ap.add_argument("--part", choices=("lift", "p", "all"), default="all")
    ap.add_argument("--reps", type=int, default=200_000)
    ap.add_argument("--boot-reps", type=int, default=20_000)
    ap.add_argument("--synthetic-only", action="store_true")
    a = ap.parse_args(argv)
    out = Path(a.out).resolve()
    if (ROOT / "results").resolve() in [out, *out.parents]:
        print("REFUSED: the calibration writes no result file (Q-16's brief); choose a scratch --out")
        return 3
    out.mkdir(parents=True, exist_ok=True)
    if a.part in ("lift", "all") and not a.synthetic_only and a.pairs is None:
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
    meta["seconds"] = round(time.time() - t0, 1)
    meta["peak_working_set_mb"] = round(working_set_mb(peak=True), 1)
    (out / f"calibrate_{a.part}.json").write_text(json.dumps(meta, indent=1, default=str), encoding="utf-8")
    log(f"EXIT 0; peak working set {meta['peak_working_set_mb']} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
