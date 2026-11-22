---
description: Give the operator's short brief -- what is running, what has come back, the decisions that are theirs, and the blockers -- in plain language, with no typed result number
allowed-tools: Read, Bash, PowerShell, Glob, Grep
---

Give the operator's short brief (CLAUDE.md "Silence": the operator hears only a result, a decision that is theirs, or a
blocker). The operator is not a quant: write for a reader who knows trading accounts, not statistics. Read-only: this
command writes nothing (only the lead edits `STATUS.md`, `TASK_QUEUE.md`, `PROGRESS.md`, `DECISIONS.md`); the shell
is for the two status scripts below and read-only `git` only -- never a command that writes a file, takes the run
lock, starts a run or sends anything.

**Read first:** `STATUS.md` (the board: phase, running now, `NEEDS_OPERATOR`, the run lock, the machine), the last
entries of `PROGRESS.md`, the newest rows of `DECISIONS.md`, the top of `TASK_QUEUE.md`, `docs/OPERATOR_SETUP.md`
(their manual tasks), and `python scripts/run_lock.py status` and `python scripts/status.py` for the live state (if a
script is missing, read its sources directly and say so).

**Write the brief in four short parts, in this order, each a few plain sentences or bullets:**

1. **What is running.** The heavy run under the lock (its job, when it started, when it should end, and what it is
   for in one line), and the lanes at work (which worktree builds what, in words). Say "nothing heavy is running" when
   the lock is free.
2. **What has come back.** Each result collected since the last brief: what question it answered and what it means for
   the user's journey, in words ("passed its check", "did not beat the coin baseline", "held"), with its decision row
   and its result file named. **Never type a result number.** A figure appears only if quoted from a result file with
   a manifest, with the file named beside it (`results/<file>.csv`, the row and column); if it cannot be traced, leave
   it out and say "see `<file>`". **Never quote anything from a licensed-price derivative** -- a result file that is
   git-ignored or on the licence list (`.gitignore`'s "Licensed-price derivatives" block: E-179, E-245, e.g.
   `results/s1_range.csv`, `results/q121_vol_descriptive_a1.csv`): name the file and its row in `DECISIONS.md`, never a
   value, a level or a row of it. A figure from the search years is said to be from the years the design was chosen
   on, with its held-out reading beside when one exists. A failed check is reported as failed, with what is being
   diagnosed -- never softened.
3. **Decisions that are theirs.** Only what CLAUDE.md reserves to the operator: a payment (state the cost and what it
   buys, and that nothing is bought until they say so -- e.g. the confirmation-window data), a change to the objective,
   and anything `STATUS.md` lists under `NEEDS_OPERATOR`. Each as a question they can answer in a line, with the safe
   default the work keeps meanwhile. A research question is never theirs: do not put one here.
4. **Blockers.** Anything stopping the work: a stale or held run lock, memory too short for a heavy run, a failing
   identity or test, a result whose manifest does not verify, a declaration whose pinned hash no longer matches, an
   operator setup task outstanding in `docs/OPERATOR_SETUP.md`. Say "none" when there are none.

**Rules for the text.**
- Plain words; every term a quant would use is explained in passing (e.g. "the held-out years -- the data kept aside
  for the final check").
- No result number typed from memory or from a document; only quoted from a result file, named.
- Hand entry only: never suggest automating orders; a playbook (`extended/playbook.py`) is described as what the user
  trades by hand, and never quoted for a price (it prints none).
- Short: the whole brief fits on one screen. Lead with anything that needs the operator's answer.
- In plain English (the template's text v2 on wt/wt-lit): a design is shown against the operator's limits in the form in force -- the point estimate governs, the one-sided check beside (E-230) -- and every number is traced to its result file.
