"""RD-02's real inputs (`prereg/RD-02_payout_policy.md` 8.1, 9.1 item 8, 14; Q-105e after the red team's third read,
`docs/reviews/BUILD_RD-02_v3_2026-11-16.md`, D2): what the reading reads through Stage 2's own builders -- U1's jobs
and U1's file (8.1 item 2's repeat), Q-44's per-start file read as text (item 6), the registered gate calls with their
zero-edge twin and the registered gate rows (9.1 item 8) -- in a module of its own, so that the identity that certifies
it (`identity/pp_identity.py`, the reference policy only) covers exactly this file and not the reading's other code.

    from extended import use_vendored_stage2; use_vendored_stage2()
    from extended import pp_inputs as PI
    ri = PI.RealInputs()                         # the reading's (extended/pp_run.py) and the identity's, the same code

The reading (`extended/pp_run.py`) re-exports every name here. Importing this module puts the vendored tree on
`sys.path`.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import pandas as pd

from extended import ROOT, use_vendored_stage2

use_vendored_stage2()

from extended import payout_policy as PP  # noqa: E402
from extended import user_readings as R  # noqa: E402

BESIDE = ("denial_10", "denial_25", "denial_50", "rtp")
#: 9.1 item 8 (D-564 (4)'s rows) and item 6 on the gate, from a gate row's columns
GATE_READING = (("growth_on_required_bankroll", "pf_growth_on_base_p50"), ("required_bankroll_p90", "pf_required_p90"),
                ("days_to_first_payout_median", "median_days_to_first_payout"),
                ("payouts_per_path_mean", "mean_payouts_per_path"))
GATE_DIVERGE = (("evaluations_bought_mean", "mean_combine_purchases"), ("funded_accounts_mean", "mean_accounts_funded"),
                ("share_accounts_ever_paid", "share_accounts_ever_paid"),
                ("realised_to_intended_capped_risk", "realised_to_intended_capped_risk"))
GATE_SHIFTS = ("point", "lower_bound")

NAN = float("nan")


class Refused(RuntimeError):
    """A check of 8.1 or 8.2 failed: the reading stops, nothing is written (the failure protocol applies)."""


class Inputs:
    """What the run reads, for one source (the real designs, or a synthetic campaign in the tests)."""

    def preflight(self, designs: Sequence[str]) -> list[str]:
        """Everything that can be checked before the judged block's reads are authorised (its problems): read no bar."""
        return []

    def jobs(self, design: str) -> dict[str, dict[str, Any]]:
        raise NotImplementedError

    def identity_problems(self, design: str, arm: str, outs: list[dict[str, Any]]) -> list[str]:
        """8.1 item 2's repeat: the `ref` start rows against the reference."""
        raise NotImplementedError

    def ladder_problems(self, design: str, response: str, outs: list[dict[str, Any]]) -> list[str]:
        """8.1 item 6: `ref`'s readings beside against the reference."""
        raise NotImplementedError

    def gate_call(self, design: str, cell: str, twin: bool) -> dict[str, Any]:
        """The gate's keywords for a cell (`blocks` among them), its path sink and its label."""
        raise NotImplementedError

    def gate_pairing_rows(self, design: str, cell: str, twin: bool, g: dict[str, Any]) -> list[dict[str, Any]]:
        """9.1 item 8: the cell's gate paths beside the base's registered ones (none for a source without them)."""
        return []

    def base_gate_rows(self, design: str) -> dict[str, dict[str, Any]]:
        """The base's registered gate row at 0 %, the placement off, by shift (none for a source without one)."""
        return {}

    def n_paths(self) -> int:
        raise NotImplementedError


ROW_KEYS = ("section", "part", "design", "arm", "cell", "mode", "response", "base", "block", "measure", "stat", "value",
            "n", "h", "note")


def _row(**kw: Any) -> dict[str, Any]:
    base = {"section": "", "part": "", "design": "", "arm": "", "cell": "", "mode": "", "response": "off", "base": "",
            "block": "", "measure": "", "stat": "", "value": np.nan, "n": 0, "h": 0, "note": ""}
    base.update(kw)
    if not base["part"]:
        base["part"] = base["section"]
    return base


def _f(x: Any) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return NAN
    return v


# ------------------------------------------------------------------------------------------------ Q-44's comparison


LADDER_TEXT = ("design", "arm", "response", "start_date", "exact_runs_differing")


def _blank(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, str):
        return v.strip() in ("", "nan", "NaN", "None")
    try:
        return not math.isfinite(float(v))
    except (TypeError, ValueError):
        return False


def _text(v: Any) -> str:
    if _blank(v):
        return ""
    if isinstance(v, str):
        return v.strip()
    f = float(v)
    return str(int(f)) if f.is_integer() else repr(f)


def q44_problems(mine: pd.DataFrame, theirs: pd.DataFrame, what: str, *, all_starts: bool) -> list[str]:
    """8.1 item 6 (R4): our per-start rows (`user_readings.rounded(start_table(...))`) against Q-44's file read as text
    (`extended.results.read_result(..., text=True)`), start for start, every column that file writes, by E-010's
    comparator's rules: a blank equals only a blank; text as text (a day list such as "63" or "21 63" stays text); money
    to the cent (both rounded to it: equal within 1e-6); every other number within 1e-9."""
    out = []
    by: dict[int, dict] = {}
    for r in theirs.to_dict("records"):
        s = int(float(r["start_day"]))
        if s in by:
            return [f"{what}: start {s} twice in Q-44's file"]
        by[s] = r
    ours = {int(r["start_day"]): r for r in mine.to_dict("records")}
    missing = sorted(set(ours) - set(by))
    if missing:
        out.append(f"{what}: {len(missing)} of our starts not in Q-44's file (first: start {missing[0]})")
    if all_starts and set(by) - set(ours):
        out.append(f"{what}: {len(set(by) - set(ours))} of Q-44's {len(by)} starts not reproduced")
    common = sorted(set(ours) & set(by))
    for col in R.START_COLS:
        if col not in theirs.columns:
            out.append(f"{what}: Q-44's file has no column {col}")
            continue
        tol = 1e-6 if col in R.MONEY_COLS else 1e-9
        bad = []
        for s in common:
            a, b = ours[s].get(col), by[s].get(col)
            if col in LADDER_TEXT:
                same = _text(a) == _text(b)
            elif _blank(a) or _blank(b):
                same = _blank(a) and _blank(b)
            else:
                try:
                    same = abs(float(a) - float(b)) <= tol
                except (TypeError, ValueError):
                    same = False
            if not same:
                bad.append(s)
        if bad:
            s = bad[0]
            out.append(f"{what}: {col} differs from Q-44's file on {len(bad)} of {len(common)} starts (first: start "
                       f"{s}: {ours[s].get(col)!r} against {by[s].get(col)!r})")
    return out


class RealInputs(Inputs):
    """P-14's and P-16's registered designs, read through Stage 2's own builders (the lead's run, from a clean
    checkout, its reads authorised first): U1's jobs (`identity/user_beside_identity.py`'s `build`), U1's file for 8.1
    item 2's repeat, Q-44's per-start file (as text) for item 6, the registered gate calls and their zero-edge twin, and
    the registered gate rows. `identity/pp_identity.py` certifies this class at `ref` (D2): its gate comparison is built
    through `gate_call(design, "ref", twin)`, its U1 rows through `jobs` and `identity_problems`, and 8.1 item 6 at `ref`
    through `ladder_problems`."""

    GATE_FILES = {"p14": "a3_brk30_cb20_gate.csv", "p16": "rc_s150_all_gate.csv"}

    def __init__(self, starts: int | None = None, n_paths: int = 500, q44_path: Path | str | None = None):
        self.starts = starts
        self._n_paths = int(n_paths)
        self._jobs: dict[str, Any] = {}
        self._gate: dict[str, Any] = {}
        self._q44: pd.DataFrame | None = None
        self._q44_path = Path(q44_path) if q44_path is not None else ROOT / "results" / "user_beside_starts.csv"
        self._base_gate: dict[str, dict[str, dict[str, Any]]] = {}

    def n_paths(self) -> int:
        return self._n_paths

    def q44(self) -> pd.DataFrame:
        if self._q44 is None:
            from extended.results import read_result

            self._q44 = read_result(self._q44_path, text=True)
        return self._q44

    def preflight(self, designs: Sequence[str]) -> list[str]:
        """Before any read is authorised: Q-44's file verifies and reads as text with every column and the verdict rows
        of each design and response beside; each design's registered gate row is one row a shift at 0 %, the placement
        off, with the columns 9.1 items 6 and 8 read."""
        out = []
        try:
            f = self.q44()
        except Exception as exc:                          # noqa: BLE001 -- any failure here is a refusal before reads
            return [f"Q-44's per-start file: {exc}"]
        miss = [c for c in R.START_COLS if c not in f.columns]
        if miss:
            out.append(f"Q-44's per-start file lacks {miss}")
        else:
            for d in designs:
                for resp in BESIDE:
                    if not ((f["design"] == d) & (f["arm"] == "verdict") & (f["response"] == resp)).any():
                        out.append(f"Q-44's per-start file has no {d} verdict {resp} rows")
        for d in designs:
            try:
                rows = self.base_gate_rows(d)
            except Exception as exc:                      # noqa: BLE001
                out.append(f"{d}'s registered gate rows: {exc}")
                continue
            if sorted(rows) != sorted(GATE_SHIFTS):
                out.append(f"{d}'s registered gate rows: shifts {sorted(rows)}, not {list(GATE_SHIFTS)}")
            for shift, r in rows.items():
                need = [c for _, c in (*GATE_READING, *GATE_DIVERGE)] + ["mean_payouts_per_path"]
                miss = [c for c in need if c not in r]
                if miss:
                    out.append(f"{d} {shift}'s registered gate row lacks {miss}")
        return out

    def base_gate_rows(self, design: str) -> dict[str, dict[str, Any]]:
        """The base's registered gate rows (`section` gate, 0 %, the placement off), one a shift, as `rc_screen.
        p14_beside` reads P-14's (read, never rerun); refused unless exactly one row a shift."""
        if design in self._base_gate:
            return self._base_gate[design]
        from propedge import RESULTS_DIR
        from propedge.reporting.results import read_result

        d = read_result(RESULTS_DIR / self.GATE_FILES[design])
        g = d[(d["section"].astype(str) == "gate") & np.isclose(d["enforcement_p"].astype(float), 0.0)
              & (d["placement"].astype(str) == "off")]
        out = {}
        for shift in GATE_SHIFTS:
            s = g[g["shift"].astype(str) == shift]
            if len(s) != 1:
                raise ValueError(f"{self.GATE_FILES[design]}: {len(s)} gate rows at 0 % for {shift}, not one")
            out[shift] = s.iloc[0].to_dict()
        self._base_gate[design] = out
        return out

    def jobs(self, design: str) -> dict[str, dict[str, Any]]:
        """U1's jobs for a design (`identity/user_beside_identity.py`'s `build`, its own identities refusing), built once
        an instance."""
        import user_beside_identity as UI

        from propedge import RESULTS_DIR

        if design in self._jobs:
            return self._jobs[design][0]
        jobs, c, probs = UI.build(RESULTS_DIR, design)
        if probs:
            raise Refused(f"{design}: the builder's own identities fail: {probs[:4]}")
        self._jobs[design] = (jobs, c, UI.u1_reference(RESULTS_DIR, [design]))
        return jobs

    def identity_problems(self, design: str, arm: str, outs: list[dict[str, Any]]) -> list[str]:
        import user_beside_identity as UI

        jobs, c, ref = self._jobs[design]
        return UI.u1_compare_outs(design, c, arm, outs, ref, len(jobs[arm]["blocks"]), self.starts)

    def ladder_problems(self, design: str, response: str, outs: list[dict[str, Any]]) -> list[str]:
        """Q-44's `results/user_beside_starts.csv` rows for the design, the verdict arm and the response, start for
        start, every column that file writes, at its precision (money to the cent): the file read as text (R4)."""
        f = self.q44()
        theirs = f[(f["design"] == design) & (f["arm"] == "verdict") & (f["response"] == response)]
        mine = R.rounded(R.start_table(design, "verdict", response, outs))
        return q44_problems(mine, theirs, f"{design} {response}", all_starts=self.starts is None)

    def _gate_inputs(self, design: str) -> dict[str, Any]:
        if design in self._gate:
            return self._gate[design]
        import a3_brk30 as B
        import a3_brk30_cb20 as C
        import atlas_a3 as A
        import rc_screen as S
        import score_fv3_grid as gf
        import stage2_identity as SI

        if design == "p14":
            I = S.inputs()
            L = I["L"]
            t, days = B.cell_trades(L)
            seed, gap, budget = S.SEED, S.STRICT_GAP, S.BUDGET
        else:
            import rc150_dev_test as P
            import rc_dev_test as D

            sp = P.SPEC
            I, b = sp.build()
            L = I["L"]
            t, days = b["cells"][sp.cell]["trades"], b["days"]
            if D.trades_hash(t) != sp.trades_sha256:
                raise Refused(f"P-16's trades hash is not the pinned {sp.trades_sha256}")
            seed, gap, budget = SI.P16_SEED, C.STRICT_GAP, C.BUDGET
        cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
        keys = B.rrs(t)
        _, e_by, lb_by, _, _ = A.bounds(t, days, keys, cfg)
        blocks, n_used = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
        if n_used != len(t):
            raise Refused("the blocks hold a different number of trades")
        g = {"A": A, "I": I, "fcfg": fcfg, "tv": tv, "e_by": e_by, "lb_by": lb_by, "blocks": blocks, "seed": seed,
             "gap": gap, "budget": budget, "cap": B.capacity(t, fcfg)}
        self._gate[design] = g
        return g

    def gate_call(self, design: str, cell: str, twin: bool) -> dict[str, Any]:
        import fv3d_lever_test as lt
        import portfolio_stage as ps

        g = self._gate_inputs(design)
        fcfg = g["fcfg"]
        blocks, e_by, lb_by = g["blocks"], g["e_by"], g["lb_by"]
        if twin:                                         # the zero-edge twin, as atlas_a3.campaign builds it
            fr = float(fcfg["state_policy"]["fresh"]["funded_rr"])
            blocks = ps.zero_edge_blocks(blocks, e_by, fr)
            e_by = lb_by = {k: 0.0 for k in g["e_by"]}
        sink: list[dict] = []
        pc = fcfg["portfolio"]
        inner = ps.composed_hook({"margin": float(pc["margin"]), "block_days": int(pc["block_days"])}, sink=sink)
        hook = lt.lever_hook(inner)
        label = f"{design}_{cell}{'_twin' if twin else ''}"
        ps._label(inner, label)
        kw = g["A"].gate_kwargs(blocks, fcfg, g["tv"], g["I"]["plan"], e_by, lb_by, hook, seed=g["seed"],
                                n_paths=self._n_paths, horizon=int(fcfg["gate"]["campaign"]["horizon_days"]),
                                capacity=g["cap"], levels=(0.0,), rtp=False, one_at_a_time=g["gap"],
                                purchase_budget=g["budget"])
        kw["protocol"] = PP.cell_protocol(kw["protocol"], cell)
        return {"kw": kw, "sink": sink, "label": label}

    @staticmethod
    def registered_paths_file(design: str) -> str:
        """The base's registered gate paths file (the vendored tree's `results/`): P-14's or P-16's."""
        import rc_screen as S
        import stage2_identity as SI

        return S.P14_PATHS if design == "p14" else SI.P16_PATHS

    def gate_pairing_rows(self, design: str, cell: str, twin: bool, g: dict[str, Any]) -> list[dict[str, Any]]:
        """The cell's paths (its hook's sink) against the base's registered gate paths, path for path (the same seed,
        so the same day draws): each `zero_edge_decomposition.PATH_COLS` column's mean over paths, the cell's, the
        base's and their difference, point and bound; the twin against the registered `zero_edge_twin` run on the point
        arm (its bound arm is the same paths at e = lb = 0)."""
        import zero_edge_decomposition as zd

        from propedge import RESULTS_DIR
        from propedge.reporting.results import read_result

        rows = []
        mine = pd.DataFrame([r for r in g["sink"] if r.get("run") == g["label"]
                             and float(r.get("enforcement_p", 0.0)) == 0.0])
        ref = read_result(RESULTS_DIR / self.registered_paths_file(design))
        theirs_run = "zero_edge_twin" if twin else "gate"
        for shift in (("point",) if twin else ("point", "lower_bound")):
            a = mine[mine["shift"] == shift].sort_values("path").reset_index(drop=True) if len(mine) else mine
            b = ref[(ref["run"].astype(str) == theirs_run) & (ref["shift"].astype(str) == shift)
                    & np.isclose(ref["enforcement_p"].astype(float), 0.0)].sort_values("path").head(len(a))
            b = b.reset_index(drop=True)
            for col in zd.PATH_COLS:
                if col not in a:
                    continue
                x = pd.to_numeric(a[col], errors="coerce").to_numpy(float)
                k = dict(section="gate", part="pairing", design=design, cell=cell, mode="declared", block=shift,
                         measure=col, n=int(len(a)), note="the zero-edge twin" if twin else "")
                rows.append(_row(**k, stat="cell_mean", value=float(np.nanmean(x)) if x.size else np.nan))
                if len(b) == len(a) and col in b and len(a):
                    y = pd.to_numeric(b[col], errors="coerce").to_numpy(float)
                    rows += [_row(**k, stat="base_registered_mean", value=float(np.nanmean(y))),
                             _row(**k, stat="cell_less_base_mean", value=float(np.nanmean(x - y)))]
                else:
                    rows.append(_row(**k, stat="base_registered_mean", value=np.nan,
                                     note=f"no registered {theirs_run} run of {len(a)} paths to pair with"))
        return rows


__all__ = ["Refused", "Inputs", "RealInputs", "q44_problems", "BESIDE", "GATE_READING", "GATE_DIVERGE", "GATE_SHIFTS",
           "LADDER_TEXT", "ROW_KEYS", "NAN"]
