# Step 1 — Data Understanding: IN-IndianFootballLeague

India Indian Football League — the **I-League** (tier 2), FotMob
league_id 8982. Split-year seasons 2021/2022–2026/2027, 608 played
matches in the bundle index (`index_8982.csv`, 608 rows). Warehouse
mirror: `data_enrichment/fotmob_world/India/Indian Football
League/<season>/<match_id>.json`.

## Format

- 2021/2022: 13 teams, 114 matches — a regular phase (78) followed by
  a split into a Championship Group (21) and a Relegation Group (15).
- 2022/2023: 12 teams, 132 matches, single group. 2023/2024: 13
  teams, 154 matches, single group. 2024/2025: 12 teams, 132
  matches, single group.
- 2025/2026 (virgin): 10 teams, 66 matches — regular phase 45 (a
  single round-robin: 10×9/2 = 45), then a Promotion Group (15) and
  a Relegation Group (6). The season is COMPLETE: its full split
  structure is present in the bundle and the following season
  (2026/2027) has already begun (10 matches). The brief's suggested
  virgin therefore stands.
- 2026/2027 (reserve): 10 matches so far, in progress — untouched.
- Split-phase rows (championship / relegation) are ordinary rows with
  a phase flag, never filtered: main 551, championship 36,
  relegation 21 over the corpus.
- 24 distinct FotMob team ids over the corpus; 19 appear in the dev
  era (2021/2022–2024/2025).

## Identity / naming

- The competition was rebranded mid-corpus: `general.leagueName` is
  **"I-League"** for all of 2021/2022–2024/2025 (with
  `"I-League Championship Group"` / `"I-League Relegation Group"`
  for the 2021/2022 split rows), becomes **"Indian Football
  League"** in 2025/2026 (with `"Indian Football League Promotion
  Group"` / `"Indian Football League Relegation Group"`), and
  2026/2027 mixes `"I League"` (7) and `"Indian Football League"`
  (3). Same league_id (8982) and same warehouse path throughout —
  one competition, a name change, no merge.
- `coverageLevel` is `"lower"` for all 608 matches.
- All logic keys by FotMob team id. Four ids carry two name
  spellings (Rajasthan United FC / Rajasthan United; Sudeva / Sudeva
  FC; Aizawl / Aizawl FC; Real Kashmir / Real Kashmir FC) — names in
  the CSVs are as published per match; the engine keys by id.

## Feeds (measured, `eda_summary.json` / `inventory_summary.json`)

- **Stats feed: 0/608 matches in every season.** `content.stats`
  carries no `Periods` key anywhere. No xG, no SOT, no corners, no
  shots, no yellows from stats. Period splits: 0. This is a
  **scores-only league** — confirmed, not assumed.
- **Shotmap: 0/608.** No xG anywhere.
- **Events: 574/608** (2021/2022: 105/114, 2022/2023: 125/132,
  2023/2024: 146/154, 2024/2025: 125/132, 2025/2026: 63/66,
  2026/2027: 10/10). All 34 matches without events are 0-0 draws per
  the header — they carry no goals at all; their events-derived
  fields are missing, never zero.
- **Lineups:** present per the index in most matches (105 / 132 /
  154 / 132 / 66 / 10 by season). Not used by any candidate.
- **Referee: named in 467/608** — dev era 453/496 (84/114, 130/132,
  138/154, 101/132), but only **4/66 in the virgin** and 10/10 in the
  reserve. Dev-era referee coverage is real, yet X8 cannot rescue K:
  there is no yellows target in dev at all (F5).
- Event goals agree with the header score in all but 4 matches —
  exactly the 4 awarded matches (below); header `scoreStr` is
  authoritative throughout.

## Scores

- Goals/match by season: 2.579 / 2.727 / 3.331 / 3.182 (dev
  2021/2022–2024/2025), 3.045 in the virgin 2025/2026, 2.700 in the
  reserve 2026/2027. The level ROSE across the dev era (the two most
  recent dev seasons are the two highest); OU2.5 over-rate 0.48–0.61
  per dev season; home-win rate 0.35–0.52; draw rate 0.22–0.27.
- Total goals in corpus: 1,861. Dev era (2021/2022–2024/2025):
  1,587 goals (n=532). Dev scored window (2022/2023–2024/2025):
  1,293 goals, 3.093/match (n=418).
- Four awarded matches (kept as ordinary rows with `awarded=true`,
  FT score is the awarded score; in each case the on-pitch score
  differed, hence the 4 score/event mismatches): 4058291 (2022/2023,
  Sudeva 0-3 Kenkre, played 1-2), 4058277 (2022/2023, Real Kashmir
  0-3 Churchill Brothers, played 1-0), 4664604 (2024/2025, Namdhari
  0-3 Inter Kashi, played 2-0), 4664639 (2024/2025, Aizawl 3-0
  Churchill Brothers, played 1-1). Their event-derived 1H goals are
  excluded from dev halves by construction (awarded matches
  excluded). None sits in the virgin season.

## Split (frozen)

- Dev: seasons ≤ 2024/2025 (warm-up 2021/2022, scored
  2022/2023–2024/2025, n=418).
- Virgin: 2025/2026 (complete, n=66 — small; the gate is applied as
  written, not softened) — read ONCE per dev-passing candidate
  (G only can pass).
- Reserve: 2026/2027 (n=10, in progress) — untouched, confirmatory
  reserve.
