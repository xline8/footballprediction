# Step 1 — Data Understanding: FR-Ligue3

France Ligue 3 (tier 3), FotMob league_id 8970. Season-year
seasons 2021/2022–2026/2027, 1,570 played matches in the bundle index
(`index_8970.csv`, 1,570 rows). Warehouse mirror:
`data_enrichment/fotmob_world/France/Ligue 3/<season>/<match_id>.json`.

## Format

- Single group every season: 18 teams (306 matches) in
  2021/2022–2023/2024, 17 teams (272 matches) from 2024/2025.
  2026/2027 has 18 teams but only 108 matches in the bundle (season
  in progress). No championship / relegation split inside a season;
  every row is an ordinary row with phase flag `main`, never filtered.
- 42 distinct FotMob team ids over the corpus.
- Season-year seasons (Aug–May approx.); promotion/relegation churn
  between seasons is large (21 entrant transitions in the dev era
  alone — see EDA F4).

## Identity / naming

- The league was the Championnat National through 2025/2026 and
  was rebranded Ligue 3 for 2026/2027. `general.leagueName` is
  `"National"` for 1,462 matches (2021/2022–2025/2026) and
  `"Ligue 3"` only for the 108 matches of 2026/2027. The index
  already carries the league name "Ligue 3" for all rows; the raw
  JSON `leagueName` is the per-season truth. Same competition
  throughout — no split, no merge.
- All logic keys by FotMob team id. Four ids carry two spellings
  (accent/prefix variants, same club): 6246 Bourg en Bresse
  Peronnas / Péronnas; 47211 Orleans / Orléans; 238671 Paris 13
  Atletico / Atlético; 293443 Aubagne / SC Aubagne Air Bel. Team
  names in the CSVs are as published per match; the engine keys by id.

## Feeds (measured, `eda_summary.json` / `inventory_summary.json`)

- **Stats feed: 0/1,570 matches in every season.** `content.stats`
  carries no `Periods` key anywhere. No xG, no SOT, no corners, no
  shots, no yellows from stats. Period splits: 0. This is a
  **scores-only league** — confirmed, not assumed.
- **Shotmap: 0/1,570.** No xG anywhere.
- **Events: 1,532/1,570** (2021/2022: 287/306, 2022/2023: 287/306,
  2023/2024–2026/2027: all matches). The 38 matches without events
  carry 3 goals between them — their events-derived fields are
  missing, never zero.
- **Lineups: 963/1,570** (5 in 2021/2022, 0 in 2022/2023, all
  matches from 2023/2024). Not used by any candidate.
- **Referee: named in 0/1,570 matches, every season.** X8 is
  impossible by data absence.
- Event goals agree with the header score in all but 6 matches: the
  5 awarded matches below (header wins) plus 4879591 (2025/2026,
  Valenciennes–Caen, header 2-1 vs 3 event home goals — a duplicated
  Goal event; header wins). Header `scoreStr` is authoritative
  throughout.

## Scores

- Goals/match by season: 2.503 / 2.503 / 2.546 / 2.393 (dev
  2021/2022–2024/2025), 2.423 in the virgin 2025/2026, 2.389 in the
  reserve 2026/2027. Low-scoring league: OU2.5 over-rate 0.40–0.49
  every season; home-win rate 0.37–0.45; draw rate 0.26–0.33.
- Total goals in corpus: 3,879. Dev-era (2021/2022–2024/2025)
  goals: 2,962 (n=1,190). Dev scored window (2022/2023–2024/2025):
  2,196 goals, 2.484/match (n=884).
- Six awarded matches (kept as ordinary rows with `awarded=true`,
  FT score is the awarded score): 3663409 (2021/2022, Stade
  Briochin–Boulogne, played 1-0, awarded 3-0), 3663603 (2021/2022,
  Red Star–Sete, played 0-2, awarded 0-3), 3955519 (2022/2023,
  Concarneau–Orleans, played 1-1, awarded 0-3), 3955521 (2022/2023,
  Cholet–Avranches, played 1-3, awarded 3-0), 4125433 (2022/2023,
  Nancy–Concarneau, played 0-0, awarded 0-3), 4879528 (2025/2026,
  Valenciennes–Sochaux, played 0-1, awarded 0-3). Their
  event-derived 1H goals reflect the played game and are excluded
  from dev halves by construction (awarded matches excluded).

## Split (frozen)

- Dev: seasons ≤ 2024/2025 (warm-up 2021/2022, scored
  2022/2023–2024/2025, n=884).
- Virgin: 2025/2026 (complete, n=272) — read ONCE per dev-passing
  candidate (G only can pass).
- Reserve: 2026/2027 (n=108, in progress) — untouched,
  confirmatory reserve.
