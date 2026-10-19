# Training datasets

## 1. Offline past games (local judge): `arena/offline.py`
Sources are cloned into `arena/.data/` (gitignored, untrusted: reference scripts run with `python -I`):
- https://github.com/gergely-elias/ccc ("confirmed solutions"): statement PDFs, inputs with example in/out, and Python solutions.
- https://github.com/blu3r4y/ccc-linz-nov2021 and https://github.com/blu3r4y/ccc-linz-oct2023: PDFs, inputs, and the author's submitted outputs. These outputs are trusted only for levels the README marks as solved.

Reference outputs come from the archive outputs, matched by input content hash, or from running the confirmed solution, capped at 60 s per input. Judges for non-unique or optimization levels were written by a separate agent, so the trainee stays unspoiled. They live in `arena/.data/games/<game>/judges/levelN.py`, with a README per game.

| Game (offline name) | Contest | Levels | Reference outputs | Use |
|---|---|---|---|---|
| `pacman` | Classic ≈2022 | 7 | L1–L7 (script) | training (Opus inline) |
| `islands` | 38th Classic, Nov 2023 | 7 | L1–L5 (blu3r4y passed); L6–L7 judge only | training (Opus inline) |
| `smartgrid` | Classic 2020.10 | 7 | L1–L3 full; L4 2/6, L5 5/6; L6–L7 judge only | holdout for the model A/B |
| `interp2021` | 35th Classic, Nov 2021 | 4 | L1–L4 (blu3r4y archive) | holdout for the model A/B (speed drill) |
| `lawnmower-gh` | Classic 2024.04 | 4 | our own passed solvers | judge replay test only |

Not usable: gergely `matchmaking` and `addictive_game`, which have code only (no statements or inputs).

## 2. Platform practice games (real judge): `python arena/ccc.py games`
Classic: Spaceship, Room Planner, Lawn Mower, RPS (all solved, see `past-games.md`).
School, 5–6 levels, not yet played: `ccc-2025.11-school-asteroid-mining`, `ccc-2024.10-school-drones`, `ccc-2024.04-school-magic-money`, `ccc-2023.03-school-honeycomb`. AI track: `ccc-2025.11-ai-birds` (not Classic).
