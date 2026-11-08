# Step 1 — Data Understanding (RO-LigaI, FotMob id 189)

Source: FotMob world warehouse, `data_enrichment/fotmob_world_index.csv`
filter `league_id = 189`; per-match JSONs under
`data_enrichment/fotmob_world/Romania/Liga I/<season>/`.
Inventory measured 2026-11-10 by full scan of all 1,701 files.

## Inventory

| Season | Matches | Stats feed | Period splits | Shotmap | Referee |
|---|---|---|---|---|---|
| 2021/2022 | 316 | 311 (98.4%) | none | 0 shots | 316/316 |
| 2022/2023 | 317 | 306 (96.5%) | none | 0 shots | 317/317 |
| 2023/2024 | 317 | 307 (96.8%) | none | 0 shots | 316/317 |
| 2024/2025 | 315 | 315 (100%) | none | 0 shots | 313/315 |
| 2025/2026 | 317 | 317 (100%) | 317 (100%) | 0 shots | 316/317 |
| 2026/2027 | 119 (in progress) | 119 | 119 | 0 shots | 112/119 |

Total 1,701 played matches (all `finished`), 26 team ids, 16 teams/season.

## Format — the split is IN the feed, every season

Each season is four sub-tournaments under parent league 189
(`general.leagueId` / `general.leagueName`):

| Phase | n/season | Structure |
|---|---|---|
| regular | 240 | 16 teams, rounds 1–30, double round-robin |
| championship | 30 | top 6, rounds 1–10 |
| relegation | 45 | bottom 10, rounds 1–9 |
| ecl_playoff | 1–2 | one-legged knockout for a European place (semi + final; absent 2024/2025) |

Phase rule (frozen in the preregs): regular + championship +
relegation are modelled as ordinary league matches (same clubs,
90-minute league fixtures; phase recorded in the CSV, never a model
input). The ECL playoff is EXCLUDED (7 matches total): one-off
knockout ties, and the only extra-time matches in the corpus (both
2025/2026 ECL matches carry Extra-period stats blocks).
Included n = 315 per complete season; 2026/2027 partial = 119
(regular season only so far). League renamed Liga I → Superliga from
2022/2023 (same parent id 189; cosmetic).

## Field coverage quirks (all measured, not assumed)

- **No xG anywhere**: the `expected_goals` stats key never appears in
  any season; shotmap is present as a container but holds **zero
  shots in all 1,701 matches**. Goals modelling is goals-only.
- **Two stats-feed eras.** 2021/2022–2024/2025 the feed is minimal —
  only `BallPossesion`, `total_shots`, `ShotsOnTarget`, `corners`
  (plus nothing else). From 2025/2026 the feed is rich (30+ keys:
  off-target, blocked, box splits, big chances, box touches, fouls,
  yellow/red card counts, passes, duels, …) AND period splits
  (FirstHalf/SecondHalf) appear. Any feature needing rich keys has
  **no dev-era data**.
- **Total-shots definition break at 2025/2026**: mean total shots
  17.8–18.7/match in the minimal era vs 26.1 (2025/2026) and 29.4
  (2026/2027) in the rich era, while SOT (8.2–8.5 → 8.5), corners
  (8.7–9.5 → 9.7) and goals are continuous. In the rich era
  total = SOT + off-target + blocked exactly (blocked ≈ 6.9/match);
  total − blocked = 19.2 in the virgin season — closer to dev levels
  but still +1.1, and +4.7 by 2026/2027, so the reconstruction's
  identity cannot be verified from dev-era data (no components were
  stored). See MODEL_DESIGN: T-RO is not buildable.
- **Cards: stats-vs-events artefact PRESENT** (the known cross-league
  pattern). Stats-feed `yellow_cards` exists only from 2025/2026.
  On the 434 rich-era matches: exact both-sides agreement with the
  event feed only 76.5%; stats mean 4.01 yellows/match vs events
  4.22 — the stats feed undercounts by ≈0.21/match. Events exist for
  every match in every season (7,563 Yellow + 171 YellowRed + 202 Red
  card events). The cards target is therefore the EVENT count for
  all eras (frozen in PREPROCESSING + prereg).
- **Referee**: named in `matchFacts.infoBox.Referee` for 1,690/1,701
  (99.4%); 66 distinct referees.
- **Events**: non-empty for all 1,701 matches → HT score from goal
  events is available for every match.
- **Team identity**: keyed by FotMob team id (26 ids, stable). Names
  vary cosmetically by id across seasons — diacritics added in
  2026/2027 (Botosani→Botoșani, Dinamo Bucuresti→Dinamo București,
  Otelul Galati→Oțelul Galați, etc.) and one rename
  (id 9723: "FC FCSB" → "FCSB" from 2024/2025). Ids, never names,
  are the join key.
- Missing-stats matches (26, all in 2021/2022–2023/2024) keep their
  goals/cards/events but have no SOT/corners/shots targets; they are
  excluded per-market, never imputed.
