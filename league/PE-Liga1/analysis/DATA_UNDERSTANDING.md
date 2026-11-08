# Step 1 — Data Understanding: PE-Liga1 (Peru Liga 1, FotMob id 131)

Source: FotMob world warehouse, `data_enrichment/fotmob_world_index.csv`
filtered to `league_id = 131`; per-match JSONs under
`data_enrichment/fotmob_world/Peru/Liga 1/<season>/<id>.json`.
All numbers below were measured from the payloads on 2026-11-10
(`analysis/eda.py`, `analysis/inventory_summary.json`).

## Inventory

- **1,860 matches**, calendar-year seasons **2021–2026**. Every indexed
  file is finished. Season counts: 2021: 239, 2022: 346, 2023: 344,
  2024: 306, 2025: 328, 2026: 297.
- **Format (verified from `general.leagueName`, not assumed):** two
  regular tournaments per year plus a tiny play-off tail carried as
  separate sub-leagues:
  - 2021: Fase 1 (81) + Fase 2 (153); play-offs: Fase 1 Championship
    Playoff 1, Final Stage 2, Qualification 2.
  - 2022–2025: Apertura (171/171/153/171) + Clausura (171/171/153/153);
    Final Stage 4 (2022), 2 (2023); Placement Playoff 4 (2025).
  - 2026: a single payload league (`Liga 1`, id 131) whose rounds
    `1`–`17` are the Apertura (153) and `Clausura - Round 1..16` the
    Clausura (144) — the Clausura is **in progress** (16 of 17 rounds
    at pull time).
  - Play-off total: **15 matches**. Round labels restart per
    tournament, so the walk-forward block is the (season, tournament)
    pair — the CSV's `block` column.
- **Awarded matches: 9** (`header.status.awarded`): eight in 2023
  (the February 2023 walkover wave — six 3-0/0-3 in Apertura rounds
  1–3, one 0-0 in Clausura, one 0-3 in Clausura) and one in 2025
  Clausura (Ayacucho FC 0-3 Comerciantes Unidos, 2025-11-08). These
  were not played; their scores are administrative.
- **Teams: 28** FotMob ids across the window. Ids are perfectly
  stable; names are stable except accent variants that appear in
  2026 payloads for three clubs (Alianza Atlético, Atlético Grau,
  Asociación Deportiva Tarma). The builder keys everything by id
  and canonicalises display names to the most frequent spelling.
  Membership churn is real (19/19/19/18/19/18 clubs per year) —
  promotion/relegation with a Liga 2 that is **not** in the
  warehouse (Peru contributes only Liga 1 to the index).

## Field coverage per season (of n)

| Season | n | stats | rich stats | period splits | referee named | xG | shotmap |
|---|---|---|---|---|---|---|---|
| 2021 | 239 | 224 | 41 | 0 | 0 | 0 | 0 |
| 2022 | 346 | 298 | 156 | 1 | 239 | 0 | 0 |
| 2023 | 344 | 328 | 159 | 5 | 336 | 0 | 0 |
| 2024 | 306 | 270 | 152 | 2 | 259 | 0 | 0 |
| 2025 | 328 | 285 | 199 | 199 | 262 | 0 | 0 |
| 2026 | 297 | 297 | 297 | 297 | 141 | 0 | 0 |

- **No xG anywhere** (no `expected_goals` key in any of the 1,860
  files) and **no shotmap in any file**. The goals model is
  goals-only by construction; every xG/shotmap feature is dead on
  arrival (FEATURES.md).
- **Stats feed has two depths.** A *sparse* block (`BallPossesion`,
  `total_shots`, `ShotsOnTarget`, `corners`) exists in ~92% of all
  matches in every season. A *rich* block (adding `yellow_cards`,
  `touches_opp_box`, `big_chance`, `fouls`, off-target/blocked splits,
  …) exists in a subset that is concentrated in **Apertura**
  tournaments in 2021–2024 (rich by block: Fase 1: 40, Fase 2: 0,
  2022-Ap: 156, 2022-Cl: 0, 2023-Ap: 159, 2023-Cl: 0, 2024-Ap: 152,
  2024-Cl: 0, 2025-Ap: 46, 2025-Cl: 152, 2026: all). Duplicate keys
  across sections (`top_stats` vs `shots`/`discipline`) carry
  identical values; the builder de-duplicates by first occurrence.
- **Period splits** are effectively a 2025+ phenomenon: 8 matches in
  2021–2024 combined, 199/328 in 2025, 297/297 in 2026.
- **Events** are complete for goals (`events_exact` on 1,851/1,860;
  HT score recoverable for all but 7 matches, all in 2023) — but see
  the cards defect in EDA.md: **plain-yellow Card events do not
  exist in 2021–2022 payloads at all** (only YellowRed/Red appear),
  so event-derived yellows are meaningless before 2023.
- **Referee** (`infoBox.Referee.text`): 0% in 2021, then 69% (2022),
  98% (2023), 85% (2024), 80% (2025), 47% of the in-progress 2026.

## Quirks recorded

1. The `total_shots` key is **not one quantity**: in rich matches
   `total_shots = SOT + off-target + blocked` exactly (100% of rich
   matches); sparse-block means (~19–20) track rich `SOT + off`
   (~19.6–20.8), not the rich total (~25–27). See EDA F-feed-2 for
   the unified target this forces.
2. Stadium city is present per match (`infoBox.Stadium.city`) —
   altitude is measurable as a home-city attribute (EDA F-alt).
3. 2021 Fase 1 was a group phase (81 = 9 rounds × 9 matches with
   round labels repeating across the two tournaments); it is a
   regular-phase block like any other for modelling purposes.
