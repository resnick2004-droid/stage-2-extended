"""Q-18b (the lead, E-132): the parts of P-14's stress checks the audit of `results/p14_validation.csv` found missing
(`docs/audits/Q-18_p14_stress_2026-11-17.md`, E-125's caveats 1-5), built as Stage 2 declared them -- adapters and pure
readings over the vendored V1 and D-583 code (imported, never edited) and `extended/v1_adapter.py` (unchanged).

    from extended import p14_stress_b as Q    # puts the vendored tree on sys.path: import it in a process of its own

What each piece is, and where Stage 2 fixed it:

* `Engine` -- `extended.v1_adapter.Engine` (the vendored `v1_validation.Engine` with the Monte-Carlo seed an argument)
  whose `_run` is the vendored `_run` line for line, the gate row's kept columns widened by `EXTRA` (the engine's own
  `ruin_probability`, `share_accounts_ever_paid` (D-583), `pf_required_worst` (D-312's bankroll distribution), and
  D-145's pattern measures) and each arm's per-path required bankroll kept (`REQUIRED`) so the ruin figures below can
  be read against any bankroll. Every vendored column is the vendored `_run`'s, value for value (tested), so the
  vendored parts' rows from this engine are the rows `scripts/p14_validation.py` wrote (the runner checks them against
  the file, every cell).
* `ruin_columns` -- **a ruin figure beside every stressed growth (Stage 2 D-145, D-14), in Stage 2's form for a run
  whose bankroll is an output (D-312):** "ruin is not defined where cash never binds and the bankroll distribution
  takes its place" -- the engine's `ruin_probability` as the gate row records it (zero by construction at the unbound
  bankroll, as Stage 2's audits state it: "ruin at the required base by construction"), the required bankroll's p50,
  p90, p99 and worst, and the share of paths whose required bankroll (D-312: the deepest loss below the start plus the
  margin) exceeds the run's own p90 (the base growth is read on) and exceeds the reference run's p90 (the bankroll the
  unstressed run said was needed) -- the paths a stated bankroll of that size would not have carried.
* `part_a2` -- D-663's A2 (the vendored `v1_validation.part_a2`, line for line; a test compares the two sources) with
  the resampled paths' root seed an argument in place of D-663's `SEED_A2` (the brief's rule for anything new, as
  `scripts/p14_validation.py` took B1's and C1's).
* `part_slip_b` -- D-583's readings `scripts/p14_validation.py`'s slippage part did not carry, on the same nine arms:
  each arm's run at **D-583's own level** (the 0.05 bound by the era rule, `a3_brk30.bounds_at_n`'s `lb_gate`) beside
  the one at **P-14's verdict level** (0.05/370 by the era rule, the existing reading, re-run), the **zero-edge twin**
  (`portfolio_stage.zero_edge_blocks` with the arm's own e removed, e and the bound zero -- P-14's registered
  `zero_edge_twin` call), the **share of accounts ever paid**, **D-509's four slice lines against FV3-C** (the arm's
  verdict arm at the 0.05 bound replayed from every start by `customer_slices`' machinery, as P-14's registered slices
  were, against FV3-C's frozen summary in P-14's registered file) and **D-212's resolution** (unchanged by cost;
  reported); then `slip_readings` -- per family and per bound level, D-583's fixed reading
  (`p16_slip_stress.reading`): the lowest level with growth at the bound at or below zero and the highest level at
  which all four slice lines hold.
* `assumption_rows` -- the run's standing assumptions, each read from the engine call it describes (E-125 caveat 4).
* `file_problems` -- every cell of the re-made vendored rows against `results/p14_validation.csv`'s.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from extended import v1_adapter as X

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

VS, V, ps16 = X.VS, X.V, X.ps16

WHO = "Q-18b"
#: the gate row's columns kept beside the vendored ones: the engine's ruin (D-14, D-145), D-583's share of accounts
#: ever paid, D-312's worst required bankroll, D-145's pattern measures (tier 3's exposure, purchases and MLL breaches
#: in 21 days)
EXTRA = ("ruin_probability", "share_accounts_ever_paid", "pf_required_worst", "share_payouts_exposed",
         "mean_max_combine_purchases_21d", "mean_max_mll_breaches_21d")
#: each arm's per-path required bankroll, kept in the run's rows (and its resume line), never written to the file
REQUIRED = "_required_by_path"
RUIN_FORM = ("Stage 2 D-312: the bankroll an output (cash that never binds), so the engine's ruin_probability is zero "
             "by construction and the required bankroll's distribution takes its place -- p50, p90, p99, worst, and "
             "the share of paths whose required bankroll (the deepest loss below the start plus the margin) exceeds "
             "the run's own p90 and the reference run's p90")
LEVEL_VERDICT, LEVEL_D583 = "verdict", "d583"


def refused(msg: str) -> SystemExit:
    return SystemExit(f"REFUSED ({WHO}): {msg}")


# ------------------------------------------------------------------------------------------------ the engine


class Engine(X.Engine):
    """`extended.v1_adapter.Engine` with every run's result kept by label (`results`), the gate row's `EXTRA` columns
    kept and each arm's per-path required bankroll (`REQUIRED`). `run` and `path_problems` are the vendored methods.
    `keep_sink=False` (the declared run, where no per-path identity reads it) empties the per-path record after each
    run -- memory only; no row reads it."""

    def __init__(self, sub: VS.Subject, n_paths: int, workers: int, resume: VS.Resume | None, *, mc_seed: Any,
                 keep_sink: bool = True):
        super().__init__(sub, n_paths, workers, resume, mc_seed=mc_seed)
        self.results: dict[str, dict[str, dict]] = {}
        self.keep_sink = bool(keep_sink)

    def run(self, label: str, *, blocks: list | None = None, e_by: dict | None = None, lb_by: dict | None = None,
            mean_block: float | None = None) -> dict[str, dict]:
        res = VS.Engine.run(self, label, blocks=blocks, e_by=e_by, lb_by=lb_by, mean_block=mean_block)
        self.results[label] = res
        if not self.keep_sink:
            self.sink.clear()
        return res

    def _run(self, label: str, blocks, e_by, lb_by, mean_block) -> dict[str, dict]:
        """The vendored `v1_validation.Engine._run`, line for line, but the columns kept (`EXTRA` added) and the
        per-path required bankroll of each arm (from the hook's own `path_values`)."""
        import time

        import portfolio_stage as ps

        from propedge.campaign import gate

        sub = self.sub
        kw = dict(sub.kw)
        kw["n_paths"] = self.n_paths
        if e_by is not None:
            kw["e_by_rr"], kw["e"] = dict(e_by), float(e_by[sub.frr])
        if lb_by is not None:
            kw["lb_by_rr"], kw["lb"] = dict(lb_by), float(lb_by[sub.frr])
        if mean_block is not None:
            kw["mean_block"] = float(mean_block)
        ps._label(self.inner, f"{sub.name} {label}")
        self.values.clear()
        t0 = time.time()
        df, _ = gate.run_gate(sub.blocks if blocks is None else blocks, workers=self.workers, path_hook=self.hook,
                              **kw)
        self.seconds.append(time.time() - t0)
        out = {}
        for arm, shift in VS.ARMS:
            r = df[df["shift"].astype(str) == shift]
            if len(r) != 1:
                raise refused(f"{len(r)} {shift} rows from one call.")
            r = r.iloc[0]
            out[arm] = {c: VS._plain(r[c]) for c in dict.fromkeys(VS.READ + VS.BESIDE + VS.IDENT_COLS + EXTRA)
                        if c in r.index}
            v = self.values.get(shift)
            if v is None:
                raise refused(f"the path hook saw no {shift} paths in run {label!r}.")
            out[arm][REQUIRED] = [float(x) for x in v["required"]]
        return out


# ------------------------------------------------------------------------------------------------ ruin (D-145, D-312)


def share_above(required: Sequence[float], bankroll: float) -> float:
    """The share of paths whose required bankroll exceeds `bankroll` (strictly): the paths a stated bankroll of that
    size would not have carried (D-312's required bankroll: the deepest loss below the start plus the margin)."""
    req = np.asarray(required, float)
    if not len(req) or not np.isfinite(float(bankroll)):
        return float("nan")
    return float(np.mean(req > float(bankroll)))


def ruin_columns(res_arm: Mapping[str, Any], ref_arm: Mapping[str, Any]) -> dict[str, Any]:
    """One run's arm: Stage 2's ruin figures beside its growth (`RUIN_FORM`), against the reference run's same arm."""
    req = res_arm.get(REQUIRED) or []
    own, ref = float(res_arm.get("pf_required_p90", np.nan)), float(ref_arm.get("pf_required_p90", np.nan))
    return {"pf_growth_on_base_p50": res_arm.get("pf_growth_on_base_p50"),
            "ruin_probability": res_arm.get("ruin_probability", float("nan")),
            "pf_required_p50": res_arm.get("pf_required_p50"), "pf_required_p90": res_arm.get("pf_required_p90"),
            "pf_required_p99": res_arm.get("pf_required_p99"),
            "pf_required_worst": res_arm.get("pf_required_worst", float("nan")),
            "share_required_above_own_p90": share_above(req, own),
            "reference_required_p90": ref, "share_required_above_reference_p90": share_above(req, ref),
            "v1_share_below_start": res_arm.get("v1_share_below_start"), "paths_read": int(len(req)),
            "ruin_form": RUIN_FORM}


def ruin_rows(results: Mapping[str, Mapping[str, dict]], refs: Mapping[str, str], arm_names: Mapping[str, str],
              part_of: Callable[[str], str], subject: str) -> list[dict]:
    """Section `ruin`: one row a run and arm -- every run in `results` (label -> its two arms) against the reference
    run `refs[label]` names (the unstressed run at the same bound level)."""
    out = []
    for label, res in results.items():
        ref = results[refs[label]]
        for arm, _ in VS.ARMS:
            out.append({"section": "ruin", "subject": subject, "run": label, "part": part_of(label),
                        "arm": arm_names[arm], "reference_run": refs[label], **ruin_columns(res[arm], ref[arm])})
    return out


# ------------------------------------------------------------------------------------------------ A2 (D-663)


# D-663's A2 on a subject Stage 2 never gave it: the vendored `v1_validation.part_a2`, line for line, with the
# resampled paths' root seed the argument `seed` (vendored: `V.SEED_A2`) and the vendored module's helpers named
# through `VS`; nothing else differs (tests/p14_validation_b_checks.py compares the two sources).
def part_a2(sub: VS.Subject, starts_cap: int | None, n_paths: int, resume: VS.Resume | None, *, seed: int
            ) -> list[dict]:
    import customer_slices as cs

    from propedge.campaign.lockstep import path_seeds, simulate_lockstep_path
    from propedge.campaign.shared_days import SharedDayDraws

    H = V.A2_HORIZON
    starts = V.a2_starts(len(sub.days))
    if not starts:
        return [{"section": "a2", "subject": sub.name, "computable": False, "sessions": len(sub.days), "horizon": H,
                 "note": f"not computable: the subject has {len(sub.days)} sessions, so no real-order start holds a "
                         f"{H}-session horizon; nothing run"}]
    if starts_cap is not None:
        starts = starts[: int(starts_cap)]
    rows = []
    for arm, (blk, args) in VS.replay_form(sub).items():
        def real(blk=blk, args=args):
            lps = [cs.replay(blk[s:s + H], args) for s in starts]
            v = V.path_values(lps, sub.margin)
            return {"required": v["required"].tolist(), "net": v["net"].tolist()}

        r = VS._cached(resume, f"{sub.name} a2 real {arm} {len(starts)}", real)
        for scheme, L in [("independent", None)] + [(f"stationary, mean block {x}", x) for x in V.MEAN_BLOCKS]:
            def resampled(blk=blk, args=args, L=L):
                lps = []
                for s in path_seeds(int(seed), n_paths):
                    extra = {} if L is None else {"mean_block": float(L)}
                    sd = SharedDayDraws({0: list(blk)}, seed=s, **args["draws"], **extra)
                    lps.append(simulate_lockstep_path(args["draws"]["protocol"], seed=s, horizon_days=H + 1,
                                                      **args["path"], **sd.lockstep_kwargs()))
                v = V.path_values(lps, sub.margin)
                return {"required": v["required"].tolist(), "net": v["net"].tolist()}

            sc = VS._cached(resume, f"{sub.name} a2 {scheme} {arm} {n_paths}", resampled)
            rows.append({"section": "a2", "subject": sub.name, "arm": arm, "scheme": scheme,
                         "mean_block": float(L) if L is not None else float("nan"), "computable": True,
                         "horizon": H, "start_step": V.A2_STEP, "first_start": sub.days[starts[0]],
                         "last_start": sub.days[starts[-1]],
                         **V.exceed_shares(r["required"], r["net"], sc["required"], sc["net"]),
                         "note": "the real-order starts overlap and are dependent: these shares carry no interval; "
                                 "both sides run the replay-form call (the funded horizon 'never', the bankroll "
                                 "unbound), only the order of days differs"})
        print(f"  {sub.name} A2 {arm}: done", flush=True)
    return rows


def a2_path_sets(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    """A2's resampled path sets (one a scheme and arm), the engine runs D-665 counts beside the gate calls."""
    return [f"a2 {r['scheme']} {r['arm']}" for r in rows if r.get("section") == "a2" and r.get("computable")]


# ------------------------------------------------------------------------------------------------ D-583's readings


def rebound_both(sub: VS.Subject, bounds_at_n: Callable | None = None
                 ) -> Callable[[pd.DataFrame], tuple[dict, dict, dict, bool]]:
    """The stressed trades' e and bound by P-14's registered rule at both levels -- (e by R, the 0.05 bound by R
    (D-583's level), the 0.05/N bound by R (P-14's verdict level), the eras' flag) -- from one `a3_brk30.bounds_at_n`
    call (the era rule's lower era when flagged; its 0.05 bound is `atlas_a3.bounds`', checked inside it)."""
    if bounds_at_n is None:
        import a3_brk30 as B

        bounds_at_n = B.bounds_at_n

    def rebound(tt: pd.DataFrame):
        _, e_by, lb05_by, lbn_by, _, flagged = bounds_at_n(tt, sub.days, sub.extra["cfg"], sub.n_led)
        return dict(e_by), dict(lb05_by), dict(lbn_by), bool(flagged)

    return rebound


def zero_twin(blocks: list, e_by: Mapping[float, float], frr: float, zero_edge_blocks: Callable | None = None
              ) -> tuple[list, dict, dict]:
    """The zero-edge twin's (blocks, e by R, the bound by R): every R's outcomes less its own e
    (`portfolio_stage.zero_edge_blocks`), e and the bound zero -- P-14's registered `zero_edge_twin` call."""
    if zero_edge_blocks is None:
        import portfolio_stage as ps

        zero_edge_blocks = ps.zero_edge_blocks
    zero = {k: 0.0 for k in e_by}
    return zero_edge_blocks(blocks, dict(e_by), float(frr)), zero, dict(zero)


def slice_campaign(sub: VS.Subject, name: str, blocks: list, e_by: Mapping[float, float],
                   lb05_by: Mapping[float, float], *, seed: int, strict_gap: float):
    """An arm's campaign in `customer_slices.Campaign`'s form, as `customer_slices.p13_campaign` builds P-14's slice
    campaign (the slices P-14's verdict read): the subject's engine arguments with e and the bound at 0.05 by R, P-13's
    seed and strict rule, no path count and no purchase budget among them (the budget is the slice call's argument)."""
    import customer_slices as cs

    kw = {k: v for k, v in sub.kw.items() if k not in ("n_paths", "purchase_budget")}
    kw.update(e_by_rr=dict(e_by), lb_by_rr=dict(lb05_by), e=float(e_by[sub.frr]), lb=float(lb05_by[sub.frr]),
              seed=int(seed), one_at_a_time=float(strict_gap))
    return cs.Campaign(name, list(blocks), [str(d) for d in sub.days], kw)


def summary_frame(rows: pd.DataFrame | Sequence[Mapping[str, Any]], config: str) -> pd.DataFrame:
    """A configuration's verdict-arm summary rows (`customer_slices.summarise`' form) out of a registered file's
    `slices` section."""
    d = pd.DataFrame(rows)
    d = d[(d["config"].astype(str) == config) & (d["arm"].astype(str) == "verdict")].copy()
    d["horizon"] = d["horizon"].astype(float).astype(int)
    return d.reset_index(drop=True)


def slice_lines_of(summary: pd.DataFrame, fv3c: pd.DataFrame, name: str, slice_lines: Callable
                   ) -> tuple[list[dict], bool]:
    """D-509's four lines (`a3_brk30_cb20.slice_lines`) of `name`'s summary against FV3-C's frozen summary."""
    both = pd.concat([summary, fv3c], ignore_index=True)
    lines = slice_lines(both, candidate=name, reference="fv3c")
    return lines, bool(all(r["holds"] for r in lines))


def summary_problems(mine: pd.DataFrame, theirs: pd.DataFrame, cols: Sequence[str], same: Callable) -> list[str]:
    """The base arm's slice summary against P-14's registered `slices` rows, horizon for horizon, every column."""
    out = []
    a, b = mine.set_index("horizon"), theirs.set_index("horizon")
    if sorted(a.index) != sorted(b.index):
        return [f"horizons {sorted(a.index)} against the registered {sorted(b.index)}"]
    for h in sorted(a.index):
        out += [f"horizon {h} {c}: {a.loc[h, c]!r} against {b.loc[h, c]!r}" for c in cols
                if not same(a.loc[h, c], b.loc[h, c])]
    return out


def lines_problems(mine: Sequence[Mapping[str, Any]], theirs: pd.DataFrame, same: Callable) -> list[str]:
    """The base arm's four lines against P-14's registered `slice_lines` rows (candidate, reference, holds)."""
    t = theirs.set_index(theirs["line"].astype(str))
    out = []
    for r in mine:
        if str(r["line"]) not in t.index:
            out.append(f"line {r['line']}: not registered")
            continue
        o = t.loc[str(r["line"])]
        out += [f"line {r['line']} {k}: {r[k]!r} against {o[k]!r}" for k in ("candidate", "reference", "holds")
                if not same(r[k], o[k])]
    return out


def slip_b_row(sub: VS.Subject, a: Mapping[str, Any], level: str, arm: str, res: Mapping[str, dict],
               ref: Mapping[str, dict], twin: Mapping[str, dict], e_by: Mapping[float, float],
               lb_by: Mapping[float, float], flagged: bool, lines: Sequence[Mapping[str, Any]] | None,
               lines_hold: bool | None, resolution: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """One arm at one bound level, one engine arm: D-583's readings (section `slip_b`)."""
    r, tw = res[arm], twin["point"]
    lv = {LEVEL_VERDICT: f"0.05/{sub.n_led} by the era rule (P-14's verdict level; the existing reading's, fixed in "
                         f"scripts/p14_validation.py, in no decision row)",
          LEVEL_D583: "0.05 by the era rule (Stage 2 D-583's own level)"}[level]
    row = {"section": "slip_b", "subject": sub.name, "scheme": a["arm"], "family": a["family"], "level": int(a["level"]),
           "bound_level": level, "bound_level_text": lv,
           "arm": (sub.arm_names[arm] if level == LEVEL_VERDICT else "bound (0.05)") if arm == "bound" else "point",
           "entry_slip_ticks": int(a["entry_slip_ticks"]), "stop_slip_ticks": int(a["stop_slip_ticks"]),
           "flatten_slip_ticks": int(a["flatten_slip_ticks"]), "target_slip_ticks": int(a["target_slip_ticks"]),
           **ruin_columns(r, ref[arm]),
           "growth_above_zero": bool(np.isfinite(float(r["pf_growth_on_base_p50"]))
                                     and float(r["pf_growth_on_base_p50"]) > 0),
           "share_accounts_ever_paid": r.get("share_accounts_ever_paid", float("nan")),
           "v1_payouts_per_path_p50": r.get("v1_payouts_per_path_p50"),
           "median_days_to_first_payout": r.get("median_days_to_first_payout"),
           "mean_combine_purchases": r.get("mean_combine_purchases"),
           "share_payouts_exposed": r.get("share_payouts_exposed", float("nan")),
           "growth_zero_edge_twin": tw.get("pf_growth_on_base_p50"),
           "twin_share_accounts_ever_paid": tw.get("share_accounts_ever_paid", float("nan")),
           "twin_required_p90": tw.get("pf_required_p90"),
           "e_fresh_funded_r": float(e_by[sub.frr]), "bound_fresh_funded_r": float(lb_by[sub.frr]),
           "e_fresh_combine_r": float(e_by[sub.crr]), "bound_fresh_combine_r": float(lb_by[sub.crr]),
           "era_flagged": bool(flagged),
           "every_offered_r_resolves": bool(all(bool(x["resolves"]) for x in resolution)) if resolution else None,
           "resolution_worst_unresolved": (float(max(float(x["unresolved"]) for x in resolution)) if resolution
                                           else float("nan")),
           "slice_lines_hold": lines_hold,
           "slice_lines_level": "0.05 by the era rule (P-14's registered slices' level, D-583's)"}
    for x in lines or ():
        row[f"slice_{x['line']}_{x['measure']}"] = x["candidate"]
        row[f"slice_{x['line']}_{x['measure']}_fv3c"] = x["reference"]
        row[f"slice_{x['line']}_holds"] = bool(x["holds"])
    return row


def slip_readings(rows: Sequence[Mapping[str, Any]], sub_arm_names: Mapping[str, str]) -> list[dict]:
    """D-583's fixed reading (`p16_slip_stress.reading`) per bound level: the bound arm's rows by family -- the lowest
    level with growth at the bound at or below zero, the highest at which all four slice lines hold."""
    out = []
    for level in (LEVEL_VERDICT, LEVEL_D583):
        mine = [{"arm": r["scheme"], "family": r["family"], "level": r["level"],
                 "growth_on_required": float(r["pf_growth_on_base_p50"]), "slice_lines_hold": r["slice_lines_hold"]}
                for r in rows if r["section"] == "slip_b" and r["bound_level"] == level and r["arm"] != "point"]
        for x in ps16.reading(mine):
            out.append({**x, "section": "slip_reading_b", "bound_level": level, "arms": x["arms"],
                        "note": "Stage 2 D-583's reading, literally: no interpolation, no level chosen after"})
    return out


def part_slip_b(eng: Engine, reg: dict[str, dict], reg05: dict[str, dict], rebound: Callable,
                slices: Callable[[str, list, dict, dict], tuple[pd.DataFrame, list[dict], bool]],
                resolution: Callable[[pd.DataFrame], list[dict]], zero_edge_blocks: Callable | None = None
                ) -> tuple[list[dict], list[dict], dict[str, str]]:
    """D-583's nine arms (`p16_slip_stress.arms`): each at P-14's verdict level (`slip <arm>`, the existing reading's
    label, so a re-run it reproduces) and at D-583's level (`slip05 <arm>`; the base is the registered call at 0.05),
    its zero-edge twin (`twin <arm>`), its slices at the 0.05 bound (`slices`: (summary, lines, all hold)) and its
    resolution. (rows of sections slip_b and slip_b_slices, the run labels' references for `ruin_rows`)."""
    sub = eng.sub
    rows, srows, refs = [], [], {}
    for a in ps16.arms():
        name = a["arm"]
        if name == "base":
            if any(v != 0 for v in ps16.added_ticks(a).values()):
                raise refused("D-583's base arm adds ticks.")
            tt, blocks = sub.t, list(sub.blocks)
            e_by, lb05, lbn, flagged = dict(sub.e_by), dict(sub.extra["lb05_by"]), dict(sub.lb_by), bool(
                sub.extra["flagged"])
            res_n, res_05 = reg, reg05
        else:
            tt = ps16.stress(sub.t, a)
            bad = ps16.cost_problems(sub.t, tt, a)
            if bad:
                raise refused(f"the stressed trades are not D-583's arm {name} -- " + "; ".join(bad[:6]))
            e_by, lb05, lbn, flagged = rebound(tt)
            blocks = sub.rebuild(tt)
            res_n = eng.run(f"slip {name}", blocks=blocks, e_by=dict(e_by), lb_by=dict(lbn))
            res_05 = eng.run(f"slip05 {name}", blocks=blocks, e_by=dict(e_by), lb_by=dict(lb05))
            refs[f"slip {name}"], refs[f"slip05 {name}"] = "registered", "registered at 0.05"
        zb, ze, zl = zero_twin(blocks, e_by, sub.frr, zero_edge_blocks)
        twin = eng.run(f"twin {name}", blocks=zb, e_by=ze, lb_by=zl)
        refs[f"twin {name}"] = "twin base"
        summ, lines, hold = slices(name, blocks, e_by, lb05)
        srows += [{**r, "section": "slip_b_slices", "subject": sub.name, "scheme": name}
                  for r in pd.DataFrame(summ).to_dict("records")]
        srows += [{**r, "section": "slip_b_lines", "subject": sub.name, "scheme": name} for r in lines]
        res_rows = resolution(tt)
        for level, res, ref, lb in ((LEVEL_VERDICT, res_n, reg, lbn), (LEVEL_D583, res_05, reg05, lb05)):
            for arm in ("bound", "point"):
                if level == LEVEL_D583 and arm == "point":
                    continue                        # the point arm reads e, not the bound: one row (the verdict level's)
                rows.append(slip_b_row(sub, a, level, arm, res, ref, twin, e_by, lb, flagged, lines, hold, res_rows))
        print(f"  {sub.name} D-583's readings {name}: done", flush=True)
    return rows, srows, refs


# ------------------------------------------------------------------------------------------------ the assumptions


def assumption_rows(sub: VS.Subject, *, payout_lag_days: int | None, payout_method: str | None,
                    fills_profile: str | None,
                    base_ticks: Mapping[str, int], plan_id: str | None) -> list[dict]:
    """E-125 caveat 4: each standing assumption of every run here, read from the engine call (`sub.kw`) it describes;
    the text says where it comes from and what it means for the figures."""
    kw = sub.kw
    proto = kw.get("protocol")
    rules = kw.get("rules")
    levels = tuple(float(x) for x in kw.get("levels", ()))

    def row(key: str, value: Any, source: str, meaning: str) -> dict:
        return {"section": "assumptions", "subject": sub.name, "assumption": key, "value": json.dumps(value,
                default=str), "source": source, "meaning": meaning}

    return [
        row("payout_denial", list(levels), "the engine call's denial levels (gate.run_gate levels)",
            "every figure at 0 % payout denial: no payout is refused for stacking, excessive purchases or the "
            "catch-all (Stage 2 D-145 tier 3 priced at 0 %; the verdict's reading, CHARTER section 2)"),
        row("placement", bool(kw.get("rtp", False)), "the engine call's rtp (Stage 2 D-289)",
            "the Responsible Trading Program's placement off: no tier-2 consequence applied (D-289's base case)"),
        row("focused_trader", "focused_trader" in kw, "the engine call (Stage 2 D-497: off, not passed)",
            "the Focused Trader Program off"),
        row("fills", {"profile": fills_profile, "base_ticks": dict(base_ticks)},
            "config/fills.yaml's active profile; D-583's base ticks (fv3_rung_walk.EXIT_TICKS)",
            "the fill model is ASSUMED, never measured (D-95); only slippage is stressed (D-583's arms), commissions, "
            "the trade-through target fill and the stop-first tie are not"),
        row("payout_model", {"payout_path": getattr(proto, "payout_path", None),
                             "payout_frac": getattr(proto, "payout_frac", None),
                             "keep_balance": getattr(proto, "keep_balance", None),
                             "payout_method": payout_method, "payout_lag_days": payout_lag_days,
                             "payout_timing": kw.get("payout_timing", "default"),
                             "subscription": getattr(rules, "subscription", None)},
            "the engine call's protocol and rules (rules_for_method; the lag from the verified ledger)",
            "payouts on the protocol's path, lag and timing as modelled; nothing here tests the firm paying"),
        row("purchase_budget", kw.get("purchase_budget"), "the engine call (a3_brk30_cb20.BUDGET, Stage 2 D-502)",
            "at most this many Combine purchases and resets in this many trading days"),
        row("strict_rule_minutes", kw.get("one_at_a_time"), "the engine call (a3_brk30_cb20.STRICT_GAP, D-429)",
            "the strict one-at-a-time rule: one trade at a time across accounts, this gap in minutes"),
        row("state_table", plan_id, "rc_screen.inputs' plan (a3_brk30_cb20.noclose_plan, pinned)",
            "the no-closure state table, solved at the base costs and frozen under every stress"),
        row("bankroll", kw.get("bankroll"), "score_fv3_grid.bankroll_of (Stage 2 D-312: the bankroll an output)",
            "cash never binds; growth is read on the required bankroll's p90 and ruin is zero by construction"),
        row("breakeven_move", "the stop to the entry at the next FV3 session open when that open is a tick or more in "
                              "favour (fv3_rung_walk, FV3's rule)",
            "propedge/research/fv3_rung_walk.py's Breakeven; E-007's red team",
            "modelled at zero latency; E-007's red team found it matches Topstep's tier-1 'auto-breakeven' wording "
            "(10305426); every figure assumes the move is allowed as made"),
    ]


# ------------------------------------------------------------------------------------------------ the file's identity


def same_cell(new: Any, old: Any) -> bool:
    """A re-made row's value against the CSV's (read as text-faithful as `pd.read_csv(keep_default_na=False,
    na_values=[''], float_precision='round_trip')` gives it): a missing value against a blank; a flag as its word;
    a number exactly; text as text."""
    old_na = old is None or (isinstance(old, float) and np.isnan(old))
    if new is None or (isinstance(new, (float, np.floating)) and np.isnan(new)) or (isinstance(new, str) and new == ""):
        return old_na
    if old_na:
        return False
    if isinstance(new, (bool, np.bool_)):
        return str(bool(new)) == str(old)
    if isinstance(new, (int, float, np.integer, np.floating)):
        try:
            return float(new) == float(old)
        except (TypeError, ValueError):
            return False
    return str(new) == str(old)


def read_file(path: Path) -> pd.DataFrame:
    """The CSV as written: blanks missing, every other cell as its text gives it, floats to their last digit."""
    return pd.read_csv(path, keep_default_na=False, na_values=[""], float_precision="round_trip", low_memory=False)


def file_problems(rows: Sequence[Mapping[str, Any]], old: pd.DataFrame, sections: Sequence[str]) -> list[str]:
    """Every re-made row of `sections` against the file's rows of that section, in order, every key it carries."""
    out = []
    for sec in sections:
        mine = [r for r in rows if r.get("section") == sec]
        theirs = old[old["section"].astype(str) == sec].reset_index(drop=True)
        if len(mine) != len(theirs):
            out.append(f"{sec}: {len(mine)} rows against the file's {len(theirs)}")
            continue
        for i, r in enumerate(mine):
            o = theirs.iloc[i]
            for k, v in r.items():
                if k not in o.index:
                    if not same_cell(v, None):
                        out.append(f"{sec} row {i} {k}: {v!r}, a column the file lacks")
                elif not same_cell(v, o[k]):
                    out.append(f"{sec} row {i} {k}: {v!r} against the file's {o[k]!r}")
    return out


def registered_extra_problems(res: Mapping[str, dict], ref: Mapping[str, pd.Series], cols: Sequence[str] = EXTRA
                              ) -> list[str]:
    """The registered call's `EXTRA` columns against the registered file's rows, exactly (each column the file has)."""
    out = []
    for arm, _ in VS.ARMS:
        for c in cols:
            if c not in ref[arm].index or pd.isna(ref[arm][c]):
                continue
            a, b = res[arm].get(c), float(ref[arm][c])
            if a is None or not (float(a) == b or (np.isnan(float(a)) and np.isnan(b))):
                out.append(f"{arm} {c}: {a!r} against the registered {b!r}")
    return out


# ------------------------------------------------------------------------------------------------ provenance


def file_manifest(path: Path, **about: Any) -> Path:
    """A sidecar manifest for a file this run keeps outside `results/` (the resume file, E-125 caveat 5): its sha256,
    size, line count and what it is, beside it as `<name>.manifest.json`."""
    p = Path(path)
    data = p.read_bytes()
    man = {"file": p.name, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
           "lines": int(sum(1 for x in data.splitlines() if x.strip())), **about}
    out = p.with_name(p.name + ".manifest.json")
    out.write_text(json.dumps(man, indent=2, default=str) + "\n", encoding="utf-8")
    return out


__all__ = ["WHO", "EXTRA", "REQUIRED", "RUIN_FORM", "LEVEL_VERDICT", "LEVEL_D583", "refused", "Engine", "share_above",
           "ruin_columns", "ruin_rows", "part_a2", "a2_path_sets", "rebound_both", "zero_twin", "slice_campaign",
           "summary_frame", "slice_lines_of", "summary_problems", "lines_problems", "slip_b_row", "slip_readings",
           "part_slip_b", "assumption_rows", "same_cell", "read_file", "file_problems", "registered_extra_problems",
           "file_manifest", "VS", "V", "ps16"]
