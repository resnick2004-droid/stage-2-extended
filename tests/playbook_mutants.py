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
RT = "extended/router.py"
PO_ = "extended/pin_order.py"

#: (id, file, old, new, note); note "equivalent: why" marks an expected survivor
MUTANTS = [
    ('C1 void list ignored', PB, 'if any(parse_day(v["date"]) == day for v in decl["void_dates"]):', 'if False:', ''),
    ('C2 side not from the declared rule', PB, 'side = TS.trigger_side(trig, c["side_rule"], off)', 'side = TS.trigger_side(trig, "with_breakout" if trig.source == "p14" else c["side_rule"], off)', ''),
    ("C3 the offer's level in the alert's inputs", PB, '"role": int(off.role), "stretches": []}', '"role": int(off.role), "stretches": [], "level": float(off.level)}', 'equivalent: no piece reads it; C3b, which prints it, is killed'),
    ('C3b the level printed in the order line', PB, '" at the level itself, read on your chart.")', '" at the level itself, read on your chart.", _v(*T_, "level"))', ''),
    ('G1 duplicate account ids', PB, 'if len(set(ids)) != len(ids):', 'if False:', ''),
    ('G2 side rule free words', TS, 'if not isinstance(rule, str) or rule not in P14_RULES:', 'if not isinstance(rule, str):', ''),
    ('G3 bankroll row unchecked', PB, '_cited(rows, decl["bankroll"]["row"], "the bankroll budget\'s row")', 'pass', ''),
    ('G4 empty expected list', PB, 'if not list(exp["rows"]):', 'if False:', ''),
    ('G5 void-date reason unchecked', PB, 'if d["reason"] not in VOID_WORDS:', 'if False:', ''),
    ('G6 blank result value', PB, 'if not res.values[k].strip():', 'if False:', ''),
    ('G8 no account at all', PB, 'if not accounts:', 'if False:', ''),
    ('G9 pool component unchecked', PB, 'if name not in names or any(a not in ids for a in pool):', 'if any(a not in ids for a in pool):', ''),
    ('W1 playbook side rule of component 0', PB, '            d.line("    ", SIDE_RULE_WORDS[c["side_rule"]], ".")', '            d.line("    ", SIDE_RULE_WORDS[decl["components"][0]["side_rule"]], ".")', ''),
    ('W2 alert side rule of component 0', PB, '"; the rule is ", SIDE_RULE_WORDS[c["side_rule"]], ".")', '"; the rule is ", SIDE_RULE_WORDS[decl["components"][0]["side_rule"]], ".")', ''),
    ('W3 playbook stop of component 0', PB, 'd.line("  Stop: ", _v(*P, "stop_ticks")', 'd.line("  Stop: ", _v(D, "components", 0, "stop_ticks")', ''),
    ('W4 alert role of account 0', PB, 'ROLES[decl["firm"]][decl["accounts"][ai]["role"]][1], " -- the rotation', 'ROLES[decl["firm"]][decl["accounts"][0]["role"]][1], " -- the rotation', ''),
    ('W5 alert account from the first account', PB, '"live": live, "account": account,', '"live": live, "account": accounts[0],', ''),
    ('W6 rotation pools not printed', PB, 'for name in sorted(dict(rot.get("pools", {}))):', 'for name in []:', ''),
    ('W7 last account not listed', PB, 'for i, a in enumerate(decl["accounts"]):\n        d.line("  - "', 'for i, a in enumerate(decl["accounts"][:-1]):\n        d.line("  - "', ''),
    ('W8 void dates not listed', PB, 'for i, v in enumerate(decl["void_dates"]):', 'for i, v in enumerate(decl["void_dates"][:0]):', ''),
    ('W9 limit window printed from the gap', PB, '"- Limit orders work ", _v(*E, "limit_window_min")', '"- Limit orders work ", _v(*E, "gap_minutes")', ''),
    ('W10 target by ceil', PB, '"target": lambda stop, rr: str(W.target_ticks(float(rr), int(stop))),', '"target": lambda stop, rr: str(math.ceil(float(rr) * int(stop))),', ''),
    ('W11 news before/after swapped', PB, '_v(*P, "before"), " minutes before the release to ", _v(*P, "after")', '_v(*P, "after"), " minutes before the release to ", _v(*P, "before")', ''),
    ('W12 expected label of row 0', PB, '_v(D, "expected", "rows", i, "label")', '_v(D, "expected", "rows", 0, "label")', ''),
    ('W13 closed window end from its start', PB, '_ct(*E, "closed_window", 1), " CT, every day.")', '_ct(*E, "closed_window", 0), " CT, every day.")', ''),
    ('W14 alert flatten from the last entry', PB, '"flatten": int(rules.walk_end), "window": flat_window,', '"flatten": int(decl["execution"]["last_entry"]), "window": flat_window,', ''),
    ('W15 the scheduled close dropped', PB, 'kept, refused = T.admit(group, ctx)', 'kept, refused = T.admit(group, T.DayContext(ctx.session, ctx.date, ctx.bls, ctx.fomc, False, ctx.prior_void, ctx.windows))', ''),
    ('M2 news windows not from the record', PB, 'windows=_day_windows(decl, day))\n    except', 'windows=())\n    except', ''),
    ("M3 router's rotation unchecked", PB, 'if (router.routing.rotation, dict(router.routing.pools)) != (want.rotation, dict(want.pools)):', 'if False:', ''),
    ('M4 alert size cap dropped', PB, 'if int(c["contracts"]) * len(kept) > cap:', 'if False:', 'equivalent: check_declaration refuses the same size, every ticket together, for every account of the pool'),
    ('M5 declaration size cap dropped', PB, 'if n * _legs(trig) > size_cap(firm, roles[acct], decl["instrument"]):', 'if False:', ''),
    ("M6 funded cap from the Combine's", PB, '"funded": ("funded_scaling_entry_tier_minis"', '"funded": ("combine_position_size_limit"', ''),
    ('M7 micros counted as minis', PB, 'return minis * micros_per_mini(firm) if instrument in MICRO else minis', 'return minis', ''),
    ('M10 any brk tag', TS, 'if offer.tag not in (stem + "+", stem + "-"):', 'if not offer.tag.startswith("brk"):', ''),
    ('M11 fade and break inverted', TS, 'side = role if how == "break" else -role', 'side = -role if how == "break" else role', ''),
    ('M12 trigger side mint unbound', TS, 'and self._mint[1] == self._fields()):', '):', ''),
    ('M13 carried bytes unbound', PB, 'and hashlib.sha256(self.decl_bytes).hexdigest() == self.decl_sha):', '):', ''),
    ('M14 clean run unchecked', PB, 'if not (isinstance(prov, Mapping) and isinstance(prov.get("clean_run"), Mapping) and prov["clean_run"].get("name")):', 'if False:', ''),
    ('M15 dirty flag unchecked', PB, 'or man.get("git_dirty") is not False):', '):', ''),
    ('M16 exploratory unchecked', PB, 'if man.get("exploratory") is not False:', 'if False:', ''),
    ('M18 CSV pin unchecked', PB, 'or man.get(HASH) != carried_pins.get(rel):', ':', ''),
    ('M19 git-ignored accepted', PB, 'if _ignored(rel, (ROOT, root)):', 'if False:', ''),
    ('M21 verify_result skipped', PB, 'ok, msg = _verify_result(p)', 'ok, msg = True, ""', ''),
    ("M23 no-harm row's design unchecked", PB, '_names(nh_row, did, f"the no-harm row {nh_id}")', 'pass', ''),
    ('M24 result outside results/', PB, 'if p.parent != (root / "results").resolve():', 'if False:', ''),
    ('M25 free notice reason', PB, 'if reason not in REASON_WORDS:', 'if False:', ''),
    ('M26 latency-free L unchecked', PB, 'if lat is not None or LS.latency_cells(src) != (None,):', 'if False:', ''),
    ('M28 void rules partial', PB, 'if sorted(rules) != sorted(VOID_WORDS) or len(set(rules)) != len(rules):', 'if any(r not in VOID_WORDS for r in rules):', ''),
    ('M29 firm unchecked', PB, 'if firm not in FIRMS:', 'if False:', 'equivalent: plan_name refuses a firm without a verified plan first'),
    ('M30 label digits accepted', PB, '_plain(e["label"], "an expected-journey label")', 'pass', ''),
    ('M31 window flatten never named', PB, 'flat_window = int(rules.walk_end) < int(T.JOURNEY.walk_end) and nxt is not None', 'flat_window = False', ''),
    ("M33 caller's day accepted", PB, 'if not isinstance(sources, DC.Sources):', 'if False:', ''),
    ('M34 repeated log row accepted', PB, 'if m.group(1) in rows:', 'if False:', ''),
    ('M35 CRLF not normalised', PB, 'return data.replace(b"\\r\\n", b"\\n")', 'return data', ''),
    ('M36 held-out note dropped', PB, 'if e["block"] == "search" and (e["section"], e["measure"], e["stat"]) not in held:', 'if False:', ''),
    ('M37 coin reason dropped', TS, 'if src in NO_SIDE:', 'if False:', ''),
    ('M41 N-3 block words swapped', PB, '"search": "search years: the years this design was chosen on', '"held_out": "search years: the years this design was chosen on', ''),
    ('B1b declaration path unbound', PB, '"declaration_file": decl_file,\n            ', '', ''),
    ('B1c margin unbound', PB, 'extra={"margin": decl["side"]["margin"]}, **bind)', '**bind)', ''),
    ('B1d script unchecked', PB, 'if man.get("script") != script or man.get("prereg_id") != family:', 'if man.get("prereg_id") != family:', ''),
    ('B1e family unchecked', PB, 'if man.get("script") != script or man.get("prereg_id") != family:', 'if man.get("script") != script:', ''),
    ('B1f recorded side rule unchecked', PB, 'if res.values[k["side_rule"]] != canonical_rule(c["side_rule"]):', 'if False:', ''),
    ('B1h floor read as a word', PB, 'if tc < cc - margin:', 'if False:', ''),
    ('B1i margin ignored in the floor', PB, 'if tc < cc - margin:', 'if tc < cc:', ''),
    ('B1j absent floor accepted', PB, 'if any(k[s] not in res.values for s in NO_HARM_STATS):', 'if False:', ''),
    ("B1l P-14's k unchecked", PB, 'if isinstance(obj, T.P14Breakout) and int(obj.k) != T.P14_K:', 'if False:', ''),
    ('B1m RL3 canonical rule unsorted', PB, 'return ";".join(f"{k}={rule[k]}" for k in sorted(rule))', 'return ";".join(f"{k}={rule[k]}" for k in sorted(rule, reverse=True))', ''),
    ('B2a bars after the alert kept', PB, 'y[i, int(at) + 1:] = np.nan', 'pass', ''),
    ('B2b one bar too many kept', PB, 'y[i, int(at) + 1:] = np.nan', 'y[i, int(at) + 2:] = np.nan', ''),
    ('B2e history type unchecked', PB, 'if not isinstance(hist, T.History) or isinstance(i, bool)', 'if False and isinstance(i, bool)', ''),
    ('B4a pair as single tickets', PB, '    pair = len(tickets) > 1\n', '    pair = False\n', ''),
    ('B4c pair total from one ticket', PB, '"total": int(c["contracts"]) * len(tickets),', '"total": int(c["contracts"]),', ''),
    ('B4d declaration legs counted once', PB, 'return len(TS.rl3_names(trig)) if isinstance(trig, T.RL3Tickets) else 1', 'return 1', ''),
    ('B5a research voids read', DC_, 'void = close is not None and close - 1 < _walk_last_stamp(rules)', 'void = (close is not None and close - 1 < _walk_last_stamp(rules)) or d in src.early_end', ''),
    ('B5b scheduled close ignored', DC_, 'void = close is not None and close - 1 < _walk_last_stamp(rules)', 'void = False', ''),
    ('B5e the full day_flags context', PB, 'ctx = DC.alert_context(sources, UNDERLYING_OF[decl["instrument"]], day, i, windows=_day_windows(decl, day))\n    except', 'ctx = T.context_for(trig, sources, day, i, _day_windows(decl, day))\n    except', ''),
    ('B5f FOMC not read', DC_, 'bls=d in src.bls, fomc=d in src.fomc, void=bool(void),', 'bls=d in src.bls, fomc=False, void=bool(void),', ''),
    ('B6b release dates unchecked (X37)', PB, '            parse_day(d, "a release date")', '            pass', ''),
    ('B6c anchor dates unchecked (X36)', PB, '        parse_day(d, "a session-anchor date")', '        pass', ''),
    ('B6d void dates unchecked', PB, '        parse_day(d["date"], "a void date")', '        pass', ''),
    ('B6e release dates as strings', PB, 'if day in {parse_day(x) for x in w["dates"]})', 'if str(day) in w["dates"])', 'equivalent: with every date strict ISO a date and its text compare alike; B6a and B6b, which let another form in, are killed'),
    ('m1 manifest pin unchecked', PB, 'if hashlib.sha256(_lf(mraw)).hexdigest() != carried_pins.get(rel + MANIFEST_SUFFIX):', 'if False:', ''),
    ('m4a duplicate keys accepted', PB, '        if k in out:\n            raise PlaybookRefused(f"a key {k!r} appears twice', '        if False:\n            raise PlaybookRefused(f"a key {k!r} appears twice', ''),
    ('m4b NaN accepted', PB, 'return json.loads(data, object_pairs_hook=_no_dupes, parse_constant=_no_constant)', 'return json.loads(data, object_pairs_hook=_no_dupes)', ''),
    ('m6 bar end for its stamp', PB, '"stamp": lambda s: DC.label(int(s) - 1),', '"stamp": lambda s: DC.label(int(s)),', ''),
    ('m8 empty news list accepted', PB, '        if "news_none" not in decl:\n', '        if False:\n', ''),
    ('N3 a path pinned twice accepted', PB, '            if strict:\n                raise', '            if False:\n                raise', ''),
    ('X35 missing anchor unchecked', PB, 'if not isinstance(anchors, Mapping) or sess not in anchors:', 'if False:', ''),
    ('X65 every window flatten named news', PB, 'WINDOW_WORDS[s["window_kind"]],', 'WINDOW_WORDS["news"],', ''),
    ('R1 coin trade alerted', PB, '    return _notice(carried, tr.component, int(tr.live), "coin_side")', '    return _notice(carried, tr.component, int(tr.live), "position")', ''),
    ('X4 prior_void for pd only', TR, 'if kind in ("pd", "pdc"):\n        why = ""', 'if kind == "pd":\n        why = ""', ''),
    ('G7 carrying record pin unchecked', PB, 'if pins.get(rrel) != rsha:', 'if False:', ''),
    ('M20 label-column band dropped', PB, '                if lo <= x <= hi:', '                if False:', ''),
    ('M27 fixed-CT breakout bounds accepted', PB, 'if src == P14 and any(k not in P14_PARAMS for k in params):', 'if False:', ''),
    ('B1a declaration sha unbound', PB, 'DECL_SHA_KEY: decl_sha, **dict(extra or {})}', '**dict(extra or {})}', ''),
    ('B1g recorded margin unchecked', PB, 'if _bare(res.values[k["margin"]], "the recorded margin") != margin:', 'if False:', ''),
    ('B1k declared after the floor accepted', PB, 'if first is None or not order.index(first) < order.index(nh_id) < order.index(crow):', 'if first is None:', ''),
    ('B2c offers outside the window kept', PB, 'group = [o for o in offers if int(o.alert) == int(at) and int(comp.first) <= int(o.live) <= int(comp.last)]', 'group = [o for o in offers if int(o.alert) == int(at)]', "equivalent: the breakout's alerts are its window less L on each date, and RL3's live slot is checked inside its window, so no offer lies outside it"),
    ('B2d any alert slot', PB, 'group = [o for o in offers if int(o.alert) == int(at) and int(comp.first) <= int(o.live) <= int(comp.last)]', 'group = [o for o in offers if int(comp.first) <= int(o.live) <= int(comp.last)]', ''),
    ('B4b pair words dropped', PB, '        d.line(PAIR_WORDS)\n', '', ''),
    ('B4e the pair counted as two orders', PB, '(" (these tickets count as one order)" if pair else "")', '""', ''),
    ('B5c prior state ignored', DC_, 'prior_void=bool(_prior_known(src, d)), windows=tuple(windows))', 'prior_void=False, windows=tuple(windows))', ''),
    ('B5d prior data voids read', DC_, 'prior_void=bool(_prior_known(src, d)), windows=tuple(windows))', 'prior_void=bool(_prior_known(src, d)) or (src.previous(d) is not None and bool(_day_void(src, src.previous(d), _walk_last_stamp(rules)))), windows=tuple(windows))', ''),
    ('B6a basic form accepted', PB, 'if not isinstance(v, str) or not ISO.fullmatch(v):', 'if not isinstance(v, str):', 'equivalent: the ISO round trip (`d.isoformat() != v`) refuses the basic and short forms too; B6b-d are killed'),
    ('m2 negated or conditional carrying accepted (C2-7)', PB, 'if NOT_CARRIED.search(carrying):', 'if False:', ''),
    ("m2b 'not yet carried' accepted", PB, 'NOT_CARRIED = re.compile(r"\\bnot\\s+(?:yet\\s+)?carried\\b|', 'NOT_CARRIED = re.compile(r"\\bnot carried\\b|', ''),
    ('m3 label numbers only bare', PB, 'NUMBER_IN = re.compile(r"\\d[\\d,]*(?:\\.\\d+)?")', 'NUMBER_IN = re.compile(r"^\\d+(?:\\.\\d+)?$")', ''),
    ('m5 router bypassed', PB, 'account = router.peek(decl["firm"], c["name"], today)', 'account = today[0]', ''),
    ('m7 dotted identifiers', PB, 'IDENT = re.compile(r"[A-Za-z][A-Za-z_-]*(?:_v\\d)?")', 'IDENT = re.compile(r"[A-Za-z][A-Za-z\\d_.-]*")', ''),
    ('C2-1 margin row unchecked', PB, 'if _margin_of(m_row, f"the margin row {decl[\'side\'][\'margin_row\']}") != float(decl["side"]["margin"]):', 'if False:', ''),
    ('C2-1b margin stated twice accepted', PB, '    if len(found) != 1:', '    if not found:', ''),
    ('C2-2c the last pin, not the first', PO_, 'p = _git(repo, "log", "--reverse", "--format=%H", "-S", text, "--", log)', 'p = _git(repo, "log", "--format=%H", "-S", text, "--", log)', ''),
    ('C2-2d a missing commit accepted', PO_, '        if _git(repo, "cat-file", "-e", f"{c}^{{commit}}").returncode:\n            return False', '        if False:\n            return False', 'equivalent: `merge-base --is-ancestor` fails on a commit the repository does not hold'),
    ("C2-3a one date's windows for all", PB, 'for name, _, a, b in space.windows_on(_space_design(decl), day):', 'for name, _, a, b in space.windows_on(_space_design(decl), SS.search_days()[0]):', ''),
    ('C2-3b offsets as absolute slots', PB, 'return SS.Space(tuple(dims), slots=tuple(slots), constraints=tuple(cons), starts=_starts, days=SS.search_days())', 'return SS.Space(tuple(dims), slots=tuple(slots), constraints=tuple(cons), starts=None, days=SS.search_days())', ''),
    ("C2-3c the space's check skipped", PB, '    if why is not None:\n        raise PlaybookRefused(f"the windows', '    if False:\n        raise PlaybookRefused(f"the windows', ''),
    ('C2-5 registration allowed in the declaration', PB, '    for k in ("row", "registration"):\n        if k in decl:', '    for k in ():\n        if k in decl:', ''),
    ('C2-5b record keys unchecked', PB, 'if not isinstance(record, Mapping) or sorted(record) != sorted(RECORD_KEYS):', 'if not isinstance(record, Mapping):', ''),
    ("C2-5c record's declaration hash unchecked", PB, '    if record[DECL_SHA_KEY] != sha:', '    if False:', ''),
    ('C2-8a off-list columns accepted', PB, '    if off:\n', '    if False:\n', ''),
    ('C2-8b printed figures not bare', PB, '        _bare(res.values[k], f"{res.file}\'s value for {k}")\n', '', ''),
    ("C2-9a the prior session's bars misnamed", PB, '"prior_last": T.PRIOR_RTH[1]', '"prior_last": T.PRIOR_RTH[1] + 1', ''),
    ('C2-9b the platform-level line dropped', PB, '    if isinstance(trig, T.RL3Tickets):\n        d.line(PLATFORM_LEVEL)\n', '', ''),
    ('C2-10 identifiers matched by prefix', PB, 'if not isinstance(v, str) or not IDENT.fullmatch(v):', 'if not isinstance(v, str) or not IDENT.match(v):', ''),
    ('C2-11a floor after the carrying row accepted (Y1)', PB, 'if first is None or not order.index(first) < order.index(nh_id) < order.index(crow):', 'if first is None or not order.index(first) < order.index(nh_id):', ''),
    ("C2-11b the cut keeps later days' rows (Y3)", PB, '        y = np.array(x[: i + 1], dtype=float, copy=True)', '        y = np.array(x, dtype=float, copy=True)', ''),
    ("C2-11c peek writes the router's state (Y6)", RT, '        return self._pick(SimpleNamespace(firm=firm, component=component), accs)', '        pick = self._pick(SimpleNamespace(firm=firm, component=component), accs); self.last_account[firm] = pick; return pick', ''),
    ('N-c2-1 every declared account alive', PB, '    today = _today(decl, accounts)', '    today = tuple(a["id"] for a in decl["accounts"])', ''),
    ('G7b any carried token accepted', PB, 'if not isinstance(ho_rel, str) or tokens != [(did, sha, reg, pins.get(ho_rel, ""))]:', 'if not tokens:', ''),
    ('m2c registration ignored in the token', PB, 'if not isinstance(ho_rel, str) or tokens != [(did, sha, reg, pins.get(ho_rel, ""))]:', 'if [t[:2] + t[3:] for t in tokens] != [(did, sha, pins.get(ho_rel, ""))]:', ''),
    ("C2-2 the floor's run order unchecked", PB, '    if not _run_after_pin(root, pin_text, no_harm.commit):', '    if False:', ''),
    ('C2-2b any commit descends from the pin', PO_, '    if _git(repo, "merge-base", "--is-ancestor", ancestor, commit).returncode != 0:\n        return False', '    if False:\n        return False', ''),
    ('C2-4 void-at-live line dropped', PB, '                d.line("  Each time you place it (", ("again, " if k else ""), "the bar stamped ", _ct(*S, "live"),\n                       " CT), ", VOID_AT_LIVE, VOID_END[pair])', '                pass', ''),
    ("C3-1a the store's previous day for the session", DC_, '    prev = prior_session(src, d)\n    if prev is None:\n        return ["first_day"]', '    prev = src.previous(d)\n    if prev is None:\n        return ["first_day"]', ''),
    ('C3-1b the mismatch check dropped', PB, '        if i == 0 or prev is None or parse_day(hist.days[i - 1], "the previous day") != prev:', '        if False:', ''),
    ('C3-1c a scheduled close missing from the store ignored', DC_, '    if _scheduled_close(src.calendar.get(prev)) is not None:\n        prior.append("after_abbreviated")\n    k = prev', '    if prev in src._index and _scheduled_close(src.calendar.get(prev)) is not None:\n        prior.append("after_abbreviated")\n    k = prev', ''),
    ('C3-1d closures not skipped', DC_, '    while k.weekday() >= 5 or _closed_all_day(src, k):', '    while k.weekday() >= 5:', ''),
    ('C3-1e a store gap read as a closure (N-c2-2)', DC_, '        if k.weekday() < 5 and _closed_all_day(src, k):', '        if k.weekday() < 5:', 'equivalent: prior_session walks back over every scheduled closure, so every weekday between it and the day is one; C3-1d, which stops skipping them, is killed'),
    ("C3-2 the breakout's bounds not clipped", PB, '        lo = min(max(int(first) - lat, 0), T.P14_LAST)', '        lo = int(first) - lat', ''),
    ("C3-2b the breakout's last not clipped", PB, '        hi = max(min(int(last) - lat, T.P14_LAST), lo)', '        hi = int(last) - lat', ''),
    ('C3-3a the void line on the first stretch only', PB, '            if t["kind"] != W.MARKET:\n                d.line(', '            if t["kind"] != W.MARKET and not k:\n                d.line(', ''),
    ('C3-3b the pair worded as one order', PB, '" CT), ", VOID_AT_LIVE, VOID_END[pair])', '" CT), ", VOID_AT_LIVE, VOID_END[False])', ''),
    ("C3-4 a run off HEAD's line accepted", PO_, '    return _git(repo, "merge-base", "--is-ancestor", commit, "HEAD").returncode == 0', '    return True', ''),
    ('C3-5a several margin rows accepted', PB, '    if margins != [decl["side"]["margin_row"]] or not order.index(margins[0]) < order.index(first):', '    if decl["side"]["margin_row"] not in margins or not order.index(decl["side"]["margin_row"]) < order.index(first):', ''),
    ('C3-5b a margin row after the pin accepted', PB, '    if margins != [decl["side"]["margin_row"]] or not order.index(margins[0]) < order.index(first):', '    if margins != [decl["side"]["margin_row"]]:', ''),
    ('C3-6a the source line dropped from the pair', PB, '        d.line(PAIR_WORDS)\n        d.line(*_SOURCE_LINE)\n', '        d.line(PAIR_WORDS)\n', ''),
    ('C3-6b the double fill flattened only', PB, '"fill both before you cancel: if it does, close every position and cancel every working order in this "', '"fill both before you cancel: if it does, flatten the second fill at once in this "', ''),
    ('C3-7a the held-out verdict unread', PB, '    if heldout.values.get(hk) != HELDOUT_ACCEPTED:', '    if False:', ''),
    ('C3-7b withdrawn accepted', PB, '                         r"\\bunless\\b|\\bpending\\b|\\bdraft\\b|\\bprovisional\\b|\\bconditional|\\bwithdrawn\\b|"', '                         r"\\bunless\\b|\\bpending\\b|\\bdraft\\b|\\bprovisional\\b|\\bconditional|"', ''),
    ('C3-7c reverted, would be, not run accepted', PB, '                         r"\\brevert(?:ed|s)?\\b|\\bwould be\\b|\\bnot run\\b", re.I)', '                         r"\\bnever\\b", re.I)', ''),
    ('C3-8a a band value for any measure', PB, '            elif RESULT_COLUMNS[f] == FIGURE and not listed and BARE.fullmatch(cell):', '            elif False:', ''),
    ('C3-8b no exponent', PB, 'BARE = re.compile(r"-?\\d+(?:\\.\\d+)?(?:[eE][-+]?\\d+)?")', 'BARE = re.compile(r"-?\\d+(?:\\.\\d+)?")', ''),
    ('C3-8c any measure id may carry a band figure', PB, '                if f == "measure" and listed:', '                if f == "measure":', ''),
    ('N-c3-2 ny_pm accepted', PB, '        if c["session"] in UNDECLARED_SESSIONS:', '        if False:', ''),
    ("N-c3-3 the journey's run order unchecked", PB, '    if not _run_after_pin(root, pin_text, expected.commit):', '    if False:', ''),
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
