"""EXPLORATORY (D-663, V1): block-resampled days, the bound's calibration and execution stress on the two best results --
P-16's registered development gate (S1) and FV3-C's confirmation P-06 (S2). Read beside the registered verdicts; changes
no verdict, selects nothing, creates no candidate.

    python scripts/v1_validation.py --check                       # a smoke of every part at 4 paths and a few
                                                                  #   replicates: each subject's registered call path
                                                                  #   reproduced path for path; no reading printed;
                                                                  #   nothing written
    python scripts/v1_validation.py --check --part A1 --subject S2
    python scripts/v1_validation.py --part all --workers 1        # the declared run (a clean checkout, D-474), in the
                                                                  #   order A1 B2 A0 B1 A2 C1 C2 B3, a file a part

**The declaration** is DECISIONS.md's D-663 row, read as text, its sha256 pinned
(`propedge.research.v1_validation.DECLARATION_SHA256`) and every constant checked against its words; a difference refuses
every run, --check included.

**The subjects' engine calls are their registered ones.** S1: P-16's cell rebuilt (`rc_stop_walkforward.walk_stop` /
`cell`; content hash `rc150_dev_test.TRADES_SHA256`), its bounds by the era rule at 0.05 and 0.05/414
(`a3_brk30.bounds_at_n`), `atlas_a3.gate_kwargs` exactly as `rc_dev_test.run`'s `gate_at_ledger_n` arm calls it (the
no-closure table, 20 purchases and resets in 21 days, the strict rule, five seats, the placement off, 0 %), the
registered seed `rc150_dev_test.SEED`. One call gives the verdict arm (the bound at 0.05/414) and the point arm. S2:
P-06's trades, blocks, policy and `gate.run_gate` arguments rebuilt as `scripts/fv3c_confirmation_path_detail.py`
rebuilds them (`score_fv3_grid.run_gate`'s placement-off call at 0 % alone), the registered seed
(`config/fv3_corrected_portfolio.yaml` `seeds.gate`). **Identity, refusing, before any reading:** with `mean_block` off
each subject's row equals its registered file's on `IDENT_COLS` at 500 paths (in --check: its first paths equal the
registered per-path file's, `zero_edge_decomposition.path_problems`).

**The parts** (`propedge/research/v1_validation.py`'s docstring states every reading):
A0 dependence of the day series; A1 the gate at mean blocks 1, 5, 21, 63; A2 the real-order replay from every 21st
session over 252 sessions against each scheme's resampled paths through the same replay-form call
(`customer_slices.engine_args` / `replay`); B1 the bound's coverage; B2 the break-even e; B3 the familywise false pass
of FV3's 32-cell screen (`gate4_checks`' matrices and walk-forward), P-16's stop family recorded not done; C1 missed
trades and sessions; C2 D-583's slippage families on FV3-C by exit kind.

**Resume** (D-540's form): each finished engine run kept outside the checkout, keyed by commit and paths; off in --check.

Writes `results/v1_validation_<part>.csv` (EXPLORATORY) with its manifest, a part a file, each when its part finishes.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

if __name__ == "__main__":                 # one BLAS thread, before numpy loads (D-464 (5))
    for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from propedge.research import v1_validation as V  # noqa: E402

SCRIPT = "scripts/v1_validation.py"
DECISION = V.DECISION
CHECK_PATHS = 4
CHECK_REPS = 2000                          # --check: B1's replicates
CHECK_B3_REPS = 20
CHECK_STARTS = 2                           # --check: A2's real-order starts and, x2, its paths a scheme
S1_FILE, S1_PATHS = "rc_s150_all_gate.csv", "rc_s150_all_gate_paths.csv"
S2_FILE, S2_PATHS = "fv3_confirmation.csv", "fv3_confirmation_paths.csv"
S2_RUN = "gate placement off"
#: the registered row's columns the reproduction must equal, to the last digit
IDENT_COLS = ("mean_r_used", "pf_growth_on_base_p50", "pf_required_p50", "pf_required_p90", "pf_required_p99",
              "median_log_growth", "mean_final_cash", "median_final_cash", "mean_max_drawdown", "p90_max_drawdown",
              "mean_combine_purchases")
#: a run's readings (design, part A1), each beside the registered run's and as a difference
READ = ("pf_growth_on_base_p50", "pf_required_p90", "pf_required_p50", "pf_required_p99", "v1_share_below_start",
        "mean_max_drawdown", "v1_payout_drought_p90", "v1_payouts_per_path_p50", "mean_combine_purchases")
BESIDE = ("mean_r_used", "paths", "horizon_days", "v1_net_p10", "v1_net_p50", "median_days_to_first_payout",
          "mean_accounts_funded", "growth_se", "required_p90_se", "mc_resamples")
ARMS = (("bound", "lower_bound"), ("point", "point"))
B1_CHUNK_CELLS = 3_000_000                 # B1: days x R x replicates gathered at once (memory, not a result)


# ------------------------------------------------------------------------------------------------ resume (D-540)


class Resume:
    """`rc_robust.Resume`'s form under this study's own file name: each finished engine run's rows, outside the checkout."""

    def __init__(self, folder: Path | None, key: str):
        self.path = None if folder is None else Path(folder) / f"{V.RESULT}_{key}.jsonl"
        self.rows: dict[str, Any] = {}
        if self.path is not None and self.path.is_file():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    r = json.loads(line)
                    self.rows[r["_label"]] = r["row"]
            print(f"  resume: {len(self.rows)} finished run(s) read from {self.path}", flush=True)

    def get(self, label: str):
        return self.rows.get(label)

    def put(self, label: str, row: Any) -> None:
        self.rows[label] = row
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps({"_label": label, "row": row}) + "\n")


def _plain(x: Any) -> Any:
    if isinstance(x, (np.bool_, bool)):
        return bool(x)
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, (np.floating, float)):
        return float(x)
    if x is None or isinstance(x, (int, str)):
        return x
    return str(x)


def _cached(resume: Resume | None, label: str, make: Callable[[], Any]) -> Any:
    """The run's rows from the resume file, or made now and kept -- as they read back from JSON either way."""
    row = resume.get(label) if resume is not None else None
    if row is None:
        row = json.loads(json.dumps(make()))
        if resume is not None:
            resume.put(label, row)
    return row


# ------------------------------------------------------------------------------------------------ the subjects


@dataclass
class Subject:
    """One subject's registered campaign: its trades, day set, bounds, blocks and `gate.run_gate` arguments (all but the
    blocks, the path hook and the path count), and what its identity is read against."""
    name: str
    describe: str
    t: pd.DataFrame
    days: list[str]
    keys: list[float]
    tv: float
    e_by: dict[float, float]
    lb_by: dict[float, float]              # the verdict arm's bound by R (S1: 0.05/414 by the era rule; S2: 0.05)
    kw: dict[str, Any]
    blocks: list
    margin: float
    block_days: int
    crr: float
    frr: float
    n_led: int
    alpha_verdict: float
    seed: int
    hook_base: Callable[[list], tuple[Any, Any]]
    arm_names: dict[str, str]
    ref_file: str
    ref_rows: Callable[[pd.DataFrame], dict[str, pd.Series]]
    ref_paths: str
    ref_pairs: dict[str, tuple[str, str]]  # our arm -> (the per-path file's run label, its shift)
    full: bool = True                      # False: a --check day subset, the registered files not comparable
    extra: dict[str, Any] = field(default_factory=dict)

    def rebuild(self, t: pd.DataFrame) -> list:
        """The blocks of a changed trade set on this subject's own day set, as its registered run builds them."""
        import score_fv3_grid as gf

        blocks, n_used = gf.gate_blocks(t, self.days, self.tv, self.keys, require_sides=True, require_exits=True)
        if n_used != len(t):
            raise SystemExit(f"REFUSED ({DECISION}): the blocks hold a different number of trades.")
        return blocks


def smoke_days(L: dict, n: int) -> dict:
    """--check --days: the first n/2 walked sessions of 2020-2023 and of 2024 on (`p16_robust`'s smoke)."""
    import a3_resolution_map as m0

    dk = L["days"].copy()
    dk["date"] = dk["date"].astype(str)
    walked = sorted(dk.loc[dk["day_kind"].astype(str).isin(m0.WALK_DAY_KINDS), "date"])
    half = max(int(n) // 2, 1)
    pick = set([d for d in walked if d <= "2023-12-31"][:half] + [d for d in walked if d >= "2024-01-01"][:half])
    return {**L, "days": dk[dk["date"].isin(pick)].reset_index(drop=True)}


def build_s1(check_days: int | None = None) -> Subject:
    import a3_brk30 as B
    import a3_brk30_cb20 as C
    import atlas_a3 as A
    import fv3d_lever_test as lt
    import portfolio_stage as ps
    import rc150_dev_test as R150
    import rc_dev_test as D
    import rc_screen as S
    import rc_stop_walkforward as WF
    import score_fv3_grid as gf

    I = S.inputs()
    if check_days is not None:
        I = {**I, "L": smoke_days(I["L"], check_days)}
    L = I["L"]
    cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
    W = WF.walk_stop(I, R150.STOP)
    days = list(W["days"])
    t = WF.cell(W, R150.STOP, days)["trades"]
    if t is None or not len(t):
        raise SystemExit(f"REFUSED ({DECISION}): P-16's cell has no trades on these days.")
    full = check_days is None
    if full and D.trades_hash(t) != R150.TRADES_SHA256:
        raise SystemExit(f"REFUSED ({DECISION}): the cell's content hash {D.trades_hash(t)[:16]} is not P-16's "
                         f"{R150.TRADES_SHA256[:16]}.")
    keys = [float(R) for R in B.rrs(t)]
    n_led = V.LEDGER_N["S1"]
    st, e_by, lb05_by, lbn_by, era_rows, flagged = B.bounds_at_n(t, days, cfg, n_led)
    blocks, n_used = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise SystemExit(f"REFUSED ({DECISION}): the blocks hold a different number of trades.")
    horizon = int(fcfg["gate"]["campaign"]["horizon_days"])
    kw = A.gate_kwargs(blocks, fcfg, tv, I["plan"], e_by, lbn_by, None, seed=R150.SEED, n_paths=V.N_PATHS,
                       horizon=horizon, capacity=B.capacity(t, fcfg), levels=(0.0,), rtp=False,
                       one_at_a_time=C.STRICT_GAP, purchase_budget=C.BUDGET)
    kw.pop("blocks")
    kw.pop("path_hook")
    pcfg = {"margin": float(fcfg["portfolio"]["margin"]), "block_days": int(fcfg["portfolio"]["block_days"])}

    def hook_base(sink: list):
        inner = ps.composed_hook(pcfg, sink=sink)
        return inner, lt.lever_hook(inner)

    def ref_rows(d: pd.DataFrame) -> dict[str, pd.Series]:
        zero = np.isclose(d["enforcement_p"].astype(float), 0.0)
        b = d[(d["section"].astype(str) == "gate_at_ledger_n") & (d["shift"].astype(str) == "lower_bound") & zero]
        p = d[(d["section"].astype(str) == "gate") & (d["shift"].astype(str) == "point") & zero]
        if len(b) != 1 or len(p) != 1:
            raise SystemExit(f"REFUSED ({DECISION}): {S1_FILE} holds {len(b)} verdict and {len(p)} point rows.")
        return {"bound": b.iloc[0], "point": p.iloc[0]}

    fr = fcfg["state_policy"]["fresh"]
    spans = tuple(tuple(int(y) for y in x) for x in cfg["bounds"]["eras"])
    return Subject(
        name="S1", describe="P-16 (rc_s150_all_nr): the registered development gate, the bound at 0.05/414",
        t=t, days=days, keys=keys, tv=tv, e_by=dict(e_by), lb_by=dict(lbn_by), kw=kw, blocks=list(blocks),
        margin=pcfg["margin"], block_days=int(cfg["bounds"]["block_days"]), crr=float(fr["combine_rr"]),
        frr=float(fr["funded_rr"]), n_led=n_led, alpha_verdict=V.ALPHA / n_led, seed=int(R150.SEED),
        hook_base=hook_base, arm_names={"bound": "verdict (0.05/414)", "point": "point"}, ref_file=S1_FILE,
        ref_rows=ref_rows, ref_paths=S1_PATHS,
        ref_pairs={"bound": ("gate_at_ledger_n", "lower_bound"), "point": ("gate", "point")}, full=full,
        extra={"lb05_by": dict(lb05_by), "flagged": bool(flagged), "era_spans": spans, "pooled": st,
               "trades_sha256": D.trades_hash(t), "plan": getattr(I["plan"], "id", None)})


def build_s2() -> Subject:
    """P-06's campaign as `scripts/fv3c_confirmation_path_detail.py` rebuilds it (`confirm_fv3.main`'s own steps)."""
    import confirm_fv3 as cf
    import portfolio_stage as ps
    import score_fv3_grid as gf

    from propedge import RESULTS_DIR
    from propedge.campaign.payout_method import rules_for_method
    from propedge.campaign.protocols import Protocol
    from propedge.data.orb_kit import params
    from propedge.execution.fills import FillModel
    from propedge.reporting.results import read_result
    from propedge.research.model_card import BAND_FILE, setups_minimum

    rd, rund = RESULTS_DIR, ROOT / "runs"
    conf = cf.config()
    states = {str(p["id"]): cf.period_state(p, rd, rund) for p in conf["periods"]}
    chosen = {k: run for k, (s, run, _) in states.items() if s == "ingested"}
    cand = cf.candidate(conf)
    sig, ses, _bench, sessions_by, window_days, label_of_day = cf.load_window(conf, cand, chosen, rd, rund)
    fm = FillModel.load("assumed")
    q = params("NQ")
    tv = q["micro_tick"] * q["micro_point_value"]
    S = gf.Signals3(sig, float(fm.round_turn_by_instrument[q["micro"]]), float(fm.round_turn_by_instrument["NQ"]), tv,
                    cand["ladder"])
    S.year = np.array([label_of_day[str(d)] for d in S.df["date"]], dtype=int)
    fresh = cand["state_policy"]["fresh"]
    need = setups_minimum(float(fresh["combine_rr"]), float(fresh["combine_risk"]), 0.0)
    ev = gf.EvaluatedFV3(S, ses, cand, sessions_by, read_result(BAND_FILE), float(need))
    sels = {int(y): 0 for y in ev.years}
    t = gf.gate_trades(S, ev, sels, ev.cells[0])
    menu = [float(R) for R in gf.rr_menu(cand)]
    n_led = int(conf["ledger_n"])
    if n_led != V.LEDGER_N["S2"]:
        raise SystemExit(f"REFUSED ({DECISION}): P-06's ledger N is {n_led}, the declaration's {V.LEDGER_N['S2']}.")
    block_days = int(conf["block_days"])
    stats = cf.edge_stats(t, menu, window_days, block_days, n_led)
    fr = float(fresh["funded_rr"])
    blocks, n_used = gf.gate_blocks(t, window_days, tv, menu, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise SystemExit(f"REFUSED ({DECISION}): the blocks hold a different number of trades.")
    policy, _, pol_id = gf.policy_for_edge(cand, stats[fr]["lb"])
    camp = cand["gate"]["campaign"]
    if bool(camp["rtp"]):
        raise SystemExit(f"REFUSED ({DECISION}): the frozen candidate's base case is not placement off.")
    protocol = Protocol(name="fv3", combine_rr=float(fresh["combine_rr"]), combine_risk=float(fresh["combine_risk"]),
                        funded_rr=float(fresh["funded_rr"]), funded_risk=float(fresh["funded_risk"]),
                        trades_per_day=gf.MAX_PER_DAY, payout_path="standard", keep_balance=0.0, payout_frac=1.0,
                        max_concurrent_accounts=int(camp["accounts"]), family="fv3", source="config/fv3_grid.yaml",
                        note="FV3's gate under the state policy (D-290)", params=gf.protocol_params(cand))
    e_by = {R: float(stats[R]["e"]) for R in menu}
    lb_by = {R: float(stats[R]["lb"]) for R in menu}
    f = gf.fidelity_of(cand)
    # score_fv3_grid.run_gate's placement-off call, its arguments unchanged, at 0 % denial only
    kw = dict(e=e_by[fr], lb=lb_by[fr], protocol=protocol, bankroll=gf.bankroll_of(cand),
              horizon_days=int(camp["horizon_days"]), n_paths=int(camp["n_paths"]), seed=int(cand["seeds"]["gate"]),
              accounts=int(camp["accounts"]), sizing=gf.sizing_rule(cand, tv),
              rules=rules_for_method(camp["payout_method"]), mode=camp["mode"], settlement=camp["settlement"],
              combines=int(camp["combines"]), total_accounts=int(camp["accounts"]), risk_policy=policy,
              e_by_rr=e_by, lb_by_rr=lb_by, rtp=False, routing=f["routing"],
              cross_account=bool(f.get("cross_account_rule", False)), flip=gf.flip_spec_of(cand),
              hold_to_own_exit=bool(f.get("hold_to_own_exit", False)), levels=(0.0,))
    if int(kw["n_paths"]) != V.N_PATHS:
        raise SystemExit(f"REFUSED ({DECISION}): P-06 ran {kw['n_paths']} paths, the declaration says {V.N_PATHS}.")
    pcfg = cand["portfolio"]

    def hook_base(sink: list):
        inner = ps.composed_hook(pcfg, sink=sink)
        return inner, inner

    def ref_rows(d: pd.DataFrame) -> dict[str, pd.Series]:
        g = d[(d["section"].astype(str) == "gate") & (d["placement"].astype(str) == "off")
              & np.isclose(d["enforcement_p"].astype(float), 0.0)]
        b, p = g[g["shift"].astype(str) == "lower_bound"], g[g["shift"].astype(str) == "point"]
        if len(b) != 1 or len(p) != 1:
            raise SystemExit(f"REFUSED ({DECISION}): {S2_FILE} holds {len(b)} bound and {len(p)} point rows.")
        return {"bound": b.iloc[0], "point": p.iloc[0]}

    return Subject(
        name="S2", describe="FV3-C's confirmation P-06: the gate's placement-off arm at 0 %, the bound at 0.05",
        t=t, days=list(window_days), keys=menu, tv=float(tv), e_by=e_by, lb_by=lb_by, kw=kw, blocks=list(blocks),
        margin=float(pcfg.get("margin", 49.0)), block_days=block_days, crr=float(fresh["combine_rr"]), frr=fr,
        n_led=n_led, alpha_verdict=V.ALPHA, seed=int(kw["seed"]), hook_base=hook_base,
        arm_names={"bound": "bound (0.05)", "point": "point"}, ref_file=S2_FILE, ref_rows=ref_rows,
        ref_paths=S2_PATHS, ref_pairs={"bound": (S2_RUN, "lower_bound"), "point": (S2_RUN, "point")},
        extra={"stats": stats, "S": S, "ev": ev, "sels": sels, "cand": cand, "policy_id": pol_id,
               "lb_at_n_by": {R: float(stats[R]["lb_at_n"]) for R in menu}})


# ------------------------------------------------------------------------------------------------ the engine call


class Engine:
    """A subject's registered engine call, with what a part may change: the blocks, each R's e and bound, the mean
    block. Every run's rows keep `READ`, `BESIDE` and `IDENT_COLS`; its per-path record stays here for the identity."""

    def __init__(self, sub: Subject, n_paths: int, workers: int, resume: Resume | None):
        self.sub, self.n_paths, self.workers, self.resume = sub, int(n_paths), int(workers), resume
        self.sink: list[dict] = []
        self.inner, base = sub.hook_base(self.sink)
        self.values: dict[str, dict[str, np.ndarray]] = {}

        def hook(shift: str, p: float, paths) -> dict:
            out = dict(base(shift, p, paths))
            out.update(V.path_readings(paths, sub.margin))
            v = V.path_values(paths, sub.margin)
            days = len(paths[0].path.cash_series) if len(paths) else 0
            g, b = V.growth_on_required(v["net"], v["required"], days) if days else (float("nan"), float("nan"))
            want = out.get("pf_growth_on_base_p50")
            if days and np.isfinite(g) and want is not None and not np.isclose(g, float(want), rtol=1e-9, atol=1e-12):
                raise SystemExit(f"REFUSED ({DECISION}): growth on the required bankroll re-read from the paths "
                                 f"({g!r}) is not the hook's ({want!r}).")
            if days:
                out.update(V.mc_error(v["net"], v["required"], days, np.random.default_rng([V.SEED_B1, 9])))
            self.values[shift] = v
            return out

        self.hook = hook
        self.seconds: list[float] = []
        self.labels: list[str] = []            # every run asked for beyond the registered reproduction (the variants)

    def run(self, label: str, *, blocks: list | None = None, e_by: dict | None = None, lb_by: dict | None = None,
            mean_block: float | None = None) -> dict[str, dict]:
        """{'bound': row, 'point': row} of one `gate.run_gate` call (cached by `label`)."""
        if label != "registered" and label not in self.labels:
            self.labels.append(label)
        return _cached(self.resume, f"{self.sub.name} {label}",
                       lambda: self._run(label, blocks, e_by, lb_by, mean_block))

    def _run(self, label: str, blocks, e_by, lb_by, mean_block) -> dict[str, dict]:
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
        t0 = time.time()
        df, _ = gate.run_gate(sub.blocks if blocks is None else blocks, workers=self.workers, path_hook=self.hook,
                              **kw)
        self.seconds.append(time.time() - t0)
        out = {}
        for arm, shift in ARMS:
            r = df[df["shift"].astype(str) == shift]
            if len(r) != 1:
                raise SystemExit(f"REFUSED ({DECISION}): {len(r)} {shift} rows from one call.")
            r = r.iloc[0]
            out[arm] = {c: _plain(r[c]) for c in dict.fromkeys(READ + BESIDE + IDENT_COLS) if c in r.index}
        return out

    def path_problems(self, label: str, n: int) -> list[str]:
        """--check's identity: this call's first `n` paths against the registered per-path file's, both arms."""
        import zero_edge_decomposition as zd

        from propedge import RESULTS_DIR
        from propedge.reporting.results import read_result

        ref = read_result(RESULTS_DIR / self.sub.ref_paths)
        mine = f"{self.sub.name} {label}"
        pairs = [(mine, shift, *self.sub.ref_pairs[arm]) for arm, shift in ARMS]
        return zd.path_problems(self.sink, ref, pairs, int(n))


def row_problems(res: dict[str, dict], ref: dict[str, pd.Series]) -> list[str]:
    """The declared run's identity: the reproduction's rows against the registered file's on `IDENT_COLS`, exactly."""
    out = []
    for arm, _ in ARMS:
        for c in IDENT_COLS:
            if c not in ref[arm].index or c not in res[arm]:
                out.append(f"{arm} {c}: not on both rows")
                continue
            a, b = float(res[arm][c]), float(ref[arm][c])
            if not (a == b or (np.isnan(a) and np.isnan(b))):
                out.append(f"{arm} {c}: {a!r} against the registered {b!r}")
    return out


def reading_rows(section: str, sub: Subject, scheme: str, res: dict[str, dict], reg: dict[str, dict],
                 **more: Any) -> list[dict]:
    """A run's two arms as rows: every reading beside the registered run's and as a difference, and the sign of growth."""
    rows = []
    for arm, _ in ARMS:
        r, b = res[arm], reg[arm]
        g = float(r["pf_growth_on_base_p50"])
        row = {"section": section, "subject": sub.name, "arm": sub.arm_names[arm], "scheme": scheme, **more,
               **{c: r.get(c) for c in READ + BESIDE},
               **{f"registered_{c}": b.get(c) for c in READ},
               **{f"diff_{c}": (float(r[c]) - float(b[c])) if (r.get(c) is not None and b.get(c) is not None)
                  else float("nan") for c in READ},
               "growth_above_zero": bool(np.isfinite(g) and g > 0)}
        rows.append(row)
    return rows


def registered_run(eng: Engine, declared: bool) -> tuple[dict[str, dict], dict]:
    """The subject's registered call with the new option off, and its identity (refusing): at the declared path count
    the registered file's rows; in --check the registered per-path file's first paths."""
    import a3_brk30 as B

    from propedge import RESULTS_DIR

    sub = eng.sub
    fresh = eng.resume is None or eng.resume.get(f"{sub.name} registered") is None
    res = eng.run("registered")
    if declared:
        bad = row_problems(res, sub.ref_rows(B._exact(RESULTS_DIR / sub.ref_file)))
        if bad:
            raise SystemExit(f"REFUSED ({DECISION}): {sub.name}'s call with the option off is not {sub.ref_file} -- "
                             + "; ".join(bad[:8]))
        how = (f"at {eng.n_paths} paths and seed {sub.seed}, mean_block off, reproduces results/{sub.ref_file}'s "
               f"verdict and point rows on {', '.join(IDENT_COLS)} exactly")
    elif sub.full and fresh:
        bad = eng.path_problems("registered", eng.n_paths)
        if bad:
            raise SystemExit(f"REFUSED ({DECISION}): {sub.name}'s first {eng.n_paths} paths are not "
                             f"{sub.ref_paths}'s -- " + "; ".join(bad[:8]))
        how = f"the first {eng.n_paths} paths equal results/{sub.ref_paths}'s, both arms"
    else:
        how = "not comparable on a --check day subset"
    print(f"identity {'HOLDS' if 'not comparable' not in how else 'skipped'}: {sub.name}'s registered call -- {how}",
          flush=True)
    return res, {"section": "identity", "subject": sub.name, "holds": "not comparable" not in how,
                 "check": f"{sub.name} ({sub.describe}): {how}"}


# ------------------------------------------------------------------------------------------------ the parts


def part_a0(sub: Subject) -> list[dict]:
    sums, _ = V.day_sums(sub.t, sub.days, sub.keys)
    x = sums[:, sub.keys.index(sub.crr)]
    rows = V.dependence_rows({"day_r": x, "abs_day_r": np.abs(x), "sign": np.sign(x)})
    return [{**r, "subject": sub.name, "rr": sub.crr, "days": len(sub.days),
             "series_definition": "the day's summed net R over all offered trades at the fresh Combine's R"
                                  + {"day_r": "", "abs_day_r": ", its absolute value", "sign": ", its sign"}[r["series"]]}
            for r in rows]


def part_a1(eng: Engine, reg: dict[str, dict]) -> list[dict]:
    sub = eng.sub
    rows = reading_rows("a1", sub, "independent (registered)", reg, reg, mean_block=float("nan"))
    for L in V.MEAN_BLOCKS:
        t0 = time.time()
        res = eng.run(f"a1 mean_block {L}", mean_block=L)
        rows += reading_rows("a1", sub, f"stationary, mean block {L}", res, reg, mean_block=float(L),
                             control=bool(L == 1))
        print(f"  {sub.name} A1 mean block {L}: done ({time.time() - t0:.0f} s)", flush=True)
    return rows


def part_b2(eng: Engine, reg: dict[str, dict], max_steps: int) -> list[dict]:
    sub = eng.sub
    rows, shifts = [], V.b2_shifts()[: max_steps + 1]
    for scheme, L in (("independent", None), (f"stationary, mean block {V.B2_MEAN_BLOCK}", V.B2_MEAN_BLOCK)):
        curve, done = [], False
        for k, s in enumerate(shifts):
            if done:
                break
            if k == 0 and L is None:
                res = reg
            elif k == 0:                               # A1's run at this mean block: one run, one label
                res = eng.run(f"a1 mean_block {L}", mean_block=L)
            else:
                lb = {R: float(v) + s for R, v in sub.lb_by.items()}
                res = eng.run(f"b2 {scheme} step {k}", lb_by=lb, mean_block=L)
            g = float(res["bound"]["pf_growth_on_base_p50"])
            curve.append((s, g))
            rows.append({"section": "b2_curve", "subject": sub.name, "arm": sub.arm_names["bound"], "scheme": scheme,
                         "mean_block": float(L) if L is not None else float("nan"), "step": k, "shift_r": s,
                         "bound_fresh_funded_r": float(sub.lb_by[sub.frr]) + s,
                         **{c: res["bound"].get(c) for c in READ + BESIDE},
                         "growth_above_zero": bool(np.isfinite(g) and g > 0)})
            done = len(curve) >= 2 and not (np.isfinite(curve[-2][1]) and curve[-2][1] > 0)
            print(f"  {sub.name} B2 {scheme} step {k}: done", flush=True)
        be = V.break_even(curve)
        rows.append({"section": "b2", "subject": sub.name, "arm": sub.arm_names["bound"], "scheme": scheme,
                     "mean_block": float(L) if L is not None else float("nan"),
                     "registered_bound_fresh_funded_r": float(sub.lb_by[sub.frr]),
                     "break_even_e_fresh_funded_r": float(sub.lb_by[sub.frr]) + float(be["break_even_shift"]), **be,
                     "note": "every R's outcomes shifted by the same amount below its registered bound "
                             "(gate.shifted_blocks, as the registered arm shifts); the sizing table frozen, not "
                             "re-solved; no extrapolation past the declared steps"})
    return rows


def _era_positions(sub: Subject) -> list[np.ndarray]:
    yrs = np.array([int(str(d)[:4]) for d in sub.days])
    return [np.nonzero((yrs >= lo) & (yrs <= hi))[0] for lo, hi in sub.extra["era_spans"]]


def _materialise(sub: Subject, rows_by_day: list[np.ndarray], hist: np.ndarray) -> tuple[pd.DataFrame, list[str]]:
    """A resampled history as a trade table on its own calendar, for the registered functions."""
    take = [rows_by_day[h] for h in hist]
    lab = np.repeat([f"p{i:05d}" for i in range(len(hist))], [len(x) for x in take])
    tb = sub.t.iloc[np.concatenate(take)].copy() if len(lab) else sub.t.iloc[:0].copy()
    tb["date"] = lab
    return tb.reset_index(drop=True), [f"p{i:05d}" for i in range(len(hist))]


def part_b1(sub: Subject, subject_index: int, reps: int, verify: int, auto: int) -> list[dict]:
    """B1 on one subject: the registered bound on stationary-bootstrap histories, its coverage of the pooled mean."""
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
    # the rules: every subject's pooled bound; S1's era rule (the lower era's bound, the flag as registered)
    rules: dict[str, list[np.ndarray] | None] = {"pooled": None}
    ident = V.block_bounds(sums, cnts, np.arange(n)[None, :], sub.block_days, alphas)
    st = cf.edge_stats(sub.t, keys, sub.days, sub.block_days, sub.n_led)
    bad = [f"{R:g}" for j, R in enumerate(keys)
           if not (np.isclose(ident["lb"][0, 0, j], st[R]["lb"], rtol=0, atol=1e-12)
                   and np.isclose(ident["lb"][1, 0, j], st[R]["lb_at_n"], rtol=0, atol=1e-12)
                   and np.isclose(ident["e"][0, j], st[R]["e"], rtol=0, atol=1e-12))]
    if bad:
        raise SystemExit(f"REFUSED ({DECISION}): {sub.name}'s fast bound is not confirm_fv3.edge_stats' at R {bad}.")
    truth = {R: float(st[R]["e"]) for R in keys}
    registered_rule = "pooled"
    if sub.name == "S1":
        eras = _era_positions(sub)
        if sum(len(e) for e in eras) != n:
            raise SystemExit(f"REFUSED ({DECISION}): S1's eras do not cover its days.")
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
            raise SystemExit(f"REFUSED ({DECISION}): S1's fast {registered_rule} bound is not a3_brk30.bounds_at_n's "
                             f"at R {bad}.")
    blocks = list(dict.fromkeys(list(V.B1_BLOCKS) + [int(auto)]))
    out: list[dict] = []
    chunk = max(1, int(B1_CHUNK_CELLS // max(1, n * len(keys))))
    for L in blocks:
        for rule, eras in rules.items():
            rng = np.random.default_rng([V.SEED_B1, subject_index, int(L), 0 if rule == "pooled" else 1])
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
                while checked < min(verify, m):            # the registered function on materialised replicates
                    parts = [_materialise(sub, rows_by_day, ix[checked]) for ix in idx]
                    refs = [cf.edge_stats(tb, keys, dd, sub.block_days, sub.n_led) for tb, dd in parts]
                    for j, R in enumerate(keys):
                        want = (min(r[R]["lb"] for r in refs), min(r[R]["lb_at_n"] for r in refs))
                        got = (b["lb"][0, checked, j], b["lb"][1, checked, j])
                        if not all((np.isnan(w) and np.isnan(g)) or np.isclose(g, w, rtol=0, atol=1e-9)
                                   for g, w in zip(got, want)):
                            raise SystemExit(f"REFUSED ({DECISION}): {sub.name} {rule} L {L} replicate {checked} R "
                                             f"{R:g}: the fast bound {got} is not the registered function's {want}.")
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


def replay_form(sub: Subject) -> dict[str, tuple[list, dict]]:
    """A2: each arm's blocks and `customer_slices.engine_args` -- the replay-form path call of the subject's campaign."""
    import customer_slices as cs

    kw = {k: v for k, v in sub.kw.items() if k not in ("n_paths", "purchase_budget")}
    camp = cs.Campaign(sub.name, list(sub.blocks), list(sub.days), kw)
    return {arm: (cs.arm_blocks(camp, arm),
                  cs.engine_args(camp.kw, arm, camp.blocks, purchase_budget=sub.kw.get("purchase_budget")))
            for arm in ("verdict", "point")}


def part_a2(sub: Subject, starts_cap: int | None, n_paths: int, resume: Resume | None) -> list[dict]:
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
    for arm, (blk, args) in replay_form(sub).items():
        def real(blk=blk, args=args):
            lps = [cs.replay(blk[s:s + H], args) for s in starts]
            v = V.path_values(lps, sub.margin)
            return {"required": v["required"].tolist(), "net": v["net"].tolist()}

        r = _cached(resume, f"{sub.name} a2 real {arm} {len(starts)}", real)
        for scheme, L in [("independent", None)] + [(f"stationary, mean block {x}", x) for x in V.MEAN_BLOCKS]:
            def resampled(blk=blk, args=args, L=L):
                lps = []
                for s in path_seeds(V.SEED_A2, n_paths):
                    extra = {} if L is None else {"mean_block": float(L)}
                    sd = SharedDayDraws({0: list(blk)}, seed=s, **args["draws"], **extra)
                    lps.append(simulate_lockstep_path(args["draws"]["protocol"], seed=s, horizon_days=H + 1,
                                                      **args["path"], **sd.lockstep_kwargs()))
                v = V.path_values(lps, sub.margin)
                return {"required": v["required"].tolist(), "net": v["net"].tolist()}

            sc = _cached(resume, f"{sub.name} a2 {scheme} {arm} {n_paths}", resampled)
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


def part_c1(eng: Engine, reg: dict[str, dict], subject_index: int) -> list[dict]:
    """C1: each arm in `C1_REALISATIONS` seeded realisations (`v1_validation.c1_seed`), each a row pair, then per arm and
    reading the realisations' mean, smallest, largest and range (section `c1_summary`)."""
    sub = eng.sub
    rows = []
    for i, (name, kind, p) in enumerate(V.C1_ARMS):
        arm_rows = []
        for j in range(V.C1_REALISATIONS):
            seed = V.c1_seed(subject_index, i, j)
            rng = np.random.default_rng(seed)
            if kind == "trade":
                tt, gone = V.drop_trades(sub.t, p, rng), []
            else:
                tt, gone = V.miss_sessions(sub.t, sub.days, p, rng)
            res = eng.run(f"c1 {name} realisation {j}", blocks=sub.rebuild(tt))
            arm_rows += reading_rows("c1", sub, name, res, reg, kind=kind, p=p, realisation=j, realisation_seed=seed,
                                     trades_offered=int(len(sub.t)), trades_left=int(len(tt)),
                                     sessions_missed=len(gone),
                                     note=f"realisation {j} of {V.C1_REALISATIONS} (seed v1_validation.c1_seed); each "
                                          "R's e and bound as registered")
            print(f"  {sub.name} C1 {name} realisation {j}: done", flush=True)
        rows += arm_rows
        for arm in (sub.arm_names["bound"], sub.arm_names["point"]):
            mine = [r for r in arm_rows if r["arm"] == arm]
            row: dict[str, Any] = {"section": "c1_summary", "subject": sub.name, "arm": arm, "scheme": name,
                                   "kind": kind, "p": p, "realisations": len(mine),
                                   "share_realisations_growth_above_zero": float(np.mean([r["growth_above_zero"]
                                                                                         for r in mine]))}
            for c in READ + ("trades_left", "sessions_missed"):
                for k, v in V.realisation_summary([r.get(c) for r in mine]).items():
                    if k != "n":
                        row[f"{c}_{k}"] = v
            rows.append(row)
    return rows


def fv3c_kinds(sub: Subject) -> pd.DataFrame:
    """C2: each of P-06's gate trades' exit kind at every R (`Signals3.outcome`'s stop, target, breakeven and flatten
    flags), row for row with the trades -- the trades' dates and net outcomes re-derived and checked equal (refusing),
    as `confirm_fv3.cost_rows` checks its own."""
    import score_fv3_grid as gf

    S, ev, cand = sub.extra["S"], sub.extra["ev"], sub.extra["cand"]
    spec = gf.leg_spec(cand, "combine")
    out = []
    for y, k in sub.extra["sels"].items():
        if k is None:
            continue
        c = ev.cells[k]
        cnd = S.candidates(c)
        rung = S.rung(bool(c["double_rung_reversions"]))
        base = S.outcome(rung, "r", spec[1], spec[2], spec[3])
        kept = S.kept(cnd & base["permitted"], base["exit"], base["stopped"],
                      two_losses_bos_only=(c["displacement"] == "rule")) & (S.year == y)
        per = {R: S.outcome(rung, "r", float(R), spec[2], spec[3]) for R in sub.keys}
        for i in np.nonzero(kept)[0]:
            row: dict[str, Any] = {"date": str(S.df["date"].iat[i])}
            for R in sub.keys:
                o = per[R]
                if not bool(o["permitted"][i]):
                    row[f"o_{R:g}"], row[f"net_{R:g}"] = "", float("nan")
                    continue
                row[f"o_{R:g}"] = ("s" if o["stopped"][i] else "t" if o["target"][i] else "b" if o["breakeven"][i]
                                   else "f" if o["flat"][i] else "?")
                row[f"net_{R:g}"] = float(o["gross"][i] - o["cost"][i])
            out.append(row)
    k = pd.DataFrame(out)
    if len(k) != len(sub.t) or list(k["date"]) != list(sub.t["date"].astype(str)):
        raise SystemExit(f"REFUSED ({DECISION}): the exit kinds are not row for row with P-06's gate trades.")
    for R in sub.keys:
        a, b = k[f"net_{R:g}"].to_numpy(float), sub.t[f"r_{R:g}"].to_numpy(float)
        if not np.allclose(a, b, rtol=0, atol=1e-12, equal_nan=True):
            raise SystemExit(f"REFUSED ({DECISION}): the kinds' net outcome at {R:g}R is not the gate trades'.")
    return k


def part_c2(eng: Engine, reg: dict[str, dict]) -> list[dict]:
    """D-583's slippage families on FV3-C: each trade's net R at every R lowered by the arm's extra ticks for its exit
    kind over its own stop; e and the 0.05 bound re-read on the stressed trades; the table frozen."""
    import confirm_fv3 as cf
    import score_fv3_grid as gf

    from propedge.research import p16_slip_stress as ps16

    sub = eng.sub
    base = {"s": float(gf.STOP_SLIP_TICKS), "t": 0.0, "f": float(gf.FLATTEN_SLIP_TICKS), "b": float(gf.STOP_SLIP_TICKS)}
    want = {k: float(v) for k, v in ps16.base_exit_ticks().items()}
    if base != want:
        raise SystemExit(f"REFUSED ({DECISION}): FV3's exit ticks {base} are not D-583's base {want}.")
    kinds = fv3c_kinds(sub)
    rows = []
    for arm in ps16.arms():
        add = ps16.added_ticks(arm)
        if arm["arm"] == "base":
            res = reg
            tt = sub.t
        else:
            tt = V.stress_by_kind(sub.t, kinds, add, sub.keys)
            st = cf.edge_stats(tt, sub.keys, sub.days, sub.block_days, sub.n_led)
            res = eng.run(f"c2 {arm['arm']}", blocks=sub.rebuild(tt), e_by={R: float(st[R]["e"]) for R in sub.keys},
                          lb_by={R: float(st[R]["lb"]) for R in sub.keys})
        rows += reading_rows("c2", sub, arm["arm"], res, reg, family=arm["family"], level=int(arm["level"]),
                             **{f"added_ticks_{k}": float(v) for k, v in add.items()},
                             mean_stop_ticks=float(tt["stop_ticks"].mean()),
                             note="the extra ticks over each trade's own stop; the entry's extra ticks are added to "
                                  "FV3's own entry cost (its spread, at least one tick); the state table frozen")
        print(f"  S2 C2 {arm['arm']}: done", flush=True)
    arm_rows = list(rows)
    for fam in ps16.FAMILIES:
        fr = sorted((r for r in arm_rows if r["arm"] == sub.arm_names["bound"] and r["family"] in ("base", fam)),
                    key=lambda r: r["level"])
        low = next((int(r["level"]) for r in fr if not r["growth_above_zero"]), ps16.NONE)
        rows.append({"section": "c2_reading", "subject": sub.name, "family": fam,
                     "levels": " ".join(str(r["level"]) for r in fr),
                     "lowest_level_growth_at_bound_at_or_below_zero": low})
    rows.append({"section": "c2_not_done", "subject": sub.name,
                 "note": "latency on FV3-C is not done: its signal lives in the QuantConnect captures, which carry "
                         "outcomes at latencies 0 and 5 only as codes, not a walk that can be re-entered later"})
    return rows


def part_b3(reps: int) -> list[dict]:
    """The familywise false pass of FV3's declared 32-cell screen under a zero-mean null: `gate4_checks`' per-day
    matrices, every cell centred to a zero mean per trade on both legs, signal days resampled jointly by the
    stationary bootstrap, the screen's own walk-forward (`gate4_checks.walkforward`: each test year's pick by the
    plateau rule on the years before it) and the bound of its stitched out-of-sample series."""
    import confirm_fv3 as cf
    import gate4_checks as G4
    import score_orb5_grid as g5

    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result

    cfg, S, ev = G4.build_screen(RESULTS_DIR)
    chk = G4.screen_check(ev, cfg, read_result(RESULTS_DIR / G4.SCREEN_RESULT))
    if not all(r["equal"] for r in chk):
        raise SystemExit(f"REFUSED ({DECISION}): the rebuilt screen is not {G4.SCREEN_RESULT}.")
    mats, yi = G4.day_matrices(S, ev, cfg)
    if np.any(np.diff(yi) < 0):
        raise SystemExit(f"REFUSED ({DECISION}): the screen's signal days are not in date order.")
    first = int(cfg["selection"]["walkforward"]["first_test_year"])
    k = len(ev.cells)
    null = {leg: {"n": mats[leg]["n"], "flat": mats[leg]["flat"],
                  "metric": V.centre_cells(mats[leg]["metric"], mats[leg]["n"])} for leg in G4.LEGS}
    nd = len(yi)
    rng = np.random.default_rng([V.SEED_B3, 0])
    above05 = abovek = mean_above = no_pick = 0
    done = 0
    while done < reps:
        m = min(200, reps - done)
        idx = V.stationary_indices(nd, V.B3_MEAN_BLOCK, m, rng)
        for r in range(m):
            boot = {leg: {s: null[leg][s][:, idx[r]] for s in ("n", "metric", "flat")} for leg in G4.LEGS}
            wf = G4.walkforward(G4.with_years(ev, boot, yi), first)
            vals = pd.Series([0.0 if not np.isfinite(v) else v for _, _, v in wf], dtype=float)
            no_pick += int(all(p is None for _, p, _ in wf))
            above05 += int(float(g5.bound(vals)) > 0)
            abovek += int(float(cf.bound_at(vals, V.ALPHA / k)) > 0)
            mean_above += int(float(vals.mean()) > 0)
        done += m
    rows = []
    for name, cnt, alpha in (("the screen's own level, 0.05", above05, V.ALPHA),
                             (f"0.05/k, k = {k}", abovek, V.ALPHA / k)):
        c = V.coverage_counts(cnt, reps, 0, alpha)
        rows.append({"section": "b3", "family": "FV3's 32-cell screen (config/fv3_grid.yaml)", "cells": k,
                     "signal_days": nd, "mean_block": V.B3_MEAN_BLOCK, "level": name, **c,
                     "share_stitched_mean_above_zero": mean_above / reps, "share_no_pick_in_any_year": no_pick / reps,
                     "first_test_year": first,
                     "note": "the null centres every cell's metric to a zero mean per trade: it calibrates the "
                             "screen's selection and its bound as a test of edge, not the D-145 gate (which a "
                             "zero-edge campaign can pass on the contract's shape); a block is 21 signal days (days "
                             "with at least one recorded signal), year labels by position"})
    rows.append({"section": "b3_not_done", "family": "P-16's stop family (rc_width_screen, rc_stop_walkforward, "
                                                     "rc_stop_fine)",
                 "note": "not done: the family's selection rule (D-538) picks the stop with the highest growth on the "
                         "required bankroll at the bound, a 500-path engine statistic that cannot be recomputed on "
                         "20,000 resampled histories; no proxy rule is substituted"})
    return rows


# ------------------------------------------------------------------------------------------------ main


def write_part(part: str, rows: list[dict], idents: list[dict], params: dict, results_dir: Path | None,
               seed: int, runs: list[tuple[str, str, int]]) -> None:
    """The part's file with its manifest; before it, every engine run of the part beyond the registered reproductions
    in the variant ledger (`runs`: subject, label, campaign seed), once each."""
    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import write_result

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    counter = VariantCounter(path=rd / "variants.jsonl")
    for subject, label, run_seed in runs:
        counter.record(prereg_id=DECISION, seed=int(run_seed), exploratory=True,
                       params={"study": f"{DECISION}, V1's validation checks", "part": part, "subject": subject,
                               "run": label, "paths": params["paths"]},
                       label=f"{DECISION}'s V1: {subject} {label}")
    out = pd.DataFrame(idents + rows)
    out.insert(1, "reading", V.READING)
    name = f"{V.RESULT}_{part.lower()}"
    write_result(out, name, script=SCRIPT, seed=seed, exploratory=True, results_dir=results_dir, parameters=params,
                 variant_count=len(runs),
                 notes={"status": V.READING, "selection": "none: beside the registered verdicts",
                        "readings": "propedge/research/v1_validation.py's docstring"},
                 description=f"EXPLORATORY ({DECISION}): V1's part {part} on P-16's registered gate and FV3-C's "
                             "confirmation P-06 -- read beside the registered verdicts, changing none.")
    print(f"written: {name}.csv ({len(rows)} rows)", flush=True)


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="a smoke: a few paths and replicates; no reading printed; "
                                                         "nothing written")
    ap.add_argument("--part", default="all", help="A0 A1 A2 B1 B2 B3 C1 C2, or all (the declared order)")
    ap.add_argument("--subject", default="both", choices=("S1", "S2", "both"))
    ap.add_argument("--paths", type=int, default=None, help=f"--check: paths ({CHECK_PATHS})")
    ap.add_argument("--days", type=int, default=None, help="--check: S1 on a subset of walked sessions (no identity)")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--no-resume", action="store_true")
    ap.add_argument("--resume-dir", default=None)
    a = ap.parse_args(argv)
    part = a.part.upper()
    parts = list(V.PARTS) if part == "ALL" else [part]
    if any(p not in V.PARTS for p in parts):
        print(f"REFUSED ({DECISION}): --part is one of {V.PARTS} or all.")
        return 2
    if not a.check and (a.paths is not None or a.days is not None):
        print(f"REFUSED ({DECISION}): the declared run uses {V.N_PATHS} paths on every day; a smaller run is --check.")
        return 2
    declared = not a.check
    decl = V.declaration(ROOT)
    bad = V.declaration_problems(decl, declared=declared)
    if bad:
        print(f"REFUSED ({DECISION}): the build is not the declaration -- " + "; ".join(bad))
        return 2
    print(f"the declaration HOLDS (DECISIONS.md's {DECISION} row; sha256 "
          f"{decl['sha256'][:16]})", flush=True)
    t_all = time.time()
    n_paths = V.N_PATHS if declared else int(a.paths or CHECK_PATHS)
    resume = None
    if declared and not a.no_resume:
        import subprocess

        commit = subprocess.run(["git", "rev-parse", "--short=12", "HEAD"], cwd=ROOT, capture_output=True,
                                text=True).stdout.strip() or "nocommit"
        folder = Path(a.resume_dir) if a.resume_dir else (
            Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "stage2-runs" / "resume")
        resume = Resume(folder, f"{commit}_{n_paths}")
    names = list(V.SUBJECTS) if a.subject == "both" else [a.subject]
    subjects: dict[str, Subject] = {}
    engines: dict[str, Engine] = {}
    regs: dict[str, dict] = {}
    idents: dict[str, dict] = {}
    autos: dict[str, int] = {}

    def subject(name: str) -> Subject:
        if name not in subjects:
            t0 = time.time()
            subjects[name] = build_s1(a.days) if name == "S1" else build_s2()
            s = subjects[name]
            print(f"{name} built: {len(s.days)} sessions, {len(s.t)} offered trades ({time.time() - t0:.0f} s)",
                  flush=True)
        return subjects[name]

    def engine(name: str) -> tuple[Engine, dict]:
        if name not in engines:
            engines[name] = Engine(subject(name), n_paths, a.workers, resume)
            regs[name], idents[name] = registered_run(engines[name], declared)
        return engines[name], regs[name]

    def auto(name: str) -> int:
        if name not in autos:
            r0 = part_a0(subject(name))
            autos[name] = int(next(r["auto_block"] for r in r0 if r["series"] == "day_r"))
        return autos[name]

    head = [{"section": "declaration", "holds": True,
             "check": f"the {DECISION} row's sha256 {decl['sha256']}, read as text; every constant agrees"}]
    counted: set[tuple[str, str]] = set()
    for p in parts:
        t0 = time.time()
        rows: list[dict] = []
        used: list[str] = []
        if p == "B3":
            rows = part_b3(V.B3_REPS if declared else CHECK_B3_REPS)
        for name in ([] if p == "B3" else names):
            if p == "C2" and name != "S2":
                continue
            used.append(name)
            if p == "A0":
                rows += part_a0(subject(name))
            elif p == "B1":
                rows += part_b1(subject(name), V.SUBJECTS.index(name), V.B1_REPS if declared else CHECK_REPS,
                                V.B1_VERIFY if declared else 2, auto(name))
            elif p == "A2":
                rows += part_a2(subject(name), None if declared else CHECK_STARTS,
                                V.A2_PATHS if declared else 2 * CHECK_STARTS, resume)
            else:
                eng, reg = engine(name)
                if p == "A1":
                    rows += part_a1(eng, reg)
                elif p == "B2":
                    rows += part_b2(eng, reg, V.B2_MAX_STEPS if declared else 2)
                elif p == "C1":
                    rows += part_c1(eng, reg, V.SUBJECTS.index(name))
                elif p == "C2":
                    rows += part_c2(eng, reg)
        secs = time.time() - t0
        timing = {n: [round(x, 2) for x in engines[n].seconds] for n in used if n in engines}
        if a.check:
            print(f"--check part {p}: ran ({len(rows)} rows built, none printed, nothing written). {secs:.0f} s; "
                  f"engine calls' seconds at {n_paths} paths: {timing}", flush=True)
            continue
        params = {"decision": DECISION, "declaration_sha256": decl["sha256"], "part": p, "subjects": used,
                  "paths": n_paths, "mean_blocks": list(V.MEAN_BLOCKS), "ledger_n": dict(V.LEDGER_N),
                  "campaign_seeds": {n: subjects[n].seed for n in used},
                  "seeds": {"A2": V.SEED_A2, "B1": V.SEED_B1, "B3": V.SEED_B3, "C1": V.SEED_C1},
                  "a2": {"horizon": V.A2_HORIZON, "step": V.A2_STEP, "paths": V.A2_PATHS},
                  "b1": {"blocks": list(V.B1_BLOCKS), "auto": {n: autos[n] for n in used if n in autos},
                         "replicates": V.B1_REPS, "verified": V.B1_VERIFY},
                  "b2": {"step": V.B2_STEP, "max_steps": V.B2_MAX_STEPS, "mean_block": V.B2_MEAN_BLOCK},
                  "b3": {"replicates": V.B3_REPS, "mean_block": V.B3_MEAN_BLOCK},
                  "c1": {"arms": [list(x) for x in V.C1_ARMS], "realisations": V.C1_REALISATIONS,
                         "seeds": "v1_validation.c1_seed: lockstep.child_seed(SEED_C1, 3 x subject + arm, realisation)"},
                  "identity_columns": list(IDENT_COLS),
                  "engine_keyword": "gate.run_gate(mean_block=...), shared_days.StationaryDayTable; off by default",
                  "workers": int(a.workers), "seconds": round(secs, 1)}
        seed = {"A2": V.SEED_A2, "B1": V.SEED_B1, "B3": V.SEED_B3, "C1": V.SEED_C1}.get(
            p, subjects[used[0]].seed if used else V.SEED_B3)
        runs = [(n, lab, subjects[n].seed) for n in used if n in engines for lab in engines[n].labels
                if (n, lab) not in counted]
        counted.update((n, lab) for n, lab, _ in runs)
        write_part(p, rows, head + [idents[n] for n in used if n in idents], params, results_dir, seed, runs)
    if a.check:
        print(f"--check done: parts {parts} on {names}; no reading printed; nothing written. "
              f"{time.time() - t_all:.0f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
