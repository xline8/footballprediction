# Phase 2 — Preprocessing: IR Azadegan League

Builder: `league/IR-AzadeganLeague/data/build_data.py` (adapted from
`league/NL-TweedeDivisie/data/build_data.py`, same FotMob matchDetails
format, same `jleague_lib` helpers). It regenerates
`league/IR-AzadeganLeague/data/ir_azadegan_matches.csv` (one row per
played match) and `team_matches.csv` (two rows per match, team-long).
The CSVs are gitignored by repo norm; the builder is committed so
the CSVs are reproducible. The builder reads the warehouse index
from the worktree when present and falls back to the absolute main-
checkout path (the 24 GB warehouse is gitignored and lives only in
the main checkout), exactly as the NL-TweedeDivisie builder does.

## Inclusion rules

- League rows: index `league_id = 9372` AND payload
  `general.leagueName = "Azadegan League"` (0 rows excluded on name).
- Played matches only: `header.status.finished` must be True. This
  excludes exactly 2 index rows — 3743953 (2021/2022) and 5098083
  (2025/2026) — both `started` False with a placeholder 0-0. A
  0-0 that was never played is not a draw and must not enter levels,
  traits, or any fit. Played n = 1,562 (asserted in the builder).
- No other exclusions: no score is missing or unparseable among
  played matches; no duplicate match ids; the maximum fixture-pair
  duplication is 2 (the home/away legs of the double round-robin),
  as expected.
- Season labels are exactly as in the warehouse (`2021/2022`, …,
  `2026/2027`). No relabelling.

## Score extraction

`header.status.scoreStr`, falling back to `header.teams[].score`.
Cross-checked against the index `score` column: agreement on all
1,562 played matches. Target for the goals candidate is the FT
score as stored; there are no shootouts or extra-time scores in
this corpus.

## Split-source rules

- **HT goals**: from the goal-event feed only (`ht_from_events`,
  goals with `time <= 45`), and only where the feed reproduces the
  FT score per side. `ht_source` values in the CSV:
  - `events` (1,258): feed reproduces FT; HT from events.
  - `events-zero` (276): empty event feed on a 0-0; HT is (0, 0)
    by the same feed.
  - `events-incomplete` (3): feed disagrees with the FT score
    (3863817, 4159522, 4321829); HT is NaN — the feed cannot be
    trusted for the split even though the FT score stands.
  - `none` (25): empty event feed on a scored match; HT is NaN.
- **Period splits**: never fabricated. There are no stats periods
  in any payload, so no `fh_*`/`sh_*` stat column is ever populated
  (all NaN by construction).
- **Stats/xG/shotmap columns**: `content.stats` is null and the
  shotmap shot list is empty in every payload, so every `*_home` /
  `*_away` stat and xG column is NaN and every `sm_*` column is 0.
  This is a measured absence, not a fill: the columns exist in the
  schema so the CSV matches the program's shape, and their emptiness
  is what makes S/C/K/T not buildable.
- **Cards**: the only card source is the event feed
  (`cards_source = "events-red-only"`). Yellows are 0 in every row;
  reds count Red + YellowRed events per side. No stats-feed yellow
  column exists to cross-check against (both are NaN).
- **Referee**: the column is empty in every row (no referee text in
  any payload).
- **Team identity**: FotMob team id. Three ids renamed mid-corpus
  (see DATA_UNDERSTANDING.md); the id is stable across the rename
  and is the join key everywhere.

## Team-long table

`team_matches.csv` mirrors the NL-TweedeDivisie shape: one row per
team-match (3,124 rows), with `_against` columns for the opponent's
values of each counted quantity. It is the table the EDA trait
checks and the engine's naive baselines read.

## Reproducibility check

Re-running the builder reproduces the CSVs exactly (deterministic
sort by date then match id). Headline levels recomputed from the
built CSV match the independent payload-level EDA run to the third
decimal (e.g. pooled 1H share 0.4148 from the CSV vs 0.4147 from
payloads; GF split-half r 0.272 vs 0.271); the only differences are
the two excluded 0-0 placeholders, which carry no goals.
