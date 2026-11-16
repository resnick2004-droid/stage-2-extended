# Operator setup -- the only channel for the operator's manual tasks

Each item is copy-paste complete. Nothing here blocks the research: every item has a safe default the sessions keep
until it is done. **Nothing is ever bought without the operator's explicit yes.**

| # | item | why | safe default meanwhile | status |
|---|---|---|---|---|
| 1 | **NQ 1-minute bars from 2026-07-17** (Databento GLBX.MDP3 ohlcv-1m, at least six months) | the declared confirmation window of any carried candidate (F-01 section 6; Stage 2 `docs/OPERATOR_SETUP.md` item 6) | nothing is confirmed; development work continues | open -- a purchase: the price is quoted by Databento at the time; not authorised |
| 2 | **ES 1-minute bars** | more markets raise the power of every family (Stage 2 `docs/OPERATOR_SETUP.md` item 1) | NQ only | open -- a purchase; not authorised |
| 3 | **Topstep support questions** -- closing a funded account at request to free its seat; seat timing (Stage 2 item 5) | an unverified rule (`xfa_closure_at_request`) no design may use until answered | no design closes funded accounts at request | open |
| 4 | **Lucid's two unpriced fees** (funded monthly, payout) | a Lucid design cannot be priced in full | Lucid stays a reading beside, never a candidate | open |
| 5 | **A private GitHub remote for this repository** | backup; push after every commit | -- | done by the session (E-004): `resnick2004-droid/stage-2-extended`, private |
| 6 | **May this repository live outside OneDrive?** (asked once) | OneDrive locks files under a running job and has broken in-repo worktrees before; the worktrees and clean runs already live outside it, in `%LOCALAPPDATA%` | it stays at `Desktop\Stage 2 - Extended`; GitHub is the backup | open -- answer yes or no; on yes the session moves it to `%USERPROFILE%\research\stage2-extended` and leaves a note in the old folder |
| 7 | **More history, free: QuantConnect's NQ and ES minute data from 2009** | six and a half years of NQ give low power for rare effects (bootstrap Part 6); QuantConnect's history would add about eleven years | NQ 2020-2026 only | open -- see below |
| 8 | **More history, a purchase: Databento NQ 1-minute bars 2010-01-01 to 2019-12-31** | the same reason, on the operator's own licensed store, read locally | NQ 2020-2026 only | open -- a purchase; not authorised |
| 9 | **Memory for heavy runs** | a campaign or a full identity needs about 3 GB; on 2026-11-15 the machine had about 1.7 GB available, the rest held by other applications | light work runs; a heavy run waits until the memory is there (the session checks before it starts) | open -- see below |

## Item 6 -- the repository outside OneDrive

Answer **yes** or **no** in any session. Nothing else to do.

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

Nothing is required. If convenient, before leaving the machine for a while, close idle applications (spare editor
windows, games, WSL, browser tabs) or tell any session the hours the machine is usually idle; heavy runs are then
scheduled into them. A heavy run never starts without the memory it needs.
