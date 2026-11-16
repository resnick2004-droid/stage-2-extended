"""A3-BRK30 (D-494): family A3's top cell -- the 30-minute breakout, followed -- walked on FV3-C's rungs by D-492's rung
rule, sized by FV3-C's exact exported v12 policy under FV3-C's protocol, on NQ; and its registered development test.

    python scripts/a3_brk30.py --stop-distribution     # the card's stop distribution and the plan's facts (EXPLORATORY)
    python scripts/a3_brk30.py --prereg P-xx           # the registered test; refused without a runnable registration

**The cell** (D-492 (4)'s rule: rank 1 of family A3's screen, `results/atlas_screen_a3.csv`, D-494): pattern `brk30` of
`config/atlas_a3.yaml` (A1's grid, kind `brk`, k 30: the first one-minute close beyond the high or the low of the
completed 30-minute bar, in the 30 minutes after it, is the event, on that side, each side once per bar), side rule
`follow`, entered at the open of the fifth bar after the event (the operator's latency, D-428 (1)), events from 17:00 to
14:00 CT, FOMC days and early closes out, no trade before the 07:30 CT cut on a BLS report day.

**Its trades** are the screen's (`atlas_a3._job`'s steps): A1's events as A1's walk found them (`data/atlas/A1`, read
only), walked on FV3-C's 12.5 and 25-point rungs by `propedge/research/fv3_rung_walk.py` into A3's own cache
(`data/atlas/A3`, read only here: a stale or missing cache REFUSES the run, it is never rebuilt by this script), each
event at the rung its hour takes by D-492 (2)'s rule (read from step 0's pinned map) and every R offered there, in
FV3-C's gate-trades shape with FV3-C's cost model at one tick of entry (`atlas_a3.cell_trades`). The day set is every
day record of A1's walk. Before anything else, FV3-C's own development trades through A3's campaign path must reproduce
the first paths of `results/fv3_corrected_v1_paths.csv` (`atlas_a3.identity`, the screen's first step); then the trades
are checked against the screen's own rows for the cell (`identity_with_screen`): the screen file is the one fixed at
registration (sha256), the rung walk's cache inputs, the rung rule and the policy are the ones its manifest records, the
cell is its rank 1 with the same trade count, busiest day, hours, rung shares, resolution and bounds read as its row,
and each R's e, pooled bound, bound read, count and blocks equal its `edge` rows, the era rows its `eras` rows.

**The plan** is FV3-C's exported v12 policy at its own edge cell (`state_dp_e-0.050_lamstar`, D-492 (3)), not re-solved:
the same policy sizes every arm of the run. Its fresh decisions (the card's sizes) are FV3-C's declared fresh legs.

**The run** is the screen's campaign path (`atlas_a3.run_campaign`: FV3-C's engine call under
`config/fv3_corrected_portfolio.yaml`, every switch from it, the day capacity raised to the cell's busiest day, D-469)
**with the operator's strict rule on every arm** (the unstrict reading beside excepted, D-499) -- one open position across all accounts at any moment, five minutes
flat between, each trade to the longest-waiting account able to take it (R2, D-409; `gate.run_gate`'s `one_at_a_time`,
D-429; the setting P-11 and P-12 ran) -- which the operator's standing rule puts above D-492 (3)'s "FV3-C's protocol
verbatim" (D-496, declared before the registered run; the exploratory screen ran without it, and FV3-C's identity keeps
FV3-C's own protocol, since it proves the path) -- at the registered seeds -- the campaign 20261028 (P-11's and P-12's, not the screen's 20261030), the bootstraps
20261017 -- and FV3-C's 500 paths over 504 sessions; the bounds over 21-session blocks with P-11's era rule
(`atlas_a3.bounds`, the screen's, and the same rule at 0.05/N). Arms: the gate (0, 10, 25 and 50 % denial; the point and
the bound), the bound at 0.05/N, the placement on, the zero-edge twin, **the fixed-legs twin in P-06's form**
(`docs/SUCCESS_CRITERIA.md` §4, D-304, D-355, D-488: stage one's fixed legs from `config/fv3_portfolio.yaml`'s
`portfolio.fixed_legs` through `portfolio_stage.fixed_legs_policy`, its point arm one row in section `twin`, `twin` =
`fixed_legs`), and, an extra reading that is NOT P-06's form and never decides, T24-GF15b's fixed plan (section
`gf15b_twin`); the check period's campaign beside; **the Focused Trader Program's 16 declared models** (D-497's grid,
`ftp_sweep.models()`) on this campaign, section `ftp`, and **the campaign without the strict rule** (FV3-C's protocol
unchanged, the screen's design), section `unstrict_beside` -- both beside the verdict, never deciding (D-234, D-499).
The per-path record (D-465) in `results/a3_brk30_gate_paths.csv`.
Beside the verdict: tier 3's exposure (the share of payouts exposed, the break-even denial, Combine purchases in any 21
days, closures at request), tier 2's measures, each R's resolution, the per-era and check-period rows, the deflated
Sharpe at N, the fade cell, the drift rule, the walk caches' identity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from pathlib import Path

if __name__ == "__main__":                 # the registered run's one BLAS thread (D-464 (5)), before numpy loads
    for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/a3_brk30.py"
DECISION = "D-494"
MODEL = "A3-BRK30"
FAMILY, WALK_FAMILY = "A3", "A1"            # A3 walks A1's events on FV3-C's rungs (D-492 (1))
PATTERN, RULE = "brk30", "follow"
KIND, KMIN = "brk", 30
POLICY_ID = "state_dp_e-0.050_lamstar"      # FV3-C's own exported v12 cell (D-492 (3))
K = 1                                       # the selected cell; the screens' cells are counted in N (the ledger)
WINDOW = ("2020-01-01", "2026-07-16")       # development (D-461): the local bars' span, the reserve unread
CHECK = ("2025-01-17", "2026-07-16")        # the window's last eighteen months, reported beside (P-11's, P-12's)
ERAS = ((2020, 2022), (2023, 2026))         # P-11's eras, `config/atlas_a3.yaml`'s `bounds.eras` (checked)
SEED = 20261028                             # the campaign (P-08's, P-09's, P-11's, P-12's; not the screen's 20261030)
SEED_BOOT, REPS = 20261017, 2000            # the eras' whole-year bootstrap and haircut's day bootstrap (t24_gf15's)
N_PATHS = 500                               # FV3-C's gate paths (`config/fv3_corrected_portfolio.yaml`, checked)
LEVELS = (0.0, 0.10, 0.25, 0.50)            # the tier-3 denial ladder: 0 % the gate (D-234), the rest beside
STRICT_GAP = 5.0                            # the operator's strict rule (R2, D-409; D-429's switch): D-160's five minutes,
                                            # `t24_wide.GAP`, P-11's and P-12's -- on every arm (D-496)
REALISED_MIN = 0.90                         # docs/SUCCESS_CRITERIA.md §3: realised over capped intended risk, gate row
UNRESOLVED_MAX = 0.05                       # D-212 as D-308 amended it; `atlas_a3.UNRESOLVED_MAX`
FIXED_LEGS_CONFIG = "config/fv3_portfolio.yaml"   # `portfolio.fixed_legs`: stage one's legs, P-06's twin (D-304, D-488)
#: the Focused Trader Program reading beside the verdict, never the gate (D-234, D-495, D-497, D-499): D-497's declared
#: grid (`ftp_sweep.models()`: Combine purchases and resets in 21 days at 10/20/30/40/60, funded accounts lost at 3/5/10,
#: each alone, on the Slowdown and the Corrective path -- 16 models) on this cell's own registered campaign
FTP_MODELS = 16
FTP_VARIANTS = "D-499:a3_brk30_ftp"         # the variant ledger's label for the 16 program models (exploratory)
FTP_REFERENCE = "ftp_sweep.csv"             # D-498's read on FV3-C's and P-11's campaigns, named beside (never read here)
FTP_REFERENCE_SHA256 = "73123c8a7d013be88646402c30fb823478863c87b43934887d42a38fb27a5d46"   # from a clean 934c36d
FILLS_PROFILE = "assumed"                   # `config/fills.yaml`'s profile the fees come from (atlas_a3.fee_by_stop)
RESULT = "a3_brk30_gate"
SCREEN = "atlas_screen_a3.csv"              # the screen the cell was selected from (D-494)
SCREEN_SHA256 = "f353658410aa0c5d5b71dd149cfc7f2d780c851378f66c52ee281213db25f7c5"   # written from a clean 7c45824, committed 75e2ebb
#: the screen row's readings the run's trades must reproduce (the trades' own facts, not a campaign's)
SCREEN_FACTS = ("trades", "hours_traded", "share_rung_50", "busiest_day", "capacity", "era_flagged", "bounds_read",
                "lb_funded_fresh", "lowest_offered_lb", "policy_id", "resolves")
EDGE_COLS = ("e", "lb_pooled", "lb_read", "n", "blocks")
ERA_COLS = ("diff_lo", "diff_hi", "flagged", "era1_lb", "era2_lb")
TOL = 1e-12
EXIT_KINDS = {"t": "target", "s": "stop", "b": "stop", "f": "flatten"}   # a breakeven exit is a stop (FV3-C's card)


def cell_label(rule: str = RULE) -> str:
    return f"{PATTERN} {rule}"


def config_problems(cfg: dict) -> list[str]:
    """What the cell needs of family A3's declaration: the pattern, FV3-C's exact v12 plan and protocol, A1's walk,
    five bars late, the follow rule, the busiest-day capacity and P-11's bounds. The problems, empty when it holds."""
    out = []
    ids = [i for i, p in enumerate(cfg.get("patterns") or []) if p.get("name") == PATTERN]
    if len(ids) != 1:
        out.append(f"the config holds {len(ids)} patterns named {PATTERN!r}")
    else:
        p = cfg["patterns"][ids[0]]
        if p.get("kind") != KIND or int(p.get("k", 0)) != KMIN:
            out.append(f"{PATTERN} is not the 30-minute breakout: {p}")
    if str(cfg.get("plan")) != "v12_exact":
        out.append(f"the plan is {cfg.get('plan')!r}, not FV3-C's exact v12 policy (D-492 (3))")
    if str((cfg.get("policy") or {}).get("id")) != POLICY_ID:
        out.append(f"the policy is {(cfg.get('policy') or {}).get('id')!r}, not FV3-C's cell {POLICY_ID}")
    if str(cfg.get("protocol")) != "fv3c" or str(cfg.get("capacity")) != "busiest_day":
        out.append("the protocol is not FV3-C's with the day capacity at the busiest day (D-492 (3), D-469)")
    if str(cfg.get("walk_family")) != WALK_FAMILY:
        out.append(f"the walk is {cfg.get('walk_family')!r}'s, not {WALK_FAMILY}'s (D-492 (1))")
    if int(cfg.get("screen_delay_min", -1)) != 5:
        out.append(f"the entry delay is {cfg.get('screen_delay_min')!r}, not five bars (D-428 (1))")
    if RULE not in (cfg.get("side_rules") or []):
        out.append(f"{RULE!r} is not among the side rules")
    b = cfg.get("bounds") or {}
    if (int(b.get("block_days", 0)) != 21 or tuple(tuple(int(y) for y in x) for x in b.get("eras") or ()) != ERAS
            or int(b.get("era_seed", 0)) != SEED_BOOT):
        out.append(f"the bounds are {b!r}, not P-11's (21-session blocks, eras {ERAS}, seed {SEED_BOOT})")
    return out


def pattern_id(cfg: dict) -> int:
    return [i for i, p in enumerate(cfg["patterns"]) if p.get("name") == PATTERN][0]


def inputs() -> dict:
    """Everything the cell reads (`atlas_a3.load_inputs`, A3's walk read only: refused when stale or missing)."""
    import atlas_a3 as A

    return A.load_inputs(FAMILY, write_walk=False)


def fresh_rr(L: dict) -> tuple[float, float]:
    """(the fresh Combine's R, the fresh funded account's R): FV3-C's declared fresh legs."""
    fr = L["fcfg"]["state_policy"]["fresh"]
    return float(fr["combine_rr"]), float(fr["funded_rr"])


def cell_trades(L: dict, rule: str = RULE) -> tuple[pd.DataFrame, list[str]]:
    """The cell's trades and the day set exactly as the screen built them (`atlas_a3._job`): `atlas_a3.cell_trades` at
    the rung rule, the fresh Combine's R for the log's single exit, the config's entry slip; then padded as
    `atlas_a3.run_cell` pads them (every R the policy asks for)."""
    import atlas_a3 as A
    import zero_edge_decomposition as zd

    cfg = L["cfg"]
    bad = config_problems(cfg)
    if bad:
        raise SystemExit("REFUSED: " + "; ".join(bad))
    t = A.cell_trades(L["events"], L["walks"], L["days"], pattern_id(cfg), rule, L["rung"], L["offered"], L["fees"],
                      rr_grid=A.rrs(cfg), fresh_rr=fresh_rr(L)[0], tick_value=L["tv"],
                      entry_ticks=float(cfg["slip_ticks"]))
    if t.empty:
        raise SystemExit(f"REFUSED: the cell {cell_label(rule)} has no trades")
    t = zd.pad(t, sorted(set(A.rrs(cfg)) | set(zd.policy_rrs(L["policy"]))))
    return t, sorted(L["days"]["date"].astype(str))


def rrs(t: pd.DataFrame) -> list[float]:
    import zero_edge_decomposition as zd

    return zd.rr_keys(t)


def busiest(t: pd.DataFrame) -> int:
    return int(t.groupby("date").size().max())


def capacity(t: pd.DataFrame, fcfg: dict) -> int:
    """The day capacity (D-469; `atlas_a3.run_cell`'s reading): the cell's busiest day where FV3-C's five is too few."""
    import portfolio_stage as ps

    return max(busiest(t), int(ps.protocol_of(fcfg).trades_per_day))


# ------------------------------------------------------------------------------------------------ the identity


def _exact(path: Path) -> pd.DataFrame:
    """A result CSV checked against its manifest, then read with every float to its last digit (D-471)."""
    from propedge.reporting.results import verify_result

    ok, msg = verify_result(path)
    if not ok:
        raise ValueError(msg)
    return pd.read_csv(path, float_precision="round_trip", low_memory=False)


def _plain(v):
    return v.item() if isinstance(v, np.generic) else v


def _truth(x) -> bool:
    return x.strip() == "True" if isinstance(x, str) else bool(x)


def _same(a, b) -> bool:
    """Equal as the screen wrote it: a flag as a flag, a number to 1e-12 (NaN equal to NaN), a word as a word."""
    if any(isinstance(x, (bool, np.bool_)) or str(x) in ("True", "False") for x in (a, b)):
        return _truth(a) is _truth(b)
    try:
        x, y = float(a), float(b)
    except (TypeError, ValueError):
        return str(a) == str(b)
    return (np.isnan(x) and np.isnan(y)) or bool(np.isclose(x, y, rtol=TOL, atol=TOL))


def _cell(s: pd.DataFrame) -> pd.Series:
    return (s["pattern"].astype(str) == PATTERN) & (s["rule"].astype(str) == RULE)


def screen_reading(t: pd.DataFrame, days: list[str], L: dict) -> tuple[dict, dict, list[dict]]:
    """(the screen row's facts the trades give, `atlas_a3.bounds`' statistics by R, its era rows) -- computed exactly as
    `atlas_a3._job` and `run_cell` compute them, no campaign."""
    import atlas_a3 as A

    cfg, fcfg = L["cfg"], L["fcfg"]
    keys = rrs(t)
    st, e_by, lb_by, era_rows, flagged = A.bounds(t, days, keys, cfg)
    res, resolves = A.resolution(t, A.rrs(cfg))
    fr = fresh_rr(L)[1]
    facts = {"trades": int(len(t)), "trades_per_day": len(t) / max(len(days), 1),
             "hours_traded": int(t["decision_ct"].nunique()), "share_rung_50": float((t["S"] == 50).mean()),
             "busiest_day": busiest(t), "capacity": capacity(t, fcfg), "era_flagged": bool(flagged),
             "bounds_read": "the lower era's" if flagged else "pooled", "lb_funded_fresh": lb_by[fr],
             "lowest_offered_lb": float(min(v for R, v in lb_by.items() if st[R]["n"] > 0)),
             "policy_id": L["policy"].id, "resolves": bool(resolves), **res}
    edge = {R: {"e": st[R]["e"], "lb_pooled": st[R]["lb"], "lb_read": lb_by[R], "n": int(st[R]["n"]),
                "blocks": int(st[R]["blocks"])} for R in keys}
    return facts, edge, era_rows


def identity_with_screen(rd: Path, t: pd.DataFrame, days: list[str], L: dict, *, sha256: str | None = SCREEN_SHA256,
                         walk_inputs: dict | None = None) -> list[str]:
    """The trades are the screen's cell: the screen file is the one fixed at registration (its sha256); the rung walk's
    cache inputs (A1's cache inputs, the rung walk's code, the rungs, the R grid, the delay), the rung rule and the
    policy are the ones its manifest records; the cell is its rank 1 and every fact of its row the trades give
    (`SCREEN_FACTS`, the unresolved shares) equals the run's; each R's e, pooled bound, bound read, count and blocks
    equal its `edge` rows and each R's era row its `eras` row (to 1e-12). The problems, empty when it holds."""
    import atlas_a3 as A

    path = Path(rd) / SCREEN
    out = []
    if sha256 is not None and hashlib.sha256(path.read_bytes()).hexdigest() != sha256:
        out.append(f"{SCREEN} is not the file fixed at registration (sha256 {sha256[:12]})")
    man = json.loads(Path(str(path) + ".manifest.json").read_text(encoding="utf-8"))
    par = man.get("parameters") or {}
    if walk_inputs is None:
        walk_inputs = A.walk_inputs(L["cfg"], L["a1_inputs"])
    if par.get("walk_cache_inputs") != walk_inputs:
        out.append("the rung walk's cache inputs (A1's cache, the walk's code, the rungs) are not the ones the screen read")
    rule = {h: {"stop_ticks": int(L["rung"][h]), "offered": [float(R) for R in L["offered"][h]]} for h in L["rung"]}
    if par.get("rung_rule") != rule:
        out.append("the rung rule is not the one the screen read")
    if par.get("policy_id") != L["policy"].id:
        out.append(f"the policy {L['policy'].id!r} is not the screen's {par.get('policy_id')!r}")
    s = _exact(path)
    cell = _cell(s)
    scr = s[cell & (s["section"] == "screen")]
    if len(scr) != 1:
        return out + [f"the screen holds {len(scr)} rows for {cell_label()}"]
    row = scr.iloc[0]
    if not (np.isfinite(float(row["rank"])) and int(float(row["rank"])) == 1):
        out.append(f"{cell_label()} is rank {row['rank']} of the screen, not 1 (D-492 (4))")
    facts, edge, era_rows = screen_reading(t, days, L)
    for c in (*SCREEN_FACTS, "trades_per_day", *sorted(k for k in facts if k.startswith("unresolved"))):
        if c not in row.index or not _same(facts.get(c), row[c]):
            out.append(f"{c}: {facts.get(c)!r} against the screen's {row.get(c)!r}")
    er = s[cell & (s["section"] == "edge")].copy()
    er["rr"] = er["rr"].astype(float)
    er = er.set_index("rr")
    if set(er.index) != set(edge):
        return out + [f"edge rows at R {sorted(er.index)} against the run's {sorted(edge)}"]
    for R, d in edge.items():
        for k in EDGE_COLS:
            if not _same(d[k], er.loc[R, k]):
                out.append(f"R {R:g} {k}: {d[k]!r} against the screen's {er.loc[R, k]!r}")
    ea = s[cell & (s["section"] == "eras")].copy()
    ea["rr"] = ea["rr"].astype(float)
    ea = ea.set_index("rr")
    for r in era_rows:
        R = float(r["rr"])
        if R not in ea.index:
            out.append(f"no era row at R {R:g} in the screen")
            continue
        for k in ERA_COLS:
            if k in r and not _same(r[k], ea.loc[R, k]):
                out.append(f"era R {R:g} {k}: {r[k]!r} against the screen's {ea.loc[R, k]!r}")
    return out


# ------------------------------------------------------------------------------------------------ the bounds


def bounds_at_n(t: pd.DataFrame, days: list[str], cfg: dict, n_led: int):
    """The screen's bounds (`atlas_a3.bounds`: each R's 0.05 bound over 21-session blocks, the lower era's when the
    eras are flagged, an R offered in one era its pooled bound, an R offered nowhere e = lb = 0) and the same rule at
    one-sided 0.05/N -- (pooled stats with N, e by R, the bound at 0.05 by R, the bound at 0.05/N by R, the era rows at
    N, flagged). The eras' bootstrap is the screen's (the same Rs, the same seed), so its flag and its 0.05 bounds are
    the screen's; checked here."""
    import atlas_a3 as A
    import confirm_fv3 as cf
    import t24_gf15 as tg

    keys = rrs(t)
    _, e_by, lb_by, _, flagged = A.bounds(t, days, keys, cfg)
    b = cfg["bounds"]
    spans = tuple(tuple(int(y) for y in x) for x in b["eras"])
    st = cf.edge_stats(t, keys, days, int(b["block_days"]), int(n_led))
    yr = t["year"].astype(int)
    both = [R for R in keys if all(((yr >= lo) & (yr <= hi) & t[f"g_{R:g}"].notna()).any() for lo, hi in spans)]
    era_rows, fl, low, low_n = [], False, {}, {}
    if both:
        era_rows, fl, low, low_n = tg.eras(t, days, both, int(n_led), seed=int(b["era_seed"]), era_spans=spans)
    era_rows += [{"section": "eras", "rr": R, "offered": int(st[R]["n"]), "flagged": False,
                  "note": "offered in at most one era: its pooled bound read"} for R in keys if R not in both]
    if bool(fl) != bool(flagged):
        raise RuntimeError("the eras' flag differs from the screen's bounds")
    lbn_by = {}
    for R in keys:
        if int(st[R]["n"]) == 0:
            lbn_by[R] = 0.0
            continue
        want = float(low[R]) if (flagged and R in low) else float(st[R]["lb"])
        if not _same(want, lb_by[R]):
            raise RuntimeError(f"R {R:g}: the 0.05 bound differs from the screen's bounds")
        lbn_by[R] = float(low_n[R]) if (flagged and R in low_n) else float(st[R]["lb_at_n"])
    return st, e_by, lb_by, lbn_by, era_rows, bool(flagged)


def check_bounds(t: pd.DataFrame, days: list[str], keys) -> tuple[dict, dict]:
    """The check period's own pooled e and 0.05 bound by R (P-11's check-period reading); an R offered on none of its
    trades e = lb = 0 (`atlas_a3.bounds`' rule: nothing to shift)."""
    import confirm_fv3 as cf

    st = cf.edge_stats(t, list(keys), days, 21, None)
    e_by = {float(R): (0.0 if int(st[R]["n"]) == 0 else float(st[R]["e"])) for R in keys}
    lb_by = {float(R): (0.0 if int(st[R]["n"]) == 0 else float(st[R]["lb"])) for R in keys}
    return e_by, lb_by


# ------------------------------------------------------------------------------------------------ the plans


def policy(L: dict):
    """FV3-C's exported v12 policy at its own cell, as the screen loaded it (`atlas_a3.policy`)."""
    if L["policy"].id != POLICY_ID:
        raise SystemExit(f"REFUSED: the policy is {L['policy'].id}, not FV3-C's {POLICY_ID}")
    return L["policy"]


def fixed_legs_values() -> dict:
    """Stage one's fixed legs as `FIXED_LEGS_CONFIG` declares them (`portfolio.fixed_legs`), read from the file, never
    typed (D-488)."""
    import yaml

    doc = yaml.safe_load((ROOT / FIXED_LEGS_CONFIG).read_text(encoding="utf-8"))
    return dict(doc["portfolio"]["fixed_legs"])


def fixed_legs():
    """The fixed-legs twin's plan in P-06's form (docs/SUCCESS_CRITERIA.md §4, D-304, D-355, D-488): stage one's legs
    through `portfolio_stage.fixed_legs_policy`, the function P-06's twin used -- beside the verdict, never part of it."""
    import portfolio_stage as ps

    return ps.fixed_legs_policy({"fixed_legs": fixed_legs_values()})


def gf15b_plan():
    """An extra reading beside the verdict, NOT P-06's form and never deciding (D-488's precedent): T24-GF15b's fixed
    plan (D-439), the plan family A1's rescreen sized A1's cells with -- A3's screen rows carry it beside each cell."""
    import t24_gf15b as tb

    return tb.policy()


def fresh_decisions(pol) -> dict[str, dict]:
    """The policy's decision on a fresh Combine and a fresh funded account (A2-NB158's reading of a table)."""
    import a2_nb158 as a2

    return a2.fresh_decisions(pol)


def realised_by_stop(fresh: dict[str, dict], stops_ticks: list[int]) -> dict[str, dict[str, float]]:
    """D-312 (1): each fresh state's dollar risk in whole micros at each rung's stop (in MNQ ticks), under the full
    verified allowance (`model_card.full_allowance`) -- {state: {'<ticks> ticks': $}}."""
    from propedge.research.model_card import full_allowance

    cap = full_allowance()
    out = {}
    for state, d in fresh.items():
        out[state] = {}
        for S in stops_ticks:
            per = int(S) * 0.5                                     # an MNQ tick is $0.50
            out[state][f"{int(S)} ticks"] = float(min(math.floor(d["risk"] / per + 1e-9), cap[state]) * per)
    return out


def fresh_rows(pol) -> list[dict]:
    return [{"section": "policy_fresh", "cell": cell_label(), "phase": ph, "policy_risk": d["risk"],
             "policy_rr": d["rr"], "policy_max_trades": d["max_trades"], "policy_abandon": d["abandon"],
             "regime": d["regime"]} for ph, d in fresh_decisions(pol).items()]


def stop_distribution(t: pd.DataFrame, combine_rr: float, funded_rr: float) -> pd.DataFrame:
    """The card's stops (D-191, D-212; A2-NB158's form): one row per trade and state -- its stop in MNQ ticks, the R,
    the exit its state's bracket took (a breakeven exit a stop, as FV3-C's card reads it) and its date: the Combine at
    the policy's fresh Combine R, the funded account at its fresh funded R, each where the event hour offers that R."""
    rows = []
    for state, R in (("combine", float(combine_rr)), ("funded", float(funded_rr))):
        g = t[t[f"o_{R:g}"].astype(str) != ""]
        rows.append(pd.DataFrame({"market": "NQ", "stop_ticks": g["S"].astype(int), "state": state, "rr": R,
                                  "exit": g[f"o_{R:g}"].map(EXIT_KINDS), "date": g["date"]}))
    return pd.concat(rows, ignore_index=True)


# ------------------------------------------------------------------------------------------------ beside the verdict


def fade_rows(f: pd.DataFrame, days: list[str], keys) -> list[dict]:
    """The pattern's fade cell (the same events, the other side, at the same rungs): each R's net e, its one-sided 95 %
    bound over 21-session blocks and its count -- the directional reading beside the verdict, never part of it."""
    import confirm_fv3 as cf

    st = cf.edge_stats(f, list(keys), days, 21, None)
    return [{"section": "fade", "rr": R, "e": st[R]["e"], "lb": st[R]["lb"], "n": st[R]["n"]} for R in keys]


def drift_rows(t: pd.DataFrame, keys) -> list[dict]:
    """D-271's drift rule in ORB5's form (`a1_ins15.drift_rows`, over A3's R grid): per offered R, pooled and per year,
    the long and the short trades' mean net R, the long share, the balanced net R and the part of e the lean explains."""
    out = []
    side = t["side"].astype(str)
    for R in keys:
        r = t[f"r_{R:g}"].astype(float)
        m = np.isfinite(r.to_numpy())
        if not m.any():
            continue
        years = sorted(int(y) for y in t.loc[m, "year"].unique())
        for period, sel in [("all", m)] + [(str(y), m & (t["year"].astype(int) == y).to_numpy()) for y in years]:
            lo, sh = sel & (side == "long").to_numpy(), sel & (side == "short").to_numpy()
            ml = float(r[lo].mean()) if lo.any() else float("nan")
            ms = float(r[sh].mean()) if sh.any() else float("nan")
            e = float(r[sel].mean())
            bal = (ml + ms) / 2.0
            out.append({"section": "drift", "rr": R, "period": period, "n": int(sel.sum()),
                        "long_share": float(lo.sum() / sel.sum()), "long_mean": ml, "short_mean": ms, "e": e,
                        "balanced": bal, "drift_part": e - bal})
    return out


def resolution_rows(t: pd.DataFrame, keys) -> list[dict]:
    """Each offered R's unresolved share (the 15:10 flatten; a breakeven exit resolved) in the trades as taken, overall
    and in its worst year (`atlas_a3.resolution`'s reading, one row an R)."""
    out = []
    for R in keys:
        o = t[f"o_{R:g}"].astype(str)
        m = o != ""
        if not m.any():
            continue
        f = o[m] == "f"
        worst = float(f.groupby(t.loc[m, "year"]).mean().max())
        out.append({"section": "resolution", "rr": R, "offered": int(m.sum()), "unresolved": float(f.mean()),
                    "unresolved_worst_year": worst,
                    "resolves": bool(f.mean() <= UNRESOLVED_MAX + 1e-12 and worst <= UNRESOLVED_MAX + 1e-12)})
    return out


def walk_rows(L: dict) -> list[dict]:
    """The caches' identity: A1's (its events) and A3's rung walk (its manifest's inputs and rows)."""
    import a1_ins15 as a1
    import atlas_a3 as A

    p = A.cache_dir() / "manifest.json"
    m = json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}
    inp = m.get("inputs") or {}
    a3 = {"section": "walk", "family": FAMILY, "rung_walk_sha256": inp.get("rung_walk_sha256"),
          "stops_ticks": json.dumps(inp.get("stops_ticks")), "delay": inp.get("delay"),
          "a1_cache_matches": inp == A.walk_inputs(L["cfg"], L["a1_inputs"]),
          **{f"rows_{k}": v for k, v in (m.get("rows") or {}).items()}}
    return a1.walk_rows(WALK_FAMILY) + [a3]


def rung_rows(t: pd.DataFrame, L: dict) -> list[dict]:
    """The rung rule's rows (step 0's map read, D-492 (2)) with the cell's trades at each hour."""
    n = t.groupby("decision_ct").size()
    return [{**r, "cell": cell_label(), "cell_trades": int(n.get(r["hour"], 0))} for r in L["rung_rows"]]


def ftp_grid() -> list:
    """D-497's declared grid, exactly as `scripts/ftp_sweep.py` swept FV3-C's and P-11's campaigns (D-498): 16
    `FocusedTraderModel`s, path-major, purchases before losses -- run on this cell's registered campaign beside the
    verdict, never the gate (D-234, D-499)."""
    import ftp_sweep as fs

    grid = fs.models()
    if len(grid) != FTP_MODELS:
        raise RuntimeError(f"the Focused Trader Program grid holds {len(grid)} models, not {FTP_MODELS} (D-497)")
    return grid


def ftp_frame(gate_df: pd.DataFrame, parts: list[pd.DataFrame]) -> pd.DataFrame:
    """The program's rows (section `ftp`): every model's point and bound arms at 0 % denial with the placement off, each
    with growth on the required bankroll (`pf_growth_on_base_p50` at `pf_required_p90`, D-312), its change from the
    gate's own arm at the same shift (the run without the program, common random numbers), the measure and the
    threshold -- `ftp_sweep.sweep_rows`' reading. Never a gate row (D-234, D-497)."""
    base = gate_df[np.isclose(gate_df["enforcement_p"].astype(float), 0.0)].set_index("shift")["pf_growth_on_base_p50"]
    out = []
    for df in parts:
        df = df.copy()
        df["section"] = "ftp"
        df["arm"] = np.where(df["shift"] == "point", "point", "bound")
        df["measure"] = np.where(np.isfinite(df["ftp_combine_purchases"].astype(float)), "combine_purchases",
                                 "funded_lost")
        df["threshold"] = np.where(df["measure"] == "combine_purchases", df["ftp_combine_purchases"].astype(float),
                                   df["ftp_funded_lost"].astype(float))
        df["growth_on_required"] = df["pf_growth_on_base_p50"].astype(float)
        df["required_p90"] = df["pf_required_p90"].astype(float)
        df["growth_change_from_off"] = df["growth_on_required"] - df["shift"].map(base).astype(float)
        df["reading"] = "beside the verdict, never the gate (D-234, D-497, D-499)"
        df["is_gate_row"] = False
        out.append(df)
    return pd.concat(out, ignore_index=True)


def ftp_summary(ftp_df: pd.DataFrame) -> dict:
    """The verdict row's program columns: the model count, the lowest growth at the bound and its model, and the share
    of models whose growth at the bound stays above zero -- read beside the verdict, never as it."""
    b = ftp_df[ftp_df["arm"] == "bound"]
    g = b["growth_on_required"].astype(float)
    i = int(np.nanargmin(g.to_numpy())) if g.notna().any() else None
    return {"ftp_models": int(b["ftp_label"].nunique()),
            "ftp_growth_bound_min": float(g.iloc[i]) if i is not None else float("nan"),
            "ftp_growth_bound_min_model": str(b["ftp_label"].iloc[i]) if i is not None else "",
            "ftp_share_models_growth_bound_positive": float((g > 0).mean()) if len(g) else float("nan"),
            "ftp_reference": f"results/{FTP_REFERENCE}", "ftp_reference_sha256": FTP_REFERENCE_SHA256,
            "ftp_reading": "beside the verdict, never the gate (D-234, D-497, D-499)"}


TIER3 = ("share_payouts_exposed", "pf_break_even_denial_p50", "mean_max_combine_purchases_21d", "mean_combine_purchases",
         "pf_share_combines_abandoned", "pf_share_xfa_abandoned", "share_paid_xfa_closed",
         "mean_same_day_multi_breach_days", "mean_max_mll_breaches_21d")


# ------------------------------------------------------------------------------------------------ the registered run


def _registered_run(pid: str, rd: Path, results_dir: Path | None, L: dict, t: pd.DataFrame, days: list[str],
                    beside: list[dict], ident: dict, *, reproduce: bool = False) -> int:
    """Every arm on A3's campaign path at the registered seeds and paths; the verdict; the files."""
    import atlas_a3 as A
    import confirm_fv3 as cf
    import fv3d_lever_test as lt
    import portfolio_stage as ps
    import score_fv3_grid as gf
    import t23_d20 as td
    import t24_gf15 as tg

    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import write_result
    from propedge.research import ledger as lg

    if reproduce:                                          # R11 (D-479): the same computation, relabelled
        from propedge.reporting.reproduction import writer

        write_result = writer(pid, results_dir)            # noqa: F811 -- outside the repository, exploratory
    cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
    pol = policy(L)
    camp = fcfg["gate"]["campaign"]
    n_paths, horizon = int(N_PATHS), int(camp["horizon_days"])
    keys = rrs(t)
    cap = capacity(t, fcfg)
    n_led = lg.count_n(lg.load_ledger(), model=MODEL, k=K, markets=["NQ"], window=WINDOW)["N"]
    st, e_by, lb_by, lbn_by, era_rows, flagged = bounds_at_n(t, days, cfg, n_led)
    by_k = cf.edge_stats(t, keys, days, 21, K)
    blocks, n_used = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise SystemExit("REFUSED: the blocks hold a different number of trades.")
    pcfg = fcfg["portfolio"]
    paths_rows: list[dict] = []
    inner = ps.composed_hook({"margin": float(pcfg["margin"]), "block_days": int(pcfg["block_days"])}, sink=paths_rows)
    hook = lt.lever_hook(inner)

    def go(section: str, blk, eb, lbb, *, plan=pol, levels=(0.0,), rtp=False, strict=True,
           focused_trader=None) -> pd.DataFrame:
        ps._label(inner, section)
        df = A.run_campaign(blk, fcfg, tv, plan, eb, lbb, hook, seed=SEED, n_paths=n_paths, horizon=horizon,
                            capacity=cap, levels=levels, rtp=rtp, one_at_a_time=STRICT_GAP if strict else None,
                            focused_trader=focused_trader)
        df.insert(0, "section", section)
        return df

    gate_df = go("gate", blocks, e_by, lb_by, levels=LEVELS)
    n_df = go("gate_at_ledger_n", blocks, e_by, lbn_by)
    n_df = n_df[n_df["shift"] == "lower_bound"]
    on_df = go("placement_on", blocks, e_by, lb_by, rtp=True)
    fr = fresh_rr(L)[1]
    zero = {k: 0.0 for k in e_by}
    z_df = go("zero_edge_twin", ps.zero_edge_blocks(blocks, e_by, fr), zero, zero)
    z_df = z_df[z_df["shift"] == "point"]
    f_df = go("twin fixed_legs", blocks, e_by, lb_by, plan=fixed_legs())
    f_df = f_df[f_df["shift"] == "point"].copy()           # P-06's twins: the point arm, as traded
    f_df["section"], f_df["twin"] = "twin", "fixed_legs"
    b_df = go("gf15b_twin", blocks, e_by, lb_by, plan=gf15b_plan())
    tc_, dc = lt.in_period(t, days, *CHECK)
    ec, lbc = check_bounds(tc_, dc, keys)
    bc, _ = gf.gate_blocks(tc_, dc, tv, keys, require_sides=True, require_exits=True)
    c_df = go("check_years", bc, ec, lbc)
    # D-499 (the gatekeeper's items 1 and 3), beside the verdict and never deciding: the Focused Trader Program's 16
    # declared models on this cell's own registered campaign (the gate's blocks, bounds, policy, strict rule, seed and
    # paths; 0 % denial, the placement off), and the same campaign under FV3-C's protocol unchanged (the strict rule
    # off -- the screen's design), so the strict rule's cost is computable
    grid = ftp_grid()
    ftp_df = ftp_frame(gate_df, [go(f"ftp {mdl.label}", blocks, e_by, lb_by, focused_trader=mdl) for mdl in grid])
    u_df = go("unstrict_beside", blocks, e_by, lb_by, strict=False)
    u_df["is_gate_row"] = False
    u_df["reading"] = ("beside the verdict, never deciding: FV3-C's protocol unchanged (the strict rule off, the "
                       "screen's design), for the strict rule's cost (D-499)")
    row = gate_df[(gate_df["shift"] == "lower_bound") & np.isclose(gate_df["enforcement_p"].astype(float), 0.0)].iloc[0]
    g = float(row["pf_growth_on_base_p50"])
    g_n = float(n_df.iloc[0]["pf_growth_on_base_p50"])
    res_rows = resolution_rows(t, keys)
    resolves = all(r["resolves"] for r in res_rows)
    realised = float(row.get("realised_to_intended_capped_risk", float("nan")))
    fidelity = bool(np.isfinite(realised) and realised >= REALISED_MIN)
    word = td.verdict_of(g, g_n) if (resolves and fidelity) else "FAIL"

    def at(df, shift, level=0.0):
        r = df[(df["shift"] == shift) & np.isclose(df["enforcement_p"].astype(float), level)]
        return float(r.iloc[0]["pf_growth_on_base_p50"]) if len(r) else float("nan")

    beside_v = {f"tier3_{c}": float(row[c]) if c in row.index and pd.notna(row[c]) else float("nan") for c in TIER3}
    for c in ("share_trades_skipped_busy", "share_trades_skipped_opposite"):     # the strict rule's refused share (D-429)
        beside_v[c] = float(row[c]) if c in row.index and pd.notna(row[c]) else float("nan")
    beside_v.update({f"growth_bound_denial_{int(round(p * 100))}": at(gate_df, "lower_bound", p) for p in LEVELS[1:]})
    beside_v.update({"growth_point": at(gate_df, "point"), "growth_placement_on": at(on_df, "lower_bound"),
                     "growth_zero_edge_twin": at(z_df, "point"), "growth_fixed_legs_twin": at(f_df, "point"),
                     "growth_gf15b_point": at(b_df, "point"), "growth_gf15b_bound": at(b_df, "lower_bound"),
                     "growth_check_years_bound": at(c_df, "lower_bound"),
                     "growth_unstrict_point": at(u_df, "point"), "growth_unstrict_bound": at(u_df, "lower_bound")})
    beside_v["strict_rule_cost_bound"] = beside_v["growth_unstrict_bound"] - g   # the unstrict arm less the gate's
    urow = u_df[u_df["shift"] == "lower_bound"].iloc[0]
    beside_v["unstrict_share_trades_skipped_opposite"] = (float(urow["share_trades_skipped_opposite"])
                                                          if pd.notna(urow.get("share_trades_skipped_opposite"))
                                                          else float("nan"))
    beside_v.update(ftp_summary(ftp_df))
    edges = pd.DataFrame([{"section": "edge", "rr": R, "e": st[R]["e"], "lb": st[R]["lb"], "n": st[R]["n"],
                           "blocks": st[R]["blocks"], "sd": st[R]["sd"], "lb_at_ledger_n": st[R]["lb_at_n"],
                           "ledger_n": n_led, "lb_at_k": by_k[R]["lb_at_n"], "k": K, "lb_gate": lb_by[R],
                           "lb_gate_at_ledger_n": lbn_by[R],
                           "d47_met": bool(st[R]["n"] > 0 and st[R]["e"] >= 0.10 and st[R]["lb"] >= 0.05)}
                          for R in keys])
    verdict = pd.DataFrame([{"section": "verdict", "prereg": pid, "gate_growth_on_base_p50": g,
                             "gate_at_ledger_n_growth_on_base_p50": g_n, "resolves": resolves, "verdict": word,
                             "era_flagged": flagged, "bounds_read": "the lower era's" if flagged else "pooled",
                             "trades": len(t), "days": len(days), "realised_to_intended_capped_risk": realised,
                             "realised_min": REALISED_MIN, "fidelity": fidelity, "trades_per_day_capacity": cap,
                             "busiest_day": busiest(t), "ledger_n": n_led, "one_at_a_time": STRICT_GAP, **beside_v}])
    besides = pd.DataFrame(beside + res_rows + [ident]
                           + tg.period_rows(t, days, keys, n_led, window=WINDOW, check=CHECK, era_spans=ERAS)
                           + era_rows + tg.sharpe_rows(t, days, keys, n_led))
    res = pd.concat([gate_df, n_df, on_df, z_df, f_df, b_df, c_df, ftp_df, u_df, edges, besides, verdict],
                    ignore_index=True)
    counter = VariantCounter(path=rd / "variants.jsonl")
    if not reproduce:                                      # a reproduction is not a configuration tried (R11)
        counter.record(prereg_id=pid, seed=SEED, exploratory=False,
                       params={"study": f"{MODEL} gate", "decision": DECISION},
                       label=f"{MODEL}'s registered test ({pid})")
        for mdl in grid:                                   # D-499: the program's models, beside, under their own label
            counter.record(prereg_id=FTP_VARIANTS, seed=SEED, exploratory=True,
                           params={"study": f"{MODEL} Focused Trader Program reading", "registration": pid,
                                   **mdl.as_dict(), "paths": n_paths, "horizon": horizon},
                           label=f"Focused Trader Program beside {MODEL} ({pid}): {mdl.label}")
    params = {"decision": DECISION, "prereg": pid, "model": MODEL, "k": K, "ledger_n": n_led, "cell": cell_label(),
              "atlas_family": FAMILY, "walk_family": WALK_FAMILY, "config": "config/atlas_a3.yaml",
              "walk_config": "config/atlas_a1.yaml", "policy_id": pol.id,
              "policies_json": cfg["policy"]["policies_json"], "protocol_config": cfg["policy"]["config"],
              "protocol": "FV3-C's (atlas_a3.run_campaign: portfolio_stage.run_campaign's engine call under "
                          "config/fv3_corrected_portfolio.yaml) except the day capacity raised to the cell's busiest "
                          "day (D-469), the bounds (21-session blocks with P-11's era rule) and the operator's strict "
                          "rule on every arm but the unstrict reading beside (one open position across all "
                          "accounts, five minutes flat between; R2, D-409, D-429; D-496) -- the screen ran without "
                          "it",
              "one_at_a_time": STRICT_GAP, "rule": "strict, five minutes",
              "trades_per_day_capacity": cap, "n_paths": n_paths, "horizon": horizon, "levels": list(LEVELS),
              "seed": SEED, "seed_bootstrap": SEED_BOOT, "reps": REPS, "window": list(WINDOW), "check": list(CHECK),
              "eras": [list(x) for x in ERAS], "realised_min": REALISED_MIN, "unresolved_max": UNRESOLVED_MAX,
              "payout_method": camp["payout_method"], "rung_rule": {h: {"stop_ticks": int(L["rung"][h]),
                                                                         "offered": [float(R) for R in L["offered"][h]]}
                                                                     for h in L["rung"]},
              "walk_cache_inputs": A.walk_inputs(cfg, L["a1_inputs"]), "fees_micro_eq":
                  {str(k): v for k, v in L["fees"].items()},
              "fixed_legs_twin": "P-06's form (docs/SUCCESS_CRITERIA.md §4, D-304, D-355, D-488): stage one's fixed "
                                 f"legs from {FIXED_LEGS_CONFIG} portfolio.fixed_legs through "
                                 "portfolio_stage.fixed_legs_policy; its point arm, section twin, twin fixed_legs; "
                                 "beside the verdict, never deciding",
              "fixed_legs": fixed_legs_values(), "fixed_legs_config": FIXED_LEGS_CONFIG,
              "gf15b_twin": "NOT P-06's form: T24-GF15b's fixed plan (t24_gf15b.policy), the plan A3's screen rows "
                            "carry beside each cell from A1's rescreen; its point and bound rows, section gf15b_twin; "
                            "never deciding",
              "delay": int(cfg["screen_delay_min"]), "screen": f"results/{SCREEN}", "screen_sha256": SCREEN_SHA256,
              "ftp": "beside the verdict, never the gate (D-234, D-495, D-497, D-499): D-497's 16 declared models "
                     "(ftp_sweep.models(): Combine purchases and resets in 21 days at 10/20/30/40/60, funded accounts "
                     "lost in 21 days at 3/5/10, each alone, Slowdown and Corrective) on this cell's registered "
                     "campaign -- the gate's blocks, bounds, policy, strict rule, seed and paths, 0 % denial, the "
                     "placement off, point and bound arms; section ftp, no row a gate row",
              "ftp_models": [mdl.as_dict() for mdl in grid], "ftp_variant_label": FTP_VARIANTS,
              "ftp_variant_count": len(grid), "ftp_reference": f"results/{FTP_REFERENCE}",
              "ftp_reference_sha256": FTP_REFERENCE_SHA256,
              "unstrict_beside": "beside the verdict, never deciding (D-499): the gate's campaign under FV3-C's "
                                 "protocol unchanged -- the strict rule off, the screen's design -- same blocks, "
                                 "bounds, policy, capacity, seed and paths, 0 % denial, the placement off; not a "
                                 "configuration tried (the screen's own cell), so not a variant",
              "fills_profile": f"config/fills.yaml {FILLS_PROFILE} (assumed values, D-95; atlas_a3.fee_by_stop)",
              "fv3c_identity": ident.get("check"), "paths_file": f"{RESULT}_paths.csv",
              "bars": "data/bars/NQ (Databento GLBX.MDP3 ohlcv-1m, D-458)"}
    write_result(res, RESULT, script=SCRIPT, seed=SEED, exploratory=False, results_dir=results_dir, prereg_id=pid,
                 variant_count=counter.count(pid), parameters=params,
                 notes={"status": f"the registered test of {MODEL} ({pid}, {DECISION})"},
                 description=(f"{MODEL}'s registered development test ({DECISION}): family A3's selected cell -- the "
                              "30-minute breakout, followed, five bars late, on FV3-C's 12.5 and 25-point rungs by "
                              "D-492's rung rule -- sized by FV3-C's exact exported v12 policy under FV3-C's protocol "
                              "(the day capacity at the busiest day) with the operator's strict one-at-a-time rule on "
                              "every arm (D-496), on the local NQ bars; the D-145 gate at 0.05/N "
                              "and 0.05; beside it the denial ladder, the placement on, the zero-edge twin, the "
                              "fixed-legs twin in P-06's form and, never deciding, T24-GF15b's plan (section "
                              "gf15b_twin), tier 3's exposure, the Focused Trader Program's 16 declared models "
                              "(section ftp) and the campaign without the strict rule (section unstrict_beside), "
                              "beside the verdict, never the gate (D-499)."))
    write_result(pd.DataFrame(paths_rows), f"{RESULT}_paths", script=SCRIPT, seed=SEED, exploratory=False,
                 prereg_id=pid, results_dir=results_dir, variant_count=counter.count(pid),
                 parameters={"result": f"{RESULT}.csv", "prereg": pid, "model": MODEL},
                 notes={"status": f"the registered test of {MODEL} ({pid}, {DECISION})",
                        "companion_of": f"{RESULT}.csv"},
                 description=f"The per-path record of {RESULT}.csv (D-465): every resampled path of every campaign "
                             "the registered run ran, labelled by its section, so its rows can be re-derived from the "
                             "files.")
    print(f"{'REPRODUCTION, not a verdict' if reproduce else 'VERDICT'} ({pid}): {word} -- growth on the required "
          f"bankroll {g:+.4f} at the 95 % bound, {g_n:+.4f} at 0.05/{n_led}; resolves {resolves}; realised "
          f"{realised:.4f}")
    return 0


def registered(pid: str, rd: Path, results_dir: Path | None, *, reproduce: bool = False) -> int:
    """The registered run of `pid` (after `main`'s registration check): FV3-C's identity on A3's campaign path first
    (`atlas_a3.identity`, the screen's), then the cell's trades and their identity with the screen, then every arm.
    `reproduce` is D-479's seam (`scripts/reproduce_registered.py` only): the same computation, written outside the
    repository as a reproduction, never a verdict, nothing appended to the variant ledger."""
    import atlas_a3 as A

    cfg = A.config(FAMILY)
    bad, ident = A.identity(cfg, rd)
    if bad:
        print("REFUSED (D-494): FV3-C's trades on A3's campaign path do not reproduce its development paths -- "
              + "; ".join(bad[:8]))
        return 3
    L = inputs()
    t, days = cell_trades(L)
    problems = identity_with_screen(rd, t, days, L)
    if problems:
        print("REFUSED (D-494): A3-BRK30's trades are not the screen's cell -- " + "; ".join(problems))
        return 3
    keys = rrs(t)
    f, _ = cell_trades(L, "fade")
    beside = (rung_rows(t, L) + fresh_rows(policy(L)) + walk_rows(L) + fade_rows(f, days, keys) + drift_rows(t, keys)
              + [{"section": "screen_identity", "check": f"the trades are {SCREEN}'s rank 1 ({cell_label()}): its "
                  "sha256, the rung walk's inputs, the rung rule, the policy, the row's facts, the edge and era rows",
                  "holds": True}])
    return _registered_run(pid, rd, results_dir, L, t, days, beside, ident, reproduce=reproduce)


def stop_distribution_main(rd: Path, results_dir: Path | None) -> int:
    """The card's stop distribution and the plan's facts (EXPLORATORY: a reading of the cell's trades and of the policy
    D-492 fixed, no campaign): the trades and their identity with the screen, the fresh decisions, the stops at those
    R, each R's offered count and per-trade sd, the busiest day, the hours and the rungs."""
    import a1_ins15 as a1

    from propedge.reporting.results import write_result

    L = inputs()
    t, days = cell_trades(L)
    problems = identity_with_screen(rd, t, days, L)
    if problems:
        print("REFUSED (D-494): A3-BRK30's trades are not the screen's cell -- " + "; ".join(problems))
        return 3
    pol = policy(L)
    fresh = fresh_decisions(pol)
    crr, frr = fresh_rr(L)
    if (fresh["combine"]["rr"], fresh["funded"]["rr"]) != (crr, frr) or any(
            d["abandon"] or d["max_trades"] == 0 for d in fresh.values()):
        print(f"REFUSED (D-494): the policy's fresh decisions are not FV3-C's declared fresh legs: {fresh}")
        return 3
    keys = rrs(t)
    stops = sorted(int(s) for s in t["S"].unique())
    offered = {f"{R:g}": int(np.isfinite(t[f"r_{R:g}"].astype(float)).sum()) for R in keys}
    sd_r = {f"{R:g}": float(t[f"r_{R:g}"].astype(float).std(ddof=1)) for R in keys if offered[f"{R:g}"] > 1}
    facts, _, _ = screen_reading(t, days, L)
    sd = stop_distribution(t, crr, frr)
    write_result(sd, "a3_brk30_stop_distribution", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 results_dir=results_dir,
                 parameters={"decision": DECISION, "model": MODEL, "cell": cell_label(), "trades": len(t),
                             "days": len(days), "trades_per_day": len(t) / len(days), "busiest_day": busiest(t),
                             "trades_per_day_capacity": capacity(t, L["fcfg"]), "offered": offered, "sd_r": sd_r,
                             "stops_ticks": stops, "share_rung_50": facts["share_rung_50"],
                             "hours_traded": facts["hours_traded"], "long_share": float((t["side"] == "long").mean()),
                             "policy_id": pol.id, "fresh": fresh, "realised_by_stop": realised_by_stop(fresh, stops),
                             "exit_mapping": "target at the state's R; flatten at 15:10; stop or breakeven -> stop",
                             "resolution": {k: v for k, v in facts.items() if k.startswith("unresolved")},
                             "era_flagged": facts["era_flagged"], "screen": f"results/{SCREEN}",
                             "screen_sha256": SCREEN_SHA256,
                             "identity_with_screen": "holds (the row's facts, the edge and era rows, the rung walk's "
                                                     "inputs, the rung rule and the policy)",
                             "walk": a1.walk_rows(WALK_FAMILY)[0]},
                 notes={"status": "the card's stop distribution and the plan's facts (D-494); no campaign",
                        "seed": "none: a reading of the walk and of the policy D-492 fixed"},
                 description="A3-BRK30's stops (D-494): one row per trade and state -- the Combine at the policy's "
                             "fresh Combine R, the funded account at its fresh funded R, each where the event hour "
                             "offers it -- its stop in MNQ ticks, the R, the exit its state's bracket took (a "
                             "breakeven a stop) and its date; the policy's fresh decisions in the manifest.")
    print(f"stop distribution: {len(t)} trades on {len(days)} days, the busiest day {busiest(t)}; fresh Combine "
          f"${fresh['combine']['risk']:,.0f} at {fresh['combine']['rr']:g}R, fresh funded ${fresh['funded']['risk']:,.0f} "
          f"at {fresh['funded']['rr']:g}R")
    return 0


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--stop-distribution", action="store_true")
    ap.add_argument("--prereg", default=None)
    a = ap.parse_args(argv)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    if a.stop_distribution:
        return stop_distribution_main(rd, results_dir)
    from propedge.backtest.harness import PreregRegistry, UnregisteredRunError

    try:
        PreregRegistry.load().require_runnable(a.prereg)
    except UnregisteredRunError as exc:
        print(f"REFUSED ({DECISION}): {exc}")
        return 2
    return registered(a.prereg, rd, results_dir)


if __name__ == "__main__":
    raise SystemExit(main())
