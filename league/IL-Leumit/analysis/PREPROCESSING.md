# Step 2 — Preprocessing: IL-Leumit

Builder: `league/IL-Leumit/data/build_data.py` (committed; the CSV is
gitignored by repo norm and regenerable). Output:
`league/IL-Leumit/data/il_leumit_matches.csv` — **1,581 rows**, one per
played match, exactly matching the warehouse index count for
league_id 128 (296 × 5 complete seasons + 101 in-progress 2026/2027).
Row order: date, then match id.

## Derivation rules

1. **FT goals** = `header.teams[0/1].score` (equivalently
   `header.status.scoreStr`). Never the event feed.
2. **Team identity by FotMob team ID** (`general.homeTeam.id` /
   `awayTeam.id`), never by name. Display name = the most frequent
   name for that ID across the corpus.
3. **Team-identity quirk RESOLVED** (flagged at Step 1): 2023/2024
   shows 17 distinct names but exactly **16 distinct team IDs**, as a
   16-team league must. The variant: team_id **752833** appears as
   both 'SC Kafr Qasim' (canonical, majority) and 'SC Kfar Kasem'.
   One club, two feed spellings; keyed by ID the corpus has 30
   distinct clubs over six seasons.
4. **Phase flag** (frozen Step-1 fact): rounds 1–30 = `regular`,
   rounds 31–37 = `split`. Both phases are real league matches and
   both are included; the flag is carried on every row.
5. **Round** = `general.matchRound` (int).
6. **Inclusion**: played matches only — every index row for this
   league is finished with a score (Step 1 verified 1,581/1,581), so
   nothing is excluded and nothing is fabricated.
7. **No stats columns exist to include**: `has_stats` and
   `has_shotmap` are 0/1,581 in the index, so the CSV is fixture +
   score only. Period splits are absent → no HT goals, no halves
   quantities of any kind.
