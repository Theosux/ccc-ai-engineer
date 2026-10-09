# Format and levels

## Structure
- **Story:** one game (one story) told across **about 7–8 levels**. The 2025 game, Spaceship, had 8 levels; the winners completed 7 and nobody finished all 8. Earlier games had 7. Source: https://codingcontest.org/api/games
- **Unlocking:** level N+1 opens only after **every scored input file of level N passes**. In the game client: `isLevelAccessible = isUntimed() || e <= maxAccessibleLevel`.
- **Difficulty:** rises each level, and later levels reuse earlier code. Official PDFs say things like "use your code from the previous level to validate your solution".

## Per level you get
- **One zip:** `level-N.zip` from `GET /api/contestant/level/{N}/files`, containing the problem statement and input files.
- **Example file:** an **unscored** example (UI id `0-example`), including its expected output.
- **Visualizer:** some levels include an optional sandbox or visualizer (`/api/contestant/level/{N}/sandbox`).
- **Legacy naming (≤2025):** `levelN_1.in … levelN_5.in` plus `levelN_example.in/.out`, with a PDF statement. ⚠️ The 2026 naming is unverified.

## What you submit
- **Output files only:** one output file per input file. Source upload no longer exists in the new client.
- **Upload:** drag the files into the "Solutions Module" (batch upload or level tabs). The API endpoint is `POST /api/contestant/submit-{level}-{fileId}`.
- **Matching by filename:** the **last number in the filename picks the case** (e.g. `out_level_1_0-example.txt` → `0-example`). Non-standard extensions only trigger a warning. Oversized files get HTTP 413.

## Validation
- **Instant, per file:** each file gets a verdict of Correct, Wrong Solution, Parsing Error or Not Given.
- **Passed files stay passed.** The level is done when every scored file passes.
- **Cooldown:** after each submission, that file has a **per-file cooldown** (HTTP 429). The length is unknown ⚠️.
- **Optimization levels:** these can exist. To unlock the next level you must reach a score threshold ("≥ X on every file").

## Typical problem style (from past games)
The usual progression goes from parsing and counting, to simulation, to a validator (VALID/INVALID), to grid or constructive placement, then pathfinding, then optimization. Inputs are small to medium (66 B to about 350 KB). The usual format is a first line with N, then the records.
- **Room Planner (2024.10):** fit desks in a room. L1 counts desks, L2 prints a grid of IDs, L3 drops the divisibility rule, L4 adds no touching, L5 uses 1×2 desks, L6 uses lengths 1–7.
- **Lawn Mower (2024.04):** L1 counts WASD moves, L2 computes a bounding box, L3 validates a path, L4 constructs a Hamiltonian path around a tree.
- **Rock Paper Scissors (2023.03):** L1 decides one fight, L2 simulates rounds, L3–4 build rigged pairings, L5 adds new styles, L6–7 add wildcards.
- **Archive:** level PDFs and inputs are at https://github.com/gergely-elias/ccc

## Resolved (hands-on, 2026-10-09)
- **Zip contents:** `level-N.pdf`, the inputs `in_level-N_{0-example,1-small,2-small,3-medium,4-medium,5-large}.txt`, and the expected example output `out_level-N_0-example.txt`.
- **Cooldown:** about 5 s per file.
- **Feedback:** per case, with line ranges and a message. See [platform.md](platform.md).
