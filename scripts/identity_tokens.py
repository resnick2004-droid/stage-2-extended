"""The identity-holds tokens of DECISIONS.md (Q-110; E-098's rule, E-104's positional form): each row's token, whether
the waits asked for are met, and every breach.

    python scripts/identity_tokens.py                                     # this tree's DECISIONS.md
    python scripts/identity_tokens.py --held Q-80 extended/gate.py identity/gate_identity.py --held t10w2 <paths>
    python scripts/identity_tokens.py --path <a file> --repo <a repository> --head <a commit>

The lead runs it before committing a row that writes a token, and before committing any heavy run whose runner waits
on tokens. `--held ID PATH [PATH ...]` (repeatable) asks `extended.identity_tokens.held` whether a row records ID
holding at a commit that is `--head` (default HEAD) or its ancestor, with the PATHs unchanged since, in `--repo`
(default this tree); for each it prints the row admitted, or NOT held and why each row carrying ID did not qualify.

Exit 0: no breach and every wait asked is met; 1: a breach (listed; it takes precedence); 3: no breach, but a wait
asked is not met; 2: the file cannot be read, or a wait cannot be checked (a covered path not at the head, a head that
is not a commit). The grammar, the checks and their limits: `extended/identity_tokens.py`. Reads nothing but the one
text file and git's objects; writes nothing.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import extended.identity_tokens as IT  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--path", type=Path, default=ROOT / "DECISIONS.md", help="the decision log (default: this tree's)")
    ap.add_argument("--held", nargs="+", action="append", default=[], metavar=("ID", "PATH"),
                    help="an identity's id and the paths its identity covers (repeatable)")
    ap.add_argument("--repo", type=Path, default=ROOT, help="the repository the shas are read in (default: this tree)")
    ap.add_argument("--head", default="HEAD", help="the commit being run (default: HEAD)")
    a = ap.parse_args(argv)

    try:
        text = a.path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        print(f"cannot read {a.path}: {e}")
        return 2

    toks = IT.parse(text)
    print(f"{a.path.name}: {len(toks)} identity-holds token(s), positional only (placeholders <id> and Q-nn ignored)")
    for t in toks:
        print(f"  {t.row}  {t.ident}  at {t.sha}")

    unmet = 0
    if a.held:
        print(f"held at {a.head} in {a.repo}:")
    for item in a.held:
        ident, covered = item[0], item[1:]
        if not covered:
            print(f"  {ident}: cannot check -- give the paths its identity covers after the id")
            return 2
        try:
            tok, why = IT.held_report(text, ident, a.repo, a.head, covered)
        except (ValueError, TypeError, RuntimeError, OSError) as e:
            print(f"  {ident}: cannot check -- {e}")
            return 2
        if tok is not None:
            print(f"  {ident}: held -- {tok.row} at {tok.sha}; unchanged since: {', '.join(covered)}")
        else:
            unmet += 1
            print(f"  {ident}: NOT held")
        for w in why:
            print(f"      {w}")

    probs = IT.problems(text)
    if probs:
        print(f"breaches ({len(probs)}):")
        for p in probs:
            print(f"  {p}")
        return 1
    print("breaches: none")
    return 3 if unmet else 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")
    raise SystemExit(main())
