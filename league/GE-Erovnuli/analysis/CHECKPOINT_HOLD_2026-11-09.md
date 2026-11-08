# GE-Erovnuli — HOLD checkpoint (2026-11-09 18:30 WIB)

Builder paused by user escalation 18:30 WIB (all focus to Bulgaria
Second Professional League). This file records the exact state at
the hold so the resume starts from verified facts, not memory.
Branch: `build/ge-erovnuli` @ worktree `~/workspace/wt-ge-erovnuli`.
Base: `local/fotmob-source` @ 2e71b52. No fitting has been run.
No prereg exists yet. PROGRAM_STATUS.md untouched (coordinator-only).

## Step in progress at the hold: Step 1 — DATA UNDERSTANDING (exploration only)

Verified so far (from `data_enrichment/fotmob_world_index.csv`,
league_id = 439, and direct JSON inspection):

- n = 1,059 matches. Seasons (calendar-year): 2021 = 180,
  2022 = 180, 2023 = 180, 2024 = 180, 2025 = 180, 2026 = 159.
- Index coverage flags: has_stats 0/1,059, has_shotmap 0/1,059,
  has_period_splits 0/1,059 — GOALS-ONLY league (task brief).
- 2025 is the last COMPLETE season (2025-02-28 to 2025-12-06,
  n = 180) — the virgin candidate per the task brief's IN-ISL-style
  split discipline (state n = 180 on resume; wide SEs expected).
- 2026 is IN PROGRESS: 159 played, 2026-02-28 to 2026-11-08
  (index pull date), 10 teams. Tonight's 23:00 WIB kickoff sits in
  this season. 2026 is NOT a virgin candidate (incomplete).
- 18 distinct team names across all seasons; 10 teams per recent
  season (180 = 10 teams x 36 rounds, quadruple round-robin shape).
  Championship/relegation split in recent seasons still to be
  phase-checked and frozen in the prereg on resume (task brief).
- Warehouse location quirk: the per-match JSONs are NOT in this
  worktree (gitignored warehouse). Index `path` values resolve
  against the MAIN checkout `~/workspace/footballprediction/`
  (e.g. `data_enrichment/fotmob_world/Georgia/Erovnuli Liga/2021/
  3523727.json` exists there, not in the worktree). The data
  builder on resume must read from the main checkout (or the
  coordinator's convention for other conveyor builders).
- Sample JSONs inspected (2021 id 3523727; 2024 mid-season file;
  2026 mid-season file): `content.stats` is null, `content.shotmap`
  present but `shots` is empty (0 shots), `content.lineup` null,
  referee `infoBox.Referee.text` is empty string, and
  `matchFacts.events` contains ONLY `Goal` and `Half` event types
  (4-7 events per sampled match) — i.e. no card events either, so
  S/C/K/T are not buildable from ANY source in the payload, not
  just from the stats feed. Score is in
  `header.status.scoreStr` / `header.teams[].score` as usual.
  Full-coverage audit over all 1,059 files still to run on resume
  (the 3 samples agree with the index flags, but Step 1 must
  confirm across the corpus, per season).

## What remains (in template order, nothing started)

1. Step 1: full DATA_UNDERSTANDING.md (corpus-wide coverage audit,
   format/split history, phase rule).
2. Step 2: PREPROCESSING.md + `data/build_data.py` + analysis CSV.
3. Step 3: EDA.md (goals levels, home advantage, trait reliability
   for goals only; halves question is moot — no period splits, so
   goals halves constants cannot be measured from splits; design
   must state FT-only or the frozen-constant treatment honestly).
4. Step 4: charts/ + make_charts.py.
5. Step 5: FEATURES.md (J1 X1-X9 template: X1 goals-only ADOPTED
   in reduced form; X3-X9 expected DROPPED for absent data, each
   with the coverage number; SHRINK arm eligibility per the
   template's G-J2 lesson to be decided in design, pre-fitting).
6. Step 6: MODEL_DESIGN.md — feasibility matrix GOALS-ONLY
   (G candidate; S/C/K/T documented not-buildable).
7. Prereg (own commit, BEFORE any fitting), engine, dev
   walk-forward, virgin read ONCE (2025) if dev gate passes,
   verdict, predictions on PASS.

## Commits on this branch at the hold

- (this checkpoint commit only, on top of base 2e71b52)
