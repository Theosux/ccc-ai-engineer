# DATA/AI repo bootstrap (for Dobrin + Iustin)

Teo competes in **CLASSIC**. Teammates **Dobrin** and **Iustin** compete in **42nd DATA/AI CCC**
(`42nd-data-ai-ccc-5873`, Fri 23 Oct 2026 13:00 UTC, 240 min, max team 3). This side project gives them a
separate private repo with our tooling, workflow and Data/AI research. After the bootstrap only they work on it.

- **Repo:** `Theosux/ccc-ai-engineer-data-ai` (private; README + description empty). Teo sends the invites.
- **Local clone:** `C:\Personal\Business\mvp\AiEngineer - ccc-data-ai`
- **Desktop prompt (deliverable):** `C:\Users\Teo\Desktop\ccc-data-ai-prompt.txt` (line 1 = `signature: `)
- **Practice game:** `ccc-2025.11-ai-birds` "Migratory Birds" (6 levels, ML). Our solvers go to
  `arena/runs/SPOILER-birds/` in the new repo.
- **Trigger after /clear:** "we are working on ccc data/ai it-N; check claude.md for context" → read this file,
  then continue iteration N from the first ☐ step. Update the boxes and push after every step.

## it-1: repo + research + tooling
- ☐ 1. This doc, CLAUDE.md ritual, memory (main repo)
- ☐ 2. Create repo, clone, skeleton (CLAUDE.md, INDEX, docs/team/, ccc-ai-context skill, .gitignore), push
- ☐ 3. Research agents A (contest facts) + B (problem side) → new repo `docs/research/`
- ☐ 4. Port tooling (ccc.py, golive.py, lib) to the AI slug; install sklearn/lightgbm/xgboost; `lib/ml.py`; smoke-test Birds `train` + `fetch 1`
- ☐ 5. Verification agent → `docs/research/verification-report.md`

## it-2: hands-on Migratory Birds
- ☐ 1. Fetch L1–L6 (exploration), solve level by level with the CLI loop, time each level
- ☐ 2. Write `knowledge/past-games.md`, `data-ai-patterns.md`, `ml-playbook.md`; generalize helpers into `lib/ml.py`
- ☐ 3. Fix tool gaps the Data/AI format exposes

## it-3: strategy, skills, prompt, handover
- ☐ 1. Merge verified research into `docs/contest/`
- ☐ 2. `strategy/workflow.md`, `contest-day-runbook.md`, `training-plan.md`
- ☐ 3. Skills `ccc-ai-solve`, `ccc-ai-patterns`; INDEX complete; signed progress-log entry
- ☐ 4. Desktop prompt file
- ☐ 5. Final consistency pass (fresh clone, link check), push both repos

## Notes
(agent outputs, decisions, next step go here)
