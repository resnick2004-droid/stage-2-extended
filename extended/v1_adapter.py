"""Stage 2 D-663's V1 validation parts for a subject Stage 2 never gave them (TASK_QUEUE Q-18: P-14) -- adapters over
the vendored `scripts/v1_validation.py` and `propedge/research/v1_validation.py`, both imported, never edited.

    from extended import v1_adapter as X       # puts the vendored tree on sys.path: import it in a process of its own

What is the vendored code's, unchanged: the `Subject` record, the engine call (`v1_validation.Engine.run`: the cache,
the per-path record, `gate.run_gate` with the blocks, each R's e and bound and `mean_block` replaced), the readings of a
run (`reading_rows`, `path_readings`, `growth_on_required`, `mc_error`), A0 (`part_a0`), A1 (`part_a1`), B2
(`part_b2`), and every pure function of `propedge.research.v1_validation` (the stationary bootstrap, the bounds' fast
arithmetic, the coverage counts, the break-even, the missed trades and sessions).

What this module changes, and why -- **only where the vendored code fixes a seed or a subject's name**:

* `Engine`: the vendored hook draws each run's Monte-Carlo error from `[SEED_B1, 9]`, D-663's own seed. Here the seed
  is an argument (`mc_seed`); with `mc_seed=[V.SEED_B1, 9]` the hook is the vendored one (tested).
* `part_b1`: the vendored part draws its histories from `[V.SEED_B1, subject, L, rule]` and takes the era rule only for
  the subject named `S1`. Here the seed is an argument, and the era rule is taken for any subject whose `extra` holds
  `era_spans` (its registered rule then the era rule when `extra["flagged"]`, as for S1). With `seed=V.SEED_B1` and a
  subject named S1 the rows are the vendored part's (tested).
* `part_c1`: the vendored part seeds each realisation by `v1_validation.c1_seed` from D-663's `SEED_C1`. Here
  `c1_seed(seed, subject, arm, realisation)` is `lockstep.child_seed(seed, 3 x subject + arm, realisation)`, the same
  form; with `seed=V.SEED_C1` the rows are the vendored part's but the note naming the seed function (tested).

And one part V1 ran only on FV3-C, written here for a subject whose trades carry their exit kinds:

* `part_slip`: Stage 2 D-583's slippage families (`propedge.research.p16_slip_stress`: its nine arms, `stress`,
  `cost_problems` refusing, `family_rows`) on the subject's trades -- (A) stop slip 2, 3, 5, 8, 12 ticks with the
  flatten one more, (B) entry = stop slip 2, 3, 5 with the flatten one more, targets at zero -- each arm's e and bound
  re-read on the stressed trades by the subject's own registered bound rule (`rebound`), the sizing table frozen, run
  through the subject's registered engine call; the reading per family: the lowest declared level at which growth on
  the required bankroll at the bound is at or below zero ("none" if every level grows), level by level (V1's C2 form).
"""
from __future__ import annotations

import os
from typing import Any, Callable, Mapping

from extended import use_vendored_stage2

use_vendored_stage2()

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import v1_validation as VS  # noqa: E402  (the vendored scripts/v1_validation.py)
from propedge.research import p16_slip_stress as ps16  # noqa: E402
from propedge.research import v1_validation as V  # noqa: E402

WHO = "Q-18"


def refused(msg: str) -> SystemExit:
    return SystemExit(f"REFUSED ({WHO}): {msg}")


# ------------------------------------------------------------------------------------------------ the engine call


def make_hook(sub: VS.Subject, base: Callable, values: dict, mc_seed: Any) -> Callable:
    """The vendored `Engine`'s path hook (`v1_validation.Engine.__init__`'s `hook`), the Monte-Carlo error drawn from
    `np.random.default_rng(mc_seed)` for every run."""

    def hook(shift: str, p: float, paths) -> dict:
        out = dict(base(shift, p, paths))
        out.update(V.path_readings(paths, sub.margin))
        v = V.path_values(paths, sub.margin)
        days = len(paths[0].path.cash_series) if len(paths) else 0
        g, b = V.growth_on_required(v["net"], v["required"], days) if days else (float("nan"), float("nan"))
        want = out.get("pf_growth_on_base_p50")
        if days and np.isfinite(g) and want is not None and not np.isclose(g, float(want), rtol=1e-9, atol=1e-12):
            raise refused(f"growth on the required bankroll re-read from the paths ({g!r}) is not the hook's "
                          f"({want!r}).")
        if days:
            out.update(V.mc_error(v["net"], v["required"], days, np.random.default_rng(mc_seed)))
        values[shift] = v
        return out

    return hook


class Engine(VS.Engine):
    """`v1_validation.Engine` -- its `run`, `_run` and `path_problems` inherited unchanged -- with the Monte-Carlo
    error's seed an argument (`mc_seed`) instead of D-663's `[SEED_B1, 9]`."""

    def __init__(self, sub: VS.Subject, n_paths: int, workers: int, resume: VS.Resume | None, *, mc_seed: Any):
        self.sub, self.n_paths, self.workers, self.resume = sub, int(n_paths), int(workers), resume
        self.mc_seed = mc_seed
        self.sink: list[dict] = []
        self.inner, base = sub.hook_base(self.sink)
        self.values: dict[str, dict[str, np.ndarray]] = {}
        self.hook = make_hook(sub, base, self.values, mc_seed)
        self.seconds: list[float] = []
        self.labels: list[str] = []


# ------------------------------------------------------------------------------------------------ B1


def part_b1(sub: VS.Subject, *, seed: int, reps: int, verify: int, auto: int, subject_index: int = 0) -> list[dict]:
    """B1 on one subject (the vendored `v1_validation.part_b1`, line for line): the registered bound on
    stationary-bootstrap histories of the subject's own length at `V.B1_BLOCKS` and `auto`, its coverage of the
    pooled mean at 0.05 and 0.05/N, with the exact interval; histories from `np.random.default_rng([seed,
    subject_index, L, rule])`. The era rule is read for a subject whose `extra` holds `era_spans` (registered when
    `extra["flagged"]`); its fast bound checked against the registered bounds (`extra["lb05_by"]`, `sub.lb_by`) and,
    on `verify` materialised replicates a run, against `confirm_fv3.edge_stats` -- refusing."""
    import confirm_fv3 as cf

    keys = [R for R in sub.keys if np.isfinite(sub.t[f"r_{R:g}"].to_numpy(float)).any()]
    cols = [sub.keys.index(R) for R in keys]
    sums, cnts = V.day_sums(sub.t, sub.days, sub.keys)
    sums, cnts = sums[:, cols], cnts[:, cols]
    n = len(sub.days)
    alphas = (V.ALPHA, V.ALPHA / sub.n_led)
    pos = {d: i for i, d in enumerate(sub.days)}
    order = sub.t["date"].astype(str).map(pos).to_numpy(int)
    rows_by_day = [np.nonzero(order == i)[0] for i in range(n)] if verify else []
    rules: dict[str, list[np.ndarray] | None] = {"pooled": None}
    ident = V.block_bounds(sums, cnts, np.arange(n)[None, :], sub.block_days, alphas)
    st = cf.edge_stats(sub.t, keys, sub.days, sub.block_days, sub.n_led)
    bad = [f"{R:g}" for j, R in enumerate(keys)
           if not (np.isclose(ident["lb"][0, 0, j], st[R]["lb"], rtol=0, atol=1e-12)
                   and np.isclose(ident["lb"][1, 0, j], st[R]["lb_at_n"], rtol=0, atol=1e-12)
                   and np.isclose(ident["e"][0, j], st[R]["e"], rtol=0, atol=1e-12))]
    if bad:
        raise refused(f"{sub.name}'s fast bound is not confirm_fv3.edge_stats' at R {bad}.")
    truth = {R: float(st[R]["e"]) for R in keys}
    registered_rule = "pooled"
    if "era_spans" in sub.extra:
        yrs = np.array([int(str(d)[:4]) for d in sub.days])
        eras = [np.nonzero((yrs >= lo) & (yrs <= hi))[0] for lo, hi in sub.extra["era_spans"]]
        if sum(len(e) for e in eras) != n:
            raise refused(f"{sub.name}'s eras do not cover its days.")
        er = V.era_rule_bounds(sums, cnts, [e[None, :] for e in eras], sub.block_days, alphas)
        if sub.extra["flagged"]:
            rules["era_rule"] = eras
            registered_rule = "era_rule"
        reg05, regn = sub.extra["lb05_by"], sub.lb_by
        src = er if sub.extra["flagged"] else ident
        bad = [f"{R:g}" for j, R in enumerate(keys)
               if not (np.isclose(src["lb"][0, 0, j], reg05[R], rtol=0, atol=1e-12)
                       and np.isclose(src["lb"][1, 0, j], regn[R], rtol=0, atol=1e-12))]
        if bad:
            raise refused(f"{sub.name}'s fast {registered_rule} bound is not a3_brk30.bounds_at_n's at R {bad}.")
    blocks = list(dict.fromkeys(list(V.B1_BLOCKS) + [int(auto)]))
    out: list[dict] = []
    chunk = max(1, int(VS.B1_CHUNK_CELLS // max(1, n * len(keys))))
    for L in blocks:
        for rule, eras in rules.items():
            rng = np.random.default_rng([int(seed), int(subject_index), int(L), 0 if rule == "pooled" else 1])
            exceed = np.zeros((len(alphas), len(keys)), dtype=np.int64)
            exceed_low = np.zeros_like(exceed)
            defined = np.zeros_like(exceed)
            lb_sum = np.zeros((len(alphas), len(keys)))
            e_sum, e_sq = np.zeros(len(keys)), np.zeros(len(keys))
            tr = np.array([truth[R] for R in keys])
            low_truth = None
            if eras is not None:
                low_truth = V.era_rule_bounds(sums, cnts, [e[None, :] for e in eras], sub.block_days, alphas)["e_low"][0]
            done, checked = 0, 0
            while done < reps:
                m = min(chunk, reps - done)
                if eras is None:
                    idx = [V.stationary_indices(n, L, m, rng)]
                    b = V.block_bounds(sums, cnts, idx[0], sub.block_days, alphas)
                else:
                    idx = [e[V.stationary_indices(len(e), L, m, rng)] for e in eras]
                    b = V.era_rule_bounds(sums, cnts, idx, sub.block_days, alphas)
                ok = np.isfinite(b["lb"])
                defined += ok.sum(axis=1)
                exceed += (ok & (b["lb"] > tr[None, None, :])).sum(axis=1)
                if low_truth is not None:
                    exceed_low += (ok & (b["lb"] > low_truth[None, None, :])).sum(axis=1)
                lb_sum += np.where(ok, b["lb"], 0.0).sum(axis=1)
                e_sum += np.nansum(b["e"], axis=0)
                e_sq += np.nansum(b["e"] ** 2, axis=0)
                while checked < min(verify, m):
                    parts = [VS._materialise(sub, rows_by_day, ix[checked]) for ix in idx]
                    refs = [cf.edge_stats(tb, keys, dd, sub.block_days, sub.n_led) for tb, dd in parts]
                    for j, R in enumerate(keys):
                        want = (min(r[R]["lb"] for r in refs), min(r[R]["lb_at_n"] for r in refs))
                        got = (b["lb"][0, checked, j], b["lb"][1, checked, j])
                        if not all((np.isnan(w) and np.isnan(g)) or np.isclose(g, w, rtol=0, atol=1e-9)
                                   for g, w in zip(got, want)):
                            raise refused(f"{sub.name} {rule} L {L} replicate {checked} R {R:g}: the fast bound {got} "
                                          f"is not the registered function's {want}.")
                    checked += 1
                done += m
            for a, alpha in enumerate(alphas):
                for j, R in enumerate(keys):
                    c = V.coverage_counts(int(exceed[a, j]), int(defined[a, j]), int(reps - defined[a, j]), alpha)
                    row = {"section": "b1", "subject": sub.name, "rule": rule,
                           "registered_rule": bool(rule == registered_rule), "mean_block": int(L),
                           "block_is_auto": bool(int(L) == int(auto)), "rr": R,
                           "leg": "fresh_combine" if R == sub.crr else "fresh_funded" if R == sub.frr else "",
                           "level": "0.05" if a == 0 else f"0.05/{sub.n_led}",
                           "verdict_level": bool(np.isclose(alpha, sub.alpha_verdict)), "truth": truth[R], **c,
                           "mean_bound": float(lb_sum[a, j] / defined[a, j]) if defined[a, j] else float("nan"),
                           "sd_of_e": float(np.sqrt(max(e_sq[j] / reps - (e_sum[j] / reps) ** 2, 0.0))),
                           "verified_replicates": int(checked), "resampling": (
                               "the whole history" if eras is None else "inside each era, the eras' lengths kept")}
                    if low_truth is not None:
                        lo = V.coverage_counts(int(exceed_low[a, j]), int(defined[a, j]), 0, alpha)
                        row.update({"truth_lower_era": float(low_truth[j]),
                                    "share_exceed_lower_era": lo["share_exceed"],
                                    "share_lower_era_lo": lo["share_lo"], "share_lower_era_hi": lo["share_hi"]})
                    out.append(row)
            print(f"  {sub.name} B1 {rule} mean block {L}: {reps} replicates", flush=True)
    return out


# ------------------------------------------------------------------------------------------------ C1


def c1_seed(seed: int, subject_index: int, arm_index: int, realisation: int) -> int:
    """C1's seed for one realisation: `lockstep.child_seed(seed, len(C1_ARMS) x subject + arm, realisation)` --
    `v1_validation.c1_seed`'s form with the root seed an argument."""
    from propedge.campaign.lockstep import child_seed

    return int(child_seed(int(seed), len(V.C1_ARMS) * int(subject_index) + int(arm_index), int(realisation)))


def part_c1(eng: VS.Engine, reg: dict[str, dict], *, seed: int, subject_index: int = 0) -> list[dict]:
    """C1 (the vendored `v1_validation.part_c1`, line for line): each of `V.C1_ARMS` -- every offered trade dropped
    with p 0.10 and 0.25, whole sessions missed with p 0.10 (the day kept, empty) -- in `V.C1_REALISATIONS` seeded
    realisations (`c1_seed`), each a row pair through the subject's registered call with each R's e and bound as
    registered; then per arm and reading the realisations' mean, smallest, largest and range (`c1_summary`)."""
    sub = eng.sub
    rows = []
    for i, (name, kind, p) in enumerate(V.C1_ARMS):
        arm_rows = []
        for j in range(V.C1_REALISATIONS):
            rs = c1_seed(seed, subject_index, i, j)
            rng = np.random.default_rng(rs)
            if kind == "trade":
                tt, gone = V.drop_trades(sub.t, p, rng), []
            else:
                tt, gone = V.miss_sessions(sub.t, sub.days, p, rng)
            res = eng.run(f"c1 {name} realisation {j}", blocks=sub.rebuild(tt))
            arm_rows += VS.reading_rows("c1", sub, name, res, reg, kind=kind, p=p, realisation=j, realisation_seed=rs,
                                        trades_offered=int(len(sub.t)), trades_left=int(len(tt)),
                                        sessions_missed=len(gone),
                                        note=f"realisation {j} of {V.C1_REALISATIONS} (seed extended.v1_adapter."
                                             f"c1_seed from {int(seed)}); each R's e and bound as registered")
            print(f"  {sub.name} C1 {name} realisation {j}: done", flush=True)
        rows += arm_rows
        for arm in (sub.arm_names["bound"], sub.arm_names["point"]):
            mine = [r for r in arm_rows if r["arm"] == arm]
            row: dict[str, Any] = {"section": "c1_summary", "subject": sub.name, "arm": arm, "scheme": name,
                                   "kind": kind, "p": p, "realisations": len(mine),
                                   "share_realisations_growth_above_zero": float(np.mean([r["growth_above_zero"]
                                                                                         for r in mine]))}
            for c in VS.READ + ("trades_left", "sessions_missed"):
                for k, v in V.realisation_summary([r.get(c) for r in mine]).items():
                    if k != "n":
                        row[f"{c}_{k}"] = v
            rows.append(row)
    return rows


# ------------------------------------------------------------------------------------------------ slippage (D-583)


def part_slip(eng: VS.Engine, reg: dict[str, dict],
              rebound: Callable[[pd.DataFrame], tuple[Mapping[float, float], Mapping[float, float], dict]]
              ) -> list[dict]:
    """Stage 2 D-583's nine arms on the subject's trades (`p16_slip_stress.arms`): the base is the registered run;
    every other arm's trades are `p16_slip_stress.stress`'s (each offered R's net outcome lowered, and its cost raised,
    by the arm's extra ticks over the base for that R's exit kind, over the trade's own stop), checked by
    `p16_slip_stress.cost_problems` (refusing), their e and bound re-read by `rebound` (the subject's registered rule,
    at its verdict level: (e by R, the bound by R, extra columns)), the sizing table frozen, through the subject's
    registered call. Rows (section `slip`, both arms) beside the registered run's, then per family the lowest declared
    level at which growth on the required bankroll at the bound is at or below zero (section `slip_reading`)."""
    sub = eng.sub
    rows: list[dict] = []
    for a in ps16.arms():
        add = ps16.added_ticks(a)
        if a["arm"] == "base":
            if any(v != 0 for v in add.values()):
                raise refused("D-583's base arm adds ticks.")
            res, tt, e_by, lb_by, more = reg, sub.t, dict(sub.e_by), dict(sub.lb_by), {}
        else:
            tt = ps16.stress(sub.t, a)
            bad = ps16.cost_problems(sub.t, tt, a)
            if bad:
                raise refused(f"the stressed trades are not D-583's arm {a['arm']} -- " + "; ".join(bad[:6]))
            e_by, lb_by, more = rebound(tt)
            res = eng.run(f"slip {a['arm']}", blocks=sub.rebuild(tt), e_by=dict(e_by), lb_by=dict(lb_by))
        rows += VS.reading_rows(
            "slip", sub, a["arm"], res, reg, family=a["family"], level=int(a["level"]),
            entry_slip_ticks=int(a["entry_slip_ticks"]), stop_slip_ticks=int(a["stop_slip_ticks"]),
            flatten_slip_ticks=int(a["flatten_slip_ticks"]), target_slip_ticks=int(a["target_slip_ticks"]),
            **{f"added_ticks_{k}": float(v) for k, v in add.items()},
            e_fresh_funded_r=float(e_by[sub.frr]), bound_fresh_funded_r=float(lb_by[sub.frr]),
            e_fresh_combine_r=float(e_by[sub.crr]), bound_fresh_combine_r=float(lb_by[sub.crr]), **more,
            note="D-583's arm: each offered R's net outcome lowered by the extra ticks over the base for its exit kind, "
                 "over the trade's own stop; targets at zero slip; e and the bound re-read on the stressed trades by "
                 "the subject's registered rule at its verdict level; the sizing table frozen")
        print(f"  {sub.name} slippage {a['arm']}: done", flush=True)
    bound = sub.arm_names["bound"]
    for fam in ps16.FAMILIES:
        fr = ps16.family_rows([r for r in rows if r["arm"] == bound], fam)
        low = next((int(r["level"]) for r in fr if not r["growth_above_zero"]), ps16.NONE)
        rows.append({"section": "slip_reading", "subject": sub.name, "arm": bound, "family": fam,
                     "levels": " ".join(str(int(r["level"])) for r in fr),
                     "arms_read": " ".join(str(r["scheme"]) for r in fr),
                     "lowest_level_growth_at_bound_at_or_below_zero": low})
    return rows


# ------------------------------------------------------------------------------------------------ measurement


def peak_memory() -> str | None:
    """This process's peak working set and peak private commit (Windows `GetProcessMemoryInfo`), else None."""
    if os.name != "nt":
        return None
    try:
        import ctypes
        from ctypes import wintypes

        class PMC(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                        ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                        ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]

        k32 = ctypes.windll.kernel32
        k32.GetCurrentProcess.restype = wintypes.HANDLE
        fn = ctypes.windll.psapi.GetProcessMemoryInfo
        fn.argtypes = [wintypes.HANDLE, ctypes.POINTER(PMC), wintypes.DWORD]
        m = PMC()
        m.cb = ctypes.sizeof(PMC)
        if not fn(k32.GetCurrentProcess(), ctypes.byref(m), m.cb):
            return None
        return (f"peak working set {m.PeakWorkingSetSize / 2**30:.2f} GB, peak private commit "
                f"{m.PeakPagefileUsage / 2**30:.2f} GB (this process, GetProcessMemoryInfo)")
    except Exception:                                # noqa: BLE001 -- a measurement, never a failure
        return None


__all__ = ["WHO", "refused", "make_hook", "Engine", "part_b1", "c1_seed", "part_c1", "part_slip", "peak_memory", "VS",
           "V", "ps16"]
