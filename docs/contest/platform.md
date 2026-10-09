# Platform (codingcontest.org, the rebuilt platform)

## Key facts
- **Catcoder is retired.** `catcoder.codingcontest.org` and `register.codingcontest.org` now redirect with a 302 to codingcontest.org. Community tools built for Catcoder (Lingepumpe/ccc_solver_template, lcian/catcoder-cli, catcoder-vscode) are **probably broken**.
- **New platform:** an Angular app. The contest game page is `/contests/:contestName/game`. **Each game is its own app inside an iframe** (e.g. `spaceship.codingcontest.org`).
- **Auth:** the platform calls `POST /api/game-token`, then posts `{type:'ccc:auth-token', token, contestSlug, contestStartMs, contestDurationMinutes}` to the iframe. The game sends `Authorization: <token>` and `X-CCC-SLUG: <slug>`. Opened directly, a game URL returns 403: "This game can only be accessed through the CCC platform".
- **The 2026 contest is the first live contest on this platform.** It went live around 2026-09-15.

## Game API endpoints (from the game client, 2026)
| Purpose | Endpoint |
|---|---|
| Contestant state | `GET /api/contestant/contestant-info` |
| Level zip (statement + inputs) | `GET /api/contestant/level/{N}/files` → `level-N.zip` |
| Single input | `GET /api/contestant/level/{N}/input/{fileId}` |
| Visualizer/sandbox | `GET /api/contestant/level/{N}/sandbox` |
| Submit one output | `POST /api/contestant/submit-{level}-{fileId}` (multipart field `solution`) |
| Live scores (SSE) | `/api/contests/scores/stream?contestSlug=…` |

## Public API (no login needed)
| Purpose | Endpoint |
|---|---|
| Current edition | https://codingcontest.org/api/editions/active |
| Our contest | https://codingcontest.org/api/contests/42nd-classic-ccc-5872 (the game shows as `unknown-game` until the start) |
| Practice games list | https://codingcontest.org/api/games |
| One practice game | https://codingcontest.org/api/training/{slug} (e.g. `ccc-2025.11-classic-spaceship`) |
| Hall of Fame (2025 Classic) | https://codingcontest.org/api/hall-of-fame/contests/37/leaderboard |

## Practice: https://codingcontest.org/challenges (login + Participant role)
- **Challenge mode:** timed at 240 minutes; levels unlock one after another, exactly like the real contest.
- **Exploration mode:** no timer and every level is open. Use it to download statements and try the visualizer.
- **Classic games available (4):**

  | Game | Levels |
  |---|---|
  | Spaceship (2025.11) | 8 |
  | Room Planner (2024.10) | 7 |
  | Lawn Mower (2024.04) | 7 |
  | Rock Paper Scissors (2023.03) | 7 |

  (Islands is not available.)
- **Offline archives:**
  - https://github.com/gergely-elias/ccc (PDFs and inputs for Room Planner, Lawn Mower and RPS)
  - https://github.com/aarroyoc/catcoder
  - https://github.com/angua/CCC41 (a Spaceship solution in C#)

## Confirmed by hands-on test (2026-10-09, Lawn Mower in Exploration mode)
- **Auth:** cookies `SESSION` + `XSRF-TOKEN` (POSTs need the `X-XSRF-TOKEN` header).
  - `POST /api/game-token {contestSlug}` → `{token}`.
  - The game API lives on the **game's origin** (e.g. `https://lawn-mower.codingcontest.org/api/contestant/...`) with headers `Authorization: <token>` and `X-CCC-SLUG: <contestSlug>`.
  - **Scripted access works.** Our CLI is `arena/ccc.py`.
- **Training start:** `POST /api/training/{gameSlug}/start?mode=exploration|challenge` → contest `training-<slug>-<id>`. Then `GET /api/contests/{name}` gives the `gameBaseUrl`.
- **Zip contents:**
  - Inputs: `in_level-N_<fileId>.txt` with fileIds `0-example`, `1-small`, `2-small`, `3-medium`, `4-medium`, `5-large`.
  - Expected example output: `out_level-N_0-example.txt`.
  - Statement: `level-N.pdf`, about 1 MB, styled slides.
- **`contestant-info`** → `score.state.levelN.passedFiles` (scored ids) and `passedAt`; `score.gameScore {level, timeMs}`.
- **Submit response:** `{"evaluation":{"isCorrect":bool,"cases":[{isCorrect, caseState: CORRECT|WRONG_SOLUTION|NOT_GIVEN, startLineNumber, endLineNumberExcl, caseMessage}]}}`, i.e. **per-case feedback with line ranges**.
- **Cooldown:** about 5 s per file after a submit (HTTP 429 `{"cooldownSec":N}` plus a `Retry-After` header).
- **Speed:** one level took about 30 s from fetch to all files correct for the simple Lawn Mower L1–L3.

## Implications for automation
- **Downloading and submitting are scripted and tested** via `arena/ccc.py`. Teo cleared the rules with the organizers (2026-10-09).
- **The safest fallback** is a local pipeline that unzips the level, solves it, writes the outputs with the right file names, and leaves the drag-and-drop upload to a person.

## Open questions
- Whether the zip naming and statement format will be the same for the new 2026 game. If not, the tool falls back to the platform's "last number picks the case" rule.
