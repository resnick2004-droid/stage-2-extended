"""Q-106's M1: an independent route to each gate path's counts, for T-10's gate leg (`tests/pp_synthetic.py`).

`CollectingRecorder` is a `extended.place_records.PlaceRecorder` whose reducer runs each path as the vendored
`_one_path` runs it, inside `extended.payout_policy.collecting()` in the process that runs the path, and keeps that
path's accounts' counts under its seed -- so the counts come home with the path itself, not through the channel's
draw wrapper (`CountingDraws`). The gate is called with it as its `recorder` (the counters' channel off), and its
per-path counts are compared with the channel's. A module of its own, so the classes pickle to a path worker.
"""
from __future__ import annotations

from dataclasses import fields
from typing import Any

from extended import payout_policy as PP
from extended import place_records as PR


class CollectingReducer(PR.PathReducer):
    def __init__(self, shift: str, enforcement_p: float):
        self.shift, self.enforcement_p = str(shift), float(enforcement_p)
        self.columns = None
        self.keep_trades = self.keep_days = False

    def one_path(self, protocol: Any, path_index: int, path_seed: int, path_kwargs: dict[str, Any],
                 draw_factories_for_path: Any, flip_for_path: Any, wallet_for_path: Any) -> PR.RecordedPath:
        with PP.collecting() as got:
            x = PR._one_path(protocol, path_index, path_seed, path_kwargs, draw_factories_for_path, flip_for_path,
                             wallet_for_path)
        kept = PR.replace(x, trades=(), account_days=(), campaign_days=())
        return PR.RecordedPath(**{f.name: getattr(kept, f.name) for f in fields(PR.LockstepPath)},
                               place_record={"seed": int(path_seed), "counts": list(got)})


class CollectingRecorder(PR.PlaceRecorder):
    def __init__(self) -> None:
        super().__init__()
        self.got: dict[tuple[str, float], dict[int, list]] = {}

    def wants(self, shift: str, enforcement_p: float) -> bool:
        return True

    def reducer(self, shift: str, enforcement_p: float, blk: Any, rules: Any) -> CollectingReducer:
        return CollectingReducer(shift, enforcement_p)

    def collect(self, shift: str, enforcement_p: float, paths: list, **kw: Any) -> list:
        self.got[(str(shift), float(enforcement_p))] = {int(x.place_record["seed"]): x.place_record["counts"]
                                                        for x in paths}
        return [PR.plain_path(x) for x in paths]
