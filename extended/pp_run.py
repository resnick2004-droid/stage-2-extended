"""RD-02's reading, run (`prereg/RD-02_payout_policy.md` sections 8, 9, 12 and 14; Q-105b, fixed under Q-105d after the
red team's second read, `docs/reviews/BUILD_RD-02_v2_2026-11-16.md`): the cells x arms x blocks on U1's start-day replay,
the readings beside, the gates, 8.1 items 4 to 6, 8.2's oracles, 8.3's mechanics, 9.1's reading with 9.2's uncertainty
and the honesty table, the menu -- as three tables for `scripts/pp_reading.py` to write.

    from extended import use_vendored_stage2; use_vendored_stage2()
    from extended import pp_run as RUN
    tables = RUN.run_reading(RUN.RealInputs(), designs=("p14", "p16"))          # the lead's, from a clean run

**The order, across both designs (14 step 2, 8.1; Q-102's m4; the second read's R2).**
(a) every design's `ref` at `off`, both arms, with Q-94's recorder and the counters' channel on -- 8.1 item 2's repeat
(the inputs' reference comparison), item 4 (the levers' counts zero) and the held-state rule's firing check (Q-106's
m2); (b) every design's `ref` under `denial_10/25/50` and `rtp`, verdict arm -- item 6 (Q-44's per-start file in the
real run); (c) every new run (the three new cells of each design; on P-14 also the three rule-sensitivity runs) at
`off` on both arms, recorded and counted, checked under item 5 (the recorder's per-start checks) and the firing check
before anything of it is read, then its readings beside (policy cells, verdict arm); then the new cells' gates (point,
bound and the zero-edge twin), each path's held-state rule checked (n3); (d) 8.2's oracles on every replay and every
gate, then 8.3's mechanics; and only then the reading. **Any failed check raises `Refused`: no reading of any new run
is computed, written or printed** (the script writes only what returns). Between (c)'s check of a run and the reading,
a run's records are kept compacted (each start's tallies of the recorder's rows), never read.

**Each measure at its own horizon (5 item 3; R1).** The per-start table (`start_frame`) cuts every event measure at its
declared h as Q-17's reading does (`extended/user_readings.py`'s `path_rows`): the first pass and the first payout at
126 -- reached by 126 or not, the sessions and the cash only for the starts reaching it by 126 -- and break-even at 252
(and by month m, 1{break-even by 21 m}); so a start's value reads no session after its h, and the early block
(`u_select.block(records, "early", h)`) touches no 2024 session.

**The reading (9.1).** On all starts, the early and the late block, and by start year (means only, not purged):
* item 1 -- the card (`u_select.scorecard`: P, S1 to S5c), with S2 (the first pass at 126: sessions and cash, p90),
  S3d (U1's first payout's cash, p50) and Q (U1's Q1 at 21, 30 and 42 sessions and Q2), each cell's card paired with its
  base on the same starts (`paired_with=`); the frontier on P, S1, S3a and S5a among the four policies;
* item 2 -- E-014's journey variables, each cut at its h, the share broken even by months 1, 2, 3, 6 and 12;
* item 3 -- each measure's distribution (mean, p10, p50, p90; for sessions to an event also with an unreached start
  beyond) and S6's form, the start day's share of the variance across the four policies (and U1's luck ratio);
* item 4 -- each measure paired with the base: the per-start difference's p10/p50/p90, the shares better, equal and
  worse, the mean with 9.2's kept-window interval, sign count, n_eff and MDD, the honesty label and the rare-shape line;
  for the share ahead the four-way split; for a measure defined only where its event happened (r3) the four-way split
  by definedness over every start, the difference's distribution labelled as over the starts defined on both sides;
* item 5 -- `lock` and `half` against `ref`, `lock_half` against each lever alone (and each minimal-rescue run against
  its declared cell, the second read's n5);
* item 6 -- what diverges, per block: accounts activated and lost, payouts' count and size, fees, trades taken (the
  recorder's rows), the held account-sessions by class and their share of the funded account-sessions; the evaluations
  bought and the realised risk within D-212 (1)'s line (P-14's allowance-capped form, E-022 (1)) from the gate rows
  (7.1's recorder keeps no trade column that holds them on the replay: said so on its rows);
* item 7 -- the readings beside with every reading above, CVaR10 of the month-3 net and P under Q-17's bankroll limits
  (per start, paired), the exact runs' differing count, and the ladder's ranking of the four policies against `off`;
* item 8 -- the gates' rows (growth on the required bankroll, the required bankroll, payouts a month, days to the first
  payout; D-564 (4)) beside the base's registered gate row;
* item 9 -- the evenness trade-off curve: the four policies' points of P against each evenness measure, and each step's
  cost in P per unit of evenness (E-015's menu form);
* item 10 -- the menu: each cell's headline, its guarded measures paired, the stability flag over P and every guarded
  measure (`GUARDED`), E-015's limits as declared hooks (only those the caller hands in), the count of intervals.

**8.3's mechanics, per block** -- the shares of starts differing within 63, 126 and 252 sessions, the levers' and the
held reads' counts (per block, each start's long replay, purged at 252), the share of starts held at sessions 63, 126
and 252, the holiday-hours reach (each request dated on its own session, r2), the minutes-release count, E-029's voided
days per block and horizon; a cell identical to its base on every start is "no effect on these trades", and nothing more
is read for it.

**The honesty table** (9.2 item 7): at every (h, n_w) an interval is printed for, the 21 shapes' coverage and misses,
`HONESTY_SERIES` series a setting, from the declared seed (read from the pinned file's section 11, never written here).
"""
from __future__ import annotations

import hashlib
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import numpy as np
import pandas as pd

from extended import ROOT, use_vendored_stage2

use_vendored_stage2()

from extended import payout_policy as PP  # noqa: E402
from extended import pp_reading as RD  # noqa: E402
from extended import user_measures as M  # noqa: E402
from extended import user_readings as R  # noqa: E402

DECLARATION = "prereg/RD-02_payout_policy.md"
PREREG_ID = "RD-02"
PIN_ROW = "E-082"
PURPOSES = ("payout_scorecard", "payout_ladder_beside", "payout_gate_beside")
DESIGNS = ("p14", "p16")
ARMS = ("verdict", "point")
NEW_CELLS = ("lock", "half", "lock_half")
POLICY_CELLS = ("ref",) + NEW_CELLS
SENSITIVITY_DESIGN = "p14"
BESIDE = ("denial_10", "denial_25", "denial_50", "rtp")
LADDER = ("denial_10", "denial_25", "denial_50")
#: 7.1: the trade columns the replay recorder keeps (fixed; its checks run on the full record where the start ran)
RECORD_COLUMNS = ("date", "entry_t", "exit_t", "at_cap", "kind")
BLOCKS = (("all", None), ("early", "early"), ("late", "late"))
HELD_SESSIONS = (63, 126, 252)
DIFFER_SESSIONS = (63, 126, 252)
#: a count over a start's whole long replay (U1's 252 sessions) is read on the blocks purged at 252
WHOLE = R.YEAR_WINDOW
MONTH = R.MONTH
FIRST_WINDOW, YEAR_WINDOW = R.FIRST_WINDOW, R.YEAR_WINDOW
LUCK_MONTHS = (1, 3, 6, 12)
MINUTES_RELEASE_CT = "13:00"
VOIDED_DAYS = ("2020-07-01", "2025-06-30", "2025-07-01")
CALENDARS = {"config/calendar_early_closes.csv": "72db4941f95320900aac29c6c047742da176cd9b55c925cc9275a18fb3e67fb2",
             "config/calendar_fomc_minutes.csv": "0350d41fe224909d93ae9211761e839c4925c231b83f039ccb92f1d8a4127ce7"}
LOWER, HIGHER = "lower", "higher"
ADAPTER_FILES = ("extended/payout_policy.py", "extended/pp_reading.py", "extended/pp_run.py", "extended/user_beside.py",
                 "extended/gate.py", "extended/campaign.py", "extended/replay_records.py", "scripts/pp_reading.py")
#: pp_reading.csv's sections (14); every row also names its `part` (what it is within the section)
SECTIONS = ("identity", "oracle", "mechanics", "scorecard", "paired", "diverge", "coverage", "beside")
#: 9.1 item 1's frontier
FRONTIER = ("P", "S1", "S3a", "S5a")
#: the guarded measures the stability flag reads besides P (9.1 item 10): the card's guarded keys
GUARDED = ("P", "card_S1", "card_S3a", "card_S3b", "card_S3c", "card_S4a", "card_S4b", "card_S5a", "card_S5b",
           "card_S5c")
#: 9.1 item 8 (D-564 (4)'s rows) and item 6 on the gate, from a gate row's columns
GATE_READING = (("growth_on_required_bankroll", "pf_growth_on_base_p50"), ("required_bankroll_p90", "pf_required_p90"),
                ("days_to_first_payout_median", "median_days_to_first_payout"),
                ("payouts_per_path_mean", "mean_payouts_per_path"))
GATE_DIVERGE = (("evaluations_bought_mean", "mean_combine_purchases"), ("funded_accounts_mean", "mean_accounts_funded"),
                ("share_accounts_ever_paid", "share_accounts_ever_paid"),
                ("realised_to_intended_capped_risk", "realised_to_intended_capped_risk"))
GATE_SHIFTS = ("point", "lower_bound")
#: the request oracle's tolerance (8.2: "to 1e-9"), relative to the request
ORACLE_TOL = 1e-9

NAN = float("nan")


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


def holiday_sessions(cal: Mapping[str, pd.DataFrame], dates: Sequence[str]) -> set[str]:
    """E-029's holiday-hours reach (section 4): the sessions that close early (an early close, or a holiday's abbreviated
    session) and the last session before a scheduled holiday, on the job's own dates."""
    ec = cal["config/calendar_early_closes.csv"]
    early = set(ec.loc[ec["kind"].isin(["early_close", "holiday"]), "date"])
    holidays = set(ec.loc[ec["kind"] == "holiday", "date"])
    di = {str(d): i for i, d in enumerate(dates)}
    eve = {str(dates[di[d] - 1]) for d in holidays if d in di and di[d] > 0}
    return early | eve


# ------------------------------------------------------------------------------------------------ the inputs


class Inputs:
    """What the run reads, for one source (the real designs, or a synthetic campaign in the tests)."""

    def preflight(self, designs: Sequence[str]) -> list[str]:
        """Everything that can be checked before the judged block's reads are authorised (its problems): read no bar."""
        return []

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

    def base_gate_rows(self, design: str) -> dict[str, dict[str, Any]]:
        """The base's registered gate row at 0 %, the placement off, by shift (none for a source without one)."""
        return {}

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


# ------------------------------------------------------------------------------------------------ the measures


@dataclass(frozen=True)
class Measure:
    """One per-start measure of 9.1 items 1, 2, 4 and 7: its name, the per-start table's column, its horizon's key
    (`pp_reading.horizon`), the better direction, and its kind -- `value` (defined on every start with h left),
    `sessions` (an event's sessions, defined only for the starts reaching it by h: an unreached start counts beyond) or
    `conditional` (defined only where its event happened by h)."""

    name: str
    col: str
    hkey: str
    direction: str
    kind: str = "value"


_NET_HKEY = {1: "net_m1", 2: "net_m2", 3: "net_m3", 6: "share_m6", 9: "net_m9", 12: "share_m12"}

MEASURES: tuple[Measure, ...] = (
    Measure("P", "p_start", "P", HIGHER),
    *(Measure(f"net_month_{m}", f"net_month_{m}", _NET_HKEY[m], HIGHER) for m in (1, 2, 3, 6, 9, 12)),
    *(Measure(f"ahead_month_{m}", f"ahead_{m}", f"share_m{m}", HIGHER) for m in (1, 2, 3, 6, 9, 12)),
    Measure("reached_first_pass_by_126", "reached_first_pass_by_126", "first_pass_sessions", HIGHER),
    Measure("sessions_to_first_pass", "first_pass_by_126", "first_pass_sessions", LOWER, "sessions"),
    Measure("cash_before_first_pass", "spent_before_first_pass_by_126", "first_pass_cash", LOWER, "conditional"),
    Measure("reached_first_payout_by_126", "reached_first_payout_by_126", "first_payout_sessions", HIGHER),
    Measure("sessions_to_first_payout", "first_payout_by_126", "first_payout_sessions", LOWER, "sessions"),
    Measure("cash_before_first_payout", "spent_before_first_payout_by_126", "first_payout_cash", LOWER, "conditional"),
    *(Measure(f"broken_even_by_month_{m}", f"broken_even_m{m}", f"broken_even_m{m}", HIGHER)
      for m in R.BREAK_EVEN_MONTHS),
    Measure("sessions_to_break_even", "break_even_by_252", "break_even_sessions", LOWER, "sessions"),
    Measure("fell_back_below_zero", "fell_back_by_252", "fell_back", LOWER, "conditional"),
    Measure("deepest_fall_after_break_even", "deepest_fall_by_252", "deepest_fall", LOWER, "conditional"),
    Measure("share_months_positive", "share_months_positive", "positive_months", HIGHER),
    Measure("longest_months_without_payout", "longest_months_without_payout", "longest_no_payout_run", LOWER),
    Measure("sd_monthly_net", "sd_monthly_net", "monthly_net_spread", LOWER),
    Measure("payouts_per_month", "payouts_per_month", "payouts_per_month", HIGHER),
    Measure("payout_cash_per_month", "payout_cash_per_month", "payouts_per_month", HIGHER),
    Measure("largest_month_share", "largest_month_share", "largest_month_share", LOWER, "conditional"),
    *(Measure(f"P_bankroll_{int(lim)}", f"p_bankroll_{int(lim)}", "P_bankroll_limit", HIGHER)
      for lim in R.BANKROLL_LIMITS),
)
BY_NAME = {m.name: m for m in MEASURES}
#: 9.1 item 2's evenness measures (the trade-off curve, item 9)
EVENNESS = ("share_months_positive", "longest_months_without_payout", "sd_monthly_net",
            "deepest_fall_after_break_even", "payouts_per_month", "largest_month_share")


# ------------------------------------------------------------------------------------------------ per start


def start_frame(design: str, arm: str, response: str, outs: Sequence[Mapping[str, Any]]) -> pd.DataFrame:
    """Q-17's per-start table (`extended.user_readings.start_table`) with the month-9 net, the per-start P, the shares
    ahead, every event measure cut at its declared horizon (R1: the first pass and payout at 126, as Q-17's `path_rows`
    reads them; break-even at 252 and by month m), and P under Q-17's bankroll limits per start."""
    t = R.start_table(design, arm, response, outs)
    t["net_month_9"] = [float(x["rec"]["net_month"][8]) if x["rec"]["net_month"][8] is not None else np.nan
                        for x in outs]
    t["p_start"] = t["months_ahead"] / 3.0
    for m in (1, 2, 3, 6, 9, 12):
        col = f"net_month_{m}"
        t[f"ahead_{m}"] = np.where(t[col].isna(), np.nan, (t[col] > 0).astype(float))
    obs = t["observed"].to_numpy(int)
    for ev, spent in (("first_pass", "spent_before_first_pass"), ("first_payout", "spent_before_first_payout")):
        h = FIRST_WINDOW
        f = t[ev].to_numpy(float)
        ok = obs >= h
        hit = np.isfinite(f) & (f <= h)
        t[f"reached_{ev}_by_{h}"] = np.where(ok, hit.astype(float), np.nan)
        t[f"{ev}_by_{h}"] = np.where(ok & hit, f, np.nan)
        t[f"{spent}_by_{h}"] = np.where(ok & hit, t[spent].to_numpy(float), np.nan)
    be = t["break_even_day"].to_numpy(float)
    ok = obs >= YEAR_WINDOW
    hit = np.isfinite(be) & (be <= YEAR_WINDOW)
    t[f"broken_even_by_{YEAR_WINDOW}"] = np.where(ok, hit.astype(float), np.nan)
    t[f"break_even_by_{YEAR_WINDOW}"] = np.where(ok & hit, be, np.nan)
    t[f"fell_back_by_{YEAR_WINDOW}"] = np.where(ok & hit, t["fell_back"].to_numpy(float), np.nan)
    t[f"deepest_fall_by_{YEAR_WINDOW}"] = np.where(ok & hit, t["deepest_fall_after_break_even"].to_numpy(float), np.nan)
    for m in R.BREAK_EVEN_MONTHS:
        hm = RD.month_horizon(m)
        t[f"broken_even_m{m}"] = np.where(obs >= hm, (np.isfinite(be) & (be <= MONTH * m)).astype(float), np.nan)
    nets = t[["net_month_1", "net_month_2", "net_month_3"]].to_numpy(float)
    spent = t["spent_before_first_payout"].to_numpy(float)
    full = np.isfinite(nets).all(axis=1) & (obs >= 3 * MONTH)
    for lim in R.BANKROLL_LIMITS:                     # a month ahead counts only within the limit (Q-17's rule)
        within = np.where(np.isfinite(spent), spent, np.inf) <= float(lim)
        t[f"p_bankroll_{int(lim)}"] = np.where(full, ((nets > 0) & within[:, None]).sum(axis=1) / 3.0, np.nan)
    return t


def records_of(t: pd.DataFrame) -> list[dict[str, Any]]:
    return [{"start_day": int(r.start_day), "start_date": str(r.start_date), "observed": int(r.observed)}
            for r in t.itertuples()]


def block_days(recs: Sequence[Mapping[str, Any]], which: str | None, h: int) -> list[int]:
    from propedge.research import u_select as US

    return [int(r["start_day"]) for r in US.block(recs, which, int(h))]


ROW_KEYS = ("section", "part", "design", "arm", "cell", "mode", "response", "base", "block", "measure", "stat", "value",
            "n", "h", "note")


def _row(**kw: Any) -> dict[str, Any]:
    base = {"section": "", "part": "", "design": "", "arm": "", "cell": "", "mode": "", "response": "off", "base": "",
            "block": "", "measure": "", "stat": "", "value": np.nan, "n": 0, "h": 0, "note": ""}
    base.update(kw)
    if not base["part"]:
        base["part"] = base["section"]
    return base


def _f(x: Any) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return NAN
    return v


# ------------------------------------------------------------------------------------------------ distributions


def distribution_rows(t: pd.DataFrame, key: dict[str, Any]) -> list[dict[str, Any]]:
    """9.1 item 3: each measure as a distribution over the block's starts (mean, p10, p50, p90 over the starts where it is
    defined; for sessions to an event also with an unreached start beyond, Q-17's form), and by start year (means only,
    not purged)."""
    out = []
    recs = records_of(t)
    tt = t.set_index("start_day")
    for bname, which in BLOCKS:
        for m in MEASURES:
            h = RD.horizon(m.hkey)
            days = [int(r["start_day"]) for r in RD.block(recs, which, m.hkey)]
            x = tt.loc[days, m.col].to_numpy(float) if days else np.zeros(0)
            fin = x[np.isfinite(x)]
            note = "" if fin.size == x.size else (f"{x.size - fin.size} of {x.size} starts undefined"
                                                  + (" (not reached by h)" if m.kind != "value" else ""))
            for stat, v in (("mean", fin.mean() if fin.size else np.nan),
                            *((f"p{p}", np.percentile(fin, p) if fin.size else np.nan) for p in (10, 50, 90))):
                out.append(_row(section="scorecard", part="distribution", **key, block=bname, measure=m.name,
                                stat=stat, value=float(v), n=int(fin.size), h=h, note=note))
            if m.kind == "sessions":
                for p in (10, 50, 90):
                    out.append(_row(section="scorecard", part="distribution", **key, block=bname, measure=m.name,
                                    stat=f"p{p}_unreached_beyond", value=float(M.days_quantile(x, h, p)) if x.size
                                    else np.nan, n=int(x.size), h=h,
                                    note=f"window {h}; an unreached start beyond (blank when the percentile is beyond)"))
    for m in MEASURES:
        h = RD.horizon(m.hkey)
        for y, rs in RD.by_year(recs, m.hkey).items():
            x = tt.loc[[int(r["start_day"]) for r in rs], m.col].to_numpy(float)
            fin = x[np.isfinite(x)]
            out.append(_row(section="scorecard", part="by_year", **key, block=f"year_{y}", measure=m.name, stat="mean",
                            value=float(fin.mean()) if fin.size else np.nan, n=int(fin.size), h=h,
                            note="means only, not purged: a start late in a year reads sessions of the next"))
    return out


# ------------------------------------------------------------------------------------------------ the card


def extra_card(recs: Sequence[Mapping[str, Any]], which: str | None,
               paired_with: Sequence[Mapping[str, Any]] | None = None) -> dict[str, dict[str, Any]]:
    """9.1 item 1's reported rows at h = 126 (5 item 3): S2 -- the first pass's sessions p90 (an unreached start beyond)
    and the cash spent before it p90 (among the starts reaching it by 126); S3d -- U1's first payout's cash p50
    (`first_payout:cash_p50@126`); Q -- U1's Q1 at 21, 30 and 42 sessions and Q2 (`quit:*`), each read as U1 reads it
    (`user_journey.Views`, the exact-length run where it differed). `paired_with`: on the start dates both sides hold."""
    from propedge.research import u_select as US
    from propedge.research import user_journey as U

    h = FIRST_WINDOW
    mine = US.block(recs, which, h)
    if paired_with is not None:
        dates = {str(r["start_date"]) for r in US.block(paired_with, which, h)}
        mine = [r for r in mine if str(r["start_date"]) in dates]
    keys = ("S2_sessions_p90", "S2_cash_p90", "S3d", "Q1_21", "Q1_30", "Q1_42", "Q2")
    if not mine:
        return {k: {"value": NAN, "n": 0} for k in keys}
    V = U.Views(mine)
    t = V.at(h)
    m = t["observed"].to_numpy(int) >= h
    f = t["first_pass"].to_numpy(float)
    hit = m & np.isfinite(f) & (f <= h)
    s = t["spent_before_first_pass"].to_numpy(float)[hit]
    rows = {r["key"]: r for r in U.metric_rows(V)}

    def u1(k: str) -> dict[str, Any]:
        r = rows.get(k)
        return {"value": _f(r["value"]), "n": int(r["n"])} if r is not None else {"value": NAN, "n": 0}

    return {"S2_sessions_p90": {"value": float(M.days_quantile(f[m], h, 90)), "n": int(m.sum())},
            "S2_cash_p90": {"value": float(np.percentile(s, 90)) if s.size else NAN, "n": int(s.size)},
            "S3d": u1("first_payout:cash_p50@126"), "Q1_21": u1("quit:q1_mean_net@21"),
            "Q1_30": u1("quit:q1_mean_net@30"), "Q1_42": u1("quit:q1_mean_net@42"), "Q2": u1("quit:q2_mean_net@63")}


def card_of(recs: Sequence[Mapping[str, Any]], which: str | None,
            paired_with: Sequence[Mapping[str, Any]] | None = None) -> dict[str, dict[str, Any]]:
    """The card (`u_select.scorecard`) and the reported rows (`extra_card`) on one block."""
    from propedge.research import u_select as US

    card = US.scorecard(recs, which, paired_with=paired_with)
    card.update(extra_card(recs, which, paired_with))
    return card


def card_horizon(k: str) -> int:
    from propedge.research import u_select as US

    return int(US.BY_KEY[k].horizon) if k in US.BY_KEY else FIRST_WINDOW


def card_rows(cards: Mapping[str, Mapping[str, Mapping[str, Any]]], key: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for bname, _ in BLOCKS:
        for k, v in cards[bname].items():
            out.append(_row(section="scorecard", part="card", **key, block=bname, measure=f"card_{k}", stat="value",
                            value=_f(v["value"]), n=int(v["n"]), h=card_horizon(k)))
    return out


def paired_card_rows(cell_recs: Sequence[Mapping[str, Any]], base_recs: Sequence[Mapping[str, Any]],
                     key: dict[str, Any]) -> list[dict[str, Any]]:
    """9.1 item 1 paired (the second read's R5): each block's card of the cell less the base's, both on the start dates
    both sides hold at each measure's horizon (`u_select.scorecard(..., paired_with=...)`)."""
    out = []
    for bname, which in BLOCKS:
        c, b = card_of(cell_recs, which, base_recs), card_of(base_recs, which, cell_recs)
        for k in c:
            x, y = _f(c[k]["value"]), _f(b[k]["value"])
            for stat, v in (("cell", x), ("base", y), ("cell_less_base", x - y)):
                out.append(_row(section="paired", part="card", **key, block=bname, measure=f"card_{k}", stat=stat,
                                value=float(v), n=int(c[k]["n"]), h=card_horizon(k),
                                note="on the start dates both sides hold at the measure's horizon"))
    return out


# ------------------------------------------------------------------------------------------------ paired


def _ahead_split(xa: np.ndarray, ya: np.ndarray) -> list[tuple[str, float]]:
    return [("ahead_cell_not_base", float((xa & ~ya).mean())), ("ahead_both", float((xa & ya).mean())),
            ("ahead_neither", float((~xa & ~ya).mean())), ("ahead_base_not_cell", float((~xa & ya).mean()))]


def paired_rows(cell: pd.DataFrame, base: pd.DataFrame, key: dict[str, Any], honesty: dict) -> list[dict[str, Any]]:
    """9.1 items 4 and 5 and 9.2: each measure, cell less base on the same starts, per block, and by start year (means
    only, not purged). A measure defined only where its event happened by h (r3): the four-way split by definedness
    over every start of the block (both, the cell only, the base only, neither), and for sessions to an event the
    shares better, equal and worse with an unreached start counted beyond; the difference's distribution and the shares
    over the starts defined on both sides, labelled so; no interval (the kept windows rest on consecutive starts)."""
    out = []
    a = cell.set_index("start_day")
    b = base.set_index("start_day")
    common = sorted(set(a.index) & set(b.index))
    recs = records_of(b.loc[common].reset_index())
    for bname, which in BLOCKS:
        for m in MEASURES:
            h = RD.horizon(m.hkey)
            days = [int(r["start_day"]) for r in RD.block(recs, which, m.hkey)]
            k = dict(section="paired", part="paired", **key, block=bname, measure=m.name, h=h)
            if not days:
                out.append(_row(**k, stat="mean", value=np.nan, n=0, note="no start in the block"))
                continue
            x, y = a.loc[days, m.col].to_numpy(float), b.loc[days, m.col].to_numpy(float)
            fx, fy = np.isfinite(x), np.isfinite(y)
            ok = fx & fy
            n_all = len(days)
            if not ok.all():
                what = "reached by h" if m.kind != "value" else "defined"
                for stat, v in (("defined_both", (fx & fy).mean()), ("defined_cell_only", (fx & ~fy).mean()),
                                ("defined_base_only", (~fx & fy).mean()), ("defined_neither", (~fx & ~fy).mean())):
                    out.append(_row(**k, stat=stat, value=float(v), n=n_all,
                                    note=f"over every start of the block: the measure {what} on the side(s) named"))
                if m.kind == "sessions":
                    xv, yv = np.where(fx, x, np.inf), np.where(fy, y, np.inf)
                    for stat, v in (("share_better_unreached_beyond", (xv < yv).mean()),
                                    ("share_equal_unreached_beyond", (xv == yv).mean()),
                                    ("share_worse_unreached_beyond", (xv > yv).mean())):
                        out.append(_row(**k, stat=stat, value=float(v), n=n_all,
                                        note="over every start of the block; a start not reaching the event by h "
                                             "counts beyond (sooner is better)"))
            n = int(ok.sum())
            if n == 0:
                out.append(_row(**k, stat="mean", value=np.nan, n=0, note="no start of the block with the measure "
                                                                          "defined on both sides"))
                continue
            d = x[ok] - y[ok]
            note = "" if ok.all() else "over the starts defined on both sides (the event reached by h on both)"
            better = (d > 0) if m.direction == HIGHER else (d < 0)
            worse = (d < 0) if m.direction == HIGHER else (d > 0)
            for stat, v in (("mean", d.mean()), ("p10", np.percentile(d, 10)), ("p50", np.percentile(d, 50)),
                            ("p90", np.percentile(d, 90)), ("share_better", better.mean()),
                            ("share_equal", (d == 0).mean()), ("share_worse", worse.mean())):
                out.append(_row(**k, stat=stat, value=float(v), n=n, note=note))
            if m.name.startswith("ahead_month_"):
                for stat, v in _ahead_split(x[ok] == 1.0, y[ok] == 1.0):
                    out.append(_row(**k, stat=stat, value=v, n=n))
            if not ok.all():
                out.append(_row(**k, stat="interval", value=np.nan, n=n,
                                note="not computed: the measure is undefined on some starts of the block, and the "
                                     "kept windows rest on consecutive starts (the distribution and the shares only)"))
                continue
            _interval_rows(out, k, x, y, d, h, n, honesty)
    # by start year: means only, not purged
    for m in MEASURES:
        h = RD.horizon(m.hkey)
        for yr, rs in RD.by_year(recs, m.hkey).items():
            days = [int(r["start_day"]) for r in rs]
            x, y = a.loc[days, m.col].to_numpy(float), b.loc[days, m.col].to_numpy(float)
            ok = np.isfinite(x) & np.isfinite(y)
            out.append(_row(section="paired", part="by_year", **key, block=f"year_{yr}", measure=m.name, stat="mean",
                            value=float((x[ok] - y[ok]).mean()) if ok.any() else np.nan, n=int(ok.sum()), h=h,
                            note="means only, not purged: a start late in a year reads sessions of the next"))
    return out


def _interval_rows(out: list, k: dict, x: np.ndarray, y: np.ndarray, d: np.ndarray, h: int, n: int,
                   honesty: dict) -> None:
    desc = RD.describe(d, h)
    wm_c, wm_b, wm = RD.window_means(x, h), RD.window_means(y, h), RD.window_means(d, h)
    sc = RD.sign_count(wm_c, wm_b)
    out += [_row(**k, stat="n_w", value=float(wm.size), n=n), _row(**k, stat="sign_above", value=float(sc[0]), n=n),
            _row(**k, stat="sign_equal", value=float(sc[1]), n=n), _row(**k, stat="sign_below", value=float(sc[2]), n=n),
            _row(**k, stat="n_eff", value=float(M.n_eff_bartlett(d, lag=h)), n=n)]
    if desc != "interval":
        out.append(_row(**k, stat="interval", value=np.nan, n=n, note=desc))
        return
    lo, hi = RD.t_interval(wm)
    mdd = RD.mdd(wm)
    out += [_row(**k, stat="mdd", value=float(mdd), n=n, note="printed before the mean, as 9.2 item 5 asks"),
            _row(**k, stat="kept_mean", value=float(wm.mean()), n=n), _row(**k, stat="ci90_low", value=lo, n=n),
            _row(**k, stat="ci90_high", value=hi, n=n)]
    honesty[(h, int(wm.size))] = True
    out.append(_row(**k, stat="interval_label", value=np.nan, n=n, note=f"pending honesty setting {h} {wm.size}"))


def cvar_rows(t: pd.DataFrame, base: pd.DataFrame | None, key: dict[str, Any]) -> list[dict[str, Any]]:
    """9.1 item 7: CVaR10 of the month-3 net (Q-17's `cvar`, h = 63) per block -- the cell's, and with a base the base's
    on the same starts and the difference."""
    out = []
    h = RD.horizon("cvar10_m3")
    a = t.set_index("start_day")
    recs = records_of(t)
    for bname, which in BLOCKS:
        days = [int(r["start_day"]) for r in RD.block(recs, which, "cvar10_m3")]
        if base is None:
            x = a.loc[days, "net_month_3"].to_numpy(float) if days else np.zeros(0)
            out.append(_row(section="scorecard", part="cvar10", **key, block=bname, measure="cvar10_net_month_3",
                            stat="value", value=float(M.cvar(x, 0.10)), n=int(np.isfinite(x).sum()), h=h,
                            note="the mean of the worst ceil(0.10 n) month-3 nets"))
            continue
        b = base.set_index("start_day")
        days = [s for s in days if s in b.index]
        x = a.loc[days, "net_month_3"].to_numpy(float) if days else np.zeros(0)
        y = b.loc[days, "net_month_3"].to_numpy(float) if days else np.zeros(0)
        cx, cy = M.cvar(x, 0.10), M.cvar(y, 0.10)
        for stat, v in (("cell", cx), ("base", cy), ("cell_less_base", cx - cy)):
            out.append(_row(section="paired", part="cvar10", **key, block=bname, measure="cvar10_net_month_3",
                            stat=stat, value=float(v), n=len(days), h=h, note="on the same starts"))
    return out


# ------------------------------------------------------------------------------------------------ across policies


def s6_rows(frames: Mapping[str, pd.DataFrame], key: dict[str, Any]) -> list[dict[str, Any]]:
    """9.1 item 3, S6's form: for each measure and block, the start day's share of the variance across the four policies
    (a two-way decomposition of every (start, policy) value on the starts where all four are defined: the starts'
    means, the policies' means, the rest), and for the nets at months 1, 3, 6 and 12 U1's luck ratio (each policy's
    spread across starts over the spread of the four policies' means, as `user_journey.luck_rows` forms it)."""
    out = []
    cells = [c for c in POLICY_CELLS if c in frames]
    if len(cells) < 2:
        return out
    tabs = {c: frames[c].set_index("start_day") for c in cells}
    recs = records_of(frames[cells[0]])
    for bname, which in BLOCKS:
        for m in MEASURES:
            h = RD.horizon(m.hkey)
            days = [int(r["start_day"]) for r in RD.block(recs, which, m.hkey) if all(int(r["start_day"]) in tabs[c].index
                                                                                     for c in cells)]
            X = np.column_stack([tabs[c].loc[days, m.col].to_numpy(float) for c in cells]) if days else \
                np.zeros((0, len(cells)))
            X = X[np.isfinite(X).all(axis=1)]
            k = dict(section="scorecard", part="s6", **key, cell=",".join(cells), block=bname, measure=m.name, h=h,
                     n=int(len(X)))
            tot = float(((X - X.mean()) ** 2).sum()) if len(X) else 0.0
            if len(X) < 2 or not tot > 0:
                out.append(_row(**k, stat="start_share", value=np.nan, note="no variance across the starts and "
                                                                            "policies" if len(X) >= 2 else "too few starts"))
                continue
            g = X.mean()
            ss_start = len(cells) * float(((X.mean(axis=1) - g) ** 2).sum())
            ss_pol = len(X) * float(((X.mean(axis=0) - g) ** 2).sum())
            for stat, v in (("start_share", ss_start / tot), ("policy_share", ss_pol / tot),
                            ("interaction_share", (tot - ss_start - ss_pol) / tot)):
                out.append(_row(**k, stat=stat, value=float(v),
                                note="the share of the (start, policy) values' sum of squares; the four policies on the "
                                     "starts where all are defined"))
            if m.name in tuple(f"net_month_{mm}" for mm in LUCK_MONTHS):
                means = X.mean(axis=0)
                between = float(np.std(means, ddof=1)) if len(means) > 1 else np.nan
                for j, c in enumerate(cells):
                    within = float(np.std(X[:, j], ddof=1))
                    out.append(_row(**k, stat=f"luck_ratio_{c}", value=within / between if between > 0 else np.nan,
                                    note="U1's luck form: the policy's spread across starts over the spread of the four "
                                         "policies' means (ddof 1), on the common starts"))
    return out


def frontier_rows(cards: Mapping[str, Mapping[str, Mapping[str, Any]]], key: dict[str, Any]) -> list[dict[str, Any]]:
    """9.1 item 1: the frontier on P, S1, S3a and S5a among the four policies of a base (each on the block, in its own
    direction): a policy is on it unless another is at least as good on all four and better on one; a blank never
    dominates and is never dominated."""
    from propedge.research import u_select as US

    out = []
    cells = [c for c in POLICY_CELLS if c in cards]
    for bname, _ in BLOCKS:
        pts = {c: [_f(cards[c][bname][k]["value"]) for k in FRONTIER] for c in cells}
        sign = [1.0 if US.BY_KEY[k].direction == US.HIGHER else -1.0 for k in FRONTIER]

        def dominates(p: list, q: list) -> bool:
            if not all(math.isfinite(v) for v in p + q):
                return False
            ge = all(s * a >= s * b for s, a, b in zip(sign, p, q))
            gt = any(s * a > s * b for s, a, b in zip(sign, p, q))
            return ge and gt

        for c in cells:
            by = [o for o in cells if o != c and dominates(pts[o], pts[c])]
            out.append(_row(section="scorecard", part="frontier", **key, cell=c, block=bname,
                            measure="on_frontier_P_S1_S3a_S5a", stat="value", value=float(not by),
                            note=("dominated by " + ", ".join(by)) if by else "on the frontier among the four policies"))
    return out


def evenness_rows(frames: Mapping[str, pd.DataFrame], cards: Mapping[str, Mapping[str, Mapping[str, Any]]],
                  key: dict[str, Any]) -> list[dict[str, Any]]:
    """9.1 item 9, E-015's menu form: the four policies' points of P (the card's, on the block) against each evenness
    measure's mean (on the block at its h), ordered from the least even to the most even, and each step's change in P,
    in the measure, and P per unit of evenness gained."""
    out = []
    cells = [c for c in POLICY_CELLS if c in frames and c in cards]
    for bname, which in BLOCKS:
        for name in EVENNESS:
            m = BY_NAME[name]
            pts = []
            for c in cells:
                t = frames[c]
                days = [int(r["start_day"]) for r in RD.block(records_of(t), which, m.hkey)]
                x = t.set_index("start_day").loc[days, m.col].to_numpy(float) if days else np.zeros(0)
                x = x[np.isfinite(x)]
                ev, p = float(x.mean()) if x.size else NAN, _f(cards[c][bname]["P"]["value"])
                pts.append((c, ev, p))
                out.append(_row(section="scorecard", part="evenness_tradeoff", **key, cell=c, block=bname, measure=name,
                                stat="evenness_mean", value=ev, n=int(x.size), h=RD.horizon(m.hkey)))
                out.append(_row(section="scorecard", part="evenness_tradeoff", **key, cell=c, block=bname, measure=name,
                                stat="P", value=p, h=RD.horizon("P")))
            sgn = 1.0 if m.direction == HIGHER else -1.0
            ok = [q for q in pts if math.isfinite(q[1]) and math.isfinite(q[2])]
            ok.sort(key=lambda q: (sgn * q[1], q[0]))                    # least even first
            for (c0, e0, p0), (c1, e1, p1) in zip(ok, ok[1:]):
                gain = sgn * (e1 - e0)
                kk = dict(section="scorecard", part="evenness_tradeoff", **key, cell=f"{c0}->{c1}", block=bname,
                          measure=name)
                out += [_row(**kk, stat="step_evenness_gained", value=float(gain)),
                        _row(**kk, stat="step_P_change", value=float(p1 - p0)),
                        _row(**kk, stat="step_P_per_unit_evenness", value=float((p1 - p0) / gain) if gain else np.nan,
                             note="the change in the share ahead (P) per unit of evenness gained (E-015's menu form)")]
    return out


def ladder_rank_rows(p_by: Mapping[str, Mapping[str, Mapping[str, float]]], key: dict[str, Any]) -> list[dict[str, Any]]:
    """9.1 item 7: the ladder's ranking of the four policies by P (the card's), at each denial level and the placement on,
    against the 0 % headline (`off`); a tie shares the better rank. `p_by`: {response: {cell: {block: P}}}."""
    out = []
    if "off" not in p_by:
        return out
    cells = [c for c in POLICY_CELLS if c in p_by["off"]]

    def ranks(resp: str, bname: str) -> dict[str, float]:
        v = pd.Series({c: p_by[resp].get(c, {}).get(bname, NAN) for c in cells}, dtype=float)
        return v.rank(ascending=False, method="min").to_dict()

    for bname, _ in BLOCKS:
        head = ranks("off", bname)
        for resp in (*LADDER, "rtp"):
            if resp not in p_by:
                continue
            rk = ranks(resp, bname)
            for c in cells:
                out.append(_row(section="beside", part="ladder_rank", **key, cell=c, response=resp, block=bname,
                                measure="rank_by_P", stat="rank", value=_f(rk.get(c)),
                                note=f"the 0 % headline's rank {_f(head.get(c)):g}"
                                     + ("; differs from the headline" if _f(rk.get(c)) != _f(head.get(c)) else "")))
    return out


# ------------------------------------------------------------------------------------------------ tallies per start


def start_tallies(outs: Sequence[Mapping[str, Any]], dates: Sequence[str], lag: int, holiday: set[str]) -> pd.DataFrame:
    """Each start's counts from its long replay's record (9.1 items 6 and 7; 8.3's holiday-hours reach): the passes,
    the funded accounts activated, the payouts' count and cash, the fees by the last month end, the exact runs checked
    and differing, and the requests dated on their own session (r2: the request's campaign day k is the arrival less
    the lag, and campaign day k plays the window's historical day k - 1, so its session is `dates[s + k - 1]`); a request
    whose cash would arrive after the replay is not in the record and is not counted."""
    rows = []
    for x in outs:
        r = x["rec"]
        s = int(r["start_day"])
        fm = [float(v) for v in r["fees_month"] if v is not None and np.isfinite(float(v))]
        req = hit = 0
        for d in r["pay_days"]:
            k = int(d) - int(lag)
            i = s + k - 1
            if k >= 1 and 0 <= i < len(dates):
                req += 1
                hit += int(str(dates[i]) in holiday)
        cash = [float(c) for c in r["pay_cash"]]
        rows.append({"start_day": s, "start_date": str(r["start_date"]), "observed": int(r["observed"]),
                     "passes": len(r["pass_days"]), "funded_activated": len(r["funded_days"]),
                     "payouts": len(r["pay_days"]), "payout_cash": float(sum(cash)), "fees": fm[-1] if fm else 0.0,
                     "requests_dated": req, "requests_at_early_close_or_holiday_eve": hit,
                     "exact_checked": int(bool(x.get("checked"))), "exact_differing": len(x.get("differs") or ())})
    return pd.DataFrame(rows)


def counter_tallies(per_start: Mapping[int, Sequence[Mapping[str, Any]]]) -> pd.DataFrame:
    """Each start's counters from the channel (13.1 item 1): every counter summed over its accounts, the held sessions,
    and whether an account was held at sessions 63, 126 and 252."""
    rows = []
    for s, accts in per_start.items():
        tot = PP.total_counters(accts)
        rows.append({"start_day": int(s), **{k: int(v) for k, v in tot.items()},
                     **{f"held_at_{h}": int(any(h in set(a["held_days"]) for a in accts)) for h in HELD_SESSIONS}})
    return pd.DataFrame(rows)


def recorder_tallies(rec: Any, design: str, arm: str, response: str, cal: Mapping[str, pd.DataFrame]) -> pd.DataFrame:
    """Each start's counts from Q-94's records (7.1's kept columns and the accounts, always kept): the trades taken (by
    kind), the funded accounts recorded, lost (closed, not abandoned) and abandoned, the funded account-sessions, and
    the trades open at 13:00 CT on an FOMC-minutes day (E-050), executed at the tier's allowance."""
    from propedge.campaign.flip import slot_from_ct

    t13 = slot_from_ct(MINUTES_RELEASE_CT)
    mins = set(cal["config/calendar_fomc_minutes.csv"]["release_date"])
    tr = rec.trades(design, arm, response)
    ac = rec.accounts(design, arm, response)
    out: dict[int, dict[str, Any]] = {}
    if len(tr):
        open13 = tr["date"].astype(str).isin(mins) & (tr["entry_t"] < t13) & (tr["exit_t"] >= t13)
        g = pd.DataFrame({"start_day": tr["start_day"].astype(int), "trade": 1,
                          "funded": (tr["kind"].astype(str) == "funded").astype(int),
                          "combine": (tr["kind"].astype(str) == "combine").astype(int), "open13": open13.astype(int),
                          "open13_cap": (open13 & tr["at_cap"].astype(bool)).astype(int)}).groupby("start_day").sum()
        for s, r in g.iterrows():
            out.setdefault(int(s), {}).update({"trades": int(r["trade"]), "trades_funded": int(r["funded"]),
                                               "trades_combine": int(r["combine"]),
                                               "executed_open_at_minutes_release": int(r["open13"]),
                                               "executed_open_at_minutes_release_at_allowance": int(r["open13_cap"])})
    if len(ac):
        closed, ab = ac["closed"].astype(bool), ac["abandoned"].astype(bool)
        g = pd.DataFrame({"start_day": ac["start_day"].astype(int), "funded_recorded": 1,
                          "funded_lost": (closed & ~ab).astype(int), "funded_abandoned": ab.astype(int),
                          "funded_sessions": ac["days"].astype(int)}).groupby("start_day").sum()
        for s, r in g.iterrows():
            out.setdefault(int(s), {}).update({k: int(r[k]) for k in ("funded_recorded", "funded_lost",
                                                                      "funded_abandoned", "funded_sessions")})
    starts = sorted({int(r["start_day"]) for r in rec.per_start(design, arm, response)})
    cols = ("trades", "trades_funded", "trades_combine", "executed_open_at_minutes_release",
            "executed_open_at_minutes_release_at_allowance", "funded_recorded", "funded_lost", "funded_abandoned",
            "funded_sessions")
    return pd.DataFrame([{"start_day": s, **{c: int(out.get(s, {}).get(c, 0)) for c in cols}} for s in starts])


def merge_tallies(base: pd.DataFrame, *more: pd.DataFrame | None) -> pd.DataFrame:
    t = base
    for x in more:
        if x is not None and len(x):
            t = t.merge(x, on="start_day", how="left")
    return t


# ------------------------------------------------------------------------------------------------ divergences (item 6)


DIVERGE_COLUMNS = ("passes", "funded_activated", "payouts", "payout_cash", "fees", "trades", "trades_funded",
                   "trades_combine", "funded_lost", "funded_abandoned", "funded_sessions", "held_unchanged",
                   "held_rescued", "held_r_changed", "held_sessions")


def diverge_rows(cell: pd.DataFrame, base: pd.DataFrame, key: dict[str, Any]) -> list[dict[str, Any]]:
    """9.1 item 6: what diverges, cell against base, per block (each start's whole long replay, the blocks purged at
    252): each count's totals, the difference and the per-start mean difference; the payouts' mean size; the held
    account-sessions by class as a share of the cell's funded account-sessions. The evaluations bought and the realised
    risk are the gate's (pp_gate.csv, part `diverge`): 7.1's recorder keeps no column holding them on the replay."""
    out = []
    a, b = cell.set_index("start_day"), base.set_index("start_day")
    recs = records_of(base[base["start_day"].isin(a.index)])
    for bname, which in BLOCKS:
        days = block_days(recs, which, WHOLE)
        k = dict(section="diverge", part="diverge", **key, block=bname, h=WHOLE, n=len(days))
        for col in DIVERGE_COLUMNS:
            if col not in a.columns or col not in b.columns:
                continue
            x, y = a.loc[days, col].to_numpy(float), b.loc[days, col].to_numpy(float)
            for stat, v in (("cell_total", x.sum()), ("base_total", y.sum()), ("cell_less_base", x.sum() - y.sum()),
                            ("mean_difference_per_start", (x - y).mean() if len(days) else np.nan)):
                out.append(_row(**k, measure=col, stat=stat, value=float(v)))
        for who, t in (("cell", a), ("base", b)):
            pay, cash = t.loc[days, "payouts"].to_numpy(float).sum(), t.loc[days, "payout_cash"].to_numpy(float).sum()
            out.append(_row(**k, measure="payout_size_mean", stat=who, value=float(cash / pay) if pay else np.nan,
                            note="the cash to the user per payout"))
        if "funded_sessions" in a.columns:
            fs = a.loc[days, "funded_sessions"].to_numpy(float).sum()
            for cls in PP.HELD_CLASSES:
                if f"held_{cls}" in a.columns:
                    out.append(_row(**k, measure=f"share_funded_sessions_held_{cls}", stat="cell",
                                    value=float(a.loc[days, f"held_{cls}"].to_numpy(float).sum() / fs) if fs else np.nan,
                                    note="6.3's class, of the cell's funded account-sessions (the recorder's accounts)"))
        for what in ("evaluations_bought", "realised_risk_within_line"):
            out.append(_row(**k, measure=what, stat="not_on_the_replay", value=np.nan,
                            note="7.1's recorder keeps the trade columns date, entry_t, exit_t, at_cap and kind, none of "
                                 "which holds it; read on the gate's paths beside (pp_gate.csv, part diverge)"))
    return out


# ------------------------------------------------------------------------------------------------ mechanics (8.3)


def _same(a: Any, b: Any) -> bool:
    """Equal as data: floats with NaN equal to NaN, sequences and mappings element by element."""
    if isinstance(a, Mapping) and isinstance(b, Mapping):
        return set(a) == set(b) and all(_same(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple, np.ndarray)) and isinstance(b, (list, tuple, np.ndarray)):
        return len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b))
    try:
        fa, fb = float(a), float(b)
        if math.isnan(fa) and math.isnan(fb):
            return True
    except (TypeError, ValueError):
        pass
    return bool(a == b)


def identical_outputs(outs: Sequence[Mapping[str, Any]], base_outs: Sequence[Mapping[str, Any]]) -> bool:
    """8.3: a cell identical to its base on every start (each start's record, daily path, response and exact runs)."""
    if len(outs) != len(base_outs):
        return False
    keys = ("rec", "daily", "response", "differs")
    return all(_same({k: x.get(k) for k in keys}, {k: y.get(k) for k in keys}) for x, y in zip(outs, base_outs))


def differs_within(r: Mapping[str, Any], b: Mapping[str, Any], h: int) -> bool:
    m = h // MONTH
    same = (_same(r["net_month"][:m], b["net_month"][:m]) and
            [d for d in r["pay_days"] if d <= h] == [d for d in b["pay_days"] if d <= h] and
            [d for d in r["pass_days"] if d <= h] == [d for d in b["pass_days"] if d <= h])
    return not same


def mechanics_rows(key: dict[str, Any], run: Mapping[str, Any], base_run: Mapping[str, Any]) -> list[dict[str, Any]]:
    """8.3 for one run against its base, per block: the shares of starts differing within 63, 126 and 252 sessions (a
    month-end net, a payout's or a pass's day up to h); the class's counts and the held sessions over each start's long
    replay (the blocks purged at 252); the share of starts with an account held at sessions 63, 126 and 252; the
    holiday-hours reach (cell and base); the minutes-release count where the run was recorded."""
    out = []
    outs, bouts = run["outs"], base_run["outs"]
    t, bt = run["tally"].set_index("start_day"), base_run["tally"].set_index("start_day")
    by = {int(x["rec"]["start_day"]): x["rec"] for x in outs}
    bb = {int(x["rec"]["start_day"]): x["rec"] for x in bouts}
    recs = [{"start_day": s, "start_date": str(r["start_date"]), "observed": int(r["observed"])} for s, r in by.items()
            if s in bb]
    minimal = key.get("mode") == "minimal"
    for bname, which in BLOCKS:
        k = dict(section="mechanics", part="mechanics", **key, block=bname)
        for h in DIFFER_SESSIONS:
            days = block_days(recs, which, h)
            v = [differs_within(by[s], bb[s], h) for s in days]
            out.append(_row(**k, measure=f"share_starts_differing_within_{h}", stat="share",
                            value=float(np.mean(v)) if v else np.nan, n=len(v), h=h,
                            note="differs: a month-end net, a payout's or a pass's day up to session h"))
        days = block_days(recs, which, WHOLE)
        for col in (*PP.COUNTER_KEYS, "held_sessions"):
            if col not in t.columns:
                continue
            note = ""
            if minimal and col.startswith("held_") and col not in ("held_closes", "held_sessions"):
                note = ("the minimal rescue: only the rescued reads were read under the rule; the unchanged and "
                        "R-changed reads were answered with the firm's count (n4)")
            elif col.startswith("cons_"):
                note = "the engine's count, for any class"
            out.append(_row(**k, measure=col, stat="count", value=float(t.loc[days, col].sum()), n=len(days), h=WHOLE,
                            note=note or "the class's counters, over each start's long replay"))
        for h in HELD_SESSIONS:
            dh = block_days(recs, which, h)
            col = f"held_at_{h}"
            if col in t.columns:
                out.append(_row(**k, measure=f"share_starts_held_at_session_{h}", stat="share",
                                value=float(t.loc[dh, col].mean()) if dh else np.nan, n=len(dh), h=h))
        for col, note in (("requests_at_early_close_or_holiday_eve", "E-029's calendar; each request dated on its own "
                                                                     "session (the arrival less the lag)"),
                          ("executed_open_at_minutes_release", "E-050's calendar; Q-94's records"),
                          ("executed_open_at_minutes_release_at_allowance",
                           "timed by each block's single logged exit (exit_t); at the tier's allowance (at_cap)")):
            if col not in t.columns:
                continue
            for who, tab in (("cell", t), ("base", bt)):
                if col in tab.columns:
                    out.append(_row(**k, measure=col, stat=who, value=float(tab.loc[days, col].sum()), n=len(days),
                                    h=WHOLE, note=note))
        if "requests_dated" in t.columns:
            out.append(_row(**k, measure="requests_dated", stat="cell", value=float(t.loc[days, "requests_dated"].sum()),
                            n=len(days), h=WHOLE, note="a request whose cash arrives after the replay is not in its "
                                                       "record and is not dated"))
    return out


def stream_rows(design: str, job: dict[str, Any], cal: Mapping[str, pd.DataFrame]) -> list[dict[str, Any]]:
    """8.3 per stream: the offered trades open at 13:00 CT on an FOMC-minutes day (the blocks' own entry and exit
    times), and E-029's voided days -- the starts, per block and horizon, whose h sessions hold one (listed, never
    voided here)."""
    from propedge.campaign.flip import slot_from_ct

    t13 = slot_from_ct(MINUTES_RELEASE_CT)
    mins = set(cal["config/calendar_fomc_minutes.csv"]["release_date"])
    n = 0
    for d, b in zip(job["dates"], job["blocks"]):
        if str(d) in mins and b.entry_t is not None and b.exit_t is not None:
            n += int(np.sum((np.asarray(b.entry_t) < t13) & (np.asarray(b.exit_t) >= t13)))
    rows = [_row(section="mechanics", part="stream", design=design, block="all", measure="offered_open_at_minutes_release",
                 stat="count", value=float(n), note="the stream's own offers (the same in every cell)")]
    dates = [str(d) for d in job["dates"]]
    nd = len(dates)
    recs = [{"start_day": s, "start_date": dates[s], "observed": min(WHOLE, nd - s)} for s in range(nd)]
    di = {d: i for i, d in enumerate(dates)}
    for v in VOIDED_DAYS:
        for h in RD.HORIZON_SET:
            for bname, which in BLOCKS:
                days = block_days(recs, which, h)
                k = sum(1 for s in days if v in di and s <= di[v] < s + h)
                rows.append(_row(section="mechanics", part="stream", design=design, block=bname,
                                 measure=f"starts_whose_window_holds_{v}", stat="count", value=float(k), n=len(days),
                                 h=h, note="E-029's voided day: listed, never voided here"))
    return rows


def check_times(design: str, job: dict[str, Any], lo_ct: str, hi_ct: str) -> list[str]:
    """The blocks' entry times are on the engine's clock (minutes since 17:00 CT, D-345 (7)): every offered entry
    between `lo_ct` and `hi_ct`, or the minutes count's clock is wrong (refused)."""
    from propedge.campaign.flip import slot_from_ct

    lo, hi = slot_from_ct(lo_ct), slot_from_ct(hi_ct)
    bad = sum(int(np.sum((np.asarray(b.entry_t) < lo) | (np.asarray(b.entry_t) > hi)))
              for b in job["blocks"] if b.entry_t is not None)
    return [] if not bad else [f"{design}: {bad} offered entries outside {lo_ct}-{hi_ct} CT on the engine's clock"]


# ------------------------------------------------------------------------------------------------ oracles (8.2)


def replay_oracle_rows(key: dict[str, Any], outs: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """8.2 on a replay, where its outputs allow (r1): every payout's request -- its cash plus the fee over the split --
    within [the minimum, the cap]. The replay's outputs carry no balance at a request, no floor and no account's own
    payouts, so "at most 50 % of the balance", `lock`'s "no first payout below the lock" and `half`'s "half of the
    maximum" are not checkable on it: they are checked exactly on every gate path (`GateTally`) and on toys (T-2, T-5,
    T-7). Refused on any payout outside the bounds."""
    r = PP.ledger_rules()
    split, fee, pmin, cap = float(r.profit_split), float(r.payout_fee), float(r.payout_min), float(r.std_cap)
    bad = n = 0
    for x in outs:
        for c in x["rec"]["pay_cash"]:
            req = (float(c) + fee) / split
            n += 1
            bad += int(not (pmin - 1e-6 <= req <= cap + 1e-6))
    if bad:
        raise Refused(f"8.2: {key}: {bad} of {n} payouts outside the request's bounds")
    return [_row(section="oracle", part="replay", **key, measure="payouts within the request's bounds", stat="holds",
                 value=1.0, n=n, note="the request (cash plus fee over the split) within the minimum and the cap"),
            _row(section="oracle", part="replay", **key, measure="the other three oracles", stat="not_checkable",
                 value=np.nan, n=n, note="the replay's outputs hold no balance at a request, no floor, no account's own "
                                         "payouts: checked on every gate path and on toys (T-2, T-5, T-7)")]


class GateTally:
    """8.2 on a gate: wraps the gate's `path_hook` (called with every (shift, level)'s paths, in the process that calls
    the gate) and counts, from each funded account's engine record (`FundedRecord`), the zero-edge twin's gross payouts
    per funded account, and on the Standard path: the first request against `payout_frac` x min(the balance's
    maximum share x `balance_at_first_payout`, the cap), to 1e-9 (`half`'s oracle, and the maximum for `max`); a first
    request below the minimum or above the maximum; under `lock`, a first payout with the closes' high before it
    (`peak_before_payout`) below the lock balance (the MLL not locked); a later request outside [the minimum, the cap].
    It keeps counts only, never the paths."""

    def __init__(self, inner: Any, cell: str):
        self.inner = inner
        self.frac = PP.cell_payout_frac(cell)
        self.lock = PP.CELL_LEVERS[cell][0] == "lock"
        self.counts: Counter = Counter()
        self.gross = [0.0, 0.0, 0]                       # sum, sum of squares, funded accounts (every shift)

    def __call__(self, shift: str, p: float, paths: Sequence[Any]) -> dict[str, Any]:
        self.tally(paths)
        return self.inner(shift, p, paths) if self.inner is not None else {}

    def tally(self, paths: Sequence[Any]) -> None:
        r = PP.ledger_rules()
        split, fee, pmin, cap = float(r.profit_split), float(r.payout_fee), float(r.payout_min), float(r.std_cap)
        mfrac, lock_b = float(r.payout_max_frac_of_balance), PP.lock_balance(r)
        c = self.counts
        for x in paths:
            for f in x.funded:
                g = float(f.gross_paid)
                self.gross[0] += g
                self.gross[1] += g * g
                self.gross[2] += 1
                if int(f.n_payouts) <= 0 or bool(getattr(f, "consistency_forced", False)):
                    continue
                reqs = [(float(v) + fee) / split for v in f.payout_cash]
                r1, b1 = reqs[0], float(f.balance_at_first_payout)
                want = self.frac * min(mfrac * b1, cap)
                c["first_requests_checked"] += 1
                c["first_request_not_frac_of_max"] += int(abs(r1 - want) > ORACLE_TOL * max(1.0, abs(want)))
                c["first_request_above_max"] += int(r1 > min(mfrac * b1, cap) * (1 + ORACLE_TOL))
                c["first_request_below_min"] += int(r1 < pmin - 1e-6)
                if self.lock:
                    c["lock_first_payouts_checked"] += 1
                    c["lock_first_payout_below_lock"] += int(float(f.peak_before_payout) < lock_b - 1e-9)
                for q in reqs[1:]:
                    c["later_requests_checked"] += 1
                    c["later_request_out_of_bounds"] += int(not (pmin - 1e-6 <= q <= cap + 1e-6))

    BAD = ("first_request_not_frac_of_max", "first_request_above_max", "first_request_below_min",
           "lock_first_payout_below_lock", "later_request_out_of_bounds")


def gate_oracle_rows(key: dict[str, Any], twin: bool, tally: GateTally) -> list[dict[str, Any]]:
    """8.2 on one gate: refused on any request oracle count above zero, and on the twin when the mean gross payouts per
    funded account exceed the lock balance (the martingale bound) by more than three standard errors."""
    c = tally.counts
    bad = {k: int(c.get(k, 0)) for k in GateTally.BAD if int(c.get(k, 0))}
    if bad:
        raise Refused(f"8.2: {key} {'twin' if twin else ''}: request oracles fail on the gate's paths: {bad}")
    rows = [_row(section="oracle", part="gate", **key, measure=k, stat="count", value=float(c.get(k, 0)),
                 note="the engine's funded records on every path of the gate (first payouts exactly)")
            for k in ("first_requests_checked", *GateTally.BAD[:3], "lock_first_payouts_checked",
                      "lock_first_payout_below_lock", "later_requests_checked", "later_request_out_of_bounds")]
    if twin:
        s, ss, n = tally.gross
        if n:
            m = s / n
            se = math.sqrt(max(ss / n - m * m, 0.0) * n / (n - 1)) / math.sqrt(n) if n > 1 else 0.0
            bound = PP.lock_balance()
            if m > bound + 3.0 * se:
                raise Refused(f"8.2: {key} twin: mean gross payout {m:.1f} exceeds {bound:.0f} + 3 se")
            rows.append(_row(section="oracle", part="gate", **key, measure="zero-edge twin martingale bound",
                             stat="mean_gross_per_funded_account", value=m, n=n,
                             note=f"bound {bound:.0f} + 3 x {se:.1f} (the tolerance: three standard errors)"))
    return rows


# ------------------------------------------------------------------------------------------------ the run


def _run_key(design: str, arm: str, cell: str, mode: str, response: str) -> tuple[str, str, str, str, str]:
    return (design, arm, cell, mode, response)


def run_reading(inputs: Inputs, *, designs: Sequence[str] = DESIGNS, starts: int | None = None, workers: int = 1,
                honesty_reps: int = RD.HONESTY_SERIES, honesty_seed: int | None = None, approved_limits: Sequence[
                    Mapping[str, Any]] = (), gate: bool = True, time_window: tuple[str, str] | None = None,
                sensitivity_design: str = SENSITIVITY_DESIGN, root: Path = ROOT,
                log: Callable[[str], None] = print) -> dict[str, Any]:
    """The whole reading in 14 step 2's order across both designs; raises `Refused` at the first failed check (nothing
    returned, so nothing written)."""
    import user_journey as UJ

    from extended import replay_records as RRec
    from extended import user_beside as B

    seed = declared_seed("9.2 item 7's honesty series", root) if honesty_seed is None else int(honesty_seed)
    cal = calendar_frames(root)
    run_list = runs_of(designs, sensitivity_design)
    jobs = {d: inputs.jobs(d) for d in designs}
    if time_window is not None:
        for d in designs:
            for arm in ARMS:
                probs = check_times(d, jobs[d][arm], *time_window)
                if probs:
                    raise Refused("; ".join(probs))
    hol = {d: holiday_sessions(cal, jobs[d]["verdict"]["dates"]) for d in designs}
    runs: dict[tuple, dict[str, Any]] = {}
    ident: list[dict[str, Any]] = []

    def replay(d: str, arm: str, cell: str, mode: str, rname: str, record: bool) -> dict[str, Any]:
        job = cell_job(jobs[d][arm], cell)
        chosen = UJ.start_choice(len(job["blocks"]), starts)
        rec = RRec.ReplayRecorder(columns=RECORD_COLUMNS) if record else None
        cnt = PP.ReplayCounters()
        cls = PP.REF_CLASS if cell == "ref" else PP.cell_class(cell, mode)
        outs = B.run_starts(d, arm, B.BY_NAME[rname], job, chosen, workers, funded_account_cls=cls, recorder=rec,
                            counters=cnt)
        return {"outs": outs, "rec": rec, "cnt": cnt, "job": job}

    def keep(d: str, arm: str, cell: str, mode: str, rname: str, x: dict[str, Any]) -> None:
        """A checked run kept for (d) and the reading: its outputs, and its counts and records compacted per start."""
        lag = int(x["job"]["args"]["path"]["payout_lag_days"])
        t = start_tallies(x["outs"], x["job"]["dates"], lag, hol[d])
        ct = counter_tallies(x["cnt"].starts(d, arm, rname))
        rt = recorder_tallies(x["rec"], d, arm, rname, cal) if x["rec"] is not None else None
        runs[_run_key(d, arm, cell, mode, rname)] = {"outs": x["outs"], "tally": merge_tallies(t, ct, rt)}

    # (a) every design's ref at off, both arms, recorded and counted: 8.1 item 2's repeat and item 4
    for d in designs:
        for arm in ARMS:
            x = replay(d, arm, "ref", "declared", "off", True)
            probs = inputs.identity_problems(d, arm, x["outs"]) + [f"recorder: {p}" for p in x["rec"].problems()]
            tot = PP.lever_totals(r for v in x["cnt"].starts(d, arm, "off").values() for r in v)
            if any(tot.values()):
                probs.append(f"8.1 item 4: the levers are not off in ref ({tot})")
            probs += read_check(x["cnt"], d, arm, "off", x["job"])
            ident.append(_row(section="identity", design=d, arm=arm, cell="ref", mode="declared",
                              measure="8.1 items 2 and 4", stat="holds", value=float(not probs), n=len(x["outs"]),
                              note="; ".join(probs[:4])))
            if probs:
                raise Refused(f"{d} {arm} ref: " + "; ".join(probs[:6]))
            log(f"identity HOLDS: {d} {arm} ref (8.1 items 2's repeat and 4), {len(x['outs'])} starts")
            keep(d, arm, "ref", "declared", "off", x)
    # (b) every design's ref beside, verdict arm: 8.1 item 6
    for d in designs:
        for rname in BESIDE:
            x = replay(d, "verdict", "ref", "declared", rname, False)
            probs = inputs.ladder_problems(d, rname, x["outs"])
            tot = PP.lever_totals(r for v in x["cnt"].starts(d, "verdict", rname).values() for r in v)
            if any(tot.values()):                        # the levers' own counts; the cons_* are the engine's (m4)
                probs.append(f"8.1 item 4 under {rname}: the levers are not off in ref ({tot})")
            ident.append(_row(section="identity", design=d, arm="verdict", cell="ref", mode="declared", response=rname,
                              measure="8.1 item 6", stat="holds", value=float(not probs), n=len(x["outs"]),
                              note="; ".join(probs[:4])))
            if probs:
                raise Refused(f"{d} ref {rname}: " + "; ".join(probs[:6]))
            keep(d, "verdict", "ref", "declared", rname, x)
        log(f"identity HOLDS: {d} ref beside (8.1 item 6)")
    # (c) every new run: item 5 and the held-state rule's firing before anything of it is read; its readings beside
    for d, cell, mode in run_list:
        if cell == "ref":
            continue
        for arm in ARMS:
            x = replay(d, arm, cell, mode, "off", True)
            probs = [f"8.1 item 5 (recorder): {p}" for p in x["rec"].problems()]
            probs += [f"the held-state rule (m2): {p}" for p in read_check(x["cnt"], d, arm, "off", x["job"])]
            ident.append(_row(section="identity", design=d, arm=arm, cell=cell, mode=mode, measure="8.1 item 5",
                              stat="holds", value=float(not probs), n=len(x["outs"]), note="; ".join(probs[:4])))
            if probs:
                raise Refused(f"{d} {arm} {cell} ({mode}): " + "; ".join(probs[:6]))
            keep(d, arm, cell, mode, "off", x)
        if mode == "declared":
            for rname in BESIDE:
                x = replay(d, "verdict", cell, mode, rname, False)
                rp = read_check(x["cnt"], d, "verdict", rname, x["job"])
                if rp:
                    raise Refused(f"{d} {cell} {rname}: the held-state rule (m2): " + "; ".join(rp[:4]))
                keep(d, "verdict", cell, mode, rname, x)
        log(f"checked: {d} {cell} ({mode})")
    # (c) then the new cells' gates: point and bound, and the zero-edge twin; each path's held-state rule checked (n3)
    gates: dict[tuple[str, str, bool], dict[str, Any]] = {}
    if gate:
        from extended import gate as XG

        for d in designs:
            for cell in NEW_CELLS:
                for twin in (False, True):
                    g = inputs.gate_call(d, cell, twin)
                    cnt = PP.GateCounters()
                    kw = dict(g["kw"])
                    tally = GateTally(kw.get("path_hook"), cell)
                    kw["path_hook"] = tally
                    df, _ = XG.run_gate(kw.pop("blocks"), workers=int(workers), funded_account_cls=PP.cell_class(cell),
                                        counters=cnt, **kw)
                    probs = gate_read_check(cnt, int(kw["horizon_days"]))
                    if probs:
                        raise Refused(f"{d} {cell} gate{' twin' if twin else ''}: the held-state rule (n3): "
                                      + "; ".join(probs[:4]))
                    held = {(shift, p): (PP.total_counters(r for rows in cnt.paths(shift, p).values() for r in rows),
                                         len(cnt.paths(shift, p))) for shift, p in sorted({k[:2] for k in cnt.keys()})}
                    gates[(d, cell, twin)] = {"df": df, "g": g, "tally": tally, "held": held,
                                              "horizon_days": int(kw["horizon_days"])}     # the counts' totals only (n9)
                    del cnt
                log(f"gate: {d} {cell} (point, bound, zero-edge twin)")
    # (d) 8.2's oracles on every replay and every gate, then 8.3's mechanics
    rows: list[dict[str, Any]] = list(ident)
    for (d, arm, cell, mode, rname), run in runs.items():
        rows += replay_oracle_rows(dict(design=d, arm=arm, cell=cell, mode=mode, response=rname), run["outs"])
    for (d, cell, twin), gx in gates.items():
        rows += gate_oracle_rows(dict(design=d, cell=cell, mode="declared", block="twin" if twin else "gate"), twin,
                                 gx["tally"])
    no_effect: set[tuple] = set()
    for d in designs:
        rows += stream_rows(d, jobs[d]["verdict"], cal)
    for (d, arm, cell, mode, rname), run in runs.items():
        if cell == "ref" or (rname != "off" and rname != "rtp"):
            continue
        base = runs[_run_key(d, arm, "ref", "declared", rname)]
        key = dict(design=d, arm=arm, cell=cell, mode=mode, response=rname, base="ref")
        if identical_outputs(run["outs"], base["outs"]):
            no_effect.add((d, arm, cell, mode, rname))
            rows.append(_row(section="mechanics", part="no_effect", **key, block="all", measure="no effect on these trades",
                             stat="identical_on_every_start", value=1.0, n=len(run["outs"]),
                             note="identical to its base on every start: nothing more is read for it (8.3)"))
            continue
        rows += mechanics_rows(key, run, base)
    for (d, arm, cell, mode, rname), run in runs.items():   # a beside run identical to its base is read no further
        if cell != "ref" and rname in LADDER and (d, arm, cell, mode, rname) not in no_effect and \
                identical_outputs(run["outs"], runs[_run_key(d, arm, "ref", "declared", rname)]["outs"]):
            no_effect.add((d, arm, cell, mode, rname))
            rows.append(_row(section="mechanics", part="no_effect", design=d, arm=arm, cell=cell, mode=mode,
                             response=rname, base="ref", block="all", measure="no effect on these trades",
                             stat="identical_on_every_start", value=1.0, n=len(run["outs"]),
                             note="identical to its base on every start: nothing more is read for it (8.3)"))
    log("oracles and mechanics: done")
    # the reading
    honesty: dict = {}
    rows += reading_rows(runs, designs, honesty, no_effect)
    gate_frame = gate_rows(gates, inputs)
    hon = honesty_table([k for k in honesty], seed, honesty_reps)
    label_rows([r for r in rows if r["part"] == "paired"], hon)
    rows += [_row(section="coverage", h=int(r.h), n=int(r.n_w), measure=r.shape, stat=s, value=float(getattr(r, s)),
                  note=f"shape {r.shape_index}; {honesty_reps} series; seed key [declared, 1, {r.shape_index}, {r.h}, "
                       f"{r.n_w}]") for r in hon.itertuples() for s in ("coverage", "miss_above", "miss_below")]
    for r in rows:                                     # 14's sections: the readings beside in `beside` (n6)
        if r["response"] != "off" and r["section"] in ("scorecard", "paired", "diverge", "mechanics"):
            r["section"] = "beside"
    reading = pd.DataFrame(rows, columns=list(ROW_KEYS))
    menu = menu_table(reading, approved_limits, no_effect)
    return {"reading": reading, "gate": gate_frame, "menu": menu, "honesty_seed": seed,
            "honesty_settings": sorted(honesty), "runs": run_list, "no_effect": sorted(no_effect)}


def reading_rows(runs: Mapping[tuple, Mapping[str, Any]], designs: Sequence[str], honesty: dict,
                 no_effect: set = frozenset()) -> list[dict[str, Any]]:
    """9.1 on the kept runs (also called on toy runs by T-3): each run's card and distributions, each cell paired with
    its base and `lock_half` with each lever alone, the minimal rescue with its declared cell, the divergences, CVaR10,
    and across the four policies the frontier, S6's form, the evenness trade-off and the ladder's ranking."""
    rows: list[dict[str, Any]] = []
    frames: dict[tuple, pd.DataFrame] = {}
    cards: dict[tuple, dict[str, dict]] = {}
    for (d, arm, cell, mode, rname), run in runs.items():
        frames[(d, arm, cell, mode, rname)] = start_frame(d, arm, rname, run["outs"])
    for k5, t in frames.items():
        d, arm, cell, mode, rname = k5
        recs = [x["rec"] for x in runs[k5]["outs"]]
        cards[k5] = {bname: card_of(recs, which) for bname, which in BLOCKS}
        if k5 in no_effect:
            continue
        key = dict(design=d, arm=arm, cell=cell, mode=mode, response=rname)
        rows += card_rows(cards[k5], key)
        rows += distribution_rows(t, key)
        rows += cvar_rows(t, None, key)
    pairs = []
    for (d, arm, cell, mode, rname) in frames:
        if cell == "ref":
            continue
        pairs.append(((d, arm, cell, mode, rname), (d, arm, "ref", "declared", rname)))
        if cell == "lock_half":
            for lever in ("lock", "half"):
                pairs.append(((d, arm, cell, mode, rname), (d, arm, lever, mode, rname)))
        if mode == "minimal":
            pairs.append(((d, arm, cell, mode, rname), (d, arm, cell, "declared", rname)))
    for ck, bk in pairs:
        if ck in no_effect or bk not in frames:
            continue
        key = dict(design=ck[0], arm=ck[1], cell=ck[2], mode=ck[3], response=ck[4], base=bk[2] if bk[3] == ck[3] or
                   bk[2] == "ref" else f"{bk[2]} ({bk[3]})")
        rows += paired_rows(frames[ck], frames[bk], key, honesty)
        cr, br = [x["rec"] for x in runs[ck]["outs"]], [x["rec"] for x in runs[bk]["outs"]]
        rows += paired_card_rows(cr, br, key)
        rows += cvar_rows(frames[ck], frames[bk], key)
        if "tally" in runs[ck] and "tally" in runs[bk]:
            rows += diverge_rows(runs[ck]["tally"], runs[bk]["tally"], key)
    # across the four policies of a base, per design, arm and response (the declared rule)
    groups = sorted({(d, arm, rname) for (d, arm, cell, mode, rname) in frames if mode == "declared"})
    for d, arm, rname in groups:
        fr = {c: frames[(d, arm, c, "declared", rname)] for c in POLICY_CELLS if (d, arm, c, "declared", rname) in frames}
        cd = {c: cards[(d, arm, c, "declared", rname)] for c in fr}
        key = dict(design=d, arm=arm, mode="declared", response=rname)
        rows += s6_rows(fr, key)
        rows += frontier_rows(cd, key)
        rows += evenness_rows(fr, cd, key)
    for d in designs:
        for arm in ARMS:
            p_by: dict[str, dict[str, dict[str, float]]] = {}
            for (dd, aa, cell, mode, rname), cd in cards.items():
                if dd == d and aa == arm and mode == "declared":
                    p_by.setdefault(rname, {})[cell] = {b: _f(cd[b]["P"]["value"]) for b, _ in BLOCKS}
            if len(p_by) > 1:
                rows += ladder_rank_rows(p_by, dict(design=d, arm=arm, mode="declared"))
    # the exact runs' differing count, every run (9.1 item 7; Q-76's EXACT_EVERY beside)
    for (d, arm, cell, mode, rname), run in runs.items():
        t = run.get("tally")
        if t is not None and "exact_checked" in t.columns:
            rows.append(_row(section="scorecard", part="exact_runs", design=d, arm=arm, cell=cell, mode=mode,
                             response=rname, block="all", measure="exact_runs_differing", stat="count",
                             value=float(t["exact_differing"].sum()), n=int(t["exact_checked"].sum()),
                             note="every start" if rname == "off" else "the starts whose index is a multiple of "
                                                                       "Q-76's EXACT_EVERY"))
    return rows


def read_check(cnt: Any, design: str, arm: str, response: str, job: dict[str, Any]) -> list[str]:
    """Q-106's m2: on every start, each held close the account outlives is followed by exactly one held read (the
    held-state rule fired where it must); the start's last session is its long replay's."""
    n = len(job["blocks"])
    out = []
    for s, rows in cnt.starts(design, arm, response).items():
        out += [f"start {s}: {p}" for p in PP.read_problems(rows, min(252, n - int(s)))]
    return out


def gate_read_check(cnt: Any, horizon_days: int) -> list[str]:
    """n3: the same check on every path of a gate (every shift and level), its last session `horizon_days - 1`."""
    out = []
    for shift, p, seed in cnt.keys():
        rows = cnt.paths(shift, p)[seed]
        out += [f"{shift} {p:g} path {seed}: {q}" for q in PP.read_problems(rows, int(horizon_days) - 1)]
    return out


def honesty_table(settings: Sequence[tuple[int, int]], seed: int, reps: int) -> pd.DataFrame:
    """9.2 item 7: the 21 shapes' coverage and misses at each (h, n_w)."""
    rows = []
    for h, n_w in sorted(set(settings)):
        for i, (kind, p, s) in enumerate(RD.SHAPES):
            c = RD.coverage(kind, int(n_w), int(h), RD.honesty_rng(seed, i, h, n_w), int(reps), p=p, s=s)
            rows.append({"h": int(h), "n_w": int(n_w), "shape_index": i, "shape": RD.shape_name(kind, p, s), **c})
    return pd.DataFrame(rows, columns=["h", "n_w", "shape_index", "shape", "coverage", "miss_above", "miss_below"])


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


# ------------------------------------------------------------------------------------------------ the gates' file


def gate_rows(gates: Mapping[tuple, Mapping[str, Any]], inputs: Inputs) -> pd.DataFrame:
    """pp_gate.csv (14; n6): every gate row (part `gate_row`), the pairing with the base's registered paths (part
    `pairing`), 9.1 item 8's reading (part `reading`: growth on the required bankroll, the required bankroll, days to the
    first payout, payouts per path and a month) and item 6 on the gate (part `diverge`: the evaluations bought, the
    funded accounts, the share paid, the realised risk against P-14's line) each beside the base's registered gate
    row, and the held counts by shift (part `held_counts`, n3)."""
    import a3_brk30_cb20 as C

    parts: list[pd.DataFrame] = []
    extra: list[dict[str, Any]] = []
    base_rows = {d: inputs.base_gate_rows(d) for d in sorted({k[0] for k in gates})}
    for (d, cell, twin), gx in gates.items():
        df = gx["df"].copy()
        df.insert(0, "part", "gate_row")
        df.insert(1, "twin", twin)
        df.insert(1, "cell", cell)
        df.insert(1, "design", d)
        parts.append(df)
        g = {**gx["g"], "sink_paths": None}
        extra += [{**r, "part": "pairing", "twin": twin} for r in inputs.gate_pairing_rows(d, cell, twin, g)]
        for (shift, p), (tot, n_paths) in sorted(gx["held"].items()):
            for k, v in tot.items():
                extra.append(_row(section="gate", part="held_counts", design=d, cell=cell, mode="declared",
                                  block=shift, measure=k, stat="count", value=float(v), n=int(n_paths),
                                  note=f"enforcement {p:g}; every path; "
                                       f"{'the zero-edge twin' if twin else 'the gate'}") | {"twin": twin})
        if twin:
            continue
        g0 = gx["df"]
        g0 = g0[np.isclose(pd.to_numeric(g0["enforcement_p"], errors="coerce").astype(float), 0.0)] \
            if "enforcement_p" in g0.columns else g0.iloc[0:0]
        for shift in GATE_SHIFTS:
            mine = g0[g0["shift"].astype(str) == shift] if "shift" in g0.columns else g0.iloc[0:0]
            m = mine.iloc[0].to_dict() if len(mine) else {}
            b = base_rows.get(d, {}).get(shift, {})
            hd = _f(m.get("horizon_days", gx["horizon_days"]))
            for part, cols in (("reading", GATE_READING), ("diverge", GATE_DIVERGE)):
                for name, col in cols:
                    x, y = _f(m.get(col)), _f(b.get(col))
                    for stat, v in (("cell", x), ("base_registered", y), ("cell_less_base", x - y)):
                        extra.append(_row(section="gate", part=part, design=d, cell=cell, mode="declared", block=shift,
                                          measure=name, stat=stat, value=float(v), note=f"the gate row's {col}"
                                          + ("" if b else "; no registered base row here")) | {"twin": False})
            x, y = _f(m.get("mean_payouts_per_path")), _f(b.get("mean_payouts_per_path"))
            per = hd / MONTH if hd and math.isfinite(hd) else NAN
            for stat, v in (("cell", x / per), ("base_registered", y / per), ("cell_less_base", (x - y) / per)):
                extra.append(_row(section="gate", part="reading", design=d, cell=cell, mode="declared", block=shift,
                                  measure="payouts_a_month", stat=stat, value=float(v),
                                  note=f"mean payouts per path over the gate's {hd:g} sessions in months of {MONTH}")
                             | {"twin": False})
            x = _f(m.get("realised_to_intended_capped_risk"))
            extra.append(_row(section="gate", part="diverge", design=d, cell=cell, mode="declared", block=shift,
                              measure="realised_risk_within_line", stat="cell",
                              value=float(x >= float(C.REALISED_MIN)) if math.isfinite(x) else np.nan,
                              note=f"P-14's allowance-capped form of D-212 (1): realised over the capped intention at "
                                   f"least a3_brk30_cb20.REALISED_MIN (E-022 (1))") | {"twin": False})
    out = pd.concat(parts + ([pd.DataFrame(extra)] if extra else []), ignore_index=True) if parts or extra else \
        pd.DataFrame()
    return out


# ------------------------------------------------------------------------------------------------ the menu


#: the menu's columns an E-015 limit may name (`--limit`; 9.1 item 10)
def limit_columns() -> tuple[str, ...]:
    out = ["P_level", "P_mean_difference"]
    for g in GUARDED[1:]:
        out += [f"{g}_level", f"{g}_difference"]
    return tuple(out)


def limit_problems(limits: Sequence[Mapping[str, Any]]) -> list[str]:
    """Each limit names a menu column (`limit_columns`), a kind (`max` or `min`) and a finite bound."""
    out = []
    cols = set(limit_columns())
    for lim in limits:
        if lim.get("column") not in cols:
            out.append(f"limit {lim}: the column is not one of the menu's {sorted(cols)}")
        if lim.get("kind") not in ("max", "min"):
            out.append(f"limit {lim}: the kind is max or min")
        if not math.isfinite(_f(lim.get("bound"))):
            out.append(f"limit {lim}: the bound is not a number")
    return out


def menu_table(reading: pd.DataFrame, approved_limits: Sequence[Mapping[str, Any]],
               no_effect: set = frozenset()) -> pd.DataFrame:
    """9.1 item 10: each policy (declared rule; the minimal rescue is never on the menu) against `ref` -- its P and every
    guarded measure, level and paired difference on all starts, P's interval, the stability flag (P or any guarded
    measure with opposite signs on the early and late blocks), E-015's limits crossed (which, by how much), the labels;
    the references themselves (levels); the standing counts and notes."""
    rows = []
    paired = reading[reading["part"] == "paired"]
    n_int = int((paired["stat"] == "ci90_low").sum())
    pcard = reading[(reading["part"] == "card") & (reading["section"].isin(["paired", "beside"]))
                    & (reading["stat"] == "cell_less_base")]
    lcard = reading[(reading["part"] == "card") & (reading["stat"] == "value")]

    def first(df: pd.DataFrame, **eq: Any) -> float:
        m = np.ones(len(df), bool)
        for k, v in eq.items():
            m &= (df[k] == v).to_numpy()
        s = df[m]
        return float(s["value"].iloc[0]) if len(s) else np.nan

    combos = sorted({(r.design, r.arm, r.cell, r.response) for r in lcard.itertuples() if r.mode == "declared"}
                    | {(d, a, c, rs) for (d, a, c, mo, rs) in no_effect if mo == "declared"})
    for design, arm, cell, resp in combos:
        lv = lcard[(lcard["design"] == design) & (lcard["arm"] == arm) & (lcard["cell"] == cell)
                   & (lcard["response"] == resp) & (lcard["mode"] == "declared")]
        row: dict[str, Any] = {"design": design, "arm": arm, "cell": cell, "mode": "declared", "response": resp,
                               "base": "" if cell == "ref" else "ref",
                               "P_level": first(lv, block="all", measure="card_P")}
        for g in GUARDED[1:]:
            row[f"{g}_level"] = first(lv, block="all", measure=g)
        labels = ["described, not carried"]
        if cell == "ref":
            labels.append("the reference: its levels only")
        flipped: list[str] = []
        if cell != "ref":
            pp = paired[(paired["design"] == design) & (paired["arm"] == arm) & (paired["cell"] == cell)
                        & (paired["response"] == resp) & (paired["mode"] == "declared") & (paired["base"] == "ref")]
            pc = pcard[(pcard["design"] == design) & (pcard["arm"] == arm) & (pcard["cell"] == cell)
                       & (pcard["response"] == resp) & (pcard["mode"] == "declared") & (pcard["base"] == "ref")]
            row.update({"P_mean_difference": first(pp, block="all", measure="P", stat="mean"),
                        "P_ci90_low": first(pp, block="all", measure="P", stat="ci90_low"),
                        "P_ci90_high": first(pp, block="all", measure="P", stat="ci90_high"),
                        "P_mdd": first(pp, block="all", measure="P", stat="mdd"),
                        "P_n_w": first(pp, block="all", measure="P", stat="n_w")})
            lab = pp[(pp["block"] == "all") & (pp["measure"] == "P") & (pp["stat"] == "interval_label")]
            row["P_label"] = lab["note"].iloc[0] if len(lab) else ""
            e, l_ = first(pp, block="early", measure="P", stat="mean"), first(pp, block="late", measure="P", stat="mean")
            if np.isfinite(e) and np.isfinite(l_) and np.sign(e) * np.sign(l_) < 0:
                flipped.append("P")
            for g in GUARDED[1:]:
                row[f"{g}_difference"] = first(pc, block="all", measure=g)
                e, l_ = first(pc, block="early", measure=g), first(pc, block="late", measure=g)
                if np.isfinite(e) and np.isfinite(l_) and np.sign(e) * np.sign(l_) < 0:
                    flipped.append(g)
            if PP.CELL_LEVERS.get(cell, ("", ""))[1] == "half":
                labels.append("half: the request amount is an assumption (E-034)")
            if resp == "rtp" and PP.CELL_LEVERS.get(cell, ("", ""))[0] == "lock":
                labels.append("L1 on Standard-path accounts only")
            if (design, arm, cell, "declared", resp) in no_effect:
                labels.append("no effect on these trades")
        row["stable_across_blocks"] = not flipped
        row["flag"] = "not stable across blocks" if flipped else ""
        row["flipped_measures"] = "; ".join(flipped)
        crossed = []
        for lim in approved_limits:
            v = _f(row.get(lim["column"]))
            b = _f(lim["bound"])
            if math.isfinite(v) and ((lim["kind"] == "max" and v > b) or (lim["kind"] == "min" and v < b)):
                crossed.append(f"{lim['row']}: {lim['column']} {v:.6g} {'above' if lim['kind'] == 'max' else 'below'} "
                               f"{b:.6g} by {abs(v - b):.6g}")
        row["limits"] = ("; ".join(f"{x['row']}: {x['column']} {x['kind']} {x['bound']}" for x in approved_limits)
                         if approved_limits else "none approved before the run's commit: the menu is read without flags")
        row["limits_crossed"] = "; ".join(crossed)
        row["labels"] = "; ".join(labels)
        rows.append(row)
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
        "note_sensitivity": "the rule-sensitivity runs (the minimal rescue) are never on the menu: pp_reading.csv only",
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


# ------------------------------------------------------------------------------------------------ Q-44's comparison


LADDER_TEXT = ("design", "arm", "response", "start_date", "exact_runs_differing")


def _blank(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, str):
        return v.strip() in ("", "nan", "NaN", "None")
    try:
        return not math.isfinite(float(v))
    except (TypeError, ValueError):
        return False


def _text(v: Any) -> str:
    if _blank(v):
        return ""
    if isinstance(v, str):
        return v.strip()
    f = float(v)
    return str(int(f)) if f.is_integer() else repr(f)


def q44_problems(mine: pd.DataFrame, theirs: pd.DataFrame, what: str, *, all_starts: bool) -> list[str]:
    """8.1 item 6 (R4): our per-start rows (`user_readings.rounded(start_table(...))`) against Q-44's file read as text
    (`extended.results.read_result(..., text=True)`), start for start, every column that file writes, by E-010's
    comparator's rules: a blank equals only a blank; text as text (a day list such as "63" or "21 63" stays text); money
    to the cent (both rounded to it: equal within 1e-6); every other number within 1e-9."""
    out = []
    by: dict[int, dict] = {}
    for r in theirs.to_dict("records"):
        s = int(float(r["start_day"]))
        if s in by:
            return [f"{what}: start {s} twice in Q-44's file"]
        by[s] = r
    ours = {int(r["start_day"]): r for r in mine.to_dict("records")}
    missing = sorted(set(ours) - set(by))
    if missing:
        out.append(f"{what}: {len(missing)} of our starts not in Q-44's file (first: start {missing[0]})")
    if all_starts and set(by) - set(ours):
        out.append(f"{what}: {len(set(by) - set(ours))} of Q-44's {len(by)} starts not reproduced")
    common = sorted(set(ours) & set(by))
    for col in R.START_COLS:
        if col not in theirs.columns:
            out.append(f"{what}: Q-44's file has no column {col}")
            continue
        tol = 1e-6 if col in R.MONEY_COLS else 1e-9
        bad = []
        for s in common:
            a, b = ours[s].get(col), by[s].get(col)
            if col in LADDER_TEXT:
                same = _text(a) == _text(b)
            elif _blank(a) or _blank(b):
                same = _blank(a) and _blank(b)
            else:
                try:
                    same = abs(float(a) - float(b)) <= tol
                except (TypeError, ValueError):
                    same = False
            if not same:
                bad.append(s)
        if bad:
            s = bad[0]
            out.append(f"{what}: {col} differs from Q-44's file on {len(bad)} of {len(common)} starts (first: start "
                       f"{s}: {ours[s].get(col)!r} against {by[s].get(col)!r})")
    return out


class RealInputs(Inputs):
    """P-14's and P-16's registered designs, read through Stage 2's own builders (the lead's run, from a clean
    checkout, its reads authorised first): U1's jobs (`identity/user_beside_identity.py`'s `build`), U1's file for 8.1
    item 2's repeat, Q-44's per-start file (as text) for item 6, the registered gate calls (`identity/pp_identity.py`'s)
    and the registered gate rows."""

    GATE_FILES = {"p14": "a3_brk30_cb20_gate.csv", "p16": "rc_s150_all_gate.csv"}

    def __init__(self, starts: int | None = None, n_paths: int = 500, q44_path: Path | str | None = None):
        self.starts = starts
        self._n_paths = int(n_paths)
        self._jobs: dict[str, Any] = {}
        self._gate: dict[str, Any] = {}
        self._q44: pd.DataFrame | None = None
        self._q44_path = Path(q44_path) if q44_path is not None else ROOT / "results" / "user_beside_starts.csv"
        self._base_gate: dict[str, dict[str, dict[str, Any]]] = {}

    def n_paths(self) -> int:
        return self._n_paths

    def q44(self) -> pd.DataFrame:
        if self._q44 is None:
            from extended.results import read_result

            self._q44 = read_result(self._q44_path, text=True)
        return self._q44

    def preflight(self, designs: Sequence[str]) -> list[str]:
        """Before any read is authorised: Q-44's file verifies and reads as text with every column and the verdict rows
        of each design and response beside; each design's registered gate row is one row a shift at 0 %, the placement
        off, with the columns 9.1 items 6 and 8 read."""
        out = []
        try:
            f = self.q44()
        except Exception as exc:                          # noqa: BLE001 -- any failure here is a refusal before reads
            return [f"Q-44's per-start file: {exc}"]
        miss = [c for c in R.START_COLS if c not in f.columns]
        if miss:
            out.append(f"Q-44's per-start file lacks {miss}")
        else:
            for d in designs:
                for resp in BESIDE:
                    if not ((f["design"] == d) & (f["arm"] == "verdict") & (f["response"] == resp)).any():
                        out.append(f"Q-44's per-start file has no {d} verdict {resp} rows")
        for d in designs:
            try:
                rows = self.base_gate_rows(d)
            except Exception as exc:                      # noqa: BLE001
                out.append(f"{d}'s registered gate rows: {exc}")
                continue
            if sorted(rows) != sorted(GATE_SHIFTS):
                out.append(f"{d}'s registered gate rows: shifts {sorted(rows)}, not {list(GATE_SHIFTS)}")
            for shift, r in rows.items():
                need = [c for _, c in (*GATE_READING, *GATE_DIVERGE)] + ["mean_payouts_per_path"]
                miss = [c for c in need if c not in r]
                if miss:
                    out.append(f"{d} {shift}'s registered gate row lacks {miss}")
        return out

    def base_gate_rows(self, design: str) -> dict[str, dict[str, Any]]:
        """The base's registered gate rows (`section` gate, 0 %, the placement off), one a shift, as `rc_screen.
        p14_beside` reads P-14's (read, never rerun); refused unless exactly one row a shift."""
        if design in self._base_gate:
            return self._base_gate[design]
        from propedge import RESULTS_DIR
        from propedge.reporting.results import read_result

        d = read_result(RESULTS_DIR / self.GATE_FILES[design])
        g = d[(d["section"].astype(str) == "gate") & np.isclose(d["enforcement_p"].astype(float), 0.0)
              & (d["placement"].astype(str) == "off")]
        out = {}
        for shift in GATE_SHIFTS:
            s = g[g["shift"].astype(str) == shift]
            if len(s) != 1:
                raise ValueError(f"{self.GATE_FILES[design]}: {len(s)} gate rows at 0 % for {shift}, not one")
            out[shift] = s.iloc[0].to_dict()
        self._base_gate[design] = out
        return out

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
        start, every column that file writes, at its precision (money to the cent): the file read as text (R4)."""
        f = self.q44()
        theirs = f[(f["design"] == design) & (f["arm"] == "verdict") & (f["response"] == response)]
        mine = R.rounded(R.start_table(design, "verdict", response, outs))
        return q44_problems(mine, theirs, f"{design} {response}", all_starts=self.starts is None)

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
                k = dict(section="gate", part="pairing", design=design, cell=cell, mode="declared", block=shift,
                         measure=col, n=int(len(a)), note="the zero-edge twin" if twin else "")
                rows.append(_row(**k, stat="cell_mean", value=float(np.nanmean(x)) if x.size else np.nan))
                if len(b) == len(a) and col in b and len(a):
                    y = pd.to_numeric(b[col], errors="coerce").to_numpy(float)
                    rows += [_row(**k, stat="base_registered_mean", value=float(np.nanmean(y))),
                             _row(**k, stat="cell_less_base_mean", value=float(np.nanmean(x - y)))]
                else:
                    rows.append(_row(**k, stat="base_registered_mean", value=np.nan,
                                     note=f"no registered {theirs_run} run of {len(a)} paths to pair with"))
        return rows


#: where each declared output lives (the second read's R5 remedy: a declared-outputs test reads this table): (the
#: declared item, the file, the section or None, the part, a measure (or its prefix with `*`), a stat or None)
DECLARED_OUTPUTS: tuple[tuple[str, str, str | None, str, str, str | None], ...] = (
    ("8.1 items 2 and 4", "pp_reading", "identity", "identity", "8.1 items 2 and 4", "holds"),
    ("8.1 item 5", "pp_reading", "identity", "identity", "8.1 item 5", "holds"),
    ("8.1 item 6", "pp_reading", "identity", "identity", "8.1 item 6", "holds"),
    ("8.2 the replay's bounds", "pp_reading", "oracle", "replay", "payouts within the request's bounds", "holds"),
    ("8.2 the first payouts on the gate", "pp_reading", "oracle", "gate", "first_request_not_frac_of_max", "count"),
    ("8.2 lock's first payouts on the gate", "pp_reading", "oracle", "gate", "lock_first_payout_below_lock", "count"),
    ("8.2 the twin's martingale bound", "pp_reading", "oracle", "gate", "zero-edge twin martingale bound", None),
    ("8.3 differing within h", "pp_reading", "mechanics", "mechanics", "share_starts_differing_within_*", "share"),
    ("8.3 first requests lock holds", "pp_reading", "mechanics", "mechanics", "first_requests_held", "count"),
    ("8.3 requests half cuts", "pp_reading", "mechanics", "mechanics", "half_cut_below_min", "count"),
    ("8.3 held sessions by class", "pp_reading", "mechanics", "mechanics", "held_rescued", "count"),
    ("8.3 held at sessions h", "pp_reading", "mechanics", "mechanics", "share_starts_held_at_session_*", "share"),
    ("8.3 the holiday-hours reach", "pp_reading", "mechanics", "mechanics", "requests_at_early_close_or_holiday_eve",
     "cell"),
    ("8.3 the minutes release, offered", "pp_reading", "mechanics", "stream", "offered_open_at_minutes_release", None),
    ("8.3 the minutes release, executed", "pp_reading", "mechanics", "mechanics",
     "executed_open_at_minutes_release_at_allowance", "cell"),
    ("8.3 E-029's voided days", "pp_reading", "mechanics", "stream", "starts_whose_window_holds_*", "count"),
    ("9.1 item 1 the card", "pp_reading", "scorecard", "card", "card_S5c", "value"),
    ("9.1 item 1 S2", "pp_reading", "scorecard", "card", "card_S2_sessions_p90", "value"),
    ("9.1 item 1 S3d", "pp_reading", "scorecard", "card", "card_S3d", "value"),
    ("9.1 item 1 Q", "pp_reading", "scorecard", "card", "card_Q2", "value"),
    ("9.1 item 1 the card paired", "pp_reading", "paired", "card", "card_S1", "cell_less_base"),
    ("9.1 item 1 the frontier", "pp_reading", "scorecard", "frontier", "on_frontier_P_S1_S3a_S5a", "value"),
    ("9.1 item 2 sessions and cash to the first pass", "pp_reading", "paired", "paired", "cash_before_first_pass",
     None),
    ("9.1 item 2 sessions to the first payout", "pp_reading", "paired", "paired", "sessions_to_first_payout", None),
    ("9.1 item 2 broken even by month", "pp_reading", "paired", "paired", "broken_even_by_month_*", "mean"),
    ("9.1 item 2 fell back", "pp_reading", "paired", "paired", "fell_back_below_zero", None),
    ("9.1 item 2 evenness", "pp_reading", "paired", "paired", "largest_month_share", None),
    ("9.1 item 3 distributions", "pp_reading", "scorecard", "distribution", "sessions_to_first_payout",
     "p90_unreached_beyond"),
    ("9.1 item 3 S6's form", "pp_reading", "scorecard", "s6", "P", "start_share"),
    ("9.1 item 4 better, equal, worse", "pp_reading", "paired", "paired", "ahead_month_12", "share_worse"),
    ("9.1 item 4 the four-way ahead split", "pp_reading", "paired", "paired", "ahead_month_1", "ahead_both"),
    ("9.1 item 4 the interval's count", "pp_reading", "paired", "paired", "P", "n_w"),
    ("9.1 item 5 lock_half against lock", "pp_reading", "paired", "paired", "P", "mean"),
    ("9.1 item 6 what diverges", "pp_reading", "diverge", "diverge", "funded_lost", "cell_less_base"),
    ("9.1 item 6 held by class's share", "pp_reading", "diverge", "diverge", "share_funded_sessions_held_*", "cell"),
    ("9.1 item 6 evaluations and realised risk on the gate", "pp_gate", None, "diverge", "realised_risk_within_line",
     "cell"),
    ("9.1 item 7 the ladder's readings", "pp_reading", "beside", "paired", "P", "mean"),
    ("9.1 item 7 CVaR10", "pp_reading", "paired", "cvar10", "cvar10_net_month_3", "cell_less_base"),
    ("9.1 item 7 P under a bankroll limit", "pp_reading", "paired", "paired", "P_bankroll_*", "mean"),
    ("9.1 item 7 the ladder's ranking", "pp_reading", "beside", "ladder_rank", "rank_by_P", "rank"),
    ("9.1 item 7 the exact runs differing", "pp_reading", "scorecard", "exact_runs", "exact_runs_differing", "count"),
    ("9.1 item 8 growth on the required bankroll", "pp_gate", None, "reading", "growth_on_required_bankroll", "cell"),
    ("9.1 item 8 the required bankroll", "pp_gate", None, "reading", "required_bankroll_p90", "cell"),
    ("9.1 item 8 payouts a month", "pp_gate", None, "reading", "payouts_a_month", "cell"),
    ("9.1 item 8 days to the first payout", "pp_gate", None, "reading", "days_to_first_payout_median", "cell"),
    ("9.1 item 9 the evenness trade-off", "pp_reading", "scorecard", "evenness_tradeoff", "sd_monthly_net",
     "step_P_per_unit_evenness"),
    ("9.1 item 10 by start year", "pp_reading", "paired", "by_year", "P", "mean"),
    ("9.2 item 7 the honesty table", "pp_reading", "coverage", "coverage", "*", "coverage"),
    ("n3 the gates' held counts", "pp_gate", None, "held_counts", "held_sessions", "count"),
)


__all__ = ["RealInputs", "DECLARATION", "PREREG_ID", "PIN_ROW", "PURPOSES", "DESIGNS", "ARMS", "NEW_CELLS", "BESIDE",
           "RECORD_COLUMNS", "CALENDARS", "SECTIONS", "GUARDED", "Refused", "declared_seed", "section_11",
           "calendar_frames", "holiday_sessions", "Inputs", "cell_job", "runs_of", "Measure", "MEASURES", "start_frame",
           "start_tallies", "distribution_rows", "paired_rows", "card_of", "extra_card", "reading_rows", "read_check",
           "gate_read_check", "run_reading", "honesty_table", "label_rows", "menu_table", "limit_columns",
           "limit_problems", "adapter_provenance", "q44_problems", "GateTally", "gate_oracle_rows",
           "replay_oracle_rows", "identical_outputs", "DECLARED_OUTPUTS"]
