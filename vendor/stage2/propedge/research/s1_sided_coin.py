"""EXPLORATORY (D-578): batch S1 of the rolling model search -- the sided coin. Pure functions; `scripts/s1_sided_coin.py`
reads the bars, builds P-16's cell and writes the result.

**What S1 is** (`config/search_program.yaml`, batch S1, fixed by D-578 before this code was built): P-16
(`rc_s150_all_nr` -- the 37.5-point / 150-tick news-safe all-day coin re-entering when flat, an offer every five minutes,
P-14's money side, five Topstep seats) with everything unchanged except the side of each offer. Instead of
`resolved_coin.coin_table` (seed 20261102) each offered (date, mark) takes its side from one of fifteen declared rules
computed only from one-minute NQ bars that have CLOSED at or before the mark; the entry stays at the open of the first
bar after the mark.

**The clock** is `collect_core`'s (`atlas_local.day_arrays`): index j of a day's arrays is a one-minute bar's END time in
minutes after 17:00 CT (1 .. 1330, the bar ending 15:10 CT the last); a mark t (minutes after 17:00 CT,
`resolved_coin.marks`) sees exactly the bars j <= t. ``c[x]`` is the close of the last bar ending at or before minute x
(D-578's definition of c[t], applied at every x); a minute before the session's first bar has no c: the rule is a tie.

**The rules** (`RULES`; side = sign of the quantity, zero or undefined = a tie, 0):

    mom<k>  c[t] - c[t-k], k = 1, 2, 3, 5, 10, 15, 30, 60, 120 (minutes on the clock)
    glbx    c[t] - the open of the session's first bar (the 17:00 CT bar; the first bar present)
    pday    the prior session's last close - its first open (the bar store's previous trading day, all its bars; one
            side all day; no prior session in the window: a tie)
    rng<N>  c[t] - the midpoint of the high and low of the last N bars ending at or before t (fewer than N: a tie)
    lbrk<k> the side of the most recent k-minute `brk` event (`atlas_core.a_events`, the whole day's clock) at a slot at
            or before t (none yet today: a tie)

**Stage 1 -- the lift** (exact; D-550's arithmetic, `a4_coin_atlas.lift`): at every offered mark of P-16's cell and every
offered R, lift = (the rule side's net R - the other side's net R) / 2 -- the gain over the coin twin, whose expected
net R is the two sides' mean. A tie is excluded (counted). Fade = minus follow exactly, so follow and fade are one
two-sided test; a survivor's side sign is its mean lift's sign. 15 rules x 6 R = 90 hypotheses; the studentised
max-statistic over a stationary block bootstrap of sessions (`a4_coin_atlas.stationary_counts` / `maxstat_test`; block
21, 2,000 replicates, seed 20261105) family-wise at 0.025 (S1's alpha_k); Benjamini-Hochberg at 10 % beside, never
selecting.

**Stage 2 -- the campaign** (survivors only): the cell's coins replaced by the rule's sides (`campaign_coins`; a tie takes
the coin sequence's own side) through P-16's engine call, then D-578's four guards (`verdict`).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from propedge.research import a4_coin_atlas as A4

DECISION = "D-578"
BATCH = "S1"
FAMILY_ID = f"{DECISION}:{BATCH}"
ALPHA = 0.025                              # alpha_1 = 0.05 / (1 x 2)
BH_Q = 0.10
BOOT_REPS = 2000
BOOT_BLOCK = 21.0
BOOT_SEED = 20261105                       # D-578 (3)
STOP_TICKS = 150
OFFERED_R = (0.25, 1.0, 1.5, 2.0, 2.5, 3.0)
CAMPAIGN_SEED = 20261131
N_PATHS = 500
COIN_SEEDS = tuple(20261600 + i for i in range(50))     # D-578 (2), D-568 (2)
G2_PATHS = 200
G2_WINS = 40
MARGIN = 0.05
SPANS = {"early": ("2020-01-01", "2023-12-31"), "late": ("2024-01-01", "2026-07-16")}
N_VARIANTS = 15
N_HYPOTHESES = 90
MOM_LAGS = (1, 2, 3, 5, 10, 15, 30, 60, 120)
RNG_BARS = (15, 60)
BRK_K = (5, 15)

#: the fifteen rules in the declaration's order: (name, kind, parameter)
RULES: tuple[tuple[str, str, int], ...] = (
    tuple((f"mom{k}", "mom", k) for k in MOM_LAGS)
    + (("glbx", "glbx", 0), ("pday", "pday", 0))
    + tuple((f"rng{n}", "rng", n) for n in RNG_BARS)
    + tuple((f"lbrk{k}", "lbrk", k) for k in BRK_K))
RULE_NAMES = tuple(r[0] for r in RULES)
DEFINITIONS = {**{f"mom{k}": f"c[t] - c[t-{k}]" for k in MOM_LAGS},
               "glbx": "c[t] - open of the session's first bar (17:00 CT)",
               "pday": "prior session's last close - prior session's first open (one side all day)",
               **{f"rng{n}": f"c[t] - midpoint of the last {n} bars' high and low" for n in RNG_BARS},
               **{f"lbrk{k}": f"side of the most recent {k}-min brk event (atlas_core.a_events) at or before t"
                  for k in BRK_K}}


# ------------------------------------------------------------------------------------------------ the declaration


#: the declaration file as D-578 fixed it (sha256 of its text with LF line ends). The file is not valid YAML as written
#: (`none yet today: tie` on the lbrk lines, `|c[t] ...` in S2), so it is read as text: its hash pinned, S1's block
#: located and every constant below checked against its words.
DECLARATION_SHA256 = "5e9342a1ee2fcf2e2eec714967912531725fa90c33756b9a373cf4ce1dcc02d0"
DECLARATION_FILE = Path(__file__).resolve().parents[2] / "config" / "search_program.yaml"


def declaration(path: Path | str | None = None) -> dict[str, Any]:
    """`config/search_program.yaml` as text: its sha256 (LF line ends), the program block, S1's block and S1's rule
    names in their order."""
    import hashlib
    import re

    p = Path(path) if path is not None else DECLARATION_FILE
    text = p.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    prog = text.split("\nbatches:", 1)[0]
    m = re.search(r"\n  - id: S1\n(.*?)(?=\n  - id: |\nproposed_not_declared:|\Z)", text, flags=re.S)
    block = m.group(1) if m else ""
    r = re.search(r"\n    rules:[^\n]*\n((?:      [^\n]*\n)+)", block + "\n")
    names = re.findall(r"^      (\w+):", r.group(1), flags=re.M) if r else []
    return {"path": str(p), "sha256": sha, "program": prog, "batch": block, "rules": names}


def declaration_problems(decl: Mapping[str, Any]) -> list[str]:
    """Every way this module's constants differ from the declaration (an empty list: they agree)."""
    out = []
    if str(decl["sha256"]) != DECLARATION_SHA256:
        out.append(f"the declaration's sha256 is {str(decl['sha256'])[:16]}, not D-578's {DECLARATION_SHA256[:16]}")
    b, prog = str(decl["batch"]), str(decl["program"])
    if not b:
        out.append("no S1 batch in the declaration")
    if f"decision: {DECISION}" not in prog:
        out.append(f"the program is not {DECISION}'s")
    if tuple(decl["rules"]) != RULE_NAMES:
        out.append(f"rules {list(decl['rules'])}, not {list(RULE_NAMES)}")
    if len(RULE_NAMES) * len(OFFERED_R) != N_HYPOTHESES:
        out.append("15 rules x 6 R is not the declared 90 hypotheses")
    for want in ("status: declared", f"alpha: {ALPHA:g}", f"stop_ticks: {STOP_TICKS}", f"variants: {N_VARIANTS}",
                 f"hypotheses: {N_HYPOTHESES}", "(0.25, 1, 1.5, 2, 2.5, 3)", "block 21", "2,000 reps",
                 f"seed {BOOT_SEED}", f"family-wise at {ALPHA:g}", "Benjamini-Hochberg at 10 %",
                 f"campaign seed {CAMPAIGN_SEED}", f"{N_PATHS} paths", "fade = minus follow"):
        if want not in b:
            out.append(f"S1's block does not say {want!r}")
    for want in ("by more than 0.05", "at least 40 of 50", "20261600 + i, 200 paths", "2020-2023, 2024-2026-07-16",
                 "resolves every offered R"):
        if want not in prog:
            out.append(f"the campaign guards do not say {want!r}")
    return out


# ------------------------------------------------------------------------------------------------ the rules


def _f(a: Sequence) -> np.ndarray:
    return np.array([np.nan if x is None else float(x) for x in a], dtype=float)


def _lists(a: np.ndarray) -> list:
    return [None if not np.isfinite(x) else float(x) for x in a]


def last_index(c: np.ndarray) -> np.ndarray:
    """li[x] = the largest j <= x (j >= 1) with a bar, else -1, for every x of the clock (0 .. len(c) - 1)."""
    have = np.isfinite(np.asarray(c, float))
    have[0] = False                                  # index 0 is never a bar (the clock starts at the 17:01 end)
    idx = np.where(have, np.arange(len(have)), -1)
    return np.maximum.accumulate(idx)


def _sign(x: np.ndarray) -> np.ndarray:
    s = np.sign(np.asarray(x, float))
    return np.where(np.isfinite(s), s, 0.0).astype(np.int8)


def brk_events(o: Sequence, h: Sequence, l: Sequence, c: Sequence, k: int) -> tuple[np.ndarray, np.ndarray]:
    """The day's k-minute `brk` events (`atlas_core.a_events`, the whole clock): (slots ascending, side per slot -- the
    sign of the sides' sum at that slot, so two opposite events at one slot are a tie)."""
    from propedge.outcomes import atlas_core

    n = len(o) - 1
    ev = atlas_core.a_events(list(o), list(h), list(l), list(c),
                             {"patterns": [{"kind": "brk", "k": int(k)}], "first_slot": 0, "last_slot": n,
                              "prior": None})
    by: dict[int, int] = {}
    for _pid, j, d in ev:
        by[int(j)] = by.get(int(j), 0) + int(d)
    slots = np.array(sorted(by), dtype=np.int64)
    return slots, np.array([int(np.sign(by[int(s)])) for s in slots], dtype=np.int8)


def day_sides(o: Sequence, h: Sequence, l: Sequence, c: Sequence, marks: Sequence[int], *,
              prior_sign: int = 0, rules: Sequence[tuple[str, str, int]] = RULES) -> dict[str, np.ndarray]:
    """{rule: side at each mark (+1, -1, 0 a tie)} on one day's arrays (the clock's; a missing bar None or NaN). Every
    value at mark t reads only bars j <= t (and, for pday, `prior_sign`, the prior session's)."""
    O, H, Lo, C = _f(o), _f(h), _f(l), _f(c)
    n = len(C) - 1
    M = np.asarray([int(m) for m in marks], dtype=np.int64)
    if len(M) and (M.min() < 0 or M.max() > n):
        raise ValueError(f"marks must lie on the day's clock 0 .. {n}")
    li = last_index(C)
    i1 = li[M] if len(M) else np.array([], dtype=np.int64)
    c1 = np.where(i1 >= 0, C[np.maximum(i1, 0)], np.nan)
    present = np.where(np.isfinite(C) & (np.arange(len(C)) >= 1))[0]
    out: dict[str, np.ndarray] = {}
    lists = None
    for name, kind, p in rules:
        if kind == "mom":
            x = M - int(p)
            i0 = np.where(x >= 0, li[np.maximum(x, 0)], -1)
            c0 = np.where(i0 >= 0, C[np.maximum(i0, 0)], np.nan)
            out[name] = _sign(c1 - c0)
        elif kind == "glbx":
            first_open = O[present[0]] if len(present) else np.nan
            out[name] = _sign(c1 - first_open)
        elif kind == "pday":
            out[name] = np.full(len(M), int(np.sign(int(prior_sign))), dtype=np.int8)
        elif kind == "rng":
            N = int(p)
            pos = np.searchsorted(present, M, side="right")         # bars ending at or before each mark
            hv = pd.Series(H[present]).rolling(N).max().to_numpy() if len(present) else np.array([])
            lv = pd.Series(Lo[present]).rolling(N).min().to_numpy() if len(present) else np.array([])
            ok = pos >= N
            j = np.maximum(pos - 1, 0)
            mid = np.where(ok, (hv[j] + lv[j]) / 2.0 if len(present) else np.nan, np.nan)
            out[name] = _sign(c1 - mid)
        elif kind == "lbrk":
            if lists is None:
                lists = (_lists(O), _lists(H), _lists(Lo), _lists(C))
            slots, sides = brk_events(*lists, int(p))
            j = np.searchsorted(slots, M, side="right") - 1
            out[name] = np.where(j >= 0, sides[np.maximum(j, 0)] if len(slots) else 0, 0).astype(np.int8)
        else:
            raise ValueError(f"unknown rule kind {kind!r}")
    return out


def session_signs(bars: pd.DataFrame) -> dict[str, int]:
    """{trading day: the sign of the PRIOR session's last close - first open} from the bar store's rows (`day`, `ts`,
    `open`, `close`): the prior session is the store's previous trading day with bars, all its bars in time order; the
    first day has none (0)."""
    if bars.empty:
        return {}
    b = bars.sort_values(["day", "ts"], kind="stable")
    g = b.groupby("day", sort=True)
    own = np.sign(g["close"].last().astype(float) - g["open"].first().astype(float)).astype(int)
    days = list(own.index.astype(str))
    vals = own.to_numpy()
    return {d: (int(vals[i - 1]) if i > 0 else 0) for i, d in enumerate(days)}


# ------------------------------------------------------------------------------------------------ stage 1


def lift_matrix(r_long: np.ndarray, r_short: np.ndarray, sides: np.ndarray) -> np.ndarray:
    """(offers, rules x R) lift, rule-major and R-minor (`a4_coin_atlas.hypothesis_frame`'s order): at each offer and
    R, (the rule side's net R - the other's) / 2 by `a4_coin_atlas.lift`; NaN where the rule ties (side 0)."""
    rl, rs = np.asarray(r_long, float), np.asarray(r_short, float)
    S = np.asarray(sides)
    if rl.shape != rs.shape or rl.ndim != 2 or S.ndim != 2 or S.shape[0] != rl.shape[0]:
        raise ValueError("r_long and r_short are (offers, R); sides is (offers, rules)")
    n, nR = rl.shape
    out = np.full((n, S.shape[1] * nR), np.nan)
    for q in range(S.shape[1]):
        s = S[:, q].astype(int)[:, None]
        lf = np.where(s > 0, A4.lift(rl, rs), A4.lift(rs, rl))
        out[:, q * nR:(q + 1) * nR] = np.where(s != 0, lf, np.nan)
    return out


def accumulate(day_index: np.ndarray, lift: np.ndarray, n_days: int) -> tuple[np.ndarray, np.ndarray]:
    """(day_sum, day_n), each (n_days, H): each session's summed lift and its counted (finite) offers per hypothesis."""
    di = np.asarray(day_index, dtype=np.int64)
    L = np.asarray(lift, float)
    ok = np.isfinite(L)
    day_sum = np.zeros((int(n_days), L.shape[1]))
    day_n = np.zeros((int(n_days), L.shape[1]))
    np.add.at(day_sum, di, np.where(ok, L, 0.0))
    np.add.at(day_n, di, ok.astype(float))
    return day_sum, day_n


def stage1(day_sum: np.ndarray, day_n: np.ndarray, *, reps: int = BOOT_REPS, block: float = BOOT_BLOCK,
           seed: int = BOOT_SEED, alpha: float = ALPHA, bh_q: float = BH_Q) -> dict[str, Any]:
    """D-578 (3)'s test: the stationary block bootstrap of sessions and the studentised max-statistic family-wise at
    `alpha` (`a4_coin_atlas`), with BH at `bh_q` on each hypothesis's own bootstrap p beside."""
    counts = A4.stationary_counts(day_sum.shape[0], reps=int(reps), mean_block=float(block), seed=int(seed))
    test = A4.maxstat_test(day_sum, day_n, counts, fwer=float(alpha))
    test["bh"] = A4.benjamini_hochberg(test["p"], float(bh_q))
    return test


def hypotheses() -> pd.DataFrame:
    """One row per (rule, R) in the accumulators' column order."""
    return A4.hypothesis_frame([{"rule": n, "rule_index": i, "definition": DEFINITIONS[n]}
                                for i, n in enumerate(RULE_NAMES)], OFFERED_R)


def survivors(hyp: pd.DataFrame) -> list[tuple[str, int]]:
    """The distinct (rule, side sign) of the surviving hypotheses in menu order (sign = the mean lift's: +1 follow, -1
    fade)."""
    s = hyp[hyp["survives"].astype(bool)]
    out: list[tuple[str, int]] = []
    for _, r in s.iterrows():
        k = (str(r["rule"]), 1 if float(r["mean_lift"]) > 0 else -1)
        if k not in out:
            out.append(k)
    order = {n: i for i, n in enumerate(RULE_NAMES)}
    return sorted(out, key=lambda k: (order[k[0]], -k[1]))


def arm_name(rule: str, sign: int) -> str:
    return f"{rule}_{'follow' if int(sign) > 0 else 'fade'}"


# ------------------------------------------------------------------------------------------------ stage 2


def campaign_coins(base: Mapping[tuple[str, int], int], keys: Sequence[tuple[str, int]], sides: Sequence[int],
                   sign: int = 1) -> dict[tuple[str, int], int]:
    """The coin table a rule's campaign cell is built with: `base` (a coin sequence: every (date, mark) of the grid),
    with each of `keys` replaced by sign x the rule's side there -- a tie (0) keeps the base coin's side."""
    if int(sign) not in (1, -1):
        raise ValueError("sign is +1 (follow) or -1 (fade)")
    if len(keys) != len(sides):
        raise ValueError("one side per key")
    out = dict(base)
    for k, s in zip(keys, sides):
        if int(s) != 0:
            kk = (str(k[0]), int(k[1]))
            if kk not in out:
                raise KeyError(f"{kk} is not on the coin's grid")
            out[kk] = int(sign) * int(np.sign(int(s)))
    return out


def g2_summary(rows: Sequence[Mapping[str, Any]], arms: Sequence[str], reference: str,
               wins_needed: int = G2_WINS) -> list[dict[str, Any]]:
    """Per arm: on how many coin sequences it grows more at the bound than the reference on the same sequence, and
    whether that reaches `wins_needed` (rows hold coin_seed, arm, growth_on_required)."""
    by: dict[int, dict[str, float]] = {}
    for r in rows:
        by.setdefault(int(r["coin_seed"]), {})[str(r["arm"])] = float(r["growth_on_required"])
    out = []
    for a in arms:
        diffs = [v[a] - v[reference] for v in by.values() if a in v and reference in v]
        wins = int(sum(d > 0 for d in diffs))
        out.append({"section": "g2_summary", "arm": a, "coins": len(diffs), "wins": wins,
                    "mean_difference": float(np.mean(diffs)) if diffs else float("nan"),
                    "wins_needed": int(wins_needed), "passes_g2": bool(len(diffs) and wins >= wins_needed)})
    return out


def verdict(arm: str, g1_growth: float, ref_growth: float, resolves: bool, g2_row: Mapping[str, Any] | None,
            span_growth: Mapping[str, float], span_ref: Mapping[str, float]) -> dict[str, Any]:
    """D-578 (2)'s four guards for one arm: (a) paired growth at the bound above the reference's by more than MARGIN;
    (b) every offered R resolves; (c) at least G2_WINS of the coin sequences won; (d) not below the reference on either
    span alone."""
    diff = float(g1_growth) - float(ref_growth)
    spans_ok = all(np.isfinite(span_growth.get(s, np.nan)) and np.isfinite(span_ref.get(s, np.nan))
                   and float(span_growth[s]) >= float(span_ref[s]) for s in SPANS)
    checks = {"a_paired_beats_by_margin": bool(np.isfinite(diff) and diff > MARGIN),
              "b_every_offered_r_resolves": bool(resolves),
              "c_wins_coin_sequences": bool(g2_row is not None and g2_row.get("passes_g2", False)),
              "d_not_below_on_either_span": bool(spans_ok)}
    return {"section": "verdict", "arm": arm, "growth_minus_reference": diff,
            **{f"{s}_growth_minus_reference": float(span_growth.get(s, np.nan)) - float(span_ref.get(s, np.nan))
               for s in SPANS}, **checks, "candidate": bool(all(checks.values()))}


__all__ = ["DECISION", "BATCH", "FAMILY_ID", "ALPHA", "BH_Q", "BOOT_REPS", "BOOT_BLOCK", "BOOT_SEED", "STOP_TICKS",
           "OFFERED_R", "CAMPAIGN_SEED", "N_PATHS", "COIN_SEEDS", "G2_PATHS", "G2_WINS", "MARGIN", "SPANS",
           "N_VARIANTS", "N_HYPOTHESES", "RULES", "RULE_NAMES", "DEFINITIONS", "declaration", "declaration_problems",
           "last_index", "brk_events", "day_sides", "session_signs", "lift_matrix", "accumulate", "stage1",
           "hypotheses", "survivors", "arm_name", "campaign_coins", "g2_summary", "verdict"]
