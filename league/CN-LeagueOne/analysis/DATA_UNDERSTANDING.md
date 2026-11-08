# Step 1 — Data Understanding: CN-LeagueOne

China League One (tier 2), FotMob league_id 9137. Calendar-year
seasons 2021–2026, 1,572 played matches in the bundle index
(`index_9137.csv`, 1,572 rows). Warehouse mirror:
`data_enrichment/fotmob_world/China/China League One/<season>/<match_id>.json`.

## Format

- A single group every season (`general.leagueName`: "China League"
  in all 1,572 payloads; phase `single` on every row, never
  filtered). No parallel groups, no championship / relegation split
  inside a season.
- The league shrank after 2022: 18 teams, 34 rounds, 306 matches
  per season in 2021–2022; 16 teams, 30 rounds, 240 matches per
  season in 2023–2026. 39 distinct FotMob team ids over the corpus.
- Calendar seasons (Apr–Nov approx.); promotion/relegation churn
  between seasons is material (15 entrant transitions in the dev
  era alone — see EDA F4).

## Feeds (measured, `eda_summary.json` / `inventory_summary.json`)

- **Stats feed: 0/1,572 matches in every season.** `content.stats`
  carries no `Periods` key anywhere. No xG, no SOT, no corners, no
  shots, no yellows from stats. Period splits: 0. This is a
  **scores-only league** — confirmed, not assumed (brief confirmed).
- **Shotmap: 0/1,572.** No xG anywhere.
- **Events: 1,447/1,572** (2021: 283/306, 2022: 281/306, 2023:
  220/240, 2024: 216/240, 2025: 225/240, 2026: 222/240). The 125
  matches without events are NOT all scoreless: 3 of them carry
  goals (9 goals in total) — their events-derived fields are
  missing, never zero.
- **Lineups: 3/1,572** (all in 2026). Not used by any candidate.
- **Referee: named in 0/1,572 matches, every season.** X8 is
  impossible by data absence.
- Event goals agree with the header score in every match with
  events (0 score mismatches). Header `scoreStr` is authoritative
  throughout.

## Scores

- Goals/match by season: 2.71 / 2.61 / 2.26 / 2.48 (dev 2021–2024),
  2.61 in the virgin 2025, 2.69 in the reserve 2026. A lower-scoring
  league than the European tier-3 precedents: OU2.5 over-rate
  0.38–0.51 every season; home-win rate 0.39–0.43; draw rate
  0.20–0.33 (2024 draws at 0.333, the highest dev season).
- Total goals in corpus: 4,042. Dev-era (2021–2024) goals: 2,769.
- Three awarded matches, all in 2022: 3892074 (2022-06-10,
  Kunshan–Beijing Technology, 3-0), 3892065 (2022-06-14, Beijing
  Technology–Jiangxi Beidamen, 0-3), 3946586 (2022-08-01,
  Heilongjiang Ice City–Zibo Cuju, 3-0). Kept as ordinary rows with
  `awarded=true` (never silently dropped); their FT score is the
  awarded score. The first has no event feed at all; all three are
  excluded from the dev halves constants by construction.

## Identity

- All logic keys by FotMob team id. No team id carries conflicting
  spellings in this corpus. Team names in the CSVs are as published
  per match; the engine keys by id.

## Split (frozen)

- Dev: seasons ≤ 2024 (warm-up 2021, scored 2022–2024, n=786).
- Virgin: 2025 (complete, n=240) — read ONCE per dev-passing
  candidate (G only can pass).
- Reserve: 2026 (n=240) — untouched, confirmatory reserve.
