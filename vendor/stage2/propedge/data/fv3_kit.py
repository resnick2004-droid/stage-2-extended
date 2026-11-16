"""FV3's data-capture kits (T17 item 3; the card `docs/candidates/cards/drafts/FV3.md`): R117 to R136 re-walk ORB3's
three NQ windows (R102-R104, 2009-06 to June 2025, development data under D-237), R117 over 2009-06 to 2010 and the
rest one calendar year each to 2021 and half-years from 2020 and 2022 on -- R117 ran at sixteen orders a record,
R125 (2018) at thirty and R128 (2021) at thirty-three (the profiles step once per new tick, and NQ at today's
price moves many more ticks a session), so a two-year window, or a whole recent year, would brush QuantConnect's
10,000 orders (FV3's records are about three times FV2's: the profiles) -- and record what
JJ Simon's own rules, the component ledger and the mechanics report need (`propedge/outcomes/fv3_core.py`). No
hypothesis, nothing selected; only the day records leave (D-120).

FV2's kit (`propedge/data/fv2_kit.py`) re-pointed at FV3: ORB1's body with the named edits (the record call now
passes the trading day, for the release calendar), ORB3's preamble with the run's own window, prefix FV3; the embedded
cores as FV2's with fv3_core in place of fv2_core, the release-day bitmasks inside it.
"""
from __future__ import annotations

from datetime import date

from propedge.data import fv2_kit as kf
from propedge.data import orb3_kit as k3
from propedge.data import orb5_kit as k5
from propedge.data import orb6_kit as k6
from propedge.data import orb_kit as ok

FV3_PREFIX = "FV3"
MARKET = "NQ"
#: each run: the ORB3 run whose days it re-walks, and its warm-up, start and end
FV3_RUNS = {
    "R117-fv3-NQ-0910": ("R102-orb3-NQ-0914", "2009-04-20", "2009-06-01", "2010-12-31"),
    "R118-fv3-NQ-1111": ("R102-orb3-NQ-0914", "2010-11-15", "2011-01-01", "2011-12-31"),
    "R119-fv3-NQ-1212": ("R102-orb3-NQ-0914", "2011-11-12", "2012-01-01", "2012-12-31"),
    "R120-fv3-NQ-1313": ("R102-orb3-NQ-0914", "2012-11-15", "2013-01-01", "2013-12-31"),
    "R121-fv3-NQ-1414": ("R102-orb3-NQ-0914", "2013-11-12", "2014-01-01", "2014-12-31"),
    "R122-fv3-NQ-1515": ("R103-orb3-NQ-1519", "2014-11-15", "2015-01-01", "2015-12-31"),
    "R123-fv3-NQ-1616": ("R103-orb3-NQ-1519", "2015-11-12", "2016-01-01", "2016-12-31"),
    "R124-fv3-NQ-1717": ("R103-orb3-NQ-1519", "2016-11-15", "2017-01-01", "2017-12-31"),
    "R125-fv3-NQ-1818": ("R103-orb3-NQ-1519", "2017-11-12", "2018-01-01", "2018-12-31"),
    "R126-fv3-NQ-1919": ("R103-orb3-NQ-1519", "2018-11-15", "2019-01-01", "2019-12-31"),
    "R127-fv3-NQ-20H1": ("R104-orb3-NQ-2025", "2019-11-12", "2020-01-01", "2020-06-30"),
    "R133-fv3-NQ-20H2": ("R104-orb3-NQ-2025", "2020-05-18", "2020-07-01", "2020-12-31"),
    "R128-fv3-NQ-2121": ("R104-orb3-NQ-2025", "2020-11-15", "2021-01-01", "2021-12-31"),
    "R129-fv3-NQ-22H1": ("R104-orb3-NQ-2025", "2021-11-12", "2022-01-01", "2022-06-30"),
    "R134-fv3-NQ-22H2": ("R104-orb3-NQ-2025", "2022-05-16", "2022-07-01", "2022-12-31"),
    "R130-fv3-NQ-23H1": ("R104-orb3-NQ-2025", "2022-11-15", "2023-01-01", "2023-06-30"),
    "R135-fv3-NQ-23H2": ("R104-orb3-NQ-2025", "2023-05-15", "2023-07-01", "2023-12-31"),
    "R131-fv3-NQ-24H1": ("R104-orb3-NQ-2025", "2023-11-12", "2024-01-01", "2024-06-30"),
    "R136-fv3-NQ-24H2": ("R104-orb3-NQ-2025", "2024-05-13", "2024-07-01", "2024-12-31"),
    "R132-fv3-NQ-2525": ("R104-orb3-NQ-2025", "2024-11-15", "2025-01-01", "2025-06-30"),
}


def dates(run: str) -> tuple[date, date, date]:
    return tuple(date.fromisoformat(x) for x in FV3_RUNS[run][1:])


def params() -> dict:
    return k3.params()


def _cores() -> str:
    import inspect

    from propedge.outcomes import fv3_core, orb3_core, orb_core

    consts = (f"OR_START, OR_MIN, OR_MINS, PRE_START, NONE = {orb_core.OR_START!r}, {orb_core.OR_MIN!r}, "
              f"{orb_core.OR_MINS!r}, {orb_core.PRE_START!r}, {orb_core.NONE!r}\n"
              "FLAT_ENTRY = FLAT - 2\n")
    helpers = "\n\n".join(inspect.getsource(getattr(orb_core, f)) for f in k3._ORB_CORE_PARTS)
    return k6._no_docstrings(k5._no_comments(consts + "\n\n" + helpers + "\n\n" + inspect.getsource(orb3_core.passages)
                                             + "\n\n" + kf._orb5_parts() + "\n\n" + k5._strip(fv3_core)))


def preamble(run: str) -> str:
    orb3, _, start, end = FV3_RUNS[run]
    return _preamble(orb3, start, end)


def _preamble(orb3: str, start: str, end: str) -> str:
    """ORB3 run `orb3`'s preamble re-pointed at FV3 over `start`..`end`, the cores embedded (the development kits'
    preamble; FV3-C's confirmation kits add their 2026 release days after it, D-355)."""
    text = k3.preamble(orb3)
    head, sep, _ = text.partition("# ---------------------------------------------------------------- orb_core's")
    assert sep, "orb3_kit's preamble changed shape"
    _, w0, w1 = k3.dates(orb3)
    s0, s1 = date.fromisoformat(start), date.fromisoformat(end)
    for old, new in ((f'PREFIX = "{k3.ORB3_PREFIX}"', f'PREFIX = "{FV3_PREFIX}"'),
                     (f"WIN_START = ({w0.year}, {w0.month}, {w0.day})", f"WIN_START = ({s0.year}, {s0.month}, {s0.day})"),
                     (f"WIN_END = ({w1.year}, {w1.month}, {w1.day})", f"WIN_END = ({s1.year}, {s1.month}, {s1.day})"),
                     ("regime_core.py (its docstring removed)",
                      "regime_core.py (its docstring and what this kit never calls removed)")):
        assert head.count(old) == 1, old
        head = head.replace(old, new)
    return k6._drop_unused(head + "# ---------------------------------------------------------------- the embedded cores "
                           "(orb_core, orb3_core, orb5_core, fv3_core; no docstrings, imports, comments or uncalled "
                           "functions)\n" + _cores()
                           + "\n# ---------------------------------------------------------------- end of the embedded "
                           "cores\n", BODY)


_EDITS_FV3 = (
    ('''            rec = day_record(o, h, l, cl, vt, ls, PARAMS, hist)''',
     '''            rec = day_record_fv3(o, h, l, cl, vt, q, ls, PARAMS, hist, d["td"])   # FV3: his rules, the ledger'''),
    ('''    head = (PREFIX + "|HEAD|v=2|market=" + MARKET + "|days=" + str(self._n) + "|warm=" + str(self._warm)''',
     '''    head = (PREFIX + "|HEAD|v=1|market=" + MARKET + "|days=" + str(self._n) + "|warm=" + str(self._warm)'''),
    ('''                self._recs.append(encode_day(d["td"], rec))''',
     '''                self._recs.append(encode_day5(d["td"], rec))   # a -1 written as nothing (D-267)'''),
    k5._EDITS5[3],
)
BODY = ok.BODY
for _old, _new in _EDITS_FV3:
    assert BODY.count(_old) == 1, _old[:60]
    BODY = BODY.replace(_old, _new)
BODY = BODY.replace("# T15, D-249: ORB1's day records at actual prices, on the regime map's body",
                    "# T17, FV3: the capture records at actual prices, on ORB1's body")


# ------------------------------------------------------------------------------------------------ FV3-C's confirmation

#: D-355: FV3-C's one confirmation on NQ's held-back window -- the development kits' body and cores unchanged, one kit
#: per period of config/fv3_confirmation.yaml, the window its own; the ORB3 run whose preamble serves as the template is
#: the last development one (no ORB3 run reads the window, so nothing is joined: the ingest records why)
CONFIRM_CONFIG_PATH = "config/fv3_confirmation.yaml"
CONFIRM_TEMPLATE_ORB3 = "R104-orb3-NQ-2025"


def confirm_config(path=None) -> dict:
    """config/fv3_confirmation.yaml (D-355)."""
    from pathlib import Path

    import yaml

    from propedge import REPO_ROOT

    p = Path(path) if path is not None else REPO_ROOT / CONFIRM_CONFIG_PATH
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def confirm_runs(cfg: dict | None = None) -> dict[str, dict]:
    """{run id: the period's row} for every confirmation kit, in period order."""
    cfg = cfg or confirm_config()
    return {str(p["run"]): dict(p) for p in cfg["periods"]}


def confirm_dates(run: str, cfg: dict | None = None) -> tuple[date, date, date]:
    """(warm-up start, period start, period end) of a confirmation kit."""
    p = confirm_runs(cfg)[run]
    return tuple(date.fromisoformat(str(p[k])) for k in ("warm", "start", "end"))


def news_mask_2026(cfg: dict | None = None) -> int:
    """2026's BLS 08:30 ET release days as fv3_core.NEWS's bitmask (bit 0 the first of January), read from the
    confirmation config's `news_2026` file with the same rule scripts/make_fv3_news.py applies to 2009-2025."""
    import csv
    from pathlib import Path

    from propedge import REPO_ROOT

    cfg = cfg or confirm_config()
    path = REPO_ROOT / str(cfg["news_2026"])
    if not path.is_file():
        raise FileNotFoundError(f"{path}: 2026's BLS release days are not on record; the confirmation kits need them (D-355)")
    mask = 0
    with Path(path).open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            d = date.fromisoformat(r["date"])
            if d.year != 2026:
                raise ValueError(f"{path}: a date outside 2026 ({d})")
            mask |= 1 << (d - date(2026, 1, 1)).days
    if not mask:
        raise ValueError(f"{path}: no release day")
    return mask


def confirm_preamble(run: str, cfg: dict | None = None) -> str:
    """The development preamble over the period's dates, then 2026's release days added to the embedded table: the
    cores stay byte-identical to the twenty development kits' (fv3_core.NEWS ends at 2025)."""
    cfg = cfg or confirm_config()
    _, start, end = confirm_dates(run, cfg)
    return (_preamble(CONFIRM_TEMPLATE_ORB3, start.isoformat(), end.isoformat())
            + "# D-355: 2026's BLS 08:30 ET release days (" + str(cfg["news_2026"]) + "), after the cores\n"
            + f"NEWS[2026] = 0x{news_mask_2026(cfg):x}\n")


__all__ = ["FV3_PREFIX", "MARKET", "FV3_RUNS", "dates", "params", "preamble", "BODY", "CONFIRM_CONFIG_PATH",
           "CONFIRM_TEMPLATE_ORB3", "confirm_config", "confirm_runs", "confirm_dates", "news_mask_2026", "confirm_preamble"]
