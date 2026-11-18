"""RD-05's A-14, the composition (`prereg/RD-05_firm_modes.md` 4.3 A-14; 2.1, 2.2, 9.5): each configuration's contract
applied to the coin engine -- its evaluation mode-corners and its funded modes' corners (Appendix M), and the pairs 9.5
joins -- and, for part F, to a design's replay and gate arguments as RD-01's A-1 (`extended/firms.py`).

**Built here: the coin side** (`corners_of`, `join_pairs`, `coin_spec`). **Not built: part F's side**
(`replay_args`, `gate_args`): `TS` leaving every argument unchanged, each plan's rules, allowances and costs on the
replay, `LU40` / `LU50` by Stage 2's `rc150_firm_split.lucid_setup`; they refuse (`NotBuilt`) until built with their
account classes, so nothing of part F can run from this commit.
"""
from __future__ import annotations

from typing import Any

from extended import modes_terms as M


class NotBuilt(RuntimeError):
    """Part F's composition is not built at this commit."""


def corners_of(config: str) -> dict[str, list[M.ModeCorner]]:
    """A configuration's evaluation mode-corners and its funded modes' corners (Appendix M)."""
    emode = M.EVAL_OF[config]
    return {M.EVAL: [m for m in M.MODE_CORNERS if m.kind == M.EVAL and m.mode == emode],
            M.FUNDED: [m for m in M.MODE_CORNERS if m.kind == M.FUNDED and m.mode in M.FUNDED_OF[config]]}


def join_pairs(config: str) -> list[tuple[M.ModeCorner, M.ModeCorner]]:
    """9.5: every evaluation corner with every funded corner of its funded modes -- strict with strict and lenient
    with lenient where both have two corners, a single corner with each."""
    c = corners_of(config)
    out = []
    for e in c[M.EVAL]:
        for f in c[M.FUNDED]:
            if e.corner != M.SINGLE and f.corner != M.SINGLE and e.corner != f.corner:
                continue
            out.append((e, f))
    return out


def coin_spec(m: M.ModeCorner, w: float, r: float, **kw: Any) -> Any:
    from extended import modes_engine as E

    return E.spec_for(m, w, r, **kw)


def replay_args(*_a: Any, **_k: Any) -> Any:
    raise NotBuilt("A-14's part-F composition (a plan on a design's replay arguments) is not built")


def gate_args(*_a: Any, **_k: Any) -> Any:
    raise NotBuilt("A-14's part-F composition (a plan on a design's gate arguments) is not built")


__all__ = ["NotBuilt", "corners_of", "join_pairs", "coin_spec", "replay_args", "gate_args"]
