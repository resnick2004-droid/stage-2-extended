"""Q-172 (`docs/MEASURES.md` section 6, "to run before the held-out runner is declared"; the lead's option 2): the count
of exact-length-run differences on P-14's **point arm** (as traded) on the search years, so the held-out runner's
M-2 refusal is priced before any held-out record is seen. Counts only: no measure's value is read or written.

    from extended import exact_run_diffs as X
    starts = X.choose_starts(n)                       # the last 252 search starts, plus every 21st earlier one
    rows = X.count_rows(outs, design="p14", arm="point", response="off", n=n)
    frame = X.frame(rows); X.output_problems(frame)

This module imports no engine and reads nothing; `scripts/exact_run_diffs.py` builds the job on the search cut
(`extended.search_cut`), runs `user_beside.run_starts(..., journey=True)` and writes the file.

**The starts** (`choose_starts`): of a job of n search sessions (indices 0 .. n - 1, the last 2023-12-29), the
**last 252** (`CUT_STARTS`: n - 252 .. n - 1, the starts whose 252-session long run reaches the cut -- all but the
first of them are cut by it) and **every 21st earlier start** (`CONTROL_EVERY`: indices 0, 21, 42, ... below n - 252),
the uncut control. Each start's group is written (`cut`, `control`).

**What is checked.** For a start of long-run length L (`min(252, n - s)`, `user_beside.journey_length`), the runner
makes the exact h-session run for each h of `HORIZONS` (21, 63, 90, 126) with h < L (`user_beside._task`), and the
vendored `user_journey._one_start` compares its event days up to h -- the passes, the funded activations and the pay
days (`user_journey.events_upto`) -- with the long run's; a differing h is in the start's `differs`, and the exact run's
record in `rec["alt"][h]`. **The caveat, declared:** near the cut, L falls below h, so the h-session run is not made
and the start is not checked at h -- the 126-session count shrinks over the last 126 starts, the 90-session count over
the last 90, and so on (`checked` is written per horizon and group; `starts` beside it).

**The classification of a difference at h** (`classify`, against the long record's days): for each event kind --
`pass` (a Combine's pass), `funded` (a funded activation), `pay` (a payout's arrival) -- the two runs' days up to h are
paired in order; the first of each kind is named `first_pass`, `first_funded`, `first_payout`, the later ones
`later_pass`, `later_funded`, `later_pay`. A pair whose days differ is `moved` by (exact - long) sessions; a day in the
exact run with no partner in the long one `appeared`, one in the long run only `vanished` (no shift). A difference
whose kinds all agree day for day is impossible (`differs` is the event-day comparison) and is refused.

**The file** (`COLUMNS`): section `checked` -- per response, group and horizon: `starts` (the starts run), `checked`
(the starts with an exact run at h), `differing` (the starts whose exact run at h differs); section `moved` -- per
response, group, horizon, event, change and shift: `count` (events). No date, no money, no measure.
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Iterable, Mapping, Sequence

import pandas as pd

TASK = "Q-172"
HORIZONS = (21, 63, 90, 126)
LONG = 252
CUT_STARTS = 252
CONTROL_EVERY = 21
GROUPS = ("cut", "control")
RESPONSES = ("off", "denial_25")
KINDS = (("pass", "pass_days", "first_pass", "later_pass"), ("funded", "funded_days", "first_funded", "later_funded"),
         ("pay", "pay_days", "first_payout", "later_pay"))
EVENTS = tuple(e for _, _, a, b in KINDS for e in (a, b))
CHANGES = ("moved", "appeared", "vanished")
SECTIONS = ("checked", "moved")
COLUMNS = ("section", "design", "arm", "response", "group", "horizon", "event", "change", "shift", "starts", "checked",
           "differing", "count")


def choose_starts(n: int) -> dict[int, str]:
    """{start: group}: the last `CUT_STARTS` of n starts (`cut`), and every `CONTROL_EVERY`-th earlier one
    (`control`)."""
    n = int(n)
    if n <= CUT_STARTS:
        raise ValueError(f"{TASK}: a job of {n} sessions holds no start before its last {CUT_STARTS}")
    out = {s: "control" for s in range(0, n - CUT_STARTS, CONTROL_EVERY)}
    out.update({s: "cut" for s in range(n - CUT_STARTS, n)})
    return dict(sorted(out.items()))


def expected_checked(s: int, n: int) -> list[int]:
    """The horizons a start's exact runs are made at: h < L = min(252, n - s)."""
    L = min(LONG, int(n) - int(s))
    return [h for h in HORIZONS if h < L]


def _upto(days: Iterable[Any], h: int) -> list[int]:
    return sorted(int(d) for d in days if int(d) <= int(h))


def classify(long_rec: Mapping[str, Any], exact_rec: Mapping[str, Any], h: int) -> list[tuple[str, str, int | None]]:
    """[(event, change, shift)] for one difference at horizon h (the module's docstring); refused when no event
    differs."""
    out: list[tuple[str, str, int | None]] = []
    for _, key, first, later in KINDS:
        a, b = _upto(long_rec[key], h), _upto(exact_rec[key], h)
        for i in range(max(len(a), len(b))):
            name = first if i == 0 else later
            if i < len(a) and i < len(b):
                if a[i] != b[i]:
                    out.append((name, "moved", int(b[i]) - int(a[i])))
            elif i < len(b):
                out.append((name, "appeared", None))
            else:
                out.append((name, "vanished", None))
    if not out:
        raise ValueError(f"{TASK}: a difference at {h} whose event days agree")
    return out


def count_rows(outs: Sequence[Mapping[str, Any]], *, design: str, arm: str, response: str, n: int,
               groups: Mapping[int, str] | None = None) -> list[dict[str, Any]]:
    """The file's rows for one design, arm and response, from `run_starts`' outputs. Refused (`ValueError`) when a
    start's checked horizons are not the runner's rule's, a differing horizon is unchecked or has no exact record."""
    groups = dict(groups if groups is not None else choose_starts(n))
    starts: Counter = Counter()
    checked: Counter = Counter()
    differing: Counter = Counter()
    moved: Counter = Counter()
    seen = set()
    for x in outs:
        rec = x["rec"]
        s = int(rec["start_day"])
        if s in seen or s not in groups:
            raise ValueError(f"{TASK}: start {s} twice, or not a chosen start")
        seen.add(s)
        g = groups[s]
        got = sorted(int(h) for h in x["checked"])
        if got != expected_checked(s, n):
            raise ValueError(f"{TASK}: start {s} checked at {got}, not {expected_checked(s, n)}")
        for h in HORIZONS:
            starts[(g, h)] += 1
            if h in got:
                checked[(g, h)] += 1
        for h in sorted(int(h) for h in x["differs"]):
            if h not in got:
                raise ValueError(f"{TASK}: start {s} differs at {h}, which it did not check")
            alt = (rec.get("alt") or {}).get(str(h))
            if alt is None:
                raise ValueError(f"{TASK}: start {s} differs at {h} with no exact record")
            differing[(g, h)] += 1
            for ev, ch, sh in classify(rec, alt, h):
                moved[(g, h, ev, ch, sh)] += 1
    if seen != set(groups):
        raise ValueError(f"{TASK}: {len(set(groups) - seen)} chosen starts have no output")
    base = {"design": design, "arm": arm, "response": response}
    rows = [{"section": "checked", **base, "group": g, "horizon": h, "starts": starts[(g, h)],
             "checked": checked[(g, h)], "differing": differing[(g, h)]} for g in GROUPS for h in HORIZONS]
    rows += [{"section": "moved", **base, "group": g, "horizon": h, "event": ev, "change": ch, "shift": sh,
              "count": c} for (g, h, ev, ch, sh), c in sorted(moved.items(), key=lambda kv: str(kv[0]))]
    return rows


def frame(rows: Sequence[Mapping[str, Any]]) -> pd.DataFrame:
    out = pd.DataFrame(list(rows), columns=list(COLUMNS))
    for c in ("horizon", "shift", "starts", "checked", "differing", "count"):
        out[c] = out[c].astype("Int64")
    return out


def output_problems(f: pd.DataFrame) -> list[str]:
    """Why a frame is not this reading's: columns, sections, a `checked` row per response, group and horizon, counts
    ordered (differing <= checked <= starts), every `moved` row's horizon differing somewhere, a level-named column."""
    from extended.price_levels import is_level_name

    bad = []
    if list(f.columns) != list(COLUMNS):
        return [f"columns are not COLUMNS: {list(f.columns)}"]
    if [c for c in f.columns if is_level_name(c)]:
        bad.append("a level-named column")
    if not set(f["section"]) <= set(SECTIONS) or "checked" not in set(f["section"]):
        bad.append(f"sections {sorted(set(f['section']))}")
    ch = f[f["section"] == "checked"]
    for (d, a, r), g in ch.groupby(["design", "arm", "response"]):
        have = {(x, int(h)) for x, h in zip(g["group"], g["horizon"])}
        if have != {(x, h) for x in GROUPS for h in HORIZONS} or len(g) != len(have):
            bad.append(f"{d} {a} {r}: the checked rows are not one per group and horizon")
    if ((ch["differing"] > ch["checked"]) | (ch["checked"] > ch["starts"]) | (ch["differing"] < 0)).any():
        bad.append("a checked row's counts out of order")
    mv = f[f["section"] == "moved"]
    if len(mv):
        if not set(mv["event"]) <= set(EVENTS) or not set(mv["change"]) <= set(CHANGES):
            bad.append("a moved row of an unknown event or change")
        keyed = {(d, a, r, g, int(h)): int(n) for d, a, r, g, h, n in
                 zip(ch["design"], ch["arm"], ch["response"], ch["group"], ch["horizon"], ch["differing"])}
        for d, a, r, g, h in zip(mv["design"], mv["arm"], mv["response"], mv["group"], mv["horizon"]):
            if keyed.get((d, a, r, g, int(h)), 0) == 0:
                bad.append(f"a moved row at {d} {a} {r} {g} {h} where nothing differs")
                break
        moved_ok = (mv["change"] == "moved") == mv["shift"].notna()
        if not moved_ok.all():
            bad.append("a shift on a change that is not 'moved', or none on one that is")
    return bad


# ------------------------------------------------------------------------------------------------ the nested cut


def nested_problems(short: Mapping[str, Any], long: Mapping[str, Any], short_last: str,
                    canon=None) -> list[str]:
    """The nested-cut identity's logic: a job built on the shorter cut equals the one built on the longer, block for
    block, on every date up to the shorter cut's last day -- the same dates in the same order, the same block. `short`
    and `long` are {"dates": [...], "blocks": [...]}; `canon` maps a block to a comparable form."""
    canon = canon or (lambda b: b)
    out = []
    sd, ld = [str(d) for d in short["dates"]], [str(d) for d in long["dates"]]
    if len(sd) != len(short["blocks"]) or len(ld) != len(long["blocks"]):
        return ["a job whose blocks and dates differ in length"]
    late = [d for d in sd if d > short_last]
    if late:
        out.append(f"the shorter job holds {len(late)} date(s) past {short_last} (first {late[0]})")
    head = [d for d in ld if d <= short_last]
    if head != sd:
        out.append(f"the dates up to {short_last} differ ({len(sd)} against {len(head)})")
        return out
    bad = [i for i in range(len(sd)) if canon(short["blocks"][i]) != canon(long["blocks"][i])]
    if bad:
        out.append(f"{len(bad)} of {len(sd)} blocks differ (first {sd[bad[0]]})")
    if not sd:
        out.append("nothing compared")
    return out


__all__ = ["TASK", "HORIZONS", "LONG", "CUT_STARTS", "CONTROL_EVERY", "GROUPS", "RESPONSES", "EVENTS", "CHANGES",
           "SECTIONS", "COLUMNS", "choose_starts", "expected_checked", "classify", "count_rows", "frame",
           "output_problems", "nested_problems"]
