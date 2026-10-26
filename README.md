# [Cloudflight Coding Contest Classic 2026](https://codingcontest.org)

| Ranking | Place |
|---|---|
| Local (CREIC Cluj) | **3rd** |
| Country (Romania) | **3rd** |
| World | **9th** |

This repo is our setup for the 42nd Cloudflight Coding Contest (CCC) Classic, held on 23 October 2026. We competed as team **Krateo**.

AI tools were allowed, so we went all in. Instead of only practising algorithms, we spent two weeks building a Claude Code workflow that does the boring parts for us: downloading a level, reading the statement, running the solver, checking the output and submitting it. On contest day our job was mostly to think about the problem and make good decisions.

## The contest

The game was **Nanofabricator**: a machine that builds matter on a hexagonal board using laser beams. There were 6 levels. Each one added a rule: draw the board, simulate the lasers, two beams create matter and three destroy it, then a pick-up arm that removes finished patterns. Level 6 was an optimization level: write the shortest programs that build a list of patterns. Fewer lines meant a better score.

## What the AI workflow achieved

- Our script noticed the contest had started 12 seconds after it went live. It registered us and printed level 1 automatically.
- Levels 1 to 5 were done in about 9 minutes.
- On level 6 we took our score from a first answer of 123,551 lines down to **14,528 lines**, every file checked as correct by the server.
- Before the contest, a full replay of the 2025 game (Spaceship, 8 levels) went from 36.6 minutes to **13.9 minutes**. That year's winners solved 7 of the 8 levels in 3h42m.

## How we worked in iterations

We worked in short sessions and wrote down what we learned after each one in `docs/progress-log.md`. Every session started from the previous notes, so nothing got lost when Claude's context was cleared.

1. **Research.** Agents collected the contest rules, scoring and platform details. A separate agent checked their claims against the sources.
2. **Tooling.** The 2026 platform was new, so the old community tools did not work. We read the site's JavaScript and built our own command line client for it.
3. **Training.** We solved past games one after another (Lawn Mower, Desks, Rock Paper Scissors, Spaceship, Islands, Pacman and more), some of them on a timer.
4. **Fixing what was slow.** After every timed run we looked at where the minutes went. In the first Spaceship run, 20 of the 29 minutes on one level were spent waiting for a solver that was too slow. So we added a `probe` command that tests a few big inputs first and predicts how long the full run will take.
5. **Rules from mistakes.** Every wrong answer became a rule in the skills, for example "always read the rule images before the first submit" and "never strip blank lines from the output".

We also compared Claude Opus and Sonnet on the same unseen games. Both were equally fast with zero wrong answers, but Opus followed the process better, so Opus drove on contest day.

## How we worked as a team

- One person drove the contest and was the only one allowed to submit. The platform loses answers if two people submit at the same time, which we found out in training.
- On level 6, Claude acted as a coordinator and ran three helper agents in parallel: one ran long searches, one looked for a formula behind the top scores, and one reviewed ideas and tried new solvers. Each helper wrote candidate answers into its own folder.
- A small merge script checked every candidate with our own simulator, kept the shortest correct program for each pattern, and only then submitted. The server keeps the latest submission, not the best one, so this step mattered.
- Teammates worked on their own git branches, and nothing from them was merged until it passed the same check.

## The technical side

- **`arena/ccc.py`**: our client for the contest platform. Commands like `fetch`, `go`, `probe` and `submit`. `go N` runs the solver on all inputs in parallel, checks the example, submits smallest file first and opens the next level.
- **`arena/golive.py`**: watches the contest start in several ways at once (API polling, a live event stream, registrations, trying to download level 1) and fires as soon as one of them sees it.
- **`arena/lib/`**: a helper library built from past games: input parsing, grids, BFS/Dijkstra/A*, Hamiltonian paths and cycles, simulation with cycle skipping, rectangle packing, tournament brackets, plus wrappers for OR-Tools (CP-SAT and max flow).
- **`arena/offline.py`**: replays past games locally with our own judge, so we could train on games the platform did not offer.
- **Level 6 solvers**: an exact simulator, a row-by-row sweep, and a beam search over all 4096 possible actions per tick using bitmasks. They ran on PyPy and used all 16 CPU cores.
- **Claude Code setup**: custom skills in `.claude/skills/` (`ccc-solve` for the per-level loop, `ccc-patterns` for which technique to use, `ccc-context` to reload the project), two solver agents in `.claude/agents/`, and a knowledge base in `docs/`.

## Repo layout

```
docs/            contest facts, strategy, knowledge base, progress log
arena/           ccc.py, golive.py, offline.py, lib/, tests/
arena/runs/      every training run and the contest run, one folder per level
.claude/         custom skills and agents
```
