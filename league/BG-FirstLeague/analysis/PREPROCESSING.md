# Step 2 — Preprocessing: BG-FirstLeague

Builder: `league/BG-FirstLeague/data/build_data.py` (adapted from the
ZA-PSL builder; regenerates both CSVs from the warehouse; CSVs are
gitignored by repo norm, the builder is the committed record).
Warehouse root is the main repo (`~/workspace/footballprediction`),
passed via `--warehouse-root` if needed.

## Inclusion rules

- One row per played match in the index for league_id 270: **1,471
  rows**, no exclusions. Phase parsed from `general.leagueName`:
  plain name → `regular`; `Championship Playoff` →
  `championship_playoff`; `ECL Group` → `ecl_group`; `Relegation
  Group` → `relegation_group`; `ECL Playoff` → `ecl_playoff`; any
  other leagueName raises. Phase counts asserted per season in the
  builder (see Step 1 table).
- Score from `header.status.scoreStr` (fallback: index `score`).
- Stats columns keep the ZA schema (same STAT_KEYS tuple) so
  downstream loaders see identical columns; keys the Bulgarian feed
  never publishes (`expected_goals`, `touches_opp_box`, `big_chance`,
  `yellow_cards`, …) are present as empty columns, never fabricated.
- Period-split columns (`fh_`/`sh_`) exist for schema parity and are
  empty in every row: this league has no period splits (Step 1).
- Cards: `ev_yellow_*` = direct Yellow + YellowRed events per side;
  `ev_red_*` = Red + YellowRed; the modelling target columns
  `yellow_home`/`yellow_away` are set to the event-unified counts and
  `cards_source = events` on all 1,471 rows (frozen in Step 1).
- First-half event columns: `ht_home_goals`/`ht_away_goals` from Goal
  events with minute ≤ 45 (stoppage time at 45+ parses to 45 via the
  builder's minute parser, matching the ZA/RU convention), and
  `ht_yellow_home`/`ht_yellow_away` likewise from card events. These
  are the ONLY halves source in this league.
- Team-match long table: 2,942 rows (for/against per team per match).
- Season labels exactly as in the warehouse (`2021/2022` style).
  Team identity = FotMob team id everywhere.

## Windows (frozen here, before any fitting)

- **Goals:** training seed 2021/2022; dev evaluation 2022/2023,
  2023/2024, 2024/2025 (n = 859, all phases); virgin 2025/2026
  (n = 293, last complete season); 2026/2027 (97, in progress) is the
  reserved confirmatory window — never read in this build.
- **Count markets (SOT, corners, cards, total shots):** stats exist
  from 2021/2022, so warm-up/seed = 2021/2022; dev scored =
  2022/2023–2024/2025 (stats rows n = 841; cards rows n = 859, the
  event target exists on every row); virgin = 2025/2026 (stats rows
  n = 293; cards n = 293). Stats-missing rows (24 across the dev
  seasons) are excluded from count-market scoring only; they remain
  in the goals corpus and in chronological state updates where the
  sibling harnesses define that behaviour.
- Calibration convention everywhere: **actual − predicted**.
