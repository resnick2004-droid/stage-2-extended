"""ORB3's QuantConnect kits (config/orb3_search.yaml; T15 item 9, D-256): NQ in three runs -- R102 (2009-06 to 2014),
R103 (2015 to 2019) and R104 (2020 to June 2025), all development data under D-237 -- split so each carries about as
many order tags as runs that have completed.

ORB1's kit (`propedge/data/orb_kit.py`'s body: its histories, its every-contract volume, its roll handling) with one
named edit: each day writes ORB3's record (`propedge/outcomes/orb3_core.py` `day_record3`) instead of ORB1's -- the
first passages of every stop width of the grid, so the whole grid is scored from these runs. Only the day records leave
(D-120), never bars. HEAD's version is 3 and its prefix OR3, so neither parser can read the other's output.

The kit embeds `regime_core` and then only what ORB3's record uses -- orb_core's constants and helper functions
(`window_stats`, `direction`, `last_close_by`, `trigger`, `true_range`, `encode_day`) and orb3_core -- verbatim, with
the modules' docstrings and import lines removed, to fit QuantConnect's 32,000-character editor.
"""
from __future__ import annotations

import ast
import inspect
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from propedge import CONFIG_DIR
from propedge.data import orb_kit as ok
from propedge.data import regime_kit as rk

ORB3_PREFIX = "OR3"
MARKET = "NQ"


def config(path: Path | None = None) -> dict[str, Any]:
    return yaml.safe_load(Path(path or CONFIG_DIR / "orb3_search.yaml").read_text(encoding="utf-8"))


ORB3_RUNS = tuple(config()["runs"])


def dates(run: str, cfg: dict | None = None) -> tuple[date, date, date]:
    d = (cfg or config())["runs"][run]
    return tuple(date.fromisoformat(str(d[k])) for k in ("warm", "start", "end"))


def params(cfg: dict | None = None) -> dict[str, Any]:
    cfg = cfg or config()
    q = ok.params(MARKET)
    stops = tuple(float(s) for s in cfg["search"]["stop_atr"])
    rr = tuple(sorted({float(cfg["fixed"]["funded"]["rr"]), float(cfg["fixed"]["combine"]["rr"])}))
    return {**q, "stops": stops, "favour_rr": rr, "atr_days": int(cfg["fixed"]["atr_days"]),
            "rv_days": int(cfg["fixed"]["relative_volume_days"]),
            "p": {"tick": q["micro_tick"], "slip": q["micro_tick"], "stops": stops, "rr": rr}}


_ORB_CORE_PARTS = ("_bars", "window_stats", "direction", "last_close_by", "trigger", "true_range", "encode_day")


def _cores() -> str:
    """orb_core's constants and helpers, then orb3_core without its docstring and import: verbatim, function by
    function."""
    from propedge.outcomes import orb3_core, orb_core

    consts = (f"OR_START, OR_MIN, OR_MINS, PRE_START, NONE = {orb_core.OR_START!r}, {orb_core.OR_MIN!r}, "
              f"{orb_core.OR_MINS!r}, {orb_core.PRE_START!r}, {orb_core.NONE!r}\n"
              "FLAT_ENTRY = FLAT - 2                # 15:08 CT, slot 1328 (orb_core)\n")
    assert orb_core.FLAT_ENTRY == __import__("propedge.outcomes.regime_core", fromlist=["FLAT"]).FLAT - 2
    helpers = "\n\n".join(inspect.getsource(getattr(orb_core, f)) for f in _ORB_CORE_PARTS)
    src = ok._without_docstring(inspect.getsource(orb3_core))
    imports = [n for n in ast.parse(src).body if isinstance(n, (ast.Import, ast.ImportFrom))]
    assert len(imports) == 1 and imports[0].module == "propedge.outcomes.orb_core", imports
    lines = src.splitlines(keepends=True)
    body = "".join(lines[:imports[0].lineno - 1] + lines[imports[0].end_lineno:])
    return consts + "\n\n" + helpers + "\n\n" + body


def preamble(run: str) -> str:
    from propedge.outcomes import regime_core

    q = params()
    _, w0, w1 = dates(run)
    return f'''
MARKET = "{MARKET}"
TICK = {q["tick"]!r}                    # the standard contract's tick (the data)
MICRO_TICK = {q["micro_tick"]!r}        # the micro's tick (slippage, stop sizes)
WIN_START = ({w0.year}, {w0.month}, {w0.day})   # days before this are warm-up: they fill the histories only
WIN_END = ({w1.year}, {w1.month}, {w1.day})
FILTER_DAYS = 120
PREFIX = "{ORB3_PREFIX}"
LOG_BUDGET_BYTES = {rk.LOG_BUDGET_BYTES}
TAG_CHARS = {rk.REGIME_TAG_CHARS}
PARAMS = {q["p"]!r}
ATR_DAYS = {q["atr_days"]!r}
RV_DAYS = {q["rv_days"]!r}
FIXED_STOPS = []
RANGE_DAYS = 20
RANGE_MULTIPLES = []
WIDE_SPREAD_TICKS = 4.0
WIDE_SPREAD_CAP = 50.0
from datetime import timedelta as _delta


class CarrierInitializer(BrokerageModelSecurityInitializer):
    """Zero fees: the carrier orders' own P&L is never used, so nothing is modelled on them."""

    def initialize(self, security):
        super().initialize(security)
        security.set_fee_model(ConstantFeeModel(0))


# ---------------------------------------------------------------- embedded verbatim from
# ---------------------------------------------------------------- propedge/outcomes/regime_core.py (its docstring removed)
{ok._without_docstring(inspect.getsource(regime_core))}
# ---------------------------------------------------------------- orb_core's constants and helpers, and
# ---------------------------------------------------------------- propedge/outcomes/orb3_core.py (docstring and import removed)
{_cores()}
# ---------------------------------------------------------------- end of the embedded cores
'''


_EDITS3 = (
    ('''            rec = day_record(o, h, l, cl, vt, ls, PARAMS, hist)''',
     '''            rec = day_record3(o, h, l, cl, vt, ls, PARAMS, hist)   # ORB3: the grid's first passages'''),
    ('''    head = (PREFIX + "|HEAD|v=2|market=" + MARKET + "|days=" + str(self._n) + "|warm=" + str(self._warm)''',
     '''    head = (PREFIX + "|HEAD|v=3|market=" + MARKET + "|days=" + str(self._n) + "|warm=" + str(self._warm)'''),
)
BODY = ok.BODY
for _old, _new in _EDITS3:
    assert BODY.count(_old) == 1, _old[:60]
    BODY = BODY.replace(_old, _new)
BODY = BODY.replace("# T15, D-249: ORB1's day records at actual prices, on the regime map's body",
                    "# T15, D-256: ORB3's day records at actual prices, on ORB1's body")


__all__ = ["ORB3_PREFIX", "MARKET", "ORB3_RUNS", "config", "dates", "params", "preamble", "BODY"]
