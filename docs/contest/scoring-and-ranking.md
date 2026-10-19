# Scoring and ranking

- **Ranking rule:** "The candidate (or team) reaching the highest level within the shortest time wins." https://codingcontest.org/info/how-it-works
- **Ranking order:** **levels completed (descending), then time (ascending)**. Confirmed on the 2025 leaderboard: https://codingcontest.org/api/hall-of-fame/contests/37/leaderboard
- **Optimization levels:** these rank **by level, then score, then time**. Reaching the next level beats any extra points (from the game client tooltip).
- **Partial credit:** none within a level. A level counts only when all of its scored files pass.

## Penalties and bonuses
- **Legacy rules (until 2025):** a wrong solution cost **+1 penalty minute**, and uploading source code earned **−2 bonus minutes**. Source: Wayback snapshot of the old how-it-works page.
- **2026 ⚠️:** the new site doesn't mention either rule, and the new client **cannot upload source**, so the bonus is gone. A server-side penalty for wrong answers cannot be ruled out, so **treat wrong submissions as costly** and validate against the example first.

## Benchmarks (winning pace)
| Contest | Winner result |
|---|---|
| 2025 (Spaceship, 8 levels) | 7 levels in **3h42m**; 2nd place 7 levels in 3h49m; 3rd place only 6 levels |
| 2024.10 (Room Planner) | 7 levels in about 148 min (solo, Online) |
| 2024.04 (Lawn Mower) | 7 levels in about 146 min (Craiova) |
| 2023.10 (Islands) | 7 levels in about 138 min |
| 2023.03 (RPS) | 7 levels in 64 min |

Romanian venues (Craiova, Bucharest, Timișoara, Chișinău) often place in the top 10.

## Prizes
Prizes are **per venue**, plus the global Hall of Fame and certificates. There is no global cash prize.

## Hands-on finding (2026-10-19, Spaceship Challenge mode)
- **Test:** a deliberately wrong submit on L1, followed by a correct one.
- **Result:** `passedAt` was exactly the wall-clock time of the correct submit (12:20:29 UTC, 58.8 s after the start). **No +60 s was added.** `gameScore.timeMs` equals the last level's `passedAt`.
- **Caveat:** a leaderboard-side penalty in the real contest cannot be ruled out, so keep using `check()`.

## Open questions
- Does a time penalty for wrong submissions still exist in 2026? Ask the organizers, or test it in Challenge mode.
- Tie-breaks beyond time are not documented.
