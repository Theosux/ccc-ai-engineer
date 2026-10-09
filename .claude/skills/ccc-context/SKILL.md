---
name: ccc-context
description: Reload full CCC project context (contest facts, strategy, custom skills, progress, git state). Use when the user's message starts with "We are working on ccc check claude.md for context", or whenever context about the CCC contest project is missing (e.g. after /clear).
---

# CCC Context Ritual

Run these steps in order before answering anything else. Read in parallel where possible.

1. Read `docs/00-INDEX.md`.
2. Read every file in `docs/contest/`.
3. Read every file in `docs/strategy/`.
4. Read the last 3 entries of `docs/progress-log.md`.
5. List `.claude/skills/*/SKILL.md` and read the frontmatter (name + description) of each custom skill,
   so you know which project skills exist and when to use them.
6. Skim `arena/runs/` (directory listing only: runs and levels with a `solve.py`) to know what was trained.
7. Run `git status --short` and `git log --oneline -5`.

Do NOT read `docs/research/` unless a question needs the raw sources.

## Then reply with a short "Context loaded" summary (max ~6 lines):
- Days left until the contest (23 Oct 2026) from today's date.
- What exists so far (docs, skills, training problems solved).
- Last session's outcome and the planned next step (from the progress log).
- Any uncommitted changes.

Then continue with the user's actual request.

## Standing rules (also in CLAUDE.md)
- Commit and push after every update.
- Append a dated entry to `docs/progress-log.md` at the end of each session.
- Keep README.md and the repo description empty until after the contest.
