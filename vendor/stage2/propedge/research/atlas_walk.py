"""A signal-atlas family's walk over the local bar store (R5, D-460): every event of every declared pattern, and every
(event minute, delay, side) bracket walk, for every trading day of the family's development window.

The events come from `atlas_core.a_events` (the kits' code); the walks from `fast_walk.day_walks` (the kits' walk in
numpy, tested record for record); the days are classified as the kits classify them (`atlas_local.close_day`'s rules).
The tables are cached under `data/atlas/<family>/` (git-ignored: they are derived from licensed bars, and large) with a
manifest naming the bar store's parquet sha256, the config's sha256 and the code's; a cache whose inputs changed is
rebuilt, never read.
"""
from __future__ import annotations

import hashlib
import inspect
import json
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from propedge import CONFIG_DIR, REPO_ROOT
from propedge.outcomes import atlas_core
from propedge.outcomes.collect_core import C_FLAT, c_slot
from propedge.research import atlas_local, fast_walk

CACHE = REPO_ROOT / "data" / "atlas"
RTH_OPEN = c_slot(8, 30)


def config(family: str) -> dict[str, Any]:
    return yaml.safe_load((CONFIG_DIR / f"atlas_{family.lower()}.yaml").read_text(encoding="utf-8"))


#: The keys a family's walk and grid are read from: the walk's parameters (`params`), its days (the market and the
#: development window) and the cells built on it. A family that reads another's walk (`walk_family`, D-481 (1)) must
#: declare every one of them exactly as that family does.
WALK_KEYS = ("market", "bars", "development", "contract", "day", "entry_delays_min", "screen_delay_min", "slip_ticks",
             "side_rules", "brackets", "stop_maps", "cells", "patterns", "news")


def walk_source(family: str) -> tuple[str, dict[str, Any]]:
    """(the family whose walk `family` reads, that family's config). A family reads its own walk unless its config
    names a `walk_family` (D-481: A2 reads A1's); then the walk is that family's in every respect -- its config's
    parameters and days, its cache under `data/atlas/<walk family>/` and the cache's identity under ITS config's digest
    -- so a change to that family's config or to the bars still forces the rebuild that family itself would do, and
    the borrowing family never writes a cache of its own. Refused when the two configs differ in a walk key or the
    walk family borrows in turn."""
    cfg = config(family)
    src = str(cfg.get("walk_family") or family)
    if src == family:
        return family, cfg
    scfg = config(src)
    if str(scfg.get("walk_family") or src) != src:
        raise ValueError(f"{family} reads {src}'s walk, which reads {scfg['walk_family']}'s: name the walk's own family")
    differ = [k for k in WALK_KEYS if cfg.get(k) != scfg.get(k)]
    if differ:
        raise ValueError(f"{family} reads {src}'s walk but declares {differ} differently: the walk would not be its own")
    return src, scfg


def _hm(x: str) -> tuple[int, int]:
    return tuple(int(v) for v in str(x).split(":"))           # type: ignore[return-value]


def _clock(ct: str) -> int:
    """A CT time on the trading-day clock; 17:00 is the session's open, slot 0 (c_slot maps it to the next day's)."""
    return 0 if str(ct) == "17:00" else c_slot(*_hm(ct))


def t24_slots() -> list[int]:
    """T24's 23 decision slots (config/t24_capture.yaml): every hour start 17:00 to 14:00 CT and 08:30."""
    from propedge.data import t23_kit as tk
    return list(tk.params_t23("R149-t24-NQ-2021")["slots"])


def params(cfg: dict[str, Any]) -> dict[str, Any]:
    """The walk's parameters from a family's config: levels, brackets as level indices, delays, slip, the decision
    window, the patterns with their slots resolved, the BLS cut and the release days over the development window."""
    from propedge.data import flip_kit as fk

    tick = float(cfg["contract"]["tick"])
    brackets = [(float(a), float(b)) for a, b in cfg["brackets"]]
    levels = sorted({x for br in brackets for x in br})
    pats = []
    for p in cfg["patterns"]:
        q = {k: v for k, v in p.items() if k != "name"}
        if q["kind"] == "orb":
            q["open_slot"] = _clock(q["open_ct"])
            q.pop("open_ct")
        if q["kind"] == "clock":
            q["slots"] = t24_slots()
        pats.append(q)
    dev = cfg["development"]
    win = {"news": cfg["news"], "window": {"warm": dev["start"], "start": dev["start"], "end": dev["end"]}}
    fomc, bls = fk.collect_release_days(win)
    return {"tick": tick, "slip": tick * float(cfg["slip_ticks"]), "levels": levels,
            "brackets": [(levels.index(T), levels.index(S)) for T, S in brackets], "bracket_points": brackets,
            "delays": [int(x) for x in cfg["entry_delays_min"]], "screen_delay": int(cfg["screen_delay_min"]),
            "identity_slots": t24_slots(),
            "first_slot": _clock(cfg["day"]["first_decision_ct"]),
            "last_slot": c_slot(*_hm(cfg["day"]["last_decision_ct"])),
            "patterns": pats, "names": [p["name"] for p in cfg["patterns"]],
            "bls_cut": c_slot(*_hm(cfg["news"]["bls_cut_ct"])), "fomc": set(fomc), "bls": set(bls)}


def _arrays(day_bars: pd.DataFrame) -> tuple[np.ndarray, ...]:
    o, h, l, c = atlas_local.day_arrays(day_bars)
    return tuple(np.array([np.nan if x is None else x for x in a], dtype=float) for a in (o, h, l, c))


def _kind(o: np.ndarray, key: int, q: dict) -> tuple[str, int | None]:
    last = fast_walk.last_bar(o, C_FLAT)
    if last is None:
        return "x", None
    if last < C_FLAT - 10:
        return "e", None
    if key in q["fomc"]:
        return "o", None
    if key in q["bls"]:
        return "b", q["bls_cut"]
    return "n", None


def walk_days(root: str, days: list[str], q: dict, purpose: str, *, store=None, windows=None) -> tuple[pd.DataFrame, ...]:
    """(events, walks, day kinds) for `days` -- the window guard first, for the whole span."""
    from propedge.data.bars import read_bars
    from propedge.data.windows import WINDOWS_PATH

    bars = read_bars(root, min(days), max(days), purpose, store=store, windows=windows or WINDOWS_PATH,
                     what="atlas walk")
    by_day = {d: g for d, g in bars.groupby("day", sort=False)}
    P = {"patterns": q["patterns"], "first_slot": q["first_slot"], "last_slot": q["last_slot"], "prior": None}
    ev_rows, walk_rows, day_rows = [], [], []
    prior_range = None
    for day in days:
        g = by_day.get(day)
        o, h, l, c = _arrays(g if g is not None else bars.iloc[0:0])
        kind, cut = _kind(o, atlas_local.yymmdd(day), q)
        day_rows.append({"date": day, "day_kind": kind})
        if kind in ("n", "b"):
            lo = [None if np.isnan(x) else float(x) for x in o]
            hi = [None if np.isnan(x) else float(x) for x in h]
            lw = [None if np.isnan(x) else float(x) for x in l]
            cl = [None if np.isnan(x) else float(x) for x in c]
            P["prior"] = prior_range
            ev = atlas_core.a_events(lo, hi, lw, cl, P)
            for pid, t, d in ev:
                ev_rows.append((day, pid, t, d))
            slots = sorted({t for _, t, _ in ev})
            # the screened delay at every event minute; every walked delay at T24's slots (the identity's walks)
            plan = [(slots, [q["screen_delay"]]),
                    (sorted(set(q["identity_slots"])), [x for x in q["delays"] if x != q["screen_delay"]])]
            for sl, dls in plan:
                if not sl or not dls:
                    continue
                for t, dl, d, j0, outs in fast_walk.day_walks(o, h, l, c, sl, dls, q["levels"], q["brackets"],
                                                             q["slip"], q["tick"], C_FLAT, cut):
                    r = [day, t, dl, d, j0]
                    for k, m, u, gp, x in outs:
                        r += [k, m, u, gp, x]
                    walk_rows.append(r)
        if kind != "x":
            rng = atlas_core.a_rth_range([None if np.isnan(x) else float(x) for x in o],
                                         [None if np.isnan(x) else float(x) for x in h],
                                         [None if np.isnan(x) else float(x) for x in l], RTH_OPEN, C_FLAT)
            if rng is not None:
                prior_range = rng
    nb = len(q["brackets"])
    wcols = ["date", "slot", "delay", "side", "entry_slot"]
    for b in range(nb):
        wcols += [f"o{b}", f"m{b}", f"u{b}", f"g{b}", f"x{b}"]
    events = pd.DataFrame(ev_rows, columns=["date", "pattern", "slot", "side"]).astype(
        {"pattern": "int16", "slot": "int16", "side": "int8"})
    walks = pd.DataFrame(walk_rows, columns=wcols)
    small = {"slot": "int16", "delay": "int8", "side": "int8", "entry_slot": "int16"}
    for b in range(nb):
        small.update({f"o{b}": "category", f"m{b}": "int16", f"u{b}": "bool", f"g{b}": "int16", f"x{b}": "int32"})
    walks = walks.astype(small)
    walks = walks.sort_values(["date", "slot", "delay", "side"], kind="stable").reset_index(drop=True)
    return events, walks, pd.DataFrame(day_rows)


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def inputs_digest(family: str, root: str, store: Path | None = None) -> dict[str, str]:
    from propedge.data.bars import manifest
    m = manifest(root, store) or {}
    code = "".join(inspect.getsource(x) for x in (atlas_core, fast_walk, atlas_local)) + inspect.getsource(walk_days)
    return {"bars_parquet_sha256": str(m.get("parquet_sha256")),
            "config_sha256": _sha((CONFIG_DIR / f"atlas_{family.lower()}.yaml").read_bytes().replace(b"\r\n", b"\n")),
            "code_sha256": _sha(code.encode("utf-8"))}


def cached(family: str, root: str, days: list[str], q: dict, purpose: str, *, rebuild: bool = False) -> tuple[pd.DataFrame, ...]:
    """The family's walk, from the cache when its inputs are unchanged, else walked and cached."""
    d = CACHE / family
    want = {**inputs_digest(family, root), "days": len(days), "first": min(days), "last": max(days),
            "purpose": purpose}
    man = d / "manifest.json"
    if not rebuild and man.is_file() and json.loads(man.read_text(encoding="utf-8")).get("inputs") == want:
        return tuple(pd.read_parquet(d / f"{n}.parquet") for n in ("events", "walks", "days"))
    out = walk_days(root, days, q, purpose)
    d.mkdir(parents=True, exist_ok=True)
    for name, df in zip(("events", "walks", "days"), out):
        df.to_parquet(d / f"{name}.parquet", index=False)
    man.write_text(json.dumps({"inputs": want, "rows": {n: int(len(x)) for n, x in zip(("events", "walks", "days"), out)},
                               "written": date.today().isoformat()}, indent=1) + "\n", encoding="utf-8")
    return out


__all__ = ["CACHE", "WALK_KEYS", "config", "walk_source", "params", "t24_slots", "walk_days", "inputs_digest", "cached"]
