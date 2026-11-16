"""RD-02's reading, run (`prereg/RD-02_payout_policy.md` sections 8, 9, 12 and 14; Q-105b): the cells x arms x blocks on
U1's start-day replay, the readings beside, the gates, 8.1 items 4 to 6, 8.2's oracles, 8.3's mechanics, 9.2's
uncertainty with the honesty table, the menu -- as three tables for `scripts/pp_reading.py` to write.

    from extended import use_vendored_stage2; use_vendored_stage2()
    from extended import pp_run as RUN
    tables = RUN.run_reading(RUN.RealInputs(), designs=("p14", "p16"))          # the lead's, from a clean run

**What runs, in the order 8.1 and 14 step 2 fix** (Q-102's m4). For each design: (a) `ref` at `off` on both arms, with
Q-94's recorder and the counters' channel on -- 8.1 item 2's repeat (the inputs' own reference comparison) and item 4
(every counter zero); (b) `ref` under `denial_10/25/50` and `rtp` on the verdict arm -- item 6 (the inputs' ladder
reference: Q-44's per-start file in the real run); (c) each new run (the three new cells; on P-14 also the three
rule-sensitivity runs) at `off` on both arms, recorded and counted, checked under item 5 (the recorder's per-start
checks: every routed trade is in the start's blocks) before anything of it is read, then its readings beside (policy
cells only, verdict arm); (d) the new cells' gates (500 paths at the base's registered seed, point and bound, and the
zero-edge twin), through `extended/gate.py` with the class and the counters. **Any failed check raises `Refused`: nothing
of a new run is computed past it, and nothing is written** (`scripts/pp_reading.py` writes only what returns).

**The readings** (9.1, 9.2) on all starts, the early and the late block, each measure at its own horizon
(`extended.pp_reading.HORIZONS`): the card (`u_select.scorecard`), each measure's distribution, and paired with the base
on the same starts -- the per-start difference's p10/p50/p90, the shares better, equal and worse (for a share ahead, the
four-way split), the mean, and 9.2's kept-window interval, sign count, n_eff and MDD with the honesty label and the
rare-shape line. A measure undefined on some starts of a block (a first pass never reached) gets its distribution and
shares only: the interval rests on consecutive starts.

**The honesty table** (9.2 item 7): at every (h, n_w) an interval is printed for, the 21 shapes' coverage and misses,
`HONESTY_SERIES` series a setting, from the declared seed (read from the pinned file's section 11, never written here),
keys `[seed, 1, shape, h, n_w]`.

**The menu** (9.1 item 10): each cell's headline paired readings with their labels, the stability flag, E-015's
limits (only those the caller names as approved before the run's commit), the count of intervals and the tenth
expected to exclude zero by chance, and the standing labels (`half` an assumption; `lock` under the placement "L1 on
Standard-path accounts only"; the Focused Trader models not read, `half` named; not modelled).
"""
from __future__ import annotations

import dataclasses
import hashlib
import re
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import numpy as np
import pandas as pd

from extended import ROOT, use_vendored_stage2

use_vendored_stage2()

from extended import payout_policy as PP  # noqa: E402
from extended import pp_reading as RD  # noqa: E402

DECLARATION = "prereg/RD-02_payout_policy.md"
PREREG_ID = "RD-02"
PIN_ROW = "E-082"
PURPOSES = ("payout_scorecard", "payout_ladder_beside", "payout_gate_beside")
DESIGNS = ("p14", "p16")
ARMS = ("verdict", "point")
NEW_CELLS = ("lock", "half", "lock_half")
SENSITIVITY_DESIGN = "p14"
BESIDE = ("denial_10", "denial_25", "denial_50", "rtp")
RECORD_COLUMNS = ("date", "entry_t", "exit_t", "at_cap", "kind")
BLOCKS = (("all", None), ("early", "early"), ("late", "late"))
HELD_SESSIONS = (63, 126, 252)
MINUTES_RELEASE_CT = "13:00"
CALENDARS = {"config/calendar_early_closes.csv": "72db4941f95320900aac29c6c047742da176cd9b55c925cc9275a18fb3e67fb2",
             "config/calendar_fomc_minutes.csv": "0350d41fe224909d93ae9211761e839c4925c231b83f039ccb92f1d8a4127ce7"}
#: the measures paired with the base (9.1 items 1, 2 and 4): (name, the per-start table's column or a function, the
#: horizon key, whether higher is better)
LOWER, HIGHER = "lower", "higher"
ADAPTER_FILES = ("extended/payout_policy.py", "extended/pp_reading.py", "extended/pp_run.py", "extended/user_beside.py",
                 "extended/gate.py", "extended/campaign.py", "extended/replay_records.py", "scripts/pp_reading.py")


class Refused(RuntimeError):
    """A check of 8.1 or 8.2 failed: the reading stops, nothing is written (the failure protocol applies)."""


# ------------------------------------------------------------------------------------------------ the declaration


def sha256_lf(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def declared_seed(role_prefix: str, root: Path = ROOT) -> int:
    """A seed of section 11 read from the pinned file itself: the row whose 'what it draws' starts with `role_prefix`
    and whose status is 'in use' (so no seed of the block is written in code, T-9). Refused if the file is not its
    pin's."""
    from extended import reader

    path = root / DECLARATION
    pins = reader.pins((root / "DECISIONS.md").read_text(encoding="utf-8")).get(DECLARATION) or set()
    if sha256_lf(path) not in pins:
        raise Refused(f"{DECLARATION} does not hash to its pin in DECISIONS.md")
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    sec = text.split("\n## 11.", 1)[1].split("\n## 12.", 1)[0]
    for seed, status, what in re.findall(r"^\|\s*(\d{8})\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", sec, re.MULTILINE):
        if status.strip().lower().startswith("in use") and what.strip().startswith(role_prefix):
            return int(seed)
    raise Refused(f"no seed in use for {role_prefix!r} in {DECLARATION}'s section 11")


def section_11(root: Path = ROOT) -> list[dict[str, Any]]:
    """Section 11's seed table as the pinned file states it (each seed, its status, what it draws), for the manifests;
    refused if the file is not its pin's."""
    declared_seed("9.2 item 7's honesty series", root)               # the pin checked
    text = (root / DECLARATION).read_text(encoding="utf-8").replace("\r\n", "\n")
    sec = text.split("\n## 11.", 1)[1].split("\n## 12.", 1)[0]
    return [{"seed": int(s), "status": st.strip().strip("*").strip(), "draws": w.strip()}
            for s, st, w in re.findall(r"^\|\s*(\d{8})\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", sec, re.MULTILINE)]


def calendar_frames(root: Path = ROOT) -> dict[str, pd.DataFrame]:
    """The two pinned calendars (E-029, E-050), each refused unless its LF sha256 is the one 4 and 8.3 cite."""
    out = {}
    for rel, want in CALENDARS.items():
        got = sha256_lf(root / rel)
        if got != want:
            raise Refused(f"{rel} hashes to {got}, not the pinned {want}")
        out[rel] = pd.read_csv(root / rel, comment="#", dtype=str)
    return out


# ------------------------------------------------------------------------------------------------ the inputs


class Inputs:
    """What the run reads, for one source (the real designs, or a synthetic campaign in the tests)."""

    def jobs(self, design: str) -> dict[str, dict[str, Any]]:
        raise NotImplementedError

    def identity_problems(self, design: str, arm: str, outs: list[dict[str, Any]]) -> list[str]:
        """8.1 item 2's repeat: the `ref` start rows against the reference."""
        raise NotImplementedError

    def ladder_problems(self, design: str, response: str, outs: list[dict[str, Any]]) -> list[str]:
        """8.1 item 6: `ref`'s readings beside against the reference."""
        raise NotImplementedError

    def gate_call(self, design: str, cell: str, twin: bool) -> dict[str, Any]:
        """The gate's keywords for a cell (`blocks` among them), its path sink and its label."""
        raise NotImplementedError

    def gate_pairing_rows(self, design: str, cell: str, twin: bool, g: dict[str, Any]) -> list[dict[str, Any]]:
        """9.1 item 8: the cell's gate paths beside the base's registered ones (none for a source without them)."""
        return []

    def n_paths(self) -> int:
        raise NotImplementedError


def cell_job(job: dict[str, Any], cell: str) -> dict[str, Any]:
    """A cell's job: the base's, with only the protocol's `payout_frac` replaced (`payout_policy.cell_protocol`)."""
    proto = PP.cell_protocol(job["args"]["draws"]["protocol"], cell)
    if proto is job["args"]["draws"]["protocol"]:
        return job
    args = {**job["args"], "draws": {**job["args"]["draws"], "protocol": proto}}
    return {**job, "args": args}


def runs_of(designs: Sequence[str], sensitivity_design: str = SENSITIVITY_DESIGN) -> list[tuple[str, str, str]]:
    """Section 12's 11 runs: (design, cell, held mode) -- the references, the new cells, P-14's rule sensitivity."""
    out = []
    for d in designs:
        out.append((d, "ref", "declared"))
        out += [(d, c, "declared") for c in NEW_CELLS]
        if d == sensitivity_design:
            out += [(d, c, "minimal") for c in NEW_CELLS]
    return out


# ------------------------------------------------------------------------------------------------ per start


def start_frame(design: str, arm: str, response: str, outs: Sequence[Mapping[str, Any]]) -> pd.DataFrame:
    """Q-17's per-start table (`extended.user_readings.start_table`) with the month-9 net and the per-start P."""
    from extended import user_readings as R

    t = R.start_table(design, arm, response, outs)
    t["net_month_9"] = [float(x["rec"]["net_month"][8]) if x["rec"]["net_month"][8] is not None else np.nan
                        for x in outs]
    t["p_start"] = t["months_ahead"] / 3.0
    for m in (1, 2, 3, 6, 9, 12):
        col = f"net_month_{m}"
        t[f"ahead_{m}"] = np.where(t[col].isna(), np.nan, (t[col] > 0).astype(float))
    return t


def records_of(t: pd.DataFrame) -> list[dict[str, Any]]:
    return [{"start_day": int(r.start_day), "start_date": str(r.start_date), "observed": int(r.observed)}
            for r in t.itertuples()]


MEASURES: tuple[tuple[str, str, str, str], ...] = (
    ("P", "p_start", "P", HIGHER),
    *((f"net_month_{m}", f"net_month_{m}", ("net_m%d" % m) if m <= 3 or m == 9 else f"share_m{m}", HIGHER)
      for m in (1, 2, 3, 6, 9, 12)),
    *((f"ahead_month_{m}", f"ahead_{m}", f"share_m{m}", HIGHER) for m in (1, 2, 3, 6, 9, 12)),
    ("sessions_to_first_pass", "first_pass", "first_pass_sessions", LOWER),
    ("cash_before_first_pass", "spent_before_first_pass", "first_pass_cash", LOWER),
    ("sessions_to_first_payout", "first_payout", "first_payout_sessions", LOWER),
    ("cash_before_first_payout", "spent_before_first_payout", "first_payout_cash", LOWER),
    ("sessions_to_break_even", "break_even_day", "break_even_sessions", LOWER),
    ("fell_back_below_zero", "fell_back", "fell_back", LOWER),
    ("deepest_fall_after_break_even", "deepest_fall_after_break_even", "deepest_fall", LOWER),
    ("share_months_positive", "share_months_positive", "positive_months", HIGHER),
    ("longest_months_without_payout", "longest_months_without_payout", "longest_no_payout_run", LOWER),
    ("sd_monthly_net", "sd_monthly_net", "monthly_net_spread", LOWER),
    ("payouts_per_month", "payouts_per_month", "payouts_per_month", HIGHER),
    ("largest_month_share", "largest_month_share", "largest_month_share", LOWER),
)


def _row(**kw: Any) -> dict[str, Any]:
    base = {"section": "", "design": "", "arm": "", "cell": "", "mode": "", "response": "off", "block": "",
            "measure": "", "stat": "", "value": np.nan, "n": 0, "h": 0, "note": ""}
    base.update(kw)
    return base


# ------------------------------------------------------------------------------------------------ the readings


def distribution_rows(t: pd.DataFrame, key: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    recs = records_of(t)
    for bname, which in BLOCKS:
        for name, col, hkey, _ in MEASURES:
            h = RD.horizon(hkey)
            sel = {r["start_day"] for r in RD.block(recs, which, hkey)}
            x = t.loc[t["start_day"].isin(sel), col].to_numpy(float)
            fin = x[np.isfinite(x)]
            for stat, v in (("mean", fin.mean() if fin.size else np.nan),
                            *((f"p{p}", np.percentile(fin, p) if fin.size else np.nan) for p in (10, 50, 90))):
                out.append(_row(section="scorecard", **key, block=bname, measure=name, stat=stat, value=float(v),
                                n=int(fin.size), h=h, note="" if fin.size == x.size else
                                f"{x.size - fin.size} starts undefined (never reached)"))
    return out


def card_rows(outs: Sequence[Mapping[str, Any]], key: dict[str, Any]) -> list[dict[str, Any]]:
    from propedge.research import u_select as US

    recs = [x["rec"] for x in outs]
    out = []
    for bname, which in BLOCKS:
        for k, v in US.scorecard(recs, which).items():
            out.append(_row(section="scorecard", **key, block=bname, measure=f"card_{k}", stat="value",
                            value=float(v["value"]), n=int(v["n"]), h=int(US.BY_KEY[k].horizon)))
    return out


def paired_rows(cell: pd.DataFrame, base: pd.DataFrame, key: dict[str, Any], honesty: dict) -> list[dict[str, Any]]:
    """9.1 item 4 and 9.2: each measure, cell less base on the same starts, per block."""
    from extended import user_measures as M

    out = []
    a = cell.set_index("start_day")
    b = base.set_index("start_day")
    common = sorted(set(a.index) & set(b.index))
    recs = records_of(base.set_index("start_day").loc[common].reset_index())
    for bname, which in BLOCKS:
        for name, col, hkey, direction in MEASURES:
            h = RD.horizon(hkey)
            days = [r["start_day"] for r in RD.block(recs, which, hkey)]
            x, y = a.loc[days, col].to_numpy(float), b.loc[days, col].to_numpy(float)
            ok = np.isfinite(x) & np.isfinite(y)
            d = x[ok] - y[ok]
            n = int(ok.sum())
            k = dict(section="paired", **key, block=bname, measure=name, h=h, n=n)
            if n == 0:
                out.append(_row(**k, stat="mean", value=np.nan, note="no common start with the measure defined"))
                continue
            better = (d > 0) if direction == HIGHER else (d < 0)
            worse = (d < 0) if direction == HIGHER else (d > 0)
            for stat, v in (("mean", d.mean()), ("p10", np.percentile(d, 10)), ("p50", np.percentile(d, 50)),
                            ("p90", np.percentile(d, 90)), ("share_better", better.mean()),
                            ("share_equal", (d == 0).mean()), ("share_worse", worse.mean())):
                out.append(_row(**k, stat=stat, value=float(v)))
            if name.startswith("ahead_month_"):
                xa, ya = x[ok] > 0.5, y[ok] > 0.5
                for stat, v in (("ahead_cell_not_base", (xa & ~ya).mean()), ("ahead_both", (xa & ya).mean()),
                                ("ahead_neither", (~xa & ~ya).mean()), ("ahead_base_not_cell", (~xa & ya).mean())):
                    out.append(_row(**k, stat=stat, value=float(v)))
            if not ok.all():
                out.append(_row(**k, stat="interval", value=np.nan,
                                note="not computed: the measure is undefined on some starts of the block, and the "
                                     "kept windows rest on consecutive starts (distribution and shares only)"))
                continue
            desc = RD.describe(d, h)
            wm_c, wm_b, wm = RD.window_means(x, h), RD.window_means(y, h), RD.window_means(d, h)
            sc = RD.sign_count(wm_c, wm_b)
            out += [_row(**k, stat="n_w", value=float(wm.size)), _row(**k, stat="sign_above", value=float(sc[0])),
                    _row(**k, stat="sign_equal", value=float(sc[1])), _row(**k, stat="sign_below", value=float(sc[2])),
                    _row(**k, stat="n_eff", value=float(M.n_eff_bartlett(d, lag=h)))]
            if desc != "interval":
                out.append(_row(**k, stat="interval", value=np.nan, note=desc))
                continue
            lo, hi = RD.t_interval(wm)
            mdd = RD.mdd(wm)
            out += [_row(**k, stat="mdd", value=float(mdd), note="printed before the mean, as 9.2 item 5 asks"),
                    _row(**k, stat="kept_mean", value=float(wm.mean())), _row(**k, stat="ci90_low", value=lo),
                    _row(**k, stat="ci90_high", value=hi)]
            honesty[(h, int(wm.size))] = True
            out.append(_row(**k, stat="interval_label", value=np.nan, note=f"pending honesty setting {h} {wm.size}"))
    return out


def honesty_table(settings: Sequence[tuple[int, int]], seed: int, reps: int) -> pd.DataFrame:
    """9.2 item 7: the 21 shapes' coverage and misses at each (h, n_w)."""
    rows = []
    for h, n_w in sorted(set(settings)):
        for i, (kind, p, s) in enumerate(RD.SHAPES):
            c = RD.coverage(kind, int(n_w), int(h), RD.honesty_rng(seed, i, h, n_w), int(reps), p=p, s=s)
            rows.append({"h": int(h), "n_w": int(n_w), "shape_index": i, "shape": RD.shape_name(kind, p, s), **c})
    return pd.DataFrame(rows)


def label_rows(paired: list[dict[str, Any]], hon: pd.DataFrame) -> None:
    """Fill each printed interval's label and rare-shape line from the honesty table (9.2 item 7)."""
    for r in paired:
        if r["stat"] != "interval_label":
            continue
        h, n_w = (int(v) for v in r["note"].rsplit(" ", 2)[-2:])
        sub = hon[(hon["h"] == h) & (hon["n_w"] == n_w)]
        cov = dict(zip(sub["shape"], sub["coverage"]))
        line = RD.rare_line(cov, dict(zip(sub["shape"], sub["miss_above"])), dict(zip(sub["shape"], sub["miss_below"])))
        lab = RD.label(cov)
        r["value"] = float(lab)
        r["note"] = (("under-covers at this window count" if lab else "covers near nominal at this window count")
                     + f"; lowest of gauss/ahead/paired {min(cov[k] for k in RD.LABEL_SHAPES):.3f}; if the "
                     f"difference is rare and lumpy: {line['shape']} covers {line['coverage']:.3f}, misses above "
                     f"{line['miss_above']:.3f}, below {line['miss_below']:.3f}")


# ------------------------------------------------------------------------------------------------ mechanics (8.3)


def mechanics_rows(design: str, arm: str, cell: str, mode: str, outs: list, base_outs: list, counts: dict,
                   recorder: Any, response: str, cal: dict[str, pd.DataFrame], dates: Sequence[str],
                   lag: int) -> list[dict[str, Any]]:
    key = dict(section="mechanics", design=design, arm=arm, cell=cell, mode=mode, response=response)
    out = []
    by_start = {int(x["rec"]["start_day"]): x["rec"] for x in outs}
    base = {int(x["rec"]["start_day"]): x["rec"] for x in base_outs}
    for h in HELD_SESSIONS:
        diff = []
        for s, r in by_start.items():
            b = base.get(s)
            if b is None or int(r["observed"]) < h:
                continue
            m = h // RD.MONTH
            same = (r["net_month"][:m] == b["net_month"][:m] and
                    [d for d in r["pay_days"] if d <= h] == [d for d in b["pay_days"] if d <= h] and
                    [d for d in r["pass_days"] if d <= h] == [d for d in b["pass_days"] if d <= h])
            diff.append(not same)
        out.append(_row(**key, block="all", measure=f"share_starts_differing_within_{h}", stat="share",
                        value=float(np.mean(diff)) if diff else np.nan, n=len(diff), h=h,
                        note="differs: a month-end net, a payout's or a pass's day up to session h"))
    tot = PP.total_counters(row for rows in counts.values() for row in rows)
    note = ("the minimal rescue: only the rescued reads were read under the rule; the unchanged and R-changed reads "
            "were answered with the firm's count (n4)") if mode == "minimal" else ""
    for k, v in tot.items():
        out.append(_row(**key, block="all", measure=k, stat="count", value=float(v), n=len(counts),
                        note=note if k.startswith("held_") and k != "held_closes" else
                        ("the engine's count, for any class" if k.startswith("cons_") else "")))
    for h in HELD_SESSIONS:
        held = [any(h in set(row["held_days"]) for row in rows) for s, rows in counts.items()
                if int(by_start.get(s, {}).get("observed", 0)) >= h]
        out.append(_row(**key, block="all", measure=f"share_starts_held_at_session_{h}", stat="share",
                        value=float(np.mean(held)) if held else np.nan, n=len(held), h=h))
    # the holiday-hours reach (E-029): requests at an early close, or at the last session before a scheduled holiday
    ec = cal["config/calendar_early_closes.csv"]
    early = set(ec.loc[ec["kind"].isin(["early_close", "holiday"]), "date"])
    holidays = set(ec.loc[ec["kind"] == "holiday", "date"])
    di = {d: i for i, d in enumerate(dates)}
    eve = {dates[i - 1] for d in holidays if d in di and di[d] > 0 for i in [di[d]]}
    n_req = n_hit = 0
    for s, r in by_start.items():
        for d in r["pay_days"]:
            k = s + int(d) - int(lag)                    # the request's session: the cash arrives `lag` sessions later
            if 0 <= k < len(dates):
                n_req += 1
                n_hit += int(dates[k] in early or dates[k] in eve)
    out.append(_row(**key, block="all", measure="requests_at_early_close_or_holiday_eve", stat="count",
                    value=float(n_hit), n=n_req, note="E-029's calendar; the request's session is the arrival less "
                                                      "the payout lag"))
    # an unnamed release (E-034, E-050): trades open at 13:00 CT on a minutes day, executed at the tier's allowance
    if recorder is not None:
        from propedge.campaign.flip import slot_from_ct

        t13 = slot_from_ct(MINUTES_RELEASE_CT)
        mins = set(cal["config/calendar_fomc_minutes.csv"]["release_date"])
        tr = recorder.trades(design, arm, response)
        if len(tr):
            open13 = tr["date"].astype(str).isin(mins) & (tr["entry_t"] < t13) & (tr["exit_t"] >= t13)
            out.append(_row(**key, block="all", measure="executed_open_at_minutes_release", stat="count",
                            value=float(open13.sum()), n=int(len(tr))))
            out.append(_row(**key, block="all", measure="executed_open_at_minutes_release_at_allowance", stat="count",
                            value=float((open13 & tr["at_cap"].astype(bool)).sum()), n=int(open13.sum()),
                            note="timed by each block's single logged exit (exit_t)"))
    return out


def offered_minutes_rows(design: str, job: dict[str, Any], cal: dict[str, pd.DataFrame]) -> list[dict[str, Any]]:
    from propedge.campaign.flip import slot_from_ct

    t13 = slot_from_ct(MINUTES_RELEASE_CT)
    mins = set(cal["config/calendar_fomc_minutes.csv"]["release_date"])
    n = 0
    for d, b in zip(job["dates"], job["blocks"]):
        if str(d) in mins and b.entry_t is not None and b.exit_t is not None:
            n += int(np.sum((np.asarray(b.entry_t) < t13) & (np.asarray(b.exit_t) >= t13)))
    voided = ("2020-07-01", "2025-06-30", "2025-07-01")
    rows = [_row(section="mechanics", design=design, measure="offered_open_at_minutes_release", stat="count",
                 value=float(n), note="the stream's own offers (the same in every cell)")]
    di = {str(d): i for i, d in enumerate(job["dates"])}
    for v in voided:
        for h in RD.HORIZON_SET:
            if v in di:
                k = sum(1 for s in range(len(job["dates"])) if s <= di[v] < s + h)
                rows.append(_row(section="mechanics", design=design, measure=f"starts_whose_window_holds_{v}",
                                 stat="count", value=float(k), h=h, note="E-029's voided day: listed, never voided here"))
    return rows


def check_times(design: str, job: dict[str, Any], lo_ct: str, hi_ct: str) -> list[str]:
    """The blocks' entry times are on the engine's clock (minutes since 17:00 CT, D-345 (7)): every offered entry
    between `lo_ct` and `hi_ct`, or the minutes count's clock is wrong (refused)."""
    from propedge.campaign.flip import slot_from_ct

    lo, hi = slot_from_ct(lo_ct), slot_from_ct(hi_ct)
    bad = sum(int(np.sum((np.asarray(b.entry_t) < lo) | (np.asarray(b.entry_t) > hi)))
              for b in job["blocks"] if b.entry_t is not None)
    return [] if not bad else [f"{design}: {bad} offered entries outside {lo_ct}-{hi_ct} CT on the engine's clock"]


# ------------------------------------------------------------------------------------------------ the run


def run_reading(inputs: Inputs, *, designs: Sequence[str] = DESIGNS, starts: int | None = None, workers: int = 1,
                honesty_reps: int = RD.HONESTY_SERIES, honesty_seed: int | None = None, approved_limits: Sequence[
                    dict[str, Any]] = (), gate: bool = True, time_window: tuple[str, str] | None = None,
                sensitivity_design: str = SENSITIVITY_DESIGN, root: Path = ROOT,
                log: Callable[[str], None] = print) -> dict[str, Any]:
    """The whole reading; raises `Refused` at the first failed check (nothing returned, so nothing written)."""
    import user_journey as UJ

    from extended import replay_records as RRec
    from extended import user_beside as B

    seed = declared_seed("9.2 item 7's honesty series", root) if honesty_seed is None else int(honesty_seed)
    cal = calendar_frames(root)
    rows: list[dict[str, Any]] = []
    gate_rows: list[pd.DataFrame] = []
    counts_all: dict[tuple, dict] = {}
    honesty: dict = {}
    run_list = runs_of(designs, sensitivity_design)
    for design in designs:
        jobs = inputs.jobs(design)
        frames: dict[tuple, pd.DataFrame] = {}
        outs_of: dict[tuple, list] = {}
        if time_window is not None:
            for arm in ARMS:
                probs = check_times(design, jobs[arm], *time_window)
                if probs:
                    raise Refused("; ".join(probs))
        rows += offered_minutes_rows(design, jobs["verdict"], cal)
        # (a) ref at off, both arms, recorded and counted: items 2's repeat and 4
        for arm in ARMS:
            job = jobs[arm]
            chosen = UJ.start_choice(len(job["blocks"]), starts)
            rec, cnt = RRec.ReplayRecorder(columns=RECORD_COLUMNS), PP.ReplayCounters()
            outs = B.run_starts(design, arm, B.BY_NAME["off"], job, chosen, workers, funded_account_cls=PP.REF_CLASS,
                                recorder=rec, counters=cnt)
            probs = inputs.identity_problems(design, arm, outs) + [f"recorder: {p}" for p in rec.problems()]
            tot = PP.lever_totals(r for v in cnt.starts(design, arm, "off").values() for r in v)
            if any(tot.values()):
                probs.append(f"8.1 item 4: the levers are not off in ref ({tot})")
            probs += read_check(cnt, design, arm, "off", job)
            rows.append(_row(section="identity", design=design, arm=arm, cell="ref", measure="8.1 items 2 and 4",
                             stat="holds", value=float(not probs), n=len(outs), note="; ".join(probs[:4])))
            if probs:
                raise Refused(f"{design} {arm} ref: " + "; ".join(probs[:6]))
            log(f"identity HOLDS: {design} {arm} ref (8.1 items 2's repeat and 4), {len(outs)} starts")
            outs_of[(arm, "ref", "declared", "off")] = outs
            frames[(arm, "ref", "declared", "off")] = start_frame(design, arm, "off", outs)
            counts_all[(design, arm, "ref", "declared", "off")] = cnt.starts(design, arm, "off")
            rows += mechanics_rows(design, arm, "ref", "declared", outs, outs, cnt.starts(design, arm, "off"), rec,
                                   "off", cal, jobs[arm]["dates"], int(job["args"]["path"]["payout_lag_days"]))
        # (b) ref beside, verdict arm: item 6
        for rname in BESIDE:
            job = jobs["verdict"]
            chosen = UJ.start_choice(len(job["blocks"]), starts)
            cnt = PP.ReplayCounters()
            outs = B.run_starts(design, "verdict", B.BY_NAME[rname], job, chosen, workers,
                                funded_account_cls=PP.REF_CLASS, counters=cnt)
            probs = inputs.ladder_problems(design, rname, outs)
            tot = PP.lever_totals(r for v in cnt.starts(design, "verdict", rname).values() for r in v)
            if any(tot.values()):                        # the levers' own counts; the cons_* are the engine's (m4)
                probs.append(f"8.1 item 4 under {rname}: the levers are not off in ref ({tot})")
            rows.append(_row(section="identity", design=design, arm="verdict", cell="ref", response=rname,
                             measure="8.1 item 6", stat="holds", value=float(not probs), n=len(outs),
                             note="; ".join(probs[:4])))
            if probs:
                raise Refused(f"{design} ref {rname}: " + "; ".join(probs[:6]))
            outs_of[("verdict", "ref", "declared", rname)] = outs
            frames[("verdict", "ref", "declared", rname)] = start_frame(design, "verdict", rname, outs)
        log(f"identity HOLDS: {design} ref beside (8.1 item 6)")
        # (c) each new run: item 5 first, then its readings and its readings beside
        for d, cell, mode in run_list:
            if d != design or cell == "ref":
                continue
            cls = PP.cell_class(cell, mode)
            for arm in ARMS:
                job = cell_job(jobs[arm], cell)
                chosen = UJ.start_choice(len(job["blocks"]), starts)
                rec, cnt = RRec.ReplayRecorder(columns=RECORD_COLUMNS), PP.ReplayCounters()
                outs = B.run_starts(design, arm, B.BY_NAME["off"], job, chosen, workers, funded_account_cls=cls,
                                    recorder=rec, counters=cnt)
                probs = [f"8.1 item 5 (recorder): {p}" for p in rec.problems()]
                probs += [f"the held-state rule (m2): {p}" for p in read_check(cnt, design, arm, "off", job)]
                rows.append(_row(section="identity", design=design, arm=arm, cell=cell, mode=mode,
                                 measure="8.1 item 5", stat="holds", value=float(not probs), n=len(outs),
                                 note="; ".join(probs[:4])))
                if probs:
                    raise Refused(f"{design} {arm} {cell} ({mode}): " + "; ".join(probs[:6]))
                outs_of[(arm, cell, mode, "off")] = outs
                frames[(arm, cell, mode, "off")] = start_frame(design, arm, "off", outs)
                counts_all[(design, arm, cell, mode, "off")] = cnt.starts(design, arm, "off")
                rows += mechanics_rows(design, arm, cell, mode, outs, outs_of[(arm, "ref", "declared", "off")],
                                       cnt.starts(design, arm, "off"), rec, "off", cal, job["dates"],
                                       int(job["args"]["path"]["payout_lag_days"]))
                rows += oracle_rows(design, arm, cell, mode, outs)
            if mode == "declared":
                for rname in BESIDE:
                    job = cell_job(jobs["verdict"], cell)
                    chosen = UJ.start_choice(len(job["blocks"]), starts)
                    cnt = PP.ReplayCounters()
                    outs = B.run_starts(design, "verdict", B.BY_NAME[rname], job, chosen, workers,
                                        funded_account_cls=cls, counters=cnt)
                    rp = read_check(cnt, design, "verdict", rname, job)
                    if rp:
                        raise Refused(f"{design} {cell} {rname}: the held-state rule (m2): " + "; ".join(rp[:4]))
                    outs_of[("verdict", cell, mode, rname)] = outs
                    frames[("verdict", cell, mode, rname)] = start_frame(design, "verdict", rname, outs)
                    counts_all[(design, "verdict", cell, mode, rname)] = cnt.starts(design, "verdict", rname)
                    if rname == "rtp":
                        rows += mechanics_rows(design, "verdict", cell, mode, outs,
                                               outs_of[("verdict", "ref", "declared", "rtp")],
                                               cnt.starts(design, "verdict", rname), None, rname, cal,
                                               job["dates"], int(job["args"]["path"]["payout_lag_days"]))
            log(f"read: {design} {cell} ({mode})")
        # the readings: each frame's card and distributions; each cell paired with its base
        for (arm, cell, mode, rname), t in frames.items():
            key = dict(design=design, arm=arm, cell=cell, mode=mode, response=rname)
            rows += card_rows(outs_of[(arm, cell, mode, rname)], key)
            rows += distribution_rows(t, key)
            if cell != "ref":
                base = frames[(arm, "ref", "declared", rname)]
                rows += paired_rows(t, base, key, honesty)
                rows += diverge_rows(outs_of[(arm, cell, mode, rname)], outs_of[(arm, "ref", "declared", rname)],
                                     key)
        # (d) the new cells' gates: point and bound, and the zero-edge twin
        if gate:
            for cell in NEW_CELLS:
                for twin in (False, True):
                    g = inputs.gate_call(design, cell, twin)
                    from extended import gate as XG

                    cnt = PP.GateCounters()
                    kw = dict(g["kw"])
                    seen: list = []
                    orig = kw.get("path_hook")

                    def hook(shift, p, paths, _orig=orig, _seen=seen):
                        if shift == "point":
                            _seen.extend([list(x.funded) for x in paths])
                        return _orig(shift, p, paths) if _orig is not None else {}

                    kw["path_hook"] = hook
                    df, passed = XG.run_gate(kw.pop("blocks"), workers=int(workers), funded_account_cls=PP.cell_class(
                        cell), counters=cnt, **kw)
                    g = {**g, "sink_paths": seen}
                    rows += inputs.gate_pairing_rows(design, cell, twin, g)
                    df = df.copy()
                    df.insert(0, "twin", twin)
                    df.insert(0, "cell", cell)
                    df.insert(0, "design", design)
                    gate_rows.append(df)
                    rows += gate_oracle_rows(design, cell, twin, g, cnt)
                log(f"gate: {design} {cell} (point, bound, zero-edge twin)")
    # the honesty table at every setting an interval was printed for, then the labels
    hon = honesty_table([k for k in honesty], seed, honesty_reps)
    paired = [r for r in rows if r["section"] == "paired"]
    label_rows(paired, hon)
    rows += [_row(section="coverage", h=int(r.h), n=int(r.n_w), measure=r.shape, stat=s, value=float(getattr(r, s)),
                  note=f"shape {r.shape_index}; {honesty_reps} series; seed key [declared, 1, {r.shape_index}, {r.h}, "
                       f"{r.n_w}]") for r in hon.itertuples() for s in ("coverage", "miss_above", "miss_below")]
    reading = pd.DataFrame(rows)
    menu = menu_table(reading, approved_limits)
    return {"reading": reading, "gate": pd.concat(gate_rows, ignore_index=True) if gate_rows else pd.DataFrame(),
            "menu": menu, "honesty_seed": seed, "honesty_settings": sorted(honesty), "runs": run_list}


def read_check(cnt: Any, design: str, arm: str, response: str, job: dict[str, Any]) -> list[str]:
    """Q-106's m2: on every start, each held close the account outlives is followed by exactly one held read (the
    held-state rule fired where it must); the start's last session is its long replay's."""
    n = len(job["blocks"])
    out = []
    for s, rows in cnt.starts(design, arm, response).items():
        out += [f"start {s}: {p}" for p in PP.read_problems(rows, min(252, n - int(s)))]
    return out


def oracle_rows(design: str, arm: str, cell: str, mode: str, outs: list) -> list[dict[str, Any]]:
    """8.2 on the replay: every payout's cash is the split of a request within its bounds less the fee -- read back
    from each start's payouts (the request is cash plus fee over the split)."""
    r = PP.ledger_rules()
    split, fee, pmin, cap = float(r.profit_split), float(r.payout_fee), float(r.payout_min), float(r.std_cap)
    bad = 0
    n = 0
    for x in outs:
        for c in x["rec"]["pay_cash"]:
            req = (float(c) + fee) / split
            n += 1
            bad += int(not (pmin - 1e-6 <= req <= cap + 1e-6))
    if bad:
        raise Refused(f"8.2: {design} {arm} {cell} ({mode}): {bad} of {n} payouts outside the request's bounds")
    return [_row(section="oracle", design=design, arm=arm, cell=cell, mode=mode, measure="payouts within the bounds",
                 stat="holds", value=1.0, n=n)]


def gate_oracle_rows(design: str, cell: str, twin: bool, g: dict[str, Any], cnt: Any) -> list[dict[str, Any]]:
    """8.2 on the gate's zero-edge twin: the mean gross payouts per funded account within the start's cushion beyond
    three standard errors; on every gate, `lock`'s first payouts never below the lock (the class's counters)."""
    rows = []
    if twin:
        gross = [float(f.gross_paid) for p in g["sink_paths"] for f in p]
        if gross:
            cushion = PP.lock_balance()
            m, se = float(np.mean(gross)), float(np.std(gross, ddof=1) / np.sqrt(len(gross))) if len(gross) > 1 else 0.0
            if m > cushion + 3.0 * se:
                raise Refused(f"8.2: {design} {cell} twin: mean gross payout {m:.1f} exceeds {cushion:.0f} + 3 se")
            rows.append(_row(section="oracle", design=design, cell=cell, measure="zero-edge twin martingale bound",
                             stat="mean_gross_per_funded_account", value=m, n=len(gross),
                             note=f"bound {cushion:.0f} + 3 x {se:.1f} (the tolerance: three standard errors)"))
    return rows


def diverge_rows(outs: list, base_outs: list, key: dict[str, Any]) -> list[dict[str, Any]]:
    """9.1 item 6: what diverges, cell against base, summed over starts (each start's long replay)."""
    def tot(xs):
        c = Counter()
        for x in xs:
            r = x["rec"]
            c["passes"] += len(r["pass_days"])
            c["funded_activated"] += len(r["funded_days"])
            c["payouts"] += len(r["pay_days"])
            c["payout_cash"] += float(sum(r["pay_cash"]))
            fm = [v for v in r["fees_month"] if v is not None and np.isfinite(v)]
            c["fees_to_last_month"] += float(fm[-1]) if fm else 0.0
        return c
    a, b = tot(outs), tot(base_outs)
    return [_row(section="diverge", **key, block="all", measure=k, stat="cell_less_base", value=float(a[k] - b[k]),
                 n=len(outs)) for k in sorted(set(a) | set(b))]


GUARDED = ("P", "card_S1", "card_S3a", "card_S3b", "card_S3c", "card_S4a", "card_S4b", "card_S5a", "card_S5b",
           "card_S5c")


def menu_table(reading: pd.DataFrame, approved_limits: Sequence[dict[str, Any]]) -> pd.DataFrame:
    """9.1 item 10: each cell's headline and its flags; the counts; the standing labels."""
    rows = []
    p = reading[reading["section"] == "paired"]
    n_int = int(((p["stat"] == "ci90_low")).sum())
    for (design, arm, cell, mode, resp), g in p.groupby(["design", "arm", "cell", "mode", "response"], sort=True):
        def val(block, measure, stat):
            s = g[(g["block"] == block) & (g["measure"] == measure) & (g["stat"] == stat)]
            return float(s["value"].iloc[0]) if len(s) else np.nan
        early, late = val("early", "P", "mean"), val("late", "P", "mean")
        flag = bool(np.isfinite(early) and np.isfinite(late) and np.sign(early) * np.sign(late) < 0)
        lab = g[(g["block"] == "all") & (g["measure"] == "P") & (g["stat"] == "interval_label")]
        labels = ["described, not carried"]
        if PP.CELL_LEVERS.get(cell, ("", ""))[1] == "half":
            labels.append("half: the request amount is an assumption (E-034)")
        if resp == "rtp" and PP.CELL_LEVERS.get(cell, ("", ""))[0] == "lock":
            labels.append("L1 on Standard-path accounts only")
        if mode == "minimal":
            labels.append("rule sensitivity: the minimal rescue, never on the menu")
        rows.append({"design": design, "arm": arm, "cell": cell, "mode": mode, "response": resp,
                     "P_mean_difference": val("all", "P", "mean"), "P_ci90_low": val("all", "P", "ci90_low"),
                     "P_ci90_high": val("all", "P", "ci90_high"), "P_mdd": val("all", "P", "mdd"),
                     "P_label": lab["note"].iloc[0] if len(lab) else "",
                     "stable_across_blocks": not flag, "flag": "not stable across blocks" if flag else "",
                     "limits": "; ".join(str(x) for x in approved_limits) if approved_limits else
                               "none approved before the run's commit: the menu is read without flags",
                     "labels": "; ".join(labels)})
    m = pd.DataFrame(rows)
    standing = {
        "intervals_printed": n_int,
        "intervals_expected_to_exclude_zero_by_chance": n_int / 10.0,
        "note_intervals": "each a marginal 90 % interval, none simultaneous; a tenth would exclude zero by chance "
                          "alone were there no effect anywhere -- a count, not a level and not a correction",
        "note_focused_trader": "the Focused Trader models are not read for any cell (E-059 (2)); for half, the lever "
                               "that keeps accounts alive, there is no Focused Trader reading",
        "note_not_modelled": "a user who stops when their own money runs out; the user's time; taxes; payouts "
                             "unavailable in holiday hours; the move to a Live Funded Account; Topstep's unstated news "
                             "rules (which releases count, holding through one, the GDP minute); the Focused Trader "
                             "Program for any policy cell, half named",
    }
    for k, v in standing.items():
        m[k] = v
    return m


def adapter_provenance(root: Path = ROOT, strict: bool = True) -> dict[str, Any]:
    """m7: the commit actually run and each adapter file's blob id there; refused (`strict`, the real run) if any is
    changed in the tree, else the changes listed (the synthetic run, before a commit)."""
    import subprocess

    def git(*a: str) -> str:
        return subprocess.run(["git", *a], cwd=root, capture_output=True, text=True).stdout.strip()

    out = {"commit": git("rev-parse", "HEAD"), "blobs": {}}
    for rel in ADAPTER_FILES:
        out["blobs"][rel] = git("rev-parse", f"HEAD:{rel}") or None
    dirty = git("status", "--porcelain", "--", *ADAPTER_FILES)
    if dirty and strict:
        raise Refused(f"the adapter files are changed in the tree: {dirty[:200]}")
    out["changed_in_tree"] = dirty.splitlines() if dirty else []
    return out


class RealInputs(Inputs):
    """P-14's and P-16's registered designs, read through Stage 2's own builders (the lead's run, from a clean
    checkout, its reads authorised first): U1's jobs (`identity/user_beside_identity.py`'s `build`), U1's file for 8.1
    item 2's repeat, Q-44's per-start file for item 6, and the registered gate calls (`identity/pp_identity.py`'s)."""

    def __init__(self, starts: int | None = None, n_paths: int = 500):
        self.starts = starts
        self._n_paths = int(n_paths)
        self._jobs: dict[str, Any] = {}
        self._gate: dict[str, Any] = {}
        self._q44: pd.DataFrame | None = None

    def n_paths(self) -> int:
        return self._n_paths

    def jobs(self, design: str) -> dict[str, dict[str, Any]]:
        import user_beside_identity as UI

        from propedge import RESULTS_DIR

        jobs, c, probs = UI.build(RESULTS_DIR, design)
        if probs:
            raise Refused(f"{design}: the builder's own identities fail: {probs[:4]}")
        self._jobs[design] = (jobs, c, UI.u1_reference(RESULTS_DIR, [design]))
        return jobs

    def identity_problems(self, design: str, arm: str, outs: list[dict[str, Any]]) -> list[str]:
        import user_beside_identity as UI

        jobs, c, ref = self._jobs[design]
        return UI.u1_compare_outs(design, c, arm, outs, ref, len(jobs[arm]["blocks"]), self.starts)

    def ladder_problems(self, design: str, response: str, outs: list[dict[str, Any]]) -> list[str]:
        """Q-44's `results/user_beside_starts.csv` rows for the design, the verdict arm and the response, start for
        start, every column that file writes, at its precision (money to the cent)."""
        from extended import user_readings as R
        from extended.results import read_result

        if self._q44 is None:
            self._q44 = read_result(ROOT / "results" / "user_beside_starts.csv")
        f = self._q44
        theirs = f[(f["design"] == design) & (f["arm"] == "verdict") & (f["response"] == response)]
        mine = R.rounded(R.start_table(design, "verdict", response, outs))
        theirs = theirs.set_index("start_day").loc[[int(s) for s in mine["start_day"]]].reset_index()
        probs = []
        for col in R.START_COLS:
            a, b = mine[col].to_numpy(), theirs[col].to_numpy()
            if mine[col].dtype.kind in "fi":
                same = np.isclose(a.astype(float), b.astype(float), rtol=0, atol=1e-9, equal_nan=True)
            else:
                same = np.array([str(x) == str(y) for x, y in zip(a, b)])
            if not same.all():
                probs.append(f"{design} {response}: {col} differs from Q-44's file on {int((~same).sum())} starts")
        return probs

    def _gate_inputs(self, design: str) -> dict[str, Any]:
        if design in self._gate:
            return self._gate[design]
        import a3_brk30 as B
        import a3_brk30_cb20 as C
        import atlas_a3 as A
        import rc_screen as S
        import score_fv3_grid as gf
        import stage2_identity as SI

        if design == "p14":
            I = S.inputs()
            L = I["L"]
            t, days = B.cell_trades(L)
            seed, gap, budget = S.SEED, S.STRICT_GAP, S.BUDGET
        else:
            import rc150_dev_test as P
            import rc_dev_test as D

            sp = P.SPEC
            I, b = sp.build()
            L = I["L"]
            t, days = b["cells"][sp.cell]["trades"], b["days"]
            if D.trades_hash(t) != sp.trades_sha256:
                raise Refused(f"P-16's trades hash is not the pinned {sp.trades_sha256}")
            seed, gap, budget = SI.P16_SEED, C.STRICT_GAP, C.BUDGET
        cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
        keys = B.rrs(t)
        _, e_by, lb_by, _, _ = A.bounds(t, days, keys, cfg)
        blocks, n_used = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
        if n_used != len(t):
            raise Refused("the blocks hold a different number of trades")
        g = {"A": A, "I": I, "fcfg": fcfg, "tv": tv, "e_by": e_by, "lb_by": lb_by, "blocks": blocks, "seed": seed,
             "gap": gap, "budget": budget, "cap": B.capacity(t, fcfg)}
        self._gate[design] = g
        return g

    def gate_call(self, design: str, cell: str, twin: bool) -> dict[str, Any]:
        import fv3d_lever_test as lt
        import portfolio_stage as ps

        g = self._gate_inputs(design)
        fcfg = g["fcfg"]
        blocks, e_by, lb_by = g["blocks"], g["e_by"], g["lb_by"]
        if twin:                                         # the zero-edge twin, as atlas_a3.campaign builds it
            fr = float(fcfg["state_policy"]["fresh"]["funded_rr"])
            blocks = ps.zero_edge_blocks(blocks, e_by, fr)
            e_by = lb_by = {k: 0.0 for k in g["e_by"]}
        sink: list[dict] = []
        pc = fcfg["portfolio"]
        inner = ps.composed_hook({"margin": float(pc["margin"]), "block_days": int(pc["block_days"])}, sink=sink)
        hook = lt.lever_hook(inner)
        label = f"{design}_{cell}{'_twin' if twin else ''}"
        ps._label(inner, label)
        kw = g["A"].gate_kwargs(blocks, fcfg, g["tv"], g["I"]["plan"], e_by, lb_by, hook, seed=g["seed"],
                                n_paths=self._n_paths, horizon=int(fcfg["gate"]["campaign"]["horizon_days"]),
                                capacity=g["cap"], levels=(0.0,), rtp=False, one_at_a_time=g["gap"],
                                purchase_budget=g["budget"])
        kw["protocol"] = PP.cell_protocol(kw["protocol"], cell)
        return {"kw": kw, "sink": sink, "label": label}

    def gate_pairing_rows(self, design: str, cell: str, twin: bool, g: dict[str, Any]) -> list[dict[str, Any]]:
        """The cell's paths (its hook's sink) against the base's registered gate paths, path for path (the same seed,
        so the same day draws): each `zero_edge_decomposition.PATH_COLS` column's mean over paths, the cell's, the
        base's and their difference, point and bound. The twin has no registered twin here: its own means alone."""
        import stage2_identity as SI
        import zero_edge_decomposition as zd

        from propedge import RESULTS_DIR
        from propedge.reporting.results import read_result

        import rc_screen as S

        rows = []
        mine = pd.DataFrame([r for r in g["sink"] if r.get("run") == g["label"]
                             and float(r.get("enforcement_p", 0.0)) == 0.0])
        ref = read_result(RESULTS_DIR / (S.P14_PATHS if design == "p14" else SI.P16_PATHS))
        theirs_run = "zero_edge_twin" if twin else "gate"
        for shift in (("point",) if twin else ("point", "lower_bound")):
            a = mine[mine["shift"] == shift].sort_values("path").reset_index(drop=True) if len(mine) else mine
            b = ref[(ref["run"].astype(str) == theirs_run) & (ref["shift"].astype(str) == shift)
                    & np.isclose(ref["enforcement_p"].astype(float), 0.0)].sort_values("path").head(len(a))
            b = b.reset_index(drop=True)
            for col in zd.PATH_COLS:
                if col not in a:
                    continue
                x = pd.to_numeric(a[col], errors="coerce").to_numpy(float)
                k = dict(section="gate", design=design, cell=cell, mode="declared", block=shift, measure=col,
                         n=int(len(a)), note="the zero-edge twin" if twin else "")
                rows.append(_row(**k, stat="cell_mean", value=float(np.nanmean(x)) if x.size else np.nan))
                if len(b) == len(a) and col in b and len(a):
                    y = pd.to_numeric(b[col], errors="coerce").to_numpy(float)
                    rows += [_row(**k, stat="base_registered_mean", value=float(np.nanmean(y))),
                             _row(**k, stat="cell_less_base_mean", value=float(np.nanmean(x - y)))]
                else:
                    rows.append(_row(**k, stat="base_registered_mean", value=np.nan,
                                     note=f"no registered {theirs_run} run of {len(a)} paths to pair with"))
        return rows


__all__ = ["RealInputs", "DECLARATION", "PREREG_ID", "PIN_ROW", "PURPOSES", "DESIGNS", "ARMS", "NEW_CELLS", "BESIDE",
           "RECORD_COLUMNS", "CALENDARS", "Refused", "declared_seed", "section_11", "calendar_frames", "Inputs", "cell_job", "runs_of",
           "start_frame", "MEASURES", "read_check", "run_reading", "honesty_table", "menu_table", "adapter_provenance"]
