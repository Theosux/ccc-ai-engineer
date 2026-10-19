# Index

## Contest facts (`docs/contest/`)
| File | Purpose |
|---|---|
| [overview.md](contest/overview.md) | What CCC Classic is: date/time, duration, location, team size, eligibility, registration |
| [format-and-levels.md](contest/format-and-levels.md) | Level progression, inputs/outputs, submission + validation flow |
| [scoring-and-ranking.md](contest/scoring-and-ranking.md) | Points, time/wrong-answer penalties, tie-breaks, prizes |
| [rules-and-ai-policy.md](contest/rules-and-ai-policy.md) | What's allowed (AI, internet, languages) and forbidden |
| [platform.md](contest/platform.md) | Catcoder platform mechanics, practice problems, tooling |

## Research (`docs/research/`)
| File | Purpose |
|---|---|
| [agent-1-rules-format.md](research/agent-1-rules-format.md) | Raw report: rules, format, scoring |
| [agent-2-platform-mechanics.md](research/agent-2-platform-mechanics.md) | Raw report: platform + problem mechanics, winning team's AI method |
| [verification-report.md](research/verification-report.md) | Cross-check of all key claims (✅/⚠️/❌) |

## Strategy (`docs/strategy/`)
| File | Purpose |
|---|---|
| [README.md](strategy/README.md) | Contest-day workflow + training status |
| [contest-day-runbook.md](strategy/contest-day-runbook.md) | **Contest day**: timeline, golive detectors, fallback ladder |
| [workflow-speed.md](strategy/workflow-speed.md) | Loop timings + optimizations |

## Problem-solving knowledge (`docs/knowledge/`)
| File | Purpose |
|---|---|
| [ccc-patterns.md](knowledge/ccc-patterns.md) | "Level says X → technique Y → arena/lib function Z" + pitfalls |
| [solving-playbook.md](knowledge/solving-playbook.md) | Step-by-step procedure per level under time pressure; slow-solver recipe |
| [past-games.md](knowledge/past-games.md) | Level-by-level progressions + techniques of past CCC games |
| [resources.md](knowledge/resources.md) | External references + locally available libraries |

## Custom skills (`.claude/skills/`)
| Skill | Purpose |
|---|---|
| `ccc-context` | The ritual: reloads all project context after /clear |
| `ccc-solve` | Fast loop per level: fetch → statement → solve.py → go (training + contest) |
| `ccc-patterns` | How to solve a level: technique cheat sheet + `arena/lib` API (with ccc-solve) |

## Other
- [progress-log.md](progress-log.md) — dated session log
- `arena/golive.py` — contest go-live automation (preflight, detectors D1–D6, trigger). Tests: `python arena/tests/test_golive.py`
- `arena/lib/` — Python helper library for solvers (parse, grid, paths/Hamiltonian, search, sim, opt, geom, check). Tests: `python arena/lib/tests/test_lib.py`
- [arena/README.md](../arena/README.md) — working folder: CLI usage, folder layout (zips, inputs, outputs, solvers)
