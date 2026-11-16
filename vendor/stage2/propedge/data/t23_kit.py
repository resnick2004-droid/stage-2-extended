"""T23's per-trade capture kits (D-416): R147-t23-NQ-2022 and R148-t23-NQ-2025.

The collect map's kit (`flip_kit`, D-381) with its minute bookkeeping, contract roll and second-bar history requests
unchanged; at each day's close the walks run with no box (`t23_core.T_NO_BOX`: to the day's last bar or the BLS cut,
D-212) and every walk leaves as one record -- each bracket's outcome and minutes (`t23_core.t_records`) -- with one day
record (`t23_core.t_day`: the day's kind and the A3 sign per slot). Records leave in order tags, one emit a year.
"""
from __future__ import annotations

import inspect
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from propedge.data import flip_kit as fk

CONFIG_FILE = "t23_capture.yaml"
T23_PREFIX = "FM8"
T23_HEAD_EXTRA = ("fomc", "bls", "ties", "secreq", "secbars", "nosec", "nosecbar", "records", "dayrecs")
T23_HEAD_TEXT = tuple(fk.SECONDS_HEAD_TEXT)


#: D-428: the captures this kit serves -- T23's (D-416) and T24's -- each run named in exactly one of them
CAPTURE_FILES = (CONFIG_FILE, "t24_capture.yaml", "t24_confirm.yaml")   # D-439: the held-back capture


def config_t23(path: Path | None = None) -> dict[str, Any]:
    return yaml.safe_load(Path(path or fk.CONFIG_DIR / CONFIG_FILE).read_text(encoding="utf-8"))


def config_for_run(run: str) -> dict[str, Any]:
    """D-428: the capture config that declares `run` (T23's or T24's); refused when none or more than one does."""
    found = [c for c in (config_t23(fk.CONFIG_DIR / f) for f in CAPTURE_FILES)
             if run in {str(r["run"]) for r in c["runs"]}]
    if len(found) != 1:
        raise ValueError(f"no run {run!r} in {', '.join(CAPTURE_FILES)}" if not found else
                         f"run {run!r} is declared by more than one capture")
    return found[0]


def runs_t23(cfg: dict | None = None) -> dict[str, tuple[date, date, date]]:
    """Each run's (warm, start, end)."""
    cfg = cfg or config_t23()
    return {str(r["run"]): tuple(date.fromisoformat(str(r[k])) for k in ("warm", "start", "end")) for r in cfg["runs"]}


def params_t23(run: str, cfg: dict | None = None) -> dict[str, Any]:
    """The kit's parameters for `run`: the collect map's slots and clock labels, the brackets as level indices, the
    delays, the BLS cut, the release days; the walk's PARAMS (one box past any day's end)."""
    from propedge.outcomes.collect_core import c_slot
    from propedge.outcomes.t23_core import T_NO_BOX

    cfg = cfg or config_for_run(run)
    day = cfg["day"]

    def hm(x):
        return tuple(map(int, str(x).split(":")))

    last = c_slot(*hm(day["last_decision_ct"]))
    times = set(range(0, last + 1, int(day["decision_every_min"])))
    for x in day.get("extra_decisions_ct") or ():
        times.add(c_slot(*hm(x)))
    times = sorted(times)
    labels = [f"{((17 * 60 + t) % 1440) // 60:02d}:{(17 * 60 + t) % 60:02d}" for t in times]
    k = cfg["contract"]
    tick = float(k["tick"])
    brackets = [(float(a), float(b)) for a, b in cfg["brackets"]]
    for T, S in brackets:
        for x, what in ((T, "target"), (S, "stop")):
            if not (x > 0 and abs(x / tick - round(x / tick)) < 1e-9):
                raise ValueError(f"the {what} of {x:g} points is not a positive whole number of ticks")
    if len(set(brackets)) != len(brackets):
        raise ValueError("each bracket once")
    levels = sorted({x for b in brackets for x in b})
    idx = [(levels.index(T), levels.index(S)) for T, S in brackets]
    delays = [int(x) for x in cfg["entry_delays_min"]]
    if delays[0] != 0 or sorted(delays) != delays:
        raise ValueError("the delays ascend from on time")
    windows = runs_t23(cfg)
    if run not in windows:
        raise ValueError(f"no run {run!r} in {CONFIG_FILE}")
    warm, start, end = windows[run]
    fomc, bls = fk.collect_release_days({**cfg, "window": {"warm": str(warm), "start": str(start), "end": str(end)}})
    return {"run": run, "market": str(cfg["market"]), "ticker": str(k["ticker"]), "tick": tick,
            "point_value": float(k["point_value"]), "micro": str(k["micro"]),
            "micro_point_value": float(k["micro_point_value"]), "slots": times, "slot_labels": labels,
            "brackets": brackets, "levels": levels, "delays": delays,
            "bls_cut": c_slot(*hm(cfg["news"]["bls_cut_ct"])), "fomc_days": fomc, "bls_days": bls,
            "warm": warm, "start": start, "end": end, "y0": start.year, "time_unit": "minute", "prefix": T23_PREFIX,
            "head_extra": list(T23_HEAD_EXTRA), "head_text": list(T23_HEAD_TEXT),
            "p": {"slots": times, "delays": delays, "boxes": [T_NO_BOX], "levels": levels,
                  "slip": tick * float(cfg["slip_ticks"]), "pairs": [idx], "brackets": idx, "tick": tick}}


def preamble_t23(run: str, cfg: dict | None = None) -> str:
    from propedge.outcomes import collect_core, t23_core

    cfg = cfg or config_for_run(run)
    q = params_t23(run, cfg)
    w0, w1 = q["start"], q["end"]
    return f'''
MARKET = "{q["ticker"]}"
TICK = {q["tick"]!r}
WIN_START = ({w0.year}, {w0.month}, {w0.day})   # earlier days are warm-up and record nothing
WIN_END = ({w1.year}, {w1.month}, {w1.day})
FILTER_DAYS = 120
PREFIX = "{T23_PREFIX}"
LOG_BUDGET_BYTES = {fk.LOG_BUDGET_BYTES}
TAG_CHARS = {fk.FLIP_TAG_CHARS}
PARAMS = {q["p"]!r}
BLS_CUT = {q["bls_cut"]}                # the last bar before a BLS 08:30 ET release (07:30 CT) on the trading-day clock
GROUP = {fk.COLLECT_GROUP_MINUTES}
FOMC = frozenset(int(x) for x in "{",".join(str(x) for x in q["fomc_days"])}".split(","))   # yymmdd: no walk
BLS = frozenset(int(x) for x in "{",".join(str(x) for x in q["bls_days"])}".split(","))     # yymmdd: ended by BLS_CUT
from datetime import timedelta as _delta
from datetime import datetime as _dt


class CarrierInitializer(BrokerageModelSecurityInitializer):
    """Zero fees: the carrier orders' own P&L is never used."""

    def initialize(self, security):
        super().initialize(security)
        security.set_fee_model(ConstantFeeModel(0))


def _clean(text):
    out = "".join((ch if (ch.isalnum() or ch in ".,:_-[]()") else "_") for ch in str(text))
    return out[:160] if out else "none"


def iter_history_bars(hist):
    """(end time, open, high, low, close) per row; the time is the LAST index level (expiry, symbol, time)."""
    try:
        if hist is None or len(hist) == 0:
            return
        idx = hist.index
        times = idx.get_level_values(-1) if getattr(idx, "nlevels", 1) > 1 else idx
        for t, bo, bh, bl, bc in zip(times, hist["open"], hist["high"], hist["low"], hist["close"]):
            if isinstance(t, tuple):
                t = t[-1]
            t = t.to_pydatetime() if hasattr(t, "to_pydatetime") else t
            yield t, float(bo), float(bh), float(bl), float(bc)
    except Exception:
        return


# ---------------------------------------------------------------- embedded verbatim from
# ---------------------------------------------------------------- propedge/outcomes/collect_core.py
{inspect.getsource(collect_core)}
# ---------------------------------------------------------------- end of the embedded core
# ---------------------------------------------------------------- embedded verbatim from
# ---------------------------------------------------------------- propedge/outcomes/t23_core.py
{inspect.getsource(t23_core)}
# ---------------------------------------------------------------- end of the embedded core
'''


# The collect kit's body with three parts replaced: the accumulators (records, not counts), the day's close (records)
# and the emit/HEAD (records; two counters added). Each anchor is checked, so a change to the collect body is refused.
_SETUP_OLD = "    self._acc, self._aux, self._year, self._emitted = {}, {}, None, 0\n"
_SETUP_NEW = "    self._recs, self._year, self._emitted, self._records, self._dayrecs = [], None, 0, 0, 0\n"
_CLOSE_START = "def _close_day(self):\n"
_CLOSE_END = "def on_end_of_algorithm(self):\n"
_CLOSE_NEW = '''def _close_day(self):
    d = self._day
    self._day = None
    if d["td"] < WIN_START or d["td"] > WIN_END:
        self._warm += 1
        return
    year = d["td"][0]
    if self._year is not None and year != self._year:
        self._emit()
    self._year = year
    self._n += 1
    o, h, l, cl = d["o"], d["h"], d["l"], d["cl"]
    key = (year % 100) * 10000 + d["td"][1] * 100 + d["td"][2]
    last = c_last(o)
    a3 = t_a3(cl, PARAMS["slots"])
    if last is None:
        self._noref += 1
        kind = "x"
    elif last < C_FLAT - 10:
        self._early += 1
        kind = "e"
    elif key in FOMC:
        self._fomc += 1
        kind = "o"
    else:
        cut = None
        kind = "n"
        if key in BLS:
            cut = BLS_CUT
            self._bls += 1
            kind = "b"
        walks = c_walks(o, h, l, cl, PARAMS, cut)
        self._entries += len(walks)
        secs = self._tied(d, sorted(c_ties(walks, PARAMS)))

        def tie(j, entry, dd, T, S):
            s = secs.get(j)
            return None if s is None else c_tie(s[0], s[1], s[2], entry, dd, T, S)

        recs = t_records(walks, PARAMS, tie)
        self._recs.extend(recs)
        self._records += len(recs)
    self._recs.append(t_day(d["td"], kind, a3))
    self._dayrecs += 1
    if d["td"] >= WIN_END:
        self._emit()
        self._done = True

def _emit(self):
    cells = self._recs
    self._recs = []
    if not cells:
        return
    chunks, cur = [], ""
    for x in cells:
        if cur and len(cur) + 1 + len(x) > TAG_CHARS:
            chunks.append(cur)
            cur = x
        else:
            cur = x if not cur else cur + "/" + x
    chunks.append(cur)
    self._emitted += 1
    carrier = self._active or self.future.mapped
    for k, x in enumerate(chunks):
        tag = "F|e=" + str(self._emitted) + ";k=" + str(k) + ";K=" + str(len(chunks)) + ";x=" + x
        self._orders += 1
        self.market_order(carrier, 1 if self._orders % 2 else -1, tag=tag)

'''
_END_OLD = "    if self._acc or self._aux:\n        self._emit()\n"
_END_NEW = "    if self._recs:\n        self._emit()\n"
_HEAD_OLD = '            + "|nosecbar=" + str(self._nosecbar)\n'
_HEAD_NEW = ('            + "|nosecbar=" + str(self._nosecbar)\n'
             '            + "|records=" + str(self._records) + "|dayrecs=" + str(self._dayrecs)\n')


def body_t23() -> str:
    b = fk.BODY_COLLECT
    for old in (_SETUP_OLD, _CLOSE_START, _CLOSE_END, _END_OLD, _HEAD_OLD):
        if b.count(old) != 1:
            raise ValueError(f"the collect body's anchor {old.strip()[:40]!r} is not there exactly once")
    b = b.replace(_SETUP_OLD, _SETUP_NEW)
    i, j = b.index(_CLOSE_START), b.index(_CLOSE_END)
    b = b[:i] + _CLOSE_NEW + b[j:]
    return b.replace(_END_OLD, _END_NEW).replace(_HEAD_OLD, _HEAD_NEW)


BODY_T23 = body_t23()

__all__ = ["CONFIG_FILE", "T23_PREFIX", "T23_HEAD_EXTRA", "T23_HEAD_TEXT", "CAPTURE_FILES", "config_t23", "config_for_run",
           "runs_t23", "params_t23", "preamble_t23", "body_t23", "BODY_T23"]
