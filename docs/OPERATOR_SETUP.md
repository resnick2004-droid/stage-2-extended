# Operator setup -- the only channel for the operator's manual tasks

Each item is copy-paste complete. Nothing here blocks the research: every item has a safe default the sessions keep
until it is done. **Nothing is ever bought without the operator's explicit yes.**

| # | item | why | safe default meanwhile | status |
|---|---|---|---|---|
| 1 | **NQ 1-minute bars from 2026-07-17** (Databento GLBX.MDP3 ohlcv-1m, at least six months) | the declared confirmation window of any carried candidate (F-01 section 6; Stage 2 `docs/OPERATOR_SETUP.md` item 6) | nothing is confirmed; development work continues | open -- a purchase: the price is quoted by Databento at the time; not authorised |
| 2 | **ES 1-minute bars** | more markets raise the power of every family (Stage 2 `docs/OPERATOR_SETUP.md` item 1) | NQ only | open -- a purchase; not authorised |
| 3 | **Topstep support questions** -- closing a funded account at request to free its seat; seat timing (Stage 2 item 5); and, optional (E-013), whether a funded account's first trade sized several times its later trades breaches Terms of Use s.8 -- text below | an unverified rule (`xfa_closure_at_request`) no design may use until answered | no design closes funded accounts at request | open |
| 4 | **Lucid's two unpriced fees** (funded monthly, payout) | a Lucid design cannot be priced in full | Lucid stays a reading beside, never a candidate | open |
| 5 | **A private GitHub remote for this repository** | backup; push after every commit | -- | done by the session (E-004): `resnick2004-droid/stage-2-extended`, private |
| 6 | **May this repository live outside OneDrive?** (asked once) | OneDrive locks files under a running job and has broken in-repo worktrees before; the worktrees and clean runs already live outside it, in `%LOCALAPPDATA%` | it stays at `Desktop\Stage 2 - Extended`; GitHub is the backup | **answered 2026-11-15** -- the operator: "Pushing the updates to github is best". The repository stays where it is; every commit and every worker branch is pushed to the private remote (the post-commit hook) |
| 7 | **More history, free: QuantConnect's NQ and ES minute data from 2009** | six and a half years of NQ give low power for rare effects (bootstrap Part 6); QuantConnect's history would add about eleven years | NQ 2020-2026 only | open -- see below |
| 8 | **More history, a purchase: Databento NQ 1-minute bars 2010-01-01 to 2019-12-31** | the same reason, on the operator's own licensed store, read locally | NQ 2020-2026 only | open -- a purchase; not authorised |
| 9 | **Memory for heavy runs** | a campaign or a full identity needs about 3 GB; on 2026-11-15 the machine had about 1.7 GB available, the rest held by other applications | light work runs; a heavy run waits until the memory is there (the session checks before it starts) | open -- see below |
| 10 | **Two written questions to other firms** (optional) -- DayTraders.com on its Terms s.26 item 3.c, TradeDay on its multiple-users sentence -- text below | the other-firms reading (`prereg/DRAFT_RD_firms.md`) names each question as open on its plan's rows | the reading runs as declared, those rows labelled | open |
| 11 | **Alpha Futures' $50K terms, and Lucid's $50K prices, read by hand** (E-197) -- screenshots of public pages, saved unedited | Alpha's terms forbid automated access (E-020 (2)), and Lucid's, as modified on 2026-11-13, forbid copying or monitoring its content "by automated or unauthorized means", and an agent driving the operator's browser is still automated access, so no session reads Alpha's site | Alpha is carried as unread: no contract, no zero-edge map, no sizing grid; Lucid stays on Stage 2's verified LucidFlex record, unpriced for the other plans | open |
| 12 | **The Mac as a second run host** (Apple M4, 16 GB; the operator's choice, E-298) | a second machine runs heavy parts beside this one, if its results match this machine's digit for digit | every heavy run on this machine, one at a time | **done** -- the Mac's exact H4 slice matched this machine's file for file (E-301) |
| 13 | **Start the Mac run agent** (E-301) -- one hand start, then a timer | the Mac runs the heavy parts the lead assigns it, by itself, one at a time | those parts wait for this machine | open -- see below |

## Item 6 -- the repository outside OneDrive

Answered 2026-11-15: it stays; GitHub is the backup. Worktrees and clean runs stay in `%LOCALAPPDATA%`.

## Item 7 -- QuantConnect (free)

1. On quantconnect.com, sign in, open **My Account -> API Access**, and copy your **User ID** and **API Token**.
2. In Windows: **Start -> "Edit environment variables for your account" -> New**, twice:
   - name `QC_USER_ID`, value: your User ID
   - name `QC_API_TOKEN`, value: your API Token
3. Restart VS Code, then tell any session: "QuantConnect configured".

The session then connects QuantConnect's MCP server, with every live-trading tool denied (`.claude/settings.json`
and a hook), and reads only development data; the confirmation window (NQ from 2026-07-17) stays unread. The free tier
is enough: the session never buys a seat, node or data, and states any cost it finds before anything is spent.

## Item 8 -- Databento, older NQ (a purchase)

The same request shape as the NQ purchase on record (Stage 2, 2026-10-07):

| field | value |
|---|---|
| dataset | `GLBX.MDP3` |
| schema | `ohlcv-1m` |
| symbology | `parent` |
| symbols | `NQ.FUT` |
| date range | `2010-01-01` to `2019-12-31` (UTC) |
| encoding | CSV |
| options | pretty prices, pretty timestamps, symbols mapped |
| delivery | download; leave the zip in `Downloads`, do not rename it |

Expected cost: Databento's checkout shows the exact figure before paying; the operator decides there. After download,
tell any session "older NQ downloaded": the session records the zip's sha256 in a decision row and declares how the
older era is used (Stage 2 D-271's era rule) before any of it is read.

## Item 9 -- memory for heavy runs

**Needed now (2026-11-20, E-244):** the machine has under 1 GB of memory free, and every commit's test run needs 1.5 GB
and every heavy run 1.5 to 3 GB, so the work is stalled. What holds it, none of it this project's: WSL / Docker (about
3 GB), the Campaign Studio server (`scripts/serve.py` of "Stage 2C - Campaign Studio", about 2.8 GB), other Claude
sessions and editor windows, Discord, Steam, the ChatGPT app and browser tabs. Closing whichever you are not using
frees it; nothing of this project needs any of them. Otherwise, nothing is required. If convenient, before leaving the machine for a while, close idle applications (spare editor
windows, games, WSL, browser tabs) or tell any session the hours the machine is usually idle; heavy runs are then
scheduled into them. A heavy run never starts without the memory it needs.

## Item 3 -- the optional question on position size (E-013)

If you write to Topstep support, this is the question, ready to paste:

> Your Terms of Use (section 8) say risk standards are not met where a trader opens "substantially larger position
> sizes compared to your other trades". On an Express Funded Account, is it a breach to size the account's first
> trade larger than its later ones -- for example a first trade risking about $1,000-1,500 and later trades risking
> about $250 each, every trade within the account's position limits and the scaling plan? If there is a threshold
> or a guideline, where is it published?

Tell any session what they answer; it is recorded in a decision row. Until then the clause is priced as a risk.

## Item 10 -- two optional written questions to other firms (E-045)

Only if you hold or want an account there; each from your own account, by the firm's support channel. Ready to paste:

> **To DayTraders.com**, on its Terms of Use s.26 item 3.c ("Sharing trades and strategies with other users or making
> trades that were not Customer's own creation"): I trade only my own accounts, placing every order by hand. The trades
> follow a rules-based strategy I did not design myself (it was built for me from historical data). Are trades placed
> this way "not Customer's own creation" under s.26 3.c? Does the answer change if other, unconnected people could
> follow the same published strategy in their own accounts? Two more: do the commissions on your Instruments and
> Commissions page (MNQ $1.02, NQ $3.98 a round turn) include exchange and NFA fees, or are those charged on top?
> And how many business days does a payout take from request to receipt?

> **To TradeDay**, on "If multiple users are making the same trades, then all the accounts will be shut down, and the
> users suspended": I am one user trading my own accounts by hand. If my trades follow a strategy that other,
> unconnected TradeDay users might also follow independently, so that our trades coincide without any coordination,
> would my accounts fall under this sentence? Is one person copying their own trades across their own Evaluation and
> Funded Sim accounts outside it?

Tell any session what they answer; it is recorded in a decision row.

## Item 11 -- Alpha Futures' $50K terms, read by hand (E-197)

Alpha Futures' terms forbid "any automated use of the system, such as ... web scraping robots" (E-009, E-020 (2)). A session driving your browser would still be automated use, so this one is done by hand, the way Stage 2 read Lucid's prices (Stage 2 D-574).

1. Open https://alpha-futures.com/ in your own browser. Use only its public pages; don't sign in.
2. For each page below, take full-page screenshots (or Print -> Save as PDF), unedited, and save them in `docs/rules/alpha_2026-11-18/` with names like `B-03_standard_50k.png`. The date in each capture's corner, or the file's date, is the read date.
3. Tell any session "Alpha screenshots saved". The session hashes them, reads them, and the rules-verifier records each term under a decision row.

The pages (the full list with what each must show is section "Pages for the lead's browser" of `docs/research/firms/alphafutures_50k_2026-11-18.md`):

- B-1 the home page and its plan or pricing picker (every $50K product sold now)
- B-2 the Terms and Conditions
- B-3 the Standard $50K evaluation and funded account; B-4 the Advanced $50K; B-5 any instant-funded $50K
- B-6 drawdown; B-7 daily loss limit; B-8 consistency (evaluation and funded); B-9 payouts
- B-10 the move from funded to live; B-11 position size and scaling; B-12 account limits per person
- B-13 news trading; B-14 prohibited strategies and copy trading
- B-15 announcements from the last six months; B-16 data and platform fees; B-17 commissions

### Lucid (added by E-197)

Lucid's Terms of Use ("Last Modified: November 13, 2026") forbid anyone to "copy or monitor its content by automated or unauthorized means", so no session reads lucidtrading.com or its help centre from now on. By hand, as you did on 2026-11-05 (Stage 2 D-574): open https://lucidtrading.com/, and save unedited screenshots of the $50K pricing cards -- list and reset prices, and any activation, data or monthly fee line -- for LucidFlex (all four configurations), LucidPro (daily loss limit on and off), LucidDaily (each daily-loss-limit, drawdown and 30/40/50 % option) and LucidDirect, into `docs/rules/lucid_2026-11-18/`. Tell any session "Lucid screenshots saved".

**Also needed for Lucid's own design search (added E-246; optional, only when convenient):** on the same site and help centre, screenshots of the pages that state, for **LucidFlex 50K**: (1) the trading hours and any daily maintenance break; (2) how long a payout request or a held account stays open before it expires; (3) any limit on how many accounts can be started in a period; (4) how the payout request amount is chosen (all available, or a choice); (5) any payout fee; (6) the funded account's monthly fee. Save them in the same folder. Without them, Lucid's search runs with those levers switched off, which is safe but narrower.

## Item 12 -- the Mac as a second run host (E-298)

The licence: you are the licensee and have decided a private copy on your own Mac is within it (E-298 records your
decision). Five steps, about half an hour; the sessions do the rest.

1. **Tools** (Terminal): install Homebrew from brew.sh if it is not there, then
   `brew install python@3.12 git gh` and `gh auth login` (sign in to GitHub yourself, in the browser it opens).
2. **The repository**, outside iCloud Drive (iCloud locks files as OneDrive does):
   `mkdir -p ~/stage2x && cd ~/stage2x && gh repo clone resnick2004-droid/stage-2-extended && cd stage-2-extended`
   then `python3.12 -m venv ~/stage2x/venv && source ~/stage2x/venv/bin/activate && python -m pip install numpy==2.5.2 scipy==1.18.1 pandas==3.0.5 pyarrow==25.0.1 PyYAML==6.0.3 pytest==9.1.1 pytest-xdist==3.6.1`
3. **The data, directly between your two machines on the home network** -- never through OneDrive, iCloud, GitHub,
   e-mail or a chat (the licence: private use, no redistribution). On the Mac: System Settings > General > Sharing >
   Remote Login on. On this PC, in a terminal in the repository, type one encrypted copy of the two folders (about 64 MB)
   into the Mac's copy: `scp -r vendor/stage2/data/bars vendor/stage2/data/atlas <mac-user>@<mac-name>.local:~/stage2x/stage-2-extended/vendor/stage2/data/`
   Then Remote Login off again. Nothing is left anywhere else; this PC's copy is only read. Never screenshot them.
4. **Check** (Terminal, in the repository, with `source ~/stage2x/venv/bin/activate` first):
   `python scripts/vendor_stage2.py --verify` then
   `OMP_NUM_THREADS=1 python identity/stage2_identity.py --paths 4 > ~/identity_mac.txt 2>&1`
   (a few minutes).
5. **Send** the file `~/identity_mac.txt` to any session here (paste its text). The sessions decide from it whether the
   Mac's numbers match this machine's to the last digit; if any digit differs, the Mac is not used for results (that is
   expected on a different processor and costs nothing).

## Item 13 -- start the Mac run agent (E-301)

The agent runs, by itself, the heavy parts the lead assigns to the Mac: one at a time, under the Mac's own lock, and
it pushes only that run's result files to a private `mac/<run>` branch after the price-level check. It never places an
order, never touches `master`, never re-runs a failed part. In Terminal, on the Mac:

1. **Start it once by hand** (checks that fetching and pushing work without a password prompt):
   `cd ~/stage2x/stage-2-extended && git pull --ff-only && source ~/stage2x/venv/bin/activate`
   then `python scripts/mac_agent.py --status` and then `python scripts/mac_agent.py`
   (it runs one part, or says there is nothing to run, and exits).
2. **Install the timer** (it wakes at load and every 30 minutes; keep the Mac on power with the lid open):
   `mkdir -p ~/stage2-extended-runs/mac-agent`
   `python scripts/mac_agent.py --plist > ~/Library/LaunchAgents/com.stage2x.mac-agent.plist`
   `plutil -lint ~/Library/LaunchAgents/com.stage2x.mac-agent.plist`
   `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.stage2x.mac-agent.plist`
3. **To look:** `tail -n 40 ~/stage2-extended-runs/mac-agent/agent.log`, or `python scripts/mac_agent.py --status`.
   A `PUSHED mac/<name>` line or a `FAILED:` block: tell any session here (the lead collects or diagnoses it).
4. **To pause** without stopping a run: `touch ~/stage2-extended-runs/mac-agent/STOP` (remove the file to resume).
   **To remove the timer**, only while `--status` shows the lock FREE:
   `launchctl bootout gui/$(id -u)/com.stage2x.mac-agent` then `rm ~/Library/LaunchAgents/com.stage2x.mac-agent.plist`.
   Removing it during a run stops the run and leaves the lock held: tell the lead.
