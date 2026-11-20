"""Mutation probes of `extended/playbook.py` and `extended/trigger_sides.py` against their tests (the red team's
BUILD_W35 R-8: its 27 mutants, re-expressed on the rebuilt module, and the builder's own). Not collected by pytest; run
by hand when the module or its tests change:

    python tests/playbook_mutants.py            # prints KILLED / SURVIVED per mutant and the count

Each mutant replaces one exact text (found exactly once) in its file, runs `tests/test_playbook.py` and
`tests/test_trigger_sides.py` with `-x`, and restores the file in a `finally` -- the file's sha256 is checked after
every mutant and at the end. A mutant marked `equivalent` is one no test can kill because another guard refuses the
same input first; it is listed so that the equivalence is on record, never counted as killed.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PB = "extended/playbook.py"
TS = "extended/trigger_sides.py"

#: (id, file, old, new, note); note "equivalent: why" marks an expected survivor
MUTANTS = [
    # ---- the red team's 27 (BUILD_W35 R-8, its mutate.py), mapped onto the rebuilt module
    ("C1 void list ignored", PB, 'if any(v["date"] == day for v in decl["void_dates"]):', "if False:", ""),
    ("C2 side not from the declared rule", PB, 'side = TS.trigger_side(trig, c["side_rule"], offer)',
     'side = TS.trigger_side(trig, "with_breakout" if trig.source == "p14" else c["side_rule"], offer)', ""),
    ("C3 the offer's level put in the alert's inputs", PB, 'for f in fields(offer) if f.name != "level"}',
     "for f in fields(offer)}", "equivalent: no piece reads it; C3b, which prints it, is killed"),
    ("C3b the level in the order line", PB, '" at the level itself, read on your chart.")',
     '" at the level itself, read on your chart.", _v("offer", "level"))', ""),
    ("G1 duplicate account ids", PB, "if len(set(ids)) != len(ids):", "if False:", ""),
    ("G2 side rule free words", TS, "if not isinstance(rule, str) or rule not in P14_RULES:",
     "if not isinstance(rule, str):", ""),
    ("G3 bankroll row unchecked", PB, '_cited(rows, decl["bankroll"]["row"], "the bankroll budget\'s row")', "pass", ""),
    ("G4 empty expected list", PB, 'if not list(exp["rows"]):', "if False:", ""),
    ("G5 void-date reason unchecked", PB, 'if d["reason"] not in VOID_WORDS:', "if False:", ""),
    ("G6 blank result value", PB, "if not res.values[k].strip():", "if False:", ""),
    ("G7 declaration pin unchecked", PB, "if pins.get(rel) != sha:", "if False:", ""),
    ("G7b carrying row's design unchecked", PB, '_names(carrying, did, f"the carrying row {decl[\'row\']}")', "pass",
     ""),
    ("G8 no account at all", PB, "if not accounts:", "if False:", ""),
    ("G9 pool component unchecked", PB, "if name not in names or any(a not in ids for a in pool):",
     "if any(a not in ids for a in pool):", ""),
    ("W1 playbook side rule of component 0", PB, '            d.line("    ", SIDE_RULE_WORDS[c["side_rule"]], ".")',
     '            d.line("    ", SIDE_RULE_WORDS[decl["components"][0]["side_rule"]], ".")', ""),
    ("W2 alert side rule of component 0", PB, '"; the rule is ",\n               SIDE_RULE_WORDS[c["side_rule"]], ".")',
     '"; the rule is ",\n               SIDE_RULE_WORDS[decl["components"][0]["side_rule"]], ".")', ""),
    ("W3 playbook stop of component 0", PB, 'd.line("  Stop: ", _v(*P, "stop_ticks")',
     'd.line("  Stop: ", _v(D, "components", 0, "stop_ticks")', ""),
    ("W4 alert role of account 0", PB, 'ROLES[decl["firm"]][decl["accounts"][ai]["role"]][1], ".")',
     'ROLES[decl["firm"]][decl["accounts"][0]["role"]][1], ".")', ""),
    ("W5 alert account id of account 0", PB, 'account ", _v(D, "accounts", ai, "id")',
     'account ", _v(D, "accounts", 0, "id")', ""),
    ("W6 rotation pools not printed", PB, 'for name in sorted(dict(rot.get("pools", {}))):', "for name in []:", ""),
    ("W7 last account not listed", PB, 'for i, a in enumerate(decl["accounts"]):\n        d.line("  - "',
     'for i, a in enumerate(decl["accounts"][:-1]):\n        d.line("  - "', ""),
    ("W8 void dates not listed", PB, 'for i, v in enumerate(decl["void_dates"]):',
     'for i, v in enumerate(decl["void_dates"][:0]):', ""),
    ("W9 limit window printed from the gap", PB, '"- Limit orders work ", _v(*E, "limit_window_min")',
     '"- Limit orders work ", _v(*E, "gap_minutes")', ""),
    ("W10 target by ceil", PB, '"target": lambda stop, rr: str(W.target_ticks(float(rr), int(stop))),',
     '"target": lambda stop, rr: str(math.ceil(float(rr) * int(stop))),', ""),
    ("W11 news before/after swapped", PB, '_v(*P, "before"), " minutes before to ", _v(*P, "after")',
     '_v(*P, "after"), " minutes before to ", _v(*P, "before")', ""),
    ("W12 expected label of row 0", PB, '_v(D, "expected", "rows", i, "label")', '_v(D, "expected", "rows", 0, "label")',
     ""),
    ("W13 closed window end from its start", PB, '_ct(*E, "closed_window", 1), " CT, every day.")',
     '_ct(*E, "closed_window", 0), " CT, every day.")', ""),
    ("W14 alert flatten from the last entry", PB, '"flatten": int(rules.walk_end), "window": flat_window,',
     '"flatten": int(decl["execution"]["last_entry"]), "window": flat_window,', ""),
    ("W15 the calendar's day-wide void dropped", PB, "kept, refused = T.admit([offer], ctx)",
     "kept, refused = T.admit([offer], T.DayContext(ctx.session, ctx.date, ctx.bls, ctx.fomc, False, "
     "ctx.prior_void, ctx.windows))", ""),
    # ---- the builder's own
    ("M1 prior_void ignored", PB, 'trig.kind in ("pd", "pdc") and ctx.prior_void:', 'trig.kind in ("pd", "pdc") and False:',
     ""),
    ("M2 news windows not from the record", PB, "return T.context_for(trig, sources, d, int(session), _day_windows(decl, day),",
     "return T.context_for(trig, sources, d, int(session), (),", ""),
    ("M3 pool unchecked in the alert", PB, 'if account not in _routes(decl, c["name"]):', "if False:", ""),
    ("M4 alert size cap dropped", PB, 'if int(c["contracts"]) > cap:', "if False:",
     "equivalent: check_declaration refuses the same size for every account of the pool first"),
    ("M5 declaration size cap dropped", PB, 'if n > size_cap(firm, roles[acct], decl["instrument"]):', "if False:", ""),
    ("M6 funded cap from the Combine's", PB, '"funded": ("funded_scaling_entry_tier_minis"',
     '"funded": ("combine_position_size_limit"', ""),
    ("M7 micros counted as minis", PB, "return minis * micros_per_mini(firm) if instrument in MICRO else minis",
     "return minis", ""),
    ("M8 live outside the window", PB, 'if not int(c["first"]) <= int(off.live) <= int(c["last"]):', "if False:",
     "equivalent: the trigger's alert bounds (within the window less L) and live = alert + L refuse first"),
    ("M9 live = alert + L unchecked", PB, "int(off.live) == int(off.alert) + lat", "True", ""),
    ("M10 any brk tag", TS, 'if offer.tag not in (stem + "+", stem + "-"):', 'if not offer.tag.startswith("brk"):', ""),
    ("M11 fade and break inverted", TS, 'side = role if how == "break" else -role', 'side = -role if how == "break" else role',
     ""),
    ("M12 trigger side mint unbound", TS, "and self._mint[1] == self._fields()):", "):", ""),
    ("M13 carried bytes unbound", PB, "and hashlib.sha256(self.decl_bytes).hexdigest() == self.decl_sha):", "):", ""),
    ("M14 clean run unchecked", PB,
     'if not (isinstance(prov, Mapping) and isinstance(prov.get("clean_run"), Mapping) and prov["clean_run"].get("name")):',
     "if False:", ""),
    ("M15 dirty flag unchecked", PB, 'or man.get("git_dirty") is not False):', "):", ""),
    ("M16 exploratory unchecked", PB, 'if man.get("exploratory") is not False:', "if False:", ""),
    ("M17 design unchecked", PB, 'if params.get("design_id") != design_id or params.get("convention") != convention:',
     'if params.get("convention") != convention:', ""),
    ("M18 row pin unchecked", PB, "or man.get(HASH) != pinned:", ":", ""),
    ("M19 git-ignored accepted", PB, "if _ignored(rel, (ROOT, root)):", "if False:", ""),
    ("M20 price-level scan dropped", PB, "if _price_findings(p.name, text):", "if False:", ""),
    ("M21 verify_result skipped", PB, "ok, msg = _verify_result(p)", 'ok, msg = True, ""', ""),
    ("M22 failed no-harm accepted", PB, "if v != PASS:", "if v is None:", ""),
    ("M23 no-harm row's design unchecked", PB,
     "_names(nh_row, did, f\"the no-harm row {decl['side']['no_harm_row']}\")", "pass", ""),
    ("M24 result outside results/", PB, 'if p.parent != (root / "results").resolve():', "if False:", ""),
    ("M25 free notice reason", PB, "if reason not in REASON_WORDS:", "if False:", ""),
    ("M26 latency-free L unchecked", PB, "if lat is not None or LS.latency_cells(src) != (None,):", "if False:", ""),
    ("M27 trigger bounds unchecked", PB,
     "if isinstance(obj, T.P14Breakout) and not (first - lat <= int(obj.first) <= int(obj.last) <= last - lat):",
     "if False:", ""),
    ("M28 void rules partial", PB, "if sorted(rules) != sorted(VOID_WORDS) or len(set(rules)) != len(rules):",
     "if any(r not in VOID_WORDS for r in rules):", ""),
    ("M29 firm unchecked", PB, "if firm not in FIRMS:", "if False:",
     "equivalent: plan_name refuses a firm without a verified plan first"),
    ("M30 label digits accepted", PB, '_plain(e["label"], "an expected-journey label")', "pass", ""),
    ("M31 window flatten never named", PB,
     "flat_window = int(rules.walk_end) < int(T.JOURNEY.walk_end) and nxt is not None", "flat_window = False", ""),
    ("M32 the calendar read for no source", PB, "return T.context_for(trig, sources,", "return T.context_for(None, sources,",
     ""),
    ("M33 caller's day accepted", PB, "if not isinstance(sources, DC.Sources):", "if False:", ""),
    ("M34 repeated log row accepted", PB, "if m.group(1) in rows:", "if False:", ""),
    ("M35 CRLF not normalised", PB, 'data = p.read_bytes().replace(b"\\r\\n", b"\\n")', "data = p.read_bytes()", ""),
    ("M36 held-out note dropped", PB, 'if e["block"] == "search" and (e["section"], e["measure"], e["stat"]) not in held:',
     "if False:", ""),
    ("M37 coin reason dropped", TS, "if src in NO_SIDE:", "if False:", ""),
    ("M38 offer type unchecked", PB, "if not isinstance(off, T.Offer):", "if False:", ""),
    ("M39 RL3 expiry unchecked", PB, "and off.expires == int(trig.cutoff) - 1", "", ""),
    ("M40 P-14 entry unchecked", PB, "and off.entry == trig.entry", "", ""),
    ("M41 N-3 block words swapped", PB, '"search": "search years: the years this design was chosen on',
     '"held_out": "search years: the years this design was chosen on', ""),
]


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    env = dict(os.environ, OMP_NUM_THREADS="1", PYTHONDONTWRITEBYTECODE="1")
    cmd = [sys.executable, "-m", "pytest", "-q", "-x", "-o", "addopts=", "-p", "no:cacheprovider",
           "tests/test_playbook.py", "tests/test_trigger_sides.py"]
    files = {f: (ROOT / f) for f in (PB, TS)}
    orig = {f: p.read_bytes() for f, p in files.items()}
    shas = {f: _sha(p) for f, p in files.items()}
    base = subprocess.run(cmd, cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=900)
    if base.returncode != 0:
        print("the unmutated tests fail: no mutant is judged")
        print(base.stdout[-2000:])
        return 2
    killed = survived = equiv = 0
    try:
        for mid, f, old, new, note in MUTANTS:
            text = orig[f].decode()
            if "\r\n" in text:                       # a checkout with CRLF line ends: a mutant spanning lines matches it
                old, new = old.replace("\n", "\r\n"), new.replace("\n", "\r\n")
            n = text.count(old)
            if n != 1:
                print(f"SKIP     {mid}: the text occurs {n} times")
                survived += 1
                continue
            files[f].write_bytes(text.replace(old, new).encode())
            try:
                p = subprocess.run(cmd, cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=900)
            finally:
                files[f].write_bytes(orig[f])
            assert _sha(files[f]) == shas[f], f"{f} not restored"
            last = (p.stdout.strip().splitlines() or [""])[-1][:100]
            if p.returncode != 0:
                killed += 1
                print(f"KILLED   {mid} :: {last}")
            elif note.startswith("equivalent"):
                equiv += 1
                print(f"EQUIV    {mid} :: {note}")
            else:
                survived += 1
                print(f"SURVIVED {mid} :: {last}")
    finally:
        for f, p in files.items():
            p.write_bytes(orig[f])
    assert all(_sha(p) == shas[f] for f, p in files.items())
    print(f"killed {killed} of {len(MUTANTS)}; equivalent (on record) {equiv}; survived {survived}")
    return 0 if survived == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
