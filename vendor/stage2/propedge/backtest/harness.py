"""Walk-forward harness. Refuses to run without a registered pre-registration id.

Three properties this harness exists to guarantee, in order of importance:

1. **Rules are fixed before the test period.** A fold's parameters are frozen when the fold is
   constructed and the strategy is handed a period it cannot see beyond. The harness passes
   the training slice and the test slice separately, and only the test slice's trades count
   toward the reported edge.
2. **Every configuration tried is counted.** `VariantCounter` appends one record per run to
   `results/variants.jsonl`. The count is reported with any result, because an edge selected
   as the best of forty variants is not the same finding as an edge found on the first try,
   and the difference is invisible unless someone counted.
3. **No unregistered runs.** `prereg_id` must name an entry in `prereg/REGISTRY.md`. There is
   no override flag. A backtest whose hypothesis was written after the result is not evidence,
   and the only reliable way to enforce that is to make the unregistered path impossible
   rather than discouraged.

What the harness does *not* do is choose the strategy. `StrategyFn` is supplied by the caller;
T4 in NEXT_STEPS.md is where candidates get specified, and `default_strategy` raises until
then.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Protocol, Sequence

import pandas as pd

from propedge import PREREG_DIR, RESULTS_DIR


class UnregisteredRunError(RuntimeError):
    """Raised when a run is attempted without a registered pre-registration id."""


class LookaheadError(RuntimeError):
    """Raised when a fold's trades fall outside its test window."""


# --------------------------------------------------------------- pre-registration


@dataclass(frozen=True)
class PreregEntry:
    id: str
    date: str
    title: str
    status: str
    outcome: str


class PreregRegistry:
    """Reader for `prereg/REGISTRY.md`.

    The registry is a Markdown table (`id | date | title | status | outcome`) rather than a
    database because it has to be readable in a diff and in the final report. It is written
    by the **prereg-gatekeeper** agent, which refuses to register a pre-registration missing
    a data period, fixed rules, metrics, pass/fail criteria or a seed.
    """

    #: A pre-registration may be run while it is in one of these states.
    RUNNABLE = {"registered", "open", "running"}

    def __init__(self, entries: dict[str, PreregEntry], path: Path):
        self._entries = entries
        self.path = path

    @classmethod
    def load(cls, path: Path | str | None = None) -> "PreregRegistry":
        path = Path(path) if path is not None else PREREG_DIR / "REGISTRY.md"
        entries: dict[str, PreregEntry] = {}
        if not path.is_file():
            return cls(entries, path)
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < 4:
                continue
            pid = cells[0]
            # Skip the header row and the |---|---| separator.
            if not re.fullmatch(r"P-\d+", pid):
                continue
            entries[pid] = PreregEntry(
                id=pid,
                date=cells[1],
                title=cells[2],
                status=cells[3].lower(),
                outcome=cells[4] if len(cells) > 4 else "",
            )
        return cls(entries, path)

    def __contains__(self, pid: str) -> bool:
        return pid in self._entries

    def __len__(self) -> int:
        return len(self._entries)

    def get(self, pid: str) -> PreregEntry | None:
        return self._entries.get(pid)

    def all(self) -> list[PreregEntry]:
        return sorted(self._entries.values(), key=lambda e: e.id)

    def open_entries(self) -> list[PreregEntry]:
        """Registered but with no recorded outcome -- what `/status` and `/close-check` want."""
        return [
            e for e in self.all()
            if not e.outcome or e.outcome.lower() in {"", "-", "pending", "tbd"}
        ]

    def require_runnable(self, pid: str | None) -> PreregEntry:
        """Assert `pid` names an entry that may be run. Raises `UnregisteredRunError`."""
        if not pid:
            raise UnregisteredRunError(
                "this run has no pre-registration id.\n"
                "Every test in this stage is pre-registered before it is run -- the "
                "hypothesis, the data period, the fixed rules, the metrics, the pass/fail "
                "criteria and the seed are written down first.\n"
                "Run `/prereg <title>` to create one from prereg/TEMPLATE.md; the "
                "prereg-gatekeeper agent assigns the id and adds it to prereg/REGISTRY.md. "
                "There is no flag to skip this."
            )
        entry = self._entries.get(pid)
        if entry is None:
            known = ", ".join(sorted(self._entries)) or "(none registered yet)"
            raise UnregisteredRunError(
                f"pre-registration id {pid!r} is not in {self.path}.\n"
                f"Registered ids: {known}.\n"
                "Create one with `/prereg <title>`; the prereg-gatekeeper agent assigns the "
                "id and registers it."
            )
        if entry.status not in self.RUNNABLE:
            raise UnregisteredRunError(
                f"pre-registration {pid} has status {entry.status!r}; it may only be run "
                f"while its status is one of {sorted(self.RUNNABLE)}.\n"
                "A pre-registration that already has an outcome is not rerun: a failed "
                "pre-registered check is kept on record and diagnosed (terminal states -> "
                "stage decomposition -> component in isolation -> replication with seeds "
                "fixed beforehand), never rerun until it passes. See the failure protocol in "
                "CLAUDE.md and propsim D-40."
            )
        return entry


# ------------------------------------------------------------------- variants


@dataclass(frozen=True)
class VariantRecord:
    """One configuration tried."""

    variant_id: str
    prereg_id: str
    timestamp: str
    params: dict[str, Any]
    seed: int
    label: str = ""
    exploratory: bool = False

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class VariantCounter:
    """Append-only count of every configuration tried, across sessions.

    Persisted as JSONL so a count survives process restarts -- a variant count that resets
    when the session does is not a count. The `variant_id` is a hash of the parameters, so
    rerunning an identical configuration is recognisable as a repeat rather than inflating
    the count.
    """

    def __init__(self, path: Path | str | None = None):
        self.path = Path(path) if path is not None else RESULTS_DIR / "variants.jsonl"

    @staticmethod
    def variant_id(params: dict[str, Any], seed: int) -> str:
        blob = json.dumps({"params": params, "seed": seed}, sort_keys=True, default=str)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:12]

    def record(
        self,
        *,
        prereg_id: str,
        params: dict[str, Any],
        seed: int,
        label: str = "",
        exploratory: bool = False,
    ) -> VariantRecord:
        rec = VariantRecord(
            variant_id=self.variant_id(params, seed),
            prereg_id=prereg_id,
            timestamp=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            params=params,
            seed=int(seed),
            label=label,
            exploratory=exploratory,
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(rec.as_dict(), sort_keys=True, default=str) + "\n")
        from propedge.reporting.results import note_written   # D-207: the run's own append is not dirt

        note_written(self.path)
        return rec

    def all(self) -> list[dict[str, Any]]:
        if not self.path.is_file():
            return []
        return [
            json.loads(line)
            for line in self.path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def count(self, prereg_id: str | None = None, *, distinct: bool = True) -> int:
        """How many configurations have been tried. Report this with every result."""
        rows = self.all()
        if prereg_id is not None:
            rows = [r for r in rows if r.get("prereg_id") == prereg_id]
        if distinct:
            return len({r["variant_id"] for r in rows})
        return len(rows)


# ------------------------------------------------------------------ the harness


class StrategyFn(Protocol):
    """A candidate strategy.

    Args:
        train: bars for the training window. May be empty for a pure held-out test.
        test: bars for the test window. The only period whose trades count.
        params: the fold's frozen parameters.
        seed: explicit seed for any randomness in the strategy itself.

    Returns:
        A trade log conforming to `propedge.outcomes.tradelog.SCHEMA`, containing **only**
        trades entered within the test window.
    """

    def __call__(
        self, train: pd.DataFrame, test: pd.DataFrame, params: dict[str, Any], seed: int
    ) -> pd.DataFrame: ...


def default_strategy(*args: Any, **kwargs: Any) -> pd.DataFrame:
    """Placeholder: no candidate strategy has been specified yet.

    HUMAN INPUT REQUIRED (T4 in NEXT_STEPS.md). A candidate must be written as executable
    rules -- entry, exit, stop, target, session, the 15:10 CT flatten, instrument, and how the
    stop distance maps to contracts -- and fixed before any test period is touched. The
    conduct guardrails (R > 1, risk well below the maximum, no account-deciding position) are
    constraints on the specification, not filters applied to results afterwards.
    """
    raise NotImplementedError(
        "no candidate strategy is specified. See T4 in NEXT_STEPS.md: strategies are written "
        "as executable rules and fixed before any test period is touched. Pass your own "
        "StrategyFn to WalkForwardHarness.run()."
    )


@dataclass(frozen=True)
class Fold:
    """One walk-forward fold. Parameters are frozen at construction."""

    index: int
    train_start: pd.Timestamp
    train_end: pd.Timestamp
    test_start: pd.Timestamp
    test_end: pd.Timestamp
    params: dict[str, Any] = field(default_factory=dict)

    def describe(self) -> str:
        return (
            f"fold {self.index}: train {self.train_start.date()}..{self.train_end.date()}, "
            f"test {self.test_start.date()}..{self.test_end.date()}"
        )


@dataclass(frozen=True)
class HarnessResult:
    """What a walk-forward run produced."""

    prereg_id: str
    seed: int
    folds: list[Fold]
    tradelogs: list[pd.DataFrame]
    variant: VariantRecord
    variant_count: int
    params: dict[str, Any]

    @property
    def combined(self) -> pd.DataFrame:
        """All folds' test-window trades, in order. The log the edge is measured on."""
        if not self.tradelogs:
            from propedge.outcomes.tradelog import empty_tradelog

            return empty_tradelog()
        return pd.concat(self.tradelogs, ignore_index=True)


def make_folds(
    index: pd.DatetimeIndex,
    *,
    n_folds: int,
    train_days: int,
    test_days: int,
    params: dict[str, Any] | None = None,
    anchored: bool = False,
) -> list[Fold]:
    """Build walk-forward folds over a date index.

    Args:
        index: the data's timestamps.
        n_folds: how many folds.
        train_days: calendar days in each training window.
        test_days: calendar days in each test window.
        params: parameters frozen into every fold.
        anchored: if True, every training window starts at the beginning of the data
            (expanding window); if False, it rolls.

    Folds are contiguous and non-overlapping in their **test** windows, so no trade is
    counted twice and no test window is ever seen during training.
    """
    if n_folds < 1:
        raise ValueError("n_folds must be at least 1")
    idx = pd.DatetimeIndex(index).sort_values()
    if len(idx) == 0:
        raise ValueError("cannot build folds over an empty index")

    start = idx[0]
    end = idx[-1]
    needed = pd.Timedelta(days=train_days + n_folds * test_days)
    if end - start < needed:
        raise ValueError(
            f"data spans {(end - start).days} days but {n_folds} folds of "
            f"{train_days}d train + {test_days}d test need {needed.days} days. "
            "Stage one's sample-size result (propsim D-47) is the binding constraint here: "
            "demonstrating e ~ 0.10 needs 1,667-3,453 trades. See T2 in NEXT_STEPS.md."
        )

    folds: list[Fold] = []
    for i in range(n_folds):
        test_start = start + pd.Timedelta(days=train_days + i * test_days)
        test_end = test_start + pd.Timedelta(days=test_days)
        train_start = start if anchored else test_start - pd.Timedelta(days=train_days)
        folds.append(
            Fold(
                index=i,
                train_start=train_start,
                train_end=test_start,
                test_start=test_start,
                test_end=test_end,
                params=dict(params or {}),
            )
        )
    return folds


class WalkForwardHarness:
    """Runs a strategy over walk-forward folds, under the pre-registration gate.

    Args:
        prereg_id: a registered id from `prereg/REGISTRY.md`. **Required.**
        registry: a `PreregRegistry`; loaded from `prereg/REGISTRY.md` if omitted.
        counter: a `VariantCounter`; defaults to `results/variants.jsonl`.

    Raises:
        UnregisteredRunError: at construction, if `prereg_id` is missing or unregistered.
            The check is at construction rather than at `run()` so a script fails before it
            spends an hour loading data.
    """

    def __init__(
        self,
        prereg_id: str | None,
        *,
        registry: PreregRegistry | None = None,
        counter: VariantCounter | None = None,
    ):
        self.registry = registry if registry is not None else PreregRegistry.load()
        self.prereg = self.registry.require_runnable(prereg_id)
        self.prereg_id = self.prereg.id
        self.counter = counter if counter is not None else VariantCounter()

    def run(
        self,
        bars: pd.DataFrame,
        folds: Sequence[Fold],
        strategy: StrategyFn = default_strategy,
        *,
        seed: int,
        params: dict[str, Any] | None = None,
        label: str = "",
        exploratory: bool = False,
        timestamp_column: str = "timestamp",
        validate_tradelogs: bool = True,
    ) -> HarnessResult:
        """Run `strategy` over `folds`.

        Args:
            bars: the market data, with a timestamp column or a DatetimeIndex.
            folds: from `make_folds`.
            strategy: the candidate. Defaults to a placeholder that raises.
            seed: explicit. Required. Each fold gets `seed + fold.index`, so folds are
                independent but the whole run reproduces from one number.
            params: recorded with the variant. Fold-level params live on the folds.
            label: human-readable name for this configuration.
            exploratory: True if this configuration was chosen **after** seeing results.
                Recorded with the variant and reported separately -- stage one did exactly
                this and labelled it (propsim D-44). Mislabelling a post-hoc choice as
                pre-registered is the failure this whole module guards against.
            validate_tradelogs: check each fold's trades fall inside its test window.

        Returns:
            HarnessResult, whose `.combined` is the log the edge is measured on.
        """
        if not isinstance(seed, int):
            raise TypeError("seed must be an explicit int; every run in this stage is seeded")

        params = dict(params or {})
        variant = self.counter.record(
            prereg_id=self.prereg_id,
            params={"params": params, "n_folds": len(folds)},
            seed=seed,
            label=label,
            exploratory=exploratory,
        )

        ts = (
            bars.index.to_series()
            if isinstance(bars.index, pd.DatetimeIndex)
            else pd.to_datetime(bars[timestamp_column])
        )

        logs: list[pd.DataFrame] = []
        for fold in folds:
            train_mask = (ts >= fold.train_start) & (ts < fold.train_end)
            test_mask = (ts >= fold.test_start) & (ts < fold.test_end)
            log = strategy(
                bars.loc[train_mask.values],
                bars.loc[test_mask.values],
                fold.params,
                seed + fold.index,
            )
            if validate_tradelogs and log is not None and len(log):
                self._check_window(log, fold)
            if log is not None and len(log):
                log = log.copy()
                log["fold"] = fold.index
                log["variant"] = variant.variant_id
                log["prereg_id"] = self.prereg_id
                logs.append(log)

        return HarnessResult(
            prereg_id=self.prereg_id,
            seed=seed,
            folds=list(folds),
            tradelogs=logs,
            variant=variant,
            variant_count=self.counter.count(self.prereg_id),
            params=params,
        )

    @staticmethod
    def _check_window(log: pd.DataFrame, fold: Fold) -> None:
        """Every trade must be entered inside the fold's test window."""
        t = pd.to_datetime(log["timestamp_in"], utc=True)
        lo = pd.Timestamp(fold.test_start).tz_localize("UTC") if pd.Timestamp(fold.test_start).tz is None else pd.Timestamp(fold.test_start).tz_convert("UTC")
        hi = pd.Timestamp(fold.test_end).tz_localize("UTC") if pd.Timestamp(fold.test_end).tz is None else pd.Timestamp(fold.test_end).tz_convert("UTC")
        outside = (t < lo) | (t >= hi)
        if bool(outside.any()):
            raise LookaheadError(
                f"{int(outside.sum())} of {len(log)} trades in {fold.describe()} fall "
                f"outside the test window [{lo}, {hi}). A trade entered outside its test "
                "window either leaks training data into the result or double-counts across "
                "folds."
            )
