"""Wave 3.4 (the restart plan 4.3 a-b, f; CHARTER 3.3 (a), (b), (f), (g), 3.4, 3.5): the design search's space, its
space-filling sampler, the cell ledger that counts every cell proposed, and the one door through which a reading
reaches the surrogate (`extended.surrogate`) or the plateau check (`extended.plateau`).

    from extended import search_space as SS
    space = SS.from_lever_space(slots={"ny_am": 1, "ny_pm": 1})   # the Topstep $50K lever table, its loader
    ledger = SS.CellLedger()
    designs = SS.Sampler(space, seed=S0, method="sobol").survey(256, ledger=ledger, protocol=PROTOCOL,
                                                                reread_seeds=REREAD, declaration_sha256=SHA)
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
refusal's class) are carried beside the dimensions, never sampled; so are the searched rows **held until wired**
(`held`, with the label `lever_space.HELD_UNTIL_WIRED` gives: A15 and A17 at their bases until an executor applies them,
the red team's m4), whose base value sits in `fixed`.

**A component slot** (`Slot`; CHARTER 2's component, lever table T1-T5, S2): an offer window [first, last] on the
mark grid (T3's step) inside one session of the firm's day, with its source (T1), latency (T4), entry type (T5) and
reward-to-risk (S2). A design is a schedule of slots; its windows never collide within a session (CHARTER 3.5; the
same test as `components.Design`: sorted by first, each first after the previous last). **In the lever space the
window is an offset from its session's start, read per date** (E-231 (3): the asia, london and ny starts are their
local market times converted per date, `day_calendar.anchored_starts`): `Space.windows_on(design, day)` gives the
day's slots, and the offsets' bounds are the tightest over the search years' weekdays, so a window never leaves its
session on any of them.

**Window levers are offsets from local anchors, by construction** (the red team's m-6, kept by the lead): a window
is an offset from its session's anchored start, bounded by the session's shortest span over the search years'
weekdays. So an absolute CT window that lies inside its session on only part of the year (London reaching 07:30 CT
outside the US/UK mismatch weeks, Asia reaching 00:55 CT on CST dates, the evening reaching 18:00 CT on CDT dates) is
legitimately excluded from a fixed design: a design means the same local window on every date.

**What a cell is refused for, at sampling** (`Space.check`, in this order; the first reason is recorded):
1. ``tier1`` -- conduct tier 1 (CHARTER 4; Stage 2 D-145): any setting naming a tier-1 practice (`TIER_ONE`, matched
   case-insensitively), an overlap mode other than ``refused`` (the template's m-2: no design holding two positions of
   the user at once), or a firm count other than the integer 1 (``True`` is refused). **Where tier 1 is really
   enforced** (m-5): on the real lever space no lever offers a tier-1 value, so the name list is a guard; what holds
   tier 1 there is the fixed ``overlap`` and ``firms`` values here and, downstream, `extended.triggers` and
   `extended.components` (the news, BLS and FOMC windows, one position at a time across a firm, the user's book
   refusing opposite positions);
2. ``invalid`` -- a value outside its dimension's cells, bounds or lattice, or an inactive dimension holding a value;
3. ``collision`` -- two windows that collide;
4. ``session`` -- a declared source-session rule (`from_lever_space`: RL3's tickets go live at 09:00, so an RL3
   window holds that slot on every date; and a window whose first mark falls inside the closed 08:30-08:59 CT window
   on any date is refused, since it cannot fill there -- `triggers.CLOSED_FIRST` to `CLOSED_LAST`);
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
refused ones included, with its role (``survey``, ``round-<i>``, ``plateau:<finalist id>``), its seed, its status and
reason, the latency of every active component (every L tried counted, CHARTER 3.3 (g)), the plateau rule's sha256 on
a plateau row, and the numpy and scipy versions (`LIBS`). It holds designs only, never a reading. **A role is begun
once** (`begin`), with its seed: a second survey, a second round ``i`` (under any seed), a round before the one before
it, a row under a seed other than its role's, and a second plateau check of one finalist are all refused (the red
team's B-1 and m-2). **A role closes** (the red team's n-2, the lead's ruling): `begin` returns the role's `RolePen`
to the drawer that opened it -- the sampler, the proposer or the plateau check -- the only writer of its cells, and the
drawer closes it when its batch returns; a cell recorded without the pen (`NotTheDrawer`) or after the close
(`RoleClosed`) is refused, so no design is slipped into a role after a look. A round's `RoundSpec` and limits are its
role's meta (n-3). **Everything recorded is frozen** (n-1): a row, its design, its latencies and library versions, and
a role's meta are read-only (`FrozenMap`, tuples), so an edit after recording raises. `variant_rows` gives the rows for
the variants ledger (`results/variants.jsonl`), which only a clean run writes, each carrying the full declared protocol
and its sha256 (rb2-a).

**Readings and the one door** (`Protocol`, `Reading`, `admit`; the red team's B-1 and RB-2, the lead's rulings). A
`Protocol` is the declaration's reading protocol: the measure, the history blocks, the coin seeds, the outcome horizon
in sessions, and the library versions. **The survey declares it to the ledger** (`Sampler.survey(..., protocol=,
reread_seeds=, measures=, declaration_sha256=)`), with the plateau's re-read seeds (at least `MIN_REREAD_SEEDS`,
rm3-b) and the limit measures, once; **every door takes it from the ledger, never from a caller**. **The declaration
binds it** (the red team's rb2-a, the lead's ruling): `protocol_sha256` hashes the full declared protocol (the measure,
blocks, seeds, horizon and library versions, the re-read seeds and the limit measures); the search declaration states
that figure, the runner passes it as `declaration_sha256`, and the survey's `begin` refuses a protocol whose sha256
differs (`DeclarationMismatch`). Every plateau verdict and variant row carries the full protocol and its sha256, so a
second ledger opened on another protocol is visible in what it produces. A `Reading` is one design's measure read on
it, frozen (its design a read-only mapping, m-4); the last session any outcome read is derived from its blocks and
horizon on Q-40's session calendar (`reads_through`, m-3 and rn-3). `admit(readings, ledger=, measure=, reread=,
roles=)` is the one door. It refuses:
- anything that is not exactly a `Reading` (a subclass or a prediction never is);
- a tag other than ``search``; a held-out tag names the held-out years in its refusal;
- a block or an outcome session past 2023-12-29 (CHARTER 3.6 (a), (d); E-208), the confirmation window, or a day before
  2020-01-02;
- a reading off the ledger's protocol (another measure, blocks, seeds, horizon or library versions), on the
  declared re-read seeds only where the plateau asks for them (the composite and every declared limit, F-3), under a
  measure the survey did not declare;
- **a design that is not a counted ``proposed`` cell of the ledger in one of the allowed roles**.
Every reading the surrogate, the proposer or the plateau check sees comes through this door, so **within one ledger** a
design read outside the count, or on a protocol picked after a look, never reaches a fit or a finalist. Across ledgers
(a runner opening a second `CellLedger` on another protocol, rb2-a) the guard is the declaration's sha256 at the
survey's `begin` and the protocol each verdict carries; that a run builds exactly one ledger, from the pinned text, is
Wave 5's runner review's to check. The held-out years are never read
by a search (CHARTER 3.6 (a), E-221 O-1).

**What a caller does since Q-192** (the survey runner's port, BUILD_SURVEY_c2 M-1):
1. **The survey step takes the declaration's sha256**: `Sampler.survey(n, ledger=, protocol=, reread_seeds=,
   measures=, declaration_sha256=)`, where `declaration_sha256` is the figure the pinned declaration states,
   `protocol_sha256(protocol, reread_seeds, measures)`; absent or different, `begin` raises `DeclarationMismatch`.
   Fewer than `MIN_REREAD_SEEDS` re-read seeds raise `TooFewRereadSeeds`; seeds shared with the protocol's,
   `LedgerRefused`.
2. **Cells are recorded with the role's pen**: `pen = ledger.begin(role, seed, **meta)`, then
   `pen.record(space, design, refusal=..., round_index=...)`, then `pen.close()` when the batch returns.
   `ledger.record` without the role's pen raises `NotTheDrawer`, and after the close `RoleClosed`. `Sampler.survey`,
   `proposer.propose` and `plateau.check` open and close their own roles; a runner's own role (a baseline's) goes
   through the three steps above.
3. **The protocol's sha256 is the engine's**: `ledger.protocol_sha256` (and `ledger.declared`, the full record) is what
   every `PlateauVerdict` (`protocol_sha256`, `protocol`) and every variant row (`params["_protocol_sha256"]`,
   `params["_protocol"]`) carries; a runner records that figure, or checks its own digest against it.
And **a limit is read on the re-read seeds** (F-3; the lead's ruling, RB-2, E-247/E-251):
`ledger.protocol_for(limit, reread=True)` is `ledger.reread.with_measure(limit)` for exactly the limit measures the
survey declared; anything else is refused (`OffProtocol`), and no door takes seeds from the caller. `plateau.check`
reads every declared limit of the finalist there and reports it as `PlateauVerdict.reread_limits`, the point
estimate a limit decides on, the selection reading beside it.

**Wave 5's hooks** (the red team's m-9 and m-10, Wave 5's declaration by the lead's ruling): the finalist order rule
and the multi-objective frontier are not built here. A finalist reaches `extended.plateau.check` only as a counted
survey or round cell on the protocol; the order rule that names it is the declaration's. `to_components` is the bridge
from a design's offsets to `extended.components.Design(day=...)` per date (m-11).
"""
from __future__ import annotations

import functools
import hashlib
import itertools
import json
import math
import re
import warnings
from collections import Counter
from collections import abc as _abc
from dataclasses import dataclass, field
from datetime import date, timedelta
from types import MappingProxyType
from typing import Any, Callable, Iterable, Mapping, Sequence

import numpy as np
import scipy
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
#: the library versions every protocol, reading, ledger row, fit and round records (the red team's m-8): Sobol, LHS
#: and L-BFGS-B reproduce from a seed only under one set of versions, so a declaration pins them
LIBS: tuple[tuple[str, str], ...] = (("numpy", np.__version__), ("scipy", scipy.__version__))
_TIER_ONE_FOLDED = frozenset(x.casefold() for x in TIER_ONE)
_ROUND = re.compile(r"round-(\d+)")
#: the fewest re-read seeds a survey may declare (the red team's rm3-b, the lead's ruling): below it the exact law's
#: quadrature is off at many neighbours and the paired se too noisy to stand behind
MIN_REREAD_SEEDS = 5


#: the whole NY session's name (`components.session_bounds`): a registered design's, never a searched one's (m2)
WHOLE_NY = "ny"
WHOLE_NY_REFUSED = ("a searched slot in `ny`, the whole NY session, is refused: T2 declares `ny_am` and `ny_pm`, split "
                    "at T2b (the red team's m2, the lead's ruling); a registered design may still name `ny` through "
                    "`components`")


class SpaceRefused(ValueError):
    """A space, a slot or a sampler request this module cannot stand behind."""


class LedgerRefused(SpaceRefused):
    """A ledger entry that would hide a choice: a role begun twice, a round out of order, a row off its role's seed."""


class ReadingRefused(RuntimeError):
    """A reading the one door does not admit."""


class HeldOutInput(ReadingRefused):
    """An input tagged held-out, touching the held-out years, or not a search-year reading: refused (CHARTER
    3.6 (a))."""


class OffProtocol(ReadingRefused):
    """A reading on another measure, blocks, seeds, horizon or library versions than the declared protocol."""


class Uncounted(ReadingRefused):
    """A reading of a design that is not a counted cell of the ledger in an allowed role."""


class TooFewRereadSeeds(LedgerRefused):
    """A survey declaring fewer than `MIN_REREAD_SEEDS` re-read seeds (the red team's rm3-b, the lead's ruling)."""


class DeclarationMismatch(LedgerRefused):
    """A survey whose declared protocol does not hash to the declaration's sha256 (the red team's rb2-a)."""


class RoleClosed(LedgerRefused):
    """A cell recorded into a role after its batch returned (the red team's n-2)."""


class NotTheDrawer(LedgerRefused):
    """A cell recorded by anyone but the drawer that opened its role (the red team's n-2)."""


class FrozenMap(_abc.Mapping):
    """A read-only mapping of a copy (the red team's n-1): no item assignment, no attribute assignment; deep-copyable
    and comparable with a dict. The ledger's rows, their designs and library versions, and every role's meta are
    these, so an edit after recording raises."""

    __slots__ = ("_d",)

    def __init__(self, d: Mapping[str, Any] | Iterable[tuple[str, Any]] = ()) -> None:
        object.__setattr__(self, "_d", dict(d))

    def __getitem__(self, k: str) -> Any:
        return self._d[k]

    def __iter__(self):
        return iter(self._d)

    def __len__(self) -> int:
        return len(self._d)

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("a FrozenMap is read-only")

    def __delattr__(self, name: str) -> None:
        raise AttributeError("a FrozenMap is read-only")

    def __reduce__(self):
        return (FrozenMap, (self._d,))

    def __repr__(self) -> str:
        return f"FrozenMap({self._d!r})"


def freeze(x: Any) -> Any:
    """A deep read-only copy: a mapping a `FrozenMap`, a list or tuple a tuple, each member frozen."""
    if isinstance(x, _abc.Mapping):
        return FrozenMap((k, freeze(v)) for k, v in x.items())
    if isinstance(x, (list, tuple)):
        return tuple(freeze(v) for v in x)
    return x


def thaw(x: Any) -> Any:
    """A plain copy of a frozen value for JSON (a mapping a dict, a tuple a list)."""
    if isinstance(x, _abc.Mapping):
        return {k: thaw(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [thaw(v) for v in x]
    return x


def searched(role: str) -> bool:
    """A survey or round cell: what the surrogate fits and what a finalist may be."""
    return role == "survey" or _ROUND.fullmatch(role) is not None


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
    #: searched levers held at their base until an executor applies them (m4): lever -> its label
    held: Mapping[str, str] = field(default_factory=dict)

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
        if self.lever_checks and any(sl.session == WHOLE_NY for sl in self.slots):
            raise SpaceRefused(WHOLE_NY_REFUSED)
        for k in self.held:
            if k not in self.fixed or any(d.lever == k and d.slot is None for d in self.dims):
                raise SpaceRefused(f"{k} is held until wired: its base is fixed, never a dimension (m4)")
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
                if isinstance(x, str) and x.casefold() in _TIER_ONE_FOLDED:
                    return f"{k} = {x!r} is conduct tier 1 (CHARTER 4; Stage 2 D-145)"
        ov = design.get(OVERLAP_KEY, self.fixed.get(OVERLAP_KEY, OVERLAP_REFUSED))
        if ov != OVERLAP_REFUSED:
            return f"overlap {ov!r}: a design holding two positions of the user at once is refused (m-2, E-210)"
        firms = design.get(FIRMS_KEY, self.fixed.get(FIRMS_KEY, 1))
        if type(firms) is not int or firms != 1:
            return f"{firms!r} firms: a design is one firm's (one position at a time across a firm, D-429)"
        return None

    # -- the centre and the repair (a plateau neighbour's dependent levers)
    def centre(self, dim: Dim, design: Mapping[str, Any]) -> Any:
        """The dimension's centre value given the design so far: its middle cell, or its lattice's or range's middle."""
        if dim.kind == CAT:
            cells = dim.cells_of(design)
            return cells[len(cells) // 2]
        lo = float(design[dim.after]) if dim.after else float(dim.lo)
        if dim.step is None:
            return lo + 0.5 * (float(dim.hi) - lo)
        n = dim.lattice(lo)
        v = lo + (n // 2) * float(dim.step)
        return int(round(v)) if dim.kind == INT else v

    def repair(self, design: Mapping[str, Any], changed: Iterable[str]) -> dict[str, Any]:
        """After `changed` levers move: every lever after them that turned inactive holds None; one that turned active,
        or a categorical whose cells depend on a changed lever and no longer hold its value, takes its centre. Nothing
        else moves (a window's last left before its first stays, so the space refuses it)."""
        out = dict(design)
        moved = set(changed)
        for d in self.dims:
            if d.name in moved:
                continue
            if not self.active(d, out):
                if out[d.name] is not None:
                    out[d.name] = None
                    moved.add(d.name)
                continue
            if out[d.name] is None:
                out[d.name] = self.centre(d, out)
                moved.add(d.name)
            elif d.kind == CAT and d.cells is not None and out[d.name] not in d.cells_of(out):
                out[d.name] = self.centre(d, out)
                moved.add(d.name)
        return out

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


def protocol_record(protocol: "Protocol", reread_seeds: Sequence[int], measures: Sequence[str] = ()) -> dict[str, Any]:
    """The full declared protocol as plain JSON values (the red team's rb2-a): the measure, the search-year blocks, the
    selection seeds, the outcome horizon, the library versions, the plateau's re-read seeds and the limit measures."""
    return {"measure": protocol.measure, "blocks": [list(b) for b in protocol.blocks], "seeds": list(protocol.seeds),
            "horizon": int(protocol.horizon), "libs": [list(x) for x in protocol.libs],
            "reread_seeds": [int(x) for x in reread_seeds], "measures": list(measures)}


def protocol_sha256(protocol: "Protocol", reread_seeds: Sequence[int], measures: Sequence[str] = ()) -> str:
    """The sha256 of `protocol_record`'s canonical JSON (sorted keys, no spaces): the figure a search declaration states
    for its protocol and the survey's `begin` checks (rb2-a)."""
    blob = json.dumps(protocol_record(protocol, reread_seeds, measures), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


class RolePen:
    """The capability to record cells of one role (the red team's n-2): `CellLedger.begin` returns it to the drawer that
    opened the role -- the sampler (the survey), the proposer (a round), the plateau check (its neighbours) -- and the
    drawer closes it when its batch returns. A cell recorded without it, or after it closed, is refused."""

    def __init__(self, ledger: "CellLedger", role: str, seed: int) -> None:
        self._ledger, self.role, self.seed = ledger, role, int(seed)

    def record(self, space: "Space", design: Mapping[str, Any], *, refusal: tuple[str, str] | None,
               round_index: int | None = None) -> Mapping[str, Any]:
        return self._ledger.record(space, design, role=self.role, seed=self.seed, refusal=refusal,
                                   round_index=round_index, pen=self)

    def close(self) -> None:
        self._ledger._close(self.role, self)


class CellLedger:
    """Every cell proposed -- by the survey, a round or a plateau check -- refused ones included (CHARTER 3.3 (f),
    (g); the template's section 13). Designs only: a reading never enters it. **The survey declares the protocol**
    (the red team's RB-2, the lead's ruling): `begin("survey", seed, protocol=, reread_seeds=, measures=,
    declaration_sha256=)` stores the declared `Protocol`, the plateau's re-read seeds (at least `MIN_REREAD_SEEDS`) and
    the declared limit measures, once, and refuses them unless they hash to the declaration's sha256
    (`protocol_sha256`, rb2-a); every door takes them from here (`protocol_for`), never from a caller. **A role closes**
    (n-2): `begin` returns the role's `RolePen` to its drawer, the only writer of its cells, which closes it when its
    batch returns. `rows`, `roles`, every row's design, latencies and library versions, every role's meta and the
    stored protocol are read-only (rn-4, n-1)."""

    def __init__(self) -> None:
        self._rows: list[FrozenMap] = []
        self._roles: dict[str, dict[str, Any]] = {}
        self._pens: dict[str, RolePen] = {}
        self._closed: set[str] = set()
        self._protocol: Protocol | None = None
        self._reread_seeds: tuple[int, ...] = ()
        self._measures: tuple[str, ...] = ()

    # -- read-only views (rn-4, n-1)
    @property
    def rows(self) -> tuple[Mapping[str, Any], ...]:
        return tuple(self._rows)

    @property
    def roles(self) -> Mapping[str, Mapping[str, Any]]:
        return MappingProxyType({k: FrozenMap({"seed": v["seed"], "meta": v["meta"], "closed": k in self._closed})
                                 for k, v in self._roles.items()})

    @property
    def protocol(self) -> "Protocol":
        if self._protocol is None:
            raise LedgerRefused("no protocol is declared: the survey declares it (begin('survey', ..., protocol=))")
        return self._protocol

    @property
    def reread(self) -> "Protocol":
        """The plateau's re-read protocol: the declared protocol on the declared re-read seeds."""
        return self.protocol.with_seeds(self._reread_seeds)

    @property
    def measures(self) -> tuple[str, ...]:
        """The declared limit measures, read on the protocol's blocks, seeds and horizon."""
        return self._measures

    @property
    def declared(self) -> Mapping[str, Any]:
        """The full declared protocol (`protocol_record`), read-only: what every verdict and variant row carries."""
        return freeze(protocol_record(self.protocol, self._reread_seeds, self._measures))

    @property
    def protocol_sha256(self) -> str:
        """The declared protocol's sha256 (`protocol_sha256`), checked at the survey's `begin`."""
        return protocol_sha256(self.protocol, self._reread_seeds, self._measures)

    def protocol_for(self, measure: str | None = None, *, reread: bool = False) -> "Protocol":
        """The declared protocol for `measure` (its own measure, or a declared limit's), on the re-read seeds when
        `reread` -- a declared limit included (BUILD_SURVEY_v2 F-3, the lead's ruling: a limit decided on the
        selection reading, the luckiest, is biased toward inside); anything else is refused."""
        base = self.reread if reread else self.protocol
        if measure is None or measure == base.measure:
            return base
        if measure not in self._measures:
            raise OffProtocol(f"REFUSED: measure {measure!r} is not declared on this ledger's protocol (the survey "
                              f"declared {base.measure!r} and limits {self._measures})")
        return base.with_measure(measure)

    def begin(self, role: str, seed: int, *, protocol: "Protocol | None" = None,
              reread_seeds: Sequence[int] | None = None, measures: Sequence[str] = (),
              declaration_sha256: str | None = None, **meta: Any) -> RolePen:
        """Open `role` under `seed`, once (the module docstring), and return its pen: a role begun before is refused,
        and a round needs the one before it (the survey before round one). The survey, and only the survey, declares
        the protocol, checked against the declaration's sha256."""
        if not isinstance(seed, (int, np.integer)) or isinstance(seed, bool):
            raise LedgerRefused("a role's seed is an explicit integer")
        if not role:
            raise LedgerRefused("a cell has a role")
        if role in self._roles:
            raise LedgerRefused(f"role {role!r} is already recorded (seed {self._roles[role]['seed']}): a second "
                                f"{role} under seed {seed} would let the reader choose between them")
        if role == "survey":
            if type(protocol) is not Protocol:
                raise LedgerRefused("the survey declares the protocol (a `Protocol`), and the re-read seeds")
            rr = tuple(reread_seeds) if reread_seeds is not None else ()
            if len(set(rr)) != len(rr) or not all(
                    isinstance(x, (int, np.integer)) and not isinstance(x, bool) for x in rr):
                raise LedgerRefused("the plateau's re-read seeds are distinct integers, declared now")
            if len(rr) < MIN_REREAD_SEEDS:
                raise TooFewRereadSeeds(f"{len(rr)} re-read seeds declared: the floor is {MIN_REREAD_SEEDS} (rm3-b)")
            if set(rr) & set(protocol.seeds):
                raise LedgerRefused("the re-read seeds are fresh: disjoint from the protocol's")
            ms = tuple(measures)
            if len(set(ms)) != len(ms) or protocol.measure in ms or not all(isinstance(x, str) and x for x in ms):
                raise LedgerRefused(f"the limit measures are distinct names other than {protocol.measure!r}")
            got = protocol_sha256(protocol, rr, ms)
            if not isinstance(declaration_sha256, str) or declaration_sha256 != got:
                raise DeclarationMismatch(f"the survey's protocol hashes to {got}; the declaration's sha256 is "
                                          f"{declaration_sha256!r} (rb2-a): a protocol other than the declared one is "
                                          "refused")
            self._protocol, self._reread_seeds, self._measures = protocol, tuple(int(x) for x in rr), ms
        elif protocol is not None or reread_seeds is not None or measures or declaration_sha256 is not None:
            raise LedgerRefused(f"only the survey declares a protocol; {role!r} reads the survey's")
        else:
            m = _ROUND.fullmatch(role)
            if m:
                i = int(m.group(1))
                before = "survey" if i == 1 else f"round-{i - 1}"
                if i < 1 or before not in self._roles:
                    raise LedgerRefused(f"{role} before {before}: rounds are recorded in order, from the survey")
        self._roles[role] = {"seed": int(seed), "meta": freeze(meta)}
        pen = RolePen(self, role, int(seed))
        self._pens[role] = pen
        return pen

    def _close(self, role: str, pen: RolePen) -> None:
        if self._pens.get(role) is not pen:
            raise NotTheDrawer(f"role {role!r} is closed by the drawer that opened it")
        self._closed.add(role)

    def closed(self, role: str) -> bool:
        return role in self._closed

    def record(self, space: Space, design: Mapping[str, Any], *, role: str, seed: int,
               refusal: tuple[str, str] | None, round_index: int | None = None,
               pen: RolePen | None = None) -> Mapping[str, Any]:
        """One cell of `role`, by its drawer (`pen`, the role's `RolePen`) while the role is open (n-2)."""
        if not isinstance(seed, (int, np.integer)) or isinstance(seed, bool):
            raise LedgerRefused("a cell's seed is an explicit integer")
        if role not in self._roles:
            raise LedgerRefused(f"role {role!r} was not begun: a cell is recorded under a begun role")
        if role in self._closed:
            raise RoleClosed(f"role {role!r} is closed: its batch has returned, and a cell recorded after it would be "
                             "a choice made after a look (n-2)")
        if pen is None or self._pens.get(role) is not pen:
            raise NotTheDrawer(f"a {role} cell is recorded only by the drawer that opened the role (its pen; n-2)")
        if int(seed) != self._roles[role]["seed"]:
            raise LedgerRefused(f"a {role} cell under seed {seed}, its role's seed is {self._roles[role]['seed']}")
        meta = self._roles[role]["meta"]
        row = FrozenMap({"cell": len(self._rows), "id": design_id(design), "role": role, "seed": int(seed),
                         "round": round_index, "status": "refused" if refusal else "proposed",
                         "class": refusal[0] if refusal else "", "reason": refusal[1] if refusal else "",
                         "latencies": tuple(str(x) for x in space.latencies(design)), "design": freeze(dict(design)),
                         "rule": meta.get("rule", ""), "libs": FrozenMap(LIBS)})
        self._rows.append(row)
        return row

    def proposed_ids(self, roles: Callable[[str], bool]) -> frozenset[str]:
        """The ids of the cells proposed (not refused) under the roles `roles` accepts."""
        return frozenset(r["id"] for r in self._rows if r["status"] == "proposed" and roles(r["role"]))

    def counts(self) -> dict[str, Any]:
        rows = self._rows
        return {"cells": len(rows),
                "proposed": sum(r["status"] == "proposed" for r in rows),
                "refused": sum(r["status"] == "refused" for r in rows),
                "distinct": len({r["id"] for r in rows}),
                "by_role": dict(Counter(r["role"] for r in rows)),
                "by_class": dict(Counter(r["class"] for r in rows if r["status"] == "refused")),
                "latency": dict(Counter(x for r in rows for x in r["latencies"]))}

    def variant_rows(self, prereg_id: str) -> list[dict[str, Any]]:
        """The rows for `VariantCounter.record` (prereg id, params, seed, label): written only by a clean run. Each
        row's params carry the design, the library versions, the full declared protocol and its sha256 (rb2-a)."""
        declared, sha = thaw(self.declared), self.protocol_sha256
        return [{"prereg_id": prereg_id,
                 "params": dict(thaw(r["design"]), _libs=thaw(r["libs"]), _protocol=declared, _protocol_sha256=sha),
                 "seed": r["seed"], "label": f"{r['role']}:{r['status']}" + (f":{r['class']}" if r["class"] else "")}
                for r in self._rows]


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
        if any(sl.session == WHOLE_NY for sl in space.slots):
            raise SpaceRefused(WHOLE_NY_REFUSED)
        self.space, self.seed, self.method = space, int(seed), method

    def _stream(self, combo: int, fixed: Mapping[int, float], n: int, pen: RolePen,
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
                    pen.record(self.space, design, refusal=refusal, round_index=round_index)
                    tried += 1
                    if refusal is None:
                        out.append(design)
        return out

    def survey(self, n: int, *, ledger: CellLedger, protocol: "Protocol", reread_seeds: Sequence[int],
               measures: Sequence[str] = (), declaration_sha256: str | None = None, role: str = "survey",
               max_proposals: int | None = None, cross: Sequence[str] = (),
               round_index: int | None = None) -> list[dict[str, Any]]:
        """`n` designs that pass every check (per combination of `cross`'s categoricals, crossed in full, when given),
        every cell proposed recorded in `ledger`, whose survey role declares the protocol, the plateau's re-read seeds
        and the limit measures, checked against the declaration's sha256 (`CellLedger.begin`). The survey role closes
        when the batch returns (n-2): no cell enters it after."""
        if int(n) <= 0:
            raise SpaceRefused("a survey has at least one design")
        cap = int(max_proposals) if max_proposals is not None else 64 * int(n)
        idx = []
        for name in cross:
            d = self.space.dim(name)
            if d.kind != CAT or d.cells is not None or d.active_if is not None:
                raise SpaceRefused(f"{name}: only a static, always-active categorical is enumerated")
            idx.append((self.space.names().index(name), d.values))
        pen = ledger.begin(role, self.seed, protocol=protocol, reread_seeds=reread_seeds, measures=measures,
                           declaration_sha256=declaration_sha256)
        try:
            if not cross:
                return self._stream(0, {}, int(n), pen, cap, round_index)
            out: list[dict[str, Any]] = []
            for c, combo in enumerate(itertools.product(*[vals for _, vals in idx])):
                fixed = {j: (vals.index(v) + 0.5) / len(vals) for (j, vals), v in zip(idx, combo)}
                out += self._stream(c + 1, fixed, int(n), pen, cap, round_index)
            return out
        finally:
            pen.close()


# ------------------------------------------------------------------------------------------------ the lever space


def _overnight_allowed() -> bool:
    from extended import triggers as T

    return T.overnight_allowed()


def session_spans(day: date, ny_boundary: int | None = None) -> dict[str, tuple[int, int]]:
    """Trading day `day`'s sessions as [start, end) in slots after the reopen (`components.session_windows_of(day)`, the
    one function every session window is read through, anchored per date, E-231 (3)), each end clipped to one past the
    firm's last new entry. Without a boundary NY is one session, `ny` (the whole session: a reading of windows, the
    registered designs' form; a searched slot never takes it, m2); given one (a slot), `ny_am` and `ny_pm`, and it must
    be T2b's declared boundary (`lever_space.check_ny_boundary`: noon New York; any other value is refused, the red
    team's L-M2)."""
    from extended import components as C
    from extended import lever_space as LS

    td = LS.trading_day()
    step = int(LS.bounds("T3").step)
    sw = C.session_windows_of(day)                         # the one function every session window is read through
    spans = {k: v for k, v in sw.items() if k not in ("ny_am", "ny_pm")}
    ny = (sw["ny_am"][0], sw["ny_pm"][1])
    if ny_boundary is None:
        spans["ny"] = ny
    else:
        try:
            b = LS.check_ny_boundary(ny_boundary, firm="topstep")
        except LS.LeverRefused as e:
            raise SpaceRefused(f"{e} (on {day})") from None
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


def _closed_first(slot: str, session_starts: Sequence[int]) -> Callable[[Mapping[str, Any]], str | None]:
    """A window whose first mark falls inside the closed 08:30-08:59 CT window on any date is refused (it cannot fill
    there; the red team's n-3, the lead's ruling)."""
    from extended import triggers as T

    lo, hi = int(T.CLOSED_FIRST), int(T.CLOSED_LAST)

    def fn(design: Mapping[str, Any]) -> str | None:
        if design.get(slot_dim(slot, "on")) == ON:
            a = int(design[slot_dim(slot, "first")])
            bad = sorted({s + a for s in session_starts if lo <= s + a <= hi})
            if bad:
                return f"its first mark {bad} lies inside the closed window [{lo}, {hi}] (08:30-08:59 CT)"
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
    carried as refused. **NY is split at T2b** (m2): `ny_boundary` defaults to T2b's loaded value and must be it, and a
    slot in `ny`, the whole session, is refused. **A15 and A17 are held until wired** (m4): fixed at their declared
    bases (`lever_space.held_value`) and labelled in `held`, never dimensions, until an executor applies them."""
    from extended import lever_space as LS
    from extended import triggers as T

    if WHOLE_NY in slots:
        raise SpaceRefused(WHOLE_NY_REFUSED)
    if ny_boundary is None:
        ny_boundary = int(LS.bounds("T2b").values[0])
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
    held = {k: label for k, label in LS.HELD_UNTIL_WIRED.items() if k in loaded}
    for k in held:
        fixed[k] = (loaded[k].values[0],)                    # its base: the first declared value
    dims: list[Dim] = []
    for k, r in loaded.items():
        lv = LS.LEVERS[k]
        if lv.cls != LS.SEARCHED or k in SLOT_LEVERS or k == "T2" or k in held:
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
            srcs = tuple(s for s in sources if s != "rl3" or name == "ny_am")
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
            if "S1" in loaded:                                 # Q-171: k x the session's trailing range
                r1 = LS.stop_width(name)
                dims.append(Dim(slot_dim(sn, "S1"), REAL, lo=float(r1.lo), hi=float(r1.hi), active_if=act,
                                lever="S1", slot=sn))
            if "S2" in loaded:
                r = loaded["S2"]
                dims.append(Dim(slot_dim(sn, "S2"), REAL, lo=float(r.lo), hi=float(r.hi), active_if=act,
                                lever="S2", slot=sn))
            if "rl3" in srcs:
                constraints.append(Constraint(f"{sn} rl3 live", "session",
                                              _rl3_live(sn, [sp[name][0] for sp in spans_by_day.values()])))
            session_starts = sorted({sp[name][0] for sp in spans_by_day.values()})
            if any(int(T.CLOSED_FIRST) <= a + last and a + first <= int(T.CLOSED_LAST) for a in session_starts):
                constraints.append(Constraint(f"{sn} closed window", "session", _closed_first(sn, session_starts)))

    def starts(day: date) -> dict[str, int]:
        return {k: a for k, (a, _) in session_spans(day, ny_boundary).items()}

    return Space(tuple(dims), fixed=fixed, refused=refused, slots=tuple(slot_objs), constraints=tuple(constraints),
                 lever_checks=True, firm="topstep_50k", starts=starts, days=days, held=held)


# ------------------------------------------------------------------------------------------------ readings


def _check_blocks(blocks: Any) -> tuple[tuple[str, str], ...]:
    if not blocks:
        raise HeldOutInput("REFUSED: a reading names the search-year blocks it was read on")
    out = []
    for b in blocks:
        if not (isinstance(b, tuple) and len(b) == 2):
            raise HeldOutInput(f"REFUSED: a block is (start, end), got {b!r}")
        try:
            got = R.blocks_of(b[0], b[1])                   # refuses the confirmation window and before 2020-01-02
        except (R.ReadRefused, ValueError, TypeError) as e:
            raise HeldOutInput(f"REFUSED: block {b!r}: {e}") from e
        if got != ("choice",):
            raise HeldOutInput(f"REFUSED: block {b[0]} to {b[1]} touches the held-out years ({got}; E-208): a search "
                               "reads the search years only")
        out.append((str(b[0]), str(b[1])))
    return tuple(out)


@functools.lru_cache(maxsize=1)
def _closures() -> frozenset[date]:
    """Q-40's full closures (`config/calendar_early_closes.csv`: a holiday with no close): weekdays without a session.
    A verified calendar file, not a bar."""
    from extended import calendar_early_closes as CE

    return frozenset(date.fromisoformat(r["date"]) for r in CE.read_calendar()
                     if r["kind"] == "holiday" and not r["close_ct"])


def is_session(d: date) -> bool:
    return d.weekday() < 5 and d not in _closures()


def session_after(day: date, horizon: int) -> date:
    """The session `horizon` sessions after `day` (0: the last session at or before `day`), counting weekdays that are
    not a full closure in Q-40's calendar (the red team's rn-3)."""
    d = day
    while not is_session(d):
        d -= timedelta(days=1)
    for _ in range(int(horizon)):
        d += timedelta(days=1)
        while not is_session(d):
            d += timedelta(days=1)
    return d


def reads_through(blocks: Sequence[tuple[str, str]], horizon: int) -> date:
    """The last session any outcome of a reading on `blocks` at `horizon` reads: the last block's end advanced by
    `horizon` sessions (derived, never reported by the caller; CHARTER 3.6 (d))."""
    return session_after(max(date.fromisoformat(str(b[1])[:10]) for b in blocks), horizon)


def _check_through(blocks: Sequence[tuple[str, str]], horizon: int) -> date:
    t = reads_through(blocks, horizon)
    if t > R.CHOICE_END:
        raise HeldOutInput(f"REFUSED: outcomes read through {t}, after the search years end on {R.CHOICE_END} "
                           f"(horizon {horizon} sessions past the last block; CHARTER 3.6 (d), E-208)")
    return t


def _int_seeds(seeds: Any) -> tuple[int, ...]:
    if not seeds or not all(isinstance(x, (int, np.integer)) and not isinstance(x, bool) for x in seeds):
        raise HeldOutInput("REFUSED: a reading names its coin seeds, as integers")
    return tuple(int(x) for x in seeds)


@dataclass(frozen=True)
class Protocol:
    """The declaration's reading protocol: the measure, the search-year blocks, the coin seeds, the outcome horizon in
    sessions (how far after its start an outcome reads), and the library versions (`LIBS`; the run's must be these)."""

    measure: str
    blocks: tuple[tuple[str, str], ...]
    seeds: tuple[int, ...]
    horizon: int
    libs: tuple[tuple[str, str], ...] = LIBS

    def __post_init__(self) -> None:
        if not isinstance(self.measure, str) or not self.measure:
            raise OffProtocol("a protocol names its measure")
        object.__setattr__(self, "blocks", _check_blocks(tuple(tuple(b) for b in self.blocks)))
        seeds = _int_seeds(self.seeds)
        if len(set(seeds)) != len(seeds):
            raise OffProtocol(f"a protocol's seeds are distinct, got {seeds}")
        object.__setattr__(self, "seeds", seeds)
        if type(self.horizon) is not int or self.horizon < 0:
            raise OffProtocol(f"a protocol's horizon is a whole number of sessions, got {self.horizon!r}")
        _check_through(self.blocks, self.horizon)
        object.__setattr__(self, "libs", tuple(tuple(x) for x in self.libs))
        if self.libs != LIBS:
            raise OffProtocol(f"the protocol pins {self.libs}; this run has {LIBS} -- a seed reproduces only under the "
                              "declared versions (m-8)")

    def with_measure(self, measure: str) -> "Protocol":
        return Protocol(measure, self.blocks, self.seeds, self.horizon, self.libs)

    def with_seeds(self, seeds: Sequence[int]) -> "Protocol":
        return Protocol(self.measure, self.blocks, tuple(seeds), self.horizon, self.libs)


@dataclass(frozen=True)
class Reading:
    """A design's measure read on a protocol: its blocks ((start, end) ISO days), coin seeds and outcome horizon in
    sessions; the last session any outcome read is derived from them (`reads_through`, never the caller's: rn-3).
    `tag` 'search' is the only one admitted;
    `se` the value's standard error over its seeds, `per_seed` its value under each seed (in the protocol's order),
    when known. Frozen: the design becomes a read-only mapping of a copy, the sequences tuples (m-4)."""

    design: Mapping[str, Any]
    value: float
    blocks: tuple[tuple[str, str], ...]
    seeds: tuple[int, ...]
    tag: str
    measure: str
    horizon: int
    se: float | None = None
    per_seed: tuple[float, ...] | None = None
    libs: tuple[tuple[str, str], ...] = LIBS

    def __post_init__(self) -> None:
        object.__setattr__(self, "design", MappingProxyType(dict(self.design)))
        object.__setattr__(self, "blocks", tuple(tuple(b) for b in self.blocks))
        object.__setattr__(self, "seeds", tuple(self.seeds))
        if self.per_seed is not None:
            object.__setattr__(self, "per_seed", tuple(float(x) for x in self.per_seed))
        object.__setattr__(self, "libs", tuple(tuple(x) for x in self.libs))

    @property
    def id(self) -> str:
        return design_id(self.design)

    @property
    def reads_through(self) -> date:
        return reads_through(self.blocks, self.horizon)


def admit_one(r: Any, *, ledger: CellLedger, measure: str | None = None, reread: bool = False,
              roles: Callable[[str], bool] = searched) -> Reading:
    """The one door (the module docstring): the reading, or a `ReadingRefused` naming why. **The protocol is the
    ledger's** (`CellLedger.protocol_for(measure, reread=)`), never the caller's (RB-2)."""
    if type(r) is not Reading:
        raise HeldOutInput(f"REFUSED: {type(r).__name__} is not exactly a search-year Reading (a prediction or a "
                           "subclass never is one)")
    if type(ledger) is not CellLedger:
        raise ReadingRefused("the door takes the cell ledger, which holds the declared protocol")
    tag = str(r.tag)
    low = tag.lower().replace("-", "").replace("_", "").replace(" ", "")
    if any(w in low for w in ("heldout", "judged", "holdout", "confirm")):
        raise HeldOutInput(f"REFUSED: a reading tagged {tag!r} is held-out: a search never reads the held-out years "
                           "(CHARTER 3.6 (a); E-208, E-221 O-1)")
    if tag != SEARCH_TAG:
        raise HeldOutInput(f"REFUSED: a reading tagged {tag!r}; only {SEARCH_TAG!r} is admitted")
    blocks = _check_blocks(r.blocks)
    seeds = _int_seeds(r.seeds)
    if type(r.horizon) is not int or r.horizon < 0:
        raise OffProtocol(f"REFUSED: a reading's horizon is a whole number of sessions, got {r.horizon!r}")
    _check_through(blocks, r.horizon)
    protocol = ledger.protocol_for(measure, reread=reread)
    if not math.isfinite(float(r.value)):
        raise HeldOutInput(f"REFUSED: a reading's value is finite, got {r.value!r}")
    if r.se is not None and not (math.isfinite(float(r.se)) and float(r.se) >= 0):
        raise HeldOutInput(f"REFUSED: a reading's standard error is finite and non-negative, got {r.se!r}")
    if r.per_seed is not None and (len(r.per_seed) != len(seeds)
                                   or not all(math.isfinite(x) for x in r.per_seed)):
        raise HeldOutInput("REFUSED: a reading's per-seed values are finite, one a seed")
    for what, got, want in (("measure", r.measure, protocol.measure), ("blocks", blocks, protocol.blocks),
                            ("seeds", seeds, protocol.seeds), ("horizon", r.horizon, protocol.horizon),
                            ("library versions", r.libs, protocol.libs)):
        if got != want or (what == "horizon" and type(got) is not int):
            raise OffProtocol(f"REFUSED: a reading on {what} {got!r}; the declared protocol's are {want!r}")
    if r.id not in ledger.proposed_ids(roles):
        raise Uncounted(f"REFUSED: design {r.id} is not a counted proposed cell of the ledger in an allowed role: a "
                        "design read outside the count never reaches a fit or a finalist (CHARTER 3.3 (f))")
    return r


def admit(readings: Iterable[Any], *, ledger: CellLedger, measure: str | None = None, reread: bool = False,
          roles: Callable[[str], bool] = searched) -> list[Reading]:
    """Every reading through the one door, or the first refusal (nothing admitted)."""
    return [admit_one(r, ledger=ledger, measure=measure, reread=reread, roles=roles) for r in readings]


# ------------------------------------------------------------------------------------------------ to the scheduler


def to_components(space: Space, design: Mapping[str, Any], day: date, *, firm: str,
                  build: Callable[[str, Mapping[str, Any]], tuple[Any, int]]) -> Any:
    """The design on trading day `day` as `extended.components.Design(day=day)` (the red team's m-11): each active
    slot's offsets read from that date's session start (`Space.windows_on`), its session the slot's own (`ny_am`
    and `ny_pm` strict at T2b's split in `components.session_bounds`, the red team's m1; a whole-NY slot is `ny`
    there too), its reward-to-risk from S2.
    `build(slot, levers)` gives the slot's trigger and stop in ticks (S1 and the sources' own parameters are not levers
    yet: the caller's, from its declaration)."""
    from extended import components as C

    why = space.check(design)
    if why is not None:
        raise SpaceRefused(f"a design the space refuses ({why[0]}: {why[1]})")
    comps = []
    for name, sess, a, b in space.windows_on(design, day):
        levers = {k[len(name) + 1:]: v for k, v in design.items() if k.startswith(name + ".")}
        if levers.get("S2") is None:
            raise SpaceRefused(f"slot {name} has no reward-to-risk (S2)")
        trigger, stop = build(name, MappingProxyType(levers))
        comps.append(C.Component(name, sess, int(a), int(b), trigger, int(stop),
                                 float(levers["S2"])))
    return C.Design(firm, tuple(comps), day=day)


__all__ = ["TASK", "REAL", "INT", "CAT", "OFF", "ON", "METHODS", "SEARCH_TAG", "REFUSAL_CLASSES", "TIER_ONE",
           "SLOT_LEVERS", "TICKET", "LIBS", "WHOLE_NY", "SpaceRefused", "LedgerRefused", "ReadingRefused", "HeldOutInput",
           "OffProtocol", "Uncounted", "TooFewRereadSeeds", "DeclarationMismatch", "RoleClosed", "NotTheDrawer",
           "FrozenMap", "freeze", "thaw", "MIN_REREAD_SEEDS", "searched", "Dim", "Slot", "slot_dim", "Constraint",
           "design_id", "Space", "protocol_record", "protocol_sha256", "RolePen", "CellLedger", "child_rng",
           "STREAM_SURVEY", "STREAM_POOL", "STREAM_LOCAL",
           "STREAM_FIT", "STREAM_PLATEAU", "UnitPoints", "Sampler", "session_spans", "search_days", "session_slots",
           "from_lever_space", "is_session", "session_after", "reads_through", "Protocol", "Reading", "admit_one",
           "admit", "to_components"]
