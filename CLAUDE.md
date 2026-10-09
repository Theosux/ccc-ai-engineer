# CCC AI-Engineer — Project Instructions

## Ritual (MANDATORY)
If the user's message begins with **"We are working on ccc check claude.md for context"**,
invoke the `ccc-context` skill (`.claude/skills/ccc-context/SKILL.md`) BEFORE doing anything else,
and follow it exactly. It reloads all project knowledge after a `/clear`.

## Project summary
- **Goal:** win the **Cloudflight Coding Contest (CCC) #classic on 23 Oct 2026** by AI-engineering
  a fast, automated Claude Code workflow (AI/LLMs are allowed in the contest).
- **Owner:** Teo (GitHub: Theosux). Repo: `Theosux/ccc-ai-engineer` (private until after the contest).
- **Approach:** structured knowledge base in `docs/`, custom skills in `.claude/skills/`, training on
  past games in `arena/runs/`, then a battle-tested contest-day pipeline.
- **Budget:** Teo's Claude Code usage limit — prefer efficient workflows over brute-force agent spam.

## Where things live
- `docs/00-INDEX.md` — map of every doc. Start here.
- `docs/contest/` — verified facts about how the contest works (rules, format, scoring, platform, AI policy).
- `docs/research/` — raw research reports + verification report (sources).
- `docs/strategy/` — our contest-day workflow / AI pipeline (built in later sessions).
- `docs/progress-log.md` — dated session log. Append an entry at the end of every session.
- `arena/` — working folder for training + contest: `ccc.py` CLI (login/fetch/run/submit), `runs/<run>/levelN/`. See `arena/README.md`.
- `.claude/skills/` — custom project skills.

## Rules
1. **Commit + push after every update.** One commit per logical change, then `git push` immediately.
   **Never add a `Co-Authored-By: Claude` trailer or any Claude attribution to commits/PRs.**
2. Keep `README.md` and the GitHub repo description **empty** until the contest is over.
3. New knowledge goes into the right `docs/` file and gets a line in `docs/00-INDEX.md`.
4. New custom skills go in `.claude/skills/<name>/SKILL.md` and get listed in `docs/00-INDEX.md`.
5. Facts in `docs/contest/` must have a source URL; unverified items go under "Open questions".
