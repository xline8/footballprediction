# Step 1 — Data Understanding: NO-2Divisjon

Norway 2. divisjon (tier 3), FotMob league_id 204. Calendar-year
seasons 2021–2026, 2,158 played matches in the bundle index
(`index_204.csv`, 2,158 rows). Warehouse mirror:
`data_enrichment/fotmob_world/Norway/2. divisjon/<season>/<match_id>.json`.

## Format

- Two parallel groups, Avd. 1 and Avd. 2 (`general.leagueName`:
  "2. Divisjon Avd. 1" / "2. Divisjon Avd. 2"), 14 teams per group,
  26 rounds, 182 matches per group per full season. No championship /
  relegation split inside a season; every row is an ordinary row with
  a phase flag (`avd1` / `avd2`), never filtered.
- 2022 is short: 338 matches, not 364 — Avd. 1 had 13 teams that
  season (156 matches), Avd. 2 had 14 (182). 27 teams in 2022, 28 in
  every other season. 59 distinct FotMob team ids over the corpus.
- Calendar seasons (Mar–Nov approx.); promotion/relegation churn
  between seasons is large (25 entrant transitions in the dev era
  alone — see EDA F4).

## Feeds (measured, `eda_summary.json` / `inventory_summary.json`)

- **Stats feed: 0/2,158 matches in every season.** `content.stats`
  carries no `Periods` key anywhere. No xG, no SOT, no corners, no
  shots, no yellows from stats. Period splits: 0. This is a
  **scores-only league** — confirmed, not assumed.
- **Shotmap: 0/2,158.** No xG anywhere.
- **Events: 2,126/2,158** (2021: 352/364, 2022: 331/338, 2023:
  351/364, 2024–2026: 364/364). The 32 matches without events are
  all scoreless (0 goals in them) — their events-derived fields are
  missing, never zero.
- **Lineups: 1,111/2,158** (0 in 2021–2022, 19 in 2023, 364 in
  2024–2026). Not used by any candidate.
- **Referee: named in 0/2,158 matches, every season.** X8 is
  impossible by data absence.
- Event goals agree with the header score in all but 2 matches:
  4696470 (awarded — played 4-3, awarded 0-3; header wins) and
  5143624 (2026, a duplicated Goal event at minute 79; header 0-4
  wins). Header `scoreStr` is authoritative throughout.

## Scores

- Goals/match by season: 3.52 / 3.39 / 3.33 / 3.45 (dev 2021–2024),
  3.53 in the virgin 2025, 3.45 in the reserve 2026. High-scoring
  league: OU2.5 over-rate 0.62–0.68 every season; home-win rate
  0.46–0.51; draw rate 0.15–0.22.
- Total goals in corpus: 7,431. Dev-era (2021–2024) goals: 4,893.
- One awarded match: 4696470, 2025-03-31, Alta–Levanger, played 4-3,
  awarded 0-3. It sits in the virgin season; kept as an ordinary row
  with `awarded=true` (never silently dropped), its FT score is the
  awarded score. Its event-derived 1H goals reflect the played game
  and are excluded from dev halves by construction (virgin season).

## Identity

- All logic keys by FotMob team id. One id carries two spellings:
  10232 = "Ullensaker/Kisa" vs "Ull/Kisa" (same club, shortened in
  some seasons). No other name conflicts. Team names in the CSVs are
  as published per match; the engine keys by id.

## Split (frozen)

- Dev: seasons ≤ 2024 (warm-up 2021, scored 2022–2024, n=1,066).
- Virgin: 2025 (complete, n=364) — read ONCE per dev-passing
  candidate (G only can pass).
- Reserve: 2026 (n=364) — untouched, confirmatory reserve.
