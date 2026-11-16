"""F-03 (family O): the population, its labels and its strata (sections 5.2, 5.3, 7.2; build item 18.1 item 2).

    from extended import opening_population as OP
    pop = OP.population_frame(walk, walk_close, coins, kinds, admitted, rr_grid=..., costs=..., entry_ticks=1.0)
    pop = OP.centre(pop, OP.strata(pop))                 # y = c - mu_g within the block read (7.2)

**The population** (5.2): P-16's offers at the marks 17:00 .. 08:25 CT of its walked sessions (day kinds `n` and `b`),
on a report day (`b`) from 07:40 only -- each walked long and short at 3R from P-16's market entry (the first bar
opening at or after the mark, one tick adverse) under `extended.walker.STAGE2`, and at 3R under C1-close's named
instance `Rules("fo_stage2_close", FLAT_ENTRY, "close", True)` (5.3, m2-7). **Labels** (5.2, the review's F3): every
other P-16 offer -- its marks 08:30 .. 09:00 and the report-day 07:35 mark -- walked the same way, labels only (a
fallback opening's value), never in any state's population. P-16's admitted marks are its registration's (D-525 (4):
the screen file's `marks` section at 150 ticks, pinned by sha256), not recomputed from any walk.

**The values** (5.3): l_i and r_i the long's and the short's net R at 3R -- gross ticks / 150 less Stage 2's costs by
the exit's kind (`extended.walker.net_r`: a tick at entry, the fee at the stop, a stop or breakeven exit one tick, a
flatten two) -- and the side-symmetric value c_i = (l_i + r_i) / 2; `c_close` the same under the close instance. Every
table R is kept for both sides (`rl_<R>`, `rs_<R>`) so V_other can value a trade at its own R (7.4).

**The strata** g = (mark, day kind, calendar year) (5.2, 7.1), computed within the block being read; mu_g the mean of c
over **every** offer of the stratum (population and labels alike -- a stratum is wholly one or the other, since a
label's mark is never a population mark on its day kind); y = c - mu_g, so the twin's exact expectation is zero in every
stratum (7.2's centring).

**The real build** (`build_span`, run 1 on the choice block, run 2 on the judged block, A0 on both): the bars through
`extended.reader` only (a judged span under its declared purpose), A1's day table through the reader (dates and day
kinds), the coin by `resolved_coin.coin_table`'s construction over **every** stored session's date (the choice block's
from A1, the judged block's from Q-83's pinned session list, `results/q82_judged_sessions.csv`: 657 sessions, its
sha256 in E-094 -- so building the choice span reads no judged row), the walk by this repository's walker
(`walk_offers`, the generalisation of E-011's `identity/walker_identity.walk_minutes` to a `Rules`), and P-16's trades
on the span by the vendored `resolved_coin.cell_trades`, `zero_edge_decomposition.pad` and
`resolved_coin.drop_release_minute` -- `rc_width_screen.build`'s steps on the span, with the cutoff's admitted marks
read from P-16's registration instead of re-walked. A0 holds the two spans' trades, concatenated, to P-16's pinned
content hash (A0 item 1).
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence

import numpy as np
import pandas as pd

from extended import features as F
from extended import walker as W

STOP = 150
R_JUDGED = 3.0
#: C1-close's walk (5.3; the second read's m2-7): STAGE2 with the flatten at the close of the bar ending 15:08
CLOSE_RULES = W.Rules("fo_stage2_close", W.FLAT_ENTRY, "close", True)
#: the population's time range (5.2) and a report day's first population mark
FIRST_MARK, LAST_MARK = F.slot(17, 0), F.slot(8, 25)
REPORT_FIRST = F.slot(7, 40)
REPORT_DAY_KIND, NORMAL_DAY_KIND = "b", "n"
WALKED_KINDS = (NORMAL_DAY_KIND, REPORT_DAY_KIND)
#: P-16's report-day cut (D-533 (2)): its registered report-day entries start at 07:35 CT
P16_REPORT_CLEAR = F.slot(7, 35)
#: the opening window's marks (labels only; D-281 (3))
WINDOW_FIRST, WINDOW_LAST = F.slot(8, 30), F.slot(9, 0)
#: Q-83's judged session list (E-094): its count and the sha256 of the ISO dates joined by LF, no trailing newline
JUDGED_SESSIONS_FILE = "q82_judged_sessions.csv"
JUDGED_SESSIONS_COUNT = 657
JUDGED_SESSIONS_SHA256 = "d1e4524b15dc6a69c2f66865462a5fe30527c6a56b4c7cc7aaccc1436a30f3bd"
#: walked a chunk of days at a time so the process stays small (as `scripts/q16_p16_pairs.py`)
CHUNK_DAYS = 40


def rkey(R: float) -> str:
    return f"{float(R):g}"


# ------------------------------------------------------------------------------------------------ the walk


def walk_offers(minutes: pd.DataFrame, arrays: Callable[[str], tuple], rr_grid: Sequence[float], *,
                rules: W.Rules = W.STAGE2, stops: Sequence[int] = (STOP,), tick: float = W.TICK) -> pd.DataFrame:
    """Each (date, mark) of `minutes` a market order on each side, live at the mark, filled at the open of the first
    bar opening at or after it before the walk's end, walked under `rules` at every (stop, R) -- one row a (date, slot,
    side) with `entry_slot` and per (S, R) the kind `k`, exit bar `x`, MAE `a` and gross `g` in ticks: E-011's
    `walk_minutes` (identity/walker_identity.py) with the rules a parameter; under STAGE2 it is that frame exactly
    (T-4)."""
    bl = W.brackets(tuple(int(S) for S in stops), tuple(float(R) for R in rr_grid))
    cols = []
    for S in stops:
        for R in rr_grid:
            cols += [f"k{S}_{R:g}", f"x{S}_{R:g}", f"a{S}_{R:g}", f"g{S}_{R:g}"]
    parts = []
    for day, g in minutes.groupby("date", sort=True):
        o, h, l, c = (np.asarray(x, dtype=float) for x in arrays(str(day)))
        slots = g["slot"].astype(int).tolist()
        fb = W.market_fill_bars(o, slots, rules=rules)
        ent = [(s, side, int(j)) for s, j in zip(slots, fb) if j != W.NONE for side in (1, -1)]
        if not ent:
            continue
        bars = [x[2] for x in ent]
        res = W.walk(o, h, l, c, bars, o[bars], [x[1] for x in ent], False, bl, tick=float(tick), rules=rules)
        head = pd.DataFrame(ent, columns=["slot", "side", "entry_slot"]).assign(date=str(day), delay=0)
        body = np.empty((len(ent), 4 * len(bl)), dtype=np.int32)
        body[:, 0::4], body[:, 1::4] = res["kind"], res["exit"]
        body[:, 2::4], body[:, 3::4] = res["mae"], res["gross"]
        parts.append(pd.concat([head, pd.DataFrame(body, columns=cols)], axis=1))
    lead = ["date", "slot", "delay", "side", "entry_slot"]
    if not parts:
        return pd.DataFrame(columns=lead + cols)
    w = pd.concat(parts, ignore_index=True)[lead + cols]
    w = w.astype({"slot": "int16", "delay": "int8", "side": "int8", "entry_slot": "int16",
                  **{c: ("int8" if c.startswith("k") else "int32") for c in cols}})
    return w.sort_values(["date", "slot", "side"], kind="stable").reset_index(drop=True)


# ------------------------------------------------------------------------------------------------ the frame


def in_population(slot: np.ndarray, day_kind: np.ndarray) -> np.ndarray:
    """5.2: the marks 17:00 .. 08:25 CT on walked days, a report day's from 07:40."""
    s = np.asarray(slot, dtype=np.int64)
    k = np.asarray(day_kind).astype(str)
    walked = np.isin(k, WALKED_KINDS)
    first = np.where(k == REPORT_DAY_KIND, REPORT_FIRST, FIRST_MARK)
    return walked & (s >= first) & (s <= LAST_MARK) & (s % 5 == 0)


def p16_offered(slot: np.ndarray, day_kind: np.ndarray, admitted: Sequence[int]) -> np.ndarray:
    """P-16's own offers: an admitted mark on a walked day, a report day's from 07:35 (D-533 (2))."""
    s = np.asarray(slot, dtype=np.int64)
    k = np.asarray(day_kind).astype(str)
    adm = np.isin(s, np.asarray(list(admitted), dtype=np.int64))
    return np.isin(k, WALKED_KINDS) & adm & ~((k == REPORT_DAY_KIND) & (s < P16_REPORT_CLEAR))


def population_frame(walk: pd.DataFrame, walk_close: pd.DataFrame, coins: Any, kinds: Mapping[str, str],
                     admitted: Sequence[int], *, rr_grid: Sequence[float], costs: W.Costs,
                     entry_ticks: float = float(W.SLIP_TICKS), extras: Mapping[str, pd.DataFrame] | None = None
                     ) -> pd.DataFrame:
    """One row a P-16 offer (date, mark) walked on both sides: `date`, `year`, `day_kind`, `slot`, `entry_slot`, `coin`
    (+1 / -1, the registered coin), `population` (5.2) and `label` (the other P-16 offers), the kinds `kl`, `ks` and
    the net R `rl`, `rs`, `rl_close`, `rs_close` at 3R, `c` and `c_close`, both sides' net R and kind at every table
    R (`rl_<R>`, `rs_<R>`, `kl_<R>`, `ks_<R>`), and for each further walk at 3R in `extras` (name -> walk frame, such
    as Q-20's corrected moves) `rl_<name>`, `rs_<name>`, `c_<name>`. A row is kept only where P-16 offers it and both
    sides filled."""
    S = STOP
    rr = [float(R) for R in rr_grid]
    if R_JUDGED not in rr:
        raise ValueError("the walk's grid does not carry 3R")
    w = walk.assign(date=walk["date"].astype(str), slot=walk["slot"].astype(np.int64))
    lo = w[w["side"].astype(int) > 0].set_index(["date", "slot"]).sort_index()
    sh = w[w["side"].astype(int) < 0].set_index(["date", "slot"]).sort_index()
    both = lo.index.intersection(sh.index)
    lo, sh = lo.loc[both], sh.loc[both]
    if not np.array_equal(lo["entry_slot"].to_numpy(), sh["entry_slot"].to_numpy()):
        raise ValueError("a pair's two sides enter at different bars")
    dates = both.get_level_values(0).astype(str).to_numpy()
    slots = both.get_level_values(1).to_numpy(np.int64)
    dk = np.array([kinds.get(d, "") for d in dates], dtype=object)
    offered = p16_offered(slots, dk, admitted)
    out = pd.DataFrame({"date": dates, "year": np.array([int(d[:4]) for d in dates], dtype=np.int64),
                        "day_kind": dk.astype(str), "slot": slots,
                        "entry_slot": lo["entry_slot"].to_numpy(np.int64),
                        "coin": np.array([coins[(d, int(s))] for d, s in zip(dates, slots)], dtype=np.int8)})
    pop = in_population(slots, dk) & offered
    out["population"] = pop
    out["label"] = offered & ~pop

    def net(side: pd.DataFrame, R: float) -> np.ndarray:
        k = side[f"k{S}_{rkey(R)}"].astype(int).to_numpy()
        g = side[f"g{S}_{rkey(R)}"].astype(float).to_numpy()
        return W.net_r(g, k, S, entry_ticks=entry_ticks, costs=costs)

    for R in rr:
        out[f"rl_{rkey(R)}"] = net(lo, R)
        out[f"rs_{rkey(R)}"] = net(sh, R)
        out[f"kl_{rkey(R)}"] = lo[f"k{S}_{rkey(R)}"].astype(np.int8).to_numpy()
        out[f"ks_{rkey(R)}"] = sh[f"k{S}_{rkey(R)}"].astype(np.int8).to_numpy()
    out["kl"] = lo[f"k{S}_3"].astype(np.int8).to_numpy()
    out["ks"] = sh[f"k{S}_3"].astype(np.int8).to_numpy()
    out["rl"], out["rs"] = out["rl_3"].to_numpy(), out["rs_3"].to_numpy()
    wc = walk_close.assign(date=walk_close["date"].astype(str), slot=walk_close["slot"].astype(np.int64))
    cl = wc[wc["side"].astype(int) > 0].set_index(["date", "slot"]).reindex(both)
    cs = wc[wc["side"].astype(int) < 0].set_index(["date", "slot"]).reindex(both)
    if cl[f"k{S}_3"].isna().any() or cs[f"k{S}_3"].isna().any():
        raise ValueError("the close walk does not cover every offer")
    for k_col in ("k", "x", "a"):                                  # 5.3: only a flattened trade's price differs
        for a, b in ((lo, cl), (sh, cs)):
            if not np.array_equal(a[f"{k_col}{S}_3"].astype(int).to_numpy(), b[f"{k_col}{S}_3"].astype(int).to_numpy()):
                raise ValueError(f"the close instance changed a trade's {k_col} (it may change a flatten's price only)")
    out["rl_close"] = net(cl, R_JUDGED)
    out["rs_close"] = net(cs, R_JUDGED)
    out["c"] = (out["rl"] + out["rs"]) / 2.0
    out["c_close"] = (out["rl_close"] + out["rs_close"]) / 2.0
    for name, wx in (extras or {}).items():
        wx = wx.assign(date=wx["date"].astype(str), slot=wx["slot"].astype(np.int64))
        xl = wx[wx["side"].astype(int) > 0].set_index(["date", "slot"]).reindex(both)
        xs = wx[wx["side"].astype(int) < 0].set_index(["date", "slot"]).reindex(both)
        if xl[f"k{S}_3"].isna().any() or xs[f"k{S}_3"].isna().any():
            raise ValueError(f"the walk {name!r} does not cover every offer")
        out[f"rl_{name}"], out[f"rs_{name}"] = net(xl, R_JUDGED), net(xs, R_JUDGED)
        out[f"c_{name}"] = (out[f"rl_{name}"] + out[f"rs_{name}"]) / 2.0
    out = out[offered].reset_index(drop=True)
    return out


def strata(pop: pd.DataFrame) -> pd.Series:
    """g = (mark, day kind, calendar year) as one key a row (7.1)."""
    return (pop["slot"].astype(np.int64).astype(str) + "|" + pop["day_kind"].astype(str) + "|"
            + pop["year"].astype(np.int64).astype(str))


def centre(pop: pd.DataFrame, g: pd.Series | None = None, value: str = "c", out: str = "y") -> pd.DataFrame:
    """`out` = value - mu_g, mu_g the mean of `value` over every row of the frame in the row's stratum (the twin's
    exact expectation, 7.2); computed within the frame given (the block read). The frame is returned with the column
    added (and `g`, `mu_<value>`)."""
    g = strata(pop) if g is None else g
    mu = pop.groupby(g.to_numpy())[value].transform("mean")
    res = pop.copy()
    res["g"] = g.to_numpy()
    res[f"mu_{value}"] = mu.to_numpy()
    res[out] = res[value].to_numpy() - mu.to_numpy()
    return res


def session_ordinals(dates: Sequence[str], calendar: Sequence[str]) -> np.ndarray:
    """Each date's ordinal in the block's calendar (every trading session counted, 7.2); refused for a date outside."""
    cal = {str(d): i for i, d in enumerate(sorted(str(x) for x in calendar))}
    try:
        return np.array([cal[str(d)] for d in dates], dtype=np.int64)
    except KeyError as exc:
        raise ValueError(f"the date {exc} is not in the block's calendar") from None


def offer_id(date: str, slot: int) -> str:
    """An offer's id, the join key between the replay's records and the population (18.1 item 4): `<date>|<slot>`."""
    return f"{date}|{int(slot)}"


def frame_sha256(pop: pd.DataFrame, columns: Sequence[str] | None = None) -> str:
    """The population frame's content hash (19.2's manifest): pandas' row hashes over the columns, sorted by name."""
    cols = sorted(pop.columns) if columns is None else list(columns)
    h = pd.util.hash_pandas_object(pop[cols].reset_index(drop=True), index=False).to_numpy()
    return hashlib.sha256(h.tobytes() + "|".join(cols).encode()).hexdigest()


# ------------------------------------------------------------------------------------------------ the session list


def judged_sessions(dates: Sequence[str]) -> tuple[list[str], str]:
    """(the judged block's session list, the sha256 of its ISO dates joined by LF): refused unless 657 sessions with
    E-094's sha256 (19.1, E-052 (3)'s assertions carried, 7.2)."""
    cal = sorted(str(d) for d in dates)
    if len(set(cal)) != len(cal):
        raise ValueError("REFUSED (F-03): the judged session list repeats a day")
    sha = hashlib.sha256("\n".join(cal).encode("ascii")).hexdigest()
    if len(cal) != JUDGED_SESSIONS_COUNT or sha != JUDGED_SESSIONS_SHA256:
        raise ValueError(f"REFUSED (F-03): the judged session list has {len(cal)} sessions and sha256 {sha[:12]}, not "
                         f"E-094's {JUDGED_SESSIONS_COUNT} and {JUDGED_SESSIONS_SHA256[:12]}")
    return cal, sha


def read_judged_sessions(results_dir) -> tuple[list[str], str]:
    """Q-83's session list from its result file (its manifest verified first), refused unless E-094's."""
    from pathlib import Path

    from extended.results import verify_result

    p = Path(results_dir) / JUDGED_SESSIONS_FILE
    ok, msg = verify_result(p)
    if not ok:
        raise ValueError(f"REFUSED (F-03): {p.name}: {msg}")
    d = pd.read_csv(p, dtype=str)
    return judged_sessions(d["date"].tolist())


class CoinArray:
    """`resolved_coin.coin_table`'s coins as an array lookup (the same rng and order: dates sorted, slots ascending,
    `u < 0.5` long) -- `scripts/q16_p16_pairs.py`'s."""

    def __init__(self, dates: Sequence[str], slots: Sequence[int], seed: int):
        self.ds = sorted(str(d) for d in dates)
        self.ss = sorted(int(s) for s in slots)
        self.di = {d: i for i, d in enumerate(self.ds)}
        self.si = {s: j for j, s in enumerate(self.ss)}
        u = np.random.default_rng(int(seed)).random(len(self.ds) * len(self.ss))
        self.side = np.where(u < 0.5, 1, -1).astype(np.int8)

    def __getitem__(self, key):
        d, s = key
        return int(self.side[self.di[str(d)] * len(self.ss) + self.si[int(s)]])

    def digest(self) -> str:
        return hashlib.sha256(self.side.tobytes() + "|".join(self.ds).encode() + str(self.ss).encode()).hexdigest()


# ------------------------------------------------------------------------------------------------ the real build


@dataclass
class Span:
    """A span's built inputs: the population frame (with labels), P-16's trades on the span, the walked days (date,
    day kind), the walk's grid of R, the admitted marks, the coin's digest."""
    population: pd.DataFrame
    trades: pd.DataFrame
    days: pd.DataFrame
    rr_grid: list[float]
    admitted: list[int]
    coin_digest: str
    walks: int


def admitted_marks(results_dir=None) -> list[int]:
    """P-16's admitted marks at 150 ticks: its screen file's `marks` section (D-525 (4)), the file's sha256 the one P-16
    pinned (`rc150_dev_test.SCREEN_SHA256`) -- read, never recomputed."""
    from pathlib import Path

    import a3_brk30 as B
    import rc150_dev_test as P16

    from propedge import RESULTS_DIR

    p = Path(results_dir or RESULTS_DIR) / P16.SCREEN_FILE
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    if sha != P16.SCREEN_SHA256:
        raise ValueError(f"REFUSED (F-03): {p.name} is not the file P-16 pinned ({sha[:12]})")
    s = B._exact(p)
    mk = s[(s["section"] == "marks") & (pd.to_numeric(s["stop_ticks"], errors="coerce") == STOP)]
    return sorted(int(x) for x, f in zip(pd.to_numeric(mk["slot"]), mk["offered"]) if str(f) == "True")


def p16_inputs() -> dict:
    """P-16's configuration and registered constants, none from a bar or walk: A3's config, FV3-C's, the tick value,
    the no-closure plan, the R keys; and from P-16's registered gate file (its manifest verified, floats to the last
    digit) the per-R shift (section `edge`: `e`, `lb_gate`) and the day capacity (`trades_per_day_capacity`) -- the
    bound arm's shift P-16 registered (12, C2; 4 item 4's disclosed pre-read). A0 holds them to `atlas_a3.bounds` and
    `a3_brk30.capacity` on the whole window's trades before they are trusted (its item 1)."""
    import a3_brk30 as B
    import a3_brk30_cb20 as Cb
    import atlas_a3 as A
    import zero_edge_decomposition as zd

    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_manifest

    cfg = A.config(A.FAMILY)
    fcfg = A.fv3_config(cfg)
    gate = Path(RESULTS_DIR) / "rc_s150_all_gate.csv"
    g = B._exact(gate)
    e = g[g["section"] == "edge"]
    plan = Cb.noclose_plan(RESULTS_DIR)
    return {"cfg": cfg, "fcfg": fcfg, "tv": float(A.TICK_VALUE), "plan": plan,
            "e_by": {float(r): float(v) for r, v in zip(e["rr"], e["e"])},
            "lb_by": {float(r): float(v) for r, v in zip(e["rr"], e["lb_gate"])},
            "cap": int(read_manifest(gate).parameters["trades_per_day_capacity"]),
            "keys": sorted(set(float(R) for R in A.rrs(cfg)) | set(zd.policy_rrs(plan)))}


def build_span(start: str, end: str, all_dates: Sequence[str], *, purpose: str | None = None,
               declaration: Any = None, repeat: str | None = None, results_dir=None,
               arrays_for: Callable[[list[str]], Callable[[str], tuple]] | None = None,
               days_table: pd.DataFrame | None = None, admitted: Sequence[int] | None = None,
               log: Callable[[str], None] = print,
               extra_rules: Mapping[str, W.Rules] | None = None) -> Span:
    """The span's population, labels and P-16 trades (the module docstring). `all_dates`: every stored session of the
    development window (the coin's grid); `purpose`/`declaration`/`repeat`: the reader's, for a judged span. Seams for
    the synthetic tests: `arrays_for(dates) -> arrays(day)`, `days_table` (date, day_kind) and `admitted` (the marks)
    replace the reads."""
    import a3_brk30_cb20 as Cb
    import atlas_a3 as A
    import rc_screen as S
    import zero_edge_decomposition as zd

    from propedge import RESULTS_DIR
    from propedge.outcomes.collect_core import c_slot
    from propedge.research import atlas_local
    from propedge.research import resolved_coin as rc

    from extended import reader

    rd = results_dir or RESULTS_DIR
    cfg = A.config(A.FAMILY)
    fcfg = A.fv3_config(cfg)
    tv = float(A.TICK_VALUE)
    plan = Cb.noclose_plan(rd)
    rr_grid = [float(R) for R in A.rrs(cfg)]
    keys = sorted(set(rr_grid) | set(zd.policy_rrs(plan)))
    cut = c_slot(*(int(x) for x in str(cfg["news"]["bls_cut_ct"]).split(":")))
    clear = c_slot(*rc.RELEASE_CLEAR_CT)
    if int(clear) != P16_REPORT_CLEAR:
        raise ValueError("REFUSED (F-03): Stage 2's release-clear mark is not 07:35 CT")
    admitted = admitted_marks(rd) if admitted is None else sorted(int(m) for m in admitted)
    if days_table is None:
        days = reader.read_walks("A1", "days", start, end, purpose=purpose, declaration=declaration, repeat=repeat,
                                 columns=["date", "day_kind"], what=f"F-03: A1's day table {start} to {end}")
    else:
        days = days_table[(days_table["date"].astype(str) >= start) & (days_table["date"].astype(str) <= end)]
    days = days.assign(date=days["date"].astype(str), day_kind=days["day_kind"].astype(str))
    span_dates = sorted(days["date"])
    if not set(span_dates) <= set(map(str, all_dates)):
        raise ValueError("REFUSED (F-03): the span holds a session the coin's grid lacks")
    coins = CoinArray(all_dates, rc.marks(), rc.COIN_SEED)
    fees = A.fee_by_stop(fcfg, (STOP,), tv)
    costs = W.Costs(float(fees[STOP]), tv, float(cfg["slip_ticks"]))
    crr = float(fcfg["state_policy"]["fresh"]["combine_rr"])
    kinds = dict(zip(days["date"], days["day_kind"]))
    mins = S.walked_minutes(days, admitted, cut)
    walk_dates = sorted(mins["date"].unique())
    tick = float(cfg["contract"]["tick"])

    def read_arrays(chunk: list[str]):
        if arrays_for is not None:
            return arrays_for(chunk)
        bars = reader.read_bars(chunk[0], chunk[-1], purpose=purpose, declaration=declaration, repeat=repeat,
                                what=f"F-03: the bars {chunk[0]} to {chunk[-1]}")
        by_day = {d: g for d, g in bars.groupby("day", sort=False)}

        def arrays(day: str):
            return tuple(np.array([np.nan if x is None else x for x in v], dtype=float)
                         for v in atlas_local.day_arrays(by_day.get(day, bars.iloc[0:0])))
        return arrays

    walks, closes = [], []
    extras: dict[str, list[pd.DataFrame]] = {n: [] for n in (extra_rules or {})}
    for i in range(0, len(walk_dates), CHUNK_DAYS):
        chunk = walk_dates[i:i + CHUNK_DAYS]
        arr = read_arrays(chunk)
        m = mins[mins["date"].isin(chunk)]
        walks.append(walk_offers(m, arr, rr_grid, rules=W.STAGE2, tick=tick))
        closes.append(walk_offers(m, arr, [R_JUDGED], rules=CLOSE_RULES, tick=tick))
        for n_, rules_ in (extra_rules or {}).items():
            extras[n_].append(walk_offers(m, arr, [R_JUDGED], rules=rules_, tick=tick))
        log(f"  F-03 walked {min(i + CHUNK_DAYS, len(walk_dates))}/{len(walk_dates)} days")
    walk = pd.concat(walks, ignore_index=True) if walks else walk_offers(mins.iloc[0:0], None, rr_grid)
    walk_close = pd.concat(closes, ignore_index=True)
    pop = population_frame(walk, walk_close, coins, kinds, admitted, rr_grid=rr_grid, costs=costs,
                           entry_ticks=float(cfg["slip_ticks"]),
                           extras={n_: pd.concat(v, ignore_index=True) for n_, v in extras.items() if v})
    raw = rc.cell_trades(walk, kinds, admitted, STOP, coins, fees, rr_grid=rr_grid, fresh_rr=crr, tick_value=tv,
                         entry_ticks=float(cfg["slip_ticks"]), cut=cut)
    trades = rc.drop_release_minute(zd.pad(raw, keys), clear) if len(raw) else raw
    return Span(pop, trades, days[["date", "day_kind"]].reset_index(drop=True), rr_grid, admitted, coins.digest(),
                int(len(walk)))


__all__ = ["STOP", "R_JUDGED", "CLOSE_RULES", "FIRST_MARK", "LAST_MARK", "REPORT_FIRST", "P16_REPORT_CLEAR",
           "JUDGED_SESSIONS_COUNT", "JUDGED_SESSIONS_SHA256", "walk_offers", "in_population", "p16_offered",
           "population_frame", "strata", "centre", "session_ordinals", "offer_id", "frame_sha256", "judged_sessions",
           "read_judged_sessions", "CoinArray", "Span", "admitted_marks", "p16_inputs", "build_span"]
