"""Q-17: one design, arm and response's readings from its starts (`extended.user_beside.run_starts`' outputs) -- the
rows of `results/user_beside.csv` and `results/user_beside_starts.csv`. Imports the vendored engine's pure modules
(`propedge.research.user_journey`, `u_select`) at call time: run in a process with `use_vendored_stage2()` done.

**Blocks (Wave 3.1; `docs/MEASURES.md` 1.1 and section 6, B-1).** The default everywhere is **E-208's search years**
(`BLOCKS = ("search",)`): `search` and `held_out` (`E208_BLOCKS`) read only **block-bounded journeys** --
`user_beside.run_starts(..., journey=True)`, each start's long run stopped at its block's last session -- and their
`E_h` is the block's starts with at least h sessions observed inside it (`obs_u >= h`). A held-out reading is made only
by the held-out test's runner, which names `held_out`; a default call never computes one. A block of E-208 asked of
records that are not block-bounded, or a registered block asked of journeys, is refused (`ValueError`).

**The registered readings' blocks** (read with the held-out years visible; MEASURES.md 7) stay as they were, each named
by its caller: `all` -- every start with the reading's horizon left; `judged` -- D-621 (4)(b)'s late block, the starts
from 2024 with the horizon left (`u_select.block(..., "late", h)`); Q-44's readings use these two (`Q44_BLOCKS`).
RD-01's 6 item 4 passes `READING_BLOCKS` (all, early and late): `early` the starts of 2023 and before less those within
the horizon of the block's last start (`u_select.block(..., "early", h)`), `late` the same as `judged`. On these blocks
every row is as before Wave 3.1, except that "ahead" reads a net above 1e-6 (m-11).

**Sections** (each row: design, arm, response and its descriptors, block, measure, stat, value, n):

* `scorecard` -- D-621's card (`u_select.scorecard`): P, S1, S3a, S3b, S3c, S4a, S4b, S5a, S5b, S5c, each on its own
  eligible starts, exact-length runs read where they differed (`user_journey.Views`), as Stage 2 reads it.
* `extra` -- E-007 (e): the shares ahead at months 1, 2, 3 and P on the starts with 63 sessions (P must equal the
  card's: a refusing check, until Wave 3.1; since, like with like -- see `consistency_problems`); the mean net at
  months 1, 2, 3; CVaR10 of the month-3 net; on the registered blocks, P under a bankroll limit of $2,000 and $2,500
  of cash spent before the first payout (`P_bankroll_*`: MEASURES.md section 2's sub-reading "before the first
  payout"), and the share of starts past each limit; on E-208's blocks, at each budget B the caller names (the
  operator's, Wave 4), **`P_B_*`: P with the peak out-of-pocket through each month close at most B** (MEASURES.md
  section 2), and beside it `P_B_before_first_payout_*` -- the share past a limit is replaced by (24)'s three states
  (section `journey`); the effective
  number of independent starts (`n_eff_bartlett` at lag 63 on each start's months ahead over three, start order) and
  the non-overlapping count n / 63; the minimum detectable difference in P -- **blank**: TASK_QUEUE Q-16's calibrated
  P comparison is not on master (2026-11-15), and an uncalibrated one is what E-007 (1) found does not deliver its level.
* `path` -- the operator's measures (2026-11-15), each a distribution over starts (p10, p50, p90; shares where named):
  sessions to the first pass and to the first payout (window 126, an unreached start beyond; the share reached), the
  cash spent before each (among those reaching it by 126); sessions to break-even at daily resolution (window 252) and
  the share broken even by months 1, 2, 3, 6, 12 (each on the starts with that horizon left), the share of those broken
  even by 252 that later close below zero, the deepest fall from the running high after break-even; on the starts with
  twelve months: the share of months with a positive net change, the longest run of months without a payout, the
  standard deviation of the monthly net, payouts per month (count and dollars), the largest month's share of the
  twelve months' payout dollars. These read each start's long replay (its daily closes), not an exact-length run.
* `response` -- what the response did: the share of starts it acted on by months 1, 3, 12 (its first denial, placement
  or forfeiture close), that close's distribution (window 252), payouts denied and cash forfeited per start.
* `journey` (E-208's blocks only; Wave 3.1; written by `extended.journey_readings`, `journey_rows`, so this module
  imports nothing new) -- `docs/MEASURES.md`'s measures read from each journey's closes 0 .. h
  (`extended.journey_measures`): the record each reading read (m-8); (2) the cash to the first pass, (3) the
  evaluations before it and (6) the cash before the first payout over all of `E_W`, unreached units at their censored
  lower bounds, each percentile with its strict-rule flag (`*_exact`: 1 exact, 0 "at least"); (24) the three states
  at each budget, with the limit's "not paid within B by W" and the peak form beside; (21) the longest wait for a
  payout from day 0 (unpaid censored at 127); (13) S4a and S4b above 1e-6; (15) the return on money at risk; (16) the
  median and the mean monthly net in months 4-12; (25) the peak out-of-pocket in 12 months; (31) the funded-account
  lifetime (Kaplan-Meier, each unit weighted equally, the censored count by kind).

On E-208's blocks the days rows of `path` and `response` take **the censored form** as the headline (`p10` .. `p90`:
an unreached start at W + 1, never blank) with Stage 2's blanking form beside (`stage2_p10` ..).
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from extended import user_measures as M

#: Q-44's blocks: a registered reading's, each named by the caller that reproduces it (MEASURES.md 7: read with the
#: held-out years visible)
Q44_BLOCKS = ("all", "judged")
#: E-208's blocks (W3.1): a journey's start days, window and E_h inside each
E208_BLOCKS = ("search", "held_out")
#: the default everywhere (W3.1; MEASURES.md section 6): the search years; a held-out reading names `held_out`
BLOCKS = ("search",)
#: every block a reading may name (`blocks=`); `judged` and `late` are one block under two names
KNOWN_BLOCKS = ("all", "judged", "early", "late", "search", "held_out")
#: RD-01 6 item 4's three blocks (the firms reading passes them; Q-44's default stays `BLOCKS`)
READING_BLOCKS = ("all", "early", "late")
MONTH = 21
FIRST_WINDOW = 126
YEAR_WINDOW = 252
BANKROLL_LIMITS = (2000.0, 2500.0)
BREAK_EVEN_MONTHS = (1, 2, 3, 6, 12)
ACTED_MONTHS = (1, 3, 12)
N_EFF_LAG = 63
MDD_NOTE = ("not computed: TASK_QUEUE Q-16's calibrated P comparison is not on master (2026-11-15); an uncalibrated MDD "
            "is what E-007 (1) found does not deliver its level")
#: the per-start file's columns (money as the engine books it, to the cent)
START_COLS = ("design", "arm", "response", "start_day", "start_date", "observed", "exact_runs_differing",
              "months_ahead", "net_month_1", "net_month_2", "net_month_3", "net_month_6", "net_month_12",
              "first_pass", "spent_before_first_pass", "first_payout", "spent_before_first_payout", "payouts",
              "break_even_day", "fell_back", "deepest_fall_after_break_even", "share_months_positive",
              "longest_months_without_payout", "sd_monthly_net", "payouts_per_month", "payout_cash_per_month",
              "largest_month_share", "response_day", "payouts_denied", "cash_forfeited")
MONEY_COLS = ("net_month_1", "net_month_2", "net_month_3", "net_month_6", "net_month_12", "spent_before_first_pass",
              "spent_before_first_payout", "deepest_fall_after_break_even", "sd_monthly_net", "payout_cash_per_month",
              "cash_forfeited")
#: W3.1: a journey's per-start columns, after `START_COLS` (block-bounded outputs only): its block, the sessions left
#: in it, the peak out-of-pocket through each month close (MEASURES.md section 6, B-2)
PEAK_COLS = tuple(f"peak_month_{m}" for m in range(1, M.MONTHS + 1))
JOURNEY_COLS = ("block", "block_left", *PEAK_COLS)


def _which(block: str) -> str | None:
    if block not in KNOWN_BLOCKS:
        raise ValueError(f"a block is one of {KNOWN_BLOCKS}, got {block!r}")
    if block in ("all", *E208_BLOCKS):                     # W3.1: E-208's records come pre-chosen by block
        return None
    return "early" if block == "early" else "late"


def is_journey(outs: Sequence[Mapping[str, Any]]) -> bool:
    """W3.1: whether the outputs are block-bounded journeys (`user_beside.run_starts(..., journey=True)`); refused
    (`ValueError`) when some are and some are not."""
    have = [("journey" in x) for x in outs]
    if any(have) and not all(have):
        raise ValueError("REFUSED (W3.1): some outputs are block-bounded journeys and some are not")
    return bool(have) and all(have)


def is_journey_table(t: pd.DataFrame) -> bool:
    """W3.1: whether a per-start table is of block-bounded journeys (`start_table` gave it `JOURNEY_COLS`; another
    reading's table may carry a `block` column of its own, so the mark is `block_left`)."""
    return "block_left" in t.columns


def check_blocks(blocks: Sequence[str], journey: bool, what: str = "a reading") -> None:
    """W3.1: E-208's blocks read journeys only, the registered blocks never read them (`ValueError`)."""
    for b in blocks:
        _which(b)
        if b in E208_BLOCKS and not journey:
            raise ValueError(f"REFUSED (W3.1): {what} on the {b!r} block reads block-bounded journeys "
                             "(user_beside.run_starts(..., journey=True)); a registered reading names its blocks "
                             f"(Q44_BLOCKS {Q44_BLOCKS}, READING_BLOCKS {READING_BLOCKS})")
        if b not in E208_BLOCKS and journey:
            raise ValueError(f"REFUSED (W3.1): {what}: the registered block {b!r} is not read on block-bounded "
                             f"journeys; their blocks are {E208_BLOCKS}")


def _in_block(records: Sequence[Mapping[str, Any]], b: str, block_of: Mapping[int, str] | None
              ) -> Sequence[Mapping[str, Any]]:
    """The records a block reads: a registered block, every record (its own rule chooses); one of E-208's, the
    records whose journey lies in it (`block_of`: start day -> block, required)."""
    if b not in E208_BLOCKS:
        if block_of is not None:
            raise ValueError(f"REFUSED (W3.1): the registered block {b!r} is not read on block-bounded journeys")
        return records
    if block_of is None:
        raise ValueError(f"REFUSED (W3.1): the {b!r} block reads block-bounded journeys; no start's block is given")
    return [r for r in records if block_of[int(r["start_day"])] == b]


# ------------------------------------------------------------------------------------------------ per start


def start_table(design: str, arm: str, response: str, outs: Sequence[Mapping[str, Any]]) -> pd.DataFrame:
    """One row a start: the record's long-replay values, the daily path measures, the evenness over twelve months (a
    start with 252 sessions), what the response did."""
    rows = []
    jour = is_journey(outs)                                                     # W3.1
    for x in outs:
        r, d, z = x["rec"], x["daily"], x["response"]
        nm = [np.nan if v is None else float(v) for v in r["net_month"]]
        ev = (M.evenness(nm, list(zip(r["pay_days"], r["pay_cash"]))) if int(r["observed"]) >= YEAR_WINDOW
              else {k: np.nan for k in ("share_months_positive", "longest_months_without_payout", "sd_monthly_net",
                                        "payouts_per_month", "payout_cash_per_month", "largest_month_share")})
        ahead = M.months_ahead(np.array([nm[:3]]))[0] if int(r["observed"]) >= 63 else np.nan
        rows.append({"design": design, "arm": arm, "response": response, "start_day": int(r["start_day"]),
                     "start_date": str(r["start_date"]), "observed": int(r["observed"]),
                     "exact_runs_differing": " ".join(str(int(h)) for h in x["differs"]),
                     "months_ahead": ahead, **{f"net_month_{k}": nm[k - 1] for k in (1, 2, 3, 6, 12)},
                     **{k: float(r[k]) for k in ("first_pass", "spent_before_first_pass", "first_payout",
                                                 "spent_before_first_payout")},
                     "payouts": len(r["pay_days"]), **{k: float(v) for k, v in d.items()},
                     **{k: float(v) for k, v in ev.items()},
                     **{k: float(z[k]) for k in ("response_day", "payouts_denied", "cash_forfeited")}})
        if jour:                                                                # W3.1: the journey's columns
            j = x["journey"]
            rows[-1].update({"block": str(j["block"]), "block_left": int(j["block_left"]),
                             **{c: float(v) for c, v in zip(PEAK_COLS, j["peak_month"])}})
    t = pd.DataFrame(rows, columns=list(START_COLS) + (list(JOURNEY_COLS) if jour else []))
    return t


def rounded(t: pd.DataFrame) -> pd.DataFrame:
    """The per-start file's form: money to the cent (the summary rows are read before rounding)."""
    t = t.copy()
    for c in MONEY_COLS + tuple(c for c in PEAK_COLS if c in t.columns):       # W3.1: the peaks, when held
        t[c] = t[c].astype(float).round(2)
    return t


# ------------------------------------------------------------------------------------------------ the summary


def _row(section: str, block: str, measure: str, stat: str, value: float, n: int, note: str = "") -> dict[str, Any]:
    return {"section": section, "block": block, "measure": measure, "stat": stat, "value": float(value), "n": int(n),
            "note": note}


def _elig(t: pd.DataFrame, block: str, h: int) -> np.ndarray:
    """The table's starts in `block` at horizon `h`, as `u_select.block` chooses them (`judged` / `late`: from 2024 with
    h sessions; `early`: 2023 and before, less the starts within h of the block's last, with h sessions). W3.1, E-208's
    blocks: `E_h` inside the block -- the block's journeys with at least h sessions observed in it (`obs_u >= h`, the
    run itself stopped at the block's end); a table without the journey's columns is refused."""
    _which(block)
    m = t["observed"].to_numpy(int) >= int(h)
    if block in E208_BLOCKS:                                                    # W3.1
        if not is_journey_table(t):
            raise ValueError(f"REFUSED (W3.1): the {block!r} block reads a table of block-bounded journeys")
        if (t["observed"].to_numpy(int) > t["block_left"].to_numpy(int)).any():
            raise ValueError("REFUSED (W3.1): a journey observes sessions past its block's end")
        return m & (t["block"].astype(str).to_numpy() == block)
    if is_journey_table(t):
        raise ValueError(f"REFUSED (W3.1): the registered block {block!r} is not read on block-bounded journeys")
    if block in ("judged", "late", "early"):
        from propedge.research import u_select as S

        year = t["start_date"].astype(str).str[:4].astype(int).to_numpy()
        if block == "early":
            e = year <= int(S.CHOICE_LAST_YEAR)
            day = t["start_day"].to_numpy(int)
            last = int(day[e].max()) if e.any() else 0
            m &= e & (day <= last - int(h))
        else:
            m &= year >= int(S.JUDGED_FIRST_YEAR)
    return m


def _dist(section: str, block: str, measure: str, x: np.ndarray, note: str = "") -> list[dict[str, Any]]:
    q = M.quantiles(x)
    return [_row(section, block, measure, f"p{p}", q[f"p{p}"], q["n"], note) for p in M.PERCENTILES]


def _days(section: str, block: str, measure: str, first: np.ndarray, window: int) -> list[dict[str, Any]]:
    n = len(first)
    if block in E208_BLOCKS:                                                    # W3.1: the censored headline
        out = [_row(section, block, measure, f"p{p}", M.days_quantile(first, window, p, censored=True), n,
                    f"window {window}; an unreached start censored at {window + 1}") for p in M.PERCENTILES]
        out += [_row(section, block, measure, f"stage2_p{p}", M.days_quantile(first, window, p), n,
                     f"Stage 2's form beside: an unreached start beyond, a percentile beyond the window blank")
                for p in M.PERCENTILES]
        hit = np.isfinite(first) & (first <= window)
        out.append(_row(section, block, measure, f"share_by_{window}", float(hit.mean()) if n else np.nan, n))
        return out
    out = [_row(section, block, measure, f"p{p}", M.days_quantile(first, window, p), n,
                f"window {window}; an unreached start beyond") for p in M.PERCENTILES]
    hit = np.isfinite(first) & (first <= window)
    out.append(_row(section, block, measure, f"share_by_{window}", float(hit.mean()) if n else np.nan, n))
    return out


def scorecard_rows(records: Sequence[Mapping[str, Any]], blocks: Sequence[str] = BLOCKS, *,
                   block_of: Mapping[int, str] | None = None) -> list[dict[str, Any]]:
    """D-621's card (Stage 2's, `> 0`: read beside under Stage 2's tolerance) on each block; W3.1: on E-208's blocks
    the block's journeys (`block_of`: start day -> block)."""
    from propedge.research import u_select as S

    out = []
    for b in blocks:
        card = S.scorecard(_in_block(records, b, block_of), _which(b))
        out += [_row("scorecard", b, k, "value", v["value"], v["n"]) for k, v in card.items()]
    return out


def extra_rows(records: Sequence[Mapping[str, Any]], blocks: Sequence[str] = BLOCKS, *,
               block_of: Mapping[int, str] | None = None, peaks: Mapping[int, Sequence[float]] | None = None,
               budgets: Sequence[float] = ()) -> list[dict[str, Any]]:
    """E-007 (e)'s rows on each block. W3.1, on E-208's blocks (`block_of`, and `peaks`: start day -> the peak
    out-of-pocket through each month close): at each budget B, `P_B_{B}` (MEASURES.md section 2: ahead at a month only
    with the peak through its close at most B) and `P_B_before_first_payout_{B}` (its named sub-reading: the spending
    before the first payout, read on closes 0 .. 21 m); the share past a limit is not written there ((24) replaces it,
    `journey_rows`)."""
    from propedge.research import u_select as S
    from propedge.research import user_journey as U

    out = []
    for b in blocks:
        sub = S.block(_in_block(records, b, block_of), _which(b), S.P_HORIZON)
        if not sub:
            out += [_row("extra", b, "P", "value", np.nan, 0)]
            continue
        V = U.Views(sub)
        nets = np.column_stack([U._net_at(V, MONTH * m) for m in M.P_MONTHS])
        spent = np.column_stack([V.at(MONTH * m)["spent_before_first_payout"].to_numpy(float) for m in M.P_MONTHS])
        p = M.p_by_month(nets)
        n = p["n"]
        out += [_row("extra", b, f"share_ahead_month_{m}", "value", p[f"share_month_{m}"], n) for m in M.P_MONTHS]
        out.append(_row("extra", b, "P", "value", p["P"], n))
        for i, m in enumerate(M.P_MONTHS):
            x = nets[:, i]
            out.append(_row("extra", b, f"mean_net_month_{m}", "value", float(np.nanmean(x)), int(np.isfinite(x).sum())))
        out.append(_row("extra", b, "cvar10_net_month_3", "value", M.cvar(nets[:, 2], 0.10),
                        int(np.isfinite(nets[:, 2]).sum()), "the mean of the worst ceil(0.10 n) month-3 nets"))
        if b in E208_BLOCKS:                                                    # W3.1: P_B, the peak through the close
            if peaks is None:
                raise ValueError(f"REFUSED (W3.1): P_B on the {b!r} block needs each journey's peak by month")
            pk = np.array([[float(peaks[int(r["start_day"])][m - 1]) for m in M.P_MONTHS] for r in sub], float)
            fy = np.column_stack([V.at(MONTH * m)["first_payout"].to_numpy(float) for m in M.P_MONTHS])
            within = np.where(fy <= np.array([MONTH * m for m in M.P_MONTHS]), spent, np.nan)   # closes 0 .. 21 m
            for lim in budgets:
                q = M.p_by_month(nets, spent=pk, limit=float(lim))
                out.append(_row("extra", b, f"P_B_{lim:g}", "value", q["P"], q["n"],
                                f"ahead only with the peak out-of-pocket through the month close at most ${lim:,.0f}"))
                q = M.p_by_month(nets, spent=within, limit=float(lim))
                out.append(_row("extra", b, f"P_B_before_first_payout_{lim:g}", "value", q["P"], q["n"],
                                f"beside: ahead only with the cash spent before the first payout at most ${lim:,.0f}"))
        for lim in (BANKROLL_LIMITS if b not in E208_BLOCKS else ()):
            q = M.p_by_month(nets, spent=spent, limit=lim)
            out.append(_row("extra", b, f"P_bankroll_{int(lim)}", "value", q["P"], q["n"],
                            f"ahead only within ${lim:,.0f} of cash spent before the first payout"))
            out.append(_row("extra", b, f"share_spent_over_{int(lim)}", "value",
                            M.share_over_limit(spent[:, 2], lim), int(np.isfinite(spent[:, 2]).sum()),
                            "among starts with a first payout within the observed sessions (the month-3 reading)"))
        ahead = M.months_ahead(nets) / len(M.P_MONTHS)
        out.append(_row("extra", b, "n_eff_bartlett", "value", M.n_eff_bartlett(ahead, N_EFF_LAG), n,
                        f"each start's months ahead over three, start order; Bartlett lag {N_EFF_LAG}; a description"))
        out.append(_row("extra", b, "n_nonoverlapping", "value", n / float(S.P_HORIZON), n,
                        f"the starts over the reading's {S.P_HORIZON} sessions"))
        out.append(_row("extra", b, "mdd_P", "value", np.nan, n, MDD_NOTE))
    return out


def path_rows(t: pd.DataFrame, blocks: Sequence[str] = BLOCKS) -> list[dict[str, Any]]:
    check_blocks(blocks, is_journey_table(t), "the path rows")                 # W3.1
    out = []
    for b in blocks:
        e = _elig(t, b, FIRST_WINDOW)
        for ev, spent in (("first_pass", "spent_before_first_pass"), ("first_payout", "spent_before_first_payout")):
            f = t[ev].to_numpy(float)[e]
            out += _days("path", b, f"{ev}_days", f, FIRST_WINDOW)
            hit = np.isfinite(f) & (f <= FIRST_WINDOW)
            out += _dist("path", b, spent, t[spent].to_numpy(float)[e][hit], f"among starts reaching it by {FIRST_WINDOW}")
        e = _elig(t, b, YEAR_WINDOW)
        be = t["break_even_day"].to_numpy(float)
        out += _days("path", b, "break_even_days", be[e], YEAR_WINDOW)
        for m in BREAK_EVEN_MONTHS:
            em = _elig(t, b, MONTH * m)
            x = be[em]
            out.append(_row("path", b, "break_even", f"share_by_month_{m}",
                            float((np.isfinite(x) & (x <= MONTH * m)).mean()) if em.any() else np.nan, int(em.sum())))
        hit = e & np.isfinite(be)
        fb = t["fell_back"].to_numpy(float)[hit]
        out.append(_row("path", b, "break_even", "share_fell_back", float(fb.mean()) if len(fb) else np.nan, len(fb),
                        f"of the starts broken even within {YEAR_WINDOW}: a later close below zero"))
        out += _dist("path", b, "deepest_fall_after_break_even", t["deepest_fall_after_break_even"].to_numpy(float)[hit],
                     f"of the starts broken even within {YEAR_WINDOW}")
        for c in ("share_months_positive", "longest_months_without_payout", "sd_monthly_net", "payouts_per_month",
                  "payout_cash_per_month", "largest_month_share"):
            x = t[c].to_numpy(float)[e]
            out += _dist("path", b, c, x, "starts with twelve months" + ("; paid within them" if c ==
                                                                         "largest_month_share" else ""))
            if c in ("share_months_positive", "payouts_per_month", "payout_cash_per_month"):
                out.append(_row("path", b, c, "mean", float(np.nanmean(x)) if np.isfinite(x).any() else np.nan,
                                int(np.isfinite(x).sum())))
    return out


def response_rows(t: pd.DataFrame, blocks: Sequence[str] = BLOCKS) -> list[dict[str, Any]]:
    check_blocks(blocks, is_journey_table(t), "the response rows")             # W3.1
    out = []
    day = t["response_day"].to_numpy(float)
    for b in blocks:
        for m in ACTED_MONTHS:
            em = _elig(t, b, MONTH * m)
            x = day[em]
            out.append(_row("response", b, "acted", f"share_by_month_{m}",
                            float((np.isfinite(x) & (x <= MONTH * m)).mean()) if em.any() else np.nan, int(em.sum())))
        e = _elig(t, b, YEAR_WINDOW)
        out += _days("response", b, "response_day", day[e], YEAR_WINDOW)
        for c in ("payouts_denied", "cash_forfeited"):
            x = t[c].to_numpy(float)[_elig(t, b, 1)]
            out.append(_row("response", b, c, "mean", float(np.nanmean(x)) if np.isfinite(x).any() else np.nan,
                            int(np.isfinite(x).sum()), "per start, its long replay"))
    return out


def summary(design: str, arm: str, resp: Any, outs: Sequence[Mapping[str, Any]], *,
            blocks: Sequence[str] = BLOCKS, budgets: Sequence[float] = ()) -> tuple[list[dict], pd.DataFrame]:
    """One design, arm and response: (the summary rows, the per-start table), on `blocks` -- by default the search
    years (W3.1), which read block-bounded journeys; a registered reading names its blocks (`Q44_BLOCKS`,
    `READING_BLOCKS`). On E-208's blocks `budgets` are `P_B`'s B (the operator's); the section `journey` is
    `extended.journey_readings`' (its `summary` is this one with that section added)."""
    records = [x["rec"] for x in outs]
    jour = is_journey(outs)                                                     # W3.1
    check_blocks(blocks, jour, "the summary")
    t = start_table(design, arm, resp.name, outs)
    if jour:
        block_of = {int(x["rec"]["start_day"]): str(x["journey"]["block"]) for x in outs}
        peaks = {int(x["rec"]["start_day"]): list(x["journey"]["peak_month"]) for x in outs}
        rows = (scorecard_rows(records, blocks, block_of=block_of)
                + extra_rows(records, blocks, block_of=block_of, peaks=peaks, budgets=budgets)
                + path_rows(t, blocks) + response_rows(t, blocks))
    else:
        rows = (scorecard_rows(records, blocks) + extra_rows(records, blocks) + path_rows(t, blocks)
                + response_rows(t, blocks))
    head = {"design": design, "arm": arm, "response": resp.name, "kind": resp.kind,
            "enforcement_p": float(resp.enforcement_p), "rtp": bool(resp.rtp), "rtp_warnings": int(resp.rtp_warnings),
            "ftp_label": resp.ftp_label}
    return [{**head, **r} for r in rows], t


def consistency_problems(rows: Sequence[Mapping[str, Any]], outs: Sequence[Mapping[str, Any]], what: str, *,
                         blocks: Sequence[str] = BLOCKS) -> list[str]:
    """The refusing checks on one reading: every run's payouts and fees against the engine's totals; the record from
    the long replay alone equal to `_one_start`'s wherever both are made; **the extra P like with like** (W3.1,
    MEASURES.md section 6, m-11): this repository's P (`p_by_month`, ahead above 1e-6) equal to the mean of its own
    three month shares, on the card's starts (the same n), and never above Stage 2's card (`> 0`, read beside under
    Stage 2's tolerance -- a net above 1e-6 is above 0 -- never held equal to it); P within each bankroll limit not
    above P, the $2,000 one not above the $2,500 one; on E-208's blocks `P_B` not above its sub-reading nor above P,
    and rising with B, and (24)'s three states summing to one; every share in [0, 1]."""
    out = []
    for k in ("pay", "cash", "fee"):
        n = int(sum(x[f"{k}_bad"] for x in outs))
        if n:
            out.append(f"{what}: {n} runs' {k} check against the engine's totals fails")
    n = sum(1 for x in outs if x.get("record_same") is False)
    if n:
        out.append(f"{what}: on {n} starts the long replay's record is not user_journey._one_start's")
    by = {(r["section"], r["block"], r["measure"], r["stat"]): float(r["value"]) for r in rows}
    ns = {(r["section"], r["block"], r["measure"], r["stat"]): int(r["n"]) for r in rows}
    for b in blocks:
        card, mine = by.get(("scorecard", b, "P", "value")), by.get(("extra", b, "P", "value"))
        shares = [by.get(("extra", b, f"share_ahead_month_{m}", "value")) for m in M.P_MONTHS]
        if card is None or mine is None:
            out.append(f"{what} {b}: the extra P {mine} or the card's {card} is missing")
        elif np.isnan(card) or np.isnan(mine):
            if not (np.isnan(card) and np.isnan(mine)):
                out.append(f"{what} {b}: the extra P {mine} and the card's {card}: one is blank")
        elif (None in shares or abs(mine - float(np.mean(shares))) > 1e-12 or mine > card + 1e-12
              or ns.get(("extra", b, "P", "value")) != ns.get(("scorecard", b, "P", "value"))):
            out.append(f"{what} {b}: the extra P {mine} is not the mean of its month shares {shares} on the card's "
                       f"starts, at most the card's {card}")
        pb = sorted((float(r["measure"][4:]), float(r["value"])) for r in rows if r["block"] == b and
                    r["section"] == "extra" and r["measure"].startswith("P_B_") and
                    not r["measure"].startswith("P_B_before"))
        for (lim, v) in pb:
            sub_ = by.get(("extra", b, f"P_B_before_first_payout_{lim:g}", "value"))
            if mine is not None and np.isfinite(mine) and not (v <= mine + 1e-12 and sub_ is not None and
                                                                v <= sub_ + 1e-12):
                out.append(f"{what} {b}: P_B at {lim:g} ({v}) is above P ({mine}) or its sub-reading ({sub_})")
        if any(y > x + 1e-12 for (_, y), (_, x) in zip(pb, pb[1:])):
            out.append(f"{what} {b}: P_B falls as the budget rises")
        for r in rows:
            if r["block"] == b and r["section"] == "journey" and r["measure"].startswith("bankroll_stop_") and \
                    r["stat"] == "share_paid_within":
                tot = sum(by[("journey", b, r["measure"], f"share_{k}")] for k in ("paid_within", "run_out", "censored"))
                if np.isfinite(tot) and abs(tot - 1.0) > 1e-9:
                    out.append(f"{what} {b}: {r['measure']}'s three states sum to {tot}, not one")
        lo, hi = by.get(("extra", b, "P_bankroll_2000", "value")), by.get(("extra", b, "P_bankroll_2500", "value"))
        if None not in (lo, hi, mine) and np.isfinite(mine) and not (lo <= hi + 1e-12 and hi <= mine + 1e-12):
            out.append(f"{what} {b}: P within the limits ({lo}, {hi}) not ordered below P {mine}")
    for r in rows:
        if (r["stat"].startswith("share") or r["measure"].startswith("share")) and np.isfinite(r["value"]) and \
                not -1e-12 <= r["value"] <= 1 + 1e-12:
            out.append(f"{what}: {r['section']} {r['block']} {r['measure']} {r['stat']} = {r['value']} is not a share")
    return out


__all__ = ["BLOCKS", "Q44_BLOCKS", "E208_BLOCKS", "KNOWN_BLOCKS", "READING_BLOCKS", "START_COLS", "MONEY_COLS",
           "PEAK_COLS", "JOURNEY_COLS", "MDD_NOTE", "is_journey", "is_journey_table", "check_blocks", "start_table",
           "rounded", "scorecard_rows", "extra_rows", "path_rows", "response_rows", "summary",
           "consistency_problems"]
