"""Wave 3.4 (the restart plan 4.3 a-b, f; CHARTER 3.3 (a), (b), (f), (g), 3.4, 3.5): the design search's space, its
space-filling sampler, the cell ledger that counts every cell proposed, and the one door through which a reading
reaches the surrogate (`extended.surrogate`) or the plateau check (`extended.plateau`).

    from extended import search_space as SS
    space = SS.from_lever_space(slots={"ny": 2})            # the Topstep $50K lever table, through its loader
    ledger = SS.CellLedger()
    designs = SS.Sampler(space, seed=S0, method="sobol").survey(256, ledger=ledger)
    ledger.counts()                                           # every cell proposed, the refused ones included

Synthetic objectives only at this commit: nothing here reads a bar, a walk, a trade or a result file, and nothing
writes one. **No rule value is typed**: every range of a space built by `from_lever_space` is read from
`extended.lever_space` (its bounds by key, its refusals, its latency cells, its session windows).

**A space** (`Space`) is an ordered tuple of dimensions (`Dim`): real (continuous, or on a lattice), integer (on a
lattice) or categorical. A categorical may be **dependent**: its cells are a function of the design drawn so far (the
latency cells of a component's source, `lever_space.latency_cells`: 5, 3 and 2 minutes, or one `None` cell for a
latency-free source). An integer may run **after** another (a window's last mark is at or after its first). A
dimension may be **active only if** another holds a value (a component slot's levers only when the slot is on);
inactive, it holds `None`. Levers held fixed (`fixed`) and levers refused by the loader (`refused`, with the
refusal's class) are carried beside the dimensions, never sampled.

**A component slot** (`Slot`; CHARTER 2's component, lever table T1-T5, S2): an offer window [first, last] on the
mark grid (T3's step) inside one session of the firm's day, with its source (T1), latency (T4), entry type (T5) and
reward-to-risk (S2). A design is a schedule of slots; its windows never collide within a session (CHARTER 3.5; the
same test as `components.Design`: sorted by first, each first after the previous last). **In the lever space the
window is an offset from its session's start, read per date** (E-231 (3): the asia, london and ny starts are their
local market times converted per date, `day_calendar.anchored_starts`): `Space.windows_on(design, day)` gives the
day's slots, and the offsets' bounds are the tightest over the search years' weekdays, so a window never leaves its
session on any of them.

**What a cell is refused for, at sampling** (`Space.check`, in this order; the first reason is recorded):
1. ``tier1`` -- conduct tier 1 (CHARTER 4; Stage 2 D-145): any setting naming a tier-1 practice (`TIER_ONE`), an
   overlap mode other than ``refused`` (the template's m-2: no design holding two positions of the user at once), or
   more than one firm in a design;
2. ``invalid`` -- a value outside its dimension's cells, bounds or lattice, or an inactive dimension holding a value;
3. ``collision`` -- two windows that collide;
4. ``session`` -- a declared source-session rule (`from_lever_space`: RL3's tickets go live at 09:00, so an RL3
   window holds that slot);
5. ``rule`` -- a combination no verified rule settles (`lever_space.check_design`: Back2Funded under the No
   Activation Fee path, a latency off its source's cells), read from the record each time.
A refused cell is recorded in the ledger with its class and reason and is never returned as a design.

**The sampler** (`Sampler`) is seeded explicitly (no default seed) and reproducible: a scrambled Sobol sequence
(`method="sobol"`, drawn in power-of-two blocks and used in order) or a Latin hypercube (`"lhs"`, one block of the
remaining size at a time) over the unit cube, one coordinate a dimension, decoded dimension by dimension. A
categorical's coordinate picks its cell by equal strata (floor(u m)), so its marginal is stratified by the sequence's
own one-dimensional balance; `cross=` crosses chosen static categoricals in full instead, each combination with its
own stream. Streams are children of the seed (`numpy.random.SeedSequence(seed, spawn_key=...)`), never the seed plus
an offset (E-171).

**The cell ledger** (`CellLedger`) counts every cell the sampler, the round proposer or the plateau check proposes,
refused ones included, with its role (``survey``, ``round-<i>``, ``plateau``), its seed, its status and reason, and
the latency of every active component (every L tried counted, CHARTER 3.3 (g)). It holds designs only, never a reading.
`variant_rows` gives the rows for the variants ledger (`results/variants.jsonl`), which only a clean run writes.

**Readings** (`Reading`, `admit`): a design's composite (or another measure) read on declared history blocks and coin
seeds. `admit` is the one door: it refuses anything not tagged ``search``, any block touching the held-out years
(2024-01-02 on, E-208; `extended.reader`'s blocks) or the confirmation window, a non-finite value, and anything that is
not a `Reading` (a surrogate's prediction is never a reading). The held-out years are never read by a search
(CHARTER 3.6 (a), E-221 O-1).
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import warnings
from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Callable, Iterable, Mapping, Sequence

import numpy as np
from scipy.stats import qmc

from extended import reader as R

TASK = "Wave 3.4"
REAL, INT, CAT = "real", "int", "cat"
KINDS = (REAL, INT, CAT)
OFF, ON = "off", "on"
METHODS = ("sobol", "lhs")
SEARCH_TAG = "search"
#: the refusal classes, in the order `Space.check` applies them
REFUSAL_CLASSES = ("tier1", "invalid", "collision", "session", "rule")
#: settings that are conduct tier 1 by definition (CHARTER 4; Stage 2 D-145): never sampled, whatever a space holds
TIER_ONE = frozenset({
    "hedge_across_accounts", "hedge_across_firms", "opposite_positions", "copy_trade_across_accounts",
    "sim_fill_exploit", "auto_breakeven_sim_fills", "max_size_into_major_news", "conceal_pattern",
})
OVERLAP_KEY, OVERLAP_REFUSED = "overlap", "refused"
FIRMS_KEY = "firms"
#: the component levers of a slot (lever table T1, T3-T5, S2); every other searched lever is the design's
SLOT_LEVERS = ("T1", "T3", "T4", "T5", "S1", "S2")
#: RL3's entry is its ticket (lever table T5: "for RL3 it is the same-bar pair of fade limit and break stop", E-204)
TICKET = "ticket"
#: the unit-cube coordinate a dimension takes when inactive (any value: an inactive dimension ignores it)
_INACTIVE_U = 0.5


class SpaceRefused(ValueError):
    """A space, a slot or a sampler request this module cannot stand behind."""


class HeldOutInput(RuntimeError):
    """An input tagged held-out, touching the held-out years, or not a search-year reading: refused (CHARTER
    3.6 (a))."""


# ------------------------------------------------------------------------------------------------ dimensions


@dataclass(frozen=True)
class Dim:
    """One coordinate of the space. `values`: a categorical's static cells; `cells`: a dependent categorical's cells
    from the design so far, `labels` every value it can take; `after`: an integer starting at another's value;
    `active_if`: (name, value) the dimension is active under; `lever`: the lever table's id; `slot`: its slot."""

    name: str
    kind: str
    lo: float | None = None
    hi: float | None = None
    step: float | None = None
    values: tuple[Any, ...] = ()
    labels: tuple[Any, ...] = ()
    cells: Callable[[Mapping[str, Any]], tuple[Any, ...]] | None = None
    after: str | None = None
    active_if: tuple[str, Any] | None = None
    lever: str = ""
    slot: str | None = None

    def __post_init__(self) -> None:
        if self.kind not in KINDS:
            raise SpaceRefused(f"dimension {self.name}: unknown kind {self.kind!r}")
        if self.kind == CAT:
            if self.cells is None and not self.values:
                raise SpaceRefused(f"dimension {self.name}: a categorical has cells")
            if self.cells is not None and not self.labels:
                raise SpaceRefused(f"dimension {self.name}: a dependent categorical names every value it can take")
        else:
            if self.lo is None or self.hi is None or not (math.isfinite(self.lo) and math.isfinite(self.hi)):
                raise SpaceRefused(f"dimension {self.name}: finite bounds")
            if self.hi < self.lo:
                raise SpaceRefused(f"dimension {self.name}: hi below lo")
            if self.kind == INT and (self.step is None or self.step <= 0):
                raise SpaceRefused(f"dimension {self.name}: an integer has a positive lattice step")
            if self.step is not None and self.step <= 0:
                raise SpaceRefused(f"dimension {self.name}: a lattice step is positive")

    def cells_of(self, design: Mapping[str, Any]) -> tuple[Any, ...]:
        return tuple(self.cells(design)) if self.cells is not None else tuple(self.values)

    def every_value(self) -> tuple[Any, ...]:
        return tuple(self.labels) if self.cells is not None else tuple(self.values)

    def lattice(self, lo: float) -> int:
        """How many lattice points from `lo` to `hi`."""
        return int(math.floor((float(self.hi) - lo) / float(self.step) + 1e-9)) + 1


@dataclass(frozen=True)
class Slot:
    """A component slot: its session and the first and last marks a window may take there (inclusive), on `step`."""

    name: str
    session: str
    lo: int
    hi: int
    step: int

    def __post_init__(self) -> None:
        if not (0 <= self.lo <= self.hi) or self.step <= 0 or (self.hi - self.lo) % self.step:
            raise SpaceRefused(f"slot {self.name}: marks lo <= hi on the step, got {self.lo}, {self.hi}, {self.step}")


def slot_dim(slot: str, key: str) -> str:
    return f"{slot}.{key}"


@dataclass(frozen=True)
class Constraint:
    """A declared rule a cell must meet: `fn(design)` returns a reason (refused) or None; `cls` its refusal class."""

    name: str
    cls: str
    fn: Callable[[Mapping[str, Any]], str | None]


def design_id(design: Mapping[str, Any]) -> str:
    """A design's id: the sha256 of its canonical JSON (sorted keys), sixteen hex digits."""
    blob = json.dumps({k: design[k] for k in sorted(design)}, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


# ------------------------------------------------------------------------------------------------ the space


@dataclass(frozen=True)
class Space:
    dims: tuple[Dim, ...]
    fixed: Mapping[str, Any] = field(default_factory=dict)
    refused: Mapping[str, str] = field(default_factory=dict)
    slots: tuple[Slot, ...] = ()
    constraints: tuple[Constraint, ...] = ()
    lever_checks: bool = False
    firm: str = ""
    #: a trading day's session starts (slots after the reopen), when the slots' windows are offsets from them (the
    #: lever space: E-231 (3), anchored per date); None when the windows are absolute (a synthetic space)
    starts: Callable[[date], Mapping[str, int]] | None = None
    #: the dates the offsets' bounds hold on (every window inside its session on each)
    days: tuple[date, ...] = ()

    def __post_init__(self) -> None:
        names = [d.name for d in self.dims]
        if len(set(names)) != len(names):
            raise SpaceRefused(f"dimension names repeat: {names}")
        seen: set[str] = set()
        for d in self.dims:
            for ref in ([d.after] if d.after else []) + ([d.active_if[0]] if d.active_if else []):
                if ref not in seen:
                    raise SpaceRefused(f"dimension {d.name} refers to {ref!r}, which is not an earlier dimension")
            seen.add(d.name)
        if not self.dims:
            raise SpaceRefused("a space has at least one dimension")
        for c in self.constraints:
            if c.cls not in REFUSAL_CLASSES:
                raise SpaceRefused(f"constraint {c.name}: unknown class {c.cls!r}")
        if self.fixed.get(OVERLAP_KEY, OVERLAP_REFUSED) != OVERLAP_REFUSED:
            raise SpaceRefused("overlap is refused until the template defines it (m-2, E-210)")
        object.__setattr__(self, "_by_name", {d.name: d for d in self.dims})

    # -- access
    @property
    def d(self) -> int:
        return len(self.dims)

    def dim(self, name: str) -> Dim:
        return self._by_name[name]                                     # type: ignore[attr-defined]

    def names(self) -> tuple[str, ...]:
        return tuple(d.name for d in self.dims)

    def active(self, dim: Dim, design: Mapping[str, Any]) -> bool:
        return dim.active_if is None or design.get(dim.active_if[0]) == dim.active_if[1]

    def latencies(self, design: Mapping[str, Any]) -> tuple[Any, ...]:
        """The latency of every active component (the T4 dimensions), in slot order."""
        return tuple(design.get(d.name) for d in self.dims if d.lever == "T4" and self.active(d, design))

    # -- decoding
    def decode(self, u: Sequence[float]) -> dict[str, Any]:
        """The design at unit point `u` (one coordinate a dimension, in [0, 1))."""
        if len(u) != self.d:
            raise SpaceRefused(f"a unit point has {self.d} coordinates, got {len(u)}")
        out: dict[str, Any] = {}
        for d, x in zip(self.dims, u):
            x = min(max(float(x), 0.0), np.nextafter(1.0, 0.0))
            if not self.active(d, out):
                out[d.name] = None
            elif d.kind == CAT:
                cells = d.cells_of(out)
                out[d.name] = cells[min(int(x * len(cells)), len(cells) - 1)]
            else:
                lo = float(out[d.after]) if d.after else float(d.lo)
                if d.step is None:
                    out[d.name] = lo + x * (float(d.hi) - lo)
                else:
                    n = d.lattice(lo)
                    v = lo + min(int(x * n), n - 1) * float(d.step)
                    out[d.name] = int(round(v)) if d.kind == INT else v
        return out

    def unit_of(self, design: Mapping[str, Any]) -> np.ndarray:
        """A unit point that decodes to `design` (each coordinate at its cell's centre); inactive dimensions at 0.5."""
        u = np.full(self.d, _INACTIVE_U)
        for j, d in enumerate(self.dims):
            v = design[d.name]
            if v is None:
                continue
            if d.kind == CAT:
                cells = d.cells_of(design)
                u[j] = (cells.index(v) + 0.5) / len(cells)
            else:
                lo = float(design[d.after]) if d.after else float(d.lo)
                if d.step is None:
                    u[j] = 0.5 if d.hi == lo else (float(v) - lo) / (float(d.hi) - lo)
                else:
                    n = d.lattice(lo)
                    u[j] = (round((float(v) - lo) / float(d.step)) + 0.5) / n
        return np.clip(u, 0.0, np.nextafter(1.0, 0.0))

    # -- checking
    def _tier_one(self, design: Mapping[str, Any]) -> str | None:
        for k, v in list(design.items()) + list(self.fixed.items()):
            vals = v if isinstance(v, (tuple, list)) else (v,)
            for x in vals:
                if isinstance(x, str) and x in TIER_ONE:
                    return f"{k} = {x!r} is conduct tier 1 (CHARTER 4; Stage 2 D-145)"
        ov = design.get(OVERLAP_KEY, self.fixed.get(OVERLAP_KEY, OVERLAP_REFUSED))
        if ov != OVERLAP_REFUSED:
            return f"overlap {ov!r}: a design holding two positions of the user at once is refused (m-2, E-210)"
        firms = design.get(FIRMS_KEY, self.fixed.get(FIRMS_KEY, 1))
        if not isinstance(firms, int) or firms != 1:
            return f"{firms!r} firms: a design is one firm's (one position at a time across a firm, D-429)"
        return None

    def _invalid(self, design: Mapping[str, Any]) -> str | None:
        extra = sorted(set(design) - set(self.names()) - {OVERLAP_KEY, FIRMS_KEY})
        missing = [n for n in self.names() if n not in design]
        if extra or missing:
            return f"keys off the space: extra {extra}, missing {missing}"
        for d in self.dims:
            v = design[d.name]
            if not self.active(d, design):
                if v is not None:
                    return f"{d.name} is inactive and holds {v!r}"
                continue
            if d.kind == CAT:
                if v not in d.cells_of(design):
                    return f"{d.name} = {v!r} is not one of its cells {d.cells_of(design)}"
                continue
            if v is None:
                return f"{d.name} is active and holds nothing"
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(float(v)):
                return f"{d.name} = {v!r} is not a finite number"
            lo = float(design[d.after]) if d.after else float(d.lo)
            if not lo - 1e-9 <= float(v) <= float(d.hi) + 1e-9:
                return f"{d.name} = {v!r} outside [{lo}, {d.hi}]"
            if d.step is not None:
                k = (float(v) - lo) / float(d.step)
                if abs(k - round(k)) > 1e-6:
                    return f"{d.name} = {v!r} is off its lattice (step {d.step} from {lo})"
            if d.kind == INT and not isinstance(v, int):
                return f"{d.name} = {v!r} is not an integer"
        if self.slots and not self.windows(design):
            return "no component is on: a design has at least one"
        return None

    def windows(self, design: Mapping[str, Any]) -> list[tuple[str, int, int]]:
        """The active slots' windows (slot, first, last) as the design holds them (offsets from the session's start
        when `starts` is set), sorted by first."""
        out = []
        for s in self.slots:
            if design.get(slot_dim(s.name, "on")) == ON:
                out.append((s.name, int(design[slot_dim(s.name, "first")]), int(design[slot_dim(s.name, "last")])))
        return sorted(out, key=lambda w: (w[1], w[2], w[0]))

    def windows_on(self, design: Mapping[str, Any], day: date) -> list[tuple[str, str, int, int]]:
        """The active windows on trading day `day`, (slot, session, first, last) in slots after the reopen: each
        offset read from that date's session start (`starts`), sorted by first."""
        st = self.starts(day) if self.starts is not None else None
        sess = {s.name: s.session for s in self.slots}
        out = []
        for name, a, b in self.windows(design):
            base = 0 if st is None else int(st[sess[name]])
            out.append((name, sess[name], base + a, base + b))
        return sorted(out, key=lambda w: (w[2], w[3], w[0]))

    def _collision(self, design: Mapping[str, Any]) -> str | None:
        sess = {s.name: s.session for s in self.slots}
        by: dict[str, list[tuple[str, int, int]]] = {}
        for w in self.windows(design):                  # within one session: offsets share that session's start
            by.setdefault(sess[w[0]], []).append(w)
        for ws in by.values():
            for x, y in zip(ws, ws[1:]):
                if y[1] <= x[2]:
                    return f"windows of {x[0]} [{x[1]}, {x[2]}] and {y[0]} [{y[1]}, {y[2]}] collide (CHARTER 3.5)"
        return None

    def _rules(self, design: Mapping[str, Any]) -> str | None:
        from extended import lever_space as LS
        from extended.firm_terms import UnverifiedTerm

        glob = {d.lever: design[d.name] for d in self.dims if d.slot is None and d.lever}
        settings = [glob] + [{"T1": design.get(slot_dim(s.name, "T1")), "T4": design.get(slot_dim(s.name, "T4"))}
                             for s in self.slots if design.get(slot_dim(s.name, "on")) == ON]
        for st in settings:
            try:
                LS.check_design(st)
            except (LS.LeverRefused, UnverifiedTerm) as e:
                return f"{type(e).__name__}: {e}"
        return None

    def check(self, design: Mapping[str, Any]) -> tuple[str, str] | None:
        """(class, reason) of the first rule the design breaks, or None (the module docstring's order)."""
        why = self._tier_one(design)
        if why:
            return "tier1", why
        why = self._invalid(design)
        if why:
            return "invalid", why
        why = self._collision(design)
        if why:
            return "collision", why
        for c in self.constraints:
            if c.cls == "session":
                why = c.fn(design)
                if why:
                    return c.cls, f"{c.name}: {why}"
        if self.lever_checks:
            why = self._rules(design)
            if why:
                return "rule", why
        for c in self.constraints:
            if c.cls != "session":
                why = c.fn(design)
                if why:
                    return c.cls, f"{c.name}: {why}"
        return None


# ------------------------------------------------------------------------------------------------ the cell ledger


@dataclass
class CellLedger:
    """Every cell proposed -- by the survey, a round or a plateau check -- refused ones included (CHARTER 3.3 (f),
    (g); the template's section 13). Designs only: a reading never enters it."""

    rows: list[dict[str, Any]] = field(default_factory=list)

    def record(self, space: Space, design: Mapping[str, Any], *, role: str, seed: int,
               refusal: tuple[str, str] | None, round_index: int | None = None) -> dict[str, Any]:
        if not isinstance(seed, (int, np.integer)) or isinstance(seed, bool):
            raise SpaceRefused("a cell's seed is an explicit integer")
        if not role:
            raise SpaceRefused("a cell has a role")
        row = {"cell": len(self.rows), "id": design_id(design), "role": role, "seed": int(seed),
               "round": round_index, "status": "refused" if refusal else "proposed",
               "class": refusal[0] if refusal else "", "reason": refusal[1] if refusal else "",
               "latencies": [str(x) for x in space.latencies(design)], "design": dict(design)}
        self.rows.append(row)
        return row

    def counts(self) -> dict[str, Any]:
        rows = self.rows
        return {"cells": len(rows),
                "proposed": sum(r["status"] == "proposed" for r in rows),
                "refused": sum(r["status"] == "refused" for r in rows),
                "distinct": len({r["id"] for r in rows}),
                "by_role": dict(Counter(r["role"] for r in rows)),
                "by_class": dict(Counter(r["class"] for r in rows if r["status"] == "refused")),
                "latency": dict(Counter(x for r in rows for x in r["latencies"]))}

    def variant_rows(self, prereg_id: str) -> list[dict[str, Any]]:
        """The rows for `VariantCounter.record` (prereg id, params, seed, label): written only by a clean run."""
        return [{"prereg_id": prereg_id, "params": r["design"], "seed": r["seed"],
                 "label": f"{r['role']}:{r['status']}" + (f":{r['class']}" if r["class"] else "")} for r in self.rows]


# ------------------------------------------------------------------------------------------------ the sampler


def child_rng(seed: int, *key: int) -> np.random.Generator:
    """A generator for one stream of `seed`: a child by spawn key, never the seed plus an offset (E-171)."""
    if not isinstance(seed, (int, np.integer)) or isinstance(seed, bool):
        raise SpaceRefused("a seed is an explicit integer")
    return np.random.default_rng(np.random.SeedSequence(int(seed), spawn_key=tuple(int(k) for k in key)))


#: spawn-key heads, one per stream kind of this module and its users (fixed; a new stream takes a new head)
STREAM_SURVEY, STREAM_POOL, STREAM_LOCAL, STREAM_FIT, STREAM_PLATEAU = 1, 2, 3, 4, 5


class UnitPoints:
    """Unit points in order: a scrambled Sobol sequence (blocks doubling the total, so every drawn total is a power of
    two, used in order), or Latin hypercubes, each of the size still wanted."""

    def __init__(self, method: str, d: int, rng: np.random.Generator):
        if method not in METHODS:
            raise SpaceRefused(f"unknown method {method!r}; one of {METHODS}")
        self.method, self.d, self.rng = method, int(d), rng
        self.eng = qmc.Sobol(self.d, scramble=True, seed=rng) if method == "sobol" else None

    def next(self, wanted: int) -> np.ndarray:
        if self.eng is None:
            return qmc.LatinHypercube(self.d, seed=self.rng).random(max(int(wanted), 1))
        if self.eng.num_generated == 0:
            return self.eng.random_base2(max(4, int(math.ceil(math.log2(max(int(wanted), 1))))))
        return self.eng.random(min(int(self.eng.num_generated), 2 ** 14))


class Sampler:
    """The survey's space-filling sampler (the module docstring). `seed` is explicit; `method` 'sobol' or 'lhs'."""

    def __init__(self, space: Space, *, seed: int, method: str):
        if method not in METHODS:
            raise SpaceRefused(f"unknown method {method!r}; one of {METHODS}")
        child_rng(seed)                                                   # refuses a seed that is not an integer
        self.space, self.seed, self.method = space, int(seed), method

    def _stream(self, combo: int, fixed: Mapping[int, float], n: int, ledger: CellLedger, role: str,
                max_proposals: int, round_index: int | None) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        tried = 0
        points = UnitPoints(self.method, self.space.d, child_rng(self.seed, STREAM_SURVEY, combo))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=UserWarning)     # Sobol's balance note on a used prefix
            while len(out) < n:
                for u in points.next(n - len(out)):
                    if len(out) >= n:
                        break
                    if tried >= max_proposals:
                        raise SpaceRefused(f"{tried} cells proposed for {n} designs: more than the cap "
                                           f"{max_proposals} -- the space refuses too much to fill")
                    u = np.array(u, dtype=float)
                    for j, x in fixed.items():
                        u[j] = x
                    design = self.space.decode(u)
                    refusal = self.space.check(design)
                    ledger.record(self.space, design, role=role, seed=self.seed, refusal=refusal,
                                  round_index=round_index)
                    tried += 1
                    if refusal is None:
                        out.append(design)
        return out

    def survey(self, n: int, *, ledger: CellLedger, role: str = "survey", max_proposals: int | None = None,
               cross: Sequence[str] = (), round_index: int | None = None) -> list[dict[str, Any]]:
        """`n` designs that pass every check (per combination of `cross`'s categoricals, crossed in full, when given),
        every cell proposed recorded in `ledger`."""
        if int(n) <= 0:
            raise SpaceRefused("a survey has at least one design")
        cap = int(max_proposals) if max_proposals is not None else 64 * int(n)
        if not cross:
            return self._stream(0, {}, int(n), ledger, role, cap, round_index)
        idx = []
        for name in cross:
            d = self.space.dim(name)
            if d.kind != CAT or d.cells is not None or d.active_if is not None:
                raise SpaceRefused(f"{name}: only a static, always-active categorical is enumerated")
            idx.append((self.space.names().index(name), d.values))
        out: list[dict[str, Any]] = []
        for c, combo in enumerate(itertools.product(*[vals for _, vals in idx])):
            fixed = {j: (vals.index(v) + 0.5) / len(vals) for (j, vals), v in zip(idx, combo)}
            out += self._stream(c + 1, fixed, int(n), ledger, role, cap, round_index)
        return out


# ------------------------------------------------------------------------------------------------ the lever space


def _overnight_allowed() -> bool:
    from extended import triggers as T

    return T.overnight_allowed()


def session_spans(day: date, ny_boundary: int | None = None) -> dict[str, tuple[int, int]]:
    """Trading day `day`'s sessions as [start, end) in slots after the reopen (`lever_space.session_windows(day)`,
    anchored per date, E-231 (3)), each end clipped to one past the firm's last new entry. Until T2b (the NY AM / NY
    PM boundary) is declared, NY is one session, `ny`; given the boundary (a slot), `ny_am` and `ny_pm`."""
    from extended import lever_space as LS

    td = LS.trading_day()
    step = int(LS.bounds("T3").step)
    sw = LS.session_windows(day)
    spans = {k: v for k, v in sw.items() if k not in ("ny_am", "ny_pm")}
    ny = (sw["ny_am"][0], sw["ny_pm"][1])
    if ny_boundary is None:
        spans["ny"] = ny
    else:
        b = int(ny_boundary)
        if not ny[0] < b < ny[1] or b % step:
            raise SpaceRefused(f"the NY boundary {b} lies off the mark grid or outside NY {ny} on {day}")
        spans["ny_am"], spans["ny_pm"] = (ny[0], b), (b, ny[1])
    return {k: (int(a), min(int(e), int(td["last_entry_offset"]) + 1)) for k, (a, e) in spans.items()}


def search_days() -> tuple[date, ...]:
    """The weekdays of the search years (`day_calendar.SEARCH_START` to `SEARCH_END`, E-208): calendar dates only."""
    from extended import day_calendar as DC
    from extended import lever_space as LS

    return tuple(LS.trading_dates(DC.SEARCH_START, DC.SEARCH_END))


def session_slots(ny_boundary: int | None = None, days: Sequence[date] | None = None
                  ) -> dict[str, tuple[int, int, int]]:
    """Each session's window offsets (first, last, step) from its start, on T3's mark step: from 0 to the last mark
    that keeps a window inside the session **on every one of `days`** (default: the search years' weekdays), so a
    window read on any of those dates never leaves its session. A session start off the mark grid is refused."""
    from extended import lever_space as LS

    step = int(LS.bounds("T3").step)
    days = tuple(days) if days is not None else search_days()
    if not days:
        raise SpaceRefused("the offsets' bounds hold on at least one day")
    room: dict[str, int] = {}
    for d in days:
        for name, (a, e) in session_spans(d, ny_boundary).items():
            if a % step:
                raise SpaceRefused(f"session {name} starts at {a} on {d}, off the {step}-minute mark grid")
            room[name] = min(room.get(name, e - 1 - a), e - 1 - a)
    return {name: (0, (r // step) * step, step) for name, r in room.items() if r >= 0}


def _entry_cells(source: str) -> tuple[str, ...]:
    from extended import lever_space as LS

    return (TICKET,) if source == "rl3" else tuple(LS.bounds("T5").values)


def _rl3_live(slot: str, session_starts: Sequence[int]) -> Callable[[Mapping[str, Any]], str | None]:
    """RL3's window holds its live slot (09:00 CT) on every date: its offsets from each of the session's starts."""
    from extended import triggers as T

    live = int(T.LIVE_0900)
    offs = sorted({live - int(a) for a in session_starts})

    def fn(design: Mapping[str, Any]) -> str | None:
        if design.get(slot_dim(slot, "on")) == ON and design.get(slot_dim(slot, "T1")) == "rl3":
            a, b = int(design[slot_dim(slot, "first")]), int(design[slot_dim(slot, "last")])
            if not all(a <= o <= b for o in offs):
                return f"an RL3 window holds its live slot {live} (09:00, offsets {offs}); got [{a}, {b}]"
        return None

    return fn


def from_lever_space(*, slots: Mapping[str, int], ny_boundary: int | None = None,
                     days: Sequence[date] | None = None) -> Space:
    """The Topstep $50K space from `extended.lever_space`: every searched lever whose range loads, as a dimension of
    the design (the account-policy and dollar-risk levers) or of each component slot (T1, T3-T5, S2); every declared
    lever that loads, fixed; every refusal carried by its class. `slots` names how many component slots each session
    holds (the search declaration's choice; a session absent holds none). A slot's window levers are **offsets from
    its session's start, read per date** (`Space.windows_on`; the starts anchored to local market times, E-231 (3)),
    bounded so the window stays inside its session on every one of `days` (default: the search years' weekdays). An
    overnight session's slot holds no source until H2's row (`triggers.overnight_allowed`), so it is always off and
    carried as refused."""
    from extended import lever_space as LS
    from extended import triggers as T

    days = tuple(days) if days is not None else search_days()
    sess = session_slots(ny_boundary, days)
    spans_by_day = {d: session_spans(d, ny_boundary) for d in days}
    for name in slots:
        if name not in sess:
            raise SpaceRefused(f"unknown session {name!r}; this firm's are {sorted(sess)}")
    loaded = LS.space()
    refused = dict(LS.refusals())
    fixed = {k: r.values for k, r in loaded.items() if LS.LEVERS[k].cls == LS.FIXED}
    fixed[OVERLAP_KEY] = OVERLAP_REFUSED
    fixed[FIRMS_KEY] = 1
    dims: list[Dim] = []
    for k, r in loaded.items():
        lv = LS.LEVERS[k]
        if lv.cls != LS.SEARCHED or k in SLOT_LEVERS or k == "T2":
            continue
        if r.kind == "choices":
            dims.append(Dim(k, CAT, values=tuple(r.values), lever=k))
        elif r.kind == "interval":
            integral = r.step is not None and all(float(x).is_integer() for x in (r.lo, r.hi, r.step))
            dims.append(Dim(k, INT if integral else REAL, lo=int(r.lo) if integral else float(r.lo),
                            hi=int(r.hi) if integral else float(r.hi), step=r.step, lever=k))
        else:
            raise SpaceRefused(f"{k}: a searched lever of kind {r.kind!r}")
    sources = tuple(loaded["T1"].values)
    lat_labels = tuple(dict.fromkeys(x for s in sources for x in LS.latency_cells(s)))
    ent_labels = tuple(dict.fromkeys(x for s in sources for x in _entry_cells(s)))
    overnight = not _overnight_allowed()
    rth = int(T.RTH_OPEN)
    slot_objs: list[Slot] = []
    constraints: list[Constraint] = []
    for name, count in slots.items():
        first, last, step = sess[name]
        for i in range(int(count)):
            sn = f"{name}.{i}"
            slot_objs.append(Slot(sn, name, first, last, step))
            night = all(sp[name][1] <= rth for sp in spans_by_day.values())
            on_cells = (OFF,) if (night and overnight) else (OFF, ON)
            if night and overnight:
                refused[sn] = "OvernightRefused"
            srcs = tuple(s for s in sources if s != "rl3" or name in ("ny", "ny_am"))
            act = (slot_dim(sn, "on"), ON)
            dims.append(Dim(slot_dim(sn, "on"), CAT, values=on_cells, lever="T2", slot=sn))
            dims.append(Dim(slot_dim(sn, "T1"), CAT, values=srcs, active_if=act, lever="T1", slot=sn))
            src_key = slot_dim(sn, "T1")
            dims.append(Dim(slot_dim(sn, "T4"), CAT, labels=lat_labels, active_if=act, lever="T4", slot=sn,
                            cells=lambda d, k=src_key: LS.latency_cells(d[k])))
            dims.append(Dim(slot_dim(sn, "T5"), CAT, labels=ent_labels, active_if=act, lever="T5", slot=sn,
                            cells=lambda d, k=src_key: _entry_cells(d[k])))
            dims.append(Dim(slot_dim(sn, "first"), INT, lo=first, hi=last, step=step, active_if=act, lever="T3",
                            slot=sn))
            dims.append(Dim(slot_dim(sn, "last"), INT, lo=first, hi=last, step=step, after=slot_dim(sn, "first"),
                            active_if=act, lever="T3", slot=sn))
            if "S2" in loaded:
                r = loaded["S2"]
                dims.append(Dim(slot_dim(sn, "S2"), REAL, lo=float(r.lo), hi=float(r.hi), active_if=act,
                                lever="S2", slot=sn))
            if "rl3" in srcs:
                constraints.append(Constraint(f"{sn} rl3 live", "session",
                                              _rl3_live(sn, [sp[name][0] for sp in spans_by_day.values()])))

    def starts(day: date) -> dict[str, int]:
        return {k: a for k, (a, _) in session_spans(day, ny_boundary).items()}

    return Space(tuple(dims), fixed=fixed, refused=refused, slots=tuple(slot_objs), constraints=tuple(constraints),
                 lever_checks=True, firm="topstep_50k", starts=starts, days=days)


# ------------------------------------------------------------------------------------------------ readings


@dataclass(frozen=True)
class Reading:
    """A design's measure read on declared history blocks ((start, end) ISO days) and coin seeds. `tag` 'search' is the
    only one admitted; `se` the reading's standard error over its seeds, if known."""

    design: Mapping[str, Any]
    value: float
    blocks: tuple[tuple[str, str], ...]
    seeds: tuple[int, ...]
    tag: str
    measure: str = "composite"
    se: float | None = None

    @property
    def id(self) -> str:
        return design_id(self.design)


def admit_one(r: Any) -> Reading:
    """The one door (the module docstring): the reading, or `HeldOutInput`."""
    if not isinstance(r, Reading):
        raise HeldOutInput(f"REFUSED: {type(r).__name__} is not a search-year reading (a prediction never is one)")
    tag = str(r.tag)
    low = tag.lower().replace("-", "").replace("_", "").replace(" ", "")
    if any(w in low for w in ("heldout", "judged", "holdout", "confirm")):
        raise HeldOutInput(f"REFUSED: a reading tagged {tag!r} is held-out: a search never reads the held-out years "
                           "(CHARTER 3.6 (a); E-208, E-221 O-1)")
    if tag != SEARCH_TAG:
        raise HeldOutInput(f"REFUSED: a reading tagged {tag!r}; only {SEARCH_TAG!r} is admitted")
    if not r.blocks:
        raise HeldOutInput("REFUSED: a reading names the search-year blocks it was read on")
    for b in r.blocks:
        if not (isinstance(b, tuple) and len(b) == 2):
            raise HeldOutInput(f"REFUSED: a block is (start, end), got {b!r}")
        try:
            got = R.blocks_of(b[0], b[1])                   # refuses the confirmation window and before 2020-01-02
        except (R.ReadRefused, ValueError, TypeError) as e:
            raise HeldOutInput(f"REFUSED: block {b!r}: {e}") from e
        if got != ("choice",):
            raise HeldOutInput(f"REFUSED: block {b[0]} to {b[1]} touches the held-out years ({got}; E-208): a search "
                               "reads the search years only")
    if not r.seeds or not all(isinstance(s, (int, np.integer)) and not isinstance(s, bool) for s in r.seeds):
        raise HeldOutInput("REFUSED: a reading names its coin seeds, as integers")
    if not math.isfinite(float(r.value)):
        raise HeldOutInput(f"REFUSED: a reading's value is finite, got {r.value!r}")
    if r.se is not None and not (math.isfinite(float(r.se)) and float(r.se) >= 0):
        raise HeldOutInput(f"REFUSED: a reading's standard error is finite and non-negative, got {r.se!r}")
    return r


def admit(readings: Iterable[Any]) -> list[Reading]:
    """Every reading through the one door, or the first refusal (nothing admitted)."""
    return [admit_one(r) for r in readings]


__all__ = ["TASK", "REAL", "INT", "CAT", "OFF", "ON", "METHODS", "SEARCH_TAG", "REFUSAL_CLASSES", "TIER_ONE",
           "SLOT_LEVERS", "TICKET", "SpaceRefused", "HeldOutInput", "Dim", "Slot", "slot_dim", "Constraint",
           "design_id", "Space", "CellLedger", "child_rng", "STREAM_SURVEY", "STREAM_POOL", "STREAM_LOCAL",
           "STREAM_FIT", "STREAM_PLATEAU", "UnitPoints", "Sampler", "session_spans", "search_days", "session_slots",
           "from_lever_space", "Reading",
           "admit_one", "admit"]
