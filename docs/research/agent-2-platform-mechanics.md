# Agent 2: Platform and problem mechanics (raw report, 2026-10-09)

Tags: **[OFFICIAL]** means Cloudflight pages, APIs, or the platform's JavaScript bundle. **[SECONDARY]** means participant repos, tools, or search snippets.

## 0. The biggest finding: Catcoder is retired
- `catcoder.codingcontest.org` now returns a 302 redirect to `https://codingcontest.org/`, and so do its old API paths. [OFFICIAL, 2026]
- The new platform is an Angular app with these routes:
  - `/challenges`
  - `/challenges/:gameSlug` (practice)
  - `/contests/:contestName/game`

  [OFFICIAL bundle, 2026]
- Each game runs as **its own app inside an iframe** (for example `https://spaceship.codingcontest.org/`). It authenticates with a token from `POST /api/game-token`. Opening the game directly returns "This game can only be accessed through the CCC platform". [OFFICIAL, 2026]
- **Consequence:** community tools built for Catcoder (`Lingepumpe/ccc_solver_template`, `lcian/catcoder-cli`) are probably dead. Any automation has to target the new game API described below.
- **The 42nd Classic:** 23 Oct 2026 at 13:00 UTC, 240 minutes, teams of up to 3. The game is not assigned yet (`"gameSlug":"unknown-game"`). https://codingcontest.org/api/contests/42nd-classic-ccc-5872 [OFFICIAL]

## 1. Problem structure
- The contest is level-based and difficulty rises with each level. The winner is the "highest level within the shortest time". https://codingcontest.org/info/how-it-works [OFFICIAL, 2026]
- Each game tells one story across all its levels, and later levels build on earlier code. https://github.com/gergely-elias/ccc [SECONDARY]
- Level counts from https://codingcontest.org/api/games (`totalLevels`) [OFFICIAL]:

  | Game | Edition | Levels |
  |---|---|---|
  | Spaceship | 2025.11 | 8 |
  | Room Planner | 2024.10 | 7 |
  | Lawn Mower | 2024.04 | 7 |
  | Rock Paper Scissors | 2023.03 | 7 |

  - The counts conflict. The 2025 recap blog says "six difficulty levels". The 2025 winner shows "7 levels".
  - Most participants don't finish all levels. [OFFICIAL]
- **Level N+1 unlocks only after level N passes.** The game code checks `isLevelAccessible(e) = isUntimed() || e <= maxAccessibleLevel`. [OFFICIAL bundle, 2026]
  - Practice "Challenge" mode works the same way: "Levels unlock sequentially… Simulates the real contest format." [OFFICIAL]

## 2. What you get per level
- **New platform:** one download per level, `level-${N}.zip`, from `GET /api/contestant/level/{N}/files`. The instructions say: "Download the problem statement and input files… Each level has its own download." [OFFICIAL bundle, 2026]
  - **Single input files:** `GET /api/contestant/level/{N}/input/{fileId}`.
  - **Optional sandbox/visualizer:** `GET /api/contestant/level/{N}/sandbox`.
  - **Metadata:** `inputFiles` and `unscoredFiles`. The example file is "Unscored / Optional", and the UI uses file id `0-example`.
  - **Unverified:** the exact file names inside the 2026 zip.
- **Catcoder era (2018–2024):** a PDF per level plus a zip of inputs. [SECONDARY] gergely-elias/ccc, aarroyoc/catcoder
  - **Inputs:** usually 5 scored inputs (`levelN_1.in` … `levelN_5.in`) plus `levelN_example.in` and `levelN_example.out`.
  - **Visualizer:** some levels included `visualizer.html`.
- The PDFs tell you to "For each input file, calculate the output and write it in a file. Upload your output file". [SECONDARY]

## 3. What you submit
- **Only output files, one per input.** [OFFICIAL bundle, 2026]
  - Endpoint: `POST /api/contestant/submit-{level}-{fileId}`, with multipart field `solution`.
  - Headers: `Authorization: <game token>` and `X-CCC-SLUG: <contestSlug>`.
  - In the UI you can "Drop your output files in the Solutions Module. Batch upload solutions or use the level tabs."
- **File names are matched loosely.** "Last number in the filename picks the case — e.g. `out_level_1_0-example.txt` → `0-example`." [OFFICIAL bundle]
  - **Accepted extensions:** none, `.txt .csv .tsv .out .dat .sol .log .json`.
  - **Size limit:** files over the limit get HTTP 413.
- **Source code:** the new client has **no source upload path**. "Any language, any tool." [OFFICIAL bundle]
  - **Catcoder era:** uploading source after finishing a level earned 2 bonus minutes. [OFFICIAL via snippet; SECONDARY tools]

## 4. Validation, scoring and penalties
- **Validation is automatic and instant, case by case.** The verdicts are "Correct / Wrong Solution / Parsing Error / Not Given". [OFFICIAL bundle]
- **Each file passes independently, and passed files stay passed.** A level passes when every scored file passes. The example file is not scored. [OFFICIAL bundle]
- **Optimization levels** can exist (`optimization:true`, `passScore`, `scoreDirection`). The UI says "Next level: ≥ X on every file" and **"Ranking goes by level, then score, then time"**. [OFFICIAL bundle]
- **There is no hard cap on attempts**, but there is a **per-file cooldown** after each submit (HTTP 429, "Cooldown Ns"). The server sets its length, which is unknown. [OFFICIAL bundle]
- **Wrong-answer penalty:** on Catcoder it was 1 minute per wrong solution. I found no penalty logic in the 2026 client. Unconfirmed.
- Every team member can submit, and multiple laptops are allowed. [OFFICIAL]

## 5. Style, input conventions, examples
- **Input format:** the first line is N (the number of cases), followed by N records separated by spaces. Grids appear as blocks of characters. The output is one line or block per case. The new client's case splitter assumes exactly this format. [OFFICIAL bundle + SECONDARY PDFs]
- **Sizes are small to medium:** from about 66 B up to about 350 KB per input. [SECONDARY]
- **Typical progression by level:** parsing and counting, then simulation, then validators, then grid and constructive placement, then pathfinding, then optimization. Later levels say things like "use your code from the previous level to validate".
- **Examples:**
  1. **Room Planner (Oct 2024, 7 levels)**, https://github.com/gergely-elias/ccc/tree/HEAD/room_planner
     - L1: max number of 1×3 desks in a room.
     - L2: print the grid of desk IDs.
     - L3: the room is no longer divisible by 3.
     - L4: desks may not touch, not even diagonally.
     - L5: 1×2 desks.
     - L6: desks of length 1–7.
  2. **Robotic Lawn Mower (Apr 2024, 7 levels)**, https://github.com/gergely-elias/ccc/tree/HEAD/lawn_mower
     - L1: count the WASD moves.
     - L2: compute the bounding box.
     - L3: VALID/INVALID path validator.
     - L4: construct a Hamiltonian path around a tree.
     - Later levels are harder.
  3. **Rock Paper Scissors (Mar 2023, 7 levels)**, https://github.com/gergely-elias/ccc/tree/HEAD/rock_paper_scissors
     - L1: decide one fight.
     - L2: simulate tournament rounds.
     - L3–L4: build pairings so Scissors wins.
     - L5: new styles (Y, L).
     - L6–L7: wildcards.
  - **Spaceship (Nov 2025):** "Pilot a spaceship and dock with a station while avoiding collisions with asteroids". A C# solution is at https://github.com/angua/CCC41

## 6. Practice
- https://codingcontest.org/challenges offers two modes [OFFICIAL, 2026]:
  - **Challenge:** timed, 240 minutes, levels unlock in order.
  - **Exploration:** no timer and all levels open; good for downloading descriptions and trying the visualizer.
- Playing requires a login with the Participant role. [OFFICIAL]
- **Public game list:** `GET https://codingcontest.org/api/games` lists 9 games. Per-game data is at `GET /api/training/{slug}` (for example `ccc-2025.11-classic-spaceship`). [OFFICIAL]
- **No public bulk download**, but the zip and input endpoints can be scripted once you have a token.
- **Community tools (built for Catcoder, so probably broken now):**
  - Lingepumpe/ccc_solver_template
  - lcian/catcoder-cli
  - pan2013e/catcoder-vscode
  - rzlsoftware/RZL.CodingContestEnvironment
- **Problem archives:** gergely-elias/ccc and aarroyoc/catcoder.

## 7. How the 2025 Classic winners used AI
- **Winner:** KI_ist_unverdient, a 3-person team on-site in St. Pölten. They reached level 7 in about 3h42m. [OFFICIAL]
- **Second place:** ai_usage_is_no_fun, also from St. Pölten, level 7 in about 3h49m. [OFFICIAL]
- **I found no documented workflow** for either team.
- **Context:** in the April 2024 survey, AI-assisted coders were on average more than 10% slower. [OFFICIAL, 2024]

## Gaps / unresolved
- It's unconfirmed whether any time penalty for wrong answers applies on the 2026 platform. The length of the cooldown is also unknown.
- The exact file names inside the 2026 zip and the format of the statement (PDF or HTML) are unknown. Logging into an Exploration game would settle both.
- Automating submissions needs the game token from the browser. It hasn't been tested from a script.
- The 2025 level count conflicts: 6 (blog), 8 (API), 7 (winner).
- It's unknown whether the Nov 2025 contest ran on Catcoder or on the new platform. The games were added to the new platform on 2026-09-15.
