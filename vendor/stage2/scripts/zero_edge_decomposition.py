"""EXPLORATORY (D-485 (4)): where FV3-C's zero-edge money comes from -- its signal's structure, its exact v12 table or
the campaign's protocol switches -- read on files and trades already on record, development data only, nothing past each
trade set's own window, no new data.

    python scripts/zero_edge_decomposition.py           # the identity checks, then the declared grid
    python scripts/zero_edge_decomposition.py --check   # the identity checks only (nothing written)
    python scripts/zero_edge_decomposition.py --switches   # POST-HOC: cell (a) with one P-11 switch at a time

**The grid, declared here before any cell ran** (its size is the manifest's variant count). Each cell is a trade set, a
plan and a protocol; each runs at 150 paths over 504 sessions (the screens' convention) on the SAME campaign seed
(common random numbers), FV3-C's gate seed 20261019, so cell (a)'s paths are the first 150 of `fv3_corrected_v1`'s:

=====  ===============================================  ===================================  ==============
cell   trades                                           plan                                 protocol
=====  ===============================================  ===================================  ==============
a      FV3-C's development gate trades                  FV3-C's v12 table (its own cell)     FV3-C's
b      FV3-C's                                          T24-GF15b's fixed plan               FV3-C's
c      A1-INS15's (P-11's trades)                       FV3-C's v12 table (FV3-C's cell)     P-11's
c2     A1-INS15's                                       v12 with every R above 2 set to 2    P-11's
d      A1-INS15's                                       T24-GF15b's fixed plan               P-11's (anchor)
e      FV3-C's thinned to A1-INS15's count each date    FV3-C's v12 table                    FV3-C's
f      FV3-C's                                          FV3-C's v12 table                    P-11's
g      FV3-C's                                          T24-GF15b's fixed plan               P-11's
h      FV3-C's, the intermediate quarter-R targets out  FV3-C's v12 table                    FV3-C's
=====  ===============================================  ===================================  ==============

(a)-(e) are D-485 (4)'s and the caller's; (c2), (f), (g) and (h) are added here, before any run, to break the
confounding of trades with protocol (f, g: FV3-C's trades under P-11's switches) and to read two structural features
apart: A1's map offers no R above 2, which the v12 funded leg asks for (c2 caps the table's R at 2 -- a reading of v12
on A1's map, NOT FV3-C's table and NOT a re-solve), and FV3's trades carry an outcome at every quarter-R, which the
need-aware and consistency-cap exits read (h keeps only the R values the v12 table itself asks for: 0.25, 1, 1.5, 2, 2.5,
3). (e) keeps, on each FV3-C date, at most as many FV3-C trades as A1-INS15 recorded that date, drawn at random (seed
20261031) and kept in entry order.

**Each cell's three arms, read as the scoreboard reads them** (growth on the required bankroll, `pf_growth_on_base_p50`
on `pf_required_p90`, the bankroll an output): the point arm (outcomes as measured), the bound arm (each R shifted to its
one-sided 95 % lower bound -- the trade set's own convention on record: FV3-C's trades the development scorer's yearly
bound, `fv3_corrected_v1`'s; A1-INS15's the 21-session blocks, P-11's, pooled because its eras were not flagged) and the
zero-edge twin (every R's outcomes shifted to a zero mean, the point arm, as each run's own script builds it). All at
0 % denial with the Responsible Trading Program's placement off.

**The protocols.** FV3-C's: `portfolio_stage.run_campaign` under `config/fv3_corrected_portfolio.yaml` exactly as
frozen (five trades a day's capacity, its sizing with the 45-tick stand-aside and the Combine's room cap only, settlement
by the trade's MAE, routing to able accounts, the firm's cross-account rule, each position held to its own exit, no
strict one-at-a-time, the seat freed the same evening; the five fidelity switches). P-11's: `t24_gf15.run`'s engine
call (T24's protocol with its day capacity raised to the trades' busiest day where 23 is too few, T24's sizing with the
room cap on both legs and no stand-aside, pessimistic settlement, the strict rule at five minutes, the same five
switches). `PROTOCOL_DIFFERENCES` lists every switch that differs, and the run writes them into the manifest.

**The identity checks, before any other cell is read:** cell (a)'s paths -- point, bound and twin -- must equal the
first 150 paths of `results/fv3_corrected_v1_paths.csv` (gate placement off at 0 %, and the zero-edge twin) on every
compared column; and P-11's engine path is run at P-11's own seed for 20 paths, which must equal the first 20 paths of
`results/a1_ins15_gate_paths.csv` (gate point and bound at 0 %, and the zero-edge twin). Either failing refuses the run:
nothing is written and no other cell is read. A1-INS15's trades are also checked against the rescreen file fixed at
P-11's registration (`a1_ins15.identity_with_screen`).

Writes `results/zero_edge_decomposition.csv` (sections `campaign`, `edge`, `reference`, `identity`) with its manifest;
each cell recorded in `results/variants.jsonl` under `D-485:zero_edge_decomposition`.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/zero_edge_decomposition.py"
DECISION = "D-485"
RESULT = "zero_edge_decomposition"
FAMILY_ID = f"{DECISION}:zero_edge_decomposition"
SEED = 20261019                     # FV3-C's gate seed: cell (a)'s paths are fv3_corrected_v1's first 150
THIN_SEED = 20261031                # (e)'s draw of which FV3-C trades a date keeps
N_PATHS, HORIZON = 150, 504         # the screens' convention
P11_SEED, P11_CHECK_PATHS = 20261028, 20
MARGIN, BLOCK = 49.0, 21
FV3_CONFIG = ROOT / "config" / "fv3_corrected_portfolio.yaml"
FV3_RUN = "fv3_corrected_v1"
P11_RUN = "a1_ins15_gate"
#: (c2): the widest R A1-INS15's m40 map offers at any hour (3:1 is offered at none, P-11's audit)
RR_CAP = 2.0
#: (h): the R values FV3-C's v12 table asks for at its cell (every leaf of `state_dp_e-0.050_lamstar`)
TABLE_RRS = (0.25, 1.0, 1.5, 2.0, 2.5, 3.0)

#: cell -> (trades, plan, protocol, description)
CELLS = {
    "a": ("fv3c", "v12", "fv3c", "FV3-C's trades, its v12 table, its protocol (the identity)"),
    "b": ("fv3c", "gf15b", "fv3c", "FV3-C's trades under T24-GF15b's fixed plan, FV3-C's protocol"),
    "c": ("a1", "v12", "p11", "A1-INS15's trades under FV3-C's exact v12 table, P-11's protocol"),
    "c2": ("a1", "v12_rr_cap2", "p11", "A1-INS15's trades under v12 with every R above 2 set to 2, P-11's protocol"),
    "d": ("a1", "gf15b", "p11", "A1-INS15's trades under T24-GF15b's plan, P-11's protocol (the anchor)"),
    "e": ("fv3c_thin", "v12", "fv3c", "FV3-C's trades thinned to A1-INS15's count each date, v12, FV3-C's protocol"),
    "f": ("fv3c", "v12", "p11", "FV3-C's trades, its v12 table, P-11's protocol switches"),
    "g": ("fv3c", "gf15b", "p11", "FV3-C's trades under T24-GF15b's plan, P-11's protocol"),
    "h": ("fv3c_coarse", "v12", "fv3c", "FV3-C's trades with only the table's own R (no intermediate quarter-R exits), "
                                        "v12, FV3-C's protocol"),
}
ARMS = ("point", "bound", "twin")

#: every engine switch that differs between FV3-C's development campaign and P-11's (each from its own code and config)
PROTOCOL_DIFFERENCES = {
    "combine_plan": ("v12 table: fresh $2,000 at 1.5R, a Combine menu with R below 1, abandon by state, one trade a "
                     "session", "two-shot 1:1 at $1,600, one a session, closed once the room cannot carry $1,600"),
    "funded_plan": ("v12 table: fresh $2,000 at 3R, R 1-3 by winning days and payout-line band, D-325's $500 cap "
                    "above the start, abandon by state", "growth $1,600 at 1:1.5 at or below the start, $240 1:1 flips "
                    "above it, closed once the room cannot carry the state's trade"),
    "one_at_a_time": ("none (the firm's cross-account rule only)", "strict: no trade while any account holds a "
                      "position or within 5 minutes of one closing"),
    "settlement": ("mae (a trade risking more than the room settles by its MAE)", "pessimistic"),
    "room_cap": ("the Combine only", "the Combine and the funded account"),
    "stand_aside": ("a stop under 45 ticks ($22.50 a micro) is not traded, both legs", "none"),
    "trades_per_day_capacity": ("5", "23, or the trades' busiest day where more (A1-INS15: 23)"),
    "pnl_shift_key": ("the funded fresh R (3) for the trade log's single outcome", "R 1"),
    "bound_convention": ("yearly means, 2021-2025 H1 (the development scorer's)", "21-session blocks, pooled "
                         "(eras not flagged)"),
    "campaign_seed": ("20261019", "20261028"),
    "trade_records": ("outcomes at every quarter R 0.25-3 where the room rule permits (FV3's ladder: 12.5 / 25 / "
                      "50-point stops, $25 / $50 / $100 a micro)", "outcomes at R 1, 1.5, 2 where the m40 map offers "
                      "them, none at 3 (20 / 40-point stops, $40 / $80 a micro)"),
    "data_window": ("FV3's QuantConnect captures, gate trades 2021-01-04 to 2025-06-30 (1,083 sessions, the walk-forward's "
                    "test years)", "Databento bars 2020-01-02 to 2026-07-16 (1,691 sessions)"),
    "entry": ("the signal bar's close plus two minutes (seated latency)", "five bars after the event"),
}
#: switches that are the SAME in both campaigns (recorded so the list is complete)
PROTOCOL_SAME = ("five accounts, five Combines, five live accounts at most; rotation; 504 sessions, 500 paths; Aeropay; "
                 "the bankroll an output (cash never binds); placement off at the gate; routing to able accounts; the "
                 "firm's cross-account rule; each position held to its own exit; need-aware and consistency-cap Combine "
                 "exits; the no-trade state on the Standard path only; decision inputs to the cent; the seat freed the "
                 "same evening; each trade's fee re-priced at the contracts it holds (MNQ $1.22, NQ $3.78 a round turn)")

#: the per-path record's columns an identity compares
PATH_COLS = ("final_cash", "fees", "payouts", "trades", "trades_sized", "accounts_funded", "attempts_started",
             "realised_risk", "intended_capped_risk", "deepest_loss_from_start", "days_to_first_payout")
#: the campaign row's columns kept, beside the cell's labels
KEEP = ("shift", "enforcement_p", "placement", "risk_policy", "pf_growth_on_base_p50", "pf_growth_on_base_p10",
        "pf_required_p50", "pf_required_p90", "pf_required_p99", "pf_net_p50", "median_log_growth",
        "mean_combine_purchases", "mean_accounts_funded", "share_accounts_ever_paid", "median_days_to_first_payout",
        "mean_payouts_per_path", "median_payouts_per_path", "mean_payout_gross", "share_paid_xfa_closed",
        "pf_share_combines_abandoned", "pf_share_xfa_abandoned", "pf_slot_days_per_attempt", "pf_slot_days_per_xfa",
        "pf_cash_per_slot_day_p50", "share_trades_skipped_busy", "share_trades_skipped_opposite",
        "share_trades_skipped_no_flat_account", "share_trades_need_exits", "share_trades_room_capped",
        "share_trades_stood_aside", "share_trades_unsized", "share_combines_out_of_room",
        "realised_to_intended_capped_risk", "pf_break_even_denial_p50", "one_at_a_time", "settlement")


# ------------------------------------------------------------------------------------------------ the trades


def fv3_config() -> dict:
    import score_fv3_grid as gf

    return gf.config(FV3_CONFIG)


def fv3_trades(rd: Path) -> tuple[pd.DataFrame, list[str], float]:
    """FV3-C's development gate trades, day set and tick value exactly as the scorer built them (checked there against
    the run's `gate_inputs`)."""
    import fv3_xfa_time_budget as xb

    return xb.rebuild_trades(fv3_config())


def a1_trades(rd: Path) -> tuple[pd.DataFrame, list[str]]:
    """A1-INS15's trades and day set as P-11 ran them, checked against the rescreen file fixed at its registration."""
    import a1_ins15 as a1

    t, days, _ = a1.trades(rd)
    bad = a1.identity_with_screen(rd, t, days)
    if bad:
        raise SystemExit("REFUSED: A1-INS15's trades are not P-11's -- " + "; ".join(bad))
    return t, days


def rr_keys(t: pd.DataFrame) -> list[float]:
    import score_fv3_grid as gf

    return [float(R) for R in gf.trade_keys(t)]


def pad(t: pd.DataFrame, keys) -> pd.DataFrame:
    """The trades with an outcome column at every R of `keys`: an R the trades do not carry is offered on none of them
    (NaN outcome, MAE and exit) -- an account whose state asks for it takes no trade and the router passes the trade on
    (D-318); its outcomes are never invented."""
    t = t.copy()
    for R in keys:
        for c in ("r", "mae", "exit_t"):
            if f"{c}_{R:g}" not in t.columns:
                t[f"{c}_{R:g}"] = np.nan
    return t


def coarse(t: pd.DataFrame, keep=TABLE_RRS) -> pd.DataFrame:
    """(h): FV3-C's trades with only the R values the v12 table asks for; the intermediate quarter-R targets -- read
    only by the need-aware and consistency-cap exits -- dropped."""
    keep = {float(R) for R in keep}
    drop = [c for R in rr_keys(t) if R not in keep for c in (f"r_{R:g}", f"mae_{R:g}", f"exit_t_{R:g}")
            if c in t.columns]
    return t.drop(columns=drop)


def thin(t: pd.DataFrame, ref: pd.DataFrame, seed: int = THIN_SEED) -> pd.DataFrame:
    """(e): on each of `t`'s dates at most as many of its trades as `ref` recorded that date, drawn without replacement
    by one seeded generator in date order, kept in entry order; a date `ref` has no trade on keeps none."""
    rng = np.random.default_rng(int(seed))
    cap = ref.groupby(ref["date"].astype(str)).size()
    keep = []
    for d, g in t.groupby(t["date"].astype(str), sort=True):
        n = int(cap.get(d, 0))
        idx = g.index.to_numpy()
        if n >= len(idx):
            keep.extend(idx.tolist())
        elif n > 0:
            keep.extend(sorted(rng.choice(idx, size=n, replace=False).tolist()))
    return t.loc[sorted(keep)].reset_index(drop=True)


def stats_of(t: pd.DataFrame, days: list[str], keys, rule: str) -> dict[float, dict[str, float]]:
    """Each R's net edge and one-sided 95 % bound: `yearly` (FV3-C's development scorer, `fv3_corrected_v1`) or
    `blocks21` (P-06's 21-session blocks, P-11's). An R offered on no trade has e = lb = 0: nothing to shift."""
    import confirm_fv3 as cf
    import fv3d_lever_test as lt

    keys = [float(R) for R in keys]
    st = lt.period_stats(t, days, keys, "yearly") if rule == "yearly" else cf.edge_stats(t, keys, days, BLOCK, None)
    out = {}
    for R in keys:
        s = dict(st[R])
        if int(s.get("n", 0)) == 0:
            s.update({"e": 0.0, "lb": 0.0, "n": 0})
        out[R] = {k: s[k] for k in ("e", "lb", "n")}
    return out


# ------------------------------------------------------------------------------------------------ the plans


def fv3_cell(rd: Path) -> str:
    """The v12 cell FV3-C's development run used -- its gate rows' one policy id."""
    from propedge.reporting.results import read_result

    run = read_result(Path(rd) / f"{FV3_RUN}.csv")
    ids = set(run[run["section"] == "gate"]["policy_id"].astype(str))
    if len(ids) != 1:
        raise SystemExit(f"REFUSED: {FV3_RUN}.csv's gate rows carry {sorted(ids)}, not one policy.")
    return ids.pop()


def v12_dict(cfg: dict, pid: str) -> dict:
    pols = json.loads((ROOT / cfg["state_policy"]["policies_json"]).read_text(encoding="utf-8"))
    if pid not in pols:
        raise SystemExit(f"REFUSED: no exported policy {pid} in {cfg['state_policy']['policies_json']}.")
    return pols[pid]


def rr_capped(d: dict, cap: float = RR_CAP) -> dict:
    """(c2): the exported policy with every leaf's R above `cap` set to `cap`; risks, trade limits, abandons and the
    states' tree unchanged."""
    d = copy.deepcopy(d)

    def walk(n):
        if isinstance(n, dict):
            if n.get("type") == "fixed" and n.get("rr") is not None and float(n["rr"]) > cap + 1e-12:
                n["rr"] = float(cap)
            for v in n.values():
                walk(v)
        elif isinstance(n, list):
            for v in n:
                walk(v)
    walk(d["root"])
    d["id"] = f"{d['id']}_rrcap{cap:g}"
    return d


def policy_rrs(pol) -> list[float]:
    """Every R a policy's leaves ask for, in any phase."""
    from propedge.campaign.risk_policy import PHASES

    return sorted({float(leaf.rr) for leaf, _ in pol.root.leaves(frozenset(PHASES)) if leaf.rr is not None})


def plan(name: str, cfg: dict, pid: str):
    from propedge.campaign.risk_policy import RiskPolicy

    if name == "gf15b":
        import t24_gf15b as tb

        return tb.policy()
    d = v12_dict(cfg, pid)
    if name == "v12_rr_cap2":
        d = rr_capped(d)
    elif name != "v12":
        raise ValueError(f"unknown plan {name!r}")
    p = RiskPolicy.from_dict(d)
    p.validate()
    return p


# ------------------------------------------------------------------------------------------------ the campaigns


def hook_for(sink: list):
    import fv3d_lever_test as lt
    import portfolio_stage as ps

    inner = ps.composed_hook({"margin": MARGIN, "block_days": BLOCK}, sink=sink)
    return lt.lever_hook(inner), inner


def run_fv3c(blocks, cfg, tv, policy, e_by, lb_by, hook, *, seed: int, n_paths: int, horizon: int,
             fr: float = 3.0) -> pd.DataFrame:
    """FV3-C's protocol: `portfolio_stage.run_campaign` under FV3-C's config, as its identity run calls it."""
    import portfolio_stage as ps

    return ps.run_campaign(blocks, cfg, int(seed), tv, policy, e=e_by[fr], lb=lb_by[fr], e_by=e_by, lb_by=lb_by,
                           levels=(0.0,), n_paths=int(n_paths), horizon=int(horizon), hook=hook, rtp=False)


def run_p11(blocks, t, policy, e_by, lb_by, hook, *, seed: int, n_paths: int, horizon: int) -> pd.DataFrame:
    """P-11's protocol: `t24_gf15.run`'s engine call with the path count, horizon and seed as arguments; the day
    capacity as `a1_ins15.protocol_for`."""
    import a1_ins15 as a1
    import score_fv3_grid as gf
    import t24_wide as tw

    from propedge.campaign import gate
    from propedge.campaign.payout_method import rules_for_method

    df, _ = gate.run_gate(list(blocks), e=e_by[1.0], lb=lb_by[1.0], protocol=a1.protocol_for(t),
                          bankroll=gf.UNBOUND_BANKROLL, horizon_days=int(horizon), n_paths=int(n_paths), seed=int(seed),
                          accounts=tw.ACCOUNTS, sizing=tw.sizing(), rules=rules_for_method("aeropay"), mode="rotation",
                          settlement="pessimistic", combines=tw.ACCOUNTS, total_accounts=tw.ACCOUNTS,
                          risk_policy=policy, e_by_rr=e_by, lb_by_rr=lb_by, levels=(0.0,), path_hook=hook,
                          rtp=False, routing="able", cross_account=True, hold_to_own_exit=True, one_at_a_time=tw.GAP)
    df["placement"] = "off"
    return df


def campaign(t, days, tv, keys, stats, policy, protocol: str, cfg, *, seed: int, n_paths: int, horizon: int,
             label: str) -> tuple[dict[str, pd.Series], list[dict]]:
    """One cell's three arms -- the point and bound arms in one engine call, the zero-edge twin in a second -- and every
    path's record, labelled `<label> <arm>`."""
    import portfolio_stage as ps
    import score_fv3_grid as gf

    blocks, n_used = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise SystemExit("REFUSED: the blocks hold a different number of trades.")
    e_by, lb_by = ps._by(stats, "e"), ps._by(stats, "lb")
    fr = 3.0 if protocol == "fv3c" else 1.0              # each script's own key for the log's single outcome
    sink: list[dict] = []
    hook, inner = hook_for(sink)

    def go(blk, eb, lbb, arm):
        ps._label(inner, f"{label} {arm}")
        if protocol == "fv3c":
            return run_fv3c(blk, cfg, tv, policy, eb, lbb, hook, seed=seed, n_paths=n_paths, horizon=horizon, fr=fr)
        if protocol == "p11":
            return run_p11(blk, t, policy, eb, lbb, hook, seed=seed, n_paths=n_paths, horizon=horizon)
        raise ValueError(f"unknown protocol {protocol!r}")

    g = go(blocks, e_by, lb_by, "gate")
    zero = {k: 0.0 for k in e_by}
    z = go(ps.zero_edge_blocks(blocks, e_by, fr), zero, zero, "twin")
    rows = {"point": g[g["shift"] == "point"].iloc[0], "bound": g[g["shift"] == "lower_bound"].iloc[0],
            "twin": z[z["shift"] == "point"].iloc[0]}
    return rows, sink


def path_summary(sink: list[dict], run: str, shift: str) -> dict[str, float]:
    """From the per-path record: the Combine pass share (funded over started, all paths), and per path the trades
    executed, the dollars paid out and the fees."""
    p = pd.DataFrame([r for r in sink if r["run"] == run and r["shift"] == shift and float(r["enforcement_p"]) == 0.0])
    if p.empty:
        return {}
    att = float(p["attempts_started"].sum())
    return {"combine_pass_share": float(p["accounts_funded"].sum()) / att if att else float("nan"),
            "mean_trades_executed": float(p["trades"].astype(float).mean()),
            "mean_payouts_dollars": float(p["payouts"].mean()), "mean_fees_dollars": float(p["fees"].mean()),
            "mean_attempts_started": float(p["attempts_started"].mean())}


# ------------------------------------------------------------------------------------------------ the identities


def path_problems(sink: list[dict], ref: pd.DataFrame, pairs, n: int) -> list[str]:
    """Each (our run label, our shift, the reference's run label, its shift) at 0 %: our paths equal the reference's
    first `n` on every PATH_COLS column (to 1e-6; a missing value equal to a missing value). The problems."""
    out = []
    for mine, shift, theirs, tshift in pairs:
        a = pd.DataFrame([r for r in sink if r["run"] == mine and r["shift"] == shift
                          and float(r["enforcement_p"]) == 0.0]).sort_values("path").reset_index(drop=True)
        b = ref[(ref["run"].astype(str) == theirs) & (ref["shift"].astype(str) == tshift)
                & np.isclose(ref["enforcement_p"].astype(float), 0.0)].sort_values("path").head(n).reset_index(drop=True)
        if len(a) != n or len(b) != n:
            out.append(f"{mine} {shift}: {len(a)} paths against the reference's {len(b)} (want {n})")
            continue
        for c in PATH_COLS:
            x = pd.to_numeric(a[c], errors="coerce").to_numpy(float)
            y = pd.to_numeric(b[c], errors="coerce").to_numpy(float)
            same = (np.isnan(x) & np.isnan(y)) | np.isclose(x, y, rtol=0, atol=1e-6)
            if not same.all():
                i = int(np.argmin(same))
                out.append(f"{mine} {shift} {c}: path {i} {x[i]!r} against {theirs}'s {y[i]!r} "
                           f"({int((~same).sum())} of {n} differ)")
    return out


FV3_PAIRS = (("a gate", "point", "gate placement off", "point"),
             ("a gate", "lower_bound", "gate placement off", "lower_bound"),
             ("a twin", "point", "twin zero_edge", "point"))
P11_PAIRS = (("p11check gate", "point", "gate", "point"), ("p11check gate", "lower_bound", "gate", "lower_bound"),
             ("p11check twin", "point", "zero_edge_twin", "point"))


def p11_check(rd: Path, ta: pd.DataFrame, da: list[str], cfg: dict, n: int | None = None) -> list[str]:
    """P-11's engine path at P-11's seed for `n` paths (P11_CHECK_PATHS) against the first `n` of its per-path
    record."""
    from propedge.reporting.results import read_result

    n = P11_CHECK_PATHS if n is None else int(n)
    keys = rr_keys(ta)
    st = stats_of(ta, da, keys, "blocks21")
    _, sink = campaign(ta, da, 0.5, keys, st, plan("gf15b", cfg, ""), "p11", cfg, seed=P11_SEED, n_paths=n,
                       horizon=HORIZON, label="p11check")
    return path_problems(sink, read_result(Path(rd) / f"{P11_RUN}_paths.csv"), P11_PAIRS, n)


# ------------------------------------------------------------------------------------------------ the reference rows


def reference_rows(rd: Path) -> list[dict]:
    """The 500-path rows on record beside the grid: FV3-C-dev's gate point and bound arms (placement off, 0 %) and its
    zero-edge twin; P-11's likewise; each with its Combine pass share from its own per-path record."""
    from propedge.reporting.results import read_result

    out = []
    for name, sel, paths_sel in (
            (FV3_RUN, lambda r: (r["section"] == "gate") & (r["placement"].astype(str) == "off"),
             {"point": ("gate placement off", "point"), "bound": ("gate placement off", "lower_bound"),
              "twin": ("twin zero_edge", "point")}),
            (P11_RUN, lambda r: r["section"] == "gate",
             {"point": ("gate", "point"), "bound": ("gate", "lower_bound"), "twin": ("zero_edge_twin", "point")})):
        r = read_result(Path(rd) / f"{name}.csv")
        p = read_result(Path(rd) / f"{name}_paths.csv")
        g = r[sel(r) & np.isclose(r["enforcement_p"].astype(float), 0.0)]
        tw_ = (r[(r["section"] == "twin") & (r["twin"].astype(str) == "zero_edge")] if name == FV3_RUN
               else r[(r["section"] == "zero_edge_twin") & (r["shift"] == "point")])
        for arm, row in (("point", g[g["shift"] == "point"].iloc[0]), ("bound", g[g["shift"] == "lower_bound"].iloc[0]),
                         ("twin", tw_.iloc[0])):
            run, shift = paths_sel[arm]
            q = p[(p["run"].astype(str) == run) & (p["shift"].astype(str) == shift)
                  & np.isclose(p["enforcement_p"].astype(float), 0.0)]
            att = float(q["attempts_started"].sum())
            out.append({"section": "reference", "source": f"results/{name}.csv", "arm": arm, "paths": len(q),
                        **{k: row[k] for k in KEEP if k in row.index},
                        "combine_pass_share": float(q["accounts_funded"].sum()) / att if att else float("nan"),
                        "mean_trades_executed": float(pd.to_numeric(q["trades"], errors="coerce").mean()),
                        "mean_payouts_dollars": float(q["payouts"].mean()), "mean_fees_dollars": float(q["fees"].mean()),
                        "mean_attempts_started": float(q["attempts_started"].mean())})
    return out


# ------------------------------------------------------------------------------------------------ the switches


#: `--switches` (EXPLORATORY, chosen AFTER the grid was read: cell (f) put FV3-C's trades and table under P-11's
#: protocol and the twin fell by about half): cell (a) with ONE of P-11's protocol switches at a time, to find which of
#: them the v12 table's money depends on. Each reads the point arm and the zero-edge twin only.
SWITCHES = {"none": "FV3-C's protocol as frozen (the baseline; must reproduce fv3_corrected_v1's first paths)",
            "strict": "the strict one-at-a-time rule at five minutes (P-11's)",
            "pessimistic": "pessimistic settlement in place of the MAE's (P-11's)",
            "room_cap_funded": "the room cap on the funded account too (P-11's sizing)",
            "no_stand_aside": "no 45-tick stand-aside (P-11's sizing)"}
SWITCH_PAIRS = (("sw none gate", "point", "gate placement off", "point"),
                ("sw none gate", "lower_bound", "twin zero_edge", "point"))


def run_fv3c_switched(blocks, cfg, tv, policy, e_by, lb_by, hook, switch: str, *, seed: int, n_paths: int,
                      horizon: int, fr: float = 3.0) -> pd.DataFrame:
    """`portfolio_stage.run_campaign`'s engine call under FV3-C's config with one of P-11's switches (`SWITCHES`);
    'none' is that call exactly."""
    from dataclasses import replace

    import portfolio_stage as ps
    import score_fv3_grid as gf

    from propedge.campaign import gate
    from propedge.campaign.payout_method import rules_for_method

    if switch not in SWITCHES:
        raise ValueError(f"unknown switch {switch!r}")
    camp = cfg["gate"]["campaign"]
    f = gf.fidelity_of(cfg)
    sizing = gf.sizing_rule(cfg, tv)
    if switch == "room_cap_funded":
        sizing = replace(sizing, room_cap=("combine", "funded"))
    elif switch == "no_stand_aside":
        sizing = replace(sizing, stand_aside=None)
    df, _ = gate.run_gate(
        list(blocks), e=e_by[fr], lb=lb_by[fr], protocol=ps.protocol_of(cfg), bankroll=gf.bankroll_of(cfg),
        horizon_days=int(horizon), n_paths=int(n_paths), seed=int(seed), accounts=int(camp["accounts"]), sizing=sizing,
        rules=rules_for_method(camp["payout_method"]), mode=camp["mode"],
        settlement="pessimistic" if switch == "pessimistic" else camp["settlement"], combines=int(camp["combines"]),
        total_accounts=int(camp["accounts"]), risk_policy=policy, e_by_rr=e_by, lb_by_rr=lb_by, levels=(0.0,),
        path_hook=hook, rtp=False, routing=f["routing"], cross_account=bool(f.get("cross_account_rule", False)),
        flip=gf.flip_spec_of(cfg), hold_to_own_exit=bool(f.get("hold_to_own_exit", False)),
        one_at_a_time=5.0 if switch == "strict" else None)
    df["placement"] = "off"
    return df


def switch_rows(sets: dict, cfg: dict, pid: str, switch: str, *, seed: int | None = None,
                n_paths: int | None = None, horizon: int | None = None) -> tuple[list[dict], list[dict]]:
    """Cell (a) under one switch: the point arm and the zero-edge twin from ONE engine call -- the twin as its
    lower-bound arm with every R's bound set to zero, which shifts each R by minus its edge exactly as
    `portfolio_stage.zero_edge_blocks` does (checked on the baseline against fv3_corrected_v1's twin)."""
    import portfolio_stage as ps
    import score_fv3_grid as gf

    seed = SEED if seed is None else int(seed)
    n_paths = N_PATHS if n_paths is None else int(n_paths)
    horizon = HORIZON if horizon is None else int(horizon)
    t, days, tv, rule = sets["fv3c"]
    pol = plan("v12", cfg, pid)
    keys = rr_keys(t)
    stats = stats_of(t, days, keys, rule)
    blocks, _ = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
    e_by = ps._by(stats, "e")
    sink: list[dict] = []
    hook, inner = hook_for(sink)
    ps._label(inner, f"sw {switch} gate")
    df = run_fv3c_switched(blocks, cfg, tv, pol, e_by, {k: 0.0 for k in e_by}, hook, switch, seed=seed,
                           n_paths=n_paths, horizon=horizon)
    out = []
    for arm, shift in (("point", "point"), ("twin", "lower_bound")):
        r = df[df["shift"] == shift].iloc[0]
        out.append({"section": "switch", "switch": switch, "what": SWITCHES[switch], "arm": arm, "seed": seed,
                    "paths": n_paths, "horizon": horizon, "policy_id": pol.id,
                    **{k: r[k] for k in KEEP if k in r.index and k != "shift"},
                    **path_summary(sink, f"sw {switch} gate", shift)})
    return out, sink


def run_switches(rd: Path, results_dir: Path | None) -> int:
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import read_result, write_result

    cfg = fv3_config()
    pid = fv3_cell(rd)
    t, days, tv = fv3_trades(rd)
    sets = {"fv3c": (t, days, tv, "yearly")}
    rows, counter = [], VariantCounter(path=Path(rd) / "variants.jsonl")
    for sw in SWITCHES:
        print(f"switch {sw}: {SWITCHES[sw]}...", flush=True)
        r, sink = switch_rows(sets, cfg, pid, sw)
        if sw == "none":
            bad = path_problems(sink, read_result(Path(rd) / f"{FV3_RUN}_paths.csv"), SWITCH_PAIRS, N_PATHS)
            print(f"  identity with {FV3_RUN} (point and twin): {'HOLDS' if not bad else 'FAILS'}", flush=True)
            if bad:
                print("REFUSED (identity): " + "; ".join(bad[:8]))
                return 3
        else:
            counter.record(prereg_id=FAMILY_ID, seed=SEED, exploratory=True,
                           params={"cell": "a", "switch": sw, "paths": N_PATHS, "horizon": HORIZON},
                           label=f"zero-edge decomposition (D-485 (4)), post-hoc switch diagnostic: {sw}")
        rows += r
        print("  " + "  ".join(f"{x['arm']} {x['pf_growth_on_base_p50']:+.4f}" for x in r), flush=True)
    res = pd.DataFrame(rows + [{"section": "identity", "check": f"the 'none' switch's point and twin equal "
                                f"{FV3_RUN}_paths.csv's first {N_PATHS}", "holds": True}])
    n_var = len({r["variant_id"] for r in counter.all() if r.get("prereg_id") == FAMILY_ID})
    write_result(res, f"{RESULT}_switches", script=SCRIPT, seed=SEED, exploratory=True, results_dir=results_dir,
                 variant_count=n_var,
                 parameters={"decision": DECISION, "cell": "a (FV3-C's trades, v12, FV3-C's protocol)",
                             "switches": SWITCHES, "paths": N_PATHS, "horizon": HORIZON, "seed": SEED,
                             "v12_cell": pid, "arms": ["point", "twin"],
                             "twin": "the lower-bound arm with every R's bound zero (= zero_edge_blocks)"},
                 notes={"status": "EXPLORATORY and POST-HOC: chosen after reading results/zero_edge_decomposition.csv "
                                  "(cell f's twin about half of cell a's); a diagnosis of which protocol switch the v12 "
                                  "table's money depends on, never a selection",
                        "variant_count_rule": "the family's distinct configurations (the grid's nine and these four)"},
                 description="EXPLORATORY, post-hoc (D-485 (4)): FV3-C's trades and v12 table under FV3-C's protocol "
                             "with one of P-11's switches at a time (strict one-at-a-time, pessimistic settlement, the "
                             "funded room cap, no stand-aside), the point arm and the zero-edge twin at 150 paths.")
    pd.set_option("display.width", 200)
    print(res[res["section"] == "switch"].pivot_table(index="switch", columns="arm", values="pf_growth_on_base_p50",
                                                      sort=False).round(4).to_string())
    return 0


# ------------------------------------------------------------------------------------------------ the grid


def trade_sets(rd: Path) -> dict[str, tuple]:
    """Every trade set the grid reads: (trades, days, tick value, bound rule)."""
    t, days, tv = fv3_trades(rd)
    ta, da = a1_trades(rd)
    return {"fv3c": (t, days, tv, "yearly"), "a1": (ta, da, 0.5, "blocks21"),
            "fv3c_thin": (thin(t, ta), days, tv, "yearly"), "fv3c_coarse": (coarse(t), days, tv, "yearly")}


def run_cell(cell: str, sets: dict, cfg: dict, pid: str, *, seed: int | None = None, n_paths: int | None = None,
             horizon: int | None = None) -> tuple[list[dict], list[dict], list[dict]]:
    """One cell: (its three campaign rows, its edge rows, its per-path record); the seed, paths and horizon the
    module's SEED, N_PATHS and HORIZON unless given."""
    import score_fv3_grid as gf

    seed = SEED if seed is None else int(seed)
    n_paths = N_PATHS if n_paths is None else int(n_paths)
    horizon = HORIZON if horizon is None else int(horizon)
    trades_name, plan_name, protocol, what = CELLS[cell]
    t, days, tv, rule = sets[trades_name]
    pol = plan(plan_name, cfg, pid)
    if plan_name.startswith("v12"):
        t = pad(t, sorted(set(rr_keys(t)) | set(policy_rrs(pol))))
    keys = rr_keys(t)
    stats = stats_of(t, days, keys, rule)
    rows, sink = campaign(t, days, tv, keys, stats, pol, protocol, cfg, seed=seed, n_paths=n_paths, horizon=horizon,
                          label=cell)
    own = gf.policy_for_edge(cfg, stats[3.0]["lb"] if stats.get(3.0, {}).get("n", 0) else float("nan"))[2]
    lbs = [v["lb"] for v in stats.values() if v["n"] > 0]
    out = []
    for arm in ARMS:
        r = rows[arm]
        run, shift = ((f"{cell} gate", "point") if arm == "point" else (f"{cell} gate", "lower_bound")
                      if arm == "bound" else (f"{cell} twin", "point"))
        out.append({"section": "campaign", "cell": cell, "arm": arm, "trades_set": trades_name, "plan": plan_name,
                    "protocol": protocol, "description": what, "bound_rule": rule, "seed": seed, "paths": n_paths,
                    "horizon": horizon, "policy_id": getattr(pol, "id", None), "n_trades": len(t), "n_days": len(days),
                    "trades_per_day": len(t) / len(days) if days else float("nan"),
                    "busiest_day": int(t.groupby("date").size().max()) if len(t) else 0,
                    "lowest_offered_lb": float(min(lbs)) if lbs else float("nan"),
                    "v12_cell_by_own_r3_bound": own if plan_name.startswith("v12") else None,
                    **{k: r[k] for k in KEEP if k in r.index}, **path_summary(sink, run, shift)})
    edge = [{"section": "edge", "cell": cell, "trades_set": trades_name, "bound_rule": rule, "rr": R, "e": s["e"],
             "lb": s["lb"], "n": s["n"]} for R, s in stats.items()]
    return out, edge, sink


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import read_result, write_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="the identity checks only; nothing written")
    ap.add_argument("--switches", action="store_true",
                    help="EXPLORATORY, post-hoc: cell (a) with one of P-11's protocol switches at a time")
    a = ap.parse_args(argv)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    if a.switches:
        return run_switches(rd, results_dir)
    cfg = fv3_config()
    pid = fv3_cell(rd)
    sets = trade_sets(rd)

    # the identity checks first: cell (a) against fv3_corrected_v1's first paths, P-11's engine path at its own seed
    t, days, tv, _ = sets["fv3c"]
    import score_fv3_grid as gf
    st = stats_of(t, days, rr_keys(t), "yearly")
    own = gf.policy_for_edge(cfg, st[3.0]["lb"])[2]
    if own != pid:
        print(f"REFUSED: FV3-C's trades read the v12 cell {own}, not {FV3_RUN}'s {pid}.")
        return 3
    print(f"cell a (the identity): {len(t)} trades on {len(days)} days, {pid}, {N_PATHS} paths...", flush=True)
    rows_a, edge_a, sink_a = run_cell("a", sets, cfg, pid)
    bad = path_problems(sink_a, read_result(rd / f"{FV3_RUN}_paths.csv"), FV3_PAIRS, N_PATHS)
    print(f"  identity with {FV3_RUN}: {'HOLDS' if not bad else 'FAILS'}", flush=True)
    if bad:
        print("REFUSED (identity): cell (a) does not reproduce FV3-C's development paths -- " + "; ".join(bad[:8]))
        return 3
    ta, da, _, _ = sets["a1"]
    print(f"P-11's engine path at its own seed, {P11_CHECK_PATHS} paths...", flush=True)
    bad = p11_check(rd, ta, da, cfg)
    print(f"  identity with {P11_RUN}: {'HOLDS' if not bad else 'FAILS'}", flush=True)
    if bad:
        print("REFUSED (identity): P-11's engine path does not reproduce its paths -- " + "; ".join(bad[:8]))
        return 3
    identity = [{"section": "identity", "check": f"cell a's first {N_PATHS} paths equal {FV3_RUN}_paths.csv's",
                 "compared": ",".join(PATH_COLS), "pairs": len(FV3_PAIRS), "paths": N_PATHS, "holds": True},
                {"section": "identity", "check": f"P-11's engine at seed {P11_SEED}, first {P11_CHECK_PATHS} paths "
                 f"equal {P11_RUN}_paths.csv's", "compared": ",".join(PATH_COLS), "pairs": len(P11_PAIRS),
                 "paths": P11_CHECK_PATHS, "holds": True}]
    if a.check:
        print("identity checks hold; nothing written (--check).")
        return 0

    camp, edges = list(rows_a), list(edge_a)
    counter = VariantCounter(path=rd / "variants.jsonl")
    for cell in CELLS:
        if cell != "a":
            tn = CELLS[cell][0]
            print(f"cell {cell}: {CELLS[cell][3]} ({len(sets[tn][0])} trades)...", flush=True)
            r, e, _ = run_cell(cell, sets, cfg, pid)
            camp += r
            edges += e
        counter.record(prereg_id=FAMILY_ID, seed=SEED, exploratory=True,
                       params={"cell": cell, "trades": CELLS[cell][0], "plan": CELLS[cell][1],
                               "protocol": CELLS[cell][2], "paths": N_PATHS, "horizon": HORIZON},
                       label=f"zero-edge decomposition (D-485 (4)): cell {cell}")
        last = camp[-3:]
        print("  " + "  ".join(f"{x['arm']} {x['pf_growth_on_base_p50']:+.4f}" for x in last), flush=True)
    res = pd.DataFrame(camp + edges + reference_rows(rd) + identity)
    write_result(res, RESULT, script=SCRIPT, seed=SEED, exploratory=True, results_dir=results_dir,
                 variant_count=len(CELLS),
                 parameters={"decision": DECISION, "cells": {k: {"trades": v[0], "plan": v[1], "protocol": v[2],
                                                                 "what": v[3]} for k, v in CELLS.items()},
                             "paths": N_PATHS, "horizon": HORIZON, "seed": SEED, "thin_seed": THIN_SEED,
                             "levels": [0.0], "placement": "off", "v12_cell": pid, "rr_cap": RR_CAP,
                             "table_rrs": list(TABLE_RRS), "fv3_config": "config/fv3_corrected_portfolio.yaml",
                             "p11_identity": {"seed": P11_SEED, "paths": P11_CHECK_PATHS},
                             "protocol_differences": {k: {"fv3c": v[0], "p11": v[1]}
                                                      for k, v in PROTOCOL_DIFFERENCES.items()},
                             "protocol_same": PROTOCOL_SAME,
                             "metric": "pf_growth_on_base_p50 on pf_required_p90 (the scoreboard's)",
                             "references": [f"results/{FV3_RUN}.csv", f"results/{P11_RUN}.csv"]},
                 notes={"status": "EXPLORATORY (D-485 (4)): a decomposition on development trades already on record; "
                                  "no verdict, no selection, no money decision",
                        "variant_count_rule": "the grid's size: each cell one configuration (D-485 (4))",
                        "identity": "cell a's paths equal fv3_corrected_v1's first 150; P-11's engine path at its own "
                                    "seed equals a1_ins15_gate's first 20"},
                 description="EXPLORATORY (D-485 (4)): where FV3-C's zero-edge money comes from -- a declared grid of "
                             "trade sets (FV3-C's, A1-INS15's, FV3-C's thinned or coarsened), plans (FV3-C's v12 table, "
                             "T24-GF15b's fixed plan) and protocols (FV3-C's, P-11's), each at 150 paths over 504 "
                             "sessions on one seed, its point arm, one-sided 0.05 bound arm and zero-edge twin read on "
                             "the gate's measure; the 500-path rows on record beside.")
    show = res[res["section"] == "campaign"].pivot_table(index="cell", columns="arm", values="pf_growth_on_base_p50",
                                                          sort=False)
    beside = res[(res["section"] == "campaign") & (res["arm"] == "twin")].set_index("cell")[
        ["pf_required_p90", "combine_pass_share", "mean_payouts_per_path", "mean_combine_purchases"]]
    pd.set_option("display.width", 200)
    print(show.join(beside.add_prefix("twin_")).round(4).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
