"""Mutation probes of the Mac run agent (Q-229 part 2) against `tests/test_mac_agent.py`. Not collected by pytest; run
by hand when the agent, its schema, its collect step or their tests change:

    python tests/mac_agent_mutants.py            # prints KILLED / SURVIVED per mutant and the count
    python tests/mac_agent_mutants.py A17 C15    # only the mutants with these ids

Each mutant replaces exact texts (each found exactly once) in one file, runs the tests its refusal is guarded by (a
`-k` selection of `tests/test_mac_agent.py`, `-x`), and restores the file in a `finally` -- the file's sha256 is checked
after every mutant and at the end. A mutant is KILLED when the selected tests fail.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MA_ = "extended/mac_assignments.py"
AG_ = "scripts/mac_agent.py"
CO_ = "scripts/mac_collect.py"
RL_ = "scripts/run_lock.py"
RC_ = "scripts/run_clean.py"

GUARD_PUBLISH = ('''        bad = self.guard(run, idx)
        if bad:
            return self.fail(run, "the price-level guard refused the run's files: " + "; ".join(bad))
        tree = self.text("write-tree", env=self._index_env(idx))''',
                 '''        tree = self.text("write-tree", env=self._index_env(idx))''')
PUSH_THEN_GUARD = ('''        self.git("update-ref", ref, commit, "")                       # made only if it does not exist
        return self._push_and_mark(run, ref, commit)''',
                   '''        self.git("update-ref", ref, commit, "")                       # made only if it does not exist
        rc = self._push_and_mark(run, ref, commit)
        bad = self.guard(run, idx)
        if bad:
            return self.fail(run, "the price-level guard refused the run's files: " + "; ".join(bad))
        return rc''')

#: (id, file, [(old, new), ...], -k selection)
MUTANTS = [
    # the schema
    ("S1 a missing field accepted", MA_, [('        if k not in r:\n            bad.append(f"{who}: the field {k!r} is missing")',
                                          '        if False:\n            bad.append(f"{who}: the field {k!r} is missing")')], "missing_field"),
    ("S2 a short sha accepted", MA_, [('SHA = re.compile(r"[0-9a-f]{40}")', 'SHA = re.compile(r"[0-9a-f]{7,40}")')], "sha"),
    ("S3 a duplicate name accepted", MA_, [('for n in sorted({n for n in names if isinstance(n, str) and names.count(n) > 1}):', 'for n in []:')], "duplicate"),
    ("S4 any command accepted", MA_, [('        if not isinstance(cmd, str) or not COMMAND.fullmatch(cmd):', '        if not isinstance(cmd, str):')], "command_outside"),
    ("S5 shell syntax accepted", MA_, [('unsafe = not isinstance(cmd, str) or not SAFE.fullmatch(cmd) or "  " in cmd or cmd != cmd.strip()', 'unsafe = False')], "shell_syntax"),
    ("S6 dates unchecked", MA_, [("        if day is not None and day >= SEAL_START:", "        if False:")], "markers"),
    ("S7 only the confirmation window's dates", MA_, [("        if day is not None and day >= SEAL_START:", "        if day is not None and day >= CONFIRMATION_START:")], "markers"),
    ("S8 marker words unchecked", MA_, [("    for m in MARKER_WORDS.finditer(text):", "    for m in []:")], "markers"),
    ("S9 a block option unchecked", MA_, [('        if "block" in parts and val.lower() not in BLOCK_OK:', '        if False:')], "markers"),
    ("S10 a year option unchecked", MA_, [("        if parts & DATE_OPTION_WORDS and YEAR.fullmatch(val) and int(val) > SEAL_START.year:", "        if False:")], "markers"),
    ("S11 names and outputs unscanned", MA_, [("    texts = [v for v in (name, cmd, t, note) if isinstance(v, str)]", "    texts = [v for v in (cmd,) if isinstance(v, str)]")], "markers_in_names"),
    ("S12 an unknown field accepted", MA_, [("        if k not in FIELDS and k not in OPTIONAL:", "        if False:")], "malformed"),
    ("S13 the agent's own scripts accepted", MA_, [("            if script in FORBIDDEN_SCRIPTS:", "            if False:")], "own_scripts"),
    # the lock's TAKEN line
    ("L1 TAKEN without the memory", RL_, [('          f"{memory_words(lock)}")', '          "")')], "taken_line"),
    ("L2 the memory words not from the record", RL_, [('    have, need = lock.get("mem_gb_available_at_start"), lock.get("mem_gb_needed")', '    have, need = None, lock.get("mem_gb_needed")')], "taken_line or memory_words"),
    # the agent
    ("A1 a held lock not looked at", AG_, [("        if held is not None:\n            self.say(f\"the run lock is held", "        if False:\n            self.say(f\"the run lock is held")], "held_lock"),
    ("A2 unreadable memory not looked at", AG_, [('        if gb is None:\n            self.say("this machine', '        if False:\n            self.say("this machine')], "unreadable_memory_starts"),
    ("A3 short memory not looked at", AG_, [("        if gb < run.mem_gb:", "        if False:")], "short_memory"),
    ("A4 a refused take read as a failure", AG_, [("            if rc in (HELD, MEMORY) and any(line.startswith(LOCK_REFUSED) for line in tail):", "            if False:")], "at_run_cleans_take"),
    ("A5 the push before the guard", AG_, [GUARD_PUBLISH, PUSH_THEN_GUARD], "guard"),
    ("A6 the guard skipped", AG_, [GUARD_PUBLISH], "guard"),
    ("A7 the guard's refusals ignored", AG_, [('        bad = [f"REFUSED {f}" for f in rep.refused]', "        bad = []")], "guard"),
    ("A8 any ref pushed", AG_, [("        if not MAC_REF.fullmatch(ref) or self.remote != REMOTE:", "        if False:")], "push_to"),
    ("A9 the mac ref pattern loosened", AG_, [('MAC_REF = re.compile(r"refs/heads/mac/" + MA.NAME.pattern)', 'MAC_REF = re.compile(r"refs/heads/mac/.+")')], "push_to"),
    ("A10 a non-zero exit read as success", AG_, [("        if rc != 0 or m is None or int(m.group(1)) != 0:", "        if m is None:")], "non_zero"),
    ("A11 a failed run re-run", AG_, [('            if self.marker(r.name, "done").exists() or self.marker(r.name, "failed").exists():\n                continue',
                                       '            if self.marker(r.name, "done").exists():\n                continue')], "non_zero"),
    ("A12 an unacknowledged failure not blocking", AG_, [("        if blocking:", "        if False:")], "non_zero"),
    ("A13 a wrong or dirty manifest accepted", AG_, [('            if m.get("git_commit") != run.commit or m.get("git_dirty") is not False:', "            if False:")], "wrong_manifest"),
    ("A14 a file not assigned accepted", AG_, [('        bad = [f"missing: {p}" for p in sorted(want - got)] + [f"not assigned: {p}" for p in sorted(got - want)]',
                                               '        bad = [f"missing: {p}" for p in sorted(want - got)]')], "wrong_manifest"),
    ("A15 the assignments read from the local HEAD", AG_, [('        out = self.git("show", f"{self.remote}/master:{MA.CONFIG_REL}", check=False)',
                                                            '        out = self.git("show", f"HEAD:{MA.CONFIG_REL}", check=False)')], "origin_master"),
    ("A16 an interrupted run re-run", AG_, [("        if wt.exists() or log.exists():", "        if False:")], "interrupted"),
    ("A17 the allow-list read from the local tree", AG_, [("        allow_file.write_bytes(out.stdout)", "        allow_file.write_bytes((self.repo / PL.ALLOWLIST_REL).read_bytes())")], "allow_list"),
    ("A18 STOP ignored", AG_, [('        if (self.state / "STOP").exists():', "        if False:")], "stop_file"),
    ("A19 two agents at once", AG_, [("            if not alone:", "            if False:")], "second_agent"),
    ("A20 the sha256 of a file unchecked", AG_, [('            if m.get("sha256") != _sha256(wt / o):', "            if False:")], "wrong_manifest"),
    ("A21 a branch on origin not skipped", AG_, [("            if pushed:\n                self.done(r, pushed)", "            if False:\n                self.done(r, pushed)")], "already_on_origin"),
    ("A22 a failed push not retried", AG_, [('            if self.local(r):\n', "            if False:\n")], "failed_push"),
    # run_clean's log and the manifest's host
    ("R1 the log does not name the host", RC_, [('        f.write(host + "\\n")', "        pass")], "pushed_to_its_mac_branch"),
    # the collect
    ("C1 the commit unchecked", CO_, [('        if m.get("git_commit") != run.commit:', "        if False:")], "collect_refuses_a_mismatch"),
    ("C2 dirty accepted", CO_, [('        if m.get("git_dirty") is not False:', "        if False:")], "collect_refuses_a_mismatch"),
    ("C3 the files unchecked", CO_, [("    if set(entries) != want:", "    if False:")], "collect_refuses_a_mismatch"),
    ("C4 verify skipped", CO_, [("            if not ok:\n                raise CollectRefused", "            if False:\n                raise CollectRefused")], "collect_refuses_a_mismatch or vendored_verify"),
    ("C6 the record unmatched", CO_, [('    if not isinstance(record, dict) or not MA.same_identity(record.get("assignment") or {}, run.as_dict()):', "    if not isinstance(record, dict):")], "collect_refuses_a_mismatch"),
    ("C7 the log's exit unchecked", CO_, [('    if not log_lines or log_lines[-1].strip() != "EXIT 0":', "    if not log_lines:")], "collect_refuses_a_mismatch"),
    ("C9 any checkout path", CO_, [('        if not (c.startswith("/") and parts[-2:] == ("stage2-extended-runs", run.name)):', "        if False:")], "posix_runs_path"),
    ("C10 a held folder overwritten", CO_, [('    if dest.exists():\n        raise CollectRefused', "    if False:\n        raise CollectRefused")], "copies_a_good_run"),
    ("C11 a results folder accepted", CO_, [('        if q.name.lower() == "results":', "        if False:")], "holding_folder"),
    ("C12 the clean run's name unchecked", CO_, [('        if clean.get("name") != run.name:', "        if False:")], "collect_refuses_a_mismatch"),
    ("C13 the log's host unchecked", CO_, [('    if not (first.startswith(f"host: {host} (") and first.endswith(")")):', "    if False:")], "logs_host or records_host"),
    ("C14 a run not assigned collected", CO_, [("    if run is None:\n        raise CollectRefused", "    if False:\n        raise CollectRefused")], "not_assigned"),
    ("C16 a record without a host accepted", CO_, [('    if not isinstance(host, str) or not host:', "    if False:")], "without_a_host"),
    ("A23 git may prompt", AG_, [('        env = {**(env if env is not None else os.environ), "GIT_TERMINAL_PROMPT": "0"}', "        env = env")], "never_prompts"),
]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    env = {**os.environ, "OMP_NUM_THREADS": "1", "PYTHONDONTWRITEBYTECODE": "1"}
    originals = {f: sha(ROOT / f) for f in {m[1] for m in MUTANTS}}
    killed, survived = [], []
    only = sys.argv[1:]
    for mid, f, edits, sel in MUTANTS:
        if only and mid.split()[0] not in only:
            continue
        path = ROOT / f
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        crlf = "\r\n" in text
        s = text.replace("\r\n", "\n")
        for old, new in edits:
            n = s.count(old)
            if n != 1:
                print(f"BAD MUTANT {mid}: its text is found {n} times in {f}")
                return 2
            s = s.replace(old, new)
        try:
            path.write_bytes((s.replace("\n", "\r\n") if crlf else s).encode("utf-8"))
            out = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-o", "addopts=", "-p", "no:cacheprovider",
                                  "tests/test_mac_agent.py", "-k", sel], cwd=ROOT, env=env, capture_output=True,
                                 text=True, timeout=900)
        finally:
            path.write_bytes(raw)
        if sha(path) != originals[f]:
            print(f"RESTORE FAILED for {f}")
            return 3
        ok = out.returncode == 1 and " failed" in out.stdout
        (killed if ok else survived).append(mid)
        print(f"{'KILLED' if ok else 'SURVIVED'}  {mid}  (exit {out.returncode}; {out.stdout.strip().splitlines()[-1] if out.stdout.strip() else ''})",
              flush=True)
    for f, h in originals.items():
        if sha(ROOT / f) != h:
            print(f"RESTORE FAILED for {f}")
            return 3
    print(f"{len(killed)} killed, {len(survived)} survived of {len(killed) + len(survived)} run "
          f"({len(MUTANTS)} defined): {survived}")
    return 0 if not survived else 1


if __name__ == "__main__":
    raise SystemExit(main())
