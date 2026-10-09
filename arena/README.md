# Arena: the working folder for training and contest day

All commands are run from the repo root: `python arena/ccc.py <cmd>`.

## Layout: what is where
```
arena/
├── ccc.py                 # the CLI: login / train / contest / fetch / run / submit / go / info / api
├── README.md              # this file
├── .auth/                 # GITIGNORED: Edge login profile, cookies.json, state.json (active run + game token)
└── runs/
    └── <run>/             # one folder per game or contest (e.g. spaceship, desks, contest)
        ├── contest.json           # platform contest metadata (slug, gameBaseUrl, ...)
        ├── contestant-info.json   # latest level/score state from the game API
        └── level<N>/
            ├── level-<N>.zip      # the raw download, as given by the platform
            ├── files/             # unzipped zip: statement + inputs + example (in/out)
            ├── map.json           # input file -> platform fileId; which files are unscored
            ├── sandbox.html       # optional visualizer, when the level has one
            ├── solve.py           # THE solver: reads stdin, writes stdout
            ├── out/<stem>.out     # generated outputs, one per input
            └── submissions.jsonl  # log of each submit and its verdicts
```

## Loop per level (the fast path)
1. `python arena/ccc.py fetch N` downloads and unzips level N, writes `map.json`, and creates a `solve.py` stub.
2. Read the statement in `files/` and write `levelN/solve.py`. It reads stdin and prints the answer, so you can reuse code from level N-1.
3. `python arena/ccc.py go N` runs the solver on every input and checks the example against its expected output. **It only submits if the example matches.** Then it prints the verdicts and the level status.
4. When the level passes, the next level unlocks: `fetch N+1`.

Useful extras:
- `run N`: generate outputs only.
- `submit N --only 3`: submit a single file.
- `info`: show status. `info --raw`: dump the raw JSON.

## Setup
- **Practice:** run `python arena/ccc.py train <gameSlug> --mode exploration` (no timer, all levels open). Use `--mode challenge` for a timed 4 h rehearsal where levels unlock one by one.
- **Contest day:** run `python arena/ccc.py contest 42nd-classic-ccc-5872`. Do this once the contest has started and its game is assigned.
- **List practice games:** `python arena/ccc.py games`.
- **Switch between runs:** `python arena/ccc.py use <run>`.

## Auth
- `login` opens Edge with a dedicated profile. You log in once, and the cookies are saved to `.auth/`.
- The game token is fetched automatically and refreshed on a 401/403.
- If the commands report "not logged in", run `login` again.
