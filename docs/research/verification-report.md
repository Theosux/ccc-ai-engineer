# Verification report: CCC #classic, 23 Oct 2026 (checked 2026-10-09)

## Method
The verification agent re-checked the claims with read-only GET requests against these sources:
- the live platform API;
- all 38 JS chunks of the codingcontest.org bundle;
- the Spaceship game client bundle, which needs `Referer`/`Origin: https://spaceship.codingcontest.org` and `Sec-Fetch-Site: same-origin` headers;
- Wayback snapshots from 2026-06-07 and 2026-07-12;
- the PDFs in the gergely-elias/ccc repository.

## Claims table
| # | Claim | Verdict | Source | Note |
|---|---|---|---|---|
| 1 | "42nd CLASSIC CCC" starts 2026-10-23T13:00:00Z | ✅ | https://codingcontest.org/api/contests/42nd-classic-ccc-5872 | Live data |
| 2 | Duration 240 min | ✅ | API + how-it-works bundle | |
| 3 | 13:00 UTC = 15:00–19:00 CEST | ✅ | zoneinfo | EU switches back on 25 Oct. Romania (EEST) is 16:00–20:00 |
| 4 | #school 8:00 UTC; #classic and #data/ai 13:00 UTC | ✅ | how-it-works bundle | |
| 5 | Cloudflight page says "15:00 #classic (CET)" | ✅ | https://www.cloudflight.io/en/event/42-cloudflight-coding-contest/ | "CET" means Vienna local time. The page links to the old register/Catcoder sites |
| 6 | Single slot; 3 contests in the edition | ✅ | https://codingcontest.org/api/editions/active | Classic is id 40 |
| 7 | Legacy page said 14:00 UTC (superseded) | ✅ | Wayback 2026-06-07 | The 2026-07-12 snapshot already shows 13:00 |
| 8 | Max team size 3 | ✅ | API `maxTeamSize: 3` | |
| 9 | Solo allowed, same leaderboard | ✅ | how-it-works; HoF API | 39 of the 2025 top 100 were solo |
| 10 | Every member can submit; team can be formed before the event | ✅ | how-it-works | |
| 11 | ONLINE venue exists | ✅ | contest API | |
| 12 | 32 Classic venues | ✅ | contest API | Includes 8 Romanian venues |
| 13 | Free | ✅ | codingcontest.org meta tag | |
| 14 | Registration open | ✅ | API | 1,238 entries, 1,662 people |
| 15 | Age 16+ (14+ in Austria); one account per person | ✅ | /terms/overview | |
| 16 | Venue-specific terms take precedence | ✅ | Terms | |
| 17 | No explicit AI/LLM rule exists | ✅ | bundle, game client, Terms, cloudflight.io | |
| 18 | Codeforces "and AI" headline shows AI is allowed in Classic | ❌ | https://codeforces.com/blog/entry/147433 | The headline refers to the Data/AI track |
| 19 | 2024 survey: 741 vs 299 AI users; AI users >10% slower | ✅ | cloudflight.io blog | Not a rule |
| 20 | 2026 LinkedIn "role of AI" video | ✅ exists / ⚠️ content | LinkedIn showcase | The video content couldn't be read; the post frames AI, it doesn't set a rule |
| 21 | Ranking: levels desc, then time asc | ✅ | HoF API contest 37 | |
| 22 | Optimization levels rank "by level, then score, then time" | ✅ | Spaceship client | |
| 23 | Legacy rules: wrong answer +1 min, source upload −2 min | ✅ (legacy) | Wayback 2026-06-07 and 2026-07-12 | |
| 24 | Penalty and bonus still apply in 2026 | ⚠️ | — | The new site doesn't mention them. There is no source-upload path anymore. A server-side penalty is possible |
| 25 | catcoder.codingcontest.org redirects with 302 | ✅ | curl | Paths redirect to the same path on codingcontest.org |
| 26 | Game runs in an iframe and gets a token from `POST /api/game-token` | ✅ | bundle + game client | The token arrives by postMessage `ccc:auth-token` |
| 27 | Levels unlock in order (except in Exploration) | ✅ | Spaceship client | |
| 28 | Per-level zip at `GET /api/contestant/level/{N}/files` | ✅ | Spaceship client | |
| 29 | Output-only submit via `POST /api/contestant/submit-{level}-{fileId}` | ✅ | Spaceship client | |
| 30 | Instant per-file verdicts; passed files stay passed | ✅ | Spaceship client | |
| 31 | The last number in the filename picks the case | ✅ | Spaceship client | |
| 32 | Only the listed extensions are accepted | ⚠️ | Spaceship client | Other extensions get a warning but are still submitted |
| 33 | Per-file cooldown (HTTP 429) | ✅ | Spaceship client | Length unknown |
| 34 | Example file is unscored | ✅ | Spaceship client | |
| 35 | Case splitter "first line N" is platform-wide | ⚠️ | Spaceship client | It is specific to the Spaceship game |
| 36 | Challenge (timed, 240 min) and Exploration modes | ✅ | bundle; /api/training | Participant role required |
| 37 | /api/games level counts: Spaceship 8, RP 7, LM 7, RPS 7 | ✅ | https://codingcontest.org/api/games | |
| 38 | Islands is a practice game | ❌ | /api/training | Returns "Game not found" |
| 39 | 6 vs 7 vs 8 levels | ✅ resolved | /api/games + HoF | 8 levels; winners completed 7; nobody finished all 8 |
| 40–42 | Room Planner, Lawn Mower and RPS level progressions | ✅ | gergely-elias/ccc PDFs | |
| 43 | Legacy file naming `levelN_1..5.in` + example in/out | ✅ | gergely-elias/ccc | The 2026 zip naming is unverified |
| 44 | 2025 winner KI_ist_unverdient: 7 levels in 3h42m | ✅ | HoF API | Venue was Raiffeisenbank St. Pölten |
| 45 | No write-up of the winners' AI workflow exists | ✅ (none found) | multiple searches | |
| 46 | Prizes are per venue | ✅ | Codeforces 147433 | |
| 47 | Contacts: team@codingcontest.org and Discord | ✅ | bundle | A second invite is also in the bundle: discord.gg/HekGjMrj7n |
| 48 | On-site: arrive 30–45 min early, bring a laptop | ✅ | how-it-works | |

## Corrections
1. **Islands is not available for practice.** Only 4 Classic games are: Spaceship, Room Planner, Lawn Mower and RPS.
2. **The Codeforces "and AI" headline is not evidence for Classic.** It refers to the Data/AI track.
3. **Level count: Spaceship has 8 levels.** The HoF `level` field means levels completed. The blog's "six levels" figure is wrong.
4. **Unlisted extensions are not rejected.** They trigger a warning.
5. **The case splitter is game-specific,** not a platform-wide input format.
6. **Catcoder paths redirect to the same path,** not to the root.
7. **Registration numbers:** 1,238 entries and 1,662 people.
8. **The 13:00 UTC start was set by 2026-07-12** at the latest.

## New findings
- **Reading the game client:** the bundle can be fetched read-only with same-origin headers. This is useful for studying the mechanics.
- **Auth handshake:** the platform posts `{type:'ccc:auth-token', token, contestSlug, contestStartMs, contestDurationMinutes}` to the iframe. Requests then carry `Authorization` and `X-CCC-SLUG`. Other endpoints: `/api/contestant/contestant-info`, `/api/contestant/level/{N}/input/{fileId}` and `/api/contestant/level/{N}/sandbox`.
- **Live scores:** served over SSE at `/api/contests/scores/stream?contestSlug=…`.
- **The 2025 contest ran on the legacy platform.** **23 Oct 2026 will be the first live contest on the new platform** (it went live around 2026-09-15).
- **Past Classic winners:**
  - 2024.10: 7 levels in about 148 min (solo, Online)
  - 2024.04: 7 levels in about 146 min (Craiova)
  - 2023.10: 7 levels in about 138 min
  - 2023.03: 7 levels in 64 min
  - 2025: 7 of 8 levels in 3h42m, so it was notably harder
- **Romanian venues are strong.** Craiova, Bucharest, Timișoara and Chișinău are often in the top 10.
- **2026 LinkedIn framing of AI:** "A magic wand is nothing without the magician… The same is true for AI."

## Still open (the user must resolve)
1. **AI/LLM policy:** email team@codingcontest.org or ask on Discord. Watch the LinkedIn video and read the venue email.
2. **Time penalty for wrong submissions** in 2026: ask the organizers, or test in Challenge mode.
3. **Per-file cooldown length:** test in Exploration mode.
4. **What the 2026 zip contains** (file names; PDF or HTML statement): download a level in Exploration mode.
5. **Scripted submission with a browser token:** untested; check the spirit of the Terms first.
6. **Venue:** ONLINE or a local one (prizes are per venue). Confirm registration and team setup.
7. **Start time:** re-check it and any hints in the email during contest week.
