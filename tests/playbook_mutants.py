"""Mutation probes of `extended/playbook.py` and `extended/trigger_sides.py` against their tests (the red team's
BUILD_W35 R-8: its 27 mutants, re-expressed on the rebuilt module; BUILD_W35_v2's survivors X4, X35, X36, X37, X65;
and the builder's own for every finding of both notes). Not collected by pytest; run
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
DC_ = "extended/day_calendar.py"
TR = "extended/triggers.py"

#: (id, file, old, new, note); note "equivalent: why" marks an expected survivor
MUTANTS = [
    # ---- the red team's 27 (BUILD_W35 R-8, its mutate.py), mapped onto the module as rebuilt in cycle 2
    ("C1 void list ignored", PB, 'if any(parse_day(v["date"]) == day for v in decl["void_dates"]):', "if False:", ""),
    ("C2 side not from the declared rule", PB, 'side = TS.trigger_side(trig, c["side_rule"], off)',
     'side = TS.trigger_side(trig, "with_breakout" if trig.source == "p14" else c["side_rule"], off)', ""),
    ("C3 the offer's level in the alert's inputs", PB, '"role": int(off.role), "stretches": []}',
     '"role": int(off.role), "stretches": [], "level": float(off.level)}',
     "equivalent: no piece reads it; C3b, which prints it, is killed"),
    ("C3b the level printed in the order line", PB, '" at the level itself, read on your chart.")',
     '" at the level itself, read on your chart.", _v(*T_, "level"))', ""),
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
    ("W2 alert side rule of component 0", PB, '"; the rule is ", SIDE_RULE_WORDS[c["side_rule"]], ".")',
     '"; the rule is ", SIDE_RULE_WORDS[decl["components"][0]["side_rule"]], ".")', ""),
    ("W3 playbook stop of component 0", PB, 'd.line("  Stop: ", _v(*P, "stop_ticks")',
     'd.line("  Stop: ", _v(D, "components", 0, "stop_ticks")', ""),
    ("W4 alert role of account 0", PB, 'ROLES[decl["firm"]][decl["accounts"][ai]["role"]][1], " -- the rotation',
     'ROLES[decl["firm"]][decl["accounts"][0]["role"]][1], " -- the rotation', ""),
    ("W5 alert account from the first account", PB, '"live": live, "account": account,',
     '"live": live, "account": accounts[0],', ""),
    ("W6 rotation pools not printed", PB, 'for name in sorted(dict(rot.get("pools", {}))):', "for name in []:", ""),
    ("W7 last account not listed", PB, 'for i, a in enumerate(decl["accounts"]):\n        d.line("  - "',
     'for i, a in enumerate(decl["accounts"][:-1]):\n        d.line("  - "', ""),
    ("W8 void dates not listed", PB, 'for i, v in enumerate(decl["void_dates"]):',
     'for i, v in enumerate(decl["void_dates"][:0]):', ""),
    ("W9 limit window printed from the gap", PB, '"- Limit orders work ", _v(*E, "limit_window_min")',
     '"- Limit orders work ", _v(*E, "gap_minutes")', ""),
    ("W10 target by ceil", PB, '"target": lambda stop, rr: str(W.target_ticks(float(rr), int(stop))),',
     '"target": lambda stop, rr: str(math.ceil(float(rr) * int(stop))),', ""),
    ("W11 news before/after swapped", PB, '_v(*P, "before"), " minutes before the release to ", _v(*P, "after")',
     '_v(*P, "after"), " minutes before the release to ", _v(*P, "before")', ""),
    ("W12 expected label of row 0", PB, '_v(D, "expected", "rows", i, "label")', '_v(D, "expected", "rows", 0, "label")',
     ""),
    ("W13 closed window end from its start", PB, '_ct(*E, "closed_window", 1), " CT, every day.")',
     '_ct(*E, "closed_window", 0), " CT, every day.")', ""),
    ("W14 alert flatten from the last entry", PB, '"flatten": int(rules.walk_end), "window": flat_window,',
     '"flatten": int(decl["execution"]["last_entry"]), "window": flat_window,', ""),
    ("W15 the scheduled close dropped", PB, "kept, refused = T.admit(group, ctx)",
     "kept, refused = T.admit(group, T.DayContext(ctx.session, ctx.date, ctx.bls, ctx.fomc, False, ctx.prior_void, "
     "ctx.windows))", ""),
    # ---- cycle 1's own, where the code they probe still stands
    ("M2 news windows not from the record", PB, "windows=_day_windows(decl, day))\n    except", "windows=())\n    except",
     ""),
    ("M3 router's rotation unchecked", PB, "if (router.routing.rotation, dict(router.routing.pools)) != (want.rotation, "
     "dict(want.pools)):", "if False:", ""),
    ("M4 alert size cap dropped", PB, 'if int(c["contracts"]) * len(kept) > cap:', "if False:",
     "equivalent: check_declaration refuses the same size, every ticket together, for every account of the pool"),
    ("M5 declaration size cap dropped", PB, 'if n * _legs(trig) > size_cap(firm, roles[acct], decl["instrument"]):',
     "if False:", ""),
    ("M6 funded cap from the Combine's", PB, '"funded": ("funded_scaling_entry_tier_minis"',
     '"funded": ("combine_position_size_limit"', ""),
    ("M7 micros counted as minis", PB, "return minis * micros_per_mini(firm) if instrument in MICRO else minis",
     "return minis", ""),
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
    ("M18 CSV pin unchecked", PB, "or man.get(HASH) != carried_pins.get(rel):", ":", ""),
    ("M19 git-ignored accepted", PB, "if _ignored(rel, (ROOT, root)):", "if False:", ""),
    ("M20 price scan dropped", PB, "if _price_cells(p.name, text, rows):", "if False:", ""),
    ("M21 verify_result skipped", PB, "ok, msg = _verify_result(p)", 'ok, msg = True, ""', ""),
    ("M23 no-harm row's design unchecked", PB, '_names(nh_row, did, f"the no-harm row {nh_id}")', "pass", ""),
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
    ("M33 caller's day accepted", PB, "if not isinstance(sources, DC.Sources):", "if False:", ""),
    ("M34 repeated log row accepted", PB, "if m.group(1) in rows:", "if False:", ""),
    ("M35 CRLF not normalised", PB, 'return data.replace(b"\\r\\n", b"\\n")', "return data", ""),
    ("M36 held-out note dropped", PB, 'if e["block"] == "search" and (e["section"], e["measure"], e["stat"]) not in held:',
     "if False:", ""),
    ("M37 coin reason dropped", TS, "if src in NO_SIDE:", "if False:", ""),
    ("M41 N-3 block words swapped", PB, '"search": "search years: the years this design was chosen on',
     '"held_out": "search years: the years this design was chosen on', ""),
    # ---- cycle 2: B-1, B-3 (the bindings and the floor)
    ("B1a declaration sha unbound", PB, '"declaration_" + HASH: decl_sha, **dict(extra or {})}',
     '**dict(extra or {})}', ""),
    ("B1b declaration path unbound", PB, '"declaration_file": decl_file,\n            ', "", ""),
    ("B1c margin unbound", PB, 'extra={"margin": decl["side"]["margin"]}, **bind)', "**bind)", ""),
    ("B1d script unchecked", PB, 'if man.get("script") != script or man.get("prereg_id") != family:',
     'if man.get("prereg_id") != family:', ""),
    ("B1e family unchecked", PB, 'if man.get("script") != script or man.get("prereg_id") != family:',
     'if man.get("script") != script:', ""),
    ("B1f recorded side rule unchecked", PB, 'if res.values[k["side_rule"]] != canonical_rule(c["side_rule"]):',
     "if False:", ""),
    ("B1g recorded margin unchecked", PB, 'if _finite(res.values[k["margin"]], "the recorded margin") != margin:',
     "if False:", ""),
    ("B1h floor read as a word", PB, "if tc < cc - margin:", "if False:", ""),
    ("B1i margin ignored in the floor", PB, "if tc < cc - margin:", "if tc < cc:", ""),
    ("B1j absent floor accepted", PB, "if any(k[s] not in res.values for s in NO_HARM_STATS):", "if False:", ""),
    ("B1k declared after the floor accepted", PB,
     'if first is None or not order.index(first) < order.index(nh_id) < order.index(decl["row"]):',
     "if first is None:", ""),
    ("B1l P-14's k unchecked", PB, "if isinstance(obj, T.P14Breakout) and int(obj.k) != T.P14_K:", "if False:", ""),
    ("B1m RL3 canonical rule unsorted", PB, 'return ";".join(f"{k}={rule[k]}" for k in sorted(rule))',
     'return ";".join(f"{k}={rule[k]}" for k in sorted(rule, reverse=True))', ""),
    # ---- B-2 (offers recomputed from the bars closed at the alert)
    ("B2a bars after the alert kept", PB, "y[i, int(at) + 1:] = np.nan", "pass", ""),
    ("B2b one bar too many kept", PB, "y[i, int(at) + 1:] = np.nan", "y[i, int(at) + 2:] = np.nan", ""),
    ("B2c offers outside the window kept", PB,
     'group = [o for o in offers if int(o.alert) == int(at) and int(c["first"]) <= int(o.live) <= int(c["last"])]',
     "group = [o for o in offers if int(o.alert) == int(at)]",
     "equivalent: the trigger's alert bounds, inside the window less L, never make an offer outside it"),
    ("B2d any alert slot", PB,
     'group = [o for o in offers if int(o.alert) == int(at) and int(c["first"]) <= int(o.live) <= int(c["last"])]',
     'group = [o for o in offers if int(c["first"]) <= int(o.live) <= int(c["last"])]', ""),
    ("B2e history type unchecked", PB, "if not isinstance(hist, T.History) or isinstance(i, bool)",
     "if False and isinstance(i, bool)", ""),
    # ---- B-4 (the RL3 pair)
    ("B4a pair as single tickets", PB, "    pair = len(tickets) > 1\n", "    pair = False\n", ""),
    ("B4b OCO words dropped", PB, "        d.line(OCO_WORDS)\n", "", ""),
    ("B4c pair total from one ticket", PB, '"total": int(c["contracts"]) * len(tickets),', '"total": int(c["contracts"]),',
     ""),
    ("B4d declaration legs counted once", PB, 'return len(TS.rl3_names(trig)) if isinstance(trig, T.RL3Tickets) else 1',
     "return 1", ""),
    ("B4e the pair counted as two orders", PB, '(" (this pair counts as one order)" if pair else "")', '""', ""),
    # ---- B-5 (the day known at the alert): day_calendar.alert_context and the playbook's use of it
    ("B5a research voids read", DC_, "void = close is not None and close - 1 < _walk_last_stamp(rules)",
     "void = (close is not None and close - 1 < _walk_last_stamp(rules)) or d in src.early_end", ""),
    ("B5b scheduled close ignored", DC_, "void = close is not None and close - 1 < _walk_last_stamp(rules)",
     "void = False", ""),
    ("B5c prior state ignored", DC_, "prior_void=bool(_prior_scheduled(src, d)), windows=tuple(windows))",
     "prior_void=False, windows=tuple(windows))", ""),
    ("B5d prior data voids read", DC_, "prior_void=bool(_prior_scheduled(src, d)), windows=tuple(windows))",
     "prior_void=bool(_prior_scheduled(src, d)) or (src.previous(d) is not None and bool(_day_void(src, "
     "src.previous(d), _walk_last_stamp(rules)))), windows=tuple(windows))", ""),
    ("B5e the full day_flags context", PB,
     "ctx = DC.alert_context(sources, UNDERLYING_OF[decl[\"instrument\"]], day, i, windows=_day_windows(decl, day))\n"
     "    except",
     "ctx = T.context_for(trig, sources, day, i, _day_windows(decl, day))\n    except", ""),
    ("B5f FOMC not read", DC_, "bls=d in src.bls, fomc=d in src.fomc, void=bool(void),",
     "bls=d in src.bls, fomc=False, void=bool(void),", ""),
    # ---- B-6 (strict dates, compared as dates)
    ("B6a basic form accepted", PB, "if not isinstance(v, str) or not ISO.match(v):", "if not isinstance(v, str):",
     "equivalent: the ISO round trip (`d.isoformat() != v`) refuses the basic and short forms too; B6b-d are killed"),
    ("B6b release dates unchecked (X37)", PB, '            parse_day(d, "a release date")', "            pass", ""),
    ("B6c anchor dates unchecked (X36)", PB, '        parse_day(d, "a session-anchor date")', "        pass", ""),
    ("B6d void dates unchecked", PB, '        parse_day(d["date"], "a void date")', "        pass", ""),
    ("B6e release dates as strings", PB, 'if day in {parse_day(x) for x in w["dates"]})', 'if str(day) in w["dates"])',
     "equivalent: with every date strict ISO a date and its text compare alike; B6a and B6b, which let another form "
     "in, are killed"),
    # ---- the minors
    ("m1 manifest pin unchecked", PB,
     "if hashlib.sha256(_lf(mraw)).hexdigest() != carried_pins.get(rel + MANIFEST_SUFFIX):", "if False:", ""),
    ("m2 'carried' unchecked", PB, 'if not re.search(r"\\bcarried\\b", carrying) or NOT_CARRIED.search(carrying):',
     "if False:", ""),
    ("m2b 'not carried' accepted", PB, 'if not re.search(r"\\bcarried\\b", carrying) or NOT_CARRIED.search(carrying):',
     'if not re.search(r"\\bcarried\\b", carrying):', ""),
    ("m2c registration unchecked", PB, '_names(carrying, decl["registration"], f"the carrying row {decl[\'row\']}")',
     "pass", ""),
    ("m3 single price cell accepted", PB, "return bool(cells) and bool(PL.on_level(np.asarray(cells, dtype=float)).any())",
     "return False", ""),
    ("m4a duplicate keys accepted", PB, "        if k in out:\n            raise PlaybookRefused(f\"a key {k!r} appears twice",
     "        if False:\n            raise PlaybookRefused(f\"a key {k!r} appears twice", ""),
    ("m4b NaN accepted", PB, "return json.loads(data, object_pairs_hook=_no_dupes, parse_constant=_no_constant)",
     "return json.loads(data, object_pairs_hook=_no_dupes)", ""),
    ("m5 router bypassed", PB, 'account = router.peek(decl["firm"], c["name"], accounts)', "account = accounts[0]", ""),
    ("m6 bar end for its stamp", PB, '"stamp": lambda s: DC.label(int(s) - 1),', '"stamp": lambda s: DC.label(int(s)),',
     ""),
    ("m7 dotted identifiers", PB, 'IDENT = re.compile(r"[A-Za-z][A-Za-z_-]*\\d?\\d?$")',
     'IDENT = re.compile(r"[A-Za-z][A-Za-z\\d_.-]*$")', ""),
    ("m8 empty news list accepted", PB, '        if "news_none" not in decl:\n', '        if False:\n', ""),
    ("N3 a path pinned twice accepted", PB, "            if strict:\n                raise",
     "            if False:\n                raise", ""),
    ("X35 missing anchor unchecked", PB, "if not isinstance(anchors, Mapping) or sess not in anchors:", "if False:",
     ""),
    ("X65 every window flatten named news", PB, 'WINDOW_WORDS[s["window_kind"]],', 'WINDOW_WORDS["news"],', ""),
    ("R1 coin trade alerted", PB, '    return _notice(carried, tr.component, int(tr.live), "coin_side")',
     '    return _notice(carried, tr.component, int(tr.live), "position")', ""),
    ("X4 prior_void for pd only", TR, 'if kind in ("pd", "pdc"):\n        why = ""', 'if kind == "pd":\n        why = ""',
     ""),
]


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    if sys.argv[1:] == ["--check"]:                  # every mutant's text found exactly once, nothing run
        bad = 0
        for mid, f, old, new, note in MUTANTS:
            text = (ROOT / f).read_bytes().decode()
            if "\r\n" in text:
                old = old.replace("\n", "\r\n")
            if text.count(old) != 1:
                bad += 1
                print(f"{mid}: found {text.count(old)} times")
        print(f"{len(MUTANTS)} mutants, {bad} not found exactly once")
        return 1 if bad else 0
    env = dict(os.environ, OMP_NUM_THREADS="1", PYTHONDONTWRITEBYTECODE="1")
    cmd = [sys.executable, "-m", "pytest", "-q", "-x", "-o", "addopts=", "-p", "no:cacheprovider",
           "tests/test_playbook.py", "tests/test_trigger_sides.py"]
    files = {f: (ROOT / f) for f in sorted({m[1] for m in MUTANTS})}
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
