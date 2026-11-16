"""EXPLORATORY (D-578, D-590): S3's candidate at the operator's latency -- the pure parts. `scripts/s3_latency.py` reads
the bars, builds P-16's cell and writes `results/s3_latency.csv`.

**What it is** (DECISIONS.md's D-590 row, fixed before this code was built; D-266, D-589 (5)): S3's one candidate,
`lnbar1x4_follow` (the side of the most recent 1-minute 4-bar `nbar` event, followed; D-588), with the side at mark t
read from bars closed at or before t - 5 minutes instead of at or before t. The alert goes at t - 5 carrying its side;
the order works at the first bar after t exactly as P-16's -- entry, stop, R, table, walk, news-safe cut, engine, seeds
and path counts are S3's unchanged, so the cell's trades are P-16's and only the sides move. No other latency is tried.

**The lag** (`lag_marks`, `lagged_day_sides`): the side at mark t at latency L is S3's side (`s3_event_kinds.day_sides`)
computed at mark t - L, which reads exactly the bars ending at or before t - L (S3's clock: index j of a day's arrays is
a bar's END in minutes after 17:00 CT). A mark with t - L < 0 ("before minute 5 on the clock") ties (0) and, as S3's ties
do, takes the coin's side in the campaign (`s1_sided_coin.campaign_coins`). At L = 0 this is S3's side exactly. P-16's
marks are every five minutes from 0, so at L = 5 the side at mark t is S3's side at the previous mark, and mark 0 ties
(as it does at L = 0: no bar has closed).

**The guards** (`GUARDS`, `guard_rows`): D-578 (2)'s four against P-16 at S3's seeds and path counts, in D-590's order
resolution, G1, G2, G3; each is `s1_sided_coin.verdict`'s own check (its checks are independent of each other, so the
guard just run is read from it alone). The first failing guard ends the run: the rest are `not_run` and the candidate is
False. With all four run, the verdict equals S3's `verdict` (checked).

**Beside, deciding nothing** (`lift_beside`, `changed_share`): stage 1's lift for this one rule at the six offered R at
L = 5 -- the per-R studentised mean lift over S3's stationary session bootstrap (seed 20261109, block 21, 2,000
replicates); one rule, so no family-wise selection (the critical value and survival are not read) -- and the share of
marks whose side changes from L = 0.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from propedge.research import a4_coin_atlas as A4
from propedge.research import s1_sided_coin as S1
from propedge.research import s3_event_kinds as S3

DECISION = "D-578"
DECLARED_BY = "D-590"
VARIANT = "S3-L5"
FAMILY_ID = f"{DECISION}:{VARIANT}"
RESULT = "s3_latency"
N_VARIANTS = 1
LATENCY = 5                                # minutes on the clock (D-266: the operator's L)
RULE = "lnbar1x4"
SIGN = 1                                   # follow
S3_ARM = "lnbar1x4_follow"                 # S3's campaign row (results/s3_event_kinds.csv)
ARM_L0 = f"{S3_ARM}_L0"
ARM = f"{S3_ARM}_L{LATENCY}"
REFERENCE = "P16_coin"
NOT_RUN = "not_run"
#: S3's constants, unchanged (D-590: "at S3's seeds and path counts")
CAMPAIGN_SEED = S3.CAMPAIGN_SEED
N_PATHS = S3.N_PATHS
COIN_SEEDS = S3.COIN_SEEDS
G2_PATHS = S3.G2_PATHS
G2_WINS = S3.G2_WINS
MARGIN = S3.MARGIN
SPANS = S3.SPANS
STOP_TICKS = S3.STOP_TICKS
OFFERED_R = S3.OFFERED_R
BOOT_SEED = S3.BOOT_SEED
BOOT_BLOCK = S3.BOOT_BLOCK
BOOT_REPS = S3.BOOT_REPS
#: the rule's entry in S3's menu
RULE_SPEC = next(r for r in S3.RULES if r[0] == RULE)
RULE_INDEX = S3.RULE_NAMES.index(RULE)

#: `results/s3_event_kinds.csv` as D-588 read it and D-589 audited it (its manifest's sha256)
S3_RESULT_FILE = "s3_event_kinds.csv"
S3_RESULT_SHA256 = "f5e0a8f2bebbac74b4a1808ddb593f152f209eb5cfe16162801d5e6286c64528"
#: identities (c) and (d): the columns compared with S3's campaign rows, and the tolerance (S1's identity (iii)'s)
IDENT_COLS = ("growth_on_required", "growth_on_required_point", "required_p90", "growth_zero_edge_twin")
IDENT_ATOL = 1e-9
#: the stage-1 reproduction at L = 0 against S3's lift rows (the same bootstrap; floating matrix products only)
LIFT_RTOL = 1e-9
LIFT_P_ATOL = 2.0 / BOOT_REPS

#: D-590's order, each guard with `s1_sided_coin.verdict`'s check
GUARDS = ("resolution", "g1", "g2", "g3")
GUARD_CHECK = {"resolution": "b_every_offered_r_resolves", "g1": "a_paired_beats_by_margin",
               "g2": "c_wins_coin_sequences", "g3": "d_not_below_on_either_span"}

# ------------------------------------------------------------------------------------------------ the declaration

#: DECISIONS.md's D-590 row (LF, the line itself): its sha256 and the phrases each constant rests on
DECLARATION_SHA256 = "46157dd3bb66bd4abec043b3799258d72311d4547832a87f80f5be113ebc573b"
D590_WORDS = (
    "Declared before it is built or read (EXPLORATORY)",
    f"`{S3_ARM}` with the side at mark t read from bars closed at or before t - {LATENCY} minutes",
    f"The alert goes at t - {LATENCY} carrying its side",
    "the order works at the first bar after t exactly as P-16's (entry, stop, R, table, walk, news-safe cut and engine "
    "unchanged, so the cell's trades are P-16's and only sides move)",
    f"a mark before minute {LATENCY} on the clock ties and takes the coin's side, as S3's ties do",
    "No other latency is tried",
    "at L = 0 the side table equals S3's for the rule at every mark",
    f"its paired G1 row at seed {CAMPAIGN_SEED}, {N_PATHS} paths reproduces `results/{S3_RESULT_FILE}`'s `{S3_ARM}` "
    "campaign row",
    "the reference is S3's P-16 row",
    "D-578's four against P-16, at S3's seeds and path counts, in the order resolution, G1, G2, G3",
    "the first failing guard ends the run and the rest are reported as not run (any failure fails the candidate)",
    f"stage 1's lift for this rule at the six R at L = {LATENCY} (S3's bootstrap seed and block)",
    "the share of marks whose side changes from L = 0",
    f"One variant, `{FAMILY_ID}`",
    f"Writes `results/{RESULT}.csv`",
    "workers 1",
)


def declaration(path: Path | str | None = None) -> dict[str, Any]:
    """DECISIONS.md's D-590 row (LF line ends, the line itself) and its sha256 (`p16_slip_stress.declaration`'s way)."""
    p = Path(path) if path is not None else Path(__file__).resolve().parents[2] / "DECISIONS.md"
    text = p.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")
    rows = [line for line in text.split("\n") if line.startswith(f"| {DECLARED_BY} |")]
    row = rows[0] if len(rows) == 1 else ""
    return {"path": str(p), "rows": len(rows), "row": row, "sha256": hashlib.sha256(row.encode("utf-8")).hexdigest()}


def declaration_problems(decl: Mapping[str, Any]) -> list[str]:
    """Every way this module's constants differ from D-590's row and from S3's build (an empty list: they agree)."""
    out = []
    if int(decl["rows"]) != 1:
        out.append(f"DECISIONS.md holds {decl['rows']} {DECLARED_BY} rows, not one")
    if str(decl["sha256"]) != DECLARATION_SHA256:
        out.append(f"the {DECLARED_BY} row's sha256 is {str(decl['sha256'])[:16]}, not the pinned "
                   f"{DECLARATION_SHA256[:16]}")
    row = re.sub(r"\s+", " ", str(decl["row"]))
    out += [f"{DECLARED_BY} does not say {w!r}" for w in D590_WORDS if w not in row]
    # S3's build is the one D-588 read: its declaration, its shared constants, its rule and arm
    out += [f"S3: {x}" for x in S3.declaration_problems(S3.declaration()) + S3.shared_problems()]
    if RULE_SPEC != (RULE, "event", {"kind": "nbar", "k": 1, "n": 4}):
        out.append(f"S3's {RULE} is {RULE_SPEC!r}, not the 1-minute 4-bar nbar event")
    if S3.arm_name(RULE, SIGN) != S3_ARM:
        out.append(f"S3's arm name for ({RULE}, {SIGN}) is {S3.arm_name(RULE, SIGN)!r}, not {S3_ARM!r}")
    return out


# ------------------------------------------------------------------------------------------------ the lag


def lag_marks(marks: Sequence[int], latency: int = LATENCY) -> tuple[np.ndarray, np.ndarray]:
    """(the mark each side is read at, t - L clipped at 0; whether t - L >= 0). A mark with t - L < 0 ties."""
    if int(latency) < 0:
        raise ValueError("latency is at least 0")
    M = np.asarray([int(m) for m in marks], dtype=np.int64)
    at = M - int(latency)
    valid = at >= 0
    return np.where(valid, at, 0), valid


def lagged_day_sides(o: Sequence, h: Sequence, l: Sequence, c: Sequence, marks: Sequence[int],
                     latency: int = LATENCY, *, prev_close: float | None = None,
                     rules: Sequence[tuple[str, str, dict]] = (RULE_SPEC,)) -> dict[str, np.ndarray]:
    """{rule: side at each mark at latency L}: S3's `day_sides` at mark t - L (bars ending at or before t - L); a mark
    with t - L < 0 ties (0). At L = 0, S3's `day_sides` exactly."""
    at, valid = lag_marks(marks, latency)
    sd = S3.day_sides(o, h, l, c, at.tolist(), prev_close=prev_close, rules=rules)
    return {k: np.where(valid, v, 0).astype(np.int8) for k, v in sd.items()}


def shift_problems(l0: Mapping[str, np.ndarray], lag: Mapping[str, np.ndarray], marks: Sequence[int],
                   latency: int = LATENCY) -> list[str]:
    """The lag's identity on a side table ({date: (marks,) sides}): the side at t at latency L equals the L = 0 side at
    t - L wherever t - L is a mark, and ties where t - L < 0. Marks whose t - L is neither are not compared."""
    M = [int(m) for m in marks]
    pos = {m: i for i, m in enumerate(M)}
    out = []
    for d in sorted(set(l0) | set(lag)):
        if d not in l0 or d not in lag:
            out.append(f"{d}: in one table only")
            continue
        a, b = np.asarray(l0[d]), np.asarray(lag[d])
        for i, t in enumerate(M):
            s = t - int(latency)
            want = 0 if s < 0 else (int(a[pos[s]]) if s in pos else None)
            if want is not None and int(b[i]) != want:
                out.append(f"{d} mark {t}: {int(b[i])} at L = {latency}, {want} at L = 0 mark {s}")
                break
    return out


def changed_share(l0: np.ndarray, lag: np.ndarray) -> dict[str, Any]:
    """How the sides move from L = 0 to L: the share of marks whose side differs, and its parts (a flip between sides,
    a side becoming a tie, a tie becoming a side), with the tie shares at both."""
    a, b = np.asarray(l0, dtype=int), np.asarray(lag, dtype=int)
    if a.shape != b.shape:
        raise ValueError("one side per mark at both latencies")
    n = int(a.size)
    share = (lambda m: float(np.sum(m)) / n) if n else (lambda m: float("nan"))
    return {"marks": n, "changed": int(np.sum(a != b)), "share_changed": share(a != b),
            "share_flipped": share((a != 0) & (b != 0) & (a != b)), "share_side_to_tie": share((a != 0) & (b == 0)),
            "share_tie_to_side": share((a == 0) & (b != 0)), "tie_share_l0": share(a == 0),
            "tie_share_lag": share(b == 0)}


# ------------------------------------------------------------------------------------------------ stage 1, beside


def lift_beside(day_sum: np.ndarray, day_n: np.ndarray, *, reps: int = BOOT_REPS, block: float = BOOT_BLOCK,
                seed: int = BOOT_SEED) -> dict[str, np.ndarray]:
    """Per hypothesis (this rule at each offered R): the mean lift, its bootstrap sd, the studentised t, its own
    two-sided bootstrap p and the counted trades -- S3's stage 1 statistics (`a4_coin_atlas.stationary_counts` /
    `maxstat_test` at S3's seed, block and replicates). Each column's statistics are its own (the max-statistic's
    critical value is not read: one rule, no family-wise selection)."""
    counts = A4.stationary_counts(day_sum.shape[0], reps=int(reps), mean_block=float(block), seed=int(seed))
    test = A4.maxstat_test(day_sum, day_n, counts, fwer=S3.ALPHA)
    return {k: np.asarray(test[k]) for k in ("mean", "sd", "t", "p", "trades")}


def lift_problems(mine: Mapping[str, np.ndarray], want: Mapping[str, np.ndarray], *, rtol: float = LIFT_RTOL,
                  p_atol: float = LIFT_P_ATOL) -> list[str]:
    """The L = 0 lift against S3's lift rows for the rule (trades exact; mean, sd, t to `rtol`; p to `p_atol`)."""
    out = []
    if not np.array_equal(np.asarray(mine["trades"], float), np.asarray(want["trades"], float)):
        out.append(f"trades {list(mine['trades'])} against S3's {list(want['trades'])}")
    for k in ("mean", "sd", "t"):
        if not np.allclose(np.asarray(mine[k], float), np.asarray(want[k], float), rtol=rtol, atol=0, equal_nan=True):
            out.append(f"{k} {list(mine[k])} against S3's {list(want[k])}")
    if not np.allclose(np.asarray(mine["p"], float), np.asarray(want["p"], float), rtol=0, atol=p_atol, equal_nan=True):
        out.append(f"p {list(mine['p'])} against S3's {list(want['p'])}")
    return out


# ------------------------------------------------------------------------------------------------ identities


def row_problems(mine: Mapping[str, Any], want: Mapping[str, Any], cols: Sequence[str] = IDENT_COLS,
                 atol: float = IDENT_ATOL) -> list[str]:
    """A campaign row against S3's (each of `cols` within `atol`; a missing value is a problem)."""
    out = []
    for c in cols:
        try:
            a, b = float(mine[c]), float(want[c])
        except (KeyError, TypeError, ValueError):
            out.append(f"{c}: missing")
            continue
        if not (np.isfinite(a) and np.isfinite(b) and abs(a - b) <= atol):
            out.append(f"{c}: {a!r} against S3's {b!r}")
    return out


# ------------------------------------------------------------------------------------------------ the guards


def next_guard(done: Sequence[Mapping[str, Any]]) -> str | None:
    """The guard to run next given those run (in order), or None: every guard ran, or one failed."""
    for i, g in enumerate(done):
        if g["guard"] != GUARDS[i]:
            raise ValueError(f"guard {i + 1} is {GUARDS[i]!r}, not {g['guard']!r}")
        if not bool(g["passes"]):
            return None
    return GUARDS[len(done)] if len(done) < len(GUARDS) else None


def guard_check(guard: str, v: Mapping[str, Any]) -> bool:
    """One guard read from `s1_sided_coin.verdict`'s output (its four checks are independent of each other)."""
    return bool(v[GUARD_CHECK[guard]])


def guard_rows(arm: str, done: Sequence[Mapping[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """(one row per guard in D-590's order -- pass, fail or not_run -- and the verdict row). The first failure ends the
    run; a guard after it, or never reached, is not_run; the candidate needs all four passing."""
    if next_guard(done) is not None:
        raise ValueError(f"guard {next_guard(done)!r} is still to run")
    status = {g: NOT_RUN for g in GUARDS}
    rows = []
    for i, g in enumerate(GUARDS):
        r = done[i] if i < len(done) else None
        status[g] = NOT_RUN if r is None else ("pass" if bool(r["passes"]) else "fail")
        rows.append({"section": "guard", "arm": arm, "order": i + 1, "guard": g, "check": GUARD_CHECK[g],
                     "status": status[g], **({k: v for k, v in r.items() if k not in ("guard", "passes")} if r else {})})
    cand = all(status[g] == "pass" for g in GUARDS)
    first_fail = next((g for g in GUARDS if status[g] == "fail"), "")
    verdict = {"section": "verdict", "arm": arm, **{GUARD_CHECK[g]: status[g] for g in GUARDS},
               "first_failing_guard": first_fail, "candidate": bool(cand)}
    return rows, verdict


def verdict_agrees(verdict: Mapping[str, Any], s3_verdict: Mapping[str, Any]) -> bool:
    """With all four guards run, the staged verdict is S3's `verdict` (every check and the candidate flag)."""
    return all((verdict[GUARD_CHECK[g]] == "pass") == bool(s3_verdict[GUARD_CHECK[g]]) for g in GUARDS) and \
        bool(verdict["candidate"]) == bool(s3_verdict["candidate"])


__all__ = ["DECISION", "DECLARED_BY", "VARIANT", "FAMILY_ID", "RESULT", "N_VARIANTS", "LATENCY", "RULE", "SIGN",
           "S3_ARM", "ARM_L0", "ARM", "REFERENCE", "NOT_RUN", "CAMPAIGN_SEED", "N_PATHS", "COIN_SEEDS", "G2_PATHS",
           "G2_WINS", "MARGIN", "SPANS", "STOP_TICKS", "OFFERED_R", "BOOT_SEED", "BOOT_BLOCK", "BOOT_REPS", "RULE_SPEC",
           "RULE_INDEX", "S3_RESULT_FILE", "S3_RESULT_SHA256", "IDENT_COLS", "IDENT_ATOL", "LIFT_RTOL", "LIFT_P_ATOL",
           "GUARDS", "GUARD_CHECK", "DECLARATION_SHA256", "D590_WORDS", "declaration", "declaration_problems",
           "lag_marks", "lagged_day_sides", "shift_problems", "changed_share", "lift_beside", "lift_problems",
           "row_problems", "next_guard", "guard_check", "guard_rows", "verdict_agrees"]
