"""Read the files a person downloads from a manual run into result tables (D-82).

Each parser refuses a run whose output is incomplete: a missing `END` line, a truncated summary,
or a missing symbol. An incomplete run is a fix-and-rerun round, not a partial result.

The **Logs** format is fixed by our own algorithms (`qc_algorithms.py`). The **Download Results**
JSON is QuantConnect's; its exact layout has not yet been seen from a real run, so
`orders_from_results` searches for the orders leniently and raises plainly if it finds none.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pandas as pd

from propedge.data import qc_algorithms as alg


class UnusableRun(ValueError):
    """The downloads do not contain a complete output. Count it as a fix-and-rerun round."""


def prefixed_lines(log_path: Path, prefix: str) -> list[str]:
    """Our summary lines, with LEAN's timestamp prefix removed."""
    out = []
    for raw in Path(log_path).read_text(encoding="utf-8", errors="replace").splitlines():
        i = raw.find(prefix + "|")
        if i >= 0:
            out.append(raw[i:].strip())
    return out


def _kv(parts: list[str]) -> dict[str, str]:
    return dict(p.split("=", 1) for p in parts if "=" in p)


# ------------------------------------------------------------------ R001 dataset checks

def _read_dataset_summary(log_path: Path, symbols) -> tuple[list, dict, dict]:
    """The rows, HEAD fields and per-symbol fields of a DSCHK summary, refusing an incomplete one."""
    lines = prefixed_lines(log_path, alg.DATASET_PREFIX)
    end = [l for l in lines if l.startswith(alg.DATASET_PREFIX + "|END|")]
    if not end:
        raise UnusableRun("no END line in the logs: the run did not finish its summary.")
    endkv = _kv(end[-1].split("|")[2:])
    if endkv.get("truncated") != "false":
        raise UnusableRun(f"the summary was truncated ({end[-1]}).")

    rows, head, syms, rolls = [], {}, {}, {}
    for line in lines:
        parts = line.split("|")
        kind = parts[1]
        if kind == "HEAD":
            head = _kv(parts[2:])
            rows += [dict(kind="HEAD", symbol="", field=k, value=v) for k, v in head.items()]
        elif kind == "SYM":
            kv = _kv(parts[3:])
            syms[parts[2]] = kv
            rows += [dict(kind="SYM", symbol=parts[2], field=k, value=v) for k, v in kv.items()]
        elif kind == "ROLL":
            n = _kv(parts[3:4]).get("n", "0")
            events = [e for e in (parts[4] if len(parts) > 4 else "").split(",") if e]
            rolls[parts[2]] = events
            rows.append(dict(kind="ROLL", symbol=parts[2], field="n", value=n))
            rows += [dict(kind="ROLL", symbol=parts[2], field="event", value=e) for e in events]
    missing = [s for s in ("SPY", *symbols) if s not in syms]
    if missing:
        raise UnusableRun(f"no SYM line for {missing}.")
    return rows, head, syms


def _present(kv) -> str:
    return "yes" if int(kv.get("bars", "0")) > 0 else "no data received"


def _start(kv, start) -> str:
    first = kv.get("first", "None")
    if first in ("None", ""):
        return "no data received"
    d = first[:10]
    return f"on or before {start.isoformat()}" if d <= start.isoformat() else d


def parse_dataset_checks(log_path: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Returns (long table of every reported field, facts keyed as in data_sources.yaml)."""
    rows, head, syms = _read_dataset_summary(log_path, alg.DATASET_FUTURES)
    facts: dict[str, Any] = {"equities_spy_present": _present(syms["SPY"])}
    for t in alg.DATASET_FUTURES:
        kv, key = syms[t], t.lower()
        facts[f"futures_present_{key}"] = _present(kv)
        facts[f"futures_start_{key}"] = _start(kv, alg.DATASET_START)
    applied = sorted({kv.get("config", "") for t, kv in syms.items() if t != "SPY"})
    facts["futures_roll_rule"] = (f"defaults {head.get('defaults', '?')}; applied "
                                  f"{' | '.join(applied)}")
    # Judged on the symbols that received bars: a symbol with none has no period, which says
    # nothing about resolution (D-89; R001 recorded false for exactly that reason).
    periods = {t: kv.get("period") for t, kv in syms.items() if _present(kv) == "yes"}
    # Python prints a one-minute timedelta as 0:01:00; .NET as 00:01:00. Accept either.
    facts["resolution_minute"] = bool(periods) and all(
        p in ("0:01:00", "00:01:00") for p in periods.values())
    return pd.DataFrame(rows, columns=["kind", "symbol", "field", "value"]), facts


def coverage_fact_suffix() -> str:
    return f"_{alg.COVERAGE_START.year}_{alg.COVERAGE_END.year}"


def parse_coverage_checks(log_path: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    """R005: were GC and HG bars received anywhere in the rest of the development period?

    The ES control must have received bars. If it did not, the run shows that nothing arrived,
    not that GC or HG are missing, so it is refused as unusable.
    """
    rows, _head, syms = _read_dataset_summary(log_path, alg.COVERAGE_FUTURES)
    if _present(syms[alg.COVERAGE_CONTROL]) != "yes":
        raise UnusableRun(f"the control {alg.COVERAGE_CONTROL} received no bars, so the run "
                          "cannot tell a missing contract from a run that read nothing.")
    sfx = coverage_fact_suffix()
    facts: dict[str, Any] = {}
    for t in alg.COVERAGE_TARGETS:
        facts[f"futures_present_{t.lower()}{sfx}"] = _present(syms[t])
        facts[f"futures_start_{t.lower()}{sfx}"] = _start(syms[t], alg.COVERAGE_START)
    return pd.DataFrame(rows, columns=["kind", "symbol", "field", "value"]), facts


# ------------------------------------------------------------------ R036-R037 extra datasets (D-127)

def _read_extras(log_path: Path, prefix: str, keys) -> tuple[pd.DataFrame, dict, dict, list]:
    """The rows, first dates, per-year counts and notes of a DXT/DXO summary, refusing an incomplete one."""
    lines = prefixed_lines(log_path, prefix)
    end = [l for l in lines if l.startswith(prefix + "|END|")]
    if not end:
        raise UnusableRun("no END line in the logs: the run did not finish its summary.")
    if _kv(end[-1].split("|")[2:]).get("truncated") != "false":
        raise UnusableRun(f"the summary was truncated ({end[-1]}).")
    rows, first, counts, notes = [], {}, {}, []
    for line in lines:
        parts = line.split("|")
        kind = parts[1]
        if kind == "HEAD":
            rows += [dict(kind="HEAD", set="", year="", field=k, value=v) for k, v in _kv(parts[2:]).items()]
        elif kind == "SET":
            first[parts[2]] = _kv(parts[3:]).get("first", "None")
            rows.append(dict(kind="SET", set=parts[2], year="", field="first", value=first[parts[2]]))
        elif kind == "Y":
            k, y = parts[2], int(parts[3])
            kv = {f: int(v) for f, v in _kv(parts[4:]).items()}
            counts.setdefault(k, {})[y] = kv
            rows += [dict(kind="Y", set=k, year=str(y), field=f, value=str(v)) for f, v in kv.items()]
        elif kind == "NOTE":
            notes.append("|".join(parts[2:]))
            rows.append(dict(kind="NOTE", set="", year="", field="note", value=notes[-1]))
    missing = [k for k in keys if k not in first]
    if missing:
        raise UnusableRun(f"no SET line for {missing}.")
    return pd.DataFrame(rows, columns=["kind", "set", "year", "field", "value"]), first, counts, notes


def _years(counts: dict, k: str, field: str) -> str:
    """The years in which `field` was counted at least once, or "no data received"."""
    ys = sorted(y for y, c in counts.get(k, {}).items() if c.get(field, 0) > 0)
    return ",".join(str(y) for y in ys) if ys else "no data received"


def _total(counts: dict, k: str, field: str) -> int:
    return sum(c.get(field, 0) for c in counts.get(k, {}).values())


def _first_text(first: dict, k: str, start) -> str:
    f = str(first.get(k, "None"))
    if f in ("None", ""):
        return "no data received"
    return f"on or before {start.isoformat()}" if f[:10] <= start.isoformat() else f[:10]


def parse_extras(log_path: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    """R036: futures quote bars, VIX futures and index values; facts keyed as in data_sources.yaml.

    ES trade bars are the control: a run in which ES received none read nothing and is refused.
    """
    keys = (*alg.EXTRAS_FUTURES, *alg.EXTRAS_INDICES)
    df, first, counts, _notes = _read_extras(log_path, alg.EXTRAS_PREFIX, keys)
    if _total(counts, alg.EXTRAS_CONTROL, "tb") == 0:
        raise UnusableRun(f"the control {alg.EXTRAS_CONTROL} received no trade bars, so the run cannot tell a "
                          "missing dataset from a run that read nothing.")
    facts: dict[str, Any] = {}
    for k in alg.EXTRAS_SPREAD_SETS:
        facts[f"futures_quotes_{k}"] = _years(counts, k, "qok")
        facts[f"futures_quote_sizes_{k}"] = _years(counts, k, "qsz")
    facts["futures_minute_vx"] = _years(counts, "vx", "tb")
    facts["futures_start_vx"] = _first_text(first, "vx", alg.EXTRAS_START)
    for k in alg.EXTRAS_INDICES:
        facts[f"index_minute_{k}"] = _years(counts, k, "tb")
        facts[f"index_daily_{k}"] = _years(counts, k, "day")
    return df, facts


def extras_fact_keys() -> tuple[str, ...]:
    """Every fact R036 and R037 answer (their slots in config/data_sources.yaml)."""
    keys = [f"futures_{w}_{k}" for k in alg.EXTRAS_SPREAD_SETS for w in ("quotes", "quote_sizes")]
    keys += ["futures_minute_vx", "futures_start_vx"]
    keys += [f"index_{w}_{k}" for k in alg.EXTRAS_INDICES for w in ("minute", "daily")]
    keys += [f"options_{w}_{k}" for k in alg.OPTIONS_SETS for w in ("chains", "start", "fields")]
    return tuple(keys)


def _share_word(num: int, den: int) -> str:
    """"most" at half or more of the contracts observed, "some" below that, "none" at zero."""
    if den == 0 or num == 0:
        return "none"
    return "most" if num / den >= 0.5 else "some"


def parse_options(log_path: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    """R037: option chains and their fields; facts keyed as in data_sources.yaml.

    The ES underlying's daily bars are the control: without them the run read nothing.
    """
    df, first, counts, _notes = _read_extras(log_path, alg.OPTIONS_PREFIX, alg.OPTIONS_SETS)
    if _total(counts, alg.OPTIONS_CONTROL, "u") == 0:
        raise UnusableRun(f"the control, the {alg.OPTIONS_CONTROL} underlying, received no bars, so the run "
                          "cannot tell a missing dataset from a run that read nothing.")
    facts: dict[str, Any] = {}
    for k in alg.OPTIONS_SETS:
        facts[f"options_chains_{k}"] = _years(counts, k, "days")
        facts[f"options_start_{k}"] = _first_text(first, k, alg.OPTIONS_START)
        seen = _total(counts, k, "k")
        facts[f"options_fields_{k}"] = ("no data received" if seen == 0 else
                                        ";".join(f"{name}={_share_word(_total(counts, k, f), seen)}"
                                                 for f, name in alg.OPTIONS_FIELDS.items()))
    return df, facts


# ------------------------------------------------------------------ R002-R004 reconciliation

def orders_from_results(results_path: Path) -> list[dict]:
    """Every order object in a Download Results JSON, wherever it sits."""
    doc = json.loads(Path(results_path).read_text(encoding="utf-8"))
    found: list[dict] = []

    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k.lower() == "orders" and isinstance(v, (dict, list)):
                    items = v.values() if isinstance(v, dict) else v
                    found.extend(o for o in items if isinstance(o, dict))
                else:
                    walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(doc)
    if not found:
        raise UnusableRun(f"no orders found in {Path(results_path).name}.")
    return found


def _tag(order: dict) -> str:
    return str(order.get("Tag") or order.get("tag") or "")


_PREV = re.compile(r"\|prev=(.*)$")


def trade_record(prev: str) -> dict[str, str]:
    """`12;c=ES ...;ent=...;...` -> {'n': '12', 'c': ..., 'ent': ...}."""
    first, *rest = prev.split(";")
    rec = {"n": first}
    rec.update(_kv(rest))
    return rec


def parse_reconciliation(log_path: Path, results_path: Path) -> tuple[pd.DataFrame, dict]:
    lines = prefixed_lines(log_path, alg.RECON_PREFIX)
    if not any(l.startswith(alg.RECON_PREFIX + "|END|") for l in lines):
        raise UnusableRun("no END line in the logs: the run did not finish its summary.")
    head = next((_kv(l.split("|")[2:]) for l in lines if l.startswith(alg.RECON_PREFIX + "|HEAD|")),
                {})
    recs, refs = [], {}
    for o in orders_from_results(results_path):
        tag = _tag(o)
        if tag.startswith("E|"):                    # E|n=12|ref=1650.25[|prev=...]
            kv = _kv(tag.split("|prev=")[0].split("|")[1:])
            if "n" in kv and "ref" in kv:
                refs[kv["n"]] = kv["ref"]
        m = _PREV.search(tag)
        if m:
            recs.append(trade_record(m.group(1)))
    last = next((l for l in lines if l.startswith(alg.RECON_PREFIX + "|LAST")), "")
    m = _PREV.search(last)
    if m:
        recs.append(trade_record(m.group(1)))
    if not recs:
        raise UnusableRun("no per-trade records in the order tags or the LAST line.")
    for r in recs:
        r["ref"] = refs.get(r["n"], "")
    if any(not r["ref"] for r in recs):
        raise UnusableRun("an entry order's tag has no intended price (ref=) for some trade.")
    df = pd.DataFrame(recs).drop_duplicates(subset="n")
    df["n"] = df["n"].astype(int)
    df = df.sort_values("n").reset_index(drop=True)
    trades = int(head.get("trades", "0"))
    if len(df) != trades:
        raise UnusableRun(f"{len(df)} trade records but HEAD reports {trades} trades.")
    return df, {"mode": head.get("mode"), "trades": trades, "exits": head.get("exits")}


# ------------------------------------------------------------------ R009-R012 C-007 leg evidence (D-97)

_REC = re.compile(r"\|rec=(.*?)(?:\||$)")
_RECS = re.compile(r"\|rec=([^|]*)")
_LEG_NUMERIC = ("ps", "e", "x", "h", "l", "rvp", "rvw", "g")


def _gap_bars(day: dict, b1: str, b2: str) -> list[dict]:
    """Decode a day's two bar strings into price rows; refuse a truncated string."""
    slots = b1.split(",") + b2.split(",")
    if len(slots) != alg.GAP_SLOTS:
        raise UnusableRun(f"day {day['n']} ({day['d']}): {len(slots)} bar slots, expected "
                          f"{alg.GAP_SLOTS}; an order tag was cut short.")
    base, tick = float(day["b"]), alg.GAP_TICK
    rows = []
    for i, s in enumerate(slots):
        if not s:
            continue
        f = s.split(".")
        if len(f) != 4 or not all(re.fullmatch(r"-?\d+", x) for x in f):
            raise UnusableRun(f"day {day['n']} ({day['d']}): bar slot {i} is malformed ({s!r}).")
        o = base + int(f[0]) * tick
        rows.append({"n": int(day["n"]), "d": day["d"], "sym": day["c"], "ps": float(day["ps"]),
                     "pst": day["pst"], "sk": day["sk"], "base": base, "nb": int(day["nb"]),
                     "lt": day["lt"], "t": alg.gap_slot_hhmm(i), "o": o, "h": o + int(f[1]) * tick,
                     "l": o - int(f[2]) * tick, "c": o + int(f[3]) * tick})
    if len(rows) != int(day["nb"]):
        raise UnusableRun(f"day {day['n']} ({day['d']}): {len(rows)} bars decoded but the record "
                          f"says {day['nb']}.")
    return rows


def openrev_cell(idx: int, n_variants: int = 6) -> dict:
    """Invert qc_algorithms' cell_index: ((fill*2 + scale)*2 + kind)*n_variants + variant."""
    variant = idx % n_variants
    rest = idx // n_variants
    kind, rest = rest % 2, rest // 2
    scale, fill = rest % 2, rest // 2
    return {"fill": ("close", "next_open")[fill], "scale": ("actual", "P_ref_4000")[scale],
            "entry": ("baseline", "structural")[kind], "variant_i": variant}


def parse_openrev_rescore(log_path: Path, results_path: Path,
                          prefix: str | None = None) -> tuple[pd.DataFrame, dict]:
    """R028 (D-122): one row per day header (cell = -1) and one per scored cell, from the order tags.

    Cell values are u in units of intended risk: zero-cost real (zr), zero-cost mirror (zm), full
    cost real (fu); `k` is the zero-cost real exit kind (t/s/g/m) and `f` the full-cost floor flag.
    """
    prefix = prefix or alg.OPENREV_PREFIX
    lines = prefixed_lines(log_path, prefix)
    if not any(l.startswith(prefix + "|END|") for l in lines):
        raise UnusableRun("no END line in the logs: the run did not finish its summary.")
    head = next((_kv(l.split("|")[2:]) for l in lines if l.startswith(prefix + "|HEAD|")), {})
    if head.get("open") == "1":
        raise UnusableRun("the run ended inside a recording window; the last day was not scored.")
    parts: dict[int, dict[int, dict]] = {}
    for tag in (_tag(o) for o in orders_from_results(results_path)):
        for m in _RECS.finditer(tag):
            rec = trade_record(m.group(1))
            if "k" not in rec:
                continue
            parts.setdefault(int(rec["n"]), {})[int(rec["k"])] = rec
    days = int(head.get("days", "0"))
    if sorted(parts) != list(range(1, days + 1)):
        raise UnusableRun(f"{len(parts)} day records but HEAD reports {days} days, or a record is missing.")
    rows: list[dict] = []
    for n in sorted(parts):
        chunks = parts[n]
        first = chunks.get(0)
        if first is None or sorted(chunks) != list(range(int(first["K"]))):
            raise UnusableRun(f"day {n}: {len(chunks)} of {first['K'] if first else '?'} tag chunks present.")
        meta = {"n": n, "d": first["d"], "sym": first["c"], "ps": float(first["ps"]), "pst": first["pst"],
                "sk": first["sk"], "nb": int(first["nb"]), "lt": first["lt"], "has_open": first["op"] == "1"}
        for key, col in (("bad", "bad"), ("r0", "r0"), ("rp", "rp"), ("ex", "x"), ("y30", "y30"),
                         ("y45", "y45"), ("y60", "y60")):              # R029 (D-124) per-day measures
            if key in first:
                meta[col] = float(first[key]) if first[key] != "" else float("nan")
        rows.append({**meta, "cell": -1})
        for k in range(int(first["K"])):
            for s in filter(None, chunks[k].get("x", "").split("/")):
                idx, vals = s.split(":")
                zr, zm, fu, kf = vals.split(",")
                num = lambda x: float(x) if x else float("nan")   # noqa: E731
                rows.append({**meta, "cell": int(idx), **openrev_cell(int(idx)), "zr": num(zr), "zm": num(zm),
                             "fu": num(fu), "k": kf[:1] if kf and kf[0] in "tsgm" else "",
                             "floor_bound": kf[-1] == "1" if kf and kf[-1] in "01" else None})
    df = pd.DataFrame(rows)
    return df, {"market": head.get("market"), "days": days, "full": int(head.get("full", "0")),
                "skips": head.get("skips"), "switches": int(head.get("switches", "0")),
                "orders": int(head.get("orders", "0"))}


def atlas_output_matches_kit(log_path: Path, results_path: Path, market: str, version: int = 1) -> None:
    """D-131's structural check for an attested run: HEAD names the kit's market and (D-133) the kit's version,
    and every day's tag carries exactly the committed kit's fields, in its order. Raises UnusableRun otherwise."""
    lines = prefixed_lines(log_path, alg.ATLAS_PREFIX)
    head = next((_kv(l.split("|")[2:]) for l in lines if l.startswith(alg.ATLAS_PREFIX + "|HEAD|")), {})
    if head.get("market") != market:
        raise UnusableRun(f"HEAD names market {head.get('market')!r}; the kit is {market!r}.")
    if head.get("v") != str(version):
        raise UnusableRun(f"HEAD reports kit version {head.get('v')!r}; the committed kit is version {version}: "
                          "a different algorithm ran.")
    want = ["d", "c", "ps", "pst", "sk", *alg._ATLAS_KEYS]
    n = 0
    for tag in (_tag(o) for o in orders_from_results(results_path)):
        for m in _RECS.finditer(tag):
            first, *rest = m.group(1).split(";")
            keys = [p.split("=", 1)[0] for p in rest]
            if keys != want:
                raise UnusableRun(f"day record {first} carries fields {keys[:6]}...; the committed kit writes "
                                  f"{want[:6]}... ({len(want)} fields): a different algorithm ran.")
            n += 1
    if n == 0:
        raise UnusableRun("no day records to check.")


def parse_atlas(log_path: Path, results_path: Path) -> tuple[pd.DataFrame, dict]:
    """R030-R035 (D-126): one row per recorded day of per-day measurements, from the order tags."""
    lines = prefixed_lines(log_path, alg.ATLAS_PREFIX)
    if not any(l.startswith(alg.ATLAS_PREFIX + "|END|") for l in lines):
        raise UnusableRun("no END line in the logs: the run did not finish its summary.")
    head = next((_kv(l.split("|")[2:]) for l in lines if l.startswith(alg.ATLAS_PREFIX + "|HEAD|")), {})
    recs: dict[int, dict] = {}
    for tag in (_tag(o) for o in orders_from_results(results_path)):
        for m in _RECS.finditer(tag):
            rec = trade_record(m.group(1))
            recs.setdefault(int(rec["n"]), rec)
    days = int(head.get("days", "0"))
    expect = days - (1 if head.get("open") == "1" else 0)          # a day still open at the end is not emitted
    if sorted(recs) != list(range(1, expect + 1)):
        raise UnusableRun(f"{len(recs)} day records but HEAD implies {expect}, or a record is missing.")
    rows = []
    for n in sorted(recs):
        r = recs[n]
        row = {"n": n, "d": r["d"], "sym": r["c"], "ps": float(r["ps"]), "pst": r["pst"], "sk": r["sk"]}
        for k in alg._ATLAS_KEYS:
            v = r.get(k, "")
            row[k] = float(v) if v != "" else float("nan")
        rows.append(row)
    return pd.DataFrame(rows), {"market": head.get("market"), "days": days,
                                "settled": int(head.get("settled", "0")), "skips": head.get("skips"),
                                "switches": int(head.get("switches", "0"))}


def parse_context(log_path: Path, results_path: Path) -> tuple[pd.DataFrame, dict]:
    """R038 (D-128): one row per session -- the VIX close and the SPX (gs) and NDX (gn) net gamma exposure."""
    p = alg.CONTEXT_PREFIX
    lines = prefixed_lines(log_path, p)
    if not any(l.startswith(p + "|END|") for l in lines):
        raise UnusableRun("no END line in the logs: the run did not finish its summary.")
    head = next((_kv(l.split("|")[2:]) for l in lines if l.startswith(p + "|HEAD|")), {})
    sources = [_tag(o) for o in orders_from_results(results_path)] + [l for l in lines if l.startswith(p + "|LAST")]
    recs: dict[int, dict] = {}
    for s in sources:
        for m in _RECS.finditer(s):
            rec = trade_record(m.group(1))
            recs.setdefault(int(rec["n"]), rec)
    sessions = int(head.get("sessions", "0"))
    if sessions == 0 or sorted(recs) != list(range(1, sessions + 1)):
        raise UnusableRun(f"{len(recs)} session records but HEAD reports {sessions}, or a record is missing.")
    rows = []
    for n in sorted(recs):
        r = recs[n]
        row = {"n": n, "d": r["d"]}
        for k in alg.CONTEXT_KEYS_V2:                    # version 1 records lack gsu/gnu: those stay NaN
            v = r.get(k, "")
            row[k] = float(v) if v != "" else float("nan")
        rows.append(row)
    return pd.DataFrame(rows), {"sessions": sessions, "vix": int(head.get("vix", "0")),
                                "gs": int(head.get("gs", "0")), "gn": int(head.get("gn", "0")),
                                "agree_gs": head.get("agree_gs"), "agree_gn": head.get("agree_gn"),
                                "und_gs": head.get("und_gs"), "und_gn": head.get("und_gn"),
                                "late": head.get("late"), "notes": int(head.get("notes", "0"))}


_FV_FAM = {"0": "atr_bands", "1": "structural"}
_FV_SCALE = {"0": "p_ref", "1": "actual"}
_FV_SESS = {"a": "am", "p": "pm"}
_FV_TAG = {"c": "cont", "r": "rev", "k": "recont"}


def parse_fv(log_path: Path, results_path: Path) -> tuple[pd.DataFrame, dict]:
    """R045-R046 (D-142): one row per day (kind 'day': integrity and the scaling reference) and one per trade
    (kind 'trade'), from the order tags. Refuses a missing day or a missing chunk of a day."""
    p = alg.FV_PREFIX
    lines = prefixed_lines(log_path, p)
    if not any(l.startswith(p + "|END|") for l in lines):
        raise UnusableRun("no END line in the logs: the run did not finish its summary.")
    head = next((_kv(l.split("|")[2:]) for l in lines if l.startswith(p + "|HEAD|")), {})
    parts: dict[int, dict[int, dict]] = {}
    for tag in (_tag(o) for o in orders_from_results(results_path)):
        for m in _RECS.finditer(tag):
            first, *rest = m.group(1).split(";")
            rec = {"n": first, **_kv(rest)}
            if "k" in rec:
                parts.setdefault(int(rec["n"]), {})[int(rec["k"])] = rec
    days = int(head.get("days", "0")) - (1 if head.get("open") == "1" else 0)
    if sorted(parts) != list(range(1, days + 1)):
        raise UnusableRun(f"{len(parts)} day records but HEAD implies {days}, or a record is missing.")
    rows: list[dict] = []
    num = lambda x: float(x) if x not in ("", None) else float("nan")          # noqa: E731
    for n in sorted(parts):
        ch = parts[n]
        first = ch.get(0)
        if first is None or sorted(ch) != list(range(int(first["K"]))):
            raise UnusableRun(f"day {n}: {len(ch)} of {first['K'] if first else '?'} tag chunks present.")
        meta = {"n": n, "d": first["d"], "sym": first["c"], "ref": num(first["ref"]), "sk": first["sk"],
                "st": int(first["st"]), "bad": int(first["bad"]), "cov": num(first["cov"]), "r0": num(first["r0"]),
                "rp": num(first["rp"])}
        rows.append({**meta, "kind": "day"})
        for k in range(int(first["K"])):
            for code in filter(None, ch[k].get("x", "").split("/")):
                f = code.split(",")
                if len(f) != 11 or len(f[0]) != 5:
                    raise UnusableRun(f"day {n}: malformed trade record {code!r}.")
                h5 = f[0]
                rows.append({"n": n, "d": meta["d"], "sym": meta["sym"], "kind": "trade",
                             "family": _FV_FAM[h5[0]], "scale": _FV_SCALE[h5[1]], "session": _FV_SESS[h5[2]],
                             "tag": _FV_TAG[h5[3]], "side": 1 if h5[4] == "+" else -1, "t": int(f[1]),
                             "j0": int(f[2]), "j_exit": int(f[3]), "stop_ticks": int(f[4]), "exit_kind": f[5],
                             "r_net": float(f[6]), "r_price": float(f[7]), "mfe": float(f[8]), "mae": float(f[9]),
                             "band": int(f[10])})
    df = pd.DataFrame(rows)
    trades = int((df["kind"] == "trade").sum()) if len(df) else 0
    if trades != int(head.get("trades", "0")):
        raise UnusableRun(f"{trades} trade records but HEAD reports {head.get('trades')}.")
    return df, {"market": head.get("market"), "days": days, "trades": trades,
                "settled": int(head.get("settled", "0")), "switches": int(head.get("switches", "0")),
                "lost": int(head.get("lost", "0")), "late": int(head.get("late", "0")), "skips": head.get("skips")}


def fv_output_matches_kit(log_path: Path, market: str) -> None:
    """D-131-style check for an attested FV1 run: HEAD names the kit's market and version; the parser then refuses
    any day record or trade record that does not carry exactly the kit's fields."""
    lines = prefixed_lines(log_path, alg.FV_PREFIX)
    head = next((_kv(l.split("|")[2:]) for l in lines if l.startswith(alg.FV_PREFIX + "|HEAD|")), {})
    if head.get("market") != market or head.get("v") != "1":
        raise UnusableRun(f"HEAD {head} does not match the committed FV1 kit for {market}: a different algorithm ran.")


def parse_bmap(log_path: Path, results_path: Path) -> tuple[pd.DataFrame, dict]:
    """R049-R052 (D-149): one row per day (kind 'day': integrity, D, stop ticks per width, the gap and close-location
    buckets) and one per decision and side (kind 'entry': the time, the four feature buckets, and per stop width wi
    mfe{wi} / hit{wi} / exit{wi} in R, from hundredths). Refuses a missing day, a missing chunk or a malformed record."""
    p = alg.BMAP_PREFIX
    lines = prefixed_lines(log_path, p)
    if not any(l.startswith(p + "|END|") for l in lines):
        raise UnusableRun("no END line in the logs: the run did not finish its summary.")
    head = next((_kv(l.split("|")[2:]) for l in lines if l.startswith(p + "|HEAD|")), {})
    parts: dict[int, dict[int, dict]] = {}
    for tag in (_tag(o) for o in orders_from_results(results_path)):
        for m in _RECS.finditer(tag):
            first, *rest = m.group(1).split(";")
            rec = {"n": first, **_kv(rest)}
            if "k" in rec:
                parts.setdefault(int(rec["n"]), {})[int(rec["k"])] = rec
    days = int(head.get("days", "0"))              # the kit counts a day only when it closes and emits it
    if sorted(parts) != list(range(1, days + 1)):
        raise UnusableRun(f"{len(parts)} day records but HEAD implies {days}, or a record is missing.")
    num = lambda x: float(x) if x not in ("", None) else float("nan")          # noqa: E731
    times = alg.bmap_params(head.get("market") or "NQ")["p"]["times"]
    rows: list[dict] = []
    entries = 0
    for n in sorted(parts):
        ch = parts[n]
        first = ch.get(0)
        if first is None or sorted(ch) != list(range(int(first["K"]))):
            raise UnusableRun(f"day {n}: {len(ch)} of {first['K'] if first else '?'} tag chunks present.")
        sk = [int(x) for x in first["sk"].split(",")] if first.get("sk") else []
        meta = {"n": n, "d": first["d"], "sym": first["c"], "sk0": first["sk0"], "st": int(first["st"]),
                "bad": int(first["bad"]), "cov": num(first["cov"]), "D": num(first["D"]), "gap": int(first["g"]),
                "clv": int(first["pc"])}
        meta.update({f"stop_ticks{wi}": s for wi, s in enumerate(sk)})
        rows.append({**meta, "kind": "day"})
        for k in range(int(first["K"])):
            for code in filter(None, ch[k].get("x", "").split("/")):
                key, _, body = code.partition("=")
                sides = body.split("~")
                if len(key) != 5 or key[0] not in alg.BMAP_TIME_CODES or len(sides) != 2:
                    raise UnusableRun(f"day {n}: malformed decision record {code!r}.")
                t = times[alg.BMAP_TIME_CODES.index(key[0])]
                for side, s in zip((1, -1), sides):
                    row = {"n": n, "d": meta["d"], "kind": "entry", "t": t, "side": side,
                           "f_fv": int(key[1]), "f_vwap": int(key[2]), "f_last30": int(key[3]), "f_range": int(key[4])}
                    for wi, rec in enumerate(s.split(",")):
                        if rec == "-":
                            row.update({f"mfe{wi}": float("nan"), f"hit{wi}": -1, f"exit{wi}": float("nan")})
                            continue
                        f = rec.split(":")
                        if len(f) != 3:
                            raise UnusableRun(f"day {n}: malformed entry record {rec!r}.")
                        row.update({f"mfe{wi}": int(f[0]) / 100.0, f"hit{wi}": int(f[1]), f"exit{wi}": int(f[2]) / 100.0})
                        entries += 1
                    rows.append(row)
    if entries != int(head.get("entries", "-1")):
        raise UnusableRun(f"{entries} entry records but HEAD reports {head.get('entries')}.")
    return pd.DataFrame(rows), {"market": head.get("market"), "days": days, "entries": entries,
                                "settled": int(head.get("settled", "0")), "switches": int(head.get("switches", "0")),
                                "lost": int(head.get("lost", "0")), "late": int(head.get("late", "0")),
                                "warm": int(head.get("warm", "0")), "skips": head.get("skips")}


def bmap_output_matches_kit(log_path: Path, market: str) -> None:
    """D-131-style check for an attested bracket-map run: HEAD names the kit's market and version; the parser then
    refuses any record that does not carry exactly the kit's fields."""
    lines = prefixed_lines(log_path, alg.BMAP_PREFIX)
    head = next((_kv(l.split("|")[2:]) for l in lines if l.startswith(alg.BMAP_PREFIX + "|HEAD|")), {})
    if head.get("market") != market or head.get("v") != "1":
        raise UnusableRun(f"HEAD {head} does not match the committed bracket-map kit for {market}.")


def _im2_walk(s: str, rr: list[int], scale: str, n: int) -> dict:
    """One walk of an IM2 entry: '-' (the entry was through its stop at this scale) or 'dist,k12:r:m,...' per R."""
    nan = float("nan")
    out: dict[str, Any] = {f"dist_{scale}": nan}
    for R in rr:
        out.update({f"kind{R}_{scale}": "", f"j{R}_{scale}": -1, f"r{R}_{scale}": nan, f"mae{R}_{scale}": nan})
    if s == "-":
        return out
    f = s.split(",")
    if len(f) != 1 + len(rr):
        raise UnusableRun(f"session {n}: malformed IM2 walk {s!r}.")
    out[f"dist_{scale}"] = float(f[0])
    for R, x in zip(rr, f[1:]):
        g = x.split(":")
        if len(g) != 3 or not g[0] or g[0][0] not in "tsgm":
            raise UnusableRun(f"session {n}: malformed IM2 bracket {x!r}.")
        out.update({f"kind{R}_{scale}": g[0][0], f"j{R}_{scale}": int(g[0][1:]), f"r{R}_{scale}": float(g[1]),
                    f"mae{R}_{scale}": float(g[2])})
    return out


def parse_im2(log_path: Path, results_path: Path) -> tuple[pd.DataFrame, dict]:
    """R053-R060 (P-04): one row per session (kind 'day': calendar status, skip reason, integrity, the open and prior
    close, the lookback's depth, the day's counts and its release minutes CT, `rel`) and one per entry (kind 'entry':
    side, decision and entry slots, the decision close, bands, VWAP and the lowest price while held, `mn`, at actual
    prices; per scale -- `_p` the reference price, `_a` actual -- the stop distance and per R the exit kind, exit slot,
    R after the fills' ticks and MAE). Refuses a missing session, a missing chunk, a record without exactly the kit's
    fields, a malformed entry, counts that disagree with the session's or HEAD's, or a HEAD showing the exchange
    calendar was not read. Records the LEAN version the run reports (P-04 §3)."""
    p = alg.IM2_PREFIX
    lines = prefixed_lines(log_path, p)
    if not any(l.startswith(p + "|END|") for l in lines):
        raise UnusableRun("no END line in the logs: the run did not finish its summary.")
    head = next((_kv(l.split("|")[2:]) for l in lines if l.startswith(p + "|HEAD|")), {})
    market = head.get("market")
    if market not in alg.IM2_MARKETS:
        raise UnusableRun(f"HEAD names market {market!r}, not one of IM2's.")
    missing_head = [k for k in _IM2_HEAD_FIELDS if k not in head]
    if missing_head:
        raise UnusableRun(f"HEAD lacks {missing_head}: not the committed IM2 kit's output.")
    if head["v"] != IM2_KIT_VERSION:
        raise UnusableRun(f"HEAD version {head['v']}, not the P-04 kit's {IM2_KIT_VERSION}.")
    rr = alg.im2_params(market)["p"]["rr"]
    parts: dict[int, dict[int, dict]] = {}
    for tag in (_tag(o) for o in orders_from_results(results_path)):
        for m in _RECS.finditer(tag):
            first, *rest = m.group(1).split(";")
            rec = {"n": first, **_kv(rest)}
            if "k" in rec:
                want = _IM2_FIRST_FIELDS if rec["k"] == "0" else _IM2_LATER_FIELDS
                if set(rec) != want:
                    raise UnusableRun(f"session {first}, chunk {rec['k']}: fields {sorted(rec)} are not the kit's "
                                      f"{sorted(want)}.")
                parts.setdefault(int(rec["n"]), {})[int(rec["k"])] = rec
    days = int(head["days"])                       # the kit counts a session only when it closes and emits it
    if sorted(parts) != list(range(1, days + 1)):
        raise UnusableRun(f"{len(parts)} session records but HEAD implies {days}, or a record is missing.")
    num = lambda x: float(x) if x not in ("", None) else float("nan")          # noqa: E731
    rows: list[dict] = []
    entries = 0
    for n in sorted(parts):
        ch = parts[n]
        first = ch.get(0)
        if first is None or sorted(ch) != list(range(int(first["K"]))):
            raise UnusableRun(f"session {n}: {len(ch)} of {first['K'] if first else '?'} tag chunks present.")
        meta = {"n": n, "d": first["d"], "sym": first["c"], "cal": first["cal"], "sk": first["sk"],
                "st": int(first["st"]), "full": int(first["full"]), "bad": int(first["bad"]), "cov": num(first["cov"]),
                "ref": num(first["ref"]), "pc": num(first["pc"]), "np": int(first["np"]),
                "signals": int(first["sig"]), "dropped": int(first["drop"]), "through": int(first["thru"]),
                "through_actual": int(first["tha"]), "no_bar": int(first["nob"]), "missing": int(first["mis"]),
                "no_band": int(first["nbd"]), "E": int(first["E"]), "rel": first["rel"], "gone": first["gone"]}
        # D-182: every signal the rules raise ends in exactly one place -- dropped inside the wait, no bar after the
        # decision, an entry through its own stop, or an entry. A session whose counts do not add up is not the
        # committed kit's output.
        parts_sum = meta["dropped"] + meta["no_bar"] + meta["through"] + meta["E"]
        if meta["signals"] != parts_sum:
            raise UnusableRun(f"session {n} ({meta['d']}): {meta['signals']} signals but dropped + no_bar + through "
                              f"+ entries = {parts_sum}.")
        rows.append({**meta, "kind": "day"})
        got = 0
        for k in range(int(first["K"])):
            for code in filter(None, ch[k].get("x", "").split("/")):
                subs = code.split("~")
                f = subs[0].split(",")
                if len(subs) != 3 or len(f) != 7 or f[0][:1] not in ("+", "-") or subs[1] == "-":
                    raise UnusableRun(f"session {n}: malformed IM2 entry {code!r}.")
                row = {"n": n, "d": meta["d"], "kind": "entry", "side": 1 if f[0][0] == "+" else -1,
                       "t": int(f[0][1:]), "j0": int(f[1]), "cl": float(f[2]), "ub": float(f[3]), "lb": float(f[4]),
                       "vw": float(f[5]), "mn": float(f[6])}
                row.update(_im2_walk(subs[1], rr, "p", n))
                row.update(_im2_walk(subs[2], rr, "a", n))
                rows.append(row)
                got += 1
        if got != meta["E"]:
            raise UnusableRun(f"session {n}: {got} entry records but its header says {meta['E']}.")
        entries += got
    if entries != int(head["entries"]):
        raise UnusableRun(f"{entries} entry records but HEAD reports {head['entries']}.")
    ints = ("days", "settled", "complete", "signals", "dropped", "through", "orders", "switches", "lost", "late",
            "warm", "hol", "ec", "lo")
    facts = {"market": market, "entries": entries, "skips": head["skips"], "open": head["open"],
             "gone": head["gone"], "lean_version": _lean_version(log_path, results_path),
             **{k: int(head[k]) for k in ints}}
    day = pd.DataFrame([r for r in rows if r["kind"] == "day"])
    for k, col in (("settled", "st"), ("complete", "full"), ("signals", "signals"), ("dropped", "dropped"),
                   ("through", "through")):
        if int(day[col].sum()) != facts[k]:
            raise UnusableRun(f"HEAD {k}={facts[k]} but the sessions sum to {int(day[col].sum())}.")
    if facts["hol"] <= 0 or facts["ec"] <= 0:
        raise UnusableRun("HEAD reports no holidays or no early closes in the window: the exchange calendar was not "
                          "read, and P-03 §3's session rules cannot be applied.")
    return pd.DataFrame(rows), facts


#: Exactly what the committed IM2 kit writes: HEAD's fields, a session's first chunk's and its later chunks'.
_IM2_HEAD_FIELDS = ("v", "market", "days", "settled", "complete", "entries", "signals", "dropped", "through", "orders",
                    "skips", "switches", "lost", "late", "warm", "open", "hol", "ec", "lo", "gone")
_IM2_FIRST_FIELDS = frozenset({"n", "k", "K", "d", "c", "cal", "sk", "st", "full", "bad", "cov", "ref", "pc", "np",
                               "sig", "drop", "thru", "tha", "nob", "mis", "nbd", "E", "rel", "gone", "x"})
#: HEAD's version for the P-04 kits (the P-03 kits, version 1, never ran)
IM2_KIT_VERSION = "2"
_IM2_LATER_FIELDS = frozenset({"n", "k", "K", "x"})


def _lean_version(log_path: Path, results_path: Path) -> str:
    """The LEAN version a run reports: "LEAN Version" in the results JSON, else "LEAN Engine v..." in the logs."""
    m = re.search(r'"LEAN Version"\s*:\s*"([^"]+)"', Path(results_path).read_text(encoding="utf-8", errors="replace"))
    if m:
        return m.group(1)
    m = re.search(r"LEAN Engine v?([0-9][0-9A-Za-z.\-]*)", Path(log_path).read_text(encoding="utf-8", errors="replace"))
    return m.group(1) if m else "not found"


def im2_output_matches_kit(log_path: Path, market: str) -> None:
    """D-131-style check for an attested IM2 run: HEAD names the kit's market and version, carries exactly the kit's
    fields, and shows the calendar was read; `parse_im2` then refuses any record without exactly the kit's fields."""
    lines = prefixed_lines(log_path, alg.IM2_PREFIX)
    head = next((_kv(l.split("|")[2:]) for l in lines if l.startswith(alg.IM2_PREFIX + "|HEAD|")), {})
    if (head.get("market") != market or head.get("v") != IM2_KIT_VERSION
            or set(head) != set(_IM2_HEAD_FIELDS)):
        raise UnusableRun(f"HEAD {head} does not match the committed IM2 kit for {market}.")
    if int(head["hol"]) <= 0 or int(head["ec"]) <= 0:
        raise UnusableRun("HEAD reports no holidays or no early closes in the window: the exchange calendar was not "
                          "read (P-04 §3).")


def grid_output_matches_kit(log_path: Path) -> None:
    """D-131-style structural check for an attested R044 run: HEAD names ZN and the committed rounding bound, and
    every per-year line carries exactly the kit's fields."""
    p = alg.GRID_PREFIX
    lines = prefixed_lines(log_path, p)
    head = next((_kv(l.split("|")[2:]) for l in lines if l.startswith(p + "|HEAD|")), {})
    if head.get("market") != alg.GRID_MARKET or head.get("rounding_ticks") != "%.6g" % alg.GRID_ROUNDING_TICKS:
        raise UnusableRun(f"HEAD {head} does not match the committed kit: a different algorithm ran.")
    for line in lines:
        parts = line.split("|")
        if parts[1] == "Y" and [x.split("=", 1)[0] for x in parts[3:]] != ["n", "ohlc", "off", "beyond", "maxoff"]:
            raise UnusableRun(f"per-year line {line!r} does not carry the kit's fields: a different algorithm ran.")


def parse_grid_check(log_path: Path) -> tuple[pd.DataFrame, dict]:
    """R044: one row per year -- bars, inconsistent bars, off-grid bars, bars beyond rounding, largest offset."""
    p = alg.GRID_PREFIX
    lines = prefixed_lines(log_path, p)
    if not any(l.startswith(p + "|END|") for l in lines):
        raise UnusableRun("no END line in the logs: the run did not finish its summary.")
    rows = []
    for line in lines:
        parts = line.split("|")
        if parts[1] == "Y":
            kv = _kv(parts[3:])
            rows.append({"year": int(parts[2]), **{k: (float(v) if k == "maxoff" else int(v)) for k, v in kv.items()}})
    if not rows:
        raise UnusableRun("no per-year lines.")
    df = pd.DataFrame(rows)
    return df, {"bars": int(df["n"].sum()), "ohlc": int(df["ohlc"].sum()), "off": int(df["off"].sum()),
                "beyond": int(df["beyond"].sum()), "maxoff": float(df["maxoff"].max())}


def parse_gamma_diagnostic(log_path: Path) -> tuple[pd.DataFrame, dict]:
    """R039: every route line as (route, d, field, value) rows, and the notes."""
    p = alg.GDIAG_PREFIX
    lines = prefixed_lines(log_path, p)
    if not any(l.startswith(p + "|END|") for l in lines):
        raise UnusableRun("no END line in the logs: the run did not finish its summary.")
    rows, notes = [], []
    for line in lines:
        parts = line.split("|")
        if parts[1] in ("SLICE", "FILTER", "OC"):
            kv = _kv(parts[2:])
            rows += [dict(route=parts[1], d=kv.get("d", ""), field=k, value=v) for k, v in kv.items() if k != "d"]
        elif parts[1] == "NOTE":
            notes.append("|".join(parts[2:]))
            rows.append(dict(route="NOTE", d="", field="note", value=notes[-1]))
    return pd.DataFrame(rows, columns=["route", "d", "field", "value"]), {"notes": notes}


def parse_gap_evidence(log_path: Path, results_path: Path) -> tuple[pd.DataFrame, dict]:
    """One row per recorded minute bar per development day (D-105), from the order tags."""
    lines = prefixed_lines(log_path, alg.GAP_PREFIX)
    if not any(l.startswith(alg.GAP_PREFIX + "|END|") for l in lines):
        raise UnusableRun("no END line in the logs: the run did not finish its summary.")
    head = next((_kv(l.split("|")[2:]) for l in lines if l.startswith(alg.GAP_PREFIX + "|HEAD|")),
                {})
    if head.get("slots") != str(alg.GAP_SLOTS):
        raise UnusableRun(f"HEAD reports slots={head.get('slots')}; this parser expects "
                          f"{alg.GAP_SLOTS}.")
    heads: dict[int, dict] = {}
    tails: dict[int, str] = {}
    sources = [_tag(o) for o in orders_from_results(results_path)]
    sources += [l for l in lines if l.startswith(alg.GAP_PREFIX + "|LAST")]
    for s in sources:
        for m in _RECS.finditer(s):
            rec = trade_record(m.group(1))
            n = int(rec["n"])
            if "b1" in rec:
                heads.setdefault(n, rec)
            if "b2" in rec:
                tails.setdefault(n, rec["b2"])
    if not heads:
        raise UnusableRun("no per-day records in the order tags or the LAST line.")
    days = int(head.get("days", "0"))
    if sorted(heads) != list(range(1, days + 1)):
        raise UnusableRun(f"{len(heads)} day records but HEAD reports {days} days, or a record "
                          "is missing.")
    missing_tail = [n for n in heads if n not in tails]
    if missing_tail:
        raise UnusableRun(f"days {missing_tail[:5]} have no second bar tag.")
    rows: list[dict] = []
    for n in sorted(heads):
        rows += _gap_bars(heads[n], heads[n]["b1"], tails[n])
    df = pd.DataFrame(rows)
    return df, {"market": head.get("market"), "days": days, "full": int(head.get("full", "0")),
                "skips": head.get("skips"), "switches": int(head.get("switches", "0"))}


def parse_leg_evidence(log_path: Path, results_path: Path) -> tuple[pd.DataFrame, dict]:
    """One row per development day of one C-007 leg, from the order tags and the LAST line."""
    lines = prefixed_lines(log_path, alg.LEG_PREFIX)
    if not any(l.startswith(alg.LEG_PREFIX + "|END|") for l in lines):
        raise UnusableRun("no END line in the logs: the run did not finish its summary.")
    head = next((_kv(l.split("|")[2:]) for l in lines if l.startswith(alg.LEG_PREFIX + "|HEAD|")),
                {})
    recs = []
    sources = [_tag(o) for o in orders_from_results(results_path)]
    sources += [l for l in lines if l.startswith(alg.LEG_PREFIX + "|LAST")]
    for s in sources:
        m = _REC.search(s)
        if m:
            recs.append(trade_record(m.group(1)))
    if not recs:
        raise UnusableRun("no per-day records in the order tags or the LAST line.")
    df = pd.DataFrame(recs).drop_duplicates(subset="n")
    df["n"] = df["n"].astype(int)
    for c in _LEG_NUMERIC:
        df[c] = pd.to_numeric(df[c])
    for c in ("dir", "np", "nw"):
        df[c] = df[c].astype(int)
    df = df.sort_values("n").reset_index(drop=True)
    days = int(head.get("days", "0"))
    unclosed = int(dict(p.split(":") for p in head.get("skips", "").split(",") if ":" in p)
                   .get("unclosed", 0))
    if len(df) != days - unclosed:
        raise UnusableRun(f"{len(df)} day records but HEAD reports {days} days "
                          f"({unclosed} unclosed).")
    if list(df["n"]) != list(range(1, len(df) + 1)):
        raise UnusableRun("day records are not consecutive: a record is missing.")
    return df, {"market": head.get("market"), "days": days, "skips": head.get("skips")}


# ------------------------------------------------------------------ R061-R062 pre-release drift (D-164)

_RELEASE_NUMERIC = ("prd", "post", "nb", "a", "b", "e", "p")


def parse_release(log_path: Path, results_path: Path) -> tuple[pd.DataFrame, dict]:
    """R061-R062 (D-164): one row per scheduled release event with its pre-release and release returns, from
    the order tags. Refuses a run whose summary is missing or whose event records do not match HEAD."""
    p = alg.RELEASE_PREFIX
    lines = prefixed_lines(log_path, p)
    if not any(l.startswith(p + "|END|") for l in lines):
        raise UnusableRun("no END line in the logs: the run did not finish its summary.")
    head = next((_kv(l.split("|")[2:]) for l in lines if l.startswith(p + "|HEAD|")), {})
    recs: dict[int, dict] = {}
    for tag in (_tag(o) for o in orders_from_results(results_path)):
        for m in _RECS.finditer(tag):
            rec = trade_record(m.group(1))
            recs.setdefault(int(rec["n"]), rec)
    emitted = int(head.get("emitted", "0"))
    if sorted(recs) != list(range(1, emitted + 1)):
        raise UnusableRun(f"{len(recs)} event records but HEAD reports {emitted}, or a record is missing.")
    rows = []
    for n in sorted(recs):
        r = recs[n]
        row = {"n": n, "d": r["d"], "t": r["t"], "k": r["k"], "sym": r["c"], "roll": int(r.get("roll", "0"))}
        for k in _RELEASE_NUMERIC:
            v = r.get(k, "")
            row[k] = float(v) if v != "" else float("nan")
        rows.append(row)
    return pd.DataFrame(rows), {"market": head.get("market"), "scheduled": int(head.get("scheduled", "0")),
                                "emitted": emitted, "nodata": int(head.get("nodata", "0")),
                                "switches": int(head.get("switches", "0"))}



def release_output_matches_kit(log_path: Path, results_path: Path, market: str, scheduled: int) -> None:
    """D-165 (as D-131 for the atlas kits): the structural check for an attested release run. HEAD names the kit's
    market and version 1 and reports the committed kit's number of scheduled events (its embedded calendar), and
    every event record carries exactly the committed kit's fields, in its order. Raises UnusableRun otherwise."""
    lines = prefixed_lines(log_path, alg.RELEASE_PREFIX)
    head = next((_kv(l.split("|")[2:]) for l in lines if l.startswith(alg.RELEASE_PREFIX + "|HEAD|")), {})
    if head.get("market") != market:
        raise UnusableRun(f"HEAD names market {head.get('market')!r}; the kit is {market!r}.")
    if head.get("v") != "1":
        raise UnusableRun(f"HEAD reports kit version {head.get('v')!r}; the committed kit is version 1: "
                          "a different algorithm ran.")
    if head.get("scheduled") != str(scheduled):
        raise UnusableRun(f"HEAD reports {head.get('scheduled')!r} scheduled events; the committed kit embeds "
                          f"{scheduled}: a different calendar ran.")
    want = ["d", "t", "k", "c", "roll", *_RELEASE_NUMERIC]
    n = 0
    for tag in (_tag(o) for o in orders_from_results(results_path)):
        for m in _RECS.finditer(tag):
            first, *rest = m.group(1).split(";")
            keys = [p.split("=", 1)[0] for p in rest]
            if keys != want:
                raise UnusableRun(f"event record {first} carries fields {keys}; the committed kit writes {want}: "
                                  "a different algorithm ran.")
            n += 1
    if n == 0:
        raise UnusableRun("no event records to check.")


# ------------------------------------------------------------------ R063-R070 IM2's second implementation (D-200)

IM2X_PREFIX = "IMX"
IM2X_KIT_VERSION = "1"
#: Exactly what the brief fixes (docs/verification/im2_second_implementation.md §4): HEAD's fields, a session's first
#: tag's and its later tags'.
_IM2X_HEAD_FIELDS = frozenset({"v", "market", "days", "warm", "signals", "orders", "switches", "hol", "ec", "lo",
                               "gone"})
_IM2X_FIRST_FIELDS = frozenset({"n", "k", "K", "d", "c", "cal", "sk", "st", "full", "cov", "ref", "pc", "np", "sig",
                                "mis", "nbd", "gone", "x"})
_IM2X_LATER_FIELDS = frozenset({"n", "k", "K", "x"})
_IM2X_SIGNAL = re.compile(r"^([+-])([0-2]\d[0-5]\d),([^,]+),([^,]+),([^,]+),([^,]+)$")


def _im2x_head(log_path: Path) -> dict[str, str]:
    lines = prefixed_lines(log_path, IM2X_PREFIX)
    if not any(l.startswith(IM2X_PREFIX + "|END") for l in lines):
        raise UnusableRun("no END line in the logs: the run did not finish its summary.")
    head = next((_kv(l.split("|")[2:]) for l in lines if l.startswith(IM2X_PREFIX + "|HEAD|")), None)
    if head is None:
        raise UnusableRun("no HEAD line in the logs.")
    return head


def im2x_output_matches_kit(log_path: Path, market: str) -> None:
    """D-131-style check for an attested run of IM2's second implementation (D-200): HEAD names the kit's market and
    version, carries exactly the brief's fields, and shows the calendar was read; `parse_im2x` then refuses any record
    without exactly the brief's fields."""
    head = _im2x_head(log_path)
    if head.get("market") != market or head.get("v") != IM2X_KIT_VERSION or set(head) != _IM2X_HEAD_FIELDS:
        raise UnusableRun(f"HEAD {head} does not match the committed second implementation for {market}.")
    if int(head["hol"]) <= 0 or int(head["ec"]) <= 0:
        raise UnusableRun("HEAD reports no holidays or no early closes in the window: the exchange calendar was not "
                          "read.")


def parse_im2x(log_path: Path, results_path: Path) -> tuple[pd.DataFrame, dict]:
    """R063-R070 (D-200; the brief's §4): one row per session (kind 'day': contract `sym`, calendar code, skip reason,
    settled, complete, coverage, open `ref`, prior close `pc`, lookback depth `np`, its `signals`, decisions with no
    bar `missing` and with no band `no_band`, and the scheduled sessions with no data before it, `gone`) and one per
    signal (kind 'signal': side, decision time `tm` in minutes after midnight CT, the decision close `cl`, the bands
    `ub` and `lb`, and `vw`). Refuses a missing END or HEAD, a HEAD or tag without exactly the brief's fields, a missing
    session or chunk, a malformed signal, or counts that disagree with the session's or HEAD's."""
    head = _im2x_head(log_path)
    market = head.get("market")
    if market not in alg.IM2_MARKETS or head.get("v") != IM2X_KIT_VERSION or set(head) != _IM2X_HEAD_FIELDS:
        raise UnusableRun(f"HEAD {head} is not the second implementation's (D-200).")
    parts: dict[int, dict[int, dict]] = {}
    orders = 0
    for tag in (_tag(o) for o in orders_from_results(results_path)):
        if not tag.startswith(IM2X_PREFIX + ";"):
            continue
        orders += 1
        rec = _kv(tag.split(";")[1:])
        want = _IM2X_FIRST_FIELDS if rec.get("k") == "0" else _IM2X_LATER_FIELDS
        if set(rec) != want:
            raise UnusableRun(f"tag {tag[:80]!r}: fields {sorted(rec)} are not the brief's {sorted(want)}.")
        parts.setdefault(int(rec["n"]), {})[int(rec["k"])] = rec
    days = int(head["days"])
    if sorted(parts) != list(range(1, days + 1)):
        raise UnusableRun(f"{len(parts)} session records but HEAD reports {days}, or a record is missing.")
    if orders != int(head["orders"]):
        raise UnusableRun(f"{orders} tagged orders but HEAD reports {head['orders']}.")
    num = lambda x: float(x) if x not in ("", None) else float("nan")          # noqa: E731
    rows: list[dict] = []
    total = 0
    for n in sorted(parts):
        ch = parts[n]
        first = ch.get(0)
        if (first is None or sorted(ch) != list(range(int(first["K"])))
                or any(c["K"] != first["K"] for c in ch.values())):
            raise UnusableRun(f"session {n}: {len(ch)} of {first['K'] if first else '?'} tag chunks present.")
        meta = {"n": n, "d": first["d"], "kind": "day", "sym": first["c"], "cal": first["cal"], "sk": first["sk"],
                "st": int(first["st"]), "full": int(first["full"]), "cov": num(first["cov"]), "ref": num(first["ref"]),
                "pc": num(first["pc"]), "np": int(first["np"]), "signals": int(first["sig"]),
                "missing": int(first["mis"]), "no_band": int(first["nbd"]), "gone": first["gone"]}
        rows.append(meta)
        got = 0
        for k in range(int(first["K"])):
            for code in filter(None, ch[k]["x"].split("/")):
                m = _IM2X_SIGNAL.match(code)
                if m is None:
                    raise UnusableRun(f"session {n}: malformed signal {code!r}.")
                hhmm = m.group(2)
                rows.append({"n": n, "d": meta["d"], "kind": "signal", "side": 1 if m.group(1) == "+" else -1,
                             "tm": int(hhmm[:2]) * 60 + int(hhmm[2:]), "cl": float(m.group(3)),
                             "ub": float(m.group(4)), "lb": float(m.group(5)), "vw": float(m.group(6))})
                got += 1
        if got != meta["signals"]:
            raise UnusableRun(f"session {n}: {got} signal records but its header says {meta['signals']}.")
        total += got
    if total != int(head["signals"]):
        raise UnusableRun(f"{total} signal records but HEAD reports {head['signals']}.")
    facts = {"market": market, "days": days, "warm": int(head["warm"]), "signals": total, "orders": orders,
             "switches": int(head["switches"]), "hol": int(head["hol"]), "ec": int(head["ec"]), "lo": int(head["lo"]),
             "gone": head["gone"], "lean_version": _lean_version(log_path, results_path)}
    if facts["hol"] <= 0 or facts["ec"] <= 0:
        raise UnusableRun("HEAD reports no holidays or no early closes in the window: the exchange calendar was not "
                          "read.")
    return pd.DataFrame(rows), facts

