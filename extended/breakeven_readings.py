"""Q-132 (the lead's E-189; the Q-45 audit's D1, C1, C2, C6, C7): the second breakeven-fidelity reading's own rows --
the per-start file every P and guard is re-derived from, the paired interval of each corrected rule set against
`stage2`, the minimum detectable difference in P, the assumptions, the variants and the log's head. Pure functions over
`extended.user_beside.run_starts`' outputs; the vendored pure modules (`propedge.research.user_journey`, `u_select`)
are imported at call time, so call them in a process with `use_vendored_stage2()` done (`scripts/
breakeven_fidelity_2.py`).

**The per-start file (D1)** (`start_frame`, `START_FILE_COLS`): one row a (design, rule set, arm, start) -- the
start's record as U1 keeps it (`user_journey.start_record`'s keys: the event days, every payout's cash, the month-end
nets and fees, the net at session 30), the exact-length runs that differed from the long replay **with their records**
(`alt`, JSON: a reading at h sessions reads the exact run's record there, `user_journey.effective`), the months ahead P
reads (`u_select.months_ahead`, blank where the start is not eligible), and Q-17's daily path and evenness values
(`extended.user_readings.start_table`). Money is written as the engine booked it, never rounded (a rounded net can
change the sign P reads). `records_from_frame` inverts it; `rederive_problems` re-makes the scorecard, extra and path
rows from the file's text alone and holds them to the runner's (a refusing check, so the file is shown to carry every
figure before it is written).

**The paired interval (C2)** (`paired_rows`): for each corrected rule set against `stage2`, design, arm and block,
the per-start difference in the months ahead over three (P's own unit, `u_select.months_ahead` / 3) on the same
starts, read by RD-02's section 9.2 (`prereg/RD-02_payout_policy.md`, pinned; `extended.pp_reading`): the mean over
every start (equal to the two cards' P difference -- a refusing check), the kept windows (every other 63-start window),
the sign count, the effective sample size, the 90 % Student-t interval and its minimum detectable difference when at
least four windows are kept, and the interval's honesty on synthetic series (`honesty_rows`, 9.2 item 7: 21 shapes,
20,000 series a setting) with its label. A description, not a test: no level, nothing decided (E-023 (1)).

**`mdd_P` (E-007 (e), now that Q-16 is merged, E-035)** (`mdd_p`, `fill_mdd_p`): the minimum detectable difference
of the scorecard's P comparison as Q-16 calibrated it (`extended.p_bound`: a design's paired difference in the ahead
average from R* = P-14 on the judged block's starts) -- the 80th percentile over null replications of the shipped
statistic's (`p_bound.SHIPPED`, `pcons`) smallest carried shift, at the next family's level 0.05 / 132 (k = 11, CHARTER
section 2), on Q-16's real-null form (the series centred, its signs flipped in blocks of 63 consecutive starts at a
random phase -- `scripts/q16_calibrate.py`'s `_flip_signs`, held equal by a test). For each design but P-14 (R*
itself), on each rule set and arm against P-14 on the same rule set and arm; the judged block only (the calibration's;
the `all` block is left blank with the reason).

**The seeds** (`SEED_BLOCK`, 20262260-20262269, found in no other file of the repository, its vendored snapshot, any
git ref, any worktree or any clean-run folder before this module was written -- `tests/test_breakeven_fidelity_2.py`
repeats the check on every run): by role, `SEED_ROLES`. The inherited seeds are their owners': the gates' registered
campaign seeds (P-14 20261131, P-15 20261204, P-16 20261206), Q-17's start seeds (`user_beside.start_seed`, nothing
drawn at 0 %), and `p_bound`'s fixed-b critical values (Q-16's 20261919).
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

from extended import ROOT
from extended import pp_reading as RD
from extended import user_readings as R

#: the block (searched for in no other file before use) and each seed's one role
SEED_BLOCK = tuple(range(20262260, 20262270))
HONESTY_SEED = SEED_BLOCK[0]
MDD_SEED = SEED_BLOCK[1]
TEST_SEED = SEED_BLOCK[2]
SEED_ROLES = {
    HONESTY_SEED: "RD-02 9.2 item 7's honesty series for this reading's paired intervals: "
                  "numpy.random.default_rng([seed, 1, shape index, h, n_w]) (extended.pp_reading.honesty_rng)",
    MDD_SEED: "mdd_P's null replications: numpy.random.default_rng([seed, design index, rule-set index, arm index]), "
              "the designs, rule sets and arms in the runner's declared order",
    TEST_SEED: "the synthetic records and series of tests/test_breakeven_fidelity_2.py only; never a reading",
    **{s: "reserved, unused" for s in SEED_BLOCK[3:]},
}

#: P's horizon and the paired reading's (u_select.P_HORIZON; checked at call time)
P_HORIZON = 63
#: RD-02 9.2's interval level, its least kept windows and its honesty series a setting (extended.pp_reading)
INTERVAL_LEVEL = RD.LEVEL
MIN_WINDOWS = RD.MIN_WINDOWS
HONESTY_SERIES = RD.HONESTY_SERIES
#: the corrected rule sets, each read against `stage2`
REFERENCE_RULES = "stage2"
#: the blocks: every start, and D-621 (4)(b)'s late block (`u_select.block(..., "late", h)`)
BLOCKS = (("all", None), ("judged", "late"))
#: mdd_P: Q-16's shipped statistic, the next family's number, the power, the replications, the flip block
MDD_K = 11
MDD_POWER = 0.80
MDD_REPS = 20_000
MDD_BATCH = 2_000
MDD_FLIP_BLOCK = 63
MDD_REFERENCE = "p14"
#: the fewest starts `pcons` can be formed on: two 63-start batches and more starts than the 126-start OBM batch and
#: flat-top taper (`p_bound.batch_t`, `obm`, `flat_top`); fewer leave mdd_P blank with the reason
MDD_MIN_STARTS = 127

#: the per-start file's columns, in order
RECORD_LIST_COLS = ("pass_days", "funded_days", "pay_days")
PATH_COLS = ("months_ahead", "break_even_day", "fell_back", "deepest_fall_after_break_even", "share_months_positive",
             "longest_months_without_payout", "sd_monthly_net", "payouts_per_month", "payout_cash_per_month",
             "largest_month_share")
MONTHS = 12
START_FILE_COLS = (
    "design", "rules", "arm", "start_day", "start_date", "observed", *RECORD_LIST_COLS, "pay_cash", "payouts",
    "first_pass", "first_funded", "first_payout", "first_payout_cash", "spent_before_first_pass",
    "spent_before_first_payout", *(f"net_month_{k}" for k in range(1, MONTHS + 1)),
    *(f"fees_month_{k}" for k in range(1, MONTHS + 1)), "net_30", "exact_runs_differing", "alt", "p_months_ahead",
    *PATH_COLS)
RECORD_FLOATS = ("first_pass", "first_funded", "first_payout", "first_payout_cash", "spent_before_first_pass",
                 "spent_before_first_payout", "net_30")
NAN = float("nan")


# ------------------------------------------------------------------------------------------------ small helpers


def _f(x: Any) -> float:
    return NAN if x is None else float(x)


def _join_ints(xs: Iterable[Any]) -> str:
    return " ".join(str(int(x)) for x in xs)


def _join_floats(xs: Iterable[Any]) -> str:
    return " ".join(repr(float(x)) for x in xs)


def _split(cell: Any, kind: type) -> list:
    if cell is None or (isinstance(cell, float) and math.isnan(cell)) or str(cell).strip() == "":
        return []
    return [kind(float(v)) if kind is int else kind(v) for v in str(cell).split()]


def _jsonable(x: Any) -> Any:
    if isinstance(x, dict):
        return {str(k): _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, np.ndarray)):
        return [_jsonable(v) for v in list(x)]
    if isinstance(x, (bool, np.bool_)):
        return bool(x)
    if isinstance(x, (int, np.integer)):
        return int(x)
    if isinstance(x, (float, np.floating)):
        return float(x)
    return x


def read_text_csv(text_or_path: Any) -> pd.DataFrame:
    """A per-start file read back as its text gives it: blanks as NaN, floats round-trip exact, dates as text."""
    import io

    src = io.StringIO(text_or_path) if isinstance(text_or_path, str) and "\n" in text_or_path else text_or_path
    return pd.read_csv(src, keep_default_na=False, na_values=[""], float_precision="round_trip",
                       dtype={"start_date": str, "alt": str, "exact_runs_differing": str, "pay_cash": str,
                              **{c: str for c in RECORD_LIST_COLS}}, low_memory=False)


# ------------------------------------------------------------------------------------------------ P's per-start unit


def p_months_ahead(records: Sequence[Mapping[str, Any]], which: str | None = None) -> dict[str, float]:
    """{start date: months ahead (0 .. 3)} as P reads them on the block (`u_select.months_ahead` on
    `u_select.block(records, which, P_HORIZON)`), in date order."""
    from propedge.research import u_select as S

    if int(S.P_HORIZON) != P_HORIZON:
        raise RuntimeError(f"u_select.P_HORIZON is {S.P_HORIZON}, not {P_HORIZON}")
    d = S.months_ahead(S.block(records, which, P_HORIZON))
    return {k: d[k] for k in sorted(d)}


# ------------------------------------------------------------------------------------------------ D1: the per-start file


def start_frame(design: str, rules: str, arm: str, outs: Sequence[Mapping[str, Any]]) -> pd.DataFrame:
    """One row a start of one design, rule set and arm (every response off): `START_FILE_COLS`."""
    records = [x["rec"] for x in outs]
    ahead = p_months_ahead(records)
    t = R.start_table(design, arm, "off", outs)
    rows = []
    for x, (_, tr) in zip(outs, t.iterrows()):
        r = x["rec"]
        alt = r.get("alt") or {}
        nm = list(r["net_month"])
        fm = list(r["fees_month"])
        if len(nm) != MONTHS or len(fm) != MONTHS:
            raise ValueError(f"{design} {rules} {arm} start {r['start_day']}: {len(nm)} month-end nets, not {MONTHS}")
        rows.append({
            "design": design, "rules": rules, "arm": arm, "start_day": int(r["start_day"]),
            "start_date": str(r["start_date"]), "observed": int(r["observed"]),
            **{k: _join_ints(r[k]) for k in RECORD_LIST_COLS}, "pay_cash": _join_floats(r["pay_cash"]),
            "payouts": len(r["pay_days"]), **{k: _f(r[k]) for k in RECORD_FLOATS},
            **{f"net_month_{k}": _f(nm[k - 1]) for k in range(1, MONTHS + 1)},
            **{f"fees_month_{k}": _f(fm[k - 1]) for k in range(1, MONTHS + 1)},
            "exact_runs_differing": _join_ints(x.get("differs") or []),
            "alt": json.dumps(_jsonable(alt), sort_keys=True) if alt else "",
            "p_months_ahead": float(ahead.get(str(r["start_date"]), NAN)),
            **{k: float(tr[k]) for k in PATH_COLS},
        })
    return pd.DataFrame(rows, columns=list(START_FILE_COLS))


def records_from_frame(df: pd.DataFrame) -> list[dict[str, Any]]:
    """The U1 records (with their `alt`) of a per-start frame or of its text read back (`read_text_csv`)."""
    out = []
    for _, row in df.iterrows():
        rec = {"start_day": int(row["start_day"]), "start_date": str(row["start_date"]),
               "observed": int(row["observed"]),
               **{k: _split(row[k], int) for k in RECORD_LIST_COLS}, "pay_cash": _split(row["pay_cash"], float),
               **{k: _f(row[k]) for k in RECORD_FLOATS},
               "net_month": [_f(row[f"net_month_{k}"]) for k in range(1, MONTHS + 1)],
               "fees_month": [_f(row[f"fees_month_{k}"]) for k in range(1, MONTHS + 1)]}
        a = row["alt"]
        if isinstance(a, str) and a.strip():
            rec["alt"] = json.loads(a)
        out.append(rec)
    return out


def path_table(df: pd.DataFrame) -> pd.DataFrame:
    """The columns `extended.user_readings.path_rows` reads, from a per-start frame."""
    cols = ["start_day", "start_date", "observed", "first_pass", "spent_before_first_pass", "first_payout",
            "spent_before_first_payout", *PATH_COLS]
    t = df[cols].copy()
    t["start_date"] = t["start_date"].astype(str)
    return t


def _same(a: float, b: float, tol: float) -> bool:
    if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
        return True
    return abs(float(a) - float(b)) <= tol * max(1.0, abs(float(b)))


def rederive_problems(df: pd.DataFrame, srows: Sequence[Mapping[str, Any]], what: str, *,
                      tol: float = 1e-9) -> list[str]:
    """The scorecard, extra and path rows re-made from the per-start frame alone (`records_from_frame`, `path_table`;
    `extended.user_readings`' own functions) against the runner's `srows`: the same keys, every value to `tol`
    relative (absolute below 1; a blank equal to a blank) and every `n` exactly."""
    recs = records_from_frame(df)
    mine = (R.scorecard_rows(recs, R.Q44_BLOCKS) + R.extra_rows(recs, R.Q44_BLOCKS)       # W3.1: named
            + R.path_rows(path_table(df), R.Q44_BLOCKS))
    keep = ("scorecard", "extra", "path")
    key = lambda r: (r["section"], r["block"], r["measure"], r["stat"])          # noqa: E731
    theirs = {key(r): r for r in srows if r["section"] in keep}
    got = {key(r): r for r in mine}
    out = []
    if set(theirs) != set(got):
        a, b = sorted(set(theirs) - set(got)), sorted(set(got) - set(theirs))
        out.append(f"{what}: the re-made rows' keys differ (only the runner's: {a[:3]}; only the file's: {b[:3]})")
    for k in sorted(set(theirs) & set(got)):
        v, w = float(got[k]["value"]), float(theirs[k]["value"])
        if not _same(v, w, tol) or int(got[k]["n"]) != int(theirs[k]["n"]):
            out.append(f"{what}: {k} re-made from the file is {v} (n {got[k]['n']}), the runner's {w} "
                       f"(n {theirs[k]['n']})")
    return out


# ------------------------------------------------------------------------------------------------ C2: the paired rows


def _row(**k: Any) -> dict[str, Any]:
    return {"section": "paired", **k}


def paired_series(x: Mapping[str, float], y: Mapping[str, float]) -> tuple[list[str], np.ndarray, np.ndarray]:
    """(the common dates in order, x's and y's ahead averages there: months ahead over three)."""
    common = sorted(set(x) & set(y))
    return common, np.array([x[d] for d in common], float) / 3.0, np.array([y[d] for d in common], float) / 3.0


def paired_reading(x: Mapping[str, float], y: Mapping[str, float], h: int = P_HORIZON) -> dict[str, Any]:
    """RD-02 9.2 items 1-6 on the per-start difference x - y (ahead averages) over their common starts, in date order:
    the mean over every start, the kept windows' count and means, the sign count, n_eff, and -- with four kept windows
    and a spread -- the 90 % interval and its MDD; `describe`'s word otherwise."""
    from extended.user_measures import n_eff_bartlett

    dates, a, b = paired_series(x, y)
    d = a - b
    out: dict[str, Any] = {"n": len(d), "mean": float(d.mean()) if len(d) else NAN, "dates": dates,
                           "only_x": len(set(x) - set(y)), "only_y": len(set(y) - set(x))}
    if not len(d):
        out.update(word="no common start", n_w=0)
        return out
    wm, wa, wb = RD.window_means(d, h), RD.window_means(a, h), RD.window_means(b, h)
    out["n_w"] = int(wm.size)
    out["signs"] = RD.sign_count(wa, wb)
    out["n_eff"] = float(n_eff_bartlett(d, lag=int(h)))
    out["word"] = RD.describe(d, h)
    if out["word"] == "interval":
        out["interval"] = RD.t_interval(wm)
        out["mdd"] = RD.mdd(wm)
        out["kept_mean"] = float(wm.mean())
    return out


def paired_rows(ahead: Mapping[tuple[str, str, str, str], Mapping[str, float]], cards: Mapping[tuple, float],
                designs: Sequence[str], rule_sets: Sequence[str], arms: Sequence[str],
                honesty: Mapping[tuple[int, int], Mapping[str, Mapping[str, float]]] | None = None,
                h: int = P_HORIZON) -> tuple[list[dict[str, Any]], list[str], set[tuple[int, int]]]:
    """Section `paired`: each corrected rule set against `stage2` (`ahead[(design, rules, arm, block)]`: P's months
    ahead by start date), every design, arm and block. Returns (the rows, the refusing checks' problems, the honesty
    settings (h, n_w) the intervals need). `cards[(design, rules, arm, block)]` is the card's P: the paired mean over
    every start must equal the cards' difference, on the same starts (no start on one side only)."""
    rows, probs, need = [], [], set()
    for design in designs:
        for rules in rule_sets:
            if rules == REFERENCE_RULES:
                continue
            for arm in arms:
                for block, _ in BLOCKS:
                    k = (design, rules, arm, block)
                    k0 = (design, REFERENCE_RULES, arm, block)
                    if k not in ahead or k0 not in ahead:
                        continue
                    p = paired_reading(ahead[k], ahead[k0], h)
                    what = f"{design} {rules} against {REFERENCE_RULES} {arm} {block}"
                    if p["only_x"] or p["only_y"]:
                        probs.append(f"{what}: {p['only_x']} starts only in {rules}, {p['only_y']} only in "
                                     f"{REFERENCE_RULES} -- the pair is not on the same starts")
                    diff = cards.get(k, NAN) - cards.get(k0, NAN)
                    if p["n"] and not _same(p["mean"], diff, 1e-12):
                        probs.append(f"{what}: the paired mean {p['mean']} is not the cards' P difference {diff}")
                    base = dict(design=design, rules=rules, against=REFERENCE_RULES, arm=arm, block=block,
                                measure="P", n=int(p["n"]), h=int(h))
                    rows.append(_row(**base, stat="mean", value=p["mean"],
                                     note="over every start of the block: the cards' P difference"))
                    if not p["n"]:
                        rows.append(_row(**base, stat="interval", value=NAN, note=p["word"]))
                        continue
                    s = p["signs"]
                    rows += [_row(**base, stat="n_w", value=float(p["n_w"]),
                                  note=f"kept windows: every other {h}-start window from the block's first start"),
                             _row(**base, stat="sign_above", value=float(s[0])),
                             _row(**base, stat="sign_equal", value=float(s[1])),
                             _row(**base, stat="sign_below", value=float(s[2])),
                             _row(**base, stat="n_eff", value=p["n_eff"],
                                  note=f"Bartlett at lag {h} on every start's difference")]
                    if p["word"] != "interval":
                        rows.append(_row(**base, stat="interval", value=NAN, note=p["word"]))
                        continue
                    lo, hi = p["interval"]
                    rows += [_row(**base, stat="mdd", value=float(p["mdd"]),
                                  note="(t(0.95) + t(0.80)) x the kept windows' se: printed before the mean, 9.2 "
                                       "item 5"),
                             _row(**base, stat="kept_mean", value=p["kept_mean"]),
                             _row(**base, stat="ci90_low", value=float(lo)), _row(**base, stat="ci90_high",
                                                                               value=float(hi))]
                    setting = (int(h), int(p["n_w"]))
                    need.add(setting)
                    if honesty is not None and setting in honesty:
                        cov = honesty[setting]
                        c = {name: v["coverage"] for name, v in cov.items()}
                        rare = RD.rare_line(c, {n_: v["miss_above"] for n_, v in cov.items()},
                                            {n_: v["miss_below"] for n_, v in cov.items()})
                        lab = RD.label(c)
                        rows += [_row(**base, stat="interval_label", value=float(lab),
                                      note=("under-covers at this window count" if lab else "covers at this window "
                                            "count") + f" (gauss, ahead, paired below {RD.LABEL_FLOOR}: 1)"),
                                 _row(**base, stat="rare_coverage", value=rare["coverage"],
                                      note=f"if the difference is rare and lumpy: the lowest coverage, "
                                           f"{rare['shape']}; misses above {rare['miss_above']:.4f}, below "
                                           f"{rare['miss_below']:.4f}")]
    return rows, probs, need


def honesty(settings: Iterable[tuple[int, int]], seed: int = HONESTY_SEED, reps: int = HONESTY_SERIES
            ) -> dict[tuple[int, int], dict[str, dict[str, float]]]:
    """9.2 item 7 at each (h, n_w): every declared shape's coverage and misses, `reps` series a setting, each setting
    and shape from `pp_reading.honesty_rng(seed, shape index, h, n_w)`."""
    out = {}
    for h, n_w in sorted(set(settings)):
        cov = {}
        for i, (kind, p, s) in enumerate(RD.SHAPES):
            rng = RD.honesty_rng(int(seed), i, int(h), int(n_w))
            cov[RD.shape_name(kind, p, s)] = RD.coverage(kind, int(n_w), int(h), rng, int(reps), p=p, s=s)
        out[(int(h), int(n_w))] = cov
    return out


def honesty_rows(h: Mapping[tuple[int, int], Mapping[str, Mapping[str, float]]], seed: int, reps: int
                 ) -> list[dict[str, Any]]:
    rows = []
    for (hh, n_w), cov in sorted(h.items()):
        for name, v in cov.items():
            for stat in ("coverage", "miss_above", "miss_below"):
                rows.append({"section": "honesty", "measure": name, "stat": stat, "value": float(v[stat]),
                             "n": int(reps), "h": int(hh), "n_w": int(n_w),
                             "note": f"RD-02 9.2 item 7: {reps} zero-mean series; rng [{seed}, 1, shape, {hh}, {n_w}]"})
    return rows


# ------------------------------------------------------------------------------------------------ mdd_P (Q-16's)


def flip_signs(rng: Any, n: int, L: int, reps: int) -> np.ndarray:
    """(n, reps) signs: one fair sign per block of L consecutive starts, the blocks' phase random per replication
    (`scripts/q16_calibrate.py`'s `_flip_signs`, line for line)."""
    phase = rng.integers(0, L, size=reps)
    nb = (n + L) // L + 1
    sg = rng.choice(np.array([-1.0, 1.0]), size=(nb, reps))
    fid = (np.arange(n)[:, None] + phase[None, :]) // L
    return np.take_along_axis(sg, fid, axis=0)


def mdd_level(k: int = MDD_K) -> float:
    from extended import lift_bound as LB

    return float(LB.family_level(int(k)))


def mdd_p(d: Sequence[float], rng: Any, *, level: float | None = None, reps: int = MDD_REPS,
          batch: int = MDD_BATCH, power: float = MDD_POWER, L: int = MDD_FLIP_BLOCK) -> float | None:
    """The `power` quantile, over `reps` null replications (the series centred, its signs flipped in blocks of `L`
    starts), of `p_bound.mdd_draws(SHIPPED, ., level)`: the smallest difference added to every start the shipped
    statistic would carry. None for a series identically zero or shorter than `MDD_MIN_STARTS`; infinite where more
    than 1 - `power` of the replications carry no shift at all (`p_bound`: a flat-top variance not positive never
    carries)."""
    from extended import p_bound as PB

    x = np.asarray(d, float)
    if len(x) < MDD_MIN_STARTS or not np.any(x != 0):
        return None
    lev = mdd_level() if level is None else float(level)
    c = x - x.mean()
    parts, done = [], 0
    while done < int(reps):
        r = min(int(batch), int(reps) - done)
        D = c[:, None] * flip_signs(rng, len(c), int(L), r)
        parts.append(np.asarray(PB.mdd_draws(PB.SHIPPED, D, level=lev), float))
        done += r
    return float(np.quantile(np.concatenate(parts), float(power)))


def mdd_rng(design_index: int, rules_index: int, arm_index: int, seed: int = MDD_SEED) -> Any:
    return np.random.default_rng([int(seed), int(design_index), int(rules_index), int(arm_index)])


def mdd_note(level: float, reps: int = MDD_REPS) -> str:
    from extended import p_bound as PB

    return (f"Q-16's P comparison (extended.p_bound, E-035): the {MDD_POWER:.0%} quantile over {int(reps)} null "
            f"replications of {PB.SHIPPED}'s smallest carried shift at one-sided {level:.6g} (k = {MDD_K}); the "
            f"design's ahead average less {MDD_REFERENCE.upper().replace('P', 'P-')}'s on the same rule set and arm, "
            f"the judged block's common starts; the null centred and sign-flipped in blocks of {MDD_FLIP_BLOCK} "
            f"starts (scripts/q16_calibrate.py's real-null form)")


def fill_mdd_p(rows: list[dict[str, Any]], ahead: Mapping[tuple[str, str, str, str], Mapping[str, float]],
               designs: Sequence[str], rule_sets: Sequence[str], arms: Sequence[str], *, seed: int = MDD_SEED,
               reps: int = MDD_REPS) -> list[dict[str, Any]]:
    """Fill every `extra`/`mdd_P` row (blank since Q-17, `user_readings.MDD_NOTE`) in place: the judged block's value
    by `mdd_p` for each design but the reference, against it on the same rule set and arm; a blank with its reason
    otherwise. Returns what was computed, for the manifest."""
    level = mdd_level()
    done = []
    order = {d: i for i, d in enumerate(designs)}
    rorder = {r: i for i, r in enumerate(rule_sets)}
    aorder = {a: i for i, a in enumerate(arms)}
    for r in rows:
        if r.get("section") != "extra" or r.get("measure") != "mdd_P":
            continue
        design, rules, arm, block = r.get("design"), r.get("rules"), r.get("arm"), r.get("block")
        r["against"] = MDD_REFERENCE
        if design == MDD_REFERENCE:
            r.update(value=NAN, note="R* itself: mdd_P is a design's P against P-14's (Q-16's comparison)")
            continue
        if block != "judged":
            r.update(value=NAN, note="Q-16 calibrated the judged block's comparison only (E-035); not read on "
                                     f"the {block} block")
            continue
        k, k0 = (design, rules, arm, "judged"), (MDD_REFERENCE, rules, arm, "judged")
        if k not in ahead or k0 not in ahead:
            r.update(value=NAN, note=f"{MDD_REFERENCE} was not run on this rule set and arm (--check)")
            continue
        _, a, b = paired_series(ahead[k], ahead[k0])
        v = mdd_p(a - b, mdd_rng(order[design], rorder[rules], aorder[arm], seed), level=level, reps=reps)
        if v is None:
            why = (f"{len(a)} common starts: too few for Q-16's statistic (at least {MDD_MIN_STARTS})"
                   if len(a) < MDD_MIN_STARTS else "identical to P-14's on these starts: no MDD")
            r.update(value=NAN, n=int(len(a)), note=why)
        elif not math.isfinite(v):
            r.update(value=NAN, n=int(len(a)),
                     note=f"infinite: on more than {1 - MDD_POWER:.0%} of the null replications "
                          "the shipped statistic carries no shift at all (a flat-top variance not positive never "
                          "carries, extended.p_bound) -- no difference in P is detectable here; " + mdd_note(level, reps))
        else:
            r.update(value=float(v), n=int(len(a)), note=mdd_note(level, reps))
        done.append({"design": design, "rules": rules, "arm": arm, "n": int(len(a)),
                     "finite": bool(v is not None and math.isfinite(v)),
                     "rng": [int(seed), order[design], rorder[rules], aorder[arm]]})
    return done


# ------------------------------------------------------------------------------------------------ C7: the assumptions


def assumptions(jobs: Mapping[tuple[str, str], Mapping[str, Any]], rule_sets: Mapping[str, Any],
                fills_profile: str | None, payout_method: str = "aeropay") -> dict[str, Any]:
    """C7's assumptions, read from the U1 jobs' engine arguments (`jobs[(design, arm)]["args"]`, the
    `customer_slices.engine_args` form) and the rule sets: the fill model, the payout lag and spacing model, the
    no-closure state table, the move's latency, the response off."""
    payout = {}
    tables = {}
    for (design, arm), job in sorted(jobs.items()):
        path, draws = job["args"]["path"], job["args"]["draws"]
        proto = draws.get("protocol")
        rp = path.get("risk_policy")
        payout[f"{design}|{arm}"] = {
            "payout_method": payout_method, "payout_lag_days": int(path["payout_lag_days"]),
            "payout_timing": repr(path.get("payout_timing")),
            "payout_path": getattr(proto, "payout_path", None), "payout_frac": getattr(proto, "payout_frac", None),
            "keep_balance": getattr(proto, "keep_balance", None),
            "purchase_budget": _jsonable(path.get("purchase_budget")),
            "one_at_a_time_minutes": _jsonable(draws.get("one_at_a_time"))}
        tables[f"{design}|{arm}"] = getattr(rp, "id", None) if rp is not None else None
    lat = {n: {"breakeven_tie": getattr(r, "breakeven_tie", None), "breakeven_delay": getattr(r, "breakeven_delay",
                                                                                              None)}
           for n, r in rule_sets.items()}
    return {
        "fills": {"profile": fills_profile, "source": "vendor/stage2/config/fills.yaml meta.active_profile",
                  "meaning": "the fill model is ASSUMED, never measured (Stage 2 D-95): entries and exits as the walk "
                             "books them, costs at the stop (atlas_a3.fee_by_stop), a limit target filled at its "
                             "price"},
        "payout": {"by_design_arm": payout,
                   "lag": "each payout arrives payout_lag_days sessions after its request (user_journey."
                          "payout_arrivals; the lag from the verified ledger's payout method, customer_slices."
                          "engine_args)",
                   "spacing": "no assumed spacing: payouts are simulated on the campaign's clock by the engine "
                              "(Stage 2 D-18: dated payouts simulated, not a PayoutSchedule), each requested when the "
                              "protocol's payout path allows it (PAYOUT_PATHS), at payout_frac of the maximum and "
                              "never below keep_balance",
                   "paths": {k: PAYOUT_PATHS.get(str(k), "not described in propedge.campaign.protocols")
                             for k in sorted({str(v["payout_path"]) for v in payout.values()})}},
        "state_table": {"by_design_arm": tables,
                        "meaning": "the no-closure state table (a3_brk30_cb20.noclose_plan, pinned by D-509's "
                                   "hashes), solved at Stage 2's walk and frozen under every rule set here"},
        "breakeven_move": {"rule_sets": lat,
                           "latency": "stage2 and stop_first: the move takes effect on the session's open bar itself "
                                      "(zero latency, Stage 2's modelling); delay5 and both: decided on the open bar's "
                                      "open and in force from the first present bar opening five minutes after it -- "
                                      "Stage 2 D-266's five minutes from alert to order, for a move made by hand "
                                      "(E-012 (2), E-013 (2))"},
        "response": "every response off: 0 % payout denial (D-234), the placement off (D-289), no Focused Trader model",
    }


#: the payout paths as `propedge.campaign.protocols.Protocol`'s docstring describes them (vendored)
PAYOUT_PATHS = {"standard": "5 winning days >= $150 before each request",
                "consistency": "3 trading days, best <= 40 % of window net"}


def assumption_rows(a: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Section `assumptions`: one row an assumption, its statement as JSON in `note` (no value)."""
    return [{"section": "assumptions", "measure": k, "stat": "stated", "value": NAN,
             "note": json.dumps(_jsonable(v), sort_keys=True, default=str)} for k, v in a.items()]


def assumptions_note(a: Mapping[str, Any]) -> str:
    lags = sorted({v["payout_lag_days"] for v in a["payout"]["by_design_arm"].values()})
    tables = sorted({str(v) for v in a["state_table"]["by_design_arm"].values()})
    paths = "; ".join(f"{k}: {v}" for k, v in a["payout"]["paths"].items())
    return (f"Assumed: the fill profile {a['fills']['profile']!r} (never measured); payouts lagged "
            f"{', '.join(str(x) for x in lags)} session(s) after their request, spacing simulated by the engine (D-18), "
            f"no assumed schedule, requests on the payout path ({paths}); the no-closure state table "
            f"{', '.join(tables)}; the breakeven move at zero latency "
            f"under stage2 and stop_first, five minutes after the open (D-266) under delay5 and both; "
            f"{a['response']}.")


# ------------------------------------------------------------------------------------------------ C6: provenance


def git_state(root: Path = ROOT) -> dict[str, Any]:
    """The commit this run is made from and whether the tree is clean (`git status --porcelain` empty)."""
    def git(*a: str) -> str:
        return subprocess.run(["git", *a], cwd=root, capture_output=True, text=True).stdout.strip()

    status = git("status", "--porcelain")
    return {"commit": git("rev-parse", "HEAD") or None, "clean": not bool(status),
            "changed": len(status.splitlines()) if status else 0, "branch": git("rev-parse", "--abbrev-ref", "HEAD")
            or None}


def provenance_line(state: Mapping[str, Any], script: str, argv: Sequence[str]) -> str:
    import os

    return (f"provenance: commit {state['commit']} (clean {state['clean']}: {state['changed']} path(s) changed; "
            f"{state['branch']}); command: python {script} {' '.join(argv)}; clean-run marker "
            f"{os.environ.get('S2X_CLEAN_RUN')!r}; run id {os.environ.get('S2X_RUN_ID')!r}; python "
            f"{sys.version.split()[0]}")


def variant_params(design: str, rules: str, rule_set: Any, n_paths: int, starts: Any) -> dict[str, Any]:
    return {"study": "Q-132: the breakeven move's fidelity, second reading (Q-20's corrections)", "design": design,
            "rules": rules, "breakeven_tie": getattr(rule_set, "breakeven_tie", None),
            "breakeven_delay": getattr(rule_set, "breakeven_delay", None), "gate_paths": int(n_paths),
            "u1_starts": starts, "response": "off"}


def record_variants(target: Path, prereg_id: str, seed: int, variants: Sequence[tuple[str, str, dict]]) -> list[str]:
    """Each variant (design, rule set, its parameters) once into `target/variants.jsonl` through the vendored
    `VariantCounter` (append-only); returns the variant ids."""
    from propedge.backtest.harness import VariantCounter

    counter = VariantCounter(path=Path(target) / "variants.jsonl")
    ids = []
    for design, rules, params in variants:
        rec = counter.record(prereg_id=prereg_id, seed=int(seed), exploratory=True, params=dict(params),
                             label=f"{prereg_id}: {design} {rules}")
        ids.append(rec.variant_id)
    return ids


__all__ = ["SEED_BLOCK", "HONESTY_SEED", "MDD_SEED", "TEST_SEED", "SEED_ROLES", "P_HORIZON", "INTERVAL_LEVEL",
           "MIN_WINDOWS", "HONESTY_SERIES", "REFERENCE_RULES",
           "BLOCKS", "MDD_K", "MDD_POWER", "MDD_REPS", "MDD_MIN_STARTS", "MDD_FLIP_BLOCK", "MDD_REFERENCE", "START_FILE_COLS",
           "PATH_COLS", "read_text_csv", "p_months_ahead", "start_frame", "records_from_frame", "path_table",
           "rederive_problems", "paired_series", "paired_reading", "paired_rows", "honesty", "honesty_rows",
           "flip_signs", "mdd_level", "mdd_p", "mdd_rng", "mdd_note", "fill_mdd_p", "assumptions",
           "PAYOUT_PATHS", "assumption_rows", "assumptions_note", "git_state", "provenance_line", "variant_params",
           "record_variants"]
