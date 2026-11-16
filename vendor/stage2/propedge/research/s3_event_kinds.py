"""EXPLORATORY (D-578, D-586): batch S3 of the rolling model search -- the sided coin on new event kinds. Pure functions;
`scripts/s3_event_kinds.py` reads the bars, builds P-16's cell and writes the result.

**What S3 is** (`config/search_program_s3.yaml`, fixed by D-586 before this code was built): S1's design exactly
(`propedge.research.s1_sided_coin`, D-579's readings) -- P-16 (`rc_s150_all_nr`, the 150-tick news-safe all-day coin
re-entering when flat, an offer every five minutes, P-14's money side, five Topstep seats) with only the side of each
offer changed: each offered (date, mark) takes its side from one of thirteen declared rules on one-minute NQ bars that
have CLOSED at or before the mark (and, for the gaps, the previous trading day). The entry stays at the open of the
first bar after the mark. Only the rules, alpha (0.05 / 12), the bootstrap seed (20261109), the counts (13 variants, 78
hypotheses), the family id (`D-578:S3`), the declaration file and the output file differ from S1; the lift, the
accumulators, the bootstrap, the coins of the campaign, G2's summary and the verdict are S1's functions, imported.

**The clock** is `collect_core`'s (`atlas_local.day_arrays`): index j of a day's arrays is a one-minute bar's END time in
minutes after 17:00 CT (1 .. 1330, the bar ending 15:10 CT the last); a mark t (`resolved_coin.marks`, 0 .. 1325 every
five minutes) sees exactly the bars j <= t. `collect_core.c_slot(h, m)` = h x 60 + m - 1020 after 17:00, else + 420:
**08:30 CT is minute 930** (8 x 60 + 30 + 420; `RTH_OPEN_SLOT`) and **16:00 CT is minute 1380** (`CLOSE_SLOT`, past the
arrays' 15:10 end, so the gap's close is read from the bar store's rows, not the arrays).

**The rules** (`RULES`; side +1 / -1, 0 = a tie: "none yet today", undefined or zero):

    lbrk1/2/3   the side of the most recent k-minute `brk` event, k = 1, 2, 3 (`atlas_core.a_events` over the whole
                day's clock, slots 0 .. 1330) at a slot at or before t; opposite events at one slot tie (S1's
                `brk_events`)
    lnbarKxN    the same for `{"kind": "nbar", "k": K, "n": N}`, K = 1, 3 and N = 4, 8
    gap_glbx    sign(the open of the session's first bar present in the arrays - the previous trading day's last close
                at or before 16:00 CT); one side all day from that bar's end on -- a mark before the first bar has
                closed (mark 0 always) ties, since no bar has closed (the program's rule); no previous trading day in
                the store (its first day, 2020-01-02, the first development day) ties all day
    gap_rth     sign(the open of the first bar present ending after 08:30 CT, i.e. at a slot > 930 (normally the bar
                08:30-08:31, slot 931) - the same close); marks before that bar's end (slot) tie, the mark at its end
                sees it; no such bar, or no previous close, ties all day
    lout5/15    the body sign (close - open) of the most recent completed k-minute bar (`atlas_core.a_bars`, clock
                aligned, a bar's slot its end, a bar with no minute left out) that is an outside bar: its high STRICTLY
                above and its low STRICTLY below the previous bar in a_bars' list (the previous bar present that day);
                the day's first bar is never one; the most recent such bar decides -- a zero body ties (no fall-back
                to an earlier outside bar)
    lrx5/15     the same for a range-expansion bar: its high - low at least twice the mean high - low of the 10 bars
                immediately before it in a_bars' list (the same trading day); fewer than 10 before it -> not a
                candidate bar

**The previous trading day's last close** (`prior_closes`): the bar store's previous trading day (the store's day
list, as S1's `session_signs` reads it) and, of its rows (Databento stamps a bar at its START, `ts`; the bar ends at
`ts` + 60 s), the one with the latest `ts` whose END lies at or before 16:00 CT on that trading day's clock -- end slot
1 .. 1380 (17:01 CT the evening before through 16:00 CT); a bar ending after 16:00 CT (the store's quarter-end bars to
17:00 CT) is never read. That close is the store's charted contract's: on a roll day the previous day's close is the
old contract's, so the gap carries the roll spread -- counted beside (`roll`), never changed.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from propedge.outcomes import atlas_core
from propedge.outcomes.collect_core import c_slot
from propedge.research import a4_coin_atlas as A4
from propedge.research import s1_sided_coin as S1

DECISION = "D-578"
DECLARED_BY = "D-586"
BATCH = "S3"
FAMILY_ID = f"{DECISION}:{BATCH}"
ALPHA = 0.05 / 12                          # alpha_3 = 0.05 / (3 x 4)
BH_Q = 0.10
BOOT_REPS = 2000
BOOT_BLOCK = 21.0
BOOT_SEED = 20261109                       # D-586
STOP_TICKS = 150
OFFERED_R = S1.OFFERED_R                   # (0.25, 1, 1.5, 2, 2.5, 3)
CAMPAIGN_SEED = 20261131
N_PATHS = 500
COIN_SEEDS = tuple(20261600 + i for i in range(50))     # D-578 (2), D-568 (2)
G2_PATHS = 200
G2_WINS = 40
MARGIN = 0.05
SPANS = dict(S1.SPANS)
N_VARIANTS = 13
N_HYPOTHESES = 78

RTH_OPEN_SLOT = c_slot(8, 30)              # 930: 08:30 CT on the trading-day clock
CLOSE_SLOT = c_slot(16, 0)                 # 1380: 16:00 CT
RX_PRIOR = 10                              # range expansion: the mean of the 10 bars before
RX_MULT = 2.0

#: the thirteen rules in the declaration's order: (name, kind, parameters)
RULES: tuple[tuple[str, str, dict], ...] = (
    tuple((f"lbrk{k}", "event", {"kind": "brk", "k": k}) for k in (1, 2, 3))
    + tuple((f"lnbar{k}x{n}", "event", {"kind": "nbar", "k": k, "n": n}) for k in (1, 3) for n in (4, 8))
    + (("gap_glbx", "gap_glbx", {}), ("gap_rth", "gap_rth", {}))
    + tuple((f"lout{k}", "outside", {"k": k}) for k in (5, 15))
    + tuple((f"lrx{k}", "rx", {"k": k}) for k in (5, 15)))
RULE_NAMES = tuple(r[0] for r in RULES)
DEFINITIONS = {
    **{f"lbrk{k}": f"side of the most recent {k}-min brk event (atlas_core.a_events, the whole day's clock) at or "
                   "before t" for k in (1, 2, 3)},
    **{f"lnbar{k}x{n}": f"side of the most recent nbar event, k = {k}, n = {n} (atlas_core.a_events) at or before t"
       for k in (1, 3) for n in (4, 8)},
    "gap_glbx": "sign(open of the session's first bar - the previous trading day's last close at or before 16:00 CT); "
                "one side all day once that bar has closed",
    "gap_rth": "sign(open of the first bar ending after 08:30 CT - the previous trading day's last close at or before "
               "16:00 CT); marks before that bar's end tie",
    **{f"lout{k}": f"body sign of the most recent completed {k}-min outside bar (high above and low below the previous "
                   f"{k}-min bar's, strictly) at or before t" for k in (5, 15)},
    **{f"lrx{k}": f"body sign of the most recent completed {k}-min bar whose range is at least twice the mean range of "
                  f"the 10 same-day {k}-min bars before it, at or before t" for k in (5, 15)}}

# re-used from S1 unchanged (D-586: S1's design exactly)
lift_matrix = S1.lift_matrix
accumulate = S1.accumulate
campaign_coins = S1.campaign_coins
arm_name = S1.arm_name
last_index = S1.last_index
_sign = S1._sign


# ------------------------------------------------------------------------------------------------ the declaration


#: `config/search_program_s3.yaml` as D-586 committed it (bbabe1f): the sha256 of its text with LF line ends (Git may
#: check it out with CRLF, `text=auto`; the hash is the repository's bytes either way -- D-579's handling)
DECLARATION_SHA256 = "24a0b239e9ca3c2aede9311650e5d12460b38c8a592f2dec9aac45fdcba594b7"
DECLARATION_FILE = Path(__file__).resolve().parents[2] / "config" / "search_program_s3.yaml"

#: phrases of the batch's own words each constant rests on (line breaks folded to spaces)
S3_WORDS = ("id: S3", "decision: D-586", "program: D-578", "name: sided coin, new event kinds",
            f"stop_ticks: {STOP_TICKS}", f"stop (150 ticks)", "Follow and fade are one two-sided test (fade = minus "
            "follow)", "A tie (rule undefined or zero) is excluded from the lift and takes P-16's own coin side in the "
            "campaign (G1) and that sequence's coin in G2", "at every offered R (0.25, 1, 1.5, 2, 2.5, 3)",
            f"hypotheses: {N_HYPOTHESES}", "13 rules x 6 R", "block 21, 2,000 reps, seed 20261109",
            "Benjamini-Hochberg at 10 % beside, never selecting", "campaign seed 20261131, 500 paths",
            "paired +0.05 at the bound", "every offered R resolves", "at least 40 of 50 coin sequences",
            "seeds 20261600 + i, 200 paths", "not below P-16 on either span alone",
            "with_no_survivor: stage 1 and the reference's paired row only", f"variants: {N_VARIANTS}",
            "results/s3_event_kinds.csv", "D-578:S3", "0.05 / (3 * 4)")
#: the words of each rule the code computes (the rule's own line in the declaration)
RULE_WORDS = {
    "lbrk1": ("most recent 1-min brk event", "atlas_core.a_events, the whole day's clock", "at or before t"),
    "lbrk2": ("most recent 2-min brk event", "at or before t"),
    "lbrk3": ("most recent 3-min brk event", "at or before t"),
    "lnbar1x4": ("most recent nbar event, k = 1, n = 4", "at or before t"),
    "lnbar1x8": ("most recent nbar event, k = 1, n = 8", "at or before t"),
    "lnbar3x4": ("most recent nbar event, k = 3, n = 4", "at or before t"),
    "lnbar3x8": ("most recent nbar event, k = 3, n = 8", "at or before t"),
    "gap_glbx": ("open of the session's first bar", "previous trading day's last close at or before 16:00 CT",
                 "one side all day", "the first development day ties"),
    "gap_rth": ("open of the first bar ending after 08:30 CT", "previous trading day's last close at or before 16:00 CT",
                "marks before that bar's end tie"),
    "lout5": ("most recent completed 5-min bar", "clock-aligned, atlas_core.a_bars", "high is above and low below the "
              "previous 5-min bar's", "an outside bar", "at or before t", "a zero body ties"),
    "lout15": ("the same on 15-min bars",),
    "lrx5": ("most recent completed 5-min bar", "high-low range is at least twice the mean range of the 10 completed "
             "5-min bars before it in the same trading day", "fewer than 10 prior bars -> not a candidate bar",
             "a zero body ties"),
    "lrx15": ("the same on 15-min bars",)}


def _fold(s: Any) -> str:
    return re.sub(r"\s+", " ", str(s))


def declaration(path: Path | str | None = None) -> dict[str, Any]:
    """`config/search_program_s3.yaml`: its sha256 (LF line ends), the parsed YAML (the file is valid YAML) and its text,
    with the program file's pin (`s1_sided_coin.declaration`) beside: the program's guards are D-578's, unchanged."""
    import yaml

    p = Path(path) if path is not None else DECLARATION_FILE
    text = p.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")
    data = yaml.safe_load(text) or {}
    batch = data.get("batch") or {}
    rules = batch.get("rules") or {}
    prog = S1.declaration()
    return {"path": str(p), "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(), "text": text,
            "batch": batch, "rules": list(rules), "rule_text": {str(k): str(v) for k, v in rules.items()},
            "program_sha256": prog["sha256"], "program": prog["program"]}


def declaration_problems(decl: Mapping[str, Any]) -> list[str]:
    """Every way this module's constants differ from the declaration (an empty list: they agree)."""
    out = []
    if str(decl["sha256"]) != DECLARATION_SHA256:
        out.append(f"the declaration's sha256 is {str(decl['sha256'])[:16]}, not D-586's {DECLARATION_SHA256[:16]}")
    if str(decl["program_sha256"]) != S1.DECLARATION_SHA256:
        out.append("the program file (config/search_program.yaml) is not D-578's pinned text")
    if f"decision: {DECISION}" not in str(decl["program"]):
        out.append(f"the program is not {DECISION}'s")
    b = decl["batch"]
    if not b:
        out.append("no S3 batch in the declaration")
    text = _fold(decl["text"])
    try:
        alpha = float(b.get("alpha"))
    except (TypeError, ValueError):
        alpha = float("nan")
    if not abs(alpha - ALPHA) < 5e-11:
        out.append(f"alpha {b.get('alpha')!r} is not 0.05 / 12")
    for key, want in (("id", BATCH), ("decision", DECLARED_BY), ("program", DECISION), ("stop_ticks", STOP_TICKS),
                      ("variants", N_VARIANTS)):
        if b.get(key) != want:
            out.append(f"{key}: {b.get(key)!r}, not {want!r}")
    if (b.get("stage_1") or {}).get("hypotheses") != N_HYPOTHESES:
        out.append(f"stage_1 hypotheses are not {N_HYPOTHESES}")
    if tuple(decl["rules"]) != RULE_NAMES:
        out.append(f"rules {list(decl['rules'])}, not {list(RULE_NAMES)}")
    if len(RULE_NAMES) * len(OFFERED_R) != N_HYPOTHESES or len(RULE_NAMES) != N_VARIANTS:
        out.append("13 rules x 6 R is not the declared 78 hypotheses and 13 variants")
    out += [f"S3's declaration does not say {w!r}" for w in S3_WORDS if w not in text]
    rt = decl["rule_text"]
    for name, words in RULE_WORDS.items():
        for w in words:
            if w not in _fold(rt.get(name, "")):
                out.append(f"rule {name} does not say {w!r}")
    if tuple(OFFERED_R) != tuple(A4.OFFERED_R):
        out.append("the offered R are not A4's / the table's")
    return out


# ------------------------------------------------------------------------------------------------ the rules


def _lists(a: np.ndarray) -> list:
    return [None if not np.isfinite(x) else float(x) for x in a]


def event_sides(o: Sequence, h: Sequence, l: Sequence, c: Sequence, pattern: Mapping[str, Any]
                ) -> tuple[np.ndarray, np.ndarray]:
    """The day's events of one `atlas_core.a_events` pattern over the whole clock (slots 0 .. n): (slots ascending, the
    sign of the sides' sum at each slot -- opposite events at one slot tie). S1's `brk_events` for any pattern."""
    n = len(o) - 1
    ev = atlas_core.a_events(list(o), list(h), list(l), list(c),
                             {"patterns": [dict(pattern)], "first_slot": 0, "last_slot": n, "prior": None})
    by: dict[int, int] = {}
    for _pid, j, d in ev:
        by[int(j)] = by.get(int(j), 0) + int(d)
    slots = np.array(sorted(by), dtype=np.int64)
    return slots, np.array([int(np.sign(by[int(s)])) for s in slots], dtype=np.int8)


def bar_candidates(o: Sequence, h: Sequence, l: Sequence, c: Sequence, k: int, kind: str
                   ) -> tuple[np.ndarray, np.ndarray]:
    """The day's k-minute candidate bars (`atlas_core.a_bars` over the whole clock; a bar's slot its end): (slots
    ascending, body sign close - open, 0 for a zero body). `kind` "outside": high > the previous listed bar's high and
    low < its low (strict); "rx": high - low >= 2 x the mean high - low of the 10 listed bars before it (fewer than 10:
    not a candidate)."""
    n = len(o) - 1
    bars = atlas_core.a_bars(list(o), list(h), list(l), list(c), int(k), n)
    slots, sides = [], []
    for i, (s, bo, bh, bl, bc) in enumerate(bars):
        if kind == "outside":
            if i == 0:
                continue
            cand = bh > bars[i - 1][2] and bl < bars[i - 1][3]
        elif kind == "rx":
            if i < RX_PRIOR:
                continue
            mean = sum(x[2] - x[3] for x in bars[i - RX_PRIOR:i]) / RX_PRIOR
            cand = (bh - bl) >= RX_MULT * mean
        else:
            raise ValueError(f"unknown bar kind {kind!r}")
        if cand:
            slots.append(int(s))
            sides.append(int(np.sign(bc - bo)))
    return np.array(slots, dtype=np.int64), np.array(sides, dtype=np.int8)


def _latest(slots: np.ndarray, sides: np.ndarray, M: np.ndarray) -> np.ndarray:
    """At each mark, the side at the most recent slot at or before it (none yet: 0)."""
    if not len(slots):
        return np.zeros(len(M), dtype=np.int8)
    j = np.searchsorted(slots, M, side="right") - 1
    return np.where(j >= 0, sides[np.maximum(j, 0)], 0).astype(np.int8)


def day_sides(o: Sequence, h: Sequence, l: Sequence, c: Sequence, marks: Sequence[int], *,
              prev_close: float | None = None, rules: Sequence[tuple[str, str, dict]] = RULES
              ) -> dict[str, np.ndarray]:
    """{rule: side at each mark (+1, -1, 0 a tie)} on one day's arrays (the clock's; a missing bar None or NaN). Every
    value at mark t reads only bars j <= t and, for the gaps, `prev_close` (the previous trading day's last close at or
    before 16:00 CT, `prior_closes`; None or NaN: the gaps tie all day)."""
    O, H, Lo, C = S1._f(o), S1._f(h), S1._f(l), S1._f(c)
    n = len(C) - 1
    M = np.asarray([int(m) for m in marks], dtype=np.int64)
    if len(M) and (M.min() < 0 or M.max() > n):
        raise ValueError(f"marks must lie on the day's clock 0 .. {n}")
    present = np.where(np.isfinite(O) & np.isfinite(C) & (np.arange(len(C)) >= 1))[0]
    pc = float("nan") if prev_close is None else float(prev_close)
    lists = None
    out: dict[str, np.ndarray] = {}
    for name, kind, p in rules:
        if kind in ("event", "outside", "rx") and lists is None:
            lists = (_lists(O), _lists(H), _lists(Lo), _lists(C))
        if kind == "event":
            out[name] = _latest(*event_sides(*lists, p), M)
        elif kind in ("outside", "rx"):
            out[name] = _latest(*bar_candidates(*lists, int(p["k"]), kind), M)
        elif kind in ("gap_glbx", "gap_rth"):
            pick = present if kind == "gap_glbx" else present[present > RTH_OPEN_SLOT]
            if not len(pick) or not np.isfinite(pc):
                out[name] = np.zeros(len(M), dtype=np.int8)
                continue
            j = int(pick[0])
            side = int(np.sign(O[j] - pc))
            out[name] = np.where(M >= j, side, 0).astype(np.int8)
        else:
            raise ValueError(f"unknown rule kind {kind!r}")
    return out


def bar_end_slots(ts: Sequence[int]) -> np.ndarray:
    """Each store bar's END on the trading-day clock (`collect_core.c_slot` of `ts` + 60 s in Chicago time)."""
    end = pd.to_datetime(pd.Series(np.asarray(ts, dtype="int64")) + 60, unit="s", utc=True).dt.tz_convert(
        "America/Chicago")
    m = (end.dt.hour * 60 + end.dt.minute).to_numpy()
    return np.where(m > 1020, m - 1020, m + 420)


def prior_closes(bars: pd.DataFrame) -> dict[str, dict[str, Any]]:
    """{trading day: the previous trading day's last close at or before 16:00 CT} from the bar store's rows (`day`,
    `ts`, `open`, `close`, and `contract` if present), the days being those with rows, in order: of the previous day's
    rows, the one with the latest `ts` ending at slot 1 .. 1380. Each value: prev_day, prev_close (NaN: none), the
    bar's end (CT, ISO) and contract, the day's own first contract and `roll` (the two differ). The first day: no
    previous day (prev_close NaN)."""
    if bars.empty:
        return {}
    b = bars.sort_values(["day", "ts"], kind="stable")
    slot = bar_end_slots(b["ts"].to_numpy())
    ok = (slot >= 1) & (slot <= CLOSE_SLOT)
    has_c = "contract" in b.columns
    days = [str(d) for d in pd.unique(b["day"].astype(str))]
    last: dict[str, tuple[float, str, str]] = {}
    q = b[ok]
    for d, g in q.groupby(q["day"].astype(str), sort=True):
        r = g.iloc[-1]
        end = pd.Timestamp(int(r["ts"]) + 60, unit="s", tz="UTC").tz_convert("America/Chicago")
        last[str(d)] = (float(r["close"]), end.isoformat(), str(r["contract"]) if has_c else "")
    first_c = b.groupby(b["day"].astype(str), sort=True)["contract"].first().astype(str).to_dict() if has_c else {}
    out = {}
    for i, d in enumerate(days):
        if i == 0:
            out[d] = {"prev_day": None, "prev_close": float("nan"), "prev_close_end_ct": None, "prev_contract": None,
                      "contract": first_c.get(d), "roll": False}
            continue
        p = days[i - 1]
        cl, end, con = last.get(p, (float("nan"), None, None))
        out[d] = {"prev_day": p, "prev_close": cl, "prev_close_end_ct": end, "prev_contract": con,
                  "contract": first_c.get(d), "roll": bool(has_c and con is not None and con != first_c.get(d))}
    return out


# ------------------------------------------------------------------------------------------------ stage 1


def stage1(day_sum: np.ndarray, day_n: np.ndarray, *, reps: int = BOOT_REPS, block: float = BOOT_BLOCK,
           seed: int = BOOT_SEED, alpha: float = ALPHA, bh_q: float = BH_Q) -> dict[str, Any]:
    """S1's test (`s1_sided_coin.stage1`) at S3's declared alpha, seed, block and replicates."""
    return S1.stage1(day_sum, day_n, reps=reps, block=block, seed=seed, alpha=alpha, bh_q=bh_q)


def hypotheses() -> pd.DataFrame:
    """One row per (rule, R) in the accumulators' column order (rule-major, R-minor)."""
    return A4.hypothesis_frame([{"rule": n, "rule_index": i, "definition": DEFINITIONS[n]}
                                for i, n in enumerate(RULE_NAMES)], OFFERED_R)


def survivors(hyp: pd.DataFrame) -> list[tuple[str, int]]:
    """The distinct (rule, side sign) of the surviving hypotheses in menu order (sign = the mean lift's: +1 follow, -1
    fade) -- S1's `survivors` on S3's menu."""
    s = hyp[hyp["survives"].astype(bool)]
    out: list[tuple[str, int]] = []
    for _, r in s.iterrows():
        k = (str(r["rule"]), 1 if float(r["mean_lift"]) > 0 else -1)
        if k not in out:
            out.append(k)
    order = {n: i for i, n in enumerate(RULE_NAMES)}
    return sorted(out, key=lambda k: (order[k[0]], -k[1]))


def g2_summary(rows: Sequence[Mapping[str, Any]], arms: Sequence[str], reference: str,
               wins_needed: int = G2_WINS) -> list[dict[str, Any]]:
    return S1.g2_summary(rows, arms, reference, wins_needed)


def verdict(arm: str, g1_growth: float, ref_growth: float, resolves: bool, g2_row: Mapping[str, Any] | None,
            span_growth: Mapping[str, float], span_ref: Mapping[str, float]) -> dict[str, Any]:
    """D-578 (2)'s four guards (`s1_sided_coin.verdict`; its margin, spans and wins are S3's, checked equal)."""
    return S1.verdict(arm, g1_growth, ref_growth, resolves, g2_row, span_growth, span_ref)


def shared_problems() -> list[str]:
    """S1's functions are used for the campaign: their constants must be S3's."""
    out = []
    for k, mine, theirs in (("margin", MARGIN, S1.MARGIN), ("spans", SPANS, S1.SPANS), ("g2 wins", G2_WINS, S1.G2_WINS),
                            ("offered R", OFFERED_R, S1.OFFERED_R), ("block", BOOT_BLOCK, S1.BOOT_BLOCK),
                            ("reps", BOOT_REPS, S1.BOOT_REPS), ("bh", BH_Q, S1.BH_Q),
                            ("coin seeds", COIN_SEEDS, S1.COIN_SEEDS), ("g2 paths", G2_PATHS, S1.G2_PATHS),
                            ("campaign seed", CAMPAIGN_SEED, S1.CAMPAIGN_SEED), ("paths", N_PATHS, S1.N_PATHS),
                            ("stop", STOP_TICKS, S1.STOP_TICKS)):
        if mine != theirs:
            out.append(f"{k}: S3's {mine!r} against S1's {theirs!r}")
    return out


__all__ = ["DECISION", "DECLARED_BY", "BATCH", "FAMILY_ID", "ALPHA", "BH_Q", "BOOT_REPS", "BOOT_BLOCK", "BOOT_SEED",
           "STOP_TICKS", "OFFERED_R", "CAMPAIGN_SEED", "N_PATHS", "COIN_SEEDS", "G2_PATHS", "G2_WINS", "MARGIN",
           "SPANS", "N_VARIANTS", "N_HYPOTHESES", "RTH_OPEN_SLOT", "CLOSE_SLOT", "RULES", "RULE_NAMES", "DEFINITIONS",
           "declaration", "declaration_problems", "event_sides", "bar_candidates", "day_sides", "bar_end_slots",
           "prior_closes", "lift_matrix", "accumulate", "stage1", "hypotheses", "survivors", "arm_name",
           "campaign_coins", "g2_summary", "verdict", "shared_problems"]
