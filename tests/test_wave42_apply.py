"""W42-R1's application script (`scripts/wave42_apply.py`; the red team's second read V-1, V-2), on synthetic files in
a temporary `results/` folder (no bar, no result file of this repository, no held-out outcome):

- it applies the rule once, to the collection result it reads from disk, recording the file's and the sidecar's
  sha256, both calendars', the ledger's, the rule's and its own; a second application is refused by the output file;
- it refuses a sidecar that is not the file's, a stress arm, a forged subset, an unpinned or another search calendar,
  and a held-out calendar that is not the pinned one or holds a date outside the held-out years;
- it derives the held-out counts from the held-out calendar's dates and the fee unit through `standard_prices`;
- its declared sources are the named adapter, Q-197's loader, the ledger's fee and `write_result`.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import yaml

from extended import wave42 as R

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod                             # a dataclass looks its module up by name
    spec.loader.exec_module(mod)
    return mod


A = _load("wave42_apply_under_test", "scripts/wave42_apply.py")
T = _load("wave42_rule_generator", "tests/test_wave42_rule.py")       # the rule's tests' synthetic generator
CAL_FILE_SHA = "c" * 64


def _held_out_csv(n: int, first: str = "2024-01-02") -> bytes:
    d = np.arange(np.datetime64(first), np.datetime64("2026-12-31"))
    dates = [str(x) for x in d[np.is_busday(d)]][:n]
    return ("ordinal,date\n" + "".join(f"{i},{x}\n" for i, x in enumerate(dates))).encode("utf-8")


class Writer:
    """A stand-in for `write_result`: records the call, writes the CSV and its sidecar, never overwrites."""

    def __init__(self):
        self.calls = []

    def __call__(self, df, name, **kw):
        out = Path(kw["results_dir"]) / name
        assert not out.exists()
        self.calls.append((name, kw))
        out.write_text(df.to_csv(index=False), encoding="utf-8")
        Path(f"{out}.manifest.json").write_text(json.dumps({"parameters": kw["parameters"]}), encoding="utf-8")
        return out, Path(f"{out}.manifest.json")


def _write_collection(d: Path, rs, **over) -> str:
    body = ("synthetic collection " + R.readings_digest(rs) + "\n").encode("utf-8")
    (d / R.COLLECTION_RESULT).write_bytes(body)
    sha = A.sha256_bytes(body)
    params = {k: v for k, v in T._manifest(rs, **over).items() if k != "sha256"}
    (d / f"{R.COLLECTION_RESULT}.manifest.json").write_text(json.dumps({"sha256": sha, "parameters": params}),
                                                            encoding="utf-8")
    return sha


@pytest.fixture()
def env(tmp_path, monkeypatch):
    d = tmp_path / "results"
    d.mkdir()
    rs = T._readings()
    _write_collection(d, rs)
    ho = _held_out_csv(T.NHO)
    (d / R.HELD_OUT_CALENDAR).write_bytes(ho)
    monkeypatch.setattr(R, "HELD_OUT_CALENDAR_SHA256", A.sha256_bytes(ho))
    monkeypatch.setattr(R, "SEARCH_CALENDAR_SHA256", CAL_FILE_SHA)
    seen = {}

    def adapter(path, man):
        seen["adapter"] = (Path(path).name, man["sha256"])
        return seen.get("readings", rs)

    def loader(path):
        seen["calendar"] = Path(path).name
        return SimpleNamespace(dates=T.CAL, calendar_sha256=R.calendar_digest(T.CAL), file_sha256=CAL_FILE_SHA)

    w = Writer()
    src = A.Sources(adapter=adapter, calendar_loader=loader, fee=lambda: (T.FEE, R.FEE_SOURCE, "f" * 64), writer=w)
    return SimpleNamespace(d=d, rs=rs, src=src, w=w, seen=seen)


def test_applies_once_and_records_every_hash(env) -> None:
    params = A.apply(env.d, env.src)
    assert [c[0] for c in env.w.calls] == [R.OUTPUT_NAME] and (env.d / R.OUTPUT_NAME).is_file()
    side = (env.d / f"{R.COLLECTION_RESULT}.manifest.json").read_bytes()
    assert params["h4_result_sha256"] == A.sha256_file(env.d / R.COLLECTION_RESULT)
    assert params["h4_sidecar_sha256"] == A.sha256_bytes(side)
    assert params["readings_sha256"] == R.readings_digest(env.rs)
    assert params["held_out_calendar_sha256"] == R.HELD_OUT_CALENDAR_SHA256 and params["held_out_sessions"] == T.NHO
    assert params["search_calendar_file_sha256"] == CAL_FILE_SHA
    for k in ("rule_text_sha256", "rule_module_sha256", "script_sha256", "ledger_sha256", "values_sha256"):
        assert len(params[k]) == 64, k
    assert env.seen["adapter"] == (R.COLLECTION_RESULT, params["h4_result_sha256"])
    assert env.seen["calendar"] == R.SEARCH_CALENDAR
    direct = R.setting_rule(env.rs, h4=R.H4Binding(params["h4_result_sha256"], T._manifest(
        env.rs, sha256=params["h4_result_sha256"])), search_calendar=T.CAL, fee_unit=T.FEE, fee_source=R.FEE_SOURCE,
        test_starts=T.TEST_STARTS, test_starts_source={"file": R.HELD_OUT_CALENDAR,
                                                       "sha256": R.HELD_OUT_CALENDAR_SHA256, "sessions": T.NHO})
    assert params["values_sha256"] == direct.digest()
    kw = env.w.calls[0][1]
    assert kw["script"] == A.SCRIPT and kw["seed"] is None and kw["require_seed"] is False


def test_the_counts_are_derived_from_the_held_out_calendars_dates(env) -> None:
    params = A.apply(env.d, env.src)
    assert params["test_starts"] == {str(h): R.complete_starts(T.NHO, h) for h in R.HORIZONS}


def test_a_second_application_is_refused_by_the_output_file(env) -> None:
    A.apply(env.d, env.src)
    with pytest.raises(A.ApplyRefused, match="applied once"):
        A.apply(env.d, env.src)
    assert len(env.w.calls) == 1


def test_another_wave42_output_refuses_the_application(env) -> None:
    (env.d / "w42_r1_values_draft.csv").write_text("x\n", encoding="utf-8")
    with pytest.raises(A.ApplyRefused, match="Wave 4.2 output already exists"):
        A.apply(env.d, env.src)
    assert env.w.calls == []


def test_a_sidecar_that_is_not_the_files_is_refused(env) -> None:
    (env.d / R.COLLECTION_RESULT).write_bytes(b"another file\n")
    with pytest.raises(A.ApplyRefused, match="not its sidecar's"):
        A.apply(env.d, env.src)
    (env.d / f"{R.COLLECTION_RESULT}.manifest.json").unlink()
    with pytest.raises(A.ApplyRefused, match="sidecar are both required"):
        A.apply(env.d, env.src)
    assert env.w.calls == []


@pytest.mark.parametrize("arm", ["worse_1", "missed_0.1", "off_as_walked"])
def test_a_stress_arm_is_refused(env, arm) -> None:
    _write_collection(env.d, env.rs, arm=arm)
    with pytest.raises(R.Wave42Refused, match="arm under the verdict"):
        A.apply(env.d, env.src)
    assert env.w.calls == []


def test_a_forged_subset_is_refused(env) -> None:
    """V-1's P2: a sidecar written for the first half of the start days, the adapter handing that half in."""
    half = T._subset(env.rs, rows=slice(0, T.N // 2))
    _write_collection(env.d, half)
    env.seen["readings"] = half
    with pytest.raises(R.Wave42Refused, match="every session of the search calendar"):
        A.apply(env.d, env.src)
    assert env.w.calls == []


def test_the_search_calendar_is_bound_by_its_pinned_sha256(env, monkeypatch) -> None:
    monkeypatch.setattr(R, "SEARCH_CALENDAR_SHA256", None)
    with pytest.raises(A.ApplyRefused, match="not pinned yet"):
        A.apply(env.d, env.src)
    monkeypatch.setattr(R, "SEARCH_CALENDAR_SHA256", "d" * 64)
    with pytest.raises(A.ApplyRefused, match="not the pinned one"):
        A.apply(env.d, env.src)
    assert env.w.calls == []


def test_the_held_out_calendar_is_bound_by_its_pinned_sha256(env, monkeypatch) -> None:
    (env.d / R.HELD_OUT_CALENDAR).write_bytes(_held_out_csv(T.NHO + 1))
    with pytest.raises(A.ApplyRefused, match="is not the pinned"):
        A.apply(env.d, env.src)
    early = _held_out_csv(T.NHO, first="2023-12-01")             # holds search-year dates
    (env.d / R.HELD_OUT_CALENDAR).write_bytes(early)
    monkeypatch.setattr(R, "HELD_OUT_CALENDAR_SHA256", A.sha256_bytes(early))
    with pytest.raises(A.ApplyRefused, match="strictly increasing inside"):
        A.apply(env.d, env.src)
    assert env.w.calls == []


def test_only_the_date_column_is_read(env, monkeypatch) -> None:
    """The ledger entry: dates only. A column beside the dates is not read (its values never reach the rule)."""
    rows = _held_out_csv(T.NHO).decode("utf-8").splitlines()
    text = "\n".join([rows[0] + ",note"] + [r + ",not read" for r in rows[1:]]) + "\n"
    (env.d / R.HELD_OUT_CALENDAR).write_bytes(text.encode("utf-8"))
    monkeypatch.setattr(R, "HELD_OUT_CALENDAR_SHA256", A.sha256_bytes(text.encode("utf-8")))
    assert A.held_out_sessions(env.d) == (T.NHO, R.HELD_OUT_CALENDAR_SHA256)


def test_the_declared_sources(monkeypatch) -> None:
    names = []
    monkeypatch.setattr(A, "_import", lambda dotted: names.append(dotted) or (lambda *a, **k: None))
    s = A.declared_sources()
    assert names == [R.ADAPTER, "extended.search_calendar:load_search_calendar"]
    assert R.ADAPTER == "extended.h4_collect:w42_readings"
    assert s.fee is A._declared_fee and s.writer is A._declared_writer


def test_an_unbuilt_source_refuses() -> None:
    with pytest.raises(A.ApplyRefused, match="not built on this commit"):
        A._import("extended.no_such_module_w42:w42_readings")


def test_the_declared_fee_is_the_ledgers_standard_subscription() -> None:
    """V-2: in its own process (the vendored loader), `_declared_fee` reads `standard_prices`' subscription."""
    code = ("import importlib.util, json, sys; sys.path.insert(0, %r); "
            "s = importlib.util.spec_from_file_location('w42a', %r); m = importlib.util.module_from_spec(s); "
            "sys.modules['w42a'] = m; s.loader.exec_module(m); print(json.dumps(m._declared_fee()))") % (str(ROOT), str(ROOT / A.SCRIPT))
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=300, cwd=ROOT)
    assert out.returncode == 0, out.stderr
    fee, source, ledger_sha = json.loads(out.stdout.strip().splitlines()[-1])
    led = yaml.safe_load((ROOT / A.LEDGER_FILE).read_text(encoding="utf-8"))["rules"]["subscription_fee"]
    assert led["status"] == "verified" and fee == float(led["value"])
    assert source == R.FEE_SOURCE and ledger_sha == A.sha256_file(ROOT / A.LEDGER_FILE)


def test_main_takes_no_argument() -> None:
    with pytest.raises(SystemExit, match="takes no argument"):
        A.main(["--results", "elsewhere"])


# ------------------------------------------------------------------------------------- the pre-pin fixes (R3-2, R3-4)
def test_the_sidecar_hash_is_line_ending_free_and_nothing_else(env) -> None:
    """R3-2: the sidecar's sha256 is over its bytes with CRLF normalised to LF, so an LF and a CRLF checkout hash the
    same; any other difference changes it, and a changed recorded sha256 is refused."""
    side = env.d / f"{R.COLLECTION_RESULT}.manifest.json"
    lf = side.read_bytes().replace(b"\r\n", b"\n")
    lf = json.dumps(json.loads(lf), indent=2).encode("utf-8")              # several lines, so CRLF has work to do
    side.write_bytes(lf)
    s_lf = A.read_collection(env.d)[3]
    side.write_bytes(lf.replace(b"\n", b"\r\n"))
    assert A.read_collection(env.d)[3] == s_lf == A.sha256_bytes(lf)
    side.write_bytes(lf.replace(b'"block"', b'"block" '))                   # one byte more, same JSON
    assert A.read_collection(env.d)[3] != s_lf
    man = json.loads(lf)
    man["sha256"] = "e" * 64
    side.write_bytes(json.dumps(man, indent=2).encode("utf-8"))
    with pytest.raises(A.ApplyRefused, match="not its sidecar's"):
        A.read_collection(env.d)


def test_the_held_out_calendar_refuses_a_confirmation_date_and_a_repeat(env, monkeypatch) -> None:
    """R3-4: a held-out calendar ending 2026-07-17 (re-hashed), or repeating a date, is refused."""
    rows = _held_out_csv(T.NHO).decode("utf-8").rstrip("\n").split("\n")
    late = "\n".join(rows + [f"{T.NHO},2026-07-17"]) + "\n"
    rep = "\n".join(rows + [rows[-1].replace(rows[-1].split(",")[0], str(T.NHO))]) + "\n"
    for text in (late, rep):
        b = text.encode("utf-8")
        (env.d / R.HELD_OUT_CALENDAR).write_bytes(b)
        monkeypatch.setattr(R, "HELD_OUT_CALENDAR_SHA256", A.sha256_bytes(b))
        with pytest.raises(A.ApplyRefused, match="strictly increasing inside"):
            A.held_out_sessions(env.d)


def test_any_wave42_output_name_refuses(env) -> None:
    """R3-4: the glob is `w42_*`: a stray `w42_x.csv` refuses the application."""
    (env.d / "w42_x.csv").write_text("x\n", encoding="utf-8")
    with pytest.raises(A.ApplyRefused, match="Wave 4.2 output already exists"):
        A.apply(env.d, env.src)


def test_the_refusal_comes_before_any_input_is_read(env, monkeypatch) -> None:
    """R3-4: with an output present, the script refuses before it reads the collection, either calendar, the fee or
    the adapter (each reader replaced by one that records a call)."""
    (env.d / R.OUTPUT_NAME).write_text("x\n", encoding="utf-8")
    calls = []
    for name in ("read_collection", "search_calendar", "held_out_sessions"):
        monkeypatch.setattr(A, name, lambda *a, _n=name, **k: calls.append(_n))
    src = A.Sources(adapter=lambda *a: calls.append("adapter"), calendar_loader=lambda *a: calls.append("loader"),
                    fee=lambda: calls.append("fee"), writer=lambda *a, **k: calls.append("writer"))
    with pytest.raises(A.ApplyRefused, match="applied once"):
        A.apply(env.d, src)
    assert calls == []


def test_the_output_records_the_fee_path_and_the_power_target(env) -> None:
    """R3-1: the audit list's fee path and MDL_POWER's value at the run's commit are in the output's parameters."""
    params = A.apply(env.d, env.src)
    assert params["fee_via"] == "extended.levers_terms.standard_prices"
    from extended.family_stats import MDL_POWER
    assert params["power_target"] == MDL_POWER
