"""Assemble the Q-12 note: body.md with its generated parts filled in.

Usage: python -I assemble.py <scratch-root> <out-note>
"""
import os
import subprocess
import sys

S, OUT = sys.argv[1], sys.argv[2]
T = os.path.join(S, "tools")
ORDER = ["funderpro", "daytraders", "tradingpit", "aqua", "alpha", "lucid", "tradeify", "blusky", "e2t",
         "fundednext", "tradeday", "topone", "fxify", "ffn", "mffu", "phidias",
         "goat", "bulenox", "tpt", "legends", "purdia", "futuresdesk"]


def run(*args):
    r = subprocess.run([sys.executable, "-I", *args], capture_output=True, text=True, encoding="utf-8", check=True)
    return r.stdout.strip()


unverified = run(os.path.join(T, "lists.py"), S, "unverified", *ORDER)
conflicts = run(os.path.join(T, "lists.py"), S, "conflicts", *ORDER)
arith = run(os.path.join(T, "arith.py"))
app_path = os.path.join(S, "appendix.md")
run(os.path.join(T, "make_appendix.py"), S, app_path, *ORDER)
appendix = open(app_path, encoding="utf-8").read().strip()
body = open(os.path.join(S, "body.md"), encoding="utf-8").read()
for k, v in (("{{UNVERIFIED}}", unverified), ("{{CONFLICTS}}", conflicts), ("{{ARITH}}", arith), ("{{APPENDIX}}", appendix)):
    assert body.count(k) == 1, k
    body = body.replace(k, v)
assert not any(m in body for m in ("{{UNVERIFIED}}", "{{CONFLICTS}}", "{{ARITH}}", "{{APPENDIX}}"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(body.rstrip() + "\n")
print(f"{OUT}: {len(body)} chars")
