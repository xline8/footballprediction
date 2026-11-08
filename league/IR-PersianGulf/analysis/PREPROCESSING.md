# Phase 2 — Preprocessing: IR Persian Gulf Pro League

Builder: `league/IR-PersianGulf/data/build_data.py` (adapted from
`league/IR-AzadeganLeague/data/build_data.py`, same FotMob
matchDetails format, same `jleague_lib` helpers). It regenerates
`league/IR-PersianGulf/data/ir_persiangulf_matches.csv` (one row per
played league match) and `team_matches.csv` (two rows per match,
team-long). The CSVs are gitignored by repo norm; the builder is
committed so the CSVs are reproducible. The builder reads the
warehouse index from the worktree when present and falls back to
the absolute main-checkout path (the 24 GB warehouse is gitignored
and lives only in the main checkout), exactly as the Azadegan
builder does.

## Inclusion rules

- League rows: index `league_id = 523` AND payload
  `general.parentLeagueId == 523` AND payload `general.leagueName`
  in ("Persian Gulf Pro League", "Persian Gulf"). The
  `parentLeagueId` key is the load-bearing one: FotMob's
  `general.leagueId` is a season-edition id (523 / 880658 /
  886556 / 893543) and filtering on it would drop 52 real league
  matches; the "Persian Gulf" name variant covers the 15 latest
  rows (2026/2027 rounds 11–12), renamed by FotMob mid-season.
  Excluded on name: 0 rows.
- Played matches only: `header.status.finished` must be True.
  No index row fails this (1,245/1,245 finished); the check is
  kept so a future pull cannot smuggle in a placeholder.
- **Playoff exclusion (the only exclusion):** rows whose
  `matchRound` is not a round number are not league matches.
  Exactly 2: 1000015890 ("Asian Qualifiers Play-offs -
  Semi-Final") and 1000015891 ("Asian Qualifiers Play-offs -
  Final"), both season 2025/2026. Played league n = 1,243
  (asserted in the builder).
- No other exclusions: no score is missing or unparseable among
  played league matches; no duplicate match ids; the maximum
  fixture-pair duplication is 2 (the home/away legs of the double
  round-robin), as expected.
- Season labels are exactly as in the warehouse (`2021/2022`, …,
  `2026/2027`). No relabelling. 2025/2026 keeps its warehouse
  shape (rounds 1–23, 178 matches) — the missing rounds 24–30
  are a warehouse gap, and no match is imputed for them.

## Score extraction

`header.status.scoreStr`, falling back to `header.teams[].score`.
Cross-checked against the index `score` column: agreement on all
1,243 played league matches. Target for the goals candidate is the
FT score as stored; there are no shootouts or extra-time scores in
league matches.

## Split-source rules

- **HT goals**: from the goal-event feed only (`ht_from_events`,
  goals with `time <= 45`), and only where the feed reproduces the
  FT score per side. `ht_source` values in the CSV:
  - `events` (1,104): feed reproduces FT; HT from events.
  - `events-zero` (129): empty event feed on a 0-0; HT is (0, 0)
    by the same feed.
  - `events-incomplete` (2): feed disagrees with the FT score
    (3765423, 3765395); HT is NaN — the feed cannot be trusted
    for the split even though the FT score stands.
  - `none` (8): empty event feed on a scored match; HT is NaN.
- **Period splits**: never fabricated. There are no stats periods
  in any payload, so no `fh_*`/`sh_*` stat column is ever populated
  (all NaN by construction).
- **Stats/xG/shotmap columns**: `content.stats` is null and the
  shotmap shot list is empty in every payload, so every `*_home` /
  `*_away` stat and xG column is NaN and every `sm_*` column is 0.
  This is a measured absence, not a fill: the columns exist in the
  schema so the CSV matches the program's shape, and their emptiness
  is what makes S/C/T not buildable.
- **Cards**: the only card source is the event feed
  (`cards_source = "events"`). Yellow and red-family counts are
  recorded per side from Card events as-is. The feed break is
  structural: Yellow events are 0 in every row of 2021/2022–
  2024/2025 and present from 2025/2026, so pre-2025/2026 yellow
  zeros are feed absence, not true zeros — no EDA or model may
  treat them as measured. No stats-feed yellow column exists to
  cross-check against (both are NaN).
- **Referee**: the column holds the `infoBox.Referee.text` value
  as-is: `""` in all 960 dev-season rows, a name in 43 recent
  rows (14 in 2025/2026, 29 in 2026/2027).
- **Team identity**: FotMob team id. One id renamed mid-corpus
  (139914 Foolad Khouzestan → Foolad Khuzestan, 2023/2024); the
  id is stable across the rename and is the join key everywhere.

## Team-long table

`team_matches.csv` mirrors the Azadegan shape: one row per
team-match (2,486 rows), with `_against` columns for the opponent's
values of each counted quantity. It is the table the EDA trait
checks and the engine's naive baselines read.

## Reproducibility check

Re-running the builder reproduces the CSVs exactly (deterministic
sort by date then match id; verified by re-run, identical md5).
Headline levels recomputed from the built CSV match the independent
payload-level EDA run to the third decimal (e.g. pooled 1H share
0.4271 from the CSV vs 0.4272 from payloads — the 9-goal difference
is the two excluded playoff rows (3 goals) plus the two mismatch
matches whose HT is NaN (6 goals)); per-season levels match exactly
once the playoff rows are excluded.
