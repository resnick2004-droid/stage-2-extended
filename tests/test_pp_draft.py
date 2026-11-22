"""Q-92, Q-92b: reading PP's declaration (`prereg/DRAFT_F-P_payout_policy.md`, renamed `prereg/RD-02_payout_policy.md`
at its pin, E-025 (1)) -- its text, and the numerical rules of its section 9.2 that a synthetic check can hold before any
build: the 90 % interval's windows and its coverage on overlapping series (E-058 (5); the firms reading's review M5,
`docs/reviews/DRAFT_RD_firms_2026-11-16.md`, and its Appendix A1).

What it checks (no engine, no bar, no result file; synthetic series only):

- **the windows** (9.2 item 1): a block's starts cut into windows of h consecutive starts from its first start, every
  other window kept -- a start reads its own h sessions, so two kept windows share no session, while adjacent windows
  share h - 1 sessions; the count n_w;
- **the interval, the sign count, the zero series, the MDD** (9.2 items 2, 3, 5, 6): the two-sided 90 % t interval only
  from 4 kept windows with a spread; the sign count; "identical on these trades" for a series zero on every start; the
  MDD (t(0.95) + t(0.80)) x the kept windows' standard error, which normal window means at that true mean put wholly
  above zero in about 80 % of draws;
- **the coverage on overlapping series** (9.2 item 7; T-6's small fixed setting, seed 20261948 under the key
  `[20261948, 0, case]` -- the reading's own honesty table draws under `[20261948, 1, ...]`): on per-start h-session
  series built from independent sessions, as the reading's own series are built, the 90 % interval on adjacent windows
  covers clearly below nominal and on separated windows near it; the second version's honesty check (independent
  window means) reports near nominal for the adjacent rule -- it cannot see the shortfall;
- **the declared null shapes have the known zero mean** they are declared with (the lumpy and the persistent ones);
- **the coverage label** (9.2 item 7; Q-102's M1): it reads gauss, ahead and paired only, and is not constant -- off on
  them at 13 kept windows (h = 63), where a lumpy shape covers below 0.88;
- **the text**: in pin-time form (E-075: the title and status of the pinned file, the `id` row with `RD-xx`, the
  `confirmation_tests_on_this_market` row, `prereg_id` as that id); every pinned calendar cited by its file's own LF
  sha256; one `Judged-block reads:` line whose purposes `extended.reader.declared_purposes` parses, none choosing, none
  `identity` or `registered_design`; section 11's seed block 20261940..20261949 once each, a seed in use or reserved
  found in no other declaration, nowhere in the vendored snapshot and in no review's or audit's scratch; the tracked
  code and tests holding a seed of the block exactly the ones section 11 names; no level in section 9.2; section 0
  citing every source row;
- **the reader, end to end** (as `tests/test_rd_firms_draft.py` does for the firms reading): this text, pinned in a
  temporary tree, authorises the engine's reads under each purpose of its line once, and a further run only under
  `repeat=` naming a row that names the file (section 14, E-053).

The bands below are fixed from theory and from the review's A1 (adjacent 0.82-0.84, separated 0.87-0.91 at h = 63)
before this file first ran; a failure is diagnosed, never met by widening a band.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path

import numpy as np
import pytest
from scipy import stats

from extended import reader
import heldout_verdict_rows as VR  # noqa: E402  (Q-194c: the joint held-out test, ledgered, and its verdict)

ROOT = Path(__file__).resolve().parent.parent
PREREG = ROOT / "prereg"
VENDOR = ROOT / "vendor"
VENDOR_DATA = VENDOR / "stage2" / "data"                     # the licensed bars and atlas: never scanned
SCRATCH_DIRS = (ROOT / "docs" / "reviews", ROOT / "docs" / "audits")
TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".csv", ".json", ".txt", ".sha256", ".toml", ".cfg", ".ini"}

#: 20261940..20261949, written without its exclusive end (that number is Q-18's seed, `tests/test_p14_validation.py`)
SEED_BLOCK = tuple(20261940 + i for i in range(10))
#: 9.2 item 7's seed; T-6 draws under the key's second element 0, the reading's honesty table under 1
COVERAGE_SEED = 20261948
T6_KEY = 0

LEVEL = 0.90               # 9.2 item 2: the two-sided interval's coverage
MIN_WINDOWS = 4            # 9.2 item 2: no interval below this many kept windows
H = 63                     # the horizon of P and months 1-3 (5 item 3)
REPS = 4000                # series per synthetic setting in this test (the reading's own table: 20,000)
CHUNK = 500                # series generated at once (memory: one small block at a time)

SEED_ROW = re.compile(r"^\|\s*(\d{8})\s*\|\s*([^|]+?)\s*\|", re.MULTILINE)
#: 9.2 item 7 (Q-102's M1): the label reads only the shapes built like the reading's own series, at this floor
LABEL_SHAPES = ("gauss", "ahead", "paired")
LABEL_FLOOR = 0.88


# ----------------------------------------------------------------------------------------- the declared method


def windows(n_starts: int, h: int, rule: str = "separated") -> list[tuple[int, int]]:
    """9.2 item 1: the [first, last + 1) start indices of the windows a reading uses. The block's starts in order cut
    into consecutive windows of h starts from the first (a last incomplete window dropped); `separated` keeps every
    other one from the first (the declared rule), `adjacent` keeps all (the second version's rule)."""
    n_all = int(n_starts) // int(h)
    if rule == "separated":
        js = range(0, n_all, 2)
    elif rule == "adjacent":
        js = range(n_all)
    else:
        raise ValueError(rule)
    return [(j * h, (j + 1) * h) for j in js]


def starts_needed(n_w: int, h: int, rule: str) -> int:
    """The fewest starts that give n_w windows under `rule`."""
    return ((2 * n_w - 1) if rule == "separated" else n_w) * h


def sessions_read(window: tuple[int, int], h: int) -> set[int]:
    """The sessions a window's starts read: start s reads sessions s .. s + h - 1 (U1's starts are consecutive
    sessions, `USER_MILESTONES.md`)."""
    a, b = window
    return set(range(a, b - 1 + h))


def t_interval(means) -> tuple[float, float] | None:
    """9.2 item 2: the two-sided 90 % Student-t interval on the kept windows' means, n_w - 1 degrees of freedom;
    None below `MIN_WINDOWS` windows or with no spread (9.2 item 6)."""
    m = np.asarray(means, float)
    n = m.size
    if n < MIN_WINDOWS:
        return None
    se = m.std(ddof=1) / np.sqrt(n)
    if not se > 0:
        return None
    t = stats.t.ppf(0.5 + LEVEL / 2, n - 1)
    return float(m.mean() - t * se), float(m.mean() + t * se)


def mdd(means) -> float | None:
    """9.2 item 5: (t(0.95; n_w - 1) + t(0.80; n_w - 1)) x the kept windows' standard error."""
    m = np.asarray(means, float)
    n = m.size
    if n < MIN_WINDOWS:
        return None
    se = m.std(ddof=1) / np.sqrt(n)
    return float((stats.t.ppf(0.95, n - 1) + stats.t.ppf(0.80, n - 1)) * se)


def sign_count(cell_means, base_means) -> tuple[int, int, int]:
    """9.2 item 3: in how many kept windows the cell's mean is above, equal to and below its base's."""
    c, b = np.asarray(cell_means, float), np.asarray(base_means, float)
    return int(np.sum(c > b)), int(np.sum(c == b)), int(np.sum(c < b))


def describe(per_start_diff, h: int) -> str:
    """9.2 item 6: what a reading prints when its series has nothing to interval."""
    d = np.asarray(per_start_diff, float)
    if not np.any(d != 0):
        return "identical on these trades"
    w = windows(d.size, h)
    if len(w) < MIN_WINDOWS:
        return "too few separated windows for an interval"
    return "interval"


# --------------------------------------------------------------------------- the synthetic series (9.2 item 7)


def per_start_means(x: np.ndarray, h: int) -> np.ndarray:
    """(reps, n_sessions) per-session values -> (reps, n_sessions - h + 1): each start's mean over its own h sessions."""
    c = np.zeros((x.shape[0], x.shape[1] + 1))
    np.cumsum(x, axis=1, out=c[:, 1:])
    return (c[:, h:] - c[:, :-h]) / h


def per_start_sums(x: np.ndarray, h: int) -> np.ndarray:
    return per_start_means(x, h) * h


def lumpy_sessions(rng, shape: tuple[int, int], h: int, p: float, s: float, g: float = 0.01) -> np.ndarray:
    """The skewed, lumpy shape on sessions: +g with probability 1 - q and -g(1 - q)/q with probability q, q = p / h
    (p rare sessions expected in h), plus N(0, h s^2) noise (a start's h-session mean has noise s). Mean exactly 0."""
    q = p / h
    rare = rng.random(shape) < q
    return np.where(rare, -g * (1 - q) / q, g) + rng.normal(0.0, s * np.sqrt(h), shape)


def persistent_states(rng, shape: tuple[int, int], h: int, p: float) -> np.ndarray:
    """The persistent shape's rare sessions: a two-state chain started from its stationary law; an ordinary session is
    followed by a rare one with probability r = p / h, a rare one by another with probability 1 - 1/h (episodes of
    mean length h). Its stationary rare share is pi = r / (r + 1/h)."""
    reps, n = shape
    r, stay = p / h, 1.0 - 1.0 / h
    pi = r / (r + 1.0 / h)
    out = np.empty(shape, bool)
    out[:, 0] = rng.random(reps) < pi
    u = rng.random(shape)
    for t in range(1, n):
        out[:, t] = np.where(out[:, t - 1], u[:, t] < stay, u[:, t] < r)
    return out


def persistent_sessions(rng, shape: tuple[int, int], h: int, p: float, s: float, g: float = 0.01) -> np.ndarray:
    r = p / h
    pi = r / (r + 1.0 / h)
    rare = persistent_states(rng, shape, h, p)
    return np.where(rare, -g * (1 - pi) / pi, g) + rng.normal(0.0, s * np.sqrt(h), shape)


def start_series(kind: str, rng, reps: int, n_starts: int, h: int, p: float | None = None,
                 s: float | None = None) -> np.ndarray:
    """(reps, n_starts) per-start series of known zero mean, built from sessions as the reading's own are:
    `gauss` a start's h-session mean of N(0, 1) sessions; `ahead` 1{its h-session sum > 0} - 1/2; `paired` the
    difference of two such indicators on walks sharing a common part (0.8 z + 0.6 e each)."""
    n_sess = n_starts + h - 1
    if kind == "gauss":
        return per_start_means(rng.standard_normal((reps, n_sess)), h)
    if kind == "ahead":
        return (per_start_sums(rng.standard_normal((reps, n_sess)), h) > 0).astype(float) - 0.5
    if kind == "paired":
        z = rng.standard_normal((reps, n_sess))
        a = per_start_sums(0.8 * z + 0.6 * rng.standard_normal((reps, n_sess)), h)
        b = per_start_sums(0.8 * z + 0.6 * rng.standard_normal((reps, n_sess)), h)
        return (a > 0).astype(float) - (b > 0).astype(float)
    if kind in ("lumpy", "persistent"):
        make = lumpy_sessions if kind == "lumpy" else persistent_sessions
        return per_start_means(make(rng, (reps, n_sess), h, p, s), h)
    raise ValueError(kind)


def label(cov: dict[str, float]) -> bool:
    """9.2 item 7's label: "under-covers at this window count" where the lowest coverage of gauss, ahead and paired is
    below 0.88; the lumpy and persistent shapes are printed beside and never set it."""
    return min(float(cov[k]) for k in LABEL_SHAPES) < LABEL_FLOOR


def coverage(kind: str, n_w: int, rule: str, case: int, h: int = H, reps: int = REPS, p: float | None = None,
             s: float | None = None) -> float:
    """The share of `reps` zero-mean series whose 90 % interval on `rule`'s windows holds 0."""
    rng = np.random.default_rng([COVERAGE_SEED, T6_KEY, case])
    n_starts = starts_needed(n_w, h, rule)
    w = windows(n_starts, h, rule)
    assert len(w) == n_w
    t = stats.t.ppf(0.5 + LEVEL / 2, n_w - 1)
    hits = 0
    for k in range(0, reps, CHUNK):
        y = start_series(kind, rng, min(CHUNK, reps - k), n_starts, h, p, s)
        m = np.stack([y[:, a:b].mean(axis=1) for a, b in w], axis=1)
        se = m.std(axis=1, ddof=1) / np.sqrt(n_w)
        hits += int(np.sum(np.abs(m.mean(axis=1)) <= t * se))
    return hits / reps


def coverage_independent_means(n_w: int, case: int, reps: int = REPS) -> float:
    """The second version's honesty check: the same interval on independent N(0, 1) window means."""
    rng = np.random.default_rng([COVERAGE_SEED, T6_KEY, case])
    m = rng.standard_normal((reps, n_w))
    se = m.std(axis=1, ddof=1) / np.sqrt(n_w)
    return float(np.mean(np.abs(m.mean(axis=1)) <= stats.t.ppf(0.5 + LEVEL / 2, n_w - 1) * se))


# ------------------------------------------------------------------------------------------------------- tests


@pytest.mark.parametrize("h", [21, 63, 252])
def test_kept_windows_share_no_session_and_adjacent_windows_do(h):
    n_starts = 11 * h + 5                                      # 11 whole windows and a dropped remainder
    adj, sep = windows(n_starts, h, "adjacent"), windows(n_starts, h, "separated")
    assert len(adj) == 11 and len(sep) == 6                    # every other window from the first
    assert sep == adj[::2]
    for w1, w2 in zip(adj, adj[1:]):                           # neighbours share h - 1 sessions
        assert len(sessions_read(w1, h) & sessions_read(w2, h)) == h - 1
    for i, w1 in enumerate(sep):                               # kept windows share none
        for w2 in sep[i + 1:]:
            assert not sessions_read(w1, h) & sessions_read(w2, h)
    assert all(b <= n_starts for _, b in sep)


def test_interval_only_from_four_kept_windows_with_spread():
    assert t_interval([0.1, -0.2, 0.3]) is None                # 3 windows: no interval
    assert t_interval([0.2] * 4) is None                       # no spread: no interval (9.2 item 6)
    m = np.array([0.1, -0.2, 0.3, 0.05])
    lo, hi = t_interval(m)
    half = stats.t.ppf(0.95, 3) * m.std(ddof=1) / 2.0
    assert lo == pytest.approx(m.mean() - half) and hi == pytest.approx(m.mean() + half)
    assert describe(np.zeros(5 * H), H) == "identical on these trades"
    assert describe(np.r_[np.zeros(6 * H), 1.0], H) == "too few separated windows for an interval"   # 3 kept
    assert describe(np.r_[np.zeros(7 * H), 1.0], H) == "interval"                                    # 4 kept


def test_sign_count_on_kept_windows():
    assert sign_count([1.0, 0.0, -1.0, 2.0], [0.0, 0.0, 0.0, 3.0]) == (1, 1, 2)


def test_mdd_is_the_difference_the_interval_excludes_zero_for_about_80_percent_of_draws():
    rng = np.random.default_rng([COVERAGE_SEED, T6_KEY, 90])
    for n_w in (4, 9, 13):
        m = rng.standard_normal((REPS, n_w))
        se_true = 1.0 / np.sqrt(n_w)
        d = (stats.t.ppf(0.95, n_w - 1) + stats.t.ppf(0.80, n_w - 1)) * se_true
        assert mdd(m[0]) == pytest.approx((stats.t.ppf(0.95, n_w - 1) + stats.t.ppf(0.80, n_w - 1))
                                          * m[0].std(ddof=1) / np.sqrt(n_w))
        x = m + d
        lower = x.mean(axis=1) - stats.t.ppf(0.95, n_w - 1) * x.std(axis=1, ddof=1) / np.sqrt(n_w)
        rate = float(np.mean(lower > 0))
        exact = 1.0 - stats.nct.cdf(stats.t.ppf(0.95, n_w - 1), n_w - 1, d / se_true)
        assert 0.79 < exact < 0.82                             # the noncentral t: about 80 %
        assert abs(rate - exact) < 0.03, (n_w, rate, exact)


@pytest.mark.parametrize("kind,n_w,case", [("gauss", 5, 1), ("gauss", 9, 2), ("ahead", 9, 3)])
def test_adjacent_windows_undercover_and_separated_windows_do_not(kind, n_w, case):
    """E-058 (5): adjacent h-start windows share sessions, so the 90 % interval on them covers clearly below 0.90;
    windows separated by h starts restore it (the review's A1: 0.82-0.84 against 0.87-0.91 at h = 63)."""
    adjacent = coverage(kind, n_w, "adjacent", case)
    separated = coverage(kind, n_w, "separated", 100 + case)
    assert adjacent < 0.87, (kind, n_w, adjacent)
    lo = 0.87 if kind == "gauss" else 0.86
    assert lo <= separated <= 0.93, (kind, n_w, separated)


@pytest.mark.parametrize("n_w,case", [(5, 11), (9, 12)])
def test_the_second_versions_honesty_check_cannot_see_the_shortfall(n_w, case):
    """On independent window means the interval covers near 0.90 whatever the windows were: the check the second
    version declared certifies the adjacent rule that under-covers above."""
    assert 0.87 <= coverage_independent_means(n_w, case) <= 0.93


def test_the_declared_lumpy_and_persistent_shapes_have_zero_mean():
    g = 0.01
    for p in (0.05, 0.10, 0.20):
        q = p / H
        assert (1 - q) * g - q * g * (1 - q) / q == pytest.approx(0.0, abs=1e-15)
        r = p / H
        pi = r / (r + 1.0 / H)
        assert (1 - pi) * g - pi * g * (1 - pi) / pi == pytest.approx(0.0, abs=1e-15)
    rng = np.random.default_rng([COVERAGE_SEED, T6_KEY, 50])
    # the chain's rare share is its stationary pi (started there, it stays there)
    st = persistent_states(rng, (400, 2000), H, 0.10)
    r = 0.10 / H
    pi = r / (r + 1.0 / H)
    assert abs(st.mean() - pi) < 0.01, (st.mean(), pi)
    assert abs(st[:, 0].mean() - pi) < 0.05 and abs(st[:, -1].mean() - pi) < 0.05
    # and a start's mean over its h sessions is centred at zero under both shapes (within 4 standard errors)
    for make in (lambda: lumpy_sessions(rng, (400, 2 * H), H, 0.10, 0.005),
                 lambda: persistent_sessions(rng, (400, 2 * H), H, 0.10, 0.005)):
        vals = np.concatenate([per_start_means(make(), H)[:, 0] for _ in range(10)])
        assert abs(vals.mean()) < 4 * vals.std(ddof=1) / np.sqrt(vals.size)


def test_the_label_reads_the_three_regular_shapes_only_and_is_not_constant():
    """Q-102's M1: the label fired on every interval when it read the lowest of all 21 shapes. It reads gauss, ahead
    and paired only: off where they cover near nominal -- here at 13 kept windows at h = 63, where a lumpy shape covers
    well below 0.88 (the old rule would have fired) -- and on where one of them is below the floor."""
    rare = {"lumpy_0.05_0.005": 0.40, "persistent_0.05_0.0025": 0.35}
    assert not label({"gauss": 0.90, "ahead": 0.89, "paired": 0.91, **rare})
    assert label({"gauss": 0.90, "ahead": LABEL_FLOOR - 0.01, "paired": 0.91, **rare})
    cov = {k: coverage(k, 13, "separated", 200 + i) for i, k in enumerate(LABEL_SHAPES)}
    assert all(v >= LABEL_FLOOR for v in cov.values()), cov
    lumpy = coverage("lumpy", 13, "separated", 210, p=0.05, s=0.005)
    assert lumpy < LABEL_FLOOR, lumpy
    assert not label({**cov, "lumpy_0.05_0.005": lumpy})
    assert min([*cov.values(), lumpy]) < LABEL_FLOOR                    # the third text's rule would have fired


# ------------------------------------------------------------------------------------------------- the text


def draft_path() -> Path:
    found = sorted(PREREG.glob("DRAFT_F-P_payout_policy.md")) + sorted(PREREG.glob("RD-*payout*.md"))
    assert len(found) == 1, f"exactly one payout-policy declaration expected under prereg/, found {found}"
    return found[0]


def text() -> str:
    return draft_path().read_text(encoding="utf-8").replace("\r\n", "\n")


def section(body: str, heading: str) -> str:
    """The text from the heading line starting with `heading` to the next heading of the same or a higher level."""
    level = len(heading.split(" ", 1)[0])
    lines = body.split("\n")
    start = None
    for i, line in enumerate(lines):
        if start is None and line.startswith(heading):
            start = i
            continue
        if start is not None and line.startswith("#"):
            hashes = len(line) - len(line.lstrip("#"))
            if hashes <= level and line[hashes:hashes + 1] == " ":
                return "\n".join(lines[start:i])
    assert start is not None, f"no heading starting {heading!r}"
    return "\n".join(lines[start:])


def test_judged_block_purposes_are_declarable_and_choose_nothing():
    body = text()
    assert len(reader.DECLARED_LINE.findall(body)) == 1, "exactly one 'Judged-block reads:' line"
    purposes = reader.declared_purposes(body)
    assert purposes, "the 'Judged-block reads:' line names no purpose"
    for p in purposes:
        assert reader.PURPOSE.fullmatch(p), p
        assert not reader._choice_purpose(p), f"{p} is a choosing or fitting purpose"
    assert reader.IDENTITY not in purposes, "identities are declared by their own E-row, from identity/*.py"
    assert reader.REGISTERED_DESIGN not in purposes, "a declaration's file can never use registered_design (E-037)"


def _text_files(base: Path, *, skip: tuple[Path, ...] = ()) -> list[Path]:
    out = []
    for p in base.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in TEXT_SUFFIXES or ".git" in p.parts:
            continue
        if any(s == p or s in p.parents for s in skip):
            continue
        out.append(p)
    return out


def _occurrences(seed: int, files) -> list[str]:
    pat = re.compile(rb"\b" + str(seed).encode() + rb"\b")
    return [str(p.relative_to(ROOT)) for p in files if pat.search(p.read_bytes())]


def test_seed_block_is_its_own_and_its_live_seeds_are_unused_elsewhere():
    rows = SEED_ROW.findall(section(text(), "## 11."))
    seeds = [int(s) for s, _ in rows]
    assert sorted(seeds) == list(SEED_BLOCK), f"section 11 must list 20261940..20261949 once each, got {seeds}"
    me = draft_path()
    others = [p for p in PREREG.glob("*.md") if p != me]
    vendored = _text_files(VENDOR, skip=(VENDOR_DATA,))
    scratch = [p for d in SCRATCH_DIRS if d.is_dir() for p in _text_files(d)]
    problems, live = [], 0
    for s, status in rows:
        status = status.strip().strip("*").strip().lower()
        if status.startswith("in use") or status.startswith("reserved"):
            live += 1
            hits = _occurrences(int(s), others) + _occurrences(int(s), vendored) + _occurrences(int(s), scratch)
            if hits:
                problems.append(f"{s} ({status}) is also in {hits}")
        elif not status.startswith("retired"):
            problems.append(f"{s}: status {status!r} is not 'in use', 'reserved' or 'retired'")
    assert not problems, "\n".join(problems)
    assert live >= 1


def test_no_level_in_the_uncertainty_section():
    s92 = section(text(), "### 9.2")
    assert "one-sided" not in s92 and "Q-16" not in s92, "a described reading has no level (E-023 (1), E-025)"
    assert not re.search(r"\b(?:at|level)\s+0\.05\b", s92), "a described reading has no level (E-023 (1), E-025)"
    head = text().split("\n## 0.", 1)[0]
    assert re.search(r"^\| level, pass line, pick \| \*\*none\*\* \|$", head, re.MULTILINE)


#: stand-ins for files the U1 replay's engine opens (Q-48's names), in the temporary tree only
ENGINE_FILES = ("vendor/stage2/data/bars/NQ/bars.parquet", "vendor/stage2/data/atlas/A3/walks.parquet")


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)


def test_once_pinned_its_line_authorises_one_run_per_purpose_and_a_rerun_needs_a_row(tmp_path, monkeypatch):
    """Section 5 item 6 and section 14 (E-041, E-053): this draft's own text, pinned as `prereg/RD-02_payout_policy.md`
    by a synthetic row in a temporary tree, authorises the engine's whole-window reads under each purpose of its line,
    inside a (simulated) clean run, ledgered as a described reading; another run under the same purpose is refused,
    unless `repeat=` names a row naming the file -- one row, one more run. Q-158, Q-194c: the tree carries NQ's
    joint held-out test, its read ledgered, and its verdict row, which a described reading's judged read needs (the
    reader's held-out rule 4)."""
    rel = "prereg/RD-02_payout_policy.md"
    body = text()
    pin = hashlib.sha256(body.encode("utf-8")).hexdigest()
    runs = tmp_path / "runs"
    t = runs / "rd-pp-sim"
    (t / "prereg").mkdir(parents=True)
    (t / rel).write_bytes(body.encode("utf-8"))
    (t / "DECISIONS.md").write_text(
        "# Decisions (synthetic, Q-92)\n\n| id | date | decision | basis |\n|---|---|---|---|\n"
        f"| E-990 | 2026-11-16 | **RD-02 declared**, `{rel}` sha256 `{pin}` | test |\n"
        f"| E-991 | 2026-11-16 | **A rerun of RD-02** (`{rel}`) after a synthetic restart | test |\n",
        encoding="utf-8")
    (t / ".gitignore").write_text("vendor/stage2/data/\nresults/\n", encoding="utf-8")
    for f in ENGINE_FILES:
        (t / f).parent.mkdir(parents=True, exist_ok=True)
        (t / f).write_bytes(b"a stand-in, never read as data\n")
    for args in (("init", "-q", "-b", "master"), ("config", "user.email", "t@example.invalid"),
                 ("config", "user.name", "t"), ("config", "core.autocrlf", "false"), ("add", "-A"),
                 ("commit", "-q", "-m", "the pinned reading")):
        _git(t, *args)
    # Q-194c: NQ's joint held-out test read through the reader (ledgered) and its verdict row, which a described
    # reading's judged read needs (rule 4)
    VR.settle(t, [t / ENGINE_FILES[0]])
    monkeypatch.setattr(reader, "RUNS_DIR", runs)
    monkeypatch.setenv(reader.CLEAN_RUN_ENV, t.name)
    monkeypatch.setenv(reader.RUN_ID_ENV, f"{t.name}@1")
    kw = dict(files=[t / f for f in ENGINE_FILES], what="reading PP (Q-92's check)", repo=t)
    purposes = sorted(reader.declared_purposes(body))
    for p in purposes:
        a = reader.authorise_engine_read("2020-01-02", "2026-07-16", purpose=p, declaration=rel, **kw)
        assert (a.judged, a.ledgered, a.kind, a.declaration_sha256) == (True, True, "described_reading", pin), (p, a)
    monkeypatch.setenv(reader.RUN_ID_ENV, f"{t.name}@2")                # a restart: another run
    with pytest.raises(reader.JudgedBlockReadTwice, match="once"):
        reader.authorise_engine_read("2020-01-02", "2026-07-16", purpose=purposes[0], declaration=rel, **kw)
    a = reader.authorise_engine_read("2020-01-02", "2026-07-16", purpose=purposes[0], declaration=rel,
                                     repeat="E-991", **kw)
    assert a.judged and a.ledgered
    monkeypatch.setenv(reader.RUN_ID_ENV, f"{t.name}@3")                # the same row twice: refused
    with pytest.raises(reader.JudgedBlockReadTwice, match="one row, one more run"):
        reader.authorise_engine_read("2020-01-02", "2026-07-16", purpose=purposes[0], declaration=rel,
                                     repeat="E-991", **kw)
    with pytest.raises(reader.JudgedBlockSealed, match="does not name"):  # no such row: refused
        reader.authorise_engine_read("2020-01-02", "2026-07-16", purpose=purposes[0], declaration=rel,
                                     repeat="E-992", **kw)


def test_section_0_maps_every_change_to_its_source_row():
    s0 = section(text(), "## 0.")
    for row in ("E-058", "E-023", "E-025", "E-041", "E-053", "E-026", "E-028", "E-044", "E-049", "E-046", "E-024",
                "E-007", "E-034", "E-029", "E-050", "E-059", "E-068", "Q-102", "E-075"):
        assert re.search(rf"\b{row}\b", s0), f"section 0 does not cite {row}"


def _sha256_lf(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


#: the placeholder id in the declaration's text before its pin; the pin substitutes `RD-02` for it
PLACEHOLDER = "RD-xx"


def test_the_text_is_in_pin_time_form():
    """E-075: the title, status and header are true of the pinned file `prereg/RD-02_payout_policy.md`. The pin
    substitutes `RD-02` for the placeholder id on exactly three lines -- the title, the `id` row, section 14's
    `prereg_id` -- and changes nothing else, so the placeholder appears on no other line (before the pin; after it, the
    same three lines carry `RD-02`)."""
    body = text()
    rid = PLACEHOLDER if draft_path().name.startswith("DRAFT_") else "RD-02"
    head = body.split("\n## 0.", 1)[0]
    status = head.split("**Its text's history.**", 1)[0]
    assert head.startswith(f"# {rid}: "), head[:80]
    for stale in ("DRAFT", "Not pinned", "not declared", "this draft"):
        assert stale not in status, stale
    assert re.search(rf"^\| id \| {rid} \(`prereg/RD-02_payout_policy\.md` at the pin\)", head, re.MULTILINE)
    assert re.search(r"^\| `confirmation_tests_on_this_market` \| 3: ", head, re.MULTILINE)
    assert f"`prereg_id`: `{rid}`" in section(body, "## 14.")
    assert "RD-nn" not in body
    lines = [ln for ln in body.split("\n") if PLACEHOLDER in ln]
    if rid == PLACEHOLDER:
        assert len(lines) == 3, lines
        assert lines[0].startswith("# RD-xx: ") and lines[1].startswith("| id | RD-xx (")
        assert "`prereg_id`: `RD-xx`" in lines[2]
    else:
        assert not lines, lines


def test_every_pinned_calendar_is_cited_by_its_own_lf_sha256():
    """E-075: each `config/calendar_*.csv` the text reads is cited with the LF sha256 of the file itself (E-029,
    E-050), and every such citation is right."""
    body = text()
    cited = set(re.findall(r"`(config/calendar_[a-z_]+\.csv)`", body))
    assert cited == {"config/calendar_early_closes.csv", "config/calendar_fomc_minutes.csv"}, cited
    pairs = re.findall(r"`(config/calendar_[a-z_]+\.csv)`[^`]{0,40}sha256\s*`([0-9a-f]{64})`", body)
    assert {c for c, _ in pairs} == cited, pairs
    for c, h in pairs:
        assert h == _sha256_lf(ROOT / c), (c, h)


def test_the_tracked_code_and_tests_holding_the_block_are_exactly_section_11s():
    """E-075: section 11's seed search states exactly what it finds, repository code and tests included. Every tracked
    `.py` file holding a seed of the block (word-bounded) is named in section 11's list, and every `.py` file named
    there holds one."""
    out = subprocess.run(["git", "ls-files", "*.py"], cwd=ROOT, capture_output=True, text=True, check=True)
    pat = re.compile(rb"\b2026194[0-9]\b")
    found = {rel for rel in out.stdout.splitlines() if pat.search((ROOT / rel).read_bytes())}
    named = set(re.findall(r"`([\w/.-]+\.py)`", section(text(), "## 11.").split("**The check", 1)[1]
                           .split("**Inherited", 1)[0]))
    assert found == named, {"found, not named": sorted(found - named), "named, not found": sorted(named - found)}
