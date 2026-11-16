"""Batch S2 of the rolling model search (D-578 (4)): the state-gated coin -- the pure parts.

P-16 (`rc_s150_all`, the 37.5-point news-safe all-day coin, its own coin seed 20261102) is unchanged except that an offer
at (date, mark) is taken only when a declared ex-ante state holds. Two measures, each read at the mark from the session's
one-minute bars that have CLOSED at or before the mark (index j <= mark on the trading-day clock, `atlas_local.day_arrays`:
a bar's index is its END minute after 17:00 CT):

    vol   the last 30 closed bars' range: max(high) - min(low) over the 30 most recent bars of the session with index
          <= mark (bars that exist; a minute without a bar is not a bar); undefined with fewer than 30 such bars
    dist  |c[t] - the session's first-bar open|: c[t] the close of the last bar with index <= mark, the open the first
          bar of the session's arrays (17:00 CT, the bar ending 17:01; the first that exists); undefined with no bar yet

Each measure at (date, mark) is compared with the same measure at the same mark on the trailing 20 sessions: the 20 most
recent PRIOR sessions (earlier dates; P-16's walked day kinds, 'n' and 'b') with a value at that mark. With fewer than 20
such sessions, or no value today, the offer is unranked and kept by every cell.

    vol_low / vol_mid / vol_high   today's vol in the bottom / middle / top third of the trailing 20 (mid-rank share
                                   p = (#below + #equal / 2) / 20: p < 1/3 low, p > 2/3 high, else mid -- with no ties,
                                   today's rank among the 21 values is uniform on 0..20 under exchangeability and each
                                   third holds exactly 7 of the 21 ranks)
    trend / range                  today's dist above / at or below the trailing 20's median

Gating removes offers from P-16's built trades before the engine; the offers kept keep P-16's coin side.
"""
from __future__ import annotations

from typing import Callable, Mapping, Sequence

import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

DECISION = "D-578"
BATCH = "S2"
VOL_BARS = 30                              # D-578 (4): the last 30 closed 1-min bars' range
TRAIL = 20                                 # the trailing 20 sessions (prior sessions only)
WALK_KINDS = ("n", "b")                    # P-16's walked day kinds (a3_resolution_map.WALK_DAY_KINDS)
CELLS = ("vol_low", "vol_mid", "vol_high", "trend", "range")
OPEN = "open"                              # every gate open: P-16 itself (the identity)
VOL_CLASSES = ("low", "mid", "high")
TREND_CLASSES = ("trend", "range")
UNRANKED = ""
#: cell -> (the state column it reads, the class it keeps); an unranked offer is kept by every cell
RULES: dict[str, tuple[str, str]] = {"vol_low": ("vol_class", "low"), "vol_mid": ("vol_class", "mid"),
                                     "vol_high": ("vol_class", "high"), "trend": ("trend_class", "trend"),
                                     "range": ("trend_class", "range")}


# ------------------------------------------------------------------------------------------------ one session


def session_measures(o, h, l, c, marks: Sequence[int], vol_bars: int = VOL_BARS) -> tuple[np.ndarray, np.ndarray]:
    """(vol, dist) at each mark for one session's arrays (index = a bar's end minute after 17:00 CT, NaN where no bar).
    Only bars with index <= the mark are read; index 0 is never a bar (`atlas_local.day_arrays` keeps 1..1330)."""
    o, h, l, c = (np.asarray(x, dtype=float) for x in (o, h, l, c))
    n = len(o)
    exist = ~np.isnan(o) & ~np.isnan(h) & ~np.isnan(l) & ~np.isnan(c)
    exist[0] = False
    idx = np.flatnonzero(exist)
    m = np.asarray([int(x) for x in marks], dtype=int)
    vol = np.full(len(m), np.nan)
    dist = np.full(len(m), np.nan)
    if idx.size == 0:
        return vol, dist
    # k = the number of existing bars with index <= mark
    k = np.searchsorted(idx, np.minimum(m, n - 1), side="right")
    k[m < 0] = 0
    first_open = float(o[idx[0]])
    has = k >= 1
    dist[has] = np.abs(c[idx[k[has] - 1]] - first_open)
    if idx.size >= vol_bars:
        hh = sliding_window_view(h[idx], vol_bars).max(axis=1)      # window w covers existing bars w .. w+vol_bars-1
        ll = sliding_window_view(l[idx], vol_bars).min(axis=1)
        ok = k >= vol_bars
        w = k[ok] - vol_bars
        vol[ok] = hh[w] - ll[w]
    return vol, dist


# ------------------------------------------------------------------------------------------------ the trailing rule


def trailing_windows(values: np.ndarray, eligible: np.ndarray, trail: int = TRAIL) -> tuple[np.ndarray, np.ndarray]:
    """For one mark's column (sessions in date order): (has, windows) -- `has[i]` True when today's value is finite and
    at least `trail` earlier sessions are eligible with a finite value; `windows[i]` (rows where `has`) those sessions'
    `trail` most recent values. Only rows before i are read."""
    v = np.asarray(values, dtype=float)
    ok = np.asarray(eligible, dtype=bool) & np.isfinite(v)
    prior = np.cumsum(ok) - ok                                       # eligible finite sessions strictly before i
    has = np.isfinite(v) & (prior >= int(trail))
    P = v[ok]
    if not has.any():
        return has, np.empty((0, int(trail)))
    win = sliding_window_view(P, int(trail))[prior[has] - int(trail)]
    return has, win


def thirds(x: np.ndarray, win: np.ndarray) -> np.ndarray:
    """'low' / 'mid' / 'high' by today's mid-rank share among the window (p < 1/3, p > 2/3, else mid)."""
    x = np.asarray(x, dtype=float)[:, None]
    n = win.shape[1]
    p = ((win < x).sum(axis=1) + 0.5 * (win == x).sum(axis=1)) / float(n)
    return np.where(p < 1.0 / 3.0, "low", np.where(p > 2.0 / 3.0, "high", "mid")).astype(object)


def halves(x: np.ndarray, win: np.ndarray) -> np.ndarray:
    """'trend' above the window's median, else 'range' (at or below)."""
    x = np.asarray(x, dtype=float)
    return np.where(x > np.median(win, axis=1), "trend", "range").astype(object)


def classes(values: np.ndarray, eligible: np.ndarray, how: Callable, trail: int = TRAIL) -> np.ndarray:
    """A (sessions x marks) value matrix's classes, column by column: `how(today, windows)` where ranked, else
    `UNRANKED`."""
    V = np.asarray(values, dtype=float)
    out = np.full(V.shape, UNRANKED, dtype=object)
    for j in range(V.shape[1]):
        has, win = trailing_windows(V[:, j], eligible, trail)
        if has.any():
            out[has, j] = how(V[has, j], win)
    return out


# ------------------------------------------------------------------------------------------------ the state table


def state_table(dates: Sequence[str], kinds: Mapping[str, str], arrays: Callable[[str], tuple], marks: Sequence[int],
                *, walk_kinds: Sequence[str] = WALK_KINDS, trail: int = TRAIL, vol_bars: int = VOL_BARS) -> pd.DataFrame:
    """One row per (date, mark) of every session of a walked kind: the two measures and their classes. `arrays(date)`
    gives the session's (o, h, l, c) on the trading-day clock."""
    ds = sorted(str(d) for d in dates if str(kinds.get(str(d), "")) in set(walk_kinds))
    if len(set(ds)) != len(ds):
        raise ValueError("state_table: duplicate session dates")
    mk = [int(x) for x in marks]
    vol = np.full((len(ds), len(mk)), np.nan)
    dist = np.full((len(ds), len(mk)), np.nan)
    for i, d in enumerate(ds):
        o, h, l, c = arrays(d)
        vol[i], dist[i] = session_measures(o, h, l, c, mk, vol_bars)
    elig = np.ones(len(ds), dtype=bool)                             # every row is a walked-kind session
    vc = classes(vol, elig, thirds, trail)
    tc = classes(dist, elig, halves, trail)
    return pd.DataFrame({"date": np.repeat(ds, len(mk)), "slot": np.tile(mk, len(ds)), "vol": vol.ravel(),
                         "dist": dist.ravel(), "vol_class": vc.ravel(), "trend_class": tc.ravel()})


# ------------------------------------------------------------------------------------------------ the gate


def keep_mask(trades: pd.DataFrame, table: pd.DataFrame, cell: str) -> np.ndarray:
    """True for each trade (offer) the cell takes. Fail-loud: every offer's (date, decision mark) must be in the table."""
    if cell != OPEN and cell not in RULES:
        raise ValueError(f"unknown S2 cell {cell!r}; one of {(OPEN,) + CELLS}")
    if trades is None or len(trades) == 0:
        return np.zeros(0, dtype=bool)
    key = pd.MultiIndex.from_arrays([trades["date"].astype(str), trades["decision_slot_minutes"].astype(int)])
    tab = table.set_index(["date", "slot"])
    if not tab.index.is_unique:
        raise ValueError("the state table holds a (date, mark) twice")
    miss = ~key.isin(tab.index)
    if miss.any():
        raise ValueError(f"{int(miss.sum())} offers have no state row (first {key[miss][0]})")
    if cell == OPEN:
        return np.ones(len(trades), dtype=bool)
    col, want = RULES[cell]
    got = tab[col].reindex(key).astype(str).to_numpy()
    return (got == UNRANKED) | (got == want)


def gate(trades: pd.DataFrame, table: pd.DataFrame, cell: str) -> pd.DataFrame | None:
    """The cell's trades: P-16's offers the state admits, every column and the order unchanged (sides are P-16's coin);
    None when no offer is kept."""
    if trades is None or len(trades) == 0:
        return None
    keep = keep_mask(trades, table, cell)
    out = trades[keep].reset_index(drop=True)
    return out if len(out) else None


def offer_counts(trades: pd.DataFrame, table: pd.DataFrame) -> list[dict]:
    """Per cell: offers, kept, the kept share and the ranked offers (the unranked share is kept by every cell)."""
    key = pd.MultiIndex.from_arrays([trades["date"].astype(str), trades["decision_slot_minutes"].astype(int)])
    tab = table.set_index(["date", "slot"])
    out = []
    for cell in CELLS:
        col, _ = RULES[cell]
        got = tab[col].reindex(key).astype(str).to_numpy()
        keep = keep_mask(trades, table, cell)
        out.append({"cell": cell, "offers": int(len(trades)), "offers_kept": int(keep.sum()),
                    "kept_share": float(keep.mean()) if len(keep) else float("nan"),
                    "ranked_share": float((got != UNRANKED).mean()) if len(got) else float("nan")})
    return out


def partition_problems(trades: pd.DataFrame, table: pd.DataFrame) -> list[str]:
    """The three vol cells cover every ranked offer exactly once, and trend + range likewise; every unranked offer is
    kept by every cell of its measure."""
    out = []
    key = pd.MultiIndex.from_arrays([trades["date"].astype(str), trades["decision_slot_minutes"].astype(int)])
    tab = table.set_index(["date", "slot"])
    for group, col in (("vol", "vol_class"), ("trend/range", "trend_class")):
        cells = [c for c in CELLS if RULES[c][0] == col]
        ranked = tab[col].reindex(key).astype(str).to_numpy() != UNRANKED
        n_kept = np.sum([keep_mask(trades, table, c) for c in cells], axis=0)
        if not np.all(n_kept[ranked] == 1):
            out.append(f"{group}: {int(np.sum(n_kept[ranked] != 1))} ranked offers not kept by exactly one cell")
        if not np.all(n_kept[~ranked] == len(cells)):
            out.append(f"{group}: {int(np.sum(n_kept[~ranked] != len(cells)))} unranked offers not kept by every cell")
    return out


# ------------------------------------------------------------------------------------------------ the declaration
#
# `config/search_program.yaml` is not valid YAML as written (S1's `none yet today: tie`, S2's `|c[t] ...`) and is never
# edited: it is read as text, its sha256 (LF line ends) pinned as S1 pins it (`s1_sided_coin.DECLARATION_SHA256`, one
# constant for the one file), S2's block located and every constant here checked against its words.

ALPHA = 0.00833                            # batch 2's family-wise level, 0.05 / (2 x 3)
N_VARIANTS = 5
COIN_SEED = 20261102                       # P-16's own coin (resolved_coin.COIN_SEED)
#: phrases of S2's block each constant above rests on (the block's own words, line breaks folded to spaces)
S2_WORDS = ("name: state-gated coin", "status: declared", f"alpha: {ALPHA:g}", f"variants: {N_VARIANTS}",
            f"P-16 unchanged (its coin, seed {COIN_SEED})", f"the trailing {TRAIL} sessions' values of the same measure "
            "at the same mark", "(prior sessions only;", f"fewer than {TRAIL} prior sessions -> the offer is kept",
            f"last-{VOL_BARS}-bar high-low range in the bottom third", "in the middle third", "in the top third",
            "|c[t] - session open| above its trailing median", "|c[t] - session open| at or below its trailing median",
            "judged directly by the campaign guards (no stage 1)")
GUARD_WORDS = ("by more than 0.05", "resolves every offered R", "at least 40 of 50",
               "coin seeds 20261600 + i, 200 paths", "not below P-16 on either span alone (2020-2023, 2024-2026-07-16)",
               "reference: P-16")


def declaration(path=None) -> dict:
    """The program file as text (`s1_sided_coin.declaration`: its path, sha256 and program block) with S2's block and
    S2's cell names in their order."""
    import re
    from pathlib import Path

    from propedge.research import s1_sided_coin as S1

    d = S1.declaration(path)
    text = Path(d["path"]).read_bytes().replace(b"\r\n", b"\n").decode("utf-8")
    m = re.search(r"\n  - id: S2\n(.*?)(?=\n  - id: |\nproposed_not_declared:|\Z)", text, flags=re.S)
    block = m.group(1) if m else ""
    c = re.search(r"\n    cells:[^\n]*\n((?:      [^\n]*\n)+)", block + "\n")
    names = re.findall(r"^      (\w+):", c.group(1), flags=re.M) if c else []
    return {"path": d["path"], "sha256": d["sha256"], "program": d["program"], "batch": block, "cells": names}


def declaration_problems(decl: Mapping) -> list[str]:
    """Every way this module's constants differ from the declaration (an empty list: they agree)."""
    import re

    from propedge.research import s1_sided_coin as S1

    out = []
    if str(decl["sha256"]) != S1.DECLARATION_SHA256:
        out.append(f"the declaration's sha256 is {str(decl['sha256'])[:16]}, not D-578's {S1.DECLARATION_SHA256[:16]}")
    fold = lambda s: re.sub(r"\s+", " ", str(s))   # noqa: E731
    b, prog = fold(decl["batch"]), fold(decl["program"])
    if not b:
        out.append("no S2 batch in the declaration")
    if f"decision: {DECISION}" not in prog:
        out.append(f"the program is not {DECISION}'s")
    if tuple(decl["cells"]) != CELLS:
        out.append(f"cells {list(decl['cells'])}, not {list(CELLS)}")
    if len(CELLS) != N_VARIANTS:
        out.append("the cells are not the declared variant count")
    out += [f"S2's block does not say {w!r}" for w in S2_WORDS if w not in b]
    out += [f"the program does not say {w!r}" for w in GUARD_WORDS if w not in prog]
    return out


__all__ = ["DECISION", "BATCH", "VOL_BARS", "TRAIL", "WALK_KINDS", "CELLS", "OPEN", "RULES", "UNRANKED", "ALPHA",
           "N_VARIANTS", "COIN_SEED", "session_measures", "trailing_windows", "thirds", "halves", "classes",
           "state_table", "keep_mask", "gate", "offer_counts", "partition_problems", "declaration",
           "declaration_problems"]
