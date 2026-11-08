# Phase 3.5 — RU Premier League X1–X9

The global causality contract is trailing-only, strictly before kickoff, with ratios of sums and null features when minimum history is unavailable.

| ID | verdict | league-specific evidence |
|---|---|---|
| X1 blend goals/xG | ADOPTED with goals-only dev fallback | Goals are complete; full stats xG is virgin-era only, with 11 2024/2025 stray rows plus one anomalous older payload. Therefore dev goals development is goals-only. |
| X2 mover tier offset | DROPPED as consumed feature | 12 same-league newcomers have GF gap -0.250 and GA gap +0.259. No second-tier corpus exists, so this is descriptive only; use a goals SHRINK arm for thin-history/newcomer teams. |
| X3 set-play xG | DROPPED | Full coverage begins in 2025/2026, inside the virgin window; it cannot be dev-gated. Descriptive xG-era reliability is not a production feature. |
| X4 xG per shot | DROPPED | Shotmap/xG data are virgin-era limited and cannot be computed for the dev window; no dev gate is possible. |
| X5 trailing target means | ADOPTED | SOT, corners, and event-unified cards exist across all seasons; reliability is 0.849/0.846, 0.702/0.582, and 0.545/0.645 (event yellows) for/against. The cards artefact is present (EDA), so the cards target is event-unified. |
| X6 attacking xGOT per shot | DROPPED | xGOT/shot is virgin-era and cannot be dev-gated; it is descriptive only. |
| X7 box touches | ADOPTED as corners variant arm (coordinator amendment, pre-prereg) | Reliability 0.876/0.811 — the strongest territorial trait here. Coverage is partial in dev (67.9% / 47.1% / 71.2% / 100% by season) but the reference min-8-of-last-10 rule governs arm inactivity match by match, exactly as in PL where X7 coverage was 0% / 61% / 77% / 100% and X7 was still a registered arm. The dev gate decides. |
| X8 referee strictness | DROPPED for primary design | Coverage is 40.0% in 2021/2022 and 70.4% in 2025/2026; pooled strictness reliability and trailing availability must be rechecked in prereg. |
| X9 possession + big chance | ADOPTED as corners Gate Zero covariates | Coverage is 100.0% in every season; reliability is 0.918 and 0.816 for possession and big chances-for. |

The adopted set is X1, X5, X7, and X9. Frozen half constants from complete 2023/2024–2025/2026 seasons are goals 0.4472, SOT 0.4612, corners 0.4801, total shots 0.4602, yellow cards 0.3519. Rejected inherited items include half-share team traits, finishing, conversion, standalone SOT rate, defensive xGOT, lineups, formations, standings, h2h, attendance, game-state, momentum, and reds.

