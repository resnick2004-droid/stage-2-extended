"""H4 audit, refusals, strict `+ 5 min` overlap counter, independent scalar oracle, and per-unit scorecard extractor
(`prereg/H4_rebaseline.md` sections 7, 9, 11, 12, 15, 16, 17, Appendix B; E-287).

Clean separation of concerns (`H4_TEXT4_c2` M-1):
- `extended/three_way_baseline.py` enforces unconditional second-rung refusal (`_hand_out`) and reports simultaneous
  holds `[entry, exit_at_R)` beside (`overlaps`, `rung_alerts`).
- THIS module (`extended/h4_audit.py`) enforces H4's refusing per-unit strict `+ 5 min` overlap check on taken trades
  in Stage 2's bar-end clock (`[fill bar end, exit bar end at taken R + 5 min)` — exact D-429 boundary: `+5 min` exact
  counts 0, `+4 min` counts 1), BOTH inside the runner AND independently in the auditor from `h4_trades_<baseline>.csv`
  without importing `three_way_baseline`.
- THIS module also provides an **independent scalar oracle** (F4-5: zero imports of `three_way_baseline`,
  `three_way_move`, or `three_way_redraw`) that replays every sampled unit's race-arm taken trade from its logged inputs
  using exact `Fraction` arithmetic for the race (`p * G - (1 - p) * L == 0`) and its own scalar walker for `walk` and
  `move`, refusing any deviation, floor violation, or historical-field leakage (`u`, `mae`, `at_need`, `rr_used`,
  `exit_kind`, F4-10).

Zero raw H4 seed literals appear here; every H4 seed is issued by role through `extended.three_way_seeds.issue`.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import subprocess
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from extended import journey_measures as JM
from extended import lock_guard as LG
from extended import search_calendar as SCAL
from extended import search_cut as SC
from extended import three_way_keys as K
from extended import three_way_seeds as S
from extended import user_measures as UM
from extended import wave42 as W

# --------------------------------------------------------------------------------------------- pinned H4 constants (E-287)

H4_DECL_REL: str = "prereg/H4_rebaseline.md"
H4_DECL_LF_SHA256: str = "a2c1408e8f22a3d4926248a3bf53f311f65234ce1e15399dc378ed35d4aa913c"
H4_REG_CONSTANTS_REL: str = "results/h4_registered_constants.csv"
H4_REG_CONSTANTS_SHA256: str = "7c3884f5445f37be09a09dd838150d34ff468636775a24f96e894e76de1dc413"
H4_SEARCH_CALENDAR_REL: str = "results/search_calendar.csv"
H4_SEARCH_CALENDAR_SHA256: str = W.SEARCH_CALENDAR_SHA256
H4_J: int = 128
H4_SAMPLE_SHARE: float = 0.01
H4_STRICT_GAP_MIN: float = 5.0
#: rc-3: 2 x 2.75 GB = 5.51 GB free disk required before running H4-B
H4_MIN_FREE_DISK_BYTES: int = int(5.51 * 1_000_000_000)
H4_WALK_MAX: int = 1024
H4_EPS: float = 1e-6
H4_SNAP: float = 1e-9
H4_FAVOUR: int = 1
H4_NESTED_CUTS: tuple[str, ...] = ("2022-12-30", "2023-06-30", "2023-09-29")
H4_LAST_NESTED_CUT: str = "2023-09-29"
#: F4-10: historical fields forbidden on race-arm trade log rows
RACE_FORBIDDEN_FIELDS: tuple[str, ...] = ("u", "mae", "at_need", "rr_used", "exit_kind")


class H4AuditRefused(RuntimeError):
    """A pre-run refusal, overlap kill, blank-rule refusal, or auditor check failed."""


class H4OracleRefused(H4AuditRefused):
    """Zero-edge oracle failed on a sampled trade log row."""


class H4OverlapRefused(H4AuditRefused):
    """Strict +5 min per-unit overlap count > 0 on taken trades (section 7 / RC-2)."""


# --------------------------------------------------------------------------------------------- pre-run refusals (section 16.1)


def lf_sha256(path: Path | str) -> str:
    raw = Path(path).read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(raw).hexdigest()


def raw_sha256(path: Path | str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_w42_freeze(repo: Path) -> str:
    """F4-3: verify W42-R1 is pinned (`config/w42_r1_pin.json`) and zero commit since pin touches `IMPORTED_FILES`."""
    pin_file = Path(repo) / "config" / "w42_r1_pin.json"
    if not pin_file.is_file():
        raise H4AuditRefused(f"REFUSED (F4-3): missing W42-R1 pin file {pin_file}")
    pin_data = json.loads(pin_file.read_text(encoding="utf-8"))
    pin_commit = str(pin_data.get("commit", ""))
    if len(pin_commit) != 40:
        raise H4AuditRefused(f"REFUSED (F4-3): malformed W42-R1 pin commit {pin_commit!r}")
    import importlib.util
    import sys as _sys

    spec = importlib.util.spec_from_file_location("_w42_apply_check", Path(repo) / "scripts" / "wave42_apply.py")
    if spec is None or spec.loader is None:
        raise H4AuditRefused("REFUSED (F4-3): cannot load scripts/wave42_apply.py")
    mod = importlib.util.module_from_spec(spec)
    _sys.modules[spec.name] = mod
    try:
        spec.loader.exec_module(mod)
        bad = mod.commit_problem(repo, pin_commit)
    finally:
        _sys.modules.pop(spec.name, None)
    if bad:
        raise H4AuditRefused(f"REFUSED (F4-3): W42-R1 IMPORTED_FILES freeze violated: {bad}")
    return pin_commit


def check_run_lock(repo: Path) -> str:
    """Verify `run.lock` exists at `main_root(repo)` and matches `S2X_LOCK_HOLDER`."""
    holder = os.environ.get(LG.LOCK_HOLDER_ENV, "").strip()
    if not holder:
        raise H4AuditRefused(f"REFUSED: {LG.LOCK_HOLDER_ENV} is unset (run under scripts/run_clean.py --hours --mem-gb)")
    mroot = LG.main_root(repo)
    if mroot is None:
        raise H4AuditRefused(f"REFUSED: cannot resolve main root for run.lock from {repo}")
    lock_file = mroot / LG.LOCK_NAME
    if not lock_file.is_file():
        raise H4AuditRefused(f"REFUSED: run.lock not found at {lock_file}")
    data = json.loads(lock_file.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("job") != holder:
        raise H4AuditRefused(f"REFUSED: run.lock job {data.get('job') if isinstance(data, dict) else None!r} != {holder!r}")
    return holder


def check_free_disk(path: Path | str, min_bytes: int = H4_MIN_FREE_DISK_BYTES) -> int:
    """rc-3: refuse unless at least `min_bytes` (default 5.51 GB = 2 x 2.75 GB) is free on disk."""
    free = int(shutil.disk_usage(Path(path)).free)
    if free < int(min_bytes):
        raise H4AuditRefused(
            f"REFUSED (rc-3): free disk {free / 1e9:.2f} GB < required {min_bytes / 1e9:.2f} GB at {path}"
        )
    return free


def assert_h4_preconditions(
    repo: Path | str,
    *,
    require_clean: bool = True,
    require_lock: bool = True,
    require_disk: bool = False,
    min_disk_bytes: int = H4_MIN_FREE_DISK_BYTES,
    check_w42_git: bool = True,
) -> dict[str, Any]:
    """H4 section 16 item 1: all pre-run refusals checked before any bar, schedule, or coin is read."""
    root = Path(repo)
    decl_path = root / H4_DECL_REL
    if not decl_path.is_file():
        raise H4AuditRefused(f"REFUSED: missing H4 declaration {decl_path}")
    got_decl = lf_sha256(decl_path)
    if got_decl != H4_DECL_LF_SHA256:
        raise H4AuditRefused(f"REFUSED: {H4_DECL_REL} LF sha256 {got_decl} != pinned {H4_DECL_LF_SHA256}")

    reg_path = root / H4_REG_CONSTANTS_REL
    try:
        reg = SC.load_constants(reg_path, expected_sha256=H4_REG_CONSTANTS_SHA256)
    except Exception as exc:
        raise H4AuditRefused(f"REFUSED: registered constants check failed: {exc}") from exc

    cal_path = root / H4_SEARCH_CALENDAR_REL
    if not cal_path.is_file():
        raise H4AuditRefused(f"REFUSED: missing search calendar {cal_path}")
    cal = SCAL.load_search_calendar(cal_path)
    if cal.file_sha256 != H4_SEARCH_CALENDAR_SHA256:
        raise H4AuditRefused(
            f"REFUSED: search_calendar.csv sha256 {cal.file_sha256} != pinned {H4_SEARCH_CALENDAR_SHA256}"
        )
    if cal.dates[0] != W.SEARCH_FIRST or cal.dates[-1] != W.SEARCH_LAST:
        raise H4AuditRefused(f"REFUSED: search calendar span {cal.dates[0]}..{cal.dates[-1]} != {W.SEARCH_FIRST}..{W.SEARCH_LAST}")

    w42_pin = check_w42_freeze(root) if check_w42_git else "skipped_in_unit_test"

    if require_clean:
        from extended import results as RES

        bad = RES.clean_run_problem()
        if bad:
            raise H4AuditRefused(f"REFUSED: H4 requires a clean run (scripts/run_clean.py): {bad}")

    holder = check_run_lock(root) if require_lock else None
    free_bytes = check_free_disk(root, min_disk_bytes) if require_disk else int(shutil.disk_usage(root).free)

    return {
        "h4_decl_sha256": got_decl,
        "w42_pin_commit": w42_pin,
        "reg_constants_sha256": H4_REG_CONSTANTS_SHA256,
        "search_calendar_sha256": cal.file_sha256,
        "search_calendar_digest": cal.calendar_sha256,
        "search_sessions": len(cal.dates),
        "lock_holder": holder,
        "free_disk_bytes": free_bytes,
        "reg_designs": sorted(reg.keys()),
    }


def check_job_ends_search_window(dates: Sequence[Any], what: str = "job") -> list[str]:
    """rm-5 & rm-6: refuse any job whose calendar does not end on 2023-12-29 or diverges from Q-197's search calendar."""
    ds = SC.check_calendar(dates, last=SC.LAST_DAY)
    if not ds or ds[-1] != W.SEARCH_LAST:
        raise H4AuditRefused(f"REFUSED (rm-5): {what} calendar ends on {ds[-1] if ds else None}, not {W.SEARCH_LAST}")
    return ds


# --------------------------------------------------------------------------------------------- audit sample (H4-U)


def sample_uniform(start: int, seed_index: int, *, seed: Any = None, part: int | None = None) -> float:
    """H4 section 15 (F4-7): unit `(start, seed_index)` audit-sample uniform from `h4_sample` in part `H4-U`."""
    sd = S.issue("h4_sample") if seed is None else seed
    pt = S.PARTS["H4-U"] if part is None else int(part)
    key = K.seed_key(sd, "plant", part=pt, history=0, plant=int(start), replicate=int(seed_index))
    return float(K.uniforms(key, 1)[0])


def is_sampled_unit(
    start: int,
    seed_index: int,
    *,
    share: float = H4_SAMPLE_SHARE,
    seed: Any = None,
    part: int | None = None,
) -> bool:
    """True when unit `(start, seed_index)` falls in H4's seeded 1% audit sample (`h4_sample`, part `H4-U`)."""
    return sample_uniform(start, seed_index, seed=seed, part=part) < float(share)


# --------------------------------------------------------------------------------------------- strict +5 min overlap (RC-2 / M-1)


def count_strict_overlaps(
    trades: Sequence[Mapping[str, Any]],
    *,
    gap_minutes: float = H4_STRICT_GAP_MIN,
    day_key: str = "day_idx",
    entry_key: str = "fill_bar",
    exit_key: str = "exit_bar_at_R",
) -> int:
    """H4 section 7 & 17 (RC-2, M-1): count pairs of taken trades whose spans
    `[fill bar end, exit bar end at taken R + gap_minutes)` intersect on Stage 2's bar-end clock
    (`day_idx * 1440 + bar_end`).

    Exact D-429 / `shared_days.py:357-359` boundary:
    - Second trade fill bar end == first trade exit bar end + 5 min -> ADMITTED, counts **0**.
    - Second trade fill bar end == first trade exit bar end + 4 min -> REFUSED, counts **1**.
    Independent of `three_way_baseline` so the auditor re-runs the exact same check on `h4_trades_<baseline>.csv`.
    """
    spans: list[tuple[float, float]] = []
    for row in trades:
        law = row.get("law")
        if law in ("missed", "day_end"):
            continue
        d = int(row[day_key])
        ent = float(row[entry_key])
        ex = float(row[exit_key])
        if not (math.isfinite(ent) and math.isfinite(ex)):
            raise H4OverlapRefused(f"non-finite fill/exit bar in overlap check: {row}")
        if ex < ent:
            raise H4OverlapRefused(f"trade exits ({ex}) before fill ({ent}): {row}")
        t0 = d * 1440.0 + ent
        t1 = d * 1440.0 + ex
        spans.append((t0, t1))
    spans.sort()
    overlaps = 0
    max_end = -math.inf
    gap = float(gap_minutes)
    for t0, t1 in spans:
        if t0 < max_end + gap - 1e-12:
            overlaps += 1
        if t1 > max_end:
            max_end = t1
    return overlaps


def assert_zero_strict_overlaps(
    trades: Sequence[Mapping[str, Any]],
    *,
    what: str = "unit",
    gap_minutes: float = H4_STRICT_GAP_MIN,
    day_key: str = "day_idx",
    entry_key: str = "fill_bar",
    exit_key: str = "exit_bar_at_R",
) -> int:
    n = count_strict_overlaps(trades, gap_minutes=gap_minutes, day_key=day_key, entry_key=entry_key, exit_key=exit_key)
    if n > 0:
        raise H4OverlapRefused(f"REFUSED (RC-2 / M-1): {what} has {n} strict +{gap_minutes:g} min overlap(s)")
    return 0


# --------------------------------------------------------------------------------------------- independent scalar oracle (F4-5)


def _indep_walk_step(sigma: float, T: float, walk_max: int = H4_WALK_MAX) -> int:
    return max(1, int(math.ceil(float(sigma) * math.sqrt(float(T)) / math.sqrt(float(walk_max)) - 1e-12)))


def _indep_walk_steps(sigma: float, T: float, step: int) -> int:
    return max(1, int(math.floor(float(sigma) * float(sigma) * float(T) / (int(step) * int(step)) + 0.5)))


def _parse_bool_flag(v: Any) -> bool:
    """Parse boolean flag safely from Python bool, int/float, or CSV string ('0'/'1'/'True'/'False')."""
    if isinstance(v, (bool, np.bool_)):
        return bool(v)
    s = str(v).strip().lower()
    if s in ("true", "t", "yes"):
        return True
    if s in ("false", "f", "no", ""):
        return False
    return bool(int(float(s)))


def walk_scalar_independent(uniforms: Sequence[float], G: Fraction, L: Fraction, step: int) -> tuple[Fraction, int]:
    """Independent scalar R-10 stopped walk (zero imports from `three_way_redraw` / `three_way_move` /
    `three_way_baseline`). Uses exact `Fraction` martingale two-point race probabilities with `H4_SNAP = 1e-9`
    interior lattice boundary matching float-divided barriers. Returns `(gross_ticks_Fraction, exit_code: 1/-1/0)`."""
    s_int = int(step)
    s = Fraction(s_int)
    u_top = max(int(math.ceil(float(G) / float(s_int) - H4_SNAP)) - 1, 0)
    d_bot = max(int(math.ceil(float(L) / float(s_int) - H4_SNAP)) - 1, 0)
    rho_u = G - u_top * s
    rho_d = L - d_bot * s
    q_top = float(s / (s + rho_u))
    q_bot = float(rho_d / (s + rho_d))
    q_both = float(rho_d / (rho_u + rho_d))
    i = 0
    for u in uniforms:
        u_f = float(u)
        top = i == u_top
        bot = i == -d_bot
        if top and bot:
            return (G, 1) if u_f < q_both else (-L, -1)
        if top:
            if u_f < q_top:
                return G, 1
            i -= 1
        elif bot:
            if u_f < q_bot:
                i += 1
            else:
                return -L, -1
        else:
            i = (i + 1) if u_f < 0.5 else (i - 1)
    return i * s, 0


def check_race_exact_zero_gross(G: Fraction, L: Fraction) -> None:
    """F4-5: exact Fraction check that `p * G - (1 - p) * L == 0` where `p = L / (L + G)`."""
    if not (G > 0 and L > 0):
        raise H4OracleRefused(f"non-positive race barriers G={G}, L={L}")
    p = L / (L + G)
    gross_ev = p * G - (Fraction(1) - p) * L
    if gross_ev != 0:
        raise H4OracleRefused(f"non-zero exact race gross EV: {gross_ev}")


def verify_race_trade_row(
    row: Mapping[str, Any],
    *,
    seed: Any,
    part: int,
    history: int = 0,
    tol: float = 1e-9,
) -> float:
    """F4-5 & F4-10: verify ONE taken race-arm trade log row from its logged inputs alone, using an independent
    scalar replay on the exact same Philox key stream. Refuses (`H4OracleRefused`) on any mismatch, non-zero gross
    expectation, floor breach, or historical-field leakage. Returns the pre-clip time-exit clip credit
    (`max(0.0, -room - out_logged)`, zero for non-time exits; `prereg/H4_rebaseline.md:257`)."""
    # F4-10: forbidden historical fields must never appear (or must be None / empty) on a race-arm row
    for bad_col in RACE_FORBIDDEN_FIELDS:
        if bad_col in row and row[bad_col] is not None and str(row[bad_col]).strip() != "":
            raise H4OracleRefused(f"REFUSED (F4-10): forbidden historical field {bad_col!r}={row[bad_col]!r} on race row")

    law = str(row["law"])
    if law in ("missed", "day_end"):
        return 0.0

    start = int(row["start"])
    seed_index = int(row["seed_index"])
    day_idx = int(row["day_idx"])
    decision = int(row["decision"])
    sub = int(row["sub"])
    underlying = str(row.get("underlying", "NQ"))

    room = float(row["room"])
    out_logged = float(row["out"])
    if not math.isfinite(out_logged):
        raise H4OracleRefused(f"taken trade has non-finite out={out_logged}")

    d = float(row["d"])
    e = float(row["e_cost"])
    xt = float(row["xt_cost"])
    xs = float(row["xs_cost"])
    xf = float(row["xf_cost"])
    stop_ticks = int(row["stop_ticks"])

    L_fill = min(float(stop_ticks) * d, room - e - max(xs, xf))
    if law == "fill_fail":
        if out_logged < -room - tol:
            raise H4OracleRefused(f"REFUSED (oracle): booked out {out_logged} passes floor -room={-room}")
        if L_fill > H4_EPS:
            raise H4OracleRefused(f"fill_fail logged with L_fill={L_fill} > EPS")
        if abs(out_logged - (-room)) > tol:
            raise H4OracleRefused(f"fill_fail booked {out_logged} != -room {-room}")
        return 0.0
    if not L_fill > H4_EPS:
        raise H4OracleRefused(f"law={law!r} logged when L_fill={L_fill} <= EPS (should be fill_fail or day_end)")

    L_dol = min(float(stop_ticks) * d, room - e - xs)
    L_ticks_want = L_dol / d
    G_ticks = float(row["G"])
    if abs(float(row["L_ticks"]) - L_ticks_want) > tol:
        raise H4OracleRefused(f"logged L_ticks={row['L_ticks']} != recomputed {L_ticks_want}")

    G_frac = Fraction(G_ticks)
    L_frac = Fraction(L_ticks_want)
    check_race_exact_zero_gross(G_frac, L_frac)

    unit = K.Unit(seed, int(part), int(history), seed_index, start)
    mom = K.moment(day_idx, decision, sub)

    if law == "race":
        if out_logged < -room - tol:
            raise H4OracleRefused(f"REFUSED (oracle): booked out {out_logged} passes floor -room={-room}")
        p_want = L_dol / (L_dol + G_ticks * d)
        if abs(float(row["p"]) - p_want) > tol:
            raise H4OracleRefused(f"logged p={row['p']} != {p_want}")
        u = float(K.uniforms(unit.coin_key(mom, K.RACE, underlying), 1)[0])
        win = u < p_want
        want_out = (-e + G_ticks * d - xt) if win else (-e - L_dol - xs)
        if abs(out_logged - want_out) > tol:
            raise H4OracleRefused(f"race scalar replay mismatch: logged {out_logged} != oracle {want_out}")
        # Cushion-bound loss lands exactly on the floor
        if not win and (room - e - xs) <= float(stop_ticks) * d + tol:
            if abs(out_logged - (-room)) > tol:
                raise H4OracleRefused(f"cushion-bound loss {out_logged} did not land on floor {-room}")
        return 0.0

    entry_bar = int(row["fill_bar"])
    limit_bar = int(row["time_limit"])
    sigma = float(row["sigma"])

    if law == "move":
        be_open = int(row["be_open"])
        if not (entry_bar < be_open < limit_bar):
            raise H4OracleRefused(f"move law logged with invalid be_open={be_open} vs entry={entry_bar}, limit={limit_bar}")
        d1 = float(be_open - entry_bar)
        d2 = float(limit_bar - be_open)
        s1 = _indep_walk_step(sigma, d1)
        n1 = _indep_walk_steps(sigma, d1, s1)
        s2 = _indep_walk_step(sigma, d2)
        n2 = _indep_walk_steps(sigma, d2, s2)
        if (int(row["s1"]), int(row["n1"]), int(row["s2"]), int(row["n2"])) != (s1, n1, s2, n2):
            raise H4OracleRefused(
                f"move step params mismatch: logged {(row['s1'], row['n1'], row['s2'], row['n2'])} != {(s1, n1, s2, n2)}"
            )
        us = K.uniforms(unit.coin_key(mom, K.WALK, underlying), n1 + n2)
        v1, k1 = walk_scalar_independent(us[:n1], G_frac, L_frac, s1)
        if k1 == 0:
            moved = v1 >= H4_FAVOUR
            down2 = v1 if moved else (v1 + L_frac)
            if abs(float(row["move_x"]) - float(v1)) > tol:
                raise H4OracleRefused(f"move_x mismatch: {row['move_x']} != {float(v1)}")
            if _parse_bool_flag(row["move_moved"]) != bool(moved):
                raise H4OracleRefused(f"move_moved mismatch: {row['move_moved']} != {moved}")
            if abs(float(row["move_G2"]) - float(G_frac - v1)) > tol:
                raise H4OracleRefused(f"move_G2 mismatch: {row['move_G2']} != {float(G_frac - v1)}")
            if abs(float(row["move_down2"]) - float(down2)) > tol:
                raise H4OracleRefused(f"move_down2 mismatch: {row['move_down2']} != {float(down2)}")
            v2, k2 = walk_scalar_independent(us[n1 : n1 + n2], G_frac - v1, down2, s2)
            if k2 == 1:
                gross_f, kc = G_frac, 1
            elif k2 == -1:
                gross_f, kc = (Fraction(0), 3) if moved else (-L_frac, -1)
            else:
                gross_f, kc = v1 + v2, 0
        else:
            gross_f, kc = v1, k1
        cost = xt if kc == 1 else (xs if kc in (-1, 3) else xf)
        want_out = -e + float(gross_f) * d - cost
        floor_min = (-room - max(0.0, xf - xs) - tol) if kc == 0 else (-room - tol)
        if out_logged < floor_min:
            raise H4OracleRefused(f"REFUSED (oracle): booked out {out_logged} passes floor bound {floor_min}")
        if abs(out_logged - want_out) > tol:
            raise H4OracleRefused(f"move scalar replay mismatch: logged {out_logged} != oracle {want_out}")
        if int(row["exit_code"]) != int(kc):
            raise H4OracleRefused(f"move exit_code mismatch: logged {row['exit_code']} != oracle {kc}")
        return max(0.0, -room - out_logged) if kc == 0 else 0.0

    if law == "walk":
        T = float(max(1, limit_bar - entry_bar))
        s = _indep_walk_step(sigma, T)
        n = _indep_walk_steps(sigma, T, s)
        if (int(row["s1"]), int(row["n1"])) != (s, n):
            raise H4OracleRefused(f"walk step params mismatch: logged {(row['s1'], row['n1'])} != {(s, n)}")
        us = K.uniforms(unit.coin_key(mom, K.WALK, underlying), n)
        v, kc = walk_scalar_independent(us, G_frac, L_frac, s)
        cost = xt if kc == 1 else (xs if kc == -1 else xf)
        want_out = -e + float(v) * d - cost
        floor_min = (-room - max(0.0, xf - xs) - tol) if kc == 0 else (-room - tol)
        if out_logged < floor_min:
            raise H4OracleRefused(f"REFUSED (oracle): booked out {out_logged} passes floor bound {floor_min}")
        if abs(out_logged - want_out) > tol:
            raise H4OracleRefused(f"walk scalar replay mismatch: logged {out_logged} != oracle {want_out}")
        if int(row["exit_code"]) != int(kc):
            raise H4OracleRefused(f"walk exit_code mismatch: logged {row['exit_code']} != oracle {kc}")
        return max(0.0, -room - out_logged) if kc == 0 else 0.0

    raise H4OracleRefused(f"unknown race-arm law {law!r}")


# --------------------------------------------------------------------------------------------- per-unit measure extractor


def accounts_active_by_day(path: Any, horizon: int) -> list[int]:
    """Count live accounts (Combines + funded accounts) trading on each calendar day k = 1 .. `horizon` of a
    `LockstepPath`. Matches lockstep's calendar convention: bought/activated on day `d` -> trades from `d + 1`
    through `resolved_on` / `ended_on` inclusive."""
    h = int(horizon)
    counts = [0] * h
    for c in path.combines:
        lo = max(1, int(c.purchase_day) + 1)
        hi = h if c.resolved_on is None else min(h, int(c.resolved_on))
        for k in range(lo, hi + 1):
            counts[k - 1] += 1
    for f in path.funded:
        lo = max(1, int(f.activation_day) + 1)
        hi = h if f.ended_on is None else min(h, int(f.ended_on))
        for k in range(lo, hi + 1):
            counts[k - 1] += 1
    return counts


def unit_days_for_measures(
    path: Any,
    log_rows: Sequence[Mapping[str, Any]],
    blocks: Sequence[Any],
    start: int,
    horizon: int,
) -> list[dict[str, Any]]:
    """Build `journey_measures.workload` and `journey_measures.supply` session dicts for days 1..`horizon`."""
    h = int(horizon)
    active = accounts_active_by_day(path, h)
    taken_by_day: dict[int, list[tuple[float, float]]] = {}
    for r in log_rows:
        if r.get("law") in ("missed", "day_end"):
            continue
        i = int(r["i"])
        k = i - int(start) + 1
        if 1 <= k <= h:
            j = int(r["j"])
            b = blocks[i]
            ent = float(b.entry_t[j])
            R = r.get("R")
            ex_by = getattr(b, "exit_by_rr", None)
            if R is not None and ex_by is not None and float(R) in ex_by and math.isfinite(float(ex_by[float(R)][j])):
                ex = float(ex_by[float(R)][j])
            else:
                ex = float(b.exit_t[j])
            taken_by_day.setdefault(k, []).append((ent, max(ent, ex)))
    days: list[dict[str, Any]] = []
    for k in range(1, h + 1):
        i = int(start) + k - 1
        b = blocks[i]
        offered = tuple(float(x) for x in getattr(b, "entry_t", ()))
        tk = tuple(taken_by_day.get(k, ()))
        ac = max(active[k - 1], 1 if tk else 0)
        days.append({"accounts": ac, "taken": tk, "offered": offered})
    return days


def extract_funded_account_records(path: Any, lag: int) -> list[dict[str, Any]]:
    """Extract Measure (31) funded-account records matching `user_beside.journey_record`'s `accounts` schema."""
    return [
        {
            "activation_day": int(f.activation_day),
            "ended_on": None if f.ended_on is None else int(f.ended_on),
            "closed": bool(f.closed),
            "abandoned": bool(getattr(f, "abandoned", False)),
            "denied": int(getattr(f, "denied", 0)),
            "household_closed": bool(getattr(f, "household_closed", False)),
            "ftp_closed": bool(getattr(f, "ftp_closed", False)),
            "arrivals": tuple(int(f.activation_day) + 1 + int(r) + int(lag) for r in f.payout_days),
        }
        for f in getattr(path, "funded", ())
    ]


def encode_funded_accounts(accounts: Sequence[Mapping[str, Any]], max_window: int = JM.YEAR) -> str:
    """Compact colon-free encoding of funded-account records (`act/end/ending/arr1+arr2;...`) for CSV storage
    (colon-free so it never triggers timestamp rules in `extended.price_levels`)."""
    parts: list[str] = []
    for a in accounts:
        act = int(a["activation_day"])
        end = -1 if a.get("ended_on") is None else int(a["ended_on"])
        ending = JM.account_ending(a, max_window if end >= 0 else max(max_window, act + 1))
        arr_s = "+".join(str(int(d)) for d in a.get("arrivals", ()))
        parts.append(f"{act}/{end}/{ending}/{arr_s}")
    return ";".join(parts)


def decode_funded_accounts(encoded: Any) -> list[dict[str, Any]]:
    """Decode `encode_funded_accounts` back into `JM.funded_lifetime`-compatible account dicts."""
    if encoded is None or (isinstance(encoded, float) and math.isnan(encoded)):
        return []
    s = str(encoded).strip()
    if not s:
        return []
    out: list[dict[str, Any]] = []
    for tok in s.split(";"):
        if not tok:
            continue
        act_s, end_s, ending, arr_s = tok.split("/", 3)
        end_i = int(end_s)
        arrs = tuple(int(x) for x in arr_s.split("+") if x)
        out.append(
            {
                "activation_day": int(act_s),
                "ended_on": None if end_i < 0 else end_i,
                "ending": None if ending == "window" else ending,
                "closed": ending == "breach",
                "abandoned": ending == "policy",
                "denied": 1 if ending == "denied" else 0,
                "household_closed": ending == "live",
                "ftp_closed": ending == "ftp",
                "arrivals": arrs,
            }
        )
    return out


def extract_unit_measures(
    *,
    baseline: str,
    arm: str,
    reading: str,
    start: int,
    start_date: str,
    seed_index: int,
    sessions_left: int,
    rel: np.ndarray,
    first_pass: int,
    first_pay: int,
    arrivals: Sequence[tuple[int, float]],
    path: Any,
    log_rows: Sequence[Mapping[str, Any]],
    blocks: Sequence[Any],
    latency: float,
    strict_overlaps: int,
    beside_counts: Mapping[str, int] | None = None,
    payout_lag: int = 2,
    W_win: int = W.W,
    year_win: int = JM.YEAR,
) -> dict[str, Any]:
    """Compute every W42-R1 `REQUIRED` key + Wave 4.1 / Appendix B per-unit measures for one `(start, seed_index)`.

    Enforces MEASURES 1.3's never-blank rule on `E_h`: finite wherever `sessions_left >= h`, NaN where `sessions_left < h`.
    """
    obs = int(len(rel) - 1)
    sl = int(sessions_left)
    row: dict[str, Any] = {
        "baseline": str(baseline),
        "arm": str(arm),
        "reading": str(reading),
        "block": W.BLOCK,
        "start_idx": int(start),
        "start": str(start_date),
        "seed": int(seed_index),
        "sessions_left": sl,
        "obs": obs,
        "strict_overlaps": int(strict_overlaps),
    }

    # Month 1..3 nets and peaks (W42-R1 REQUIRED: horizon 21*m, inclusive of close 21*m per MEASURES B-2 / M-6)
    for m in (1, 2, 3):
        h_m = JM.MONTH * m
        if sl >= h_m and obs >= h_m:
            row[f"net_month_{m}"] = float(rel[h_m])
            row[f"peak_month_{m}"] = float(UM.peak_through(rel, h_m))
        else:
            row[f"net_month_{m}"] = float("nan")
            row[f"peak_month_{m}"] = float("nan")

    # W = 126 measures (W42-R1 REQUIRED + Appendix B)
    fp_val = float(first_pass) if int(first_pass) > 0 else float("nan")
    fy_val = float(first_pay) if int(first_pay) > 0 else float("nan")
    if sl >= W_win and obs >= W_win:
        spent_pass, pass_cens = JM.spent_to_event(rel, fp_val, W_win)
        spent_pay, pay_cens = JM.spent_to_event(rel, fy_val, W_win)
        fp_days = float(fp_val) if (math.isfinite(fp_val) and fp_val <= W_win) else float(W_win + 1)
        fy_days = float(fy_val) if (math.isfinite(fy_val) and fy_val <= W_win) else float(W_win + 1)
        evals_pass, evals_cens = JM.evaluations_to_first_pass([c.purchase_day for c in path.combines], fp_val, W_win)
        days_w = unit_days_for_measures(path, log_rows, blocks, start, W_win)
        wl = JM.workload(days_w, float(latency))
        sp = JM.supply(days_w)
        lw, lw_cens = JM.longest_wait([d for d, _ in arrivals], W_win)
        first_pay_arr = [cash for d, cash in arrivals if int(d) <= W_win]
        first_pay_size = float(first_pay_arr[0]) if first_pay_arr else float("nan")
        be_126 = UM.break_even_day(rel[: W_win + 1])
        be_days = float(be_126) if math.isfinite(be_126) else float(W_win + 1)

        row.update(
            {
                "first_pass_days": fp_days,
                "cash_to_first_pass": float(spent_pass),
                "cash_to_first_pass_censored": int(pass_cens),
                "evaluations_before_first_pass": float(evals_pass),
                "evaluations_before_first_pass_censored": int(evals_cens),
                "first_payout_days": fy_days,
                "spent_before_first_payout": float(spent_pay),
                "spent_before_first_payout_censored": int(pay_cens),
                "first_payout_size": first_pay_size,
                "break_even_days_126": be_days,
                "net_month_6": float(rel[W_win]),
                "peak_oop_126": float(JM.peak_oop(rel, W_win)),
                "longest_wait_126": float(lw),
                "longest_wait_126_censored": int(lw_cens),
                "orders_max": float(wl["orders_max"]),
                "orders_mean": float(wl["orders_mean"]),
                "accounts_max": float(wl["accounts_max"]),
                "accounts_mean": float(wl["accounts_mean"]),
                "screen_hours_mean": float(wl["screen_hours_mean"]),
                "screen_hours_max": float(wl["screen_hours_max"]),
                "taken_mean": float(sp["taken_mean"]),
                "offered_mean": float(sp["offered_mean"]),
            }
        )
    else:
        for col in (
            "first_pass_days",
            "cash_to_first_pass",
            "cash_to_first_pass_censored",
            "evaluations_before_first_pass",
            "evaluations_before_first_pass_censored",
            "first_payout_days",
            "spent_before_first_payout",
            "spent_before_first_payout_censored",
            "first_payout_size",
            "break_even_days_126",
            "net_month_6",
            "peak_oop_126",
            "longest_wait_126",
            "longest_wait_126_censored",
            "orders_max",
            "orders_mean",
            "accounts_max",
            "accounts_mean",
            "screen_hours_mean",
            "screen_hours_max",
            "taken_mean",
            "offered_mean",
        ):
            row[col] = float("nan")

    # 21-session pass/pay indicators (measures (4) and (8))
    if sl >= JM.MONTH and obs >= JM.MONTH:
        row["passed_by_21"] = float(math.isfinite(fp_val) and fp_val <= JM.MONTH)
        row["paid_by_21"] = float(math.isfinite(fy_val) and fy_val <= JM.MONTH)
    else:
        row["passed_by_21"] = float("nan")
        row["paid_by_21"] = float("nan")

    # 252-session (12-month) measures (W42-R1 REQUIRED + Appendix B including W=252 beside)
    if sl >= year_win and obs >= year_win:
        rel_y = rel[: year_win + 1]
        mc = JM.monthly_changes(rel, JM.MONTHS)
        m412 = JM.monthly_net_4_12(rel)
        peak252 = JM.peak_oop(rel, year_win)
        rmar = JM.return_on_money_at_risk(rel, year_win)
        arr252 = [(int(d), float(c)) for d, c in arrivals if 1 <= int(d) <= year_win]
        paid_total = float(sum(c for _, c in arr252))
        fees_252 = paid_total - float(rel[year_win])
        payouts_per_fee = (paid_total / fees_252) if fees_252 > JM.TOL else float("nan")
        # M-7: delegate directly to UM.break_even_day / UM.fell_back / UM.deepest_fall_after (drawdown from running high)
        be_252 = UM.break_even_day(rel_y)
        fb_252 = UM.fell_back(rel_y, be_252)
        fell = float("nan") if fb_252 is None else float(fb_252)
        deepest = float(UM.deepest_fall_after(rel_y, be_252))
        # W = 252 beside versions of (1)-(3), (5)-(7), (21)
        spent_pass_252, pass_cens_252 = JM.spent_to_event(rel, fp_val, year_win)
        spent_pay_252, pay_cens_252 = JM.spent_to_event(rel, fy_val, year_win)
        fp_days_252 = float(fp_val) if (math.isfinite(fp_val) and fp_val <= year_win) else float(year_win + 1)
        fy_days_252 = float(fy_val) if (math.isfinite(fy_val) and fy_val <= year_win) else float(year_win + 1)
        evals_pass_252, evals_cens_252 = JM.evaluations_to_first_pass([c.purchase_day for c in path.combines], fp_val, year_win)
        lw_252, lw_cens_252 = JM.longest_wait([d for d, _ in arrivals], year_win)
        first_pay_size_252 = float(arr252[0][1]) if arr252 else float("nan")

        # Longest run of months without a payout in 1..12
        pay_months = {min(JM.MONTHS, (d - 1) // JM.MONTH + 1) for d, _ in arr252}
        best_run = cur_run = 0
        for mm in range(1, JM.MONTHS + 1):
            if mm in pay_months:
                cur_run = 0
            else:
                cur_run += 1
                best_run = max(best_run, cur_run)
        # Largest month's share of year's payouts (measure 23)
        by_m = np.zeros(JM.MONTHS, float)
        for d, c in arr252:
            by_m[min(JM.MONTHS, (d - 1) // JM.MONTH + 1) - 1] += c
        max_m_share = float(by_m.max() / paid_total) if paid_total > JM.TOL else float("nan")

        row.update(
            {
                "peak_oop_12_months": float(peak252),
                "share_months_positive": float(np.mean(mc > JM.TOL)),
                "net_month_12": float(rel[year_win]),
                "return_on_money_at_risk": float(rmar),
                "monthly_net_4_12_median": float(m412["median"]),
                "monthly_net_4_12_mean": float(m412["mean"]),
                "spread_monthly_net": float(np.std(mc, ddof=1)),
                "payouts_per_month": float(len(arr252) / float(JM.MONTHS)),
                "payouts_per_fee": float(payouts_per_fee),
                "longest_no_payout_months": float(best_run),
                "largest_month_payout_share": float(max_m_share),
                "break_even_days_252": float(be_252) if math.isfinite(be_252) else float(year_win + 1),
                "fell_below_be_252": float(fell),
                "deepest_fall_after_be_252": float(deepest),
                "first_pass_days_252": fp_days_252,
                "cash_to_first_pass_252": float(spent_pass_252),
                "cash_to_first_pass_252_censored": int(pass_cens_252),
                "evaluations_before_first_pass_252": float(evals_pass_252),
                "evaluations_before_first_pass_252_censored": int(evals_cens_252),
                "first_payout_days_252": fy_days_252,
                "spent_before_first_payout_252": float(spent_pay_252),
                "spent_before_first_payout_252_censored": int(pay_cens_252),
                "first_payout_size_252": first_pay_size_252,
                "longest_wait_252": float(lw_252),
                "longest_wait_252_censored": int(lw_cens_252),
            }
        )
    else:
        for col in (
            "peak_oop_12_months",
            "share_months_positive",
            "net_month_12",
            "return_on_money_at_risk",
            "monthly_net_4_12_median",
            "monthly_net_4_12_mean",
            "spread_monthly_net",
            "payouts_per_month",
            "payouts_per_fee",
            "longest_no_payout_months",
            "largest_month_payout_share",
            "break_even_days_252",
            "fell_below_be_252",
            "deepest_fall_after_be_252",
            "first_pass_days_252",
            "cash_to_first_pass_252",
            "cash_to_first_pass_252_censored",
            "evaluations_before_first_pass_252",
            "evaluations_before_first_pass_252_censored",
            "first_payout_days_252",
            "spent_before_first_payout_252",
            "spent_before_first_payout_252_censored",
            "first_payout_size_252",
            "longest_wait_252",
            "longest_wait_252_censored",
        ):
            row[col] = float("nan")

    # Beside counts (section 12: fill failures, day ends, out of room, time-exit clip credit, move / breakeven, tb_overlaps)
    row["fill_failures"] = int(sum(1 for r in log_rows if r.get("law") == "fill_fail"))
    row["day_ends"] = int(sum(1 for r in log_rows if r.get("law") == "day_end"))
    path_inner = getattr(path, "path", None)
    row["out_of_room_accounts"] = int(
        getattr(
            path_inner,
            "combines_out_of_room",
            sum(1 for c in path.combines if getattr(c, "out_of_room", False)),
        )
    )
    row["time_exit_clip_credit"] = float(
        sum(
            max(0.0, -float(r["room"]) - float(r["out"]))
            for r in log_rows
            if r.get("law") in ("walk", "move")
            and r.get("exit") == 0
            and math.isfinite(float(r.get("out", float("nan"))))
        )
    )
    row["funded_lifetimes"] = encode_funded_accounts(extract_funded_account_records(path, int(payout_lag)), year_win)
    bc = beside_counts or {}
    for k in ("move_trades", "b_redrawn", "b_historical", "be_differs", "be_unrecorded", "tb_overlaps"):
        row[k] = int(bc.get(k, 0))

    # Never-blank check on W42-R1 REQUIRED keys (MEASURES 1.3)
    for req_key, (h_req, lo, hi) in W.REQUIRED.items():
        if sl >= h_req:
            v = float(row[req_key])
            if not math.isfinite(v):
                raise H4AuditRefused(
                    f"REFUSED (blank rule): {baseline}/{arm} start={start_date} seed={seed_index} "
                    f"has non-finite {req_key}={v} on E_{h_req}"
                )
            if v < lo - 1e-12 or v > hi + 1e-12:
                raise H4AuditRefused(
                    f"REFUSED (range): {baseline}/{arm} start={start_date} seed={seed_index} "
                    f"{req_key}={v} outside [{lo}, {hi}]"
                )
    return row


def share_window_sessions_after_last_cut(
    dates: Sequence[str],
    horizon: int,
    *,
    last_cut: str = H4_LAST_NESTED_CUT,
) -> float:
    """H4 section 4 & 12: share of window sessions after `2023-09-29` across all complete starts `E_h`."""
    ds = [str(d) for d in dates]
    n = len(ds)
    h = int(horizon)
    if n < h:
        return float("nan")
    after = [1 if d > str(last_cut) else 0 for d in ds]
    # Prefix sum for O(n) exact count over all complete windows [s, s + h)
    ps = [0]
    for a in after:
        ps.append(ps[-1] + a)
    tot_after = sum(ps[s + h] - ps[s] for s in range(n - h + 1))
    tot_sessions = (n - h + 1) * h
    return float(tot_after) / float(tot_sessions)


__all__ = [
    "H4_DECL_REL",
    "H4_DECL_LF_SHA256",
    "H4_REG_CONSTANTS_REL",
    "H4_REG_CONSTANTS_SHA256",
    "H4_SEARCH_CALENDAR_REL",
    "H4_SEARCH_CALENDAR_SHA256",
    "H4_J",
    "H4_SAMPLE_SHARE",
    "H4_STRICT_GAP_MIN",
    "H4_MIN_FREE_DISK_BYTES",
    "H4_NESTED_CUTS",
    "H4_LAST_NESTED_CUT",
    "RACE_FORBIDDEN_FIELDS",
    "H4AuditRefused",
    "H4OracleRefused",
    "H4OverlapRefused",
    "lf_sha256",
    "raw_sha256",
    "check_w42_freeze",
    "check_run_lock",
    "check_free_disk",
    "assert_h4_preconditions",
    "check_job_ends_search_window",
    "sample_uniform",
    "is_sampled_unit",
    "count_strict_overlaps",
    "assert_zero_strict_overlaps",
    "walk_scalar_independent",
    "check_race_exact_zero_gross",
    "verify_race_trade_row",
    "accounts_active_by_day",
    "unit_days_for_measures",
    "extract_funded_account_records",
    "encode_funded_accounts",
    "decode_funded_accounts",
    "extract_unit_measures",
    "share_window_sessions_after_last_cut",
]
