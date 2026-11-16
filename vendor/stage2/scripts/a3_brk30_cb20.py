"""A3-BRK30-CB20 (D-509): P-13's design -- A3-BRK30's trades, its strict rule and FV3-C's protocol -- with the two
restraints D-501's compliance study read (D-504): FV3-C's v12 table re-solved WITHOUT closing funded accounts at request
(D-502's no-closure table) and a self-imposed budget of 20 Combine purchases and resets in any 21 trading days; and its
registered development test, whose verdict carries the gate AND D-509 (3)'s consistency ("slice") lines.

    python scripts/a3_brk30_cb20.py --prereg P-xx              # the registered test; refused without a registration
    python scripts/a3_brk30_cb20.py --prereg P-xx --workers 2  # each campaign's paths and the slices across workers
                                                               #   (R11: bit for bit the rows of one process)

**The candidate** (D-509 (1); chosen after D-504's exploratory read, so a new candidate, its pool counting that read):
`scripts/a3_brk30.py`'s cell, trades, bounds, day capacity, seeds, paths, horizon and strict one-at-a-time rule
exactly (P-13's, D-496, D-499), with two changes on EVERY arm, as the strict rule is on every arm:

1. **the plan** is `state_dp_e-0.050_lamstar_noclose` of `results/state_policy_v12_noclose_policies.json` (D-502's
   re-solve of FV3-C's v12 config with `funded_rules.abandon` false, its oracles held; read through its result's
   manifest, hashed line-ending-free, D-503; its sha256 pinned here) -- a funded account ends only by a breach or its
   payout life, so the result no longer rests on `xfa_closure_at_request` or the same-evening seat after a closure;
2. **the purchase budget** `(20, 21)`: a Combine purchase or reset refused while the purchases and resets of the last
   21 trading days (that day's included) have reached 20 (`lockstep`'s D-502 option, `gate.run_gate(purchase_budget=)`).

**The seeds (D-512):** every resampled arm of the registered run draws its paths at a fresh campaign seed,
`SEED` = 20261131, written down in D-512 before anything was read at it -- D-501's compliance study had already run this
configuration's gate campaign at P-13's seed 20261028 (the gatekeeper's refusal). The bootstrap seed (20261017) is
P-13's, unchanged. P-13's seed survives only in the two campaign identities (`IDENTITY_SEED`): the old seed proves the
path, the new seed is the verdict. The slices draw nothing (historical order).

**Identities first, each refusing the run before anything is written** (the order is the cost order):
FV3-C's own trades on A3's campaign path reproduce FV3-C's development paths (`atlas_a3.identity`, P-13's first step);
the trades are A3's screen's cell (`a3_brk30.identity_with_screen`); **P-13's trades**: every R's e, pooled bound, bound
the gate read, count, blocks and sd, and the trade and day counts, equal `results/a3_brk30_gate.csv`'s `edge` and
`verdict` rows (sha256 pinned); the no-closure table is the file D-502 recorded and closes no funded account, and its
fresh decisions are v12's (so P-13's stop distribution, `results/a3_brk30_stop_distribution.csv`, is this card's);
**P-13's campaign**: P-13's own configuration (v12, no budget) reproduces the first `IDENTITY_PATHS` paths of
`results/a3_brk30_gate_paths.csv`'s gate run, point and bound at 0 %, at P-13's seed; **D-508's slices**: the candidate's and FV3-C's
slices equal `results/customer_slices.csv`'s `p13_noclose_b20` and `fv3c` verdict rows, slice for slice (sha256
pinned: the slice machinery is reused, never recomputed differently); **D-501's run**: the candidate's campaign at 0 %
at the OLD seed 20261028 (section `d501_reference`, never a gate row) reproduces `results/a3_compliance_paths.csv`'s
`c_noclose_budget20` run, path for path, point and bound (sha256 pinned) -- before any registered arm runs at 20261131.

**The arms** are P-13's, each with the two changes: the gate (0, 10, 25 and 50 % denial; point and bound), the bound at
0.05/N, the placement on, the zero-edge twin, the fixed-legs twin in P-06's form (stage one's legs, section `twin`), the
extra T24-GF15b reading (section `gf15b_twin`, never deciding), the check period, the Focused Trader Program's 16
declared models (section `ftp`, D-497; beside, never the gate) and the campaign without the strict rule (section
`unstrict_beside`, never deciding) -- with the budget on every one of them, each at `SEED`; the per-path record (D-465)
in `results/a3_brk30_cb20_gate_paths.csv`. **The program and the budget count the same thing** (Combine purchases and
resets per trading day, over the same 21-day window, with `>=`): the program's purchase thresholds at or below the
budget can place (20 places on the day the budget fills), those above it (30, 40, 60, both paths) never place and
equal the campaign without the program -- so the program's summary is also reported over the models that can bind
(`ftp_*_binding`, D-512 (4)). The beside arms that close accounts at request -- the gf15b reading (its plan closes
through `t24_screen._closing`) and the P-13 identity (v12) -- rest on the unverified `xfa_closure_at_request` and
`xfa_seat_frees_at` (D-512 (5)).

**The slice lines** (D-509 (3), fixed BEFORE any slice result existed; D-510's exploratory read came after): over every
start in each configuration's development window, in historical order (`customer_slices`' as-happened replay, its own
functions: `arm_blocks`, `engine_args`, `slice_items`, `run_slices`, `summarise`), the candidate's bound-shifted gate
arm (`verdict`: every R shifted to the 0.05 bound the gate reads) against FV3-C's development configuration as frozen
(FV3-C's v12 table, its own protocol, at its own bound, `customer_slices.fv3c_campaign`), in the same run, at 63
trading days: (a) the share of slices ending positive, (b) the 10th-percentile net, (c) the share with no payout and
(d) the needed bankroll's 95th percentile must each be no worse than FV3-C's (higher, higher, lower, lower; a tie is no
worse); beside: 21 and 126 days. The summary rows in section `slices`, the four lines in section `slice_lines`, every
slice in `results/a3_brk30_cb20_gate_slices.csv`. **The like-for-like reading** (D-512 (3), beside, never deciding): the
same summary over only the start days common to both configurations at each horizon (section `slices_common`).
**What the lines can claim** (D-512): they are D-508's already-computed rows (historical order, no seed) judged against
lines D-509 fixed blind, so a PASS adds nothing on them -- their first unread reading is the confirmation; and they
compare against FV3-C only: "no worse than FV3-C's development configuration", never "the family's most consistent".

**The verdict** (D-509 (3), D-419): the gate's word (`t23_d20.verdict_of` with the lines of `docs/SUCCESS_CRITERIA.md`
§3 -- resolution, realised risk) -- PASS at 0.05/N, CONTINUE at 0.05, FAIL below; then **PASS** only with the gate's
PASS and all four slice lines; the gate's PASS with a slice line failed is **CONTINUE (consistency)**; otherwise the
gate's word. The slice lines are read beside a CONTINUE or a FAIL, never changing it. **CONTINUE (consistency) cannot
occur** on this run: the four lines are already known to hold (D-511, D-512); the word stays in the rule as D-509 wrote it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

if __name__ == "__main__":                 # the registered run's one BLAS thread (D-464 (5)), before numpy loads
    for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import a3_brk30 as B  # noqa: E402

SCRIPT = "scripts/a3_brk30_cb20.py"
DECISION = "D-509"
MODEL = "A3-BRK30-CB20"
K = 1
RESULT = "a3_brk30_cb20_gate"
SLICES_RESULT = f"{RESULT}_slices"
#: D-512: the registered run's campaign seed -- fresh, written down before anything was read at it (D-501 had run this
#: configuration at P-13's 20261028); the bootstrap seed P-13's, unchanged
SEED, SEED_BOOT = 20261131, 20261017
#: P-13's campaign seed (= `a3_brk30.SEED`), used ONLY by the two campaign identities: P-13's configuration and D-501's run
IDENTITY_SEED = 20261028
#: P-13's fixed values, carried (checked equal to `a3_brk30`'s by the tests)
N_PATHS = 500
LEVELS = (0.0, 0.10, 0.25, 0.50)
STRICT_GAP = 5.0
WINDOW = ("2020-01-01", "2026-07-16")
CHECK = ("2025-01-17", "2026-07-16")
ERAS = ((2020, 2022), (2023, 2026))
REALISED_MIN = 0.90
#: the two changes (D-509 (1))
BUDGET = (20, 21)                           # at most 20 Combine purchases and resets in any 21 trading days (D-502)
NOCLOSE_ID = "state_dp_e-0.050_lamstar_noclose"
NOCLOSE_TABLE = "state_policy_v12_noclose"
#: the no-closure policy file's sha256, line-ending-free (D-503): its result's manifest `policies_sha256`
NOCLOSE_POLICIES_SHA256 = "df95d683c2848d863eb4482e9fa0346bfd0563e093288a087e5e269fe7374b0e"
NOCLOSE_TABLE_SHA256 = "1eba6230d2d133115f3ad847707088f40e73e40a3de850881b4831d811e905de"   # state_policy_v12_noclose.csv
#: P-13's registered files (D-500), read for the identities only
P13_RESULT, P13_RESULT_SHA256 = "a3_brk30_gate.csv", "c230f65e329f1c0817e7db29523fd2c6e4d5deed2f203063d7d93902c7f2c880"
P13_PATHS, P13_PATHS_SHA256 = "a3_brk30_gate_paths.csv", "dd298a79a1968233ebda0651bab9579e2eb68afb3c5f8e3a6d225d90f3e305ce"
P13_STOPS = "a3_brk30_stop_distribution.csv"          # the card's stop distribution: the same cell, the same fresh legs
IDENTITY_PATHS = 20                                    # P-13's configuration's first paths reproduced (as FV3-C's 20)
#: D-501's compliance study (exploratory, D-504): the candidate's configuration is its `c_noclose_budget20` variant
COMPLIANCE_PATHS = "a3_compliance_paths.csv"
COMPLIANCE_PATHS_SHA256 = "1fcb719954b267b14690e35bc36c0b3671c09828e924be9c0f36649e4aee9ac0"
COMPLIANCE_RUN = "c_noclose_budget20"
COMPLIANCE_SECTION = "d501_reference"                   # D-512: D-501's run at the old seed, a refusing identity
#: D-508's slice study (exploratory, D-510): the machinery reused; its rows the identity of this run's slices
SLICES_REFERENCE = "customer_slices.csv"
SLICES_REFERENCE_SHA256 = "0009afa7be22a657a065f1939ded0f53088e59e17ca6a338cd74ced0f248bd98"
#: (config, arm, campaign, table, budget) in `customer_slices.CONFIGS`' form; and the D-508 config each must equal
CANDIDATE_SLICE, REFERENCE_SLICE = "a3_brk30_cb20", "fv3c"
SLICE_CONFIGS = ((CANDIDATE_SLICE, "verdict", "p13", "noclose", BUDGET),
                 (REFERENCE_SLICE, "verdict", "fv3c", "v12", None))
SLICE_IDENTITY = {CANDIDATE_SLICE: "p13_noclose_b20", REFERENCE_SLICE: "fv3c"}
HORIZONS = (21, 63, 126)
LINE_HORIZON = 63                           # D-509 (3): the lines at 63 trading days; 21 and 126 beside
#: D-509 (3)'s four lines: (label, summary column, the better direction) -- each no worse than FV3-C's
SLICE_LINES = (("a", "share_positive", "higher"), ("b", "net_p10", "higher"), ("c", "share_no_payout", "lower"),
               ("d", "needed_bankroll_p95", "lower"))
SLICE_LINE_TEXT = {"a": "share of 63-trading-day slices ending positive", "b": "10th-percentile 63-day net",
                   "c": "share of 63-day slices with no payout",
                   "d": "the bankroll needed at the 95th-percentile drawdown from the start (63 days)"}
FTP_VARIANTS = f"{DECISION}:a3_brk30_cb20_ftp"          # the program's 16 models beside the verdict (D-499's precedent)
CONSISTENCY = "CONTINUE (consistency)"
BUDGET_COLS = ("mean_budget_purchase_days_blocked", "mean_budget_resets_refused", "max_budget_purchases_in_window")
SLICE_ID_COLS = ("start_date", "end_net", "positive", "passes", "payouts", "payout_dollars", "no_pass", "no_payout",
                 "days_to_first_pass", "days_to_first_payout", "longest_pass_gap", "longest_payout_gap",
                 "drawdown_from_start", "drawdown_from_high", "needed_bankroll")
TOL = 1e-9


# ------------------------------------------------------------------------------------------------ the verdict logic


def slice_lines(summary: pd.DataFrame, *, candidate: str = CANDIDATE_SLICE, reference: str = REFERENCE_SLICE,
                horizon: int | None = None) -> list[dict[str, Any]]:
    """D-509 (3)'s four lines from `customer_slices.summarise`' rows: at `horizon` (63), the candidate's verdict arm
    against the reference's, each no worse (a tie no worse). One row a line."""
    h = int(LINE_HORIZON if horizon is None else horizon)

    def row(config: str) -> pd.Series:
        r = summary[(summary["config"].astype(str) == config) & (summary["arm"].astype(str) == "verdict")
                    & (summary["horizon"].astype(int) == h)]
        if len(r) != 1:
            raise ValueError(f"{len(r)} summary rows for {config} verdict at {h} days, not one")
        return r.iloc[0]

    c, f = row(candidate), row(reference)
    out = []
    for label, col, better in SLICE_LINES:
        x, y = float(c[col]), float(f[col])
        holds = bool(np.isfinite(x) and np.isfinite(y) and (x >= y if better == "higher" else x <= y))
        out.append({"section": "slice_lines", "line": label, "measure": col, "better": better, "horizon": h,
                    "candidate": x, "reference": y, "difference": x - y, "holds": holds,
                    "text": SLICE_LINE_TEXT[label] + f", no worse than FV3-C's ({better} is better)"})
    return out


def verdict_word(gate_word: str, lines_hold: bool) -> str:
    """D-509 (3): PASS needs the gate's PASS and every slice line; the gate's PASS with a line failed is CONTINUE
    (consistency); a CONTINUE or a FAIL stays the gate's word (D-419), the lines read beside."""
    if gate_word not in ("PASS", "CONTINUE", "FAIL"):
        raise ValueError(f"not a gate word: {gate_word!r}")
    if gate_word == "PASS":
        return "PASS" if lines_hold else CONSISTENCY
    return gate_word


def ftp_can_bind(measure: str, threshold: float, window_days: float | None = None, budget=BUDGET) -> bool:
    """D-512 (4): whether a Focused Trader Program model can place on a campaign under `budget` = (K, W). The program
    and the budget count the same purchases and resets per trading day (`lockstep`: `ftp_bought` and `budget_bought`,
    the same increments), the program over its window (that day included, `>=` its threshold), the budget refusing a
    purchase once the last W days (that day included) reach K. So over any window of at most W days the count never
    exceeds K: a purchase threshold above K never places (30, 40, 60 under 20, both paths); a threshold of K places on
    the day the budget fills; a funded-loss model is not limited by the budget."""
    if str(measure) != "combine_purchases":
        return True
    k, w = int(budget[0]), int(budget[1])
    if window_days is not None and np.isfinite(float(window_days)) and int(window_days) > w:
        return True                                     # a longer program window can hold more than K
    return bool(float(threshold) <= k)


def model_can_bind(mdl, budget=BUDGET) -> bool:
    """`ftp_can_bind` for a `FocusedTraderModel` (D-497's grid): a purchase model by its threshold and window."""
    if mdl.combine_purchases is None:
        return True
    return ftp_can_bind("combine_purchases", float(mdl.combine_purchases), mdl.window_days, budget)


def ftp_binding_summary(ftp_df: pd.DataFrame, budget=BUDGET) -> dict[str, Any]:
    """The verdict row's program summary over the models that can bind under the budget (`ftp_can_bind`), beside
    `a3_brk30.ftp_summary`'s over all 16 (D-512 (4)): the count, the lowest growth at the bound and its model, the
    median, the share above zero -- and the median over all 16, the reading D-504 named for this variant (which carried
    the non-binding models' unchanged growth)."""
    b = ftp_df[ftp_df["arm"] == "bound"].copy()
    wd = b["ftp_window_days"] if "ftp_window_days" in b.columns else pd.Series(np.nan, index=b.index)
    b["can_bind"] = [ftp_can_bind(mz, th, w, budget) for mz, th, w in zip(b["measure"], b["threshold"], wd)]
    g_all = b["growth_on_required"].astype(float)
    sub = b[b["can_bind"]]
    g = sub["growth_on_required"].astype(float)
    i = int(np.nanargmin(g.to_numpy())) if g.notna().any() else None
    return {"ftp_growth_bound_median": float(np.nanmedian(g_all)) if g_all.notna().any() else float("nan"),
            "ftp_models_binding": int(sub["ftp_label"].nunique()),
            "ftp_models_cannot_bind": ";".join(sorted(b.loc[~b["can_bind"], "ftp_label"].astype(str).unique())),
            "ftp_growth_bound_min_binding": float(g.iloc[i]) if i is not None else float("nan"),
            "ftp_growth_bound_min_model_binding": str(sub["ftp_label"].iloc[i]) if i is not None else "",
            "ftp_growth_bound_median_binding": float(np.nanmedian(g)) if g.notna().any() else float("nan"),
            "ftp_share_models_growth_bound_positive_binding": float((g > 0).mean()) if len(g) else float("nan")}


# ------------------------------------------------------------------------------------------------ the plans


def _sha_lf(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def noclose_plan(rd: Path):
    """D-502's no-closure table: `a3_compliance.noclose_policy` (its file against its result's manifest, line-ending
    free; no funded closure) and the hashes D-509 fixed."""
    import a3_compliance as a3

    man = json.loads((Path(rd) / f"{NOCLOSE_TABLE}.csv.manifest.json").read_text(encoding="utf-8"))
    if (man.get("parameters") or {}).get("policies_sha256") != NOCLOSE_POLICIES_SHA256:
        raise SystemExit(f"REFUSED ({DECISION}): {NOCLOSE_TABLE}'s recorded policy is not the one fixed here.")
    if man.get("sha256") != NOCLOSE_TABLE_SHA256:
        raise SystemExit(f"REFUSED ({DECISION}): {NOCLOSE_TABLE}.csv is not the file fixed here.")
    pol = a3.noclose_policy(Path(rd))
    if pol.id != NOCLOSE_ID:
        raise SystemExit(f"REFUSED ({DECISION}): the no-closure policy is {pol.id}, not {NOCLOSE_ID}.")
    return pol


def fresh_problems(noclose, v12, rd: Path | None = None) -> list[str]:
    """The no-closure table's fresh decisions are v12's (FV3-C's declared fresh legs) -- and, with `rd`, P-13's stop
    distribution's recorded `fresh` -- so that file is this card's stop distribution. The problems."""
    out = []
    a, b = B.fresh_decisions(noclose), B.fresh_decisions(v12)
    key = ("risk", "rr", "max_trades", "abandon")
    for ph in ("combine", "funded"):
        if tuple(a[ph][k] for k in key) != tuple(b[ph][k] for k in key):
            out.append(f"the no-closure table's fresh {ph} decision {a[ph]} is not v12's {b[ph]}")
    if rd is not None:
        man = json.loads((Path(rd) / f"{P13_STOPS}.manifest.json").read_text(encoding="utf-8"))["parameters"]
        for ph in ("combine", "funded"):
            if tuple(man["fresh"][ph][k] for k in key) != tuple(a[ph][k] for k in key):
                out.append(f"{P13_STOPS}'s fresh {ph} decision {man['fresh'][ph]} is not the no-closure table's")
    return out


# ------------------------------------------------------------------------------------------------ the identities


def _pinned(rd: Path, name: str, sha: str) -> pd.DataFrame:
    path = Path(rd) / name
    if hashlib.sha256(path.read_bytes()).hexdigest() != sha:
        raise SystemExit(f"REFUSED ({DECISION}): {name} is not the file fixed at registration (sha256 {sha[:12]}).")
    return B._exact(path)


def p13_trade_problems(rd: Path, t: pd.DataFrame, days: list[str], L: dict, *, sha256: str | None = P13_RESULT_SHA256
                       ) -> list[str]:
    """The trades are P-13's: each R's e, pooled bound, bound read, count, blocks and sd equal P-13's `edge` rows, and
    the trade and day counts its verdict row (to 1e-12). The problems."""
    import atlas_a3 as A
    import confirm_fv3 as cf

    path = Path(rd) / P13_RESULT
    if sha256 is not None and hashlib.sha256(path.read_bytes()).hexdigest() != sha256:
        return [f"{P13_RESULT} is not the file fixed at registration (sha256 {sha256[:12]})"]
    s = B._exact(path)
    keys = B.rrs(t)
    st = cf.edge_stats(t, keys, days, 21, None)
    _, _, lb_by, _, _ = A.bounds(t, days, keys, L["cfg"])
    er = s[s["section"] == "edge"].copy()
    er["rr"] = er["rr"].astype(float)
    er = er.set_index("rr")
    out = []
    if set(er.index) != set(float(R) for R in keys):
        return [f"P-13's edge rows at R {sorted(er.index)} against the run's {keys}"]
    for R in keys:
        mine = {"e": st[R]["e"], "lb": st[R]["lb"], "n": st[R]["n"], "blocks": st[R]["blocks"], "sd": st[R]["sd"],
                "lb_gate": lb_by[R]}
        for k, v in mine.items():
            if not B._same(v, er.loc[float(R), k]):
                out.append(f"R {R:g} {k}: {v!r} against P-13's {er.loc[float(R), k]!r}")
    v = s[s["section"] == "verdict"].iloc[0]
    for k, mine in (("trades", len(t)), ("days", len(days))):
        if int(float(v[k])) != int(mine):
            out.append(f"{k}: {mine} against P-13's {v[k]}")
    return out


def p13_campaign_problems(sink: list[dict], rd: Path, n: int, *, label: str = "p13_reference") -> list[str]:
    """P-13's configuration at the first `n` paths against P-13's per-path record (its `gate` run, 0 %)."""
    import zero_edge_decomposition as zd

    ref = _pinned(rd, P13_PATHS, P13_PATHS_SHA256)
    return zd.path_problems(sink, ref, [(label, s, "gate", s) for s in ("point", "lower_bound")], int(n))


def compliance_problems(sink: list[dict], rd: Path, n: int, *, label: str = "gate") -> list[str]:
    """The gate's own campaign at 0 % against D-501's `c_noclose_budget20` run, every path (point and bound)."""
    import zero_edge_decomposition as zd

    ref = _pinned(rd, COMPLIANCE_PATHS, COMPLIANCE_PATHS_SHA256)
    return zd.path_problems(sink, ref, [(label, s, COMPLIANCE_RUN, s) for s in ("point", "lower_bound")], int(n))


def slice_reference_problems(rd: Path, sl: pd.DataFrame) -> list[str]:
    """Each configuration's slices against D-508's file (`SLICE_IDENTITY`), start for start at every horizon, every
    reading (numbers to 1e-9, flags as flags, dates as text). The problems."""
    ref = _pinned(rd, SLICES_REFERENCE, SLICES_REFERENCE_SHA256)
    ref = ref[(ref["section"] == "slice") & (ref["arm"].astype(str) == "verdict")]
    out = []
    for mine, theirs in SLICE_IDENTITY.items():
        a = sl[sl["config"].astype(str) == mine].sort_values(["horizon", "start_day"]).reset_index(drop=True)
        b = ref[ref["config"].astype(str) == theirs].copy()
        b = b[b["horizon"].astype(int).isin({int(h) for h in a["horizon"]})]
        b = b.sort_values(["horizon", "start_day"]).reset_index(drop=True)
        if len(a) != len(b) or not (a["horizon"].astype(int).to_numpy() == b["horizon"].astype(int).to_numpy()).all() \
                or not (a["start_day"].astype(int).to_numpy() == b["start_day"].astype(int).to_numpy()).all():
            out.append(f"{mine}: {len(a)} slices against {SLICES_REFERENCE}'s {len(b)} for {theirs}")
            continue
        for c in SLICE_ID_COLS:
            bad = [i for i in range(len(a)) if not _slice_same(a[c].iloc[i], b[c].iloc[i])]
            if bad:
                i = bad[0]
                out.append(f"{mine} {c}: horizon {int(a['horizon'].iloc[i])} start {int(a['start_day'].iloc[i])} "
                           f"{a[c].iloc[i]!r} against {theirs}'s {b[c].iloc[i]!r} ({len(bad)} differ)")
    return out


def _slice_same(x, y) -> bool:
    if any(isinstance(v, (bool, np.bool_)) or str(v) in ("True", "False") for v in (x, y)):
        return B._truth(x) is B._truth(y)
    try:
        a, b = float(x), float(y)
    except (TypeError, ValueError):
        return str(x) == str(y)
    return (np.isnan(a) and np.isnan(b)) or bool(abs(a - b) <= TOL)


# ------------------------------------------------------------------------------------------------ the slices


def slice_campaigns(rd: Path) -> dict[str, Any]:
    """The two campaigns exactly as D-508 built them: `customer_slices.p13_campaign` (P-13's trades, bounds, capacity,
    strict rule and seed) and `customer_slices.fv3c_campaign` (FV3-C's development campaign, its own protocol)."""
    import customer_slices as cs

    return {"p13": cs.p13_campaign(), "fv3c": cs.fv3c_campaign(Path(rd))}


def run_slices(campaigns: dict[str, Any], plans: dict[str, dict[str, Any]], workers: int,
               horizons=None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """`customer_slices`' own machinery on `SLICE_CONFIGS` (its study's job list, unchanged): (slices, summary)."""
    import customer_slices as cs

    hs = tuple(HORIZONS if horizons is None else horizons)
    jobs = []
    for config, arm, camp, table, budget in SLICE_CONFIGS:
        c = campaigns[camp]
        blk = cs.arm_blocks(c, arm)
        args = cs.engine_args(c.kw, arm, c.blocks, risk_policy=plans[camp][table], purchase_budget=budget)
        jobs.append((config, arm, blk, c.dates, args, cs.slice_items(len(blk), hs)))
    sl = pd.DataFrame(cs.run_slices(jobs, int(workers)), columns=list(cs.SLICE_COLS))
    return sl, cs.summarise(sl)


def common_slices(sl: pd.DataFrame, *, candidate: str = CANDIDATE_SLICE, reference: str = REFERENCE_SLICE
                  ) -> tuple[pd.DataFrame, pd.DataFrame]:
    """D-512 (3), beside and never deciding: the like-for-like reading -- at each horizon, only the slices whose start
    date both configurations have (dates compared as calendar days), summarised by `customer_slices.summarise`
    (section `slices_common`). (the common slices, their summary)."""
    import customer_slices as cs

    day = pd.to_datetime(sl["start_date"].astype(str), format="mixed").dt.strftime("%Y-%m-%d")
    keep = pd.Series(False, index=sl.index)
    for h in sorted({int(x) for x in sl["horizon"]}):
        at = sl["horizon"].astype(int) == h
        a = set(day[at & (sl["config"].astype(str) == candidate)])
        b = set(day[at & (sl["config"].astype(str) == reference)])
        keep |= at & sl["config"].astype(str).isin([candidate, reference]) & day.isin(a & b)
    common = sl[keep].copy()
    summ = cs.summarise(common) if len(common) else pd.DataFrame(columns=["section", "config", "arm", "horizon"])
    summ["section"] = "slices_common"
    summ["reading"] = ("beside, never deciding (D-512 (3)): the start days common to both configurations at each "
                       "horizon")
    return common, summ


# ------------------------------------------------------------------------------------------------ the registered run


def inputs() -> dict:
    return B.inputs()


def _registered_run(pid: str, rd: Path, results_dir: Path | None, L: dict, t: pd.DataFrame, days: list[str],
                    beside: list[dict], ident: dict, *, workers: int = 1, reproduce: bool = False,
                    campaigns: dict[str, Any] | None = None) -> int:
    """The identities that need a campaign, the slices, every arm, the verdict, the files."""
    import atlas_a3 as A
    import confirm_fv3 as cf
    import fv3d_lever_test as lt
    import portfolio_stage as ps
    import score_fv3_grid as gf
    import t23_d20 as td
    import t24_gf15 as tg

    from propedge.backtest.harness import VariantCounter
    from propedge.campaign import gate
    from propedge.reporting.results import write_result
    from propedge.research import ledger as lg

    if reproduce:                                          # R11 (D-479): the same computation, relabelled
        from propedge.reporting.reproduction import writer

        write_result = writer(pid, results_dir)            # noqa: F811 -- outside the repository, exploratory
    cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
    v12 = B.policy(L)
    nc = noclose_plan(rd)
    bad = fresh_problems(nc, v12, rd)
    if bad:
        print(f"REFUSED ({DECISION}): " + "; ".join(bad))
        return 3
    camp = fcfg["gate"]["campaign"]
    n_paths, horizon = int(N_PATHS), int(camp["horizon_days"])
    keys = B.rrs(t)
    cap = B.capacity(t, fcfg)
    n_led = lg.count_n(lg.load_ledger(), model=MODEL, k=K, markets=["NQ"], window=WINDOW)["N"]
    st, e_by, lb_by, lbn_by, era_rows, flagged = B.bounds_at_n(t, days, cfg, n_led)
    by_k = cf.edge_stats(t, keys, days, 21, K)
    blocks, n_used = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise SystemExit("REFUSED: the blocks hold a different number of trades.")
    pcfg = fcfg["portfolio"]
    paths_rows: list[dict] = []
    inner = ps.composed_hook({"margin": float(pcfg["margin"]), "block_days": int(pcfg["block_days"])}, sink=paths_rows)
    hook = lt.lever_hook(inner)

    def go(section: str, blk, eb, lbb, *, plan=nc, levels=(0.0,), rtp=False, strict=True, focused_trader=None,
           budget=BUDGET, n=None, seed=SEED) -> pd.DataFrame:
        ps._label(inner, section)
        kw = A.gate_kwargs(blk, fcfg, tv, plan, eb, lbb, hook, seed=int(seed), n_paths=int(n_paths if n is None else n),
                           horizon=horizon, capacity=cap, levels=levels, rtp=rtp,
                           one_at_a_time=STRICT_GAP if strict else None, focused_trader=focused_trader,
                           purchase_budget=budget)
        df, _ = gate.run_gate(kw.pop("blocks"), workers=int(workers), **kw)      # atlas_a3.run_campaign's call
        df["placement"] = "on" if rtp else "off"
        df.insert(0, "section", section)
        return df

    # P-13's campaign first (its configuration: v12, no budget, P-13's seed), the first IDENTITY_PATHS paths of its record
    ref_df = go("p13_reference", blocks, e_by, lb_by, plan=v12, budget=None, n=IDENTITY_PATHS, seed=IDENTITY_SEED)
    bad = p13_campaign_problems(paths_rows, rd, IDENTITY_PATHS)
    if bad:
        print(f"REFUSED ({DECISION}): P-13's configuration does not reproduce its per-path record -- " + "; ".join(bad[:8]))
        return 3
    ref_df["is_gate_row"] = False
    ref_df["reading"] = f"identity: P-13's configuration reproduces the first {IDENTITY_PATHS} paths of {P13_PATHS}"
    print(f"identity HOLDS: P-13's configuration = the first {IDENTITY_PATHS} paths of {P13_PATHS}", flush=True)
    # D-509 (3): the slices, before any expensive arm -- the candidate's verdict arm and FV3-C's, D-508's machinery
    camps = campaigns if campaigns is not None else slice_campaigns(rd)
    fv_pol = camps["fv3c"].kw["risk_policy"]
    if getattr(fv_pol, "id", None) != B.POLICY_ID or camps["fv3c"].kw.get("one_at_a_time") is not None:
        print(f"REFUSED ({DECISION}): FV3-C's slice campaign is not FV3-C as frozen (v12, its own protocol).")
        return 3
    sl, summ = run_slices(camps, {"p13": {"noclose": nc}, "fv3c": {"v12": fv_pol}}, workers)
    bad = slice_reference_problems(rd, sl)
    if bad:
        print(f"REFUSED ({DECISION}): the slices are not D-508's -- " + "; ".join(bad[:8]))
        return 3
    print(f"identity HOLDS: the candidate's and FV3-C's slices = {SLICES_REFERENCE}'s {SLICE_IDENTITY}", flush=True)
    lines = slice_lines(summ)
    lines_hold = all(r["holds"] for r in lines)
    _, common_summ = common_slices(sl)                     # D-512 (3): beside, never deciding
    have = {(str(c), int(h)) for c, h in zip(common_summ.get("config", []), common_summ.get("horizon", []))}
    if not all((c, LINE_HORIZON) in have for c in (CANDIDATE_SLICE, REFERENCE_SLICE)):
        print(f"REFUSED ({DECISION}): the like-for-like slice reading has no common start day at {LINE_HORIZON} days.")
        return 3
    # D-512: D-501's run at the OLD seed as a refusing identity, BEFORE any registered arm draws at the new seed
    d_df = go(COMPLIANCE_SECTION, blocks, e_by, lb_by, seed=IDENTITY_SEED)
    bad = compliance_problems(paths_rows, rd, n_paths, label=COMPLIANCE_SECTION)
    if bad:
        print(f"REFUSED ({DECISION}): the candidate's campaign at seed {IDENTITY_SEED} is not D-501's {COMPLIANCE_RUN} -- "
              + "; ".join(bad[:8]))
        return 3
    d_df["is_gate_row"] = False
    d_df["reading"] = (f"identity (D-512): the candidate's campaign at P-13's seed {IDENTITY_SEED} reproduces "
                       f"{COMPLIANCE_PATHS}'s {COMPLIANCE_RUN}; the registered arms draw at {SEED}")
    print(f"identity HOLDS: the candidate's campaign at seed {IDENTITY_SEED} = {COMPLIANCE_PATHS}'s {COMPLIANCE_RUN}",
          flush=True)
    # the registered arms, every one at the fresh seed (D-512)
    gate_df = go("gate", blocks, e_by, lb_by, levels=LEVELS)
    n_df = go("gate_at_ledger_n", blocks, e_by, lbn_by)
    n_df = n_df[n_df["shift"] == "lower_bound"]
    on_df = go("placement_on", blocks, e_by, lb_by, rtp=True)
    fr = B.fresh_rr(L)[1]
    zero = {k: 0.0 for k in e_by}
    z_df = go("zero_edge_twin", ps.zero_edge_blocks(blocks, e_by, fr), zero, zero)
    z_df = z_df[z_df["shift"] == "point"]
    f_df = go("twin fixed_legs", blocks, e_by, lb_by, plan=B.fixed_legs())
    f_df = f_df[f_df["shift"] == "point"].copy()           # P-06's twins: the point arm, as traded
    f_df["section"], f_df["twin"] = "twin", "fixed_legs"
    b_df = go("gf15b_twin", blocks, e_by, lb_by, plan=B.gf15b_plan())
    tc_, dc = lt.in_period(t, days, *CHECK)
    ec, lbc = B.check_bounds(tc_, dc, keys)
    bc, _ = gf.gate_blocks(tc_, dc, tv, keys, require_sides=True, require_exits=True)
    c_df = go("check_years", bc, ec, lbc)
    grid = B.ftp_grid()
    ftp_df = B.ftp_frame(gate_df, [go(f"ftp {mdl.label}", blocks, e_by, lb_by, focused_trader=mdl) for mdl in grid])
    ftp_df["reading"] = "beside the verdict, never the gate (D-234, D-497, D-499, D-509)"
    u_df = go("unstrict_beside", blocks, e_by, lb_by, strict=False)
    u_df["is_gate_row"] = False
    u_df["reading"] = ("beside the verdict, never deciding: the candidate's campaign without the strict rule (the "
                       "table and the budget kept), for the strict rule's cost (D-499's form)")
    row = gate_df[(gate_df["shift"] == "lower_bound") & np.isclose(gate_df["enforcement_p"].astype(float), 0.0)].iloc[0]
    g = float(row["pf_growth_on_base_p50"])
    g_n = float(n_df.iloc[0]["pf_growth_on_base_p50"])
    res_rows = B.resolution_rows(t, keys)
    resolves = all(r["resolves"] for r in res_rows)
    realised = float(row.get("realised_to_intended_capped_risk", float("nan")))
    fidelity = bool(np.isfinite(realised) and realised >= REALISED_MIN)
    gate_word = td.verdict_of(g, g_n) if (resolves and fidelity) else "FAIL"
    word = verdict_word(gate_word, lines_hold)

    def at(df, shift, level=0.0):
        r = df[(df["shift"] == shift) & np.isclose(df["enforcement_p"].astype(float), level)]
        return float(r.iloc[0]["pf_growth_on_base_p50"]) if len(r) else float("nan")

    def col(r, c):
        return float(r[c]) if c in r.index and pd.notna(r[c]) else float("nan")

    beside_v = {f"tier3_{c}": col(row, c) for c in B.TIER3}
    for c in ("share_trades_skipped_busy", "share_trades_skipped_opposite", *BUDGET_COLS):
        beside_v[c] = col(row, c)
    beside_v.update({f"growth_bound_denial_{int(round(p * 100))}": at(gate_df, "lower_bound", p) for p in LEVELS[1:]})
    beside_v.update({"growth_point": at(gate_df, "point"), "growth_placement_on": at(on_df, "lower_bound"),
                     "growth_zero_edge_twin": at(z_df, "point"), "growth_fixed_legs_twin": at(f_df, "point"),
                     "growth_gf15b_point": at(b_df, "point"), "growth_gf15b_bound": at(b_df, "lower_bound"),
                     "growth_check_years_bound": at(c_df, "lower_bound"),
                     "growth_unstrict_point": at(u_df, "point"), "growth_unstrict_bound": at(u_df, "lower_bound")})
    beside_v["strict_rule_cost_bound"] = beside_v["growth_unstrict_bound"] - g
    urow = u_df[u_df["shift"] == "lower_bound"].iloc[0]
    beside_v["unstrict_share_trades_skipped_opposite"] = col(urow, "share_trades_skipped_opposite")
    beside_v.update(B.ftp_summary(ftp_df))
    beside_v.update(ftp_binding_summary(ftp_df))           # D-512 (4): over the models that can bind under the budget
    beside_v["ftp_reading"] = "beside the verdict, never the gate (D-234, D-497, D-499, D-509)"
    for r in lines:
        beside_v.update({f"slice_{r['line']}_{r['measure']}_candidate": r["candidate"],
                         f"slice_{r['line']}_{r['measure']}_fv3c": r["reference"],
                         f"slice_{r['line']}_holds": r["holds"]})
    edges = pd.DataFrame([{"section": "edge", "rr": R, "e": st[R]["e"], "lb": st[R]["lb"], "n": st[R]["n"],
                           "blocks": st[R]["blocks"], "sd": st[R]["sd"], "lb_at_ledger_n": st[R]["lb_at_n"],
                           "ledger_n": n_led, "lb_at_k": by_k[R]["lb_at_n"], "k": K, "lb_gate": lb_by[R],
                           "lb_gate_at_ledger_n": lbn_by[R],
                           "d47_met": bool(st[R]["n"] > 0 and st[R]["e"] >= 0.10 and st[R]["lb"] >= 0.05)}
                          for R in keys])
    verdict = pd.DataFrame([{"section": "verdict", "prereg": pid, "gate_growth_on_base_p50": g,
                             "gate_at_ledger_n_growth_on_base_p50": g_n, "resolves": resolves, "gate_verdict": gate_word,
                             "slice_lines_hold": lines_hold, "slice_line_horizon": LINE_HORIZON, "verdict": word,
                             "era_flagged": flagged, "bounds_read": "the lower era's" if flagged else "pooled",
                             "trades": len(t), "days": len(days), "realised_to_intended_capped_risk": realised,
                             "realised_min": REALISED_MIN, "fidelity": fidelity, "trades_per_day_capacity": cap,
                             "busiest_day": B.busiest(t), "ledger_n": n_led, "one_at_a_time": STRICT_GAP,
                             "risk_policy_id": nc.id, "budget_k": BUDGET[0], "budget_window_days": BUDGET[1],
                             **beside_v}])
    summ_out = summ.copy()
    summ_out["section"] = "slices"
    summ_out["reading"] = np.where(summ_out["horizon"].astype(int) == LINE_HORIZON,
                                   "the slice lines' horizon (D-509 (3))", "beside (D-509 (3))")
    idents = [ident, {"section": "identity", "check": f"P-13's trades: each R's e, bounds, count, blocks and sd and "
                                                      f"the trade and day counts equal {P13_RESULT}'s", "holds": True},
              {"section": "identity", "check": f"P-13's configuration at seed {IDENTITY_SEED} reproduces the first "
                                               f"{IDENTITY_PATHS} paths of {P13_PATHS}'s gate run, point and bound at "
                                               "0 %", "holds": True},
              {"section": "identity", "check": f"the slices equal {SLICES_REFERENCE}'s "
                                               + ", ".join(f"{k} = {v}" for k, v in SLICE_IDENTITY.items())
                                               + " (verdict arm, every horizon and start)", "holds": True},
              {"section": "identity", "check": f"the candidate's campaign at 0 % at seed {IDENTITY_SEED} (section "
                                               f"{COMPLIANCE_SECTION}) equals {COMPLIANCE_PATHS}'s {COMPLIANCE_RUN}, all "
                                               f"{n_paths} paths, point and bound; the registered arms at seed {SEED}",
               "holds": True}]
    besides = pd.DataFrame(beside + res_rows + idents
                           + tg.period_rows(t, days, keys, n_led, window=WINDOW, check=CHECK, era_spans=ERAS)
                           + era_rows + tg.sharpe_rows(t, days, keys, n_led))
    res = pd.concat([gate_df, n_df, on_df, z_df, f_df, b_df, c_df, ftp_df, u_df, ref_df, d_df, edges, besides, summ_out,
                     common_summ, pd.DataFrame(lines), verdict], ignore_index=True)
    counter = VariantCounter(path=Path(rd) / "variants.jsonl")
    if not reproduce:                                      # a reproduction is not a configuration tried (R11)
        counter.record(prereg_id=pid, seed=SEED, exploratory=False,
                       params={"study": f"{MODEL} gate", "decision": DECISION, "table": NOCLOSE_ID,
                               "budget": list(BUDGET)},
                       label=f"{MODEL}'s registered test ({pid})")
        for mdl in grid:                                   # the program's models, beside, under their own label
            counter.record(prereg_id=FTP_VARIANTS, seed=SEED, exploratory=True,
                           params={"study": f"{MODEL} Focused Trader Program reading", "registration": pid,
                                   **mdl.as_dict(), "paths": n_paths, "horizon": horizon},
                           label=f"Focused Trader Program beside {MODEL} ({pid}): {mdl.label}")
    tp = Path(rd) / f"{NOCLOSE_TABLE}.csv.manifest.json"          # read (and its hashes checked) by noclose_plan
    tab_man = json.loads(tp.read_text(encoding="utf-8")) if tp.is_file() else {}
    params = {"decision": DECISION, "prereg": pid, "model": MODEL, "k": K, "ledger_n": n_led, "cell": B.cell_label(),
              "atlas_family": B.FAMILY, "walk_family": B.WALK_FAMILY, "config": "config/atlas_a3.yaml",
              "policy_id": nc.id, "policy_v12_reference": v12.id,
              "policies_json": f"results/{NOCLOSE_TABLE}_policies.json",
              "policies_sha256_lf": NOCLOSE_POLICIES_SHA256, "table_result_sha256": tab_man.get("sha256"),
              "budget": list(BUDGET),
              "protocol": "P-13's (atlas_a3.gate_kwargs through gate.run_gate: FV3-C's engine call under "
                          "config/fv3_corrected_portfolio.yaml, the day capacity at the cell's busiest day, the bounds "
                          "over 21-session blocks with P-11's era rule, the operator's strict rule on every arm but the "
                          "unstrict reading beside) with D-509's two changes on every arm: the no-closure table and a "
                          "purchase budget of 20 in 21 trading days",
              "one_at_a_time": STRICT_GAP, "trades_per_day_capacity": cap, "n_paths": n_paths, "horizon": horizon,
              "levels": list(LEVELS), "seed": SEED, "seed_bootstrap": SEED_BOOT, "seed_identity": IDENTITY_SEED,
              "seeds": "D-512: every resampled arm at the fresh campaign seed (written down before any read at it); "
                       "P-13's seed only in the two campaign identities (p13_reference, d501_reference); the slices "
                       "draw nothing",
              "window": list(WINDOW),
              "check": list(CHECK), "eras": [list(x) for x in ERAS], "realised_min": REALISED_MIN,
              "payout_method": camp["payout_method"], "fixed_legs": B.fixed_legs_values(),
              "fixed_legs_config": B.FIXED_LEGS_CONFIG,
              "fixed_legs_twin": "P-06's form (docs/SUCCESS_CRITERIA.md §4): stage one's fixed legs through "
                                 "portfolio_stage.fixed_legs_policy, the budget and the strict rule kept; its point "
                                 "arm, section twin; beside the verdict, never deciding",
              "gf15b_twin": "NOT P-06's form: T24-GF15b's fixed plan, the budget and the strict rule kept; section "
                            "gf15b_twin; never deciding",
              "screen": f"results/{B.SCREEN}", "screen_sha256": B.SCREEN_SHA256,
              "p13_result_sha256": P13_RESULT_SHA256, "p13_paths_sha256": P13_PATHS_SHA256,
              "identity_paths": IDENTITY_PATHS, "compliance_paths_sha256": COMPLIANCE_PATHS_SHA256,
              "compliance_run": COMPLIANCE_RUN, "compliance_section": COMPLIANCE_SECTION,
              "slices_reference_sha256": SLICES_REFERENCE_SHA256,
              "slices_common": "D-512 (3), beside and never deciding: customer_slices.summarise over the start days "
                               "common to both configurations at each horizon (section slices_common)",
              "slice_lines_claim": "D-512: D-508's already-computed rows judged against lines D-509 fixed blind; a PASS "
                                   "adds nothing on them (their first unread reading is the confirmation); against "
                                   "FV3-C's development configuration only, never the family's most consistent",
              "slice_configs": [{"config": c, "arm": a, "campaign": k, "table": tb, "budget": list(bu) if bu else None}
                                for c, a, k, tb, bu in SLICE_CONFIGS],
              "slice_identity": SLICE_IDENTITY, "slice_horizons": list(HORIZONS), "slice_line_horizon": LINE_HORIZON,
              "slice_lines": [{"line": a, "measure": c, "better": d, "text": SLICE_LINE_TEXT[a]}
                              for a, c, d in SLICE_LINES],
              "slice_campaigns": {k: {"sessions": len(v.blocks), "first": v.dates[0], "last": v.dates[-1],
                                      "seed": int(v.kw["seed"]), "one_at_a_time": v.kw.get("one_at_a_time")}
                                  for k, v in camps.items()},
              "verdict_rule": "D-509 (3): PASS = the gate's PASS and all four slice lines; the gate's PASS with a line "
                              "failed = CONTINUE (consistency); otherwise the gate's word (D-419)",
              "ftp": "beside the verdict, never the gate (D-234, D-497, D-499): D-497's 16 declared models on the "
                     "candidate's registered campaign (the budget and the table kept), section ftp",
              "ftp_models": [mdl.as_dict() for mdl in grid], "ftp_variant_label": FTP_VARIANTS,
              "ftp_binding": "D-512 (4): the program and the budget count the same purchases and resets over the same "
                             "window with >=; purchase thresholds above the budget never place, so the summary is also "
                             "reported over the models that can bind (ftp_*_binding)",
              "ftp_models_can_bind": [mdl.label for mdl in grid if model_can_bind(mdl)],
              "closing_beside_arms": "D-512 (5): the gf15b reading (t24_screen._closing) and the P-13 identity (v12) "
                                     "close accounts at request and rest on the unverified xfa_closure_at_request and "
                                     "xfa_seat_frees_at",
              "ftp_variant_count": len(grid), "ftp_reference": f"results/{B.FTP_REFERENCE}",
              "ftp_reference_sha256": B.FTP_REFERENCE_SHA256,
              "unstrict_beside": "beside the verdict, never deciding: the candidate's campaign without the strict rule "
                                 "(the table and the budget kept), for the rule's cost; not a configuration tried",
              "fills_profile": f"config/fills.yaml {B.FILLS_PROFILE} (assumed values, D-95; atlas_a3.fee_by_stop)",
              "fv3c_identity": ident.get("check"), "paths_file": f"{RESULT}_paths.csv",
              "slices_file": f"{SLICES_RESULT}.csv", "workers": int(workers),
              "bars": "data/bars/NQ (Databento GLBX.MDP3 ohlcv-1m, D-458)"}
    status = f"the registered test of {MODEL} ({pid}, {DECISION})"
    write_result(res, RESULT, script=SCRIPT, seed=SEED, exploratory=False, results_dir=results_dir, prereg_id=pid,
                 variant_count=counter.count(pid), parameters=params, notes={"status": status},
                 description=(f"{MODEL}'s registered development test ({DECISION}): P-13's design -- A3-BRK30's trades, "
                              "FV3-C's protocol with the day capacity at the busiest day, the operator's strict rule -- "
                              "with FV3-C's v12 table re-solved without closure at request and a budget of 20 Combine "
                              "purchases and resets in 21 trading days on every arm; the D-145 gate at 0.05/N and 0.05 "
                              "and D-509's four slice lines against FV3-C as frozen (section slice_lines; the summary "
                              "in section slices); beside it P-13's arms (denial ladder, placement on, zero-edge twin, "
                              "fixed-legs twin in P-06's form, gf15b reading, check period, the Focused Trader "
                              "Program's 16 models, the campaign without the strict rule), never the gate."))
    write_result(pd.DataFrame(paths_rows), f"{RESULT}_paths", script=SCRIPT, seed=SEED, exploratory=False,
                 prereg_id=pid, results_dir=results_dir, variant_count=counter.count(pid),
                 parameters={"result": f"{RESULT}.csv", "prereg": pid, "model": MODEL},
                 notes={"status": status, "companion_of": f"{RESULT}.csv"},
                 description=f"The per-path record of {RESULT}.csv (D-465): every resampled path of every campaign "
                             "the registered run ran, labelled by its section.")
    write_result(sl, SLICES_RESULT, script=SCRIPT, seed=SEED, exploratory=False, prereg_id=pid,
                 results_dir=results_dir, variant_count=counter.count(pid),
                 parameters={"result": f"{RESULT}.csv", "prereg": pid, "model": MODEL,
                             "slice_configs": params["slice_configs"], "horizons": list(HORIZONS),
                             "order": "historical (the engine's as-happened replay, D-130; no resampling)",
                             "machinery": "scripts/customer_slices.py (arm_blocks, engine_args, slice_items, "
                                          "run_slices, summarise), unchanged"},
                 notes={"status": status, "companion_of": f"{RESULT}.csv"},
                 description=f"Every slice behind {RESULT}.csv's slice lines (D-509 (3)): each start of the candidate's "
                             "and FV3-C's development windows replayed in historical order for 21, 63 and 126 trading "
                             "days, customer_slices' readings per slice.")
    print(f"{'REPRODUCTION, not a verdict' if reproduce else 'VERDICT'} ({pid}): {word} -- the gate {gate_word}: growth "
          f"on the required bankroll {g:+.4f} at the 95 % bound, {g_n:+.4f} at 0.05/{n_led}; resolves {resolves}; "
          f"realised {realised:.4f}; the slice lines " + ", ".join(f"({r['line']}) {r['holds']}" for r in lines))
    return 0


def registered(pid: str, rd: Path, results_dir: Path | None, *, workers: int = 1, reproduce: bool = False) -> int:
    """The registered run of `pid` (after `main`'s registration check): FV3-C's identity on A3's campaign path, the
    trades' identity with the screen and with P-13, then the run."""
    import atlas_a3 as A

    cfg = A.config(B.FAMILY)
    bad, ident = A.identity(cfg, rd)
    if bad:
        print(f"REFUSED ({DECISION}): FV3-C's trades on A3's campaign path do not reproduce its development paths -- "
              + "; ".join(bad[:8]))
        return 3
    L = inputs()
    t, days = B.cell_trades(L)
    problems = B.identity_with_screen(rd, t, days, L)
    if problems:
        print(f"REFUSED ({DECISION}): the trades are not the screen's cell -- " + "; ".join(problems))
        return 3
    problems = p13_trade_problems(rd, t, days, L)
    if problems:
        print(f"REFUSED ({DECISION}): the trades are not P-13's -- " + "; ".join(problems[:8]))
        return 3
    keys = B.rrs(t)
    f, _ = B.cell_trades(L, "fade")
    beside = (B.rung_rows(t, L) + B.fresh_rows(noclose_plan(rd)) + B.walk_rows(L) + B.fade_rows(f, days, keys)
              + B.drift_rows(t, keys)
              + [{"section": "screen_identity", "check": f"the trades are {B.SCREEN}'s rank 1 ({B.cell_label()}) and "
                  f"P-13's ({P13_RESULT}'s edge and verdict rows)", "holds": True}])
    return _registered_run(pid, rd, results_dir, L, t, days, beside, ident, workers=workers, reproduce=reproduce)


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--prereg", default=None)
    ap.add_argument("--workers", type=int, default=1, help="path and slice workers (R11; bit for bit)")
    a = ap.parse_args(argv)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    from propedge.backtest.harness import PreregRegistry, UnregisteredRunError

    try:
        PreregRegistry.load().require_runnable(a.prereg)
    except UnregisteredRunError as exc:
        print(f"REFUSED ({DECISION}): {exc}")
        return 2
    return registered(a.prereg, rd, results_dir, workers=a.workers)


if __name__ == "__main__":
    raise SystemExit(main())
