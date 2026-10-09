# Agent 1: Rules, format and scoring (raw report, 2026-10-09)

**Tags:** [OFFICIAL] means codingcontest.org (including its public JSON API), cloudflight.io, or the official "CodingContest" accounts. [SECONDARY] means third-party sources.

**Tip:** codingcontest.org is a JavaScript app, so plain page fetches come back empty. The public JSON API works:
- https://codingcontest.org/api/editions/active
- https://codingcontest.org/api/contests/42nd-classic-ccc-5872
- https://codingcontest.org/api/hall-of-fame/contests/37/leaderboard (41st Classic, 2025)
- https://codingcontest.org/api/contests?page=0&size=50

## 1. Date, start time, timezone, duration
- **Contest:** "42nd CLASSIC CCC", slug `42nd-classic-ccc-5872`, `startTime: 2026-10-23T13:00:00Z`, `durationMinutes: 240`. https://codingcontest.org/api/contests/42nd-classic-ccc-5872 [OFFICIAL, 2026]
- **Local time:** 13:00 UTC is **15:00–19:00 in Vienna/Berlin**. Central Europe is still on summer time (CEST) on 23 Oct; the clocks change on 25 Oct.
- **How it works page:** "#school — 8:00 UTC … #classic — 13:00 UTC … #data/ai — 13:00 UTC". https://codingcontest.org/info/how-it-works [OFFICIAL, 2026]
- **Cloudflight event page:** "15:00 #classic (CET)". The times match the API; the "CET" label really means CEST. https://www.cloudflight.io/en/event/42-cloudflight-coding-contest/ [OFFICIAL]
- **Duration:** 4 hours. [OFFICIAL]
- **One time slot only.** The edition has 3 contests: School, Classic and Data/AI. https://codingcontest.org/api/editions/active [OFFICIAL]
- **Conflict:** an old Wayback snapshot (2026-06-07) of register.codingcontest.org said 14:00 UTC. It has been superseded by the current API and site, which say 13:00 UTC.

## 2. Online vs on-site
- **Hybrid:** "40+ locations". [OFFICIAL]
- **Venues:** 32 venues are listed for Classic. One is called "ONLINE"; the rest are in AT, DE, RO, ES, PT, PL, CZ, MD and IN, including POLITEHNICA Bucharest, West Univ. Timisoara, Univ. of Craiova and AI Cuza Univ. [OFFICIAL API]
- **Remote participation:** register on codingcontest.org and choose the ONLINE venue. [OFFICIAL]
- **Where games run:** they open only from inside a logged-in CCC platform account. Old game subdomains say "This game can only be accessed through the CCC platform". [OFFICIAL, observed]
- **Discord:** optional. [OFFICIAL]

## 3. Teams, eligibility, categories
- **Classic team size:** up to 3 participants (API `maxTeamSize: 3`). Solo entries are allowed and share the same leaderboard (`isSolo` flag). [OFFICIAL]
- **Team setup:** "Every team member can submit solutions during the contest." A team can be created during registration or at any time before the event. [OFFICIAL]
- **Tracks:** #School is for pupils (2 h). #Classic is for "students and professionals" (4 h). #Data/AI is 4 h. Classic has no sub-divisions. https://www.cloudflight.io/en/the-cloudflight-coding-contest/ [OFFICIAL]
- **Age and accounts:** minimum age 16 (14 in Austria). One account per person. https://codingcontest.org/terms/overview [OFFICIAL]
- **Entry fee:** free. [OFFICIAL social]

## 4. Registration
- **How:** create an account on codingcontest.org, register for "42nd CLASSIC CCC", and pick a venue. [OFFICIAL]
- **Status:** `OPEN_REGISTRATION` since 2026-04-22, with about 1,236 registered. [OFFICIAL API]
- **New platform:** rebuilt from scratch, with practice, registration and history in one account. [OFFICIAL social, 2026]
- **Deadline:** none published; registration appears to stay open until the event. [SECONDARY/inferred]

## 5. Languages and tools
- "All programming languages permitted"; "Challenges described in English". [OFFICIAL]
- You solve locally and upload results ("Upload your solution(s) to CatCoder for each level" in the legacy rules). There is no language-specific online judge. [OFFICIAL, legacy]

## 6. AI/LLM policy
- **No explicit AI rule appears in any official text.** The only rules on the How it works page are:
  - "On-site participants are not allowed to perform excessive downloads or stream content during the contest."
  - "Teams may use multiple laptops, and every team member can submit solutions on behalf of the team."

  [OFFICIAL, 2026]
- **Evidence that AI is tolerated or allowed:**
  - Cloudflight's own survey of the 04/2024 contest: 741 participants said they considered using AI assistance and 299 said they did not. AI users were "slower by more than 10% on average". https://www.cloudflight.io/en/blog/ai-assisted-software-development-strengths-and-negative-usecases/ [OFFICIAL, 2024]
  - Codeforces announcement for the 41st contest: "for all programming languages and AI". https://codeforces.com/blog/entry/147433 [OFFICIAL account, 2025]
  - LinkedIn, 2026: a video titled "what role AI will play at this year's Cloudflight Coding Contest". The video itself could not be read. [OFFICIAL social]
  - A 2024 participant blog mentions "AI tools that were allowed during the competition". https://nikity.is-a.dev/blog/blog-1.html [SECONDARY]
  - The top two teams in the 2025 Classic were named "KI_ist_unverdient" and "ai_usage_is_no_fun". [OFFICIAL data, interpretation]
- **Caveat:** venue-specific rules may be emailed before the event and take precedence over the general terms. [OFFICIAL Terms]

## 7. Scoring and ranking
- "The candidate (or team) reaching the highest level within the shortest time wins." [OFFICIAL, 2026]
- **Leaderboard ordering:** levels completed (descending), then time (ascending). Top three in the 41st Classic (2025):

  | Rank | Level | timeMs | ≈ minutes |
  |---|---|---|---|
  | 1 | 7 | 13,330,445 | 222 |
  | 2 | 7 | 13,722,264 | 229 |
  | 3 | 6 | 5,438,992 | 91 |

  [OFFICIAL API]
- **Legacy rules (archived 2026-06):**
  - "Wrong solution = 1 penalty minute"
  - "Submission of source code after level completion = 2 bonus minutes"

  The new site doesn't restate them. https://web.archive.org/web/20260607225013/https://register.codingcontest.org/info/how-it-works [OFFICIAL, legacy]
- **Number of levels:** the 2025 winners reached level 7, but a recap blog says "six difficulty levels per track". [conflict]
- **Tie-breaks:** nothing stated beyond time.

## 8. Prizes and leaderboards
- **Prizes are per venue:** "competing with the local community for it". https://codeforces.com/blog/entry/147433 [OFFICIAL account, 2025]
- **Global Hall of Fame:** filterable by venue and country, with participation and winner certificates. https://codingcontest.org/hall-of-fame [OFFICIAL]
- **No global cash prize.** [SECONDARY]

## 9. Before the day
- **Practice:** past Classic games are available on https://codingcontest.org/challenges: Spaceship (2025), Room Planner (2024), Robotic Lawn Mower (2024), Islands (2023), Rock Paper Scissors (2023). [OFFICIAL]
- **Topic:** kept secret until the event. [OFFICIAL]
- **On-site:** bring a laptop and charger, arrive 30–45 minutes early, and check your email for local details. [OFFICIAL]
- **Contact:** team@codingcontest.org; Discord https://discord.gg/eJKvPJW7au [OFFICIAL]

## Gaps / unresolved
1. No explicit AI rule exists; allowance is inferred.
2. No rule found on internet access or outside communication (beyond the on-site downloads/streaming line).
3. The penalty and bonus minutes come only from the legacy page, so it's unknown whether they still apply.
4. The number of levels (6 vs 7) and the input format are unknown.
5. No registration deadline is published.
6. Start time: re-check the platform countdown or pre-contest email that week.
7. Venue-specific rules may be emailed and could override the general terms.
8. The submission UI on the rebuilt platform could not be inspected without logging in.
