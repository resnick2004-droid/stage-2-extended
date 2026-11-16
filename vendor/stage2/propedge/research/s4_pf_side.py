"""EXPLORATORY (D-578, D-610): batch S4 of the rolling model search -- the sided coin with each offer's side from the
Point & Figure chart. Pure functions; `scripts/s4_pf_side.py` reads the bars, builds P-16's cell and writes the result.

**What S4 is** (`config/search_program_s4.yaml`, fixed by D-610 before this code was built): S3's design exactly
(`propedge.research.s3_event_kinds`, D-579's and D-587's readings) -- P-16 (`rc_s150_all_nr`, the 150-tick news-safe
all-day coin re-entering when flat, an offer every five minutes, P-14's money side, five Topstep seats) with only the
side of each offer changed: each offered (date, mark) takes its side from one of ten declared rules on D-607's Point &
Figure engine (`propedge.research.pnf.scan`). The entry stays at the open of the first bar after the mark. Only the
rules, the latency, alpha (0.05 / 20), the bootstrap seed (20261712), the counts (10 variants, 60 hypotheses), the family
id (`D-578:S4`), the declaration file and the output file differ from S3; the lift, the accumulators, the bootstrap, the
coins of the campaign, G2's summary and the verdict are S1's functions (through S3, which imports them), unchanged.

**The chart** (D-607, `pnf.scan`): one pass over the development bars (2020-01-01 .. 2026-07-16, the bars `pf_fit`
reads, in `ts` order), continuous across sessions, restarting at every roll (a bar whose contract differs from the
previous bar's), reversal 3, one fixed box per rule. A setup's **trigger end slot** is its trigger bar's END on the
trading-day clock (`s3_event_kinds.bar_end_slots`: minutes after 17:00 CT, 1 .. 1440; Databento stamps a bar at its
start, it ends 60 s later) and its **date** the trigger bar's trading day (the store's `day`) -- `pf_fit.setup_rows`'s
`date` and `trigger_end_slot`, which identity (b) reproduces from `results/pf_fit_setups.csv`.

**The rules** (`RULES`; side +1 / -1, 0 = a tie):

    pfc<box>  the side of the most recent catapult setup under D-607's fixed reading r7_low (`max7_from_R` and
              `above_pattern_low` both true; bull +1, bear -1)
    pft<box>  the side of the most recent plain triple top buy (+1) / triple bottom sell (-1)

at boxes 2.5, 5, 6.25 (25 ticks; arm C, D-609 (1)), 7.5 and 10 points.

**The latency (D-589, D-266; `LATENCY_MIN` = 5)**: at mark t a setup counts only when its trigger bar ENDED at or
before t - 5 minutes on the clock, ON THE SAME TRADING DAY (its date is the mark's date). The most recent such setup --
the largest trigger end slot <= t - 5 -- decides; setups triggering on one bar (one slot) are summed and their sign
taken (opposite sides on one bar tie; within one rule the engine cannot produce that -- every setup triggering on a bar
is on that bar's column's side -- so the rule is defensive). None yet today -> a tie: excluded from the lift, P-16's
coin in the campaign. Marks 0 and 5 always tie (no bar of the day ends at or before slot 0). A trigger after 15:10 CT
(slot >= 1330) never precedes a mark (the last mark is 1325), so setups out of Topstep's hours never decide a side.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from propedge.research import a4_coin_atlas as A4
from propedge.research import pnf
from propedge.research import s1_sided_coin as S1
from propedge.research import s3_event_kinds as S3

DECISION = "D-578"
DECLARED_BY = "D-610"
BATCH = "S4"
FAMILY_ID = f"{DECISION}:{BATCH}"
ALPHA = 0.05 / 20                          # alpha_4 = 0.05 / (4 x 5)
BH_Q = 0.10
BOOT_REPS = 2000
BOOT_BLOCK = 21.0
BOOT_SEED = 20261712                       # D-610, used nowhere before
STOP_TICKS = 150
OFFERED_R = S1.OFFERED_R                   # (0.25, 1, 1.5, 2, 2.5, 3)
CAMPAIGN_SEED = 20261131
N_PATHS = 500
COIN_SEEDS = tuple(20261600 + i for i in range(50))     # D-578 (2), D-568 (2)
G2_PATHS = 200
G2_WINS = 40
MARGIN = 0.05
SPANS = dict(S1.SPANS)
N_VARIANTS = 10
N_HYPOTHESES = 60
LATENCY_MIN = 5                            # D-589 / D-266: the operator's L, on every S4 rule
LAST_MARK_SLOT = 1325                      # resolved_coin.marks' last (15:05 CT)

BOXES = (2.5, 5.0, 6.25, 7.5, 10.0)        # points; 6.25 = 25 ticks (arm C)
PF_FIT_BOXES = tuple(float(b) for b in pnf.BOXES)        # identity (b): the boxes results/pf_fit_setups.csv holds
CATAPULT = "catapult"
PLAIN = "plain"
FIXED_READING = "r7_low"                   # D-607's fixed catapult reading: max7_from_R and above_pattern_low


def _box_name(b: float) -> str:
    return f"{b:g}".replace(".", "_")


#: the ten rules in the declaration's order: (name, family, box points)
RULES: tuple[tuple[str, str, float], ...] = (
    tuple((f"pfc{_box_name(b)}", CATAPULT, float(b)) for b in BOXES)
    + tuple((f"pft{_box_name(b)}", PLAIN, float(b)) for b in BOXES))
RULE_NAMES = tuple(r[0] for r in RULES)
DEFINITIONS = {
    **{f"pfc{_box_name(b)}": f"side of the most recent P&F catapult (D-607's fixed reading r7_low; bull +1, bear -1) "
                             f"at box {b:g} points, reversal 3, triggered at or before t - 5 min the same trading day"
       for b in BOXES},
    **{f"pft{_box_name(b)}": f"side of the most recent plain P&F triple top buy (+1) / triple bottom sell (-1) at box "
                             f"{b:g} points, reversal 3, triggered at or before t - 5 min the same trading day"
       for b in BOXES}}

# re-used unchanged (D-610: S3's design exactly; S3's are S1's)
lift_matrix = S3.lift_matrix
accumulate = S3.accumulate
campaign_coins = S3.campaign_coins
arm_name = S3.arm_name
bar_end_slots = S3.bar_end_slots
_latest = S3._latest


# ------------------------------------------------------------------------------------------------ the declaration


#: `config/search_program_s4.yaml` as D-610 committed it (f6ab5bb): the sha256 of its text with LF line ends (Git may
#: check it out with CRLF, `text=auto`; the hash is the repository's bytes either way -- D-579's handling)
DECLARATION_SHA256 = "30887b2874acc79d7b1ef442fa8bc30cb82a1e1b1a8146f571febfe19137ab3e"
DECLARATION_FILE = Path(__file__).resolve().parents[2] / "config" / "search_program_s4.yaml"

#: `results/pf_fit_setups.csv` as D-609 read it (its manifest's sha256; the file is `-text` in .gitattributes)
PF_SETUPS_FILE = "pf_fit_setups.csv"
PF_SETUPS_SHA256 = "9fcf7d7330e607ad7bb6bd3a9f35cb24efbf2436ccfad71d0ac199da2cc19983"
#: the fields of a setup the rules use, compared in identity (b)
IDENT_FIELDS = ("date", "trigger_end_slot", "side", "kind", "box_points")

#: phrases of the batch's own words each constant rests on (line breaks folded to spaces)
S4_WORDS = ("id: S4", "decision: D-610", "program: D-578", "name: sided coin, Point & Figure direction",
            f"stop_ticks: {STOP_TICKS}", "stop (150 ticks)", "Follow and fade are one two-sided test (fade = minus "
            "follow)", "A tie (no qualifying setup yet today) is excluded from the lift and takes P-16's own coin side "
            "in the campaign (G1) and that sequence's coin in G2", "0.05 / (4 * 5)",
            "a rule at mark t reads only setups whose trigger bar ENDED at or before t - 5 minutes, on the same trading "
            "day (the trading-day clock)", "the order then works at the first bar after t exactly as P-16's",
            "D-607's engine (pnf.scan) on the development bars, continuous across sessions, restarting at every roll, "
            "reversal 3, one fixed box per rule", "a trigger after 15:10 CT never precedes a mark",
            "10 rules; side = the setup's side (bull / buy +1, bear / sell -1); none yet today -> tie",
            "at every offered R (0.25, 1, 1.5, 2, 2.5, 3)", f"hypotheses: {N_HYPOTHESES}", "10 rules x 6 R",
            "block 21, 2,000 reps, seed 20261712", "Benjamini-Hochberg at 10 % beside, never selecting",
            "campaign seed 20261131, 500 paths", "paired +0.05 at the bound", "every offered R resolves",
            "at least 40 of 50 coin sequences", "seeds 20261600 + i, 200 paths", "not below P-16 on either span alone",
            "with_no_survivor: stage 1 and the reference's paired row only", f"variants: {N_VARIANTS}",
            "results/s4_pf_side.csv", "D-578:S4", "the box at which the fixed catapult's median natural stop",
            "is 37.5 points; fixed by D-609, never searched")
#: the words of each rule the code computes (the rule's own line in the declaration)
RULE_WORDS = {
    "pfc2_5": ("side of the most recent catapult", "D-607's fixed reading r7_low", "bull or bear", "box 2.5 points"),
    "pfc5": ("the same", "box 5 points"),
    "pfc6_25": ("the same", "box 6.25 points", "arm C"),
    "pfc7_5": ("the same", "box 7.5 points"),
    "pfc10": ("the same", "box 10 points"),
    "pft2_5": ("side of the most recent plain triple top buy / triple bottom sell", "box 2.5 points"),
    "pft5": ("the same", "box 5 points"),
    "pft6_25": ("the same", "box 6.25 points"),
    "pft7_5": ("the same", "box 7.5 points"),
    "pft10": ("the same", "box 10 points")}


def _fold(s: Any) -> str:
    return re.sub(r"\s+", " ", str(s))


def declaration(path: Path | str | None = None) -> dict[str, Any]:
    """`config/search_program_s4.yaml`: its sha256 (LF line ends), the parsed YAML (the file is valid YAML) and its text,
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
        out.append(f"the declaration's sha256 is {str(decl['sha256'])[:16]}, not D-610's {DECLARATION_SHA256[:16]}")
    if str(decl["program_sha256"]) != S1.DECLARATION_SHA256:
        out.append("the program file (config/search_program.yaml) is not D-578's pinned text")
    if f"decision: {DECISION}" not in str(decl["program"]):
        out.append(f"the program is not {DECISION}'s")
    b = decl["batch"]
    if not b:
        out.append("no S4 batch in the declaration")
    text = _fold(decl["text"])
    try:
        alpha = float(b.get("alpha"))
    except (TypeError, ValueError):
        alpha = float("nan")
    if not abs(alpha - ALPHA) < 5e-11:
        out.append(f"alpha {b.get('alpha')!r} is not 0.05 / 20")
    for key, want in (("id", BATCH), ("decision", DECLARED_BY), ("program", DECISION), ("stop_ticks", STOP_TICKS),
                      ("variants", N_VARIANTS)):
        if b.get(key) != want:
            out.append(f"{key}: {b.get(key)!r}, not {want!r}")
    if (b.get("stage_1") or {}).get("hypotheses") != N_HYPOTHESES:
        out.append(f"stage_1 hypotheses are not {N_HYPOTHESES}")
    if tuple(decl["rules"]) != RULE_NAMES:
        out.append(f"rules {list(decl['rules'])}, not {list(RULE_NAMES)}")
    if len(RULE_NAMES) * len(OFFERED_R) != N_HYPOTHESES or len(RULE_NAMES) != N_VARIANTS:
        out.append("10 rules x 6 R is not the declared 60 hypotheses and 10 variants")
    if f"t - {LATENCY_MIN} minutes" not in text:
        out.append(f"the declaration's latency is not {LATENCY_MIN} minutes")
    out += [f"S4's declaration does not say {w!r}" for w in S4_WORDS if w not in text]
    rt = decl["rule_text"]
    for name, words in RULE_WORDS.items():
        for w in words:
            if w not in _fold(rt.get(name, "")):
                out.append(f"rule {name} does not say {w!r}")
    if tuple(OFFERED_R) != tuple(A4.OFFERED_R):
        out.append("the offered R are not A4's / the table's")
    if pnf.REVERSAL != 3:
        out.append(f"the engine's reversal is {pnf.REVERSAL}, not 3")
    if [pnf.box_ticks(x) for x in BOXES] != [10, 20, 25, 30, 40]:
        out.append("the boxes are not 10, 20, 25, 30 and 40 ticks")
    if not set(PF_FIT_BOXES) <= set(BOXES) or tuple(b for b in BOXES if b not in PF_FIT_BOXES) != (6.25,):
        out.append("the boxes are not pf_fit's four and 6.25")
    return out


# ------------------------------------------------------------------------------------------------ the rules


def scan_events(bars: pd.DataFrame, box: float, *, result: Mapping[str, Any] | None = None) -> pd.DataFrame:
    """Every setup of `pnf.scan` at `box` on `bars` (columns ts, day, high, low, close and contract if present; in ts
    order), one row each in the engine's order: date (the trigger bar's trading day), trigger_end_slot (its end on the
    trading-day clock), side, kind, box_points, and `fixed` (a catapult under r7_low; True on every plain setup)."""
    cols = ["date", "trigger_end_slot", "side", "kind", "box_points", "fixed"]
    if result is None:
        if len(bars) and not (np.diff(bars["ts"].to_numpy(dtype="int64")) > 0).all():
            raise ValueError("the bars must be in strictly increasing ts order")
        result = pnf.scan(bars["high"].to_numpy(), bars["low"].to_numpy(), bars["close"].to_numpy(),
                          bars["contract"].astype(str).to_numpy() if "contract" in bars.columns else None, box=box)
    S = list(result["setups"])
    if not S:
        return pd.DataFrame({c: pd.Series(dtype=t) for c, t in zip(cols, (object, "int64", "int64", object, float,
                                                                           bool))})
    ts = bars["ts"].to_numpy(dtype="int64")
    day = bars["day"].astype(str).to_numpy()
    it = np.array([s["trigger_bar"] for s in S], dtype=np.int64)
    kind = [str(s["kind"]) for s in S]
    fixed = [bool(s["max7_from_R"] is True and s["above_pattern_low"] is True) if k in pnf.CATAPULTS else True
             for s, k in zip(S, kind)]
    return pd.DataFrame({"date": day[it], "trigger_end_slot": bar_end_slots(ts[it]).astype(np.int64),
                         "side": np.array([int(s["side"]) for s in S], dtype=np.int64), "kind": kind,
                         "box_points": float(int(result["box_ticks"]) * pnf.TICK), "fixed": fixed})[cols]


def rule_events(events: pd.DataFrame, family: str) -> pd.DataFrame:
    """The setups one rule reads: the catapults under the fixed reading (`catapult`) or the plain triples (`plain`)."""
    k = events["kind"].astype(str)
    if family == CATAPULT:
        m = k.isin(pnf.CATAPULTS) & events["fixed"].astype(bool)
    elif family == PLAIN:
        m = k.isin(pnf.PLAINS)
    else:
        raise ValueError(f"unknown rule family {family!r}")
    return events[m.to_numpy()]


def day_events(events: pd.DataFrame) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """{date: (trigger end slots ascending, the sign of the sides' sum at each slot)} -- setups on one bar summed."""
    out: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    if not len(events):
        return out
    g = events.groupby([events["date"].astype(str), events["trigger_end_slot"].astype(np.int64)], sort=True)["side"].sum()
    for d, s in g.groupby(level=0, sort=True):
        out[str(d)] = (s.index.get_level_values(1).to_numpy(dtype=np.int64),
                       np.sign(s.to_numpy()).astype(np.int8))
    return out


def lagged_sides(slots: np.ndarray, sides: np.ndarray, marks: Sequence[int], lag: int = LATENCY_MIN) -> np.ndarray:
    """At each mark t, the side of the most recent slot <= t - `lag` (none: 0). `slots`, `sides` are one trading day's
    (ascending; `day_events`), so a setup of an earlier day never counts."""
    if int(lag) < 0:
        raise ValueError("the latency is not negative")
    M = np.asarray([int(m) for m in marks], dtype=np.int64)
    return _latest(np.asarray(slots, dtype=np.int64), np.asarray(sides, dtype=np.int8), M - int(lag))


def side_table(events_by_rule: Mapping[str, pd.DataFrame], days: Sequence[str], marks: Sequence[int], *,
               lag: int = LATENCY_MIN, rules: Sequence[str] = RULE_NAMES) -> dict[str, np.ndarray]:
    """{date: (marks, rules) int8 sides} on `days`: each rule's side at every mark from its own setups
    (`events_by_rule[rule]`, `rule_events`), the most recent one that triggered at or before t - `lag` that day."""
    per = {r: day_events(events_by_rule[r]) for r in rules}
    empty = (np.zeros(0, dtype=np.int64), np.zeros(0, dtype=np.int8))
    out = {}
    for d in days:
        d = str(d)
        out[d] = np.stack([lagged_sides(*per[r].get(d, empty), marks, lag) for r in rules], axis=1).astype(np.int8)
    return out


def sides_from_bars(bars: pd.DataFrame, days: Sequence[str], marks: Sequence[int], *, lag: int = LATENCY_MIN,
                    rules: Sequence[tuple[str, str, float]] = RULES) -> dict[str, np.ndarray]:
    """The whole construction from bars: one scan per box over `bars`, each rule's setups, the lagged side table."""
    scans = {}
    ev = {}
    for name, fam, box in rules:
        if box not in scans:
            scans[box] = scan_events(bars, box)
        ev[name] = rule_events(scans[box], fam)
    return side_table(ev, days, marks, lag=lag, rules=[r[0] for r in rules])


# ------------------------------------------------------------------------------------------------ identity (b)


def fixed_rows(rows: pd.DataFrame) -> pd.DataFrame:
    """`results/pf_fit_setups.csv`'s rows the rules read: the catapults under r7_low and every plain triple, in the
    file's order, the identity's fields only (date and kind as text, slot and side integers, box float)."""
    k = rows["kind"].astype(str)
    r7 = rows["r7_low"].astype(str).str.lower().isin(("true", "1"))
    m = (k.isin(pnf.CATAPULTS) & r7) | k.isin(pnf.PLAINS)
    return _norm(rows[m.to_numpy()])


def _norm(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({"date": df["date"].astype(str).to_numpy(),
                         "trigger_end_slot": df["trigger_end_slot"].astype(np.int64).to_numpy(),
                         "side": df["side"].astype(np.int64).to_numpy(), "kind": df["kind"].astype(str).to_numpy(),
                         "box_points": df["box_points"].astype(float).to_numpy()})


def setups_problems(file_rows: pd.DataFrame, engine: Mapping[float, pd.DataFrame]) -> list[str]:
    """Identity (b): for each of pf_fit's boxes, the engine's catapults under r7_low and its plain triples
    (`scan_events` -> `rule_events`, in the engine's order) equal the file's (`fixed_rows`): the count per kind and, row
    by row in order, date, trigger end slot, side, kind and box."""
    out = []
    f = fixed_rows(file_rows)
    for box in PF_FIT_BOXES:
        want = f[np.isclose(f["box_points"], box)].reset_index(drop=True)
        if box not in engine:
            out.append(f"box {box:g}: not scanned")
            continue
        ev = engine[box]
        got = _norm(pd.concat([rule_events(ev, CATAPULT), rule_events(ev, PLAIN)]).sort_index(kind="stable")
                    ).reset_index(drop=True)
        cw, cg = want["kind"].value_counts().to_dict(), got["kind"].value_counts().to_dict()
        if cw != cg:
            out.append(f"box {box:g}: the engine's counts {cg} are not the file's {cw}")
            continue
        if len(got) != len(want):
            out.append(f"box {box:g}: {len(got)} setups against the file's {len(want)}")
            continue
        for c in IDENT_FIELDS:
            a, b = got[c].to_numpy(), want[c].to_numpy()
            same = np.isclose(a.astype(float), b.astype(float), rtol=0, atol=1e-9) if c == "box_points" else a == b
            if not np.all(same):
                i = int(np.argmin(same))
                out.append(f"box {box:g}: field {c} differs from the file at its row {i} ({a[i]!r} against {b[i]!r})")
    extra = sorted(set(np.round(f["box_points"], 9)) - set(PF_FIT_BOXES))
    if extra:
        out.append(f"the file holds boxes {extra} beyond pf_fit's")
    return out


# ------------------------------------------------------------------------------------------------ stage 1


def stage1(day_sum: np.ndarray, day_n: np.ndarray, *, reps: int = BOOT_REPS, block: float = BOOT_BLOCK,
           seed: int = BOOT_SEED, alpha: float = ALPHA, bh_q: float = BH_Q) -> dict[str, Any]:
    """S1's test (`s1_sided_coin.stage1`) at S4's declared alpha, seed, block and replicates."""
    return S1.stage1(day_sum, day_n, reps=reps, block=block, seed=seed, alpha=alpha, bh_q=bh_q)


def hypotheses() -> pd.DataFrame:
    """One row per (rule, R) in the accumulators' column order (rule-major, R-minor)."""
    return A4.hypothesis_frame([{"rule": n, "rule_index": i, "definition": DEFINITIONS[n]}
                                for i, n in enumerate(RULE_NAMES)], OFFERED_R)


def survivors(hyp: pd.DataFrame) -> list[tuple[str, int]]:
    """The distinct (rule, side sign) of the surviving hypotheses in menu order (sign = the mean lift's: +1 follow, -1
    fade) -- S1's `survivors` on S4's menu."""
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
    """D-578 (2)'s four guards (`s1_sided_coin.verdict`; its margin, spans and wins are S4's, checked equal)."""
    return S1.verdict(arm, g1_growth, ref_growth, resolves, g2_row, span_growth, span_ref)


def shared_problems() -> list[str]:
    """S1's functions are used for the campaign: their constants must be S4's (and S3's, whose design S4 is)."""
    out = []
    for k, mine, s1, s3 in (("margin", MARGIN, S1.MARGIN, S3.MARGIN), ("spans", SPANS, S1.SPANS, S3.SPANS),
                            ("g2 wins", G2_WINS, S1.G2_WINS, S3.G2_WINS),
                            ("offered R", OFFERED_R, S1.OFFERED_R, S3.OFFERED_R),
                            ("block", BOOT_BLOCK, S1.BOOT_BLOCK, S3.BOOT_BLOCK),
                            ("reps", BOOT_REPS, S1.BOOT_REPS, S3.BOOT_REPS), ("bh", BH_Q, S1.BH_Q, S3.BH_Q),
                            ("coin seeds", COIN_SEEDS, S1.COIN_SEEDS, S3.COIN_SEEDS),
                            ("g2 paths", G2_PATHS, S1.G2_PATHS, S3.G2_PATHS),
                            ("campaign seed", CAMPAIGN_SEED, S1.CAMPAIGN_SEED, S3.CAMPAIGN_SEED),
                            ("paths", N_PATHS, S1.N_PATHS, S3.N_PATHS),
                            ("stop", STOP_TICKS, S1.STOP_TICKS, S3.STOP_TICKS)):
        if not (mine == s1 == s3):
            out.append(f"{k}: S4's {mine!r} against S1's {s1!r} / S3's {s3!r}")
    if BOOT_SEED in (S1.BOOT_SEED, S3.BOOT_SEED):
        out.append("S4's bootstrap seed was used by an earlier batch")
    return out


__all__ = ["DECISION", "DECLARED_BY", "BATCH", "FAMILY_ID", "ALPHA", "BH_Q", "BOOT_REPS", "BOOT_BLOCK", "BOOT_SEED",
           "STOP_TICKS", "OFFERED_R", "CAMPAIGN_SEED", "N_PATHS", "COIN_SEEDS", "G2_PATHS", "G2_WINS", "MARGIN",
           "SPANS", "N_VARIANTS", "N_HYPOTHESES", "LATENCY_MIN", "LAST_MARK_SLOT", "BOXES", "PF_FIT_BOXES",
           "CATAPULT", "PLAIN", "FIXED_READING", "RULES", "RULE_NAMES", "DEFINITIONS", "DECLARATION_SHA256",
           "DECLARATION_FILE", "PF_SETUPS_FILE", "PF_SETUPS_SHA256", "IDENT_FIELDS", "declaration",
           "declaration_problems", "scan_events", "rule_events", "day_events", "lagged_sides", "side_table",
           "sides_from_bars", "fixed_rows", "setups_problems", "lift_matrix", "accumulate", "stage1", "hypotheses",
           "survivors", "arm_name", "campaign_coins", "g2_summary", "verdict", "shared_problems"]
