# Phase 2 — Preprocessing: From Warehouse JSONs to the PL Analysis Tables

`data/build_data.py` reads only league_id 196 rows from the linked warehouse, sorts by date and match id, and writes `data/pl_matches.csv` and `data/pl_team_matches.csv`. The output has 1,654 match rows and 3,308 team rows.

## Derivation rules

The score comes from the finished-match header. Team identity is the FotMob team id. Every row is assigned `phase=regular`, because all 1,654 payloads report the same Ekstraklasa league and the competition has no split phase in this corpus. The raw league name and parent id are retained as audit fields.

All-stat fields are retained for All, FirstHalf, and SecondHalf where present. Missing fields remain empty. The separate `has_stats_all`, `has_stats_half`, and content-based coverage fields prevent index flags from being mistaken for actual values.

Cards are represented twice: raw stats-feed `yellow_cards_*`, and the unified `yellow_*` target. The latter is the stats value when both sides are available, otherwise the event Yellow count. Event YellowRed and Red counts are retained for diagnostics. Shotmap aggregates use regulation shots only and retain shot count, SOT, xG, xGOT sum, xGOT-populated shot count, and first-half shot count by side.

## Missingness and leakage contract

The builder does not use table, h2h, attendance, teamForm, lineups, or post-match snapshots as model features. It does not fit anything. Static fixture facts are limited to the two teams, venue, and (where published) referee identity. All trailing features in later phases must use matches strictly before the target kickoff; ratios are ratios of sums.

Period splits are absent in 2021/2022, partial in 2022/2023, near-complete in 2023/2024, and complete in 2024/2025–2025/2026. Halves constants are frozen only on the measured complete era 2023/2024–2025/2026.

Stats xG and shotmap xG are separate feeds. Stats xG is sparse in 2023/2024–2024/2025 and full in 2025/2026–2026/2027; shotmap xG is usable only in the 2025/2026 era. xGOT is guarded by its populated-shot era and is not treated as a pre-2025 quantity.
