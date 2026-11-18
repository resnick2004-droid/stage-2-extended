"""RD-05 step 2 (`prereg/RD-05_firm_modes.md` 18 step 2; 9, 10, 11; 15): the coin maps -- every mode-corner's gross
`steady` and `flip` cells and its costed `steady` cells, 50,000 accounts a run on section 15's keyed streams; each
run's oracles (9.6) checked before anything of it is kept; then 9.5's joins and renewal, part D's flip pairs and large
days, part E's binding gates, and 4.7 item 5's exposures. No bar is read.

    python scripts/modes_coin.py --plan       # light: the refusals and the run list; writes nothing
    python scripts/modes_coin.py --measure    # 18: time and peak memory on the timing seed 0 (outside the block),
                                              #   outputs discarded; prints the estimate against the bounds
    python scripts/run_clean.py --name rd05-step2 --task <Q> --hours 12 --mem-gb 2.5 -- python scripts/modes_coin.py

**Refusing first** (`extended.modes_steps.step_problems(2)`): the declaration at its pin, the record's keys, the
coin identity held (`modes_coin_identity`), and step 0's file read through its manifest (`extended.results.read_result`)
whose `coin_cells` rows (every cell, its `runs` and its reason, N-13) and `oracle_count` equal this commit's
recomputation -- a difference refuses. Only then are the declared coin streams cleared (`modes_engine.
allow_declared_streams`, S-7); no other caller can draw them. `--measure` runs only under `run.lock` held by an
`rd05-` job (N-14). **Order** (18): `TS-S`'s evaluation mode first, then Appendix M's order; per
`(w, r)` the steady cell, its flip, its costed cells; **any oracle breach stops the step at once: nothing of the step is
written**. Shared gross cells (N-4) are run once at the strict corner and copied, their checks counted once.

**Writes** `results/modes_coin.csv` (sections `identity`, `oracle`, `eval`, `funded`, `fees`, `joined`, `renewal`,
`flip_pairs`, `large_days`, `binding`, `exposure`) through `extended.results`, only from a clean checkout.
"""
from __future__ import annotations

import argparse
import math
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from extended import modes_engine as E  # noqa: E402
from extended import modes_join as J  # noqa: E402
from extended import modes_oracles as O  # noqa: E402
from extended import modes_reading as RD  # noqa: E402
from extended import modes_rules as R  # noqa: E402
from extended import modes_steps as S  # noqa: E402
from extended import modes_terms as M  # noqa: E402
from extended.procmem import working_set_mb  # noqa: E402

SCRIPT = "scripts/modes_coin.py"


def cell_signature_rows(rows: list[dict[str, Any]]) -> list[tuple]:
    """N-13: each coin cell's identity, whether it runs and why, normalised for comparison with step 0's file."""
    def norm_stop(x: Any) -> Any:
        if x is None or (isinstance(x, float) and math.isnan(x)) or str(x) in ("", "nan", "None"):
            return None
        return int(float(x))

    return sorted((int(r["index"]), int(r["w_index"]), int(r["r_index"]), str(r["policy"]), str(r["coin"]),
                   norm_stop(r["stop"]), str(r["runs"]) in ("True", "true", "1"), str(r.get("why") or "")
                   if str(r.get("why")) != "nan" else "") for r in rows)


def run_order() -> list[M.ModeCorner]:
    """18 step 2: `TS-S`'s evaluation mode first (Appendix M row 0 is it), then Appendix M's order."""
    return list(M.MODE_CORNERS)


def _trim(f: np.ndarray) -> np.ndarray:
    nz = np.nonzero(f)[0]
    return f[: (int(nz[-1]) + 1 if len(nz) else 1)].astype(float)


def run_cell(m: M.ModeCorner, wi: int, ri: int, policy: str, coin: str, stop: int | None, n: int,
             seeds: tuple[int, int, int] | None = None) -> dict[str, Any]:
    """One coin run on its keyed streams (or, with `seeds`, on the timing seed's streams)."""
    w, r = M.grid_w()[wi], M.grid_r()[ri]
    spec = E.spec_for(m, w, r, policy=policy, coin=coin, stop=stop)
    if seeds is None:
        ev = E.stream("coin_eval", wi, ri)
        fu = E.stream("coin_funded", wi, ri)
        pk = E.stream("coin_peak", wi, ri)
    else:
        ev = fu = np.random.default_rng([seeds[0], wi, ri])
        pk = np.random.default_rng([seeds[0], wi, ri, 1])
    if m.kind == M.EVAL:
        return {"spec": spec, "out": E.run_eval(spec, n, ev)}
    return {"spec": spec, "out": E.run_funded(spec, n, fu, pk)}


def cell_rows(m: M.ModeCorner, wi: int, ri: int, policy: str, coin: str, stop: int | None, res: dict[str, Any],
              N: int, bset: set) -> dict[str, list[dict[str, Any]]]:
    """The run's rows; its oracles checked first (raising `OracleBreach`)."""
    spec, out = res["spec"], res["out"]
    t = spec.t
    w, r = M.grid_w()[wi], M.grid_r()[ri]
    key = {"index": m.index, "kind": m.kind, "mode": m.mode, "corner": m.corner, "w": w, "r": r, "policy": policy,
           "coin": coin, "stop": stop}
    boundary = m.kind == M.EVAL and coin == "gross" and policy == "steady" and (m.index, w, r) in bset   # a flip
    # trades r_flip, off the cell's lattice: never a boundary cell
    orc = O.oracle_rows(m.kind, out, t, N=N, mode=m.mode, boundary=boundary, close_only=bool(m.index in
                                                                                             M.close_only_corners()))
    rows: dict[str, list[dict[str, Any]]] = {"oracle": [{**key, **o} for o in orc]}
    labels = "; ".join(t.labels + (GROSS_LABELS if coin == "gross" else COIN_LABELS))
    if m.kind == M.EVAL:
        rd = J.eval_reading(out, t)
        rows["eval"] = [{**key, **rd, "labels": labels}]
        p = np.asarray(out["passed"], bool)
        if policy == "steady":
            ks = np.full(int(p.sum()), RD.k_star_steady(t.target, w, r if coin == "gross" else r))
            note = "arithmetic on a steady cell (N3)"
        else:
            ks = RD.k_star_from_counts(out["flip_wins"][p], out["steady_wins"][p], t.target, w, spec.r_flip, r)
            note = ""
        rows["large_days"] = [{**key, **RD.k_star_distribution(ks), "note": note}]
        rows["binding"] = [{**key, "what": "last_gate", **RD.gate_shares(out["last_gate"][p])},
                           {**key, "what": "cause", **RD.gate_shares(out["cause"][~p])}]
    else:
        rd = J.funded_reading(out, t)
        rows["funded"] = [{**key, **rd, "labels": labels}]
        paid = np.asarray(out["first_payout_day"]) >= 0
        firsts = [RD.last_funded_gate({g: int(out["gate_rise"][g][i]) for g in out["gate_rise"]})
                  for i in np.nonzero(paid)[0]]
        rows["binding"] = [{**key, "what": "last_gate", **RD.gate_shares([x or "" for x in firsts])},
                           {**key, "what": "cause", **RD.gate_shares(out["cause"][~paid])}]
    ex = {"full_allowance_share": (float(np.sum(out["full_allowance"])) / max(1, int(np.sum(out["trades"]))))
          if coin == "costed" else "not applicable",
          "s8_ratio_max": float(np.nanmax(out["s8_ratio_max"])) if coin == "costed" and out["s8_ratio_max"] is not None
          and np.any(np.isfinite(out["s8_ratio_max"])) else "not applicable",
          "size_spread": (f"range {np.nanmean(out['size_spread']['range']):.6g}, "
                          f"sd {np.nanmean(out['size_spread']['sd']):.6g} (contracts, micro-equivalents; per-account "
                          "mean)") if coin == "costed" else "not applicable",
          "stacking_share": "in the renewal section (the joined journey's)",
          "evaluations_per_21": (int(M.declared("month")) / float(np.mean(out["days"])))
          if m.kind == M.EVAL and float(np.mean(out["days"])) > 0 else "not applicable"}
    rows["exposure"] = [{**key, **RD.exposures_row(policy, ex)}]
    return rows


#: the paired vectors' layout (flip first, then steady) and the variance algebra's constant (17.2's scan skips it)
LAYOUT: dict[str, int] = {"flip": 0, "steady": 3, "two": 2}

#: 2.6 / 12.6 (N-17): carried on step 2's rows themselves
COIN_LABELS = ("no calendar: no news rule",)
GROSS_LABELS = ("allowance and scaling not applied", "no calendar: no news rule")


def eval_moments(steady: dict[str, Any], flip: dict[str, Any], t: M.EvalTerms) -> dict[str, Any]:
    """10.2: the paired evaluation vectors' moments -- (periods, pass, censored) per account under flip and steady,
    their means and covariance (O(1) to keep), and sessions to a pass under each."""
    def vec(o: dict[str, Any]) -> np.ndarray:
        per = (np.asarray(o["sub_fees"], float) / float(t.subscription)) if t.subscription is not None else \
            np.ones(len(o["passed"]))
        return np.stack([per, np.asarray(o["passed"], float), np.asarray(o["unresolved"], float)])

    X = np.vstack([vec(flip["out"]), vec(steady["out"])])
    sess = {}
    for name, o in (("flip", flip["out"]), ("steady", steady["out"])):
        p = np.asarray(o["passed"], bool)
        d = np.asarray(o["pass_day"])[p] + 1.0
        sess[name] = (float(np.mean(d)) if len(d) else math.nan, float(np.var(d, ddof=1)) if len(d) > 1 else math.nan,
                      len(d), float(np.median(d)) if len(d) else math.nan)
    return {"n": X.shape[1], "mean": X.mean(axis=1), "cov": np.cov(X), "sessions": sess}


def funded_moments(steady: dict[str, Any], flip: dict[str, Any]) -> dict[str, Any]:
    """10.2: the paired funded nets (cash to the user) under flip and steady: means, variances, covariance."""
    Y = np.stack([np.asarray(flip["out"]["cash"], float), np.asarray(steady["out"]["cash"], float)])
    return {"n": Y.shape[1], "mean": Y.mean(axis=1), "cov": np.cov(Y)}


def flip_net_pairs(cfg: str, em: dict[str, Any], fm: dict[str, Any], price: float, act: float,
                   key: dict[str, Any]) -> list[dict[str, Any]]:
    """10.2 on the coin: the net per attempt and per funded journey, flip against steady, with paired standard
    errors -- `flip_E` (the evaluation's flip, the funded steady) and `flip_F` (the evaluation steady, the funded flip);
    the evaluation's and the funded account's streams are independent (section 15), so the variances are exact
    functions of the two paired sets of moments; the journey's by the delta method."""
    out = []
    m, C, n = em["mean"], em["cov"], em["n"]
    Ym, YC, nf = fm["mean"] - act, fm["cov"], fm["n"]
    # flip_E: d = -price (per_f - per_s) + (P_f - P_s) Y_s, Y_s independent
    a = np.array([-price, 0, 0, price, 0, 0])
    bvec = np.array([0, 1, 0, 0, -1, 0])
    EY, VY = Ym[1], YC[1, 1]
    EB = float(bvec @ m)
    VA, VB, CAB = float(a @ C @ a), float(bvec @ C @ bvec), float(a @ C @ bvec)
    var_d = VA + (VB + EB ** 2) * (VY + EY ** 2) - (EB * EY) ** 2 + LAYOUT["two"] * EY * CAB
    diff = float(a @ m) + EB * EY
    out.append({**key, "flip": "flip_E", "measure": "net_per_attempt", "diff": diff,
                "se": math.sqrt(max(var_d, 0.0) / n), "n": n})

    def J(per: float, P: float, Cn: float, Y: float) -> float:
        return (-price * per + P * Y) / (P + Cn) if P + Cn > 0 else math.nan

    jf, js = J(m[0], m[1], m[2], EY), J(m[3], m[4], m[5], EY)
    g = np.zeros(6)
    for i in (LAYOUT["flip"], LAYOUT["steady"]):
        per, P, Cn = m[i], m[i + 1], m[i + 2]
        s = 1.0 if i == LAYOUT["flip"] else -1.0
        T = P + Cn
        if T > 0:
            num = -price * per + P * EY
            g[i] = s * (-price / T)
            g[i + 1] = s * (EY / T - num / T ** 2)
            g[i + 2] = s * (-num / T ** 2)
    gy = (m[1] / (m[1] + m[2]) if m[1] + m[2] > 0 else 0.0) - (m[4] / (m[4] + m[5]) if m[4] + m[5] > 0 else 0.0)
    var_j = float(g @ C @ g) / n + gy ** 2 * VY / nf
    out.append({**key, "flip": "flip_E", "measure": "net_per_journey", "diff": jf - js, "se": math.sqrt(max(var_j, 0)),
                "n": n, "note": "delta method"})
    # flip_F: d = P_s (Y_f - Y_s), P_s from the evaluation, independent of the funded pair
    EP, VP = m[4], C[4, 4]
    EZ = float(Ym[0] - Ym[1])
    VZ = float(YC[0, 0] + YC[1, 1] - LAYOUT["two"] * YC[0, 1])
    var_f = (VP + EP ** 2) * (VZ + EZ ** 2) - (EP * EZ) ** 2
    out.append({**key, "flip": "flip_F", "measure": "net_per_attempt", "diff": EP * EZ,
                "se": math.sqrt(max(var_f, 0.0) / min(n, nf)), "n": min(n, nf)})
    fac = m[4] / (m[4] + m[5]) if m[4] + m[5] > 0 else 0.0
    out.append({**key, "flip": "flip_F", "measure": "net_per_journey", "diff": fac * EZ,
                "se": fac * math.sqrt(max(VZ, 0.0) / nf), "n": nf})
    return out


def laws_of(m: M.ModeCorner, out: dict[str, Any]) -> dict[str, Any]:
    if m.kind == M.EVAL:
        L = J.eval_laws(out)
        return {k: (_trim(v) if isinstance(v, np.ndarray) else v) for k, v in L.items()}
    L = J.funded_laws(out)
    return {k: (_trim(v) if isinstance(v, np.ndarray) else v) for k, v in L.items()}


def _pad(f: np.ndarray, W: int) -> np.ndarray:
    out = np.zeros(W + 1)
    out[: min(len(f), W + 1)] = f[: W + 1]
    return out


def joins(summ: dict[tuple, dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """9.4 / 9.5: per configuration, every evaluation cell with every funded cell of its funded modes (gross with gross,
    costed with costed at the same stop, corners strict with strict and lenient with lenient, a single corner with
    each); the renewal and the coin's stacking exposure."""
    W = J.window()
    out = {"fees": [], "joined": [], "renewal": [], "flip_net": []}
    by = {}
    for k, v in summ.items():
        by.setdefault((v["kind"], v["mode"]), []).append((k, v))
    for cfg in M.CONFIGS:
        emode = "TS" if cfg.startswith("TS") else cfg
        for ek, ev in by.get((M.EVAL, emode), []):
            t = M.eval_terms(cfg, ev["corner"])
            prices = ([None] if (t.subscription is not None or t.one_time is not None) else list(M.price_grid()))
            for price in prices:
                fees = J.mean_fees(ev["mean_periods"], t, price)
                out["fees"].append({"config": cfg, "corner": ev["corner"], "w": ev["w"], "r": ev["r"],
                                    "policy": ev["policy"], "coin": ev["coin"], "stop": ev["stop"],
                                    "price": price if price is not None else (t.subscription or t.one_time),
                                    "fees_per_attempt": fees, "p_censored": ev["laws"]["p_censored"],
                                    "label": "price unverified: on the grid" if price is not None else ""})
            for fmode in M.FUNDED_OF[cfg]:
                for fk, fv in by.get((M.FUNDED, fmode), []):
                    if fv["coin"] != ev["coin"] or fv["stop"] != ev["stop"]:
                        continue
                    if ev["corner"] != M.SINGLE and fv["corner"] != M.SINGLE and ev["corner"] != fv["corner"]:
                        continue
                    el, fl = ev["laws"], fv["laws"]
                    ends = prices if len(prices) == 1 else [prices[0], prices[-1]]   # the grid's ends; the rest exact
                    for price in ends:
                        fees = J.mean_fees(ev["mean_periods"], t, price)
                        act = float(M.rv("activation_fee_naf_50k")) if cfg == "TS-N" else float(fv["activation"])
                        net = J.attempt_net(el["p_pass"], fees, fv["mean_net"], act)
                        jr = J.journey(el["p_pass"], el["p_censored"], fees, fv["mean_net"], act)
                        row = {"what": "pair", "config": cfg, "eval_corner": ev["corner"], "funded_mode": fmode,
                               "funded_corner": fv["corner"], "coin": ev["coin"], "stop": ev["stop"],
                               "eval_w": ev["w"], "eval_r": ev["r"], "eval_policy": ev["policy"], "funded_w": fv["w"],
                               "funded_r": fv["r"], "funded_policy": fv["policy"], "price": price,
                               "net_per_attempt": net, "cost_per_attempt": J.attempt_cost(el["p_pass"], fees, act),
                               "p_pass_and_payout": el["p_pass"] * fl["p_paid"], **jr, "p_pass": el["p_pass"],
                               "funded_mean_net": fv["mean_net"], "activation": act,
                               "break_even_price": (J.break_even_price(el["p_pass"], fv["mean_net"], act,
                                                                       ev["mean_periods"])
                                                    if len(prices) > 1 or t.subscription is not None else None),
                               "price_grid": "U-2: net linear in the price; the grid's ends here, every price in "
                                             "`fees`" if len(prices) > 1 else "",
                               "diagonal": "one policy in both modes (stage one's form)" if (
                                   ev["w"], ev["r"], ev["policy"]) == (fv["w"], fv["r"], fv["policy"]) else "",
                               "block": f"{ev['policy']}/{fv['policy']}"}
                        if cfg == "TS-S" and price is None:                    # 9.6: 9.5's net == attempt_ev
                            probs = O.attempt_ev_problems(el["p_pass"], fees, fv["mean_net"], act, net)
                            if probs:
                                raise O.OracleBreach(f"9.6 at TS-S: {probs}")
                        if (price is None or price == prices[0]) and ev["policy"] == "steady" and \
                                fv["policy"] == "steady" and (ev["w"], ev["r"]) == (fv["w"], fv["r"]) and \
                                ev.get("moments") is not None and fv.get("moments") is not None:
                            key = {"config": cfg, "eval_corner": ev["corner"], "funded_mode": fmode,
                                   "funded_corner": fv["corner"], "w": ev["w"], "r": ev["r"], "coin": ev["coin"],
                                   "price": price if price is not None else (t.subscription or t.one_time)}
                            out["flip_net"].extend(flip_net_pairs(cfg, ev["moments"], fv["moments"],
                                                                  float(key["price"]) if key["price"] is not None
                                                                  else 0.0, act, key))
                        if price is None or price == prices[0]:
                            evp = {k: (_pad(v, W) if isinstance(v, np.ndarray) else v) for k, v in el.items()}
                            fup = {k: (_pad(v, W) if isinstance(v, np.ndarray) else v) for k, v in fl.items()}
                            if "_R" not in ev:                 # once per evaluation cell
                                ev["_R"] = J.renewal(evp["fail"])
                                ev["_Rn"] = J.renewal(evp["nonbreach"])
                            rn = J.first_payout_law(evp, fup, ev["_R"])
                            law = rn["law"]
                            mean = float(np.sum(np.arange(len(law)) * law) / law.sum()) if law.sum() > 0 else math.nan
                            out["renewal"].append({**{k: row[k] for k in ("config", "eval_corner", "funded_mode",
                                                                          "funded_corner", "coin", "stop", "eval_w",
                                                                          "eval_r", "eval_policy", "funded_w",
                                                                          "funded_r", "funded_policy")},
                                                   "p_payout": rn["p_payout"], "within_window": rn["within_window"],
                                                   "beyond_window": rn["beyond_window"],
                                                   "censored_attempt": rn["censored_attempt"],
                                                   "censored_funded": rn["censored_funded"],
                                                   "mean_sessions_within": mean,
                                                   "stacking_share": J.stacking_exposure(evp, fup, ev["_Rn"]),
                                                   "evaluations_per_21": ev["evaluations_per_21"],
                                                   "label": "one attempt can reach 1,008 sessions"})
                        out["joined"].append(row)
                        K = M.purchase_limit(cfg)
                        if K is not None and (price is None or price == ends[0]):      # A-4 / U-24 (9.5)
                            pl = J.under_purchase_limit(el["p_pass"], el["p_censored"], fees, fv["mean_net"], act, K)
                            out["joined"].append(
                                {**{k: row[k] for k in ("config", "eval_corner", "funded_mode", "funded_corner",
                                                        "coin", "stop", "eval_w", "eval_r", "eval_policy",
                                                        "funded_w", "funded_r", "funded_policy")},
                                 "what": "purchase_limit", "u24_end": "strict: the limit in total", **pl})
    out["flip_pairs"] = out.pop("flip_net")                   # 18's section name
    return out


def flip_pair_rows(key: dict[str, Any], steady: dict[str, Any], flip: dict[str, Any]) -> list[dict[str, Any]]:
    """10.2 on the coin: each flip against its steady cell on the same streams, paired."""
    a, b = flip["out"], steady["out"]
    def among(x: np.ndarray, y: np.ndarray, name: str) -> list[dict[str, Any]]:
        """Sessions among each cell's own successes: a difference of means (its standard error from the two sets,
        which share no account selection) and of medians."""
        se = math.sqrt(np.var(x, ddof=1) / len(x) + np.var(y, ddof=1) / len(y)) if len(x) > 1 and len(y) > 1 \
            else math.nan
        return [{**key, "measure": f"{name}_mean", "diff": float(np.mean(x) - np.mean(y)) if len(x) and len(y)
                 else math.nan, "se": se, "n": min(len(x), len(y)), "note": "among each cell's own; unpaired"},
                {**key, "measure": f"{name}_p50", "diff": float(np.median(x) - np.median(y)) if len(x) and len(y)
                 else math.nan, "se": math.nan, "n": min(len(x), len(y)), "note": "medians; no standard error"}]

    if key["kind"] == M.EVAL:
        pa, pb = np.asarray(a["passed"], bool), np.asarray(b["passed"], bool)
        rows = [{**key, "measure": "pass", **RD.paired_difference(pa, pb)},
                {**key, "measure": "sessions_occupied", **RD.paired_difference(a["days"], b["days"])}]
        rows += among(np.asarray(a["pass_day"])[pa] + 1.0, np.asarray(b["pass_day"])[pb] + 1.0, "sessions_to_pass")
    else:
        fa, fb = np.asarray(a["first_payout_day"]), np.asarray(b["first_payout_day"])
        pa, pb = fa >= 0, fb >= 0
        rows = [{**key, "measure": "any_payout", **RD.paired_difference(pa, pb)},
                {**key, "measure": "net", **RD.paired_difference(a["cash"], b["cash"])}]
        for w_ in M.declared("first_payout.within"):
            rows.append({**key, "measure": f"first_payout_within_{w_}",
                         **RD.paired_difference(pa & (fa < w_), pb & (fb < w_))})
        rows += among(fa[pa] + 1.0, fb[pb] + 1.0, "sessions_to_first_payout")
    return rows


def run(n: int, N: int, bset: set, cells: list[dict[str, Any]], seeds: tuple | None = None,
        limit: int | None = None) -> dict[str, list[dict[str, Any]]]:
    """Every coin run that runs, in step 2's order; oracles first; any breach raises (nothing kept)."""
    runs = {(c["index"], c["w_index"], c["r_index"], c["policy"], c["coin"], c["stop"]): c for c in cells}
    shared = set(M.shared_gross_corners())
    acc: dict[str, list[dict[str, Any]]] = {k: [] for k in ("oracle", "eval", "funded", "large_days", "binding",
                                                            "exposure", "flip_pairs")}
    summ: dict[tuple, dict[str, Any]] = {}
    done = 0
    for m in run_order():
        for wi in range(len(M.grid_w())):
            for ri in range(len(M.grid_r())):
                kept = {}
                for policy, coin, stop in ([("steady", "gross", None), ("flip", "gross", None)]
                                           + [("steady", "costed", int(s)) for s in M.declared("grid.s_costed")]):
                    c = runs.get((m.index, wi, ri, policy, coin, stop))
                    if c is None or not c["runs"]:
                        if c is not None and m.index in shared and coin == "gross":
                            twin = M.strict_twin(m)
                            k2 = (twin.index, wi, ri, policy, coin, stop)
                            if k2 in summ:
                                summ[(m.index, wi, ri, policy, coin, stop)] = {**summ[k2], "corner": m.corner,
                                                                               "shared": True}
                        continue
                    res = run_cell(m, wi, ri, policy, coin, stop, n, seeds)
                    rows = cell_rows(m, wi, ri, policy, coin, stop, res, N, bset)
                    for k, v in rows.items():
                        acc[k].extend(v)
                    t = res["spec"].t
                    o = res["out"]
                    s = {"kind": m.kind, "mode": m.mode, "corner": m.corner, "w": M.grid_w()[wi],
                         "r": M.grid_r()[ri], "policy": policy, "coin": coin, "stop": stop, "laws": laws_of(m, o)}
                    if m.kind == M.EVAL:
                        s["mean_periods"] = (float(np.mean(o["sub_fees"])) / float(t.subscription)
                                             if t.subscription is not None else 1.0)
                        s["evaluations_per_21"] = int(M.declared("month")) / float(np.mean(o["days"]))
                    else:
                        s["mean_net"] = float(np.mean(o["cash"]))
                        s["activation"] = float(t.activation)
                    summ[(m.index, wi, ri, policy, coin, stop)] = s
                    kept[(policy, coin, stop)] = res
                    done += 1
                    if limit is not None and done >= limit:
                        return {**acc, "_summ": [summ]}
                if ("steady", "gross", None) in kept and ("flip", "gross", None) in kept:
                    key = {"index": m.index, "kind": m.kind, "mode": m.mode, "corner": m.corner,
                           "w": M.grid_w()[wi], "r": M.grid_r()[ri]}
                    st_, fl_ = kept[("steady", "gross", None)], kept[("flip", "gross", None)]
                    acc["flip_pairs"].extend(flip_pair_rows(key, st_, fl_))
                    sk = (m.index, wi, ri, "steady", "gross", None)
                    summ[sk]["moments"] = (eval_moments(st_, fl_, st_["spec"].t) if m.kind == M.EVAL
                                           else funded_moments(st_, fl_))
    acc["_summ"] = [summ]
    return acc


def measure_lock_problem() -> str | None:
    """N-14: `--measure` is compute-heavy -- it runs only while `run.lock` is held by an `rd05-` job."""
    import json

    from extended import lock_guard

    root = lock_guard.main_root()
    lock = None if root is None else root / "run.lock"
    if lock is None or not lock.is_file():
        return "run.lock is not held: take it (scripts/run_lock.py take) for an rd05- job first"
    try:
        job = json.loads(lock.read_text(encoding="utf-8")).get("job", "")
    except (OSError, ValueError):
        return "run.lock is unreadable"
    return None if str(job).startswith("rd05-") else f"run.lock is held by {job!r}, not an rd05- job"


def measure(n: int, sample: int) -> dict[str, float]:
    """18: step 2's time and memory on the timing seed (0, outside the block), outputs discarded."""
    cells = [c for c in R.coin_cells() if c["runs"]]
    pick = cells[:: max(1, len(cells) // int(sample))][: int(sample)]
    t0 = time.time()
    for c in pick:
        m = M.MODE_CORNERS[c["index"]]
        stop = None if c["stop"] is None or (isinstance(c["stop"], float) and math.isnan(c["stop"])) else int(c["stop"])
        run_cell(m, c["w_index"], c["r_index"], c["policy"], c["coin"], stop, n, seeds=(M.TIMING_SEED, 0, 0))
    per = (time.time() - t0) / len(pick)
    return {"runs_sampled": len(pick), "seconds_per_run": per, "runs": len(cells), "hours_estimate": per * len(cells)
            / 3600.0, "peak_mb": working_set_mb(peak=True)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--measure", action="store_true")
    ap.add_argument("--sample", type=int, default=40)
    args = ap.parse_args(argv)
    n = int(M.declared("accounts"))
    if args.measure:
        bad = measure_lock_problem()
        if bad:
            print(f"REFUSED (N-14): {bad}")
            return 3
        r = measure(n, args.sample)
        bound_h, bound_gb = M.declared("time.bound_h")[2], M.declared("memory.bound_gb")[2]
        print(f"timing on seed {M.TIMING_SEED}: {r}; bounds {bound_h} h, {bound_gb} GB (summed); "
              f"{'WITHIN' if r['hours_estimate'] <= bound_h and r['peak_mb'] / 1024 <= bound_gb else 'EXCEEDS'}")
        return 0
    probs = S.step_problems(2)
    for p in probs:
        print(f"REFUSED: {p}")
    cells = R.coin_cells()
    bounds = R.boundary_cells()
    count = R.oracle_count(cells, bounds)
    print(f"runs: {count['gross_runs']} gross, {count['costed_runs']} costed; N = {count['N']}")
    if args.plan or probs:
        return 3 if probs else 0
    from extended import results

    step0 = results.read_result("modes_rules.csv")
    cc = step0[step0["section"] == "coin_cells"]
    if cell_signature_rows(cc.to_dict("records")) != cell_signature_rows(cells):        # N-13: the rows themselves
        print("REFUSED: step 0's coin_cells differ from this commit's recomputation")
        return 3
    oc = step0[step0["section"] == "oracle_count"]
    if int(float(oc["N"].iloc[0])) != count["N"]:
        print("REFUSED: step 0's N differs from this commit's recomputation")
        return 3
    bset = {(b["index"], b["w"], b["r"]) for b in bounds}
    E.allow_declared_streams("scripts/modes_coin.py main: step_problems(2) empty")   # S-7: only here
    t0 = time.time()
    try:
        acc = run(n, count["N"], bset, cells)
    except O.OracleBreach as exc:
        print(f"STOPPED: {exc}; nothing of step 2 is written")
        return 4
    summ = acc.pop("_summ")[0]
    acc.update(joins(summ))
    acc["identity"] = [{"what": "modes_coin_identity", "held": "by the lead's row (step_problems(2))"}]
    frames = []
    for sec, rows in acc.items():
        if rows:
            df = pd.DataFrame(rows)
            df.insert(0, "section", sec)
            frames.append(df)
    df = pd.concat(frames, ignore_index=True, sort=False)
    df["described"] = "described, not carried"
    params = {"prereg": M.DECLARATION, "prereg_sha256": M.DECLARATION_SHA256, "pinning_row": M.PINNING_ROW,
              "seeds": M.SEEDS, "reserved_seeds": list(M.RESERVED_SEEDS), "N": count["N"], "accounts": n,
              "runs": count, "head": S.head_sha(), "e015_limits": "none approved before the run's commit"}
    results.write_result(df, "modes_coin", script=SCRIPT, seed=M.seed("coin_eval"), parameters=params,
                         prereg_id=M.PREREG_ID, exploratory=False,
                         description="RD-05 step 2: the zero-edge coin maps (described, not carried)")
    print(f"step 2 written in {(time.time() - t0) / 3600:.2f} h; peak {working_set_mb(peak=True):.0f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
